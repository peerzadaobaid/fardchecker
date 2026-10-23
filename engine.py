"""Revenue Plus application analyser — village records, document reading and checks.

Village data lives in the repo:  villages/<Village name>/<anything>.xlsx  (Jamabandi export)
                                  villages/<Village name>/<anything>.shp/.shx/.dbf/.prj  (khasra parcels)
Nothing about an application is stored; everything is computed per request.
"""
import base64, difflib, hashlib, html, io, json, math, os, re, threading, time

import pandas as pd
import shapefile  # pyshp
from shapely.geometry import Point, shape
from shapely.ops import transform as shp_transform
from shapely.validation import make_valid

BASE = os.path.dirname(os.path.abspath(__file__))
VILLAGES_DIR = os.environ.get("VILLAGES_DIR", os.path.join(BASE, "villages"))
MARLA_M2 = 25.29285264          # 1 marla = 272.25 sq ft
SQFT_PER_MARLA = 272.25
esc = html.escape


# ───────────────────────────── helpers ─────────────────────────────
def norm(s):
    return re.sub(r"\s+", " ", str("" if s is None else s)).strip()


def num(v):
    try:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        return float(str(v).strip())
    except Exception:
        return None


def km(marla):
    """25.3 -> '1 K 5 M 82 sqft'"""
    if marla is None:
        return "—"
    neg = marla < 0
    marla = abs(marla)
    k = int(marla // 20 + 1e-9)
    m = marla - 20 * k
    mi = int(m + 1e-9)
    sq = round((m - mi) * SQFT_PER_MARLA)
    if sq >= 272:
        mi, sq = mi + 1, 0
    out = (f"{k} K " if k else "") + f"{mi} M" + (f" {sq} sqft" if sq else "")
    return ("−" if neg else "") + out


def parse_area(text):
    """'11 Marlas', '1K-5M', '0 kanal 11 marla 68 sqft', '05M 68sqfeet' -> marla (float) or None"""
    t = str(text or "").lower()
    if not t or re.search(r"report\s*pending", t):
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*k(?:anal|nl)?\s*[-–/ ]\s*(\d+(?:\.\d+)?)\s*m", t)
    if m:
        return 20 * float(m.group(1)) + float(m.group(2))
    k = re.search(r"(\d+(?:\.\d+)?)\s*k(?:anal|nl)?\b", t)
    mm = re.search(r"(\d+(?:\.\d+)?)\s*m(?:arla|arlas|rl)?\b", t)
    s = re.search(r"(\d+(?:\.\d+)?)\s*s(?:arsai|rs)\b", t)
    f = re.search(r"(\d+(?:\.\d+)?)\s*(?:sq\.?\s*f(?:ee)?t|sqft|sqfeet|sft|square\s*feet)", t)
    if not (k or mm or s or f):
        return None
    return (20 * float(k.group(1)) if k else 0) + (float(mm.group(1)) if mm else 0) + \
           (float(s.group(1)) / 9 if s else 0) + (float(f.group(1)) / SQFT_PER_MARLA if f else 0)


def first_num(s):
    m = re.match(r"\s*(\d+)", str(s or ""))
    return m.group(1) if m else ""


def name_tokens(s):
    stop = {"mst", "smt", "mrs", "mr", "ms", "sh", "shri", "late", "haji", "dr", "s", "o", "d", "w",
            "son", "daughter", "wife", "of", "and", "r", "resident", "sakindeh", "sakin", "kaum",
            "pisar", "dukhter", "zoja", "byuh", "wd", "so", "do", "wo"}
    return [t for t in re.split(r"[^a-z]+", str(s or "").lower()) if t and t not in stop and len(t) > 1]


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def tok_match(a, b, cut=0.78):
    return similar(a, b) >= cut


# ───────────────────────────── Jamabandi ─────────────────────────────
def parse_jamabandi(path):
    raw = pd.read_excel(path, header=None, dtype=object)
    head = raw.head(6).fillna("").astype(str)
    hdr_row = None
    for i in range(len(head)):
        if any(re.search(r"khasra", c, re.I) for c in head.iloc[i]):
            hdr_row = i
            break
    if hdr_row is None:
        raise ValueError("Could not find a header row with 'Khasra' in the Jamabandi")
    top = list(head.iloc[hdr_row])
    sub = list(head.iloc[hdr_row + 1]) if hdr_row + 1 < len(head) else [""] * len(top)

    def find(pat, row=top):
        for j, c in enumerate(row):
            if re.search(pat, c, re.I):
                return j
        return None

    col = {
        "khasra": find(r"khasra"), "owner": find(r"owner"), "cultivator": find(r"cultivator"),
        "khata": find(r"khata"), "khewat": find(r"khewat"), "patti": find(r"patti|numberdar"),
        "area": find(r"area"), "mut": find(r"mutation"), "status": find(r"status"),
        "irrig": find(r"irrigation"),
    }
    a = col["area"]
    col["qism"] = find(r"qism", sub) if find(r"qism", sub) is not None else a
    col["marla"] = find(r"^\s*marla", sub)
    col["kanal"] = find(r"^\s*kanal", sub)
    col["mut_type"] = find(r"^\s*type", sub) if find(r"^\s*type", sub) is not None else col["mut"]
    col["mut_no"] = find(r"number", sub) if find(r"number", sub) is not None else (col["mut"] + 1 if col["mut"] is not None else None)
    col["khasra_old"] = find(r"^\s*old", sub)
    data = raw.iloc[hdr_row + 2:]

    def g(r, k):
        j = col.get(k)
        if j is None:
            return None
        v = r[j]
        return None if (v is None or (isinstance(v, float) and math.isnan(v))) else v

    khasras, khewats = {}, {}
    cur_kw = cur_kt = None
    kw_owner = {}
    kt_cult, kt_mut = {}, {}
    cur_entry = None
    for _, r in data.iterrows():
        qism = norm(g(r, "qism"))
        if qism.lower().startswith("total area for khasra"):
            if cur_entry is not None:
                k, m = num(g(r, "kanal")) or 0, num(g(r, "marla")) or 0
                cur_entry["area_marla"] = 20 * k + m
            continue
        if qism.lower().startswith("total area for"):
            if qism.lower().endswith("khewat") and cur_kw:
                k, m = num(g(r, "kanal")) or 0, num(g(r, "marla")) or 0
                khewats.setdefault(cur_kw, {})["area_marla"] = 20 * k + m
            continue
        kw = norm(g(r, "khewat"))
        kt = norm(g(r, "khata"))
        if kw:
            cur_kw = kw
        if kt:
            cur_kt = kt
        owner = norm(g(r, "owner"))
        if owner and cur_kw:
            kw_owner[cur_kw] = (kw_owner.get(cur_kw, "") + " " + owner).strip()
        cult = norm(g(r, "cultivator"))
        if cult and cur_kt:
            kt_cult[cur_kt] = cult
        mt, mn = norm(g(r, "mut_type")), norm(g(r, "mut_no"))
        if (mt or mn) and cur_kt:
            kt_mut[cur_kt] = (mt, mn)
        ks = norm(g(r, "khasra"))
        if not ks:
            if cur_entry is not None and qism:          # continuation line (second land type of same khasra)
                cur_entry["qism_extra"].append(qism)
            continue
        if ks.startswith("/"):                         # '/239' style (sub-division of 239)
            ks = ks.strip("/")
        k, m = num(g(r, "kanal")) or 0, num(g(r, "marla")) or 0
        cur_entry = {
            "khasra": ks, "khasra_old": norm(g(r, "khasra_old")),
            "khewat": cur_kw, "khata": cur_kt,
            "khewat_no": first_num(cur_kw), "khata_no": first_num(cur_kt),
            "qism": qism, "qism_extra": [], "area_marla": 20 * k + m,
            "cultivator": cult or (kt_cult.get(cur_kt, "")),
            "mut_type": mt or (kt_mut.get(cur_kt, ("", ""))[0]),
            "mut_no": mn or (kt_mut.get(cur_kt, ("", ""))[1]),
            "status": norm(g(r, "status")),
        }
        khasras.setdefault(ks, []).append(cur_entry)
    for kwid, txt in kw_owner.items():
        khewats.setdefault(kwid, {})["owners"] = txt
    return {"khasras": khasras, "khewats": khewats}


# ───────────────────────────── Shapefile ─────────────────────────────
def local_metres(lon0, lat0):
    """Plain-Python projection to metres around a village centre (error < 0.1% within a few km)."""
    phi = math.radians(lat0)
    k_lat = 111132.92 - 559.82 * math.cos(2 * phi) + 1.175 * math.cos(4 * phi)
    k_lon = 111412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi)

    def fwd(x, y, z=None):
        return ((x - lon0) * k_lon, (y - lat0) * k_lat)
    return fwd


