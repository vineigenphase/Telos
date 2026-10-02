-- 050_mock_event_results.sql
-- Where a National Mock sitting is recorded, and the per-paper cohort summary.
--
-- Results are STORED, not computed on read, for the same reason exam_attempts
-- stores its metrics: the inputs are editable. A student's position is a record
-- of one sitting against one cohort at one moment, and if it were a live query
-- it would drift every time a late attempt was finalised or an anchor was
-- adjusted. A percentile that moves after it has been told to someone is worse
-- than no percentile.
--
-- Two tables because they answer different questions. mock_event_results is
-- "what did this student get"; mock_event_paper_stats is "what happened on this
-- paper", which is what the admin screen, the next event's copy and any claim
-- about the median all read from.
--
-- Idempotent, and so is the release script that fills these: both tables are
-- keyed so a re-run updates in place rather than appending a second set of
-- ranks.

CREATE TABLE IF NOT EXISTS mock_event_results (
    event_id    INTEGER NOT NULL REFERENCES mock_events(id) ON DELETE CASCADE,
    paper_id    INTEGER NOT NULL REFERENCES exam_papers(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- Which sitting counted. Named explicitly so a dispute can be settled by
    -- looking at the attempt rather than by trusting this row.
    attempt_id  INTEGER NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    raw         INTEGER NOT NULL,
    scaled      NUMERIC(3,1),
    -- NULL when the paper's cohort fell short, or when this sitter did not opt
    -- into the comparison. Both are ordinary outcomes, not missing data.
    rank        INTEGER,
    percentile  INTEGER,
    cohort_size INTEGER NOT NULL,
    in_cohort   BOOLEAN NOT NULL DEFAULT FALSE,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (event_id, paper_id, user_id)
);

CREATE INDEX IF NOT EXISTS mock_event_results_user
    ON mock_event_results (user_id);
CREATE INDEX IF NOT EXISTS mock_event_results_attempt
    ON mock_event_results (attempt_id);

COMMENT ON COLUMN mock_event_results.in_cohort IS
    'Whether this sitting counted toward the paper''s percentiles. False for '
    'anyone who left the cohort box unticked: they get their mark, their band '
    'and their topics, and no position.';
COMMENT ON COLUMN mock_event_results.cohort_size IS
    'The cohort this rank was measured against, stored alongside it. A rank '
    'without its denominator is not a result, and the denominator must not be '
    'recoverable only by re-running the script.';

CREATE TABLE IF NOT EXISTS mock_event_paper_stats (
    event_id    INTEGER NOT NULL REFERENCES mock_events(id) ON DELETE CASCADE,
    paper_id    INTEGER NOT NULL REFERENCES exam_papers(id) ON DELETE CASCADE,
    sitters     INTEGER NOT NULL DEFAULT 0,
    cohort      INTEGER NOT NULL DEFAULT 0,
    -- Whether percentiles were published for this paper at all. Recorded
    -- rather than re-derived from cohort >= min_cohort, because min_cohort can
    -- be changed afterwards and this has to keep saying what was actually done.
    published   BOOLEAN NOT NULL DEFAULT FALSE,
    raw_max     INTEGER,
    raw_min     INTEGER,
    raw_mean    NUMERIC(6,2),
    raw_median  NUMERIC(6,2),
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (event_id, paper_id)
);

COMMENT ON TABLE mock_event_paper_stats IS
    'One row per paper per event: how many sat it, how many counted, whether '
    'percentiles were published, and the spread. The source for any public '
    'claim about what the cohort scored.';
