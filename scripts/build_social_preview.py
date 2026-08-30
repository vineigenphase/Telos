"""Render the social preview card — the image shown when a Telos link is shared.

Two places want it and they want the same picture: GitHub's repository social
preview, and the `og:image` on the landing page, which had no image at all, so
every link to telosapp.co.uk previewed as a blank grey box.

Nothing here is drawn twice. The mark comes from brand.py, which is already the
one definition used by the PWA icons and the share cards; the fonts, palette
and letter-spacing helper come from sharecards.py. A social card is exactly the
kind of asset that gets hand-made once and then drifts from the product's
palette forever, so it is generated from the same tokens as everything else —
change --accent in telos.css and this follows.

1280x640 is GitHub's stated size and a clean 2:1, which is also within what the
Open Graph consumers want. Content is kept well inside the edges because
previews are cropped differently everywhere they appear.

Regenerate with:

    .venv\\Scripts\\python.exe scripts\\build_social_preview.py
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from brand import ACCENT, css_colour, mark_glyph  # noqa: E402
from sharecards import font, tracked  # noqa: E402

OUT = os.path.join(ROOT, "static", "og-preview.png")

W, H = 1280, 640
PAD = 76

BG = css_colour("bg", (11, 11, 12))
TEXT = css_colour("text", (242, 241, 238))
MUTED = css_colour("muted", (113, 112, 107))
BORDER = css_colour("border", (31, 31, 32))
ACCENT_2 = css_colour("accent-2", (224, 190, 85))


def main() -> int:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # A hairline frame, the same device the share cards use — structure from
    # rules and space rather than stacked panels.
    d.rectangle([PAD - 28, PAD - 28, W - PAD + 27, H - PAD + 27],
                outline=BORDER, width=2)

    # ── wordmark ────────────────────────────────────────────────────────────
    g = 52
    glyph = mark_glyph(g, ACCENT)
    img.paste(glyph, (PAD, PAD), glyph)
    tracked(d, (PAD + g + 22, PAD + 9), "TELOS", font("inter", 600, 33), TEXT, 6.5)

    # ── the levels, as an eyebrow ───────────────────────────────────────────
    tracked(d, (W - PAD, PAD + 16), "A-LEVEL · AS · HIGHER · ADVANCED HIGHER",
            font("inter", 600, 21), MUTED, 3.0, anchor_x="right")

    # ── the thesis ──────────────────────────────────────────────────────────
    #
    # The landing page's own headline. A preview that says something different
    # from the page it links to is a preview that has drifted.
    serif = font("serif", 600, 78)
    d.text((PAD, 196), "The marks between you", font=serif, fill=TEXT)
    d.text((PAD, 282), "and the ", font=serif, fill=TEXT)
    w = d.textlength("and the ", font=serif)
    d.text((PAD + w, 282), "next grade.", font=serif, fill=ACCENT_2)

    # ── what it actually does ───────────────────────────────────────────────
    sub = font("inter", 400, 27)
    d.text((PAD, 408),
           "Mark a past paper question by question. Telos finds the topics",
           font=sub, fill=MUTED)
    d.text((PAD, 444),
           "costing you marks and predicts your grade from real boundaries.",
           font=sub, fill=MUTED)

    # ── the facts, bottom rule ──────────────────────────────────────────────
    #
    # The rule sat 26px above the facts and ran straight through the descenders
    # of the line above it. Measured against the actual ink now rather than
    # guessed, with a real gap either side.
    y = H - PAD - 30
    rule_y = 508
    d.line([(PAD, rule_y), (W - PAD, rule_y)], fill=BORDER, width=2)

    # Counted here rather than typed, so the card cannot outlive the numbers.
    import paper_templates as T
    quals = sum(len(subs) for subs in T.TEMPLATES.values())
    tracked(d, (PAD, y), f"{quals} QUALIFICATIONS · AQA · EDEXCEL · OCR · SQA",
            font("inter", 600, 21), MUTED, 3.0)
    tracked(d, (W - PAD, y), "TELOSAPP.CO.UK",
            font("inter", 600, 21), ACCENT_2, 3.4, anchor_x="right")

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {os.path.relpath(OUT, ROOT)}  {W}x{H}  {size:,} bytes")
    if size > 1_000_000:
        print("  NOTE: GitHub's limit is 1MB — this is over it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
