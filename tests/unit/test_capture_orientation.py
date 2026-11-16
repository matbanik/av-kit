"""MEU-146 (Session 75): one frame for a shot with an EXIF orientation (D-903 to D-910).

AC-146.1 to AC-146.10, AC-146.12 to AC-146.14 and AC-146.20 to AC-146.26. The adapter cases
use the real `CaptureAdapter` on images written in the test: 400x300, blue with a red 40x40
block at the top left, saved as JPEG, PNG and WebP with orientation 1 to 8. The fixtures
whose tag only Pillow reads come from `tests/orientation_fixtures.py`, the builder AC-146.19
uses in the Electron suite. The service cases use the real `CaptureService` with a subclass
of `FakeCapturePort`. New names are imported inside each test, and each test catches what a
call raises and then asserts on it, so a Red run fails by assertion, never by setup.
"""

from __future__ import annotations

import io
import json
import os
import stat
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

SIZE = (400, 300)
TURNED = (300, 400)
BLUE = (20, 20, 200)
RED = (230, 20, 20)
GREEN = "#00FF00"
TAG = 0x0112
MARK = "s75mark"
STALE_EVENT = "capture.stale_bake_failed"
LOG_KEYS = {"event", "log_level", "module", "count"}
SUFFIX = {"jpg": ".jpg", "png": ".png", "webp": ".webp"}
PIL_FORMAT = {"jpg": "JPEG", "png": "PNG", "webp": "WEBP"}
# Where the red block's centre shows for each tag in the shown frame (s75-plan-probe-electron).
RED_AT = {
    1: (10, 10),
    2: (390, 10),
    3: (390, 290),
    4: (10, 290),
    5: (10, 10),
    6: (290, 10),
    7: (290, 390),
    8: (10, 390),
}
SENTINEL = b"read-shown-sentinel"


def _ac146(n: int) -> pytest.MarkDecorator:
    label = f"AC-146.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _raised(call: Callable[[], object]) -> tuple[Any, Exception | None]:
    """Run `call`; return its result and the exception it raised (None when it returned)."""
    try:
        return call(), None
    except Exception as exc:
        return None, exc


def _frame(size: tuple[int, int] = SIZE, block: int = 40) -> Any:
    from PIL import Image

    image = Image.new("RGB", size, BLUE)
    image.paste(RED, (0, 0, block, block))
    return image


def _exif(tag: int) -> bytes:
    from PIL import Image

    exif = Image.Exif()
    exif[TAG] = tag
    return exif.tobytes()


def _encoded(kind: str, tag: int | None, *, icc: bytes | None = None) -> bytes:
    """The 400x300 frame as `kind` (jpg, png, webp), tagged `tag` (None: no EXIF block)."""
    params: dict[str, object] = {}
    if kind in ("jpg", "webp"):
        params["quality"] = 95
    if tag is not None:
        params["exif"] = _exif(tag)
    if icc is not None:
        params["icc_profile"] = icc
    buffer = io.BytesIO()
    _frame().save(buffer, format=PIL_FORMAT[kind], **params)
    return buffer.getvalue()


def _mpo(tag: int) -> bytes:
    """Two 40x30 frames (a 10x10 red block), the first tagged `tag`, saved as MPO."""
    first = _frame((40, 30), 10)
    buffer = io.BytesIO()
    first.save(
        buffer, format="MPO", exif=_exif(tag), save_all=True, append_images=[_frame((40, 30), 10)]
    )
    return buffer.getvalue()


def _junk_jpeg() -> bytes:
    buffer = io.BytesIO()
    _frame().save(buffer, format="JPEG", quality=95, exif=b"Exif\x00\x00garbage")
    return buffer.getvalue()


def _write(folder: Path, name: str, data: bytes) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_bytes(data)
    return path


def _tagged(folder: Path, kinds: tuple[str, ...] = ("jpg", "png", "webp")) -> dict[Any, Path]:
    """Each kind with no tag (key None) and with tags 1 to 8, keyed `(kind, tag)`."""
    files: dict[Any, Path] = {}
    for kind in kinds:
        for tag in (None, *range(1, 9)):
            name = f"{kind}-{'none' if tag is None else tag}{SUFFIX[kind]}"
            files[(kind, tag)] = _write(folder, name, _encoded(kind, tag))
    return files


def _builder(folder: Path) -> tuple[dict[str, Path], dict[str, dict[str, object]]]:
    """The builder's eight fixtures and its report; every one must read 6 by `getexif()`."""
    from tests.orientation_fixtures import build

    report = build(folder)
    for name, entry in report.items():
        assert entry["getexif_tag"] == 6, f"the builder's {name} lost its tag"
    return {name: folder / name for name in report}, report


def _look(data: bytes) -> tuple[str | None, tuple[int, int], Any, object, object]:
    """Decode `data`: format, size, RGB pixels, the orientation tag and the ICC profile."""
    from PIL import Image

    with Image.open(io.BytesIO(data)) as image:
        fmt = image.format
        image.load()
        tag = image.getexif().get(TAG)
        icc = image.info.get("icc_profile")
        rgb = image.convert("RGB")
    return fmt, rgb.size, rgb, tag, icc


