-- 043_exam_paper_purchases.sql
-- Exam Mode papers become buyable individually, not Pro-only.
--
-- Phase 1 gated sitting a paper behind Pro. That is the wrong shape for the
-- thing most likely to sell: a candidate three weeks from the ESAT wants a
-- mock, not a subscription, and asking for £4.99 a month to sit one paper
-- loses the sale to anyone who only wants the paper.
--
-- So the same à-la-carte model the mock-paper marketplace already uses:
-- one-time Stripe Checkout, ownership recorded, and access checked against
-- ownership rather than plan. `purchases` is not reused because its
-- mock_paper_id is a NOT NULL foreign key into mock_papers — widening it would
-- make every existing row's meaning conditional.
--
-- Pro still includes every paper. Otherwise upgrading to Pro would take
-- something away from a subscriber, which is the one thing a plan change must
-- never do.
--
-- Idempotent.

ALTER TABLE exam_papers
    ADD COLUMN IF NOT EXISTS price_pence INTEGER NOT NULL DEFAULT 100;

COMMENT ON COLUMN exam_papers.price_pence IS
    'One-time price in pence. 0 means free to everyone; Pro includes every paper regardless.';

-- A paper cannot cost a negative amount, and a stray large value would be a
-- pricing accident nobody notices until a card is charged.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'exam_papers_price_sane'
    ) THEN
        ALTER TABLE exam_papers
            ADD CONSTRAINT exam_papers_price_sane
            CHECK (price_pence >= 0 AND price_pence <= 50000);
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS exam_purchases (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    paper_id          INTEGER NOT NULL REFERENCES exam_papers(id) ON DELETE CASCADE,
    stripe_session_id TEXT,
    purchased_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, paper_id)
);

CREATE INDEX IF NOT EXISTS exam_purchases_user ON exam_purchases (user_id);

-- The Mock A set at £1 each, which is where this started.
UPDATE exam_papers SET price_pence = 100
 WHERE paper_code IN ('TMUA-P1-A', 'TMUA-P2-A', 'ESAT-M1-A', 'ESAT-M2-A', 'ESAT-PHY-A');
