TEMPLATES = {
    "AQA": {
        "Economics": {
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
                          "Economic Methodology and the Economic Problem",
                          "Individual Economic Decision Making",
                          "Price Determination in a Competitive Market",
                          "Production, Costs and Revenue",
                          "Perfect Competition, Imperfect Competition and Monopoly",
                          "The Labour Market", "Distribution of Income and Wealth",
                          "Market Mechanism, Market Failure and Government Intervention"],
                "Paper 2": [
                          "Measurement of Macroeconomic Performance", "How the Macroeconomy Works",
                          "Economic Performance", "Financial Markets and Monetary Policy",
                          "Fiscal Policy and Supply-side Policies", "The International Economy"],
                "Paper 3": [
                          "Economic Methodology and the Economic Problem",
                          "Individual Economic Decision Making",
                          "Price Determination in a Competitive Market",
                          "Production, Costs and Revenue",
                          "Perfect Competition, Imperfect Competition and Monopoly",
                          "The Labour Market", "Distribution of Income and Wealth",
                          "Market Mechanism, Market Failure and Government Intervention",
                          "Measurement of Macroeconomic Performance", "How the Macroeconomy Works",
                          "Economic Performance", "Financial Markets and Monetary Policy",
                          "Fiscal Policy and Supply-side Policies", "The International Economy"],
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
                          "Water and Carbon Cycles", "Hot Desert Systems and Landscapes",
                          "Coastal Systems and Landscapes", "Glacial Systems and Landscapes",
                          "Hazards", "Ecosystems Under Stress"],
                "Paper 2": [
                          "Global Systems and Global Governance", "Changing Places",
                          "Contemporary Urban Environments", "Population and the Environment",
                          "Resource Security"],
            },
        },
        "Biology": {
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
                          "Monomers and Polymers", "Carbohydrates", "Lipids", "Proteins",
                          "Nucleic Acids", "ATP", "Water", "Inorganic Ions", "Cell Structure",
                          "Cell Division", "Transport Across Cell Membranes",
                          "Cell Recognition and the Immune System", "Surface Area to Volume Ratio",
                          "Gas Exchange", "Digestion and Absorption", "Mass Transport",
                          "DNA, Genes and Chromosomes", "DNA and Protein Synthesis",
                          "Genetic Diversity and Meiosis", "Genetic Diversity and Adaptation",
                          "Species and Taxonomy", "Biodiversity Within a Community",
                          "Investigating Diversity"],
                "Paper 2": [
                          "Photosynthesis", "Respiration", "Energy and Ecosystems",
                          "Nutrient Cycles", "Stimuli and Responses", "Nervous Coordination",
                          "Skeletal Muscles", "Homeostasis", "Inheritance", "Populations",
                          "Evolution and Speciation", "Populations in Ecosystems", "Mutations",
                          "Control of Gene Expression", "Using Genome Projects",
                          "Gene Technologies"],
                "Paper 3": [
                          "Monomers and Polymers", "Carbohydrates", "Lipids", "Proteins",
                          "Nucleic Acids", "ATP", "Water", "Inorganic Ions", "Cell Structure",
                          "Cell Division", "Transport Across Cell Membranes",
                          "Cell Recognition and the Immune System", "Surface Area to Volume Ratio",
                          "Gas Exchange", "Digestion and Absorption", "Mass Transport",
                          "DNA, Genes and Chromosomes", "DNA and Protein Synthesis",
                          "Genetic Diversity and Meiosis", "Genetic Diversity and Adaptation",
                          "Species and Taxonomy", "Biodiversity Within a Community",
                          "Investigating Diversity", "Photosynthesis", "Respiration",
                          "Energy and Ecosystems", "Nutrient Cycles", "Stimuli and Responses",
                          "Nervous Coordination", "Skeletal Muscles", "Homeostasis", "Inheritance",
                          "Populations", "Evolution and Speciation", "Populations in Ecosystems",
                          "Mutations", "Control of Gene Expression", "Using Genome Projects",
                          "Gene Technologies"],
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
                          "Atomic Structure", "Amount of Substance", "Bonding", "Energetics",
                          "Chemical Equilibria and Kc", "Oxidation, Reduction and Redox",
                          "Thermodynamics", "Equilibrium Constant Kp",
                          "Electrode Potentials and Electrochemical Cells", "Acids and Bases",
                          "Periodicity", "Group 2, the Alkaline Earth Metals",
                          "Group 7, the Halogens", "Period 3 Elements and Their Oxides",
                          "Transition Metals", "Reactions of Ions in Aqueous Solution"],
                "Paper 2": [
                          "Amount of Substance", "Bonding", "Energetics", "Kinetics",
                          "Chemical Equilibria and Kc", "Rate Equations",
                          "Introduction to Organic Chemistry", "Alkanes", "Halogenoalkanes",
                          "Alkenes", "Alcohols", "Organic Analysis", "Optical Isomerism",
                          "Aldehydes and Ketones", "Carboxylic Acids and Derivatives",
                          "Aromatic Chemistry", "Amines", "Polymers",
                          "Amino Acids, Proteins and DNA", "Organic Synthesis", "NMR Spectroscopy",
                          "Chromatography"],
                "Paper 3": [
                          "Atomic Structure", "Amount of Substance", "Bonding", "Energetics",
                          "Kinetics", "Chemical Equilibria and Kc",
                          "Oxidation, Reduction and Redox", "Thermodynamics", "Rate Equations",
                          "Equilibrium Constant Kp",
                          "Electrode Potentials and Electrochemical Cells", "Acids and Bases",
                          "Periodicity", "Group 2, the Alkaline Earth Metals",
                          "Group 7, the Halogens", "Period 3 Elements and Their Oxides",
                          "Transition Metals", "Reactions of Ions in Aqueous Solution",
                          "Introduction to Organic Chemistry", "Alkanes", "Halogenoalkanes",
                          "Alkenes", "Alcohols", "Organic Analysis", "Optical Isomerism",
                          "Aldehydes and Ketones", "Carboxylic Acids and Derivatives",
                          "Aromatic Chemistry", "Amines", "Polymers",
                          "Amino Acids, Proteins and DNA", "Organic Synthesis", "NMR Spectroscopy",
                          "Chromatography"],
            },
        },
        "Further Maths": {
            "color": "#7A7973",
            "level": "A-Level",
            "choose_optional": 2,
            # 7367. Papers 1 and 2 are compulsory and 100 marks each; the third
            # paper is two 50-mark option booklets chosen from three. AQA
            # publishes a subject row per pairing — 7367DS, 7367MD, 7367SM —
            # which is what confirms two options rather than one.
            "papers": [
                {"code": "Paper 1",  "name": "Compulsory Content 1", "max_marks": 100},
                {"code": "Paper 2",  "name": "Compulsory Content 2", "max_marks": 100},
                {"code": "Paper 3D", "name": "Discrete",   "max_marks": 50, "optional": True},
                {"code": "Paper 3M", "name": "Mechanics",  "max_marks": 50, "optional": True},
                {"code": "Paper 3S", "name": "Statistics", "max_marks": 50, "optional": True},
            ],
            # First assessed in 2019.
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Content sections A-J (compulsory), DA-DG, MA-ME and SA-SH from the
            # 7367 specification. Papers 1 and 2 share the compulsory list
            # because AQA states both "may assess content from" all ten sections
            # and does not divide them between the two.
            "topics": {
                "Paper 1": [
                          "Proof", "Complex Numbers", "Matrices", "Further Algebra and Functions",
                          "Further Calculus", "Further Vectors", "Polar Coordinates",
                          "Hyperbolic Functions", "Differential Equations", "Numerical Methods"],
                "Paper 2": [
                          "Proof", "Complex Numbers", "Matrices", "Further Algebra and Functions",
                          "Further Calculus", "Further Vectors", "Polar Coordinates",
                          "Hyperbolic Functions", "Differential Equations", "Numerical Methods"],
                "Paper 3D": [
                          "Graphs", "Networks", "Network Flows", "Linear Programming",
                          "Critical Path Analysis", "Game Theory for Zero-sum Games",
                          "Binary Operations"],
                "Paper 3M": [
                          "Dimensional Analysis", "Momentum and Collisions",
                          "Work, Energy and Power", "Circular Motion",
                          "Centres of Mass and Moments"],
                "Paper 3S": [
                          "Discrete Random Variables and Expectation", "Poisson Distribution",
                          "Type I and Type II Errors", "Continuous Random Variables",
                          "Chi-squared Tests for Association", "Exponential Distribution",
                          "Inference: One Sample t-Distribution", "Confidence Intervals"],
            },
        },
        "Maths": {
            "color": "#C9A227",
            "level": "A-Level",
            # 7357. Three 100-mark papers, all compulsory.
            "papers": [
                {"code": "Paper 1", "name": "Pure Mathematics",              "max_marks": 100},
                {"code": "Paper 2", "name": "Pure Mathematics and Mechanics","max_marks": 100},
                {"code": "Paper 3", "name": "Pure Mathematics and Statistics","max_marks": 100},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Content areas A-S from the 7357 specification's scheme of
            # assessment, which states exactly what each paper covers.
            #
            # Note Vectors sits in Paper 2, not Paper 1 — AQA puts it with the
            # mechanics content. OCR treats vectors as pure and carries it on
            # every paper, so the two boards genuinely differ here and the lists
            # are not interchangeable.
            "topics": {
                "Paper 1": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Numerical Methods"],
                "Paper 2": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Numerical Methods", "Vectors",
                          "Quantities and Units in Mechanics", "Kinematics",
                          "Forces and Newton's Laws", "Moments"],
                "Paper 3": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Numerical Methods",
                          "Statistical Sampling", "Data Presentation and Interpretation",
                          "Probability", "Statistical Distributions",
                          "Statistical Hypothesis Testing"],
            },
        },
    },
    "Edexcel": {
        "Further Maths": {
            "color": "#7A7973",
            "level": "A-Level",
            # Two of the eight optional papers. Edexcel also restricts which
            # pairs are allowed (any two Option 1 papers, or a matching Option 1
            # and Option 2 pair) — not enforced here, because a student who has
            # already been entered knows their own combination and a rule that
            # rejects a valid one is worse than no rule.
            "choose_optional": 2,
            # 9FM0. Two compulsory Core Pure papers plus two options chosen from
            # eight, so all ten are listed — a student takes four papers, but
            # which four differs between them.
            "papers": [
                {"code": "CP1", "name": "Core Pure 1",              "max_marks": 75},
                {"code": "CP2", "name": "Core Pure 2",              "max_marks": 75},
                {"code": "FP1", "name": "Further Pure 1",           "max_marks": 75, "optional": True},
                {"code": "FP2", "name": "Further Pure 2",           "max_marks": 75, "optional": True},
                {"code": "FS1", "name": "Further Statistics 1",     "max_marks": 75, "optional": True},
                {"code": "FS2", "name": "Further Statistics 2",     "max_marks": 75, "optional": True},
                {"code": "FM1", "name": "Further Mechanics 1",      "max_marks": 75, "optional": True},
                {"code": "FM2", "name": "Further Mechanics 2",      "max_marks": 75, "optional": True},
                {"code": "D1",  "name": "Decision Mathematics 1",   "max_marks": 75, "optional": True},
                {"code": "D2",  "name": "Decision Mathematics 2",   "max_marks": 75, "optional": True},
            ],
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Option-paper topics are the numbered content headings from the
            # 9FM0 specification (Issue 4, June 2023), not recalled from memory.
            # The Core Pure lists are a split of the spec's single combined Core
            # Pure content across the two papers, which is a convention rather
            # than something the spec states.
            "topics": {
                "CP1": ["Complex Numbers", "Argand Diagram", "Modulus-Argument", "Roots of Polynomials",
                        "Series (Sigma Notation)", "Matrices", "Linear Transformations", "Proof by Induction"],
                "CP2": ["Complex Numbers II", "De Moivre's Theorem", "Series & Limits",
                        "Hyperbolic Functions", "Polar Coordinates", "Methods in Calculus",
                        "Volumes of Revolution", "Differential Equations", "Maclaurin/Taylor"],
                "FP1": ["Further Trigonometry", "Further Calculus", "Further Differential Equations",
                        "Coordinate Systems", "Further Vectors", "Further Numerical Methods",
                        "Inequalities"],
                "FP2": ["Groups", "Further Calculus", "Further Matrix Algebra",
                        "Further Complex Numbers", "Number Theory", "Further Sequences and Series"],
                # Previously listed "Correlation & Regression", which is FS2
                # content — corrected against the spec.
                "FS1": ["Discrete Probability Distributions", "Poisson & Binomial Distributions",
                        "Geometric and Negative Binomial Distributions", "Hypothesis Testing",
                        "Central Limit Theorem", "Chi-Squared Tests",
                        "Probability Generating Functions", "Quality of Tests"],
                "FS2": ["Linear Regression", "Continuous Probability Distributions", "Correlation",
                        "Combinations of Random Variables",
                        "Estimation, Confidence Intervals and Tests",
                        "Other Hypothesis Tests and Confidence Intervals",
                        "Confidence Intervals and Tests using the t-Distribution"],
                # Previously listed SHM, Circular Motion and Dimensional
                # Analysis. The first two are FM2 content and the third is not
                # in Edexcel Further Maths at all — corrected against the spec.
                "FM1": ["Momentum and Impulse", "Work, Energy and Power",
                        "Elastic Strings and Springs and Elastic Energy",
                        "Elastic Collisions in One Dimension",
                        "Elastic Collisions in Two Dimensions"],
                "FM2": ["Motion in a Circle", "Centres of Mass of Plane Figures",
                        "Further Centres of Mass", "Further Dynamics", "Further Kinematics"],
                "D1":  ["Algorithms and Graph Theory", "Algorithms on Graphs",
                        "Algorithms on Graphs II", "Critical Path Analysis", "Linear Programming"],
                "D2":  ["Transportation Problems", "Allocation (Assignment) Problems",
                        "Flows in Networks", "Dynamic Programming", "Game Theory",
                        "Recurrence Relations", "Decision Analysis"],
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
        "Further Maths": {
            "color": "#7A7973",
            "level": "A-Level",
            "choose_optional": 2,
            # H245. Both Pure Core papers are mandatory; a student then takes
            # two of the four options, so all six are offered.
            "papers": [
                {"code": "Y540", "name": "Pure Core 1",              "max_marks": 75},
                {"code": "Y541", "name": "Pure Core 2",              "max_marks": 75},
                {"code": "Y542", "name": "Statistics",               "max_marks": 75, "optional": True},
                {"code": "Y543", "name": "Mechanics",                "max_marks": 75, "optional": True},
                {"code": "Y544", "name": "Discrete Mathematics",     "max_marks": 75, "optional": True},
                {"code": "Y545", "name": "Additional Pure Maths",    "max_marks": 75, "optional": True},
            ],
            # First assessed in 2019, so no 2018 series exists.
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Topic areas from the H245 specification. Y540 and Y541 share a
            # list because OCR defines Pure Core once across both mandatory
            # papers and does not split it between them — the same situation as
            # Edexcel's Core Pure.
            "topics": {
                "Y540": [
                          "Proof", "Complex Numbers", "Matrices", "Further Vectors",
                          "Further Algebra", "Series", "Hyperbolic Functions", "Further Calculus",
                          "Polar Coordinates", "Differential Equations"],
                "Y541": [
                          "Proof", "Complex Numbers", "Matrices", "Further Vectors",
                          "Further Algebra", "Series", "Hyperbolic Functions", "Further Calculus",
                          "Polar Coordinates", "Differential Equations"],
                "Y542": [
                          "Probability", "Discrete Random Variables",
                          "Continuous Random Variables", "Linear Combinations of Random Variables",
                          "Hypothesis Tests and Confidence Intervals", "Chi-squared Tests",
                          "Non-parametric Tests", "Correlation", "Linear Regression"],
                "Y543": [
                          "Dimensional Analysis", "Work, Energy and Power", "Impulse and Momentum",
                          "Centre of Mass", "Motion in a Circle",
                          "Further Dynamics and Kinematics"],
                "Y544": [
                          "Mathematical Preliminaries", "Graphs and Networks", "Algorithms",
                          "Network Algorithms", "Decision Making in Project Management",
                          "Graphical Linear Programming", "The Simplex Algorithm", "Game Theory"],
                "Y545": [
                          "Sequences and Series", "Number Theory", "Groups", "Further Vectors",
                          "Surfaces and Partial Differentiation", "Further Calculus"],
            },
        },
        "Maths": {
            "color": "#C9A227",
            "level": "A-Level",
            # H240. Three 100-mark papers; every one of them assesses pure
            # content, and two of them add an applied strand on top.
            "papers": [
                {"code": "Paper 1", "name": "Pure Mathematics",                "max_marks": 100},
                {"code": "Paper 2", "name": "Pure Mathematics and Statistics", "max_marks": 100},
                {"code": "Paper 3", "name": "Pure Mathematics and Mechanics",  "max_marks": 100},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # The numbered content areas from the H240 specification: ten pure
            # (1.01-1.10), five statistics (2.01-2.05), four mechanics
            # (3.01-3.04). Papers 2 and 3 carry the full pure list as well as
            # their applied strand, because that is what they assess — long
            # lists, but a student tagging a question needs the topic that is
            # actually on the paper.
            "topics": {
                "Paper 1": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Numerical Methods", "Vectors"],
                "Paper 2": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Numerical Methods", "Vectors",
                          "Statistical Sampling", "Data Presentation and Interpretation",
                          "Probability", "Statistical Distributions",
                          "Statistical Hypothesis Testing"],
                "Paper 3": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Numerical Methods", "Vectors",
                          "Quantities and Units in Mechanics", "Kinematics",
                          "Forces and Newton's Laws", "Moments"],
            },
        },
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
            mandatory = [p for p in data["papers"] if not p.get("optional")]
            optional = [p for p in data["papers"] if p.get("optional")]
            out.append({
                "board": board,
                "subject": subject,
                "level": data.get("level", DEFAULT_LEVEL),
                "color": data["color"],
                "papers": data["papers"],
                "paper_count": len(data["papers"]),
                "mandatory": mandatory,
                "optional": optional,
                "choose_optional": data.get("choose_optional", 0),
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


def paper_options(board, subject):
    """(mandatory, optional, choose_n) for one qualification.

    A qualification with no optional papers returns an empty optional list and
    choose_n of 0, which callers read as "everything is compulsory".
    """
    try:
        cfg = TEMPLATES[board][subject]
    except KeyError:
        return [], [], 0
    mandatory = [p for p in cfg["papers"] if not p.get("optional")]
    optional = [p for p in cfg["papers"] if p.get("optional")]
    return mandatory, optional, cfg.get("choose_optional", 0)


def has_options(board, subject):
    return bool(paper_options(board, subject)[1])
