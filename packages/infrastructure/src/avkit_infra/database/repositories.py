"""SQLAlchemy implementations of the frozen storage Protocols."""

from __future__ import annotations

from pathlib import Path

import structlog
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from avkit_core.domain.capture import CaptureRequest, CaptureShot
from avkit_core.domain.conversion import ConversionJob
from avkit_core.domain.download import (
    DownloadArchiveEntry,
    DownloadJob,
    normalize_blocker_reason,
)
from avkit_core.domain.enums import (
    CaptureRequestStatus,
    DownloadStatus,
    TranscriptItemStatus,
    TTSStatus,
)
from avkit_core.domain.errors import NotFoundError, ValidationError
from avkit_core.domain.settings import Setting
from avkit_core.domain.transcript import TranscriptItem, TranscriptJob
from avkit_core.domain.tts import ModelVariant, TTSJob
from avkit_infra.database.mappers import (
    apply_capture_request,
    apply_capture_shot,
    apply_conversion_job,
    apply_download_job,
    apply_setting,
    apply_transcript_item,
    apply_transcript_job,
    apply_tts_job,
    archive_entry_from_row,
    capture_request_from_row,
    capture_request_to_row,
    capture_shot_from_row,
    capture_shot_to_row,
    conversion_job_from_row,
    conversion_job_to_row,
    download_job_from_row,
    download_job_to_row,
    model_variant_from_row,
    setting_from_row,
    setting_to_row,
    transcript_item_from_row,
    transcript_item_to_row,
    transcript_job_from_row,
    transcript_job_to_row,
    tts_job_from_row,
    tts_job_to_row,
)
from avkit_infra.database.models import (
    CaptureRequestRow,
    CaptureShotRow,
    ConversionJobRow,
    DownloadArchiveRow,
    DownloadJobRow,
    ModelVariantRow,
    SettingRow,
    TranscriptItemRow,
    TranscriptJobRow,
    TTSJobRow,
)

log = structlog.get_logger(module="database")


class SqlAlchemyDownloadRepository:
    """Download queue persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, job: DownloadJob) -> None:
        self.session.add(download_job_to_row(normalize_blocker_reason(job)))

    def get(self, job_id: str) -> DownloadJob | None:
        row = self.session.get(DownloadJobRow, job_id)
        if row is None:
            return None
        return download_job_from_row(row)

    def list_ordered(self) -> list[DownloadJob]:
        rows = self.session.scalars(
            select(DownloadJobRow).order_by(DownloadJobRow.queue_position.asc())
        ).all()
        return [download_job_from_row(row) for row in rows]

    def save(self, job: DownloadJob) -> None:
        row = self.session.get(DownloadJobRow, job.id)
        if row is None:
            raise NotFoundError(f"download job {job.id} not found")
        apply_download_job(row, normalize_blocker_reason(job))

    def reorder(self, job_ids: list[str]) -> None:
        for position, job_id in enumerate(job_ids):
            row = self.session.get(DownloadJobRow, job_id)
            if row is None:
                raise NotFoundError(f"download job {job_id} not found")
            row.queue_position = position

    def delete(self, job_id: str) -> None:
        row = self.session.get(DownloadJobRow, job_id)
        if row is None:
            return
        self.session.delete(row)

    def delete_all(self) -> None:
        self.session.execute(delete(DownloadJobRow))

    def reset_failed(self) -> None:
        rows = self.session.scalars(
            select(DownloadJobRow).where(DownloadJobRow.status == DownloadStatus.Failed.name)
        ).all()
        for row in rows:
            job = download_job_from_row(row)
            apply_download_job(row, job.reset_failed())

    def has_video_id(self, video_id: str) -> bool:
        found = self.session.scalar(
            select(DownloadJobRow.id).where(DownloadJobRow.video_id == video_id).limit(1)
        )
        return found is not None


class SqlAlchemyArchiveRepository:
    """Skip-catalog persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, extractor: str, video_id: str) -> DownloadArchiveEntry | None:
        row = self.session.get(DownloadArchiveRow, (extractor, video_id))
        if row is None:
            return None
        return archive_entry_from_row(row)

    def add(self, entry: DownloadArchiveEntry) -> None:
        statement = (
            insert(DownloadArchiveRow)
            .values(
                extractor=entry.extractor,
                video_id=entry.video_id,
                title=entry.title,
                recorded_at=entry.recorded_at,
            )
            .on_conflict_do_nothing(index_elements=["extractor", "video_id"])
        )
        self.session.execute(statement)

    def list(self) -> list[DownloadArchiveEntry]:
        rows = self.session.scalars(select(DownloadArchiveRow)).all()
        return [archive_entry_from_row(row) for row in rows]


