"""Generate the PWA icon PNGs from the Telos mark.

The mark is a T drawn as one continuous stroked outline — the parallel stem
lines close into the crossbar — sheared 9 degrees so it shares an angle with
the italic "os" in the wordmark. The same geometry is defined for the web in
the `logo` macro in templates/_icons.html; change one and you must change the
other, because nothing enforces it.

Colours are taken from the CSS custom properties rather than restated, so a
palette change cannot leave the icons behind. Re-run after touching either.

Deliberately flat: no gradient and no sheen. The UI brief allows a gradient
only on the logo mark and rules out gloss everywhere, and a stroked outline
reads cleaner solid — the old mosaic-on-gradient icon was built for the
previous purple identity.

Usage: .venv\\Scripts\\python.exe scripts\\generate_icons.py
"""
import math
import os
import re

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "static", "icons")
CSS = os.path.join(HERE, "static", "css", "telos.css")

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
    """Read a --token from telos.css so the icons cannot drift from the UI."""
    try:
        with open(CSS, encoding="utf-8") as fh:
            m = re.search(r"--%s:\s*#([0-9A-Fa-f]{6})" % re.escape(name), fh.read())
        if m:
            h = m.group(1)
            return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except OSError:
        pass
    return fallback


ACCENT = css_colour("accent", (76, 126, 243))
GROUND = css_colour("surface", (12, 13, 16))
EDGE = css_colour("border", (33, 35, 41))


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


def draw_mark(size, box, radius_ratio, opaque=False):
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
    width = max(1, int(STROKE_W * scale))
    # Closed outline: the point list plus its first point again.
    d.line(pts + [pts[0]], fill=(*ACCENT, 255), width=width, joint="curve")
    # `joint="curve"` rounds interior joins but leaves the start/end butt, so
    # the closing corner gets a dot to match.
    r = width / 2
    d.ellipse([pts[0][0] - r, pts[0][1] - r, pts[0][0] + r, pts[0][1] + r],
              fill=(*ACCENT, 255))

    img = img.resize((size, size), Image.LANCZOS)
    if opaque:
        flat = Image.new("RGB", (size, size), GROUND)
        flat.paste(img, (0, 0), img)
        return flat
    return img


def write(img, name):
    img.save(os.path.join(OUT, name))
    print("wrote", name)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write(draw_mark(192, 0.22, 0.25), "icon-192.png")
    write(draw_mark(512, 0.22, 0.25), "icon-512.png")
    # Maskable: full bleed, mark pulled into the ~80% safe zone so Android's
    # own mask cannot crop it.
    write(draw_mark(512, 0.30, 0.0), "maskable-512.png")
    # Apple ignores alpha and applies its own rounding, so ship it opaque.
    write(draw_mark(180, 0.24, 0.0, opaque=True), "apple-touch-180.png")
