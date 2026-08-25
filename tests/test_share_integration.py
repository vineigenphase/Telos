import os
"""Phase 9 integration: creating, serving, viewing and revoking a share card.

Creates its own throwaway user and papers against the real database and
removes them in a finally block, the same shape as the Phase 4 suite.

The behaviours worth pinning here are the ones that are about access rather
than about pixels: a card is public without a login, the owner sees controls
a stranger doesn't, somebody else's card cannot be revoked, and a revoked
card is gone rather than merely hidden.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
from db import get_db  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

app = A.app
app.debug = False
fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


uid = other_uid = None
tokens = []
try:
    with get_db() as db:
        uid = db.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?,?,?)",
            ("p9-test@telos.local", "p9test",
             generate_password_hash("Passw0rd!x"))).lastrowid
        other_uid = db.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?,?,?)",
            ("p9-other@telos.local", "p9other",
             generate_password_hash("Passw0rd!x"))).lastrowid
        # Give the account a subject. Every app page redirects a signed-in
        # student with no subjects to setup, so a test user without one
        # never reaches the page it is trying to assert on.
        for u in (uid, other_uid):
            db.execute("INSERT INTO user_subjects (user_id, board, subject, level) "
                       "VALUES (?,?,?,?) ON CONFLICT DO NOTHING",
                       (u, "Edexcel", "Further Maths", "A-Level"))
        for yr in ("2022", "2023", "2024"):
            db.execute(
                "INSERT INTO papers (user_id, board, subject, paper_code, year, "
                "series, score, max_marks) VALUES (?,?,?,?,?,?,?,?)",
                (uid, "Edexcel", "Further Maths", "CP1", yr, "June", 60, 75))

    owner = app.test_client()
    with owner.session_transaction() as s:
        s["_user_id"] = str(uid); s["_fresh"] = True
    stranger = app.test_client()
    with stranger.session_transaction() as s:
        s["_user_id"] = str(other_uid); s["_fresh"] = True
    anon = app.test_client()

    # ── what this user can share ────────────────────────────────────────────
    payload, err = A.build_share_payload(uid, "milestone")
    check("papers logged is shareable", (err, payload["value"]), (None, 3))
    _, err = A.build_share_payload(uid, "heatmap")
    check("no tagged questions means no accuracy card",
          err, "no tagged questions to chart yet")
    _, err = A.build_share_payload(uid, "grade")
    check("no prediction means no grade card", err, "no prediction to share yet")

    opts = [o["type"] for o in A.share_options(uid, [], 3)]
    check("only the milestone card is offered", opts, ["milestone"])

    # ── create ──────────────────────────────────────────────────────────────
    r = owner.post("/share/milestone", follow_redirects=False)
    check("creating a card redirects to it", r.status_code, 302)
    token = r.headers["Location"].rsplit("/", 1)[-1]
    tokens.append(token)
    check("an unknown card type is a 404",
          owner.post("/share/nonsense").status_code, 404)
    check("creating a card requires a login",
          anon.post("/share/milestone").status_code in (301, 302), True)

    # ── the public page ─────────────────────────────────────────────────────
    r = anon.get(f"/s/{token}")
    body = r.get_data(as_text=True)
    check("the card page is public", r.status_code, 200)
    check("...and asks not to be indexed",
          'content="noindex, nofollow"' in body, True)
    check("...and carries the signup call to action", "/register" in body, True)
    check("...and shows a stranger no owner controls", "Revoke" in body, False)
    check("the owner sees the controls",
          "Revoke" in owner.get(f"/s/{token}").get_data(as_text=True), True)

    # ── the PNG ─────────────────────────────────────────────────────────────
    r = anon.get(f"/s/{token}.png")
    check("the PNG is public", r.status_code, 200)
    check("...and is a PNG", r.mimetype, "image/png")
    check("...and is immutable, since the payload is",
          "immutable" in (r.headers.get("Cache-Control") or ""), True)
    check("...and defaults to the story size",
          r.data[:24][16:20], (1080).to_bytes(4, "big"))
    r2 = anon.get(f"/s/{token}.png?size=post")
    check("the post size renders too", r2.status_code, 200)
    check("...and differs from the story render", r2.data != r.data, True)
    r3 = anon.get(f"/s/{token}.png?size=billboard")
    check("an unknown size falls back rather than erroring",
          (r3.status_code, r3.data == r.data), (200, True))

    # ── unknown tokens ──────────────────────────────────────────────────────
    check("an unknown token is a 404", anon.get("/s/nope").status_code, 404)
    check("...for the PNG too", anon.get("/s/nope.png").status_code, 404)

    # ── revoking ────────────────────────────────────────────────────────────
    check("a stranger cannot revoke someone else's card",
          stranger.post(f"/share/{token}/delete").status_code, 403)
    check("...and the card still works", anon.get(f"/s/{token}").status_code, 200)
    check("the owner can revoke",
          owner.post(f"/share/{token}/delete").status_code, 302)
    check("...and the link is gone, not hidden",
          anon.get(f"/s/{token}").status_code, 404)
    check("...including the PNG", anon.get(f"/s/{token}.png").status_code, 404)

finally:
    with get_db() as db:
        for t in tokens:
            db.execute("DELETE FROM share_cards WHERE token=?", (t,))
        for u in (uid, other_uid):
            if u:
                db.execute("DELETE FROM share_cards WHERE user_id=?", (u,))
                db.execute("DELETE FROM papers WHERE user_id=?", (u,))
                db.execute("DELETE FROM users WHERE id=?", (u,))

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
