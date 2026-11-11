"""Local video input, times and names for the probe, frames and sheet steps (MEU-133 to 135).

VIDEO_INPUT, TIMECODE and VideoProbe serve `POST /conversions/probe` (MEU-133); TIME_PARSE,
FRAME_TIMES and FRAME_NAME serve `POST /captures/frames` (MEU-134); SHEET_SIZE, SHEET_TIMES,
SHEET_LABEL's sizes and SHEET_NAME serve `POST /captures/sheet` (MEU-135). Every function here is
pure apart from VIDEO_INPUT's read-only path checks.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from avkit_core.domain.errors import ValidationError
from avkit_core.domain.progress import MediaInfo

#: VIDEO_INPUT's two refusals. Neither names any part of the path.
NON_LOCAL = "path must be a local absolute file path"
NOT_FOUND = "video file not found"
#: VIDEO_INPUT: the longest path text taken.
MAX_PATH_CHARS = 4096
#: VIDEO_INPUT: a URL scheme is two or more of these before `:`, so `C:` stays a drive.
_URL_SCHEME = re.compile(r"[A-Za-z0-9+.\-]{2,}:")

# FRAME_CHECKS (MEU-134, D-577 A): the most frames one call takes, by count or by `at` times.
FRAMES_MAX = 20
# TIME_PARSE (MEU-134): 99:59:59.999, the largest time TIMECODE's two-digit hours can show.
TIME_MAX_MS = 359_999_999
# D-592: a float seconds value above this is refused before the Decimal step, whose 28-digit
# quantize raises on a huge value; far above TIME_MAX_MS, so no accepted value changes.
_FLOAT_SECONDS_GUARD = 1e9
#: TIME_PARSE: the one refusal, the longest time text, and the three forms (ASCII digits only).
TIME_REFUSED = "a time must be seconds or HH:MM:SS.mmm"
TIME_TEXT_MAX = 32
_TIME_PATTERNS = (
    re.compile(r"(\d+)(?:\.(\d{1,3}))?", re.ASCII),
    re.compile(r"(\d+):([0-5]\d)(?:\.(\d{1,3}))?", re.ASCII),
    re.compile(r"(\d+):([0-5]\d):([0-5]\d)(?:\.(\d{1,3}))?", re.ASCII),
)

# SHEET_CHECKS (MEU-135, D-601 A): a sheet is `grid` by `grid` cells.
SHEET_GRID_MIN = 2
SHEET_GRID_MAX = 5
SHEET_GRID_DEFAULT = 3
# SHEET_SIZE: the image token budgets (standard up to a 1568 px edge, high above it), the
# pixels one token covers, and the source size used when the probe gives none.
SHEET_TOKENS_STANDARD = 1568
SHEET_TOKENS_HIGH = 4784
PIXELS_PER_TOKEN = 750
SHEET_FALLBACK_SIZE = (1920, 1080)
# SHEET_LABEL: the label's starting size as a percent of the cell height, and its floor.
SHEET_LABEL_PERCENT = 14
SHEET_LABEL_MIN_PX = 8


@dataclass(frozen=True)
class VideoProbe:
    """PROBE_MAP: a local video's duration, size, codecs and streams."""

    path: str
    duration_ms: int | None
    timecode: str | None
    container: str | None
    video_codec: str | None
    audio_codec: str | None
    width: int | None
    height: int | None
    fps: float | None
    has_video: bool
    has_audio: bool


@dataclass(frozen=True)
class VideoFrame:
    """One still written by `frames_from_video`: its shot and the time it was taken at."""

    id: str
    path: str
    time_ms: int
    timecode: str
    width: int
    height: int


@dataclass(frozen=True)
class VideoFrames:
    """The result of `frames_from_video`: the video's probe and its frames in time order."""

    video: VideoProbe | None
    frames: tuple[VideoFrame, ...]


@dataclass(frozen=True)
class SheetCell:
    """One cell of a sheet: its number (1 to k, in time order), time and timecode."""

    cell: int
    time_ms: int
    timecode: str


@dataclass(frozen=True)
class SheetShot:
    """The shot `sheet_from_video` wrote: its id, path and pixel size."""

    id: str
    path: str
    width: int
    height: int


