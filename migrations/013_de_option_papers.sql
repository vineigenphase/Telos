-- 013_de_option_papers.sql
-- Official D and E for the Edexcel Further Maths option papers.
--
-- Migration 010 filled only the four papers the catalogue offered at the time.
-- All ten are selectable now, so the remaining six get their published values.
--
-- Each row's official A, B and C were re-read and had to match what is already
-- stored before D/E were written; a mis-parse writes nothing.
--
-- 24 rows. Idempotent.

UPDATE grade_boundaries SET d_boundary = 26, e_boundary = 19
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'D1' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 22, e_boundary = 14
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'D1' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 23, e_boundary = 16
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'D1' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 22, e_boundary = 14
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'D1' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 22, e_boundary = 14
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'D2' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 18, e_boundary = 10
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'D2' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 23, e_boundary = 14
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'D2' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 24, e_boundary = 15
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'D2' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 29, e_boundary = 20
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FM2' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 20, e_boundary = 11
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FM2' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 29, e_boundary = 20
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FM2' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 27, e_boundary = 19
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FM2' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 27, e_boundary = 19
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FP1' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 22, e_boundary = 12
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FP1' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 30, e_boundary = 20
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FP1' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 29, e_boundary = 20
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FP1' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 23, e_boundary = 15
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FP2' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 23, e_boundary = 13
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FP2' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 23, e_boundary = 15
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FP2' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 28, e_boundary = 17
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FP2' AND year = '2025';
UPDATE grade_boundaries SET d_boundary = 28, e_boundary = 19
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FS2' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 21, e_boundary = 12
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FS2' AND year = '2022';
UPDATE grade_boundaries SET d_boundary = 25, e_boundary = 16
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FS2' AND year = '2023';
UPDATE grade_boundaries SET d_boundary = 29, e_boundary = 23
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FS2' AND year = '2025';
