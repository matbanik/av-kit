"""MEU-106 capture line and ellipse shapes (Session 72): AC-106.1 to .4, .8, .11, .15, .16, .34
and the Python half of the guard AC-106.30.

Every check works on in-memory values, on images generated under tmp_path or on scratch
copies; nothing reads user data.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN = REPO_ROOT / "docs/execution/plans/2026-11-14-capture-shapes-steps"
GEOMETRY = REPO_ROOT / "ui/tests/e2e/fixtures/capture-geometry.json"
WHITE = (255, 255, 255)
# The base bakes (row 0, C:/Temp/av-kit/s72-base-bakes.txt): SHA-256 of the RGB bytes of
# CaptureAdapter(platform="win32").render on a white image, at 5db3623.
END_ARROW_SHA = "af685c76ffcd76beed861e6cd79175d1222b97fa0fb9ebcd27064518661ba3fe"
RECT_SHA = "9ce84cf453ac76c5407e9a1a3d40e368ee42e8e1a9de784f473bed70c02a89fd"
ARROW_ARGS: dict[str, Any] = {
    "from_xy": (10, 30),
    "to_xy": (110, 30),
    "color": "#FF0000",
    "stroke_width": 3,
}
RECT_ARGS: dict[str, Any] = {
    "x": 10,
    "y": 10,
    "width": 60,
    "height": 40,
    "color": "#FF0000",
    "stroke_width": 3,
}
# The input matrix (implementation-plan.md MEU-106): each refused head and shape value.
BAD_HEADS: dict[str, object] = {
    "empty": "",
    "bell": "\x07",
    "surrogate": "\ud800",
    "End": "End",
    "int": 1,
    "None": None,
}
BAD_SHAPES: dict[str, object] = {
    "empty": "",
    "bell": "\x07",
    "surrogate": "\ud800",
    "Ellipse": "Ellipse",
    "int": 1,
    "None": None,
}
# A crop (left, top, width, height) of 40 x 30, as the plan's matrices give it.
CROP = (10, 20, 40, 30)
# The sidecar 5db3623 writes for one arrow and one rect (json.dumps, default separators).
BASE_SIDECAR = (
    b'{"version": 1, "annotations": [{"type": "arrow", "from": [10, 30], "to": [110, 30], '
    b'"color": "#FF0000", "stroke_width": 3}, {"type": "rect", "x": 10, "y": 10, "width": 60, '
    b'"height": 40, "color": "#FF0000", "stroke_width": 3}]}'
)


def _ac(n: int):
    label = f"AC-106.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


# ------------------------------------------------------------ AC-106.1 signatures


@_ac(1)
def test_ac_106_1_head_and_shape_literals(ac_id: str) -> None:
    assert ac_id == "AC-106.1"
    from dataclasses import fields
    from typing import get_args

    from avkit_core.domain import capture

    assert get_args(capture.ArrowHead) == ("end", "none", "both")
    assert get_args(capture.BoxShape) == ("rect", "ellipse")
    arrow = fields(capture.ArrowAnnotation)
    assert [f.name for f in arrow] == ["from_xy", "to_xy", "color", "stroke_width", "head"]
    assert arrow[-1].default == "end"
    box = fields(capture.RectAnnotation)
    assert [f.name for f in box] == ["x", "y", "width", "height", "color", "stroke_width", "shape"]
    assert box[-1].default == "rect"


@_ac(1)
def test_ac_106_1_clip_ellipse_and_shaft_span_signatures(ac_id: str) -> None:
    assert ac_id == "AC-106.1"
    import inspect
    from typing import get_type_hints

    from avkit_core.domain import capture
    from avkit_infra.capture import adapter

    clip = inspect.signature(capture._clip_ellipse)
    assert list(clip.parameters) == ["mark", "left", "top", "width", "height"]
    hints = get_type_hints(capture._clip_ellipse)
    assert hints["mark"] is capture.RectAnnotation
    assert [hints[name] for name in ("left", "top", "width", "height")] == [int] * 4
    assert hints["return"] == tuple[capture.RectAnnotation | None, capture.MarkCarry]
    span = inspect.signature(adapter.arrow_shaft_span)
    assert list(span.parameters) == ["from_xy", "to_xy", "stroke", "head"]
    span_hints = get_type_hints(adapter.arrow_shaft_span)
    assert span_hints["stroke"] is int
    assert span_hints["head"] == capture.ArrowHead
    point = tuple[float, float]
    assert span_hints["return"] == tuple[point, point] | None


# ------------------------------------------------------------ helpers


def _caught(build: Any) -> BaseException | None:
    try:
        build()
    except Exception as exc:  # the type is asserted by the caller
        return exc
    return None


def _echoes(value: object, message: str) -> bool:
    """Whether `message` shows `value` (Session 53 RULE-1); an empty string is looked for quoted."""
    if value == "":
        return "''" in message or '""' in message
    if isinstance(value, str) and not value.isprintable():
        return value in message or ascii(value)[1:-1] in message
    text = value if isinstance(value, str) else repr(value)
    return re.search(rf"(?<![\w.-]){re.escape(text)}(?![\w.])", message) is not None


def _render(tmp_path: Path, size: tuple[int, int], marks: list[Any]) -> Any:
    """The adapter's RENDER_BAKE of `marks` on a white image, decoded to RGB."""
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    source = tmp_path / "white.png"
    Image.new("RGB", size, WHITE).save(source)
    png = CaptureAdapter(platform="win32").render(source, marks)
    with Image.open(io.BytesIO(png)) as opened:
        return opened.convert("RGB")


