// SERVICE PLUS TRACKER VERSION 1.0
// Read-only tracker for the J&K Service Plus (JanSugam) portal — Naib Tehsildar inbox.
// It only ever clicks: Inbox, the Service / Task drop-downs, Get Data, Take Action (to read the page),
// View Processing History, the history links (Forwarded / Forwarded to Naib Tehsildar) and the report "view" links.
// It never clicks Pull, Forward, Submit, Save Draft, Reset, Cancel or Return to Pool.
!(function () {
  "use strict";
  if (window.__spTracker) {
    window.__spTracker.open();
    return;
  }
  var VER = "1.0",
    API = window.__spApiBase || "",
    LS_LAST = "spLast",
    LS_RUN = "spRun",
    LS_KEY = "spApiKey",
    SET = 10,
    stopFlag = false,
    busy = false,
    diag = [],
    blobs = {},
    view = { f: "all", q: "", sort: "days", open: {} },
    scan = null;

  // ───────────────────────── small helpers
  function T(s) {
    return String(s == null ? "" : s).replace(/ /g, " ").replace(/\s+/g, " ").trim();
  }
  function esc(s) {
    return T(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function escMl(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function sleep(ms) {
    return new Promise(function (r) {
      setTimeout(r, ms);
    });
  }
  function noTok(s) {
    return String(s || "").replace(/(OWASP_CSRFTOKEN|CSRFTOKEN|token)=[^&"' ]+/gi, "$1=…");
  }
  function log(m) {
    var line = new Date().toTimeString().slice(0, 8) + " " + noTok(m);
    diag.push(line);
    if (diag.length > 600) diag.splice(0, diag.length - 600);
  }
  function SpErr(kind, msg) {
    var e = new Error(msg || kind);
    e.kind = kind;
    return e;
  }
  async function waitFor(fn, ms, step) {
    var end = Date.now() + (ms || 20000);
    while (true) {
      if (stopFlag) throw SpErr("stopped", "Stopped");
      var v = null;
      try {
        v = fn();
      } catch (x) {
        v = null;
      }
      if (v) return v;
      if (Date.now() > end) return null;
      await sleep(step || 250);
    }
  }
  function parseD(s) {
    s = T(s);
    var m = /(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{4})(?:\D+(\d{1,2}):(\d{2})(?::(\d{2}))?)?/.exec(s);
    if (!m) return 0;
    return new Date(+m[3], +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0), +(m[6] || 0)).getTime();
  }
  function day0(t) {
    var d = new Date(t);
    d.setHours(0, 0, 0, 0);
    return d.getTime();
  }
  function daysSince(t) {
    return t ? Math.max(0, Math.round((day0(Date.now()) - day0(t)) / 864e5)) : null;
  }
  function dd(t) {
    return t ? new Date(t).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "";
  }
  function ddt(t) {
    return t ? new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "";
  }
  function title(s) {
    return T(s).toLowerCase().replace(/\b[a-z]/g, function (c) {
      return c.toUpperCase();
    });
  }
  function J(k) {
    try {
      return JSON.parse(localStorage.getItem(k) || "null");
    } catch (x) {
      return null;
    }
  }
  function setJ(k, v) {
    try {
      localStorage.setItem(k, JSON.stringify(v));
      return true;
    } catch (x) {
      log("localStorage full: " + x.message);
      return false;
    }
  }
  function login() {
    var m = /(Naib\s*tehsildar\s+[A-Za-z]+|Tehsildar\s+[A-Za-z]+)/i.exec(T((document.body.innerText || "").slice(0, 4000)));
    return m ? title(m[1]) : "Naib Tehsildar";
  }

  // ───────────────────────── service / task names
  var SVC = [
    [/agricultur/i, "Agriculture"],
    [/Other Backward Classes\s*-?\s*OBC \(for J&?K\)/i, "OBC (J&K)"],
    [/Backward Area\s*-?\s*RBA/i, "RBA"],
    [/Unemployment/i, "Unemployment"],
    [/Income Dependency/i, "Income Dependency"],
    [/Dependent/i, "Dependent"],
    [/General Caste/i, "General Caste"],
    [/Income/i, "Income"],
    [/Legal Heir/i, "Legal Heir"],
    [/OBC.*Government of India/i, "OBC (GoI)"],
    [/Unmarried|Widow|Divorce/i, "Unmarried / Widow / Divorce"],
  ];
  function svcShort(s) {
    for (var i = 0; i < SVC.length; i++) if (SVC[i][0].test(s)) return SVC[i][1];
    return T(s).replace(/^Application for (the )?issuance of /i, "").replace(/ by Tehsildar.*$/i, "").slice(0, 40);
  }
  function jobOf(task) {
    if (/naib\s*tehsildar/i.test(task) && /report/i.test(task)) return "report";
    if (/naib\s*tehsildar/i.test(task)) return "forward";
    return "other";
  }
  var JOB = { report: "Report due", forward: "To forward", other: "Other task" };

  // ───────────────────────── DOM reading (works inside the hidden frames)
  function fdoc(f) {
    try {
      return f.contentDocument;
    } catch (x) {
      return null;
    }
  }
  function ready(d) {
    try {
      return !!(d && d.readyState === "complete" && d.body && d.location && d.location.href !== "about:blank");
    } catch (x) {
      return false;
    }
  }
  function allDocs(d, out) {
    out = out || [];
    if (!d) return out;
    out.push(d);
    Array.prototype.forEach.call(d.querySelectorAll("iframe,frame"), function (f) {
      if (f.__spOwn) return;
      var c = fdoc(f);
      if (c && c.body) allDocs(c, out);
    });
    return out;
  }
  function isLogin(d) {
    try {
      return !!(d && d.querySelector('input[type="password"]') && !/Message\s*Box/i.test(d.body.textContent));
    } catch (x) {
      return false;
    }
  }
  function checkLogin(d) {
    if (isLogin(d)) throw SpErr("logout", "The Service Plus login has ended.");
  }
  function realOpts(sel) {
    return Array.prototype.filter
      .call((sel && sel.options) || [], function (o) {
        return o.value && !/^(-1|0|select)$/i.test(T(o.value)) && !/^-*\s*select\b/i.test(T(o.text));
      })
      .map(function (o) {
        return { value: o.value, text: T(o.text) };
      });
  }
  function labelOf(sel) {
    var d = sel.ownerDocument;
    if (sel.id) {
      var l = d.querySelector('label[for="' + sel.id + '"]');
      if (l) return T(l.textContent);
    }
    var p = sel.parentElement;
    for (var i = 0; i < 3 && p; i++, p = p.parentElement) {
      var prev = p.previousElementSibling;
      if (prev && T(prev.textContent).length < 40) return T(prev.textContent);
    }
    return "";
  }
  function serviceSel(d) {
    if (!d) return null;
    var best = null,
      n = 0;
    Array.prototype.forEach.call(d.querySelectorAll("select"), function (s) {
      var k = realOpts(s).filter(function (o) {
        return /^Application for/i.test(o.text);
      }).length;
      if (/select\s*service/i.test(labelOf(s))) k += 100;
      if (k > n) (n = k), (best = s);
    });
    return best;
  }
  function taskSel(d) {
    var ss = serviceSel(d);
    if (!ss) return null;
    var all = Array.prototype.slice.call(d.querySelectorAll("select")),
      lab = all.filter(function (s) {
        return s !== ss && /select\s*task/i.test(labelOf(s));
      })[0];
    if (lab) return lab;
    return (
      all.filter(function (s) {
        return s !== ss && /task|verification|report|scrutiny|forward/i.test((s.name || "") + " " + (s.id || "") + " " + T(s.textContent));
      })[0] || all[all.indexOf(ss) + 1] || null
    );
  }
  function setSel(sel, value) {
    var w = sel.ownerDocument.defaultView;
    sel.value = value;
    Array.prototype.forEach.call(sel.options, function (o) {
      o.selected = o.value === value;
    });
    try {
      sel.dispatchEvent(new w.Event("change", { bubbles: true }));
    } catch (x) {
      var ev = sel.ownerDocument.createEvent("HTMLEvents");
      ev.initEvent("change", true, false);
      sel.dispatchEvent(ev);
    }
  }
  function clickables(d) {
    return Array.prototype.slice.call(d.querySelectorAll("a,button,input[type=button],input[type=submit],span,div,h3,h4,h5,label"));
  }
  function byText(d, re, tags) {
    var els = Array.prototype.slice.call(d.querySelectorAll(tags || "a,button,input[type=button],input[type=submit]"));
    return els.filter(function (e) {
      return re.test(T(e.value || e.textContent));
    });
  }
  function hdrCells(table) {
    var r = table.querySelector("thead tr") || table.querySelector("tr");
    return r ? Array.prototype.map.call(r.children, function (c) {
      return T(c.textContent);
    }) : [];
  }
  function findTable(docs, res) {
    for (var i = 0; i < docs.length; i++) {
      var ts = docs[i].querySelectorAll("table");
      for (var j = 0; j < ts.length; j++) {
        var h = hdrCells(ts[j]).join(" | ");
        if (
          res.every(function (r) {
            return r.test(h);
          })
        )
          return ts[j];
      }
    }
    return null;
  }
  function bodyRows(table) {
    var rows = table.tBodies && table.tBodies.length ? Array.prototype.slice.call(table.tBodies[0].rows) : Array.prototype.slice.call(table.rows, 1);
    return rows.filter(function (r) {
      return r.cells.length > 1;
    });
  }
  function colIdx(table, re) {
    var h = hdrCells(table);
    for (var i = 0; i < h.length; i++) if (re.test(h[i])) return i;
    return -1;
  }
  async function showAll(table) {
    var w = table.ownerDocument.defaultView,
      $ = w.jQuery || w.$;
    try {
      if ($ && $.fn && $.fn.dataTable && $.fn.dataTable.isDataTable(table)) {
        var dt = $(table).DataTable();
        if (dt.page.info().pages > 1 || dt.page.len() !== -1) {
          dt.page.len(-1).draw(false);
          await sleep(300);
        }
        return "datatable";
      }
    } catch (x) {
      log("DataTable show-all failed: " + x.message);
    }
    return "plain";
  }
  // rows of a possibly paged table: when the DataTables API is not reachable, walk the pages with Next
  async function readPaged(table, readRows, enough) {
    var how = await showAll(table),
      out = readRows(table);
    if (how === "datatable") return out;
    if (
      bodyRows(table).some(function (r) {
        return r.style.display === "none";
      })
    )
      return out;
    var wrap = table.closest(".dataTables_wrapper") || table.parentElement;
    for (var p = 0; p < 40 && !(enough && enough(out)); p++) {
      var nx = wrap && Array.prototype.filter.call(wrap.querySelectorAll("a,button,li"), function (e) {
        return /^(next|›|»|>)$/i.test(T(e.textContent)) || /\bnext\b/.test(e.className || "");
      })[0];
      if (!nx || /disabled/.test(nx.className + " " + ((nx.parentElement && nx.parentElement.className) || ""))) break;
      var first = bodyRows(table)[0];
      (nx.querySelector("a") || nx).click();
      var ok = await waitFor(function () {
        return bodyRows(table)[0] !== first;
      }, 8000, 150);
      if (!ok) break;
      out = out.concat(readRows(table));
    }
    return out;
  }
  // label → value in "field view" pages (tables or bootstrap rows)
  function field(docs, re) {
    for (var i = 0; i < docs.length; i++) {
      var els = docs[i].querySelectorAll("td,th,label,b,strong,span,div,p,dt");
      for (var j = 0; j < els.length; j++) {
        var e = els[j],
          t = T(e.textContent).replace(/[:*]\s*$/, "").trim();
        if (t.length > 60 || !re.test(t)) continue;
        // a deeper element carries the same label → use that one (the row itself would point at the next row)
        if (
          Array.prototype.some.call(e.children, function (c) {
            return T(c.textContent).replace(/[:*]\s*$/, "").trim() === t;
          })
        )
          continue;
        var v = e.nextElementSibling;
        if (!v || !T(v.textContent + (v.querySelector("a,img") ? " x" : ""))) {
          var p = e.parentElement;
          if (p && /^(td|th|label|b|strong|span)$/i.test(e.tagName) && p.children.length === 1) v = p.nextElementSibling;
        }
        if (v) return { text: T(v.textContent), el: v };
      }
    }
    return null;
  }

  // a link that really goes somewhere (not "#" or javascript:)
  function realHref(a) {
    var h = (a.getAttribute("href") || "").trim();
    return !!h && !/^(#|javascript:)/i.test(h);
  }
  // ───────────────────────── hidden frames
  var host = null;
  function mkFrame(parentDoc, name) {
    var d = parentDoc || document,
      f = d.createElement("iframe");
    f.name = name;
    f.__spOwn = true;
    if (!parentDoc) f.setAttribute("sandbox", "allow-scripts allow-same-origin allow-forms");
    f.style.cssText = "position:fixed;left:-30000px;top:0;width:1280px;height:900px;border:0;visibility:hidden";
    (d.body || d.documentElement).appendChild(f);
    return f;
  }
  async function loadUrl(f, url) {
    var d0 = fdoc(f);
    f.src = url;
    var d = await waitFor(function () {
      var d = fdoc(f);
      return d !== d0 && ready(d) && d;
    }, 60000);
    if (!d) throw SpErr("timeout", "The portal did not answer (page " + noTok(url).replace(/^https?:\/\/[^/]+/, "") + ")");
    checkLogin(d);
    return d;
  }
  // Click a link inside a page and catch whatever it opens (same frame, a form target or window.open) in a child frame.
  var nameN = 0;
  async function openVia(link, readyTest, ms) {
    var d = link.ownerDocument,
      w = d.defaultView,
      nm = "__spF" + ++nameN,
      C = mkFrame(d, nm),
      saved = [],
      origOpen = w.open,
      url = null;
    w.open = function (u, n) {
      if (u && !/^\s*(about:blank)?\s*$/.test(u)) {
        url = new URL(u, d.baseURI).href;
        C.src = url;
      }
      if (n && !/^_(self|blank|top|parent)$/.test(n))
        try {
          C.contentWindow.name = n;
        } catch (x) {}
      return C.contentWindow;
    };
    Array.prototype.forEach.call(d.querySelectorAll("form,a"), function (el) {
      if (el.tagName === "A" && !realHref(el)) return;
      saved.push([el, el.getAttribute("target")]);
      el.setAttribute("target", nm);
    });
    var c0 = fdoc(C),
      href = link.getAttribute("href") || "";
    log("open: " + T(link.textContent).slice(0, 40) + " · " + noTok(href).slice(0, 120) + (link.getAttribute("onclick") ? " · onclick " + noTok(link.getAttribute("onclick")).slice(0, 120) : ""));
    link.click();
    var res = await waitFor(function () {
      var cd = fdoc(C);
      if (cd && cd !== c0 && ready(cd) && (!readyTest || isLogin(cd) || !/html/i.test(cd.contentType || "html") || readyTest(cd))) return { doc: cd, frame: C, where: "child" };
      if (w.document !== d && ready(w.document)) return { doc: w.document, frame: null, where: "self" };
      return null;
    }, ms || 30000);
    if (w.document === d) {
      w.open = origOpen;
      saved.forEach(function (s) {
        s[1] == null ? s[0].removeAttribute("target") : s[0].setAttribute("target", s[1]);
      });
    }
    if (!res) {
      try {
        C.remove();
      } catch (x) {}
      return { doc: null, url: url };
    }
    res.url = url;
    if (res.where === "self") log("  page opened in the same frame");
    checkLogin(res.doc);
    return res;
  }

  // ───────────────────────── Inbox
  var inboxUrl = null;
  async function openInbox(F) {
    if (!inboxUrl) {
      var a = byText(document, /^\s*Inbox\s*$/i, "a")[0];
      if (a && /^https?:/i.test(a.href) && !/#\s*$/.test(a.getAttribute("href") || "#")) inboxUrl = a.href;
    }
    if (inboxUrl) {
      var d = await loadUrl(F, inboxUrl);
      if (await waitFor(function () {
        return serviceSel(fdoc(F));
      }, 6000)) return fdoc(F);
      log("Inbox link did not show the Service list: " + noTok(fdoc(F).location.pathname));
    }
    // same page as the user, then click Message Box → Inbox inside it
    var d2 = await loadUrl(F, location.href),
      l = byText(d2, /^\s*Inbox\s*$/i, "a")[0];
    if (!l) throw SpErr("noinbox", "Could not find Message Box → Inbox. Open the Service Plus Dashboard and run the tracker again.");
    var r = await openVia(l, function (dd) {
      return serviceSel(dd);
    });
    if (!r.doc) throw SpErr("noinbox", "Inbox did not open.");
    if (r.where === "child") {
      inboxUrl = fdoc(r.frame).location.href;
      return loadUrl(F, inboxUrl);
    }
    inboxUrl = r.doc.location.href;
    return r.doc;
  }
  function selectedVal(sel) {
    return sel ? sel.value : "";
  }
  async function chooseService(F, v) {
    var d = fdoc(F),
      ss = serviceSel(d);
    if (!ss) throw SpErr("noinbox", "Service list not found on the Inbox page.");
    if (ss.value !== v) {
      // empty the task list first, so we wait for the tasks of the new service (not the old ones)
      var ts0 = taskSel(d);
      ts0 &&
        Array.prototype.slice.call(ts0.options).forEach(function (o) {
          if (realOpts({ options: [o] }).length) o.remove();
        });
      setSel(ss, v);
    }
    await sleep(500);
    var last = -1,
      same = 0;
    var ok = await waitFor(function () {
      var d = fdoc(F);
      if (!ready(d)) return null;
      var s = serviceSel(d),
        t = taskSel(d);
      if (!s || selectedVal(s) !== v || !t) return null;
      var n = realOpts(t).length;
      if (n && n === last) same++;
      else (same = 0), (last = n);
      return n && same >= 2 ? d : null;
    }, 20000);
    if (!ok) throw SpErr("task", "Task list did not fill for this service.");
    checkLogin(ok);
    return ok;
  }
  function resultTable(d) {
    return findTable(allDocs(d), [/Application\s*(Number|Ref)/i, /Action/i]);
  }
  async function getData(F, svcV, taskV) {
    var d = fdoc(F),
      ts = taskSel(d);
    if (ts && ts.value !== taskV) {
      setSel(ts, taskV);
      await sleep(400);
      d = await waitFor(function () {
        var x = fdoc(F);
        return ready(x) && taskSel(x) && x;
      }, 15000);
      ts = taskSel(d);
      if (ts && ts.value !== taskV) setSel(ts, taskV);
    }
    Array.prototype.forEach.call(d.querySelectorAll("table tr"), function (r) {
      r.__spOld = 1;
    });
    var btn = byText(d, /get\s*data/i)[0];
    if (!btn) throw SpErr("getdata", "Get Data button not found.");
    btn.click();
    var clickT = Date.now();
    var t = await waitFor(function () {
      var x = fdoc(F);
      if (!ready(x)) return null;
      var tb = resultTable(x);
      if (tb) {
        var rows = bodyRows(tb).concat(Array.prototype.map.call(tb.querySelectorAll("td.dataTables_empty"), function (td) {
          return td.parentNode;
        }));
        if (rows.length && !rows.some(function (r) {
          return r.__spOld;
        })) return tb;
      }
      var bt = T(x.body.textContent);
      if (Date.now() - clickT < 3000) return null;
      if (/no\s*(data|record|application)s?\s*(available|found)/i.test(bt) && !resultTable(x)) return "none";
      if (tb && !bodyRows(tb).length && /Showing\s*0\s*to\s*0\s*of\s*0/i.test(bt)) return "none";
      return null;
    }, 30000, 300);
    if (!t) throw SpErr("getdata", "No list came back after Get Data.");
    if (t === "none") return [];
    await sleep(300);
    var rows = await readPaged(t, function (tb) {
      var ia = colIdx(tb, /Application\s*(Number|Ref)/i),
        is = colIdx(tb, /^Status/i),
        ic = colIdx(tb, /^Action$/i);
      if (ic < 0) ic = colIdx(tb, /Action/i);
      return bodyRows(tb)
        .map(function (r) {
          var c = r.cells;
          return {
            ref: T(c[ia] && c[ia].textContent),
            status: is >= 0 ? T(c[is].textContent) : "",
            act: ic >= 0 ? T(c[ic].textContent) : "",
          };
        })
        .filter(function (x) {
          return /\/\d{4}\//.test(x.ref) || /^[A-Z]{2}-/.test(x.ref);
        });
    });
    var seen = {};
    return rows.filter(function (r) {
      return seen[r.ref] ? false : (seen[r.ref] = 1);
    });
  }
  function rowFor(d, ref) {
    var tb = resultTable(d);
    if (!tb) return null;
    var ia = colIdx(tb, /Application\s*(Number|Ref)/i),
      ic = colIdx(tb, /^Action$/i);
    if (ic < 0) ic = colIdx(tb, /Action/i);
    var r = bodyRows(tb).filter(function (r) {
      return T(r.cells[ia] && r.cells[ia].textContent) === ref;
    })[0];
    if (!r) return null;
    return { row: r, refLink: r.cells[ia] && r.cells[ia].querySelector("a"), actLink: ic >= 0 && r.cells[ic] ? r.cells[ic].querySelector("a,button") : null };
  }

  // ───────────────────────── one application
  function hasHist(d) {
    return /Processing\s*History|Task\s*Name/i.test(T(d.body && d.body.textContent));
  }
  async function history(detDoc) {
    var re = [/Task\s*Name/i, /Action\s*Details/i];
    var tb = findTable(allDocs(detDoc), re);
    if (!tb) {
      var h = Array.prototype.filter.call(detDoc.querySelectorAll("a,button,span,div,h3,h4,h5,label,b"), function (e) {
        return /^View\s*Processing\s*History$/i.test(T(e.textContent));
      });
      h.sort(function (a, b) {
        return a.textContent.length - b.textContent.length;
      });
      var el = h[0];
      if (el) {
        var c = el.closest("a,button,[onclick],[data-toggle],[data-bs-toggle],.panel-heading,.card-header") || el;
        log("  clicking View Processing History (" + c.tagName + ")");
        c.click();
      }
      tb = await waitFor(function () {
        return findTable(allDocs(detDoc), re);
      }, 25000, 300);
    }
    if (!tb) return null;
    await waitFor(function () {
      return bodyRows(tb).length;
    }, 8000);
    var rows = await readPaged(tb, function (t) {
      var I = {
        task: colIdx(t, /Task\s*Name/i),
        user: colIdx(t, /^User/i),
        rec: colIdx(t, /Received/i),
        pro: colIdx(t, /Processed/i),
        act: colIdx(t, /Action\s*Details/i),
      };
      return bodyRows(t).map(function (r) {
        var c = r.cells,
          g = function (i) {
            return i >= 0 && c[i] ? T(c[i].textContent) : "";
          };
        return {
          task: g(I.task),
          user: g(I.user),
          rec: g(I.rec),
          pro: g(I.pro),
          act: g(I.act),
          link: I.act >= 0 && c[I.act] ? c[I.act].querySelector("a") : null,
          recT: parseD(g(I.rec)),
          proT: parseD(g(I.pro)),
        };
      });
    });
    rows = rows.filter(function (r) {
      return r.task;
    });
    rows.sort(function (a, b) {
      return (b.proT || 9e15) - (a.proT || 9e15) || b.recT - a.recT;
    });
    return rows;
  }
  function isNT(t) {
    return /naib\s*tehsildar/i.test(t);
  }
  function isTeh(t) {
    return /tehsildar/i.test(t) && !isNT(t);
  }
  async function fetchFile(win, url) {
    return new Promise(function (ok, bad) {
      try {
        var x = new win.XMLHttpRequest();
        x.open("GET", url, true);
        x.responseType = "arraybuffer";
        x.withCredentials = true;
        x.timeout = 90000;
        x.onload = function () {
          if (x.status !== 200) return bad(new Error("HTTP " + x.status));
          ok({ buf: x.response, type: x.getResponseHeader("Content-Type") || "" });
        };
        x.onerror = function () {
          bad(new Error("network error"));
        };
        x.ontimeout = function () {
          bad(new Error("timed out"));
        };
        x.send();
      } catch (e) {
        bad(e);
      }
    });
  }
  function kindOf(buf, type) {
    var b = new Uint8Array(buf.slice(0, 8));
    if (b[0] === 0x25 && b[1] === 0x50 && b[2] === 0x44 && b[3] === 0x46) return "pdf";
    if (b[0] === 0xff && b[1] === 0xd8) return "jpg";
    if (b[0] === 0x89 && b[1] === 0x50) return "png";
    if (/pdf/i.test(type)) return "pdf";
    return "";
  }
  function b64(buf) {
    var s = "",
      a = new Uint8Array(buf);
    for (var i = 0; i < a.length; i += 32768) s += String.fromCharCode.apply(null, a.subarray(i, i + 32768));
    return btoa(s);
  }
  // fetch the file behind a "view" link and keep it (online in the data repo, or for this session only)
  async function grabFile(link, app, name) {
    var d = link.ownerDocument,
      w = d.defaultView,
      href = link.getAttribute("href") || "",
      url = /^\s*(#|javascript:)/i.test(href) || !href ? null : new URL(href, d.baseURI).href;
    if (!url) {
      // most "view" links call window.open(url): catch the address without opening anything
      var cap = null,
        orig = w.open;
      w.open = function (u) {
        cap = u ? new URL(u, d.baseURI).href : null;
        return { focus: function () {}, close: function () {}, document: { write: function () {}, close: function () {} } };
      };
      try {
        link.click();
        await waitFor(function () {
          return cap;
        }, 3000, 100);
      } finally {
        w.open = orig;
      }
      url = cap;
      if (!url) {
        // otherwise let it open (form posted to a window, or the page itself) in a hidden frame
        var r = await openVia(link, null, 10000).catch(function () {
          return {};
        });
        url = r.url || (r.frame && fdoc(r.frame) && fdoc(r.frame).location.href) || null;
        if (r.frame)
          try {
            r.frame.remove();
          } catch (x) {}
      }
    }
    if (!url) {
      log("  file link not understood: " + noTok(link.outerHTML).slice(0, 300));
      return { state: "failed", why: "link not understood" };
    }
    try {
      var f = await fetchFile(w, url),
        k = kindOf(f.buf, f.type);
      if (!k) {
        log("  file is not a PDF/image (" + f.type + ") from " + noTok(url).slice(0, 160));
        return { state: "failed", why: "not a PDF" };
      }
      var key = app + "|" + name;
      try {
        blobs[key] = URL.createObjectURL(new Blob([f.buf], { type: k === "pdf" ? "application/pdf" : "image/" + (k === "jpg" ? "jpeg" : "png") }));
      } catch (x) {}
      var out = { state: "local", ext: k, size: f.buf.byteLength, key: key };
      if (API && getKey(false)) {
        try {
          var j = await apiCall("POST", "/api/splus/pdf", { app: app, name: name, ext: k, b64: b64(f.buf) });
          out.state = "saved";
          out.path = j.path;
        } catch (x) {
          log("  online save of " + name + " failed: " + x.message);
          out.why = x.message;
        }
      }
      return out;
    } catch (x) {
      log("  file fetch failed: " + x.message + " · " + noTok(url).slice(0, 160));
      return { state: "failed", why: x.message };
    }
  }
  // read one "Action to be Taken by …" page (Patwari / Girdawar / Tehsildar)
  async function readAction(hrow, app, who, prevSame) {
    if (!hrow.link) return { user: hrow.user, date: hrow.pro, t: hrow.proT, text: "", nolink: true, files: [] };
    var r = await openVia(
      hrow.link,
      function (d) {
        return /Action\s*to\s*be\s*Taken|Remarks|Report/i.test(T(d.body.textContent));
      },
      30000
    );
    if (!r.doc) {
      log("  " + who + " page did not open");
      return { user: hrow.user, date: hrow.pro, t: hrow.proT, text: "", failed: true, files: [] };
    }
    var docs = allDocs(r.doc),
      g = function (re) {
        var x = field(docs, re);
        return x ? x.text : "";
      },
      out = {
        user: hrow.user,
        date: hrow.pro,
        t: hrow.proT,
        action: g(/^Action$/i),
        task: g(/^Task$/i),
        text: g(/^(Patwari\s*Report|Girdawar\s*Report|Tehsildar\s*Report|Report|Remarks)$/i),
        extra: g(/^Additional\s*Details\s*of\s*the\s*Report$/i),
        files: [],
      };
    if (!out.text) {
      var rm = field(docs, /^(\w+\s+)?(Report|Remarks)$/i);
      out.text = rm ? rm.text : "";
    }
    var slots = [
      [/^Upload\s*Report\s*\(?\s*PDF(\s*Format)?\s*\)?$/i, "report"],
      [/^Additional\s*Document\s*\(?\s*Image(\s*Format)?\s*\)?$/i, "doc-image"],
      [/^Additional\s*Document\s*\(?\s*PDF(\s*Format)?\s*\)?$/i, "doc-pdf"],
    ];
    for (var i = 0; i < slots.length; i++) {
      var f = field(docs, slots[i][0]),
        a = f && f.el.querySelector("a");
      if (!a) continue;
      var name = who + "-" + slots[i][1] + "-" + (hrow.proT ? new Date(hrow.proT).toISOString().slice(0, 10) : "x");
      if (prevSame && prevSame.files) {
        var old = prevSame.files.filter(function (z) {
          return z.name === name && z.state === "saved";
        })[0];
        if (old) {
          out.files.push(old);
          continue;
        }
      }
      var got = await grabFile(a, app, name);
      got.name = name;
      got.slot = slots[i][1];
      out.files.push(got);
    }
    if (r.frame)
      try {
        r.frame.remove();
      } catch (x) {}
    return out;
  }
  function norm(s) {
    return T(s).toLowerCase().replace(/[^a-z0-9]+/g, "");
  }
  function halqaOf(u) {
    var s = T(u)
      .replace(/^(PATWARI\s*HALQA|PATWARI|GQ|GIRDAWAR(\s*QANUNGO)?)\s*/i, "")
      .split(" ");
    if (s.length > 1 && /^(SUMBAL|SONAWARI|NOWGAM|SHADIPORA|BANDIPORA|HAJIN)$/i.test(s[s.length - 1])) s.pop();
    return title(s.join(" "));
  }
  function applicantOf(t) {
    var m = /applicant\s*(?:namely|name)?\s*(?:Mr\.?|Mst\.?|Smt\.?|Sh\.?)?\s*([A-Za-z][A-Za-z.\s]{2,45}?)\s+(?:s\/o|d\/o|w\/o|son\s*of|daughter\s*of|wife\s*of)/i.exec(t || "");
    return m ? title(m[1]) : "";
  }
  function villageOf(t) {
    var m = /village\s+([A-Za-z][A-Za-z ]{1,40}?)\s*(?:[.,;]|tehsil|teh\b|district|$)/i.exec(t || "");
    return m ? title(m[1]) : "";
  }
  var refNoHist = false;
  async function readOne(F, it, prev) {
    var d = fdoc(F),
      r = rowFor(d, it.ref);
    if (!r) throw SpErr("norow", "Application not in the list any more");
    var link = /take\s*action/i.test(it.act) ? r.actLink : /pull/i.test(it.act) ? null : r.actLink && !/pull/i.test(T(r.actLink.textContent)) ? r.actLink : null;
    var viaRef = false;
    if (!link && r.refLink && !refNoHist) (link = r.refLink), (viaRef = true);
    if (!link) {
      it.read = "nodetail";
      it.note = /pull/i.test(it.act) ? "Not pulled yet — no details open without Pull" : "No link to open";
      return { listDirty: false };
    }
    if (/pull/i.test(T(link.textContent)) || /return\s*to\s*pool/i.test(T(link.textContent))) throw SpErr("safety", "Refused to click " + T(link.textContent));
    var o = await openVia(
      link,
      function (dd) {
        return /Application\s*Reference|Processing\s*History|Current\s*Task/i.test(T(dd.body.textContent));
      },
      viaRef ? 12000 : 30000
    );
    if (!o.doc || (viaRef && !hasHist(o.doc))) {
      if (viaRef) {
        refNoHist = true;
        log("  the application-number link does not show the history — not pulled applications are listed without details");
      }
      if (o.frame)
        try {
          o.frame.remove();
        } catch (x) {}
      it.read = "nodetail";
      it.note = /pull/i.test(it.act) ? "Not pulled yet — details open only after Pull" : "Application page did not open";
      return { listDirty: o.where === "self" };
    }
    var dd = o.doc,
      docs = allDocs(dd),
      g = function (re) {
        var x = field(docs, re);
        return x ? x.text : "";
      };
    var refOn = g(/^Application\s*Reference\s*(Number|No)/i);
    if (refOn && norm(refOn) !== norm(it.ref)) {
      log("  opened " + refOn + " instead of " + it.ref);
      throw SpErr("wrongapp", "Opened a different application");
    }
    it.svcFull = g(/^Service\s*Name$/i) || it.svcFull;
    it.task = g(/^Current\s*Task$/i) || it.task;
    it.job = jobOf(it.task);
    it.applied = parseD(g(/^Application\s*(Received|Applied|Submission)\s*Date$/i));
    var h = await history(dd);
    if (!h) {
      it.read = "nohistory";
      it.note = "Processing history not found";
      log("  no history table for " + it.ref);
    } else {
      it.read = "ok";
      var cur =
        h.filter(function (x) {
          return !x.proT && isNT(x.task);
        })[0] ||
        h.filter(function (x) {
          return !x.proT;
        })[0];
      it.since = cur ? cur.recT : 0;
      var pat = h.filter(function (x) {
          return /patwari/i.test(x.task) && x.proT;
        })[0],
        gq = h.filter(function (x) {
          return /girdawar|qanungo/i.test(x.task) && x.proT;
        })[0];
      var revs = [];
      for (var i = 1; i < h.length; i++) if (isTeh(h[i].task) && h[i].proT && isNT(h[i - 1].task) && /report/i.test(h[i - 1].task)) revs.push(h[i]);
      it.halqa = pat ? halqaOf(pat.user) : gq ? halqaOf(gq.user) : "";
      it.hist = h.slice(0, 12).map(function (x) {
        return { task: x.task, user: x.user, rec: x.recT, pro: x.proT, act: x.act };
      });
      var same = function (a, b) {
        return a && b && a.user === b.user && a.t === b.t ? b : null;
      };
      it.pat = pat ? await readAction(pat, it.ref, "patwari", same({ user: pat.user, t: pat.proT }, prev && prev.pat)) : null;
      it.gq = gq ? await readAction(gq, it.ref, "girdawar", same({ user: gq.user, t: gq.proT }, prev && prev.gq)) : null;
      it.rev = null;
      if (revs.length) {
        var lr = await readAction(revs[0], it.ref, "tehsildar", same({ user: revs[0].user, t: revs[0].proT }, prev && prev.rev && prev.rev.latest));
        if (lr.task && !(isNT(lr.task) && /report/i.test(lr.task))) log("  Tehsildar step sends to “" + lr.task + "” — not counted as revert");
        it.rev = { n: revs.length, latest: lr };
      }
      if (it.pat) {
        it.applicant = applicantOf(it.pat.text);
        it.village = villageOf(it.pat.text);
      }
    }
    if (o.frame)
      try {
        o.frame.remove();
      } catch (x) {}
    return { listDirty: o.where === "self" };
  }
  function flagsOf(it) {
    var f = [];
    if (it.read === "nodetail" || it.read === "nohistory") f.push(["grey", it.note || "Details not read"]);
    if (it.rev) f.push(["red", "Reverted by Tehsildar" + (it.rev.n > 1 ? " " + it.rev.n + "×" : "")]);
    if (it.gq && !T(it.gq.text) && !it.gq.failed) f.push(["red", "Girdawar marked — no remarks"]);
    if (it.gq && it.pat && T(it.gq.text).length > 15 && norm(it.gq.text) === norm(it.pat.text)) f.push(["amber", "Girdawar remarks identical to Patwari's"]);
    if (it.pat && !patPdf(it)) f.push(["info", "No PDF submitted by Patwari"]);
    if (it.pat && patPdf(it) && patPdf(it).state === "failed") f.push(["amber", "Patwari PDF could not be fetched"]);
    return f;
  }
  function patPdf(it) {
    return it.pat && (it.pat.files || []).filter(function (z) {
      return z.slot === "report";
    })[0];
  }

  // ───────────────────────── online (Render + private data repo)
  function getKey(ask) {
    var k = "";
    try {
      k = localStorage.getItem(LS_KEY) || "";
    } catch (x) {}
    if (!k && ask) {
      k = T(prompt("Access key for the tracker (the ACCESS_KEY set on Render — same as Revenue Plus):") || "");
      if (k)
        try {
          localStorage.setItem(LS_KEY, k);
        } catch (x) {}
    }
    return k;
  }
  async function apiCall(method, path, body) {
    var key = getKey(false);
    if (!API || !key) throw new Error("no access key yet");
    var ac = window.AbortController ? new AbortController() : null;
    ac && setTimeout(function () {
      ac.abort();
    }, 120000);
    var r = await fetch(API + path, {
      method: method,
      headers: Object.assign({ "X-Access-Key": key }, body ? { "Content-Type": "application/json" } : {}),
      body: body ? JSON.stringify(body) : undefined,
      cache: "no-store",
      signal: ac ? ac.signal : undefined,
    });
    var j = {};
    try {
      j = await r.json();
    } catch (x) {}
    if (r.status === 401) {
      try {
        localStorage.removeItem(LS_KEY);
      } catch (x) {}
    }
    if (!r.ok) throw new Error(j.error || "HTTP " + r.status);
    return j;
  }
  var syncMsg = "";
  async function syncScan(s) {
    if (!API || !getKey(false)) return;
    try {
      syncMsg = "Saving scan online …";
      paintSync();
      await apiCall("POST", "/api/splus/scan", { login: s.login, scan: slim(s) });
      syncMsg = "✓ Saved online " + ddt(Date.now());
    } catch (x) {
      syncMsg = "Not saved online — " + String(x.message).slice(0, 90);
    }
    paintSync();
  }
  function slim(s) {
    var c = JSON.parse(JSON.stringify(s));
    (c.items || []).forEach(function (it) {
      ["pat", "gq"].forEach(function (k) {
        it[k] && (it[k].files || []).forEach(function (f) {
          delete f.key;
        });
      });
    });
    return c;
  }
  function paintSync() {
    var el = sh && sh.getElementById("sync");
    el && (el.textContent = syncMsg);
  }

  // ───────────────────────── the scan (sets of 10, resumable)
  var F = null;
  function frame() {
    if (!F || !F.isConnected) F = mkFrame(null, "__spList");
    return F;
  }
  async function ensureList(g) {
    var d = fdoc(frame());
    if (d && ready(d) && serviceSel(d) && selectedVal(serviceSel(d)) === g.svc && taskSel(d) && selectedVal(taskSel(d)) === g.task && resultTable(d)) return;
    if (!(d && ready(d) && serviceSel(d))) await openInbox(frame());
    await chooseService(frame(), g.svc);
    await getData(frame(), g.svc, g.task);
  }
  async function runScan(resume) {
    if (busy) return;
    busy = true;
    stopFlag = false;
    var R = resume ? J(LS_RUN) : null;
    var prevScan = J(LS_LAST),
      prev = {};
    ((prevScan && prevScan.items) || []).forEach(function (x) {
      prev[x.ref] = x;
    });
    try {
      if (!R || !R.items) {
        R = { v: VER, start: Date.now(), login: login(), items: [], i: 0, phase: "list", svcs: 0 };
        setJ(LS_RUN, R);
        prog("Opening Message Box → Inbox …", R);
        var d = await openInbox(frame());
        var svcs = realOpts(serviceSel(d));
        log("services: " + svcs.length + " · " + svcs.map(function (s) {
          return svcShort(s.text);
        }).join(", "));
        R.svcs = svcs.length;
        for (var s = 0; s < svcs.length; s++) {
          prog("Reading the list — " + svcShort(svcs[s].text) + " (" + (s + 1) + " of " + svcs.length + ")", R);
          var dd = await chooseService(frame(), svcs[s].value),
            tasks = realOpts(taskSel(dd));
          for (var k = 0; k < tasks.length; k++) {
            var rows = await getData(frame(), svcs[s].value, tasks[k].value);
            log(svcShort(svcs[s].text) + " · " + tasks[k].text + ": " + rows.length);
            rows.forEach(function (r) {
              R.items.push({
                ref: r.ref,
                svc: svcShort(svcs[s].text),
                svcFull: svcs[s].text,
                g: { svc: svcs[s].value, task: tasks[k].value },
                task: tasks[k].text,
                job: jobOf(tasks[k].text),
                act: r.act,
                status: r.status,
                read: "pending",
              });
            });
          }
        }
        R.phase = "detail";
        R.items.sort(function (a, b) {
          return (a.g.svc + a.g.task).localeCompare(b.g.svc + b.g.task);
        });
        setJ(LS_RUN, R);
      }
      for (; R.i < R.items.length; R.i++) {
        if (stopFlag) throw SpErr("stopped", "Stopped");
        var it = R.items[R.i];
        prog("Reading " + it.ref + " (" + (R.i + 1) + " of " + R.items.length + ")", R);
        var tries = 0;
        while (true) {
          try {
            await ensureList(it.g);
            var res = await readOne(frame(), it, prev[it.ref]);
            if (res.listDirty) await openInbox(frame());
            break;
          } catch (x) {
            if (x.kind === "logout" || x.kind === "stopped" || x.kind === "safety") throw x;
            log("  " + it.ref + ": " + x.message);
            if (++tries >= 2) {
              it.read = "error";
              it.note = x.message;
              break;
            }
            await openInbox(frame());
          }
        }
        it.at = Date.now();
        it.firstSeen = (prev[it.ref] && prev[it.ref].firstSeen) || it.since || Date.now();
        it.flags = flagsOf(it);
        setJ(LS_RUN, R);
        if ((R.i + 1) % SET === 0 && R.i + 1 < R.items.length) {
          finish(R, prev, prevScan, true);
        }
      }
      finish(R, prev, prevScan, false);
      try {
        localStorage.removeItem(LS_RUN);
      } catch (x) {}
      prog(null);
    } catch (x) {
      log("scan stopped: " + (x.kind || "") + " " + x.message);
      setJ(LS_RUN, R);
      prog(null);
      if (R && R.items && R.items.length) finish(R, prev, prevScan, true);
      var msg =
        x.kind === "logout"
          ? "Your Service Plus login has ended (the portal logs out after 30 minutes). Log in again, open the tracker and tap Resume — it continues from application " + (R.i + 1) + "."
          : x.kind === "stopped"
          ? "Scan stopped. Tap Resume to continue from application " + (R.i + 1) + "."
          : "The scan stopped: " + x.message + ". Tap Resume to try again, or Copy diagnostics and send them.";
      render(msg);
    } finally {
      busy = false;
      if (F) {
        try {
          F.remove();
        } catch (x) {}
        F = null;
      }
    }
  }
  function finish(R, prev, prevScan, partial) {
    var now = Date.now(),
      have = {};
    R.items.forEach(function (x) {
      have[x.ref] = 1;
    });
    var done = Object.assign({}, (prevScan && prevScan.done) || {});
    if (!partial) {
      Object.keys(prev).forEach(function (ref) {
        if (have[ref]) return;
        var p = prev[ref];
        done[ref] = { ref: ref, svc: p.svc, job: p.job, halqa: p.halqa, applicant: p.applicant, since: p.since, firstSeen: p.firstSeen, lastSeen: prevScan.at, doneAt: now };
      });
      R.items.forEach(function (x) {
        delete done[x.ref];
      });
      var ks = Object.keys(done).sort(function (a, b) {
        return done[b].doneAt - done[a].doneAt;
      });
      ks.slice(1000).forEach(function (k) {
        delete done[k];
      });
    }
    var items = R.items.map(function (x) {
      if (x.read === "pending" && prev[x.ref]) {
        var p = JSON.parse(JSON.stringify(prev[x.ref]));
        p.read = p.read === "ok" ? "old" : p.read;
        return p;
      }
      return x;
    });
    scan = { v: VER, at: R.start, login: R.login, items: items, done: done, partial: partial, read: R.i, total: R.items.length };
    setJ(LS_LAST, scan);
    syncScan(scan);
    render();
  }

  // ───────────────────────── screen
  var M = document.createElement("div");
  M.style.cssText = "position:fixed;inset:0;z-index:2147483646;";
  var sh = M.attachShadow({ mode: "open" });
  sh.innerHTML =
    "<style>:host{all:initial}*{box-sizing:border-box}.wrap{position:fixed;inset:0;background:#eef2f0;color:#17241d;font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;overflow:auto;-webkit-text-size-adjust:100%;font-variant-numeric:tabular-nums}" +
    ".bar{position:sticky;top:0;z-index:3;display:flex;align-items:center;gap:8px;padding:10px 14px;background:#123d2b;color:#fff}.bar b{font-size:16px;flex:1}.bar small{opacity:.8;font-weight:400;display:block;font-size:11px}" +
    "button{font:inherit;border:1px solid #cdd8d1;border-radius:8px;padding:8px 12px;cursor:pointer;background:#fff;color:#123d2b;font-weight:600}button.pri{background:#123d2b;border-color:#123d2b;color:#fff}button.x{background:transparent;border:0;color:#fff;font-size:22px;padding:2px 8px}" +
    ".box{max-width:1240px;margin:0 auto;padding:14px}.card{background:#fff;border:1px solid #dde5df;border-radius:12px;padding:14px;margin-bottom:12px;box-shadow:0 1px 2px rgba(16,40,30,.05)}.warn{background:#fff7e0;border-color:#f0d58a}" +
    ".top{display:flex;justify-content:space-between;align-items:flex-end;gap:10px;flex-wrap:wrap;margin-bottom:12px}.ttl{font-size:22px;font-weight:800;color:#123d2b}.sub{font-size:12px;color:#5d6b63}.btns{display:flex;gap:6px;flex-wrap:wrap}" +
    ".kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:12px}.kpi{background:#fff;border:1px solid #dde5df;border-top:4px solid #1f6b4a;border-radius:12px;padding:10px 12px;cursor:pointer}.kpi.on{outline:3px solid #123d2b}.kpi span{display:block;font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#5d6b63}.kpi b{display:block;font-size:28px;font-weight:800;line-height:1.15;color:#123d2b}.kpi em{font-style:normal;font-size:11.5px;color:#5d6b63}.kpi.red{border-top-color:#b42318}.kpi.red b{color:#b42318}.kpi.amb{border-top-color:#b26a00}.kpi.grey{border-top-color:#9aa5a0}" +
    ".tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:10px 14px;border-bottom:1px solid #e3e9e5;background:#fbfdfc}.tools input{flex:1;min-width:200px;padding:8px 11px;border:1px solid #cdd8d1;border-radius:8px;font:inherit}.tools select{padding:7px;border:1px solid #cdd8d1;border-radius:8px;font:inherit}" +
    ".tc{padding:0;overflow:hidden}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}th{background:#f3f6f4;color:#3b4a42;font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;text-align:left;padding:9px 10px;border-bottom:2px solid #d6dfd9;white-space:nowrap}td{padding:10px;border-bottom:1px solid #edf1ee;vertical-align:top}" +
    "tr.r{cursor:pointer}tr.r:hover td{background:#f4f8f6}tr.r.open td{background:#e9f2ed}tr.x td{background:#f7faf8;padding:12px 16px 16px}.ref{font-weight:800}.svc{font-size:11.5px;color:#5d6b63}.pill{display:inline-block;padding:2px 9px;border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap}" +
    ".p-report{background:#e3f1fb;color:#174e7a}.p-forward{background:#fff1d6;color:#8a5300}.p-other{background:#eceef2;color:#5b6475}.dy{display:inline-block;min-width:34px;text-align:center;padding:3px 9px;border-radius:14px;font-weight:800;font-size:14px}.d-g{background:#e3f4ea;color:#145c36}.d-a{background:#fff1d6;color:#8a5300}.d-r{background:#b42318;color:#fff}" +
    ".f{display:inline-block;margin:2px 4px 0 0;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:600}.f-red{background:#fde8e6;color:#9b1c13}.f-amber{background:#fff1d6;color:#8a5300}.f-info{background:#eef1f6;color:#3b4456}.f-grey{background:#eceef2;color:#5b6475}" +
    ".ok{color:#145c36;font-weight:700}.mut{color:#5d6b63;font-size:12px}.clip{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;max-width:300px;font-size:12.5px}.fb{padding:3px 9px;font-size:12px;margin:3px 4px 0 0}" +
    ".xg{display:grid;grid-template-columns:1fr 1fr;gap:12px}.xb{background:#fff;border:1px solid #dde5df;border-radius:10px;padding:10px 12px}.xb h5{margin:0 0 6px;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#5d6b63}.xb p{margin:4px 0;font-size:13px;white-space:pre-wrap}.xb.rv{border-color:#efc2bd;background:#fff8f7}" +
    ".hist{font-size:12px;width:100%}.hist td{padding:4px 6px;border-bottom:1px solid #eef1ef}.sums{display:grid;grid-template-columns:1fr 1fr;gap:12px}.sums td,.sums th{padding:7px 10px}" +
    ".prog{height:8px;background:#e1e7e3;border-radius:6px;overflow:hidden;margin:8px 0}.prog i{display:block;height:100%;background:#1f8a52}.dots{display:flex;flex-wrap:wrap;gap:4px}.dot{font-size:11px;padding:2px 7px;border-radius:10px;background:#eef2f0;color:#64746b}.dot.ok{background:#e3f4ea;color:#145c36;font-weight:700}.dot.cur{background:#123d2b;color:#fff}" +
    "details summary{cursor:pointer;font-weight:700;color:#123d2b}" +
    "@media(max-width:760px){.kpis{grid-template-columns:1fr 1fr}.xg,.sums{grid-template-columns:1fr}thead{display:none}tr.r{display:grid;grid-template-columns:1fr 1fr;gap:6px 10px;padding:10px 12px;border-bottom:1px solid #edf1ee}tr.r td{border:0;padding:0}tr.r td[data-l]:before{content:attr(data-l);display:block;font-size:9.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#5d6b63}tr.x{display:block}tr.x td{display:block}.clip{max-width:none}}" +
    "</style><div class=wrap><div class=bar><b>Service Plus Tracker<small>Read-only — never clicks Pull, Forward, Submit or Return to Pool · version " + VER + "</small></b><button class=x id=close title=Close>×</button></div><div class=box id=main></div></div>";
  var main = sh.getElementById("main");
  sh.getElementById("close").onclick = function () {
    if (busy && !confirm("A scan is running. Close anyway? (You can Resume later.)")) return;
    stopFlag = true;
    M.remove();
  };
  function open() {
    if (!M.isConnected) document.documentElement.appendChild(M);
    if (!busy) render();
  }
  window.__spTracker = { open: open, _diag: diag };

  var progState = null;
  function prog(msg, R) {
    progState = msg ? { msg: msg, R: R } : null;
    if (msg) log(msg);
    render();
  }
  function progHtml() {
    var p = progState,
      R = p.R || { items: [], i: 0 },
      n = R.items.length,
      pc = R.phase === "detail" && n ? Math.round((100 * R.i) / n) : 3,
      sets = [];
    for (var s = 0; s < Math.ceil(n / SET); s++) sets.push('<span class="dot ' + (R.phase === "detail" && (s + 1) * SET <= R.i ? "ok" : R.phase === "detail" && s * SET <= R.i ? "cur" : "") + '">Set ' + (s + 1) + "</span>");
    return (
      '<div class="card"><b>Scanning…</b> <span class=mut>' +
      esc(p.msg) +
      '</span><div class=prog><i style="width:' +
      pc +
      '%"></i></div>' +
      (n ? '<div class=dots>' + sets.join("") + "</div>" : "") +
      '<p class=mut>Keep this tab open. The portal logs out after 30 minutes — if that happens, log in again and tap Resume.</p><button id=stop>Stop</button></div>'
    );
  }
  function daysCls(n) {
    return n == null ? "" : n <= 3 ? "d-g" : n <= 7 ? "d-a" : "d-r";
  }
  function filt(items) {
    var q = view.q.toLowerCase();
    return items.filter(function (it) {
      var f = view.f;
      if (f === "report" && it.job !== "report") return false;
      if (f === "forward" && it.job !== "forward") return false;
      if (f === "rev" && !it.rev) return false;
      if (f === "flag" && !(it.flags || []).some(function (z) {
        return z[0] === "red" || z[0] === "amber";
      })) return false;
      if (f === "pull" && !/pull/i.test(it.act)) return false;
      if (q && (it.ref + " " + it.svc + " " + (it.halqa || "") + " " + (it.applicant || "") + " " + (it.village || "")).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
  }
  function fileBtns(it, x) {
    return (x && x.files ? x.files : [])
      .map(function (z, i) {
        var lab = z.slot === "report" ? "Report PDF" : z.slot === "doc-image" ? "Image" : "Document";
        if (z.state === "failed") return '<span class="f f-amber">' + lab + " — not fetched</span>";
        return '<button class=fb data-file="' + esc(it.ref) + "|" + esc(z.name) + '">' + lab + (z.state === "saved" ? "" : " (this browser)") + "</button>";
      })
      .join("");
  }
  function render(alertMsg) {
    if (!M.isConnected) return;
    var h = "";
    if (alertMsg) h += '<div class="card warn">' + esc(alertMsg) + "</div>";
    var run = J(LS_RUN);
    if (progState) h += progHtml();
    else if (run && run.items && run.i < run.items.length && !busy)
      h += '<div class="card warn"><b>Unfinished scan</b> — ' + run.i + " of " + run.items.length + ' applications read. <button class=pri id=resume>Resume</button> <button id=fresh>Start a new scan</button></div>';
    if (!scan) scan = J(LS_LAST);
    if (!scan) {
      h +=
        '<div class=card><div class=ttl>Applications with me</div><p class=mut>The scan goes through Message Box → Inbox for every service and task, opens each application\'s processing history, and reads the Patwari report (with its PDF), the Girdawar remarks and any Tehsildar revert comment. It only reads — nothing on the portal is changed.</p><div class=btns><button class=pri id=scan>Scan Inbox</button>' +
        (API ? "<button id=online>Show last scan saved online</button>" : "") +
        "<button id=diag>Copy diagnostics</button></div></div>";
      main.innerHTML = h;
      wire();
      return;
    }
    var items = scan.items || [],
      cnt = function (fn) {
        return items.filter(fn).length;
      },
      nRep = cnt(function (x) {
        return x.job === "report";
      }),
      nFwd = cnt(function (x) {
        return x.job === "forward";
      }),
      nRev = cnt(function (x) {
        return x.rev;
      }),
      nFlag = cnt(function (x) {
        return (x.flags || []).some(function (z) {
          return z[0] === "red" || z[0] === "amber";
        });
      }),
      nPull = cnt(function (x) {
        return /pull/i.test(x.act);
      }),
      oldest = items.reduce(function (m, x) {
        var d = daysSince(x.since);
        return d != null && d > m ? d : m;
      }, 0);
    h +=
      '<div class=top><div><div class=ttl>With ' +
      esc(scan.login || "me") +
      '</div><div class=sub>Scan of ' +
      ddt(scan.at) +
      " · " +
      items.length +
      " applications" +
      (scan.partial ? " · <b>part scan (" + scan.read + " of " + scan.total + " read)</b>" : "") +
      ' · <span id=sync>' +
      esc(syncMsg) +
      '</span></div></div><div class=btns><button class=pri id=scan>' +
      (busy ? "Scanning…" : "Rescan Inbox") +
      "</button>" +
      (API ? "<button id=online>Load online scan</button>" : "") +
      "<button id=csv>Download CSV</button><button id=diag>Copy diagnostics</button></div></div>";
    var k = function (f, cls, lab, n, em) {
      return '<div class="kpi ' + cls + (view.f === f ? " on" : "") + '" data-f="' + f + '"><span>' + lab + "</span><b>" + n + "</b><em>" + em + "</em></div>";
    };
    h +=
      "<div class=kpis>" +
      k("all", "", "With me", items.length, "oldest " + oldest + " days") +
      k("report", "", "Report due", nRep, "field reports back") +
      k("forward", "amb", "To forward", nFwd, "not yet forwarded") +
      k("rev", "red", "Reverted by Tehsildar", nRev, "comment to answer") +
      k("flag", "red", "Needs a look", nFlag, nPull + " not pulled yet") +
      "</div>";
    var list = filt(items).slice();
    list.sort(function (a, b) {
      if (view.sort === "days") return (daysSince(b.since) || -1) - (daysSince(a.since) || -1);
      if (view.sort === "halqa") return (a.halqa || "~").localeCompare(b.halqa || "~");
      if (view.sort === "svc") return a.svc.localeCompare(b.svc);
      return a.ref.localeCompare(b.ref);
    });
    h +=
      '<div class="card tc"><div class=tools><input id=q placeholder="Search application no., service, halqa, applicant…" value="' +
      esc(view.q) +
      '"><label class=mut>Sort <select id=sort>' +
      [["days", "Days with me"], ["ref", "Application no."], ["halqa", "Halqa"], ["svc", "Service"]]
        .map(function (o) {
          return '<option value="' + o[0] + '"' + (view.sort === o[0] ? " selected" : "") + ">" + o[1] + "</option>";
        })
        .join("") +
      "</select></label><span class=mut>" +
      list.length +
      " shown</span></div><div class=scroll><table><thead><tr><th>Application</th><th>Job</th><th>Halqa / applicant</th><th>With me since</th><th>Patwari</th><th>Girdawar</th><th>Tehsildar revert</th></tr></thead><tbody>";
    if (!list.length) h += '<tr><td colspan=7 class=mut style="text-align:center;padding:24px">Nothing here.</td></tr>';
    list.forEach(function (it) {
      var dys = daysSince(it.since),
        pp = patPdf(it),
        op = view.open[it.ref];
      h +=
        '<tr class="r' +
        (op ? " open" : "") +
        '" data-ref="' +
        esc(it.ref) +
        '"><td data-l=Application><div class=ref>' +
        esc(it.ref) +
        "</div><div class=svc>" +
        esc(it.svc) +
        (/pull/i.test(it.act) ? " · not pulled" : "") +
        "</div></td><td data-l=Job><span class=\"pill p-" +
        it.job +
        '">' +
        JOB[it.job] +
        '</span></td><td data-l="Halqa / applicant">' +
        esc(it.halqa || "—") +
        (it.applicant ? '<div class=mut>' + esc(it.applicant) + "</div>" : "") +
        '</td><td data-l="With me since">' +
        (dys == null ? '<span class=mut>—</span>' : '<span class="dy ' + daysCls(dys) + '">' + dys + "</span> <span class=mut>days · " + dd(it.since) + "</span>") +
        "</td><td data-l=Patwari>" +
        (it.pat
          ? '<span class=ok>✓ Report</span> <span class=mut>' + dd(it.pat.t) + "</span><br>" + (pp ? (pp.state === "failed" ? '<span class="f f-amber">PDF not fetched</span>' : '<span class=ok>PDF ✓</span>') : '<span class="f f-info">No PDF submitted</span>')
          : '<span class=mut>' + (it.read === "ok" ? "Not with Patwari yet" : "—") + "</span>") +
        "</td><td data-l=Girdawar>" +
        (it.gq
          ? T(it.gq.text)
            ? '<span class=ok>✓ Remarks</span> <span class=mut>' + dd(it.gq.t) + "</span>" + (it.pat && norm(it.gq.text) === norm(it.pat.text) && T(it.gq.text).length > 15 ? '<br><span class="f f-amber">Same as Patwari</span>' : "")
            : '<span class="f f-red">Marked — no remarks</span>'
          : '<span class=mut>' + (it.read === "ok" ? "Not marked" : "—") + "</span>") +
        '</td><td data-l="Tehsildar revert">' +
        (it.rev ? '<span class="f f-red">↩ ' + it.rev.n + "×</span> <span class=mut>" + dd(it.rev.latest.t) + '</span><div class=clip>' + esc(it.rev.latest.text) + "</div>" : '<span class=mut>—</span>') +
        ((it.flags || []).filter(function (z) {
          return z[0] === "grey";
        }).length
          ? (it.flags || [])
              .filter(function (z) {
                return z[0] === "grey";
              })
              .map(function (z) {
                return '<div><span class="f f-grey">' + esc(z[1]) + "</span></div>";
              })
              .join("")
          : "") +
        "</td></tr>";
      if (op) {
        h += '<tr class=x><td colspan=7><div class=xg>';
        h +=
          '<div class=xb><h5>Patwari report' +
          (it.pat ? " · " + esc(it.pat.user) + " · " + ddt(it.pat.t) : "") +
          "</h5>" +
          (it.pat ? "<p>" + escMl(it.pat.text || "(no text)") + "</p>" + (it.pat.extra ? '<p class=mut>' + escMl(it.pat.extra) + "</p>" : "") + (fileBtns(it, it.pat) || '<span class="f f-info">No PDF submitted</span>') : '<p class=mut>Not with the Patwari yet.</p>') +
          "</div>";
        h +=
          '<div class=xb><h5>Girdawar' +
          (it.gq ? " · " + esc(it.gq.user) + " · " + ddt(it.gq.t) : "") +
          "</h5>" +
          (it.gq ? "<p>" + escMl(it.gq.text || "(no remarks)") + "</p>" + fileBtns(it, it.gq) : '<p class=mut>Not marked to the Girdawar — no report needed.</p>') +
          "</div>";
        if (it.rev)
          h +=
            '<div class="xb rv"><h5>Reverted by Tehsildar ' +
            it.rev.n +
            "× · latest " +
            esc(it.rev.latest.user) +
            " · " +
            ddt(it.rev.latest.t) +
            "</h5><p>" +
            escMl(it.rev.latest.text || "(no remarks)") +
            "</p>" +
            fileBtns(it, it.rev.latest) +
            "</div>";
        h +=
          '<div class=xb><h5>Details</h5><p class=mut>' +
          esc(it.svcFull || it.svc) +
          "<br>Task: " +
          esc(it.task) +
          (it.applied ? "<br>Applied: " + dd(it.applied) + " (" + daysSince(it.applied) + " days ago)" : "") +
          (it.village ? "<br>Village in report: " + esc(it.village) : "") +
          "<br>On portal: " +
          esc(it.act || "—") +
          "</p>" +
          (it.hist && it.hist.length
            ? "<details><summary>Recent processing history</summary><table class=hist>" +
              it.hist
                .map(function (x) {
                  return "<tr><td>" + esc(x.task) + "</td><td>" + esc(x.user) + "</td><td>" + dd(x.rec) + "</td><td>" + (x.pro ? dd(x.pro) : "<b>pending</b>") + "</td><td>" + esc(x.act) + "</td></tr>";
                })
                .join("") +
              "</table></details>"
            : "") +
          "</div></div></td></tr>";
      }
    });
    h += "</tbody></table></div></div>";
    // summaries
    var by = function (key) {
      var m = {};
      items.forEach(function (it) {
        var k = it[key] || "—",
          o = (m[k] = m[k] || { n: 0, rep: 0, fwd: 0, rev: 0, old: 0 });
        o.n++;
        it.job === "report" && o.rep++;
        it.job === "forward" && o.fwd++;
        it.rev && o.rev++;
        o.old = Math.max(o.old, daysSince(it.since) || 0);
      });
      return Object.keys(m)
        .sort(function (a, b) {
          return m[b].n - m[a].n;
        })
        .map(function (k) {
          var o = m[k];
          return "<tr><td>" + esc(k) + "</td><td>" + o.n + "</td><td>" + o.rep + "</td><td>" + o.fwd + "</td><td>" + (o.rev || "") + '</td><td><span class="dy ' + daysCls(o.old) + '">' + o.old + "</span></td></tr>";
        })
        .join("");
    };
    var th = "<tr><th></th><th>With me</th><th>Report due</th><th>To forward</th><th>Reverted</th><th>Oldest (days)</th></tr>";
    h += '<div class=sums><div class="card tc"><table><thead>' + th.replace("<th></th>", "<th>Service</th>") + "</thead><tbody>" + by("svc") + '</tbody></table></div><div class="card tc"><table><thead>' + th.replace("<th></th>", "<th>Halqa</th>") + "</thead><tbody>" + by("halqa") + "</tbody></table></div></div>";
    var dn = Object.keys(scan.done || {})
      .map(function (k) {
        return scan.done[k];
      })
      .sort(function (a, b) {
        return b.doneAt - a.doneAt;
      });
    if (dn.length)
      h +=
        "<div class=card><details><summary>Done — left my Inbox (" +
        dn.length +
        ")</summary><p class=mut>Applications that were with you in an earlier scan and are no longer in the Inbox (forwarded or report submitted). The date is the scan that first missed them.</p><div class=scroll><table><thead><tr><th>Application</th><th>Service</th><th>Was</th><th>Halqa</th><th>With me since</th><th>Gone by</th></tr></thead><tbody>" +
        dn
          .slice(0, 300)
          .map(function (x) {
            return "<tr><td>" + esc(x.ref) + "</td><td>" + esc(x.svc) + "</td><td>" + (JOB[x.job] || "") + "</td><td>" + esc(x.halqa || "—") + "</td><td>" + dd(x.since) + "</td><td>" + dd(x.doneAt) + "</td></tr>";
          })
          .join("") +
        "</tbody></table></div></details></div>";
    main.innerHTML = h;
    wire();
  }
  function wire() {
    var $ = function (id) {
      return sh.getElementById(id);
    };
    $("scan") &&
      ($("scan").onclick = function () {
        if (busy) return;
        if (API) getKey(true);
        runScan(false);
      });
    $("resume") &&
      ($("resume").onclick = function () {
        if (API) getKey(true);
        runScan(true);
      });
    $("fresh") &&
      ($("fresh").onclick = function () {
        try {
          localStorage.removeItem(LS_RUN);
        } catch (x) {}
        if (API) getKey(true);
        runScan(false);
      });
    $("stop") &&
      ($("stop").onclick = function () {
        stopFlag = true;
        this.textContent = "Stopping…";
      });
    $("online") &&
      ($("online").onclick = async function () {
        getKey(true);
        this.textContent = "Loading…";
        try {
          var j = await apiCall("GET", "/api/splus/scan?login=" + encodeURIComponent(login()));
          if (!j.scan) return render("No scan saved online yet for " + login() + ".");
          scan = j.scan;
          setJ(LS_LAST, scan);
          syncMsg = "Loaded from online copy";
          render();
        } catch (x) {
          render("Could not load the online scan: " + x.message);
        }
      });
    $("diag") &&
      ($("diag").onclick = function () {
        var s = scan || {},
          txt =
            "Service Plus Tracker " + VER + " · " + new Date().toString() + "\nPage: " + location.pathname + "\nAPI: " + (API ? "yes" : "no") + " · key: " + (getKey(false) ? "yes" : "no") + "\nScan: " + (s.items ? s.items.length + " items, at " + ddt(s.at) : "none") + "\n" +
            (s.items || [])
              .map(function (it) {
                return it.ref + " | " + it.job + " | " + it.read + " | pat " + (it.pat ? (patPdf(it) ? patPdf(it).state : "nopdf") : "-") + " | gq " + (it.gq ? "y" : "-") + " | rev " + (it.rev ? it.rev.n : 0) + (it.note ? " | " + it.note : "");
              })
              .join("\n") +
            "\n--- log ---\n" +
            diag.join("\n");
        copy(txt);
      });
    $("csv") && ($("csv").onclick = csv);
    $("q") &&
      ($("q").oninput = function () {
        view.q = this.value;
        var p = this.selectionStart;
        render();
        var q = sh.getElementById("q");
        q.focus();
        q.setSelectionRange(p, p);
      });
    $("sort") &&
      ($("sort").onchange = function () {
        view.sort = this.value;
        render();
      });
    Array.prototype.forEach.call(sh.querySelectorAll(".kpi"), function (k) {
      k.onclick = function () {
        view.f = view.f === k.dataset.f ? "all" : k.dataset.f;
        render();
      };
    });
    Array.prototype.forEach.call(sh.querySelectorAll("tr.r"), function (r) {
      r.onclick = function (e) {
        if (e.target.closest("button")) return;
        view.open[r.dataset.ref] = !view.open[r.dataset.ref];
        render();
      };
    });
    Array.prototype.forEach.call(sh.querySelectorAll("button[data-file]"), function (b) {
      b.onclick = function (e) {
        e.stopPropagation();
        var p = b.dataset.file.split("|"),
          ref = p[0],
          name = p[1],
          it = (scan.items || []).filter(function (x) {
            return x.ref === ref;
          })[0],
          all = [].concat(it && it.pat ? it.pat.files || [] : [], it && it.gq ? it.gq.files || [] : [], it && it.rev && it.rev.latest ? it.rev.latest.files || [] : []),
          f = all.filter(function (z) {
            return z.name === name;
          })[0];
        if (!f) return;
        if (blobs[ref + "|" + name]) return window.open(blobs[ref + "|" + name], "_blank");
        if (f.state === "saved" && f.path) {
          var key = getKey(true);
          return window.open(API + "/api/splus/pdf?path=" + encodeURIComponent(f.path) + "&key=" + encodeURIComponent(key), "_blank");
        }
        alert("This file was only kept in the browser that scanned it. Rescan to fetch it again.");
      };
    });
  }
  function copy(txt) {
    if (navigator.clipboard && navigator.clipboard.writeText)
      navigator.clipboard.writeText(txt).then(
        function () {
          alert("Diagnostics copied — paste them in the chat.");
        },
        function () {
          prompt("Copy this:", txt);
        }
      );
    else prompt("Copy this:", txt);
  }
  function csv() {
    var rows = [["Application", "Service", "Job", "Halqa", "Applicant", "Applied", "With me since", "Days with me", "Patwari report", "Patwari PDF", "Girdawar remarks", "Girdawar same as Patwari", "Tehsildar reverts", "Latest revert comment", "Flags"]];
    (scan.items || []).forEach(function (it) {
      var pp = patPdf(it);
      rows.push([
        it.ref,
        it.svc,
        JOB[it.job],
        it.halqa || "",
        it.applicant || "",
        it.applied ? dd(it.applied) : "",
        it.since ? dd(it.since) : "",
        daysSince(it.since) == null ? "" : daysSince(it.since),
        it.pat ? T(it.pat.text) : "",
        it.pat ? (pp ? (pp.state === "failed" ? "not fetched" : "yes") : "No PDF submitted") : "",
        it.gq ? T(it.gq.text) || "(none)" : "not marked",
        it.gq && it.pat && norm(it.gq.text) === norm(it.pat.text) && T(it.gq.text).length > 15 ? "yes" : "",
        it.rev ? it.rev.n : "",
        it.rev ? T(it.rev.latest.text) : "",
        (it.flags || [])
          .map(function (z) {
            return z[1];
          })
          .join("; "),
      ]);
    });
    var s = "﻿" + rows
      .map(function (r) {
        return r
          .map(function (c) {
            return '"' + String(c).replace(/"/g, '""') + '"';
          })
          .join(",");
      })
      .join("\r\n");
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([s], { type: "text/csv" }));
    a.download = "ServicePlus-with-me-" + new Date().toISOString().slice(0, 10) + ".csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  if (!/jansugam\.jk\.gov\.in$/i.test(location.hostname)) log("Not on jansugam.jk.gov.in — scanning will not work here.");
  open();
  // wake Render early so the first save is quick
  if (API) fetch(API + "/api/ping", { cache: "no-store" }).catch(function () {});
})();
