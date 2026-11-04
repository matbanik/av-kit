"""Conversion jobs, presets, GPU session VO, and encode DTOs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path

from avkit_core.domain.enums import (
    AudioEncodeMode,
    ConversionKind,
    ConversionPresetId,
    ConversionStatus,
    CutCopyMode,
)
from avkit_core.domain.errors import (
    ConflictError,
    InvalidTimeRangeError,
    ValidationError,
    require_datetime,
    require_enum,
    require_fraction,
    require_non_empty_str,
    require_non_negative_int,
    require_optional_datetime,
    require_optional_non_negative_float,
    require_optional_non_negative_int,
    require_optional_str,
    require_path,
    require_uuid_str,
)
from avkit_core.domain.progress import CONVERT_OPTIONS_FIELDS as CONVERT_OPTIONS_FIELDS

CONVERSION_TRANSITIONS: dict[ConversionStatus, frozenset[ConversionStatus]] = {
    ConversionStatus.Pending: frozenset(
        {
            ConversionStatus.Processing,
            ConversionStatus.Failed,
            ConversionStatus.Skipped,
        }
    ),
    ConversionStatus.Processing: frozenset(
        {
            ConversionStatus.Done,
            ConversionStatus.Failed,
            ConversionStatus.Cancelled,
            ConversionStatus.Skipped,
        }
    ),
    ConversionStatus.Failed: frozenset({ConversionStatus.Pending}),
    ConversionStatus.Done: frozenset(),
    ConversionStatus.Cancelled: frozenset({ConversionStatus.Pending}),
    ConversionStatus.Skipped: frozenset(),
}
REQUEUEABLE_CONVERSION_STATUSES: frozenset[ConversionStatus] = frozenset(
    {
        ConversionStatus.Failed,
        ConversionStatus.Cancelled,
    }
)


def _require_time_range(in_ms: int, out_ms: int) -> None:
    if in_ms < 0 or out_ms < 0 or out_ms <= in_ms:
        raise InvalidTimeRangeError("out_ms must be greater than in_ms and both must be >= 0")


@dataclass(frozen=True)
class StreamInfo:
    """One probed media stream."""

    index: int
    codec_type: str
    codec_name: str
    language: str | None
    channels: int | None
    sample_rate: int | None

    def __post_init__(self) -> None:
        require_non_negative_int(self.index, "index")
        require_non_empty_str(self.codec_type, "codec_type")
        require_non_empty_str(self.codec_name, "codec_name")
        require_optional_str(self.language, "language")
        require_optional_non_negative_int(self.channels, "channels")
        require_optional_non_negative_int(self.sample_rate, "sample_rate")


@dataclass(frozen=True)
class FFmpegBinaries:
    """The resolved ffmpeg and the ffprobe found beside it or on PATH."""

    ffmpeg: Path
    ffprobe: Path | None


@dataclass(frozen=True)
class GPUCapabilities:
    """Session GPU/encoder snapshot. Not a table."""

    nvidia_nvenc: bool
    amd_amf: bool
    intel_qsv: bool
    vulkan: bool
    software_h265: bool
    software_h264: bool
    recommended_encoder: str
    checked_at: datetime | None

    def __post_init__(self) -> None:
        for name in (
            "nvidia_nvenc",
            "amd_amf",
            "intel_qsv",
            "vulkan",
            "software_h265",
            "software_h264",
        ):
            value = getattr(self, name)
            if not isinstance(value, bool):
                raise ValidationError(f"{name} must be bool")
        require_non_empty_str(self.recommended_encoder, "recommended_encoder")
        require_optional_datetime(self.checked_at, "checked_at")


@dataclass(frozen=True)
class ConversionPreset:
    """Built-in compress preset. Frozen catalog row, not a table."""

    preset_id: ConversionPresetId
    cq: int
    audio_mode: AudioEncodeMode
    nvenc_preset: str
    scale_height: int | None
    description: str

    def __post_init__(self) -> None:
        require_enum(self.preset_id, ConversionPresetId, "preset_id")
        require_non_negative_int(self.cq, "cq")
        require_enum(self.audio_mode, AudioEncodeMode, "audio_mode")
        require_non_empty_str(self.nvenc_preset, "nvenc_preset")
        require_optional_non_negative_int(self.scale_height, "scale_height")
        require_non_empty_str(self.description, "description")


def builtin_conversion_presets() -> tuple[ConversionPreset, ...]:
    """Return the five built-in compress presets. Default id is Balanced."""
    return (
        ConversionPreset(
            preset_id=ConversionPresetId.Archival,
            cq=18,
            audio_mode=AudioEncodeMode.Copy,
            nvenc_preset="p7",
            scale_height=None,
            description="Maximum quality, larger files",
        ),
        ConversionPreset(
            preset_id=ConversionPresetId.HighQuality,
            cq=22,
            audio_mode=AudioEncodeMode.Aac128,
            nvenc_preset="p4",
            scale_height=None,
            description="Personal library",
        ),
        ConversionPreset(
            preset_id=ConversionPresetId.Balanced,
            cq=25,
            audio_mode=AudioEncodeMode.Aac128,
            nvenc_preset="p4",
            scale_height=None,
            description="Best quality-to-size",
        ),
        ConversionPreset(
            preset_id=ConversionPresetId.Sharing,
            cq=28,
            audio_mode=AudioEncodeMode.Aac128,
            nvenc_preset="p4",
            scale_height=None,
            description="Smaller, still watchable",
        ),
        ConversionPreset(
            preset_id=ConversionPresetId.Mobile,
            cq=30,
            audio_mode=AudioEncodeMode.Aac96,
            nvenc_preset="p4",
            scale_height=720,
            description="Small files",
        ),
    )


@dataclass(frozen=True)
class VideoEncodeOptions:
    """Compress encode options for MediaPort.encode."""

    codec: str
    cq: int
    nvenc_preset: str
    scale_height: int | None
    audio_mode: AudioEncodeMode
    hwaccel: str | None
    bit_depth: int | None = None
    duration_seconds: float | None = None

    def __post_init__(self) -> None:
        require_non_empty_str(self.codec, "codec")
        require_non_negative_int(self.cq, "cq")
        require_non_empty_str(self.nvenc_preset, "nvenc_preset")
        require_optional_non_negative_int(self.scale_height, "scale_height")
        require_enum(self.audio_mode, AudioEncodeMode, "audio_mode")
        require_optional_str(self.hwaccel, "hwaccel")
        require_optional_non_negative_int(self.bit_depth, "bit_depth")
        require_optional_non_negative_float(self.duration_seconds, "duration_seconds")


@dataclass(frozen=True)
class CutOptions:
    """Cut range and copy/reencode mode."""

    in_ms: int
    out_ms: int
    copy_mode: CutCopyMode

    def __post_init__(self) -> None:
        if not isinstance(self.in_ms, int) or isinstance(self.in_ms, bool):
            raise InvalidTimeRangeError("in_ms must be an int")
        if not isinstance(self.out_ms, int) or isinstance(self.out_ms, bool):
            raise InvalidTimeRangeError("out_ms must be an int")
        _require_time_range(self.in_ms, self.out_ms)
        require_enum(self.copy_mode, CutCopyMode, "copy_mode")


@dataclass(frozen=True)
class ExtractOptions:
    """Extract one audio stream to a container."""

    stream_index: int
    output_container: str

    def __post_init__(self) -> None:
        require_non_negative_int(self.stream_index, "stream_index")
        require_non_empty_str(self.output_container, "output_container")


@dataclass(frozen=True)
class ConversionJob:
    """One conversion queue row."""

    id: str
    kind: ConversionKind
    input_path: Path
    output_path: Path
    display_name: str
    preset_id: ConversionPresetId | None
    cq: int | None
    scale_height: int | None
    audio_mode: AudioEncodeMode | None
    gpu_encoder: str | None
    in_ms: int | None
    out_ms: int | None
    copy_mode: CutCopyMode | None
    stream_index: int | None
    status: ConversionStatus
    progress: float
    speed_bps: float | None
    eta_seconds: int | None
    file_size: int | None
    duration_seconds: float | None
    width: int | None
    height: int | None
    error_message: str | None
    queue_position: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        require_uuid_str(self.id, "id")
        require_enum(self.kind, ConversionKind, "kind")
        require_path(self.input_path, "input_path")
        require_path(self.output_path, "output_path")
        require_non_empty_str(self.display_name, "display_name")
        if self.preset_id is not None:
            require_enum(self.preset_id, ConversionPresetId, "preset_id")
        require_optional_non_negative_int(self.cq, "cq")
        require_optional_non_negative_int(self.scale_height, "scale_height")
        if self.audio_mode is not None:
            require_enum(self.audio_mode, AudioEncodeMode, "audio_mode")
        require_optional_str(self.gpu_encoder, "gpu_encoder")
        require_optional_non_negative_int(self.in_ms, "in_ms")
        require_optional_non_negative_int(self.out_ms, "out_ms")
        if self.copy_mode is not None:
            require_enum(self.copy_mode, CutCopyMode, "copy_mode")
        require_optional_non_negative_int(self.stream_index, "stream_index")
        require_enum(self.status, ConversionStatus, "status")
        require_fraction(self.progress, "progress")
        require_optional_non_negative_float(self.speed_bps, "speed_bps")
        require_optional_non_negative_int(self.eta_seconds, "eta_seconds")
        require_optional_non_negative_int(self.file_size, "file_size")
        require_optional_non_negative_float(self.duration_seconds, "duration_seconds")
        require_optional_non_negative_int(self.width, "width")
        require_optional_non_negative_int(self.height, "height")
        require_optional_str(self.error_message, "error_message")
        require_non_negative_int(self.queue_position, "queue_position")
        require_datetime(self.created_at, "created_at")
        require_datetime(self.updated_at, "updated_at")
        if self.kind is ConversionKind.Compress and (
            self.in_ms is not None or self.out_ms is not None
        ):
            raise ValidationError("Compress jobs must not set in_ms or out_ms")
        if self.kind is ConversionKind.Cut:
            if self.in_ms is None or self.out_ms is None:
                raise InvalidTimeRangeError("Cut jobs require in_ms and out_ms")
            _require_time_range(self.in_ms, self.out_ms)

    def transition(self, new_status: ConversionStatus) -> ConversionJob:
        """Return a copy with `new_status` when the edge is allowed."""
        require_enum(new_status, ConversionStatus, "new_status")
        allowed = CONVERSION_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise ConflictError(
                f"illegal conversion transition {self.status.value} -> {new_status.value}"
            )
        return replace(self, status=new_status)

    def reset_failed(self) -> ConversionJob:
        """Map a re-queueable status -> Pending and clear error_message plus progress."""
        if self.status not in REQUEUEABLE_CONVERSION_STATUSES:
            allowed = ", ".join(sorted(status.value for status in REQUEUEABLE_CONVERSION_STATUSES))
            raise ConflictError(f"reset_failed is only valid from {allowed}")
        return replace(
            self.transition(ConversionStatus.Pending),
            error_message=None,
            progress=0.0,
        )
