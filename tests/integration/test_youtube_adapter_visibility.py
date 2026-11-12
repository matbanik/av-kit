"""MEU-137 FAILURE_RAISE, MEU-138 SABR_RESULT and MEU-139 YTDLP_LIVE in the adapter.

Mocked yt-dlp only.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from structlog.testing import capture_logs
from tests.integration.test_youtube_adapter import (
    _download_error,
    _options,
    _patch_ydl,
    _video_info_payload,
)
from tests.unit.test_download_failure_visibility import HOME, _home, _sqlite_stack

from avkit_core.domain.download import VideoInfo
from avkit_core.domain.enums import (
    AudioFormat,
    DownloadFailureCause,
    DownloadStatus,
    QualityPreset,
    SABRMode,
    SABRSource,
)
from avkit_core.domain.errors import AgeRestrictedError, CookieTestError, DownloadFailedError

pytestmark = pytest.mark.integration

URL = "https://youtu.be/vid12345678"
MARKER = "C:\\Users\\S65HOMEMARKER"
#: yt-dlp 2026.10.26's warning, as captured on 2026-11-10 (build plan 02 §SABR check result).
SABR_CAPTURED = (
    "WARNING: [youtube] x: Some android client https formats have been skipped as they are "
    "missing a URL. YouTube may have enabled the SABR-only streaming experiment for the "
    "current session. See https://github.com/yt-dlp/yt-dlp/issues/12482 for more details"
)


def _raised(tmp_path: Path, **overrides: object) -> BaseException | None:
    """The exception `download` raised, or None, so a wrong class fails by assertion."""
    from avkit_infra.youtube.adapter import YouTubeAdapter

    try:
        YouTubeAdapter().download(URL, _options(tmp_path, **overrides))
    except Exception as exc:  # noqa: BLE001 - the exception is the observation
        return exc
    return None


def _failed(exc: BaseException | None) -> tuple[type[BaseException] | None, object, object]:
    return (
        None if exc is None else type(exc),
        getattr(exc, "cause", None),
        getattr(exc, "detail", None),
    )


def test_ac_137_6_page_reload_raises_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    error = _download_error("ERROR: [youtube] x: The page needs to be reloaded.")
    _patch_ydl(monkeypatch, error=error)
    exc = _raised(tmp_path)
    assert _failed(exc) == (
        DownloadFailedError,
        DownloadFailureCause.refused,
        "[youtube] x: The page needs to be reloaded.",
    )
    assert exc is not None and exc.__cause__ is error


def test_ac_137_6_sabr_warning_turns_no_format_into_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_ydl(
        monkeypatch,
        sabr_msg="WARNING: [youtube] x: Some formats require a GVS PO Token which was not provided",
        error=_download_error("ERROR: [youtube] x: Requested format is not available"),
    )
    assert _failed(_raised(tmp_path)) == (
        DownloadFailedError,
        DownloadFailureCause.refused,
        "[youtube] x: Requested format is not available",
    )


def test_ac_137_6_write_error_names_no_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    error = OSError(13, "Permission denied", f"{MARKER}/x.mp4")
    assert type(error) is PermissionError
    _patch_ydl(monkeypatch, error=error)
    exc = _raised(tmp_path, mode="browser", browser="chrome", profile="Default")
    assert _failed(exc) == (
        DownloadFailedError,
        DownloadFailureCause.write_failed,
        "PermissionError: Permission denied",
    )
    assert MARKER.casefold() not in str(exc).casefold()
    assert MARKER.casefold() not in str(getattr(exc, "detail", "")).casefold()


def test_ac_137_6_file_mode_and_age_gate_keep_their_types(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape", encoding="utf-8")
    _patch_ydl(monkeypatch, error=OSError(13, "Permission denied", f"{MARKER}/x.mp4"))
    in_file_mode = _raised(tmp_path, mode="file", cookie_file=cookie)
    assert type(in_file_mode) is CookieTestError

    _patch_ydl(
        monkeypatch, error=_download_error("ERROR: [youtube] x: Sign in to confirm your age")
    )
    assert type(_raised(tmp_path)) is AgeRestrictedError


#: AC-137.12 (D-639): yt-dlp text whose secret, link or home folder a character splits. The
#: classifier and the service hand the line to `scrub_line` as written, so the split survives
#: until the scrubbers see it. The home parts never appear whole once scrubbed.
HOME_PARTS = ("S65HOME", "MARKER")
HOME_TAB = "C:\\Users\\S65HOME\tMARKER"
HOME_LS = "C:\\Users\\S65HOME\u2028MARKER"
HOME_NEL = "C:\\Users\\S65HOME\x85MARKER"
SPLIT_FAILURES: list[tuple[BaseException, str, str]] = [
    (_download_error("ERROR: co\tokie=SECRET"), "Download failed: [REDACTED].", "[REDACTED]"),
    (
        _download_error("ERROR: https:\t//e.example/private"),
        "Download failed: [link].",
        "[link]",
    ),
    (
        _download_error(f"ERROR: at\x00{HOME}\\v.mp4 cookie=SECRET"),
        "Download failed: at~\\v.mp4 [REDACTED].",
        "at~\\v.mp4 [REDACTED]",
    ),
    (
        _download_error(f"ERROR: at {HOME_TAB}\\v.mp4"),
        "Download failed: at ~\\v.mp4.",
        "at ~\\v.mp4",
    ),
    (
        _download_error(f"ERROR: at {HOME_LS}\\v.mp4"),
        "Download failed: at ~\\v.mp4.",
        "at ~\\v.mp4",
    ),
    (
        _download_error(f"\x1b[0;31mERROR:\x1b[0m at {HOME_NEL}\\v.mp4\nsecond line"),
        "Download failed: at ~\\v.mp4.",
        "at ~\\v.mp4",
    ),
    # Not a DownloadError: the adapter lets it through and the service's own branch reads it.
    (
        RuntimeError(f"at {HOME_LS}\\v.mp4 co\tokie=SECRET"),
        "Download failed: at ~\\v.mp4 [REDACTED].",
        "at ~\\v.mp4 [REDACTED]",
    ),
    (
        OSError(13, "Permission denied", f"{HOME}/x.mp4"),
        "Couldn't write the file. Check the output folder, then requeue.",
        "PermissionError: Permission denied",
    ),
]


def test_ac_137_12_split_text_from_yt_dlp_is_scrubbed_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    _home(monkeypatch)
    service, youtube, factory, engine = _sqlite_stack(tmp_path)
    adapter = YouTubeAdapter()
    monkeypatch.setattr(youtube, "download", adapter.download)
    service._settings.set("downloader", "cookie_mode", "none")
    service._settings.set("downloader", "path", str(tmp_path))
    stored: list[str | None] = []
    details: list[object] = []
    try:
        for n, (error, _message, _detail) in enumerate(SPLIT_FAILURES):
            _patch_ydl(monkeypatch, error=error)
            video_id = f"vid{n:04d}"
            youtube.video = VideoInfo(video_id=video_id, title="T", duration=1.0, formats=[])
            jobs = service.add_to_queue(
                f"https://youtu.be/{video_id}", QualityPreset.P1080, False, AudioFormat.Default
            )
            assert len(jobs) == 1
            with capture_logs() as logs:
                service.start_processing()
                if service._thread is not None:
                    service._thread.join(timeout=5)
            with factory() as uow:
                job = uow.downloads.get(jobs[0].id)
            assert job is not None
            assert job.status is DownloadStatus.Failed, (error, job.status)
            stored.append(job.error_message)
            failed = [entry for entry in logs if entry.get("event") == "download.failed"]
            assert len(failed) == 1, (error, failed)
            assert failed[0].get("error") == job.error_message
            details.append(failed[0].get("detail"))
    finally:
        engine.dispose()
    assert stored == [message for _error, message, _detail in SPLIT_FAILURES]
    assert details == [detail for _error, _message, detail in SPLIT_FAILURES]
    shown = " ".join(str(text) for text in [*stored, *details]).casefold()
    assert "secret" not in shown
    assert "e.example" not in shown
    for part in HOME_PARTS:
        assert part.casefold() not in shown, part


def test_ac_138_5_check_returns_the_matched_phrase(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    _patch_ydl(monkeypatch, info=_video_info_payload(), sabr_msg=SABR_CAPTURED)
    active = YouTubeAdapter().check_sabr_status()
    assert (active.mode, active.source, getattr(active, "matched_phrase", None)) == (
        SABRMode.Active,
        SABRSource.Detected,
        "missing a url",
    )

    _patch_ydl(monkeypatch, info=_video_info_payload(), sabr_msg="[download] plain progress")
    inactive = YouTubeAdapter().check_sabr_status()
    assert (inactive.mode, getattr(inactive, "matched_phrase", None)) == (SABRMode.Inactive, None)


def test_ac_138_5_captured_warning_turns_no_format_into_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_ydl(
        monkeypatch,
        sabr_msg=SABR_CAPTURED,
        error=_download_error("ERROR: [youtube] gKcOjnDJfzk: Requested format is not available"),
    )
    assert _failed(_raised(tmp_path)) == (
        DownloadFailedError,
        DownloadFailureCause.refused,
        "[youtube] gKcOjnDJfzk: Requested format is not available",
    )


# --- MEU-139: YTDLP_LIVE and the YTDLP_LINE trace ---------------------------------------------


class _Source:
    """A recording debug source: answers from `answers` (the last repeats) and counts reads."""

    def __init__(self, *answers: bool) -> None:
        self.answers = answers
        self.reads = 0

    def __call__(self) -> bool:
        value = self.answers[min(self.reads, len(self.answers) - 1)]
        self.reads += 1
        return value


def _attempt(call: object) -> None:
    """Run a public call whose result isn't the observation (the fake writes no file)."""
    assert callable(call)
    try:
        call()
    except Exception:  # noqa: BLE001 - only the options and the reads are observed
        pass


