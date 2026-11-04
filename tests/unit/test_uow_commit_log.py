"""Read-only UoW exit must not flood the console with debug uow.commit lines."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.tts_asset_fakes import FakeAssets, idle_runtime

from avkit_core.services.health import HealthService
from avkit_core.services.settings import SettingsService
from avkit_infra.database.engine import create_session_factory, create_sqlite_engine, init_schema
from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork


class _Media:
    def ffmpeg_version(self) -> str | None:
        return None


class _YouTube:
    def ytdlp_version(self) -> str | None:
        return None


@pytest.mark.unit
def test_uow_commit_does_not_emit_debug_console_event(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    settings = SettingsService(factory)
    health = HealthService(
        factory,
        app_data=tmp_path,
        settings=settings,
        media=_Media(),
        youtube=_YouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
        ring_capacity=64,
    )
    before = {event.seq for event in health.console_snapshot(0)}
    with SqlAlchemyUnitOfWork(session_factory):
        pass
    after = health.console_snapshot(0)
    new_messages = [event.message for event in after if event.seq not in before]
    assert "uow.commit" not in new_messages
