-- 007_physics_boundaries.sql
-- Replace the OCR A Physics grade boundaries with the official per-paper ones.
--
-- Two faults, both fatal to a Physics prediction.
--
-- 1. Granularity. The rows held the OVERALL qualification boundary (out of 270,
--    all three papers summed) under the paper_code "Overall". Students log one
--    paper at a time, out of 100 or 70. prediction.select_boundaries falls back
--    to "same subject, same year" when it cannot match a paper code, so a
--    60/100 Paper 1 was being compared against a 270-mark scale and graded U.
--
-- 2. A column shift. Every stored row was the official Overall row moved one
--    place right: the max mark (270) sat in a_star, A* sat in a, A in b, B in
--    c, and C was dropped. That is why a_star read 270 in every single year.
--    Confirmed against OCR's published PDFs for all six series.
--
-- The replacement is per-paper, from OCR's own documents:
--   Paper 1 = H556/01 Modelling physics (100)
--   Paper 2 = H556/02 Exploring physics (100)
--   Paper 3 = H556/03 Unified physics    (70)
-- The app's max marks for these three papers already agree with OCR's, which
-- is what makes the mapping unambiguous.
--
-- 2020 and 2021 are absent deliberately: there was no summer exam series in
-- either year, so no official boundaries exist. The rows previously stored for
-- them were not real. A student logging a 2020 paper now falls back to the
-- median of the real years, which is the honest answer.
--
-- "Physics B"/"OCR" is deleted outright. It is not in paper_templates.py, so
-- no user can select it, and its rows carried the same column shift.
--
-- Idempotent: deletes the subject's rows, then reinserts the official set.

DELETE FROM grade_boundaries WHERE subject = 'Physics B' AND board = 'OCR';
DELETE FROM grade_boundaries WHERE subject = 'Physics' AND board = 'OCR A';

INSERT INTO grade_boundaries
    (subject, board, paper_code, year, series, a_star, a_boundary, b_boundary, c_boundary)
VALUES
    ('Physics', 'OCR A', 'Paper 1', '2018', 'June', 83, 72, 60, 49),
    ('Physics', 'OCR A', 'Paper 2', '2018', 'June', 81, 69, 57, 46),
    ('Physics', 'OCR A', 'Paper 3', '2018', 'June', 55, 47, 39, 31),
    ('Physics', 'OCR A', 'Paper 1', '2019', 'June', 88, 80, 70, 59),
    ('Physics', 'OCR A', 'Paper 2', '2019', 'June', 87, 77, 65, 53),
    ('Physics', 'OCR A', 'Paper 3', '2019', 'June', 55, 47, 39, 32),
    ('Physics', 'OCR A', 'Paper 1', '2022', 'June', 83, 73, 60, 47),
    ('Physics', 'OCR A', 'Paper 2', '2022', 'June', 79, 67, 54, 41),
    ('Physics', 'OCR A', 'Paper 3', '2022', 'June', 49, 41, 33, 25),
    ('Physics', 'OCR A', 'Paper 1', '2023', 'June', 74, 65, 54, 43),
    ('Physics', 'OCR A', 'Paper 2', '2023', 'June', 81, 69, 57, 45),
    ('Physics', 'OCR A', 'Paper 3', '2023', 'June', 56, 48, 40, 32),
    ('Physics', 'OCR A', 'Paper 1', '2024', 'June', 72, 63, 52, 42),
    ('Physics', 'OCR A', 'Paper 2', '2024', 'June', 84, 70, 58, 46),
    ('Physics', 'OCR A', 'Paper 3', '2024', 'June', 51, 42, 36, 29),
    ('Physics', 'OCR A', 'Paper 1', '2025', 'June', 75, 66, 56, 46),
    ('Physics', 'OCR A', 'Paper 2', '2025', 'June', 84, 74, 62, 50),
    ('Physics', 'OCR A', 'Paper 3', '2025', 'June', 47, 39, 33, 27);
