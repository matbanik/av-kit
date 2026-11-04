"""Health route schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from avkit_api.schemas.common import ApiModel


class LivenessOut(ApiModel):
    """`GET /health` body."""

    status: Literal["ok"]


class VersionAvailabilityOut(ApiModel):
    """Binary version plus availability flag."""

    version: str | None
    available: bool


class FfmpegDependencyOut(VersionAvailabilityOut):
    """FFmpeg probe: the resolved binary path and whether an ffprobe was found."""

    path: str | None
    ffprobe_available: bool


class TtsAssetOut(VersionAvailabilityOut):
    """TTS runtime-asset readiness row; `available == (state == "ready")`."""

    state: Literal["ready", "missing", "downloading"]


class EspeakOut(ApiModel):
    """The user-installed eSpeak NG CLI (`ESPEAK_DETECT`); never shipped by av-kit."""

    available: bool
    version: str | None
    path: str | None


class DependenciesOut(ApiModel):
    """`GET /health/dependencies` body."""

    yt_dlp: VersionAvailabilityOut
    ffmpeg: FfmpegDependencyOut
    tts_onnx_vocab: TtsAssetOut
    tts_spacy_model: TtsAssetOut
    tts_voice_packs: TtsAssetOut
    tts_espeak: EspeakOut


class ConsoleEventOut(ApiModel):
    """One console ring item."""

    seq: int
    ts: str
    level: str
    module: str
    message: str


class ConsoleSnapshotOut(ApiModel):
    """`GET /health/console` body."""

    items: list[ConsoleEventOut]
    last_seq: int


class StartupMetricIn(ApiModel):
    """`POST /health/startup-metrics` body."""

    key: str = Field(min_length=1)
    value_ms: int | float
