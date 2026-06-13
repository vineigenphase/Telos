"""
Permanent grade boundary seed data.
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
    ("Maths", "Edexcel", "Pure 1",     "2021", "June", 71, 54, 44, 34),
    ("Maths", "Edexcel", "Pure 2",     "2021", "June", 71, 54, 44, 34),
    ("Maths", "Edexcel", "Stats&Mech", "2021", "June", 65, 49, 40, 31),
    ("Maths", "Edexcel", "Pure 1",     "2020", "June", 71, 53, 42, 32),
    ("Maths", "Edexcel", "Pure 2",     "2020", "June", 71, 53, 42, 31),
    ("Maths", "Edexcel", "Stats&Mech", "2020", "June", 72, 56, 45, 34),
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
    ("Further Maths", "Edexcel", "CP1", "2021", "June", 51, 42, 33, 24),
    ("Further Maths", "Edexcel", "CP2", "2021", "June", 49, 39, 30, 22),
    ("Further Maths", "Edexcel", "CP1", "2020", "June", 57, 43, 33, 24),
    ("Further Maths", "Edexcel", "CP2", "2020", "June", 54, 40, 31, 22),
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

    ("Further Maths", "Edexcel", "FP1", "2021", "June", 53, 41, 32, 23),
    ("Further Maths", "Edexcel", "FS1", "2021", "June", 52, 43, 34, 25),
    ("Further Maths", "Edexcel", "FM1", "2021", "June", 57, 44, 35, 26),
    ("Further Maths", "Edexcel", "D1",  "2021", "June", 49, 40, 32, 24),
    ("Further Maths", "Edexcel", "FP2", "2021", "June", 50, 41, 32, 24),
    ("Further Maths", "Edexcel", "FS2", "2021", "June", 58, 46, 36, 26),
    ("Further Maths", "Edexcel", "FM2", "2021", "June", 62, 47, 37, 27),
    ("Further Maths", "Edexcel", "D2",  "2021", "June", 51, 39, 30, 21),

    ("Further Maths", "Edexcel", "FP1", "2020", "June", 55, 47, 37, 27),
    ("Further Maths", "Edexcel", "FS1", "2020", "June", 54, 46, 36, 26),
    ("Further Maths", "Edexcel", "FM1", "2020", "June", 53, 47, 37, 27),
    ("Further Maths", "Edexcel", "D1",  "2020", "June", 49, 42, 33, 24),
    ("Further Maths", "Edexcel", "FP2", "2020", "June", 57, 43, 33, 24),
    ("Further Maths", "Edexcel", "FS2", "2020", "June", 60, 47, 37, 27),
    ("Further Maths", "Edexcel", "FM2", "2020", "June", 55, 49, 39, 29),
    ("Further Maths", "Edexcel", "D2",  "2020", "June", 48, 42, 32, 23),

    ("Further Maths", "Edexcel", "FP1", "2019", "June", 62, 53, 44, 35),
    ("Further Maths", "Edexcel", "FS1", "2019", "June", 61, 52, 43, 34),
    ("Further Maths", "Edexcel", "FM1", "2019", "June", 62, 53, 44, 36),
    ("Further Maths", "Edexcel", "D1",  "2019", "June", 57, 49, 41, 33),
    ("Further Maths", "Edexcel", "FP2", "2019", "June", 59, 50, 41, 32),
    ("Further Maths", "Edexcel", "FS2", "2019", "June", 64, 55, 46, 37),
    ("Further Maths", "Edexcel", "FM2", "2019", "June", 65, 56, 47, 38),
    ("Further Maths", "Edexcel", "D2",  "2019", "June", 57, 48, 39, 30),

    # ── OCR A Level Physics A (total qualification score, out of 270) ─────────
    ("Physics", "OCR A", "Overall", "2025", "June", 270, 206, 179, 151),
    ("Physics", "OCR A", "Overall", "2024", "June", 270, 207, 175, 146),
    ("Physics", "OCR A", "Overall", "2023", "June", 270, 211, 182, 151),
    ("Physics", "OCR A", "Overall", "2022", "June", 270, 211, 181, 147),
    ("Physics", "OCR A", "Overall", "2021", "June", 270, 214, 182, 151),
    ("Physics", "OCR A", "Overall", "2020", "June", 270, 221, 192, 159),
    ("Physics", "OCR A", "Overall", "2019", "June", 270, 230, 204, 174),
    ("Physics", "OCR A", "Overall", "2018", "June", 270, 219, 188, 158),

    # ── OCR A Level Physics B — Advancing Physics (total, out of 270) ─────────
    ("Physics B", "OCR", "Overall", "2025", "June", 270, 203, 174, 145),
    ("Physics B", "OCR", "Overall", "2024", "June", 270, 194, 158, 134),
    ("Physics B", "OCR", "Overall", "2023", "June", 270, 207, 170, 141),
    ("Physics B", "OCR", "Overall", "2022", "June", 270, 177, 143, 116),
    ("Physics B", "OCR", "Overall", "2021", "June", 270, 187, 151, 127),
    ("Physics B", "OCR", "Overall", "2020", "June", 270, 194, 161, 134),
    ("Physics B", "OCR", "Overall", "2019", "June", 270, 209, 176, 148),
    ("Physics B", "OCR", "Overall", "2018", "June", 270, 206, 173, 145),
]


def seed_boundaries(db):
    """Insert all boundary rows; existing records are skipped (INSERT OR IGNORE)."""
    db.executemany(
        """INSERT OR IGNORE INTO grade_boundaries
           (subject, board, paper_code, year, series, a_star, a_boundary, b_boundary, c_boundary)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        BOUNDARY_ROWS,
    )