def _red(pixel: tuple[int, ...]) -> bool:
    return pixel[0] > 200 and pixel[1] < 60 and pixel[2] < 60


def _green(pixel: tuple[int, ...]) -> bool:
    return pixel[1] > 200 and pixel[0] < 60 and pixel[2] < 60


def _shown_size(tag: int) -> tuple[int, int]:
    return TURNED if tag >= 5 else SIZE


@_ac146(1)
@pytest.mark.unit
def test_ac_146_1_shown_orientation_reads_only_the_exif_block(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.1"
    from PIL import Image

    from avkit_infra.capture.adapter import shown_orientation

    def shown(path: Path) -> tuple[Any, Exception | None]:
        with Image.open(path) as image:
            return _raised(lambda: shown_orientation(image))

    files = _tagged(tmp_path / "tagged")
    built, _report = _builder(tmp_path / "built")
    expected: dict[str, tuple[Path, int]] = {}
    for kind in ("jpg", "png"):
        expected[f"{kind} none"] = (files[(kind, None)], 1)
        for tag in range(1, 9):
            expected[f"{kind} {tag}"] = (files[(kind, tag)], tag)
    for tag in range(1, 9):
        mpo = _write(tmp_path / "mpo", f"mpo-{tag}.jpg", _mpo(tag))
        with Image.open(mpo) as image:
            assert image.format == "MPO", f"mpo {tag} did not open as MPO"
        expected[f"mpo {tag}"] = (mpo, tag)
        webp = files[("webp", tag)]
        with Image.open(webp) as image:
            assert image.getexif().get(TAG) == tag, f"webp {tag} lost its tag"
        expected[f"webp {tag}"] = (webp, 1)
    expected["builder o6.png"] = (built["o6.png"], 6)
    for name in ("o6-xmp.jpg", "o6-raw-profile.png", "o6-after-idat.png", "o6-prefixed.png"):
        expected[f"builder {name}"] = (built[name], 1)
    expected["junk exif"] = (_write(tmp_path / "odd", "junk.jpg", _junk_jpeg()), 1)
    for tag in (0, 9):
        expected[f"tag {tag}"] = (_write(tmp_path / "odd", f"t{tag}.jpg", _encoded("jpg", tag)), 1)
    wrong = {}
    for label, (path, want) in expected.items():
        got, exc = shown(path)
        if exc is not None or got != want:
            wrong[label] = type(exc).__name__ if exc is not None else got
    assert wrong == {}, f"cases that did not give their shown tag: {wrong}"


@_ac146(2)
@pytest.mark.unit
def test_ac_146_2_probe_swaps_width_and_height_for_5_to_8(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-146.2"
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    files = _tagged(tmp_path, ("jpg", "png"))
    wrong = {}
    for kind in ("jpg", "png"):
        for tag in range(1, 9):
            probe, exc = _raised(lambda path=files[(kind, tag)]: CaptureAdapter().probe(path))
            got = None if exc else (probe.width, probe.height)
            if got != _shown_size(tag):
                wrong[f"{kind} {tag}"] = type(exc).__name__ if exc else got
    assert wrong == {}, f"probe sizes off the shown frame: {wrong}"

    def no_transpose(self: object, method: object) -> object:
        raise AssertionError("probe turned the pixels")

    monkeypatch.setattr(Image.Image, "transpose", no_transpose)
    probe, exc = _raised(lambda: CaptureAdapter().probe(files[("jpg", 6)]))
    monkeypatch.undo()
    assert exc is None, f"probe with no transpose raised {type(exc).__name__}"
    assert (probe.width, probe.height) == TURNED


@_ac146(3)
@pytest.mark.unit
def test_ac_146_3_probe_keeps_the_stored_size_off_the_set(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.3"
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _tagged(tmp_path / "tagged", ("webp",))
    built, _report = _builder(tmp_path / "built")
    expected: dict[str, tuple[Path, tuple[int, int]]] = {
        f"webp {tag}": (files[("webp", tag)], SIZE) for tag in range(1, 9)
    }
    expected["mpo 6"] = (_write(tmp_path / "mpo", "mpo-6.jpg", _mpo(6)), (30, 40))
    expected["junk exif"] = (_write(tmp_path / "odd", "junk.jpg", _junk_jpeg()), SIZE)
    for name in ("o6-xmp.jpg", "o6-raw-profile.png", "o6-after-idat.png"):
        expected[f"builder {name}"] = (built[name], (40, 30))
    wrong = {}
    for label, (path, want) in expected.items():
        probe, exc = _raised(lambda path=path: CaptureAdapter().probe(path))
        got = None if exc else (probe.width, probe.height)
        if got != want:
            wrong[label] = type(exc).__name__ if exc else got
    assert wrong == {}, f"probe sizes: {wrong}"


@_ac146(4)
@pytest.mark.unit
def test_ac_146_4_whole_view_of_a_tagged_file_is_upright(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.4"
    from avkit_core.domain.capture import view_frame
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _tagged(tmp_path, ("jpg", "png"))
    wrong = {}
    for kind in ("jpg", "png"):
        for tag in range(2, 9):
            path = files[(kind, tag)]
            frame = view_frame(*_shown_size(tag))
            data, exc = _raised(lambda path=path, frame=frame: CaptureAdapter().view(path, frame))
            if exc is not None:
                wrong[f"{kind} {tag}"] = type(exc).__name__
                continue
            fmt, size, rgb, got_tag, _icc = _look(data)
            if (fmt, size) != (PIL_FORMAT[kind], _shown_size(tag)):
                wrong[f"{kind} {tag}"] = (fmt, size)
            elif not _red(rgb.getpixel(RED_AT[tag])) or got_tag is not None:
                wrong[f"{kind} {tag}"] = ("red", rgb.getpixel(RED_AT[tag]), "tag", got_tag)
    assert wrong == {}, f"whole views not upright: {wrong}"


@_ac146(5)
@pytest.mark.unit
def test_ac_146_5_whole_view_of_an_untagged_file_is_the_file(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.5"
    from avkit_core.domain.capture import view_frame
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _tagged(tmp_path)
    for key in (("png", None), ("jpg", 1), ("webp", 6)):
        path = files[key]
        data, exc = _raised(lambda path=path: CaptureAdapter().view(path, view_frame(*SIZE)))
        assert exc is None, f"{key}: the view raised {type(exc).__name__}"
        assert data == path.read_bytes(), f"{key}: the whole view is not the file"


@_ac146(6)
@pytest.mark.unit
def test_ac_146_6_region_is_cut_from_the_shown_frame(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.6"
    from avkit_core.domain.capture import view_frame
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _tagged(tmp_path, ("jpg", "png"))
    for kind in ("jpg", "png"):
        frame = view_frame(*TURNED, x=260, y=0, width=40, height=40)
        path = files[(kind, 6)]
        data, exc = _raised(lambda path=path, frame=frame: CaptureAdapter().view(path, frame))
        assert exc is None, f"{kind}: the region raised {type(exc).__name__}"
        _fmt, size, rgb, _tag, _icc = _look(data)
        assert size == (160, 160), f"{kind}: region size {size}"
        assert _red(rgb.getpixel((20, 20))), f"{kind}: the region centre is not red"


@_ac146(7)
@pytest.mark.unit
def test_ac_146_7_view_at_the_stored_size_is_a_conflict(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.7"
    from avkit_core.domain.capture import view_frame
    from avkit_core.domain.errors import ConflictError
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _tagged(tmp_path, ("jpg", "png"))
    for kind in ("jpg", "png"):
        path = files[(kind, 6)]
        _, exc = _raised(lambda path=path: CaptureAdapter().view(path, view_frame(*SIZE)))
        assert isinstance(exc, ConflictError), f"{kind}: no conflict for the stored size"


@_ac146(8)
@pytest.mark.unit
def test_ac_146_8_crop_cuts_the_shown_frame(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.8"
    from avkit_infra.capture.adapter import CaptureAdapter

    source = _write(tmp_path, "t6.jpg", _encoded("jpg", 6))
    out = tmp_path / "t6.crop.png"
    _, exc = _raised(lambda: CaptureAdapter().crop(source, (260, 0, 40, 40), TURNED, out))
    assert exc is None, f"the crop raised {type(exc).__name__}"
    fmt, size, rgb, tag, _icc = _look(out.read_bytes())
    assert (fmt, size) == ("PNG", (40, 40))
    assert _red(rgb.getpixel((20, 20))), "the crop centre is not red"
    assert tag is None, "the crop carries an orientation tag"
    from PIL import Image

    with Image.open(out) as image:
        assert "exif" not in image.info, "the crop carries an EXIF block"


@_ac146(9)
@pytest.mark.unit
def test_ac_146_9_bake_draws_the_mark_in_the_shown_frame(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.9"
    from avkit_core.domain.capture import RedactAnnotation
    from avkit_infra.capture.adapter import CaptureAdapter

    source = _write(tmp_path, "t6.jpg", _encoded("jpg", 6))
    out = tmp_path / "t6.annotated.png"
    mark = RedactAnnotation(x=100, y=330, width=40, height=40, color=GREEN)
    _, exc = _raised(lambda: CaptureAdapter().bake(source, [mark], out))
    assert exc is None, f"the bake raised {type(exc).__name__}"
    fmt, size, rgb, _tag, _icc = _look(out.read_bytes())
    assert size == TURNED, f"the bake is {size}"
    assert fmt == "PNG"
    assert _green(rgb.getpixel((120, 350))), "the mark is not where it was drawn"


@_ac146(10)
@pytest.mark.unit
def test_ac_146_10_render_gives_the_same_pixels_as_the_bake(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.10"
    from avkit_core.domain.capture import RedactAnnotation
    from avkit_infra.capture.adapter import CaptureAdapter

    source = _write(tmp_path, "t6.jpg", _encoded("jpg", 6))
    out = tmp_path / "t6.annotated.png"
    mark = RedactAnnotation(x=100, y=330, width=40, height=40, color=GREEN)
    rendered, exc = _raised(lambda: CaptureAdapter().render(source, [mark]))
    assert exc is None, f"the render raised {type(exc).__name__}"
    _, exc = _raised(lambda: CaptureAdapter().bake(source, [mark], out))
    assert exc is None, f"the bake raised {type(exc).__name__}"
    _fmt, size, rgb, _tag, _icc = _look(rendered)
    assert size == TURNED, f"the render is {size}"
    assert rgb.tobytes() == _look(out.read_bytes())[2].tobytes(), "render and bake differ"


def _sized_stack(tmp_path: Path) -> tuple[Any, Any, Any, Path]:
    from tests.unit.test_capture_service import _stack

    service, uow, port, inbox = _stack(tmp_path)
    port.width, port.height = SIZE
    return service, uow, port, inbox


def _size_of(uow: Any, path: Path) -> tuple[int, int] | None:
    shot = uow.capture_shots.get_by_path(path)
    return None if shot is None else (shot.width, shot.height)


@_ac146(12)
@pytest.mark.unit
def test_ac_146_12_scan_refreshes_a_size_that_swapped(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.12"
    from tests.unit.test_capture_service import _write_inbox_file

    service, uow, port, inbox = _sized_stack(tmp_path)
    path = _write_inbox_file(inbox, "t6.jpg")
    _, exc = _raised(service.scan_inbox)
    assert exc is None and _size_of(uow, path) == SIZE
    port.width, port.height = TURNED
    _, exc = _raised(service.scan_inbox)
    assert exc is None, f"the second scan raised {type(exc).__name__}"
    assert _size_of(uow, path) == TURNED, "the scan kept the old size"


@_ac146(13)
@pytest.mark.unit
def test_ac_146_13_register_refreshes_a_size_that_swapped(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.13"
    from tests.unit.test_capture_service import _write_inbox_file

    from avkit_core.domain.capture import CaptureSource

    service, uow, port, inbox = _sized_stack(tmp_path)
    path = _write_inbox_file(inbox, "t6.jpg")
    first, exc = _raised(lambda: service.register_shot(path, CaptureSource.Hotkey))
    assert exc is None and (first.width, first.height) == SIZE
    port.width, port.height = TURNED
    second, exc = _raised(lambda: service.register_shot(path, CaptureSource.Hotkey))
    assert exc is None, f"the second register raised {type(exc).__name__}"
    assert second.id == first.id
    assert (second.width, second.height) == TURNED, "register returned the old size"
    assert _size_of(uow, path) == TURNED, "register kept the old size"


@_ac146(14)
@pytest.mark.unit
def test_ac_146_14_import_in_place_refreshes_a_swapped_size(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.14"
    from tests.unit.test_capture_service import _write_inbox_file

    service, uow, port, inbox = _sized_stack(tmp_path)
    port.inspect_import = lambda data: 1
    path = _write_inbox_file(inbox, "t6.jpg")
    first, exc = _raised(lambda: service.import_image(path))
    assert exc is None and (first.width, first.height) == SIZE
    port.width, port.height = TURNED
    second, exc = _raised(lambda: service.import_image(path))
    assert exc is None, f"the second import raised {type(exc).__name__}"
    assert second.id == first.id
    assert (second.width, second.height) == TURNED, "import returned the old size"
    assert _size_of(uow, path) == TURNED, "import kept the old size"


@_ac146(20)
@pytest.mark.unit
def test_ac_146_20_read_shown_turns_a_tagged_file_upright(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.20"
    from avkit_infra.capture.adapter import CaptureAdapter

    cases = {
        "jpg": (_write(tmp_path, "t6.jpg", _encoded("jpg", 6)), "JPEG", TURNED, (290, 10)),
        "png": (_write(tmp_path, "t6.png", _encoded("png", 6)), "PNG", TURNED, (290, 10)),
        "mpo": (_write(tmp_path, "mpo6.jpg", _mpo(6)), "JPEG", (30, 40), (25, 5)),
    }
    for label, (path, want_fmt, want_size, red_at) in cases.items():
        data, exc = _raised(lambda path=path: CaptureAdapter().read_shown(path))
        assert exc is None, f"{label}: read_shown raised {type(exc).__name__}"
        fmt, size, rgb, tag, _icc = _look(data)
        assert (fmt, size) == (want_fmt, want_size), f"{label}: {(fmt, size)}"
        assert _red(rgb.getpixel(red_at)), f"{label}: red is not at the shown corner"
        assert tag is None, f"{label}: the result carries an orientation tag"


@_ac146(20)
@pytest.mark.unit
def test_ac_146_20_read_shown_keeps_palette_alpha(ac_id: str, tmp_path: Path) -> None:
    """F1 (D-1002): a tag-6 palette PNG's tRNS alpha survives `read_shown`, as in `view`."""
    assert ac_id == "AC-146.20"
    from PIL import Image

    from avkit_core.domain.capture import view_frame
    from avkit_infra.capture.adapter import CaptureAdapter

    stored = Image.new("P", (4, 2), 2)
    stored.putpalette([230, 20, 20, 20, 200, 20, 20, 20, 200])
    stored.putpixel((0, 0), 0)
    stored.putpixel((3, 0), 1)
    buffer = io.BytesIO()
    stored.save(buffer, format="PNG", exif=_exif(6), transparency=bytes([0, 128, 255]))
    path = _write(tmp_path, "p6.png", buffer.getvalue())
    with Image.open(path) as image:
        fixture = (image.mode, image.getexif().get(TAG), "transparency" in image.info)
    assert fixture == ("P", 6, True), f"the fixture is not a tagged tRNS palette PNG: {fixture}"
    # Tag 6 shows stored (x, y) of the 4x2 frame at (1 - y, x): (0, 0) at (1, 0), (3, 0) at (1, 3).
    want = {(1, 0): 0, (1, 3): 128, (0, 0): 255}
    calls = {
        "view": lambda: CaptureAdapter().view(path, view_frame(2, 4)),
        "read_shown": lambda: CaptureAdapter().read_shown(path),
    }
    for label, call in calls.items():
        data, exc = _raised(call)
        assert exc is None, f"{label}: raised {type(exc).__name__}"
        with Image.open(io.BytesIO(data)) as got:
            alpha_band = got.convert("RGBA").getchannel("A")
        assert alpha_band.size == (2, 4), f"{label}: {alpha_band.size}"
        alpha = {at: alpha_band.getpixel(at) for at in want}
        assert alpha == want, f"{label}: the palette alpha was not kept: {alpha}"


@_ac146(21)
@pytest.mark.unit
def test_ac_146_21_read_shown_returns_other_files_as_stored(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.21"
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    files = _tagged(tmp_path / "tagged")
    built, _report = _builder(tmp_path / "built")
    tagged = _encoded("jpg", 6)
    half = _write(tmp_path / "odd", "half6.jpg", tagged[: len(tagged) // 2])
    with Image.open(half) as image:
        assert image.getexif().get(TAG) == 6, "the cut JPEG lost its tag"
    cases = {
        "png none": files[("png", None)],
        "jpg 1": files[("jpg", 1)],
        "webp 6": files[("webp", 6)],
        "xmp": built["o6-xmp.jpg"],
        "raw profile": built["o6-raw-profile.png"],
        "after idat": built["o6-after-idat.png"],
        "half jpeg": half,
        "non-image": _write(tmp_path / "odd", "fake.png", b"not an image " + MARK.encode()),
    }
    for label, path in cases.items():
        data, exc = _raised(lambda path=path: CaptureAdapter().read_shown(path))
        assert exc is None, f"{label}: read_shown raised {type(exc).__name__}"
        assert data == path.read_bytes(), f"{label}: the bytes changed"


@_ac146(22)
@pytest.mark.unit
def test_ac_146_22_turned_view_and_read_keep_the_icc_profile(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.22"
    from PIL import ImageCms

    from avkit_core.domain.capture import view_frame
    from avkit_infra.capture.adapter import CaptureAdapter

    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    for kind in ("jpg", "png"):
        path = _write(tmp_path, f"icc6{SUFFIX[kind]}", _encoded(kind, 6, icc=icc))
        assert _look(path.read_bytes())[4] == icc, f"{kind}: the fixture lost its profile"
        calls = {
            "view": lambda path=path: CaptureAdapter().view(path, view_frame(*TURNED)),
            "read_shown": lambda path=path: CaptureAdapter().read_shown(path),
        }
        for label, call in calls.items():
            data, exc = _raised(call)
            assert exc is None, f"{kind} {label}: raised {type(exc).__name__}"
            _fmt, size, _rgb, _tag, got_icc = _look(data)
            assert size == TURNED, f"{kind} {label}: {size}"
            assert got_icc == icc, f"{kind} {label}: the profile was not kept"


def _shown_port() -> Any:
    """A `FakeCapturePort` whose shown tag is set per file name and whose bake is recorded."""
    from tests.unit.test_capture_service import FakeCapturePort

    class ShownPort(FakeCapturePort):
        def __init__(self) -> None:
            super().__init__()
            self.tags: dict[str, int] = {}
            self.calls: list[tuple[Path, list[object], Path, str]] = []
            self.written: dict[str, bytes] = {}
            self.fail = False
            self.shown_reads: list[Path] = []

        def shown_tag(self, path: Path) -> int:
            return self.tags.get(path.name, 1)

        def read_shown(self, path: Path) -> bytes:
            self.shown_reads.append(path)
            return SENTINEL

        def bake(
            self,
            original_path: Path,
            annotations: object,
            output_path: Path,
            output_format: str = "png",
        ) -> object:
            from avkit_core.domain.capture import ImageProbe

            self.calls.append((original_path, list(annotations), output_path, output_format))  # type: ignore[call-overload]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if self.fail:
                output_path.write_bytes(b"part")
                raise OSError(f"{output_path} {MARK} the bake failed")
            data = f"bake {len(self.calls)} of {original_path.name}".encode()
            output_path.write_bytes(data)
            self.written[original_path.name] = data
            return ImageProbe(width=self.width, height=self.height, file_size=len(data))

    return ShownPort()


def _stack_with(root: Path, port: Any) -> tuple[Any, Any, Path]:
    """`_stack` of test_capture_service.py, with the given port and the inbox under `root`."""
    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.services.capture import CaptureService
    from avkit_core.services.settings import SettingsService

    inbox = root / "inbox"
    inbox.mkdir(parents=True)
    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("capture", "inbox_dir", str(inbox))
    service = CaptureService(
        factory,
        capture=port,
        annotate=port,
        settings=settings,
        clock=lambda: datetime(2026, 11, 15, 12, 0, 0, tzinfo=UTC),
    )
    return service, uow, inbox.resolve()


def _mark() -> Any:
    from avkit_core.domain.capture import RedactAnnotation

    return RedactAnnotation(x=2, y=3, width=5, height=6, color=GREEN)


def _annotated(service: Any, uow: Any, port: Any, inbox: Path, name: str, key: int | None) -> Any:
    """A shot saved with one mark, its sidecar rewritten by hand to hold `key` (None: none)."""
    from avkit_core.domain.capture import CaptureSource

    path = inbox / name
    path.write_bytes(f"original {name}".encode())
    shot = service.register_shot(path, CaptureSource.Hotkey)
    service.annotate_and_save(shot.id, [_mark()])
    row = uow.capture_shots.get(shot.id)
    payload = json.loads(row.sidecar_path.read_text(encoding="utf-8"))
    payload.pop("baked_orientation", None)
    if key is not None:
        payload["baked_orientation"] = key
    row.sidecar_path.write_text(json.dumps(payload), encoding="utf-8")
    port.calls.clear()
    port.written.clear()
    return row


def _read(path: Path | None) -> bytes | None:
    return path.read_bytes() if path is not None and path.is_file() else None


def _files(row: Any) -> tuple[bytes | None, ...]:
    return (_read(row.original_path), _read(row.annotated_path), _read(row.sidecar_path))


def _links(uow: Any, row: Any) -> tuple[object, object]:
    now = uow.capture_shots.get(row.id)
    return (now.annotated_path, now.sidecar_path)


def _marks_of(sidecar: Path) -> object:
    return json.loads(sidecar.read_text(encoding="utf-8"))["annotations"]


def _rebake_files(inbox: Path) -> list[str]:
    return sorted(child.name for child in inbox.iterdir() if ".rebake-" in child.name)


def _bakes_for(port: Any, name: str) -> list[tuple[Path, list[object], Path, str]]:
    return [call for call in port.calls if call[0].name == name]


def _scan(service: Any) -> tuple[list[str] | None, list[dict[str, Any]], Exception | None]:
    """List the shots under `capture_logs`: the listed names, the log entries, any raise."""
    from structlog.testing import capture_logs

    with capture_logs() as logs:
        shots, exc = _raised(service.list_shots)
    names = None if exc is not None else sorted(shot.original_path.name for shot in shots)
    return names, logs, exc


def _stale(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [entry for entry in logs if entry.get("event") == STALE_EVENT]


def _one_warning(logs: list[dict[str, Any]], where: str) -> None:
    events = _stale(logs)
    assert len(events) == 1, f"{where}: {len(events)} stale-bake warnings"
    assert set(events[0]) == LOG_KEYS, f"{where}: warning keys {sorted(events[0])}"
    assert events[0]["count"] == 1, f"{where}: count {events[0]['count']}"
    assert events[0]["log_level"] == "warning", f"{where}: level {events[0]['log_level']}"
    for entry in logs:
        for value in entry.values():
            assert MARK not in str(value), f"{where}: a log value holds the marker"


@_ac146(23)
@pytest.mark.unit
def test_ac_146_23_read_image_original_goes_through_read_shown(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.23"
    port = _shown_port()
    service, uow, inbox = _stack_with(tmp_path, port)
    row = _annotated(service, uow, port, inbox, "a.png", None)
    original, exc = _raised(lambda: service.read_image(row.id, "original"))
    assert exc is None, f"original raised {type(exc).__name__}"
    assert original == SENTINEL, "the original was not read through read_shown"
    assert port.shown_reads == [row.original_path]
    annotated, exc = _raised(lambda: service.read_image(row.id, "annotated"))
    assert exc is None, f"annotated raised {type(exc).__name__}"
    assert annotated == row.annotated_path.read_bytes()
    assert port.shown_reads == [row.original_path], "the annotated copy went through read_shown"


@_ac146(24)
@pytest.mark.unit
def test_ac_146_24_sidecar_records_the_baked_orientation(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.24"
    from avkit_core.domain.capture import CaptureSource

    port = _shown_port()
    service, _uow, inbox = _stack_with(tmp_path, port)
    port.tags["t6.jpg"] = 6
    for name in ("t6.jpg", "t1.jpg"):
        (inbox / name).write_bytes(f"original {name}".encode())
    sidecars = {}
    for name in ("t6.jpg", "t1.jpg"):
        shot = service.register_shot(inbox / name, CaptureSource.Hotkey)
        saved, exc = _raised(lambda shot=shot: service.annotate_and_save(shot.id, [_mark()]))
        assert exc is None, f"{name}: the save raised {type(exc).__name__}"
        sidecars[name] = json.loads(saved.sidecar_path.read_text(encoding="utf-8"))
    assert sidecars["t6.jpg"].get("baked_orientation") == 6, "the tag-6 sidecar has no key"
    assert set(sidecars["t1.jpg"]) == {"version", "annotations"}
    assert sidecars["t6.jpg"]["version"] == 1 == sidecars["t1.jpg"]["version"]


@_ac146(25)
@pytest.mark.unit
def test_ac_146_25_scan_rebakes_a_stale_copy_once(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.25"
    from avkit_core.services.capture import annotations_to_wire

    stale = {"no key, tag 6": (None, 6), "no key, tag 3": (None, 3), "key 6, tag 1": (6, 1)}
    for index, (label, (key, shown)) in enumerate(stale.items()):
        port = _shown_port()
        service, uow, inbox = _stack_with(tmp_path / f"case-{index}", port)
        row = _annotated(service, uow, port, inbox, "a.png", key)
        saved_marks = _marks_of(row.sidecar_path)
        port.tags["a.png"] = shown
        names, _logs, exc = _scan(service)
        assert exc is None, f"{label}: the list raised {type(exc).__name__}"
        assert names == ["a.png"]
        assert len(port.calls) == 1, f"{label}: {len(port.calls)} bake calls"
        original, marks, out, fmt = port.calls[0]
        assert original == row.original_path
        assert annotations_to_wire(marks) == saved_marks, f"{label}: the marks changed"
        assert out.parent == row.annotated_path.parent and out != row.annotated_path
        assert fmt == "png", f"{label}: the bake was given {fmt}"
        assert _read(row.annotated_path) == port.written["a.png"], f"{label}: copy not new"
        sidecar = json.loads(row.sidecar_path.read_text(encoding="utf-8"))
        assert sidecar["annotations"] == saved_marks
        assert sidecar.get("baked_orientation") == (None if shown == 1 else shown), label
        assert _links(uow, row) == (row.annotated_path, row.sidecar_path)
        assert _rebake_files(inbox) == [], f"{label}: a .rebake- file is left"
        port.calls.clear()
        _names, _logs, exc = _scan(service)
        assert exc is None and port.calls == [], f"{label}: the second scan baked"
    for index, (key, shown) in enumerate(((6, 6), (None, 1))):
        port = _shown_port()
        service, uow, inbox = _stack_with(tmp_path / f"match-{index}", port)
        _annotated(service, uow, port, inbox, "a.png", key)
        port.tags["a.png"] = shown
        _names, _logs, exc = _scan(service)
        assert exc is None and port.calls == [], f"key {key}, tag {shown}: a match was baked"


def _failing_replace(fail_at: int) -> tuple[Callable[..., None], dict[str, int]]:
    """An `os.replace` raising on a scan's `fail_at`-th call that names a `.rebake-` file."""
    real = os.replace
    state = {"calls": 0}

    def replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
        if ".rebake-" in os.fspath(src) or ".rebake-" in os.fspath(dst):
            state["calls"] += 1
            if state["calls"] == fail_at:
                raise OSError(f"{src} {MARK} the replace failed")
        real(src, dst, *args, **kwargs)

    return replace, state


def _rebake_fails(root: Path, case: str) -> None:
    """Cases (a) to (e) of AC-146.26: one stale shot whose rebake fails, then works."""
    from avkit_core.services import capture as capture_module

    port = _shown_port()
    service, uow, inbox = _stack_with(root, port)
    row = _annotated(service, uow, port, inbox, "a.png", None)
    port.tags["a.png"] = 6
    if case == "d":
        service._settings.set("capture", "annotated_format", "jpeg")
    prior = row.annotated_path.with_name(f".{row.annotated_path.name}.rebake-prior")
    if case == "e":
        os.replace(row.annotated_path, prior)
    before = _files(row)
    old_copy = _read(prior) if case == "e" else before[1]
    links = _links(uow, row)
    port.fail = case in ("a", "d", "e")
    replace, state = _failing_replace({"b": 2, "c": 4}.get(case, 0))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(capture_module.os, "replace", replace)
        for attempt in ("first", "second"):
            state["calls"] = 0
            names, logs, exc = _scan(service)
            where = f"({case}) {attempt} failing scan"
            assert exc is None, f"{where}: the list raised {type(exc).__name__}"
            assert names == ["a.png"], f"{where}: listed {names}"
            if case == "e":
                assert _read(row.annotated_path) == old_copy, f"{where}: copy not restored"
                assert _files(row)[::2] == before[::2], f"{where}: a file changed"
            else:
                assert _files(row) == before, f"{where}: a file changed"
            assert _links(uow, row) == links, f"{where}: the row lost a link"
            assert _rebake_files(inbox) == [], f"{where}: {_rebake_files(inbox)} left"
            if attempt == "first":
                _one_warning(logs, where)
            else:
                assert _stale(logs) == [], f"{where}: the same failure logged again"
    port.fail = False
    port.calls.clear()
    _names, _logs, exc = _scan(service)
    assert exc is None, f"({case}) working scan raised {type(exc).__name__}"
    assert len(port.calls) == 1, f"({case}) working scan made {len(port.calls)} bake calls"
    assert _read(row.annotated_path) == port.written["a.png"]
    if case == "d":
        assert port.calls[0][3] == "png", f"(d) the bake was given {port.calls[0][3]}"
        assert row.annotated_path.name == "a.annotated.png"
        assert not (inbox / "a.annotated.jpg").exists(), "(d) a .jpg copy was written"
    port.calls.clear()
    _names, _logs, exc = _scan(service)
    assert exc is None and port.calls == [], f"({case}) the scan after baked again"


def _locked_prior(root: Path, case: str, variant: str) -> None:
    """Cases (f) and (g) of AC-146.26: a `.rebake-prior` the scan cannot remove or restore.

    (f) leaves a read-only prior beside a published copy whose key matches; `variant` is
    `chmod` (a real read-only attribute, WinError 5 on Windows) or `patch` (`os.unlink`
    raises `PermissionError` for that prior only). (g) moves the live copy to its prior and
    fakes a lock with an `os.replace` that raises `PermissionError` for that prior only.
    A second shot, b.png, is stale in both, and the same scans must rebake it.
    """
    from avkit_core.services import capture as capture_module

    port = _shown_port()
    service, uow, inbox = _stack_with(root, port)
    row = _annotated(service, uow, port, inbox, "a.png", 6 if case == "f" else None)
    other = _annotated(service, uow, port, inbox, "b.png", None)
    port.tags.update({"a.png": 6, "b.png": 6})
    prior = row.annotated_path.with_name(f".{row.annotated_path.name}.rebake-prior")
    if case == "f":
        prior.write_bytes(b"an older copy")
    else:
        os.replace(row.annotated_path, prior)
    kept = (_read(row.annotated_path), _read(prior), _marks_of(row.sidecar_path))
    links = _links(uow, row)
    real_unlink, real_replace = os.unlink, os.replace

    def unlink(path: Any, *args: Any, **kwargs: Any) -> None:
        if Path(os.fspath(path)).name == prior.name:
            raise PermissionError(f"{path} {MARK} is read-only")
        real_unlink(path, *args, **kwargs)

    def replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
        if Path(os.fspath(src)).name == prior.name:
            raise PermissionError(f"{src} {MARK} is locked")
        real_replace(src, dst, *args, **kwargs)

    where = f"({case}, {variant})"
    try:
        with pytest.MonkeyPatch.context() as patch:
            if variant == "chmod":
                os.chmod(prior, stat.S_IREAD)
            elif case == "f":
                patch.setattr(capture_module.os, "unlink", unlink)
            else:
                patch.setattr(capture_module.os, "replace", replace)
            for attempt in ("first", "second"):
                port.calls.clear()
                names, logs, exc = _scan(service)
                at = f"{where} {attempt} locked scan"
                assert exc is None, f"{at}: the list raised {type(exc).__name__}"
                assert names == ["a.png", "b.png"], f"{at}: listed {names}"
                assert _links(uow, row) == links and None not in links, f"{at}: a link changed"
                now = (_read(row.annotated_path), _read(prior), _marks_of(row.sidecar_path))
                assert now == kept, f"{at}: the copy, the prior or the marks changed"
                assert _bakes_for(port, "a.png") == [], f"{at}: the locked shot was baked"
                want_other = 1 if attempt == "first" else 0
                assert len(_bakes_for(port, "b.png")) == want_other, f"{at}: b.png bakes"
                assert _rebake_files(inbox) == [prior.name], f"{at}: {_rebake_files(inbox)}"
                if attempt == "first":
                    _one_warning(logs, at)
                else:
                    assert _stale(logs) == [], f"{at}: the same failure logged again"
    finally:
        if prior.exists():
            os.chmod(prior, stat.S_IREAD | stat.S_IWRITE)
    assert other.annotated_path.is_file()
    port.calls.clear()
    _names, _logs, exc = _scan(service)
    assert exc is None, f"{where} unlocked scan raised {type(exc).__name__}"
    assert _rebake_files(inbox) == [], f"{where}: {_rebake_files(inbox)} left once unlocked"
    if case == "f":
        assert port.calls == [], f"{where}: the unlocked scan baked"
    else:
        assert len(_bakes_for(port, "a.png")) == 1, f"{where}: the restored copy was not rebaked"
        assert _read(row.annotated_path) == port.written["a.png"]
        port.calls.clear()
        _names, _logs, exc = _scan(service)
        assert exc is None and port.calls == [], f"{where}: the scan after baked again"


@_ac146(26)
@pytest.mark.unit
def test_ac_146_26_failed_rebake_loses_nothing_and_logs_once(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.26"
    root = tmp_path / f"{MARK}-root"
    for case in ("a", "b", "c", "d", "e"):
        _rebake_fails(root / case, case)
    # A read-only attribute stops an unlink only on Windows; the patch runs everywhere.
    variants = ("chmod", "patch") if sys.platform == "win32" else ("patch",)
    for variant in variants:
        _locked_prior(root / f"f-{variant}", "f", variant)
    _locked_prior(root / "g", "g", "patch")
