"""Regenerate page 4 narration with expanded spoken abbreviations."""

import asyncio
import json
import re
import shutil
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
IDS = (
    "pg004_n0011", "pg004_n0014", "pg004_n0017", "pg004_n0020",
    "pg004_n0023", "pg004_n0025", "pg004_n0030", "pg004_im001",
)


def spoken(value: str) -> str:
    for abbreviation, expansion in (
        (r"\bDkt\.", "Daktari"),
        (r"\bBw\.", "Bwana"),
        (r"\bBi\.", "Bibi"),
        (r"\bProf\.", "Profesa"),
    ):
        value = re.sub(abbreviation, expansion, value)
    return value.replace("K Desktop Environment (KDE)", "K Desktop Environment, K D E")


async def main() -> None:
    texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))
    semaphore = asyncio.Semaphore(4)

    async def generate(text_id: str) -> None:
        async with semaphore:
            target = ROOT / "content/i18n/sw/audio" / f"{text_id}.mp3"
            await edge_tts.Communicate(spoken(texts[text_id]), "sw-TZ-DaudiNeural", rate="-5%").save(str(target))

    await asyncio.gather(*(generate(text_id) for text_id in IDS))
    for text_id in IDS:
        source = ROOT / "content/i18n/sw/audio" / f"{text_id}.mp3"
        for language in ("sw", "sw-TZ"):
            for target_id in (text_id, f"{text_id}_easy_read"):
                target = ROOT / f"content/i18n/{language}/audio" / f"{target_id}.mp3"
                if target != source:
                    shutil.copyfile(source, target)
    print(f"Regenerated {len(IDS)} page 4 pronunciations in both language variants.")


if __name__ == "__main__":
    asyncio.run(main())
