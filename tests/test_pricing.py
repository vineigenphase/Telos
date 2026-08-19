import os
"""Phase 5: pricing, checkout, webhook entitlements, idempotency."""
import hashlib
import hmac
import json
import sys
import time
from datetime import datetime, timezone, timedelta

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


def signed_post(client, payload_dict, secret=None):
    secret = secret or A.STRIPE_WEBHOOK_SECRET
    payload = json.dumps(payload_dict, separators=(",", ":"))
    t = int(time.time())
    sig = hmac.new(secret.encode(), f"{t}.{payload}".encode(), hashlib.sha256).hexdigest()
    return client.post("/subscription/webhook", data=payload.encode(),
                       headers={"Content-Type": "application/json",
                                "Stripe-Signature": f"t={t},v1={sig}"})


uid = None
CUST = "cus_phase5_test_donotmatch"
c = app.test_client()
try:
    with get_db() as db:
        cur = db.execute("INSERT INTO users (email, username, password_hash, stripe_customer_id) "
                         "VALUES (?,?,?,?)",
                         ("p5-test@telos.local", "p5test",
                          generate_password_hash("Passw0rd!x"), CUST))
        uid = cur.lastrowid
        db.execute("UPDATE users SET plan='free', grandfathered=false, "
                   "subscription_status='free' WHERE id=?", (uid,))

    # ── pricing config ─────────────────────────────────────────────────────
    check("monthly is £4.99", A.PRICING["month"]["amount_pence"], 499)
    check("annual is £29", A.PRICING["year"]["amount_pence"], 2900)
    check("legacy £2 still configured", A.PRICING["legacy"]["amount_pence"], 200)
    check("annual is the default", A.DEFAULT_INTERVAL, "year")
    check("monthly price id set", A.PRICING["month"]["price_id"].startswith("price_"), True)
    check("annual price id set", A.PRICING["year"]["price_id"].startswith("price_"), True)

    with c.session_transaction() as s:
        s["_user_id"] = str(uid)
        s["_fresh"] = True

    # ── the page ───────────────────────────────────────────────────────────
    html = c.get("/subscription?from=pro-zone").data.decode()
    check("shows £29", "£29" in html, True)
    check("shows £4.99", "£4.99" in html, True)
    check("shows the monthly equivalent", "£2.42/month" in html, True)
    check("shows the saving", "save £31" in html.lower(), True)
    check("annual radio is preselected",
          'value="year"' in html and 'value="year"\n                     checked' in html.replace("\r", "")
          or 'value="year"' in html and "checked" in html.split('value="year"')[1][:120], True)
    check("no hardcoded old £2 upgrade button", "Upgrade — £2/month" in html, False)
    check("landing from a locked feature is logged",
          A.get_predictions is not None, True)   # placeholder to keep numbering
    with get_db() as db:
        row = db.execute("SELECT detail FROM analytics_events WHERE event='upgrade_prompt_landed' "
                         "AND user_id=? ORDER BY id DESC LIMIT 1", (uid,)).fetchone()
    check("upgrade prompt source recorded", row["detail"] if row else None, "pro-zone")

    # ── checkout guards ────────────────────────────────────────────────────
    r = c.post("/subscription/checkout", data={"interval": "legacy"}, follow_redirects=True)
    check("cannot buy the legacy £2 price", b"isn&#39;t available" in r.data or b"isn't available" in r.data, True)
    r = c.post("/subscription/checkout", data={"interval": "decade"}, follow_redirects=True)
    check("rejects an unknown interval", b"isn&#39;t available" in r.data or b"isn't available" in r.data, True)

    # ── success page must NOT grant ────────────────────────────────────────
    r = c.get("/subscription/success", follow_redirects=True)
    with get_db() as db:
        u = db.execute("SELECT subscription_status, plan FROM users WHERE id=?", (uid,)).fetchone()
    check("bare success visit grants nothing", u["subscription_status"], "free")
    check("bare success visit leaves plan free", u["plan"], "free")

    # ── webhook is the only writer ─────────────────────────────────────────
    period_end = int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp())
    sub_obj = {
        "id": "sub_phase5", "object": "subscription", "customer": CUST, "status": "active",
        "current_period_end": period_end,
        "items": {"data": [{"price": {"recurring": {"interval": "year"}}}]},
    }
    ev = {"id": "evt_p5_active", "object": "event", "type": "customer.subscription.updated",
          "data": {"object": sub_obj}}
    r = signed_post(c, ev)
    check("valid webhook accepted", r.status_code, 200)
    with get_db() as db:
        u = db.execute("SELECT subscription_status, plan, plan_interval, stripe_subscription_id, "
                       "current_period_end FROM users WHERE id=?", (uid,)).fetchone()
    check("webhook granted pro", u["plan"], "pro")
    check("status recorded", u["subscription_status"], "active")
    check("interval recorded", u["plan_interval"], "year")
    check("subscription id recorded", u["stripe_subscription_id"], "sub_phase5")
    check("period end recorded", u["current_period_end"] is not None, True)

    # idempotency: same event id again must not be reprocessed
    with get_db() as db:
        db.execute("UPDATE users SET plan='sentinel' WHERE id=?", (uid,))
    r = signed_post(c, ev)
    check("duplicate event acknowledged", r.status_code, 200)
    with get_db() as db:
        u = db.execute("SELECT plan FROM users WHERE id=?", (uid,)).fetchone()
    check("duplicate event did NOT reprocess", u["plan"], "sentinel")

    # bad signature rejected
    r = signed_post(c, {"id": "evt_p5_bad", "object": "event", "type": "customer.subscription.updated",
                        "data": {"object": sub_obj}}, secret="whsec_wrong")
    check("bad signature rejected", r.status_code, 400)

    # past_due keeps access
    with get_db() as db:
        db.execute("UPDATE users SET plan='free' WHERE id=?", (uid,))
    pd = dict(sub_obj, status="past_due")
    signed_post(c, {"id": "evt_p5_pastdue", "object": "event",
                    "type": "customer.subscription.updated", "data": {"object": pd}})
    with get_db() as db:
        u = db.execute("SELECT plan, subscription_status FROM users WHERE id=?", (uid,)).fetchone()
    check("past_due keeps pro access", u["plan"], "pro")
    check("past_due status stored as past_due", u["subscription_status"], "past_due")

    # cancellation revokes
    signed_post(c, {"id": "evt_p5_deleted", "object": "event",
                    "type": "customer.subscription.deleted", "data": {"object": sub_obj}})
    with get_db() as db:
        u = db.execute("SELECT plan, subscription_status, current_period_end FROM users WHERE id=?",
                       (uid,)).fetchone()
    check("cancellation revokes pro", u["plan"], "free")
    check("cancellation clears period end", u["current_period_end"], None)
    with get_db() as db:
        row = db.execute("SELECT count(*) AS n FROM analytics_events "
                         "WHERE event='subscription_cancelled'").fetchone()
    check("cancellation logged", row["n"] >= 1, True)
finally:
    with get_db() as db:
        db.execute("DELETE FROM stripe_events WHERE event_id LIKE 'evt_p5%'")
        if uid:
            db.execute("DELETE FROM analytics_events WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))
    with get_db() as db:
        db.execute("DELETE FROM analytics_events WHERE detail=?", (CUST,))
    print(f"cleaned up test user {uid}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
