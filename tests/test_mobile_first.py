import os
"""Phase 0.6 checks: renders, mobile-first CSS rules, per-question save API."""
import json, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
from db import get_db  # noqa: E402

app = A.app
app.debug = False
app.config["WTF_CSRF_ENABLED"] = False
fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


c = app.test_client()
with c.session_transaction() as s:      # log in as the founder account, read-only
    s["_user_id"] = "1"
    s["_fresh"] = True

# ── 1. every nav destination renders ────────────────────────────────────────
for path, label in [("/", "dashboard"), ("/papers", "papers"), ("/heatmap", "heatmap"),
                    ("/revise", "revise"), ("/stats", "stats"), ("/bank", "bank"),
                    ("/subscription", "subscription"), ("/mocks", "mocks")]:
    r = c.get(path)
    check(f"GET {path} ({label})", r.status_code, 200)

# ── 2. nav renders from NAV_ITEMS in both layouts ───────────────────────────
r = c.get("/papers")
html = r.data.decode()
check("tab bar present", '<nav class="tabbar"' in html, True)
check("tab bar has 5 items", html.count('class="tab ') + html.count('class="tab"'), 5)
check("More sheet present", 'id="more-sheet"' in html, True)
check("sidebar still rendered", 'class="sidebar"' in html, True)
check("viewport-fit=cover", "viewport-fit=cover" in html, True)
check("Papers tab marked active", 'aria-current="page"' in html, True)
for lbl in ("Today", "Papers", "Heatmap", "Revise", "More"):
    check(f"tab label {lbl}", f"<span>{lbl}</span>" in html, True)
# secondary items belong in the sheet, not the tab bar
sheet = html.split('id="more-sheet"')[1]
for lbl in ("Question Bank", "Stats", "Pro Zone", "Mock Papers", "Subscription"):
    check(f"sheet contains {lbl}", lbl in sheet, True)

# admin-only items are filtered by the context processor
check("admin links present for admin user", "Manage Content" in html, True)

# ── 3. mobile-first CSS ─────────────────────────────────────────────────────
css = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "css", "telos.css"), encoding="utf-8").read()
check("no max-width media queries", "max-width:" in css.replace(" ", "") and
      "@media(max-width:" in css.replace(" ", ""), False)
check("has min-width 640 query", "@media (min-width: 640px)" in css, True)
check("has min-width 1024 query", "@media (min-width: 1024px)" in css, True)
check("--tap-min token", "--tap-min: 44px" in css, True)
check("safe-area tokens", "env(safe-area-inset-bottom" in css, True)
check("no declaration uses 100vh", bool(re.search(r"height:\s*[^;{}]*\b100vh\b", css)), False)
check("does use 100dvh", "100dvh" in css, True)
check("inputs are 16px", "font-size: 16px" in css, True)
check("buttons get touch-action", "touch-action: manipulation" in css, True)
check("tab bar padded by safe area", "padding-bottom: var(--safe-bottom)" in css, True)
check("hover rules gated behind hover query", "@media (hover: hover)" in css, True)

# ── 4. per-question save API ────────────────────────────────────────────────
pid = None
try:
    with get_db() as db:
        cur = db.execute(
            """INSERT INTO papers (user_id, subject, board, paper_code, year, series,
                                   score, max_marks, date_completed, weak_topics, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (1, "Further Maths", "Edexcel", "CP1", "2019", "June", None, 75.0,
             "2026-08-17", "", "PHASE 0.6 TEST — auto-deleted"))
        pid = cur.lastrowid

    r = c.post(f"/papers/{pid}/questions/1", json={"obtained": 5, "max_marks": 8})
    check("save q1", r.status_code, 200)
    check("save q1 total", r.get_json()["total"], 5.0)

    r = c.post(f"/papers/{pid}/questions/2", json={"obtained": 6, "max_marks": 6})
    check("save q2 running total", r.get_json()["total"], 11.0)
    check("save q2 answered count", r.get_json()["answered"], 2)

    r = c.post(f"/papers/{pid}/questions/1", json={"obtained": 7, "max_marks": 8})
    check("re-save q1 updates not duplicates", r.get_json()["total"], 13.0)
    check("re-save keeps 2 rows", r.get_json()["answered"], 2)

    r = c.post(f"/papers/{pid}/questions/2", json={"skip": True})
    check("skip removes the row", r.get_json()["answered"], 1)

    r = c.post(f"/papers/{pid}/questions/3", json={"obtained": 99, "max_marks": 6})
    check("rejects score above max", r.status_code, 400)
    r = c.post(f"/papers/{pid}/questions/3", json={"obtained": "abc", "max_marks": 6})
    check("rejects non-numeric", r.status_code, 400)

    with get_db() as db:
        row = db.execute("SELECT score FROM papers WHERE id=?", (pid,)).fetchone()
    check("paper score kept in sync", float(row["score"]), 7.0)

    r = c.get(f"/papers/{pid}/enter")
    check("GET enter flow", r.status_code, 200)
    check("enter flow has keypad", 'id="keypad"' in r.data.decode(), True)

    # ── 5. heatmap topic rollup (0.6d) ─────────────────────────────────────
    with get_db() as db:
        db.execute("INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
                   "VALUES (?,?,?,?,?)", (pid, "4", 2.0, 10.0, "Complex Numbers"))
        db.execute("INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
                   "VALUES (?,?,?,?,?)", (pid, "5", 9.0, 10.0, "Matrices"))
    r = c.get("/heatmap")
    hm = r.data.decode()
    check("heatmap renders", r.status_code, 200)
    check("topic list present", 'class="topic-list mobile-only"' in hm, True)
    check("grid wrapped for hiding on phones", '<div class="heatmap-grid">' in hm, True)
    check("two-column wrapper present", 'class="heatmap-split"' in hm, True)
    check("weakest topic listed first",
          hm.index("Complex Numbers") < hm.index("Matrices"), True)
    check("topic shows marks lost", "8.0 marks lost" in hm, True)

    # ownership: another user's paper must 404
    with c.session_transaction() as s:
        s["_user_id"] = "999999"
    r = c.post(f"/papers/{pid}/questions/1", json={"obtained": 1, "max_marks": 8})
    check("other user cannot write", r.status_code in (401, 404, 302), True)
finally:
    if pid:
        with get_db() as db:
            db.execute("DELETE FROM question_marks WHERE paper_id=?", (pid,))
            db.execute("DELETE FROM papers WHERE id=?", (pid,))
        print(f"cleaned up test paper {pid}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
