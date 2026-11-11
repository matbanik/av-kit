"""MEU-133 local video input and timecodes (Session 62): VIDEO_INPUT and TIMECODE.

Imports of the new module stay inside the tests, so a missing name fails one test, never the
collection. Every refusal names no part of its input, and its error has no cause or context.
"""

from __future__ import annotations

import math
import os
import traceback
from pathlib import Path

import pytest

from avkit_core.domain.errors import ValidationError

LOCAL = "path must be a local absolute file path"
NOT_FOUND = "video file not found"
MARKER = "s62VIDEOMARKER"


def _refusal(text: str) -> ValidationError:
    from avkit_core.services.video_input import require_local_video

    with pytest.raises(ValidationError) as caught:
        require_local_video(text)
    return caught.value


def _assert_clean(error: ValidationError, message: str) -> None:
    assert str(error) == message
    assert error.__cause__ is None
    assert error.__context__ is None
    printed = "".join(traceback.format_exception(error))
    assert MARKER.casefold() not in printed.casefold()


def test_ac_133_1_an_absolute_drive_path_is_resolved(tmp_path: Path) -> None:
    from avkit_core.services.video_input import require_local_video

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video")
    (tmp_path / "sub").mkdir()
    indirect = str(tmp_path / "sub" / ".." / "clip.mp4")
    resolved = require_local_video(indirect)
    assert resolved == clip.resolve()
    assert resolved.is_absolute()
    assert ".." not in resolved.parts
    assert clip.read_bytes() == b"video"


def test_ac_133_1_a_unc_shaped_path_is_accepted(tmp_path: Path) -> None:
    from avkit_core.services.video_input import require_local_video

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video")
    (tmp_path / "sub").mkdir()
    unc = "\\\\?\\" + str(tmp_path / "sub" / ".." / "clip.mp4")
    resolved = require_local_video(unc)
    assert resolved == Path(unc).resolve()
    assert ".." not in resolved.parts
    assert resolved.is_file()


@pytest.mark.parametrize(
    "text",
    [
        "",
        "C:/" + MARKER + "a" * (4097 - 3 - len(MARKER)),
        f"relative/{MARKER}.mp4",
        f"http://x/{MARKER}.mp4",
        f"file:///C:/{MARKER}.mp4",
        f"ftp:{MARKER}",
        f"C:/{MARKER}\ud800.mp4",
        f"C:/{MARKER}\x07.mp4",
        f"C:/{MARKER}\x00.mp4",
        f"C:/{MARKER}\x1f.mp4",
        f"C:/{MARKER}\x7f.mp4",
    ],
    ids=[
        "empty",
        "4097",
        "relative",
        "http",
        "file",
        "ftp",
        "lone-surrogate",
        "bell",
        "nul",
        "unit-separator",
        "delete",
    ],
)
def test_ac_133_1_a_non_local_path_is_refused(text: str) -> None:
    if text.startswith("C:/" + MARKER + "a"):
        assert len(text) == 4097
    _assert_clean(_refusal(text), LOCAL)


def test_ac_133_1_4096_characters_is_not_refused_as_too_long(tmp_path: Path) -> None:
    text = "C:/" + MARKER + "a" * (4096 - 3 - len(MARKER))
    assert len(text) == 4096
    _assert_clean(_refusal(text), NOT_FOUND)


def test_ac_133_1_a_missing_file_is_not_found(tmp_path: Path) -> None:
    folder = tmp_path / f"folder-{MARKER}"
    folder.mkdir()
    _assert_clean(_refusal(str(folder / f"missing-{MARKER}.mp4")), NOT_FOUND)


def test_ac_133_1_a_directory_is_not_found(tmp_path: Path) -> None:
    folder = tmp_path / f"folder-{MARKER}"
    folder.mkdir()
    _assert_clean(_refusal(str(folder)), NOT_FOUND)