def _sha(image: Any) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _ink(pixel: tuple[int, ...]) -> bool:
    return pixel[0] > 200 and pixel[1] < 160 and pixel[2] < 160


def _white(pixel: tuple[int, ...]) -> bool:
    return min(pixel[:3]) > 240


def _arrow_both() -> list[dict[str, Any]]:
    entries = json.loads(GEOMETRY.read_bytes())["arrow_both"]
    assert len(entries) == 3
    return entries


# ------------------------------------------------------------ AC-106.2 HEAD_FIELD


@_ac(2)
def test_ac_106_2_head_defaults_to_end_and_takes_none_and_both(ac_id: str) -> None:
    assert ac_id == "AC-106.2"
    from avkit_core.domain.capture import ArrowAnnotation

    assert ArrowAnnotation(**ARROW_ARGS).head == "end"
    assert ArrowAnnotation(**ARROW_ARGS, head="none").head == "none"
    assert ArrowAnnotation(**ARROW_ARGS, head="both").head == "both"


@pytest.mark.parametrize("case", list(BAD_HEADS), ids=[f"AC-106.2-{c}" for c in BAD_HEADS])
def test_ac_106_2_arrow_refuses_a_bad_head(case: str) -> None:
    from avkit_core.domain.capture import ArrowAnnotation
    from avkit_core.domain.errors import AnnotationValidationError

    value = BAD_HEADS[case]
    caught = _caught(lambda: ArrowAnnotation(**ARROW_ARGS, head=value))
    assert isinstance(caught, AnnotationValidationError), f"{case}: {caught!r}"
    message = str(caught)
    assert re.search(r"\bhead\b", message), ascii(message)
    assert not _echoes(value, message), ascii(message)


# ------------------------------------------------------------ AC-106.3 SHAPE_FIELD


@_ac(3)
def test_ac_106_3_shape_defaults_to_rect_and_takes_ellipse(ac_id: str) -> None:
    assert ac_id == "AC-106.3"
    from avkit_core.domain.capture import HighlightAnnotation, RectAnnotation

    assert RectAnnotation(**RECT_ARGS).shape == "rect"
    assert RectAnnotation(**RECT_ARGS, shape="ellipse").shape == "ellipse"
    box = {"x": 1, "y": 2, "width": 3, "height": 4, "color": "#FF0000", "opacity": 0.5}
    caught = _caught(lambda: HighlightAnnotation(**box, shape="ellipse"))  # type: ignore[call-arg]
    assert isinstance(caught, TypeError), repr(caught)


