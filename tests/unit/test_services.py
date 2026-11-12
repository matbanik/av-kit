"""Phase 3 service-layer tests — registered TEST_SERVICES gate."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Self
from uuid import uuid4

import pytest
from tests.tts_asset_fakes import FakeAssets, idle_runtime

from avkit_core.domain.download import (
    CookieTestResult,
    DownloadArchiveEntry,
    DownloadJob,
    DownloadResult,
    PlaylistInfo,
    SABRStatus,
    VideoInfo,
)
from avkit_core.domain.enums import (
    AudioFormat,
    DownloadStatus,
    QualityPreset,
    QueueProcessorState,
    SABRMode,
    SABRSource,
)
from avkit_core.domain.errors import (
    ConflictError,
    CookieTestError,
    NotFoundError,
    ValidationError,
)
from avkit_core.domain.settings import Setting
from avkit_core.services.download import DownloadService
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.health import HealthService
from avkit_core.services.settings import SettingsService


class FakeSettingsRepo:
    def __init__(self) -> None:
        self._rows: dict[tuple[str, str], Setting] = {}

    def get(self, namespace: str, key: str) -> Setting | None:
        return self._rows.get((namespace, key))

    def set(self, setting: Setting) -> None:
        self._rows[(setting.namespace, setting.key)] = setting

    def get_namespace(self, namespace: str) -> list[Setting]:
        return [row for (ns, _key), row in self._rows.items() if ns == namespace]

    def set_namespace(self, namespace: str, settings: list[Setting]) -> None:
        stale = [key for (ns, key) in self._rows if ns == namespace]
        for key in stale:
            del self._rows[(namespace, key)]
        for setting in settings:
            self.set(setting)


class _UnsupportedRepo:
    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"unexpected repo method {name}")


class FakeDownloadRepo:
    def __init__(self) -> None:
        self._rows: dict[str, DownloadJob] = {}
        self.bulk_reset_calls = 0

    def add(self, job: DownloadJob) -> None:
        self._rows[job.id] = job

    def get(self, job_id: str) -> DownloadJob | None:
        return self._rows.get(job_id)

    def list_ordered(self) -> list[DownloadJob]:
        return sorted(self._rows.values(), key=lambda job: job.queue_position)

    def save(self, job: DownloadJob) -> None:
        self._rows[job.id] = job

    def reorder(self, job_ids: list[str]) -> None:
        for index, job_id in enumerate(job_ids):
            job = self._rows[job_id]
            self._rows[job_id] = DownloadJob(**{**job.__dict__, "queue_position": index})

    def delete(self, job_id: str) -> None:
        self._rows.pop(job_id, None)

    def delete_all(self) -> None:
        self._rows.clear()

    def reset_failed(self) -> None:
        self.bulk_reset_calls += 1


class FakeTTSRepo:
    def __init__(self) -> None:
        self._rows: dict[str, object] = {}

    def add(self, job: object) -> None:
        self._rows[job.id] = job  # type: ignore[attr-defined]

    def get(self, job_id: str) -> object | None:
        return self._rows.get(job_id)

    def save(self, job: object) -> None:
        self._rows[job.id] = job  # type: ignore[attr-defined]

    def delete(self, job_id: str) -> None:
        self._rows.pop(job_id, None)

    # FIXTURE_REPAIRS (b) (Session 33, MEU-77): the port gains list_by_status.
    def list_by_status(self, status: object) -> list[object]:
        return [job for job in self._rows.values() if job.status is status]  # type: ignore[attr-defined]


class FakeModelRepo:
    def __init__(self) -> None:
        self._rows: dict[str, object] = {}

    def list_catalog(self) -> list[object]:
        return list(self._rows.values())

    def get(self, variant_id: str) -> object | None:
        return self._rows.get(variant_id)

    def mark_downloaded(self, variant_id: str, path: Path) -> None:
        row = self._rows[variant_id]
        self._rows[variant_id] = replace(row, path=path, is_downloaded=True)


class FakeTranscriptRepo:
    def __init__(self) -> None:
        self._jobs: dict[str, object] = {}
        self._items: dict[str, list[object]] = {}

    def add_job(self, job: object) -> None:
        self._jobs[job.id] = job  # type: ignore[attr-defined]

    def get_job(self, job_id: str) -> object | None:
        return self._jobs.get(job_id)

    def list_jobs_ordered(self) -> list[object]:
        return sorted(self._jobs.values(), key=lambda job: job.queue_position)  # type: ignore[attr-defined]

    def save_job(self, job: object) -> None:
        self._jobs[job.id] = job  # type: ignore[attr-defined]

    def reorder_jobs(self, job_ids: list[str]) -> None:
        for index, job_id in enumerate(job_ids):
            job = self._jobs[job_id]
            self._jobs[job_id] = replace(job, queue_position=index)

    def delete_job(self, job_id: str) -> None:
        self._jobs.pop(job_id, None)
        self._items.pop(job_id, None)

    def replace_items(self, job_id: str, items: list[object]) -> None:
        self._items[job_id] = list(items)

    def list_items(self, job_id: str) -> list[object]:
        return list(self._items.get(job_id, []))

    def save_item(self, item: object) -> None:
        rows = list(self._items.get(item.job_id, []))  # type: ignore[attr-defined]
        updated = False
        for index, row in enumerate(rows):
            if row.id == item.id:  # type: ignore[attr-defined]
                rows[index] = item
                updated = True
                break
        if not updated:
            rows.append(item)
        self._items[item.job_id] = rows  # type: ignore[attr-defined]

    def count_items(self, job_id: str) -> int:
        return len(self.list_items(job_id))

    def count_items_with_status(self, job_id: str, status: object) -> int:
        return sum(1 for item in self.list_items(job_id) if item.status is status)  # type: ignore[attr-defined]


class FakeArchiveRepo:
    def __init__(self) -> None:
        self._rows: dict[tuple[str, str], DownloadArchiveEntry] = {}

    def get(self, extractor: str, video_id: str) -> DownloadArchiveEntry | None:
        return self._rows.get((extractor, video_id))

    def add(self, entry: DownloadArchiveEntry) -> None:
        self._rows[(entry.extractor, entry.video_id)] = entry

    def list(self) -> list[DownloadArchiveEntry]:
        return list(self._rows.values())


class FakeConversionRepo:
    def __init__(self) -> None:
        self.rows: dict[str, object] = {}

    def add(self, job: object) -> None:
        self.rows[getattr(job, "id")] = job

    def get(self, job_id: str) -> object | None:
        return self.rows.get(job_id)

    def list_ordered(self) -> list[object]:
        return list(self.rows.values())

    def save(self, job: object) -> None:
        self.rows[getattr(job, "id")] = job

    def reorder(self, job_ids: list[str]) -> None:
        return None

    def delete(self, job_id: str) -> None:
        self.rows.pop(job_id, None)

    def delete_all(self) -> None:
        self.rows.clear()


class FakeCaptureShotRepo:
    def __init__(self) -> None:
        self.rows: dict[str, object] = {}

    def add(self, shot: object) -> None:
        self.rows[getattr(shot, "id")] = shot

    def get(self, shot_id: str) -> object | None:
        return self.rows.get(shot_id)

    def list(self) -> list[object]:
        return list(self.rows.values())

    def save(self, shot: object) -> None:
        self.rows[getattr(shot, "id")] = shot

    def delete(self, shot_id: str) -> None:
        self.rows.pop(shot_id, None)

    def get_by_path(self, original_path: Path) -> object | None:
        for shot in self.rows.values():
            if getattr(shot, "original_path") == original_path:
                return shot
        return None


class FakeCaptureRequestRepo:
    def __init__(self) -> None:
        self.rows: dict[str, object] = {}

    def add(self, request: object) -> None:
        self.rows[getattr(request, "id")] = request

    def get(self, request_id: str) -> object | None:
        return self.rows.get(request_id)

    def save(self, request: object) -> None:
        self.rows[getattr(request, "id")] = request

    def list(self) -> list[object]:
        return list(self.rows.values())

    def get_pending_request(self) -> object | None:
        for request in self.rows.values():
            status = getattr(request, "status")
            name = getattr(status, "name", status)
            if name == "Pending":
                return request
        return None


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.settings = FakeSettingsRepo()
        self.downloads = FakeDownloadRepo()
        self.archive = FakeArchiveRepo()
        self.transcripts = FakeTranscriptRepo()
        self.tts_jobs = FakeTTSRepo()
        self.models = FakeModelRepo()
        self.conversion_jobs = FakeConversionRepo()
        self.capture_shots = FakeCaptureShotRepo()
        self.capture_requests = FakeCaptureRequestRepo()
        self.commits = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        return None


class SharedFakeFactory:
    def __init__(self, uow: FakeUnitOfWork) -> None:
        self.uow = uow

    def __call__(self) -> FakeUnitOfWork:
        return self.uow


class FakeMedia:
    def __init__(self, version: str | None = "7.0") -> None:
        self._version = version

    def is_available(self) -> bool:
        return self._version is not None

    def ffmpeg_version(self) -> str | None:
        return self._version

    def ffmpeg_binaries(self) -> object:
        # FIXTURE_REPAIRS (c) (Session 33, MEU-78): the fake follows MediaPort.
        return None

    def convert(self, input_path: Path, output_path: Path, options: object) -> None:
        raise AssertionError("convert not used in MEU-13")

    def probe(self, file_path: Path) -> object:
        raise AssertionError("probe not used in MEU-13")

    def detect_gpu(self) -> object:
        from avkit_core.domain.conversion import GPUCapabilities

        return GPUCapabilities(
            nvidia_nvenc=False,
            amd_amf=False,
            intel_qsv=False,
            vulkan=False,
            software_h265=True,
            software_h264=True,
            recommended_encoder="libx265",
            checked_at=None,
        )

    def encode(
        self,
        input_path: Path,
        output_path: Path,
        options: object,
        on_progress: object,
        should_stop: object,
    ) -> None:
        return None

    def cut(
        self,
        input_path: Path,
        output_path: Path,
        options: object,
        on_progress: object,
        should_stop: object,
    ) -> None:
        return None

    def extract_stream(
        self,
        input_path: Path,
        output_path: Path,
        options: object,
        on_progress: object,
        should_stop: object,
    ) -> None:
        return None


class FakeYouTube:
    def __init__(self, version: str | None = "2026.01.01") -> None:
        self._version = version

    def extract_info(self, url: str, flat: bool = False, options: object = None) -> object:
        raise AssertionError("extract_info not used in MEU-13")

    def extract_video_ids(self, channel_url: str) -> list[str]:
        raise AssertionError("extract_video_ids not used in MEU-13")

    def download(self, url: str, options: object) -> object:
        raise AssertionError("download not used in MEU-13")

    def get_formats(self, video_id: str) -> list[object]:
        raise AssertionError("get_formats not used in MEU-13")

    def check_sabr_status(self) -> object:
        raise AssertionError("check_sabr_status not used in MEU-13")

    def test_cookies(
        self,
        mode: str,
        browser: str | None,
        profile: str | None,
        cookie_file: Path | None,
    ) -> object:
        raise AssertionError("test_cookies not used in MEU-13")

    def ytdlp_version(self) -> str | None:
        return self._version


def _settings_service() -> tuple[SettingsService, FakeUnitOfWork]:
    uow = FakeUnitOfWork()
    return SettingsService(SharedFakeFactory(uow)), uow


def test_ac_13_1_defaults_fill_when_no_row() -> None:
    service, _uow = _settings_service()
    assert service.get("downloader", "quality") == "1080p"
    assert service.get("app", "log_to_file") is False
    assert service.get("tts", "speed") == 1.0
    ns = service.get_namespace("ui")
    assert ns["theme"] == "dark"
    assert None not in ns.values()


def test_ac_13_2_set_round_trips_declared_types() -> None:
    service, uow = _settings_service()
    service.set("app", "log_to_file", True)
    service.set("transcript", "requests_per_hour", 120)
    service.set("downloader", "quality", "720p")
    assert service.get("app", "log_to_file") is True
    assert service.get("app", "log_to_file") is not True or isinstance(
        service.get("app", "log_to_file"), bool
    )
    assert service.get("transcript", "requests_per_hour") == 120
    assert service.get("downloader", "quality") == "720p"
    stored = uow.settings.get("app", "log_to_file")
    assert stored is not None
    assert stored.value_type.value == "Boolean"
    assert service.get("app", "log_to_file") is True


def test_ac_13_3_unknown_extra_wrong_type_and_range() -> None:
    service, _uow = _settings_service()
    with pytest.raises(ValidationError):
        service.set("nope", "path", "/tmp")
    with pytest.raises(ValidationError):
        service.set("downloader", "nope", "x")
    with pytest.raises(ValidationError):
        service.set_namespace("downloader", {"quality": "1080p", "nope": 1})
    with pytest.raises(ValidationError):
        service.set("downloader", "audio_only", "true")
    with pytest.raises(ValidationError):
        service.set("downloader", "quality", "4k")
    with pytest.raises(ValidationError):
        service.set("tts", "device", "gpu")
    with pytest.raises(ValidationError):
        service.set("ui", "theme", "solarized")
    with pytest.raises(ValidationError):
        service.set("app", "log_level", "verbose")
    with pytest.raises(ValidationError):
        service.set("tts", "speed", 0.1)
    with pytest.raises(ValidationError):
        service.set("transcript", "requests_per_hour", -1)
    with pytest.raises(ValidationError):
        service.set("transcript", "playlist_end", -1)


def test_ac_13_4_dotted_ui_keys_and_cookie_bytes() -> None:
    service, _uow = _settings_service()
    with pytest.raises(ValidationError):
        service.set("ui", "rail.collapsed", True)
    with pytest.raises(ValidationError):
        service.set("ui", "panel.console.height", 12)
    service.set("ui", "theme", "light")
    assert service.get("ui", "theme") == "light"
    with pytest.raises(ValidationError):
        service.set("downloader", "cookie_file_path", "HTTP_COOKIE=secret")
    with pytest.raises(ValidationError):
        service.set("app", "log_level", "#HttpOnly_\tchrome\ttrue")
    with pytest.raises(ValidationError):
        service.set("downloader", "path", "x" * 5000)


def test_ac_13_5_seq_owner_monotonic_and_restart(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    import structlog

    factory = SharedFakeFactory(FakeUnitOfWork())
    service = SettingsService(factory)
    health = HealthService(
        factory,
        app_data=tmp_path,
        settings=service,
        media=FakeMedia(),
        youtube=FakeYouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
        ring_capacity=8,
    )
    log = structlog.get_logger(module="test")
    log.info("first")
    log.info("second")
    events = health.console_snapshot(0)
    assert [event.seq for event in events] == [1, 2]
    other = HealthService(
        factory,
        app_data=tmp_path,
        settings=service,
        media=FakeMedia(),
        youtube=FakeYouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
        ring_capacity=8,
    )
    log.info("after-restart")
    restarted = other.console_snapshot(0)
    assert restarted[0].seq == 1


def test_ac_13_6_ring_and_after_seq(tmp_path: Path) -> None:
    import structlog

    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    health = HealthService(
        factory,
        app_data=tmp_path,
        settings=settings,
        media=FakeMedia(),
        youtube=FakeYouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
        ring_capacity=3,
    )
    log = structlog.get_logger(module="ring")
    for index in range(4):
        log.info(f"n{index}")
    events = health.console_snapshot(0)
    assert [event.seq for event in events] == [2, 3, 4]
    assert health.console_snapshot(4) == []


def test_ac_13_7_redact_before_enqueue(tmp_path: Path) -> None:
    import structlog

    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    health = HealthService(
        factory,
        app_data=tmp_path,
        settings=settings,
        media=FakeMedia(),
        youtube=FakeYouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
    )
    log = structlog.get_logger(module="secrets")
    log.info("Authorization Bearer abc")
    event = health.console_snapshot(0)[0]
    assert "abc" not in event.message
    assert "[REDACTED]" in event.message
    log.info("cookie file contents")
    cookie_event = health.console_snapshot(0)[-1]
    assert "cookie" not in cookie_event.message.lower() or "[REDACTED]" in cookie_event.message


def test_ac_13_8_liveness_dependencies_and_startup_metric(tmp_path: Path) -> None:
    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    health = HealthService(
        factory,
        app_data=tmp_path,
        settings=settings,
        media=FakeMedia("6.1"),
        youtube=FakeYouTube("2024.12"),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
    )
    assert health.liveness().ok is True
    deps = health.dependencies()
    assert deps.ffmpeg_version == "6.1"
    assert deps.ytdlp_version == "2024.12"
    before = len(factory.uow.settings.get_namespace("app"))
    health.record_startup_metric("boot_ms", 12)
    after = factory.uow.settings.get_namespace("app")
    assert len(after) == before
    assert any(event.message for event in health.console_snapshot(0))


def test_ac_13_9_g29_real_tmp_uow_settings(tmp_path: Path) -> None:
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

    service = SettingsService(factory)
    service.set("ui", "theme", "light")
    assert service.get("ui", "theme") == "light"


def test_ac_13_10_log_file_append_exception(tmp_path: Path) -> None:
    import structlog

    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    settings.set("app", "log_to_file", True)
    _health = HealthService(
        factory,
        app_data=tmp_path,
        settings=settings,
        media=FakeMedia(),
        youtube=FakeYouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
    )
    log = structlog.get_logger(module="file")
    log.info("line-one Bearer secret")
    log.info("line-two")
    path = tmp_path / "logs" / "console.log"
    text = path.read_text(encoding="utf-8")
    assert "line-one" in text
    assert "line-two" in text
    assert "secret" not in text
    assert text.count("\n") >= 2


class DownloadYouTube(FakeYouTube):
    def __init__(self) -> None:
        super().__init__()
        self.extract_calls = 0
        self.ids_calls = 0
        self.check_calls = 0
        self.playlist: PlaylistInfo | None = None
        self.video = VideoInfo(video_id="vid1", title="One", duration=1.0, formats=[])
        self.ids: list[str] = ["c1", "c2"]
        self.titles: dict[str, str] = {}
        self.channel: str | None = None
        self.delay = False
        self._release = __import__("threading").Event()
        self._entered = __import__("threading").Event()
        self.in_flight = 0
        self.max_in_flight = 0
        self.cookie_error: CookieTestError | None = None
        self.download_result = DownloadResult(
            file_path=Path("out.mp4"),
            file_size=12,
            video_id="vid1",
            title="One",
            sabr_detected=False,
        )
        self.service: DownloadService | None = None
        self.block_download = False
        self.download_entered = __import__("threading").Event()
        self.download_release = __import__("threading").Event()
        self.download_error: Exception | None = None
        self.last_options: object | None = None
        self.download_urls: list[str] = []

    def extract_info(
        self, url: str, flat: bool = False, options: object = None
    ) -> VideoInfo | PlaylistInfo:
        self.extract_calls += 1
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        self._entered.set()
        try:
            if self.delay:
                self._release.wait(timeout=2)
            if self.playlist is not None:
                return self.playlist
            return self.video
        finally:
            self.in_flight -= 1

    def extract_video_ids(self, channel_url: str) -> object:
        from avkit_core.domain.download import ListedVideo, VideoListing

        self.ids_calls += 1
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        try:
            if self.delay:
                self._release.wait(timeout=2)
            return VideoListing(
                tuple(ListedVideo(video_id, self.titles.get(video_id)) for video_id in self.ids),
                self.channel,
            )
        finally:
            self.in_flight -= 1

    def download(self, url: str, options: object) -> DownloadResult:
        self.download_urls.append(url)
        self.last_options = options
        self.download_entered.set()
        if self.block_download:
            self.download_release.wait(timeout=2)
        if self.service is not None and self.service.should_stop():
            from avkit_core.domain.errors import DownloadCancelledError

            raise DownloadCancelledError("cancelled")
        if self.download_error is not None:
            raise self.download_error
        if self.service is not None:
            self.service.on_download_progress(5, 10, 2.0)
        return self.download_result

    def check_sabr_status(self) -> SABRStatus:
        self.check_calls += 1
        return SABRStatus(
            mode=SABRMode.Active, source=SABRSource.Detected, checked_at=datetime.now(UTC)
        )

    def test_cookies(
        self,
        mode: str,
        browser: str | None,
        profile: str | None,
        cookie_file: Path | None,
    ) -> CookieTestResult:
        if self.cookie_error is not None:
            raise self.cookie_error
        return CookieTestResult(ok=True, error_message=None)


def _download_stack() -> tuple[DownloadService, SettingsService, DownloadYouTube, FakeUnitOfWork]:
    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    youtube = DownloadYouTube()
    coordinator = ExtractCoordinator(youtube)
    service = DownloadService(
        factory,
        youtube=youtube,
        coordinator=coordinator,
        settings=settings,
        sleep=lambda _seconds: None,
    )
    youtube.service = service
    return service, settings, youtube, uow


def test_ac_10_1_video_and_playlist_inserts() -> None:
    service, _settings, youtube, uow = _download_stack()
    jobs = service.add_to_queue(
        "https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default
    )
    assert len(jobs) == 1
    assert jobs[0].title == "One"
    youtube.playlist = PlaylistInfo(playlist_id="pl", title="P", video_ids=["a", "b", "c"])
    more = service.add_to_queue(
        "https://youtube.com/pl", QualityPreset.P1080, False, AudioFormat.Default
    )
    assert len(more) == 3
    assert {job.title for job in more} == {"a", "b", "c"}
    assert len(uow.downloads.list_ordered()) == 4


def test_ac_10_2_duplicate_video_id_skipped() -> None:
    service, _settings, _youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    assert len(uow.downloads.list_ordered()) == 1


def test_ac_10_3_archive_skip_and_clear_keeps_archive() -> None:
    service, settings, _youtube, uow = _download_stack()
    settings.set("downloader", "archive_tracking", True)
    uow.archive.add(
        DownloadArchiveEntry(
            extractor="youtube",
            video_id="vid1",
            title="One",
            recorded_at=datetime.now(UTC),
        )
    )
    jobs = service.add_to_queue(
        "https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default
    )
    assert jobs[0].status is DownloadStatus.Skipped
    service.clear_queue()
    assert uow.archive.get("youtube", "vid1") is not None
    assert uow.downloads.list_ordered() == []


def test_ac_10_4_apply_lock_transitions() -> None:
    service, _settings, _youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    service.force_sabr()
    job = uow.downloads.list_ordered()[0]
    assert job.status is DownloadStatus.QualityBlocked
    service.clear_sabr()
    assert uow.downloads.list_ordered()[0].status is DownloadStatus.Pending
    done = DownloadJob(
        **{
            **job.__dict__,
            "status": DownloadStatus.Done,
            "id": str(uuid4()),
            "video_id": "done1",
        }
    )
    uow.downloads.add(done)
    service.force_sabr()
    assert uow.downloads.get(done.id).status is DownloadStatus.Done


def test_ac_10_5_add_time_quality_blocked_insert() -> None:
    service, _settings, _youtube, _uow = _download_stack()
    service.force_sabr()
    jobs = service.add_to_queue(
        "https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default
    )
    assert jobs[0].status is DownloadStatus.QualityBlocked


def test_ac_10_6_apply_defaults_skips_done() -> None:
    service, settings, _youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    job = uow.downloads.list_ordered()[0]
    uow.downloads.save(
        DownloadJob(
            **{**job.__dict__, "status": DownloadStatus.Done, "quality": QualityPreset.P1080}
        )
    )
    settings.set("downloader", "quality", "360p")
    count = service.apply_defaults_to_pending()
    assert count == 0
    assert uow.downloads.list_ordered()[0].quality is QualityPreset.P1080


def test_ac_10_7_and_10_8_worker_done_and_pause_cancel() -> None:
    service, _settings, youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert uow.downloads.list_ordered()[0].status is DownloadStatus.Done
    assert uow.archive.get("youtube", "vid1") is not None
    assert service.get_processor_state().state is QueueProcessorState.Idle
    youtube.video = VideoInfo(video_id="vid2", title="Two", duration=1.0, formats=[])
    service.add_to_queue("https://youtu.be/vid2", QualityPreset.P1080, False, AudioFormat.Default)
    service.pause_processing()
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    # pause before start of next job after first already done; new job stays pending or pauses
    assert service.get_processor_state().state in {
        QueueProcessorState.Paused,
        QueueProcessorState.Idle,
    }


def test_ac_10_9_nan_progress_skipped() -> None:
    service, _settings, _youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    service._runtime = service.get_processor_state()
    object.__setattr__(
        service,
        "_runtime",
        service.get_processor_state().__class__(
            queue_name="downloads",
            state=QueueProcessorState.Processing,
            current_job_id=uow.downloads.list_ordered()[0].id,
        ),
    )
    service.on_download_progress(float("nan"), 10, 1.0)
    assert uow.downloads.list_ordered()[0].progress == 0.0


def test_ac_10_10_cookie_error_cause() -> None:
    service, _settings, youtube, _uow = _download_stack()
    cause = OSError("denied")
    youtube.cookie_error = CookieTestError("bad")
    youtube.cookie_error.__cause__ = cause
    with pytest.raises(CookieTestError) as exc:
        service.test_cookies("file", None, None, Path("cookies.txt"))
    assert exc.value.__cause__ is cause


def test_ac_10_11_extract_cache_and_mutex() -> None:
    service, _settings, youtube, _uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    assert youtube.extract_calls == 1
    assert youtube.max_in_flight <= 1


def test_ac_10_12_reorder_remove_get_job() -> None:
    service, _settings, youtube, _uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    youtube.video = VideoInfo(video_id="vid2", title="Two", duration=1.0, formats=[])
    service.add_to_queue("https://youtu.be/vid2", QualityPreset.P1080, False, AudioFormat.Default)
    ids = [job.id for job in service.get_queue()]
    service.reorder_queue(list(reversed(ids)))
    assert [job.id for job in service.get_queue()] == list(reversed(ids))
    with pytest.raises(ValidationError):
        service.reorder_queue([ids[0]])
    service.remove_from_queue(ids[0])
    with pytest.raises(NotFoundError):
        service.get_job(ids[0])


def test_ac_10_15_reset_failed_single_row() -> None:
    service, _settings, _youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    job = uow.downloads.list_ordered()[0]
    failed = DownloadJob(
        **{
            **job.transition(DownloadStatus.Downloading)
            .transition(DownloadStatus.Failed)
            .__dict__,
            "error_message": "x",
        }
    )
    uow.downloads.save(failed)
    other = DownloadJob(
        **{
            **failed.__dict__,
            "id": str(uuid4()),
            "video_id": "other",
            "status": DownloadStatus.Failed,
            "queue_position": 1,
        }
    )
    uow.downloads.add(other)
    reset = service.reset_failed(failed.id)
    assert reset.status is DownloadStatus.Pending
    assert uow.downloads.get(other.id).status is DownloadStatus.Failed
    assert uow.downloads.bulk_reset_calls == 0
    with pytest.raises(ConflictError):
        service.reset_failed(reset.id)


def test_ac_10_16_getters_do_not_probe_sabr() -> None:
    service, _settings, youtube, _uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    assert service.get_queue()
    assert service.get_processor_state().queue_name == "downloads"
    service.get_sabr_status()
    assert youtube.check_calls == 0


def test_ac_10_14_g29_real_tmp_uow_download(tmp_path: Path) -> None:
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

    settings = SettingsService(factory)
    youtube = DownloadYouTube()
    service = DownloadService(
        factory,
        youtube=youtube,
        coordinator=ExtractCoordinator(youtube),
        settings=settings,
        sleep=lambda _seconds: None,
    )
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    assert service.get_queue()[0].video_id == "vid1"


def test_ac_10_3_tracking_off_inserts_pending() -> None:
    service, settings, _youtube, uow = _download_stack()
    settings.set("downloader", "archive_tracking", False)
    uow.archive.add(
        DownloadArchiveEntry(
            extractor="youtube",
            video_id="vid1",
            title="One",
            recorded_at=datetime.now(UTC),
        )
    )
    jobs = service.add_to_queue(
        "https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default
    )
    assert jobs[0].status is DownloadStatus.Pending


def test_ac_10_4_p360_stays_pending() -> None:
    service, _settings, youtube, uow = _download_stack()
    youtube.video = VideoInfo(video_id="ok360", title="Low", duration=1.0, formats=[])
    service.add_to_queue("https://youtu.be/ok360", QualityPreset.P360, False, AudioFormat.Default)
    service.force_sabr()
    assert uow.downloads.list_ordered()[0].status is DownloadStatus.Pending


def test_ac_10_7_pause_after_current() -> None:
    service, _settings, youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    youtube.video = VideoInfo(video_id="vid2", title="Two", duration=1.0, formats=[])
    service.add_to_queue("https://youtu.be/vid2", QualityPreset.P1080, False, AudioFormat.Default)
    youtube.block_download = True
    service.start_processing()
    assert youtube.download_entered.wait(timeout=2)
    service.pause_processing()
    youtube.download_release.set()
    if service._thread is not None:
        service._thread.join(timeout=2)
    statuses = [job.status for job in uow.downloads.list_ordered()]
    assert all(status in DownloadStatus for status in statuses)
    assert statuses[0] is DownloadStatus.Done
    assert statuses[1] is DownloadStatus.Pending
    assert service.get_processor_state().state is QueueProcessorState.Paused


def test_ac_10_7_cancel_inflight() -> None:
    service, _settings, youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    youtube.block_download = True
    service.start_processing()
    assert youtube.download_entered.wait(timeout=2)
    service.stop_processing()
    youtube.download_release.set()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert uow.downloads.list_ordered()[0].status is DownloadStatus.Cancelled
    assert service.get_processor_state().state is QueueProcessorState.Idle


def test_ac_10_8_age_restricted() -> None:
    from avkit_core.domain.errors import AgeRestrictedError

    service, _settings, youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    youtube.download_error = AgeRestrictedError("age")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert uow.downloads.list_ordered()[0].status is DownloadStatus.AgeRestricted


def test_ac_10_11_concurrent_extract_mutex() -> None:
    import threading

    service, _settings, youtube, _uow = _download_stack()
    youtube.delay = True
    errors: list[BaseException] = []

    def _add(url: str, video_id: str) -> None:
        try:
            youtube.video = VideoInfo(video_id=video_id, title=video_id, duration=1.0, formats=[])
            service.add_to_queue(url, QualityPreset.P1080, False, AudioFormat.Default)
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    first = threading.Thread(target=_add, args=("https://youtu.be/a", "a"))
    first.start()
    assert youtube._entered.wait(timeout=2)
    second = threading.Thread(target=_add, args=("https://youtu.be/b", "b"))
    second.start()
    youtube._release.set()
    first.join(timeout=2)
    second.join(timeout=2)
    assert errors == []
    assert youtube.max_in_flight == 1


def test_ac_10_13_archive_skip_before_start() -> None:
    service, settings, _youtube, uow = _download_stack()
    settings.set("downloader", "archive_tracking", True)
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    uow.archive.add(
        DownloadArchiveEntry(
            extractor="youtube",
            video_id="vid1",
            title="One",
            recorded_at=datetime.now(UTC),
        )
    )
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert uow.downloads.list_ordered()[0].status is DownloadStatus.Skipped


def test_ac_10_10_unknown_cookie_mode() -> None:
    service, _settings, _youtube, _uow = _download_stack()
    with pytest.raises(ValidationError):
        service.test_cookies("bytes", None, None, None)


class FakeFilesystem:
    def __init__(self) -> None:
        self.files: dict[Path, str] = {}
        self.read_calls: list[tuple[Path, int]] = []
        self.dirs: list[Path] = []
        self.progress_exports: list[object] = []
        self.audio_writes = 0

    def write_text_atomic(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self.files[path] = text

    def write_progress_export(self, output_dir: Path, video_ids_done: list[str]) -> None:
        self.progress_exports.append((output_dir, list(video_ids_done)))

    def ensure_channel_dirs(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "raw").mkdir(parents=True, exist_ok=True)
        (output_dir / "compiled").mkdir(parents=True, exist_ok=True)
        self.dirs.append(output_dir)

    def write_audio_wav(self, path: Path, samples: object, sample_rate: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"RIFF")
        self.audio_writes += 1
        self.files[path] = "wav"

    def read_text(self, path: Path, *, max_bytes: int) -> str:
        self.read_calls.append((path, max_bytes))
        if path in self.files:
            return self.files[path]
        return path.read_text(encoding="utf-8")


class FakeCaptions:
    def __init__(self) -> None:
        self.results: dict[str, object] = {}
        self.fetch_calls: list[tuple[str, list[str]]] = []
        self.hold = False
        self.entered = __import__("threading").Event()
        self.release = __import__("threading").Event()
        self.retryable_left = 0
        self.clock: Callable[[], float] | None = None
        self.starts: list[float] = []
        self.on_call: Callable[[int], None] | None = None

    def get_transcript(self, video_id: str, languages: list[str]) -> object:
        from avkit_core.domain.errors import TranscriptRetryableError
        from avkit_core.domain.transcript import TranscriptResult

        self.fetch_calls.append((video_id, list(languages)))
        if self.clock is not None:
            self.starts.append(self.clock())
        if self.on_call is not None:
            self.on_call(len(self.fetch_calls))
        self.entered.set()
        if self.hold:
            self.release.wait(timeout=2)
        if video_id in self.results:
            value = self.results[video_id]
            if isinstance(value, Exception):
                raise value
            return value
        if self.retryable_left > 0:
            self.retryable_left -= 1
            raise TranscriptRetryableError("temp")
        return TranscriptResult(
            video_id=video_id,
            title=video_id,
            text="hello world",
            language="en",
        )


class FakeClock:
    """A monotonic clock that only its own `sleep` advances (MEU-116 rate cap)."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []
        self.on_sleep: Callable[[float], None] | None = None

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds
        if self.on_sleep is not None:
            self.on_sleep(self.now)


