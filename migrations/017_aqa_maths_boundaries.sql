-- 017_aqa_maths_boundaries.sql
-- AQA A-level Mathematics (7357), per paper. Three 100-mark papers.
--
-- These are AQA's notional component boundaries. AQA awards at qualification
-- level and derives the per-paper figures from it, so they are its own
-- statement of what a raw mark on that paper is worth rather than a separately
-- awarded boundary. That is exactly the question Telos asks — a student logs
-- one paper and wants to know what it was worth — and it is the same basis as
-- the Edexcel figures already stored, which Pearson likewise calls notional.
--
-- It also explains the even spacing in some series: 2025 Paper 1 runs
-- 87/74/61/48/35/22, steps of thirteen throughout. That is the derivation
-- showing through, not a transcription error.
--
-- The subject-level row (out of 300) is deliberately not stored.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Maths' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Maths', 'AQA', 'Paper 1', '2018', 'June', 74, 56, 50, 44, 38, 32),
    ('Maths', 'AQA', 'Paper 2', '2018', 'June', 79, 65, 56, 47, 38, 30),
    ('Maths', 'AQA', 'Paper 3', '2018', 'June', 76, 60, 52, 44, 36, 28),
    ('Maths', 'AQA', 'Paper 1', '2019', 'June', 72, 53, 43, 33, 24, 15),
    ('Maths', 'AQA', 'Paper 2', '2019', 'June', 77, 62, 50, 38, 27, 16),
    ('Maths', 'AQA', 'Paper 3', '2019', 'June', 82, 70, 57, 45, 33, 21),
    ('Maths', 'AQA', 'Paper 1', '2022', 'June', 71, 53, 42, 32, 22, 12),
    ('Maths', 'AQA', 'Paper 2', '2022', 'June', 73, 56, 45, 35, 25, 15),
    ('Maths', 'AQA', 'Paper 3', '2022', 'June', 76, 62, 50, 38, 26, 15),
    ('Maths', 'AQA', 'Paper 1', '2023', 'June', 82, 65, 52, 39, 27, 15),
    ('Maths', 'AQA', 'Paper 2', '2023', 'June', 80, 62, 50, 38, 27, 16),
    ('Maths', 'AQA', 'Paper 3', '2023', 'June', 86, 74, 60, 46, 32, 18),
    ('Maths', 'AQA', 'Paper 1', '2024', 'June', 87, 75, 61, 48, 35, 22),
    ('Maths', 'AQA', 'Paper 2', '2024', 'June', 84, 70, 58, 47, 36, 25),
    ('Maths', 'AQA', 'Paper 3', '2024', 'June', 88, 77, 64, 51, 38, 26),
    ('Maths', 'AQA', 'Paper 1', '2025', 'June', 87, 74, 61, 48, 35, 22),
    ('Maths', 'AQA', 'Paper 2', '2025', 'June', 86, 73, 61, 49, 37, 25),
    ('Maths', 'AQA', 'Paper 3', '2025', 'June', 87, 74, 61, 48, 36, 24);
