"""MEU-140 ADD_OPTS and ADD_CACHE_KEY: the add-time extract runs with the download's options.

The service tests use a SQLite stack with a recording fake port; the adapter tests patch
`YoutubeDL` with the scripted fake from the MEU-140 integration tests. Nothing reaches the
network. A wrong exception is caught and asserted on (red-check).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from tests.integration.test_youtube_adapter import COOKIE_EXTRACTOR_ARGS, _download_error
from tests.integration.test_youtube_client_fallback import BOT, RELOAD, _script
from tests.unit.test_services import DownloadYouTube

from avkit_core.domain.download import DownloadOptions, PlaylistInfo, VideoInfo
from avkit_core.domain.enums import AudioFormat, DownloadStatus, QualityPreset
from avkit_core.domain.errors import CookieTestError, ExtractError
from avkit_core.services.download import DownloadService
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.settings import SettingsService

pytestmark = pytest.mark.unit

URL = "https://youtu.be/vid12345678"
COOKIE_KEYS = ("cookiesfrombrowser", "cookiefile")


def _opts(tmp_path: Path, **overrides: object) -> DownloadOptions:
    payload: dict[str, object] = {
        "quality": QualityPreset.P720,
        "audio_only": False,
        "audio_format": AudioFormat.Default,
        "output_dir": tmp_path / "out",
        "mode": "none",
        "browser": None,
        "profile": None,
        "cookie_file": None,
    }
    payload.update(overrides)
    return DownloadOptions(**payload)  # type: ignore[arg-type]


def _outcome(call: Callable[[], object]) -> tuple[object, BaseException | None]:
    """The call's result or the exception it raised, so a wrong class fails by assertion."""
    try:
        return call(), None
    except Exception as exc:  # noqa: BLE001 - the exception is the observation
        return None, exc


# --- AC-140.9: ADD_OPTS through the service ----------------------------------------------------


class OptionsYouTube(DownloadYouTube):
    """Records the options each add-time extract received."""

    def __init__(self) -> None:
        super().__init__()
        self.extract_options: list[object] = []

    def extract_info(
        self, url: str, flat: bool = False, options: object = None
    ) -> VideoInfo | PlaylistInfo:
        self.extract_options.append(options)
        return super().extract_info(url, flat)


@contextmanager
def _service(tmp_path: Path) -> Iterator[tuple[DownloadService, OptionsYouTube, Any, Any]]:
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

    youtube = OptionsYouTube()
    settings = SettingsService(factory)
    service = DownloadService(
        factory,
        youtube=youtube,
        coordinator=ExtractCoordinator(youtube),
        settings=settings,
        sleep=lambda _seconds: None,
    )
    youtube.service = service
    try:
        yield service, youtube, settings, factory
    finally:
        engine.dispose()


def _run_queue(service: DownloadService) -> None:
    service.start_processing()
    thread = service._thread
    if thread is not None:
        thread.join(timeout=5)


def test_ac_140_9_add_passes_the_browser_options_the_download_uses(tmp_path: Path) -> None:
    with _service(tmp_path) as (service, youtube, settings, factory):
        settings.set("downloader", "path", str(tmp_path / "out"))
        settings.set("downloader", "cookie_mode", "browser")
        settings.set("downloader", "cookie_browser", "firefox")
        settings.set("downloader", "cookie_browser_profile", "p1")
        jobs = service.add_to_queue(URL, QualityPreset.P720, False, AudioFormat.Default)
        assert len(jobs) == 1
        _run_queue(service)
        with factory() as uow:
            job = uow.downloads.get(jobs[0].id)
    expected = _opts(tmp_path, mode="browser", browser="firefox", profile="p1")
    assert youtube.extract_options == [expected]
    assert youtube.last_options == expected
    assert job is not None and job.status is DownloadStatus.Done


def test_ac_140_9_add_passes_the_file_options_the_download_uses(tmp_path: Path) -> None:
    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    with _service(tmp_path) as (service, youtube, settings, _factory):
        settings.set("downloader", "path", str(tmp_path / "out"))
        settings.set("downloader", "cookie_mode", "file")
        settings.set("downloader", "cookie_file_path", str(cookie))
        jobs = service.add_to_queue(URL, QualityPreset.P360, True, AudioFormat.HighM4a)
        assert len(jobs) == 1
        _run_queue(service)
    expected = _opts(
        tmp_path,
        quality=QualityPreset.P360,
        audio_only=True,
        audio_format=AudioFormat.HighM4a,
        mode="file",
        browser="chrome",
        cookie_file=cookie,
    )
    assert youtube.extract_options == [expected]
    assert youtube.last_options == expected


