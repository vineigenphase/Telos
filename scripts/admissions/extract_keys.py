"""Extract the official answer keys, and refuse to emit one that does not check out.

This is the same discipline as the boundary loaders: the structure derived from
the question papers says exactly how many answers each key must contain, so a
mis-parsed key is caught here rather than silently mis-marking a student's
sitting for the rest of time.

Every key must satisfy all four:

  * the answer count matches what the question paper's cover states;
  * question numbers are contiguous from 1, with no gaps or repeats;
  * every answer is a single letter in A-H (ENGAA runs to H on some questions,
    which is why this is not A-E);
  * no question carries two different answers.

A key that fails any of them is reported and NOT written. Half a key is worse
than none, because it looks like data.

Run:  .venv\\Scripts\\python.exe scripts\\admissions\\extract_keys.py
Needs pypdf, installed for the run and uninstalled after — the app never parses
a PDF.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.environ.get("TELOS_ADMISSIONS_DOCS", os.path.join(HERE, "documents"))
OUT = os.path.join(HERE, "answer_keys.json")

# From the question papers themselves — see derive_structure.py. The parts are
# listed so a key can be split back into the parts a student actually sat.
STRUCTURE = {
    "ENGAA": {
        **{y: [("Part A", 28), ("Part B", 26)] for y in range(2016, 2019)},
        **{y: [("Part A", 20), ("Part B", 20)] for y in range(2019, 2024)},
    },
    "NSAA": {
        **{y: [("Part A", 18), ("Part B", 18), ("Part C", 18),
               ("Part D", 18), ("Part E", 18)] for y in range(2016, 2020)},
        **{y: [("Part A", 20), ("Part B", 20), ("Part C", 20),
               ("Part D", 20)] for y in range(2020, 2024)},
    },
}

# Three layouts across the eight years, so the number may be bare or
# Q-prefixed, and may be followed by the part it belongs to:
#
#   2016-2019   "1G", "10 D"                bare, no labels
#   2020        "Q1 D"                      Q-prefixed, single column
#   2021-2023   "Q1 E MATH  Q41 F CHEM"     two columns, WITH part labels
PAIR = re.compile(r"\bQ?(\d{1,3})\s*([A-H])\b(?:\s+(MATH|PHYS|CHEM|BIOL|BIO))?")
VALID = set("ABCDEFGH")

# The paper's own label for each part, where it prints one. Used to CHECK the
# positional split rather than replace it — see check().
LABEL_TO_PART = {
    "MATH": "Part A", "PHYS": "Part B", "CHEM": "Part C",
    "BIOL": "Part D", "BIO": "Part D",
}


def text_of(path):
    from pypdf import PdfReader
    return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)


def parse(path):
    """[(n, letter, label_or_None), ...] in the order they appear."""
    text = re.sub(r"[ \t]+", " ", text_of(path))
    out = []
    for m in PAIR.finditer(text):
        n, letter, label = int(m.group(1)), m.group(2), m.group(3)
        if 1 <= n <= 200 and letter in VALID:
            out.append((n, letter, label))
    return out


def check(name, pairs, parts):
    """Return (answers, problems). `answers` is {question_number: letter}."""
    expected = sum(n for _, n in parts)
    problems = []

    answers, clashes, labels = {}, [], {}
    for n, letter, label in pairs:
        if n in answers and answers[n] != letter:
            clashes.append((n, answers[n], letter))
        answers[n] = letter
        if label:
            labels[n] = LABEL_TO_PART.get(label.upper())

    if clashes:
        problems.append(f"{len(clashes)} question(s) given two different answers: "
                        f"{clashes[:3]}")
    if len(answers) != expected:
        problems.append(f"found {len(answers)} answers, the paper states {expected}")

    if answers:
        want = set(range(1, expected + 1))
        missing = sorted(want - set(answers))
        extra = sorted(set(answers) - want)
        if missing:
            problems.append(f"missing question numbers: {missing[:8]}"
                            f"{' ...' if len(missing) > 8 else ''}")
        if extra:
            problems.append(f"question numbers beyond the paper: {extra[:8]}"
                            f"{' ...' if len(extra) > 8 else ''}")
    else:
        problems.append("no answers parsed at all")

    # Where the paper labels its own parts, the positional split has to agree
    # with them. This is the second source: if the key says Q41 is CHEM while
    # position says Part B, the assumption is wrong, not the paper.
    if labels and not problems:
        i, disagree = 1, []
        for code, n in parts:
            for q in range(i, i + n):
                if labels.get(q) and labels[q] != code:
                    disagree.append((q, code, labels[q]))
            i += n
        if disagree:
            problems.append("the paper's own part labels disagree with the "
                            f"positional split: {disagree[:4]}")

    return answers, problems


def split_parts(answers, parts):
    """Cut a flat 1..N key into the parts the paper is actually made of."""
    out, i = {}, 1
    for code, n in parts:
        out[code] = [answers[q] for q in range(i, i + n)]
        i += n
    return out


def main():
    if not os.path.isdir(DOCS):
        print(f"no documents directory at {DOCS}", file=sys.stderr)
        return 1

    good, bad = {}, []
    for f in sorted(os.listdir(DOCS)):
        m = re.match(r"(ENGAA|NSAA)_(\d{4})_S1_AnswerKey\.pdf$", f)
        if not m:
            continue
        test, year = m.group(1), int(m.group(2))
        parts = STRUCTURE[test][year]

        pairs = parse(os.path.join(DOCS, f))
        answers, problems = check(f, pairs, parts)

        total = sum(n for _, n in parts)
        if problems:
            bad.append((f, problems))
            print(f"REJECT  {test} {year}  ({len(answers)}/{total})")
            for p in problems:
                print(f"          {p}")
            continue

        good[f"{test} {year}"] = {
            "test": test, "year": str(year), "total": total,
            "parts": split_parts(answers, parts),
        }
        dist = {}
        for letter in answers.values():
            dist[letter] = dist.get(letter, 0) + 1
        print(f"OK      {test} {year}  {total} answers  "
              f"{' '.join(f'{k}:{dist[k]}' for k in sorted(dist))}")

    print(f"\n{len(good)} keys verified, {len(bad)} rejected")
    if bad:
        print("Nothing written — fix the rejects first. A half-parsed key "
              "mis-marks every sitting that uses it.", file=sys.stderr)
        return 1

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(good, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
