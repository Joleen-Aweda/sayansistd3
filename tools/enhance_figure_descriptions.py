"""Prefix Swahili image descriptions with their actual figure number and letter."""

import html as html_lib
import json
import re
from pathlib import Path

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("sw", "sw-TZ")
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = {lang: json.loads((ROOT / f"content/i18n/{lang}/texts.json").read_text(encoding="utf-8")) for lang in LANGUAGES}
references: dict[str, tuple[str, str]] = {}


def node_text(element) -> str:
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


for page in pages:
    path = ROOT / page["href"]
    root = html.fromstring(path.read_text(encoding="utf-8"))
    elements = [element for element in root.iter() if isinstance(element.tag, str)]
    positions = {id(element): index for index, element in enumerate(elements)}
    captions = []
    for element in root.xpath('//*[@data-id or @data-duplicate-id]'):
        value = node_text(element)
        match = re.search(r"Kielelezo(?:\s+namba)?\s+(\d+)\s*:", value, flags=re.I)
        if match and len(value) < 180:
            captions.append((positions[id(element)], match.group(1)))

    for image in root.xpath('//img[@data-id or @data-duplicate-id]'):
        image_id = image.get("data-id") or image.get("data-duplicate-id")
        if not captions:
            continue
        image_position = positions[id(image)]
        figure_number = min(captions, key=lambda item: abs(item[0] - image_position))[1]
        letter = ""
        parent = image.getparent()
        for sibling in parent:
            if sibling is image:
                break
            value = node_text(sibling)
            if re.fullmatch(r"\([a-z]\)", value, flags=re.I):
                letter = value.lower()
        current = references.get(image_id)
        if current is None or (letter and not current[1]):
            references[image_id] = (figure_number, letter)


def description_body(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(
        r"^(?:Picha|Mchoro|Kielelezo(?:\s+namba\s+\d+(?:\([a-z]\))?)?)\s+(?:inaonesha|kinaonesha)\s+",
        "",
        value,
        flags=re.I,
    )
    return value[:1].lower() + value[1:] if value else value


for image_id, (number, letter) in references.items():
    body = description_body(texts["sw"].get(image_id, ""))
    if not body:
        continue
    description = f"Kielelezo namba {number}{letter} kinaonesha {body}"
    if not description.endswith("."):
        description += "."
    for lang in LANGUAGES:
        texts[lang][image_id] = description
        easy = f"{image_id}_easy_read"
        if easy in texts[lang]:
            texts[lang][easy] = description

for page in pages:
    path = ROOT / page["href"]
    markup = path.read_text(encoding="utf-8")

    def update_alt(match):
        tag = match.group(0)
        id_match = re.search(r'data-(?:duplicate-)?id="([^"]+)"', tag)
        if not id_match or id_match.group(1) not in references:
            return tag
        description = html_lib.escape(texts["sw"][id_match.group(1)], quote=True)
        if re.search(r'\balt="[^"]*"', tag):
            return re.sub(r'\balt="[^"]*"', f'alt="{description}"', tag, count=1)
        return tag[:-1] + f' alt="{description}">'

    path.write_text(re.sub(r'<img\b[^>]*>', update_alt, markup), encoding="utf-8")

for lang in LANGUAGES:
    (ROOT / f"content/i18n/{lang}/texts.json").write_text(
        json.dumps(texts[lang], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

print(f"Enhanced {len(references)} figure descriptions with their number and available letter.")
