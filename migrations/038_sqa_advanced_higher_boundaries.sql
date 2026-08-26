-- 038_sqa_advanced_higher_boundaries.sql
-- SQA Advanced Highers: Biology, Chemistry, Physics, Mathematics,
-- Economics, Geography, French, German, Spanish.
--
-- Graded A-D. a_star is NULL because there is no A*, and e_boundary is
-- NULL because there is no E - below D is No Award. prediction.py reads
-- both absences and builds a ladder that runs from D up to A.
--
-- derived_from_course is TRUE on every row. SQA publishes boundaries for
-- the whole course only, never per component, so each component's
-- boundary is its share of the course cut-off:
--
--     component_boundary = round(course_boundary * component_max / course_max)
--
-- The component max marks themselves are NOT derived - they are SQA's own,
-- from the Assessment and Component Marks tables, and each course's
-- components are checked to sum to the course maximum before anything is
-- computed from them.
--
-- 2022-2025. Several of these courses ran in a modified form in 2022 and
-- 2023 - coursework withdrawn, question papers resized - so a component
-- carries a boundary for a year only when it was the same paper that
-- year: same code, same max mark. Advanced Higher Physics' question
-- paper was 155 marks then against 120 now, so it has no row for those
-- years rather than one computed for a paper of a different length.
-- Subjects that were not modified, English among them, carry all four.
--
-- Idempotent.

-- Scoped to the Advanced Highers. When this was first written, SQA in
-- this table meant only Advanced Highers, so deleting every SQA row was
-- correct. It is not any more: migration 039 owns the Higher rows, and
-- re-running this out of numeric order wiped them. A DELETE must never
-- be wider than the INSERT that follows it.
DELETE FROM grade_boundaries
  WHERE board = 'SQA' AND subject LIKE '% (AH)';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary,
     derived_from_course)
