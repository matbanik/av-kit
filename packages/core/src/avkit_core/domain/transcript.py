"""Transcript jobs, items, and transcript port DTOs."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
from avkit_core.domain.errors import (
    ConflictError,
    ValidationError,
    require_datetime,
    require_enum,
    require_non_empty_str,
    require_non_negative_int,
    require_optional_datetime,
    require_optional_path,
    require_optional_str,
    require_path,
    require_uuid_str,
)

TRANSCRIPT_PARENT_TRANSITIONS: dict[TranscriptStatus, frozenset[TranscriptStatus]] = {
    TranscriptStatus.Pending: frozenset({TranscriptStatus.Processing}),
    TranscriptStatus.Processing: frozenset(
        {
            TranscriptStatus.Paused,
            TranscriptStatus.Done,
            TranscriptStatus.Failed,
            TranscriptStatus.Cancelled,
            TranscriptStatus.Pending,
        }
    ),
    TranscriptStatus.Paused: frozenset({TranscriptStatus.Processing, TranscriptStatus.Cancelled}),
    TranscriptStatus.Cancelled: frozenset({TranscriptStatus.Pending}),
    TranscriptStatus.Failed: frozenset({TranscriptStatus.Pending}),
}

TRANSCRIPT_ITEM_TRANSITIONS: dict[TranscriptItemStatus, frozenset[TranscriptItemStatus]] = {
    TranscriptItemStatus.Pending: frozenset(
        {
            TranscriptItemStatus.Done,
            TranscriptItemStatus.Skipped,
            TranscriptItemStatus.Failed,
        }
    ),
    TranscriptItemStatus.Failed: frozenset({TranscriptItemStatus.Pending}),
}


@dataclass(frozen=True)
class TranscriptJob:
    """Parent channel-batch row. Progress is computed from TranscriptItem rows."""

    id: str
    channel_url: str
    channel_name: str
    status: TranscriptStatus
    output_dir: Path
    video_count: int
    word_count: int
    zip_path: Path | None
    queue_position: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        require_uuid_str(self.id, "id")
        require_non_empty_str(self.channel_url, "channel_url")
        require_non_empty_str(self.channel_name, "channel_name")
        require_enum(self.status, TranscriptStatus, "status")
        require_path(self.output_dir, "output_dir")
        require_non_negative_int(self.video_count, "video_count")
        require_non_negative_int(self.word_count, "word_count")
        require_optional_path(self.zip_path, "zip_path")
        require_non_negative_int(self.queue_position, "queue_position")
        require_optional_str(self.error_message, "error_message")
        require_datetime(self.created_at, "created_at")
        require_datetime(self.updated_at, "updated_at")

    def transition(self, new_status: TranscriptStatus) -> TranscriptJob:
        """Return a copy with `new_status` when the edge is in TRANSCRIPT_PARENT_TRANSITIONS."""
        require_enum(new_status, TranscriptStatus, "new_status")
        allowed = TRANSCRIPT_PARENT_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise ConflictError(
                f"illegal transcript transition {self.status.value} -> {new_status.value}"
            )
        return replace(self, status=new_status)


@dataclass(frozen=True)
class TranscriptItem:
    """Per-video resume record. Done requires a raw markdown path pointer."""

    id: str
    job_id: str
    video_id: str
    title: str | None
    language: str | None
    word_count: int
    path: Path | None
    status: TranscriptItemStatus
    error_message: str | None
    retry_count: int
    processed_at: datetime | None

    def __post_init__(self) -> None:
        require_uuid_str(self.id, "id")
        require_non_empty_str(self.job_id, "job_id")
        require_non_empty_str(self.video_id, "video_id")
        require_optional_str(self.title, "title")
        require_optional_str(self.language, "language")
        require_non_negative_int(self.word_count, "word_count")
        require_optional_path(self.path, "path")
        require_enum(self.status, TranscriptItemStatus, "status")
        require_optional_str(self.error_message, "error_message")
        require_non_negative_int(self.retry_count, "retry_count")
        require_optional_datetime(self.processed_at, "processed_at")
        if self.status is TranscriptItemStatus.Done and self.path is None:
            raise ValidationError("Done TranscriptItem requires path")

    def transition(self, new_status: TranscriptItemStatus) -> TranscriptItem:
        """Return a copy with `new_status` when the edge is in TRANSCRIPT_ITEM_TRANSITIONS."""
        require_enum(new_status, TranscriptItemStatus, "new_status")
        allowed = TRANSCRIPT_ITEM_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise ConflictError(
                f"illegal transcript item transition {self.status.value} -> {new_status.value}"
            )
        return replace(self, status=new_status)


@dataclass(frozen=True)
class ChannelInfo:
    """Resolved channel metadata used when adding a transcript job."""

    channel_id: str
    name: str
    url: str
    video_count: int

    def __post_init__(self) -> None:
        require_non_empty_str(self.channel_id, "channel_id")
        require_non_empty_str(self.name, "name")
        require_non_empty_str(self.url, "url")
        require_non_negative_int(self.video_count, "video_count")


@dataclass(frozen=True)
class TranscriptResult:
    """Port return only. text is written to disk and discarded."""

    video_id: str
    title: str
    text: str
    language: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.video_id, "video_id")
        require_non_empty_str(self.title, "title")
        if not isinstance(self.text, str):
            raise ValidationError("text must be str")
        require_non_empty_str(self.language, "language")


class TranscriptFailureCause(StrEnum):
    """Why a video has no transcript. `failure_message` writes one text per cause."""

    blocked = "blocked"
    no_captions = "no_captions"
    unavailable = "unavailable"
    other = "other"


#: The causes a skip may carry. A block or any other failure is never a skip.
_SKIP_CAUSES = frozenset({TranscriptFailureCause.no_captions, TranscriptFailureCause.unavailable})

#: The most characters `safe_reason` keeps.
REASON_LIMIT = 200

#: A URL: a `scheme://` run up to whitespace.
_URL = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://\S*")


@dataclass(frozen=True)
class TranscriptSkip:
    """Port return for a video with no transcript. It carries its cause."""

    cause: TranscriptFailureCause

    def __post_init__(self) -> None:
        require_enum(self.cause, TranscriptFailureCause, "cause")
        if self.cause not in _SKIP_CAUSES:
            raise ValidationError(
                f"a transcript skip's cause must be no_captions or unavailable, not {self.cause}"
            )


def failure_message(cause: TranscriptFailureCause, reason: str | None = None) -> str:
    """The user-facing text for `cause`, written only here. Only `other` uses `reason`."""
    require_enum(cause, TranscriptFailureCause, "cause")
    if cause is TranscriptFailureCause.blocked:
        return (
            "YouTube is blocking caption requests from this network. "
            "Try again later or from another network, then Resume."
        )
    if cause is TranscriptFailureCause.no_captions:
        return "No captions for this video."
    if cause is TranscriptFailureCause.unavailable:
        return "This video is unavailable."
    return f"Couldn't get captions: {reason}." if reason else "Couldn't get captions."


def retry_message(attempt: int, attempts: int, delay: float) -> str:
    """The job's message while a blocked video waits: which attempt was refused, what comes next.

    The last attempt's wait ends in a pause (MEU-116), so it says so instead of a retry.
    """
    then = "pausing" if attempt >= attempts else "trying again"
    return (
        "YouTube is blocking caption requests from this network. "
        f"Attempt {attempt} of {attempts} was refused; {then} in {delay:g} s."
    )


def replace_links(text: str) -> str:
    """`text` with each URL as "[link]". `safe_reason` and the Console fields share this rule."""
    return _URL.sub("[link]", text)


def safe_reason(text: str) -> str:
    """The first line of `text`, each URL as "[link]", cut to REASON_LIMIT. Redact it first."""
    lines = text.splitlines()
    first = lines[0].strip() if lines else ""
    return replace_links(first)[:REASON_LIMIT]
