"""MEU-107 capture step mark (Session 72): AC-107.1 (Python) to .5, .9, .10, .12's Python half,
.15's service half, .23 and the Python half of the guard AC-107.28.

Every check works on in-memory values, fakes and images generated under tmp_path; nothing
reads user data.
"""

from __future__ import annotations

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
STEP_KEYS = ["type", "x", "y", "number", "color", "size"]
STEP_WIRE = {"type": "step", "x": 40, "y": 30, "number": 7, "color": "#E0AF68", "size": 32}
STEP_ARGS: dict[str, Any] = {"x": 40, "y": 30, "number": 7, "color": "#E0AF68", "size": 32}
DISC = (224, 175, 104)  # #E0AF68
WHITE = (255, 255, 255)
# The input matrix (implementation-plan.md MEU-107), Domain column: field and refused value.
BAD_FIELDS: dict[str, tuple[str, object]] = {
    "x-negative": ("x", -1),
    "x-bool": ("x", True),
    "x-float": ("x", 1.5),
    "y-negative": ("y", -1),
    "number-0": ("number", 0),
    "number-1000": ("number", 1000),
    "size-11": ("size", 11),
    "size-201": ("size", 201),
    "color-empty": ("color", ""),
    "color-bell": ("color", "\x07"),
    "color-surrogate": ("color", "\ud800"),
}
# A crop (left, top, width, height) of 40 x 30; each step centre is in the source's pixels.
CROP = (10, 20, 40, 30)
STEP_CROP: dict[str, tuple[tuple[int, int], tuple[int, int] | None]] = {
    "origin": ((10, 20), (0, 0)),
    "far-corner": ((49, 49), (39, 29)),
    "right-past": ((50, 25), None),
    "bottom-past": ((15, 50), None),
    "left-past": ((9, 25), None),
}
TEXT_COLOURS: dict[str, str] = {
    "#E0AF68": "#000000",
    "#FFFFFF": "#000000",
    "#FFFF00": "#000000",
    "#00FF00": "#000000",
    "#FF0000": "#000000",
    "#000000": "#FFFFFF",
    "#1A1B26": "#FFFFFF",
    "#0000FF": "#FFFFFF",
}
CENTRE_CASES = [(size, number) for size in (12, 32, 64, 200) for number in (1, 12, 999)]


def _ac(n: int):
    label = f"AC-107.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


# ------------------------------------------------------------ AC-107.1 signatures


@_ac(1)
def test_ac_107_1_step_type_and_mark_fields(ac_id: str) -> None:
    assert ac_id == "AC-107.1"
    from dataclasses import FrozenInstanceError, fields
    from typing import get_type_hints

    from avkit_core.domain.capture import StepAnnotation
    from avkit_core.domain.enums import AnnotationType

    assert AnnotationType.Step.to_wire() == "step"
    assert list(AnnotationType)[-1] is AnnotationType.Step
    assert [f.name for f in fields(StepAnnotation)] == ["x", "y", "number", "color", "size"]
    hints = get_type_hints(StepAnnotation)
    assert [hints[f.name] for f in fields(StepAnnotation)] == [int, int, int, str, int]
    mark = StepAnnotation(x=1, y=2, number=3, color="#E0AF68", size=32)
    with pytest.raises(FrozenInstanceError):
        mark.x = 5  # type: ignore[misc]


@_ac(1)
def test_ac_107_1_step_api_model_fields(ac_id: str) -> None:
    assert ac_id == "AC-107.1"
    from avkit_api.schemas.captures import StepAnnotationIn

    assert list(StepAnnotationIn.model_fields) == ["type", "x", "y", "number", "color", "size"]
    assert all(field.is_required() for field in StepAnnotationIn.model_fields.values())
    assert StepAnnotationIn.model_config.get("extra") == "forbid"


@_ac(1)
def test_ac_107_1_layout_colour_and_clip_signatures(ac_id: str) -> None:
    assert ac_id == "AC-107.1"
    import inspect
    from typing import get_type_hints

    from avkit_core.domain import capture
    from avkit_infra.capture import adapter

    layout = inspect.signature(adapter.step_badge_layout)
    assert list(layout.parameters) == ["x", "y", "number", "size"]
    hints = get_type_hints(adapter.step_badge_layout)
    assert [hints[name] for name in ("x", "y", "number", "size")] == [int] * 4
    assert hints["return"] is adapter.StepLayout
    assert adapter.StepLayout._fields == ("radius", "font_px", "baseline")
    assert get_type_hints(adapter.StepLayout) == {"radius": float, "font_px": int, "baseline": int}
    colour = get_type_hints(adapter.step_text_color)
    assert list(inspect.signature(adapter.step_text_color).parameters) == ["color"]
    assert colour == {"color": str, "return": str}
    clip = inspect.signature(capture._clip_step)
    assert list(clip.parameters) == ["mark", "left", "top", "width", "height"]
    clip_hints = get_type_hints(capture._clip_step)
    assert clip_hints["mark"] is capture.StepAnnotation
    assert clip_hints["return"] == tuple[capture.StepAnnotation | None, capture.MarkCarry]


