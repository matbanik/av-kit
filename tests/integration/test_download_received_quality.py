"""MEU-124 received quality, column upgrade, bare-channel queue and startup line (Session 55)."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from avkit_core.domain.download import DownloadOptions, DownloadResult, VideoInfo
from avkit_core.domain.enums import AudioFormat, DownloadStatus, QualityPreset

# The download_jobs DDL as shipped before MEU-124 (`pre-change-download-jobs.sql`).
_PRE_MEU_124_DOWNLOAD_JOBS = """
CREATE TABLE download_jobs (
	id VARCHAR(36) NOT NULL,
	url TEXT NOT NULL,
	video_id TEXT NOT NULL,
	title TEXT NOT NULL,
	quality TEXT NOT NULL,
	audio_only BOOLEAN NOT NULL,
	audio_format TEXT NOT NULL,
	status TEXT NOT NULL,
	progress FLOAT NOT NULL,
	speed_bps FLOAT,
	eta_seconds INTEGER,
	file_size INTEGER,
	file_path TEXT,
	error_message TEXT,
	queue_position INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	PRIMARY KEY (id)
)
"""

WATCH = "https://www.youtube.com/watch?v="
CHANNEL_URL = "https://www.youtube.com/@chan"

# The bare-channel shape yt-dlp returns (AC-124.10): three tabs, each a nested playlist whose
# id is the channel's, one video in two tabs, and a playlist nested in a tab.
BARE_CHANNEL: dict[str, Any] = {
    "_type": "playlist",
    "id": "UCchan",
    "title": "Chan",
    "channel": "Chan",
    "entries": [
        {
            "_type": "playlist",
            "id": "UCchan",
            "title": "Chan - Videos",
            "entries": [
                {"_type": "url", "id": "v1", "title": "One"},
                {"_type": "url", "id": "v2", "title": "Two"},
                {"_type": "url", "id": "v3", "title": "Three"},
            ],
        },
        {
            "_type": "playlist",
            "id": "UCchan",
            "title": "Chan - Shorts",
            "entries": [
                {"_type": "url", "id": "s1", "title": "Short one"},
                {"_type": "url", "id": "s2", "title": "Short two"},
                {"_type": "url", "id": "v1", "title": "One as a short"},
                {
                    "_type": "playlist",
                    "id": "PLinner",
                    "title": "Inner",
                    "entries": [{"_type": "url", "id": "i1", "title": "Inner video"}],
                },
            ],
        },
        {
            "_type": "playlist",
            "id": "UCchan",
            "title": "Chan - Live",
            "entries": [
                {"_type": "url", "id": "l1", "title": "Live one"},
                {"_type": "url", "id": "l2", "title": "Live two"},
                {"_type": "url", "id": "l3", "title": "Live three"},
            ],
        },
    ],
}


class _RecordingYouTube:
    """A download port that records each URL it is asked for and never touches the network."""

    def __init__(self, height: int | None = None) -> None:
        self.height = height
        self.urls: list[str] = []

    def extract_info(self, url: str, flat: bool = False, options: object = None) -> VideoInfo:
        return VideoInfo(video_id="vid1", title="One", duration=1.0, formats=[])

    def download(self, url: str, options: DownloadOptions) -> DownloadResult:
        self.urls.append(url)
        video_id = url.split("watch?v=", 1)[1] if "watch?v=" in url else "vid1"
        return DownloadResult(
            file_path=Path("out.mp4"),
            file_size=12,
            video_id=video_id,
            title=video_id,
            sabr_detected=False,
            height=self.height,
        )


def _patch_bare_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeYDL:
        def __init__(self, opts: dict[str, Any]) -> None:
            self.opts = opts

        def __enter__(self) -> FakeYDL:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

        def extract_info(self, url: str, download: bool = False) -> dict[str, Any]:
            assert download is False
            return BARE_CHANNEL

    monkeypatch.setattr("avkit_infra.youtube.adapter.YoutubeDL", FakeYDL)


def _real_service(db_path: Path, youtube: object, coordinator_port: object) -> Any:
    from tests.unit.test_services import FakeMedia

    from avkit_core.services.download import DownloadService
    from avkit_core.services.extract import ExtractCoordinator
    from avkit_core.services.settings import SettingsService
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    engine = create_sqlite_engine(db_path)
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    service = DownloadService(
        factory,  # type: ignore[arg-type]
        youtube=youtube,  # type: ignore[arg-type]
        media=FakeMedia(),  # type: ignore[arg-type]
        coordinator=ExtractCoordinator(coordinator_port),  # type: ignore[arg-type]
        settings=SettingsService(factory),  # type: ignore[arg-type]
        sleep=lambda _seconds: None,
    )
    return service, factory, engine


def _run_queue(service: Any) -> None:
    service.start_processing()
    thread = service._thread
    assert thread is not None
    thread.join(timeout=5)
    assert not thread.is_alive()


@pytest.mark.integration
def test_ac_124_7_old_database_gains_the_column(tmp_path: Path) -> None:
    from sqlalchemy import inspect as sa_inspect

    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.migrations import apply_migrations
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    def _columns(engine: object) -> list[str]:
        return [col["name"] for col in sa_inspect(engine).get_columns("download_jobs")]

    fresh = create_sqlite_engine(tmp_path / "fresh.db")
    init_schema(fresh)
    fresh_columns = _columns(fresh)
    fresh.dispose()

    old_path = tmp_path / "old.db"
    job_id = str(uuid4())
    connection = sqlite3.connect(old_path)
    connection.execute(_PRE_MEU_124_DOWNLOAD_JOBS)
    connection.execute(
        "INSERT INTO download_jobs (id, url, video_id, title, quality, audio_only, audio_format,"
        " status, progress, speed_bps, eta_seconds, file_size, file_path, error_message,"
        " queue_position, created_at, updated_at)"
        " VALUES (?, 'https://youtu.be/old0000001', 'old0000001', 'Old clip', 'P1080', 0,"
        " 'Default', 'Done', 1.0, 2048.0, 0, 4096, 'C:/out/Old clip.mp4', NULL, 0,"
        " '2026-10-01 10:00:00.000000', '2026-10-01 10:05:00.000000')",
        (job_id,),
    )
    connection.commit()
    connection.close()

    engine = create_sqlite_engine(old_path)
    init_schema(engine)
    assert _columns(engine) == fresh_columns
    assert fresh_columns[-1] == "received_height"
    session_factory = create_session_factory(engine)
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        loaded = uow.downloads.get(job_id)
    assert loaded is not None
    assert loaded.received_height is None
    assert loaded.url == "https://youtu.be/old0000001"
    assert loaded.video_id == "old0000001"
    assert loaded.title == "Old clip"
    assert loaded.quality is QualityPreset.P1080
    assert loaded.audio_only is False
    assert loaded.audio_format is AudioFormat.Default
    assert loaded.status is DownloadStatus.Done
    assert loaded.progress == 1.0
    assert loaded.speed_bps == 2048.0
    assert loaded.eta_seconds == 0
    assert loaded.file_size == 4096
    assert loaded.file_path == Path("C:/out/Old clip.mp4")
    assert loaded.error_message is None
    assert loaded.queue_position == 0
    assert loaded.created_at.replace(tzinfo=None) == datetime(2026, 10, 1, 10, 0, 0)
    assert loaded.updated_at.replace(tzinfo=None) == datetime(2026, 10, 1, 10, 5, 0)

    apply_migrations(engine)
    assert _columns(engine) == fresh_columns
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        assert [job.id for job in uow.downloads.list_ordered()] == [job_id]
    engine.dispose()


@pytest.mark.integration
def test_ac_124_8_received_height_persists_in_sqlite(tmp_path: Path) -> None:
    port = _RecordingYouTube(height=360)
    service, factory, engine = _real_service(tmp_path / "avkit.db", port, port)
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    _run_queue(service)
    with factory() as uow:
        jobs = uow.downloads.list_ordered()
    assert [job.status for job in jobs] == [DownloadStatus.Done]
    assert jobs[0].received_height == 360
    engine.dispose()


@pytest.mark.integration
def test_ac_124_12_bare_channel_queues_its_videos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    _patch_bare_channel(monkeypatch)
    port = _RecordingYouTube()
    service, factory, engine = _real_service(tmp_path / "avkit.db", port, YouTubeAdapter())
    created = service.add_to_queue(CHANNEL_URL, QualityPreset.P1080, False, AudioFormat.Default)
    queued = [job.video_id for job in created]
    assert queued == ["v1", "v2", "v3", "s1", "s2", "l1", "l2", "l3"]
    assert all(job.status is DownloadStatus.Pending for job in created)
    assert "UCchan" not in queued
    assert "i1" not in queued

    _run_queue(service)
    with factory() as uow:
        jobs = uow.downloads.list_ordered()
    assert port.urls == [WATCH + job.video_id for job in jobs]
    assert CHANNEL_URL not in port.urls
    assert [job.status for job in jobs] == [DownloadStatus.Done] * len(queued)
    engine.dispose()


@pytest.mark.integration
def test_ac_124_13_startup_line_holds_no_database_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    from avkit_api.wiring import build_services
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    marker = f"s55MARKER{uuid4().hex}"
    app_data = tmp_path / marker
    services, dispose = build_services(app_data=app_data)
    try:
        captured = capfd.readouterr()
        lines = (captured.out + captured.err).splitlines()
        assert [line for line in lines if marker.casefold() in line.casefold()] == []
        assert any("engine.created" in line for line in captured.out.splitlines())
        ring = " ".join(event.message for event in services.health.console_snapshot(0))
        assert marker.casefold() not in ring.casefold()
        console_log = app_data / "logs" / "console.log"
        if console_log.exists():
            assert marker.casefold() not in console_log.read_text(encoding="utf-8").casefold()
    finally:
        dispose()
