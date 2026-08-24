"""The Telos mark, and the palette, as the one place Python renders them.

The T is a single continuous stroked outline — the parallel stem lines close
into the crossbar — sheared 9 degrees so it shares an angle with the italic
"os" in the wordmark.

That geometry now has two definitions, not three: this module for anything
rendered server-side (PWA icons, share cards), and the `logo` macro in
templates/_icons.html for the web. Nothing enforces agreement between those
two, so change one and you must change the other. This module exists because
Phase 9 needed the mark a third time and a third hand-maintained copy was
one too many.

Colours are read from the CSS custom properties rather than restated, so a
palette change cannot leave the rendered assets behind.
"""
import math
import os
import re

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = os.path.join(HERE, "static", "css", "telos.css")
FONTS = os.path.join(HERE, "static", "fonts")

# Supersample factor. PIL has no antialiased stroking, so everything is drawn
# large and reduced with LANCZOS — without this the sheared diagonals crawl.
SS = 8

# The mark in its 32x32 design box, before shearing (matches the SVG path
# "M4 6 H28 V11 H18.6 V27 H13.4 V11 H4 Z").
T_POINTS = [(4, 6), (28, 6), (28, 11), (18.6, 11),
            (18.6, 27), (13.4, 27), (13.4, 11), (4, 11)]
SHEAR_DEG = 9.0
STROKE_W = 2.1          # in design-box units, as in the SVG


def css_colour(name, fallback):
    """Read a --token from telos.css so rendered assets cannot drift."""
    try:
        with open(CSS, encoding="utf-8") as fh:
            m = re.search(r"--%s:\s*#([0-9A-Fa-f]{6})" % re.escape(name), fh.read())
        if m:
            h = m.group(1)
            return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except OSError:
        pass
    return fallback


# Fallbacks are the shipped Editorial values, not the blue from the original
# brief — if telos.css ever goes missing the assets should still come out warm.
ACCENT = css_colour("accent", (201, 162, 39))
GROUND = css_colour("surface", (13, 13, 14))
EDGE = css_colour("border", (31, 31, 32))


def sheared_points(box, size):
    """Shear the T, then fit it to `box` (a fraction of `size` as margin).

    The shear is applied first and the result re-centred on its own bounding
    box; skewing after centring would push the mark off to one side.
    """
    t = math.tan(math.radians(-SHEAR_DEG))
    pts = [(x + t * y, y) for x, y in T_POINTS]

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)

    avail = size * (1 - 2 * box)
    scale = avail / max(w, h)
    ox = size * box + (avail - w * scale) / 2 - min(xs) * scale
    oy = size * box + (avail - h * scale) / 2 - min(ys) * scale
    return [(x * scale + ox, y * scale + oy) for x, y in pts], scale


def _stroke(d, pts, scale, colour):
    """Draw the closed outline. Shared so the icons and the cards can't differ."""
    width = max(1, int(STROKE_W * scale))
    d.line(pts + [pts[0]], fill=(*colour, 255), width=width, joint="curve")
    # `joint="curve"` rounds interior joins but leaves the start/end butt, so
    # the closing corner gets a dot to match.
    r = width / 2
    d.ellipse([pts[0][0] - r, pts[0][1] - r, pts[0][0] + r, pts[0][1] + r],
              fill=(*colour, 255))


def mark_glyph(size, colour=ACCENT, box=0.0):
    """The bare stroked T on transparency, for compositing onto a card."""
    big = size * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    pts, scale = sheared_points(box, big)
    _stroke(ImageDraw.Draw(img), pts, scale, colour)
    return img.resize((size, size), Image.LANCZOS)


def draw_mark(size, box, radius_ratio, opaque=False):
    """The mark on its dark plate, as the PWA icons want it."""
    big = size * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Ground. A dark plate, matching the app's own chrome — the mark is a thin
    # stroke, and on a light home screen a transparent ground would leave it
    # floating with nothing to read against.
    d.rounded_rectangle([0, 0, big - 1, big - 1],
                        radius=int(big * radius_ratio),
                        fill=(*GROUND, 255))
    if radius_ratio > 0:
        # A hairline edge so the plate separates from a black wallpaper.
        d.rounded_rectangle([0, 0, big - 1, big - 1],
                            radius=int(big * radius_ratio),
                            outline=(*EDGE, 255), width=max(1, int(big * 0.006)))

    pts, scale = sheared_points(box, big)
    _stroke(d, pts, scale, ACCENT)

    img = img.resize((size, size), Image.LANCZOS)
    if opaque:
        flat = Image.new("RGB", (size, size), GROUND)
        flat.paste(img, (0, 0), img)
        return flat
    return img