# ------------------------------------------------------------ AC-107.3 STEP_WIRE


@_ac(3)
def test_ac_107_3_wire_round_trip_keeps_key_order(ac_id: str) -> None:
    assert ac_id == "AC-107.3"
    from avkit_core.domain.capture import StepAnnotation
    from avkit_core.services.capture import _annotation_from_wire, _annotation_to_wire

    mark = _annotation_from_wire(dict(STEP_WIRE))
    assert mark == StepAnnotation(x=40, y=30, number=7, color="#E0AF68", size=32)
    wire = _annotation_to_wire(mark)
    assert list(wire) == STEP_KEYS
    assert wire == STEP_WIRE
    assert _annotation_from_wire(wire) == mark


@_ac(3)
def test_ac_107_3_wire_refuses_missing_and_extra_keys(ac_id: str) -> None:
    assert ac_id == "AC-107.3"
    from avkit_core.domain.errors import AnnotationValidationError
    from avkit_core.services.capture import _annotation_from_wire

    missing = {key: value for key, value in STEP_WIRE.items() if key != "size"}
    with pytest.raises(AnnotationValidationError, match="missing annotation field"):
        _annotation_from_wire(missing)
    with pytest.raises(AnnotationValidationError, match=r"unexpected step field\(s\)"):
        _annotation_from_wire({**STEP_WIRE, "label": "one"})


# ------------------------------------------------------------ AC-107.4 STEP_CLAMP


@_ac(4)
def test_ac_107_4_clamp_matches_the_text_anchor(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-107.4"
    from tests.unit.test_capture_service import _stack

    from avkit_core.domain.capture import StepAnnotation, TextAnnotation

    service = _stack(tmp_path)[0]
    off = StepAnnotation(x=500, y=0, number=12, color="#123456", size=48)
    # The domain refuses a negative centre (AC-107.2), so (500, -3) is set past it
    # to reach the clamp.
    object.__setattr__(off, "y", -3)
    text = TextAnnotation(x=500, y=-3, text="n", color="#123456", font_size=16, bg_color=None)
    clamped = service._clamp_annotation(off, 100, 80)
    text_clamped = service._clamp_annotation(text, 100, 80)
    assert isinstance(clamped, StepAnnotation)
    assert (clamped.x, clamped.y) == (text_clamped.x, text_clamped.y)
    assert (clamped.number, clamped.color, clamped.size) == (12, "#123456", 48)


# ------------------------------------------------------------ AC-107.15 STEP_STYLE (service)


@_ac(15)
def test_ac_107_15_settings_rows_follow_tool_lock(ac_id: str) -> None:
    assert ac_id == "AC-107.15"
    from avkit_core.services.settings import COLOR_HEX, SETTINGS_KEY_TABLE, SettingSpec

    keys = [key for ns, key in SETTINGS_KEY_TABLE if ns == "capture"]
    assert keys[keys.index("tool_lock") + 1 :] == ["step_color", "step_size"]
    assert SETTINGS_KEY_TABLE[("capture", "step_color")] == SettingSpec(
        "string", "#E0AF68", pattern=COLOR_HEX
    )
    assert SETTINGS_KEY_TABLE[("capture", "step_size")] == SettingSpec(
        "number", 32, min_number=12, max_number=200, integer=True
    )


@_ac(15)
def test_ac_107_15_fresh_store_reads_str_and_int(ac_id: str) -> None:
    assert ac_id == "AC-107.15"
    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.services.settings import SettingsService

    settings = SettingsService(SharedFakeFactory(FakeUnitOfWork()))
    color = settings.get("capture", "step_color")
    size = settings.get("capture", "step_size")
    assert color == "#E0AF68" and type(color) is str
    assert size == 32 and type(size) is int


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


def _rgb(color: str) -> tuple[int, int, int]:
    return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))


