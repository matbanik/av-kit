"""Capture inbox entities, annotation value objects, and geometry."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from avkit_core.domain.enums import CaptureRequestStatus, CaptureSource
from avkit_core.domain.errors import (
    AnnotationValidationError,
    ValidationError,
    require_datetime,
    require_enum,
    require_non_empty_str,
    require_non_negative_int,
    require_optional_path,
    require_optional_str,
    require_path,
    require_uuid_str,
)

CAPTURE_MIN_EDGE_PX = 8
TEXT_MAX_CHARS = 500
HIGHLIGHT_OPACITY_MIN = 0.0
HIGHLIGHT_OPACITY_MAX = 1.0
# PIXELATE_BLOCK (Session 39, MEU-90): the pixelate mark's block edge in pixels.
PIXELATE_BLOCK_MIN = 2
PIXELATE_BLOCK_MAX = 100
PIXELATE_BLOCK_DEFAULT = 10
NAMED_COLORS: frozenset[str] = frozenset(
    {"red", "orange", "yellow", "green", "blue", "white", "black"}
)
_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")

# ANNOTATED_FORMATS (MEU-67): the Save overlay copy is one of these, `capture.annotated_format`.
AnnotatedFormat = Literal["png", "jpeg", "webp"]
ANNOTATED_FORMATS: tuple[AnnotatedFormat, ...] = ("png", "jpeg", "webp")
ANNOTATED_EXT: dict[str, str] = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}
ANNOTATED_SUFFIXES: tuple[str, ...] = tuple(f".annotated{ext}" for ext in ANNOTATED_EXT.values())

CAPTURE_REQUEST_TRANSITIONS: dict[CaptureRequestStatus, frozenset[CaptureRequestStatus]] = {
    CaptureRequestStatus.Pending: frozenset(
        {
            CaptureRequestStatus.Completed,
            CaptureRequestStatus.Cancelled,
            CaptureRequestStatus.Expired,
        }
    ),
    CaptureRequestStatus.Completed: frozenset(),
    CaptureRequestStatus.Cancelled: frozenset(),
    CaptureRequestStatus.Expired: frozenset(),
}


def _require_absolute_path(value: object, field: str) -> Path:
    path = require_path(value, field)
    if not path.is_absolute():
        raise ValidationError(f"{field} must be an absolute Path")
    return path


def _require_color(value: object, field: str) -> str:
    text = require_non_empty_str(value, field)
    if text in NAMED_COLORS or _HEX_COLOR.fullmatch(text):
        return text
    raise AnnotationValidationError(f"{field} must be a named color or #RRGGBB")


def _require_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AnnotationValidationError(f"{field} must be an int")
    return value


def _require_opacity(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise AnnotationValidationError(f"{field} must be a number")
    number = float(value)
    if number < HIGHLIGHT_OPACITY_MIN or number > HIGHLIGHT_OPACITY_MAX:
        raise AnnotationValidationError(
            f"{field} must be in [{HIGHLIGHT_OPACITY_MIN}, {HIGHLIGHT_OPACITY_MAX}]"
        )
    return number


def _require_point(value: object, field: str) -> tuple[int, int]:
    if not isinstance(value, tuple) or len(value) != 2:
        raise AnnotationValidationError(f"{field} must be a two-int tuple")
    return (_require_int(value[0], f"{field}[0]"), _require_int(value[1], f"{field}[1]"))


@dataclass(frozen=True)
class BBox:
    """Virtual-desktop rectangle. Width and height must be at least CAPTURE_MIN_EDGE_PX."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if isinstance(self.x, bool) or not isinstance(self.x, int):
            raise ValidationError("x must be an int")
        if isinstance(self.y, bool) or not isinstance(self.y, int):
            raise ValidationError("y must be an int")
        if isinstance(self.width, bool) or not isinstance(self.width, int):
            raise ValidationError("width must be an int")
        if isinstance(self.height, bool) or not isinstance(self.height, int):
            raise ValidationError("height must be an int")
        if self.width < CAPTURE_MIN_EDGE_PX or self.height < CAPTURE_MIN_EDGE_PX:
            raise ValidationError(
                f"width and height must be >= {CAPTURE_MIN_EDGE_PX}"
            )


@dataclass(frozen=True)
class ImageProbe:
    """Pixel size and byte length of an image file."""

    width: int
    height: int
    file_size: int

    def __post_init__(self) -> None:
        require_non_negative_int(self.width, "width")
        require_non_negative_int(self.height, "height")
        require_non_negative_int(self.file_size, "file_size")


@dataclass(frozen=True)
class ArrowAnnotation:
    """Pixel-space arrow from from_xy to to_xy."""

    from_xy: tuple[int, int]
    to_xy: tuple[int, int]
    color: str
    stroke_width: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "from_xy", _require_point(self.from_xy, "from_xy"))
        object.__setattr__(self, "to_xy", _require_point(self.to_xy, "to_xy"))
        object.__setattr__(self, "color", _require_color(self.color, "color"))
        if isinstance(self.stroke_width, bool) or not isinstance(self.stroke_width, int):
            raise AnnotationValidationError("stroke_width must be an int")


@dataclass(frozen=True)
class RectAnnotation:
    """Stroke rectangle in original-image pixels."""

    x: int
    y: int
    width: int
    height: int
    color: str
    stroke_width: int

    def __post_init__(self) -> None:
        _require_int(self.x, "x")
        _require_int(self.y, "y")
        _require_int(self.width, "width")
        _require_int(self.height, "height")
        if self.width < 0 or self.height < 0:
            raise AnnotationValidationError("rect size must not be negative")
        object.__setattr__(self, "color", _require_color(self.color, "color"))
        if isinstance(self.stroke_width, bool) or not isinstance(self.stroke_width, int):
            raise AnnotationValidationError("stroke_width must be an int")


