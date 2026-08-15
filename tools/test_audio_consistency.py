"""Validate synchronized, non-empty and byte-identical Swahili narration assets."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))
sw = json.loads((ROOT / "content/i18n/sw/audios.json").read_text(encoding="utf-8"))
tz = json.loads((ROOT / "content/i18n/sw-TZ/audios.json").read_text(encoding="utf-8"))

assert sw == tz
assert all(texts.get(key, "").strip() for key in sw)
for key, mapped in sw.items():
    filename = mapped.split("?", 1)[0]
    left = ROOT / "content/i18n/sw/audio" / filename
    right = ROOT / "content/i18n/sw-TZ/audio" / filename
    assert left.exists() and left.stat().st_size > 512, key
    assert right.exists() and right.stat().st_size == left.stat().st_size, key
    assert hashlib.sha256(left.read_bytes()).digest() == hashlib.sha256(right.read_bytes()).digest(), key

print(f"PASS: {len(sw)} narration mappings use byte-identical Swahili audio in sw and sw-TZ.")
