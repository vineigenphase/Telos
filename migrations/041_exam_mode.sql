-- 041_exam_mode.sql
-- Exam Mode — original TMUA/ESAT mock papers sat under test conditions.
--
-- Six tables from the engine spec, plus one the spec needs but does not
-- define. Section 2 requires the loader to reject a paper if any spec_refs
-- entry does not "exist in the spec table for that module", and no such table
-- appears in section 3. Without it that validation cannot run, and it is the
-- one that enforces the spec's own hard rules — the sine and cosine rules live
-- in MM4.1, so a question carrying that reference must not appear in ESAT
-- Maths 1 or TMUA Part 2, where candidates are not expected to recall them.
-- exam_spec_refs is that table.
--
-- Nothing here touches an existing table.
--
-- Idempotent.

-- ── papers ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS exam_papers (
    id             SERIAL PRIMARY KEY,
    paper_code     TEXT NOT NULL UNIQUE,
    family         TEXT NOT NULL CHECK (family IN ('TMUA', 'ESAT')),
    module         TEXT NOT NULL CHECK (module IN ('P1', 'P2', 'M1', 'M2', 'PHY', 'CHM', 'BIO')),
    title          TEXT NOT NULL,
    series         TEXT,
    spec_version   TEXT,
    duration_sec   INTEGER NOT NULL CHECK (duration_sec > 0),
    question_count INTEGER NOT NULL CHECK (question_count > 0),
    is_published   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── questions ───────────────────────────────────────────────────────────────
-- answer is CHAR(1) A-H: the real papers run to eight options, not five, which
-- the ENGAA answer keys confirm.
CREATE TABLE IF NOT EXISTS exam_questions (
    id            SERIAL PRIMARY KEY,
    paper_id      INTEGER NOT NULL REFERENCES exam_papers(id) ON DELETE CASCADE,
    n             INTEGER NOT NULL CHECK (n > 0),
    topic         TEXT,
    spec_refs     TEXT[] NOT NULL DEFAULT '{}',
    difficulty    INTEGER CHECK (difficulty BETWEEN 1 AND 5),
    stem_html     TEXT NOT NULL,
    diagram_svg   TEXT,
    options       JSONB NOT NULL,
    answer        CHAR(1) NOT NULL CHECK (answer ~ '^[A-H]$'),
    solution_html TEXT,
    traps         JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (paper_id, n)
);

-- ── scale anchors ───────────────────────────────────────────────────────────
-- Editable without a deploy, per the spec. `module` NULL means the anchors
-- apply to the whole family.
CREATE TABLE IF NOT EXISTS exam_scale_anchors (
    id      SERIAL PRIMARY KEY,
    family  TEXT NOT NULL CHECK (family IN ('TMUA', 'ESAT')),
    module  TEXT,
    anchors JSONB NOT NULL,
    active  BOOLEAN NOT NULL DEFAULT TRUE,
    note    TEXT
);

-- One active anchor set per family+module. A partial unique index rather than
-- a constraint, because inactive historical sets must be allowed to pile up.
CREATE UNIQUE INDEX IF NOT EXISTS exam_scale_anchors_active_family
    ON exam_scale_anchors (family, COALESCE(module, '')) WHERE active;

-- ── attempts ────────────────────────────────────────────────────────────────
-- status is TEXT + CHECK rather than a Postgres ENUM: adding a value to an
-- ENUM later needs ALTER TYPE, which does not compose with the
-- re-runnable-migration rule this repo works to.
CREATE TABLE IF NOT EXISTS exam_attempts (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    paper_id     INTEGER NOT NULL REFERENCES exam_papers(id) ON DELETE CASCADE,
    started_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ends_at      TIMESTAMPTZ NOT NULL,
    submitted_at TIMESTAMPTZ,
    status       TEXT NOT NULL DEFAULT 'live'
                 CHECK (status IN ('live', 'submitted', 'expired')),
    raw          INTEGER,
    scaled       NUMERIC(3, 1),
    metrics      JSONB,
    client_meta  JSONB
);

-- ── responses ───────────────────────────────────────────────────────────────
-- selected is nullable: an unanswered question is a row with no letter, which
-- is what lets the review screen count unanswered without a second query.
CREATE TABLE IF NOT EXISTS exam_responses (
    attempt_id   INTEGER NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    question_id  INTEGER NOT NULL REFERENCES exam_questions(id) ON DELETE CASCADE,
    selected     CHAR(1) CHECK (selected IS NULL OR selected ~ '^[A-H]$'),
    flagged      BOOLEAN NOT NULL DEFAULT FALSE,
    time_sec     INTEGER NOT NULL DEFAULT 0 CHECK (time_sec >= 0),
    change_count INTEGER NOT NULL DEFAULT 0 CHECK (change_count >= 0),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (attempt_id, question_id)
);

-- ── specification references ────────────────────────────────────────────────
-- The table section 2's validation needs and section 3 omits.
--
-- `code` is the reference as the awarding body writes it (MM4.1, M5.18, Arg1).
-- `modules` is every module the reference may legitimately appear in, which is
-- what makes the cross-module rules enforceable rather than advisory.
CREATE TABLE IF NOT EXISTS exam_spec_refs (
    id      SERIAL PRIMARY KEY,
    code    TEXT NOT NULL UNIQUE,
    family  TEXT NOT NULL CHECK (family IN ('TMUA', 'ESAT', 'BOTH')),
    modules TEXT[] NOT NULL,
    title   TEXT,
    note    TEXT
);

-- ── indices ─────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS exam_attempts_user_status
    ON exam_attempts (user_id, status);
CREATE INDEX IF NOT EXISTS exam_responses_attempt
    ON exam_responses (attempt_id);
CREATE INDEX IF NOT EXISTS exam_questions_paper
    ON exam_questions (paper_id, n);

-- ── seed: scale anchors ─────────────────────────────────────────────────────
--
-- From section 1. The TMUA set is on the 40-mark full-sitting basis; a single
-- paper is scaled up by 40/20 before interpolation. The ESAT set is the spec's
-- own first guess, scaled from TMUA by 27/40, and the note says so — these are
-- an estimate presented as an estimate, and the admin screen exists so they can
-- be recalibrated without a deploy.
--
-- No raw-to-scale conversion has ever been published for either test, in any
-- year. Anything circulating as one is a reconstruction, not an official
-- document, which is exactly why these are editable and labelled.
INSERT INTO exam_scale_anchors (family, module, anchors, active, note)
SELECT 'TMUA', NULL,
       '[[0,1.0],[8,2.0],[14,3.3],[20,4.5],[26,6.0],[30,7.0],[34,8.0],[38,8.8],[40,9.0]]'::jsonb,
       TRUE,
       'Engine spec v1 section 1. 40-mark full-sitting basis; a single paper is scaled by 40/20 first. Estimated — UAT-UK publishes no raw-to-scale table.'
WHERE NOT EXISTS (
    SELECT 1 FROM exam_scale_anchors WHERE family = 'TMUA' AND module IS NULL AND active
);

INSERT INTO exam_scale_anchors (family, module, anchors, active, note)
SELECT 'ESAT', NULL,
       '[[0,1.0],[5,2.0],[9,3.3],[13,4.5],[17,6.0],[20,7.0],[23,8.0],[26,8.8],[27,9.0]]'::jsonb,
       TRUE,
       'Engine spec v1 section 1. 27 marks per module, scored separately as in the real test. First guess, scaled from the TMUA set by 27/40 — recalibrate here rather than in code.'
WHERE NOT EXISTS (
    SELECT 1 FROM exam_scale_anchors WHERE family = 'ESAT' AND module IS NULL AND active
);

-- ── seed: specification reference groups ────────────────────────────────────
--
-- Seeded at GROUP level. A question citing "MM4.1" validates against the MM4
-- group, because the awarding body's full sub-point lists are not in the repo
-- and inventing them would be worse than validating one level up. What this
-- does enforce is the part that actually matters: which groups a module may
-- draw on at all.
--
-- That is what turns the spec's prose rules into checks. ESAT Maths 1 (module
-- M1) permits only M-group references, so a question tagged MM4.1 — the sine
-- and cosine rules — is rejected rather than shipped into a paper where
-- candidates are not expected to recall them.
--
-- Naming trap worth knowing: the Physics groups are P1-P7 and the TMUA modules
-- are also called P1 and P2. Different columns, no collision in the data, but
-- do not read `code` and `modules` as the same namespace.

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'MM1', 'TMUA', '{P1,P2,M2}'::text[], 'Section 1 Part 1 / ESAT Maths 2. Sine and cosine rules live here (MM4.1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'MM1');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'MM2', 'TMUA', '{P1,P2,M2}'::text[], 'Section 1 Part 1 / ESAT Maths 2. Sine and cosine rules live here (MM4.1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'MM2');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'MM3', 'TMUA', '{P1,P2,M2}'::text[], 'Section 1 Part 1 / ESAT Maths 2. Sine and cosine rules live here (MM4.1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'MM3');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'MM4', 'TMUA', '{P1,P2,M2}'::text[], 'Section 1 Part 1 / ESAT Maths 2. Sine and cosine rules live here (MM4.1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'MM4');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'MM5', 'TMUA', '{P1,P2,M2}'::text[], 'Section 1 Part 1 / ESAT Maths 2. Sine and cosine rules live here (MM4.1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'MM5');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'MM6', 'TMUA', '{P1,P2,M2}'::text[], 'Section 1 Part 1 / ESAT Maths 2. Sine and cosine rules live here (MM4.1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'MM6');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'MM7', 'TMUA', '{P1,P2,M2}'::text[], 'Section 1 Part 1 / ESAT Maths 2. Sine and cosine rules live here (MM4.1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'MM7');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'MM8', 'TMUA', '{P1,P2,M2}'::text[], 'Section 1 Part 1 / ESAT Maths 2. Sine and cosine rules live here (MM4.1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'MM8');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'M1', 'BOTH', '{P1,P2,M1,M2,PHY}'::text[], 'Section 1 Part 2 / ESAT Maths 1. Candidates are NOT expected to recall the sine or cosine rules here (M5.18).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'M1');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'M2', 'BOTH', '{P1,P2,M1,M2,PHY}'::text[], 'Section 1 Part 2 / ESAT Maths 1. Candidates are NOT expected to recall the sine or cosine rules here (M5.18).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'M2');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'M3', 'BOTH', '{P1,P2,M1,M2,PHY}'::text[], 'Section 1 Part 2 / ESAT Maths 1. Candidates are NOT expected to recall the sine or cosine rules here (M5.18).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'M3');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'M4', 'BOTH', '{P1,P2,M1,M2,PHY}'::text[], 'Section 1 Part 2 / ESAT Maths 1. Candidates are NOT expected to recall the sine or cosine rules here (M5.18).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'M4');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'M5', 'BOTH', '{P1,P2,M1,M2,PHY}'::text[], 'Section 1 Part 2 / ESAT Maths 1. Candidates are NOT expected to recall the sine or cosine rules here (M5.18).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'M5');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'M6', 'BOTH', '{P1,P2,M1,M2,PHY}'::text[], 'Section 1 Part 2 / ESAT Maths 1. Candidates are NOT expected to recall the sine or cosine rules here (M5.18).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'M6');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'M7', 'BOTH', '{P1,P2,M1,M2,PHY}'::text[], 'Section 1 Part 2 / ESAT Maths 1. Candidates are NOT expected to recall the sine or cosine rules here (M5.18).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'M7');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Arg1', 'TMUA', '{P2}'::text[], 'Logic and argument. TMUA Paper 2 only. Prose only — no symbolic notation, no truth tables (Arg1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Arg1');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Arg2', 'TMUA', '{P2}'::text[], 'Logic and argument. TMUA Paper 2 only. Prose only — no symbolic notation, no truth tables (Arg1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Arg2');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Arg3', 'TMUA', '{P2}'::text[], 'Logic and argument. TMUA Paper 2 only. Prose only — no symbolic notation, no truth tables (Arg1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Arg3');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Arg4', 'TMUA', '{P2}'::text[], 'Logic and argument. TMUA Paper 2 only. Prose only — no symbolic notation, no truth tables (Arg1).'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Arg4');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Prf1', 'TMUA', '{P2}'::text[], 'Proof. TMUA Paper 2 only.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Prf1');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Prf2', 'TMUA', '{P2}'::text[], 'Proof. TMUA Paper 2 only.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Prf2');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Prf3', 'TMUA', '{P2}'::text[], 'Proof. TMUA Paper 2 only.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Prf3');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Prf4', 'TMUA', '{P2}'::text[], 'Proof. TMUA Paper 2 only.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Prf4');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Prf5', 'TMUA', '{P2}'::text[], 'Proof. TMUA Paper 2 only.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Prf5');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Err1', 'TMUA', '{P2}'::text[], 'Identifying errors in reasoning. TMUA Paper 2 only.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Err1');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'Err2', 'TMUA', '{P2}'::text[], 'Identifying errors in reasoning. TMUA Paper 2 only.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'Err2');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'P1', 'ESAT', '{PHY}'::text[], 'ESAT Physics. The specification lists its equations explicitly; nothing outside that list may be required.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'P1');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'P2', 'ESAT', '{PHY}'::text[], 'ESAT Physics. The specification lists its equations explicitly; nothing outside that list may be required.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'P2');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'P3', 'ESAT', '{PHY}'::text[], 'ESAT Physics. The specification lists its equations explicitly; nothing outside that list may be required.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'P3');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'P4', 'ESAT', '{PHY}'::text[], 'ESAT Physics. The specification lists its equations explicitly; nothing outside that list may be required.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'P4');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'P5', 'ESAT', '{PHY}'::text[], 'ESAT Physics. The specification lists its equations explicitly; nothing outside that list may be required.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'P5');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'P6', 'ESAT', '{PHY}'::text[], 'ESAT Physics. The specification lists its equations explicitly; nothing outside that list may be required.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'P6');

INSERT INTO exam_spec_refs (code, family, modules, note)
SELECT 'P7', 'ESAT', '{PHY}'::text[], 'ESAT Physics. The specification lists its equations explicitly; nothing outside that list may be required.'
WHERE NOT EXISTS (SELECT 1 FROM exam_spec_refs WHERE code = 'P7');