@dataclass(frozen=True)
class VideoSheet:
    """The result of `sheet_from_video`: the video's probe, the shot, the spacing and the cells."""

    video: VideoProbe | None
    shot: SheetShot | None
    spacing_ms: int
    cells: tuple[SheetCell, ...]


def _non_local(text: object) -> bool:
    """True for text that can't name a local absolute file: VIDEO_INPUT's first refusals."""
    if not isinstance(text, str) or not text or len(text) > MAX_PATH_CHARS:
        return True
    if any(_bad_char(char) for char in text):
        return True
    return _URL_SCHEME.match(text) is not None


def _bad_char(char: str) -> bool:
    """A control character (U+0000 to U+001F, U+007F) or a lone surrogate."""
    code = ord(char)
    return code <= 0x1F or code == 0x7F or 0xD800 <= code <= 0xDFFF


def require_local_video(text: str) -> Path:
    """VIDEO_INPUT: the resolved local video path, or a fixed `ValidationError`.

    The error is raised after the `try` statement has ended, so neither its `__cause__` nor its
    `__context__` is the filesystem exception, whose text names the path. The file is never
    opened or written.
    """
    if _non_local(text):
        raise ValidationError(NON_LOCAL)
    relative = False
    found: Path | None = None
    try:
        candidate = Path(text)
        if not candidate.is_absolute():
            relative = True
        else:
            resolved = candidate.resolve()
            if resolved.is_file():
                found = resolved
    except (OSError, ValueError, UnicodeError, RuntimeError):
        found = None
    if relative:
        raise ValidationError(NON_LOCAL)
    if found is None:
        raise ValidationError(NOT_FOUND)
    return found


