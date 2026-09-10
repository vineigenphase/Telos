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

from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from auth import requires_admin, user_is_pro
from paper_templates import all_qualifications, is_graded
from db import get_db
from exam_scoring import DEFAULT_ANCHORS, compute_metrics

exam = Blueprint("exam", __name__)

# Shown verbatim on every results page (section 4). UAT-UK equates each real
# sitting with a Rasch model against that year's own cohort and has never
# published a raw-to-scale table, so a Telos score is a modelled estimate and
# has to say so where the student reads it.
ESTIMATE_DISCLAIMER = (
    "This score is an estimate. UAT-UK scales each real sitting against that "
    "year's candidates and does not publish a raw-to-score table, so Telos "
    "models the conversion. Treat it as a guide to where you stand, not as a "
    "predicted result."
)


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


# ---------------------------------------------------------------------------
# Attempt lifecycle — engine spec section 4
# ---------------------------------------------------------------------------
#
# Timing is server-authoritative throughout. The client counts down from a
# `remaining_sec` the server computed, but every write revalidates against
# `ends_at`, so a refresh, a closed tab, a second device or a doctored clock
# cannot buy a student more time.

def _anchors_for(db, family, module=None):
    """The active anchor set, most specific first, falling back to the spec's
    published defaults if the row is somehow missing."""
    row = db.execute(
        "SELECT anchors FROM exam_scale_anchors WHERE family=? AND active "
        "  AND (module = ? OR module IS NULL) "
        "ORDER BY module NULLS LAST LIMIT 1", (family, module)).fetchone()
    if row:
        return [list(p) for p in row["anchors"]]
    return DEFAULT_ANCHORS.get(family) or DEFAULT_ANCHORS["TMUA"]


# The remaining time is computed IN SQL, by the same clock that wrote ends_at.
#
# It was computed in Python against a deadline written with Postgres NOW(), and
# the two clocks are not the same clock: measured at 1.84 seconds apart on this
# setup, with the database ahead. That difference was being handed to or taken
# from every candidate as exam time. It is small today and unbounded in
# principle — a drifting host clock would move it without anything failing.
#
# Reading both ends from the database removes the class of problem rather than
# the instance.
_REMAINING = ("GREATEST(0, FLOOR(EXTRACT(EPOCH FROM (a.ends_at - NOW()))))::int "
              "AS remaining_sec")


def _attempt_or_404(db, attempt_id):
    """An attempt belonging to the CURRENT user, or 404.

    404 rather than 403 on someone else's attempt: whether an attempt id exists
    is not something another user should be able to probe.
    """
    row = db.execute(
        "SELECT a.*, p.paper_code, p.family, p.module, p.title, p.duration_sec, "
        "       p.question_count, p.family_marks, " + _REMAINING + " "
        "FROM exam_attempts a JOIN exam_papers p ON p.id = a.paper_id "
        "WHERE a.id = ? AND a.user_id = ?", (attempt_id, current_user.id)).fetchone()
    if not row:
        abort(404)
    return row


def _remaining_sec(attempt):
    """Seconds left, as the database measured them when the row was read."""
    return int(attempt["remaining_sec"])


def _expire_if_overdue(db, attempt):
    """Lazily close an attempt whose clock ran out while nobody was looking.

    The spec allows a cron for this; a lazy check on next touch is enough and
    has no moving parts. A tab closed at question 3 and reopened next week must
    not still be live.
    """
    if attempt["status"] == "live" and _remaining_sec(attempt) <= 0:
        _finalise(db, attempt, expired=True)
        return True
    return False




# ---------------------------------------------------------------------------
# Access — who may sit a paper
# ---------------------------------------------------------------------------
#
# A paper is sittable if ANY of these holds:
#
#   * the user is Pro. Pro includes every paper, because a plan change must
#     never take something away from a subscriber;
#   * the paper is free (price_pence = 0);
#   * the user has bought that paper.
#
# Deliberately not Pro-only. A candidate three weeks from the ESAT wants a
# mock, not a subscription, and asking £4.99 a month to sit one paper loses the
# sale to everyone who only wants the paper.

