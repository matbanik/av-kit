"""Shared progress snapshots, error info, and media DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from avkit_core.domain.errors import (
    ValidationError,
    require_fraction,
    require_non_empty_str,
    require_non_negative_int,
    require_optional_non_negative_float,
    require_optional_non_negative_int,
    require_optional_str,
)

FRACTION_MIN = 0.0
FRACTION_MAX = 1.0
UNIT_LABELS: frozenset[str] = frozenset({"bytes", "videos", "segments", "frames"})
ERROR_INFO_FIELDS: tuple[str, ...] = ("message", "code")
PROGRESS_SNAPSHOT_FIELDS: tuple[str, ...] = (
    "fraction",
    "units_done",
    "units_total",
    "unit_label",
    "rate",
    "eta_seconds",
    "error",
)
CONVERT_OPTIONS_FIELDS: tuple[str, ...] = ("codec", "bitrate_kbps", "sample_rate", "channels")
MEDIA_INFO_FIELDS: tuple[str, ...] = (
    "duration",
    "container",
    "video_codec",
    "audio_codec",
    "sample_rate",
    "channels",
    "width",
    "height",
    "fps",
    "bit_depth",
    "field_order",
    "streams",
)


@dataclass(frozen=True)
class ErrorInfo:
    """Structured error payload carried on progress snapshots."""

    message: str
    code: str | None

    def __post_init__(self) -> None:
        require_non_empty_str(self.message, "message")
        require_optional_str(self.code, "code")


@dataclass(frozen=True)
class ProgressSnapshot:
    """Uniform poll shape for bytes, videos, or segments."""

    fraction: float
    units_done: int
    units_total: int | None
    unit_label: str
    rate: float | None
    eta_seconds: int | None
    error: ErrorInfo | None

    def __post_init__(self) -> None:
        require_fraction(self.fraction, "fraction")
        require_non_negative_int(self.units_done, "units_done")
        require_optional_non_negative_int(self.units_total, "units_total")
        if self.unit_label not in UNIT_LABELS:
            raise ValidationError("unit_label must be one of UNIT_LABELS")
        require_optional_non_negative_float(self.rate, "rate")
        require_optional_non_negative_int(self.eta_seconds, "eta_seconds")
        if self.error is not None and not isinstance(self.error, ErrorInfo):
            raise ValidationError("error must be ErrorInfo | None")


@dataclass(frozen=True)
class ConvertOptions:
    """FFmpeg convert choices used by MediaPort.convert."""

    codec: str
    bitrate_kbps: int | None
    sample_rate: int | None
    channels: int | None

    def __post_init__(self) -> None:
        require_non_empty_str(self.codec, "codec")
        require_optional_non_negative_int(self.bitrate_kbps, "bitrate_kbps")
        require_optional_non_negative_int(self.sample_rate, "sample_rate")
        require_optional_non_negative_int(self.channels, "channels")


@dataclass(frozen=True)
class MediaInfo:
    """FFmpeg probe result. Video and audio codecs are separate fields."""

    duration: float | None
    container: str | None
    video_codec: str | None
    audio_codec: str | None
    sample_rate: int | None
    channels: int | None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    bit_depth: int | None = None
    field_order: str | None = None
    streams: list[object] | None = None

    def __post_init__(self) -> None:
        require_optional_non_negative_float(self.duration, "duration")
        require_optional_str(self.container, "container")
        require_optional_str(self.video_codec, "video_codec")
        require_optional_str(self.audio_codec, "audio_codec")
        require_optional_non_negative_int(self.sample_rate, "sample_rate")
        require_optional_non_negative_int(self.channels, "channels")
        require_optional_non_negative_int(self.width, "width")
        require_optional_non_negative_int(self.height, "height")
        require_optional_non_negative_float(self.fps, "fps")
        require_optional_non_negative_int(self.bit_depth, "bit_depth")
        require_optional_str(self.field_order, "field_order")
        if self.streams is not None and not isinstance(self.streams, list):
            raise ValidationError("streams must be list | None")
