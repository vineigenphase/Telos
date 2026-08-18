import os, json, secrets, hashlib
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify, session, send_from_directory, abort)
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import urlunsplit
import psycopg
import stripe

from paper_templates import TEMPLATES, get_paper_info, get_topics, all_combos
from seed_boundaries import seed_boundaries
from mailer import send_email, MAIL_ENABLED
from prediction import predict as predict_grade
from auth import requires_pro, user_is_pro

import json as _json

# ── Config ───────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# ── Canonical host & HTTPS ───────────────────────────────────────────────────
# Railway terminates TLS at its edge and forwards plain HTTP, so without
# ProxyFix every _external url_for() (Stripe success/cancel URLs included)
# comes out as http:// and request.scheme lies about the real connection.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Unset locally -> canonical redirect and secure cookies are both off, so
# http://127.0.0.1:5000 still works. Set on Railway to "telosapp.co.uk".
CANONICAL_HOST = os.environ.get("CANONICAL_HOST", "").strip()

app.config.update(
    PREFERRED_URL_SCHEME="https",
    SESSION_COOKIE_SECURE=bool(CANONICAL_HOST),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_ENABLED = bool(stripe.api_key)

# Legacy £2/month. Kept active forever for the handful of people already on it —
# nobody is migrated or cancelled. STRIPE_PRICE_ID is the old variable name.
STRIPE_PRICE_LEGACY  = os.environ.get("STRIPE_PRICE_LEGACY") or os.environ.get("STRIPE_PRICE_ID", "")
STRIPE_PRICE_MONTHLY = os.environ.get("STRIPE_PRICE_MONTHLY", "")
STRIPE_PRICE_ANNUAL  = os.environ.get("STRIPE_PRICE_ANNUAL", "")

# ── Pricing ───────────────────────────────────────────────────────────────────
# One source of truth. Templates read from here — never hardcode a price in a
# template, or the day you change it you'll miss one.
#
# Why £29 annual is pushed: A-level revision collapses in June when Year 13
# finish, so monthly billing gets ~7 payments then permanent churn. Annual
# captures the whole cycle up front. And the 20p fixed Stripe fee is why £2
# never worked — it ate ~14% of every payment; at £29/year you keep ~98%.
PRICING = {
    "month": {
        "key": "month",
        "price_id": STRIPE_PRICE_MONTHLY,
        "amount_pence": 499,
        "label": "£4.99",
        "period": "per month",
        "sub": "Billed monthly. Cancel any time.",
    },
    "year": {
        "key": "year",
        "price_id": STRIPE_PRICE_ANNUAL,
        "amount_pence": 2900,
        "label": "£29",
        "period": "per year",
        "sub": "That's £2.42/month — save £31 vs monthly.",
        "recommended": True,
    },
    "legacy": {
        "key": "legacy",
        "price_id": STRIPE_PRICE_LEGACY,
        "amount_pence": 200,
        "label": "£2",
        "period": "per month",
        "sub": "Legacy price — kept for existing subscribers.",
        "hidden": True,
    },
}
DEFAULT_INTERVAL = "year"     # annual is preselected on purpose

STORAGE_DIR   = os.environ.get("STORAGE_DIR", os.path.join(os.path.dirname(__file__), "storage"))
UPLOAD_FOLDER = os.path.join(STORAGE_DIR, "uploads")   # question-bank files
MOCK_FOLDER   = os.path.join(STORAGE_DIR, "mocks")     # purchasable mock papers
ALLOWED_EXT   = {"pdf", "png", "jpg", "jpeg"}
MAX_UPLOAD_MB = 50
FREE_UPLOAD_LIMIT = 10   # free plan upload cap; Pro is unlimited
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MOCK_FOLDER, exist_ok=True)

# ── Pricing table (data-driven; later phases flip coming_soon -> live) ─────────
# NB: prices themselves are handled in Phase 5. This only drives the feature
# columns so no feature ever appears in both Free and Pro.
PRICING_FEATURES = {
    "free": [
        {"label": "Paper tracking (unlimited)"},
        {"label": "Per-question mark entry"},
        {"label": "Basic heatmap"},
        {"label": "File uploads (10 max)"},
    ],
    "pro": [
        {"label": "Everything in Free"},
        {"label": "Predicted grade + marks to next boundary", "coming_soon": True},
        {"label": "Your next 3 questions", "coming_soon": True},
        {"label": "Spaced repetition queue", "coming_soon": True},
        {"label": "Full stats & topic analytics", "coming_soon": True},
        {"label": "Pro Zone — resources, golden tips, monthly notes"},
        {"label": "Original mock papers"},
        {"label": "Weekly parent report", "coming_soon": True},
        {"label": "Unlimited file uploads"},
        {"label": "Pro badge"},
    ],
}

