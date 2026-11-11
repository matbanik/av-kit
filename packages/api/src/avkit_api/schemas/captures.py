"""Capture REST request and response schemas."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, StrictFloat, StrictInt, StrictStr, model_validator

from avkit_api.schemas.common import ApiModel
from avkit_core.domain.capture import (
    CAPTURE_MIN_EDGE_PX,
    NAMED_COLORS,
    PIXELATE_BLOCK_DEFAULT,
    PIXELATE_BLOCK_MAX,
    PIXELATE_BLOCK_MIN,
    TEXT_MAX_CHARS,
)
from avkit_core.services.video_input import FRAMES_MAX, MAX_PATH_CHARS

RegisterSourceWire = Literal["hotkey", "gui", "scan"]
RequestStatusQueryWire = Literal["pending", "completed", "cancelled", "expired"]
ImageVariantWire = Literal["original", "annotated"]
_NAMED_COLOR = "|".join(sorted(NAMED_COLORS))
COLOR_PATTERN = rf"^#[0-9A-Fa-f]{{6}}$|^({_NAMED_COLOR})$"


class CaptureRegisterIn(ApiModel):
    """POST /captures body for mode=register."""

    mode: Literal["register"]
    path: str
    source: RegisterSourceWire


class CaptureFullscreenIn(ApiModel):
    """POST /captures body for mode=fullscreen."""

    mode: Literal["fullscreen"]


class CaptureRegionIn(ApiModel):
    """POST /captures body for mode=region."""

    mode: Literal["region"]
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=CAPTURE_MIN_EDGE_PX)
    height: int = Field(ge=CAPTURE_MIN_EDGE_PX)


class CaptureImportIn(ApiModel):
    """POST /captures body for mode=import."""

    mode: Literal["import"]
    path: str


CaptureCreateIn = Annotated[
    CaptureRegisterIn | CaptureFullscreenIn | CaptureRegionIn | CaptureImportIn,
    Field(discriminator="mode"),
]


class CaptureCompleteIn(ApiModel):
    """POST /captures/requests/{id}/complete body."""

    path: str = Field(min_length=1)


class ArrowAnnotationIn(ApiModel):
    """Arrow overlay."""

    type: Literal["arrow"]
    color: str = Field(pattern=COLOR_PATTERN)
    stroke_width: int
    from_xy: tuple[int, int] = Field(alias="from")
    to_xy: tuple[int, int] = Field(alias="to")


class RectAnnotationIn(ApiModel):
    """Stroke rectangle overlay."""

    type: Literal["rect"]
    x: int
    y: int
    width: int
    height: int
    color: str = Field(pattern=COLOR_PATTERN)
    stroke_width: int


class HighlightAnnotationIn(ApiModel):
    """Translucent fill overlay."""

    type: Literal["highlight"]
    x: int
    y: int
    width: int
    height: int
    color: str = Field(pattern=COLOR_PATTERN)
    opacity: float = Field(ge=0, le=1)


class TextAnnotationIn(ApiModel):
    """Text overlay."""

    type: Literal["text"]
    x: int
    y: int
    text: str = Field(min_length=1, max_length=TEXT_MAX_CHARS)
    color: str = Field(pattern=COLOR_PATTERN)
    font_size: int
    bg_color: str | None = Field(default=None, pattern=COLOR_PATTERN)


class PixelateAnnotationIn(ApiModel):
    """Pixelate region: a mosaic of ``block_size`` squares over the rectangle."""

    type: Literal["pixelate"]
    x: int
    y: int
    width: int
    height: int
    block_size: int = Field(
        default=PIXELATE_BLOCK_DEFAULT, ge=PIXELATE_BLOCK_MIN, le=PIXELATE_BLOCK_MAX
    )


class EraserAnnotationIn(ApiModel):
    """Eraser region: the rectangle filled with one colour sampled around it."""

    type: Literal["eraser"]
    x: int
    y: int
    width: int
    height: int


AnnotationIn = Annotated[
    ArrowAnnotationIn
    | RectAnnotationIn
    | HighlightAnnotationIn
    | TextAnnotationIn
    | PixelateAnnotationIn
    | EraserAnnotationIn,
    Field(discriminator="type"),
]


class AnnotateIn(ApiModel):
    """POST /captures/{id}/annotate body."""

    annotations: list[AnnotationIn]


class CaptureShotOut(ApiModel):
    """One capture catalog row. Paths are strings; no bytes."""

    id: str
    original_path: str
    annotated_path: str | None
    sidecar_path: str | None
    display_name: str
    width: int
    height: int
    file_size: int
    source: str
    created_at: str
    updated_at: str


class CaptureShotDetailOut(CaptureShotOut):
    """GET /captures/{id} includes validated sidecar annotations and the newest backup path."""

    annotations: list[AnnotationIn]
    backup_path: str | None


class CaptureListOut(ApiModel):
    """Catalog list. Not a queue — no processor key."""

    items: list[CaptureShotOut]


class CaptureItemOut(ApiModel):
    """POST /captures 201 envelope."""

    item: CaptureShotOut


class CaptureRequestOut(ApiModel):
    """Interactive capture wait row."""

    id: str
    status: str
    shot_id: str | None
    created_at: str
    expires_at: str


class CaptureRequestListOut(ApiModel):
    """Interactive request catalog."""

    items: list[CaptureRequestOut]


class CaptureCropIn(ApiModel):
    """POST /captures/{id}/crop body (MEU-130, CROP_REQUEST).

    The box has no bounds here: the service resolves it with REGION_RESOLVE, whose messages
    are the contract. `name` is checked by CROP_NAME.
    """

    x: float
    y: float
    width: float
    height: float
    unit: Literal["px", "fraction"] | None = None
    name: str | None = None


class CaptureCropRequestedOut(ApiModel):
    """The box as sent, with `unit` defaulting to px."""

    x: float
    y: float
    width: float
    height: float
    unit: Literal["px", "fraction"]


class CaptureCropAppliedOut(ApiModel):
    """The box that was cut, in source px after clamping."""

    x: int
    y: int
    width: int
    height: int


class CaptureCropMarksOut(ApiModel):
    """How the source's saved marks travelled: kept, clipped or dropped (MARK_CARRY)."""

    kept: int
    clipped: int
    dropped: int


