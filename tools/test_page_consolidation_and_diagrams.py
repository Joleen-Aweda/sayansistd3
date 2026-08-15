#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))

assert len(pages) == 151
assert not any(item["section_id"].startswith("qz") for item in pages)
assert not list(ROOT.glob("qz*.html"))
assert not (ROOT / "pg022_sec001.html").exists()
assert not (ROOT / "pg023_sec002.html").exists()
assert not any(item["section_id"] == "pg061_sec001" for item in pages)
assert not any(item["section_id"] == "pg067_sec001" for item in pages)
assert not any(item["section_id"] == "pg108_sec001" for item in pages)

page60 = (ROOT / "pg060_sec001.html").read_text(encoding="utf-8")
for text_id in ("pg060_n0024", "pg061_n0003", "pg061_n0006", "pg061_n0009"):
    assert f'data-id="{text_id}"' in page60

page66 = (ROOT / "pg066_sec003.html").read_text(encoding="utf-8")
for text_id in ("pg066_n0039", "pg067_n0002", "pg067_n0007", "pg067_n0034"):
    assert f'data-id="{text_id}"' in page66

page107 = (ROOT / "pg107_sec002.html").read_text(encoding="utf-8")
for text_id in ("pg107_n0027", "pg108_n0004", "pg108_n0006", "pg108_n0008"):
    assert f'data-id="{text_id}"' in page107

page21 = (ROOT / "pg021_sec002.html").read_text(encoding="utf-8")
for text_id in ("pg021_n0046", "pg022_n0002", "pg022_n0003", "pg022_n0018"):
    assert f'data-id="{text_id}"' in page21
assert '"item-2":"Kemia"' in page21 and '"item-3":"Baiolojia"' in page21

page23 = (ROOT / "pg023_sec001.html").read_text(encoding="utf-8")
assert 'data-id="pg023_n0015"' in page23 and "<svg" in page23
assert 'data-id="pg023_n0018"' in page23 and 'data-id="pg023_n0022"' in page23

page24 = (ROOT / "pg024_sec001.html").read_text(encoding="utf-8")
assert '<line x1="50" y1="21" x2="54" y2="48"' in page24

page26 = (ROOT / "pg026_sec001.html").read_text(encoding="utf-8")
assert 'viewBox="0 0 820 560"' in page26
assert page26.count("<line ") == 2 and page26.count("<polyline ") == 2
assert '<line x1="105" y1="222" x2="321" y2="321"' in page26
assert '<line x1="643" y1="169" x2="500" y2="216"' in page26
assert 'points="690,273 625,273 553,316"' in page26
assert 'points="690,300 625,300 521,416"' in page26

page27 = (ROOT / "pg027_sec001.html").read_text(encoding="utf-8")
assert 'viewBox="0 0 760 494"' in page27
assert page27.count("<line ") == 3 and page27.count("<polyline ") == 1
for endpoint in ('x2="186" y2="210"', 'x2="230" y2="250"', 'x2="553" y2="245"'):
    assert endpoint in page27
assert 'points="105,369 145,369 165,330 203,294"' in page27

for language in ("sw", "sw-TZ"):
    for filename in ("texts.json", "audios.json"):
        data = json.loads((ROOT / "content/i18n" / language / filename).read_text(encoding="utf-8"))
        assert not any(key.startswith("qz") for key in data)

print("PASS: merged pages, quiz removal, Fikiri icon and directional diagrams are valid.")
