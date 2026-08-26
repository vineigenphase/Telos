-- 033_coursework_components.sql
-- The non-written components that count toward the grade.
--
-- Geography's fieldwork investigation (7037/C, 60 marks) and the MFL
-- speaking exams (7652/3T, 7662/3T, 7692/3T, 60 marks each) were previously
-- excluded on the rule that a paper belongs here if a student can sit and
-- mark it alone. That rule was wrong in one respect: these count toward the
-- grade. Leaving them out meant a Geography prediction was built from 80%
-- of the qualification and an MFL prediction from 70%, without saying so.
--
-- The OCR Practical Endorsements stay out, which is the same rule applied
-- correctly: they are reported separately and contribute nothing to the
-- grade, so a prediction has nothing to do with them.
--
-- Speaking uses the teacher-conducted variant. AQA publishes 3T and 3V
-- separately and their boundaries are identical in every series checked, so
-- one row serves both and a student need not know which their centre used.
--
-- RAW boundaries: AQA scales speaking and publishes a 120-mark row too.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE board = 'AQA'
  AND ((subject = 'Geography' AND paper_code = 'NEA')
    OR (subject IN ('French', 'German', 'Spanish') AND paper_code = 'Paper 3'));

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Geography', 'AQA', 'NEA', '2018', 'June', 51, 47, 39, 32, 25, 18),
    ('Geography', 'AQA', 'NEA', '2019', 'June', 53, 49, 41, 33, 25, 18),
    ('Geography', 'AQA', 'NEA', '2022', 'June', 49, 45, 36, 28, 20, 12),
    ('Geography', 'AQA', 'NEA', '2023', 'June', 53, 49, 41, 33, 25, 18),
    ('Geography', 'AQA', 'NEA', '2024', 'June', 52, 49, 41, 33, 25, 18),
    ('Geography', 'AQA', 'NEA', '2025', 'June', 53, 49, 41, 33, 25, 18),
    ('French', 'AQA', 'Paper 3', '2018', 'June', 54, 48, 41, 34, 28, 22),
    ('French', 'AQA', 'Paper 3', '2019', 'June', 54, 48, 41, 34, 28, 22),
    ('French', 'AQA', 'Paper 3', '2022', 'June', 52, 46, 38, 31, 24, 17),
    ('French', 'AQA', 'Paper 3', '2023', 'June', 54, 48, 41, 34, 28, 22),
    ('French', 'AQA', 'Paper 3', '2024', 'June', 53, 48, 41, 34, 28, 22),
    ('French', 'AQA', 'Paper 3', '2025', 'June', 54, 48, 41, 34, 28, 22),
    ('German', 'AQA', 'Paper 3', '2018', 'June', 54, 48, 41, 34, 28, 22),
    ('German', 'AQA', 'Paper 3', '2019', 'June', 54, 48, 41, 34, 28, 22),
    ('German', 'AQA', 'Paper 3', '2022', 'June', 53, 46, 38, 31, 24, 17),
    ('German', 'AQA', 'Paper 3', '2023', 'June', 55, 48, 41, 34, 28, 22),
    ('German', 'AQA', 'Paper 3', '2024', 'June', 54, 48, 41, 34, 28, 22),
    ('German', 'AQA', 'Paper 3', '2025', 'June', 54, 48, 41, 34, 28, 22),
    ('Spanish', 'AQA', 'Paper 3', '2018', 'June', 53, 48, 41, 34, 28, 22),
    ('Spanish', 'AQA', 'Paper 3', '2019', 'June', 53, 48, 41, 34, 28, 22),
    ('Spanish', 'AQA', 'Paper 3', '2022', 'June', 51, 46, 39, 32, 25, 18),
    ('Spanish', 'AQA', 'Paper 3', '2023', 'June', 53, 48, 41, 34, 28, 22),
    ('Spanish', 'AQA', 'Paper 3', '2024', 'June', 53, 48, 41, 34, 28, 22),
    ('Spanish', 'AQA', 'Paper 3', '2025', 'June', 53, 48, 41, 34, 28, 22);