def _near(pixel: tuple[int, ...], want: tuple[int, int, int], within: int = 3) -> bool:
    """BAKE_AA's ringing allowance: each channel within `within` of `want`."""
    return all(abs(int(got) - w) <= within for got, w in zip(pixel[:3], want, strict=True))


def _render(tmp_path: Path, size: tuple[int, int], marks: list[Any]) -> Any:
    """The adapter's RENDER_BAKE of `marks` on a white image, decoded to RGB."""
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    source = tmp_path / "white.png"
    Image.new("RGB", size, WHITE).save(source)
    png = CaptureAdapter(platform="win32").render(source, marks)
    with Image.open(io.BytesIO(png)) as opened:
        return opened.convert("RGB")


# ------------------------------------------------------------ AC-107.2 STEP_TYPE


@_ac(2)
def test_ac_107_2_valid_steps_build(ac_id: str) -> None:
    assert ac_id == "AC-107.2"
    from avkit_core.domain.capture import StepAnnotation

    low = StepAnnotation(x=0, y=0, number=1, color="#E0AF68", size=12)
    high = StepAnnotation(x=5000, y=5000, number=999, color="blue", size=200)
    assert (low.number, low.size, high.number, high.size) == (1, 12, 999, 200)


@pytest.mark.parametrize("case", list(BAD_FIELDS), ids=[f"AC-107.2-{c}" for c in BAD_FIELDS])
def test_ac_107_2_step_refuses_a_bad_field(case: str) -> None:
    from avkit_core.domain.capture import StepAnnotation
    from avkit_core.domain.errors import AnnotationValidationError

    field, value = BAD_FIELDS[case]
    caught = _caught(lambda: StepAnnotation(**{**STEP_ARGS, field: value}))
    assert isinstance(caught, AnnotationValidationError), f"{case}: {caught!r}"
    message = str(caught)
    assert re.search(rf"\b{field}\b", message), ascii(message)
    assert not _echoes(value, message), ascii(message)


# ------------------------------------------------------------ AC-107.5 STEP_CLIP


@pytest.mark.parametrize("case", list(STEP_CROP), ids=[f"AC-107.5-{c}" for c in STEP_CROP])
def test_ac_107_5_step_is_kept_and_moved_or_dropped(case: str) -> None:
    from avkit_core.domain.capture import StepAnnotation, clip_mark

    (x, y), moved = STEP_CROP[case]
    mark = StepAnnotation(**{**STEP_ARGS, "x": x, "y": y})
    got = clip_mark(mark, *CROP)
    if moved is None:
        assert got == (None, "dropped"), (case, got)
    else:
        want = StepAnnotation(**{**STEP_ARGS, "x": moved[0], "y": moved[1]})
        assert got == (want, "kept"), (case, got)


@_ac(5)
def test_ac_107_5_never_probe_refuses_domain_without_step(ac_id: str) -> None:
    assert ac_id == "AC-107.5"
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
    starts = [i for i, line in enumerate(lines) if line.startswith("== ")]
    domain = [i for i in starts if lines[i].startswith("== domain:")]
    assert len(domain) == 1, lines
    after = [i for i in starts if i > domain[0]]
    section = lines[domain[0] : after[0] if after else len(lines)]
    assert "one error naming StepAnnotation and Never at assert_never: True" in section, section


# ------------------------------------------------------------ AC-107.9 STEP_BAKE contrast


@pytest.mark.parametrize(
    "color", list(TEXT_COLOURS), ids=[f"AC-107.9-{c[1:]}" for c in TEXT_COLOURS]
)
def test_ac_107_9_text_colour_follows_luminance(color: str) -> None:
    from avkit_infra.capture.adapter import step_text_color

    assert step_text_color(color) == TEXT_COLOURS[color], color


@pytest.mark.parametrize(
    "color", ["#E0AF68", "#1A1B26"], ids=["AC-107.9-bake-E0AF68", "AC-107.9-bake-1A1B26"]
)
def test_ac_107_9_bake_draws_disc_and_number_colours(color: str, tmp_path: Path) -> None:
    from avkit_core.domain.capture import StepAnnotation

    x = y = 60
    size = 64
    radius = size // 2
    image = _render(
        tmp_path, (120, 120), [StepAnnotation(x=x, y=y, number=8, color=color, size=size)]
    )
    disc = image.getpixel((x, y - radius + 2))
    assert _near(disc, _rgb(color)), (color, disc)
    text = _rgb(TEXT_COLOURS[color])
    inner = radius - 3
    hits = [
        (px, py)
        for py in range(y - inner, y + inner + 1)
        for px in range(x - inner, x + inner + 1)
        if (px - x) ** 2 + (py - y) ** 2 <= inner * inner and _near(image.getpixel((px, py)), text)
    ]
    assert hits, (color, "no pixel of the number has the text colour")