def test_ac_140_9_add_reads_the_cookie_mode_fresh(tmp_path: Path) -> None:
    # Cached settings are read fresh (Session 60): a mode change reaches the next add.
    with _service(tmp_path) as (service, youtube, settings, _factory):
        settings.set("downloader", "path", str(tmp_path / "out"))
        service.add_to_queue(URL, QualityPreset.P720, False, AudioFormat.Default)
        settings.set("downloader", "cookie_mode", "browser")
        settings.set("downloader", "cookie_browser", "edge")
        service.add_to_queue(
            "https://youtu.be/vid22222222", QualityPreset.P720, False, AudioFormat.Default
        )
    assert youtube.extract_options == [
        _opts(tmp_path, browser="chrome"),
        _opts(tmp_path, mode="browser", browser="edge"),
    ]


# --- AC-140.9: ADD_OPTS in the adapter -------------------------------------------------------


def _extract(options: DownloadOptions | None, flat: bool = False) -> tuple[object, Any]:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    adapter = YouTubeAdapter()
    if options is None:
        return _outcome(lambda: adapter.extract_info(URL, flat=flat))
    return _outcome(lambda: adapter.extract_info(URL, flat=flat, options=options))


def test_ac_140_9_extract_with_options_applies_cookies_and_retries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = _script(monkeypatch, [_download_error(RELOAD), None])
    result, raised = _extract(_opts(tmp_path, mode="browser", browser="firefox", profile="p1"))
    assert raised is None, repr(raised)
    assert isinstance(result, VideoInfo)
    assert result.video_id == "vid12345678"
    assert len(seen.runs) == 2
    first, second = seen.opts(0), seen.opts(1)
    assert first.get("cookiesfrombrowser") == ("firefox", "p1")
    assert "extractor_args" not in first, first.get("extractor_args")
    assert second.get("cookiesfrombrowser") == ("firefox", "p1")
    assert second.get("extractor_args") == COOKIE_EXTRACTOR_ARGS
    assert [run["download"] for run in seen.runs] == [False, False]


def test_ac_140_9_extract_with_file_options_runs_once_when_it_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    seen = _script(monkeypatch, [None])
    result, raised = _extract(_opts(tmp_path, mode="file", cookie_file=cookie))
    assert raised is None, repr(raised)
    assert isinstance(result, VideoInfo)
    assert len(seen.runs) == 1
    assert seen.opts(0).get("cookiefile") == str(cookie)
    assert "extractor_args" not in seen.opts(0)


def test_ac_140_9_extract_with_options_fails_after_two_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = _script(monkeypatch, [_download_error(RELOAD), _download_error(RELOAD), None])
    result, raised = _extract(_opts(tmp_path))
    assert result is None
    assert isinstance(raised, ExtractError), repr(raised)
    assert len(seen.runs) == 2


def test_ac_140_9_extract_with_options_does_not_retry_a_bot_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = _script(monkeypatch, [_download_error(BOT), None])
    result, raised = _extract(_opts(tmp_path, mode="browser", browser="firefox"))
    assert result is None
    assert isinstance(raised, ExtractError), repr(raised)
    assert len(seen.runs) == 1
    assert seen.opts(0).get("cookiesfrombrowser") == ("firefox", None)


def test_ac_140_9_extract_with_a_missing_cookie_file_runs_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = _script(monkeypatch, [None])
    missing = tmp_path / "absent" / "cookies.txt"
    result, raised = _extract(_opts(tmp_path, mode="file", cookie_file=missing))
    assert result is None
    assert isinstance(raised, CookieTestError), repr(raised)
    assert seen.inits == 0
    assert seen.runs == []


@pytest.mark.parametrize("flat", [False, True], ids=["full", "flat"])
def test_ac_140_9_no_options_no_cookies_one_run(
    monkeypatch: pytest.MonkeyPatch, flat: bool
) -> None:
    # The transcript path: unchanged, so this holds before and after the retry exists.
    seen = _script(monkeypatch, [_download_error(RELOAD), None])
    result, raised = _extract(None, flat=flat)
    assert result is None
    assert isinstance(raised, ExtractError), repr(raised)
    assert len(seen.runs) == 1
    assert [key for key in (*COOKIE_KEYS, "extractor_args") if key in seen.opts(0)] == []


