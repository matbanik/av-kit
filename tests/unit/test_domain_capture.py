"""MEU-34 capture domain tests. Imports stay inside tests so collection cannot ERROR."""

from __future__ import annotations

import ast
import inspect
from dataclasses import fields
from datetime import UTC, datetime
from pathlib import Path
from typing import get_type_hints
from uuid import uuid4

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_SRC = REPO_ROOT / "packages" / "core" / "src"

CAPTURE_SOURCE_MEMBERS = (
    "Hotkey",
    "Gui",
    "McpFullscreen",
    "McpRegion",
    "McpInteractive",
    "Scan",
)
CAPTURE_REQUEST_STATUS_MEMBERS = ("Pending", "Completed", "Cancelled", "Expired")
# TA-1 (Session 39, MEU-90, MEU-91): + Pixelate, Eraser.
ANNOTATION_TYPE_MEMBERS = ("Arrow", "Rect", "Highlight", "Text", "Pixelate", "Eraser")
ANNOTATION_WIRE = {
    "Arrow": "arrow",
    "Rect": "rect",
    "Highlight": "highlight",
    "Text": "text",
    "Pixelate": "pixelate",
    "Eraser": "eraser",
}
# PIXELATE_BLOCK (Session 39): MIN, MAX, DEFAULT, restated so the oracle is independent.
PIXELATE_BLOCK = (2, 100, 10)
NAMED_COLORS = ("red", "orange", "yellow", "green", "blue", "white", "black")
TEXT_MAX_CHARS = 500
HIGHLIGHT_OPACITY_MIN = 0
HIGHLIGHT_OPACITY_MAX = 1
CAPTURE_MIN_EDGE_PX = 8
CAPTURE_SHOT_COLUMNS = (
    "id",
    "original_path",
    "annotated_path",
    "sidecar_path",
    "display_name",
    "width",
    "height",
    "file_size",
    "source",
    "created_at",
    "updated_at",
)
CAPTURE_REQUEST_COLUMNS = ("id", "status", "shot_id", "created_at", "expires_at")
SETTING_NS = "capture"
FORBIDDEN_QUEUE_NAME = "captures"
PIL_FORBIDDEN = ("PIL", "mss")
CAPTURE_ERRORS = (
    "CaptureNotSupportedError",
    "CaptureFailedError",
    "InboxPathError",
    "AnnotationValidationError",
    "CaptureRequestConflictError",
)


def _now() -> datetime:
    return datetime.now(UTC)


def _field_names(cls: type[object]) -> tuple[str, ...]:
    return tuple(item.name for item in fields(cls))


def _shot_kwargs(**overrides: object) -> dict[str, object]:
    from avkit_core.domain.enums import CaptureSource

    base: dict[str, object] = {
        "id": str(uuid4()),
        "original_path": Path("C:/inbox/shot.png"),
        "annotated_path": None,
        "sidecar_path": None,
        "display_name": "shot.png",
        "width": 1920,
        "height": 1080,
        "file_size": 12,
        "source": CaptureSource.Hotkey,
        "created_at": _now(),
        "updated_at": _now(),
    }
    base.update(overrides)
    return base


def _request_kwargs(**overrides: object) -> dict[str, object]:
    from avkit_core.domain.enums import CaptureRequestStatus

    base: dict[str, object] = {
        "id": str(uuid4()),
        "status": CaptureRequestStatus.Pending,
        "shot_id": None,
        "created_at": _now(),
        "expires_at": _now(),
    }
    base.update(overrides)
    return base


@pytest.mark.parametrize("ac_id", ["AC-34.1"], ids=["AC-34.1"])
@pytest.mark.unit
def test_ac_34_1_capture_enums_persist_name_and_wire(ac_id: str) -> None:
    assert ac_id == "AC-34.1"
    from avkit_core.domain.enums import AnnotationType, CaptureRequestStatus, CaptureSource

    assert tuple(member.name for member in CaptureSource) == CAPTURE_SOURCE_MEMBERS
    assert tuple(member.value for member in CaptureSource) == CAPTURE_SOURCE_MEMBERS
    assert tuple(member.name for member in CaptureRequestStatus) == CAPTURE_REQUEST_STATUS_MEMBERS
    assert tuple(member.name for member in AnnotationType) == ANNOTATION_TYPE_MEMBERS
    for member in CaptureSource:
        assert member.value == member.name
    for member in AnnotationType:
        assert member.to_wire() == ANNOTATION_WIRE[member.name]
    with pytest.raises(ValueError):
        CaptureSource("Nope")


