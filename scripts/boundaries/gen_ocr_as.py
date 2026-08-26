"""OCR AS-levels: Mathematics A (H230), Further Mathematics A (H235),
Physics A (H156), Chemistry A (H032), Biology A (H020).

AS is a qualification in its own right, not the first half of an A-level: it has
its own papers, its own boundaries, and no A* grade. So each gets its own
catalogue key, suffixed "(AS)", because `papers`, `grade_boundaries` and
`user_subjects` are all keyed by that string and an AS row must never be matched
against an A-level one.

a_star is stored NULL for every row here. That is the whole point — an AS
certificate has no A* on it, and prediction.py reads the absence to know the
grade ladder stops at A.

Only 2022-2025 are available: OCR published AS boundaries in a separate document
before 2022 and those files are not to hand. Stated rather than guessed at.

Topics are the AS subset of each specification, which is genuinely smaller than
the A-level content — an AS Chemistry student is not examined on transition
elements. Taking the A-level topic list would offer topics they never study.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from ocr_as_extract import extract

TELOS = REPO
SCRATCH = DOCS
YEARS = ["2019", "2022", "2023", "2024", "2025"]

PURE_AS = ["Proof", "Algebra and Functions", "Coordinate Geometry",
           "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
           "Differentiation", "Integration", "Vectors"]
STATS_AS = ["Statistical Sampling", "Data Presentation and Interpretation",
            "Probability", "Statistical Distributions",
            "Statistical Hypothesis Testing"]
MECH_AS = ["Quantities and Units in Mechanics", "Kinematics",
           "Forces and Newton's Laws"]

PRACTICAL = ["Planning", "Implementing", "Analysis", "Evaluation"]
PHYS_AS = PRACTICAL + [
    "Physical Quantities and Units", "Making Measurements and Analysing Data",
    "Motion", "Forces in Action", "Work, Energy and Power", "Materials",
    "Laws of Motion and Momentum", "Charge and Current",
    "Energy, Power and Resistance", "Electrical Circuits", "Waves",
    "Quantum Physics"]
CHEM_AS = PRACTICAL + [
    "Atomic Structure and Isotopes", "Compounds, Formulae and Equations",
    "Amount of Substance", "Acids", "Redox", "Electron Structure",
    "Bonding and Structure", "Periodicity", "Group 2", "The Halogens",
    "Qualitative Analysis", "Enthalpy Changes", "Reaction Rates",
    "Chemical Equilibrium", "Basic Concepts of Organic Chemistry", "Alkanes",
    "Alkenes", "Alcohols", "Haloalkanes", "Organic Synthesis", "Spectroscopy"]
BIO_AS = PRACTICAL + [
    "Cell Structure", "Biological Molecules", "Nucleotides and Nucleic Acids",
    "Enzymes", "Biological Membranes",
    "Cell Division, Diversity and Organisation", "Exchange Surfaces",
    "Transport in Animals", "Transport in Plants",
    "Communicable Diseases and the Immune System", "Biodiversity",
    "Classification and Evolution"]

# (key, display name, colour, heading, expected max, papers, topics)
SPECS = [
    ("Maths (AS)", "Maths", "#C9A227", "AS GCE Mathematics A",
     {"H230 01": 75, "H230 02": 75},
     [("Paper 1", "Pure Mathematics and Statistics", 75, "H230 01"),
      ("Paper 2", "Pure Mathematics and Mechanics", 75, "H230 02")],
     {"Paper 1": PURE_AS + STATS_AS, "Paper 2": PURE_AS + MECH_AS}),

    ("Further Maths (AS)", "Further Maths", "#C9A227",
     "AS GCE Further Mathematics A",
     {"Y531": 60, "Y532": 60, "Y533": 60, "Y534": 60, "Y535": 60},
     [("Y531", "Pure Core", 60, "Y531"),
      ("Y532", "Statistics", 60, "Y532", True),
      ("Y533", "Mechanics", 60, "Y533", True),
      ("Y534", "Discrete Mathematics", 60, "Y534", True),
      ("Y535", "Additional Pure Maths", 60, "Y535", True)],
     {"Y531": ["Matrices", "Complex Numbers", "Vectors", "Algebra", "Series",
               "Roots of Polynomials", "Proof by Induction"],
      "Y532": ["Discrete Random Variables", "Bivariate Data",
               "Chi-squared Tests", "Non-parametric Tests"],
      "Y533": ["Dimensional Analysis", "Work, Energy and Power",
               "Impulse and Momentum", "Centre of Mass"],
      "Y534": ["Mathematical Preliminaries", "Graphs and Networks",
               "Network Algorithms", "Critical Path Analysis",
               "Linear Programming"],
      "Y535": ["Sequences and Series", "Number Theory", "Groups",
               "Vectors and Surfaces", "Curves"]}),

    ("Physics (AS)", "Physics", "#5E8B7E", "AS GCE Physics A",
     {"H156 01": 70, "H156 02": 70},
     [("Paper 1", "Breadth in Physics", 70, "H156 01"),
      ("Paper 2", "Depth in Physics", 70, "H156 02")],
     {"Paper 1": PHYS_AS, "Paper 2": PHYS_AS}),

    ("Chemistry (AS)", "Chemistry", "#5E8B7E", "AS GCE Chemistry A",
     {"H032 01": 70, "H032 02": 70},
     [("Paper 1", "Breadth in Chemistry", 70, "H032 01"),
      ("Paper 2", "Depth in Chemistry", 70, "H032 02")],
     {"Paper 1": CHEM_AS, "Paper 2": CHEM_AS}),

    ("Biology (AS)", "Biology", "#5E9E6B", "AS GCE Biology A",
     {"H020 01": 70, "H020 02": 70},
     [("Paper 1", "Breadth in Biology", 70, "H020 01"),
      ("Paper 2", "Depth in Biology", 70, "H020 02")],
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
for key, name, colour, heading, expect, papers, topics in SPECS:
    data, probs = extract(heading, expect, YEARS)
    if probs:
        print("REFUSING " + key + ":")
        for p in probs:
            print("  -", p)
        raise SystemExit(1)

    rows = []
    for p in papers:
        code, _pname, mx, comp = p[0], p[1], p[2], p[3]
        for year in YEARS:
            got = data.get((comp, year))
            assert got is not None, "%s %s %s" % (key, comp, year)
            m, a, b, c, d, e = got
            assert m == mx, "%s %s %s max %s" % (key, comp, year, m)
            assert a > b > c > d > e > 0, "%s %s %s" % (key, comp, year)
            rows.append((code, year, a, b, c, d, e))
    rows.sort(key=lambda r: (r[1], r[0]))

    for code, year, a, b, c, d, e in rows:
        all_values.append(
            "    ('%s', 'OCR A', '%s', '%s', 'June', NULL, %d, %d, %d, %d, %d)"
            % (key, code, year, a, b, c, d, e))
        seeds.append('    ("%s", "OCR A", "%s", "%s", "June", None, %d, %d, %d),'
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
    entry += ('            # %s. A qualification in its own right, graded A-E\n'
              '            # with no A*.\n' % heading.replace("AS GCE ", ""))
    entry += '            "papers": [\n%s\n            ],\n' % paper_lines
    if choose:
        entry += '            "choose_optional": %d,\n' % choose
    entry += ('            # OCR published AS boundaries in a separate document\n'
              '            # before 2022; those series are not stored.\n')
    entry += '            "years": ["SPEC", "2022", "2023", "2024", "2025"],\n'
    entry += '            "topics": {\n%s\n            },\n' % topic_lines
    entry += '        },\n'
    entries.append(entry)

sql = (
    "-- 034_ocr_as_boundaries.sql\n"
    "-- OCR AS-levels: Mathematics A (H230), Further Mathematics A (H235),\n"
    "-- Physics A (H156), Chemistry A (H032), Biology A (H020).\n"
    "--\n"
    "-- a_star is NULL on every row, and that is the point: an AS-level is\n"
    "-- graded A-E and has no A*. prediction.py reads the absence and stops the\n"
    "-- grade ladder at A, so an AS student cannot be predicted a grade their\n"
    "-- certificate has no room for.\n"
    "--\n"
    "-- AS components are stored under their own subject keys, suffixed (AS).\n"
    "-- The AS and A-level papers of one subject share neither content nor\n"
    "-- boundaries, and papers, grade_boundaries and user_subjects are all keyed\n"
    "-- by subject, so the two must not collide.\n"
    "--\n"
    "-- Read from the AS section of each series document, which is a separate\n"
    "-- table with six grade columns rather than seven. A parser that tried to\n"
    "-- read both would, on a bad match, store an A boundary in the A* column.\n"
    "-- Every row is checked against its component's own max mark.\n"
    "--\n"
    "-- Only 2022-2025: OCR published AS boundaries separately before that and\n"
    "-- those documents are not to hand. No 2020 or 2021 - no summer series.\n"
    "--\n"
    "-- Idempotent.\n\n"
    "DELETE FROM grade_boundaries WHERE board = 'OCR A' AND subject LIKE '%% (AS)';\n\n"
    "INSERT INTO grade_boundaries\n"
    "    (subject, board, paper_code, year, series,\n"
    "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
    "VALUES\n%s;\n"
) % (",\n".join(all_values))

with open(os.path.join(TELOS, "migrations", "034_ocr_as_boundaries.sql"),
          "w", encoding="utf-8", newline="\n") as fh:
    fh.write(sql)
with open(os.path.join(SCRATCH, "ocr_as_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(seeds))
with open(os.path.join(SCRATCH, "ocr_as_entries.txt"), "w", encoding="utf-8") as fh:
    fh.write("".join(entries))
print("migration 034 written with %d rows" % len(all_values))
