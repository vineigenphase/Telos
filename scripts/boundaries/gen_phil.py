"""Catalogue entry and migration for AQA A-level Philosophy (7172)."""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from aqa_extract import extract

SCRATCH = DOCS
TELOS = REPO
# Reformed Philosophy was first taught in 2017 and first assessed in 2019,
# so there is no 2018 series. Stated explicitly rather than letting the
# extractor report two missing components on every run.
YEARS = ["2019", "2022", "2023", "2024", "2025"]

PAPER1 = [
    "What is Knowledge?", "Perception as a Source of Knowledge",
    "Reason as a Source of Knowledge", "The Limits of Knowledge",
    "Normative Ethical Theories", "Applied Ethics", "Meta-ethics",
]
PAPER2 = [
    "The Concept and Nature of God", "Arguments Relating to the Existence of God",
    "Religious Language", "What Do We Mean by Mind?", "Dualist Theories",
    "Physicalist Theories", "Functionalism",
]

data, probs = extract("7172", {"1": 100, "2": 100}, YEARS)
if probs:
    print("REFUSING:")
    for p in probs:
        print("  -", p)
    raise SystemExit(1)

rows = []
for (comp, year) in sorted(data, key=lambda k: (k[1], k[0])):
    mx, a_s, a, b, c, d, e = data[(comp, year)]
    assert a_s > a > b > c > d > e > 0, "%s %s not descending" % (comp, year)
    rows.append(("Paper " + comp, year, a_s, a, b, c, d, e))

values = ",\n".join(
    "    ('Philosophy', 'AQA', '%s', '%s', 'June', %d, %d, %d, %d, %d, %d)"
    % (p, y, a_s, a, b, c, d, e)
    for (p, y, a_s, a, b, c, d, e) in rows)

sql = (
    "-- 026_aqa_philosophy_boundaries.sql\n"
    "-- AQA A-level Philosophy (7172): two 100-mark papers, both compulsory.\n"
    "--\n"
    "-- Paper 1 is epistemology and moral philosophy; Paper 2 is the metaphysics\n"
    "-- of God and of mind. No options and no coursework, so both components are\n"
    "-- papers a student can sit and mark from published materials.\n"
    "--\n"
    "-- Notional component boundaries, derived by AQA from the qualification\n"
    "-- award. The subject row out of 200 is not stored.\n"
    "--\n"
    "-- No 2020 or 2021: no summer exam series.\n"
    "--\n"
    "-- Idempotent.\n\n"
    "DELETE FROM grade_boundaries WHERE subject = 'Philosophy' AND board = 'AQA';\n\n"
    "INSERT INTO grade_boundaries\n"
    "    (subject, board, paper_code, year, series,\n"
    "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
    "VALUES\n%s;\n"
) % values

with open(os.path.join(TELOS, "migrations", "026_aqa_philosophy_boundaries.sql"),
          "w", encoding="utf-8", newline="\n") as fh:
    fh.write(sql)

with open(os.path.join(SCRATCH, "phil_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(
        '    ("Philosophy", "AQA", "%s", "%s", "June", %d, %d, %d, %d),' % (p, y, a_s, a, b, c)
        for (p, y, a_s, a, b, c, d, e) in rows))


def fmt(items, indent=" " * 26):
    out, line = [], ""
    for it in items:
        piece = '"%s", ' % it
        if len(line) + len(piece) > 74:
            out.append(indent + line.rstrip())
            line = ""
        line += piece
    if line:
        out.append(indent + line.rstrip().rstrip(","))
    return "\n".join(out)


entry = '''        "Philosophy": {
            "color": "#8A8985",
            "level": "A-Level",
            # 7172. Two 100-mark papers, both compulsory, no options and no
            # coursework — the simplest shape in the catalogue.
            "papers": [
                {"code": "Paper 1", "name": "Epistemology and Moral Philosophy", "max_marks": 100},
                {"code": "Paper 2", "name": "Metaphysics of God and of Mind",    "max_marks": 100},
            ],
            # First assessed in 2019.
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Specification sections 3.1-3.4. Each paper is two sections of five
            # questions, and the sub-sections below are what those questions are
            # drawn from.
            "topics": {
                "Paper 1": [
%s],
                "Paper 2": [
%s],
            },
        },
''' % (fmt(PAPER1), fmt(PAPER2))

with open(os.path.join(SCRATCH, "phil_entry.txt"), "w", encoding="utf-8") as fh:
    fh.write(entry)
print("Philosophy: migration 026 with %d rows" % len(rows))