def test_ac_133_1_a_self_loop_symlink_is_not_found(tmp_path: Path) -> None:
    link = tmp_path / f"loop-{MARKER}.mp4"
    try:
        os.symlink(link, link)
    except OSError:
        pytest.skip("os.symlink is refused here; the patched resolve cases cover the loop")
    _assert_clean(_refusal(str(link)), NOT_FOUND)


@pytest.mark.parametrize(
    "error",
    [
        RuntimeError(f"Symlink loop from {MARKER}"),
        OSError(f"[WinError 1920] {MARKER}"),
        ValueError(f"bad {MARKER}"),
        UnicodeEncodeError("utf-8", MARKER, 0, 1, "surrogates not allowed"),
    ],
    ids=["runtime", "os", "value", "unicode"],
)
def test_ac_133_1_a_failing_resolve_is_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    clip = tmp_path / f"clip-{MARKER}.mp4"
    clip.write_bytes(b"video")
    original = Path.resolve

    def _resolve(self: Path, strict: bool = False) -> Path:
        if MARKER in str(self):
            raise error
        return original(self, strict=strict)

    monkeypatch.setattr(Path, "resolve", _resolve)
    refused = _refusal(str(clip))
    monkeypatch.undo()
    _assert_clean(refused, NOT_FOUND)


def test_ac_133_1_the_video_is_never_opened(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.video_input import require_local_video

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video")
    before = clip.stat().st_mtime_ns
    opened: list[str] = []
    original = Path.open

    def _open(self: Path, *args: object, **kwargs: object) -> object:
        opened.append(str(self))
        return original(self, *args, **kwargs)  # type: ignore[arg-type]

    (tmp_path / "sub").mkdir()
    monkeypatch.setattr(Path, "open", _open)
    resolved = require_local_video(str(tmp_path / "sub" / ".." / "clip.mp4"))
    monkeypatch.undo()
    assert opened == []
    assert resolved == clip.resolve()
    assert ".." not in resolved.parts
    assert clip.stat().st_mtime_ns == before


@pytest.mark.parametrize(
    "ms,expected",
    [
        (0, "00:00:00.000"),
        (999, "00:00:00.999"),
        (1000, "00:00:01.000"),
        (3_599_999, "00:59:59.999"),
        (359_999_999, "99:59:59.999"),
    ],
)
def test_ac_133_2_format_timecode(ms: int, expected: str) -> None:
    from avkit_core.services.video_input import format_timecode

    assert format_timecode(ms) == expected


@pytest.mark.parametrize(
    "seconds,expected",
    [
        (3.0, 3000),
        (7200.021, 7200021),
        (3.0005, 3001),
        (3.0004, 3000),
        (0.0005, 1),
        (None, None),
        (math.nan, None),
        (math.inf, None),
        (-math.inf, None),
        (0, None),
        (0.0, None),
        (-1, None),
    ],
    ids=[
        "3.0",
        "7200.021",
        "exact-half-up",
        "below-half",
        "smallest-half",
        "none",
        "nan",
        "inf",
        "minus-inf",
        "zero",
        "zero-float",
        "minus-one",
    ],
)
def test_ac_133_2_duration_ms(seconds: float | None, expected: int | None) -> None:
    from avkit_core.services.video_input import duration_ms

    assert duration_ms(seconds) == expected


# ---------------------------------------------------------------- MEU-134 (Session 62)

TIME_REFUSED = "a time must be seconds or HH:MM:SS.mmm"
PROBE2_TIMES = [
    180001,
    540002,
    900003,
    1260004,
    1620005,
    1980006,
    2340007,
    2700008,
    3060009,
    3420010,
    3780011,
    4140012,
    4500013,
    4860014,
    5220015,
    5580016,
    5940017,
    6300018,
    6660019,
    7020020,
]


@pytest.mark.parametrize(
    "value,expected",
    [
        (1, 1000),
        (1.5, 1500),
        ("75", 75_000),
        ("1:15", 75_000),
        ("01:02:03.5", 3_723_500),
        (0.0005, 1),
        (1.0005, 1001),
        ("99:59:59.999", 359_999_999),
        ("2.25", 2250),
        ("0:00:01.001", 1001),
    ],
    ids=["1", "1.5", "75", "1:15", "01:02:03.5", "exact-half", "1.0005", "max", "2.25", "hms"],
)
def test_ac_134_2_parse_time(value: object, expected: int) -> None:
    from avkit_core.services.video_input import parse_time

    assert parse_time(value) == expected


@pytest.mark.parametrize("value", [0, 0.0, "0", 0.0004], ids=["0", "0.0", "zero-text", "below"])
def test_ac_134_2_parse_time_zero(value: object) -> None:
    from avkit_core.services.video_input import parse_time

    assert parse_time(value) == 0


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        -1,
        -0.5,
        math.nan,
        math.inf,
        "1:60",
        "1:2",
        "1:00:60",
        "a",
        "",
        "١",
        "\ud800",
        "\x00",
        "1\x07",
        "0" * 33,
        "100:00:00",
        360_000,
        "0.0005",
        " 1",
        "1.",
        None,
        [1],
    ],
    ids=[
        "true",
        "false",
        "minus-one",
        "minus-half",
        "nan",
        "inf",
        "1:60",
        "1:2",
        "1:00:60",
        "letter",
        "empty",
        "arabic-digit",
        "lone-surrogate",
        "nul",
        "bell",
        "33-chars",
        "100h",
        "360000s",
        "four-digits",
        "space",
        "trailing-dot",
        "none",
        "list",
    ],
)
def test_ac_134_2_parse_time_refused(value: object) -> None:
    from avkit_core.services.video_input import parse_time

    with pytest.raises(ValidationError) as caught:
        parse_time(value)
    assert str(caught.value) == TIME_REFUSED
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


