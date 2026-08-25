-- 020_aqa_biology_boundaries.sql
-- AQA A-level Biology (7402), per paper: Paper 1 (91), Paper 2 (91), Paper 3 (78).
--
-- The three papers have different max marks, which is the detail that
-- matters here: a 78-mark paper measured against a 91-mark boundary would
-- grade every student a U. The extractor checks each component against its
-- own expected max rather than assuming a qualification's papers share one.
--
-- Notional component boundaries, derived by AQA from the qualification
-- award. The subject row out of 260 is not stored.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Biology' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Biology', 'AQA', 'Paper 1', '2018', 'June', 56, 46, 38, 30, 23, 16),
    ('Biology', 'AQA', 'Paper 2', '2018', 'June', 61, 52, 43, 35, 27, 19),
    ('Biology', 'AQA', 'Paper 3', '2018', 'June', 49, 40, 33, 27, 21, 15),
    ('Biology', 'AQA', 'Paper 1', '2019', 'June', 62, 52, 43, 35, 27, 19),
    ('Biology', 'AQA', 'Paper 2', '2019', 'June', 62, 52, 43, 34, 25, 16),
    ('Biology', 'AQA', 'Paper 3', '2019', 'June', 54, 45, 38, 31, 24, 18),
    ('Biology', 'AQA', 'Paper 1', '2022', 'June', 62, 51, 41, 31, 22, 13),
    ('Biology', 'AQA', 'Paper 2', '2022', 'June', 62, 51, 41, 31, 22, 13),
    ('Biology', 'AQA', 'Paper 3', '2022', 'June', 50, 40, 32, 25, 18, 11),
    ('Biology', 'AQA', 'Paper 1', '2023', 'June', 63, 53, 43, 34, 25, 16),
    ('Biology', 'AQA', 'Paper 2', '2023', 'June', 66, 58, 47, 36, 25, 15),
    ('Biology', 'AQA', 'Paper 3', '2023', 'June', 51, 42, 34, 27, 20, 13),
    ('Biology', 'AQA', 'Paper 1', '2024', 'June', 67, 58, 49, 40, 31, 23),
    ('Biology', 'AQA', 'Paper 2', '2024', 'June', 67, 57, 48, 39, 30, 21),
    ('Biology', 'AQA', 'Paper 3', '2024', 'June', 58, 50, 43, 36, 29, 23),
    ('Biology', 'AQA', 'Paper 1', '2025', 'June', 66, 56, 47, 38, 29, 21),
    ('Biology', 'AQA', 'Paper 2', '2025', 'June', 69, 60, 50, 40, 30, 20),
    ('Biology', 'AQA', 'Paper 3', '2025', 'June', 57, 49, 42, 35, 28, 22);
