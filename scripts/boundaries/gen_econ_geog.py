"""Catalogue entries and migrations for AQA Economics (7136) and Geography (7037).

Geography's third component is a teacher-marked fieldwork investigation. It is
deliberately absent from both the catalogue and the boundaries: Telos tracks
past papers, and there is no past paper to attempt for your own coursework.
Offering it would invite a student to "log" something they cannot sit.
"""

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

# ── Economics 7136: sections 4.1.1-4.1.8 (micro), 4.2.1-4.2.6 (macro) ───────
ECON_MICRO = [
    "Economic Methodology and the Economic Problem",
    "Individual Economic Decision Making",
    "Price Determination in a Competitive Market",
    "Production, Costs and Revenue",
    "Perfect Competition, Imperfect Competition and Monopoly",
    "The Labour Market",
    "Distribution of Income and Wealth",
    "Market Mechanism, Market Failure and Government Intervention",
]
ECON_MACRO = [
    "Measurement of Macroeconomic Performance",
    "How the Macroeconomy Works",
    "Economic Performance",
    "Financial Markets and Monetary Policy",
    "Fiscal Policy and Supply-side Policies",
    "The International Economy",
]
ECON_ALL = ECON_MICRO + ECON_MACRO

# ── Geography 7037: 3.1.1-3.1.6 (physical), 3.2.1-3.2.5 (human) ────────────
GEOG_PHYSICAL = [
    "Water and Carbon Cycles",
    "Hot Desert Systems and Landscapes",
    "Coastal Systems and Landscapes",
    "Glacial Systems and Landscapes",
    "Hazards",
    "Ecosystems Under Stress",
]
GEOG_HUMAN = [
    "Global Systems and Global Governance",
    "Changing Places",
    "Contemporary Urban Environments",
    "Population and the Environment",
    "Resource Security",
]

print("Economics  P1=%d P2=%d P3=%d" % (len(ECON_MICRO), len(ECON_MACRO), len(ECON_ALL)))
print("Geography  P1=%d P2=%d" % (len(GEOG_PHYSICAL), len(GEOG_HUMAN)))

YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]
SPECS = [
    ("Economics", "7136", {"1": 80, "2": 80, "3": 80}, 240, 21,
     "Three compulsory papers, 80 marks each."),
    ("Geography", "7037", {"1": 120, "2": 120}, 300, 22,
     "Two written papers of 120 marks. The 60-mark fieldwork investigation\n"
     "-- (component C) is coursework, marked by teachers, and is not stored: there\n"
     "-- is no past paper to attempt for your own investigation."),
]

seed_blocks = []
for subject, qual, expect, total, num, note in SPECS:
    data, probs = extract(qual, expect, YEARS)
    if probs:
        print("REFUSING " + subject + ":")
        for p in probs:
            print("  -", p)
        raise SystemExit(1)

    rows = []
    for (comp, year) in sorted(data, key=lambda k: (k[1], k[0])):
        mx, a_s, a, b, c, d, e = data[(comp, year)]
        assert a_s > a > b > c > d > e > 0, "%s %s %s not descending" % (subject, comp, year)
        rows.append(("Paper " + comp, year, a_s, a, b, c, d, e))

    values = ",\n".join(
        "    ('%s', 'AQA', '%s', '%s', 'June', %d, %d, %d, %d, %d, %d)"
        % (subject, p, y, a_s, a, b, c, d, e)
        for (p, y, a_s, a, b, c, d, e) in rows)

    sql = (
        "-- 0%d_aqa_%s_boundaries.sql\n"
        "-- AQA A-level %s (%s), per paper.\n"
        "--\n"
        "-- %s\n"
        "--\n"
        "-- Notional component boundaries, derived by AQA from the qualification\n"
        "-- award. The subject row out of %d is not stored.\n"
        "--\n"
        "-- No 2020 or 2021: no summer exam series.\n"
        "--\n"
        "-- Idempotent.\n\n"
        "DELETE FROM grade_boundaries WHERE subject = '%s' AND board = 'AQA';\n\n"
        "INSERT INTO grade_boundaries\n"
        "    (subject, board, paper_code, year, series,\n"
        "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
        "VALUES\n%s;\n"
    ) % (num, subject.lower(), subject, qual, note, total, subject, values)

    out = os.path.join(TELOS, "migrations", "0%d_aqa_%s_boundaries.sql" % (num, subject.lower()))
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sql)

    seed_blocks.append("\n".join(
        '    ("%s", "AQA", "%s", "%s", "June", %d, %d, %d, %d),' % (subject, p, y, a_s, a, b, c)
        for (p, y, a_s, a, b, c, d, e) in rows))
    print("  %s: migration 0%d with %d rows" % (subject, num, len(rows)))

with open(os.path.join(SCRATCH, "eg_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n\n".join(seed_blocks))


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


entries = '''        "Economics": {
            "color": "#C08A3E",
            "level": "A-Level",
            # 7136. Three compulsory papers, 80 marks each.
            "papers": [
                {"code": "Paper 1", "name": "Markets and Market Failure",     "max_marks": 80},
                {"code": "Paper 2", "name": "National and International Economy", "max_marks": 80},
                {"code": "Paper 3", "name": "Economic Principles and Issues", "max_marks": 80},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Specification sections 4.1.1-4.1.8 and 4.2.1-4.2.6. AQA describes
            # them as "content 1-14": Paper 1 assesses 1-8, Paper 2 assesses
            # 9-14, and Paper 3 assesses all fourteen.
            "topics": {
                "Paper 1": [
__ECON_P1__],
                "Paper 2": [
__ECON_P2__],
                "Paper 3": [
__ECON_P3__],
            },
        },
        "Geography": {
            "color": "#6E8F5E",
            "level": "A-Level",
            # 7037. Two written papers of 120 marks. The third component is a
            # 3,000-4,000 word fieldwork investigation, marked by teachers —
            # not a past paper, so it is not offered here and its boundaries
            # are not stored.
            "papers": [
                {"code": "Paper 1", "name": "Physical Geography", "max_marks": 120},
                {"code": "Paper 2", "name": "Human Geography",    "max_marks": 120},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Sections 3.1.1-3.1.6 and 3.2.1-3.2.5. Each paper offers choices
            # within it — Paper 1 Section B is one of three landscape systems,
            # Section C one of two — so every option is listed: different
            # students sit different questions on the same paper, and each needs
            # the topic they actually answered.
            "topics": {
                "Paper 1": [
__GEOG_P1__],
                "Paper 2": [
__GEOG_P2__],
            },
        },
'''
for key, items in (("__ECON_P1__", ECON_MICRO), ("__ECON_P2__", ECON_MACRO),
                   ("__ECON_P3__", ECON_ALL),
                   ("__GEOG_P1__", GEOG_PHYSICAL), ("__GEOG_P2__", GEOG_HUMAN)):
    entries = entries.replace(key, fmt(items))

with open(os.path.join(SCRATCH, "eg_entries.txt"), "w", encoding="utf-8") as fh:
    fh.write(entries)
print("catalogue entries written")
