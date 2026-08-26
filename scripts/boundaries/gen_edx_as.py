"""Edexcel AS-levels: Mathematics (8MA0), Further Mathematics (8FM0),
Physics (8PH0), Chemistry (8CH0), Biology A (8BN0).

Same reasoning as the OCR AS load: a separate catalogue key suffixed "(AS)",
a_star NULL on every row, and every component checked against its own max mark.

Two things here are not symmetrical with the A-level and are read from the
specification rather than assumed:

  * AS Mathematics Paper 2 is 60 marks, not 100. Paper 1 (Pure) is 100. An
    A-level Maths student sits three 100-mark papers, so carrying the A-level
    shape across would have overstated Paper 2 by two thirds.
  * AS Further Mathematics Paper 2 is not one paper. It is two 40-mark option
    sections chosen from eight, and Pearson publishes each option separately
    under labels 21-28. They are stored as eight optional papers of which a
    student picks two, which is what the student actually sits.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from pearson_extract import extract, NOTES

TELOS = REPO
SCRATCH = DOCS
YEARS = ["2019", "2022", "2023", "2024", "2025"]

PURE_AS = ["Proof", "Algebra and Functions", "Coordinate Geometry",
           "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
           "Differentiation", "Integration", "Vectors", "Numerical Methods"]
STATS_MECH_AS = ["Statistical Sampling", "Data Presentation and Interpretation",
                 "Probability", "Statistical Distributions",
                 "Statistical Hypothesis Testing", "Quantities and Units in Mechanics",
                 "Kinematics", "Forces and Newton's Laws"]

PHYS_AS = ["Working as a Physicist", "Mechanics", "Electric Circuits", "Materials",
           "Waves and Particle Nature of Light"]
CHEM_AS = ["Atomic Structure and the Periodic Table", "Bonding and Structure",
           "Redox I", "Inorganic Chemistry and the Periodic Table",
           "Formulae, Equations and Amounts of Substance", "Organic Chemistry I",
           "Modern Analytical Techniques I", "Energetics I", "Kinetics I",
           "Equilibrium I"]
BIO_AS = ["Lifestyle, Health and Risk", "Genes and Health", "Voice of the Genome",
          "Biodiversity and Natural Resources"]

FM_OPTIONS = [
    ("21", "Further Pure Mathematics 1",
     ["Complex Numbers", "Roots of Polynomials", "Series", "Coordinate Systems",
      "Matrix Algebra", "Proof by Induction"]),
    ("22", "Further Pure Mathematics 2",
     ["Inequalities", "Series", "First Order Differential Equations",
      "Second Order Differential Equations", "Maclaurin and Taylor Series",
      "Polar Coordinates"]),
    ("23", "Further Statistics 1",
     ["Discrete Probability Distributions", "Poisson Distribution",
      "Geometric and Negative Binomial", "Hypothesis Testing",
      "Chi-squared Tests", "Probability Generating Functions"]),
    ("24", "Further Statistics 2",
     ["Linear Regression", "Continuous Probability Distributions",
      "Correlation", "Combinations of Random Variables", "Quality of Tests"]),
    ("25", "Further Mechanics 1",
     ["Momentum and Impulse", "Work, Energy and Power", "Elastic Strings and Springs",
      "Elastic Collisions in One Dimension"]),
    ("26", "Further Mechanics 2",
     ["Motion in a Circle", "Centres of Mass", "Further Dynamics",
      "Further Kinematics"]),
    ("27", "Decision Mathematics 1",
     ["Algorithms and Graph Theory", "Algorithms on Graphs", "Critical Path Analysis",
      "Linear Programming", "Route Inspection"]),
    ("28", "Decision Mathematics 2",
     ["Transportation Problems", "Allocation Problems", "Flows in Networks",
      "Dynamic Programming", "Game Theory"]),
]

# (key, display name, colour, pearson title, {paper label: max}, papers, topics)
SPECS = [
    ("Maths (AS)", "Maths", "#C9A227", "Mathematics",
     {"1": 100, "2": 60},
     [("Paper 1", "Pure Mathematics", 100, "1"),
      ("Paper 2", "Statistics and Mechanics", 60, "2")],
     {"Paper 1": PURE_AS, "Paper 2": STATS_MECH_AS}),

    ("Further Maths (AS)", "Further Maths", "#C9A227", "Further Mathematics",
     dict({"1": 80}, **{lab: 40 for lab, _n, _t in FM_OPTIONS}),
     [("Paper 1", "Core Pure Mathematics", 80, "1")]
     + [("Paper 2%s" % lab, name, 40, lab, True) for lab, name, _t in FM_OPTIONS],
     dict({"Paper 1": ["Complex Numbers", "Matrices", "Vectors", "Roots of Polynomials",
                       "Series", "Proof by Induction"]},
          **{"Paper 2%s" % lab: tl for lab, _n, tl in FM_OPTIONS})),

    ("Physics (AS)", "Physics", "#5E8B7E", "Physics",
     {"1": 80, "2": 80},
     [("Paper 1", "Core Physics I", 80, "1"),
      ("Paper 2", "Core Physics II", 80, "2")],
     {"Paper 1": PHYS_AS, "Paper 2": PHYS_AS}),

    ("Chemistry (AS)", "Chemistry", "#5E8B7E", "Chemistry",
     {"1": 80, "2": 80},
     [("Paper 1", "Core Inorganic and Physical Chemistry", 80, "1"),
      ("Paper 2", "Core Organic and Physical Chemistry", 80, "2")],
     {"Paper 1": CHEM_AS, "Paper 2": CHEM_AS}),

    ("Biology (AS)", "Biology", "#5E9E6B", "Biology A (Salters Nuffield)",
     {"1": 80, "2": 80},
     [("Paper 1", "Lifestyle, Transport, Genes and Health", 80, "1"),
      ("Paper 2", "Development, Plants and the Environment", 80, "2")],
     {"Paper 1": BIO_AS, "Paper 2": BIO_AS}),
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


all_values, seeds, entries = [], [], []
for key, name, colour, title, expect, papers, topics in SPECS:
    data, probs = extract(title, expect, YEARS, level="AS")
    # A series that simply does not carry this qualification is reported, but
    # only a bad READ is fatal — a missing paper in a year we do have is.
    hard = [p for p in probs if "no PDF" not in p]
    missing_years = {p.split(":")[0] for p in hard}
    usable = [y for y in YEARS if y not in missing_years]
    if not usable:
        print("REFUSING " + key + ":")
        for p in probs:
            print("  -", p)
        raise SystemExit(1)
    if hard:
        print("  %s: skipping %s (%s)" % (key, ", ".join(sorted(missing_years)),
                                          hard[0].split(": ", 1)[1]))

    rows = []
    for p in papers:
        code, _pname, mx, lab = p[0], p[1], p[2], p[3]
        for year in usable:
            got = data.get((lab, year))
            if got is None:
                continue
            m, a_s, a, b, c, d, e = got
            assert m == mx, "%s %s %s max %s" % (key, lab, year, m)
            assert a_s is None, "%s %s %s has an A*: %s" % (key, lab, year, a_s)
            assert a > b > c > d > e > 0, "%s %s %s" % (key, lab, year)
            rows.append((code, year, a, b, c, d, e))
    rows.sort(key=lambda r: (r[1], r[0]))

    for code, year, a, b, c, d, e in rows:
        all_values.append(
            "    ('%s', 'Edexcel', '%s', '%s', 'June', NULL, %d, %d, %d, %d, %d)"
            % (key, code, year, a, b, c, d, e))
        seeds.append('    ("%s", "Edexcel", "%s", "%s", "June", None, %d, %d, %d),'
                     % (key, code, year, a, b, c))
    print("%s: %d rows" % (key, len(rows)))

    paper_lines = "\n".join(
        '                {"code": "%s", "name": "%s", "max_marks": %d%s},'
        % (p[0], p[1], p[2], ', "optional": True' if len(p) > 4 else "")
        for p in papers)
    topic_lines = "\n".join(
        '                "%s": [\n%s],' % (code, fmt(tl))
        for code, tl in topics.items())
    choose = 2 if key == "Further Maths (AS)" else 0
    entry = '        "%s": {\n' % key
    entry += '            "name": "%s",\n' % name
    entry += '            "color": "%s",\n' % colour
    entry += '            "level": "AS-Level",\n'
    entry += ('            # AS %s. A qualification in its own right, graded A-E\n'
              '            # with no A*.\n' % title)
    entry += '            "papers": [\n%s\n            ],\n' % paper_lines
    if choose:
        entry += ('            # Paper 2 is two 40-mark option sections, not one\n'
                  '            # paper; Pearson publishes each option separately.\n')
        entry += '            "choose_optional": %d,\n' % choose
    entry += '            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],\n'
    entry += '            "topics": {\n%s\n            },\n' % topic_lines
    entry += '        },\n'
    entries.append(entry)

sql = (
    "-- 035_edexcel_as_boundaries.sql\n"
    "-- Edexcel AS-levels: Mathematics (8MA0), Further Mathematics (8FM0),\n"
    "-- Physics (8PH0), Chemistry (8CH0), Biology A (8BN0).\n"
    "--\n"
    "-- a_star is NULL on every row: an AS-level is graded A-E. prediction.py\n"
    "-- reads the absence and stops the grade ladder at A.\n"
    "--\n"
    "-- Read from the AS section of the same series documents as the A-levels.\n"
    "-- Those tables use the no-A* layout the parser already handled for\n"
    "-- A-level Mathematics, so the shape is not new - but the title must match\n"
    "-- exactly, because 'AS Mathematics' is a substring of nothing while\n"
    "-- 'AS Further Mathematics' is its own qualification.\n"
    "--\n"
    "-- AS Mathematics Paper 2 is 60 marks, not 100. Carrying the A-level shape\n"
    "-- across would have overstated it by two thirds; it is read from the\n"
    "-- document and checked, like every other row.\n"
    "--\n"
    "-- No 2018 document to hand, and no 2020 or 2021 - no summer exam series.\n"
    "--\n"
    "-- Idempotent.\n\n"
    "DELETE FROM grade_boundaries WHERE board = 'Edexcel' AND subject LIKE '%% (AS)';\n\n"
    "INSERT INTO grade_boundaries\n"
    "    (subject, board, paper_code, year, series,\n"
    "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
    "VALUES\n%s;\n"
) % (",\n".join(all_values))

with open(os.path.join(TELOS, "migrations", "035_edexcel_as_boundaries.sql"),
          "w", encoding="utf-8", newline="\n") as fh:
    fh.write(sql)
with open(os.path.join(SCRATCH, "edx_as_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(seeds))
with open(os.path.join(SCRATCH, "edx_as_entries.txt"), "w", encoding="utf-8") as fh:
    fh.write("".join(entries))
for n in NOTES:
    print("NOTE:", n)
print("migration 035 written with %d rows" % len(all_values))
