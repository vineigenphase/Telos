"""Compare stored Edexcel boundaries against Pearson's official notional
component boundaries. Reports only; changes nothing."""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
from pypdf import PdfReader

SP = DOCS
sys.path.insert(0, REPO)

# Pearson prints the numbers, then the paper label on the NEXT line.
DATA = re.compile(r"^(9FM0|9MA0)\s+A Level .*?Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s*$")
LABEL = re.compile(r"^(Paper\s+\d[A-D]?)\s*$")

# Edexcel paper -> this app's paper_code.
MAP = {("9FM0", "Paper 1"): "CP1", ("9FM0", "Paper 2"): "CP2",
       ("9FM0", "Paper 3C"): "FM1", ("9FM0", "Paper 3B"): "FS1",
       ("9MA0", "Paper 1"): "Pure 1", ("9MA0", "Paper 2"): "Pure 2",
       ("9MA0", "Paper 3"): "Stats&Mech"}
SUBJ = {"9FM0": "Further Maths", "9MA0": "Maths"}

official = {}
for year in ("2022", "2023", "2024", "2025"):
    path = os.path.join(SP, f"pearson{year}.pdf")
    if not os.path.exists(path):
        continue
    lines = []
    for pg in PdfReader(path).pages:
        lines += (pg.extract_text() or "").splitlines()
    for i, l in enumerate(lines):
        m = DATA.match(l.strip())
        if not m:
            continue
        lab = LABEL.match(lines[i + 1].strip()) if i + 1 < len(lines) else None
        if not lab:
            continue
        qual, mx, a_s, a, b, c, d, e = m.groups()
        key = (qual, lab.group(1).replace("  ", " "))
        if key in MAP:
            official[(SUBJ[qual], MAP[key], year)] = (int(mx), int(a_s), int(a), int(b), int(c))

os.environ.pop("CANONICAL_HOST", None)
import app as A
with A.get_db() as db:
    stored = {(r["subject"], r["paper_code"], r["year"]):
              (r["a_star"], r["a_boundary"], r["b_boundary"], r["c_boundary"])
              for r in db.execute("SELECT * FROM grade_boundaries WHERE board='Edexcel'").fetchall()}

print(f"{'SUBJECT':<15}{'PAPER':<12}{'YEAR':<6}{'STORED':<22}{'OFFICIAL':<22}RESULT")
mismatch = missing = agree = 0
for key in sorted(official):
    subj, paper, year = key
    mx, *off = official[key]
    st = stored.get(key)
    if st is None:
        print(f"{subj:<15}{paper:<12}{year:<6}{'(not stored)':<22}{str(tuple(off)):<22}MISSING")
        missing += 1
    elif tuple(st) == tuple(off):
        agree += 1
    else:
        print(f"{subj:<15}{paper:<12}{year:<6}{str(tuple(st)):<22}{str(tuple(off)):<22}MISMATCH")
        mismatch += 1
print(f"\nchecked {len(official)} official rows: {agree} agree, {mismatch} mismatch, {missing} missing")
