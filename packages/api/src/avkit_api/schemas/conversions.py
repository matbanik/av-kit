"""Conversion request and response schemas."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from avkit_api.schemas.common import ApiModel, QueueRuntimeOut

PresetWire = Literal["archival", "high_quality", "balanced", "sharing", "mobile"]
CopyWire = Literal["fast_copy", "reencode"]
AudioEncodeWire = Literal["copy", "aac_96", "aac_128", "aac_192"]
GpuPrefWire = Literal["auto", "nvidia", "amd", "intel", "software"]
StreamModeWire = Literal["first", "all"]


class ConversionCompressIn(ApiModel):
    """POST /conversions body for kind=compress."""

    paths: list[str] = Field(min_length=1)
    kind: Literal["compress"]
    preset: PresetWire = "balanced"
    cq: int | None = Field(default=None, ge=0)
    scale_height: int | None = Field(default=None, ge=0)
    audio_mode: AudioEncodeWire | None = None
    gpu_preference: GpuPrefWire | None = None


class ConversionCutIn(ApiModel):
    """POST /conversions body for kind=cut."""

    paths: list[str] = Field(min_length=1)
    kind: Literal["cut"]
    in_ms: int = Field(ge=0)
    out_ms: int = Field(ge=0)
    copy_mode: CopyWire = "fast_copy"

    @model_validator(mode="after")
    def require_forward_range(self) -> Self:
        if self.out_ms <= self.in_ms:
            raise ValueError("out_ms must be greater than in_ms")
        return self


class ConversionExtractIn(ApiModel):
    """POST /conversions body for kind=extract."""

    paths: list[str] = Field(min_length=1)
    kind: Literal["extract"]
    stream_mode: StreamModeWire
    stream_index: int | None = Field(default=None, ge=0)


ConversionCreateIn = Annotated[
    ConversionCompressIn | ConversionCutIn | ConversionExtractIn,
    Field(discriminator="kind"),
]


class ConversionReorderIn(ApiModel):
    """PUT /conversions/reorder body."""

    job_ids: list[str] = Field(min_length=1)


class ConversionJobOut(ApiModel):
    """One formatted conversion queue row."""

    id: str
    kind: str
    input_path: str
    output_path: str
    display_name: str
    preset_id: str | None
    cq: int | None
    scale_height: int | None
    audio_mode: str | None
    gpu_encoder: str | None
    in_ms: int | None
    out_ms: int | None
    copy_mode: str | None
    stream_index: int | None
    status: str
    progress: float
    speed: str | None
    eta: str | None
    file_size: int | None
    duration_seconds: float | None
    width: int | None
    height: int | None
    error_message: str | None
    queue_position: int
    created_at: str


class ConversionCreateOut(ApiModel):
    """POST /conversions envelope."""

    items: list[ConversionJobOut]


class ConversionListOut(ApiModel):
    """GET /conversions envelope."""

    items: list[ConversionJobOut]
    processor: QueueRuntimeOut


class GPUCapabilitiesOut(ApiModel):
    """Session GPU probe snapshot. Matches the domain value object."""

    nvidia_nvenc: bool
    amd_amf: bool
    intel_qsv: bool
    vulkan: bool
    software_h265: bool
    software_h264: bool
    recommended_encoder: str
    checked_at: str | None


class ConversionProbeIn(ApiModel):
    """POST /conversions/probe body (MEU-133 PROBE_ROUTE): one local video path."""

    path: str = Field(min_length=1)


class ConversionProbeOut(ApiModel):
    """A local video's duration, size, codecs and streams (MEU-133 PROBE_MAP).

    `duration_ms` and `timecode` are null for a raw stream with no duration.
    """

    path: str
    duration_ms: int | None
    timecode: str | None
    container: str | None
    video_codec: str | None
    audio_codec: str | None
    width: int | None
    height: int | None
    fps: float | None
    has_video: bool
    has_audio: bool
