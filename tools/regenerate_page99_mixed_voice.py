"""Generate page 99 clips with English pronunciation for names and URLs."""

import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
ENGLISH_VOICE = "en-US-GuyNeural"
SWAHILI_VOICE = "sw-TZ-DaudiNeural"


async def generate_mixed_clip(output: Path, segments: tuple[tuple[str, str], ...]) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        paths = []
        for index, (text, voice) in enumerate(segments):
            path = temp / f"segment-{index}.mp3"
            await edge_tts.Communicate(text, voice, rate="-5%").save(str(path))
            paths.append(path)
        subprocess.run(
            ["ffmpeg", "-y", "-i", f"concat:{'|'.join(map(str, paths))}", "-c", "copy", str(output)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


async def main() -> None:
    clips = {
        "pg099_n0014": (
            ("Katika kujifunza na kucheza michezo hii utatumia programu tumizi inayoitwa", SWAHILI_VOICE),
            ("G Compri S.", ENGLISH_VOICE),
        ),
        "pg099_n0015": (
            ("Programu hiyo inaweza kupakuliwa kutoka", SWAHILI_VOICE),
            ("H T T P S colon slash slash T I E dot G O dot T Z slash pages slash download hyphen software.", ENGLISH_VOICE),
        ),
    }
    for text_id, segments in clips.items():
        source = ROOT / f"content/i18n/sw/audio/{text_id}.mp3"
        await generate_mixed_clip(source, segments)
        for language, target_id in (
            ("sw", f"{text_id}_easy_read"),
            ("sw-TZ", text_id),
            ("sw-TZ", f"{text_id}_easy_read"),
        ):
            shutil.copy2(source, ROOT / f"content/i18n/{language}/audio/{target_id}.mp3")


if __name__ == "__main__":
    asyncio.run(main())