# ── Navigation ───────────────────────────────────────────────────────────────
# One structure drives BOTH layouts — the phone's bottom tab bar (primary
# items) and the sidebar (everything) — so the two can't drift apart.
#   primary : shows in the mobile tab bar. Exactly 4, because the 5th slot is
#             the "More" sheet holding the rest.
#   match   : endpoints that light this item up as active.
NAV_ITEMS = [
    {"endpoint": "dashboard",     "label": "Dashboard",      "short": "Today",
     "icon": "grid",     "primary": True,  "section": "Main",
     "match": ("dashboard",)},
    {"endpoint": "papers",        "label": "Papers",         "short": "Papers",
     "icon": "book",     "primary": True,  "section": "Main",
     "match": ("papers", "add_paper", "edit_paper", "enter_marks")},
    {"endpoint": "heatmap",       "label": "Heatmap",        "short": "Heatmap",
     "icon": "cells",    "primary": True,  "section": "Main",
     "match": ("heatmap",)},
    {"endpoint": "revise",        "label": "Revise",         "short": "Revise",
     "icon": "repeat",   "primary": True,  "section": "Main",
     "match": ("revise",)},
    {"endpoint": "bank",          "label": "Question Bank",  "short": "Bank",
     "icon": "database", "primary": False, "section": "Main",
     "match": ("bank", "upload_file", "tag_upload")},
    {"endpoint": "stats",         "label": "Stats",          "short": "Stats",
     "icon": "bars",     "primary": False, "section": "Main",
     "match": ("stats",)},
    {"endpoint": "pro_zone",      "label": "Pro Zone",       "short": "Pro",
     "icon": "star",     "primary": False, "section": "Main",
     "match": ("pro_zone",)},
    {"endpoint": "mocks",         "label": "Mock Papers",    "short": "Mocks",
     "icon": "file",     "primary": False, "section": "Main",
     "match": ("mocks",)},
    {"endpoint": "subscription",  "label": "Subscription",   "short": "Plan",
     "icon": "card",     "primary": False, "section": "Account",
     "match": ("subscription",)},
    {"endpoint": "admin_content", "label": "Manage Content", "short": "Content",
     "icon": "pencil",   "primary": False, "section": "Account", "admin": True,
     "match": ("admin_content",)},
    {"endpoint": "admin_mocks",   "label": "Manage Mocks",   "short": "Mocks",
     "icon": "tag",      "primary": False, "section": "Account", "admin": True,
     "match": ("admin_mocks",)},
    {"endpoint": "boundaries",    "label": "Boundaries",     "short": "Bounds",
     "icon": "pulse",    "primary": False, "section": "Account", "admin": True,
     "match": ("boundaries",)},
]

app.jinja_env.globals["NAV_ITEMS"] = NAV_ITEMS

DB_PATH = os.path.join(os.path.dirname(__file__), "telos.db")


@app.context_processor
def nav_context():
    """Admin-filtered nav for both layouts, plus the Pro flag the templates use.

    `is_pro_user` deliberately reads current_user.is_premium rather than the
    Phase 2 `is_pro` Jinja global — Phase 2 is parked on its own branch, and
    the nav must not depend on it to render.
    """
    if not current_user.is_authenticated:
        return {"nav_visible": [], "is_pro_user": False}
    is_admin = bool(getattr(current_user, "is_admin", False))
    return {
        "nav_visible": [i for i in NAV_ITEMS if not i.get("admin") or is_admin],
        "is_pro_user": bool(getattr(current_user, "is_premium", False)),
    }

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."


def canonical_url(path=None):
    """Absolute URL for `path` (default: the current request) on the canonical
    host. Falls back to the request's own host when CANONICAL_HOST is unset."""
    path = path if path is not None else request.path
    if not CANONICAL_HOST:
        return request.url_root.rstrip("/") + path
    return urlunsplit(("https", CANONICAL_HOST, path, "", ""))


app.jinja_env.globals["canonical_url"] = canonical_url


@app.before_request
def _force_canonical_host():
    """301 to one hostname over https — www and the old *.up.railway.app host
    both fold into CANONICAL_HOST. Two hostnames serving the same content
    splits SEO and breaks the PWA scope in Phase 2.5.

    Only GET/HEAD are redirected: a 301 on POST makes clients drop the body and
    re-issue as GET, which would silently break the Stripe webhook if its
    endpoint URL is ever stale. Those are answered on whatever host they hit.
    """
    if not CANONICAL_HOST or app.debug:
        return
    if request.method not in ("GET", "HEAD"):
        return
    if request.host.split(":")[0] == CANONICAL_HOST and request.scheme == "https":
        return
    return redirect(
        urlunsplit(("https", CANONICAL_HOST, request.path,
                    request.query_string.decode(), "")),
        301,
    )


