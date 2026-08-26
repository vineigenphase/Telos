-- 037_boundary_derived_flag.sql
-- Marks a boundary row as derived rather than published.
--
-- Every row in this table until now came from an awarding body's own
-- document. The SQA rows do not: SQA publishes grade boundaries at course
-- level only, so a component's boundary is that component's share of the
-- course cut-off. That is an estimate, and an estimate that is
-- indistinguishable from published data is a trap for whoever reads this
-- table next.
--
-- Idempotent.

ALTER TABLE grade_boundaries
    ADD COLUMN IF NOT EXISTS derived_from_course BOOLEAN NOT NULL DEFAULT FALSE;
