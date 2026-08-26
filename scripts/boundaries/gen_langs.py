"""Catalogue entries and migrations for AQA French (7652), German (7662)
and Spanish (7692).

Two decisions are worth reading before changing anything here.

Speaking is not included. AQA's third component is a 21-23 minute oral
conducted by a teacher or visiting examiner. The rule applied across the
catalogue is: a paper belongs here if a student can obtain it, sit it under
timed conditions, and mark it against a published mark scheme on their own. A
written paper passes that test; a speaking exam and a coursework investigation
do not. Geography's fieldwork investigation is left out for the same reason.

Paper 2 carries two topics, not a list of set works. The paper is two essays on
works the student chose from AQA's prescribed lists, and those lists differ by
language and change between series. "Literary Text Essay" and "Film Essay"
are true for every student and still tell them which of the two is costing
them marks; naming every set text would produce a long list of which all but
two entries are irrelevant to any given student.
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
YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]

LANGS = [
    ("French", "7652", "#4C7EF3", 23, [
        "Aspects of French-speaking Society: Current Trends",
        "Aspects of French-speaking Society: Current Issues",
        "Artistic Culture in the French-speaking World",
        "Aspects of Political Life in the French-speaking World",
    ], "Translation into French"),
    ("German", "7662", "#C08A3E", 24, [
        "Aspects of German-speaking Society",
        "Artistic Culture in the German-speaking World",
        "Multiculturalism in German-speaking Society",
        "Aspects of Political Life in German-speaking Society",
    ], "Translation into German"),
    ("Spanish", "7692", "#B4574C", 25, [
        "Aspects of Hispanic Society",
        "Artistic Culture in the Hispanic World",
        "Multiculturalism in Hispanic Society",
        "Aspects of Political Life in Hispanic Society",
    ], "Translation into Spanish"),
]

PAPER2 = ["Literary Text Essay", "Film Essay"]


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


seed_blocks, entries = [], []
for subject, qual, colour, num, themes, into_target in LANGS:
    data, probs = extract(qual, {"1": 100, "2": 80}, YEARS)
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
        "-- AQA A-level %s (%s): Paper 1 (100) and Paper 2 (80).\n"
        "--\n"
        "-- RAW boundaries, not scaled. AQA scales both of these components and\n"
        "-- prints two rows for each: the raw boundaries, then the scaled ones —\n"
        "-- Paper 1 appears both as \"100 91 82 70...\" and as \"200 182 164 140...\".\n"
        "-- A student marks their own paper out of the raw total, so the extractor\n"
        "-- picks the row whose max matches the paper's real mark. Taking the last\n"
        "-- match instead would have doubled every boundary and graded everyone U.\n"
        "--\n"
        "-- Speaking (component 3) is not stored. It is a 21-23 minute oral\n"
        "-- conducted by a teacher or visiting examiner, which a student cannot sit\n"
        "-- or mark alone from published materials.\n"
        "--\n"
        "-- No 2020 or 2021: no summer exam series.\n"
        "--\n"
        "-- Idempotent.\n\n"
        "DELETE FROM grade_boundaries WHERE subject = '%s' AND board = 'AQA';\n\n"
        "INSERT INTO grade_boundaries\n"
        "    (subject, board, paper_code, year, series,\n"
        "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
        "VALUES\n%s;\n"
    ) % (num, subject.lower(), subject, qual, subject, values)

    out = os.path.join(TELOS, "migrations", "0%d_aqa_%s_boundaries.sql" % (num, subject.lower()))
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sql)

    seed_blocks.append("\n".join(
        '    ("%s", "AQA", "%s", "%s", "June", %d, %d, %d, %d),' % (subject, p, y, a_s, a, b, c)
        for (p, y, a_s, a, b, c, d, e) in rows))

    paper1 = themes + ["Translation into English", into_target]
    entry = '''        "%s": {
            "color": "%s",
            "level": "A-Level",
            # %s. Paper 1 is listening, reading and translation; Paper 2 is two
            # essays on set works. The speaking component is not tracked — it is
            # an oral conducted by an examiner, not a paper a student can sit
            # and mark alone.
            "papers": [
                {"code": "Paper 1", "name": "Listening, Reading and Writing", "max_marks": 100},
                {"code": "Paper 2", "name": "Writing",                        "max_marks": 80},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # The four specification themes, plus the two translation tasks —
            # separately marked at 10 each, and the place students most often
            # lose marks without noticing which half of the paper did it.
            "topics": {
                "Paper 1": [
%s],
                # Two essays on works the student chose from AQA's prescribed
                # lists. Naming every set text would be a long list of which all
                # but two entries are irrelevant to any given student.
                "Paper 2": [
%s],
            },
        },
''' % (subject, colour, qual, fmt(paper1), fmt(PAPER2))
    entries.append(entry)
    print("  %s: migration 0%d with %d rows" % (subject, num, len(rows)))

with open(os.path.join(SCRATCH, "lang_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n\n".join(seed_blocks))
with open(os.path.join(SCRATCH, "lang_entries.txt"), "w", encoding="utf-8") as fh:
    fh.write("".join(entries))
print("catalogue entries written")
