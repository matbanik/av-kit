"""MEU-140: yt-dlp's own client first, one retry on the cookie pin, and a `/best` catch-all.

`YoutubeDL` is a scripted fake: each run takes the next outcome, so a test can fail attempt 1
and pass attempt 2. Nothing reaches the network. A wrong exception is caught and asserted on,
so every failure here is an assertion (red-check).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from structlog.testing import capture_logs
from tests.integration.test_youtube_adapter import (
    AUDIO_FORMAT_SELECTORS,
    COOKIE_AUDIO_SELECTOR,
    COOKIE_EXTRACTOR_ARGS,
    QUALITY_HEIGHT,
    QUALITY_SELECTOR_BEST,
    QUALITY_SELECTOR_LOWEST,
    SABR_EXTRACTOR_ARGS,
    SABR_PROBE_URL,
    _download_error,
    _options,
    _video_info_payload,
)

from avkit_core.domain.download import DownloadOptions, DownloadResult
from avkit_core.domain.enums import AudioFormat, DownloadFailureCause, QualityPreset
from avkit_core.domain.errors import (
    AgeRestrictedError,
    CookieTestError,
    DownloadCancelledError,
    DownloadFailedError,
    ExtractError,
)

pytestmark = pytest.mark.integration

URL = "https://youtu.be/vid12345678"
COOKIE_KEYS = ("cookiesfrombrowser", "cookiefile")
#: A yt-dlp warning that names SABR, as yt-dlp 2026.10.26 writes it.
SABR_LINE = (
    "WARNING: [youtube] vid12345678: Some web client https formats have been skipped as they "
    "are missing a url. YouTube is forcing SABR streaming for this client."
)
RELOAD = "ERROR: [youtube] vid12345678: The page needs to be reloaded."
NO_FORMAT = (
    "ERROR: [youtube] vid12345678: Requested format is not available. "
    "Use --list-formats for a list of available formats"
)


class Scripted:
    """What the fake `YoutubeDL` saw: each run's opts, its download flag and its URL."""

    def __init__(self) -> None:
        self.runs: list[dict[str, Any]] = []
        self.inits = 0

    def opts(self, n: int) -> dict[str, Any]:
        assert len(self.runs) > n, (n, len(self.runs))
        return self.runs[n]["opts"]


def _script(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: list[BaseException | None],
    *,
    info: dict[str, Any] | None = None,
    sabr_lines: dict[int, str] | None = None,
    on_run: Callable[[int], None] | None = None,
) -> Scripted:
    """Patch `YoutubeDL` so run n raises `outcomes[n]`, or returns `info` when it is None.

    `sabr_lines[n]` is written to run n's logger as a warning before the run ends. A run past
    the script's end returns `info`, so a test still sees how many runs there were.
    """
    seen = Scripted()

    class FakeYDL:
        def __init__(self, opts: dict[str, Any]) -> None:
            self.opts = opts
            seen.inits += 1

        def __enter__(self) -> FakeYDL:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

        def extract_info(self, url: str, download: bool = False) -> dict[str, Any]:
            n = len(seen.runs)
            seen.runs.append({"opts": self.opts, "download": download, "url": url})
            line = (sabr_lines or {}).get(n)
            logger = self.opts.get("logger")
            if line is not None and logger is not None:
                logger.warning(line)
            if on_run is not None:
                on_run(n)
            outcome = outcomes[n] if n < len(outcomes) else None
            if outcome is not None:
                raise outcome
            return info if info is not None else _video_info_payload()

        def prepare_filename(self, extracted: dict[str, Any]) -> str:
            return str(extracted.get("_filename") or "prepared.mp4")

    monkeypatch.setattr("avkit_infra.youtube.adapter.YoutubeDL", FakeYDL)
    return seen


def _info(tmp_path: Path) -> tuple[dict[str, Any], Path]:
    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    return {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}, outfile