def _where(e):
    import traceback
    tb = traceback.extract_tb(e.__traceback__)
    last = tb[-1] if tb else None
    return f"{type(e).__name__}: {e}" + (f" [{os.path.basename(last.filename)}:{last.lineno} {last.name}]" if last else "")


def _reader(path):
    for enc in ("utf-8", "latin-1"):
        try:
            rd = shapefile.Reader(path, encoding=enc)
            fields = [f[0] for f in rd.fields[1:]]
            recs = list(rd.iterShapeRecords())
            return fields, recs
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not read shapefile text encoding")


def village_field(fields):
    return next((f for f in fields if re.search(r"^vill|village", f, re.I)), None)


def shapefile_villages(path):
    """Cheap: village names present in a shapefile's attribute table (dbf only)."""
    try:
        rd = shapefile.Reader(path, encoding="latin-1")
        fields = [f[0] for f in rd.fields[1:]]
        vcol = village_field(fields)
        if not vcol:
            return []
        return sorted({norm(r[0]) for r in rd.iterRecords(fields=[vcol]) if norm(r[0])})
    except Exception:
        return []


def parse_shapefile(path, only_village=None):
    fields, recs = _reader(path)
    kcol = next((f for f in fields if re.search(r"khasra", f, re.I)), None)
    tcol = next((f for f in fields if re.search(r"kind|soil|qism|land.?use", f, re.I)), None)
    acol = next((f for f in fields if re.search(r"ror", f, re.I)), None)
    vcol = village_field(fields)
    parcels = []
    for sr in recs:
        if sr.shape.shapeType == 0 or not sr.shape.points:
            continue
        rec = sr.record.as_dict()
        if only_village and vcol and _key(rec.get(vcol)) != _key(only_village):
            continue
        try:
            geo = shape(sr.shape.__geo_interface__)
            if geo.has_z:
                geo = shp_transform(lambda x, y, z=None: (x, y), geo)
            if not geo.is_valid:
                geo = make_valid(geo)
        except Exception:
            continue
        kv = rec.get(kcol) if kcol else None
        kn = ""
        if kv not in (None, ""):
            try:
                kn = str(int(float(kv))) if float(kv) == int(float(kv)) else str(kv)
            except Exception:
                kn = norm(kv)
        parcels.append({"khasra": kn, "geom": geo, "type": norm(rec.get(tcol)) if tcol else "",
                        "ror": rec.get(acol) if acol else None})
    if not parcels:
        raise ValueError("No usable polygons in the shapefile" + (f" for village {only_village}" if only_village else ""))
    c = parcels[0]["geom"].centroid
    crs = (round(c.x, 6), round(c.y, 6))
    fwd = local_metres(*crs)
    for p in parcels:
        p["m"] = shp_transform(fwd, p["geom"])
    return {"parcels": parcels, "crs": crs, "khasra_col": kcol}


# ───────────────────────────── Village registry ─────────────────────────────
# Layout (all optional except the village folder):
#   villages/<Village>/ *.xlsx            Jamabandi export
#   villages/<Village>/ *.shp .shx .dbf .prj   parcels of this village
#   villages/<Village>/aliases.txt        other spellings used on the portal, one per line
#   villages/_maps/ *.shp ...             a tehsil/district-wide shapefile with a Village column,
#                                         used for any village folder that has no .shp of its own
# Only a few villages are kept in memory (MAX_VILLAGES_IN_MEMORY); others come from a disk cache.
import pickle
from collections import OrderedDict

_cache, _lock = OrderedDict(), threading.RLock()
MAX_MEM = int(os.environ.get("MAX_VILLAGES_IN_MEMORY", "4"))
CACHE_DIR = os.environ.get("CACHE_DIR", "/tmp/rp_village_cache")
_index = {"sig": None, "map": {}, "dirs": {}}