@dataclass(frozen=True)
class HighlightAnnotation:
    """Translucent fill rectangle. Opacity is inclusive [0, 1]."""

    x: int
    y: int
    width: int
    height: int
    color: str
    opacity: float

    def __post_init__(self) -> None:
        _require_int(self.x, "x")
        _require_int(self.y, "y")
        _require_int(self.width, "width")
        _require_int(self.height, "height")
        if self.width < 0 or self.height < 0:
            raise AnnotationValidationError("highlight size must not be negative")
        object.__setattr__(self, "color", _require_color(self.color, "color"))
        object.__setattr__(self, "opacity", _require_opacity(self.opacity, "opacity"))


@dataclass(frozen=True)
class TextAnnotation:
    """Text overlay. Length is 1–TEXT_MAX_CHARS."""

    x: int
    y: int
    text: str
    color: str
    font_size: int
    bg_color: str | None

    def __post_init__(self) -> None:
        _require_int(self.x, "x")
        _require_int(self.y, "y")
        if not isinstance(self.text, str) or self.text == "" or len(self.text) > TEXT_MAX_CHARS:
            raise AnnotationValidationError(
                f"text must be 1–{TEXT_MAX_CHARS} characters"
            )
        object.__setattr__(self, "color", _require_color(self.color, "color"))
        if isinstance(self.font_size, bool) or not isinstance(self.font_size, int):
            raise AnnotationValidationError("font_size must be an int")
        if self.bg_color is not None:
            object.__setattr__(self, "bg_color", _require_color(self.bg_color, "bg_color"))


@dataclass(frozen=True)
class PixelateAnnotation:
    """Region mark (``REGION_DTO``): a mosaic of ``block_size`` squares over the rectangle."""

    x: int
    y: int
    width: int
    height: int
    block_size: int

    def __post_init__(self) -> None:
        _require_int(self.x, "x")
        _require_int(self.y, "y")
        _require_int(self.width, "width")
        _require_int(self.height, "height")
        if self.width < 0 or self.height < 0:
            raise AnnotationValidationError("pixelate size must not be negative")
        _require_int(self.block_size, "block_size")
        if not PIXELATE_BLOCK_MIN <= self.block_size <= PIXELATE_BLOCK_MAX:
            raise AnnotationValidationError(
                f"block_size must be in [{PIXELATE_BLOCK_MIN}, {PIXELATE_BLOCK_MAX}]"
            )


@dataclass(frozen=True)
class EraserAnnotation:
    """Region mark (``REGION_DTO``): the rectangle filled with one colour sampled around it."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        _require_int(self.x, "x")
        _require_int(self.y, "y")
        _require_int(self.width, "width")
        _require_int(self.height, "height")
        if self.width < 0 or self.height < 0:
            raise AnnotationValidationError("eraser size must not be negative")


Annotation = (
    ArrowAnnotation
    | RectAnnotation
    | HighlightAnnotation
    | TextAnnotation
    | PixelateAnnotation
    | EraserAnnotation
)


@dataclass(frozen=True)
class CaptureShot:
    """One original inbox file plus optional annotated sibling paths."""

    id: str
    original_path: Path
    annotated_path: Path | None
    sidecar_path: Path | None
    display_name: str
    width: int
    height: int
    file_size: int
    source: CaptureSource
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        require_uuid_str(self.id, "id")
        object.__setattr__(
            self,
            "original_path",
            _require_absolute_path(self.original_path, "original_path"),
        )
        if self.annotated_path is not None:
            object.__setattr__(
                self,
                "annotated_path",
                _require_absolute_path(self.annotated_path, "annotated_path"),
            )
        else:
            require_optional_path(self.annotated_path, "annotated_path")
        if self.sidecar_path is not None:
            object.__setattr__(
                self, "sidecar_path", _require_absolute_path(self.sidecar_path, "sidecar_path")
            )
        else:
            require_optional_path(self.sidecar_path, "sidecar_path")
        require_non_empty_str(self.display_name, "display_name")
        require_non_negative_int(self.width, "width")
        require_non_negative_int(self.height, "height")
        require_non_negative_int(self.file_size, "file_size")
        require_enum(self.source, CaptureSource, "source")
        require_datetime(self.created_at, "created_at")
        require_datetime(self.updated_at, "updated_at")


@dataclass(frozen=True)
class CaptureRequest:
    """Short-lived interactive capture wait record."""

    id: str
    status: CaptureRequestStatus
    shot_id: str | None
    created_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        require_uuid_str(self.id, "id")
        require_enum(self.status, CaptureRequestStatus, "status")
        require_optional_str(self.shot_id, "shot_id")
        if self.shot_id is not None:
            require_uuid_str(self.shot_id, "shot_id")
        if self.status is CaptureRequestStatus.Completed and self.shot_id is None:
            raise ValidationError("shot_id is required when status is Completed")
        require_datetime(self.created_at, "created_at")
        require_datetime(self.expires_at, "expires_at")


__all__ = (
    "ANNOTATED_EXT",
    "ANNOTATED_FORMATS",
    "ANNOTATED_SUFFIXES",
    "Annotation",
    "AnnotatedFormat",
    "ArrowAnnotation",
    "BBox",
    "CAPTURE_MIN_EDGE_PX",
    "CAPTURE_REQUEST_TRANSITIONS",
    "CaptureRequest",
    "CaptureShot",
    "EraserAnnotation",
    "HighlightAnnotation",
    "ImageProbe",
    "PIXELATE_BLOCK_DEFAULT",
    "PIXELATE_BLOCK_MAX",
    "PIXELATE_BLOCK_MIN",
    "PixelateAnnotation",
    "RectAnnotation",
    "TextAnnotation",
)
