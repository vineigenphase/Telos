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
| 5 | £4.99/mo + £39.99/yr, webhook-only entitlements, billing portal, analytics | `da0b797` | **live** (yearly repriced 2026-08-26 — see below) |
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
2. **Re-test the cold open after the 800ms change.** Confirmed working at
   2500ms on 2026-08-27 — black screen, then the app at 2.5s. The timeout is
   now 800ms, so the same test should show the app in under a second.
3. **Stripe checkout on the monthly plan.** The annual run is **done**
   (2026-08-27) and charged £39.99, so the repricing is confirmed end to end.
   Monthly at £4.99 is still untested. Note it needs a SECOND account: the
   founder account is grandfathered Pro, so `/subscription` offers it "Manage
   billing" and never a purchase button. If Pro never arrives, look at the
   webhook rather than the payment — entitlements are webhook-only by design,
   so a missing webhook is indistinguishable from a failed payment in the app.
4. **Cancel → period-end → access-lost** path via Stripe clock simulation.
5. **Live-mode Stripe swap** when ready for real money: recreate the product,
   all three prices and the webhook endpoint in live mode, then update the four
   env vars. Everything configured so far is test mode.
6. **Phase 2.5 device checks** — Lighthouse PWA audit on telosapp.co.uk;
   install to home screen on a real iPhone and a real iPad and confirm it
   opens without browser chrome, correct icon/splash; confirm an
   already-installed copy picks up a new deploy within one refresh
   (the "Update available" toast).
7. **Phase 4 on a real phone.** The Today panel was measured at 390px in an
   iframe (no horizontal overflow, 76px question rows, the due row exactly at
   the 44px floor) but never opened on actual hardware. Also worth confirming
   the picks feel right against your own logged papers rather than seeded ones.
8. **The Today panel's "Revision due" section is wired but unexercised.** It
   only rendered during review because three synthetic `revision_queue` rows
   were inserted by hand. Nothing writes to that table until Phase 6, so in
   production the count is 0 and the section is hidden. Ready, not working.
9. **2.5e, web push** — deliberately not built yet. Needs VAPID keys and a
   `push_subscriptions` table; the addendum says ship the rest of 2.5 first,
   which is what happened.
10. **The UI overhaul on real hardware.** Every screen was reviewed in the
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

**SQA is the one board whose boundaries Telos derives rather than reads**
(2026-08-26, migrations 037-039). Nine Advanced Highers and nine Highers, taking
the catalogue to 59 qualifications and the boundary table to 792 rows.

- **SQA publishes grade boundaries for the WHOLE COURSE only** — one maximum
  mark and A/B/C/D cut-offs — and never per component, in any subject, in any
  year. So a component's boundary is its share of the course cut-off:
  `round(course_boundary * component_max / course_max)`.
- **Migration 037 adds `derived_from_course`**, TRUE on every SQA row and false
  everywhere else, because an estimate that looks like published data is a trap
  for whoever reads the table next. `test_boundaries.py` asserts it both ways.
  Don't load anything else with that flag without meaning it.
- **The component structures are NOT derived.** SQA publishes component names
  and max marks in a *separate* release ("Assessment and Component Marks"), and
  the loaders refuse unless each course's components sum to the course maximum
  — cross-checked against the grade-boundary release, since the two are
  different publications that could drift apart.
- **The approximation's limit, stated:** it assumes a component is as hard as
  the course as a whole. Projects and multiple-choice papers generally score
  higher than that, so the estimate reads slightly harsh on those and slightly
  generous on the long written paper. Fine for a prediction, not a published
  boundary — which is what the flag is for.

**An SQA course is graded A-D, so the ladder needed a bottom as well as a top.**
`boundary_ladder` used to require D and E together, which would have thrown away
a published D to infer a pair *and* invented an E grade that does not exist. The
bottom is now data-driven exactly as the top is:

| a_star | d / e | ladder |
|---|---|---|
| present | both | E..A* — an A-level |
| absent | both | E..A — an AS-level |
| absent | D, no E | D..A — an SQA course; below D is No Award |
| either | neither | D and E inferred — hand-entered and median rows |

