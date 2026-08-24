# Telos — where we left off

**Last updated: 2026-08-25.** Living handoff document. Read this first, then
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
- **Local:** path varies by machine — `C:\Users\User\Telos` on one,
  `C:\Users\svinu\past_paper_tracker` on another. Same repo either way.

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
| 2.5 | PWA — manifest, service worker, install prompt, offline shell (a-d; 2.5e web push deferred) | `891147a` | **live** |
| 4 | Prescriptions — "your next 3 questions", Today panel | `98c0589` | **live** |
| — | UI overhaul — Editorial treatment across all twelve screens, new stroke logo | `7df213d` | **live** |
| 9 | Shareable card export — the growth engine | `feat/share-cards` | **built, awaiting sign-off** |
| 6, 8, 7, 10 | Spaced repetition, parent report, percentile, simulator | — | not started |

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
5. **Phase 2.5 device checks** — Lighthouse PWA audit on telosapp.co.uk;
   install to home screen on a real iPhone and a real iPad and confirm it
   opens without browser chrome, correct icon/splash; confirm an
   already-installed copy picks up a new deploy within one refresh
   (the "Update available" toast).
6. **Phase 4 on a real phone.** The Today panel was measured at 390px in an
   iframe (no horizontal overflow, 76px question rows, the due row exactly at
   the 44px floor) but never opened on actual hardware. Also worth confirming
   the picks feel right against your own logged papers rather than seeded ones.
7. **The Today panel's "Revision due" section is wired but unexercised.** It
   only rendered during review because three synthetic `revision_queue` rows
   were inserted by hand. Nothing writes to that table until Phase 6, so in
   production the count is 0 and the section is hidden. Ready, not working.
8. **2.5e, web push** — deliberately not built yet. Needs VAPID keys and a
   `push_subscriptions` table; the addendum says ship the rest of 2.5 first,
   which is what happened.
9. **The UI overhaul on real hardware.** Every screen was reviewed in the
   browser (and at 390px in a same-origin iframe, per the auditing gotcha
   below), but none of it has been opened on an actual phone or tablet. Worth
   a pass over the dashboard, the phone mark-entry flow and the three admin
   screens, since those were the last built and got the least eyes.

**Settled — don't re-litigate:**

**Phase 4 shipped 2026-08-23**, signed off by the owner after a visual review.
Two deliberate departures from the spec are baked in:

- The spec sources questions from `bank_questions`. That table does not exist —
  the real one is **`question_bank`**, it is per-user, and it was empty for
  every user at launch. A spec-literal Phase 4 would have rendered an empty
  panel on day one. It ships with two sources instead: unattempted
  `question_bank` questions first, then re-doing sub-60% questions from
  `question_marks`. The spec's own rule ("preferring unattempted questions,
  then ones scored below 60%") already assumes attempt data, which only the
  marks table has.
- Prescriptions are computed on read, not cached like predictions. They depend
  on the question bank as well as the marks, so a cache would need invalidating
  from the `/bank` tag and delete routes too. See the docstring on
  `build_prescriptions()`. Revisit only if the dashboard gets slow.

**UI overhaul shipped 2026-08-24** (`7df213d`, merged straight to `main` after
the owner reviewed the branch on GitHub). All twelve screens from the brief are
on the Editorial treatment, plus the new stroke logo. Three things to know:

- **The trend deltas read blank for the first week, on purpose.** Migration 005
  added `question_marks.created_at` and `grade_prediction_history` because three
  of the four headline deltas were not computable before it — there was no
  timestamp on a mark, and `grade_predictions` was upserted in place so the
  previous prediction was overwritten every recompute. Neither is backfillable.
  The dashboard shows a bare stat rather than inventing a delta. Don't "fix"
  the empty deltas; wait for the data.
- **Five templates were never restructured** — `_upgrade_prompt`, `bank_tag`,
  `bank_upload`, `papers_enter`, `papers_entry`. They carry no hardcoded hexes,
  only CSS variables, so they picked up the new palette for free and nothing
  renders the old purple. They do still lay out via inline styles if anyone
  wants to finish the job.
- **Pro Zone posts use `.post-*`, not `.entry-*`.** That namespace already
  belongs to the phone mark-entry flow — fourteen classes of it.