def _mode(tmp_path: Path, mode: str) -> DownloadOptions:
    if mode == "browser":
        return _options(tmp_path, mode="browser", browser="firefox", profile="p1")
    if mode == "file":
        cookie = tmp_path / "cookies.txt"
        cookie.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
        return _options(tmp_path, mode="file", cookie_file=cookie)
    return _options(tmp_path, mode="none")


def _download(
    options: DownloadOptions, should_stop: Callable[[], bool] | None = None
) -> tuple[DownloadResult | None, BaseException | None]:
    """`download`'s result or the exception it raised, so a wrong class fails by assertion."""
    from avkit_infra.youtube.adapter import YouTubeAdapter

    try:
        return YouTubeAdapter(should_stop=should_stop).download(URL, options), None
    except Exception as exc:  # noqa: BLE001 - the exception is the observation
        return None, exc


def _shape(exc: BaseException | None) -> tuple[type[BaseException] | None, object, object]:
    return (
        None if exc is None else type(exc),
        getattr(exc, "cause", None),
        getattr(exc, "detail", None),
    )


# --- AC-140.1: ATTEMPT_OPTS ------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["none", "browser", "file"])
def test_ac_140_1_attempt_one_sets_no_extractor_args(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    info, _outfile = _info(tmp_path)
    seen = _script(monkeypatch, [None], info=info)
    options = _mode(tmp_path, mode)
    result, raised = _download(options)
    assert raised is None, repr(raised)
    assert result is not None
    assert len(seen.runs) == 1
    first = seen.opts(0)
    assert "extractor_args" not in first, first.get("extractor_args")
    if mode == "browser":
        assert first.get("cookiesfrombrowser") == ("firefox", "p1")
    elif mode == "file":
        assert first.get("cookiefile") == str(options.cookie_file)
    else:
        assert [key for key in COOKIE_KEYS if key in first] == []


@pytest.mark.parametrize("mode", ["none", "browser", "file"])
def test_ac_140_1_attempt_opts_by_attempt(tmp_path: Path, mode: str) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    adapter = YouTubeAdapter()
    assert hasattr(adapter, "_attempt_opts")
    options = _mode(tmp_path, mode)
    first = adapter._attempt_opts(options, 1)
    second = adapter._attempt_opts(options, 2)
    assert "extractor_args" not in first, first.get("extractor_args")
    assert second.get("extractor_args") == COOKIE_EXTRACTOR_ARGS
    for key in COOKIE_KEYS:
        assert first.get(key) == second.get(key), key
    assert {key for key in second if key != "extractor_args"} == set(first)


# --- AC-140.2: CATCH_ALL ---------------------------------------------------------------------


def test_ac_140_2_height_selectors_end_with_best_catch_all() -> None:
    from avkit_infra.youtube.adapter import _audio_selector, _quality_selector

    for preset, height in QUALITY_HEIGHT.items():
        assert _quality_selector(preset) == (
            f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        ), preset
    assert _quality_selector(QualityPreset.Best) == QUALITY_SELECTOR_BEST
    assert _quality_selector(QualityPreset.Lowest) == QUALITY_SELECTOR_LOWEST
    assert set(AUDIO_FORMAT_SELECTORS) == set(AudioFormat)
    for audio_format, selector in AUDIO_FORMAT_SELECTORS.items():
        assert _audio_selector(audio_format, "none") == selector, audio_format
        assert _audio_selector(audio_format, "browser") == COOKIE_AUDIO_SELECTOR
        assert _audio_selector(audio_format, "file") == COOKIE_AUDIO_SELECTOR


def test_ac_140_2_download_passes_the_catch_all_format(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    info, _outfile = _info(tmp_path)
    seen = _script(monkeypatch, [None], info=info)
    result, raised = _download(_options(tmp_path, quality=QualityPreset.P720))
    assert raised is None, repr(raised)
    assert result is not None
    assert seen.opts(0).get("format") == "bestvideo[height<=720]+bestaudio/best[height<=720]/best"


# --- AC-140.3: RETRY_ONCE on a client-side error ---------------------------------------------

#: (id, attempt 1's error text, the SABR line attempt 1's log holds or None).
CLIENT_SIDE_CASES = [
    ("reload", RELOAD, None),
    ("requested_format", NO_FORMAT, None),
    ("no_video_formats", "ERROR: [youtube] vid12345678: No video formats found!", None),
    ("only_images", "ERROR: [youtube] vid12345678: Only images are available for download.", None),
    ("sabr_in_text", "ERROR: [youtube] vid12345678: YouTube is forcing SABR streaming", None),
    ("sabr_in_log_only", "ERROR: boom", SABR_LINE),
]


@pytest.mark.parametrize("mode", ["none", "browser", "file"])
@pytest.mark.parametrize(
    ("text", "line"),
    [(text, line) for _id, text, line in CLIENT_SIDE_CASES],
    ids=[case_id for case_id, _text, _line in CLIENT_SIDE_CASES],
)
def test_ac_140_3_retries_once_on_cookie_pin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str, text: str, line: str | None
) -> None:
    info, outfile = _info(tmp_path)
    sabr_lines = {0: line} if line is not None else None
    seen = _script(monkeypatch, [_download_error(text), None], info=info, sabr_lines=sabr_lines)
    result, raised = _download(_mode(tmp_path, mode))
    assert raised is None, repr(raised)
    assert len(seen.runs) == 2
    first, second = seen.opts(0), seen.opts(1)
    assert "extractor_args" not in first, first.get("extractor_args")
    assert second.get("extractor_args") == COOKIE_EXTRACTOR_ARGS
    for key in COOKIE_KEYS:
        assert first.get(key) == second.get(key), key
    assert isinstance(result, DownloadResult)
    assert result.file_path == outfile
    assert result.video_id == "vid12345678"


@pytest.mark.parametrize("mode", ["none", "browser", "file"])
def test_ac_140_3_attempt_two_fails_with_its_cause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    info, _outfile = _info(tmp_path)
    seen = _script(
        monkeypatch,
        [_download_error(RELOAD), _download_error(NO_FORMAT), None],
        info=info,
    )
    result, raised = _download(_mode(tmp_path, mode))
    assert result is None
    assert len(seen.runs) == 2
    assert _shape(raised) == (
        DownloadFailedError,
        DownloadFailureCause.no_format,
        NO_FORMAT.removeprefix("ERROR: "),
    )


# --- AC-140.4: no retry (a guard: holds at 0553779) --------------------------------------------

BOT = "ERROR: [youtube] x: Sign in to confirm you're not a bot. Use --cookies-from-browser"
BOT_CURLY = "ERROR: [youtube] x: Sign in to confirm you’re not a bot. Use --cookies-from-browser"
COPY_DB = "ERROR: Could not copy Chrome cookie database. See yt-dlp#7271"
DPAPI = "ERROR: Failed to decrypt with DPAPI. See yt-dlp#10927"
COOKIES_DB = "ERROR: [Cookies] The cookies database could not be read"
OPEN_WRITE = "ERROR: unable to open for writing: [Errno 13] Permission denied"
WRITE_DATA = "ERROR: unable to write data: [Errno 28] No space left on device"
FORMAT_THEN_COOKIE = (
    "ERROR: [youtube] x: Requested format is not available\n"
    "ERROR: Could not copy Chrome cookie database"
)
CANCELLED = DownloadCancelledError("download cancelled")
COOKIE_ERROR = CookieTestError("cookie file is missing or unreadable")
DENIED = PermissionError(13, "Permission denied")

R = DownloadFailureCause


def _drop(text: str) -> str:
    return text.removeprefix("ERROR: ").split("\n", 1)[0]


#: (id, mode, attempt 1's error, a SABR line in attempt 1's log, the expected shape; a None
#: shape means the very error object raised).
NO_RETRY_CASES: list[tuple[str, str, BaseException, str | None, tuple[Any, ...] | None]] = [
    (
        "bot_straight",
        "none",
        _download_error(BOT),
        None,
        (DownloadFailedError, R.refused, _drop(BOT)),
    ),
    (
        "bot_curly",
        "browser",
        _download_error(BOT_CURLY),
        None,
        (DownloadFailedError, R.refused, _drop(BOT_CURLY)),
    ),
    (
        "cookie_copy",
        "browser",
        _download_error(COPY_DB),
        None,
        (DownloadFailedError, R.cookies, _drop(COPY_DB)),
    ),
    (
        "cookie_dpapi",
        "browser",
        _download_error(DPAPI),
        None,
        (DownloadFailedError, R.cookies, _drop(DPAPI)),
    ),
    (
        "cookie_db",
        "none",
        _download_error(COOKIES_DB),
        None,
        (DownloadFailedError, R.cookies, _drop(COOKIES_DB)),
    ),
    (
        "write_open",
        "none",
        _download_error(OPEN_WRITE),
        None,
        (DownloadFailedError, R.write_failed, _drop(OPEN_WRITE)),
    ),
    (
        "write_data",
        "file",
        _download_error(WRITE_DATA),
        None,
        (DownloadFailedError, R.write_failed, _drop(WRITE_DATA)),
    ),
    (
        "other_text",
        "none",
        _download_error("ERROR: boom"),
        None,
        (DownloadFailedError, R.other, "boom"),
    ),
    ("cancelled", "none", CANCELLED, None, None),
    ("cookie_test_error", "file", COOKIE_ERROR, None, None),
    (
        "age_sign_in",
        "none",
        _download_error("ERROR: [youtube] x: Sign in to confirm your age."),
        None,
        (AgeRestrictedError, None, None),
    ),
    (
        "age_restricted",
        "browser",
        _download_error("ERROR: [youtube] x: This video is age-restricted"),
        None,
        (AgeRestrictedError, None, None),
    ),
    (
        "os_error_none",
        "none",
        DENIED,
        None,
        (DownloadFailedError, R.write_failed, "PermissionError: Permission denied"),
    ),
    ("os_error_file", "file", DENIED, None, (CookieTestError, None, None)),
    (
        "sabr_log_then_bot",
        "none",
        _download_error(BOT),
        SABR_LINE,
        (DownloadFailedError, R.refused, _drop(BOT)),
    ),
    (
        "sabr_log_then_cookie",
        "browser",
        _download_error(COPY_DB),
        SABR_LINE,
        (DownloadFailedError, R.cookies, _drop(COPY_DB)),
    ),
    (
        "sabr_log_then_write",
        "none",
        _download_error(OPEN_WRITE),
        SABR_LINE,
        (DownloadFailedError, R.write_failed, _drop(OPEN_WRITE)),
    ),
    (
        "format_then_cookie_lines",
        "none",
        _download_error(FORMAT_THEN_COOKIE),
        None,
        (DownloadFailedError, R.no_format, _drop(FORMAT_THEN_COOKIE)),
    ),
]


@pytest.mark.parametrize(
    ("mode", "error", "line", "shape"),
    [(mode, error, line, shape) for _id, mode, error, line, shape in NO_RETRY_CASES],
    ids=[case[0] for case in NO_RETRY_CASES],
)
def test_ac_140_4_no_retry_runs_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    error: BaseException,
    line: str | None,
    shape: tuple[Any, ...] | None,
) -> None:
    info, _outfile = _info(tmp_path)
    sabr_lines = {0: line} if line is not None else None
    seen = _script(monkeypatch, [error, None], info=info, sabr_lines=sabr_lines)
    result, raised = _download(_mode(tmp_path, mode))
    assert result is None
    assert len(seen.runs) == 1
    if shape is None:
        assert raised is error
    else:
        assert _shape(raised) == shape


