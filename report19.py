# FARD CHECKER VERSION 1.9.4
"""Analysis report (v1.9).

Case 1 — Pre-scrutiny: only the applicant's submission (no Patwari report yet).
    1 Geotagged photograph (scale) · 2 Survey no. and its record · 3 Title and share (scale, owner drop-down)
    4 Documents checklist with Aadhaar (scale) · Overall (scale)
Case 2 — After the Patwari's report: everything of Case 1 kept; inside each retained section a box
    "After Patwari's report" adds what the report/tatima changes. Plus 4 Tatima (scale) and
    5 Patwari's report — contradictions (expected answers + record), and Overall with Case 1 points ✓/✗.
"""
import base64
import hashlib
import html as _html
import io
import json
import math
import os
import re

import engine as E
from engine import esc, km, norm, num, pf, parse_area, parse_date, kn, main_no, first_num, name_tokens, tok_match, similar, name_key, MARLA_M2, SQFT_PER_MARLA

# ───────────────────────────── small helpers ─────────────────────────────
LV_ORDER = {"red": 0, "amber": 1, "green": 2, "info": 3}
COL = {"red": "#b42318", "amber": "#8a5300", "green": "#145c36", "info": "#5b6475"}
ICON = {"red": "●", "amber": "▲", "green": "✓", "info": "ℹ"}
GOVT_LAND = re.compile(r"kah?charai|shamil?at|shamlat|khalsa|sarkar|state\s*land|nallah?|nala\b|sarak|rasta|road|kuhl|banjar\s*qadeem|graveyard|qabristan|maqbooza\s*sarkar|forest|jungle|govt|government", re.I)
GOVT_OWNER = re.compile(r"\bsarkar\b|khalsa|\bstate\b|govt|government|kahcharai|shamil?at|shamlat|maqbooza", re.I)
EDITORS = re.compile(r"photoshop|snapseed|picsart|lightroom|gimp|canva|meitu|facetune|pixlr|remini|vsco|polarr|inshot|picsay|photo\s*editor|photodirector|airbrush|beautycam|b612|youcam|faceapp|lensa|retouch", re.I)


def T(s):
    """Escape, but keep the <b> we add on purpose."""
    return esc(str(s)).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")


def new_sec(title):
    return {"title": title, "items": [], "box": [], "html": "", "box_html": "", "score": None}


def it(sec, level, text, point=None, box=False):
    """Add a finding. point = (id, wording for 'points to verify')."""
    (sec["box"] if box else sec["items"]).append({"lv": level, "t": text, "pt": point})


def levels(sec, box=True):
    return [x["lv"] for x in sec["items"] + (sec["box"] if box else [])]


def cap_score(score, lvls):
    if "red" in lvls:
        score = min(score, 35)
    elif "amber" in lvls:
        score = min(score, 69)
    return int(max(0, min(100, round(score))))


def band(score):
    if score is None:
        return "info", "Not assessed"
    return ("green", "Satisfactory") if score >= 70 else (("amber", "Doubtful") if score >= 40 else ("red", "Poor"))


STYLE = """<style>
.r19 .sc{margin:6px 0 8px;padding:8px 10px;background:#fff;border:1px solid #e1e4ea;border-radius:10px}
.r19 .sch{display:flex;justify-content:space-between;font-size:13px;font-weight:700}
.r19 .scb{position:relative;height:10px;border-radius:6px;margin:8px 0 2px;background:linear-gradient(90deg,#d92d20 0%,#f79009 45%,#f5c400 60%,#12b76a 80%,#067647 100%)}
.r19 .mk{position:absolute;top:-4px;width:0;height:0;margin-left:-7px;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #1d2330}
.r19 .scw{font-size:12px;color:#5b6475;margin-top:4px}
.r19 .it{margin:3px 0}.r19 .red{color:#b42318}.r19 .amber{color:#8a5300}.r19 .green{color:#145c36}.r19 .info{color:#5b6475}
.r19 .bx{margin:8px 0 4px;border:2px solid #12355b;border-radius:10px;padding:8px 10px;background:#f6f9fd}.r19 .bxh{font-weight:700;color:#12355b;font-size:13px;margin-bottom:4px}
.r19 .ch{display:inline-block;margin:2px 6px 2px 0;padding:3px 9px;border-radius:12px;font-size:12px;font-weight:600}
.r19 .ch.red{background:#fdecea}.r19 .ch.amber{background:#fff4e0}.r19 .ch.green{background:#e8f6ee}.r19 .ch.info{background:#eef0f4}
.r19 details.sec{background:#fff;border:1px solid #e1e4ea;border-radius:10px;margin:8px 0;padding:0 12px}
.r19 details.sec[open]{padding-bottom:10px}.r19 details.ov{border:2px solid #12355b}
.r19 details.sec>summary{cursor:pointer;list-style:none;padding:10px 0;display:block}.r19 details.sec>summary::-webkit-details-marker{display:none}
.r19 details.sec>summary .stt{font-weight:700;font-size:15px;margin-right:8px}.r19 details.sec>summary .stt:before{content:"▸ ";color:#5b6475}
.r19 details.sec[open]>summary .stt:before{content:"▾ "}.r19 .sl{font-size:12.5px;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.r19 details.sec[open]>summary .sl{display:none}
.r19 ol{margin:4px 0 6px 18px;padding:0;font-size:13.5px}.r19 li{margin:2px 0}.r19 .mu{color:#5b6475}
</style>"""


def scale_html(title, score, why=""):
    lv, word = band(score)
    mk = "" if score is None else f'<div class="mk" style="left:{score}%"></div>'
    return (f'<div class="sc"><div class="sch"><span>{esc(title)}</span><span class="{lv}">{"—" if score is None else str(score) + "/100"} · {word}</span></div>'
            f'<div class="scb">{mk}</div>' + (f'<div class="scw">{T(why)}</div>' if why else "") + '</div>')


def chip(title, score):
    lv, word = band(score)
    return f'<span class="ch {lv}">{esc(title)}: {"—" if score is None else score}</span>'


def items_html(items):
    out = []
    for x in items:
        if x["lv"] == "html":
            out.append(x["t"])
            continue
        lv = x["lv"]
        out.append(f'<div class="it{"" if lv == "info" else " " + lv}"><span class="{lv}">{ICON.get(lv, "•")}</span> {T(x["t"])}</div>')
    return "".join(out)


def box_html(items, title="After Patwari's report"):
    if not items:
        return ""
    return f'<div class="bx"><div class="bxh">{esc(title)}</div>{items_html(items)}</div>'


def is_yes(s):
    return bool(re.match(r"\s*y(es)?\b", s or "", re.I))


def is_no(s):
    return bool(re.match(r"\s*no?\b", s or "", re.I)) and not re.match(r"\s*none", s or "", re.I)


# ───────────────────────────── context ─────────────────────────────
class Ctx:
    pass


def prepare(app, ai):
    c = Ctx()
    f = c.f = app.get("fields") or {}
    c.app = app
    c.ai = ai or {}
    c.free = c.ai.get("mode") == "free"
    c.reader = {"gemini": "Gemini", "claude": "Claude"}.get(c.ai.get("mode"), "AI")
    c.village = pf(f, "villageD") or norm(app.get("village"))
    k = pf(f, "cKhasra") if not E.is_pending(pf(f, "cKhasra")) else (pf(f, "aKhasra") or norm(app.get("khasra")))
    c.khasra = kn(re.split(r"[,;]", k)[0]) if k else ""
    c.applicant = pf(f, "applicant") or norm(app.get("name"))
    c.applied = parse_area(pf(f, "areaProposed")) or parse_area(app.get("area"))
    c.cert_area = None
    if any(pf(f, x) for x in ("cKanal", "cMarla", "cSqft")):
        c.cert_area = 20 * (num(pf(f, "cKanal")) or 0) + (num(pf(f, "cMarla")) or 0) + (num(pf(f, "cSqft")) or 0) / SQFT_PER_MARLA
    if c.applied is None:
        c.applied = c.cert_area
    pr = norm(app.get("patReport"))
    filled = any(not E.is_pending(pf(f, x)) for x in ("possession", "fit", "cKhewat", "soil"))
    c.case = 2 if (pr == "Submitted" or (not pr and filled)) else 1
    c.v = E.load_village(c.village) if c.village else None
    c.K = main_no(c.khasra, c.v) if c.khasra else ""
    c.p = E.parcel_for(c.v, c.khasra) if c.v and c.khasra else None
    c.jbs = E.jb_info(c.v, c.khasra) if c.v and c.khasra else None
    c.fam = E.khasra_family(c.v, c.khasra) if c.v and c.khasra else []
    c.jb = (c.jbs or [None])[0] or next((e for e in c.fam if e["relation"] == "same number"), c.fam[0] if c.fam else None)
    c.nbs = E.neighbours(c.v, c.p) if c.p else []
    c.near = None
    if not c.p and c.v and c.v.get("map") and c.khasra:
        q, asked = E.nearest_on_map(c.v, c.khasra)
        if q:
            c.near = {"asked": asked, "shown": q["khasra"]}
            c.map_p, c.map_nbs = q, E.neighbours(c.v, q)
    if c.p:
        c.map_p, c.map_nbs = c.p, c.nbs
    if not c.p and not c.near:
        c.map_p, c.map_nbs = None, []
    c.hist = app.get("history") or []
    c.remarks_text = " | ".join([pf(f, "patRemarks"), pf(f, "girRemarks"), pf(f, "ntRemarks"), pf(f, "lambardar")]
                                + [norm(h.get("remark")) for h in c.hist])
    return c


# ───────────────────────────── 1. Geotagged photograph ─────────────────────────────
def exif_of(raw):
    out = {}
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw))
        ex = im.getexif()
        if not ex:
            return out
        sub = {}
        try:
            sub = ex.get_ifd(0x8769) or {}
        except Exception:
            pass
        out = {"make": norm(ex.get(271)), "model": norm(ex.get(272)), "software": norm(ex.get(305)),
               "datetime": norm(sub.get(36867) or ex.get(306))}
        return {k: v for k, v in out.items() if v}
    except Exception:
        return out


def ela_png(raw):
    """Error-level analysis: re-save at a known JPEG quality and show where the picture differs most."""
    try:
        from PIL import Image, ImageChops
        import numpy as np
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        im.thumbnail((900, 900))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=90)
        re_ = Image.open(io.BytesIO(buf.getvalue())).convert("RGB")
        d = np.asarray(ImageChops.difference(im, re_), dtype=np.float32).max(axis=2)
        hi = np.percentile(d, 99.5) or 1
        v = np.clip(d / hi, 0, 1)
        # heat colours: dark blue → yellow → red
        r = np.clip(v * 2.2, 0, 1)
        g = np.clip(v * 1.6 - 0.2, 0, 1)
        b = np.clip(0.35 - v, 0, 1)
        heat = Image.fromarray((np.dstack([r, g, b]) * 255).astype("uint8"))
        heat.thumbnail((360, 360))
        out = io.BytesIO()
        heat.save(out, "PNG", optimize=True)
        return base64.b64encode(out.getvalue()).decode()
    except Exception:
        return None