class CaptureCropOut(ApiModel):
    """POST /captures/{id}/crop 201 (CROP_RESPONSE). No image bytes."""

    item: CaptureShotOut
    source_id: str
    requested: CaptureCropRequestedOut
    applied: CaptureCropAppliedOut
    clamped: bool
    marks: CaptureCropMarksOut


#: FRAMES_ROUTE: a time is seconds as a number, or text that TIME_PARSE reads.
TimeWire = StrictInt | StrictFloat | StrictStr


class CaptureFramesIn(ApiModel):
    """POST /captures/frames body (MEU-134, FRAMES_ROUTE): `at` times or a `count` of frames.

    `start` and `end` go with `count` only. Each time is read by TIME_PARSE in the service.
    """

    path: str = Field(min_length=1, max_length=MAX_PATH_CHARS)
    at: Annotated[list[TimeWire], Field(min_length=1, max_length=FRAMES_MAX)] | None = None
    count: Annotated[StrictInt, Field(ge=1, le=FRAMES_MAX)] | None = None
    start: TimeWire | None = None
    end: TimeWire | None = None

    @model_validator(mode="after")
    def _at_or_count(self) -> CaptureFramesIn:
        if (self.at is None) == (self.count is None):
            raise ValueError("use either at or count")
        if self.at is not None and (self.start is not None or self.end is not None):
            raise ValueError("start and end go with count")
        return self


class CaptureFramesVideoOut(ApiModel):
    """The video the frames came from (FRAMES_ROUTE); `duration_ms` is null for a raw stream."""

    path: str
    duration_ms: int | None
    width: int | None
    height: int | None
    fps: float | None


class CaptureFrameOut(ApiModel):
    """One new shot taken from the video, and the time it was taken at."""

    id: str
    path: str
    time_ms: int
    timecode: str
    width: int
    height: int


class CaptureFramesOut(ApiModel):
    """POST /captures/frames 201 (FRAMES_ROUTE). No image bytes."""

    video: CaptureFramesVideoOut
    frames: list[CaptureFrameOut]
