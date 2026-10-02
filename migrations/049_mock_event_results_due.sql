-- 049_mock_event_results_due.sql
-- When results are promised, as a column rather than a line of copy.
--
-- The closed-state page has one job: bring people back. "Results tomorrow"
-- does that badly; a stated time does it well. And the time has to live in the
-- row, because the whole point of the runbook is that the owner can move it
-- with an UPDATE at 22:30 on the night if marking the cohort takes longer than
-- planned — a promise in a template can only be moved by a deploy.
--
-- Distinct from results_released_at, which stays NULL until the release script
-- in W4 actually runs. One is a promise, the other is a fact.
--
-- Saturday 3 October 2026, 08:00 BST = 07:00Z. Moved forward with the event
-- itself: the original plan released on Monday 5 October, two days after a
-- Sunday sitting, and a Friday sitting cannot wait until Monday without losing
-- every share the result card was built to earn.

ALTER TABLE mock_events ADD COLUMN IF NOT EXISTS results_due_at TIMESTAMPTZ;

UPDATE mock_events
   SET results_due_at = '2026-10-03 07:00:00+00'
 WHERE slug = 'nm1' AND results_due_at IS NULL;

DO $$
DECLARE
    due TIMESTAMPTZ;
    ends TIMESTAMPTZ;
BEGIN
    SELECT results_due_at, window_end INTO due, ends
      FROM mock_events WHERE slug = 'nm1';
    IF due IS NULL OR due <= ends THEN
        RAISE EXCEPTION
            'nm1 results_due_at (%) must fall after the window closes (%)',
            due, ends;
    END IF;
END $$;
