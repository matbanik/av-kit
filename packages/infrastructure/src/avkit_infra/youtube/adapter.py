"""YouTubePort adapter backed by the yt-dlp library (no CLI shell-out)."""

from __future__ import annotations

import math
import time
import unicodedata
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import structlog
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from avkit_core.domain.download import (
    CookieTestResult,
    DownloadOptions,
    DownloadResult,
    FormatInfo,
    ListedVideo,
    PlaylistInfo,
    SABRStatus,
    VideoInfo,
    VideoListing,
)
from avkit_core.domain.enums import AudioFormat, QualityPreset, SABRMode, SABRSource
from avkit_core.domain.errors import (
    AgeRestrictedError,
    CookieTestError,
    DomainError,
    DownloadCancelledError,
    ExtractError,
    ValidationError,
)

log = structlog.get_logger(module="youtube")

COOKIE_MODES = frozenset({"none", "browser", "file"})
QUALITY_HEIGHT: dict[QualityPreset, int] = {
    QualityPreset.P2160: 2160,
    QualityPreset.P1440: 1440,
    QualityPreset.P1080: 1080,
    QualityPreset.P720: 720,
    QualityPreset.P480: 480,
    QualityPreset.P360: 360,
    QualityPreset.P240: 240,
    QualityPreset.P144: 144,
}
QUALITY_SELECTOR_BEST = "bestvideo+bestaudio/best"
QUALITY_SELECTOR_LOWEST = "worstvideo+worstaudio/worst"
AUDIO_FORMAT_SELECTORS: dict[AudioFormat, str] = {
    AudioFormat.Default: "bestaudio/best[height<=480]/best",
    AudioFormat.Lowest: "worstaudio/bestaudio/best[height<=360]/best",
    AudioFormat.Best: "bestaudio/best[height<=720]/best",
    AudioFormat.LowWebm: "bestaudio[ext=webm]/bestaudio/best[height<=360]/best",
    AudioFormat.MediumWebm: "bestaudio[ext=webm]/bestaudio/best[height<=480]/best",
    AudioFormat.StandardWebm: "bestaudio[ext=webm]/bestaudio/best[height<=480]/best",
    AudioFormat.StandardM4a: "bestaudio[ext=m4a]/bestaudio/best[height<=480]/best",
    AudioFormat.StandardMp3: "bestaudio/best[height<=480]/best",
    AudioFormat.HighM4a: "bestaudio[ext=m4a]/bestaudio/best[height<=720]/best",
}
COOKIE_AUDIO_SELECTOR = (
    "bestaudio[protocol=m3u8_native]/bestaudio[protocol=m3u8]/bestaudio/worst"
)
COOKIE_EXTRACTOR_ARGS: dict[str, dict[str, object]] = {
    "youtube": {
        "player_client": ["tv", "web_safari", "web"],
    }
}
SABR_EXTRACTOR_ARGS: dict[str, dict[str, object]] = {
    "youtube": {
        "player_client": ["android", "tv", "ios"],
        "player_skip": ["webpage", "configs"],
        "skip": ["hls", "dash"],
        "include_hls_manifest": False,
        "include_dash_manifest": False,
    }
}
SABR_LOG_NEEDLES = (
    "require a gvs po token",
    "android client sabr formats require",
    "ios client sabr formats require",
)
SABR_PROBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
AGE_GATE_NEEDLES = ("sign in to confirm your age", "age-restricted")
PROGRESS_MIN_INTERVAL_S = 0.25
WATCH_URL_PREFIX = "https://www.youtube.com/watch?v="


def _read_ytdlp_version() -> str | None:
    try:
        from yt_dlp.version import __version__
    except ImportError:
        return None
    if not isinstance(__version__, str) or __version__ == "":
        return None
    return __version__


def _quality_selector(preset: QualityPreset) -> str:
    if preset is QualityPreset.Best:
        return QUALITY_SELECTOR_BEST
    if preset is QualityPreset.Lowest:
        return QUALITY_SELECTOR_LOWEST
    height = QUALITY_HEIGHT.get(preset)
    if height is None:
        raise ValidationError(f"unsupported quality preset: {preset}")
    return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"


