-- 042_exam_family_marks.sql
-- The mark basis a paper's scaled score is computed against.
--
-- The reference player scales a raw mark onto the family's full-test basis
-- before interpolating:
--
--     scaledForRaw(r) = scaledFrom40(r * family_marks / N)
--
-- For a 20-question TMUA paper that is r x 40/20, putting a single paper on the
-- two-paper sitting's 40-mark scale, exactly as engine spec section 1 says. For
-- a 27-question ESAT module it is r x 27/27, which is the identity, because
-- ESAT modules are scored separately as in the real test.
--
-- The value is carried in every paper JSON as `family_marks`, so it is stored
-- rather than derived from the family. Deriving it would be right today and
-- would silently ignore the file the day a paper says something different —
-- and the file is the author's statement of intent.
--
-- Backfilled from the family for the papers already loaded, which is correct
-- for all five: TMUA 40, ESAT 27.
--
-- Idempotent.

ALTER TABLE exam_papers
    ADD COLUMN IF NOT EXISTS family_marks INTEGER;

UPDATE exam_papers
   SET family_marks = CASE family WHEN 'TMUA' THEN 40 WHEN 'ESAT' THEN 27 END
 WHERE family_marks IS NULL;

ALTER TABLE exam_papers
    ALTER COLUMN family_marks SET NOT NULL;

-- A mark basis of zero would divide by zero in the scaling; a negative one is
-- meaningless. Guarded here rather than trusted from the JSON.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'exam_papers_family_marks_positive'
    ) THEN
        ALTER TABLE exam_papers
            ADD CONSTRAINT exam_papers_family_marks_positive
            CHECK (family_marks > 0);
    END IF;
END $$;
