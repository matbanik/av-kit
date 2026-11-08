"""SQLite URL, WAL pragmas, session factory, and app-data resolver."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from sqlite3 import Connection as SQLiteConnection

import structlog
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from avkit_core.domain.errors import ValidationError
from avkit_infra.database.migrations import apply_migrations
from avkit_infra.database.models import Base, ModelVariantRow

log = structlog.get_logger(module="database")

SQLITE_CONNECT_ARGS: dict[str, bool] = {"check_same_thread": False}
DB_FILENAME = "avkit.db"
SEED_VARIANTS: tuple[tuple[str, str, str, str, int], ...] = (
    ("kokoro-pt-fp32", "PyTorch FP32", "PyTorch", "FP32", 326 * 1024 * 1024),
    ("kokoro-onnx-fp32", "ONNX FP32", "ONNX", "FP32", 326 * 1024 * 1024),
    ("kokoro-onnx-fp16", "ONNX FP16", "ONNX", "FP16", 163 * 1024 * 1024),
    ("kokoro-onnx-int8", "ONNX INT8", "ONNX", "INT8", 87 * 1024 * 1024),
)


def user_home() -> Path:
    """Return the current user home directory (patch point for tests)."""
    return Path.home()


def resolve_app_data() -> Path:
    """Resolve `{app_data}`: `AVKIT_APP_DATA`, else platform default."""
    override = os.environ.get("AVKIT_APP_DATA", "").strip()
    if override:
        return Path(override)
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
        if not local_app_data:
            raise ValidationError("LOCALAPPDATA is required on Windows")
        return Path(local_app_data) / "av-kit"
    return user_home() / ".avkit"


def default_db_path() -> Path:
    """Return `{app_data}/avkit.db`."""
    return resolve_app_data() / DB_FILENAME


def sqlite_url(db_path: Path) -> str:
    """Build a `sqlite+pysqlite` file URL from an absolute path."""
    resolved = db_path.resolve()
    return "sqlite+pysqlite:///" + resolved.as_posix()


def _register_sqlite_pragmas(engine: Engine) -> None:
    @event.listens_for(engine, "connect")
    def _on_connect(dbapi_connection: SQLiteConnection, _connection_record: object) -> None:
        previous = dbapi_connection.isolation_level
        dbapi_connection.isolation_level = None
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()
            dbapi_connection.isolation_level = previous


def create_sqlite_engine(db_path: Path) -> Engine:
    """Create a file-backed SQLite engine with WAL, timeout, and FKs."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        sqlite_url(db_path),
        connect_args=SQLITE_CONNECT_ARGS,
        # A SQL error's text then holds no bound value, such as a title (D-357).
        hide_parameters=True,
    )
    _register_sqlite_pragmas(engine)
    log.info("engine.created")
    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a sessionmaker bound to `engine`."""
    return sessionmaker(bind=engine, expire_on_commit=False, close_resets_only=False)


def _seed_model_variants(engine: Engine) -> None:
    from sqlalchemy.dialects.sqlite import insert

    rows = [
        {
            "id": variant_id,
            "name": name,
            "format": fmt,
            "precision": precision,
            "size_bytes": size_bytes,
            "path": None,
            "is_downloaded": False,
        }
        for variant_id, name, fmt, precision, size_bytes in SEED_VARIANTS
    ]
    statement = insert(ModelVariantRow).values(rows).on_conflict_do_nothing(index_elements=["id"])
    with engine.begin() as connection:
        connection.execute(statement)
    log.info("catalog.seeded", count=len(SEED_VARIANTS))


def init_schema(engine: Engine) -> None:
    """Create schema v1, apply migrations, seed the four catalog variants."""
    Base.metadata.create_all(engine)
    apply_migrations(engine)
    _seed_model_variants(engine)
    log.info("schema.initialized")
