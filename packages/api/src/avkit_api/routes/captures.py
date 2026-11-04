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
    CaptureFullscreenIn,
    CaptureItemOut,
    CaptureListOut,
    CaptureRegionIn,
    CaptureRegisterIn,
    CaptureRequestListOut,
    CaptureRequestOut,
    CaptureShotDetailOut,
    CaptureShotOut,
    EraserAnnotationIn,
    HighlightAnnotationIn,
    PixelateAnnotationIn,
    RectAnnotationIn,
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
    TextAnnotation,
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
    return parsed


def _image_media_type(path: Path) -> str:
    return IMAGE_MIME_MAP.get(path.suffix.lower(), "application/octet-stream")


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


@router.get("/{id}", response_model=CaptureShotDetailOut)
def get_capture(id: str, capture: Any = Depends(get_capture_service)) -> CaptureShotDetailOut:
    """Return shot metadata plus sidecar annotations. Bytes are on GET /image."""
    return _detail_for(capture, capture.get_shot(id))


@router.get("/{id}/image")
def get_capture_image(
    id: str,
    variant: Literal["original", "annotated"] = Query(default="original"),
    capture: Any = Depends(get_capture_service),
) -> Response:
    """Return original or annotated image bytes."""
    shot = capture.get_shot(id)
    payload = capture.read_image(id, variant)
    if len(payload) > IMAGE_MAX_BYTES:
        raise HTTPException(status_code=413, detail="image exceeds IMAGE_MAX_BYTES")
    media_path = shot.original_path
    if variant == "annotated":
        annotated = shot.annotated_path
        if annotated is None:
            raise HTTPException(status_code=404, detail="annotated image is missing")
        media_path = annotated
    return Response(content=payload, media_type=_image_media_type(media_path))


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


@router.delete("/{id}", status_code=204)
def delete_capture(id: str, capture: Any = Depends(get_capture_service)) -> Response:
    """Delete the shot row and its files."""
    capture.remove(id)
    return Response(status_code=204)
