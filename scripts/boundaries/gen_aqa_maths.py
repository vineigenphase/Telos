"""Migration 017 and seed rows for AQA A-level Mathematics (7357)."""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from aqa_extract import extract

YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]
CODE = {"1": "Paper 1", "2": "Paper 2", "3": "Paper 3"}

data, probs = extract("7357", {"1": 100, "2": 100, "3": 100}, YEARS)
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
    f"    ('Maths', 'AQA', '{p}', '{y}', 'June', {a_s}, {a}, {b}, {c}, {d}, {e})"
    for (p, y, a_s, a, b, c, d, e) in rows)

sql = f'''-- 017_aqa_maths_boundaries.sql
-- AQA A-level Mathematics (7357), per paper. Three 100-mark papers.
--
-- These are AQA's notional component boundaries. AQA awards at qualification
-- level and derives the per-paper figures from it, so they are its own
-- statement of what a raw mark on that paper is worth rather than a separately
-- awarded boundary. That is exactly the question Telos asks — a student logs
-- one paper and wants to know what it was worth — and it is the same basis as
-- the Edexcel figures already stored, which Pearson likewise calls notional.
--
-- It also explains the even spacing in some series: 2025 Paper 1 runs
-- 87/74/61/48/35/22, steps of thirteen throughout. That is the derivation
-- showing through, not a transcription error.
--
-- The subject-level row (out of 300) is deliberately not stored.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Maths' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
{values};
'''
open(os.path.join(MIGRATIONS, "017_aqa_maths_boundaries.sql"),
     "w", encoding="utf-8", newline="\n").write(sql)

seed = "\n".join(
    f'    ("Maths", "AQA", "{p}", "{y}", "June", {a_s}, {a}, {b}, {c}),'
    for (p, y, a_s, a, b, c, d, e) in rows)
open(os.path.join(DOCS, "aqa_maths_seed.txt"),
     "w", encoding="utf-8").write(seed)
print(f"wrote migration with {len(rows)} rows")