def _transcript_stack(
    tmp_path: Path,
    *,
    youtube: DownloadYouTube | None = None,
    coordinator: ExtractCoordinator | None = None,
    factory: SharedFakeFactory | None = None,
    clock: FakeClock | None = None,
    sleep: Callable[[float], None] | None = None,
):
    import inspect

    from avkit_core.services.transcript import TranscriptService

    uow = factory.uow if factory is not None else FakeUnitOfWork()
    factory = factory or SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("transcript", "output_dir", str(tmp_path))
    yt = youtube or DownloadYouTube()
    yt.ids = ["v1", "v2"]
    yt.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=list(yt.ids))
    coord = coordinator or ExtractCoordinator(yt)
    filesystem = FakeFilesystem()
    captions = FakeCaptions()
    sleeps: list[float] = clock.sleeps if clock is not None else []
    extra: dict[str, object] = {}
    if clock is not None:
        captions.clock = clock
        # The MEU-116 guards run before the service takes a clock; the required tests
        # assert the parameter first (_require_clock).
        if "clock" in inspect.signature(TranscriptService).parameters:
            extra["clock"] = clock
    service = TranscriptService(
        factory,
        coordinator=coord,
        captions=captions,
        filesystem=filesystem,
        settings=settings,
        sleep=sleep or (clock.sleep if clock is not None else sleeps.append),
        **extra,  # type: ignore[arg-type]
    )
    return service, settings, yt, uow, filesystem, captions, sleeps