def _audio_selector(audio_format: AudioFormat, mode: str) -> str:
    if mode in {"browser", "file"}:
        return COOKIE_AUDIO_SELECTOR
    selector = AUDIO_FORMAT_SELECTORS.get(audio_format)
    if selector is None:
        raise ValidationError(f"unsupported audio format: {audio_format}")
    return selector


def _unique_preserve_ids(entries: object) -> list[str]:
    if not isinstance(entries, list):
        return []
    ids: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        raw = entry.get("id")
        if not isinstance(raw, str) or raw == "":
            continue
        if raw in seen:
            continue
        seen.add(raw)
        ids.append(raw)
    return ids


_UNCLEAN_CATEGORIES = frozenset({"Cc", "Cs"})


def _clean_text(value: object) -> str | None:
    """`TEXT_CLEAN`: drop non-whitespace controls and lone surrogates, then collapse whitespace.

    A lone surrogate cannot be stored or written as UTF-8 (D-360), so it is dropped like a control.
    """
    if not isinstance(value, str):
        return None
    kept = "".join(
        char
        for char in value
        if char.isspace() or unicodedata.category(char) not in _UNCLEAN_CATEGORIES
    )
    return " ".join(kept.split()) or None


def _listed_videos(entries: object) -> tuple[ListedVideo, ...]:
    """Each entry's video, the first title winning (`FLAT_TABS`, D-358).

    An entry whose `_type` is `playlist` is a channel tab: it gives its own entries' videos,
    one level deep, and never its own ID (the channel's) or title (the tab's).
    """
    if not isinstance(entries, list):
        return ()
    flat: list[object] = []
    for entry in entries:
        if not (isinstance(entry, dict) and entry.get("_type") == "playlist"):
            flat.append(entry)
            continue
        inner = entry.get("entries")
        if isinstance(inner, list):
            flat.extend(
                item
                for item in inner
                if not (isinstance(item, dict) and item.get("_type") == "playlist")
            )
    videos: list[ListedVideo] = []
    seen: set[str] = set()
    for entry in flat:
        if not isinstance(entry, dict):
            continue
        raw = entry.get("id")
        if not isinstance(raw, str) or raw == "" or raw in seen:
            continue
        seen.add(raw)
        videos.append(ListedVideo(raw, _clean_text(entry.get("title"))))
    return tuple(videos)


def _map_format_row(row: object) -> FormatInfo:
    if not isinstance(row, dict):
        raise ValidationError("format row must be an object")
    format_id = row.get("format_id")
    ext = row.get("ext")
    if not isinstance(format_id, str) or format_id == "" or not isinstance(ext, str) or ext == "":
        raise ValidationError("format row requires format_id and ext")
    height_raw = row.get("height")
    height: int | None
    if isinstance(height_raw, int) and not isinstance(height_raw, bool):
        height = height_raw
    else:
        height = None
    abr_raw = row.get("abr")
    abr: float | None
    if isinstance(abr_raw, int | float) and not isinstance(abr_raw, bool):
        abr = float(abr_raw)
    else:
        abr = None
    vcodec = row.get("vcodec")
    acodec = row.get("acodec")
    return FormatInfo(
        format_id=format_id,
        ext=ext,
        height=height,
        abr=abr,
        vcodec=vcodec if isinstance(vcodec, str) else None,
        acodec=acodec if isinstance(acodec, str) else None,
    )


def _map_formats(raw: object) -> list[FormatInfo]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValidationError("formats must be a list")
    return [_map_format_row(item) for item in raw]


def _is_playlist(info: dict[str, object], flat: bool) -> bool:
    if info.get("_type") == "playlist":
        return True
    return flat and isinstance(info.get("entries"), list)


def _video_from_info(info: dict[str, object]) -> VideoInfo:
    video_id = info.get("id")
    title = info.get("title")
    if not isinstance(video_id, str) or video_id == "":
        raise ValidationError("extracted video id is required")
    if not isinstance(title, str) or title == "":
        title = video_id
    duration_raw = info.get("duration")
    duration = (
        float(duration_raw)
        if isinstance(duration_raw, int | float) and not isinstance(duration_raw, bool)
        else None
    )
    return VideoInfo(
        video_id=video_id,
        title=title,
        duration=duration,
        formats=_map_formats(info.get("formats")),
    )


