"""ORM row ↔ domain dataclass conversions."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import TypeVar

from avkit_core.domain.capture import CaptureRequest, CaptureShot
from avkit_core.domain.conversion import ConversionJob
from avkit_core.domain.download import DownloadArchiveEntry, DownloadJob
from avkit_core.domain.enums import (
    AudioEncodeMode,
    AudioFormat,
    CaptureRequestStatus,
    CaptureSource,
    ConversionKind,
    ConversionPresetId,
    ConversionStatus,
    CutCopyMode,
    DownloadStatus,
    MediaFormat,
    ModelFormat,
    ModelPrecision,
    QualityPreset,
    SettingValueType,
    TranscriptItemStatus,
    TranscriptStatus,
    TTSSourceKind,
    TTSStatus,
)
from avkit_core.domain.errors import ValidationError
from avkit_core.domain.settings import Setting
from avkit_core.domain.transcript import TranscriptItem, TranscriptJob
from avkit_core.domain.tts import TEXT_PREVIEW_MAX, ModelVariant, TTSJob
from avkit_infra.database.models import (
    CaptureRequestRow,
    CaptureShotRow,
    ConversionJobRow,
    DownloadArchiveRow,
    DownloadJobRow,
    ModelVariantRow,
    SettingRow,
    TranscriptItemRow,
    TranscriptJobRow,
    TTSJobRow,
)

EnumT = TypeVar("EnumT", bound=Enum)


def _enum_member(enum_cls: type[EnumT], name: str, field: str) -> EnumT:
    try:
        return enum_cls[name]
    except KeyError as exc:
        raise ValidationError(f"{field} must be a {enum_cls.__name__}") from exc


def _path_to_str(path: Path | None) -> str | None:
    if path is None:
        return None
    return str(path)


def _str_to_path(value: str | None) -> Path | None:
    if value is None:
        return None
    return Path(value)


def _as_bool(value: object, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    raise ValidationError(f"{field} must be bool")


def _truncate_preview(text: str) -> str:
    if len(text) <= TEXT_PREVIEW_MAX:
        return text
    return text[:TEXT_PREVIEW_MAX]


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _optional_enum(enum_cls: type[EnumT], name: str | None, field: str) -> EnumT | None:
    if name is None:
        return None
    return _enum_member(enum_cls, name, field)


def download_job_from_row(row: DownloadJobRow) -> DownloadJob:
    """Map a download_jobs row to a DownloadJob."""
    return DownloadJob(
        id=row.id,
        url=row.url,
        video_id=row.video_id,
        title=row.title,
        quality=_enum_member(QualityPreset, row.quality, "quality"),
        audio_only=_as_bool(row.audio_only, "audio_only"),
        audio_format=_enum_member(AudioFormat, row.audio_format, "audio_format"),
        status=_enum_member(DownloadStatus, row.status, "status"),
        progress=row.progress,
        speed_bps=row.speed_bps,
        eta_seconds=row.eta_seconds,
        file_size=row.file_size,
        file_path=_str_to_path(row.file_path),
        error_message=row.error_message,
        queue_position=row.queue_position,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def download_job_to_row(job: DownloadJob) -> DownloadJobRow:
    """Map a DownloadJob to a download_jobs row."""
    return DownloadJobRow(
        id=job.id,
        url=job.url,
        video_id=job.video_id,
        title=job.title,
        quality=job.quality.name,
        audio_only=job.audio_only,
        audio_format=job.audio_format.name,
        status=job.status.name,
        progress=job.progress,
        speed_bps=job.speed_bps,
        eta_seconds=job.eta_seconds,
        file_size=job.file_size,
        file_path=_path_to_str(job.file_path),
        error_message=job.error_message,
        queue_position=job.queue_position,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def apply_download_job(row: DownloadJobRow, job: DownloadJob) -> None:
    """Copy DownloadJob fields onto an existing row."""
    row.url = job.url
    row.video_id = job.video_id
    row.title = job.title
    row.quality = job.quality.name
    row.audio_only = job.audio_only
    row.audio_format = job.audio_format.name
    row.status = job.status.name
    row.progress = job.progress
    row.speed_bps = job.speed_bps
    row.eta_seconds = job.eta_seconds
    row.file_size = job.file_size
    row.file_path = _path_to_str(job.file_path)
    row.error_message = job.error_message
    row.queue_position = job.queue_position
    row.created_at = job.created_at
    row.updated_at = job.updated_at


def archive_entry_from_row(row: DownloadArchiveRow) -> DownloadArchiveEntry:
    """Map a download_archive row to a DownloadArchiveEntry."""
    return DownloadArchiveEntry(
        extractor=row.extractor,
        video_id=row.video_id,
        title=row.title,
        recorded_at=row.recorded_at,
    )


def archive_entry_to_row(entry: DownloadArchiveEntry) -> DownloadArchiveRow:
    """Map a DownloadArchiveEntry to a download_archive row."""
    return DownloadArchiveRow(
        extractor=entry.extractor,
        video_id=entry.video_id,
        title=entry.title,
        recorded_at=entry.recorded_at,
    )


def transcript_job_from_row(row: TranscriptJobRow) -> TranscriptJob:
    """Map a transcript_jobs row to a TranscriptJob."""
    return TranscriptJob(
        id=row.id,
        channel_url=row.channel_url,
        channel_name=row.channel_name,
        status=_enum_member(TranscriptStatus, row.status, "status"),
        output_dir=Path(row.output_dir),
        video_count=row.video_count,
        word_count=row.word_count,
        zip_path=_str_to_path(row.zip_path),
        queue_position=row.queue_position,
        error_message=row.error_message,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def transcript_job_to_row(job: TranscriptJob) -> TranscriptJobRow:
    """Map a TranscriptJob to a transcript_jobs row."""
    return TranscriptJobRow(
        id=job.id,
        channel_url=job.channel_url,
        channel_name=job.channel_name,
        status=job.status.name,
        output_dir=str(job.output_dir),
        video_count=job.video_count,
        word_count=job.word_count,
        zip_path=_path_to_str(job.zip_path),
        queue_position=job.queue_position,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def apply_transcript_job(row: TranscriptJobRow, job: TranscriptJob) -> None:
    """Copy TranscriptJob fields onto an existing row."""
    row.channel_url = job.channel_url
    row.channel_name = job.channel_name
    row.status = job.status.name
    row.output_dir = str(job.output_dir)
    row.video_count = job.video_count
    row.word_count = job.word_count
    row.zip_path = _path_to_str(job.zip_path)
    row.queue_position = job.queue_position
    row.error_message = job.error_message
    row.created_at = job.created_at
    row.updated_at = job.updated_at


def transcript_item_from_row(row: TranscriptItemRow) -> TranscriptItem:
    """Map a transcript_items row to a TranscriptItem."""
    return TranscriptItem(
        id=row.id,
        job_id=row.job_id,
        video_id=row.video_id,
        title=row.title,
        language=row.language,
        word_count=row.word_count,
        path=_str_to_path(row.path),
        status=_enum_member(TranscriptItemStatus, row.status, "status"),
        error_message=row.error_message,
        retry_count=row.retry_count,
        processed_at=row.processed_at,
    )


def transcript_item_to_row(item: TranscriptItem) -> TranscriptItemRow:
    """Map a TranscriptItem to a transcript_items row."""
    return TranscriptItemRow(
        id=item.id,
        job_id=item.job_id,
        video_id=item.video_id,
        title=item.title,
        language=item.language,
        word_count=item.word_count,
        path=_path_to_str(item.path),
        status=item.status.name,
        error_message=item.error_message,
        retry_count=item.retry_count,
        processed_at=item.processed_at,
    )


def apply_transcript_item(row: TranscriptItemRow, item: TranscriptItem) -> None:
    """Copy TranscriptItem fields onto an existing row."""
    row.job_id = item.job_id
    row.video_id = item.video_id
    row.title = item.title
    row.language = item.language
    row.word_count = item.word_count
    row.path = _path_to_str(item.path)
    row.status = item.status.name
    row.error_message = item.error_message
    row.retry_count = item.retry_count
    row.processed_at = item.processed_at


def tts_job_from_row(row: TTSJobRow) -> TTSJob:
    """Map a tts_jobs row to a TTSJob, truncating text_preview."""
    return TTSJob(
        id=row.id,
        source_kind=_enum_member(TTSSourceKind, row.source_kind, "source_kind"),
        source_path=_str_to_path(row.source_path),
        text_hash=row.text_hash,
        text_preview=_truncate_preview(row.text_preview),
        voice=row.voice,
        speed=row.speed,
        format=_enum_member(MediaFormat, row.format, "format"),
        status=_enum_member(TTSStatus, row.status, "status"),
        output_path=_str_to_path(row.output_path),
        segments_total=row.segments_total,
        segments_done=row.segments_done,
        error_message=row.error_message,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def tts_job_to_row(job: TTSJob) -> TTSJobRow:
    """Map a TTSJob to a tts_jobs row, truncating text_preview."""
    return TTSJobRow(
        id=job.id,
        source_kind=job.source_kind.name,
        source_path=_path_to_str(job.source_path),
        text_hash=job.text_hash,
        text_preview=_truncate_preview(job.text_preview),
        voice=job.voice,
        speed=job.speed,
        format=job.format.name,
        status=job.status.name,
        output_path=_path_to_str(job.output_path),
        segments_total=job.segments_total,
        segments_done=job.segments_done,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def apply_tts_job(row: TTSJobRow, job: TTSJob) -> None:
    """Copy TTSJob fields onto an existing row."""
    row.source_kind = job.source_kind.name
    row.source_path = _path_to_str(job.source_path)
    row.text_hash = job.text_hash
    row.text_preview = _truncate_preview(job.text_preview)
    row.voice = job.voice
    row.speed = job.speed
    row.format = job.format.name
    row.status = job.status.name
    row.output_path = _path_to_str(job.output_path)
    row.segments_total = job.segments_total
    row.segments_done = job.segments_done
    row.error_message = job.error_message
    row.created_at = job.created_at
    row.updated_at = job.updated_at


def model_variant_from_row(row: ModelVariantRow) -> ModelVariant:
    """Map a model_variants row to a ModelVariant."""
    return ModelVariant(
        id=row.id,
        name=row.name,
        format=_enum_member(ModelFormat, row.format, "format"),
        precision=_enum_member(ModelPrecision, row.precision, "precision"),
        size_bytes=row.size_bytes,
        path=_str_to_path(row.path),
        is_downloaded=_as_bool(row.is_downloaded, "is_downloaded"),
    )


def setting_from_row(row: SettingRow) -> Setting:
    """Map a settings row to a Setting."""
    return Setting(
        namespace=row.namespace,
        key=row.key,
        value=row.value,
        value_type=_enum_member(SettingValueType, row.value_type, "value_type"),
        updated_at=row.updated_at,
    )


def setting_to_row(setting: Setting) -> SettingRow:
    """Map a Setting to a settings row."""
    return SettingRow(
        namespace=setting.namespace,
        key=setting.key,
        value=setting.value,
        value_type=setting.value_type.name,
        updated_at=setting.updated_at,
    )


def apply_setting(row: SettingRow, setting: Setting) -> None:
    """Copy Setting fields onto an existing row."""
    row.value = setting.value
    row.value_type = setting.value_type.name
    row.updated_at = setting.updated_at


def conversion_job_from_row(row: ConversionJobRow) -> ConversionJob:
    """Map a conversion_jobs row to a ConversionJob."""
    return ConversionJob(
        id=row.id,
        kind=_enum_member(ConversionKind, row.kind, "kind"),
        input_path=Path(row.input_path),
        output_path=Path(row.output_path),
        display_name=row.display_name,
        preset_id=_optional_enum(ConversionPresetId, row.preset_id, "preset_id"),
        cq=row.cq,
        scale_height=row.scale_height,
        audio_mode=_optional_enum(AudioEncodeMode, row.audio_mode, "audio_mode"),
        gpu_encoder=row.gpu_encoder,
        in_ms=row.in_ms,
        out_ms=row.out_ms,
        copy_mode=_optional_enum(CutCopyMode, row.copy_mode, "copy_mode"),
        stream_index=row.stream_index,
        status=_enum_member(ConversionStatus, row.status, "status"),
        progress=row.progress,
        speed_bps=row.speed_bps,
        eta_seconds=row.eta_seconds,
        file_size=row.file_size,
        duration_seconds=row.duration_seconds,
        width=row.width,
        height=row.height,
        error_message=row.error_message,
        queue_position=row.queue_position,
        created_at=_as_utc(row.created_at),
        updated_at=_as_utc(row.updated_at),
    )


def conversion_job_to_row(job: ConversionJob) -> ConversionJobRow:
    """Map a ConversionJob to a conversion_jobs row."""
    return ConversionJobRow(
        id=job.id,
        kind=job.kind.name,
        input_path=str(job.input_path),
        output_path=str(job.output_path),
        display_name=job.display_name,
        preset_id=None if job.preset_id is None else job.preset_id.name,
        cq=job.cq,
        scale_height=job.scale_height,
        audio_mode=None if job.audio_mode is None else job.audio_mode.name,
        gpu_encoder=job.gpu_encoder,
        in_ms=job.in_ms,
        out_ms=job.out_ms,
        copy_mode=None if job.copy_mode is None else job.copy_mode.name,
        stream_index=job.stream_index,
        status=job.status.name,
        progress=job.progress,
        speed_bps=job.speed_bps,
        eta_seconds=job.eta_seconds,
        file_size=job.file_size,
        duration_seconds=job.duration_seconds,
        width=job.width,
        height=job.height,
        error_message=job.error_message,
        queue_position=job.queue_position,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def apply_conversion_job(row: ConversionJobRow, job: ConversionJob) -> None:
    """Copy ConversionJob fields onto an existing row."""
    row.kind = job.kind.name
    row.input_path = str(job.input_path)
    row.output_path = str(job.output_path)
    row.display_name = job.display_name
    row.preset_id = None if job.preset_id is None else job.preset_id.name
    row.cq = job.cq
    row.scale_height = job.scale_height
    row.audio_mode = None if job.audio_mode is None else job.audio_mode.name
    row.gpu_encoder = job.gpu_encoder
    row.in_ms = job.in_ms
    row.out_ms = job.out_ms
    row.copy_mode = None if job.copy_mode is None else job.copy_mode.name
    row.stream_index = job.stream_index
    row.status = job.status.name
    row.progress = job.progress
    row.speed_bps = job.speed_bps
    row.eta_seconds = job.eta_seconds
    row.file_size = job.file_size
    row.duration_seconds = job.duration_seconds
    row.width = job.width
    row.height = job.height
    row.error_message = job.error_message
    row.queue_position = job.queue_position
    row.created_at = job.created_at
    row.updated_at = job.updated_at


def capture_shot_from_row(row: CaptureShotRow) -> CaptureShot:
    """Map a capture_shots row to a CaptureShot."""
    return CaptureShot(
        id=row.id,
        original_path=Path(row.original_path),
        annotated_path=_str_to_path(row.annotated_path),
        sidecar_path=_str_to_path(row.sidecar_path),
        display_name=row.display_name,
        width=row.width,
        height=row.height,
        file_size=row.file_size,
        source=_enum_member(CaptureSource, row.source, "source"),
        created_at=_as_utc(row.created_at),
        updated_at=_as_utc(row.updated_at),
    )


def capture_shot_to_row(shot: CaptureShot) -> CaptureShotRow:
    """Map a CaptureShot to a capture_shots row."""
    return CaptureShotRow(
        id=shot.id,
        original_path=str(shot.original_path),
        annotated_path=_path_to_str(shot.annotated_path),
        sidecar_path=_path_to_str(shot.sidecar_path),
        display_name=shot.display_name,
        width=shot.width,
        height=shot.height,
        file_size=shot.file_size,
        source=shot.source.name,
        created_at=shot.created_at,
        updated_at=shot.updated_at,
    )


def apply_capture_shot(row: CaptureShotRow, shot: CaptureShot) -> None:
    """Copy CaptureShot fields onto an existing row."""
    row.original_path = str(shot.original_path)
    row.annotated_path = _path_to_str(shot.annotated_path)
    row.sidecar_path = _path_to_str(shot.sidecar_path)
    row.display_name = shot.display_name
    row.width = shot.width
    row.height = shot.height
    row.file_size = shot.file_size
    row.source = shot.source.name
    row.created_at = shot.created_at
    row.updated_at = shot.updated_at


def capture_request_from_row(row: CaptureRequestRow) -> CaptureRequest:
    """Map a capture_requests row to a CaptureRequest."""
    return CaptureRequest(
        id=row.id,
        status=_enum_member(CaptureRequestStatus, row.status, "status"),
        shot_id=row.shot_id,
        created_at=_as_utc(row.created_at),
        expires_at=_as_utc(row.expires_at),
    )


def capture_request_to_row(request: CaptureRequest) -> CaptureRequestRow:
    """Map a CaptureRequest to a capture_requests row."""
    return CaptureRequestRow(
        id=request.id,
        status=request.status.name,
        shot_id=request.shot_id,
        created_at=request.created_at,
        expires_at=request.expires_at,
    )


def apply_capture_request(row: CaptureRequestRow, request: CaptureRequest) -> None:
    """Copy CaptureRequest fields onto an existing row."""
    row.status = request.status.name
    row.shot_id = request.shot_id
    row.created_at = request.created_at
    row.expires_at = request.expires_at

