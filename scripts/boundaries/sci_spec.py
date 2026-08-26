"""Pull content headings and the paper mapping from an AQA science spec."""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pypdf import PdfReader

SP = DOCS


def load(name):
    lines = []
    for pg in PdfReader(os.path.join(SP, name)).pages:
        lines += (pg.extract_text() or "").splitlines()
    return [l.encode("utf-8", "replace").decode("utf-8") for l in lines]


def headings(lines, depth):
    """Numbered content headings at the requested depth, e.g. 3.1.2."""
    pat = re.compile(r"^\s*(3(?:\.\d+){%d})\s+([A-Z][^\d]{2,60}?)\s*$" % (depth - 1,))
    seen, out = set(), []
    for l in lines:
        m = pat.match(l)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append((m.group(1), re.sub(r"\s+", " ", m.group(2)).strip()))
    return out


if __name__ == "__main__":
    for label, fname in (("BIOLOGY", "aqa_bio_spec.pdf"), ("CHEMISTRY", "aqa_chem_spec.pdf")):
        lines = load(fname)
        print(f"########## {label} ##########")
        print("--- top level (3.x) ---")
        for num, name in headings(lines, 2):
            print(f"   {num:<8}{name}")
        print(f"--- second level (3.x.y): {len(headings(lines, 3))} found ---")
        for num, name in headings(lines, 3)[:8]:
            print(f"   {num:<8}{name}")
        # What each paper assesses.
        idx = [i for i, l in enumerate(lines) if "assessed" in l.lower() and "What" in l]
        print(f"--- assessment blocks at {idx[:4]} ---")
        for i in idx[:3]:
            for k in range(i - 2, min(len(lines), i + 10)):
                s = lines[k].strip()
                if s:
                    print("   ", s[:70])
            print("   ---")
        print()
