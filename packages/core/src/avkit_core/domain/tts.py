"""TTS jobs, model catalog rows, and TTS session value objects."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import assert_never

from avkit_core.domain.enums import (
    MediaFormat,
    ModelFormat,
    ModelPrecision,
    TTSSourceKind,
    TTSStatus,
)
from avkit_core.domain.errors import (
    ConflictError,
    ValidationError,
    require_bool,
    require_datetime,
    require_enum,
    require_fraction,
    require_non_empty_str,
    require_non_negative_float,
    require_non_negative_int,
    require_optional_path,
    require_optional_str,
    require_uuid_str,
)

TTS_TRANSITIONS: dict[TTSStatus, frozenset[TTSStatus]] = {
    TTSStatus.Pending: frozenset({TTSStatus.Generating}),
    TTSStatus.Generating: frozenset({TTSStatus.Done, TTSStatus.Failed, TTSStatus.Cancelled}),
}
MODEL_DOWNLOAD_STATES: frozenset[str] = frozenset({"Idle", "Downloading", "Failed"})
TTS_OUTPUT_FORMATS: frozenset[MediaFormat] = frozenset({MediaFormat.MP3, MediaFormat.WAV})
TTS_SPEED_MIN = 0.5
TTS_SPEED_MAX = 2.0
TEXT_PREVIEW_MAX = 200
VOICE_CONFIG_FIELDS: tuple[str, ...] = (
    "voice_id",
    "lang_code",
    "language",
    "gender",
    "style_description",
)
MODEL_STATUS_FIELDS: tuple[str, ...] = (
    "variant_id",
    "name",
    "device",
    "memory_bytes",
    "is_loaded",
)
MODEL_DOWNLOAD_RUNTIME_FIELDS: tuple[str, ...] = (
    "variant_id",
    "asset",
    "state",
    "fraction",
    "error_message",
)




class TtsAsset(StrEnum):
    """Kokoro runtime assets managed outside the model weights (MEU-62 `TTS_ASSETS`)."""

    ONNX_VOCAB = "tts_onnx_vocab"
    SPACY_MODEL = "tts_spacy_model"
    VOICE_PACKS = "tts_voice_packs"


class AssetState(StrEnum):
    """Readiness of one `TtsAsset` (MEU-62 `ASSET_STATES`)."""

    READY = "ready"
    MISSING = "missing"
    DOWNLOADING = "downloading"


# The spaCy English pipeline Kokoro's G2P and the `chunk` prepare step load by name.
SPACY_MODEL = "en_core_web_sm"
# Kokoro voice-id prefixes (lang codes). Mirrors `avkit_infra.tts.voices.LANG_BY_PREFIX`;
# a parity test ties the two, because core cannot import infra.
KOKORO_LANG_CODES: frozenset[str] = frozenset({"a", "b", "e", "f", "h", "i", "j", "p", "z"})
# Lang codes whose Kokoro pipeline builds misaki's English G2P, which loads the spaCy model.
SPACY_LANG_CODES: frozenset[str] = frozenset({"a", "b"})
# Prepare steps whose implementation loads the spaCy model (`services/prepare.py` `_chunk`).
SPACY_STEPS: frozenset[str] = frozenset({"chunk"})
# `VOICE_REASON` (MEU-74, D-70): lang codes whose G2P runs the user-installed eSpeak NG CLI,
# and lang codes no runtime serves yet (ja/zh need G2P packages that are not shipped).
ESPEAK_LANG_CODES: frozenset[str] = frozenset({"e", "f", "h", "i", "p"})
UNSUPPORTED_LANG_CODES: frozenset[str] = frozenset({"j", "z"})
# `LEGACY_ONNX_DIR`: where MEU-24/62 stored the v0.19 ONNX weights, under the models dir.
LEGACY_ONNX_DIR = "onnx"


def is_legacy_onnx_path(path: Path, models_dir: Path) -> bool:
    """`LEGACY_ONNX_PATH`: a `.onnx` file directly under `{models_dir}/LEGACY_ONNX_DIR`.

    Pure: compares paths only and never touches the filesystem.
    """
    return path.suffix.lower() == ".onnx" and path.parent == models_dir / LEGACY_ONNX_DIR


def required_tts_assets(
    variant_format: ModelFormat,
    voice_id: str,
    enabled_steps: Iterable[str],
) -> tuple[TtsAsset, ...]:
    """Return the assets a generation needs, in `TtsAsset` declaration order.

    `REQUIRED_TTS_ASSETS`: the vocab/config file for every model format, plus the spaCy
    model for English voices or whenever a spaCy-backed prepare step runs, plus the voice
    packs for every generation.

    Raises:
        ValidationError: `voice_id` is empty or its prefix is not a Kokoro lang code
            (fail closed on open-world input).
    """
    require_non_empty_str(voice_id, "voice_id")
    lang_code = voice_id[0]
    if lang_code not in KOKORO_LANG_CODES:
        raise ValidationError(f"unknown voice language prefix: {voice_id}")
    match variant_format:
        case ModelFormat.PyTorch | ModelFormat.ONNX:
            # The PyTorch KModel config and the ONNX vocab are the same config.json.
            required = [TtsAsset.ONNX_VOCAB]
        case _:
            assert_never(variant_format)
    if lang_code in SPACY_LANG_CODES or not SPACY_STEPS.isdisjoint(enabled_steps):
        required.append(TtsAsset.SPACY_MODEL)
    required.append(TtsAsset.VOICE_PACKS)
    return tuple(required)


@dataclass(frozen=True)
class VoiceConfig:
    """Kokoro voice catalog row. lang_code prefix must match voice_id."""

    voice_id: str
    lang_code: str
    language: str
    gender: str
    style_description: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.voice_id, "voice_id")
        require_non_empty_str(self.lang_code, "lang_code")
        require_non_empty_str(self.language, "language")
        require_non_empty_str(self.gender, "gender")
        require_non_empty_str(self.style_description, "style_description")
        if self.lang_code[0] != self.voice_id[0]:
            raise ValidationError("lang_code first character must match voice_id prefix")


class VoiceUnavailableReason(StrEnum):
    """Closed `VOICE_REASON` wire set. The UI owns the wording."""

    ESPEAK_MISSING = "espeak_missing"
    LANGUAGE_UNSUPPORTED = "language_unsupported"


@dataclass(frozen=True)
class VoiceAvailability:
    """Whether a voice can generate now; `reason` is set exactly when it cannot."""

    available: bool
    reason: VoiceUnavailableReason | None

    def __post_init__(self) -> None:
        require_bool(self.available, "available")
        if self.reason is not None:
            require_enum(self.reason, VoiceUnavailableReason, "reason")
        if self.available != (self.reason is None):
            raise ValidationError("reason must be set exactly when the voice is unavailable")


def voice_availability(lang_code: str, espeak_available: bool) -> VoiceAvailability:
    """`VOICE_REASON`: j/z never; e/f/h/i/p only with eSpeak NG; a/b always."""
    if lang_code not in KOKORO_LANG_CODES:
        raise ValidationError(f"unknown lang_code: {lang_code!r}")
    if lang_code in UNSUPPORTED_LANG_CODES:
        return VoiceAvailability(False, VoiceUnavailableReason.LANGUAGE_UNSUPPORTED)
    if lang_code in ESPEAK_LANG_CODES and not espeak_available:
        return VoiceAvailability(False, VoiceUnavailableReason.ESPEAK_MISSING)
    return VoiceAvailability(True, None)


@dataclass(frozen=True)
class EspeakStatus:
    """`ESPEAK_DETECT` result: the resolved `espeak-ng` and its first `--version` line."""

    available: bool
    version: str | None
    path: Path | None

    def __post_init__(self) -> None:
        require_bool(self.available, "available")
        require_optional_str(self.version, "version")
        require_optional_path(self.path, "path")
        if self.available and (not self.version or self.path is None):
            raise ValidationError("an available eSpeak NG has a version and a path")
        if not self.available and (self.version is not None or self.path is not None):
            raise ValidationError("an unavailable eSpeak NG has no version or path")


ESPEAK_UNAVAILABLE = EspeakStatus(available=False, version=None, path=None)


@dataclass(frozen=True)
class ModelStatus:
    """Session snapshot of the currently loaded model."""

    variant_id: str | None
    name: str
    device: str
    memory_bytes: int
    is_loaded: bool

    def __post_init__(self) -> None:
        require_optional_str(self.variant_id, "variant_id")
        require_non_empty_str(self.name, "name")
        require_non_empty_str(self.device, "device")
        require_non_negative_int(self.memory_bytes, "memory_bytes")
        require_bool(self.is_loaded, "is_loaded")


@dataclass(frozen=True)
class ModelDownloadRuntime:
    """In-memory model or TTS-asset fetch progress. Not a ModelFetchJob."""

    variant_id: str | None
    asset: TtsAsset | None
    state: str
    fraction: float
    error_message: str | None

    def __post_init__(self) -> None:
        require_optional_str(self.variant_id, "variant_id")
        if self.asset is not None:
            require_enum(self.asset, TtsAsset, "asset")
            if self.variant_id is not None:
                raise ValidationError("a download targets a variant or an asset, not both")
        require_non_empty_str(self.state, "state")
        if self.state not in MODEL_DOWNLOAD_STATES:
            raise ValidationError("state must be one of MODEL_DOWNLOAD_STATES")
        require_fraction(self.fraction, "fraction")
        require_optional_str(self.error_message, "error_message")


@dataclass(frozen=True)
class TTSJob:
    """One generation run. Full input text is not a persistable field."""

    id: str
    source_kind: TTSSourceKind
    source_path: Path | None
    text_hash: str
    text_preview: str
    voice: str
    speed: float
    format: MediaFormat
    status: TTSStatus
    output_path: Path | None
    segments_total: int
    segments_done: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        require_uuid_str(self.id, "id")
        require_enum(self.source_kind, TTSSourceKind, "source_kind")
        require_optional_path(self.source_path, "source_path")
        require_non_empty_str(self.text_hash, "text_hash")
        if not isinstance(self.text_preview, str):
            raise ValidationError("text_preview must be str")
        if len(self.text_preview) > TEXT_PREVIEW_MAX:
            raise ValidationError("text_preview exceeds TEXT_PREVIEW_MAX")
        require_non_empty_str(self.voice, "voice")
        speed = require_non_negative_float(self.speed, "speed")
        if speed < TTS_SPEED_MIN or speed > TTS_SPEED_MAX:
            raise ValidationError("speed must be within TTS_SPEED_MIN and TTS_SPEED_MAX")
        require_enum(self.format, MediaFormat, "format")
        if self.format not in TTS_OUTPUT_FORMATS:
            raise ValidationError("format must be one of TTS_OUTPUT_FORMATS")
        require_enum(self.status, TTSStatus, "status")
        require_optional_path(self.output_path, "output_path")
        require_non_negative_int(self.segments_total, "segments_total")
        require_non_negative_int(self.segments_done, "segments_done")
        require_optional_str(self.error_message, "error_message")
        require_datetime(self.created_at, "created_at")
        require_datetime(self.updated_at, "updated_at")
        if self.source_kind is TTSSourceKind.File and self.source_path is None:
            raise ValidationError("source_path is required when source_kind is File")

    def transition(self, new_status: TTSStatus) -> TTSJob:
        """Return a copy with `new_status` when the edge is in TTS_TRANSITIONS."""
        require_enum(new_status, TTSStatus, "new_status")
        allowed = TTS_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise ConflictError(
                f"illegal tts transition {self.status.value} -> {new_status.value}"
            )
        return replace(self, status=new_status)


@dataclass(frozen=True)
class ModelVariant:
    """Kokoro catalog row. Loaded device lives on ModelStatus, not here."""

    id: str
    name: str
    format: ModelFormat
    precision: ModelPrecision
    size_bytes: int
    path: Path | None
    is_downloaded: bool

    def __post_init__(self) -> None:
        require_non_empty_str(self.id, "id")
        require_non_empty_str(self.name, "name")
        require_enum(self.format, ModelFormat, "format")
        require_enum(self.precision, ModelPrecision, "precision")
        require_non_negative_int(self.size_bytes, "size_bytes")
        require_optional_path(self.path, "path")
        require_bool(self.is_downloaded, "is_downloaded")


#: `MODEL_REASONS` (D-310): why a variant of each format can't run in this build. Fixed av-kit
#: text that names the next step; it never holds exception text.
MODEL_REASONS: dict[ModelFormat, str] = {
    ModelFormat.PyTorch: "This build can't run PyTorch models. Choose an ONNX model.",
    ModelFormat.ONNX: "This build can't run ONNX models. Reinstall av-kit.",
}


@dataclass(frozen=True)
class ModelAvailability:
    """`AVAILABILITY`: whether a variant can run in this build; `reason` is set exactly when not."""

    available: bool
    reason: str | None

    def __post_init__(self) -> None:
        require_bool(self.available, "available")
        if self.reason is not None:
            require_non_empty_str(self.reason, "reason")
        if self.available != (self.reason is None):
            raise ValidationError("reason must be set exactly when the model is unavailable")


def model_availability(fmt: ModelFormat, runtime_present: bool) -> ModelAvailability:
    """`AVAILABILITY` for a variant of `fmt`, given whether this process has its runtime."""
    if runtime_present:
        return ModelAvailability(True, None)
    return ModelAvailability(False, MODEL_REASONS[fmt])


#: How many words of the text name an output file, and the most characters they keep.
OUTPUT_STEM_WORDS = 3
OUTPUT_STEM_WORDS_MAX = 60


def output_stem(text: str, voice: str) -> str:
    """An output file's stem: the text's first three words, lowercase, a dash, then the voice.

    Each word keeps only its letters and digits, and a word left empty is skipped; with no word
    left the stem starts `speech`. Mat, 2026-11-09: "first 3 words from the Text with dash
    followed by voice".
    """
    words: list[str] = []
    for raw in text.split():
        word = "".join(char for char in raw.casefold() if char.isalnum())
        if word:
            words.append(word)
            if len(words) == OUTPUT_STEM_WORDS:
                break
    head = "-".join(words)[:OUTPUT_STEM_WORDS_MAX].strip("-") or "speech"
    tail = "".join(char for char in voice if char.isalnum() or char == "_") or "voice"
    return f"{head}-{tail}"
