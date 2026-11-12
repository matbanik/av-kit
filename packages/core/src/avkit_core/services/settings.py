"""SettingsService — leaf-key table, wire validation, typed get/set."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from avkit_core.domain.capture import ANNOTATED_FORMATS
from avkit_core.domain.enums import SettingValueType
from avkit_core.domain.errors import ValidationError
from avkit_core.domain.settings import SETTING_NAMESPACES, Setting
from avkit_core.domain.wire import (
    AUDIO_WIRE_MAP,
    COOKIE_MODE_WIRES,
    DEVICE_WIRE_MAP,
    LOG_LEVEL_WIRES,
    OUTPUT_FORMAT_WIRES,
    QUALITY_WIRE_MAP,
    THEME_WIRES,
)
from avkit_core.ports.storage import UnitOfWork

TTS_SPEED_MIN = 0.5
TTS_SPEED_MAX = 2.0
COOKIE_VALUE_MAX_LEN = 4096
COOKIE_NEEDLES: tuple[str, ...] = ("HTTP_COOKIE", "#HttpOnly_")

ValueKind = Literal["string", "boolean", "number"]


@dataclass(frozen=True)
class SettingSpec:
    """One SETTINGS_KEY_TABLE row."""

    kind: ValueKind
    default: object
    wires: frozenset[str] | None = None
    min_number: float | None = None
    max_number: float | None = None
    allow_negative: bool = False


SETTINGS_KEY_TABLE: dict[tuple[str, str], SettingSpec] = {
    ("downloader", "path"): SettingSpec("string", "~/Downloads/av-kit"),
    ("downloader", "ffmpeg_path"): SettingSpec("string", ""),
    ("downloader", "quality"): SettingSpec("string", "1080p", frozenset(QUALITY_WIRE_MAP)),
    ("downloader", "audio_only"): SettingSpec("boolean", False),
    ("downloader", "audio_format"): SettingSpec("string", "default", frozenset(AUDIO_WIRE_MAP)),
    ("downloader", "cookie_mode"): SettingSpec("string", "none", COOKIE_MODE_WIRES),
    ("downloader", "cookie_browser"): SettingSpec("string", "chrome"),
    ("downloader", "cookie_browser_profile"): SettingSpec("string", ""),
    ("downloader", "cookie_file_path"): SettingSpec("string", ""),
    ("downloader", "archive_tracking"): SettingSpec("boolean", True),
    ("downloader", "yt_dlp_debug"): SettingSpec("boolean", False),
    # DENO_SETTING (MEU-141): an absolute path to deno.exe; empty means the bundle, then PATH.
    ("downloader", "deno_path"): SettingSpec("string", ""),
    ("transcript", "output_dir"): SettingSpec("string", "~/Documents/Transcripts"),
    ("transcript", "requests_per_hour"): SettingSpec("number", 300, min_number=0),
    ("transcript", "delay_between_requests"): SettingSpec("number", 6, min_number=0),
    ("transcript", "max_retries"): SettingSpec("number", 3, min_number=0),
    ("transcript", "retry_delay"): SettingSpec("number", 30, min_number=0),
    ("transcript", "batch_size"): SettingSpec("number", 50, min_number=0),
    ("transcript", "pause_between_batches"): SettingSpec("number", 300, min_number=0),
    ("transcript", "playlist_end"): SettingSpec("number", 0, min_number=0),
    ("transcript", "max_words_per_document"): SettingSpec("number", 490000, min_number=0),
    ("tts", "models_directory"): SettingSpec("string", "~/.avkit/models"),
    ("tts", "voice"): SettingSpec("string", "am_eric"),
    ("tts", "speed"): SettingSpec(
        "number", 1.0, min_number=TTS_SPEED_MIN, max_number=TTS_SPEED_MAX
    ),
    ("tts", "output_format"): SettingSpec("string", "MP3", OUTPUT_FORMAT_WIRES),
    ("tts", "output_path"): SettingSpec("string", "~/Documents"),
    ("tts", "device"): SettingSpec("string", "auto", frozenset(DEVICE_WIRE_MAP)),
    ("tts", "chunk_max_chars"): SettingSpec("number", 250, min_number=0),
    ("tts", "input_text"): SettingSpec("string", ""),
    ("app", "log_level"): SettingSpec("string", "INFO", LOG_LEVEL_WIRES),
    ("app", "log_to_file"): SettingSpec("boolean", False),
    ("app", "console_visible"): SettingSpec("boolean", True),
    ("ui", "theme"): SettingSpec("string", "dark", THEME_WIRES),
    ("converter", "output_dir"): SettingSpec("string", "~/Videos/av-kit"),
    ("converter", "default_preset"): SettingSpec(
        "string",
        "balanced",
        frozenset({"archival", "high_quality", "balanced", "sharing", "mobile"}),
    ),
    ("converter", "skip_existing"): SettingSpec("boolean", True),
    ("converter", "gpu_preference"): SettingSpec(
        "string", "auto", frozenset({"auto", "nvidia", "amd", "intel", "software"})
    ),
    ("capture", "inbox_dir"): SettingSpec("string", "~/Pictures/av-kit"),
    ("capture", "hotkey"): SettingSpec("string", "F2"),
    ("capture", "copy_to_clipboard"): SettingSpec("boolean", False),
    ("capture", "close_to_tray"): SettingSpec("boolean", True),
    ("capture", "flatten_backup"): SettingSpec("boolean", True),
    ("capture", "backup_dir"): SettingSpec("string", ""),
    ("capture", "annotated_format"): SettingSpec("string", "png", frozenset(ANNOTATED_FORMATS)),
}

UoWFactory = Callable[[], UnitOfWork]


def _kind_to_enum(kind: ValueKind) -> SettingValueType:
    if kind == "boolean":
        return SettingValueType.Boolean
    if kind == "number":
        return SettingValueType.Number
    return SettingValueType.String


def _reject_cookie_shaped(value: object) -> None:
    text = value if isinstance(value, str) else str(value)
    if len(text) > COOKIE_VALUE_MAX_LEN:
        raise ValidationError("settings value exceeds cookie-byte length limit")
    for needle in COOKIE_NEEDLES:
        if needle in text:
            raise ValidationError("cookie bytes are never settings values")


def _encode(spec: SettingSpec, key: str, value: object) -> str:
    _reject_cookie_shaped(value)
    if spec.kind == "boolean":
        if not isinstance(value, bool):
            raise ValidationError(f"{key} must be bool")
        return "true" if value else "false"
    if spec.kind == "number":
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValidationError(f"{key} must be a number")
        number = float(value)
        if not math.isfinite(number):
            raise ValidationError(f"{key} must be a finite number")
        if spec.min_number is not None and number < spec.min_number:
            raise ValidationError(f"{key} is out of range")
        if spec.max_number is not None and number > spec.max_number:
            raise ValidationError(f"{key} is out of range")
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
        if number.is_integer() and spec.min_number == 0 and key != "speed":
            return str(int(number))
        return repr(float(value)) if not isinstance(value, int) else str(value)
    if not isinstance(value, str):
        raise ValidationError(f"{key} must be a string")
    if spec.wires is not None and value not in spec.wires:
        raise ValidationError(f"{key} is not a known wire value")
    return value


def _decode(spec: SettingSpec, stored: str) -> object:
    if spec.kind == "boolean":
        return stored == "true"
    if spec.kind == "number":
        try:
            if "." in stored or "e" in stored.lower() or stored.casefold() in {
                "nan",
                "inf",
                "-inf",
                "+inf",
            }:
                number = float(stored)
                if not math.isfinite(number):
                    raise ValidationError("stored numeric setting is not finite")
                return number
            return int(stored)
        except ValueError as exc:
            raise ValidationError("stored numeric setting is invalid") from exc
    return stored


class SettingsService:
    """Typed get/set over SETTINGS_KEY_TABLE."""

    def __init__(self, uow_factory: UoWFactory) -> None:
        self._uow_factory = uow_factory

    def get(self, namespace: str, key: str) -> object:
        spec = SETTINGS_KEY_TABLE.get((namespace, key))
        if spec is None:
            raise ValidationError("unknown settings key")
        with self._uow_factory() as uow:
            row = uow.settings.get(namespace, key)
        if row is None:
            return spec.default
        return _decode(spec, row.value)

    def get_namespace(self, namespace: str) -> dict[str, object]:
        if namespace not in SETTING_NAMESPACES:
            raise ValidationError("unknown settings namespace")
        result: dict[str, object] = {}
        for (ns, key), spec in SETTINGS_KEY_TABLE.items():
            if ns != namespace:
                continue
            result[key] = self.get(namespace, key)
            _ = spec
        return result

    def set(self, namespace: str, key: str, value: object) -> None:
        spec = SETTINGS_KEY_TABLE.get((namespace, key))
        if spec is None:
            if namespace not in SETTING_NAMESPACES:
                raise ValidationError("unknown settings namespace")
            if "." in key:
                raise ValidationError("key must be a leaf name without '.'")
            raise ValidationError("unknown settings key")
        encoded = _encode(spec, key, value)
        setting = Setting(
            namespace=namespace,
            key=key,
            value=encoded,
            value_type=_kind_to_enum(spec.kind),
            updated_at=datetime.now(UTC),
        )
        with self._uow_factory() as uow:
            uow.settings.set(setting)
            uow.commit()

    def set_namespace(self, namespace: str, mapping: dict[str, object]) -> None:
        if namespace not in SETTING_NAMESPACES:
            raise ValidationError("unknown settings namespace")
        known = {key for (ns, key) in SETTINGS_KEY_TABLE if ns == namespace}
        extra = set(mapping) - known
        if extra:
            raise ValidationError("unknown settings key")
        encoded: list[tuple[str, str, SettingSpec]] = []
        for key, value in mapping.items():
            spec = SETTINGS_KEY_TABLE[(namespace, key)]
            encoded.append((key, _encode(spec, key, value), spec))
        now = datetime.now(UTC)
        with self._uow_factory() as uow:
            for key, value, spec in encoded:
                uow.settings.set(
                    Setting(
                        namespace=namespace,
                        key=key,
                        value=value,
                        value_type=_kind_to_enum(spec.kind),
                        updated_at=now,
                    )
                )
            uow.commit()