def _access(db, paper):
    """(allowed, reason). `reason` is why, so the caller can say so."""
    if user_is_pro(current_user):
        return True, "pro"
    if not paper["price_pence"]:
        return True, "free"
    owned = db.execute(
        "SELECT 1 FROM exam_purchases WHERE user_id=? AND paper_id=?",
        (current_user.id, paper["id"])).fetchone()
    return (True, "owned") if owned else (False, None)


def _owned_paper_ids(db):
    return {r["paper_id"] for r in db.execute(
        "SELECT paper_id FROM exam_purchases WHERE user_id=?",
        (current_user.id,)).fetchall()}


def _price_label(pence):
    """£1 rather than £1.00, but £1.50 in full. A round pound should read as one."""
    if not pence:
        return "Free"
    pounds = pence / 100
    return f"£{int(pounds)}" if pence % 100 == 0 else f"£{pounds:.2f}"


def _access_or_402(db, paper):
    """None if this user may sit `paper`, otherwise a 402 saying what to do.

    Still a JSON 402 rather than a redirect, so the client can raise a buy
    prompt without losing the page. What changed is the remedy: it used to be
    "upgrade", and for a paid paper it is now "buy this one" with the price and
    the checkout URL, because that is the smaller ask and usually the right one.
    """
    allowed, _reason = _access(db, paper)
    if allowed:
        return None
    return jsonify({
        "error": "purchase_required",
        "message": f"{paper['title']} is {_price_label(paper['price_pence'])}, "
                   f"or included with Telos Pro.",
        "price_pence": paper["price_pence"],
        "price": _price_label(paper["price_pence"]),
        "buy_url": url_for("exam.buy", paper_code=paper["paper_code"]),
        "upgrade_url": url_for("subscription", **{"from": "exam-mode"}),
    }), 402


def _finalise(db, attempt, expired=False):
    """Mark, scale and store. The one place an attempt stops being live.

    Metrics are computed here and STORED rather than recomputed on each view of
    the results. The anchors are editable by design, so recomputing would let a
    student's recorded score move under them months later — a result is a
    record of a sitting, not a live query.
    """
    rows = db.execute(
        "SELECT question_id, selected, flagged, time_sec, change_count "
        "FROM exam_responses WHERE attempt_id=?", (attempt["id"],)).fetchall()
    questions = db.execute(
        "SELECT id, n, topic, spec_refs, answer FROM exam_questions "
        "WHERE paper_id=? ORDER BY n", (attempt["paper_id"],)).fetchall()

    anchors = _anchors_for(db, attempt["family"], attempt["module"])
    metrics = compute_metrics(
        [dict(r) for r in rows],
        [{"id": q["id"], "n": q["n"], "topic": q["topic"],
          "spec_refs": list(q["spec_refs"] or []), "answer": q["answer"]}
         for q in questions],
        attempt["family_marks"], anchors)

    db.execute(
        "UPDATE exam_attempts SET status=?, submitted_at=NOW(), raw=?, scaled=?, "
        "metrics=? WHERE id=?",
        ("expired" if expired else "submitted", metrics["raw"], metrics["scaled"],
         json.dumps(metrics), attempt["id"]))
    return metrics


# ---------------------------------------------------------------------------
# Routes — engine spec section 4
# ---------------------------------------------------------------------------

@exam.route("/exam")
@login_required
def index():
    """The tab. Visible to free users, who see the papers and cannot start one."""
    with get_db() as db:
        papers = db.execute(
            "SELECT id, paper_code, family, module, title, series, question_count, "
            "       duration_sec, price_pence FROM exam_papers WHERE is_published "
            "ORDER BY family, module, paper_code").fetchall()
        owned = _owned_paper_ids(db)
        attempts = db.execute(
            "SELECT a.id, a.paper_id, a.status, a.raw, a.scaled, a.started_at, "
            "       a.submitted_at, p.paper_code, p.title, p.question_count "
            "FROM exam_attempts a JOIN exam_papers p ON p.id=a.paper_id "
            "WHERE a.user_id=? ORDER BY a.started_at DESC LIMIT 50",
            (current_user.id,)).fetchall()
    best = {}
    for a in attempts:
        if a["scaled"] is not None:
            cur = best.get(a["paper_id"])
            if cur is None or a["scaled"] > cur:
                best[a["paper_id"]] = a["scaled"]
    return render_template("exam_index.html", papers=papers, attempts=attempts,
                           best=best, is_pro=user_is_pro(current_user),
                           owned=owned, price_label=_price_label)


