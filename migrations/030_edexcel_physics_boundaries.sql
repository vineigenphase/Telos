-- 030_edexcel_physics_boundaries.sql
-- Edexcel A-level Physics (Physics), per paper.
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

DELETE FROM grade_boundaries WHERE subject = 'Physics' AND board = 'Edexcel';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Physics', 'Edexcel', 'Paper 1', '2019', 'June', 62, 53, 44, 35, 26, 18),
    ('Physics', 'Edexcel', 'Paper 2', '2019', 'June', 61, 52, 43, 34, 26, 18),
    ('Physics', 'Edexcel', 'Paper 3', '2019', 'June', 83, 71, 60, 49, 39, 29),
    ('Physics', 'Edexcel', 'Paper 1', '2022', 'June', 66, 55, 44, 34, 24, 14),
    ('Physics', 'Edexcel', 'Paper 2', '2022', 'June', 62, 52, 42, 32, 23, 14),
    ('Physics', 'Edexcel', 'Paper 3', '2022', 'June', 80, 67, 56, 45, 34, 24),
    ('Physics', 'Edexcel', 'Paper 1', '2023', 'June', 69, 59, 48, 38, 28, 18),
    ('Physics', 'Edexcel', 'Paper 2', '2023', 'June', 62, 53, 44, 35, 26, 17),
    ('Physics', 'Edexcel', 'Paper 3', '2023', 'June', 92, 78, 65, 52, 39, 27),
    ('Physics', 'Edexcel', 'Paper 1', '2024', 'June', 70, 60, 49, 38, 28, 18),
    ('Physics', 'Edexcel', 'Paper 2', '2024', 'June', 68, 59, 49, 39, 29, 20),
    ('Physics', 'Edexcel', 'Paper 3', '2024', 'June', 93, 80, 67, 54, 42, 30),
    ('Physics', 'Edexcel', 'Paper 1', '2025', 'June', 68, 60, 51, 42, 33, 25),
    ('Physics', 'Edexcel', 'Paper 2', '2025', 'June', 68, 59, 50, 41, 33, 25),
    ('Physics', 'Edexcel', 'Paper 3', '2025', 'June', 91, 80, 67, 54, 42, 30);
