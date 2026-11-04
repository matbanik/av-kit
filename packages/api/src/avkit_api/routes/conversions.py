"""Conversion queue routes. Static paths register before the job-id path."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, Response

from avkit_api.auth import require_bearer
from avkit_api.dependencies import get_conversion_service
from avkit_api.formatters import (
    audio_encode_wire,
    conversion_kind_wire,
    conversion_preset_wire,
    cut_copy_wire,
    format_encode_speed,
    format_eta,
    format_iso,
)
from avkit_api.schemas.common import EmptyIn, QueueRuntimeOut
from avkit_api.schemas.conversions import (
    ConversionCompressIn,
    ConversionCreateIn,
    ConversionCreateOut,
    ConversionCutIn,
    ConversionExtractIn,
    ConversionJobOut,
    ConversionListOut,
    ConversionReorderIn,
    GPUCapabilitiesOut,
)
from avkit_core.domain.conversion import GPUCapabilities
from avkit_core.domain.enums import QueueProcessorState
from avkit_core.domain.errors import ConflictError, ValidationError
from avkit_core.domain.wire import (
    AUDIO_ENCODE_WIRE_MAP,
    COPY_WIRE_MAP,
    GPU_PREF_WIRE_MAP,
    KIND_WIRE_MAP,
    PRESET_WIRE_MAP,
)
from avkit_core.services.conversion import ConversionAddSpec

router = APIRouter(prefix="/conversions", dependencies=[Depends(require_bearer)])
_gpu_ensure_lock = threading.Lock()


def ensure_conversion_gpu(conversion: Any) -> GPUCapabilities:
    """Return the session GPU snapshot, probing once on a cold cache.

    Double-checks `get_gpu` under `_gpu_ensure_lock` before `detect_gpu`.
    Does not use `ConversionService._lock` (that lock is start_processing-only).
    """
    cached = conversion.get_gpu()
    if cached is not None:
        return cached
    with _gpu_ensure_lock:
        cached = conversion.get_gpu()
        if cached is not None:
            return cached
        return conversion.detect_gpu()


def _job_out(job: Any) -> ConversionJobOut:
    return ConversionJobOut(
        id=job.id,
        kind=conversion_kind_wire(job.kind),
        input_path=str(job.input_path),
        output_path=str(job.output_path),
        display_name=job.display_name,
        preset_id=conversion_preset_wire(job.preset_id),
        cq=job.cq,
        scale_height=job.scale_height,
        audio_mode=audio_encode_wire(job.audio_mode),
        gpu_encoder=job.gpu_encoder,
        in_ms=job.in_ms,
        out_ms=job.out_ms,
        copy_mode=cut_copy_wire(job.copy_mode),
        stream_index=job.stream_index,
        status=job.status.value,
        progress=job.progress,
        speed=format_encode_speed(job.speed_bps),
        eta=format_eta(job.eta_seconds),
        file_size=job.file_size,
        duration_seconds=job.duration_seconds,
        width=job.width,
        height=job.height,
        error_message=job.error_message,
        queue_position=job.queue_position,
        created_at=format_iso(job.created_at),
    )


def _gpu_out(gpu: GPUCapabilities) -> GPUCapabilitiesOut:
    checked = None if gpu.checked_at is None else format_iso(gpu.checked_at)
    return GPUCapabilitiesOut(
        nvidia_nvenc=gpu.nvidia_nvenc,
        amd_amf=gpu.amd_amf,
        intel_qsv=gpu.intel_qsv,
        vulkan=gpu.vulkan,
        software_h265=gpu.software_h265,
        software_h264=gpu.software_h264,
        recommended_encoder=gpu.recommended_encoder,
        checked_at=checked,
    )


def _existing_files(raw_paths: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute() or not path.is_file():
            raise ValidationError("each path must be an absolute existing file")
        resolved.append(path)
    return resolved


def _spec_from_body(
    body: ConversionCompressIn | ConversionCutIn | ConversionExtractIn,
) -> ConversionAddSpec:
    kind = KIND_WIRE_MAP[body.kind]
    if isinstance(body, ConversionCompressIn):
        audio = None if body.audio_mode is None else AUDIO_ENCODE_WIRE_MAP[body.audio_mode]
        gpu = None if body.gpu_preference is None else GPU_PREF_WIRE_MAP[body.gpu_preference]
        return ConversionAddSpec(
            kind=kind,
            preset_id=PRESET_WIRE_MAP[body.preset],
            cq=body.cq,
            scale_height=body.scale_height,
            audio_mode=audio,
            gpu_preference=gpu,
        )
    if isinstance(body, ConversionCutIn):
        return ConversionAddSpec(
            kind=kind,
            in_ms=body.in_ms,
            out_ms=body.out_ms,
            copy_mode=COPY_WIRE_MAP[body.copy_mode],
        )
    return ConversionAddSpec(
        kind=kind,
        stream_mode=body.stream_mode,
        stream_index=body.stream_index,
    )


@router.post("", status_code=201, response_model=ConversionCreateOut)
def create_conversions(
    body: ConversionCreateIn,
    conversion: Any = Depends(get_conversion_service),
) -> ConversionCreateOut:
    """Enqueue one or more conversion jobs."""
    paths = _existing_files(body.paths)
    jobs = conversion.add_to_queue(paths, _spec_from_body(body))
    return ConversionCreateOut(items=[_job_out(job) for job in jobs])


@router.get("", response_model=ConversionListOut)
def list_conversions(conversion: Any = Depends(get_conversion_service)) -> ConversionListOut:
    """Return the queue plus processor snapshot."""
    runtime = conversion.get_processor_state()
    return ConversionListOut(
        items=[_job_out(job) for job in conversion.get_queue()],
        processor=QueueRuntimeOut(state=runtime.state.value, current_job_id=runtime.current_job_id),
    )


@router.get("/gpu", response_model=GPUCapabilitiesOut)
def get_conversion_gpu(conversion: Any = Depends(get_conversion_service)) -> GPUCapabilitiesOut:
    """Return the session GPU snapshot, probing once when the cache is empty."""
    return _gpu_out(ensure_conversion_gpu(conversion))


@router.post("/gpu/refresh", response_model=GPUCapabilitiesOut)
def refresh_conversion_gpu(
    body: EmptyIn | None = Body(default=None),
    conversion: Any = Depends(get_conversion_service),
) -> GPUCapabilitiesOut:
    """Re-run the GPU probe."""
    del body
    return _gpu_out(conversion.detect_gpu())


@router.post("/start", status_code=202)
def start_conversions(
    body: EmptyIn | None = Body(default=None),
    conversion: Any = Depends(get_conversion_service),
) -> Response:
    """Start the worker, or 409 when already Processing."""
    del body
    if conversion.get_processor_state().state is QueueProcessorState.Processing:
        raise ConflictError("conversion processor is already Processing")
    conversion.start_processing()
    return Response(status_code=202)


@router.post("/pause", status_code=202)
def pause_conversions(
    body: EmptyIn | None = Body(default=None),
    conversion: Any = Depends(get_conversion_service),
) -> Response:
    """Pause after the current file."""
    del body
    conversion.pause_processing()
    return Response(status_code=202)


@router.post("/resume", status_code=202)
def resume_conversions(
    body: EmptyIn | None = Body(default=None),
    conversion: Any = Depends(get_conversion_service),
) -> Response:
    """Resume from Paused."""
    del body
    conversion.resume_processing()
    return Response(status_code=202)


@router.post("/cancel", status_code=202)
def cancel_conversions(
    body: EmptyIn | None = Body(default=None),
    conversion: Any = Depends(get_conversion_service),
) -> Response:
    """Cancel in-flight work."""
    del body
    conversion.cancel_processing()
    return Response(status_code=202)


@router.put("/reorder", response_model=ConversionCreateOut)
def reorder_conversions(
    body: ConversionReorderIn,
    conversion: Any = Depends(get_conversion_service),
) -> ConversionCreateOut:
    """Reorder the queue by a permutation of ids."""
    conversion.reorder_queue(body.job_ids)
    return ConversionCreateOut(items=[_job_out(job) for job in conversion.get_queue()])


@router.delete("", status_code=204)
def clear_conversions(conversion: Any = Depends(get_conversion_service)) -> Response:
    """Remove jobs only. Files stay."""
    conversion.clear_queue()
    return Response(status_code=204)


@router.get("/{id}", response_model=ConversionJobOut)
def get_conversion(id: str, conversion: Any = Depends(get_conversion_service)) -> ConversionJobOut:
    """Return one job."""
    return _job_out(conversion.get_job(id))


@router.post("/{id}/reset", response_model=ConversionJobOut)
def reset_conversion(
    id: str,
    body: EmptyIn | None = Body(default=None),
    conversion: Any = Depends(get_conversion_service),
) -> ConversionJobOut:
    """Re-queue a job from a re-queueable state."""
    del body
    return _job_out(conversion.reset_failed(id))


@router.delete("/{id}", status_code=204)
def delete_conversion(id: str, conversion: Any = Depends(get_conversion_service)) -> Response:
    """Remove one job. Files stay."""
    conversion.remove(id)
    return Response(status_code=204)