# ------------------------------------------------------------ AC-107.10 STEP_CENTRE


@pytest.mark.parametrize(
    ("size", "number"), CENTRE_CASES, ids=[f"AC-107.10-s{s}-n{n}" for s, n in CENTRE_CASES]
)
def test_ac_107_10_number_ink_is_centred_in_the_disc(
    size: int, number: int, tmp_path: Path
) -> None:
    from avkit_core.domain.capture import StepAnnotation

    x = y = 220
    radius = size / 2
    image = _render(
        tmp_path, (440, 440), [StepAnnotation(x=x, y=y, number=number, color="#E0AF68", size=size)]
    )
    # The disc over white is never darker than its colour; the black number is.
    reach = size // 2 + 2
    ink = [
        (px, py)
        for py in range(y - reach, y + reach + 1)
        for px in range(x - reach, x + reach + 1)
        if any(c < d - 3 for c, d in zip(image.getpixel((px, py)), DISC, strict=True))
    ]
    assert ink, (size, number, "no number ink")
    left = min(px for px, _ in ink)
    top = min(py for _, py in ink)
    right = max(px for px, _ in ink) + 1
    bottom = max(py for _, py in ink) + 1
    dx = (left + right) / 2 - x
    dy = (top + bottom) / 2 - y
    assert abs(dx) <= max(2, size / 40), (size, number, dx)
    assert abs(dy) <= max(1, size / 40), (size, number, dy)
    assert left >= x - radius and right <= x + radius, (size, number, left, right)
    assert top >= y - radius and bottom <= y + radius, (size, number, top, bottom)


# ------------------------------------------------------------ AC-107.12 parity (Python half)


@_ac(12)
def test_ac_107_12_fixture_steps_equal_the_adapter_layout(ac_id: str) -> None:
    assert ac_id == "AC-107.12"
    from avkit_infra.capture.adapter import StepLayout, step_badge_layout

    entries = json.loads(GEOMETRY.read_bytes())["steps"]
    assert sorted((e["size"], e["number"]) for e in entries) == sorted(CENTRE_CASES)
    for entry in entries:
        got = step_badge_layout(entry["x"], entry["y"], entry["number"], entry["size"])
        want = StepLayout(entry["radius"], entry["font_px"], entry["baseline"])
        assert got == want, (entry, got)


# ------------------------------------------------------------ AC-107.23 export paths


def _real_stack(tmp_path: Path) -> tuple[Any, Any, Any, list[Any]]:
    """The service on fakes with the real adapter; the step bake's calls are recorded."""
    from PIL import Image
    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.domain.enums import CaptureSource
    from avkit_core.services.capture import CaptureService
    from avkit_core.services.settings import SettingsService
    from avkit_infra.capture.adapter import CaptureAdapter

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    png = inbox / "shot.png"
    Image.new("RGB", (64, 64), WHITE).save(png)
    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    settings.set("capture", "inbox_dir", str(inbox))
    settings.set("capture", "flatten_backup", False)
    adapter = CaptureAdapter(mss_factory=lambda: None, platform="linux")
    calls: list[Any] = []
    original = adapter._apply_step

    def recording(canvas: Any, annotation: Any) -> Any:
        calls.append(annotation)
        return original(canvas, annotation)

    adapter._apply_step = recording  # type: ignore[method-assign]
    service = CaptureService(factory, capture=adapter, annotate=adapter, settings=settings)
    shot = service.register_shot(png.resolve(), CaptureSource.Gui)
    return service, shot, png, calls


def _disc_pixel(image: Any) -> tuple[int, ...]:
    # The step below is centred on (32, 32) with radius 16: (x, y - radius + 2) is (32, 18).
    return image.convert("RGB").getpixel((32, 18))


def _step() -> Any:
    from avkit_core.domain.capture import StepAnnotation

    return StepAnnotation(x=32, y=32, number=1, color="#E0AF68", size=32)


