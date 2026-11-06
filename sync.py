# FARD CHECKER VERSION 1.9.11
"""Scan sync — keeps the last scan (per login) and the shared tracker state in a PRIVATE GitHub repo,
so any browser with the access key can open them.

Render settings (Environment):
    DATA_REPO     owner/repo of a private repo used only for data (NOT the code repo — that would redeploy the app)
    GITHUB_TOKEN  fine-grained token with access to that repo only, permission Contents: Read and write

Files written:
    scans/last-scan-<login>.json   the last scan of that login (application list, stages, remarks)
    scans/index.json               {login: {at, n, partial}}
    state/shared.json              gists / scores / points, owner & khata choices, pre-scrutiny points, photo prints,
                                   and "reps": which applications have a saved report online (key → version of the analysis)
    reports/<application>.json     the saved analysis report (v1.9.9) — photos, compression and satellite pictures removed,
                                   the tatima sketch kept as a reduced copy
    archive/disposed.json          applications no longer on the Dashboard list (disposed), kept ARCHIVE_DAYS days (default 365)
Phone numbers, Aadhaar and other 10/12-digit numbers are removed before anything is saved.
"""
import base64
import json
import os
import re
import threading
import time

import requests

API = os.environ.get("GITHUB_API", "https://api.github.com")
_lock = threading.Lock()
LOGIN_RE = re.compile(r"[^a-z0-9-]+")


def configured():
    return bool(os.environ.get("DATA_REPO") and os.environ.get("GITHUB_TOKEN"))