class SqlAlchemyTranscriptRepository:
    """Transcript job plus item aggregate persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add_job(self, job: TranscriptJob) -> None:
        self.session.add(transcript_job_to_row(job))

    def get_job(self, job_id: str) -> TranscriptJob | None:
        row = self.session.get(TranscriptJobRow, job_id)
        if row is None:
            return None
        return transcript_job_from_row(row)

    def list_jobs_ordered(self) -> list[TranscriptJob]:
        rows = self.session.scalars(
            select(TranscriptJobRow).order_by(TranscriptJobRow.queue_position.asc())
        ).all()
        return [transcript_job_from_row(row) for row in rows]

    def save_job(self, job: TranscriptJob) -> None:
        row = self.session.get(TranscriptJobRow, job.id)
        if row is None:
            raise NotFoundError(f"transcript job {job.id} not found")
        apply_transcript_job(row, job)

    def reorder_jobs(self, job_ids: list[str]) -> None:
        for position, job_id in enumerate(job_ids):
            row = self.session.get(TranscriptJobRow, job_id)
            if row is None:
                raise NotFoundError(f"transcript job {job_id} not found")
            row.queue_position = position

    def delete_job(self, job_id: str) -> None:
        row = self.session.get(TranscriptJobRow, job_id)
        if row is None:
            return
        self.session.delete(row)

    def replace_items(self, job_id: str, items: list[TranscriptItem]) -> None:
        parent = self.session.get(TranscriptJobRow, job_id)
        if parent is None:
            raise NotFoundError(f"transcript job {job_id} not found")
        self.session.execute(delete(TranscriptItemRow).where(TranscriptItemRow.job_id == job_id))
        for item in items:
            self.session.add(transcript_item_to_row(item))
        parent.video_count = len(items)

    def list_items(self, job_id: str) -> list[TranscriptItem]:
        rows = self.session.scalars(
            select(TranscriptItemRow)
            .where(TranscriptItemRow.job_id == job_id)
            .order_by(TranscriptItemRow.video_id.asc())
        ).all()
        return [transcript_item_from_row(row) for row in rows]

    def save_item(self, item: TranscriptItem) -> None:
        row = self.session.get(TranscriptItemRow, item.id)
        if row is None:
            raise NotFoundError(f"transcript item {item.id} not found")
        apply_transcript_item(row, item)

    def count_items(self, job_id: str) -> int:
        total = self.session.scalar(
            select(func.count()).select_from(TranscriptItemRow).where(
                TranscriptItemRow.job_id == job_id
            )
        )
        return int(total or 0)

    def count_items_with_status(self, job_id: str, status: TranscriptItemStatus) -> int:
        total = self.session.scalar(
            select(func.count())
            .select_from(TranscriptItemRow)
            .where(
                TranscriptItemRow.job_id == job_id,
                TranscriptItemRow.status == status.name,
            )
        )
        return int(total or 0)

    def progress_counts(self, job_id: str) -> dict[str, int]:
        counts = {
            "total": 0,
            "done": 0,
            "skipped": 0,
            "failed": 0,
            "pending": 0,
        }
        rows = self.session.execute(
            select(TranscriptItemRow.status, func.count())
            .where(TranscriptItemRow.job_id == job_id)
            .group_by(TranscriptItemRow.status)
        ).all()
        for status_name, amount in rows:
            counts["total"] += int(amount)
            key = str(status_name).lower()
            if key in counts:
                counts[key] = int(amount)
        return counts

    def recompute_word_count(self, job_id: str) -> None:
        parent = self.session.get(TranscriptJobRow, job_id)
        if parent is None:
            raise NotFoundError(f"transcript job {job_id} not found")
        total = self.session.scalar(
            select(func.coalesce(func.sum(TranscriptItemRow.word_count), 0)).where(
                TranscriptItemRow.job_id == job_id
            )
        )
        parent.word_count = int(total or 0)


class SqlAlchemyTTSJobRepository:
    """TTS job persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, job: TTSJob) -> None:
        self.session.add(tts_job_to_row(job))

    def get(self, job_id: str) -> TTSJob | None:
        row = self.session.get(TTSJobRow, job_id)
        if row is None:
            return None
        return tts_job_from_row(row)

    def save(self, job: TTSJob) -> None:
        row = self.session.get(TTSJobRow, job.id)
        if row is None:
            raise NotFoundError(f"tts job {job.id} not found")
        apply_tts_job(row, job)

    def delete(self, job_id: str) -> None:
        row = self.session.get(TTSJobRow, job_id)
        if row is None:
            return
        self.session.delete(row)

    def list_by_status(self, status: TTSStatus) -> list[TTSJob]:
        rows = self.session.scalars(
            select(TTSJobRow)
            .where(TTSJobRow.status == status.name)
            .order_by(TTSJobRow.created_at.asc())
        ).all()
        return [tts_job_from_row(row) for row in rows]


