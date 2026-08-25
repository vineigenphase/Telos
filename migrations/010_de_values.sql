-- 010_de_values.sql
-- The official D and E boundaries, for every row where the board publishes them.
--
-- Generated from the same OCR and Pearson PDFs as the A*/A/B/C figures, by
-- script rather than by hand. Each value was checked against the row it
-- updates: D and E must fall below that row's C boundary and stay above zero.
--
-- 39 rows updated. 0 official rows had no matching row here
-- and were skipped rather than inserted — this migration only fills in grades
-- for boundaries that already exist.
--
-- Rows left with NULL d/e keep the old behaviour: prediction.boundary_ladder
-- infers them from the mean gap, exactly as it did for every row before this.
--
-- Idempotent: re-running sets the same values.

UPDATE grade_boundaries SET d_boundary = 21, e_boundary = 12
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'CP1' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 21, e_boundary = 14
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'CP1' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 29, e_boundary = 21
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'CP1' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 21, e_boundary = 12
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'CP2' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 24, e_boundary = 17
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'CP2' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 34, e_boundary = 26
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'CP2' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 19, e_boundary = 10
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FM1' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 24, e_boundary = 17
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FM1' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 35, e_boundary = 25
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FM1' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 21, e_boundary = 11
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FS1' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 27, e_boundary = 19
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FS1' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 31, e_boundary = 25
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FS1' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 20, e_boundary = 10
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Pure 1' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 28, e_boundary = 16
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Pure 1' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 36, e_boundary = 24
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Pure 1' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 20, e_boundary = 9
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Pure 2' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 27, e_boundary = 16
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Pure 2' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 33, e_boundary = 22
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Pure 2' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 20, e_boundary = 9
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Stats&Mech' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 27, e_boundary = 15
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Stats&Mech' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 37, e_boundary = 25
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Stats&Mech' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 38, e_boundary = 27
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 1' AND year = '2018';
UPDATE grade_boundaries SET d_boundary = 48, e_boundary = 36
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 1' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 34, e_boundary = 21
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 1' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 32, e_boundary = 22
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 1' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 32, e_boundary = 22
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 1' AND year = '2024';
UPDATE grade_boundaries SET d_boundary = 36, e_boundary = 26
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 1' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 35, e_boundary = 24
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 2' AND year = '2018';
UPDATE grade_boundaries SET d_boundary = 41, e_boundary = 30
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 2' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 28, e_boundary = 16
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 2' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 34, e_boundary = 22
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 2' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 34, e_boundary = 22
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 2' AND year = '2024';
UPDATE grade_boundaries SET d_boundary = 39, e_boundary = 27
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 2' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 24, e_boundary = 17
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 3' AND year = '2018';
UPDATE grade_boundaries SET d_boundary = 25, e_boundary = 18
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 3' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 18, e_boundary = 10
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 3' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 24, e_boundary = 16
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 3' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 22, e_boundary = 15
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 3' AND year = '2024';
UPDATE grade_boundaries SET d_boundary = 21, e_boundary = 16
 WHERE subject = 'Physics' AND board = 'OCR A' AND paper_code = 'Paper 3' AND year = '2025';
