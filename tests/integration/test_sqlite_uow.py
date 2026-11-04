"""MEU-5 SQLite UoW integration tests."""

from __future__ import annotations

import ast
import inspect
import math
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INFRA_SRC = REPO_ROOT / "packages" / "infrastructure" / "src"
AVKIT_INFRA = INFRA_SRC / "avkit_infra"

INFRA_LAYOUT = (
    "database/engine.py",
    "database/models.py",
    "database/mappers.py",
    "database/repositories.py",
    "database/unit_of_work.py",
    "database/migrations.py",
    "filesystem/writer.py",
    "media/adapter.py",
    "capture/adapter.py",
)
DEFERRED_ADAPTER_DIRS: tuple[str, ...] = ()


def _read_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _dependency_name(spec: str) -> str:
    token = spec.strip()
    for separator in ("[", " ", "<", ">", "=", "!"):
        index = token.find(separator)
        if index != -1:
            token = token[:index]
    return token.lower()


def _sqlalchemy_floor_major(spec: str) -> int:
    match = re.search(r">=\s*(\d+)", spec)
    if match is None:
        raise AssertionError(f"sqlalchemy spec {spec!r} has no >= major floor")
    return int(match.group(1))


@pytest.mark.integration
def test_ac_5_1_workspace_layout_and_no_deferred_adapters() -> None:
    root_pyproject = REPO_ROOT / "pyproject.toml"
    data = _read_toml(root_pyproject)
    uv_table = data.get("tool")
    assert isinstance(uv_table, dict)
    uv = uv_table.get("uv")
    assert isinstance(uv, dict)
    workspace = uv.get("workspace")
    assert isinstance(workspace, dict)
    members = workspace.get("members")
    assert members == ["packages/core", "packages/infrastructure", "packages/api"]

    import avkit_infra

    assert avkit_infra is not None
    missing = [rel for rel in INFRA_LAYOUT if not (AVKIT_INFRA / rel).is_file()]
    assert missing == [], f"missing INFRA_LAYOUT modules: {missing}"
    present_deferred = [
        name for name in DEFERRED_ADAPTER_DIRS if (AVKIT_INFRA / name).exists()
    ]
    assert present_deferred == [], f"deferred adapter dirs present: {present_deferred}"


@pytest.mark.integration
def test_ac_5_2_infra_dependencies_and_tool_paths() -> None:
    infra_pyproject = REPO_ROOT / "packages" / "infrastructure" / "pyproject.toml"
    assert infra_pyproject.is_file()
    data = _read_toml(infra_pyproject)
    project = data.get("project")
    assert isinstance(project, dict)
    dependencies = project.get("dependencies")
    assert isinstance(dependencies, list)
    declared = {_dependency_name(str(item)) for item in dependencies}
    assert "avkit-core" in declared
    assert "sqlalchemy" in declared
    assert "structlog" in declared
    sqlalchemy_specs = [
        str(item) for item in dependencies if _dependency_name(str(item)) == "sqlalchemy"
    ]
    assert sqlalchemy_specs, "sqlalchemy dependency missing"
    assert any(_sqlalchemy_floor_major(spec) >= 2 for spec in sqlalchemy_specs)

    root = _read_toml(REPO_ROOT / "pyproject.toml")
    pytest_opts = root.get("tool")
    assert isinstance(pytest_opts, dict)
    pytest_table = pytest_opts.get("pytest")
    assert isinstance(pytest_table, dict)
    ini = pytest_table.get("ini_options")
    assert isinstance(ini, dict)
    pythonpath = ini.get("pythonpath")
    assert isinstance(pythonpath, list)
    assert "packages/core/src" in pythonpath
    assert "packages/infrastructure/src" in pythonpath

    pyright = pytest_opts.get("pyright")
    assert isinstance(pyright, dict)
    include = pyright.get("include")
    assert isinstance(include, list)
    assert "packages/infrastructure/src" in include
    extra_paths = pyright.get("extraPaths")
    assert isinstance(extra_paths, list)
    assert "packages/infrastructure/src" in extra_paths

    ruff = pytest_opts.get("ruff")
    assert isinstance(ruff, dict)
    ruff_src = ruff.get("src")
    assert isinstance(ruff_src, list)
    assert "packages/infrastructure/src" in ruff_src

    import sqlalchemy
    import structlog

    assert sqlalchemy.__version__
    assert structlog.__version__


