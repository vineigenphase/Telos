-- 015_ocr_further_maths_boundaries.sql
-- OCR A Level Further Mathematics A (H245), per component.
--
--   Y540 Pure Core 1            (75)   mandatory
--   Y541 Pure Core 2            (75)   mandatory
--   Y542 Statistics             (75)   optional
--   Y543 Mechanics              (75)   optional
--   Y544 Discrete Mathematics   (75)   optional
--   Y545 Additional Pure Maths  (75)   optional
--
-- A student takes both Pure Core papers and two of the four options, so all six
-- are stored and the catalogue offers all six.
--
-- Component boundaries only. OCR also publishes an overall figure for each of
-- the six possible option pairings (Y540+Y541+Y542+Y543 and so on); those are
-- qualification totals out of 300 and are deliberately not stored, because a
-- student logs one 75-mark paper at a time. Storing a 300-mark total under a
-- paper code is exactly what made Physics predict U.
--
-- No 2018: reformed Further Maths was first taught in 2017 and first assessed
-- in 2019, so the series does not exist. No 2020 or 2021 either — cancelled.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Further Maths' AND board = 'OCR A';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Further Maths', 'OCR A', 'Y540', '2019', 'June', 61, 51, 43, 35, 27, 20),
    ('Further Maths', 'OCR A', 'Y541', '2019', 'June', 58, 46, 38, 30, 23, 16),
    ('Further Maths', 'OCR A', 'Y542', '2019', 'June', 63, 54, 47, 41, 35, 29),
    ('Further Maths', 'OCR A', 'Y543', '2019', 'June', 52, 42, 36, 30, 24, 18),
    ('Further Maths', 'OCR A', 'Y544', '2019', 'June', 51, 45, 38, 31, 24, 18),
    ('Further Maths', 'OCR A', 'Y545', '2019', 'June', 56, 47, 39, 31, 24, 17),
    ('Further Maths', 'OCR A', 'Y540', '2022', 'June', 50, 42, 34, 27, 20, 13),
    ('Further Maths', 'OCR A', 'Y541', '2022', 'June', 45, 36, 29, 22, 16, 10),
    ('Further Maths', 'OCR A', 'Y542', '2022', 'June', 59, 49, 39, 30, 21, 12),
    ('Further Maths', 'OCR A', 'Y543', '2022', 'June', 45, 33, 26, 20, 14, 8),
    ('Further Maths', 'OCR A', 'Y544', '2022', 'June', 49, 39, 32, 25, 18, 11),
    ('Further Maths', 'OCR A', 'Y545', '2022', 'June', 39, 29, 23, 18, 13, 8),
    ('Further Maths', 'OCR A', 'Y540', '2023', 'June', 48, 38, 31, 24, 18, 12),
    ('Further Maths', 'OCR A', 'Y541', '2023', 'June', 48, 38, 31, 25, 19, 13),
    ('Further Maths', 'OCR A', 'Y542', '2023', 'June', 52, 42, 34, 27, 20, 13),
    ('Further Maths', 'OCR A', 'Y543', '2023', 'June', 51, 40, 32, 25, 18, 11),
    ('Further Maths', 'OCR A', 'Y544', '2023', 'June', 60, 50, 41, 32, 24, 16),
    ('Further Maths', 'OCR A', 'Y545', '2023', 'June', 48, 38, 32, 26, 20, 14),
    ('Further Maths', 'OCR A', 'Y540', '2024', 'June', 56, 48, 41, 34, 27, 20),
    ('Further Maths', 'OCR A', 'Y541', '2024', 'June', 56, 47, 40, 33, 26, 20),
    ('Further Maths', 'OCR A', 'Y542', '2024', 'June', 58, 48, 40, 32, 25, 18),
    ('Further Maths', 'OCR A', 'Y543', '2024', 'June', 60, 50, 42, 34, 26, 18),
    ('Further Maths', 'OCR A', 'Y544', '2024', 'June', 56, 47, 40, 33, 26, 19),
    ('Further Maths', 'OCR A', 'Y545', '2024', 'June', 44, 35, 29, 23, 17, 11),
    ('Further Maths', 'OCR A', 'Y540', '2025', 'June', 53, 45, 38, 31, 24, 18),
    ('Further Maths', 'OCR A', 'Y541', '2025', 'June', 56, 49, 42, 35, 28, 21),
    ('Further Maths', 'OCR A', 'Y542', '2025', 'June', 62, 53, 44, 35, 26, 17),
    ('Further Maths', 'OCR A', 'Y543', '2025', 'June', 60, 51, 42, 34, 26, 18),
    ('Further Maths', 'OCR A', 'Y544', '2025', 'June', 56, 48, 39, 31, 23, 15),
    ('Further Maths', 'OCR A', 'Y545', '2025', 'June', 57, 49, 40, 31, 22, 14);
