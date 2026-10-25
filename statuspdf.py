"""Application pendency status PDF (status only — no remarks, documents, analysis or phone numbers).
Input comes from the tracker's last scan, already computed with the 5/7/9 working-day rules."""
import io
import re
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta, timezone
IST = timezone(timedelta(hours=5, minutes=30), 'IST')

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, LongTable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

NAVY = colors.HexColor("#12355b")
INK = colors.HexColor("#1d2330")
MUTED = colors.HexColor("#5b6475")
LINE = colors.HexColor("#dfe4ec")
HEAD = colors.HexColor("#eef2f7")
RED = colors.HexColor("#b42318")
RED_BG = colors.HexColor("#fde8e8")
AMBER = colors.HexColor("#8a5300")
AMBER_BG = colors.HexColor("#fff3dc")
GREEN = colors.HexColor("#145c36")
GREEN_BG = colors.HexColor("#e2f5ea")
LEVEL_BG = {"Patwari": colors.HexColor("#fff7da"), "Girdawar": colors.HexColor("#ddf3ef"),
            "Naib Tehsildar": colors.HexColor("#ece5fb"), "Tehsildar": colors.HexColor("#eceef2")}
LEVELS = ["Patwari", "Girdawar", "Naib Tehsildar", "Tehsildar", "Applicant"]

S = {
    "title": ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=NAVY),
    "sub": ParagraphStyle("s", fontName="Helvetica", fontSize=8.8, leading=11.5, textColor=MUTED),
    "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=NAVY, spaceBefore=8, spaceAfter=4),
    "cell": ParagraphStyle("c", fontName="Helvetica", fontSize=7.6, leading=9.2, textColor=INK),
    "cellb": ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=7.6, leading=9.2, textColor=INK),
    "hcell": ParagraphStyle("hc", fontName="Helvetica-Bold", fontSize=7.4, leading=9, textColor=colors.HexColor("#3b4456")),
    "kpin": ParagraphStyle("kn", fontName="Helvetica-Bold", fontSize=17, leading=19, alignment=TA_CENTER, textColor=INK),
    "kpil": ParagraphStyle("kl", fontName="Helvetica", fontSize=7.4, leading=9, alignment=TA_CENTER, textColor=MUTED),
    "note": ParagraphStyle("n", fontName="Helvetica", fontSize=7.4, leading=9.4, textColor=MUTED),
}


