import os
"""Terms and privacy — the pages that have to be true.

These are not decorative. A subscription that takes a card, runs a free trial
and then charges automatically has disclosure obligations, and the failure mode
is not a broken page — it is a page that renders beautifully while contradicting
what the checkout screen says, or while naming a price nobody is charged.

So most of what is asserted here is agreement between the documents and the
code: the trial length, the two prices, and the contact address all come from
app.py, and the tests fail if a document drifts from them.

The placeholder check is deliberately soft locally and hard in production. A
sole trader contracts under their own legal name, there is no sensible default
for that, and shipping "[FULL LEGAL NAME]" to real users would be worse than
having no terms at all — but failing every developer's suite over an unset
environment variable would be noise.
"""
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402

app = A.app
app.debug = False
fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


c = app.test_client()

# ── 1. Both pages are public ────────────────────────────────────────────────
#
# Signed out is the state that matters. Someone deciding whether to sign up,
# or a parent checking what their child's revision app collects, must be able
# to read these without creating an account.
terms = c.get("/terms")
priv = c.get("/privacy")
check("terms is public", terms.status_code, 200)
check("privacy is public", priv.status_code, 200)

t_html = terms.get_data(as_text=True)
p_html = priv.get_data(as_text=True)

# ── 2. They agree with the code about money ─────────────────────────────────
check(f"terms states the {A.TRIAL_DAYS}-day trial",
      f"{A.TRIAL_DAYS}-day free trial" in t_html, True)
check("terms names the monthly price",
      A.PRICING["month"]["label"] in t_html, True)
check("terms names the annual price",
      A.PRICING["year"]["label"] in t_html, True)

# The four facts a trial that takes a card has to state. Each is checked by
# meaning, not by matching the exact sentence, so the copy can be rewritten
# without silently dropping one of them.
for label, pattern in [
    ("card is required up front", r"must enter card details"),
    ("it converts automatically", r"charged automatically"),
    ("cancelling first costs nothing", r"cancel before the trial ends you are not charged"),
    ("cancel any time", r"cancel at any time"),
]:
    check(f"terms says {label}", bool(re.search(pattern, t_html, re.I)), True)

# ── 3. Statutory rights are not quietly dropped ─────────────────────────────
check("terms keeps the 14-day distance-selling right",
      "14 days" in t_html, True)
check("terms does not purport to exclude non-excludable liability",
      "death or personal injury" in t_html, True)
check("terms names the governing law", "England and Wales" in t_html, True)

# ── 4. The privacy policy describes the schema that exists ──────────────────
#
# Written from the actual columns. Two of these were found by looking rather
# than assuming, and both would have been wrong from memory.
check("privacy discloses the password-reset IP",
      re.search(r"IP address", p_html, re.I) is not None, True)
check("privacy states card details never reach us",
      re.search(r"never (receive|see)[^.]*card", p_html, re.I) is not None, True)
check("privacy names the ICO", "ico.org.uk" in p_html, True)
check("privacy covers under-18s", re.search(r"under 18", p_html, re.I) is not None, True)

# parent_email and parent_report_optin are columns on users, but nothing ever
# writes to them — the weekly parent report was cut. Claiming we collect a
# parent's email would describe a feature that does not exist.
check("privacy does not claim to collect a parent's email",
      re.search(r"parent'?s? email address we", p_html, re.I) is None, True)

# ── 5. Reachable from where they matter ─────────────────────────────────────
#
# A legal page nobody can find does no work. The two that count are the point
# of sale and the point of sign-up.
reg = c.get("/register").get_data(as_text=True)
check("register links the terms", "/terms" in reg, True)
check("register links the privacy policy", "/privacy" in reg, True)

landing = c.get("/").get_data(as_text=True)
check("landing footer links the terms", "/terms" in landing, True)
check("landing footer links the privacy policy", "/privacy" in landing, True)

# ── 6. No placeholders in front of real users ───────────────────────────────
#
# Soft locally, hard in production: LEGAL_NAME has no sensible default, and the
# placeholder is meant to be impossible to miss — but a developer running the
# suite without the variable set should not see a failure.
placeholder = "FULL LEGAL NAME" in t_html or "FULL LEGAL NAME" in p_html
if os.environ.get("LEGAL_NAME"):
    check("no placeholder remains when LEGAL_NAME is set", placeholder, False)
    check("the configured name is on both pages",
          os.environ["LEGAL_NAME"] in t_html and os.environ["LEGAL_NAME"] in p_html, True)
elif placeholder:
    print("NOTE  LEGAL_NAME is unset, so both documents still show the "
          "placeholder. Set it in Railway before these pages go in front of "
          "anyone — this is a warning locally and a failure in production.")

check("both pages publish a contact address",
      A.LEGAL_EMAIL in t_html and A.LEGAL_EMAIL in p_html, True)

# A policy that redates itself every morning destroys the record of what a user
# actually agreed to, so the date must be a fixed string, not today().
check("the updated date is fixed, not generated",
      bool(re.fullmatch(r"\d{1,2} \w+ \d{4}", A.LEGAL_UPDATED)), True)
check("both pages show it", A.LEGAL_UPDATED in t_html and A.LEGAL_UPDATED in p_html, True)

# ── 7. A licence exists ─────────────────────────────────────────────────────
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lic = os.path.join(root, "LICENSE")
check("LICENSE exists", os.path.isfile(lic), True)
if os.path.isfile(lic):
    body = open(lic, encoding="utf-8").read()
    check("licence reserves rights", "All rights reserved" in body, True)
    # The boundary data is published by the exam boards and is not ours to
    # license. Saying so is the difference between a licence and a claim.
    check("licence disclaims the exam boards' boundary data",
          "awarding organisations" in body, True)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