def dhash(img_b64_or_bytes):
    try:
        from PIL import Image
        raw = img_b64_or_bytes if isinstance(img_b64_or_bytes, (bytes, bytearray)) else base64.b64decode(img_b64_or_bytes)
        im = Image.open(io.BytesIO(raw)).convert("L").resize((17, 16))
        px = list(im.getdata())
        bits = 0
        for y in range(16):
            for x in range(16):
                bits = (bits << 1) | (1 if px[y * 17 + x] > px[y * 17 + x + 1] else 0)
        return f"{bits:064x}"
    except Exception:
        return ""


def ham(a, b):
    try:
        return bin(int(a, 16) ^ int(b, 16)).count("1")
    except Exception:
        return 999


def photo_section(c, photo_page, other_fps):
    s = new_sec("1 · Geotagged photograph")
    ph = c.ai.get("photo") or {}
    f = c.f
    lat = num(ph.get("lat")) if ph.get("found") else None
    lng = num(ph.get("lng")) if ph.get("found") else None
    c.geo, c.point, c.photo_hash, c.ela, c.photo_thumb = None, None, "", None, None
    if not ph.get("found") and not photo_page:
        it(s, "red", "No geotagged photograph found among the applicant's documents.", ("photo-missing", "Geotagged photograph of the land not uploaded."))
        s["score"] = cap_score(0, ["red"])
        return s
    raw = (photo_page or {}).get("orig")
    # where the point falls
    if lat is None or lng is None:
        it(s, "amber", "The GPS stamp on the photo could not be read (no latitude/longitude found).", ("photo-nogps", "Geotag (lat/long) on the photograph not legible / absent."))
    else:
        c.geo = (lat, lng)
        it(s, "info", f"Stamp reads {lat:.6f}, {lng:.6f}" + (f" · Plus Code {esc(ph.get('pluscode'))}" if ph.get("pluscode") else "")
           + (f" · {esc(ph.get('datetime'))}" if ph.get("datetime") else "") + (f" ({esc(ph.get('place_label'))})" if ph.get("place_label") else "") + ".")
        if c.v and c.v.get("map"):
            pm, inside, dist = E.locate_point(c.v, lat, lng, c.p)
            c.point = pm
            if c.p and c.p["m"].contains(pm):
                it(s, "green", f"The point falls <b>inside</b> survey no. {esc(c.p['khasra'])} (about {c.p['m'].centroid.distance(pm):.0f} m from its centre).")
            elif c.p and dist is not None and dist <= 20:
                it(s, "info", f"The point is {dist:.0f} m outside survey no. {esc(c.p['khasra'])} — within the 20 m GPS tolerance.")
            elif c.p and dist is not None:
                where = (f"it falls in khasra {inside['khasra'] or '(unnumbered parcel)'}" if inside else "it is not inside any parcel of this village")
                it(s, "red", f"The point is <b>outside</b> survey no. {esc(c.p['khasra'])}, {dist:.0f} m away; {esc(where)}.",
                   ("photo-outside", f"Geotag falls {dist:.0f} m outside survey no. {c.p['khasra']} — fresh geotagged photograph of the land required."))
            elif c.near:
                it(s, "amber", f"Survey no. {esc(c.near['asked'])} is not on the village map, so the point could not be checked against it"
                   + (f"; it falls in khasra {esc(inside['khasra'] or '(unnumbered)')}" if inside else "") + ".",
                   ("photo-unchecked", f"Location of survey no. {c.near['asked']} to be verified on spot (not on village map)."))
            elif not inside:
                it(s, "red", "The point is not inside this village's map.", ("photo-village", "Geotag lies outside the village — verify."))
    # Plus Code vs lat/long. The camera app prints the Plus Code of its address lookup, not of the exact GPS fix,
    # so tens of metres apart is normal (genuine photos show 40–70 m); only a large gap points to a typed / reused location.
    if ph.get("pluscode") and lat is not None:
        try:
            import pluscode
            plat, plng, h = pluscode.recover(ph["pluscode"], lat, lng)
            d = math.hypot((plat - lat) * 111000, (plng - lng) * 111000 * math.cos(math.radians(lat)))
            if d <= 120:
                it(s, "green", f"Plus Code and lat/long agree ({d:.0f} m apart — normal for the camera app's address line).")
            elif d <= 300:
                it(s, "amber", f"Plus Code and lat/long are {d:.0f} m apart — more than usual.",
                   ("photo-pluscode", "Plus Code and lat/long on the geotag stamp do not agree — verify the photograph."))
            else:
                it(s, "red", f"Plus Code and lat/long are <b>{d:.0f} m apart</b> — they cannot come from the same place; the location was likely typed in or the stamp reused.",
                   ("photo-pluscode", "Geotag stamp inconsistent (Plus Code vs lat/long) — fresh geotagged photograph required."))
        except Exception:
            pass
    # date
    pdt = parse_date(ph.get("datetime") or "") if ph.get("datetime") else None
    adt = parse_date(c.app.get("appDate") or "")
    if not ph.get("datetime"):
        it(s, "amber", "No date/time on the GPS stamp — the photo cannot be tied to this application.", ("photo-nodate", "Geotag stamp carries no date/time."))
    elif pdt and adt:
        gap = (adt - pdt).days
        if gap > 180:
            it(s, "red", f"Photo dated {pdt:%d %b %Y}, {gap} days before the application.", ("photo-old", "Geotagged photograph is old — fresh photograph required."))
        elif gap > 60:
            it(s, "amber", f"Photo dated {pdt:%d %b %Y}, {gap} days before the application.", ("photo-old", "Geotagged photograph is not recent."))
        else:
            it(s, "green", f"Photo dated {pdt:%d %b %Y} — recent.")
    # hidden camera data
    ex = exif_of(raw) if raw else {}
    if ex:
        bits = [f"camera {ex.get('make', '')} {ex.get('model', '')}".strip()] if (ex.get("make") or ex.get("model")) else []
        if ex.get("datetime"):
            bits.append("taken " + ex["datetime"])
        if ex.get("software"):
            bits.append("saved by " + ex["software"])
        if EDITORS.search(ex.get("software", "")):
            it(s, "red", f"The photo file was saved by an <b>editing app</b> ({esc(ex['software'])}).", ("photo-edited", "Photograph saved by an editing app — original photograph required."))
        else:
            it(s, "info", "Camera data in the file: " + esc("; ".join(b for b in bits if b)) + ".")
    # same photo in another application
    src = raw or (photo_page or {}).get("data")
    c.photo_hash = dhash(src) if src else ""
    if c.photo_hash:
        for o in other_fps or []:
            if o.get("app") and o.get("app") != c.app.get("appNo") and ham(c.photo_hash, o.get("hash", "")) <= 8:
                it(s, "red", f"<b>Same photograph</b> as application {esc(o['app'])} — reused photo.", ("photo-reused", f"Same photograph used in application {o['app']}."))
                break
    # AI view on editing / person replaced
    es = (ph.get("editing_signs") or "").lower()
    if es in ("likely", "possible"):
        it(s, "red" if es == "likely" else "amber", f"{c.reader}: {'likely' if es == 'likely' else 'possible'} signs of editing — {esc(ph.get('editing_note') or 'see photo')}.",
           ("photo-ai-edit", "Possible editing / replaced person in the photograph — verify on spot."))
    # the heat-map
    c.ela = ela_png(raw) if raw and (raw[:3] == b"\xff\xd8\xff") else None
    if photo_page and photo_page.get("data"):
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(base64.b64decode(photo_page["data"]))).convert("RGB")
            im.thumbnail((360, 360))
            b = io.BytesIO()
            im.save(b, "JPEG", quality=70)
            c.photo_thumb = base64.b64encode(b.getvalue()).decode()
        except Exception:
            pass
    # Case 2 box: point vs shaded side / on-spot
    if c.case == 2:
        tt = c.ai.get("tatima") or {}
        side = (tt.get("shaded_side") or "").lower()
        if c.point is not None and c.p and c.p["m"].contains(c.point) and side in ("north", "south", "east", "west"):
            mnx, mny, mxx, mxy = c.p["m"].bounds
            fx, fy = (c.point.x - mnx) / max(1e-6, mxx - mnx), (c.point.y - mny) / max(1e-6, mxy - mny)
            where = {"north": fy > 0.5, "south": fy < 0.5, "east": fx > 0.5, "west": fx < 0.5}[side]
            it(s, "green" if where else "amber", f"Geotag lies in the {'same' if where else 'other'} part of the khasra as the shaded {side} portion.",
               None if where else ("photo-side", f"Geotag is not on the shaded ({side}) portion — verify spot of the land applied."), box=True)
        bu = (ph.get("built_up") or "").lower()
        onspot = pf(f, "onspot")
        if onspot and bu in ("yes", "no"):
            vac, blt = bool(re.search(r"vacant|open|agri|cultiv", onspot, re.I)), bool(re.search(r"built", onspot, re.I))
            if blt and not vac and bu == "no":
                it(s, "amber", f"Report says on-spot “{esc(onspot)}”, the photo shows open land.", ("onspot-photo", "On-spot position does not match the photograph."), box=True)
            elif vac and not blt and bu == "yes":
                it(s, "amber", f"Report says on-spot “{esc(onspot)}”, the photo shows a structure.", ("onspot-photo", "On-spot position does not match the photograph."), box=True)
    lv = levels(s)
    s["score"] = cap_score(100 - 12 * lv.count("amber") - 30 * lv.count("red"), lv)
    return s