A-level ladders are unchanged and tested for it: still six grades, still from E.

**Only 2024 and 2025 are stored, for both SQA levels.** In 2022 and 2023 these
courses ran in a modified form with the coursework removed — Advanced Higher
Biology was 120 marks rather than 160, Higher Geography 70 rather than 110.
That is a different set of components, not the same course with different
numbers, so those years are left out rather than bent to fit.

**Two things that would have shipped wrong without a second source:**

- **The Advanced Higher Chemistry and Biology course specifications give totals
  of 134 and 122, not the 160 SQA's own boundary tables show** — those PDFs
  describe a future revision. The component-marks release gave the structure
  actually in force. Never take a course spec as evidence of what a past series
  contained.
- **SQA is inconsistent about its own component names between years.** Higher
  German's coursework is "Assignment: Writing" in 2024 and "Assignment -
  Writing" in 2025. Names are normalised before comparison so a punctuation
  change does not read as a course restructure.

**SQA component order is SQA's, not a student's** — it lists Paper 2 before
Paper 1 for the sciences. The loader reorders to written papers, then oral, then
coursework. Don't sort these alphabetically; "Assignment" would lead.

**Higher English is the first subject with no sibling at any other level.**
Every other subject in the catalogue exists at A-level and is joined there by an
AS or an SQA course; English exists only as `SQA / English (H)`. The picker
copes — it groups by subject name and English simply has one level under it —
but a reader expecting the A-level to be the anchor of every subject should know
this one isn't. Advanced Higher English is *not* loaded; adding it is one entry
in `gen_sqa_ah.py` and a rerun.

**Coverage target is 2019 + 2022-2025, and 2020/2021 will never exist**
(2026-08-26). Both series were cancelled across every board — grades came from
centre and teacher assessment and no boundaries were published — so "every year
since 2019" is five series, not seven. `test_boundaries.py` fails if a
2020 or 2021 row ever reappears.

Coverage now stands at **1001 rows, 49 of 61 qualifications complete**. Every
A-level and every AS-level is complete. What is left is SQA only, and each gap
has a reason:

