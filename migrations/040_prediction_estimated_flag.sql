-- 040_prediction_estimated_flag.sql
-- Marks a cached prediction as resting on estimated boundaries.
--
-- grade_boundaries.derived_from_course (migration 037) says a BOUNDARY was
-- computed rather than published. This is the same fact carried forward to the
-- PREDICTION built from it, because the dashboard reads the cache and never
-- recomputes, so without it the dashboard has no way to know.
--
-- Only SQA produces these today: it publishes cut-off scores for the whole
-- course and never per component, so a component boundary is that component's
-- share of one. A student should be told that rather than shown an estimate
-- with the same authority as an AQA boundary.
--
-- Existing rows default to FALSE, which is correct for every prediction made
-- before SQA existed in the catalogue. They are recomputed on the owner's next
-- mark entry anyway.
--
-- Idempotent.

ALTER TABLE grade_predictions
    ADD COLUMN IF NOT EXISTS estimated BOOLEAN NOT NULL DEFAULT FALSE;
