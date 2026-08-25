-- 022_aqa_geography_boundaries.sql
-- AQA A-level Geography (7037), per paper.
--
-- Two written papers of 120 marks. The 60-mark fieldwork investigation
-- (component C) is coursework, marked by teachers, and is not stored: there
-- is no past paper to attempt for your own investigation.
--
-- Notional component boundaries, derived by AQA from the qualification
-- award. The subject row out of 300 is not stored.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Geography' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Geography', 'AQA', 'Paper 1', '2018', 'June', 86, 72, 61, 50, 40, 30),
    ('Geography', 'AQA', 'Paper 2', '2018', 'June', 88, 74, 62, 50, 39, 28),
    ('Geography', 'AQA', 'Paper 1', '2019', 'June', 93, 80, 69, 58, 47, 36),
    ('Geography', 'AQA', 'Paper 2', '2019', 'June', 90, 75, 64, 53, 42, 32),
    ('Geography', 'AQA', 'Paper 1', '2022', 'June', 86, 72, 60, 48, 36, 25),
    ('Geography', 'AQA', 'Paper 2', '2022', 'June', 92, 81, 69, 57, 45, 33),
    ('Geography', 'AQA', 'Paper 1', '2023', 'June', 95, 83, 70, 57, 44, 32),
    ('Geography', 'AQA', 'Paper 2', '2023', 'June', 92, 78, 65, 53, 41, 29),
    ('Geography', 'AQA', 'Paper 1', '2024', 'June', 93, 80, 69, 58, 47, 37),
    ('Geography', 'AQA', 'Paper 2', '2024', 'June', 94, 82, 69, 56, 43, 31),
    ('Geography', 'AQA', 'Paper 1', '2025', 'June', 94, 81, 70, 59, 48, 38),
    ('Geography', 'AQA', 'Paper 2', '2025', 'June', 95, 83, 71, 60, 49, 38);
