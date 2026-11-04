# FARD CHECKER VERSION 1.6
"""Revenue Plus Tracker — hosted tracker + application analyser (Flask, for Render).

Environment variables (Render → Environment):
  ACCESS_KEY         a password of your choice; the tracker asks for it once per browser
  ANTHROPIC_API_KEY  OPTIONAL Claude API key (paid) to also read handwritten fard/tatima
  CLAUDE_MODEL       optional, default claude-opus-5-5
  GEMINI_API_KEY     OPTIONAL Google Gemini key (free tier available) — reads handwriting/tatima/photo when no Claude key
  GEMINI_MODEL       optional, default gemini-3.8-flash
  (Without ANTHROPIC_API_KEY the app runs in free mode: GPS overlay read by free OCR, handwriting not read.)
"""
import base64, gc, hmac, html, os, time

from flask import Flask, Response, jsonify, request, send_file

import engine
import version

APP_FILES = ["version.py", "app.py", "engine.py", "tracker.js", "statuspdf.py", "pluscode.py", "gunicorn.conf.py", "requirements.txt"]


def file_versions():
    """Version line found in each file of the app (to catch a file that was not uploaded)."""
    import re as _re
    out = {}
    for f in APP_FILES:
        try:
            with open(os.path.join(BASE, f), encoding="utf-8", errors="ignore") as fh:
                m = _re.search(r"FARD CHECKER VERSION ([\d.]+)", fh.read(4000))
            out[f] = m.group(1) if m else "no version (old file)"
        except FileNotFoundError:
            out[f] = "missing"
    return out

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
    body = f'window.__rpApiBase="{base}";window.__rpVersion="{version.VERSION}";\n' + code
    return Response(body, mimetype="application/javascript",
                    headers={"Cache-Control": "no-store", "Access-Control-Allow-Origin": "*"})


@app.get("/api/ping")
def ping():
    import sys, importlib.metadata as md
    vers = {}
    for p in ("shapely", "pyshp", "pandas", "numpy", "pymupdf", "rapidocr-onnxruntime"):
        try:
            vers[p] = md.version(p)
        except Exception:
            vers[p] = None
    reader = "claude" if os.environ.get("ANTHROPIC_API_KEY") else ("gemini" if os.environ.get("GEMINI_API_KEY") else "free-ocr")
    fv = file_versions()
    return jsonify(ok=True, version=version.VERSION, version_date=version.DATE, files_ok=all(v == version.VERSION for v in fv.values()), files=fv,
                   key_ok=ok_key(), ai=reader != "free-ocr", reader=reader,
                   gemini_model=os.environ.get("GEMINI_MODEL", "gemini-3.8-flash") if reader == "gemini" else None,
                   python=sys.version.split()[0], versions=vers)


@app.get("/api/test-reader")
def test_reader():
    """Checks that the configured document reader (Gemini / Claude) answers — tiny text-only request."""
    if not ok_key():
        return jsonify(error="Wrong or missing access key"), 401
    import requests
    t0 = time.time()
    try:
        if os.environ.get("ANTHROPIC_API_KEY"):
            model = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
            r = requests.post("https://api.anthropic.com/v1/messages", timeout=60,
                              headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"},
                              json={"model": model, "max_tokens": 10, "messages": [{"role": "user", "content": "Reply with just: OK"}]})
            ok = r.status_code == 200
            reply = "".join(b.get("text", "") for b in r.json().get("content", [])) if ok else r.text[:300]
            return jsonify(reader="Claude", model=model, ok=ok, status=r.status_code, reply=reply, secs=round(time.time() - t0, 1))
        if os.environ.get("GEMINI_API_KEY"):
            import requests as rq
            tried = []
            for model in engine.gemini_models():
                r = rq.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", timeout=60,
                            headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "content-type": "application/json"},
                            json={"contents": [{"role": "user", "parts": [{"text": "Reply with just: OK"}]}]})
                if r.status_code == 200:
                    engine._gemini_ok_model = model
                    tried.append({"model": model, "ok": True})
                    break
                tried.append({"model": model, "ok": False, "why": engine.gemini_error(r)})
                if r.status_code in (400, 401, 403):
                    break
            good = next((t for t in tried if t["ok"]), None)
            return jsonify(reader="Gemini", ok=bool(good), model=good["model"] if good else None, tried=tried,
                           status=200 if good else 429, secs=round(time.time() - t0, 1),
                           reply=("Working with " + good["model"]) if good else "No Gemini model answered — see details.")
        return jsonify(reader="Free OCR only", ok=True, reply="No GEMINI_API_KEY or ANTHROPIC_API_KEY set — handwriting is not read.")
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 200