@_ac(23)
def test_ac_107_23_annotated_export_draws_the_disc(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-107.23"
    from PIL import Image

    service, shot, _png, calls = _real_stack(tmp_path)
    saved = service.annotate_and_save(shot.id, [_step()])
    assert calls == [_step()]
    assert saved.annotated_path is not None
    with Image.open(saved.annotated_path) as baked:
        assert _near(_disc_pixel(baked), DISC), _disc_pixel(baked)


@_ac(23)
def test_ac_107_23_flatten_draws_the_disc(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-107.23"
    from PIL import Image

    service, shot, png, calls = _real_stack(tmp_path)
    service.annotate_and_save(shot.id, [_step()])
    calls.clear()
    service.flatten(shot.id)
    assert _step() in calls
    with Image.open(png) as flat:
        assert _near(_disc_pixel(flat), DISC), _disc_pixel(flat)


@_ac(23)
def test_ac_107_23_copy_image_bake_draws_the_disc(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-107.23"
    from PIL import Image

    service, shot, _png, calls = _real_stack(tmp_path)
    data = service.render_marks(shot.id, [_step()])
    assert calls == [_step()]
    with Image.open(io.BytesIO(data)) as shown:
        assert _near(_disc_pixel(shown), DISC), _disc_pixel(shown)


# ------------------------------------------------------------ AC-107.28 (guard, Python half)


def _others() -> dict[str, tuple[Any, list[str], Any]]:
    """One mark of every other type inside CROP: (mark, wire keys, clip result)."""
    from avkit_core.domain import capture as c

    return {
        "arrow": (
            c.ArrowAnnotation(from_xy=(15, 25), to_xy=(40, 40), color="red", stroke_width=3),
            ["type", "from", "to", "color", "stroke_width"],
            c.ArrowAnnotation(from_xy=(5, 5), to_xy=(30, 20), color="red", stroke_width=3),
        ),
        "rect": (
            c.RectAnnotation(x=15, y=25, width=10, height=8, color="red", stroke_width=2),
            ["type", "x", "y", "width", "height", "color", "stroke_width"],
            c.RectAnnotation(x=5, y=5, width=10, height=8, color="red", stroke_width=2),
        ),
        "highlight": (
            c.HighlightAnnotation(x=15, y=25, width=10, height=8, color="#FFFF00", opacity=0.4),
            ["type", "x", "y", "width", "height", "color", "opacity"],
            c.HighlightAnnotation(x=5, y=5, width=10, height=8, color="#FFFF00", opacity=0.4),
        ),
        "text": (
            c.TextAnnotation(x=15, y=25, text="hi", color="red", font_size=16, bg_color=None),
            ["type", "x", "y", "text", "color", "font_size"],
            c.TextAnnotation(x=5, y=5, text="hi", color="red", font_size=16, bg_color=None),
        ),
        "pixelate": (
            c.PixelateAnnotation(x=15, y=25, width=10, height=8, block_size=4),
            ["type", "x", "y", "width", "height", "block_size"],
            c.PixelateAnnotation(x=5, y=5, width=10, height=8, block_size=4),
        ),
        "eraser": (
            c.EraserAnnotation(x=15, y=25, width=10, height=8),
            ["type", "x", "y", "width", "height"],
            c.EraserAnnotation(x=5, y=5, width=10, height=8),
        ),
        "redact": (
            c.RedactAnnotation(x=15, y=25, width=10, height=8, color="#000000"),
            ["type", "x", "y", "width", "height", "color"],
            c.RedactAnnotation(x=5, y=5, width=10, height=8, color="#000000"),
        ),
    }


OTHER_KINDS = ["arrow", "rect", "highlight", "text", "pixelate", "eraser", "redact"]


@pytest.mark.parametrize("kind", OTHER_KINDS, ids=[f"AC-107.28-{k}" for k in OTHER_KINDS])
def test_ac_107_28_other_marks_hold_beside_a_step(kind: str, tmp_path: Path) -> None:
    from tests.unit.test_capture_service import _stack

    from avkit_core.domain.capture import StepAnnotation, clip_mark
    from avkit_core.services.capture import annotations_from_sidecar, annotations_to_wire

    mark, keys, clipped = _others()[kind]
    step = StepAnnotation(x=20, y=30, number=1, color="#E0AF68", size=24)
    marks = [step, mark, step]
    wire = annotations_to_wire(marks)
    assert list(wire[1]) == keys
    assert annotations_from_sidecar({"annotations": wire})[1] == mark
    service = _stack(tmp_path)[0]
    assert [service._clamp_annotation(m, 100, 80) for m in marks][1] == mark
    assert [clip_mark(m, *CROP) for m in marks][1] == (clipped, "kept")
