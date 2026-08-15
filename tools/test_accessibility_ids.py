"""Audit unique IDs, image descriptions and narration mappings in the published spine."""

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
LANGUAGES = ("sw", "sw-TZ")


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.duplicate_ids = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("data-id"):
            self.ids.append(values["data-id"])
        if values.get("data-duplicate-id"):
            self.duplicate_ids.append(values["data-duplicate-id"])
        if tag == "img":
            self.images.append(values)


seen = {}
image_count = 0
for language in LANGUAGES:
    texts = json.loads((ROOT / f"content/i18n/{language}/texts.json").read_text(encoding="utf-8"))
    audios = json.loads((ROOT / f"content/i18n/{language}/audios.json").read_text(encoding="utf-8"))
    for entry in PAGES:
        page = ROOT / entry["href"]
        parser = Parser()
        parser.feed(page.read_text(encoding="utf-8"))
        if language == LANGUAGES[0]:
            for text_id in parser.ids:
                assert text_id not in seen, f"duplicate data-id {text_id}: {seen.get(text_id)} and {page.name}"
                seen[text_id] = page.name
        for text_id in parser.ids + parser.duplicate_ids:
            assert text_id in texts, f"missing {language} text for {text_id} in {page.name}"
            assert text_id in audios, f"missing {language} narration mapping for {text_id} in {page.name}"
        for image in parser.images:
            if language == LANGUAGES[0]:
                image_count += 1
            text_id = image.get("data-id") or image.get("data-duplicate-id")
            assert text_id, f"meaningful image without data ID in {page.name}: {image.get('src')}"
            assert image.get("alt", "").strip(), f"image without Swahili description in {page.name}: {image.get('src')}"
            assert image["alt"].strip() == texts[text_id], f"image description mismatch for {text_id}"
            assert len(texts[text_id].split()) >= 3, f"image description too short for {text_id}"

print(f"PASS: {len(seen)} unique narration IDs and {image_count} described images are synchronized.")
