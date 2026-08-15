"""Apply wording, merged-Shukurani and complete Swahili image-description corrections."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("sw", "sw-TZ")
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
published = [ROOT / entry["href"] for entry in pages]

# Spell the table abbreviation out consistently in every visible fallback.
for path in published:
    markup = path.read_text(encoding="utf-8")
    markup = re.sub(r"\bNa\.?(?=\s|<|$)", "namba", markup)
    path.write_text(markup, encoding="utf-8")

new_page_four = {
    "pg004_n0027": "Vilevile, TET inatoa shukurani kwa walimu wote wa shule za msingi na wanafunzi walioshiriki katika ujaribishaji wa kitabu hiki.",
    "pg004_n0028": "Mwisho, TET inaishukuru Serikali ya Jamhuri ya Muungano wa Tanzania kwa kutoa fedha zilizofanikisha kazi ya uandishi na uchapaji wa kitabu hiki.",
    "pg004_im001": "Picha inaonesha sahihi ya Dkt. Aneth A. Komba.",
    "pg004_n0030": "Dkt. Aneth A. Komba",
    "pg004_n0031": "Mkurugenzi Mkuu",
    "pg004_n0032": "Taasisi ya Elimu Tanzania",
}

used_image_ids = set()
for path in published:
    markup = path.read_text(encoding="utf-8")
    used_image_ids.update(re.findall(r'<img\b[^>]*\bdata-(?:duplicate-)?id="([^"]+)"', markup, flags=re.I))


def full_description(value: str) -> str:
    value = re.sub(r"\s+", " ", html.unescape(value)).strip().rstrip(".")
    if value.lower().startswith(("picha inaonesha ", "mchoro unaonesha ")):
        return value + "."
    if not value:
        return value
    first = value[0].lower() + value[1:]
    return f"Picha inaonesha {first}."


for lang in LANGUAGES:
    texts_path = ROOT / f"content/i18n/{lang}/texts.json"
    texts = json.loads(texts_path.read_text(encoding="utf-8"))
    for key, value in list(texts.items()):
        texts[key] = re.sub(r"\bNa\.?(?=\s|$)", "namba", value)
    texts.update(new_page_four)
    for image_id in used_image_ids:
        texts[image_id] = full_description(texts.get(image_id, new_page_four.get(image_id, "")))
        easy = f"{image_id}_easy_read"
        if easy in texts:
            texts[easy] = texts[image_id]
    # The old separate page 5 is no longer part of the publication spine.
    for key in list(texts):
        if key.startswith("pg005_"):
            del texts[key]
    texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

toc_path = ROOT / "content/toc.json"
toc = json.loads(toc_path.read_text(encoding="utf-8"))
for entry in toc:
    entry["title"] = re.sub(r"\bNa\.?(?=\s|$)", "namba", entry.get("title", ""))
toc_path.write_text(json.dumps(toc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Corrected 'namba' and synchronized {len(used_image_ids)} Swahili image descriptions.")
