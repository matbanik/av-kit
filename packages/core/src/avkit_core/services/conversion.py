"""ConversionService — sequential one-FFmpeg worker over conversion_jobs."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import structlog

from avkit_core.domain.conversion import (
    CutOptions,
    ExtractOptions,
    GPUCapabilities,
    StreamInfo,
    VideoEncodeOptions,
    builtin_conversion_presets,
)
from avkit_core.domain.enums import (
    AudioEncodeMode,
    ConversionKind,
    ConversionPresetId,
    ConversionStatus,
    CutCopyMode,
    GpuPreference,
    QueueProcessorState,
)
from avkit_core.domain.errors import (
    ConflictError,
    FilesystemError,
    GpuUnavailableError,
    MediaProbeError,
    NotFoundError,
    ValidationError,
)
from avkit_core.domain.progress import MediaInfo, ProgressSnapshot
from avkit_core.domain.queue import QueueRuntime
from avkit_core.ports.media import MediaPort
from avkit_core.ports.storage import UnitOfWork
from avkit_core.services.settings import SettingsService

UoWFactory = Callable[[], UnitOfWork]
log = structlog.get_logger(module="convert")

KIND_TOKEN: dict[ConversionKind, str] = {
    ConversionKind.Compress: "compress",
    ConversionKind.Cut: "cut",
    ConversionKind.Extract: "a",
}
EXTRACT_CONTAINER_MAP: dict[str, str] = {
    "pcm": ".wav",
    "aac": ".m4a",
    "ac3": ".ac3",
    "eac3": ".eac3",
    "opus": ".opus",
    "vorbis": ".oga",
    "mp3": ".mp3",
    "mp2": ".mp2",
    "wma": ".wma",
}
EXTRACT_UNKNOWN_EXT = ".mka"
COMPRESS_EXT = ".mp4"
PRESET_WIRE: dict[str, ConversionPresetId] = {
    "archival": ConversionPresetId.Archival,
    "high_quality": ConversionPresetId.HighQuality,
    "balanced": ConversionPresetId.Balanced,
    "sharing": ConversionPresetId.Sharing,
    "mobile": ConversionPresetId.Mobile,
}
GPU_WIRE: dict[str, GpuPreference] = {
    "auto": GpuPreference.Auto,
    "nvidia": GpuPreference.Nvidia,
    "amd": GpuPreference.Amd,
    "intel": GpuPreference.Intel,
    "software": GpuPreference.Software,
}


def _now() -> datetime:
    return datetime.now(UTC)


def _preset_by_id(preset_id: ConversionPresetId):
    for item in builtin_conversion_presets():
        if item.preset_id is preset_id:
            return item
    raise ValidationError("unknown conversion preset")


@dataclass(frozen=True)
class ConversionAddSpec:
    """Add-to-queue request. Unexpected fields are rejected by the dataclass."""

    kind: ConversionKind
    preset_id: ConversionPresetId | None = None
    cq: int | None = None
    scale_height: int | None = None
    audio_mode: AudioEncodeMode | None = None
    gpu_preference: GpuPreference | None = None
    in_ms: int | None = None
    out_ms: int | None = None
    copy_mode: CutCopyMode | None = None
    stream_mode: str | None = None
    stream_index: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ConversionKind):
            raise ValidationError("kind must be a ConversionKind")
        if self.stream_mode is not None and self.stream_mode not in {"first", "all"}:
            raise ValidationError("stream_mode must be first or all")
        if self.kind is ConversionKind.Cut and (self.in_ms is None or self.out_ms is None):
            raise ValidationError("Cut jobs require in_ms and out_ms")


class ConversionService:
    """Conversion queue owner. One FFmpeg process at a time."""

    def __init__(
        self,
        uow_factory: UoWFactory,
        *,
        media: MediaPort,
        settings: SettingsService,
    ) -> None:
        self._uow_factory = uow_factory
        self._media = media
        self._settings = settings
        self._runtime = QueueRuntime(
            queue_name="conversions",
            state=QueueProcessorState.Idle,
            current_job_id=None,
        )
        self._pause = False
        self._cancel = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._gpu: GPUCapabilities | None = None

    def should_stop(self) -> bool:
        return self._cancel

    def get_queue(self):
        with self._uow_factory() as uow:
            return uow.conversion_jobs.list_ordered()

    def get_job(self, job_id: str):
        with self._uow_factory() as uow:
            job = uow.conversion_jobs.get(job_id)
        if job is None:
            raise NotFoundError(f"conversion job {job_id} not found")
        return job

    def get_processor_state(self) -> QueueRuntime:
        return self._runtime

    def detect_gpu(self) -> GPUCapabilities:
        self._gpu = self._media.detect_gpu()
        return self._gpu

    def get_gpu(self) -> GPUCapabilities | None:
        return self._gpu

    def add_to_queue(self, paths: list[Path], spec: ConversionAddSpec):
        if not isinstance(paths, list) or not paths:
            raise ValidationError("paths must be a non-empty list")
        created = []
        reserved: set[Path] = set()
        with self._uow_factory() as uow:
            position = len(uow.conversion_jobs.list_ordered())
            for path in paths:
                if not isinstance(path, Path):
                    raise ValidationError("paths must contain Path values")
                for job in self._jobs_for_path(path, spec, position, reserved):
                    uow.conversion_jobs.add(job)
                    created.append(job)
                    reserved.add(job.output_path)
                    position += 1
            uow.commit()
        return created

    def start_processing(self) -> None:
        with self._lock:
            if self._runtime.state is QueueProcessorState.Processing:
                raise ConflictError("conversion already processing")
            self._pause = False
            self._cancel = False
            self._runtime = QueueRuntime(
                queue_name="conversions",
                state=QueueProcessorState.Processing,
                current_job_id=self._runtime.current_job_id,
            )
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._worker, daemon=True)
                self._thread.start()

    def pause_processing(self) -> None:
        self._pause = True

    def resume_processing(self) -> None:
        if self._runtime.state is not QueueProcessorState.Paused:
            raise ConflictError("resume_processing requires Paused")
        self.start_processing()

    def cancel_processing(self) -> None:
        self._cancel = True

    def reorder_queue(self, job_ids: list[str]) -> None:
        with self._uow_factory() as uow:
            current = [job.id for job in uow.conversion_jobs.list_ordered()]
            if sorted(job_ids) != sorted(current):
                raise ValidationError("reorder_queue requires a permutation of current ids")
            uow.conversion_jobs.reorder(job_ids)
            uow.commit()

    def remove(self, job_id: str) -> None:
        with self._uow_factory() as uow:
            if uow.conversion_jobs.get(job_id) is None:
                raise NotFoundError(f"conversion job {job_id} not found")
            uow.conversion_jobs.delete(job_id)
            uow.commit()

    def clear_queue(self) -> None:
        with self._uow_factory() as uow:
            uow.conversion_jobs.delete_all()
            uow.commit()

    def reset_failed(self, job_id: str):
        with self._uow_factory() as uow:
            job = uow.conversion_jobs.get(job_id)
            if job is None:
                raise NotFoundError(f"conversion job {job_id} not found")
            updated = job.reset_failed()
            uow.conversion_jobs.save(updated)
            uow.commit()
        return updated

    def _jobs_for_path(
        self,
        path: Path,
        spec: ConversionAddSpec,
        position: int,
        reserved: set[Path],
    ) -> list:
        from avkit_core.domain.conversion import ConversionJob

        display = path.name
        info: MediaInfo | None = None
        probe_error: str | None = None
        try:
            info = self._media.probe(path)
        except (MediaProbeError, FilesystemError, OSError, ValidationError) as exc:
            probe_error = str(exc) or "probe failed"
        plans = self._expand_plans(spec, info)
        jobs = []
        for offset, plan in enumerate(plans):
            output, skipped = self._resolve_output(
                path,
                spec.kind,
                plan,
                info,
                reserved,
                include_stream_index=(
                    spec.kind is ConversionKind.Extract
                    and spec.stream_mode == "all"
                    and len(plans) > 1
                ),
            )
            status = ConversionStatus.Skipped if skipped else ConversionStatus.Pending
            if probe_error is not None:
                status = ConversionStatus.Failed
            preset_id, cq, scale_height, audio_mode = self._compress_fields(spec)
            job = ConversionJob(
                id=str(uuid4()),
                kind=spec.kind,
                input_path=path,
                output_path=output,
                display_name=display,
                preset_id=preset_id if spec.kind is ConversionKind.Compress else None,
                cq=cq if spec.kind is ConversionKind.Compress else spec.cq,
                scale_height=scale_height if spec.kind is ConversionKind.Compress else None,
                audio_mode=audio_mode if spec.kind is ConversionKind.Compress else None,
                gpu_encoder=None,
                in_ms=spec.in_ms if spec.kind is ConversionKind.Cut else None,
                out_ms=spec.out_ms if spec.kind is ConversionKind.Cut else None,
                copy_mode=(
                    spec.copy_mode or CutCopyMode.FastCopy
                    if spec.kind is ConversionKind.Cut
                    else None
                ),
                stream_index=plan.get("stream_index"),
                status=status,
                progress=0.0,
                speed_bps=None,
                eta_seconds=None,
                file_size=None if info is None else None,
                duration_seconds=None if info is None else info.duration,
                width=None if info is None else info.width,
                height=None if info is None else info.height,
                error_message=probe_error,
                queue_position=position + offset,
                created_at=_now(),
                updated_at=_now(),
            )
            jobs.append(job)
            reserved.add(output)
        return jobs

    def _expand_plans(
        self,
        spec: ConversionAddSpec,
        info: MediaInfo | None,
    ) -> list[dict[str, int | None]]:
        if spec.kind is not ConversionKind.Extract:
            return [{"stream_index": spec.stream_index}]
        if spec.stream_mode == "all" and info is not None and info.streams:
            audio = [
                stream
                for stream in info.streams
                if isinstance(stream, StreamInfo) and stream.codec_type == "audio"
            ]
            if audio:
                return [{"stream_index": stream.index} for stream in audio]
        index = spec.stream_index if spec.stream_index is not None else 0
        return [{"stream_index": index}]

    def _compress_fields(self, spec: ConversionAddSpec):
        if spec.kind is not ConversionKind.Compress:
            return None, spec.cq, spec.scale_height, spec.audio_mode
        preset_id = spec.preset_id
        if preset_id is None:
            wire = str(self._settings.get("converter", "default_preset"))
            preset_id = PRESET_WIRE.get(wire, ConversionPresetId.Balanced)
        preset = _preset_by_id(preset_id)
        cq = spec.cq if spec.cq is not None else preset.cq
        scale_height = spec.scale_height if spec.scale_height is not None else preset.scale_height
        audio_mode = spec.audio_mode if spec.audio_mode is not None else preset.audio_mode
        return preset_id, cq, scale_height, audio_mode

    def _resolve_output(
        self,
        path: Path,
        kind: ConversionKind,
        plan: dict[str, int | None],
        info: MediaInfo | None,
        reserved: set[Path],
        include_stream_index: bool = False,
    ) -> tuple[Path, bool]:
        raw_dir = str(self._settings.get("converter", "output_dir"))
        dest_dir = Path(raw_dir).expanduser()
        token = KIND_TOKEN[kind]
        ext = self._output_ext(kind, path, plan, info)
        skip = bool(self._settings.get("converter", "skip_existing"))
        stream_token = ""
        if include_stream_index and plan.get("stream_index") is not None:
            stream_token = str(plan["stream_index"])
        candidate = dest_dir / f"{path.stem}_{token}{stream_token}{ext}"
        if candidate.exists() and candidate not in reserved and skip:
            return candidate, True
        suffix = 1
        while candidate.exists() or candidate in reserved:
            candidate = dest_dir / f"{path.stem}_{token}{stream_token}_{suffix}{ext}"
            suffix += 1
        return candidate, False

    def _output_ext(
        self,
        kind: ConversionKind,
        path: Path,
        plan: dict[str, int | None],
        info: MediaInfo | None,
    ) -> str:
        if kind is ConversionKind.Compress:
            return COMPRESS_EXT
        if kind is ConversionKind.Cut:
            return path.suffix or COMPRESS_EXT
        codec = "unknown"
        if info is not None and info.streams:
            index = plan.get("stream_index")
            for stream in info.streams:
                if isinstance(stream, StreamInfo) and stream.index == index:
                    codec = stream.codec_name
                    break
        elif info is not None and info.audio_codec:
            codec = info.audio_codec
        return EXTRACT_CONTAINER_MAP.get(codec, EXTRACT_UNKNOWN_EXT)

    def _preference(self) -> GpuPreference:
        wire = str(self._settings.get("converter", "gpu_preference"))
        return GPU_WIRE.get(wire, GpuPreference.Auto)

    def _resolve_encoder(self, caps: GPUCapabilities) -> str:
        preference = self._preference()
        if preference is GpuPreference.Auto:
            return caps.recommended_encoder
        if preference is GpuPreference.Nvidia:
            return "hevc_nvenc" if caps.nvidia_nvenc else caps.recommended_encoder
        if preference is GpuPreference.Amd:
            return "hevc_amf" if caps.amd_amf else caps.recommended_encoder
        if preference is GpuPreference.Intel:
            return "hevc_qsv" if caps.intel_qsv else caps.recommended_encoder
        if caps.software_h265:
            return "libx265"
        if caps.software_h264:
            return "libx264"
        raise GpuUnavailableError("software encoder unavailable")

    def _worker(self) -> None:
        try:
            while True:
                if self._cancel:
                    self._cancel_inflight()
                    break
                if self._pause:
                    self._runtime = QueueRuntime(
                        queue_name="conversions",
                        state=QueueProcessorState.Paused,
                        current_job_id=None,
                    )
                    break
                job = self._next_pending()
                if job is None:
                    self._runtime = QueueRuntime(
                        queue_name="conversions",
                        state=QueueProcessorState.Idle,
                        current_job_id=None,
                    )
                    break
                self._run_one(job)
        finally:
            if self._cancel:
                self._runtime = QueueRuntime(
                    queue_name="conversions",
                    state=QueueProcessorState.Idle,
                    current_job_id=None,
                )
                self._cancel = False

    def _next_pending(self):
        with self._uow_factory() as uow:
            pending = [
                job
                for job in uow.conversion_jobs.list_ordered()
                if job.status is ConversionStatus.Pending
            ]
        return pending[0] if pending else None

    def _run_one(self, job) -> None:
        with self._uow_factory() as uow:
            latest = uow.conversion_jobs.get(job.id)
            if latest is None or latest.status is not ConversionStatus.Pending:
                return
            processing = replace(
                latest.transition(ConversionStatus.Processing),
                updated_at=_now(),
            )
            uow.conversion_jobs.save(processing)
            uow.commit()
        self._runtime = QueueRuntime(
            queue_name="conversions",
            state=QueueProcessorState.Processing,
            current_job_id=job.id,
        )
        try:
            self._dispatch(processing)
        except Exception as exc:
            if self._cancel:
                self._cancel_inflight()
                return
            self._finish(job.id, ConversionStatus.Failed, error=str(exc))
            return
        if self._cancel:
            self._cancel_inflight()
            return
        self._finish(job.id, ConversionStatus.Done, progress=1.0)

    def _dispatch(self, job) -> None:
        caps = self._gpu or self.detect_gpu()
        encoder = self._resolve_encoder(caps)
        with self._uow_factory() as uow:
            latest = uow.conversion_jobs.get(job.id)
            if latest is None:
                return
            latest = replace(latest, gpu_encoder=encoder, updated_at=_now())
            uow.conversion_jobs.save(latest)
            uow.commit()

        def _on_progress(snapshot: ProgressSnapshot) -> None:
            with self._uow_factory() as uow:
                current = uow.conversion_jobs.get(job.id)
                if current is None:
                    return
                uow.conversion_jobs.save(
                    replace(
                        current,
                        progress=snapshot.fraction,
                        speed_bps=snapshot.rate,
                        eta_seconds=snapshot.eta_seconds,
                        updated_at=_now(),
                    )
                )
                uow.commit()

        if job.kind is ConversionKind.Compress:
            preset = _preset_by_id(job.preset_id or ConversionPresetId.Balanced)
            probed = self._media.probe(job.input_path)
            options = VideoEncodeOptions(
                codec=encoder,
                cq=job.cq if job.cq is not None else preset.cq,
                nvenc_preset=preset.nvenc_preset,
                scale_height=job.scale_height,
                audio_mode=job.audio_mode or preset.audio_mode,
                hwaccel=None,
                bit_depth=probed.bit_depth,
                duration_seconds=job.duration_seconds or probed.duration,
            )
            self._media.encode(
                job.input_path,
                job.output_path,
                options,
                _on_progress,
                self.should_stop,
            )
            return
        if job.kind is ConversionKind.Cut:
            if job.in_ms is None or job.out_ms is None:
                raise ValidationError("Cut jobs require in_ms and out_ms")
            self._media.cut(
                job.input_path,
                job.output_path,
                CutOptions(
                    in_ms=job.in_ms,
                    out_ms=job.out_ms,
                    copy_mode=job.copy_mode or CutCopyMode.FastCopy,
                ),
                _on_progress,
                self.should_stop,
            )
            return
        self._media.extract_stream(
            job.input_path,
            job.output_path,
            ExtractOptions(
                stream_index=job.stream_index if job.stream_index is not None else 0,
                output_container=job.output_path.suffix.lstrip(".") or "m4a",
            ),
            _on_progress,
            self.should_stop,
        )

    def _finish(
        self,
        job_id: str,
        status: ConversionStatus,
        error: str | None = None,
        progress: float | None = None,
    ) -> None:
        with self._uow_factory() as uow:
            latest = uow.conversion_jobs.get(job_id)
            if latest is None:
                return
            payload = latest.transition(status)
            uow.conversion_jobs.save(
                replace(
                    payload,
                    error_message=error,
                    progress=progress if progress is not None else payload.progress,
                    updated_at=_now(),
                )
            )
            uow.commit()
        self._runtime = QueueRuntime(
            queue_name="conversions",
            state=self._runtime.state,
            current_job_id=None,
        )

    def _cancel_inflight(self) -> None:
        job_id = self._runtime.current_job_id
        if job_id is None:
            return
        with self._uow_factory() as uow:
            latest = uow.conversion_jobs.get(job_id)
            if latest is None:
                return
            if latest.status is ConversionStatus.Processing:
                uow.conversion_jobs.save(
                    replace(
                        latest.transition(ConversionStatus.Cancelled),
                        updated_at=_now(),
                    )
                )
                uow.commit()
