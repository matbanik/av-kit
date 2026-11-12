"""MEU-136 `CaptureAdapter.export` (Session 64): EXPORT_ENCODE. AC-136.4 to AC-136.7.

Every source is built with Pillow (or as hand-written PNG bytes) under `tmp_path`; nothing is
read from the network. The adapter's export is called through `_export`, which hands any
exception back as a value, so a Red fails by an assertion on what came back.
"""

from __future__ import annotations

import random
import struct
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
from PIL import Image, ImageCms, PngImagePlugin

from avkit_core.domain.capture import ImageProbe
from avkit_core.domain.errors import ConflictError, InboxPathError
from avkit_infra.capture import adapter as adapter_mod
from avkit_infra.capture.adapter import CaptureAdapter

FORMATS = ("png", "jpeg", "webp")
PIL_FORMAT = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}
SUFFIX = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}
NOT_OPENED = "the image could not be opened"
CHANGED = "the image file changed since the captures were listed; list them again and retry"
NOT_SAVED = "the export could not be saved"
SIZE = (64, 48)
SHRUNK = (32, 24)
#: The depth map's modes (D-619), as EXPORT_ENCODE names them.
DEPTH_MODES = ("I;16", "I;16L", "I;16B", "I;16N", "I")
#: The 256x64 depth source: four 64-px blocks, their centres, and those centres at max_edge 128.
DEPTH_BLOCKS = (0, 257, 32768, 65535)
DEPTH_CENTRES = ((32, 32), (96, 32), (160, 32), (224, 32))
DEPTH_CENTRES_128 = ((16, 16), (48, 16), (80, 16), (112, 16))
#: `v * 255 / 65535` rounded half up for each block value.
DEPTH_L = (0, 1, 128, 255)
KEYED = 2  # the 32768 block carries the transparency key


def _ac(label: str) -> pytest.MarkDecorator:
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _export(
    source: Path,
    out: Path,
    *,
    fmt: str,
    size: tuple[int, int] | None = None,
    source_size: tuple[int, int] | None = None,
    quality: int | None = None,
) -> ImageProbe | Exception:
    """The real adapter's export; an exception comes back as the value."""
    if source_size is None:
        with Image.open(source) as opened:
            source_size = opened.size
    try:
        return CaptureAdapter().export(
            source,
            source_size,
            out,
            fmt=fmt,
            size=source_size if size is None else size,
            quality=quality,
        )
    except Exception as exc:  # noqa: BLE001 - a Red must fail by assertion, not by the raise
        return exc


def _done(result: ImageProbe | Exception) -> ImageProbe:
    assert isinstance(result, ImageProbe), f"export raised {type(result).__name__}: {result}"
    return result


def _raised(result: ImageProbe | Exception) -> tuple[type, str]:
    return (type(result), str(result))


@dataclass
class Out:
    format: str | None
    image: Image.Image
    info: dict[str, Any]
    text: dict[str, str]
    exif: dict[int, Any]

    def rgba(self, xy: tuple[int, int]) -> tuple[int, ...]:
        return tuple(self.image.convert("RGBA").getpixel(xy))  # type: ignore[arg-type]


def _read(path: Path) -> Out:
    assert path.is_file(), f"no output at {path.name}"
    with Image.open(path) as opened:
        opened.load()
        return Out(
            opened.format,
            opened.copy(),
            dict(opened.info),
            dict(getattr(opened, "text", {})),
            dict(opened.getexif()),
        )


def _within(got: int, want: int, tol: int) -> bool:
    return abs(got - want) <= tol


def _distinct(size: tuple[int, int] = SIZE) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size)
    image.putdata(
        [
            ((x * 4) % 256, (y * 5) % 256, ((x + y) * 3) % 256)
            for y in range(height)
            for x in range(width)
        ]
    )
    return image


def _gradient_alpha(size: tuple[int, int] = SIZE) -> Image.Image:
    width, height = size
    alpha = Image.new("L", size)
    alpha.putdata([(x * 3 + y * 2) % 256 for y in range(height) for x in range(width)])
    return alpha


