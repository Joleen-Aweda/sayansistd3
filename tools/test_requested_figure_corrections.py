#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

page13 = (ROOT / "pg013_sec001.html").read_text(encoding="utf-8")
assert '<line x1="46" y1="17" x2="43" y2="35"' in page13

page14 = (ROOT / "pg014_sec002.html").read_text(encoding="utf-8")
assert page14.count('type="text"') == 4
assert 'type="radio"' not in page14
assert "window.correctAnswers" not in page14

page16 = (ROOT / "pg016_sec001.html").read_text(encoding="utf-8")
label16 = page16.index('data-id="pg016_n0002"')
image16 = page16.index('data-duplicate-id="pg016_im002"')
assert label16 < image16

page20 = (ROOT / "pg020_sec001.html").read_text(encoding="utf-8")
assert page20.count("<line ") == 7
assert '<line x1="445" y1="470" x2="333" y2="597"' in page20
assert '<line x1="535" y1="470" x2="706" y2="597"' in page20
for label_id, image_id in (
    ("pg020_n0002", "pg020_im004"),
    ("pg020_n0004", "pg020_im003"),
    ("pg020_n0006", "pg020_im002"),
    ("pg020_n0008", "pg020_im006"),
    ("pg020_n0010", "pg020_im001"),
    ("pg020_n0012", "pg020_im005"),
    ("pg020_n0014", "pg020_im007"),
):
    assert page20.index(f'data-id="{label_id}"') < page20.index(f'data-duplicate-id="{image_id}"')

print("PASS: requested figure, answer-field and narration-order corrections are present.")
