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
from db import get_db  # noqa: E402

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
# ── the social preview card ────────────────────────────────────────────────
#
# A relative og:image is silently IGNORED by every consumer rather than
# reported, so the failure looks exactly like having no image at all: the link
# previews as a blank grey box and nothing anywhere says why. The absolute-URL
# check is the point of this block; the rest just stops the tag pointing at a
# file that is not there.
import re as _re

_og = _re.search(r'<meta property="og:image" content="([^"]+)"', body)
check("the landing page declares an og:image", _og is not None, True)
if _og:
    _url = _og.group(1)
    check(f"og:image is absolute ({_url[:52]})", _url.startswith("http"), True)
    _path = _url.split("/static/", 1)[-1]
    _file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "static", _path)
    check(f"the image it points at exists ({_path})", os.path.isfile(_file), True)
    if os.path.isfile(_file):
        # GitHub rejects a social preview over 1MB, and the same file is used
        # for both, so the ceiling belongs here.
        _kb = os.path.getsize(_file) / 1024
        check(f"it is under GitHub's 1MB limit ({_kb:.0f}KB)", _kb < 1024, True)

check("og:image carries its dimensions",
      'property="og:image:width"' in body and 'property="og:image:height"' in body, True)
check("it has alt text", 'property="og:image:alt"' in body, True)
check("twitter renders it large",
      'name="twitter:card" content="summary_large_image"' in body, True)

robots = anon.get("/robots.txt").get_data(as_text=True)
check("robots does not disallow the whole site",
      any(line.strip() == "Disallow: /" for line in robots.splitlines()), False)

# ── Exam Mode is advertised ────────────────────────────────────────────────
#
# The mocks are the thing most likely to sell, and a landing page that does not
# mention them is the marketing equivalent of hiding the product. These check
# it is really there and, more importantly, that the price on the page is the
# price the checkout will charge — a landing page quoting a price the till does
# not is the exact mistake the "never hardcode a price" rule exists to prevent.
import re as _re2

check("the landing page advertises Exam Mode", 'id="exam-mode"' in body, True)
check("and names both tests", "TMUA" in body and "ESAT" in body, True)

with get_db() as db:
    _papers = db.execute(
        "SELECT paper_code, title, question_count, duration_sec, price_pence "
        "FROM exam_papers WHERE is_published ORDER BY paper_code").fetchall()

if _papers:
    check(f"every published paper is listed ({len(_papers)})",
          [p["title"] for p in _papers if p["title"] not in body], [])
    _prices = {p["price_pence"] for p in _papers if p["price_pence"]}
    if len(_prices) == 1:
        _pence = _prices.pop()
        _want = f"£{_pence // 100}" if _pence % 100 == 0 else f"£{_pence / 100:.2f}"
        check(f"the advertised price matches what the checkout charges ({_want})",
              _want in body, True)
        # And it must not be typed rather than read: change the price and the
        # page must change with it, which is what reading from the row gives.
        check("the price is not a hardcoded string in the template",
              "£1 a paper" in open(
                  os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "templates", "landing.html"), encoding="utf-8").read(),
              False)
    else:
        # Papers priced differently: the page must say nothing rather than
        # quote one of them as if it covered all.
        check("no single price is quoted when papers differ",
              "a paper.</strong>" in body, False)



# ── /practice-papers ─────────────────────────────────────────────────────────
#
# The one page on the site a search engine can use. Everything worth ranking
# for is behind @login_required, which is correct and also means Telos is
# invisible to anyone searching "free TMUA practice papers".
#
# These checks are about the two things that would quietly destroy its value:
# serving it to a crawler as a redirect, and letting the counts drift away from
# the catalogue so the page advertises papers that are not there.

import admissions_papers as _ap  # noqa: E402

_pp = app.test_client().get("/practice-papers")
check("the paper catalogue is public", _pp.status_code, 200)
_body = _pp.get_data(as_text=True)

_groups = _ap.all_official_papers()
_total = sum(len(v) for v in _groups.values())
_marked = sum(1 for rows in _groups.values() for r in rows
              if _ap.answer_key(r["subject"], r["year"], r.get("part")))
check(f"it states the real paper count ({_total})",
      f"{_total} admissions-test papers" in _body, True)
check(f"and the real auto-marked count ({_marked})",
      f"{_marked} of them" in _body, True)

# Every test in the catalogue has to appear, or the page is advertising a
# subset while claiming the total.
_names = {_ap.test_name(k) for k in _groups}
check(f"every test is named ({len(_names)})",
      sorted(n for n in _names if n not in _body), [])

# The distinction that must never blur. A Telos mock is not a past paper and
# not anybody's official material, and the page says so in both directions.
check("Telos mocks are not passed off as past papers",
      "not past papers" in _body, True)
check("the independence line is present",
      "not affiliated with any awarding organisation" in _body, True)
check("nothing on the page calls a Telos paper official",
      "official Telos" in _body.lower(), False)

# The PDFs are third-party material and stay behind the login — see
# exam.admissions_pdf. A public page that linked straight to one would undo
# that decision silently.
check("no past-paper PDF is linked from the public page",
      "/admissions/paper/" in _body, False)

check("it is listed in the sitemap",
      "/practice-papers" in app.test_client().get(
          "/sitemap.xml").get_data(as_text=True), True)

# Crawlable means reachable without a redirect, for a signed-out visitor.
check("and robots are not told to skip it",
      "/practice-papers" in app.test_client().get(
          "/robots.txt").get_data(as_text=True), False)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