VALUES
    ('Biology (AH)', 'SQA', 'Section 1', '2022', 'June', NULL, 14, 12, 9, 6, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Section 2', '2022', 'June', NULL, 58, 46, 35, 24, NULL, TRUE),
    ('Economics (AH)', 'SQA', 'Question Paper', '2022', 'June', NULL, 53, 45, 37, 29, NULL, TRUE),
    ('Economics (AH)', 'SQA', 'Project', '2022', 'June', NULL, 26, 22, 18, 14, NULL, TRUE),
    ('English (AH)', 'SQA', 'Literary Study', '2022', 'June', NULL, 13, 11, 9, 7, NULL, TRUE),
    ('English (AH)', 'SQA', 'Textual Analysis', '2022', 'June', NULL, 13, 11, 9, 7, NULL, TRUE),
    ('English (AH)', 'SQA', 'Dissertation', '2022', 'June', NULL, 20, 16, 14, 11, NULL, TRUE),
    ('English (AH)', 'SQA', 'Portfolio', '2022', 'June', NULL, 20, 16, 14, 11, NULL, TRUE),
    ('French (AH)', 'SQA', 'Listening', '2022', 'June', NULL, 48, 41, 34, 27, NULL, TRUE),
    ('French (AH)', 'SQA', 'Reading', '2022', 'June', NULL, 34, 29, 24, 19, NULL, TRUE),
    ('French (AH)', 'SQA', 'Talking', '2022', 'June', NULL, 34, 29, 24, 19, NULL, TRUE),
    ('French (AH)', 'SQA', 'Portfolio', '2022', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Question Paper', '2022', 'June', NULL, 33, 27, 21, 15, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Folio A', '2022', 'June', NULL, 39, 32, 25, 18, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Folio B', '2022', 'June', NULL, 26, 21, 17, 12, NULL, TRUE),
    ('German (AH)', 'SQA', 'Listening', '2022', 'June', NULL, 48, 41, 34, 27, NULL, TRUE),
    ('German (AH)', 'SQA', 'Reading', '2022', 'June', NULL, 34, 29, 24, 19, NULL, TRUE),
    ('German (AH)', 'SQA', 'Talking', '2022', 'June', NULL, 34, 29, 24, 19, NULL, TRUE),
    ('German (AH)', 'SQA', 'Portfolio', '2022', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Maths (AH)', 'SQA', 'Paper 1', '2022', 'June', NULL, 24, 20, 15, 11, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Listening', '2022', 'June', NULL, 47, 40, 33, 26, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Reading', '2022', 'June', NULL, 34, 28, 24, 18, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Talking', '2022', 'June', NULL, 34, 28, 24, 18, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Portfolio', '2022', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Section 1', '2023', 'June', NULL, 16, 13, 10, 7, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Section 2', '2023', 'June', NULL, 66, 53, 41, 28, NULL, TRUE),
    ('Economics (AH)', 'SQA', 'Question Paper', '2023', 'June', NULL, 56, 47, 38, 29, NULL, TRUE),
    ('Economics (AH)', 'SQA', 'Project', '2023', 'June', NULL, 28, 23, 19, 14, NULL, TRUE),
    ('English (AH)', 'SQA', 'Literary Study', '2023', 'June', NULL, 13, 11, 9, 7, NULL, TRUE),
    ('English (AH)', 'SQA', 'Textual Analysis', '2023', 'June', NULL, 13, 11, 9, 7, NULL, TRUE),
    ('English (AH)', 'SQA', 'Dissertation', '2023', 'June', NULL, 20, 16, 14, 11, NULL, TRUE),
    ('English (AH)', 'SQA', 'Portfolio', '2023', 'June', NULL, 20, 16, 14, 11, NULL, TRUE),
    ('French (AH)', 'SQA', 'Listening', '2023', 'June', NULL, 48, 41, 34, 27, NULL, TRUE),
    ('French (AH)', 'SQA', 'Reading', '2023', 'June', NULL, 34, 30, 24, 20, NULL, TRUE),
    ('French (AH)', 'SQA', 'Talking', '2023', 'June', NULL, 34, 30, 24, 20, NULL, TRUE),
    ('French (AH)', 'SQA', 'Portfolio', '2023', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Question Paper', '2023', 'June', NULL, 33, 27, 21, 15, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Folio A', '2023', 'June', NULL, 39, 32, 25, 18, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Folio B', '2023', 'June', NULL, 26, 21, 17, 12, NULL, TRUE),
    ('German (AH)', 'SQA', 'Listening', '2023', 'June', NULL, 48, 41, 34, 27, NULL, TRUE),
    ('German (AH)', 'SQA', 'Reading', '2023', 'June', NULL, 34, 30, 24, 20, NULL, TRUE),
    ('German (AH)', 'SQA', 'Talking', '2023', 'June', NULL, 34, 30, 24, 20, NULL, TRUE),
    ('German (AH)', 'SQA', 'Portfolio', '2023', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('Maths (AH)', 'SQA', 'Paper 1', '2023', 'June', NULL, 24, 20, 15, 10, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Listening', '2023', 'June', NULL, 48, 41, 34, 27, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Reading', '2023', 'June', NULL, 34, 29, 24, 19, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Talking', '2023', 'June', NULL, 34, 29, 24, 19, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Portfolio', '2023', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Section 1', '2024', 'June', NULL, 16, 13, 10, 8, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Section 2', '2024', 'June', NULL, 62, 52, 42, 32, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Project', '2024', 'June', NULL, 26, 22, 18, 13, NULL, TRUE),
    ('Chemistry (AH)', 'SQA', 'Section 1', '2024', 'June', NULL, 18, 15, 12, 9, NULL, TRUE),
    ('Chemistry (AH)', 'SQA', 'Section 2', '2024', 'June', NULL, 60, 51, 42, 33, NULL, TRUE),
    ('Chemistry (AH)', 'SQA', 'Project', '2024', 'June', NULL, 26, 22, 18, 14, NULL, TRUE),
    ('Economics (AH)', 'SQA', 'Question Paper', '2024', 'June', NULL, 56, 48, 40, 32, NULL, TRUE),
    ('Economics (AH)', 'SQA', 'Project', '2024', 'June', NULL, 28, 24, 20, 16, NULL, TRUE),
    ('English (AH)', 'SQA', 'Literary Study', '2024', 'June', NULL, 13, 11, 10, 8, NULL, TRUE),
    ('English (AH)', 'SQA', 'Textual Analysis', '2024', 'June', NULL, 13, 11, 10, 8, NULL, TRUE),
    ('English (AH)', 'SQA', 'Dissertation', '2024', 'June', NULL, 20, 17, 14, 12, NULL, TRUE),
    ('English (AH)', 'SQA', 'Portfolio', '2024', 'June', NULL, 20, 17, 14, 12, NULL, TRUE),
    ('French (AH)', 'SQA', 'Listening', '2024', 'June', NULL, 52, 44, 37, 30, NULL, TRUE),
    ('French (AH)', 'SQA', 'Reading', '2024', 'June', NULL, 37, 32, 26, 21, NULL, TRUE),
    ('French (AH)', 'SQA', 'Talking', '2024', 'June', NULL, 37, 32, 26, 21, NULL, TRUE),
    ('French (AH)', 'SQA', 'Portfolio', '2024', 'June', NULL, 22, 19, 16, 13, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Question Paper', '2024', 'June', NULL, 35, 29, 24, 18, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Folio A', '2024', 'June', NULL, 42, 35, 28, 22, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Folio B', '2024', 'June', NULL, 28, 23, 19, 14, NULL, TRUE),
    ('German (AH)', 'SQA', 'Listening', '2024', 'June', NULL, 49, 42, 35, 28, NULL, TRUE),
    ('German (AH)', 'SQA', 'Reading', '2024', 'June', NULL, 35, 30, 25, 20, NULL, TRUE),
    ('German (AH)', 'SQA', 'Talking', '2024', 'June', NULL, 35, 30, 25, 20, NULL, TRUE),
    ('German (AH)', 'SQA', 'Portfolio', '2024', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('Maths (AH)', 'SQA', 'Paper 1', '2024', 'June', NULL, 24, 20, 16, 12, NULL, TRUE),
    ('Maths (AH)', 'SQA', 'Paper 2', '2024', 'June', NULL, 56, 46, 37, 27, NULL, TRUE),
    ('Physics (AH)', 'SQA', 'Question Paper', '2024', 'June', NULL, 82, 69, 56, 42, NULL, TRUE),
    ('Physics (AH)', 'SQA', 'Project', '2024', 'June', NULL, 28, 23, 18, 14, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Listening', '2024', 'June', NULL, 47, 40, 33, 26, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Reading', '2024', 'June', NULL, 34, 28, 24, 18, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Talking', '2024', 'June', NULL, 34, 28, 24, 18, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Portfolio', '2024', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Section 1', '2025', 'June', NULL, 15, 13, 10, 8, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Section 2', '2025', 'June', NULL, 60, 50, 41, 32, NULL, TRUE),
    ('Biology (AH)', 'SQA', 'Project', '2025', 'June', NULL, 25, 21, 17, 13, NULL, TRUE),
    ('Chemistry (AH)', 'SQA', 'Section 1', '2025', 'June', NULL, 18, 16, 13, 10, NULL, TRUE),
    ('Chemistry (AH)', 'SQA', 'Section 2', '2025', 'June', NULL, 63, 53, 44, 35, NULL, TRUE),
    ('Chemistry (AH)', 'SQA', 'Project', '2025', 'June', NULL, 27, 23, 19, 15, NULL, TRUE),
    ('Economics (AH)', 'SQA', 'Question Paper', '2025', 'June', NULL, 59, 49, 40, 31, NULL, TRUE),
    ('Economics (AH)', 'SQA', 'Project', '2025', 'June', NULL, 29, 25, 20, 15, NULL, TRUE),
    ('English (AH)', 'SQA', 'Literary Study', '2025', 'June', NULL, 13, 11, 10, 8, NULL, TRUE),
    ('English (AH)', 'SQA', 'Textual Analysis', '2025', 'June', NULL, 13, 11, 10, 8, NULL, TRUE),
    ('English (AH)', 'SQA', 'Dissertation', '2025', 'June', NULL, 20, 17, 14, 12, NULL, TRUE),
    ('English (AH)', 'SQA', 'Portfolio', '2025', 'June', NULL, 20, 17, 14, 12, NULL, TRUE),
    ('French (AH)', 'SQA', 'Listening', '2025', 'June', NULL, 50, 43, 35, 27, NULL, TRUE),
    ('French (AH)', 'SQA', 'Reading', '2025', 'June', NULL, 36, 30, 25, 20, NULL, TRUE),
    ('French (AH)', 'SQA', 'Talking', '2025', 'June', NULL, 36, 30, 25, 20, NULL, TRUE),
    ('French (AH)', 'SQA', 'Portfolio', '2025', 'June', NULL, 22, 18, 15, 12, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Question Paper', '2025', 'June', NULL, 35, 30, 25, 19, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Folio A', '2025', 'June', NULL, 42, 36, 30, 23, NULL, TRUE),
    ('Geography (AH)', 'SQA', 'Folio B', '2025', 'June', NULL, 28, 24, 20, 15, NULL, TRUE),
    ('German (AH)', 'SQA', 'Listening', '2025', 'June', NULL, 49, 42, 35, 28, NULL, TRUE),
    ('German (AH)', 'SQA', 'Reading', '2025', 'June', NULL, 35, 30, 25, 20, NULL, TRUE),
    ('German (AH)', 'SQA', 'Talking', '2025', 'June', NULL, 35, 30, 25, 20, NULL, TRUE),
    ('German (AH)', 'SQA', 'Portfolio', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('Maths (AH)', 'SQA', 'Paper 1', '2025', 'June', NULL, 25, 22, 18, 15, NULL, TRUE),
    ('Maths (AH)', 'SQA', 'Paper 2', '2025', 'June', NULL, 58, 49, 42, 33, NULL, TRUE),
    ('Physics (AH)', 'SQA', 'Question Paper', '2025', 'June', NULL, 82, 69, 56, 43, NULL, TRUE),
    ('Physics (AH)', 'SQA', 'Project', '2025', 'June', NULL, 28, 23, 19, 14, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Listening', '2025', 'June', NULL, 49, 42, 35, 28, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Reading', '2025', 'June', NULL, 35, 30, 25, 20, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Talking', '2025', 'June', NULL, 35, 30, 25, 20, NULL, TRUE),
    ('Spanish (AH)', 'SQA', 'Portfolio', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE);
