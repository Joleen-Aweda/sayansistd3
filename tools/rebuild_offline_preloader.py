"""Rebuild the offline inline content map from the published page spine."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRELOADER = ROOT / "assets/offline-preloader.js"

source = PRELOADER.read_text(encoding="utf-8")
match = re.search(r"var INLINE = (\{.*?\});\n\s*var ", source, re.DOTALL)
if not match:
    raise RuntimeError("Could not find the embedded offline content map")

old = json.loads(match.group(1))
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
bundle_version = json.loads((ROOT / "assets/config.json").read_text(encoding="utf-8"))["bundleVersion"]
priority = [
    "./assets/config.json",
    "./content/pages.json",
    "./content/toc.json",
    "./content/navigation/nav.html",
    "./index.html",
    *[f'./{page["href"]}' for page in pages],
]
extras = [key for key in old if not key.endswith(".html") and key not in priority]
inline = {}
for key in [*priority, *extras]:
    path = ROOT / key.removeprefix("./")
    if not path.exists():
        continue
    inline[key] = json.loads(path.read_text(encoding="utf-8")) if path.suffix == ".json" else path.read_text(encoding="utf-8")

encoded = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
PRELOADER.write_text(source[:match.start(1)] + encoded + source[match.end(1):], encoding="utf-8")

for page in pages:
    path = ROOT / page["href"]
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"assets/offline-preloader\.js(?:\?v=\d+)?", f"assets/offline-preloader.js?v={bundle_version}", html)
    html = re.sub(r"assets/fonts\.css(?:\?v=\d+)?", f"assets/fonts.css?v={bundle_version}", html)
    concurrent_script = (
        f'<script src="./assets/concurrent-sign-language-playback.js?v={bundle_version}"></script>'
    )
    if "assets/concurrent-sign-language-playback.js" in html:
        html = re.sub(
            r'<script src="\./assets/concurrent-sign-language-playback\.js(?:\?v=\d+)?"></script>',
            concurrent_script,
            html,
        )
    else:
        html = re.sub(
            r'(<script src="\./assets/base\.bundle\.local\.js">)',
            concurrent_script + r"\n    \1",
            html,
            count=1,
        )
    # Image files are frequently corrected in place during post-processing.
    # Version every local image URL so the reader never reuses an older image
    # cached under the same filename on a different page.
    html = re.sub(
        r'(src=["\']images/[^"\'?]+)(?:\?v=\d+)?(["\'])',
        rf'\1?v={bundle_version}\2',
        html,
    )
    path.write_text(html, encoding="utf-8")

print(f"Embedded {len(pages)} consecutive pages with bundle version {bundle_version}.")
