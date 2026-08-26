-- 034_ocr_as_boundaries.sql
-- OCR AS-levels: Mathematics A (H230), Further Mathematics A (H235),
-- Physics A (H156), Chemistry A (H032), Biology A (H020).
--
-- a_star is NULL on every row, and that is the point: an AS-level is
-- graded A-E and has no A*. prediction.py reads the absence and stops the
-- grade ladder at A, so an AS student cannot be predicted a grade their
-- certificate has no room for.
--
-- AS components are stored under their own subject keys, suffixed (AS).
-- The AS and A-level papers of one subject share neither content nor
-- boundaries, and papers, grade_boundaries and user_subjects are all keyed
-- by subject, so the two must not collide.
--
-- Read from the AS section of each series document, which is a separate
-- table with six grade columns rather than seven. A parser that tried to
-- read both would, on a bad match, store an A boundary in the A* column.
-- Every row is checked against its component's own max mark.
--
-- Only 2022-2025: OCR published AS boundaries separately before that and
-- those documents are not to hand. No 2020 or 2021 - no summer series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE board = 'OCR A' AND subject LIKE '% (AS)';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Maths (AS)', 'OCR A', 'Paper 1', '2019', 'June', NULL, 51, 44, 37, 31, 25),
    ('Maths (AS)', 'OCR A', 'Paper 2', '2019', 'June', NULL, 49, 42, 35, 28, 21),
    ('Maths (AS)', 'OCR A', 'Paper 1', '2022', 'June', NULL, 49, 40, 32, 23, 14),
    ('Maths (AS)', 'OCR A', 'Paper 2', '2022', 'June', NULL, 45, 36, 27, 19, 11),
    ('Maths (AS)', 'OCR A', 'Paper 1', '2023', 'June', NULL, 50, 42, 35, 28, 20),
    ('Maths (AS)', 'OCR A', 'Paper 2', '2023', 'June', NULL, 46, 39, 32, 25, 19),
    ('Maths (AS)', 'OCR A', 'Paper 1', '2024', 'June', NULL, 49, 42, 36, 30, 24),
    ('Maths (AS)', 'OCR A', 'Paper 2', '2024', 'June', NULL, 46, 40, 33, 26, 19),
    ('Maths (AS)', 'OCR A', 'Paper 1', '2025', 'June', NULL, 57, 51, 45, 39, 33),
    ('Maths (AS)', 'OCR A', 'Paper 2', '2025', 'June', NULL, 50, 43, 36, 30, 24),
    ('Further Maths (AS)', 'OCR A', 'Y531', '2019', 'June', NULL, 39, 34, 30, 26, 22),
    ('Further Maths (AS)', 'OCR A', 'Y532', '2019', 'June', NULL, 38, 33, 29, 25, 21),
    ('Further Maths (AS)', 'OCR A', 'Y533', '2019', 'June', NULL, 31, 26, 21, 16, 12),
    ('Further Maths (AS)', 'OCR A', 'Y534', '2019', 'June', NULL, 34, 30, 26, 22, 19),
    ('Further Maths (AS)', 'OCR A', 'Y535', '2019', 'June', NULL, 36, 32, 28, 24, 21),
    ('Further Maths (AS)', 'OCR A', 'Y531', '2022', 'June', NULL, 38, 33, 29, 25, 21),
    ('Further Maths (AS)', 'OCR A', 'Y532', '2022', 'June', NULL, 37, 32, 28, 24, 20),
    ('Further Maths (AS)', 'OCR A', 'Y533', '2022', 'June', NULL, 36, 31, 27, 23, 19),
    ('Further Maths (AS)', 'OCR A', 'Y534', '2022', 'June', NULL, 33, 29, 25, 21, 18),
    ('Further Maths (AS)', 'OCR A', 'Y535', '2022', 'June', NULL, 35, 31, 27, 23, 20),
    ('Further Maths (AS)', 'OCR A', 'Y531', '2023', 'June', NULL, 42, 37, 32, 27, 23),
    ('Further Maths (AS)', 'OCR A', 'Y532', '2023', 'June', NULL, 37, 32, 27, 22, 17),
    ('Further Maths (AS)', 'OCR A', 'Y533', '2023', 'June', NULL, 41, 36, 31, 27, 23),
    ('Further Maths (AS)', 'OCR A', 'Y534', '2023', 'June', NULL, 36, 31, 27, 23, 19),
    ('Further Maths (AS)', 'OCR A', 'Y535', '2023', 'June', NULL, 30, 26, 22, 19, 16),
    ('Further Maths (AS)', 'OCR A', 'Y531', '2024', 'June', NULL, 38, 33, 29, 25, 21),
    ('Further Maths (AS)', 'OCR A', 'Y532', '2024', 'June', NULL, 39, 34, 29, 25, 21),
    ('Further Maths (AS)', 'OCR A', 'Y533', '2024', 'June', NULL, 42, 37, 32, 27, 23),
    ('Further Maths (AS)', 'OCR A', 'Y534', '2024', 'June', NULL, 36, 31, 26, 21, 17),
    ('Further Maths (AS)', 'OCR A', 'Y535', '2024', 'June', NULL, 31, 27, 24, 21, 18),
    ('Further Maths (AS)', 'OCR A', 'Y531', '2025', 'June', NULL, 45, 40, 35, 31, 27),
    ('Further Maths (AS)', 'OCR A', 'Y532', '2025', 'June', NULL, 43, 38, 33, 29, 25),
    ('Further Maths (AS)', 'OCR A', 'Y533', '2025', 'June', NULL, 37, 32, 27, 22, 17),
    ('Further Maths (AS)', 'OCR A', 'Y534', '2025', 'June', NULL, 37, 32, 27, 22, 18),
    ('Further Maths (AS)', 'OCR A', 'Y535', '2025', 'June', NULL, 39, 34, 29, 25, 21),
    ('Physics (AS)', 'OCR A', 'Paper 1', '2019', 'June', NULL, 49, 44, 38, 32, 27),
    ('Physics (AS)', 'OCR A', 'Paper 2', '2019', 'June', NULL, 52, 46, 41, 36, 31),
    ('Physics (AS)', 'OCR A', 'Paper 1', '2022', 'June', NULL, 46, 39, 31, 24, 16),
    ('Physics (AS)', 'OCR A', 'Paper 2', '2022', 'June', NULL, 47, 39, 32, 24, 17),
    ('Physics (AS)', 'OCR A', 'Paper 1', '2023', 'June', NULL, 47, 40, 34, 27, 21),
    ('Physics (AS)', 'OCR A', 'Paper 2', '2023', 'June', NULL, 42, 36, 30, 25, 19),
    ('Physics (AS)', 'OCR A', 'Paper 1', '2024', 'June', NULL, 53, 46, 39, 33, 27),
    ('Physics (AS)', 'OCR A', 'Paper 2', '2024', 'June', NULL, 48, 42, 36, 30, 24),
    ('Physics (AS)', 'OCR A', 'Paper 1', '2025', 'June', NULL, 52, 45, 38, 31, 25),
    ('Physics (AS)', 'OCR A', 'Paper 2', '2025', 'June', NULL, 41, 36, 31, 26, 21),
    ('Chemistry (AS)', 'OCR A', 'Paper 1', '2019', 'June', NULL, 55, 48, 42, 35, 29),
    ('Chemistry (AS)', 'OCR A', 'Paper 2', '2019', 'June', NULL, 52, 46, 39, 33, 27),
    ('Chemistry (AS)', 'OCR A', 'Paper 1', '2022', 'June', NULL, 54, 45, 37, 28, 20),
    ('Chemistry (AS)', 'OCR A', 'Paper 2', '2022', 'June', NULL, 52, 44, 35, 27, 18),
    ('Chemistry (AS)', 'OCR A', 'Paper 1', '2023', 'June', NULL, 56, 48, 41, 34, 27),
    ('Chemistry (AS)', 'OCR A', 'Paper 2', '2023', 'June', NULL, 52, 45, 37, 29, 22),
    ('Chemistry (AS)', 'OCR A', 'Paper 1', '2024', 'June', NULL, 59, 53, 47, 41, 35),
    ('Chemistry (AS)', 'OCR A', 'Paper 2', '2024', 'June', NULL, 58, 51, 44, 37, 30),
    ('Chemistry (AS)', 'OCR A', 'Paper 1', '2025', 'June', NULL, 57, 51, 44, 38, 32),
    ('Chemistry (AS)', 'OCR A', 'Paper 2', '2025', 'June', NULL, 56, 48, 41, 34, 27),
    ('Biology (AS)', 'OCR A', 'Paper 1', '2019', 'June', NULL, 47, 42, 37, 32, 27),
    ('Biology (AS)', 'OCR A', 'Paper 2', '2019', 'June', NULL, 42, 37, 32, 27, 23),
    ('Biology (AS)', 'OCR A', 'Paper 1', '2022', 'June', NULL, 39, 33, 28, 22, 16),
    ('Biology (AS)', 'OCR A', 'Paper 2', '2022', 'June', NULL, 38, 32, 26, 21, 16),
    ('Biology (AS)', 'OCR A', 'Paper 1', '2023', 'June', NULL, 41, 36, 31, 26, 21),
    ('Biology (AS)', 'OCR A', 'Paper 2', '2023', 'June', NULL, 45, 39, 33, 28, 23),
    ('Biology (AS)', 'OCR A', 'Paper 1', '2024', 'June', NULL, 45, 40, 35, 30, 25),
    ('Biology (AS)', 'OCR A', 'Paper 2', '2024', 'June', NULL, 47, 42, 37, 32, 27),
    ('Biology (AS)', 'OCR A', 'Paper 1', '2025', 'June', NULL, 44, 40, 35, 31, 26),
    ('Biology (AS)', 'OCR A', 'Paper 2', '2025', 'June', NULL, 43, 38, 34, 29, 25);