@pytest.mark.parametrize("case", list(BAD_SHAPES), ids=[f"AC-106.3-{c}" for c in BAD_SHAPES])
def test_ac_106_3_rect_refuses_a_bad_shape(case: str) -> None:
    from avkit_core.domain.capture import RectAnnotation
    from avkit_core.domain.errors import AnnotationValidationError

    value = BAD_SHAPES[case]
    caught = _caught(lambda: RectAnnotation(**RECT_ARGS, shape=value))
    assert isinstance(caught, AnnotationValidationError), f"{case}: {caught!r}"
    message = str(caught)
    assert re.search(r"\bshape\b", message), ascii(message)
    assert not _echoes(value, message), ascii(message)


# ------------------------------------------------------------ AC-106.4 DEFAULT_OMIT


@_ac(4)
def test_ac_106_4_default_marks_write_no_head_or_shape(ac_id: str) -> None:
    assert ac_id == "AC-106.4"
    from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation
    from avkit_core.services.capture import _annotation_to_wire

    assert "head" not in _annotation_to_wire(ArrowAnnotation(**ARROW_ARGS))
    assert "shape" not in _annotation_to_wire(RectAnnotation(**RECT_ARGS))


@_ac(4)
def test_ac_106_4_other_values_are_written(ac_id: str) -> None:
    assert ac_id == "AC-106.4"
    from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation
    from avkit_core.services.capture import _annotation_to_wire

    assert _annotation_to_wire(ArrowAnnotation(**ARROW_ARGS, head="none")).get("head") == "none"
    assert _annotation_to_wire(ArrowAnnotation(**ARROW_ARGS, head="both")).get("head") == "both"
    ellipse = RectAnnotation(**RECT_ARGS, shape="ellipse")
    assert _annotation_to_wire(ellipse).get("shape") == "ellipse"


@_ac(4)
def test_ac_106_4_wire_reads_missing_default_and_set_values(ac_id: str) -> None:
    assert ac_id == "AC-106.4"
    from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation
    from avkit_core.services.capture import _annotation_from_wire, _annotation_to_wire

    arrow = _annotation_to_wire(ArrowAnnotation(**ARROW_ARGS))
    rect = _annotation_to_wire(RectAnnotation(**RECT_ARGS))
    assert _annotation_from_wire(arrow) == ArrowAnnotation(**ARROW_ARGS)
    assert _annotation_from_wire({**arrow, "head": "end"}) == ArrowAnnotation(**ARROW_ARGS)
    assert _annotation_from_wire(rect) == RectAnnotation(**RECT_ARGS)
    assert _annotation_from_wire({**rect, "shape": "rect"}) == RectAnnotation(**RECT_ARGS)
    none = _annotation_from_wire({**arrow, "head": "none"})
    assert none == ArrowAnnotation(**ARROW_ARGS, head="none")
    ellipse = _annotation_from_wire({**rect, "shape": "ellipse"})
    assert ellipse == RectAnnotation(**RECT_ARGS, shape="ellipse")


WIRE_REFUSALS = [
    (f"{field}-{name}", field, value)
    for field in ("head", "shape")
    for name, value in (("x", "x"), ("empty", ""), ("null", None))
]


