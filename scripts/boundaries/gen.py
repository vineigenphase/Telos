
import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import json, pathlib

SP = pathlib.Path(DOCS)
d = json.loads((SP / "cards.json").read_text())

def img(k, cls):
    return f'<img class="{cls}" src="data:image/png;base64,{d[k]}" alt="{k} render" loading="lazy">'

sections = [
    ("grade", "Predicted grade", d["grade-title"],
     "The Pro card, and the one with the most reach &mdash; a grade is the thing a student actually "
     "wants to show. Where a next boundary exists it carries the most shareable sentence Telos can "
     "produce: <em>6 marks from an A*</em>. This render sits at A* already, so there is no next grade "
     "and the line correctly doesn't appear."),
    ("heatmap", "Accuracy", d["heatmap-title"],
     "The grid is texture that says <em>this is measured</em> &mdash; no labels, because a topic name "
     "small enough to fit is a name nobody reads in a feed. On the square card the layout walks a "
     "ladder: grid rows and whether strongest and weakest get a line each both flex, and dropping the "
     "grid is the last resort."),
    ("milestone", "Papers logged", d["milestone-title"],
     "The only card a brand-new free account can make, which is the point &mdash; it works from the "
     "first paper logged. The spec also names a <em>streak</em> card; nothing in Telos tracks "
     "consecutive days, so that is flagged rather than faked, and the renderer keeps a day-streak path "
     "for whenever something computes one."),
]

blocks = []
for key, label, title, note in sections:
    blocks.append(f'''  <section class="card-section">
    <header class="section-head">
      <h2 class="section-title">{label}</h2>
      <p class="section-render">{title}</p>
    </header>
    <div class="renders">
      <figure class="render">
        {img(key + "-story", "shot shot-story")}
        <figcaption>Story <span class="dim">1080 &times; 1920</span></figcaption>
      </figure>
      <figure class="render">
        {img(key + "-post", "shot shot-post")}
        <figcaption>Post <span class="dim">1080 &times; 1080</span></figcaption>
      </figure>
    </div>
    <p class="note">{note}</p>
  </section>''')

TEMPLATE = pathlib.Path(SP / "template.html").read_text(encoding="utf-8")
html = TEMPLATE.replace("__SECTIONS__", "\n\n".join(blocks))
out = SP / "share-cards-review.html"
out.write_text(html, encoding="utf-8")
print("written:", out, len(html) // 1024, "KB")
