"""Verify every Edexcel Further Maths and Maths paper against Pearson's own
notional component boundaries. Reports only."""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
from pypdf import PdfReader

SP = DOCS
sys.path.insert(0, REPO)

# 9FM0 option papers: 3A/3B/3C/3D are the first option, 4A-4D the second.
MAP = {("9FM0", "1"): "CP1",  ("9FM0", "01"): "CP1",
       ("9FM0", "2"): "CP2",  ("9FM0", "02"): "CP2",
       ("9FM0", "3A"): "FP1", ("9FM0", "3B"): "FS1",
       ("9FM0", "3C"): "FM1", ("9FM0", "3D"): "D1",
       ("9FM0", "4A"): "FP2", ("9FM0", "4B"): "FS2",
       ("9FM0", "4C"): "FM2", ("9FM0", "4D"): "D2",
       ("9MA0", "1"): "Pure 1", ("9MA0", "01"): "Pure 1",
       ("9MA0", "2"): "Pure 2", ("9MA0", "02"): "Pure 2",
       ("9MA0", "3"): "Stats&Mech", ("9MA0", "03"): "Stats&Mech"}
SUBJ = {"9FM0": "Further Maths", "9MA0": "Maths"}

# Later years print A* A B C D E U; 2019 prints A B C D E U for these subjects.
SEVEN = re.compile(r"^(?:(9FM0|9MA0)\s+)?A Level (?:Further Mathematics|Mathematics)\s+Raw"
                   r"\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+0\s*$")
SIX = re.compile(r"^(?:(9FM0|9MA0)\s+)?A Level (?:Further Mathematics|Mathematics)\s+Raw"
                 r"\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+0\s*$")
LABEL = re.compile(r"^Paper\s+(\d{1,2}[A-D]?)\s*$")

official = {}
for year in ("2019", "2022", "2023", "2024", "2025"):
    path = os.path.join(SP, f"pearson{year}.pdf")
    if not os.path.exists(path):
        print(f"  (no PDF for {year})"); continue
    lines = []
    for pg in PdfReader(path).pages:
        lines += (pg.extract_text() or "").splitlines()
    for i, l in enumerate(lines):
        s = l.strip()
        qual = None
        if "Further Mathematics" in s:
            qual = "9FM0"
        elif "A Level Mathematics" in s:
            qual = "9MA0"
        if not qual or i + 1 >= len(lines):
            continue
        lab = LABEL.match(lines[i + 1].strip())
        if not lab:
            continue
        code = lab.group(1).lstrip("0") or "0"
        m7, m6 = SEVEN.match(s), SIX.match(s)
        if m7:
            g = m7.groups()[1:]
            a_star, a, b, c = int(g[1]), int(g[2]), int(g[3]), int(g[4])
        elif m6:
            g = m6.groups()[1:]
            a_star, a, b, c = None, int(g[1]), int(g[2]), int(g[3])
        else:
            continue
        key = MAP.get((qual, lab.group(1))) or MAP.get((qual, code))
        if key:
            official[(SUBJ[qual], key, year)] = (a_star, a, b, c)

os.environ.pop("CANONICAL_HOST", None)
import app as A
with A.get_db() as db:
    stored = {(r["subject"], r["paper_code"], r["year"]):
              (r["a_star"], r["a_boundary"], r["b_boundary"], r["c_boundary"])
              for r in db.execute("SELECT * FROM grade_boundaries WHERE board='Edexcel'").fetchall()}

agree = mismatch = nostar = 0
print(f"{'SUBJECT':<15}{'PAPER':<12}{'YEAR':<6}{'STORED':<22}{'OFFICIAL':<22}")
for key in sorted(official):
    off = official[key]
    st = stored.get(key)
    if st is None:
        continue
    if off[0] is None:            # 2019: no A* published at component level
        if tuple(st[1:]) == tuple(off[1:]):
            nostar += 1
        else:
            print(f"{key[0]:<15}{key[1]:<12}{key[2]:<6}{str(st):<22}{str(off):<22}  A/B/C MISMATCH")
            mismatch += 1
        continue
    if tuple(st) == tuple(off):
        agree += 1
    else:
        print(f"{key[0]:<15}{key[1]:<12}{key[2]:<6}{str(st):<22}{str(off):<22}  MISMATCH")
        mismatch += 1

print(f"\nfull matches: {agree}   A/B/C-only matches (2019, no A* published): {nostar}   mismatches: {mismatch}")
