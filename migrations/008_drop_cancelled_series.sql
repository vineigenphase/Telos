-- 008_drop_cancelled_series.sql
-- Remove grade boundaries for the summer 2020 and 2021 series.
--
-- Those series did not happen. A-level exams in England were cancelled in both
-- years and grades were awarded by centre assessment (2020) and teacher
-- assessment (2021), so no exam boundaries were ever published. OCR's own
-- archive lists "no summer exam series" against both. Whatever the rows in
-- grade_boundaries were, they were not official — and this app's entire claim
-- is that a prediction is built from real boundaries.
--
-- Removing them is not a loss of information. prediction.select_boundaries
-- falls back to the median of the same paper in other years, so a student who
-- sits a 2020 paper as practice now gets a grade estimated from real series
-- instead of one derived from invented numbers. The papers themselves still
-- exist and stay loggable; only the fake boundaries go.
--
-- Idempotent: deleting rows that are already gone is a no-op.

DELETE FROM grade_boundaries WHERE year IN ('2020', '2021');