class SqlAlchemySettingsRepository:
    """Namespaced settings persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, namespace: str, key: str) -> Setting | None:
        row = self.session.get(SettingRow, (namespace, key))
        if row is None:
            return None
        return setting_from_row(row)

    def set(self, setting: Setting) -> None:
        row = self.session.get(SettingRow, (setting.namespace, setting.key))
        if row is None:
            self.session.add(setting_to_row(setting))
            return
        apply_setting(row, setting)

    def get_namespace(self, namespace: str) -> list[Setting]:
        rows = self.session.scalars(
            select(SettingRow)
            .where(SettingRow.namespace == namespace)
            .order_by(SettingRow.key.asc())
        ).all()
        return [setting_from_row(row) for row in rows]

    def set_namespace(self, namespace: str, settings: list[Setting]) -> None:
        for setting in settings:
            if setting.namespace != namespace:
                raise ValidationError("setting namespace must match set_namespace namespace")
        self.session.execute(delete(SettingRow).where(SettingRow.namespace == namespace))
        for setting in settings:
            self.session.add(setting_to_row(setting))


class SqlAlchemyModelRepository:
    """Model catalog persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_catalog(self) -> list[ModelVariant]:
        rows = self.session.scalars(
            select(ModelVariantRow).order_by(ModelVariantRow.id.asc())
        ).all()
        return [model_variant_from_row(row) for row in rows]

    def get(self, variant_id: str) -> ModelVariant | None:
        row = self.session.get(ModelVariantRow, variant_id)
        if row is None:
            return None
        return model_variant_from_row(row)

    def mark_downloaded(self, variant_id: str, path: Path) -> None:
        row = self.session.get(ModelVariantRow, variant_id)
        if row is None:
            raise NotFoundError(f"model variant {variant_id} not found")
        row.path = str(path)
        row.is_downloaded = True
        if path.is_file():
            row.size_bytes = path.stat().st_size
        log.info("model.marked_downloaded", variant_id=variant_id, path=str(path))

    def list_downloaded(self) -> list[ModelVariant]:
        rows = self.session.scalars(
            select(ModelVariantRow)
            .where(ModelVariantRow.is_downloaded.is_(True))
            .order_by(ModelVariantRow.id.asc())
        ).all()
        return [model_variant_from_row(row) for row in rows]


