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
