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
    """'11 Marlas', '1K-5M', '02k14m', '01k14', '01k', '0 kanal 11 marla 68 sqft', '05M 68sqfeet' -> marla (float) or None"""
    t = str(text or "").lower().replace(",", " ")
    if not t or re.search(r"report\s*pending", t):
        return None
    f0 = re.search(r"(\d+(?:\.\d+)?)\s*(?:sq\.?\s*f(?:ee)?t|sqft|sqfeet|sft|square\s*feet)", t)
    m = re.search(r"(\d+(?:\.\d+)?)\s*k(?:anal|nl|n)?s?\s*[-–/ ]\s*(\d+(?:\.\d+)?)\s*m", t)
    if m:
        return 20 * float(m.group(1)) + float(m.group(2)) + (float(f0.group(1)) / SQFT_PER_MARLA if f0 else 0)
    k = re.search(r"(\d+(?:\.\d+)?)\s*k(?:anal|nl|n)?s?(?![a-z])", t)
    mm = re.search(r"(\d+(?:\.\d+)?)\s*m(?:arla|arlas|arala|rl)?s?(?![a-z])", t)
    s_ = re.search(r"(\d+(?:\.\d+)?)\s*s(?:arsai|rs)(?![a-z])", t)
    f = re.search(r"(\d+(?:\.\d+)?)\s*(?:sq\.?\s*f(?:ee)?t|sqft|sqfeet|sft|square\s*feet)", t)
    if k and not mm:   # '01k14' → kanal followed by a bare number = marla
        tail = re.match(r"\s*[-–/ ]?\s*(\d+(?:\.\d+)?)(?!\s*s(?:q|arsai|rs))", t[k.end():])
        if tail:
            return 20 * float(k.group(1)) + float(tail.group(1)) + (float(f.group(1)) / SQFT_PER_MARLA if f else 0)
    if not (k or mm or s_ or f):
        return None
    return (20 * float(k.group(1)) if k else 0) + (float(mm.group(1)) if mm else 0) + \
           (float(s_.group(1)) / 9 if s_ else 0) + (float(f.group(1)) / SQFT_PER_MARLA if f else 0)

def parse_date(s):
    import datetime as _dt
    s = norm(s)
    for pat, fmts in ((r"\d{1,2}/\d{1,2}/\d{4}", ("%d/%m/%Y",)), (r"\d{1,2}[ -][A-Za-z]{3}[a-z]*[ -,]+\d{4}", ("%d %b %Y", "%d-%b-%Y")),
                      (r"[A-Za-z]{3}[a-z]*\s+\d{1,2},?\s+\d{4}", ("%b %d %Y",))):
        m = re.search(pat, s)
        if m:
            t = re.sub(r"[,]", "", m.group(0)).replace("-", " ")
            t = re.sub(r"([A-Za-z]{3})[a-z]*", r"\1", t)
            for f in fmts:
                try:
                    return _dt.datetime.strptime(t, f.replace("-", " "))
                except Exception:
                    pass
    return None


def kn(s):
    """Normalise a khasra number: '08' -> '8', '8 Min' -> '8min', ' 282 / 1 ' -> '282/1'."""
    t = re.sub(r"\s+", "", str(s or "").lower())
    t = re.sub(r"(?<!\d)0+(?=\d)", "", t)
    return t.strip("/")


def kparts(s):
    """'828/301' -> (base '828', rest ['301']); '8min' -> ('8', ['min'])"""
    t = kn(s)
    nums = re.findall(r"\d+", t)
    return (nums[0] if nums else ""), nums[1:], ("min" in t)


def first_num(s):
    m = re.match(r"\s*(\d+)", str(s or ""))
    return m.group(1) if m else ""


def name_tokens(s):
    stop = {"mst", "smt", "mrs", "mr", "ms", "sh", "shri", "late", "haji", "dr", "s", "o", "d", "w",
            "son", "daughter", "wife", "of", "and", "r", "resident", "sakindeh", "sakin", "kaum",
            "pisar", "dukhter", "zoja", "byuh", "wd", "so", "do", "wo"}
    return [t for t in re.split(r"[^a-z]+", str(s or "").lower()) if t and t not in stop and len(t) > 1]


ABBR = {"gh": "ghulam", "gul": "ghulam", "ghm": "ghulam", "mohd": "mohammad", "md": "mohammad", "mohmad": "mohammad",
        "muhammad": "mohammad", "mohammed": "mohammad", "ab": "abdul", "abd": "abdul", "ali": "ali"}


def name_key(s):
    """'Gh Mohi ud din Wani' / 'ghulam mohuidin wani' -> comparable collapsed key"""
    toks = [ABBR.get(t, t) for t in re.split(r"[^a-z]+", str(s or "").lower()) if t]
    k = "".join(toks)
    return re.sub(r"(.)\1+", r"\1", k.replace("uddin", "udin").replace("udeen", "udin").replace("uldin", "udin"))


def parent_names(text):
    """Names that follow 'son of / daughter of / s/o / d/o / w/o / pisar / dukhter' in a text."""
    out = []
    for m in re.finditer(r"(?:son|daughter|wife|widow)\s+of\s+|\b[sdw]/o\s*|\bpisar\s+|\bdukhter\s+", str(text or ""), re.I):
        words = re.findall(r"[A-Za-z]+", text[m.end():m.end() + 60])[:4]
        stop = {"as", "resident", "r", "kaum", "sakin", "sakindeh", "and", "in", "the", "is", "of", "caste"}
        nm = []
        for w_ in words:
            if w_.lower() in stop:
                break
            nm.append(w_)
        if nm:
            out.append(" ".join(nm))
    return out


