-- 039_sqa_higher_boundaries.sql
-- SQA Highers: Biology, Chemistry, Physics, Mathematics, Economics,
-- Geography, French, German, Spanish.
--
-- Same treatment as the Advanced Highers in migration 038, for the same
-- reason: SQA publishes cut-off scores for the whole course and never per
-- component, so each component's boundary is its share of the course
-- cut-off and derived_from_course is TRUE on every row.
--
--     component_boundary = round(course_boundary * component_max / course_max)
--
-- The component max marks are NOT derived. They are SQA's own, from the
-- Assessment and Component Marks tables, and every course is checked to
-- sum to the course maximum published in the separate grade boundaries
-- release before anything is computed from it.
--
-- Graded A-D: a_star and e_boundary are both NULL. Below D is No Award.
--
-- 2024 and 2025 only. In 2022 and 2023 these courses ran in a modified
-- form - Geography 70 marks rather than 110, the sciences 120 rather than
-- 150 - which is a different set of components, not the same course with
-- different numbers.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE board = 'SQA' AND subject LIKE '% (H)';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary,
     derived_from_course)
VALUES
    ('Biology (H)', 'SQA', 'Paper 1', '2024', 'June', NULL, 17, 14, 11, 8, NULL, TRUE),
    ('Biology (H)', 'SQA', 'Paper 2', '2024', 'June', NULL, 65, 54, 43, 32, NULL, TRUE),
    ('Biology (H)', 'SQA', 'Assignment', '2024', 'June', NULL, 20, 17, 14, 10, NULL, TRUE),
    ('Chemistry (H)', 'SQA', 'Paper 1', '2024', 'June', NULL, 17, 14, 11, 8, NULL, TRUE),
    ('Chemistry (H)', 'SQA', 'Paper 2', '2024', 'June', NULL, 64, 53, 41, 30, NULL, TRUE),
    ('Chemistry (H)', 'SQA', 'Assignment', '2024', 'June', NULL, 20, 17, 13, 9, NULL, TRUE),
    ('Economics (H)', 'SQA', 'Question Paper', '2024', 'June', NULL, 63, 54, 45, 36, NULL, TRUE),
    ('Economics (H)', 'SQA', 'Assignment', '2024', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('English (H)', 'SQA', 'Paper 1', '2024', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('English (H)', 'SQA', 'Paper 2', '2024', 'June', NULL, 27, 23, 19, 15, NULL, TRUE),
    ('English (H)', 'SQA', 'Portfolio', '2024', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('French (H)', 'SQA', 'Directed Writing', '2024', 'June', NULL, 10, 9, 7, 6, NULL, TRUE),
    ('French (H)', 'SQA', 'Listening', '2024', 'June', NULL, 20, 18, 14, 12, NULL, TRUE),
    ('French (H)', 'SQA', 'Reading', '2024', 'June', NULL, 20, 18, 14, 12, NULL, TRUE),
    ('French (H)', 'SQA', 'Talking', '2024', 'June', NULL, 20, 18, 14, 12, NULL, TRUE),
    ('French (H)', 'SQA', 'Assignment', '2024', 'June', NULL, 10, 9, 7, 6, NULL, TRUE),
    ('Geography (H)', 'SQA', 'Paper 1', '2024', 'June', NULL, 35, 29, 23, 17, NULL, TRUE),
    ('Geography (H)', 'SQA', 'Paper 2', '2024', 'June', NULL, 21, 17, 14, 10, NULL, TRUE),
    ('Geography (H)', 'SQA', 'Assignment', '2024', 'June', NULL, 21, 17, 14, 10, NULL, TRUE),
    ('German (H)', 'SQA', 'Directed Writing', '2024', 'June', NULL, 10, 9, 7, 6, NULL, TRUE),
    ('German (H)', 'SQA', 'Listening', '2024', 'June', NULL, 20, 18, 14, 12, NULL, TRUE),
    ('German (H)', 'SQA', 'Reading', '2024', 'June', NULL, 20, 18, 14, 12, NULL, TRUE),
    ('German (H)', 'SQA', 'Talking', '2024', 'June', NULL, 20, 18, 14, 12, NULL, TRUE),
    ('German (H)', 'SQA', 'Assignment', '2024', 'June', NULL, 10, 9, 7, 6, NULL, TRUE),
    ('Maths (H)', 'SQA', 'Paper 1', '2024', 'June', NULL, 38, 33, 27, 21, NULL, TRUE),
    ('Maths (H)', 'SQA', 'Paper 2', '2024', 'June', NULL, 46, 38, 32, 25, NULL, TRUE),
    ('Physics (H)', 'SQA', 'Paper 1', '2024', 'June', NULL, 18, 15, 12, 10, NULL, TRUE),
    ('Physics (H)', 'SQA', 'Paper 2', '2024', 'June', NULL, 66, 56, 46, 36, NULL, TRUE),
    ('Physics (H)', 'SQA', 'Assignment', '2024', 'June', NULL, 21, 18, 15, 11, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Directed Writing', '2024', 'June', NULL, 10, 9, 7, 6, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Listening', '2024', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Reading', '2024', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Talking', '2024', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Assignment', '2024', 'June', NULL, 10, 9, 7, 6, NULL, TRUE),
    ('Biology (H)', 'SQA', 'Paper 1', '2025', 'June', NULL, 18, 15, 12, 10, NULL, TRUE),
    ('Biology (H)', 'SQA', 'Paper 2', '2025', 'June', NULL, 68, 58, 48, 37, NULL, TRUE),
    ('Biology (H)', 'SQA', 'Assignment', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('Chemistry (H)', 'SQA', 'Paper 1', '2025', 'June', NULL, 18, 15, 13, 10, NULL, TRUE),
    ('Chemistry (H)', 'SQA', 'Paper 2', '2025', 'June', NULL, 68, 58, 49, 39, NULL, TRUE),
    ('Chemistry (H)', 'SQA', 'Assignment', '2025', 'June', NULL, 22, 18, 15, 12, NULL, TRUE),
    ('Economics (H)', 'SQA', 'Question Paper', '2025', 'June', NULL, 64, 55, 46, 37, NULL, TRUE),
    ('Economics (H)', 'SQA', 'Assignment', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('English (H)', 'SQA', 'Paper 1', '2025', 'June', NULL, 20, 17, 15, 12, NULL, TRUE),
    ('English (H)', 'SQA', 'Paper 2', '2025', 'June', NULL, 27, 23, 20, 16, NULL, TRUE),
    ('English (H)', 'SQA', 'Portfolio', '2025', 'June', NULL, 20, 17, 15, 12, NULL, TRUE),
    ('French (H)', 'SQA', 'Directed Writing', '2025', 'June', NULL, 11, 9, 8, 6, NULL, TRUE),
    ('French (H)', 'SQA', 'Listening', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('French (H)', 'SQA', 'Reading', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('French (H)', 'SQA', 'Talking', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('French (H)', 'SQA', 'Assignment', '2025', 'June', NULL, 11, 9, 8, 6, NULL, TRUE),
    ('Geography (H)', 'SQA', 'Paper 1', '2025', 'June', NULL, 35, 29, 23, 17, NULL, TRUE),
    ('Geography (H)', 'SQA', 'Paper 2', '2025', 'June', NULL, 21, 17, 14, 10, NULL, TRUE),
    ('Geography (H)', 'SQA', 'Assignment', '2025', 'June', NULL, 21, 17, 14, 10, NULL, TRUE),
    ('German (H)', 'SQA', 'Directed Writing', '2025', 'June', NULL, 10, 9, 7, 6, NULL, TRUE),
    ('German (H)', 'SQA', 'Listening', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('German (H)', 'SQA', 'Reading', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('German (H)', 'SQA', 'Talking', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('German (H)', 'SQA', 'Assignment', '2025', 'June', NULL, 10, 9, 7, 6, NULL, TRUE),
    ('Maths (H)', 'SQA', 'Paper 1', '2025', 'June', NULL, 39, 33, 28, 22, NULL, TRUE),
    ('Maths (H)', 'SQA', 'Paper 2', '2025', 'June', NULL, 47, 40, 32, 25, NULL, TRUE),
    ('Physics (H)', 'SQA', 'Paper 1', '2025', 'June', NULL, 17, 14, 12, 9, NULL, TRUE),
    ('Physics (H)', 'SQA', 'Paper 2', '2025', 'June', NULL, 63, 53, 44, 34, NULL, TRUE),
    ('Physics (H)', 'SQA', 'Assignment', '2025', 'June', NULL, 20, 17, 14, 11, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Directed Writing', '2025', 'June', NULL, 10, 9, 8, 6, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Listening', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Reading', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Talking', '2025', 'June', NULL, 21, 18, 15, 12, NULL, TRUE),
    ('Spanish (H)', 'SQA', 'Assignment', '2025', 'June', NULL, 10, 9, 8, 6, NULL, TRUE);
