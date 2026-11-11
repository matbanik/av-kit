"""MEU-135 SHEET_TILE and SHEET_LABEL with the real CaptureAdapter (Session 63): AC-135.6, .7.

The cells are small PNGs made here with Pillow, so every pixel the sheet should hold is known.
No file is written: `CaptureAdapter.sheet` takes bytes and returns bytes.
"""

from __future__ import annotations

import inspect
import io
from typing import Any

import pytest
from PIL import Image, ImageColor, ImageDraw

from avkit_core.services.video_input import sheet_label, sheet_label_px, sheet_label_stroke
from avkit_infra.capture.adapter import CaptureAdapter

PNG_SIGNATURE = bytes.fromhex("89504e470d0a1a0a")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 20)
GREEN = (20, 200, 20)
BLUE = (20, 20, 220)
YELLOW = (230, 220, 10)
#: A channel within this of 0 or 255 counts as near black or near white (AC-135.7).
NEAR = 32
#: The share of a label box that must be near white and near black (AC-135.7).
CONTRAST_SHARE = 0.02


def _adapter() -> CaptureAdapter:
    return CaptureAdapter(mss_factory=lambda: None, platform="linux")


def _png(colour: tuple[int, int, int], size: tuple[int, int] = (40, 30)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, colour).save(buffer, format="PNG")
    return buffer.getvalue()


