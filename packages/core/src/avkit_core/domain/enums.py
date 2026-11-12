"""Closed Phase 1 domain enumerations."""

from __future__ import annotations

from enum import StrEnum


class DownloadStatus(StrEnum):
    """Downloader queue item status. Pause is QueueProcessorState, not a status."""

    Pending = "Pending"
    Downloading = "Downloading"
    Done = "Done"
    Failed = "Failed"
    Skipped = "Skipped"
    QualityBlocked = "QualityBlocked"
    AgeRestricted = "AgeRestricted"
    Cancelled = "Cancelled"


class TranscriptStatus(StrEnum):
    """Parent channel-batch status, including the durable Paused badge."""

    Pending = "Pending"
    Processing = "Processing"
    Done = "Done"
    Failed = "Failed"
    Paused = "Paused"
    Cancelled = "Cancelled"


class TranscriptItemStatus(StrEnum):
    """Per-video transcript child status."""

    Pending = "Pending"
    Done = "Done"
    Skipped = "Skipped"
    Failed = "Failed"


class TTSStatus(StrEnum):
    """TTS generation job status."""

    Pending = "Pending"
    Generating = "Generating"
    Done = "Done"
    Failed = "Failed"
    Cancelled = "Cancelled"


class TTSSourceKind(StrEnum):
    """Whether TTS input was pasted or loaded from a file."""

    Inline = "Inline"
    File = "File"


class QueueProcessorState(StrEnum):
    """In-memory processor state for a module queue."""

    Idle = "Idle"
    Processing = "Processing"
    Paused = "Paused"


class MediaFormat(StrEnum):
    """Container / encode target."""

    MP4 = "MP4"
    WEBM = "WEBM"
    MP3 = "MP3"
    M4A = "M4A"
    WAV = "WAV"
    OPUS = "OPUS"


class QualityPreset(StrEnum):
    """Downloader quality dropdown values."""

    Best = "Best"
    P2160 = "P2160"
    P1440 = "P1440"
    P1080 = "P1080"
    P720 = "P720"
    P480 = "P480"
    P360 = "P360"
    P240 = "P240"
    P144 = "P144"
    Lowest = "Lowest"


class AudioFormat(StrEnum):
    """Downloader audio-only dropdown values."""

    Default = "Default"
    Best = "Best"
    Lowest = "Lowest"
    LowWebm = "LowWebm"
    MediumWebm = "MediumWebm"
    StandardWebm = "StandardWebm"
    StandardM4a = "StandardM4a"
    StandardMp3 = "StandardMp3"
    HighM4a = "HighM4a"


class DeviceType(StrEnum):
    """TTS load-device argument. Not a ModelVariant column."""

    Auto = "Auto"
    CUDA = "CUDA"
    MPS = "MPS"
    CPU = "CPU"


class ModelFormat(StrEnum):
    """Kokoro model file format."""

    PyTorch = "PyTorch"
    ONNX = "ONNX"


class ModelPrecision(StrEnum):
    """Kokoro model numeric precision."""

    FP32 = "FP32"
    FP16 = "FP16"
    INT8 = "INT8"


class SABRMode(StrEnum):
    """Session SABR mode."""

    Inactive = "Inactive"
    Active = "Active"
    Checking = "Checking"


class SABRSource(StrEnum):
    """How SABR Active was set."""

    Detected = "Detected"
    Forced = "Forced"


class DownloadFailureCause(StrEnum):
    """Why a download failed (`FAILURE_CAUSE_ENUM`, MEU-137); each cause has one card message."""

    refused = "refused"
    no_format = "no_format"
    cookies = "cookies"
    write_failed = "write_failed"
    other = "other"


class SettingValueType(StrEnum):
    """Serialized settings value kind."""

    String = "String"
    Number = "Number"
    Boolean = "Boolean"
    Json = "Json"


class ConversionKind(StrEnum):
    """Conversion queue item kind."""

    Compress = "Compress"
    Cut = "Cut"
    Extract = "Extract"


class ConversionStatus(StrEnum):
    """Conversion queue item status. Pause is QueueProcessorState, not a status."""

    Pending = "Pending"
    Processing = "Processing"
    Done = "Done"
    Failed = "Failed"
    Cancelled = "Cancelled"
    Skipped = "Skipped"


class ConversionPresetId(StrEnum):
    """Built-in compress preset identifier."""

    Archival = "Archival"
    HighQuality = "HighQuality"
    Balanced = "Balanced"
    Sharing = "Sharing"
    Mobile = "Mobile"


class CutCopyMode(StrEnum):
    """Cut path: stream copy or re-encode."""

    FastCopy = "FastCopy"
    Reencode = "Reencode"


class AudioEncodeMode(StrEnum):
    """Compress audio encode mode."""

    Copy = "Copy"
    Aac96 = "Aac96"
    Aac128 = "Aac128"
    Aac192 = "Aac192"


class GpuPreference(StrEnum):
    """GPU encoder preference for conversion."""

    Auto = "Auto"
    Nvidia = "Nvidia"
    Amd = "Amd"
    Intel = "Intel"
    Software = "Software"


class CaptureSource(StrEnum):
    """How a capture original landed in the inbox."""

    Hotkey = "Hotkey"
    Gui = "Gui"
    McpFullscreen = "McpFullscreen"
    McpRegion = "McpRegion"
    McpInteractive = "McpInteractive"
    Scan = "Scan"
    # IMPORT_SOURCE (MEU-129, D-414): a file brought in with POST /captures mode=import.
    Import = "Import"
    # CROP_SOURCE (MEU-130, D-484): a region cut from another shot by POST /captures/{id}/crop.
    Crop = "Crop"
    # VIDEO_SOURCE (MEU-134, D-582): a still taken from a local video by POST /captures/frames.
    Video = "Video"
    # EXPORT_SOURCE (MEU-136, D-618): a resized or re-encoded copy written by
    # POST /captures/{id}/export.
    Export = "Export"


class CaptureRequestStatus(StrEnum):
    """Short-lived interactive capture request status."""

    Pending = "Pending"
    Completed = "Completed"
    Cancelled = "Cancelled"
    Expired = "Expired"


class AnnotationType(StrEnum):
    """Sidecar/API annotation discriminator. Wire values are lowercase."""

    Arrow = "Arrow"
    Rect = "Rect"
    Highlight = "Highlight"
    Text = "Text"
    Pixelate = "Pixelate"
    Eraser = "Eraser"

    def to_wire(self) -> str:
        """Return the sidecar/API lowercase type token."""
        mapping = {
            AnnotationType.Arrow: "arrow",
            AnnotationType.Rect: "rect",
            AnnotationType.Highlight: "highlight",
            AnnotationType.Text: "text",
            AnnotationType.Pixelate: "pixelate",
            AnnotationType.Eraser: "eraser",
        }
        return mapping[self]


SABR_RESTRICTED_AUDIO: frozenset[AudioFormat] = frozenset(
    {AudioFormat.StandardMp3, AudioFormat.HighM4a}
)
