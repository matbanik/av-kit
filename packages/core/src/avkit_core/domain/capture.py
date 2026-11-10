"""Capture inbox entities, annotation value objects, and geometry."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, replace
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Literal, TypeVar, assert_never

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
# REGION_VIEW (MEU-128, D-409, D-426): a view's longest returned edge, and the upscale cap.
REGION_MAX_EDGE_DEFAULT = 1568
REGION_MAX_EDGE_MIN = 64
REGION_MAX_EDGE_MAX = 2576
REGION_UPSCALE_MAX = 4
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
class ViewFrame:
    """The frame of a region view (MEU-128): source size, applied region, returned size."""

    source_width: int
    source_height: int
    x: int
    y: int
    width: int
    height: int
    returned_width: int
    returned_height: int
    scale: float
    clamped: bool


RegionUnit = Literal["px", "fraction"]


def resolve_region(
    source_width: int,
    source_height: int,
    x: float,
    y: float,
    width: float,
    height: float,
    unit: RegionUnit,
) -> tuple[int, int, int, int, bool]:
    """REGION_RESOLVE (MEU-128, D-407, D-408): a region in original px, clamped to the image.

    Returns ``(left, top, width, height, clamped)``. The caller has already checked that the
    four values are finite (``view_frame``).
    """
    values = (x, y, width, height)
    if x < 0 or y < 0:
        raise ValidationError("x and y must be 0 or more")
    if width <= 0 or height <= 0:
        raise ValidationError("width and height must be more than 0")
    if unit == "px":
        if not all(float(value).is_integer() for value in values):
            raise ValidationError(
                "with unit px, x, y, width and height are whole pixels; "
                'use unit: "fraction" for parts of the image'
            )
        # Python ints before any sum, so 1e308 + 1e308 stays exact and finite.
        left, top = int(x), int(y)
        right, bottom = left + int(width), top + int(height)
    else:
        if any(value > 1 for value in values):
            raise ValidationError(
                "with unit fraction, x, y, width and height are between 0 and 1"
            )
        # The 9-place guard (D-408) drops binary error before floor and ceil.
        left = math.floor(round(x * source_width, 9))
        top = math.floor(round(y * source_height, 9))
        right = math.ceil(round((x + width) * source_width, 9))
        bottom = math.ceil(round((y + height) * source_height, 9))
    if left >= source_width or top >= source_height:
        raise ValidationError(
            f"region starts outside the image, which is {source_width}x{source_height} px"
        )
    clamped = right > source_width or bottom > source_height
    right, bottom = min(right, source_width), min(bottom, source_height)
    region_width, region_height = right - left, bottom - top
    if region_width < CAPTURE_MIN_EDGE_PX or region_height < CAPTURE_MIN_EDGE_PX:
        raise ValidationError(
            f"region is {region_width}x{region_height} px after clamping to the image; "
            f"each edge must be at least {CAPTURE_MIN_EDGE_PX} px"
        )
    return (left, top, region_width, region_height, clamped)


def view_scale(width: int, height: int, max_edge: int, *, upscale: bool) -> float:
    """VIEW_SCALE (MEU-128, D-409): fit the longest edge to ``max_edge``.

    A region may be enlarged up to ``REGION_UPSCALE_MAX``; a whole image only shrinks.
    """
    return min(max_edge / max(width, height), REGION_UPSCALE_MAX if upscale else 1)


def _returned_edge(edge: int, scale: float) -> int:
    """A returned edge: half rounds up, and never below 1 px."""
    return max(1, math.floor(edge * scale + 0.5))


def view_frame(
    source_width: int,
    source_height: int,
    *,
    x: float | None = None,
    y: float | None = None,
    width: float | None = None,
    height: float | None = None,
    unit: RegionUnit | None = None,
    max_edge: int | None = None,
) -> ViewFrame:
    """The frame of a region view (MEU-128): REGION_ERRORS, then REGION_RESOLVE and VIEW_SCALE."""
    fields = (x, y, width, height)
    given = [value is not None for value in fields]
    if any(given) and not all(given):
        raise ValidationError("x, y, width and height go together: give all four or none")
    has_region = all(given)
    if unit is not None and not has_region:
        raise ValidationError("unit needs x, y, width and height")
    if max_edge is not None and not REGION_MAX_EDGE_MIN <= max_edge <= REGION_MAX_EDGE_MAX:
        raise ValidationError(
            f"max_edge must be between {REGION_MAX_EDGE_MIN} and {REGION_MAX_EDGE_MAX}"
        )
    if x is not None and y is not None and width is not None and height is not None:
        if not all(math.isfinite(value) for value in (x, y, width, height)):
            raise ValidationError("x, y, width and height must be finite numbers")
        left, top, region_width, region_height, clamped = resolve_region(
            source_width, source_height, x, y, width, height, unit or "px"
        )
        edge = REGION_MAX_EDGE_DEFAULT if max_edge is None else max_edge
        scale = view_scale(region_width, region_height, edge, upscale=True)
    else:
        left, top, region_width, region_height, clamped = (
            0,
            0,
            source_width,
            source_height,
            False,
        )
        scale = (
            1.0
            if max_edge is None
            else view_scale(source_width, source_height, max_edge, upscale=False)
        )
    return ViewFrame(
        source_width=source_width,
        source_height=source_height,
        x=left,
        y=top,
        width=region_width,
        height=region_height,
        returned_width=_returned_edge(region_width, scale),
        returned_height=_returned_edge(region_height, scale),
        scale=scale,
        clamped=clamped,
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

MarkCarry = Literal["kept", "clipped", "dropped"]


def clip_mark(
    mark: Annotation, left: int, top: int, width: int, height: int
) -> tuple[Annotation | None, MarkCarry]:
    """MARK_CARRY: move a saved mark into a crop's frame and clip it to the crop (MEU-130).

    The crop is `(left, top, width, height)` in the source's original pixels. The result is
    a new mark (the input is never changed) and how it was carried; a dropped mark is `None`.
    Every returned mark is a fixed point of the service's `_clamp_annotation` (D-485).
    """
    match mark:
        case ArrowAnnotation():
            return _clip_arrow(mark, left, top, width, height)
        case RectAnnotation():
            return _clip_rect(mark, left, top, width, height)
        case HighlightAnnotation():
            return _clip_half_open(mark, left, top, width, height)
        case PixelateAnnotation():
            return _clip_half_open(mark, left, top, width, height)
        case EraserAnnotation():
            return _clip_half_open(mark, left, top, width, height)
        case TextAnnotation():
            return _clip_text(mark, left, top, width, height)
        case _:
            assert_never(mark)


_HalfOpenMark = TypeVar(
    "_HalfOpenMark", HighlightAnnotation, PixelateAnnotation, EraserAnnotation
)


def _clip_half_open(
    mark: _HalfOpenMark, left: int, top: int, width: int, height: int
) -> tuple[_HalfOpenMark | None, MarkCarry]:
    """MARK_CLIP_BOX: highlight, pixelate and eraser cover `[x, x+w) x [y, y+h)` (D-486)."""
    x0, y0 = mark.x - left, mark.y - top
    x1, y1 = x0 + mark.width, y0 + mark.height
    if mark.width == 0 or mark.height == 0:
        # Draws nothing: kept while its origin is inside, as the clamp would leave it.
        if 0 <= x0 < width and 0 <= y0 < height:
            return replace(mark, x=x0, y=y0), "kept"
        return None, "dropped"
    if x0 >= 0 and y0 >= 0 and x1 <= width and y1 <= height:
        return replace(mark, x=x0, y=y0), "kept"
    cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, width), min(y1, height)
    if cx0 >= cx1 or cy0 >= cy1:
        return None, "dropped"
    return replace(mark, x=cx0, y=cy0, width=cx1 - cx0, height=cy1 - cy0), "clipped"


def _clip_rect(
    mark: RectAnnotation, left: int, top: int, width: int, height: int
) -> tuple[RectAnnotation | None, MarkCarry]:
    """MARK_CLIP_BOX: a rect's outline covers `[x, x+w] x [y, y+h]`, a line when w or h is 0."""
    x0, y0 = mark.x - left, mark.y - top
    x1, y1 = x0 + mark.width, y0 + mark.height
    right, bottom = width - 1, height - 1
    if x0 >= 0 and y0 >= 0 and x1 <= right and y1 <= bottom:
        return replace(mark, x=x0, y=y0), "kept"
    cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, right), min(y1, bottom)
    if cx0 > cx1 or cy0 > cy1:
        return None, "dropped"
    return replace(mark, x=cx0, y=cy0, width=cx1 - cx0, height=cy1 - cy0), "clipped"