def same_name(a, b, cut=0.78):
    ka, kb = name_key(a), name_key(b)
    return bool(ka and kb) and (similar(ka, kb) >= cut or (len(ka) > 8 and (ka in kb or kb in ka)))


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
        cur_entry["khasra"] = ks = kn(ks)
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
    khasra = kn(khasra)
    base = first_num(khasra) or str(khasra)
    ps = [p for p in v["map"]["parcels"] if kn(p["khasra"]) == khasra] or \
         [p for p in v["map"]["parcels"] if p["khasra"] == base]
    if not ps:
        return None
    if len(ps) == 1:
        return ps[0]
    from shapely.ops import unary_union
    return {"khasra": ps[0]["khasra"], "geom": unary_union([p["geom"] for p in ps]),
            "m": unary_union([p["m"] for p in ps]), "type": ps[0]["type"], "ror": ps[0]["ror"]}


def neighbours(v, p):
    """Adjoining parcels with the compass side they lie on — taken from the direction the shared
    boundary faces (outward normal), so long strips and diagonal plots get correct sides."""
    from shapely.geometry.polygon import orient
    from shapely.geometry import LineString
    t = p["m"]
    polys = [orient(g_, 1.0) for g_ in getattr(t, "geoms", [t]) if g_.geom_type == "Polygon"]
    segs = []
    for pg in polys:
        cs = list(pg.exterior.coords)
        for (x1, y1), (x2, y2) in zip(cs, cs[1:]):
            if (x1, y1) != (x2, y2):
                segs.append(((x1, y1), (x2, y2), LineString([(x1, y1), (x2, y2)])))
    out = []
    tb = t.buffer(1.5)
    for q in v["map"]["parcels"]:
        if q is p or (q["khasra"] and q["khasra"] == p["khasra"]):
            continue
        if not q["m"].intersects(tb):
            continue
        zone = q["m"].buffer(1.5)
        nx = ny = shared = 0.0
        for (x1, y1), (x2, y2), ln in segs:
            l_ = ln.intersection(zone).length
            if l_ <= 0:
                continue
            L = math.hypot(x2 - x1, y2 - y1)
            nx += (y2 - y1) / L * l_       # outward normal of a CCW ring = (dy, -dx)
            ny += -(x2 - x1) / L * l_
            shared += l_
        if shared < 1:
            continue
        ang = math.degrees(math.atan2(nx, ny)) % 360
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
    k = kn(khasra)
    return ks.get(k) or ks.get(first_num(k))


def khasra_family(v, khasra):
    """All Jamabandi entries belonging to khasra K: K itself, K/1 K/2 sub-divisions, K min,
    and new numbers carved out of K (e.g. 828/K, or old-khasra column = K)."""
    if not v or not v["jb"]:
        return []
    K = first_num(kn(khasra))
    if not K:
        return []
    out = []
    for key, entries in v["jb"]["khasras"].items():
        base, rest, is_min = kparts(key)
        for e in entries:
            old_nums = re.findall(r"\d+", kn(e.get("khasra_old")))
            rel = None
            if base == K and not rest and not is_min:
                rel = "same number"
            elif base == K and is_min:
                rel = "part (min)"
            elif base == K and rest:
                rel = "sub-division of " + K
            elif K in old_nums or (rest and rest[-1] == K and int(K) >= 10):
                rel = "carved out of " + K
            elif K in rest[:-1]:
                rel = "carved out of " + K + " (via " + "/".join(rest) + ")"
            if rel:
                out.append(dict(e, relation=rel))
    order = {"same number": 0, "part (min)": 1}
    return sorted(out, key=lambda e: (order.get(e["relation"], 2), [int(x) for x in re.findall(r"\d+", e["khasra"])]))


TRANSFER = re.compile(r"baya|bay'?a|sale|hiba|gift|tabadla|exchange|rehan|mortgage|lease|ijara|award|acquisition|hasool|sehat|family\s*settle|partition|taqseem|khangi", re.I)


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
def trim_memory():
    """Give freed memory back to the OS (glibc); keeps the Render free plan under its limit."""
    import gc
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


def doc_to_images(label, mime, b64, max_side=1400, seen=None):
    """Render document pages one at a time (low memory), skipping duplicate pages early."""
    import gc
    from PIL import Image
    raw = base64.b64decode(b64)
    seen = seen if seen is not None else set()
    out = []

    def add_img(lab, im):
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=80)
        out.append({"label": lab, "data": base64.b64encode(buf.getvalue()).decode()})

    if "pdf" in (mime or "") or raw[:4] == b"%PDF":
        import fitz  # pymupdf
        try:
            fitz.TOOLS.store_maxsize = 20 * 1024 * 1024
        except Exception:
            pass
        doc = fitz.open(stream=raw, filetype="pdf")
        del raw
        for i, page in enumerate(doc):
            if i >= 30:
                break
            # 1) tiny render to detect duplicate pages cheaply
            tz = 48 / max(page.rect.width, page.rect.height)
            tp = page.get_pixmap(matrix=fitz.Matrix(tz, tz), colorspace=fitz.csGRAY)
            h = hashlib.md5(Image.frombytes("L", (tp.width, tp.height), tp.samples).resize((24, 24)).tobytes()).hexdigest()
            del tp
            if h in seen:
                continue
            seen.add(h)
            # 2) real render at modest resolution
            zoom = min(1.6, max_side / max(page.rect.width, page.rect.height))
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB, alpha=False)
            im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            del pix
            add_img(f"{label} — page {i + 1}", im)
            del im
            fitz.TOOLS.store_shrink(100)
        doc.close()
        trim_memory()
    else:
        try:
            im = Image.open(io.BytesIO(raw))
            frames = getattr(im, "n_frames", 1)
            for i in range(min(frames, 10)):
                im.seek(i)
                fr = im.convert("RGB")
                h = hashlib.md5(fr.convert("L").resize((24, 24)).tobytes()).hexdigest()
                if h in seen:
                    continue
                seen.add(h)
                add_img(f"{label}" + (f" — page {i + 1}" if frames > 1 else ""), fr)
        except Exception:
            return []
    for o in out:
        o["hash"] = hashlib.md5(o["data"][:2000].encode()).hexdigest()
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


