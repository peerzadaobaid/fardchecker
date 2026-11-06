# FARD CHECKER VERSION 1.9.7
"""Scan sync — keeps the last scan (per login) and the shared tracker state in a PRIVATE GitHub repo,
so any browser with the access key can open them.

Render settings (Environment):
    DATA_REPO     owner/repo of a private repo used only for data (NOT the code repo — that would redeploy the app)
    GITHUB_TOKEN  fine-grained token with access to that repo only, permission Contents: Read and write

Files written:
    scans/last-scan-<login>.json   the last scan of that login (application list, stages, remarks)
    scans/index.json               {login: {at, n, partial}}
    state/shared.json              gists / scores / points, owner & khata choices, pre-scrutiny points, photo prints
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


STATE_PARTS = ("gists", "choices", "points", "fps")


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
