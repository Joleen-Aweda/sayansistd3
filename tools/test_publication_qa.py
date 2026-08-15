"""Cross-book publication checks for the corrected Swahili bundle."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))

assert json.loads((ROOT / "assets/config.json").read_text(encoding="utf-8"))["bundleVersion"] == "24"
assert pages[0]["href"] == "pg001_sec001.html"
assert [item["page_number"] for item in pages] == list(range(1, len(pages) + 1))
assert len(pages) == 186

for index, item in enumerate(pages, 1):
    markup = (ROOT / item["href"]).read_text(encoding="utf-8")
    assert re.search(rf'<meta name="page-section-id" content="{index}"\s*/?>', markup), item["href"]
    assert "offline-preloader.js?v=24" in markup, item["href"]
    assert not re.search(r'<img\b[^>]+src="https?://', markup), item["href"]

all_markup = "\n".join((ROOT / item["href"]).read_text(encoding="utf-8") for item in pages)
assert not re.search(r"\bAngalia\b", all_markup, flags=re.I)
assert "FOR ONLINE READING ONLY" not in (ROOT / "pg037_sec001.html").read_text(encoding="utf-8")
assert (ROOT / "pg020_sec001.html").read_text(encoding="utf-8").count("<line ") == 7

for key in ("pg001_im001", "pg005_im001", "pg006_im001"):
    assert key in texts and len(texts[key].split()) >= 3

print("PASS: 186-page version 24 publication order, local assets, inclusive wording and key diagrams are valid.")