def _get_ocr():
    global _ocr
    if _ocr is None:
        import onnxruntime as ort
        import rapidocr_onnxruntime.utils as ru

        class OneThread(ort.SessionOptions):          # Render free = a fraction of one CPU: avoid thread thrash
            def __init__(self, *a, **k):
                super().__init__(*a, **k)
                self.intra_op_num_threads = 1
                self.inter_op_num_threads = 1
        ru.SessionOptions = OneThread
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR(use_angle_cls=False, det_model_path=None, det_limit_side_len=960, det_limit_type="max")
    return _ocr


GPS_RE = re.compile(r"Lat(?:itude)?\s*[:.]?\s*(\d{1,2}\.\d{3,})\s*°?\s*[NS]?\s*,?\s*Lon(?:g(?:itude)?)?\s*[:.]?\s*(\d{2,3}\.\d{3,})", re.I)


def _colourfulness(im):
    """Share of strongly coloured pixels — photos score high, scanned forms low."""
    t = im.convert("HSV").resize((64, 64))
    sat = list(t.getdata(1))
    return sum(1 for x in sat if x > 70) / len(sat)


def free_read(pages):
    """Free mode (no API key): OCR the printed GPS overlay of a geotagged photo. Handwriting is not read."""
    out = {"mode": "free", "photo": {"found": False}}
    try:
        import numpy as np
        from PIL import Image
        ocr = _get_ocr()
        cands = []
        for p in pages:
            im = Image.open(io.BytesIO(base64.b64decode(p["data"]))).convert("RGB")
            cands.append((_colourfulness(im), p, im))
        cands.sort(key=lambda c: -c[0])
        # photos first; plain scans (almost no colour) only if nothing found
        tries = [c for c in cands if c[0] >= 0.08] + [c for c in cands if c[0] < 0.08]
        for col, p, im in tries:
            w, h = im.size
            for box in ((0, int(h * 0.55), w, h), (0, 0, w, h)):   # bottom strip first, then whole page
                crop = im.crop(box)
                crop.thumbnail((1000, 1000))
                res, _ = ocr(np.array(crop))
                txt = " ".join(r[1] for r in (res or []))
                m = GPS_RE.search(txt)
                if m and 6 <= float(m.group(1)) <= 38 and 68 <= float(m.group(2)) <= 98:
                    dt = re.search(r"(\d{1,2}/\d{1,2}/\d{4})\s*(\d{1,2}:\d{2}\s*[AP]M)?", txt, re.I)
                    pc = re.search(r"\b([23456789CFGHJMPQRVWX]{4,8}\+[23456789CFGHJMPQRVWX]{2,3})\b", txt.upper())
                    out["photo"] = {"found": True, "lat": float(m.group(1)), "lng": float(m.group(2)),
                                    "pluscode": pc.group(1) if pc else "",
                                    "datetime": " ".join(x for x in dt.groups() if x) if dt else "", "label": p["label"]}
                    trim_memory()
                    return out
                if "gps" not in txt.lower() and box[1] > 0 and col < 0.08:
                    break   # plain scan with no GPS text in the bottom strip: skip full-page OCR
        trim_memory()
    except Exception as e:
        out["error"] = f"OCR failed: {e}"
    return out


