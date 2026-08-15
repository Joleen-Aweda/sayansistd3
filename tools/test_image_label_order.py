import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
TEXTS = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))

violations = []
for entry in PAGES:
    markup = (ROOT / entry["href"]).read_text(encoding="utf-8")
    for match in re.finditer(r'(<img\b[^>]*>)(\s*<(?:div|span|p)\b[^>]*data-id="([^"]+)"[^>]*>.*?</(?:div|span|p)>)', markup, re.DOTALL):
        value = TEXTS.get(match.group(3), "").strip()
        if re.fullmatch(r"\(?[A-Za-z]\)?\.?", value):
            violations.append((entry["href"], match.group(3)))

assert not violations, violations[:20]
print("PASS: image letters are ordered before their corresponding image descriptions.")