@pytest.mark.parametrize("ac_id", ["AC-34.2"], ids=["AC-34.2"])
@pytest.mark.unit
def test_ac_34_2_queue_names_excludes_captures(ac_id: str) -> None:
    assert ac_id == "AC-34.2"
    from avkit_core.domain.enums import CaptureSource, QueueProcessorState
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.queue import QUEUE_NAMES, QueueRuntime

    assert CaptureSource.Scan.name == "Scan"
    assert FORBIDDEN_QUEUE_NAME not in QUEUE_NAMES
    with pytest.raises(ValidationError):
        QueueRuntime(
            queue_name=FORBIDDEN_QUEUE_NAME,
            state=QueueProcessorState.Idle,
            current_job_id=None,
        )


@pytest.mark.parametrize("ac_id", ["AC-34.3"], ids=["AC-34.3"])
@pytest.mark.unit
def test_ac_34_3_setting_namespace_capture(ac_id: str) -> None:
    assert ac_id == "AC-34.3"
    from avkit_core.domain.enums import SettingValueType
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.settings import SETTING_NAMESPACES, Setting

    assert SETTING_NS in SETTING_NAMESPACES
    setting = Setting(
        namespace=SETTING_NS,
        key="inbox_dir",
        value="~/Pictures/av-kit",
        value_type=SettingValueType.String,
        updated_at=_now(),
    )
    assert setting.namespace == SETTING_NS
    with pytest.raises(ValidationError):
        Setting(
            namespace="not-a-namespace",
            key="inbox_dir",
            value="x",
            value_type=SettingValueType.String,
            updated_at=_now(),
        )


@pytest.mark.parametrize("ac_id", ["AC-34.4"], ids=["AC-34.4"])
@pytest.mark.unit
def test_ac_34_4_capture_shot_fields_frozen_absolute(ac_id: str) -> None:
    assert ac_id == "AC-34.4"
    from avkit_core.domain.capture import CaptureShot
    from avkit_core.domain.errors import ValidationError

    shot = CaptureShot(**_shot_kwargs())
    assert _field_names(CaptureShot) == CAPTURE_SHOT_COLUMNS
    assert CaptureShot.__dataclass_params__.frozen is True
    with pytest.raises(TypeError):
        CaptureShot(**_shot_kwargs(), extra_field=1)  # type: ignore[call-arg]
    with pytest.raises(ValidationError):
        CaptureShot(**_shot_kwargs(original_path=Path("relative/shot.png")))
    with pytest.raises(ValidationError):
        CaptureShot(**_shot_kwargs(width=-1))
    with pytest.raises(ValidationError):
        CaptureShot(**_shot_kwargs(height=-1))
    with pytest.raises(ValidationError):
        CaptureShot(**_shot_kwargs(file_size=-1))
    assert shot.width == 1920


@pytest.mark.parametrize("ac_id", ["AC-34.5"], ids=["AC-34.5"])
@pytest.mark.unit
def test_ac_34_5_capture_request_fields_optional_shot(ac_id: str) -> None:
    assert ac_id == "AC-34.5"
    from avkit_core.domain.capture import CaptureRequest
    from avkit_core.domain.enums import CaptureRequestStatus

    pending = CaptureRequest(**_request_kwargs())
    assert _field_names(CaptureRequest) == CAPTURE_REQUEST_COLUMNS
    assert pending.shot_id is None
    assert pending.status is CaptureRequestStatus.Pending
    completed = CaptureRequest(
        **_request_kwargs(status=CaptureRequestStatus.Completed, shot_id=str(uuid4()))
    )
    assert completed.shot_id is not None
    from avkit_core.domain.errors import ValidationError

    with pytest.raises(ValidationError):
        CaptureRequest(**_request_kwargs(status=CaptureRequestStatus.Completed, shot_id=None))
    with pytest.raises(TypeError):
        CaptureRequest(**_request_kwargs(), extra_field=True)  # type: ignore[call-arg]


