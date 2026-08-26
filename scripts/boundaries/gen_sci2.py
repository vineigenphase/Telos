"""Second boards for the sciences: AQA Physics (7408), OCR Biology A (H420)
and OCR Chemistry A (H432).

AQA Physics is the interesting one. AQA publishes Paper 3 as separate
components — Section A (45 marks, practical skills and data analysis) and five
Section B options of 35 marks each — rather than as one 80-mark paper. They are
modelled here the way AQA publishes them, because those are the boundaries that
exist: there is no 80-mark boundary to compare an 80-mark score against. It also
means a student can see whether they are losing marks on the practical analysis
or on their optional topic, which one combined figure would hide.

Module 1 in both OCR specs is practical skills. Only 1.1.1-1.1.4 are used as
topics; 1.2.1 and 1.2.2 are the Practical Endorsement, which is assessed
separately from the written papers and reported apart from the grade.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from aqa_extract import extract as aqa
from ocr_extract import extract as ocr

SCRATCH = DOCS
TELOS = REPO
YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]

# ── AQA Physics 7408 ────────────────────────────────────────────────────────
PHYS_CORE = ["Measurements and Their Errors", "Particles and Radiation", "Waves",
             "Mechanics and Materials", "Electricity", "Periodic Motion"]
PHYS_P2 = ["Thermal Physics", "Fields and Their Consequences", "Nuclear Physics"] + PHYS_CORE
PHYS_3A = ["Practical Skills", "Data Analysis and Uncertainties"]
PHYS_OPTS = {
    "3BA": ("Astrophysics", ["Telescopes", "Classification of Stars", "Cosmology"]),
    "3BB": ("Medical Physics", ["Physics of the Eye", "Physics of the Ear",
                                "Biological Measurement", "Non-ionising Imaging",
                                "X-ray Imaging", "Radionuclide Imaging and Therapy"]),
    "3BC": ("Engineering Physics", ["Rotational Dynamics", "Thermodynamics and Engines"]),
    "3BD": ("Turning Points in Physics", ["The Discovery of the Electron",
                                          "Wave-particle Duality", "Special Relativity"]),
    "3BE": ("Electronics", ["Discrete Semiconductor Devices",
                            "Analogue and Digital Signals", "Analogue Signal Processing",
                            "Operational Amplifiers", "Digital Signal Processing",
                            "Data Communication Systems"]),
}

# ── OCR module content ──────────────────────────────────────────────────────
BIO_M = {
    1: ["Planning", "Implementing", "Analysis", "Evaluation"],
    2: ["Cell Structure", "Biological Molecules", "Nucleotides and Nucleic Acids",
        "Enzymes", "Biological Membranes", "Cell Division, Diversity and Organisation"],
    3: ["Exchange Surfaces", "Transport in Animals", "Transport in Plants"],
    4: ["Communicable Diseases and Immunity", "Biodiversity", "Classification and Evolution"],
    5: ["Communication and Homeostasis", "Excretion", "Neuronal Communication",
        "Hormonal Communication", "Plant and Animal Responses", "Photosynthesis",
        "Respiration"],
    6: ["Cellular Control", "Patterns of Inheritance", "Manipulating Genomes",
        "Cloning and Biotechnology", "Ecosystems", "Populations and Sustainability"],
}
CHEM_M = {
    1: ["Planning", "Implementing", "Analysis", "Evaluation"],
    2: ["Atomic Structure and Isotopes", "Compounds, Formulae and Equations",
        "Amount of Substance", "Acids", "Redox", "Electron Structure",
        "Bonding and Structure"],
    3: ["Periodicity", "Group 2", "The Halogens", "Qualitative Analysis",
        "Enthalpy Changes", "Reaction Rates", "Chemical Equilibrium"],
    4: ["Basic Concepts of Organic Chemistry", "Alkanes", "Alkenes", "Alcohols",
        "Haloalkanes", "Organic Synthesis", "Analytical Techniques"],
    5: ["How Fast?", "How Far?", "Acids, Bases and Buffers", "Lattice Enthalpy",
        "Enthalpy and Entropy", "Redox and Electrode Potentials",
        "Transition Elements", "Qualitative Analysis II"],
    6: ["Aromatic Compounds", "Carbonyl Compounds", "Carboxylic Acids and Esters",
        "Amines", "Amino Acids, Amides and Chirality", "Polyesters and Polyamides",
        "Carbon-carbon Bond Formation", "Organic Synthesis II",
        "Chromatography and Qualitative Analysis", "Spectroscopy"],
}


def modules(mod, keys):
    out = []
    for k in keys:
        out.extend(mod[k])
    return out


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


def write_migration(num, subject, board, rows, note):
    values = ",\n".join(
        "    ('%s', '%s', '%s', '%s', 'June', %d, %d, %d, %d, %d, %d)"
        % (subject, board, p, y, a_s, a, b, c, d, e)
        for (p, y, a_s, a, b, c, d, e) in rows)
    slug = "%s_%s" % (board.split()[0].lower(), subject.lower())
    sql = (
        "-- 0%d_%s_boundaries.sql\n"
        "-- %s A-level %s, per paper.\n"
        "--\n"
        "-- %s\n"
        "--\n"
        "-- Each component is checked against its own expected max mark, so a paper\n"
        "-- measured against another paper's scale fails loudly instead of grading\n"
        "-- every student wrongly.\n"
        "--\n"
        "-- No 2020 or 2021: no summer exam series.\n"
        "--\n"
        "-- Idempotent.\n\n"
        "DELETE FROM grade_boundaries WHERE subject = '%s' AND board = '%s';\n\n"
        "INSERT INTO grade_boundaries\n"
        "    (subject, board, paper_code, year, series,\n"
        "     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)\n"
        "VALUES\n%s;\n"
    ) % (num, slug, board, subject, note, subject, board, values)
    with open(os.path.join(TELOS, "migrations", "0%d_%s_boundaries.sql" % (num, slug)),
              "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sql)
    return "\n".join(
        '    ("%s", "%s", "%s", "%s", "June", %d, %d, %d, %d),' % (subject, board, p, y, a_s, a, b, c)
        for (p, y, a_s, a, b, c, d, e) in rows)


seeds, entries = [], []

# ── AQA Physics ─────────────────────────────────────────────────────────────
exp = {"1": 85, "2": 85, "3A": 45, "3BA": 35, "3BB": 35, "3BC": 35, "3BD": 35, "3BE": 35}
data, probs = aqa("7408", exp, YEARS)
if probs:
    print("REFUSING AQA Physics:")
    for p in probs:
        print("  -", p)
    raise SystemExit(1)
rows = []
for (comp, year) in sorted(data, key=lambda k: (k[1], k[0])):
    mx, a_s, a, b, c, d, e = data[(comp, year)]
    assert a_s > a > b > c > d > e > 0, "%s %s" % (comp, year)
    rows.append(("Paper " + comp, year, a_s, a, b, c, d, e))
seeds.append(write_migration(
    27, "Physics", "AQA", rows,
    "AQA publishes Paper 3 as separate components: Section A (45, practical skills\n"
    "-- and data analysis) and five Section B options of 35 each. They are stored\n"
    "-- that way because those are the boundaries that exist — there is no 80-mark\n"
    "-- Paper 3 boundary to compare a combined score against."))
print("AQA Physics: %d rows" % len(rows))

opt_papers = "\n".join(
    '                {"code": "Paper %s", "name": "Paper 3B: %s", "max_marks": 35, "optional": True},'
    % (code, name) for code, (name, _t) in PHYS_OPTS.items())
opt_topics = "\n".join(
    '                "Paper %s": [\n%s],' % (code, fmt(tops))
    for code, (_n, tops) in PHYS_OPTS.items())

entries.append('''        "Physics": {
            "color": "#5E8B7E",
            "level": "A-Level",
            "choose_optional": 1,
            # 7408. Papers 1 and 2 plus Paper 3, which AQA publishes as two
            # separate components: a compulsory 45-mark practical section and
            # one 35-mark optional topic chosen from five. Modelled the way AQA
            # publishes it, because those are the boundaries that exist.
            "papers": [
                {"code": "Paper 1",  "name": "Sections 1-5 and Periodic Motion", "max_marks": 85},
                {"code": "Paper 2",  "name": "Thermal, Fields and Nuclear",      "max_marks": 85},
                {"code": "Paper 3A", "name": "Paper 3A: Practical and Data",     "max_marks": 45},
%s
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Paper 1 is sections 1-5 and 6.1; Paper 2 is 6.2, 7 and 8 with
            # sections 1-6.1 as assumed knowledge, so those are listed there too
            # — a Paper 2 question can be on mechanics, and a student needs
            # somewhere accurate to tag it.
            "topics": {
                "Paper 1": [
%s],
                "Paper 2": [
%s],
                "Paper 3A": [
%s],
%s
            },
        },
''' % (opt_papers, fmt(PHYS_CORE), fmt(PHYS_P2), fmt(PHYS_3A), opt_topics))

# ── OCR Biology A and Chemistry A ───────────────────────────────────────────
for subject, qual, heading, mod, colour, num in (
        ("Biology", "H420", "A Level Biology A", BIO_M, "#5E9E6B", 28),
        ("Chemistry", "H432", "A Level Chemistry A", CHEM_M, "#5E8B7E", 29)):
    d, pr = ocr(qual, heading, {"01": 100, "02": 100, "03": 70})
    if pr:
        print("REFUSING OCR " + subject + ":")
        for p in pr:
            print("  -", p)
        raise SystemExit(1)
    rows = []
    for (comp, year) in sorted(d, key=lambda k: (k[1], k[0])):
        mx, a_s, a, b, c, dd, e = d[(comp, year)]
        assert a_s > a > b > c > dd > e > 0, "%s %s" % (comp, year)
        rows.append(("Paper " + comp.lstrip("0"), year, a_s, a, b, c, dd, e))
    seeds.append(write_migration(
        num, subject, "OCR A", rows,
        "Three written papers. Component 01 assesses modules 1, 2, 3 and 5;\n"
        "-- component 02 assesses 1, 2, 4 and 6; component 03 assesses all six. The\n"
        "-- Practical Endorsement (component 04) is reported separately from the\n"
        "-- grade and is not a written paper, so it is not stored."))
    print("OCR %s: %d rows" % (subject, len(rows)))

    entries.append('''        "%s": {
            "color": "%s",
            "level": "A-Level",
            # %s. Three written papers; the Practical Endorsement is reported
            # separately from the grade and is not tracked.
            "papers": [
                {"code": "Paper 1", "name": "%s", "max_marks": 100},
                {"code": "Paper 2", "name": "%s", "max_marks": 100},
                {"code": "Paper 3", "name": "Unified %s", "max_marks": 70},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Module 1 is practical skills, assessed inside every written paper,
            # so its four planning-to-evaluation sections appear on all three.
            # Modules 1.2.1 and 1.2.2 are the Practical Endorsement and are left
            # out — they are not assessed by these papers.
            "topics": {
                "Paper 1": [
%s],
                "Paper 2": [
%s],
                "Paper 3": [
%s],
            },
        },
''' % (subject, colour, qual,
       "Biological processes" if subject == "Biology" else "Periodic Table and Physical",
       "Biological diversity" if subject == "Biology" else "Synthesis and Analysis",
       subject.lower(),
       fmt(modules(mod, [1, 2, 3, 5])),
       fmt(modules(mod, [1, 2, 4, 6])),
       fmt(modules(mod, [1, 2, 3, 4, 5, 6]))))

with open(os.path.join(SCRATCH, "sci2_seed.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n\n".join(seeds))
with open(os.path.join(SCRATCH, "sci2_entries.txt"), "w", encoding="utf-8") as fh:
    fh.write("".join(entries))
print("entries written")