# ───────────────────────────── 2. Survey no. and its record ─────────────────────────────
def survey_section(c):
    s = new_sec(f"2 · Survey no. {c.K or c.khasra or '?'} and its record")
    c.total = c.alien = None
    c.alien_rows = []
    if not c.v:
        _, why = E.match_village(c.village)
        it(s, "red", why, ("village", f"Village records for {c.village} not available to the checker."))
        s["score"] = None
        return s
    if not c.v.get("jb"):
        it(s, "amber", "No Jamabandi on file for this village.")
        s["score"] = None
        return s
    K = c.K
    if K != kn(c.khasra) and K == (re.findall(r"\d+", kn(c.khasra)) or [""])[-1]:
        it(s, "info", f"Khasra {esc(c.khasra)} is a new number under main survey no. <b>{esc(K)}</b>; map location and total area are taken for {esc(K)}.")
    if not c.fam:
        it(s, "red", f"No entry for survey no. {esc(K)} (or {esc(K)} min, …/{esc(K)}) in the Jamabandi on file.",
           ("survey-missing", f"Survey no. {c.khasra} not found in the digitised Jamabandi of {c.village}."))
        s["score"] = cap_score(10, ["red"])
        return s
    TD = '<td style="padding:4px 6px;border-bottom:1px solid #eceef2;vertical-align:top">'
    rows = ['<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:12.5px;margin:4px 0">'
            '<tr style="background:#f0f2f6"><th style="text-align:left;padding:4px 6px">Khasra</th><th style="text-align:left;padding:4px 6px">Khewat / Khata</th>'
            '<th style="text-align:right;padding:4px 6px">Area</th><th style="text-align:left;padding:4px 6px">Land type</th>'
            '<th style="text-align:left;padding:4px 6px">Mutation</th><th style="text-align:left;padding:4px 6px">Cultivator</th></tr>']
    total = alien = 0.0
    for e in c.fam:
        total += e["area_marla"] or 0
        tr = bool(e["mut_type"]) and bool(E.TRANSFER.search(e["mut_type"])) and not re.search(r"inherit|warasat", e["mut_type"], re.I)
        if tr:
            alien += e["area_marla"] or 0
            owners = c.v["jb"]["khewats"].get(e["khewat"], {}).get("owners", "")
            c.alien_rows.append((e, owners))
        mine = kn(e["khasra"]) == kn(c.khasra)
        rows.append(f'<tr style="{"background:#fff7da;" if tr else ""}">{TD}<b>{esc(e["khasra"])}</b>{" <b style=color:#12355b>◀ applied</b>" if mine else ""}</td>'
                    f'{TD}{esc(e["khewat_no"])} / {esc(e["khata_no"])}</td><td style="padding:4px 6px;border-bottom:1px solid #eceef2;text-align:right;white-space:nowrap">{km(e["area_marla"])}</td>'
                    f'{TD}{esc(e["qism"])}</td>{TD}{esc((e["mut_no"] or "—") + (" " + e["mut_type"] if e["mut_type"] else ""))}</td>{TD}{esc(e["cultivator"][:120])}</td></tr>')
    rows.append(f'<tr style="font-weight:700"><td colspan="2" style="padding:4px 6px">Total ({len(c.fam)} entr{"y" if len(c.fam) == 1 else "ies"})</td>'
                f'<td style="padding:4px 6px;text-align:right;white-space:nowrap">{km(total)}</td><td colspan="3"></td></tr></table></div>')
    s["items"].append({"lv": "html", "t": "".join(rows), "pt": None})
    c.total, c.alien = total, alien
    bal = total - alien
    if c.alien_rows:
        it(s, "info", f"<b>Alienated</b> out of survey no. {esc(K)}: <b>{km(alien)}</b> of {km(total)} (rows shaded above):")
        for e, owners in c.alien_rows:
            oe = E.owner_entries(owners)
            it(s, "info", f"&nbsp;&nbsp;• {esc(e['khasra'])}: {km(e['area_marla'])} by mutation {esc(e['mut_no'] or '—')} ({esc(e['mut_type'])}) → now held by "
                          f"{esc(_owner_name(oe[0]) if oe else '—')}" + (f" and {len(oe) - 1} other(s)" if len(oe) > 1 else ""))
    else:
        it(s, "info", f"<b>Alienated</b>: nothing — no sale / gift / partition is recorded against survey no. {esc(K)}.")
    it(s, "info", f"Balance not yet alienated: <b>{km(bal)}</b>" + (f" · area applied {km(c.applied)}" if c.applied is not None else "") + ".")
    if c.applied is not None:
        if c.applied > total + 0.25:
            it(s, "red", f"Area applied ({km(c.applied)}) is more than the whole survey no. ({km(total)}).",
               ("survey-exceeds", f"Area applied {km(c.applied)} exceeds total area {km(total)} of survey no. {K}."))
        elif c.applied > bal + 0.25:
            it(s, "amber", f"Area applied ({km(c.applied)}) is more than the part not yet alienated ({km(bal)}).",
               ("survey-balance", f"Area applied {km(c.applied)} exceeds the unalienated balance {km(bal)} of survey no. {K}."))
        else:
            it(s, "green", f"Area applied ({km(c.applied)}) is within the unalienated balance ({km(bal)}).")
    # map
    if c.v.get("map"):
        on_map = [q for q in c.v["map"]["parcels"] if main_no(q["khasra"], c.v) == K]
        if on_map:
            m2 = sum(q["m"].area for q in on_map) / MARLA_M2
            if total and abs(m2 - total) > max(3, 0.15 * total):
                it(s, "amber", f"Measured on the map {km(m2)} against {km(total)} in the Jamabandi (more than 15% apart).")
        elif c.near:
            it(s, "amber", f"Survey no. {esc(K)} is not drawn on the village map — nearest available {esc(c.near['shown'])} is shown for locality only.")
    # Case 2 box: certificate vs record, final mutation
    if c.case == 2:
        f = c.f
        jb = c.jb
        if jb:
            ck, ckt = first_num(pf(f, "cKhewat")), first_num(pf(f, "cKhata"))
            if ck and ck != jb["khewat_no"]:
                it(s, "red", f"Khewat on certificate {esc(ck)} ≠ Jamabandi {esc(jb['khewat_no'])}.", ("cert-khewat", f"Correct khewat number ({ck} vs {jb['khewat_no']})."), box=True)
            if ckt and ckt != jb["khata_no"]:
                it(s, "red", f"Khata on certificate {esc(ckt)} ≠ Jamabandi {esc(jb['khata_no'])}.", ("cert-khata", f"Correct khata number ({ckt} vs {jb['khata_no']})."), box=True)
            if ck and ckt and ck == jb["khewat_no"] and ckt == jb["khata_no"]:
                it(s, "green", f"Khewat {esc(ck)} / khata {esc(ckt)} on the certificate agree with the Jamabandi.", box=True)
        if c.applied is not None and c.cert_area is not None and abs(c.applied - c.cert_area) > 0.25:
            it(s, "amber", f"Area proposed {km(c.applied)} ≠ area on certificate {km(c.cert_area)}.", ("cert-area", "Reconcile area proposed with certificate area."), box=True)
        mut = c.app.get("mut") or {}
        final = [r for r in (mut.get("final") or []) if any(re.search(r"\d", str(x)) for x in r.values())]
        gist = [r for r in (mut.get("gist") or []) if any(re.search(r"\d", str(x)) for x in r.values())]
        for r in final:
            g_ = lambda pat, r=r: next((norm(v_) for k_, v_ in r.items() if re.search(pat, k_, re.I)), "")
            mn = first_num(g_(r"mutation\s*no"))
            it(s, "info", f"Final mutation (portal): No. {esc(mn or '—')}, {esc(g_(r'type') or '—')}, {esc(g_(r'date') or '—')}; "
                          f"{esc(g_(r'first')[:120])} → {esc(g_(r'second')[:100])}.", box=True)
            if mn and jb and jb["mut_no"] and mn != first_num(jb["mut_no"]):
                it(s, "info", f"Mutation {esc(mn)} is not yet in the Jamabandi copy on file (it shows {esc(jb['mut_no'])}).", box=True)
        if not final:
            it(s, "amber", "No final mutation in the applicant's name is shown on the portal.", ("mut-final", "Show the final mutation in which the applicant's name appears."), box=True)
        if final and not gist and jb and jb["mut_no"]:
            it(s, "amber", "“Gist of all successive mutations” is empty.", ("mut-gist", "Fill the gist of successive mutations."), box=True)
    lv = levels(s)
    s["score"] = cap_score(95 - 10 * lv.count("amber") - 30 * lv.count("red"), lv)
    return s


# ───────────────────────────── 3. Title and share ─────────────────────────────
AREA_RE = re.compile(r"(-?\d+)\s*kanal\s*(-?\d+)\s*mar\w*\s*(?:(\d+)\s*(?:marabba|sq)\w*\s*(?:foot|feet|ft)?)?", re.I)
REL_RE = re.compile(r"\b(pisaran|pisar|dukhtaran|dukhter|byuh|s/o|d/o|w/o|son of|daughter of|wife of)\b\s*(.*)$", re.I)


def _owner_name(entry):
    t = re.split(r"\d|\b(?:s/o|d/o|w/o|pisar\w*|dukht\w*|byuh|son of|daughter of|wife of|sakin|sakindeh)\b", entry, 1, flags=re.I)[0]
    return norm(t).strip(" .,-").title() or norm(entry)[:40]


def parse_owners(text):
    """Owner column → [{name, parent, area, fraction, entry}] (parentage of 'pisaran/dukhtaran' groups carried back)."""
    out, group = [], []
    for e in E.owner_entries(text):
        o = {"entry": e, "name": _owner_name(e), "parent": "", "area": None, "fraction": None}
        m = AREA_RE.search(e)
        if m:
            o["area"] = 20 * int(m.group(1)) + int(m.group(2)) + (int(m.group(3) or 0) / SQFT_PER_MARLA)
        fr = re.search(r"(\d+)\s*/\s*(\d+)\s*$", e) or re.search(r"sakin\w*\s+(\d+)\s*/\s*(\d+)", e, re.I)
        if fr and not m:
            o["fraction"] = (int(fr.group(1)), int(fr.group(2)))
        r = REL_RE.search(e)
        if r:
            par = re.split(r"\bsakin(?:deh)?\b|\bkaum\b|\d", r.group(2), 1, flags=re.I)[0]
            o["parent"] = norm(par).strip(" ,.").title()
            o["rel"] = r.group(1).lower()
            if r.group(1).lower() in ("pisaran", "dukhtaran"):
                for g in group:
                    if not g["parent"]:
                        g["parent"] = o["parent"]
            group = []
        else:
            group.append(o)
        out.append(o)
    return out


def _who_matches(a, b):
    ka, kb = name_key(a), name_key(b)
    if not ka or not kb:
        return 0.0
    s1 = similar(ka, kb)
    ta, tb = name_tokens(a), name_tokens(b)
    s2 = similar(ta[0], tb[0]) if ta and tb else 0
    return max(s1, 0.85 * s2 if len(ta) == 1 or len(tb) == 1 else 0.6 * s2 + 0.4 * s1)


def _strict(a, b):
    """Whole-name match (for predecessors and mutation parties): a lone 'Mohammad' must not match 'Mohammad Ismail'."""
    ka, kb = name_key(a), name_key(b)
    if not ka or not kb:
        return False
    if similar(ka, kb) >= 0.85:
        return True
    ta, tb = name_tokens(a), name_tokens(b)
    return len(ta) >= 2 and len(tb) >= 2 and tok_match(ta[0], tb[0], 0.85) and tok_match(ta[1], tb[1], 0.8)


def _mut_parties(c):
    """Transfers from the portal (final/gist) and from AI-read documents: [(no, type, from_text, to_text, area, src)]."""
    out = []
    mut = c.app.get("mut") or {}
    for r in (mut.get("final") or []) + (mut.get("gist") or []):
        if not any(re.search(r"\d", str(x)) for x in r.values()):
            continue
        g_ = lambda pat, r=r: next((norm(v_) for k_, v_ in r.items() if re.search(pat, k_, re.I)), "")
        q = 20 * (num(g_(r"^\s*kanal")) or 0) + (num(g_(r"^\s*marla")) or 0) + (num(g_(r"sq")) or 0) / SQFT_PER_MARLA
        out.append((first_num(g_(r"mutation\s*no")), g_(r"type"), g_(r"first"), g_(r"second"), q, "portal"))
    for m_ in c.ai.get("mutations") or []:
        fr = ", ".join(norm(t.get("name")) for t in m_.get("from") or [])
        to = ", ".join(norm(t.get("name")) for t in m_.get("to") or [])
        q = sum(num(t.get("area_marla")) or 0 for t in (m_.get("to") or [])) or sum(num(t.get("area_marla")) or 0 for t in (m_.get("from") or []))
        out.append((first_num(m_.get("number")), m_.get("type") or "", fr, to, q, c.reader))
    seen, uniq = set(), []
    for x in out:
        k = (x[0], x[2][:20], x[3][:20])
        if x[0] and k in seen:
            continue
        seen.add(k)
        uniq.append(x)
    return uniq


