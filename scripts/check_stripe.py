"""Check that Stripe is configured the way the app believes it is.

Read-only. Creates nothing, changes nothing, charges nothing. Run it after any
change to the Stripe variables, and before taking real money:

    railway run .venv\\Scripts\\python.exe scripts\\check_stripe.py

Exits non-zero when something is wrong, so it can gate a deploy.

Why this exists. Every fault it looks for is one that produces no error until a
customer hits it:

  * a price variable pointing at the wrong amount — the page advertised £39.99
    for a while against a Stripe price of £29, and nothing anywhere noticed
  * monthly and yearly swapped — both are valid price IDs, so the app cannot
    tell; it simply charges yearly customers £4.99 a year
  * the two prices on different products — checkout works, but the billing
    portal cannot offer a plan switch, and you find out from a support email
  * a webhook missing an event — entitlements are webhook-only by design, so a
    missing event looks exactly like a failed payment from inside the app
  * the customer portal not activated in live mode — fine in test, 500s in live
  * keys from different modes, or price IDs left pointing at the other mode

The expected prices are read from the app's own PRICING table rather than
written here, so this checks Stripe against what the pricing page actually
says instead of against a second copy that can drift.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import stripe
except ImportError:
    raise SystemExit("stripe is not installed in this environment.")

# The app's own table: label, amount and interval all come from there.
from app import PRICING  # noqa: E402

# The events app.stripe_webhook() actually handles. Anything else it ignores.
REQUIRED_EVENTS = {
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.subscription.paused",
    "invoice.payment_succeeded",
    "invoice.payment_failed",
}
WEBHOOK_PATH = "/subscription/webhook"

problems, notes = [], []


def problem(msg):
    problems.append(msg)


def note(msg):
    notes.append(msg)


sk = os.environ.get("STRIPE_SECRET_KEY", "")
pk = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
if not sk:
    raise SystemExit("STRIPE_SECRET_KEY is not set. Run this under `railway run`.")
stripe.api_key = sk

live = sk.startswith("sk_live")
print("mode: %s" % ("LIVE — real money" if live else "test"))

if not os.environ.get("STRIPE_WEBHOOK_SECRET"):
    problem("STRIPE_WEBHOOK_SECRET is not set; every webhook will fail signature "
            "verification and no subscription will ever grant Pro")
if pk and pk.startswith("pk_live") != live:
    problem("the secret and publishable keys are from different modes")

# ── prices ──────────────────────────────────────────────────────────────────
#
# Checked against PRICING so the question asked is "does Stripe agree with the
# page", which is the question that matters.
products, checked = {}, 0
for key, plan in PRICING.items():
    pid = plan.get("price_id") or ""
    var = {"month": "STRIPE_PRICE_MONTHLY", "year": "STRIPE_PRICE_ANNUAL",
           "legacy": "STRIPE_PRICE_LEGACY"}.get(key, key)
    if not pid:
        if not plan.get("hidden"):
            problem("%s has no price id" % var)
        continue

    try:
        price = stripe.Price.retrieve(pid)
    except Exception as exc:
        msg = "%s (%s) does not exist in this mode" % (var, pid)
        if plan.get("hidden"):
            note(msg + " — it is hidden from the pricing page, so nothing renders "
                       "it, but it is stale config worth clearing")
        else:
            problem(msg + ": %s" % exc)
        continue

    interval = price.recurring.interval if price.recurring else "one-off"
    want_interval = "month" if plan["period"].endswith("month") else "year"
    amount_ok = price.unit_amount == plan["amount_pence"]
    interval_ok = interval == want_interval
    currency_ok = (price.currency or "").lower() == "gbp"

    print("%-22s £%-8.2f %-4s / %-6s active=%s  %s"
          % (var, (price.unit_amount or 0) / 100, (price.currency or "").upper(),
             interval, price.active,
             "OK" if (amount_ok and interval_ok and currency_ok) else "MISMATCH"))
    checked += 1

    if not amount_ok:
        problem("%s is £%.2f in Stripe but the pricing page says %s"
                % (var, (price.unit_amount or 0) / 100, plan["label"]))
    if not interval_ok:
        problem("%s bills every %s but the page says %s — monthly and yearly may "
                "be the wrong way round" % (var, interval, plan["period"]))
    if not currency_ok:
        problem("%s is in %s, not GBP" % (var, (price.currency or "?").upper()))
    if not price.active and not plan.get("hidden"):
        problem("%s is archived in Stripe" % var)

    if not plan.get("hidden"):
        products.setdefault(price.product, []).append(var)

if checked == 0:
    problem("no sellable price could be read at all")

# Plan switching in the billing portal only works within one product.
if len(products) > 1:
    problem("the sellable prices sit on different products (%s) — the billing "
            "portal cannot offer a plan switch between them"
            % "; ".join("%s: %s" % (p, ", ".join(v)) for p, v in products.items()))
elif products:
    print("both sellable prices share product %s" % next(iter(products)))

# ── webhook ─────────────────────────────────────────────────────────────────
try:
    endpoints = stripe.WebhookEndpoint.list(limit=50).data
except Exception as exc:
    endpoints = []
    problem("could not list webhook endpoints: %s" % exc)

mine = [e for e in endpoints if (e.url or "").endswith(WEBHOOK_PATH)]
if not mine:
    near = [e.url for e in endpoints if "telos" in (e.url or "")]
    problem("no webhook endpoint ending in %s%s" % (
        WEBHOOK_PATH, (" — found %s" % ", ".join(near)) if near else ""))

for e in mine:
    print("webhook %s  status=%s" % (e.url, e.status))
    if e.status != "enabled":
        problem("the webhook is %s rather than enabled" % e.status)
    events = set(e.enabled_events or [])
    if "*" in events:
        note("the webhook is subscribed to every event; the app handles %d"
             % len(REQUIRED_EVENTS))
        continue
    missing = REQUIRED_EVENTS - events
    if missing:
        problem("the webhook is missing %s" % ", ".join(sorted(missing)))
    else:
        print("  all %d required events present" % len(REQUIRED_EVENTS))
    extra = events - REQUIRED_EVENTS
    if extra:
        note("the webhook sends %d event(s) the app ignores" % len(extra))

# ── customer portal ─────────────────────────────────────────────────────────
try:
    configs = stripe.billing_portal.Configuration.list(limit=10).data
    if any(c.active for c in configs):
        print("customer portal configured")
    else:
        problem("the customer portal has no active configuration — Manage billing "
                "will fail. Settings -> Billing -> Customer portal.")
except Exception as exc:
    problem("could not read the customer portal configuration: %s" % exc)

# ── verdict ─────────────────────────────────────────────────────────────────
print()
for n in notes:
    print("NOTE     %s" % n)
for p in problems:
    print("PROBLEM  %s" % p)
print()
if problems:
    print("%d problem(s) — do not take payments until these are fixed"
          % len(problems))
else:
    print("READY" + (" — this account is live and will charge real cards" if live
                     else " (test mode)"))
sys.exit(1 if problems else 0)
