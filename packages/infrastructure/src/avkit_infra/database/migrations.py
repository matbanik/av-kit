"""Append-only ALTER/CREATE list. Schema v1 is models.py CREATE TABLE."""

from __future__ import annotations

from typing import Any

import structlog

from avkit_core.domain.download import BLOCKER_REASONS
from avkit_core.domain.enums import DownloadStatus

log = structlog.get_logger(module="database")

_QUALITY_BLOCKED_REASON_SQL = BLOCKER_REASONS[DownloadStatus.QualityBlocked].replace("'", "''")

MIGRATIONS: list[str] = [
    """
    CREATE TABLE IF NOT EXISTS conversion_jobs (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        kind TEXT NOT NULL,
        input_path TEXT NOT NULL,
        output_path TEXT NOT NULL,
        display_name TEXT NOT NULL,
        preset_id TEXT,
        cq INTEGER,
        scale_height INTEGER,
        audio_mode TEXT,
        gpu_encoder TEXT,
        in_ms INTEGER,
        out_ms INTEGER,
        copy_mode TEXT,
        stream_index INTEGER,
        status TEXT NOT NULL,
        progress FLOAT NOT NULL,
        speed_bps FLOAT,
        eta_seconds INTEGER,
        file_size INTEGER,
        duration_seconds FLOAT,
        width INTEGER,
        height INTEGER,
        error_message TEXT,
        queue_position INTEGER NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        gpu_preference TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_conversion_jobs_queue_position "
    "ON conversion_jobs (queue_position)",
    "CREATE INDEX IF NOT EXISTS ix_conversion_jobs_status ON conversion_jobs (status)",
    """
    CREATE TABLE IF NOT EXISTS capture_shots (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        original_path TEXT NOT NULL,
        annotated_path TEXT,
        sidecar_path TEXT,
        display_name TEXT NOT NULL,
        width INTEGER NOT NULL,
        height INTEGER NOT NULL,
        file_size INTEGER NOT NULL,
        source TEXT NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        UNIQUE (original_path)
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_capture_shots_created_at ON capture_shots (created_at)",
    """
    CREATE TABLE IF NOT EXISTS capture_requests (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        status TEXT NOT NULL,
        shot_id VARCHAR(36),
        created_at DATETIME NOT NULL,
        expires_at DATETIME NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_capture_requests_status ON capture_requests (status)",
    "CREATE INDEX IF NOT EXISTS ix_capture_requests_expires_at ON capture_requests (expires_at)",
]

# Append-only data backfills, applied after MIGRATIONS by apply_migrations(). Kept
# separate because every MIGRATIONS entry is self-guarding DDL ("IF NOT EXISTS"),
# which no UPDATE can be; a data statement is guarded by its table's existence
# instead, so a bare engine is a legitimate no-op.
DATA_MIGRATIONS: list[str] = [
    # Legacy QualityBlocked rows shipped with no explanation, or with a stale one that
    # named a quality the row no longer carries. Idempotent: the predicate stops matching
    # once the canonical reason is in place. Rows in any other status are never rewritten,
    # so a Failed job's real error text survives.
    "UPDATE download_jobs SET error_message = '"
    + _QUALITY_BLOCKED_REASON_SQL
    + "' WHERE status = 'QualityBlocked'"
    + " AND (error_message IS NULL OR error_message <> '"
    + _QUALITY_BLOCKED_REASON_SQL
    + "')",
]


# Columns added after a table first shipped. create_all and CREATE TABLE IF NOT EXISTS
# both leave an existing table alone, and ADD COLUMN has no IF NOT EXISTS, so each entry
# runs only when PRAGMA table_info says the column is missing. A table that does not exist
# yet is skipped: create_all builds it with every column.
COLUMN_MIGRATIONS: list[tuple[str, str, str]] = [
    ("conversion_jobs", "gpu_preference", "TEXT"),
    ("download_jobs", "received_height", "INTEGER"),
]


def _data_migration_table(statement: str) -> str:
    """Return the table a data migration writes to (`UPDATE <table> SET ...`)."""
    parts = statement.split()
    if len(parts) < 2:
        raise ValueError(f"data migration is not a table statement: {statement!r}")
    return parts[1]


def apply_migrations(engine: Any) -> None:
    """Apply each migration SQL statement. Repeats are no-ops via IF NOT EXISTS."""
    if not MIGRATIONS:
        log.debug("migrations.apply", count=0)
        return
    if engine is None:
        return
    with engine.begin() as connection:
        for statement in MIGRATIONS:
            connection.exec_driver_sql(statement)
        rows = connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type = 'table'")
        tables = {str(row[0]) for row in rows}
        applied_data = 0
        for statement in DATA_MIGRATIONS:
            if _data_migration_table(statement) not in tables:
                continue
            connection.exec_driver_sql(statement)
            applied_data += 1
        added_columns = 0
        for table, column, sql_type in COLUMN_MIGRATIONS:
            if table not in tables:
                continue
            existing = connection.exec_driver_sql(f"PRAGMA table_info({table})")
            if column in {str(row[1]) for row in existing}:
                continue
            connection.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")
            added_columns += 1
    log.info(
        "migrations.apply",
        count=len(MIGRATIONS),
        data_count=applied_data,
        added_columns=added_columns,
    )