def _shown(opts: dict[str, object]) -> tuple[object, object, object]:
    logger = opts.get("logger")
    return (opts.get("quiet"), opts.get("verbose"), getattr(logger, "debug_enabled", None))


def test_ac_139_4_each_public_call_reads_the_source_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    captured = _patch_ydl(monkeypatch, info=_video_info_payload())
    flips = _Source(False, True)
    adapter = YouTubeAdapter(yt_dlp_debug=flips)
    _attempt(lambda: adapter.download(URL, _options(tmp_path)))
    _attempt(lambda: adapter.download(URL, _options(tmp_path)))
    assert [_shown(opts) for opts in captured] == [(True, False, False), (False, True, True)]
    assert flips.reads == 2

    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape", encoding="utf-8")
    calls = {
        "download": lambda a: a.download(URL, _options(tmp_path)),
        "extract_info": lambda a: a.extract_info(URL),
        "extract_video_ids": lambda a: a.extract_video_ids(URL),
        "check_sabr_status": lambda a: a.check_sabr_status(),
        "test_cookies": lambda a: a.test_cookies("file", None, None, cookie),
    }
    reads = {}
    shown = {}
    for name, call in calls.items():
        source = _Source(True)
        each = YouTubeAdapter(yt_dlp_debug=source)
        captured.clear()
        _attempt(lambda c=call, a=each: c(a))
        reads[name] = source.reads
        shown[name] = [_shown(opts) for opts in captured]
    assert reads == {name: 1 for name in calls}
    assert shown == {name: [(False, True, True)] for name in calls}