@exam.route("/exam/<paper_code>/start", methods=["POST"])
@login_required
def start(paper_code):
    """Begin an attempt, or resume the live one.

    Idempotent by design (section 4): a second start while an attempt is live
    returns that attempt rather than a fresh one. Otherwise a double-tap, or a
    student reopening the tab, would silently discard the work already done and
    hand them a new clock.
    """
    with get_db() as db:
        paper = db.execute(
            "SELECT * FROM exam_papers WHERE paper_code=? AND is_published",
            (paper_code,)).fetchone()
        if not paper:
            abort(404)

        gate = _access_or_402(db, paper)
        if gate:
            return gate

        live = db.execute(
            "SELECT a.*, p.paper_code, p.family, p.module, p.title, p.duration_sec, "
            "       p.question_count, p.family_marks, " + _REMAINING + " "
            "FROM exam_attempts a JOIN exam_papers p ON p.id=a.paper_id "
            "WHERE a.user_id=? AND a.paper_id=? AND a.status='live' "
            "ORDER BY a.id DESC LIMIT 1", (current_user.id, paper["id"])).fetchone()

        if live:
            # A live attempt whose clock already ran out is closed rather than
            # resumed — resuming would hand back a dead timer.
            if not _expire_if_overdue(db, live):
                return jsonify({"attempt_id": live["id"], "resumed": True,
                                "remaining_sec": _remaining_sec(live)})

        row = db.execute(
            "INSERT INTO exam_attempts (user_id, paper_id, ends_at, client_meta) "
            "VALUES (?,?, NOW() + (? || ' seconds')::interval, ?) RETURNING id",
            (current_user.id, paper["id"], str(paper["duration_sec"]),
             json.dumps({"ua": (request.headers.get("User-Agent") or "")[:300]}))
        ).fetchone()
        # Read the clock back from the database rather than echoing the
        # paper's duration, so a fresh attempt and a resumed one are measured
        # the same way and cannot disagree by the round-trip.
        fresh = _attempt_or_404(db, row["id"])
        return jsonify({"attempt_id": row["id"], "resumed": False,
                        "remaining_sec": _remaining_sec(fresh)})


@exam.route("/exam/attempt/<int:attempt_id>/answer", methods=["POST"])
@login_required
def answer(attempt_id):
    """Record one answer. Refused once the attempt is no longer live.

    change_count increments only when the letter actually changes, so it counts
    a student changing their mind rather than the autosave firing.
    """
    data = request.get_json(silent=True) or {}
    with get_db() as db:
        attempt = _attempt_or_404(db, attempt_id)
        if _expire_if_overdue(db, attempt) or attempt["status"] != "live":
            return jsonify({"error": "attempt_not_live"}), 409

        qid = data.get("question_id")
        q = db.execute("SELECT id FROM exam_questions WHERE id=? AND paper_id=?",
                       (qid, attempt["paper_id"])).fetchone()
        if not q:
            return jsonify({"error": "unknown_question"}), 400

        selected = data.get("selected")
        if selected is not None:
            selected = str(selected).upper()[:1]
            if selected not in "ABCDEFGH":
                return jsonify({"error": "bad_option"}), 400
        flagged = bool(data.get("flagged", False))

        db.execute(
            "INSERT INTO exam_responses (attempt_id, question_id, selected, flagged) "
            "VALUES (?,?,?,?) "
            "ON CONFLICT (attempt_id, question_id) DO UPDATE SET "
            "  change_count = exam_responses.change_count + "
            "    CASE WHEN exam_responses.selected IS DISTINCT FROM EXCLUDED.selected "
            "         AND EXCLUDED.selected IS NOT NULL THEN 1 ELSE 0 END, "
            "  selected = EXCLUDED.selected, "
            "  flagged = EXCLUDED.flagged, "
            "  updated_at = NOW()",
            (attempt_id, qid, selected, flagged))
        return jsonify({"ok": True, "remaining_sec": _remaining_sec(attempt)})


