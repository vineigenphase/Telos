r"""Generate the PWA icon PNGs from the Telos mark.

The geometry, the palette lookup and the drawing all live in brand.py, which
this and the Phase 9 share-card renderer share — see that module for why. This
script is now just the sizes and the output names.

Deliberately flat: no gradient and no sheen. The UI brief allows a gradient
only on the logo mark and rules out gloss everywhere, and a stroked outline
reads cleaner solid — the old mosaic-on-gradient icon was built for the
previous purple identity.

Usage: .venv\Scripts\python.exe scripts\generate_icons.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brand import draw_mark  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "static", "icons")


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
