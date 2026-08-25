-- 021_aqa_economics_boundaries.sql
-- AQA A-level Economics (7136), per paper.
--
-- Three compulsory papers, 80 marks each.
--
-- Notional component boundaries, derived by AQA from the qualification
-- award. The subject row out of 240 is not stored.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Economics' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Economics', 'AQA', 'Paper 1', '2018', 'June', 66, 59, 50, 42, 34, 26),
    ('Economics', 'AQA', 'Paper 2', '2018', 'June', 62, 54, 45, 37, 29, 21),
    ('Economics', 'AQA', 'Paper 3', '2018', 'June', 60, 50, 43, 37, 31, 25),
    ('Economics', 'AQA', 'Paper 1', '2019', 'June', 65, 56, 47, 39, 31, 23),
    ('Economics', 'AQA', 'Paper 2', '2019', 'June', 64, 55, 46, 37, 29, 21),
    ('Economics', 'AQA', 'Paper 3', '2019', 'June', 63, 53, 46, 39, 32, 25),
    ('Economics', 'AQA', 'Paper 1', '2022', 'June', 59, 51, 42, 33, 25, 17),
    ('Economics', 'AQA', 'Paper 2', '2022', 'June', 59, 51, 41, 31, 22, 13),
    ('Economics', 'AQA', 'Paper 3', '2022', 'June', 57, 49, 41, 34, 27, 20),
    ('Economics', 'AQA', 'Paper 1', '2023', 'June', 63, 56, 46, 37, 28, 19),
    ('Economics', 'AQA', 'Paper 2', '2023', 'June', 60, 51, 43, 35, 27, 20),
    ('Economics', 'AQA', 'Paper 3', '2023', 'June', 59, 49, 42, 35, 29, 23),
    ('Economics', 'AQA', 'Paper 1', '2024', 'June', 59, 52, 44, 36, 28, 20),
    ('Economics', 'AQA', 'Paper 2', '2024', 'June', 58, 50, 42, 34, 26, 19),
    ('Economics', 'AQA', 'Paper 3', '2024', 'June', 56, 47, 40, 34, 28, 22),
    ('Economics', 'AQA', 'Paper 1', '2025', 'June', 61, 54, 45, 36, 28, 20),
    ('Economics', 'AQA', 'Paper 2', '2025', 'June', 60, 52, 43, 34, 26, 18),
    ('Economics', 'AQA', 'Paper 3', '2025', 'June', 56, 47, 41, 35, 29, 23);