class SqlAlchemyConversionJobRepository:
    """Conversion queue persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, job: ConversionJob) -> None:
        self.session.add(conversion_job_to_row(job))

    def get(self, job_id: str) -> ConversionJob | None:
        row = self.session.get(ConversionJobRow, job_id)
        if row is None:
            return None
        return conversion_job_from_row(row)

    def list_ordered(self) -> list[ConversionJob]:
        rows = self.session.scalars(
            select(ConversionJobRow).order_by(ConversionJobRow.queue_position.asc())
        ).all()
        return [conversion_job_from_row(row) for row in rows]

    def save(self, job: ConversionJob) -> None:
        row = self.session.get(ConversionJobRow, job.id)
        if row is None:
            raise NotFoundError(f"conversion job {job.id} not found")
        apply_conversion_job(row, job)

    def reorder(self, job_ids: list[str]) -> None:
        for position, job_id in enumerate(job_ids):
            row = self.session.get(ConversionJobRow, job_id)
            if row is None:
                raise NotFoundError(f"conversion job {job_id} not found")
            row.queue_position = position

    def delete(self, job_id: str) -> None:
        row = self.session.get(ConversionJobRow, job_id)
        if row is None:
            return
        self.session.delete(row)

    def delete_all(self) -> None:
        self.session.execute(delete(ConversionJobRow))


class SqlAlchemyCaptureShotRepository:
    """Capture inbox original persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, shot: CaptureShot) -> None:
        self.session.add(capture_shot_to_row(shot))

    def get(self, shot_id: str) -> CaptureShot | None:
        row = self.session.get(CaptureShotRow, shot_id)
        if row is None:
            return None
        return capture_shot_from_row(row)

    def list(self) -> list[CaptureShot]:
        rows = self.session.scalars(
            select(CaptureShotRow).order_by(CaptureShotRow.created_at.desc())
        ).all()
        return [capture_shot_from_row(row) for row in rows]

    def save(self, shot: CaptureShot) -> None:
        row = self.session.get(CaptureShotRow, shot.id)
        if row is None:
            raise NotFoundError(f"capture shot {shot.id} not found")
        apply_capture_shot(row, shot)

    def delete(self, shot_id: str) -> None:
        row = self.session.get(CaptureShotRow, shot_id)
        if row is None:
            return
        self.session.delete(row)

    def get_by_path(self, original_path: Path) -> CaptureShot | None:
        row = self.session.scalar(
            select(CaptureShotRow).where(CaptureShotRow.original_path == str(original_path))
        )
        if row is None:
            return None
        return capture_shot_from_row(row)


class SqlAlchemyCaptureRequestRepository:
    """Interactive capture request persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, request: CaptureRequest) -> None:
        self.session.add(capture_request_to_row(request))

    def get(self, request_id: str) -> CaptureRequest | None:
        row = self.session.get(CaptureRequestRow, request_id)
        if row is None:
            return None
        return capture_request_from_row(row)

    def save(self, request: CaptureRequest) -> None:
        row = self.session.get(CaptureRequestRow, request.id)
        if row is None:
            raise NotFoundError(f"capture request {request.id} not found")
        apply_capture_request(row, request)

    def list(self) -> list[CaptureRequest]:
        rows = self.session.scalars(
            select(CaptureRequestRow).order_by(CaptureRequestRow.created_at.desc())
        ).all()
        return [capture_request_from_row(row) for row in rows]

    def get_pending_request(self) -> CaptureRequest | None:
        row = self.session.scalar(
            select(CaptureRequestRow)
            .where(CaptureRequestRow.status == CaptureRequestStatus.Pending.name)
            .order_by(CaptureRequestRow.created_at.asc())
        )
        if row is None:
            return None
        return capture_request_from_row(row)