@pytest.mark.parametrize(
    ("case", "field", "value"),
    WIRE_REFUSALS,
    ids=[f"AC-106.4-{case}" for case, _f, _v in WIRE_REFUSALS],
)
def test_ac_106_4_wire_refuses_a_bad_value(case: str, field: str, value: object) -> None:
    from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation
    from avkit_core.domain.errors import AnnotationValidationError
    from avkit_core.services.capture import _annotation_from_wire, _annotation_to_wire

    mark = ArrowAnnotation(**ARROW_ARGS) if field == "head" else RectAnnotation(**RECT_ARGS)
    item = {**_annotation_to_wire(mark), field: value}
    caught = _caught(lambda: _annotation_from_wire(item))
    assert isinstance(caught, AnnotationValidationError), f"{case}: {caught!r}"


@_ac(4)
def test_ac_106_4_base_sidecar_round_trips_byte_for_byte(ac_id: str) -> None:
    assert ac_id == "AC-106.4"
    from avkit_core.services.capture import (
        SIDECAR_VERSION,
        _annotation_from_wire,
        _annotation_to_wire,
    )

    document = json.loads(BASE_SIDECAR)
    marks = [_annotation_from_wire(item) for item in document["annotations"]]
    assert SIDECAR_VERSION == document["version"] == 1
    again = json.dumps(
        {"version": SIDECAR_VERSION, "annotations": [_annotation_to_wire(m) for m in marks]}
    )
    assert again.encode("utf-8") == BASE_SIDECAR


# ------------------------------------------------------------ AC-106.8 HEAD_BAKE


