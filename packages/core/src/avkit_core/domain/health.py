"""In-process console and dependency health value objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avkit_core.domain.errors import (
    ValidationError,
    require_bool,
    require_datetime,
    require_non_empty_str,
)
from avkit_core.domain.tts import ESPEAK_UNAVAILABLE, AssetState, EspeakStatus
from avkit_core.domain.wire import LOG_LEVEL_WIRES


@dataclass(frozen=True)
class ConsoleEvent:
    """One redacted console ring entry. Not persistable."""

    seq: int
    message: str
    module: str
    timestamp: datetime
    level: str

    def __post_init__(self) -> None:
        if not isinstance(self.seq, int) or isinstance(self.seq, bool) or self.seq < 1:
            raise TypeError("seq must be a positive int")
        require_non_empty_str(self.message, "message")
        require_non_empty_str(self.module, "module")
        require_datetime(self.timestamp, "timestamp")
        require_non_empty_str(self.level, "level")
        if self.level not in LOG_LEVEL_WIRES:
            raise ValidationError("level must be a log level wire")


@dataclass(frozen=True)
class DependencyHealth:
    """Optional binary versions from frozen ports, plus TTS runtime-asset readiness."""

    ffmpeg_version: str | None
    ytdlp_version: str | None
    tts_onnx_vocab: AssetState
    tts_spacy_model: AssetState
    tts_voice_packs: AssetState
    tts_spacy_version: str | None = None
    tts_espeak: EspeakStatus = ESPEAK_UNAVAILABLE
    ffmpeg_path: str | None = None
    ffprobe_available: bool = False


@dataclass(frozen=True)
class HealthLiveness:
    """Process-up probe."""

    ok: bool

    def __post_init__(self) -> None:
        require_bool(self.ok, "ok")
