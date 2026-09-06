"""Validate and upsert an Exam Mode paper JSON.

Engine spec section 2. Validation is separated from the database the same way
prediction.py is separated from Flask: `validate()` is pure and takes the spec
table as an argument, so every rule is testable without a connection, and
`upsert()` does the I/O.

A paper that fails ANY check is rejected whole. Loading eighteen of twenty
questions would leave a paper that looks complete, sits like a real test, and
is quietly wrong — the same reasoning as the answer-key extractor, which
refuses a half-parsed key.

The spec's checks, and where each lives below:

  * 20 or 27 questions                            _check_shape
  * answer is one of the options                  _check_question
  * every wrong option has a trap                 _check_question
  * no two options textually identical            _check_question
  * every spec_ref valid for this module          _check_spec_refs
  * difficulty histogram in the report            report()

Two checks are stricter than the spec's wording, and are flagged rather than
silently added. Both are recorded in the report as warnings, not errors, so a
paper still loads if the author disagrees:

  * question count against the FAMILY, not just "20 or 27" — TMUA is 20 and
    ESAT is 27, so a 27-question TMUA paper satisfies the letter of the rule
    and is still broken.
  * duration against the family — 4500s for TMUA, 2400s for ESAT.
"""

from __future__ import annotations

import json
import os
import re

# From engine spec section 0.
FAMILY_SHAPE = {
    "TMUA": {"questions": 20, "duration_sec": 4500},
    "ESAT": {"questions": 27, "duration_sec": 2400},
}
VALID_MODULES = {"P1", "P2", "M1", "M2", "PHY", "CHM", "BIO"}
OPTION_LETTERS = "ABCDEFGH"

# "MM4.1" -> "MM4"; "Arg1" -> "Arg1"; "M5.18" -> "M5"; "P1.2d" -> "P1". The
# group is what the seeded spec table holds, because the awarding body's full
# sub-point lists are not in the repo and inventing them would be worse than
# validating one level up. See the note in migration 041.
#
# The trailing letter matters. The maths specifications number sub-points
# numerically (M5.18), and the physics specification suffixes them with a
# letter (P1.2d, P3.7h, P6.1g). An earlier version of this pattern allowed only
# the numeric form and rejected all 64 references in the Physics mock as
# unrecognisable — the papers were right and the pattern was wrong.
_GROUP = re.compile(r"^([A-Za-z]+\d+)(?:\.\d+[a-z]?)*$", re.IGNORECASE)


def spec_group(ref):
    m = _GROUP.match((ref or "").strip())
    return m.group(1) if m else None


# The mark basis a scaled score is computed against: 40 for a TMUA sitting of
# two papers, 27 for an ESAT module. Carried in every paper JSON, so it is read
# from the file and only falls back to the family default when absent — the
# file is the author's statement of intent, and deriving it would silently
# ignore a paper that says something different.
FAMILY_MARKS = {"TMUA": 40, "ESAT": 27}


def family_marks_of(paper):
    return paper.get("family_marks") or FAMILY_MARKS.get(paper.get("family"), 0)


class PaperInvalid(Exception):
    """Carries every problem found, not just the first."""

    def __init__(self, problems):
        self.problems = problems
        super().__init__(f"{len(problems)} problem(s): " + "; ".join(problems[:3]))


# ---------------------------------------------------------------------------
# validation — pure
# ---------------------------------------------------------------------------

