-- Webhook idempotency.
--
-- Stripe retries deliveries (and can send the same event more than once even
-- without a failure), so every handler has to be safe to run twice. Keying on
-- the Stripe event id and inserting BEFORE processing means a duplicate hits
-- the primary key and is dropped.

CREATE TABLE IF NOT EXISTS stripe_events (
    event_id     TEXT PRIMARY KEY,
    event_type   TEXT        NOT NULL,
    received_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stripe_events_received ON stripe_events (received_at);
