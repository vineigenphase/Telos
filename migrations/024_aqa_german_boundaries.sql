-- 024_aqa_german_boundaries.sql
-- AQA A-level German (7662): Paper 1 (100) and Paper 2 (80).
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

DELETE FROM grade_boundaries WHERE subject = 'German' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('German', 'AQA', 'Paper 1', '2018', 'June', 85, 67, 55, 43, 32, 21),
    ('German', 'AQA', 'Paper 2', '2018', 'June', 67, 51, 42, 33, 24, 15),
    ('German', 'AQA', 'Paper 1', '2019', 'June', 82, 66, 54, 42, 31, 20),
    ('German', 'AQA', 'Paper 2', '2019', 'June', 66, 54, 44, 34, 24, 15),
    ('German', 'AQA', 'Paper 1', '2022', 'June', 81, 64, 52, 40, 29, 18),
    ('German', 'AQA', 'Paper 2', '2022', 'June', 61, 43, 35, 27, 19, 11),
    ('German', 'AQA', 'Paper 1', '2023', 'June', 87, 72, 57, 43, 29, 15),
    ('German', 'AQA', 'Paper 2', '2023', 'June', 67, 52, 41, 30, 19, 9),
    ('German', 'AQA', 'Paper 1', '2024', 'June', 89, 78, 66, 54, 42, 30),
    ('German', 'AQA', 'Paper 2', '2024', 'June', 65, 52, 42, 32, 22, 12),
    ('German', 'AQA', 'Paper 1', '2025', 'June', 89, 78, 66, 54, 42, 30),
    ('German', 'AQA', 'Paper 2', '2025', 'June', 66, 54, 44, 34, 24, 15);
