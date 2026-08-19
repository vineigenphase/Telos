# Telos — where we left off

**Last updated: 2026-08-19.** Living handoff document. Read this first, then
`TELOS_V2_SPEC.md` and `TELOS_V2_ADDENDUM.md` (the addendum reorders the
phases and adds the mobile/PWA work).

Update this file whenever a phase ships. It is the one thing that survives a
wiped machine, because it lives in the GitHub repo.

---

## What Telos is

A Flask past-paper tracker for A-level students. Log past papers, enter marks
per question, see weak topics, get a predicted grade. Free tier = diagnosis;
Pro tier = prediction and prescription.

- **Live:** https://telosapp.co.uk
- **Repo:** github.com/vineigenphase/Telos (auto-deploys `main`)
- **Local:** `C:\Users\User\Telos`

---

## Infrastructure

| Piece | Detail |
|---|---|
| Host | Railway, project `hospitable-illumination`, service `web`, EU West |
| Database | Neon Postgres, eu-west-2 London. Use the **direct** connection string, not `-pooler` — psycopg3 prepared statements clash with PgBouncer |
| DB layer | `db.py` — a psycopg3 shim that makes Postgres quack like the old `sqlite3` API (`?` placeholders, `.lastrowid`, sqlite3.Row-alike) |
| Files | Railway volume `web-volume` at `/data`; `STORAGE_DIR` → `/data/uploads` and `/data/mocks` |
| DNS | Cloudflare. Apex CNAME-flattened to Railway. **Records must stay DNS-only (grey cloud)** or Railway cert validation breaks |
| Email | Resend, sending as `noreply@telosapp.co.uk`, DKIM/SPF/MX verified |
| Payments | Stripe, **test mode** |
| Git auth | Repo-scoped PAT in Windows Credential Manager, so `git push` just works |

### Environment variables (values live in Railway, never in git)

`DATABASE_URL`, `SECRET_KEY`, `STORAGE_DIR`, `CANONICAL_HOST`,
`RESEND_API_KEY`, `MAIL_FROM`, `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`,
`STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_MONTHLY`, `STRIPE_PRICE_ANNUAL`,
`STRIPE_PRICE_LEGACY`, `STRIPE_PRICE_ID` (old name for legacy).

See `.env.example`. Pull real values with `railway variables`.

---

## Phase status

Order (from the addendum): `0 → 0.4 → 0.6 → 1 → 2 → 3 → 2.5 → 5 → 4 → 9 → 6 → 8 → 7 → 10`

| Phase | What | Commit | Status |
|---|---|---|---|
| 0 | Data-driven pricing table, fixed Free/Pro contradiction | `f7fad02` | **live** |
| 0.4 | Custom domain, canonical-host 301, HTTPS + cookie hardening, robots/sitemap | `fbe12c5` | **live** |
| 0.6 | Mobile-first CSS, bottom tab bar, phone mark entry, per-topic heatmap | `f6ac99c` | **live** |
| 1 | Schema for tiers/plans, migrations framework | `edc6343` | **live** |
| 2 | Access control, `user_is_pro` single source of truth | `616346b` | **live** |
| 3 | Predicted grade engine | `36cdb62` | **live** |
| 5 | £4.99/mo + £29/yr, webhook-only entitlements, billing portal, analytics | `da0b797` | **live** |
| — | Password reset via emailed single-use link | `34faf81` | **live** |
| 2.5 | PWA — manifest, service worker, install prompt | — | **next** |
| 4 | Prescriptions — "your next 3 questions" | — | not started |
| 9, 6, 8, 7, 10 | Share cards, spaced repetition, parent report, percentile, simulator | — | not started |

---

## Open items

**Needs a human (I can't do these):**

1. **Phone test of Phase 0.6** — log an 8-question paper one-handed and time
   it; target is under 60 seconds. And with airplane mode on, entering a mark
   must show *"Not saved yet — will retry"*, never a false *"Saved"*.
2. **Real Stripe checkout** with card `4242 4242 4242 4242` on the £29 plan,
   confirming the webhook grants Pro within seconds.
3. **Cancel → period-end → access-lost** path via Stripe clock simulation.
4. **Live-mode Stripe swap** when ready for real money: recreate product,
   both prices and the webhook endpoint in live mode, update the four env vars.

**Decisions waiting on the owner:**

5. **`db.py` connection check.** The first request after Neon idles returns a
   500 (`AdminShutdown: terminating connection due to administrator command`);
   the retry works. Fix is one argument — `check=ConnectionPool.check_connection`
   on the pool. Not applied because spec working-rule 7 says don't touch
   `db.py` without asking.
6. **D/E grade boundaries.** `grade_boundaries` stores A*/A/B/C only.
   `prediction.infer_de()` extrapolates D and E from the mean gap of the known
   boundaries. Owner approved keeping this (2026-08-19); revisit if real D/E
   data is ever sourced. Delete that one function if so.

**Known good, don't "fix":**

- Founder account (`svinujan10@gmail.com`, user 1) is `grandfathered=true` on
  purpose — permanent free Pro. It also means that account never sees the
  checkout UI.
- The legacy £2 Stripe price stays **active and unsellable**. Never migrate or
  cancel those subscribers.

---

## Running it

```bash
# Local dev server, with production env injected (no .env file on this machine)
cd C:\Users\User\Telos
railway run .venv\Scripts\python.exe app.py        # http://127.0.0.1:5000

# CANONICAL_HOST must be EMPTY locally or you get a redirect loop over http.
# STORAGE_DIR should point at .\storage, not /data.

# All test suites (talks to the real Neon DB; cleans up after itself)
railway run .venv\Scripts\python.exe tests\run_all.py

# Migrations — numbered, idempotent, safe to re-run
railway run .venv\Scripts\python.exe migrations\run_migrations.py
```

Local dev runs against the **production** database. Fine while there's one
user; use a Neon branch once there are real students.

---

## Gotchas that cost real debugging time

- **`StripeObject.get()` raises.** It subclasses `dict` but routes attribute
  access through `__getattr__`, so `obj.get("x")` throws `AttributeError`
  instead of returning a default. Use `app._sget()` for webhook payloads.
- **Resend is behind Cloudflare.** Default `Python-urllib/3.x` User-Agent gets
  a 403 with body `error code: 1010`, which looks exactly like a bad API key.
  `mailer.py` sends an explicit User-Agent.
- **`.main` needs `min-width: 0`.** It's a flex item; without it the paper
  matrix drags the whole page into horizontal scroll (251px at 768px).
- **Touch targets are gated on `(pointer: fine)`, not width.** A 768px iPad is
  still a finger. Don't move those relaxations into a width breakpoint.
- **`login.html` and `register.html` don't extend `base.html`.** They carry
  their own `<head>`, so viewport/canonical/meta changes must be made in three
  places.
- **The webhook route is `/subscription/webhook`**, not `/stripe/webhook` as
  the spec's Phase 5 text assumes.
- **Auditing responsive layout on this machine:** Chrome won't resize below the
  display width. Load the page in a same-origin iframe at the target width
  instead, and strip the `(hover:hover)` media rule before measuring tap
  targets or you measure mouse-sized controls.

---

## Conventions

- One phase per branch, one commit per phase, sign-off before merging to `main`
  (merging auto-deploys).
- Schema changes only via numbered files in `migrations/`, each idempotent.
- Never hardcode a price in a template — read from `PRICING` in `app.py`.
- Postgres `LIKE` is case-sensitive; use `ILIKE` for anything user-facing.
- Don't touch `db.py`, `migrate_to_postgres.py` or `scan_sqliteisms.py` without
  asking.
