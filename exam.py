"""Exam Mode — the `exam` blueprint.

Engine spec v1. Phase 1 is the schema, the loader and the two admin screens;
the attempt lifecycle (section 4) and the player (section 5) land in later
phases.

A blueprint rather than more routes in app.py because the spec asks for one and
because this feature is large enough to be worth a boundary — it owns six
tables nothing else touches. `requires_admin` comes from auth.py rather than
app.py, since app.py registers this blueprint and importing back would be
circular.

Anti-leak (section 6) is a rule about this module specifically: `answer`,
`solution_html` and `traps` must never reach a page during a live attempt. The
query helpers below are split so that the live-attempt path physically cannot
select those columns, rather than relying on remembering to strip them.
"""

from __future__ import annotations

import json

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import login_required

from auth import requires_admin
from db import get_db

exam = Blueprint("exam", __name__)


# ---------------------------------------------------------------------------
# Columns a live attempt may see. See section 6.
# ---------------------------------------------------------------------------
#
# Written as a constant and used by the player query so the safe set is stated
# once, in one place, and a future edit to the player cannot quietly widen it.
LIVE_QUESTION_COLUMNS = "id, n, topic, stem_html, diagram_svg, options"
GRADED_QUESTION_COLUMNS = LIVE_QUESTION_COLUMNS + ", answer, solution_html, traps, spec_refs, difficulty"


def _anchor_sets(db):
    return db.execute(
        "SELECT id, family, module, anchors, active, note FROM exam_scale_anchors "
        "ORDER BY family, module NULLS FIRST, id").fetchall()


# ---------------------------------------------------------------------------
# Admin — paper loading
# ---------------------------------------------------------------------------

@exam.route("/admin/exam/load", methods=["GET", "POST"])
@login_required
@requires_admin
def admin_load():
    """Upload a paper JSON, validate it, and upsert only if it is clean.

    The validation report is shown whether or not the paper loaded, because a
    rejected paper's report is the thing the author actually needs — it names
    every problem at once rather than the first.
    """
    report_text, loaded = None, False
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not f.filename:
            flash("Choose a paper JSON file.", "error")
            return redirect(url_for("exam.admin_load"))
        if not f.filename.lower().endswith(".json"):
            flash("Exam papers are JSON files.", "error")
            return redirect(url_for("exam.admin_load"))

        # Imported here rather than at module level: content/ is data, not part
        # of the application package, and only this route needs it.
        import os
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "content", "exam_papers"))
        import loader as paper_loader

        try:
            paper = json.load(f.stream)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            flash(f"That file is not valid JSON: {e}", "error")
            return redirect(url_for("exam.admin_load"))

        with get_db() as db:
            errors, warnings = paper_loader.validate(
                paper, paper_loader.spec_table_from_db(db))
            report_text = paper_loader.report(paper, errors, warnings)
            if not errors:
                paper_loader.upsert(db, paper)
                loaded = True

        flash(f"Loaded {paper.get('paper_code')}." if loaded
              else "Rejected — nothing was written. See the report.",
              "success" if loaded else "error")

    with get_db() as db:
        papers = db.execute(
            "SELECT id, paper_code, family, module, title, series, question_count, "
            "       duration_sec, is_published, created_at "
            "FROM exam_papers ORDER BY family, module, paper_code").fetchall()
    return render_template("admin_exam_load.html", papers=papers,
                           report=report_text, loaded=loaded)


@exam.route("/admin/exam/papers/<int:paper_id>/publish", methods=["POST"])
@login_required
@requires_admin
def admin_publish(paper_id):
    """Publish or unpublish a paper. Papers load unpublished by design, so a
    half-checked paper cannot appear to students the moment it is uploaded."""
    want = request.form.get("publish") == "1"
    with get_db() as db:
        db.execute("UPDATE exam_papers SET is_published=? WHERE id=?", (want, paper_id))
    flash("Published." if want else "Unpublished.", "success")
    return redirect(url_for("exam.admin_load"))


# ---------------------------------------------------------------------------
# Admin — scale anchors
# ---------------------------------------------------------------------------

@exam.route("/admin/exam/anchors", methods=["GET", "POST"])
@login_required
@requires_admin
def admin_anchors():
    """View and edit the raw-to-scale anchor sets.

    Editable without a deploy, per section 1, because these are an estimate and
    will need recalibrating. No raw-to-scale conversion has ever been published
    for TMUA or ESAT in any year, so nothing here can be checked against an
    official table — which is exactly why it must be easy to change.
    """
    if request.method == "POST":
        anchor_id = request.form.get("id", type=int)
        raw = (request.form.get("anchors") or "").strip()
        note = (request.form.get("note") or "").strip() or None
        problems = []
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            parsed = None
            problems.append(f"not valid JSON: {e}")

        if parsed is not None:
            if not isinstance(parsed, list) or len(parsed) < 2:
                problems.append("anchors must be a list of at least two [mark, score] pairs")
            else:
                marks, scores = [], []
                for pair in parsed:
                    if (not isinstance(pair, (list, tuple)) or len(pair) != 2
                            or not all(isinstance(v, (int, float)) for v in pair)):
                        problems.append(f"{pair!r} is not a [mark, score] pair of numbers")
                        break
                    marks.append(pair[0])
                    scores.append(pair[1])
                else:
                    # Both axes must ascend, or interpolation between them is
                    # meaningless and a higher mark could score lower.
                    if marks != sorted(marks):
                        problems.append("marks must ascend")
                    if scores != sorted(scores):
                        problems.append("scores must ascend — otherwise a better "
                                        "raw mark could produce a lower scaled score")
                    if scores and (min(scores) < 1.0 or max(scores) > 9.0):
                        problems.append("scores must lie within 1.0-9.0")

        if problems:
            for p in problems:
                flash(p, "error")
        else:
            with get_db() as db:
                db.execute("UPDATE exam_scale_anchors SET anchors=?, note=? WHERE id=?",
                           (json.dumps(parsed), note, anchor_id))
            flash("Anchors updated.", "success")
        return redirect(url_for("exam.admin_anchors"))

    with get_db() as db:
        sets = _anchor_sets(db)
    return render_template("admin_exam_anchors.html", anchor_sets=sets)
