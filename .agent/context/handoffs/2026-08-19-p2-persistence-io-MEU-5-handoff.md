---
date: "2026-08-19"
project: "p2-persistence-io"
meu: "MEU-5"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-19-p2-persistence-io/implementation-plan.md"
build_plan_section: "bp02s2.1"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-18-p1-domain-foundation-MEU-4-handoff.md"
---

# Handoff: 2026-08-19-p2-persistence-io-MEU-5-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-5 — SQLite WAL engine, seven-table schema, catalog seed, mappers, repositories, `SqlAlchemyUnitOfWork`
**Build Plan Section**: `docs/build-plan/02-infrastructure.md` §Database + ORM/UoW
**Predecessor**: Session 1 MEU-4 (frozen `avkit_core.ports.storage`)

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-5.1 | unit | Workspace member; `avkit_infra`; `INFRA_LAYOUT`; no `DEFERRED_ADAPTER_DIRS` | Spec layout 24–45 | `test_ac_5_1_workspace_layout_and_no_deferred_adapters` | ✅ |
| AC-5.2 | unit | `avkit-core`, `sqlalchemy>=2`, `structlog`; pythonpath/pyright/ruff include infra | Spec; Local Canon | `test_ac_5_2_infra_dependencies_and_tool_paths` | ✅ |
| AC-5.3 | integration | File engine `PRAGMA_LOCKS`; `check_same_thread is False`; journal `wal` | Spec 54–62 | `test_ac_5_3_file_engine_applies_pragma_locks` | ✅ |
| AC-5.4 | integration | `init_schema` creates exactly `TABLES`; forbidden tables/columns absent | Spec 90–92 | `test_ac_5_4_init_schema_creates_exactly_seven_tables` | ✅ |
| AC-5.5 | integration | Seed `SEED_VARIANT_IDS` + `SEED_SIZE_BYTES`; second boot no duplicate | Spec 204–211 | `test_ac_5_5_catalog_seed_is_idempotent` | ✅ |
| AC-5.6 | unit | Empty `MIGRATIONS`; apply twice is no-op; no Alembic | Spec 64 | `test_ac_5_6_migrations_empty_apply_is_noop` | ✅ |
| AC-5.7 | unit | Mapper enum/path; `text_preview` truncated to 200 | Spec 235 | `test_ac_5_7_mapper_enums_paths_and_preview_truncation` | ✅ |
| AC-5.8 | integration | `DOWNLOAD_REPO_METHODS`; `list_ordered`; `delete_all` leaves archive; bulk `reset_failed()`; `has_video_id` | Spec 241–253; frozen Protocol | `test_ac_5_8_download_repo_order_delete_all_and_reset_failed` | ✅ |
| AC-5.9 | integration | Archive unique key; second add idempotent; `list` | Spec 255–261 | `test_ac_5_9_archive_unique_is_idempotent` | ✅ |
| AC-5.10 | integration | Cascade delete; `replace_items`; counts; `progress_counts`; `recompute_word_count` | Spec 263–274 | `test_ac_5_10_transcript_aggregate_cascade_and_counts` | ✅ |
| AC-5.11 | integration | TTS `TTS_REPO_METHODS`; no `text` column | Spec 170–190 | `test_ac_5_11_tts_repo_has_no_full_text_column` | ✅ |
| AC-5.12 | integration | Settings get missing → `None`; `set_namespace` replaces that namespace only | Spec 215–225 | `test_ac_5_12_settings_missing_none_and_namespace_replace` | ✅ |
| AC-5.13 | integration | `mark_downloaded`; `list_downloaded`; no `is_loaded` | Spec 284–286 | `test_ac_5_13_model_mark_downloaded_and_list_downloaded` | ✅ |
| AC-5.14 | integration | Clean `with` persists without in-block `commit()`; exception rolls back; shared session; closed after exit | Spec 288–302 | `test_ac_5_14_uow_commits_on_clean_exit_rolls_back_on_error` | ✅ |
| AC-5.15 | unit | `resolve_app_data` honors `AVKIT_APP_DATA` then platform defaults; `avkit.db` | Spec 57 | `test_ac_5_15_resolve_app_data_env_and_defaults` | ✅ |
| AC-5.16 | unit | Core still has no infra imports | Phase 1 Goal | `test_ac_5_16_core_has_no_infra_imports` | ✅ |
| AC-5.17 | integration | Finite progress round-trips; NaN still `ValidationError` | p1 RULE-1 | `test_ac_5_17_finite_progress_round_trips_nan_rejected` | ✅ |
| AC-5.18 | unit | `inspect.signature` matches frozen Protocols; `CONCRETE_EXTRAS` extra only | Frozen `storage.py`; p1 RULE-3 | `test_ac_5_18_storage_protocol_signatures_and_concrete_extras` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| `test_ac_5_1_workspace_layout_and_no_deferred_adapters` | `assert ['packages/core'] == ['packages/core', 'packages/infrastructure']` | passed | `tests/integration/test_sqlite_uow.py` |
| `test_ac_5_3_file_engine_applies_pragma_locks` | `ImportError: SQLITE_CONNECT_ARGS` | passed | `tests/integration/test_sqlite_uow.py` |
| `test_ac_5_7_mapper_enums_paths_and_preview_truncation` | `ImportError: download_job_from_row` | passed | `tests/integration/test_sqlite_uow.py` |

