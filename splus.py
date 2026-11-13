# SERVICE PLUS TRACKER VERSION 1.0
"""Service Plus (JanSugam) Tracker — server part, added to the Fard Checker app on Render.

What it adds (nothing else in the app changes):
  /splus            page with the bookmark for the Service Plus Tracker
  /splus.js         the tracker code the bookmark loads
  /api/splus/scan   GET / POST  last scan of the Inbox (per login) in the private data repo
  /api/splus/pdf    GET / POST  report PDFs fetched from the portal, kept in the private data repo

Uses the same ACCESS_KEY, DATA_REPO and GITHUB_TOKEN as the Revenue Plus tracker.
Files written in the data repo:
  splus/last-scan-<login>.json          applications with me, their reports, revert comments, and the "done" record
  splus/pdf/<application>/<name>.pdf    Patwari report PDFs and other attachments
Phone / Aadhaar numbers are removed from the scan before it is saved (same as Revenue Plus).
"""
import base64
import os
import re
import threading
import time

import requests
from flask import Response, jsonify, request

VERSION = "1.0"
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

    @app.get("/splus")
    def splus_page():
        base = base_url()
        js = ("javascript:(function(){if(window.__spTracker){window.__spTracker.open();return}"
              "var u='" + base + "/splus.js?t='+Date.now(),d=document,n=d.createElement('div');"
              "n.textContent='Loading Service Plus Tracker…';n.style.cssText='position:fixed;top:10px;left:10px;z-index:2147483647;background:%23123d2b;color:%23fff;padding:10px 14px;border-radius:8px;font:14px sans-serif';"
              "d.body.appendChild(n);var s=d.createElement('script');s.src=u;s.onload=function(){n.remove()};"
              "s.onerror=function(){fetch(u).then(function(r){return r.text()}).then(function(c){n.remove();(new Function(c))()})"
              ".catch(function(){n.textContent='Could not load the tracker. Render may be waking up — try again in 30 s.';setTimeout(function(){n.remove()},6000)})};"
              "d.body.appendChild(s)})()")
        import html as _h
        sync_ok = "yes" if sync.configured() else "NO — set DATA_REPO and GITHUB_TOKEN on Render"
        page = f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Service Plus Tracker</title><style>body{{font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:#eef3f0;color:#17241d;margin:0}}
.w{{max-width:760px;margin:0 auto;padding:18px}}.c{{background:#fff;border:1px solid #dce5df;border-radius:12px;padding:16px;margin-bottom:12px}}
h1{{font-size:22px;margin:0 0 4px;color:#123d2b}}a.bm{{display:inline-block;background:#123d2b;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:700}}
textarea{{width:100%;height:90px;font:12px monospace}}.m{{color:#5b6b62;font-size:13px}}ol li{{margin-bottom:6px}}</style></head><body><div class=w>
<div class=c><h1>Service Plus Tracker</h1><div class=m>Version {VERSION} · read-only — it never clicks Pull, Forward, Submit, Save Draft or Return to Pool · online saving: {sync_ok}</div></div>
<div class=c><b>Computer:</b> drag this button to the bookmarks bar → <a class=bm href="{_h.escape(js)}">SP Tracker</a>
<p class=m><b>Phone / any browser:</b> make a new bookmark named <b>SP Tracker</b> and paste the text below as its address (URL).</p>
<textarea readonly onclick="this.select()">{_h.escape(js)}</textarea></div>
<div class=c><b>Use</b><ol><li>Log in to <a href="https://jansugam.jk.gov.in/">jansugam.jk.gov.in</a> as Naib Tehsildar (the Dashboard is fine).</li>
<li>Tap the <b>SP Tracker</b> bookmark. The first time it asks for the access key (the same ACCESS_KEY as the Revenue Plus tracker).</li>
<li>Tap <b>Scan Inbox</b>. It goes through every service and task in Message Box → Inbox, reads each application's processing history, the Patwari and Girdawar reports and any Tehsildar revert comment, and keeps the Patwari's PDF.</li>
<li>Applications are read in sets of 10. If the login ends, log in again, open the tracker and tap <b>Resume</b>.</li></ol></div>
</div></body></html>"""
        return Response(page, mimetype="text/html")