def test_ac_11_1_add_channel_and_no_progress_read(tmp_path: Path) -> None:
    service, settings, _yt, uow, filesystem, _captions, _sleeps = _transcript_stack(tmp_path)
    settings.set("transcript", "playlist_end", 1)
    job = service.add_channel("https://youtube.com/@example")
    assert job.channel_name == "My Channel"
    assert job.video_count == 1
    assert job.status.value == "Pending"
    assert filesystem.dirs
    items = uow.transcripts.list_items(job.id)
    assert len(items) == 1
    assert items[0].status.value == "Pending"
    assert filesystem.read_calls == []
    with pytest.raises(ConflictError):
        service.add_channel("https://youtube.com/@example")


def test_ac_11_2_start_pending_only(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptStatus

    service, _settings, _yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path)
    paused = service.add_channel("https://youtube.com/@paused")
    uow.transcripts.save_job(
        replace(paused, status=TranscriptStatus.Paused, channel_url="https://youtube.com/@paused")
    )
    pending = service.add_channel("https://youtube.com/@pending")
    captions.hold = True
    service.start_processing()
    assert captions.entered.wait(timeout=2)
    assert uow.transcripts.get_job(paused.id).status is TranscriptStatus.Paused
    assert uow.transcripts.get_job(pending.id).status is TranscriptStatus.Processing
    with pytest.raises(ConflictError):
        service.start_processing()
    service.stop_processing()
    captions.release.set()
    if service._thread is not None:
        service._thread.join(timeout=2)


def test_ac_11_3_resume_only_from_paused(tmp_path: Path) -> None:
    service, _settings, _yt, _uow, _fs, _captions, _sleeps = _transcript_stack(tmp_path)
    service.add_channel("https://youtube.com/@example")
    with pytest.raises(ConflictError):
        service.resume_processing()


def test_ac_11_4_stop_leaves_pending_and_keeps_done(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus

    service, _settings, _yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path)
    job = service.add_channel("https://youtube.com/@example")
    captions.hold = True
    service.start_processing()
    assert captions.entered.wait(timeout=2)
    service.stop_processing()
    captions.release.set()
    if service._thread is not None:
        service._thread.join(timeout=2)
    parent = uow.transcripts.get_job(job.id)
    assert parent.status is TranscriptStatus.Cancelled
    items = uow.transcripts.list_items(job.id)
    assert all(item.status is TranscriptItemStatus.Pending for item in items)
    assert service.get_processor_state().state is QueueProcessorState.Idle
    assert service.get_processor_state().current_job_id is None


