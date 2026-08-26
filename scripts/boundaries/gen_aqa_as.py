"""AQA AS-levels: Mathematics (7356), Further Mathematics (7366),
Physics (7407), Chemistry (7404), Biology (7401), Geography (7036),
Economics (7135), French (7651), German (7661), Spanish (7691).

There is no AS Philosophy: AQA does not award one, so the catalogue does not
offer one. An honest gap, not an oversight.

Same rules as the OCR and Edexcel AS loads: a catalogue key suffixed "(AS)",
a_star NULL on every row, every component checked against its own max mark.

The topics are the AS subset of each specification, and the subsets are real —
AS Biology is Topics 1-4 of eight, AS Chemistry stops before thermodynamics and
transition metals, AS Economics has no synoptic third paper. Carrying the
A-level topic list across would offer a student topics they never study.

The AS papers are also NOT the A-level papers at a smaller mark total. AS Maths
Paper 1 is Pure and Mechanics where the A-level Paper 1 is Pure alone, and the
MFL AS writing paper is 50 marks against the A-level's 80. Each is read from
the specification.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from aqa_as_extract import extract

TELOS = REPO
SCRATCH = DOCS
YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]

PURE_AS = ["Proof", "Algebra and Functions", "Coordinate Geometry",
           "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
           "Differentiation", "Integration", "Vectors"]
MECH_AS = ["Quantities and Units in Mechanics", "Kinematics",
           "Forces and Newton's Laws"]
STATS_AS = ["Statistical Sampling", "Data Presentation and Interpretation",
            "Probability", "Statistical Distributions",
            "Statistical Hypothesis Testing"]

PHYS_AS = ["Measurements and Their Errors", "Particles and Radiation", "Waves",
           "Mechanics and Materials", "Electricity"]
CHEM_INORG_AS = ["Atomic Structure", "Amount of Substance", "Bonding",
                 "Energetics", "Chemical Equilibria and Kc",
                 "Oxidation, Reduction and Redox", "Periodicity",
                 "Group 2, the Alkaline Earth Metals", "Group 7, the Halogens"]
CHEM_ORG_AS = ["Amount of Substance", "Bonding", "Energetics", "Kinetics",
               "Chemical Equilibria and Kc", "Introduction to Organic Chemistry",
               "Alkanes", "Halogenoalkanes", "Alkenes", "Alcohols",
               "Organic Analysis"]
BIO_AS = ["Monomers and Polymers", "Carbohydrates", "Lipids", "Proteins",
          "Nucleic Acids", "ATP", "Water", "Inorganic Ions", "Cell Structure",
          "Cell Division", "Transport Across Cell Membranes",
          "Cell Recognition and the Immune System",
          "Surface Area to Volume Ratio", "Gas Exchange",
          "Digestion and Absorption", "Mass Transport",
          "DNA, Genes and Chromosomes", "DNA and Protein Synthesis",
          "Genetic Diversity and Meiosis", "Genetic Diversity and Adaptation",
          "Species and Taxonomy", "Biodiversity Within a Community",
          "Investigating Diversity"]
GEOG_PHYS_AS = ["Water and Carbon Cycles", "Hot Desert Systems and Landscapes",
                "Coastal Systems and Landscapes", "Glacial Systems and Landscapes"]
GEOG_HUM_AS = ["Changing Places", "Contemporary Urban Environments"]
ECON_MICRO_AS = ["Economic Methodology and the Economic Problem",
                 "Individual Economic Decision Making",
                 "Price Determination in a Competitive Market",
                 "Production, Costs and Revenue",
                 "Competitive and Concentrated Markets", "The Labour Market",
                 "Market Mechanism, Market Failure and Government Intervention"]
ECON_MACRO_AS = ["Measurement of Macroeconomic Performance",
                 "How the Macroeconomy Works", "Economic Performance",
                 "Macroeconomic Policy", "The International Economy"]

MFL_P1 = ["Aspects of Society: Current Trends", "Artistic Culture",
          "Translation into English", "Translation into the Target Language"]
MFL_P2 = ["Literary Text Essay", "Film Essay"]
MFL_P3 = ["Theme Discussion", "Stimulus Card Discussion"]

# (key, name, colour, qual code, expected max, papers, topics)
SPECS = [
    ("Maths (AS)", "Maths", "#C9A227", "7356", {"1": 80, "2": 80},
     [("Paper 1", "Pure Mathematics and Mechanics", 80, "1"),
      ("Paper 2", "Pure Mathematics and Statistics", 80, "2")],
     {"Paper 1": PURE_AS + MECH_AS, "Paper 2": PURE_AS + STATS_AS}, 0),

    ("Further Maths (AS)", "Further Maths", "#C9A227", "7366",
     {"1": 80, "2D": 40, "2M": 40, "2S": 40},
     [("Paper 1", "Compulsory Pure Content", 80, "1"),
      ("Paper 2D", "Discrete", 40, "2D", True),
      ("Paper 2M", "Mechanics", 40, "2M", True),
      ("Paper 2S", "Statistics", 40, "2S", True)],
     {"Paper 1": ["Complex Numbers", "Matrices", "Further Algebra and Functions",
                  "Further Calculus", "Further Vectors", "Proof by Induction"],
      "Paper 2D": ["Graphs and Networks", "Network Flows", "Linear Programming",
                   "Critical Path Analysis", "Game Theory"],
      "Paper 2M": ["Dimensional Analysis", "Momentum and Collisions",
                   "Work, Energy and Power", "Circular Motion"],
      "Paper 2S": ["Discrete Random Variables", "Poisson Distribution",
                   "Contingency Tables", "Hypothesis Testing"]}, 2),

    ("Physics (AS)", "Physics", "#5E8B7E", "7407", {"1": 70, "2": 70},
     [("Paper 1", "Sections 1-5", 70, "1"),
      ("Paper 2", "Sections 1-5 and Practical Skills", 70, "2")],
     {"Paper 1": PHYS_AS,
      "Paper 2": PHYS_AS + ["Practical Skills", "Data Analysis and Uncertainties"]}, 0),

    ("Chemistry (AS)", "Chemistry", "#5E8B7E", "7404", {"1": 80, "2": 80},
     [("Paper 1", "Inorganic and Physical Chemistry", 80, "1"),
      ("Paper 2", "Organic and Physical Chemistry", 80, "2")],
     {"Paper 1": CHEM_INORG_AS, "Paper 2": CHEM_ORG_AS}, 0),

    ("Biology (AS)", "Biology", "#5E9E6B", "7401", {"1": 75, "2": 75},
     [("Paper 1", "Topics 1-4", 75, "1"),
      ("Paper 2", "Topics 1-4 and Practical Skills", 75, "2")],
     {"Paper 1": BIO_AS,
      "Paper 2": BIO_AS + ["Practical Skills"]}, 0),

    ("Geography (AS)", "Geography", "#6E8F5E", "7036", {"1": 80, "2": 80},
     [("Paper 1", "Physical Geography and People and the Environment", 80, "1"),
      ("Paper 2", "Human Geography and Geography Fieldwork Investigation", 80, "2")],
     {"Paper 1": GEOG_PHYS_AS,
      "Paper 2": GEOG_HUM_AS + ["Fieldwork Investigation"]}, 0),

    ("Economics (AS)", "Economics", "#C08A3E", "7135", {"1": 70, "2": 70},
     [("Paper 1", "The Operation of Markets and Market Failure", 70, "1"),
      ("Paper 2", "The National Economy in a Global Context", 70, "2")],
     {"Paper 1": ECON_MICRO_AS, "Paper 2": ECON_MACRO_AS}, 0),

    ("French (AS)", "French", "#4C7EF3", "7651", {"1": 90, "2": 50, "3T": 60},
     [("Paper 1", "Listening, Reading and Writing", 90, "1"),
      ("Paper 2", "Writing", 50, "2"),
      ("Paper 3", "Speaking", 60, "3T", False, "oral")],
     {"Paper 1": MFL_P1, "Paper 2": MFL_P2, "Paper 3": MFL_P3}, 0),

    ("German (AS)", "German", "#C08A3E", "7661", {"1": 90, "2": 50, "3T": 60},
     [("Paper 1", "Listening, Reading and Writing", 90, "1"),
      ("Paper 2", "Writing", 50, "2"),
      ("Paper 3", "Speaking", 60, "3T", False, "oral")],
     {"Paper 1": MFL_P1, "Paper 2": MFL_P2, "Paper 3": MFL_P3}, 0),

    ("Spanish (AS)", "Spanish", "#D06A5A", "7691", {"1": 90, "2": 50, "3T": 60},
     [("Paper 1", "Listening, Reading and Writing", 90, "1"),
      ("Paper 2", "Writing", 50, "2"),
      ("Paper 3", "Speaking", 60, "3T", False, "oral")],
     {"Paper 1": MFL_P1, "Paper 2": MFL_P2, "Paper 3": MFL_P3}, 0),
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
for key, name, colour, qual, expect, papers, topics, choose in SPECS:
    data, probs = extract(qual, expect, YEARS)
    if probs:
        print("REFUSING " + key + ":")
        for p in probs:
            print("  -", p)
        raise SystemExit(1)

    rows = []
    for p in papers:
        code, mx, comp = p[0], p[2], p[3]
        for year in YEARS:
            got = data[(comp, year)]
            m, a, b, c, d, e = got
            assert m == mx, "%s %s %s max %s" % (key, comp, year, m)
            assert a > b > c > d > e > 0, "%s %s %s" % (key, comp, year)
            rows.append((code, year, a, b, c, d, e))
    rows.sort(key=lambda r: (r[1], r[0]))

    for code, year, a, b, c, d, e in rows:
        all_values.append(
            "    ('%s', 'AQA', '%s', '%s', 'June', NULL, %d, %d, %d, %d, %d)"
            % (key, code, year, a, b, c, d, e))
        seeds.append('    ("%s", "AQA", "%s", "%s", "June", None, %d, %d, %d),'
                     % (key, code, year, a, b, c))
    print("%s: %d rows" % (key, len(rows)))

    paper_lines = []
    for p in papers:
        extra = ""
        if len(p) > 4 and p[4]:
            extra += ', "optional": True'
        if len(p) > 5:
            extra += ', "assessment": "%s"' % p[5]
        paper_lines.append(
            '                {"code": "%s", "name": "%s", "max_marks": %d%s},'
            % (p[0], p[1], p[2], extra))
    topic_lines = "\n".join(
        '                "%s": [\n%s],' % (code, fmt(tl))
        for code, tl in topics.items())

    entry = '        "%s": {\n' % key
    entry += '            "name": "%s",\n' % name
    entry += '            "color": "%s",\n' % colour
    entry += '            "level": "AS-Level",\n'
    entry += ('            # %s. A qualification in its own right, graded A-E\n'
              '            # with no A*.\n' % qual)
    entry += '            "papers": [\n%s\n            ],\n' % "\n".join(paper_lines)
    if choose:
        entry += '            "choose_optional": %d,\n' % choose
    entry += '            "years": ["SPEC", "2022", "2023", "2024", "2025"],\n'
    entry += '            "topics": {\n%s\n            },\n' % topic_lines
    entry += '        },\n'
    entries.append(entry)

sql = (
    "-- 036_aqa_as_boundaries.sql\n"
    "-- AQA AS-levels: Mathematics (7356), Further Mathematics (7366),\n"
    "-- Physics (7407), Chemistry (7404), Biology (7401), Geography (7036),\n"
    "-- Economics (7135), French (7651), German (7661), Spanish (7691).\n"
    "--\n"
    "-- There is no AS Philosophy. AQA does not award one, so none is offered.\n"
    "--\n"
    "-- a_star is NULL on every row: an AS-level is graded A-E. prediction.py\n"
    "-- reads the absence and stops the grade ladder at A.\n"
    "--\n"
    "-- Read from AQA's separate AS boundary documents, which are not the same\n"
    "-- files as the A-level ones - the A-level documents contain no AS tables\n"
    "-- at all. An AS row carries six numbers (max, then A B C D E) where an\n"
    "-- A-level row carries seven, so it is parsed by its own reader rather\n"
    "-- than risking an A boundary being stored in the A* column.\n"
    "--\n"
    "-- The bare subject rows (7356 MATHEMATICS AS 160 ...) are the award across\n"
    "-- every paper and are never matched: they carry no slash. Storing one as\n"
    "-- if it were a paper is the fault that made Physics predict U on an 85%%.\n"
    "--\n"
    "-- Speaking is stored from the teacher-conducted variant; 3T and 3V agree\n"
    "-- in every series checked.\n"
    "--\n"
    "-- Only 2022-2025: AQA's AS documents before that are not to hand.\n"
    "--\n"
    "-- Idempotent.\n\n"
    "DELETE FROM grade_boundaries WHERE board = 'AQA' AND subject LIKE '%% (AS)';\n\n"
    "INSERT INTO grade_boundaries\n"
    "    (subject, board, paper_code, year, series,\n"
    "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
    "VALUES\n%s;\n"
) % (",\n".join(all_values))

with open(os.path.join(TELOS, "migrations", "036_aqa_as_boundaries.sql"),
          "w", encoding="utf-8", newline="\n") as fh:
    fh.write(sql)
with open(os.path.join(SCRATCH, "aqa_as_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(seeds))
with open(os.path.join(SCRATCH, "aqa_as_entries.txt"), "w", encoding="utf-8") as fh:
    fh.write("".join(entries))
print("migration 036 written with %d rows" % len(all_values))
