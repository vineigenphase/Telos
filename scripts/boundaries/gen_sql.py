"""Generate migration 007 straight from the parsed OCR PDFs.

Written by machine on purpose: eighteen rows of six numbers retyped by hand is
exactly how the existing Physics data came to be shifted a column in the first
place.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pypdf import PdfReader

SP = DOCS
YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]
EXPECTED_MAX = {"01": 100, "02": 100, "03": 70}
# OCR component -> the paper code this app uses. Max marks agree on all three,
# which is what makes the mapping unambiguous.
CODE = {"01": "Paper 1", "02": "Paper 2", "03": "Paper 3"}

ONE_LINE = re.compile(
    r"^H556\s+(0\d)\s+(.+?)\s+Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s*$")
RAW = re.compile(r"^Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
COMP = re.compile(r"^(0\d)\s+(\D.*)$")

def block(lines):
    i = next(n for n, l in enumerate(lines) if l.strip() == "A Level Physics A")
    out = []
    for l in lines[i + 1:]:
        s = l.strip()
        if s.startswith(("A Level ", "AS Level ", "AS GCE ")):
            break
        out.append(s)
    return out

rows = []
for year in YEARS:
    lines = []
    for pg in PdfReader(os.path.join(SP, f"ocr{year}.pdf")).pages:
        lines += (pg.extract_text() or "").splitlines()
    found = {}
    for l in (x.strip() for x in lines):
        m = ONE_LINE.match(l)
        if m:
            code, _n, mx, a_s, a, b, c, d, e = m.groups()
            found[code] = (int(mx), int(a_s), int(a), int(b), int(c))
    if not found:
        blk = block(lines)
        comps = [COMP.match(l).group(1) for l in blk if COMP.match(l)]
        raws = [RAW.match(l).groups() for l in blk if RAW.match(l)]
        for code, r in zip(comps, raws):
            found[code] = (int(r[0]), int(r[1]), int(r[2]), int(r[3]), int(r[4]))
    for code in ("01", "02", "03"):
        mx, a_s, a, b, c = found[code]
        assert mx == EXPECTED_MAX[code], f"{year} {code} max {mx}"
        assert a_s > a > b > c > 0, f"{year} {code} not descending"
        rows.append((CODE[code], year, a_s, a, b, c))

sql = ['''-- 007_physics_boundaries.sql
-- Replace the OCR A Physics grade boundaries with the official per-paper ones.
--
-- Two faults, both fatal to a Physics prediction.
--
-- 1. Granularity. The rows held the OVERALL qualification boundary (out of 270,
--    all three papers summed) under the paper_code "Overall". Students log one
--    paper at a time, out of 100 or 70. prediction.select_boundaries falls back
--    to "same subject, same year" when it cannot match a paper code, so a
--    60/100 Paper 1 was being compared against a 270-mark scale and graded U.
--
-- 2. A column shift. Every stored row was the official Overall row moved one
--    place right: the max mark (270) sat in a_star, A* sat in a, A in b, B in
--    c, and C was dropped. That is why a_star read 270 in every single year.
--    Confirmed against OCR's published PDFs for all six series.
--
-- The replacement is per-paper, from OCR's own documents:
--   Paper 1 = H556/01 Modelling physics (100)
--   Paper 2 = H556/02 Exploring physics (100)
--   Paper 3 = H556/03 Unified physics    (70)
-- The app's max marks for these three papers already agree with OCR's, which
-- is what makes the mapping unambiguous.
--
-- 2020 and 2021 are absent deliberately: there was no summer exam series in
-- either year, so no official boundaries exist. The rows previously stored for
-- them were not real. A student logging a 2020 paper now falls back to the
-- median of the real years, which is the honest answer.
--
-- "Physics B"/"OCR" is deleted outright. It is not in paper_templates.py, so
-- no user can select it, and its rows carried the same column shift.
--
-- Idempotent: deletes the subject's rows, then reinserts the official set.

DELETE FROM grade_boundaries WHERE subject = 'Physics B' AND board = 'OCR';
DELETE FROM grade_boundaries WHERE subject = 'Physics' AND board = 'OCR A';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series, a_star, a_boundary, b_boundary, c_boundary)
VALUES''']

vals = [f"    ('Physics', 'OCR A', '{p}', '{y}', 'June', {a_s}, {a}, {b}, {c})"
        for (p, y, a_s, a, b, c) in rows]
sql.append(",\n".join(vals) + ";\n")

out = os.path.join(MIGRATIONS, "007_physics_boundaries.sql")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(sql))
print(f"wrote {out} with {len(rows)} rows")
for r in rows:
    print("   ", r)
