"""Real SQLite-backed download/conversion stack for the MEU-42 re-queue ACs.

The Phase 4 REST fakes never reach a repository, so a *persisted-state*
invariant (`BLOCKER_REASON_INVARIANT`) cannot be observed through them. This
module builds the production `DownloadService` / `ConversionService` over a
real temp SQLite file and swaps them into the shared fake bundle, so a
`TestClient` call travels route -> service -> domain -> repository for real.
Only the network-facing ports (`YouTubePort`, `ExtractCoordinator`,
`MediaPort`) are stubbed; nothing under test is faked.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from tests.e2e.api_fakes import TOKENS, make_bundle

from avkit_api.main import create_app
from avkit_api.wiring import AppServices
from avkit_core.domain.conversion import ConversionJob
from avkit_core.domain.download import DownloadJob, SABRStatus, VideoInfo
from avkit_core.domain.enums import (
    AudioFormat,
    ConversionKind,
    ConversionPresetId,
    ConversionStatus,
    DownloadStatus,
    QualityPreset,
    SABRMode,
)
from avkit_core.services.conversion import ConversionService
from avkit_core.services.download import DownloadService
from avkit_core.services.settings import SettingsService
from avkit_infra.database.engine import (
    create_session_factory,
    create_sqlite_engine,
    init_schema,
)
from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork


class StubYouTube:
    """Only the SABR probe is reachable from the re-queue paths under test."""

    def __init__(self, mode: SABRMode = SABRMode.Inactive) -> None:
        self.mode = mode

    def check_sabr_status(self) -> SABRStatus:
        return SABRStatus(mode=self.mode, source=None, checked_at=datetime.now(UTC))


class StubCoordinator:
    """Return a fixed `VideoInfo` instead of calling yt-dlp."""

    def __init__(self, video_id: str = "dQw4w9wgGc", title: str = "Example") -> None:
        self.video_id = video_id
        self.title = title
        self.calls: list[str] = []

    def extract_info(self, url: str) -> VideoInfo:
        self.calls.append(url)
        return VideoInfo(video_id=self.video_id, title=self.title, duration=1.0, formats=[])


class StubMedia:
    """FFmpeg is never invoked by the re-queue paths; probe/detect stay inert."""

    def is_available(self) -> bool:
        return True

    def ffmpeg_version(self) -> str:
        return "6.0"


class RealStack:
    """Production download/conversion services over a real temp SQLite file."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.engine = create_sqlite_engine(db_path)
        init_schema(self.engine)
        session_factory = create_session_factory(self.engine)

        def _make_uow() -> SqlAlchemyUnitOfWork:
            return SqlAlchemyUnitOfWork(session_factory)

        self.uow_factory: Callable[[], SqlAlchemyUnitOfWork] = _make_uow
        self.settings = SettingsService(self.uow_factory)
        self.youtube = StubYouTube()
        self.coordinator = StubCoordinator()
        self.download = DownloadService(
            self.uow_factory,
            youtube=self.youtube,
            coordinator=self.coordinator,
            settings=self.settings,
        )
        self.conversion = ConversionService(
            self.uow_factory,
            media=StubMedia(),
            settings=self.settings,
        )
        base, _trx, _tts, _models = make_bundle()
        self.services: AppServices = replace(
            base,
            download=self.download,
            conversion=self.conversion,
        )
        self.app = create_app(tokens=TOKENS, services=self.services, engine_dispose=None)
        self.client = TestClient(self.app)

    def close(self) -> None:
        self.client.close()
        self.engine.dispose()

    # -- seeding ---------------------------------------------------------
    def seed_download(self, status: DownloadStatus, **overrides: object) -> DownloadJob:
        """Persist a download row directly, bypassing every service path."""
        payload: dict[str, object] = {
            "id": str(uuid4()),
            "url": "https://youtu.be/dQw4w9wgGc",
            "video_id": uuid4().hex[:11],
            "title": "Example",
            "quality": QualityPreset.P1080,
            "audio_only": False,
            "audio_format": AudioFormat.Default,
            "status": status,
            "progress": 0.5,
            "speed_bps": None,
            "eta_seconds": None,
            "file_size": None,
            "file_path": None,
            "error_message": None,
            "queue_position": 0,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        payload.update(overrides)
        job = DownloadJob(**payload)
        with self.uow_factory() as uow:
            uow.downloads.add(job)
            uow.commit()
        return job

    def seed_conversion(self, status: ConversionStatus, **overrides: object) -> ConversionJob:
        """Persist a conversion row directly, bypassing every service path."""
        payload: dict[str, object] = {
            "id": str(uuid4()),
            "kind": ConversionKind.Compress,
            "input_path": Path("C:/in/a.mp4"),
            "output_path": Path("C:/out/a_compress.mp4"),
            "display_name": "a.mp4",
            "preset_id": ConversionPresetId.Balanced,
            "cq": 25,
            "scale_height": None,
            "audio_mode": None,
            "gpu_encoder": None,
            "in_ms": None,
            "out_ms": None,
            "copy_mode": None,
            "stream_index": None,
            "status": status,
            "progress": 0.5,
            "speed_bps": None,
            "eta_seconds": None,
            "file_size": None,
            "duration_seconds": None,
            "width": None,
            "height": None,
            "error_message": None,
            "queue_position": 0,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        payload.update(overrides)
        job = ConversionJob(**payload)
        with self.uow_factory() as uow:
            uow.conversion_jobs.add(job)
            uow.commit()
        return job

    def insert_legacy_row(
        self,
        *,
        status: DownloadStatus,
        error_message: str | None = None,
        quality: QualityPreset = QualityPreset.P1080,
    ) -> str:
        """Insert a download row with Core SQL, bypassing the repository entirely.

        This is the only way to produce the *legacy* on-disk shape (a blocked row
        with no reason) once the repository normalizes at its own boundary.
        """
        from avkit_infra.database.models import DownloadJobRow

        job_id = str(uuid4())
        now = datetime.now(UTC)
        with self.engine.begin() as connection:
            connection.execute(
                DownloadJobRow.__table__.insert().values(
                    id=job_id,
                    url="https://youtu.be/dQw4w9wgGc",
                    video_id=uuid4().hex[:11],
                    title="Legacy",
                    quality=quality.name,
                    audio_only=False,
                    audio_format=AudioFormat.Default.name,
                    status=status.name,
                    progress=0.0,
                    speed_bps=None,
                    eta_seconds=None,
                    file_size=None,
                    file_path=None,
                    error_message=error_message,
                    queue_position=0,
                    created_at=now,
                    updated_at=now,
                )
            )
        return job_id

    # -- reads -----------------------------------------------------------
    def read_download(self, job_id: str) -> DownloadJob:
        with self.uow_factory() as uow:
            job = uow.downloads.get(job_id)
        if job is None:
            raise AssertionError(f"download row {job_id} vanished")
        return job

    def read_conversion(self, job_id: str) -> ConversionJob:
        with self.uow_factory() as uow:
            job = uow.conversion_jobs.get(job_id)
        if job is None:
            raise AssertionError(f"conversion row {job_id} vanished")
        return job

    def listed_download(self, job_id: str, auth: dict[str, str]) -> dict[str, object]:
        """Return the `GET /downloads` payload for one job, as the card sees it."""
        response = self.client.get("/api/v1/downloads", headers=auth)
        if response.status_code != 200:
            raise AssertionError(f"GET /downloads returned {response.status_code}")
        for item in response.json()["items"]:
            if item["id"] == job_id:
                return dict(item)
        raise AssertionError(f"job {job_id} missing from GET /downloads")


@contextmanager
def real_stack(db_path: Path) -> Iterator[RealStack]:
    """Yield a `RealStack` and dispose its engine on exit."""
    stack = RealStack(db_path)
    try:
        yield stack
    finally:
        stack.close()