TABLES = (
    "download_jobs",
    "download_archive",
    "transcript_jobs",
    "transcript_items",
    "tts_jobs",
    "model_variants",
    "settings",
    "conversion_jobs",
    "capture_shots",
    "capture_requests",
)
FORBIDDEN_TABLES = (
    "jobs",
    "job_artifacts",
    "queue_runtime",
    "sabr_state",
    "download_job_parents",
)
FORBIDDEN_MODEL_COLUMNS = ("is_loaded", "device")
SEED_VARIANT_IDS = (
    "kokoro-pt-fp32",
    "kokoro-onnx-fp32",
    "kokoro-onnx-fp16",
    "kokoro-onnx-int8",
)
SEED_SIZE_BYTES = (
    326 * 1024 * 1024,
    326 * 1024 * 1024,
    163 * 1024 * 1024,
    87 * 1024 * 1024,
)


def _file_engine(tmp_path: Path):
    from avkit_infra.database.engine import create_sqlite_engine, init_schema

    db_path = tmp_path / "avkit.db"
    assert db_path.name == "avkit.db"
    engine = create_sqlite_engine(db_path)
    init_schema(engine)
    return engine, db_path


@pytest.mark.integration
def test_ac_5_3_file_engine_applies_pragma_locks(tmp_path: Path) -> None:
    from avkit_infra.database.engine import SQLITE_CONNECT_ARGS

    engine, db_path = _file_engine(tmp_path)
    assert db_path.is_file()
    assert ":memory:" not in str(engine.url)
    assert SQLITE_CONNECT_ARGS["check_same_thread"] is False
    with engine.connect() as connection:
        journal = connection.exec_driver_sql("PRAGMA journal_mode").scalar()
        timeout = connection.exec_driver_sql("PRAGMA busy_timeout").scalar()
        foreign_keys = connection.exec_driver_sql("PRAGMA foreign_keys").scalar()
    assert str(journal).lower() == "wal"
    assert int(timeout) == 5000
    assert int(foreign_keys) == 1


@pytest.mark.integration
def test_ac_5_4_init_schema_creates_exactly_seven_tables(tmp_path: Path) -> None:
    from sqlalchemy import inspect

    from avkit_infra.database.models import Base

    engine, _db_path = _file_engine(tmp_path)
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    assert names == set(TABLES)
    for forbidden in FORBIDDEN_TABLES:
        assert forbidden not in names
    variant_columns = {column["name"] for column in inspector.get_columns("model_variants")}
    for forbidden in FORBIDDEN_MODEL_COLUMNS:
        assert forbidden not in variant_columns
    tts_columns = {column["name"] for column in inspector.get_columns("tts_jobs")}
    assert "text" not in tts_columns
    metadata_names = set(Base.metadata.tables)
    assert metadata_names == set(TABLES)


@pytest.mark.integration
def test_ac_5_5_catalog_seed_is_idempotent(tmp_path: Path) -> None:
    from sqlalchemy import text

    from avkit_infra.database.engine import init_schema

    engine, _db_path = _file_engine(tmp_path)
    init_schema(engine)
    with engine.connect() as connection:
        rows = list(
            connection.execute(
                text(
                    "SELECT id, name, format, precision, size_bytes, path, is_downloaded "
                    "FROM model_variants ORDER BY id"
                )
            )
        )
    assert [row[0] for row in rows] == sorted(SEED_VARIANT_IDS)
    by_id = {row[0]: row for row in rows}
    expected = {
        "kokoro-pt-fp32": ("PyTorch FP32", "PyTorch", "FP32", SEED_SIZE_BYTES[0]),
        "kokoro-onnx-fp32": ("ONNX FP32", "ONNX", "FP32", SEED_SIZE_BYTES[1]),
        "kokoro-onnx-fp16": ("ONNX FP16", "ONNX", "FP16", SEED_SIZE_BYTES[2]),
        "kokoro-onnx-int8": ("ONNX INT8", "ONNX", "INT8", SEED_SIZE_BYTES[3]),
    }
    for variant_id, (name, fmt, precision, size) in expected.items():
        row = by_id[variant_id]
        assert row[1] == name
        assert row[2] == fmt
        assert row[3] == precision
        assert int(row[4]) == size
        assert row[5] is None
        assert int(row[6]) == 0


