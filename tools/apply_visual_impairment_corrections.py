"""Apply the approved visual-impairment corrections to the local ADT bundle."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("sw", "sw-TZ")
BUNDLE_VERSION = "189"
STARFALL_URL = "https://www.starfall.com/h/creative-corner/mixpaint/?sn=colors"

ACTIVITY_HEADINGS = {
    "pg099_n0018": "Kazi ya kufanya namba 2",
    "pg101_n0016": "Kazi ya kufanya namba 3",
    "pg103_n0013": "Kazi ya kufanya namba 4",
    "pg105_n0003": "Kazi ya kufanya namba 5",
    "pg106_n0013": "Kazi ya kufanya namba 6",
    "pg108_n0011": "Kazi ya kufanya namba 7",
    "pg110_n0003": "Kazi ya kufanya namba 8",
}

REPLACEMENTS = {
    **ACTIVITY_HEADINGS,
    "pg100_n0007": "Kompyuta ya mezani, kompyuta mpakato, tableti au kishikwambi iliyosakinishwa programu ya mchezo",
    "pg101_n0029": "Kompyuta ya mezani, kompyuta mpakato, tableti au kishikwambi iliyosakinishwa programu ya mchezo",
    "pg103_n0026": "Kompyuta ya mezani, kompyuta mpakato, tableti au kishikwambi iliyosakinishwa programu ya mchezo",
    "pg105_n0016": "Kompyuta ya mezani, kompyuta mpakato, tableti au kishikwambi iliyosakinishwa programu ya mchezo",
    "pg106_n0025": "Kompyuta ya mezani, kompyuta mpakato, tableti au kishikwambi iliyosakinishwa programu ya mchezo",
    "pg108_n0027": "Kompyuta ya mezani, kompyuta mpakato, tableti au kishikwambi iliyosakinishwa programu ya mchezo",
    "pg110_n0018": "Kompyuta ya mezani, kompyuta mpakato, tableti au kishikwambi iliyosakinishwa programu ya mchezo",
    "pg108_n0032": "1. Fungua Starfall Mix and Paint, kisha chagua rangi unayoipenda kutoka kwenye paleti ya rangi.",
    "pg109_n0026": "Nini kimekuvutia katika mchezo wa Starfall Mix and Paint au mchezo wa mchoro sahili?",
}

NEW_TEXTS = {
    "pg099_n0016": "Mchezo mwingine fikivu:",
    "pg099_n0017": "Starfall Mix and Paint",
    "pg108_n0014": "Mchezo mwingine fikivu:",
    "pg108_n0015": "Starfall Mix and Paint",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def replace_data_id_text(html: str, text_id: str, value: str) -> str:
    pattern = re.compile(
        rf'(<[^>]+\bdata-id=["\']{re.escape(text_id)}["\'][^>]*>)(.*?)(</[^>]+>)',
        flags=re.DOTALL,
    )
    updated, count = pattern.subn(rf"\g<1>{value}\g<3>", html)
    if count == 0:
        raise RuntimeError(f"Could not find visible element for {text_id}")
    return updated


def update_html() -> None:
    pages = read_json(ROOT / "content/pages.json")
    for entry in pages:
        path = ROOT / entry["href"]
        html = path.read_text(encoding="utf-8")
        for text_id, value in {**REPLACEMENTS, **NEW_TEXTS}.items():
            if f'data-id="{text_id}"' in html:
                html = replace_data_id_text(html, text_id, value)

        # Keep non-data-id fallback headings synchronized.
        for number in range(2, 9):
            html = html.replace(
                f"Kazi ya kufanya ya {number}", f"Kazi ya kufanya namba {number}"
            )
        html = html.replace("tableti au simumaizi", "tableti au kishikwambi")

        end_id = f'{entry["section_id"]}_end'
        end_markup = (
            f'<span class="sr-only" data-id="{end_id}">Mwisho wa ukurasa.</span>'
        )
        if f'data-id="{end_id}"' not in html:
            final_section = html.rfind("</section>")
            if final_section < 0:
                raise RuntimeError(f"No closing section in {path.name}")
            html = html[:final_section] + end_markup + html[final_section:]
        path.write_text(html, encoding="utf-8")

    intro = ROOT / "pg099_sec001.html"
    html = intro.read_text(encoding="utf-8")
    if 'data-id="pg099_n0016"' not in html:
        anchor = (
            '        <span data-id="pg099_n0014">Katika kujifunza na kucheza michezo hii utatumia programu tumizi inayoitwa &#x201c;Gcompris&#x201d;.</span> '
            '<span data-id="pg099_n0015">Programu hiyo inaweza kupakuliwa kutoka https://tie.go.tz/pages/download-software</span>\n'
            '      </p>'
        )
        starfall = (
            anchor + '\n'
            '      <p class="mt-5 text-left text-[1.65rem] leading-[1.45] text-zinc-800 max-lg:text-[1.45rem] max-sm:text-[1.15rem]">\n'
            '        <span data-id="pg099_n0016">Mchezo mwingine fikivu ni</span> '
            f'<a href="{STARFALL_URL}" target="_blank" rel="noopener noreferrer" '
            'aria-label="Fungua Starfall Mix and Paint katika kichupo kipya" '
            'class="font-semibold text-sky-700 underline decoration-2 underline-offset-4">'
            '<span data-id="pg099_n0017">Starfall Mix and Paint</span></a>.\n'
            '      </p>'
        )
        if anchor not in html:
            raise RuntimeError("Could not find Starfall intro insertion point")
        html = html.replace(anchor, starfall, 1)
        intro.write_text(html, encoding="utf-8")

    activity = ROOT / "pg108_sec002.html"
    html = activity.read_text(encoding="utf-8")
    if 'data-id="pg108_n0014"' not in html:
        anchor = (
            '<p><span data-id="pg108_n0017" class="font-extrabold">Jina la mchezo:</span>'
            '<span> </span><span data-id="pg108_n0018">Mchezo wa mchoro sahili</span></p>'
        )
        starfall = anchor + (
            '\n            <p><span data-id="pg108_n0014" class="font-extrabold">'
            'Mchezo mwingine fikivu:</span><span> </span>'
            f'<a href="{STARFALL_URL}" target="_blank" rel="noopener noreferrer" '
            'aria-label="Fungua Starfall Mix and Paint katika kichupo kipya" '
            'class="font-semibold text-sky-700 underline decoration-2 underline-offset-4">'
            '<span data-id="pg108_n0015">Starfall Mix and Paint</span></a></p>'
        )
        if anchor not in html:
            raise RuntimeError("Could not find Starfall activity insertion point")
        html = html.replace(anchor, starfall, 1)
        activity.write_text(html, encoding="utf-8")


def update_catalogs() -> None:
    pages = read_json(ROOT / "content/pages.json")
    end_texts = {
        f'{entry["section_id"]}_end': "Mwisho wa ukurasa." for entry in pages
    }
    changed_ids = set(REPLACEMENTS) | set(NEW_TEXTS)
    for language in LANGUAGES:
        directory = ROOT / f"content/i18n/{language}"
        texts = read_json(directory / "texts.json")
        audios = read_json(directory / "audios.json")
        for text_id, value in {**REPLACEMENTS, **NEW_TEXTS}.items():
            texts[text_id] = value
            texts[f"{text_id}_easy_read"] = value
            audios[text_id] = f"{text_id}.mp3?v={BUNDLE_VERSION}"
            audios[f"{text_id}_easy_read"] = (
                f"{text_id}_easy_read.mp3?v={BUNDLE_VERSION}"
            )
        texts.update(end_texts)
        for text_id in end_texts:
            audios[text_id] = f"page_end.mp3?v={BUNDLE_VERSION}"

        for text_id in (
            "pg002_n0012",
            "pg002_n0013",
            "pg002_n0012_easy_read",
            "pg002_n0013_easy_read",
        ):
            audios[text_id] = f"{text_id}.mp3?v={BUNDLE_VERSION}"

        write_json(directory / "texts.json", texts)
        write_json(directory / "audios.json", audios)

    config_path = ROOT / "assets/config.json"
    config = read_json(config_path)
    config["bundleVersion"] = BUNDLE_VERSION
    write_json(config_path, config)

    toc_path = ROOT / "content/toc.json"
    toc = read_json(toc_path)
    for entry in toc:
        chapter_id = entry.get("chapter_id")
        if chapter_id in ACTIVITY_HEADINGS:
            entry["title"] = ACTIVITY_HEADINGS[chapter_id]
    write_json(toc_path, toc)


def main() -> None:
    update_html()
    update_catalogs()
    print("Applied Starfall, terminology, activity-heading and page-ending corrections.")


if __name__ == "__main__":
    main()
