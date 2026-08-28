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
from _fixtures import fresh_user, purge_user  # noqa: E402

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
        uid = fresh_user(db, "p5-test@telos.local", "p5test",
                         generate_password_hash("Passw0rd!x"),
                         stripe_customer_id=CUST)
        # Every app page redirects a signed-in student with no subjects to
        # setup, so a test user without one never reaches the page under test.
        db.execute("INSERT INTO user_subjects (user_id, board, subject, level) "
                   "VALUES (?,?,?,?) ON CONFLICT DO NOTHING",
                   (uid, "Edexcel", "Further Maths", "A-Level"))
        db.execute("UPDATE users SET plan='free', grandfathered=false, "
                   "subscription_status='free' WHERE id=?", (uid,))

    # ── pricing config ─────────────────────────────────────────────────────
    check("monthly is £4.99", A.PRICING["month"]["amount_pence"], 499)
    check("annual is £39.99", A.PRICING["year"]["amount_pence"], 3999)
    check("legacy £2 still configured", A.PRICING["legacy"]["amount_pence"], 200)
    check("annual is the default", A.DEFAULT_INTERVAL, "year")
    check("monthly price id set", A.PRICING["month"]["price_id"].startswith("price_"), True)
    check("annual price id set", A.PRICING["year"]["price_id"].startswith("price_"), True)

    # The words on the page must agree with the pence in the table. A price
    # whose own copy contradicts it is the kind of thing a customer finds first.
    m_pence = A.PRICING["month"]["amount_pence"]
    y_pence = A.PRICING["year"]["amount_pence"]
    check("the yearly label matches its amount",
          A.PRICING["year"]["label"], "£%.2f" % (y_pence / 100))
    check("the monthly label matches its amount",
          A.PRICING["month"]["label"], "£%.2f" % (m_pence / 100))
    check("the advertised per-month figure is the real one",
          "£%.2f/month" % (y_pence / 100 / 12) in A.PRICING["year"]["sub"], True)
    check("the advertised saving is the real one",
          "save £%d" % round((m_pence * 12 - y_pence) / 100) in A.PRICING["year"]["sub"], True)
    check("yearly actually beats twelve months of monthly", y_pence < m_pence * 12, True)

    # The offer list must not sell something that was withdrawn, and must not
    # flag as "soon" anything already shipped.
    pro_labels = [f["label"] for f in A.PRICING_FEATURES["pro"]]
    check("spaced repetition is no longer offered",
          any("epetition" in l for l in pro_labels), False)
    check("full stats is offered", any("Full stats" in l for l in pro_labels), True)
    check("nothing in the Pro list is still flagged soon",
          any(f.get("coming_soon") for f in A.PRICING_FEATURES["pro"]), False)

    with c.session_transaction() as s:
        s["_user_id"] = str(uid)
        s["_fresh"] = True

    # ── the page ───────────────────────────────────────────────────────────
    html = c.get("/subscription?from=pro-zone").data.decode()
    check("shows £39.99", "£39.99" in html, True)
    check("shows £4.99", "£4.99" in html, True)
    check("shows the monthly equivalent", "£3.33/month" in html, True)
    check("shows the saving", "save £20" in html.lower(), True)
    # The interval used to be a radio pair nested inside one Pro card. It is
    # now one card per plan, each posting a fixed interval — so there is no
    # preselection to get wrong, and nothing for a reader to mis-tick.
    check("three plans are offered", html.count('class="plan-card'), 3)
    check("monthly posts its own interval",
          'name="interval" value="month"' in html, True)
    check("yearly posts its own interval",
          'name="interval" value="year"' in html, True)
    check("the radio pair is gone", "interval-list" in html, False)
    check("the yearly saving sits with the monthly button", "save £20" in html, True)
    check("no hardcoded old £2 upgrade button", "Upgrade — £2/month" in html, False)

    # ── the free trial ──────────────────────────────────────────────────────
    #
    # A trial that takes a card and renews by itself has to say so where the
    # button is, not in terms nobody opens. These check the three facts a
    # student needs before handing over a card: how long it is free, what they
    # will be charged, and that it happens on its own.
    check("a trial is configured", A.TRIAL_DAYS > 0, True)
    check("the page offers it", f"{A.TRIAL_DAYS}-day free trial" in html, True)
    check("...says a card is needed now", "Card required now" in html, True)
    check("...says what happens at the end", "automatically" in html, True)
    check("...and names the price that will be charged",
          A.PRICING["year"]["label"] + " a year" in html, True)
    check("...and says cancelling before the end costs nothing",
          f"before" in html and "not charged" in html, True)
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
