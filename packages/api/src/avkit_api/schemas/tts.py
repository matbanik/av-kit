"""TTS request and response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from avkit_api.schemas.common import ApiModel
from avkit_core.domain.tts import TTS_SPEED_MAX, TTS_SPEED_MIN


class TTSPrepareIn(ApiModel):
    """POST /tts/prepare body."""

    text: str
    enabled_steps: list[str]
    chunk_max_chars: int | None = None


class TTSPrepareOut(ApiModel):
    """Prepare result. No job row."""

    cleaned_text: str


class TTSGenerateIn(ApiModel):
    """POST /tts/generate body."""

    text: str = Field(min_length=1)
    voice: str
    speed: float = Field(ge=TTS_SPEED_MIN, le=TTS_SPEED_MAX)
    format: Literal["MP3", "WAV"]
    enabled_steps: list[str]
    source_kind: Literal["inline", "file"] = "inline"
    source_path: str | None = None


class TTSJobOut(ApiModel):
    """TTS job without full text."""

    id: str
    source_kind: str
    source_path: str | None
    text_hash: str
    text_preview: str
    voice: str
    speed: float
    format: str
    status: str
    output_path: str | None
    segments_total: int
    segments_done: int
    error_message: str | None
    created_at: str


class VoiceOut(ApiModel):
    """Public voice row. No user-set lang_code. `reason` is a `VOICE_REASON` (MEU-74)."""

    voice_id: str
    language: str
    gender: str
    style_description: str
    available: bool
    reason: Literal["espeak_missing", "language_unsupported"] | None


class VoiceListOut(ApiModel):
    """GET /tts/voices envelope."""

    items: list[VoiceOut]