def read_documents_gemini(pages, ctx):
    """Read documents with Google Gemini (free or paid key). Same JSON shape as the Claude reader."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None, "GEMINI_API_KEY is not set."
    if not pages:
        return None, "No readable documents were received."
    import requests
    model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
    parts = []
    for p in pages[:int(os.environ.get("MAX_PAGES", "16"))]:
        parts.append({"text": f"[{p['label']}]"})
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": p["data"]}})
    parts.append({"text": READ_PROMPT.format(**ctx)})
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json", "maxOutputTokens": 8000}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    try:
        r = requests.post(url, json=body, timeout=170, headers={"x-goog-api-key": key, "content-type": "application/json"})
        if r.status_code == 429:
            return None, "Gemini free-tier limit reached for now — try again later (record checks below are unaffected)."
        if r.status_code != 200:
            return None, f"Gemini error {r.status_code}: {r.text[:300]}"
        cands = r.json().get("candidates") or []
        txt = "".join(p_.get("text", "") for c in cands[:1] for p_ in (c.get("content") or {}).get("parts", []))
        m = re.search(r"\{.*\}", txt, re.S)
        if not m:
            return None, "Gemini returned no readable result (the documents may have been blocked or unreadable)."
        out = json.loads(m.group(0))
        out["mode"] = "gemini"
        return out, None
    except Exception as e:
        return None, f"Gemini reading failed: {e}"


def merge_ocr(ai, ocr):
    """Use exact OCR numbers for the GPS stamp; keep the AI's description of the photo."""
    ai = ai or {}
    o = (ocr or {}).get("photo") or {}
    if o.get("found"):
        ph = ai.get("photo") or {}
        ph.update({k: o[k] for k in ("lat", "lng", "pluscode", "datetime") if o.get(k) not in (None, "")})
        ph["found"], ph["source"] = True, "OCR"
        ai["photo"] = ph
    return ai


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
        out = json.loads(m.group(0))
        out["mode"] = "claude"
        return out, None
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
    khasra = kn(re.split(r"[,;]", khasra)[0]) if khasra else ""
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
        if v["map"] and not p:
            add(s0, "amber", f"Khasra {khasra} not found on the village map (it may be an unnumbered parcel or a new sub-division).")

    # ── 1. Geotag
    # ── Khasra family: K, K/1.., K min, numbers carved out of K
    fam = khasra_family(v, khasra) if v else []
    if v and v["jb"]:
        K = first_num(khasra)
        sf = rep.sec(f"Khasra {K} — all entries in the Jamabandi (sub-divisions, “min”, carved-out numbers)")
        if not fam:
            add(sf, "red", f"No entry for khasra {K} (or its sub-divisions) in the Jamabandi on file.",
                f"Check khasra number {khasra} — not found in the village Jamabandi.", rep)
        else:
            if not jb:
                jb = next((e for e in fam if e["relation"] == "same number"), fam[0])
                jbs = [jb]
            T = '<td style="padding:4px 6px;border-bottom:1px solid #eceef2;vertical-align:top">'
            rows = ['<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:12.5px;margin:4px 0">'
                    '<tr style="background:#f0f2f6"><th style="text-align:left;padding:4px 6px">Khasra</th><th style="text-align:left;padding:4px 6px">How related</th>'
                    '<th style="text-align:left;padding:4px 6px">Khewat / Khata</th><th style="text-align:right;padding:4px 6px">Area</th>'
                    '<th style="text-align:left;padding:4px 6px">Land type</th><th style="text-align:left;padding:4px 6px">Mutation</th>'
                    '<th style="text-align:left;padding:4px 6px">Cultivator / possession</th></tr>']
            total = alien = 0.0
            alien_rows = []
            for e in fam:
                total += e["area_marla"] or 0
                is_tr = bool(e["mut_type"]) and bool(TRANSFER.search(e["mut_type"])) and not re.search(r"inherit|warasat", e["mut_type"], re.I)
                if is_tr:
                    alien += e["area_marla"] or 0
                    owners = v["jb"]["khewats"].get(e["khewat"], {}).get("owners", "")
                    alien_rows.append((e, owners))
                hl = "background:#fff7da;" if is_tr else ""
                rows.append(f'<tr style="{hl}">{T}<b>{esc(e["khasra"])}</b>{(" <span style=color:#5b6475>(old " + esc(e["khasra_old"]) + ")</span>") if e.get("khasra_old") else ""}</td>'
                            f'{T}{esc(e["relation"])}</td>{T}{esc(e["khewat_no"])} / {esc(e["khata_no"])}</td>'
                            f'<td style="padding:4px 6px;border-bottom:1px solid #eceef2;text-align:right;white-space:nowrap">{km(e["area_marla"])}</td>'
                            f'{T}{esc(e["qism"])}</td>{T}{esc((e["mut_no"] or "—") + (" " + e["mut_type"] if e["mut_type"] else ""))}</td>'
                            f'{T}{esc(e["cultivator"][:140])}</td></tr>')
            rows.append(f'<tr style="font-weight:700"><td colspan="3" style="padding:4px 6px">Total ({len(fam)} entr{"y" if len(fam) == 1 else "ies"})</td>'
                        f'<td style="padding:4px 6px;text-align:right;white-space:nowrap">{km(total)}</td><td colspan="3"></td></tr></table></div>')
            add(sf, "html", "".join(rows))
            if applied is not None and applied > total + 0.25:
                add(sf, "red", f"Area applied ({km(applied)}) is MORE than the whole recorded area of khasra {K} ({km(total)}).",
                    f"Area applied {km(applied)} exceeds total area of khasra {K} ({km(total)}) — verify.", rep)
            if len(fam) == 1:
                add(sf, "info", f"Khasra {K} is not sub-divided in the Jamabandi: one entry of {km(total)}.")
            else:
                add(sf, "info", f"Khasra {K} appears as {len(fam)} entries: " + ", ".join(dict.fromkeys(e['khasra'] for e in fam)) + f"; total recorded area {km(total)}.")
            if alien_rows:
                add(sf, "info", f"Area that has passed by sale / gift / partition etc. (Jamabandi): <b>{km(alien)}</b> of {km(total)}:")
                for e, owners in alien_rows:
                    add(sf, "info", f"&nbsp;&nbsp;• {e['khasra']}: {km(e['area_marla'])} by mutation {e['mut_no'] or '—'} ({e['mut_type']}); possession: {e['cultivator'][:120] or '—'}; now owned by: {owner_entries(owners)[0][:90] if owners else '—'}"
                        + (f" and {len(owner_entries(owners)) - 1} others" if owners and len(owner_entries(owners)) > 1 else ""))
            else:
                kinds = sorted({e['mut_type'] for e in fam if e['mut_type']})
                add(sf, "info", f"No sale / gift / partition mutation is recorded against khasra {K} in the Jamabandi on file"
                                + (f" (only {', '.join(kinds)})." if kinds else " (no mutation reference at all — ownership as per settlement record)."))
            # portal mutations (who gave how much to whom)
            pm = [r for r in ((app.get("mut") or {}).get("gist") or []) + ((app.get("mut") or {}).get("final") or [])
                  if any(re.search(r"\d", str(x)) for x in r.values())]
            for r in pm:
                def g_(pat, r=r):
                    return next((norm(v_) for k_, v_ in r.items() if re.search(pat, k_, re.I)), "")
                q = 20 * (num(g_(r"^\s*kanal")) or 0) + (num(g_(r"^\s*marla")) or 0) + (num(g_(r"sq")) or 0) / SQFT_PER_MARLA
                mno, mty, mdt = g_(r"mutation\s*no") or "—", g_(r"type") or "—", g_(r"date") or "—"
                fp, sp = g_(r"first")[:160], g_(r"second")[:120]
                add(sf, "info", f"Portal mutation {mno} ({mty}, {mdt}): by <b>{fp}</b> → in favour of <b>{sp}</b>; quantum {km(q) if q else '—'}.")
                if q and q > total + 0.25:
                    add(sf, "amber", f"Mutation {mno} quantum ({km(q)}) is more than the recorded area of khasra {K} ({km(total)}).",
                        f"Mutation {mno} quantum {km(q)} exceeds khasra {K} area {km(total)} — check.", rep)
            # map comparison
            if v["map"]:
                nums = {first_num(e["khasra"]) for e in fam} | {K}
                on_map = [p_ for p_ in v["map"]["parcels"] if first_num(kn(p_["khasra"])) in nums]
                if on_map:
                    m2 = sum(p_["m"].area for p_ in on_map)
                    diff = m2 / MARLA_M2 - total
                    lvl = "green" if abs(diff) <= max(2, 0.08 * total) else "amber"
                    add(sf, lvl, f"Map survey: parcel(s) {', '.join(sorted({kn(p_['khasra']) for p_ in on_map}, key=lambda x: int(first_num(x) or 0)))} measure "
                                 f"{m2:.0f} m² ≈ {km(m2 / MARLA_M2)} vs Jamabandi {km(total)} (difference {km(diff) if diff >= 0 else '−' + km(-diff)}).")
                    missing = sorted(nums - {first_num(kn(p_['khasra'])) for p_ in on_map}, key=lambda x: int(x))
                    if missing:
                        add(sf, "info", f"Not drawn separately on the map: {', '.join(missing)} (may lie inside the parent parcel).")
                else:
                    add(sf, "amber", f"Khasra {K} is not drawn on the village map.")

    # ── Application, Patwari report and remarks: consistency across the whole page
    final = [r_ for r_ in ((app.get("mut") or {}).get("final") or []) if any(re.search(r"\w", str(x)) for x in r_.values())]
    sc = rep.sec("Application, Patwari report and remarks")
    hist = app.get("history") or []
    if hist:
        lines = []
        for h_ in hist:
            lines.append(f"{h_.get('date') or ''} — {h_.get('by') or ''}: {norm(h_.get('remark'))[:220]}")
        add(sc, "info", "Movement: " + " | ".join(lines))
    if jb:
        for lab, key, want in (("Khewat", "aKhewat", jb["khewat_no"]), ("Khata", "aKhata", jb["khata_no"])):
            for k2 in (key, "c" + key[1:]):
                val = pf(f, k2)
                if val and re.fullmatch(r"na|n/a|nil|-+|0", val, re.I):
                    add(sc, "amber", f"{lab} entered as “{val}” ({'application' if k2 == key else 'certificate'}) though the Jamabandi has {lab.lower()} {want}.",
                        f"Enter {lab.lower()} {want} instead of “{val}”.", rep)
                    break
    # alienated in khewat vs khasra
    ak, akh = parse_area(pf(f, "alienKhewat")), parse_area(pf(f, "alienKhasra"))
    if pf(f, "alienKhewat") and re.fullmatch(r"\s*0\s*", pf(f, "alienKhewat")):
        ak = 0.0
    if pf(f, "alienKhasra") and re.fullmatch(r"\s*0\s*", pf(f, "alienKhasra")):
        akh = 0.0
    if jb and v and v["jb"]:
        kw_khasras = sorted({k for k, es in v["jb"]["khasras"].items() for e in es if e["khewat"] == jb["khewat"]})
        transfers = [e for es in v["jb"]["khasras"].values() for e in es if e["khewat"] == jb["khewat"]
                     and e["mut_type"] and TRANSFER.search(e["mut_type"]) and not re.search(r"inherit|warasat", e["mut_type"], re.I)]
        if ak is not None and akh is not None and len(kw_khasras) == 1 and abs(ak - akh) > 0.25:
            add(sc, "red", f"Report says {km(ak)} already alienated in the khewat but {km(akh)} in the khasra — khewat {jb['khewat_no']} contains only khasra {kw_khasras[0]}, so both must be the same.",
                f"Rectify “area already alienated” (khewat {km(ak)} vs khasra {km(akh)}; khewat has only khasra {kw_khasras[0]}).", rep)
        if ak and ak > 0.25 and not transfers:
            add(sc, "amber", f"Report says {km(ak)} already alienated in khewat {jb['khewat_no']}, but the Jamabandi on file shows no sale/gift mutation in this khewat.",
                f"Give the deed/mutation for the {km(ak)} already alienated.", rep)
        skw, skh = parse_area(pf(f, "shareKhewat")), parse_area(pf(f, "shareKhasra"))
        kw_area = v["jb"]["khewats"].get(jb["khewat"], {}).get("area_marla")
        if skw is not None and kw_area and len(owner_entries(v["jb"]["khewats"].get(jb["khewat"], {}).get("owners", ""))) == 1 and abs(skw - kw_area) > 0.25:
            add(sc, "amber", f"Share in khewat stated {km(skw)}; Jamabandi khewat {jb['khewat_no']} (single owner) is {km(kw_area)}.", "Reconcile share in khewat with Jamabandi.", rep)
        if skh is not None and applied is not None and applied > skh + 0.25:
            add(sc, "red", f"Area proposed ({km(applied)}) exceeds the applicant's stated share in the khasra ({km(skh)}).", "Area proposed exceeds share in khasra.", rep)
    # possession
    poss = pf(f, "possession")
    cult = (jb or {}).get("cultivator", "")
    rem_poss = [h_ for h_ in hist if re.search(r"possession|kashtkar|cultivat|girdawari", norm(h_.get("remark")), re.I)]
    if re.match(r"\s*yes", poss, re.I) and rem_poss:
        add(sc, "amber", f"Report says applicant is in possession, but a remark says: “{norm(rem_poss[0].get('remark'))[:200]}” ({rem_poss[0].get('by')}).",
            "Clarify possession: report says “Yes” but remarks/Girdawari show another kashtkar.", rep)
    if cult and not re.search(r"khud\s*kasht|self", cult, re.I) and re.match(r"\s*yes", poss, re.I):
        add(sc, "info", f"Jamabandi cultivator column: “{cult[:120]}” — check against “applicant in possession: Yes”.")
    # vendee relation to occupier
    vparent = pf(f, "vendeeParent")
    if vparent:
        for h_ in rem_poss + ([{"remark": cult, "by": "Jamabandi cultivator column"}] if cult else []):
            if any(same_name(vparent, pn) for pn in parent_names(h_.get("remark"))):
                add(sc, "info", f"Vendee {pf(f, 'vendee') or ''} (d/o or s/o {vparent}) shares her parentage with the person shown in possession ({h_.get('by')}) — "
                                "the vendee appears to be of the occupier's family; the sale may regularise existing possession. Verify the possession position before issue.")
                break
    # land type vs urban / eligibility
    agri = jb and re.search(r"abi|abe|aabi|wari|bagh|baag|maidan|medani|khushk|nehri|chahi", jb["qism"], re.I)
    if agri and (re.search(r"urban", pf(f, "areaType"), re.I) or re.match(r"\s*yes", pf(f, "municipal"), re.I)):
        add(sc, "info", f"Land is agricultural ({jb['qism']}) and shown as Urban / within municipal limits — check land-use (conversion) requirements before alienation.")
    if pf(f, "vendee") and agri and re.search(r"^\s*(nil|none|0)\s*$", pf(f, "landUT"), re.I):
        add(sc, "info", f"Vendee owns no land in the UT (occupation: {pf(f, 'vendeeOcc') or '—'}) — verify eligibility to purchase agricultural land under the transfer restrictions (J&K Land Revenue Act s.133-B).")
    av = pf(f, "vendeeAadhaarOk")
    if av == "invalid":
        add(sc, "red", "Vendee's Aadhaar number on the portal fails the Aadhaar check-digit test — it is mistyped or not genuine.", "Correct the vendee's Aadhaar number.", rep)
    elif av == "valid":
        add(sc, "green", "Vendee's Aadhaar number passes the Aadhaar check-digit test (format only — confirm with the QR code).")
    if final and all(re.search(r"nil|na", " ".join(map(str, r_.values())), re.I) for r_ in final):
        add(sc, "info", "Final mutation entered as NILL/NA (ownership from Misl Haqiyat / pre-settlement) — consistent only if the Jamabandi shows the applicant as owner.")

    s1 = rep.sec("Geotagged photograph")
    ph = ai.get("photo") or {}
    lat = num(pf(f, "lat")) or num(ph.get("lat"))
    lng = num(pf(f, "lng")) or num(ph.get("lng"))
    free = ai.get("mode") == "free"
    reader = {"gemini": "Gemini", "claude": "Claude"}.get(ai.get("mode"), "AI")
    src = "Patwari report" if num(pf(f, "lat")) else (("photo overlay (" + ("read by OCR" if (free or ph.get("source") == "OCR") else f"read by {reader}") + ")") if num(ph.get("lat")) else "")
    rep.point = None
    rep.geo = (lat, lng) if lat is not None and lng is not None else None
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
    if ph.get("found") and ph.get("pluscode") and lat is not None:
        try:
            import pluscode
            plat, plng, _ = pluscode.recover(ph["pluscode"], lat, lng)
            dpc = math.hypot((plat - lat) * 111000, (plng - lng) * 111000 * math.cos(math.radians(lat)))
            if dpc <= 200:
                add(s1, "green", f"Plus Code on the photo ({ph['pluscode']}) agrees with the printed lat/long ({dpc:.0f} m apart — normal for the camera app's address line).")
            else:
                add(s1, "red", f"Plus Code on the photo ({ph['pluscode']}) points {dpc:.0f} m away from the printed lat/long — the overlay may have been edited or the location set manually.",
                    "Geotag overlay inconsistent (Plus Code vs lat/long) — get a fresh geotagged photo in presence of Patwari.", rep)
        except Exception:
            pass
    if ph.get("found") and ph.get("datetime"):
        pdt, adt = parse_date(ph["datetime"]), parse_date(app.get("appDate") or "")
        if pdt and adt:
            gap = (adt - pdt).days
            if gap > 60:
                add(s1, "amber", f"Photo is dated {pdt:%d %b %Y}, {gap} days before the application — not a recent spot photo.", "Get a recent geotagged photo of the spot.", rep)
            elif gap < -1:
                add(s1, "info", f"Photo dated {pdt:%d %b %Y}, after the application date (taken during processing).")
    if ph.get("found"):
        add(s1, "info", "Note: the GPS stamp is text drawn on the picture by a camera app; it can be faked with location-spoofing or edited. "
                        "Rely on it only when the Plus Code, the mini-map and the scene agree, or have the Patwari capture the photo himself.")
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
        add(s2, "info", f"Read by {reader} from documents: mutation {m_.get('number') or '—'} ({m_.get('type') or '—'}{', ' + m_['date'] if m_.get('date') else ''}): {m_.get('summary') or ''}")
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
            add(s2, "info", f"Fard remark {i} ({reader} translation — confirm): {rmk}")
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
        add(s4, "info", f"Tatima as read by {reader}: {tt.get('as_written') or '—'}; shaded side: {tt.get('shaded_side') or '—'} (confirm on the sketch).")
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
    if nbs:
        have = {n_["dir"] for n_ in nbs}
        empty = [d for d in ("North", "East", "South", "West") if not any(d in x for x in have)]
        if empty:
            add(s4, "info", f"No parcel is drawn against the {', '.join(empty)} side(s) on the map — likely a road, nallah or unmapped land; Patwari should state what bounds it there.")
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
        pass
    if ai.get("uncertain"):
        add(s4, "info", "Could not be read with confidence: " + "; ".join(map(str, ai["uncertain"]))[:600])
    if ai_error:
        add(rep.sections[0], "amber", ai_error)
    if free:
        if ai.get("error"):
            add(rep.sections[0], "amber", ai["error"])
    rep.p, rep.nbs, rep.jb, rep.v = p, nbs, jb, v
    rep.ai, rep.reader, rep.free = ai, reader, free
    return rep


