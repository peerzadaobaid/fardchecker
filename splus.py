# SERVICE PLUS TRACKER VERSION 1.8
"""Service Plus (JanSugam) Tracker — server part, added to the Fard Checker app on Render.

What it adds (nothing else in the app changes):
  /splus            page with the bookmark for the Service Plus Tracker
  /splus.js         the tracker code the bookmark loads
  /splus/bridge     small helper window: the JanSugam portal blocks the page from talking to Render
                    (Content Security Policy), so the bookmark opens this window and talks to it by messages
  /api/splus/scan   GET / POST  last scan of the Inbox (per login) in the private data repo
  /api/splus/pdf    GET / POST  report PDFs fetched from the portal, kept in the private data repo

Uses the same ACCESS_KEY, DATA_REPO and GITHUB_TOKEN as the Revenue Plus tracker.
Files written in the data repo:
  splus/last-scan-<login>.json          applications with me, their reports, revert comments, and the "done" record
  splus/pdf/<application>/<name>.pdf    Patwari report PDFs and other attachments
Phone / Aadhaar numbers are removed from the scan before it is saved (same as Revenue Plus).
"""
import base64
import json
import os
import re
import threading
import time

import requests
from flask import Response, jsonify, request

VERSION = "1.8"
ORIGINS = ("https://jansugam.jk.gov.in",)
_lock = threading.Lock()


def _safe(s, n=80):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(s or ""))[:n].strip("_") or "x"


