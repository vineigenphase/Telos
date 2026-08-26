"""Catalogue entries and migrations for AQA Chemistry (7405) and Biology (7402).

Topic labels are the specification's own section headings, shortened where AQA
writes them as sentences rather than titles ("Homeostasis is the maintenance of
a stable internal environment" becomes "Homeostasis"). The section numbers are
kept here so any label can be traced back to the spec.
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

BIO = {
    "3.1.1": "Monomers and Polymers", "3.1.2": "Carbohydrates", "3.1.3": "Lipids",
    "3.1.4": "Proteins", "3.1.5": "Nucleic Acids", "3.1.6": "ATP",
    "3.1.7": "Water", "3.1.8": "Inorganic Ions",
    "3.2.1": "Cell Structure", "3.2.2": "Cell Division",
    "3.2.3": "Transport Across Cell Membranes",
    "3.2.4": "Cell Recognition and the Immune System",
    "3.3.1": "Surface Area to Volume Ratio", "3.3.2": "Gas Exchange",
    "3.3.3": "Digestion and Absorption", "3.3.4": "Mass Transport",
    "3.4.1": "DNA, Genes and Chromosomes", "3.4.2": "DNA and Protein Synthesis",
    "3.4.3": "Genetic Diversity and Meiosis", "3.4.4": "Genetic Diversity and Adaptation",
    "3.4.5": "Species and Taxonomy", "3.4.6": "Biodiversity Within a Community",
    "3.4.7": "Investigating Diversity",
    "3.5.1": "Photosynthesis", "3.5.2": "Respiration",
    "3.5.3": "Energy and Ecosystems", "3.5.4": "Nutrient Cycles",
    "3.6.1": "Stimuli and Responses", "3.6.2": "Nervous Coordination",
    "3.6.3": "Skeletal Muscles", "3.6.4": "Homeostasis",
    "3.7.1": "Inheritance", "3.7.2": "Populations",
    "3.7.3": "Evolution and Speciation", "3.7.4": "Populations in Ecosystems",
    "3.8.1": "Mutations", "3.8.2": "Control of Gene Expression",
    "3.8.3": "Using Genome Projects", "3.8.4": "Gene Technologies",
}
BIO_P1 = [v for k, v in BIO.items() if k[:3] in ("3.1", "3.2", "3.3", "3.4")]
BIO_P2 = [v for k, v in BIO.items() if k[:3] in ("3.5", "3.6", "3.7", "3.8")]
BIO_P3 = list(BIO.values())

CHEM = {
    "3.1.1": "Atomic Structure", "3.1.2": "Amount of Substance", "3.1.3": "Bonding",
    "3.1.4": "Energetics", "3.1.5": "Kinetics",
    "3.1.6": "Chemical Equilibria and Kc", "3.1.7": "Oxidation, Reduction and Redox",
    "3.1.8": "Thermodynamics", "3.1.9": "Rate Equations",
    "3.1.10": "Equilibrium Constant Kp",
    "3.1.11": "Electrode Potentials and Electrochemical Cells",
    "3.1.12": "Acids and Bases",
    "3.2.1": "Periodicity", "3.2.2": "Group 2, the Alkaline Earth Metals",
    "3.2.3": "Group 7, the Halogens", "3.2.4": "Period 3 Elements and Their Oxides",
    "3.2.5": "Transition Metals", "3.2.6": "Reactions of Ions in Aqueous Solution",
    "3.3.1": "Introduction to Organic Chemistry", "3.3.2": "Alkanes",
    "3.3.3": "Halogenoalkanes", "3.3.4": "Alkenes", "3.3.5": "Alcohols",
    "3.3.6": "Organic Analysis", "3.3.7": "Optical Isomerism",
    "3.3.8": "Aldehydes and Ketones", "3.3.9": "Carboxylic Acids and Derivatives",
    "3.3.10": "Aromatic Chemistry", "3.3.11": "Amines", "3.3.12": "Polymers",
    "3.3.13": "Amino Acids, Proteins and DNA", "3.3.14": "Organic Synthesis",
    "3.3.15": "NMR Spectroscopy", "3.3.16": "Chromatography",
}
P1_PHYS = ["3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.1.6", "3.1.7", "3.1.8",
           "3.1.10", "3.1.11", "3.1.12"]
P2_PHYS = ["3.1.2", "3.1.3", "3.1.4", "3.1.5", "3.1.6", "3.1.9"]
CHEM_P1 = [CHEM[k] for k in P1_PHYS] + [v for k, v in CHEM.items() if k[:3] == "3.2"]
CHEM_P2 = [CHEM[k] for k in P2_PHYS] + [v for k, v in CHEM.items() if k[:3] == "3.3"]
CHEM_P3 = list(CHEM.values())

print("Biology   P1=%d P2=%d P3=%d" % (len(BIO_P1), len(BIO_P2), len(BIO_P3)))
print("Chemistry P1=%d P2=%d P3=%d" % (len(CHEM_P1), len(CHEM_P2), len(CHEM_P3)))

YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]
SPECS = [("Chemistry", "7405", {"1": 105, "2": 105, "3": 90}, 300, 19),
         ("Biology", "7402", {"1": 91, "2": 91, "3": 78}, 260, 20)]

seed_blocks = []
for subject, qual, expect, total, num in SPECS:
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

    maxes = ", ".join("Paper %s (%d)" % (k, v) for k, v in expect.items())
    smallest = min(expect.values())
    largest = max(expect.values())

    sql = (
        "-- 0%d_aqa_%s_boundaries.sql\n"
        "-- AQA A-level %s (%s), per paper: %s.\n"
        "--\n"
        "-- The three papers have different max marks, which is the detail that\n"
        "-- matters here: a %d-mark paper measured against a %d-mark boundary would\n"
        "-- grade every student a U. The extractor checks each component against its\n"
        "-- own expected max rather than assuming a qualification's papers share one.\n"
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
    ) % (num, subject.lower(), subject, qual, maxes, smallest, largest, total,
         subject, values)

    out = os.path.join(TELOS, "migrations", "0%d_aqa_%s_boundaries.sql" % (num, subject.lower()))
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sql)

    seed_blocks.append("\n".join(
        '    ("%s", "AQA", "%s", "%s", "June", %d, %d, %d, %d),' % (subject, p, y, a_s, a, b, c)
        for (p, y, a_s, a, b, c, d, e) in rows))
    print("  %s: migration 0%d with %d rows" % (subject, num, len(rows)))

with open(os.path.join(SCRATCH, "sci_seed.txt"), "w", encoding="utf-8") as fh:
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


entries = '''        "Biology": {
            "color": "#5E9E6B",
            "level": "A-Level",
            # 7402. Three compulsory papers with different mark totals.
            "papers": [
                {"code": "Paper 1", "name": "Topics 1-4",  "max_marks": 91},
                {"code": "Paper 2", "name": "Topics 5-8",  "max_marks": 91},
                {"code": "Paper 3", "name": "Any content", "max_marks": 78},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Specification sections 3.1-3.8. Paper 1 covers topics 1-4, Paper 2
            # covers 5-8, and Paper 3 covers everything — which is why its list
            # is long. A shorter one would leave a student unable to tag half
            # the questions on the paper they actually sat.
            "topics": {
                "Paper 1": [
__BIO_P1__],
                "Paper 2": [
__BIO_P2__],
                "Paper 3": [
__BIO_P3__],
            },
        },
        "Chemistry": {
            "color": "#5E8B7E",
            "level": "A-Level",
            # 7405. Three compulsory papers; Paper 3 is shorter than the others.
            "papers": [
                {"code": "Paper 1", "name": "Inorganic and Physical", "max_marks": 105},
                {"code": "Paper 2", "name": "Organic and Physical",   "max_marks": 105},
                {"code": "Paper 3", "name": "Any content",            "max_marks": 90},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Paper 1 takes physical 3.1.1-3.1.4, 3.1.6-3.1.8 and 3.1.10-3.1.12
            # with all of inorganic; Paper 2 takes physical 3.1.2-3.1.6 and
            # 3.1.9 with all of organic. Kinetics and rate equations sit on
            # Paper 2 only, thermodynamics on Paper 1 only — the physical
            # content is genuinely split between them, not shared.
            "topics": {
                "Paper 1": [
__CHEM_P1__],
                "Paper 2": [
__CHEM_P2__],
                "Paper 3": [
__CHEM_P3__],
            },
        },
'''
for key, items in (("__BIO_P1__", BIO_P1), ("__BIO_P2__", BIO_P2), ("__BIO_P3__", BIO_P3),
                   ("__CHEM_P1__", CHEM_P1), ("__CHEM_P2__", CHEM_P2), ("__CHEM_P3__", CHEM_P3)):
    entries = entries.replace(key, fmt(items))

with open(os.path.join(SCRATCH, "sci_entries.txt"), "w", encoding="utf-8") as fh:
    fh.write(entries)
print("catalogue entries written")
