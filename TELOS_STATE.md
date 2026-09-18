# Telos — where we left off

**Last updated: 2026-09-18.** Living handoff document. Read this first, then
`TELOS_V2_SPEC.md` and `TELOS_V2_ADDENDUM.md` (the addendum reorders the
phases and adds the mobile/PWA work).

**`TELOS_ARCHIVE.md` holds the reasoning behind every settled decision.** This
file lists them; that one says why, and what it cost to find out. It was split
out on 2026-08-30 because the settled section had grown to 730 of this file's
1,063 lines, which made the document you are meant to read first the one nobody
finished. Archived means settled, not superseded — if the archive disagrees
with the code or with this file, trust those and fix the archive.

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
| Exam Mode | 8 tables (`exam_papers`, `exam_questions`, `exam_attempts`, `exam_responses`, `exam_purchases`, `exam_scale_anchors`, `exam_spec_refs`), migrations 041-043. Five Mock A papers published, 121 questions, £1 each |
| Admissions papers | 16 official ENGAA/NSAA PDFs on the volume at `STORAGE_DIR/admissions`, uploaded through `/admin/admissions/papers` — **never committed**. `scripts/admissions/answer_keys.json` (tracked) is what marks them. The 9 TMUA papers are not held yet |
| Payments | Stripe, **live mode** since 2026-08-28. Full lifecycle verified with a real card — charge, webhook, Pro granted, cancel, access removed. 7-day free trial, card up front. Re-checked 2026-09-16 with `scripts/check_stripe.py`: `READY`, both prices on `prod_V9MGf8ekk9ZPDp`, webhook enabled with all 7 events, portal configured |
| Git auth | Repo-scoped PAT in Windows Credential Manager, so `git push` just works |

### Environment variables (values live in Railway, never in git)

`DATABASE_URL`, `SECRET_KEY`, `STORAGE_DIR`, `CANONICAL_HOST`,
`RESEND_API_KEY`, `MAIL_FROM`, `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`,
`STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_MONTHLY`, `STRIPE_PRICE_ANNUAL`,
`STRIPE_PRICE_LEGACY`, `STRIPE_PRICE_ID` (old name for legacy),
`TUTORING_EMAIL`, `LEGAL_NAME`, `LEGAL_EMAIL`.

`LEGAL_NAME` is the one with no sensible default — the terms name whoever is
contracting with the student, and Telos is run by a sole trader, so it is a
person's legal name. It is set in Railway. Unset, `/terms` and `/privacy`
render a conspicuous placeholder and `test_legal.py` fails in production while
only warning locally. `LEGAL_EMAIL` falls back to `TUTORING_EMAIL`.

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
| 5 | £4.99/mo + £39.99/yr, webhook-only entitlements, billing portal, analytics | `da0b797` | **live** (yearly repriced 2026-08-26 — `TELOS_ARCHIVE.md`, "The landing page, pricing") |
| — | Password reset via emailed single-use link | `34faf81` | **live** |
| 2.5 | PWA — manifest, service worker, install prompt, offline shell (a-d; 2.5e web push deferred) | `891147a` | **live** |
| 4 | Prescriptions — "your next 3 questions", Today panel | `98c0589` | **live** |
| — | UI overhaul — Editorial treatment across all twelve screens, new stroke logo | `7df213d` | **live** |
| 9 | Shareable card export — the growth engine | `0df51d7` | **live** |
| — | Page loader — the mark charges during navigation | `0df51d7` | **live** |
| 6 | Spaced repetition — queue fills itself, SM-2 simplified, daily cap | `pending` | **live** |
| — | 7-day free trial — card up front, converts automatically | `e703cfd` | **live** |
| — | README, proprietary LICENSE, `/terms`, `/privacy` | `9e57de0` | **live** |
| — | Social preview card + landing `og:image` | `e60265b` | **live** |
| — | Revision mentoring added to the tutoring section | `b706354` | **live** |
| 11 | Admissions tests — TMUA, ESAT, ENGAA/NSAA catalogue, ungraded model | `eca34f9` `44bc94e` | **live** |
| 11 | Exam Mode — schema, loader, admin screens | `7450fc7` | **live** |
| 11 | Exam Mode — attempt lifecycle, server-authoritative timing | `90801ae` | **live** |
| 11 | Exam Mode — the test player | `2f1ecd2` `1ff7762` | **live** |
| 11 | Exam Mode — results screen | `4858bc2` | **live** |
| 11 | Exam Mode — QA pass, £1 per paper, advertised on the landing page | `9bfc838` `317e050` | **live** |
| 11 | Exam Mode pages styled — the Phase 11 templates used five classes that were in no stylesheet | `784ca7a` | **live** |
| 11 | Admissions past-paper tracker — 80 official papers, 52 auto-marked from the official keys | `784ca7a` | **live** |
| 11 | TMUA papers and keys — 70 of 80 tracked papers now mark themselves | `7f1e3e9` | **live** |
| 12 | TMUA Pass — £3.99 for 30 days | `7d883b1` | **removed** 2026-09-18, see below |
| 7, 10 | Percentile, boundary simulator | — | not started |
| 8 | Weekly parent report | — | **cut** (2026-08-25) |

