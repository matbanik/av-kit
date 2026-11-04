"""SqlAlchemyUnitOfWork — one session per enter, commit on clean exit."""

from __future__ import annotations

from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from avkit_core.domain.errors import ValidationError
from avkit_infra.database.repositories import (
    SqlAlchemyArchiveRepository,
    SqlAlchemyCaptureRequestRepository,
    SqlAlchemyCaptureShotRepository,
    SqlAlchemyConversionJobRepository,
    SqlAlchemyDownloadRepository,
    SqlAlchemyModelRepository,
    SqlAlchemySettingsRepository,
    SqlAlchemyTranscriptRepository,
    SqlAlchemyTTSJobRepository,
)


class SqlAlchemyUnitOfWork:
    """Transactional boundary over the Phase 1 repository set."""

    downloads: SqlAlchemyDownloadRepository
    archive: SqlAlchemyArchiveRepository
    transcripts: SqlAlchemyTranscriptRepository
    tts_jobs: SqlAlchemyTTSJobRepository
    settings: SqlAlchemySettingsRepository
    models: SqlAlchemyModelRepository
    conversion_jobs: SqlAlchemyConversionJobRepository
    capture_shots: SqlAlchemyCaptureShotRepository
    capture_requests: SqlAlchemyCaptureRequestRepository

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> Self:
        session = self._session_factory()
        self._session = session
        self.downloads = SqlAlchemyDownloadRepository(session)
        self.archive = SqlAlchemyArchiveRepository(session)
        self.transcripts = SqlAlchemyTranscriptRepository(session)
        self.tts_jobs = SqlAlchemyTTSJobRepository(session)
        self.settings = SqlAlchemySettingsRepository(session)
        self.models = SqlAlchemyModelRepository(session)
        self.conversion_jobs = SqlAlchemyConversionJobRepository(session)
        self.capture_shots = SqlAlchemyCaptureShotRepository(session)
        self.capture_requests = SqlAlchemyCaptureRequestRepository(session)
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        session = self._session
        if session is None:
            return
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            session.close()
            self._session = None

    def commit(self) -> None:
        if self._session is None:
            raise ValidationError("unit of work is not active")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            raise ValidationError("unit of work is not active")
        self._session.rollback()
