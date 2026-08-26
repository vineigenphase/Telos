"""Edexcel sciences: Physics (9PH0), Chemistry (9CH0), Biology A (9BN0).

Paper-to-topic mappings are read from each specification's "this paper will
examine the following topics" list, not inferred. They are not symmetrical and
could not have been guessed — Chemistry Paper 1 takes twelve of the nineteen
topics and Paper 2 takes ten, overlapping on four.

Physics is taught by two routes, Concept and Salters Horners, which sit the
same papers. The Concept topic names are used because they match the numbered
Topics 1-13 the rest of the specification is organised by.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from pearson_extract import extract, NOTES

SCRATCH = DOCS
TELOS = REPO
# No 2018 PDF to hand; 2019 and 2022-2025 are the five real series available.
YEARS = ["2019", "2022", "2023", "2024", "2025"]

PHYS = {
    1: "Working as a Physicist", 2: "Mechanics", 3: "Electric Circuits",
    4: "Materials", 5: "Waves and Particle Nature of Light",
    6: "Further Mechanics", 7: "Electric and Magnetic Fields",
    8: "Nuclear and Particle Physics", 9: "Thermodynamics", 10: "Space",
    11: "Nuclear Radiation", 12: "Gravitational Fields", 13: "Oscillations",
}
PHYS_P1 = [1, 2, 3, 6, 7, 8]
PHYS_P2 = [1, 4, 5, 9, 10, 11, 12, 13]

CHEM = {
    1: "Atomic Structure and the Periodic Table", 2: "Bonding and Structure",
    3: "Redox I", 4: "Inorganic Chemistry and the Periodic Table",
    5: "Formulae, Equations and Amounts of Substance", 6: "Organic Chemistry I",
    7: "Modern Analytical Techniques I", 8: "Energetics I", 9: "Kinetics I",
    10: "Equilibrium I", 11: "Equilibrium II", 12: "Acid-base Equilibria",
    13: "Energetics II", 14: "Redox II", 15: "Transition Metals",
    16: "Kinetics II", 17: "Organic Chemistry II", 18: "Organic Chemistry III",
    19: "Modern Analytical Techniques II",
}
CHEM_P1 = [1, 2, 3, 4, 5, 8, 10, 11, 12, 13, 14, 15]
CHEM_P2 = [2, 3, 5, 6, 7, 9, 16, 17, 18, 19]

BIO = {
    1: "Lifestyle, Health and Risk", 2: "Genes and Health",
    3: "Voice of the Genome", 4: "Biodiversity and Natural Resources",
    5: "On the Wild Side", 6: "Immunity, Infection and Forensics",
    7: "Run for your Life", 8: "Grey Matter",
}
BIO_P1 = [1, 2, 3, 4, 5, 6]
BIO_P2 = [1, 2, 3, 4, 7, 8]

SPECS = [
    ("Physics", "Physics", {"1": 90, "2": 90, "3": 120}, 30, "#5E8B7E",
     PHYS, PHYS_P1, PHYS_P2,
     ("Advanced Physics I", "Advanced Physics II", "General and Practical Principles")),
    ("Chemistry", "Chemistry", {"1": 90, "2": 90, "3": 120}, 31, "#5E8B7E",
     CHEM, CHEM_P1, CHEM_P2,
     ("Advanced Inorganic and Physical", "Advanced Organic and Physical",
      "General and Practical Principles")),
    ("Biology", "Biology A (Salters Nuffield)", {"1": 100, "2": 100, "3": 100}, 32, "#5E9E6B",
     BIO, BIO_P1, BIO_P2,
     ("Natural Environment and Species Survival", "Energy, Exercise and Co-ordination",
      "General and Practical Applications")),
]


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


seeds, entries = [], []
for subject, spec_name, expect, num, colour, topics, p1, p2, names in SPECS:
    data, probs = extract(spec_name, expect, YEARS)
    if probs:
        print("REFUSING " + subject + ":")
        for p in probs:
            print("  -", p)
        raise SystemExit(1)

    rows, no_star = [], 0
    for (paper, year) in sorted(data, key=lambda k: (k[1], k[0])):
        mx, a_s, a, b, c, d, e = data[(paper, year)]
        if a_s is None:
            no_star += 1
            continue          # a component with no published A* is not stored
        assert a_s > a > b > c > d > e > 0, "%s %s %s" % (subject, paper, year)
        rows.append(("Paper " + paper, year, a_s, a, b, c, d, e))

    values = ",\n".join(
        "    ('%s', 'Edexcel', '%s', '%s', 'June', %d, %d, %d, %d, %d, %d)"
        % (subject, p, y, a_s, a, b, c, d, e)
        for (p, y, a_s, a, b, c, d, e) in rows)

    sql = (
        "-- 0%d_edexcel_%s_boundaries.sql\n"
        "-- Edexcel A-level %s (%s), per paper.\n"
        "--\n"
        "-- Notional component boundaries. Pearson prints these in four different\n"
        "-- layouts across the series — name and numbers on one line, split across\n"
        "-- two, one number per line, and in one case a row whose paper label is\n"
        "-- missing entirely. Every row is checked against its paper's expected max\n"
        "-- mark, which is what makes reading four layouts safe.\n"
        "--\n"
        "-- No 2018 series is stored: that document was not to hand. No 2020 or 2021\n"
        "-- either — no summer exam series.\n"
        "--\n"
        "-- Idempotent.\n\n"
        "DELETE FROM grade_boundaries WHERE subject = '%s' AND board = 'Edexcel';\n\n"
        "INSERT INTO grade_boundaries\n"
        "    (subject, board, paper_code, year, series,\n"
        "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
        "VALUES\n%s;\n"
    ) % (num, subject.lower(), subject, spec_name, subject, values)

    with open(os.path.join(TELOS, "migrations",
                           "0%d_edexcel_%s_boundaries.sql" % (num, subject.lower())),
              "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sql)

    seeds.append("\n".join(
        '    ("%s", "Edexcel", "%s", "%s", "June", %d, %d, %d, %d),' % (subject, p, y, a_s, a, b, c)
        for (p, y, a_s, a, b, c, d, e) in rows))
    print("%s: %d rows%s" % (subject, len(rows),
                             " (%d skipped: no published A*)" % no_star if no_star else ""))

    entries.append('''        "%s": {
            "color": "%s",
            "level": "A-Level",
            # %s. Three compulsory papers; Paper 3 is synoptic and assesses
            # every topic, which is why its list is the whole subject.
            "papers": [
                {"code": "Paper 1", "name": "%s", "max_marks": %d},
                {"code": "Paper 2", "name": "%s", "max_marks": %d},
                {"code": "Paper 3", "name": "%s", "max_marks": %d},
            ],
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Paper-to-topic mapping read from the specification, not inferred.
            # Papers 1 and 2 overlap: several topics are assessed by both.
            "topics": {
                "Paper 1": [
%s],
                "Paper 2": [
%s],
                "Paper 3": [
%s],
            },
        },
''' % (subject, colour, spec_name,
       names[0], expect["1"], names[1], expect["2"], names[2], expect["3"],
       fmt([topics[i] for i in p1]),
       fmt([topics[i] for i in p2]),
       fmt([topics[i] for i in sorted(topics)])))

with open(os.path.join(SCRATCH, "edx_sci_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n\n".join(seeds))
with open(os.path.join(SCRATCH, "edx_sci_entries.txt"), "w", encoding="utf-8") as fh:
    fh.write("".join(entries))
for n in NOTES:
    print("NOTE:", n)
print("entries written")
