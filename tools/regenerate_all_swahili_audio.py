"""Regenerate the complete published narration with one Tanzanian Swahili voice."""

import argparse
import asyncio
import hashlib
import json
import re
import shutil
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("sw", "sw-TZ")
VOICE = "sw-TZ-DaudiNeural"
RATE = "-5%"
VERSION = "24"
ROMAN = {
    "i": "moja", "ii": "mbili", "iii": "tatu", "iv": "nne", "v": "tano",
    "vi": "sita", "vii": "saba", "viii": "nane", "ix": "tisa", "x": "kumi",
}


def spoken_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if not value or re.fullmatch(r"[_\.\-–—\s]+", value):
        return ""
    value = re.sub(
        r"^\(([ivx]+)\)\s*",
        lambda m: f"{ROMAN.get(m.group(1).lower(), m.group(1))}. ",
        value,
        flags=re.I,
    )
    value = re.sub(r"^\(([a-z])\)\s*", lambda m: f"Herufi {m.group(1).upper()}. ", value, flags=re.I)
    value = value.replace("→", ", inaelekea, ").replace("←", ", inatoka, ")
    return value


async def generate(cache: Path, texts: list[str], concurrency: int) -> None:
    semaphore = asyncio.Semaphore(concurrency)
    completed = 0

    async def one(text: str) -> None:
        nonlocal completed
        target = cache / f"{hashlib.sha256(text.encode()).hexdigest()}.mp3"
        if target.exists() and target.stat().st_size > 512:
            completed += 1
            return
        async with semaphore:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(target))
            completed += 1
            if completed % 100 == 0:
                print(f"Generated {completed}/{len(texts)} unique narration clips.", flush=True)

    await asyncio.gather(*(one(text) for text in texts))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=6)
    args = parser.parse_args()

    source_texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))
    source_audio = json.loads((ROOT / "content/i18n/sw/audios.json").read_text(encoding="utf-8"))
    narration = {key: spoken_text(source_texts.get(key, "")) for key in source_audio}
    narration = {key: value for key, value in narration.items() if value}
    unique = sorted(set(narration.values()))
    cache = ROOT / ".cache" / f"narration-{VOICE}-{RATE.replace('%', 'pct')}"
    cache.mkdir(parents=True, exist_ok=True)
    asyncio.run(generate(cache, unique, args.concurrency))

    mapping = {key: f"{key}.mp3?v={VERSION}" for key in narration}
    for lang in LANGUAGES:
        audio_dir = ROOT / f"content/i18n/{lang}/audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        for key, text in narration.items():
            cached = cache / f"{hashlib.sha256(text.encode()).hexdigest()}.mp3"
            shutil.copyfile(cached, audio_dir / f"{key}.mp3")
        (ROOT / f"content/i18n/{lang}/audios.json").write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Wrote {len(narration)} synchronized clips per language from {len(unique)} unique recordings.")


if __name__ == "__main__":
    main()
