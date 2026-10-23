"""Minimal Open Location Code (Plus Code) decoder — enough to check a GPS-camera overlay.
A short code like '6MG2+X6H' is recovered against a nearby reference point (the village)."""
ALPH = "23456789CFGHJMPQRVWX"
RES = [20.0, 1.0, 0.05, 0.0025, 0.000125]


def _encode_prefix(lat, lng, n_pairs):
    lat = min(max(lat + 90, 0), 179.999999)
    lng = (lng + 180) % 360
    out = ""
    for i in range(n_pairs):
        r = RES[i]
        a, b = int(lat // r), int(lng // r)
        out += ALPH[a] + ALPH[b]
        lat -= a * r
        lng -= b * r
    return out


def decode(code):
    """Full code -> (lat_centre, lng_centre, cell_height_deg)."""
    c = code.upper().replace("+", "").rstrip("0")
    lat = lng = 0.0
    pairs, extra = c[:10], c[10:]
    for i in range(0, len(pairs), 2):
        r = RES[i // 2]
        lat += ALPH.index(pairs[i]) * r
        lng += ALPH.index(pairs[i + 1]) * r
    h = w = RES[len(pairs) // 2 - 1]
    for ch in extra[:5]:
        h, w = h / 5, w / 4
        k = ALPH.index(ch)
        lat += (k // 4) * h
        lng += (k % 4) * w
    return lat - 90 + h / 2, lng - 180 + w / 2, h


def recover(short, ref_lat, ref_lng):
    """Short code (e.g. '6MG2+X6H') + reference point -> full code centre (lat, lng, cell_deg)."""
    s = short.upper().strip()
    if "+" not in s:
        return None
    sep = s.index("+")
    missing = 8 - sep
    if missing <= 0:
        return decode(s)
    full = _encode_prefix(ref_lat, ref_lng, 4)[:missing] + s
    lat, lng, h = decode(full)
    span = RES[missing // 2 - 1] if missing >= 2 else 20.0
    # pick the nearest candidate to the reference
    if lat - ref_lat > span / 2:
        lat -= span
    elif ref_lat - lat > span / 2:
        lat += span
    if lng - ref_lng > span / 2:
        lng -= span
    elif ref_lng - lng > span / 2:
        lng += span
    return lat, lng, h
