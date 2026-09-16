"""Push the official ENGAA/NSAA question papers onto the Railway volume.

The PDFs live in `scripts/admissions/documents/`, which is gitignored: they are
18MB of third-party documents and a git repository is the one place they must
not be. So they reach production the way every other file does — through an
authenticated upload to the running app, which writes to STORAGE_DIR/admissions
on the volume.

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

Standard library only, deliberately. This first shipped importing `requests`,
which is installed in .venv and not in the system Python — so running it as
`python scripts\\upload_admissions_papers.py` rather than with the venv's
interpreter exited on the import guard before making a single request, and
looked from the outside exactly like an upload that had worked. `mailer.py`
posts to Resend over urllib for the same reason. requirements.txt is seven
pinned dependencies and this is not going to be the eighth.
"""
import argparse
import getpass
import http.cookiejar
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

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


def _opener():
    """A urllib opener that keeps cookies, which is all a session needs here."""
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def _post_form(opener, url, fields, timeout=30):
    """POST an ordinary urlencoded form. Returns (final_url, status, body)."""
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.geturl(), r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.geturl(), e.code, e.read()


def _post_files(opener, url, field, paths, timeout=300):
    """POST files as multipart/form-data, all under the same field name.

    Written out by hand because the standard library has no multipart encoder.
    It is about twenty lines and they are the same twenty lines every time: a
    boundary that does not occur in the payload, one part per file, and CRLF
    line endings because the format says CRLF and some servers mean it.
    """
    boundary = "----telos" + uuid.uuid4().hex
    body = bytearray()
    for path in paths:
        name = os.path.basename(path)
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        body += f"--{boundary}\r\n".encode()
        body += (f'Content-Disposition: form-data; name="{field}"; '
                 f'filename="{name}"\r\n').encode()
        body += f"Content-Type: {ctype}\r\n\r\n".encode()
        with open(path, "rb") as fh:
            body += fh.read()
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(body)))
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _get(opener, url, timeout=30):
    try:
        with opener.open(url, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


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
              f"will never ask for — the answer keys live here too):")
        for f in skipped:
            print(f"  {f}")
    if args.dry_run or not files:
        return 0

    email, password = _credentials()
    base = args.base.rstrip("/")
    opener = _opener()

    # The login page renders 200 on a bad password and redirects on a good one,
    # so the status code alone does not say which happened.
    final_url, _status, _body = _post_form(opener, f"{base}/login",
                                           {"email": email, "password": password})
    if "/login" in final_url:
        raise SystemExit("login failed — check the email and password.")
    print(f"\nsigned in at {base}")

    url = f"{base}/admin/admissions/papers"
    status, _ = _get(opener, url)
    if status != 200:
        raise SystemExit(
            f"{url} answered {status}, not 200. Either that account is not an "
            f"admin, or this build is not deployed yet.")

    sent, failed = 0, []
    for i in range(0, len(files), BATCH):
        batch = files[i:i + BATCH]
        status, _body = _post_files(
            opener, url, "papers", [os.path.join(DOCS, n) for n in batch])
        if status not in (200, 302):
            failed.extend(batch)
            print(f"  FAILED  {', '.join(batch)}  (HTTP {status})")
            continue
        sent += len(batch)
        print(f"  sent {sent}/{len(files)}  {batch[0] if BATCH == 1 else ''}")

    print(f"\nuploaded {sent} of {len(files)} paper(s).")
    if failed:
        print("failed: " + ", ".join(failed))
    print(f"Check {url} for what the volume now holds.")
    return 0 if sent == len(files) else 1


if __name__ == "__main__":
    sys.exit(main())
