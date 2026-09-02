import json
import re
import threading
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
handler = partial(SimpleHTTPRequestHandler, directory=ROOT)
server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()

try:
    base = f"http://127.0.0.1:{server.server_port}/"
    pages = json.load(urllib.request.urlopen(base + "content/pages.json"))
    assert [page["page_number"] for page in pages if "page_number" in page] == list(range(1, 110)) + list(range(111, 150))
    assert pages[0]["href"] == "index.html"
    assert pages[-1]["href"] == "back-cover.html"
    preloader = (ROOT / "assets/offline-preloader.js").read_text(encoding="utf-8")
    embedded_match = re.search(r"var INLINE = (\{.*?\});\n\s*var ", preloader, re.DOTALL)
    assert embedded_match
    embedded = json.loads(embedded_match.group(1))
    assert embedded["./content/pages.json"] == pages
    version = json.loads((ROOT / "assets/config.json").read_text(encoding="utf-8"))["bundleVersion"]
    assert embedded["./assets/config.json"]["bundleVersion"] == version
    for number in (1, 58, 59, 60, len(pages)):
        response = urllib.request.urlopen(base + pages[number - 1]["href"])
        markup = response.read().decode("utf-8")
        assert response.status == 200
        assert f'content="{number}"' in markup
        assert 'id="content"' in markup
        assert "assets/base.bundle.local.js" in markup
        assert f"assets/offline-preloader.js?v={version}" in markup
        assert f"assets/fonts.css?v={version}" in markup
    landing = urllib.request.urlopen(base + "index.html").read().decode("utf-8")
    assert 'data-id="cover_im001"' in landing
    assert 'id="nav-container"' in urllib.request.urlopen(base + pages[0]["href"]).read().decode("utf-8")
    print("PASS: front cover, representative book pages and back cover load with manifest navigation.")
finally:
    server.shutdown()
    server.server_close()