def _halves(
    left: tuple[int, int, int], right: tuple[int, int, int], size: tuple[int, int]
) -> bytes:
    image = Image.new("RGB", size, left)
    image.paste(right, (size[0] // 2, 0, size[0], size[1]))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _sheet(
    cells: list[bytes],
    *,
    grid: int = 2,
    cell_size: tuple[int, int] = (40, 30),
    labels: list[str] | None = None,
) -> bytes:
    return _adapter().sheet(
        cells,
        grid=grid,
        cell_size=cell_size,
        labels=labels if labels is not None else [""] * len(cells),
    )


def _open(data: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(data))
    image.load()
    return image


def _cell_box(index: int, grid: int, cell_size: tuple[int, int]) -> tuple[int, int, int, int]:
    width, height = cell_size
    x0, y0 = (index % grid) * width, (index // grid) * height
    return (x0, y0, x0 + width, y0 + height)


def label_box(index: int, grid: int, cell_size: tuple[int, int]) -> tuple[int, int, int, int]:
    """The top band of a cell where SHEET_LABEL draws: two pads and two label heights."""
    x0, y0, x1, _ = _cell_box(index, grid, cell_size)
    px = sheet_label_px(cell_size[1])
    pad = max(1, px // 4)
    return (x0, y0, x1, y0 + min(cell_size[1], 2 * pad + 2 * px))


def near_shares(image: Image.Image, box: tuple[int, int, int, int]) -> tuple[float, float]:
    """(near white, near black) shares of the pixels in `box`."""
    pixels = list(image.convert("RGB").crop(box).getdata())
    white = sum(1 for p in pixels if min(p) >= 255 - NEAR)
    black = sum(1 for p in pixels if max(p) <= NEAR)
    return white / len(pixels), black / len(pixels)


def _rgb(value: object) -> tuple[int, ...]:
    if isinstance(value, str):
        return tuple(ImageColor.getrgb(value)[:3])
    if isinstance(value, tuple):
        return tuple(value[:3])
    raise AssertionError(f"not a colour: {value!r}")


# AC-135.6 SHEET_TILE --------------------------------------------------------------------------


def test_ac_135_6_cells_land_in_grid_order() -> None:
    data = _sheet([_png(RED), _png(GREEN), _png(BLUE), _png(YELLOW)], labels=["1", "2", "3", "4"])
    assert data.startswith(PNG_SIGNATURE)
    image = _open(data)
    assert image.size == (80, 60)
    assert image.mode == "RGB"
    # Sampled at each cell's lower right, away from the label at its top left.
    corners = ((0, 0), (40, 0), (0, 30), (40, 30))
    samples = [image.getpixel((x0 + 34, y0 + 24)) for x0, y0 in corners]
    assert samples == [RED, GREEN, BLUE, YELLOW]


def test_ac_135_6_a_narrow_cell_is_centred_on_black() -> None:
    data = _sheet([_png(RED, (20, 30))], grid=2)
    assert data.startswith(PNG_SIGNATURE)
    image = _open(data)
    row = [image.getpixel((x, 20)) for x in (0, 9, 10, 29, 30, 39)]
    assert row == [BLACK, BLACK, RED, RED, BLACK, BLACK]
    assert image.crop((0, 0, 10, 30)).getextrema() == ((0, 0), (0, 0), (0, 0))
    assert image.crop((30, 0, 40, 30)).getextrema() == ((0, 0), (0, 0), (0, 0))


def test_ac_135_6_a_large_cell_is_shrunk_and_a_small_one_never_enlarged() -> None:
    data = _sheet([_halves(RED, BLUE, (80, 60)), _png(GREEN, (10, 6))], grid=2)
    assert data.startswith(PNG_SIGNATURE)
    image = _open(data)
    left = image.getpixel((5, 20))
    right = image.getpixel((35, 20))
    assert max(abs(a - b) for a, b in zip(left, RED, strict=True)) <= 2
    assert max(abs(a - b) for a, b in zip(right, BLUE, strict=True)) <= 2
    # A 10x6 cell stays 10x6, centred in its 40x30 box at (40 + 15, 12).
    small = image.crop((40, 0, 80, 30))
    assert small.crop((15, 12, 25, 18)).getextrema() == ((20, 20), (200, 200), (20, 20))
    assert small.getpixel((14, 15)) == BLACK
    assert small.getpixel((25, 15)) == BLACK
    assert small.getpixel((20, 11)) == BLACK
    assert small.getpixel((20, 18)) == BLACK


def test_ac_135_6_cells_past_the_last_stay_black() -> None:
    data = _sheet([_png(RED), _png(GREEN), _png(BLUE)], labels=["1", "2", "3"])
    assert data.startswith(PNG_SIGNATURE)
    image = _open(data)
    assert image.size == (80, 60)
    assert image.crop((40, 30, 80, 60)).getextrema() == ((0, 0), (0, 0), (0, 0))


def test_ac_135_6_a_long_label_stays_in_its_cell() -> None:
    cells = [_png(RED), _png(GREEN), _png(BLUE), _png(YELLOW)]
    long_label = "1 " + "W" * 200
    plain = _sheet(cells, labels=["", "", "", ""])
    labelled = _sheet(cells, labels=[long_label, "", "", ""])
    assert plain.startswith(PNG_SIGNATURE)
    assert labelled.startswith(PNG_SIGNATURE)
    before, after = _open(plain), _open(labelled)
    assert (
        before.crop(_cell_box(0, 2, (40, 30))).tobytes()
        != after.crop(_cell_box(0, 2, (40, 30))).tobytes()
    )
    for index in (1, 2, 3):
        box = _cell_box(index, 2, (40, 30))
        assert before.crop(box).tobytes() == after.crop(box).tobytes(), index


def test_ac_135_6_the_png_has_no_metadata() -> None:
    data = _sheet([_png(RED), _png(GREEN), _png(BLUE), _png(YELLOW)], labels=["1", "2", "3", "4"])
    assert data.startswith(PNG_SIGNATURE)
    image = _open(data)
    assert image.format == "PNG"
    assert image.size == (80, 60)
    assert "exif" not in image.info
    assert "icc_profile" not in image.info
    assert getattr(image, "text", {}) == {}
    assert b"tEXt" not in data
    assert b"iTXt" not in data
    assert b"zTXt" not in data
    assert b"eXIf" not in data


def test_ac_135_6_an_undecodable_cell_raises() -> None:
    with pytest.raises((OSError, ValueError)):
        _sheet([_png(RED), b"not an image at all"], labels=["1", "2"])


@pytest.mark.parametrize(
    "cells,labels",
    [
        ([_png(RED), _png(GREEN)], ["1"]),
        ([_png(RED)], ["1", "2"]),
        ([_png(RED)] * 5, ["1", "2", "3", "4", "5"]),
    ],
    ids=["fewer-labels", "more-labels", "more-cells-than-the-grid"],
)
def test_ac_135_6_mismatched_lengths_raise(cells: list[bytes], labels: list[str]) -> None:
    with pytest.raises(ValueError):
        _sheet(cells, labels=labels)


# AC-135.7 label contrast ----------------------------------------------------------------------

CONTRAST_CELL = (482, 271)
CONTRAST_TIMES = [375, 1125, 1875, 2625]


def _contrast_labels() -> list[str]:
    from avkit_core.services.video_input import format_timecode

    return [sheet_label(n, format_timecode(ms), 750) for n, ms in enumerate(CONTRAST_TIMES, 1)]


@pytest.mark.parametrize(
    "colour,contrast", [(WHITE, "black"), (BLACK, "white")], ids=["white-cells", "black-cells"]
)
def test_ac_135_7_labels_contrast_on_white_and_black(
    colour: tuple[int, int, int], contrast: str
) -> None:
    cells = [_png(colour, CONTRAST_CELL)] * 4
    labelled = _sheet(cells, cell_size=CONTRAST_CELL, labels=_contrast_labels())
    plain = _sheet(cells, cell_size=CONTRAST_CELL, labels=[""] * 4)
    assert labelled.startswith(PNG_SIGNATURE)
    assert plain.startswith(PNG_SIGNATURE)
    image, control = _open(labelled), _open(plain)
    assert image.size == (964, 542)
    for index in range(4):
        box = label_box(index, 2, CONTRAST_CELL)
        white, black = near_shares(image, box)
        assert (index, white >= CONTRAST_SHARE, black >= CONTRAST_SHARE) == (index, True, True)
        control_white, control_black = near_shares(control, box)
        # The control: with no label, the box holds none of the contrasting colour.
        contrasting = control_black if contrast == "black" else control_white
        assert (index, contrasting) == (index, 0.0)


def test_ac_135_7_labels_drawn_are_the_labels_passed(monkeypatch: pytest.MonkeyPatch) -> None:
    original = ImageDraw.ImageDraw.text
    signature = inspect.signature(original)
    calls: list[dict[str, Any]] = []

    def recording(self: ImageDraw.ImageDraw, *args: Any, **kwargs: Any) -> Any:
        bound = signature.bind(self, *args, **kwargs)
        bound.apply_defaults()
        calls.append(dict(bound.arguments))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ImageDraw.ImageDraw, "text", recording)
    labels = _contrast_labels()
    data = _sheet([_png(WHITE, CONTRAST_CELL)] * 4, cell_size=CONTRAST_CELL, labels=labels)
    assert data.startswith(PNG_SIGNATURE)
    assert [call["text"] for call in calls] == labels
    for call in calls:
        assert _rgb(call["fill"]) == WHITE
        assert _rgb(call["stroke_fill"]) == BLACK
        assert call["stroke_width"] >= 1
        size = getattr(call["font"], "size", None)
        if size is not None:
            assert size <= sheet_label_px(CONTRAST_CELL[1])
            assert call["stroke_width"] == sheet_label_stroke(int(size))