def owner_figures(c, kw, o, owners):
    """Share in khewat → indicative holding in the survey no. → received / alienated → balance."""
    kwd = c.v["jb"]["khewats"].get(kw, {})
    kw_area = kwd.get("area_marla")
    surv = sum(e["area_marla"] or 0 for e in c.fam if e["khewat"] == kw)
    steps, holding, how = [], None, ""
    kwno = first_num(kw)
    if o["area"] is not None:
        steps.append(f"Share in khewat {kwno} (ownership column): <b>{km(o['area'])}</b>" + (f" of {km(kw_area)}" if kw_area else ""))
        if kw_area:
            holding = o["area"] / kw_area * surv
            how = f"{km(o['area'])} ÷ {km(kw_area)} × {km(surv)} (survey no. {c.K} in this khewat)"
    elif o["fraction"]:
        a, b = o["fraction"]
        steps.append(f"Share in khewat {kwno} (ownership column): <b>{a}/{b}</b> of the share of {esc(o['parent'] or 'the predecessor')}")
        pred = next((x for x in owners if x is not o and x["area"] is not None and o["parent"] and _strict(x["name"], o["parent"])), None)
        if pred and kw_area:
            holding = pred["area"] / kw_area * surv * a / b
            how = f"{a}/{b} × {esc(pred['name'])}'s {km(pred['area'])} ÷ {km(kw_area)} × {km(surv)}"
        else:
            ent = next((e for e in c.fam if e["khewat"] == kw), None)
            cult = (ent or {}).get("cultivator", "")
            if o["parent"] and cult and (_strict(o["parent"], re.sub(r"^\s*kasht\s*|\d.*$", "", cult, flags=re.I)) or _who_matches(o["parent"], re.sub(r"^\s*kasht\s*|\d.*$", "", cult, flags=re.I)) >= 0.8):
                holding = surv * a / b
                how = f"{a}/{b} × {km(surv)} — survey no. {c.K} is in the possession of {esc(o['parent'])} (cultivator column)"
    else:
        steps.append(f"Share in khewat {kwno}: not stated as an area or fraction in the ownership column")
    if holding is not None:
        steps.append(f"Indicative share in survey no. {esc(c.K)}: <b>{km(holding)}</b> <span class='mu'>({how})</span>")
    else:
        steps.append(f"Share in survey no. {esc(c.K)}: cannot be worked out from the Jamabandi alone")
    rec = giv = 0.0
    det_r, det_g = [], []
    for mno, mty, fr, to, q, src in _mut_parties(c):
        if re.search(r"inherit|warasat", mty or "", re.I):
            continue
        if to and any(_strict(o["name"], _owner_name(t)) for t in re.split(r",|&| and |\(", to)) and q:
            rec += q
            det_r.append(f"mutation {mno or '—'} ({mty or '—'}) {km(q)} from {fr[:60] or '—'} [{src}]")
        elif fr and any(_strict(o["name"], _owner_name(t)) for t in re.split(r",|&| and |\(", fr)) and q:
            giv += q
            det_g.append(f"mutation {mno or '—'} ({mty or '—'}) {km(q)} to {to[:60] or '—'} [{src}]")
    if det_r:
        steps.append("Received later: <b>+" + km(rec) + "</b> — " + esc("; ".join(det_r)))
    steps.append("Alienated by this owner: <b>" + (("−" + km(giv)) if giv else "nil found") + "</b>" + (" — " + esc("; ".join(det_g)) if det_g else
                 " <span class='mu'>(the Jamabandi does not record who sold; only mutations on the portal / in the documents are counted)</span>"))
    bal = (holding + rec - giv) if holding is not None else (rec - giv if rec else None)
    return {"steps": steps, "holding": holding, "rec": rec, "giv": giv, "balance": bal, "kw": kwno, "kw_area": kw_area, "surv": surv}


def title_section(c):
    """Returns (sections_per_owner, options, default_index)."""
    opts, variants = [], []
    if not c.v or not c.v.get("jb") or not c.fam:
        s = new_sec("3 · Title and share")
        it(s, "amber", "Title could not be checked — survey no. not found in the Jamabandi on file.",
           ("title-unchecked", "Title of the applicant to be verified from the revenue record."))
        s["score"] = cap_score(50, ["amber"])
        return [s], [], -1
    kws = list(dict.fromkeys(e["khewat"] for e in c.fam if e.get("khewat")))
    hint = ""
    m = re.search(r"(?:son|daughter|wife)\s+of\s+(.+?)(?:\bwife\b|$)|\b[sdw]/o\s+(.+?)(?:\bw/o\b|$)", pf(c.f, "owners") or pf(c.f, "ownRecords"), re.I)
    if m:
        hint = m.group(1) or m.group(2) or ""
    cand = []
    for kw in kws:
        owners = parse_owners(c.v["jb"]["khewats"].get(kw, {}).get("owners", ""))
        for o in owners:
            sc = _who_matches(c.applicant, o["name"])
            if hint and o["parent"]:
                sc += 0.15 * _who_matches(hint, o["parent"])
            cand.append((kw, o, owners, sc))
    c.n_owners = len(cand)
    cand = sorted(cand, key=lambda x: -x[3])[:30]          # the 30 closest names are offered in the list
    best = 0 if cand else -1
    default = best if best >= 0 and cand[best][3] >= 0.8 else -1
    # documents naming the applicant (for the amber rule)
    fd = c.ai.get("fard") or {}
    doc_names = " ".join([norm(fd.get("owner_entry")), " ".join(norm(t.get("name")) for m_ in c.ai.get("mutations") or [] for t in (m_.get("to") or []))])
    docs_support = bool(doc_names.strip()) and any(_who_matches(c.applicant, w) >= 0.82 for w in re.split(r",|;|\band\b", doc_names) if w.strip())
    # the "not found" variant
    s = new_sec("3 · Title and share")
    if docs_support:
        it(s, "amber", f"“{esc(c.applicant)}” is <b>not traced</b> among the owners in the Jamabandi on file, but the uploaded "
                       f"fard / mutation names the applicant — possibly a recent mutation not yet in the digitised copy.",
           ("title-notfound", f"Title of {c.applicant} not traced in the digitised Jamabandi — verify from the latest record / mutation."))
        s["score"] = cap_score(45, ["amber"])
    else:
        it(s, "red", f"“{esc(c.applicant)}” is <b>not recorded</b> among the owners of survey no. {esc(c.K)} (khewat {', '.join(first_num(k) for k in kws)}) "
                     f"in the Jamabandi on file, and no uploaded document shows how the applicant became owner.",
           ("title-notfound", f"Applicant {c.applicant} not recorded as owner in survey no. {c.K} as per the digitised Jamabandi."))
        s["score"] = cap_score(10, ["red"])
    if cand:
        close = sorted(cand, key=lambda x: -x[3])[:3]
        it(s, "info", "Closest names in the ownership column: " + esc("; ".join(f"{x[1]['name']}" + (f" ({x[1].get('rel', 's/o')} {x[1]['parent']})" if x[1]['parent'] else "") for x in close))
           + ". If one of them is the applicant, choose it in the list above.")
    _title_box(c, s, None)
    variants_nf = s
    for i, (kw, o, owners, sc) in enumerate(cand):
        s = new_sec("3 · Title and share")
        fig = owner_figures(c, kw, o, owners)
        it(s, "info", f"Owner: <b>{esc(o['name'])}</b>" + (f" ({esc(o.get('rel', ''))} {esc(o['parent'])})" if o["parent"] else "")
           + f" — khewat {esc(first_num(kw))}" + ("" if i == default else " — chosen in the list") + ".")
        it(s, "info", f"Entry as written: “{esc(o['entry'][:220])}”.")
        steps = "".join(f"<li>{x}</li>" for x in fig["steps"])
        bal = fig["balance"]
        if bal is not None:
            steps += f"<li>Balance: <b>{km(bal)}</b>" + (f" · area applied <b>{km(c.applied)}</b>" if c.applied is not None else "") + "</li>"
        s["items"].append({"lv": "html", "t": f"<ol>{steps}</ol>", "pt": None})
        lvset = []
        if c.applied is not None and bal is not None:
            if c.applied > bal + 0.25:
                it(s, "red", f"Area applied ({km(c.applied)}) <b>exceeds</b> the balance ({km(bal)}) — not eligible for the full area.",
                   ("title-exceeds", f"Area applied {km(c.applied)} exceeds the applicant's balance share {km(bal)} in survey no. {c.K}."))
            else:
                it(s, "green", f"Area applied ({km(c.applied)}) is within the balance ({km(bal)}) — eligible on record.")
        elif c.applied is not None:
            it(s, "amber", "The share could not be converted to an area for this survey no. — eligibility for the area applied to be confirmed.",
               ("title-unknown", f"Applicant's share in survey no. {c.K} to be worked out (fraction of predecessor's share)."))
        if len(owners) > 1:
            it(s, "info", f"Joint khewat: {len(owners)} owner entries.")
        _title_box(c, s, fig, joint=len(owners) > 1)
        lv = levels(s)
        s["score"] = cap_score(92 - (8 if sc < 0.9 and i == default else 0) - 12 * lv.count("amber") - 30 * lv.count("red"), lv)
        variants.append(s)
        lab = f"{o['name']}" + (f" ({o.get('rel', '')} {o['parent']})" if o["parent"] else "") + f" — khewat {first_num(kw)}" + \
              (f" · {km(o['area'])}" if o["area"] is not None else (f" · {o['fraction'][0]}/{o['fraction'][1]}" if o["fraction"] else ""))
        opts.append(lab)
    return [variants_nf] + variants, opts, default


def _title_box(c, s, fig, joint=False):
    if c.case != 2:
        return
    f = c.f
    skw, skh = pf(f, "shareKhewat"), pf(f, "shareKhasra")
    ak, akh = pf(f, "alienKhewat"), pf(f, "alienKhasra")
    rows = [("Share in khewat", skw), ("Share in khasra", skh), ("Already alienated in khewat", ak), ("Already alienated in khasra", akh)]
    txt = " · ".join(f"{a}: <b>{esc(b or '—')}</b>" for a, b in rows)
    it(s, "info", "Patwari's figures — " + txt + ".", box=True)
    if fig:
        hk = parse_area(skh)
        if hk is not None and fig["balance"] is not None and abs(hk - fig["balance"]) > max(1.0, 0.05 * fig["balance"]):
            it(s, "amber", f"Patwari's share in khasra ({esc(skh)}) differs from the balance worked out above ({km(fig['balance'])}).",
               ("share-differs", "Give owner-wise share calculation for the khasra (Patwari's figure differs from record)."), box=True)
        elif hk is not None and fig["balance"] is not None:
            it(s, "green", "Patwari's share in khasra agrees with the record.", box=True)
        if c.applied is not None and hk is not None and c.applied > hk + 0.25:
            it(s, "red", f"Area proposed ({km(c.applied)}) exceeds the Patwari's own share figure ({esc(skh)}).", ("share-exceeds", "Area proposed exceeds share in khasra."), box=True)
        a1, a2 = parse_area(ak) if not re.fullmatch(r"\s*0\s*", ak or "") else 0.0, parse_area(akh) if not re.fullmatch(r"\s*0\s*", akh or "") else 0.0
        if a1 is not None and fig["giv"] and abs(a1 - fig["giv"]) > 0.5:
            it(s, "amber", f"Patwari says {km(a1)} already alienated in the khewat; transfers found for this owner total {km(fig['giv'])}.",
               ("alien-differs", "Reconcile area already alienated with the mutations."), box=True)
    if joint and is_no(pf(f, "consent")):
        it(s, "amber", "Joint khewat but co-sharer consent is “No” — the report should say why consent is not needed.",
           ("consent", "Explain co-sharer consent for the joint khewat."), box=True)