def _playlist_from_info(info: dict[str, object]) -> PlaylistInfo:
    playlist_id = info.get("id")
    title = info.get("title")
    if not isinstance(playlist_id, str) or playlist_id == "":
        raise ValidationError("extracted playlist id is required")
    if not isinstance(title, str) or title == "":
        title = playlist_id
    return PlaylistInfo(
        playlist_id=playlist_id,
        title=title,
        video_ids=_unique_preserve_ids(info.get("entries")),
    )


def _ydl(opts: dict[str, object]) -> YoutubeDL:
    """Construct YoutubeDL. Stubs type params as TypedDict; runtime accepts a dict."""
    return YoutubeDL(cast(Any, opts))


def _info_dict(info: object) -> dict[str, object]:
    if not isinstance(info, dict):
        raise DomainError("yt-dlp returned no info")
    return {str(key): value for key, value in info.items()}


def _finite_int(value: object, *, missing: int | None) -> tuple[bool, int | None]:
    """Return (False, None) when value is a non-finite number that must skip the tick."""
    if value is None:
        return True, missing
    if isinstance(value, bool) or not isinstance(value, int | float):
        return True, missing
    number = float(value)
    if not math.isfinite(number):
        return False, None
    return True, int(number)


def _result_path(info: dict[str, object], ydl: YoutubeDL) -> Path:
    requested = info.get("requested_downloads")
    if isinstance(requested, list) and requested:
        first = requested[0]
        if isinstance(first, dict):
            raw = first.get("filepath") or first.get("filename")
            if isinstance(raw, str) and raw:
                return Path(raw)
    raw_path = info.get("filepath") or info.get("_filename")
    if isinstance(raw_path, str) and raw_path:
        return Path(raw_path)
    return Path(ydl.prepare_filename(cast(Any, info)))


class _YtDlpLogger:
    def __init__(self, debug_enabled: bool) -> None:
        self.sabr_detected = False
        self._debug_enabled = debug_enabled
        self._log = structlog.get_logger(module="yt-dlp")

    def _scan(self, message: object) -> None:
        text = str(message).casefold()
        for needle in SABR_LOG_NEEDLES:
            if needle in text:
                self.sabr_detected = True
                break
        if self._debug_enabled:
            self._log.debug("yt-dlp", message=str(message))

    def debug(self, message: object) -> None:
        self._scan(message)

    def info(self, message: object) -> None:
        self._scan(message)

    def warning(self, message: object) -> None:
        self._scan(message)

    def error(self, message: object) -> None:
        self._scan(message)


