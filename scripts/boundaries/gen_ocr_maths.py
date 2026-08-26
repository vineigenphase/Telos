"""Migration 014 and the seed rows for OCR A Level Mathematics A (H240).

Generated from OCR's published boundary PDFs, not transcribed. Component 01 is
Paper 1, 02 is Paper 2, 03 is Paper 3, and all three are out of 100 — which the
extractor has already checked against the PDFs, so the mapping is unambiguous.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from ocr_extract import extract

CODE = {"01": "Paper 1", "02": "Paper 2", "03": "Paper 3"}

data, probs = extract("H240", "A Level Mathematics A", {"01": 100, "02": 100, "03": 100})
if probs:
    print("REFUSING — parse problems:")
    for p in probs:
        print("  -", p)
    raise SystemExit(1)

rows = []
for (code, year) in sorted(data, key=lambda k: (k[1], k[0])):
    mx, a_s, a, b, c, d, e = data[(code, year)]
    assert a_s > a > b > c > d > e > 0, f"{code} {year} not descending"
    rows.append((CODE[code], year, a_s, a, b, c, d, e))

values = ",\n".join(
    f"    ('Maths', 'OCR A', '{p}', '{y}', 'June', {a_s}, {a}, {b}, {c}, {d}, {e})"
    for (p, y, a_s, a, b, c, d, e) in rows)

sql = f'''-- 014_ocr_maths_boundaries.sql
-- OCR A Level Mathematics A (H240), per paper, from OCR's published PDFs.
--
--   Paper 1 = H240/01 Pure Mathematics                 (100)
--   Paper 2 = H240/02 Pure Mathematics and Statistics  (100)
--   Paper 3 = H240/03 Pure Mathematics and Mechanics   (100)
--
-- Component boundaries, not the overall 300-mark qualification figure —
-- students log one paper at a time, and storing the qualification total under a
-- paper code is what made Physics predict U for every student who tried it.
--
-- D and E are included because OCR publishes them; the columns exist from
-- migration 009.
--
-- No 2020 or 2021: no summer exam series in either year.
--
-- Idempotent: clears the subject's rows, then reinserts.

DELETE FROM grade_boundaries WHERE subject = 'Maths' AND board = 'OCR A';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
{values};
'''
out = os.path.join(MIGRATIONS, "014_ocr_maths_boundaries.sql")
open(out, "w", encoding="utf-8", newline="\n").write(sql)
print(f"wrote migration with {len(rows)} rows")

seed = "\n".join(
    f'    ("Maths", "OCR A", "{p}", "{y}", "June", {a_s}, {a}, {b}, {c}),'
    for (p, y, a_s, a, b, c, d, e) in rows)
open(os.path.join(DOCS, "ocr_maths_seed.txt"),
     "w", encoding="utf-8").write(seed)
print("seed rows written to scratchpad")
