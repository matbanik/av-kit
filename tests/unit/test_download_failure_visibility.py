"""MEU-137 download failure visibility: the cause, the card message and the cleaned line.

Module-level imports use only names that row 1 added or that existed at the baseline, so a
behaviour test fails by assertion on a row 1 stub, never by an import error (Session 62 RULE-3).
A test that expects an exception records the class it got and asserts it.
"""

from __future__ import annotations

import dataclasses
import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from structlog.testing import capture_logs
from tests.unit.test_services import DownloadYouTube, _download_stack

from avkit_core.domain import download as download_domain
from avkit_core.domain.download import SABRStatus, clean_line, download_failure_message
from avkit_core.domain.enums import (
    AudioFormat,
    DownloadFailureCause,
    DownloadStatus,
    QualityPreset,
    SABRMode,
    SABRSource,
)
from avkit_core.domain.errors import (
    DOMAIN_ERROR_TYPES,
    AgeRestrictedError,
    CookieTestError,
    DomainError,
    DownloadCancelledError,
    DownloadFailedError,
    ValidationError,
)
from avkit_core.services import health as health_module
from avkit_core.services.download import DownloadService, scrub_line
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.settings import SettingsService
from avkit_infra.youtube import adapter as adapter_module

pytestmark = pytest.mark.unit

Cause = DownloadFailureCause

MESSAGES = {
    Cause.refused: (
        "YouTube refused the download (page reload, SABR-only or bot check). Try again later."
    ),
    Cause.no_format: "No format at the chosen quality. Pick another quality and requeue.",
    Cause.cookies: (
        "Couldn't read the browser sign-in data. Check Settings → Downloader, then requeue."
    ),
    Cause.write_failed: "Couldn't write the file. Check the output folder, then requeue.",
}

#: The FAILURE_CAUSE needles, in the plan's order (D-636).
CAUSE_NEEDLES = (
    (
        Cause.refused,
        ("the page needs to be reloaded", "confirm you're not a bot", "confirm you’re not a bot"),
    ),
    (
        Cause.no_format,
        (
            "requested format is not available",
            "no video formats found",
            "only images are available",
        ),
    ),
    (
        Cause.cookies,
        (
            "could not copy chrome cookie database",
            "failed to decrypt with dpapi",
            "cookies database",
        ),
    ),
    (Cause.write_failed, ("unable to open for writing", "unable to write data")),
)
CAPTURED_PREFIX = "[youtube] gKcOjnDJfzk: "

#: A synthetic home folder; no test reads the real one. Split forms put a character inside
#: the user name that `clean_line` drops (an ANSI code) or turns into a space (U+0085).
HOME_USER = "S65HOMEMARKER"
HOME = f"C:\\Users\\{HOME_USER}"
HOME_X85 = "C:\\Users\\S65HOME\x85MARKER"
HOME_ANSI = "C:\\Users\\S65HOME\x1b[0mMARKER"


def _raised(call: Callable[[], object]) -> type[BaseException] | None:
    """The class `call` raised, or None, so a wrong class fails by assertion."""
    try:
        call()
    except Exception as exc:  # noqa: BLE001 - the class is the observation
        return type(exc)
    return None