@exam.route("/exam/attempt/<int:attempt_id>/time", methods=["POST"])
@login_required
def record_time(attempt_id):
    """Batched per-question time, sent every 10s by the client.

    The increment is clamped to the attempt's own window, so a client reporting
    an hour on one question cannot inflate the totals past the time the paper
    actually ran for.
    """
    data = request.get_json(silent=True) or {}
    with get_db() as db:
        attempt = _attempt_or_404(db, attempt_id)
        if attempt["status"] != "live":
            return jsonify({"error": "attempt_not_live"}), 409
        try:
            delta = int(data.get("delta_sec") or 0)
        except (TypeError, ValueError):
            return jsonify({"error": "bad_delta"}), 400
        delta = max(0, min(delta, int(attempt["duration_sec"])))
        qid = data.get("question_id")
        db.execute(
            "INSERT INTO exam_responses (attempt_id, question_id, time_sec) "
            "VALUES (?,?,?) ON CONFLICT (attempt_id, question_id) DO UPDATE SET "
            "  time_sec = LEAST(exam_responses.time_sec + EXCLUDED.time_sec, ?), "
            "  updated_at = NOW()",
            (attempt_id, qid, delta, int(attempt["duration_sec"])))
        return jsonify({"ok": True, "remaining_sec": _remaining_sec(attempt)})


@exam.route("/exam/attempt/<int:attempt_id>/submit", methods=["POST"])
@login_required
def submit(attempt_id):
    """End the attempt and mark it.

    A submit arriving after ends_at is ACCEPTED and stamped `expired` rather
    than refused: the work was done inside the window and only the last packet
    was late. Refusing it would throw away a completed paper over latency.
    """
    with get_db() as db:
        attempt = _attempt_or_404(db, attempt_id)
        if attempt["status"] != "live":
            # Already finished — usually because the clock ran out and an
            # earlier request closed it. Return the score anyway rather than a
            # bare acknowledgement: a client whose submit lost the race to
            # auto-expiry still needs the number to show.
            m = attempt["metrics"] or {}
            return jsonify({"attempt_id": attempt_id, "status": attempt["status"],
                            "already_submitted": True,
                            "raw": attempt["raw"], "scaled": float(attempt["scaled"])
                            if attempt["scaled"] is not None else None,
                            "metrics": m})
        expired = _remaining_sec(attempt) <= 0
        metrics = _finalise(db, attempt, expired=expired)
    return jsonify({"attempt_id": attempt_id,
                    "status": "expired" if expired else "submitted",
                    "raw": metrics["raw"], "scaled": metrics["scaled"]})


@exam.route("/exam/attempt/<int:attempt_id>/results.json")
@login_required
def results_json(attempt_id):
    """Full results, answers and all. Only for a finished attempt (section 6)."""
    with get_db() as db:
        attempt = _attempt_or_404(db, attempt_id)
        if _expire_if_overdue(db, attempt):
            attempt = _attempt_or_404(db, attempt_id)
        if attempt["status"] == "live":
            return jsonify({"error": "attempt_still_live"}), 409

        questions = db.execute(
            "SELECT " + GRADED_QUESTION_COLUMNS + " FROM exam_questions "
            "WHERE paper_id=? ORDER BY n", (attempt["paper_id"],)).fetchall()
        return jsonify({
            "attempt_id": attempt["id"],
            "paper": {"code": attempt["paper_code"], "title": attempt["title"],
                      "family": attempt["family"], "module": attempt["module"],
                      "question_count": attempt["question_count"],
                      "duration_sec": attempt["duration_sec"]},
            "status": attempt["status"],
            "metrics": attempt["metrics"],
            "questions": [dict(q) for q in questions],
            "disclaimer": ESTIMATE_DISCLAIMER,
        })


