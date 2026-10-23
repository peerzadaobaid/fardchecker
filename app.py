"""Revenue Plus Tracker — hosted tracker + application analyser (Flask, for Render).

Environment variables (Render → Environment):
  ACCESS_KEY         a password of your choice; the tracker asks for it once per browser
  ANTHROPIC_API_KEY  OPTIONAL Claude API key (paid) to also read handwritten fard/tatima
  CLAUDE_MODEL       optional, default claude-opus-5-5
  (Without ANTHROPIC_API_KEY the app runs in free mode: GPS overlay read by free OCR, handwriting not read.)
"""
import hmac, html, os, time

from flask import Flask, Response, jsonify, request, send_file

import engine

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024
BASE = os.path.dirname(os.path.abspath(__file__))
ALLOWED = os.environ.get("ALLOWED_ORIGINS", "https://jkrevenue.nic.in").split(",")


def ok_key():
    want = os.environ.get("ACCESS_KEY", "")
    got = request.headers.get("X-Access-Key") or request.args.get("key") or ""
    return bool(want) and hmac.compare_digest(want, got)


@app.after_request
def cors(resp):
    origin = request.headers.get("Origin", "")
    if origin and (origin in ALLOWED or "*" in ALLOWED or origin.startswith("http://localhost")):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Access-Key"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@app.route("/api/<path:_any>", methods=["OPTIONS"])
def preflight(_any):
    return Response(status=204)


@app.get("/tracker.js")
def tracker_js():
    base = request.host_url.rstrip("/")
    if request.headers.get("X-Forwarded-Proto") == "https":
        base = base.replace("http://", "https://")
    with open(os.path.join(BASE, "tracker.js"), encoding="utf-8") as fh:
        code = fh.read()
    body = f'window.__rpApiBase="{base}";\n' + code
    return Response(body, mimetype="application/javascript",
                    headers={"Cache-Control": "no-store", "Access-Control-Allow-Origin": "*"})


@app.get("/api/ping")
def ping():
    return jsonify(ok=True, key_ok=ok_key(), ai=bool(os.environ.get("ANTHROPIC_API_KEY")))


@app.get("/api/villages")
def villages():
    if not ok_key():
        return jsonify(error="Wrong or missing access key"), 401
    return jsonify(engine.village_status())


@app.get("/api/khasra")
def khasra():
    if not ok_key():
        return jsonify(error="Wrong or missing access key"), 401
    v = engine.load_village(request.args.get("village", ""))
    k = request.args.get("khasra", "")
    if not v:
        return jsonify(error="village not found"), 404
    info = engine.jb_info(v, k) or []
    p = engine.parcel_for(v, k)
    nb = engine.neighbours(v, p) if p else []
    return jsonify(village=v["name"], jamabandi=info,
                   map_area_m2=round(p["m"].area, 1) if p else None,
                   neighbours=[{k2: n[k2] for k2 in ("dir", "khasra", "type")} for n in nb])


@app.post("/api/analyse")
def analyse():
    if not ok_key():
        return jsonify(error="Wrong or missing access key"), 401
    t0 = time.time()
    data = request.get_json(force=True, silent=True) or {}
    appd = data.get("app") or {}
    pages, skipped = [], []
    for d in data.get("docs") or []:
        lab = d.get("label") or "Document"
        if not d.get("data"):
            skipped.append(f"{lab}: {d.get('error') or 'not fetched'}")
            continue
        try:
            for pg in engine.doc_to_images(lab, d.get("type", ""), d["data"]):
                if pg["hash"] not in {p["hash"] for p in pages}:
                    pages.append(pg)
        except Exception as e:
            skipped.append(f"{lab}: {e}")
    f = appd.get("fields") or {}
    ctx = {"service": appd.get("service") or f.get("svcType") or "", "khasra": f.get("cKhasra") or appd.get("khasra") or "",
           "village": f.get("villageD") or appd.get("village") or "", "applicant": f.get("applicant") or appd.get("name") or "",
           "area": f.get("areaProposed") or appd.get("area") or ""}
    ai, ai_err = (None, None)
    if os.environ.get("ANTHROPIC_API_KEY") and data.get("read_docs", True):
        ai, ai_err = engine.read_documents(pages, ctx)
    else:
        ai = engine.free_read(pages)
    rep = engine.analyse(appd, ai, ai_err)
    if skipped:
        engine.add(rep.sections[0], "amber", "Some documents could not be opened: " + "; ".join(skipped))
    engine.add(rep.sections[0], "info", f"{len(pages)} distinct document page(s) read in {time.time() - t0:.0f} s.")
    return jsonify(html=engine.render(rep), ai=ai)


