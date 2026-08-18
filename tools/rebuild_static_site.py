"""Publish only non-empty ADT pages in one consecutive navigation spine."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContentAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.in_content = False
        self.text = []
        self.visual_or_field_count = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if self.in_content:
            self.depth += 1
        elif attributes.get("id") == "content":
            self.in_content = True
            self.depth = 1
        if self.in_content and tag in {"img", "svg", "video", "audio", "canvas", "input", "textarea", "select", "button"}:
            self.visual_or_field_count += 1

    def handle_endtag(self, tag):
        if self.in_content:
            self.depth -= 1
            if self.depth == 0:
                self.in_content = False

    def handle_data(self, data):
        if self.in_content and data.strip():
            self.text.append(data.strip())

    @property
    def empty(self):
        return not re.search(r"[A-Za-z0-9À-ž]", " ".join(self.text)) and self.visual_or_field_count == 0


pages_path = ROOT / "content/pages.json"
pages = json.loads(pages_path.read_text(encoding="utf-8"))
pages[0]["href"] = "pg001_sec001.html"
excluded_sections = {
    "pg005_sec001",  # Its Shukurani content is merged into digital page 4.
    "pg021_sec001",  # Its matching-table rows are merged into page 20 section 2.
    "pg058_sec002",  # Its activity is relocated into page 58 section 1.
}
kept = []
for page in pages:
    if page["section_id"] in excluded_sections:
        continue
    path = ROOT / page["href"]
    if not path.exists():
        continue
    audit = ContentAudit()
    audit.feed(path.read_text(encoding="utf-8"))
    if not audit.empty:
        kept.append(page)

for number, page in enumerate(kept, start=1):
    page["page_number"] = number
    path = ROOT / page["href"]
    html = path.read_text(encoding="utf-8")
    html = re.sub(
        r'(<meta name="page-section-id" content=")\d+("\s*/>)',
        rf"\g<1>{number}\2",
        html,
        count=1,
    )
    path.write_text(html, encoding="utf-8")

pages_path.write_text(json.dumps(kept, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

toc_path = ROOT / "content/toc.json"
toc = json.loads(toc_path.read_text(encoding="utf-8"))
valid_sections = {page["section_id"] for page in kept}
toc = [entry for entry in toc if entry.get("section_id") in valid_sections and (ROOT / entry.get("href", "")).exists()]
page_numbers = {page["section_id"]: page["page_number"] for page in kept}
for entry in toc:
    entry["page_number"] = page_numbers[entry["section_id"]]
toc_path.write_text(json.dumps(toc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Keep the printed contents page aligned with the actual digital navigation spine.
contents_path = ROOT / "pg003_sec001.html"
contents = contents_path.read_text(encoding="utf-8")
contents_ids = {
    "pg004_sec001": "pg003_n0006",
    "pg006_sec001": "pg003_n0009",
    "pg007_sec001": "pg003_n0014",
    "pg023_sec001": "pg003_n0019",
    "pg044_sec001": "pg003_n0024",
    "pg081_sec001": "pg003_n0029",
    "pg097_sec001": "pg003_n0034",
}
for section_id, text_id in contents_ids.items():
    number = page_numbers[section_id]
    contents = re.sub(
        rf'(<[^>]+data-id="{text_id}"[^>]*>)[^<]*(</[^>]+>)',
        rf"\g<1>{number}\2",
        contents,
        count=1,
    )
contents_path.write_text(contents, encoding="utf-8")

manifest_path = ROOT / "imsmanifest.xml"
if manifest_path.exists():
    manifest = manifest_path.read_text(encoding="utf-8")
    if '<file href="pg001_sec001.html"/>' not in manifest:
        manifest = manifest.replace('<file href="index.html"/>', '<file href="index.html"/>\n      <file href="pg001_sec001.html"/>', 1)
        manifest_path.write_text(manifest, encoding="utf-8")

print(f"Published {len(kept)} consecutive non-empty pages.")
