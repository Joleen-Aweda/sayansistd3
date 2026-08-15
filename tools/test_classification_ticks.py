from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page46 = (ROOT / "pg046_sec001.html").read_text(encoding="utf-8")
page47 = (ROOT / "pg047_sec001.html").read_text(encoding="utf-8")

assert page46.count('<input type="checkbox"') == 10
assert page47.count('<input type="checkbox"') == 12
assert 'type="radio"' not in page46
assert 'type="text"' not in page47
assert "option-letter" not in page46
assert '"item-1":true' in page46 and '"item-10":true' in page46
assert '"item-1":true' in page47 and '"item-12":true' in page47
assert page46.count("other.checked = false") == 1
assert page47.count("other.checked = false") == 1

print("PASS: pages 46–47 use mutually exclusive accessible tick controls and boolean answer keys.")
