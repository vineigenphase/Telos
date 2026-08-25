-- 031_edexcel_chemistry_boundaries.sql
-- Edexcel A-level Chemistry (Chemistry), per paper.
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

DELETE FROM grade_boundaries WHERE subject = 'Chemistry' AND board = 'Edexcel';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Chemistry', 'Edexcel', 'Paper 1', '2019', 'June', 67, 56, 46, 36, 26, 16),
    ('Chemistry', 'Edexcel', 'Paper 2', '2019', 'June', 75, 63, 51, 40, 29, 18),
    ('Chemistry', 'Edexcel', 'Paper 3', '2019', 'June', 99, 83, 68, 53, 38, 23),
    ('Chemistry', 'Edexcel', 'Paper 1', '2022', 'June', 71, 58, 47, 36, 25, 14),
    ('Chemistry', 'Edexcel', 'Paper 2', '2022', 'June', 69, 56, 45, 34, 23, 13),
    ('Chemistry', 'Edexcel', 'Paper 3', '2022', 'June', 95, 78, 63, 48, 34, 20),
    ('Chemistry', 'Edexcel', 'Paper 1', '2023', 'June', 73, 59, 48, 37, 26, 16),
    ('Chemistry', 'Edexcel', 'Paper 2', '2023', 'June', 70, 57, 46, 35, 25, 15),
    ('Chemistry', 'Edexcel', 'Paper 3', '2023', 'June', 98, 79, 63, 48, 33, 18),
    ('Chemistry', 'Edexcel', 'Paper 1', '2024', 'June', 80, 67, 55, 43, 31, 20),
    ('Chemistry', 'Edexcel', 'Paper 2', '2024', 'June', 73, 63, 52, 41, 30, 19),
    ('Chemistry', 'Edexcel', 'Paper 3', '2024', 'June', 99, 86, 70, 54, 38, 22),
    ('Chemistry', 'Edexcel', 'Paper 1', '2025', 'June', 75, 66, 54, 42, 31, 20),
    ('Chemistry', 'Edexcel', 'Paper 2', '2025', 'June', 70, 59, 49, 39, 29, 19),
    ('Chemistry', 'Edexcel', 'Paper 3', '2025', 'June', 101, 82, 66, 51, 36, 21);
