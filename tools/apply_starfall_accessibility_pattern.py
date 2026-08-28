"""Apply the Standard 4 Quorum-style accessibility pattern to Starfall."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "192"
STARFALL_URL = "https://www.starfall.com/h/index-acv.php"

TEXT_UPDATES = {
    # Introduction and accessible route.
    "pg099_n0014": "Katika kujifunza na kucheza michezo hii unaweza kutumia programu tumizi ya GCompris au chaguo fikivu la Starfall.",
    "pg099_n0016": "Starfall ni tovuti ya kujifunzia yenye Kielezo Fikivu kinachoweza kutumiwa kwa kisoma skrini na kibodi.",
    "pg099_n0017": "Fungua Kielezo Fikivu cha Starfall",
    # Activity 2: maze.
    "pg099_n0019": "Kutafuta mtandao wa njia kwa GCompris/Starfall",
    "pg099_n0024": "Mchezo wa mtandao wa njia wa GCompris/shughuli fikivu ya Starfall",
    "pg099_n0027": "Kufuata maelekezo kwa mpangilio sahihi ili kufikia lengo",
    "pg099_im001": "Maelezo ya GCompris: Picha inaonesha mchezo wa mtandao wa njia wenye njia za kupita; mshale mwekundu unaonyesha mwanzo upande wa kushoto na mshale wa kijani unaonyesha njia ya kutoka upande wa kulia. Maelezo ya Starfall: Katika Kielezo Fikivu cha Starfall, tumia Tab kusikiliza machaguo na Enter kuchagua shughuli, kisha fuata maelekezo yanayosomwa na kisoma skrini.",
    "pg100_im001": "Maelezo ya GCompris: Kielelezo namba 2 kinaonesha mchezo wa mtandao wa njia unaomuonyesha Tux akiwa mwanzo wa njia ndani ya ramani, akielekezwa kufika kwenye mlango wa kutokea ulio upande wa kulia. Maelezo ya Starfall: Katika Kielezo Fikivu, tumia Tab kufikia shughuli ya maelekezo au fumbo, bonyeza Enter kuifungua, kisha fuata maelekezo ya sauti au kisoma skrini hadi mwisho.",
    # Exercise 1.
    "pg101_n0005": "1. Nini hutokea unapofuata njia isiyo sahihi katika GCompris au unapochagua jibu lisilo sahihi katika Starfall?",
    "pg101_n0007": "2. Je, uliwahi kufuata mwelekeo usio sahihi katika GCompris au Starfall?",
    "pg101_n0008": "Nini kilitokea?",
    "pg101_n0010": "3. Ulifanya nini baada ya kubaini kuwa umefuata mwelekeo usio sahihi?",
    "pg101_n0012": "4. Ulitumia mbinu gani kufuata maelekezo ya mchezo?",
    "pg101_n0014": "5. Ni shughuli gani za kila siku zinahusiana na mchezo wa mtandao wa njia au shughuli ya Starfall uliyofanya?",
    # Activity 3: route coding.
    "pg101_n0017": "Kutafuta njia kwa GCompris au Starfall",
    "pg101_n0020": "Usimbaji wa njia katika GCompris au shughuli ya maelekezo katika Starfall",
    "pg101_n0023": "Kufuata na kupanga maelekezo ili kufikia lengo",
    "pg102_im001": "Maelezo ya GCompris: Kielelezo namba 3 kinaonesha mchezo wa kusimbaji wa njia wenye gridi ya vigae; Tux yuko mwanzo juu kushoto akifuata njia ya vigae vya kijivu kuelekea bendera nyekundu chini kushoto, huku pembeni kukiwa na mishale ya kuelekeza juu, chini, kushoto na kulia. Maelezo ya Starfall: Fungua Kielezo Fikivu, tumia Tab na Enter kuchagua shughuli ya maelekezo, kisha tumia maelekezo yanayotolewa kwa sauti au maandishi kufuata hatua kwa mpangilio hadi lengo.",
    # Exercise 2.
    "pg103_n0005": "1. Nini hutokea unapochagua hatua isiyo sahihi katika GCompris au Starfall?",
    "pg103_n0007": "2. Ulitumiaje maelekezo ya sauti, maandishi au vitufe kuepuka vizuizi?",
    "pg103_n0009": "3. Ni mara ngapi ulifuata njia au hatua isiyo sahihi?",
    "pg103_n0011": "4. Utatumiaje mbinu ulizojifunza katika GCompris au Starfall shuleni au nyumbani?",
    # Activity 4: logic and decoding.
    "pg103_n0014": "Kugundua mantiki kwa GCompris au Starfall",
    "pg103_n0017": "Usimbuaji wa njia katika GCompris au shughuli ya mantiki katika Starfall",
    "pg103_n0020": "Kutumia mantiki na maelekezo ili kufikia lengo",
    "pg104_im001": "Maelezo ya GCompris: Kielelezo namba 4 kinaonesha mchezo wa gridi wenye Tux akianzia kushoto, akifuata mfuatano wa mishale ya maelekezo kuelekea bendera nyekundu huku akikwepa mawe, maziwa, miti na vichaka; hitilafu ni sifuri. Maelezo ya Starfall: Katika Kielezo Fikivu, chagua shughuli ya mantiki au kupanga hatua, sikiliza maelekezo, tumia Tab kufikia machaguo na Enter kuthibitisha kila hatua.",
    # Exercise 3.
    "pg104_n0011": "1. Nini hutokea unapochagua hatua yenye kizuizi au jibu lisilo sahihi katika GCompris au Starfall?",
    "pg104_n0012": "2. Ulifanya hatua ngapi zisizo sahihi?",
    "pg104_n0013": "3. Ulifanya nini kupunguza hitilafu katika hatua zilizofuata?",
    "pg104_n0014": "4. Ulitumia mbinu gani kumaliza shughuli bila kupata hitilafu?",
    "pg104_n0015": "5. Ni ujuzi gani umejifunza kupitia GCompris au Starfall?",
    # Activity 5: simplified Hanoi / puzzle.
    "pg105_n0004": "Kutumia mantiki kwa GCompris au Starfall",
    "pg105_n0007": "Mnara uliorahisishwa wa Hanoi au fumbo la Starfall",
    "pg105_n0010": "Kutumia mantiki kupanga vitu au hatua kwa mpangilio sahihi",
    "pg105_im001": "Maelezo ya GCompris: Kielelezo namba 5 kinaonesha mchezo wa Mnara wa Hanoi wenye nguzo tano; diski za rangi zenye alama zimepangwa kwenye nguzo mbalimbali, na lengo ni kujenga mnara unaofanana na ule wa upande wa kulia kwenye nguzo ya kijani iliyo wazi katikati. Maelezo ya Starfall: Fungua Kielezo Fikivu na uchague fumbo linalopatikana. Tumia Tab kupitia vitu au machaguo, Enter kuvichagua, na maelekezo ya kisoma skrini kuvipanga kwa mpangilio unaotakiwa.",
    # Exercise 4.
    "pg106_n0007": "1. Nini hutokea unapokamilisha mnara katika GCompris au fumbo katika Starfall?",
    "pg106_n0008": "2. Je, unaweza kubadilisha mpangilio bila kuzingatia hatua au kanuni za shughuli?",
    "pg106_n0009": "Toa sababu.",
    "pg106_n0010": "3. Ni kanuni zipi umejifunza kuhusu kupanga na kuhamisha vitu?",
    "pg106_n0011": "4. Umejifunza nini kutokana na GCompris au Starfall?",
    # Activity 6: Hanoi.
    "pg106_n0014": "Kutumia mantiki kwa GCompris au Starfall",
    "pg106_im001": "Maelezo ya GCompris: Picha inaonesha mnara wa Hanoi wenye nguzo na diski nne za rangi tofauti zilizopangwa kutoka kubwa chini hadi ndogo juu. Maelezo ya Starfall: Katika Kielezo Fikivu, chagua fumbo la kupanga vitu, tumia Tab na Enter kuchagua na kuhamisha kila kitu, kisha fuata kanuni zinazotolewa na kisoma skrini.",
    "pg106_n0019": "Mnara wa Hanoi au fumbo la kupanga vitu katika Starfall",
    "pg106_n0021": "Kuhamisha au kupanga vitu kwa kufuata kanuni hadi kukamilisha lengo",
    "pg107_im001_seg001_v1": "Maelezo ya GCompris: Kielelezo namba 6 kinaonesha mwanzo wa mchezo wa mnara wa Hanoi: diski tatu za ukubwa tofauti zimepangwa kwenye mnara wa kushoto, minara ya katikati na kulia ikiwa tupu. Maelezo ya Starfall: Mwanzoni mwa fumbo fikivu, sikiliza maelezo ya vitu na nafasi zake, kisha tumia Tab kufikia kila chaguo na Enter kulichagua.",
    "pg107_im001_seg002_v1": "Maelezo ya GCompris: Kielelezo namba 6 kinaonesha mwisho wa mchezo wa mnara wa Hanoi: diski tatu zote zimehamishwa na kupangwa kwa mpangilio sahihi kwenye mnara wa kulia, minara ya kushoto na katikati ikiwa tupu. Maelezo ya Starfall: Mwishoni mwa fumbo fikivu, vitu vinakuwa katika mpangilio unaotakiwa na ujumbe wa sauti au kisoma skrini huthibitisha kuwa shughuli imekamilika.",
    # Exercise 5.
    "pg107_n0027": "1. Je, mchezo wa mnara wa Hanoi au fumbo ulilochagua katika Starfall ulikuwa rahisi au mgumu?",
    "pg108_n0004": "Kwa nini unafikiri hivyo?",
    "pg108_n0006": "2. Nini hutokea unapokiuka kanuni ya kupanga vitu katika mchezo?",
    "pg108_n0008": "3. Ni shughuli zipi za kila siku zinazohusiana na kupanga vitu kwa kufuata kanuni?",
    # Activity 7: drawing and shapes.
    "pg108_n0013": "Kuunda michoro kwa GCompris au Starfall",
    "pg108_im001": "Maelezo ya GCompris: Picha inaonesha gridi ya miraba yenye miraba ya rangi nyekundu, njano na kijani, paleti ya rangi na brashi, pamoja na maneno Kuchora mchoro sahili. Maelezo ya Starfall: Katika Kielezo Fikivu, tumia Tab na Enter kuchagua shughuli inayohusiana na maumbo au ubunifu, kisha fuata maelekezo yanayosomwa kuhusu vitu na machaguo ya shughuli.",
    "pg108_n0018": "Mchezo wa mchoro sahili katika GCompris au shughuli ya maumbo katika Starfall",
    "pg108_n0014": "Chaguo fikivu:",
    "pg108_n0015": "Kielezo Fikivu cha Starfall",
    "pg108_n0021": "Kuimarisha ubunifu kwa kutumia maumbo, mpangilio na rangi katika GCompris au shughuli fikivu ya Starfall",
    "pg108_n0032": "1. Fungua Kielezo Fikivu cha Starfall, tumia Tab kufikia shughuli na Enter kuichagua, kisha fuata maelekezo yanayosomwa.",
    "pg109_im001_seg001_v1": "Maelezo ya GCompris: Kielelezo namba 7 kinaonesha mwanzo wa mchezo wa mchoro sahili wenye gridi tupu, paleti ya rangi pembeni, na mandhari ya nyasi, vilima na mawingu nyuma. Maelezo ya Starfall: Mwanzoni mwa shughuli fikivu, kisoma skrini hutaja shughuli na machaguo yake; tumia Tab kupitia machaguo na Enter kuchagua.",
    "pg109_im001_seg002_v1": "Maelezo ya GCompris: Kielelezo namba 7 kinaonesha mwisho wa mchezo wa mchoro sahili ukiwa na mchoro wa mnyama wa rangi ya pinki mwenye kichwa cha kahawia na sehemu ya njano kwenye gridi. Maelezo ya Starfall: Baada ya kukamilisha shughuli fikivu, sikiliza ujumbe wa matokeo na ueleze maumbo, mpangilio au maamuzi uliyotumia.",
    # Exercise 6.
    "pg109_n0017": "Umekamilisha kazi ngapi za sanaa au shughuli za ubunifu?",
    "pg109_n0019": "Umechagua maumbo au vitu gani katika GCompris au Starfall?",
    "pg109_n0021": "Ulitumia rangi, maumbo au mpangilio gani zaidi?",
    "pg109_n0024": "Umejifunza nini kuhusu maumbo, mpangilio na ubunifu kupitia GCompris au Starfall?",
    "pg109_n0026": "Nini kimekuvutia katika Starfall au mchezo wa mchoro sahili wa GCompris?",
    # Activity 8: route programming.
    "pg110_n0005": "Kupanga njia kwa GCompris au Starfall",
    "pg110_n0008": "Kupangilia mtandao wa njia au hatua za shughuli fikivu",
    "pg110_n0011": "Katika GCompris, Tux ana njaa; katika Starfall, fuata lengo linalosomwa katika shughuli uliyochagua.",
    "pg110_n0012": "Panga maelekezo au machaguo kwa mpangilio sahihi ili kufikia lengo.",
    "pg110_im002": "Maelezo ya GCompris: Kielelezo namba 8 kinaonesha skrini ya mchezo wa GCompris ikionyesha Tux upande wa kushoto akielekea kwa samaki kupitia visanduku vya njia, na chini kuna vitufe vya amri vya kwenda mbele, kugeuka kushoto na kugeuka kulia pamoja na agizo la kufikisha samaki kwa kutumia maagizo 5. Maelezo ya Starfall: Katika Kielezo Fikivu, tumia Tab kufikia shughuli ya maelekezo au mantiki, Enter kuichagua, na maelekezo ya kisoma skrini kupanga hatua zinazohitajika kufikia lengo.",
    "pg111_n0005": "Katika GCompris, chagua maelekezo ya mwelekeo; katika Starfall, tumia Tab kupitia machaguo yanayosomwa.",
    "pg111_n0008": "Panga maelekezo au machaguo sahihi ili kufikia lengo la shughuli.",
    "pg111_n0012": "Kamilisha hatua zote kulingana na njia au lengo la shughuli.",
    "pg111_n0013": "Kisha bonyeza “Sawa” katika GCompris au Enter kuthibitisha chaguo katika Starfall.",
    "pg111_n0016": "Unaweza kurudia GCompris au shughuli fikivu ya Starfall mara nyingi uwezavyo.",
    "pg111_n0017": "Michezo hii inakusaidia kujifunza kupanga hatua, kufuata maelekezo na kutatua changamoto.",
    # Revision exercise.
    "pg111_n0022": "1. Ulikamilisha lengo la GCompris au Starfall mara ngapi?",
    "pg111_n0023": "2. Ulitumia mbinu gani kufikia lengo la shughuli?",
    "pg111_n0024": "3. Uliwezaje kutabiri na kupanga hatua zako?",
    "pg111_n0025": "4. Ni mchezo gani wa GCompris au Starfall ulioufurahia zaidi?",
    "pg111_n0026": "5. Nini kilikuvutia zaidi katika mchezo huo?",
    "pg111_n0027": "6. Ni mambo gani muhimu umejifunza katika GCompris au Starfall?",
}

PAGES = [
    ROOT / p for p in (
        "pg099_sec001.html", "pg099_sec002.html", "pg100_sec001.html",
        "pg101_sec001.html", "pg101_sec002.html", "pg102_sec001.html",
        "pg103_sec001.html", "pg103_sec002.html", "pg104_sec001.html",
        "pg104_sec002.html", "pg105_sec001.html", "pg106_sec001.html",
        "pg106_sec002.html", "pg107_sec001.html", "pg107_sec002.html",
        "pg108_sec002.html", "pg109_sec001.html", "pg109_sec002.html",
        "pg110_sec001.html", "pg111_sec001.html", "pg111_sec002.html",
    )
]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_element_text(markup: str, text_id: str, value: str) -> str:
    pattern = re.compile(
        rf'(<(?P<tag>span|div|p|h1|h2|h3)(?=[^>]*\bdata-id="{re.escape(text_id)}")[^>]*>)'
        rf'.*?(</(?P=tag)>)',
        re.DOTALL,
    )
    return pattern.sub(lambda m: f"{m.group(1)}{value}{m.group(3)}", markup)


def replace_image_alt(markup: str, text_id: str, value: str) -> str:
    pattern = re.compile(
        rf'(<img\b(?=[^>]*(?:data-id|data-duplicate-id)="{re.escape(text_id)}")[^>]*\balt=")'
        rf'([^"]*)(")',
        re.DOTALL,
    )
    return pattern.sub(lambda m: f"{m.group(1)}{value}{m.group(3)}", markup)


for language in ("sw", "sw-TZ"):
    base = ROOT / "content" / "i18n" / language
    texts_path = base / "texts.json"
    audios_path = base / "audios.json"
    texts = json.loads(texts_path.read_text(encoding="utf-8"))
    audios = json.loads(audios_path.read_text(encoding="utf-8"))
    for text_id, value in TEXT_UPDATES.items():
        for variant in (text_id, f"{text_id}_easy_read"):
            texts[variant] = value
            audios[variant] = f"{variant}.mp3?v={VERSION}"
    for text_id, filename in list(audios.items()):
        if text_id.endswith("_end") and filename.startswith("page_end.mp3"):
            audios[text_id] = f"page_end.mp3?v={VERSION}"
    write_json(texts_path, texts)
    write_json(audios_path, audios)

for page in PAGES:
    markup = page.read_text(encoding="utf-8")
    for text_id, value in TEXT_UPDATES.items():
        if text_id in markup:
            markup = replace_element_text(markup, text_id, value)
            if "_im" in text_id:
                markup = replace_image_alt(markup, text_id, value)
    if page.name in {"pg099_sec001.html", "pg099_sec002.html", "pg108_sec002.html"}:
        markup = re.sub(
            r'href="https://www\.starfall\.com/h/creative-corner/mixpaint/\?sn=colors"',
            f'href="{STARFALL_URL}"',
            markup,
        )
        markup = markup.replace(
            'aria-label="Fungua Starfall Mix and Paint katika kichupo kipya"',
            'aria-label="Fungua Kielezo Fikivu cha Starfall katika kichupo kipya"',
        )
    if page.name == "pg099_sec002.html":
        markup = re.sub(
            r'<div class="mt-5 rounded-2xl border-2 border-sky-500 bg-sky-50 p-5 text-zinc-900">.*?</div></div><span class="sr-only"',
            '</div><span class="sr-only"',
            markup,
            flags=re.DOTALL,
        )
    page.write_text(markup, encoding="utf-8")

config_path = ROOT / "assets" / "config.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
config["bundleVersion"] = VERSION
write_json(config_path, config)

audio_ids = sorted(
    variant
    for text_id in TEXT_UPDATES
    for variant in (text_id, f"{text_id}_easy_read")
)
Path("/private/tmp/sayansi-starfall-audio-ids.txt").write_text(
    "\n".join(audio_ids) + "\n", encoding="utf-8"
)

print(f"Updated {len(TEXT_UPDATES)} Starfall-alternative narration items at version {VERSION}.")