def test_ac_11_5_requeue_and_retry(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
    from avkit_core.domain.transcript import TranscriptItem

    service, _settings, _yt, uow, _fs, _captions, _sleeps = _transcript_stack(tmp_path)
    job = service.add_channel("https://youtube.com/@example")
    cancelled = job.transition(TranscriptStatus.Processing).transition(TranscriptStatus.Cancelled)
    uow.transcripts.save_job(cancelled)
    requeued = service.requeue_channel(job.id)
    assert requeued.status is TranscriptStatus.Pending
    with pytest.raises(ConflictError):
        service.requeue_channel(job.id)
    failed = requeued.transition(TranscriptStatus.Processing).transition(TranscriptStatus.Failed)
    uow.transcripts.save_job(failed)
    items = uow.transcripts.list_items(job.id)
    done = TranscriptItem(
        **{
            **items[0].__dict__,
            "status": TranscriptItemStatus.Done,
            "path": tmp_path / "raw" / "v1.md",
            "word_count": 2,
        }
    )
    failed_item = TranscriptItem(
        **{
            **items[1].__dict__,
            "status": TranscriptItemStatus.Failed,
            "error_message": "x",
        }
    )
    uow.transcripts.replace_items(job.id, [done, failed_item])
    retried = service.retry_failed_channel(job.id)
    assert retried.status is TranscriptStatus.Pending
    after = {item.video_id: item for item in uow.transcripts.list_items(job.id)}
    assert after["v1"].status is TranscriptItemStatus.Done
    assert after["v2"].status is TranscriptItemStatus.Pending


def test_ac_11_6_skip_retry_and_write(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
    from avkit_core.domain.transcript import TranscriptFailureCause, TranscriptSkip

    service, settings, yt, uow, filesystem, captions, sleeps = _transcript_stack(tmp_path)
    yt.ids = ["none", "retry"]
    yt.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=list(yt.ids))
    settings.set("transcript", "max_retries", 1)
    settings.set("transcript", "retry_delay", 7)
    captions.results["none"] = TranscriptSkip(TranscriptFailureCause.no_captions)
    captions.retryable_left = 3
    job = service.add_channel("https://youtube.com/@retry")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    items = {item.video_id: item for item in uow.transcripts.list_items(job.id)}
    assert items["none"].status is TranscriptItemStatus.Skipped
    assert items["retry"].status is TranscriptItemStatus.Pending
    assert items["retry"].retry_count == 0
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Paused
    assert 7 in sleeps
    assert not any(
        item.video_id == "retry" and "hello world" in str(item) for item in items.values()
    )
    assert all("progress.json" not in str(path) for path, _max in filesystem.read_calls)


def test_ac_11_7_delay_and_batch_sleeps(tmp_path: Path) -> None:
    service, settings, _yt, _uow, _fs, _captions, sleeps = _transcript_stack(tmp_path)
    settings.set("transcript", "delay_between_requests", 6)
    settings.set("transcript", "batch_size", 1)
    settings.set("transcript", "pause_between_batches", 9)
    service.add_channel("https://youtube.com/@example")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert 6 in sleeps
    assert 9 in sleeps


def test_ac_11_8_failed_parent_skips_zip(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptStatus
    from avkit_core.domain.errors import DomainError

    service, settings, yt, uow, filesystem, captions, _sleeps = _transcript_stack(tmp_path)
    yt.ids = ["ok", "bad"]
    yt.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=list(yt.ids))
    settings.set("transcript", "max_retries", 0)
    captions.results["bad"] = DomainError("no")
    job = service.add_channel("https://youtube.com/@fail")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    parent = uow.transcripts.get_job(job.id)
    assert parent.status is TranscriptStatus.Failed
    assert parent.zip_path is None
    assert not list(tmp_path.rglob("*.zip"))


def test_ac_11_9_and_11_10_compile_split_and_zip(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptStatus

    service, settings, _yt, uow, filesystem, _captions, _sleeps = _transcript_stack(tmp_path)
    settings.set("transcript", "max_words_per_document", 2)
    job = service.add_channel("https://youtube.com/@example")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    parent = uow.transcripts.get_job(job.id)
    assert parent.status is TranscriptStatus.Done
    compiled = list((parent.output_dir / "compiled").glob("*_vol*.md"))
    assert len(compiled) == 2
    raw_before = {
        path: path.read_text(encoding="utf-8")
        for path in (parent.output_dir / "raw").glob("*.md")
    }
    assert parent.zip_path is not None
    assert parent.zip_path.exists()
    after = {path: path.read_text(encoding="utf-8") for path in raw_before}
    assert after == raw_before
    assert filesystem.read_calls


def test_ac_11_11_recover_stale_processing(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptStatus

    service, _settings, _yt, uow, _fs, _captions, _sleeps = _transcript_stack(tmp_path)
    job = service.add_channel("https://youtube.com/@example")
    uow.transcripts.save_job(job.transition(TranscriptStatus.Processing))
    paused = service.add_channel("https://youtube.com/@paused")
    uow.transcripts.save_job(replace(paused, status=TranscriptStatus.Paused))
    service.recover_stale_processing()
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Pending
    assert uow.transcripts.get_job(paused.id).status is TranscriptStatus.Paused


def test_ac_11_12_remove_keeps_files(tmp_path: Path) -> None:
    service, _settings, _yt, uow, filesystem, _captions, _sleeps = _transcript_stack(tmp_path)
    job = service.add_channel("https://youtube.com/@example")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    files = dict(filesystem.files)
    service.remove_channel(job.id)
    assert uow.transcripts.get_job(job.id) is None
    assert filesystem.files == files
    with pytest.raises(NotFoundError):
        service.get_job(job.id)


def test_ac_11_13_g29_real_tmp_uow_transcript(tmp_path: Path) -> None:
    from avkit_core.services.transcript import TranscriptService
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

    settings = SettingsService(factory)
    settings.set("transcript", "output_dir", str(tmp_path))
    youtube = DownloadYouTube()
    youtube.ids = ["g29"]
    youtube.playlist = PlaylistInfo(playlist_id="ch", title="G29", video_ids=["g29"])
    service = TranscriptService(
        factory,
        coordinator=ExtractCoordinator(youtube),
        captions=FakeCaptions(),
        filesystem=FakeFilesystem(),
        settings=settings,
        sleep=lambda _seconds: None,
    )
    job = service.add_channel("https://youtube.com/@g29")
    assert service.list_items(job.id)[0].video_id == "g29"


def test_ac_11_14_required_getters_and_compile(tmp_path: Path) -> None:
    service, _settings, _yt, _uow, _fs, _captions, _sleeps = _transcript_stack(tmp_path)
    first = service.add_channel("https://youtube.com/@a")
    second = service.add_channel("https://youtube.com/@b")
    service.reorder_queue([second.id, first.id])
    assert [job.id for job in service.get_queue()] == [second.id, first.id]
    with pytest.raises(ValidationError):
        service.reorder_queue([first.id])
    got = service.get_job(first.id)
    assert got.video_count == 2
    assert service.list_items(first.id)
    assert service.get_processor_state().queue_name == "transcripts"
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    paths = service.compile_channel(first.id)
    assert paths
    with pytest.raises(NotFoundError):
        service.get_job(str(uuid4()))


def test_ac_11_15_shared_extract_mutex(tmp_path: Path) -> None:
    import threading

    youtube = DownloadYouTube()
    youtube.delay = True
    youtube.ids = ["c1"]
    youtube.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=["c1"])
    coordinator = ExtractCoordinator(youtube)
    download, _settings, _yt, uow = _download_stack()
    download = DownloadService(
        SharedFakeFactory(uow),
        youtube=youtube,
        coordinator=coordinator,
        settings=SettingsService(SharedFakeFactory(uow)),
        sleep=lambda _seconds: None,
    )
    transcript, *_rest = _transcript_stack(tmp_path, youtube=youtube, coordinator=coordinator)
    errors: list[BaseException] = []

    def _download() -> None:
        try:
            youtube.video = VideoInfo(video_id="dl", title="DL", duration=1.0, formats=[])
            download.add_to_queue(
                "https://youtu.be/dl", QualityPreset.P1080, False, AudioFormat.Default
            )
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    def _channel() -> None:
        try:
            transcript.add_channel("https://youtube.com/@mutex")
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    first = threading.Thread(target=_download)
    first.start()
    assert youtube._entered.wait(timeout=2)
    second = threading.Thread(target=_channel)
    second.start()
    youtube._release.set()
    first.join(timeout=2)
    second.join(timeout=2)
    assert errors == []
    assert youtube.max_in_flight == 1


def test_ac_12_1_prepare_order_and_unknown() -> None:
    from avkit_core.services.prepare import TextPreparationService

    service = TextPreparationService()
    left = service.prepare("Hello!!! AI", ["kokoro", "punctuation"])
    right = service.prepare("Hello!!! AI", ["punctuation", "kokoro"])
    assert left == right
    with pytest.raises(ValidationError):
        service.prepare("Hello", ["not-a-step"])
    only_ws = service.prepare("  30  ", ["whitespace"])
    assert "thirty" not in only_ws
    assert "30" in only_ws


def test_ac_12_2_chunk_and_kokoro(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_core.domain.errors import SpacyModelNotFoundError
    from avkit_core.services.prepare import SPACY_MODEL, TextPreparationService

    class _Sent:
        def __init__(self, text: str) -> None:
            self.text = text

    class _Doc:
        def __init__(self, text: str) -> None:
            parts = [part.strip() for part in text.replace("!", ".").split(".") if part.strip()]
            self.sents = [_Sent(part) for part in parts]

    class _Nlp:
        def __call__(self, text: str) -> _Doc:
            return _Doc(text)

    class _Spacy:
        def load(self, name: str) -> _Nlp:
            assert name == SPACY_MODEL
            return _Nlp()

    monkeypatch.setitem(__import__("sys").modules, "spacy", _Spacy())
    service = TextPreparationService()
    chunked = service.prepare("First sentence. Second sentence.", ["chunk"], chunk_max_chars=20)
    assert "First" in chunked
    long = " ".join(["word"] * 26)
    kokoro = service.prepare('He said “AI is 30” ... ' + long, ["kokoro"])
    assert "A I" in kokoro
    assert "thirty" in kokoro
    assert "“" not in kokoro
    assert "..." not in kokoro
    assert all(len(part.split()) <= 25 for part in kokoro.split(".") if part.strip())

    class _Missing:
        def load(self, name: str) -> _Nlp:
            raise OSError("missing")

    monkeypatch.setitem(__import__("sys").modules, "spacy", _Missing())
    with pytest.raises(SpacyModelNotFoundError):
        service.prepare("Hello there.", ["chunk"])
    cleaned = service.prepare("  Hello   there  ", ["whitespace"])
    assert cleaned == "Hello there"


class FakeTTSPort:
    def __init__(self) -> None:
        from avkit_core.domain.enums import DeviceType
        from avkit_core.domain.tts import ModelStatus, VoiceConfig

        self.voices = [
            VoiceConfig(
                voice_id="am_eric",
                lang_code="a",
                language="en",
                gender="m",
                style_description="narration",
            )
        ]
        self.status = ModelStatus(
            variant_id="kokoro-pt-fp32",
            name="Kokoro",
            device="cpu",
            memory_bytes=1,
            is_loaded=True,
        )
        self.progress_values: list[float] = [0.25, 1.0]
        self.load_calls: list[object] = []
        self.unload_calls = 0
        self.generate_calls = 0
        self.service = None
        self.hold = False
        self.entered = __import__("threading").Event()
        self.release = __import__("threading").Event()
        self.in_flight = 0
        self.max_in_flight = 0
        # TA-4 (Session 35, MEU-75)
        self.devices: tuple[object, ...] = (DeviceType.Auto, DeviceType.CPU)
        self.device_calls: list[object] = []
        # TA-3 (Session 51, MEU-117): the formats whose runtime this fake build lacks.
        self.absent: set[object] = set()

    def load_model(self, variant: object, device: object) -> None:
        self.load_calls.append((variant, device))

    def unload_model(self) -> None:
        self.unload_calls += 1

    def generate(self, text: str, voice: object, speed: float, on_progress: object) -> object:
        import numpy as np

        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        self.entered.set()
        try:
            if self.hold:
                self.release.wait(timeout=2)
            self.generate_calls += 1
            self.last_text = text
            for value in self.progress_values:
                on_progress(value)
            return np.zeros(8, dtype=np.float32)
        finally:
            self.in_flight -= 1

    def list_voices(self) -> list[object]:
        return list(self.voices)

    def get_model_status(self) -> object:
        return self.status

    def available_devices(self, fmt: object) -> tuple[object, ...]:
        self.device_calls.append(fmt)
        return self.devices

    def runtime_present(self, fmt: object) -> bool:
        return fmt not in self.absent


class FakeCatalog:
    def __init__(self) -> None:
        self.sideload_rows: list[object] = []
        self.download_error: Exception | None = None
        self.progress = [0.4]
        self.hold = False
        self.hold_after_progress = False
        self.entered = __import__("threading").Event()
        self.release = __import__("threading").Event()
        self.progressed = __import__("threading").Event()
        self.release_after_progress = __import__("threading").Event()
        self.in_flight = 0
        self.max_in_flight = 0

    def download(self, variant: object, dest_dir: Path, on_progress: object) -> Path:
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        self.entered.set()
        try:
            if self.hold:
                self.release.wait(timeout=2)
            if self.download_error is not None:
                raise self.download_error
            for value in self.progress:
                on_progress(value)
                self.progressed.set()
                if self.hold_after_progress:
                    self.release_after_progress.wait(timeout=2)
            return dest_dir / "model.bin"
        finally:
            self.in_flight -= 1

    def sideload(self, models_dir: Path) -> list[object]:
        return list(self.sideload_rows)


class FakeConvertMedia(FakeMedia):
    def __init__(self) -> None:
        super().__init__()
        self.convert_calls: list[object] = []

    def convert(self, input_path: Path, output_path: Path, options: object) -> None:
        self.convert_calls.append((input_path, output_path, options))
        output_path.write_bytes(b"mp3")


def _tts_stack(tmp_path: Path):
    from avkit_core.domain.enums import ModelFormat, ModelPrecision
    from avkit_core.domain.tts import ModelVariant
    from avkit_core.services.models import ModelService
    from avkit_core.services.prepare import TextPreparationService
    from avkit_core.services.tts import TTSService

    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("tts", "output_path", str(tmp_path))
    settings.set("tts", "models_directory", str(tmp_path / "models"))
    variant = ModelVariant(
        id="kokoro-pt-fp32",
        name="Kokoro PT",
        format=ModelFormat.PyTorch,
        precision=ModelPrecision.FP32,
        size_bytes=1,
        path=None,
        is_downloaded=False,
    )
    uow.models._rows[variant.id] = variant
    tts_port = FakeTTSPort()
    catalog = FakeCatalog()
    filesystem = FakeFilesystem()
    media = FakeConvertMedia()
    prepare = TextPreparationService()
    models = ModelService(
        factory, catalog=catalog, tts=tts_port, settings=settings, assets=FakeAssets()
    )
    service = TTSService(
        factory,
        tts=tts_port,
        filesystem=filesystem,
        media=media,
        settings=settings,
        prepare=prepare,
        assets=FakeAssets(),
        # FIXTURE_REPAIRS (a) (Session 33, MEU-77): run the worker synchronously.
        spawn=lambda fn: fn(),
    )
    tts_port.service = service
    return service, models, tts_port, catalog, filesystem, media, uow


def test_ac_12_3_and_12_4_generate_hash_and_mp3(tmp_path: Path) -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind
    from avkit_core.domain.progress import ConvertOptions

    service, _models, tts_port, _catalog, filesystem, media, _uow = _tts_stack(tmp_path)
    job = service.generate(
        "hello world",
        "am_eric",
        1.0,
        MediaFormat.MP3,
        ["whitespace"],
        TTSSourceKind.File,
        tmp_path / "source.txt",
    )
    assert job.text_preview == "hello world"
    assert job.text_hash
    assert filesystem.read_calls == []
    assert filesystem.audio_writes == 1
    assert media.convert_calls
    _input, output, options = media.convert_calls[0]
    assert output == job.output_path
    assert options == ConvertOptions(
        codec="libmp3lame",
        bitrate_kbps=192,
        sample_rate=24000,
        channels=1,
    )
    assert tts_port.generate_calls == 1


def test_ac_12_5_progress_resolution_and_cancel(tmp_path: Path) -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus

    service, _models, tts_port, _catalog, _fs, _media, uow = _tts_stack(tmp_path)
    tts_port.progress_values = [float("nan"), 0.25]
    job = service.generate(
        "again",
        "am_eric",
        1.0,
        MediaFormat.WAV,
        ["whitespace"],
        TTSSourceKind.Inline,
        None,
    )
    assert job.segments_total == 1000
    assert uow.tts_jobs.get(job.id).segments_done == 250

    def _generate(text: str, voice: object, speed: float, on_progress: object) -> object:
        on_progress(0.1)
        service.cancel(service._current_id)
        on_progress(0.8)
        import numpy as np

        return np.zeros(4, dtype=np.float32)

    tts_port.generate = _generate  # type: ignore[method-assign]
    cancelled = service.generate(
        "cancel-three",
        "am_eric",
        1.0,
        MediaFormat.WAV,
        ["whitespace"],
        TTSSourceKind.Inline,
        None,
    )
    assert cancelled.status is TTSStatus.Cancelled
    tts_port.generate = FakeTTSPort.generate.__get__(tts_port, FakeTTSPort)
    tts_port.progress_values = [1.5]
    # TA-7 (Session 33, MEU-77): the worker records the failure; generate does not raise.
    bad = service.generate(
        "bad-f",
        "am_eric",
        1.0,
        MediaFormat.WAV,
        ["whitespace"],
        TTSSourceKind.Inline,
        None,
    )
    assert service.wait_idle(5.0) is True
    assert service.get_status(bad.id).status is TTSStatus.Failed


def test_ac_12_6_validation_and_illegal_edge(tmp_path: Path) -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus

    service, _models, tts_port, _catalog, _fs, _media, uow = _tts_stack(tmp_path)
    with pytest.raises(ValidationError):
        service.generate("", "am_eric", 1.0, MediaFormat.MP3, [], TTSSourceKind.Inline, None)
    with pytest.raises(ValidationError):
        service.generate("hi", "am_eric", 9.0, MediaFormat.MP3, [], TTSSourceKind.Inline, None)
    tts_port.status = replace(tts_port.status, is_loaded=False)
    with pytest.raises(ConflictError):
        service.generate("hi", "am_eric", 1.0, MediaFormat.MP3, [], TTSSourceKind.Inline, None)
    tts_port.status = replace(tts_port.status, is_loaded=True)
    job = service.generate("hi", "am_eric", 1.0, MediaFormat.WAV, [], TTSSourceKind.Inline, None)
    stored = uow.tts_jobs.get(job.id)
    with pytest.raises(ConflictError):
        stored.transition(TTSStatus.Pending)  # type: ignore[union-attr]


def test_ac_12_7_model_download_runtime(tmp_path: Path) -> None:
    import threading

    from avkit_core.domain.errors import ModelDownloadError
    from avkit_core.services.models import ModelService

    _service, models, _tts, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    catalog.hold = True
    thread = threading.Thread(target=lambda: models.download("kokoro-pt-fp32"))
    thread.start()
    assert catalog.entered.wait(timeout=2)
    with pytest.raises(ConflictError):
        models.download("kokoro-pt-fp32")
    catalog.release.set()
    thread.join(timeout=2)
    if models._thread is not None:
        models._thread.join(timeout=2)
    assert models.get_download_runtime().state == "Idle"
    assert uow.models.get("kokoro-pt-fp32").is_downloaded is True  # type: ignore[union-attr]
    catalog.hold = False
    catalog.download_error = ModelDownloadError("hf")
    uow.models._rows["kokoro-pt-fp32"] = replace(
        uow.models.get("kokoro-pt-fp32"),
        is_downloaded=False,
        path=None,
    )
    with pytest.raises(ModelDownloadError):
        models.download("kokoro-pt-fp32")
        if models._thread is not None:
            models._thread.join(timeout=2)
        if models._worker_error is not None:
            raise models._worker_error
    assert models.get_download_runtime().state == "Failed"
    fresh = ModelService(
        SharedFakeFactory(uow),
        catalog=catalog,
        tts=FakeTTSPort(),
        settings=SettingsService(SharedFakeFactory(uow)),
        assets=FakeAssets(),
    )
    assert fresh.get_download_runtime().state == "Idle"


def test_ac_12_8_list_load_no_torch(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DeviceType, ModelFormat, ModelPrecision
    from avkit_core.domain.tts import ModelVariant

    _service, models, tts_port, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    extra = ModelVariant(
        id="side",
        name="Side",
        format=ModelFormat.ONNX,
        precision=ModelPrecision.INT8,
        size_bytes=2,
        path=tmp_path / "side.onnx",
        is_downloaded=True,
    )
    catalog.sideload_rows = [extra]
    ids = {row.id for row in models.list_available()}
    assert "kokoro-pt-fp32" in ids
    assert "side" in ids
    uow.models.mark_downloaded("kokoro-pt-fp32", tmp_path / "model.bin")
    assert all(row.is_downloaded for row in models.list_downloaded())
    models.load("kokoro-pt-fp32", DeviceType.CPU)
    assert tts_port.load_calls
    models.unload()
    assert tts_port.unload_calls == 1
    assert models.get_status() is tts_port.status
    source = Path("packages/core/src/avkit_core/services/models.py").read_text(encoding="utf-8")
    assert "torch" not in source
    assert "import avkit_infra" not in source


def test_ac_12_9_g29_real_tmp_uow_tts(tmp_path: Path) -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus
    from avkit_core.domain.tts import TTSJob
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

    job = TTSJob(
        id=str(uuid4()),
        source_kind=TTSSourceKind.Inline,
        source_path=None,
        text_hash="abc123def",
        text_preview="hello",
        voice="am_eric",
        speed=1.0,
        format=MediaFormat.WAV,
        status=TTSStatus.Pending,
        output_path=None,
        segments_total=1000,
        segments_done=0,
        error_message=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    with factory() as uow:
        uow.tts_jobs.add(job)
        uow.commit()
        loaded = uow.tts_jobs.get(job.id)
    assert loaded is not None
    assert loaded.text_preview == "hello"
    assert not hasattr(loaded, "text")


def test_ac_12_10_get_status(tmp_path: Path) -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind

    service, _models, _tts, _catalog, _fs, _media, _uow = _tts_stack(tmp_path)
    job = service.generate("hi", "am_eric", 1.0, MediaFormat.WAV, [], TTSSourceKind.Inline, None)
    assert service.get_status(job.id).id == job.id
    with pytest.raises(NotFoundError):
        service.get_status(str(uuid4()))


def test_ac_13_3_nonfinite_rejected_and_corrupt_decode() -> None:
    from avkit_core.domain.enums import SettingValueType
    from avkit_core.domain.settings import Setting

    service, uow = _settings_service()
    with pytest.raises(ValidationError):
        service.set("tts", "speed", float("nan"))
    with pytest.raises(ValidationError):
        service.set("transcript", "requests_per_hour", float("inf"))
    assert uow.settings.get("tts", "speed") is None
    uow.settings.set(
        Setting(
            namespace="tts",
            key="speed",
            value="nan",
            value_type=SettingValueType.Number,
            updated_at=datetime.now(UTC),
        )
    )
    with pytest.raises(ValidationError):
        service.get("tts", "speed")


def test_ac_13_2_set_namespace_atomic_no_partial_write() -> None:
    service, uow = _settings_service()
    service.set("downloader", "quality", "1080p")
    with pytest.raises(ValidationError):
        service.set_namespace("downloader", {"quality": "720p", "audio_only": "true"})
    assert service.get("downloader", "quality") == "1080p"
    assert uow.settings.get("downloader", "audio_only") is None
    service.set_namespace("downloader", {"quality": "480p", "audio_only": True})
    assert service.get("downloader", "quality") == "480p"
    assert service.get("downloader", "audio_only") is True


def test_ac_10_6_apply_defaults_pending_and_blocked() -> None:
    service, settings, _youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    service.force_sabr()
    youtube_pending = uow.downloads.list_ordered()[0]
    assert youtube_pending.status in {DownloadStatus.Pending, DownloadStatus.QualityBlocked}
    settings.set("downloader", "quality", "360p")
    count = service.apply_defaults_to_pending()
    assert count == 1
    assert uow.downloads.list_ordered()[0].quality is QualityPreset.P360


def test_ac_10_9_nonfinite_total_speed_and_throttle() -> None:
    service, _settings, _youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    job_id = uow.downloads.list_ordered()[0].id
    object.__setattr__(
        service,
        "_runtime",
        service.get_processor_state().__class__(
            queue_name="downloads",
            state=QueueProcessorState.Processing,
            current_job_id=job_id,
        ),
    )
    clock = {"now": 10.0}
    service._clock = lambda: clock["now"]
    before = uow.commits
    service.on_download_progress(5, 10, 1.0)
    assert uow.downloads.list_ordered()[0].progress == 0.5
    service.on_download_progress(8, 10, 2.0)
    assert uow.downloads.list_ordered()[0].progress == 0.5
    assert uow.commits == before + 1
    clock["now"] = 11.1
    service.on_download_progress(8, 10, 2.0)
    assert uow.downloads.list_ordered()[0].progress == 0.8
    service.on_download_progress(3, float("inf"), 1.0)
    service.on_download_progress(3, 10, float("nan"))
    assert uow.downloads.list_ordered()[0].progress == 0.8


def test_ac_10_12_remove_keeps_archive_and_illegal_edge() -> None:
    service, _settings, youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    job = uow.downloads.list_ordered()[0]
    uow.archive.add(
        DownloadArchiveEntry(
            extractor="youtube",
            video_id="vid1",
            title="One",
            recorded_at=datetime.now(UTC),
        )
    )
    service.remove_from_queue(job.id)
    assert uow.archive.get("youtube", "vid1") is not None
    done = job.transition(DownloadStatus.Downloading).transition(DownloadStatus.Done)
    with pytest.raises(ConflictError):
        done.transition(DownloadStatus.QualityBlocked)


def test_ac_11_4_stop_after_paused_keeps_done(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
    from avkit_core.domain.transcript import TranscriptItem

    service, _settings, _yt, uow, filesystem, _captions, _sleeps = _transcript_stack(tmp_path)
    job = service.add_channel("https://youtube.com/@example")
    items = uow.transcripts.list_items(job.id)
    done_path = tmp_path / "done.md"
    filesystem.write_text_atomic(done_path, "done")
    uow.transcripts.save_item(
        TranscriptItem(
            **{
                **items[0].__dict__,
                "status": TranscriptItemStatus.Done,
                "path": done_path,
                "word_count": 1,
            }
        )
    )
    paused = replace(
        job.transition(TranscriptStatus.Processing).transition(TranscriptStatus.Paused)
    )
    uow.transcripts.save_job(paused)
    service._runtime = service.get_processor_state().__class__(
        queue_name="transcripts",
        state=QueueProcessorState.Paused,
        current_job_id=None,
    )
    service._thread = None
    service.stop_processing()
    parent = uow.transcripts.get_job(job.id)
    assert parent is not None
    assert parent.status is TranscriptStatus.Cancelled
    leftover = uow.transcripts.list_items(job.id)
    assert leftover[0].status is TranscriptItemStatus.Done
    assert leftover[0].path == done_path
    assert service.get_processor_state().state is QueueProcessorState.Idle


def test_ac_12_5_invalid_progress_marks_failed(tmp_path: Path) -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus

    service, _models, tts_port, _catalog, _fs, _media, uow = _tts_stack(tmp_path)
    tts_port.progress_values = [1.5]
    # TA-8 (Session 33, MEU-77): the worker records the failure; generate does not raise.
    service.generate(
        "bad-f-terminal",
        "am_eric",
        1.0,
        MediaFormat.WAV,
        ["whitespace"],
        TTSSourceKind.Inline,
        None,
    )
    assert service.wait_idle(5.0) is True
    rows = list(uow.tts_jobs._rows.values())
    assert len(rows) == 1
    assert rows[0].status is TTSStatus.Failed


def test_ac_12_6_single_generation_conflict(tmp_path: Path) -> None:
    import threading

    from avkit_core.domain.enums import MediaFormat, TTSSourceKind

    service, _models, tts_port, _catalog, _fs, _media, _uow = _tts_stack(tmp_path)
    tts_port.hold = True
    errors: list[BaseException] = []

    def _run() -> None:
        try:
            service.generate("one", "am_eric", 1.0, MediaFormat.WAV, [], TTSSourceKind.Inline, None)
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(target=_run)
    thread.start()
    assert tts_port.entered.wait(timeout=2)
    with pytest.raises(ConflictError):
        service.generate("two", "am_eric", 1.0, MediaFormat.WAV, [], TTSSourceKind.Inline, None)
    tts_port.release.set()
    thread.join(timeout=2)
    assert errors == []
    assert tts_port.max_in_flight == 1


def test_ac_12_7_immediate_return_fraction_and_lock(tmp_path: Path) -> None:
    import threading

    _service, models, _tts, catalog, _fs, _media, _uow = _tts_stack(tmp_path)
    catalog.hold = True
    catalog.hold_after_progress = True
    returned = threading.Event()
    result: list[object] = []

    def _run() -> None:
        result.append(models.download("kokoro-pt-fp32"))
        returned.set()

    thread = threading.Thread(target=_run)
    thread.start()
    assert returned.wait(timeout=2)
    assert models.get_download_runtime().state == "Downloading"
    assert catalog.entered.wait(timeout=2)
    catalog.release.set()
    assert catalog.progressed.wait(timeout=2)
    assert models.get_download_runtime().fraction == 0.4
    catalog.release_after_progress.set()
    if models._thread is not None:
        models._thread.join(timeout=2)
    thread.join(timeout=2)
    assert models.get_download_runtime().state == "Idle"

    catalog.hold = True
    catalog.hold_after_progress = False
    catalog.entered.clear()
    catalog.release.clear()
    starters = threading.Barrier(2)
    inflight: list[str] = []

    def _contend(label: str) -> None:
        starters.wait()
        try:
            models.download("kokoro-pt-fp32")
            inflight.append(label + "-ok")
        except ConflictError:
            inflight.append(label + "-conflict")

    first = threading.Thread(target=_contend, args=("a",))
    second = threading.Thread(target=_contend, args=("b",))
    first.start()
    second.start()
    assert catalog.entered.wait(timeout=2)
    # download() returns while the catalog is held, so both contenders finish their call
    # before the held download is released; the later caller must see "Downloading" (A14).
    first.join(timeout=2)
    second.join(timeout=2)
    catalog.release.set()
    if models._thread is not None:
        models._thread.join(timeout=2)
    assert sum(1 for item in inflight if item.endswith("-conflict")) == 1
    assert catalog.max_in_flight == 1


def test_ac_12_8_no_direct_mkdir_in_services() -> None:
    import ast
    from pathlib import Path

    root = Path("packages/core/src/avkit_core/services")
    hits: list[str] = []
    for path in root.glob("*.py"):
        if path.name == "health.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "mkdir":
                    hits.append(f"{path.as_posix()}:{node.lineno}")
    assert hits == []


def test_ac_75_7_model_service_available_devices_returns_the_port_value(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DeviceType, ModelFormat

    _service, models, tts_port, _catalog, _filesystem, _media, _uow = _tts_stack(tmp_path)
    expected = (DeviceType.Auto, DeviceType.CUDA, DeviceType.CPU)
    tts_port.devices = expected
    assert models.available_devices(ModelFormat.ONNX) == expected
    assert tts_port.device_calls == [ModelFormat.ONNX]


# --- AC-98.1 / 98.2 / 98.3 SIDELOAD_RECORD, RECORD_RULE (Session 42, MEU-98) -------------------


def _sideload_row(variant_id: str, path: Path, *, onnx: bool = False) -> object:
    from avkit_core.domain.enums import ModelFormat, ModelPrecision
    from avkit_core.domain.tts import ModelVariant

    return ModelVariant(
        id=variant_id,
        name=variant_id,
        format=ModelFormat.ONNX if onnx else ModelFormat.PyTorch,
        precision=ModelPrecision.INT8 if onnx else ModelPrecision.FP32,
        size_bytes=2,
        path=path,
        is_downloaded=True,
    )


def _record_marks(uow: FakeUnitOfWork) -> list[tuple[str, Path]]:
    """Wrap the fake repository's `mark_downloaded` so each call is recorded."""
    calls: list[tuple[str, Path]] = []
    real = uow.models.mark_downloaded

    def mark(variant_id: str, path: Path) -> None:
        calls.append((variant_id, path))
        real(variant_id, path)

    uow.models.mark_downloaded = mark  # type: ignore[method-assign]
    return calls


def _seed_onnx_row(uow: FakeUnitOfWork, path: Path | None, *, downloaded: bool) -> None:
    from avkit_core.domain.enums import ModelFormat, ModelPrecision
    from avkit_core.domain.tts import ModelVariant

    uow.models._rows["kokoro-onnx-int8"] = ModelVariant(
        id="kokoro-onnx-int8",
        name="ONNX INT8",
        format=ModelFormat.ONNX,
        precision=ModelPrecision.INT8,
        size_bytes=1,
        path=path,
        is_downloaded=downloaded,
    )


def test_ac_98_1_list_available_records_sideload(tmp_path: Path) -> None:
    _service, models, _tts, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    models_dir = tmp_path / "models"
    dropped = models_dir / "kokoro.pth"
    catalog.sideload_rows = [
        _sideload_row("kokoro-pt-fp32", dropped),
        _sideload_row("side", models_dir / "side.onnx", onnx=True),
    ]
    marks = _record_marks(uow)
    before = uow.commits
    listed = {row.id: row for row in models.list_available()}
    assert listed["kokoro-pt-fp32"].is_downloaded
    assert listed["side"].is_downloaded
    row = uow.models.get("kokoro-pt-fp32")
    assert row is not None
    assert (row.is_downloaded, row.path) == (True, dropped)
    assert marks == [("kokoro-pt-fp32", dropped)]
    assert uow.commits == before + 1
    models.list_available()
    assert marks == [("kokoro-pt-fp32", dropped)]
    assert uow.commits == before + 1
    assert uow.models.get("side") is None

    # list_downloaded records the same way, on a fresh stack.
    _service, models, _tts, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    catalog.sideload_rows = [_sideload_row("kokoro-pt-fp32", dropped)]
    before = uow.commits
    assert [row.id for row in models.list_downloaded()] == ["kokoro-pt-fp32"]
    row = uow.models.get("kokoro-pt-fp32")
    assert row is not None
    assert (row.is_downloaded, row.path) == (True, dropped)
    assert uow.commits == before + 1


def test_ac_98_1_core_does_no_file_io() -> None:
    source = Path("packages/core/src/avkit_core/services/models.py").read_text(encoding="utf-8")
    for needle in (".is_file(", ".exists(", ".stat(", "avkit_infra"):
        assert needle not in source, needle


def test_ac_98_2_load_records_and_passes_path(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DeviceType

    _service, models, tts_port, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    dropped = tmp_path / "models" / "kokoro.pth"
    catalog.sideload_rows = [_sideload_row("kokoro-pt-fp32", dropped)]
    before = uow.commits
    models.load("kokoro-pt-fp32", DeviceType.CPU)
    assert len(tts_port.load_calls) == 1
    variant, device = tts_port.load_calls[0]
    assert (variant.id, variant.path, variant.is_downloaded) == ("kokoro-pt-fp32", dropped, True)
    assert device is DeviceType.CPU
    row = uow.models.get("kokoro-pt-fp32")
    assert row is not None
    assert row.path == dropped
    assert uow.commits == before + 1


def test_ac_98_2_side_only_id_is_not_found(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DeviceType

    _service, models, tts_port, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    catalog.sideload_rows = [_sideload_row("side", tmp_path / "models" / "side.onnx", onnx=True)]
    with pytest.raises(NotFoundError):
        models.load("side", DeviceType.CPU)
    assert tts_port.load_calls == []
    assert uow.models.get("side") is None


def test_ac_98_2_vocab_conflict_unchanged(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DeviceType
    from avkit_core.domain.tts import AssetState, TtsAsset

    _service, models, tts_port, catalog, _fs, _media, _uow = _tts_stack(tmp_path)
    catalog.sideload_rows = [_sideload_row("kokoro-pt-fp32", tmp_path / "models" / "kokoro.pth")]
    models._assets.states[TtsAsset.ONNX_VOCAB] = AssetState.MISSING  # type: ignore[attr-defined]
    with pytest.raises(ConflictError, match="tts_onnx_vocab"):
        models.load("kokoro-pt-fp32", DeviceType.CPU)
    assert tts_port.load_calls == []

    # With no scanned file, the seeded row reaches the port with `path is None` (unchanged).
    _service, models, tts_port, _catalog, _fs, _media, _uow = _tts_stack(tmp_path)
    models.load("kokoro-pt-fp32", DeviceType.CPU)
    assert [(call[0].id, call[0].path) for call in tts_port.load_calls] == [
        ("kokoro-pt-fp32", None)
    ]


def test_ac_98_2_legacy_row_with_new_file_loads(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DeviceType
    from avkit_core.domain.tts import LEGACY_ONNX_DIR

    _service, models, tts_port, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    models_dir = tmp_path / "models"
    _seed_onnx_row(uow, models_dir / LEGACY_ONNX_DIR / "model_quantized.onnx", downloaded=True)
    current = models_dir / "kokoro-v1.0-onnx" / "onnx" / "model_quantized.onnx"
    catalog.sideload_rows = [_sideload_row("kokoro-onnx-int8", current, onnx=True)]
    conflict: ConflictError | None = None
    try:
        models.load("kokoro-onnx-int8", DeviceType.CPU)
    except ConflictError as exc:  # the legacy 409 before the fix
        conflict = exc
    assert conflict is None, conflict
    assert [(call[0].id, call[0].path) for call in tts_port.load_calls] == [
        ("kokoro-onnx-int8", current)
    ]
    row = uow.models.get("kokoro-onnx-int8")
    assert row is not None
    assert row.path == current


def test_ac_98_2_legacy_row_without_file_still_conflicts(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DeviceType
    from avkit_core.domain.tts import LEGACY_ONNX_DIR

    _service, models, tts_port, _catalog, _fs, _media, uow = _tts_stack(tmp_path)
    legacy = tmp_path / "models" / LEGACY_ONNX_DIR / "model_quantized.onnx"
    _seed_onnx_row(uow, legacy, downloaded=True)
    before = uow.commits
    with pytest.raises(ConflictError, match="re-download"):
        models.load("kokoro-onnx-int8", DeviceType.CPU)
    assert tts_port.load_calls == []
    row = uow.models.get("kokoro-onnx-int8")
    assert row is not None
    assert row.path == legacy
    assert uow.commits == before


def test_ac_98_3_changed_path_rerecorded(tmp_path: Path) -> None:
    _service, models, _tts, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    models_dir = tmp_path / "models"
    managed = models_dir / "kokoro-v1_0.pth"
    dropped = models_dir / "dropped" / "kokoro.pth"
    uow.models.mark_downloaded("kokoro-pt-fp32", managed)
    catalog.sideload_rows = [_sideload_row("kokoro-pt-fp32", dropped)]
    marks = _record_marks(uow)
    before = uow.commits
    models.list_available()
    row = uow.models.get("kokoro-pt-fp32")
    assert row is not None
    assert row.path == dropped
    assert marks == [("kokoro-pt-fp32", dropped)]
    assert uow.commits == before + 1


def test_ac_98_3_same_path_not_written(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DeviceType

    _service, models, tts_port, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    managed = tmp_path / "models" / "kokoro-v1_0.pth"
    uow.models.mark_downloaded("kokoro-pt-fp32", managed)
    catalog.sideload_rows = [_sideload_row("kokoro-pt-fp32", managed)]
    marks = _record_marks(uow)
    before = uow.commits
    models.list_available()
    models.list_downloaded()
    models.load("kokoro-pt-fp32", DeviceType.CPU)
    assert marks == []
    assert uow.commits == before
    assert [call[0].path for call in tts_port.load_calls] == [managed]


# --- MEU-115 failure reason: items, jobs and log lines ---------------------------------------


def _run_reasons(
    tmp_path: Path, ids: list[str], results: dict[str, object], *, max_retries: int = 0
):
    service, settings, yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path)
    yt.ids = list(ids)
    yt.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=list(ids))
    settings.set("transcript", "max_retries", max_retries)
    captions.results.update(results)
    job = service.add_channel("https://youtube.com/@reasons")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    return job, uow


def test_ac_115_5_items_store_the_failure_message(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus
    from avkit_core.domain.errors import DomainError, TranscriptRetryableError
    from avkit_core.domain.transcript import (
        TranscriptFailureCause,
        TranscriptSkip,
        failure_message,
    )

    cause = TranscriptFailureCause
    job, uow = _run_reasons(
        tmp_path,
        ["none", "gone", "broken", "linked", "secret", "ok", "blocked"],
        {
            "none": TranscriptSkip(cause.no_captions),
            "gone": TranscriptSkip(cause.unavailable),
            "broken": DomainError("the video is age-restricted"),
            "linked": DomainError("line one https://example.invalid/x?token=abc\nline two"),
            "secret": DomainError("Authorization: Bearer SYNTHETIC_ITEM_MARKER"),
            "blocked": TranscriptRetryableError("caption request blocked"),
        },
        max_retries=1,
    )
    items = {item.video_id: item for item in uow.transcripts.list_items(job.id)}
    status = TranscriptItemStatus
    assert {key: (item.status, item.error_message) for key, item in items.items()} == {
        "none": (status.Skipped, failure_message(cause.no_captions)),
        "gone": (status.Skipped, failure_message(cause.unavailable)),
        "broken": (status.Failed, failure_message(cause.other, "the video is age-restricted")),
        "linked": (status.Failed, failure_message(cause.other, "line one [link]")),
        "secret": (status.Failed, failure_message(cause.other, "[REDACTED]")),
        "ok": (status.Done, None),
        "blocked": (status.Pending, failure_message(cause.blocked)),
    }


def test_ac_115_6_job_message_counts_failures_and_skips(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptStatus
    from avkit_core.domain.errors import DomainError
    from avkit_core.domain.transcript import TranscriptFailureCause, TranscriptSkip

    skip = TranscriptSkip(TranscriptFailureCause.no_captions)
    failed, failed_uow = _run_reasons(
        tmp_path / "failed",
        ["a", "b", "c", "d"],
        {"a": DomainError("first reason"), "b": skip, "c": DomainError("second reason")},
    )
    skipped, skipped_uow = _run_reasons(tmp_path / "skipped", ["x", "y"], {"x": skip})
    clean, clean_uow = _run_reasons(tmp_path / "clean", ["v1", "v2"], {})
    outcomes = [
        (uow.transcripts.get_job(job.id).status, uow.transcripts.get_job(job.id).error_message)
        for job, uow in ((failed, failed_uow), (skipped, skipped_uow), (clean, clean_uow))
    ]
    assert outcomes == [
        (
            TranscriptStatus.Failed,
            "2 of 4 videos failed. Last: Couldn't get captions: second reason.",
        ),
        (
            TranscriptStatus.Done,
            "1 of 2 videos had no transcript. Last: No captions for this video.",
        ),
        (TranscriptStatus.Done, None),
    ]


def test_ac_115_7_each_skip_and_failure_logs_one_line(tmp_path: Path) -> None:
    from structlog.testing import capture_logs

    from avkit_core.domain.errors import DomainError, TranscriptRetryableError
    from avkit_core.domain.transcript import (
        TranscriptFailureCause,
        TranscriptSkip,
        failure_message,
    )

    cause = TranscriptFailureCause
    with capture_logs() as logs:
        job, _uow = _run_reasons(
            tmp_path,
            ["none", "broken", "blocked", "ok"],
            {
                "none": TranscriptSkip(cause.no_captions),
                "broken": DomainError("the video is age-restricted"),
                "blocked": TranscriptRetryableError("caption request blocked"),
            },
            max_retries=2,
        )
    lines = [
        entry
        for entry in logs
        if entry["event"]
        in {"transcript.item_skipped", "transcript.item_failed", "transcript.blocked"}
    ]
    assert [
        (
            entry["event"],
            entry["log_level"],
            entry.get("job_id"),
            entry.get("video_id"),
            entry.get("error"),
        )
        for entry in lines
    ] == [
        (
            "transcript.item_skipped",
            "warning",
            job.id,
            "none",
            failure_message(cause.no_captions),
        ),
        (
            "transcript.item_failed",
            "error",
            job.id,
            "broken",
            failure_message(cause.other, "the video is age-restricted"),
        ),
        (
            "transcript.blocked",
            "error",
            job.id,
            "blocked",
            failure_message(cause.blocked),
        ),
    ], logs
    assert lines[0].get("persist") is True
    assert sum(1 for entry in logs if entry.get("video_id") == "blocked") == 1, logs


# --- MEU-115 Console rider -------------------------------------------------------------------


def _health(tmp_path: Path, *, log_to_file: bool = False) -> HealthService:
    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    settings.set("app", "log_to_file", log_to_file)
    return HealthService(
        factory,
        app_data=tmp_path,
        settings=settings,
        media=FakeMedia(),
        youtube=FakeYouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
    )


def _messages(health: HealthService, prefix: str) -> list[str]:
    events = health.console_snapshot(0)
    return [event.message for event in events if event.message.startswith(prefix)]


def _console_lines(app_data: Path) -> list[dict[str, object]]:
    import json

    path = app_data / "logs" / "console.log"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_ac_115_9_console_fields_in_order_single_line_and_cut(tmp_path: Path) -> None:
    import structlog

    from avkit_core.services import health as health_module

    assert hasattr(health_module, "FIELD_LIMIT")
    assert health_module.FIELD_LIMIT == 300
    assert health_module.CONSOLE_FIELDS == (
        "job_id",
        "video_id",
        "variant_id",
        "device",
        "error",
        "detail",
        "request_id",
        "route",
    )
    health = _health(tmp_path)
    log = structlog.get_logger(module="fields")
    log.error(
        "probe.order",
        route="/r",
        request_id="q",
        detail="d",
        error="e",
        device="cpu",
        variant_id="var",
        video_id="vid",
        job_id="job",
        other="dropped",
    )
    log.error(
        "probe.shape",
        detail="first\r\n\nsecond\rthird https://example.invalid/a?b=c end",
        error="x" * 400,
    )
    assert _messages(health, "probe.order") == [
        "probe.order job_id=job video_id=vid variant_id=var device=cpu error=e detail=d "
        "request_id=q route=/r"
    ]
    assert _messages(health, "probe.shape") == [
        "probe.shape error=" + "x" * 300 + " detail=first second third [link] end"
    ]


def test_ac_115_10_secrets_reach_no_console_surface(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    import json
    import re

    import structlog

    ansi = re.compile(r"\x1b\[[0-9;]*m")
    rendered = re.compile(r"\S+ \S+ \[[a-z]+ *\] (?P<message>.*?) +seq=(?P<seq>\d+)")
    markers = (
        "SYNTHETIC_VIDEO_MARKER",
        "SYNTHETIC_COOKIE_MARKER",
        "SYNTHETIC_BEARER_MARKER",
        "SYNTHETIC_URL_MARKER",
        "SYNTHETIC_UNKEPT_MARKER",
        "SYNTHETIC_TRACE_MARKER",
    )
    health = _health(tmp_path, log_to_file=True)
    log = structlog.get_logger()
    log.error("probe.kept", video_id="vid-kept", detail="kept detail")
    assert _messages(health, "probe.kept") == ["probe.kept video_id=vid-kept detail=kept detail"]
    log.error(
        "probe.secret",
        video_id="avkit_token=SYNTHETIC_VIDEO_MARKER",
        error="cookie: SID=SYNTHETIC_COOKIE_MARKER",
        detail="Authorization: Bearer SYNTHETIC_BEARER_MARKER",
    )
    log.warning(
        "probe.url",
        detail="see https://example.invalid/caption?token=SYNTHETIC_URL_MARKER now",
        unkept="SYNTHETIC_UNKEPT_MARKER",
    )
    try:
        raise ValueError("SYNTHETIC_TRACE_MARKER")
    except ValueError:
        log.exception("probe.trace")
    ring = health.console_snapshot(0)
    stdout = capsys.readouterr().out
    filed = (tmp_path / "logs" / "console.log").read_text(encoding="utf-8")
    surfaces = {"ring": " ".join(event.message for event in ring), "stdout": stdout, "file": filed}
    leaks = {
        name: [item for item in (*markers, "Traceback") if item in text]
        for name, text in surfaces.items()
    }
    assert leaks == {"ring": [], "stdout": [], "file": []}
    safe = {(event.message, event.seq) for event in ring}
    for raw in stdout.splitlines():
        line = ansi.sub("", raw)
        if line.startswith("{"):
            assert set(json.loads(line)) == {"seq", "message", "module", "level"}, line
            continue
        match = rendered.fullmatch(line)
        assert match is not None, line
        assert (match["message"], int(match["seq"])) in safe, line


#: Each character case-folds to more than one character (D-296 review F2).
FOLDING_PREFIXES = {"sharp-s": "\u00df" * 64, "dotted-i": "\u0130" * 40, "ffi": "\ufb03" * 30}


@pytest.mark.parametrize("prefix", FOLDING_PREFIXES.values(), ids=FOLDING_PREFIXES.keys())
def test_ac_115_10_case_folding_prefix_still_redacts(prefix: str) -> None:
    from avkit_core.services.health import console_field, redact_message

    secret = prefix + " Bearer SYNTHETIC_FOLD_MARKER"
    assert redact_message(secret) == prefix + " [REDACTED]"
    assert redact_message(prefix + "BEARER") == prefix + " [REDACTED]"
    assert "SYNTHETIC" not in console_field(secret)


def test_ac_115_10_context_bound_values_reach_no_stdout_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    import re

    import structlog

    ansi = re.compile(r"\x1b\[[0-9;]*m")
    rendered = re.compile(r"\S+ \S+ \[[a-z]+ *\] (?P<message>.*?) +seq=(?P<seq>\d+)")
    health = _health(tmp_path, log_to_file=True)
    log = structlog.get_logger()
    structlog.contextvars.bind_contextvars(request_id="req-ctx")
    try:
        log.error("probe.context")
        structlog.contextvars.bind_contextvars(request_id="Bearer SYNTHETIC_CONTEXT_MARKER")
        log.error("probe.hostile")
    finally:
        structlog.contextvars.unbind_contextvars("request_id")
    assert _messages(health, "probe.") == [
        "probe.context request_id=req-ctx",
        "probe.hostile request_id=[REDACTED]",
    ]
    stdout = capsys.readouterr().out
    filed = (tmp_path / "logs" / "console.log").read_text(encoding="utf-8")
    assert [
        name for name, text in {"stdout": stdout, "file": filed}.items() if "SYNTHETIC" in text
    ] == []
    safe = {(event.message, event.seq) for event in health.console_snapshot(0)}
    for raw in stdout.splitlines():
        line = ansi.sub("", raw)
        if line.startswith("{"):
            continue
        match = rendered.fullmatch(line)
        assert match is not None, line
        assert (match["message"], int(match["seq"])) in safe, line


def test_ac_115_11_errors_and_flagged_lines_always_reach_the_file(tmp_path: Path) -> None:
    import structlog

    from avkit_core.services import health as health_module

    for name in ("PERSIST_LEVELS", "PERSIST_FIELD", "LEVEL_ALIASES"):
        assert hasattr(health_module, name), name
    assert health_module.PERSIST_LEVELS == ("ERROR", "CRITICAL")
    assert health_module.PERSIST_FIELD == "persist"
    assert dict(health_module.LEVEL_ALIASES) == {
        "exception": "ERROR",
        "fatal": "CRITICAL",
        "warn": "WARNING",
    }
    health = _health(tmp_path)
    log = structlog.get_logger(module="file")
    log.error("keep.error")
    try:
        raise ValueError("boom")
    except ValueError:
        log.exception("keep.exception")
    log.warning("keep.flagged", persist=True)
    log.warning("drop.warning")
    log.info("drop.info")
    assert [line["message"] for line in _console_lines(tmp_path)] == [
        "keep.error",
        "keep.exception",
        "keep.flagged",
    ]
    ring = health.console_snapshot(0)
    assert {event.message: event.level for event in ring}["keep.exception"] == "ERROR"
    assert [event.message for event in ring if "persist" in event.message] == []


def test_ac_115_12_append_failure_never_raises(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    import structlog

    health = _health(tmp_path, log_to_file=True)
    (tmp_path / "logs" / "console.log").mkdir(parents=True)
    log = structlog.get_logger(module="file")
    raised: OSError | None = None
    try:
        log.error("append.blocked")
    except OSError as exc:
        raised = exc
    assert raised is None
    assert _messages(health, "append.blocked") == ["append.blocked"]
    assert '"message": "append.blocked"' in capsys.readouterr().out


def test_ac_115_13_two_threads_both_reach_the_ring(tmp_path: Path) -> None:
    import threading

    import structlog

    health = _health(tmp_path)
    entered = threading.Event()
    release = threading.Event()

    class Blocker:
        def __str__(self) -> str:
            entered.set()
            release.wait(timeout=2)
            return "held"

    log = structlog.get_logger(module="threads")
    first = threading.Thread(target=lambda: log.info("thread.first", error=Blocker()))
    first.start()
    try:
        assert entered.wait(timeout=2)
        log.info("thread.second")
    finally:
        release.set()
        first.join(timeout=5)
    messages = {event.message for event in health.console_snapshot(0)}
    assert {"thread.first error=held", "thread.second"} <= messages, messages


# --- MEU-116 block stop and rate cap ----------------------------------------------------------


def _set_ids(yt: DownloadYouTube, ids: list[str]) -> None:
    yt.ids = list(ids)
    yt.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=list(ids))


def _join(service: object, timeout: float = 10) -> None:
    thread = service._thread  # type: ignore[attr-defined]
    if thread is not None:
        thread.join(timeout=timeout)


def _wait_until(predicate: Callable[[], bool], timeout: float = 5) -> bool:
    import time

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


def _require_clock() -> None:
    import inspect

    from avkit_core.services.transcript import TranscriptService

    assert "clock" in inspect.signature(TranscriptService).parameters


def _blocked_run(tmp_path: Path):
    service, settings, yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path)
    _set_ids(yt, ["first", "second"])
    settings.set("transcript", "max_retries", 3)
    captions.retryable_left = 10**6
    job = service.add_channel("https://youtube.com/@blocked")
    service.start_processing()
    _join(service)
    return service, uow, captions, job


def test_ac_116_1_exhausted_block_pauses_the_job(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
    from avkit_core.domain.transcript import TranscriptFailureCause, failure_message

    service, uow, captions, job = _blocked_run(tmp_path)
    blocked = failure_message(TranscriptFailureCause.blocked)
    calls = [video_id for video_id, _languages in captions.fetch_calls]
    parent = uow.transcripts.get_job(job.id)
    items = [
        (item.video_id, item.status, item.retry_count, item.error_message)
        for item in uow.transcripts.list_items(job.id)
    ]
    assert (calls.count("first"), calls.count("second")) == (3, 0)
    assert (parent.status, parent.error_message) == (TranscriptStatus.Paused, blocked)
    assert items == [
        ("first", TranscriptItemStatus.Pending, 0, blocked),
        ("second", TranscriptItemStatus.Pending, 0, None),
    ]
    assert service.get_processor_state().state is QueueProcessorState.Paused


def test_ac_116_2_resume_after_a_block_finishes_the_job(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus

    service, uow, captions, job = _blocked_run(tmp_path)
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Paused
    captions.retryable_left = 0
    service.resume_processing()
    _join(service)
    parent = uow.transcripts.get_job(job.id)
    assert (parent.status, parent.error_message) == (TranscriptStatus.Done, None)
    assert [(item.status, item.error_message) for item in uow.transcripts.list_items(job.id)] == [
        (TranscriptItemStatus.Done, None),
        (TranscriptItemStatus.Done, None),
    ]


def test_ac_116_3_other_failure_fails_the_video_and_the_run_goes_on(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus
    from avkit_core.domain.errors import DomainError

    job, uow = _run_reasons(
        tmp_path, ["bad", "next"], {"bad": DomainError("the video is age-restricted")}
    )
    items = {item.video_id: item.status for item in uow.transcripts.list_items(job.id)}
    assert items == {"bad": TranscriptItemStatus.Failed, "next": TranscriptItemStatus.Done}


def _capped(tmp_path: Path, ids: list[str], cap: float):
    clock = FakeClock()
    service, settings, yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path, clock=clock)
    _set_ids(yt, ids)
    settings.set("transcript", "delay_between_requests", 0)
    settings.set("transcript", "batch_size", 0)
    settings.set("transcript", "requests_per_hour", cap)
    return service, settings, uow, captions, clock


def _run_capped(service: object) -> object:
    job = service.add_channel("https://youtube.com/@capped")  # type: ignore[attr-defined]
    service.start_processing()  # type: ignore[attr-defined]
    _join(service)
    return job


def test_ac_116_4_third_request_waits_until_the_first_is_an_hour_old(tmp_path: Path) -> None:
    _require_clock()
    service, _settings, _uow, captions, _clock = _capped(tmp_path, ["a", "b", "c"], 2)
    _run_capped(service)
    assert captions.starts == [0.0, 0.0, 3600.0]


def test_ac_116_4_a_retry_counts_as_a_request(tmp_path: Path) -> None:
    _require_clock()
    service, settings, _uow, captions, _clock = _capped(tmp_path, ["a", "b"], 2)
    settings.set("transcript", "max_retries", 3)
    settings.set("transcript", "retry_delay", 5)
    captions.retryable_left = 1
    _run_capped(service)
    assert captions.starts == [0.0, 5.0, 3600.0]


def test_ac_116_4_a_cap_of_zero_never_waits(tmp_path: Path) -> None:
    _require_clock()
    service, _settings, _uow, captions, clock = _capped(tmp_path, ["a", "b", "c"], 0)
    _run_capped(service)
    assert (captions.starts, max(clock.sleeps, default=0.0)) == ([0.0, 0.0, 0.0], 0.0)


def test_ac_116_4_a_lowered_cap_is_read_for_the_next_request(tmp_path: Path) -> None:
    _require_clock()
    service, settings, _uow, captions, _clock = _capped(tmp_path, ["a", "b"], 300)
    captions.on_call = lambda _count: settings.set("transcript", "requests_per_hour", 1)
    _run_capped(service)
    assert captions.starts == [0.0, 3600.0]


@pytest.mark.parametrize(
    ("action", "status"),
    [("pause_processing", "Paused"), ("stop_processing", "Cancelled")],
    ids=["pause", "stop"],
)
def test_ac_116_4_stop_or_pause_ends_a_cap_wait(tmp_path: Path, action: str, status: str) -> None:
    _require_clock()
    service, _settings, uow, captions, clock = _capped(tmp_path, ["a", "b"], 1)
    fired: list[float] = []

    def at_100(now: float) -> None:
        if now >= 100 and not fired:
            fired.append(now)
            getattr(service, action)()

    clock.on_sleep = at_100
    job = _run_capped(service)
    calls = [video_id for video_id, _languages in captions.fetch_calls]
    parent = uow.transcripts.get_job(job.id)  # type: ignore[attr-defined]
    assert (fired, calls, parent.status.value) == ([100.0], ["a"], status)
    assert clock.now <= fired[0] + 1.0


@pytest.mark.parametrize("raised", [5, 0])
def test_ac_116_4_a_raised_or_cleared_cap_ends_the_wait(tmp_path: Path, raised: int) -> None:
    _require_clock()
    service, settings, _uow, captions, clock = _capped(tmp_path, ["a", "b"], 1)
    fired: list[float] = []

    def at_100(now: float) -> None:
        if now >= 100 and not fired:
            fired.append(now)
            settings.set("transcript", "requests_per_hour", raised)

    clock.on_sleep = at_100
    _run_capped(service)
    assert captions.starts == [0.0, 100.0]


def _four_hundred(tmp_path: Path, *, retries: int):
    from avkit_core.domain.enums import TranscriptStatus

    clock = FakeClock()
    service, _settings, yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path, clock=clock)
    _set_ids(yt, [f"v{index}" for index in range(400)])
    captions.retryable_left = retries
    job = service.add_channel("https://youtube.com/@four-hundred")
    service.start_processing()
    _join(service, timeout=120)
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Done
    return captions, clock


def test_ac_116_5_default_cap_delays_nothing_without_retries(tmp_path: Path) -> None:
    captions, clock = _four_hundred(tmp_path, retries=0)
    assert len(captions.fetch_calls) == 400
    assert set(clock.sleeps) <= {0.0, 6.0, 300.0}, sorted(set(clock.sleeps))


def test_ac_116_9_a_retry_makes_the_default_cap_wait(tmp_path: Path) -> None:
    _require_clock()
    captions, _clock = _four_hundred(tmp_path, retries=1)
    starts = captions.starts
    assert len(starts) == 401
    assert starts[300] == pytest.approx(3600.0)
    busiest = max(sum(1 for start in starts if end - 3600 < start <= end) for end in starts)
    assert busiest <= 300


def _race_stack(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    sleep: Callable[[float], None] | None = None,
):
    import threading

    service, settings, yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path, sleep=sleep)
    _set_ids(yt, ["first", "second"])
    settings.set("transcript", "max_retries", 1)
    captions.retryable_left = 10**6
    workers = {"active": 0, "most": 0}
    guard = threading.Lock()
    original = service._worker

    def counted() -> None:
        with guard:
            workers["active"] += 1
            workers["most"] = max(workers["most"], workers["active"])
        try:
            original()
        finally:
            with guard:
                workers["active"] -= 1

    monkeypatch.setattr(service, "_worker", counted)
    return service, uow, captions, workers


def _assert_race_finished(
    service: object, uow: FakeUnitOfWork, job_id: str, workers: dict[str, int]
) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus

    def finished() -> bool:
        state = service.get_processor_state().state  # type: ignore[attr-defined]
        return state is QueueProcessorState.Idle and workers["active"] == 0

    _wait_until(finished)
    parent = uow.transcripts.get_job(job_id)
    assert (
        parent.status,
        [item.status for item in uow.transcripts.list_items(job_id)],
        service.get_processor_state().state,  # type: ignore[attr-defined]
        workers["most"],
    ) == (
        TranscriptStatus.Done,
        [TranscriptItemStatus.Done, TranscriptItemStatus.Done],
        QueueProcessorState.Idle,
        1,
    )


def test_ac_116_8_resume_while_the_worker_publishes_the_pause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import threading

    from avkit_core.domain.enums import TranscriptStatus

    service, uow, captions, workers = _race_stack(tmp_path, monkeypatch)
    published = threading.Event()
    release = threading.Event()
    original = service._pause_parent

    def held(*args: object, **kwargs: object) -> None:
        original(*args, **kwargs)
        published.set()
        release.wait(timeout=5)

    monkeypatch.setattr(service, "_pause_parent", held)
    job = service.add_channel("https://youtube.com/@race-a")
    try:
        service.start_processing()
        assert published.wait(timeout=2)
        assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Paused
        service.resume_processing()
        captions.retryable_left = 0
    finally:
        release.set()
    _assert_race_finished(service, uow, job.id, workers)


def test_ac_116_8_resume_while_the_worker_sleeps_after_the_job(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import threading

    from avkit_core.domain.enums import TranscriptStatus

    held = threading.Event()
    release = threading.Event()

    def sleep(seconds: float) -> None:
        if seconds == 0 and not held.is_set():
            held.set()
            release.wait(timeout=5)

    service, uow, captions, workers = _race_stack(tmp_path, monkeypatch, sleep=sleep)
    job = service.add_channel("https://youtube.com/@race-b")
    try:
        service.start_processing()
        assert held.wait(timeout=2)
        assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Paused
        service.resume_processing()
        captions.retryable_left = 0
    finally:
        release.set()
    _assert_race_finished(service, uow, job.id, workers)


# --- AC-117.6 / 117.7 MODEL_REFUSAL (Session 51, MEU-117) ------------------------------------


def test_ac_117_6_download_refuses_a_variant_this_build_cannot_run(tmp_path: Path) -> None:
    from structlog.testing import capture_logs

    from avkit_core.domain.enums import ModelFormat
    from avkit_core.domain.tts import MODEL_REASONS

    _service, models, tts_port, catalog, _fs, _media, _uow = _tts_stack(tmp_path)
    reason = MODEL_REASONS[ModelFormat.PyTorch]
    tts_port.absent = {ModelFormat.PyTorch}
    with capture_logs() as logs, pytest.raises(ConflictError) as raised:
        models.download("kokoro-pt-fp32")
    assert str(raised.value) == reason
    assert models.get_download_runtime().state == "Idle"
    assert models._thread is None
    assert not catalog.entered.is_set()
    assert [
        (entry["log_level"], entry.get("variant_id"), entry.get("detail"))
        for entry in logs
        if entry["event"] == "model.download_refused"
    ] == [("warning", "kokoro-pt-fp32", reason)]
    with pytest.raises(NotFoundError):
        models.download("kokoro-missing")

    # With the runtime present the download starts as today, and while it runs the in-flight
    # 409 comes before the build check.
    tts_port.absent = set()
    catalog.hold = True
    assert models.download("kokoro-pt-fp32").id == "kokoro-pt-fp32"
    assert models.get_download_runtime().state == "Downloading"
    assert catalog.entered.wait(timeout=2)
    tts_port.absent = {ModelFormat.PyTorch}
    try:
        with capture_logs() as busy_logs, pytest.raises(ConflictError) as busy:
            models.download("kokoro-pt-fp32")
    finally:
        catalog.release.set()
        if models._thread is not None:
            models._thread.join(timeout=2)
    assert str(busy.value) == "a model download is already in progress"
    assert [entry for entry in busy_logs if entry["event"] == "model.download_refused"] == []
    assert models.get_download_runtime().state == "Idle"


def test_ac_117_7_load_refuses_a_variant_this_build_cannot_run_first(tmp_path: Path) -> None:
    from structlog.testing import capture_logs

    from avkit_core.domain.enums import DeviceType, ModelFormat
    from avkit_core.domain.errors import DomainError
    from avkit_core.domain.tts import LEGACY_ONNX_DIR, MODEL_REASONS, AssetState, TtsAsset

    _service, models, tts_port, _catalog, _fs, _media, uow = _tts_stack(tmp_path)
    models_dir = tmp_path / "models"
    uow.models.mark_downloaded("kokoro-pt-fp32", models_dir / "kokoro-v1_0.pth")
    # A v0.19 path, so the ONNX row would meet the legacy 409 if the build check came later.
    _seed_onnx_row(uow, models_dir / LEGACY_ONNX_DIR / "model_quantized.onnx", downloaded=True)
    assets = models._assets
    assets.states[TtsAsset.ONNX_VOCAB] = AssetState.MISSING
    assets.states[TtsAsset.SPACY_MODEL] = AssetState.MISSING
    tts_port.absent = {ModelFormat.PyTorch, ModelFormat.ONNX}
    refused: list[tuple[str, DomainError]] = []
    with capture_logs() as logs:
        for variant_id in ("kokoro-pt-fp32", "kokoro-onnx-int8"):
            with pytest.raises(DomainError) as raised:
                models.load(variant_id, DeviceType.CPU)
            refused.append((variant_id, raised.value))
    assert [(variant_id, type(error).__name__, str(error)) for variant_id, error in refused] == [
        ("kokoro-pt-fp32", "ModelLoadError", MODEL_REASONS[ModelFormat.PyTorch]),
        ("kokoro-onnx-int8", "ModelLoadError", MODEL_REASONS[ModelFormat.ONNX]),
    ]
    assert tts_port.load_calls == []
    assert assets.downloads == []
    assert models.get_download_runtime().state == "Idle"
    assert [
        (entry["log_level"], entry.get("variant_id"), entry.get("detail"))
        for entry in logs
        if entry["event"] == "model.load_refused"
    ] == [
        ("warning", "kokoro-pt-fp32", MODEL_REASONS[ModelFormat.PyTorch]),
        ("warning", "kokoro-onnx-int8", MODEL_REASONS[ModelFormat.ONNX]),
    ]
    with pytest.raises(NotFoundError):
        models.load("kokoro-missing", DeviceType.CPU)

    tts_port.absent = set()
    assets.states[TtsAsset.ONNX_VOCAB] = AssetState.READY
    assets.states[TtsAsset.SPACY_MODEL] = AssetState.READY
    models.load("kokoro-pt-fp32", DeviceType.CPU)
    assert [variant.id for variant, _device in tts_port.load_calls] == ["kokoro-pt-fp32"]


# --- AC-119.10 HOME_SCRUB (Session 52, MEU-119, D-335) ---------------------------------------

#: A synthetic home folder; no test reads the real one.
SYNTHETIC_HOME = "C:\\Users\\SYNTHETIC_HOME_USER"


def _scrub_ready(monkeypatch: pytest.MonkeyPatch, home: str, *, ignore_case: bool) -> None:
    """Asserts the scrub's names exist, so a missing one fails by assertion, then patches them."""
    from avkit_core.services import health as health_module

    assert hasattr(health_module, "home_folder")
    assert hasattr(health_module, "scrub_home")
    assert hasattr(health_module, "HOME_IGNORES_CASE")
    monkeypatch.setattr(health_module, "home_folder", lambda: home)
    monkeypatch.setattr(health_module, "HOME_IGNORES_CASE", ignore_case)


def test_ac_119_10_home_folder_becomes_tilde(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_core.services.health import console_field

    _scrub_ready(monkeypatch, SYNTHETIC_HOME, ignore_case=True)
    assert [
        console_field(text)
        for text in (
            "at C:\\Users\\SYNTHETIC_HOME_USER\\.avkit\\models\\m.onnx",
            "at C:/Users/SYNTHETIC_HOME_USER/.avkit/models/m.onnx",
            "at 'C:\\\\Users\\\\SYNTHETIC_HOME_USER\\\\.avkit\\\\models\\\\m.onnx'",
            "home is C:\\Users\\SYNTHETIC_HOME_USER",
            'quoted "C:\\Users\\SYNTHETIC_HOME_USER"',
        )
    ] == [
        "at ~\\.avkit\\models\\m.onnx",
        "at ~/.avkit/models/m.onnx",
        "at '~\\\\.avkit\\\\models\\\\m.onnx'",
        "home is ~",
        'quoted "~"',
    ]


def test_ac_119_10_case_follows_home_ignores_case(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_core.services.health import console_field

    folded = "at c:\\users\\synthetic_home_user\\f"
    _scrub_ready(monkeypatch, SYNTHETIC_HOME, ignore_case=True)
    assert console_field(folded) == "at ~\\f"
    _scrub_ready(monkeypatch, SYNTHETIC_HOME, ignore_case=False)
    assert console_field(folded) == folded
    assert console_field("at C:\\Users\\SYNTHETIC_HOME_USER\\f") == "at ~\\f"


def test_ac_119_10_other_paths_stay(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_core.services.health import console_field

    _scrub_ready(monkeypatch, SYNTHETIC_HOME, ignore_case=True)
    kept = (
        "at C:\\Users\\SYNTHETIC_HOME_USER2\\x",
        "at C:\\Users\\Public\\f",
        "at E:\\mirror\\C:\\Users\\SYNTHETIC_HOME_USER\\f",
        "at backupC:\\Users\\SYNTHETIC_HOME_USER\\f",
    )
    assert [console_field(text) for text in kept] == list(kept)


def test_ac_119_10_cut_keeps_no_part_of_the_user_name(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_core.services.health import FIELD_LIMIT, console_field

    _scrub_ready(monkeypatch, SYNTHETIC_HOME, ignore_case=True)
    prefix = "p" * 289 + " "
    assert len(prefix) == 290
    # Cut first, this keeps "C:\Users\S": the scrub runs before the cut.
    field = console_field(prefix + "C:\\Users\\SYNTHETIC_HOME_USER\\f")
    assert field == prefix + "~\\f"
    assert len(field) <= FIELD_LIMIT


@pytest.mark.parametrize(
    "home", ["C:", "C:\\", "\\", "/", ""], ids=["drive", "drive-sep", "bs", "slash", "empty"]
)
def test_ac_119_10_bare_drive_or_empty_home_changes_nothing(
    monkeypatch: pytest.MonkeyPatch, home: str
) -> None:
    from avkit_core.services import health as health_module

    _scrub_ready(monkeypatch, home, ignore_case=True)
    text = "at C:\\Users\\x\\f and /home/x/f"
    assert (health_module.scrub_home(text), health_module.console_field(text)) == (text, text)


def test_ac_119_10_home_folder_reaches_no_console_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import json
    import re

    import structlog

    _scrub_ready(monkeypatch, SYNTHETIC_HOME, ignore_case=True)
    health = _health(tmp_path, log_to_file=True)
    path = SYNTHETIC_HOME + "\\.avkit\\models\\m.onnx"
    missing = FileNotFoundError(path)
    unreadable = OSError(2, "No such file or directory", path)
    structlog.get_logger().error("probe.home", error=str(unreadable), detail=str(missing))
    assert _messages(health, "probe.home") == [
        "probe.home error=[Errno 2] No such file or directory: '~\\\\.avkit\\\\models\\\\m.onnx' "
        "detail=~\\.avkit\\models\\m.onnx"
    ]
    ring = " ".join(event.message for event in health.console_snapshot(0))
    stdout = re.sub(r"\x1b\[[0-9;]*m", "", capsys.readouterr().out)
    # Stdout carries each Console line as JSON, so its backslashes are doubled there.
    printed = " ".join(
        str(json.loads(line).get("message")) for line in stdout.splitlines() if line.startswith("{")
    )
    filed = " ".join(str(line.get("message")) for line in _console_lines(tmp_path))
    raw = {"ring": ring, "stdout": stdout, "file": filed}
    assert {name: "SYNTHETIC_HOME_USER" in text for name, text in raw.items()} == {
        "ring": False,
        "stdout": False,
        "file": False,
    }
    surfaces = {"ring": ring, "stdout": printed, "file": filed}
    assert {name: "~\\.avkit\\models\\m.onnx" in text for name, text in surfaces.items()} == {
        "ring": True,
        "stdout": True,
        "file": True,
    }


def _run_download_queue(service: DownloadService) -> None:
    service.start_processing()
    thread = service._thread
    assert thread is not None
    thread.join(timeout=2)
    assert not thread.is_alive()


def test_ac_124_2_done_stores_the_received_height() -> None:
    service, _settings, youtube, uow = _download_stack()
    youtube.download_result = replace(youtube.download_result, height=360)
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    _run_download_queue(service)
    done = uow.downloads.list_ordered()[0]
    assert done.status is DownloadStatus.Done
    assert done.received_height == 360


def test_ac_124_3_unknown_height_stays_none() -> None:
    service, _settings, youtube, uow = _download_stack()
    youtube.download_result = replace(youtube.download_result, height=None)
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    _run_download_queue(service)
    done = uow.downloads.list_ordered()[0]
    assert done.status is DownloadStatus.Done
    assert done.received_height is None


def test_ac_124_4_audio_only_stores_no_height() -> None:
    service, _settings, youtube, uow = _download_stack()
    youtube.download_result = replace(youtube.download_result, height=480)
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, True, AudioFormat.Default)
    _run_download_queue(service)
    done = uow.downloads.list_ordered()[0]
    assert done.audio_only is True
    assert done.status is DownloadStatus.Done
    assert done.received_height is None


def test_ac_124_16_list_items_download_their_own_video() -> None:
    service, _settings, youtube, uow = _download_stack()
    service.add_to_queue("https://youtu.be/vid1", QualityPreset.P1080, False, AudioFormat.Default)
    youtube.playlist = PlaylistInfo(playlist_id="pl", title="P", video_ids=["a", "b"])
    service.add_to_queue("https://youtube.com/pl", QualityPreset.P1080, False, AudioFormat.Default)
    assert [job.url for job in uow.downloads.list_ordered()] == [
        "https://youtu.be/vid1",
        "https://www.youtube.com/watch?v=a",
        "https://www.youtube.com/watch?v=b",
    ]
    _run_download_queue(service)
    jobs = uow.downloads.list_ordered()
    assert youtube.download_urls == [job.url for job in jobs]
    assert [job.status for job in jobs] == [DownloadStatus.Done] * 3