# --- AC-140.10: ADD_CACHE_KEY ----------------------------------------------------------------


class KeywordPort(DownloadYouTube):
    """Records each extract's flat flag and the keywords beyond it."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[str, bool, dict[str, object]]] = []

    def extract_info(  # type: ignore[override]
        self, url: str, flat: bool = False, **kwargs: object
    ) -> VideoInfo | PlaylistInfo:
        self.calls.append((url, flat, dict(kwargs)))
        return super().extract_info(url, flat)


class NoOptionsPort(DownloadYouTube):
    """A transcript-path fake whose extract_info takes no options (test_transcript_flat_extract)."""

    def __init__(self) -> None:
        super().__init__()
        self.flat_args: list[bool] = []

    def extract_info(self, url: str, flat: bool = False) -> VideoInfo | PlaylistInfo:  # type: ignore[override]
        self.flat_args.append(flat)
        return super().extract_info(url, flat)


def test_ac_140_10_a_cookie_mode_change_misses_the_cache(tmp_path: Path) -> None:
    port = KeywordPort()
    coordinator = ExtractCoordinator(port)
    none = _opts(tmp_path)
    browser = _opts(tmp_path, mode="browser", browser="firefox", profile="p1")
    coordinator.extract_info(URL, options=none)
    coordinator.extract_info(URL, options=browser)
    coordinator.extract_info(URL, options=browser)
    assert [kwargs for _url, _flat, kwargs in port.calls] == [
        {"options": none},
        {"options": browser},
    ]


@pytest.mark.parametrize(
    "change",
    [
        {"browser": "edge"},
        {"profile": "p2"},
        {"mode": "file", "cookie_file": Path("a.txt")},
    ],
    ids=["browser", "profile", "cookie_file"],
)
def test_ac_140_10_each_cookie_field_is_in_the_key(
    tmp_path: Path, change: dict[str, object]
) -> None:
    port = KeywordPort()
    coordinator = ExtractCoordinator(port)
    base = _opts(tmp_path, mode="browser", browser="firefox", profile="p1")
    if change.get("mode") == "file":
        base = _opts(tmp_path, mode="file", cookie_file=Path("b.txt"))
    changed = _opts(
        tmp_path,
        **{
            "mode": base.mode,
            "browser": base.browser,
            "profile": base.profile,
            "cookie_file": base.cookie_file,
            **change,
        },
    )
    coordinator.extract_info(URL, options=base)
    coordinator.extract_info(URL, options=changed)
    assert len(port.calls) == 2
    assert sorted(coordinator._info_cache, key=repr) == sorted(
        [
            (URL, False, base.mode, base.browser, base.profile, base.cookie_file),
            (URL, False, changed.mode, changed.browser, changed.profile, changed.cookie_file),
        ],
        key=repr,
    )


def test_ac_140_10_the_same_options_hit_the_cache(tmp_path: Path) -> None:
    port = KeywordPort()
    coordinator = ExtractCoordinator(port)
    options = _opts(tmp_path, mode="browser", browser="firefox", profile="p1")
    first = coordinator.extract_info(URL, options=options)
    second = coordinator.extract_info(
        f"  {URL} ",
        options=_opts(tmp_path, **{"mode": "browser", "browser": "firefox", "profile": "p1"}),
    )
    assert first is second
    assert len(port.calls) == 1
    assert list(coordinator._info_cache) == [(URL, False, "browser", "firefox", "p1", None)]


def test_ac_140_10_the_no_options_key_is_unchanged(tmp_path: Path) -> None:
    port = KeywordPort()
    coordinator = ExtractCoordinator(port)
    coordinator.extract_info(URL)
    coordinator.extract_info(URL, flat=True)
    coordinator.extract_info(URL)
    assert port.calls == [(URL, False, {}), (URL, True, {})]
    assert list(coordinator._info_cache) == [(URL, False), (URL, True)]


def test_ac_140_10_a_port_without_options_still_serves_the_transcript_path() -> None:
    port = NoOptionsPort()
    coordinator = ExtractCoordinator(port)
    result, raised = _outcome(lambda: coordinator.extract_info(URL, flat=True))
    assert raised is None, repr(raised)
    assert isinstance(result, VideoInfo)
    assert port.flat_args == [True]
