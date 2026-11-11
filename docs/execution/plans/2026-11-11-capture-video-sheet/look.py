"""Session 63 D-602 A look sheets (task row 3, last step; implementation-plan.md §Verification Plan 2).

Runs only after row 3's Green. It generates three clips with the pinned FFmpeg from lavfi
sources and writes three sheets, built by the real adapters and the pure sheet functions,
into C:/Temp/av-kit/s63/look/ for Mat to look at:

* white-grid3.png: an all-white 1280x720 clip, 10 s, grid 3;
* black-grid3.png: an all-black 1280x720 clip, 10 s, grid 3;
* tall-grid5.png: a 1080x1920 (9:16) testsrc2 clip, 30 s, grid 5.

Each sheet uses max_edge 1568, the default. It goes through FFmpegAdapter.grab_frame with the
cell box and CaptureAdapter.sheet with the SHEET_LABEL labels, the same calls sheet_from_video
makes, but writes no inbox file and no database row: it never builds a CaptureService. It
never reads a video from anywhere else, makes no network request and writes nothing in the
repository. Run from the repository root with ``uv run python``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from avkit_core.services.video_input import (
    duration_ms,
    format_timecode,
    frame_times,
    sheet_cell_size,
    sheet_label,
    sheet_spacing_ms,
)
from avkit_infra.capture.adapter import CaptureAdapter
from avkit_infra.media.adapter import FFmpegAdapter

REPO_ROOT = Path(__file__).resolve().parents[4]
FFMPEG = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffmpeg.exe"
LOOK = Path("C:/Temp/av-kit/s63/look")
MAX_EDGE = 1568
X264 = ["-c:v", "libx264", "-g", "250", "-pix_fmt", "yuv420p"]
#: name -> (lavfi source, grid)
SHEETS: dict[str, tuple[str, int]] = {
    "white-grid3": ("color=c=white:s=1280x720:r=25:d=10", 3),
    "black-grid3": ("color=c=black:s=1280x720:r=25:d=10", 3),
    "tall-grid5": ("testsrc2=size=1080x1920:rate=25:duration=30", 5),
}


def main() -> int:
    if not FFMPEG.is_file():
        print(f"the pinned ffmpeg is missing (S4): {FFMPEG.relative_to(REPO_ROOT)}")
        return 1
    clips = LOOK / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    media = FFmpegAdapter(configured_path=FFMPEG)
    image = CaptureAdapter(mss_factory=lambda: None, platform="linux")
    for name, (source, grid) in SHEETS.items():
        clip = clips / f"{name}.mp4"
        command = [str(FFMPEG), "-hide_banner", "-nostdin", "-y", "-f", "lavfi", "-i", source, *X264, str(clip)]
        subprocess.run(command, check=True, capture_output=True, timeout=120)
        info = media.probe(clip, timeout_s=30)
        end = duration_ms(info.duration)
        if end is None:
            print(f"{name}: the clip has no duration")
            return 1
        times = sorted(set(frame_times(0, end, grid * grid)))
        spacing = sheet_spacing_ms(0, end, grid)
        cell = sheet_cell_size(info.width, info.height, grid, MAX_EDGE)
        cells = [media.grab_frame(clip, ms, seek="input", timeout_s=30, box=cell) for ms in times]
        empty = [ms for ms, data in zip(times, cells, strict=True) if not data.startswith(b"\x89PNG\r\n\x1a\n")]
        if empty:
            print(f"{name}: frame grab failed at {[format_timecode(ms) for ms in empty]}")
            return 1
        labels = [sheet_label(n, format_timecode(ms), spacing) for n, ms in enumerate(times, 1)]
        data = image.sheet(cells, grid=grid, cell_size=cell, labels=labels)
        out = LOOK / f"{name}.png"
        out.write_bytes(data)
        print(f"{name}: source {info.width}x{info.height}, grid {grid}, cell {cell[0]}x{cell[1]}, {len(cells)} cells, labels {labels[0]!r} .. {labels[-1]!r}, wrote {out.as_posix()} ({len(data)} B)")
    print("look: three sheets written; ask Mat to look")
    return 0


if __name__ == "__main__":
    sys.exit(main())