def _clip_text(
    mark: TextAnnotation, left: int, top: int, width: int, height: int
) -> tuple[TextAnnotation | None, MarkCarry]:
    """MARK_CLIP_TEXT: kept when its anchor is in `[0, width) x [0, height)`; never clipped."""
    x0, y0 = mark.x - left, mark.y - top
    if 0 <= x0 < width and 0 <= y0 < height:
        return replace(mark, x=x0, y=y0), "kept"
    return None, "dropped"


def _round_half_up(value: Fraction, hi: int) -> int:
    return min(max(math.floor(value + 0.5), 0), hi)


def _clip_arrow(
    mark: ArrowAnnotation, left: int, top: int, width: int, height: int
) -> tuple[ArrowAnnotation | None, MarkCarry]:
    """MARK_CLIP_ARROW: Liang-Barsky against the closed `[0, width] x [0, height]` (D-487).

    The parameters are exact fractions, so an end that lands on a half pixel rounds up in
    either direction (round 1 F2): a float could fall just below the tie.
    """
    x0, y0 = mark.from_xy[0] - left, mark.from_xy[1] - top
    x1, y1 = mark.to_xy[0] - left, mark.to_xy[1] - top
    if 0 <= x0 <= width and 0 <= y0 <= height and 0 <= x1 <= width and 0 <= y1 <= height:
        return replace(mark, from_xy=(x0, y0), to_xy=(x1, y1)), "kept"
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = Fraction(0), Fraction(1)
    for p, q in ((-dx, x0), (dx, width - x0), (-dy, y0), (dy, height - y0)):
        if p == 0:
            if q < 0:
                return None, "dropped"
            continue
        r = Fraction(q) / p
        if p < 0:
            if r > t1:
                return None, "dropped"
            t0 = max(t0, r)
        else:
            if r < t0:
                return None, "dropped"
            t1 = min(t1, r)
    start = (_round_half_up(x0 + t0 * dx, width), _round_half_up(y0 + t0 * dy, height))
    end = (_round_half_up(x0 + t1 * dx, width), _round_half_up(y0 + t1 * dy, height))
    if start == end:
        return None, "dropped"
    return replace(mark, from_xy=start, to_xy=end), "clipped"


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


@dataclass(frozen=True)
class CropResult:
    """A crop's new shot, its boxes and its mark counts (MEU-130, CROP_RESPONSE).

    `requested` is the box as sent with its unit; `applied` is `(left, top, width, height)`
    in original pixels after `resolve_region`.
    """

    shot: CaptureShot
    source_id: str
    requested: tuple[float, float, float, float, RegionUnit]
    applied: tuple[int, int, int, int]
    clamped: bool
    kept: int
    clipped: int
    dropped: int


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
    "CropResult",
    "EraserAnnotation",
    "HighlightAnnotation",
    "ImageProbe",
    "MarkCarry",
    "PIXELATE_BLOCK_DEFAULT",
    "PIXELATE_BLOCK_MAX",
    "PIXELATE_BLOCK_MIN",
    "PixelateAnnotation",
    "REGION_MAX_EDGE_DEFAULT",
    "REGION_MAX_EDGE_MAX",
    "REGION_MAX_EDGE_MIN",
    "REGION_UPSCALE_MAX",
    "RectAnnotation",
    "RegionUnit",
    "TextAnnotation",
    "ViewFrame",
    "clip_mark",
    "resolve_region",
    "view_frame",
    "view_scale",
)
