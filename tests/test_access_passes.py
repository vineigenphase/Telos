"""The TMUA pass — gating, granting, extension and expiry.

No Stripe here: the checkout call itself needs a card and a human, and is the
one part of this that a test cannot reach. What it does cover is everything
that decides whether a student who paid gets what they paid for, and whether
one who did not is kept out — which is where the bugs that cost money live.

`grant_pass` is called directly rather than through a fake webhook, because it
is the single place both the webhook and the success route write through, and
testing it twice through two wrappers would test the wrappers.
"""
import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import app as A  # noqa: E402
import exam as E  # noqa: E402
from db import get_db  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402
from _fixtures import fresh_user, purge_user  # noqa: E402

app = A.app
app.debug = False
PW = "pass-check-pw"
FREE = "pass-free@telos.test"
PRO = "pass-pro@telos.test"
fails = []


def check(label, got, want):
    ok = got == want
    print(("PASS  " if ok else "FAIL  ") + label + f": {got!r}"
          + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


def login(email):
    c = app.test_client()
    c.post("/login", data={"email": email, "password": PW})
    return c


try:
    with get_db() as db:
        free_id = fresh_user(db, FREE, "passfree", generate_password_hash(PW))
        pro_id = fresh_user(db, PRO, "passpro", generate_password_hash(PW),
                            grandfathered=True, plan="pro")
    for uid in (free_id, pro_id):
        A.set_user_subjects(uid, ["UAT-UK|TMUA|Admissions test",
                                  "UAT-UK|ENGAA (2019-2023)|Admissions test"])

    # ── which tests are gated ───────────────────────────────────────────────
    check("TMUA is a gated scope", "TMUA" in E.PASSES, True)
    check("and costs £3.99", E.PASSES["TMUA"]["price_pence"], 399)
    check("for 30 days", E.PASSES["TMUA"]["days"], 30)
    check("ENGAA is not gated", E.PASSES.get("ENGAA"), None)

    # ── a free student without a pass ───────────────────────────────────────
    c = login(FREE)
    body = c.get("/admissions/tmua").get_data(as_text=True)
    check("the TMUA list is still visible without a pass",
          "Applications of Mathematical Knowledge" in body, True)
    check("and offers the pass", "TMUA Pass" in body and "3.99" in body, True)
    check("but the papers are locked", "Locked" in body, True)
    check("and no download link is dangled",
          "/admissions/paper/TMUA" in body, False)

    r = c.get("/admissions/tmua/2022/paper-1")
    check("entering a TMUA paper redirects without a pass", r.status_code, 302)
    r = c.get("/admissions/paper/TMUA_2022_P1.pdf")
    check("and the PDF is refused", r.status_code, 302)

    # ENGAA is untouched by any of this.
    # Fetch once to clear the flash left by the refusals above, which would
    # otherwise render on the ENGAA page and look like a pass being offered
    # there. A flash is shown on the next page whatever that page is.
    c.get("/admissions")
    body = c.get("/admissions/engaa-2019-2023").get_data(as_text=True)
    check("ENGAA stays free — no pass offered",
          "Get the TMUA Pass" in body, False)
    check("and its papers are not locked", "Locked" in body, False)
    check("entering an ENGAA paper still works",
          c.get("/admissions/engaa-2019-2023/2021/part-a").status_code, 200)

    # ── granting ────────────────────────────────────────────────────────────
    with get_db() as db:
        first = E.grant_pass(db, free_id, "TMUA", "cs_test_session_one", 399)
        again = E.grant_pass(db, free_id, "TMUA", "cs_test_session_one", 399)
    check("a pass is granted once", first, True)
    check("and the same Stripe session never grants twice", again, False)

    with get_db() as db:
        rows = db.execute(
            "SELECT expires_at FROM access_passes WHERE user_id=?",
            (free_id,)).fetchall()
    check("exactly one pass row", len(rows), 1)
    days = (rows[0]["expires_at"]
            - datetime.datetime.now(datetime.timezone.utc)).days
    check("it runs about 30 days", 28 <= days <= 30, True)

    c = login(FREE)
    body = c.get("/admissions/tmua").get_data(as_text=True)
    check("the list now says the pass is active", "active" in body, True)
    check("the papers are unlocked", "Locked" in body, False)
    check("entering a TMUA paper now works",
          c.get("/admissions/tmua/2022/paper-1").status_code, 200)

    # ── a second purchase extends rather than replaces ──────────────────────
    with get_db() as db:
        E.grant_pass(db, free_id, "TMUA", "cs_test_session_two", 399)
        rows = db.execute(
            "SELECT expires_at FROM access_passes WHERE user_id=? "
            "ORDER BY expires_at", (free_id,)).fetchall()
    check("a second purchase adds a row", len(rows), 2)
    gap = (rows[1]["expires_at"] - rows[0]["expires_at"]).days
    check("and extends from the old expiry, not from today", gap, 30)

    # ── expiry ──────────────────────────────────────────────────────────────
    with get_db() as db:
        db.execute("UPDATE access_passes SET expires_at = NOW() - INTERVAL "
                   "'1 day' WHERE user_id=?", (free_id,))
    c = login(FREE)
    r = c.get("/admissions/tmua/2022/paper-1")
    check("a lapsed pass locks the paper again", r.status_code, 302)
    body = c.get("/admissions/tmua").get_data(as_text=True)
    check("and the page offers it again", "Get the TMUA Pass" in body, True)
    check("saying the last one ran out", "run out" in body, True)

    with get_db() as db:
        kept = db.execute("SELECT COUNT(*) AS n FROM access_passes "
                          "WHERE user_id=?", (free_id,)).fetchone()["n"]
    check("expired passes are kept as history, not deleted", kept, 2)

    # ── Pro needs no pass ───────────────────────────────────────────────────
    c = login(PRO)
    body = c.get("/admissions/tmua").get_data(as_text=True)
    check("Pro is not sold a pass", "Get the TMUA Pass" in body, False)
    check("and is told why", "included with your Pro subscription" in body, True)
    check("Pro can enter a TMUA paper",
          c.get("/admissions/tmua/2022/paper-1").status_code, 200)
    with get_db() as db:
        pro_rows = db.execute("SELECT COUNT(*) AS n FROM access_passes "
                              "WHERE user_id=?", (pro_id,)).fetchone()["n"]
    check("without a pass row ever being written", pro_rows, 0)

finally:
    with get_db() as db:
        purge_user(db, FREE)
        purge_user(db, PRO)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
