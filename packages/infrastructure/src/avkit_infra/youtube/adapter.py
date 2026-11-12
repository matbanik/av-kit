"""YouTubePort adapter backed by the yt-dlp library (no CLI shell-out)."""

from __future__ import annotations

import math
import re
import time
import unicodedata
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeVar, cast

import structlog
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from avkit_core.domain.download import (
    ANSI_CSI,
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
from avkit_core.domain.enums import (
    AudioFormat,
    DownloadFailureCause,
    QualityPreset,
    SABRMode,
    SABRSource,
)
from avkit_core.domain.errors import (
    AgeRestrictedError,
    CookieTestError,
    DomainError,
    DownloadCancelledError,
    DownloadFailedError,
    ExtractError,
    ValidationError,
)
from avkit_core.services.download import first_line, scrub_line
from avkit_infra.youtube.js_runtime import JsRuntime

log = structlog.get_logger(module="youtube")
T = TypeVar("T")

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
# SABR_MATCH (D-623, D-624): yt-dlp 2026.10.26's own SABR words, matched as whole words.
# They replace the three old needles, which `require a gvs po token` and `sabr` still match.
SABR_PHRASES: tuple[str, ...] = ("forcing sabr", "missing a url", "require a gvs po token", "sabr")
# FAILURE_CAUSE (D-636): each cause with the case-folded needles that name it, in order.
FAILURE_CAUSE_NEEDLES: tuple[tuple[DownloadFailureCause, tuple[str, ...]], ...] = (
    (
        DownloadFailureCause.refused,
        ("the page needs to be reloaded", "confirm you're not a bot", "confirm you’re not a bot"),
    ),
    (
        DownloadFailureCause.no_format,
        (
            "requested format is not available",
            "no video formats found",
            "only images are available",
        ),
    ),
    (
        DownloadFailureCause.cookies,
        (
            "could not copy chrome cookie database",
            "failed to decrypt with dpapi",
            "cookies database",
        ),
    ),
    (DownloadFailureCause.write_failed, ("unable to open for writing", "unable to write data")),
)
# FAILURE_CAUSE (D-639): a leading `ERROR:` with the ANSI codes and whitespace around it.
_ERROR_PREFIX = re.compile(rf"^(?:{ANSI_CSI.pattern}|\s)*ERROR:(?:{ANSI_CSI.pattern}|\s)*")
SABR_PROBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
AGE_GATE_NEEDLES = ("sign in to confirm your age", "age-restricted")
# CLIENT_SIDE (D-643): the needles that refuse a retry wherever they appear, and the ones that
# select it. Both come from FAILURE_CAUSE_NEEDLES; the bot check is `refused` but never retries.
_CAUSE_NEEDLES = dict(FAILURE_CAUSE_NEEDLES)
RELOAD_NEEDLE = "the page needs to be reloaded"
NO_RETRY_NEEDLES: tuple[str, ...] = (
    *AGE_GATE_NEEDLES,
    *(needle for needle in _CAUSE_NEEDLES[DownloadFailureCause.refused] if needle != RELOAD_NEEDLE),
    *_CAUSE_NEEDLES[DownloadFailureCause.cookies],
    *_CAUSE_NEEDLES[DownloadFailureCause.write_failed],
)
RETRY_NEEDLES: tuple[str, ...] = (*_CAUSE_NEEDLES[DownloadFailureCause.no_format], RELOAD_NEEDLE)
# ATTEMPT_LOG: the `clients` each attempt names; constants, never yt-dlp text.
ATTEMPT_CLIENTS: dict[int, str] = {1: "default", 2: "tv,web_safari,web"}
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
    # CATCH_ALL: `/best` takes whatever the client offers when no format fits the height.
    return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"


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


def _flat_entries(entries: object) -> list[object]:
    """`FLAT_TABS` (D-358): each channel tab's entries in place of the tab, one level deep."""
    if not isinstance(entries, list):
        return []
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
    return flat


def _listed_videos(entries: object) -> tuple[ListedVideo, ...]:
    """Each entry's video, the first title winning (`FLAT_TABS`, D-358).

    An entry whose `_type` is `playlist` is a channel tab: it gives its own entries' videos,
    one level deep, and never its own ID (the channel's) or title (the tab's).
    """
    if not isinstance(entries, list):
        return ()
    videos: list[ListedVideo] = []
    seen: set[str] = set()
    for entry in _flat_entries(entries):
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
        video_ids=_unique_preserve_ids(_flat_entries(info.get("entries"))),
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


def sabr_phrase(text: str) -> str | None:
    """The first `SABR_PHRASES` entry in `text` as a whole word, else None (`SABR_MATCH`)."""
    folded = text.casefold()
    for phrase in SABR_PHRASES:
        if re.search(rf"\b{re.escape(phrase)}\b", folded):
            return phrase
    return None


def classify_download_error(text: str, sabr_matched: bool) -> tuple[DownloadFailureCause, str]:
    """The cause and the first line of yt-dlp's error text (`FAILURE_CAUSE`, D-636).

    `detail` is `first_line(text)` as written, with only a leading `ERROR:` and the ANSI codes
    and whitespace around it dropped (D-639): the service's `scrub_line` cleans it, so a split
    inside a secret or the home folder reaches the scrubbers. The cause is the first needle's,
    else `refused` when a SABR phrase is found, else `other`; a `no_format` becomes `refused`
    when the download's log matched SABR.
    """
    detail = _ERROR_PREFIX.sub("", first_line(text), count=1)
    folded = text.casefold()
    cause = next(
        (
            candidate
            for candidate, needles in FAILURE_CAUSE_NEEDLES
            if any(needle in folded for needle in needles)
        ),
        None,
    )
    if cause is None:
        found = sabr_phrase(text) is not None
        cause = DownloadFailureCause.refused if found else DownloadFailureCause.other
    if cause is DownloadFailureCause.no_format and sabr_matched:
        cause = DownloadFailureCause.refused
    return (cause, detail)


def client_side_error(text: str, sabr_matched: bool) -> bool:
    """Whether a failed attempt's error is one another client may avoid (`CLIENT_SIDE`, D-643).

    Two steps over the whole case-folded text: a refusing needle anywhere is never client-side,
    whatever else the text or the log holds; otherwise a format or reload-page needle, a SABR
    phrase in the text, or a SABR match in the attempt's log is.
    """
    folded = text.casefold()
    if any(needle in folded for needle in NO_RETRY_NEEDLES):
        return False
    if any(needle in folded for needle in RETRY_NEEDLES):
        return True
    return sabr_phrase(text) is not None or sabr_matched


def _is_age_gate(text: str) -> bool:
    folded = text.casefold()
    return any(needle in folded for needle in AGE_GATE_NEEDLES)


def _extract_failure(exc: DownloadError) -> DomainError:
    """An extract's DownloadError as the domain error it raises."""
    if _is_age_gate(str(exc)):
        return AgeRestrictedError("video is age-restricted")
    return ExtractError(str(exc) or "yt-dlp download failed")


def _download_failure(exc: DownloadError, logger: _YtDlpLogger) -> DomainError:
    """A download's DownloadError as the domain error it raises (FAILURE_RAISE, D-637)."""
    if _is_age_gate(str(exc)):
        return AgeRestrictedError("video is age-restricted")
    # The cause and yt-dlp's first line, read with the failing attempt's own log.
    cause, detail = classify_download_error(str(exc), logger.sabr_detected)
    return DownloadFailedError(cause, detail)


class _YtDlpLogger:
    def __init__(self, debug_enabled: bool) -> None:
        self.matched_phrase: str | None = None
        self.debug_enabled = debug_enabled
        self._log = structlog.get_logger(module="yt-dlp")

    @property
    def sabr_detected(self) -> bool:
        """True once a line held a SABR phrase (`SABR_SCAN`); read-only."""
        return self.matched_phrase is not None

    def _scan(self, message: object) -> str:
        text = str(message)
        # SABR_SCAN: the first line with a phrase sets it, and it never changes after.
        if self.matched_phrase is None:
            self.matched_phrase = sabr_phrase(text)
        return text

    def _emit(self, level: str, detail: str) -> None:
        # YTDLP_LINE: `detail` only, already scrubbed; a line that scrubs to nothing logs nothing.
        if detail != "":
            getattr(self._log, level)("yt-dlp", detail=detail)

    def debug(self, message: object) -> None:
        text = self._scan(message)
        if self.debug_enabled:
            self._emit("debug", scrub_line(text))

    def info(self, message: object) -> None:
        text = self._scan(message)
        if self.debug_enabled:
            self._emit("debug", scrub_line(text))

    def warning(self, message: object) -> None:
        self._emit("warning", scrub_line(self._scan(message)))

    def error(self, message: object) -> None:
        detail = scrub_line(self._scan(message))
        # D-632: only an `ERROR:` line is an error; a bare traceback is a debug line. The
        # prefix is read after cleaning, so a coloured `ERROR:` still counts.
        if detail.startswith("ERROR:"):
            self._emit("error", detail)
        elif self.debug_enabled:
            self._emit("debug", detail)


class YouTubeAdapter:
    """Library-backed YouTubePort. Cookie bytes never enter opts or logs."""

    def __init__(
        self,
        *,
        playlist_end: int = 0,
        on_progress: Callable[[int, int | None, float | None], None] | None = None,
        should_stop: Callable[[], bool] | None = None,
        yt_dlp_debug: Callable[[], bool] | None = None,
        ffmpeg_location: Callable[[], Path | None] | None = None,
        js_runtime: Callable[[], JsRuntime | None] | None = None,
    ) -> None:
        if not isinstance(playlist_end, int) or isinstance(playlist_end, bool) or playlist_end < 0:
            raise ValidationError("playlist_end must be a non-negative int")
        self._playlist_end = playlist_end
        self._on_progress = on_progress
        self._should_stop = should_stop
        self._yt_dlp_debug = yt_dlp_debug
        self._ffmpeg_location = ffmpeg_location
        self._js_runtime = js_runtime
        self._last_progress: float | None = None

    def _debug_now(self) -> bool:
        """YTDLP_LIVE: the debug switch, read once per public call.

        No source, a source that raises and any answer but True all read as off.
        """
        if self._yt_dlp_debug is None:
            return False
        try:
            return self._yt_dlp_debug() is True
        except Exception:  # noqa: BLE001 - an unreadable switch is off
            return False

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
            "quiet": not logger.debug_enabled,
            "verbose": logger.debug_enabled,
            "noprogress": True,
            "logger": logger,
            "progress_hooks": [self._progress_hook],
        }
        # FFMPEG_LOCATION: read per call, so a changed ffmpeg setting reaches the next run.
        ffmpeg = self._ffmpeg_location() if self._ffmpeg_location is not None else None
        if ffmpeg is not None:
            opts["ffmpeg_location"] = str(ffmpeg.parent)
        # JS_RUNTIME_OPTS: read per call; no runtime leaves the key out.
        runtime = self._runtime_now()
        if runtime is not None:
            opts["js_runtimes"] = {runtime.name: {"path": str(runtime.path)}}
        return opts

    def _runtime_now(self) -> JsRuntime | None:
        """The JS runtime for this call; no source or a source that raises gives None."""
        if self._js_runtime is None:
            return None
        try:
            found = self._js_runtime()
        except Exception:  # noqa: BLE001 - an unreadable runtime leaves the key out
            return None
        return found if isinstance(found, JsRuntime) else None

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

    def _attempt_opts(self, options: DownloadOptions, attempt: int) -> dict[str, object]:
        """The cookie and client options for one attempt (`ATTEMPT_OPTS`).

        Attempt 1 leaves the client choice to yt-dlp (no `extractor_args`) in every mode;
        attempt 2 pins `COOKIE_EXTRACTOR_ARGS`. Both keep `_cookie_opts`' cookies, and a missing
        cookie file raises `CookieTestError` before any run.
        """
        if attempt not in ATTEMPT_CLIENTS:
            raise ValidationError(f"unknown attempt: {attempt}")
        extra = self._cookie_opts(options)
        extra.pop("extractor_args", None)
        if attempt == 2:
            extra["extractor_args"] = COOKIE_EXTRACTOR_ARGS
        return extra

    def _attempt_sequence(
        self,
        url: str,
        options: DownloadOptions,
        opts_for: Callable[[_YtDlpLogger], dict[str, object]],
        run: Callable[[YoutubeDL], T],
        fail: Callable[[DownloadError, _YtDlpLogger], DomainError],
        *,
        stoppable: bool,
    ) -> tuple[T, int, bool]:
        """Attempt 1, then attempt 2 once on a client-side error (`RETRY_ONCE`, D-643).

        `download` and `extract_info` with options both run this. It returns `run`'s value, the
        passing attempt and whether either attempt's log matched a SABR phrase (`SABR_ACROSS`).
        A DownloadError that does not retry, and attempt 2's, is raised as `fail` maps it with
        that attempt's own logger; every other exception is raised as `run` raised it. When
        `stoppable`, a stop requested during attempt 1 raises `DownloadCancelledError` and
        runs no attempt 2 (D-656: the add-time extract has no job to stop).
        """
        debug = self._debug_now()
        sabr_seen = False
        attempt = 1
        while True:
            extra = self._attempt_opts(options, attempt)
            logger = _YtDlpLogger(debug)
            opts = opts_for(logger)
            opts.update(extra)
            self._last_progress = None
            try:
                with _ydl(opts) as ydl:
                    value = run(ydl)
            except DownloadError as exc:
                sabr_seen = sabr_seen or logger.sabr_detected
                text = str(exc)
                if attempt == 2 or not client_side_error(text, logger.sabr_detected):
                    raise fail(exc, logger) from exc
                if stoppable and self._should_stop is not None and self._should_stop():
                    raise DownloadCancelledError("download cancelled") from exc
                # ATTEMPT_LOG (D-644, D-655): yt-dlp's text only through scrub_line.
                cause, detail = classify_download_error(text, logger.sabr_detected)
                log.warning(
                    "youtube.attempt_failed",
                    attempt=attempt,
                    clients=ATTEMPT_CLIENTS[attempt],
                    cause=cause,
                    detail=scrub_line(detail),
                )
                attempt = 2
                continue
            return value, attempt, sabr_seen or logger.sabr_detected

    def _run_extract(
        self,
        url: str,
        opts: dict[str, object],
        *,
        download: bool = False,
    ) -> tuple[dict[str, object], _YtDlpLogger]:
        logger = opts.get("logger")
        if not isinstance(logger, _YtDlpLogger):
            logger = _YtDlpLogger(self._debug_now())
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
            raise _extract_failure(exc) from exc
        except OSError as exc:
            raise ExtractError("yt-dlp IO failed") from exc
        if not isinstance(raw, dict):
            raise ExtractError("yt-dlp returned no info")
        return _info_dict(raw), logger

    def _extract_opts(self, logger: _YtDlpLogger, flat: bool) -> dict[str, object]:
        opts = self._base_opts(logger)
        opts["extract_flat"] = True if flat else False
        if self._playlist_end > 0:
            opts["playlistend"] = self._playlist_end
        return opts

    def extract_info(
        self, url: str, flat: bool = False, options: DownloadOptions | None = None
    ) -> VideoInfo | PlaylistInfo:
        if options is None:
            # The transcript path: no cookies, one run, as before (ADD_OPTS).
            opts = self._extract_opts(_YtDlpLogger(self._debug_now()), flat)
            info, _logger = self._run_extract(url, opts, download=False)
        else:
            # ADD_OPTS (D-646): the add-time extract runs the download's attempt sequence.
            try:
                raw, _attempt, _sabr = self._attempt_sequence(
                    url,
                    options,
                    lambda logger: self._extract_opts(logger, flat),
                    lambda ydl: ydl.extract_info(url, download=False),
                    lambda exc, _logger: _extract_failure(exc),
                    stoppable=False,
                )
            except OSError as exc:
                raise ExtractError("yt-dlp IO failed") from exc
            if not isinstance(raw, dict):
                raise ExtractError("yt-dlp returned no info")
            info = _info_dict(raw)
        if _is_playlist(info, flat):
            return _playlist_from_info(info)
        return _video_from_info(info)

    def extract_video_ids(self, channel_url: str) -> VideoListing:
        logger = _YtDlpLogger(self._debug_now())
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
        # A missing cookie file raises CookieTestError before the format is chosen, as before.
        self._cookie_opts(options)
        if options.audio_only:
            selector = _audio_selector(options.audio_format, options.mode)
        else:
            selector = _quality_selector(options.quality)

        def opts_for(logger: _YtDlpLogger) -> dict[str, object]:
            opts = self._base_opts(logger)
            opts["format"] = selector
            opts["outtmpl"] = str(options.output_dir / "%(title)s.%(ext)s")
            return opts

        def run(ydl: YoutubeDL) -> tuple[dict[str, object], Path]:
            info = _info_dict(ydl.extract_info(url, download=True))
            return info, _result_path(info, ydl)

        try:
            (info, path), attempt, sabr_detected = self._attempt_sequence(
                url, options, opts_for, run, _download_failure, stoppable=True
            )
        except DownloadCancelledError:
            raise
        except CookieTestError:
            raise
        except AgeRestrictedError:
            raise
        except OSError as exc:
            if options.mode == "file":
                raise CookieTestError("cookie file is missing or unreadable") from exc
            # The error's type and strerror only, never its filename (D-637).
            reason = f"{type(exc).__name__}: {exc.strerror or ''}".rstrip(": ")
            raise DownloadFailedError(DownloadFailureCause.write_failed, reason) from exc
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
        raw_height = info.get("height")
        height = (
            raw_height
            if isinstance(raw_height, int) and not isinstance(raw_height, bool) and raw_height > 0
            else None
        )
        result = DownloadResult(
            file_path=path,
            file_size=path.stat().st_size,
            video_id=video_id,
            title=title,
            sabr_detected=sabr_detected,
            height=height,
        )
        log.info(
            "youtube.download",
            video_id=video_id,
            sabr_detected=result.sabr_detected,
            attempt=attempt,
        )
        return result

    def get_formats(self, video_id: str) -> list[FormatInfo]:
        extracted = self.extract_info(f"{WATCH_URL_PREFIX}{video_id}", flat=False)
        if not isinstance(extracted, VideoInfo):
            raise ValidationError("get_formats requires a single video")
        return extracted.formats

    def check_sabr_status(self) -> SABRStatus:
        logger = _YtDlpLogger(self._debug_now())
        opts = self._base_opts(logger)
        opts["extractor_args"] = SABR_EXTRACTOR_ARGS
        _info, logger = self._run_extract(SABR_PROBE_URL, opts, download=False)
        mode = SABRMode.Active if logger.sabr_detected else SABRMode.Inactive
        # SABR_RESULT: the phrase the scan matched travels with an Active result.
        return SABRStatus(
            mode=mode,
            source=SABRSource.Detected,
            checked_at=datetime.now(UTC),
            matched_phrase=logger.matched_phrase if mode is SABRMode.Active else None,
        )

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
            logger = _YtDlpLogger(self._debug_now())
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
