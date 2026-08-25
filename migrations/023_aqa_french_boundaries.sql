-- 023_aqa_french_boundaries.sql
-- AQA A-level French (7652): Paper 1 (100) and Paper 2 (80).
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

DELETE FROM grade_boundaries WHERE subject = 'French' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('French', 'AQA', 'Paper 1', '2018', 'June', 87, 75, 65, 56, 47, 38),
    ('French', 'AQA', 'Paper 2', '2018', 'June', 72, 64, 54, 45, 36, 27),
    ('French', 'AQA', 'Paper 1', '2019', 'June', 89, 80, 69, 58, 48, 38),
    ('French', 'AQA', 'Paper 2', '2019', 'June', 71, 63, 53, 44, 35, 26),
    ('French', 'AQA', 'Paper 1', '2022', 'June', 85, 75, 64, 53, 43, 33),
    ('French', 'AQA', 'Paper 2', '2022', 'June', 63, 52, 42, 33, 24, 15),
    ('French', 'AQA', 'Paper 1', '2023', 'June', 91, 82, 70, 58, 47, 36),
    ('French', 'AQA', 'Paper 2', '2023', 'June', 70, 60, 50, 40, 30, 21),
    ('French', 'AQA', 'Paper 1', '2024', 'June', 92, 85, 75, 65, 55, 45),
    ('French', 'AQA', 'Paper 2', '2024', 'June', 68, 59, 49, 40, 31, 22),
    ('French', 'AQA', 'Paper 1', '2025', 'June', 91, 82, 73, 64, 56, 48),
    ('French', 'AQA', 'Paper 2', '2025', 'June', 71, 62, 53, 44, 35, 27);
