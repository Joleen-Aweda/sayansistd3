"""Import and optimize the page-level sign-language videos for the ADT reader."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("/Users/joleen/Desktop/28. SAYANSI STD III - Complete")
OUTPUT_DIR = ROOT / "content/i18n/sw/video"


def numbered_sources(source_dir: Path) -> dict[int, Path]:
    videos: dict[int, Path] = {}
    for path in source_dir.glob("*.mp4"):
        match = re.search(r"(\d+)", path.stem)
        if match:
            number = int(match.group(1))
            if number in videos:
                raise RuntimeError(f"Duplicate video number {number}: {path}")
            videos[number] = path
    return videos


def transcode(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp.mp4")
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-an",
            "-vf",
            "scale=640:-2:flags=lanczos,fps=25",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "31",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(temporary),
        ],
        check=True,
    )
    temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
    content_pages = [page for page in pages if "page_number" in page]
    sources = numbered_sources(args.source)
    expected = set(range(1, len(content_pages) + 1))
    if set(sources) != expected:
        raise RuntimeError(
            f"Expected video numbers 1-{len(content_pages)}; "
            f"missing={sorted(expected - set(sources))}, "
            f"unexpected={sorted(set(sources) - expected)}"
        )

    jobs = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for number in sorted(expected):
            destination = OUTPUT_DIR / f"video-{number:03d}.mp4"
            jobs.append(
                executor.submit(transcode, sources[number], destination)
            )
        for completed, job in enumerate(as_completed(jobs), start=1):
            job.result()
            print(f"Optimized {completed}/{len(jobs)}", flush=True)

    # Keep one physical set under the default Swahili locale. The reader prefixes
    # mappings with content/i18n/{language}/video/, so sw-TZ can resolve the same
    # files through a relative locale path without duplicating large media.
    sw_mapping = {
        f"video-{number + 1}": f"video-{number:03d}.mp4"
        for number in sorted(expected)
    }
    sw_tz_mapping = {
        key: f"../../sw/video/{filename}"
        for key, filename in sw_mapping.items()
    }
    mappings = {"sw": sw_mapping, "sw-TZ": sw_tz_mapping}
    for language, mapping in mappings.items():
        video_dir = ROOT / f"content/i18n/{language}/video"
        video_dir.mkdir(parents=True, exist_ok=True)
        (video_dir / ".gitkeep").touch(exist_ok=True)
        (ROOT / f"content/i18n/{language}/videos.json").write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    total_bytes = sum(path.stat().st_size for path in OUTPUT_DIR.glob("*.mp4"))
    print(
        f"Imported {len(jobs)} silent videos ({total_bytes / 1_000_000:.1f} MB)."
    )


if __name__ == "__main__":
    main()
