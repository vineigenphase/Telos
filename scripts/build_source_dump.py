"""Generate TELOS_FULL_SOURCE.txt — every line of source in one file.

A complete, ordered listing of the code that makes up Telos: every tracked
text file, in full, with a table of contents and a build appendix.

Ordering is deliberate rather than alphabetical. Someone reading top to bottom
gets configuration, then the application, then the pure engines, then the data,
then the migrations that shaped the schema, then the interface, then the tests
that hold it all in place. Alphabetical order would open on `app.py` at 2,997
lines and teach nothing.

Binary files (fonts and icons) are listed in the manifest with
their sizes but obviously not inlined.

Regenerate with:

    .venv\\Scripts\\python.exe scripts\\build_source_dump.py
"""

from __future__ import annotations

import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "TELOS_FULL_SOURCE.txt")

TEXT_EXT = {".py", ".sql", ".html", ".css", ".js", ".json", ".webmanifest",
            ".txt", ".md", ".example", ".gitignore", ""}

# (heading, blurb, [predicates]) — first section that claims a file wins, so
# order matters and the catch-all sits last.
SECTIONS = [
    ("CONFIGURATION AND DEPLOYMENT",
     "What the host needs to run it. Seven runtime dependencies, a bare\n"
     "gunicorn line, and the environment contract. No secrets — values live in\n"
     "Railway and never in the repository.",
     lambda p: p in ("Procfile", "requirements.txt", ".env.example", ".gitignore")),

    ("CORE APPLICATION",
     "Routes, session handling, entitlement gates, and the database layer.\n"
     "db.py is the one to read first: it presents the sqlite3 interface the\n"
     "app was written against, over psycopg3, and carries the retry logic that\n"
     "serverless Postgres requires.",
     lambda p: p in ("app.py", "db.py", "auth.py", "mailer.py", "brand.py")),

    ("PURE ENGINES",
     "No Flask, no database, no I/O. Plain data in, plain data out. This is\n"
     "the decision the rest of the codebase leans on hardest — every rule\n"
     "about grade ladders, recency weighting and confidence is testable\n"
     "without a request context or a network round trip.",
     lambda p: p in ("prediction.py", "prescription.py", "revision.py")),

    ("CATALOGUE AND RENDERING",
     "The 61 qualifications and 199 components the app offers, the permanent\n"
     "boundary seed data, and the share cards rendered server-side as PNG.",
     lambda p: p in ("paper_templates.py", "seed_boundaries.py", "sharecards.py")),

    ("MIGRATIONS",
     "40 numbered, idempotent SQL migrations, tracked by filename in\n"
     "schema_migrations. They do not run on deploy — the Procfile is a bare\n"
     "gunicorn line — because a migration that runs automatically on every\n"
     "boot will eventually run during an incident.",
     lambda p: p.startswith("migrations/")),

    ("TEMPLATES",
     "Server-rendered Jinja. No client framework and no build step.",
     lambda p: p.startswith("templates/")),

    ("STATIC — CSS, JAVASCRIPT, PWA",
     "Hand-written CSS and vanilla JavaScript. The service worker keys its\n"
     "cache on the deployed git commit, so a deploy invalidates it.",
     lambda p: p.startswith("static/")),

    ("TESTS",
     "20 standalone suites, 567 assertions, no pytest. Each file runs top to\n"
     "bottom, prints PASS/FAIL per assertion and exits non-zero on failure.\n"
     "Several suites guard invariants rather than behaviour: a dashboard costs\n"
     "at most 22 statements, deltas are None and never 0 when there is nothing\n"
     "to compare against, and the safe-area CSS rules stay last in their file.",
     lambda p: p.startswith("tests/")),

    ("SCRIPTS — BOUNDARY LOADERS AND TOOLING",
     "36 loaders, one per board document. Every extractor validates each\n"
     "component against its own maximum mark before emitting SQL, because a\n"
     "mis-parsed column produces boundaries that are plausible, wrong, and\n"
     "would quietly mis-grade every student who sat that paper.",
     lambda p: p.startswith("scripts/")),

    ("PROJECT DOCUMENTS",
     "The living handoff document and the v2 specification.",
     lambda p: p.endswith(".md")),

    ("EVERYTHING ELSE",
     "One-off migration and audit tooling from earlier stages, kept because it\n"
     "documents how the SQLite-to-Postgres move was actually carried out.",
     lambda p: True),
]


