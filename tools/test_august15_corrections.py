"""Verify the August 15 wording, descriptions, contents and Shukurani merge."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
toc = json.loads((ROOT / "content/toc.json").read_text(encoding="utf-8"))
texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))

assert len(pages) == 151
assert not any(page["section_id"] == "pg005_sec001" for page in pages)
assert pages[3]["section_id"] == "pg004_sec001" and pages[3]["page_number"] == 4
assert pages[4]["section_id"] == "pg006_sec001" and pages[4]["page_number"] == 5

page_four = (ROOT / "pg004_sec001.html").read_text(encoding="utf-8")
for text_id in ("pg004_n0027", "pg004_n0028", "pg004_im001", "pg004_n0030", "pg004_n0031", "pg004_n0032"):
    assert f'data-id="{text_id}"' in page_four
assert "K Desktop Environment (KDE)" in html.unescape(page_four)
assert "KDesktop Environment" not in page_four
for abbreviation in ("Dkt.", "Bw.", "Bi."):
    assert abbreviation in page_four

number_by_section = {page["section_id"]: page["page_number"] for page in pages}
assert all(entry["page_number"] == number_by_section[entry["section_id"]] for entry in toc)
chapter_pages = {
    "pg003_n0006": "4", "pg003_n0009": "5", "pg003_n0014": "6",
    "pg003_n0019": "27", "pg003_n0024": "57", "pg003_n0029": "109", "pg003_n0034": "130",
}
for text_id, number in chapter_pages.items():
    assert texts[text_id] == number

all_markup = "\n".join((ROOT / page["href"]).read_text(encoding="utf-8") for page in pages)
assert not re.search(r"\bNa\.?(?=\s|<|$)", all_markup)
assert not any(re.search(r"\bNa\.?(?=\s|$)", value) for value in texts.values())
page_ten = (ROOT / "pg010_sec002.html").read_text(encoding="utf-8")
assert "kila picha a mpaka de." in page_ten
assert texts["pg010_n0008"] == "Jaza jedwali lifuatalo kwa kueleza tendo la kisayansi lililooneshwa kwa kila picha a mpaka de."
assert texts["pg010_n0012"].lower() == "namba"

image_ids = set()
for match in re.finditer(r'<img\b[^>]*\bdata-(?:duplicate-)?id="([^"]+)"[^>]*>', all_markup, flags=re.I):
    image_id = match.group(1)
    image_ids.add(image_id)
    alt = re.search(r'alt="([^"]+)"', match.group(0))
    assert alt and html.unescape(alt.group(1)) == texts[image_id]
    assert texts[image_id].startswith(("Picha inaonesha ", "Mchoro unaonesha ", "Kielelezo namba "))

assert len(image_ids) == 167
assert sum(texts[image_id].startswith("Kielelezo namba ") for image_id in image_ids) == 127
print("PASS: namba wording, 167 Swahili image descriptions (127 numbered figures), digital contents and merged pages are synchronized.")