class YouTubeAdapter:
    """Library-backed YouTubePort. Cookie bytes never enter opts or logs."""

    def __init__(
        self,
        *,
        playlist_end: int = 0,
        on_progress: Callable[[int, int | None, float | None], None] | None = None,
        should_stop: Callable[[], bool] | None = None,
        yt_dlp_debug: bool = False,
        ffmpeg_location: Callable[[], Path | None] | None = None,
    ) -> None:
        if not isinstance(playlist_end, int) or isinstance(playlist_end, bool) or playlist_end < 0:
            raise ValidationError("playlist_end must be a non-negative int")
        self._playlist_end = playlist_end
        self._on_progress = on_progress
        self._should_stop = should_stop
        self._yt_dlp_debug = yt_dlp_debug
        self._ffmpeg_location = ffmpeg_location
        self._last_progress: float | None = None

    def _progress_hook(self, status: dict[str, object]) -> None:
        if self._should_stop is not None and self._should_stop():
            raise DownloadCancelledError("download cancelled")
        if status.get("status") != "downloading":
            return
        now = time.monotonic()
        speed_raw = status.get("speed")
        speed: float | None
        if speed_raw is None:
            speed = None
        elif isinstance(speed_raw, int | float) and not isinstance(speed_raw, bool):
            speed = float(speed_raw)
            if not math.isfinite(speed):
                return
        else:
            return
        downloaded_ok, downloaded = _finite_int(status.get("downloaded_bytes"), missing=0)
        if not downloaded_ok or downloaded is None:
            return
        total_raw = status.get("total_bytes")
        if total_raw is None:
            total_raw = status.get("total_bytes_estimate")
        total_ok, total = _finite_int(total_raw, missing=None)
        if not total_ok:
            return
        if (
            self._last_progress is not None
            and now - self._last_progress < PROGRESS_MIN_INTERVAL_S
        ):
            return
        self._last_progress = now
        if self._on_progress is None:
            return
        self._on_progress(downloaded, total, speed)

    def _base_opts(self, logger: _YtDlpLogger) -> dict[str, object]:
        opts: dict[str, object] = {
            "quiet": not self._yt_dlp_debug,
            "noprogress": True,
            "logger": logger,
            "progress_hooks": [self._progress_hook],
        }
        # FFMPEG_LOCATION: read per call, so a changed ffmpeg setting reaches the next run.
        ffmpeg = self._ffmpeg_location() if self._ffmpeg_location is not None else None
        if ffmpeg is not None:
            opts["ffmpeg_location"] = str(ffmpeg.parent)
        return opts

    def _cookie_opts(self, options: DownloadOptions) -> dict[str, object]:
        if options.mode not in COOKIE_MODES:
            raise ValidationError(f"unknown cookie mode: {options.mode}")
        extra: dict[str, object] = {}
        if options.mode == "none":
            extra["extractor_args"] = SABR_EXTRACTOR_ARGS
            return extra
        extra["extractor_args"] = COOKIE_EXTRACTOR_ARGS
        if options.mode == "browser":
            extra["cookiesfrombrowser"] = (options.browser, options.profile)
            return extra
        cookie_file = options.cookie_file
        if cookie_file is None or not cookie_file.is_file():
            missing = cookie_file if cookie_file is not None else Path("cookies.txt")
            raise CookieTestError("cookie file is missing or unreadable") from FileNotFoundError(
                str(missing)
            )
        try:
            with cookie_file.open("rb"):
                pass
        except OSError as exc:
            raise CookieTestError("cookie file is missing or unreadable") from exc
        extra["cookiefile"] = str(cookie_file)
        return extra

    def _run_extract(
        self,
        url: str,
        opts: dict[str, object],
        *,
        download: bool = False,
    ) -> tuple[dict[str, object], _YtDlpLogger]:
        logger = opts.get("logger")
        if not isinstance(logger, _YtDlpLogger):
            logger = _YtDlpLogger(self._yt_dlp_debug)
            opts = {**opts, "logger": logger}
        try:
            with _ydl(opts) as ydl:
                raw = ydl.extract_info(url, download=download)
        except DownloadCancelledError:
            raise
        except CookieTestError:
            raise
        except AgeRestrictedError:
            raise
        except DownloadError as exc:
            text = str(exc).casefold()
            if any(needle in text for needle in AGE_GATE_NEEDLES):
                raise AgeRestrictedError("video is age-restricted") from exc
            raise ExtractError(str(exc) or "yt-dlp download failed") from exc
        except OSError as exc:
            raise ExtractError("yt-dlp IO failed") from exc
        if not isinstance(raw, dict):
            raise ExtractError("yt-dlp returned no info")
        return _info_dict(raw), logger

    def extract_info(self, url: str, flat: bool = False) -> VideoInfo | PlaylistInfo:
        logger = _YtDlpLogger(self._yt_dlp_debug)
        opts = self._base_opts(logger)
        opts["extract_flat"] = True if flat else False
        if self._playlist_end > 0:
            opts["playlistend"] = self._playlist_end
        info, _logger = self._run_extract(url, opts, download=False)
        if _is_playlist(info, flat):
            return _playlist_from_info(info)
        return _video_from_info(info)

    def extract_video_ids(self, channel_url: str) -> VideoListing:
        logger = _YtDlpLogger(self._yt_dlp_debug)
        opts = self._base_opts(logger)
        opts["extract_flat"] = True
        if self._playlist_end > 0:
            opts["playlistend"] = self._playlist_end
        info, _logger = self._run_extract(channel_url, opts, download=False)
        channel = _clean_text(info.get("channel")) or _clean_text(info.get("uploader"))
        if _is_playlist(info, True):
            return VideoListing(_listed_videos(info.get("entries")), channel)
        video = _video_from_info(info)
        listed = ListedVideo(video.video_id, _clean_text(info.get("title")))
        return VideoListing((listed,), channel)

    def download(self, url: str, options: DownloadOptions) -> DownloadResult:
        self._last_progress = None
        logger = _YtDlpLogger(self._yt_dlp_debug)
        opts = self._base_opts(logger)
        opts.update(self._cookie_opts(options))
        if options.audio_only:
            opts["format"] = _audio_selector(options.audio_format, options.mode)
        else:
            opts["format"] = _quality_selector(options.quality)
        opts["outtmpl"] = str(options.output_dir / "%(title)s.%(ext)s")
        try:
            with _ydl(opts) as ydl:
                info = _info_dict(ydl.extract_info(url, download=True))
                path = _result_path(info, ydl)
        except DownloadCancelledError:
            raise
        except CookieTestError:
            raise
        except AgeRestrictedError:
            raise
        except DownloadError as exc:
            text = str(exc).casefold()
            if any(needle in text for needle in AGE_GATE_NEEDLES):
                raise AgeRestrictedError("video is age-restricted") from exc
            raise DomainError(str(exc) or "yt-dlp download failed") from exc
        except OSError as exc:
            if options.mode == "file":
                raise CookieTestError("cookie file is missing or unreadable") from exc
            raise DomainError("yt-dlp IO failed") from exc
        if not path.is_file():
            raise DomainError("download completed without an output file") from FileNotFoundError(
                str(path)
            )
        video_id = info.get("id")
        title = info.get("title")
        if not isinstance(video_id, str) or video_id == "":
            raise ValidationError("downloaded video id is required")
        if not isinstance(title, str) or title == "":
            title = video_id
        result = DownloadResult(
            file_path=path,
            file_size=path.stat().st_size,
            video_id=video_id,
            title=title,
            sabr_detected=logger.sabr_detected,
        )
        log.info("youtube.download", video_id=video_id, sabr_detected=result.sabr_detected)
        return result

    def get_formats(self, video_id: str) -> list[FormatInfo]:
        extracted = self.extract_info(f"{WATCH_URL_PREFIX}{video_id}", flat=False)
        if not isinstance(extracted, VideoInfo):
            raise ValidationError("get_formats requires a single video")
        return extracted.formats

    def check_sabr_status(self) -> SABRStatus:
        logger = _YtDlpLogger(self._yt_dlp_debug)
        opts = self._base_opts(logger)
        opts["extractor_args"] = SABR_EXTRACTOR_ARGS
        _info, logger = self._run_extract(SABR_PROBE_URL, opts, download=False)
        mode = SABRMode.Active if logger.sabr_detected else SABRMode.Inactive
        return SABRStatus(mode=mode, source=SABRSource.Detected, checked_at=datetime.now(UTC))

    def test_cookies(
        self,
        mode: str,
        browser: str | None,
        profile: str | None,
        cookie_file: Path | None,
    ) -> CookieTestResult:
        if mode not in COOKIE_MODES:
            return CookieTestResult(ok=False, error_message="unknown cookie mode")
        if mode == "none":
            return CookieTestResult(ok=True, error_message=None)
        if mode == "file":
            if cookie_file is None or not cookie_file.is_file():
                return CookieTestResult(ok=False, error_message="cookie file is missing")
        try:
            options = DownloadOptions(
                quality=QualityPreset.P144,
                audio_only=False,
                audio_format=AudioFormat.Default,
                output_dir=Path("."),
                mode=mode,
                browser=browser,
                profile=profile,
                cookie_file=cookie_file,
            )
            logger = _YtDlpLogger(False)
            opts = self._base_opts(logger)
            opts.update(self._cookie_opts(options))
            with _ydl(opts) as ydl:
                ydl.extract_info(SABR_PROBE_URL, download=False)
        except CookieTestError as exc:
            return CookieTestResult(ok=False, error_message=str(exc))
        except OSError as exc:
            return CookieTestResult(ok=False, error_message=str(exc) or "cookie source unreadable")
        except DownloadError as exc:
            return CookieTestResult(ok=False, error_message=str(exc) or "cookie probe failed")
        except DomainError as exc:
            return CookieTestResult(ok=False, error_message=str(exc))
        return CookieTestResult(ok=True, error_message=None)

    def ytdlp_version(self) -> str | None:
        return _read_ytdlp_version()
