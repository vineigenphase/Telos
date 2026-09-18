"""One-off purchases are granted by the webhook, not only by the redirect.

The hole this closes. Both the £1 Exam Mode papers and the marketplace question
banks recorded a sale only in the route Stripe redirects back to. That route
verifies properly — it asks Stripe rather than trusting the redirect — but it
only runs if the student comes back. Close the tab on Stripe's confirmation
screen and the card is charged while nothing unlocks, which from inside the app
is indistinguishable from never having paid.

The webhook is posted for real here, with a genuine signature computed from
STRIPE_WEBHOOK_SECRET, so this exercises the route rather than the helper it
happens to call. Nothing here touches Stripe: the event is constructed locally
and signed locally, which is exactly what Stripe's own CLI does when it
forwards test events.
"""
import hashlib
import hmac
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import app as A  # noqa: E402
from db import get_db  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402
from _fixtures import fresh_user, purge_user  # noqa: E402

app = A.app
app.debug = False
EMAIL = "webhookgrant@telos.test"
PW = "webhook-grant-pw"
fails = []


def check(label, got, want):
    ok = got == want
    print(("PASS  " if ok else "FAIL  ") + label + f": {got!r}"
          + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


def post_event(event):
    """POST a correctly signed event at the real webhook route."""
    body = json.dumps(event).encode()
    ts = int(time.time())
    secret = A.STRIPE_WEBHOOK_SECRET or ""
    mac = hmac.new(secret.encode(), f"{ts}.".encode() + body,
                   hashlib.sha256).hexdigest()
    return app.test_client().post(
        "/subscription/webhook", data=body,
        headers={"Stripe-Signature": f"t={ts},v1={mac}",
                 "Content-Type": "application/json"})


def session_event(event_id, session_id, meta, payment_status="paid"):
    # `"object": "event"` is not decoration. stripe 15.x reads the top-level
    # object to tell a v1 event from a v2 one, and without it construct_event
    # raises before it ever looks at the payload — which the route turns into a
    # 400 that looks exactly like a bad signature.
    return {
        "id": event_id,
        "object": "event",
        "type": "checkout.session.completed",
        "data": {"object": {
            "id": session_id,
            "object": "checkout.session",
            "customer": "cus_test_grant",
            "subscription": None,
            "payment_status": payment_status,
            "status": "complete",
            "metadata": meta,
        }},
    }


def rows(table, column, uid):
    with get_db() as db:
        return [r[column] for r in db.execute(
            f"SELECT {column} FROM {table} WHERE user_id=?", (uid,)).fetchall()]


skip = not (A.STRIPE_ENABLED and A.STRIPE_WEBHOOK_SECRET)
if skip:
    print("SKIP  no STRIPE_WEBHOOK_SECRET in this environment — "
          "the signature cannot be produced, so the route cannot be reached")

try:
    with get_db() as db:
        uid = fresh_user(db, EMAIL, "webhookgrant", generate_password_hash(PW))
        paper = db.execute("SELECT id FROM exam_papers WHERE is_published "
                           "ORDER BY id LIMIT 1").fetchone()
        bank = db.execute("SELECT id FROM mock_papers ORDER BY id "
                          "LIMIT 1").fetchone()

    if not skip and paper:
        n = int(time.time())
        r = post_event(session_event(f"evt_grant_{n}", f"cs_grant_{n}",
                                     {"user_id": str(uid),
                                      "exam_paper_id": str(paper["id"])}))
        check("the webhook accepts the event", r.status_code, 200)
        check("and the paper is owned without anyone returning from Stripe",
              rows("exam_purchases", "paper_id", uid), [paper["id"]])

        # Stripe retries. A second delivery of the same event must not double up.
        post_event(session_event(f"evt_grant_{n}", f"cs_grant_{n}",
                                 {"user_id": str(uid),
                                  "exam_paper_id": str(paper["id"])}))
        check("a redelivered event grants nothing twice",
              len(rows("exam_purchases", "paper_id", uid)), 1)

        # And the redirect route, arriving late, must also be a no-op rather
        # than an error — both paths write, whichever lands first.
        with get_db() as db:
            db.execute(
                "INSERT INTO exam_purchases (user_id, paper_id, stripe_session_id) "
                "VALUES (?,?,?) ON CONFLICT (user_id, paper_id) DO NOTHING",
                (uid, paper["id"], f"cs_grant_{n}"))
        check("the success route arriving afterwards changes nothing",
              len(rows("exam_purchases", "paper_id", uid)), 1)

    if not skip and bank:
        n = int(time.time()) + 1
        post_event(session_event(f"evt_bank_{n}", f"cs_bank_{n}",
                                 {"user_id": str(uid),
                                  "mock_paper_id": str(bank["id"])}))
        check("a question bank is granted the same way",
              rows("purchases", "mock_paper_id", uid), [bank["id"]])

    if not skip:
        # An unpaid session, and a session that is nothing to do with us.
        n = int(time.time()) + 2
        before = len(rows("exam_purchases", "paper_id", uid))
        post_event(session_event(f"evt_unpaid_{n}", f"cs_unpaid_{n}",
                                 {"user_id": str(uid),
                                  "exam_paper_id": str(paper["id"])},
                                 payment_status="unpaid"))
        check("an unpaid session grants nothing",
              len(rows("exam_purchases", "paper_id", uid)), before)

        r = post_event(session_event(f"evt_other_{n}", f"cs_other_{n}",
                                     {"something_else": "1"}))
        check("a session with no metadata of ours is ignored, not an error",
              r.status_code, 200)

    # The helper is pure enough to check the guards directly.
    with get_db() as db:
        A._grant_one_time_purchase(db, {"payment_status": "paid",
                                        "id": "cs_nometa", "metadata": {}})
    check("no user_id means no grant",
          len(rows("exam_purchases", "paper_id", uid)), 1 if not skip else 0)
finally:
    with get_db() as db:
        purge_user(db, EMAIL)
        db.execute("DELETE FROM stripe_events WHERE event_id LIKE 'evt_grant_%' "
                   "OR event_id LIKE 'evt_bank_%' OR event_id LIKE 'evt_unpaid_%' "
                   "OR event_id LIKE 'evt_other_%'")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