- **SQA 2019 borrows the 2022 component structure** (owner's call, 2026-08-26).
  SQA's component-marks publication begins in 2022, so 2019 has published
  course boundaries and no published structure. The 2022 shape stands in — but
  only where it can be shown to fit, and the check is the course maximum: if
  the 2022 components sum to the course maximum SQA published for 2019, the
  course had the same shape that year.

  That passed for 13 of 20 SQA qualifications and refused 7, because 2022 was
  itself a modified year for several courses. Higher Biology was a 150-mark
  course in 2019 and 120 in 2022; Advanced Higher Physics 130 against 155.
  Those get no 2019 rows rather than components that do not add up to the
  course they claim to describe. Individual components are refused the same
  way — Higher MFL "Directed Writing" was 30 marks in 2019 and is 15 now — so
  a subject can carry 2019 for its unchanged papers and not for the rest.

  `BORROWED = {"2019": "2022"}` in both SQA generators is the whole mechanism.
  Do not extend it to another year without the same sum check: it is the only
  thing separating a defensible substitution from an invented one.
- **SQA 2022 and 2023 are partial on purpose.** Those courses ran in a modified
  form: coursework withdrawn and several question papers resized. A component
  earns a row for a year only when it was the same paper that year — same code,
  same max mark. Advanced Higher Physics' question paper was 155 marks in 2022
  and 2023 against 120 now, so it gets no row for those years rather than a
  boundary computed for a paper of a different length. The generators print
  every skip with both max marks, so the gaps are visible on each run.
- Each year is pro-rated against **its own** course total. In 2023 Higher
  Biology Paper 2 was 95 marks of a 120-mark course, not 95 of 150 — using the
  current total would have made a modified year unusable rather than partial.

**Three more document quirks, all found by refusing to guess:**

- **AQA's AS documents for 2018/2019 need `cryptography` installed** alongside
  `pypdf` — they are encrypted where the later ones are not, and pypdf fails
  with an opaque traceback rather than saying so.
- **OCR published AS boundaries as their own document in 2019** ("Reformed AS
  Levels"), with no AS section heading because the whole file is AS. The
  extractor recognises an AS-only file by content — AS headings and no A-level
  ones — rather than by title, so a combined document whose heading wording
  changes again cannot have its A-level half read as AS.
- **SQA renames its own components between years, again.** Beyond the
  "Assignment: Writing" / "Assignment - Writing" case, 2023 writes "Reading for
  Understanding  Analysis and Evaluation" with a double space where every other
  year uses a comma. The normaliser now collapses commas too. Expect more of
  this; normalise before comparing, never match SQA's names literally.

**The component-marks reader handles four spreadsheet layouts.** 2022 leads
with a Qualification Number column and heads on row 1; 2023 has no such column
and heads on row 2; 2024 and 2025 head on row 3 and add an "Assessment Maximum
Mark". The header row is found by looking for the Subject cell. Where a file
carries no assessment total the components are summed and checked against the
grade boundary release instead — a stronger check than reading a total from the
same file it is meant to validate.

**A migration's DELETE must never be wider than its INSERT** (found
2026-08-26). Migration 038 opened with `DELETE FROM grade_boundaries WHERE
board = 'SQA'` and then inserted only the Advanced Highers. That was correct
when it was written, because SQA meant only Advanced Highers — and it silently
became destructive the moment migration 039 added the Highers. Re-running 038
took the boundary table from 947 rows to 849 and deleted every Higher row.

A fresh install in numeric order never sees it: 039 runs after 038 and puts them
back. It only bites on a re-run, which is exactly why it would have sat there.
Both are scoped by subject suffix now — `LIKE '% (AH)'` and `LIKE '% (H)'` —
and the fix was verified by running 038 alone against a populated table and
confirming all 114 Higher rows survived.

**Indentation inside a dict literal is not load-bearing, and that is a trap.**
`"Biology (H)"` sat at twelve spaces rather than eight in `paper_templates.py`
for two commits. Python accepted it, the catalogue loaded correctly, every suite
passed — and it was invisible to any edit that located entries by their indent,
which silently dropped it. Anything editing that file structurally should match
on `^\s+"[^"]+": \{` and never assume the indent. Two related traps in the same
family: that pattern also matches the board line `    "SQA": {` itself, so a
search for the first entry must start past the block's opening brace, and
truncating a block at its first entry removes the indent belonging to its own
closing brace.

**The landing page and pricing were reworked** (2026-08-26, owner's brief).

- **Three plans, not two:** Free £0, Pro Monthly £4.99, Pro Yearly £39.99.
  Clicking *Choose monthly* reveals an "Are you sure?" panel with the yearly
  figure rather than navigating — an argument the student can walk past, with
  two real exits. It is not a modal and it traps nobody.
- **The advertised figures are derived, not typed.** £39.99 / 12 = £3.33 and
  £4.99 x 12 - £39.99 = £19.89 -> "save £20". `tests/test_pricing.py` asserts
  the label matches `amount_pence`, that the per-month figure and the saving in
  `sub` are the real ones, and that yearly actually beats twelve months of
  monthly. Change a price and the suite tells you which words now lie.
- **`STRIPE_PRICE_ANNUAL` MUST BE REPOINTED.** The table says £39.99; Stripe
  still holds the £29 price until a new one is created in the dashboard and the
  env var updated. Until then the page advertises one figure and charges
  another. Existing £29 subscribers stay on their price, exactly as the legacy
  £2 subscribers do — never migrate or cancel them.
- **`/stats` is now `@requires_pro`.** It was `@login_required` only while being
  sold as a Pro feature. That is the same class of untruth as the `coming_soon`
  flags that outlived their features. One line to revert — but then "Full stats
  & topic analytics" has to come out of the Pro list at the same time.
- **The spaced repetition queue was removed from the offer**, not left flagged.
  A "soon" that never arrives is worse than an absence. Nothing in the Pro list
  carries `coming_soon` any more, and the suite fails if anything does.

**The eyebrow read "A-level past papers" while the catalogue carried four
levels.** It told a Scottish or AS student, in the line above the headline, that
this was not for them. It now names all four. Anything that describes coverage
in prose — the eyebrow, the meta description, the mockups — has to move when the
catalogue does; none of it is generated.

**`TUTORING_EMAIL`** drives the tutoring section's "book a free call" mailto.
It defaults to `tutor.telos@gmail.com`, so the page works from a clean checkout
with nothing configured; the environment variable is there to repoint it
without a deploy. The founder's personal address is deliberately not the
fallback — a landing page publishes whatever it is given.

**Stripe now matches the pricing table** (2026-08-26, test mode).

    price_1U8pgMQh06XJIdap5l5YBVRy   £39.99 / year   <- STRIPE_PRICE_ANNUAL
    price_1U5w6XQh06XJIdapt3F1kkuR   £29.00 / year      left active
    price_1U5w6WQh06XJIdapQUfJRkQ2   £4.99  / month  <- STRIPE_PRICE_MONTHLY
    price_1U3drKQh06XJIdapskilvmkh   £2.00  / month  <- STRIPE_PRICE_LEGACY

- The £39.99 price sits on the **same product** as the old annual one
  (`prod_V3lOOOHqOsq4IH`), so the billing portal, the webhook and plan changes
  treat them as one product with several prices rather than unrelated things.
  Create any future price the same way.
- **The £29 price is still active and nobody was moved off it**, which is the
  same rule the legacy £2 price has always had. Never migrate or cancel either.
- Reversal, should it be wanted: archive `price_1U8pgM…` and set
  `STRIPE_PRICE_ANNUAL` back to `price_1U5w6X…`.
- **All of this is test mode.** `sk_test_…`. The live-mode swap remains a
  separate job: recreate the product, all three prices and the webhook endpoint
  in live mode, then update the four environment variables.

**`/subscription` shows three cards, not two with a radio inside one.** Free,
Pro Monthly and Pro Yearly. The two paid cards carry an **identical** feature
list on purpose — the product is identical, and trimming the monthly list to
flatter yearly would misrepresent what £4.99 buys. The interval is the card, so
each posts a fixed `interval` to `create_checkout` and there is no radio left to
mis-read. Annual still leads for the reason worth keeping written down: A-level
revision collapses in June, so monthly billing takes about seven payments and
then churns permanently.

**Every suite that creates a throwaway user uses `tests/_fixtures.py`.** All
eight, not the two that were converted when the helper was written. Leaving the
rest on raw INSERTs was a mistake that cost a full suite run the first time a
session was paused mid-flight: the killed suite's `finally` never ran, its user
was left behind, and the next run died on a unique constraint in a suite that
had nothing to do with what was being changed. `fresh_user()` clears any
leftover under that email before inserting. Add a suite, use the helper.

**Perceived speed: what was actually wrong** (2026-08-27, measured).

- **The cold-open black screen was 2500ms because that was the timeout, not
  because anything was slow.** Warm production TTFB is 70-235ms, so the worker
  was waiting roughly ten times longer than a healthy network ever needs, and
  the only thing that patience bought was a longer black screen on the one
  occasion the fallback matters. **Now 800ms.** `tests/test_pwa.py` pins it
  between 500 and 1200: below 500 a healthy request starts losing the race to
  its own timeout, above 1200 a person has already decided the app is broken.
- **Nothing was prefetched.** Server-rendered means the browser cannot start
  until the click completes. The page now fetches on `pointerdown` — a finger
  is down about 100ms before it lifts and the server answers in about 200ms —
  and the worker stores the response under its URL so the navigation finds it.
  This is not stale caching: the copy is a few hundred milliseconds old and was
  fetched because the user was already reaching for it.
- **`/logout` answers GET as well as POST**, so prefetching it would sign a user
  out for touching a link near it. `NO_PREFETCH` mirrors the worker's
  never-cache prefixes and the suite asserts every entry. Anything added to one
  list belongs in the other.

**The checkout check now has a 15-second grace, and a retry that makes the
grace safe** (2026-08-27, owner's call). Testing every checkout cost a round
trip, and one dashboard render borrows a connection thirteen times within a few
milliseconds — about 158ms of pure overhead per page.

    page        check always   15s grace    saved
    /               744 ms       600 ms     145 ms
    /papers         318 ms       258 ms      60 ms
    /heatmap        235 ms       187 ms      48 ms

    empty checkout   12.2 ms  ->  0.5 ms

**The grace on its own would have been a downgrade.** `test_db_resilience.py`
kills a backend and re-checks out within milliseconds, so the kill lands inside
the grace, the pre-emptive check is skipped, and the corpse is handed out. The
suite would have failed — correctly.

So `Connection.execute` replaces the connection and retries **once**, and only
before any statement has succeeded: after that there is a transaction in
progress, and replaying one statement of it against a fresh connection is worse
than the error. `_used` is the flag that enforces it.

The trade is therefore not "less safe, more fast". It is: stop paying a round
trip on every checkout to PREDICT a dead connection, and instead pay nothing
until one actually turns up, then recover. Strictly better than before.

Fourteen checks pin it — an unstamped connection is checked, one returned
moments ago is not, one idle past the grace is, a dead connection is retried,
and a dead connection mid-transaction is not. Do not add the grace anywhere
else without the matching retry.

**Then the query count came down too** (2026-08-27). 24 statements to render a
dashboard became 20, and four things were wrong:

- **`SELECT * FROM grade_boundaries` with no WHERE, in four places** — the whole
  thousand-row table pulled to grade eight recent papers, and it grows with
  every board added. `boundary_rows_for()` scopes it to the student's
  `(board, subject)` pairs. **Scoped no further, deliberately:**
  `select_boundaries` falls back WITHIN a subject — same paper other years,
  then same subject same year — so narrowing to the exact papers logged would
  change which fallback it finds and therefore change the grade.
- `SELECT COUNT(*) FROM papers` ran **three times** with identical arguments.
- `SELECT * FROM user_subjects` ran **twice**.
- The accuracy aggregate scanned the same join **three times** for three date
  windows. One pass with `FILTER` now.

**The memo is per-request and the invalidation is the load-bearing part.**
`_memo` hangs off `g`, so nothing survives a request or leaks between users.
`set_user_subjects` drops its own key, and the paper count is dropped inside
`recompute_predictions` — already the one hook every paper and mark change
funnels through. Memoise nothing here whose answer a write in the same request
can change without going through those.

    page        before      after
    /            744 ms     474 ms
    /papers      318 ms     197 ms
    /heatmap     235 ms    ~170 ms

`tests/test_trend_deltas.py` holds the ceiling: at most 22 statements, no
statement repeated verbatim, and no unscoped pull of `grade_boundaries`. It
asserts the page returned **200** first — a guard that tolerates any status
would happily count the queries of a redirect and report a comfortable number
that meant nothing. That is not hypothetical: the check failed on its first run
because the fixture had no `user_subjects` row and the setup gate 302'd it.

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

# What boundary data is missing, per qualification, for 2019 and 2022-2025
railway run .venv\Scripts\python.exe scripts\boundaries\audit.py
```

**`scripts/boundaries/` holds every loader that produced a boundary row**,
with its own README covering the method, each board's document URLs, and the
layout quirks that cost real time to find. The documents are gitignored
(~60MB); set `TELOS_BOUNDARY_DOCS` or drop them in
`scripts/boundaries/documents/`. `pypdf`, `cryptography` and `openpyxl` are
installed only while running a loader and are deliberately not in
`requirements.txt` — the app never parses a PDF. Read that README before
adding a board: the "don't hand-type boundary data" rule above is the whole
reason it exists.

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