# ───────────────────────────── Rendering ─────────────────────────────
ICON = {"red": ("●", "#b42318"), "amber": ("▲", "#8a5300"), "green": ("✓", "#145c36"), "info": ("ℹ", "#5b6475")}


def coords_block(rep):
    p = rep.p
    if not p:
        return ""
    import urllib.parse
    g = p["geom"]
    c = g.representative_point()
    sat = lambda la, lo: f"https://www.google.com/maps/@?api=1&map_action=map&center={la:.6f},{lo:.6f}&zoom=20&basemap=satellite"
    pin = lambda la, lo: f"https://www.google.com/maps/search/?api=1&query={la:.6f},{lo:.6f}"
    a = 'style="color:#12355b;font-weight:600"'
    rows = [f'<div style="background:#fff;border:1px solid #e1e4ea;border-radius:10px;padding:10px 12px;margin:6px 0 10px;font-size:13px">'
            f'<b>Exact location</b><div style="margin-top:4px">Khasra {esc(p["khasra"])} centre: <code>{c.y:.6f}, {c.x:.6f}</code> · '
            f'<a {a} href="{sat(c.y, c.x)}" target="_blank" rel="noopener">Open in Google Maps (satellite)</a></div>']
    if getattr(rep, "geo", None):
        la, lo = rep.geo
        rows.append(f'<div>Geotag of photo: <code>{la:.6f}, {lo:.6f}</code> · <a {a} href="{pin(la, lo)}" target="_blank" rel="noopener">Show point in Google Maps</a></div>')
    simp = g.simplify(0.000004, preserve_topology=True)
    ring = list((simp.geoms[0] if hasattr(simp, "geoms") else simp).exterior.coords)[:-1]
    if 3 <= len(ring) <= 40:
        pts = " · ".join(f"P{i + 1} {y:.6f}, {x:.6f}" for i, (x, y) in enumerate(ring))
        rows.append(f'<details style="margin-top:4px"><summary style="cursor:pointer">Boundary points of khasra {esc(p["khasra"])} ({len(ring)})</summary>'
                    f'<div style="font:12px/1.6 ui-monospace,monospace;color:#3b4456">{esc(pts)}</div></details>')
    # KML (khasra + neighbours + geotag) as a download
    def kml_poly(name, geom, colour):
        out = ""
        for pg in getattr(geom, "geoms", [geom]):
            if pg.geom_type != "Polygon":
                continue
            cs = " ".join(f"{x:.7f},{y:.7f},0" for x, y in pg.exterior.coords)
            out += (f"<Placemark><name>{esc(name)}</name><Style><LineStyle><color>{colour}</color><width>3</width></LineStyle>"
                    f"<PolyStyle><fill>0</fill></PolyStyle></Style><Polygon><outerBoundaryIs><LinearRing><coordinates>{cs}</coordinates>"
                    f"</LinearRing></outerBoundaryIs></Polygon></Placemark>")
        return out
    kml = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
    kml += kml_poly(f"Khasra {p['khasra']}", g, "ff00d4ff")
    for n_ in rep.nbs:
        kml += kml_poly(f"Khasra {n_['khasra']}", n_["q"]["geom"], "ffb0b0b0")
    if getattr(rep, "geo", None):
        kml += f"<Placemark><name>Geotag</name><Point><coordinates>{rep.geo[1]:.7f},{rep.geo[0]:.7f},0</coordinates></Point></Placemark>"
    kml += "</Document></kml>"
    href = "data:application/vnd.google-earth.kml+xml;charset=utf-8," + urllib.parse.quote(kml)
    rows.append(f'<div style="margin-top:4px"><a {a} download="khasra_{esc(p["khasra"])}.kml" href="{href}">Download KML (open in Google Earth)</a></div></div>')
    return "".join(rows)


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
    # scale bar (round number of metres ≈ 1/4 of width)
    want = (w / 4) / s
    step = next((x for x in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000) if x >= want), 1000)
    bl = step * s
    out.append(f'<path d="M10,{h - 12} h{bl:.1f}" stroke="#3b4456" stroke-width="3"/>'
               f'<text x="{10 + bl / 2:.1f}" y="{h - 16}" font-size="10" text-anchor="middle" fill="#3b4456">{step} m</text>')
    out.append(f'<text x="{w - 14}" y="18" font-size="12" font-weight="700" fill="#3b4456" text-anchor="middle">N</text>'
               f'<path d="M{w - 14},22 L{w - 18},32 L{w - 10},32 Z" fill="#3b4456"/>')
    out.append("</svg>")
    return "".join(out)


