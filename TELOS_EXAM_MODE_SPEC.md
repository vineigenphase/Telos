# Telos Exam Mode — Engine Specification v1

Pro-only tab. Simulates the Pearson VUE computer-based TMUA/ESAT experience with original Telos papers. This document is the contract between the content (papers as JSON, written by Claude in chat) and the integration (Flask/Postgres, done by Claude Code in the Telos repo).

## 0. Spec compliance (verified against UAT-UK 2026/27 documents, 5 Sep 2026)

| Paper | Questions | Time | Content source | Notes |
|---|---|---|---|---|
| TMUA Paper 1 | 20 MCQ | 75 min | TMUA Section 1 (Part 1 MM1–MM8 + Part 2 M1–M7) | No logic/proof |
| TMUA Paper 2 | 20 MCQ | 75 min | Section 1 + Section 2 (Arg1–4, Prf1–5, Err1–2) | Only paper with logic/proof |
| ESAT Maths 1 | 27 MCQ | 40 min | ESAT M1–M7 (identical to TMUA Part 2) | GCSE-level content, hard problems |
| ESAT Maths 2 | 27 MCQ | 40 min | ESAT MM1–MM8 (identical to TMUA Part 1) + M | No logic/proof, no cosine-rule exclusion |
| ESAT Physics | 27 MCQ | 40 min | ESAT P1–P7 + M | g = 10 N/kg; SI prefixes nano→giga |

Hard rules from the specs that the question writer must obey:
- No calculator; no formula booklet. Numbers must be hand-computable.
- ESAT Maths 1 / TMUA Part 2: candidates are **not** expected to recall sine or cosine rules (M5.18). Sine/cosine rule belongs to MM4.1 (Maths 2 / TMUA Part 1).
- MM5.2: change of base formula will not be set. Write log questions so they never need it.
- MM6.3: inflexion points not examined. Differentiation from first principles excluded.
- MM7.2: no integration of x⁻¹ (n ≠ −1).
- Arg1: no symbolic logic notation, no truth tables. Prose only ("if A then B", "A only if B").
- Physics: spec explicitly lists the equations. Do not require anything not listed (e.g. no s = ut + ½at², only v² − u² = 2as and graph methods; no F = BQv; no E = hf).
- 1 mark per question, no negative marking. Options: 5–8 (A–H). Real papers vary; default 6.

## 1. Scoring model

UAT-UK does not publish raw→scale conversions. Live scores are Rasch-equated per sitting with median fixed at 4.5, ~10% above 7.0, cap 9.0. Telos therefore reports an **estimated** scaled score, labelled as such, using piecewise-linear interpolation between anchor points stored in the DB so they can be recalibrated.

```
scale_anchors (per exam family, marks on the family's full-test basis):
  TMUA  (40 marks, both papers): [[0,1.0],[8,2.0],[14,3.3],[20,4.5],[26,6.0],[30,7.0],[34,8.0],[38,8.8],[40,9.0]]
  ESAT  (27 marks, per module):  [[0,1.0],[5,2.0],[9,3.3],[13,4.5],[17,6.0],[20,7.0],[23,8.0],[26,8.8],[27,9.0]]
```

Single TMUA paper: equivalent = raw × 40 / 20, then interpolate. Full TMUA sitting (P1 + P2 in one session): raw out of 40 directly. ESAT modules are scored separately, as in the real test.

Derived metrics on the results page (all required):
- `raw`, `max`, `scaled` (1 d.p.)
- `next_whole_grade` = floor(scaled) + 1 (null if ≥ 9.0)
- `raw_needed_for_next` = min raw with scaled ≥ next_whole_grade; `marks_to_next` = that − raw
- grade ladder: for g in 2..9, min raw achieving g.0
- per-topic and per-spec-reference correct/total
- time per question, flagged slow when > 1.8 × mean
- unanswered count, flagged count, changed-answer count (answer edited after first selection)

The ESAT anchors above are a first guess scaled from the TMUA ones by 27/40. Both sets must be editable in the admin panel without a deploy.

