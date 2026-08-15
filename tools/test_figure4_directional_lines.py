#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "pg027_sec001.html").read_text(encoding="utf-8")

for text_id in ("pg027_n0002", "pg027_n0003", "pg027_n0004", "pg027_n0005"):
    assert f'data-id="{text_id}"' in page

assert 'style="left: 1.5%; top: 28%;"' in page
assert 'data-id="pg027_n0004" class="absolute' in page and 'style="left: 1.5%; top: 50%;">Lenzi' in page
assert 'data-id="pg027_n0003" class="absolute' in page and 'style="left: 1.5%; top: 72%;">Pupili' in page
assert 'style="right: 1%; top: 9%;"' in page
assert '<line x1="105" y1="153" x2="186" y2="210"' in page
assert '<line x1="105" y1="260" x2="230" y2="250"' in page
assert 'points="105,369 145,369 165,330 203,294"' in page
assert '<line x1="655" y1="64" x2="553" y2="245"' in page

print("PASS: Figure 4 labels are spaced and connected to mboni, pupili, lenzi and retina.")
