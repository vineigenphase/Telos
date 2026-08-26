"""Migration 015 and seed rows for OCR A Level Further Mathematics A (H245)."""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from ocr_fm import extract

data, probs = extract()
if probs:
    print("REFUSING — parse problems:")
    for p in probs:
        print("  -", p)
    raise SystemExit(1)

rows = []
for (code, year) in sorted(data, key=lambda k: (k[1], k[0])):
    mx, a_s, a, b, c, d, e = data[(code, year)]
    assert a_s > a > b > c > d > e > 0, f"{code} {year} not descending"
    rows.append((code, year, a_s, a, b, c, d, e))

values = ",\n".join(
    f"    ('Further Maths', 'OCR A', '{p}', '{y}', 'June', {a_s}, {a}, {b}, {c}, {d}, {e})"
    for (p, y, a_s, a, b, c, d, e) in rows)

sql = f'''-- 015_ocr_further_maths_boundaries.sql
-- OCR A Level Further Mathematics A (H245), per component.
--
--   Y540 Pure Core 1            (75)   mandatory
--   Y541 Pure Core 2            (75)   mandatory
--   Y542 Statistics             (75)   optional
--   Y543 Mechanics              (75)   optional
--   Y544 Discrete Mathematics   (75)   optional
--   Y545 Additional Pure Maths  (75)   optional
--
-- A student takes both Pure Core papers and two of the four options, so all six
-- are stored and the catalogue offers all six.
--
-- Component boundaries only. OCR also publishes an overall figure for each of
-- the six possible option pairings (Y540+Y541+Y542+Y543 and so on); those are
-- qualification totals out of 300 and are deliberately not stored, because a
-- student logs one 75-mark paper at a time. Storing a 300-mark total under a
-- paper code is exactly what made Physics predict U.
--
-- No 2018: reformed Further Maths was first taught in 2017 and first assessed
-- in 2019, so the series does not exist. No 2020 or 2021 either — cancelled.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Further Maths' AND board = 'OCR A';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
{values};
'''
open(os.path.join(MIGRATIONS, "015_ocr_further_maths_boundaries.sql"),
     "w", encoding="utf-8", newline="\n").write(sql)

seed = "\n".join(
    f'    ("Further Maths", "OCR A", "{p}", "{y}", "June", {a_s}, {a}, {b}, {c}),'
    for (p, y, a_s, a, b, c, d, e) in rows)
open(os.path.join(DOCS, "ocr_fm_seed.txt"),
     "w", encoding="utf-8").write(seed)
print(f"wrote migration with {len(rows)} rows across {len({r[1] for r in rows})} series")