def case_text(rep):
    """Plain-text case for pasting into a Claude chat (final review). No ID or phone numbers."""
    hd = rep.head
    L = ["Please review this Revenue Plus application as a Naib Tehsildar in J&K would, and make the final call.",
         "Below are automated record checks (village Jamabandi + map) and values read from the uploaded documents "
         f"by {getattr(rep, 'reader', 'AI') if not getattr(rep, 'free', False) else 'OCR (GPS stamp only)'}. "
         "If I attach the documents, verify the AI-read values against them. Give: (1) final assessment, (2) discrepancies by severity, "
         "(3) anything the checks missed, (4) a remark I can enter on the portal.", "",
         f"## Application: {hd.get('service') or ''} — khasra {hd.get('khasra')}, village {hd.get('village')}; applicant {hd.get('applicant')}; "
         f"app. no. {hd.get('appNo')}; area applied {km(hd['applied']) if hd.get('applied') is not None else '—'}"]
    sym = {"red": "[SERIOUS]", "amber": "[CORRECT]", "green": "[OK]", "info": "-"}
    for s in rep.sections:
        if not s["items"]:
            continue
        L.append("")
        L.append("## " + s["title"])
        for lvl, text in s["items"]:
            if lvl == "html":
                rows = re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S)
                for r_ in rows:
                    cells = [norm(re.sub(r"<[^>]+>", " ", c)) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r_, re.S)]
                    if any(cells):
                        L.append("  | " + " | ".join(cells))
                continue
            L.append(f"{sym[lvl]} " + html.unescape(re.sub(r"<[^>]+>", "", text)).replace("\xa0", " "))
    if getattr(rep, "neigh_rows", None):
        L.append("")
        L.append("## Adjoining khasras (map)")
        for d, k, t, c, sm in rep.neigh_rows:
            L.append(f"- {d}: {k} — {t}{'; ' + c if c else ''}")
    ai = getattr(rep, "ai", None) or {}
    if ai and not getattr(rep, "free", False):
        keep = {k: ai.get(k) for k in ("fard", "mutations", "tatima", "uncertain") if ai.get(k)}
        if ai.get("photo"):
            keep["photo"] = {k: v for k, v in ai["photo"].items() if k in ("lat", "lng", "pluscode", "datetime", "land_description", "built_up", "person_present")}
        if keep:
            L.append("")
            L.append(f"## Raw values read by {getattr(rep, 'reader', 'AI')} (unverified)")
            L.append(json.dumps(keep, ensure_ascii=False, indent=1)[:6000])
    if rep.actions:
        L.append("")
        L.append("## Remark suggested by the checks")
        for i, a in enumerate(dict.fromkeys(rep.actions), 1):
            L.append(f"{i}. {a}")
    out = "\n".join(L)
    out = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[number removed]", out)    # never carry Aadhaar-like numbers
    out = re.sub(r"\b[6-9]\d{9}\b", "[number removed]", out)                    # or mobile numbers
    return out


