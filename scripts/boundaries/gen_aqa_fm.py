"""Migration 018 and seed rows for AQA A-level Further Mathematics (7367)."""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from aqa_extract import extract

YEARS = ["2019", "2022", "2023", "2024", "2025"]
EXPECT = {"1": 100, "2": 100, "3D": 50, "3M": 50, "3S": 50}
CODE = {"1": "Paper 1", "2": "Paper 2", "3D": "Paper 3D",
        "3M": "Paper 3M", "3S": "Paper 3S"}

data, probs = extract("7367", EXPECT, YEARS)
if probs:
    print("REFUSING — parse problems:")
    for p in probs:
        print("  -", p)
    raise SystemExit(1)

rows = []
for (comp, year) in sorted(data, key=lambda k: (k[1], k[0])):
    mx, a_s, a, b, c, d, e = data[(comp, year)]
    assert a_s > a > b > c > d > e > 0, f"{comp} {year} not descending"
    rows.append((CODE[comp], year, a_s, a, b, c, d, e))

values = ",\n".join(
    f"    ('Further Maths', 'AQA', '{p}', '{y}', 'June', {a_s}, {a}, {b}, {c}, {d}, {e})"
    for (p, y, a_s, a, b, c, d, e) in rows)

sql = f'''-- 018_aqa_further_maths_boundaries.sql
-- AQA A-level Further Mathematics (7367), per paper.
--
--   Paper 1  (100)  compulsory
--   Paper 2  (100)  compulsory
--   Paper 3D (50)   Discrete    | choose two
--   Paper 3M (50)   Mechanics   | of these
--   Paper 3S (50)   Statistics  | three
--
-- 100 + 100 + 50 + 50 = 300. The three optional papers are confirmed by AQA's
-- own subject rows, which are published per option pairing: 7367DS, 7367MD and
-- 7367SM. Those pairing rows are qualification totals out of 300 and are not
-- stored — a student logs one paper at a time.
--
-- Notional component boundaries, as with AQA Maths: awarded at qualification
-- level and derived per paper. The optional papers being out of 50 rather than
-- 100 is the detail worth guarding, and the extractor checks each component
-- against its own max mark rather than assuming they match.
--
-- No 2018: reformed Further Maths was first assessed in 2019.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Further Maths' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
{values};
'''
open(os.path.join(MIGRATIONS, "018_aqa_further_maths_boundaries.sql"),
     "w", encoding="utf-8", newline="\n").write(sql)

seed = "\n".join(
    f'    ("Further Maths", "AQA", "{p}", "{y}", "June", {a_s}, {a}, {b}, {c}),'
    for (p, y, a_s, a, b, c, d, e) in rows)
open(os.path.join(DOCS, "aqa_fm_seed.txt"),
     "w", encoding="utf-8").write(seed)
print(f"wrote migration with {len(rows)} rows")
