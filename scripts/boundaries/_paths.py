"""Where the awarding bodies' documents live, and where output goes.

The documents themselves are not in the repository: they are ~60MB of PDFs and
spreadsheets that belong to the boards, and every one of them is a stable public
URL recorded in README.md. Download them into `documents/` (gitignored) or point
TELOS_BOUNDARY_DOCS somewhere else.

Nothing here writes to the database. A generator reads documents and writes a
migration; applying it is a separate, deliberate step.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

DOCS = os.environ.get("TELOS_BOUNDARY_DOCS") or os.path.join(HERE, "documents")
MIGRATIONS = os.path.join(REPO, "migrations")


def require_docs():
    """Fail with something readable rather than a stack trace on a missing file."""
    if not os.path.isdir(DOCS):
        raise SystemExit(
            "No document directory at %s.\n"
            "Download the board documents listed in scripts/boundaries/README.md,\n"
            "or set TELOS_BOUNDARY_DOCS to where they already are." % DOCS)
    return DOCS
