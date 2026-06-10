import os, json, secrets
from datetime import datetime, timezone
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify, session, send_from_directory, abort)
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import stripe

from paper_templates import TEMPLATES, get_paper_info, get_topics, all_combos

import json as _json

# ── Config ───────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PRICE_ID    = os.environ.get("STRIPE_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_ENABLED = bool(stripe.api_key)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXT   = {"pdf", "png", "jpg", "jpeg"}
MAX_UPLOAD_MB = 50
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "telos.db")

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."

# Jinja2 filter so templates can parse stored JSON strings
@app.template_filter("from_json")
def from_json_filter(s):
    try:
        return _json.loads(s)
    except Exception:
        return []

# ── Database ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id                  INTEGER PRIMARY KEY,
            email               TEXT UNIQUE NOT NULL,
            username            TEXT NOT NULL,
            password_hash       TEXT NOT NULL,
            subscription_status TEXT NOT NULL DEFAULT 'free',
            stripe_customer_id  TEXT,
            created_at          TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS papers (
            id            INTEGER PRIMARY KEY,
            user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject       TEXT NOT NULL,
            board         TEXT NOT NULL,
            paper_code    TEXT NOT NULL,
            year          TEXT NOT NULL,
            series        TEXT NOT NULL DEFAULT 'June',
            score         REAL,
            max_marks     REAL NOT NULL,
            date_completed TEXT,
            time_taken    INTEGER,
            weak_topics   TEXT,
            notes         TEXT,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS question_marks (
            id          INTEGER PRIMARY KEY,
            paper_id    INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
            q_num       TEXT NOT NULL,
            obtained    REAL NOT NULL,
            max_marks   REAL NOT NULL,
            topic       TEXT,
            notes       TEXT
        );

        CREATE TABLE IF NOT EXISTS grade_boundaries (
            id          INTEGER PRIMARY KEY,
            subject     TEXT NOT NULL,
            board       TEXT NOT NULL,
            paper_code  TEXT NOT NULL,
            year        TEXT NOT NULL,
            series      TEXT NOT NULL DEFAULT 'June',
            a_star      INTEGER,
            a_boundary  INTEGER,
            b_boundary  INTEGER,
            c_boundary  INTEGER,
            UNIQUE(subject, board, paper_code, year, series)
        );

        CREATE TABLE IF NOT EXISTS uploads (
            id          INTEGER PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            filename    TEXT NOT NULL,
            orig_name   TEXT NOT NULL,
            subject     TEXT,
            board       TEXT,
            paper_code  TEXT,
            year        TEXT,
            file_type   TEXT,
            upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
            file_size   INTEGER
        );

        CREATE TABLE IF NOT EXISTS question_bank (
            id          INTEGER PRIMARY KEY,
            upload_id   INTEGER NOT NULL REFERENCES uploads(id) ON DELETE CASCADE,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            q_num       TEXT NOT NULL,
            page_num    INTEGER,
            topics      TEXT,
            keywords    TEXT,
            max_marks   INTEGER,
            notes       TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

# ── Auth model ────────────────────────────────────────────────────────────────

class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.email = row["email"]
        self.username = row["username"]
        self.subscription_status = row["subscription_status"]
        self.stripe_customer_id  = row["stripe_customer_id"]

    @property
    def is_premium(self):
        return self.subscription_status == "active"


@login_manager.user_loader
def load_user(uid):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return User(row) if row else None

# ── Helpers ───────────────────────────────────────────────────────────────────

def allowed_file(fname):
    return "." in fname and fname.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def get_grade(score, max_marks, a_star=None, a=None, b=None, c=None):
    if not score or not max_marks:
        return None, None
    pct = score / max_marks * 100
    if a_star is not None and score >= a_star:
        return "A*", "#f59e0b"
    if a is not None and score >= a:
        return "A", "#22c55e"
    if b is not None and score >= b:
        return "B", "#3b82f6"
    if c is not None and score >= c:
        return "C", "#a78bfa"
    # percentage fallback
    if pct >= 90: return "A*", "#f59e0b"
    if pct >= 80: return "A",  "#22c55e"
    if pct >= 70: return "B",  "#3b82f6"
    if pct >= 60: return "C",  "#a78bfa"
    if pct >= 50: return "D",  "#f97316"
    return "E", "#ef4444"


def paper_matrix(user_id):
    """Build the full paper completion matrix per template."""
    with get_db() as db:
        done = db.execute(
            "SELECT subject, board, paper_code, year, id, score, max_marks "
            "FROM papers WHERE user_id=?", (user_id,)
        ).fetchall()
        boundaries = db.execute("SELECT * FROM grade_boundaries").fetchall()

    done_map = {}
    for p in done:
        key = (p["subject"], p["board"], p["paper_code"], p["year"])
        done_map[key] = {"id": p["id"], "score": p["score"], "max_marks": p["max_marks"]}

    bnd_map = {}
    for b in boundaries:
        key = (b["subject"], b["board"], b["paper_code"], b["year"])
        bnd_map[key] = b

    matrix = []
    for board, subjects in TEMPLATES.items():
        for subject, data in subjects.items():
            rows = []
            for paper in data["papers"]:
                cells = []
                for yr in data["years"]:
                    key   = (subject, board, paper["code"], yr)
                    bnd   = bnd_map.get(key)
                    entry = done_map.get(key)
                    if entry and entry["score"] is not None:
                        grade, color = get_grade(
                            entry["score"], entry["max_marks"],
                            bnd["a_star"]     if bnd else None,
                            bnd["a_boundary"] if bnd else None,
                            bnd["b_boundary"] if bnd else None,
                            bnd["c_boundary"] if bnd else None,
                        )
                        pct = round(entry["score"] / entry["max_marks"] * 100, 1)
                        cells.append({"year": yr, "done": True, "pct": pct,
                                      "grade": grade, "color": color, "id": entry["id"]})
                    elif entry:
                        cells.append({"year": yr, "done": True, "pct": None,
                                      "grade": None, "color": None, "id": entry["id"]})
                    else:
                        cells.append({"year": yr, "done": False})
                rows.append({"paper": paper, "cells": cells})
            matrix.append({
                "board": board, "subject": subject,
                "color": data["color"], "years": data["years"],
                "rows": rows,
            })
    return matrix

# ── Auth routes ───────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        pw    = request.form["password"]
        with get_db() as db:
            row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if row and check_password_hash(row["password_hash"], pw):
            login_user(User(row), remember=True)
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Incorrect email or password.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        username = request.form["username"].strip()
        pw       = request.form["password"]
        if len(pw) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("register.html")
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (email, username, password_hash) VALUES (?,?,?)",
                    (email, username, generate_password_hash(pw))
                )
            flash("Account created — log in to get started.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.", "error")
    return render_template("register.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def dashboard():
    with get_db() as db:
        recent = db.execute(
            "SELECT * FROM papers WHERE user_id=? ORDER BY created_at DESC LIMIT 8",
            (current_user.id,)
        ).fetchall()
        counts = db.execute(
            "SELECT subject, board, COUNT(*) as n, AVG(score/max_marks*100) as avg_pct "
            "FROM papers WHERE user_id=? AND score IS NOT NULL GROUP BY subject, board",
            (current_user.id,)
        ).fetchall()
        total = db.execute(
            "SELECT COUNT(*) as n FROM papers WHERE user_id=?",
            (current_user.id,)
        ).fetchone()["n"]
        boundaries = {
            (b["subject"], b["board"], b["paper_code"], b["year"]): b
            for b in db.execute("SELECT * FROM grade_boundaries").fetchall()
        }

    stats = {}
    for row in counts:
        key = (row["subject"], row["board"])
        stats[key] = {"n": row["n"], "avg": round(row["avg_pct"] or 0, 1)}

    recent_enriched = []
    for p in recent:
        bnd = boundaries.get((p["subject"], p["board"], p["paper_code"], p["year"]))
        grade, color = get_grade(
            p["score"], p["max_marks"],
            bnd["a_star"] if bnd else None,
            bnd["a_boundary"] if bnd else None,
            bnd["b_boundary"] if bnd else None,
            bnd["c_boundary"] if bnd else None,
        ) if p["score"] else (None, None)
        pct = round(p["score"] / p["max_marks"] * 100, 1) if p["score"] else None
        recent_enriched.append({**dict(p), "grade": grade, "grade_color": color, "pct": pct})

    return render_template("dashboard.html", recent=recent_enriched,
                           stats=stats, total=total, templates=TEMPLATES)

# ── Papers matrix ─────────────────────────────────────────────────────────────

@app.route("/papers")
@login_required
def papers():
    matrix = paper_matrix(current_user.id)
    return render_template("papers_list.html", matrix=matrix)

# ── Add / edit paper ──────────────────────────────────────────────────────────

@app.route("/papers/add", methods=["GET", "POST"])
@login_required
def add_paper():
    # Pre-fill from query params (coming from matrix click)
    pre = {
        "board":      request.args.get("board", ""),
        "subject":    request.args.get("subject", ""),
        "paper_code": request.args.get("paper_code", ""),
        "year":       request.args.get("year", ""),
    }
    if pre["board"] and pre["subject"] and pre["paper_code"]:
        info = get_paper_info(pre["board"], pre["subject"], pre["paper_code"])
        if info:
            pre["max_marks"] = info["max_marks"]
            pre["topics"] = get_topics(pre["board"], pre["subject"], pre["paper_code"])
    else:
        pre["topics"] = []
        pre["max_marks"] = ""

    if request.method == "POST":
        board      = request.form["board"]
        subject    = request.form["subject"]
        paper_code = request.form["paper_code"]
        year       = request.form["year"]
        series     = request.form.get("series", "June")
        max_marks  = float(request.form["max_marks"])
        date_done  = request.form.get("date_completed") or datetime.now().strftime("%Y-%m-%d")
        time_taken = request.form.get("time_taken") or None
        weak       = request.form.get("weak_topics", "").strip()
        notes      = request.form.get("notes", "").strip()

        # Parse per-question marks
        q_nums  = request.form.getlist("q_num[]")
        q_got   = request.form.getlist("q_obtained[]")
        q_max   = request.form.getlist("q_max[]")
        q_topic = request.form.getlist("q_topic[]")

        score = None
        qmarks = []
        if q_nums and any(v.strip() for v in q_got):
            total = 0.0
            for qn, got, mx, tp in zip(q_nums, q_got, q_max, q_topic):
                try:
                    if got.strip():
                        g = float(got); m = float(mx) if mx.strip() else 0.0
                        total += g
                        qmarks.append((qn, g, m, tp))
                except ValueError:
                    pass
            score = total if qmarks else None
        else:
            raw = request.form.get("score_direct", "").strip()
            try:
                score = float(raw) if raw else None
            except ValueError:
                score = None

        with get_db() as db:
            cur = db.execute(
                """INSERT INTO papers
                   (user_id, subject, board, paper_code, year, series, score, max_marks,
                    date_completed, time_taken, weak_topics, notes)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (current_user.id, subject, board, paper_code, year, series,
                 score, max_marks, date_done,
                 int(time_taken) if time_taken else None, weak, notes)
            )
            paper_id = cur.lastrowid
            for qn, got, mx, tp in qmarks:
                db.execute(
                    "INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
                    "VALUES (?,?,?,?,?)",
                    (paper_id, qn, got, mx, tp or None)
                )

        flash("Paper logged.", "success")
        return redirect(url_for("papers"))

    return render_template("papers_entry.html", pre=pre, templates=TEMPLATES,
                           mode="add")


@app.route("/papers/<int:pid>/edit", methods=["GET", "POST"])
@login_required
def edit_paper(pid):
    with get_db() as db:
        paper = db.execute(
            "SELECT * FROM papers WHERE id=? AND user_id=?",
            (pid, current_user.id)
        ).fetchone()
        if not paper:
            abort(404)
        qmarks = db.execute(
            "SELECT * FROM question_marks WHERE paper_id=? ORDER BY id",
            (pid,)
        ).fetchall()

    if request.method == "POST":
        subject    = request.form["subject"]
        board      = request.form["board"]
        paper_code = request.form["paper_code"]
        year       = request.form["year"]
        series     = request.form.get("series", "June")
        max_marks  = float(request.form["max_marks"])
        date_done  = request.form.get("date_completed") or paper["date_completed"]
        time_taken = request.form.get("time_taken") or None
        weak       = request.form.get("weak_topics", "").strip()
        notes      = request.form.get("notes", "").strip()

        q_nums  = request.form.getlist("q_num[]")
        q_got   = request.form.getlist("q_obtained[]")
        q_max   = request.form.getlist("q_max[]")
        q_topic = request.form.getlist("q_topic[]")

        score  = None
        new_qm = []
        if q_nums and any(v.strip() for v in q_got):
            total = 0.0
            for qn, got, mx, tp in zip(q_nums, q_got, q_max, q_topic):
                try:
                    if got.strip():
                        g = float(got); m = float(mx) if mx.strip() else 0.0
                        total += g
                        new_qm.append((qn, g, m, tp))
                except ValueError:
                    pass
            score = total if new_qm else paper["score"]
        else:
            raw = request.form.get("score_direct", "").strip()
            try:
                score = float(raw) if raw else paper["score"]
            except ValueError:
                score = paper["score"]

        with get_db() as db:
            db.execute(
                """UPDATE papers SET subject=?,board=?,paper_code=?,year=?,series=?,
                   score=?,max_marks=?,date_completed=?,time_taken=?,weak_topics=?,notes=?
                   WHERE id=?""",
                (subject, board, paper_code, year, series, score, max_marks,
                 date_done, int(time_taken) if time_taken else None, weak, notes, pid)
            )
            db.execute("DELETE FROM question_marks WHERE paper_id=?", (pid,))
            for qn, got, mx, tp in new_qm:
                db.execute(
                    "INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
                    "VALUES (?,?,?,?,?)",
                    (pid, qn, got, mx, tp or None)
                )

        flash("Paper updated.", "success")
        return redirect(url_for("papers"))

    info = get_paper_info(paper["board"], paper["subject"], paper["paper_code"])
    pre = dict(paper)
    pre["topics"] = get_topics(paper["board"], paper["subject"], paper["paper_code"])
    pre["max_marks"] = paper["max_marks"]
    return render_template("papers_entry.html", pre=pre, paper=paper,
                           qmarks=qmarks, templates=TEMPLATES, mode="edit", pid=pid)


@app.route("/papers/<int:pid>/delete", methods=["POST"])
@login_required
def delete_paper(pid):
    with get_db() as db:
        db.execute("DELETE FROM papers WHERE id=? AND user_id=?",
                   (pid, current_user.id))
    flash("Paper deleted.", "success")
    return redirect(url_for("papers"))

# ── Heatmap ───────────────────────────────────────────────────────────────────

@app.route("/heatmap")
@login_required
def heatmap():
    subject_filter = request.args.get("subject", "")
    board_filter   = request.args.get("board", "")
    code_filter    = request.args.get("code", "")

    with get_db() as db:
        papers_raw = db.execute(
            "SELECT p.*, GROUP_CONCAT(q.q_num||':'||q.obtained||'/'||q.max_marks, '|') as qdata "
            "FROM papers p LEFT JOIN question_marks q ON q.paper_id=p.id "
            "WHERE p.user_id=? GROUP BY p.id ORDER BY p.year, p.series, p.paper_code",
            (current_user.id,)
        ).fetchall()

    # Build heatmap data per (board, subject, paper_code)
    heatmap_data = {}
    max_q = {}

    for p in papers_raw:
        if subject_filter and p["subject"] != subject_filter:
            continue
        if board_filter and p["board"] != board_filter:
            continue
        if code_filter and p["paper_code"] != code_filter:
            continue

        key = (p["board"], p["subject"], p["paper_code"])
        if key not in heatmap_data:
            heatmap_data[key] = []
            max_q[key] = 0

        qmap = {}
        if p["qdata"]:
            for item in p["qdata"].split("|"):
                parts = item.split(":")
                if len(parts) == 2:
                    qn, vals = parts
                    got, mx = vals.split("/")
                    try:
                        qmap[qn] = {"obtained": float(got), "max": float(mx),
                                    "pct": round(float(got)/float(mx)*100, 1) if float(mx) else 0}
                    except (ValueError, ZeroDivisionError):
                        pass

        q_count = len(qmap)
        if q_count > max_q[key]:
            max_q[key] = q_count

        heatmap_data[key].append({
            "label": f"{p['year']} {p['paper_code']}",
            "year":  p["year"],
            "score": p["score"],
            "max":   p["max_marks"],
            "pct":   round(p["score"]/p["max_marks"]*100, 1) if p["score"] and p["max_marks"] else None,
            "qmap":  qmap,
        })

    # Build Q-number lists
    sections = []
    for key, rows in heatmap_data.items():
        board, subject, code = key
        all_nums = set()
        for r in rows:
            all_nums.update(r["qmap"].keys())
        def sort_key(x):
            try:    return (0, int(x))
            except: return (1, x)
        q_nums = sorted(all_nums, key=sort_key)
        sections.append({
            "board": board, "subject": subject, "code": code,
            "color": TEMPLATES[board][subject]["color"],
            "q_nums": q_nums, "rows": rows,
        })

    # Dropdowns
    all_subjects = [(board, subj) for board, s in TEMPLATES.items() for subj in s]
    all_codes = []
    if subject_filter and board_filter:
        try:
            all_codes = [p["code"] for p in TEMPLATES[board_filter][subject_filter]["papers"]]
        except KeyError:
            pass

    return render_template("heatmap.html", sections=sections,
                           subject_filter=subject_filter, board_filter=board_filter,
                           code_filter=code_filter,
                           all_subjects=all_subjects, all_codes=all_codes,
                           templates=TEMPLATES)

# ── Question Bank ─────────────────────────────────────────────────────────────

@app.route("/bank")
@login_required
def bank():
    topic_filter = request.args.get("topic", "")
    subj_filter  = request.args.get("subject", "")
    with get_db() as db:
        uploads = db.execute(
            "SELECT u.*, COUNT(q.id) as q_count "
            "FROM uploads u LEFT JOIN question_bank q ON q.upload_id=u.id "
            "WHERE u.user_id=? GROUP BY u.id ORDER BY u.upload_date DESC",
            (current_user.id,)
        ).fetchall()
        questions = db.execute(
            "SELECT q.*, u.orig_name, u.subject, u.board, u.paper_code, u.year "
            "FROM question_bank q JOIN uploads u ON q.upload_id=u.id "
            "WHERE q.user_id=?",
            (current_user.id,)
        ).fetchall()

    all_topics = set()
    for q in questions:
        if q["topics"]:
            for t in json.loads(q["topics"]):
                all_topics.add(t)

    if topic_filter:
        questions = [q for q in questions
                     if q["topics"] and topic_filter in json.loads(q["topics"])]
    if subj_filter:
        questions = [q for q in questions if q["subject"] == subj_filter]

    return render_template("bank_index.html", uploads=uploads, questions=questions,
                           all_topics=sorted(all_topics),
                           topic_filter=topic_filter, subj_filter=subj_filter,
                           templates=TEMPLATES)


@app.route("/bank/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not f.filename:
            flash("No file selected.", "error")
            return redirect(request.url)
        if not allowed_file(f.filename):
            flash("Only PDF, PNG, JPG files allowed.", "error")
            return redirect(request.url)

        safe   = secure_filename(f.filename)
        uid    = secrets.token_hex(8)
        stored = f"{uid}_{safe}"
        path   = os.path.join(UPLOAD_FOLDER, stored)
        f.save(path)
        size   = os.path.getsize(path)

        with get_db() as db:
            cur = db.execute(
                """INSERT INTO uploads
                   (user_id, filename, orig_name, subject, board, paper_code, year, file_type, file_size)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (current_user.id, stored, f.filename,
                 request.form.get("subject"), request.form.get("board"),
                 request.form.get("paper_code"), request.form.get("year"),
                 request.form.get("file_type", "question_paper"), size)
            )
            upload_id = cur.lastrowid

        flash("File uploaded. Now tag the questions.", "success")
        return redirect(url_for("tag_upload", uid=upload_id))

    return render_template("bank_upload.html", templates=TEMPLATES)


@app.route("/bank/<int:uid>/tag", methods=["GET", "POST"])
@login_required
def tag_upload(uid):
    with get_db() as db:
        upload = db.execute(
            "SELECT * FROM uploads WHERE id=? AND user_id=?",
            (uid, current_user.id)
        ).fetchone()
        if not upload:
            abort(404)
        existing = db.execute(
            "SELECT * FROM question_bank WHERE upload_id=? ORDER BY id",
            (uid,)
        ).fetchall()

    if request.method == "POST":
        q_nums   = request.form.getlist("q_num[]")
        pages    = request.form.getlist("page_num[]")
        topics_l = request.form.getlist("topics[]")
        keywords = request.form.getlist("keywords[]")
        maxmarks = request.form.getlist("max_marks[]")
        notes    = request.form.getlist("notes[]")

        with get_db() as db:
            db.execute("DELETE FROM question_bank WHERE upload_id=?", (uid,))
            for qn, pg, tp, kw, mx, nt in zip(q_nums, pages, topics_l, keywords, maxmarks, notes):
                if qn.strip():
                    topics_json = json.dumps([t.strip() for t in tp.split(",") if t.strip()])
                    db.execute(
                        """INSERT INTO question_bank
                           (upload_id, user_id, q_num, page_num, topics, keywords, max_marks, notes)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (uid, current_user.id, qn.strip(),
                         int(pg) if pg.strip() else None,
                         topics_json, kw.strip(),
                         int(mx) if mx.strip() else None, nt.strip() or None)
                    )
        flash("Questions saved.", "success")
        return redirect(url_for("bank"))

    topics = get_topics(upload["board"] or "", upload["subject"] or "", upload["paper_code"] or "")
    return render_template("bank_tag.html", upload=upload, existing=existing,
                           topics=topics, templates=TEMPLATES)


@app.route("/bank/question/<int:qid>/delete", methods=["POST"])
@login_required
def delete_question(qid):
    with get_db() as db:
        db.execute("DELETE FROM question_bank WHERE id=? AND user_id=?",
                   (qid, current_user.id))
    flash("Question removed.", "success")
    return redirect(url_for("bank"))


@app.route("/uploads/<path:filename>")
@login_required
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ── Stats ─────────────────────────────────────────────────────────────────────

@app.route("/stats")
@login_required
def stats():
    with get_db() as db:
        papers = db.execute(
            "SELECT * FROM papers WHERE user_id=? AND score IS NOT NULL "
            "ORDER BY date_completed",
            (current_user.id,)
        ).fetchall()
        boundaries = {
            (b["subject"], b["board"], b["paper_code"], b["year"]): b
            for b in db.execute("SELECT * FROM grade_boundaries").fetchall()
        }

    by_subject = {}
    for p in papers:
        key = (p["subject"], p["board"])
        if key not in by_subject:
            by_subject[key] = []
        bnd = boundaries.get((p["subject"], p["board"], p["paper_code"], p["year"]))
        pct = round(p["score"] / p["max_marks"] * 100, 1)
        grade, color = get_grade(
            p["score"], p["max_marks"],
            bnd["a_star"] if bnd else None,
            bnd["a_boundary"] if bnd else None,
            bnd["b_boundary"] if bnd else None,
            bnd["c_boundary"] if bnd else None,
        )
        by_subject[key].append({**dict(p), "pct": pct, "grade": grade, "grade_color": color})

    # Per-code averages
    code_stats = {}
    with get_db() as db:
        rows = db.execute(
            "SELECT paper_code, board, subject, AVG(score/max_marks*100) as avg_pct, COUNT(*) as n "
            "FROM papers WHERE user_id=? AND score IS NOT NULL GROUP BY paper_code, board, subject",
            (current_user.id,)
        ).fetchall()
    for r in rows:
        code_stats[(r["subject"], r["board"], r["paper_code"])] = {
            "avg": round(r["avg_pct"], 1), "n": r["n"]
        }

    return render_template("stats.html", by_subject=by_subject,
                           code_stats=code_stats, templates=TEMPLATES)

# ── Grade Boundaries import ───────────────────────────────────────────────────

@app.route("/admin/boundaries", methods=["GET", "POST"])
@login_required
def boundaries():
    if request.method == "POST":
        try:
            data = json.loads(request.form["json_data"])
            with get_db() as db:
                for row in data:
                    db.execute(
                        """INSERT OR REPLACE INTO grade_boundaries
                           (subject, board, paper_code, year, series,
                            a_star, a_boundary, b_boundary, c_boundary)
                           VALUES (?,?,?,?,?,?,?,?,?)""",
                        (row["subject"], row["board"], row["paper_code"],
                         row["year"], row.get("series", "June"),
                         row.get("a_star"), row.get("a"), row.get("b"), row.get("c"))
                    )
            flash(f"Imported {len(data)} boundary records.", "success")
        except Exception as e:
            flash(f"Import error: {e}", "error")

    with get_db() as db:
        all_bounds = db.execute("SELECT * FROM grade_boundaries ORDER BY subject, year").fetchall()
    return render_template("boundaries.html", boundaries=all_bounds)

# ── Subscription ──────────────────────────────────────────────────────────────

@app.route("/subscription")
@login_required
def subscription():
    return render_template("subscription.html",
                           stripe_enabled=STRIPE_ENABLED,
                           stripe_pk=os.environ.get("STRIPE_PUBLISHABLE_KEY", ""))


@app.route("/subscription/checkout", methods=["POST"])
@login_required
def create_checkout():
    if not STRIPE_ENABLED:
        flash("Stripe not configured.", "error")
        return redirect(url_for("subscription"))
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
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
            mode="subscription",
            success_url=url_for("sub_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("subscription", _external=True),
        )
        return redirect(sess.url)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("subscription"))


@app.route("/subscription/success")
@login_required
def sub_success():
    with get_db() as db:
        db.execute("UPDATE users SET subscription_status='active' WHERE id=?",
                   (current_user.id,))
    flash("You're now a Telos Pro member!", "success")
    return redirect(url_for("dashboard"))


@app.route("/subscription/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig     = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception:
        return "", 400

    obj = event["data"]["object"]
    if event["type"] in ("customer.subscription.deleted", "customer.subscription.paused"):
        with get_db() as db:
            db.execute(
                "UPDATE users SET subscription_status='free' WHERE stripe_customer_id=?",
                (obj.get("customer"),)
            )
    elif event["type"] == "customer.subscription.updated":
        status = "active" if obj.get("status") == "active" else "free"
        with get_db() as db:
            db.execute(
                "UPDATE users SET subscription_status=? WHERE stripe_customer_id=?",
                (status, obj.get("customer"))
            )
    return "", 200

# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/templates")
@login_required
def api_templates():
    return jsonify(all_combos())


@app.route("/api/template-info")
@login_required
def api_template_info():
    board   = request.args.get("board")
    subject = request.args.get("subject")
    code    = request.args.get("code")
    info    = get_paper_info(board, subject, code)
    topics  = get_topics(board, subject, code)
    return jsonify({"info": dict(info) if info else None, "topics": topics})

# ── Boot ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print(" * Telos running on http://127.0.0.1:5000")
    app.run(debug=True)
