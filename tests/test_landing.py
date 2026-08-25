import os
"""The public landing page at "/".

"/" used to be @login_required, so a first-time visitor and every crawler got a
redirect to /login — while sitemap.xml listed "/" as a public page. It now
serves the landing page to anonymous visitors and the dashboard to signed-in
ones, and these tests pin both halves of that branch.

The last check is the one that matters most. The reveal animations hide content
with CSS, and that hiding is only ever applied under a class that JavaScript
adds after confirming it can also remove it. If the class were ever rendered
into the HTML directly, a visitor without JavaScript — or with a stalled one —
would get a blank page below the hero. That is not a hypothetical: it happened
twice during development.
"""
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


anon = app.test_client()
user = app.test_client()
with user.session_transaction() as s:
    s["_user_id"] = "1"
    s["_fresh"] = True

r = anon.get("/")
body = r.get_data(as_text=True)
check("anonymous / is the landing page, not a redirect", r.status_code, 200)
check("...and it is the landing template", "lp-hero" in body, True)
check("...with a signup call to action", "/register" in body, True)
check("...and a way back in", "/login" in body, True)

check("signed in, / is still the dashboard",
      "statrow" in user.get("/").get_data(as_text=True), True)

# Prices are data-driven. The rule is in TELOS_STATE.md and a marketing page is
# the most tempting place in the app to break it.
plan = A.PRICING[A.DEFAULT_INTERVAL]
check("the price comes from PRICING", plan["label"] in body, True)
check("...and so does the period", plan["period"] in body, True)
check("the cut parent report is not advertised",
      "parent report" in body.lower(), False)

# The reveal gate must be set by script, never rendered into the markup.
check("the hide-content class is not in the served HTML",
      'class="lp-reveal-ready"' in body or "<html class" in body, False)
check("...and the script that sets it is present",
      "lp-reveal-ready" in body, True)

# Public pages must stay crawlable and self-describing. canonical_url() reads
# the live request, so it is resolved inside one rather than called bare.
with app.test_request_context("/"):
    canonical = A.canonical_url("/")

check("the landing page declares a canonical URL",
      'rel="canonical"' in body, True)
check("it carries a meta description", 'name="description"' in body, True)
check("sitemap still lists /",
      "<loc>" + canonical + "</loc>" in anon.get("/sitemap.xml").get_data(as_text=True),
      True)
robots = anon.get("/robots.txt").get_data(as_text=True)
check("robots does not disallow the whole site",
      any(line.strip() == "Disallow: /" for line in robots.splitlines()), False)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
