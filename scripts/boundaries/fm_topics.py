"""Pull the topic-area headings for each OCR H245 component from the spec.

Within each content section OCR numbers its topic areas "1.01 Proof",
"1.02 Complex numbers" and so on, restarting per component. The name is
sometimes on the same line as the number and sometimes on the next.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

SP = DOCS
lines = open(os.path.join(SP, "ocr_fm_spec.txt"), encoding="utf-8").read().splitlines()

SECTIONS = [("Y540/Y541 Pure Core", 969, 2027), ("Y542 Statistics", 2027, 2619),
            ("Y543 Mechanics", 2619, 3014), ("Y544 Discrete", 3014, 3642),
            ("Y545 Additional Pure", 3642, 4125)]

HEAD = re.compile(r"^\s*(\d{1,2}\.\d{2})[\s\t]+(.*)$")

for name, lo, hi in SECTIONS:
    seen, topics = set(), []
    for i in range(lo, min(hi, len(lines))):
        m = HEAD.match(lines[i].replace("\t", " "))
        if not m:
            continue
        num, rest = m.group(1), m.group(2).strip()
        if not rest and i + 1 < len(lines):
            rest = lines[i + 1].replace("\t", " ").strip()
        rest = re.sub(r"\s+", " ", rest)
        # Topic headings are short title-case phrases; sub-items are sentences.
        if (rest and num not in seen and 3 <= len(rest) <= 44
                and rest[0].isupper() and not rest.endswith(".")):
            seen.add(num)
            topics.append(rest)
    print(f"{name}:")
    for t in topics:
        print(f"    {t}")
    print()
