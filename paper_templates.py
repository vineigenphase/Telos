TEMPLATES = {
    "AQA": {
        "French": {
            "color": "#4C7EF3",
            "level": "A-Level",
            # 7652. Paper 1 is listening, reading and translation; Paper 2 is two
            # essays on set works. Paper 3 is the speaking exam, marked as a
            # whole rather than question by question — it counts toward the
            # grade, so leaving it out built a prediction from 70% of the
            # qualification.
            "papers": [
                {"code": "Paper 1", "name": "Listening, Reading and Writing", "max_marks": 100},
                {"code": "Paper 2", "name": "Writing",                        "max_marks": 80},
                {"code": "Paper 3", "name": "Speaking",                       "max_marks": 60,
                 "assessment": "oral"},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # The four specification themes, plus the two translation tasks —
            # separately marked at 10 each, and the place students most often
            # lose marks without noticing which half of the paper did it.
            "topics": {
                "Paper 1": [
                          "Aspects of French-speaking Society: Current Trends",
                          "Aspects of French-speaking Society: Current Issues",
                          "Artistic Culture in the French-speaking World",
                          "Aspects of Political Life in the French-speaking World",
                          "Translation into English", "Translation into French"],
                # Two essays on works the student chose from AQA's prescribed
                # lists. Naming every set text would be a long list of which all
                # but two entries are irrelevant to any given student.
                "Paper 2": [
                          "Literary Text Essay", "Film Essay"],
                # Speaking is a discussion of one sub-theme plus the student's
                # own research project.
                "Paper 3": ["Theme Discussion", "Individual Research Project"],
            },
        },
        "German": {
            "color": "#C08A3E",
            "level": "A-Level",
            # 7662. Paper 1 is listening, reading and translation; Paper 2 is two
            # essays on set works. Paper 3 is the speaking exam, marked as a
            # whole rather than question by question — it counts toward the
            # grade, so leaving it out built a prediction from 70% of the
            # qualification.
            "papers": [
                {"code": "Paper 1", "name": "Listening, Reading and Writing", "max_marks": 100},
                {"code": "Paper 2", "name": "Writing",                        "max_marks": 80},
                {"code": "Paper 3", "name": "Speaking",                       "max_marks": 60,
                 "assessment": "oral"},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # The four specification themes, plus the two translation tasks —
            # separately marked at 10 each, and the place students most often
            # lose marks without noticing which half of the paper did it.
            "topics": {
                "Paper 1": [
                          "Aspects of German-speaking Society",
                          "Artistic Culture in the German-speaking World",
                          "Multiculturalism in German-speaking Society",
                          "Aspects of Political Life in German-speaking Society",
                          "Translation into English", "Translation into German"],
                # Two essays on works the student chose from AQA's prescribed
                # lists. Naming every set text would be a long list of which all
                # but two entries are irrelevant to any given student.
                "Paper 2": [
                          "Literary Text Essay", "Film Essay"],
                # Speaking is a discussion of one sub-theme plus the student's
                # own research project.
                "Paper 3": ["Theme Discussion", "Individual Research Project"],
            },
        },
        "Philosophy": {
            "color": "#8A8985",
            "level": "A-Level",
            # 7172. Two 100-mark papers, both compulsory, no options and no
            # coursework — the simplest shape in the catalogue.
            "papers": [
                {"code": "Paper 1", "name": "Epistemology and Moral Philosophy", "max_marks": 100},
                {"code": "Paper 2", "name": "Metaphysics of God and of Mind",    "max_marks": 100},
            ],
            # First assessed in 2019.
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Specification sections 3.1-3.4. Each paper is two sections of five
            # questions, and the sub-sections below are what those questions are
            # drawn from.
            "topics": {
                "Paper 1": [
                          "What is Knowledge?", "Perception as a Source of Knowledge",
                          "Reason as a Source of Knowledge", "The Limits of Knowledge",
                          "Normative Ethical Theories", "Applied Ethics", "Meta-ethics"],
                "Paper 2": [
                          "The Concept and Nature of God",
                          "Arguments Relating to the Existence of God", "Religious Language",
                          "What Do We Mean by Mind?", "Dualist Theories", "Physicalist Theories",
                          "Functionalism"],
            },
        },
        "Spanish": {
            "color": "#B4574C",
            "level": "A-Level",
            # 7692. Paper 1 is listening, reading and translation; Paper 2 is two
            # essays on set works. Paper 3 is the speaking exam, marked as a
            # whole rather than question by question — it counts toward the
            # grade, so leaving it out built a prediction from 70% of the
            # qualification.
            "papers": [
                {"code": "Paper 1", "name": "Listening, Reading and Writing", "max_marks": 100},
                {"code": "Paper 2", "name": "Writing",                        "max_marks": 80},
                {"code": "Paper 3", "name": "Speaking",                       "max_marks": 60,
                 "assessment": "oral"},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # The four specification themes, plus the two translation tasks —
            # separately marked at 10 each, and the place students most often
            # lose marks without noticing which half of the paper did it.
            "topics": {
                "Paper 1": [
                          "Aspects of Hispanic Society", "Artistic Culture in the Hispanic World",
                          "Multiculturalism in Hispanic Society",
                          "Aspects of Political Life in Hispanic Society",
                          "Translation into English", "Translation into Spanish"],
                # Two essays on works the student chose from AQA's prescribed
                # lists. Naming every set text would be a long list of which all
                # but two entries are irrelevant to any given student.
                "Paper 2": [
                          "Literary Text Essay", "Film Essay"],
                # Speaking is a discussion of one sub-theme plus the student's
                # own research project.
                "Paper 3": ["Theme Discussion", "Individual Research Project"],
            },
        },
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
                {"code": "NEA",     "name": "Fieldwork Investigation", "max_marks": 60,
                 "assessment": "coursework"},
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
                # The investigation is the student's own question on any part of
                # the specification, so it has no fixed topic list.
                "NEA": ["Fieldwork Investigation"],
                "Paper 2": [
                          "Global Systems and Global Governance", "Changing Places",
                          "Contemporary Urban Environments", "Population and the Environment",
                          "Resource Security"],
            },
        },
        "Physics": {
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
                {"code": "Paper 3BA", "name": "Paper 3B: Astrophysics", "max_marks": 35, "optional": True},
                {"code": "Paper 3BB", "name": "Paper 3B: Medical Physics", "max_marks": 35, "optional": True},
                {"code": "Paper 3BC", "name": "Paper 3B: Engineering Physics", "max_marks": 35, "optional": True},
                {"code": "Paper 3BD", "name": "Paper 3B: Turning Points in Physics", "max_marks": 35, "optional": True},
                {"code": "Paper 3BE", "name": "Paper 3B: Electronics", "max_marks": 35, "optional": True},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Paper 1 is sections 1-5 and 6.1; Paper 2 is 6.2, 7 and 8 with
            # sections 1-6.1 as assumed knowledge, so those are listed there too
            # — a Paper 2 question can be on mechanics, and a student needs
            # somewhere accurate to tag it.
            "topics": {
                "Paper 1": [
                          "Measurements and Their Errors", "Particles and Radiation", "Waves",
                          "Mechanics and Materials", "Electricity", "Periodic Motion"],
                "Paper 2": [
                          "Thermal Physics", "Fields and Their Consequences", "Nuclear Physics",
                          "Measurements and Their Errors", "Particles and Radiation", "Waves",
                          "Mechanics and Materials", "Electricity", "Periodic Motion"],
                "Paper 3A": [
                          "Practical Skills", "Data Analysis and Uncertainties"],
                "Paper 3BA": [
                          "Telescopes", "Classification of Stars", "Cosmology"],
                "Paper 3BB": [
                          "Physics of the Eye", "Physics of the Ear", "Biological Measurement",
                          "Non-ionising Imaging", "X-ray Imaging",
                          "Radionuclide Imaging and Therapy"],
                "Paper 3BC": [
                          "Rotational Dynamics", "Thermodynamics and Engines"],
                "Paper 3BD": [
                          "The Discovery of the Electron", "Wave-particle Duality",
                          "Special Relativity"],
                "Paper 3BE": [
                          "Discrete Semiconductor Devices", "Analogue and Digital Signals",
                          "Analogue Signal Processing", "Operational Amplifiers",
                          "Digital Signal Processing", "Data Communication Systems"],
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
            "Maths (AS)": {
            "name": "Maths",
            "color": "#C9A227",
            "level": "AS-Level",
            # 7356. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Pure Mathematics and Mechanics", "max_marks": 80},
                {"code": "Paper 2", "name": "Pure Mathematics and Statistics", "max_marks": 80},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Vectors",
                          "Quantities and Units in Mechanics", "Kinematics",
                          "Forces and Newton's Laws"],
                "Paper 2": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Vectors", "Statistical Sampling",
                          "Data Presentation and Interpretation", "Probability",
                          "Statistical Distributions", "Statistical Hypothesis Testing"],
            },
        },
        "Further Maths (AS)": {
            "name": "Further Maths",
            "color": "#C9A227",
            "level": "AS-Level",
            # 7366. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Compulsory Pure Content", "max_marks": 80},
                {"code": "Paper 2D", "name": "Discrete", "max_marks": 40, "optional": True},
                {"code": "Paper 2M", "name": "Mechanics", "max_marks": 40, "optional": True},
                {"code": "Paper 2S", "name": "Statistics", "max_marks": 40, "optional": True},
            ],
            "choose_optional": 2,
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Complex Numbers", "Matrices", "Further Algebra and Functions",
                          "Further Calculus", "Further Vectors", "Proof by Induction"],
                "Paper 2D": [
                          "Graphs and Networks", "Network Flows", "Linear Programming",
                          "Critical Path Analysis", "Game Theory"],
                "Paper 2M": [
                          "Dimensional Analysis", "Momentum and Collisions",
                          "Work, Energy and Power", "Circular Motion"],
                "Paper 2S": [
                          "Discrete Random Variables", "Poisson Distribution",
                          "Contingency Tables", "Hypothesis Testing"],
            },
        },
        "Physics (AS)": {
            "name": "Physics",
            "color": "#5E8B7E",
            "level": "AS-Level",
            # 7407. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Sections 1-5", "max_marks": 70},
                {"code": "Paper 2", "name": "Sections 1-5 and Practical Skills", "max_marks": 70},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Measurements and Their Errors", "Particles and Radiation", "Waves",
                          "Mechanics and Materials", "Electricity"],
                "Paper 2": [
                          "Measurements and Their Errors", "Particles and Radiation", "Waves",
                          "Mechanics and Materials", "Electricity", "Practical Skills",
                          "Data Analysis and Uncertainties"],
            },
        },
        "Chemistry (AS)": {
            "name": "Chemistry",
            "color": "#5E8B7E",
            "level": "AS-Level",
            # 7404. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Inorganic and Physical Chemistry", "max_marks": 80},
                {"code": "Paper 2", "name": "Organic and Physical Chemistry", "max_marks": 80},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Atomic Structure", "Amount of Substance", "Bonding", "Energetics",
                          "Chemical Equilibria and Kc", "Oxidation, Reduction and Redox",
                          "Periodicity", "Group 2, the Alkaline Earth Metals",
                          "Group 7, the Halogens"],
                "Paper 2": [
                          "Amount of Substance", "Bonding", "Energetics", "Kinetics",
                          "Chemical Equilibria and Kc", "Introduction to Organic Chemistry",
                          "Alkanes", "Halogenoalkanes", "Alkenes", "Alcohols", "Organic Analysis"],
            },
        },
        "Biology (AS)": {
            "name": "Biology",
            "color": "#5E9E6B",
            "level": "AS-Level",
            # 7401. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Topics 1-4", "max_marks": 75},
                {"code": "Paper 2", "name": "Topics 1-4 and Practical Skills", "max_marks": 75},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
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
                          "Monomers and Polymers", "Carbohydrates", "Lipids", "Proteins",
                          "Nucleic Acids", "ATP", "Water", "Inorganic Ions", "Cell Structure",
                          "Cell Division", "Transport Across Cell Membranes",
                          "Cell Recognition and the Immune System", "Surface Area to Volume Ratio",
                          "Gas Exchange", "Digestion and Absorption", "Mass Transport",
                          "DNA, Genes and Chromosomes", "DNA and Protein Synthesis",
                          "Genetic Diversity and Meiosis", "Genetic Diversity and Adaptation",
                          "Species and Taxonomy", "Biodiversity Within a Community",
                          "Investigating Diversity", "Practical Skills"],
            },
        },
        "Geography (AS)": {
            "name": "Geography",
            "color": "#6E8F5E",
            "level": "AS-Level",
            # 7036. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Physical Geography and People and the Environment", "max_marks": 80},
                {"code": "Paper 2", "name": "Human Geography and Geography Fieldwork Investigation", "max_marks": 80},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Water and Carbon Cycles", "Hot Desert Systems and Landscapes",
                          "Coastal Systems and Landscapes", "Glacial Systems and Landscapes"],
                "Paper 2": [
                          "Changing Places", "Contemporary Urban Environments",
                          "Fieldwork Investigation"],
            },
        },
        "Economics (AS)": {
            "name": "Economics",
            "color": "#C08A3E",
            "level": "AS-Level",
            # 7135. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "The Operation of Markets and Market Failure", "max_marks": 70},
                {"code": "Paper 2", "name": "The National Economy in a Global Context", "max_marks": 70},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Economic Methodology and the Economic Problem",
                          "Individual Economic Decision Making",
                          "Price Determination in a Competitive Market",
                          "Production, Costs and Revenue", "Competitive and Concentrated Markets",
                          "The Labour Market",
                          "Market Mechanism, Market Failure and Government Intervention"],
                "Paper 2": [
                          "Measurement of Macroeconomic Performance", "How the Macroeconomy Works",
                          "Economic Performance", "Macroeconomic Policy",
                          "The International Economy"],
            },
        },
        "French (AS)": {
            "name": "French",
            "color": "#4C7EF3",
            "level": "AS-Level",
            # 7651. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Listening, Reading and Writing", "max_marks": 90},
                {"code": "Paper 2", "name": "Writing", "max_marks": 50},
                {"code": "Paper 3", "name": "Speaking", "max_marks": 60, "assessment": "oral"},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Aspects of Society: Current Trends", "Artistic Culture",
                          "Translation into English", "Translation into the Target Language"],
                "Paper 2": [
                          "Literary Text Essay", "Film Essay"],
                "Paper 3": [
                          "Theme Discussion", "Stimulus Card Discussion"],
            },
        },
        "German (AS)": {
            "name": "German",
            "color": "#C08A3E",
            "level": "AS-Level",
            # 7661. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Listening, Reading and Writing", "max_marks": 90},
                {"code": "Paper 2", "name": "Writing", "max_marks": 50},
                {"code": "Paper 3", "name": "Speaking", "max_marks": 60, "assessment": "oral"},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Aspects of Society: Current Trends", "Artistic Culture",
                          "Translation into English", "Translation into the Target Language"],
                "Paper 2": [
                          "Literary Text Essay", "Film Essay"],
                "Paper 3": [
                          "Theme Discussion", "Stimulus Card Discussion"],
            },
        },
        "Spanish (AS)": {
            "name": "Spanish",
            "color": "#D06A5A",
            "level": "AS-Level",
            # 7691. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Listening, Reading and Writing", "max_marks": 90},
                {"code": "Paper 2", "name": "Writing", "max_marks": 50},
                {"code": "Paper 3", "name": "Speaking", "max_marks": 60, "assessment": "oral"},
            ],
            # Every series AQA has run for these AS qualifications.
            "years": ["SPEC", "2018", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Aspects of Society: Current Trends", "Artistic Culture",
                          "Translation into English", "Translation into the Target Language"],
                "Paper 2": [
                          "Literary Text Essay", "Film Essay"],
                "Paper 3": [
                          "Theme Discussion", "Stimulus Card Discussion"],
            },
        },
},
    "Edexcel": {
        "Physics": {
            "color": "#5E8B7E",
            "level": "A-Level",
            # Physics. Three compulsory papers; Paper 3 is synoptic and assesses
            # every topic, which is why its list is the whole subject.
            "papers": [
                {"code": "Paper 1", "name": "Advanced Physics I", "max_marks": 90},
                {"code": "Paper 2", "name": "Advanced Physics II", "max_marks": 90},
                {"code": "Paper 3", "name": "General and Practical Principles", "max_marks": 120},
            ],
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Paper-to-topic mapping read from the specification, not inferred.
            # Papers 1 and 2 overlap: several topics are assessed by both.
            "topics": {
                "Paper 1": [
                          "Working as a Physicist", "Mechanics", "Electric Circuits",
                          "Further Mechanics", "Electric and Magnetic Fields",
                          "Nuclear and Particle Physics"],
                "Paper 2": [
                          "Working as a Physicist", "Materials",
                          "Waves and Particle Nature of Light", "Thermodynamics", "Space",
                          "Nuclear Radiation", "Gravitational Fields", "Oscillations"],
                "Paper 3": [
                          "Working as a Physicist", "Mechanics", "Electric Circuits", "Materials",
                          "Waves and Particle Nature of Light", "Further Mechanics",
                          "Electric and Magnetic Fields", "Nuclear and Particle Physics",
                          "Thermodynamics", "Space", "Nuclear Radiation", "Gravitational Fields",
                          "Oscillations"],
            },
        },
        "Chemistry": {
            "color": "#5E8B7E",
            "level": "A-Level",
            # Chemistry. Three compulsory papers; Paper 3 is synoptic and assesses
            # every topic, which is why its list is the whole subject.
            "papers": [
                {"code": "Paper 1", "name": "Advanced Inorganic and Physical", "max_marks": 90},
                {"code": "Paper 2", "name": "Advanced Organic and Physical", "max_marks": 90},
                {"code": "Paper 3", "name": "General and Practical Principles", "max_marks": 120},
            ],
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Paper-to-topic mapping read from the specification, not inferred.
            # Papers 1 and 2 overlap: several topics are assessed by both.
            "topics": {
                "Paper 1": [
                          "Atomic Structure and the Periodic Table", "Bonding and Structure",
                          "Redox I", "Inorganic Chemistry and the Periodic Table",
                          "Formulae, Equations and Amounts of Substance", "Energetics I",
                          "Equilibrium I", "Equilibrium II", "Acid-base Equilibria",
                          "Energetics II", "Redox II", "Transition Metals"],
                "Paper 2": [
                          "Bonding and Structure", "Redox I",
                          "Formulae, Equations and Amounts of Substance", "Organic Chemistry I",
                          "Modern Analytical Techniques I", "Kinetics I", "Kinetics II",
                          "Organic Chemistry II", "Organic Chemistry III",
                          "Modern Analytical Techniques II"],
                "Paper 3": [
                          "Atomic Structure and the Periodic Table", "Bonding and Structure",
                          "Redox I", "Inorganic Chemistry and the Periodic Table",
                          "Formulae, Equations and Amounts of Substance", "Organic Chemistry I",
                          "Modern Analytical Techniques I", "Energetics I", "Kinetics I",
                          "Equilibrium I", "Equilibrium II", "Acid-base Equilibria",
                          "Energetics II", "Redox II", "Transition Metals", "Kinetics II",
                          "Organic Chemistry II", "Organic Chemistry III",
                          "Modern Analytical Techniques II"],
            },
        },
        "Biology": {
            "color": "#5E9E6B",
            "level": "A-Level",
            # Biology A (Salters Nuffield). Three compulsory papers; Paper 3 is synoptic and assesses
            # every topic, which is why its list is the whole subject.
            "papers": [
                {"code": "Paper 1", "name": "Natural Environment and Species Survival", "max_marks": 100},
                {"code": "Paper 2", "name": "Energy, Exercise and Co-ordination", "max_marks": 100},
                {"code": "Paper 3", "name": "General and Practical Applications", "max_marks": 100},
            ],
            "years": ["SPEC", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Paper-to-topic mapping read from the specification, not inferred.
            # Papers 1 and 2 overlap: several topics are assessed by both.
            "topics": {
                "Paper 1": [
                          "Lifestyle, Health and Risk", "Genes and Health", "Voice of the Genome",
                          "Biodiversity and Natural Resources", "On the Wild Side",
                          "Immunity, Infection and Forensics"],
                "Paper 2": [
                          "Lifestyle, Health and Risk", "Genes and Health", "Voice of the Genome",
                          "Biodiversity and Natural Resources", "Run for your Life", "Grey Matter"],
                "Paper 3": [
                          "Lifestyle, Health and Risk", "Genes and Health", "Voice of the Genome",
                          "Biodiversity and Natural Resources", "On the Wild Side",
                          "Immunity, Infection and Forensics", "Run for your Life", "Grey Matter"],
            },
        },
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
            "Maths (AS)": {
            "name": "Maths",
            "color": "#C9A227",
            "level": "AS-Level",
            # AS Mathematics. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Pure Mathematics", "max_marks": 100},
                {"code": "Paper 2", "name": "Statistics and Mechanics", "max_marks": 60},
            ],
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Vectors", "Numerical Methods"],
                "Paper 2": [
                          "Statistical Sampling", "Data Presentation and Interpretation",
                          "Probability", "Statistical Distributions",
                          "Statistical Hypothesis Testing", "Quantities and Units in Mechanics",
                          "Kinematics", "Forces and Newton's Laws"],
            },
        },
        "Further Maths (AS)": {
            "name": "Further Maths",
            "color": "#C9A227",
            "level": "AS-Level",
            # AS Further Mathematics. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Core Pure Mathematics", "max_marks": 80},
                {"code": "Paper 221", "name": "Further Pure Mathematics 1", "max_marks": 40, "optional": True},
                {"code": "Paper 222", "name": "Further Pure Mathematics 2", "max_marks": 40, "optional": True},
                {"code": "Paper 223", "name": "Further Statistics 1", "max_marks": 40, "optional": True},
                {"code": "Paper 224", "name": "Further Statistics 2", "max_marks": 40, "optional": True},
                {"code": "Paper 225", "name": "Further Mechanics 1", "max_marks": 40, "optional": True},
                {"code": "Paper 226", "name": "Further Mechanics 2", "max_marks": 40, "optional": True},
                {"code": "Paper 227", "name": "Decision Mathematics 1", "max_marks": 40, "optional": True},
                {"code": "Paper 228", "name": "Decision Mathematics 2", "max_marks": 40, "optional": True},
            ],
            # Paper 2 is two 40-mark option sections, not one
            # paper; Pearson publishes each option separately.
            "choose_optional": 2,
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Complex Numbers", "Matrices", "Vectors", "Roots of Polynomials",
                          "Series", "Proof by Induction"],
                "Paper 221": [
                          "Complex Numbers", "Roots of Polynomials", "Series",
                          "Coordinate Systems", "Matrix Algebra", "Proof by Induction"],
                "Paper 222": [
                          "Inequalities", "Series", "First Order Differential Equations",
                          "Second Order Differential Equations", "Maclaurin and Taylor Series",
                          "Polar Coordinates"],
                "Paper 223": [
                          "Discrete Probability Distributions", "Poisson Distribution",
                          "Geometric and Negative Binomial", "Hypothesis Testing",
                          "Chi-squared Tests", "Probability Generating Functions"],
                "Paper 224": [
                          "Linear Regression", "Continuous Probability Distributions",
                          "Correlation", "Combinations of Random Variables", "Quality of Tests"],
                "Paper 225": [
                          "Momentum and Impulse", "Work, Energy and Power",
                          "Elastic Strings and Springs", "Elastic Collisions in One Dimension"],
                "Paper 226": [
                          "Motion in a Circle", "Centres of Mass", "Further Dynamics",
                          "Further Kinematics"],
                "Paper 227": [
                          "Algorithms and Graph Theory", "Algorithms on Graphs",
                          "Critical Path Analysis", "Linear Programming", "Route Inspection"],
                "Paper 228": [
                          "Transportation Problems", "Allocation Problems", "Flows in Networks",
                          "Dynamic Programming", "Game Theory"],
            },
        },
        "Physics (AS)": {
            "name": "Physics",
            "color": "#5E8B7E",
            "level": "AS-Level",
            # AS Physics. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Core Physics I", "max_marks": 80},
                {"code": "Paper 2", "name": "Core Physics II", "max_marks": 80},
            ],
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Working as a Physicist", "Mechanics", "Electric Circuits", "Materials",
                          "Waves and Particle Nature of Light"],
                "Paper 2": [
                          "Working as a Physicist", "Mechanics", "Electric Circuits", "Materials",
                          "Waves and Particle Nature of Light"],
            },
        },
        "Chemistry (AS)": {
            "name": "Chemistry",
            "color": "#5E8B7E",
            "level": "AS-Level",
            # AS Chemistry. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Core Inorganic and Physical Chemistry", "max_marks": 80},
                {"code": "Paper 2", "name": "Core Organic and Physical Chemistry", "max_marks": 80},
            ],
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Atomic Structure and the Periodic Table", "Bonding and Structure",
                          "Redox I", "Inorganic Chemistry and the Periodic Table",
                          "Formulae, Equations and Amounts of Substance", "Organic Chemistry I",
                          "Modern Analytical Techniques I", "Energetics I", "Kinetics I",
                          "Equilibrium I"],
                "Paper 2": [
                          "Atomic Structure and the Periodic Table", "Bonding and Structure",
                          "Redox I", "Inorganic Chemistry and the Periodic Table",
                          "Formulae, Equations and Amounts of Substance", "Organic Chemistry I",
                          "Modern Analytical Techniques I", "Energetics I", "Kinetics I",
                          "Equilibrium I"],
            },
        },
        "Biology (AS)": {
            "name": "Biology",
            "color": "#5E9E6B",
            "level": "AS-Level",
            # AS Biology A (Salters Nuffield). A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Lifestyle, Transport, Genes and Health", "max_marks": 80},
                {"code": "Paper 2", "name": "Development, Plants and the Environment", "max_marks": 80},
            ],
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Lifestyle, Health and Risk", "Genes and Health", "Voice of the Genome",
                          "Biodiversity and Natural Resources"],
                "Paper 2": [
                          "Lifestyle, Health and Risk", "Genes and Health", "Voice of the Genome",
                          "Biodiversity and Natural Resources"],
            },
        },
},
    "OCR A": {
        "Biology": {
            "color": "#5E9E6B",
            "level": "A-Level",
            # H420. Three written papers; the Practical Endorsement is reported
            # separately from the grade and is not tracked.
            "papers": [
                {"code": "Paper 1", "name": "Biological processes", "max_marks": 100},
                {"code": "Paper 2", "name": "Biological diversity", "max_marks": 100},
                {"code": "Paper 3", "name": "Unified biology", "max_marks": 70},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Module 1 is practical skills, assessed inside every written paper,
            # so its four planning-to-evaluation sections appear on all three.
            # Modules 1.2.1 and 1.2.2 are the Practical Endorsement and are left
            # out — they are not assessed by these papers.
            "topics": {
                "Paper 1": [
                          "Planning", "Implementing", "Analysis", "Evaluation", "Cell Structure",
                          "Biological Molecules", "Nucleotides and Nucleic Acids", "Enzymes",
                          "Biological Membranes", "Cell Division, Diversity and Organisation",
                          "Exchange Surfaces", "Transport in Animals", "Transport in Plants",
                          "Communication and Homeostasis", "Excretion", "Neuronal Communication",
                          "Hormonal Communication", "Plant and Animal Responses", "Photosynthesis",
                          "Respiration"],
                "Paper 2": [
                          "Planning", "Implementing", "Analysis", "Evaluation", "Cell Structure",
                          "Biological Molecules", "Nucleotides and Nucleic Acids", "Enzymes",
                          "Biological Membranes", "Cell Division, Diversity and Organisation",
                          "Communicable Diseases and Immunity", "Biodiversity",
                          "Classification and Evolution", "Cellular Control",
                          "Patterns of Inheritance", "Manipulating Genomes",
                          "Cloning and Biotechnology", "Ecosystems",
                          "Populations and Sustainability"],
                "Paper 3": [
                          "Planning", "Implementing", "Analysis", "Evaluation", "Cell Structure",
                          "Biological Molecules", "Nucleotides and Nucleic Acids", "Enzymes",
                          "Biological Membranes", "Cell Division, Diversity and Organisation",
                          "Exchange Surfaces", "Transport in Animals", "Transport in Plants",
                          "Communicable Diseases and Immunity", "Biodiversity",
                          "Classification and Evolution", "Communication and Homeostasis",
                          "Excretion", "Neuronal Communication", "Hormonal Communication",
                          "Plant and Animal Responses", "Photosynthesis", "Respiration",
                          "Cellular Control", "Patterns of Inheritance", "Manipulating Genomes",
                          "Cloning and Biotechnology", "Ecosystems",
                          "Populations and Sustainability"],
            },
        },
        "Chemistry": {
            "color": "#5E8B7E",
            "level": "A-Level",
            # H432. Three written papers; the Practical Endorsement is reported
            # separately from the grade and is not tracked.
            "papers": [
                {"code": "Paper 1", "name": "Periodic Table and Physical", "max_marks": 100},
                {"code": "Paper 2", "name": "Synthesis and Analysis", "max_marks": 100},
                {"code": "Paper 3", "name": "Unified chemistry", "max_marks": 70},
            ],
            "years": ["SPEC", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            # Module 1 is practical skills, assessed inside every written paper,
            # so its four planning-to-evaluation sections appear on all three.
            # Modules 1.2.1 and 1.2.2 are the Practical Endorsement and are left
            # out — they are not assessed by these papers.
            "topics": {
                "Paper 1": [
                          "Planning", "Implementing", "Analysis", "Evaluation",
                          "Atomic Structure and Isotopes", "Compounds, Formulae and Equations",
                          "Amount of Substance", "Acids", "Redox", "Electron Structure",
                          "Bonding and Structure", "Periodicity", "Group 2", "The Halogens",
                          "Qualitative Analysis", "Enthalpy Changes", "Reaction Rates",
                          "Chemical Equilibrium", "How Fast?", "How Far?",
                          "Acids, Bases and Buffers", "Lattice Enthalpy", "Enthalpy and Entropy",
                          "Redox and Electrode Potentials", "Transition Elements",
                          "Qualitative Analysis II"],
                "Paper 2": [
                          "Planning", "Implementing", "Analysis", "Evaluation",
                          "Atomic Structure and Isotopes", "Compounds, Formulae and Equations",
                          "Amount of Substance", "Acids", "Redox", "Electron Structure",
                          "Bonding and Structure", "Basic Concepts of Organic Chemistry",
                          "Alkanes", "Alkenes", "Alcohols", "Haloalkanes", "Organic Synthesis",
                          "Analytical Techniques", "Aromatic Compounds", "Carbonyl Compounds",
                          "Carboxylic Acids and Esters", "Amines",
                          "Amino Acids, Amides and Chirality", "Polyesters and Polyamides",
                          "Carbon-carbon Bond Formation", "Organic Synthesis II",
                          "Chromatography and Qualitative Analysis", "Spectroscopy"],
                "Paper 3": [
                          "Planning", "Implementing", "Analysis", "Evaluation",
                          "Atomic Structure and Isotopes", "Compounds, Formulae and Equations",
                          "Amount of Substance", "Acids", "Redox", "Electron Structure",
                          "Bonding and Structure", "Periodicity", "Group 2", "The Halogens",
                          "Qualitative Analysis", "Enthalpy Changes", "Reaction Rates",
                          "Chemical Equilibrium", "Basic Concepts of Organic Chemistry", "Alkanes",
                          "Alkenes", "Alcohols", "Haloalkanes", "Organic Synthesis",
                          "Analytical Techniques", "How Fast?", "How Far?",
                          "Acids, Bases and Buffers", "Lattice Enthalpy", "Enthalpy and Entropy",
                          "Redox and Electrode Potentials", "Transition Elements",
                          "Qualitative Analysis II", "Aromatic Compounds", "Carbonyl Compounds",
                          "Carboxylic Acids and Esters", "Amines",
                          "Amino Acids, Amides and Chirality", "Polyesters and Polyamides",
                          "Carbon-carbon Bond Formation", "Organic Synthesis II",
                          "Chromatography and Qualitative Analysis", "Spectroscopy"],
            },
        },
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
        "Maths (AS)": {
            "name": "Maths",
            "color": "#C9A227",
            "level": "AS-Level",
            # Mathematics A. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Pure Mathematics and Statistics", "max_marks": 75},
                {"code": "Paper 2", "name": "Pure Mathematics and Mechanics", "max_marks": 75},
            ],
            # 2019 is from OCR's AS-only "Reformed AS Levels" document;
            # from 2022 the AS tables are a section of the combined series
            # document. No 2018 to hand.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Vectors", "Statistical Sampling",
                          "Data Presentation and Interpretation", "Probability",
                          "Statistical Distributions", "Statistical Hypothesis Testing"],
                "Paper 2": [
                          "Proof", "Algebra and Functions", "Coordinate Geometry",
                          "Sequences and Series", "Trigonometry", "Exponentials and Logarithms",
                          "Differentiation", "Integration", "Vectors",
                          "Quantities and Units in Mechanics", "Kinematics",
                          "Forces and Newton's Laws"],
            },
        },
        "Further Maths (AS)": {
            "name": "Further Maths",
            "color": "#C9A227",
            "level": "AS-Level",
            # Further Mathematics A. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Y531", "name": "Pure Core", "max_marks": 60},
                {"code": "Y532", "name": "Statistics", "max_marks": 60, "optional": True},
                {"code": "Y533", "name": "Mechanics", "max_marks": 60, "optional": True},
                {"code": "Y534", "name": "Discrete Mathematics", "max_marks": 60, "optional": True},
                {"code": "Y535", "name": "Additional Pure Maths", "max_marks": 60, "optional": True},
            ],
            "choose_optional": 2,
            # 2019 is from OCR's AS-only "Reformed AS Levels" document;
            # from 2022 the AS tables are a section of the combined series
            # document. No 2018 to hand.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Y531": [
                          "Matrices", "Complex Numbers", "Vectors", "Algebra", "Series",
                          "Roots of Polynomials", "Proof by Induction"],
                "Y532": [
                          "Discrete Random Variables", "Bivariate Data", "Chi-squared Tests",
                          "Non-parametric Tests"],
                "Y533": [
                          "Dimensional Analysis", "Work, Energy and Power", "Impulse and Momentum",
                          "Centre of Mass"],
                "Y534": [
                          "Mathematical Preliminaries", "Graphs and Networks",
                          "Network Algorithms", "Critical Path Analysis", "Linear Programming"],
                "Y535": [
                          "Sequences and Series", "Number Theory", "Groups",
                          "Vectors and Surfaces", "Curves"],
            },
        },
        "Physics (AS)": {
            "name": "Physics",
            "color": "#5E8B7E",
            "level": "AS-Level",
            # Physics A. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Breadth in Physics", "max_marks": 70},
                {"code": "Paper 2", "name": "Depth in Physics", "max_marks": 70},
            ],
            # 2019 is from OCR's AS-only "Reformed AS Levels" document;
            # from 2022 the AS tables are a section of the combined series
            # document. No 2018 to hand.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Planning", "Implementing", "Analysis", "Evaluation",
                          "Physical Quantities and Units",
                          "Making Measurements and Analysing Data", "Motion", "Forces in Action",
                          "Work, Energy and Power", "Materials", "Laws of Motion and Momentum",
                          "Charge and Current", "Energy, Power and Resistance",
                          "Electrical Circuits", "Waves", "Quantum Physics"],
                "Paper 2": [
                          "Planning", "Implementing", "Analysis", "Evaluation",
                          "Physical Quantities and Units",
                          "Making Measurements and Analysing Data", "Motion", "Forces in Action",
                          "Work, Energy and Power", "Materials", "Laws of Motion and Momentum",
                          "Charge and Current", "Energy, Power and Resistance",
                          "Electrical Circuits", "Waves", "Quantum Physics"],
            },
        },
        "Chemistry (AS)": {
            "name": "Chemistry",
            "color": "#5E8B7E",
            "level": "AS-Level",
            # Chemistry A. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Breadth in Chemistry", "max_marks": 70},
                {"code": "Paper 2", "name": "Depth in Chemistry", "max_marks": 70},
            ],
            # 2019 is from OCR's AS-only "Reformed AS Levels" document;
            # from 2022 the AS tables are a section of the combined series
            # document. No 2018 to hand.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Planning", "Implementing", "Analysis", "Evaluation",
                          "Atomic Structure and Isotopes", "Compounds, Formulae and Equations",
                          "Amount of Substance", "Acids", "Redox", "Electron Structure",
                          "Bonding and Structure", "Periodicity", "Group 2", "The Halogens",
                          "Qualitative Analysis", "Enthalpy Changes", "Reaction Rates",
                          "Chemical Equilibrium", "Basic Concepts of Organic Chemistry", "Alkanes",
                          "Alkenes", "Alcohols", "Haloalkanes", "Organic Synthesis",
                          "Spectroscopy"],
                "Paper 2": [
                          "Planning", "Implementing", "Analysis", "Evaluation",
                          "Atomic Structure and Isotopes", "Compounds, Formulae and Equations",
                          "Amount of Substance", "Acids", "Redox", "Electron Structure",
                          "Bonding and Structure", "Periodicity", "Group 2", "The Halogens",
                          "Qualitative Analysis", "Enthalpy Changes", "Reaction Rates",
                          "Chemical Equilibrium", "Basic Concepts of Organic Chemistry", "Alkanes",
                          "Alkenes", "Alcohols", "Haloalkanes", "Organic Synthesis",
                          "Spectroscopy"],
            },
        },
        "Biology (AS)": {
            "name": "Biology",
            "color": "#5E9E6B",
            "level": "AS-Level",
            # Biology A. A qualification in its own right, graded A-E
            # with no A*.
            "papers": [
                {"code": "Paper 1", "name": "Breadth in Biology", "max_marks": 70},
                {"code": "Paper 2", "name": "Depth in Biology", "max_marks": 70},
            ],
            # 2019 is from OCR's AS-only "Reformed AS Levels" document;
            # from 2022 the AS tables are a section of the combined series
            # document. No 2018 to hand.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Planning", "Implementing", "Analysis", "Evaluation", "Cell Structure",
                          "Biological Molecules", "Nucleotides and Nucleic Acids", "Enzymes",
                          "Biological Membranes", "Cell Division, Diversity and Organisation",
                          "Exchange Surfaces", "Transport in Animals", "Transport in Plants",
                          "Communicable Diseases and the Immune System", "Biodiversity",
                          "Classification and Evolution"],
                "Paper 2": [
                          "Planning", "Implementing", "Analysis", "Evaluation", "Cell Structure",
                          "Biological Molecules", "Nucleotides and Nucleic Acids", "Enzymes",
                          "Biological Membranes", "Cell Division, Diversity and Organisation",
                          "Exchange Surfaces", "Transport in Animals", "Transport in Plants",
                          "Communicable Diseases and the Immune System", "Biodiversity",
                          "Classification and Evolution"],
            },
        },
    },
    # SQA. A separate board, and the only one whose boundaries Telos
    # derives rather than reads: SQA publishes cut-off scores for the
    # whole course and never per component. The component max marks are
    # SQA's own. Keys are suffixed (AH) to leave room for Highers.
    "SQA": {
        "Biology (AH)": {
            "name": "Biology",
            "color": "#5E9E6B",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Section 1", "name": "Section 1: Objective Test", "max_marks": 24},
                {"code": "Section 2", "name": "Section 2", "max_marks": 96},
                {"code": "Project", "name": "Project", "max_marks": 40, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Section 1": [
                          "Cells and Proteins", "Organisms and Evolution", "Investigative Biology"],
                "Section 2": [
                          "Cells and Proteins", "Organisms and Evolution", "Investigative Biology"],
                "Project": [
                          "Research Project"],
            },
        },
        "Chemistry (AH)": {
            "name": "Chemistry",
            "color": "#5E8B7E",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Section 1", "name": "Section 1: Objective Test", "max_marks": 27},
                {"code": "Section 2", "name": "Section 2", "max_marks": 93},
                {"code": "Project", "name": "Project", "max_marks": 40, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Section 1": [
                          "Inorganic and Physical Chemistry",
                          "Organic Chemistry and Instrumental Analysis", "Researching Chemistry"],
                "Section 2": [
                          "Inorganic and Physical Chemistry",
                          "Organic Chemistry and Instrumental Analysis", "Researching Chemistry"],
                "Project": [
                          "Research Project"],
            },
        },
        "Economics (AH)": {
            "name": "Economics",
            "color": "#C08A3E",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Question Paper", "name": "Question Paper", "max_marks": 80},
                {"code": "Project", "name": "Project", "max_marks": 40, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Question Paper": [
                          "Economics of the Market", "Global Economic Activity", "The UK Economy",
                          "Economic Data and Analysis"],
                "Project": [
                          "Economics Project"],
            },
        },
        "English (AH)": {
            "name": "English",
            "color": "#8A6FA8",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Literary Study", "name": "Literary Study", "max_marks": 20},
                {"code": "Textual Analysis", "name": "Textual Analysis", "max_marks": 20},
                {"code": "Dissertation", "name": "Project: Dissertation", "max_marks": 30, "assessment": "coursework"},
                {"code": "Portfolio", "name": "Portfolio: Writing", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Literary Study": [
                          "Critical Essay on a Chosen Text", "Poetry", "Prose Fiction",
                          "Prose Non-fiction", "Drama", "Film and Television Drama",
                          "Language Study"],
                "Textual Analysis": [
                          "Unseen Poetry", "Unseen Prose", "Unseen Drama", "Comparative Analysis"],
                "Dissertation": [
                          "Independent Literary Study"],
                "Portfolio": [
                          "Broadly Creative Writing", "Broadly Discursive Writing"],
            },
        },
        "French (AH)": {
            "name": "French",
            "color": "#4C7EF3",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Listening", "name": "Listening and Discursive Writing", "max_marks": 70},
                {"code": "Reading", "name": "Reading and Translation", "max_marks": 50},
                {"code": "Talking", "name": "Performance: Talking", "max_marks": 50, "assessment": "oral"},
                {"code": "Portfolio", "name": "Portfolio", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Listening": [
                          "Listening Comprehension", "Discursive Writing"],
                "Reading": [
                          "Reading Comprehension", "Translation into English"],
                "Talking": [
                          "Presentation", "Discussion"],
                "Portfolio": [
                          "Written Portfolio"],
            },
        },
        "Geography (AH)": {
            "name": "Geography",
            "color": "#6E8F5E",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Question Paper", "name": "Question Paper", "max_marks": 50},
                {"code": "Folio A", "name": "Project-folio: Geographical Study", "max_marks": 60, "assessment": "coursework"},
                {"code": "Folio B", "name": "Project-folio: Geographical Issue", "max_marks": 40, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Question Paper": [
                          "Geographical Methods and Techniques"],
                "Folio A": [
                          "Geographical Study"],
                "Folio B": [
                          "Geographical Issue"],
            },
        },
        "German (AH)": {
            "name": "German",
            "color": "#C08A3E",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Listening", "name": "Listening and Discursive Writing", "max_marks": 70},
                {"code": "Reading", "name": "Reading and Translation", "max_marks": 50},
                {"code": "Talking", "name": "Performance: Talking", "max_marks": 50, "assessment": "oral"},
                {"code": "Portfolio", "name": "Portfolio", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Listening": [
                          "Listening Comprehension", "Discursive Writing"],
                "Reading": [
                          "Reading Comprehension", "Translation into English"],
                "Talking": [
                          "Presentation", "Discussion"],
                "Portfolio": [
                          "Written Portfolio"],
            },
        },
        "Maths (AH)": {
            "name": "Maths",
            "color": "#C9A227",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Paper 1", "name": "Paper 1 (Non-calculator)", "max_marks": 35},
                {"code": "Paper 2", "name": "Paper 2 (Calculator)", "max_marks": 80},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Methods in Algebra and Calculus",
                          "Applications of Algebra and Calculus",
                          "Geometry, Proof and Systems of Equations"],
                "Paper 2": [
                          "Methods in Algebra and Calculus",
                          "Applications of Algebra and Calculus",
                          "Geometry, Proof and Systems of Equations"],
            },
        },
        "Physics (AH)": {
            "name": "Physics",
            "color": "#5E8B7E",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Question Paper", "name": "Question Paper", "max_marks": 120},
                {"code": "Project", "name": "Project", "max_marks": 40, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Question Paper": [
                          "Rotational Motion and Astrophysics", "Quanta and Waves",
                          "Electromagnetism", "Units, Prefixes and Uncertainties"],
                "Project": [
                          "Research Project"],
            },
        },
        "Spanish (AH)": {
            "name": "Spanish",
            "color": "#D06A5A",
            "level": "Advanced Higher",
            # Graded A-D: no A* and no E. The component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Listening", "name": "Listening and Discursive Writing", "max_marks": 70},
                {"code": "Reading", "name": "Reading and Translation", "max_marks": 50},
                {"code": "Talking", "name": "Performance: Talking", "max_marks": 50, "assessment": "oral"},
                {"code": "Portfolio", "name": "Portfolio", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with the project
            # removed, which is a different set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Listening": [
                          "Listening Comprehension", "Discursive Writing"],
                "Reading": [
                          "Reading Comprehension", "Translation into English"],
                "Talking": [
                          "Presentation", "Discussion"],
                "Portfolio": [
                          "Written Portfolio"],
            },
        },
        "Biology (H)": {
            "name": "Biology",
            "color": "#5E9E6B",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Paper 1", "name": "Paper 1 (Multiple Choice)", "max_marks": 25},
                {"code": "Paper 2", "name": "Paper 2", "max_marks": 95},
                {"code": "Assignment", "name": "Assignment", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "DNA and the Genome", "Metabolism and Survival",
                          "Sustainability and Interdependence"],
                "Paper 2": [
                          "DNA and the Genome", "Metabolism and Survival",
                          "Sustainability and Interdependence"],
                "Assignment": [
                          "Assignment"],
            },
        },
        "Chemistry (H)": {
            "name": "Chemistry",
            "color": "#5E8B7E",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Paper 1", "name": "Paper 1 (Multiple Choice)", "max_marks": 25},
                {"code": "Paper 2", "name": "Paper 2", "max_marks": 95},
                {"code": "Assignment", "name": "Assignment", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Chemical Changes and Structure", "Nature's Chemistry",
                          "Chemistry in Society", "Researching Chemistry"],
                "Paper 2": [
                          "Chemical Changes and Structure", "Nature's Chemistry",
                          "Chemistry in Society", "Researching Chemistry"],
                "Assignment": [
                          "Assignment"],
            },
        },
        "Economics (H)": {
            "name": "Economics",
            "color": "#C08A3E",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Question Paper", "name": "Question Paper", "max_marks": 90},
                {"code": "Assignment", "name": "Assignment", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Question Paper": [
                          "Economics of the Market", "UK Economic Activity",
                          "Global Economic Activity"],
                "Assignment": [
                          "Economics Assignment"],
            },
        },
        "English (H)": {
            "name": "English",
            "color": "#8A6FA8",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Paper 1", "name": "Reading for Understanding, Analysis and Evaluation", "max_marks": 30},
                {"code": "Paper 2", "name": "Critical Reading", "max_marks": 40},
                {"code": "Portfolio", "name": "Portfolio: Writing", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Reading for Understanding", "Analysis", "Evaluation", "Summarising",
                          "Comparison of Passages"],
                "Paper 2": [
                          "Scottish Text", "Critical Essay: Drama", "Critical Essay: Prose",
                          "Critical Essay: Poetry", "Critical Essay: Film and Television Drama",
                          "Critical Essay: Language"],
                "Portfolio": [
                          "Broadly Creative Writing", "Broadly Discursive Writing"],
            },
        },
        "French (H)": {
            "name": "French",
            "color": "#4C7EF3",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Directed Writing", "name": "Directed Writing", "max_marks": 15},
                {"code": "Listening", "name": "Listening", "max_marks": 30},
                {"code": "Reading", "name": "Reading", "max_marks": 30},
                {"code": "Talking", "name": "Performance: Talking", "max_marks": 30, "assessment": "oral"},
                {"code": "Assignment", "name": "Assignment: Writing", "max_marks": 15, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Directed Writing": [
                          "Directed Writing"],
                "Listening": [
                          "Listening Comprehension"],
                "Reading": [
                          "Reading Comprehension"],
                "Talking": [
                          "Presentation", "Conversation"],
                "Assignment": [
                          "Written Assignment"],
            },
        },
        "Geography (H)": {
            "name": "Geography",
            "color": "#6E8F5E",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Paper 1", "name": "Physical and Human Environments", "max_marks": 50},
                {"code": "Paper 2", "name": "Global Issues and Geographical Skills", "max_marks": 30},
                {"code": "Assignment", "name": "Assignment", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Atmosphere", "Hydrosphere", "Lithosphere", "Biosphere", "Population",
                          "Rural Land Use", "Urban"],
                "Paper 2": [
                          "River Basin Management", "Development and Health",
                          "Global Climate Change", "Energy", "Geographical Skills"],
                "Assignment": [
                          "Geographical Assignment"],
            },
        },
        "German (H)": {
            "name": "German",
            "color": "#C08A3E",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Directed Writing", "name": "Directed Writing", "max_marks": 15},
                {"code": "Listening", "name": "Listening", "max_marks": 30},
                {"code": "Reading", "name": "Reading", "max_marks": 30},
                {"code": "Talking", "name": "Performance: Talking", "max_marks": 30, "assessment": "oral"},
                {"code": "Assignment", "name": "Assignment: Writing", "max_marks": 15, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Directed Writing": [
                          "Directed Writing"],
                "Listening": [
                          "Listening Comprehension"],
                "Reading": [
                          "Reading Comprehension"],
                "Talking": [
                          "Presentation", "Conversation"],
                "Assignment": [
                          "Written Assignment"],
            },
        },
        "Maths (H)": {
            "name": "Maths",
            "color": "#C9A227",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Paper 1", "name": "Paper 1 (Non-calculator)", "max_marks": 55},
                {"code": "Paper 2", "name": "Paper 2 (Calculator)", "max_marks": 65},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Algebraic and Trigonometric Skills", "Geometric Skills",
                          "Calculus Skills", "Algebraic and Geometric Skills"],
                "Paper 2": [
                          "Algebraic and Trigonometric Skills", "Geometric Skills",
                          "Calculus Skills", "Reasoning Skills"],
            },
        },
        "Physics (H)": {
            "name": "Physics",
            "color": "#5E8B7E",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Paper 1", "name": "Paper 1 (Multiple Choice)", "max_marks": 25},
                {"code": "Paper 2", "name": "Paper 2", "max_marks": 95},
                {"code": "Assignment", "name": "Assignment", "max_marks": 30, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Paper 1": [
                          "Our Dynamic Universe", "Particles and Waves", "Electricity"],
                "Paper 2": [
                          "Our Dynamic Universe", "Particles and Waves", "Electricity"],
                "Assignment": [
                          "Assignment"],
            },
        },
        "Spanish (H)": {
            "name": "Spanish",
            "color": "#D06A5A",
            "level": "Higher",
            # Graded A-D: no A* and no E. Component max marks are
            # SQA's own; the boundaries are derived from the course
            # cut-off, because SQA publishes none per component.
            "papers": [
                {"code": "Directed Writing", "name": "Directed Writing", "max_marks": 15},
                {"code": "Listening", "name": "Listening", "max_marks": 30},
                {"code": "Reading", "name": "Reading", "max_marks": 30},
                {"code": "Talking", "name": "Performance: Talking", "max_marks": 30, "assessment": "oral"},
                {"code": "Assignment", "name": "Assignment: Writing", "max_marks": 15, "assessment": "coursework"},
            ],
            # 2022 and 2023 ran in a modified form with a different
            # set of components.
            "years": ["SPEC", "2019", "2022", "2023", "2024", "2025"],
            "topics": {
                "Directed Writing": [
                          "Directed Writing"],
                "Listening": [
                          "Listening Comprehension"],
                "Reading": [
                          "Reading Comprehension"],
                "Talking": [
                          "Presentation", "Conversation"],
                "Assignment": [
                          "Written Assignment"],
            },
        },
    },
    "UAT-UK": {
        # Admissions tests, not qualifications. Reported on a 1-9 scale to one
        # decimal place, so `graded: False` — Telos tracks every mark and topic
        # and refuses to name a grade. See is_graded().
        "TMUA": {
            "color": "#7A5AF8",
            "level": "Admissions test",
            "graded": False,
            "name": "TMUA",
            "papers": [
                {"code": "Paper 1", "name": "Applications of Mathematical Knowledge",
                 "max_marks": 20},
                {"code": "Paper 2", "name": "Mathematical Reasoning",
                 "max_marks": 20},
            ],
            # Official papers run 2016-2023. UAT-UK does not release the live
            # questions from 2024 onward, so those years are deliberately absent
            # rather than listed and unloggable.
            "years": ['SPEC', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023'],
            "topics": {
                "Paper 1": [
                    "Algebra and functions", "Sequences and series",
                    "Coordinate geometry", "Trigonometry",
                    "Exponentials and logarithms", "Differentiation",
                    "Integration", "Graphs of functions",
                    "Number and place value", "Probability", "Statistics",
                ],
                "Paper 2": [
                    "Logic and proof", "Mathematical reasoning",
                    "Necessary and sufficient conditions", "Proof by contradiction",
                    "Proof by counterexample", "Proof by induction",
                    "Identifying flawed arguments", "Algebra and functions",
                    "Sequences and series", "Number theory", "Geometry",
                ],
            },
        },
        "ESAT": {
            "color": "#0F9D8C",
            "level": "Admissions test",
            "graded": False,
            "name": "ESAT",
            # Each module is 27 multiple-choice questions in 40 minutes, and is
            # scored separately. Mathematics 1 is compulsory; most candidates
            # sit it plus two more, but which two is set by the course applied
            # for, so no choose_optional is declared here.
            "papers": [
                {"code": "Mathematics 1", "name": "Mathematics 1 (compulsory)",
                 "max_marks": 27},
                {"code": "Mathematics 2", "name": "Mathematics 2", "max_marks": 27},
                {"code": "Biology", "name": "Biology", "max_marks": 27},
                {"code": "Chemistry", "name": "Chemistry", "max_marks": 27},
                {"code": "Physics", "name": "Physics", "max_marks": 27},
            ],
            # First sat in 2024. UAT-UK publishes no ESAT past or specimen
            # papers at all — only subject guides — so the years here are the
            # sittings themselves, for a student logging a test they took. The
            # practice corpus is ENGAA and NSAA, which are separate entries.
            "years": ["2024", "2025"],
            "topics": {
                "Mathematics 1": [
                    "Units", "Number", "Ratio and proportion", "Algebra",
                    "Sequences", "Graphs of functions", "Coordinate geometry",
                    "Trigonometry", "Geometry", "Statistics", "Probability",
                ],
                "Mathematics 2": [
                    "Algebra and functions", "Sequences and series",
                    "Coordinate geometry", "Trigonometry",
                    "Exponentials and logarithms", "Differentiation",
                    "Integration", "Vectors", "Proof",
                ],
                "Biology": [
                    "Cells", "Movement across membranes", "Cell division and sex determination",
                    "Inheritance", "DNA", "Gene technologies", "Variation",
                    "Enzymes", "Animal physiology", "Ecosystems", "Plant physiology",
                ],
                "Chemistry": [
                    "Atomic structure", "The Periodic Table", "Chemical reactions",
                    "Quantitative chemistry", "Oxidation and reduction",
                    "Chemical bonding, structure and properties",
                    "Group chemistry", "Separation techniques",
                    "Acids, bases and salts", "Rates of reaction",
                    "Energetics", "Electrolysis", "Organic chemistry",
                    "Metals", "Kinetic theory", "Chemical tests", "Air and water",
                ],
                "Physics": [
                    "Electricity", "Magnetism", "Mechanics", "Thermal physics",
                    "Matter", "Waves", "Radioactivity", "Subatomic physics",
                    "Units",
                ],
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

# Only a full A-level awards A*. AS is graded A-E, and the SQA Highers are
# graded A-D. A qualification's ceiling is a property of the level, not of the
# board or the subject.
LEVELS_WITH_A_STAR = {"A-Level"}

# A catalogue key is a storage identity, not a label. Two qualifications in the
# same subject and board — AQA Mathematics at A-level and at AS — need separate
# keys, because `papers`, `grade_boundaries` and `user_subjects` are all keyed
# by that string and the two have different papers and different boundaries.
# The convention is a suffixed key with a "name" field carrying what a student
# should actually read. A-level entries need neither, so they carry no suffix
# and their key is already the name.


def is_graded(board, subject):
    """Whether this qualification awards a grade Telos can predict.

    False for admissions tests. TMUA and ESAT report a 1-9 scale score, and
    ENGAA/NSAA reported raw marks against a published distribution — none of
    them has an A*-E ladder, and no amount of data would give them one. Telos
    still tracks every mark and topic; it just refuses to name a grade.

    Defaults to True, so a qualification is graded unless it says otherwise and
    a typo cannot silently turn grading off for a real A-level.
    """
    try:
        return TEMPLATES[board][subject].get("graded", True)
    except KeyError:
        return True


def ungraded_keys():
    """Every (board, subject) that is tracked but not graded."""
    return {(b, s) for b, subs in TEMPLATES.items() for s in subs
            if not subs[s].get("graded", True)}


def qualification_level(board, subject):
    """The level of one catalogue entry, defaulting to A-Level."""
    try:
        return TEMPLATES[board][subject].get("level", DEFAULT_LEVEL)
    except KeyError:
        return DEFAULT_LEVEL


def top_grade(level):
    """The highest grade this level can award: A* for an A-level, else A."""
    return "A*" if level in LEVELS_WITH_A_STAR else "A"


def has_a_star(board, subject):
    """Whether this qualification can award an A* at all."""
    return qualification_level(board, subject) in LEVELS_WITH_A_STAR


def display_name(board, subject):
    """What a student should read for this catalogue key.

    Falls back to the key, so an entry that needs no disambiguation — every
    A-level — simply doesn't carry a name.
    """
    try:
        return TEMPLATES[board][subject].get("name", subject)
    except KeyError:
        return subject


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
            level = data.get("level", DEFAULT_LEVEL)
            out.append({
                "board": board,
                # The storage identity. "name" is what a student reads; the two
                # differ only where one subject is offered at several levels.
                "subject": subject,
                "name": data.get("name", subject),
                "level": level,
                "top_grade": top_grade(level),
                "color": data["color"],
                "papers": data["papers"],
                "paper_count": len(data["papers"]),
                "mandatory": mandatory,
                "optional": optional,
                "choose_optional": data.get("choose_optional", 0),
                "years": data["years"],
            })
    return sorted(out, key=lambda q: (q["name"], LEVELS.index(q["level"])
                                      if q["level"] in LEVELS else 99, q["board"]))


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