@pytest.mark.parametrize(
    "value", [1e25, 1e100, 1e308, -1e25], ids=["1e25", "1e100", "1e308", "minus-1e25"]
)
def test_ac_134_2_huge_finite_times_get_the_fixed_refusal(value: float) -> None:
    # D-592 (execution review round 1, F1): a finite float far past the cap is refused with the
    # fixed message, not by decimal.InvalidOperation from the half-up quantize. Any exception is
    # caught so that the wrong one fails by assertion (red-check, as D-589).
    from avkit_core.services.video_input import parse_time

    with pytest.raises(Exception) as caught:
        parse_time(value)
    assert type(caught.value) is ValidationError
    assert str(caught.value) == TIME_REFUSED
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


def test_ac_134_2_32_characters_is_not_refused_as_too_long() -> None:
    from avkit_core.services.video_input import parse_time

    text = "0" * 31 + "7"
    assert len(text) == 32
    assert parse_time(text) == 7000


@pytest.mark.parametrize(
    "start,end,count,expected",
    [
        (0, 3000, 3, [500, 1500, 2500]),
        (0, 7_200_021, 20, PROBE2_TIMES),
        (0, 3, 5, [0, 1, 2]),
        (0, 1, 2, [0]),
        (2999, 3000, 2, [2999]),
        (0, 3000, 1, [1500]),
    ],
    ids=["three", "probe2", "capped", "half-up", "last-ms", "one"],
)
def test_ac_134_3_frame_times(start: int, end: int, count: int, expected: list[int]) -> None:
    from avkit_core.services.video_input import frame_times

    assert frame_times(start, end, count) == expected


def test_ac_134_3_frame_times_stay_inside_the_span() -> None:
    from avkit_core.services.video_input import frame_times

    outside: list[tuple[int, int, int, list[int]]] = []
    for first in (0, 1000):
        for span in range(1, 41):
            for count in range(1, 21):
                times = frame_times(first, first + span, count)
                inside = bool(times) and all(first <= t < first + span for t in times)
                ordered = times == sorted(set(times))
                if not inside or not ordered or len(times) > count:
                    outside.append((first, span, count, times))
    assert outside == []