@exam.route("/exam/attempt/<int:attempt_id>")
@login_required
def player(attempt_id):
    """The test player.

    Section 6 is enforced here by construction rather than by discipline: the
    query selects LIVE_QUESTION_COLUMNS, which has no answer, no solution and
    no traps in it, so there is nothing in this handler's scope to leak into the
    page even by mistake.

    A finished attempt redirects to its results rather than reopening — a paper
    that has been ended cannot be re-entered, which is the whole point of
    ending it.
    """
    with get_db() as db:
        attempt = _attempt_or_404(db, attempt_id)
        _expire_if_overdue(db, attempt)
        attempt = _attempt_or_404(db, attempt_id)
        if attempt["status"] != "live":
            return redirect(url_for("exam.results", attempt_id=attempt_id))

        questions = db.execute(
            "SELECT " + LIVE_QUESTION_COLUMNS + " FROM exam_questions "
            "WHERE paper_id=? ORDER BY n", (attempt["paper_id"],)).fetchall()
        responses = db.execute(
            "SELECT question_id, selected, flagged FROM exam_responses "
            "WHERE attempt_id=?", (attempt_id,)).fetchall()

    saved = {r["question_id"]: {"selected": r["selected"], "flagged": r["flagged"]}
             for r in responses}
    payload = {
        "attempt_id": attempt["id"],
        "remaining_sec": _remaining_sec(attempt),
        "paper": {
            "code": attempt["paper_code"], "title": attempt["title"],
            "family": attempt["family"], "module": attempt["module"],
            "question_count": attempt["question_count"],
            "duration_sec": attempt["duration_sec"],
        },
        "questions": [
            {"id": q["id"], "n": q["n"], "topic": q["topic"],
             "stem_html": q["stem_html"], "diagram_svg": q["diagram_svg"],
             "options": q["options"],
             "selected": saved.get(q["id"], {}).get("selected"),
             "flagged": bool(saved.get(q["id"], {}).get("flagged"))}
            for q in questions
        ],
    }
    return render_template("exam_player.html", payload=payload, attempt=attempt)


@exam.route("/exam/attempt/<int:attempt_id>/results")
@login_required
def results(attempt_id):
    """The results page shell. Phase 4 fills it from results.json."""
    with get_db() as db:
        attempt = _attempt_or_404(db, attempt_id)
        if _expire_if_overdue(db, attempt):
            attempt = _attempt_or_404(db, attempt_id)
        if attempt["status"] == "live":
            return redirect(url_for("exam.player", attempt_id=attempt_id))
    return render_template("exam_results.html", attempt=attempt,
                           disclaimer=ESTIMATE_DISCLAIMER)


# ---------------------------------------------------------------------------
# Buying a single paper
# ---------------------------------------------------------------------------
#
# The same shape as the mock-paper marketplace: a one-time Checkout Session,
# verified with Stripe before the sale is recorded, and ownership stored
# against the user. Nothing here trusts the redirect — a student who edits the
# success URL by hand gets nothing, exactly as on the subscription path.

@exam.route("/exam/<paper_code>/buy", methods=["POST"])
@login_required
def buy(paper_code):
    """Start a one-time Checkout for a single paper."""
    from app import STRIPE_ENABLED, stripe

    with get_db() as db:
        paper = db.execute(
            "SELECT * FROM exam_papers WHERE paper_code=? AND is_published",
            (paper_code,)).fetchone()
        if not paper:
            abort(404)
        allowed, reason = _access(db, paper)

    if allowed:
        # Already entitled — say which, because "you already have this" and
        # "this is included in your plan" are different facts to a student.
        flash("Pro includes every Exam Mode paper." if reason == "pro"
              else "You already have that paper.", "success")
        return redirect(url_for("exam.index"))

    if not STRIPE_ENABLED:
        flash("Payments aren't configured yet.", "error")
        return redirect(url_for("exam.index"))

    try:
        customer_id = current_user.stripe_customer_id
        if not customer_id:
            cust = stripe.Customer.create(email=current_user.email,
                                          metadata={"user_id": current_user.id})
            customer_id = cust.id
            with get_db() as db:
                db.execute("UPDATE users SET stripe_customer_id=? WHERE id=?",
                           (customer_id, current_user.id))
        sess = stripe.checkout.Session.create(
            mode="payment",
            customer=customer_id,
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"{paper['title']} ({paper['family']} {paper['module']})",
                        "description": f"{paper['question_count']} questions, "
                                       f"{paper['duration_sec'] // 60} minutes, "
                                       f"with full worked solutions.",
                    },
                    "unit_amount": paper["price_pence"],
                },
                "quantity": 1,
            }],
            metadata={"user_id": current_user.id, "exam_paper_id": paper["id"]},
            success_url=url_for("exam.buy_success", _external=True)
                        + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("exam.index", _external=True),
        )
        return redirect(sess.url)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("exam.index"))


