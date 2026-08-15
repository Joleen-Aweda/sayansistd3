"""Verify images are narrated once without requiring the optional image mode."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))
markup = "\n".join((ROOT / page["href"]).read_text(encoding="utf-8") for page in pages)
image_ids = re.findall(r'<img\b[^>]*data-duplicate-id="([^"]+)"', markup)
narrated = re.findall(r'<span\b[^>]*class="[^"]*adt-image-description[^"]*"[^>]*data-id="([^"]+)"', markup)

assert len(image_ids) == 181
assert len(set(image_ids)) == 168
assert len(narrated) == len(set(narrated)) == 168
assert set(narrated) == set(image_ids)
assert all(texts.get(image_id, "").strip() for image_id in narrated)
assert not re.search(r'<img\b[^>]*\bdata-id="', markup)

print("PASS: all 168 unique image descriptions occur once in the normal read-aloud sequence.")