**Phase 9 is built but not merged.** Five commits on `feat/share-cards`, all
tests green (12 suites). Migration 006 is already applied to production — it is
additive and nothing in `main` reads it. Two departures from the spec, both
agreed with the owner before building:

- **The card page is `noindex`.** A student chose to show a result to the people
  they sent it to, which is not the same as agreeing to surface in a search for
  their name. `/s/` is deliberately NOT disallowed in robots.txt: a crawler has
  to be able to fetch the page to read the noindex.
- **Cards can be revoked**, which the spec doesn't mention. A permanent public
  page of your own grades that you can't take down is the wrong default.
  Revoking deletes the row, so the link 404s rather than going blank.

**The spec's "streak" card has no data behind it.** Phase 9's card types are
listed as "predicted grade / heatmap snapshot / streak or papers-completed
milestone". Nothing in Telos tracks consecutive days — there is no streak
field anywhere in the schema — so the milestone card ships as papers-completed.
`render_milestone` already takes `unit="days"` and will render a day streak the
moment something computes one; per the UI brief's rule, this is flagged rather
than faked with a placeholder number.

**A free account cannot make the grade card**, and that is correct rather than
a bug. Prediction is the Pro half of the free/Pro split, so a free user has
accuracy and papers-logged to share but no predicted grade. The dashboard
offers only the cards the data supports.

**Decisions waiting on the owner:**

10. **`db.py` connection check.** The first request after Neon idles returns a
   500 (`AdminShutdown: terminating connection due to administrator command`);
   the retry works. Fix is one argument — `check=ConnectionPool.check_connection`
   on the pool. Not applied because spec working-rule 7 says don't touch
   `db.py` without asking.
11. **D/E grade boundaries.** `grade_boundaries` stores A*/A/B/C only.
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
- **`railway run tests\run_all.py` used to fail 5 of 6 suites** on any
  machine, because `railway run` injects the real production `CANONICAL_HOST`
  into every subprocess, and the Flask test client's default Host header
  ("localhost") then gets 301'd by the canonical-redirect hook — which
  Werkzeug's test client refuses to follow. Fixed in `run_all.py`: it strips
  `CANONICAL_HOST` from each suite's env except `test_canonical_host.py`,
  which wants the real thing. If a suite is ever run standalone
  (`python tests\test_x.py` directly, not via `run_all.py`) under
  `railway run`, this will resurface.
- **The spec's `bank_questions` is really `question_bank`.** Per-user, filled
  only by that user's own upload-and-tag flow, and its `topics` column is a
  JSON array — `question_marks.topic` is a single string. Phase 4 matches the
  two case- and whitespace-insensitively.
- **Migrations do not run on deploy.** `Procfile` is bare gunicorn and nothing
  in `app.py` calls the runner, so pushing `main` deploys code against whatever
  schema production already has. Run
  `railway run .venv\Scripts\python.exe migrations\run_migrations.py` **before**
  the push, never after — the window between the two is a live 500 for every
  user if the new code reads a column that isn't there yet. Migrations are
  additive and idempotent by convention, so applying one against the old
  running code is always safe.
- **`railway run` needs quoted backslash paths.** `railway run .venv/Scripts/...`
  fails — the command is handed to `cmd.exe`, which won't take a forward-slash
  executable path. Unquoted backslashes get eaten as escapes by the shell.
  Quote both arguments: `railway run ".venv\Scripts\python.exe" "path\to.py"`.
- **`db.Row` subclasses `dict`, so `tuple(row)` gives you the column names,**
  not the values. Index by key. The entry point is `db.get_db()`; there is no
  `get_conn()`.
- **PWA icons are generated, not hand-drawn.** `scripts\generate_icons.py`
  builds them from CSS values (the sidebar gradient, the heatmap's
  `pct-0..90` colors) — re-run it after changing either, don't edit the PNGs.

---

## Conventions

- One phase per branch, one commit per phase, sign-off before merging to `main`
  (merging auto-deploys).
- Schema changes only via numbered files in `migrations/`, each idempotent.
- Never hardcode a price in a template — read from `PRICING` in `app.py`.
- Postgres `LIKE` is case-sensitive; use `ILIKE` for anything user-facing.
- Don't touch `db.py`, `migrate_to_postgres.py` or `scan_sqliteisms.py` without
  asking.
