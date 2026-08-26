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

Order (from the addendum): `0 → 0.4 → 0.6 → 1 → 2 → 3 → 2.5 → 5 → 4 → 9 → 6 → 7 → 10`
(Phase 8, the weekly parent report, was cut on 2026-08-25.)

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
| 9 | Shareable card export — the growth engine | `0df51d7` | **live** |
| — | Page loader — the mark charges during navigation | `0df51d7` | **live** |
| 6, 7, 10 | Spaced repetition, percentile, simulator | — | not started |
| 8 | Weekly parent report | — | **cut** (2026-08-25) |

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

**Phase 9 shipped 2026-08-25** (`0df51d7`), together with the page loader. Two
departures from the spec, both agreed with the owner before building:

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

**The page loader is deliberately shy, and deliberately inert until needed.** It
waits 180ms before appearing, because a loader that flashes on every fast click
makes an app feel less settled rather than more. It animates only transform and
opacity — the charge is two counter-translated transforms, not an animated
height or clip-path — because it plays exactly while the main thread is busy
parsing the next document, which is when anything layout-driven would stutter.
And it ships as an inert `<template>` that `telos.js` clones on first use: a
`position:fixed inset:0` element in live markup becomes an opaque sheet over
the whole app if its stylesheet ever fails to arrive. Don't "simplify" any of
those three into the obvious version.

**The Neon wake-up 500 is fixed** (2026-08-25, owner approved touching `db.py`).
The pool now passes `check=ConnectionPool.check_connection`, which tests a
connection on checkout and replaces a dead one. Note the old description of the
symptom here was wrong in a way that mattered: it said the first request after
an idle period fails and "the retry works". In practice the pool holds several
connections and each request borrows a different one, so a wake-up could
produce a *run* of 500s — the app looked broken rather than slow.
`tests/test_db_resilience.py` reproduces it by killing a backend from a second
connection, and was confirmed to fail without the argument. Cost is one
round-trip per checkout.

**Decisions waiting on the owner:**

10. *(settled 2026-08-25 — see "Grade boundaries" below.)*

**Grade boundaries were substantially wrong, and are now sourced from the
boards' own PDFs** (2026-08-25, migrations 007-011).

- **Physics predicted U on papers scoring 81-90%.** The rows held the OVERALL
  qualification boundary — out of 270, all three papers summed — under the
  paper code "Overall", while students log one paper at a time out of 100 or
  70. `select_boundaries` cannot match "Paper 1", falls back to "same subject,
  same year", and measured an 85/100 against an A boundary of 219. Every one of
  those rows was *also* shifted a column, with the max mark sitting in `a_star`
  — which is why `a_star` read 270 in all eight years. Replaced with OCR's
  per-paper raw boundaries: Paper 1 = H556/01 (100), Paper 2 = H556/02 (100),
  Paper 3 = H556/03 (70).
- **Summer 2020 and 2021 boundaries were invented.** Those series were
  cancelled; grades came from centre and teacher assessment and no boundaries
  were published. All such rows are deleted, for every subject. A 2020 paper now
  falls back to the median of real years.
- **The Edexcel data was checked and is correct.** All 21 Further Maths and
  Maths rows Pearson publishes notional component boundaries for across
  2022-2025 match exactly, as do the 2019 rows' A/B/C. Only OCR was wrong.
- **D and E are now the published values** where the board prints them (46 of
  83 rows). `infer_de()` remains for the rest — hand-entered rows and medians
  across years carry only four boundaries — but it is the fallback, not the
  rule.

**Don't hand-type boundary data.** Migrations 007, 010 and 011 were generated by
scripts that parse the official PDFs, because eighteen rows of six numbers typed
by hand is precisely how the Physics data came to be shifted a column. The
generators also refuse to write: 011 re-reads each row's official A/B/C and
declines unless they match what is stored, so a mis-parse produces nothing
rather than something plausible.