## 2. Paper JSON format

One file per paper under `content/exam_papers/<family>/<paper_code>.json`. Loader validates and upserts.

```json
{
  "paper_code": "TMUA-P1-A",
  "family": "TMUA",              // TMUA | ESAT
  "module": "P1",                // P1 | P2 | M1 | M2 | PHY | CHM | BIO
  "title": "Paper 1: Applications of Mathematical Knowledge",
  "series": "Telos Mock A",
  "spec_version": "2026-27",
  "duration_sec": 4500,
  "marks_per_question": 1,
  "target_note": "7+ candidates: 15+/20 with time to spare",
  "questions": [
    {
      "n": 1,
      "topic": "Indices & exponential equations",
      "spec_refs": ["MM1.1","MM5.3"],
      "difficulty": 2,                    // 1–5, for per-paper balance checks
      "stem_html": "...",                 // sanitised HTML, inline math as HTML (sup/sub/fraction spans)
      "diagram_svg": null,                // full <svg> string or null; original, no external refs
      "options": {"A":"...","B":"...","C":"...","D":"...","E":"...","F":"..."},
      "answer": "C",
      "solution_html": "...",             // full worked solution
      "traps": {"A":"why A is wrong", "B":"...", ...}   // one per wrong option
    }
  ]
}
```

Validation on load (reject the file if any fail): 20 or 27 questions; `answer` ∈ options; every wrong option has a trap; no two options textually identical; every `spec_refs` entry exists in the spec table for that module; difficulty histogram present in loader output so the author can see the ramp.

## 3. Database (Postgres/Neon)

```sql
exam_papers(id, paper_code unique, family, module, title, series, spec_version, duration_sec, question_count, is_published bool, created_at)
exam_questions(id, paper_id fk, n, topic, spec_refs text[], difficulty int, stem_html, diagram_svg, options jsonb, answer char(1), solution_html, traps jsonb)
exam_scale_anchors(id, family, module nullable, anchors jsonb, active bool, note)
exam_attempts(id, user_id fk, paper_id fk, started_at timestamptz, ends_at timestamptz, submitted_at nullable, status enum('live','submitted','expired'), raw int null, scaled numeric(3,1) null, metrics jsonb null, client_meta jsonb)
exam_responses(attempt_id fk, question_id fk, selected char(1) null, flagged bool default false, time_sec int default 0, change_count int default 0, updated_at, primary key(attempt_id, question_id))
```

Indices: `exam_attempts(user_id, status)`, `exam_responses(attempt_id)`.

Free users can see the Exam Mode tab and the paper list but every start action returns 402 → upgrade modal. One live attempt per user per paper at a time; a second start resumes the live one.

## 4. Routes (Flask blueprint `exam`)

```
GET  /exam                               tab: paper list, past attempts, best scores
POST /exam/<paper_code>/start            Pro only. Creates attempt, ends_at = now + duration. Returns attempt id. Idempotent if live attempt exists.
GET  /exam/attempt/<id>                  player page. Server sends questions WITHOUT answer/solution/traps. Sends server-computed remaining_sec.
POST /exam/attempt/<id>/answer           {question_id, selected|null, flagged} → upsert response, increment change_count when selected changes. 409 if attempt not live or past ends_at.
POST /exam/attempt/<id>/time             {question_id, delta_sec} batched every 10s from client; server clamps to attempt window.
POST /exam/attempt/<id>/submit           marks, scales, stores metrics, status→submitted. Also called by a cron/lazy check that expires overdue live attempts on next request.
GET  /exam/attempt/<id>/results          full results incl. solutions + traps. Only after submitted/expired.
GET  /exam/attempt/<id>/results.json     same, for the results page JS.
POST /admin/exam/load                    upload/validate/upsert a paper JSON (admin only)
GET/POST /admin/exam/anchors             view/edit scale anchors
```

Timer is server-authoritative: the client counts down from `remaining_sec` but every write is validated against `ends_at`, and submit after `ends_at` is accepted but stamped `expired`. Refresh, tab close, or device switch does not reset the clock.

