"""Fard Checker — single place for the version number and the change list.
FARD CHECKER VERSION 1.9
Every file of the app carries the same "FARD CHECKER VERSION x.y" line; the Render page checks they all match."""
VERSION = "1.9"
DATE = "5 Nov 2026"

# newest first: (version, date, what changed)
CHANGES = [
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