@pytest.mark.integration
def test_ac_5_6_migrations_empty_apply_is_noop() -> None:
    from avkit_infra.database.migrations import MIGRATIONS, apply_migrations

    assert MIGRATIONS
    assert all("IF NOT EXISTS" in statement for statement in MIGRATIONS)
    assert any(
        "CREATE TABLE IF NOT EXISTS conversion_jobs" in statement for statement in MIGRATIONS
    )
    apply_migrations(None)
    apply_migrations(None)
    alembic = list((REPO_ROOT / "packages" / "infrastructure").rglob("alembic.ini"))
    assert alembic == []


@pytest.mark.integration
def test_ac_5_15_resolve_app_data_env_and_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from avkit_infra.database.engine import DB_FILENAME, default_db_path, resolve_app_data

    override = tmp_path / "override-app-data"
    monkeypatch.setenv("AVKIT_APP_DATA", str(override))
    assert resolve_app_data() == override
    assert default_db_path() == override / DB_FILENAME
    assert DB_FILENAME == "avkit.db"

    monkeypatch.delenv("AVKIT_APP_DATA")
    monkeypatch.setattr("avkit_infra.database.engine.sys.platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    assert resolve_app_data() == tmp_path / "local" / "av-kit"

    monkeypatch.setattr("avkit_infra.database.engine.sys.platform", "linux")
    monkeypatch.setattr(
        "avkit_infra.database.engine.user_home",
        lambda: tmp_path / "home",
    )
    assert resolve_app_data() == tmp_path / "home" / ".avkit"


DOWNLOAD_REPO_METHODS = (
    "add",
    "get",
    "list_ordered",
    "save",
    "reorder",
    "delete",
    "delete_all",
    "reset_failed",
)
ARCHIVE_REPO_METHODS = ("get", "add", "list")
TRANSCRIPT_REPO_METHODS = (
    "add_job",
    "get_job",
    "list_jobs_ordered",
    "save_job",
    "reorder_jobs",
    "delete_job",
    "replace_items",
    "list_items",
    "save_item",
    "count_items",
    "count_items_with_status",
)
# TA-6 (Session 33, MEU-77)
TTS_REPO_METHODS = ("add", "get", "save", "delete", "list_by_status")
SETTINGS_REPO_METHODS = ("get", "set", "get_namespace", "set_namespace")
MODEL_REPO_METHODS = ("list_catalog", "get", "mark_downloaded")
UOW_ATTRIBUTES = (
    "downloads",
    "archive",
    "transcripts",
    "tts_jobs",
    "settings",
    "models",
    "conversion_jobs",
    "capture_shots",
    "capture_requests",
)
UOW_METHODS = ("__enter__", "__exit__", "commit", "rollback")
TEXT_PREVIEW_MAX = 200
INFRA_NAMES = frozenset(
    {
        "sqlalchemy",
        "yt_dlp",
        "fastapi",
        "youtube_transcript_api",
        "huggingface_hub",
        "soundfile",
    }
)


def _now() -> datetime:
    return datetime(2026, 8, 19, 12, 0, tzinfo=UTC)


def _download_job(**overrides: object):
    from avkit_core.domain.download import DownloadJob
    from avkit_core.domain.enums import AudioFormat, DownloadStatus, QualityPreset

    payload: dict[str, object] = {
        "id": str(uuid4()),
        "url": "https://youtu.be/dQw4w9wgGc",
        "video_id": "dQw4w9wgGc",
        "title": "Example",
        "quality": QualityPreset.P1080,
        "audio_only": False,
        "audio_format": AudioFormat.Default,
        "status": DownloadStatus.Pending,
        "progress": 0.0,
        "speed_bps": None,
        "eta_seconds": None,
        "file_size": None,
        "file_path": None,
        "error_message": None,
        "queue_position": 0,
        "created_at": _now(),
        "updated_at": _now(),
    }
    payload.update(overrides)
    return DownloadJob(**payload)


def _archive_entry(**overrides: object):
    from avkit_core.domain.download import DownloadArchiveEntry

    payload: dict[str, object] = {
        "extractor": "youtube",
        "video_id": "dQw4w9wgGc",
        "title": "Example",
        "recorded_at": _now(),
    }
    payload.update(overrides)
    return DownloadArchiveEntry(**payload)


def _transcript_job(**overrides: object):
    from avkit_core.domain.enums import TranscriptStatus
    from avkit_core.domain.transcript import TranscriptJob

    payload: dict[str, object] = {
        "id": str(uuid4()),
        "channel_url": "https://youtube.com/@example",
        "channel_name": "Example",
        "status": TranscriptStatus.Pending,
        "output_dir": Path("channels/example"),
        "video_count": 0,
        "word_count": 0,
        "zip_path": None,
        "queue_position": 0,
        "error_message": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    payload.update(overrides)
    return TranscriptJob(**payload)


def _transcript_item(*, job_id: str, **overrides: object):
    from avkit_core.domain.enums import TranscriptItemStatus
    from avkit_core.domain.transcript import TranscriptItem

    payload: dict[str, object] = {
        "id": str(uuid4()),
        "job_id": job_id,
        "video_id": "vid001",
        "title": "Item",
        "language": "en",
        "word_count": 0,
        "path": None,
        "status": TranscriptItemStatus.Pending,
        "error_message": None,
        "retry_count": 0,
        "processed_at": None,
    }
    payload.update(overrides)
    return TranscriptItem(**payload)


def _tts_job(**overrides: object):
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus
    from avkit_core.domain.tts import TTSJob

    payload: dict[str, object] = {
        "id": str(uuid4()),
        "source_kind": TTSSourceKind.Inline,
        "source_path": None,
        "text_hash": "abc123",
        "text_preview": "hello",
        "voice": "af_heart",
        "speed": 1.0,
        "format": MediaFormat.MP3,
        "status": TTSStatus.Pending,
        "output_path": None,
        "segments_total": 0,
        "segments_done": 0,
        "error_message": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    payload.update(overrides)
    return TTSJob(**payload)


def _setting(**overrides: object):
    from avkit_core.domain.enums import SettingValueType
    from avkit_core.domain.settings import Setting

    payload: dict[str, object] = {
        "namespace": "downloader",
        "key": "quality",
        "value": "P1080",
        "value_type": SettingValueType.String,
        "updated_at": _now(),
    }
    payload.update(overrides)
    return Setting(**payload)


def _make_uow_factory(tmp_path: Path):
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory():
        return SqlAlchemyUnitOfWork(session_factory)

    return factory


def _imported_module_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def _annotation_token(value: object) -> str:
    if value is inspect.Signature.empty:
        return "empty"
    if isinstance(value, str):
        return value
    return getattr(value, "__name__", str(value)).replace("typing.", "")


def _signature_snapshot(func: object) -> tuple[tuple[object, ...], ...]:
    signature = inspect.signature(func)
    params = tuple(
        (
            name,
            parameter.kind,
            _annotation_token(parameter.annotation),
            parameter.default,
        )
        for name, parameter in signature.parameters.items()
    )
    return params + ((_annotation_token(signature.return_annotation),),)


def _assert_protocol_signatures(
    protocol_cls: type, impl_cls: type, method_names: tuple[str, ...]
) -> None:
    for name in method_names:
        protocol_sig = _signature_snapshot(getattr(protocol_cls, name))
        impl_sig = _signature_snapshot(getattr(impl_cls, name))
        assert impl_sig == protocol_sig, (
            f"{impl_cls.__name__}.{name} {impl_sig!r} != {protocol_sig!r}"
        )


@pytest.mark.integration
def test_ac_5_7_mapper_enums_paths_and_preview_truncation(tmp_path: Path) -> None:
    from avkit_core.domain.enums import QualityPreset
    from avkit_core.domain.tts import TEXT_PREVIEW_MAX as DOMAIN_PREVIEW_MAX
    from avkit_infra.database.mappers import download_job_from_row, tts_job_from_row, tts_job_to_row
    from avkit_infra.database.models import DownloadJobRow, TTSJobRow

    assert DOMAIN_PREVIEW_MAX == TEXT_PREVIEW_MAX
    job = _download_job(quality=QualityPreset.P720, file_path=Path("downloads/video.mp4"))
    uow_factory = _make_uow_factory(tmp_path)
    with uow_factory() as uow:
        uow.downloads.add(job)
    with uow_factory() as uow:
        loaded = uow.downloads.get(job.id)
    assert loaded is not None
    assert loaded.quality is QualityPreset.P720
    assert loaded.file_path == Path("downloads/video.mp4")
    assert type(loaded).__name__ == "DownloadJob"
    assert not hasattr(loaded, "_sa_instance_state")

    row = DownloadJobRow(
        id=job.id,
        url=job.url,
        video_id=job.video_id,
        title=job.title,
        quality="P1080",
        audio_only=False,
        audio_format="Default",
        status="Pending",
        progress=0.0,
        speed_bps=None,
        eta_seconds=None,
        file_size=None,
        file_path="downloads/video.mp4",
        error_message=None,
        queue_position=0,
        created_at=_now(),
        updated_at=_now(),
    )
    mapped = download_job_from_row(row)
    assert mapped.quality is QualityPreset.P1080
    assert mapped.file_path == Path("downloads/video.mp4")

    long_preview = "x" * (TEXT_PREVIEW_MAX + 1)
    tts = _tts_job(text_preview="hello")
    tts_row = tts_job_to_row(tts)
    tts_row.text_preview = long_preview
    truncated = tts_job_from_row(tts_row)
    assert len(truncated.text_preview) == TEXT_PREVIEW_MAX
    assert isinstance(tts_row, TTSJobRow)


@pytest.mark.integration
def test_ac_5_8_download_repo_order_delete_all_and_reset_failed(tmp_path: Path) -> None:
    from avkit_core.domain.enums import DownloadStatus
    from avkit_core.domain.errors import ConflictError
    from avkit_infra.database.repositories import SqlAlchemyDownloadRepository

    for name in DOWNLOAD_REPO_METHODS:
        assert callable(getattr(SqlAlchemyDownloadRepository, name))
    assert callable(SqlAlchemyDownloadRepository.has_video_id)

    first = _download_job(video_id="aaa11111111", queue_position=1, title="Second")
    second = _download_job(video_id="bbb22222222", queue_position=0, title="First")
    failed = _download_job(
        video_id="fail3333333",
        queue_position=2,
        status=DownloadStatus.Failed,
        progress=0.5,
        error_message="boom",
    )
    done = _download_job(
        video_id="done4444444",
        queue_position=3,
        status=DownloadStatus.Done,
        progress=1.0,
    )
    archive = _archive_entry(video_id="aaa11111111")
    uow_factory = _make_uow_factory(tmp_path)
    with uow_factory() as uow:
        uow.downloads.add(first)
        uow.downloads.add(second)
        uow.downloads.add(failed)
        uow.downloads.add(done)
        uow.archive.add(archive)
        ordered = uow.downloads.list_ordered()
        assert [job.video_id for job in ordered] == [
            "bbb22222222",
            "aaa11111111",
            "fail3333333",
            "done4444444",
        ]
        uow.downloads.reorder([first.id, second.id, failed.id, done.id])
        assert uow.downloads.has_video_id("aaa11111111") is True
        uow.downloads.reset_failed()
        with pytest.raises(ConflictError):
            done.reset_failed()

    with uow_factory() as uow:
        reset = uow.downloads.get(failed.id)
        untouched = uow.downloads.get(done.id)
        assert reset is not None
        assert reset.status is DownloadStatus.Pending
        assert reset.progress == 0.0
        assert reset.error_message is None
        assert untouched is not None
        assert untouched.status is DownloadStatus.Done
        reordered = uow.downloads.list_ordered()
        assert [job.id for job in reordered] == [first.id, second.id, failed.id, done.id]
        assert [job.queue_position for job in reordered] == [0, 1, 2, 3]
        uow.downloads.delete_all()

    with uow_factory() as uow:
        assert uow.downloads.list_ordered() == []
        assert uow.archive.get("youtube", "aaa11111111") is not None
        assert uow.downloads.has_video_id("aaa11111111") is False
        uow.downloads.add(first)
        uow.downloads.delete(first.id)

    with uow_factory() as uow:
        assert uow.downloads.get(first.id) is None


@pytest.mark.integration
def test_ac_5_9_archive_unique_is_idempotent(tmp_path: Path) -> None:
    from avkit_infra.database.repositories import SqlAlchemyArchiveRepository

    for name in ARCHIVE_REPO_METHODS:
        assert callable(getattr(SqlAlchemyArchiveRepository, name))
    entry = _archive_entry()
    duplicate = _archive_entry(title="Other title")
    uow_factory = _make_uow_factory(tmp_path)
    with uow_factory() as uow:
        uow.archive.add(entry)
        uow.archive.add(duplicate)
        listed = uow.archive.list()
    assert len(listed) == 1
    assert listed[0].extractor == "youtube"
    assert listed[0].video_id == "dQw4w9wgGc"
    with uow_factory() as uow:
        assert uow.archive.get("youtube", "missing") is None


@pytest.mark.integration
def test_ac_5_10_transcript_aggregate_cascade_and_counts(tmp_path: Path) -> None:
    from avkit_core.domain.enums import TranscriptItemStatus
    from avkit_infra.database.repositories import SqlAlchemyTranscriptRepository

    for name in TRANSCRIPT_REPO_METHODS:
        assert callable(getattr(SqlAlchemyTranscriptRepository, name))
    assert callable(SqlAlchemyTranscriptRepository.progress_counts)
    assert callable(SqlAlchemyTranscriptRepository.recompute_word_count)

    job = _transcript_job()
    other = _transcript_job(queue_position=1)
    pending = _transcript_item(job_id=job.id, video_id="ccc", word_count=3)
    done = _transcript_item(
        job_id=job.id,
        video_id="aaa",
        word_count=10,
        status=TranscriptItemStatus.Done,
        path=Path("raw/aaa.md"),
    )
    skipped = _transcript_item(
        job_id=job.id,
        video_id="bbb",
        word_count=1,
        status=TranscriptItemStatus.Skipped,
    )
    failed = _transcript_item(
        job_id=job.id,
        video_id="ddd",
        word_count=2,
        status=TranscriptItemStatus.Failed,
        error_message="no captions",
    )
    uow_factory = _make_uow_factory(tmp_path)
    with uow_factory() as uow:
        uow.transcripts.add_job(job)
        uow.transcripts.add_job(other)
        uow.transcripts.replace_items(job.id, [pending, done, skipped, failed])
        items = uow.transcripts.list_items(job.id)
        assert [item.video_id for item in items] == ["aaa", "bbb", "ccc", "ddd"]
        parent = uow.transcripts.get_job(job.id)
        assert parent is not None
        assert parent.video_count == 4
        assert uow.transcripts.count_items(job.id) == 4
        assert uow.transcripts.count_items_with_status(job.id, TranscriptItemStatus.Done) == 1
        counts = uow.transcripts.progress_counts(job.id)
        assert counts == {
            "total": 4,
            "done": 1,
            "skipped": 1,
            "failed": 1,
            "pending": 1,
        }
        uow.transcripts.recompute_word_count(job.id)
        parent = uow.transcripts.get_job(job.id)
        assert parent is not None
        assert parent.word_count == 16
        updated = _transcript_item(
            job_id=job.id,
            id=pending.id,
            video_id="ccc",
            word_count=7,
            status=TranscriptItemStatus.Done,
            path=Path("raw/ccc.md"),
        )
        uow.transcripts.save_item(updated)
        uow.transcripts.recompute_word_count(job.id)
        uow.transcripts.reorder_jobs([other.id, job.id])

    with uow_factory() as uow:
        parent = uow.transcripts.get_job(job.id)
        assert parent is not None
        assert parent.word_count == 20
        ordered = uow.transcripts.list_jobs_ordered()
        assert [row.id for row in ordered] == [other.id, job.id]
        uow.transcripts.delete_job(job.id)

    with uow_factory() as uow:
        assert uow.transcripts.get_job(job.id) is None
        assert uow.transcripts.list_items(job.id) == []
        assert uow.transcripts.get_job(other.id) is not None


@pytest.mark.integration
def test_ac_5_11_tts_repo_has_no_full_text_column(tmp_path: Path) -> None:
    from sqlalchemy import inspect

    from avkit_infra.database.engine import create_sqlite_engine, init_schema
    from avkit_infra.database.repositories import SqlAlchemyTTSJobRepository

    for name in TTS_REPO_METHODS:
        assert callable(getattr(SqlAlchemyTTSJobRepository, name))
    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    columns = {column["name"] for column in inspect(engine).get_columns("tts_jobs")}
    assert "text" not in columns
    job = _tts_job()
    uow_factory = _make_uow_factory(tmp_path)
    with uow_factory() as uow:
        uow.tts_jobs.add(job)
        uow.tts_jobs.save(
            _tts_job(
                id=job.id,
                text_hash=job.text_hash,
                text_preview=job.text_preview,
                voice=job.voice,
                segments_total=3,
                segments_done=1,
            )
        )
    with uow_factory() as uow:
        loaded = uow.tts_jobs.get(job.id)
        assert loaded is not None
        assert loaded.segments_done == 1
        uow.tts_jobs.delete(job.id)
    with uow_factory() as uow:
        assert uow.tts_jobs.get(job.id) is None


@pytest.mark.integration
def test_ac_5_12_settings_missing_none_and_namespace_replace(tmp_path: Path) -> None:
    from avkit_infra.database.repositories import SqlAlchemySettingsRepository

    for name in SETTINGS_REPO_METHODS:
        assert callable(getattr(SqlAlchemySettingsRepository, name))
    quality = _setting(namespace="downloader", key="quality", value="P1080")
    audio = _setting(namespace="downloader", key="audio_only", value="false")
    ui = _setting(namespace="ui", key="theme", value="dark")
    replacement = _setting(namespace="downloader", key="quality", value="P720")
    uow_factory = _make_uow_factory(tmp_path)
    with uow_factory() as uow:
        assert uow.settings.get("downloader", "quality") is None
        uow.settings.set(quality)
        uow.settings.set(audio)
        uow.settings.set(ui)
        uow.settings.set_namespace("downloader", [replacement])
    with uow_factory() as uow:
        assert uow.settings.get("downloader", "audio_only") is None
        loaded = uow.settings.get("downloader", "quality")
        assert loaded is not None
        assert loaded.value == "P720"
        assert uow.settings.get("ui", "theme") is not None
        namespaced = uow.settings.get_namespace("downloader")
        assert [item.key for item in namespaced] == ["quality"]


@pytest.mark.integration
def test_ac_5_13_model_mark_downloaded_and_list_downloaded(tmp_path: Path) -> None:
    from avkit_infra.database.models import ModelVariantRow
    from avkit_infra.database.repositories import SqlAlchemyModelRepository

    for name in MODEL_REPO_METHODS:
        assert callable(getattr(SqlAlchemyModelRepository, name))
    assert callable(SqlAlchemyModelRepository.list_downloaded)
    payload = b"onnx-weights"
    model_path = tmp_path / "kokoro-onnx-fp16.onnx"
    model_path.write_bytes(payload)
    uow_factory = _make_uow_factory(tmp_path)
    with uow_factory() as uow:
        catalog = uow.models.list_catalog()
        assert {item.id for item in catalog} == set(SEED_VARIANT_IDS)
        uow.models.mark_downloaded("kokoro-onnx-fp16", model_path)
        missing_path = tmp_path / "does-not-exist.onnx"
        uow.models.mark_downloaded("kokoro-onnx-int8", missing_path)
    with uow_factory() as uow:
        downloaded = uow.models.list_downloaded()
        assert {item.id for item in downloaded} == {"kokoro-onnx-fp16", "kokoro-onnx-int8"}
        fp16 = uow.models.get("kokoro-onnx-fp16")
        int8 = uow.models.get("kokoro-onnx-int8")
        assert fp16 is not None
        assert fp16.is_downloaded is True
        assert fp16.path == model_path
        assert fp16.size_bytes == len(payload)
        assert int8 is not None
        assert int8.is_downloaded is True
        assert int8.size_bytes == SEED_SIZE_BYTES[3]
        models_source = (
            REPO_ROOT
            / "packages"
            / "infrastructure"
            / "src"
            / "avkit_infra"
            / "database"
            / "models.py"
        ).read_text(encoding="utf-8")
        variant_block = models_source.split("class ModelVariantRow")[1].split("class ")[0]
        assert "is_loaded" not in variant_block
        assert "device" not in variant_block
        _ = ModelVariantRow


@pytest.mark.integration
def test_ac_5_14_uow_commits_on_clean_exit_rolls_back_on_error(tmp_path: Path) -> None:
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    uow_factory = _make_uow_factory(tmp_path)
    persisted = _download_job(video_id="persist00111")
    rolled_back = _download_job(video_id="rollback0022")
    with uow_factory() as uow:
        for name in UOW_ATTRIBUTES:
            assert getattr(uow, name) is not None
        session = uow.downloads.session
        assert uow.archive.session is session
        assert uow.transcripts.session is session
        assert uow.tts_jobs.session is session
        assert uow.settings.session is session
        assert uow.models.session is session
        uow.downloads.add(persisted)
    with uow_factory() as uow:
        assert uow.downloads.get(persisted.id) is not None
        closed_session = uow.downloads.session
    assert closed_session.in_transaction() is False
    with pytest.raises(RuntimeError, match="boom"):
        with uow_factory() as uow:
            uow.downloads.add(rolled_back)
            raise RuntimeError("boom")
    with uow_factory() as uow:
        assert uow.downloads.get(rolled_back.id) is None
    assert SqlAlchemyUnitOfWork.__name__ == "SqlAlchemyUnitOfWork"


@pytest.mark.integration
def test_ac_5_16_core_has_no_infra_imports() -> None:
    core_src = REPO_ROOT / "packages" / "core" / "src"
    hits: list[str] = []
    for path in core_src.rglob("*.py"):
        imported = _imported_module_names(path)
        forbidden = sorted(imported & INFRA_NAMES)
        if forbidden:
            hits.append(f"{path.relative_to(REPO_ROOT)}:{forbidden}")
    assert hits == []


@pytest.mark.integration
def test_ac_5_17_finite_progress_round_trips_nan_rejected(tmp_path: Path) -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_infra.database.mappers import download_job_from_row
    from avkit_infra.database.models import DownloadJobRow

    job = _download_job(progress=0.25)
    uow_factory = _make_uow_factory(tmp_path)
    with uow_factory() as uow:
        uow.downloads.add(job)
    with uow_factory() as uow:
        loaded = uow.downloads.get(job.id)
    assert loaded is not None
    assert loaded.progress == 0.25
    with pytest.raises(ValidationError):
        _download_job(progress=float("nan"))
    row = DownloadJobRow(
        id=job.id,
        url=job.url,
        video_id=job.video_id,
        title=job.title,
        quality="P1080",
        audio_only=False,
        audio_format="Default",
        status="Pending",
        progress=float("nan"),
        speed_bps=None,
        eta_seconds=None,
        file_size=None,
        file_path=None,
        error_message=None,
        queue_position=0,
        created_at=_now(),
        updated_at=_now(),
    )
    with pytest.raises(ValidationError):
        download_job_from_row(row)
    assert math.isnan(row.progress)


@pytest.mark.integration
def test_ac_5_18_storage_protocol_signatures_and_concrete_extras() -> None:
    from avkit_core.ports.storage import (
        ArchiveRepository,
        DownloadRepository,
        ModelRepository,
        SettingsRepository,
        TranscriptRepository,
        TTSJobRepository,
        UnitOfWork,
    )
    from avkit_infra.database.repositories import (
        SqlAlchemyArchiveRepository,
        SqlAlchemyDownloadRepository,
        SqlAlchemyModelRepository,
        SqlAlchemySettingsRepository,
        SqlAlchemyTranscriptRepository,
        SqlAlchemyTTSJobRepository,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    _assert_protocol_signatures(
        DownloadRepository, SqlAlchemyDownloadRepository, DOWNLOAD_REPO_METHODS
    )
    _assert_protocol_signatures(
        ArchiveRepository, SqlAlchemyArchiveRepository, ARCHIVE_REPO_METHODS
    )
    _assert_protocol_signatures(
        TranscriptRepository, SqlAlchemyTranscriptRepository, TRANSCRIPT_REPO_METHODS
    )
    _assert_protocol_signatures(TTSJobRepository, SqlAlchemyTTSJobRepository, TTS_REPO_METHODS)
    _assert_protocol_signatures(
        SettingsRepository, SqlAlchemySettingsRepository, SETTINGS_REPO_METHODS
    )
    _assert_protocol_signatures(ModelRepository, SqlAlchemyModelRepository, MODEL_REPO_METHODS)
    _assert_protocol_signatures(UnitOfWork, SqlAlchemyUnitOfWork, UOW_METHODS)

    reset = inspect.signature(SqlAlchemyDownloadRepository.reset_failed)
    assert list(reset.parameters) == ["self"]
    setter = inspect.signature(SqlAlchemySettingsRepository.set)
    assert list(setter.parameters) == ["self", "setting"]
    mark = inspect.signature(SqlAlchemyModelRepository.mark_downloaded)
    assert list(mark.parameters) == ["self", "variant_id", "path"]

    assert hasattr(SqlAlchemyDownloadRepository, "has_video_id")
    assert hasattr(SqlAlchemyTranscriptRepository, "progress_counts")
    assert hasattr(SqlAlchemyTranscriptRepository, "recompute_word_count")
    assert hasattr(SqlAlchemyModelRepository, "list_downloaded")
    assert not hasattr(DownloadRepository, "has_video_id")
    assert not hasattr(TranscriptRepository, "progress_counts")
    assert not hasattr(ModelRepository, "list_downloaded")

