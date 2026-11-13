"""Authenticated capture catalog routes. Static requests path registers before the shot-id path."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response

from avkit_api.auth import require_bearer
from avkit_api.dependencies import get_capture_service
from avkit_api.formatters import format_iso
from avkit_api.schemas.captures import (
    AnnotateIn,
    AnnotationIn,
    ArrowAnnotationIn,
    CaptureCompleteIn,
    CaptureCreateIn,
    CaptureCropAppliedOut,
    CaptureCropIn,
    CaptureCropMarksOut,
    CaptureCropOut,
    CaptureCropRequestedOut,
    CaptureExportIn,
    CaptureExportOut,
    CaptureExportShotOut,
    CaptureFrameOut,
    CaptureFramesIn,
    CaptureFramesOut,
    CaptureFramesVideoOut,
    CaptureFullscreenIn,
    CaptureImportIn,
    CaptureItemOut,
    CaptureListOut,
    CaptureRegionIn,
    CaptureRegisterIn,
    CaptureRequestListOut,
    CaptureRequestOut,
    CaptureSheetCellOut,
    CaptureSheetIn,
    CaptureSheetOut,
    CaptureSheetShotOut,
    CaptureShotDetailOut,
    CaptureShotOut,
    EraserAnnotationIn,
    HighlightAnnotationIn,
    PixelateAnnotationIn,
    RectAnnotationIn,
    RedactAnnotationIn,
    TextAnnotationIn,
)
from avkit_api.schemas.common import EmptyIn
from avkit_core.domain.capture import (
    Annotation,
    ArrowAnnotation,
    BBox,
    EraserAnnotation,
    HighlightAnnotation,
    PixelateAnnotation,
    RectAnnotation,
    RedactAnnotation,
    TextAnnotation,
    ViewFrame,
)
from avkit_core.domain.wire import REGISTER_SOURCE_WIRE_MAP, REQUEST_STATUS_QUERY_MAP
from avkit_core.services.capture import annotations_to_wire

IMAGE_MAX_BYTES = 15_728_640
IMAGE_MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
_REQUESTS_PATH = "/requests"
# OVERSIZE_HINT (MEU-128, D-411): the 413 names the two ways to a smaller image.
IMAGE_OVERSIZE_DETAIL = (
    "image exceeds IMAGE_MAX_BYTES; pass max_edge (64 to 2576) or a region for a smaller image"
)
# FRAME_HEADERS (MEU-128, D-411): every 200 from GET /captures/{id}/image carries the frame.
_FRAME_HEADER_DOCS: dict[str, Any] = {
    "X-Capture-Source": {
        "description": "The source image size in px: `W,H`.",
        "schema": {"type": "string"},
    },
    "X-Capture-Region": {
        "description": "The applied region in source px, after clamping: `x,y,width,height`.",
        "schema": {"type": "string"},
    },
    "X-Capture-Returned": {
        "description": "The returned image size in px: `width,height`.",
        "schema": {"type": "string"},
    },
    "X-Capture-Scale": {
        "description": "Returned px per source px, to 6 places. Source px = region.x + x / scale.",
        "schema": {"type": "string"},
    },
    "X-Capture-Clamped": {
        "description": "`true` when the region was cut to fit the image, else `false`.",
        "schema": {"type": "string"},
    },
}

router = APIRouter(prefix="/captures", dependencies=[Depends(require_bearer)])


def _shot_out(shot: Any) -> CaptureShotOut:
    annotated = shot.annotated_path
    sidecar = shot.sidecar_path
    return CaptureShotOut(
        id=shot.id,
        original_path=str(shot.original_path),
        annotated_path=None if annotated is None else str(annotated),
        sidecar_path=None if sidecar is None else str(sidecar),
        display_name=shot.display_name,
        width=shot.width,
        height=shot.height,
        file_size=shot.file_size,
        source=shot.source.value,
        created_at=format_iso(shot.created_at),
        updated_at=format_iso(shot.updated_at),
    )


def _shot_detail_out(
    shot: Any,
    annotations: list[Annotation],
    backup_path: Path | None,
) -> CaptureShotDetailOut:
    base = _shot_out(shot)
    # model_validate runs the same discriminated-union validation over the wire dicts that the
    # keyword constructor did at runtime, without asserting they are already AnnotationIn models.
    return CaptureShotDetailOut.model_validate(
        {
            **base.model_dump(),
            "annotations": annotations_to_wire(annotations),
            "backup_path": None if backup_path is None else str(backup_path),
        },
    )


def _detail_for(capture: Any, shot: Any) -> CaptureShotDetailOut:
    return _shot_detail_out(
        shot, capture.load_shot_annotations(shot.id), capture.latest_backup(shot.id)
    )


def _request_out(request: Any) -> CaptureRequestOut:
    return CaptureRequestOut(
        id=request.id,
        status=request.status.value,
        shot_id=request.shot_id,
        created_at=format_iso(request.created_at),
        expires_at=format_iso(request.expires_at),
    )


def _annotations_from_in(items: list[AnnotationIn]) -> list[Annotation]:
    parsed: list[Annotation] = []
    for item in items:
        if isinstance(item, ArrowAnnotationIn):
            parsed.append(
                ArrowAnnotation(
                    from_xy=item.from_xy,
                    to_xy=item.to_xy,
                    color=item.color,
                    stroke_width=item.stroke_width,
                )
            )
            continue
        if isinstance(item, RectAnnotationIn):
            parsed.append(
                RectAnnotation(
                    x=item.x,
                    y=item.y,
                    width=item.width,
                    height=item.height,
                    color=item.color,
                    stroke_width=item.stroke_width,
                )
            )
            continue
        if isinstance(item, HighlightAnnotationIn):
            parsed.append(
                HighlightAnnotation(
                    x=item.x,
                    y=item.y,
                    width=item.width,
                    height=item.height,
                    color=item.color,
                    opacity=item.opacity,
                )
            )
            continue
        if isinstance(item, TextAnnotationIn):
            parsed.append(
                TextAnnotation(
                    x=item.x,
                    y=item.y,
                    text=item.text,
                    color=item.color,
                    font_size=item.font_size,
                    bg_color=item.bg_color,
                )
            )
            continue
        if isinstance(item, PixelateAnnotationIn):
            parsed.append(
                PixelateAnnotation(
                    x=item.x,
                    y=item.y,
                    width=item.width,
                    height=item.height,
                    block_size=item.block_size,
                )
            )
            continue
        if isinstance(item, EraserAnnotationIn):
            parsed.append(
                EraserAnnotation(x=item.x, y=item.y, width=item.width, height=item.height)
            )
            continue
        if isinstance(item, RedactAnnotationIn):
            parsed.append(
                RedactAnnotation(
                    x=item.x, y=item.y, width=item.width, height=item.height, color=item.color
                )
            )
            continue
    return parsed


def _image_media_type(path: Path) -> str:
    return IMAGE_MIME_MAP.get(path.suffix.lower(), "application/octet-stream")


def _frame_headers(frame: ViewFrame) -> dict[str, str]:
    return {
        "X-Capture-Source": f"{frame.source_width},{frame.source_height}",
        "X-Capture-Region": f"{frame.x},{frame.y},{frame.width},{frame.height}",
        "X-Capture-Returned": f"{frame.returned_width},{frame.returned_height}",
        "X-Capture-Scale": f"{frame.scale:.6f}",
        "X-Capture-Clamped": "true" if frame.clamped else "false",
    }


def _whole_frame(width: int, height: int) -> ViewFrame:
    return ViewFrame(
        source_width=width,
        source_height=height,
        x=0,
        y=0,
        width=width,
        height=height,
        returned_width=width,
        returned_height=height,
        scale=1.0,
        clamped=False,
    )


@router.get("", response_model=CaptureListOut)
def list_captures(capture: Any = Depends(get_capture_service)) -> CaptureListOut:
    """Return the inbox catalog. Not a queue."""
    shots = capture.list_shots()
    return CaptureListOut(items=[_shot_out(item) for item in shots])


@router.post("", status_code=201, response_model=CaptureItemOut)
def create_capture(
    body: CaptureCreateIn,
    capture: Any = Depends(get_capture_service),
) -> CaptureItemOut:
    """Register an inbox file or grab fullscreen/region."""
    if isinstance(body, CaptureRegisterIn):
        shot = capture.register_shot(Path(body.path), REGISTER_SOURCE_WIRE_MAP[body.source])
    elif isinstance(body, CaptureFullscreenIn):
        shot = capture.capture_fullscreen()
    elif isinstance(body, CaptureRegionIn):
        shot = capture.capture_region(
            BBox(x=body.x, y=body.y, width=body.width, height=body.height)
        )
    elif isinstance(body, CaptureImportIn):
        # IMPORT_MODE (MEU-129, D-415): copy or register a local image; the source is only read.
        shot = capture.import_image(Path(body.path))
    else:
        raise HTTPException(status_code=422, detail="unknown capture mode")
    return CaptureItemOut(item=_shot_out(shot))


@router.get(_REQUESTS_PATH, response_model=CaptureRequestListOut)
def list_capture_requests(
    status: Literal["pending", "completed", "cancelled", "expired"] | None = Query(default=None),
    capture: Any = Depends(get_capture_service),
) -> CaptureRequestListOut:
    """Expire stale rows, then list interactive requests."""
    mapped = None if status is None else REQUEST_STATUS_QUERY_MAP[status]
    rows = capture.list_requests(status=mapped)
    return CaptureRequestListOut(items=[_request_out(item) for item in rows])


@router.post(_REQUESTS_PATH, status_code=201, response_model=CaptureRequestOut)
def create_capture_request(
    body: EmptyIn | None = Body(default=None),
    capture: Any = Depends(get_capture_service),
) -> CaptureRequestOut:
    """Create a pending overlay wait. Second pending is 409."""
    del body
    return _request_out(capture.request_interactive())


@router.post("/requests/{id}/complete", response_model=CaptureRequestOut)
def complete_capture_request(
    id: str,
    body: CaptureCompleteIn,
    capture: Any = Depends(get_capture_service),
) -> CaptureRequestOut:
    """Register the overlay PNG and complete the request in one UoW."""
    return _request_out(capture.complete_request(id, Path(body.path)))


@router.post("/requests/{id}/cancel", response_model=CaptureRequestOut)
def cancel_capture_request(
    id: str,
    body: EmptyIn | None = Body(default=None),
    capture: Any = Depends(get_capture_service),
) -> CaptureRequestOut:
    """Cancel a pending overlay wait."""
    del body
    return _request_out(capture.cancel_request(id))


@router.post("/frames", status_code=201, response_model=CaptureFramesOut)
def capture_frames(
    body: CaptureFramesIn,
    capture: Any = Depends(get_capture_service),
) -> CaptureFramesOut:
    """FRAMES_ROUTE (MEU-134): stills from a local video, each a new shot with source Video."""
    result = capture.frames_from_video(
        body.path, at=body.at, count=body.count, start=body.start, end=body.end
    )
    video = result.video
    return CaptureFramesOut(
        video=CaptureFramesVideoOut(
            path=video.path,
            duration_ms=video.duration_ms,
            width=video.width,
            height=video.height,
            fps=video.fps,
        ),
        frames=[
            CaptureFrameOut(
                id=frame.id,
                path=frame.path,
                time_ms=frame.time_ms,
                timecode=frame.timecode,
                width=frame.width,
                height=frame.height,
            )
            for frame in result.frames
        ],
    )


@router.post("/sheet", status_code=201, response_model=CaptureSheetOut)
def capture_sheet(
    body: CaptureSheetIn,
    capture: Any = Depends(get_capture_service),
) -> CaptureSheetOut:
    """SHEET_ROUTE (MEU-135): one labelled grid of a span of a local video, as a new shot."""
    result = capture.sheet_from_video(
        body.path, start=body.start, end=body.end, grid=body.grid, max_edge=body.max_edge
    )
    video = result.video
    shot = result.shot
    return CaptureSheetOut(
        video=CaptureFramesVideoOut(
            path=video.path,
            duration_ms=video.duration_ms,
            width=video.width,
            height=video.height,
            fps=video.fps,
        ),
        shot=CaptureSheetShotOut(id=shot.id, path=shot.path, width=shot.width, height=shot.height),
        spacing_ms=result.spacing_ms,
        cells=[
            CaptureSheetCellOut(cell=cell.cell, time_ms=cell.time_ms, timecode=cell.timecode)
            for cell in result.cells
        ],
    )


@router.get("/{id}", response_model=CaptureShotDetailOut)
def get_capture(id: str, capture: Any = Depends(get_capture_service)) -> CaptureShotDetailOut:
    """Return shot metadata plus sidecar annotations. Bytes are on GET /image."""
    return _detail_for(capture, capture.get_shot(id))


@router.get("/{id}/image", responses={200: {"headers": _FRAME_HEADER_DOCS}})
def get_capture_image(
    id: str,
    variant: Literal["original", "annotated"] = Query(default="original"),
    x: float | None = Query(default=None),
    y: float | None = Query(default=None),
    width: float | None = Query(default=None),
    height: float | None = Query(default=None),
    unit: Literal["px", "fraction"] | None = Query(default=None),
    max_edge: int | None = Query(default=None),
    capture: Any = Depends(get_capture_service),
) -> Response:
    """Return original or annotated image bytes."""
    # MEU-128 (D-411): with none of x, y, width, height, unit and max_edge, the file's bytes
    # are returned unchanged; the five X-Capture-* headers give the frame either way. The
    # region fields have no ge or le: the domain's messages are the contract.
    shot = capture.get_shot(id)
    if all(value is None for value in (x, y, width, height, unit, max_edge)):
        payload = capture.read_image(id, variant)
        frame = _whole_frame(shot.width, shot.height)
    else:
        payload, frame = capture.read_image_view(
            id,
            variant,
            x=x,
            y=y,
            width=width,
            height=height,
            unit=unit,
            max_edge=max_edge,
        )
    if len(payload) > IMAGE_MAX_BYTES:
        raise HTTPException(status_code=413, detail=IMAGE_OVERSIZE_DETAIL)
    media_path = shot.original_path
    if variant == "annotated":
        annotated = shot.annotated_path
        if annotated is None:
            raise HTTPException(status_code=404, detail="annotated image is missing")
        media_path = annotated
    return Response(
        content=payload,
        media_type=_image_media_type(media_path),
        headers=_frame_headers(frame),
    )


@router.post("/{id}/annotate", response_model=CaptureShotOut)
def annotate_capture(
    id: str,
    body: AnnotateIn,
    capture: Any = Depends(get_capture_service),
) -> CaptureShotOut:
    """Bake annotations or clear them when the array is empty."""
    return _shot_out(capture.annotate_and_save(id, _annotations_from_in(body.annotations)))


@router.post("/{id}/flatten", response_model=CaptureShotDetailOut)
def flatten_capture(
    id: str,
    body: EmptyIn | None = Body(default=None),
    capture: Any = Depends(get_capture_service),
) -> CaptureShotDetailOut:
    """Bake saved marks into the original after a backup; a JPEG/WebP shot gets a new PNG copy."""
    del body
    return _detail_for(capture, capture.flatten(id))


@router.post("/{id}/revert", response_model=CaptureShotDetailOut)
def revert_capture(
    id: str,
    body: EmptyIn | None = Body(default=None),
    capture: Any = Depends(get_capture_service),
) -> CaptureShotDetailOut:
    """Restore the newest backup over the original; the backup file is kept."""
    del body
    return _detail_for(capture, capture.revert(id))


@router.post("/{id}/crop", status_code=201, response_model=CaptureCropOut)
def crop_capture(
    id: str,
    body: CaptureCropIn,
    capture: Any = Depends(get_capture_service),
) -> CaptureCropOut:
    """Cut a region into a new PNG shot (source `Crop`); the source is never changed."""
    result = capture.crop_shot(
        id,
        x=body.x,
        y=body.y,
        width=body.width,
        height=body.height,
        unit=body.unit,
        name=body.name,
    )
    req_x, req_y, req_width, req_height, req_unit = result.requested
    left, top, width, height = result.applied
    return CaptureCropOut(
        item=_shot_out(result.shot),
        source_id=result.source_id,
        requested=CaptureCropRequestedOut(
            x=req_x, y=req_y, width=req_width, height=req_height, unit=req_unit
        ),
        applied=CaptureCropAppliedOut(x=left, y=top, width=width, height=height),
        clamped=result.clamped,
        marks=CaptureCropMarksOut(
            kept=result.kept, clipped=result.clipped, dropped=result.dropped
        ),
    )


@router.post("/{id}/export", status_code=201, response_model=CaptureExportOut)
def export_capture(
    id: str,
    body: CaptureExportIn,
    capture: Any = Depends(get_capture_service),
) -> CaptureExportOut:
    """Write a resized or re-encoded copy as a new shot (source `Export`); the source is kept."""
    result = capture.export_shot(
        id, fmt=body.format, max_edge=body.max_edge, quality=body.quality
    )
    shot = result.shot
    return CaptureExportOut(
        shot=CaptureExportShotOut(
            id=shot.id,
            path=str(shot.original_path),
            width=shot.width,
            height=shot.height,
            bytes=result.bytes,
        ),
        source_id=result.source_id,
    )


@router.delete("/{id}", status_code=204)
def delete_capture(id: str, capture: Any = Depends(get_capture_service)) -> Response:
    """Delete the shot row and its files."""
    capture.remove(id)
    return Response(status_code=204)