def _home(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the home folder to the marker path, as AC-119.10 does (test_services.py:3313)."""
    assert hasattr(health_module, "home_folder")
    assert hasattr(health_module, "HOME_IGNORES_CASE")
    monkeypatch.setattr(health_module, "home_folder", lambda: HOME)
    monkeypatch.setattr(health_module, "HOME_IGNORES_CASE", True)


def _mixed_case(text: str) -> str:
    return "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))


def test_ac_137_1_failure_types_have_their_planned_shape() -> None:
    assert [(m.name, m.value) for m in DownloadFailureCause] == [
        ("refused", "refused"),
        ("no_format", "no_format"),
        ("cookies", "cookies"),
        ("write_failed", "write_failed"),
        ("other", "other"),
    ]

    assert issubclass(DownloadFailedError, DomainError)
    err = DownloadFailedError(DownloadFailureCause.other, "raw line")
    assert err.cause is DownloadFailureCause.other
    assert err.detail == "raw line"
    assert str(err) == "download failed: other"
    assert DOMAIN_ERROR_TYPES[-1] is DownloadFailedError

    message_params = list(inspect.signature(download_failure_message).parameters.values())
    assert [(p.name, p.kind, p.default) for p in message_params] == [
        ("cause", inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
        ("reason", inspect.Parameter.POSITIONAL_OR_KEYWORD, None),
    ]

    clean_params = list(inspect.signature(clean_line).parameters.values())
    assert [(p.name, p.default) for p in clean_params] == [("text", inspect.Parameter.empty)]
    assert clean_params[0].annotation in (str, "str")

    assert hasattr(adapter_module, "classify_download_error")
    classify_params = list(inspect.signature(adapter_module.classify_download_error).parameters)
    assert classify_params == ["text", "sabr_matched"]

    fields = dataclasses.fields(SABRStatus)
    assert fields[-1].name == "matched_phrase"
    assert fields[-1].default is None
    assert download_domain.SABR_STATUS_FIELDS[-1] == "matched_phrase"


def test_ac_137_2_each_cause_has_its_exact_message() -> None:
    for cause, text in MESSAGES.items():
        assert download_failure_message(cause) == text
        assert download_failure_message(cause, "ignored reason") == text
    assert download_failure_message(Cause.other, "x") == "Download failed: x."
    assert download_failure_message(Cause.other, None) == "Download failed."
    assert download_failure_message(Cause.other, "") == "Download failed."
    assert download_failure_message(Cause.other) == "Download failed."
    for bogus in ("refused", "bogus", None):
        assert _raised(lambda bogus=bogus: download_failure_message(bogus)) is ValidationError  # type: ignore[arg-type]


def test_ac_137_3_messages_hold_no_needle_link_or_path() -> None:
    for cause in DownloadFailureCause:
        for reason in (None, "x"):
            message = download_failure_message(cause, reason)
            assert message != "", (cause, reason)
            assert message.endswith("."), (cause, reason, message)
            folded = message.casefold()
            assert [n for n in health_module.REDACT_NEEDLES if n in folded] == [], message
            assert "://" not in message
            assert "/" not in message and "\\" not in message


def test_ac_137_4_clean_line_keeps_one_readable_line() -> None:
    cases = [
        ("\x1b[0;31mERROR:\x1b[0m bad", "ERROR: bad"),
        ("\ud800", ""),
        ("\x00", ""),
        ("\x07", ""),
        ("\x7f", ""),
        ("\x9b", ""),
        ("a\r\n\tb", "a b"),
        ("a\u2028b", "a b"),
        ("co\x00okie", "cookie"),
        ("a\u200bb", "ab"),
        ("\u202e", ""),
        ("C:\\Us\x1b[0mers", "C:\\Users"),
        ("", ""),
        ("\x00\x07\x1b[0m\u200b\u202e\x7f", ""),
        ("Łódź ✓", "Łódź ✓"),
    ]
    assert [(text, clean_line(text)) for text, _want in cases] == cases


def test_ac_137_4_scrub_line_joins_split_needles_links_and_home(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _home(monkeypatch)
    cases = [
        ("co\x85okie=SECRET", "[REDACTED]"),
        ("co\u2028okie=SECRET", "[REDACTED]"),
        ("https:\u2028//e.example/private", "[link]"),
        (f"{HOME_X85}\\v.mp4", "~\\v.mp4"),
        ("a\tb cookie=X", "ab [REDACTED]"),
        ("a\u2028b", "a b"),
        ("co okie=x", "co okie=x"),
        ("", ""),
        ("\ud800", ""),
        (f"at\t{HOME}\\v.mp4 cookie=SECRET", "at~\\v.mp4 [REDACTED]"),
        (f"at\t{HOME_X85}\\v.mp4 cookie=SECRET", "at~\\v.mp4 [REDACTED]"),
        (f"at\x00{HOME}\\v.mp4 cookie=SECRET", "at~\\v.mp4 [REDACTED]"),
        (f"at\t{HOME}\\v.mp4", "at ~\\v.mp4"),
        (f"x{HOME}\\v.mp4", f"x{HOME}\\v.mp4"),
        (f"{HOME}2\\v.mp4", f"{HOME}2\\v.mp4"),
    ]
    assert [(text, scrub_line(text)) for text, _want in cases] == cases


def test_ac_137_5_each_needle_names_its_cause() -> None:
    classify = adapter_module.classify_download_error
    for cause, needles in CAUSE_NEEDLES:
        for needle in needles:
            for shown in (needle.upper(), _mixed_case(needle)):
                line = f"{CAPTURED_PREFIX}{shown}"
                assert classify(f"ERROR: {line}", False) == (cause, line), shown


def test_ac_137_5_prefix_lines_and_the_sabr_override() -> None:
    classify = adapter_module.classify_download_error
    coloured = "\x1b[0;31mERROR:\x1b[0m [youtube] x: The page needs to be reloaded."
    assert classify(coloured, False) == (
        Cause.refused,
        "[youtube] x: The page needs to be reloaded.",
    )
    multi = "\n \x1b[0m\nERROR: [youtube] x: first line\nsecond line"
    assert classify(multi, False) == (Cause.other, "[youtube] x: first line")
    no_format = "ERROR: [youtube] x: Requested format is not available"
    assert classify(no_format, False) == (
        Cause.no_format,
        "[youtube] x: Requested format is not available",
    )
    assert classify(no_format, True) == (
        Cause.refused,
        "[youtube] x: Requested format is not available",
    )
    assert classify("ERROR: [youtube] x: something new", False) == (
        Cause.other,
        "[youtube] x: something new",
    )
    assert classify("", False) == (Cause.other, "")


# --- AC-137.7 and AC-137.8: FAILURE_LOG ------------------------------------------------------


def _sqlite_stack(tmp_path: Path) -> tuple[DownloadService, DownloadYouTube, Any, Any]:
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    youtube = DownloadYouTube()
    service = DownloadService(
        factory,
        youtube=youtube,
        coordinator=ExtractCoordinator(youtube),
        settings=SettingsService(factory),
        sleep=lambda _seconds: None,
    )
    youtube.service = service
    return service, youtube, factory, engine


def _stored(
    service: DownloadService, youtube: DownloadYouTube, factory: Any, error: Exception, n: int
) -> str | None:
    from avkit_core.domain.download import VideoInfo

    video_id = f"vid{n:04d}"
    youtube.video = VideoInfo(video_id=video_id, title="T", duration=1.0, formats=[])
    youtube.download_error = error
    jobs = service.add_to_queue(
        f"https://youtu.be/{video_id}", QualityPreset.P1080, False, AudioFormat.Default
    )
    assert len(jobs) == 1
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=5)
    with factory() as uow:
        job = uow.downloads.get(jobs[0].id)
    assert job is not None
    assert job.status is DownloadStatus.Failed, (error, job.status)
    return job.error_message


def test_ac_137_7_each_failure_stores_its_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _home(monkeypatch)
    service, youtube, factory, engine = _sqlite_stack(tmp_path)
    cases: list[tuple[Exception, str]] = [
        (DownloadFailedError(cause, "ERROR: x"), text) for cause, text in MESSAGES.items()
    ]
    cases += [
        (DownloadFailedError(Cause.other, "boom"), "Download failed: boom."),
        (CookieTestError("cookie file is missing or unreadable"), MESSAGES[Cause.cookies]),
        (
            DomainError("download completed without an output file"),
            "Download failed: download completed without an output file.",
        ),
        (RuntimeError(""), "Download failed: RuntimeError."),
        (DownloadFailedError(Cause.other, "bad cookie=SECRET"), "Download failed: bad [REDACTED]."),
        (DownloadFailedError(Cause.other, f"at {HOME}\\v.mp4"), "Download failed: at ~\\v.mp4."),
        (
            DownloadFailedError(Cause.other, "see https://e.example/private now"),
            "Download failed: see [link] now.",
        ),
        (DownloadFailedError(Cause.other, "a" * 500), "Download failed: " + "a" * 200 + "."),
    ]
    try:
        stored = [
            _stored(service, youtube, factory, error, n) for n, (error, _want) in enumerate(cases)
        ]
    finally:
        engine.dispose()
    assert stored == [want for _error, want in cases]


def test_ac_137_7_split_forms_are_scrubbed_before_storage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _home(monkeypatch)
    service, youtube, factory, engine = _sqlite_stack(tmp_path)
    cases = [
        ("co\x00okie=SECRET", "Download failed: [REDACTED]."),
        ("https\x00://e.example/private", "Download failed: [link]."),
        (f"at {HOME_ANSI}\\v.mp4", "Download failed: at ~\\v.mp4."),
        ("co\x85okie=SECRET", "Download failed: [REDACTED]."),
        ("co\u2028okie=SECRET", "Download failed: [REDACTED]."),
        ("https:\u2028//e.example/private", "Download failed: [link]."),
        (f"at {HOME_X85}\\v.mp4", "Download failed: at ~\\v.mp4."),
        (f"at\t{HOME_X85}\\v.mp4 cookie=SECRET", "Download failed: at~\\v.mp4 [REDACTED]."),
    ]
    try:
        stored = [
            _stored(service, youtube, factory, DownloadFailedError(Cause.other, raw), n)
            for n, (raw, _want) in enumerate(cases)
        ]
    finally:
        engine.dispose()
    assert stored == [want for _raw, want in cases]
    joined = " ".join(text or "" for text in stored)
    assert "SECRET" not in joined
    assert "e.example" not in joined
    assert HOME_USER.casefold() not in joined.casefold()


def _logged_run(
    error: Exception | None,
) -> tuple[str, list[dict[str, Any]], list[tuple[Any, ...]], Any]:
    """Run one job under `capture_logs`, recording when the port is called and each commit."""
    service, _settings, youtube, uow = _download_stack()
    jobs = service.add_to_queue(
        "https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default
    )
    job_id = jobs[0].id
    trace: list[tuple[Any, ...]] = []
    with capture_logs() as logs:
        real_download = youtube.download
        real_commit = uow.commit

        def recording_download(url: str, options: object) -> object:
            trace.append(("port", len(logs)))
            return real_download(url, options)

        def recording_commit() -> None:
            real_commit()
            trace.append(("commit", uow.downloads.get(job_id).status, len(logs)))

        youtube.download = recording_download  # type: ignore[method-assign]
        uow.commit = recording_commit  # type: ignore[method-assign]
        youtube.download_error = error
        service.start_processing()
        if service._thread is not None:
            service._thread.join(timeout=5)
    return job_id, list(logs), trace, uow


def _download_events(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    names = ("download.started", "download.done", "download.failed")
    return [entry for entry in logs if entry.get("event") in names]


def test_ac_137_8_success_logs_started_then_done(monkeypatch: pytest.MonkeyPatch) -> None:
    job_id, logs, trace, uow = _logged_run(None)
    events = _download_events(logs)
    assert [entry["event"] for entry in events] == ["download.started", "download.done"]
    for entry in events:
        assert entry.get("job_id") == job_id
        assert entry.get("video_id") == "vid1"
        assert entry.get("log_level") == "info"
    started_at = logs.index(events[0])
    done_at = logs.index(events[1])
    port_calls = [item[1] for item in trace if item[0] == "port"]
    assert len(port_calls) == 1
    assert started_at < port_calls[0], "download.started must be logged before the port call"
    done_commits = [
        item[2] for item in trace if item[0] == "commit" and item[1] is DownloadStatus.Done
    ]
    assert done_commits, "the row was never committed Done"
    assert done_at >= done_commits[0], "download.done must be logged after the Done commit"
    assert uow.downloads.get(job_id).status is DownloadStatus.Done


@pytest.mark.parametrize(
    ("error", "stored", "detail"),
    [
        (
            DownloadFailedError(Cause.refused, "[youtube] x: The page needs to be reloaded."),
            MESSAGES[Cause.refused],
            "[youtube] x: The page needs to be reloaded.",
        ),
        (DownloadFailedError(Cause.other, "boom"), "Download failed: boom.", "boom"),
        (
            CookieTestError("cookie file is missing or unreadable"),
            MESSAGES[Cause.cookies],
            "[REDACTED]",
        ),
        (
            DomainError("download completed without an output file"),
            "Download failed: download completed without an output file.",
            "download completed without an output file",
        ),
        (
            RuntimeError("disk on fire\nsecond line"),
            "Download failed: disk on fire.",
            "disk on fire",
        ),
        (
            AgeRestrictedError("video is age-restricted"),
            "video is age-restricted",
            "video is age-restricted",
        ),
    ],
    ids=["refused", "other", "cookies", "domain", "exception", "age"],
)
def test_ac_137_8_each_failure_logs_one_failed_line(
    error: Exception, stored: str, detail: str
) -> None:
    job_id, logs, _trace, uow = _logged_run(error)
    events = _download_events(logs)
    assert [entry["event"] for entry in events] == ["download.started", "download.failed"]
    failed = events[1]
    assert failed.get("log_level") == "error"
    assert failed.get("job_id") == job_id
    assert failed.get("video_id") == "vid1"
    row = uow.downloads.get(job_id)
    assert row.error_message == stored
    assert failed.get("error") == stored
    assert failed.get("detail") == detail


def test_ac_137_8_cancelled_logs_nothing_new() -> None:
    job_id, logs, _trace, uow = _logged_run(DownloadCancelledError("cancelled"))
    events = _download_events(logs)
    assert [entry["event"] for entry in events] == ["download.started"]
    assert uow.downloads.get(job_id).status is DownloadStatus.Cancelled


# --- MEU-138: the SABR phrases, the passive scan and the stored phrase ------------------------

#: yt-dlp 2026.10.26's warning, as captured on 2026-11-10 (build plan 02 §SABR check result).
SABR_CAPTURED = (
    "WARNING: [youtube] x: Some android client https formats have been skipped as they are "
    "missing a URL. YouTube may have enabled the SABR-only streaming experiment for the "
    "current session. See https://github.com/yt-dlp/yt-dlp/issues/12482 for more details"
)
SABR_PHRASES_PLANNED = ("forcing sabr", "missing a url", "require a gvs po token", "sabr")


def test_ac_138_1_sabr_names_have_their_planned_shape() -> None:
    assert getattr(adapter_module, "SABR_PHRASES", None) == SABR_PHRASES_PLANNED
    assert hasattr(adapter_module, "SABR_LOG_NEEDLES") is False

    params = list(inspect.signature(adapter_module.sabr_phrase).parameters.values())
    assert [(p.name, p.kind, p.default) for p in params] == [
        ("text", inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty)
    ]
    assert params[0].annotation in (str, "str")

    assert download_domain.SABR_STATUS_FIELDS[-1] == "matched_phrase"
    assert [f.name for f in dataclasses.fields(SABRStatus)][-1] == "matched_phrase"
    static = inspect.getattr_static(adapter_module._YtDlpLogger, "sabr_detected", None)
    assert isinstance(static, property)


def test_ac_138_2_each_phrase_is_matched_as_a_whole_word() -> None:
    phrase = adapter_module.sabr_phrase
    found = {
        "captured": phrase(SABR_CAPTURED),
        "forcing upper": phrase("YouTube is FORCING SABR streaming for this client"),
        "forcing mixed": phrase("youtube is Forcing Sabr streaming"),
        "gvs": phrase("Some formats require a GVS PO Token which was not provided"),
        "android": phrase("android client sabr formats require a token"),
        "ios": phrase("ios client SABR formats require a token"),
        "sabr-only": phrase("the SABR-only experiment"),
    }
    assert found == {
        "captured": "missing a url",
        "forcing upper": "forcing sabr",
        "forcing mixed": "forcing sabr",
        "gvs": "require a gvs po token",
        "android": "sabr",
        "ios": "sabr",
        "sabr-only": "sabr",
    }
    near = ["Sabrina", "the sabre", "sabrs", "PO Token required for GVS", "plain progress", ""]
    assert [phrase(text) for text in near] == [None] * len(near)


def test_ac_138_2_a_sabr_phrase_alone_classifies_as_refused() -> None:
    line = "ERROR: [youtube] x: YouTube is forcing SABR streaming for this client"
    assert adapter_module.classify_download_error(line, False) == (
        Cause.refused,
        "[youtube] x: YouTube is forcing SABR streaming for this client",
    )


def test_ac_138_3_the_scan_keeps_the_first_phrase() -> None:
    logger = adapter_module._YtDlpLogger(False)
    logger.info("[download] Destination: clip.mp4")
    logger.warning(SABR_CAPTURED)
    logger.warning("YouTube is forcing SABR streaming for this client")
    assert (logger.matched_phrase, logger.sabr_detected) == ("missing a url", True)

    fresh = adapter_module._YtDlpLogger(False)
    assert (fresh.matched_phrase, fresh.sabr_detected) == (None, False)

    scanned = {}
    for method in ("debug", "info", "warning", "error"):
        each = adapter_module._YtDlpLogger(False)
        getattr(each, method)("YouTube is forcing SABR streaming")
        scanned[method] = (each.matched_phrase, each.sabr_detected)
    assert scanned == {method: ("forcing sabr", True) for method in scanned}

    def assign() -> None:
        fresh.sabr_detected = True  # type: ignore[misc]

    assert _raised(assign) is AttributeError


def test_ac_138_4_a_phrase_needs_active_detected() -> None:
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    built = SABRStatus(SABRMode.Active, SABRSource.Detected, now, "sabr")
    assert built.matched_phrase == "sabr"
    assert SABRStatus(SABRMode.Inactive, SABRSource.Detected, now).matched_phrase is None

    invalid: list[tuple[SABRMode, SABRSource | None, Any]] = [
        (SABRMode.Active, SABRSource.Forced, "sabr"),
        (SABRMode.Inactive, SABRSource.Detected, "sabr"),
        (SABRMode.Inactive, None, "sabr"),
        (SABRMode.Active, SABRSource.Detected, ""),
        (SABRMode.Active, SABRSource.Detected, 1),
    ]
    got = [
        _raised(lambda m=mode, s=source, p=value: SABRStatus(m, s, now, p))
        for mode, source, value in invalid
    ]
    assert got == [ValidationError] * len(invalid)

    def missing_field() -> None:
        SABRStatus(SABRMode.Inactive, None)  # type: ignore[call-arg]

    assert _raised(missing_field) is TypeError


# --- MEU-139: YTDLP_LINE and YTDLP_LIVE ------------------------------------------------------


def _ytdlp_lines(logs: list[dict[str, Any]]) -> list[tuple[str, object, object, bool]]:
    """The captured `yt-dlp` events as (level, module, detail, has a `message` key)."""
    return [
        (entry["log_level"], entry.get("module"), entry.get("detail"), "message" in entry)
        for entry in logs
        if entry.get("event") == "yt-dlp"
    ]


def test_ac_139_1_debug_source_and_logger_have_their_planned_shape() -> None:
    source = inspect.signature(adapter_module.YouTubeAdapter).parameters["yt_dlp_debug"]
    assert (source.kind, source.annotation, source.default) == (
        inspect.Parameter.KEYWORD_ONLY,
        "Callable[[], bool] | None",
        None,
    )
    logger_params = inspect.signature(adapter_module._YtDlpLogger).parameters
    assert list(logger_params) == ["debug_enabled"]
    assert (
        adapter_module._YtDlpLogger(True).debug_enabled,
        adapter_module._YtDlpLogger(False).debug_enabled,
    ) == (True, False)
    base_params = inspect.signature(adapter_module.YouTubeAdapter._base_opts).parameters
    assert list(base_params) == ["self", "logger"]


def test_ac_139_2_warnings_and_error_lines_log_with_debug_off() -> None:
    logger = adapter_module._YtDlpLogger(False)
    with capture_logs() as logs:
        logger.warning("x")
        logger.error("ERROR: y")
    assert _ytdlp_lines(logs) == [
        ("warning", "yt-dlp", "x", False),
        ("error", "yt-dlp", "ERROR: y", False),
    ]


def test_ac_139_3_debug_lines_log_only_with_debug_on() -> None:
    traceback = "Traceback (most recent call last):"
    off = adapter_module._YtDlpLogger(False)
    with capture_logs() as off_logs:
        off.debug("a")
        off.info("b")
        off.error(traceback)
    assert _ytdlp_lines(off_logs) == []

    on = adapter_module._YtDlpLogger(True)
    with capture_logs() as on_logs:
        on.debug("a")
        on.info("b")
        on.error(traceback)
    assert _ytdlp_lines(on_logs) == [
        ("debug", "yt-dlp", "a", False),
        ("debug", "yt-dlp", "b", False),
        ("debug", "yt-dlp", traceback, False),
    ]

    with capture_logs() as empty_logs:
        on.warning("")
        on.warning("\x1b[0m")
        on.debug("\x00")
    assert _ytdlp_lines(empty_logs) == []


def test_ac_139_9_surrogate_control_and_long_lines_are_cleaned(tmp_path: Path) -> None:
    from tests.unit.test_services import _health

    raw = "bad\ud800 x\x00y \x1b[31mred " + "z" * 400
    logger = adapter_module._YtDlpLogger(False)
    with capture_logs() as logs:
        logger.warning(raw)
        logger.warning("")
    lines = _ytdlp_lines(logs)
    assert len(lines) == 1, lines
    detail = lines[0][2]
    assert isinstance(detail, str)
    assert [c for c in ("\ud800", "\x00", "\x1b") if c in detail] == []
    assert detail.startswith("bad xy red z")

    health = _health(tmp_path / "app")
    last = health.console_snapshot(0)[-1].seq if health.console_snapshot(0) else 0
    adapter_module._YtDlpLogger(False).warning(raw)
    shown = [event.message for event in health.console_snapshot(last)]
    assert len(shown) == 1, shown
    prefix = "yt-dlp detail="
    assert shown[0].startswith(prefix), shown[0]
    assert len(shown[0]) - len(prefix) <= health_module.FIELD_LIMIT
    assert [c for c in ("\ud800", "\x00", "\x1b") if c in shown[0]] == []
