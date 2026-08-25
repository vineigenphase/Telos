-- 028_ocr_biology_boundaries.sql
-- OCR A A-level Biology, per paper.
--
-- Three written papers. Component 01 assesses modules 1, 2, 3 and 5;
-- component 02 assesses 1, 2, 4 and 6; component 03 assesses all six. The
-- Practical Endorsement (component 04) is reported separately from the
-- grade and is not a written paper, so it is not stored.
--
-- Each component is checked against its own expected max mark, so a paper
-- measured against another paper's scale fails loudly instead of grading
-- every student wrongly.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Biology' AND board = 'OCR A';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Biology', 'OCR A', 'Paper 1', '2018', 'June', 76, 65, 54, 44, 34, 24),
    ('Biology', 'OCR A', 'Paper 2', '2018', 'June', 60, 51, 43, 35, 27, 20),
    ('Biology', 'OCR A', 'Paper 3', '2018', 'June', 51, 43, 37, 31, 25, 19),
    ('Biology', 'OCR A', 'Paper 1', '2019', 'June', 76, 65, 56, 47, 37, 28),
    ('Biology', 'OCR A', 'Paper 2', '2019', 'June', 61, 52, 45, 38, 31, 23),
    ('Biology', 'OCR A', 'Paper 3', '2019', 'June', 48, 41, 35, 29, 24, 19),
    ('Biology', 'OCR A', 'Paper 1', '2022', 'June', 71, 60, 50, 40, 30, 19),
    ('Biology', 'OCR A', 'Paper 2', '2022', 'June', 66, 56, 47, 38, 28, 19),
    ('Biology', 'OCR A', 'Paper 3', '2022', 'June', 47, 40, 33, 26, 20, 14),
    ('Biology', 'OCR A', 'Paper 1', '2023', 'June', 68, 58, 48, 38, 29, 20),
    ('Biology', 'OCR A', 'Paper 2', '2023', 'June', 65, 55, 46, 38, 29, 20),
    ('Biology', 'OCR A', 'Paper 3', '2023', 'June', 50, 42, 36, 30, 24, 18),
    ('Biology', 'OCR A', 'Paper 1', '2024', 'June', 71, 61, 52, 43, 33, 23),
    ('Biology', 'OCR A', 'Paper 2', '2024', 'June', 68, 58, 49, 40, 32, 24),
    ('Biology', 'OCR A', 'Paper 3', '2024', 'June', 48, 41, 35, 29, 24, 19),
    ('Biology', 'OCR A', 'Paper 1', '2025', 'June', 69, 59, 49, 40, 31, 22),
    ('Biology', 'OCR A', 'Paper 2', '2025', 'June', 69, 60, 52, 43, 35, 26),
    ('Biology', 'OCR A', 'Paper 3', '2025', 'June', 49, 42, 36, 30, 24, 19);
