"""YouTube extract/download port protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from avkit_core.domain.download import (
    CookieTestResult,
    DownloadOptions,
    DownloadResult,
    FormatInfo,
    PlaylistInfo,
    SABRStatus,
    VideoInfo,
    VideoListing,
)


class YouTubePort(Protocol):
    """IO-shaped YouTube operations implemented in Phase 2."""

    def extract_info(
        self, url: str, flat: bool = False, options: DownloadOptions | None = None
    ) -> VideoInfo | PlaylistInfo: ...

    def extract_video_ids(self, channel_url: str) -> VideoListing: ...

    def download(self, url: str, options: DownloadOptions) -> DownloadResult: ...

    def get_formats(self, video_id: str) -> list[FormatInfo]: ...

    def check_sabr_status(self) -> SABRStatus: ...

    def test_cookies(
        self,
        mode: str,
        browser: str | None,
        profile: str | None,
        cookie_file: Path | None,
    ) -> CookieTestResult: ...

    def ytdlp_version(self) -> str | None: ...