def format_timecode(ms: int) -> str:
    """TIMECODE: `HH:MM:SS.mmm`, with two-digit hours below `TIME_MAX_MS`."""
    hours, rest = divmod(ms, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    seconds, millis = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def duration_ms(seconds: float | None) -> int | None:
    """TIMECODE: whole milliseconds rounded half-up, or `None` with no usable duration."""
    if seconds is None:
        return None
    try:
        value = float(seconds)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value) or value <= 0:
        return None
    exact = Decimal(repr(value)) * 1000
    return int(exact.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def video_probe(resolved: Path, info: MediaInfo) -> VideoProbe:
    """PROBE_MAP: the `VideoProbe` for a resolved local video and its `MediaInfo`."""
    ms = duration_ms(info.duration)
    return VideoProbe(
        path=str(resolved),
        duration_ms=ms,
        timecode=None if ms is None else format_timecode(ms),
        container=info.container,
        video_codec=info.video_codec,
        audio_codec=info.audio_codec,
        width=info.width,
        height=info.height,
        fps=info.fps,
        has_video=info.video_codec is not None,
        has_audio=info.audio_codec is not None,
    )


def parse_time(value: object) -> int:
    """TIME_PARSE: seconds or `HH:MM:SS.mmm` as whole milliseconds.

    Every refusal is the one fixed message, which echoes no input, raised when no exception is
    being handled.
    """
    ms = _time_ms(value)
    if ms is None or ms > TIME_MAX_MS:
        raise ValidationError(TIME_REFUSED)
    return ms


def _time_ms(value: object) -> int | None:
    """TIME_PARSE's grammar: whole milliseconds, or `None` for anything it refuses."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        # Not through math.isfinite: a huge int would overflow converting to float.
        return value * 1000 if value >= 0 else None
    if isinstance(value, float):
        if not math.isfinite(value) or value < 0 or abs(value) > _FLOAT_SECONDS_GUARD:
            return None
        exact = Decimal(repr(value)) * 1000
        return int(exact.quantize(Decimal(1), rounding=ROUND_HALF_UP))
    if not isinstance(value, str) or len(value) > TIME_TEXT_MAX:
        return None
    for pattern in _TIME_PATTERNS:
        found = pattern.fullmatch(value)
        if found is None:
            continue
        *parts, fraction = found.groups()
        seconds = 0
        for part in parts:
            seconds = seconds * 60 + int(part)
        millis = int(fraction.ljust(3, "0")) if fraction else 0
        return seconds * 1000 + millis
    return None


def frame_times(start_ms: int, end_ms: int, count: int) -> list[int]:
    """FRAME_TIMES: the midpoints of `count` equal parts of `[start_ms, end_ms)`.

    Each midpoint is rounded half-up in integers and capped at `end_ms - 1`, then the list is
    de-duplicated and sorted. The caller has made `start_ms` less than `end_ms`.
    """
    span = end_ms - start_ms
    times = {
        min(end_ms - 1, start_ms + ((2 * i + 1) * span + count) // (2 * count))
        for i in range(count)
    }
    return sorted(times)


def frame_name(stem: str, ms: int) -> str:
    """FRAME_NAME: `stem-tHHhMMmSS.mmms`, with the stem made safe as IMPORT_NAME makes it."""
    # Imported here: services.capture imports this module for VideoFrames.
    from avkit_core.services.capture import import_stem

    hours, rest = divmod(ms, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    seconds, millis = divmod(rest, 1000)
    return f"{import_stem(stem)}-t{hours:02d}h{minutes:02d}m{seconds:02d}.{millis:03d}s"


def _half_up(num: int, den: int) -> int:
    """The one integer rounding SHEET_SIZE, SHEET_TIMES and SHEET_LABEL use: half up."""
    return (2 * num + den) // (2 * den)


def sheet_cell_size(
    width: int | None, height: int | None, grid: int, max_edge: int
) -> tuple[int, int]:
    """SHEET_SIZE (MEU-135): one cell's `(width, height)`, integers only.

    The sheet is `grid` cells on each axis, so its long edge is at most `max_edge` and its
    area at most the token budget. A source with no usable size counts as 1920x1080.
    """
    if width is None or height is None or width < 1 or height < 1:
        width, height = SHEET_FALLBACK_SIZE
    tokens = SHEET_TOKENS_STANDARD if max_edge <= SHEET_TOKENS_STANDARD else SHEET_TOKENS_HIGH
    budget = tokens * PIXELS_PER_TOKEN
    long_src, short_src = max(width, height), min(width, height)
    long = max(1, max_edge // grid)
    short = max(1, _half_up(long * short_src, long_src))
    while grid * grid * long * short > budget and long > 1:
        long -= 1
        short = max(1, _half_up(long * short_src, long_src))
    return (long, short) if width >= height else (short, long)


def sheet_spacing_ms(start_ms: int, end_ms: int, grid: int) -> int:
    """SHEET_TIMES (MEU-135): the span over `grid` squared, rounded half up."""
    return _half_up(end_ms - start_ms, grid * grid)


def sheet_label(cell: int, timecode: str, spacing_ms: int) -> str:
    """SHEET_LABEL (MEU-135): the cell number and its timecode, to the second when the
    cells are 10 s or more apart, else to the millisecond."""
    return f"{cell} {timecode if spacing_ms < 10_000 else timecode[:8]}"


def sheet_label_px(cell_h: int) -> int:
    """SHEET_LABEL (MEU-135): the label's starting size for a cell `cell_h` high."""
    return max(SHEET_LABEL_MIN_PX, _half_up(cell_h * SHEET_LABEL_PERCENT, 100))


def sheet_label_stroke(px: int) -> int:
    """SHEET_LABEL (MEU-135): the label's stroke width for a size of `px`."""
    return max(1, _half_up(px, 10))


def _whole_seconds(ms: int) -> str:
    hours, rest = divmod(ms // 1000, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours:02d}h{minutes:02d}m{seconds:02d}s"


def sheet_name(stem: str, start_ms: int, end_ms: int) -> str:
    """SHEET_NAME (MEU-135): `stem-sheet-HHhMMmSSs-HHhMMmSSs`, whole seconds floored, with the
    stem made safe as IMPORT_NAME makes it."""
    # Imported here: services.capture imports this module for VideoSheet.
    from avkit_core.services.capture import import_stem

    return f"{import_stem(stem)}-sheet-{_whole_seconds(start_ms)}-{_whole_seconds(end_ms)}"