@app.post("/api/status-pdf")
def status_pdf():
    """Pendency status PDF from the tracker's last scan (status fields only)."""
    if not ok_key():
        return jsonify(error="Wrong or missing access key"), 401
    import statuspdf
    data = request.get_json(force=True, silent=True) or {}
    pdf = statuspdf.build(data)
    return Response(pdf, mimetype="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=Pendency_Status.pdf", "Cache-Control": "no-store"})


@app.post("/api/merge-pdf")
def merge_pdf():
    """Join several documents (PDFs and images) into one PDF, with a bookmark per document. Nothing is stored."""
    if not ok_key():
        return jsonify(error="Wrong or missing access key"), 401
    import fitz
    data = request.get_json(force=True, silent=True) or {}
    files = data.get("files") or []
    if not files:
        return jsonify(error="No documents"), 400
    out, toc, skipped = fitz.open(), [], []
    for f in files:
        label = str(f.get("label") or "Document")[:120]
        try:
            raw = base64.b64decode(f.get("data") or "")
        except Exception:
            skipped.append(label)
            continue
        start = out.page_count
        try:
            if raw[:4] == b"%PDF":
                src = fitz.open(stream=raw, filetype="pdf")
                out.insert_pdf(src)
                src.close()
            else:
                img = fitz.open(stream=raw)                      # jpg / png / tif …
                pdfb = img.convert_to_pdf()
                img.close()
                src = fitz.open("pdf", pdfb)
                out.insert_pdf(src)
                src.close()
        except Exception:
            skipped.append(label)
            continue
        if out.page_count > start:
            toc.append([1, label, start + 1])
        del raw
    if not out.page_count:
        return jsonify(error="None of the documents could be read as PDF or image", skipped=skipped), 422
    try:
        out.set_toc(toc)
        out.set_metadata({"title": str(data.get("title") or "")[:200], "producer": "Fard Checker"})
    except Exception:
        pass
    pdf = out.tobytes(garbage=3, deflate=True)
    out.close()
    gc.collect()
    return Response(pdf, mimetype="application/pdf",
                    headers={"Cache-Control": "no-store", "X-Skipped": ", ".join(skipped)[:500],
                             "Access-Control-Expose-Headers": "X-Skipped"})


@app.get("/api/villages")
def villages():
    if not ok_key():
        return jsonify(error="Wrong or missing access key"), 401
    return jsonify(engine.village_status(request.args.get("check")))


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


import threading
_one_at_a_time = threading.Lock()   # free plan: never run two analyses together (memory)


@app.post("/api/analyse")
def analyse():
    if not ok_key():
        return jsonify(error="Wrong or missing access key"), 401
    if not _one_at_a_time.acquire(timeout=170):
        return jsonify(error="Analyser busy — try again in a minute"), 503
    try:
        return _analyse()
    finally:
        _one_at_a_time.release()


