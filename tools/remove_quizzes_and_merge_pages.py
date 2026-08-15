#!/usr/bin/env python3
"""Remove quiz pages and consolidate the two requested split pages."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOVED_SECTIONS = {"pg022_sec001", "pg023_sec002"}

pages_path = ROOT / "content/pages.json"
pages = json.loads(pages_path.read_text(encoding="utf-8"))
pages = [
    item for item in pages
    if not item["section_id"].startswith("qz")
    and item["section_id"] not in REMOVED_SECTIONS
]
for index, item in enumerate(pages, 1):
    item["page_number"] = index
pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

page_number_by_section = {item["section_id"]: item["page_number"] for item in pages}
for index, item in enumerate(pages, 1):
    path = ROOT / item["href"]
    markup = path.read_text(encoding="utf-8")
    markup, count = re.subn(
        r'(<meta name="page-section-id" content=")\d+("\s*/?>)',
        rf"\g<1>{index}\2",
        markup,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"Could not renumber {path.name}")
    path.write_text(markup, encoding="utf-8")

toc_path = ROOT / "content/toc.json"
toc = json.loads(toc_path.read_text(encoding="utf-8"))

def clean_toc(value):
    if isinstance(value, list):
        cleaned = []
        for item in value:
            if isinstance(item, dict):
                section_id = item.get("section_id", "")
                if section_id.startswith("qz") or section_id in REMOVED_SECTIONS:
                    continue
            cleaned.append(clean_toc(item))
        return cleaned
    if isinstance(value, dict):
        cleaned = {key: clean_toc(item) for key, item in value.items()}
        section_id = cleaned.get("section_id")
        if section_id in page_number_by_section:
            cleaned["page_number"] = page_number_by_section[section_id]
        return cleaned
    return value

toc_path.write_text(json.dumps(clean_toc(toc), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for language in ("sw", "sw-TZ"):
    base = ROOT / "content/i18n" / language
    for filename in ("texts.json", "audios.json"):
        path = base / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        data = {key: value for key, value in data.items() if not key.startswith("qz")}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for audio in (base / "audio").glob("qz*.mp3"):
        audio.unlink()

for page in ROOT.glob("qz*.html"):
    page.unlink()
for section_id in REMOVED_SECTIONS:
    (ROOT / f"{section_id}.html").unlink(missing_ok=True)

print(f"Published {len(pages)} consolidated pages with no quizzes.")
