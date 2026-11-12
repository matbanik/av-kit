"""Domain error types raised by constructors, services, and adapters."""

from __future__ import annotations

import math
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path

from avkit_core.domain.enums import DownloadFailureCause


class DomainError(Exception):
    """Base type for user-visible domain failures."""

    def __init__(self, message: str) -> None:
        if not isinstance(message, str) or message == "":
            raise TypeError("domain error message must be a non-empty str")
        super().__init__(message)


class ValidationError(DomainError):
    """Invalid constructor input or settings value."""


class NotFoundError(DomainError):
    """Unknown job, variant, or settings namespace."""


class ConflictError(DomainError):
    """Illegal status transition or conflicting runtime state."""


class AgeRestrictedError(DomainError):
    """yt-dlp age gate."""


class ExtractError(DomainError):
    """yt-dlp could not extract the URL (bot wall, IO, no info); the request is refused."""


class DownloadCancelledError(DomainError):
    """User cancelled an in-flight download."""


class DownloadFailedError(DomainError):
    """A download failed (`FAILED_ERROR`, MEU-137, D-631).

    `cause` is the `DownloadFailureCause` and `detail` yt-dlp's raw first line. `str` names
    only the cause, so no yt-dlp text reaches a generic error path.
    """

    def __init__(self, cause: DownloadFailureCause, detail: str) -> None:
        super().__init__(f"download failed: {cause.value}")
        self.cause = cause
        self.detail = detail


class SABRDetectedError(DomainError):
    """Adapter observed SABR during extract or download."""


class CookieTestError(DomainError):
    """Cookie probe failed or the cookie source was unreadable."""


CookieAccessError = CookieTestError


class TranscriptsDisabledError(DomainError):
    """Channel or video has transcripts disabled."""


class NoTranscriptFoundError(DomainError):
    """No caption track in the requested languages."""


class TranscriptRetryableError(DomainError):
    """Transient transcript fetch failure."""


class FFmpegNotFoundError(DomainError):
    """FFmpeg binary missing after the locked probe order."""


class FFmpegEncodeError(DomainError):
    """Non-zero FFmpeg exit after encode/cut/extract started."""


class MediaProbeError(DomainError):
    """ffprobe failed or the file is not media."""


class InvalidTimeRangeError(DomainError):
    """Cut range is empty, inverted, or negative."""


class GpuUnavailableError(DomainError):
    """Requested GPU encoder override is not available."""


class ModelDownloadError(DomainError):
    """Hugging Face model fetch failed."""


class ModelLoadError(DomainError):
    """Model file missing or unsupported torch/ONNX load."""


class FilesystemError(DomainError):
    """Atomic write or bounded read failed."""


class SpacyModelNotFoundError(DomainError):
    """spaCy model `en_core_web_sm` is missing; only the chunk step fails."""


class CaptureNotSupportedError(DomainError):
    """OS grab is not supported on this platform in this phase."""


class CaptureFailedError(DomainError):
    """Empty/black frame, permission, or mss grab failure."""


class InboxPathError(DomainError):
    """Path is outside the inbox, not a file, or not an image."""


class AnnotationValidationError(DomainError):
    """Unknown annotation type/color, empty text, or invalid geometry/opacity."""


class CaptureRequestConflictError(ConflictError):
    """A second Pending interactive capture request is not allowed."""


class CaptureFlattenConflictError(ConflictError):
    """Flatten/revert cannot proceed.

    Causes: no saved marks, an unsupported file, a bad backup dir, or file I/O.
    """


def require_non_empty_str(value: object, field: str) -> str:
    """Return `value` when it is a non-empty str; otherwise raise ValidationError."""
    if not isinstance(value, str) or value == "":
        raise ValidationError(f"{field} must be a non-empty str")
    return value


def require_optional_str(value: object, field: str) -> str | None:
    """Return `value` when it is str | None; otherwise raise ValidationError."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be str | None")
    return value


def require_bool(value: object, field: str) -> bool:
    """Return `value` when it is bool; otherwise raise ValidationError."""
    if not isinstance(value, bool):
        raise ValidationError(f"{field} must be bool")
    return value


def require_non_negative_int(value: object, field: str) -> int:
    """Return `value` when it is a non-negative int (not bool)."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValidationError(f"{field} must be a non-negative int")
    return value


def require_optional_non_negative_int(value: object, field: str) -> int | None:
    """Return `value` when it is int | None and, if int, non-negative."""
    if value is None:
        return None
    return require_non_negative_int(value, field)


def require_non_negative_float(value: object, field: str) -> float:
    """Return `value` when it is a finite non-negative int/float (not bool)."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValidationError(f"{field} must be a non-negative number")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValidationError(f"{field} must be a finite non-negative number")
    return number


def require_optional_non_negative_float(value: object, field: str) -> float | None:
    """Return `value` when it is float | None and, if present, non-negative."""
    if value is None:
        return None
    return require_non_negative_float(value, field)


def require_uuid_str(value: object, field: str) -> str:
    """Return `value` when it is a UUID-format str."""
    text = require_non_empty_str(value, field)
    try:
        uuid.UUID(text)
    except ValueError as exc:
        raise ValidationError(f"{field} must be a UUID str") from exc
    return text


def require_datetime(value: object, field: str) -> datetime:
    """Return `value` when it is datetime."""
    if not isinstance(value, datetime):
        raise ValidationError(f"{field} must be datetime")
    return value


def require_optional_datetime(value: object, field: str) -> datetime | None:
    """Return `value` when it is datetime | None."""
    if value is None:
        return None
    return require_datetime(value, field)


def require_path(value: object, field: str) -> Path:
    """Return `value` when it is Path."""
    if not isinstance(value, Path):
        raise ValidationError(f"{field} must be a Path")
    return value


def require_optional_path(value: object, field: str) -> Path | None:
    """Return `value` when it is Path | None."""
    if value is None:
        return None
    return require_path(value, field)


def require_enum(value: object, enum_cls: type[Enum], field: str) -> Enum:
    """Return `value` when it is a member of `enum_cls`."""
    if not isinstance(value, enum_cls):
        raise ValidationError(f"{field} must be a {enum_cls.__name__}")
    return value


def require_fraction(value: object, field: str) -> float:
    """Return `value` when it is a float in [0.0, 1.0]."""
    number = require_non_negative_float(value, field)
    if number > 1.0:
        raise ValidationError(f"{field} must be between 0.0 and 1.0")
    return number


DOMAIN_ERROR_TYPES: tuple[type[DomainError], ...] = (
    ValidationError,
    NotFoundError,
    ConflictError,
    AgeRestrictedError,
    DownloadCancelledError,
    SABRDetectedError,
    CookieTestError,
    TranscriptsDisabledError,
    NoTranscriptFoundError,
    TranscriptRetryableError,
    FFmpegNotFoundError,
    FFmpegEncodeError,
    MediaProbeError,
    InvalidTimeRangeError,
    GpuUnavailableError,
    ModelDownloadError,
    ModelLoadError,
    FilesystemError,
    SpacyModelNotFoundError,
    CaptureNotSupportedError,
    CaptureFailedError,
    InboxPathError,
    AnnotationValidationError,
    CaptureRequestConflictError,
    CaptureFlattenConflictError,
    ExtractError,
    DownloadFailedError,
)
