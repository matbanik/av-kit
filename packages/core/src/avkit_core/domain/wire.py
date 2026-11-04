"""GUI wire-string maps. Settings persist these strings; jobs store enums."""

from __future__ import annotations

from avkit_core.domain.enums import (
    AudioEncodeMode,
    AudioFormat,
    CaptureRequestStatus,
    CaptureSource,
    ConversionKind,
    ConversionPresetId,
    CutCopyMode,
    DeviceType,
    GpuPreference,
    QualityPreset,
)

QUALITY_WIRE_MAP: dict[str, QualityPreset] = {
    "best": QualityPreset.Best,
    "2160p": QualityPreset.P2160,
    "1440p": QualityPreset.P1440,
    "1080p": QualityPreset.P1080,
    "720p": QualityPreset.P720,
    "480p": QualityPreset.P480,
    "360p": QualityPreset.P360,
    "240p": QualityPreset.P240,
    "144p": QualityPreset.P144,
    "lowest": QualityPreset.Lowest,
}

AUDIO_WIRE_MAP: dict[str, AudioFormat] = {
    "default": AudioFormat.Default,
    "best": AudioFormat.Best,
    "lowest": AudioFormat.Lowest,
    "low_webm": AudioFormat.LowWebm,
    "medium_webm": AudioFormat.MediumWebm,
    "standard_webm": AudioFormat.StandardWebm,
    "standard_m4a": AudioFormat.StandardM4a,
    "standard_mp3": AudioFormat.StandardMp3,
    "high_m4a": AudioFormat.HighM4a,
}

DEVICE_WIRE_MAP: dict[str, DeviceType] = {
    "auto": DeviceType.Auto,
    "cuda": DeviceType.CUDA,
    "cpu": DeviceType.CPU,
    "mps": DeviceType.MPS,
}

THEME_WIRES: frozenset[str] = frozenset({"dark", "light"})
LOG_LEVEL_WIRES: frozenset[str] = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
OUTPUT_FORMAT_WIRES: frozenset[str] = frozenset({"MP3", "WAV"})
COOKIE_MODE_WIRES: frozenset[str] = frozenset({"none", "browser", "file"})

KIND_WIRE_MAP: dict[str, ConversionKind] = {
    "compress": ConversionKind.Compress,
    "cut": ConversionKind.Cut,
    "extract": ConversionKind.Extract,
}

PRESET_WIRE_MAP: dict[str, ConversionPresetId] = {
    "archival": ConversionPresetId.Archival,
    "high_quality": ConversionPresetId.HighQuality,
    "balanced": ConversionPresetId.Balanced,
    "sharing": ConversionPresetId.Sharing,
    "mobile": ConversionPresetId.Mobile,
}

COPY_WIRE_MAP: dict[str, CutCopyMode] = {
    "fast_copy": CutCopyMode.FastCopy,
    "reencode": CutCopyMode.Reencode,
}

AUDIO_ENCODE_WIRE_MAP: dict[str, AudioEncodeMode] = {
    "copy": AudioEncodeMode.Copy,
    "aac_96": AudioEncodeMode.Aac96,
    "aac_128": AudioEncodeMode.Aac128,
    "aac_192": AudioEncodeMode.Aac192,
}

GPU_PREF_WIRE_MAP: dict[str, GpuPreference] = {
    "auto": GpuPreference.Auto,
    "nvidia": GpuPreference.Nvidia,
    "amd": GpuPreference.Amd,
    "intel": GpuPreference.Intel,
    "software": GpuPreference.Software,
}

REGISTER_SOURCE_WIRE_MAP: dict[str, CaptureSource] = {
    "hotkey": CaptureSource.Hotkey,
    "gui": CaptureSource.Gui,
    "scan": CaptureSource.Scan,
}

REQUEST_STATUS_QUERY_MAP: dict[str, CaptureRequestStatus] = {
    "pending": CaptureRequestStatus.Pending,
    "completed": CaptureRequestStatus.Completed,
    "cancelled": CaptureRequestStatus.Cancelled,
    "expired": CaptureRequestStatus.Expired,
}
