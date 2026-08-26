
import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from ocr_as_extract import extract

data, _ = extract("AS GCE Mathematics A", {"H230 01": 75, "H230 02": 75})
for (c, y) in sorted(data, key=lambda k: (k[1], k[0])):
    print(y, c, data[(c, y)])
print()
data, _ = extract("AS GCE Further Mathematics A",
                  {"Y531": 60, "Y532": 60, "Y533": 60, "Y534": 60, "Y535": 60})
for (c, y) in sorted(data, key=lambda k: (k[1], k[0])):
    if y in ("2023", "2024"):
        print(y, c, data[(c, y)])
