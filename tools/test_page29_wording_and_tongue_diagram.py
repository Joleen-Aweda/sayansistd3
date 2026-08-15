#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

page29 = (ROOT / "pg029_sec002.html").read_text(encoding="utf-8")
page30 = (ROOT / "pg030_sec001.html").read_text(encoding="utf-8")

expected = "Chunguza picha za maumbo a mpaka e katika Kielelezo namba 5."
assert expected in page29
assert "(a) - (e)" not in page29

for language in ("sw", "sw-TZ"):
    texts = json.loads((ROOT / "content/i18n" / language / "texts.json").read_text(encoding="utf-8"))
    assert texts["pg029_n0021"] == expected
    assert texts["pg029_n0021_easy_read"] == expected

assert 'viewBox="0 0 900 342"' in page30
assert page30.count("<polyline points=") == 7
assert page30.count("<circle cx=") == 7
for label in ("Uchungu", "Uchachu", "Chumvichumvi", "Umami", "Utamu"):
    assert label in page30

print("PASS: page 29 wording and the spaced, routed tongue labels are valid.")
