"""Pure wire formatters for speed, ETA, ISO timestamps, and enum maps."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Literal

from avkit_core.domain.enums import (
    AudioEncodeMode,
    AudioFormat,
    ConversionKind,
    ConversionPresetId,
    CutCopyMode,
    DeviceType,
    QualityPreset,
    SABRMode,
    SABRSource,
)
from avkit_core.domain.wire import (
    AUDIO_ENCODE_WIRE_MAP,
    AUDIO_WIRE_MAP,
    COPY_WIRE_MAP,
    DEVICE_WIRE_MAP,
    KIND_WIRE_MAP,
    PRESET_WIRE_MAP,
    QUALITY_WIRE_MAP,
)

QUALITY_ENUM_TO_WIRE = {preset: wire for wire, preset in QUALITY_WIRE_MAP.items()}
AUDIO_ENUM_TO_WIRE = {preset: wire for wire, preset in AUDIO_WIRE_MAP.items()}
DEVICE_ENUM_TO_WIRE = {preset: wire for wire, preset in DEVICE_WIRE_MAP.items()}
KIND_ENUM_TO_WIRE = {preset: wire for wire, preset in KIND_WIRE_MAP.items()}
PRESET_ENUM_TO_WIRE = {preset: wire for wire, preset in PRESET_WIRE_MAP.items()}
COPY_ENUM_TO_WIRE = {preset: wire for wire, preset in COPY_WIRE_MAP.items()}
AUDIO_ENCODE_ENUM_TO_WIRE = {preset: wire for wire, preset in AUDIO_ENCODE_WIRE_MAP.items()}
SABR_MODE_WIRE: dict[SABRMode, Literal["inactive", "active", "checking"]] = {
    SABRMode.Inactive: "inactive",
    SABRMode.Active: "active",
    SABRMode.Checking: "checking",
}
SABR_SOURCE_WIRE: dict[SABRSource, Literal["detected", "forced"]] = {
    SABRSource.Detected: "detected",
    SABRSource.Forced: "forced",
}


def format_encode_speed(speed: float | None) -> str | None:
    """Format an FFmpeg realtime multiplier as `{n:.2f}x`, or None when missing."""
    if speed is None:
        return None
    if isinstance(speed, bool) or not isinstance(speed, int | float):
        return None
    value = float(speed)
    if not math.isfinite(value) or value < 0:
        return None
    return f"{value:.2f}x"


def format_speed(speed_bps: float | None) -> str | None:
    """Format bytes/sec with SI-1000 units, or None when missing/non-finite."""
    if speed_bps is None:
        return None
    if isinstance(speed_bps, bool) or not isinstance(speed_bps, int | float):
        return None
    value = float(speed_bps)
    if not math.isfinite(value) or value < 0:
        return None
    units = ("B", "KB", "MB", "GB")
    index = 0
    while value >= 1000.0 and index < len(units) - 1:
        value /= 1000.0
        index += 1
    return f"{value:.1f} {units[index]}/s"


def format_eta(eta_seconds: int | None) -> str | None:
    """Format seconds as `M:SS`. Minutes may exceed 59."""
    if eta_seconds is None:
        return None
    if isinstance(eta_seconds, bool) or not isinstance(eta_seconds, int) or eta_seconds < 0:
        return None
    minutes, seconds = divmod(eta_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def format_iso(value: datetime) -> str:
    """Naive datetimes emit `…Z`; aware datetimes emit offset ISO-8601."""
    if value.tzinfo is None:
        return f"{value.isoformat()}Z"
    return value.isoformat()


def quality_wire(preset: QualityPreset) -> str:
    """Map a quality enum to its GUI wire string."""
    return QUALITY_ENUM_TO_WIRE[preset]


def audio_wire(preset: AudioFormat) -> str:
    """Map an audio enum to its GUI wire string."""
    return AUDIO_ENUM_TO_WIRE[preset]


def device_wire(preset: DeviceType) -> str:
    """Map a device enum to its GUI wire string."""
    return DEVICE_ENUM_TO_WIRE[preset]


def conversion_kind_wire(kind: ConversionKind) -> str:
    """Map a conversion kind enum to its GUI wire string."""
    return KIND_ENUM_TO_WIRE[kind]


def conversion_preset_wire(preset: ConversionPresetId | None) -> str | None:
    """Map a conversion preset enum to its GUI wire string."""
    if preset is None:
        return None
    return PRESET_ENUM_TO_WIRE[preset]


def cut_copy_wire(mode: CutCopyMode | None) -> str | None:
    """Map a cut copy-mode enum to its GUI wire string."""
    if mode is None:
        return None
    return COPY_ENUM_TO_WIRE[mode]


def audio_encode_wire(mode: AudioEncodeMode | None) -> str | None:
    """Map a conversion audio-mode enum to its GUI wire string."""
    if mode is None:
        return None
    return AUDIO_ENCODE_ENUM_TO_WIRE[mode]


def sabr_mode_wire(mode: SABRMode) -> Literal["inactive", "active", "checking"]:
    """Map SABR mode to lowercase wire."""
    return SABR_MODE_WIRE[mode]


def sabr_source_wire(source: SABRSource | None) -> Literal["detected", "forced"] | None:
    """Map SABR source to lowercase wire."""
    if source is None:
        return None
    return SABR_SOURCE_WIRE[source]
