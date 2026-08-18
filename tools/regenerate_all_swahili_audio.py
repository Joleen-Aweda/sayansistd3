"""Regenerate the complete published narration with one Tanzanian Swahili voice."""

import argparse
import asyncio
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("sw", "sw-TZ")
VOICE = "sw-TZ-DaudiNeural"
RATE = "-5%"
VERSION = "176"
ROMAN = {
    "i": "moja", "ii": "mbili", "iii": "tatu", "iv": "nne", "v": "tano",
    "vi": "sita", "vii": "saba", "viii": "nane", "ix": "tisa", "x": "kumi",
}
LETTER_NAMES = {"a": "a", "b": "be", "c": "che", "d": "de"}
ACTIVITY_ORDINALS = {
    "1": "kwanza", "2": "pili", "3": "tatu", "4": "nne", "5": "tano",
    "6": "sita", "7": "saba", "8": "nane", "9": "tisa",
}
FIGURE_ORDINALS = {
    "1": "kwanza", "2": "pili", "3": "tatu", "4": "nne", "5": "tano",
    "6": "sita", "7": "saba", "8": "nane", "9": "tisa", "10": "kumi",
    "11": "kumi na moja", "12": "kumi na mbili", "13": "kumi na tatu",
    "14": "kumi na nne", "15": "kumi na tano", "16": "kumi na sita",
    "17": "kumi na saba", "18": "kumi na nane", "19": "kumi na tisa",
    "20": "ishirini", "21": "ishirini na moja", "22": "ishirini na mbili",
}


