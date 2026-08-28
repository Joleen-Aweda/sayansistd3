"""Make selected activity titles visible and align page 145 questions."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "194"

TITLE_IDS = {
    "pg101_sec002.html": "pg101_n0016",  # page 132
    "pg103_sec001.html": "pg103_n0002",  # page 134
    "pg103_sec002.html": "pg103_n0013",  # page 135
    "pg106_sec002.html": "pg106_n0013",  # page 140
    "pg107_sec002.html": "pg107_n0026",  # page 142
    "pg108_sec002.html": "pg108_n0011",  # page 143
}

BANNER_COLOURS = {
    "pg101_sec002.html": "#f86f4d",
    "pg103_sec001.html": "#56c3e8",
    "pg103_sec002.html": "#ff6f4d",
    "pg106_sec002.html": "#fb923c",
    "pg107_sec002.html": "#58c7eb",
    "pg108_sec002.html": "#f96d4a",
}

PAGE_COLOURS = {
    "pg101_sec002.html": "#fff7ed",
    "pg103_sec001.html": "#c9effb",
    "pg103_sec002.html": "#d7f2fb",
    "pg106_sec002.html": "#f0f9ff",
    "pg107_sec002.html": "#ffffff",
    "pg108_sec002.html": "#f0f9ff",
}

for filename, text_id in TITLE_IDS.items():
    path = ROOT / filename
    markup = path.read_text(encoding="utf-8")
    markup = re.sub(
        rf'(<(?:h1|div)[^>]*data-id="{re.escape(text_id)}"[^>]*?)\s+style="[^"]*"(>)',
        rf'\1 style="color:#ffffff!important"\2',
        markup,
        count=1,
    )
    markup = re.sub(
        rf'(<(?:h1|div)[^>]*data-id="{re.escape(text_id)}"(?![^>]*\sstyle=)[^>]*)(>)',
        rf'\1 style="color:#ffffff!important"\2',
        markup,
        count=1,
    )
    # Put the printed banner colour on the title node too. This keeps the
    # title visible if reader styling overrides or removes its parent colour.
    markup = re.sub(
        rf'(<(?:h1|div)(?=[^>]*data-id="{re.escape(text_id)}")[^>]*?)\sstyle="[^"]*"(>)',
        lambda match: match.group(1)
        + f' style="display:inline-block!important;background-color:{BANNER_COLOURS[filename]}!important;'
          'color:#ffffff!important;padding:.65rem 1.25rem!important;'
          'border-radius:1rem!important;line-height:1.15!important"'
        + match.group(2),
        markup,
        count=1,
    )
    # The colour utilities are also written inline so the printed-book banner
    # remains visible even when a cached or reduced stylesheet is loaded.
    markup = re.sub(
        rf'(<div class="[^"]*"(?![^>]*\sstyle=)[^>]*)(>\s*<(?:h1|div)[^>]*data-id="{re.escape(text_id)}")',
        rf'\1 style="background-color:{BANNER_COLOURS[filename]}!important"\2',
        markup,
        count=1,
    )
    section_id = filename.removesuffix(".html")
    markup = re.sub(
        rf'(<section[^>]*data-section-id="{re.escape(section_id)}"(?![^>]*\sstyle=)[^>]*)(>)',
        rf'\1 style="background-color:{PAGE_COLOURS[filename]}!important"\2',
        markup,
        count=1,
    )
    path.write_text(markup, encoding="utf-8")

page145 = ROOT / "pg109_sec002.html"
markup = page145.read_text(encoding="utf-8")
markup = markup.replace(
    '<div class="inline-block rounded-[1.75rem] bg-sky-400 px-9 py-3 shadow-sm max-lg:px-8 max-lg:py-3 max-sm:px-5 max-sm:py-2">',
    '<div class="inline-block rounded-[1.75rem] bg-sky-400 px-9 py-3 shadow-sm max-lg:px-8 max-lg:py-3 max-sm:px-5 max-sm:py-2" style="background-color:#38bdf8!important">',
)
markup = markup.replace(
    '<div class="rounded-[1.75rem] bg-sky-100 px-6 py-6 max-lg:px-5 max-lg:py-5 max-sm:px-4 max-sm:py-4">',
    '<div class="rounded-[1.75rem] bg-sky-100 px-6 py-6 max-lg:px-5 max-lg:py-5 max-sm:px-4 max-sm:py-4" style="background-color:#e0f2fe!important">',
)
question_row = (
    'style="display:flex!important;align-items:flex-start!important;'
    'gap:1rem!important;width:100%!important"'
)
markup = re.sub(
    r'(<div class="grid grid-cols-\[auto_1fr\][^"]*")>',
    rf'\1 {question_row}>',
    markup,
)
for text_id in ("pg109_n0016", "pg109_n0018", "pg109_n0020", "pg109_n0023", "pg109_n0025"):
    markup = re.sub(
        rf'(<span class="not-italic" data-id="{text_id}")>',
        r'\1 style="flex:0 0 2rem;width:2rem;white-space:nowrap">',
        markup,
        count=1,
    )
for text_id in ("pg109_n0017", "pg109_n0019", "pg109_n0021", "pg109_n0024", "pg109_n0026"):
    markup = re.sub(
        rf'(<(?:span|div)(?=[^>]*(?:data-id|data-duplicate-id)="{text_id}")[^>]*)(>)',
        lambda match: re.sub(r'\sstyle="[^"]*"', '', match.group(1))
        + ' style="flex:1 1 auto;min-width:0"' + match.group(2),
        markup,
        count=1,
    )
page145.write_text(markup, encoding="utf-8")

config_path = ROOT / "assets/config.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
config["bundleVersion"] = VERSION
config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Restored printed-book backgrounds, six title banners and five page 145 question rows.")
