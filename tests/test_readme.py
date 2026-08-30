import os
"""The README states figures as fact. This checks they are still true.

A README full of specific numbers goes stale precisely BECAUSE it is specific,
and it goes stale silently — nothing breaks, the document simply starts lying
to whoever reads it first. Adding /terms and /privacy moved the route count
from 49 to 51 and the file count from 169 to 175 within a day of the figures
being written, which is what prompted this.

Two rules make the guard honest rather than annoying:

  1. A claim that cannot be FOUND fails. If the README is reworded so a regex
     stops matching, this suite must fail loudly rather than quietly stop
     checking anything. A guard that silently covers nothing is worse than no
     guard, because it looks like protection.

  2. The check enforces the precision the README claims. A figure written as
     "51" is checked exactly; one written with a leading "~" is approximate on
     purpose and is checked to the rounding it implies. The assertion count is
     the one number that churns with every test edit — including this file —
     so it carries a band wide enough that adding a check does not break the
     build, but narrow enough to catch a figure that has drifted.
"""
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
import paper_templates as T  # noqa: E402
from db import get_db  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


def near(label, got, want, tol):
    ok = abs(got - want) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got}" +
          ("" if ok else f"  (README says {want}, tolerance ±{tol})"))
    if not ok:
        fails.append(label)


readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()


def claimed(label, pattern):
    """Pull one number out of the README, or fail — never silently skip."""
    m = re.search(pattern, readme)
    if not m:
        print(f"FAIL  README no longer states {label} — pattern {pattern!r} matched nothing. "
              f"Either restore the claim or delete this check; do not leave it unmatched.")
        fails.append(f"claim missing: {label}")
        return None
    return int(m.group(1).replace(",", ""))


# ── counted from the repository ─────────────────────────────────────────────
def git_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    return [p for p in out.splitlines() if p]


def count_dir(rel, suffix):
    d = os.path.join(ROOT, *rel.split("/"))
    return len([f for f in os.listdir(d) if f.endswith(suffix)])


tracked = git_files()
code = [p for p in tracked if p.endswith((".py", ".sql", ".html", ".css", ".js"))]
loc = 0
for p in code:
    with open(os.path.join(ROOT, p), encoding="utf-8", errors="replace") as fh:
        loc += sum(1 for _ in fh)

suite_files = sorted(f for f in os.listdir(os.path.join(ROOT, "tests"))
                     if f.startswith("test_") and f.endswith(".py"))
assertions = 0
for f in suite_files:
    with open(os.path.join(ROOT, "tests", f), encoding="utf-8") as fh:
        for line in fh:
            if re.match(r"\s*(check|ok)\(", line) and "def " not in line:
                assertions += 1

quals = sum(len(subs) for subs in T.TEMPLATES.values())
components = sum(len(cfg["papers"]) for subs in T.TEMPLATES.values() for cfg in subs.values())

with get_db() as db:
    boundary_rows = db.execute("SELECT COUNT(*) AS n FROM grade_boundaries").fetchone()["n"]
    tables = db.execute("SELECT COUNT(*) AS n FROM information_schema.tables "
                        "WHERE table_schema='public'").fetchone()["n"]

# Every rule Flask actually serves, minus the static endpoint it adds itself.
routes = len([r for r in A.app.url_map.iter_rules() if r.endpoint != "static"])

# scripts/boundaries holds extractors, generators AND verifiers. Calling all of
# them "loaders" overstated it — six are helpers (_paths, audit, topics,
# fm_topics, verify_as, verify_fm), so the README says "scripts" and this
# counts scripts.
boundary_scripts = count_dir("scripts/boundaries", ".py")

deps = len([l for l in open(os.path.join(ROOT, "requirements.txt"), encoding="utf-8")
            if l.strip() and not l.startswith("#")])

css = sum(1 for f in os.listdir(os.path.join(ROOT, "static/css")) if f.endswith(".css")
          for _ in open(os.path.join(ROOT, "static/css", f), encoding="utf-8"))
js = sum(1 for f in os.listdir(os.path.join(ROOT, "static/js")) if f.endswith(".js")
         for _ in open(os.path.join(ROOT, "static/js", f), encoding="utf-8"))

app_lines = sum(1 for _ in open(os.path.join(ROOT, "app.py"), encoding="utf-8"))