@pytest.mark.parametrize("ac_id", ["AC-34.6"], ids=["AC-34.6"])
@pytest.mark.unit
def test_ac_34_6_capture_request_transitions_exhaustive(ac_id: str) -> None:
    assert ac_id == "AC-34.6"
    from avkit_core.domain.capture import CAPTURE_REQUEST_TRANSITIONS
    from avkit_core.domain.enums import CaptureRequestStatus

    assert set(CAPTURE_REQUEST_TRANSITIONS.keys()) == set(CaptureRequestStatus)
    allowed = CAPTURE_REQUEST_TRANSITIONS[CaptureRequestStatus.Pending]
    assert allowed == frozenset(
        {
            CaptureRequestStatus.Completed,
            CaptureRequestStatus.Cancelled,
            CaptureRequestStatus.Expired,
        }
    )
    assert CAPTURE_REQUEST_TRANSITIONS[CaptureRequestStatus.Completed] == frozenset()
    assert CAPTURE_REQUEST_TRANSITIONS[CaptureRequestStatus.Cancelled] == frozenset()
    assert CAPTURE_REQUEST_TRANSITIONS[CaptureRequestStatus.Expired] == frozenset()


@pytest.mark.parametrize("ac_id", ["AC-34.7"], ids=["AC-34.7"])
@pytest.mark.unit
def test_ac_34_7_annotation_vos_reject_unknown_color_and_text(ac_id: str) -> None:
    assert ac_id == "AC-34.7"
    from avkit_core.domain.capture import HighlightAnnotation, RectAnnotation, TextAnnotation
    from avkit_core.domain.errors import AnnotationValidationError

    with pytest.raises(AnnotationValidationError):
        RectAnnotation(x=0, y=0, width=10, height=10, color="purple", stroke_width=2)
    with pytest.raises(AnnotationValidationError):
        TextAnnotation(x=0, y=0, text="", color="red", font_size=12, bg_color=None)
    with pytest.raises(AnnotationValidationError):
        TextAnnotation(
            x=0,
            y=0,
            text="x" * (TEXT_MAX_CHARS + 1),
            color="red",
            font_size=12,
            bg_color=None,
        )
    with pytest.raises(AnnotationValidationError):
        RectAnnotation(x=0, y=0, width=-1, height=10, color="red", stroke_width=2)
    with pytest.raises(TypeError):
        HighlightAnnotation(
            x=0,
            y=0,
            width=10,
            height=10,
            color="red",
            opacity=0.4,
            extra_field=1,  # type: ignore[call-arg]
        )
    ok = TextAnnotation(x=1, y=2, text="ok", color="#00FF00", font_size=12, bg_color=None)
    assert ok.text == "ok"
    for name in NAMED_COLORS:
        RectAnnotation(x=0, y=0, width=4, height=4, color=name, stroke_width=1)


@pytest.mark.parametrize("ac_id", ["AC-34.8"], ids=["AC-34.8"])
@pytest.mark.unit
def test_ac_34_8_bbox_min_edge(ac_id: str) -> None:
    assert ac_id == "AC-34.8"
    from avkit_core.domain.capture import BBox
    from avkit_core.domain.errors import ValidationError

    ok = BBox(x=0, y=0, width=CAPTURE_MIN_EDGE_PX, height=CAPTURE_MIN_EDGE_PX)
    assert ok.width == CAPTURE_MIN_EDGE_PX
    with pytest.raises(ValidationError):
        BBox(x=0, y=0, width=7, height=7)
    with pytest.raises(ValidationError):
        BBox(x=0, y=0, width=CAPTURE_MIN_EDGE_PX, height=7)