**`tests/test_boundaries.py` guards the class of fault, not the instance.** No
boundary may exceed or equal its paper's max mark (a 270 against a 100-mark
paper is invisible when reading numbers and obvious when comparing them to the
paper), A*>A>B>C must hold, C>D>E>0 wherever D/E exist, every offered paper
needs data, and no cancelled series may reappear.

**Pearson's 2019 file uses two layouts.** Most sections print
"Max Mark A* A B C D E U"; Mathematics and Further Mathematics print
"Max Mark A B C D E U" with no A* at component level, and zero-padded paper
labels. The A* figures stored for 2019 did not come from that document and are
left as they are.

**Six Further Maths papers have boundaries but cannot be logged.** Edexcel
publishes FP1, FP2, FS2, FM2, D1 and D2; `paper_templates.py` offers only CP1,
CP2, FM1, FS1. Students on those options have nowhere to put them. Real data,
missing feature — `test_boundaries.py` prints it as a NOTE on every run.

**The subject catalogue now covers 21 qualifications across five boards**
(2026-08-25/26, migrations 012-033). Every board was onboarded the same way,
and the method is the point:

> download the board's own PDFs -> write or extend a parser for that board's
> layout -> **validate every component against its own expected max mark** ->
> generate the migration SQL *by script, never by hand* -> cross-check against a
> second source where one exists -> author topics from the specification ->
> run the suites -> deploy.

The expected-max guard has caught a genuine fault on **every** board it was
pointed at. It is not ceremony.

- **Each board prints boundaries differently, and all the layouts are handled.**
  OCR uses three table layouts. Pearson uses four, including one with a single
  number per line (2024) and one row whose paper label is simply missing
  (Physics 2019 Paper 2, where the label line reads `9PE0`) — that one is placed
  only when exactly one paper is unaccounted for and exactly one unlabelled row
  of that max mark remains, and it prints a note when it fires. AQA scales its
  language components and publishes both a raw and a scaled row, so taking the
  last match would double every boundary.
- **Students see only the modules they chose.** `visible_papers()` returns the
  compulsory papers always, and an optional paper only if that student picked
  it. A student who has picked nothing sees the compulsory papers alone, not
  every option in the catalogue. `paper_options()` is the single source for
  which is which.
- **A signed-in student with no subjects is redirected to choose them**
  (`_require_subject_setup`, with `SETUP_EXEMPT` for the routes that must stay
  reachable). This broke four integration suites whose throwaway users had no
  subjects; each now gets a `user_subjects` row, which is a more honest fixture
  anyway.

**Coursework and speaking components count toward the grade, and were missing**
(2026-08-26, migration 033). Geography's fieldwork investigation (7037/C, 60
marks) and the three MFL speaking exams (7652/3T, 7662/3T, 7692/3T, 60 each)
were excluded under the rule *"a paper belongs here if a student can sit and
mark it alone."* That rule was wrong for these four: a Geography prediction was
being built from 80% of the qualification and an MFL prediction from 70%, and
nothing said so.

- **The OCR Practical Endorsements stay out, and that is the same rule applied
  correctly.** They are reported separately and contribute nothing to the grade,
  so a prediction has nothing to do with them. Don't "finish the job" by adding
  them.
- **The form asks for one mark, not a breakdown.** A catalogue paper may carry
  `"assessment": "coursework"` or `"oral"` (default `"exam"`). `applyAssessment()`
  in `telos.js` reads it off `/api/template-info`, hides `#q-breakdown`, and
  clears any rows already there so nothing hidden gets posted. A 3,000-word
  investigation has no question numbers to enter.
- **Speaking is stored from the teacher-conducted variant.** AQA publishes 3T
  and 3V separately and their boundaries are identical in every series checked,
  so one row serves both and a student need not know which their centre used.
- **`tests/test_coursework.py` guards the omission, not the fix.** It sums each
  qualification's components against the total the board actually grades out of.
  That is the only check that sees a missing component — the papers that *are*
  there look perfectly correct on their own. Physics counts one 35-mark option
  because a student sits exactly one.