@exam.route("/exam/purchase/success")
@login_required
def buy_success():
    """Verify the session with Stripe, then record the sale.

    The redirect is not evidence. Ownership is written only when Stripe itself
    says the session is complete, is paid, and belongs to this user — the same
    rule the subscription path follows, and for the same reason.
    """
    from app import STRIPE_ENABLED, stripe

    session_id = request.args.get("session_id")
    if not (STRIPE_ENABLED and session_id):
        flash("Couldn't confirm your purchase.", "error")
        return redirect(url_for("exam.index"))
    try:
        sess = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        flash("Couldn't confirm your purchase.", "error")
        return redirect(url_for("exam.index"))

    meta = sess["metadata"] or {}
    paid = sess["status"] == "complete" and sess["payment_status"] == "paid"
    mine = ("user_id" in meta) and str(meta["user_id"]) == str(current_user.id)
    pid = meta["exam_paper_id"] if "exam_paper_id" in meta else None

    if paid and mine and pid:
        with get_db() as db:
            db.execute(
                "INSERT INTO exam_purchases (user_id, paper_id, stripe_session_id) "
                "VALUES (?,?,?) ON CONFLICT (user_id, paper_id) DO NOTHING",
                (current_user.id, int(pid), session_id))
        flash("Paper unlocked — it's yours to sit whenever you like.", "success")
    else:
        flash("We couldn't verify that purchase. If you just paid, give it a "
              "moment and refresh.", "error")
    return redirect(url_for("exam.index"))


# ---------------------------------------------------------------------------
# Tracking — which admissions tests a student is preparing for
# ---------------------------------------------------------------------------
#
# Its own tab rather than a section of /subjects. A student choosing "Physics,
# whose board?" is doing a different job from one saying "I am sitting the ESAT
# in October", and one list asked them to do both at once. They also behave
# differently once chosen: an admissions test has no grade to predict, is
# scored per module, and has a date the student is counting down to.
#
# Selection is stored in user_subjects, the same table as everything else. A
# tracked test is a tracked qualification; only the picker is separate.

@exam.route("/admissions", methods=["GET", "POST"])
@login_required
def tracking():
    """Choose which admissions tests to track, and see progress on each."""
    # Imported here rather than at module level: these live in app.py, which
    # registers this blueprint, so a module-level import would be circular.
    from app import (_keep_other_kind, get_user_subjects, log_event,
                     set_user_subjects)

    if request.method == "POST":
        # Only the admissions half is rewritten; the graded subjects chosen on
        # /subjects are carried through. The same helper both graded pickers
        # use, from the other direction — one rule, stated once.
        picked = request.form.getlist("qualification")
        set_user_subjects(current_user.id,
                          picked + _keep_other_kind(current_user.id, "graded"))
        log_event("admissions_updated", current_user.id, str(len(picked)))
        flash("Tests updated." if picked else
              "No tests tracked — pick one to see it on your dashboard.",
              "success")
        return redirect(url_for("exam.tracking"))

    mine = get_user_subjects(current_user.id)
    chosen = {f"{s['board']}|{s['subject']}|{s['level']}"
              for s in mine if not is_graded(s["board"], s["subject"])}

    tests = all_qualifications("admissions")

    # What the student has actually logged against each test, so the page shows
    # progress rather than just a set of checkboxes.
    with get_db() as db:
        logged = db.execute(
            "SELECT board, subject, COUNT(*) AS papers, "
            "       SUM(score) AS marks, SUM(max_marks) AS out_of "
            "FROM papers WHERE user_id=? GROUP BY board, subject",
            (current_user.id,)).fetchall()
        attempts = db.execute(
            "SELECT p.family, COUNT(*) AS n, MAX(a.scaled) AS best "
            "FROM exam_attempts a JOIN exam_papers p ON p.id = a.paper_id "
            "WHERE a.user_id=? AND a.status <> 'live' GROUP BY p.family",
            (current_user.id,)).fetchall()

    progress = {(r["board"], r["subject"]): dict(r) for r in logged}
    mocks = {r["family"]: dict(r) for r in attempts}

    return render_template("admissions.html", tests=tests, chosen=chosen,
                           progress=progress, mocks=mocks)