def _h(raw=False):
    return {"Authorization": "Bearer " + os.environ.get("GITHUB_TOKEN", ""), "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "fard-checker"}


def _url(path):
    return f"{API}/repos/{os.environ.get('DATA_REPO', '').strip()}/contents/{path}"


def get(path):
    """(object, sha) or (None, None) when the file does not exist yet."""
    r = requests.get(_url(path), headers=_h(), timeout=30)
    if r.status_code == 404:
        return None, None
    if r.status_code != 200:
        raise RuntimeError(_why(r))
    meta = r.json()
    sha = meta.get("sha")
    if meta.get("content") and meta.get("encoding") == "base64":
        raw = base64.b64decode(meta["content"])
    else:                                              # files over 1 MB come back without content — fetch raw
        rr = requests.get(_url(path), headers=_h(raw=True), timeout=60)
        if rr.status_code != 200:
            raise RuntimeError(_why(rr))
        raw = rr.content
    return json.loads(raw.decode("utf-8") or "null"), sha


def put(path, obj, sha=None, message=None):
    body = {"message": message or f"update {path}", "content": base64.b64encode(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).decode()}
    if sha:
        body["sha"] = sha
    r = requests.put(_url(path), headers=_h(), json=body, timeout=60)
    if r.status_code in (409, 422) and "sha" in r.text:
        raise ConflictError(_why(r))
    if r.status_code not in (200, 201):
        raise RuntimeError(_why(r))
    return r.json().get("content", {}).get("sha")


class ConflictError(RuntimeError):
    pass


def _why(r):
    try:
        m = r.json().get("message", "")
    except Exception:
        m = r.text[:200]
    hint = {401: "token not accepted — check GITHUB_TOKEN", 403: "token has no write permission for DATA_REPO (Contents: Read and write)",
            404: "DATA_REPO not found or the token cannot see it"}.get(r.status_code, "")
    return f"GitHub {r.status_code}: {m}" + (f" ({hint})" if hint else "")


# ── privacy: remove phone / Aadhaar / other long numbers (application numbers have 20 digits and are kept)
_DROP_KEYS = re.compile(r"mobile|phone|aadhaa?r|aadhar|email|vendeeAadhaar", re.I)


def scrub(x):
    if isinstance(x, dict):
        return {k: (None if _DROP_KEYS.search(str(k)) else scrub(v)) for k, v in x.items()}
    if isinstance(x, list):
        return [scrub(v) for v in x]
    if isinstance(x, str):
        s = re.sub(r"(?<!\d)\d{4}\s?\d{4}\s?\d{4}(?!\d)", "[removed]", x)
        s = re.sub(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)", "[removed]", s)
        s = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[removed]", s)
        return s
    return x


def login_slug(s):
    return LOGIN_RE.sub("-", str(s or "default").lower()).strip("-")[:40] or "default"


def save_scan(login, scan):
    login = login_slug(login)
    scan = scrub(scan)
    n = len(scan.get("items") or [])
    with _lock:
        for attempt in range(3):
            try:
                _, sha = get(f"scans/last-scan-{login}.json")
                put(f"scans/last-scan-{login}.json", scan, sha, f"last scan ({login}): {n} applications")
                idx, isha = get("scans/index.json")
                idx = idx or {}
                idx[login] = {"at": scan.get("at"), "n": n, "partial": bool(scan.get("partial")), "saved": int(time.time() * 1000)}
                put("scans/index.json", idx, isha, f"index ({login})")
                return idx
            except ConflictError:
                time.sleep(1 + attempt)
        raise RuntimeError("GitHub kept reporting a conflict — try again")


def load_scan(login):
    obj, _ = get(f"scans/last-scan-{login_slug(login)}.json")
    return obj


def index():
    obj, _ = get("scans/index.json")
    return obj or {}


STATE_PARTS = ("gists", "choices", "points", "fps", "reps")


def _merge(old, new):
    """Per key, the entry with the later 'at' wins."""
    out = dict(old or {})
    for k, v in (new or {}).items():
        if not isinstance(v, dict):
            continue
        o = out.get(k)
        if not isinstance(o, dict) or (v.get("at") or 0) >= (o.get("at") or 0):
            out[k] = v
    return out


def save_state(part_updates):
    upd = scrub({p: part_updates.get(p) or {} for p in STATE_PARTS})
    with _lock:
        for attempt in range(3):
            try:
                cur, sha = get("state/shared.json")
                cur = cur or {}
                for p in STATE_PARTS:
                    cur[p] = _merge(cur.get(p), upd.get(p))
                    if len(cur[p]) > 3000:            # keep the newest 3000 per part
                        keep = sorted(cur[p].items(), key=lambda kv: -(kv[1].get("at") or 0))[:3000]
                        cur[p] = dict(keep)
                cur["saved"] = int(time.time() * 1000)
                put("state/shared.json", cur, sha, "tracker state: " + ", ".join(f"{p} {len(upd[p])}" for p in STATE_PARTS if upd[p]))
                return {p: len(cur[p]) for p in STATE_PARTS}
            except ConflictError:
                time.sleep(1 + attempt)
        raise RuntimeError("GitHub kept reporting a conflict — try again")


def load_state():
    obj, _ = get("state/shared.json")
    return obj or {}


# ── saved reports (v1.9.9): the register opens any analysed application at once, on any browser
_IMG = re.compile(r'<img\b[^>]*?\balt="([^"]*)"[^>]*?\bsrc="data:image/[a-z+]+;base64,([A-Za-z0-9+/=]+)"[^>]*>', re.I)
_IMG_ANY = re.compile(r'<img\b[^>]*?\bsrc="data:[^"]*"[^>]*>', re.I)


def _small_jpeg(b64, side=900, q=60):
    from io import BytesIO
    from PIL import Image
    im = Image.open(BytesIO(base64.b64decode(b64)))
    im = im.convert("L") if im.mode in ("L", "LA", "1") else im.convert("RGB")
    im.thumbnail((side, side))
    out = BytesIO()
    im.save(out, "JPEG", quality=q, optimize=True)
    return base64.b64encode(out.getvalue()).decode()


def slim_html(html, clean=None):
    """Report as kept online: the tatima sketch is reduced, every other picture (photo, compression check, satellite) is removed.
    clean(text) is applied to the text only — never to the picture data."""
    keep = []

    def one(m):
        r = _one(m)
        keep.append(r)
        return f"\x00IMG{len(keep) - 1}\x00"

    def _one(m):
        alt = (m.group(1) or "").lower()
        if alt == "sketch":
            try:
                return ('<img alt="sketch" src="data:image/jpeg;base64,' + _small_jpeg(m.group(2)) +
                        '" style="max-width:100%;max-height:420px;object-fit:contain">')
            except Exception:
                pass
        return ('<div style="display:inline-block;padding:10px 12px;border:1px dashed #c9ced8;border-radius:6px;color:#5b6475;font-size:12px">'
                f'{alt or "picture"} — not kept in the online copy (tap Run again for the full report)</div>')
    html = _IMG.sub(one, html or "")
    # downloads inside the report (KML / KMZ) are kept as they are, and never touched by the number scrubbing
    html = re.sub(r'href="(data:[^"]+)"', lambda m: (keep.append(m.group(0)), f"\x00IMG{len(keep) - 1}\x00")[1], html)
    html = _IMG_ANY.sub('<span style="color:#5b6475;font-size:12px">[picture not kept online]</span>', html)
    if clean:
        html = clean(html)
    return re.sub(r"\x00IMG(\d+)\x00", lambda m: keep[int(m.group(1))], html)


def _rep_path(key):
    return "reports/" + re.sub(r"[^A-Za-z0-9_-]+", "_", str(key))[:120] + ".json"


def save_report(key, ver, appv, gist, html):
    if not key or not ver:
        return None
    rec = scrub({"key": key, "ver": ver, "appv": appv, "gist": gist, "at": int(time.time() * 1000)})
    rec["html"] = slim_html(html, scrub)
    with _lock:
        for attempt in range(3):
            try:
                _, sha = get(_rep_path(key))
                put(_rep_path(key), rec, sha, f"report {key}")
                break
            except ConflictError:
                time.sleep(1 + attempt)
    save_state({"reps": {key: {"ver": ver, "appv": appv, "at": rec["at"]}},
                "gists": {key: {"ver": ver, "gist": gist, "at": rec["at"]}} if gist else {}})
    return len(rec["html"])


def load_report(key):
    obj, _ = get(_rep_path(key))
    return obj


# ── disposed applications (no longer on the Dashboard list)
def archive_days():
    try:
        return max(1, int(os.environ.get("ARCHIVE_DAYS", "365")))
    except ValueError:
        return 365


def _trim_archive(arc):
    cut = int(time.time() * 1000) - archive_days() * 86400000
    return {k: v for k, v in (arc or {}).items() if isinstance(v, dict) and (v.get("disposedAt") or v.get("at") or 0) >= cut}


def save_disposed(items, back=()):
    """items: {key: slim application with disposedAt}; back: keys that are on the Dashboard again."""
    items = scrub(items or {})
    with _lock:
        for attempt in range(3):
            try:
                cur, sha = get("archive/disposed.json")
                cur = _merge(cur or {}, items)
                for k in back or ():
                    cur.pop(k, None)
                cur = _trim_archive(cur)
                put("archive/disposed.json", cur, sha, f"disposed: +{len(items)} −{len(back or ())}")
                return len(cur)
            except ConflictError:
                time.sleep(1 + attempt)
        raise RuntimeError("GitHub kept reporting a conflict — try again")


def load_disposed():
    obj, _ = get("archive/disposed.json")
    return _trim_archive(obj)


def check():
    """For the landing page: can we read and write?"""
    if not configured():
        return {"ok": False, "why": "DATA_REPO / GITHUB_TOKEN not set in Render"}
    try:
        r = requests.get(f"{API}/repos/{os.environ['DATA_REPO'].strip()}", headers=_h(), timeout=20)
        if r.status_code != 200:
            return {"ok": False, "why": _why(r)}
        j = r.json()
        if not j.get("private"):
            return {"ok": False, "why": f"{j.get('full_name')} is PUBLIC — make it private before saving any scan"}
        perms = j.get("permissions") or {}
        if perms and not perms.get("push", True):
            return {"ok": False, "why": "the token cannot write to the repo (Contents: Read and write needed)"}
        return {"ok": True, "repo": j.get("full_name"), "index": index()}
    except Exception as e:
        return {"ok": False, "why": str(e)[:200]}