# ── exact claims ────────────────────────────────────────────────────────────
for label, pattern, actual in [
    ("qualifications",     r"\| Qualifications \| \*\*(\d+)\*\*",              quals),
    ("boundary rows",      r"\| Grade boundary rows \| \*\*([\d,]+)\*\*",      boundary_rows),
    ("components",         r"\| Components \| ([\d,]+) papers",                components),
    ("routes",             r"\| Routes \| (\d+) \|",                           routes),
    ("tables",             r"\| Tables \| (\d+), under",                        tables),
    ("migrations (table)", r"\| Tables \| \d+, under (\d+) numbered",           count_dir("migrations", ".sql")),
    ("suites",             r"\| Tests \| (\d+) suites",                         len(suite_files)),
    ("tracked files",      r"lines across (\d+) tracked files",                 len(tracked)),
    ("catalogue line",     r"paper_templates\.py\s+(\d+) qualifications",       quals),
    ("components line",    r"paper_templates\.py\s+\d+ qualifications, (\d+)",  components),
    ("migrations (map)",   r"migrations/\s+(\d+) numbered",                     count_dir("migrations", ".sql")),
    ("suites (map)",       r"tests/\s+(\d+) standalone suites",                 len(suite_files)),
    ("boundary scripts",   r"scripts/boundaries/\s+(\d+) board-document",       boundary_scripts),
    ("templates",          r"templates/\s+(\d+) Jinja templates",               count_dir("templates", ".html")),
    ("suites (repo map)",  r"tests/\s+(\d+) suites,",                           len(suite_files)),
]:
    want = claimed(label, pattern)
    if want is not None:
        check(f"README {label}", actual, want)

# "Seven runtime dependencies" is written as a word, not a digit.
if "Seven runtime dependencies" not in readme:
    fails.append("claim missing: dependencies")
    print("FAIL  README no longer says 'Seven runtime dependencies'")
else:
    check("README dependency count", deps, 7)

# ── approximate claims, checked to the precision they advertise ─────────────
#
# "~28,000 lines" means the thousands figure, so that is what is compared.
want_loc = claimed("total lines", r"\| Code \| ~([\d,]+) lines")
if want_loc is not None:
    check("README total lines (to the nearest thousand)",
          round(loc / 1000) * 1000, want_loc)

# app.py grows whenever a route is added, so this is approximate too.
want_app = claimed("app.py lines", r"entitlement gates\s+\(~([\d,]+) lines\)")
if want_app is not None:
    check("README app.py lines (to the nearest hundred)",
          round(app_lines / 100) * 100, want_app)

want_css = claimed("CSS lines", r"~([\d,]+) lines of hand-written CSS")
if want_css is not None:
    check("README CSS lines (to the nearest hundred)", round(css / 100) * 100, want_css)

want_js = claimed("JS lines", r"and (\d+) of vanilla JS")
if want_js is not None:
    near("README JS lines", js, want_js, 20)

# The assertion count changes with every test edit, including edits to this
# file, so an exact match would fail the build for adding a single check. The
# band is one suite wide: it ignores routine churn and still catches a figure
# that has genuinely drifted.
want_asserts = claimed("assertions", r"\| Tests \| \d+ suites, ~([\d,]+) assertions")
if want_asserts is not None:
    near("README assertion count", assertions, want_asserts, 30)

want_asserts_map = claimed("assertions (repo map)", r"tests/\s+\d+ suites, ~([\d,]+) assertions")
if want_asserts_map is not None:
    near("README assertion count (repo map)", assertions, want_asserts_map, 30)

# ── a related invariant worth holding here ──────────────────────────────────
#
# A suite file that nobody registered never runs, and looks like coverage while
# providing none. This is the natural place to catch it.
sys.path.insert(0, os.path.join(ROOT, "tests"))
import run_all  # noqa: E402

registered = {f for _, f in run_all.SUITES}
unregistered = sorted(set(suite_files) - registered)
check(f"every suite file is registered in run_all "
      f"({', '.join(unregistered) if unregistered else 'all registered'})",
      unregistered, [])

missing = sorted(registered - set(suite_files))
check(f"every registered suite exists "
      f"({', '.join(missing) if missing else 'all present'})", missing, [])

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
