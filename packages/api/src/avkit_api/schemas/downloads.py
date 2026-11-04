"""Download request and response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from avkit_api.schemas.common import ApiModel, QueueRuntimeOut

QualityWire = Literal[
    "best",
    "2160p",
    "1440p",
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p",
    "144p",
    "lowest",
]
AudioWire = Literal[
    "default",
    "best",
    "lowest",
    "low_webm",
    "medium_webm",
    "standard_webm",
    "standard_m4a",
    "standard_mp3",
    "high_m4a",
]


class DownloadCreateIn(ApiModel):
    """POST /downloads body."""

    url: str = Field(min_length=1)
    quality: QualityWire
    audio_only: bool = False
    audio_format: AudioWire = "default"


class DownloadJobOut(ApiModel):
    """One formatted download queue row."""

    id: str
    url: str
    video_id: str
    title: str
    quality: str
    audio_only: bool
    audio_format: str
    status: str
    progress: float
    speed: str | None
    eta: str | None
    file_size: int | None
    file_path: str | None
    error_message: str | None
    queue_position: int
    created_at: str


class DownloadListOut(ApiModel):
    """GET /downloads envelope."""

    items: list[DownloadJobOut]
    processor: QueueRuntimeOut


class DownloadCreateOut(ApiModel):
    """POST /downloads envelope."""

    items: list[DownloadJobOut]


class ReorderIn(ApiModel):
    """PUT /downloads/reorder body."""

    job_ids: list[str]


class CookieTestIn(ApiModel):
    """POST /downloads/cookies/test body."""

    mode: Literal["none", "browser", "file"]
    browser: str | None = None
    profile: str | None = None
    cookie_file: str | None = None


class CookieTestOut(ApiModel):
    """Cookie probe result without cookie bytes."""

    ok: bool


class SABRStatusOut(ApiModel):
    """Session SABR snapshot."""

    mode: Literal["inactive", "active", "checking"]
    source: Literal["detected", "forced"] | None
    checked_at: str | None


class ApplyDefaultsOut(ApiModel):
    """POST /downloads/apply-defaults body."""

    updated: int
