"""The TikTok path, walked as a new visitor would walk it.

Lands on /, follows the question-bank call to action, registers, picks a
subject, and checks they arrive at the question bank rather than the dashboard
— which is the whole claim the section makes.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import flask  # noqa: E402
import app as A  # noqa: E402
from db import get_db  # noqa: E402
from _fixtures import purge_user  # noqa: E402

app = A.app
app.debug = False
EMAIL = "funnel@telos.test"
PW = "funnel-password-1"
fails = []


def check(label, got, want):
    ok = got == want
    print(("PASS  " if ok else "FAIL  ") + label + f": {got!r}"
          + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


try:
    with get_db() as db:
        purge_user(db, EMAIL)

    c = app.test_client()
    home = c.get("/").get_data(as_text=True)
    check("the landing page offers the question bank",
          'id="question-bank"' in home, True)

    # The visitor clicks "Start free trial".
    r = c.get("/register?next=/mocks")
    check("the register page loads with a destination", r.status_code, 200)

    r = c.post("/register?next=/mocks",
               data={"email": EMAIL, "username": "funnel", "password": PW},
               follow_redirects=False)
    check("registering redirects", r.status_code, 302)
    check("to the subject picker, which cannot be skipped",
          "/welcome" in r.headers.get("Location", ""), True)

    # They pick a subject.
    r = c.post("/welcome", data={"qualification": "Edexcel|Maths|A-Level"},
               follow_redirects=False)
    check("finishing setup redirects", r.status_code, 302)
    dest = r.headers.get("Location", "")
    check("straight to the question bank, not the dashboard",
          dest.endswith("/mocks"), True)

    body = c.get("/mocks").get_data(as_text=True)
    check("and the question bank is there",
          "TMUA Challenging Question Bank 1" in body, True)
    check("with a buy button", "Buy £1.00" in body, True)

    # And the ordinary path is unaffected.
    with get_db() as db:
        purge_user(db, EMAIL)
    c2 = app.test_client()
    c2.post("/register", data={"email": EMAIL, "username": "funnel",
                               "password": PW})
    r = c2.post("/welcome", data={"qualification": "Edexcel|Maths|A-Level"},
                follow_redirects=False)
    # The dashboard is served at "/" for a signed-in student, so that — not
    # "/dashboard" — is what a plain sign-up should redirect to.
    with app.test_request_context():
        dashboard_url = flask.url_for("dashboard")
    check("a normal sign-up still lands on the dashboard",
          r.headers.get("Location", ""), dashboard_url)
finally:
    with get_db() as db:
        purge_user(db, EMAIL)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
