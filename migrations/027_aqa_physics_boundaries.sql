-- 027_aqa_physics_boundaries.sql
-- AQA A-level Physics, per paper.
--
-- AQA publishes Paper 3 as separate components: Section A (45, practical skills
-- and data analysis) and five Section B options of 35 each. They are stored
-- that way because those are the boundaries that exist — there is no 80-mark
-- Paper 3 boundary to compare a combined score against.
--
-- Each component is checked against its own expected max mark, so a paper
-- measured against another paper's scale fails loudly instead of grading
-- every student wrongly.
--
-- No 2020 or 2021: no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE subject = 'Physics' AND board = 'AQA';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Physics', 'AQA', 'Paper 1', '2018', 'June', 66, 56, 47, 38, 29, 21),
    ('Physics', 'AQA', 'Paper 2', '2018', 'June', 60, 48, 40, 32, 24, 16),
    ('Physics', 'AQA', 'Paper 3A', '2018', 'June', 30, 23, 19, 15, 11, 7),
    ('Physics', 'AQA', 'Paper 3BA', '2018', 'June', 27, 23, 19, 15, 11, 7),
    ('Physics', 'AQA', 'Paper 3BB', '2018', 'June', 25, 20, 16, 12, 9, 6),
    ('Physics', 'AQA', 'Paper 3BC', '2018', 'June', 28, 25, 20, 16, 12, 8),
    ('Physics', 'AQA', 'Paper 3BD', '2018', 'June', 26, 22, 18, 14, 10, 6),
    ('Physics', 'AQA', 'Paper 3BE', '2018', 'June', 29, 26, 21, 17, 13, 9),
    ('Physics', 'AQA', 'Paper 1', '2019', 'June', 69, 60, 50, 40, 31, 22),
    ('Physics', 'AQA', 'Paper 2', '2019', 'June', 69, 60, 50, 41, 32, 23),
    ('Physics', 'AQA', 'Paper 3A', '2019', 'June', 34, 28, 23, 18, 14, 10),
    ('Physics', 'AQA', 'Paper 3BA', '2019', 'June', 27, 23, 19, 15, 11, 7),
    ('Physics', 'AQA', 'Paper 3BB', '2019', 'June', 26, 21, 17, 13, 9, 6),
    ('Physics', 'AQA', 'Paper 3BC', '2019', 'June', 26, 21, 17, 14, 11, 8),
    ('Physics', 'AQA', 'Paper 3BD', '2019', 'June', 27, 22, 18, 14, 10, 6),
    ('Physics', 'AQA', 'Paper 3BE', '2019', 'June', 30, 27, 22, 17, 12, 7),
    ('Physics', 'AQA', 'Paper 1', '2022', 'June', 63, 56, 46, 36, 27, 18),
    ('Physics', 'AQA', 'Paper 2', '2022', 'June', 54, 45, 37, 29, 22, 15),
    ('Physics', 'AQA', 'Paper 3A', '2022', 'June', 26, 20, 16, 12, 9, 6),
    ('Physics', 'AQA', 'Paper 3BA', '2022', 'June', 20, 16, 13, 10, 7, 4),
    ('Physics', 'AQA', 'Paper 3BB', '2022', 'June', 22, 18, 14, 11, 8, 5),
    ('Physics', 'AQA', 'Paper 3BC', '2022', 'June', 21, 15, 12, 9, 6, 4),
    ('Physics', 'AQA', 'Paper 3BD', '2022', 'June', 19, 13, 10, 7, 5, 3),
    ('Physics', 'AQA', 'Paper 3BE', '2022', 'June', 27, 24, 19, 15, 11, 7),
    ('Physics', 'AQA', 'Paper 1', '2023', 'June', 59, 48, 40, 32, 25, 18),
    ('Physics', 'AQA', 'Paper 2', '2023', 'June', 54, 42, 34, 26, 19, 12),
    ('Physics', 'AQA', 'Paper 3A', '2023', 'June', 25, 19, 16, 13, 10, 7),
    ('Physics', 'AQA', 'Paper 3BA', '2023', 'June', 26, 20, 16, 12, 8, 5),
    ('Physics', 'AQA', 'Paper 3BB', '2023', 'June', 24, 18, 14, 11, 8, 5),
    ('Physics', 'AQA', 'Paper 3BC', '2023', 'June', 26, 23, 18, 14, 10, 6),
    ('Physics', 'AQA', 'Paper 3BD', '2023', 'June', 28, 24, 19, 14, 9, 5),
    ('Physics', 'AQA', 'Paper 3BE', '2023', 'June', 31, 26, 21, 16, 11, 7),
    ('Physics', 'AQA', 'Paper 1', '2024', 'June', 60, 49, 41, 33, 26, 19),
    ('Physics', 'AQA', 'Paper 2', '2024', 'June', 55, 41, 33, 26, 19, 12),
    ('Physics', 'AQA', 'Paper 3A', '2024', 'June', 32, 26, 21, 17, 13, 9),
    ('Physics', 'AQA', 'Paper 3BA', '2024', 'June', 24, 22, 17, 13, 9, 5),
    ('Physics', 'AQA', 'Paper 3BB', '2024', 'June', 27, 23, 18, 13, 9, 5),
    ('Physics', 'AQA', 'Paper 3BC', '2024', 'June', 28, 19, 15, 11, 8, 5),
    ('Physics', 'AQA', 'Paper 3BD', '2024', 'June', 25, 22, 17, 13, 9, 5),
    ('Physics', 'AQA', 'Paper 3BE', '2024', 'June', 26, 23, 19, 15, 11, 7),
    ('Physics', 'AQA', 'Paper 1', '2025', 'June', 63, 53, 44, 36, 28, 20),
    ('Physics', 'AQA', 'Paper 2', '2025', 'June', 61, 50, 41, 32, 23, 14),
    ('Physics', 'AQA', 'Paper 3A', '2025', 'June', 33, 27, 23, 19, 15, 11),
    ('Physics', 'AQA', 'Paper 3BA', '2025', 'June', 26, 22, 17, 13, 9, 5),
    ('Physics', 'AQA', 'Paper 3BB', '2025', 'June', 24, 18, 14, 11, 8, 5),
    ('Physics', 'AQA', 'Paper 3BC', '2025', 'June', 29, 25, 20, 15, 10, 6),
    ('Physics', 'AQA', 'Paper 3BD', '2025', 'June', 26, 21, 17, 13, 9, 6),
    ('Physics', 'AQA', 'Paper 3BE', '2025', 'June', 27, 23, 18, 14, 10, 6);
