"""Fard Checker — single place for the version number and the change list.
FARD CHECKER VERSION 1.9.7
Every file of the app carries the same "FARD CHECKER VERSION x.y" line; the Render page checks they all match."""
VERSION = "1.9.7"
DATE = "6 Nov 2026"

# newest first: (version, date, what changed)
CHANGES = [
    ("1.9.7", "6 Nov 2026",
     "Scan sync: the last scan of each login, analysis gists, choices, pre-scrutiny points and photo prints are kept in a private GitHub data repo (DATA_REPO + GITHUB_TOKEN on Render) and can be opened from any browser with the access key. Phone / Aadhaar numbers removed before saving. New file sync.py."),
    ("1.9.6", "6 Nov 2026",
     "Section 2 lists every khewat/khata holding the survey no. (ownership and cultivation in brief) with a select button; Title and share works on the selected one. Two separate boxes with their own scales: Ownership (khewat) — share, total alienated by the person in all khatas of the khewat (read from the khata column), remaining share; Cultivation (khata) — strictly the khata's cultivator cell (heirs not named → cultivation stands with the deceased). Person chosen from the khewat or khata list; choices remembered."),
    ("1.9.5", "5 Nov 2026",
     "Title and share on two bases, as area in the khata of the application: ownership column (share in khewat ÷ khewat total × khata area; heirs by fraction of the deceased's unaccounted remainder) and cultivation column (fraction in the khata's cultivator cell × khata area, inherited through the person named in it). Mutations received / alienated give the balance on each basis; eligibility green on both, amber on one, red on neither."),
    ("1.9.4", "5 Nov 2026",
     "Screen kept awake (like a video) while the tracker is scanning or analysing; released when work stops."),
    ("1.9.3", "5 Nov 2026",
     "Gemini again uses its full reasoning (the brief-thinking setting of 1.9.2 is removed). All other speed changes kept — they change only the order of work, not what is read or checked."),
    ("1.9.2", "5 Nov 2026",
     "Speed: documents of the next application are fetched while the current one is analysed; each application page is opened once for all its documents; GPS-stamp OCR and the satellite view run alongside the AI reader; Gemini asked to think briefly; Render woken when the tracker opens; timing shown in the background panel."),
    ("1.9.1", "5 Nov 2026",
     "Analysis summary after a scan (Case 1 and Case 2 tables, closed until opened; a row opens that application). Report sections fold into one line each and open on a tap. Geotag up to 20 m outside the khasra is only mentioned. Three explanatory photo lines removed. A serious finding in any section keeps the overall at doubtful at best."),
    ("1.9", "5 Nov 2026",
     "New analysis: Case 1 pre-scrutiny (photo, survey record, title with owner drop-down, documents with Aadhaar) and Case 2 after the Patwari's report (boxes inside each section, tatima, report contradictions). Satisfaction scales, overall verdict, pre-scrutiny points marked resolved/open. Every application analysed in the background. Movement line removed."),
    ("1.8", "4 Nov 2026",
     "After an update, analyses saved by the older version are discarded and every case is analysed afresh (background and on request). Within the same version, saved analyses are still reused until the file moves or documents change."),
    ("1.7", "4 Nov 2026",
     "Tatima page chosen by content: the sketch page (no table column lines, red shading) instead of simply the last page, so Jamabandi/girdawari pages scanned with the tatima are skipped. Non-rectangular sketches are located by the outline round the red shading."),
    ("1.6", "4 Nov 2026",
     "Saved record named by survey no. + village, with two PDFs (applicant documents, Patwari documents) plus the KMZ. If the survey no. is not on the map, the nearest available survey no. and its neighbours are shown, clearly marked as locality only."),
    ("1.5", "4 Nov 2026",
     "Sketch is laid over the map only when it is the Patwari's tatima with a real outline of the khasra. The applicant's rough sketch or a location/route sketch is shown beside the map (and in the KMZ) but never stretched over the khasra; the report says why."),
    ("1.4", "3 Nov 2026",
     "Save record to folder (Chrome/Edge): one sub-folder per application with all uploaded documents, the Patwari's tatima, the KMZ with the tatima laid over the khasra, and Details.txt."),
    ("1.3", "3 Nov 2026",
     "Tracker reads a new application still at the Tehsildar desk (no movement yet, Members Remarks empty): shown as With Tehsildar — not yet forwarded, instead of Could not read."),
    ("1.2", "3 Nov 2026",
     "Main survey number is the denominator: 1513/141 is located on the map as 141, and the total area of 141 adds 141, 141 min and every …/141 number. Old khasra numbers are no longer used."),
    ("1.1", "3 Nov 2026",
     "Tracker now reads the application page under the Tehsildar login (movement table headed 'Action By', officers shown by full title, 'Name of Applicant/Vendor'); Naib Tehsildar no longer mistaken for Tehsildar; 'Required' validator text removed from values."),
    ("1.0", "1 Nov 2026",
     "Version numbers introduced. Includes: scanning in sets of 10 with Resume, scan speed and diagnostics, "
     "Status PDF, Patwari's sketch laid over the khasra map at 70% (report + KMZ), tatima beside the map, "
     "UTM maps, khasra family, geotag/Plus Code checks, optional Gemini reading, background analysis."),
]
