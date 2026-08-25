-- 025_aqa_spanish_boundaries.sql
-- AQA A-level Spanish (7692): Paper 1 (100) and Paper 2 (80).
--
-- RAW boundaries, not scaled. AQA scales both of these components and
-- prints two rows for each: the raw boundaries, then the scaled ones —
-- Paper 1 appears both as "100 91 82 70..." and as "200 182 164 140...".
-- A student marks their own paper out of the raw total, so the extractor
-- picks the row whose max matches the paper's real mark. Taking the last
-- match instead would have doubled every boundary and graded everyone U.
--
-- Speaking (component 3) is not stored. It is a 21-23 minute oral
-- conducted by a teacher or visiting examiner, which a student cannot sit
-- or mark alone from published materials.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Spanish' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Spanish', 'AQA', 'Paper 1', '2018', 'June', 86, 76, 64, 52, 41, 30),
    ('Spanish', 'AQA', 'Paper 2', '2018', 'June', 68, 59, 49, 39, 29, 19),
    ('Spanish', 'AQA', 'Paper 1', '2019', 'June', 82, 70, 58, 46, 34, 23),
    ('Spanish', 'AQA', 'Paper 2', '2019', 'June', 68, 60, 49, 38, 28, 18),
    ('Spanish', 'AQA', 'Paper 1', '2022', 'June', 80, 68, 55, 42, 30, 18),
    ('Spanish', 'AQA', 'Paper 2', '2022', 'June', 64, 54, 44, 34, 24, 15),
    ('Spanish', 'AQA', 'Paper 1', '2023', 'June', 87, 77, 63, 49, 35, 21),
    ('Spanish', 'AQA', 'Paper 2', '2023', 'June', 67, 57, 46, 36, 26, 16),
    ('Spanish', 'AQA', 'Paper 1', '2024', 'June', 86, 75, 62, 49, 36, 24),
    ('Spanish', 'AQA', 'Paper 2', '2024', 'June', 66, 57, 46, 35, 25, 15),
    ('Spanish', 'AQA', 'Paper 1', '2025', 'June', 89, 81, 68, 56, 44, 32),
    ('Spanish', 'AQA', 'Paper 2', '2025', 'June', 65, 55, 46, 37, 28, 19);