@pytest.mark.parametrize(
    "stem,ms,expected",
    [
        ("standup", 725_500, "standup-t00h12m05.500s"),
        ("clip", 0, "clip-t00h00m00.000s"),
        ("clip", 359_999_999, "clip-t99h59m59.999s"),
        ("clip", 1000, "clip-t00h00m01.000s"),
        ("Łodz", 1, "Łodz-t00h00m00.001s"),
        ("CON", 0, "import_CON-t00h00m00.000s"),
        ("..", 0, "import-t00h00m00.000s"),
        ("", 0, "import-t00h00m00.000s"),
        ("a\x07b", 0, "a_b-t00h00m00.000s"),
        ("a\ud800b", 0, "a_b-t00h00m00.000s"),
    ],
    ids=[
        "standup",
        "zero",
        "max",
        "one-second",
        "polish",
        "reserved",
        "dots",
        "empty",
        "bell",
        "lone-surrogate",
    ],
)
def test_ac_134_4_frame_name(stem: str, ms: int, expected: str) -> None:
    from avkit_core.services.video_input import frame_name

    assert frame_name(stem, ms) == expected


# AC-135.2 to AC-135.5 (Session 63, MEU-135): SHEET_SIZE, SHEET_TIMES, SHEET_LABEL, SHEET_NAME.

#: (source size, max_edge) -> the cell for grids 2, 3, 4 and 5, from the planning probe
#: (C:/Temp/av-kit/s63-size-probe-receipt.txt). 9:16 is 16:9 transposed.
SHEET_CELLS: dict[tuple[tuple[int, int], int], list[tuple[int, int]]] = {
    ((1920, 1080), 1568): [(722, 406), (482, 271), (361, 203), (288, 162)],
    ((1920, 1080), 2576): [(1263, 710), (841, 473), (631, 355), (505, 284)],
    ((1920, 1080), 64): [(32, 18), (21, 12), (16, 9), (12, 7)],
    ((1440, 1080), 1568): [(625, 469), (417, 313), (312, 234), (250, 188)],
    ((1440, 1080), 2576): [(1093, 820), (728, 546), (546, 410), (437, 328)],
    ((1440, 1080), 64): [(32, 24), (21, 16), (16, 12), (12, 9)],
}
SHEET_SHAPES = {
    "16:9": (3840, 2160),
    "4:3": (1440, 1080),
    "9:16": (1080, 1920),
    "1:1": (1000, 1000),
    "odd": (1919, 1079),
    "21:9": (2560, 1080),
    "tall_extreme": (16, 4000),
    "wide_extreme": (4000, 2),
}
SHEET_EDGES = [64, 65, 99, 100, 199, 200, 313, 777, 1000, 1567, 1568, 1569, 2000, 2575, 2576]


def _half_up(num: int, den: int) -> int:
    return (2 * num + den) // (2 * den)


def _expected_cells() -> list[tuple[int, int, int, int, tuple[int, int]]]:
    rows = []
    for ((width, height), edge), cells in SHEET_CELLS.items():
        for grid, cell in zip(range(2, 6), cells, strict=True):
            rows.append((width, height, grid, edge, cell))
            if (width, height) == (1920, 1080):
                rows.append((height, width, grid, edge, (cell[1], cell[0])))
    return rows


@pytest.mark.parametrize(
    "width,height,grid,max_edge,cell",
    _expected_cells(),
    ids=[f"{w}x{h}-g{g}-e{e}" for w, h, g, e, _ in _expected_cells()],
)
def test_ac_135_2_sheet_cell_size_matches_the_probe(
    width: int, height: int, grid: int, max_edge: int, cell: tuple[int, int]
) -> None:
    from avkit_core.services.video_input import sheet_cell_size

    assert sheet_cell_size(width, height, grid, max_edge) == cell