---

## Open items

**Needs a human (I can't do these):**

1. ~~**Time an 8-question paper one-handed.**~~ **Done** — the owner confirmed the phone flow works (2026-09-08). The airplane-mode retry banner has still not been seen on a real device, which is the part of this that remains unverified.
2. **Re-test the cold open after the 800ms change.** Confirmed working at
   2500ms on 2026-08-27 — black screen, then the app at 2.5s. The timeout is
   now 800ms, so the same test should show the app in under a second.
3. **Monthly checkout at £4.99.** The yearly path is proven end to end with a
   real card (`TELOS_ARCHIVE.md`, "Payments, proven live") — charge, webhook,
   Pro granted, cancel, access
   removed. Monthly is the same code with a different price id, so this is a
   low-risk confirmation rather than an unknown. It needs a SECOND account: the
   founder account is grandfathered Pro and is offered "Manage billing", never
   a purchase button. If Pro never arrives, look at the webhook rather than the
   payment — entitlements are webhook-only by design, so a missing webhook is
   indistinguishable from a failed payment inside the app.
4. **Phase 2.5 device checks** — Lighthouse PWA audit on telosapp.co.uk;
   install to home screen on a real iPhone and a real iPad and confirm it
   opens without browser chrome, correct icon/splash; confirm an
   already-installed copy picks up a new deploy within one refresh
   (the "Update available" toast).
5. **Phase 4 on a real phone.** The Today panel was measured at 390px in an
   iframe (no horizontal overflow, 76px question rows, the due row exactly at
   the 44px floor) but never opened on actual hardware. Also worth confirming
   the picks feel right against your own logged papers rather than seeded ones.
6. **Decide whether spaced repetition goes back on the pricing page.**
   `/revise` is `@requires_pro`, per the spec, but the feature was removed from
   `PRICING_FEATURES["pro"]` on 2026-08-26 while it was still vapourware. It is
   real now, so it is currently a Pro feature that is not being sold. Adding it
   back is one line, with no `coming_soon` flag.
7. **2.5e, web push** — deliberately not built yet. Needs VAPID keys and a
   `push_subscriptions` table; the addendum says ship the rest of 2.5 first,
   which is what happened.
8. **The UI overhaul on real hardware.** Every screen was reviewed in the
   browser (and at 390px in a same-origin iframe, per the auditing gotcha
   below), but none of it has been opened on an actual phone or tablet. Worth
   a pass over the dashboard, the phone mark-entry flow and the three admin
   screens, since those were the last built and got the least eyes.

9. **Have a solicitor read `/terms` and `/privacy`.** They are careful and
   specific — written from the real schema, with the statutory 14-day right
   preserved and non-excludable liability left alone — but they were not
   written by a lawyer. Worth an hour of one's time now that live money is
   moving through a trial that converts by itself.
10. **There is no way to email all subscribers.** Section 7 of the terms
   promises 30 days' notice by email before a price change, and section 14
   promises the same for material changes to the terms. `mailer.py` sends one
   message at a time and nothing iterates the user table. That promise cannot
   currently be kept — build the path before the first repricing, not during.
11. **Buy one Exam Mode paper with a real card.** The £1 checkout mirrors
   the mock-paper flow that IS proven live, but that path has never taken a
   payment itself. It needs a SECOND account — the founder account is
   grandfathered Pro and is never offered a purchase. Confirm the charge reads
   £1, that the paper unlocks, and that a refund does not silently leave it
   unlocked.
12. **Write more Exam Mode papers.** Only Mock A exists — five papers. Sitting
   one is a good experience; a student who buys all five has run out, and the
   £1-a-paper model only works if there is a next paper to buy.
13. **Topics in the Mock A papers are too fine-grained.** Every question
   carries a unique topic, so the results screen's "By topic" section is twenty
   rows of 1/1 — the same information as the question list below it, in a
   different shape. Six to eight topics per paper would make that section say
   something. A content change, not a code one.
14. **Film the demo account.** `scripts/seed_demo_account.py` builds it. Re-run
   it on the morning of filming: the dates are relative to today, so "this
   week" stops meaning this week as it ages.
15. **Facebook's cache, only if it matters.** LinkedIn was re-scraped on
   2026-08-30 and shows the new card. The Facebook Sharing Debugger needs a
   Facebook login, so it was skipped — and it is probably a no-op, because
   Facebook only caches a URL that has actually been shared into a Meta
   property, and the `og:image` did not exist before that day.

**Needs the owner, for the admissions tracker (2026-09-16):**

16. ~~**Upload the 16 official question papers.**~~ **Done 2026-09-16** — all
   16 ENGAA and NSAA papers are on the volume and verified serving as real
   PDFs to a logged-in student, sizes matching the sources. The 9 TMUA rows
   still read "use your own copy"; see item 18. The original note follows,
   because the mechanism still matters for the TMUA papers when they arrive.

   **Upload the official question papers.** They are on this machine at
   `scripts/admissions/documents/` (gitignored, 17MB) and nowhere else —
   production has none of them, so every paper row currently reads "use your
   own copy" rather than offering a download. `scripts/upload_admissions_papers.py`
   pushes them through the admin route. It prompts for the admin email and
   password at the terminal — not echoed, never in the shell history — so run
   it from your own shell. It cannot be run for you and should not be: an
   agent session has no terminal to prompt at, and the one thing that must not
   happen to that password is ending up in a transcript. Check the result at
   `/admin/admissions/papers`.
17. **Decide whether hosting those PDFs is a risk worth taking.** They are
   Cambridge Assessment copyright, and serving them from telosapp.co.uk to
   paying subscribers is a different act from linking to the pages that publish
   them. The owner chose to host on 2026-09-16 having been told this. The
   tracker works either way — a paper with no PDF on the volume simply says so
   — so this can be reversed by deleting the files, without touching code.
18. **TMUA has no answer keys.** `extract_keys.py` was only ever run over the
   ENGAA and NSAA papers, so TMUA's 18 papers are self-marked: the student taps
   right or wrong. The official TMUA papers and keys are published, so this is
   a matter of downloading them and running the same extractor, not of writing
   anything new.

**Noesis lives in its own repository now.** A `noesis/` package — a TikTok
content CLI for @vini_noesis — was built in this working tree on 2026-09-10
and moved out on 2026-09-11 to **github.com/vineigenphase/Noesis** (private,
`C:\Users\User\Noesis`). Nothing of it remains here: no directory, no branch,
and `README.md`, `.gitignore` and `.env.example` are back to their committed
state. `test_readme` passes, and so does the full suite.

It reads `exam_questions` over a **read-only** connection and nothing else, so
it is a consumer of this database, not a part of this application. Two things
follow. Renaming or reshaping `exam_questions` breaks content generation over
there silently — there is no test in this repo that would notice. And the
reason it could not stay is worth remembering before anything else is added
here: `test_readme.py` asserts an exact tracked-file count and a line total, so
every file added moves a number, and `requirements.txt` is pinned at exactly
seven dependencies.

**Settled — don't re-litigate.** Each line below is a decision that has
already been argued out. The reasoning, and what it cost to find out, is in
**`TELOS_ARCHIVE.md`** — read it before reopening any of these.

*The last session — trial, licence, legal pages, presentation (2026-08-28..30)*

- The 7-day free trial shipped 2026-08-28.
- The repository was made presentable 2026-08-29.
- Two layout changes shipped alongside the trial.
- Revision mentoring was added to the tutoring section 2026-08-30.
- Repo metadata was set 2026-08-30.

*Phases 4, 9, the UI overhaul, and the Neon wake-up*

- Phase 4 shipped 2026-08-23.
- UI overhaul shipped 2026-08-24.
- Phase 9 shipped 2026-08-25.
- The spec's "streak" card has no data behind it.
- A free account cannot make the grade card.
- The page loader is deliberately shy, and deliberately inert until needed.
- The Neon wake-up 500 is fixed.

*Grade boundaries, and the subject catalogue*

- Grade boundaries were substantially wrong, and are now sourced from the
  boards' own PDFs.
- Don't hand-type boundary data.
- `tests/test_boundaries.py` guards the class of fault, not the instance.
- Pearson's 2019 file uses two layouts.
- Six Further Maths papers have boundaries but cannot be logged.
- The subject catalogue now covers 21 qualifications across five boards.
- Coursework and speaking components count toward the grade, and were missing.
- AS-levels are a separate qualification, not half an A-level.
- A catalogue key is a storage identity, not a label.
- Three things about the data that could not have been guessed.
- AS rows carry six numbers, A-level rows carry seven.
- Gaps, stated rather than papered over.
- The subject picker nests subject -> level -> board.
- SQA is the one board whose boundaries Telos derives rather than reads.
- An SQA course is graded A-D, so the ladder needed a bottom as well as a top.
- Only 2024 and 2025 are stored, for both SQA levels.
- Two things that would have shipped wrong without a second source.
- SQA component order is SQA's, not a student's.
- Higher English is the first subject with no sibling at any other level.
- Coverage target is 2019 + 2022-2025, and 2020/2021 will never exist.
- Three more document quirks, all found by refusing to guess.
- The component-marks reader handles four spreadsheet layouts.
- A migration's DELETE must never be wider than its INSERT.
- Indentation inside a dict literal is not load-bearing, and that is a trap.

*The landing page, pricing, and the subscription screen*

- The landing page and pricing were reworked.
- The eyebrow read "A-level past papers" while the catalogue carried four
  levels.
- `TUTORING_EMAIL` drives the tutoring section's "book a free call" mailto.
- Stripe now matches the pricing table.
- `/subscription` shows three cards, not two with a radio inside one.
- Every suite that creates a throwaway user uses `tests/_fixtures.py`.

*Perceived speed, and the query count*

- Perceived speed: what was actually wrong.
- The checkout check now has a 15-second grace, and a retry that makes the
  grace safe.
- The grace on its own would have been a downgrade.
- Then the query count came down too — 24 statements to render a dashboard,
  now capped at 22 by a test.
- The memo is per-request and the invalidation is the load-bearing part.

*Phase 0.6 mark entry, and Phase 6 spaced repetition*

- Phase 0.6's one-handed target was marginal, and the reason was measurable.
- The mark allocation now carries to the next question.
- "Saved" must be reachable from exactly one place.
- Phase 6 shipped 2026-08-27.

*Admissions tests and Exam Mode (2026-09-04..10)*

- TMUA, ESAT, ENGAA and NSAA are tracked but NOT graded.
- ENGAA and NSAA structures were read from the papers, and the secondary sources were wrong.
- The 16 official answer keys are extracted and verified, never hand-typed.
- The 1-9 scale is norm-referenced and has been re-anchored four times.
- Exam Mode is server-authoritative about time, and reads one clock.
- Nothing in a live attempt's page may carry an answer.
- Papers are bought individually at £1; Pro includes every paper.
- Admissions tracking lives on its own tab, and each picker carries the other's selection.
- The `telos` demo account is seeded by script, deterministically.

*The Exam Mode pages, and the admissions tracker (2026-09-16)*

- **Four Phase 11 templates were never styled, and nobody noticed for twelve
  days.** `exam_index.html`, `admissions.html` and the two admin screens used
  `.hint`, `.pill`, `.table`, `.empty` and `.mk-row-sub` — five class names that
  appear in no stylesheet in this repository. The pages rendered as bare HTML
  tables inside correctly styled cards, which is why they looked half-finished
  rather than broken. `.hint` and `.pill` were worth having and are now defined;
  the other three were renamed to the vocabulary that already existed
  (`.data-table`, `.empty-inline`). `.mk-row-sub` is defined in `landing.css`,
  which app pages do not load — the class existed, just not there.
- **The paper list is rows, not a table.** Seven columns at 390px was a sideways
  scroll through the one screen that has something to sell.
- **An admissions paper is an ordinary `papers` row.** One `question_marks` row
  per question at one mark each, 0 or 1, plus the letter chosen in the new
  `answer_given` column. Not a table of its own, because the heatmap, the
  prescription engine and the revision queue all read those two tables and a
  parallel store would have made admissions papers invisible to every one of
  them.
- **Marking is comparing two lists of letters.** Every one of these tests is
  multiple choice at one mark a question with no negative marking, so the
  generic mark-entry screen — "how many marks out of 6?" — was twenty needless
  taps on a question whose only answers are 0 and 1.
- **The keypad's letters come from the key, not from A-E.** ENGAA Part A runs to
  H. Offering five options on a paper with eight would put three correct answers
  out of reach, and it would look like the student being wrong.
- **Re-entering a paper replaces it.** A student fixing a mistyped answer means
  to correct the sitting, not to claim they sat it twice.

*The pass that lasted a day (2026-09-18)*

- **The £3.99 TMUA pass was built, shipped and removed, and the reason is worth
  keeping.** It sold thirty days of "everything TMUA" — the two Telos mocks and
  the eighteen official past papers. UAT-UK publishes those eighteen free, so
  most of what the pass gated was a toll on a document a student can download
  in one click, and the first question anyone would ask is the one that ends
  the sale. The owner asked for it removed the day after it went live.
- **What is sold now is only what Telos made:** the five Exam Mode papers at £1
  each, and the question bank at £1. The official papers, their keys, the
  marking and the topic analysis are free to any signed-in student.
- **The mechanism is gone, not disabled.** `PASSES`, `pass_state`, `grant_pass`,
  the two routes, the webhook branch and `test_access_passes.py` were removed.
  Migration 045 and the `access_passes` table are left in place, empty and
  unused — a table with no rows costs nothing and dropping it would be the one
  irreversible part of undoing a feature that took a day to decide against.
- **Worked solutions live on TikTok**, and the pointer to @vini_noesis now sits
  on the admissions paper list, the marked-paper screen and the Mock Papers
  page rather than in a footer.
- **Mock Papers lists the Exam Mode papers too**, so "the mock papers" means
  all of them. It links rather than checks out: buying and sitting stay in Exam
  Mode, so there is one purchase path per paper rather than two.

*Payments, proven live*

- The live payment lifecycle is proven with a real card.
- Refunding a charge does not cancel the subscription.
- Stripe is live.
- Known good, don't "fix" — the dead parent-report columns, and the rest.

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

# What boundary data is missing, per qualification, for 2019 and 2022-2025
railway run .venv\Scripts\python.exe scripts\boundaries\audit.py

# Does Stripe agree with the pricing page? Read-only; non-zero if not
railway run .venv\Scripts\python.exe scripts\check_stripe.py

# The whole codebase as one annotated file (gitignored output, ~1.6MB)
.venv\Scripts\python.exe scripts\build_source_dump.py

# The social preview card — GitHub's repo image and the landing og:image
.venv\Scripts\python.exe scripts\build_social_preview.py
```

**22 suites as of 2026-08-30.** `test_legal.py` and `test_readme.py` are the
two newest and neither tests behaviour: the first checks the legal documents
agree with the code about money, the second recounts every figure the README
states as fact.

**Run `scripts/check_stripe.py` after any change to a Stripe variable.** It
reads the expected amounts from the app's own `PRICING` table, so it asks
"does Stripe agree with the page" rather than comparing against a second
copy that can drift. Every fault it looks for produces no error until a
customer hits it: a price pointing at the wrong amount (the page advertised
£39.99 against a £29 Stripe price for a while and nothing noticed), monthly
and yearly swapped — both are valid IDs, so the app cannot tell — the two
prices on different products so the portal cannot switch plans, a missing
webhook event, and the customer portal left unactivated, which is fine in
test and 500s in live.

**`scripts/boundaries/` holds every loader that produced a boundary row**,
with its own README covering the method, each board's document URLs, and the
layout quirks that cost real time to find. The documents are gitignored
(~60MB); set `TELOS_BOUNDARY_DOCS` or drop them in
`scripts/boundaries/documents/`. `pypdf`, `cryptography` and `openpyxl` are
installed only while running a loader and are deliberately not in
`requirements.txt` — the app never parses a PDF. Read that README before
adding a board: the "don't hand-type boundary data" rule — indexed above,
reasoned out in `TELOS_ARCHIVE.md` — is the whole reason it exists.

Local dev runs against the **production** database. Fine while there's one
user; use a Neon branch once there are real students.

---

## Gotchas that cost real debugging time

- **The safe-area rules have to stay last in `telos.css`.** The standalone
  block and the width blocks both style `.page-header` from inside a media
  query, so specificity is identical and only source order separates them —
  and the width blocks set `padding` as a SHORTHAND, which resets padding-top
  and throws the inset away. Written above them, the fix worked in phone
  portrait and did nothing on an installed iPad or a phone in landscape. The
  `.sidebar` rule was inert at every width. Four checks in `test_mobile_first`
  guard this; each was verified to fail when its bug is put back.
- **The PWA serves CSS from the service-worker cache**, so a browser reload can
  keep showing old styles after a deploy. `CACHE_VERSION` is the git commit and
  `activate` drops old caches, so it corrects itself — but when verifying a CSS
  change by hand, fetch with `cache: 'no-store'` or you will audit the old file
  and conclude the deploy failed.
- **A JavaScript syntax error takes down the WHOLE file, and page-source tests
  cannot see it.** One unescaped quote killed the entire exam player: no Start
  button, no timer, no options. The markup was right, the routes returned the
  right data, and every test passed, because the tests read page source. Found
  by opening it in a browser. `test_mobile_first` now runs `node --check` over
  every file in `static/js`, and skips loudly rather than silently where node
  is absent.
- **Postgres's `?` jsonb operator is unreachable through `db.py`.** The shim
  rewrites every `?` into a placeholder, so `options ? answer` fails with a
  parameter-count error. Use `jsonb_exists(col, key)`, which is identical in
  effect.
- **Two clocks are one clock too many.** Exam Mode wrote `ends_at` with
  Postgres NOW() and computed the remaining time in Python — 1.84 seconds apart
  when measured, so every candidate was handed or denied that much exam time.
  Anything comparing against a stored deadline must read both ends from the
  same clock.
- **Text written into a file by a script can reach an API double-encoded.**
  The GitHub repo description went up as `â€”` instead of an em-dash: the
  generating script held the literal and was decoded as cp1252 on the way out.
  Caught only because the value was READ BACK rather than trusting the 200.
  Write non-ASCII as an escape (`—`) from ASCII-only source, and verify
  by reading, not by status code.
- **A relative `og:image` is silently ignored**, not reported. The failure is
  indistinguishable from having no image at all — the link previews blank and
  nothing anywhere says why. `test_landing.py` asserts the URL is absolute.
- **LinkedIn caches on inspection as well as on sharing**, and copies the image
  onto its own CDN. Re-run Post Inspector after changing `og-preview.png` or it
  will keep serving the old copy. X's Card Validator was retired; X re-fetches
  on first share.
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
- **`railway run tests\run_all.py` used to fail most suites** on any
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
  The same rule now covers the legal pages and the social card: `/terms` reads
  `PRICING` and `TRIAL_DAYS`, and `build_social_preview.py` counts the
  catalogue at render time.
- **The README states about twenty numbers as fact, and `test_readme.py`
  recounts every one.** Adding a route or a template will fail the build until
  the README is updated — that is deliberate. Two rules keep it honest: a claim
  whose pattern stops matching FAILS rather than silently checking nothing, and
  the check enforces the precision the README claims (plain figures exactly,
  `~`-prefixed ones to the rounding they imply). Both failure modes were
  confirmed by mutation. It also asserts every file in `tests/` is registered in
  `run_all.py` — an unregistered suite never runs and looks like coverage.
- **`LEGAL_UPDATED` changes by hand, in the same commit that changes the terms
  or privacy wording.** Never `today()`.
- **A newly settled decision goes in two places**: one line in the index above,
  and the reasoning in `TELOS_ARCHIVE.md`. Putting the paragraph here is how
  this file grew to a thousand lines the first time; putting only the paragraph
  in the archive is how a decision gets quietly re-litigated, because nobody
  scanning this file ever learns it was decided.
- Postgres `LIKE` is case-sensitive; use `ILIKE` for anything user-facing.
- Don't touch `db.py`, `migrate_to_postgres.py` or `scan_sqliteisms.py` without
  asking.