def _check_shape(paper, errors, warnings):
    for field in ("paper_code", "family", "module", "title", "duration_sec", "questions"):
        if not paper.get(field):
            errors.append(f"missing required field: {field}")
    family = paper.get("family")
    if family not in FAMILY_SHAPE:
        errors.append(f"family must be TMUA or ESAT, got {family!r}")
    if paper.get("module") not in VALID_MODULES:
        errors.append(f"module must be one of {sorted(VALID_MODULES)}, "
                      f"got {paper.get('module')!r}")

    qs = paper.get("questions") or []
    if len(qs) not in (20, 27):
        errors.append(f"a paper has 20 or 27 questions, this one has {len(qs)}")

    if family in FAMILY_SHAPE:
        want = FAMILY_SHAPE[family]
        if qs and len(qs) != want["questions"]:
            warnings.append(f"{family} papers are {want['questions']} questions, "
                            f"this one has {len(qs)}")
        if paper.get("duration_sec") and paper["duration_sec"] != want["duration_sec"]:
            warnings.append(f"{family} runs {want['duration_sec']}s, "
                            f"this paper says {paper['duration_sec']}s")
        # family_marks drives the scaling, so a wrong one silently mis-scores
        # every attempt rather than failing visibly.
        fm = paper.get("family_marks")
        if fm is not None and fm != FAMILY_MARKS[family]:
            warnings.append(f"{family} scales against {FAMILY_MARKS[family]} marks, "
                            f"this paper says family_marks={fm}")
        if fm is not None and (not isinstance(fm, int) or fm <= 0):
            errors.append(f"family_marks must be a positive integer, got {fm!r}")

    ns = [q.get("n") for q in qs]
    if qs and sorted(n for n in ns if isinstance(n, int)) != list(range(1, len(qs) + 1)):
        errors.append(f"question numbers must run 1..{len(qs)} exactly once, got {ns}")


def _check_question(q, errors):
    n = q.get("n", "?")
    opts = q.get("options") or {}
    if len(opts) < 5 or len(opts) > 8:
        errors.append(f"q{n}: 5-8 options required, got {len(opts)}")
    bad = [k for k in opts if k not in OPTION_LETTERS]
    if bad:
        errors.append(f"q{n}: option keys must be A-H, got {bad}")

    answer = q.get("answer")
    if answer not in opts:
        errors.append(f"q{n}: answer {answer!r} is not one of the options {sorted(opts)}")

    # Identical options make a question unanswerable however good the maths is.
    seen = {}
    for k, v in opts.items():
        norm = re.sub(r"\s+", " ", str(v)).strip().lower()
        if norm in seen:
            errors.append(f"q{n}: options {seen[norm]} and {k} are textually identical")
        seen[norm] = k

    # A trap per wrong option: the results screen promises "why your option is
    # wrong" for every wrong answer, so a missing one is a hole in the product,
    # not just in the data.
    traps = q.get("traps") or {}
    for k in opts:
        if k != answer and not str(traps.get(k, "")).strip():
            errors.append(f"q{n}: no trap explaining why {k} is wrong")
    stray = [k for k in traps if k not in opts]
    if stray:
        errors.append(f"q{n}: traps for options that do not exist: {stray}")
    if answer in traps:
        errors.append(f"q{n}: the correct answer {answer} has a trap explanation")

    if not str(q.get("stem_html", "")).strip():
        errors.append(f"q{n}: stem_html is empty")

    d = q.get("difficulty")
    if d is not None and (not isinstance(d, int) or not 1 <= d <= 5):
        errors.append(f"q{n}: difficulty must be 1-5, got {d!r}")


def _check_spec_refs(paper, spec_table, errors):
    """spec_table: {group_code: [modules it may appear in]}.

    This is the check the spec asks for and the one that enforces its prose
    rules. ESAT Maths 1 permits only M-group references, so a question tagged
    MM4.1 — the sine and cosine rules — is caught here rather than shipped into
    a paper where candidates are not expected to recall them.
    """
    module = paper.get("module")
    for q in paper.get("questions") or []:
        n = q.get("n", "?")
        refs = q.get("spec_refs") or []
        if not refs:
            errors.append(f"q{n}: no spec_refs")
            continue
        for ref in refs:
            group = spec_group(ref)
            if group is None:
                errors.append(f"q{n}: spec_ref {ref!r} is not a recognisable reference")
                continue
            if group not in spec_table:
                errors.append(f"q{n}: spec_ref {ref!r} (group {group}) is not in the "
                              f"specification table")
                continue
            allowed = spec_table[group]
            if module not in allowed:
                errors.append(f"q{n}: spec_ref {ref!r} belongs to {group}, which module "
                              f"{module} may not draw on (allowed: {sorted(allowed)})")


def validate(paper, spec_table):
    """(errors, warnings). Empty errors means the paper may be loaded."""
    errors, warnings = [], []
    _check_shape(paper, errors, warnings)
    for q in paper.get("questions") or []:
        _check_question(q, errors)
    _check_spec_refs(paper, spec_table, errors)
    return errors, warnings