@pytest.mark.parametrize("ac_id", ["AC-34.9"], ids=["AC-34.9"])
@pytest.mark.unit
def test_ac_34_9_image_probe_fields(ac_id: str) -> None:
    assert ac_id == "AC-34.9"
    from avkit_core.domain.capture import ImageProbe

    ImageProbe(width=10, height=20, file_size=30)
    assert _field_names(ImageProbe) == ("width", "height", "file_size")
    with pytest.raises(TypeError):
        ImageProbe(width=10, height=20, file_size=30, extra=1)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        ImageProbe(width=10, height=20)  # type: ignore[call-arg]


@pytest.mark.parametrize("ac_id", ["AC-34.10"], ids=["AC-34.10"])
@pytest.mark.unit
def test_ac_34_10_capture_ports_signatures(ac_id: str) -> None:
    assert ac_id == "AC-34.10"
    from avkit_core.domain.capture import Annotation, BBox
    from avkit_core.ports.capture import ImageAnnotatePort, ScreenCapturePort

    capture_full = inspect.signature(ScreenCapturePort.capture_fullscreen)
    capture_region = inspect.signature(ScreenCapturePort.capture_region)
    probe = inspect.signature(ImageAnnotatePort.probe)
    bake = inspect.signature(ImageAnnotatePort.bake)
    assert list(capture_full.parameters) == ["self", "output_path"]
    assert capture_full.parameters["output_path"].annotation is Path
    assert list(capture_region.parameters) == ["self", "output_path", "bbox"]
    assert capture_region.parameters["bbox"].annotation is BBox
    assert list(probe.parameters) == ["self", "path"]
    assert probe.parameters["path"].annotation is Path
    # TA-9 (Session 30, MEU-67): BAKE_PORT gains the defaulted output_format.
    assert list(bake.parameters) == [
        "self",
        "original_path",
        "annotations",
        "output_path",
        "output_format",
    ]
    hints = get_type_hints(ImageAnnotatePort.bake)
    assert hints["original_path"] is Path
    assert hints["output_path"] is Path
    assert "Sequence" in str(hints["annotations"]) or hints["annotations"] is not Path
    _ = Annotation
    from avkit_core.domain.capture import ArrowAnnotation

    assert ArrowAnnotation.__name__ == "ArrowAnnotation"


@pytest.mark.parametrize("ac_id", ["AC-34.11"], ids=["AC-34.11"])
@pytest.mark.unit
def test_ac_34_11_capture_errors_exist_no_hotkey(ac_id: str) -> None:
    assert ac_id == "AC-34.11"
    from avkit_core.domain import errors as errors_mod

    for name in CAPTURE_ERRORS:
        cls = getattr(errors_mod, name)
        err = cls("domain failure")
        assert isinstance(err, Exception)
        assert type(err) is cls
    assert getattr(errors_mod, "HotkeyConflictError", None) is None


@pytest.mark.parametrize("ac_id", ["AC-34.12"], ids=["AC-34.12"])
@pytest.mark.unit
def test_ac_34_12_core_forbids_pillow_and_mss(ac_id: str) -> None:
    assert ac_id == "AC-34.12"
    from tests.unit.test_domain import INFRA_NAMES

    assert (CORE_SRC / "avkit_core" / "domain" / "capture.py").is_file()
    assert set(PIL_FORBIDDEN) <= INFRA_NAMES
    forbidden = set(PIL_FORBIDDEN)
    hits: list[str] = []
    for path in CORE_SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        found = sorted(names & forbidden)
        if found:
            hits.append(f"{path.relative_to(REPO_ROOT)}:{found}")
    assert hits == []


