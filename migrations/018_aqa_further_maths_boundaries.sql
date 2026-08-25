-- 018_aqa_further_maths_boundaries.sql
-- AQA A-level Further Mathematics (7367), per paper.
--
--   Paper 1  (100)  compulsory
--   Paper 2  (100)  compulsory
--   Paper 3D (50)   Discrete    | choose two
--   Paper 3M (50)   Mechanics   | of these
--   Paper 3S (50)   Statistics  | three
--
-- 100 + 100 + 50 + 50 = 300. The three optional papers are confirmed by AQA's
-- own subject rows, which are published per option pairing: 7367DS, 7367MD and
-- 7367SM. Those pairing rows are qualification totals out of 300 and are not
-- stored — a student logs one paper at a time.
--
-- Notional component boundaries, as with AQA Maths: awarded at qualification
-- level and derived per paper. The optional papers being out of 50 rather than
-- 100 is the detail worth guarding, and the extractor checks each component
-- against its own max mark rather than assuming they match.
--
-- No 2018: reformed Further Maths was first assessed in 2019.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Further Maths' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Further Maths', 'AQA', 'Paper 1', '2019', 'June', 67, 52, 42, 32, 22, 12),
    ('Further Maths', 'AQA', 'Paper 2', '2019', 'June', 69, 55, 45, 35, 26, 17),
    ('Further Maths', 'AQA', 'Paper 3D', '2019', 'June', 40, 35, 30, 25, 20, 16),
    ('Further Maths', 'AQA', 'Paper 3M', '2019', 'June', 36, 29, 23, 18, 13, 8),
    ('Further Maths', 'AQA', 'Paper 3S', '2019', 'June', 38, 33, 27, 21, 15, 9),
    ('Further Maths', 'AQA', 'Paper 1', '2022', 'June', 58, 45, 36, 27, 19, 11),
    ('Further Maths', 'AQA', 'Paper 2', '2022', 'June', 56, 43, 34, 26, 18, 10),
    ('Further Maths', 'AQA', 'Paper 3D', '2022', 'June', 35, 31, 26, 21, 16, 11),
    ('Further Maths', 'AQA', 'Paper 3M', '2022', 'June', 30, 24, 19, 14, 10, 6),
    ('Further Maths', 'AQA', 'Paper 3S', '2022', 'June', 37, 33, 26, 19, 12, 5),
    ('Further Maths', 'AQA', 'Paper 1', '2023', 'June', 75, 62, 50, 39, 28, 17),
    ('Further Maths', 'AQA', 'Paper 2', '2023', 'June', 71, 57, 46, 36, 26, 16),
    ('Further Maths', 'AQA', 'Paper 3D', '2023', 'June', 39, 33, 27, 22, 17, 12),
    ('Further Maths', 'AQA', 'Paper 3M', '2023', 'June', 29, 24, 19, 15, 11, 7),
    ('Further Maths', 'AQA', 'Paper 3S', '2023', 'June', 41, 36, 29, 22, 15, 9),
    ('Further Maths', 'AQA', 'Paper 1', '2024', 'June', 77, 64, 52, 40, 29, 18),
    ('Further Maths', 'AQA', 'Paper 2', '2024', 'June', 77, 63, 51, 40, 29, 18),
    ('Further Maths', 'AQA', 'Paper 3D', '2024', 'June', 41, 36, 30, 24, 19, 14),
    ('Further Maths', 'AQA', 'Paper 3M', '2024', 'June', 39, 33, 27, 21, 15, 10),
    ('Further Maths', 'AQA', 'Paper 3S', '2024', 'June', 42, 35, 29, 23, 17, 12),
    ('Further Maths', 'AQA', 'Paper 1', '2025', 'June', 79, 65, 54, 43, 32, 21),
    ('Further Maths', 'AQA', 'Paper 2', '2025', 'June', 79, 65, 53, 42, 31, 20),
    ('Further Maths', 'AQA', 'Paper 3D', '2025', 'June', 43, 38, 33, 28, 23, 19),
    ('Further Maths', 'AQA', 'Paper 3M', '2025', 'June', 39, 33, 28, 24, 20, 16),
    ('Further Maths', 'AQA', 'Paper 3S', '2025', 'June', 42, 36, 29, 22, 15, 9);
