-- 026_aqa_philosophy_boundaries.sql
-- AQA A-level Philosophy (7172): two 100-mark papers, both compulsory.
--
-- Paper 1 is epistemology and moral philosophy; Paper 2 is the metaphysics
-- of God and of mind. No options and no coursework, so both components are
-- papers a student can sit and mark from published materials.
--
-- Notional component boundaries, derived by AQA from the qualification
-- award. The subject row out of 200 is not stored.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Philosophy' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Philosophy', 'AQA', 'Paper 1', '2019', 'June', 76, 64, 52, 40, 29, 18),
    ('Philosophy', 'AQA', 'Paper 2', '2019', 'June', 78, 67, 54, 41, 29, 17),
    ('Philosophy', 'AQA', 'Paper 1', '2022', 'June', 69, 58, 46, 35, 24, 13),
    ('Philosophy', 'AQA', 'Paper 2', '2022', 'June', 71, 61, 48, 35, 22, 10),
    ('Philosophy', 'AQA', 'Paper 1', '2023', 'June', 79, 69, 56, 43, 30, 18),
    ('Philosophy', 'AQA', 'Paper 2', '2023', 'June', 78, 67, 53, 40, 27, 14),
    ('Philosophy', 'AQA', 'Paper 1', '2024', 'June', 78, 67, 55, 43, 31, 20),
    ('Philosophy', 'AQA', 'Paper 2', '2024', 'June', 77, 66, 53, 40, 27, 15),
    ('Philosophy', 'AQA', 'Paper 1', '2025', 'June', 79, 68, 55, 43, 31, 19),
    ('Philosophy', 'AQA', 'Paper 2', '2025', 'June', 79, 68, 54, 40, 27, 14);
