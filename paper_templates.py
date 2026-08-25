TEMPLATES = {
    "Edexcel": {
        "Further Maths": {
            "color": "#7A7973",
            "level": "A-Level",
            "papers": [
                {"code": "CP1", "name": "Core Pure 1",          "max_marks": 75},
                {"code": "CP2", "name": "Core Pure 2",          "max_marks": 75},
                {"code": "FM1", "name": "Further Mechanics 1",  "max_marks": 75},
                {"code": "FS1", "name": "Further Statistics 1", "max_marks": 75},
            ],
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            "topics": {
                "CP1": ["Complex Numbers", "Argand Diagram", "Modulus-Argument", "Roots of Polynomials",
                        "Series (Sigma Notation)", "Matrices", "Linear Transformations", "Proof by Induction"],
                "CP2": ["Complex Numbers II", "De Moivre's Theorem", "Series & Limits",
                        "Hyperbolic Functions", "Polar Coordinates", "Methods in Calculus",
                        "Volumes of Revolution", "Differential Equations", "Maclaurin/Taylor"],
                "FM1": ["Momentum & Impulse", "Elastic Strings & Springs", "Elastic Collisions",
                        "SHM", "Circular Motion", "Dimensional Analysis"],
                "FS1": ["Discrete Distributions", "Poisson Distribution", "CLT",
                        "Hypothesis Testing", "Chi-Squared Tests", "PGFs", "Correlation & Regression"],
            },
        },
        "Maths": {
            "color": "#C9A227",
            "level": "A-Level",
            "papers": [
                {"code": "Pure 1",      "name": "Pure Mathematics 1",    "max_marks": 100},
                {"code": "Pure 2",      "name": "Pure Mathematics 2",    "max_marks": 100},
                {"code": "Stats&Mech",  "name": "Statistics & Mechanics","max_marks": 100},
            ],
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            "topics": {
                "Pure 1": ["Proof", "Algebra & Functions", "Coordinate Geometry", "Circles",
                           "Binomial Expansion", "Trigonometry", "Differentiation", "Integration",
                           "Exponentials & Logarithms", "Vectors"],
                "Pure 2": ["Algebraic Methods", "Functions", "Sequences & Series",
                           "Binomial Expansion II", "Radians", "Trig Functions & Modelling",
                           "Parametric Equations", "Differentiation Methods",
                           "Integration Methods", "Numerical Methods"],
                "Stats&Mech": ["Statistical Sampling", "Data Presentation", "Probability",
                               "Binomial Distribution", "Normal Distribution", "Hypothesis Testing",
                               "Kinematics", "Forces & Newton's Laws", "Work Energy Power",
                               "Moments", "Projectiles", "Variable Acceleration"],
            },
        },
    },
    "OCR A": {
        "Physics": {
            "color": "#5E8B7E",
            "level": "A-Level",
            "papers": [
                {"code": "Paper 1", "name": "Breadth in Physics", "max_marks": 100},
                {"code": "Paper 2", "name": "Depth in Physics",   "max_marks": 100},
                {"code": "Paper 3", "name": "Unified Physics",    "max_marks": 70},
            ],
            "years": ["SPEC", "2017", "2018", "2019", "2020", "2021",
                      "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": ["Measurements & Errors", "Scalars & Vectors", "Equations of Motion",
                            "Newton's Laws", "Work, Energy & Power", "Materials",
                            "Waves", "Optics", "Current & Charge", "Electrical Circuits", "Semiconductors"],
                "Paper 2": ["Projectiles", "Momentum", "Circular Motion", "Oscillations",
                            "Gravitational Fields", "Electric Fields", "Magnetic Fields",
                            "Electromagnetic Induction", "Capacitors", "Nuclear Physics",
                            "Radioactivity", "Thermal Physics"],
                "Paper 3": ["Experimental Design", "Uncertainty & Error Analysis",
                            "Data Analysis", "Practical Skills", "Cross-topic Synthesis"],
            },
        },
    },
}


def get_paper_info(board, subject, code):
    try:
        for p in TEMPLATES[board][subject]["papers"]:
            if p["code"] == code:
                return p
    except KeyError:
        pass
    return None


def get_topics(board, subject, code):
    try:
        return TEMPLATES[board][subject]["topics"].get(code, [])
    except KeyError:
        return []


def all_combos():
    """Return flat list of (board, subject, paper_dict) for API."""
    out = []
    for board, subjects in TEMPLATES.items():
        for subject, data in subjects.items():
            for p in data["papers"]:
                out.append({"board": board, "subject": subject, **p,
                            "color": data["color"],
                            "years": data["years"]})
    return out


# ── Qualification levels ─────────────────────────────────────────────────────
# The levels Telos can support. A level only appears to students once there is
# at least one qualification in the catalogue offering it — an empty option is
# a promise the app cannot keep, so LEVELS is the vocabulary and
# available_levels() is what the picker actually shows.
LEVELS = [
    "A-Level",
    "AS-Level",
    "Advanced Higher",
    "Higher",
]

DEFAULT_LEVEL = "A-Level"


def qualification_level(board, subject):
    """The level of one catalogue entry, defaulting to A-Level."""
    try:
        return TEMPLATES[board][subject].get("level", DEFAULT_LEVEL)
    except KeyError:
        return DEFAULT_LEVEL


def all_qualifications():
    """Every (board, subject, level) the catalogue offers, with its papers.

    The unit a student picks in onboarding. Sorted by subject so the picker
    groups the way a person thinks — "Physics, whose board?" rather than
    "OCR A, which subjects?".
    """
    out = []
    for board, subjects in TEMPLATES.items():
        for subject, data in subjects.items():
            out.append({
                "board": board,
                "subject": subject,
                "level": data.get("level", DEFAULT_LEVEL),
                "color": data["color"],
                "papers": data["papers"],
                "paper_count": len(data["papers"]),
                "years": data["years"],
            })
    return sorted(out, key=lambda q: (q["subject"], q["level"], q["board"]))


def available_levels():
    """Levels with at least one qualification behind them, in LEVELS order."""
    present = {q["level"] for q in all_qualifications()}
    return [lvl for lvl in LEVELS if lvl in present]


def available_subjects(level=None):
    """Subject names on offer, optionally for one level."""
    qs = all_qualifications()
    if level:
        qs = [q for q in qs if q["level"] == level]
    seen, out = set(), []
    for q in qs:
        if q["subject"] not in seen:
            seen.add(q["subject"])
            out.append(q["subject"])
    return out
