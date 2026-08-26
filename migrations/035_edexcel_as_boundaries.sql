-- 035_edexcel_as_boundaries.sql
-- Edexcel AS-levels: Mathematics (8MA0), Further Mathematics (8FM0),
-- Physics (8PH0), Chemistry (8CH0), Biology A (8BN0).
--
-- a_star is NULL on every row: an AS-level is graded A-E. prediction.py
-- reads the absence and stops the grade ladder at A.
--
-- Read from the AS section of the same series documents as the A-levels.
-- Those tables use the no-A* layout the parser already handled for
-- A-level Mathematics, so the shape is not new - but the title must match
-- exactly, because 'AS Mathematics' is a substring of nothing while
-- 'AS Further Mathematics' is its own qualification.
--
-- AS Mathematics Paper 2 is 60 marks, not 100. Carrying the A-level shape
-- across would have overstated it by two thirds; it is read from the
-- document and checked, like every other row.
--
-- No 2018 document to hand, and no 2020 or 2021 - no summer exam series.
--
-- Idempotent.

DELETE FROM grade_boundaries WHERE board = 'Edexcel' AND subject LIKE '% (AS)';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series,
     a_star, a_boundary, b_boundary, c_boundary, d_boundary, e_boundary)
VALUES
    ('Maths (AS)', 'Edexcel', 'Paper 1', '2019', 'June', NULL, 63, 54, 46, 38, 30),
    ('Maths (AS)', 'Edexcel', 'Paper 2', '2019', 'June', NULL, 38, 33, 28, 23, 18),
    ('Maths (AS)', 'Edexcel', 'Paper 1', '2022', 'June', NULL, 60, 50, 40, 31, 22),
    ('Maths (AS)', 'Edexcel', 'Paper 2', '2022', 'June', NULL, 35, 29, 24, 19, 14),
    ('Maths (AS)', 'Edexcel', 'Paper 1', '2023', 'June', NULL, 65, 56, 48, 40, 32),
    ('Maths (AS)', 'Edexcel', 'Paper 2', '2023', 'June', NULL, 38, 33, 28, 24, 20),
    ('Maths (AS)', 'Edexcel', 'Paper 1', '2024', 'June', NULL, 60, 51, 42, 34, 26),
    ('Maths (AS)', 'Edexcel', 'Paper 2', '2024', 'June', NULL, 45, 39, 33, 27, 21),
    ('Maths (AS)', 'Edexcel', 'Paper 1', '2025', 'June', NULL, 63, 55, 48, 41, 34),
    ('Maths (AS)', 'Edexcel', 'Paper 2', '2025', 'June', NULL, 45, 39, 33, 28, 23),
    ('Further Maths (AS)', 'Edexcel', 'Paper 1', '2019', 'June', NULL, 49, 41, 33, 25, 18),
    ('Further Maths (AS)', 'Edexcel', 'Paper 221', '2019', 'June', NULL, 25, 21, 18, 15, 12),
    ('Further Maths (AS)', 'Edexcel', 'Paper 222', '2019', 'June', NULL, 24, 21, 18, 15, 12),
    ('Further Maths (AS)', 'Edexcel', 'Paper 223', '2019', 'June', NULL, 27, 23, 20, 17, 14),
    ('Further Maths (AS)', 'Edexcel', 'Paper 224', '2019', 'June', NULL, 23, 20, 17, 15, 13),
    ('Further Maths (AS)', 'Edexcel', 'Paper 225', '2019', 'June', NULL, 24, 21, 18, 15, 13),
    ('Further Maths (AS)', 'Edexcel', 'Paper 226', '2019', 'June', NULL, 20, 17, 15, 13, 11),
    ('Further Maths (AS)', 'Edexcel', 'Paper 227', '2019', 'June', NULL, 24, 21, 18, 15, 12),
    ('Further Maths (AS)', 'Edexcel', 'Paper 228', '2019', 'June', NULL, 23, 20, 17, 14, 11),
    ('Further Maths (AS)', 'Edexcel', 'Paper 1', '2022', 'June', NULL, 47, 38, 30, 22, 14),
    ('Further Maths (AS)', 'Edexcel', 'Paper 221', '2022', 'June', NULL, 23, 19, 15, 12, 9),
    ('Further Maths (AS)', 'Edexcel', 'Paper 222', '2022', 'June', NULL, 23, 19, 15, 12, 9),
    ('Further Maths (AS)', 'Edexcel', 'Paper 223', '2022', 'June', NULL, 25, 21, 17, 13, 9),
    ('Further Maths (AS)', 'Edexcel', 'Paper 224', '2022', 'June', NULL, 22, 19, 16, 13, 10),
    ('Further Maths (AS)', 'Edexcel', 'Paper 225', '2022', 'June', NULL, 22, 18, 15, 12, 9),
    ('Further Maths (AS)', 'Edexcel', 'Paper 226', '2022', 'June', NULL, 19, 16, 14, 12, 10),
    ('Further Maths (AS)', 'Edexcel', 'Paper 227', '2022', 'June', NULL, 22, 19, 16, 13, 10),
    ('Further Maths (AS)', 'Edexcel', 'Paper 228', '2022', 'June', NULL, 21, 18, 15, 12, 10),
    ('Further Maths (AS)', 'Edexcel', 'Paper 1', '2023', 'June', NULL, 57, 48, 40, 32, 24),
    ('Further Maths (AS)', 'Edexcel', 'Paper 221', '2023', 'June', NULL, 29, 25, 21, 18, 15),
    ('Further Maths (AS)', 'Edexcel', 'Paper 222', '2023', 'June', NULL, 24, 21, 18, 15, 12),
    ('Further Maths (AS)', 'Edexcel', 'Paper 223', '2023', 'June', NULL, 26, 22, 19, 16, 13),
    ('Further Maths (AS)', 'Edexcel', 'Paper 224', '2023', 'June', NULL, 23, 20, 17, 15, 13),
    ('Further Maths (AS)', 'Edexcel', 'Paper 225', '2023', 'June', NULL, 27, 24, 21, 18, 16),
    ('Further Maths (AS)', 'Edexcel', 'Paper 226', '2023', 'June', NULL, 30, 27, 24, 21, 18),
    ('Further Maths (AS)', 'Edexcel', 'Paper 227', '2023', 'June', NULL, 25, 22, 19, 16, 13),
    ('Further Maths (AS)', 'Edexcel', 'Paper 228', '2023', 'June', NULL, 24, 21, 18, 15, 12),
    ('Further Maths (AS)', 'Edexcel', 'Paper 1', '2024', 'June', NULL, 57, 48, 39, 31, 23),
    ('Further Maths (AS)', 'Edexcel', 'Paper 221', '2024', 'June', NULL, 27, 23, 19, 16, 13),
    ('Further Maths (AS)', 'Edexcel', 'Paper 222', '2024', 'June', NULL, 23, 20, 17, 14, 12),
    ('Further Maths (AS)', 'Edexcel', 'Paper 223', '2024', 'June', NULL, 31, 28, 25, 22, 19),
    ('Further Maths (AS)', 'Edexcel', 'Paper 224', '2024', 'June', NULL, 23, 20, 17, 14, 12),
    ('Further Maths (AS)', 'Edexcel', 'Paper 225', '2024', 'June', NULL, 31, 28, 25, 22, 20),
    ('Further Maths (AS)', 'Edexcel', 'Paper 226', '2024', 'June', NULL, 30, 27, 24, 21, 18),
    ('Further Maths (AS)', 'Edexcel', 'Paper 227', '2024', 'June', NULL, 23, 21, 19, 18, 17),
    ('Further Maths (AS)', 'Edexcel', 'Paper 228', '2024', 'June', NULL, 26, 23, 20, 17, 14),
    ('Further Maths (AS)', 'Edexcel', 'Paper 1', '2025', 'June', NULL, 58, 49, 40, 32, 24),
    ('Further Maths (AS)', 'Edexcel', 'Paper 221', '2025', 'June', NULL, 25, 21, 18, 15, 12),
    ('Further Maths (AS)', 'Edexcel', 'Paper 222', '2025', 'June', NULL, 27, 24, 21, 18, 16),
    ('Further Maths (AS)', 'Edexcel', 'Paper 223', '2025', 'June', NULL, 31, 28, 25, 23, 21),
    ('Further Maths (AS)', 'Edexcel', 'Paper 224', '2025', 'June', NULL, 27, 24, 21, 18, 16),
    ('Further Maths (AS)', 'Edexcel', 'Paper 225', '2025', 'June', NULL, 28, 26, 24, 22, 20),
    ('Further Maths (AS)', 'Edexcel', 'Paper 226', '2025', 'June', NULL, 30, 27, 24, 21, 18),
    ('Further Maths (AS)', 'Edexcel', 'Paper 227', '2025', 'June', NULL, 24, 22, 20, 18, 17),
    ('Further Maths (AS)', 'Edexcel', 'Paper 228', '2025', 'June', NULL, 24, 21, 18, 15, 12),
    ('Physics (AS)', 'Edexcel', 'Paper 1', '2019', 'June', NULL, 39, 33, 27, 22, 17),
    ('Physics (AS)', 'Edexcel', 'Paper 2', '2019', 'June', NULL, 43, 37, 31, 25, 20),
    ('Physics (AS)', 'Edexcel', 'Paper 1', '2022', 'June', NULL, 42, 36, 30, 24, 18),
    ('Physics (AS)', 'Edexcel', 'Paper 2', '2022', 'June', NULL, 41, 35, 29, 23, 18),
    ('Physics (AS)', 'Edexcel', 'Paper 1', '2023', 'June', NULL, 45, 38, 31, 24, 18),
    ('Physics (AS)', 'Edexcel', 'Paper 2', '2023', 'June', NULL, 48, 41, 34, 27, 21),
    ('Physics (AS)', 'Edexcel', 'Paper 1', '2024', 'June', NULL, 45, 38, 31, 24, 18),
    ('Physics (AS)', 'Edexcel', 'Paper 2', '2024', 'June', NULL, 48, 41, 34, 27, 21),
    ('Physics (AS)', 'Edexcel', 'Paper 1', '2025', 'June', NULL, 50, 42, 34, 27, 20),
    ('Physics (AS)', 'Edexcel', 'Paper 2', '2025', 'June', NULL, 52, 44, 37, 30, 23),
    ('Chemistry (AS)', 'Edexcel', 'Paper 1', '2019', 'June', NULL, 58, 51, 44, 37, 31),
    ('Chemistry (AS)', 'Edexcel', 'Paper 2', '2019', 'June', NULL, 56, 49, 43, 37, 31),
    ('Chemistry (AS)', 'Edexcel', 'Paper 1', '2022', 'June', NULL, 51, 43, 36, 29, 22),
    ('Chemistry (AS)', 'Edexcel', 'Paper 2', '2022', 'June', NULL, 49, 41, 34, 27, 20),
    ('Chemistry (AS)', 'Edexcel', 'Paper 1', '2023', 'June', NULL, 49, 42, 35, 28, 22),
    ('Chemistry (AS)', 'Edexcel', 'Paper 2', '2023', 'June', NULL, 50, 43, 36, 29, 23),
    ('Chemistry (AS)', 'Edexcel', 'Paper 1', '2024', 'June', NULL, 56, 48, 40, 33, 26),
    ('Chemistry (AS)', 'Edexcel', 'Paper 2', '2024', 'June', NULL, 49, 42, 35, 29, 23),
    ('Chemistry (AS)', 'Edexcel', 'Paper 1', '2025', 'June', NULL, 54, 46, 39, 32, 25),
    ('Chemistry (AS)', 'Edexcel', 'Paper 2', '2025', 'June', NULL, 52, 45, 38, 32, 26),
    ('Biology (AS)', 'Edexcel', 'Paper 1', '2019', 'June', NULL, 54, 48, 42, 37, 32),
    ('Biology (AS)', 'Edexcel', 'Paper 2', '2019', 'June', NULL, 48, 43, 38, 33, 28),
    ('Biology (AS)', 'Edexcel', 'Paper 1', '2022', 'June', NULL, 52, 45, 38, 32, 26),
    ('Biology (AS)', 'Edexcel', 'Paper 2', '2022', 'June', NULL, 48, 41, 34, 28, 22),
    ('Biology (AS)', 'Edexcel', 'Paper 1', '2023', 'June', NULL, 56, 49, 42, 35, 28),
    ('Biology (AS)', 'Edexcel', 'Paper 2', '2023', 'June', NULL, 54, 47, 40, 33, 26),
    ('Biology (AS)', 'Edexcel', 'Paper 1', '2024', 'June', NULL, 59, 52, 45, 38, 32),
    ('Biology (AS)', 'Edexcel', 'Paper 2', '2024', 'June', NULL, 57, 50, 43, 36, 30),
    ('Biology (AS)', 'Edexcel', 'Paper 1', '2025', 'June', NULL, 59, 52, 45, 38, 32),
    ('Biology (AS)', 'Edexcel', 'Paper 2', '2025', 'June', NULL, 52, 46, 40, 34, 28);