@_ac(8)
def test_ac_106_8_end_head_bakes_the_base_bytes(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.8"
    from avkit_core.domain.capture import ArrowAnnotation

    image = _render(tmp_path, (120, 60), [ArrowAnnotation(**ARROW_ARGS, head="end")])
    assert _sha(image) == END_ARROW_SHA


@_ac(8)
def test_ac_106_8_none_head_draws_no_head(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.8"
    from avkit_core.domain.capture import ArrowAnnotation

    image = _render(tmp_path, (120, 60), [ArrowAnnotation(**ARROW_ARGS, head="none")])
    assert _ink(image.getpixel((108, 30))), image.getpixel((108, 30))
    # Outside the 3 px stroke band (y 28.5 to 31.5) nothing is drawn at either end.
    for point in ((100, 26), (100, 34), (20, 26), (20, 34)):
        assert _white(image.getpixel(point)), (point, image.getpixel(point))


@_ac(8)
def test_ac_106_8_both_heads_draw_at_each_end(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.8"
    from avkit_core.domain.capture import ArrowAnnotation

    image = _render(tmp_path, (120, 60), [ArrowAnnotation(**ARROW_ARGS, head="both")])
    for point in ((20, 26), (20, 34), (100, 26), (100, 34)):
        assert _ink(image.getpixel(point)), (point, image.getpixel(point))


@_ac(8)
def test_ac_106_8_head_vertices_match_the_fixture(ac_id: str) -> None:
    assert ac_id == "AC-106.8"
    from avkit_infra.capture.adapter import arrowhead_vertices

    for entry in _arrow_both():
        start, end, stroke = tuple(entry["from"]), tuple(entry["to"]), entry["stroke"]
        _tip, end_left, end_right = arrowhead_vertices(start, end, stroke)
        _tail, start_left, start_right = arrowhead_vertices(end, start, stroke)
        got = [end_left, end_right, start_left, start_right]
        want = [entry[key] for key in ("end_left", "end_right", "start_left", "start_right")]
        for (gx, gy), (wx, wy) in zip(got, want, strict=True):
            assert abs(gx - wx) <= 1e-9 and abs(gy - wy) <= 1e-9, (entry, got)


@_ac(8)
def test_ac_106_8_both_shaft_span_matches_the_fixture(ac_id: str) -> None:
    assert ac_id == "AC-106.8"
    from avkit_infra.capture.adapter import arrow_shaft_span

    for entry in _arrow_both():
        start, end, stroke = tuple(entry["from"]), tuple(entry["to"]), entry["stroke"]
        span = arrow_shaft_span(start, end, stroke, "both")
        if entry["shaft"] is None:
            assert span is None, (entry["from"], entry["to"], span)
            continue
        assert span is not None, entry
        flat = [span[0][0], span[0][1], span[1][0], span[1][1]]
        want = [entry["shaft"][0][0], entry["shaft"][0][1], entry["shaft"][1][0]]
        want.append(entry["shaft"][1][1])
        assert all(abs(g - w) <= 1e-9 for g, w in zip(flat, want, strict=True)), (entry, span)


@_ac(8)
def test_ac_106_8_short_both_arrow_has_two_heads_and_no_shaft(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.8"
    from avkit_core.domain.capture import ArrowAnnotation
    from avkit_infra.capture.adapter import arrow_shaft_span

    # 20 px long: two heads of 15 px (stroke 3) leave no room for a shaft.
    short = {**ARROW_ARGS, "to_xy": (30, 30)}
    assert arrow_shaft_span((10, 30), (30, 30), 3, "both") is None
    image = _render(tmp_path, (120, 60), [ArrowAnnotation(**short, head="both")])
    # (22, 25) lies in the start head only and (18, 25) in the end head only.
    for point in ((22, 25), (18, 25)):
        assert _ink(image.getpixel(point)), (point, image.getpixel(point))


# ------------------------------------------------------------ AC-106.11 ELLIPSE_BAKE


@_ac(11)
def test_ac_106_11_ellipse_bakes_as_pillow_draws_it(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.11"
    from PIL import Image, ImageDraw

    from avkit_core.domain.capture import RectAnnotation

    image = _render(tmp_path, (80, 60), [RectAnnotation(**RECT_ARGS, shape="ellipse")])
    assert _white(image.getpixel((11, 11))), image.getpixel((11, 11))
    assert _ink(image.getpixel((40, 11))), image.getpixel((40, 11))
    want = Image.new("RGB", (80, 60), WHITE).convert("RGBA")
    ImageDraw.Draw(want).ellipse([10, 10, 70, 50], outline=(255, 0, 0), width=3)
    assert image.tobytes() == want.convert("RGB").tobytes()


# ------------------------------------------------------------ AC-106.15 ELLIPSE_CLIP

# The box in the crop's pixels and the carry (D-676 A: the ellipse is never clipped).
ELLIPSE_CASES: dict[str, tuple[tuple[int, int, int, int], str]] = {
    "inside": ((5, 5, 20, 10), "kept"),
    "touching": ((20, 20, 20, 10), "kept"),
    "straddling": ((30, 5, 20, 10), "dropped"),
    "outside": ((50, 50, 5, 5), "dropped"),
    "one-past": ((21, 20, 20, 10), "dropped"),
}


@pytest.mark.parametrize("case", list(ELLIPSE_CASES), ids=[f"AC-106.15-{c}" for c in ELLIPSE_CASES])
def test_ac_106_15_ellipse_is_kept_or_dropped(case: str) -> None:
    from avkit_core.domain.capture import RectAnnotation, clip_mark

    (x, y, width, height), carry = ELLIPSE_CASES[case]
    left, top = CROP[0], CROP[1]
    mark = RectAnnotation(
        x=x + left,
        y=y + top,
        width=width,
        height=height,
        color="red",
        stroke_width=2,
        shape="ellipse",
    )
    got = clip_mark(mark, *CROP)
    if carry == "kept":
        moved = RectAnnotation(
            x=x, y=y, width=width, height=height, color="red", stroke_width=2, shape="ellipse"
        )
        assert got == (moved, "kept"), (case, got)
    else:
        assert got == (None, "dropped"), (case, got)


@_ac(15)
def test_ac_106_15_rect_with_the_straddling_box_is_clipped(ac_id: str) -> None:
    assert ac_id == "AC-106.15"
    from avkit_core.domain.capture import RectAnnotation, clip_mark

    mark = RectAnnotation(x=40, y=25, width=20, height=10, color="red", stroke_width=2)
    want = RectAnnotation(x=30, y=5, width=9, height=10, color="red", stroke_width=2)
    assert clip_mark(mark, *CROP) == (want, "clipped")


# ------------------------------------------------------------ AC-106.16 HEAD_CLIP (guard)

# In the source's pixels; the crop is CROP. Each gives (from, to) in the crop's pixels.
HEAD_CLIP_CASES: dict[str, tuple[tuple[int, int], tuple[int, int], Any, str]] = {
    "inside": ((15, 25), (40, 40), ((5, 5), (30, 20)), "kept"),
    "straddling": ((15, 25), (80, 40), ((5, 5), (40, 13)), "clipped"),
    "outside": ((60, 60), (80, 70), None, "dropped"),
}
HEAD_CLIP = [(head, case) for head in ("end", "none", "both") for case in HEAD_CLIP_CASES]


@pytest.mark.parametrize(
    ("head", "case"), HEAD_CLIP, ids=[f"AC-106.16-{h}-{c}" for h, c in HEAD_CLIP]
)
def test_ac_106_16_clip_keeps_the_head(head: str, case: str) -> None:
    from avkit_core.domain.capture import ArrowAnnotation, clip_mark

    start, end, moved, carry = HEAD_CLIP_CASES[case]
    mark = ArrowAnnotation(from_xy=start, to_xy=end, color="red", stroke_width=3, head=head)
    got, how = clip_mark(mark, *CROP)
    assert how == carry, (head, case, got)
    if moved is None:
        assert got is None
        return
    assert isinstance(got, ArrowAnnotation)
    assert (got.from_xy, got.to_xy) == moved
    assert got.head == head
    if carry == "clipped":
        assert got.to_xy[0] == CROP[2]  # the moved end lies on the crop's right edge


# ------------------------------------------------------------ AC-106.30 (guard, Python half)


@_ac(30)
def test_ac_106_30_end_arrow_and_rect_bakes_are_unchanged(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.30"
    from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation

    arrow = _render(tmp_path, (120, 60), [ArrowAnnotation(**ARROW_ARGS)])
    assert _sha(arrow) == END_ARROW_SHA
    rect = _render(tmp_path, (80, 60), [RectAnnotation(**RECT_ARGS)])
    assert _sha(rect) == RECT_SHA


@_ac(30)
def test_ac_106_30_rect_clip_is_unchanged(ac_id: str) -> None:
    assert ac_id == "AC-106.30"
    from avkit_core.domain.capture import RectAnnotation, _clip_rect, clip_mark

    def rect(x: int, y: int, width: int, height: int) -> RectAnnotation:
        return RectAnnotation(x=x, y=y, width=width, height=height, color="red", stroke_width=2)

    cases = [
        (rect(15, 25, 20, 10), (rect(5, 5, 20, 10), "kept")),
        (rect(30, 40, 19, 9), (rect(20, 20, 19, 9), "kept")),
        (rect(30, 40, 20, 10), (rect(20, 20, 19, 9), "clipped")),
        (rect(40, 25, 20, 10), (rect(30, 5, 9, 10), "clipped")),
        (rect(60, 60, 5, 5), (None, "dropped")),
    ]
    for mark, want in cases:
        assert _clip_rect(mark, *CROP) == want, mark
        assert clip_mark(mark, *CROP) == want, mark


# ------------------------------------------------------------ AC-106.34 guard


@_ac(34)
def test_ac_106_34_assert_never_probe_passes(ac_id: str) -> None:
    assert ac_id == "AC-106.34"
    # The probe copies domain/capture.py and routes/captures.py to C:/Temp/av-kit/s72/never-probe,
    # removes each step branch and requires pyright to refuse the copy at its assert_never line.
    run = subprocess.run(
        [sys.executable, str(PLAN / "assert-never-probe.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=600,
        check=False,
    )
    lines = run.stdout.strip().splitlines()
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    assert lines[-1] == "assert-never-probe: pass"
