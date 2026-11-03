"""Fard Checker — single place for the version number and the change list.
FARD CHECKER VERSION 1.0
Every file of the app carries the same "FARD CHECKER VERSION x.y" line; the Render page checks they all match."""
VERSION = "1.0"
DATE = "1 Nov 2026"

# newest first: (version, date, what changed)
CHANGES = [
    ("1.0", "1 Nov 2026",
     "Version numbers introduced. Includes: scanning in sets of 10 with Resume, scan speed and diagnostics, "
     "Status PDF, Patwari's sketch laid over the khasra map at 70% (report + KMZ), tatima beside the map, "
     "UTM maps, khasra family, geotag/Plus Code checks, optional Gemini reading, background analysis."),
]
