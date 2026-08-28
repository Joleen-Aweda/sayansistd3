"""Synchronize page 129 Starfall correction across both Swahili catalogs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "190"
TEXTS = {
    "pg099_n0028": "Kazi ya kufanya ya Starfall",
    "pg099_n0029": (
        "Maelezo ya mchezo: Starfall Mix and Paint una paleti ya rangi na "
        "eneo la kuchorea na kupaka rangi."
    ),
    "pg099_n0030": (
        "Fungua mchezo, chagua rangi unayoipenda, kisha chora au paka "
        "rangi mchoro."
    ),
    "pg099_n0031": "Fungua Starfall Mix and Paint",
}


def write_json(path: Path, data: dict[str, str]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


for language in ("sw", "sw-TZ"):
    base = ROOT / "content" / "i18n" / language
    texts_path = base / "texts.json"
    audios_path = base / "audios.json"
    texts = json.loads(texts_path.read_text(encoding="utf-8"))
    audios = json.loads(audios_path.read_text(encoding="utf-8"))
    for text_id, value in TEXTS.items():
        for variant in (text_id, f"{text_id}_easy_read"):
            texts[variant] = value
            audios[variant] = f"{variant}.mp3?v={VERSION}"
    for text_id, filename in list(audios.items()):
        if text_id.endswith("_end") and filename.startswith("page_end.mp3"):
            audios[text_id] = f"page_end.mp3?v={VERSION}"
    write_json(texts_path, texts)
    write_json(audios_path, audios)

config_path = ROOT / "assets" / "config.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
config["bundleVersion"] = VERSION
write_json(config_path, config)

page_path = ROOT / "pg099_sec002.html"
markup = page_path.read_text(encoding="utf-8")
markup = markup.replace(
    'bg-[#f86f4c] px-7 py-3 max-lg:px-6 max-sm:w-full '
    'max-sm:rounded-br-none max-sm:px-5">',
    'bg-[#f86f4c] px-7 py-3 max-lg:px-6 max-sm:w-full '
    'max-sm:rounded-br-none max-sm:px-5" style="background-color:#f86f4c">',
    1,
)
markup = markup.replace(
    'text-zinc-950 max-lg:text-[1.8rem] max-sm:text-[1.5rem]">',
    'text-zinc-950 max-lg:text-[1.8rem] max-sm:text-[1.5rem]" '
    'style="color:#18181b">',
    1,
)
markup = markup.replace(
    'text-white underline underline-offset-4"><span data-id="pg099_n0031">',
    'text-white underline underline-offset-4" '
    'style="background-color:#0369a1;color:#ffffff"><span '
    'data-id="pg099_n0031">',
    1,
)
page_path.write_text(markup, encoding="utf-8")

print("Synchronized page 129 Starfall correction at bundle version 190.")