@app.route("/robots.txt")
def robots_txt():
    body = "\n".join([
        "User-agent: *",
        "Disallow: /admin",
        "Disallow: /subscription/success",
        "Disallow: /subscription/webhook",
        "Disallow: /mocks/success",
        "Disallow: /papers",
        "Disallow: /heatmap",
        "Disallow: /stats",
        "Disallow: /bank",
        "",
        f"Sitemap: {canonical_url('/sitemap.xml')}",
        "",
    ])
    return app.response_class(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    # Public pages only — everything else is behind @login_required, so listing
    # it would just feed crawlers a wall of redirects.
    pages = ["/", "/login", "/register", "/subscription"]
    urls = "".join(f"<url><loc>{canonical_url(p)}</loc></url>" for p in pages)
    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{urls}</urlset>")
    return app.response_class(body, mimetype="application/xml")

# Jinja2 filter so templates can parse stored JSON strings
@app.template_filter("from_json")
def from_json_filter(s):
    try:
        return _json.loads(s)
    except Exception:
        return []

# ── Database ──────────────────────────────────────────────────────────────────

from db import get_db


def init_db():
    # Schema is owned by migrate_to_postgres.py; init_db only seeds the
    # permanent grade-boundary reference data (idempotent, never overwrites).
    with get_db() as db:
        seed_boundaries(db)

# ── Auth model ────────────────────────────────────────────────────────────────

class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.email = row["email"]
        self.username = row["username"]
        self.subscription_status = row["subscription_status"]
        self.stripe_customer_id  = row["stripe_customer_id"]
        self.is_admin = bool(row["is_admin"])
        self.plan = row["plan"]
        self.plan_interval = row["plan_interval"]
        self.grandfathered = bool(row["grandfathered"])
        self.current_period_end = row["current_period_end"]

    @property
    def is_premium(self):
        return user_is_pro(self)


@login_manager.user_loader
def load_user(uid):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return User(row) if row else None


@app.context_processor
def inject_globals():
    """Expose is_pro to every template so they can render locked states."""
    return {"is_pro": user_is_pro(current_user)}


# ── Access control ────────────────────────────────────────────────────────────
# requires_pro + user_is_pro now live in auth.py (single source of truth).

def requires_admin(view):
    """Gate a route behind the admin flag (content management)."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            abort(403)
        return view(*args, **kwargs)
    return wrapped


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
        except psycopg.errors.UniqueViolation:
            flash("That email is already registered.", "error")
    return render_template("register.html")


# ── Password reset ────────────────────────────────────────────────────────────

RESET_TTL_MINUTES = 60


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _issue_reset(db, user_id, ip=None):
    """Create a single-use reset token. Returns the RAW token (emailed once)."""
    raw = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(minutes=RESET_TTL_MINUTES)
    # Any earlier unused link becomes dead the moment a new one is asked for.
    db.execute("UPDATE password_resets SET used_at=NOW() "
               "WHERE user_id=? AND used_at IS NULL", (user_id,))
    db.execute("INSERT INTO password_resets (user_id, token_hash, expires_at, requested_ip) "
               "VALUES (?,?,?,?)", (user_id, _hash_token(raw), expires, ip))
    return raw


@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        with get_db() as db:
            row = db.execute("SELECT id, email, username FROM users WHERE email=?",
                             (email,)).fetchone()
            if row:
                raw = _issue_reset(db, row["id"], request.remote_addr)
                link = canonical_url(url_for("reset_password", token=raw))
                send_email(
                    row["email"],
                    "Reset your Telos password",
                    f"Hi {row['username']},\n\n"
                    f"Use this link to set a new password. It works once and "
                    f"expires in {RESET_TTL_MINUTES} minutes:\n\n{link}\n\n"
                    "If you didn't ask for this, you can ignore this email — "
                    "your password hasn't changed.\n",
                )
        # Deliberately identical whether or not the account exists, and whether
        # or not mail is configured. Anything else turns this into a way to
        # test which emails have Telos accounts.
        flash("If that email has an account, a reset link is on its way.", "success")
        return redirect(url_for("login"))

    return render_template("forgot.html")


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    with get_db() as db:
        row = db.execute(
            "SELECT pr.id, pr.user_id FROM password_resets pr "
            "WHERE pr.token_hash=? AND pr.used_at IS NULL AND pr.expires_at > NOW()",
            (_hash_token(token),)
        ).fetchone()

    if not row:
        flash("That reset link has expired or already been used.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        pw = request.form.get("password", "")
        if len(pw) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("reset.html", token=token)
        if pw != request.form.get("confirm", ""):
            flash("Those passwords don't match.", "error")
            return render_template("reset.html", token=token)

        with get_db() as db:
            # Re-check inside the write: the link may have been used since the
            # page was rendered.
            still = db.execute(
                "SELECT id FROM password_resets WHERE id=? AND used_at IS NULL "
                "AND expires_at > NOW()", (row["id"],)
            ).fetchone()
            if not still:
                flash("That reset link has expired or already been used.", "error")
                return redirect(url_for("forgot_password"))
            db.execute("UPDATE users SET password_hash=? WHERE id=?",
                       (generate_password_hash(pw), row["user_id"]))
            db.execute("UPDATE password_resets SET used_at=NOW() WHERE id=?", (row["id"],))

        flash("Password updated — you can log in now.", "success")
        return redirect(url_for("login"))

    return render_template("reset.html", token=token)


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

    # Read from the cache — predictions are recomputed on write, never here.
    predictions = get_predictions(current_user.id) if user_is_pro(current_user) else []

    return render_template("dashboard.html", recent=recent_enriched,
                           stats=stats, total=total, templates=TEMPLATES,
                           predictions=predictions, papers_logged=total)

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

        recompute_predictions(current_user.id)
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

        recompute_predictions(current_user.id)
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
    recompute_predictions(current_user.id)
    flash("Paper deleted.", "success")
    return redirect(url_for("papers"))

# ── Heatmap ───────────────────────────────────────────────────────────────────

# ── Analytics ─────────────────────────────────────────────────────────────────

def log_event(event, user_id=None, detail=None):
    """Server-side only, no third-party tracker.

    Never allowed to break a request: if the insert fails, the user's checkout
    still goes through and we lose one analytics row.
    """
    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO analytics_events (event, user_id, detail) VALUES (?,?,?)",
                (event, user_id, detail)
            )
    except Exception:
        app.logger.warning("analytics insert failed for %s", event, exc_info=True)


# ── Predicted grade ───────────────────────────────────────────────────────────

def recompute_predictions(user_id):
    """Recompute and cache this user's predictions. Called on every change to
    their papers or question marks — never on page load, so the dashboard costs
    a fixed number of queries no matter how many papers exist."""
    with get_db() as db:
        papers = db.execute(
            "SELECT board, subject, paper_code, year, score, max_marks FROM papers "
            "WHERE user_id=? ORDER BY date_completed DESC, id DESC", (user_id,)
        ).fetchall()
        bounds = db.execute(
            "SELECT board, subject, paper_code, year, a_star, a_boundary, "
            "b_boundary, c_boundary FROM grade_boundaries"
        ).fetchall()

    boundary_rows = [dict(b) for b in bounds]
    groups = {}
    for p in papers:
        groups.setdefault((p["board"], p["subject"]), []).append(dict(p))

    with get_db() as db:
        for (board, subject), attempts in groups.items():
            result = predict_grade(attempts, boundary_rows)
            if not result.get("ready"):
                # Not enough data is a state, not a stale prediction to keep.
                db.execute("DELETE FROM grade_predictions WHERE user_id=? AND board=? "
                           "AND subject=?", (user_id, board, subject))
                continue
            db.execute(
                "INSERT INTO grade_predictions "
                "(user_id, board, subject, grade_score, predicted_grade, next_grade, "
                " marks_to_next, confidence, sample_size, computed_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,NOW()) "
                "ON CONFLICT (user_id, board, subject) DO UPDATE SET "
                " grade_score=EXCLUDED.grade_score, predicted_grade=EXCLUDED.predicted_grade, "
                " next_grade=EXCLUDED.next_grade, marks_to_next=EXCLUDED.marks_to_next, "
                " confidence=EXCLUDED.confidence, sample_size=EXCLUDED.sample_size, "
                " computed_at=NOW()",
                (user_id, board, subject, result["grade_score"], result["predicted_grade"],
                 result["next_grade"], result["marks_to_next"], result["confidence"],
                 result["sample_size"])
            )
        # Subjects the user no longer has papers for shouldn't linger.
        keep = list(groups.keys())
        if keep:
            placeholders = " OR ".join(["(board=? AND subject=?)"] * len(keep))
            params = [user_id] + [v for pair in keep for v in pair]
            db.execute(f"DELETE FROM grade_predictions WHERE user_id=? "
                       f"AND NOT ({placeholders})", tuple(params))
        else:
            db.execute("DELETE FROM grade_predictions WHERE user_id=?", (user_id,))


def get_predictions(user_id):
    with get_db() as db:
        return db.execute(
            "SELECT * FROM grade_predictions WHERE user_id=? ORDER BY subject",
            (user_id,)
        ).fetchall()


# ── Mobile mark entry ─────────────────────────────────────────────────────────

def _own_paper(pid):
    with get_db() as db:
        paper = db.execute("SELECT * FROM papers WHERE id=? AND user_id=?",
                           (pid, current_user.id)).fetchone()
    if not paper:
        abort(404)
    return paper


def _paper_totals(db, pid):
    row = db.execute(
        "SELECT COALESCE(SUM(obtained),0) AS got, COALESCE(SUM(max_marks),0) AS mx, "
        "COUNT(*) AS n FROM question_marks WHERE paper_id=?", (pid,)
    ).fetchone()
    return float(row["got"]), float(row["mx"]), int(row["n"])


@app.route("/papers/<int:pid>/enter")
@login_required
def enter_marks(pid):
    """One-question-per-screen entry. Deliberately a separate flow from the
    desktop table in papers_entry.html rather than a shrunk version of it."""
    paper = _own_paper(pid)
    with get_db() as db:
        rows = db.execute(
            "SELECT q_num, obtained, max_marks, topic FROM question_marks "
            "WHERE paper_id=? ORDER BY id", (pid,)
        ).fetchall()
    questions = [{"n": r["q_num"], "obtained": r["obtained"],
                  "max": r["max_marks"], "topic": r["topic"]} for r in rows]
    topics = get_topics(paper["board"], paper["subject"], paper["paper_code"]) or []
    return render_template("papers_enter.html", paper=paper,
                           questions=questions, topics=topics)


@app.route("/papers/<int:pid>/questions/<q_num>", methods=["POST"])
@login_required
def save_question(pid, q_num):
    """Save ONE question, debounced from the client.

    Saving per paper instead would mean a dropped connection costs a student
    every mark they just entered, and they don't come back. `skip` deletes the
    row: question_marks.obtained is NOT NULL, so "unanswered" is the absence
    of a row, not a null in one.
    """
    _own_paper(pid)
    data = request.get_json(silent=True) or {}
    q_num = str(q_num).strip()[:16]
    if not q_num:
        return jsonify({"ok": False, "error": "bad question number"}), 400

    with get_db() as db:
        if data.get("skip"):
            db.execute("DELETE FROM question_marks WHERE paper_id=? AND q_num=?",
                       (pid, q_num))
        else:
            try:
                obtained = float(data.get("obtained"))
                max_marks = float(data.get("max_marks"))
            except (TypeError, ValueError):
                return jsonify({"ok": False, "error": "obtained and max_marks must be numbers"}), 400
            if max_marks <= 0 or obtained < 0 or obtained > max_marks:
                return jsonify({"ok": False, "error": "marks out of range"}), 400

            topic = (data.get("topic") or "").strip() or None
            existing = db.execute(
                "SELECT id FROM question_marks WHERE paper_id=? AND q_num=?",
                (pid, q_num)
            ).fetchone()
            if existing:
                db.execute(
                    "UPDATE question_marks SET obtained=?, max_marks=?, topic=? WHERE id=?",
                    (obtained, max_marks, topic, existing["id"])
                )
            else:
                db.execute(
                    "INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
                    "VALUES (?,?,?,?,?)",
                    (pid, q_num, obtained, max_marks, topic)
                )

        got, mx, n = _paper_totals(db, pid)
        # Keep the paper's headline score in step with its questions.
        db.execute("UPDATE papers SET score=? WHERE id=?",
                   (got if n else None, pid))

    # The paper's score just moved, so the cached prediction is stale.
    recompute_predictions(current_user.id)

    return jsonify({"ok": True, "total": got, "max_total": mx, "answered": n,
                    "pct": round(got / mx * 100, 1) if mx else None})


@app.route("/revise")
@login_required
def revise():
    """Placeholder so the Revise tab isn't a dead link. The real spaced
    repetition queue is Phase 6."""
    return render_template("revise.html")


@app.route("/heatmap")
@login_required
def heatmap():
    subject_filter = request.args.get("subject", "")
    board_filter   = request.args.get("board", "")
    code_filter    = request.args.get("code", "")

    with get_db() as db:
        papers_raw = db.execute(
            "SELECT p.*, STRING_AGG(q.q_num||':'||q.obtained||'/'||q.max_marks, '|') as qdata "
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

    # Per-topic rollup — the mobile rendering of the same data. A 7-year x
    # 8-question grid is illegible at 390px, so phones get topics ranked
    # worst-first instead of a shrunken table.
    with get_db() as db:
        topic_rows = db.execute(
            "SELECT q.topic, q.q_num, q.obtained, q.max_marks, "
            "       p.year, p.paper_code, p.board, p.subject "
            "FROM question_marks q JOIN papers p ON p.id = q.paper_id "
            "WHERE p.user_id=? AND q.topic IS NOT NULL AND q.topic <> '' "
            "ORDER BY p.year DESC, q.id",
            (current_user.id,)
        ).fetchall()

    topic_agg = {}
    for r in topic_rows:
        if subject_filter and r["subject"] != subject_filter:
            continue
        if board_filter and r["board"] != board_filter:
            continue
        if code_filter and r["paper_code"] != code_filter:
            continue
        t = topic_agg.setdefault(r["topic"], {"topic": r["topic"], "got": 0.0,
                                              "max": 0.0, "n": 0, "detail": []})
        t["got"] += float(r["obtained"])
        t["max"] += float(r["max_marks"])
        t["n"] += 1
        t["detail"].append({
            "label": f"{r['year']} {r['paper_code']}",
            "q_num": r["q_num"],
            "obtained": float(r["obtained"]),
            "max": float(r["max_marks"]),
            "pct": round(float(r["obtained"]) / float(r["max_marks"]) * 100)
                   if float(r["max_marks"]) else 0,
        })

    topics_ranked = []
    for t in topic_agg.values():
        t["pct"] = round(t["got"] / t["max"] * 100, 1) if t["max"] else 0.0
        t["lost"] = round(t["max"] - t["got"], 1)
        topics_ranked.append(t)
    topics_ranked.sort(key=lambda t: (t["pct"], -t["lost"]))   # weakest first

    # Dropdowns
    all_subjects = [(board, subj) for board, s in TEMPLATES.items() for subj in s]
    all_codes = []
    if subject_filter and board_filter:
        try:
            all_codes = [p["code"] for p in TEMPLATES[board_filter][subject_filter]["papers"]]
        except KeyError:
            pass

    return render_template("heatmap.html", sections=sections,
                           topics_ranked=topics_ranked,
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
        if not current_user.is_premium:
            with get_db() as db:
                used = db.execute(
                    "SELECT COUNT(*) AS n FROM uploads WHERE user_id=?",
                    (current_user.id,)
                ).fetchone()["n"]
            if used >= FREE_UPLOAD_LIMIT:
                flash(f"Free plan is capped at {FREE_UPLOAD_LIMIT} uploads — "
                      "upgrade to Pro for unlimited.", "error")
                return redirect(url_for("subscription"))
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
@requires_admin
def boundaries():
    if request.method == "POST":
        try:
            data = json.loads(request.form["json_data"])
            with get_db() as db:
                for row in data:
                    db.execute(
                        """INSERT INTO grade_boundaries
                           (subject, board, paper_code, year, series,
                            a_star, a_boundary, b_boundary, c_boundary)
                           VALUES (?,?,?,?,?,?,?,?,?)
                           ON CONFLICT (subject, board, paper_code, year, series)
                           DO UPDATE SET a_star=EXCLUDED.a_star,
                                         a_boundary=EXCLUDED.a_boundary,
                                         b_boundary=EXCLUDED.b_boundary,
                                         c_boundary=EXCLUDED.c_boundary""",
                        (row["subject"], row["board"], row["paper_code"],
                         row["year"], row.get("series", "June"),
                         row.get("a_star"), row.get("a"), row.get("b"), row.get("c"))
                    )
            flash(f"Imported {len(data)} boundary records.", "success")
        except Exception as e:
            flash(f"Import error: {e}", "error")

    with get_db() as db:
        all_bounds = db.execute(
            "SELECT * FROM grade_boundaries ORDER BY board, subject, paper_code, year DESC"
        ).fetchall()

    groups = {}
    for b in all_bounds:
        key = (b["board"], b["subject"])
        if key not in groups:
            groups[key] = []
        groups[key].append(b)

    return render_template("boundaries.html", groups=groups)

# ── Pro content hub ───────────────────────────────────────────────────────────

@app.route("/pro")
@login_required
@requires_pro("Pro Zone")
def pro_zone():
    with get_db() as db:
        resources = db.execute(
            "SELECT * FROM resources ORDER BY category, title"
        ).fetchall()
        tips = db.execute(
            "SELECT * FROM pro_posts WHERE kind='tip' ORDER BY created_at DESC, id DESC"
        ).fetchall()
        notes = db.execute(
            "SELECT * FROM pro_posts WHERE kind='note' ORDER BY created_at DESC, id DESC"
        ).fetchall()
    res_by_cat = {}
    for r in resources:
        res_by_cat.setdefault(r["category"], []).append(r)
    return render_template("pro.html", res_by_cat=res_by_cat, tips=tips, notes=notes)


@app.route("/admin/content", methods=["GET", "POST"])
@login_required
@requires_admin
def admin_content():
    if request.method == "POST":
        form_type = request.form.get("form_type")
        try:
            with get_db() as db:
                if form_type == "resource":
                    db.execute(
                        "INSERT INTO resources (category, title, url, description) VALUES (?,?,?,?)",
                        (request.form["category"].strip(), request.form["title"].strip(),
                         request.form["url"].strip(),
                         request.form.get("description", "").strip() or None),
                    )
                elif form_type in ("tip", "note"):
                    db.execute(
                        "INSERT INTO pro_posts (kind, subject, title, body, period) VALUES (?,?,?,?,?)",
                        (form_type, request.form.get("subject", "").strip() or None,
                         request.form["title"].strip(), request.form["body"].strip(),
                         request.form.get("period", "").strip() or None),
                    )
                else:
                    flash("Unknown content type.", "error")
                    return redirect(url_for("admin_content"))
            flash("Content added.", "success")
        except Exception as e:
            flash(f"Couldn't save: {e}", "error")
        return redirect(url_for("admin_content"))

    with get_db() as db:
        resources = db.execute("SELECT * FROM resources ORDER BY category, title").fetchall()
        posts = db.execute("SELECT * FROM pro_posts ORDER BY kind, created_at DESC, id DESC").fetchall()
    return render_template("admin_content.html", resources=resources, posts=posts)


@app.route("/admin/content/resource/<int:rid>/delete", methods=["POST"])
@login_required
@requires_admin
def delete_resource(rid):
    with get_db() as db:
        db.execute("DELETE FROM resources WHERE id=?", (rid,))
    flash("Resource deleted.", "success")
    return redirect(url_for("admin_content"))


@app.route("/admin/content/post/<int:pid>/delete", methods=["POST"])
@login_required
@requires_admin
def delete_post(pid):
    with get_db() as db:
        db.execute("DELETE FROM pro_posts WHERE id=?", (pid,))
    flash("Deleted.", "success")
    return redirect(url_for("admin_content"))

# ── Subscription ──────────────────────────────────────────────────────────────

@app.route("/subscription")
@login_required
def subscription():
    # Which plan a legacy subscriber is actually on, so the page doesn't tell
    # someone paying £2 that they're on the £4.99 tier.
    plans = [PRICING["year"], PRICING["month"]]      # annual first, deliberately
    came = request.args.get("from", "")
    if came:
        # Which locked feature actually drove someone here — the only way to
        # tell what's selling.
        log_event("upgrade_prompt_landed", user_id=current_user.id, detail=came)
    return render_template("subscription.html",
                           stripe_enabled=STRIPE_ENABLED,
                           stripe_pk=os.environ.get("STRIPE_PUBLISHABLE_KEY", ""),
                           pricing_features=PRICING_FEATURES,
                           plans=plans,
                           default_interval=DEFAULT_INTERVAL,
                           pricing=PRICING,
                           came_from=request.args.get("from", ""))


@app.route("/subscription/checkout", methods=["POST"])
@login_required
def create_checkout():
    if not STRIPE_ENABLED:
        flash("Stripe not configured.", "error")
        return redirect(url_for("subscription"))

    interval = request.form.get("interval", DEFAULT_INTERVAL)
    plan = PRICING.get(interval)
    # Only the two purchasable plans — nobody can pick their way onto the
    # legacy £2 price through a crafted form post.
    if interval not in ("month", "year") or not plan or not plan["price_id"]:
        flash("That plan isn't available.", "error")
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
            client_reference_id=str(current_user.id),
            payment_method_types=["card"],
            line_items=[{"price": plan["price_id"], "quantity": 1}],
            mode="subscription",
            metadata={"user_id": str(current_user.id), "interval": interval},
            success_url=url_for("sub_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("subscription", _external=True),
        )
        log_event("checkout_started", user_id=current_user.id,
                  detail=f"{interval}:{request.form.get('from', '')}")
        return redirect(sess.url)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("subscription"))


@app.route("/subscription/portal", methods=["POST"])
@login_required
def billing_portal():
    """Stripe's own billing portal — cancellation, card updates, invoices.
    Deliberately not a custom cancel flow."""
    if not (STRIPE_ENABLED and current_user.stripe_customer_id):
        flash("No billing account to manage yet.", "error")
        return redirect(url_for("subscription"))
    try:
        portal = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for("subscription", _external=True),
        )
        return redirect(portal.url)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("subscription"))


@app.route("/subscription/success")
@login_required
def sub_success():
    """Confirmation page only.

    This route does NOT grant Pro. The redirect URL can be typed by hand, so
    entitlements are written by the webhook and nowhere else. The worst case
    here is a few seconds of "payment received, activating" before the webhook
    lands.
    """
    session_id = request.args.get("session_id")
    if not (STRIPE_ENABLED and session_id):
        flash("Couldn't confirm your subscription.", "error")
        return redirect(url_for("subscription"))
    try:
        sess = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        flash("Couldn't confirm your subscription.", "error")
        return redirect(url_for("subscription"))

    completed = (sess["status"] == "complete"
                 and sess["payment_status"] in ("paid", "no_payment_required"))
    belongs = bool(sess["customer"]) and sess["customer"] == current_user.stripe_customer_id
    if not (completed and belongs):
        flash("We couldn't verify that payment. If you just paid, give it a moment and refresh.", "error")
        return redirect(url_for("subscription"))

    log_event("checkout_completed", user_id=current_user.id)
    if user_is_pro(current_user):
        flash("You're now a Telos Pro member!", "success")
    else:
        flash("Payment received — activating your Pro access. Refresh in a few seconds.", "success")
    return redirect(url_for("dashboard"))


# ── Stripe webhook — the ONLY place entitlements are written ──────────────────

def _sget(obj, key, default=None):
    """Safe key read for Stripe objects.

    StripeObject subclasses dict but routes attribute access through
    __getattr__, so `obj.get(...)` raises AttributeError instead of returning
    a default. Everything touching a webhook payload must go through this.
    """
    try:
        return obj[key]
    except (KeyError, TypeError):
        return default


def _apply_subscription(db, customer_id, sub):
    """Write entitlement state from a Stripe subscription object."""
    status = _sget(sub, "status")
    # past_due deliberately keeps access: a failed card should not lock a
    # student out mid-revision. Stripe retries for ~2 weeks.
    active = status in ("active", "trialing", "past_due")
    interval = None
    try:
        interval = sub["items"]["data"][0]["price"]["recurring"]["interval"]
    except (KeyError, IndexError, TypeError):
        pass

    period_end = _sget(sub, "current_period_end")
    period_end_dt = (datetime.fromtimestamp(period_end, tz=timezone.utc)
                     if period_end else None)

    db.execute(
        "UPDATE users SET subscription_status=?, plan=?, plan_interval=?, "
        "stripe_subscription_id=?, current_period_end=? WHERE stripe_customer_id=?",
        (status if active else "free",
         "pro" if active else "free",
         interval,
         _sget(sub, "id"),
         period_end_dt,
         customer_id)
    )


@app.route("/subscription/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig     = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return "", 400
    except Exception:
        # Malformed body etc. Distinguished from a processing failure below so
        # Stripe isn't told "don't retry" when the fault is ours.
        return "", 400

    event_id = _sget(event, "id")
    etype    = _sget(event, "type")

    # Idempotency: claim the event id first. A duplicate delivery collides on
    # the primary key and is acknowledged without being processed twice.
    try:
        with get_db() as db:
            db.execute("INSERT INTO stripe_events (event_id, event_type) VALUES (?,?)",
                       (event_id, etype))
    except psycopg.errors.UniqueViolation:
        return "", 200

    obj = event["data"]["object"]
    customer = _sget(obj, "customer")

    try:
        with get_db() as db:
            if etype == "checkout.session.completed":
                sub_id = _sget(obj, "subscription")
                if sub_id:
                    sub = stripe.Subscription.retrieve(sub_id)
                    _apply_subscription(db, customer, sub)
            elif etype in ("customer.subscription.updated",
                           "customer.subscription.created"):
                _apply_subscription(db, customer, obj)
            elif etype in ("customer.subscription.deleted",
                           "customer.subscription.paused"):
                db.execute(
                    "UPDATE users SET subscription_status='free', plan='free', "
                    "current_period_end=NULL WHERE stripe_customer_id=?", (customer,))
                log_event("subscription_cancelled", detail=str(customer))
            elif etype == "invoice.payment_succeeded":
                sub_id = _sget(obj, "subscription")
                if sub_id:
                    _apply_subscription(db, customer, stripe.Subscription.retrieve(sub_id))
            elif etype == "invoice.payment_failed":
                # No downgrade here — Stripe moves the subscription to past_due
                # and retries. user_is_pro() keeps access during that window.
                log_event("payment_failed", detail=str(customer))
    except Exception:
        # Un-claim so Stripe's retry can have another go at it.
        with get_db() as db:
            db.execute("DELETE FROM stripe_events WHERE event_id=?", (event_id,))
        app.logger.exception("webhook %s (%s) failed", event_id, etype)
        return "", 500

    return "", 200

# ── Mock paper marketplace (one-off £ purchases) ──────────────────────────────

@app.route("/mocks")
@login_required
def mocks():
    with get_db() as db:
        papers = db.execute("SELECT * FROM mock_papers ORDER BY subject, title").fetchall()
        owned = {
            r["mock_paper_id"]
            for r in db.execute(
                "SELECT mock_paper_id FROM purchases WHERE user_id=?", (current_user.id,)
            ).fetchall()
        }
    return render_template("mocks.html", papers=papers, owned=owned)


@app.route("/mocks/<int:mid>/checkout", methods=["POST"])
@login_required
def mock_checkout(mid):
    if not STRIPE_ENABLED:
        flash("Payments aren't configured yet.", "error")
        return redirect(url_for("mocks"))
    with get_db() as db:
        m = db.execute("SELECT * FROM mock_papers WHERE id=?", (mid,)).fetchone()
        already = db.execute(
            "SELECT 1 FROM purchases WHERE user_id=? AND mock_paper_id=?",
            (current_user.id, mid),
        ).fetchone()
    if not m:
        abort(404)
    if already:
        flash("You already own that set.", "success")
        return redirect(url_for("mocks"))
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
                    "product_data": {"name": m["title"]},
                    "unit_amount": m["price_pence"],
                },
                "quantity": 1,
            }],
            metadata={"user_id": current_user.id, "mock_paper_id": mid},
            success_url=url_for("mock_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("mocks", _external=True),
        )
        return redirect(sess.url)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("mocks"))


@app.route("/mocks/success")
@login_required
def mock_success():
    # Verify the one-time Checkout Session with Stripe before recording the sale.
    session_id = request.args.get("session_id")
    if not (STRIPE_ENABLED and session_id):
        flash("Couldn't confirm your purchase.", "error")
        return redirect(url_for("mocks"))
    try:
        sess = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        flash("Couldn't confirm your purchase.", "error")
        return redirect(url_for("mocks"))

    meta = sess["metadata"] or {}
    paid = sess["status"] == "complete" and sess["payment_status"] == "paid"
    owns = ("user_id" in meta) and str(meta["user_id"]) == str(current_user.id)
    mid = meta["mock_paper_id"] if "mock_paper_id" in meta else None
    if paid and owns and mid:
        with get_db() as db:
            db.execute(
                "INSERT INTO purchases (user_id, mock_paper_id, stripe_session_id) "
                "VALUES (?,?,?) ON CONFLICT (user_id, mock_paper_id) DO NOTHING",
                (current_user.id, int(mid), session_id),
            )
        flash("Purchase complete — it's yours to download.", "success")
    else:
        flash("We couldn't verify that purchase. If you just paid, give it a moment and refresh.", "error")
    return redirect(url_for("mocks"))


@app.route("/mocks/<int:mid>/download")
@login_required
def mock_download(mid):
    with get_db() as db:
        owned = db.execute(
            "SELECT 1 FROM purchases WHERE user_id=? AND mock_paper_id=?",
            (current_user.id, mid),
        ).fetchone()
        m = db.execute("SELECT * FROM mock_papers WHERE id=?", (mid,)).fetchone()
    if not m or not m["filename"]:
        abort(404)
    if not owned:
        flash("Buy this set to download it.", "error")
        return redirect(url_for("mocks"))
    return send_from_directory(MOCK_FOLDER, m["filename"],
                               as_attachment=True,
                               download_name=m["orig_name"] or m["filename"])


@app.route("/admin/mocks", methods=["GET", "POST"])
@login_required
@requires_admin
def admin_mocks():
    if request.method == "POST":
        f = request.files.get("file")
        title = request.form.get("title", "").strip()
        if not title or not f or not f.filename:
            flash("Title and a file are required.", "error")
            return redirect(url_for("admin_mocks"))
        if not allowed_file(f.filename):
            flash("Only PDF, PNG or JPG files allowed.", "error")
            return redirect(url_for("admin_mocks"))
        try:
            pounds = float(request.form.get("price", "1") or "1")
        except ValueError:
            pounds = 1.0
        price_pence = max(30, int(round(pounds * 100)))   # Stripe GBP minimum ~30p
        stored = f"{secrets.token_hex(8)}_{secure_filename(f.filename)}"
        f.save(os.path.join(MOCK_FOLDER, stored))
        with get_db() as db:
            db.execute(
                "INSERT INTO mock_papers (title, subject, board, description, price_pence, filename, orig_name) "
                "VALUES (?,?,?,?,?,?,?)",
                (title, request.form.get("subject", "").strip() or None,
                 request.form.get("board", "").strip() or None,
                 request.form.get("description", "").strip() or None,
                 price_pence, stored, f.filename),
            )
        flash("Mock paper set added.", "success")
        return redirect(url_for("admin_mocks"))

    with get_db() as db:
        papers = db.execute(
            "SELECT m.*, (SELECT COUNT(*) FROM purchases p WHERE p.mock_paper_id=m.id) AS sales "
            "FROM mock_papers m ORDER BY m.created_at DESC, m.id DESC"
        ).fetchall()
    return render_template("admin_mocks.html", papers=papers)


@app.route("/admin/mocks/<int:mid>/delete", methods=["POST"])
@login_required
@requires_admin
def delete_mock(mid):
    with get_db() as db:
        m = db.execute("SELECT * FROM mock_papers WHERE id=?", (mid,)).fetchone()
        db.execute("DELETE FROM mock_papers WHERE id=?", (mid,))
    if m and m["filename"]:
        try:
            os.remove(os.path.join(MOCK_FOLDER, m["filename"]))
        except OSError:
            pass
    flash("Mock paper deleted.", "success")
    return redirect(url_for("admin_mocks"))

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

# Run at import time so gunicorn also initialises the DB
init_db()

if __name__ == "__main__":
    print(" * Telos running on http://127.0.0.1:5000")
    app.run(debug=True)
