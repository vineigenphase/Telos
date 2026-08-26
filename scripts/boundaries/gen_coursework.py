"""Reinstate the non-written components: Geography's fieldwork investigation
and the three MFL speaking exams.

These were left out on the rule that a paper belongs in Telos if a student can
sit and mark it alone. That rule was wrong in one respect: these components
count toward the grade. Excluding them meant a Geography student's predicted
grade was computed from 80% of their qualification and an MFL student's from
70%, silently. They are included now, marked so the app asks for a single
overall mark rather than a question-by-question breakdown, which is meaningless
for a 3,000-word investigation or a 21-minute oral.

The OCR Practical Endorsements stay out, and that is the same rule applied
correctly: they are reported separately and do not contribute to the grade at
all, so there is nothing for a prediction to use.

Speaking is stored from the teacher-conducted variant. AQA publishes 3T and 3V
(visiting examiner) separately and their boundaries are identical in every
series checked, so one row serves both and the student does not have to know
which their centre used.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from aqa_extract import extract

TELOS = REPO
SCRATCH = DOCS
YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]

JOBS = [
    ("Geography", "7037", "C", 60, "NEA"),
    ("French", "7652", "3T", 60, "Paper 3"),
    ("German", "7662", "3T", 60, "Paper 3"),
    ("Spanish", "7692", "3T", 60, "Paper 3"),
]

all_values, seed_lines = [], []
for subject, qual, comp, mx, paper_code in JOBS:
    data, probs = extract(qual, {comp: mx}, YEARS)
    if probs:
        print("REFUSING " + subject + ":")
        for p in probs:
            print("  -", p)
        raise SystemExit(1)
    for (c, year) in sorted(data, key=lambda k: k[1]):
        m, a_s, a, b, cc, d, e = data[(c, year)]
        assert m == mx and a_s > a > b > cc > d > e > 0, "%s %s" % (subject, year)
        all_values.append("    ('%s', 'AQA', '%s', '%s', 'June', %d, %d, %d, %d, %d, %d)"
                          % (subject, paper_code, year, a_s, a, b, cc, d, e))
        seed_lines.append('    ("%s", "AQA", "%s", "%s", "June", %d, %d, %d, %d),'
                          % (subject, paper_code, year, a_s, a, b, cc))
    print("%s %s: %d rows" % (subject, paper_code, len(data)))

sql = (
    "-- 033_coursework_components.sql\n"
    "-- The non-written components that count toward the grade.\n"
    "--\n"
    "-- Geography's fieldwork investigation (7037/C, 60 marks) and the MFL\n"
    "-- speaking exams (7652/3T, 7662/3T, 7692/3T, 60 marks each) were previously\n"
    "-- excluded on the rule that a paper belongs here if a student can sit and\n"
    "-- mark it alone. That rule was wrong in one respect: these count toward the\n"
    "-- grade. Leaving them out meant a Geography prediction was built from 80%%\n"
    "-- of the qualification and an MFL prediction from 70%%, without saying so.\n"
    "--\n"
    "-- The OCR Practical Endorsements stay out, which is the same rule applied\n"
    "-- correctly: they are reported separately and contribute nothing to the\n"
    "-- grade, so a prediction has nothing to do with them.\n"
    "--\n"
    "-- Speaking uses the teacher-conducted variant. AQA publishes 3T and 3V\n"
    "-- separately and their boundaries are identical in every series checked, so\n"
    "-- one row serves both and a student need not know which their centre used.\n"
    "--\n"
    "-- RAW boundaries: AQA scales speaking and publishes a 120-mark row too.\n"
    "--\n"
    "-- Idempotent.\n\n"
    "DELETE FROM grade_boundaries WHERE board = 'AQA'\n"
    "  AND ((subject = 'Geography' AND paper_code = 'NEA')\n"
    "    OR (subject IN ('French', 'German', 'Spanish') AND paper_code = 'Paper 3'));\n\n"
    "INSERT INTO grade_boundaries\n"
    "    (subject, board, paper_code, year, series,\n"
    "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
    "VALUES\n%s;\n"
) % (",\n".join(all_values))

with open(os.path.join(TELOS, "migrations", "033_coursework_components.sql"),
          "w", encoding="utf-8", newline="\n") as fh:
    fh.write(sql)
with open(os.path.join(SCRATCH, "coursework_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(seed_lines))
print("migration 033 written with %d rows" % len(all_values))
