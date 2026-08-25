"""
Permanent grade boundary seed data.

Only real exam series appear here. Summer 2020 and 2021 were cancelled in
England — grades came from centre and teacher assessment — so no boundaries
were published for them, and rows for those years used to be seeded anyway.
An attempt at a 2020 or 2021 paper falls back to the median of the real years,
which is the honest answer. See migrations/008_drop_cancelled_series.sql.
Called once from init_db() — uses INSERT OR IGNORE so existing records are never overwritten.
"""

BOUNDARY_ROWS = [
    # (subject, board, paper_code, year, series, a_star, a, b, c)

    # ── Edexcel A Level Maths ─────────────────────────────────────────────────
    ("Maths", "Edexcel", "Pure 1",     "2025", "June", 88, 74, 61, 48),
    ("Maths", "Edexcel", "Pure 2",     "2025", "June", 83, 67, 55, 44),
    ("Maths", "Edexcel", "Stats&Mech", "2025", "June", 87, 73, 61, 49),
    ("Maths", "Edexcel", "Pure 1",     "2024", "June", 81, 66, 53, 40),
    ("Maths", "Edexcel", "Pure 2",     "2024", "June", 81, 65, 53, 42),
    ("Maths", "Edexcel", "Stats&Mech", "2024", "June", 89, 74, 60, 46),
    ("Maths", "Edexcel", "Pure 1",     "2023", "June", 82, 67, 54, 41),
    ("Maths", "Edexcel", "Pure 2",     "2023", "June", 80, 63, 51, 39),
    ("Maths", "Edexcel", "Stats&Mech", "2023", "June", 82, 66, 53, 40),
    ("Maths", "Edexcel", "Pure 1",     "2022", "June", 70, 53, 42, 31),
    ("Maths", "Edexcel", "Pure 2",     "2022", "June", 73, 55, 43, 31),
    ("Maths", "Edexcel", "Stats&Mech", "2022", "June", 74, 56, 44, 32),
    ("Maths", "Edexcel", "Pure 1",     "2019", "June", 74, 56, 45, 35),
    ("Maths", "Edexcel", "Pure 2",     "2019", "June", 68, 52, 42, 32),
    ("Maths", "Edexcel", "Stats&Mech", "2019", "June", 75, 57, 46, 35),

    # ── Edexcel Further Maths — Core Pure ────────────────────────────────────
    ("Further Maths", "Edexcel", "CP1", "2025", "June", 62, 53, 45, 37),
    ("Further Maths", "Edexcel", "CP2", "2025", "June", 70, 61, 52, 43),
    ("Further Maths", "Edexcel", "CP1", "2024", "June", 67, 60, 51, 42),
    ("Further Maths", "Edexcel", "CP2", "2024", "June", 63, 56, 48, 40),
    ("Further Maths", "Edexcel", "CP1", "2023", "June", 51, 43, 35, 28),
    ("Further Maths", "Edexcel", "CP2", "2023", "June", 56, 46, 38, 31),
    ("Further Maths", "Edexcel", "CP1", "2022", "June", 61, 51, 41, 31),
    ("Further Maths", "Edexcel", "CP2", "2022", "June", 60, 50, 40, 30),
    ("Further Maths", "Edexcel", "CP1", "2019", "June", 58, 49, 40, 31),
    ("Further Maths", "Edexcel", "CP2", "2019", "June", 57, 45, 37, 29),

    # ── Edexcel Further Maths — Modules ──────────────────────────────────────
    # FP1 = Further Pure 1, FS1 = Further Statistics 1, FM1 = Further Mechanics 1
    # D1 = Decision 1, FP2 = Further Pure 2, FS2 = Further Statistics 2
    # FM2 = Further Mechanics 2, D2 = Decision 2
    ("Further Maths", "Edexcel", "FP1", "2025", "June", 62, 57, 47, 38),
    ("Further Maths", "Edexcel", "FS1", "2025", "June", 58, 51, 44, 37),
    ("Further Maths", "Edexcel", "FM1", "2025", "June", 72, 68, 57, 46),
    ("Further Maths", "Edexcel", "D1",  "2025", "June", 52, 46, 38, 30),
    ("Further Maths", "Edexcel", "FP2", "2025", "June", 68, 62, 50, 39),
    ("Further Maths", "Edexcel", "FS2", "2025", "June", 54, 50, 43, 36),
    ("Further Maths", "Edexcel", "FM2", "2025", "June", 58, 51, 43, 35),
    ("Further Maths", "Edexcel", "D2",  "2025", "June", 57, 52, 42, 33),

    ("Further Maths", "Edexcel", "FP1", "2024", "June", 72, 69, 55, 41),
    ("Further Maths", "Edexcel", "FS1", "2024", "June", 58, 49, 41, 33),
    ("Further Maths", "Edexcel", "FM1", "2024", "June", 68, 61, 51, 41),
    ("Further Maths", "Edexcel", "D1",  "2024", "June", 51, 41, 33, 25),
    ("Further Maths", "Edexcel", "FP2", "2024", "June", 67, 55, 45, 35),
    ("Further Maths", "Edexcel", "FS2", "2024", "June", 53, 47, 39, 31),
    ("Further Maths", "Edexcel", "FM2", "2024", "June", 56, 48, 40, 32),
    ("Further Maths", "Edexcel", "D2",  "2024", "June", 62, 57, 46, 36),

    ("Further Maths", "Edexcel", "FP1", "2023", "June", 64, 60, 50, 40),
    ("Further Maths", "Edexcel", "FS1", "2023", "June", 60, 52, 43, 35),
    ("Further Maths", "Edexcel", "FM1", "2023", "June", 58, 48, 40, 32),
    ("Further Maths", "Edexcel", "D1",  "2023", "June", 60, 46, 38, 30),
    ("Further Maths", "Edexcel", "FP2", "2023", "June", 60, 50, 41, 32),
    ("Further Maths", "Edexcel", "FS2", "2023", "June", 60, 53, 43, 34),
    ("Further Maths", "Edexcel", "FM2", "2023", "June", 67, 56, 47, 38),
    ("Further Maths", "Edexcel", "D2",  "2023", "June", 63, 53, 43, 33),

    ("Further Maths", "Edexcel", "FP1", "2022", "June", 65, 54, 43, 32),
    ("Further Maths", "Edexcel", "FS1", "2022", "June", 61, 51, 41, 31),
    ("Further Maths", "Edexcel", "FM1", "2022", "June", 58, 48, 38, 28),
    ("Further Maths", "Edexcel", "D1",  "2022", "June", 55, 46, 38, 30),
    ("Further Maths", "Edexcel", "FP2", "2022", "June", 65, 54, 43, 33),
    ("Further Maths", "Edexcel", "FS2", "2022", "June", 59, 49, 39, 30),
    ("Further Maths", "Edexcel", "FM2", "2022", "June", 58, 48, 38, 29),
    ("Further Maths", "Edexcel", "D2",  "2022", "June", 54, 45, 36, 27),



    ("Further Maths", "Edexcel", "FP1", "2019", "June", 62, 53, 44, 35),
    ("Further Maths", "Edexcel", "FS1", "2019", "June", 61, 52, 43, 34),
    ("Further Maths", "Edexcel", "FM1", "2019", "June", 62, 53, 44, 36),
    ("Further Maths", "Edexcel", "D1",  "2019", "June", 57, 49, 41, 33),
    ("Further Maths", "Edexcel", "FP2", "2019", "June", 59, 50, 41, 32),
    ("Further Maths", "Edexcel", "FS2", "2019", "June", 64, 55, 46, 37),
    ("Further Maths", "Edexcel", "FM2", "2019", "June", 65, 56, 47, 38),
    ("Further Maths", "Edexcel", "D2",  "2019", "June", 57, 48, 39, 30),

    # ── AQA A-level French (7652), German (7662), Spanish (7692) ─────────────
    # Paper 1 (100) and Paper 2 (80), RAW boundaries — AQA scales both and
    # publishes a scaled row too. Speaking is an oral and is not tracked.
    ("French", "AQA", "Paper 1", "2018", "June", 87, 75, 65, 56),
    ("French", "AQA", "Paper 2", "2018", "June", 72, 64, 54, 45),
    ("French", "AQA", "Paper 1", "2019", "June", 89, 80, 69, 58),
    ("French", "AQA", "Paper 2", "2019", "June", 71, 63, 53, 44),
    ("French", "AQA", "Paper 1", "2022", "June", 85, 75, 64, 53),
    ("French", "AQA", "Paper 2", "2022", "June", 63, 52, 42, 33),
    ("French", "AQA", "Paper 1", "2023", "June", 91, 82, 70, 58),
    ("French", "AQA", "Paper 2", "2023", "June", 70, 60, 50, 40),
    ("French", "AQA", "Paper 1", "2024", "June", 92, 85, 75, 65),
    ("French", "AQA", "Paper 2", "2024", "June", 68, 59, 49, 40),
    ("French", "AQA", "Paper 1", "2025", "June", 91, 82, 73, 64),
    ("French", "AQA", "Paper 2", "2025", "June", 71, 62, 53, 44),

    ("German", "AQA", "Paper 1", "2018", "June", 85, 67, 55, 43),
    ("German", "AQA", "Paper 2", "2018", "June", 67, 51, 42, 33),
    ("German", "AQA", "Paper 1", "2019", "June", 82, 66, 54, 42),
    ("German", "AQA", "Paper 2", "2019", "June", 66, 54, 44, 34),
    ("German", "AQA", "Paper 1", "2022", "June", 81, 64, 52, 40),
    ("German", "AQA", "Paper 2", "2022", "June", 61, 43, 35, 27),
    ("German", "AQA", "Paper 1", "2023", "June", 87, 72, 57, 43),
    ("German", "AQA", "Paper 2", "2023", "June", 67, 52, 41, 30),
    ("German", "AQA", "Paper 1", "2024", "June", 89, 78, 66, 54),
    ("German", "AQA", "Paper 2", "2024", "June", 65, 52, 42, 32),
    ("German", "AQA", "Paper 1", "2025", "June", 89, 78, 66, 54),
    ("German", "AQA", "Paper 2", "2025", "June", 66, 54, 44, 34),

    ("Spanish", "AQA", "Paper 1", "2018", "June", 86, 76, 64, 52),
    ("Spanish", "AQA", "Paper 2", "2018", "June", 68, 59, 49, 39),
    ("Spanish", "AQA", "Paper 1", "2019", "June", 82, 70, 58, 46),
    ("Spanish", "AQA", "Paper 2", "2019", "June", 68, 60, 49, 38),
    ("Spanish", "AQA", "Paper 1", "2022", "June", 80, 68, 55, 42),
    ("Spanish", "AQA", "Paper 2", "2022", "June", 64, 54, 44, 34),
    ("Spanish", "AQA", "Paper 1", "2023", "June", 87, 77, 63, 49),
    ("Spanish", "AQA", "Paper 2", "2023", "June", 67, 57, 46, 36),
    ("Spanish", "AQA", "Paper 1", "2024", "June", 86, 75, 62, 49),
    ("Spanish", "AQA", "Paper 2", "2024", "June", 66, 57, 46, 35),
    ("Spanish", "AQA", "Paper 1", "2025", "June", 89, 81, 68, 56),
    ("Spanish", "AQA", "Paper 2", "2025", "June", 65, 55, 46, 37),

    # ── AQA A-level Economics (7136) and Geography (7037) ────────────────────
    # Economics: three 80-mark papers. Geography: two 120-mark papers; the
    # fieldwork investigation is coursework and is not tracked.
    ("Economics", "AQA", "Paper 1", "2018", "June", 66, 59, 50, 42),
    ("Economics", "AQA", "Paper 2", "2018", "June", 62, 54, 45, 37),
    ("Economics", "AQA", "Paper 3", "2018", "June", 60, 50, 43, 37),
    ("Economics", "AQA", "Paper 1", "2019", "June", 65, 56, 47, 39),
    ("Economics", "AQA", "Paper 2", "2019", "June", 64, 55, 46, 37),
    ("Economics", "AQA", "Paper 3", "2019", "June", 63, 53, 46, 39),
    ("Economics", "AQA", "Paper 1", "2022", "June", 59, 51, 42, 33),
    ("Economics", "AQA", "Paper 2", "2022", "June", 59, 51, 41, 31),
    ("Economics", "AQA", "Paper 3", "2022", "June", 57, 49, 41, 34),
    ("Economics", "AQA", "Paper 1", "2023", "June", 63, 56, 46, 37),
    ("Economics", "AQA", "Paper 2", "2023", "June", 60, 51, 43, 35),
    ("Economics", "AQA", "Paper 3", "2023", "June", 59, 49, 42, 35),
    ("Economics", "AQA", "Paper 1", "2024", "June", 59, 52, 44, 36),
    ("Economics", "AQA", "Paper 2", "2024", "June", 58, 50, 42, 34),
    ("Economics", "AQA", "Paper 3", "2024", "June", 56, 47, 40, 34),
    ("Economics", "AQA", "Paper 1", "2025", "June", 61, 54, 45, 36),
    ("Economics", "AQA", "Paper 2", "2025", "June", 60, 52, 43, 34),
    ("Economics", "AQA", "Paper 3", "2025", "June", 56, 47, 41, 35),

    ("Geography", "AQA", "Paper 1", "2018", "June", 86, 72, 61, 50),
    ("Geography", "AQA", "Paper 2", "2018", "June", 88, 74, 62, 50),
    ("Geography", "AQA", "Paper 1", "2019", "June", 93, 80, 69, 58),
    ("Geography", "AQA", "Paper 2", "2019", "June", 90, 75, 64, 53),
    ("Geography", "AQA", "Paper 1", "2022", "June", 86, 72, 60, 48),
    ("Geography", "AQA", "Paper 2", "2022", "June", 92, 81, 69, 57),
    ("Geography", "AQA", "Paper 1", "2023", "June", 95, 83, 70, 57),
    ("Geography", "AQA", "Paper 2", "2023", "June", 92, 78, 65, 53),
    ("Geography", "AQA", "Paper 1", "2024", "June", 93, 80, 69, 58),
    ("Geography", "AQA", "Paper 2", "2024", "June", 94, 82, 69, 56),
    ("Geography", "AQA", "Paper 1", "2025", "June", 94, 81, 70, 59),
    ("Geography", "AQA", "Paper 2", "2025", "June", 95, 83, 71, 60),

    # ── AQA A-level Chemistry (7405) and Biology (7402) ──────────────────────
    # Three compulsory papers each, with different max marks per paper:
    # Chemistry 105/105/90, Biology 91/91/78.
    ("Chemistry", "AQA", "Paper 1", "2018", "June", 86, 72, 58, 45),
    ("Chemistry", "AQA", "Paper 2", "2018", "June", 84, 69, 57, 45),
    ("Chemistry", "AQA", "Paper 3", "2018", "June", 71, 57, 47, 38),
    ("Chemistry", "AQA", "Paper 1", "2019", "June", 85, 71, 58, 45),
    ("Chemistry", "AQA", "Paper 2", "2019", "June", 86, 72, 59, 47),
    ("Chemistry", "AQA", "Paper 3", "2019", "June", 74, 63, 52, 41),
    ("Chemistry", "AQA", "Paper 1", "2022", "June", 81, 65, 52, 39),
    ("Chemistry", "AQA", "Paper 2", "2022", "June", 84, 70, 56, 43),
    ("Chemistry", "AQA", "Paper 3", "2022", "June", 72, 61, 49, 37),
    ("Chemistry", "AQA", "Paper 1", "2023", "June", 87, 72, 58, 45),
    ("Chemistry", "AQA", "Paper 2", "2023", "June", 88, 75, 61, 48),
    ("Chemistry", "AQA", "Paper 3", "2023", "June", 75, 63, 52, 41),
    ("Chemistry", "AQA", "Paper 1", "2024", "June", 87, 74, 60, 46),
    ("Chemistry", "AQA", "Paper 2", "2024", "June", 82, 67, 54, 42),
    ("Chemistry", "AQA", "Paper 3", "2024", "June", 70, 57, 47, 37),
    ("Chemistry", "AQA", "Paper 1", "2025", "June", 84, 70, 57, 44),
    ("Chemistry", "AQA", "Paper 2", "2025", "June", 82, 66, 54, 42),
    ("Chemistry", "AQA", "Paper 3", "2025", "June", 73, 61, 50, 40),

    ("Biology", "AQA", "Paper 1", "2018", "June", 56, 46, 38, 30),
    ("Biology", "AQA", "Paper 2", "2018", "June", 61, 52, 43, 35),
    ("Biology", "AQA", "Paper 3", "2018", "June", 49, 40, 33, 27),
    ("Biology", "AQA", "Paper 1", "2019", "June", 62, 52, 43, 35),
    ("Biology", "AQA", "Paper 2", "2019", "June", 62, 52, 43, 34),
    ("Biology", "AQA", "Paper 3", "2019", "June", 54, 45, 38, 31),
    ("Biology", "AQA", "Paper 1", "2022", "June", 62, 51, 41, 31),
    ("Biology", "AQA", "Paper 2", "2022", "June", 62, 51, 41, 31),
    ("Biology", "AQA", "Paper 3", "2022", "June", 50, 40, 32, 25),
    ("Biology", "AQA", "Paper 1", "2023", "June", 63, 53, 43, 34),
    ("Biology", "AQA", "Paper 2", "2023", "June", 66, 58, 47, 36),
    ("Biology", "AQA", "Paper 3", "2023", "June", 51, 42, 34, 27),
    ("Biology", "AQA", "Paper 1", "2024", "June", 67, 58, 49, 40),
    ("Biology", "AQA", "Paper 2", "2024", "June", 67, 57, 48, 39),
    ("Biology", "AQA", "Paper 3", "2024", "June", 58, 50, 43, 36),
    ("Biology", "AQA", "Paper 1", "2025", "June", 66, 56, 47, 38),
    ("Biology", "AQA", "Paper 2", "2025", "June", 69, 60, 50, 40),
    ("Biology", "AQA", "Paper 3", "2025", "June", 57, 49, 42, 35),

    # ── AQA A-level Further Mathematics (7367) — notional components ─────────
    # Papers 1 and 2 compulsory (100 each); two 50-mark options from
    # Discrete / Mechanics / Statistics. First assessed 2019.
    ("Further Maths", "AQA", "Paper 1", "2019", "June", 67, 52, 42, 32),
    ("Further Maths", "AQA", "Paper 2", "2019", "June", 69, 55, 45, 35),
    ("Further Maths", "AQA", "Paper 3D", "2019", "June", 40, 35, 30, 25),
    ("Further Maths", "AQA", "Paper 3M", "2019", "June", 36, 29, 23, 18),
    ("Further Maths", "AQA", "Paper 3S", "2019", "June", 38, 33, 27, 21),
    ("Further Maths", "AQA", "Paper 1", "2022", "June", 58, 45, 36, 27),
    ("Further Maths", "AQA", "Paper 2", "2022", "June", 56, 43, 34, 26),
    ("Further Maths", "AQA", "Paper 3D", "2022", "June", 35, 31, 26, 21),
    ("Further Maths", "AQA", "Paper 3M", "2022", "June", 30, 24, 19, 14),
    ("Further Maths", "AQA", "Paper 3S", "2022", "June", 37, 33, 26, 19),
    ("Further Maths", "AQA", "Paper 1", "2023", "June", 75, 62, 50, 39),
    ("Further Maths", "AQA", "Paper 2", "2023", "June", 71, 57, 46, 36),
    ("Further Maths", "AQA", "Paper 3D", "2023", "June", 39, 33, 27, 22),
    ("Further Maths", "AQA", "Paper 3M", "2023", "June", 29, 24, 19, 15),
    ("Further Maths", "AQA", "Paper 3S", "2023", "June", 41, 36, 29, 22),
    ("Further Maths", "AQA", "Paper 1", "2024", "June", 77, 64, 52, 40),
    ("Further Maths", "AQA", "Paper 2", "2024", "June", 77, 63, 51, 40),
    ("Further Maths", "AQA", "Paper 3D", "2024", "June", 41, 36, 30, 24),
    ("Further Maths", "AQA", "Paper 3M", "2024", "June", 39, 33, 27, 21),
    ("Further Maths", "AQA", "Paper 3S", "2024", "June", 42, 35, 29, 23),
    ("Further Maths", "AQA", "Paper 1", "2025", "June", 79, 65, 54, 43),
    ("Further Maths", "AQA", "Paper 2", "2025", "June", 79, 65, 53, 42),
    ("Further Maths", "AQA", "Paper 3D", "2025", "June", 43, 38, 33, 28),
    ("Further Maths", "AQA", "Paper 3M", "2025", "June", 39, 33, 28, 24),
    ("Further Maths", "AQA", "Paper 3S", "2025", "June", 42, 36, 29, 22),

    # ── AQA A-level Mathematics (7357) — notional component boundaries ───────
    # Three 100-mark papers. AQA awards at qualification level and derives the
    # per-paper figures, which is why some series are evenly spaced.
    ("Maths", "AQA", "Paper 1", "2018", "June", 74, 56, 50, 44),
    ("Maths", "AQA", "Paper 2", "2018", "June", 79, 65, 56, 47),
    ("Maths", "AQA", "Paper 3", "2018", "June", 76, 60, 52, 44),
    ("Maths", "AQA", "Paper 1", "2019", "June", 72, 53, 43, 33),
    ("Maths", "AQA", "Paper 2", "2019", "June", 77, 62, 50, 38),
    ("Maths", "AQA", "Paper 3", "2019", "June", 82, 70, 57, 45),
    ("Maths", "AQA", "Paper 1", "2022", "June", 71, 53, 42, 32),
    ("Maths", "AQA", "Paper 2", "2022", "June", 73, 56, 45, 35),
    ("Maths", "AQA", "Paper 3", "2022", "June", 76, 62, 50, 38),
    ("Maths", "AQA", "Paper 1", "2023", "June", 82, 65, 52, 39),
    ("Maths", "AQA", "Paper 2", "2023", "June", 80, 62, 50, 38),
    ("Maths", "AQA", "Paper 3", "2023", "June", 86, 74, 60, 46),
    ("Maths", "AQA", "Paper 1", "2024", "June", 87, 75, 61, 48),
    ("Maths", "AQA", "Paper 2", "2024", "June", 84, 70, 58, 47),
    ("Maths", "AQA", "Paper 3", "2024", "June", 88, 77, 64, 51),
    ("Maths", "AQA", "Paper 1", "2025", "June", 87, 74, 61, 48),
    ("Maths", "AQA", "Paper 2", "2025", "June", 86, 73, 61, 49),
    ("Maths", "AQA", "Paper 3", "2025", "June", 87, 74, 61, 48),

    # ── OCR A Level Further Mathematics A (H245) — per component ─────────────
    # Y540/Y541 Pure Core (mandatory), Y542-Y545 options. All 75 marks.
    # First assessed 2019.
    ("Further Maths", "OCR A", "Y540", "2019", "June", 61, 51, 43, 35),
    ("Further Maths", "OCR A", "Y541", "2019", "June", 58, 46, 38, 30),
    ("Further Maths", "OCR A", "Y542", "2019", "June", 63, 54, 47, 41),
    ("Further Maths", "OCR A", "Y543", "2019", "June", 52, 42, 36, 30),
    ("Further Maths", "OCR A", "Y544", "2019", "June", 51, 45, 38, 31),
    ("Further Maths", "OCR A", "Y545", "2019", "June", 56, 47, 39, 31),
    ("Further Maths", "OCR A", "Y540", "2022", "June", 50, 42, 34, 27),
    ("Further Maths", "OCR A", "Y541", "2022", "June", 45, 36, 29, 22),
    ("Further Maths", "OCR A", "Y542", "2022", "June", 59, 49, 39, 30),
    ("Further Maths", "OCR A", "Y543", "2022", "June", 45, 33, 26, 20),
    ("Further Maths", "OCR A", "Y544", "2022", "June", 49, 39, 32, 25),
    ("Further Maths", "OCR A", "Y545", "2022", "June", 39, 29, 23, 18),
    ("Further Maths", "OCR A", "Y540", "2023", "June", 48, 38, 31, 24),
    ("Further Maths", "OCR A", "Y541", "2023", "June", 48, 38, 31, 25),
    ("Further Maths", "OCR A", "Y542", "2023", "June", 52, 42, 34, 27),
    ("Further Maths", "OCR A", "Y543", "2023", "June", 51, 40, 32, 25),
    ("Further Maths", "OCR A", "Y544", "2023", "June", 60, 50, 41, 32),
    ("Further Maths", "OCR A", "Y545", "2023", "June", 48, 38, 32, 26),
    ("Further Maths", "OCR A", "Y540", "2024", "June", 56, 48, 41, 34),
    ("Further Maths", "OCR A", "Y541", "2024", "June", 56, 47, 40, 33),
    ("Further Maths", "OCR A", "Y542", "2024", "June", 58, 48, 40, 32),
    ("Further Maths", "OCR A", "Y543", "2024", "June", 60, 50, 42, 34),
    ("Further Maths", "OCR A", "Y544", "2024", "June", 56, 47, 40, 33),
    ("Further Maths", "OCR A", "Y545", "2024", "June", 44, 35, 29, 23),
    ("Further Maths", "OCR A", "Y540", "2025", "June", 53, 45, 38, 31),
    ("Further Maths", "OCR A", "Y541", "2025", "June", 56, 49, 42, 35),
    ("Further Maths", "OCR A", "Y542", "2025", "June", 62, 53, 44, 35),
    ("Further Maths", "OCR A", "Y543", "2025", "June", 60, 51, 42, 34),
    ("Further Maths", "OCR A", "Y544", "2025", "June", 56, 48, 39, 31),
    ("Further Maths", "OCR A", "Y545", "2025", "June", 57, 49, 40, 31),

    # ── OCR A Level Mathematics A (H240) — per paper, official raw marks ─────
    # Paper 1 = H240/01 (100), Paper 2 = H240/02 (100), Paper 3 = H240/03 (100).
    # Component boundaries, not the 300-mark qualification total.
    ("Maths", "OCR A", "Paper 1", "2018", "June", 83, 67, 55, 44),
    ("Maths", "OCR A", "Paper 2", "2018", "June", 75, 61, 50, 39),
    ("Maths", "OCR A", "Paper 3", "2018", "June", 82, 69, 57, 45),
    ("Maths", "OCR A", "Paper 1", "2019", "June", 72, 54, 44, 34),
    ("Maths", "OCR A", "Paper 2", "2019", "June", 76, 58, 47, 36),
    ("Maths", "OCR A", "Paper 3", "2019", "June", 68, 49, 39, 30),
    ("Maths", "OCR A", "Paper 1", "2022", "June", 73, 56, 44, 33),
    ("Maths", "OCR A", "Paper 2", "2022", "June", 62, 48, 39, 30),
    ("Maths", "OCR A", "Paper 3", "2022", "June", 58, 45, 36, 27),
    ("Maths", "OCR A", "Paper 1", "2023", "June", 74, 58, 46, 34),
    ("Maths", "OCR A", "Paper 2", "2023", "June", 67, 52, 42, 32),
    ("Maths", "OCR A", "Paper 3", "2023", "June", 68, 51, 41, 31),
    ("Maths", "OCR A", "Paper 1", "2024", "June", 73, 57, 47, 36),
    ("Maths", "OCR A", "Paper 2", "2024", "June", 72, 56, 46, 36),
    ("Maths", "OCR A", "Paper 3", "2024", "June", 71, 55, 44, 34),
    ("Maths", "OCR A", "Paper 1", "2025", "June", 84, 69, 57, 46),
    ("Maths", "OCR A", "Paper 2", "2025", "June", 83, 67, 56, 45),
    ("Maths", "OCR A", "Paper 3", "2025", "June", 75, 60, 50, 39),

    # ── OCR A Level Physics A (H556) — per paper, official raw marks ─────────
    # Paper 1 = H556/01 Modelling physics (100), Paper 2 = H556/02 Exploring
    # physics (100), Paper 3 = H556/03 Unified physics (70). Taken from OCR's
    # published boundary PDFs.
    #
    # These were previously the OVERALL qualification boundaries (out of 270)
    # stored under paper_code "Overall", and shifted a column besides — the max
    # mark sat in a_star, so A* read 270 in every year and everything else was
    # one grade too generous. Students log one paper at a time, so a 60/100
    # Paper 1 was measured against a 270-mark scale and came out U. See
    # migrations/007_physics_boundaries.sql.
    #
    # No 2020 or 2021: there was no summer exam series in either year, so no
    # official boundaries exist. An attempt at one of those papers falls back to
    # the median of the real years.
    ("Physics", "OCR A", "Paper 1", "2018", "June", 83, 72, 60, 49),
    ("Physics", "OCR A", "Paper 2", "2018", "June", 81, 69, 57, 46),
    ("Physics", "OCR A", "Paper 3", "2018", "June", 55, 47, 39, 31),
    ("Physics", "OCR A", "Paper 1", "2019", "June", 88, 80, 70, 59),
    ("Physics", "OCR A", "Paper 2", "2019", "June", 87, 77, 65, 53),
    ("Physics", "OCR A", "Paper 3", "2019", "June", 55, 47, 39, 32),
    ("Physics", "OCR A", "Paper 1", "2022", "June", 83, 73, 60, 47),
    ("Physics", "OCR A", "Paper 2", "2022", "June", 79, 67, 54, 41),
    ("Physics", "OCR A", "Paper 3", "2022", "June", 49, 41, 33, 25),
    ("Physics", "OCR A", "Paper 1", "2023", "June", 74, 65, 54, 43),
    ("Physics", "OCR A", "Paper 2", "2023", "June", 81, 69, 57, 45),
    ("Physics", "OCR A", "Paper 3", "2023", "June", 56, 48, 40, 32),
    ("Physics", "OCR A", "Paper 1", "2024", "June", 72, 63, 52, 42),
    ("Physics", "OCR A", "Paper 2", "2024", "June", 84, 70, 58, 46),
    ("Physics", "OCR A", "Paper 3", "2024", "June", 51, 42, 36, 29),
    ("Physics", "OCR A", "Paper 1", "2025", "June", 75, 66, 56, 46),
    ("Physics", "OCR A", "Paper 2", "2025", "June", 84, 74, 62, 50),
    ("Physics", "OCR A", "Paper 3", "2025", "June", 47, 39, 33, 27),
]


def seed_boundaries(db):
    """Insert all boundary rows; existing records are skipped (ON CONFLICT DO NOTHING)."""
    db.executemany(
        """INSERT INTO grade_boundaries
           (subject, board, paper_code, year, series, a_star, a_boundary, b_boundary, c_boundary)
           VALUES (?,?,?,?,?,?,?,?,?)
           ON CONFLICT DO NOTHING""",
        BOUNDARY_ROWS,
    )