Receipts: `C:/Temp/av-kit/fail-to-pass-meu-5-scaffold.txt`, `fail-to-pass-meu-5-schema.txt`, `fail-to-pass-meu-5-uow.txt`.

AC-5.14 closed-session oracle: SQLAlchemy 2 `Session.is_active` is True when `_transaction is None` (ready to autobegin). Tests assert `in_transaction() is False` after `__exit__`; `sessionmaker(..., close_resets_only=False)`.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `uv run pytest tests/unit/test_domain.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py` | 0 | 74 passed |
| `uv run pyright packages/infrastructure/ packages/core/` | 0 | 0 errors |
| `uv run ruff check packages/infrastructure/ packages/core/` | 0 | All checks passed |
| `uv sync --all-packages` | 0 | sqlalchemy 2.0.52, structlog 26.1.0 |

### Quality Gate Results

```
pyright: 0 errors, 0 warnings
ruff: 0 violations
pytest: 74 passed
anti-placeholder: 0 matches
SCAN_CORE_INFRA: 0 matches
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `pyproject.toml` | modified | workspace | member + pythonpath/pyright/ruff src |
| `packages/infrastructure/pyproject.toml` | new | full | `avkit-infra` hatchling |
| `packages/infrastructure/src/avkit_infra/database/engine.py` | new | full | WAL pragmas, seed, `resolve_app_data` |
| `packages/infrastructure/src/avkit_infra/database/models.py` | new | full | seven tables |
| `packages/infrastructure/src/avkit_infra/database/mappers.py` | new | full | ORM ↔ domain |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | new | full | Protocol impls + extras |
| `packages/infrastructure/src/avkit_infra/database/unit_of_work.py` | new | full | commit on clean `__exit__` |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | new | full | empty `MIGRATIONS` |
| `tests/integration/test_sqlite_uow.py` | new | full | AC-5.* |
| `tests/unit/test_domain.py` | modified | AC-1.1 | members include infrastructure |

```diff
+[tool.uv.workspace]
+members = ["packages/core", "packages/infrastructure"]
+
+class SqlAlchemyUnitOfWork:
+    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
+        if exc_type is None:
+            self.commit()
+        else:
+            self.rollback()
```

Frozen `packages/core/src/avkit_core/ports/storage.py` was not mutated.

---

## Codex Validation Report

_Left blank for reviewer agent._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | — | — | — | — |

### Verdict

`pending` — independent Codex `/execution-critical-review`

---

## Corrections Applied (2026-08-19)

**Findings resolved**: 0/0 (pre-review)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| — | — | — | — |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| YouTube / transcript / TTS / model_manager adapters | Session 3 grouping | MEU-6, MEU-7, MEU-9 | grouping Session 3 `p2-external-adapters` |
| `ProgressSnapshot.unit_label` TypeError leftover | p1 residual; out of Session 2 | none (optional leftover) | p1 exec r2 note |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | Initial MEU-5 handoff |
| Submitted for review | 2026-08-19 | cursor-grok-4.6 | Pending Codex exec review |
