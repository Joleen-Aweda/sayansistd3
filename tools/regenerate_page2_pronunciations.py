"""Generate page 2 clips that need English-style pronunciation."""

import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
ISBN_TEXT = "I S B N."
EMAIL_TEXT = "director dot general at T I E dot G O dot T Z."
WEBSITE_TEXT = "W W W dot T I E dot G O dot T Z."
PAGE6_WEBSITE_TEXT = "H T T P S colon slash slash O L dot T I E dot G O dot T Z, au, O L dot T I E dot G O dot T Z."
VOICE = "en-US-GuyNeural"
SWAHILI_VOICE = "sw-TZ-DaudiNeural"


async def generate_page6_mixed_voice(source: Path) -> None:
    """Read both addresses in English while keeping the conjunction in Swahili."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        segments = (
            ("H T T P S colon slash slash O L dot T I E dot G O dot T Z.", VOICE),
            ("au", SWAHILI_VOICE),
            ("O L dot T I E dot G O dot T Z.", VOICE),
        )
        paths = []
        for index, (text, voice) in enumerate(segments):
            path = temp / f"segment-{index}.mp3"
            await edge_tts.Communicate(text, voice, rate="-5%").save(str(path))
            paths.append(path)
        subprocess.run(
            ["ffmpeg", "-y", "-i", f"concat:{'|'.join(map(str, paths))}", "-c", "copy", str(source)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


async def main() -> None:
    for base_id, text in (
        ("pg002_n0017", ISBN_TEXT),
        ("pg002_n0012", EMAIL_TEXT),
        ("pg002_n0013", WEBSITE_TEXT),
    ):
        source = ROOT / f"content/i18n/sw/audio/{base_id}.mp3"
        await edge_tts.Communicate(text, VOICE, rate="-5%").save(str(source))
        for language, text_id in (
            ("sw", f"{base_id}_easy_read"),
            ("sw-TZ", base_id),
            ("sw-TZ", f"{base_id}_easy_read"),
        ):
            target = ROOT / f"content/i18n/{language}/audio/{text_id}.mp3"
            shutil.copy2(source, target)

    base_id = "pg006_n0016"
    source = ROOT / f"content/i18n/sw/audio/{base_id}.mp3"
    await generate_page6_mixed_voice(source)
    for language, text_id in (
        ("sw", f"{base_id}_easy_read"),
        ("sw-TZ", base_id),
        ("sw-TZ", f"{base_id}_easy_read"),
    ):
        shutil.copy2(source, ROOT / f"content/i18n/{language}/audio/{text_id}.mp3")


if __name__ == "__main__":
    asyncio.run(main())