def test_ac_135_2_every_shape_is_bounded_and_maximal() -> None:
    from avkit_core.services.video_input import sheet_cell_size

    broken: list[tuple[str, int, int, tuple[int, int], str]] = []
    for shape, (width, height) in SHEET_SHAPES.items():
        long_src, short_src = max(width, height), min(width, height)
        for grid in range(2, 6):
            for edge in SHEET_EDGES:
                cell = sheet_cell_size(width, height, grid, edge)
                tokens = 1568 if edge <= 1568 else 4784
                budget = tokens * 750
                cell_w, cell_h = cell
                if (cell_w >= cell_h) != (width >= height) and cell_w != cell_h:
                    broken.append((shape, grid, edge, cell, "orientation"))
                if max(cell_w, cell_h) * grid > edge:
                    broken.append((shape, grid, edge, cell, "long edge"))
                if grid * grid * cell_w * cell_h > budget:
                    broken.append((shape, grid, edge, cell, "budget"))
                if min(cell_w, cell_h) < 1:
                    broken.append((shape, grid, edge, cell, "empty cell"))
                bigger = max(cell_w, cell_h) + 1
                bigger_short = max(1, _half_up(bigger * short_src, long_src))
                fits = bigger * grid <= edge and grid * grid * bigger * bigger_short <= budget
                if fits:
                    broken.append((shape, grid, edge, cell, "not maximal"))
    assert broken == []


def test_ac_135_2_the_token_tier_changes_above_1568() -> None:
    from avkit_core.services.video_input import (
        PIXELS_PER_TOKEN,
        SHEET_TOKENS_HIGH,
        SHEET_TOKENS_STANDARD,
        sheet_cell_size,
    )

    assert (SHEET_TOKENS_STANDARD, SHEET_TOKENS_HIGH, PIXELS_PER_TOKEN) == (1568, 4784, 750)
    # 1568 keeps the 1568-token budget; 1569 gets the 4,784-token one, so the cell is
    # bounded by the edge alone (784 = 1569 // 2).
    assert sheet_cell_size(1920, 1080, 2, 1568) == (722, 406)
    assert sheet_cell_size(1920, 1080, 2, 1569) == (784, 441)
    assert 4 * 784 * 441 > 1568 * 750


@pytest.mark.parametrize(
    "width,height",
    [(None, None), (None, 1080), (1920, None), (0, 0), (0, 1080), (1920, 0), (-5, 720)],
    ids=["none", "no-width", "no-height", "zero", "zero-width", "zero-height", "negative"],
)
def test_ac_135_2_missing_sizes_use_16_9(width: int | None, height: int | None) -> None:
    from avkit_core.services.video_input import SHEET_FALLBACK_SIZE, sheet_cell_size

    assert SHEET_FALLBACK_SIZE == (1920, 1080)
    assert sheet_cell_size(width, height, 3, 1568) == (482, 271)
    assert sheet_cell_size(width, height, 5, 64) == (12, 7)


@pytest.mark.parametrize(
    "span,grid,expected",
    [(14, 2, 4), (13, 2, 3), (2, 2, 1), (1, 2, 0), (3_000, 3, 333), (3_004, 3, 334)],
    ids=["14-up", "13-down", "2-up", "1-down", "3000", "3004"],
)
def test_ac_135_3_spacing_rounds_half_up(span: int, grid: int, expected: int) -> None:
    from avkit_core.services.video_input import sheet_spacing_ms

    assert sheet_spacing_ms(0, span, grid) == expected
    assert sheet_spacing_ms(1000, 1000 + span, grid) == expected


def test_ac_135_3_every_short_span_for_every_grid() -> None:
    from avkit_core.services.video_input import frame_times, sheet_spacing_ms

    wrong: list[tuple[int, int, int, list[int], int]] = []
    for grid in range(2, 6):
        cells = grid * grid
        for first in (0, 1000):
            for span in range(1, 61):
                end = first + span
                times = frame_times(first, end, cells)
                spacing = sheet_spacing_ms(first, end, grid)
                ok = bool(times) and all(first <= t < end for t in times)
                ok = ok and times == sorted(set(times))
                ok = ok and len(times) <= min(cells, span)
                if span > cells:
                    ok = ok and len(times) == cells
                if span == cells:
                    ok = ok and len(times) == cells - 1
                ok = ok and spacing == _half_up(span, cells)
                if not ok:
                    wrong.append((grid, first, span, times, spacing))
    assert wrong == []


