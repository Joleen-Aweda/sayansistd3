"""Replace visible true/false choices with the reference book's blank answer lines."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "pg042_sec002.html": 5,
    "pg079_sec002.html": 4,
    "pg095_sec002.html": 5,
}

for filename, expected in PAGES.items():
    path = ROOT / filename
    markup = path.read_text(encoding="utf-8")
    groups = re.compile(
        r'</legend>\s*<div class="[^"]*">(?P<body>.*?)</div>\s*</fieldset>',
        re.DOTALL,
    )

    def blank(match):
        item = re.search(r'data-activity-item="(item-\d+)"', match.group("body"))
        if not item:
            return match.group(0)
        number = item.group(1).split("-")[-1]
        return (
            '</legend>'
            f'<input type="text" data-activity-item="{item.group(1)}" '
            f'aria-label="Nafasi ya jibu la swali {number}" '
            'class="ml-14 mt-3 h-11 w-[min(26rem,calc(100%-3.5rem))] border-0 border-b-2 '
            'border-slate-500 bg-transparent px-2 outline-none focus:border-sky-600 max-sm:ml-10">'
            '</fieldset>'
        )

    markup, count = groups.subn(blank, markup)
    if count == 0 and markup.count('type="text"') == expected:
        count = expected
    if count != expected:
        raise RuntimeError(f"{filename}: expected {expected} answer groups, replaced {count}")
    answers = ",".join(f'"item-{index}":""' for index in range(1, expected + 1))
    markup = re.sub(r"window\.correctAnswers = JSON\.parse\('\{.*?\}'\);", f"window.correctAnswers = JSON.parse('{{{answers}}}');", markup)
    path.write_text(markup, encoding="utf-8")

print("Converted three true/false exercises to fourteen blank answer lines.")
