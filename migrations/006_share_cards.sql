-- 006_share_cards.sql
-- Phase 9: shareable card export. Additive and idempotent.
--
-- A row is created when a user exports a card. The token is the entire
-- security boundary — a shared card resolves to a public, unauthenticated
-- page — so it is generated with secrets.token_urlsafe, never from the user
-- id or a sequence. Anyone holding the link can read the payload, which is
-- why the payload stores only what the card itself already displays.
--
-- payload is a snapshot, deliberately not a live query. A card shared in
-- March must keep showing the March number; re-reading predictions at view
-- time would silently rewrite a student's shared result as their grade moved,
-- and would also leak their current data to everyone holding an old link.

CREATE TABLE IF NOT EXISTS share_cards (
    token       TEXT PRIMARY KEY,
    user_id     BIGINT      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_type   TEXT        NOT NULL,
    payload     JSONB       NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- "My share cards", newest first, for the eventual management view.
CREATE INDEX IF NOT EXISTS idx_share_cards_user
    ON share_cards (user_id, created_at DESC);
