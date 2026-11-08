"""Download jobs, archive entries, and download-session value objects."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path

from avkit_core.domain.enums import AudioFormat, DownloadStatus, QualityPreset, SABRMode, SABRSource
from avkit_core.domain.errors import (
    ConflictError,
    ValidationError,
    require_bool,
    require_datetime,
    require_enum,
    require_fraction,
    require_non_empty_str,
    require_non_negative_int,
    require_optional_non_negative_float,
    require_optional_non_negative_int,
    require_optional_path,
    require_optional_str,
    require_path,
    require_uuid_str,
)

SABR_STATUS_FIELDS: tuple[str, ...] = ("mode", "source", "checked_at")
DOWNLOAD_TRANSITIONS: dict[DownloadStatus, frozenset[DownloadStatus]] = {
    DownloadStatus.Pending: frozenset(
        {
            DownloadStatus.Downloading,
            DownloadStatus.QualityBlocked,
            DownloadStatus.Skipped,
        }
    ),
    DownloadStatus.Downloading: frozenset(
        {
            DownloadStatus.Done,
            DownloadStatus.Failed,
            DownloadStatus.Cancelled,
            DownloadStatus.Skipped,
            DownloadStatus.QualityBlocked,
            DownloadStatus.AgeRestricted,
        }
    ),
    DownloadStatus.Failed: frozenset({DownloadStatus.Pending}),
    DownloadStatus.QualityBlocked: frozenset({DownloadStatus.Pending}),
    DownloadStatus.AgeRestricted: frozenset({DownloadStatus.Pending}),
    DownloadStatus.Cancelled: frozenset({DownloadStatus.Pending}),
}
REQUEUEABLE_DOWNLOAD_STATUSES: frozenset[DownloadStatus] = frozenset(
    {
        DownloadStatus.Failed,
        DownloadStatus.Cancelled,
        DownloadStatus.QualityBlocked,
        DownloadStatus.AgeRestricted,
    }
)
BLOCKER_REASONS: dict[DownloadStatus, str] = {
    DownloadStatus.QualityBlocked: (
        "YouTube is limiting which formats this video will serve right now, "
        "so the requested quality or audio format is not available."
    ),
    DownloadStatus.AgeRestricted: "video is age-restricted",
}
BLOCKER_REMEDIATION: dict[DownloadStatus, str] = {
    DownloadStatus.QualityBlocked: (
        "Settings > Downloader > Quality (choose a lower quality, "
        "or a supported audio format for audio-only jobs)"
    ),
    DownloadStatus.AgeRestricted: (
        "Settings > Cookies & Authentication (sign-in required for this video)"
    ),
}
_BLOCKER_REASON_VALUES: frozenset[str] = frozenset(BLOCKER_REASONS.values())


def normalize_blocker_reason(job: DownloadJob) -> DownloadJob:
    """Return `job` with its blocker reason made consistent with its status.

    A blocked job always carries the canonical reason for its status; a job that
    has left a blocker status drops a reason it no longer explains. The clear is
    deliberately narrow -- only an exact `BLOCKER_REASONS` value is removed, so a
    Failed job's real error text is never eaten.
    """
    reason = BLOCKER_REASONS.get(job.status)
    if reason is not None:
        if job.error_message == reason:
            return job
        return replace(job, error_message=reason)
    if job.error_message in _BLOCKER_REASON_VALUES:
        return replace(job, error_message=None)
    return job


@dataclass(frozen=True)
class SABRStatus:
    """Session SABR snapshot held on DownloadService, not a table."""

    mode: SABRMode
    source: SABRSource | None
    checked_at: datetime | None

    def __post_init__(self) -> None:
        if not isinstance(self.mode, SABRMode):
            raise ValidationError("mode must be a SABRMode")
        if self.mode is SABRMode.Active and self.source is None:
            raise ValidationError("source is required when mode is Active")
        if self.source is not None and not isinstance(self.source, SABRSource):
            raise ValidationError("source must be SABRSource | None")
        if self.checked_at is not None and not isinstance(self.checked_at, datetime):
            raise ValidationError("checked_at must be datetime | None")


@dataclass(frozen=True)
class DownloadJob:
    """One downloader queue row per video."""

    id: str
    url: str
    video_id: str
    title: str
    quality: QualityPreset
    audio_only: bool
    audio_format: AudioFormat
    status: DownloadStatus
    progress: float
    speed_bps: float | None
    eta_seconds: int | None
    file_size: int | None
    file_path: Path | None
    error_message: str | None
    queue_position: int
    created_at: datetime
    updated_at: datetime
    received_height: int | None = None

    def __post_init__(self) -> None:
        require_uuid_str(self.id, "id")
        require_non_empty_str(self.url, "url")
        require_non_empty_str(self.video_id, "video_id")
        require_non_empty_str(self.title, "title")
        require_enum(self.quality, QualityPreset, "quality")
        require_bool(self.audio_only, "audio_only")
        require_enum(self.audio_format, AudioFormat, "audio_format")
        require_enum(self.status, DownloadStatus, "status")
        require_fraction(self.progress, "progress")
        require_optional_non_negative_float(self.speed_bps, "speed_bps")
        require_optional_non_negative_int(self.eta_seconds, "eta_seconds")
        require_optional_non_negative_int(self.file_size, "file_size")
        require_optional_path(self.file_path, "file_path")
        require_optional_str(self.error_message, "error_message")
        require_non_negative_int(self.queue_position, "queue_position")
        require_datetime(self.created_at, "created_at")
        require_datetime(self.updated_at, "updated_at")
        require_optional_non_negative_int(self.received_height, "received_height")

    def transition(self, new_status: DownloadStatus) -> DownloadJob:
        """Return a copy with `new_status` when the edge is in DOWNLOAD_TRANSITIONS."""
        require_enum(new_status, DownloadStatus, "new_status")
        allowed = DOWNLOAD_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise ConflictError(
                f"illegal download transition {self.status.value} -> {new_status.value}"
            )
        return replace(self, status=new_status)

    def reset_failed(self) -> DownloadJob:
        """Map a re-queueable status -> Pending and clear error_message plus progress."""
        if self.status not in REQUEUEABLE_DOWNLOAD_STATUSES:
            allowed = ", ".join(sorted(status.value for status in REQUEUEABLE_DOWNLOAD_STATUSES))
            raise ConflictError(f"reset_failed is only valid from {allowed}")
        return replace(
            self.transition(DownloadStatus.Pending),
            error_message=None,
            progress=0.0,
        )


@dataclass(frozen=True)
class DownloadArchiveEntry:
    """Skip catalog keyed by extractor + video_id. Not job history."""

    extractor: str
    video_id: str
    title: str | None
    recorded_at: datetime

    def __post_init__(self) -> None:
        require_non_empty_str(self.extractor, "extractor")
        require_non_empty_str(self.video_id, "video_id")
        require_optional_str(self.title, "title")
        require_datetime(self.recorded_at, "recorded_at")


@dataclass(frozen=True)
class FormatInfo:
    """One yt-dlp format row returned by YouTubePort."""

    format_id: str
    ext: str
    height: int | None
    abr: float | None
    vcodec: str | None
    acodec: str | None

    def __post_init__(self) -> None:
        require_non_empty_str(self.format_id, "format_id")
        require_non_empty_str(self.ext, "ext")
        require_optional_non_negative_int(self.height, "height")
        require_optional_non_negative_float(self.abr, "abr")
        require_optional_str(self.vcodec, "vcodec")
        require_optional_str(self.acodec, "acodec")


@dataclass(frozen=True)
class VideoInfo:
    """Single-video extract result."""

    video_id: str
    title: str
    duration: float | None
    formats: list[FormatInfo]

    def __post_init__(self) -> None:
        require_non_empty_str(self.video_id, "video_id")
        require_non_empty_str(self.title, "title")
        require_optional_non_negative_float(self.duration, "duration")
        if not isinstance(self.formats, list) or not all(
            isinstance(item, FormatInfo) for item in self.formats
        ):
            raise ValidationError("formats must be a list of FormatInfo")


@dataclass(frozen=True)
class PlaylistInfo:
    """Flat playlist extract result used to insert N download jobs."""

    playlist_id: str
    title: str
    video_ids: list[str]

    def __post_init__(self) -> None:
        require_non_empty_str(self.playlist_id, "playlist_id")
        require_non_empty_str(self.title, "title")
        if not isinstance(self.video_ids, list) or not all(
            isinstance(item, str) and item for item in self.video_ids
        ):
            raise ValidationError("video_ids must be a list of non-empty str")


def _require_text_clean(value: object, field: str) -> None:
    """`TEXT_CLEAN`: None, or non-empty single-spaced text with no controls or lone surrogates.

    The message names the field, never the value (Session 50 RULE-1).
    """
    if value is None:
        return
    if (
        not isinstance(value, str)
        or value == ""
        or " ".join(value.split()) != value
        or any(unicodedata.category(char) in ("Cc", "Cs") for char in value)
    ):
        raise ValidationError(
            f"{field} must be None or single-spaced text without controls or lone surrogates"
        )


@dataclass(frozen=True)
class ListedVideo:
    """One video from a flat enumeration: its ID and, when given, its title."""

    video_id: str
    title: str | None

    def __post_init__(self) -> None:
        require_non_empty_str(self.video_id, "video_id")
        _require_text_clean(self.title, "title")


@dataclass(frozen=True)
class VideoListing:
    """A flat enumeration's videos and, when given, the channel that owns them."""

    videos: tuple[ListedVideo, ...]
    channel_name: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.videos, tuple) or not all(
            isinstance(item, ListedVideo) for item in self.videos
        ):
            raise ValidationError("videos must be a tuple of ListedVideo")
        if len({item.video_id for item in self.videos}) != len(self.videos):
            raise ValidationError("videos must not repeat a video_id")
        _require_text_clean(self.channel_name, "channel_name")


