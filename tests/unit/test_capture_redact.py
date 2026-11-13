"""MEU-103 capture redact mark, domain to bake (Session 68). AC-103.1 to .6, .8 and .10.

Imports stay inside tests so collection cannot ERROR. A call that the Red tree cannot make yet
goes through `_attempt`, so the Red reason is an assertion on its result, never a bare
exception (Session 62 RULE-3). Every image is generated under tmp_path; nothing reaches the
network.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

BLACK = "#000000"
REDACT_FIELDS = ("x", "y", "width", "height", "color")
# The input matrix (implementation-plan.md MEU-103): every colour the domain refuses.
BAD_COLORS = (
    ("empty", ""),
    ("short-hex", "#000"),
    ("trailing-space", "#000000 "),
    ("nul", "\x00"),
    ("escape", "\x1b[31m"),
    ("newline", "#000000\n"),
    ("lone-surrogate", "\ud800"),
    ("not-str", 5),
)
GOOD_COLORS = ("#FF0000", "#ff0000", "red", BLACK)


def _attempt(fn: Callable[..., Any], *args: Any) -> tuple[Any, BaseException | None]:
    """Call `fn`; return (result, None) or (None, the exception) so the test asserts on it."""
    try:
        return fn(*args), None
    except Exception as exc:  # noqa: BLE001 - the test asserts on the type it gets
        return None, exc


def _ac(n: int):
    label = f"AC-103.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _redact_cls() -> Any:
    from avkit_core.domain import capture

    assert hasattr(capture, "RedactAnnotation")
    return capture.RedactAnnotation


# ------------------------------------------------------------ AC-103.1 type


@_ac(1)
@pytest.mark.unit
def test_ac_103_1_redact_fields_default_and_enum(ac_id: str) -> None:
    assert ac_id == "AC-103.1"
    from dataclasses import fields

    from avkit_core.domain.enums import AnnotationType

    redact = _redact_cls()
    assert tuple(field.name for field in fields(redact)) == REDACT_FIELDS
    mark = redact(x=1, y=2, width=3, height=4)
    assert mark.color == BLACK
    assert AnnotationType.Redact.value == "Redact"
    assert AnnotationType.Redact.to_wire() == "redact"
    members = [member.name for member in AnnotationType]
    assert members[members.index("Eraser") + 1] == "Redact"


# ------------------------------------------------------------ AC-103.2 validation

BAD_NUMBERS = (
    ("neg-width", {"width": -1}),
    ("neg-height", {"height": -1}),
    ("float-x", {"x": 1.5}),
    ("str-y", {"y": "1"}),
    ("bool-width", {"width": True}),
)


@pytest.mark.parametrize(
    ("case", "change"),
    [(name, change) for name, change in BAD_NUMBERS]
    + [(f"color-{name}", {"color": value}) for name, value in BAD_COLORS],
    ids=[name for name, _ in BAD_NUMBERS] + [f"color-{name}" for name, _ in BAD_COLORS],
)
@pytest.mark.unit
def test_ac_103_2_redact_refuses_bad_value(case: str, change: dict[str, Any]) -> None:
    from avkit_core.domain.errors import AnnotationValidationError

    redact = _redact_cls()
    values: dict[str, Any] = {"x": 0, "y": 0, "width": 4, "height": 4, **change}
    with pytest.raises(AnnotationValidationError) as caught:
        redact(**values)
    assert caught.type is AnnotationValidationError, case


@pytest.mark.parametrize("color", GOOD_COLORS, ids=list(GOOD_COLORS))
@pytest.mark.unit
def test_ac_103_2_redact_keeps_good_color(color: str) -> None:
    redact = _redact_cls()
    mark = redact(x=-3, y=4, width=0, height=7, color=color)
    assert (mark.x, mark.y, mark.width, mark.height, mark.color) == (-3, 4, 0, 7, color)


# ------------------------------------------------------------ AC-103.3 union order


@_ac(3)
@pytest.mark.unit
def test_ac_103_3_union_ends_pixelate_eraser_redact(ac_id: str) -> None:
    assert ac_id == "AC-103.3"
    from typing import get_args

    from avkit_core.domain.capture import Annotation, EraserAnnotation, PixelateAnnotation

    redact = _redact_cls()
    members = get_args(Annotation)
    assert len(members) >= 3
    assert members[-3:] == (PixelateAnnotation, EraserAnnotation, redact)


# ------------------------------------------------------------ AC-103.4 sidecar wire

WIRE = {"type": "redact", "x": 3, "y": 4, "width": 10, "height": 6, "color": "#FF0000"}
WIRE_REFUSED = (
    ("missing-color", {k: v for k, v in WIRE.items() if k != "color"}),
    ("missing-height", {k: v for k, v in WIRE.items() if k != "height"}),
    ("extra-block-size", {**WIRE, "block_size": 10}),
    ("extra-note", {**WIRE, "note": 1}),
    ("bad-color", {**WIRE, "color": "#000"}),
    ("neg-width", {**WIRE, "width": -1}),
    ("float-x", {**WIRE, "x": 1.5}),
)


def _wire_mark() -> Any:
    return _redact_cls()(x=3, y=4, width=10, height=6, color="#FF0000")


@_ac(4)
@pytest.mark.unit
def test_ac_103_4_redact_wire_round_trip(ac_id: str) -> None:
    assert ac_id == "AC-103.4"
    from avkit_core.services.capture import _annotation_from_wire, _annotation_to_wire

    mark = _wire_mark()
    wire, error = _attempt(_annotation_to_wire, mark)
    assert error is None, repr(error)
    assert wire == WIRE
    back, error = _attempt(_annotation_from_wire, WIRE)
    assert error is None, repr(error)
    assert back == mark


@pytest.mark.parametrize(("case", "item"), WIRE_REFUSED, ids=[n for n, _ in WIRE_REFUSED])
@pytest.mark.unit
def test_ac_103_4_sidecar_refuses_bad_redact(case: str, item: dict[str, Any]) -> None:
    from avkit_core.domain.errors import AnnotationValidationError
    from avkit_core.services.capture import annotations_from_sidecar

    # The good entry reads first, so the refusal below is the redact rule, not an unknown type.
    good, error = _attempt(annotations_from_sidecar, {"version": 1, "annotations": [WIRE]})
    assert error is None, repr(error)
    assert good == [_wire_mark()]
    with pytest.raises(AnnotationValidationError) as caught:
        annotations_from_sidecar({"version": 1, "annotations": [item]})
    assert caught.type is AnnotationValidationError, case


@_ac(4)
@pytest.mark.unit
def test_ac_103_4_sidecar_without_redact_keeps_bytes(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-103.4"
    from tests.unit.test_capture_service import _stack, _write_inbox_file

    from avkit_core.domain.capture import EraserAnnotation, PixelateAnnotation, RectAnnotation
    from avkit_core.domain.enums import CaptureSource

    service, _uow, _port, inbox = _stack(tmp_path)
    shot = service.register_shot(_write_inbox_file(inbox, "plain.png"), CaptureSource.Gui)
    marks = [
        RectAnnotation(x=1, y=2, width=5, height=6, color="red", stroke_width=2),
        PixelateAnnotation(x=3, y=4, width=8, height=8, block_size=4),
        EraserAnnotation(x=0, y=0, width=4, height=4),
    ]
    saved = service.annotate_and_save(shot.id, marks)
    assert saved.sidecar_path is not None
    first = saved.sidecar_path.read_bytes()
    again = service.annotate_and_save(shot.id, service.load_shot_annotations(shot.id))
    assert again.sidecar_path is not None
    assert again.sidecar_path.read_bytes() == first
    assert b"redact" not in first


# ------------------------------------------------------------ AC-103.5 clamp


@_ac(5)
@pytest.mark.unit
def test_ac_103_5_redact_clamps_like_a_pixelate(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-103.5"
    from tests.unit.test_capture_service import _stack

    from avkit_core.domain.capture import PixelateAnnotation

    redact = _redact_cls()
    service, _uow, _port, _inbox = _stack(tmp_path)
    width, height = 32, 24
    # One box past each edge, and one inside.
    for x, y in ((-5, 3), (4, -6), (40, 3), (4, 30), (-9, -9), (50, 50), (6, 7)):
        mark = redact(x=x, y=y, width=9, height=5, color="#12AB34")
        pixelate = PixelateAnnotation(x=x, y=y, width=9, height=5, block_size=4)
        out, error = _attempt(service._clamp_annotation, mark, width, height)
        assert error is None, repr(error)
        expected = service._clamp_annotation(pixelate, width, height)
        assert isinstance(out, redact)
        assert (out.x, out.y, out.width, out.height) == (
            expected.x,
            expected.y,
            expected.width,
            expected.height,
        )
        assert out.color == "#12AB34"
        assert service._clamp_annotation(out, width, height) == out


# ------------------------------------------------------------ AC-103.6 crop clip

CLIP_CROP = (100, 50, 200, 100)
# id, box in the crop's frame (the source box is this plus the crop's origin)
CLIP_CASES = (
    ("inside", (30, 30, 50, 30)),
    ("left", (-20, 10, 50, 30)),
    ("top", (10, -20, 30, 50)),
    ("right", (180, 10, 40, 30)),
    ("bottom", (10, 80, 30, 40)),
    ("corner", (-10, -10, 230, 130)),
    ("whole-crop", (0, 0, 200, 100)),
    ("outside", (250, 10, 20, 20)),
    ("touch-right", (200, 10, 20, 20)),
    ("touch-left", (-20, 10, 20, 20)),
    ("w0-in", (50, 20, 0, 30)),
    ("w0-out", (-5, 20, 0, 30)),
    ("h0-in", (50, 20, 30, 0)),
    ("h0-out", (50, 100, 30, 0)),
)


def _half_open_oracle(
    box: tuple[int, int, int, int], width: int, height: int
) -> tuple[tuple[int, int, int, int] | None, str]:
    """MARK_CLIP_BOX restated: `[x, x+w) x [y, y+h)` against `[0, width) x [0, height)`."""
    x0, y0, w, h = box
    if w == 0 or h == 0:
        inside = 0 <= x0 < width and 0 <= y0 < height
        return ((x0, y0, w, h), "kept") if inside else (None, "dropped")
    x1, y1 = x0 + w, y0 + h
    cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, width), min(y1, height)
    if cx0 >= cx1 or cy0 >= cy1:
        return None, "dropped"
    clipped = (cx0, cy0, cx1 - cx0, cy1 - cy0)
    return clipped, "kept" if clipped == box else "clipped"


def _closed_clip(box: tuple[int, int, int, int], width: int, height: int) -> object:
    """A closed-box clip (`[x, x+w] x [y, y+h]`), the rect rule, for the negative check."""
    x0, y0, w, h = box
    cx0, cy0 = max(x0, 0), max(y0, 0)
    cx1, cy1 = min(x0 + w, width - 1), min(y0 + h, height - 1)
    if cx0 > cx1 or cy0 > cy1:
        return None
    return (cx0, cy0, cx1 - cx0, cy1 - cy0)


@pytest.mark.parametrize(("case", "box"), CLIP_CASES, ids=[name for name, _ in CLIP_CASES])
@pytest.mark.unit
def test_ac_103_6_redact_clip_matches_oracle(
    case: str, box: tuple[int, int, int, int], tmp_path: Path
) -> None:
    from tests.unit.test_capture_service import _stack

    from avkit_core.domain.capture import clip_mark

    redact = _redact_cls()
    left, top, width, height = CLIP_CROP
    mark = redact(x=box[0] + left, y=box[1] + top, width=box[2], height=box[3], color="red")
    result, error = _attempt(clip_mark, mark, left, top, width, height)
    assert error is None, f"{case}: {error!r}"
    out, carry = result
    expected, expected_carry = _half_open_oracle(box, width, height)
    assert carry == expected_carry, case
    if expected is None:
        assert out is None, case
        return
    assert isinstance(out, redact), case
    assert (out.x, out.y, out.width, out.height) == expected, case
    assert out.color == "red"
    service, _uow, _port, _inbox = _stack(tmp_path)
    assert service._clamp_annotation(out, width, height) == out, case


@_ac(6)
@pytest.mark.unit
def test_ac_103_6_oracle_is_not_a_closed_clip(ac_id: str) -> None:
    assert ac_id == "AC-103.6"
    _left, _top, width, height = CLIP_CROP
    differ = [
        name
        for name, box in CLIP_CASES
        if box[2] and box[3] and _half_open_oracle(box, width, height)[0] != _closed_clip(
            box, width, height
        )
    ]
    assert {"right", "bottom", "corner", "whole-crop", "touch-left"} <= set(differ)


# ------------------------------------------------------------ AC-103.8 bake

BAKE_SIZE = (40, 30)


def _gradient_rgba() -> Any:
    from PIL import Image

    width, height = BAKE_SIZE
    image = Image.new("RGBA", BAKE_SIZE)
    image.putdata(
        [
            (x * 6 % 256, y * 8 % 256, (x + y) * 3 % 256, 128 if (x + y) % 5 == 0 else 255)
            for y in range(height)
            for x in range(width)
        ]
    )
    return image


@_ac(8)
@pytest.mark.unit
def test_ac_103_8_region_pass_fills_the_redact_box(ac_id: str) -> None:
    assert ac_id == "AC-103.8"
    from avkit_infra.capture.adapter import apply_region_pass, region_clip

    redact = _redact_cls()
    width, height = BAKE_SIZE
    source = _gradient_rgba()
    for mark in (
        redact(x=5, y=4, width=12, height=9, color="#12AB34"),
        redact(x=-3, y=-2, width=10, height=8, color="blue"),
        redact(x=33, y=25, width=20, height=20),
    ):
        box = region_clip(mark, width, height)
        assert box is not None
        rgb = {"#12AB34": (0x12, 0xAB, 0x34), "blue": (0, 0, 255), BLACK: (0, 0, 0)}[mark.color]
        got = apply_region_pass(source.copy(), [mark])
        x0, y0, x1, y1 = box
        inside = [(x, y) for y in range(y0, y1) for x in range(x0, x1)]
        assert inside
        assert any(source.getpixel(p)[3] == 128 for p in inside)
        for point in inside:
            assert got.getpixel(point) == (*rgb, 255), (mark, point)
        for y in range(height):
            for x in range(width):
                if not (x0 <= x < x1 and y0 <= y < y1):
                    assert got.getpixel((x, y)) == source.getpixel((x, y)), (mark, x, y)


@_ac(8)
@pytest.mark.unit
def test_ac_103_8_region_marks_apply_in_list_order(ac_id: str) -> None:
    assert ac_id == "AC-103.8"
    from avkit_core.domain.capture import PixelateAnnotation
    from avkit_infra.capture.adapter import apply_region_pass

    redact = _redact_cls()
    source = _gradient_rgba()
    solid = redact(x=4, y=4, width=16, height=12, color="#FF0000")
    pixelate = PixelateAnnotation(x=0, y=0, width=24, height=20, block_size=8)
    over = apply_region_pass(source.copy(), [pixelate, solid])
    for y in range(4, 16):
        for x in range(4, 20):
            assert over.getpixel((x, y)) == (255, 0, 0, 255), ("redact over pixelate", x, y)
    under = apply_region_pass(source.copy(), [solid, pixelate])
    stepwise = apply_region_pass(apply_region_pass(source.copy(), [solid]), [pixelate])
    assert under.tobytes() == stepwise.tobytes()
    assert under.tobytes() != over.tobytes()
    assert under.tobytes() != apply_region_pass(source.copy(), [pixelate]).tobytes()


@_ac(8)
@pytest.mark.unit
def test_ac_103_8_bake_draws_the_arrow_over_a_redact(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-103.8"
    from PIL import Image

    from avkit_core.domain.capture import ArrowAnnotation
    from avkit_infra.capture.adapter import CaptureAdapter, apply_region_pass

    redact = _redact_cls()
    source = _gradient_rgba().convert("RGB")
    path = tmp_path / "shot.png"
    source.save(path, format="PNG")
    solid = redact(x=0, y=0, width=40, height=30, color="#00FF00")
    probe = apply_region_pass(source.convert("RGBA"), [solid])
    assert probe.getpixel((20, 15)) == (0, 255, 0, 255)
    arrow = ArrowAnnotation(from_xy=(2, 15), to_xy=(36, 15), color="red", stroke_width=3)
    out = tmp_path / "shot.annotated.png"
    # The arrow is listed first, but the region pass runs before every drawn mark.
    _probe, error = _attempt(CaptureAdapter().bake, path, [arrow, solid], out)
    assert error is None, repr(error)
    with Image.open(out) as baked:
        rgb = baked.convert("RGB")
        assert rgb.getpixel((20, 15))[0] > 200 and rgb.getpixel((20, 15))[1] < 80
        assert rgb.getpixel((20, 2)) == (0, 255, 0)
        # REDACT_OUTLINE: no outline in the bake; the box reaches the image edge untouched.
        assert rgb.getpixel((0, 0)) == (0, 255, 0)
        assert rgb.getpixel((39, 29)) == (0, 255, 0)


# ------------------------------------------------------------ AC-103.10 trace


@_ac(10)
@pytest.mark.unit
def test_ac_103_10_redact_traced_api_to_pixels(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-103.10"
    from PIL import Image
    from tests.e2e.test_api_capture_crop import (
        AUTH,
        PREFIX,
        _annotated_of,
        _inbox,
        _rgb,
        _shot_id,
        _stack,
    )

    from avkit_core.services import capture as service_mod
    from avkit_infra.capture import adapter as adapter_mod

    redact = _redact_cls()
    assert hasattr(adapter_mod, "apply_region_pass")
    assert hasattr(service_mod, "_annotation_from_wire")
    baked: list[list[object]] = []
    read: list[object] = []
    real_pass = adapter_mod.apply_region_pass
    real_read = service_mod._annotation_from_wire

    def recording_pass(canvas: Any, marks: Any) -> Any:
        baked.append(list(marks))
        return real_pass(canvas, marks)

    def recording_read(item: object) -> Any:
        out = real_read(item)
        read.append(out)
        return out

    monkeypatch.setattr(adapter_mod, "apply_region_pass", recording_pass)
    monkeypatch.setattr(service_mod, "_annotation_from_wire", recording_read)

    inbox = _inbox(tmp_path)
    Image.new("RGB", (64, 48), (200, 210, 220)).save(inbox / "shot.png")
    body = {"type": "redact", "x": -4, "y": 5, "width": 20, "height": 10}
    stored = {**body, "x": 0, "color": BLACK}
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        saved = client.post(
            f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": [body]}
        )
        assert saved.status_code == 200, saved.text
        sidecar = Path(saved.json()["sidecar_path"])
        assert json.loads(sidecar.read_text(encoding="utf-8"))["annotations"] == [stored]
        detail = client.get(f"{PREFIX}/{shot_id}", headers=AUTH)
        assert detail.status_code == 200, detail.text
        assert detail.json()["annotations"] == [stored]
        annotated = _rgb(_annotated_of(client, "shot.png"))
    clamped = redact(x=0, y=5, width=20, height=10, color=BLACK)
    assert len(baked) == 1
    assert [mark for mark in baked[0] if isinstance(mark, redact)] == [clamped]
    assert clamped in read
    assert {annotated.getpixel((x, y)) for x in range(0, 20) for y in range(5, 15)} == {(0, 0, 0)}
    assert annotated.getpixel((20, 5)) == (200, 210, 220)
    assert annotated.getpixel((0, 15)) == (200, 210, 220)