def _key(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def village_dirs():
    if not os.path.isdir(VILLAGES_DIR):
        return {}
    return {d: os.path.join(VILLAGES_DIR, d) for d in sorted(os.listdir(VILLAGES_DIR))
            if os.path.isdir(os.path.join(VILLAGES_DIR, d)) and not d.startswith(("_", "."))}


def shared_maps():
    p = os.path.join(VILLAGES_DIR, "_maps")
    return [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(".shp")] if os.path.isdir(p) else []


def _files_sig(paths):
    out = []
    for d in paths:
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            fp = os.path.join(d, f)
            if os.path.isfile(fp):
                out.append((fp, os.path.getmtime(fp), os.path.getsize(fp)))
    return tuple(out)


def name_index():
    """{normalised name -> folder} from folder names, aliases.txt and shapefile village names."""
    dirs = village_dirs()
    sig = _files_sig(list(dirs.values()))
    with _lock:
        if _index["sig"] == sig:
            return _index
        m, clash = {}, {}
        explicit = {}

        def put(name, folder, strong):
            k = _key(name)
            if not k:
                return
            if strong:
                if k in explicit and explicit[k] != folder:
                    clash.setdefault(k, {explicit[k]}).add(folder)
                explicit[k] = folder
                m[k] = folder
            elif k not in explicit:            # shapefile names never override folder names / aliases
                if k in m and m[k] != folder:
                    clash.setdefault(k, {m[k]}).add(folder)
                else:
                    m[k] = folder

        for d, path in dirs.items():
            put(d, d, True)
            put(re.sub(r"[_\-\s]*\d+$", "", d), d, True)          # 'Wahidpora_2815' -> 'Wahidpora'
            al = os.path.join(path, "aliases.txt")
            if os.path.isfile(al):
                for line in open(al, encoding="utf-8", errors="ignore"):
                    put(line.strip(), d, True)
        for d, path in dirs.items():
            for f in os.listdir(path):
                if f.lower().endswith(".shp"):
                    for vn in shapefile_villages(os.path.join(path, f)):
                        put(vn, d, False)
        _index.update(sig=sig, map=m, dirs=dirs, clash={k: sorted(v) for k, v in clash.items()})
        return _index


def match_village(name):
    """Return (folder, how) or (None, message). Never guesses between two close names."""
    idx = name_index()
    if not idx["dirs"]:
        return None, "No village folders in the repo yet."
    k = _key(name)
    if not k:
        return None, "Village name missing on the application."
    if k in idx["map"]:
        return idx["map"][k], "exact"
    if k in idx.get("clash", {}):
        return None, f"“{name}” matches more than one folder ({', '.join(idx['clash'][k])}) — fix aliases.txt."
    scored = sorted(((similar(k, kk), f) for kk, f in idx["map"].items()), reverse=True)
    best = scored[0] if scored else (0, None)
    second = next((s for s in scored if s[1] != best[1]), (0, None))
    if best[0] >= 0.88 and best[0] - second[0] >= 0.08:
        return best[1], f"close spelling ({best[0]:.0%})"
    near = ", ".join(dict.fromkeys(f for _, f in scored[:3]))
    return None, (f"No village folder matches “{name}”. Closest: {near}. Add the portal spelling to that folder's aliases.txt."
                  if near else f"No village folder matches “{name}”.")


def _build(folder, path):
    v = {"name": folder, "errors": [], "jb": None, "map": None, "map_source": ""}
    files = sorted(os.listdir(path))
    xl = [f for f in files if f.lower().endswith((".xlsx", ".xls")) and not f.startswith("~$")]
    shp = [f for f in files if f.lower().endswith(".shp")]
    if len(xl) > 1:
        v["errors"].append(f"{len(xl)} Excel files in folder — using {xl[0]}; keep only the Jamabandi.")
    if xl:
        try:
            v["jb"] = parse_jamabandi(os.path.join(path, xl[0]))
        except Exception as e:
            v["errors"].append(f"Jamabandi ({xl[0]}): {_where(e)}")
    else:
        v["errors"].append("No Jamabandi .xlsx in folder")
    try:
        if shp:
            v["map"] = parse_shapefile(os.path.join(path, shp[0]))
            v["map_source"] = shp[0]
            inside = shapefile_villages(os.path.join(path, shp[0]))
            mine = {_key(folder), _key(re.sub(r"[_\-\s]*\d+$", "", folder))}
            if os.path.isfile(os.path.join(path, "aliases.txt")):
                mine |= {_key(l) for l in open(os.path.join(path, "aliases.txt"), encoding="utf-8", errors="ignore") if l.strip()}
            if inside and not ({_key(x) for x in inside} & mine):
                v["errors"].append(f"Shapefile {shp[0]} says village “{', '.join(inside[:3])}”, not {folder} — wrong file? "
                                   f"(If it is only a spelling difference, add that spelling to aliases.txt.)")
            for ext in (".shx", ".dbf"):
                if not os.path.exists(os.path.join(path, shp[0][:-4] + ext)):
                    v["errors"].append(f"{shp[0][:-4]}{ext} missing")
        else:
            names = [folder] + [l.strip() for l in open(os.path.join(path, "aliases.txt"), encoding="utf-8", errors="ignore")
                                if l.strip()] if os.path.isfile(os.path.join(path, "aliases.txt")) else [folder]
            for sp in shared_maps():
                have = {_key(x): x for x in shapefile_villages(sp)}
                hit = next((have[_key(n)] for n in names if _key(n) in have), None)
                if hit:
                    v["map"] = parse_shapefile(sp, only_village=hit)
                    v["map_source"] = f"_maps/{os.path.basename(sp)} (village “{hit}”)"
                    break
            if not v["map"]:
                v["errors"].append("No shapefile for this village (none in folder, not found in _maps)")
    except Exception as e:
        v["errors"].append(f"Shapefile: {_where(e)}")
    return v


def _attach(v):
    if v.get("map"):
        v["map"]["fwd"] = local_metres(*v["map"]["crs"])
    return v


def load_village(name, exact_folder=False):
    folder, how = (name, "folder") if exact_folder else match_village(name)
    if not folder or folder not in village_dirs():
        return None
    path = village_dirs()[folder]
    sig = _files_sig([path] + ([os.path.join(VILLAGES_DIR, "_maps")] if not any(
        f.lower().endswith(".shp") for f in os.listdir(path)) else []))
    with _lock:
        c = _cache.get(folder)
        if c and c["sig"] == sig:
            _cache.move_to_end(folder)
            c["how"] = how
            return c
        h = hashlib.md5(repr(sig).encode()).hexdigest()
        cp = os.path.join(CACHE_DIR, f"{_key(folder)}_{h}.pkl")
        v = None
        if os.path.exists(cp):
            try:
                with open(cp, "rb") as fh:
                    v = pickle.load(fh)
            except Exception:
                v = None
        if v is None:
            v = _build(folder, path)
            try:
                os.makedirs(CACHE_DIR, exist_ok=True)
                for old in os.listdir(CACHE_DIR):
                    if old.startswith(_key(folder) + "_"):
                        os.remove(os.path.join(CACHE_DIR, old))
                with open(cp, "wb") as fh:
                    pickle.dump(v, fh, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception:
                pass
        v = _attach(v)
        v["sig"], v["how"] = sig, how
        _cache[folder] = v
        _cache.move_to_end(folder)
        while len(_cache) > MAX_MEM:
            _cache.popitem(last=False)
        return v


def village_status(check=None):
    """Light listing of all folders; full parse only for the one asked to check."""
    idx = name_index()
    out = []
    for d, path in idx["dirs"].items():
        files = os.listdir(path)
        row = {"village": d,
               "jamabandi": next((f for f in files if f.lower().endswith((".xlsx", ".xls"))), ""),
               "shapefile": next((f for f in files if f.lower().endswith(".shp")), "") or ("(_maps)" if shared_maps() else ""),
               "aliases": [k for k, f in idx["map"].items() if f == d],
               "checked": False}
        if check and _key(check) == _key(d):
            v = load_village(d, exact_folder=True)
            row.update(checked=True, khasras_jamabandi=len(v["jb"]["khasras"]) if v["jb"] else 0,
                       parcels_map=len(v["map"]["parcels"]) if v["map"] else 0, errors=v["errors"],
                       map_source=v.get("map_source", ""),
                       on_map_not_in_jb=sorted({p["khasra"] for p in v["map"]["parcels"] if p["khasra"]} - set(v["jb"]["khasras"]),
                                               key=lambda x: (len(x), x))[:30] if v["jb"] and v["map"] else [])
        out.append(row)
    return {"villages": out, "clashes": idx.get("clash", {}), "shared_maps": [os.path.basename(p) for p in shared_maps()]}


# ───────────────────────────── Map lookups ─────────────────────────────
DIRS = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]


def parcel_for(v, khasra):
    if not v or not v["map"]:
        return None
    base = first_num(khasra) or str(khasra)
    ps = [p for p in v["map"]["parcels"] if p["khasra"] == str(khasra)] or \
         [p for p in v["map"]["parcels"] if p["khasra"] == base]
    if not ps:
        return None
    if len(ps) == 1:
        return ps[0]
    from shapely.ops import unary_union
    return {"khasra": ps[0]["khasra"], "geom": unary_union([p["geom"] for p in ps]),
            "m": unary_union([p["m"] for p in ps]), "type": ps[0]["type"], "ror": ps[0]["ror"]}


def neighbours(v, p):
    t = p["m"]
    c = t.centroid
    out = []
    for q in v["map"]["parcels"]:
        if q is p or q["khasra"] == p["khasra"]:
            continue
        if not q["m"].intersects(t.buffer(1.5)):
            continue
        shared = q["m"].intersection(t.buffer(1.5)).length
        if shared < 1:
            continue
        pt = q["m"].intersection(t.buffer(3)).centroid
        ang = math.degrees(math.atan2(pt.x - c.x, pt.y - c.y)) % 360
        out.append({"khasra": q["khasra"] or "(no number)", "type": q["type"], "dir": DIRS[int(((ang + 22.5) % 360) // 45)],
                    "angle": ang, "shared_m": shared, "q": q})
    return sorted(out, key=lambda r: r["angle"])


def locate_point(v, lat, lng, p):
    pm = Point(v["map"]["fwd"](lng, lat))
    inside = next((q for q in v["map"]["parcels"] if q["m"].contains(pm)), None)
    dist = p["m"].distance(pm) if p else None
    return pm, inside, dist


def jb_info(v, khasra):
    if not v or not v["jb"]:
        return None
    ks = v["jb"]["khasras"]
    k = str(khasra).strip()
    return ks.get(k) or ks.get(first_num(k))


# ───────────────────────────── Owner / share parsing ─────────────────────────────
def owner_entries(text):
    """Split the khewat owner column into individual entries."""
    return [norm(x) for x in re.split(r",", text or "") if norm(x)]


def find_applicant_share(owner_text, applicant, parent_hint=""):
    """Return list of matching owner entries with their fraction / area, best first."""
    a_toks = name_tokens(applicant)
    p_toks = name_tokens(parent_hint)
    if not a_toks:
        return []
    res = []
    for e in owner_entries(owner_text):
        et = name_tokens(e)
        if not et:
            continue
        if not tok_match(et[0], a_toks[0]):
            continue
        score = similar(et[0], a_toks[0])
        par = re.search(r"\b(?:s/o|d/o|w/o|pisar|dukhter|zoja|byuh)\b\s*(.+?)(?:\bsakin\w*|\bkaum\b|\d|$)", e, re.I)
        par_name = norm(par.group(1)) if par else ""
        if p_toks and par_name:
            pt = name_tokens(par_name)
            hits = sum(1 for x in p_toks if any(tok_match(x, y) for y in pt))
            score += 0.5 * hits / max(1, len(p_toks))
        fr = re.search(r"(\d+)\s*/\s*(\d+)", e)
        ar = re.search(r"(\d+)\s*kanal\s*(-?\d+)\s*marla", e, re.I)
        res.append({"entry": e, "score": score, "parent": par_name,
                    "fraction": (int(fr.group(1)), int(fr.group(2))) if fr else None,
                    "area_marla": (20 * int(ar.group(1)) + int(ar.group(2))) if ar else None})
    return sorted(res, key=lambda r: -r["score"])


# ───────────────────────────── Documents → images ─────────────────────────────
def doc_to_images(label, mime, b64, max_side=1568):
    from PIL import Image
    raw = base64.b64decode(b64)
    imgs = []
    if "pdf" in (mime or "") or raw[:4] == b"%PDF":
        import fitz  # pymupdf
        doc = fitz.open(stream=raw, filetype="pdf")
        for i, page in enumerate(doc):
            if i >= 30:
                break
            zoom = min(2.0, max_side / max(page.rect.width, page.rect.height))
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            imgs.append((f"{label} — page {i + 1}", Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")))
    else:
        try:
            im = Image.open(io.BytesIO(raw))
            frames = getattr(im, "n_frames", 1)
            for i in range(min(frames, 10)):
                im.seek(i)
                imgs.append((f"{label}" + (f" — page {i + 1}" if frames > 1 else ""), im.convert("RGB")))
        except Exception:
            return []
    out, seen = [], set()
    for lab, im in imgs:
        im.thumbnail((max_side, max_side))
        h = hashlib.md5(im.convert("L").resize((24, 24)).tobytes()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82)
        out.append({"label": lab, "hash": h, "data": base64.b64encode(buf.getvalue()).decode()})
    return out


READ_PROMPT = """You are assisting a Naib Tehsildar in Jammu & Kashmir who is scrutinising a Revenue Plus application ({service}) for khasra {khasra}, village {village}. Applicant: {applicant}. Area applied: {area}.

The images above are the documents attached to the application (applicant uploads and Patwari uploads). They may include: a fard / intikhab-e-jamabandi (handwritten Urdu, 12-13 columns), an intikhab khasra girdawari, a tatima / aks shajra sketch with a shaded portion, a geotagged site photograph (GPS Map Camera overlay), mutation copies, and ID cards.

Read them carefully and return ONLY a JSON object, no other text, in exactly this shape (use null when not present or not legible):
{{
 "pages": [{{"label": "<label shown above the image>", "kind": "fard|girdawari|tatima|site_photo|mutation|id_card|other", "note": "<one line>"}}],
 "photo": {{"found": bool, "lat": number|null, "lng": number|null, "datetime": "<as printed>", "place_label": "<as printed>",
            "land_description": "<what the land in the photo looks like: open/vacant, cultivated, orchard, built-up, under construction, structures visible…>",
            "built_up": "yes|no|partly|unclear", "person_present": bool}},
 "fard": {{"found": bool, "khewat": "", "khata": "", "khasra": "", "area_kanal": number|null, "area_marla": number|null, "land_type": "",
           "owner_entry": "<English transliteration of the owner column>", "cultivator_entry": "<English transliteration>",
           "remarks": ["<English translation of each numbered remark / note in Kaifiyat or below the table>"],
           "patwari_date": "", "versions_differ": "<if two different fards are attached, say how they differ, else empty>"}},
 "mutations": [{{"number": "", "type": "inheritance|gift|sale|other", "date": "", "from": [{{"name": "", "area_marla": number|null, "share": ""}}],
                 "to": [{{"name": "", "area_marla": number|null, "share": ""}}], "summary": "<one line in English>"}}],
 "tatima": {{"found": bool, "khasra": "", "total_marla": number|null, "shaded_marla": number|null, "remaining_marla": number|null,
             "as_written": "<the area figures exactly as written, e.g. 1K-5M / 0-14 / 0-11>", "shaded_side": "north|south|east|west|centre|unclear",
             "dimensions_marked": bool, "neighbours_marked": {{"north": "", "east": "", "south": "", "west": ""}}, "note": ""}},
 "uncertain": ["<anything you could not read with confidence>"]
}}
Rules: areas are kanal/marla/sqft (1 kanal = 20 marla, 1 marla = 272.25 sqft); convert to marla numbers in *_marla fields. Read Urdu numerals carefully. Do NOT output Aadhaar, phone or any ID numbers. Be honest in "uncertain" rather than guessing."""


_ocr = None


def free_read(pages):
    """Free mode (no API key): OCR the printed GPS overlay of a geotagged photo. Handwriting is not read."""
    global _ocr
    out = {"mode": "free", "photo": {"found": False}}
    try:
        import numpy as np
        from PIL import Image
        if _ocr is None:
            from rapidocr_onnxruntime import RapidOCR
            _ocr = RapidOCR()
        for p in pages:
            im = Image.open(io.BytesIO(base64.b64decode(p["data"]))).convert("RGB")
            im.thumbnail((1200, 1200))
            res, _ = _ocr(np.array(im))
            txt = " ".join(r[1] for r in (res or []))
            m = re.search(r"Lat(?:itude)?\s*[:.]?\s*(\d{1,2}\.\d{3,})\s*°?\s*[NS]?\s*,?\s*Lon(?:g(?:itude)?)?\s*[:.]?\s*(\d{2,3}\.\d{3,})", txt, re.I)
            if not m or not (6 <= float(m.group(1)) <= 38 and 68 <= float(m.group(2)) <= 98):
                continue
            dt = re.search(r"(\d{1,2}/\d{1,2}/\d{4})\s*(\d{1,2}:\d{2}\s*[AP]M)?", txt, re.I)
            out["photo"] = {"found": True, "lat": float(m.group(1)), "lng": float(m.group(2)),
                            "datetime": " ".join(x for x in dt.groups() if x) if dt else "", "label": p["label"]}
            break
    except Exception as e:
        out["error"] = f"OCR failed: {e}"
    return out


def read_documents(pages, ctx):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None, "ANTHROPIC_API_KEY is not set on Render, so documents were not read."
    if not pages:
        return None, "No readable documents were received."
    import requests
    content = []
    for p in pages[:int(os.environ.get("MAX_PAGES", "16"))]:
        content.append({"type": "text", "text": f"[{p['label']}]"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": p["data"]}})
    content.append({"type": "text", "text": READ_PROMPT.format(**ctx)})
    body = {"model": os.environ.get("CLAUDE_MODEL", "claude-opus-5-5"), "max_tokens": 4000,
            "messages": [{"role": "user", "content": content}]}
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", json=body, timeout=170,
                          headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        if r.status_code != 200:
            return None, f"Claude API error {r.status_code}: {r.text[:300]}"
        txt = "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)), None
    except Exception as e:
        return None, f"Document reading failed: {e}"


# ───────────────────────────── Analysis ─────────────────────────────
class Report:
    def __init__(self):
        self.sections, self.actions = [], []

    def sec(self, title):
        s = {"title": title, "items": [], "html": ""}
        self.sections.append(s)
        return s


def add(s, level, text, action=None, rep=None):
    s["items"].append((level, text))
    if action and rep is not None:
        rep.actions.append(action)


def pf(f, k):
    return norm((f or {}).get(k, ""))


def is_pending(v):
    return not norm(v) or re.fullmatch(r"(report\s*)?pending\.?|0|na|n/a|-+|nil|none", norm(v), re.I) is not None


def analyse(app, ai=None, ai_error=None):
    f = app.get("fields") or {}
    village = pf(f, "villageD") or norm(app.get("village"))
    khasra = pf(f, "cKhasra") if not is_pending(pf(f, "cKhasra")) else (pf(f, "aKhasra") or norm(app.get("khasra")))
    khasra = norm(re.split(r"[,;]", khasra)[0]) if khasra else ""
    applicant = pf(f, "applicant") or norm(app.get("name"))
    owners_portal = pf(f, "owners") or pf(f, "ownRecords")
    parent_hint = ""
    m = re.search(r"(?:son|daughter|wife|s/o|d/o|w/o)\s+of\s+(.+?)(?:\bwife\b|\bw/o\b|$)", owners_portal, re.I) or \
        re.search(r"(?:s/o|d/o)\s+(.+?)(?:\bw/o\b|$)", owners_portal, re.I)
    if m:
        parent_hint = m.group(1)
    applied = parse_area(pf(f, "areaProposed")) or parse_area(app.get("area"))
    cert_area = None
    if any(pf(f, k) for k in ("cKanal", "cMarla", "cSqft")):
        cert_area = 20 * (num(pf(f, "cKanal")) or 0) + (num(pf(f, "cMarla")) or 0) + (num(pf(f, "cSqft")) or 0) / SQFT_PER_MARLA
    if applied is None:
        applied = cert_area

    v = load_village(village) if village else None
    rep = Report()
    ai = ai or {}
    p = parcel_for(v, khasra) if v else None
    jbs = jb_info(v, khasra) if v else None
    jb = jbs[0] if jbs else None
    nbs = neighbours(v, p) if p else []

    # ── header facts
    rep.head = {"applicant": applicant, "village": village, "khasra": khasra, "service": norm(app.get("service")) or pf(f, "svcType"),
                "purpose": norm(app.get("purpose")), "appNo": norm(app.get("appNo")), "applied": applied,
                "village_found": v["name"] if v else None}

    # ── 0. village data
    s0 = rep.sec("Village records used")
    if not v:
        _, why = match_village(village)
        add(s0, "red", why + f" (Repo folder: villages/<Village>/ with the Jamabandi .xlsx and shapefile.)")
    else:
        for e in v["errors"]:
            add(s0, "amber", e)
        add(s0, "info", f"Portal village “{village}” → folder villages/{v['name']} ({v.get('how', '')}): "
                        f"{len(v['jb']['khasras']) if v['jb'] else 0} khasras in Jamabandi, "
                        f"{len(v['map']['parcels']) if v['map'] else 0} parcels on map" + (f" from {v['map_source']}" if v.get('map_source') else "") + ".")
        if v["jb"] and not jb:
            add(s0, "red", f"Khasra {khasra} not found in the Jamabandi on file.", f"Check khasra number {khasra} — not in the village Jamabandi.", rep)
        if v["map"] and not p:
            add(s0, "amber", f"Khasra {khasra} not found on the village map (it may be an unnumbered parcel or a new sub-division).")

    # ── 1. Geotag
    s1 = rep.sec("Geotagged photograph")
    ph = ai.get("photo") or {}
    lat = num(pf(f, "lat")) or num(ph.get("lat"))
    lng = num(pf(f, "lng")) or num(ph.get("lng"))
    free = ai.get("mode") == "free"
    src = "Patwari report" if num(pf(f, "lat")) else (("photo overlay (" + ("read by free OCR" if free else "read by AI") + ")") if num(ph.get("lat")) else "")
    rep.point = None
    if lat is None or lng is None:
        add(s1, "amber", "No spot coordinates: latitude/longitude blank in the Patwari report and none read from a photo.",
            "Record latitude/longitude of the spot (geotagged photograph).", rep)
    else:
        add(s1, "info", f"Coordinates {lat:.6f}, {lng:.6f} from {src}" + (f"; photo taken {esc(ph.get('datetime'))}" if ph.get("datetime") else "") + ".")
        if not num(pf(f, "lat")):
            add(s1, "amber", "Latitude/longitude fields are blank in the Patwari report although the photo carries them.",
                "Fill latitude/longitude in the report.", rep)
        if v and v["map"]:
            pm, inside, dist = locate_point(v, lat, lng, p)
            rep.point = pm
            if p and p["m"].contains(pm):
                cd = p["m"].centroid.distance(pm)
                add(s1, "green", f"The point falls INSIDE khasra {khasra} (about {cd:.0f} m from its centre).")
            elif p and dist is not None:
                lvl = "amber" if dist <= 15 else "red"
                add(s1, lvl, f"The point is OUTSIDE khasra {khasra}, {dist:.0f} m away" +
                    (f"; it falls in khasra {inside['khasra'] or '(unnumbered parcel)'} ({inside['type']})." if inside else "; it is not inside any parcel of this village."),
                    f"Geotag does not fall on khasra {khasra} — get a fresh geotagged photo on the spot.", rep)
            elif inside:
                add(s1, "info", f"The point falls in khasra {inside['khasra'] or '(unnumbered)'}.")
            else:
                add(s1, "red", "The point is not inside this village's map.", "Geotag is outside the village — verify.", rep)
    if ph.get("found") and free:
        add(s1, "info", f"Land shown in the photo was not assessed (free mode) — compare it yourself with on-spot position “{pf(f, 'onspot') or '—'}”.")
    elif ph.get("found"):
        add(s1, "info", f"Photo shows: {(ph.get('land_description') or '—').rstrip('.')}." + (" A person is standing on the plot." if ph.get("person_present") else ""))
        onspot = pf(f, "onspot")
        bu = (ph.get("built_up") or "").lower()
        if onspot and re.search(r"built", onspot, re.I) and bu == "no":
            add(s1, "amber", f"Report says on-spot position “{onspot}” but the photo shows no structure on the plot.",
                f"Explain/correct on-spot position “{onspot}” — photo shows open land.", rep)
        elif onspot and re.search(r"vacant|open|agri|cultiv", onspot, re.I) and bu == "yes":
            add(s1, "amber", f"Report says “{onspot}” but the photo shows built-up land.", "Reconcile on-spot position with photo.", rep)
        if ph.get("person_present"):
            add(s1, "info", "Identity of the person in the photo is to be confirmed by Patwari/Girdawar (not checked automatically).")
    elif ai:
        add(s1, "amber", "No geotagged site photograph found among the documents.", "Upload a geotagged photograph of the spot.", rep)

    # ── 2. Record & mutations
    s2 = rep.sec("Record and mutation details")
    if jb:
        cult = jb["cultivator"] or "—"
        add(s2, "info", f"Jamabandi: Khewat {jb['khewat'].replace(chr(10), ' ')}, Khata {jb['khata'].replace(chr(10), ' ')}, "
                        f"area {km(jb['area_marla'])}, {jb['qism']}{(' + ' + ', '.join(jb['qism_extra'])) if jb['qism_extra'] else ''}; "
                        f"cultivator: {cult}; last mutation {jb['mut_no'] or '—'} ({jb['mut_type'] or '—'}).")
        if len(jbs) > 1:
            add(s2, "info", f"Khasra {khasra} appears in {len(jbs)} khata entries in the Jamabandi.")
        ck, ckt = first_num(pf(f, "cKhewat")), first_num(pf(f, "cKhata"))
        if ck and ck != jb["khewat_no"]:
            add(s2, "red", f"Khewat on certificate ({ck}) ≠ Jamabandi ({jb['khewat_no']}).", f"Correct khewat number ({ck} vs {jb['khewat_no']}).", rep)
        if ckt and ckt != jb["khata_no"]:
            add(s2, "red", f"Khata on certificate ({ckt}) ≠ Jamabandi ({jb['khata_no']}).", f"Correct khata number ({ckt} vs {jb['khata_no']}).", rep)
        soil = pf(f, "soil")
        if soil and jb["qism"]:
            a, b = name_tokens(soil), name_tokens(jb["qism"])
            if a and b and not any(tok_match(x, y, 0.7) for x in a for y in b):
                add(s2, "amber", f"Kind of soil in report “{soil}” vs Jamabandi “{jb['qism']}”.", "Reconcile kind of soil with Jamabandi.", rep)
        if p and p.get("ror") not in (None, ""):
            r = num(p["ror"])
            if r is not None:
                rm = int(r) * 20 + round((r % 1) * 100)
                if abs(rm - jb["area_marla"]) > 1:
                    add(s2, "info", f"Map's ROR area ({p['ror']}) differs from Jamabandi ({km(jb['area_marla'])}).")
        if p:
            add(s2, "info", f"Measured on map: {p['m'].area:.0f} m² ≈ {km(p['m'].area / MARLA_M2)}"
                + (" — consistent with the record." if jb and abs(p['m'].area / MARLA_M2 - jb['area_marla']) <= max(2, 0.1 * jb['area_marla']) else
                   (f" — differs from the record ({km(jb['area_marla'])})." if jb else "")))
    mut = app.get("mut") or {}
    gist = [r for r in (mut.get("gist") or []) if any(re.search(r"\d", str(x)) for x in r.values())]
    final = [r for r in (mut.get("final") or []) if any(re.search(r"\d", str(x)) for x in r.values())]
    ai_muts = ai.get("mutations") or []
    known = set()
    if jb and jb["mut_no"]:
        known.add(first_num(jb["mut_no"]))
    for r in final:
        mn = next((first_num(v_) for k_, v_ in r.items() if re.search(r"mutation\s*no", k_, re.I)), "")
        dt = next((v_ for k_, v_ in r.items() if re.search(r"date", k_, re.I)), "")
        ty = next((v_ for k_, v_ in r.items() if re.search(r"type", k_, re.I)), "")
        fp = next((v_ for k_, v_ in r.items() if re.search(r"first", k_, re.I)), "")
        add(s2, "info", f"Final mutation (portal): No. {mn or '—'}, {ty or '—'}, attested {dt or '—'}; first party: {fp[:160]}.")
        if mn and jb and jb["mut_no"] and mn != first_num(jb["mut_no"]):
            add(s2, "info", f"Mutation {mn} is not yet reflected in the Jamabandi copy on file (which shows mutation {jb['mut_no']}).")
        if mn:
            known.add(mn)
    for m_ in ai_muts:
        add(s2, "info", f"From documents: mutation {m_.get('number') or '—'} ({m_.get('type') or '—'}{', ' + m_['date'] if m_.get('date') else ''}): {m_.get('summary') or ''}")
        if first_num(m_.get("number")):
            known.add(first_num(m_.get("number")))
    if not final:
        add(s2, "amber", "No final mutation in the applicant's name is shown on the portal.", "Show the final mutation in which the applicant's name appears.", rep)
    if not gist and len(known) >= 1:
        add(s2, "amber", f"“Gist of all successive mutations” is empty, but mutation(s) {', '.join(sorted(known, key=lambda x: int(x) if x.isdigit() else 0))} affect this land.",
            f"Fill the gist of successive mutations ({', '.join(sorted(known))}).", rep)
    fd = ai.get("fard") or {}
    if fd.get("found"):
        for i, rmk in enumerate(fd.get("remarks") or [], 1):
            add(s2, "info", f"Fard remark {i} (AI translation): {rmk}")
        if fd.get("versions_differ"):
            add(s2, "info", f"Two fard versions attached: {fd['versions_differ']}")
        if jb and fd.get("area_marla") is not None:
            fa = 20 * (num(fd.get("area_kanal")) or 0) + (num(fd.get("area_marla")) or 0)
            if abs(fa - jb["area_marla"]) > 0.5:
                add(s2, "amber", f"Area on fard ({km(fa)}) ≠ Jamabandi ({km(jb['area_marla'])}).", "Reconcile fard area with Jamabandi.", rep)

    # ── 3. Share
    s3 = rep.sec("Share of the applicant")
    holding = None
    if jb and v and v["jb"]:
        kw_owners = v["jb"]["khewats"].get(jb["khewat"], {}).get("owners", "")
        n_entries = len(owner_entries(kw_owners))
        joint = n_entries > 1
        add(s3, "info", f"Khewat {jb['khewat_no']} has {n_entries} owner entr{'y' if n_entries == 1 else 'ies'}" + (" — joint khewat." if joint else "."))
        hits = find_applicant_share(kw_owners, applicant, parent_hint)
        if not hits:
            add(s3, "red", f"Applicant “{applicant}” not found among the owners of khewat {jb['khewat_no']} in the Jamabandi on file.",
                "Show how the applicant became owner (mutation) — not in Jamabandi owners.", rep)
        else:
            h = hits[0]
            add(s3, "info", f"Jamabandi owner entry: “{h['entry'][:200]}”.")
            if h["fraction"]:
                a_, b_ = h["fraction"]
                cult_toks = name_tokens(jb["cultivator"])
                par_toks = name_tokens(h["parent"])
                pred = cult_toks and par_toks and tok_match(par_toks[0], cult_toks[0] if cult_toks[0] not in ("kasht",) else (cult_toks[1] if len(cult_toks) > 1 else ""))
                pred = pred or (par_toks and any(tok_match(par_toks[0], c) for c in cult_toks))
                if pred and jb["area_marla"]:
                    holding = jb["area_marla"] * a_ / b_
                    add(s3, "info", f"Khasra {khasra} is in possession of {jb['cultivator']} (the applicant's predecessor), so the applicant's inherited share in this khasra ≈ {a_}/{b_} × {km(jb['area_marla'])} = {km(holding)} (indicative).")
                else:
                    add(s3, "info", f"The applicant's share is {a_}/{b_} of the predecessor's share in the khewat; it cannot be converted to an area for this khasra from the Jamabandi alone.")
            elif h["area_marla"] is not None:
                holding = h["area_marla"]
                add(s3, "info", f"Share recorded as {km(holding)} in the khewat.")
        # later mutations in favour/against applicant (AI-read)
        a_toks = name_tokens(applicant)
        rec_, giv_ = 0.0, 0.0
        detail, counted = [], set()
        # portal "final mutation" rows where the applicant is the second party (recipient)
        for r in final:
            mn = next((first_num(v_) for k_, v_ in r.items() if re.search(r"mutation\s*no", k_, re.I)), "")
            ty = next((v_ for k_, v_ in r.items() if re.search(r"type", k_, re.I)), "")
            sp = next((v_ for k_, v_ in r.items() if re.search(r"second", k_, re.I)), "")
            sp_t = name_tokens(sp)
            if re.search(r"inherit|warasat", ty, re.I) or not (a_toks and sp_t and tok_match(sp_t[0], a_toks[0])):
                continue
            kk = next((num(v_) for k_, v_ in r.items() if re.fullmatch(r"\s*kanal\s*", k_, re.I)), None) or 0
            mm = next((num(v_) for k_, v_ in r.items() if re.fullmatch(r"\s*marla\s*", k_, re.I)), None) or 0
            sq = next((num(v_) for k_, v_ in r.items() if re.fullmatch(r"\s*sq\.?\s*ft\s*", k_, re.I)), None) or 0
            got = 20 * kk + mm + sq / SQFT_PER_MARLA
            if got:
                rec_ += got
                counted.add(mn)
                detail.append(f"mutation {mn} ({ty}): received {km(got)} as per portal")
        for m_ in ai_muts:
            if first_num(m_.get("number")) in counted:
                if m_.get("from"):
                    detail.append(f"breakup read from documents for mutation {m_.get('number')}: " + ", ".join(
                        f"{t.get('name')} {km(num(t.get('area_marla'))) if num(t.get('area_marla')) is not None else '?'}" for t in m_["from"]))
                continue
            to_me = any(a_toks and name_tokens(t.get("name")) and tok_match(name_tokens(t.get("name"))[0], a_toks[0]) for t in m_.get("to") or [])
            from_me = any(a_toks and name_tokens(t.get("name")) and tok_match(name_tokens(t.get("name"))[0], a_toks[0]) for t in m_.get("from") or [])
            if (m_.get("type") or "").startswith("inherit"):
                continue
            if to_me:
                parts = [(t.get("name"), num(t.get("area_marla"))) for t in m_.get("from") or []]
                got = sum(x for _, x in parts if x)
                rec_ += got
                detail.append(f"mutation {m_.get('number')}: received {km(got)} (" + ", ".join(f"{n} {km(x) if x is not None else '?'}" for n, x in parts) + ")")
            if from_me:
                gv = sum(num(t.get("area_marla")) or 0 for t in m_.get("to") or [])
                giv_ += gv
                detail.append(f"mutation {m_.get('number')}: gave {km(gv)}")
        if detail:
            add(s3, "info", "Later transfers: " + "; ".join(detail) + ".")
        if holding is not None or rec_:
            total = (holding or 0) + rec_ - giv_
            add(s3, "info", f"Indicative holding in khasra {khasra}: inherited {km(holding or 0)} + received {km(rec_)} − given {km(giv_)} = <b>{km(total)}</b>.")
            if applied is not None:
                if applied > total + 0.25:
                    add(s3, "red", f"Area applied ({km(applied)}) exceeds the indicative holding ({km(total)}).",
                        f"Area applied {km(applied)} exceeds holding {km(total)} — give donor-wise share calculation.", rep)
                else:
                    add(s3, "green", f"Area applied ({km(applied)}) is within the indicative holding ({km(total)}).")
        sk, skh = pf(f, "shareKhewat"), pf(f, "shareKhasra")
        if joint and sk and parse_area(sk) is not None:
            add(s3, "amber", f"Report states share in khewat as “{sk}”. In a joint khewat the applicant's khewat share is a fraction of the whole khewat, not the area of one khasra.",
                "Correct “share in khewat” (joint khewat — state fraction / full share).", rep)
        if holding is not None and skh and parse_area(skh) is not None and abs(parse_area(skh) - ((holding or 0) + rec_ - giv_)) > 0.5:
            add(s3, "amber", f"Report's share in khasra (“{skh}”) differs from the indicative holding ({km((holding or 0) + rec_ - giv_)}).",
                "Give donor-wise share calculation for the khasra.", rep)
        consent = pf(f, "consent")
        if joint and re.match(r"\s*no", consent, re.I):
            add(s3, "amber", "Joint holding but co-sharer consent is “No”; report should state why consent is not needed (exclusive possession / within own share).",
                "Explain co-sharer consent position for the joint khewat.", rep)
    elif applied is not None:
        add(s3, "info", f"Area applied: {km(applied)}. Village Jamabandi not available for the share check.")

    # ── 4. Tatima / shaded portion
    s4 = rep.sec("Shaded portion (tatima) and Patwari's report")
    tt = ai.get("tatima") or {}
    if free:
        if applied is not None and cert_area is not None and abs(applied - cert_area) > 0.25:
            add(s4, "amber", f"Area proposed ({km(applied)}) ≠ area on certificate ({km(cert_area)}).", "Reconcile area proposed with certificate area.", rep)
        add(s4, "info", "Tatima and handwritten fard were not read (free mode) — check the shaded area, its side and dimensions on the tatima yourself"
                        + (f"; the plot is about {p['m'].bounds[2] - p['m'].bounds[0]:.0f} m E–W × {p['m'].bounds[3] - p['m'].bounds[1]:.0f} m N–S" if p else "")
                        + (f", so {km(applied)} is about {applied * MARLA_M2:.0f} m²" if applied else "") + ".")
    elif tt.get("found"):
        add(s4, "info", f"Tatima reads: {tt.get('as_written') or '—'}; shaded side: {tt.get('shaded_side') or '—'}.")
        tot, sh, remn = num(tt.get("total_marla")), num(tt.get("shaded_marla")), num(tt.get("remaining_marla"))
        if jb and tot is not None and abs(tot - jb["area_marla"]) > 0.5:
            add(s4, "amber", f"Total on tatima ({km(tot)}) ≠ Jamabandi area ({km(jb['area_marla'])}).", "Correct total area on tatima.", rep)
        if sh is not None and applied is not None and abs(sh - applied) > 0.25:
            add(s4, "red", f"Shaded area on tatima ({km(sh)}) ≠ area applied ({km(applied)}).", "Shaded area on tatima must equal area applied.", rep)
        elif sh is not None and applied is not None:
            add(s4, "green", f"Shaded area ({km(sh)}) matches the area applied.")
        if tot is not None and sh is not None and remn is not None and abs(tot - sh - remn) > 0.25:
            add(s4, "amber", f"Tatima arithmetic does not add up: {km(tot)} − {km(sh)} ≠ {km(remn)}.", "Correct tatima arithmetic.", rep)
        if not tt.get("dimensions_marked"):
            dims = ""
            if p and applied:
                minx, miny, maxx, maxy = p["m"].bounds
                ew, ns = maxx - minx, maxy - miny
                side = (tt.get("shaded_side") or "").lower()
                need = applied * MARLA_M2
                if side in ("north", "south") and ew:
                    dims = f" (plot is ~{ew:.0f} m E–W × {ns:.0f} m N–S; a {side} strip of {km(applied)} would be ~{ew:.0f} m × {need / ew:.0f} m)"
                elif side in ("east", "west") and ns:
                    dims = f" (plot is ~{ew:.0f} m E–W × {ns:.0f} m N–S; a {side} strip of {km(applied)} would be ~{need / ns:.0f} m × {ns:.0f} m)"
            add(s4, "amber", "No dimensions (karam/feet) are marked on the shaded portion" + dims + ".", "Mark dimensions of the shaded portion on the tatima.", rep)
        side = (tt.get("shaded_side") or "").lower()
        if nbs and side in ("north", "south", "east", "west"):
            touch = [n_ for n_ in nbs if n_["dir"].lower().startswith(side) or n_["dir"].lower().endswith(side)]
            if touch:
                add(s4, "info", f"The shaded {side} portion borders khasra " + ", ".join(
                    f"{t['khasra']} ({(jb_info(v, t['khasra']) or [{'qism': t['type']}])[0]['qism'] or t['type']}"
                    + (f", {(jb_info(v, t['khasra']) or [{}])[0].get('cultivator', '')[:50]}" if jb_info(v, t['khasra']) else "") + ")" for t in touch) + ".")
    elif ai:
        add(s4, "amber", "No tatima found among the documents.", "Upload the tatima with the shaded portion.", rep)
    adj = app.get("adj") or {}
    if nbs:
        rows = []
        for n_ in nbs:
            info = jb_info(v, n_["khasra"])
            j0 = info[0] if info else None
            rows.append((n_["dir"], n_["khasra"], (j0["qism"] if j0 else "") or n_["type"],
                         (j0["cultivator"][:60] if j0 else ""), f"{n_['shared_m']:.0f} m"))
        rep.neigh_rows = rows
    else:
        rep.neigh_rows = []
    pend = [d for d, r in adj.items() if is_pending((r or {}).get("khasra")) or is_pending((r or {}).get("owner"))]
    if adj and pend:
        sugg = "; ".join(f"{n_['dir']} {n_['khasra']}" for n_ in nbs) if nbs else ""
        add(s4, "amber", f"Adjoining khasra details are blank / “Report Pending” for: {', '.join(pend)}." + (f" From the map: {sugg}." if sugg else ""),
            "Record adjoining khasras" + (f" ({sugg})" if sugg else "") + " with owners.", rep)
    elif adj and nbs:
        for d, r in adj.items():
            k_ = first_num((r or {}).get("khasra"))
            mapk = [n_["khasra"] for n_ in nbs if n_["dir"].lower().startswith(d.lower()[:4]) or d.lower() in n_["dir"].lower()]
            if k_ and mapk and k_ not in mapk:
                add(s4, "amber", f"{d}: report says khasra {k_}, map shows {', '.join(mapk)}.", f"Check {d} adjoining khasra ({k_} vs map {', '.join(mapk)}).", rep)
    lmb = pf(f, "lambardar")
    if lmb and re.search(r"pending", lmb, re.I):
        add(s4, "amber", "Lambardar/Chowkidar statement still “Report Pending”.", "Record Lambardar/Chowkidar statement.", rep)
    mun = pf(f, "municipal")
    if mun and re.fullmatch(r"\s*(yes|no)\s*", mun, re.I):
        add(s4, "info", f"“Within or outside Municipal limits” answered just “{mun}” — ambiguous.")
    if ai.get("uncertain"):
        add(s4, "info", "Could not be read with confidence: " + "; ".join(map(str, ai["uncertain"]))[:600])
    if ai_error:
        add(rep.sections[0], "amber", ai_error)
    if free:
        add(rep.sections[0], "info", "Free mode: documents were scanned only for the printed GPS overlay. For handwritten fard/tatima, use “Copy case for Claude” and paste it into your Claude app with the documents.")
        if ai.get("error"):
            add(rep.sections[0], "amber", ai["error"])
    rep.p, rep.nbs, rep.jb, rep.v = p, nbs, jb, v
    return rep


# ───────────────────────────── Rendering ─────────────────────────────
ICON = {"red": ("●", "#b42318"), "amber": ("▲", "#8a5300"), "green": ("✓", "#145c36"), "info": ("ℹ", "#5b6475")}


def svg_map(rep, w=360, h=300):
    p, nbs = rep.p, rep.nbs
    if not p:
        return ""
    geoms = [p["m"]] + [n_["q"]["m"] for n_ in nbs]
    from shapely.ops import unary_union
    env = unary_union(geoms).envelope
    pt = rep.point
    minx, miny, maxx, maxy = env.bounds
    if pt is not None and p["m"].distance(pt) < 300:
        minx, miny, maxx, maxy = min(minx, pt.x), min(miny, pt.y), max(maxx, pt.x), max(maxy, pt.y)
    pad = 6
    sx = (w - 2 * pad) / max(1e-6, (maxx - minx))
    sy = (h - 2 * pad) / max(1e-6, (maxy - miny))
    s = min(sx, sy)

    def P(x, y):
        return (pad + (x - minx) * s, h - pad - (y - miny) * s)

    def path(g):
        polys = getattr(g, "geoms", [g])
        d = ""
        for pg in polys:
            if pg.geom_type != "Polygon":
                continue
            for ring in [pg.exterior] + list(pg.interiors):
                pts = [P(x, y) for x, y in list(ring.coords)]
                d += "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + " Z "
        return d

    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;background:#f7f9fc;border:1px solid #e1e4ea;border-radius:8px">']
    for n_ in nbs:
        g = n_["q"]["m"]
        out.append(f'<path d="{path(g)}" fill="#e9edf3" stroke="#8892a3" stroke-width="1"/>')
        c = g.representative_point()
        x, y = P(c.x, c.y)
        out.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="11" text-anchor="middle" fill="#3b4456">{esc(n_["khasra"])}</text>')
    out.append(f'<path d="{path(p["m"])}" fill="#ffe08a" stroke="#b26a00" stroke-width="2"/>')
    c = p["m"].representative_point()
    x, y = P(c.x, c.y)
    out.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="13" font-weight="700" text-anchor="middle" fill="#5a3b00">{esc(p["khasra"])}</text>')
    if pt is not None and p["m"].distance(pt) < 300:
        x, y = P(pt.x, pt.y)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#c62828" stroke="#fff" stroke-width="2"/>')
    out.append(f'<text x="{w - 14}" y="18" font-size="12" font-weight="700" fill="#3b4456" text-anchor="middle">N</text>'
               f'<path d="M{w - 14},22 L{w - 18},32 L{w - 10},32 Z" fill="#3b4456"/>')
    out.append("</svg>")
    return "".join(out)


def render(rep):
    hd = rep.head
    n_red = sum(1 for s in rep.sections for l, _ in s["items"] if l == "red")
    n_amb = sum(1 for s in rep.sections for l, _ in s["items"] if l == "amber")
    verdict = ("#b42318", f"{n_red} serious issue(s), {n_amb} to correct") if n_red else \
              (("#8a5300", f"{n_amb} point(s) to correct before issue") if n_amb else ("#145c36", "No issues found in the checks"))
    h = ['<div class="rpa" style="font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1d2330;padding:14px;max-width:900px;margin:0 auto">']
    h.append(f'<h2 style="margin:0 0 4px;font-size:18px">{esc(hd["service"] or "Application")} — Khasra {esc(hd["khasra"] or "?")}, {esc(hd["village"] or "?")}</h2>')
    h.append(f'<div style="color:#5b6475;font-size:13px">Applicant: {esc(hd["applicant"] or "—")} · App. no. {esc(hd["appNo"] or "—")}'
             f'{" · Area applied: " + km(hd["applied"]) if hd["applied"] is not None else ""}</div>')
    h.append(f'<div style="margin:10px 0;padding:10px 12px;border-radius:10px;background:#fff;border:1px solid #e1e4ea;border-left:6px solid {verdict[0]};font-weight:600">{verdict[1]}</div>')
    m = svg_map(rep)
    if m:
        h.append('<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start;margin-bottom:8px">'
                 f'<div style="flex:1;min-width:240px">{m}<div style="font-size:12px;color:#5b6475">Yellow: khasra {esc(hd["khasra"])} · grey: adjoining khasras · red dot: geotag</div></div>')
        if rep.neigh_rows:
            h.append('<div style="flex:1;min-width:240px"><b>Adjoining khasras (from map)</b><table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:4px">'
                     '<tr style="background:#f0f2f6"><th style="text-align:left;padding:4px">Side</th><th style="text-align:left;padding:4px">Khasra</th><th style="text-align:left;padding:4px">Type / cultivator</th></tr>')
            for d, k, t, c, sm in rep.neigh_rows:
                h.append(f'<tr><td style="padding:4px;border-bottom:1px solid #eceef2">{esc(d)}</td><td style="padding:4px;border-bottom:1px solid #eceef2"><b>{esc(k)}</b></td>'
                         f'<td style="padding:4px;border-bottom:1px solid #eceef2">{esc(t)}{("<br><span style=color:#5b6475>" + esc(c) + "</span>") if c else ""}</td></tr>')
            h.append("</table></div>")
        h.append("</div>")
    for s in rep.sections:
        if not s["items"]:
            continue
        h.append(f'<h3 style="font-size:15px;margin:14px 0 6px">{esc(s["title"])}</h3>')
        for lvl, text in s["items"]:
            ic, col = ICON[lvl]
            # text may include <b> we added deliberately; escape everything else
            safe = esc(text).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            h.append(f'<div style="margin:3px 0;color:{col if lvl != "info" else "#1d2330"}"><span style="color:{col}">{ic}</span> {safe}</div>')
    if rep.actions:
        seen, acts = set(), []
        for a in rep.actions:
            if a not in seen:
                seen.add(a)
                acts.append(a)
        note = "Returned to Patwari for the following:\n" + "\n".join(f"{i}. {a}" for i, a in enumerate(acts, 1))
        h.append('<h3 style="font-size:15px;margin:16px 0 6px">Suggested remark</h3>')
        h.append(f'<pre id="rpa-note" style="white-space:pre-wrap;background:#fff;border:1px solid #e1e4ea;border-radius:8px;padding:10px;font:13px/1.5 system-ui,sans-serif">{esc(note)}</pre>')
        h.append('<button data-copy="rpa-note" style="font:inherit;border:0;border-radius:8px;padding:8px 14px;background:#1a7f5a;color:#fff;cursor:pointer">Copy remark</button>')
    h.append('<p style="color:#5b6475;font-size:12px;margin-top:14px">Values marked “AI translation” or “read from documents” were read from handwritten/scanned documents by Claude — confirm them against the originals. '
             'Shares are indicative and assume the khasra is in the predecessor\'s possession as recorded. Nothing is submitted to the portal.</p></div>')
    return "".join(h)
