-- 019_aqa_chemistry_boundaries.sql
-- AQA A-level Chemistry (7405), per paper: Paper 1 (105), Paper 2 (105), Paper 3 (90).
--
-- The three papers have different max marks, which is the detail that
-- matters here: a 90-mark paper measured against a 105-mark boundary would
-- grade every student a U. The extractor checks each component against its
-- own expected max rather than assuming a qualification's papers share one.
--
-- Notional component boundaries, derived by AQA from the qualification
-- award. The subject row out of 300 is not stored.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Chemistry' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Chemistry', 'AQA', 'Paper 1', '2018', 'June', 86, 72, 58, 45, 32, 19),
    ('Chemistry', 'AQA', 'Paper 2', '2018', 'June', 84, 69, 57, 45, 33, 21),
    ('Chemistry', 'AQA', 'Paper 3', '2018', 'June', 71, 57, 47, 38, 29, 20),
    ('Chemistry', 'AQA', 'Paper 1', '2019', 'June', 85, 71, 58, 45, 33, 21),
    ('Chemistry', 'AQA', 'Paper 2', '2019', 'June', 86, 72, 59, 47, 35, 23),
    ('Chemistry', 'AQA', 'Paper 3', '2019', 'June', 74, 63, 52, 41, 31, 21),
    ('Chemistry', 'AQA', 'Paper 1', '2022', 'June', 81, 65, 52, 39, 27, 15),
    ('Chemistry', 'AQA', 'Paper 2', '2022', 'June', 84, 70, 56, 43, 30, 17),
    ('Chemistry', 'AQA', 'Paper 3', '2022', 'June', 72, 61, 49, 37, 26, 15),
    ('Chemistry', 'AQA', 'Paper 1', '2023', 'June', 87, 72, 58, 45, 32, 19),
    ('Chemistry', 'AQA', 'Paper 2', '2023', 'June', 88, 75, 61, 48, 35, 22),
    ('Chemistry', 'AQA', 'Paper 3', '2023', 'June', 75, 63, 52, 41, 31, 21),
    ('Chemistry', 'AQA', 'Paper 1', '2024', 'June', 87, 74, 60, 46, 33, 20),
    ('Chemistry', 'AQA', 'Paper 2', '2024', 'June', 82, 67, 54, 42, 30, 18),
    ('Chemistry', 'AQA', 'Paper 3', '2024', 'June', 70, 57, 47, 37, 27, 17),
    ('Chemistry', 'AQA', 'Paper 1', '2025', 'June', 84, 70, 57, 44, 31, 19),
    ('Chemistry', 'AQA', 'Paper 2', '2025', 'June', 82, 66, 54, 42, 31, 20),
    ('Chemistry', 'AQA', 'Paper 3', '2025', 'June', 73, 61, 50, 40, 30, 20);