def run(*args: str) -> str:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def is_text(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    if ext not in TEXT_EXT:
        return False
    full = os.path.join(ROOT, path)
    try:
        with open(full, "rb") as fh:
            return b"\x00" not in fh.read(4096)
    except OSError:
        return False


def main() -> int:
    tracked = [p for p in run("git", "ls-files").splitlines() if p]
    if not tracked:
        print("no tracked files — is this a git repository?", file=sys.stderr)
        return 1

    # Exclude our own output. It is a tracked .txt, so without this the dump
    # swallows the previous copy of itself and doubles in size every run.
    tracked = [p for p in tracked if os.path.basename(p) != os.path.basename(OUT)]

    text_files, binaries = [], []
    for p in tracked:
        (text_files if is_text(p) else binaries).append(p)

    # Assign each file to the first section that claims it.
    buckets: list[tuple[str, str, list[str]]] = []
    remaining = list(text_files)
    for heading, blurb, claims in SECTIONS:
        taken = [p for p in remaining if claims(p)]
        remaining = [p for p in remaining if p not in set(taken)]
        if taken:
            buckets.append((heading, blurb, sorted(taken)))

    total_lines = 0
    for _, _, files in buckets:
        for p in files:
            with open(os.path.join(ROOT, p), encoding="utf-8", errors="replace") as fh:
                total_lines += sum(1 for _ in fh)

    commit = run("git", "rev-parse", "--short", "HEAD")
    ncommits = run("git", "rev-list", "--count", "HEAD")
    first = run("git", "log", "--reverse", "--format=%ad", "--date=short")
    first = first.splitlines()[0] if first else "?"
    today = datetime.date.today().isoformat()

    bar = "=" * 78
    parts: list[str] = []
    w = parts.append

    w(bar)
    w("  TELOS — COMPLETE SOURCE")
    w(bar)
    w("")
    w("  Every line of source that makes up Telos, in one file.")
    w("")
    w("  Live:        https://telosapp.co.uk")
    w("  Repository:  github.com/vineigenphase/Telos")
    w(f"  Commit:      {commit}")
    w(f"  Generated:   {today}")
    w("")
    w(f"  {len(text_files)} source files, {total_lines:,} lines")
    w(f"  {ncommits} commits, {first} to {today}")
    w("")
    w("  Flask past-paper tracker for A-level and SQA students. Records every")
    w("  question separately, converts each attempt to a position on a grade")
    w("  scale using that paper's real published boundaries, and turns the")
    w("  residue into a ranked list of what is costing marks.")
    w("")
    w("  Sections run configuration, application, engines, data, migrations,")
    w("  interface, tests, tooling. A build appendix follows at the end.")
    w("")

    # ── contents ────────────────────────────────────────────────────────────
    w(bar)
    w("  CONTENTS")
    w(bar)
    w("")
    for i, (heading, _, files) in enumerate(buckets, 1):
        n = sum(1 for _ in files)
        w(f"  {i}. {heading}   ({n} file{'s' if n != 1 else ''})")
        for p in files:
            with open(os.path.join(ROOT, p), encoding="utf-8", errors="replace") as fh:
                ln = sum(1 for _ in fh)
            w(f"       {p:<58} {ln:>6} lines")
        w("")
    w(f"  {len(buckets) + 1}. BUILD APPENDIX — commands and commit history")
    w("")
    if binaries:
        w("  Binary files, listed but not inlined:")
        for p in sorted(binaries):
            size = os.path.getsize(os.path.join(ROOT, p))
            w(f"       {p:<58} {size:>7,} bytes")
        w("")

    # ── the source ──────────────────────────────────────────────────────────
    for i, (heading, blurb, files) in enumerate(buckets, 1):
        w("")
        w(bar)
        w(bar)
        w(f"  SECTION {i} — {heading}")
        w(bar)
        w(bar)
        w("")
        for line in blurb.splitlines():
            w(f"  {line}")
        w("")

        for p in files:
            full = os.path.join(ROOT, p)
            with open(full, encoding="utf-8", errors="replace") as fh:
                body = fh.read().splitlines()
            w("")
            w("-" * 78)
            w(f"  FILE:  {p}")
            w(f"  LINES: {len(body)}")
            w("-" * 78)
            w("")
            width = len(str(len(body))) if body else 1
            for n, line in enumerate(body, 1):
                w(f"{n:>{width}} | {line}")
            w("")

    # ── build appendix ──────────────────────────────────────────────────────
    w("")
    w(bar)
    w(bar)
    w(f"  SECTION {len(buckets) + 1} — BUILD APPENDIX")
    w(bar)
    w(bar)
    w("")
    w("  How the code above is built, run, tested and deployed, and the commit")
    w("  history that produced it.")
    w("")
    w("-" * 78)
    w("  ENVIRONMENT")
    w("-" * 78)
    w("")
    for line in [
        "python -m venv .venv",
        ".venv\\Scripts\\python.exe -m pip install -r requirements.txt",
        "",
        "# railway run injects the environment; secrets never live in the repo",
        "railway run .venv\\Scripts\\python.exe app.py                      # dev :5000",
        "railway run .venv\\Scripts\\python.exe tests\\run_all.py            # 20 suites",
        "railway run .venv\\Scripts\\python.exe migrations\\run_migrations.py",
        "railway run .venv\\Scripts\\python.exe scripts\\check_stripe.py     # read-only",
        "",
        "# deploy is a push — Railway builds main automatically",
        "git push origin main",
    ]:
        w(f"  {line}")
    w("")
    w("-" * 78)
    w("  MIGRATIONS APPLIED, IN ORDER")
    w("-" * 78)
    w("")
    for p in sorted(p for p in text_files if p.startswith("migrations/") and p.endswith(".sql")):
        w(f"  {os.path.basename(p)}")
    w("")
    w("-" * 78)
    w(f"  COMMIT HISTORY — {ncommits} commits")
    w("-" * 78)
    w("")
    for line in run("git", "log", "--format=%ad  %h  %s", "--date=short").splitlines():
        w(f"  {line}")
    w("")
    w(bar)
    w("  END")
    w(bar)

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts) + "\n")

    size = os.path.getsize(OUT)
    print(f"wrote {os.path.basename(OUT)}")
    print(f"  {len(text_files)} files, {total_lines:,} source lines")
    print(f"  {len(parts):,} lines out, {size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
