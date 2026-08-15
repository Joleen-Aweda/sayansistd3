#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = sorted(ROOT.glob("pg*.html")) + sorted(ROOT.glob("qz*.html"))

script = (ROOT / "assets/image-narration-highlight.js").read_text(encoding="utf-8")
styles = (ROOT / "assets/fonts.css").read_text(encoding="utf-8")

assert "MutationObserver" in script
assert "tts-active-block" in script
assert "img[data-duplicate-id]" in script
assert "adt-image-narration-active" in script
assert "#2563eb" in styles
assert "img.adt-image-narration-active" in styles

missing = [page.name for page in pages if "image-narration-highlight.js?v=49" not in page.read_text(encoding="utf-8")]
assert not missing, f"Pages missing image narration highlight script: {missing}"

print(f"Image narration highlighting verified on {len(pages)} pages.")