@pytest.mark.parametrize("ac_id", ["AC-34.13"], ids=["AC-34.13"])
@pytest.mark.unit
def test_ac_34_13_highlight_opacity_inclusive_bounds(ac_id: str) -> None:
    assert ac_id == "AC-34.13"
    from avkit_core.domain.capture import HighlightAnnotation
    from avkit_core.domain.errors import AnnotationValidationError

    low = HighlightAnnotation(
        x=0, y=0, width=4, height=4, color="red", opacity=HIGHLIGHT_OPACITY_MIN
    )
    high = HighlightAnnotation(
        x=0, y=0, width=4, height=4, color="red", opacity=HIGHLIGHT_OPACITY_MAX
    )
    assert low.opacity == HIGHLIGHT_OPACITY_MIN
    assert high.opacity == HIGHLIGHT_OPACITY_MAX
    with pytest.raises(AnnotationValidationError):
        HighlightAnnotation(x=0, y=0, width=4, height=4, color="red", opacity=2)
    with pytest.raises(AnnotationValidationError):
        HighlightAnnotation(x=0, y=0, width=4, height=4, color="red", opacity=-0.1)


@pytest.mark.parametrize("ac_id", ["AC-90.1"], ids=["AC-90.1"])
@pytest.mark.unit
def test_ac_90_1_pixelate_annotation_and_block_bounds(ac_id: str) -> None:
    assert ac_id == "AC-90.1"
    from typing import get_args

    from avkit_core.domain.capture import (
        PIXELATE_BLOCK_DEFAULT,
        PIXELATE_BLOCK_MAX,
        PIXELATE_BLOCK_MIN,
        Annotation,
        PixelateAnnotation,
    )
    from avkit_core.domain.enums import AnnotationType
    from avkit_core.domain.errors import AnnotationValidationError

    assert (PIXELATE_BLOCK_MIN, PIXELATE_BLOCK_MAX, PIXELATE_BLOCK_DEFAULT) == PIXELATE_BLOCK
    assert AnnotationType.Pixelate.to_wire() == "pixelate"
    assert PixelateAnnotation in get_args(Annotation)
    assert _field_names(PixelateAnnotation) == ("x", "y", "width", "height", "block_size")
    for block in PIXELATE_BLOCK:
        mark = PixelateAnnotation(x=-3, y=4, width=0, height=7, block_size=block)
        assert (mark.x, mark.y, mark.width, mark.height, mark.block_size) == (-3, 4, 0, 7, block)
    for bad in (1, 101, True, 2.0):
        with pytest.raises(AnnotationValidationError):
            PixelateAnnotation(x=0, y=0, width=4, height=4, block_size=bad)  # type: ignore[arg-type]
    with pytest.raises(AnnotationValidationError):
        PixelateAnnotation(x=0, y=0, width=-1, height=4, block_size=10)
    with pytest.raises(AnnotationValidationError):
        PixelateAnnotation(x=0, y=0, width=4, height=-1, block_size=10)
    with pytest.raises(AnnotationValidationError):
        PixelateAnnotation(x=1.5, y=0, width=4, height=4, block_size=10)  # type: ignore[arg-type]


@pytest.mark.parametrize("ac_id", ["AC-91.1"], ids=["AC-91.1"])
@pytest.mark.unit
def test_ac_91_1_eraser_annotation_is_a_rectangle(ac_id: str) -> None:
    assert ac_id == "AC-91.1"
    from typing import get_args

    from avkit_core.domain.capture import Annotation, EraserAnnotation
    from avkit_core.domain.enums import AnnotationType
    from avkit_core.domain.errors import AnnotationValidationError

    assert AnnotationType.Eraser.to_wire() == "eraser"
    assert EraserAnnotation in get_args(Annotation)
    assert _field_names(EraserAnnotation) == ("x", "y", "width", "height")
    mark = EraserAnnotation(x=-3, y=4, width=0, height=7)
    assert (mark.x, mark.y, mark.width, mark.height) == (-3, 4, 0, 7)
    with pytest.raises(AnnotationValidationError):
        EraserAnnotation(x=0, y=0, width=4, height=-1)
    with pytest.raises(AnnotationValidationError):
        EraserAnnotation(x=0, y=0, width=-1, height=4)
    with pytest.raises(AnnotationValidationError):
        EraserAnnotation(x=True, y=0, width=4, height=4)  # type: ignore[arg-type]
    with pytest.raises(AnnotationValidationError):
        EraserAnnotation(x=0, y=1.5, width=4, height=4)  # type: ignore[arg-type]
