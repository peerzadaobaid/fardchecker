// FARD CHECKER VERSION 1.9.9
!(function () {
  "use strict";
  if (window.__rpTracker) window.__rpTracker.open();
  else {
    var e = 400,
      t = "rpTrackerLast",
      a = [
        "With Patwari",
        "With Girdawar",
        "With Naib Tehsildar",
        "With Tehsildar",
        "Returned to applicant",
      ],
      r = [
        ["pat", /Patwari\s*Remarks\s*:/i],
        ["gir", /Gird\w*\s*Remarks\s*:/i],
        ["nt", /Naib\s*Tehsildar\s*Remarks\s*:/i],
        ["teh", /(?<!Naib\s{0,3})Tehsildar\s*Remarks\s*:/i],
        [
          "_stop",
          /Gist of all successive|Details of Final mutation|Enter Final Remarks/i,
        ],
      ],
      n = [
        ["svcType", "Service Type"],
        ["appNoD", "Applica\\w* No\\.?"],
        ["applicant", "Name of Applicant(?:\\s*/\\s*Vendor)?"],
        ["address", "Address"],
        ["mobileD", "Mobile"],
        ["email", "Email"],
        ["vendee", "Name of Vendee"],
        ["vendeeParent", "Parentage of Vendee"],
        ["_aadhaar", "Aadhaar No\\.? of Vendee"],
        ["vendeeOcc", "Occupation Of Vendee"],
        ["landUT", "Total land Owned in the UT"],
        ["landVillage", "Total land Owned in the Village"],
        ["vendeeMobile", "Mobile No\\.? of Vendee"],
        ["vendeeEmail", "Email Id of Vendee"],
        ["vendeeRes", "Resident\\w* Address of Vendee"],
        ["vendeePerm", "Permanent Address of Vendee"],
        ["_s", "Other Details"],
        ["district", "District"],
        ["tehsil", "Tehsil\\s*/\\s*Sub Tehsil"],
        ["areaType", "Area Type"],
        ["villageD", "Village"],
        ["villageArea", "Village Area"],
        ["areaCovered", "Area Covered"],
        ["aKhewat", "Khewat"],
        ["aKhata", "Khata"],
        ["aKhasra", "Khasra"],
        ["aOwnType", "Ownership Type"],
        ["aOwners", "No\\.? Of Owners"],
        ["aOwnPct", "Ownership Percentage"],
        ["applicantRemarks", "Applicant Remarks"],
        ["_s", "Uploaded Documents"],
        ["_s", "Members Remarks"],
        ["_s", "General Remarks"],
        ["_s", "By Patwari\\s*:?"],
        [
          "areaProposed",
          "Area Proposed for Alienation[^:]{0,60}?Purpose\\s*:?",
        ],
        ["_s", "Tatima Uploaded by Patwari"],
        ["_s", "Other Supporting Documents"],
        ["_s", "Certificate Details\\s*:?"],
        ["cKhewat", "Khewat No\\.?\\s*:"],
        ["cKhata", "Khata No\\.?\\s*:"],
        ["cKhasra", "Khasra No\\.?\\s*:"],
        ["cKanal", "Kanal\\s*:"],
        ["cMarla", "Marla\\s*:"],
        ["cSqft", "Sq\\.?\\s*Ft\\.?\\s*:"],
        ["cOwnType", "Ownership Type\\s*:"],
        ["owners", "Owner\\(s\\) name with full description\\s*:"],
        [
          "cultivator",
          "Cultivator\\s*/\\s*Owner name with full description\\s*:",
        ],
        ["ownRecords", "Ownership Details as per Revenue Records\\s*:"],
        ["shareKhewat", "Total share of applicant\\(s\\) in the Khewat\\s*:"],
        ["alienKhewat", "Area Already alienated in the Khewat\\s*:"],
        ["shareKhasra", "Total share of applicant\\(s\\) in the Khasra\\s*:"],
        ["alienKhasra", "Area Already alienated in the Khasra\\s*:"],
        ["cOwnType2", "Ownership Type"],
        [
          "possession",
          "Whether applicant is in possession of land in question\\s*:",
        ],
        [
          "encroach",
          "Whether the applicant has encroached any govt land\\s*/\\s*common land\\s*:",
        ],
        [
          "consent",
          "Whether consent for alienation has been given by the co-sharers[^:]{0,40}:",
        ],
        [
          "litigation",
          "Whether there is any court case\\s*/\\s*litigation on this land\\s*:",
        ],
        ["masterPlan", "Under Any Master Plan\\s*/\\s*Development Plan\\s*:"],
        [
          "vesting",
          "Whether the land has been given under Vesting of Ownership[^:]{0,40}:",
        ],
        [
          "roshni",
          "Has Been a Govt land in last 20 years or given under Rosh\\w* Scheme\\s*:",
        ],
        ["acquisition", "Under Land Acquisition Act\\s*:"],
        ["mortgage", "Is Morta\\w*ed or on lease\\s*:"],
        [
          "municipal",
          "Whether the land is situated within or outside Municipal Limits\\s*:",
        ],
        ["fit", "Whether the land is fit for alienation\\s*:"],
        ["onspot", "Onspot position of Land\\s*:"],
        ["possDuration", "Duration of possession\\s*:"],
        ["lat", "Latitude of the spot\\s*:"],
        ["lng", "Longitude of the spot\\s*:"],
        ["soil", "Kind of Soil as per Jamabandi\\s*:"],
        ["tatimaSource", "Source of Tatima\\s*:"],
        ["_s", "Adjoining Khasra Details\\s*:?"],
        ["lambardar", "Brief Summary of the statement of Lambardar[^:]{0,60}:"],
        ["barred", "Whether the land is barred from alienation[^:]{0,60}:"],
        ["patRemarks", "Patwari Remarks\\s*:"],
        ["girRemarks", "Gird\\w* Remarks\\s*:"],
        ["ntRemarks", "Naib Tehsildar Remarks\\s*:"],
        ["_s", "Gist of all successive"],
        ["_s", "Details of Final mutation"],
        ["_s", "Enter Final Remarks"],
        ["_s", "Documents Preview"],
      ],
      i = {
        svcType: "Service type",
        appNoD: "Application no.",
        applicant: "Applicant",
        address: "Applicant address",
        mobileD: "Applicant mobile",
        email: "Applicant email",
        vendee: "Vendee",
        vendeeParent: "Vendee parentage",
        vendeeOcc: "Vendee occupation",
        landUT: "Vendee land in UT",
        landVillage: "Vendee land in village",
        vendeeMobile: "Vendee mobile",
        vendeeEmail: "Vendee email",
        vendeeRes: "Vendee residential address",
        vendeePerm: "Vendee permanent address",
        district: "District",
        tehsil: "Tehsil",
        areaType: "Area type",
        villageD: "Village",
        villageArea: "Village area",
        areaCovered: "Area covered",
        aKhewat: "Khewat (application)",
        aKhata: "Khata (application)",
        aKhasra: "Khasra (application)",
        aOwnType: "Ownership type (application)",
        aOwners: "No. of owners",
        aOwnPct: "Ownership %",
        applicantRemarks: "Applicant remarks",
        areaProposed: "Area proposed for alienation (Patwari)",
        cKhewat: "Khewat (certificate)",
        cKhata: "Khata (certificate)",
        cKhasra: "Khasra (certificate)",
        cKanal: "Kanal",
        cMarla: "Marla",
        cSqft: "Sq. ft",
        cOwnType: "Ownership type (certificate)",
        owners: "Owner(s) with full description",
        cultivator: "Cultivator/owner",
        ownRecords: "Ownership as per revenue records",
        shareKhewat: "Applicant share in khewat",
        alienKhewat: "Already alienated in khewat",
        shareKhasra: "Applicant share in khasra",
        alienKhasra: "Already alienated in khasra",
        cOwnType2: "Ownership type",
        possession: "Applicant in possession",
        encroach: "Encroachment of govt/common land",
        consent: "Co-sharer consent",
        litigation: "Court case / litigation",
        masterPlan: "Under master/development plan",
        vesting: "Vesting of Ownership Act 2001",
        roshni: "Govt land in last 20 yrs / Roshni",
        acquisition: "Under Land Acquisition Act",
        mortgage: "Mortgaged / on lease",
        municipal: "Within municipal limits",
        fit: "Fit for alienation",
        onspot: "On-spot position",
        possDuration: "Duration of possession",
        lat: "Latitude",
        lng: "Longitude",
        soil: "Kind of soil (Jamabandi)",
        tatimaSource: "Source of tatima",
        lambardar: "Lambardar/Chowkidar statement",
        barred: "Barred from alienation under",
        patRemarks: "Patwari remarks",
        girRemarks: "Girdawar remarks",
        ntRemarks: "Naib Tehsildar remarks",
      },
      o =
        /^(mst|smt|mrs?|ms|sh|shri|late|haji|dr|mohd|mohammad|muhammad|md|gh|ghulam|ab|abdul)$/,
      s = "rpTrackerSLA",
      l = 864e5,
      d = { Patwari: "pat", Girdawar: "gir", "Naib Tehsildar": "nt" },
      c = { role: {}, village: {} },
      p = [
        "2026-01-05",
        "2026-01-17",
        "2026-01-26",
        "2026-02-15",
        "2026-03-17",
        "2026-03-19",
        "2026-03-20",
        "2026-03-21",
        "2026-03-26",
        "2026-04-14",
        "2026-05-01",
        "2026-05-27",
        "2026-05-28",
        "2026-06-26",
        "2026-07-05",
        "2026-08-15",
        "2026-08-26",
        "2026-08-28",
        "2026-09-04",
        "2026-09-23",
        "2026-10-02",
        "2026-10-20",
        "2026-10-26",
        "2026-11-08",
        "2026-11-24",
        "2026-12-25",
      ],
      u = null,
      f = ["Patwari", "Girdawar", "Naib Tehsildar"],
      h = "rpTrackerSeen",
      v = null,
      m = "#b42318",
      g = "#b26a00",
      b = document.createElement("div");
    b.style.cssText = "position:fixed;inset:0;z-index:2147483647;";
    var y = b.attachShadow({ mode: "open" });
    y.innerHTML =
      '<style>:host{all:initial}*{box-sizing:border-box}.wrap{position:fixed;inset:0;background:#f4f5f7;color:#1d2330;font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;overflow:auto;-webkit-text-size-adjust:100%}.bar{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:8px;padding:10px 14px;background:#12355b;color:#fff}.bar b{font-size:16px;flex:1}.bar small{opacity:.8;font-weight:400;display:block;font-size:11px}button{font:inherit;border:0;border-radius:8px;padding:9px 14px;cursor:pointer;background:#e6e9ef;color:#1d2330}button.pri{background:#1a7f5a;color:#fff}button.x{background:transparent;color:#fff;font-size:22px;padding:2px 8px}.box{max-width:1100px;margin:0 auto;padding:14px}.card{background:#fff;border:1px solid #e1e4ea;border-radius:12px;padding:14px;margin-bottom:12px}.warn{background:#fff7e0;border-color:#f0d58a}.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:12px}.tile{background:#fff;border:1px solid #e1e4ea;border-radius:10px;padding:10px;cursor:pointer}.tile.on{outline:2px solid #12355b}.tile .n{font-size:24px;font-weight:700}.tile .l{font-size:12px;color:#5b6475}.prog{height:10px;background:#e1e4ea;border-radius:6px;overflow:hidden;margin:10px 0}.prog i{display:block;height:100%;background:#1a7f5a;width:0}.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}input.s{flex:1;min-width:180px;padding:9px 12px;border:1px solid #c9ced8;border-radius:8px;font:inherit}.chip{padding:6px 10px;border-radius:20px;background:#e6e9ef;font-size:12px}.chip.on{background:#12355b;color:#fff}table{width:100%;border-collapse:collapse;background:#fff;font-size:13px}th,td{text-align:left;padding:8px;border-bottom:1px solid #eceef2;vertical-align:top}th{background:#f0f2f6;font-size:12px}tr.r{cursor:pointer}tr.r:hover{background:#f7f9fc}.st{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;white-space:nowrap}.s0{background:#fde2e2;color:#8a1c1c}.s1{background:#fff0d6;color:#7a4b00}.s2{background:#dcecff;color:#123f7a}.s3{background:#dff5e8;color:#145c36}.s9{background:#eee;color:#555}.apps tr.lv-p,.apps tr.lv-p td{background:#fff7da}.apps tr.lv-p td:first-child{box-shadow:inset 5px 0 0 #d9a400}.apps tr.lv-g,.apps tr.lv-g td{background:#ddf3ef}.apps tr.lv-g td:first-child{box-shadow:inset 5px 0 0 #1f9184}.apps tr.lv-n,.apps tr.lv-n td{background:#ece5fb}.apps tr.lv-n td:first-child{box-shadow:inset 5px 0 0 #6b48c8}.apps tr.lv-t,.apps tr.lv-t td{background:#eceef2}.apps tr.lv-t td:first-child{box-shadow:inset 5px 0 0 #6b7385}@media(max-width:640px){.apps tr.lv-p{box-shadow:inset 5px 0 0 #d9a400}.apps tr.lv-g{box-shadow:inset 5px 0 0 #1f9184}.apps tr.lv-n{box-shadow:inset 5px 0 0 #6b48c8}.apps tr.lv-t{box-shadow:inset 5px 0 0 #6b7385}.apps tr.r td:first-child{box-shadow:none}}.lvl{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}.lv{border-radius:10px;padding:10px;cursor:pointer;border:1px solid #e1e4ea;background:#fff}.lv .n{font-size:22px;font-weight:700}.lv .l{font-size:12px;color:#5b6475}.lv.on{outline:2px solid #12355b}.lv.k-p{background:#fff7da;border-left:5px solid #d9a400}.lv.k-g{background:#ddf3ef;border-left:5px solid #1f9184}.lv.k-n{background:#ece5fb;border-left:5px solid #6b48c8}.lv.k-t{background:#eceef2;border-left:5px solid #6b7385}.lv.k-0{border-left:5px solid #c9ced8}input.num{width:56px;padding:6px;border:1px solid #c9ced8;border-radius:6px;font:inherit}select{padding:6px;border:1px solid #c9ced8;border-radius:6px;font:inherit;max-width:100%}table.tlv tr.vrow{cursor:pointer}table.tlv tr.vrow:hover td{background:#f7f9fc}table.tlv tr.sel td{background:#e4ecf7}table.tl td,table.tl th{padding:5px 8px}.d{font-weight:700}.d.hi{color:#c62828}.flag{color:#c62828;font-size:12px}.det td{background:#fafbfd;font-size:12px}.det p{margin:4px 0}.scroll{overflow-x:auto;border-radius:10px;border:1px solid #e1e4ea}h3{margin:0 0 8px;font-size:15px}.muted{color:#5b6475;font-size:12px}@media(max-width:640px){.apps thead{display:none}.apps tr.r{display:block;padding:8px 6px;border-bottom:1px solid #eceef2}.apps tr.r td{display:inline-block;border:0;padding:2px 10px 2px 0;vertical-align:top}.apps tr.det td{display:block}.bar b{font-size:15px}}.modal{font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1d2330;position:fixed;inset:0;z-index:10;background:rgba(10,20,35,.6);display:flex;align-items:center;justify-content:center;padding:10px}.modal[hidden]{display:none}.mbox{background:#fff;border-radius:12px;width:min(980px,100%);height:min(92vh,960px);display:flex;flex-direction:column;overflow:hidden}.mhead{display:flex;gap:8px;align-items:center;padding:10px 12px;border-bottom:1px solid #e1e4ea}.mhead b{flex:1;font-size:14px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.mbody{flex:1;overflow:auto;display:flex;align-items:center;justify-content:center;background:#eef0f4}.mbody img{max-width:100%;max-height:100%;object-fit:contain}.mbody iframe{width:100%;height:100%;border:0;background:#fff}.docs{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}.docs button{padding:6px 10px;font-size:12px;background:#e4ecf7;color:#12355b}</style><div class="wrap"><div class="bar"><b>Revenue Plus Tracker<small>Read-only — never submits or changes anything · <span id="rpver">version 1.9.9</span><span id="rpwake"></span></small></b><button class="x" id="close">×</button></div><div id="rpscanbar" hidden style="position:sticky;top:0;z-index:2;background:#fff;border-bottom:1px solid #d5dbe6;box-shadow:0 3px 8px rgba(16,32,60,.08)"></div><div class="box" id="main"></div></div><div class="modal" id="modal" hidden><div class="mbox"><div class="mhead"><b id="mtitle"></b><span id="macts" style="display:flex;gap:6px"></span><button id="mclose">Close</button></div><div class="mbody" id="mbody"></div></div></div>';
    var w = y.getElementById("main");
    (y.getElementById("close").onclick = function () {
      location.assign(k.split("#")[0]);
    }),
      (y.getElementById("mclose").onclick = function () {
        !(function () {
          S && (S.hidden = !0);
          R && (URL.revokeObjectURL(R), (R = null));
        })();
      }),
      (y.getElementById("close").title = "Close and reload the dashboard");
    var x = null,
      k = location.href,
      A = !1,
      T = !1,
      P = !1,
      E = {
        logout:
          "Your Revenue Plus login has ended (the portal logs out after some time without use). Log in again, open the Dashboard, run Tracker and tap “Show last scan”. The documents will open again.",
        gone: "This application is no longer in the pending list on the Dashboard. It may have been processed since the scan. Run a new scan.",
        nolist: "The Dashboard did not show an application list when reloaded.",
      },
      S = null,
      R = null,
      N = {
        stage: "",
        age: "",
        q: "",
        flags: !1,
        errs: !1,
        scr: !1,
        level: "",
        village: "",
        over: "",
        tlBy: "village",
        tlEdit: !1,
        open: {},
        sum: !1,
      },
      O = [
        ["None", "k-0", "", "No action yet"],
        ["Patwari", "k-p", "lv-p", "Last comment: Patwari"],
        ["Girdawar", "k-g", "lv-g", "Last comment: Girdawar"],
        ["Naib Tehsildar", "k-n", "lv-n", "Last comment: Naib Tehsildar"],
        ["Tehsildar", "k-t", "lv-t", "Last comment: Tehsildar (later)"],
      ];
    (window.__rpTracker = {
      open: me,
      _recordSeen: de,
      _resetSeen: function () {
        v = null;
      },
      _dayNum: ie,
      _compliance: ce,
      _scrutiny: H,
      _caseText: W,
      _stage: Q,
      _jsDocUrl: function (e, t, a) {
        var r = j(e);
        return Pe(F(r)[t], r, a);
      },
      _parseDetail: I,
      _parseList: G,
      _stageOf: Q,
    }),
      me();
  }
  function D(e) {
    return String(null == e ? "" : e)
      .replace(/ /g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }
  function C(e) {
    return new Promise(function (t) {
      setTimeout(t, e);
    });
  }
  function L(e) {
    return D(e).replace(/[&<>"']/g, function (e) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[e];
    });
  }
  function j(e) {
    return new DOMParser().parseFromString(e, "text/html");
  }
  function M(e) {
    return (
      !(e = D(e)) ||
      /^(report\s*)?pending\.?$/i.test(e) ||
      /^(na|n\/a|-+|nil|none)$/i.test(e)
    );
  }
  function K(e) {
    var t = new URLSearchParams();
    return (
      Array.prototype.forEach.call(e.elements, function (e) {
        if (e.name && !e.disabled) {
          var a = (e.type || "").toLowerCase();
          ["submit", "button", "image", "reset", "file"].indexOf(a) >= 0 ||
            ((("checkbox" !== a && "radio" !== a) || e.checked) &&
              ("select-multiple" !== a
                ? t.append(e.name, e.value)
                : Array.prototype.forEach.call(e.options, function (a) {
                    a.selected && t.append(e.name, a.value);
                  })));
        }
      }),
      t.set("__EVENTTARGET", ""),
      t.set("__EVENTARGUMENT", ""),
      t
    );
  }
  function B(e) {
    return Array.prototype.filter.call(
      e.querySelectorAll("input[type=submit],button"),
      function (e) {
        return (
          /process/i.test((e.value || "") + " " + (e.textContent || "")) &&
          e.name
        );
      },
    );
  }
  function G(e) {
    var t = B(e),
      a = [];
    if (!t.length) return a;
    for (
      var r = t[0].closest("table"),
        n = [],
        i = r ? Array.prototype.slice.call(r.querySelectorAll("tr")) : [],
        o = 0;
      o < i.length;
      o++
    )
      if (/application\s*no/i.test(i[o].textContent) && !B(i[o]).length) {
        n = Array.prototype.map.call(i[o].children, function (e) {
          return D(e.textContent);
        });
        break;
      }
    function s(e, t) {
      for (var a in e) if (t.test(a)) return e[a];
      return "";
    }
    return (
      t.forEach(function (t) {
        var r = t.closest("tr");
        if (r) {
          var i = Array.prototype.map.call(r.children, function (e) {
              return D(e.textContent);
            }),
            o = {};
          n.forEach(function (e, t) {
            e && (o[e] = i[t] || "");
          }),
            a.push({
              appNo: s(o, /application\s*no/i) || i[0] || "",
              name: s(o, /name/i),
              mobile: s(o, /mobile/i),
              village: s(o, /village/i),
              khasra: s(o, /khasra/i),
              purpose: s(o, /purpose/i),
              appDate: s(o, /application\s*date/i),
              revert: parseInt(s(o, /revert/i), 10) || 0,
              days: parseInt(s(o, /days/i), 10) || 0,
              btnName: t.name,
              btnValue: t.value || "Process",
              form: t.form || e.forms[0],
            });
        }
      }),
      a
    );
  }
  function I(e) {
    var t = j(e),
      a = D(t.body ? t.body.textContent : ""),
      i = [];
    r.forEach(function (e) {
      var t = e[1].exec(a);
      t && i.push({ k: e[0], s: t.index, e: t.index + t[0].length });
    }),
      i.sort(function (e, t) {
        return e.s - t.s;
      });
    var o = { ok: !1 };
    function s(e) {
      var t = e.exec(a);
      return t ? D(t[1]) : "";
    }
    i.forEach(function (e, t) {
      if ("_stop" !== e.k) {
        var r = t + 1 < i.length ? i[t + 1].s : Math.min(a.length, e.e + 500);
        (o[e.k] = D(a.slice(e.e, r)).slice(0, 500)), (o.ok = !0);
      }
    }),
      (o.khewat = s(/Khewat\s*No\.?\s*:\s*(\S+)/i)),
      (o.khata = s(/Khata\s*No\.?\s*:\s*(\S+)/i)),
      (o.patReportPending =
        /Owner\(s\) name with full description\s*:\s*Report Pending/i.test(a)),
      (o.vendee = s(/Name of Vendee\s*(.{0,80}?)\s*Parentage of Vendee/i)),
      (o.area = s(
        /Area Proposed for Alienation[^:]{0,60}?Purpose\s*:?\s*(.{0,60}?)\s*(?:Tatima|Other Supporting|Certificate Details)/i,
      )),
      /Area Proposed for Alienation/i.test(a)
        ? (o.patTopPending = !o.area || /report\s*pending/i.test(o.area))
        : (o.patTopPending = o.patReportPending),
      o.patTopPending && (o.area = ""),
      (o.docs = F(t).map(function (e, t) {
        return { i: t, label: $(e) };
      }));
    try {
      (o.fields = (function (e) {
        var t = (function (e) {
            var t = e.body.cloneNode(!0);
            return (
              Array.prototype.forEach.call(
                t.querySelectorAll(
                  "script,style,noscript,option:not([selected])",
                ),
                function (e) {
                  e.remove();
                },
              ),
              Array.prototype.forEach.call(
                t.querySelectorAll("input"),
                function (t) {
                  var a = (t.getAttribute("type") || "text").toLowerCase();
                  [
                    "hidden",
                    "submit",
                    "button",
                    "image",
                    "reset",
                    "file",
                    "password",
                  ].indexOf(a) >= 0
                    ? t.remove()
                    : ("checkbox" !== a && "radio" !== a) ||
                        t.hasAttribute("checked")
                      ? t.replaceWith(
                          e.createTextNode(
                            " " + (t.getAttribute("value") || "") + " ",
                          ),
                        )
                      : t.remove();
                },
              ),
              Array.prototype.forEach.call(
                t.querySelectorAll(
                  "br,p,div,tr,li,label,h1,h2,h3,h4,h5,td,th,span,b,strong",
                ),
                function (e) {
                  e.insertAdjacentText("beforebegin", " "),
                    e.insertAdjacentText("afterend", " ");
                },
              ),
              D(t.textContent)
            );
          })(e),
          a = 0,
          r = [];
        n.forEach(function (e) {
          var n = new RegExp(e[1].replace(/ /g, "\\s+"), "i").exec(t.slice(a));
          if (n) {
            var i = a + n.index;
            r.push({ k: e[0], s: i, e: i + n[0].length }),
              (a = i + n[0].length);
          }
        });
        var i = {};
        return (
          r.forEach(function (e, a) {
            if ("_" !== e.k.charAt(0)) {
              var n = D(
                t.slice(e.e, a + 1 < r.length ? r[a + 1].s : e.e + 300),
              ).replace(/^[:\-\s]+/, "");
              /^View Uploaded Document/i.test(n) && (n = ""),
                (n = n.replace(/\s*(?:Name|Address\.?|Mobile No\.?|Email)?\s*Required\s*$/i, "")),
                (i[e.k] = n.slice(0, 600));
            }
          }),
          (function () {
            // Aadhaar check digit (Verhoeff) — only the result is kept, never the number
            var am = /Aadhaar\s*No\.?\s*of\s*Vendee\s*[:\-]?\s*(\d{4}\s?\d{4}\s?\d{4})(?!\d)/i.exec(t);
            if (!am) return;
            var num = am[1].replace(/\s/g, ""),
              vd = [[0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],[4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],[6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],[8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0]],
              vp = [[0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],[8,9,1,6,0,4,3,5,2,7],[9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],[2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8]],
              c = 0,
              rv = num.split("").reverse();
            for (var q = 0; q < rv.length; q++) c = vd[c][vp[q % 8][+rv[q]]];
            i.vendeeAadhaarOk = 0 === c && !/^[01]/.test(num) ? "valid" : "invalid";
          })(),
          i
        );
      })(t)),
        (o.adj = (function (e) {
          var t = Array.prototype.find.call(
            e.querySelectorAll("table"),
            function (e) {
              return (
                /north/i.test(e.textContent) &&
                /south/i.test(e.textContent) &&
                /west/i.test(e.textContent)
              );
            },
          );
          if (!t) return null;
          var a = Array.prototype.map.call(
              t.querySelectorAll("tr"),
              function (e) {
                return Array.prototype.map.call(e.children, function (e) {
                  return D(e.textContent);
                });
              },
            ),
            r = a[0] || [],
            n = {};
          return (
            a.slice(1).forEach(function (e) {
              var t = /owner/i.test(e[0])
                ? "owner"
                : /khasra/i.test(e[0])
                  ? "khasra"
                  : e[0];
              r.forEach(function (a, r) {
                r && a && ((n[a] = n[a] || {}), (n[a][t] = e[r] || ""));
              });
            }),
            n
          );
        })(t)),
        (o.mut = (function (e) {
          var t = { gist: [], final: [] };
          return (
            Array.prototype.forEach.call(
              e.querySelectorAll("table"),
              function (e) {
                var a = e.querySelector("tr");
                if (
                  a &&
                  /mutation/i.test(a.textContent) &&
                  !/forwarded/i.test(a.textContent)
                ) {
                  var r =
                    (function (e) {
                      for (
                        var t = e, a = 0;
                        t && a < 4;
                        t = t.parentElement, a++
                      )
                        for (
                          var r = t.previousElementSibling;
                          r;
                          r = r.previousElementSibling
                        ) {
                          var n = D(r.textContent);
                          if (n) return n.slice(0, 120);
                        }
                      return "";
                    })(e) +
                    " " +
                    (e.closest("div")
                      ? D(e.closest("div").textContent).slice(0, 80)
                      : "");
                  (/final/i.test(r) ? t.final : t.gist).push.apply(
                    /final/i.test(r) ? t.final : t.gist,
                    (function (e) {
                      var t = Array.prototype.slice.call(
                        e.querySelectorAll("tr"),
                      );
                      if (!t.length) return [];
                      var a = Array.prototype.map.call(
                        t[0].children,
                        function (e) {
                          return D(e.textContent);
                        },
                      );
                      return t
                        .slice(1)
                        .map(function (e) {
                          var t = {};
                          return (
                            Array.prototype.forEach.call(
                              e.children,
                              function (e, r) {
                                t[a[r] || "col" + r] = D(e.textContent);
                              },
                            ),
                            t
                          );
                        })
                        .filter(function (e) {
                          return Object.keys(e).some(function (t) {
                            return e[t];
                          });
                        });
                    })(e),
                  );
                }
              },
            ),
            t
          );
        })(t));
    } catch (e) {
      o.fields = o.fields || {};
    }
    o.history = [];
    var l = Array.prototype.find.call(
      t.querySelectorAll("table"),
      function (e) {
        var t = e.querySelector("tr");
        return t && (/forwarded\s*by/i.test(t.textContent) || (/action\s*by/i.test(t.textContent) && /date/i.test(t.textContent)));
      },
    );
    return (
      l &&
        (Array.prototype.slice
          .call(l.querySelectorAll("tr"), 1)
          .forEach(function (e) {
            var t = Array.prototype.map.call(e.children, function (e) {
              return D(e.textContent);
            });
            if (!(t.length < 3) && t[1]) {
              var a = t[t.length - 1];
              o.history.push({
                by: t[1],
                remark: t.slice(2, t.length - 1).join(" "),
                date: a,
                t: J(a),
              });
            }
          }),
        o.history.length && (o.ok = !0)),
      !/Area Proposed for Alienation/i.test(a) &&
        o.history.length &&
        ((o.patTopPending = !o.history.some(function (h) {
          return "Patwari" === X(h.by);
        })),
        (o.patReportPending = o.patTopPending),
        o.patTopPending && (o.area = "")),
      !o.ok &&
        o.fields &&
        (o.fields.appNoD || o.fields.applicant) &&
        /Members\s*Remarks[\s\S]{0,120}?No\s*data\s*found/i.test(a) &&
        ((o.ok = !0), (o.fresh = !0)),
      o
    );
  }
  function U(e) {
    if (!(e = String(e || "").toLowerCase()) || /pending|^na$|^nil/.test(e))
      return null;
    var t = /(\d+(?:\.\d+)?)\s*k(?:anal|nl)?\b/.exec(e),
      a = /(\d+(?:\.\d+)?)\s*m(?:arla|rl)?\b/.exec(e),
      r = /(\d+(?:\.\d+)?)\s*s(?:arsai|rs)\b/.exec(e),
      n = /(\d+(?:\.\d+)?)\s*(?:sq\.?\s*ft|sqft|square\s*feet|sft)\b/.exec(e);
    return t || a || r || n
      ? (t ? 20 * +t[1] : 0) +
          (a ? +a[1] : 0) +
          (r ? +r[1] / 9 : 0) +
          (n ? +n[1] / 272.25 : 0)
      : null;
  }
  function q(e) {
    if (null == e) return "—";
    var t = Math.floor(e / 20 + 1e-9);
    return (t ? t + " K " : "") + Math.round(100 * (e - 20 * t)) / 100 + " M";
  }
  function V(e, t) {
    var a = String(t || "")
        .toLowerCase()
        .replace(/[^a-z ]/g, " ")
        .split(/\s+/)
        .filter(Boolean),
      r = String(e || "")
        .toLowerCase()
        .replace(/[^a-z ]/g, " ")
        .split(/\s+/)
        .filter(function (e) {
          return e && !o.test(e);
        });
    return r.length && a.length
      ? a.some(function (e) {
          return (
            1 -
              (function (e, t) {
                for (var a = [], r = 0; r <= e.length; r++) a[r] = [r];
                for (var n = 0; n <= t.length; n++) a[0][n] = n;
                for (r = 1; r <= e.length; r++)
                  for (n = 1; n <= t.length; n++)
                    a[r][n] = Math.min(
                      a[r - 1][n] + 1,
                      a[r][n - 1] + 1,
                      a[r - 1][n - 1] + (e[r - 1] === t[n - 1] ? 0 : 1),
                    );
                return a[e.length][t.length];
              })(r[0], e) /
                Math.max(r[0].length, e.length) >=
            0.75
          );
        })
      : null;
  }
  function _(e) {
    return /^\s*(yes|y|haan|ha)\b/i.test(e || "");
  }
  function z(e) {
    return /^\s*(no|n|nil|nill|none|na)\b/i.test(e || "");
  }
  function H(e) {
    var t = e.fields || {},
      a = [];
    function r(e, t) {
      a.push({ l: e, t: t });
    }
    if (!e.fields) return a;
    if ("Pending" === e.patReport)
      r("info", "Patwari report not yet submitted — report checks skipped.");
    else {
      _(t.roshni) &&
        r("red", "Govt land in last 20 years / Roshni: " + t.roshni),
        _(t.encroach) &&
          r("red", "Encroachment of govt/common land: " + t.encroach),
        _(t.litigation) && r("red", "Court case / litigation: " + t.litigation),
        _(t.acquisition) &&
          r("red", "Under Land Acquisition Act: " + t.acquisition),
        _(t.vesting) &&
          r("red", "Given under Vesting of Ownership Act 2001: " + t.vesting),
        t.fit &&
          z(t.fit) &&
          r("red", "Patwari says land is NOT fit for alienation."),
        !t.barred ||
          z(t.barred) ||
          /pending/i.test(t.barred) ||
          r("red", "Barred from alienation under: " + t.barred),
        _(t.mortgage) && r("amber", "Mortgaged / on lease: " + t.mortgage),
        t.possession &&
          z(t.possession) &&
          r("amber", "Applicant not in possession."),
        _(t.masterPlan) &&
          r("amber", "Under master/development plan: " + t.masterPlan),
        (+t.aOwners > 1 ||
          (t.aOwnPct && +t.aOwnPct < 100) ||
          /joint/i.test(t.cOwnType + " " + t.aOwnType)) &&
          !_(t.consent) &&
          r(
            "amber",
            'Joint holding but co-sharer consent is "' +
              (t.consent || "blank") +
              '".',
          );
      var n = U(t.areaProposed),
        i = U(t.shareKhewat),
        o = U(t.alienKhewat) || 0;
      null != n &&
        null != i &&
        n > i - o + 0.01 &&
        r(
          "red",
          "Area proposed (" +
            q(n) +
            ") exceeds share in khewat less already alienated (" +
            q(i - o) +
            ").",
        );
      var s =
        20 * (+t.cKanal || 0) + (+t.cMarla || 0) + (+t.cSqft || 0) / 272.25;
      null != n &&
        s &&
        Math.abs(n - s) > 0.05 &&
        r(
          "amber",
          "Area proposed (" +
            q(n) +
            ") differs from certificate area (" +
            q(s) +
            ").",
        ),
        t.shareKhasra &&
          /^\s*k(anal)?\s*$/i.test(t.shareKhasra) &&
          r(
            "amber",
            'Share in khasra has no figure ("' + t.shareKhasra + '").',
          ),
        /pending/i.test(t.lambardar || "") &&
          r("amber", 'Lambardar/Chowkidar statement still "Report Pending".'),
        (D(t.lat) && D(t.lng)) ||
          r("info", "Spot latitude/longitude not recorded.");
      var l = String(t.applicant || e.name || "")
          .split(/\s+and\s+|,|&/i)
          .map(D)
          .filter(Boolean),
        d = [t.owners, t.ownRecords]
          .concat(
            ((e.mut && e.mut.final) || []).map(function (e) {
              return Object.keys(e)
                .map(function (t) {
                  return e[t];
                })
                .join(" ");
            }),
          )
          .join(" "),
        c = l.filter(function (e) {
          return !1 === V(e, d);
        });
      c.length &&
        r(
          "amber",
          "Applicant name not found in owner details / final mutation: " +
            c.join(", ") +
            ".",
        );
    }
    return (
      t.aKhasra &&
        t.cKhasra &&
        !/pending/i.test(t.cKhasra) &&
        D(t.aKhasra).toLowerCase() !== D(t.cKhasra).toLowerCase() &&
        r(
          "amber",
          "Khasra on application (" +
            t.aKhasra +
            ") ≠ certificate (" +
            t.cKhasra +
            ").",
        ),
      t.aKhewat &&
        t.cKhewat &&
        !/pending/i.test(t.cKhewat) &&
        D(t.aKhewat) !== D(t.cKhewat) &&
        r(
          "amber",
          "Khewat on application (" +
            t.aKhewat +
            ") ≠ certificate (" +
            t.cKhewat +
            ").",
        ),
      e.mut &&
        !e.mut.final.length &&
        "Pending" !== e.patReport &&
        r("amber", "No final mutation in the applicant's name is shown."),
      (e.history || []).some(function (e) {
        return /already issued|stands issued|previously issued/i.test(e.remark);
      }) && r("info", "A remark says a Fard was already issued for this land."),
      e.revert >= 2 && r("info", "Reverted " + e.revert + " times."),
      a
    );
  }
  function W(e) {
    var t = e.fields || {},
      a = [];
    a.push(
      "Please scrutinise this Revenue Plus application as a Naib Tehsildar in J&K would. Check ownership and share, area proposed against share and earlier alienations, restrictions (State/Kahcharai land, Roshni, Land Acquisition, Agrarian Reforms / Vesting Act 2001, mortgage, litigation, municipal or master-plan limits), consistency between the application, the Patwari report and the mutation record, and the movement history (delays, reverts). List the issues by severity, say what is missing, and draft a suitable remark and next action.",
    ),
      a.push(
        "",
        "## Application",
        "Service: " +
          (t.svcType || e.service) +
          " · Application no.: " +
          e.appNo +
          " · Purpose: " +
          e.purpose +
          " · Applied/resubmitted: " +
          e.appDate +
          " · Revert count: " +
          e.revert +
          " · Days passed (portal): " +
          e.days,
      ),
      a.push(
        "Current stage (tracker): " +
          e.stage +
          (e.holder ? " — " + e.holder : "") +
          (null != e.stageDays
            ? ", " + e.stageDays + " days at this stage"
            : "") +
          " · Patwari report: " +
          (e.patReport || "?"),
      );
    var r = {
      mobileD: 1,
      email: 1,
      vendeeMobile: 1,
      vendeeEmail: 1,
      appNoD: 1,
      svcType: 1,
    };
    a.push("", "## Details on the portal"),
      Object.keys(i).forEach(function (e) {
        !r[e] && t[e] && a.push("- " + i[e] + ": " + t[e]);
      }),
      e.adj &&
        (a.push("", "## Adjoining khasras"),
        Object.keys(e.adj).forEach(function (t) {
          a.push(
            "- " +
              t +
              ": khasra " +
              (e.adj[t].khasra || "—") +
              ", owner " +
              (e.adj[t].owner || "—"),
          );
        })),
      e.mut &&
        [
          ["gist", "Successive mutations on this land"],
          ["final", "Final mutation in which applicant's name appears"],
        ].forEach(function (t) {
          a.push("", "## " + t[1]);
          var r = e.mut[t[0]] || [];
          r.length || a.push("- None shown"),
            r.forEach(function (e) {
              a.push(
                "- " +
                  Object.keys(e)
                    .filter(function (t) {
                      return e[t];
                    })
                    .map(function (t) {
                      return t + ": " + e[t];
                    })
                    .join("; "),
              );
            });
        }),
      a.push("", "## Movement of file (Members Remarks)"),
      (e.history || []).forEach(function (e, t) {
        a.push(
          t + 1 + ". " + (Z(e.t) || e.date) + " — " + e.by + ": " + e.remark,
        );
      });
    var n = H(e);
    return (
      n.length &&
        (a.push("", "## Automatic checks already flagged"),
        n.forEach(function (e) {
          a.push("- [" + e.l + "] " + e.t);
        })),
      a.push(
        "",
        "Note: on this portal the “Patwari / Naib Tehsildar Remarks” lines near the end often stay “Report Pending” even after action. The Members Remarks history is the real record. Whether the Patwari report is in is shown by “Area proposed for alienation (Patwari)”.",
      ),
      a.push(
        "",
        "(Mobile numbers, emails and Aadhaar are left out on purpose.)",
      ),
      a.join("\n")
    );
  }
  function F(e) {
    return Array.prototype.filter.call(
      e.querySelectorAll(
        "a,input[type=submit],input[type=button],input[type=image],button",
      ),
      function (e) {
        return /(view|download)\s*uploaded\s*doc/i.test(
          (e.value || "") +
            " " +
            (e.textContent || "") +
            " " +
            (e.getAttribute("title") || ""),
        );
      },
    );
  }
  function $(e) {
    if (/download/i.test((e.value || "") + " " + e.textContent))
      return "All documents (download)";
    for (var t = e, a = 0; a < 4 && t; a++) {
      for (var r = t.previousElementSibling; r; r = r.previousElementSibling) {
        var n = D(r.textContent);
        if (n && n.length < 70 && !/uploaded\s*doc/i.test(n))
          return n.replace(/\s*:$/, "");
        if (n && /uploaded\s*doc/i.test(n)) break;
      }
      t = t.parentElement;
    }
    return "Document";
  }
  function J(e) {
    var t = /([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})/.exec(e);
    if (t) {
      var a = new Date(t[1] + " " + t[2] + " " + t[3]).getTime();
      if (!isNaN(a)) return a;
    }
    if ((t = /(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?,?\s+(\d{4})/.exec(e))) {
      var r = new Date(t[2] + " " + t[1] + " " + t[3]).getTime();
      if (!isNaN(r)) return r;
    }
    return (t = /(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{4})/.exec(e))
      ? new Date(+t[3], +t[2] - 1, +t[1]).getTime()
      : 0;
  }
  function X(e) {
    return (
      (e = String(e || "").toUpperCase().trim()),
      /^NAIB/.test(e)
        ? "Naib Tehsildar"
        : /^TEH/.test(e)
        ? "Tehsildar"
        : /^NT/.test(e)
          ? "Naib Tehsildar"
          : /^(GIR|GD|GQ|GR)/.test(e)
            ? "Girdawar"
            : /^(PAT|PT)/.test(e)
              ? "Patwari"
              : ""
    );
  }
  function Y(e) {
    var t = X(e);
    if (!t) return e;
    if (/^(naib\s+tehsildar|tehsildar|girdh?awar|patwari)\b/i.test(String(e).trim())) return D(e); // already a full title
    var a = String(e).replace(/^(TEH|NT|GIR|GD|GQ|GR|PAT|PT)/i, "");
    return (
      t +
      ((a = a.charAt(0).toUpperCase() + a.slice(1).toLowerCase())
        ? " " + a
        : "")
    );
  }
  function Z(e) {
    return e
      ? new Date(e).toLocaleDateString("en-IN", {
          day: "2-digit",
          month: "short",
        })
      : "";
  }
  // An officer's remark field (bottom of the page) is filled although Members Remarks has no entry yet
  function rpFieldDone(o, role) {
    var v = "Girdawar" === role ? o.gir : "Naib Tehsildar" === role ? o.nt : null;
    return !!v && !M(v) && !/^\s*report\s*pending/i.test(v) && D(v).length > 8;
  }
  function Q(e) {
    return e && e.ok
      ? e.history && e.history.length
        ? (function (e, t) {
            var a,
              r = e[e.length - 1],
              n = X(r.by),
              i = r.remark,
              o = /revert|reject|return|mismatch|deficien|not legible/i;
            a =
              "Patwari" === n
                ? "Girdawar"
                : "Girdawar" === n
                  ? "Naib Tehsildar"
                  : "Naib Tehsildar" === n
                    ? /patwari[^.]{0,60}\bdirected\b|\bdirected\b[^.]{0,60}patwari/i.test(
                        i,
                      )
                      ? "Patwari"
                      : "Tehsildar"
                    : "Tehsildar" === n
                      ? ae(i)
                        ? "Applicant"
                        : "Patwari"
                      : "";
            var fieldNote = "";
            for (var hop = 0; hop < 2; hop++) {
              if ("Girdawar" === a && t && rpFieldDone(t, "Girdawar"))
                (a = "Naib Tehsildar"), (fieldNote = "Girdawar");
              else if ("Naib Tehsildar" === a && t && rpFieldDone(t, "Naib Tehsildar"))
                (a = "Tehsildar"), (fieldNote = "Naib Tehsildar");
            }
            for (
              var s =
                  "Applicant" === a
                    ? "Returned to applicant"
                    : a
                      ? "With " + a
                      : "Unknown holder",
                l = a,
                d = e.length - 1;
              d >= 0;
              d--
            )
              if (X(e[d].by) === a) {
                l = Y(e[d].by);
                break;
              }
            for (var c = 0, p = 1; p < e.length; p++) {
              var u = X(e[p - 1].by),
                f = X(e[p].by);
              ("Naib Tehsildar" !== u && "Girdawar" !== u) ||
                "Patwari" !== f ||
                c++,
                "Tehsildar" === f && ae(e[p].remark) && c++;
            }
            for (var h = [], v = -1, m = e.length - 1; m >= 0; m--)
              if ("Tehsildar" === X(e[m].by)) {
                v = m;
                break;
              }
            var g = e.slice(v + 1).filter(function (e) {
              var t = X(e.by);
              return "Girdawar" === t || "Naib Tehsildar" === t;
            });
            t &&
              t.patTopPending &&
              g.length &&
              h.push(
                "Error: " +
                  Y(g[0].by) +
                  " acted but Patwari report is “Report Pending”",
              );
            c && h.push("Sent back " + c + "×");
            fieldNote &&
              h.push(fieldNote + " remark is on the page but not yet in Members Remarks — treated as done");
            "Tehsildar" !== n &&
              o.test(i) &&
              h.push(Y(r.by) + " suggests revert/rejection");
            var b = "Tehsildar" === X(e[0].by) ? e.slice(1) : e.slice(),
              y = b.length ? b[b.length - 1] : null;
            return {
              level: fieldNote ? fieldNote : y ? X(y.by) || "Other" : "None",
              levelBy: fieldNote ? fieldNote : y ? Y(y.by) : "",
              levelT: fieldNote ? 0 : y ? y.t : 0,
              stage: s,
              holder: l,
              flag: h.join("; "),
              lastBy: Y(r.by),
              lastT: r.t,
              lastRemark: i,
              patReport: t ? (t.patTopPending ? "Pending" : "Submitted") : "",
              stageDays: r.t
                ? Math.max(0, Math.floor((Date.now() - r.t) / 864e5))
                : null,
              history: e.map(function (e) {
                return { by: Y(e.by), remark: e.remark, t: e.t, date: e.date };
              }),
            };
          })(e.history, e)
        : (function (e) {
            "patTopPending" in e &&
              (e = Object.assign({}, e, {
                pat: e.patTopPending
                  ? "Report Pending"
                  : M(e.pat)
                    ? "Report submitted"
                    : e.pat,
              }));
            var t = [
                ["Patwari", "pat"],
                ["Girdawar", "gir"],
                ["Naib Tehsildar", "nt"],
                ["Tehsildar", "teh"],
              ].filter(function (t) {
                return t[1] in e;
              }),
              a = -1;
            t.forEach(function (t, r) {
              M(e[t[1]]) || (a = r);
            });
            var r,
              n = [];
            e.patTopPending &&
              t.slice(1).some(function (t) {
                return !M(e[t[1]]);
              }) &&
              n.push(
                "Error: later officer acted but Patwari report is “Report Pending”",
              );
            r =
              a + 1 < t.length
                ? "With " + t[a + 1][0]
                : "teh" in e
                  ? "Tehsildar acted"
                  : "With Tehsildar";
            e.fresh &&
              n.push("New application — not yet forwarded by the Tehsildar (no movement yet)");
            return {
              stage: r,
              flag: n.join("; "),
              patReport: e.fresh ? "Not yet sent" : e.patTopPending ? "Pending" : "Submitted",
            };
          })(e)
      : { stage: "Could not read", flag: "" };
  }
  function ee() {
    var e = { pat: 5, gir: 7, nt: 9, mode: "app" };
    try {
      Object.assign(e, JSON.parse(localStorage.getItem(s) || "{}"));
    } catch (e) {}
    return "stage" !== e.mode && (e.mode = "app"), e;
  }
  function te(e) {
    return (
      (e = String(e || "")),
      /^Naib Tehsildar/i.test(e)
        ? "Naib Tehsildar"
        : /^Tehsildar/i.test(e)
          ? "Tehsildar"
          : /^Patwari/i.test(e)
            ? "Patwari"
            : /^Girdawar/i.test(e)
              ? "Girdawar"
              : X(e)
    );
  }
  function ae(e) {
    return !/process\s*under\s*rules|forward|marked\s*to|to\s*(the\s*)?patwari/i.test(
      e || "",
    );
  }
  function re(e, t) {
    return "Patwari" === e
      ? c.village[t.village || "—"] || c.role.Patwari || e
      : c.role[e] || e;
  }
  function ne(e) {
    return (
      e.getFullYear() +
      "-" +
      ("0" + (e.getMonth() + 1)).slice(-2) +
      "-" +
      ("0" + e.getDate()).slice(-2)
    );
  }
  function ie(e, t) {
    var a =
        u ||
        ((u = {}),
        (ee().holidays || p).forEach(function (e) {
          u[e] = 1;
        }),
        u),
      r = 0,
      n = new Date(e);
    n.setHours(0, 0, 0, 0);
    var i = new Date(t);
    i.setHours(0, 0, 0, 0);
    for (var o = 0; n < i && o < 3e3; o++)
      n.setDate(n.getDate() + 1), 0 === n.getDay() || a[ne(n)] || r++;
    return r;
  }
  function oe(e) {
    var t = String(e.appDate || "").split("/"),
      a = J(t[0] || ""),
      r = J(t[1] || "");
    return {
      applied: a,
      resub: r && r >= a ? r : 0,
      base: r && r >= a ? r : a,
    };
  }
  function se() {
    if (v) return v;
    try {
      v = JSON.parse(localStorage.getItem(h) || "{}");
    } catch (e) {
      v = {};
    }
    return v;
  }
  function le(e) {
    var t = oe(e);
    return e.appNo + "|" + (t.base ? ne(new Date(t.base)) : "");
  }
  function de(e, t) {
    var a = se();
    e.forEach(function (e) {
      if ("Pending" === e.patReport || "Submitted" === e.patReport) {
        var r = le(e),
          n = (a[r] = a[r] || {});
        "Pending" === e.patReport
          ? n.sub || (n.pend = Math.max(n.pend || 0, t))
          : n.sub || (n.sub = t),
          (n.touch = t);
      }
    });
    var r = t - 200 * l;
    Object.keys(a).forEach(function (e) {
      (a[e].touch || 0) < r && delete a[e];
    });
    try {
      localStorage.setItem(h, JSON.stringify(a));
    } catch (e) {}
  }
  function ce(e, t) {
    var a = e.history || [];
    t = t || ee();
    var r,
      n,
      i,
      o = ((r = new Date()).setHours(0, 0, 0, 0), r.getTime()),
      s = [],
      l = oe(e);
    if ("stage" !== t.mode && l.base) {
      var c = [];
      c.push({ base: l.base, end: 0, earlier: !1 });
      var p = "Returned to applicant" === e.stage;
      c.forEach(function (r) {
        f.forEach(function (n) {
          for (var i = +t[d[n]], c = null, u = 0; u < a.length; u++) {
            var f = a[u].t;
            if (
              f &&
              f >= r.base &&
              (!r.end || f < r.end) &&
              te(a[u].by) === n
            ) {
              c = a[u];
              break;
            }
          }
          var h = { role: n, from: r.base, limit: i, earlier: r.earlier };
          if (c)
            (h.to = c.t),
              (h.by = c.by),
              (h.acted = !0),
              (h.days = ie(r.base, c.t)),
              (h.over = Math.max(0, h.days - i)),
              (h.status = h.over ? "late" : "ontime");
          else if (!r.earlier && rpFieldDone(e, n))
            (h.by = re(n, e)),
              (h.acted = !0),
              (h.days = null),
              (h.over = 0),
              (h.status = "reported"),
              (h.note = "remark recorded on the application page; its date is not yet in Members Remarks");
          else if ("Patwari" !== n || r.earlier || "Submitted" !== e.patReport)
            r.earlier
              ? ((h.by = re(n, e)),
                (h.status = "notreached"),
                (h.days = null),
                (h.over = 0))
              : p
                ? ((h.by = re(n, e)),
                  (h.status = "stopped"),
                  (h.days = null),
                  (h.over = 0))
                : ((h.open = !0),
                  (h.by = re(n, e)),
                  (h.days = ie(r.base, o)),
                  (h.over = Math.max(0, h.days - i)),
                  (h.left = Math.max(0, i - h.days)),
                  (h.status = h.over ? "overdue" : "running"));
          else {
            (h.by = re(n, e)), (h.acted = !0), (h.days = null), (h.over = 0);
            var v = se()[le(e)] || {};
            if (v.sub && v.pend && v.pend < v.sub) {
              var m = ie(r.base, v.pend),
                g = ie(r.base, v.sub);
              (h.to = v.sub),
                (h.days = g),
                (h.est = !0),
                (h.note =
                  "report found in scan of " +
                  Z(v.sub) +
                  "; still pending in scan of " +
                  Z(v.pend)),
                g <= i
                  ? (h.status = "ontime")
                  : m >= i
                    ? ((h.status = "late"),
                      (h.over = m + 1 - i),
                      (h.overMax = g - i))
                    : ((h.status = "reported"),
                      (h.note +=
                        " — submitted between day " +
                        (m + 1) +
                        " and day " +
                        g +
                        ", so it may or may not be late"));
            } else
              (h.status = "reported"),
                (h.note =
                  "report is in; date unknown, because no earlier scan in this round saw it pending");
          }
          "Patwari" !== n ||
            r.earlier ||
            (h.acted &&
              "Pending" === e.patReport &&
              (h.note = "comment only, report still pending"),
            h.open &&
              (h.note =
                "Pending" === e.patReport
                  ? "no report or comment yet"
                  : l.resub
                    ? "no report or comment since resubmission"
                    : "report filled, no comment yet")),
            s.push(h);
        });
      });
      var u = null;
      if (
        (s.forEach(function (e) {
          !e.earlier &&
            e.open &&
            (u
              ? ((e.open = !1),
                (e.status = "waiting"),
                (e.waitFor = u.role),
                (e.over = 0),
                (e.left = null),
                (e.days = null),
                delete e.note)
              : (u = e));
        }),
        u && "overdue" === u.status)
      ) {
        var h = s.indexOf(u),
          v = h > 0 ? s[h - 1] : null;
        v &&
          v.acted &&
          null != v.days &&
          v.days > u.limit &&
          ((u.inherited = !0),
          (u.cause = (v.by || v.role) + " acted only on day " + v.days));
      }
      return pe(s, {
        mode: "app",
        base: l.base,
        resub: l.resub,
        dayNow: ie(l.base, o),
        stopped: p,
      });
    }
    if (!a.length || !a[0].t) return null;
    for (var m = 0; m < a.length; m++) {
      var g = te(a[m].by),
        b =
          ((n = g),
          (i = a[m].remark),
          "Patwari" === n
            ? "Girdawar"
            : "Girdawar" === n
              ? "Naib Tehsildar"
              : "Naib Tehsildar" === n
                ? /patwari[^.]{0,60}\bdirected\b|\bdirected\b[^.]{0,60}patwari/i.test(
                    i,
                  )
                  ? "Patwari"
                  : "Tehsildar"
                : "Tehsildar" === n
                  ? ae(i)
                    ? "Applicant"
                    : "Patwari"
                  : ""),
        y = d[b];
      if (y && a[m].t) {
        var w = a[m].t,
          x = +t[y],
          k = a[m + 1],
          A = { role: b, from: w, limit: x };
        k && k.t
          ? ((A.to = k.t),
            (A.acted = te(k.by) === b),
            (A.days = ie(w, k.t)),
            (A.over = Math.max(0, A.days - x)),
            (A.by = k.by),
            (A.status = A.acted ? (A.over ? "late" : "ontime") : "moved"),
            A.acted ||
              ((A.note =
                k.by + " acted on " + Z(k.t) + " without a " + b + " entry"),
              (A.by = re(b, e)),
              (A.over = 0)))
          : ((A.open = !0),
            (A.days = ie(w, o)),
            (A.over = Math.max(0, A.days - x)),
            (A.left = Math.max(0, x - A.days)),
            (A.status = A.over ? "overdue" : "running"),
            (A.by =
              e.holder && te(e.holder) === b && e.holder !== b
                ? e.holder
                : re(b, e)),
            "Patwari" === b &&
              (A.note =
                "Pending" === e.patReport
                  ? "no report or comment yet"
                  : "report filled, not yet forwarded")),
          s.push(A);
      }
    }
    return pe(s, { mode: "stage" });
  }
  function pe(e, t) {
    var a = e.filter(function (e) {
        return e.open;
      }),
      r = e.filter(function (e) {
        return "late" === e.status;
      }),
      n = {
        visits: e,
        open: a,
        overdue: a.filter(function (e) {
          return "overdue" === e.status;
        }),
        late: r,
        lateDays: r.reduce(function (e, t) {
          return e + t.over;
        }, 0),
        acted: e.filter(function (e) {
          return e.acted && "reported" !== e.status;
        }).length,
        ontime: e.filter(function (e) {
          return "ontime" === e.status;
        }).length,
      };
    return (n.cur = n.overdue[0] || a[0] || null), Object.assign(n, t);
  }
  function rpFetch(u, o) {
    o = o || {};
    if (window.AbortController && !o.signal) {
      var ac = new AbortController();
      (o.signal = ac.signal),
        setTimeout(function () {
          ac.abort();
        }, 9e4);
    }
    return fetch(u, o);
  }
  async function ue(e, t, a, r) {
    var n = K(e);
    a.forEach(function (e) {
      n.set(e[0], e[1]);
    });
    var i = new URL(e.getAttribute("action") || t, t).href,
      o = await rpFetch(i, {
        method: "POST",
        body: n,
        credentials: "include",
        redirect: "follow",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      }),
      s = await o.text(),
      l = o.url,
      d = { status: o.status, url: l, html: s, followed: "" };
    if (!r && !/Remarks\s*:|Members\s*Remarks/i.test(s)) {
      var c =
        /['"]([^'"\s<>]*Approve[A-Za-z]*\.aspx[^'"\s<>]*)['"]/i.exec(s) ||
        /(?:location\.href|location\.replace|window\.location|window\.open)\s*(?:=|\()\s*['"]([^'"]+\.aspx[^'"]*)['"]/i.exec(
          s,
        ) ||
        /pageRedirect\|\|([^|]+)\|/i.exec(s);
      if (c) {
        var p = new URL(decodeURIComponent(c[1]).replace(/&amp;/g, "&"), l)
            .href,
          u = await rpFetch(p, { credentials: "include" });
        (s = await u.text()),
          (l = u.url),
          (d.followed = "HTTP " + u.status + " " + new URL(l).pathname);
      }
    }
    return { html: s, url: l, diag: d };
  }
  function fe(e) {
    function t(e) {
      return D(e).replace(/\d{6,}/g, "XXXXX");
    }
    var a = e.diag,
      r = j(a.html),
      n = Array.prototype.map
        .call(r.querySelectorAll("script:not([src])"), function (e) {
          return e.textContent;
        })
        .filter(function (e) {
          return /location|open\(|\.aspx|alert/i.test(e);
        })
        .map(t)
        .join(" ¦ ")
        .slice(0, 300),
      i = t(r.body ? r.body.textContent : ""),
      o =
        /[^.]{0,60}(error|invalid|expired|not authori[sz]ed|unauthori[sz]ed|denied|exception|login|try again)[^.]{0,120}/i.exec(
          i,
        ),
      s = o ? "message: " + D(o[0]) : i.slice(0, 220);
    return (
      "HTTP " +
      a.status +
      " " +
      new URL(a.url).pathname +
      (a.followed ? " → " + a.followed : "") +
      " · title: " +
      t(r.title || "—") +
      " · has list: " +
      (/application\s*no/i.test(a.html) ? "yes" : "no") +
      (n ? " · scripts: " + n : "") +
      " · text: " +
      s +
      (e.html !== a.html
        ? " · final text: " +
          t(j(e.html).body ? j(e.html).body.textContent : "").slice(0, 220)
        : "")
    );
  }
  function he(e) {
    return (
      Array.prototype.find.call(e.querySelectorAll("select"), function (e) {
        return Array.prototype.some.call(e.options, function (e) {
          return /fard/i.test(e.text);
        });
      }) || e.querySelector("select")
    );
  }
  function ve(e) {
    return Array.prototype.find.call(
      e.querySelectorAll("input[type=submit],button"),
      function (e) {
        return /^\s*view\s*$/i.test(e.value || e.textContent || "");
      },
    );
  }
  function me() {
    x ||
      ((x = j(document.documentElement.outerHTML)),
      (document.head.innerHTML =
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Revenue Plus Tracker</title>'),
      (document.body.innerHTML = ""),
      document.body.removeAttribute("class"),
      document.body.setAttribute("style", "margin:0;background:#f4f5f7"),
      document.body.appendChild(b),
      window.scrollTo(0, 0)),
      ge();
  }
  function ge(manual) {
    setTimeout(rpVersionBadge, 0);
    manual === !0 && rpReg && (rpReg.gen++, (rpReg.on = !1));
    var e = x.forms[0],
      a = G(x),
      r = e && he(e),
      n = r
        ? r.options[r.selectedIndex] && r.options[r.selectedIndex].text
        : "",
      i = null;
    try {
      i = JSON.parse(localStorage.getItem(t) || "null");
    } catch (e) {}
    var rpU = rpScanLoad(),
      rpUS = rpU && rpU.plan ? rpScanStats(rpU) : null,
      rpCard =
        !rpUS || (rpUS.complete && !rpUS.errs)
          ? ""
          : '<div class="card" style="border:2px solid #1b4a7a"><h3>Unfinished scan</h3><p class="muted" style="margin:0 0 8px">Started ' +
            L(new Date(rpU.started).toLocaleString("en-IN")) +
            (rpU.allTypes ? " · all service types" : "") +
            " · <b>" + rpUS.read + " of " + rpUS.N + "</b> applications read · <b>" + rpUS.setsDone + " of " + rpUS.S + "</b> sets of " + 10 + " complete.</p>" +
            (rpUS.errs ? '<p class="muted" style="margin:0 0 8px;color:#8a5300">' + rpUS.errs + " could not be read and will be retried:</p>" + rpUnreadHtml(rpU) : "") +
            (rpU.lastRun ? '<p class="muted" style="margin:6px 0 8px">Last run: ' + L(rpU.lastRun) + "</p>" : "") +
            '<div class="tools"><button class="pri" id="rpresume">' +
            (rpUS.complete ? "Retry " + rpUS.errs + " unread" : "Resume scan (" + (rpUS.N - rpUS.read + rpUS.errs) + " left)") +
            '</button><button id="rpsofar">Show results so far</button></div><p class="muted" style="margin:8px 0 0">Starting a new scan below discards this unfinished one.</p></div>';
    // v1.9.9: straight into the register — saved applications at once, new ones prepared in the background
    if (manual !== !0 && !rpCard && e && a.length && window.__rpApiBase) {
      w.innerHTML = '<div class="card"><h3>Opening the register …</h3></div>';
      return void setTimeout(function () {
        rpRegisterOpen(i); // after the rest of the tracker has initialised
      }, 0);
    }
    setTimeout(function () {
      rpSyncOffer(i && i.at);
    }, 0);
    function rpBindResume() {
      var rb = y.getElementById("rpresume");
      rb &&
        (rb.onclick = function () {
          rpResume();
        });
      var dl2 = y.getElementById("rpdiagdl");
      dl2 &&
        (dl2.onclick = function (ev) {
          ev.preventDefault(), rpDiagDownload();
        });
      var sf = y.getElementById("rpsofar");
      sf &&
        (sf.onclick = function () {
          Ne({ at: rpU.at || Date.now(), items: rpOrdered(rpU), partial: !0 });
        });
    }
    if (e && (a.length || r)) {
      w.innerHTML =
        rpCard +
        '<div id="rpsynccard"></div>' +
        '<div class="card"><h3>' + (rpCard ? "Or start a new scan" : "Scan pending applications") + '</h3>' + (i ? '<div class="tools" style="margin:0 0 8px"><button class="pri" id="rpopenreg" style="background:#5b3fa8">Open the register (saved applications at once, only new ones prepared)</button></div>' : "") + '<p class="muted">The tracker presses “Process” for each application in the background, only to read the Patwari, Girdawar and Naib Tehsildar remarks. It never types remarks or presses Submit.</p><div class="tools"><button class="pri" id="one">Scan this list' +
        (n ? " (" + L(n) + ")" : "") +
        " — " +
        a.length +
        " applications (" + Math.max(1, Math.ceil(a.length / 10)) + " sets)</button>" +
        (r ? '<button id="all">Scan all service types</button>' : "") +
        '</div></div><div class="card warn"><b>Before you start:</b> close any other Revenue Plus tab where an application is open. When you are done, tap <b>×</b> — it reloads the Dashboard. Always reload before processing an application, because the portal remembers the last application opened.</div>' +
        (i
          ? '<div class="card"><div class="tools"><span>Last scan: <b>' +
            L(new Date(i.at).toLocaleString()) +
            "</b> — " +
            i.items.length +
            ' applications</span><button id="showlast">Show last scan</button></div></div>'
          : "");
      var orb = y.getElementById("rpopenreg");
      orb &&
        (orb.onclick = function () {
          rpRegisterOpen(i);
        });
      var o = y.getElementById("one");
      o &&
        (o.onclick = function () {
          Se(!1);
        });
      var s = y.getElementById("all");
      s &&
        (s.onclick = function () {
          Se(!0);
        });
      var l = y.getElementById("showlast");
      l &&
        (l.onclick = function () {
          Ne(i), rpStartBackground(i.items);
        });
      rpBindResume();
    } else {
      w.innerHTML =
        rpCard +
        '<div id="rpsynccard"></div>' +
        '<div class="card warn"><b>No application list found.</b><br>Open the Revenue Plus <b>Dashboard</b>, choose a Service Type, press <b>View</b>, then run Tracker again.</div>' +
        (i
          ? '<div class="card"><button id="showlast">Show last scan (' +
            L(new Date(i.at).toLocaleString()) +
            ")</button></div>"
          : "");
      var d = y.getElementById("showlast");
      d &&
        (d.onclick = function () {
          Ne(i), rpStartBackground(i.items);
        });
      rpBindResume();
    }
  }
  function be(e, t, a) {
    (w.innerHTML =
      '<div class="card"><h3>' +
      L(e) +
      '</h3><div class="prog"><i style="width:' +
      (a ? Math.round((t / a) * 100) : 0) +
      '%"></i></div><div class="muted">' +
      t +
      " of " +
      a +
      ' read. Keep this tab open.</div><div class="tools" style="margin-top:10px"><button id="stop">Stop</button></div></div>'),
      (y.getElementById("stop").onclick = function () {
        T = !0;
      });
  }
  async function ye(e, t) {
    var a = await rpFetch(k.split("#")[0], { credentials: "include" }),
      r = a.url,
      rawDash = await a.text(),
      bytes = rawDash.length,
      n = j(rawDash);
    if (we(n, r)) return { why: "logout" };
    var i = function (t) {
        return G(t).filter(function (t) {
          return D(t.appNo) === D(e);
        })[0];
      },
      o = i(n);
    if (!o && t && n.forms[0]) {
      var s = n.forms[0],
        l = he(s),
        d = ve(s);
      if (l && d) {
        var c = await ue(
          s,
          r,
          [
            [l.name, t],
            [d.name, d.value || "View"],
          ],
          !0,
        );
        if (((bytes += c.html.length), (rawDash = c.html), (r = c.url), !(o = i((n = j(c.html)))) && we(n, r)))
          return { why: "logout" };
      }
    }
    return o
      ? { row: o, baseUrl: r, bytes: bytes, dash: rawDash }
      : {
          why: G(n).length ? "gone" : "nolist",
          bytes: bytes,
          dash: rawDash,
          detail: fe({
            html: n.documentElement.outerHTML,
            diag: {
              status: a.status,
              url: r,
              html: n.documentElement.outerHTML,
              followed: "",
            },
          }),
        };
  }
  function we(e, t) {
    return (
      !!e.querySelector("input[type=password]") ||
      (/login|signin|sessionexpired|default\.html/i.test(new URL(t).pathname) &&
        !/App\/Default\.aspx/i.test(t))
    );
  }
  async function xe(e, t, a) {
    var r = K(e);
    a.forEach(function (e) {
      r.set(e[0], e[1]);
    });
    var n = new URL(e.getAttribute("action") || t, t).href;
    return fetch(n, {
      method: "POST",
      body: r,
      credentials: "include",
      redirect: "follow",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  }
  function ke(e) {
    return Array.prototype.map.call(
      e.querySelectorAll(
        "iframe[src],embed[src],object[data],img[src],a[href]",
      ),
      function (e) {
        return {
          tag: e.tagName,
          src:
            e.getAttribute("src") ||
            e.getAttribute("data") ||
            e.getAttribute("href") ||
            "",
        };
      },
    );
  }
  async function Ae(e, t, a) {
    var r = (e.headers.get("content-type") || "").toLowerCase();
    if (!/text\/html/.test(r)) {
      var n = e.headers.get("content-disposition") || "",
        i = /filename\*?=(?:UTF-8'')?["']?([^"';]+)/i.exec(n);
      return {
        blob: await e.blob(),
        type: r.split(";")[0],
        name: i ? decodeURIComponent(i[1]) : "",
      };
    }
    var o = await e.text(),
      s = j(o),
      l = e.url,
      d = {};
    (t || []).forEach(function (e) {
      d[e.src] = 1;
    });
    var c = ke(s).filter(function (e) {
        return (
          e.src &&
          !d[e.src] &&
          !/^(javascript:|#|mailto:)/i.test(e.src) &&
          !/logo|emblem|banner|icon/i.test(e.src) &&
          ("A" !== e.tag ||
            /\.(pdf|jpe?g|png|gif|tiff?|zip)(\?|$)|\.ashx|handler|download|viewdoc|getdoc|file/i.test(
              e.src,
            ))
        );
      }),
      p =
        c.filter(function (e) {
          return "A" !== e.tag && "IMG" !== e.tag;
        })[0] ||
        c.filter(function (e) {
          return "IMG" === e.tag;
        })[0] ||
        c[0],
      u = p && p.src;
    if (!u) {
      var f = ke(s).filter(function (e) {
        return (
          "A" !== e.tag &&
          "IMG" !== e.tag &&
          e.src &&
          !/^(about:|javascript:)/i.test(e.src)
        );
      });
      f.length && (u = f[f.length - 1].src);
    }
    if (!u) {
      var h =
        /(?:window\.open|location\.href\s*=|location\.replace)\s*\(?\s*['"]([^'"]+)['"]/i.exec(
          o,
        );
      h && (u = h[1]);
    }
    if (!u)
      throw new Error(
        "The portal did not return a document. " +
          fe({
            html: o,
            diag: { status: e.status, url: l, html: o, followed: "" },
          }),
      );
    if (/^data:/i.test(u)) {
      var v = await (await fetch(u)).blob();
      return { blob: v, type: v.type, name: "" };
    }
    if (a > 2)
      throw new Error("Too many redirects while opening the document.");
    return Ae(
      await fetch(new URL(u.replace(/&amp;/g, "&"), l).href, {
        credentials: "include",
      }),
      ke(s),
      a + 1,
    );
  }
  function Te(e) {
    function t(e) {
      return D(e)
        .replace(/\d{8,}/g, "XXXXX")
        .slice(0, 160);
    }
    return (
      "<" +
      e.tagName.toLowerCase() +
      (e.getAttribute("type") ? " type=" + e.getAttribute("type") : "") +
      (e.name ? " name=" + t(e.name) : "") +
      (e.getAttribute("href") ? " href=" + t(e.getAttribute("href")) : "") +
      (e.getAttribute("onclick")
        ? " onclick=" + t(e.getAttribute("onclick"))
        : "") +
      (e.getAttribute("data-url") || e.getAttribute("data-src")
        ? " data=" + t(e.getAttribute("data-url") || e.getAttribute("data-src"))
        : "") +
      ">"
    );
  }
  function Pe(e, t, a) {
    var r =
        (e.getAttribute("onclick") || "") +
        " " +
        (e.getAttribute("href") || ""),
      n = e.getAttribute("data-url") || e.getAttribute("data-src");
    if (n) return new URL(n, a).href;
    var i = [];
    r.replace(/['"]([^'"]{3,})['"]/g, function (e, t) {
      i.push(t);
    });
    var o = i.filter(function (e) {
        return /[\/\\].*\.\w{2,4}$|\.(pdf|jpe?g|png|tiff?)$|\.as[hp]x/i.test(e);
      })[0],
      s = /([A-Za-z_$][\w$]*)\s*\(/.exec(
        r.replace(/^javascript:/i, "").replace(/return\s+/i, ""),
      ),
      l = "";
    s &&
      Array.prototype.forEach.call(
        t.querySelectorAll("script:not([src])"),
        function (e) {
          var t = e.textContent.indexOf("function " + s[1]);
          t >= 0 && (l = e.textContent.slice(t, t + 2e3));
        },
      );
    var d = /['"]([^'"]*\.(?:aspx|ashx)[^'"]*?)['"]/i.exec(l),
      c =
        /getElementById\(\s*['"]([^'"]+)['"]\s*\)\.value|\$\(\s*['"]#([^'"]+)['"]\s*\)\.val\(\)/.exec(
          l,
        ),
      p = c
        ? (t.getElementById(c[1] || c[2]) || {}).value ||
          (
            t.getElementById(c[1] || c[2]) || {
              getAttribute: function () {
                return "";
              },
            }
          ).getAttribute("value")
        : "",
      u = o || p || i[0] || "",
      f = d
        ? d[1] + (u && !/\.(pdf|jpe?g|png)$/i.test(d[1]) ? u : "")
        : o || "";
    return f
      ? new URL(f.replace(/^~\//, "/revenueplus/").replace(/\\/g, "/"), a).href
      : "";
  }
  // Open the application page ONCE and take every document from it (one list + one page load per application,
  // instead of per document). Any document that fails this way is fetched again the old way.
  async function rpDetailOpen(e) {
    var a = await ye(e.appNo, e.svc);
    if (!a.row) throw new Error(E[a.why] + ("nolist" === a.why && a.detail ? " Details: " + a.detail : ""));
    var r = await ue(a.row.form, a.baseUrl, [[a.row.btnName, a.row.btnValue]]),
      n = j(r.html);
    return { r: r, n: n, allb: F(n) };
  }
  async function rpDetailDoc(dt, t, lab) {
    var r = dt.r,
      n = dt.n,
      allb = dt.allb,
      byLab = lab
        ? allb.filter(function (b) {
            return D($(b)).toLowerCase() === D(lab).toLowerCase();
          })
        : [],
      i = byLab.length === 1 ? byLab[0] : allb[t] || byLab[0];
    if (!i) throw new Error("document button not found");
    var o,
      s = i.form || i.closest("form") || n.forms[0],
      l = i.getAttribute("href") || "",
      d = i.getAttribute("onclick") || "",
      c =
        /__doPostBack\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]*)['"]/.exec(l + " " + d) ||
        /WebForm_PostBackOptions\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]*)['"]/.exec(l + " " + d),
      p = /open\(\s*['"]([^'"]+)['"]/.exec(d);
    if (c) o = await xe(s, r.url, [["__EVENTTARGET", c[1]], ["__EVENTARGUMENT", c[2]]]);
    else if ("A" === i.tagName && l && !/^(javascript:|#)/i.test(l)) o = await fetch(new URL(l, r.url).href, { credentials: "include" });
    else if (p) o = await fetch(new URL(p[1], r.url).href, { credentials: "include" });
    else if (i.name) o = await xe(s, r.url, [[i.name, i.value || ""]]);
    else {
      var u = Pe(i, n, r.url);
      u && (o = await fetch(u, { credentials: "include" }));
    }
    if (!o) throw new Error("unrecognised document button");
    return await Ae(o, ke(n), 0);
  }
  // portal access one at a time (background prefetch and your own request never hit the portal together)
  var rpPortalQ = Promise.resolve();
  function rpPortal(fn) {
    var p = rpPortalQ.then(fn, fn);
    rpPortalQ = p.then(
      function () {},
      function () {},
    );
    return p;
  }
  async function Ee(e, t, lab) {
    if (A) throw new Error("A scan is reading the portal right now — wait for it to finish (or stop it), then open documents.");
    var a = await ye(e.appNo, e.svc);
    if (!a.row)
      throw new Error(
        E[a.why] +
          ("nolist" === a.why && a.detail ? " Details: " + a.detail : ""),
      );
    var r = await ue(a.row.form, a.baseUrl, [[a.row.btnName, a.row.btnValue]]),
      n = j(r.html),
      allb = F(n),
      byLab = lab
        ? allb.filter(function (b) {
            return D($(b)).toLowerCase() === D(lab).toLowerCase();
          })
        : [],
      i = byLab.length === 1 ? byLab[0] : allb[t] || byLab[0];
    if (!i)
      throw new Error(
        "Could not find this document button on the application page (" +
          allb.length +
          " document buttons found: " +
          allb.map($).join(", ") +
          ").",
      );
    var o,
      s = i.form || i.closest("form") || n.forms[0],
      l = i.getAttribute("href") || "",
      d = i.getAttribute("onclick") || "",
      c =
        /__doPostBack\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]*)['"]/.exec(
          l + " " + d,
        ) ||
        /WebForm_PostBackOptions\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]*)['"]/.exec(
          l + " " + d,
        ),
      p = /open\(\s*['"]([^'"]+)['"]/.exec(d);
    if (c)
      o = await xe(s, r.url, [
        ["__EVENTTARGET", c[1]],
        ["__EVENTARGUMENT", c[2]],
      ]);
    else if ("A" === i.tagName && l && !/^(javascript:|#)/i.test(l))
      o = await fetch(new URL(l, r.url).href, { credentials: "include" });
    else if (p)
      o = await fetch(new URL(p[1], r.url).href, { credentials: "include" });
    else if (i.name) o = await xe(s, r.url, [[i.name, i.value || ""]]);
    else {
      var u = Pe(i, n, r.url);
      u && (o = await fetch(u, { credentials: "include" }));
    }
    if (!o)
      throw new Error(
        "This document button works in a way the tracker does not recognise yet. " +
          Te(i),
      );
    try {
      return await Ae(o, ke(n), 0);
    } catch (e) {
      throw new Error(e.message + " — Button: " + Te(i));
    }
  }
  // ───── Scan in sets of 10, saved after every application, resumable ─────
  var rpStopSet = !1; // set size and storage name are fixed values below (the start screen draws before vars initialise)
  function rpScanKey(e) {
    return (e.svc || "") + "|" + e.appNo;
  }
  function rpScanLoad() {
    try {
      return JSON.parse(localStorage.getItem("rpTrackerScan") || "null");
    } catch (x) {
      return null;
    }
  }
  function rpScanSave(r) {
    try {
      localStorage.setItem("rpTrackerScan", JSON.stringify(r));
    } catch (x) {
      try {
        // storage full: keep the status, drop the heavy per-application details
        r.items.forEach(function (e) {
          (e.docs = []), (e.mut = null), (e.adj = null), (e.fields = null);
        });
        localStorage.setItem("rpTrackerScan", JSON.stringify(r));
      } catch (q) {}
    }
  }
  function rpScanStats(r) {
    var N = r.plan.length,
      S = Math.max(1, Math.ceil(N / 10)),
      got = {},
      sets = [];
    r.items.forEach(function (e) {
      got[rpScanKey(e)] = e;
    });
    (r.gone || []).forEach(function (k) {
      got[k] = "gone";
    });
    for (var i = 0; i < S; i++) sets.push({ no: i + 1, n: 0, read: 0, err: 0, gone: 0 });
    r.plan.forEach(function (e, i) {
      var st = sets[Math.floor(i / 10)],
        g = got[rpScanKey(e)];
      st.n++;
      "gone" === g ? (st.read++, st.gone++) : g && (st.read++, g.err && st.err++);
    });
    sets.forEach(function (st) {
      st.complete = st.read === st.n;
    });
    var read = sets.reduce(function (a, st) {
      return a + st.read;
    }, 0);
    return {
      N: N, S: S, sets: sets, read: read,
      setsDone: sets.filter(function (st) { return st.complete; }).length,
      complete: read >= N,
      errs: r.items.filter(function (e) { return e.err; }).length,
    };
  }
  function rpOrdered(r) {
    var pos = {};
    r.plan.forEach(function (e, i) {
      pos[rpScanKey(e)] = i;
    });
    return r.items.slice().sort(function (a, b) {
      return pos[rpScanKey(a)] - pos[rpScanKey(b)];
    });
  }
  function rpShowResults(obj) {
    var wr = y.querySelector(".wrap"),
      top = wr ? wr.scrollTop : 0;
    Ne(obj);
    wr && (wr.scrollTop = top);
  }
  var rpDiag = null;
  function rpSpeed(r, left) {
    var tm = (r.timing || []).filter(function (x) {
      return x.tot;
    });
    if (!tm.length) return null;
    function sec(v) {
      return (v / 1e3).toFixed(1) + " s";
    }
    function kb(v) {
      return v >= 1048576 ? (v / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(v / 1024)) + " KB";
    }
    function avg(f) {
      return tm.reduce(function (a, x) { return a + x[f]; }, 0) / tm.length;
    }
    var last = tm[tm.length - 1],
      wd = tm.filter(function (x) { return x.db; }),
      dAvg = wd.length ? wd.reduce(function (a, x) { return a + x.d; }, 0) / wd.length : 0,
      dbAvg = wd.length ? wd.reduce(function (a, x) { return a + x.db; }, 0) / wd.length : 0,
      per = avg("tot"),
      mins = left ? Math.round((per * left) / 6e4) : 0;
    return {
      last: (last.db ? "Dashboard reload " + sec(last.d) + " (" + kb(last.db) + ") · " : "") + "application page " + sec(last.a) + " (" + kb(last.ab) + ")",
      avg:
        "average " + sec(per) + " per application (" + (per ? (6e4 / per).toFixed(1) : "–") + " per minute)" +
        (dAvg ? " — Dashboard reload " + sec(dAvg) + " (" + kb(dbAvg) + "), application page " + sec(avg("a")) + " (" + kb(avg("ab")) + ")" : ""),
      eta: left ? (mins < 1 ? "under a minute left" : "about " + mins + " min left") : "",
      slow: last.d + last.a > 3e4,
    };
  }
  function rpUnreadHtml(r) {
    var un = r.items.filter(function (x) {
      return x.err;
    });
    if (!un.length) return "";
    var by = {};
    un.forEach(function (x) {
      var k = x.errWhy || "could not be read";
      (by[k] = by[k] || []).push(x.appNo);
    });
    return (
      '<div style="font-size:12px;color:#5b6475;margin-top:4px">' +
      Object.keys(by)
        .map(function (k) {
          return "<b>" + by[k].length + "</b> — " + L(k) + ' <span style="font-size:11px">(' + L(by[k].slice(0, 4).join(", ")) + (by[k].length > 4 ? " …" : "") + ")</span>";
        })
        .join("<br>") +
      (rpDiag ? '<br><a href="#" id="rpdiagdl" style="color:#12355b;font-weight:600">Download diagnostic file</a> — send it to whoever maintains the tracker' : "") +
      "</div>"
    );
  }
  function rpDiagDownload() {
    var t = rpDiag;
    if (!t) return;
    function clean(h) {
      return String(h || "")
        .replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, "[email removed]")
        .replace(/\b\d{4}\s?\d{4}\s?\d{4}\b/g, "[number removed]")
        .replace(/\b[6-9]\d{9}\b/g, "[number removed]");
    }
    var txt =
      "Revenue Plus Tracker diagnostic\nApplication: " + t.app + "\nTime: " + t.at + "\nReason: " + t.why +
      "\nButton pressed: " + t.button + "\nFirst reply: " + t.firstUrl + "\nFinal page: " + t.finalUrl +
      (t.timing ? "\nTiming: dashboard " + t.timing.d + " ms / " + t.timing.db + " bytes, application page " + t.timing.a + " ms / " + t.timing.ab + " bytes" : "") +
      "\n\n===== DASHBOARD (reloaded before Process) =====\n" + clean(t.dash) +
      "\n\n===== FIRST REPLY AFTER PROCESS =====\n" + clean(t.first) +
      "\n\n===== FINAL PAGE =====\n" + clean(t.final),
      a = document.createElement("a");
    (a.href = URL.createObjectURL(new Blob([txt], { type: "text/plain" }))),
      (a.download = "tracker-diagnostic-" + t.app + ".txt"),
      document.body.appendChild(a),
      a.click(),
      a.remove();
  }
  function rpScanBar(r, setNo, inSet, msg, extra) {
    var b = y.getElementById("rpscanbar"),
      bar = y.querySelector(".bar");
    if (!b) return;
    b.style.top = (bar ? bar.offsetHeight : 0) + "px";
    if (null === r) return void (b.hidden = !0);
    var s = rpScanStats(r);
    b.hidden = !1;
    if (msg) {
      b.innerHTML =
        '<div style="max-width:1100px;margin:0 auto;padding:8px 14px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:13px"><b style="color:#8a5300;flex:1">' +
        L(msg) +
        '</b><button id="rpsbx" style="padding:6px 10px;font-size:12.5px">Hide</button>' + (extra ? '<div style="flex-basis:100%">' + extra + "</div>" : "") + "</div>";
      y.getElementById("rpsbx").onclick = function () {
        b.hidden = !0;
      };
      var dl = y.getElementById("rpdiagdl");
      dl &&
        (dl.onclick = function (ev) {
          ev.preventDefault(), rpDiagDownload();
        });
      return;
    }
    b.innerHTML =
      '<div style="max-width:1100px;margin:0 auto;padding:8px 14px"><div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px"><span><b style="color:#12355b">Scanning · Set ' +
      setNo + " of " + s.S + "</b> · application " + (inSet + 1) + " of " + s.sets[setNo - 1].n + " · " + s.read + " of " + s.N +
      ' read</span><span style="display:flex;gap:6px"><button id="rpstopset" style="padding:6px 10px;font-size:12.5px"' +
      (rpStopSet ? " disabled" : "") + ">" + (rpStopSet ? "Stopping after this set…" : "Stop after this set") +
      '</button><button id="rpstopnow" style="padding:6px 10px;font-size:12.5px">Stop now</button></span></div><div class="prog" style="height:6px;margin:6px 0"><i style="width:' +
      (s.N ? Math.round((s.read / s.N) * 100) : 0) +
      '%"></i></div>' +
      (function () {
        var sp = rpSpeed(r, s.N - s.read);
        return sp
          ? '<div style="font-size:11.5px;color:#4a5466;margin:0 0 6px;line-height:1.4">Last: ' + L(sp.last) + "<br>Speed: " + L(sp.avg) + (sp.eta ? " · <b>" + L(sp.eta) + "</b>" : "") +
              (sp.slow ? '<br><span style="color:#8a5300">The portal is responding slowly right now.</span>' : "") +
              (s.errs ? '<br><span style="color:#8a5300">' + s.errs + " could not be read so far — they are retried on Resume.</span>" : "") + "</div>"
          : "";
      })() +
      '<div style="display:flex;flex-wrap:wrap;gap:4px">' +
      s.sets
        .map(function (st) {
          var cur = st.no === setNo && !st.complete;
          return (
            '<span style="font-size:11px;padding:2px 7px;border-radius:10px;' +
            (st.complete ? "background:#e3f4ea;color:#145c36;font-weight:600" : cur ? "background:#12355b;color:#fff;font-weight:600" : "background:#eef1f6;color:#64708a") +
            '">' + (st.complete ? "✓ " : "") + "Set " + st.no + (cur ? " · " + inSet + "/" + st.n : "") + "</span>"
          );
        })
        .join("") +
      '</div><div class="muted" style="margin-top:4px">Results of each completed set appear below while the next set is read. Every application is saved as soon as it is read — if the scan stops, run Tracker again and tap Resume.</div></div>';
    y.getElementById("rpstopnow").onclick = function () {
      (T = !0), (this.textContent = "Stopping…"), (this.disabled = !0);
    };
    y.getElementById("rpstopset").onclick = function () {
      (rpStopSet = !0), (this.disabled = !0), (this.textContent = "Stopping after this set…");
    };
  }
  async function Se(a) {
    rpReg.gen++, (rpReg.on = !1);
    rpBG.gen++, (rpBG.queue = []), (rpBG.total = 0);
    if (!A) {
      (A = !0), (T = !1);
      var refs = {},
        plan = [];
      P = !1;
      try {
        var n = x.forms[0],
          i = [];
        if (a)
          for (
            var o = he(n),
              s = ve(n),
              l = Array.prototype.filter.call(o.options, function (e) {
                return e.value && "0" !== e.value && "-1" !== e.value && !/select/i.test(e.text);
              }),
              d = 0;
            d < l.length && !T;
            d++
          ) {
            be("Loading list: " + l[d].text, d, l.length);
            var c = [[o.name, l[d].value]];
            s && c.push([s.name, s.value || "View"]);
            var p = await ue(n, k, c, !0),
              u = j(p.html),
              f = G(u);
            i.push({ service: D(l[d].text), svc: l[d].value, rows: f, form: f.length ? f[0].form : u.forms[0], baseUrl: p.url }),
              u.forms[0] && ((o = he((n = u.forms[0])) || o), (s = ve(n) || s)),
              await C(e);
          }
        else {
          var h = he(n);
          i.push({ service: h ? h.options[h.selectedIndex].text : "", svc: h ? h.value : "", rows: G(x), form: n, baseUrl: k });
        }
        i.forEach(function (b) {
          b.rows.forEach(function (E) {
            var pl = {
              service: b.service, svc: b.svc || "", appNo: E.appNo, name: E.name, mobile: E.mobile, village: E.village,
              khasra: E.khasra, purpose: E.purpose, appDate: E.appDate, revert: E.revert, days: E.days,
            };
            plan.push(pl), (refs[rpScanKey(pl)] = { row: E, baseUrl: b.baseUrl });
          });
        });
      } catch (err) {
        return (
          (w.innerHTML =
            '<div class="card warn"><b>Scan stopped:</b> ' +
            L((err && err.message) || err) +
            "<br>Close this, make sure you are still logged in, and try again from the Dashboard.</div>"),
          void (A = !1)
        );
      }
      if (T) return (A = !1), void ge();
      var prog = { started: Date.now(), allTypes: !!a, plan: plan, items: [], gone: [] };
      rpScanSave(prog), (A = !1), await rpRunPlan(prog, refs);
    }
  }
  async function rpResume() {
    var r = rpScanLoad();
    if (!r || !r.plan) return ge();
    (r.items = r.items.filter(function (e) {
      return !e.err; // unread ones are tried again
    })),
      await rpRunPlan(r, {});
  }
  // Read one application from the portal: reload the Dashboard (unless its row is already in hand), press Process, parse the page.
  async function rpReadOne(E, memIn, first, tmArr, setNo) {
      var S = { ok: !1 },
        mem = memIn,
        gone = !1,
        tf = Date.now(),
        th = tf,
        tdb = 0,
        tab = 0,
        dashRaw = "";
      try {
        var R,
          Nn = null;
        if (!first || !mem) {
          Nn = await ye(E.appNo, E.svc);
          (th = Date.now()), (tdb = (Nn && Nn.bytes) || 0), (dashRaw = (Nn && Nn.dash) || "");
          if (Nn && "logout" === Nn.why) return { logout: !0 };
          if (Nn && "gone" === Nn.why) gone = !0;
          else if (!Nn.row) {
            if (!mem) throw new Error(E_MSG(Nn.why));
            Nn = null;
          }
        }
        if (!gone) {
          R = Nn
            ? await ue(Nn.row.form, Nn.baseUrl, [[Nn.row.btnName, Nn.row.btnValue]])
            : await ue(mem.row.form, mem.baseUrl, [[mem.row.btnName, mem.row.btnValue]]);
          tab = R.html.length;
          var tm = tmArr;
          tm.push({ d: th - tf, db: tdb, a: Date.now() - th, ab: tab, tot: 0 }), tm.length > 200 && tm.shift();
          S = I(R.html);
          if (!S.ok) {
            var dd = j(R.html);
            if (we(dd, R.url)) return { logout: !0 };
            (S.diag = fe(R)), (S.err = !0);
            S.why = /Remarks\s*:/i.test(R.html) ? "page opened but its layout was not recognised" : "the portal did not return the application page";
            rpDiag = {
              app: E.appNo, at: new Date().toLocaleString("en-IN"), why: S.why,
              button: Nn ? Nn.row.btnName + " = " + Nn.row.btnValue : mem ? mem.row.btnName + " = " + mem.row.btnValue : "",
              dash: dashRaw, first: (R.diag && R.diag.html) || "", firstUrl: (R.diag && R.diag.url) || "",
              final: R.html, finalUrl: R.url, timing: tm[tm.length - 1],
            };
          }
        }
      } catch (err) {
        var why =
          err && "AbortError" === err.name
            ? "the portal did not respond within 90 s"
            : /Dashboard/i.test(String(err && err.message))
              ? "the Dashboard did not load / application not found on it"
              : "error: " + String((err && err.message) || err).slice(0, 120);
        S = { ok: !1, err: !0, why: why, diag: "Error: " + why };
        rpDiag = { app: E.appNo, at: new Date().toLocaleString("en-IN"), why: why, button: "", dash: dashRaw, first: "", firstUrl: "", final: "", finalUrl: "" };
      }
      if (gone) return { gone: !0 };
      var O = Q(S);
      return {
        item: {
          service: E.service, appNo: E.appNo, name: E.name, mobile: E.mobile, village: E.village, khasra: E.khasra,
          purpose: E.purpose, appDate: E.appDate, revert: E.revert, days: E.days,
          khewat: S.khewat || "", pat: S.pat || "", gir: S.gir || "", nt: S.nt || "", teh: S.teh || "",
          stage: O.stage, flag: O.flag, diag: S.diag || "", holder: O.holder || "", lastBy: O.lastBy || "",
          lastT: O.lastT || 0, lastRemark: O.lastRemark || "", stageDays: null == O.stageDays ? null : O.stageDays,
          svc: E.svc || "", docs: S.docs || [], fields: S.fields || null, adj: S.adj || null, mut: S.mut || null,
          patReport: O.patReport || "", level: O.level || "", levelBy: O.levelBy || "", levelT: O.levelT || 0,
          history: O.history || [], vendee: S.vendee || "", area: S.area || "", set: setNo, err: !!S.err, errWhy: S.why || "",
          readAt: Date.now(),
        },
      };
  }
  async function rpRunPlan(r, refs) {
    if (A) return;
    (A = !0), (T = !1), (P = !1), (rpStopSet = !1), (rpDiag = null);
    rpBG.gen++, (rpBG.queue = []), (rpBG.total = 0);
    var runStart = Date.now(),
      runRead = 0,
      done = {},
      first = !0;
    r.items.forEach(function (e) {
      done[rpScanKey(e)] = 1;
    });
    (r.gone = r.gone || []).forEach(function (k) {
      done[k] = 1;
    });
    var st0 = rpScanStats(r);
    st0.setsDone
      ? rpShowResults({ at: Date.now(), items: rpOrdered(r), partial: !0 })
      : (w.innerHTML = '<div class="card"><h3>Reading applications in sets of ' + 10 + '</h3><p class="muted" style="margin:0">Results appear here as soon as Set 1 is complete, so you can start working on it while the next sets are read.</p></div>');
    for (var ix = 0; ix < r.plan.length && !T; ix++) {
      var E = r.plan[ix],
        key = rpScanKey(E);
      if (done[key]) continue;
      var setNo = Math.floor(ix / 10) + 1;
      rpScanBar(r, setNo, ix % 10);
      var tf = Date.now(),
        one = await rpReadOne(E, refs[key], first, (r.timing = r.timing || []), setNo);
      if (one.logout) {
        (T = !0), (P = !0);
        break;
      }
      (first = !1), runRead++;
      if (one.gone) r.gone.push(key);
      else r.items.push(one.item);
      r.timing && r.timing.length && !r.timing[r.timing.length - 1].tot && (r.timing[r.timing.length - 1].tot = Date.now() - tf + e);
      (done[key] = 1), rpScanSave(r);
      if ((ix + 1) % 10 == 0 || ix === r.plan.length - 1) {
        try {
          rpShowResults({ at: Date.now(), items: rpOrdered(r), partial: !0 });
        } catch (x) {}
        rpStopSet && (T = !0);
      }
      await C(e);
    }
    A = !1;
    var fin = rpScanStats(r);
    (r.complete = fin.complete), (r.at = Date.now()), rpScanSave(r);
    var items = rpOrdered(r),
      M = { at: r.at, items: items, partial: !fin.complete, loggedOut: P };
    try {
      de(items, M.at);
    } catch (x) {}
    try {
      localStorage.setItem(t, JSON.stringify(M));
    } catch (x) {}
    rpSyncScan(M);
    if (fin.complete && !fin.errs)
      try {
        localStorage.removeItem("rpTrackerScan");
      } catch (x) {}
    rpShowResults(M);
    var spd = rpSpeed(r, 0),
      took = Math.round((Date.now() - runStart) / 1000),
      runLine = runRead ? runRead + " read in " + (took >= 60 ? Math.floor(took / 60) + " min " + (took % 60) + " s" : took + " s") + (spd ? " · " + spd.avg : "") : "";
    r.lastRun = runLine;
    (fin.complete && !fin.errs) || rpScanSave(r); // a finished, clean scan stays cleared
    var endMsg =
      P
        ? "The portal logged you out after " + fin.read + " of " + fin.N + ". Log in again, run Tracker and tap Resume."
        : !fin.complete
          ? "Scan stopped after " + fin.read + " of " + fin.N + " (" + fin.setsDone + " of " + fin.S + " sets). Run Tracker again and tap Resume to continue."
          : fin.errs
            ? fin.errs + " application(s) could not be read — run Tracker again and tap “Retry unread”." + (runLine ? " (" + runLine + ")" : "")
            : null;
    endMsg || (endMsg = runLine ? "Scan complete — " + runLine : null);
    endMsg ? rpScanBar(r, 0, 0, endMsg, fin.errs ? rpUnreadHtml(r) : "") : rpScanBar(null);
    rpStartBackground(M.items);
  }
  function E_MSG(why) {
    return E[why] || "The Dashboard did not load.";
  }
  // ───── Analyse with village records (hosted version) ─────
  var rpAnaCache = {},
    rpChain = Promise.resolve(),
    rpCurrent = null,
    rpBG = { gen: 0, paused: !1, running: !1, queue: [], done: 0, total: 0, failed: 0, cur: "", userWaiting: 0 },
    RP_LS = "rpAnaCache2";
  function rpBlobB64(b) {
    return new Promise(function (ok, bad) {
      var fr = new FileReader();
      fr.onload = function () {
        ok(String(fr.result).split(",")[1] || "");
      };
      fr.onerror = function () {
        bad(fr.error);
      };
      fr.readAsDataURL(b);
    });
  }
  function rpKey(e) {
    return e.appNo + "|" + e.service;
  }
  // Stage 1: only the applicant (a Patwari comment alone is still Stage 1). Stage 2: Patwari's report submitted AND tatima uploaded.
  function rpStage(e) {
    var tat = (e.docs || []).some(function (d) {
      return /tatima/i.test(d.label);
    });
    return "Submitted" === e.patReport && tat ? 2 : 1;
  }
  function rpPatCount(e) {
    return (e.history || []).filter(function (h) {
      return X(h.by) === "Patwari";
    }).length;
  }
  // Sent back to the Patwari after his report (Naib Tehsildar / Girdawar / Tehsildar acted after him and the file is with the Patwari again)
  function rpReverted(e) {
    var h = e.history || [],
      lastPat = -1;
    h.forEach(function (x, i) {
      X(x.by) === "Patwari" && (lastPat = i);
    });
    if (lastPat < 0 || !/Patwari/i.test(e.stage || "")) return null;
    var after = h.slice(lastPat + 1).filter(function (x) {
      return X(x.by) !== "Patwari";
    });
    if (!after.length) return null;
    var last = after[after.length - 1];
    return { by: last.by, date: last.date };
  }
  function rpVer(e) {
    // A new analysis is needed only when the stage changes, the Patwari resubmits (one more Patwari entry), or documents change.
    // Comments / forwarding by the Girdawar, Naib Tehsildar or Tehsildar do not change the analysis.
    // A new Fard Checker version does NOT discard analyses — "Run again" or "Re-analyse all" uses the new version.
    var st = rpStage(e);
    return ["S" + st, st === 2 ? rpPatCount(e) : 0, (e.docs || []).length, e.appDate || ""].join("|");
  }
  // owner chosen in the report's drop-down — remembered per application
  function rpOwnerGet(e) {
    try {
      var m = JSON.parse(localStorage.getItem("rpOwnerSel") || "{}") || {};
      return m[rpKey(e)];
    } catch (x) {
      return undefined;
    }
  }
  function rpOwnerSet(e, v, label) {
    try {
      var m = JSON.parse(localStorage.getItem("rpOwnerSel") || "{}") || {};
      m[rpKey(e)] = { v: String(v), label: label || "", at: Date.now() };
      localStorage.setItem("rpOwnerSel", JSON.stringify(m));
      rpSyncStateSoon(15e3);
    } catch (x) {}
  }
  function rpWireOwner(root, e) {
    // v1.9.6: khewat/khata row chosen in section 2 (radio) + person chosen in section 3 → variant "g:p"
    var radios = root.querySelectorAll("input[data-rp-group]"),
      sels = root.querySelectorAll("select[data-rp-person]");
    if (!radios.length && !sels.length) return;
    function curG() {
      var r = Array.prototype.filter.call(radios, function (x) {
        return x.checked;
      })[0];
      return r ? r.value : "0";
    }
    function selFor(g) {
      return Array.prototype.filter.call(sels, function (x) {
        return x.dataset.g === String(g);
      })[0];
    }
    function apply() {
      var g = curG(),
        sel = selFor(g),
        k = g + ":" + (sel ? sel.value : "-1");
      Array.prototype.forEach.call(root.querySelectorAll("[data-owner]"), function (el) {
        el.style.display = el.getAttribute("data-owner") === k ? "" : "none";
      });
      Array.prototype.forEach.call(root.querySelectorAll("[data-gsel]"), function (el) {
        el.style.display = el.getAttribute("data-gsel") === g ? "" : "none";
      });
      Array.prototype.forEach.call(radios, function (x) {
        var tr = x.closest("tr");
        tr && (tr.style.background = x.checked ? "#eef5ff" : "");
      });
      return { k: k, label: sel && sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : "" };
    }
    var saved = rpOwnerGet(e);
    if (saved && /^\d+:-?\d+$/.test(saved.v)) {
      var sg = saved.v.split(":")[0],
        sp = saved.v.split(":")[1],
        rr = Array.prototype.filter.call(radios, function (x) {
          return x.value === sg;
        })[0];
      if (rr) {
        rr.checked = !0;
        var ss = selFor(sg);
        ss && ss.querySelector('option[value="' + sp + '"]') && (ss.value = sp);
      }
    }
    apply();
    function save() {
      var r = apply(),
        rowTxt = "";
      try {
        var tr = Array.prototype.filter.call(radios, function (x) {
          return x.checked;
        })[0];
        tr && (rowTxt = "khewat " + tr.closest("tr").cells[1].textContent.trim() + ", khata " + tr.closest("tr").cells[2].textContent.trim() + " — ");
      } catch (x) {}
      rpOwnerSet(e, r.k, rowTxt + r.label);
    }
    Array.prototype.forEach.call(radios, function (x) {
      x.onchange = save;
    });
    Array.prototype.forEach.call(sels, function (x) {
      x.onchange = save;
    });
  }
  // pre-scrutiny points (kept across versions) and photo fingerprints (to catch a reused photo)
  function rpPtsGet(e) {
    try {
      return (JSON.parse(localStorage.getItem("rpPts") || "{}") || {})[rpKey(e)] || null;
    } catch (x) {
      return null;
    }
  }
  function rpPtsSave(e, kase, points) {
    try {
      var m = JSON.parse(localStorage.getItem("rpPts") || "{}") || {},
        k = rpKey(e),
        o = m[k] || {};
      if (o.case && !o.s1 && !o.s2) o = o.case === 1 ? { s1: { points: o.points, at: o.at } } : { s2: { points: o.points, at: o.at, key: "" } };
      var key = rpVer(e);
      if (kase === 1) o.s1 = { points: points || [], at: Date.now() };
      else {
        if (o.s2 && o.s2.key !== key) o.s2prev = o.s2;           // the Patwari resubmitted — keep the previous report's points
        o.s2 = { points: points || [], at: Date.now(), key: key };
      }
      o.at = Date.now();
      m[k] = o;
      var ks = Object.keys(m).sort(function (a, b) {
        return (m[b].at || 0) - (m[a].at || 0);
      });
      ks.slice(400).forEach(function (k) {
        delete m[k];
      });
      localStorage.setItem("rpPts", JSON.stringify(m));
    } catch (x) {}
  }
  function rpFpAll() {
    try {
      return JSON.parse(localStorage.getItem("rpPhotoFp") || "{}") || {};
    } catch (x) {
      return {};
    }
  }
  function rpFpSave(e, h) {
    if (!h) return;
    try {
      var m = rpFpAll();
      m[e.appNo] = { h: h, at: Date.now() };
      var ks = Object.keys(m).sort(function (a, b) {
        return m[b].at - m[a].at;
      });
      ks.slice(600).forEach(function (k) {
        delete m[k];
      });
      localStorage.setItem("rpPhotoFp", JSON.stringify(m));
    } catch (x) {}
  }
  // ── Analysis summary: one line per application, Case 1 and Case 2 in separate tables
  var rpSumItems = null,
    rpSumGo = null;
  function rpSumHtml(items) {
    var c1 = [],
      c2 = [];
    (items || []).forEach(function (e) {
      (rpStage(e) === 2 ? c2 : c1).push(e);
    });
    function tbl(list, title, note) {
      var ready = 0;
      var rows = list
        .map(function (e) {
          var g = (rpCacheGet(e) || {}).gist || (function () {
              var r = rpJ("rpGistRemote")[rpKey(e)];
              return r && r.ver === rpVer(e) && (r.at || 0) > rpReAllAt() ? r.gist : null;
            })(),
            col = g ? { red: "#b42318", amber: "#8a5300", green: "#145c36" }[g.band] || "#5b6475" : "#5b6475";
          g && ready++;
          return (
            '<tr class="sumr" data-k="' + L(e.appNo + "|" + e.service) + '" style="cursor:pointer"><td><b>…' + L(String(e.appNo || "").slice(-4)) + "</b>" +
            '<div class="muted">' + L(e.service || "") + "</div></td><td>" + L(e.name || "") + "</td><td>" + L(e.village || "") + "</td><td>" + L(e.khasra || "") +
            '</td><td style="min-width:240px">' +
            (g
              ? '<b style="color:' + col + '">' + (g.score == null ? "—" : g.score) + "/100</b> — " + L(g.text || "") +
                (rpReverted(e) ? ' <b style="color:#8a5300">· ↩ reverted to Patwari, awaiting resubmission</b>' : "") +
                ((rpReady(e) || {}).appv && (rpReady(e) || {}).appv !== rpAppVersion() ? ' <span class="muted">· v' + L((rpReady(e) || {}).appv) + "</span>" : "")
              : '<span class="muted">' + (rpEligible(e) ? "Analysis pending (runs in the background)" : "No documents to analyse") + "</span>") +
            "</td></tr>"
          );
        })
        .join("");
      return (
        '<div class="card"><h3>' + title + ' <span class="muted">(' + ready + " of " + list.length + ' analysed)</span></h3><div class="muted" style="margin:-4px 0 6px">' + note +
        '</div><div class="scroll"><table><thead><tr><th>App. no.</th><th>Applicant</th><th>Village</th><th>Survey no.</th><th>Gist</th></tr></thead><tbody>' +
        (rows || '<tr><td colspan="5" class="muted">None</td></tr>') + "</tbody></table></div></div>"
      );
    }
    return (
      tbl(c1, "Stage 1 — Applicant's submission (Patwari report and tatima not yet in)", "Photo, survey record, title and documents. Tap a row to open that application.") +
      tbl(c2, "Stage 2 — Patwari's report and tatima submitted", "Includes the tatima and the report's contradictions. Tap a row to open that application.")
    );
  }
  function rpSumBind() {
    var box = y.getElementById("rpsum");
    box &&
      Array.prototype.forEach.call(box.querySelectorAll("tr.sumr"), function (r) {
        r.onclick = function () {
          rpSumGo && rpSumGo(r.dataset.k);
        };
      });
  }
  function rpSumRefresh() {
    try {
      var box = y.getElementById("rpsum");
      if (box && !box.hidden && rpSumItems) (box.innerHTML = rpSumHtml(rpSumItems)), rpSumBind();
    } catch (x) {}
  }
  // ── Scan sync: last scan per login + shared state, kept in a private GitHub repo through the Render app
  function rpLogin() {
    try {
      return localStorage.getItem("rpLogin") || "naib-tehsildar";
    } catch (x) {
      return "naib-tehsildar";
    }
  }
  var rpSyncMsg = "";
  function rpSyncShow(m) {
    rpSyncMsg = m;
    try {
      var el = y.getElementById("rpsyncst");
      el && (el.textContent = m);
    } catch (x) {}
  }
  async function rpSyncCall(method, path, body) {
    var API = window.__rpApiBase || "",
      key = rpGetKey(!1);
    if (!API || !key) throw new Error("no access key yet");
    var r = await rpFetch(API + path, {
      method: method,
      headers: Object.assign({ "X-Access-Key": key }, body ? { "Content-Type": "application/json" } : {}),
      body: body ? JSON.stringify(body) : void 0,
      cache: "no-store",
    });
    var j = {};
    try {
      j = await r.json();
    } catch (x) {}
    if (!r.ok) throw new Error(j.error || "HTTP " + r.status);
    return j;
  }
  async function rpSyncScan(M) {
    try {
      localStorage.setItem("rpSyncPending", "1");
    } catch (x) {}
    try {
      rpSyncShow("Saving scan online …");
      await rpSyncCall("POST", "/api/sync/scan", { login: rpLogin(), scan: M });
      localStorage.removeItem("rpSyncPending");
      rpSyncShow("✓ Scan saved online (" + rpLogin().replace(/-/g, " ") + ")");
      rpSyncStateSoon(2000);
    } catch (x) {
      if (/not set up|no access key/.test(String(x.message))) {
        localStorage.removeItem("rpSyncPending");
        rpSyncShow("");
      } else rpSyncShow("Scan not synced — will retry (" + String(x.message).slice(0, 80) + ")");
    }
  }
  var rpSyncT = null;
  function rpSyncStateSoon(ms) {
    clearTimeout(rpSyncT);
    rpSyncT = setTimeout(rpSyncState, ms || 45e3);
  }
  function rpJ(k) {
    try {
      return JSON.parse(localStorage.getItem(k) || "{}") || {};
    } catch (x) {
      return {};
    }
  }
  async function rpSyncState() {
    var since = +(localStorage.getItem("rpSyncAt") || 0),
      now = Date.now(),
      pick = function (m, f) {
        var o = {};
        Object.keys(m).forEach(function (k) {
          var v = f ? f(m[k]) : m[k];
          v && (v.at || 0) > since && (o[k] = v);
        });
        return o;
      };
    var body = {
      gists: pick(rpJ(RP_LS), function (c) {
        return c && c.gist ? { ver: c.ver, gist: c.gist, at: c.at } : null;
      }),
      choices: pick(rpJ("rpOwnerSel")),
      points: pick(rpJ("rpPts")),
      fps: pick(rpJ("rpPhotoFp")),
    };
    var any = Object.keys(body).some(function (k) {
      return Object.keys(body[k]).length;
    });
    if (!any) return;
    try {
      await rpSyncCall("POST", "/api/sync/state", body);
      localStorage.setItem("rpSyncAt", String(now));
    } catch (x) {}
  }
  function rpMergeLocal(key, remote) {
    if (!remote) return;
    var m = rpJ(key);
    Object.keys(remote).forEach(function (k) {
      var r = remote[k],
        l = m[k];
      if (r && (!l || (r.at || 0) > (l.at || 0))) m[k] = r;
    });
    try {
      localStorage.setItem(key, JSON.stringify(m));
    } catch (x) {}
  }
  async function rpSyncPull() {
    try {
      var j = await rpSyncCall("GET", "/api/sync/state");
      var st = j.state || {};
      rpMergeLocal("rpOwnerSel", st.choices);
      rpMergeLocal("rpPts", st.points);
      rpMergeLocal("rpPhotoFp", st.fps);
      rpMergeLocal("rpGistRemote", st.gists);
      rpMergeLocal("rpRepRemote", st.reps);
      rpSumRefresh();
    } catch (x) {}
  }
  // start screen: list the scans saved online; the newer ones are highlighted
  async function rpSyncOffer(localAt) {
    var box = y.getElementById("rpsynccard");
    if (!box) return;
    if (localStorage.getItem("rpSyncPending") === "1") {
      try {
        var mine = JSON.parse(localStorage.getItem(t) || "null");
        mine && rpSyncScan(mine);
      } catch (x) {}
    }
    var j;
    try {
      j = await rpSyncCall("GET", "/api/sync/index");
    } catch (x) {
      return;
    }
    if (!j.configured) return;
    rpSyncPull();
    var ix = j.index || {},
      ks = Object.keys(ix).sort(function (a, b) {
        return (ix[b].at || 0) - (ix[a].at || 0);
      }),
      opts = ["naib-tehsildar", "tehsildar", "other"],
      nice = function (k) {
        return k.replace(/-/g, " ").replace(/\b\w/g, function (c) {
          return c.toUpperCase();
        });
      },
      sel =
        '<select id="rplogin" style="font:inherit;padding:3px;border:1px solid #c9ced8;border-radius:6px">' +
        opts
          .map(function (o) {
            return '<option value="' + o + '"' + (o === rpLogin() ? " selected" : "") + ">" + nice(o) + "</option>";
          })
          .join("") +
        "</select>";
    box.innerHTML =
      '<div class="card"><h3>Scans saved online</h3>' +
      (ks.length
        ? ks
            .map(function (k) {
              var v = ix[k],
                newer = !localAt || (v.at || 0) > localAt;
              return (
                '<div class="tools" style="margin:4px 0"><span><b>' + L(nice(k)) + "</b> — " + L(new Date(v.at).toLocaleString()) + " · " + v.n + " applications" +
                (v.partial ? " (partial)" : "") + (newer ? ' <b style="color:#145c36">· newer than this browser</b>' : "") +
                '</span><button data-sync-open="' + L(k) + '"' + (newer ? ' class="pri"' : "") + ">Open</button></div>"
              );
            })
            .join("")
        : '<p class="muted">No scan saved online yet.</p>') +
      '<p class="muted" style="margin:6px 0 0">This browser saves its scans as: ' + sel + ' <span id="rpsyncst">' + L(rpSyncMsg) + "</span></p></div>";
    var ls = y.getElementById("rplogin");
    ls &&
      (ls.onchange = function () {
        try {
          localStorage.setItem("rpLogin", ls.value);
        } catch (x) {}
      });
    Array.prototype.forEach.call(box.querySelectorAll("[data-sync-open]"), function (b) {
      b.onclick = async function () {
        b.disabled = !0;
        b.textContent = "Loading …";
        try {
          var r = await rpSyncCall("GET", "/api/sync/scan?login=" + encodeURIComponent(b.dataset.syncOpen));
          if (!r.scan || !r.scan.items) throw new Error("empty");
          r.scan.fromOnline = b.dataset.syncOpen;
          try {
            localStorage.setItem(t, JSON.stringify(r.scan));
          } catch (x) {}
          await rpSyncPull();
          Ne(r.scan), rpStartBackground(r.scan.items);
        } catch (x) {
          b.disabled = !1;
          b.textContent = "Open";
          alert("Could not load the online scan: " + String((x && x.message) || x));
        }
      };
    });
  }
  function rpAppVersion() {
    return String(window.__rpVersion || RP_TRACKER_VERSION || "");
  }
  function rpReanalyseAll(items) {
    try {
      localStorage.setItem("rpReAllAt", String(Date.now())); // saved analyses here and online count as not ready
    } catch (x) {}
    rpAnaCache = {};
    rpPre = {};
    rpMarkButtons();
    rpSumRefresh();
    rpStartBackground(items || rpSumItems || []);
  }
  // v1.9.9 register: the report text lives in IndexedDB (no limit of 12), the list of ready reports in localStorage.
  // A report saved online (no photos, reduced tatima) also counts as ready, so any browser opens it at once.
  function rpRepDb(mode, k, val) {
    return new Promise(function (ok) {
      try {
        var rq = indexedDB.open("rpReports", 1);
        rq.onupgradeneeded = function () {
          rq.result.createObjectStore("html");
        };
        rq.onerror = function () {
          ok(null);
        };
        rq.onsuccess = function () {
          try {
            var tx = rq.result.transaction("html", mode === "get" ? "readonly" : "readwrite"),
              st = tx.objectStore("html"),
              r2 = mode === "get" ? st.get(k) : st.put(val, k);
            r2.onsuccess = function () {
              ok(mode === "get" ? r2.result || null : !0);
            };
            r2.onerror = function () {
              ok(null);
            };
          } catch (x) {
            ok(null);
          }
        };
      } catch (x) {
        ok(null);
      }
    });
  }
  function rpReAllAt() {
    try {
      return +(localStorage.getItem("rpReAllAt") || 0);
    } catch (x) {
      return 0;
    }
  }
  function rpCacheGet(e) {
    var k = rpKey(e),
      c = rpAnaCache[k];
    if (!c) {
      try {
        c = (JSON.parse(localStorage.getItem(RP_LS) || "{}") || {})[k];
      } catch (x) {}
    }
    return c && c.ver === rpVer(e) && (c.at || 0) > rpReAllAt() ? c : null;
  }
  function rpRemoteRep(e) {
    var r = rpJ("rpRepRemote")[rpKey(e)];
    return r && r.ver === rpVer(e) && (r.at || 0) > rpReAllAt() ? r : null;
  }
  function rpReady(e) {
    return rpCacheGet(e) || rpRemoteRep(e);
  }
  // full report: memory → this browser (IndexedDB / older localStorage copy) → online copy
  async function rpHtmlGet(e, k, ver) {
    k = k || rpKey(e);
    ver = ver || rpVer(e);
    var c = rpAnaCache[k];
    if (c && c.ver === ver && c.html) return c;
    var m = null;
    try {
      m = (JSON.parse(localStorage.getItem(RP_LS) || "{}") || {})[k];
    } catch (x) {}
    if (m && m.ver === ver) {
      if (m.html) return (rpAnaCache[k] = m);
      var h = await rpRepDb("get", k);
      if (h && h.ver === ver && h.html) return (rpAnaCache[k] = Object.assign({}, m, { html: h.html }));
    }
    try {
      var j = await rpSyncCall("GET", "/api/sync/report?key=" + encodeURIComponent(k)),
        r = j.report;
      if (r && r.html && r.ver === ver) {
        var o = { ver: r.ver, html: r.html, at: r.at, gist: r.gist, appv: r.appv, online: !0 };
        rpAnaCache[k] = o;
        return o;
      }
    } catch (x) {}
    return null;
  }
  function rpCachePut(e, html, gist) {
    var k = rpKey(e),
      c = { ver: rpVer(e), html: html, at: Date.now(), gist: gist || null, appv: rpAppVersion() };
    rpAnaCache[k] = c;
    rpRepDb("put", k, { ver: c.ver, html: html, at: c.at });
    try {
      var all = JSON.parse(localStorage.getItem(RP_LS) || "{}") || {};
      all[k] = { ver: c.ver, at: c.at, gist: c.gist, appv: c.appv };
      Object.keys(all).forEach(function (x) {
        all[x] && all[x].html && x !== k && (rpRepDb("put", x, { ver: all[x].ver, html: all[x].html, at: all[x].at }), delete all[x].html); // move older copies out of localStorage
      });
      var keys = Object.keys(all).sort(function (a, b) {
        return all[b].at - all[a].at;
      });
      keys.slice(3000).forEach(function (x) {
        delete all[x];
      });
      localStorage.setItem(RP_LS, JSON.stringify(all));
    } catch (x) {}
  }
  function rpGetKey(ask) {
    var key = "";
    try {
      key = localStorage.getItem("rpApiKey") || "";
    } catch (x) {}
    if (!key && ask) {
      key = (prompt("Access key for the analyser (the ACCESS_KEY set on Render):") || "").trim();
      if (key)
        try {
          localStorage.setItem("rpApiKey", key);
        } catch (x) {}
    }
    return key;
  }
  // One analysis at a time (the portal session can only have one application open)
  function rpSerial(fn) {
    var p = rpChain.then(fn, fn);
    rpChain = p.catch(function () {});
    return p;
  }
  // Core: fetch documents of application e, send to Render, return report html
  function rpAbortErr() {
    var x = new Error("stopped to give way to your request");
    x.stage = "aborted";
    return x;
  }
  async function rpCore(e, key, status, ctl) {
    var API = window.__rpApiBase || "",
      stage = "connecting";
    ctl = ctl || { aborted: !1, ac: null };
    function chk() {
      if (ctl.aborted) throw rpAbortErr();
    }
    try {
      var pr = await fetch(API + "/api/ping", { cache: "no-store", signal: ctl.ac && ctl.ac.signal });
      if (!pr.ok) throw new Error("HTTP " + pr.status);
    } catch (err) {
      if (ctl.aborted) throw rpAbortErr();
      var x = new Error(
        "Cannot reach the analyser (" + String((err && err.message) || err) + "). If Render was asleep, wait 30–50 s and try again; if it keeps failing, the portal is blocking the connection.",
      );
      x.stage = stage;
      throw x;
    }
    try {
      stage = "fetching documents";
      var pf_ = rpPre[rpKey(e)];
      delete rpPre[rpKey(e)];
      var got = pf_ ? await pf_.catch(function () {
            return null;
          }) : null;
      var tf = Date.now();
      if (!got) got = await rpPortal(function () {
          return rpFetchDocs(e, status, chk);
        });
      var fetchSecs = (Date.now() - tf) / 1e3;
      rpPrefetchNext(e); // while the analyser works on this one, the next application's documents are fetched
      var docs = got.docs,
        idDocs = got.idDocs,
        ts = Date.now();
      chk();
      stage = "sending to the analyser";
      status(
        "Reading " +
          docs.filter(function (d) {
            return d.data;
          }).length +
          " document(s) and checking the village Jamabandi and map … this can take up to a minute.",
      );
      var resp = await fetch(API + "/api/analyse", {
        signal: ctl.ac && ctl.ac.signal,
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Access-Key": key },
        body: JSON.stringify({
          app: {
            appNo: e.appNo, name: e.name, village: e.village, khasra: e.khasra, service: e.service,
            purpose: e.purpose, appDate: e.appDate, area: e.area, fields: e.fields, adj: e.adj, mut: e.mut, history: e.history,
            patReport: e.patReport || "", stage: e.stage || "", stageN: rpStage(e),
          },
          docs: docs,
          id_docs: idDocs,
          rp_key: rpKey(e),
          rp_ver: rpVer(e),
          rp_appv: rpAppVersion(),
          doc_labels: (e.docs || []).map(function (d) {
            return d.label;
          }),
          prev_points: (function () {
            var pp = rpPtsGet(e) || {};
            return pp.s1 ? pp.s1.points : pp.case === 1 ? pp.points : null;
          })(),
          prev_report_points: (function () {
            var pp = rpPtsGet(e) || {};
            if (rpStage(e) !== 2) return null;
            if (pp.s2 && pp.s2.key && pp.s2.key !== rpVer(e)) return pp.s2.points;   // first analysis after a resubmission
            return pp.s2prev ? pp.s2prev.points : null;                               // "Run again" on the same submission
          })(),
          photo_fps: (function () {
            var m = rpFpAll();
            return Object.keys(m)
              .filter(function (k) {
                return k !== e.appNo;
              })
              .slice(0, 600)
              .map(function (k) {
                return { app: k, hash: m[k].h };
              });
          })(),
        }),
      });
      if (401 === resp.status) {
        try {
          localStorage.removeItem("rpApiKey");
        } catch (x) {}
        var k = new Error("Wrong access key.");
        k.stage = "key";
        throw k;
      }
      var j = await resp.json();
      if (!resp.ok) throw new Error(j.error || "HTTP " + resp.status);
      rpCachePut(e, j.html, j.gist);
      if (j.saved_online) {
        var rr = rpJ("rpRepRemote");
        rr[rpKey(e)] = { ver: rpVer(e), appv: rpAppVersion(), at: Date.now() };
        try {
          localStorage.setItem("rpRepRemote", JSON.stringify(rr));
        } catch (x) {}
      }
      rpRegPaint();
      rpStat(fetchSecs, (Date.now() - ts) / 1e3);
      rpPtsSave(e, j.case, j.points);
      rpSumRefresh();
      rpFpSave(e, j.photo_hash);
      rpSyncStateSoon();
      rpMarkButtons();
      return j.html;
    } catch (err) {
      if (ctl.aborted) throw rpAbortErr();
      err.stage = err.stage || stage;
      throw err;
    }
  }
  // Documents of one application, fetched from a single opening of its page.
  var rpPre = {},
    rpStats = { n: 0, f: 0, a: 0 };
  function rpStat(f, a) {
    rpStats.n++, (rpStats.f += f), (rpStats.a += a);
  }
  function rpPrefetchNext(cur) {
    try {
      if (A || rpBG.paused) return;
      var nx = rpBG.queue.filter(function (q) {
        return q !== cur && !rpReady(q) && !rpPre[rpKey(q)];
      })[0];
      if (!nx || Object.keys(rpPre).length >= 1) return;
      var k = rpKey(nx);
      rpPre[k] = rpPortal(function () {
        if (A) throw new Error("scan running");
        return rpFetchDocs(nx);
      });
      rpPre[k].catch(function () {
        delete rpPre[k];
      });
    } catch (x) {}
  }
  async function rpFetchDocs(e, status, chk) {
    chk = chk || function () {};
    status = status || function () {};
    if (A) throw new Error("A scan is reading the portal right now.");
    var kase1 = rpStage(e) === 1,
      idre = /identity|aadhaar|aadhar|id proof|voter|pan card/i,
      want = (e.docs || []).filter(function (d) {
        return !/^All documents/.test(d.label) && (kase1 || !idre.test(d.label));
      }),
      docs = [],
      idDocs = [],
      size = 0,
      dt = null;
    try {
      dt = await rpDetailOpen(e);
    } catch (x) {
      dt = null;
    }
    for (var i = 0; i < want.length; i++) {
      chk();
      var d = want[i],
        isId = idre.test(d.label);
      status((isId ? "Fetching identity proof for the Aadhaar check" : "Fetching document " + (i + 1) + " of " + want.length + ": " + d.label) + " …");
      try {
        var res = null;
        if (dt)
          try {
            res = await rpDetailDoc(dt, d.i, d.label);
          } catch (x) {
            res = null;
          }
        if (!res) res = await Ee(e, d.i, d.label);
        var blob = res.blob.type ? res.blob : new Blob([res.blob], { type: res.type || "" });
        if (/zip/.test(res.type || blob.type)) throw new Error("ZIP skipped");
        if (isId) {
          // identity proof: read on the server by local OCR only (Aadhaar check), never sent to an AI reader
          if (blob.size < 12e6) idDocs.push({ label: d.label, type: res.type || blob.type, data: await rpBlobB64(blob) });
        } else {
          if (size + blob.size > 30e6) throw new Error("too large to send");
          size += blob.size;
          docs.push({ label: d.label, type: res.type || blob.type, data: await rpBlobB64(blob) });
        }
      } catch (err) {
        if (err && err.name === "AbortError") throw err;
        isId || docs.push({ label: d.label, error: String((err && err.message) || err).slice(0, 200) });
      }
      await C(150);
    }
    return { docs: docs, idDocs: idDocs };
  }
  // bg = true for background jobs. A request from you stops a running background job (it is re-queued) and goes first.
  function rpRunFor(e, status, bg, force) {
    var ck = rpKey(e);
    if (rpCurrent && rpCurrent.ck === ck) {
      if (!bg) rpCurrent.bg = !1; // you asked for the one already running: let it finish
      return rpCurrent.promise;
    }
    if (!bg) {
      rpBG.userWaiting++;
      if (rpCurrent && rpCurrent.bg) {
        rpCurrent.ctl.aborted = !0;
        try {
          rpCurrent.ctl.ac && rpCurrent.ctl.ac.abort();
        } catch (x) {}
      }
    }
    var key = rpGetKey(!1);
    var job = rpSerial(async function () {
      if (!force && rpReady(e)) {
        var hit = await rpHtmlGet(e);
        if (hit) return hit.html;
      }
      if (bg && rpBG.userWaiting) throw rpAbortErr(); // let your request go first
      var ctl = { aborted: !1, ac: window.AbortController ? new AbortController() : null };
      var p = rpCore(e, key, status, ctl);
      rpCurrent = { ck: ck, promise: p, bg: !!bg, ctl: ctl };
      try {
        return await p;
      } finally {
        rpCurrent = null;
      }
    });
    if (!bg)
      job.then(
        function () {
          rpBG.userWaiting--, rpKick();
        },
        function () {
          rpBG.userWaiting--, rpKick();
        },
      );
    return job;
  }
  function rpKick() {
    // resume background after your request is done
    !rpBG.userWaiting && !rpBG.running && !rpBG.paused && rpBG.queue.length && !rpBG.needKey && rpLoop(rpBG.gen);
  }
  async function rpAnalyse(e, force) {
    var API = window.__rpApiBase || "";
    S = y.getElementById("modal");
    var ttl = y.getElementById("mtitle"),
      body = y.getElementById("mbody"),
      acts = y.getElementById("macts");
    ttl.textContent = "Analysis — " + (e.name || e.appNo);
    acts.innerHTML = "";
    S.hidden = !1;
    function st(msg, err) {
      body.innerHTML =
        '<div style="padding:18px;max-width:640px;align-self:flex-start;' + (err ? "color:#b42318" : "color:#5b6475") + '">' + L(msg) + "</div>";
    }
    function again() {
      acts.innerHTML = '<button id="rpaRe">Run again</button><button id="rpaSv" style="background:#5b3fa8;color:#fff">Save record to folder</button>';
      y.getElementById("rpaRe").onclick = function () {
        rpAnalyse(e, !0);
      };
      y.getElementById("rpaSv").onclick = function () {
        rpSaveRecord(e, this);
      };
    }
    function show(html, cachedAt, online, appv) {
      var rv = rpReverted(e),
        cc = rpReady(e) || {},
        oldV = cachedAt && (appv || cc.appv) && (appv || cc.appv) !== rpAppVersion() ? appv || cc.appv : "";
      body.innerHTML =
        '<div style="align-self:flex-start;width:100%;background:#f4f5f7">' +
        (rv
          ? '<div style="max-width:900px;margin:8px auto 0;padding:8px 14px;border-radius:8px;background:#fff4e0;color:#8a5300;font-weight:600">↩ Reverted to Patwari' +
            (rv.date ? " on " + L(String(rv.date).replace(/\s+\d{1,2}:\d{2}.*$/, "")) : "") + " by " + L(rv.by || "") +
            " — awaiting resubmission. This is the report on his previous submission.</div>"
          : "") +
        (oldV
          ? '<div style="max-width:900px;margin:8px auto 0;padding:8px 14px;border-radius:8px;background:#eef0f4;color:#3b4456">Made with version ' + L(oldV) +
            " — tap <b>Run again</b> to analyse with version " + L(rpAppVersion()) + ".</div>"
          : "") +
        (online
          ? '<div style="max-width:900px;margin:8px auto 0;padding:8px 14px;border-radius:8px;background:#eef5ff;color:#12355b">Saved copy from the online register (' +
            L(new Date(cachedAt).toLocaleString()) + ") — the photo, compression check and satellite pictures are not kept online; the tatima is a reduced copy. Tap <b>Run again</b> for the full report.</div>"
          : cachedAt
            ? '<div style="max-width:900px;margin:8px auto 0;padding:0 14px;font-size:12px;color:#5b6475">Prepared in the background at ' +
              L(new Date(cachedAt).toLocaleString()) +
              " · tap “Run again” for a fresh analysis</div>"
            : "") +
        html +
        "</div>";
      rpWireOwner(body, e);
      Array.prototype.forEach.call(body.querySelectorAll("[data-copy]"), function (b) {
        b.onclick = function () {
          var el = Array.prototype.filter.call(body.querySelectorAll("#" + b.dataset.copy), function (q) {
              var v = q.closest("[data-owner]");
              return !v || v.style.display !== "none";
            })[0],
            txt = el ? el.textContent : "";
          navigator.clipboard && navigator.clipboard.writeText
            ? navigator.clipboard.writeText(txt).then(
                function () {
                  b.textContent = "Copied ✓";
                },
                function () {
                  prompt("Copy this:", txt);
                },
              )
            : prompt("Copy this:", txt);
        };
      });
      again();
    }
    if (!API) return st("This tracker was not loaded from the Render app.", !0);
    if (!force && (rpReady(e) || e._archived)) {
      st("Opening the saved analysis …");
      var hit = await rpHtmlGet(e, e._archived ? rpKey(e) : null, e._archived ? e.ver : null);
      if (hit) return show(hit.html, hit.at, hit.online, hit.appv);
      if (e._archived) return st("No saved analysis of this application was found (it is no longer on the Dashboard, so it cannot be analysed again).", !0);
    }
    if (e._archived) return st("This application is no longer on the Dashboard — only its saved analysis can be opened.", !0);
    if (A) return st("A scan is reading the portal right now. Analyse becomes available when it finishes — or tap “Stop after this set”.", !0);
    if (!e.fields) return st("Run a new scan first — this application was read by an older tracker version.", !0);
    if (!rpGetKey(!0)) return (S.hidden = !0), void 0;
    if (force) {
      delete rpAnaCache[rpKey(e)];
      try {
        var all = JSON.parse(localStorage.getItem(RP_LS) || "{}") || {};
        delete all[rpKey(e)];
        localStorage.setItem(RP_LS, JSON.stringify(all));
      } catch (x) {}
    }
    st(
      rpCurrent && rpCurrent.ck !== rpKey(e) && rpCurrent.bg
        ? "Stopping the background analysis to take up your application first …"
        : "Connecting to the analyser …",
    );
    try {
      var html = await rpRunFor(e, st, !1, !!force);
      show(html);
      rpStartBackground(); // key may have just been entered
    } catch (err) {
      st(
        "Analysis failed while " +
          (err.stage || "working") +
          ": " +
          String((err && err.message) || err) +
          (err.stage === "sending to the analyser"
            ? " The analyser was reachable but dropped this request — usually it ran out of memory or time on Render. Tap Run again; if it repeats, send a screenshot of the Render Logs."
            : ""),
        !0,
      );
      again();
    }
  }
  // ───── Save record to a folder on this computer (Chrome / Edge) ─────
  // Each application gets its own sub-folder: applicant's documents, the Patwari's tatima, and the KMZ
  // (khasra on the map with the tatima laid over it). The chosen folder is remembered on this computer.
  function rpIdb(mode, val) {
    return new Promise(function (ok) {
      try {
        var rq = indexedDB.open("rpRecords", 1);
        rq.onupgradeneeded = function () {
          rq.result.createObjectStore("kv");
        };
        rq.onerror = function () {
          ok(null);
        };
        rq.onsuccess = function () {
          try {
            var tx = rq.result.transaction("kv", mode === "get" ? "readonly" : "readwrite"),
              st = tx.objectStore("kv"),
              r2 = mode === "get" ? st.get("dir") : st.put(val, "dir");
            r2.onsuccess = function () {
              ok(mode === "get" ? r2.result || null : !0);
            };
            r2.onerror = function () {
              ok(null);
            };
          } catch (x) {
            ok(null);
          }
        };
      } catch (x) {
        ok(null);
      }
    });
  }
  var rpDirMem = null;
  async function rpSaveDir(change) {
    if (!window.showDirectoryPicker) return null;
    var h = change ? null : rpDirMem || (await rpIdb("get"));
    if (h) {
      try {
        var q = await h.queryPermission({ mode: "readwrite" });
        if (q !== "granted") q = await h.requestPermission({ mode: "readwrite" });
        if (q === "granted") return (rpDirMem = h);
      } catch (x) {}
    }
    h = await window.showDirectoryPicker({ id: "fardrecords", mode: "readwrite", startIn: "documents" });
    rpDirMem = h;
    await rpIdb("put", h);
    return h;
  }
  function rpSafe(t) {
    return String(t || "").replace(/[\\/:*?"<>|\x00-\x1f]+/g, " ").replace(/\s+/g, " ").trim().slice(0, 80) || "x";
  }
  function rpExt(type, name) {
    var m = /\.([a-z0-9]{2,4})$/i.exec(name || "");
    if (m) return m[1].toLowerCase();
    type = type || "";
    return /pdf/.test(type) ? "pdf" : /png/.test(type) ? "png" : /jpe?g/.test(type) ? "jpg" : /gif/.test(type) ? "gif" : /tif/.test(type) ? "tif" : /zip/.test(type) ? "zip" : "bin";
  }
  async function rpWrite(dir, name, data) {
    var fh = await dir.getFileHandle(name, { create: !0 }),
      w = await fh.createWritable();
    await w.write(data);
    await w.close();
  }
  function rpB64Blob(b64, type) {
    var bin = atob(b64),
      u = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    return new Blob([u], { type: type });
  }
  function rpDownload(name, blob) {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () {
      URL.revokeObjectURL(a.href), a.remove();
    }, 4000);
  }
  function rpSurveyName(e) {
    var k = String(e.khasra || "").replace(/\//g, "-").replace(/\s+/g, " ").trim(),
      v = String(e.village || "").replace(/\s*-\s*/g, "-").replace(/\s+/g, " ").trim();
    return rpSafe((k || "No khasra") + " " + (v || "Village"));
  }
  // Patwari's uploads start at the tatima (the portal lists the Patwari's section after the applicant's)
  function rpSplitDocs(docs) {
    var list = docs.filter(function (d) {
        return !/^All documents/.test(d.label);
      }),
      at = -1;
    list.forEach(function (d, i) {
      at < 0 && /tatima|patwari|girdh?awar|field\s*report/i.test(d.label) && (at = i);
    });
    return { applicant: at < 0 ? list : list.slice(0, at), patwari: at < 0 ? [] : list.slice(at) };
  }
  async function rpMergePdf(files, title) {
    var API = window.__rpApiBase || "",
      key = rpGetKey(!1);
    if (!API || !key) throw new Error("needs the access key");
    var resp = await rpFetch(API + "/api/merge-pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Access-Key": key },
      body: JSON.stringify({ title: title, files: files }),
    });
    if (!resp.ok) {
      var m = "";
      try {
        m = (await resp.json()).error || "";
      } catch (x) {}
      throw new Error(m || "HTTP " + resp.status);
    }
    return { blob: await resp.blob(), skipped: resp.headers.get("X-Skipped") || "" };
  }
  async function rpSaveRecord(e, btn) {
    var old = btn.textContent;
    function say(t) {
      btn.textContent = t;
    }
    if (A) return alert("A scan is reading the portal right now — save after it finishes (or tap “Stop after this set”).");
    if (!e.docs) return alert("Run a new scan first — this application was read by an older tracker version.");
    if (!rpGetKey(!0)) return;
    btn.disabled = !0;
    var dir = null,
      base = rpSurveyName(e),
      folder = base,
      saved = [],
      failed = [];
    try {
      try {
        dir = await rpSaveDir(!1);
      } catch (x) {
        if (x && x.name === "AbortError") return say(old);
        dir = null;
      }
      var sub = null;
      if (dir) {
        // same survey no. + village already saved for a different application → keep both
        try {
          var ex = await dir.getDirectoryHandle(folder),
            dt = await (await (await ex.getFileHandle("Details.txt")).getFile()).text();
          if (dt.indexOf(String(e.appNo || "")) < 0) folder = base + " (app " + String(e.appNo || "").slice(-6) + ")";
        } catch (x) {}
        sub = await dir.getDirectoryHandle(folder, { create: !0 });
      }
      async function put(name, blob) {
        if (sub) await rpWrite(sub, name, blob);
        else rpDownload(name, blob);
        saved.push(name);
      }
      var parts = rpSplitDocs(e.docs),
        groups = [
          ["Applicant documents", parts.applicant],
          ["Patwari documents", parts.patwari],
        ];
      for (var gi = 0; gi < groups.length; gi++) {
        var gname = groups[gi][0],
          list = groups[gi][1],
          files = [];
        if (!list.length) {
          failed.push(gname + " (none uploaded)");
          continue;
        }
        for (var i = 0; i < list.length; i++) {
          var d = list[i];
          say(gname + ": fetching " + (i + 1) + " of " + list.length + " (" + d.label + ") …");
          try {
            var r = await Ee(e, d.i, d.label);
            files.push({ label: d.label, type: r.type || (r.blob && r.blob.type) || "", data: await rpBlobB64(r.blob) });
          } catch (x) {
            failed.push(gname + ": " + d.label + " (" + String((x && x.message) || x).slice(0, 100) + ")");
          }
          await C(300);
        }
        if (!files.length) continue;
        say(gname + ": joining into one PDF …");
        try {
          var mg = await rpMergePdf(files, base + " - " + gname);
          await put(base + " - " + gname + ".pdf", mg.blob);
          mg.skipped && failed.push(gname + ": could not be added to the PDF — " + mg.skipped);
        } catch (x) {
          failed.push(gname + " PDF (" + String((x && x.message) || x).slice(0, 100) + ")");
        }
        files = null;
      }
      // KMZ with the tatima over the khasra (from the analysis)
      var html = (rpCacheGet(e) || {}).html;
      if (!html && rpCacheGet(e)) html = ((await rpHtmlGet(e)) || {}).html;
      if (!html && window.__rpApiBase && e.fields) {
        say("Preparing KMZ (analysing) …");
        try {
          html = await rpRunFor(e, function (t) {
            say(String(t).slice(0, 60));
          });
        } catch (x) {
          failed.push("KMZ (analysis failed: " + String((x && x.message) || x).slice(0, 100) + ")");
        }
      }
      var km = html && /download="([^"]+\.kmz)"\s+href="data:application\/vnd\.google-earth\.kmz;base64,([^"]+)"/.exec(html);
      if (km) await put(base + " - map with tatima.kmz", rpB64Blob(km[2], "application/vnd.google-earth.kmz"));
      else if (html) failed.push("KMZ (village map or khasra not found, or no tatima — so no KMZ was made)");
      var nearM = html && /Survey no\. (\S+) not on map — nearest available (\S+) shown/.exec(html);
      var out = [
        "Survey no.: " + (e.khasra || ""),
        "Village: " + (e.village || ""),
        "Application no.: " + (e.appNo || ""),
        "Service: " + (e.service || e.svc || ""),
        "Applicant: " + (e.name || ""),
        "Applied on: " + (e.appDate || ""),
        "Saved on: " + new Date().toLocaleString("en-IN"),
        "Owner matched in the analysis: " + ((rpOwnerGet(e) || {}).label || "as found automatically"),
        "",
        "Applicant documents: " + (parts.applicant.map(function (d) { return d.label; }).join(", ") || "none"),
        "Patwari documents: " + (parts.patwari.map(function (d) { return d.label; }).join(", ") || "none"),
      ]
        .concat(nearM ? ["", "NOTE: survey no. " + nearM[1] + " is not on the village map; the KMZ shows the nearest available survey no. " + nearM[2] + " for locality only."] : [])
        .concat(["", "Files saved: " + saved.join(", ")])
        .concat(failed.length ? ["", "Not saved: " + failed.join("; ")] : []);
      await put(sub ? "Details.txt" : base + " - Details.txt", new Blob([out.join("\r\n")], { type: "text/plain" }));
      say(failed.length ? "Saved ✓ (" + failed.length + " note(s))" : "Saved to folder ✓");
      btn.title = (sub ? "Folder: " + dir.name + "\\" + folder : "Downloaded to your Downloads folder") + (failed.length ? "\nNot saved: " + failed.join("; ") : "");
      if (failed.length) alert("Saved to “" + (sub ? dir.name + "\\" + folder : "Downloads") + "”.\n\nNotes:\n• " + failed.join("\n• "));
    } catch (x) {
      say(old);
      alert("Could not save: " + String((x && x.message) || x));
    } finally {
      btn.disabled = !1;
    }
  }
  // ───── Status PDF (pendency only — no remarks, documents or analysis) ─────
  var rpScanAt = 0;
  async function rpStatusPdf(items, btn) {
    var API = window.__rpApiBase || "";
    if (!API) return alert("Status PDF needs the tracker loaded from the Render app.");
    var key = rpGetKey(!0);
    if (!key) return;
    var old = btn.textContent;
    btn.textContent = "Preparing PDF …";
    btn.disabled = !0;
    try {
      var set = ee(),
        office = "";
      items.some(function (e) {
        var tf = e.fields && e.fields.tehsil;
        return tf && (office = "Tehsil " + tf.replace(/\s*\/.*$/, ""));
      });
      var rows = items.map(function (e) {
        var c = null;
        try {
          c = ce(e, set);
        } catch (x) {}
        var cur = c && c.cur ? c.cur : null,
          ob = oe(e);
        return {
          appNo: e.appNo, name: e.name, village: e.village, khasra: e.khasra, service: e.service, purpose: e.purpose,
          appDate: ob.applied ? new Date(ob.applied).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : (e.appDate || "").split("/")[0],
          resub: ob.resub ? new Date(ob.resub).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "",
          stage: e.stage, holder: e.holder, revert: e.revert,
          withSince: (function () {
            var hh = e.history || [], w = e.lastT || (hh.length && hh[hh.length - 1].t) || ob.base;
            return w ? new Date(w).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "";
          })(),
          withDays: (function () {
            var hh = e.history || [], w = e.lastT || (hh.length && hh[hh.length - 1].t) || ob.base;
            if (!w) return null;
            try {
              var td = new Date();
              td.setHours(0, 0, 0, 0);
              return ie(w, td.getTime());
            } catch (x) {
              return null;
            }
          })(),
          dayNow: c && c.dayNow != null ? c.dayNow : null,
          cur: cur ? { role: cur.role, limit: cur.limit, days: cur.days, over: cur.over || 0, left: cur.left, status: cur.status } : null,
          late: c ? c.late.map(function (v) { return { who: v.by || v.role, over: v.over }; }) : [],
        };
      });
      var resp = await fetch(API + "/api/status-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Access-Key": key },
        body: JSON.stringify({ scanAt: rpScanAt || Date.now(), office: office, limits: { pat: +set.pat, gir: +set.gir, nt: +set.nt }, mode: set.mode, items: rows }),
      });
      if (401 === resp.status) {
        try {
          localStorage.removeItem("rpApiKey");
        } catch (x) {}
        throw new Error("Wrong access key — tap again to re-enter it.");
      }
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      var blob = await resp.blob(),
        a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "Pendency_Status_" + new Date(rpScanAt || Date.now()).toISOString().slice(0, 10) + ".pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () {
        URL.revokeObjectURL(a.href);
      }, 5000);
      btn.textContent = "PDF downloaded ✓";
    } catch (err) {
      btn.textContent = "PDF failed";
      prompt("Status PDF could not be made:", String((err && err.message) || err));
    } finally {
      btn.disabled = !1;
      setTimeout(function () {
        btn.textContent = old;
      }, 3000);
    }
  }
  // ───── Background pre-analysis while the tracker stays open ─────
  function rpEligible(e) {
    var docs = (e.docs || []).filter(function (d) {
      return !/^All documents/.test(d.label);
    });
    // v1.9: every application is analysed — Case 1 (pre-scrutiny) and Case 2 (after the Patwari's report)
    return (
      !!e.fields &&
      docs.some(function (d) {
        return !/identity|aadhaar|aadhar|id proof|voter|pan card/i.test(d.label);
      })
    );
  }
  function rpPanel() {
    var p = y.getElementById("rpbg");
    if (!p) {
      p = document.createElement("div");
      p.id = "rpbg";
      p.style.cssText =
        "position:fixed;left:12px;bottom:12px;z-index:5;max-width:min(420px,calc(100vw - 24px));background:#12355b;color:#fff;border-radius:10px;padding:10px 12px;font:13px/1.4 system-ui,sans-serif;box-shadow:0 4px 16px rgba(0,0,0,.25)";
      y.appendChild(p);
    }
    var b = rpBG,
      left = b.queue.length + (b.cur ? 1 : 0);
    if (!b.total) return (p.style.display = "none"), p;
    p.style.display = "block";
    p.innerHTML =
      "<b>Background analysis</b> — " +
      b.done +
      " of " +
      b.total +
      " ready" +
      (b.failed ? ", " + b.failed + " failed" : "") +
      (rpStats.n
        ? '<div style="opacity:.85;font-size:12px">Average per application: documents ' + Math.round(rpStats.f / rpStats.n) + " s · analysis " + Math.round(rpStats.a / rpStats.n) +
          " s (fetching the next one runs alongside)</div>"
        : "") +
      (b.userWaiting && left ? '<div style="opacity:.85">Paused for your request — resumes automatically.</div>' : "") +
      (b.cur && !b.paused ? '<div style="opacity:.85">Now: ' + L(b.cur) + "</div>" : "") +
      (left && !b.paused
        ? '<div style="opacity:.85;font-size:12px;margin-top:2px">Don’t process applications on the portal in another tab until this finishes.</div>'
        : "") +
      (b.needKey ? '<div style="margin-top:2px">Tap “Analyse” on any application once to enter the access key — background analysis starts after that.</div>' : "") +
      '<div style="margin-top:6px;display:flex;gap:6px">' +
      (left
        ? '<button id="rpbgP" style="padding:5px 10px;font-size:12px">' + (b.paused ? "Resume" : "Pause") + "</button>"
        : "") +
      '<button id="rpbgX" style="padding:5px 10px;font-size:12px">Hide</button></div>';
    var pb = y.getElementById("rpbgP");
    pb &&
      (pb.onclick = function () {
        b.paused = !b.paused;
        rpPanel();
        b.paused || rpLoop(b.gen);
      });
    y.getElementById("rpbgX").onclick = function () {
      p.style.display = "none";
    };
    return p;
  }
  function rpMarkButtons() {
    Array.prototype.forEach.call(w.querySelectorAll(".ana"), function (btn) {
      var it = (rpBG.items || []).filter(function (t) {
        return rpKey(t) === btn.dataset.k;
      })[0];
      if (!it) return;
      var ready = rpReady(it);
      btn.textContent = ready ? "Open analysis ✓ (ready)" : "Analyse with village records";
      btn.style.background = ready ? "#1a7f5a" : "#12355b";
    });
  }
  function rpStartBackground(items) {
    if (!window.__rpApiBase) return;
    if (items) {
      rpBG.gen++;
      rpBG.items = items;
      rpBG.queue = items.filter(function (e) {
        return rpEligible(e) && !rpReady(e);
      });
      rpBG.total = items.filter(rpEligible).length;
      rpBG.done = rpBG.total - rpBG.queue.length;
      rpBG.failed = 0;
      rpBG.paused = !1;
    }
    rpBG.needKey = !rpGetKey(!1) && rpBG.queue.length > 0;
    rpPanel();
    rpMarkButtons();
    if (!rpBG.needKey && !rpBG.running) rpLoop(rpBG.gen);
  }
  async function rpLoop(gen) {
    if (rpBG.running) return;
    rpBG.running = !0;
    try {
      while (rpBG.queue.length && !rpBG.paused && gen === rpBG.gen && !A && !rpBG.userWaiting) {
        var e = rpBG.queue.shift();
        if (rpReady(e)) {
          rpBG.done++;
          continue;
        }
        rpBG.cur = (e.name || e.appNo) + (e.village ? " · " + e.village : "") + (e.khasra ? " · khasra " + e.khasra : "");
        rpPanel();
        try {
          await rpRunFor(e, function () {}, !0);
          rpBG.done++;
        } catch (err) {
          if (err && err.stage === "aborted") {
            rpBG.queue.unshift(e); // put it back; resume after your request
            rpBG.cur = "";
            rpPanel();
            break;
          }
          rpBG.failed++;
          if (err && err.stage === "key") {
            rpBG.needKey = !0;
            rpBG.queue.unshift(e);
            break;
          }
          if (err && err.stage === "connecting") {
            rpBG.queue.unshift(e);
            rpBG.failed--;
            await C(30000); // Render waking up — retry in 30 s
          }
        }
        rpBG.cur = "";
        rpPanel();
        rpMarkButtons();
        await C(300);
      }
    } finally {
      rpBG.running = !1;
      rpBG.cur = "";
      rpPanel();
    }
  }
  // ───── v1.9.9 Fard register ─────
  // On opening, every application known from earlier scans (this browser or the online register) is shown at once with its
  // saved analysis. In the background: the Dashboard list is compared with the register — new applications are read and
  // analysed first, those no longer on the list go to the archive (disposed), then the others are re-read quietly and only
  // the ones whose stage changed, that were resubmitted or whose documents changed are analysed again.
  var rpReg = { on: !1, gen: 0, running: !1, phase: "", msg: "", M: null, pending: [], reading: "", newKeys: {}, upd: {}, doneN: 0, totN: 0, days: 365 };
  var RP_REFRESH_GAP = 20 * 6e4; // existing applications re-read at most every 20 minutes
  function rpDisposedAll() {
    var m = rpJ("rpDisposed"),
      cut = Date.now() - rpReg.days * 864e5,
      out = {};
    Object.keys(m).forEach(function (k) {
      m[k] && (m[k].disposedAt || m[k].at || 0) >= cut && (out[k] = m[k]);
    });
    return out;
  }
  function rpDisposedPut(add, back) {
    var m = rpDisposedAll();
    Object.keys(add || {}).forEach(function (k) {
      m[k] = add[k];
    });
    (back || []).forEach(function (k) {
      delete m[k];
    });
    try {
      localStorage.setItem("rpDisposed", JSON.stringify(m));
    } catch (x) {}
    (Object.keys(add || {}).length || (back || []).length) &&
      rpSyncCall("POST", "/api/sync/disposed", { items: add || {}, back: back || [] }).catch(function () {});
  }
  async function rpDisposedPull() {
    try {
      var j = await rpSyncCall("GET", "/api/sync/disposed");
      j.days && (rpReg.days = j.days);
      rpMergeLocal("rpDisposed", j.items || {});
      rpRegPaint();
    } catch (x) {}
  }
  function rpSlim(e) {
    var g = (rpReady(e) || {}).gist || (rpJ("rpGistRemote")[rpKey(e)] || {}).gist || null;
    return {
      appNo: e.appNo, service: e.service, svc: e.svc || "", name: e.name || "", village: e.village || "", khasra: e.khasra || "",
      appDate: e.appDate || "", stage: e.stage || "", patReport: e.patReport || "", lastBy: e.lastBy || "", lastRemark: String(e.lastRemark || "").slice(0, 300),
      stageN: rpStage(e), ver: rpVer(e), gist: g, disposedAt: Date.now(), at: Date.now(),
    };
  }
  function rpCurrentRows() {
    var n = x.forms[0],
      h = n && he(n),
      out = { plan: [], refs: {}, svc: h ? h.value : "", service: h && h.options[h.selectedIndex] ? h.options[h.selectedIndex].text : "" };
    G(x).forEach(function (E) {
      var pl = {
        service: out.service, svc: out.svc, appNo: E.appNo, name: E.name, mobile: E.mobile, village: E.village,
        khasra: E.khasra, purpose: E.purpose, appDate: E.appDate, revert: E.revert, days: E.days,
      };
      out.plan.push(pl), (out.refs[rpScanKey(pl)] = { row: E, baseUrl: k });
    });
    return out;
  }
  function rpRegSaveLocal(reg) {
    try {
      localStorage.setItem(t, JSON.stringify(reg));
    } catch (x) {}
  }
  function rpRegShow(reg, first) {
    rpReg.M = reg;
    reg.partial = !1;
    first && (N.sum = !0); // the Stage 1 / Stage 2 tables are the "Ready" lists of the register
    rpShowResults(reg);
    first && rpStartBackground(reg.items);
  }
  async function rpRegisterOpen(local) {
    rpReg.on = !0;
    var gen = ++rpReg.gen,
      cur = rpCurrentRows(),
      reg = local && local.items ? local : null;
    rpReg.phase = "open";
    rpReg.msg = "Checking the online register …";
    if (reg) rpRegShow(reg, !0);
    else w.innerHTML = '<div class="card"><h3>Opening the register …</h3><p class="muted" style="margin:0">Loading the applications saved online.</p></div>';
    var online = null;
    try {
      var j = await rpSyncCall("GET", "/api/sync/index");
      if (j.configured) {
        var me_ = (j.index || {})[rpLogin()];
        if (me_ && (!reg || (me_.at || 0) > (reg.at || 0))) {
          var r2 = await rpSyncCall("GET", "/api/sync/scan?login=" + encodeURIComponent(rpLogin()));
          r2.scan && r2.scan.items && (online = r2.scan);
        }
        await rpSyncPull();
        rpDisposedPull();
      }
    } catch (x) {}
    if (gen !== rpReg.gen) return;
    if (online) (reg = online), rpRegSaveLocal(reg), rpRegShow(reg, !0);
    if (!reg) return (rpReg.on = !1), ge(!0); // first time on this login: the normal start screen
    rpRegisterRefresh(reg, cur, gen);
  }
  function rpWhyChanged(o, n) {
    var a = rpStage(o),
      b = rpStage(n);
    if (a !== b) return b === 2 ? "Patwari's report and tatima submitted — now Stage 2" : "back to Stage 1 (report or tatima withdrawn)";
    if (b === 2 && rpPatCount(n) > rpPatCount(o)) return "Patwari resubmitted his report";
    if ((n.docs || []).length !== (o.docs || []).length) return "documents changed (" + (o.docs || []).length + " → " + (n.docs || []).length + ")";
    return "application details changed";
  }
  // put one application in the background-analysis queue: new ones first (prio 0), updated ones next (1), the rest after (2)
  function rpBGAdd(e, prio) {
    var k = rpKey(e);
    rpBG.queue = rpBG.queue.filter(function (q) {
      return rpKey(q) !== k;
    });
    if (rpEligible(e) && !rpReady(e)) {
      e._prio = prio;
      var at = rpBG.queue.length;
      for (var i = 0; i < rpBG.queue.length; i++)
        if ((rpBG.queue[i]._prio == null ? 2 : rpBG.queue[i]._prio) > prio) {
          at = i;
          break;
        }
      rpBG.queue.splice(at, 0, e);
    }
    rpBG.total = (rpBG.items || []).filter(rpEligible).length;
    rpBG.done = Math.max(0, rpBG.total - rpBG.queue.length - (rpBG.cur ? 1 : 0));
    rpStartBackground();
  }
  async function rpRegisterRefresh(reg, cur, gen) {
    if (rpReg.running) return;
    rpReg.running = !0;
    var tm = [],
      onList = {},
      dirty = 0;
    function alive() {
      return gen === rpReg.gen && !A;
    }
    function same(e) {
      return onList[e.appNo] ? !0 : cur.svc && e.svc ? e.svc === cur.svc : (e.service || "") === cur.service;
    }
    function idxOf(key) {
      for (var i = 0; i < reg.items.length; i++) if (reg.items[i].appNo === key) return i;
      return -1;
    }
    function dispose(list) {
      var add = {};
      list.forEach(function (e) {
        add[rpKey(e)] = rpSlim(e);
        var i = idxOf(e.appNo);
        i >= 0 && reg.items.splice(i, 1);
        rpBG.queue = rpBG.queue.filter(function (q) {
          return rpKey(q) !== rpKey(e);
        });
      });
      list.length && (rpDisposedPut(add), dirty++);
    }
    try {
      if (!cur.plan.length) {
        rpReg.phase = "done";
        rpReg.msg = "No application list on this Dashboard page — showing the register as last saved.";
        return rpRegPaint();
      }
      // 1 · compare the Dashboard list with the register
      cur.plan.forEach(function (p) {
        onList[p.appNo] = p;
      });
      var have = {};
      reg.items.forEach(function (e) {
        have[e.appNo] = e;
      });
      dispose(
        reg.items.filter(function (e) {
          return same(e) && !onList[e.appNo];
        }),
      );
      var newRows = cur.plan.filter(function (p) {
          return !have[p.appNo];
        }),
        arch = rpDisposedAll(),
        back = newRows
          .map(function (p) {
            return p.appNo + "|" + p.service;
          })
          .filter(function (k) {
            return arch[k];
          });
      back.length && rpDisposedPut({}, back);
      rpReg.pending = newRows.slice();
      rpReg.phase = "new";
      rpReg.totN = newRows.length;
      rpReg.doneN = 0;
      rpReg.msg = newRows.length ? "Reading " + newRows.length + " new application(s) …" : "";
      dirty && (rpRegSaveLocal(reg), rpShowResults(reg));
      rpRegPaint();
      // 2 · new applications: read, then analysed first
      for (var i = 0; i < newRows.length && alive(); i++) {
        var E = newRows[i];
        rpReg.reading = E.appNo;
        rpRegPaint();
        var one = await rpPortal(function () {
          return rpReadOne(E, null, !1, tm, 0);
        });
        rpReg.pending = rpReg.pending.filter(function (p) {
          return p !== E;
        });
        rpReg.doneN++;
        if (one.logout) {
          rpReg.phase = "stopped";
          rpReg.msg = "The portal logged you out — log in again and run Tracker; the register is kept.";
          return rpRegPaint();
        }
        if (one.gone) continue;
        reg.items.push(one.item);
        rpReg.newKeys[rpKey(one.item)] = Date.now();
        rpBG.items !== reg.items && (rpBG.items = reg.items);
        rpBGAdd(one.item, 0);
        rpRegSaveLocal(reg);
        rpShowResults(reg);
      }
      rpReg.reading = "";
      if (!alive()) return;
      newRows.length && ((reg.at = Date.now()), rpRegSaveLocal(reg), rpSyncScan(reg));
      // 3 · quiet refresh of the others
      var ex = reg.items.filter(function (e) {
        return onList[e.appNo] && !rpReg.newKeys[rpKey(e)] && Date.now() - (e.readAt || 0) > (window.__rpRefreshGap != null ? window.__rpRefreshGap : RP_REFRESH_GAP);
      });
      rpReg.phase = "refresh";
      rpReg.totN = ex.length;
      rpReg.doneN = 0;
      rpReg.msg = "";
      rpRegPaint();
      for (var j2 = 0; j2 < ex.length && alive(); j2++) {
        var old = ex[j2],
          k2 = old.appNo,
          E2 = onList[k2];
        rpReg.reading = old.appNo;
        rpRegPaint();
        var r2 = await rpPortal(function () {
          return rpReadOne(E2, null, !1, tm, old.set || 0);
        });
        rpReg.doneN++;
        if (r2.logout) {
          rpReg.phase = "stopped";
          rpReg.msg = "The portal logged you out after " + rpReg.doneN + " of " + rpReg.totN + " — log in again and run Tracker; the rest are refreshed then.";
          break;
        }
        if (r2.gone) {
          dispose([old]);
          continue;
        }
        if (r2.item.err) continue; // keep what we had
        var ix = idxOf(k2);
        if (ix < 0) continue;
        var nu = r2.item,
          changed = rpVer(old) !== rpVer(nu);
        nu.set = old.set;
        reg.items[ix] = nu;
        if (changed) (rpReg.upd[rpKey(nu)] = { why: rpWhyChanged(old, nu), at: Date.now() }), rpBGAdd(nu, 1);
        else
          rpBG.queue = rpBG.queue.map(function (q) {
            return q === old ? nu : q;
          });
        if (changed || nu.stage !== old.stage || nu.lastT !== old.lastT || nu.lastRemark !== old.lastRemark) dirty++;
        if (dirty >= 5 || changed) (dirty = 0), rpRegSaveLocal(reg), rpShowResults(reg);
      }
      rpReg.reading = "";
      if (gen !== rpReg.gen) return;
      reg.at = Date.now();
      rpReg.phase === "stopped" || ((reg.refreshedAt = reg.at), (rpReg.phase = "done"), (rpReg.msg = ""));
      try {
        de(reg.items, reg.at);
      } catch (x) {}
      rpRegSaveLocal(reg);
      rpSyncScan(reg);
      rpShowResults(reg);
    } catch (err) {
      rpReg.phase = "stopped";
      rpReg.msg = "Refresh stopped: " + String((err && err.message) || err).slice(0, 150);
      rpRegPaint();
    } finally {
      rpReg.running = !1;
      rpReg.reading = "";
      rpRegPaint();
    }
  }
  function rpRegStatus(e) {
    if (e.err) return '<span style="color:#b42318">could not be read — tap Full rescan later</span>';
    if (rpReady(e)) return '<b style="color:#145c36">ready ✓</b>';
    if (!rpEligible(e)) return '<span class="muted">no documents to analyse</span>';
    if (rpCurrent && rpCurrent.ck === rpKey(e)) return '<b style="color:#12355b">being analysed now …</b>';
    return '<span style="color:#8a5300">queued for analysis</span>';
  }
  function rpRegRow(e, extra) {
    var g = (rpReady(e) || {}).gist || null;
    return (
      '<tr class="regr" data-k="' + L(rpKey(e)) + '" style="cursor:pointer"><td><b>…' + L(String(e.appNo || "").slice(-4)) + '</b><div class="muted">' + L(e.service || "") +
      "</div></td><td>" + L(e.name || "") + "</td><td>" + L(e.village || "") + "</td><td>" + L(e.khasra || "") + "</td><td>" + (extra ? extra + "<br>" : "") + rpRegStatus(e) +
      (g && g.text ? '<div class="muted">' + (g.score == null ? "" : "<b>" + g.score + "/100</b> — ") + L(g.text) + "</div>" : "") + "</td></tr>"
    );
  }
  var RP_REG_HEAD = '<div class="scroll"><table><thead><tr><th>App. no.</th><th>Applicant</th><th>Village</th><th>Survey no.</th><th>Status</th></tr></thead><tbody>';
  function rpRegPaint() {
    try {
      if (!rpReg.on || !rpReg.M) return;
      var top = y.getElementById("rpregnew"),
        bot = y.getElementById("rpregrest");
      if (!top || !bot) return;
      var reg = rpReg.M,
        byKey = {};
      reg.items.forEach(function (e) {
        byKey[rpKey(e)] = e;
      });
      var ph = rpReg.phase,
        line =
          ph === "open"
            ? "Checking the online register …"
            : ph === "new"
              ? "Reading new applications · " + rpReg.doneN + " of " + rpReg.totN
              : ph === "refresh"
                ? "Refreshing the other applications quietly · " + rpReg.doneN + " of " + rpReg.totN + " re-read — only a changed stage, a resubmission or changed documents is analysed again"
                : ph === "done"
                  ? "Up to date — Dashboard list checked " + new Date(reg.at || Date.now()).toLocaleTimeString()
                  : "";
      rpReg.msg && (line = rpReg.msg + (line && ph !== "stopped" ? " · " + line : ""));
      var newer = Object.keys(rpReg.newKeys)
          .map(function (k) {
            return byKey[k];
          })
          .filter(Boolean),
        rows =
          rpReg.pending
            .map(function (p) {
              return (
                "<tr><td><b>…" + L(String(p.appNo || "").slice(-4)) + "</b></td><td>" + L(p.name || "") + "</td><td>" + L(p.village || "") + "</td><td>" + L(p.khasra || "") + "</td><td>" +
                (rpReg.reading === p.appNo ? '<b style="color:#12355b">being read from the portal …</b>' : '<span class="muted">new — being prepared</span>') + "</td></tr>"
              );
            })
            .join("") +
          newer
            .map(function (e) {
              return rpRegRow(e, '<b style="color:#5b3fa8">New</b>');
            })
            .join("");
      var busy = rpReg.running && (ph === "new" || ph === "refresh");
      top.innerHTML =
        '<div class="card" style="border:2px solid #5b3fa8"><h3 style="margin-bottom:4px">Fard register · ' + reg.items.length + ' applications <span class="muted">(' +
        L(rpLogin().replace(/-/g, " ")) + ")</span></h3>" +
        '<div class="muted" style="margin:0 0 6px;' + (ph === "stopped" ? "color:#8a5300" : "") + '">' + (busy ? "⟳ " : "") + L(line) +
        (ph === "refresh" && rpReg.totN ? '<div class="prog" style="height:5px;margin-top:4px"><i style="width:' + Math.round((rpReg.doneN / rpReg.totN) * 100) + '%"></i></div>' : "") +
        "</div>" +
        (rows
          ? "<b>New since last time (" + (rpReg.pending.length + newer.length) + ")</b> — read and analysed first" + RP_REG_HEAD + rows + "</tbody></table></div>"
          : ph === "open" || ph === "new"
            ? ""
            : '<div class="muted">No new applications on this list since the last check.</div>') +
        "</div>";
      var upd = Object.keys(rpReg.upd)
          .map(function (k) {
            var e = byKey[k];
            return e ? rpRegRow(e, L(rpReg.upd[k].why)) : "";
          })
          .join(""),
        arch = rpDisposedAll(),
        ak = Object.keys(arch).sort(function (a, b) {
          return (arch[b].disposedAt || 0) - (arch[a].disposedAt || 0);
        });
      bot.innerHTML =
        (upd
          ? '<div class="card"><h3>Updating (' + Object.keys(rpReg.upd).length + ')</h3><div class="muted" style="margin:-4px 0 6px">Changed since the last check — analysed again in the background (after the new ones).</div>' +
            RP_REG_HEAD + upd + "</tbody></table></div></div>"
          : "") +
        '<div class="card"><details id="rparch"' + (rpReg.archOpen ? " open" : "") + '><summary style="cursor:pointer"><b>Disposed — archive (' + ak.length +
        ")</b> <span class=\"muted\">applications no longer on the Dashboard list, kept " + Math.round(rpReg.days / 30) + " months</span></summary>" +
        (ak.length
          ? RP_REG_HEAD.replace("<th>Status</th>", "<th>Last seen</th>") +
            ak
              .slice(0, 400)
              .map(function (k) {
                var a = arch[k],
                  g = a.gist;
                return (
                  '<tr class="arcr" data-k="' + L(k) + '" style="cursor:pointer"><td><b>…' + L(String(a.appNo || "").slice(-4)) + '</b><div class="muted">' + L(a.service || "") + "</div></td><td>" +
                  L(a.name) + "</td><td>" + L(a.village) + "</td><td>" + L(a.khasra) + "</td><td>Disposed by " + L(new Date(a.disposedAt).toLocaleDateString("en-IN")) +
                  " · last " + L(a.stage || "") + " · Stage " + (a.stageN || 1) +
                  (g && g.text ? '<div class="muted">' + (g.score == null ? "" : "<b>" + g.score + "/100</b> — ") + L(g.text) + "</div>" : "") + "</td></tr>"
                );
              })
              .join("") +
            "</tbody></table></div>" + (ak.length > 400 ? '<div class="muted">Showing the latest 400.</div>' : "")
          : '<div class="muted" style="margin-top:6px">None yet.</div>') +
        "</details></div>";
      Array.prototype.forEach.call(w.querySelectorAll("tr.regr"), function (r) {
        r.onclick = function () {
          var e = byKey[r.dataset.k];
          e && rpReady(e) ? rpAnalyse(e, !1) : rpSumGo && rpSumGo(r.dataset.k);
        };
      });
      var det = y.getElementById("rparch");
      det &&
        (det.ontoggle = function () {
          rpReg.archOpen = det.open;
        });
      Array.prototype.forEach.call(w.querySelectorAll("tr.arcr"), function (r) {
        r.onclick = function () {
          var a = arch[r.dataset.k];
          a && rpAnalyse(Object.assign({ _archived: !0 }, a), !1);
        };
      });
    } catch (x) {}
  }
  function Re(e) {
    return null != e.stageDays ? e.stageDays : e.days;
  }
  var RP_TRACKER_VERSION = "1.9.9";
  (function () {
    try {
      window.__rpApiBase && fetch(window.__rpApiBase + "/api/ping", { cache: "no-store" }).catch(function () {});
    } catch (x) {}
  })();
  // Keep the screen awake (like a video) while the tracker is working: scanning, background analysis or your analysis.
  // Uses the browser's Screen Wake Lock (Chrome / Edge on PC and Android, Safari 16.4+); released as soon as work stops.
  var rpWakeLock = null,
    rpWakeBusy = !1;
  function rpBusyNow() {
    try {
      return !!(A || (rpBG && (rpBG.running || rpBG.cur)) || rpCurrent);
    } catch (x) {
      return !1;
    }
  }
  function rpWakeShow() {
    try {
      var el = y.getElementById("rpwake");
      if (!el) return;
      if (!rpWakeBusy) return (el.textContent = ""), void 0;
      el.textContent = rpWakeLock
        ? " · ☀ screen kept on while working"
        : "wakeLock" in navigator
          ? " · screen may sleep — tap anywhere on the tracker once"
          : " · this browser can't keep the screen on — set screen timeout to “Never” while scanning";
    } catch (x) {}
  }
  async function rpWakeTick() {
    var busy = rpBusyNow();
    rpWakeBusy = busy;
    try {
      if (busy && !rpWakeLock && "wakeLock" in navigator && document.visibilityState === "visible") {
        rpWakeLock = await navigator.wakeLock.request("screen");
        rpWakeLock.addEventListener("release", function () {
          rpWakeLock = null;
          rpWakeShow();
        });
      } else if (!busy && rpWakeLock) {
        var l = rpWakeLock;
        rpWakeLock = null;
        await l.release();
      }
    } catch (x) {}
    rpWakeShow();
  }
  setInterval(rpWakeTick, 2000);
  document.addEventListener("visibilitychange", rpWakeTick);
  // a tap counts as user activation, which some browsers need before granting the lock
  document.addEventListener("pointerdown", function () {
    rpWakeBusy && !rpWakeLock && rpWakeTick();
  }, !0);
  function rpVersionBadge() {
    try {
      var el = y.getElementById("rpver"),
        sv = window.__rpVersion;
      if (!el) return;
      el.textContent = "version " + RP_TRACKER_VERSION;
      if (sv && sv !== RP_TRACKER_VERSION)
        (el.textContent = "⚠ tracker v" + RP_TRACKER_VERSION + " but server v" + sv + " — upload all files to GitHub"), (el.style.color = "#ffd27a");
    } catch (x) {}
  }
  function Ne(e) {
    rpVersionBadge();
    var t = e.items;
    rpScanAt = e.at;
    function r(e) {
      return t.filter(e).length;
    }
    !(function (e) {
      var t = {},
        a = {};
      e.forEach(function (e) {
        (e.history || []).forEach(function (r) {
          var n = te(r.by);
          if (
            n &&
            r.by !== n &&
            (((t[n] = t[n] || {})[r.by] = 1), "Patwari" === n)
          ) {
            var i = e.village || "—";
            (a[i] = a[i] || {})[r.by] = ((a[i] || {})[r.by] || 0) + 1;
          }
        });
      }),
        (c = { role: {}, village: {} }),
        Object.keys(t).forEach(function (e) {
          var a = Object.keys(t[e]);
          1 === a.length && (c.role[e] = a[0]);
        }),
        Object.keys(a).forEach(function (e) {
          var t = Object.keys(a[e]).sort(function (t, r) {
            return a[e][r] - a[e][t];
          });
          c.village[e] = t[0];
        });
    })(t);
    var n = a
      .concat(["Tehsildar acted", "Unknown holder", "Could not read"])
      .filter(function (e) {
        return r(function (t) {
          return t.stage === e;
        });
      });
    !(function i() {
      var o = (function () {
          var e = N.q.toLowerCase();
          return t
            .filter(function (t) {
              if (N.stage && t.stage !== N.stage) return !1;
              if (
                N.age &&
                ((a = Re(t)) <= 7 ? "0–7" : a <= 15 ? "8–15" : "16+") !== N.age
              )
                return !1;
              var a;
              if (N.flags && !t.flag) return !1;
              if (N.errs && !/Error:/.test(t.flag)) return !1;
              if (N.level && t.level !== N.level) return !1;
              if (N.village && (t.village || "—") !== N.village) return !1;
              if (N.over) {
                var r = ce(t);
                if (
                  !r ||
                  !r.overdue.length ||
                  ("all" !== N.over && r.overdue[0].role !== N.over)
                )
                  return !1;
              }
              return !(
                (N.scr &&
                  !H(t).some(function (e) {
                    return "red" === e.l;
                  })) ||
                (e &&
                  [
                    t.appNo,
                    t.name,
                    t.mobile,
                    t.village,
                    t.khasra,
                    t.khewat,
                    t.service,
                    t.holder,
                    t.vendee,
                  ]
                    .join(" ")
                    .toLowerCase()
                    .indexOf(e) < 0)
              );
            })
            .sort(function (e, t) {
              return Re(t) - Re(e) || t.days - e.days;
            });
        })(),
        l =
          '<div class="tiles"><div class="tile' +
          (N.stage || N.flags || N.errs || N.scr ? "" : " on") +
          '" data-s=""><div class="n">' +
          t.length +
          '</div><div class="l">All pending</div></div>' +
          n
            .map(function (e) {
              return (
                '<div class="tile' +
                (N.stage === e ? " on" : "") +
                '" data-s="' +
                L(e) +
                '"><div class="n">' +
                r(function (t) {
                  return t.stage === e;
                }) +
                '</div><div class="l">' +
                L(e) +
                "</div></div>"
              );
            })
            .join("") +
          '<div class="tile' +
          (N.errs ? " on" : "") +
          '" data-e="1"><div class="n" style="color:#c62828">' +
          r(function (e) {
            return /Error:/.test(e.flag);
          }) +
          '</div><div class="l">Errors (report pending but moved ahead)</div></div><div class="tile' +
          (N.scr ? " on" : "") +
          '" data-c="1"><div class="n" style="color:#b42318">' +
          r(function (e) {
            return H(e).some(function (e) {
              return "red" === e.l;
            });
          }) +
          '</div><div class="l">Serious scrutiny issues</div></div><div class="tile' +
          (N.flags ? " on" : "") +
          '" data-f="1"><div class="n" style="color:#c62828">' +
          r(function (e) {
            return e.flag;
          }) +
          '</div><div class="l">Flagged</div></div></div>',
        d = {};
      t.forEach(function (e) {
        var t = e.village || "—";
        (d[t] = d[t] || { t: 0 }),
          d[t].t++,
          (d[t][e.stage] = (d[t][e.stage] || 0) + 1);
      });
      var c = Object.keys(d)
        .sort(function (e, t) {
          return d[t].t - d[e].t;
        })
        .map(function (e) {
          return (
            "<tr><td>" +
            L(e) +
            "</td>" +
            n
              .map(function (t) {
                return "<td>" + (d[e][t] || "") + "</td>";
              })
              .join("") +
            "<td><b>" +
            d[e].t +
            "</b></td></tr>"
          );
        })
        .join("");
      (w.innerHTML =
        '<div class="tools"><span class="muted">Scanned ' +
        L(new Date(e.at).toLocaleString()) +
        (e.loggedOut
          ? " (stopped: the portal logged you out — log in again and rescan)"
          : e.partial
            ? " (stopped early)"
            : "") +
        '</span><span style="flex:1"></span><button id="rpsumbtn" style="background:#5b3fa8;color:#fff">' + (N.sum ? "Hide analysis summary" : "Analysis summary") + '</button><button id="rpreall" title="Discard all saved analyses and analyse every application again with version ' + L(rpAppVersion()) + '">Re-analyse all</button><button id="stpdf" style="background:#12355b;color:#fff">Status PDF</button><button id="csv">Download Excel (CSV)</button><button id="json">Download all data</button><button id="wa">Copy summary</button><button id="again" title="Read every application again from the start screen">' + (rpReg.on ? "Full rescan" : "New scan") + "</button></div>" +
        '<div id="rpregnew"></div><div id="rpsum"' + (N.sum ? "" : " hidden") + ">" + (N.sum ? rpSumHtml(t) : "") + '</div><div id="rpregrest"></div>' +
        l +
        (t.some(function (e) {
          return e.level;
        })
          ? '<div class="card"><h3>Who commented last</h3><div class="lvl">' +
            O.map(function (e) {
              var t = r(function (t) {
                return t.level === e[0];
              });
              return t || "Tehsildar" !== e[0]
                ? '<div class="lv ' +
                    e[1] +
                    (N.level === e[0] ? " on" : "") +
                    '" data-l="' +
                    e[0] +
                    '"><div class="n">' +
                    t +
                    '</div><div class="l">' +
                    e[3] +
                    "</div></div>"
                : "";
            }).join("") +
            "</div></div>"
          : "") +
        (function () {
          var e = ee(),
            a = t
              .map(function (t) {
                return { it: t, c: ce(t, e) };
              })
              .filter(function (e) {
                return e.c;
              });
          if (!a.length) return "";
          var r = {
              Patwari: [0, 0],
              Girdawar: [0, 0],
              "Naib Tehsildar": [0, 0],
            },
            n = 0;
          a.forEach(function (e) {
            var t = e.c.overdue[0];
            t && (r[t.role][t.inherited ? 1 : 0]++, n++);
          });
          var i = N.tlEdit
            ? '<div class="tools" style="margin:6px 0">Patwari <input class="num" id="sp" type="number" min="1" value="' +
              e.pat +
              '"> Girdawar <input class="num" id="sg" type="number" min="1" value="' +
              e.gir +
              '"> Naib Tehsildar <input class="num" id="sn" type="number" min="1" value="' +
              e.nt +
              '"> days, counted <select id="sm"><option value="app"' +
              ("app" === e.mode ? " selected" : "") +
              '>from the Application / Resubmit date (as the portal counts)</option><option value="stage"' +
              ("stage" === e.mode ? " selected" : "") +
              '>from when each officer receives the file</option></select> <button class="pri" id="ssave">Save</button></div><div style="margin:6px 0"><div class="muted">Holidays skipped in the count (one date per line, YYYY-MM-DD). Sundays are always skipped.</div><textarea id="shol" rows="6" style="width:100%;max-width:420px;font:12px ui-monospace,monospace;border:1px solid #c9ced8;border-radius:6px;padding:6px">' +
              L((e.holidays || p).join(" ")).replace(/ /g, "\n") +
              "</textarea></div>"
            : '<div class="muted" style="margin-bottom:8px">Limits: Patwari ' +
              e.pat +
              " · Girdawar " +
              e.gir +
              " · Naib Tehsildar " +
              e.nt +
              " days from the " +
              ("app" === e.mode
                ? "Application / Resubmit date"
                : "date each officer receives the file") +
              ', Sundays and holidays excluded · <a href="#" id="sedit">Change</a></div>';
          function o(e, t) {
            var a = "all" === e ? n : r[e][0] + r[e][1],
              i = "all" === e ? 0 : r[e][1];
            return (
              '<div class="tile' +
              (N.over === e ? " on" : "") +
              '" data-o="' +
              e +
              '"><div class="n" style="color:' +
              (a ? m : "#145c36") +
              '">' +
              a +
              '</div><div class="l">' +
              t +
              (i
                ? '<br><span style="color:' +
                  g +
                  '">' +
                  i +
                  " due to earlier stage</span>"
                : "") +
              "</div></div>"
            );
          }
          var s =
              '<div class="tiles" style="margin-bottom:10px">' +
              o("all", "Files overdue now") +
              o("Patwari", "Overdue with Patwari") +
              o("Girdawar", "Overdue with Girdawar") +
              o("Naib Tehsildar", "Overdue with Naib Tehsildar") +
              "</div>",
            l = {};
          function d(e) {
            return (l[e] = l[e] || {
              files: 0,
              run: 0,
              P: [0, 0],
              G: [0, 0],
              N: [0, 0],
              own: [0, 0],
            });
          }
          var c = { Patwari: "P", Girdawar: "G", "Naib Tehsildar": "N" };
          a.forEach(function (e) {
            var t = e.c,
              a = t.overdue[0] || t.open[0];
            if ("village" === N.tlBy) {
              var r = d(e.it.village || "—");
              r.files++,
                !t.overdue.length && t.open.length && r.run++,
                t.overdue[0] &&
                  r[c[t.overdue[0].role]][t.overdue[0].inherited ? 1 : 0]++;
            } else if (a) {
              var n = d(
                "Patwari" === a.role
                  ? "Patwari · " + (e.it.village || "—")
                  : a.by || a.role,
              );
              (n.role = a.role),
                n.files++,
                "overdue" === a.status ? n.own[a.inherited ? 1 : 0]++ : n.run++;
            }
          });
          var u,
            f = Object.keys(l).sort(function (e, t) {
              function a(e) {
                return (
                  e.P[0] +
                  e.P[1] +
                  e.G[0] +
                  e.G[1] +
                  e.N[0] +
                  e.N[1] +
                  e.own[0] +
                  e.own[1]
                );
              }
              return (
                a(l[t]) - a(l[e]) ||
                l[t].files - l[e].files ||
                e.localeCompare(t)
              );
            });
          function h(e) {
            var t = e[0] + e[1];
            return t
              ? '<b style="color:' +
                  (e[0] ? m : g) +
                  '">' +
                  t +
                  "</b>" +
                  (e[0] && e[1]
                    ? ' <span style="color:' +
                      g +
                      ';font-size:11px">(' +
                      e[1] +
                      " earlier stage)</span>"
                    : "")
              : "";
          }
          if ("village" === N.tlBy) {
            var v = { files: 0, run: 0, P: [0, 0], G: [0, 0], N: [0, 0] };
            function b(e) {
              var t = e.P[0] + e.P[1] + e.G[0] + e.G[1] + e.N[0] + e.N[1];
              return t ? '<b style="color:' + m + '">' + t + "</b>" : "";
            }
            f.forEach(function (e) {
              var t = l[e];
              (v.files += t.files),
                (v.run += t.run),
                ["P", "G", "N"].forEach(function (e) {
                  (v[e][0] += t[e][0]), (v[e][1] += t[e][1]);
                });
            }),
              (u =
                '<table class="tlv"><thead><tr><th>Village</th><th>Files</th><th>Within limit</th><th>Overdue: Patwari</th><th>Overdue: Girdawar</th><th>Overdue: Naib Tehsildar</th><th>Overdue total</th></tr></thead><tbody>' +
                f
                  .map(function (e) {
                    var t = l[e];
                    return (
                      '<tr class="vrow' +
                      (N.village === e ? " sel" : "") +
                      '" data-v="' +
                      L(e) +
                      '"><td>' +
                      L(e) +
                      "</td><td>" +
                      t.files +
                      "</td><td>" +
                      (t.run || "") +
                      "</td><td>" +
                      h(t.P) +
                      "</td><td>" +
                      h(t.G) +
                      "</td><td>" +
                      h(t.N) +
                      "</td><td>" +
                      b(t) +
                      "</td></tr>"
                    );
                  })
                  .join("") +
                '<tr style="font-weight:700;background:#f0f2f6"><td>Total</td><td>' +
                v.files +
                "</td><td>" +
                (v.run || "") +
                "</td><td>" +
                h(v.P) +
                "</td><td>" +
                h(v.G) +
                "</td><td>" +
                h(v.N) +
                "</td><td>" +
                b(v) +
                "</td></tr></tbody></table>");
          } else
            u =
              '<table class="tlv"><thead><tr><th>Officer</th><th>Files pending</th><th>Within limit</th><th>Overdue</th></tr></thead><tbody>' +
              f
                .map(function (e) {
                  var t = l[e];
                  return (
                    "<tr><td>" +
                    L(e) +
                    "</td><td>" +
                    t.files +
                    "</td><td>" +
                    (t.run || "") +
                    "</td><td>" +
                    h(t.own) +
                    "</td></tr>"
                  );
                })
                .join("") +
              "</tbody></table>";
          return (
            '<div class="card"><div class="tools" style="margin-bottom:4px"><h3 style="margin:0;flex:1">Time-limit compliance</h3><span class="chip' +
            ("village" === N.tlBy ? " on" : "") +
            '" data-tb="village">By village</span><span class="chip' +
            ("officer" === N.tlBy ? " on" : "") +
            '" data-tb="officer">By officer</span></div>' +
            i +
            s +
            '<div class="scroll">' +
            u +
            '</div><div class="muted" style="margin-top:6px"><b style="color:' +
            m +
            '">Red</b>: the officer holding the file has not acted. <b style="color:' +
            g +
            '">Amber</b>: overdue because the earlier stage submitted late.' +
            ("village" === N.tlBy
              ? " Tap a village to list only its applications."
              : "") +
            "</div></div>"
          );
        })() +
        (N.village
          ? '<div class="tools"><span class="chip on" id="clrv">Village: ' +
            L(N.village) +
            " ×</span></div>"
          : "") +
        (t.length &&
        r(function (e) {
          return "Could not read" === e.stage;
        }) === t.length
          ? '<div class="card warn"><b>None of the application pages could be read.</b> Tap any row below and send a screenshot of the “What the portal returned” line so the tracker can be adjusted.</div>'
          : "") +
        '<div class="tools"><input class="s" id="q" placeholder="Search application no, name, mobile, village, khasra, patwari" value="' +
        L(N.q) +
        '">' +
        ["", "0–7", "8–15", "16+"]
          .map(function (e) {
            return (
              '<span class="chip' +
              (N.age === e ? " on" : "") +
              '" data-a="' +
              e +
              '">' +
              (e ? e + " days at stage" : "Any age") +
              "</span>"
            );
          })
          .join("") +
        '</div><div class="scroll"><table class="apps"><thead><tr><th>Application</th><th>Applicant</th><th>Village / Khasra</th><th>Purpose</th><th>Days</th><th>Stage</th></tr></thead><tbody>' +
        (o.length
          ? o
              .map(function (e, t) {
                var r,
                  n,
                  i,
                  o = e.appNo + "|" + e.service,
                  s = (function (e) {
                    for (var t = 0; t < O.length; t++)
                      if (O[t][0] === e) return O[t];
                    return null;
                  })(e.level);
                return (
                  '<tr class="r' +
                  (s && s[2] ? " " + s[2] : "") +
                  '" data-k="' +
                  L(o) +
                  '"><td>' +
                  L(e.appNo) +
                  (e.service
                    ? '<div class="muted">' + L(e.service) + "</div>"
                    : "") +
                  "</td><td>" +
                  L(e.name) +
                  '<div class="muted">' +
                  L(e.mobile) +
                  "</div></td><td>" +
                  L(e.village) +
                  '<div class="muted">' +
                  L(e.khasra) +
                  "</div></td><td>" +
                  L(e.purpose) +
                  (e.revert
                    ? '<div class="flag">Reverted ' + e.revert + "×</div>"
                    : "") +
                  '</td><td class="d' +
                  (Re(e) > 15 ? " hi" : "") +
                  '">' +
                  Re(e) +
                  " days" +
                  (null != e.stageDays
                    ? '<div class="muted">at this stage · ' +
                      e.days +
                      " total</div>"
                    : "") +
                  '</td><td><span class="st ' +
                  ((n = e.stage),
                  ((i = a.indexOf(n)) >= 0 && i < 4
                    ? "s" + i
                    : "Tehsildar acted" === n
                      ? "s3"
                      : "s9") + '">') +
                  L(e.stage) +
                  "</span>" +
                  (e.holder && e.holder !== e.stage.replace("With ", "")
                    ? '<div class="muted">' + L(e.holder) + "</div>"
                    : "") +
                  ("Pending" === e.patReport
                    ? '<div class="muted">Patwari report: pending</div>'
                    : "") +
                  ((function (e) {
                    if (!e) return "";
                    var t =
                      "app" === e.mode
                        ? e.dayNow +
                          " days since " +
                          (e.resub ? "resubmission" : "application")
                        : "";
                    if (e.stopped)
                      return (
                        '<div class="muted">⏱ ' +
                        t +
                        " · returned to applicant, clock stopped</div>"
                      );
                    var a = e.overdue[0];
                    if (a) {
                      var r = a.inherited ? g : m,
                        n = a.inherited
                          ? " — " + a.cause
                          : "Patwari" === a.role && a.note
                            ? " — " + a.note
                            : " — not acted yet";
                      return (
                        '<div style="color:' +
                        r +
                        ';font-size:12px;font-weight:600">⏱ ' +
                        L(a.role) +
                        " overdue by " +
                        a.over +
                        "d — " +
                        L(n.replace(/^ — /, "")) +
                        (t
                          ? ' <span style="font-weight:400">(' + t + ")</span>"
                          : "") +
                        "</div>"
                      );
                    }
                    return e.open.length
                      ? '<div style="color:' +
                          ((a = e.open[0]).left <= 1 ? g : "#145c36") +
                          ';font-size:12px;font-weight:600">⏱ ' +
                          L(a.role) +
                          (0 === a.left
                            ? " due today"
                            : " due in " +
                              a.left +
                              " day" +
                              (1 === a.left ? "" : "s")) +
                          (t
                            ? ' <span style="font-weight:400">(' +
                              t +
                              ")</span>"
                            : "") +
                          "</div>"
                      : t
                        ? '<div class="muted">⏱ ' +
                          t +
                          " · all levels have acted</div>"
                        : "";
                  })((r = ce(e))) +
                    (function (e) {
                      return e && e.late.length
                        ? '<div class="muted" style="color:' +
                            g +
                            '">Delay: ' +
                            e.late
                              .map(function (e) {
                                return (
                                  L(e.by || e.role) +
                                  " late by " +
                                  e.over +
                                  (e.overMax && e.overMax > e.over
                                    ? "–" + e.overMax
                                    : "") +
                                  "d"
                                );
                              })
                              .join(", ") +
                            "</div>"
                        : "";
                    })(r)) +
                  (e.lastBy
                    ? '<div class="muted">Last: ' +
                      L(e.lastBy) +
                      ", " +
                      L(Z(e.lastT)) +
                      "</div>"
                    : "") +
                  (e.flag
                    ? '<div class="flag">⚠ ' + L(e.flag) + "</div>"
                    : "") +
                  "</td></tr>" +
                  (N.open[o]
                    ? '<tr class="det"><td colspan="6">' +
                      (e.history && e.history.length
                        ? "<p><b>Movement of file</b></p>" +
                          e.history
                            .map(function (e, t) {
                              return (
                                "<p>" +
                                (t + 1) +
                                ". <b>" +
                                L(Z(e.t) || e.date) +
                                " · " +
                                L(e.by) +
                                ":</b> " +
                                L(e.remark) +
                                "</p>"
                              );
                            })
                            .join("")
                        : "<p><b>Patwari:</b> " +
                          L(e.pat || "—") +
                          "</p><p><b>Girdawar:</b> " +
                          L(e.gir || "—") +
                          "</p><p><b>Naib Tehsildar:</b> " +
                          L(e.nt || "—") +
                          "</p>") +
                      (function (e) {
                        if (!e) return "";
                        var t = e.visits.filter(function (e) {
                          return "waiting" !== e.status;
                        });
                        if (!t.length) return "";
                        var a = {
                          ontime: ["On time", "#145c36"],
                          late: ["Late", m],
                          overdue: ["Overdue", m],
                          running: ["Within limit", "#145c36"],
                          moved: ["No entry", "#5b6475"],
                          stopped: ["Clock stopped", "#5b6475"],
                          reported: ["Report submitted", "#145c36"],
                        };
                        return (
                          '<p><b>Time-limit record</b> <span class="muted">(current round; Sundays and holidays excluded, as the portal counts)</span></p><div class="scroll"><table class="tl"><thead><tr><th>Officer</th><th>Counted from</th><th>Acted on</th><th>Days taken</th><th>Allowed</th><th>Status</th></tr></thead><tbody>' +
                          t
                            .map(function (e) {
                              var t =
                                "overdue" === e.status && e.inherited
                                  ? ["Overdue (earlier stage late)", g]
                                  : a[e.status];
                              return (
                                "<tr><td>" +
                                L(e.by || e.role) +
                                "</td><td>" +
                                L(Z(e.from)) +
                                "</td><td>" +
                                (e.to
                                  ? (e.est ? "by " : "") + L(Z(e.to))
                                  : e.open
                                    ? "<i>pending</i>"
                                    : "—") +
                                "</td><td>" +
                                (null != e.days
                                  ? (e.est ? "about " : "") + e.days + " days"
                                  : "—") +
                                "</td><td>Within " +
                                e.limit +
                                ' days</td><td style="color:' +
                                t[1] +
                                ';font-weight:600">' +
                                t[0] +
                                (e.over
                                  ? " by " +
                                    e.over +
                                    (e.overMax && e.overMax > e.over
                                      ? "–" + e.overMax
                                      : "") +
                                    "d"
                                  : "") +
                                ((e.inherited ? e.cause : e.note)
                                  ? '<div class="muted" style="font-weight:400">' +
                                    L(e.inherited ? e.cause : e.note) +
                                    "</div>"
                                  : "") +
                                "</td></tr>"
                              );
                            })
                            .join("") +
                          "</tbody></table></div>"
                        );
                      })(ce(e)) +
                      (function (e) {
                        var t = H(e);
                        if (!e.fields)
                          return '<p class="muted">Run a new scan to get the full scrutiny for this application.</p>';
                        if (!t.length)
                          return '<p><b>Scrutiny:</b> <span style="color:#145c36">no issues found in the captured data</span></p>';
                        var a = {
                            red: "#b42318",
                            amber: "#8a5300",
                            info: "#5b6475",
                          },
                          r = { red: "●", amber: "▲", info: "ℹ" };
                        return (
                          "<p><b>Scrutiny</b></p>" +
                          t
                            .map(function (e) {
                              return (
                                '<p style="color:' +
                                a[e.l] +
                                '">' +
                                r[e.l] +
                                " " +
                                L(e.t) +
                                "</p>"
                              );
                            })
                            .join("")
                        );
                      })(e) +
                      '<div class="docs"><button class="cpy" data-k="' +
                      L(o) +
                      '">Copy case for Claude</button>' +
                      (window.__rpApiBase
                        ? '<button class="ana" style="background:#12355b;color:#fff" data-k="' +
                          L(o) +
                          '">Analyse with village records</button>'
                        : "") +
                      '<button class="sav" style="background:#5b3fa8;color:#fff" data-k="' +
                      L(o) +
                      '">Save record to folder</button>' +
                      (window.showDirectoryPicker ? '<button class="savdir" title="Choose a different folder for saved records">Change save folder</button>' : "") +
                      "</div>" +
                      (e.docs && e.docs.length
                        ? '<p><b>Uploaded documents</b></p><div class="docs">' +
                          e.docs
                            .slice()
                            .sort(function (e, t) {
                              return (
                                (/^All documents/.test(e.label) ? 1 : 0) -
                                  (/^All documents/.test(t.label) ? 1 : 0) ||
                                e.i - t.i
                              );
                            })
                            .map(function (e) {
                              return (
                                '<button class="docbtn" data-k="' +
                                L(o) +
                                '" data-d="' +
                                e.i +
                                '">' +
                                L(e.label) +
                                "</button>"
                              );
                            })
                            .join("") +
                          "</div>"
                        : e.docs
                          ? ""
                          : '<p class="muted">Run a new scan to see documents for this application.</p>') +
                      (e.vendee || e.area
                        ? '<p class="muted">' +
                          (e.vendee ? "Vendee: " + L(e.vendee) : "") +
                          (e.vendee && e.area ? " · " : "") +
                          (e.area ? "Area: " + L(e.area) : "") +
                          "</p>"
                        : "") +
                      (e.diag
                        ? '<p class="muted" style="word-break:break-word"><b>What the portal returned:</b> ' +
                          L(e.diag) +
                          "</p>"
                        : "") +
                      '<p class="muted">Khewat ' +
                      L(e.khewat || "—") +
                      " · Applied " +
                      L(e.appDate || "—") +
                      "</p></td></tr>"
                    : "")
                );
              })
              .join("")
          : '<tr><td colspan="6" class="muted">No applications match.</td></tr>') +
        "</tbody></table></div>" +
        (function (e) {
          var t = {};
          e.forEach(function (e) {
            if (e.holder) {
              var a = e.holder;
              (t[a] = t[a] || { n: 0, old: 0, over: 0 }),
                t[a].n++,
                (t[a].old = Math.max(t[a].old, Re(e))),
                Re(e) > 7 && t[a].over++;
            }
          });
          var a = Object.keys(t).sort(function (e, a) {
            return t[a].n - t[e].n || t[a].old - t[e].old;
          });
          return a.length
            ? '<div class="card" style="margin-top:12px"><h3>Who is holding the files</h3><div class="scroll"><table><thead><tr><th>Holder</th><th>Files</th><th>Over 7 days</th><th>Oldest (days)</th></tr></thead><tbody>' +
                a
                  .map(function (e) {
                    return (
                      "<tr><td>" +
                      L(e) +
                      "</td><td><b>" +
                      t[e].n +
                      "</b></td><td>" +
                      (t[e].over || "") +
                      '</td><td class="d' +
                      (t[e].old > 15 ? " hi" : "") +
                      '">' +
                      t[e].old +
                      "</td></tr>"
                    );
                  })
                  .join("") +
                "</tbody></table></div></div>"
            : "";
        })(t) +
        '<div class="card" style="margin-top:12px"><h3>Village-wise pendency</h3><div class="scroll"><table><thead><tr><th>Village</th>' +
        n
          .map(function (e) {
            return "<th>" + L(e.replace("With ", "")) + "</th>";
          })
          .join("") +
        "<th>Total</th></tr></thead><tbody>" +
        c +
        "</tbody></table></div></div>"),
        Array.prototype.forEach.call(
          w.querySelectorAll(
            '.tile:not([data-o]):not([style*="cursor:default"])',
          ),
          function (e) {
            e.onclick = function () {
              if (e.dataset.c)
                return (
                  (N.scr = !N.scr),
                  (N.flags = !1),
                  (N.errs = !1),
                  (N.stage = ""),
                  void i()
                );
              (N.scr = !1),
                e.dataset.f
                  ? ((N.flags = !N.flags), (N.errs = !1), (N.stage = ""))
                  : e.dataset.e
                    ? ((N.errs = !N.errs), (N.flags = !1), (N.stage = ""))
                    : ((N.stage = e.dataset.s), (N.flags = !1), (N.errs = !1)),
                i();
            };
          },
        ),
        Array.prototype.forEach.call(
          w.querySelectorAll("[data-o]"),
          function (e) {
            e.onclick = function () {
              (N.over = N.over === e.dataset.o ? "" : e.dataset.o), i();
            };
          },
        ),
        Array.prototype.forEach.call(
          w.querySelectorAll("[data-tb]"),
          function (e) {
            e.onclick = function () {
              (N.tlBy = e.dataset.tb), i();
            };
          },
        ),
        Array.prototype.forEach.call(
          w.querySelectorAll("tr.vrow"),
          function (e) {
            e.onclick = function () {
              (N.village = N.village === e.dataset.v ? "" : e.dataset.v), i();
            };
          },
        );
      var f = y.getElementById("clrv");
      f &&
        (f.onclick = function () {
          (N.village = ""), i();
        });
      var h = y.getElementById("sedit");
      h &&
        (h.onclick = function (e) {
          e.preventDefault(), (N.tlEdit = !0), i();
        });
      var v = y.getElementById("ssave");
      v &&
        (v.onclick = function () {
          var e = y
              .getElementById("shol")
              .value.split(/[\s,]+/)
              .filter(function (e) {
                return /^\d{4}-\d{2}-\d{2}$/.test(e);
              }),
            t = {
              pat: Math.max(1, +y.getElementById("sp").value || 5),
              gir: Math.max(1, +y.getElementById("sg").value || 7),
              nt: Math.max(1, +y.getElementById("sn").value || 9),
              mode: y.getElementById("sm").value,
              holidays: e,
            };
          u = null;
          try {
            localStorage.setItem(s, JSON.stringify(t));
          } catch (e) {}
          (N.tlEdit = !1), i();
        }),
        Array.prototype.forEach.call(w.querySelectorAll(".cpy"), function (e) {
          e.onclick = function (a) {
            a.stopPropagation();
            var r = t.filter(function (t) {
              return t.appNo + "|" + t.service === e.dataset.k;
            })[0];
            if (r) {
              var n = W(r);
              navigator.clipboard && navigator.clipboard.writeText
                ? navigator.clipboard.writeText(n).then(
                    function () {
                      (e.textContent = "Copied ✓ — paste into Claude"),
                        setTimeout(function () {
                          e.textContent = "Copy case for Claude";
                        }, 2500);
                    },
                    function () {
                      prompt("Copy this:", n);
                    },
                  )
                : prompt("Copy this:", n);
            }
          };
        }),
        Array.prototype.forEach.call(w.querySelectorAll(".ana"), function (e) {
          e.onclick = function (a) {
            a.stopPropagation();
            var r = t.filter(function (t) {
              return t.appNo + "|" + t.service === e.dataset.k;
            })[0];
            r && rpAnalyse(r, !1);
          };
        }),
        Array.prototype.forEach.call(w.querySelectorAll(".sav"), function (e) {
          e.onclick = function (a) {
            a.stopPropagation();
            var r = t.filter(function (t) {
              return t.appNo + "|" + t.service === e.dataset.k;
            })[0];
            r && rpSaveRecord(r, e);
          };
        }),
        Array.prototype.forEach.call(w.querySelectorAll(".savdir"), function (e) {
          e.onclick = async function (a) {
            a.stopPropagation();
            try {
              var h = await rpSaveDir(!0);
              h && (e.textContent = "Folder: " + h.name + " ✓");
            } catch (x) {}
          };
        }),
        (rpSumItems = t),
        (function () {
          var ra = y.getElementById("rpreall");
          ra &&
            (ra.onclick = function () {
              if (!confirm("Analyse every application again with version " + rpAppVersion() + "? Saved analyses are discarded; this runs in the background and takes a while.")) return;
              rpReanalyseAll(t);
              ra.textContent = "Re-analysing …";
            });
          var bt = y.getElementById("rpsumbtn");
          bt &&
            (bt.onclick = function () {
              (N.sum = !N.sum), i();
            });
          rpSumGo = function (k) {
            (N.stage = N.age = N.q = N.level = N.village = N.over = ""), (N.flags = N.errs = N.scr = !1);
            (N.open[k] = !0), i();
            var row = Array.prototype.filter.call(w.querySelectorAll("tr.r"), function (r) {
              return r.dataset.k === k;
            })[0];
            row && row.scrollIntoView({ behavior: "smooth", block: "center" });
          };
          rpSumBind();
          rpRegPaint();
        })(),
        rpMarkButtons(),
        (function () {
          var sb = y.getElementById("stpdf");
          sb &&
            (sb.onclick = function () {
              rpStatusPdf(t, sb);
            });
        })(),
        Array.prototype.forEach.call(
          w.querySelectorAll(".docbtn"),
          function (e) {
            e.onclick = function (a) {
              a.stopPropagation();
              var r = t.filter(function (t) {
                  return t.appNo + "|" + t.service === e.dataset.k;
                })[0],
                n =
                  r &&
                  r.docs.filter(function (t) {
                    return String(t.i) === e.dataset.d;
                  })[0];
              r &&
                n &&
                (async function (e, t) {
                  S = y.getElementById("modal");
                  var a = y.getElementById("mtitle"),
                    r = y.getElementById("mbody"),
                    n = y.getElementById("macts");
                  (a.textContent = t.label + " — " + e.name),
                    (n.innerHTML = ""),
                    (r.innerHTML =
                      '<div class="muted">Fetching document…</div>'),
                    (S.hidden = !1);
                  try {
                    var i = await Ee(e, t.i, t.label),
                      o = i.type || i.blob.type || "",
                      s = i.blob.type
                        ? i.blob
                        : new Blob([i.blob], { type: o });
                    R && URL.revokeObjectURL(R), (R = URL.createObjectURL(s));
                    var l = /pdf/.test(o)
                        ? ".pdf"
                        : /png/.test(o)
                          ? ".png"
                          : /jpe?g/.test(o)
                            ? ".jpg"
                            : /zip/.test(o)
                              ? ".zip"
                              : /tif/.test(o)
                                ? ".tif"
                                : "",
                      d =
                        i.name ||
                        (e.appNo + " " + t.label).replace(/[^\w .-]+/g, "_") +
                          l,
                      c = /Android/i.test(navigator.userAgent);
                    /^image\//.test(o) && !/tif/.test(o)
                      ? (r.innerHTML = '<img alt="" src="' + R + '">')
                      : /pdf/.test(o) && !c
                        ? (r.innerHTML =
                            '<iframe title="Document" src="' +
                            R +
                            '"></iframe>')
                        : (r.innerHTML =
                            '<div class="muted" style="padding:16px;text-align:center">' +
                            (/zip/.test(o)
                              ? "This is a ZIP of all documents. Your office network may block opening ZIP files — view documents one by one instead."
                              : "Document ready (" +
                                L(o || "file") +
                                ", " +
                                Math.round(s.size / 1024) +
                                " KB). Tap Open or Save.") +
                            "</div>"),
                      (n.innerHTML =
                        '<button id="mopen">Open</button><button id="msave">Save</button>'),
                      (y.getElementById("mopen").onclick = function () {
                        window.open(R, "_blank");
                      }),
                      (y.getElementById("msave").onclick = function () {
                        var e = document.createElement("a");
                        (e.href = R),
                          (e.download = d),
                          document.body.appendChild(e),
                          e.click(),
                          e.remove();
                      });
                  } catch (e) {
                    r.innerHTML =
                      '<div class="muted" style="padding:16px;word-break:break-word"><b>Could not open the document.</b><br>' +
                      L((e && e.message) || e) +
                      "</div>";
                  }
                })(r, n);
            };
          },
        ),
        Array.prototype.forEach.call(w.querySelectorAll(".lv"), function (e) {
          e.onclick = function () {
            (N.level = N.level === e.dataset.l ? "" : e.dataset.l), i();
          };
        }),
        Array.prototype.forEach.call(
          w.querySelectorAll(".chip[data-a]"),
          function (e) {
            e.onclick = function () {
              (N.age = e.dataset.a), i();
            };
          },
        ),
        Array.prototype.forEach.call(w.querySelectorAll("tr.r"), function (e) {
          e.onclick = function () {
            var t = e.dataset.k;
            (N.open[t] = !N.open[t]), i();
          };
        });
      var b = y.getElementById("q");
      (b.oninput = function () {
        N.q = b.value;
        var e = b.selectionStart;
        i();
        var t = y.getElementById("q");
        t.focus(), t.setSelectionRange(e, e);
      }),
        (y.getElementById("csv").onclick = function () {
          !(function (e, t) {
            var a = [
                ["Service", "service"],
                ["Application No", "appNo"],
                ["Applicant", "name"],
                ["Mobile", "mobile"],
                ["Village", "village"],
                ["Khasra", "khasra"],
                ["Khewat", "khewat"],
                ["Purpose", "purpose"],
                ["Vendee", "vendee"],
                ["Area Proposed", "area"],
                ["Application Date", "appDate"],
                ["Revert Count", "revert"],
                ["Days Passed", "days"],
                ["Current Stage", "stage"],
                ["Holder", "holder"],
                ["Patwari Report", "patReport"],
                ["Last Comment Level", "levelTxt"],
                ["Last Comment By", "levelBy"],
                ["Days at Stage", "stageDays"],
                ["Last Action By", "lastBy"],
                ["Last Action Date", "lastDate"],
                ["Last Remark", "lastRemark"],
                ["Flag", "flag"],
                ["Time Status", "tlNow"],
                ["Overdue Days", "tlOver"],
                ["Late Earlier", "tlLate"],
                ["Scrutiny", "scr"],
                ["Movement History", "hist"],
                ["Read problem", "diag"],
              ],
              r = function (e) {
                return (
                  '"' +
                  (e = String(null == e ? "" : e)).replace(/"/g, '""') +
                  '"'
                );
              },
              n = [
                a
                  .map(function (e) {
                    return r(e[0]);
                  })
                  .join(","),
              ].concat(
                e.map(function (e) {
                  var t = ce(e),
                    n = {
                      tlNow: t
                        ? (t.dayNow ? "Day " + t.dayNow : "") +
                          (t.overdue.length
                            ? " · overdue: " +
                              t.overdue
                                .map(function (e) {
                                  return e.role + " +" + e.over + "d";
                                })
                                .join(", ")
                            : t.open.length
                              ? " · " +
                                t.open[0].role +
                                " due within " +
                                t.open[0].limit +
                                " days"
                              : "")
                        : "",
                      tlOver:
                        t && t.overdue.length
                          ? Math.max.apply(
                              null,
                              t.overdue.map(function (e) {
                                return e.over;
                              }),
                            )
                          : "",
                      tlLate: t
                        ? t.late
                            .map(function (e) {
                              return (e.by || e.role) + " +" + e.over + "d";
                            })
                            .join(", ")
                        : "",
                      scr: H(e)
                        .map(function (e) {
                          return e.t;
                        })
                        .join(" | "),
                      levelTxt: "None" === e.level ? "No action yet" : e.level,
                      lastDate: Z(e.lastT),
                      hist: (e.history || [])
                        .map(function (e) {
                          return (
                            (Z(e.t) || e.date) + " " + e.by + ": " + e.remark
                          );
                        })
                        .join(" | "),
                    };
                  return a
                    .map(function (t) {
                      var a = t[1] in n ? n[t[1]] : e[t[1]];
                      return "appNo" === t[1] || "mobile" === t[1]
                        ? r("⁠" + a)
                        : r(a);
                    })
                    .join(",");
                }),
              ),
              i = new Blob(["\ufeff" + n.join("\r\n")], {
                type: "text/csv;charset=utf-8",
              }),
              o = document.createElement("a");
            (o.href = URL.createObjectURL(i)),
              (o.download =
                "RevenuePlus_Pendency_" +
                new Date(t).toISOString().slice(0, 10) +
                ".csv"),
              document.body.appendChild(o),
              o.click(),
              o.remove(),
              setTimeout(function () {
                URL.revokeObjectURL(o.href);
              }, 5e3);
          })(t, e.at);
        }),
        (y.getElementById("json").onclick = function () {
          var a = t.map(function (e) {
              var t = Object.assign({}, e);
              return (t.scrutiny = H(e)), t;
            }),
            r = new Blob(
              [
                JSON.stringify(
                  {
                    scannedAt: new Date(e.at).toISOString(),
                    source: "Revenue Plus Tracker",
                    applications: a,
                  },
                  null,
                  1,
                ),
              ],
              { type: "application/json" },
            ),
            n = document.createElement("a");
          (n.href = URL.createObjectURL(r)),
            (n.download =
              "RevenuePlus_FullData_" +
              new Date(e.at).toISOString().slice(0, 10) +
              ".json"),
            document.body.appendChild(n),
            n.click(),
            n.remove();
        }),
        (y.getElementById("wa").onclick = function () {
          !(function (e, t, a, r) {
            var n = [
              "*Revenue Plus pendency — " +
                new Date(a).toLocaleDateString("en-IN") +
                "*",
              "Total pending: " + e.length,
            ];
            t.forEach(function (t) {
              n.push(
                t +
                  ": " +
                  e.filter(function (e) {
                    return e.stage === t;
                  }).length,
              );
            });
            var i = e.filter(function (e) {
              return Re(e) > 15;
            }).length;
            n.push("Stuck over 15 days at one stage: " + i);
            var o = {};
            e.forEach(function (e) {
              e.holder && (o[e.holder] = (o[e.holder] || 0) + 1);
            });
            var s = Object.keys(o).sort(function (e, t) {
              return o[t] - o[e];
            });
            s.length &&
              (n.push("", "*Holding:*"),
              s.forEach(function (e) {
                n.push(e + ": " + o[e]);
              }));
            e.some(function (e) {
              return e.level;
            }) &&
              (n.push("", "*Last comment:*"),
              O.forEach(function (t) {
                var a = e.filter(function (e) {
                  return e.level === t[0];
                }).length;
                a &&
                  n.push(("None" === t[0] ? "No action yet" : t[0]) + ": " + a);
              }));
            var l = e
                .map(function (e) {
                  return ce(e);
                })
                .filter(Boolean),
              d = ee();
            if (l.length) {
              var c = { Patwari: 0, Girdawar: 0, "Naib Tehsildar": 0 };
              l.forEach(function (e) {
                e.overdue.forEach(function (e) {
                  c[e.role]++;
                });
              }),
                n.push(
                  "",
                  "*Overdue (Patwari " +
                    d.pat +
                    ", Girdawar " +
                    d.gir +
                    ", NT " +
                    d.nt +
                    " days; Sundays & holidays excluded):*",
                  "Patwari: " + c.Patwari,
                  "Girdawar: " + c.Girdawar,
                  "Naib Tehsildar: " + c["Naib Tehsildar"],
                );
            }
            var p = e.filter(function (e) {
              return /Error:/.test(e.flag);
            }).length;
            p && n.push("Errors (moved ahead without Patwari report): " + p);
            var u = e.filter(function (e) {
              return e.flag;
            }).length;
            u && n.push("Flagged: " + u);
            var f = n.join("\n");
            function h() {
              (r.textContent = "Copied ✓"),
                setTimeout(function () {
                  r.textContent = "Copy summary";
                }, 1500);
            }
            navigator.clipboard && navigator.clipboard.writeText
              ? navigator.clipboard.writeText(f).then(h, function () {
                  prompt("Copy this:", f);
                })
              : prompt("Copy this:", f);
          })(t, n, e.at, this);
        }),
        (y.getElementById("again").onclick = function () {
          ge(!0);
        });
    })();
  }
})();
