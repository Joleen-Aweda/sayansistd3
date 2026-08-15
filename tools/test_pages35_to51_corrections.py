#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda name: (ROOT / name).read_text(encoding="utf-8")

assert "pg035_im002_seg001_clean.png" in read("pg035_sec002.html")
assert "pg035_im002_seg002_clean.png" in read("pg035_sec002.html")

ear = read("pg037_sec001.html")
assert "Ngoma ya sikio" in ear and "(Ngoma ya sikio)" not in ear
assert "pg037_im001_clean.png" in ear and "pg037_reference.png" not in ear
assert "<svg" in ear and 'data-id="pg037_n0003" class="sr-only"' in ear
assert 'data-duplicate-id="pg037_n0003" class="ear-figure-label"' in ear
assert ear.index("pg037_n0002") < ear.index("pg037_im001_clean.png") < ear.index('data-id="pg037_im001"')

choices = read("pg042_sec001.html")
for letter in "abcd":
    assert f"({letter})" in choices

glossary = read("pg043_sec001.html")
assert glossary.count("grid-cols-[155px_1fr]") == 3

pages = json.loads(read("content/pages.json"))
assert not any(item["section_id"] == "pg044_sec002" for item in pages)
merged = read("pg044_sec001.html")
assert "pg044_n0018" in merged and "pg044_n0022" in merged

plants = read("pg049_sec001.html")
assert "grid-cols-3" in plants and plants.count(">Mwanga</div>") == 3

activity = read("pg051_sec001.html")
for number in (1, 2, 3):
    assert f"pg051_im001_seg00{number}_clean.png" in activity
for label in ("pg051_n0012", "pg051_n0014", "pg051_n0016"):
    assert activity.index(label) < activity.index(label.replace("n0012", "im001_seg001_v1").replace("n0014", "im001_seg002_v1").replace("n0016", "im001_seg003_v1"))

print("PASS: requested page 35–51 layouts, labels, crops, choices and page merge are present.")
