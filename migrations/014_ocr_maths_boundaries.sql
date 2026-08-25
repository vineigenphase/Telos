-- 014_ocr_maths_boundaries.sql
-- OCR A Level Mathematics A (H240), per paper, from OCR's published PDFs.
--
--   Paper 1 = H240/01 Pure Mathematics                 (100)
--   Paper 2 = H240/02 Pure Mathematics and Statistics  (100)
--   Paper 3 = H240/03 Pure Mathematics and Mechanics   (100)
--
-- Component boundaries, not the overall 300-mark qualification figure —
-- students log one paper at a time, and storing the qualification total under a
-- paper code is what made Physics predict U for every student who tried it.
--
-- D and E are included because OCR publishes them; the columns exist from
-- migration 009.
--
-- No 2020 or 2021: no summer exam series in either year.
--
-- Idempotent: clears the subject's rows, then reinserts.

DELETE FROM grade_boundaries WHERE subject = 'Maths' AND board = 'OCR A';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Maths', 'OCR A', 'Paper 1', '2018', 'June', 83, 67, 55, 44, 33, 21),
    ('Maths', 'OCR A', 'Paper 2', '2018', 'June', 75, 61, 50, 39, 28, 18),
    ('Maths', 'OCR A', 'Paper 3', '2018', 'June', 82, 69, 57, 45, 33, 21),
    ('Maths', 'OCR A', 'Paper 1', '2019', 'June', 72, 54, 44, 34, 24, 13),
    ('Maths', 'OCR A', 'Paper 2', '2019', 'June', 76, 58, 47, 36, 25, 15),
    ('Maths', 'OCR A', 'Paper 3', '2019', 'June', 68, 49, 39, 30, 21, 12),
    ('Maths', 'OCR A', 'Paper 1', '2022', 'June', 73, 56, 44, 33, 22, 11),
    ('Maths', 'OCR A', 'Paper 2', '2022', 'June', 62, 48, 39, 30, 21, 12),
    ('Maths', 'OCR A', 'Paper 3', '2022', 'June', 58, 45, 36, 27, 18, 9),
    ('Maths', 'OCR A', 'Paper 1', '2023', 'June', 74, 58, 46, 34, 23, 12),
    ('Maths', 'OCR A', 'Paper 2', '2023', 'June', 67, 52, 42, 32, 22, 12),
    ('Maths', 'OCR A', 'Paper 3', '2023', 'June', 68, 51, 41, 31, 21, 11),
    ('Maths', 'OCR A', 'Paper 1', '2024', 'June', 73, 57, 47, 36, 26, 15),
    ('Maths', 'OCR A', 'Paper 2', '2024', 'June', 72, 56, 46, 36, 25, 15),
    ('Maths', 'OCR A', 'Paper 3', '2024', 'June', 71, 55, 44, 34, 24, 14),
    ('Maths', 'OCR A', 'Paper 1', '2025', 'June', 84, 69, 57, 46, 34, 23),
    ('Maths', 'OCR A', 'Paper 2', '2025', 'June', 83, 67, 56, 45, 34, 23),
    ('Maths', 'OCR A', 'Paper 3', '2025', 'June', 75, 60, 50, 39, 29, 18);