def _analyse():
    t0 = time.time()
    data = request.get_json(force=True, silent=True) or {}
    appd = data.get("app") or {}
    pages, skipped, seen = [], [], set()
    for d in data.pop("docs", None) or []:
        lab = d.get("label") or "Document"
        if not d.get("data"):
            skipped.append(f"{lab}: {d.get('error') or 'not fetched'}")
            continue
        try:
            pages += engine.doc_to_images(lab, d.get("type", ""), d.pop("data"), seen=seen)
        except Exception as e:
            skipped.append(f"{lab}: {e}")
    engine.trim_memory()
    f = appd.get("fields") or {}
    ctx = {"service": appd.get("service") or f.get("svcType") or "", "khasra": f.get("cKhasra") or appd.get("khasra") or "",
           "village": f.get("villageD") or appd.get("village") or "", "applicant": f.get("applicant") or appd.get("name") or "",
           "area": f.get("areaProposed") or appd.get("area") or ""}
    ai, ai_err = (None, None)
    t1 = time.time()
    used = "Free OCR (GPS stamp only — handwriting not read)"
    if os.environ.get("ANTHROPIC_API_KEY") and data.get("read_docs", True):
        ai, ai_err = engine.read_documents(pages, ctx)
        used = "Claude (" + os.environ.get("CLAUDE_MODEL", "claude-opus-5-5") + ")"
        ai = engine.merge_ocr(ai, engine.free_read(pages)) if ai else engine.free_read(pages)
    elif os.environ.get("GEMINI_API_KEY") and data.get("read_docs", True):
        ocr = engine.free_read(pages)
        ai, ai_err = engine.read_documents_gemini(pages, ctx)
        used = "Gemini (" + ((ai or {}).get("model") or engine.gemini_models()[0]) + ")"
        ai = engine.merge_ocr(ai, ocr) if ai else ocr
    else:
        ai = engine.free_read(pages)
    reader_status = {"used": used, "ok": ai_err is None, "error": ai_err, "pages": len(pages), "secs": round(time.time() - t1),
                     "read": [k for k in ("fard", "tatima", "mutations") if (ai or {}).get(k) and (not isinstance(ai.get(k), dict) or ai[k].get("found"))]
                             + (["GPS stamp"] if ((ai or {}).get("photo") or {}).get("lat") else [])}
    rep = engine.analyse(appd, ai, ai_err)
    rep.reader_status = reader_status
    try:
        rep.tatima = engine.pick_tatima_page(pages)
    except Exception:
        rep.tatima = None
    try:
        rep.overlay = engine.sketch_overlay(rep)
    except Exception:
        rep.overlay = None
    try:
        s4 = next((s_ for s_ in rep.sections if s_["title"].startswith("Shaded portion")), None)
        if s4 is not None and rep.tatima and not rep.tatima.get("patwari", True):
            engine.add(s4, "amber", "No tatima uploaded by the Patwari was found — only the applicant's rough sketch, which is shown beside the map.",
                       "Patwari to upload the tatima showing the shaded portion of the khasra.", rep)
        tk = str(((ai or {}).get("tatima") or {}).get("sketch_kind") or "").lower()
        if s4 is not None and rep.tatima and rep.tatima.get("patwari", True) and tk.startswith("loc"):
            engine.add(s4, "amber", "The Patwari's tatima is only a location / route sketch — it does not draw the khasra or mark the shaded portion.",
                       "Patwari to upload a tatima (aks shajra) of the khasra with the shaded portion and dimensions.", rep)
    except Exception:
        pass
    if skipped:
        engine.add(rep.sections[0], "amber", "Some documents could not be opened: " + "; ".join(skipped))
    engine.add(rep.sections[0], "info", f"{len(pages)} distinct document page(s) read in {time.time() - t0:.0f} s.")
    out = jsonify(html=engine.render(rep), ai=ai)
    engine.trim_memory()
    return out


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
<h1>Revenue Plus Tracker <span style="font-size:14px;background:#12355b;color:#fff;border-radius:12px;padding:3px 10px;vertical-align:middle">v{ver}</span></h1>{verbox}<p class="m">Read-only tracker and application analyser for the JK Revenue Plus portal. The bookmark below always loads the latest version from this server — update <code>tracker.js</code> or <code>engine.py</code> on GitHub and Render redeploys; the bookmark itself never changes.</p>
<div class="c"><h2>1 · Install the bookmark (once per browser)</h2>
<p><b>Desktop:</b> drag this button to your bookmarks bar: <a class="bm" href="{bm}">RP Tracker</a></p>
<p><b>Phone (Chrome):</b> bookmark any page, edit the bookmark, and replace its URL with the text below. Name it <b>RP Tracker</b>; on the portal type “RP Tracker” in the address bar and tap the bookmark.</p>
<textarea readonly id="bmt">{bm_text}</textarea><button onclick="navigator.clipboard.writeText(document.getElementById('bmt').value);this.textContent='Copied ✓'">Copy bookmark code</button>
<p class="m">First tap after a while may take ~30–50 s while Render wakes up.</p></div>
<div class="c"><h2>2 · Use</h2><p>Log in to Revenue Plus → Dashboard → choose service type → View → tap <b>RP Tracker</b> → scan. Open an application row and tap <b>Analyse with village records</b>. The first time it asks for the access key (set as ACCESS_KEY on Render).</p></div>
<div class="c"><h2>Document reader (AI)</h2><p class="m">Shows which AI reads handwritten fards / tatimas and whether it answers right now.</p>
<p><input id="k2" placeholder="Access key" type="password"> <button onclick="testReader()">Test document reader</button></p><div id="tr"></div>
<script>async function testReader(){{var o=document.getElementById('tr');o.textContent='Testing…';try{{var r=await fetch('/api/test-reader?key='+encodeURIComponent(document.getElementById('k2').value));var d=await r.json();
if(!r.ok){{o.innerHTML='<span style="color:#b42318">'+(d.error||r.status)+'</span>';return}}
o.innerHTML=(d.ok?'<b style="color:#145c36">✓ Working</b>':'<b style="color:#b42318">✗ Not working</b>')+' — '+(d.reader||'')+(d.model?' ('+d.model+')':'')+(d.secs!=null?' · '+d.secs+' s':'')+'<div class=m>'+String(d.reply||d.error||'').replace(/[<>&]/g,'')+'</div>'+
(d.tried?'<div class=m>'+d.tried.map(function(t){{return (t.ok?'✓ ':'✗ ')+t.model+(t.why?' — '+String(t.why).replace(/[<>&]/g,''):'')}}).join('<br>')+'</div>':'')+(d.tried&&!d.ok&&d.tried.every(function(t){{return /limit 0/.test(t.why||'')}})?'<div class=m><b>All free limits show 0</b> — this key\'s Google project has no free quota. Create the key in a <b>new project</b> at aistudio.google.com (Get API key → Create API key in new project), or enable billing on the project.</div>':'')+(d.status==404?'<div class=m>Model name not found — set GEMINI_MODEL on Render to a current model.</div>':'')+(d.status==400||d.status==403?'<div class=m>Check the API key value on Render.</div>':'')}}catch(e){{o.textContent='Error: '+e}}}}</script></div>
<div class="c"><h2>3 · Village data</h2><p class="m">One folder per village in GitHub: <code>villages/&lt;Village name&gt;/</code> with the Jamabandi .xlsx and the shapefile (.shp .shx .dbf .prj). To add a village, open the <code>villages</code> folder on GitHub → Add file → Upload files → drag the whole village folder. Optional <code>aliases.txt</code> (one spelling per line) if the portal spells the village differently. A tehsil-wide shapefile with a Village column can go in <code>villages/_maps/</code> instead of a shapefile per village.</p>
<p><input id="k" placeholder="Access key" type="password"> <button onclick="load()">Show villages</button> <button onclick="all_()" style="background:#12355b">Check all</button></p><div id="vs"></div></div>
<script>
var done={{}};function esc(s){{return String(s==null?'':s).replace(/[&<>"]/g,function(c){{return{{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
async function all_(){{await load();var names=Array.from(document.querySelectorAll('button[data-v]')).map(function(b){{return b.dataset.v}});for(var i=0;i<names.length;i++){{await load(names[i])}}}}
async function load(chk){{var k=document.getElementById('k').value;var r=await fetch('/api/villages?key='+encodeURIComponent(k)+(chk?'&check='+encodeURIComponent(chk):''));var d=await r.json();
if(!r.ok){{document.getElementById('vs').textContent=d.error;return}}
var h='<p class=m>'+d.villages.length+' village folders'+(d.shared_maps.length?' · shared maps: '+esc(d.shared_maps.join(', ')):'')+'</p>';
if(Object.keys(d.clashes).length)h+='<p style="color:#b42318">Name clash (same spelling in two folders): '+esc(JSON.stringify(d.clashes))+'</p>';
d.villages.forEach(function(v){{if(v.checked)done[v.village]=v}});d.villages=d.villages.map(function(v){{return done[v.village]||v}});
h+='<table><tr><th>Village folder</th><th>Jamabandi</th><th>Shapefile</th><th>Check</th></tr>'+d.villages.map(function(v){{
var c=v.checked?('<b>'+v.khasras_jamabandi+'</b> khasras · <b>'+v.parcels_map+'</b> parcels'+(v.errors.length?'<div style="color:#b42318">'+esc(v.errors.join('; '))+'</div>':'<div style="color:#145c36">OK</div>')+((v.notes||[]).length?'<div class=m>'+esc(v.notes.join('; '))+'</div>':'')+(v.map_source?'<div class=m>Map: '+esc(v.map_source)+'</div>':'')+(v.on_map_not_in_jb.length?'<div class=m>On map, not in Jamabandi: '+esc(v.on_map_not_in_jb.join(', '))+'</div>':'')):'<button data-v="'+esc(v.village)+'">Check</button>';
return '<tr><td>'+esc(v.village)+'<div class=m>matches: '+esc(v.aliases.join(', '))+'</div></td><td class=m>'+esc(v.jamabandi||'— missing')+'</td><td class=m>'+esc(v.shapefile||'— missing')+'</td><td>'+c+'</td></tr>'}}).join('')+'</table>';
var el=document.getElementById('vs');el.innerHTML=h;el.querySelectorAll('button[data-v]').forEach(function(b){{b.onclick=function(){{b.textContent='Checking…';load(b.dataset.v)}}}})}}
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
    fv = file_versions()
    bad = {f: v for f, v in fv.items() if v != version.VERSION}
    rows = "".join(f'<tr><td><code>{html.escape(f)}</code></td><td>{"✓ v" + v if v == version.VERSION else "<b style=color:#b42318>" + html.escape(v if v in ("missing", "no version (old file)") else "v" + v) + "</b>"}</td></tr>'
                   for f, v in fv.items())
    verbox = ('<div class="c" style="border:2px solid ' + ("#b42318" if bad else "#1a7f5a") + '"><b>'
              + (f"⚠ {len(bad)} file(s) not on v{version.VERSION} — upload the complete set of files again" if bad
                 else f"✓ All files are on version {version.VERSION} ({version.DATE})") + "</b>"
              + '<details style="margin-top:6px"' + (" open" if bad else "") + '><summary class="m" style="cursor:pointer">Files and what changed</summary>'
              + '<table style="margin:6px 0">' + rows + "</table>"
              + "".join(f'<p class="m" style="margin:4px 0"><b>v{html.escape(v)}</b> · {html.escape(d)} — {html.escape(t)}</p>' for v, d, t in version.CHANGES[:5])
              + "</details></div>")
    return LANDING.format(bm=html.escape(js), bm_text=html.escape(js), ver=version.VERSION, verbox=verbox)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