@dataclass(frozen=True)
class DownloadOptions:
    """Download adapter options. Cookie bytes never appear here."""

    quality: QualityPreset
    audio_only: bool
    audio_format: AudioFormat
    output_dir: Path
    mode: str
    browser: str | None
    profile: str | None
    cookie_file: Path | None

    def __post_init__(self) -> None:
        require_enum(self.quality, QualityPreset, "quality")
        require_bool(self.audio_only, "audio_only")
        require_enum(self.audio_format, AudioFormat, "audio_format")
        require_path(self.output_dir, "output_dir")
        require_non_empty_str(self.mode, "mode")
        require_optional_str(self.browser, "browser")
        require_optional_str(self.profile, "profile")
        require_optional_path(self.cookie_file, "cookie_file")


@dataclass(frozen=True)
class DownloadResult:
    """Completed download pointer plus SABR observation for this call."""

    file_path: Path
    file_size: int
    video_id: str
    title: str
    sabr_detected: bool
    height: int | None = None

    def __post_init__(self) -> None:
        require_path(self.file_path, "file_path")
        require_non_negative_int(self.file_size, "file_size")
        require_non_empty_str(self.video_id, "video_id")
        require_non_empty_str(self.title, "title")
        require_bool(self.sabr_detected, "sabr_detected")
        require_optional_non_negative_int(self.height, "height")


@dataclass(frozen=True)
class CookieTestResult:
    """Cookie probe outcome. Never carries cookie bytes."""

    ok: bool
    error_message: str | None

    def __post_init__(self) -> None:
        require_bool(self.ok, "ok")
        require_optional_str(self.error_message, "error_message")