**AS-levels are a separate qualification, not half an A-level** (2026-08-26,
migrations 034-036). 20 AS qualifications across AQA, OCR A and Edexcel, taking
the catalogue to 41 and the boundary table to 676 rows.

The engine had to change before any of it could be loaded, because it assumed
every grade ladder ends at A*:

- **`boundary_ladder` now accepts `a_star = NULL` and ends at A** (point 5).
  `attempt_grade_score` and `marks_for_score` read the ceiling from
  `ladder[-1]` instead of hardcoding 6, `infer_de` derives D/E from the gaps
  that exist, and `next_grade` caps at the qualification's own top. Without
  this an AS student scoring 95% was predicted **A***, a grade their
  certificate cannot carry.
- **`_median_set` returns `a_star = None` unless every row in the set has one.**
  A median over the rows that happen to have an A* would invent a top grade for
  a qualification that has none.
- **`get_grade`'s percentage fallback awarded A* at >=90% regardless.** With no
  boundary row at all, `a_star` is None whether the qualification has no A* or
  simply has no data, and those are not the same thing — hence the explicit
  `top` argument, passed from `top_grade(qualification_level(...))` at all
  three call sites.

**A catalogue key is a storage identity, not a label.** AQA Mathematics exists
at A-level and at AS, and `papers`, `grade_boundaries` and `user_subjects` are
all keyed by that string — so the AS entry's key is `"Maths (AS)"` and it
carries a `"name"` field with what a student reads. `display_name()` falls back
to the key, so every A-level entry needs neither. Don't "tidy" the suffix away.

**Three things about the data that could not have been guessed:**

- **AQA's A-level documents contain no AS tables at all.** They are separate
  PDFs. Assuming the files already downloaded covered AS would have produced
  nothing, silently.
- **An AS paper is not the A-level paper at a smaller total.** Edexcel AS Maths
  Paper 2 is 60 marks against the A-level's 100; AQA's AS MFL writing paper is
  50 against 80; AS Maths Paper 1 is Pure *and Mechanics* where the A-level
  Paper 1 is Pure alone. Each was read from the specification, and
  `test_coursework.py` checks all 21 AS totals against what the board grades.
- **Pearson zero-pads paper labels to three digits in 2019** (`Paper 021`) where
  every other series writes `Paper 21`. The label regex rejected them, so AS
  Further Maths silently lost a whole series. After widening it, the three
  A-level Edexcel migrations were regenerated and confirmed byte-identical
  before the change was trusted.

**AS rows carry six numbers, A-level rows carry seven**, so each board's AS
tables are parsed by their own reader rather than a widened one. A parser
reading both would, on a near-miss, store an A boundary in the A* column — the
exact shape of the fault that made Physics predict U on an 85%.

**Gaps, stated rather than papered over:** there is no AS Philosophy (AQA does
not award one). OCR and AQA published AS boundaries separately before 2022 and
those documents are not to hand, so AS carries 2022-2025 only — Edexcel also
has 2019. SQA Advanced Highers and Highers are **not loaded**: `LEVELS` lists
them and `top_grade()` already returns A for both, but no data exists yet and
SQA uses course-level cut-off scores rather than the per-component model, which
needs a design decision first.

**The subject picker nests subject -> level -> board.** One subject is offered
at several levels and a student takes one of them, so a flat list would put
"AQA A-Level" and "AQA AS-Level" side by side reading as near-duplicates.
`all_qualifications()` is sorted by (name, level, board) and the template opens
a new heading whenever either changes — keep that sort and that grouping
together.

**Known good, don't "fix":**

- **`users.parent_email` and `users.parent_report_optin` are dead columns.**
  Migration 001 created them for the weekly parent report, which was cut on
  2026-08-25. Zero rows have either set and nothing outside that migration
  touches them. Left in place on purpose — dropping a column is destructive and
  irreversible, and two unused nullable columns cost nothing. Don't "tidy" them
  away without deciding to.

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
