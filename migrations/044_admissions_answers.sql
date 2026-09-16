-- 044_admissions_answers.sql
-- Record the letter a student chose, not just whether it was right.
--
-- The admissions tests are entirely multiple choice, and every question is
-- worth exactly one mark. That makes `question_marks.obtained` a 0 or a 1 and
-- `max_marks` always 1 — which is enough to score a paper and not enough to
-- review one. A student looking back at ENGAA 2021 wants to see that they put
-- D where the key says B, because the wrong option they were drawn to is the
-- misconception, and "you got Q14 wrong" does not name it.
--
-- So one nullable column rather than a parallel table. Every consumer of
-- question_marks — the heatmap, the prescription engine, the revision queue —
-- keeps working untouched on papers that never set it, which is every paper
-- logged before today and every written paper after it.
--
-- Deliberately TEXT and not a CHECK constraint on 'A'..'H'. ENGAA Part A ran to
-- H, the NSAA sections vary, and a future test with more options would fail a
-- constraint written from today's papers. The route validates against that
-- paper's own answer key, which is narrower than any constraint could be.
--
-- Idempotent.

ALTER TABLE question_marks
    ADD COLUMN IF NOT EXISTS answer_given TEXT;

COMMENT ON COLUMN question_marks.answer_given IS
    'Multiple-choice option the student selected, e.g. "D". NULL on written '
    'papers, and on MCQ papers the student self-marked rather than answered.';
