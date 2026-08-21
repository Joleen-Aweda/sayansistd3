"""Validate sign-language mappings and optimized video delivery properties."""

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))


def probe(path: Path) -> dict:
    return json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=codec_name,codec_type,width,height",
                "-of",
                "json",
                str(path),
            ],
            text=True,
        )
    )


def main() -> None:
    config = json.loads((ROOT / "assets/config.json").read_text(encoding="utf-8"))
    assert config["features"]["signLanguage"] is True
    assert config["bundleVersion"] == "187"

    concurrent_script = ROOT / "assets/concurrent-sign-language-playback.js"
    assert concurrent_script.is_file()
    for page in PAGES:
        markup = (ROOT / page["href"]).read_text(encoding="utf-8")
        assert (
            'assets/concurrent-sign-language-playback.js?v=187' in markup
        ), page["href"]

    expected_keys = {f"video-{number}" for number in range(1, len(PAGES) + 1)}
    mappings = []
    for language in ("sw", "sw-TZ"):
        mapping = json.loads(
            (ROOT / f"content/i18n/{language}/videos.json").read_text(
                encoding="utf-8"
            )
        )
        assert set(mapping) == expected_keys
        mappings.append(mapping)
    assert mappings[0] == mappings[1]

    files = sorted((ROOT / "content/sign-language").glob("*.mp4"))
    assert len(files) == len(PAGES)
    for path in files:
        metadata = probe(path)
        streams = metadata["streams"]
        video = [stream for stream in streams if stream["codec_type"] == "video"]
        audio = [stream for stream in streams if stream["codec_type"] == "audio"]
        assert len(video) == 1
        assert video[0]["codec_name"] == "h264"
        assert video[0]["width"] == 640 and video[0]["height"] == 360
        assert not audio, f"Audio track remains in {path.name}"
        with path.open("rb") as stream:
            header = stream.read(1_000_000)
        assert header.find(b"moov") < header.find(b"mdat"), path.name

    print(f"Validated {len(files)} silent, fast-start sign-language videos.")


if __name__ == "__main__":
    main()
