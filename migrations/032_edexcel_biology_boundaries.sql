-- 032_edexcel_biology_boundaries.sql
-- Edexcel A-level Biology (Biology A (Salters Nuffield)), per paper.
--
-- Notional component boundaries. Pearson prints these in four different
-- layouts across the series — name and numbers on one line, split across
-- two, one number per line, and in one case a row whose paper label is
-- missing entirely. Every row is checked against its paper's expected max
-- mark, which is what makes reading four layouts safe.
--
-- No 2018 series is stored: that document was not to hand. No 2020 or 2021
-- either — no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Biology' AND board = 'Edexcel';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Biology', 'Edexcel', 'Paper 1', '2019', 'June', 73, 63, 55, 47, 39, 31),
    ('Biology', 'Edexcel', 'Paper 2', '2019', 'June', 70, 60, 52, 44, 36, 29),
    ('Biology', 'Edexcel', 'Paper 3', '2019', 'June', 61, 52, 45, 38, 31, 24),
    ('Biology', 'Edexcel', 'Paper 1', '2022', 'June', 66, 55, 45, 36, 27, 18),
    ('Biology', 'Edexcel', 'Paper 2', '2022', 'June', 56, 47, 39, 31, 23, 15),
    ('Biology', 'Edexcel', 'Paper 3', '2022', 'June', 64, 53, 43, 34, 25, 16),
    ('Biology', 'Edexcel', 'Paper 1', '2023', 'June', 79, 68, 57, 46, 35, 24),
    ('Biology', 'Edexcel', 'Paper 2', '2023', 'June', 74, 64, 54, 44, 34, 25),
    ('Biology', 'Edexcel', 'Paper 3', '2023', 'June', 69, 60, 50, 41, 32, 23),
    ('Biology', 'Edexcel', 'Paper 1', '2024', 'June', 72, 62, 51, 40, 30, 20),
    ('Biology', 'Edexcel', 'Paper 2', '2024', 'June', 69, 59, 50, 41, 33, 25),
    ('Biology', 'Edexcel', 'Paper 3', '2024', 'June', 58, 50, 42, 34, 27, 20),
    ('Biology', 'Edexcel', 'Paper 1', '2025', 'June', 79, 70, 59, 48, 38, 28),
    ('Biology', 'Edexcel', 'Paper 2', '2025', 'June', 72, 64, 56, 48, 40, 32),
    ('Biology', 'Edexcel', 'Paper 3', '2025', 'June', 74, 66, 57, 48, 40, 32);