def register(app, ok_key):
    import sync

    def base_url():
        b = request.host_url.rstrip("/")
        if request.headers.get("X-Forwarded-Proto") == "https":
            b = b.replace("http://", "https://")
        return b

    @app.after_request
    def splus_cors(resp):
        origin = request.headers.get("Origin", "")
        if origin in ORIGINS and request.path.startswith("/api/"):
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Access-Key"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return resp

    @app.get("/splus.js")
    def splus_js():
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "splus.js"), encoding="utf-8") as fh:
            code = fh.read()
        body = f'window.__spApiBase="{base_url()}";\n' + code
        return Response(body, mimetype="application/javascript",
                        headers={"Cache-Control": "no-store", "Access-Control-Allow-Origin": "*"})

    def need():
        if not ok_key():
            return jsonify(error="Wrong or missing access key"), 401
        if not sync.configured():
            return jsonify(error="Scan sync is not set up (DATA_REPO / GITHUB_TOKEN)"), 503
        return None

    @app.post("/api/splus/scan")
    def splus_save_scan():
        bad = need()
        if bad:
            return bad
        d = request.get_json(force=True, silent=True) or {}
        login = sync.login_slug(d.get("login"))
        scan = sync.scrub(d.get("scan") or {})
        path = f"splus/last-scan-{login}.json"
        try:
            with _lock:
                for attempt in range(3):
                    try:
                        _, sha = sync.get(path)
                        sync.put(path, scan, sha, f"service plus scan ({login}): {len(scan.get('items') or [])} applications")
                        break
                    except sync.ConflictError:
                        time.sleep(1 + attempt)
            return jsonify(ok=True, at=int(time.time() * 1000))
        except Exception as e:
            return jsonify(error=str(e)[:300]), 502

    @app.get("/api/splus/scan")
    def splus_load_scan():
        bad = need()
        if bad:
            return bad
        try:
            obj, _ = sync.get(f"splus/last-scan-{sync.login_slug(request.args.get('login'))}.json")
            return jsonify(scan=obj)
        except Exception as e:
            return jsonify(error=str(e)[:300]), 502

    def pdf_path(app_no, name, ext="pdf"):
        ext = ext if ext in ("pdf", "jpg", "png") else "pdf"
        return f"splus/pdf/{_safe(app_no)}/{_safe(name, 60)}.{ext}"

    def meta(path):
        r = requests.get(sync._url(path), headers=sync._h(), timeout=30)
        if r.status_code == 404:
            return None
        if r.status_code != 200:
            raise RuntimeError(sync._why(r))
        j = r.json()
        return {"sha": j.get("sha"), "size": j.get("size")}

    @app.post("/api/splus/pdf")
    def splus_save_pdf():
        bad = need()
        if bad:
            return bad
        d = request.get_json(force=True, silent=True) or {}
        b64 = d.get("b64") or ""
        try:
            raw = base64.b64decode(b64)
        except Exception:
            return jsonify(error="file data could not be read"), 400
        if not raw:
            return jsonify(error="empty file"), 400
        path = pdf_path(d.get("app"), d.get("name"), d.get("ext") or "pdf")
        try:
            with _lock:
                m = meta(path)
                if m and m.get("size") == len(raw):
                    return jsonify(ok=True, path=path, same=True)
                body = {"message": f"service plus pdf {d.get('app')} {d.get('name')}", "content": base64.b64encode(raw).decode()}
                if m:
                    body["sha"] = m["sha"]
                r = requests.put(sync._url(path), headers=sync._h(), json=body, timeout=120)
                if r.status_code not in (200, 201):
                    raise RuntimeError(sync._why(r))
            return jsonify(ok=True, path=path, size=len(raw))
        except Exception as e:
            return jsonify(error=str(e)[:300]), 502

    @app.get("/api/splus/pdf")
    def splus_load_pdf():
        if not ok_key():
            return Response("Wrong or missing access key", status=401)
        path = request.args.get("path") or ""
        if not re.fullmatch(r"splus/pdf/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+\.(pdf|jpg|png)", path):
            return Response("Bad file name", status=400)
        mime = {"pdf": "application/pdf", "jpg": "image/jpeg", "png": "image/png"}[path.rsplit(".", 1)[-1]]
        try:
            r = requests.get(sync._url(path), headers=sync._h(raw=True), timeout=120)
            if r.status_code == 404:
                return Response("This PDF is not in the data repo (yet).", status=404)
            if r.status_code != 200:
                return Response(sync._why(r), status=502)
            return Response(r.content, mimetype=mime,
                            headers={"Content-Disposition": f'inline; filename="{path.rsplit("/", 2)[-2]}-{path.rsplit("/", 1)[-1]}"',
                                     "Cache-Control": "private, max-age=3600"})
        except Exception as e:
            return Response(str(e)[:300], status=502)

    def code_text():
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "splus.js"), encoding="utf-8") as fh:
            return fh.read()

    def loader_js(base):
        # small bookmark: opens the helper window, gets the latest tracker code from it, runs it on the portal page
        return ("javascript:(function(){if(window.__spTracker){window.__spTracker.open();return}"
                "var B='" + base + "',d=document,n=d.createElement('div');"
                "n.textContent='Opening the helper window… (first time after a while: up to a minute while Render wakes up)';"
                "n.style.cssText='position:fixed;top:10px;left:10px;z-index:2147483647;background:%23123d2b;color:%23fff;padding:10px 14px;border-radius:8px;font:14px sans-serif;max-width:420px';"
                "d.body.appendChild(n);var w=window.open(B+'/splus/bridge','spBridge','width=440,height=320');"
                "if(!w){n.textContent='Pop-up blocked. Allow pop-ups for jansugam.jk.gov.in (icon at the right of the address bar) and tap SP Tracker again.';return}"
                "window.__spBridge=w;var done=0;function onm(e){if(e.origin!==B)return;var m=e.data||{};"
                "if(m.sp==='ready'&&!done){w.postMessage({sp:'code'},B)}"
                "else if(m.sp==='code'&&!done){done=1;window.removeEventListener('message',onm);n.remove();window.__spApiBase=B;"
                "var s=d.createElement('script');s.textContent=m.code;d.documentElement.appendChild(s);s.remove();"
                "if(!window.__spTracker){try{(new Function(m.code))()}catch(x){alert('The portal does not allow the tracker to start this way. Use the SP Tracker (full) bookmark from '+B+'/splus')}}}}"
                "window.addEventListener('message',onm);"
                "setTimeout(function(){if(!done)n.textContent='No answer from the helper window yet. If it stays like this, use the SP Tracker (full) bookmark from '+B+'/splus'},60000)})()")

    def full_js(base):
        # whole tracker inside the bookmark (when the portal does not let the small bookmark start it)
        from urllib.parse import quote
        lines = []
        for ln in code_text().splitlines():
            t = ln.strip()
            if not t or t.startswith("//"):
                continue
            lines.append(t)
        code = f'window.__spApiBase="{base}";\n' + "\n".join(lines)
        return "javascript:(function(){" + quote(code, safe=" !\"$&'()*+,-./:;<=>?@[\\]^_`{|}~=") + "%0A})()"

    @app.get("/splus/bridge")
    def splus_bridge():
        page = r"""<!doctype html><html><head><meta charset=utf-8><title>SP Tracker — helper window</title>
<style>body{font:14px/1.45 system-ui,Segoe UI,sans-serif;margin:0;background:#123d2b;color:#fff;padding:16px}b{font-size:16px}p{margin:8px 0}.m{opacity:.8;font-size:12.5px}#st{background:#ffffff1f;border-radius:8px;padding:8px 10px}</style></head>
<body><b>Service Plus Tracker — helper window</b><p>Keep this small window open (you can minimise it) while the tracker scans. It saves the scans and the Patwari PDFs to your private data repo.</p>
<p id=st>Waiting for the tracker…</p><p class=m>The JanSugam portal does not let its page talk to other websites, so the tracker sends everything through this window.</p>
<script>
var OK=__ORIGINS__,n=0,st=document.getElementById('st');
function allowed(o){return OK.indexOf(o)>=0||/^http:\/\/localhost(:\d+)?$/.test(o)}
function say(t){st.textContent=t}
window.addEventListener('message',async function(e){
  if(!allowed(e.origin))return;var m=e.data||{};
  if(m.sp==='code'){var r=await fetch('/splus.js?t='+Date.now(),{cache:'no-store'});var c=await r.text();e.source.postMessage({sp:'code',code:c},e.origin);say('Tracker started on the portal page.');return}
  if(m.sp==='api'){var out={sp:'res',id:m.id};
    try{var h={'X-Access-Key':m.key||''};if(m.body)h['Content-Type']='application/json';
      var r2=await fetch(m.path,{method:m.method||'GET',headers:h,body:m.body?JSON.stringify(m.body):undefined,cache:'no-store'});
      out.status=r2.status;try{out.json=await r2.json()}catch(x){out.json={}}
      n++;say((r2.ok?'✓ ':'✗ ')+(/pdf/.test(m.path)?'PDF':/scan/.test(m.path)?'Scan':'Request')+' '+(r2.ok?'saved / loaded':'failed ('+r2.status+')')+' · '+new Date().toLocaleTimeString()+' · '+n+' so far')
    }catch(x){out.error=String(x&&x.message||x);say('✗ '+out.error)}
    e.source.postMessage(out,e.origin)}
});
if(window.opener){try{window.opener.postMessage({sp:'ready'},'*')}catch(x){}}else say('Open this window from the SP Tracker bookmark on the portal.');
</script></body></html>"""
        return Response(page.replace("__ORIGINS__", json.dumps(list(ORIGINS))), mimetype="text/html", headers={"Cache-Control": "no-store"})

    @app.get("/splus")
    def splus_page():
        base = base_url()
        import html as _h
        js, full = loader_js(base), full_js(base)
        sync_ok = "yes" if sync.configured() else "NO — set DATA_REPO and GITHUB_TOKEN on Render"
        page = f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Service Plus Tracker</title><style>body{{font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:#eef3f0;color:#17241d;margin:0}}
.w{{max-width:760px;margin:0 auto;padding:18px}}.c{{background:#fff;border:1px solid #dce5df;border-radius:12px;padding:16px;margin-bottom:12px}}
h1{{font-size:22px;margin:0 0 4px;color:#123d2b}}a.bm{{display:inline-block;background:#123d2b;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:700}}
textarea{{width:100%;height:80px;font:12px monospace}}.m{{color:#5b6b62;font-size:13px}}ol li{{margin-bottom:6px}}button{{font:inherit;border:0;border-radius:8px;padding:8px 12px;background:#1f6b4a;color:#fff;cursor:pointer}}</style></head><body><div class=w>
<div class=c><h1>Service Plus Tracker</h1><div class=m>Version {VERSION} · read-only — it never clicks Pull, Forward, Submit, Save Draft or Return to Pool · online saving: {sync_ok}</div></div>
<div class=c><b>1 · Bookmark (use this one)</b><p>Computer: drag this button to the bookmarks bar → <a class=bm href="{_h.escape(js)}">SP Tracker</a></p>
<p class=m>Phone / other browser: make a bookmark named <b>SP Tracker</b> and paste this as its address (URL):</p>
<textarea readonly id=t1 onclick="this.select()">{_h.escape(js)}</textarea><button onclick="navigator.clipboard.writeText(document.getElementById('t1').value);this.textContent='Copied ✓'">Copy</button>
<p class=m>When you tap it on the portal, a <b>small helper window</b> opens on this site. Keep it open while scanning — the portal does not let its own page talk to Render, so scans and PDFs are saved through that window. If the browser blocks the pop-up, allow pop-ups for jansugam.jk.gov.in once.</p></div>
<div class=c><b>2 · Backup bookmark — only if the one above does not start</b><p>The whole tracker is inside this bookmark: <a class=bm href="{_h.escape(full)}" style="background:#5b6b62">SP Tracker (full)</a></p>
<p class=m>It always starts, but it does not update itself — drag it again from this page after each new version. It still uses the helper window for saving (opened when you tap Scan Inbox).</p>
<textarea readonly id=t2 onclick="this.select()">{_h.escape(full)}</textarea><button onclick="navigator.clipboard.writeText(document.getElementById('t2').value);this.textContent='Copied ✓'">Copy</button></div>
<div class=c><b>Use</b><ol><li>Log in to <a href="https://jansugam.jk.gov.in/">jansugam.jk.gov.in</a> as Naib Tehsildar (the Dashboard is fine).</li>
<li>Tap <b>SP Tracker</b>. The first time it asks for the access key (the same ACCESS_KEY as the Revenue Plus tracker).</li>
<li>Tap <b>Scan Inbox</b>. It goes through every service and task in Message Box → Inbox, reads each application's processing history, the Patwari and Girdawar reports and any Tehsildar revert comment, and keeps the Patwari's PDF.</li>
<li>Applications are read in sets of 10. If the login ends, log in again, open the tracker and tap <b>Resume</b>.</li></ol></div>
</div></body></html>"""
        return Response(page, mimetype="text/html")