def _i16(values: list[int], size: tuple[int, int]) -> Image.Image:
    """An `I;16` image from raw little-endian bytes: `paste(32768)` writes 0 on Pillow 13.0.0."""
    return Image.frombytes("I;16", size, b"".join(struct.pack("<H", v) for v in values))


def _depth_source(folder: Path, key: int | None = None) -> Path:
    row = [DEPTH_BLOCKS[x // 64] for x in range(256)]
    image = _i16(row * 64, (256, 64))
    for (x, y), want in zip(DEPTH_CENTRES, DEPTH_BLOCKS, strict=True):
        assert image.getpixel((x, y)) == want, ("built", x, want)
    path = folder / ("depth-keyed.png" if key is not None else "depth.png")
    extra = {} if key is None else {"transparency": key}
    image.save(path, format="PNG", **extra)
    with Image.open(path) as opened:
        opened.load()
        assert opened.mode == "I;16"
        for (x, y), want in zip(DEPTH_CENTRES, DEPTH_BLOCKS, strict=True):
            assert opened.getpixel((x, y)) == want, ("reopened", x, want)
        assert opened.info.get("transparency") == key
    return path


def _mode_source(mode: str, folder: Path) -> Path:
    """A 64x48 source in `mode` for the mode table of AC-136.4."""
    base = _distinct()
    path = folder / f"mode-{mode.replace(';', '')}.png"
    if mode in ("RGBA", "LA"):
        image = base.convert(mode)
        image.putalpha(_gradient_alpha())
        image.save(path, format="PNG")
    elif mode == "P":
        base.quantize(16).save(path, format="PNG", transparency=3)
    elif mode == "I;16":
        width, height = SIZE
        _i16([x * 1000 + y for y in range(height) for x in range(width)], SIZE).save(
            path, format="PNG"
        )
    elif mode == "CMYK":
        from tests.unit.test_capture_adapter import _cmyk_icc, _cmyk_jpeg

        path = folder / "mode-CMYK.jpg"
        _cmyk_jpeg(path, _cmyk_icc())
    else:
        base.convert(mode).save(path, format="PNG")
    with Image.open(path) as opened:
        assert opened.mode == mode, (mode, opened.mode)
    return path


# The output mode each source mode gives, unresized and shrunk (EXPORT_ENCODE steps 3, 4, 6).
MODE_WANT: dict[str, dict[str, str]] = {
    "RGBA": {"png": "RGBA", "jpeg": "RGB", "webp": "RGBA"},
    "LA": {"png": "LA", "jpeg": "RGB", "webp": "RGBA"},
    "L": {"png": "L", "jpeg": "RGB", "webp": "RGB"},
    "P": {"png": "P", "jpeg": "RGB", "webp": "RGBA"},
    "1": {"png": "1", "jpeg": "RGB", "webp": "RGB"},
    "I;16": {"png": "I;16", "jpeg": "RGB", "webp": "RGB"},
    "CMYK": {"png": "RGB", "jpeg": "RGB", "webp": "RGB"},
}
MODE_WANT_SHRUNK_PNG = {
    "RGBA": "RGBA",
    "LA": "LA",
    "L": "L",
    "P": "RGBA",
    "1": "L",
    "I;16": "I;16",
    "CMYK": "RGB",
}


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def _pack(values: list[int], depth: int) -> bytes:
    if depth == 8:
        return bytes(values)
    out, per = bytearray(), 8 // depth
    for i in range(0, len(values), per):
        byte = 0
        for j, value in enumerate(values[i : i + per]):
            byte |= value << (8 - depth * (j + 1))
        out.append(byte)
    return bytes(out)


def _gray_png(depth: int, row: list[int], key: int, height: int = 64) -> bytes:
    """A gray PNG (colour type 0) at `depth` with a tRNS key, written byte by byte."""
    raw = b"".join(b"\x00" + _pack(row, depth) for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", len(row), height, depth, 0, 0, 0, 0))
        + _chunk(b"tRNS", struct.pack(">H", key))
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )


def _rgb16_png(
    row: list[tuple[int, int, int]], key: tuple[int, int, int], height: int = 8
) -> bytes:
    raw = b"".join(
        b"\x00" + b"".join(struct.pack(">HHH", *pixel) for pixel in row) for _ in range(height)
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", len(row), height, 16, 2, 0, 0, 0))
        + _chunk(b"tRNS", struct.pack(">HHH", *key))
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )


# --- AC-136.4: EXPORT_ENCODE ------------------------------------------------------------------


@pytest.mark.parametrize("fmt", FORMATS)
@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_metadata_dropped_icc_kept(ac_id: str, fmt: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.4"
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    exif = Image.Exif()
    exif[0x0112] = 1
    exif[0x010F] = "private maker"
    text = PngImagePlugin.PngInfo()
    text.add_text("Comment", "private comment")
    text.add_itxt("XML:com.adobe.xmp", "<x:xmpmeta>private xmp</x:xmpmeta>")
    source = tmp_path / "source.png"
    _distinct().save(source, format="PNG", icc_profile=icc, exif=exif, pnginfo=text)
    planted = _read(source)
    assert planted.info.get("icc_profile") == icc
    assert "exif" in planted.info
    assert planted.exif.get(0x010F) == "private maker"
    assert planted.text.get("Comment") == "private comment"
    assert "XML:com.adobe.xmp" in planted.text
    out = tmp_path / f"out{SUFFIX[fmt]}"
    probe = _done(_export(source, out, fmt=fmt))
    assert (probe.width, probe.height) == SIZE
    assert probe.file_size == out.stat().st_size
    got = _read(out)
    assert got.format == PIL_FORMAT[fmt]
    assert got.image.size == SIZE
    assert got.info.get("icc_profile") == icc
    assert "exif" not in got.info
    assert "xmp" not in got.info
    assert "XML:com.adobe.xmp" not in got.info
    assert "Comment" not in got.info
    assert got.exif == {}
    assert got.text == {}
    assert b"private" not in out.read_bytes()


@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_same_size_is_not_resampled(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.4"
    board = Image.new("RGB", SIZE)
    width, height = SIZE
    board.putdata(
        [(255, 255, 255) if (x + y) % 2 else (0, 0, 0) for y in range(height) for x in range(width)]
    )
    source = tmp_path / "board.png"
    board.save(source, format="PNG")
    out = tmp_path / "board-export.png"
    _done(_export(source, out, fmt="png"))
    got = _read(out)
    assert (got.image.mode, got.image.size) == ("RGB", SIZE)
    assert got.image.tobytes() == board.tobytes()


@pytest.mark.parametrize("fmt", FORMATS)
@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_shrink_gives_exactly_size(ac_id: str, fmt: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.4"
    source = tmp_path / "source.png"
    _distinct().save(source, format="PNG")
    for size in (SIZE, SHRUNK, (17, 5)):
        out = tmp_path / f"out-{size[0]}x{size[1]}{SUFFIX[fmt]}"
        probe = _done(_export(source, out, fmt=fmt, size=size))
        assert (probe.width, probe.height) == size
        got = _read(out)
        assert (got.format, got.image.size) == (PIL_FORMAT[fmt], size)


@pytest.mark.parametrize("fmt", FORMATS)
@pytest.mark.parametrize("mode", list(MODE_WANT), ids=[m.replace(";", "") for m in MODE_WANT])
@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_modes(ac_id: str, mode: str, fmt: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.4"
    source = _mode_source(mode, tmp_path)
    out = tmp_path / f"out{SUFFIX[fmt]}"
    _done(_export(source, out, fmt=fmt))
    got = _read(out)
    assert (got.format, got.image.mode, got.image.size) == (
        PIL_FORMAT[fmt],
        MODE_WANT[mode][fmt],
        SIZE,
    )
    if mode == "P" and fmt == "png":
        assert got.info.get("transparency") == 3
    small = tmp_path / f"small{SUFFIX[fmt]}"
    _done(_export(source, small, fmt=fmt, size=SHRUNK))
    shrunk = _read(small)
    want = MODE_WANT_SHRUNK_PNG[mode] if fmt == "png" else MODE_WANT[mode][fmt]
    assert (shrunk.format, shrunk.image.mode, shrunk.image.size) == (PIL_FORMAT[fmt], want, SHRUNK)
    if "A" in shrunk.image.mode:
        assert "transparency" not in shrunk.info


@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_depth_map_formula(ac_id: str) -> None:
    """D-619: `_depth_to_l` over every `I;16` value, and an `I` image's out-of-range values."""
    assert ac_id == "AC-136.4"
    depth_to_l = getattr(adapter_mod, "_depth_to_l", None)
    assert callable(depth_to_l), "the adapter has no _depth_to_l"
    assert getattr(adapter_mod, "EXPORT_DEPTH_MODES", None) == DEPTH_MODES
    assert callable(getattr(adapter_mod, "_png_key", None)), "the adapter has no _png_key"
    every = _i16(list(range(65536)), (256, 256))
    mapped = depth_to_l(every)
    assert (mapped.mode, mapped.size) == ("L", (256, 256))
    got = list(mapped.getdata())
    want = [(2 * v * 255 + 65535) // (2 * 65535) for v in range(65536)]
    mismatches = [v for v in range(65536) if got[v] != want[v]]
    assert mismatches == []
    # The formula is v * 255 / 65535 rounded half up, checked against Fraction at the blocks.
    for v, level in zip(DEPTH_BLOCKS, DEPTH_L, strict=True):
        assert want[v] == level == int(Fraction(v * 255, 65535) + Fraction(1, 2))
    wide = Image.new("I", (2, 1))
    wide.putdata([-5, 70000])
    clamped = depth_to_l(wide)
    assert (clamped.mode, list(clamped.getdata())) == ("L", [0, 255])


@pytest.mark.parametrize("fmt", FORMATS)
@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_depth_blocks(ac_id: str, fmt: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.4"
    source = _depth_source(tmp_path)
    for size, centres in (((256, 64), DEPTH_CENTRES), ((128, 32), DEPTH_CENTRES_128)):
        out = tmp_path / f"depth-{size[0]}{SUFFIX[fmt]}"
        _done(_export(source, out, fmt=fmt, size=size))
        got = _read(out)
        assert (got.format, got.image.size) == (PIL_FORMAT[fmt], size)
        if fmt == "png":
            assert got.image.mode == "I;16"
            tol = 0 if size == (256, 64) else 1
            values = [got.image.getpixel(xy) for xy in centres]
            assert all(
                _within(int(v), w, tol)
                for v, w in zip(values, DEPTH_BLOCKS, strict=True)  # type: ignore[arg-type]
            ), values
        else:
            levels = [got.rgba(xy)[:3] for xy in centres]
            for level, want in zip(levels, DEPTH_L, strict=True):
                assert all(_within(c, want, 2) for c in level), (levels, DEPTH_L)
            assert all(c != 255 for c in levels[KEYED]), levels


@pytest.mark.parametrize("fmt", FORMATS)
@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_depth_with_key(ac_id: str, fmt: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.4"
    source = _depth_source(tmp_path, key=DEPTH_BLOCKS[KEYED])
    for size, centres in (((256, 64), DEPTH_CENTRES), ((128, 32), DEPTH_CENTRES_128)):
        out = tmp_path / f"keyed-{size[0]}{SUFFIX[fmt]}"
        _done(_export(source, out, fmt=fmt, size=size))
        got = _read(out)
        assert (got.format, got.image.size) == (PIL_FORMAT[fmt], size)
        if fmt == "png" and size == (256, 64):
            assert got.image.mode == "I;16"
            assert got.info.get("transparency") == DEPTH_BLOCKS[KEYED]
            continue
        pixels = [got.rgba(xy) for xy in centres]
        if fmt == "jpeg":
            assert got.image.mode == "RGB"
            for pixel, want in zip(pixels, DEPTH_L, strict=True):
                assert all(_within(c, want, 2) for c in pixel[:3]), (pixels, DEPTH_L)
            continue
        assert got.image.mode == ("RGBA" if fmt == "webp" else "LA")
        assert "transparency" not in got.info
        tol = 2 if fmt == "webp" else 1
        for index, (pixel, want) in enumerate(zip(pixels, DEPTH_L, strict=True)):
            if index == KEYED:
                assert pixel[3] == 0, pixels
                continue
            assert pixel[3] == 255, pixels
            assert all(_within(c, want, tol) for c in pixel[:3]), (pixels, DEPTH_L)


def _stored_colour_sources(folder: Path) -> list[Path]:
    """A 256x64 RGBA and P source whose left half is fully transparent, stored as (200, 40, 40)."""
    rgba = Image.new("RGBA", (256, 64), (20, 20, 200, 255))
    rgba.paste((200, 40, 40, 0), (0, 0, 128, 64))
    rgba_path = folder / "stored-rgba.png"
    rgba.save(rgba_path, format="PNG")
    pal = Image.new("P", (256, 64), 1)
    pal.putpalette([200, 40, 40, 20, 20, 200])
    pal.paste(0, (0, 0, 128, 64))
    pal_path = folder / "stored-p.png"
    pal.save(pal_path, format="PNG", transparency=0)
    for path in (rgba_path, pal_path):
        assert _read(path).rgba((64, 32)) == (200, 40, 40, 0), path.name
    return [rgba_path, pal_path]


@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_jpeg_shows_the_stored_colour(ac_id: str, tmp_path: Path) -> None:
    """Round 2 F1: alpha is dropped before any resize, so the hidden colour shows, never black."""
    assert ac_id == "AC-136.4"
    for source in _stored_colour_sources(tmp_path):
        for size, centre in (((256, 64), (64, 32)), ((128, 32), (32, 16))):
            out = tmp_path / f"{source.stem}-{size[0]}.jpg"
            _done(_export(source, out, fmt="jpeg", size=size))
            got = _read(out)
            assert (got.image.mode, got.image.size) == ("RGB", size)
            pixel = got.rgba(centre)[:3]
            assert all(_within(c, w, 3) for c, w in zip(pixel, (200, 40, 40), strict=True)), (
                source.name,
                size,
                pixel,
            )


@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_keyed_l_and_rgb_shrunk_to_png(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.4"
    gray = Image.new("L", (256, 64), 30)
    gray.paste(128, (0, 0, 128, 64))
    gray_path = tmp_path / "keyed-l.png"
    gray.save(gray_path, format="PNG", transparency=128)
    colour = Image.new("RGB", (256, 64), (20, 20, 200))
    colour.paste((200, 40, 40), (0, 0, 128, 64))
    colour_path = tmp_path / "keyed-rgb.png"
    colour.save(colour_path, format="PNG", transparency=(200, 40, 40))
    for source, mode in ((gray_path, "LA"), (colour_path, "RGBA")):
        out = tmp_path / f"{source.stem}-small.png"
        _done(_export(source, out, fmt="png", size=(128, 32)))
        got = _read(out)
        assert (got.image.mode, got.image.size) == (mode, (128, 32))
        assert "transparency" not in got.info
        assert got.rgba((32, 16))[3] == 0
        assert got.rgba((96, 16))[3] == 255


@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_one_bit_columns_keep_half_alpha(ac_id: str, tmp_path: Path) -> None:
    """Round 3 F5: 1-px black and keyed-white columns shrink to half alpha over black."""
    assert ac_id == "AC-136.4"
    source = tmp_path / "columns.png"
    source.write_bytes(_gray_png(1, [x % 2 for x in range(256)], 1))
    for fmt, mode in (("png", "LA"), ("webp", "RGBA")):
        out = tmp_path / f"columns-small{SUFFIX[fmt]}"
        _done(_export(source, out, fmt=fmt, size=(128, 32)))
        got = _read(out)
        assert (got.image.mode, got.image.size) == (mode, (128, 32))
        assert "transparency" not in got.info
        pixel = got.rgba((64, 16))
        assert pixel != (127, 127, 127, 255)
        assert _within(pixel[3], 127, 10), pixel
        assert all(_within(c, 0, 10) for c in pixel[:3]), pixel


LOW_BIT_KEYS = ((1, 0), (1, 1), (2, 1), (2, 3), (4, 1), (4, 15))


@pytest.mark.parametrize(
    ("depth", "key"), LOW_BIT_KEYS, ids=[f"d{d}-key{k}" for d, k in LOW_BIT_KEYS]
)
@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_low_bit_keys(ac_id: str, depth: int, key: int, tmp_path: Path) -> None:
    """Round 3 F5: 32-px stripes, keyed alternating with unkeyed, at depths 1, 2 and 4."""
    assert ac_id == "AC-136.4"
    top = (1 << depth) - 1
    other = 0 if key != 0 else top
    row = [key if (x // 32) % 2 else other for x in range(256)]
    source = tmp_path / f"stripes-d{depth}.png"
    source.write_bytes(_gray_png(depth, row, key))
    stored = round(key * 255 / top)
    for size in ((256, 64), (128, 32)):
        stripe = 32 * size[0] // 256
        keyed = [(stripe + stripe // 2 + 2 * stripe * k, size[1] // 2) for k in range(4)]
        clear = [(stripe // 2 + 2 * stripe * k, size[1] // 2) for k in range(4)]
        for fmt in FORMATS:
            out = tmp_path / f"stripes-{size[0]}{SUFFIX[fmt]}"
            _done(_export(source, out, fmt=fmt, size=size))
            got = _read(out)
            assert got.image.size == size
            if fmt == "jpeg":
                for xy in keyed:
                    assert all(_within(c, stored, 3) for c in got.rgba(xy)[:3]), (xy, got.rgba(xy))
                continue
            assert [got.rgba(xy)[3] for xy in keyed] == [0, 0, 0, 0], (fmt, size)
            assert [got.rgba(xy)[3] for xy in clear] == [255, 255, 255, 255], (fmt, size)
            if "A" in got.image.mode:
                assert "transparency" not in got.info, (fmt, size, got.info)


@_ac("AC-136.4")
@pytest.mark.unit
def test_ac_136_4_sixteen_bit_rgb_key_is_dropped(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.4"
    row = [(0x8012, 0x4034, 0x2056), (0x8099, 0x40AA, 0x20BB)] * 8
    source = tmp_path / "rgb16.png"
    source.write_bytes(_rgb16_png(row, row[0]))
    for fmt, size in (("png", (16, 8)), ("png", (8, 4)), ("webp", (16, 8))):
        out = tmp_path / f"rgb16-{size[0]}{SUFFIX[fmt]}"
        _done(_export(source, out, fmt=fmt, size=size))
        got = _read(out)
        assert "transparency" not in got.info
        alphas = {pixel[3] for pixel in got.image.convert("RGBA").getdata()}  # type: ignore[index]
        assert alphas == {255}


# --- AC-136.5: quality -------------------------------------------------------------------------


@pytest.mark.parametrize("fmt", ("jpeg", "webp"))
@_ac("AC-136.5")
@pytest.mark.unit
def test_ac_136_5_quality_orders_bytes(ac_id: str, fmt: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.5"
    noise = Image.frombytes("RGB", (512, 512), random.Random(136).randbytes(512 * 512 * 3))
    source = tmp_path / "noise.png"
    noise.save(source, format="PNG")
    low = _done(_export(source, tmp_path / f"q20{SUFFIX[fmt]}", fmt=fmt, quality=20))
    high = _done(_export(source, tmp_path / f"q95{SUFFIX[fmt]}", fmt=fmt, quality=95))
    assert low.file_size < high.file_size


@_ac("AC-136.5")
@pytest.mark.unit
def test_ac_136_5_quality_reaches_the_save(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-136.5"
    source = tmp_path / "source.png"
    _distinct().save(source, format="PNG")
    assert callable(Image.Image.save)
    real_save: Callable[..., None] = Image.Image.save
    seen: list[dict[str, Any]] = []

    def recording_save(self: Image.Image, fp: Any, format: Any = None, **params: Any) -> None:  # noqa: A002
        seen.append({"format": format, **params})
        real_save(self, fp, format, **params)

    monkeypatch.setattr(Image.Image, "save", recording_save)
    cases = (
        ("jpeg", None, 90),
        ("jpeg", 37, 37),
        ("webp", None, 90),
        ("webp", 37, 37),
        ("png", None, None),
    )
    for fmt, quality, want in cases:
        seen.clear()
        _done(
            _export(source, tmp_path / f"q-{fmt}-{quality}{SUFFIX[fmt]}", fmt=fmt, quality=quality)
        )
        assert len(seen) == 1, (fmt, quality, seen)
        if want is None:
            assert "quality" not in seen[0], seen
        else:
            assert seen[0].get("quality") == want, (fmt, quality, seen)
        for key in ("exif", "xmp", "pnginfo"):
            assert key not in seen[0], (key, seen)


# --- AC-136.6: adapter failures ----------------------------------------------------------------


@_ac("AC-136.6")
@pytest.mark.unit
def test_ac_136_6_undecodable_source(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.6"
    source = tmp_path / "broken.png"
    source.write_bytes(b"\x89PNG\r\n\x1a\nnot really an image")
    for fmt in FORMATS:
        out = tmp_path / f"broken-export{SUFFIX[fmt]}"
        result = _export(source, out, fmt=fmt, source_size=SIZE)
        assert _raised(result) == (InboxPathError, NOT_OPENED)
        assert not out.exists()


@_ac("AC-136.6")
@pytest.mark.unit
def test_ac_136_6_size_changed(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.6"
    source = tmp_path / "source.png"
    _distinct().save(source, format="PNG")
    out = tmp_path / "out.png"
    result = _export(source, out, fmt="png", source_size=(65, 48), size=(64, 48))
    assert _raised(result) == (ConflictError, CHANGED)
    assert not out.exists()


@_ac("AC-136.6")
@pytest.mark.unit
def test_ac_136_6_save_failure_names_no_path(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-136.6"
    source = tmp_path / "source.png"
    _distinct().save(source, format="PNG")
    marker = str(tmp_path / "private-marker-136" / "out.png")
    assert callable(Image.Image.save)

    def failing_save(self: Image.Image, fp: Any, format: Any = None, **params: Any) -> None:  # noqa: A002
        raise OSError(f"cannot write {marker}")

    monkeypatch.setattr(Image.Image, "save", failing_save)
    for fmt in FORMATS:
        result = _export(source, tmp_path / f"out{SUFFIX[fmt]}", fmt=fmt)
        assert _raised(result) == (OSError, NOT_SAVED)
        assert marker not in str(result)
        assert "private-marker-136" not in str(result)


# --- AC-136.7: CAPTURE-EXIF-SCANNED-ORIENTATION ------------------------------------------------


@pytest.mark.parametrize("fmt", FORMATS)
@_ac("AC-136.7")
@pytest.mark.unit
def test_ac_136_7_exif_orientation_is_not_applied(ac_id: str, fmt: str, tmp_path: Path) -> None:
    """Characterises the known issue CAPTURE-EXIF-SCANNED-ORIENTATION (D-613).

    A JPEG tagged orientation 6 exports in its stored frame, as crop does: no `exif_transpose`,
    and the tag is dropped with the rest of the EXIF. This records the behaviour; it fixes
    nothing.
    """
    assert ac_id == "AC-136.7"
    image = Image.new("RGB", (400, 300), (20, 20, 200))
    image.paste((230, 20, 20), (0, 0, 40, 40))
    exif = Image.Exif()
    exif[0x0112] = 6
    source = tmp_path / "turned.jpg"
    image.save(source, format="JPEG", quality=95, exif=exif)
    planted = _read(source)
    assert planted.exif.get(0x0112) == 6
    assert planted.image.size == (400, 300)
    out = tmp_path / f"turned-export{SUFFIX[fmt]}"
    _done(_export(source, out, fmt=fmt))
    got = _read(out)
    assert got.image.size == (400, 300)
    red = got.rgba((10, 10))[:3]
    assert red[0] > 180 and red[1] < 70 and red[2] < 70, red
    blue = got.rgba((390, 290))[:3]
    assert blue[2] > 150 and blue[0] < 70, blue
    assert 0x0112 not in got.exif
    assert "exif" not in got.info
