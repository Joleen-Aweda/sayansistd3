"""Synchronize page IDs, Swahili fallbacks, image alternatives and audio mappings."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("sw", "sw-TZ")
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = {lang: json.loads((ROOT / f"content/i18n/{lang}/texts.json").read_text(encoding="utf-8")) for lang in LANGUAGES}
audios = {lang: json.loads((ROOT / f"content/i18n/{lang}/audios.json").read_text(encoding="utf-8")) for lang in LANGUAGES}


def clean_markup(value: str) -> str:
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def explicit_description(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        return value
    if len(value.split()) < 3:
        value = value.rstrip(".")
        return f"Picha inaonesha {value.lower()}."
    return value


seen = set()
for entry in pages:
    path = ROOT / entry["href"]
    markup = path.read_text(encoding="utf-8")

    # Activity container IDs identify the activity; they are not spoken text.
    markup = re.sub(
        r'(<section\b(?=[^>]*(?:\brole="activity"|\bdata-section-type="activity_quiz"))[^>]*?)\sdata-id="qz\d+"',
        r"\1",
        markup,
        flags=re.DOTALL,
    )

    # Repeated diagram labels retain localization without replaying narration.
    def unique_id(match):
        text_id = match.group(1)
        if text_id in seen:
            return f'data-duplicate-id="{text_id}"'
        seen.add(text_id)
        return match.group(0)

    markup = re.sub(r'data-id="([^"]+)"', unique_id, markup)

    # Preserve manually corrected Swahili fallback text as the localized source.
    pattern = re.compile(r'<(?P<tag>[A-Za-z0-9]+)\b(?P<attrs>[^>]*)\bdata-id="(?P<id>[^"]+)"(?P<tail>[^>]*)>(?P<body>.*?)</(?P=tag)>', re.DOTALL)
    for match in pattern.finditer(markup):
        text_id = match.group("id")
        if text_id.startswith("qz") or "data-id=" in match.group("body") or match.group("tag").lower() in {"section", "div"} and not clean_markup(match.group("body")):
            continue
        fallback = clean_markup(match.group("body"))
        if fallback:
            for lang in LANGUAGES:
                texts[lang][text_id] = fallback
                easy = f"{text_id}_easy_read"
                if easy in texts[lang]:
                    texts[lang][easy] = fallback

    # Image alternatives come from the same localized narration string.
    def sync_image(match):
        tag = match.group(0)
        id_match = re.search(r'data-(?:duplicate-)?id="([^"]+)"', tag)
        if not id_match:
            return tag
        text_id = id_match.group(1)
        description = explicit_description(texts["sw"].get(text_id, ""))
        if not description:
            alt_match = re.search(r'alt="([^"]*)"', tag)
            description = explicit_description(html.unescape(alt_match.group(1))) if alt_match else ""
        if description:
            for lang in LANGUAGES:
                texts[lang][text_id] = description
                easy = f"{text_id}_easy_read"
                if easy in texts[lang]:
                    texts[lang][easy] = description
            escaped = html.escape(description, quote=True)
            if re.search(r'\balt="[^"]*"', tag):
                tag = re.sub(r'\balt="[^"]*"', f'alt="{escaped}"', tag, count=1)
            else:
                tag = tag[:-1] + f' alt="{escaped}">'
        return tag

    markup = re.sub(r'<img\b[^>]*>', sync_image, markup)
    path.write_text(markup, encoding="utf-8")

for lang in LANGUAGES:
    for text_id, value in texts[lang].items():
        if value.strip() and (text_id in seen or text_id.startswith(("gl", "qz"))):
            audios[lang].setdefault(text_id, f"{text_id}.mp3?v=24")
    (ROOT / f"content/i18n/{lang}/texts.json").write_text(json.dumps(texts[lang], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / f"content/i18n/{lang}/audios.json").write_text(json.dumps(audios[lang], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Synchronized {len(seen)} unique narration IDs across {len(pages)} published pages.")