def test_ac_139_4_a_raising_or_missing_source_reads_as_off(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    captured = _patch_ydl(monkeypatch, info=_video_info_payload())

    def broken() -> bool:
        raise RuntimeError("settings unavailable")

    for adapter in (
        YouTubeAdapter(yt_dlp_debug=broken),
        YouTubeAdapter(yt_dlp_debug=None),
        YouTubeAdapter(),
    ):
        _attempt(lambda a=adapter: a.download(URL, _options(tmp_path)))
    assert [_shown(opts) for opts in captured] == [(True, False, False)] * 3


def test_ac_139_7_a_warning_inside_extract_reaches_the_console(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The Session 55 RULE-3 trace: yt-dlp's own call reaches the Console row, debug off."""
    from tests.unit.test_services import _health

    from avkit_core.services.health import HealthService
    from avkit_infra.youtube.adapter import YouTubeAdapter

    monkeypatch.setattr(HealthService, "_active", None)
    marker = "S65TRACEMARKER"
    recorded: list[tuple[str, object]] = []

    class WarningYDL:
        def __init__(self, params: dict[str, object]) -> None:
            self.params = params

        def __enter__(self) -> WarningYDL:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

        def extract_info(self, url: str, download: bool = False) -> dict[str, object]:
            logger = self.params["logger"]
            recorded.append((url, logger))
            logger.warning(f"[youtube] x: {marker} warning")  # type: ignore[attr-defined]
            return _video_info_payload()

    monkeypatch.setattr("avkit_infra.youtube.adapter.YoutubeDL", WarningYDL)
    health = _health(tmp_path / "app")
    before = health.console_snapshot(0)
    last = before[-1].seq if before else 0
    YouTubeAdapter(yt_dlp_debug=_Source(False)).extract_info(URL)
    assert [url for url, _logger in recorded] == [URL]
    rows = [(event.level, event.module, event.message) for event in health.console_snapshot(last)]
    assert rows == [("WARNING", "yt-dlp", f"yt-dlp detail=[youtube] x: {marker} warning")]
