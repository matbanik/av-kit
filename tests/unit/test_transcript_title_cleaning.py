"""MEU-147 transcript title cleaning: the shared cleaner and the two fallbacks.

AC-147.1 to AC-147.5 (docs/execution/plans/2026-11-15-text-scrub-residuals). Each test asserts
``clean_text`` exists first (Session 52 RULE-4), so a missing name fails as an assertion.
Surrogates and control characters are written as escapes, never raw.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.unit.test_services import DownloadYouTube, _transcript_stack

from avkit_core.domain import download as download_domain
from avkit_core.domain.download import PlaylistInfo, VideoInfo
from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
from avkit_core.domain.errors import ValidationError
from avkit_core.domain.transcript import TranscriptResult

URL = "https://youtube.com/@example"
SURROGATE = "\ud800"
BELL = "\x07"
SOH = "\x01"
RAW_CHANNEL = f"Chan {SURROGATE} {BELL}Name"
RAW_TITLE = f"Talk {SURROGATE} {BELL}title"
CLEANS_TO_NOTHING = SURROGATE + SOH


def _require_clean_text() -> None:
    assert hasattr(download_domain, "clean_text")


def _passes_guard(value: object) -> bool:
    try:
        download_domain._require_text_clean(value, "value")
    except ValidationError:
        return False
    return True


def _process(service: object, timeout: float = 5.0) -> None:
    service.start_processing()  # type: ignore[attr-defined]
    thread = service._thread  # type: ignore[attr-defined]
    if thread is not None:
        thread.join(timeout=timeout)


def _front(raw: str) -> dict[str, str]:
    # A file read back from disk on Windows has CRLF line ends.
    head = raw.replace("\r\n", "\n").split("---\n", 2)[1]
    fields: dict[str, str] = {}
    for line in head.splitlines():
        key, _, value = line.partition(": ")
        fields[key] = json.loads(value) if value.startswith('"') else value
    return fields


CLEAN_CASES = (
    ("surrogate-inside", f"Talk {SURROGATE} title", "Talk title"),
    ("control-inside", f"Talk{BELL} title", "Talk title"),
    ("control-joins", f"Ta{SOH}lk", "Talk"),
    ("whitespace-runs", "  a\t\tb\n c  ", "a b c"),
    ("zero-width-kept", "a\u200bb", "a\u200bb"),
    ("only-surrogates", SURROGATE + "\udfff", None),
    ("only-controls", BELL + SOH, None),
    ("only-whitespace", " \t\n ", None),
    ("mixed-nothing", f" {SURROGATE}{SOH} ", None),
    ("empty", "", None),
    ("none", None, None),
    ("int", 7, None),
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [case[1:] for case in CLEAN_CASES],
    ids=[case[0] for case in CLEAN_CASES],
)
def test_ac_147_1_clean_text_drops_controls_and_surrogates(
    value: object, expected: str | None
) -> None:
    _require_clean_text()
    got = download_domain.clean_text(value)
    assert got == expected
    if got is not None:
        assert _passes_guard(got)


def test_ac_147_1_adapter_uses_the_domain_cleaner() -> None:
    _require_clean_text()
    from avkit_infra.youtube import adapter

    assert not hasattr(adapter, "_clean_text")
    assert not hasattr(adapter, "_UNCLEAN_CATEGORIES")
    assert adapter.clean_text is download_domain.clean_text


def test_ac_147_2_channel_fallback_cleaned_for_a_playlist(tmp_path: Path) -> None:
    _require_clean_text()
    from avkit_core.services.transcript import slugify

    service, _settings, yt, uow, filesystem, _captions, _sleeps = _transcript_stack(tmp_path)
    yt.channel = None
    yt.ids = ["v1"]
    yt.playlist = PlaylistInfo(playlist_id="ch", title=RAW_CHANNEL, video_ids=["v1"])
    job = service.add_channel(URL)
    stored = uow.transcripts.get_job(job.id)
    assert stored is not None
    assert stored.channel_name == "Chan Name"
    assert _passes_guard(stored.channel_name)
    assert job.output_dir == tmp_path / slugify(RAW_CHANNEL)
    _process(service)
    raw = filesystem.files[job.output_dir / "raw" / "v1.md"]
    assert _front(raw)["channel"] == "Chan Name"


def test_ac_147_2_channel_fallback_cleaned_for_a_video(tmp_path: Path) -> None:
    _require_clean_text()
    from avkit_core.services.transcript import slugify

    service, _settings, yt, uow, filesystem, _captions, _sleeps = _transcript_stack(tmp_path)
    yt.channel = None
    yt.ids = []
    yt.playlist = None
    yt.video = VideoInfo(video_id="vid1", title=RAW_CHANNEL, duration=1.0, formats=[])
    job = service.add_channel(URL)
    stored = uow.transcripts.get_job(job.id)
    assert stored is not None
    assert stored.channel_name == "Chan Name"
    assert _passes_guard(stored.channel_name)
    assert job.output_dir == tmp_path / slugify(RAW_CHANNEL)
    _process(service)
    raw = filesystem.files[job.output_dir / "raw" / "vid1.md"]
    assert _front(raw)["channel"] == "Chan Name"


def test_ac_147_3_title_that_cleans_to_nothing_takes_the_playlist_id(tmp_path: Path) -> None:
    _require_clean_text()
    service, _settings, yt, uow, _filesystem, _captions, _sleeps = _transcript_stack(tmp_path)
    yt.channel = None
    yt.ids = ["v1"]
    yt.playlist = PlaylistInfo(playlist_id="ch", title=CLEANS_TO_NOTHING, video_ids=["v1"])
    job = service.add_channel(URL)
    stored = uow.transcripts.get_job(job.id)
    assert stored is not None
    assert stored.channel_name == "ch"
    assert stored.status is TranscriptStatus.Pending


def test_ac_147_3_title_that_cleans_to_nothing_takes_the_video_id(tmp_path: Path) -> None:
    _require_clean_text()
    service, _settings, yt, uow, _filesystem, _captions, _sleeps = _transcript_stack(tmp_path)
    yt.channel = None
    yt.ids = []
    yt.playlist = None
    yt.video = VideoInfo(video_id="vid1", title=CLEANS_TO_NOTHING, duration=1.0, formats=[])
    job = service.add_channel(URL)
    stored = uow.transcripts.get_job(job.id)
    assert stored is not None
    assert stored.channel_name == "vid1"
    assert stored.status is TranscriptStatus.Pending


def test_ac_147_4_result_title_cleaned_and_falls_back_to_the_id(tmp_path: Path) -> None:
    _require_clean_text()
    service, _settings, yt, uow, _filesystem, captions, _sleeps = _transcript_stack(tmp_path)
    yt.titles = {}
    captions.results["v1"] = TranscriptResult(
        video_id="v1", title=RAW_TITLE, text="hello world", language="en"
    )
    captions.results["v2"] = TranscriptResult(
        video_id="v2", title=CLEANS_TO_NOTHING, text="hello world", language="en"
    )
    job = service.add_channel(URL)
    _process(service)
    items = {item.video_id: item for item in uow.transcripts.list_items(job.id)}
    for video_id, want in (("v1", "Talk title"), ("v2", "v2")):
        assert items[video_id].status is TranscriptItemStatus.Done
        assert items[video_id].title == want
        assert _passes_guard(items[video_id].title)
        raw = (job.output_dir / "raw" / f"{video_id}.md").read_bytes().decode("utf-8")
        assert _front(raw)["title"] == want


@pytest.mark.integration
def test_ac_147_5_unclean_fallbacks_survive_real_storage(tmp_path: Path) -> None:
    _require_clean_text()
    from tests.unit.test_services import FakeCaptions

    from avkit_core.services.extract import ExtractCoordinator
    from avkit_core.services.settings import SettingsService
    from avkit_core.services.transcript import TranscriptService
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork
    from avkit_infra.filesystem.writer import FilesystemAdapter

    yt = DownloadYouTube()
    yt.channel = None
    yt.ids = ["a"]
    yt.playlist = PlaylistInfo(playlist_id="ch", title=RAW_CHANNEL, video_ids=["a"])
    captions = FakeCaptions()
    captions.results["a"] = TranscriptResult(
        video_id="a", title=RAW_TITLE, text="hello world", language="en"
    )
    engine = create_sqlite_engine(tmp_path / "avkit.db")
    try:
        init_schema(engine)
        session_factory = create_session_factory(engine)

        def uow_factory() -> SqlAlchemyUnitOfWork:
            return SqlAlchemyUnitOfWork(session_factory)

        settings = SettingsService(uow_factory)
        settings.set("transcript", "output_dir", str(tmp_path / "out"))
        service = TranscriptService(
            uow_factory,
            coordinator=ExtractCoordinator(yt),
            captions=captions,
            filesystem=FilesystemAdapter(),
            settings=settings,
            sleep=lambda _seconds: None,
        )
        error = None
        job = None
        try:
            job = service.add_channel(URL)
        except Exception as exc:  # the Red records the failure as a value, not a crash
            error = type(exc).__name__
        assert error is None
        assert job is not None
        _process(service)
        with uow_factory() as uow:
            stored = uow.transcripts.get_job(job.id)
            items = uow.transcripts.list_items(job.id)
        assert stored is not None
        assert stored.status is TranscriptStatus.Done
        assert stored.channel_name == "Chan Name"
        assert [item.title for item in items] == ["Talk title"]
        raw = (job.output_dir / "raw" / "a.md").read_bytes().decode("utf-8")
        front = _front(raw)
        assert front["title"] == "Talk title"
        assert front["channel"] == "Chan Name"
    finally:
        engine.dispose()
