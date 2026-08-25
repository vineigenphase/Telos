-- 009_de_boundaries.sql
-- Store the D and E grade boundaries that the exam boards actually publish.
--
-- grade_boundaries held A*/A/B/C only, and prediction.infer_de() extended the
-- mean gap downward to guess D and E. That was a reasonable approximation of
-- data we did not have — but we do have it: OCR and Pearson both print D and E
-- in the same tables the other four grades come from. Guessing a boundary when
-- the real one is published is indefensible in a product whose claim is that
-- predictions come from official boundaries.
--
-- The columns are nullable on purpose. A row entered by hand through the admin
-- screen, or a median assembled across years, may legitimately have no D/E, and
-- boundary_ladder falls back to inferring them for exactly those rows. Adding
-- the columns does not oblige anyone to fill them.
--
-- Additive and idempotent.

ALTER TABLE grade_boundaries ADD COLUMN IF NOT EXISTS d_boundary INTEGER;
ALTER TABLE grade_boundaries ADD COLUMN IF NOT EXISTS e_boundary INTEGER;
