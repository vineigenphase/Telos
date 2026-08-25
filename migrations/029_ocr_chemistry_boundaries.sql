-- 029_ocr_chemistry_boundaries.sql
-- OCR A A-level Chemistry, per paper.
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

DELETE FROM grade_boundaries WHERE subject = 'Chemistry' AND board = 'OCR A';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Chemistry', 'OCR A', 'Paper 1', '2018', 'June', 90, 80, 66, 52, 39, 26),
    ('Chemistry', 'OCR A', 'Paper 2', '2018', 'June', 87, 73, 59, 45, 32, 19),
    ('Chemistry', 'OCR A', 'Paper 3', '2018', 'June', 60, 52, 43, 34, 25, 17),
    ('Chemistry', 'OCR A', 'Paper 1', '2019', 'June', 85, 72, 59, 46, 33, 20),
    ('Chemistry', 'OCR A', 'Paper 2', '2019', 'June', 90, 80, 67, 53, 39, 25),
    ('Chemistry', 'OCR A', 'Paper 3', '2019', 'June', 55, 44, 35, 27, 19, 11),
    ('Chemistry', 'OCR A', 'Paper 1', '2022', 'June', 78, 62, 48, 35, 22, 9),
    ('Chemistry', 'OCR A', 'Paper 2', '2022', 'June', 83, 66, 52, 38, 24, 10),
    ('Chemistry', 'OCR A', 'Paper 3', '2022', 'June', 52, 40, 32, 24, 16, 8),
    ('Chemistry', 'OCR A', 'Paper 1', '2023', 'June', 83, 71, 57, 43, 29, 15),
    ('Chemistry', 'OCR A', 'Paper 2', '2023', 'June', 90, 77, 61, 45, 30, 15),
    ('Chemistry', 'OCR A', 'Paper 3', '2023', 'June', 61, 50, 40, 30, 20, 10),
    ('Chemistry', 'OCR A', 'Paper 1', '2024', 'June', 91, 80, 66, 51, 37, 23),
    ('Chemistry', 'OCR A', 'Paper 2', '2024', 'June', 92, 81, 66, 51, 36, 21),
    ('Chemistry', 'OCR A', 'Paper 3', '2024', 'June', 60, 51, 41, 32, 23, 14),
    ('Chemistry', 'OCR A', 'Paper 1', '2025', 'June', 92, 81, 66, 52, 38, 24),
    ('Chemistry', 'OCR A', 'Paper 2', '2025', 'June', 91, 81, 66, 51, 36, 21),
    ('Chemistry', 'OCR A', 'Paper 3', '2025', 'June', 60, 51, 43, 34, 25, 16);
