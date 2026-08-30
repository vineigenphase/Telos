# Telos

**A past-paper tracker that tells A-level and SQA students the grade they are
actually on, and the three questions that would move it.**

Live at **[telosapp.co.uk](https://telosapp.co.uk)** · Flask · Postgres ·
Railway · Stripe · installable PWA

---

## The problem

A student finishes a past paper, writes "62%" at the top, and files it. That
number is close to meaningless. 62% on a brutal 2019 Physics paper and 62% on a
soft 2023 one are not the same performance, and neither tells them what to do
on Tuesday evening.

Telos records every question separately, converts each attempt to a position on
a continuous grade scale using **that paper's real published boundaries**, and
turns the residue into a ranked list of what is costing marks.

Three questions, in order:

| | |
|---|---|
| **Diagnosis** | Which topics are bleeding marks, ranked by what they actually cost |
| **Prediction** | What grade am I on, with a confidence level and the marks to the next boundary |
| **Prescription** | What are the three specific questions to do next |

---

## Scale

| | |
|---|---|
| Qualifications | **61**, across AQA, Edexcel, OCR A and SQA |
| Grade boundary rows | **1,001** real published boundaries |
| Levels | A-Level, AS-Level, Higher, Advanced Higher |
| Components | 199 papers and coursework units |
| Routes | 51 |
| Tables | 20, under 40 numbered migrations |
| Tests | 22 suites, ~610 assertions |
| Code | ~28,000 lines across 179 tracked files |

Coverage is not approximate. `test_boundaries.py` fails the build if **any**
paper the app offers lacks boundaries — a qualification a student can select
but cannot be graded on is a bug, not a gap.

The reverse direction is reported but deliberately not failed on: Edexcel
publishes boundaries for Further Maths option papers the catalogue does not yet
offer. That is real data waiting on a missing feature, so the suite prints it
every run rather than hiding it or treating it as an error.

---

## Architecture

```
app.py            Flask routes, session, entitlement gates      (~3,000 lines)
db.py             psycopg3 shim — Postgres behind a sqlite3 API
prediction.py     grade engine        — pure, no Flask, no DB
prescription.py   "your next 3 questions" — pure
revision.py       spaced repetition   — pure
sharecards.py     server-rendered PNG share cards
brand.py          the Telos mark, drawn in code
paper_templates.py  61 qualifications, 199 components
migrations/       40 numbered idempotent SQL migrations
tests/            22 standalone suites
scripts/boundaries/  36 board-document scripts
```

### The engines are pure functions

`prediction.py`, `prescription.py` and `revision.py` import no Flask and touch
no database. They take plain data and return plain data.

This is the single decision the codebase most depends on. The grade engine has
genuinely intricate rules — recency weighting, difficulty normalisation,
confidence intervals, qualifications whose ladder stops at A instead of A\* —
and all of it is testable without a request context, a fixture user, or a
network round trip. `test_prediction.py` and `test_engine_sweep.py` between
them exercise every qualification in the catalogue in about a second.

### Grade scale, not percentages

```
A*=6  A=5  B=4  C=3  D=2  E=1  U=0     with fractional positions between
```

A grade score of 4.6 means "comfortably into B, most of the way to an A". Each
attempt is placed on this scale using the boundaries for that specific paper
and series, so paper difficulty normalises out automatically.

Three details that took real care:

- **Not every ladder reaches the top.** An AS-level is graded A–E with no A\*;
  SQA runs A–D with no E. The ladder's ends are read *from the data* — `a_star`
  absent means it tops out at A, `d` present with `e` absent means it bottoms
  out at D — so an AS student is never predicted a grade that cannot appear on
  their certificate.
- **Missing boundaries are never guessed around.** `MissingBoundaries` is
  raised and handled. Summer 2020 and 2021 were cancelled in England, so no
  boundaries exist; an attempt at those years falls back to the median of the
  real years, which is the honest answer.
- **SQA does not publish component boundaries** — they are computed from the
  course award, and every such row is flagged `derived_from_course` so the
  interface can say so rather than implying a precision that is not there.

### Entitlements move only when Stripe says so

`auth.py` is the single source of truth for paid access, and nothing grants Pro
on a redirect back from checkout. A `customer.subscription.*` webhook is the
only thing that writes an entitlement. A user who closes the tab at the wrong
moment, or who edits the success URL by hand, gets exactly what they paid for.

The gate is deliberately generous in the other direction: `past_due` keeps
access, because Stripe retries a failed card for about two weeks and a student
mid-revision should not be locked out over an expired card. Only `canceled` and
`unpaid` cut access.

This was verified end to end in live mode with a real card — charge, webhook,
Pro granted, cancel, access removed.

### `db.py` — Postgres behind a sqlite3 API

Telos began on SQLite. Rather than rewrite every call site during the Postgres
migration, `db.py` presents the sqlite3 interface the app already spoke — `?`
placeholders, `.lastrowid`, row objects that index by name — over psycopg3.

It also carries the operational scar tissue that hosting on Neon requires: a
serverless Postgres instance sleeps, so a pooled connection can be dead by the
time it is handed out. Connections idle longer than a 15-second grace are
health-checked before use, and a query that fails on a dead connection is
retried exactly once — but only if it had not already done work, so a retry can
never replay a partial write.

---

## Features

**Free — diagnosis**
- Unlimited paper logging, per-question mark entry
- Per-topic heatmap
- 61 qualifications with real boundary data
- File uploads

**Pro — prediction and prescription**
- Predicted grade per subject, with confidence and marks to the next boundary
- "Your next 3 questions", chosen from the student's own marks
- Full statistics and topic analytics
- Spaced repetition queue (SM-2, simplified; daily cap)
- Pro Zone — resources, monthly notes
- Original mock papers

**Everyone**
- Installable PWA — offline shell, service worker, install prompt
- Share cards rendered server-side as PNG
- Password reset over single-use emailed links

---

## Engineering notes

A few decisions worth explaining, and a few scars worth keeping.

### Migrations are numbered, idempotent, and do not run on deploy

40 SQL files, tracked by filename in `schema_migrations`. The `Procfile` is a
bare gunicorn line — migrations are run deliberately, by hand, because a
migration that runs automatically on every boot is a migration that will
eventually run during an incident.

They are idempotent because they get re-run. One of them once had a `DELETE`
scoped more widely than its `INSERT` and removed 98 rows it had not written on
its second run. The fix — scoping the delete to exactly what the insert
creates — is now the rule the rest follow.

### Boundary data is loaded by script, never by hand

36 scripts under `scripts/boundaries/` — extractors, generators and
verifiers. Every extractor
validates each component against **its own maximum mark** before emitting SQL.
That guard exists because a mis-parsed PDF column silently produces boundaries
that are plausible, wrong, and would quietly mis-grade every student who sat
that paper.

PDF and spreadsheet parsing dependencies are installed for the extraction and
uninstalled afterwards. They are not in `requirements.txt` — the running
application has no reason to be able to read a PDF.

### Tests are standalone scripts

No pytest. Each suite is a Python file that runs top to bottom, prints
`PASS`/`FAIL` per assertion, and exits non-zero on failure; `tests/run_all.py`
runs all 22. The integration suites create and destroy their own fixture users
through `tests/_fixtures.py`, which exists because killed runs used to leave
orphans behind that broke the next run.

The suite is also where non-obvious invariants live:

- A dashboard render costs **at most 22 statements**, with no statement
  repeated verbatim and no unscoped pull of the boundary table. This is a
  ceiling, not a target. The page once cost 24 statements, several of them the
  same query with the same arguments, and pulled all 1,001 boundary rows to
  grade eight papers.
- Deltas must be `None` when there is nothing to compare against, never `0` —
  a new account has no trend, and "+0 this week" is a lie told to every user on
  their first day.

### Things that cost real debugging time

`TELOS_STATE.md` keeps the full list. Three that generalise:

- **`.btn { display: inline-flex }` beats the browser's `[hidden]` rule.**
  Buttons meant to be hidden were visible in production. Specificity beat
  intent, silently.
- **Equal-specificity CSS is decided by source order, 1,500 lines apart.** A
  safe-area fix for the installed PWA header was written above the width
  breakpoints that overrode it, so it worked in phone portrait and did nothing
  on a tablet or in landscape. It was caught by forcing the media query to
  match in a live page and measuring: 24px before, 24px after. The rule was
  inert while reading perfectly correctly. Four tests now guard it, each
  verified to fail when its bug is reintroduced.
- **Refunding a Stripe charge does not cancel the subscription.** They are
  separate objects. The refunded subscription stayed active and would have
  rebilled a year later.

---

## Running it

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

railway run .venv\Scripts\python.exe app.py                     # dev server :5000
railway run .venv\Scripts\python.exe tests\run_all.py           # all 22 suites
railway run .venv\Scripts\python.exe migrations\run_migrations.py
```

`railway run` injects the environment; see `.env.example` for the variable
list. Secrets live in Railway and never in the repository.

> `railway run` also injects the production `CANONICAL_HOST`, which 301s the
> test client. `run_all.py` strips it per suite — which is why suites are run
> through the runner rather than individually.

---

## Stack

| | |
|---|---|
| Application | Flask 3.1, Flask-Login, gunicorn |
| Database | Neon Postgres (eu-west-2), psycopg3 with pooling |
| Hosting | Railway, EU West, auto-deploy from `main` |
| Payments | Stripe — Checkout, Billing Portal, webhooks (live) |
| Email | Resend, DKIM/SPF verified |
| Images | Pillow — share cards and PWA icons rendered in code |
| Front end | Server-rendered Jinja, hand-written CSS, no framework |

Seven runtime dependencies. There is no JavaScript build step, no bundler and
no CSS framework — ~3,500 lines of hand-written CSS and 530 of vanilla JS.

---

## Licence

**Proprietary — all rights reserved.** See [LICENSE](LICENSE).

Telos is a commercial service. The source is published so it can be read and
evaluated, not so it can be reused: no permission is granted to deploy it, copy
it, or run a service derived from it. Quoting excerpts for review or teaching is
fine, with attribution.

The grade boundary data is published by AQA, Pearson Edexcel, OCR and SQA. It is
factual reference data, it is not mine, and those organisations' own terms
govern it.

`/terms` and `/privacy` are the service's own documents, and both are public —
somebody deciding whether to sign up, or a parent checking what their child's
revision app collects, should not need an account to read them.

---

## Repository map

```
app.py  db.py  auth.py  mailer.py  brand.py       core application
prediction.py  prescription.py  revision.py       pure engines
sharecards.py  paper_templates.py                 rendering, catalogue
migrations/          40 numbered SQL migrations
scripts/boundaries/  36 board-document scripts
scripts/check_stripe.py        read-only Stripe config verification
scripts/build_source_dump.py   whole codebase as one annotated file
tests/               22 suites, ~610 assertions
templates/           33 Jinja templates, including /terms and /privacy
LICENSE              proprietary — all rights reserved
static/              CSS, JS, fonts, PWA manifest, service worker
TELOS_STATE.md       living handoff — infrastructure, phases, gotchas
TELOS_ARCHIVE.md     the reasoning behind every settled decision
```
