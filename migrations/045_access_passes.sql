-- 045_access_passes.sql
-- Time-limited access to one test's material, bought once.
--
-- The gap this fills. Exam Mode sells a paper outright at £1 and Pro sells
-- everything at £4.99 a month. Neither suits a candidate four weeks from the
-- TMUA who wants the whole of one test and nothing else: buying the two mocks
-- individually gets them two mocks and none of the eighteen official papers,
-- and a subscription is a commitment to a product they will stop needing in
-- November.
--
-- So a pass: one payment, one test, thirty days. Not a subscription — there is
-- nothing to cancel, nothing renews, and a student who forgets about it is
-- charged once. That is deliberate. A recurring charge aimed at people with a
-- deadline collects most of its money from the months after they stop caring.
--
-- `scope` is the test family ('TMUA'), not a paper id, because the thing being
-- sold is "everything TMUA" — both Exam Mode mocks and all eighteen official
-- papers with their keys and PDFs. ESAT or ENGAA passes would be new rows, not
-- new tables.
--
-- Rows are never deleted and never updated to a shorter window. A lapsed pass
-- is history: it says this student had access in October, which is the honest
-- answer when they ask why a paper they once opened is now locked. Re-buying
-- extends `expires_at` from whichever is later, now or the current expiry, so
-- a second purchase before the first lapses adds thirty days rather than
-- throwing away what is left.
--
-- `stripe_session_id` is UNIQUE, and that is what makes granting idempotent.
-- Both the webhook and the /success route try to write the same row, because
-- either may arrive first and neither is guaranteed to arrive at all — the
-- student may close the tab, or the webhook may be delayed. The unique
-- constraint means the second one to land changes nothing.
--
-- Idempotent.

CREATE TABLE IF NOT EXISTS access_passes (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scope             TEXT NOT NULL,
    granted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at        TIMESTAMPTZ NOT NULL,
    price_pence       INTEGER NOT NULL DEFAULT 0,
    stripe_session_id TEXT UNIQUE
);

CREATE INDEX IF NOT EXISTS access_passes_user_scope
    ON access_passes (user_id, scope, expires_at DESC);

COMMENT ON COLUMN access_passes.scope IS
    'Test family the pass covers, e.g. "TMUA". Not a paper id: the pass sells '
    'every paper of one test, mocks and official papers alike.';
COMMENT ON COLUMN access_passes.expires_at IS
    'When access stops. Rows outlive it — a lapsed pass is the record that '
    'this student did have access, which is why a paper they opened is locked.';
