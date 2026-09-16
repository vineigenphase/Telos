"""Push the official ENGAA/NSAA question papers onto the Railway volume.

The PDFs live in `scripts/admissions/documents/`, which is gitignored: they are
18MB of third-party documents and a git repository is the one place they must
not be. So they reach production the same way every other file does — through
an authenticated upload to the running app, which writes to the volume at
STORAGE_DIR/admissions.

    .venv\\Scripts\\python.exe scripts\\upload_admissions_papers.py

It asks for the admin email and password at the terminal. The password is not
echoed, and unlike a flag or an exported variable it never reaches the shell
history or the process list. For an unattended run set TELOS_ADMIN_EMAIL and
TELOS_ADMIN_PASSWORD instead, and it will not prompt.

Defaults to https://telosapp.co.uk; pass --base to aim it somewhere else, which
is how you try it against a local server first. `--dry-run` lists what it would
send and stops without asking for anything.

Only files named TEST_YEAR_S1_QuestionPaper.pdf are sent, because that is the
name the catalogue rebuilds when it looks a paper up. Anything else would land
on the volume with nothing ever linking to it, so it is reported here rather
than uploaded and forgotten.

Re-running is safe: an upload overwrites the file of the same name.
"""
import argparse
import getpass
import os
import re
import sys

try:
    import requests
except ImportError:
    raise SystemExit("requests is not installed in this environment.")

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.environ.get("TELOS_ADMISSIONS_DOCS", os.path.join(HERE, "admissions",
                                                            "documents"))
WANTED = re.compile(r"[A-Za-z]+_[0-9A-Z]+_S1_QuestionPaper\.pdf")

# One file per request. The app sets no MAX_CONTENT_LENGTH, but the proxy in
# front of it is entitled to, and the NSAA papers are not uniform — 2018 alone
# is 6MB against ENGAA 2023's 258KB, so any fixed batch size is either wasteful
# or occasionally enormous. Sixteen small requests also mean a rejection names
# the file that caused it, which one 17MB request would not.
BATCH = 1


def _credentials():
    """Admin email and password — prompted for, rather than taken from argv.

    Asking at the terminal is the default because the alternatives both leak.
    A `--password` flag puts the password in the shell history and in the
    process list; an environment variable put it in the history too, on the
    line that exported it. `getpass` echoes nothing and keeps it in memory for
    the length of one upload.

    The environment is still read first, because a scheduled or piped run has
    no terminal to prompt at and should say so clearly rather than hang.
    """
    email = os.environ.get("TELOS_ADMIN_EMAIL")
    password = os.environ.get("TELOS_ADMIN_PASSWORD")
    if email and password:
        return email, password

    if not sys.stdin.isatty():
        raise SystemExit(
            "no terminal to prompt at. Either run this from a shell, or set "
            "TELOS_ADMIN_EMAIL and TELOS_ADMIN_PASSWORD for an unattended run.")

    email = email or input("admin email: ").strip()
    password = password or getpass.getpass("password (not echoed): ")
    if not (email and password):
        raise SystemExit("both an email and a password are needed.")
    return email, password


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="https://telosapp.co.uk",
                    help="site to upload to (default: production)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be sent and stop")
    args = ap.parse_args(argv)

    if not os.path.isdir(DOCS):
        raise SystemExit(f"no documents directory at {DOCS}")

    files = sorted(f for f in os.listdir(DOCS) if WANTED.fullmatch(f))
    skipped = sorted(f for f in os.listdir(DOCS)
                     if f.lower().endswith(".pdf") and not WANTED.fullmatch(f))

    print(f"{len(files)} question paper(s) to upload from {DOCS}")
    for f in files:
        size = os.path.getsize(os.path.join(DOCS, f)) / 1024
        print(f"  {f:<40} {size:>7.0f} KB")
    if skipped:
        print(f"\nignored ({len(skipped)} file(s) whose names the catalogue "
              f"will never ask for — answer keys live here too):")
        for f in skipped:
            print(f"  {f}")
    if args.dry_run or not files:
        return 0

    email, password = _credentials()

    base = args.base.rstrip("/")
    s = requests.Session()
    r = s.post(f"{base}/login", data={"email": email, "password": password},
               allow_redirects=True, timeout=30)
    # The login page renders 200 on a bad password and redirects on a good one,
    # so the status code alone does not say which happened.
    if "/login" in r.url:
        raise SystemExit("login failed — check the email and password.")

    url = f"{base}/admin/admissions/papers"
    if s.get(url, timeout=30).status_code != 200:
        raise SystemExit(f"{url} did not answer 200 — is that account an admin, "
                         f"and is this build deployed?")

    sent = 0
    for i in range(0, len(files), BATCH):
        batch = files[i:i + BATCH]
        handles = [("papers", (name, open(os.path.join(DOCS, name), "rb"),
                               "application/pdf")) for name in batch]
        try:
            resp = s.post(url, files=handles, timeout=300)
        finally:
            for _, (_, fh, _) in handles:
                fh.close()
        if resp.status_code not in (200, 302):
            print(f"  FAILED batch {batch}: HTTP {resp.status_code}")
            continue
        sent += len(batch)
        print(f"  sent {sent}/{len(files)}")

    print(f"\nuploaded {sent} paper(s). Check {url} for what the volume holds.")
    return 0 if sent == len(files) else 1


if __name__ == "__main__":
    sys.exit(main())
