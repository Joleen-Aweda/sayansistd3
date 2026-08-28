"""Generate shared and special-voice audio for visual-impairment corrections."""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
SWAHILI_VOICE = "sw-TZ-DaudiNeural"
ENGLISH_VOICE = "en-US-GuyNeural"
RATE = "-5%"


async def main() -> None:
    sw_audio = ROOT / "content/i18n/sw/audio"
    tz_audio = ROOT / "content/i18n/sw-TZ/audio"

    page_end = sw_audio / "page_end.mp3"
    await edge_tts.Communicate(
        "Mwisho wa ukurasa.", SWAHILI_VOICE, rate=RATE
    ).save(str(page_end))
    shutil.copy2(page_end, tz_audio / page_end.name)

    for text_id in ("pg099_n0017", "pg108_n0015"):
        source = sw_audio / f"{text_id}.mp3"
        await edge_tts.Communicate(
            "Starfall Mix and Paint", ENGLISH_VOICE, rate=RATE
        ).save(str(source))
        for language, variant in (
            ("sw", f"{text_id}_easy_read"),
            ("sw-TZ", text_id),
            ("sw-TZ", f"{text_id}_easy_read"),
        ):
            shutil.copy2(
                source, ROOT / f"content/i18n/{language}/audio/{variant}.mp3"
            )

    contact_pronunciations = {
        "pg002_n0012": "director dot general at T I E dot G O dot T Z.",
        "pg002_n0013": "W W W dot T I E dot G O dot T Z.",
    }
    for text_id, spoken_text in contact_pronunciations.items():
        source = sw_audio / f"{text_id}.mp3"
        await edge_tts.Communicate(
            spoken_text, ENGLISH_VOICE, rate=RATE
        ).save(str(source))
        for language, variant in (
            ("sw", f"{text_id}_easy_read"),
            ("sw-TZ", text_id),
            ("sw-TZ", f"{text_id}_easy_read"),
        ):
            shutil.copy2(
                source, ROOT / f"content/i18n/{language}/audio/{variant}.mp3"
            )

    print("Generated page-ending, Starfall name, and contact audio.")


if __name__ == "__main__":
    asyncio.run(main())
