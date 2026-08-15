#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
nose = (ROOT / "pg034_sec001.html").read_text(encoding="utf-8")
skin = (ROOT / "pg035_sec001.html").read_text(encoding="utf-8")

assert 'object-fit: contain; object-position: center;' in nose
assert '<svg' not in nose
assert '<polyline' not in nose
assert '<circle' not in nose

assert 'viewBox="0 0 880 539"' in skin
assert skin.count('<polyline points=') == 7
assert '<circle' not in skin
assert 'points="131,90 630,90"' in skin  # hair shaft to label
assert 'points="570,155 585,155 585,530 570,530"' in skin
for label in ("Kinyweleo", "Tabaka la juu", "Tabaka la kati", "Tabaka la ndani"):
    assert label in skin

print("PASS: the full nose reference layout and all four skin leader lines are valid.")