LANDING = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revenue Plus Tracker</title><style>
body{{margin:0;background:#f4f5f7;color:#1d2330;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
.w{{max-width:820px;margin:0 auto;padding:16px}}.c{{background:#fff;border:1px solid #e1e4ea;border-radius:12px;padding:16px;margin:12px 0}}
h1{{font-size:20px;margin:6px 0}}h2{{font-size:16px;margin:0 0 8px}}a.bm{{display:inline-block;background:#12355b;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600}}
textarea{{width:100%;box-sizing:border-box;height:90px;font:12px monospace;border:1px solid #c9ced8;border-radius:8px;padding:8px}}
button{{font:inherit;border:0;border-radius:8px;padding:9px 14px;background:#1a7f5a;color:#fff;cursor:pointer}}
table{{width:100%;border-collapse:collapse;font-size:14px}}td,th{{text-align:left;padding:6px;border-bottom:1px solid #eceef2}}.m{{color:#5b6475;font-size:13px}}
input{{font:inherit;padding:8px;border:1px solid #c9ced8;border-radius:8px}}
</style></head><body><div class="w">
<h1>Revenue Plus Tracker</h1><p class="m">Read-only tracker and application analyser for the JK Revenue Plus portal. The bookmark below always loads the latest version from this server — update <code>tracker.js</code> or <code>engine.py</code> on GitHub and Render redeploys; the bookmark itself never changes.</p>
<div class="c"><h2>1 · Install the bookmark (once per browser)</h2>
<p><b>Desktop:</b> drag this button to your bookmarks bar: <a class="bm" href="{bm}">RP Tracker</a></p>
<p><b>Phone (Chrome):</b> bookmark any page, edit the bookmark, and replace its URL with the text below. Name it <b>RP Tracker</b>; on the portal type “RP Tracker” in the address bar and tap the bookmark.</p>
<textarea readonly id="bmt">{bm_text}</textarea><button onclick="navigator.clipboard.writeText(document.getElementById('bmt').value);this.textContent='Copied ✓'">Copy bookmark code</button>
<p class="m">First tap after a while may take ~30–50 s while Render wakes up.</p></div>
<div class="c"><h2>2 · Use</h2><p>Log in to Revenue Plus → Dashboard → choose service type → View → tap <b>RP Tracker</b> → scan. Open an application row and tap <b>Analyse with village records</b>. The first time it asks for the access key (set as ACCESS_KEY on Render).</p></div>
<div class="c"><h2>3 · Village data</h2><p class="m">In GitHub, folder <code>villages/&lt;Village name&gt;/</code> with the Jamabandi .xlsx and the shapefile (.shp .shx .dbf .prj). Folder name should match the village name on the portal.</p>
<p><input id="k" placeholder="Access key" type="password"> <button onclick="load()">Show loaded villages</button></p><div id="vs"></div></div>
<script>
async function load(){{var k=document.getElementById('k').value;var r=await fetch('/api/villages?key='+encodeURIComponent(k));var d=await r.json();
if(!r.ok){{document.getElementById('vs').textContent=d.error;return}}
document.getElementById('vs').innerHTML='<table><tr><th>Village</th><th>Khasras (Jamabandi)</th><th>Parcels (map)</th><th>Problems</th></tr>'+d.map(function(v){{return '<tr><td>'+v.village+'</td><td>'+v.khasras_jamabandi+'</td><td>'+v.parcels_map+'</td><td class=m>'+(v.errors.join('; ')||'—')+'</td></tr>'}}).join('')+'</table>'}}
</script></div></body></html>"""


@app.get("/")
def landing():
    base = request.host_url.rstrip("/")
    if request.headers.get("X-Forwarded-Proto") == "https":
        base = base.replace("http://", "https://")
    js = ("javascript:(function(){if(window.__rpTracker){window.__rpTracker.open();return}"
          "var u='" + base + "/tracker.js?t='+Date.now(),d=document,n=d.createElement('div');"
          "n.textContent='Loading RP Tracker…';n.style.cssText='position:fixed;top:10px;left:10px;z-index:2147483647;background:%2312355b;color:%23fff;padding:10px 14px;border-radius:8px;font:14px sans-serif';"
          "d.body.appendChild(n);var s=d.createElement('script');s.src=u;s.onload=function(){n.remove()};"
          "s.onerror=function(){fetch(u).then(function(r){return r.text()}).then(function(c){n.remove();(new Function(c))()})"
          ".catch(function(){n.textContent='Could not load RP Tracker. Render may be waking up — try again in 30 s.';setTimeout(function(){n.remove()},6000)})};"
          "d.body.appendChild(s)})()")
    return LANDING.format(bm=html.escape(js), bm_text=html.escape(js))


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
