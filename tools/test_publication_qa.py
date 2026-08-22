"""Cross-book publication checks for the corrected Swahili bundle."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))

version = json.loads((ROOT / "assets/config.json").read_text(encoding="utf-8"))["bundleVersion"]
assert version == "188"
assert pages[0]["href"] == "pg001_sec001.html"
assert [item["page_number"] for item in pages] == list(range(1, 110)) + list(range(111, 150))
assert len(pages) == 148
assert "pg021_sec001" not in {item["section_id"] for item in pages}

for item in pages:
    markup = (ROOT / item["href"]).read_text(encoding="utf-8")
    assert re.search(rf'<meta name="page-section-id" content="{item["page_number"]}"\s*/?>', markup), item["href"]
    assert f"offline-preloader.js?v={version}" in markup, item["href"]
    assert not re.search(r'<img\b[^>]+src="https?://', markup), item["href"]
    for image_src in re.findall(r'<img\b[^>]+src=["\'](images/[^"\']+)', markup, flags=re.I):
        clean_src = image_src.split("?", 1)[0]
        assert (ROOT / clean_src).is_file(), (item["href"], clean_src)
        assert image_src.endswith(f"?v={version}"), (item["href"], image_src)

all_markup = "\n".join((ROOT / item["href"]).read_text(encoding="utf-8") for item in pages)
assert not re.search(r"\bAngalia\b", all_markup, flags=re.I)
assert "FOR ONLINE READING ONLY" not in all_markup
assert not re.search(r"\bKazi ya kufanya \d+\b", all_markup, flags=re.I)
assert "FOR ONLINE READING ONLY" not in (ROOT / "pg037_sec001.html").read_text(encoding="utf-8")
page20 = (ROOT / "pg020_sec001.html").read_text(encoding="utf-8")
assert page20.count("<line ") == 7

for key in ("pg001_im001", "pg004_im001", "pg006_im001"):
    assert key in texts and len(texts[key].split()) >= 3

page2 = (ROOT / "pg002_sec001.html").read_text(encoding="utf-8")
assert page2.index('data-id="pg002_n0017"') < page2.index('data-id="pg002_n0003"')
assert texts["pg002_n0017"] == "I. S. B. N."
assert texts["pg002_n0003"] == "978-9987-09-952-8"

page8_instruction = "Chunguza kielelezo namba 2 na andika unachokiona / ulichokichunguza"
page8 = (ROOT / "pg008_sec002.html").read_text(encoding="utf-8")
assert page8_instruction in page8
assert texts["pg008_n0017"] == page8_instruction
assert texts["pg008_n0017_easy_read"] == page8_instruction
for language in ("sw", "sw-TZ"):
    language_texts = json.loads(
        (ROOT / f"content/i18n/{language}/texts.json").read_text(encoding="utf-8")
    )
    language_audios = json.loads(
        (ROOT / f"content/i18n/{language}/audios.json").read_text(encoding="utf-8")
    )
    assert language_texts["pg008_n0017"] == page8_instruction
    assert language_audios["pg008_n0017"] == "pg008_n0017.mp3?v=188"
    assert language_audios["pg008_n0017_easy_read"] == "pg008_n0017_easy_read.mp3?v=188"

print(f"PASS: 148-section version {version} publication order, local assets, inclusive wording and key diagrams are valid.")