def report(paper, errors, warnings):
    """Human-readable validation report, including the difficulty ramp.

    The histogram is required by the spec so the author can see whether the
    paper actually ramps. A paper of twenty level-3 questions passes every
    other check and is a bad test.
    """
    qs = paper.get("questions") or []
    lines = [f"{paper.get('paper_code', '?')} — {paper.get('family', '?')} "
             f"{paper.get('module', '?')} — {len(qs)} questions"]

    hist = {}
    for q in qs:
        hist[q.get("difficulty")] = hist.get(q.get("difficulty"), 0) + 1
    if hist:
        lines.append("difficulty ramp:")
        for d in sorted(k for k in hist if k is not None):
            lines.append(f"   {d}  {'#' * hist[d]} ({hist[d]})")
        if None in hist:
            lines.append(f"   ?  {'#' * hist[None]} ({hist[None]} with no difficulty)")

    groups = {}
    for q in qs:
        for ref in q.get("spec_refs") or []:
            g = spec_group(ref)
            groups[g] = groups.get(g, 0) + 1
    if groups:
        # Sorted by a string key, not the raw one. An unrecognisable reference
        # yields a group of None, and sorting None against a string raises —
        # which crashed the report before it could print the errors that were
        # about to name the bad reference. The report has to survive the very
        # thing it exists to tell you about.
        lines.append("spec coverage: " +
                     ", ".join(f"{g or '(unrecognised)'} x{n}"
                               for g, n in sorted(groups.items(),
                                                  key=lambda kv: (kv[0] is None, kv[0] or ""))))

    for w in warnings:
        lines.append(f"WARNING  {w}")
    for e in errors:
        lines.append(f"ERROR    {e}")
    lines.append("REJECTED — nothing was written" if errors else "OK — ready to load")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# database
# ---------------------------------------------------------------------------

def spec_table_from_db(db):
    rows = db.execute("SELECT code, modules FROM exam_spec_refs").fetchall()
    return {r["code"]: list(r["modules"]) for r in rows}


def upsert(db, paper):
    """Write a validated paper. Replaces its questions wholesale.

    Questions are deleted and reinserted rather than merged: a paper is edited
    as a document, and a merge would leave an orphaned question 21 behind if
    the author shortened it.
    """
    row = db.execute(
        """INSERT INTO exam_papers
             (paper_code, family, module, title, series, spec_version,
              duration_sec, question_count, is_published, family_marks)
           VALUES (?,?,?,?,?,?,?,?,FALSE,?)
           ON CONFLICT (paper_code) DO UPDATE SET
             family=EXCLUDED.family, module=EXCLUDED.module, title=EXCLUDED.title,
             series=EXCLUDED.series, spec_version=EXCLUDED.spec_version,
             duration_sec=EXCLUDED.duration_sec,
             question_count=EXCLUDED.question_count,
             family_marks=EXCLUDED.family_marks
           RETURNING id""",
        (paper["paper_code"], paper["family"], paper["module"], paper["title"],
         paper.get("series"), paper.get("spec_version"), paper["duration_sec"],
         len(paper["questions"]), family_marks_of(paper))).fetchone()
    paper_id = row["id"]

    db.execute("DELETE FROM exam_questions WHERE paper_id=?", (paper_id,))
    for q in paper["questions"]:
        db.execute(
            """INSERT INTO exam_questions
                 (paper_id, n, topic, spec_refs, difficulty, stem_html,
                  diagram_svg, options, answer, solution_html, traps)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (paper_id, q["n"], q.get("topic"), q.get("spec_refs") or [],
             q.get("difficulty"), q["stem_html"], q.get("diagram_svg"),
             json.dumps(q["options"]), q["answer"], q.get("solution_html"),
             json.dumps(q.get("traps") or {})))
    return paper_id


def load_file(db, path):
    """Validate then upsert one file. Returns (paper_id_or_None, report_text)."""
    with open(path, encoding="utf-8") as fh:
        paper = json.load(fh)
    errors, warnings = validate(paper, spec_table_from_db(db))
    text = report(paper, errors, warnings)
    if errors:
        return None, text
    return upsert(db, paper), text


def main(argv=None):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
    from db import get_db

    paths = (argv or sys.argv[1:])
    if not paths:
        print("usage: loader.py <paper.json> [...]")
        return 1
    bad = 0
    for p in paths:
        with get_db() as db:
            pid, text = load_file(db, p)
        print(text)
        print()
        if pid is None:
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