def esc(s):
    return (str("" if s is None else s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def P(t, st="cell"):
    return Paragraph(t if isinstance(t, str) else esc(t), S[st])


def level_of(it):
    st = it.get("stage") or ""
    if re.search(r"returned to applicant", st, re.I):
        return "Applicant"
    for lv in ("Naib Tehsildar", "Tehsildar", "Girdawar", "Patwari"):
        if lv.lower() in st.lower():
            return lv
    cur = (it.get("cur") or {}).get("role") or ""
    return cur if cur in LEVELS else "Other"


def status_of(it):
    c = it.get("cur") or {}
    if level_of(it) == "Applicant":
        return ("Returned to applicant", None, MUTED)
    if c.get("over"):
        return (f"Overdue by {c['over']} day{'s' if c['over'] != 1 else ''}", "over", RED)
    if c.get("left") == 0 and c.get("status") == "running":
        return ("Due today", "ok", AMBER)
    if c.get("left") is not None and c.get("status") == "running":
        return (f"Within time · {c['left']} day{'s' if c['left'] != 1 else ''} left", "ok", GREEN)
    if c.get("status") in ("running", "waiting"):
        return ("Within time", "ok", GREEN)
    return ("—", None, MUTED)


def table(data, widths, header_rows=1, zebra=True, extra=None, long=False):
    T = (LongTable if long else Table)(data, colWidths=widths, repeatRows=header_rows)
    st = [("FONT", (0, 0), (-1, -1), "Helvetica", 7.6),
          ("BACKGROUND", (0, 0), (-1, header_rows - 1), HEAD),
          ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if extra:
        st += extra
    T.setStyle(TableStyle(st))
    return T


def build(payload):
    items = payload.get("items") or []
    lim = payload.get("limits") or {}
    lp, lg, ln = lim.get("pat", 5), lim.get("gir", 7), lim.get("nt", 9)
    office = payload.get("office") or "Tehsil"
    try:
        scan_at = datetime.fromtimestamp((payload.get("scanAt") or 0) / 1000, IST)
    except Exception:
        scan_at = datetime.now(IST)
    pending = [i for i in items if level_of(i) != "Applicant"]
    returned = [i for i in items if level_of(i) == "Applicant"]
    over = [i for i in pending if status_of(i)[1] == "over"]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=11 * mm, rightMargin=11 * mm, topMargin=10 * mm, bottomMargin=12 * mm,
                            title=f"Application Pendency Status — {office}", author=office)
    W = landscape(A4)[0] - 22 * mm

    def footer(cv, d):
        cv.saveState()
        cv.setFont("Helvetica", 7)
        cv.setFillColor(MUTED)
        cv.drawString(11 * mm, 6 * mm, f"Application pendency status · {office} · as on {scan_at:%d %b %Y, %I:%M %p}")
        cv.drawRightString(landscape(A4)[0] - 11 * mm, 6 * mm, f"Page {d.page}")
        cv.restoreState()

    story = []
    services = sorted({i.get("service") for i in items if i.get("service")})
    story.append(P("Revenue Plus — Application Pendency Status", "title"))
    story.append(P(f"{esc(office)} · Services: {esc(', '.join(services) or '—')} · Position as on <b>{scan_at:%d %b %Y, %I:%M %p}</b>", "sub"))
    story.append(P(f"Time limits: <b>Patwari {lp}</b>, <b>Girdawar {lg}</b>, <b>Naib Tehsildar {ln}</b> working days, counted from the application date "
                   f"(or resubmission date). Sundays and holidays are excluded.", "sub"))
    story.append(Spacer(1, 6))

    # KPI tiles
    by_level = OrderedDict((lv, [i for i in items if level_of(i) == lv]) for lv in LEVELS)
    tiles = [("Pending", len(pending), INK), ("Overdue", len(over), RED if over else GREEN)] + \
            [(f"With {lv}" if lv != "Applicant" else "Returned to applicant", len(by_level[lv]), INK) for lv in LEVELS]
    cells = [[Paragraph(f'<font color="{c.hexval()}">{n}</font>', S["kpin"]) for _, n, c in tiles],
             [P(esc(t), "kpil") for t, _, _ in tiles]]
    kt = Table(cells, colWidths=[W / len(tiles)] * len(tiles))
    kt.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                            ("BACKGROUND", (0, 0), (-1, -1), colors.white), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                            ("BACKGROUND", (1, 0), (1, -1), RED_BG if over else GREEN_BG)]))
    story.append(kt)

    # Level-wise and officer-wise side by side
    lv_rows = [[P("Pending with", "hcell"), P("Applications", "hcell"), P("Within time", "hcell"), P("Overdue", "hcell"), P("Max. overdue (days)", "hcell")]]
    lv_style = []
    for lv in ["Patwari", "Girdawar", "Naib Tehsildar", "Tehsildar"]:
        its = by_level[lv]
        ov = [status_of(i) for i in its]
        mx = max([(i.get("cur") or {}).get("over") or 0 for i in its] or [0])
        n_over = sum(1 for s in ov if s[1] == "over")
        lv_rows.append([P(f"<b>{lv}</b>"), P(len(its)), P(sum(1 for s in ov if s[1] == "ok")), P(f'<font color="{RED.hexval()}"><b>{n_over}</b></font>' if n_over else "0"), P(mx or "—")])
        lv_style.append(("BACKGROUND", (0, len(lv_rows) - 1), (0, len(lv_rows) - 1), LEVEL_BG[lv]))
    lv_rows.append([P("<b>Total</b>"), P(f"<b>{len(pending)}</b>"), P(f"<b>{len(pending) - len(over)}</b>"),
                    P(f'<font color="{RED.hexval()}"><b>{len(over)}</b></font>'), P("")])

    hold = defaultdict(lambda: {"n": 0, "ok": 0, "over": 0, "max": 0, "lv": ""})
    for i in pending:
        h = i.get("holder") or level_of(i)
        r = hold[h]
        r["n"] += 1
        r["lv"] = level_of(i)
        s = status_of(i)
        if s[1] == "over":
            r["over"] += 1
            r["max"] = max(r["max"], (i.get("cur") or {}).get("over") or 0)
        elif s[1] == "ok":
            r["ok"] += 1
    of_rows = [[P("Officer / holder", "hcell"), P("Files", "hcell"), P("Within time", "hcell"), P("Overdue", "hcell"), P("Max. overdue (days)", "hcell")]]
    of_style = []
    for h, r in sorted(hold.items(), key=lambda kv: (-kv[1]["over"], -kv[1]["max"], -kv[1]["n"])):
        of_rows.append([P(f"<b>{esc(h)}</b>"), P(r["n"]), P(r["ok"]), P(f'<font color="{RED.hexval()}"><b>{r["over"]}</b></font>' if r["over"] else "0"), P(r["max"] or "—")])
        if r["lv"] in LEVEL_BG:
            of_style.append(("BACKGROUND", (0, len(of_rows) - 1), (0, len(of_rows) - 1), LEVEL_BG[r["lv"]]))
    half = (W - 8 * mm) / 2
    cw = [half * 0.36, half * 0.15, half * 0.16, half * 0.14, half * 0.19]
    left = [P("Level-wise", "h"), table(lv_rows, cw, extra=lv_style + [("LINEABOVE", (0, -1), (-1, -1), 0.8, NAVY)])]
    right = [P("Officer-wise", "h"), table(of_rows, cw, extra=of_style)]
    two = Table([[left, "", right]], colWidths=[half, 8 * mm, half])
    two.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(two)

    # Village-wise
    vil = defaultdict(lambda: defaultdict(int))
    for i in items:
        v = i.get("village") or "—"
        vil[v][level_of(i)] += 1
        if status_of(i)[1] == "over":
            vil[v]["over"] += 1
    if vil:
        vr = [[P(x, "hcell") for x in ("Village", "Patwari", "Girdawar", "Naib Tehsildar", "Tehsildar", "Pending", "Overdue", "Returned")]]
        for v, r in sorted(vil.items(), key=lambda kv: (-kv[1]["over"], -sum(kv[1][l] for l in LEVELS[:4]), kv[0])):
            tot = sum(r[l] for l in LEVELS[:4])
            vr.append([P(f"<b>{esc(v)}</b>")] + [P(r[l] or "·") for l in LEVELS[:4]] + [P(f"<b>{tot}</b>"),
                      P(f'<font color="{RED.hexval()}"><b>{r["over"]}</b></font>' if r["over"] else "0"), P(r["Applicant"] or "·")])
        vr.append([P("<b>Total</b>")] + [P(f"<b>{len(by_level[l])}</b>") for l in LEVELS[:4]] + [P(f"<b>{len(pending)}</b>"),
                  P(f'<font color="{RED.hexval()}"><b>{len(over)}</b></font>'), P(f"<b>{len(returned)}</b>")])
        cwv = [W * 0.28] + [W * 0.1] * 7
        story.append(KeepTogether([P("Village-wise", "h"), table(vr, cwv, extra=[("LINEABOVE", (0, -1), (-1, -1), 0.8, NAVY)] +
                                                                   [("BACKGROUND", (1 + k, 0), (1 + k, 0), LEVEL_BG[l]) for k, l in enumerate(LEVELS[:4])])]))

    # Application list
    story.append(P("Applications (most overdue first)", "h"))
    hdr = ["#", "Application no.", "Applicant", "Village", "Khasra", "Service / purpose", "Applied", "Pending with",
           "Working days", "Limit", "Status", "Earlier delays"]
    rows = [[P(h, "hcell") for h in hdr]]
    sty = []

    def sort_key(i):
        c = i.get("cur") or {}
        return (0 if status_of(i)[1] == "over" else (1 if level_of(i) != "Applicant" else 2), -(c.get("over") or 0),
                -(i.get("dayNow") or 0), i.get("village") or "")

    for n, i in enumerate(sorted(items, key=sort_key), 1):
        c = i.get("cur") or {}
        txt, kind, col = status_of(i)
        lv = level_of(i)
        late = ", ".join(f"{esc(x.get('who'))} +{x.get('over')}d" for x in (i.get("late") or []) if x.get("over"))
        applied = esc(i.get("appDate") or "")
        if i.get("resub"):
            applied += f"<br/><font color='{MUTED.hexval()}'>resub. {esc(i['resub'])}</font>"
        rows.append([P(n), P(esc(i.get("appNo"))), P(esc(i.get("name"))), P(esc(i.get("village"))), P(esc(i.get("khasra"))),
                     P(esc(" / ".join(x for x in (i.get("service"), i.get("purpose")) if x))), P(applied),
                     P(f"<b>{esc(lv if lv != 'Applicant' else 'Returned to applicant')}</b>" + (f"<br/><font color='{MUTED.hexval()}'>{esc(i.get('holder'))}</font>" if i.get("holder") and lv != "Applicant" else "")),
                     P(i.get("dayNow") if i.get("dayNow") is not None else "—"), P(c.get("limit") or "—"),
                     P(f'<font color="{col.hexval()}"><b>{esc(txt)}</b></font>'), P(late or "—")])
        r_ = len(rows) - 1
        if kind == "over":
            sty.append(("BACKGROUND", (10, r_), (10, r_), RED_BG))
        elif kind == "ok":
            sty.append(("BACKGROUND", (10, r_), (10, r_), GREEN_BG))
        if lv in LEVEL_BG:
            sty.append(("BACKGROUND", (7, r_), (7, r_), LEVEL_BG[lv]))
    fr = [0.03, 0.125, 0.12, 0.085, 0.055, 0.095, 0.075, 0.115, 0.055, 0.04, 0.11, 0.095]
    story.append(table(rows, [W * f for f in fr], extra=sty, long=True))
    story.append(Spacer(1, 5))
    story.append(P("Working days = days since the application (or resubmission) date, excluding Sundays and holidays. "
                   "Status compares these with the limit of the level the file is pending at; “Earlier delays” lists levels that acted after their limit. "
                   "Prepared from the Revenue Plus portal; status only.", "note"))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
