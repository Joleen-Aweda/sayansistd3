"""Place each image description in the normal read-aloud sequence exactly once."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))
seen = set()

for page in pages:
    path = ROOT / page["href"]
    markup = path.read_text(encoding="utf-8")
    markup = re.sub(
        r'\s*<span\b[^>]*class="[^"]*\badt-image-description\b[^"]*"[^>]*>.*?</span>',
        "",
        markup,
        flags=re.DOTALL,
    )

    def narratable_image(match):
        tag = match.group(0)
        id_match = re.search(r'data-(?:duplicate-)?id="([^"]+)"', tag)
        if not id_match:
            return tag
        image_id = id_match.group(1)
        tag = re.sub(r'\bdata-id="', 'data-duplicate-id="', tag, count=1)
        if image_id in seen:
            return tag
        seen.add(image_id)
        description = texts.get(image_id, "").strip()
        if not description:
            return tag
        hidden = (
            f'<span class="adt-image-description" data-id="{html.escape(image_id, quote=True)}">'
            f'{html.escape(description)}</span>'
        )
        return tag + hidden

    path.write_text(re.sub(r'<img\b[^>]*>', narratable_image, markup), encoding="utf-8")

print(f"Added {len(seen)} hidden image descriptions to the normal narration sequence.")