# ───────────────────────────── 4 (Case 1). Documents checklist + Aadhaar ─────────────────────────────
VERHOEFF_D = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6], [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
              [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1], [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
              [8, 7, 6, 5, 9, 3, 2, 1, 0, 4], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
VERHOEFF_P = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2], [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
              [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1], [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]


def verhoeff_ok(n):
    c = 0
    for i, d in enumerate(reversed(n)):
        c = VERHOEFF_D[c][VERHOEFF_P[i % 8][int(d)]]
    return c == 0 and n[0] not in "01"


def read_aadhaar(id_pages):
    """Local OCR only (never sent to an AI). Returns {name, last4, valid, masked, read}."""
    out = {"read": False}
    if not id_pages:
        return out
    try:
        import numpy as np
        from PIL import Image
        ocr = E._get_ocr()
        lines = []
        for p in id_pages[:4]:
            im = Image.open(io.BytesIO(base64.b64decode(p["data"]))).convert("RGB")
            im.thumbnail((1400, 1400))
            res, _ = ocr(np.array(im))
            lines += [norm(r[1]) for r in sorted(res or [], key=lambda r: (r[0][0][1], r[0][0][0]))]
        txt = " \n ".join(lines)
        out["read"] = bool(lines)
        m = re.search(r"(?<!\d)(\d{4})\s?(\d{4})\s?(\d{4})(?!\d)", txt)
        mm = re.search(r"[xX*]{4}\s?[xX*]{4}\s?(\d{4})", txt)
        if m:
            n = "".join(m.groups())
            out.update(last4=n[-4:], valid=verhoeff_ok(n), masked=False)
        elif mm:
            out.update(last4=mm.group(1), valid=None, masked=True)
        # name: the English line just above the DOB / Year of birth / gender line
        for i, l in enumerate(lines):
            if re.search(r"\bDOB\b|date of birth|year of birth|\bYOB\b|जन्म|\bMALE\b|\bFEMALE\b", l, re.I):
                for j in range(i - 1, max(-1, i - 4), -1):
                    cand = re.sub(r"[^A-Za-z .]", "", lines[j]).strip()
                    if len(cand) >= 4 and not re.search(r"government|india|aadhaar|unique|authority|father|address|to$", cand, re.I):
                        out["name"] = cand
                        break
                break
        E.trim_memory()
    except Exception as e:
        out["error"] = str(e)[:120]
    return out


def docs_section(c, doc_labels, aad):
    s = new_sec("4 · Documents uploaded by the applicant")
    labels = [l for l in doc_labels if not re.match(r"All documents", l)]
    at = next((i for i, l in enumerate(labels) if re.search(r"tatima|patwari|girdh?awar", l, re.I)), len(labels))
    app_docs = labels[:at]
    need = [("Identity proof (Aadhaar)", r"identity|aadhaa?r|id\s*proof"), ("Land document (fard / mutation)", r"land|fard|jamabandi|mutation|intikhab|record"),
            ("Rough sketch", r"sketch"), ("Photo of applicant", r"photo")]
    rows = []
    n = 0
    for lab in app_docs:
        n += 1
        extra = ""
        if re.search(r"identity|aadhaa?r|id\s*proof", lab, re.I):
            extra = _aadhaar_html(c, aad)
        rows.append(f"<tr><td style='padding:4px 6px;border-bottom:1px solid #eceef2;width:28px'>{n}</td><td style='padding:4px 6px;border-bottom:1px solid #eceef2'>"
                    f"<span style='color:#145c36'>✓</span> {esc(lab)}{extra}</td></tr>")
    for name, pat in need:
        if not any(re.search(pat, l, re.I) for l in app_docs):
            n += 1
            rows.append(f"<tr><td style='padding:4px 6px;border-bottom:1px solid #eceef2'>{n}</td><td style='padding:4px 6px;border-bottom:1px solid #eceef2;color:#b42318'>✗ {esc(name)} — missing</td></tr>")
            it(s, "amber", f"{esc(name)} not uploaded.", ("doc-" + name.split()[0].lower(), f"{name} not uploaded by the applicant."))
    s["items"].insert(0, {"lv": "html", "t": "<table style='width:100%;border-collapse:collapse;font-size:13.5px'>" + "".join(rows) + "</table>", "pt": None})
    if aad.get("score") is not None and aad["score"] < 40:
        it(s, "red", "Aadhaar check failed — see the Aadhaar report above.", ("aadhaar", "Identity proof (Aadhaar) does not match the applicant / fails the check."))
    elif aad.get("score") is not None and aad["score"] < 70:
        it(s, "amber", "Aadhaar could only be partly checked.", None)
    lv = levels(s)
    s["score"] = cap_score(100 - 15 * lv.count("amber") - 35 * lv.count("red"), lv)
    return s


def aadhaar_assess(c, aad):
    pts, why = 100, []
    if not aad.get("read"):
        aad["score"] = None
        return aad
    if aad.get("name"):
        sm = _who_matches(c.applicant, aad["name"])
        aad["name_ok"] = sm >= 0.8
        if not aad["name_ok"]:
            pts -= 65
    else:
        pts -= 25
    if aad.get("valid") is False:
        pts -= 65
    elif aad.get("valid") is None:
        pts -= 15
    aad["score"] = int(max(0, min(100, pts)))
    return aad


def _aadhaar_html(c, aad):
    if not aad.get("read"):
        return "<div style='font-size:12.5px;color:#5b6475;margin-top:3px'>Aadhaar card could not be read automatically — check it on the original.</div>"
    lines = []
    if aad.get("name"):
        ok = aad.get("name_ok")
        lines.append(f"<span style='color:{COL['green'] if ok else COL['red']}'>{'✓' if ok else '✗'}</span> Name on card “{esc(aad['name'])}” "
                     f"{'matches' if ok else 'does <b>not</b> match'} the applicant “{esc(c.applicant)}”")
    else:
        lines.append("<span style='color:#8a5300'>▲</span> Name on the card not legible to the reader")
    if aad.get("last4"):
        if aad.get("masked"):
            lines.append(f"<span style='color:#8a5300'>▲</span> Masked Aadhaar (ends {esc(aad['last4'])}) — check digit cannot be tested")
        else:
            lines.append(f"<span style='color:{COL['green'] if aad.get('valid') else COL['red']}'>{'✓' if aad.get('valid') else '✗'}</span> Aadhaar ending {esc(aad['last4'])} "
                         f"{'passes' if aad.get('valid') else '<b>fails</b>'} the check-digit test")
    else:
        lines.append("<span style='color:#8a5300'>▲</span> Aadhaar number not legible")
    lines.append("<span style='color:#5b6475'>ℹ</span> The application form carries no Aadhaar number of the applicant, so the number is checked on the card only")
    return ("<div style='margin-top:4px'>" + scale_html("Aadhaar", aad.get("score")) +
            "<div style='font-size:12.5px;line-height:1.6'>" + "<br>".join(lines) + "</div></div>")


# ───────────────────────────── 4 (Case 2). Tatima ─────────────────────────────
def tatima_section(c, tat):
    s = new_sec("4 · Tatima")
    tt = c.ai.get("tatima") or {}
    if not tat or not tat.get("patwari", True):
        it(s, "red", "No tatima uploaded by the Patwari" + (" — only the applicant's rough sketch is available." if tat else "."),
           ("tatima-missing", "Patwari to upload the tatima (aks shajra) showing the shaded portion."))
    else:
        kind = (tt.get("sketch_kind") or "").lower()
        if kind.startswith("loc"):
            it(s, "red", "The tatima is only a location / route sketch — it does not draw the khasra or mark the shaded portion.",
               ("tatima-location", "Upload a tatima (aks shajra) of the khasra with the shaded portion and dimensions."))
        elif c.overlay or kind.startswith("shaj"):
            it(s, "green", "A proper aks shajra of the khasra" + (" — laid over the map." if c.overlay else "."))
        if tat.get("of", 1) > 1:
            it(s, "info", f"Sketch taken from {esc(tat['label'].split(' — ')[-1])} of {tat['of']} ({esc(tat.get('why', ''))}).")
        src = pf(c.f, "tatimaSource")
        if src:
            it(s, "info", f"Source of tatima: {esc(src)}.")
        if c.free:
            it(s, "amber", "Shaded area and figures not read (free mode) — check them on the sketch beside the map.")
        elif tt.get("found"):
            it(s, "info", f"As read by {c.reader}: {esc(tt.get('as_written') or '—')}; shaded side {esc(tt.get('shaded_side') or '—')}.")
            tot, sh, rem = num(tt.get("total_marla")), num(tt.get("shaded_marla")), num(tt.get("remaining_marla"))
            if sh is not None and c.applied is not None:
                if abs(sh - c.applied) > 0.25:
                    it(s, "red", f"Shaded area {km(sh)} ≠ area applied {km(c.applied)}.", ("tatima-shaded", "Shaded area on tatima must equal area applied."))
                else:
                    it(s, "green", f"Shaded area {km(sh)} matches the area applied.")
            ref = c.total if c.total else (c.jb or {}).get("area_marla")
            if tot is not None and ref and abs(tot - ref) > 0.5:
                it(s, "amber", f"Total on tatima {km(tot)} ≠ Jamabandi {km(ref)}.", ("tatima-total", "Correct total area on tatima."))
            if None not in (tot, sh, rem) and abs(tot - sh - rem) > 0.25:
                it(s, "amber", f"Arithmetic: {km(tot)} − {km(sh)} ≠ {km(rem)}.", ("tatima-sum", "Correct tatima arithmetic."))
            if not tt.get("dimensions_marked"):
                it(s, "amber", "No dimensions marked on the shaded portion.", ("tatima-dims", "Mark dimensions (karam/feet) of the shaded portion on the tatima."))
            else:
                it(s, "green", "Dimensions are marked on the shaded portion.")
    lv = levels(s)
    s["score"] = cap_score(95 - 12 * lv.count("amber") - 30 * lv.count("red"), lv)
    return s


# ───────────────────────────── 5 (Case 2). Patwari's report — contradictions ─────────────────────────────
EXPECTED = [("possession", "In possession of land", "Yes"), ("encroach", "Encroached govt/common land", "No"),
            ("litigation", "Court case / litigation", "No"), ("masterPlan", "Under Master / Development Plan", "No"),
            ("vesting", "Vesting of Ownership (Act 2001)", "No"), ("roshni", "Govt land in last 20 yrs / Roshni", "No"),
            ("acquisition", "Under Land Acquisition Act", "No"), ("mortgage", "Mortgaged or on lease", "No"),
            ("fit", "Fit for alienation", "Yes"), ("barred", "Barred from alienation", "None"),
            ("soil", "Kind of soil", "As per Jamabandi"), ("tatimaSource", "Source of tatima", "Aks latha (massavi / field book)"),
            ("onspot", "On-spot position", "As seen on the ground")]


def sat_image(c):
    """Esri World Imagery around the khasra with its outline drawn. Returns (jpeg_b64, None) or (None, why)."""
    if not c.p:
        return None, "khasra not on the map"
    try:
        import requests
        from PIL import Image, ImageDraw
        g = c.p["geom"]
        mnx, mny, mxx, mxy = g.bounds
        cx, cy = (mnx + mxx) / 2, (mny + mxy) / 2
        half = max((mxx - mnx) * math.cos(math.radians(cy)), mxy - mny) * 0.85 + 0.00025
        bx = (cx - half / math.cos(math.radians(cy)), cy - half, cx + half / math.cos(math.radians(cy)), cy + half)
        url = ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
               f"bbox={bx[0]:.7f},{bx[1]:.7f},{bx[2]:.7f},{bx[3]:.7f}&bboxSR=4326&imageSR=4326&size=480,480&format=jpg&f=image")
        r = requests.get(url, timeout=12)
        if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image"):
            return None, "satellite image not available right now"
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        W, H = im.size
        d = ImageDraw.Draw(im)
        for pg in getattr(g, "geoms", [g]):
            pts = [((x - bx[0]) / (bx[2] - bx[0]) * W, (bx[3] - y) / (bx[3] - bx[1]) * H) for x, y in pg.exterior.coords]
            d.line(pts, fill=(255, 214, 0), width=3)
        b = io.BytesIO()
        im.save(b, "JPEG", quality=78)
        return base64.b64encode(b.getvalue()).decode(), None
    except Exception as e:
        return None, "satellite image not available right now"


def sat_judge(img_b64):
    if not os.environ.get("GEMINI_API_KEY") or not img_b64:
        return None
    try:
        parts = [{"inline_data": {"mime_type": "image/jpeg", "data": img_b64}},
                 {"text": 'Satellite image of a land parcel outlined in yellow (Kashmir). Return ONLY JSON: {"inside": "vacant|built_up|partly_built|orchard|cultivated|unclear", "note": "<one short line>"}'}]
        txt, model, err = E.gemini_call(parts, max_tokens=300, timeout=40)
        m = re.search(r"\{.*\}", txt or "", re.S)
        return json.loads(m.group(0)) if m else None
    except Exception:
        return None


def sat_prefetch(app):
    """Fetched in parallel with the AI reader (Case 2 only): satellite image of the khasra and the AI's reading of it."""
    try:
        f = app.get("fields") or {}
        pr = norm(app.get("patReport"))
        if pr != "Submitted" or not pf(f, "onspot"):
            return None
        c = Ctx()
        c.village = pf(f, "villageD") or norm(app.get("village"))
        k = pf(f, "cKhasra") if not E.is_pending(pf(f, "cKhasra")) else (pf(f, "aKhasra") or norm(app.get("khasra")))
        c.khasra = kn(re.split(r"[,;]", k)[0]) if k else ""
        c.v = E.load_village(c.village) if c.village else None
        c.p = E.parcel_for(c.v, c.khasra) if c.v and c.khasra else None
        img, why = sat_image(c)
        return {"img": img, "why": why, "ai": sat_judge(img)}
    except Exception as e:
        return {"img": None, "why": "satellite image not available right now", "ai": None}


def report_section(c, sat_pre=None):
    s = new_sec("5 · Patwari's report — contradictions")
    f = c.f
    rows, flagged = [], 0
    fam_text = " ".join(f"{e.get('mut_type', '')} {e.get('status', '')} {e.get('qism', '')}" for e in c.fam)
    owners_text = " ".join(c.v["jb"]["khewats"].get(kw, {}).get("owners", "") for kw in {e["khewat"] for e in c.fam}) if c.v and c.v.get("jb") else ""
    qism = " ".join(norm(e.get("qism")) for e in c.fam)
    rem = c.remarks_text
    flags = {}

    def flag(key, lv, why, pt=None):
        flags.setdefault(key, []).append((lv, why))
        if pt:
            c.extra_points.append((lv, pt))

    c.extra_points = []
    # expected answers + record checks
    poss = pf(f, "possession")
    if poss and not is_yes(poss):
        flag("possession", "red", "answer is not “Yes”", ("rep-possession", "Applicant not in possession as per report."))
    elif is_yes(poss) and c.jb:
        cult = c.jb.get("cultivator", "")
        if cult and not re.search(r"khud\s*kasht|\bself\b", cult, re.I) and _who_matches(c.applicant, re.sub(r"^\s*kasht\s*", "", cult, flags=re.I)) < 0.75:
            pred = any(_who_matches(pn, re.sub(r"^\s*kasht\s*|\d.*$", "", cult, flags=re.I)) >= 0.8 for pn in E.parent_names(pf(f, "owners") + " " + pf(f, "ownRecords")))
            flag("possession", "amber", f"Jamabandi cultivator column: “{esc(cult[:90])}”" + (" (the applicant's predecessor)" if pred else ""),
                 ("rep-possession", "Possession: cultivator column shows " + ("the predecessor" if pred else "another person") + " — clarify possession of the applicant."))
        if re.search(r"possession|kashtkar|in\s+cultivation", rem, re.I) and re.search(r"not|another|other|of\s+\w+\s+son", rem, re.I):
            flag("possession", "amber", "a remark on the page questions possession")
    enc = pf(f, "encroach")
    if enc and not is_no(enc):
        flag("encroach", "red", "answer is not “No”", ("rep-encroach", "Encroachment on govt/common land reported."))
    elif GOVT_LAND.search(qism) or GOVT_OWNER.search(owners_text):
        flag("encroach", "red", "the survey no. is recorded as govt / common land (" + esc((GOVT_LAND.search(qism) or GOVT_OWNER.search(owners_text)).group(0)) + ")",
             ("rep-govt", "Land recorded as govt / common land — encroachment / eligibility to be examined."))
    lit = pf(f, "litigation")
    if lit and not is_no(lit):
        flag("litigation", "red", "answer is not “No”", ("rep-litigation", "Litigation on the land reported."))
    elif re.search(r"court|stay|decree|litigat|case\s*no|attach|injunction|status\s*quo", rem + " " + fam_text, re.I):
        flag("litigation", "red", "remarks / record mention a court matter", ("rep-litigation", "Remarks mention a court matter — clarify litigation."))
    mp = pf(f, "masterPlan")
    if mp and not is_no(mp):
        flag("masterPlan", "red", "answer is not “No”", ("rep-masterplan", "Land under Master / Development Plan."))
    elif re.search(r"within", pf(f, "municipal"), re.I) or is_yes(pf(f, "municipal")):
        flag("masterPlan", "amber", "land is within municipal limits — confirm Master Plan position")
    for key, pat, pid in (("vesting", r"vesting|occupan", "rep-vesting"), ("roshni", r"roshni|roshini|state\s*land|khalsa", "rep-roshni")):
        val = pf(f, key)
        if val and not is_no(val):
            flag(key, "red", "answer is not “No”", (pid, "Land given under vesting / Roshni / was govt land."))
        elif re.search(pat, fam_text, re.I) or GOVT_OWNER.search(owners_text):
            flag(key, "red", "record shows State / vesting ownership", (pid, "Record shows State / vesting ownership — examine."))
    acq = pf(f, "acquisition")
    if acq and not is_no(acq):
        flag("acquisition", "red", "answer is not “No”", ("rep-acq", "Land under acquisition."))
    elif re.search(r"acqui|award|hasool", fam_text + " " + rem, re.I):
        flag("acquisition", "red", "record / remarks mention acquisition", ("rep-acq", "Record mentions acquisition — clarify."))
    mort = pf(f, "mortgage")
    if mort and not is_no(mort):
        flag("mortgage", "red", "answer is not “No”", ("rep-mortgage", "Land mortgaged / on lease."))
    elif re.search(r"rehan|rahan|mortgag|ijara|lease|\bbank\b", fam_text + " " + rem, re.I):
        flag("mortgage", "red", "record / remarks show a mortgage or lease", ("rep-mortgage", "Record shows mortgage / lease — clarify."))
    barred = pf(f, "barred")
    if barred and not re.fullmatch(r"\s*(none|nil|no|na|n/a)\.?\s*", barred, re.I):
        flag("barred", "red", "answer is not “None”", ("rep-barred", "Land barred from alienation as per report."))
    elif GOVT_LAND.search(qism):
        flag("barred", "red", f"land type “{esc(qism[:60])}” is a barred category", ("rep-barred", "Land type is a barred category."))
    soil = pf(f, "soil")
    if soil and c.jb and c.jb.get("qism"):
        a, b = name_tokens(soil), name_tokens(" ".join([c.jb["qism"]] + c.jb.get("qism_extra", [])))
        if a and b and not any(tok_match(x, y, 0.7) for x in a for y in b):
            flag("soil", "amber", f"Jamabandi has “{esc(c.jb['qism'])}”", ("rep-soil", "Kind of soil does not match the Jamabandi."))
    src = pf(f, "tatimaSource")
    if src and not re.search(r"aks|latha|massavi|musavi|field\s*book", src, re.I):
        flag("tatimaSource", "amber", "not aks latha / massavi / field book", ("rep-source", "Source of tatima to be stated (aks latha / massavi / field book)."))
    elif re.search(r"aks|latha|massavi", src or "", re.I) and str((c.ai.get("tatima") or {}).get("sketch_kind") or "").lower().startswith("loc"):
        flag("tatimaSource", "red", "the uploaded tatima is only a location sketch", ("rep-source", "Tatima said to be from aks latha but only a location sketch is uploaded."))
    onspot = pf(f, "onspot")
    c.sat, c.sat_why, c.sat_ai = None, None, None
    if onspot:
        vac, blt = bool(re.search(r"vacant|open", onspot, re.I)), bool(re.search(r"built", onspot, re.I))
        if vac and blt and not re.search(r"\(", onspot):
            flag("onspot", "amber", "the entry says both vacant and built up")
        if sat_pre is not None:
            c.sat, c.sat_why, c.sat_ai = sat_pre.get("img"), sat_pre.get("why"), sat_pre.get("ai")
        else:
            c.sat, c.sat_why = sat_image(c)
            c.sat_ai = sat_judge(c.sat)
        ins = ((c.sat_ai or {}).get("inside") or "").lower()
        if ins in ("built_up", "partly_built") and vac and not blt:
            flag("onspot", "red", f"satellite view shows a structure ({esc((c.sat_ai or {}).get('note') or ins)})", ("rep-onspot", "On-spot position (vacant) contradicts the satellite view."))
        elif ins in ("vacant", "orchard", "cultivated") and blt and not vac:
            flag("onspot", "red", f"satellite view shows {esc(ins)} land", ("rep-onspot", "On-spot position (built up) contradicts the satellite view."))
    # fit for alienation — must agree with everything above
    fit = pf(f, "fit")
    bad = [k for k, v_ in flags.items() if any(l == "red" for l, _ in v_) and k not in ("fit", "soil", "tatimaSource")]
    if fit and not is_yes(fit):
        flag("fit", "red", "answer is not “Yes”", ("rep-fit", "Land reported unfit for alienation."))
    elif is_yes(fit) and bad:
        flag("fit", "red", "but " + ", ".join(dict(EXPECTED_MAP)[k] for k in bad) + " is flagged above", ("rep-fit", "“Fit for alienation: Yes” is inconsistent with the other columns."))
    TD = "<td style='padding:4px 6px;border-bottom:1px solid #eceef2;vertical-align:top'>"
    for key, lab, exp in EXPECTED:
        ans = pf(f, key)
        fl = flags.get(key, [])
        if not ans and not fl:
            continue
        lv = "red" if any(l == "red" for l, _ in fl) else ("amber" if fl else "green")
        if fl:
            flagged += 1
        why = "; ".join(w for _, w in fl)
        rows.append(f"<tr style='{'background:#fdecea' if lv == 'red' else 'background:#fff4e0' if lv == 'amber' else ''}'>{TD}<span style='color:{COL[lv]}'>{ICON[lv]}</span> {esc(lab)}</td>"
                    f"{TD}<b>{esc(ans or '—')}</b></td>{TD}{esc(exp)}</td>{TD}{why or '<span style=color:#5b6475>—</span>'}</td></tr>")
    if rows:
        s["items"].append({"lv": "html", "t": "<div style='overflow-x:auto'><table style='width:100%;border-collapse:collapse;font-size:13px'>"
                           "<tr style='background:#f0f2f6'><th style='text-align:left;padding:4px 6px'>Column</th><th style='text-align:left;padding:4px 6px'>Patwari's answer</th>"
                           "<th style='text-align:left;padding:4px 6px'>Expected</th><th style='text-align:left;padding:4px 6px'>Contradiction</th></tr>" + "".join(rows) + "</table></div>", "pt": None})
    if not flagged and rows:
        it(s, "green", "All report columns as expected and consistent with the record on file.")
    for lv, pt in c.extra_points:
        it(s, lv, pt[1], pt)
    s["items"] = [x for x in s["items"] if x["lv"] == "html" or x["lv"] == "green"] + [x for x in s["items"] if x["lv"] in ("red", "amber")]
    for x in s["items"]:
        if x["lv"] in ("red", "amber"):
            x["hidden"] = True                 # shown in the table; kept for the score and the points list
    if pf(f, "lambardar") and re.search(r"pending", pf(f, "lambardar"), re.I):
        it(s, "amber", "Lambardar / Chowkidar statement still “Report Pending”.", ("rep-lambardar", "Record the Lambardar / Chowkidar statement."))
    pend = [d for d, r in (c.app.get("adj") or {}).items() if E.is_pending((r or {}).get("khasra")) or E.is_pending((r or {}).get("owner"))]
    if pend:
        it(s, "amber", f"Adjoining khasra details blank / “Report Pending”: {esc(', '.join(pend))}.", ("rep-adj", "Record adjoining khasras with owners."))
    it(s, "info", "Record checks cover only what the digitised Jamabandi and the remarks on the page show — a clean result means “nothing in the record”, not “verified clear”.")
    lv = levels(s)
    s["score"] = cap_score(100 - 10 * lv.count("amber") - 25 * lv.count("red"), lv)
    return s


EXPECTED_MAP = [(k, lab) for k, lab, _ in EXPECTED]


# ───────────────────────────── Overall ─────────────────────────────
def overall(c, secs, title_s, prev_points):
    if c.case == 1:
        w = [("Title", title_s, 40), ("Survey record", secs["survey"], 20), ("Photo", secs["photo"], 25), ("Documents", secs.get("docs"), 15)]
    else:
        w = [("Title", title_s, 30), ("Report", secs.get("report"), 15), ("Survey record", secs["survey"], 15), ("Photo", secs["photo"], 20), ("Tatima", secs.get("tatima"), 20)]
    have = [(n, s_["score"], wt) for n, s_, wt in w if s_ is not None and s_.get("score") is not None]
    score = round(sum(sc * wt for _, sc, wt in have) / max(1, sum(wt for _, _, wt in have))) if have else None
    if score is not None and title_s.get("score") is not None and title_s["score"] < 40:
        score = min(score, 35)
    elif score is not None and any(sc < 40 for _, sc, _ in have):
        score = min(score, 69)                 # a serious finding anywhere keeps the overall at "doubtful" at best
    # points (current)
    pts = []
    for s_ in [secs["photo"], secs["survey"], title_s, secs.get("docs"), secs.get("tatima"), secs.get("report")]:
        if not s_:
            continue
        for x in s_["items"] + s_["box"]:
            if x.get("pt") and x["lv"] in ("red", "amber"):
                pts.append({"id": x["pt"][0], "text": x["pt"][1], "lv": x["lv"]})
    seen, uniq = set(), []
    for p_ in sorted(pts, key=lambda z: LV_ORDER[z["lv"]]):
        if p_["id"] in seen:
            continue
        seen.add(p_["id"])
        uniq.append(p_)
    # overview
    reds = [p_["text"] for p_ in uniq if p_["lv"] == "red"]
    ambs = [p_["text"] for p_ in uniq if p_["lv"] == "amber"]
    lv, word = band(score)
    if reds:
        comment = "Serious points: " + " ".join(reds[:3])
    elif ambs:
        comment = "Points to clarify: " + " ".join(ambs[:3])
    else:
        comment = "The checks raise no objection on record."
    ov = []
    for n, sc, _ in have:
        ov.append(f"{n} {band(sc)[1].lower()} ({sc})")
    return {"score": score, "points": uniq, "comment": comment, "summary": " · ".join(ov), "prev": prev_points if c.case == 2 else None}


def overall_html(c, o):
    h = [scale_html("Overall satisfaction", o["score"], o["summary"])]
    h.append(f"<div style='margin:6px 0;font-size:13.5px'><b>Comment:</b> {T(o['comment'])}</div>")
    if o.get("prev"):
        cur = {p_["id"] for p_ in o["points"]}
        rows = []
        for p_ in o["prev"]:
            done = p_.get("id") not in cur
            rows.append(f"<div style='margin:2px 0;color:{COL['green'] if done else COL['red']}'>{'✓ resolved' if done else '✗ still open'} — {esc(p_.get('text', ''))}</div>")
        if rows:
            h.append("<div style='margin:8px 0 4px;font-weight:700'>Pre-scrutiny points after the Patwari's report</div>" + "".join(rows))
    if o["points"]:
        note = "\n".join(f"{i}. {p_['text']}" for i, p_ in enumerate(o["points"], 1))
        h.append("<div style='margin:10px 0 4px;font-weight:700'>Points to verify</div>")
        h.append(f'<pre id="rpa-note" style="white-space:pre-wrap;background:#fff;border:1px solid #e1e4ea;border-radius:8px;padding:10px;font:13px/1.5 system-ui,sans-serif;margin:0">{esc(note)}</pre>')
        h.append('<button data-copy="rpa-note" style="font:inherit;border:0;border-radius:8px;padding:7px 12px;margin-top:6px;background:#1a7f5a;color:#fff;cursor:pointer">Copy points</button>')
    return "".join(h)


# ───────────────────────────── Build + render ─────────────────────────────
class Rep:
    """Carries what engine's map / KML / KMZ helpers need."""
    pass


def build(app, ai, ai_err=None, pages=None, id_pages=None, doc_labels=None, prev_points=None, other_fps=None, reader_status=None, skipped=None, sat_pre=None):
    ai = ai or {}
    c = prepare(app, ai)
    pages = pages or []
    rep = Rep()
    rep.head = {"applicant": c.applicant, "village": c.village, "khasra": c.khasra, "service": norm(app.get("service")) or pf(c.f, "svcType"),
                "purpose": norm(app.get("purpose")), "appNo": norm(app.get("appNo")), "applied": c.applied, "village_found": c.v["name"] if c.v else None}
    # photo page (from OCR / AI)
    ph = ai.get("photo") or {}
    lab = ph.get("label") or next((x.get("label") for x in (ai.get("pages") or []) if isinstance(x, dict) and x.get("kind") == "site_photo"), None)
    photo_page = next((p for p in pages if p["label"] == lab), None) if lab else None
    if not photo_page and ph.get("found"):
        photo_page = next((p for p in pages if p.get("orig")), None)
    secs = {}
    secs["photo"] = photo_section(c, photo_page, other_fps)
    secs["survey"] = survey_section(c)
    titles, opts, default = title_section(c)
    # tatima + overlay (for both cases; Case 1 shows the rough sketch beside the map)
    try:
        rep.tatima = E.pick_tatima_page(pages, ai)
    except Exception:
        rep.tatima = None
    rep.p, rep.nbs, rep.v, rep.near, rep.ai = c.map_p, c.map_nbs, c.v, c.near, ai
    rep.point, rep.geo = c.point, c.geo
    rep.overlay, rep.overlay_note = None, ""
    try:
        if c.case == 2 and c.p:
            rep.p = c.p
            rep.overlay = E.sketch_overlay(rep)
    except Exception:
        rep.overlay = None
    c.overlay = rep.overlay
    if c.case == 1:
        aad = aadhaar_assess(c, read_aadhaar(id_pages or []))
        secs["docs"] = docs_section(c, doc_labels or [p["label"] for p in pages], aad)
    else:
        secs["tatima"] = tatima_section(c, rep.tatima)
        secs["report"] = report_section(c, sat_pre)
    ovs = [overall(c, secs, t, prev_points) for t in titles]
    out = render(c, rep, secs, titles, opts, default, ovs, reader_status, ai_err, skipped)
    d = default + 1                                   # variant index (0 = not found)
    gist = {"case": c.case, "score": ovs[d]["score"], "band": band(ovs[d]["score"])[0],
            "text": " · ".join(p_["text"] for p_ in ovs[d]["points"][:3]) or "No objection on record."}
    return {"html": out, "case": c.case, "gist": gist, "points": [{"id": p_["id"], "text": p_["text"]} for p_ in ovs[d]["points"]],
            "photo_hash": c.photo_hash, "owner_default": default, "rep": rep}


def _map_block(c, rep, with_tatima):
    m = E.svg_map(rep) if rep.p else ""
    if not m:
        return ""
    cap = (("Dashed: nearest available survey no. " + esc(c.near["shown"]) + " (" + esc(c.near["asked"]) + " is not on the map)") if c.near
           else ("Yellow: survey no. " + esc(c.khasra))) + " · grey: adjoining khasras · red dot: geotag"
    if rep.overlay:
        cap += f" · ink: Patwari's sketch at 70% ({esc(rep.overlay['how'])}; approximate)"
    elif with_tatima and rep.overlay_note:
        cap += " · " + esc(rep.overlay_note)
    left = f'<div style="flex:1;min-width:240px">{m}<div style="font-size:12px;color:#5b6475">{cap}</div></div>'
    right = ""
    tat = rep.tatima
    if tat:
        right = (f'<div style="flex:1;min-width:240px"><div style="background:#fff;border:1px solid #e1e4ea;border-radius:8px;padding:4px;text-align:center">'
                 f'<img alt="sketch" src="data:image/jpeg;base64,{tat["data"]}" style="max-width:100%;max-height:420px;object-fit:contain"></div>'
                 f'<div style="font-size:12px;color:#5b6475">{esc(E.tatima_title(rep))} — {esc(tat["label"])}</div></div>')
    return '<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start;margin:6px 0">' + left + right + '</div>' + E.coords_block(rep)


def _headline(s):
    """One line for the closed section: the most serious finding."""
    for lv in ("red", "amber"):
        x = next((x for x in s["items"] + s["box"] if x["lv"] == lv), None)
        if x:
            return lv, re.sub(r"<[^>]+>", "", x["t"])
    g = next((x for x in s["items"] + s["box"] if x["lv"] == "green"), None)
    return ("green", re.sub(r"<[^>]+>", "", g["t"])) if g else ("info", "")


def _summary(title, score, s=None):
    lv, line = _headline(s) if s else ("info", "")
    return (f'<summary><span class="stt">{esc(title)}</span>{chip("Score", score) if score is not None else ""}'
            + (f'<div class="sl {lv}">{esc(_html.unescape(line))[:180]}</div>' if line else "") + "</summary>")


def _sec_html(s, extra_top="", scale_title=None):
    h = ['<details class="sec">' + _summary(s["title"], s["score"], s)]
    if scale_title:
        h.append(scale_html(scale_title, s["score"]))
    h.append(extra_top)
    h.append(items_html([x for x in s["items"] if not x.get("hidden")]))
    h.append(box_html([x for x in s["box"] if not x.get("hidden")]))
    h.append("</details>")
    return "".join(h)


def render(c, rep, secs, titles, opts, default, ovs, rs, ai_err, skipped):
    hd = rep.head
    h = [STYLE + '<div class="rpa r19" style="font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1d2330;padding:14px;max-width:900px;margin:0 auto">']
    h.append(f'<h2 style="margin:0 0 4px;font-size:18px">{esc(hd["service"] or "Application")} — Survey no. {esc(hd["khasra"] or "?")}, {esc(hd["village"] or "?")}</h2>')
    h.append(f'<div style="color:#5b6475;font-size:13px">Applicant: {esc(hd["applicant"] or "—")} · App. no. {esc(hd["appNo"] or "—")}'
             f'{" · Area applied: " + km(hd["applied"]) if hd["applied"] is not None else ""}</div>')
    lab = ("Pre-scrutiny — Patwari report not yet submitted", "#5b3fa8") if c.case == 1 else ("After the Patwari's report", "#12355b")
    h.append(f'<div style="display:inline-block;margin:8px 0 4px;padding:4px 12px;border-radius:14px;background:{lab[1]};color:#fff;font-weight:700;font-size:13px">{lab[0]}</div>')
    if not c.v:
        h.append(f'<div style="margin:6px 0;padding:8px 10px;border-radius:8px;background:#fdecea;color:#b42318">Village records not found for “{esc(c.village)}” — record checks could not run.</div>')
    # chips (owner-dependent ones in variants)
    nvar = len(titles)
    d = default + 1

    def vwrap(i, inner, block=True):
        disp = "" if i == d else "display:none"
        tag = "div" if block else "span"
        return f'<{tag} data-owner="{i - 1}" style="{disp}">{inner}</{tag}>'

    fixed = chip("Photo", secs["photo"]["score"]) + chip("Survey record", secs["survey"]["score"])
    if c.case == 1:
        fixed += chip("Documents", secs["docs"]["score"])
    else:
        fixed += chip("Tatima", secs["tatima"]["score"]) + chip("Report", secs["report"]["score"])
    chips = "".join(vwrap(i, chip("Overall", ovs[i]["score"]) + chip("Title", titles[i]["score"]), block=False) for i in range(nvar))
    h.append(f'<div style="margin:4px 0 8px">{chips}{fixed}</div>')
    # 1 photo (+ map in Case 1)
    ph_extra = ""
    pics = []
    if c.photo_thumb:
        pics.append(f'<div style="flex:1;min-width:200px;text-align:center"><img alt="photo" src="data:image/jpeg;base64,{c.photo_thumb}" style="max-width:100%;max-height:300px;border-radius:6px">'
                    f'<div style="font-size:12px;color:#5b6475">Geotagged photograph</div></div>')
    if getattr(c, "ela", None):
        pics.append(f'<div style="flex:1;min-width:200px;text-align:center"><img alt="compression check" src="data:image/png;base64,{c.ela}" style="max-width:100%;max-height:300px;border-radius:6px">'
                    f'<div style="font-size:12px;color:#5b6475">Compression check (brighter = saved differently)</div></div>')
    if pics:
        ph_extra = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:6px 0">' + "".join(pics) + "</div>"
    if c.case == 1:
        ph_extra += _map_block(c, rep, False)
    h.append(_sec_html(secs["photo"], ph_extra, "Photo satisfaction"))
    # 2 survey
    h.append(_sec_html(secs["survey"]))
    # 3 title (owner drop-down)
    sel = ""
    if opts:
        o_html = '<option value="-1">— Applicant not among these owners —</option>' + "".join(
            f'<option value="{i}"{" selected" if i == default else ""}>{esc(t)}</option>' for i, t in enumerate(opts))
        sel = (f'<div style="margin:4px 0 8px;font-size:13px">Owner matched to the applicant: '
               f'<select data-rp-owner data-app="{esc(hd["appNo"] or "")}" style="font:inherit;max-width:100%;padding:4px;border:1px solid #c9ced8;border-radius:6px">{o_html}</select>'
               f'<div style="color:#5b6475;font-size:12px">If the spelling match picked the wrong person, choose the right owner — the figures, the scale and the overall update at once. '
               f'The list shows the {len(opts)} names closest to the applicant out of {getattr(c, "n_owners", len(opts))} owner entries.</div></div>')
    th, heads = [], []
    for i, s_ in enumerate(titles):
        inner = scale_html("Eligibility", s_["score"]) + items_html([x for x in s_["items"] if not x.get("hidden")]) + box_html(s_["box"])
        th.append(vwrap(i, inner))
        lv_, line_ = _headline(s_)
        heads.append(vwrap(i, chip("Score", s_["score"]) + (f'<div class="sl {lv_}">{esc(_html.unescape(line_))[:180]}</div>' if line_ else ""), block=False))
    h.append(f'<details class="sec"><summary><span class="stt">3 · Title and share</span>{"".join(heads)}</summary>{sel}{"".join(th)}</details>')
    # 4 / 5
    if c.case == 1:
        h.append(_sec_html(secs["docs"]))
    else:
        h.append(_sec_html(secs["tatima"], _map_block(c, rep, True), "Tatima satisfaction"))
        sat = ""
        if c.sat:
            j = c.sat_ai or {}
            sat = (f'<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-start;margin:6px 0"><img alt="satellite" src="data:image/jpeg;base64,{c.sat}" style="max-width:300px;width:100%;border-radius:6px">'
                   f'<div style="flex:1;min-width:200px;font-size:13px">Satellite view of survey no. {esc(c.khasra)} (yellow outline; Esri World Imagery — date of imagery may be older).'
                   + (f'<br><b>{c.reader if os.environ.get("GEMINI_API_KEY") else "AI"} reading:</b> {esc(j.get("inside", "—"))} — {esc(j.get("note", ""))}' if j else
                      "<br>Compare with the on-spot position in the report.") + '</div></div>')
        elif getattr(c, "sat_why", None):
            sat = f'<div style="font-size:12px;color:#5b6475">Satellite check: {esc(c.sat_why)}.</div>'
        h.append(_sec_html(secs["report"], sat, "Report consistency"))
    # overall
    oh = "".join(vwrap(i, overall_html(c, ovs[i])) for i in range(nvar))
    h.append(f'<details class="sec ov" open><summary><span class="stt">Overall</span></summary>{oh}</details>')
    # case for Claude (default owner)
    h.append(f'<pre id="rpa-case" style="display:none">{esc(case_text(c, secs, titles[d], ovs[d]))}</pre>')
    h.append('<div style="margin-top:12px;padding:10px 12px;background:#fff;border:1px solid #e1e4ea;border-radius:10px">'
             '<b>Final review by Claude</b><div style="font-size:13px;color:#5b6475;margin:2px 0 8px">Copies all findings (no Aadhaar or phone numbers). '
             'Paste into a Claude chat with the documents attached and ask for the final call.</div>'
             '<button data-copy="rpa-case" style="font:inherit;border:0;border-radius:8px;padding:8px 14px;background:#12355b;color:#fff;cursor:pointer">Copy full case for Claude</button></div>')
    # footer: village records, reader, notes
    foot = []
    if c.v:
        foot.append(f"Records: villages/{esc(c.v['name'])} — {len(c.v['jb']['khasras']) if c.v.get('jb') else 0} khasras in Jamabandi, "
                    f"{len(c.v['map']['parcels']) if c.v.get('map') else 0} parcels on map.")
        for e in c.v.get("errors", []):
            foot.append(esc(e))
    if rs:
        foot.append(esc(("✗ " + rs["used"] + " could not read: " + str(rs["error"])) if rs.get("error") else ("Documents read by " + rs["used"])) + f" · {rs['pages']} page(s), {rs['secs']} s.")
    if ai_err:
        foot.append(esc(ai_err))
    if skipped:
        foot.append("Not opened: " + esc("; ".join(skipped)))
    foot.append(f"Values read from handwritten / scanned documents by AI must be confirmed against the originals. Shares are indicative. Nothing is submitted to the portal. · Fard Checker v{E._app_version()}")
    h.append('<p style="color:#5b6475;font-size:12px;margin-top:14px">' + "<br>".join(foot) + "</p></div>")
    return "".join(h)


def case_text(c, secs, title_s, ov):
    L = ["Please review this Revenue Plus application as a Naib Tehsildar in J&K would, and make the final call.",
         ("Stage: pre-scrutiny (Patwari report not yet submitted)." if c.case == 1 else "Stage: after the Patwari's report."), "",
         f"## Application: {c.app.get('service') or ''} — survey no. {c.khasra}, village {c.village}; applicant {c.applicant}; "
         f"app. no. {c.app.get('appNo')}; area applied {km(c.applied) if c.applied is not None else '—'}"]
    sym = {"red": "[SERIOUS]", "amber": "[CHECK]", "green": "[OK]", "info": "-"}

    def dump(s_):
        if not s_:
            return
        L.append("")
        L.append(f"## {s_['title']} — score {s_['score'] if s_.get('score') is not None else '—'}")
        for x in s_["items"] + s_["box"]:
            if x["lv"] == "html":
                for r_ in re.findall(r"<tr[^>]*>(.*?)</tr>", x["t"], re.S):
                    cells = [norm(re.sub(r"<[^>]+>", " ", q)) for q in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r_, re.S)]
                    if any(cells):
                        L.append("  | " + " | ".join(cells))
                for li in re.findall(r"<li[^>]*>(.*?)</li>", x["t"], re.S):
                    L.append("  - " + norm(_html.unescape(re.sub(r"<[^>]+>", "", li))))
                continue
            L.append(f"{sym.get(x['lv'], '-')} " + _html.unescape(re.sub(r"<[^>]+>", "", x["t"])).replace("\xa0", " "))
    for s_ in (secs["photo"], secs["survey"], title_s, secs.get("docs"), secs.get("tatima"), secs.get("report")):
        dump(s_)
    L.append("")
    L.append(f"## Overall {ov['score']} — {ov['comment']}")
    for i, p_ in enumerate(ov["points"], 1):
        L.append(f"{i}. {p_['text']}")
    out = "\n".join(L)
    out = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[number removed]", out)
    out = re.sub(r"\b[6-9]\d{9}\b", "[number removed]", out)
    return out
