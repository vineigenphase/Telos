-- 048_mock_events.sql
-- The National Mock: a timed cohort event, and the attribution to measure it.
--
-- Everyone sits the same papers in the same window, so a percentile means
-- something. The window lives in a row rather than a constant because the
-- owner has already moved it once — from Sunday 4 October to Friday 2 October
-- — and on the day itself the only safe way to extend it is an UPDATE, not a
-- deploy. The runbook depends on that.
--
-- Times are stored in UTC. The UK is on BST until the last Sunday in October,
-- so the 10:00-22:00 local window is 09:00-21:00Z. Getting this wrong by an
-- hour would open the event while the owner is still asleep.
--
-- Idempotent throughout.

CREATE TABLE IF NOT EXISTS mock_events (
    id                  SERIAL PRIMARY KEY,
    slug                TEXT NOT NULL UNIQUE,
    title               TEXT NOT NULL,
    window_start        TIMESTAMPTZ NOT NULL,
    window_end          TIMESTAMPTZ NOT NULL,
    paper_codes         TEXT[] NOT NULL,
    results_released_at TIMESTAMPTZ,
    min_cohort          INT NOT NULL DEFAULT 20
);

COMMENT ON COLUMN mock_events.min_cohort IS
    'Below this many opted-in sitters, a paper''s percentiles are suppressed '
    'entirely. A rank among eleven people is noise presented as information.';

-- Friday 2 October 2026, 10:00-22:00 BST.
INSERT INTO mock_events (slug, title, window_start, window_end, paper_codes)
VALUES ('nm1', 'Telos National Mock',
        '2026-10-02 09:00:00+00', '2026-10-02 21:00:00+00',
        ARRAY['TMUA-P1-A', 'TMUA-P2-A', 'ESAT-M1-A', 'ESAT-M2-A', 'ESAT-PHY-A'])
ON CONFLICT (slug) DO UPDATE
   SET window_start = EXCLUDED.window_start,
       window_end   = EXCLUDED.window_end,
       paper_codes  = EXCLUDED.paper_codes;

CREATE TABLE IF NOT EXISTS mock_event_entries (
    event_id         INTEGER NOT NULL REFERENCES mock_events(id) ON DELETE CASCADE,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source           TEXT,
    percentile_optin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (event_id, user_id)
);

CREATE INDEX IF NOT EXISTS mock_event_entries_event ON mock_event_entries (event_id);

COMMENT ON COLUMN mock_event_entries.percentile_optin IS
    'Unticked by default, per the Phase 7 spec and the ICO Children''s Code: '
    'most of these users are 16-18, so sharing a score into a cohort is '
    'something they choose, not something they are enrolled in.';

-- Attribution and referral, on users.
ALTER TABLE users ADD COLUMN IF NOT EXISTS signup_source    TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code    TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by      INTEGER
      REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS marketing_optin  BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bonus_pro_until  TIMESTAMPTZ;

COMMENT ON COLUMN users.signup_source IS
    'First-touch source code from ?r= at the landing, e.g. tt-03 or sch-foo. '
    'First touch, not last: the video that found them is the one that worked.';
COMMENT ON COLUMN users.bonus_pro_until IS
    'Pro granted by referral, never by Stripe. The webhook must not touch it.';

-- Backfill referral codes for everyone who already has an account, then make
-- the column unique. Derived from the id through md5 rather than from the id
-- directly, so the codes are not a sequence anyone can walk.
UPDATE users
   SET referral_code = upper(substr(md5('telos-nm-' || id::text), 1, 7))
 WHERE referral_code IS NULL;

DO $$
DECLARE
    dupes INT;
BEGIN
    SELECT COUNT(*) INTO dupes FROM (
        SELECT referral_code FROM users
         WHERE referral_code IS NOT NULL
         GROUP BY referral_code HAVING COUNT(*) > 1) d;
    IF dupes > 0 THEN
        RAISE EXCEPTION 'referral_code collision on % code(s); widen the substr',
            dupes;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'users_referral_code_key'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT users_referral_code_key
              UNIQUE (referral_code);
    END IF;
END $$;