def render(rep):
    hd = rep.head
    n_red = sum(1 for s in rep.sections for l, _ in s["items"] if l == "red")  # html items ignored
    n_amb = sum(1 for s in rep.sections for l, _ in s["items"] if l == "amber")
    verdict = ("#b42318", f"{n_red} serious issue(s), {n_amb} to correct") if n_red else \
              (("#8a5300", f"{n_amb} point(s) to correct before issue") if n_amb else ("#145c36", "No issues found in the checks"))
    h = ['<div class="rpa" style="font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1d2330;padding:14px;max-width:900px;margin:0 auto">']
    h.append(f'<h2 style="margin:0 0 4px;font-size:18px">{esc(hd["service"] or "Application")} — Khasra {esc(hd["khasra"] or "?")}, {esc(hd["village"] or "?")}</h2>')
    h.append(f'<div style="color:#5b6475;font-size:13px">Applicant: {esc(hd["applicant"] or "—")} · App. no. {esc(hd["appNo"] or "—")}'
             f'{" · Area applied: " + km(hd["applied"]) if hd["applied"] is not None else ""}</div>')
    h.append(f'<div style="margin:10px 0;padding:10px 12px;border-radius:10px;background:#fff;border:1px solid #e1e4ea;border-left:6px solid {verdict[0]};font-weight:600">{verdict[1]}</div>')
    rs = getattr(rep, "reader_status", None)
    if rs:
        if rs.get("error"):
            col, txt = "#b42318", f"✗ {rs['used']} could not read the documents: {rs['error']}"
        elif rs["used"].startswith("Free"):
            col, txt = "#5b6475", f"Documents: {rs['used']}"
        else:
            col, txt = "#145c36", f"✓ Documents read by {rs['used']}: {', '.join(rs['read']) or 'nothing recognisable'}"
        h.append(f'<div style="margin:-4px 0 10px;font-size:12.5px;color:{col}">{esc(txt)} · {rs["pages"]} page(s), {rs["secs"]} s</div>')
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
    h.append(coords_block(rep))
    for s in rep.sections:
        if not s["items"]:
            continue
        h.append(f'<h3 style="font-size:15px;margin:14px 0 6px">{esc(s["title"])}</h3>')
        for lvl, text in s["items"]:
            if lvl == "html":
                h.append(text)
                continue
            ic, col = ICON[lvl]
            # text may include <b> we added deliberately; escape everything else
            safe = esc(text).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>").replace("&amp;nbsp;", "&nbsp;")
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
        h.append('<button data-copy="rpa-note" style="font:inherit;border:0;border-radius:8px;padding:8px 14px;background:#1a7f5a;color:#fff;cursor:pointer">Copy remark</button> ')
    h.append(f'<pre id="rpa-case" style="display:none">{esc(case_text(rep))}</pre>')
    h.append('<div style="margin-top:12px;padding:10px 12px;background:#fff;border:1px solid #e1e4ea;border-radius:10px">'
             '<b>Final review by Claude</b><div style="font-size:13px;color:#5b6475;margin:2px 0 8px">Copies all findings and AI-read values (no Aadhaar or phone numbers). '
             'Paste into a Claude chat — attach the fard, tatima and photo for Claude to verify — and ask for the final call.</div>'
             '<button data-copy="rpa-case" style="font:inherit;border:0;border-radius:8px;padding:8px 14px;background:#12355b;color:#fff;cursor:pointer">Copy full case for Claude</button></div>')
    rd = getattr(rep, "reader", "AI")
    h.append(f'<p style="color:#5b6475;font-size:12px;margin-top:14px">Values marked “{rd} translation” or “read by {rd}” were read from handwritten/scanned documents by AI — confirm them against the originals. '
             'Shares are indicative and assume the khasra is in the predecessor\'s possession as recorded. Nothing is submitted to the portal.</p></div>')
    return "".join(h)
