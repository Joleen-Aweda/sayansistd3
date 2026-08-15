#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
nose = (ROOT / "pg034_sec001.html").read_text(encoding="utf-8")
skin = (ROOT / "pg035_sec001.html").read_text(encoding="utf-8")

assert 'viewBox="0 0 500 248"' in nose
assert nose.count("<polyline points=") == 2
assert nose.count("<circle cx=") == 2

assert 'viewBox="0 0 820 539"' in skin
assert skin.count("<polyline points=") == 4
assert skin.count("<circle cx=") == 4
for text_id, label in {
    "pg035_n0002": "Kinyweleo",
    "pg035_n0003": "Tabaka la juu",
    "pg035_n0004": "Tabaka la kati",
    "pg035_n0005": "Tabaka la ndani",
}.items():
    assert f'data-id="{text_id}"' in skin
    assert f">({label})<" not in skin
    for language in ("sw", "sw-TZ"):
        texts = json.loads((ROOT / "content/i18n" / language / "texts.json").read_text(encoding="utf-8"))
        assert texts[text_id] == label
        assert texts[f"{text_id}_easy_read"] == label

print("PASS: both nostrils and all four skin parts have clear directional lines.")
