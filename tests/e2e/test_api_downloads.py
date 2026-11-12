"""MEU-15 download / SABR / cookie / formatter tests (AC-15.1–15.9)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from avkit_api.formatters import format_eta, format_iso, format_speed
from avkit_api.main import create_app
from avkit_api.wiring import AppServices
from avkit_core.domain.download import CookieTestResult, DownloadJob, SABRStatus
from avkit_core.domain.enums import (
    AudioFormat,
    DownloadStatus,
    QualityPreset,
    QueueProcessorState,
    SABRMode,
    SABRSource,
)
from avkit_core.domain.errors import ConflictError, CookieTestError, NotFoundError
from avkit_core.domain.queue import QueueRuntime

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}


class _Lifecycle:
    def recover_stale_processing(self) -> None:
        return None

    def stop_processing(self) -> None:
        return None

    def unload(self) -> None:
        return None

    def cancel_processing(self) -> None:
        return None

    def liveness(self) -> SimpleNamespace:
        return SimpleNamespace(ok=True)

    def dependencies(self) -> SimpleNamespace:
        return SimpleNamespace(ffmpeg_version="6.0", ytdlp_version="2024.12")


class FakeDownload(_Lifecycle):
    def __init__(self) -> None:
        self.jobs: list[DownloadJob] = []
        self.runtime = QueueRuntime("downloads", QueueProcessorState.Idle, None)
        self.sabr = SABRStatus(SABRMode.Inactive, None, None)
        self.start_calls = 0
        self.pause_calls = 0
        self.resume_calls = 0
        self.cancel_calls = 0
        self.check_calls = 0
        self.clear_queue_calls = 0
        self.archive_cleared = False
        self.cookie_error: CookieTestError | None = None
        self.last_cookie: tuple[object, ...] | None = None
        self.apply_updated = 2
        self.last_reorder: list[str] = []

    def get_queue(self) -> list[DownloadJob]:
        return list(self.jobs)

    def get_job(self, job_id: str) -> DownloadJob:
        for job in self.jobs:
            if job.id == job_id:
                return job
        raise NotFoundError(f"download job {job_id} not found")

    def get_processor_state(self) -> QueueRuntime:
        return self.runtime

    def get_sabr_status(self) -> SABRStatus:
        return self.sabr

    def add_to_queue(
        self,
        url: str,
        quality: QualityPreset,
        audio_only: bool,
        audio_format: AudioFormat,
    ) -> list[DownloadJob]:
        now = datetime(2026, 1, 2, 3, 4, 5)
        job = DownloadJob(
            id=str(uuid4()),
            url=url,
            video_id="vid1",
            title="One",
            quality=quality,
            audio_only=audio_only,
            audio_format=audio_format,
            status=DownloadStatus.Pending,
            progress=0.0,
            speed_bps=12300000.0,
            eta_seconds=125,
            file_size=1,
            file_path=None,
            error_message=None,
            queue_position=0,
            created_at=now,
            updated_at=now,
        )
        self.jobs.append(job)
        return [job]

    def start_processing(self) -> None:
        self.start_calls += 1

    def pause_processing(self) -> None:
        self.pause_calls += 1

    def resume_processing(self) -> None:
        self.resume_calls += 1
        if self.runtime.state is not QueueProcessorState.Paused:
            raise ConflictError("resume_processing requires Paused")

    def cancel_processing(self) -> None:
        self.cancel_calls += 1

    def remove_from_queue(self, job_id: str) -> None:
        self.get_job(job_id)
        self.jobs = [job for job in self.jobs if job.id != job_id]

    def clear_queue(self) -> None:
        self.clear_queue_calls += 1
        self.jobs = []

    def reorder_queue(self, job_ids: list[str]) -> None:
        by_id = {job.id: job for job in self.jobs}
        self.jobs = [by_id[job_id] for job_id in job_ids if job_id in by_id]
        self.last_reorder = list(job_ids)

    def reset_failed(self, job_id: str) -> DownloadJob:
        job = self.get_job(job_id)
        if job.status is not DownloadStatus.Failed:
            raise ConflictError("reset requires Failed")
        return job

    def check_sabr(self) -> SABRStatus:
        self.check_calls += 1
        self.sabr = SABRStatus(SABRMode.Active, SABRSource.Detected, datetime.now(UTC))
        return self.sabr

    def force_sabr(self) -> SABRStatus:
        self.sabr = SABRStatus(SABRMode.Active, SABRSource.Forced, datetime.now(UTC))
        return self.sabr

    def clear_sabr(self) -> SABRStatus:
        self.sabr = SABRStatus(SABRMode.Inactive, None, datetime.now(UTC))
        return self.sabr

    def apply_defaults_to_pending(self) -> int:
        return self.apply_updated

    def test_cookies(
        self,
        mode: str,
        browser: str | None,
        profile: str | None,
        cookie_file: Path | None,
    ) -> CookieTestResult:
        self.last_cookie = (mode, browser, profile, cookie_file)
        if self.cookie_error is not None:
            raise self.cookie_error
        return CookieTestResult(ok=True, error_message=None)


def _app(download: FakeDownload | None = None) -> tuple[TestClient, FakeDownload]:
    fake = download or FakeDownload()
    life = _Lifecycle()
    services = AppServices(
        download=fake,
        transcript=life,
        tts=life,
        models=life,
        settings=life,
        health=life,
        conversion=life,
        capture=life,
    )
    app = create_app(tokens=TOKENS, services=services, engine_dispose=None)
    return TestClient(app), fake


def test_ac_15_1_create_download_round_trip_and_boundary() -> None:
    client, _fake = _app()
    created = client.post(
        "/api/v1/downloads",
        headers=AUTH,
        json={"url": "https://youtu.be/aaaaaaaaaaa", "quality": "1080p"},
    )
    extra = client.post(
        "/api/v1/downloads",
        headers=AUTH,
        json={"url": "https://youtu.be/aaaaaaaaaaa", "quality": "1080p", "nope": 1},
    )
    missing = client.post(
        "/api/v1/downloads",
        json={"url": "https://youtu.be/aaaaaaaaaaa", "quality": "1080p"},
    )
    assert created.status_code == 201
    body = created.json()
    assert "items" in body
    assert body["items"][0]["quality"] == "1080p"
    assert extra.status_code == 422
    assert "error" in extra.json()
    assert missing.status_code == 401


def test_ac_15_2_list_envelope_has_no_paused_status() -> None:
    client, fake = _app()
    client.post(
        "/api/v1/downloads",
        headers=AUTH,
        json={"url": "https://youtu.be/aaaaaaaaaaa", "quality": "720p"},
    )
    listed = client.get("/api/v1/downloads", headers=AUTH)
    assert listed.status_code == 200
    payload = listed.json()
    assert set(payload) == {"items", "processor"}
    assert payload["processor"]["state"] == "Idle"
    assert all(item["status"] != "Paused" for item in payload["items"])
    assert fake.jobs[0].status is DownloadStatus.Pending


def test_ac_15_3_start_if_processing_does_not_call_start() -> None:
    fake = FakeDownload()
    fake.runtime = QueueRuntime("downloads", QueueProcessorState.Processing, None)
    client, _ = _app(fake)
    response = client.post("/api/v1/downloads/start", headers=AUTH)
    assert response.status_code == 409
    assert "error" in response.json()
    assert fake.start_calls == 0


def test_ac_15_4_pause_resume_cancel_stop() -> None:
    client, fake = _app()
    assert client.post("/api/v1/downloads/pause", headers=AUTH).status_code == 202
    assert client.post("/api/v1/downloads/cancel", headers=AUTH).status_code == 202
    assert client.post("/api/v1/downloads/stop", headers=AUTH).status_code == 202
    assert fake.pause_calls == 1
    assert fake.cancel_calls == 2
    resume_conflict = client.post("/api/v1/downloads/resume", headers=AUTH)
    assert resume_conflict.status_code == 409
    fake.runtime = QueueRuntime("downloads", QueueProcessorState.Paused, None)
    assert client.post("/api/v1/downloads/resume", headers=AUTH).status_code == 202
    assert fake.resume_calls == 2


def test_ac_15_5_reset_delete_and_clear_keep_archive() -> None:
    client, fake = _app()
    created = client.post(
        "/api/v1/downloads",
        headers=AUTH,
        json={"url": "https://youtu.be/aaaaaaaaaaa", "quality": "1080p"},
    )
    job_id = created.json()["items"][0]["id"]
    reset = client.post(f"/api/v1/downloads/{job_id}/reset", headers=AUTH)
    missing = client.post(f"/api/v1/downloads/{uuid4()}/reset", headers=AUTH)
    deleted = client.delete(f"/api/v1/downloads/{job_id}", headers=AUTH)
    cleared = client.delete("/api/v1/downloads", headers=AUTH)
    assert reset.status_code == 409
    assert missing.status_code == 404
    assert deleted.status_code == 204
    assert cleared.status_code == 204
    assert fake.clear_queue_calls == 1
    assert fake.archive_cleared is False


def test_ac_15_6_sabr_get_does_not_check() -> None:
    client, fake = _app()
    got = client.get("/api/v1/downloads/sabr", headers=AUTH)
    assert got.status_code == 200
    assert got.json()["mode"] == "inactive"
    assert fake.check_calls == 0
    checked = client.post("/api/v1/downloads/sabr/check", headers=AUTH)
    forced = client.post("/api/v1/downloads/sabr/force", headers=AUTH)
    cleared = client.post("/api/v1/downloads/sabr/clear", headers=AUTH)
    assert fake.check_calls == 1
    assert checked.json()["mode"] == "active"
    assert checked.json()["source"] == "detected"
    assert forced.json()["source"] == "forced"
    assert cleared.json()["mode"] == "inactive"


def test_ac_15_7_cookie_test_envelope() -> None:
    client, fake = _app()
    ok = client.post(
        "/api/v1/downloads/cookies/test",
        headers=AUTH,
        json={"mode": "browser", "browser": "chrome"},
    )
    fake.cookie_error = CookieTestError("unreadable")
    failed = client.post(
        "/api/v1/downloads/cookies/test",
        headers=AUTH,
        json={"mode": "file", "cookie_file": "C:/cookies.txt"},
    )
    assert ok.status_code == 200
    assert ok.json() == {"ok": True}
    assert "error_message" not in ok.json()
    assert "HTTP_COOKIE" not in ok.text
    assert failed.status_code == 422
    assert "cookie" not in failed.text.lower() or "unreadable" in failed.json()["error"]["message"]


def test_ac_15_8b_reorder_forwards_job_ids() -> None:
    client, fake = _app()
    first = client.post(
        "/api/v1/downloads",
        headers=AUTH,
        json={"url": "https://youtu.be/aaaaaaaaaaa", "quality": "1080p"},
    )
    second = client.post(
        "/api/v1/downloads",
        headers=AUTH,
        json={"url": "https://youtu.be/bbbbbbbbbbb", "quality": "720p"},
    )
    id_a = first.json()["items"][0]["id"]
    id_b = second.json()["items"][0]["id"]
    response = client.put(
        "/api/v1/downloads/reorder",
        headers=AUTH,
        json={"job_ids": [id_b, id_a]},
    )
    assert response.status_code == 200
    assert fake.last_reorder == [id_b, id_a]
    assert [item["id"] for item in response.json()["items"]] == [id_b, id_a]


def test_ac_15_8_apply_defaults() -> None:
    client, _fake = _app()
    response = client.post("/api/v1/downloads/apply-defaults", headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {"updated": 2}


def test_ac_15_9_speed_eta_iso_formatters() -> None:
    assert format_speed(None) is None
    assert format_speed(12300.0) == "12.3 KB/s"
    assert format_speed(12300000.0) == "12.3 MB/s"
    assert format_eta(None) is None
    assert format_eta(125) == "2:05"
    assert format_eta(3600) == "60:00"
    naive = datetime(2026, 1, 2, 3, 4, 5)
    aware = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    assert format_iso(naive).endswith("Z")
    assert format_iso(aware).endswith("+00:00")
    assert format_speed(float("nan")) is None


# --- MEU-42 re-queue widening + blocker-reason invariant -----------------------
REPO_ROOT_42 = Path(__file__).resolve().parents[2]
QUALITY_BLOCKED_REASON = (
    "YouTube is limiting which formats this video will serve right now, "
    "so the requested quality or audio format is not available."
)
QUALITY_BLOCKED_REMEDIATION = (
    "Settings > Downloader > Quality (choose a lower quality, "
    "or a supported audio format for audio-only jobs)"
)
AGE_RESTRICTED_REASON = "video is age-restricted"
REQUEUE_ROUTE_DOCSTRING = "Re-queue a job from a re-queueable state."
ROUTE_COUNT_AFTER = 78  # TA-6 (Session 30, MEU-67): + POST /captures/{id}/flatten, /revert
# MEU-130 (Session 59): + POST /captures/{id}/crop and the avkit_capture.crop action.
# MEU-133 (Session 62): + POST /conversions/probe and the avkit_convert.probe action.
# MEU-134 (Session 62): + POST /captures/frames and the avkit_capture.frames action.
# MEU-135 (Session 63): + POST /captures/sheet and the avkit_capture.sheet action.
# MEU-136 (Session 64): + POST /captures/{id}/export and the avkit_capture.export action.
# TA-9 (Session 27, MEU-62): +1 appended MCP action avkit_models.download_asset.
ACTION_INDEX_AFTER = 75  # TA-8 (Session 30, MEU-67): + avkit_capture.flatten, .revert
BLOCKER_REASON_MIGRATION_PREDICATE = (
    "status = 'QualityBlocked' AND (error_message IS NULL OR error_message <> '"
    + QUALITY_BLOCKED_REASON
    + "')"
)


def test_ac_42_7_services_persist_widened_requeue(tmp_path: Path) -> None:
    from tests.e2e.real_stack import real_stack

    from avkit_core.domain.enums import ConversionStatus

    with real_stack(tmp_path / "avkit.db") as stack:
        job = stack.seed_download(DownloadStatus.Cancelled, error_message="cancelled", progress=0.4)
        returned = stack.download.reset_failed(job.id)
        assert returned.status is DownloadStatus.Pending
        persisted = stack.read_download(job.id)
        assert persisted.status is DownloadStatus.Pending
        assert persisted.error_message is None
        assert persisted.progress == 0.0

        conv = stack.seed_conversion(ConversionStatus.Cancelled, error_message="cancelled")
        conv_returned = stack.conversion.reset_failed(conv.id)
        assert conv_returned.status is ConversionStatus.Pending
        conv_persisted = stack.read_conversion(conv.id)
        assert conv_persisted.status is ConversionStatus.Pending
        assert conv_persisted.error_message is None
        assert conv_persisted.progress == 0.0

        for call in (stack.download.reset_failed, stack.conversion.reset_failed):
            raised = False
            try:
                call(str(uuid4()))
            except NotFoundError:
                raised = True
            assert raised


def test_ac_42_9_surface_counts_are_flat_and_openapi_regenerated() -> None:
    import json

    spec = json.loads((REPO_ROOT_42 / "openapi.committed.json").read_text(encoding="utf-8"))
    methods = ("get", "post", "put", "delete", "patch")
    operations = [
        item[method]
        for item in spec["paths"].values()
        for method in item
        if method in methods
    ]
    assert len(operations) == ROUTE_COUNT_AFTER
    assert [path for path in spec["paths"] if path.endswith("/retry")] == [
        "/api/v1/transcripts/{id}/retry"
    ]

    reset_ops = [
        item[method]
        for path, item in spec["paths"].items()
        if path.endswith("/reset")
        for method in item
        if method in methods
    ]
    assert len(reset_ops) == 2
    for operation in reset_ops:
        assert operation["description"] == REQUEUE_ROUTE_DOCSTRING

    registry = (REPO_ROOT_42 / "mcp-server/src/toolsets/registry.ts").read_text(encoding="utf-8")
    assert registry.count("{ tool:") == ACTION_INDEX_AFTER


def test_ac_42_10_blocker_requeue_revalidates(tmp_path: Path) -> None:
    from tests.e2e.real_stack import real_stack

    with real_stack(tmp_path / "avkit.db") as stack:
        stack.download.force_sabr()

        # (b) compatible once the current downloader defaults are applied.
        stack.settings.set("downloader", "quality", "360p")
        ok = stack.seed_download(
            DownloadStatus.QualityBlocked,
            quality=QualityPreset.P1080,
            error_message=QUALITY_BLOCKED_REASON,
        )
        response = stack.client.post(f"/api/v1/downloads/{ok.id}/reset", headers=AUTH)
        assert response.status_code == 200
        assert response.json()["status"] == "Pending"
        reread = stack.read_download(ok.id)
        assert reread.status is DownloadStatus.Pending
        assert reread.quality is QualityPreset.P360

        # (c) still incompatible under Active SABR: refuse, name the setting, write nothing.
        stack.settings.set("downloader", "quality", "1080p")
        blocked = stack.seed_download(
            DownloadStatus.QualityBlocked,
            quality=QualityPreset.P1080,
            error_message=QUALITY_BLOCKED_REASON,
        )
        refused = stack.client.post(f"/api/v1/downloads/{blocked.id}/reset", headers=AUTH)
        assert refused.status_code == 409
        assert QUALITY_BLOCKED_REMEDIATION in refused.json()["error"]["message"]
        assert stack.read_download(blocked.id).status is DownloadStatus.QualityBlocked

        # (d) AgeRestricted re-queues unconditionally, SABR still Active.
        aged = stack.seed_download(
            DownloadStatus.AgeRestricted, error_message=AGE_RESTRICTED_REASON
        )
        aged_response = stack.client.post(f"/api/v1/downloads/{aged.id}/reset", headers=AUTH)
        assert aged_response.status_code == 200
        assert stack.read_download(aged.id).status is DownloadStatus.Pending


def test_ac_42_11_quality_blocked_jobs_carry_a_reason(tmp_path: Path) -> None:
    from tests.e2e.real_stack import real_stack

    from avkit_core.domain.download import BLOCKER_REASONS

    assert BLOCKER_REASONS[DownloadStatus.QualityBlocked] == QUALITY_BLOCKED_REASON
    assert BLOCKER_REASONS[DownloadStatus.AgeRestricted] == AGE_RESTRICTED_REASON
    for token in ("SABR", "1080", "{"):
        assert token not in QUALITY_BLOCKED_REASON

    with real_stack(tmp_path / "avkit.db") as stack:
        stack.download.force_sabr()

        # Producer 1: enqueue under an Active lock.
        created = stack.download.add_to_queue(
            "https://youtu.be/dQw4w9wgGc",
            QualityPreset.P1080,
            False,
            AudioFormat.Default,
        )
        enqueued = created[0]
        assert stack.read_download(enqueued.id).status is DownloadStatus.QualityBlocked
        assert stack.read_download(enqueued.id).error_message == QUALITY_BLOCKED_REASON
        assert stack.listed_download(enqueued.id, AUTH)["error_message"] == QUALITY_BLOCKED_REASON

        # Producer 2: apply_lock over an already-Pending incompatible job.
        pending = stack.seed_download(DownloadStatus.Pending, quality=QualityPreset.P1080)
        stack.download.apply_lock()
        assert stack.read_download(pending.id).status is DownloadStatus.QualityBlocked
        assert stack.read_download(pending.id).error_message == QUALITY_BLOCKED_REASON
        assert stack.listed_download(pending.id, AUTH)["error_message"] == QUALITY_BLOCKED_REASON


def test_ac_42_12_blocked_reason_survives_later_mutations(tmp_path: Path) -> None:
    from tests.e2e.real_stack import real_stack

    with real_stack(tmp_path / "avkit.db") as stack:
        stack.download.force_sabr()

        # (a) the legacy on-disk shape: blocked, no reason, then apply_lock.
        legacy = stack.insert_legacy_row(status=DownloadStatus.QualityBlocked)
        stack.download.apply_lock()
        assert stack.read_download(legacy).error_message == QUALITY_BLOCKED_REASON
        assert stack.listed_download(legacy, AUTH)["error_message"] == QUALITY_BLOCKED_REASON

        # (b) Apply Defaults rewrites a blocked row's quality without blanking the reason.
        stack.download.apply_defaults_to_pending()
        assert stack.read_download(legacy).status is DownloadStatus.QualityBlocked
        assert stack.read_download(legacy).error_message == QUALITY_BLOCKED_REASON
        assert stack.listed_download(legacy, AUTH)["error_message"] == QUALITY_BLOCKED_REASON

        # (c) the refused Retry canonicalizes the row it refuses.
        blank = stack.insert_legacy_row(status=DownloadStatus.QualityBlocked)
        refused = stack.client.post(f"/api/v1/downloads/{blank}/reset", headers=AUTH)
        assert refused.status_code == 409
        assert stack.read_download(blank).status is DownloadStatus.QualityBlocked
        assert stack.read_download(blank).error_message == QUALITY_BLOCKED_REASON
        assert stack.listed_download(blank, AUTH)["error_message"] == QUALITY_BLOCKED_REASON


def test_ac_42_13_unblocking_clears_the_reason(tmp_path: Path) -> None:
    from tests.e2e.real_stack import real_stack

    with real_stack(tmp_path / "avkit.db") as stack:
        job = stack.seed_download(
            DownloadStatus.QualityBlocked, error_message=QUALITY_BLOCKED_REASON
        )
        stack.download.clear_sabr()
        cleared = stack.read_download(job.id)
        assert cleared.status is DownloadStatus.Pending
        assert cleared.error_message is None
        assert stack.listed_download(job.id, AUTH)["error_message"] is None


def test_ac_42_14_repository_boundary_owns_the_invariant(tmp_path: Path) -> None:
    from dataclasses import replace

    from tests.e2e.real_stack import real_stack

    from avkit_core.domain.download import normalize_blocker_reason

    with real_stack(tmp_path / "avkit.db") as stack:
        # add(): a blocked job built with no reason gains one, with no service involved.
        added = stack.seed_download(DownloadStatus.QualityBlocked)
        assert stack.read_download(added.id).error_message == QUALITY_BLOCKED_REASON

        # save(): a blanked reason on a still-blocked row is refilled.
        with stack.uow_factory() as uow:
            uow.downloads.save(replace(stack.read_download(added.id), error_message=None))
            uow.commit()
        assert stack.read_download(added.id).error_message == QUALITY_BLOCKED_REASON

        # clause (2): leaving a blocker status clears the blocker reason.
        with stack.uow_factory() as uow:
            uow.downloads.save(
                replace(stack.read_download(added.id), status=DownloadStatus.Pending)
            )
            uow.commit()
        assert stack.read_download(added.id).error_message is None

        # narrowness: a real failure message on a non-blocker row is preserved untouched.
        failed = stack.seed_download(DownloadStatus.Failed, error_message="Traceback: boom")
        assert stack.read_download(failed.id).error_message == "Traceback: boom"

    # purity + location: a pure domain function, applied at the repository, nowhere else.
    job = DownloadJob(
        id=str(uuid4()),
        url="https://youtu.be/dQw4w9wgGc",
        video_id="dQw4w9wgGc",
        title="Example",
        quality=QualityPreset.P1080,
        audio_only=False,
        audio_format=AudioFormat.Default,
        status=DownloadStatus.QualityBlocked,
        progress=0.0,
        speed_bps=None,
        eta_seconds=None,
        file_size=None,
        file_path=None,
        error_message=None,
        queue_position=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    assert normalize_blocker_reason(job).error_message == QUALITY_BLOCKED_REASON
    assert job.error_message is None

    repositories = (
        REPO_ROOT_42 / "packages/infrastructure/src/avkit_infra/database/repositories.py"
    ).read_text(encoding="utf-8")
    assert repositories.count("normalize_blocker_reason(") == 2
    for relative in (
        "packages/core/src/avkit_core/services/download.py",
        "packages/api/src/avkit_api/routes/downloads.py",
        "packages/api/src/avkit_api/serializers.py",
    ):
        source = REPO_ROOT_42 / relative
        if source.is_file():
            assert "normalize_blocker_reason" not in source.read_text(encoding="utf-8")


def test_ac_42_15_upgrade_backfills_legacy_blocked_rows(tmp_path: Path) -> None:
    from tests.e2e.real_stack import RealStack, real_stack

    from avkit_infra.database.migrations import DATA_MIGRATIONS, apply_migrations

    assert any(
        BLOCKER_REASON_MIGRATION_PREDICATE in statement for statement in DATA_MIGRATIONS
    )
    migrations_source = (
        REPO_ROOT_42 / "packages/infrastructure/src/avkit_infra/database/migrations.py"
    ).read_text(encoding="utf-8")
    assert "BLOCKER_REASONS" in migrations_source

    db_path = tmp_path / "avkit.db"
    seeded = RealStack(db_path)
    blank = seeded.insert_legacy_row(status=DownloadStatus.QualityBlocked)
    keep = seeded.insert_legacy_row(
        status=DownloadStatus.Failed, error_message="real traceback"
    )
    already = seeded.insert_legacy_row(
        status=DownloadStatus.QualityBlocked, error_message=QUALITY_BLOCKED_REASON
    )
    seeded.close()

    # A fresh engine runs apply_migrations() before any route can serve.
    with real_stack(db_path) as upgraded:
        assert upgraded.listed_download(blank, AUTH)["error_message"] == QUALITY_BLOCKED_REASON
        assert upgraded.listed_download(keep, AUTH)["error_message"] == "real traceback"
        assert upgraded.listed_download(already, AUTH)["error_message"] == QUALITY_BLOCKED_REASON

        # Idempotent: a second pass changes nothing.
        apply_migrations(upgraded.engine)
        assert upgraded.listed_download(blank, AUTH)["error_message"] == QUALITY_BLOCKED_REASON
        assert upgraded.listed_download(keep, AUTH)["error_message"] == "real traceback"
        assert upgraded.listed_download(already, AUTH)["error_message"] == QUALITY_BLOCKED_REASON


# --- Round-1 review finding 1: a *stale* blocker reason must not survive -------
STALE_QUALITY_BLOCKED_REASON = "The requested 1080p quality is unavailable"


def test_r1f1_stale_blocker_reason_is_canonicalized_at_the_boundary(tmp_path: Path) -> None:
    """A nonblank *noncanonical* blocker reason is stale, not sacred: canonicalize it.

    AC-42.12/42.14 only proved the *blank* legacy shape gets filled. A row whose
    reason names a quality it no longer carries (`insert_legacy_row` + Apply
    Defaults) kept its stale text, so the card showed "1080p unavailable" on a
    360p job.
    """
    from dataclasses import replace

    from tests.e2e.real_stack import real_stack

    with real_stack(tmp_path / "avkit.db") as stack:
        stack.download.force_sabr()

        # add(): a blocked job built with a stale reason is canonicalized on write.
        added = stack.seed_download(
            DownloadStatus.QualityBlocked, error_message=STALE_QUALITY_BLOCKED_REASON
        )
        assert stack.read_download(added.id).error_message == QUALITY_BLOCKED_REASON

        # save(): a stale reason written onto a still-blocked row is canonicalized.
        with stack.uow_factory() as uow:
            uow.downloads.save(
                replace(
                    stack.read_download(added.id),
                    error_message=STALE_QUALITY_BLOCKED_REASON,
                )
            )
            uow.commit()
        assert stack.read_download(added.id).error_message == QUALITY_BLOCKED_REASON

        # the refused Retry canonicalizes a stale reason, not only a blank one.
        refused_id = stack.insert_legacy_row(
            status=DownloadStatus.QualityBlocked,
            error_message=STALE_QUALITY_BLOCKED_REASON,
        )
        refused = stack.client.post(f"/api/v1/downloads/{refused_id}/reset", headers=AUTH)
        assert refused.status_code == 409
        assert stack.read_download(refused_id).status is DownloadStatus.QualityBlocked
        assert stack.read_download(refused_id).error_message == QUALITY_BLOCKED_REASON

        # Apply Defaults over a legacy stale row: the quality moves, the reason follows.
        stale = stack.insert_legacy_row(
            status=DownloadStatus.QualityBlocked,
            error_message=STALE_QUALITY_BLOCKED_REASON,
            quality=QualityPreset.P1080,
        )
        stack.settings.set("downloader", "quality", "360p")
        stack.download.apply_defaults_to_pending()
        after = stack.read_download(stale)
        assert after.status is DownloadStatus.QualityBlocked
        assert after.quality is QualityPreset.P360
        assert after.error_message == QUALITY_BLOCKED_REASON
        assert stack.listed_download(stale, AUTH)["error_message"] == QUALITY_BLOCKED_REASON

        # narrowness holds: a real failure message on a non-blocker row is untouched.
        failed = stack.seed_download(DownloadStatus.Failed, error_message="Traceback: boom")
        assert stack.read_download(failed.id).error_message == "Traceback: boom"

    # purity: the stale-reason branch replaces, and does not mutate its input.
    job = DownloadJob(
        id=str(uuid4()),
        url="https://youtu.be/dQw4w9wgGc",
        video_id="dQw4w9wgGc",
        title="Example",
        quality=QualityPreset.P360,
        audio_only=False,
        audio_format=AudioFormat.Default,
        status=DownloadStatus.QualityBlocked,
        progress=0.0,
        speed_bps=None,
        eta_seconds=None,
        file_size=None,
        file_path=None,
        error_message=STALE_QUALITY_BLOCKED_REASON,
        queue_position=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    from avkit_core.domain.download import normalize_blocker_reason

    assert normalize_blocker_reason(job).error_message == QUALITY_BLOCKED_REASON
    assert job.error_message == STALE_QUALITY_BLOCKED_REASON


def test_r1f1_upgrade_backfills_noncanonical_legacy_blocked_rows(tmp_path: Path) -> None:
    """The upgrade repairs *noncanonical* blocked rows, not only blank ones."""
    from tests.e2e.real_stack import RealStack, real_stack

    from avkit_infra.database.migrations import apply_migrations

    db_path = tmp_path / "avkit.db"
    seeded = RealStack(db_path)
    stale = seeded.insert_legacy_row(
        status=DownloadStatus.QualityBlocked,
        error_message=STALE_QUALITY_BLOCKED_REASON,
    )
    whitespace = seeded.insert_legacy_row(
        status=DownloadStatus.QualityBlocked, error_message="   "
    )
    keep = seeded.insert_legacy_row(
        status=DownloadStatus.Failed, error_message=STALE_QUALITY_BLOCKED_REASON
    )
    seeded.close()

    with real_stack(db_path) as upgraded:
        assert upgraded.listed_download(stale, AUTH)["error_message"] == QUALITY_BLOCKED_REASON
        assert (
            upgraded.listed_download(whitespace, AUTH)["error_message"] == QUALITY_BLOCKED_REASON
        )
        assert (
            upgraded.listed_download(keep, AUTH)["error_message"]
            == STALE_QUALITY_BLOCKED_REASON
        )

        # Idempotent: a second pass changes nothing.
        apply_migrations(upgraded.engine)
        assert upgraded.listed_download(stale, AUTH)["error_message"] == QUALITY_BLOCKED_REASON
        assert (
            upgraded.listed_download(whitespace, AUTH)["error_message"] == QUALITY_BLOCKED_REASON
        )
        assert (
            upgraded.listed_download(keep, AUTH)["error_message"]
            == STALE_QUALITY_BLOCKED_REASON
        )


def test_ac_124_9_list_items_carry_received_height() -> None:
    from dataclasses import replace

    client, fake = _app()
    for url in ("https://youtu.be/aaaaaaaaaaa", "https://youtu.be/bbbbbbbbbbb"):
        client.post("/api/v1/downloads", headers=AUTH, json={"url": url, "quality": "1080p"})
    fake.jobs[0] = replace(fake.jobs[0], received_height=360)
    listed = client.get("/api/v1/downloads", headers=AUTH)
    assert listed.status_code == 200
    by_id = {item["id"]: item for item in listed.json()["items"]}
    assert by_id[fake.jobs[0].id].get("received_height") == 360
    other = by_id[fake.jobs[1].id]
    assert "received_height" in other
    assert other["received_height"] is None