@pytest.mark.parametrize(
    "cell,timecode,spacing,expected",
    [
        (3, "00:00:09.999", 9_999, "3 00:00:09.999"),
        (3, "00:00:09.999", 10_000, "3 00:00:09"),
        (25, "01:56:24.375", 290_000, "25 01:56:24"),
        (1, "00:00:00.375", 750, "1 00:00:00.375"),
        (9, "99:59:59.999", 0, "9 99:59:59.999"),
    ],
    ids=["9999", "10000", "hour", "short", "zero-spacing"],
)
def test_ac_135_4_sheet_label(cell: int, timecode: str, spacing: int, expected: str) -> None:
    from avkit_core.services.video_input import sheet_label

    label = sheet_label(cell, timecode, spacing)
    assert label == expected
    number, _, time_text = label.partition(" ")
    assert number == str(cell)
    assert timecode.startswith(time_text)
    assert time_text in (timecode, timecode[:8])


@pytest.mark.parametrize(
    "cell_h,px",
    [(25, 8), (75, 11), (74, 10), (57, 8), (58, 8), (61, 9), (271, 38), (469, 66), (7, 8)],
    ids=["25", "75-half-up", "74", "57", "58", "61", "271", "469", "7"],
)
def test_ac_135_4_sheet_label_px(cell_h: int, px: int) -> None:
    from avkit_core.services.video_input import (
        SHEET_LABEL_MIN_PX,
        SHEET_LABEL_PERCENT,
        sheet_label_px,
    )

    assert (SHEET_LABEL_PERCENT, SHEET_LABEL_MIN_PX) == (14, 8)
    assert sheet_label_px(cell_h) == px


@pytest.mark.parametrize(
    "px,stroke",
    [(8, 1), (15, 2), (14, 1), (25, 3), (24, 2), (38, 4), (1, 1)],
    ids=["8", "15-half-up", "14", "25-half-up", "24", "38", "1"],
)
def test_ac_135_4_sheet_label_stroke(px: int, stroke: int) -> None:
    from avkit_core.services.video_input import sheet_label_stroke

    assert sheet_label_stroke(px) == stroke


@pytest.mark.parametrize(
    "stem,start,end,expected",
    [
        ("standup", 0, 7_200_021, "standup-sheet-00h00m00s-02h00m00s"),
        ("clip", 0, 59_999, "clip-sheet-00h00m00s-00h00m59s"),
        ("clip", 1_000, 359_999_999, "clip-sheet-00h00m01s-99h59m59s"),
        ("clip", 0, 3_000, "clip-sheet-00h00m00s-00h00m03s"),
        ("Łodz", 0, 3_000, "Łodz-sheet-00h00m00s-00h00m03s"),
        ("CON", 0, 3_000, "import_CON-sheet-00h00m00s-00h00m03s"),
        ("..", 0, 3_000, "import-sheet-00h00m00s-00h00m03s"),
    ],
    ids=["standup", "floored", "max", "clip", "polish", "reserved", "dots"],
)
def test_ac_135_5_sheet_name(stem: str, start: int, end: int, expected: str) -> None:
    from avkit_core.services.video_input import sheet_name

    assert sheet_name(stem, start, end) == expected


@pytest.mark.parametrize(
    "stem",
    ["a\ud800b", "a\x07b", "", "\x07", "\ud800"],
    ids=["surrogate", "bell", "empty", "only-bell", "only-surrogate"],
)
def test_ac_135_5_unsafe_stems_give_a_safe_name(stem: str) -> None:
    from avkit_core.services.video_input import sheet_name

    name = sheet_name(stem, 0, 3_000)
    assert name.endswith("-sheet-00h00m00s-00h00m03s")
    safe_stem = name.removesuffix("-sheet-00h00m00s-00h00m03s")
    assert safe_stem != ""
    assert [ch for ch in name if 0xD800 <= ord(ch) <= 0xDFFF] == []
    assert [ch for ch in name if ord(ch) < 0x20 or ord(ch) == 0x7F] == []
    name.encode("utf-8")
