"""Download, SABR, and cookie routes. Static paths register before `/{id}`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, Response

from avkit_api.auth import require_bearer
from avkit_api.dependencies import get_download_service
from avkit_api.formatters import (
    audio_wire,
    format_eta,
    format_iso,
    format_speed,
    quality_wire,
    sabr_mode_wire,
    sabr_source_wire,
)
from avkit_api.schemas.common import EmptyIn, QueueRuntimeOut
from avkit_api.schemas.downloads import (
    ApplyDefaultsOut,
    CookieTestIn,
    CookieTestOut,
    DownloadCreateIn,
    DownloadCreateOut,
    DownloadJobOut,
    DownloadListOut,
    ReorderIn,
    SABRStatusOut,
)
from avkit_core.domain.enums import QueueProcessorState
from avkit_core.domain.errors import ConflictError
from avkit_core.domain.wire import AUDIO_WIRE_MAP, QUALITY_WIRE_MAP

router = APIRouter(prefix="/downloads", dependencies=[Depends(require_bearer)])


def _job_out(job: Any) -> DownloadJobOut:
    file_path = None if job.file_path is None else str(job.file_path)
    return DownloadJobOut(
        id=job.id,
        url=job.url,
        video_id=job.video_id,
        title=job.title,
        quality=quality_wire(job.quality),
        audio_only=job.audio_only,
        audio_format=audio_wire(job.audio_format),
        status=job.status.value,
        progress=job.progress,
        speed=format_speed(job.speed_bps),
        eta=format_eta(job.eta_seconds),
        file_size=job.file_size,
        file_path=file_path,
        error_message=job.error_message,
        queue_position=job.queue_position,
        created_at=format_iso(job.created_at),
        received_height=job.received_height,
    )


def _sabr_out(status: Any) -> SABRStatusOut:
    checked = None if status.checked_at is None else format_iso(status.checked_at)
    return SABRStatusOut(
        mode=sabr_mode_wire(status.mode),
        source=sabr_source_wire(status.source),
        checked_at=checked,
    )


@router.post("", status_code=201, response_model=DownloadCreateOut)
def create_downloads(
    body: DownloadCreateIn,
    download: Any = Depends(get_download_service),
) -> DownloadCreateOut:
    """Enqueue one URL as one or more download jobs."""
    jobs = download.add_to_queue(
        body.url,
        QUALITY_WIRE_MAP[body.quality],
        body.audio_only,
        AUDIO_WIRE_MAP[body.audio_format],
    )
    return DownloadCreateOut(items=[_job_out(job) for job in jobs])


@router.get("", response_model=DownloadListOut)
def list_downloads(download: Any = Depends(get_download_service)) -> DownloadListOut:
    """Return the queue plus processor snapshot."""
    runtime = download.get_processor_state()
    return DownloadListOut(
        items=[_job_out(job) for job in download.get_queue()],
        processor=QueueRuntimeOut(state=runtime.state.value, current_job_id=runtime.current_job_id),
    )


@router.get("/sabr", response_model=SABRStatusOut)
def get_sabr(download: Any = Depends(get_download_service)) -> SABRStatusOut:
    """Return the session SABR snapshot without running a check."""
    return _sabr_out(download.get_sabr_status())


@router.post("/sabr/check", response_model=SABRStatusOut)
def check_sabr(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> SABRStatusOut:
    """Run a SABR probe."""
    del body
    return _sabr_out(download.check_sabr())


@router.post("/sabr/force", response_model=SABRStatusOut)
def force_sabr(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> SABRStatusOut:
    """Force SABR active."""
    del body
    return _sabr_out(download.force_sabr())


@router.post("/sabr/clear", response_model=SABRStatusOut)
def clear_sabr(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> SABRStatusOut:
    """Clear SABR to inactive."""
    del body
    return _sabr_out(download.clear_sabr())


@router.post("/cookies/test", response_model=CookieTestOut)
def test_cookies(
    body: CookieTestIn,
    download: Any = Depends(get_download_service),
) -> CookieTestOut:
    """Probe cookies and return `{ok}` only."""
    path = None if body.cookie_file is None else Path(body.cookie_file)
    result = download.test_cookies(body.mode, body.browser, body.profile, path)
    return CookieTestOut(ok=result.ok)


@router.post("/start", status_code=202)
def start_downloads(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> Response:
    """Start the worker, or 409 when already Processing."""
    del body
    if download.get_processor_state().state is QueueProcessorState.Processing:
        raise ConflictError("download processor is already Processing")
    download.start_processing()
    return Response(status_code=202)


@router.post("/pause", status_code=202)
def pause_downloads(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> Response:
    """Pause the download worker."""
    del body
    download.pause_processing()
    return Response(status_code=202)


@router.post("/resume", status_code=202)
def resume_downloads(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> Response:
    """Resume from Paused."""
    del body
    download.resume_processing()
    return Response(status_code=202)


@router.post("/cancel", status_code=202)
def cancel_downloads(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> Response:
    """Cancel in-flight work."""
    del body
    download.cancel_processing()
    return Response(status_code=202)


@router.post("/stop", status_code=202)
def stop_downloads(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> Response:
    """Alias of cancel."""
    del body
    download.cancel_processing()
    return Response(status_code=202)


@router.post("/apply-defaults", response_model=ApplyDefaultsOut)
def apply_defaults(
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> ApplyDefaultsOut:
    """Apply current downloader defaults to pending rows."""
    del body
    return ApplyDefaultsOut(updated=download.apply_defaults_to_pending())


@router.put("/reorder", response_model=DownloadCreateOut)
def reorder_downloads(
    body: ReorderIn,
    download: Any = Depends(get_download_service),
) -> DownloadCreateOut:
    """Reorder the queue by a permutation of ids."""
    download.reorder_queue(body.job_ids)
    return DownloadCreateOut(items=[_job_out(job) for job in download.get_queue()])


@router.delete("", status_code=204)
def clear_downloads(download: Any = Depends(get_download_service)) -> Response:
    """Remove jobs only; archive stays."""
    download.clear_queue()
    return Response(status_code=204)


@router.get("/{id}", response_model=DownloadJobOut)
def get_download(id: str, download: Any = Depends(get_download_service)) -> DownloadJobOut:
    """Return one job."""
    return _job_out(download.get_job(id))


@router.post("/{id}/reset", response_model=DownloadJobOut)
def reset_download(
    id: str,
    body: EmptyIn | None = Body(default=None),
    download: Any = Depends(get_download_service),
) -> DownloadJobOut:
    """Re-queue a job from a re-queueable state."""
    del body
    return _job_out(download.reset_failed(id))


@router.delete("/{id}", status_code=204)
def delete_download(id: str, download: Any = Depends(get_download_service)) -> Response:
    """Remove one job. Files stay."""
    download.remove_from_queue(id)
    return Response(status_code=204)