# --- AC-140.5: a stop between the attempts ---------------------------------------------------


@pytest.mark.parametrize("stop", [True, False], ids=["stop_requested", "no_stop"])
def test_ac_140_5_stop_between_attempts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stop: bool
) -> None:
    info, _outfile = _info(tmp_path)
    flag = {"stop": False}

    def on_run(n: int) -> None:
        # The stop arrives while attempt 1 runs, after its progress hooks.
        if n == 0:
            flag["stop"] = stop

    seen = _script(monkeypatch, [_download_error(RELOAD), None], info=info, on_run=on_run)
    result, raised = _download(_mode(tmp_path, "none"), should_stop=lambda: flag["stop"])
    if stop:
        assert result is None
        assert isinstance(raised, DownloadCancelledError), repr(raised)
        assert len(seen.runs) == 1
    else:
        assert raised is None, repr(raised)
        assert isinstance(result, DownloadResult)
        assert len(seen.runs) == 2


# --- AC-140.8: SABR_ACROSS and the attempt on youtube.download -------------------------------


def _download_events(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in logs if event.get("event") == "youtube.download"]


def test_ac_140_8_sabr_in_attempt_one_sets_sabr_detected_after_attempt_two(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    info, _outfile = _info(tmp_path)
    _script(
        monkeypatch, [_download_error("ERROR: boom"), None], info=info, sabr_lines={0: SABR_LINE}
    )
    with capture_logs() as logs:
        result, raised = _download(_mode(tmp_path, "none"))
    assert raised is None, repr(raised)
    assert isinstance(result, DownloadResult)
    assert result.sabr_detected is True
    events = _download_events(logs)
    assert len(events) == 1
    assert events[0].get("attempt") == 2
    assert events[0].get("sabr_detected") is True


def test_ac_140_8_no_sabr_in_either_attempt_gives_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    info, _outfile = _info(tmp_path)
    _script(monkeypatch, [_download_error(RELOAD), None], info=info)
    with capture_logs() as logs:
        result, raised = _download(_mode(tmp_path, "browser"))
    assert raised is None, repr(raised)
    assert isinstance(result, DownloadResult)
    assert result.sabr_detected is False
    events = _download_events(logs)
    assert len(events) == 1
    assert events[0].get("attempt") == 2


def test_ac_140_8_a_first_attempt_pass_logs_attempt_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    info, _outfile = _info(tmp_path)
    _script(monkeypatch, [None], info=info, sabr_lines={0: SABR_LINE})
    with capture_logs() as logs:
        result, raised = _download(_mode(tmp_path, "none"))
    assert raised is None, repr(raised)
    assert isinstance(result, DownloadResult)
    assert result.sabr_detected is True
    events = _download_events(logs)
    assert len(events) == 1
    assert events[0].get("attempt") == 1


# --- AC-140.12: check_sabr_status is unchanged (a guard) -------------------------------------


def test_ac_140_12_check_sabr_status_runs_once_on_the_sabr_pin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    seen = _script(monkeypatch, [None])
    status = YouTubeAdapter().check_sabr_status()
    assert len(seen.runs) == 1
    assert seen.opts(0).get("extractor_args") == SABR_EXTRACTOR_ARGS
    assert seen.runs[0]["url"] == SABR_PROBE_URL
    assert seen.runs[0]["download"] is False
    assert [key for key in COOKIE_KEYS if key in seen.opts(0)] == []
    assert status.matched_phrase is None


def test_ac_140_12_check_sabr_status_error_does_not_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    seen = _script(monkeypatch, [_download_error(RELOAD), None])
    raised: BaseException | None = None
    try:
        YouTubeAdapter().check_sabr_status()
    except Exception as exc:  # noqa: BLE001 - the exception is the observation
        raised = exc
    assert isinstance(raised, ExtractError), repr(raised)
    assert len(seen.runs) == 1