## 5. Player behaviour (matches the Pearson VUE test player flow)

1. **Instructions screen**: paper title, question count, duration, no-calculator reminder, "Start test". Clock starts on click.
2. **Question screen**: header bar with paper name, "Question n of N", "Time remaining mm:ss" (turns red at 5:00). One question per screen. Radio options with letter keys. Bottom bar: Previous · Next · Flag for review · Navigator · Review. Answer autosaves on selection.
3. **Navigator drawer**: grid of question numbers; answered = green border, flagged = orange corner, current = ring. Click to jump.
4. **Review screen**: table of every question with status (Answered / Unanswered / Flagged), filters All / Unanswered / Flagged, "Go to question", "Back to test", "End test".
5. **End test confirmation**: modal states the number of unanswered questions and that there is no penalty; "Return to review" or "End test". Ending is final.
6. **Auto-submit** at 00:00 with a "Time expired" state.
7. **Results** (Telos black/gold, not Pearson): scaled score hero, raw, marks to next whole grade, time used, grade ladder, by-topic, per-question rows (Correct / Wrong / No answer, your answer vs key, time, slow flag) expanding to stem + diagram + full solution + "why your option is wrong" if wrong. Buttons: sit again, open all solutions.

Authentic light theme by default in the player (that is what students will face); optional dark toggle. Nothing in the player uses Pearson VUE names, logos or branding.

Keyboard: arrow keys move between questions, 1–8 or A–H selects, F flags. Visible focus states. Works at 380px width.

## 6. Anti-leak

Player HTML never contains answers, solutions or traps. Results JSON is only served for submitted attempts of the requesting user. Question `stem_html` and `diagram_svg` are the only content fields sent during a live attempt.

## 7. Content pipeline

- Claude (chat) writes one paper per turn as JSON matching §2, each with a difficulty ramp report and a spec-coverage table.
- Reference implementation: `player_template.html` + `build.py` (injects a paper JSON into the template), `validate.py` (the §2 checks), `rebalance.py` (permutes options to even out answer letters). Claude Code should port its `scaledFrom40`, `minRawFor`, results layout and player flow rather than reinvent them.
- Mock A set: TMUA-P1-A, TMUA-P2-A, ESAT-M1-A, ESAT-M2-A, ESAT-PHY-A.

## 8. Claude Code handoff — phase prompts

**Phase 1 (schema + loader).** "In the Telos repo, add an `exam` blueprint. Create the tables in §3 as a migration compatible with the existing Neon Postgres setup and db.py shim. Write `content/exam_papers/loader.py` that validates a paper JSON against §2 (all listed checks) and upserts it. Add an admin route to upload a JSON and show the validation report. Seed `exam_scale_anchors` with the two anchor sets in §1. Do not touch existing tables. Run the migration locally and confirm with a test paper containing 2 questions."

**Phase 2 (attempt lifecycle).** "Implement the routes in §4 with server-authoritative timing. Enforce Pro gating using the existing Free/Pro tier check. Write tests: start → answer → submit computes raw and scaled correctly; submit after ends_at yields status expired; a Free user gets 402 on start; a second start on a live attempt resumes it."

**Phase 3 (player).** "Port the player from `telos_tmua_p1_mock.html` into a Jinja template + static JS that fetches from the attempt routes. Keep the exact screen flow in §5. Autosave answers on change; batch time deltas every 10 s. Never include answers in the page."

**Phase 4 (results).** "Port the results screen. Compute the metrics in §1 server-side at submit and store in `exam_attempts.metrics`. Results page reads from `/results.json`. Show the estimate disclaimer verbatim."

**Phase 5 (load Mock A + QA).** "Load the five Mock A JSON files. Run the QA checklist: sit each paper end-to-end as a Pro user, force a timer expiry, refresh mid-attempt, switch device mid-attempt, confirm no answer data in page source during a live attempt, confirm Free users cannot start."
