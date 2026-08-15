"""Place short image letters and names before their corresponding images."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTS = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))

node = r'<(?P<tag>div|span|p)\b(?P<attrs>[^>]*)data-id="(?P<id>[^"]+)"(?P<tail>[^>]*)>(?P<body>.*?)</(?P=tag)>'
pair = re.compile(rf'(?P<img><img\b[^>]*data-(?:duplicate-)?id="[^"]+"[^>]*>)(?P<labels>(?:\s*{node}){{1,2}})', re.DOTALL)


def qualifies(text_id: str) -> bool:
    value = re.sub(r"\s+", " ", TEXTS.get(text_id, "")).strip()
    if not value or value.lower().startswith(("kielelezo", "jedwali", "picha inaonesha")):
        return False
    return bool(re.fullmatch(r"\(?[A-Za-z]\)?\.?", value)) or len(value.split()) <= 5


def add_class(markup: str) -> str:
    if "adt-label-above" in markup:
        return markup
    if re.search(r'\bclass="', markup):
        return re.sub(r'\bclass="([^"]*)"', lambda m: f'class="{m.group(1)} adt-label-above"', markup, count=1)
    return re.sub(r'^<([A-Za-z0-9]+)', r'<\1 class="adt-label-above"', markup, count=1)


changed = 0
for entry in PAGES:
    path = ROOT / entry["href"]
    markup = path.read_text(encoding="utf-8")

    def move(match):
        nonlocal_changed = 0
        labels = match.group("labels")
        ids = re.findall(r'data-id="([^"]+)"', labels)
        if not ids or not all(qualifies(text_id) for text_id in ids):
            return match.group(0)
        labelled = re.sub(node, lambda m: add_class(m.group(0)), labels, flags=re.DOTALL)
        return labelled + "\n" + match.group("img")

    updated, count = pair.subn(move, markup)
    if updated != markup:
        changed += 1
        path.write_text(updated, encoding="utf-8")

print(f"Placed image letters or short names above images on {changed} pages.")
