from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for filename, count in (("pg042_sec002.html", 5), ("pg079_sec002.html", 4), ("pg095_sec002.html", 5)):
    markup = (ROOT / filename).read_text(encoding="utf-8")
    assert 'type="radio"' not in markup, filename
    assert markup.count('type="text"') == count, filename
    assert markup.count('"item-') >= count
    assert '"item-1":""' in markup

print("PASS: reference true/false exercises preserve fourteen blank answer fields.")