def spoken_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if not value or re.fullmatch(r"[_\.\-–—\s]+", value):
        return ""
    # Answer-field tokens are application instructions, not spoken book text.
    value = re.sub(r"\[\[blank:[^\]]+\]\]", "", value)
    value = re.sub(r"\s+([.,;:!?])", r"\1", value)
    # Keep the printed mascot name as "Tux", but pronounce it as "Tuk-si".
    value = re.sub(r"\bTux\b", "Tuk-si", value, flags=re.I)
    value = re.sub(r"\ba mpaka d\b", "a mpaka de", value, flags=re.I)
    # A line break gives the voice a short silent pause before "Vitu" without
    # adding a filler vowel or any other spoken character.
    value = re.sub(r"\bKundi ([A-G])\.\s+Vitu\b", r"Kundi \1.\nVitu", value)
    value = re.sub(r"\s*\[\[blank:[^\]]+\]\]", "", value, flags=re.I)
    value = re.sub(r"\bIII\s*[-–—]\s*VI\b", "tatu mpaka darasa la sita", value, flags=re.I)
    value = re.sub(r"\bIII\s*-\s*VI\b", "tatu mpaka sita", value, flags=re.I)
    value = re.sub(r"\bZoezi la 1\b", "Zoezi la kwanza", value, flags=re.I)
    value = re.sub(r"\bZoezi la 2\b", "Zoezi la pili", value, flags=re.I)
    value = re.sub(
        r"\bJaribio la ([1-9])\b",
        lambda match: f"Jaribio la {ACTIVITY_ORDINALS[match.group(1)]}",
        value,
        flags=re.I,
    )
    value = re.sub(
        r"\bKielelezo (\d+)(?:\(([a-z])\))?",
        lambda match: (
            f"Kielelezo cha {FIGURE_ORDINALS.get(match.group(1), match.group(1))}"
            + (
                f", {LETTER_NAMES.get(match.group(2).lower(), match.group(2))}"
                if match.group(2) else ""
            )
        ),
        value,
        flags=re.I,
    )
    value = re.sub(
        r"\bKazi ya kufanya ya ([1-9])\b",
        lambda match: f"Kazi ya kufanya ya {ACTIVITY_ORDINALS[match.group(1)]}",
        value,
        flags=re.I,
    )
    # A hyphen within a number is only a visual separator. Removing it keeps
    # the voice engine from announcing the punctuation as "ondoa".
    value = re.sub(r"(?<=\d)[-‐‑–—](?=\d)", " ", value)
    value = re.sub(
        r"^\(([ivx]+)\)\s*",
        lambda m: f"{ROMAN.get(m.group(1).lower(), m.group(1))}. ",
        value,
        flags=re.I,
    )
    value = re.sub(
        r"^\(([a-z])\)\s*",
        lambda m: (
            "a.\n" if m.group(1).lower() == "a"
            else f"{LETTER_NAMES.get(m.group(1).lower(), f'Herufi {m.group(1).upper()}')}. "
        ),
        value,
        flags=re.I,
    )
    # Keep the printed honorific abbreviations while pronouncing their full Swahili forms.
    value = re.sub(r"\bDkt\.\s*", "Doctor ", value)
    value = re.sub(r"\bBw\.\s*", "Bwana ", value)
    value = re.sub(r"\bBi\.\s*", "Bibi ", value)
    # Give the English organization name and initialism an unambiguous spoken form.
    value = value.replace("K Desktop Environment (KDE)", "Kei Desktop Environment, Kei Di Ii")
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
    parser.add_argument("--changed-only", action="store_true", help="Regenerate image, namba, contents and merged-page narration only")
    parser.add_argument("--ids", help="Comma-separated narration IDs to regenerate")
    parser.add_argument("--figure-images", action="store_true", help="Regenerate image descriptions beginning with Kielelezo")
    parser.add_argument("--letter-labels", action="store_true", help="Regenerate narration beginning with labels (a) through (d)")
    args = parser.parse_args()

    source_texts = json.loads((ROOT / "content/i18n/sw/texts.json").read_text(encoding="utf-8"))
    source_audio = json.loads((ROOT / "content/i18n/sw/audios.json").read_text(encoding="utf-8"))
    all_keys = set(source_audio) | {
        "pg002_n0010", "pg002_n0010_easy_read", "pg002_n0014", "pg002_n0014_easy_read",
        "pg002_n0017", "pg002_n0017_easy_read",
        "pg006_n0016", "pg006_n0016_easy_read",
        "pg004_n0027", "pg004_n0028", "pg004_im001", "pg004_n0030", "pg004_n0031", "pg004_n0032"
    }
    narration = {key: spoken_text(source_texts.get(key, "")) for key in all_keys}
    # Keep the printed quantity for sighted readers, but avoid repeating it in narration.
    for key in ("pg010_n0005", "pg010_n0005_easy_read"):
        narration[key] = narration.get(key, "").replace("tatu (3)", "tatu")
    # "aa" forces a pure Swahili /a/ vowel without adding an "e" sound.
    for key in ("pg014_n0017", "pg014_n0017_easy_read"):
        narration[key] = "aa... Kemia ni tawi la sayansi linalohusika na maada na nishati."
    for key in ("pg015_n0017", "pg015_n0017_easy_read"):
        narration[key] = "aa... Sayansi husaidia kujenga maarifa na stadi mbalimbali."
    # Keep the visible label unchanged while separating its letter from the
    # item name with a silent pause.
    for key in ("pg035_n0014", "pg035_n0014_easy_read"):
        narration[key] = "a.\nNazi"
    # Read the page 38 table row in discrete fields, separated only by silent
    # pauses, so none of its headings run into the following content.
    for key in ("pg038_n0041", "pg038_n0041_easy_read"):
        narration[key] = (
            "Namba.\na.\nPicha.\na.\nPicha inaonesha pua ya binadamu.\n"
            "Namba.\nbe.\nPicha.\nbe.\nPicha inaonesha mdomo wa binadamu wenye ulimi.\n"
            "Namba.\nche.\nPicha.\nche.\nPicha inaonesha macho mawili ya binadamu.\n"
            "Namba.\nde.\nPicha.\nde.\nPicha inaonesha sikio la binadamu.\n"
            "Kazi.\nMoja.\nKutambua maua yenye rangi tofauti bustanini.\n"
            "Mbili.\nKusikiliza nyimbo kuhusu utunzaji wa mazingira.\n"
            "Tatu.\nKutambua ladha ya dawa chungu.\n"
            "Nne.\nKutambua harufu ya kitu kinachoungua."
        )
    page_39_table_rows = {
        "pg039_n0011": (
            "Namba.\nbe.\nPicha.\nbe.\nPicha inaonesha mdomo wa binadamu wenye ulimi.\n"
            "Namba.\nche.\nPicha.\nche.\nPicha inaonesha macho mawili ya binadamu.\n"
            "Namba.\nde.\nPicha.\nde.\nPicha inaonesha sikio la binadamu.\n"
            "Kazi.\nMoja.\nKutambua maua yenye rangi tofauti bustanini.\n"
            "Mbili.\nKusikiliza nyimbo kuhusu utunzaji wa mazingira.\n"
            "Tatu.\nKutambua ladha ya dawa chungu.\n"
            "Nne.\nKutambua harufu ya kitu kinachoungua."
        ),
        "pg039_n0017": "Namba.\nche.\nPicha.\nPicha inaonesha macho mawili ya binadamu.\nKazi.\nTatu.\nKutambua ladha ya dawa chungu.",
        "pg039_n0023": "Namba.\nde.\nPicha.\nPicha inaonesha sikio la binadamu.\nKazi.\nNne.\nKutambua harufu ya kitu kinachoungua.",
    }
    for key, row_narration in page_39_table_rows.items():
        narration[key] = row_narration
        narration[f"{key}_easy_read"] = row_narration
    page_39_taste_rows = {
        "pg039_n0040": "Namba.\na.\nLadha.\nUtamu.\nChakula.\nAsali, sukari.",
        "pg039_n0047": "Namba.\nbe.\nLadha.\nUmami.\nChakula.",
        "pg039_n0053": "Namba.\nche.\nLadha.\nUchachu.\nChakula.",
        "pg039_n0059": "Namba.\nde.\nLadha.\nUchungu.\nChakula.",
    }
    for key, row_narration in page_39_taste_rows.items():
        narration[key] = row_narration
        narration[f"{key}_easy_read"] = row_narration
    classification_table_pages = {
        "pg046_n0017": (
            "Kiumbehai na kitu kisicho hai.\n"
            "Namba moja.\nPicha inaonesha mmea wa mahindi.\n"
            "Namba mbili.\nPicha inaonesha jiwe.\n"
            "Namba tatu.\nPicha inaonesha ng'ombe.\n"
            "Namba nne.\nPicha inaonesha kinyonga juu ya tawi.\n"
            "Namba tano.\nPicha inaonesha nyumba."
        ),
        "pg047_n0014": (
            "Kiumbehai na kitu kisicho hai.\n"
            "Namba sita.\nPicha inaonesha kobe.\n"
            "Namba saba.\nPicha inaonesha simu ya mkononi.\n"
            "Namba nane.\nPicha inaonesha sungura.\n"
            "Namba tisa.\nPicha inaonesha jongoo aliyekunjamana.\n"
            "Namba kumi.\nPicha inaonesha mpira wa miguu.\n"
            "Namba kumi na moja.\nPicha inaonesha kikombe."
        ),
    }
    for key, table_narration in classification_table_pages.items():
        narration[key] = table_narration
        narration[f"{key}_easy_read"] = table_narration
    page_54_chicken_images = {
        "pg054_im002": "Kielelezo namba saba.\na.\nKinaonesha kuku amekalia mayai kwenye kiota.",
        "pg054_im001": "Kielelezo namba saba.\nbe.\nKinaonesha vifaranga wawili wakiwa kwenye kiota pamoja na mayai yaliyoanguliwa na mengine ambayo bado hayajaanguliwa.",
        "pg054_im003": "Kielelezo namba saba.\nche.\nKinaonesha kuku mama akiongozana na vifaranga wake vitano.",
    }
    for key, image_narration in page_54_chicken_images.items():
        narration[key] = image_narration
    for key in ("pg064_n0008", "pg064_n0008_easy_read"):
        narration[key] = (
            narration.get(key, "")
            .replace("(X)", "")
            .replace("(a)-(e)", "aa.\nmpaka.\ne")
        )
    # A trailing continuation mark gives the standalone heading the same
    # connected pronunciation as "Ndege ni..." in the following sentence.
    for key in ("pg065_n0004", "pg065_n0004_easy_read"):
        narration[key] = "Ndege,"
    for key in ("pg022_n0018", "pg022_n0018_easy_read"):
        narration[key] = narration.get(key, "").replace("mbili (2)", "mbili")
    # Figure 3 is one diagram: narrate its hierarchy once, in visual reading order.
    for key in ("pg012_n0002", "pg012_n0002_easy_read"):
        narration[key] = "Matawi ya sayansi. Moja, Baiolojia. Mbili, Fizikia. Tatu, Kemia."
    narration = {key: value for key, value in narration.items() if value}
    changed_ids = {
        key for key, value in narration.items()
        if "_im" in key or "namba" in value.lower() or key in {
            "pg003_n0006", "pg003_n0009", "pg003_n0014", "pg003_n0019",
            "pg003_n0024", "pg003_n0029", "pg003_n0034",
            "pg004_n0027", "pg004_n0028", "pg004_n0030", "pg004_n0031", "pg004_n0032",
        }
    }
    requested_ids = set(args.ids.split(",")) if args.ids else None
    if args.figure_images:
        requested_ids = {key for key, value in narration.items() if "_im" in key and value.startswith("Kielelezo ")}
    if args.letter_labels:
        requested_ids = {
            key for key in narration
            if re.match(r"^\([a-d]\)", source_texts.get(key, ""), flags=re.I)
            or key in {"pg038_n0041", "pg038_n0041_easy_read"}
        }
    selected = {
        key: value for key, value in narration.items()
        if (requested_ids is None or key in requested_ids)
        and (not args.changed_only or key in changed_ids)
    }
    unique = sorted(set(selected.values()))
    cache = ROOT / ".cache" / f"narration-{VOICE}-{RATE.replace('%', 'pct')}"
    cache.mkdir(parents=True, exist_ok=True)
    asyncio.run(generate(cache, unique, args.concurrency))

    # Preserve hand-tuned mappings and update only clips selected for regeneration.
    mapping = dict(source_audio)
    mapping.update({key: f"{key}.mp3?v={VERSION}" for key in selected})
    for lang in LANGUAGES:
        audio_dir = ROOT / f"content/i18n/{lang}/audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        for key, text in selected.items():
            cached = cache / f"{hashlib.sha256(text.encode()).hexdigest()}.mp3"
            shutil.copyfile(cached, audio_dir / f"{key}.mp3")
        # Use the correctly pronounced first word from "Ndege ni..." for the
        # standalone heading; the voice engine mispronounces isolated "Ndege".
        paragraph_clip = audio_dir / "pg065_n0006.mp3"
        if paragraph_clip.exists():
            for heading_key in (
                "pg065_n0004", "pg065_n0004_easy_read",
                "pg068_n0015", "pg068_n0015_easy_read",
            ):
                subprocess.run(
                    [
                        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-i", str(paragraph_clip),
                        "-af", "atrim=start=0:end=0.545,afade=t=out:st=0.52:d=0.025,apad=pad_dur=0.9",
                        "-t", "1.43",
                        str(audio_dir / f"{heading_key}.mp3"),
                    ],
                    check=True,
                )
        (ROOT / f"content/i18n/{lang}/audios.json").write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Wrote {len(selected)} changed synchronized clips per language from {len(unique)} unique recordings; mapped {len(narration)} clips.")


if __name__ == "__main__":
    main()
