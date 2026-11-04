---
project: "2026-08-19-p2-persistence-io"
date: "2026-08-19"
source: "docs/build-plan/02-infrastructure.md"
meus: ["MEU-5", "MEU-8"]
status: "complete"
template_version: "2.0"
---

# Implementation Plan: Phase 2 Persistence + Local IO

> **Project**: `2026-08-19-p2-persistence-io`
> **Build Plan Section(s)**: [02-infrastructure.md](../../../build-plan/02-infrastructure.md) §Database, §ORM/UoW, §Filesystem, §Media
> **Status**: `complete`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 2 — MEU-5 → MEU-8

---

## Goal

Stand up `packages/infrastructure` as the first Phase 2 adapters: SQLite WAL + seven-table UoW (MEU-5) and `FilesystemPort` + subprocess `MediaPort` (MEU-8). Implement the **frozen** Phase 1 Protocols in `avkit_core.ports` without mutating them. No YouTube/transcript/Kokoro/HF adapters. No services, REST, MCP, or GUI.

av-kit remains a **job queue**. SQLite stores job records and file pointers. Transcript bodies, PCM, video bytes, cookies, and tokens are not columns.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "2026-08-19 Step 6 re-eval: graphify-out/graph.json and graphify-out-research/graph.json still absent; Headroom has no approved disposition. Continue TDD against 02-infrastructure.md plus frozen Phase 1 Protocols."
  human_message_reference: null
```

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-5 | `.agent/context/handoffs/2026-08-19-p2-persistence-io-MEU-5-handoff.md` |
| MEU-8 | `.agent/context/handoffs/2026-08-19-p2-persistence-io-MEU-8-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-19-p2-persistence-io-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB` (expected count **2**). Do not restate the wildcard here.

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-5a | MEU-5 Red: package/workspace/layout tests | — | `shared` | `C:/Temp/av-kit/fail-to-pass-meu-5-scaffold.txt` |
| WP-5b | MEU-5 Green: `packages/infrastructure` + uv member | WP-5a | `compact_continue` | `packages/infrastructure/`; compact then re-read `task.md` |
| WP-5c | MEU-5 Red: engine PRAGMA + seven tables + seed | WP-5b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-5-schema.txt` |
| WP-5d | MEU-5 Green: engine/models/migrations/seed | WP-5c | `compact_continue` | `avkit_infra/database/{engine,models,migrations}.py` |
| WP-5e | MEU-5 Red: mapper/repo/UoW integration | WP-5d | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-5-uow.txt` |
| WP-5f | MEU-5 Green: mappers/repositories/unit_of_work | WP-5e | `compact_continue` | `avkit_infra/database/{mappers,repositories,unit_of_work}.py` |
| WP-8a | MEU-8 Red: filesystem compile-only + atomic write | WP-5f | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-8-fs.txt` |
| WP-8b | MEU-8 Green: `filesystem/writer.py` | WP-8a | `compact_continue` | `avkit_infra/filesystem/writer.py` |
| WP-8c | MEU-8 Red: FFmpeg probe-order + mocked subprocess | WP-8b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-8-media.txt` |
| WP-8d | MEU-8 Green: `media/adapter.py` | WP-8c | `compact_continue` | `avkit_infra/media/adapter.py` |

## User Review Required

None. Method-name mapping (Phase 2 prose → frozen Protocol) and extra concrete capabilities are sourced below. No remaining product fork.

**This section is content for the review loop, NOT a cue to stop now.**

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `INFRA_LAYOUT` | `database/{engine,models,mappers,repositories,unit_of_work,migrations}.py`, `filesystem/writer.py`, `media/adapter.py` | this plan |
| `DEFERRED_ADAPTER_DIRS` | `youtube/`, `transcript/`, `tts/`, `model_manager/` | grouping Session 3 / MEU-6,7,9 |
| `TABLES` | `download_jobs`, `download_archive`, `transcript_jobs`, `transcript_items`, `tts_jobs`, `model_variants`, `settings` | `02-infrastructure.md` lines 90–225 |
| `FORBIDDEN_TABLES` | `jobs`, `job_artifacts`, `queue_runtime`, `sabr_state`, `download_job_parents` | Spec line 92 |
| `FORBIDDEN_MODEL_COLUMNS` | `is_loaded`, `device` on `model_variants` | Spec line 92 |
| `PRAGMA_LOCKS` | `journal_mode=WAL`, `busy_timeout=5000`, `foreign_keys=ON` | Spec lines 59–61 |
| `APP_DATA_WINDOWS` | `%LOCALAPPDATA%/av-kit` | Spec line 57 |
| `APP_DATA_POSIX` | `~/.avkit/` | Spec line 57 |
| `SEED_VARIANT_IDS` | `kokoro-pt-fp32`, `kokoro-onnx-fp32`, `kokoro-onnx-fp16`, `kokoro-onnx-int8` | Spec lines 208–211 |
| `SEED_SIZE_BYTES` | `326*1024*1024`, `326*1024*1024`, `163*1024*1024`, `87*1024*1024` (INT8 midpoint of 82–92 MB) | Spec typical sizes |
| `TEXT_PREVIEW_MAX` | `200` | frozen `avkit_core.domain.tts` |
| `UOW_ATTRIBUTES` | `downloads`, `archive`, `transcripts`, `tts_jobs`, `settings`, `models` | frozen `UnitOfWork` |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-19-p2-persistence-io` | this plan (MEU `execution_plan` value; no trailing slash) |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-19-p2-persistence-io/` | phase `"2"` `execution_plans` list entry |
| `HUB_NEXT_AFTER` | `/create-plan p2-external-adapters` | hub Next after this project’s H1-3 |
| `PHASE_ID` | `'2'` | this session’s `phases[].id` |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` (exactly one match) | Codex r3 F1 |
| `STORAGE_PROTOCOL_SIGNATURES` | Exact `inspect.signature` tables for every method on frozen `DownloadRepository`, `ArchiveRepository`, `TranscriptRepository`, `TTSJobRepository`, `SettingsRepository`, `ModelRepository`, and `UnitOfWork` commit/rollback/`__enter__`/`__exit__` — parameter names, kinds, annotations, and returns copied from `packages/core/src/avkit_core/ports/storage.py` | frozen `storage.py`; AC-5.18 |
| `DOWNLOAD_REPO_METHODS` | `add`, `get`, `list_ordered`, `save`, `reorder`, `delete`, `delete_all`, `reset_failed` | frozen `DownloadRepository` |
| `ARCHIVE_REPO_METHODS` | `get`, `add`, `list` | frozen `ArchiveRepository` |
| `TRANSCRIPT_REPO_METHODS` | `add_job`, `get_job`, `list_jobs_ordered`, `save_job`, `reorder_jobs`, `delete_job`, `replace_items`, `list_items`, `save_item`, `count_items`, `count_items_with_status` | frozen `TranscriptRepository` |
| `TTS_REPO_METHODS` | `add`, `get`, `save`, `delete` | frozen `TTSJobRepository` |
| `SETTINGS_REPO_METHODS` | `get`, `set`, `get_namespace`, `set_namespace` | frozen `SettingsRepository` |
| `MODEL_REPO_METHODS` | `list_catalog`, `get`, `mark_downloaded` | frozen `ModelRepository` |
| `CONCRETE_EXTRAS` | `SqlAlchemyDownloadRepository.has_video_id`; `SqlAlchemyTranscriptRepository.progress_counts`, `recompute_word_count`; `SqlAlchemyModelRepository.list_downloaded` | Phase 2 capability table; **not** Protocol mutations |
| `FILESYSTEM_PORT_METHODS` | `write_text_atomic`, `write_progress_export`, `ensure_channel_dirs`, `write_audio_wav`, `read_text` | frozen `FilesystemPort` |
| `MEDIA_PORT_METHODS` | `is_available`, `ffmpeg_version`, `convert`, `probe` | frozen `MediaPort` |
| `CONVERT_OPTIONS_FIELDS` | `codec`, `bitrate_kbps`, `sample_rate`, `channels` | frozen `ConvertOptions` |
| `MEDIA_INFO_FIELDS` | `duration`, `container`, `video_codec`, `audio_codec`, `sample_rate`, `channels` | frozen `MediaInfo` |
| `TTS_MP3_CONVERT_OPTIONS` | `ConvertOptions(codec="libmp3lame", bitrate_kbps=80, sample_rate=44100, channels=1)` | Spec line 425; `_shared_patterns.md` §4 |
| `COMPILE_PARENT_NAMES` | `frozenset({"raw", "compiled"})` | Spec `read_text` compile-only |
| `COMPILE_SUFFIX` | `.md` | Spec |
| `PROGRESS_EXPORT_FILENAME` | `progress.json` | Spec `write_progress_export` |
| `PROGRESS_EXPORT_KEY` | `video_ids_done` | Spec function arg; derived export only |
| `FFMPEG_PROBE_STEPS` | configured path if file exists → `{install}/resources/extra/ffmpeg/ffmpeg.exe` → `PATH` | Spec line 424; `07-distribution.md` lines 159–163 |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-19-p2-persistence-io-MEU-*-handoff.md` | this plan |
| `SCAN_PLACEHOLDER_ARGS` | `rg -n -e TODO -e FIXME -e NotImplementedError -e SabrDetectedError -e assert packages/infrastructure/src` | Verification Plan §4 |
| `SCAN_SOUNDFILE_ARGS` | `rg -n -e soundfile -e yt_dlp -e youtube_transcript_api -e huggingface_hub packages/infrastructure/src` | Verification Plan §4 |
| `SCAN_CORE_INFRA_ARGS` | `rg -n -e sqlalchemy -e yt_dlp -e fastapi -e youtube_transcript_api -e huggingface_hub -e soundfile packages/core/src` | p1 `SCAN_INFRA_ARGS` reuse |
| `SCAN_G36_ARGS` | `rg -n -e pytest.mark.skip -e pytest.mark.xfail -e pytest.skip tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py` | Verification Plan §4 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | completion-preflight |

## Implementation locks (planning resolutions)

| Topic | Lock | Source |
|-------|------|--------|
| Protocol names | Implement frozen `packages/core` Protocols **as written**. Phase 2 prose `list_queued`/`update`/`reset_failed(id)` map to `list_ordered`/`save`/`reset_failed()` + `save(job.reset_failed())`. Do not edit `avkit_core.ports`. | Spec “names may tighten; behavior may not”; Local Canon p1 reflection RULE-3 / Next Day Outline; frozen `storage.py` |
| `reset_failed()` | Protocol takes no id: bulk-apply domain `DownloadJob.reset_failed()` to every `Failed` row in one UoW transaction. Single-id path is `save(job.reset_failed())`. | Frozen Protocol; domain `download.py:115-123`; Phase 2 table line 252 |
| `mark_downloaded` | Protocol is `(variant_id, path)` only. Set `is_downloaded=True`, store path string; set `size_bytes` from `path.stat().st_size` when the file exists, else keep catalog size. | Frozen `ModelRepository`; Phase 2 line 286 |
| `CONCRETE_EXTRAS` | Extra methods on SQLAlchemy classes only. Tests assert they exist on the concrete type. Do not add them to Protocols this session. | Phase 2 capability table; grouping “no domain-layout changes” |
| Enum storage | Store `StrEnum.name` (equals `.value` for Phase 1 members). | Spec type mapping line 80 |
| Paths | Store `str(path)` as given; do not rewrite to URI. | Spec line 85 |
| Datetime | `DateTime(timezone=True)` UTC. | Spec line 86 |
| Engine | `sqlite+pysqlite` file URL. `connect_args={"check_same_thread": False}`. Connect event: autocommit dance then `PRAGMA_LOCKS` ([SQLAlchemy 2 sqlite dialect](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html)). | Spec 54–62; Research-backed SQLAlchemy docs |
| Test DB | `tmp_path / "avkit.db"` file — not `:memory:` — so WAL is observable. | Spec WAL; SQLAlchemy `:memory:` uses a different pool |
| `resolve_app_data` | `AVKIT_APP_DATA` if set, else Windows `APP_DATA_WINDOWS`, else `APP_DATA_POSIX`. Production `create_engine` uses `{app_data}/avkit.db`. Tests pass an explicit path and must not write under real LocalAppData. | Spec line 57; Local Canon `05-mcp-server.md` / `07-distribution.md` `AVKIT_APP_DATA` |
| Schema v1 | `Base.metadata.create_all` then `migrations.py` empty append-only list (repeat = no-op). No Alembic. | Spec 62–64; Local Canon `DESIGN_PROPOSAL.md` §5 |
| Seed | After create_all, upsert `SEED_VARIANT_IDS` with `is_downloaded=False`. Idempotent. MEU-9 consumes rows; does not own CREATE. | Spec 204–211 vs MEU-9 slug note |
| Settings defaults | Not pre-inserted. Missing key → `None` from repo. | Spec line 225 |
| UoW | One `Session` per enter; all `UOW_ATTRIBUTES` bound to it. `__exit__` with `exc_type is None` calls `commit()` then closes; `__exit__` with an exception calls `rollback()` then closes. Explicit `commit()` remains on the Protocol for mid-unit flushes (Phase 3) but is **not** required for the success oracle. | Spec 288–302 |
| `replace_items` | Same session: delete existing items, insert set, set parent `video_count`. Transaction = UoW. | Spec 270; atomicity corollary |
| Archive add | Unique `(extractor, video_id)`; insert ignore on conflict (idempotent Done). | Spec 260 |
| `list_items` | Stable order: `video_id` ASC. | Spec 271 |
| `delete_all` | `DELETE FROM download_jobs` only. | Spec 118, 251 |
| Cascade | `transcript_items.job_id` FK ON DELETE CASCADE. | Spec 155 |
| No second model | Repositories return domain dataclasses. Tests fail if a service-facing method returns an ORM instance. | Spec 231–233 |
| FFmpeg adapter ctor | `FFmpegAdapter(*, configured_path: Path \| None = None, bundle_path: Path \| None = None)`. Does **not** open UoW. Step 1 = configured file exists. | Spec 424; hexagonal ports |
| Probe cache | `is_available` probes once and caches. | Spec 424 |
| Binary missing | `is_available` False; `convert`/`probe` raise `FFmpegNotFoundError`. Do not swallow. | Spec 428 |
| `ffmpeg_version` | `ffmpeg -version` first line, or `None` if unavailable. No parallel helper. | Spec 430 |
| `probe` | Subprocess sibling `ffprobe` (same dir as resolved `ffmpeg`) with `-print_format json -show_format -show_streams`. Map JSON → `MEDIA_INFO_FIELDS`. ([ffprobe writers](https://ffmpeg.org/ffprobe-all.html)) | Spec 426; Phase 7 bundles ffprobe; Research-backed |
| `convert` | `ffmpeg` subprocess; `-y`; apply `CONVERT_OPTIONS_FIELDS` (`-c:a`, `-b:a {n}k`, `-ar`, `-ac`). Tests use `TTS_MP3_CONVERT_OPTIONS`. | Spec 425 |
| Live FFmpeg | Default suite **mocks** subprocess. Live binary only if `@pytest.mark.integration` **and** binary present; do not skip-pass the mocked tests (G36). | Spec Testing table 512 |
| Atomic write | Same-directory temp + flush + `os.replace`. IO failures → `FilesystemError`. ([os.replace](https://docs.python.org/3/library/os.html#os.replace)) | Spec 457 |
| `read_text` | Resolve path; parent name in `COMPILE_PARENT_NAMES`; suffix `COMPILE_SUFFIX`; file size `> max_bytes` → `FilesystemError`; else return text. Never TTS `source_path`. | Spec 461; Phase 1 lines 486–489 |
| `write_progress_export` | Atomic write `{output_dir}/progress.json` body `{"video_ids_done": [...]} `. Adapter has **no** read of that file. | Spec 458–459; Phase 1 conflict |
| WAV | stdlib `wave` only. 1-D `float` in `[-1, 1]` → int16 PCM; int16 passthrough. Else `ValidationError`. No `soundfile`. | Spec 460; Phase 1 line 462 |
| structlog | Module keys `database`, `filesystem`, `media`. No `print`. | Spec 484–486 |
| numpy / sqlalchemy | `avkit-infra` depends on `avkit-core`, `sqlalchemy>=2`, `structlog`. Workspace member `packages/infrastructure`. | Spec layout; Research-backed SQLAlchemy 2 |
| Types | No `assert` for user-visible failures. Domain constructors still validate on mapper output. | Local Canon code-quality; Python `-O` strips assert |
| Closeout validator | `tools/validate_closeout_artifacts.py` **not** in tree. Marker receipts (p1 pattern). | Local Canon `commands.md` 16–17 |
| MEU gate | pytest integration + domain regression + pyright/ruff on `packages/infrastructure` + named scans. Not `validate_codebase.py`. | Spec 519–526; commands.md |
| Production entrypoints (PR-8) | `init_schema` / `SqlAlchemyUnitOfWork.__enter__`; `FilesystemAdapter.read_text` / `write_text_atomic`; `FFmpegAdapter.is_available` / `convert` / `probe`. Controls are not test-only. | Spec Goal |
| Adversarial probes | Round-trip NaN progress is rejected by domain on map-in (p1 RULE-1). Unhashable settings namespace still `ValidationError` (RULE-2). | p1 Next Session Design Rules |
| `unit_label` hardening | Optional leftover from p1 exec r2 — **out of this project**. | p1 residual; grouping Session 2 |

### ORM column census (must match Spec tables)

Implement every column in `02-infrastructure.md` lines 94–225. Negative oracle: `FORBIDDEN_TABLES` and `FORBIDDEN_MODEL_COLUMNS` absent from `models.py` metadata.

`download_jobs.quality/audio_format/status` store enum names. `settings.key` is leaf-only (domain already rejects `.`).

## Proposed Changes

### MEU-5 `infra-sqlite-uow`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| SQLite file `{app_data}/avkit.db` (and test `tmp_path`) | SQLAlchemy `models.py` + domain dataclasses on map-out | `TABLES` columns; enum names; UUID `String(36)` except `model_variants.id` TEXT PK | Extra tables/columns forbidden (`FORBIDDEN_TABLES`, `FORBIDDEN_MODEL_COLUMNS`) |
| Settings row write | Domain `Setting` then `SettingsRepository.set` | `SETTING_NAMESPACES`; leaf `key`; `value` serialized str | Unexpected ORM columns → fail census |
| Env `AVKIT_APP_DATA` | `resolve_app_data()` | Non-empty path string | Unknown env ignored |

No REST/MCP/UI. Invalid mapped values raise existing `ValidationError` on domain construct (not 422 until MEU-14).

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-5.1 | unit | Workspace member `packages/infrastructure`; package import `avkit_infra`; `INFRA_LAYOUT` paths exist; `DEFERRED_ADAPTER_DIRS` absent. | Spec layout 24–45; grouping Session 2 | `youtube/` present or member missing → fail |
| AC-5.2 | unit | `avkit-infra` depends on `avkit-core`, `sqlalchemy>=2`, `structlog`. Root pyright/ruff/pytest `pythonpath` include `packages/infrastructure/src`. | Spec; Local Canon root `pyproject.toml` | Import sqlalchemy from infra fails → fail |
| AC-5.3 | integration | File engine applies `PRAGMA_LOCKS`; `check_same_thread is False`. Observable: `PRAGMA journal_mode` returns `wal` (case-insensitive). | Spec 54–62; Research-backed SQLAlchemy sqlite dialect | `journal_mode=delete` or FK off → fail |
| AC-5.4 | integration | `init_schema` creates exactly `TABLES`. `FORBIDDEN_TABLES` and `FORBIDDEN_MODEL_COLUMNS` absent. | Spec 90–92, 192–202 | `jobs` table or `is_loaded` column → fail |
| AC-5.5 | integration | First boot seeds `SEED_VARIANT_IDS` with `is_downloaded=False` and `SEED_SIZE_BYTES`. Second boot does not duplicate. | Spec 204–211 | Missing `kokoro-onnx-fp32` or duplicate PK → fail |
| AC-5.6 | unit | `migrations.py` exposes an empty apply-all list; invoking apply twice is a no-op. | Spec 64; DESIGN_PROPOSAL §5 | Alembic ini in this package → fail |
| AC-5.7 | unit | Mapper: enum name ↔ enum; path str ↔ `Path`; `text_preview` truncated to `TEXT_PREVIEW_MAX` before domain construct. | Spec 235 | preview 201 chars stored uncut → fail |
| AC-5.8 | integration | `DownloadRepository` exposes `DOWNLOAD_REPO_METHODS`. `list_ordered` is `ORDER BY queue_position ASC`. `delete_all` leaves archive. `reset_failed()` bulk-resets Failed via domain helper. Concrete `has_video_id` in `CONCRETE_EXTRAS`. | Spec 241–253; frozen Protocol | `delete_all` wipes archive or `reset_failed` on Done raises nothing when called via domain path incorrectly — archive row missing after delete_all → fail |
| AC-5.9 | integration | Archive unique `(extractor, video_id)`; second `add` is idempotent (no exception, one row). `list` returns entries. | Spec 255–261, 129 | duplicate insert raises uncaught IntegrityError → fail |
| AC-5.10 | integration | Transcript aggregate: `delete_job` cascades items; `replace_items` replaces set and sets `video_count`; unique `(job_id, video_id)`; `count_items` / `count_items_with_status` match; concrete `progress_counts` keys `{total, done, skipped, failed, pending}`; `recompute_word_count` writes SUM onto parent. | Spec 263–274 | orphan items after delete_job → fail |
| AC-5.11 | integration | TTS repo `TTS_REPO_METHODS`; no full-text column on `tts_jobs`. | Spec 170–190, 276–278 | `text` column in metadata → fail |
| AC-5.12 | integration | Settings `SETTINGS_REPO_METHODS`; `get` missing → `None`; `set_namespace` upserts that namespace only. | Spec 215–225, 280–282 | missing key returns a silent default row → fail |
| AC-5.13 | integration | Model repo `MODEL_REPO_METHODS`; `mark_downloaded` updates path + flag; `list_downloaded` only `is_downloaded=True`. Never write `is_loaded`. | Spec 284–286 | `is_loaded` assignment exists → fail |
| AC-5.14 | integration | `SqlAlchemyUnitOfWork` has `UOW_ATTRIBUTES`. **Success oracle:** `with uow:` adds a job and does **not** call `commit()`; after clean exit a **fresh** UoW `get()` returns the row. **Failure oracle:** raise inside `with`; a fresh UoW `get()` returns `None`. Same session object for all repos during the unit; session is closed after exit. | Spec 288–302 | clean `with` that never calls `commit()` loses the row, or exception still persists the row → fail |
| AC-5.15 | unit | `resolve_app_data` honors `AVKIT_APP_DATA`, else platform defaults. Default db filename `avkit.db`. | Spec 57; Local Canon Phase 5/7 | ignoring `AVKIT_APP_DATA` → fail |
| AC-5.16 | unit | `SCAN_CORE_INFRA_ARGS` still clean on `packages/core`. Infra may import sqlalchemy. | Phase 1 Goal | sqlalchemy in core → fail |
| AC-5.17 | integration | Mapping a `DownloadJob` with finite progress round-trips. Constructing domain with `NaN` still raises `ValidationError` (p1 F1). | p1 RULE-1 | NaN survives mapper into DB bind → fail |
| AC-5.18 | unit | Every frozen storage Protocol method on the SQLAlchemy implementations matches `STORAGE_PROTOCOL_SIGNATURES` (`inspect.signature`, parameter names/kinds/annotations/returns). `CONCRETE_EXTRAS` are additional methods, not Protocol replacements (`reset_failed` stays zero-arg; `set` takes `Setting`; `mark_downloaded` takes `(variant_id, path)` only). | Frozen `storage.py`; Local Canon p1 RULE-3 | `reset_failed(id)`, `set(namespace, key, …)`, or `mark_downloaded(..., size_bytes)` as the Protocol-facing signature → fail |

**Control binding (AC-5.3, AC-5.14):** observable = PRAGMA result / row presence after a **fresh** UoW. Chain = `init_schema` / `SqlAlchemyUnitOfWork.__enter__` → `__exit__` (commit or rollback). Negative: exception path must append **zero** durable jobs; success path must persist **without** an in-block `commit()` call.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Seven tables / no STI | Spec | `02-infrastructure.md` 90–92 |
| WAL + busy_timeout + FK | Spec + Research-backed | SQLAlchemy connect event + autocommit dance for FK |
| `check_same_thread=False` | Spec | Explicit `connect_args` even if file-DB default is False |
| No Alembic | Spec + Local Canon | Empty `migrations.py` |
| Protocol vs Phase 2 names | Local Canon | Frozen Protocols; extras on concrete classes |
| Catalog seed owner | Spec | Database first boot (MEU-5), not MEU-9 |
| `AVKIT_APP_DATA` | Local Canon | Phase 5/7 override, implemented now so tests and later API share one resolver |
| INT8 seed size | Research-backed midpoint | 87 MiB within spec 82–92 MB |
| UoW pattern | Spec | Check Zorivest pattern in-tree if present; otherwise SQLAlchemy 2 `sessionmaker` + context manager (no second invent) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `pyproject.toml` | modify | Workspace member; pythonpath/pyright/ruff src; sqlalchemy/structlog via infra package |
| `packages/infrastructure/pyproject.toml` | new | `avkit-infra` hatchling |
| `packages/infrastructure/src/avkit_infra/__init__.py` | new | Package |
| `packages/infrastructure/src/avkit_infra/database/engine.py` | new | URL, PRAGMA, session factory, `resolve_app_data` |
| `packages/infrastructure/src/avkit_infra/database/models.py` | new | Seven tables |
| `packages/infrastructure/src/avkit_infra/database/mappers.py` | new | ORM ↔ domain |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | new | Protocol impls + `CONCRETE_EXTRAS` |
| `packages/infrastructure/src/avkit_infra/database/unit_of_work.py` | new | `SqlAlchemyUnitOfWork` |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | new | Empty append-only list |
| `tests/integration/test_sqlite_uow.py` | new | `@pytest.mark.integration` AC-5.* |

### MEU-8 `infra-filesystem-media`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Filesystem write paths | `FilesystemAdapter` + domain `FilesystemError`/`ValidationError` | compile-only read; atomic replace | Extra read APIs (`read_bytes`) forbidden |
| `progress.json` export | JSON object with `PROGRESS_EXPORT_KEY` only | list[str] video ids | Extra keys forbidden in the export body |
| `ConvertOptions` | frozen dataclass | `CONVERT_OPTIONS_FIELDS` | Unexpected kwargs → `TypeError` |
| FFmpeg binary resolution | `FFmpegAdapter` ctor paths + PATH | `FFMPEG_PROBE_STEPS` | Do not read settings DB |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-8.1 | integration | `write_text_atomic` writes via same-dir temp + `os.replace`. Observable: final file content. IO error → `FilesystemError`. | Spec 457; Research-backed `os.replace` | Direct truncate-in-place without replace (test by injecting failing replace) → fail if error swallowed |
| AC-8.2 | integration | `write_progress_export` creates `PROGRESS_EXPORT_FILENAME` with only `PROGRESS_EXPORT_KEY`. Adapter provides no load/resume API. | Spec 458–459; Phase 1 conflict | Adapter method that reads progress.json exists → fail |
| AC-8.3 | integration | `ensure_channel_dirs` creates `raw/` and `compiled/` under `output_dir`. | Spec 459 | missing `compiled/` → fail |
| AC-8.4 | integration | `write_audio_wav` uses stdlib `wave`; round-trips int16; float32 `[-1,1]` encodes. Invalid shape → `ValidationError`. | Spec 460 | `import soundfile` in infra → fail (`SCAN_SOUNDFILE_ARGS`) |
| AC-8.5 | integration | `read_text(path, *, max_bytes)`: parent in `COMPILE_PARENT_NAMES`, suffix `COMPILE_SUFFIX`, size `<= max_bytes`. Else `FilesystemError`. `max_bytes` keyword-only (frozen signature). | Spec 461; Phase 1 486–489 | `raw/../secrets.txt` after resolve, or `.txt`, or oversize, or TTS-like `input.txt` → `FilesystemError` |
| AC-8.6 | unit | `is_available` follows `FFMPEG_PROBE_STEPS` with injected `configured_path` / `bundle_path`; caches first result. | Spec 424; 07-dist 159–163 | PATH used when configured file exists → fail |
| AC-8.7 | unit | Missing binary: `is_available` False; `convert`/`probe` raise `FFmpegNotFoundError`. | Spec 428 | `convert` raises `FileNotFoundError` built-in → fail |
| AC-8.8 | unit | `ffmpeg_version` parses mocked `-version` stdout or returns `None`. | Spec 430 | parallel `get_version` helper on the adapter that is not the port method → fail |
| AC-8.9 | unit | `convert` invokes ffmpeg subprocess with `-y` and `CONVERT_OPTIONS_FIELDS` mapped to `-c:a`/`-b:a`/`-ar`/`-ac`. Tests pass `TTS_MP3_CONVERT_OPTIONS`. | Spec 425; `_shared_patterns.md` §4 | bitrate 80 not present in argv when options say 80 → fail |
| AC-8.10 | unit | `probe` uses ffprobe JSON and fills `MEDIA_INFO_FIELDS` (nullable codecs). | Spec 426; Research-backed ffprobe JSON | leftover `codec` field on returned DTO → fail |
| AC-8.11 | unit | No `ConversionJob` type or table. Default tests mock subprocess (no live ffmpeg required). | Spec 420, 512 | live ffmpeg required for AC-8.9 → fail |
| AC-8.12 | unit | Adapter implements `MEDIA_PORT_METHODS` and `FILESYSTEM_PORT_METHODS` with frozen signatures (`inspect.signature`, including `read_text` keyword-only `max_bytes`). | p1 RULE-3; frozen ports | missing `ffmpeg_version` → fail |

**Control binding (AC-8.5, AC-8.7):** observable = exception type / file bytes written. Chain = `FilesystemAdapter.read_text` and `FFmpegAdapter.convert` (the production entrypoints Phase 3 will call). Negative: disallowed path writes **zero** new file bytes; missing ffmpeg appends **zero** output media files.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Compile-only `read_text` without `output_dir` arg | Spec + this lock | Parent-name + suffix after `Path.resolve()` |
| progress.json shape | Spec function args | `{video_ids_done: list[str]}` only |
| FFmpeg without settings DB | Spec hexagonal | ctor-injected paths |
| ffprobe vs ffmpeg -i | Local Canon + Research-backed | Phase 7 bundles ffprobe; official JSON writer |
| WAV dtype | Research-backed | stdlib `wave` + int16 PCM |
| Probe cache | Spec | instance attribute, first call wins |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/src/avkit_infra/filesystem/writer.py` | new | `FilesystemAdapter` |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | new | `FFmpegAdapter` |
| `tests/integration/test_filesystem_media.py` | new | `@pytest.mark.integration` + mocked subprocess unit-style tests in the same file marked integration (tmp_path is real IO) |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| `youtube/adapter.py` yt-dlp | deferred | MEU-6 | grouping Session 3; `02-infrastructure.md` §YouTube |
| `transcript/adapter.py` | deferred | MEU-7 | grouping Session 3; §Transcript |
| `tts/adapter.py` + `model_manager/` (HF download/sideload) | deferred | MEU-9 | grouping Session 3; MEU-9 seed/download — catalog **rows** still seeded here |
| Download/Transcript/TTS/Settings services | deferred | MEU-10–13 | `03-service-layer.md`; grouping Session 4 |
| REST / OpenAPI | deferred | MEU-14–16 | `04-rest-api.md` |
| MCP | deferred | MEU-17–18 | `05-mcp-server.md`; MCP never opens SQLite (A12) |
| GUI / E2E | deferred | MEU-19–23 | `06-gui.md` |
| Bundled ffmpeg.exe in installer | deferred | MEU-25 | `07-distribution.md`; MEU-8 only implements probe order |
| Alembic | out-of-scope | — | Spec lines 64–64 omit Alembic |
| Persist `QueueRuntime` / `SABRStatus` / `is_loaded` | out-of-scope | — | Spec 469–472; Phase 1 session-only |
| Unified `jobs` STI / `ConversionJob` / `ModelFetchJob` | out-of-scope | — | Spec 473–479 |
| Store transcript text / PCM / cookies / tokens | out-of-scope | — | Spec 88, 474–477 |
| Read `progress.json` to resume | out-of-scope | — | Spec 476; Phase 1 conflict |
| Live YouTube / Hugging Face in default suite | out-of-scope | — | Spec 515 |
| Mutate `avkit_core.ports` signatures | out-of-scope | — | p1 approved freeze; grouping Session 2 |
| `ProgressSnapshot.unit_label` type-before-membership | out-of-scope | — | p1 exec r2 non-blocking residual; not Session 2 grouping |
| GUI Step 4A | out-of-scope | — | No `ui/` files |
| `tools/validate_closeout_artifacts.py` port | out-of-scope | — | `commands.md` 16–17; no scheduled tools MEU |

## BUILD_PLAN.md Audit

This project does **not** rewrite Phase 2–7 contracts. Hub work at execution **task 13 + H1-3** (not a count-only grep):

1. `meu_status.py update MEU-5|MEU-8 <status> --plan PLAN_FOLDER`
2. Add `PLAN_FOLDER_SLASH` to phase `"2"` `execution_plans` in `.agent/context/meu-status.yaml` (SSOT; then `render` — do not hand-edit AUTOGEN tables).
3. Rewrite hub `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`. Preserve the Session 1 plan link.
4. Prove the post-state with Verification Plan **§7** (`SSOT_PLAN_BOUND` / `SSOT_READY` / `SSOT_APPROVED`). A YAML/hub substring or a match-count of `p2-persistence-io` is **not** a passing oracle.

## Verification Plan

Classify every command through [`.agent/docs/output-evidence-policy.md`](../../../.agent/docs/output-evidence-policy.md). `rtk proxy` for these exact-evidence receipts.

### 1. Domain regression (must stay green)

```powershell
rtk proxy uv run pytest tests/unit/test_domain.py -x --tb=short -v *> C:/Temp/av-kit/pytest-domain.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-domain.txt | Select-Object -Last 40; exit $code
```

### 2. Infrastructure integration tests

```powershell
rtk proxy uv run pytest tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py -x --tb=short -v *> C:/Temp/av-kit/pytest-infra.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-infra.txt | Select-Object -Last 40; exit $code
```

### 3. Pyright + ruff infrastructure

```powershell
rtk proxy uv run pyright packages/infrastructure/ *> C:/Temp/av-kit/pyright-infra.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/pyright-infra.txt | Select-Object -Last 40; exit $code }; rtk proxy uv run ruff check packages/infrastructure/ *> C:/Temp/av-kit/ruff-infra.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ruff-infra.txt | Select-Object -Last 40; exit $code
```

### 4. Named scans (`SCAN_*` owners — rg 0/1 are census results)

`rg` exit `0` = hits, `1` = no match, `>1` = tool failure. Clean scans treat `1` as PASS; fail on leftover hits or `$code -gt 1`.

```powershell
rtk proxy rg -n -e TODO -e FIXME -e NotImplementedError -e SabrDetectedError -e assert packages/infrastructure/src *> C:/Temp/av-kit/anti-placeholder-infra.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-placeholder-infra.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-placeholder-infra.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_PLACEHOLDER clean'; exit 0
```

```powershell
rtk proxy rg -n -e soundfile -e yt_dlp -e youtube_transcript_api -e huggingface_hub packages/infrastructure/src *> C:/Temp/av-kit/anti-soundfile-infra.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-soundfile-infra.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-soundfile-infra.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_SOUNDFILE clean'; exit 0
```

```powershell
rtk proxy rg -n -e sqlalchemy -e yt_dlp -e fastapi -e youtube_transcript_api -e huggingface_hub -e soundfile packages/core/src *> C:/Temp/av-kit/anti-infra-core.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-infra-core.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-infra-core.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_CORE_INFRA clean'; exit 0
```

```powershell
rtk proxy rg -n -e pytest.mark.skip -e pytest.mark.xfail -e pytest.skip tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py *> C:/Temp/av-kit/g36-skip-scan.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/g36-skip-scan.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/g36-skip-scan.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_G36 clean'; exit 0
```

### 5. MEU status render

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code
```

### 6. Closeout structural receipts (substitute for missing `validate_closeout_artifacts.py`)

Handoff markers (filter derived from `HANDOFF_GLOB`; expected count 2):

```powershell
rtk proxy pwsh -NoProfile -Command { $files=@(Get-ChildItem -Path '.agent/context/handoffs' -Filter '2026-08-19-p2-persistence-io-MEU-*-handoff.md'); if ($files.Count -ne 2) { Write-Error ('expected 2 handoffs, got '+$files.Count); exit 1 }; foreach ($f in $files) { foreach ($pattern in @('Acceptance Criteria','CACHE BOUNDARY','FAIL_TO_PASS','Changed Files')) { if (-not (Select-String -Path $f.FullName -Pattern $pattern -Quiet)) { Write-Error ('missing '+$pattern+' in '+$f.Name); exit 1 } } }; 'PASS: handoff markers' } *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code
```

AC-set integrity:

```powershell
rtk proxy pwsh -NoProfile -Command { $planAcs=@(Select-String -Path docs/execution/plans/2026-08-19-p2-persistence-io/implementation-plan.md -Pattern 'AC-[0-9]+(?:\.[0-9]+)?' -AllMatches).Matches.Value; $files=@(Get-ChildItem -Path '.agent/context/handoffs' -Filter '2026-08-19-p2-persistence-io-MEU-*-handoff.md'); $handoffAcs=@(); foreach ($f in $files) { $handoffAcs += @(Select-String -Path $f.FullName -Pattern 'AC-[0-9]+(?:\.[0-9]+)?' -AllMatches).Matches.Value }; $missing=@(Compare-Object ($planAcs | Sort-Object -Unique) ($handoffAcs | Sort-Object -Unique) | Where-Object SideIndicator -eq '<='); if ($missing) { $missing; exit 1 }; 'PASS: complete AC set' } *> C:/Temp/av-kit/handoff-ac-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-ac-check.txt; exit $code
```

Reflection markers (`REFLECTION_MARKERS`):

```powershell
rtk proxy pwsh -NoProfile -Command { $path='docs/execution/reflections/2026-08-19-p2-persistence-io-reflection.md'; $patterns=@('Friction Log','Execution Trace','Pattern Extraction','Patterns to KEEP','Next Session Design Rules','RULE-','Efficiency Metrics','Rule Adherence','Instruction Coverage','schema: v1','sections:','loaded:','decisive_rules:'); foreach ($pattern in $patterns) { if (-not (Select-String -Path $path -Pattern $pattern -Quiet)) { Write-Error ('missing reflection pattern: '+$pattern); exit 1 } }; 'PASS: reflection markers' } *> C:/Temp/av-kit/reflection-structure.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/reflection-structure.txt; exit $code
```

Metrics (require a row containing `p2-persistence-io`):

```powershell
rtk proxy pwsh -NoProfile -Command { $p='docs/execution/metrics.md'; if (-not (Test-Path $p)) { exit 1 }; if (-not (Select-String -Path $p -Pattern 'p2-persistence-io' -Quiet)) { Write-Error 'missing p2-persistence-io metrics row'; exit 1 }; Get-Content $p -Tail 5; 'PASS: metrics row' } *> C:/Temp/av-kit/metrics-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/metrics-check.txt; exit $code
```

### 7. SSOT post-state assertions (F1 — substring greps are not oracles)

Shared Python locals: `PLAN` = `PLAN_FOLDER`; `SLASH` = `PLAN_FOLDER_SLASH`; `NEXT` = `HUB_NEXT_AFTER`. Load SSOT via `tools.meu_status.model.load` (parsed YAML, not a raw-text search).

**Bound checks** (consumed by `SSOT_PLAN_BOUND` and `SSOT_READY`):

1. The phase whose `id == PHASE_ID` (`'2'`) has `SLASH` in its `execution_plans` list.
2. **No other phase** lists `SLASH` in `execution_plans` (blocks a Phase-3-only false pass).
3. `MEU-5` and `MEU-8` each have `execution_plan == PLAN`.
4. `docs/BUILD_PLAN.md` has exactly one `HUB_NEXT_FIELD` and its value equals `NEXT`.

**SSOT_PLAN_BOUND** (task 13): bound checks only.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p2-persistence-io'; SLASH=PLAN+'/'; NEXT='/create-plan p2-external-adapters'; data=load(); p2=next(p for p in data['phases'] if str(p['id'])=='2'); eps=list(p2.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 2 execution_plans missing PLAN_FOLDER_SLASH'); bad=next((p for p in data['phases'] if str(p['id'])!='2' and SLASH in list(p.get('execution_plans') or [])), None); bad is not None and sys.exit('PLAN_FOLDER_SLASH in phase '+str(bad['id'])); miss=next((k for k in ('MEU-5','MEU-8') if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in ('MEU-5','MEU-8') if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

**SSOT_READY** (H1-3): same bound checks, plus both MEUs `status == ready_for_review`, then `render --check`.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p2-persistence-io'; SLASH=PLAN+'/'; NEXT='/create-plan p2-external-adapters'; data=load(); p2=next(p for p in data['phases'] if str(p['id'])=='2'); eps=list(p2.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 2 execution_plans missing PLAN_FOLDER_SLASH'); bad=next((p for p in data['phases'] if str(p['id'])!='2' and SLASH in list(p.get('execution_plans') or [])), None); bad is not None and sys.exit('PLAN_FOLDER_SLASH in phase '+str(bad['id'])); miss=next((k for k in ('MEU-5','MEU-8') if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in ('MEU-5','MEU-8') if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); st=next((k for k in ('MEU-5','MEU-8') if get_meu(data,k).get('status')!='ready_for_review'), None); st is not None and sys.exit(st+' status='+str(get_meu(data,st).get('status'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_READY')" *> C:/Temp/av-kit/ssot-ready.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/ssot-ready.txt; exit $code }; rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-ready.txt; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code
```

**SSOT_APPROVED** (H2-2): both MEUs `status == approved` and `execution_plan == PLAN` (parsed YAML).

```powershell
rtk proxy uv run python -c "import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p2-persistence-io'; data=load(); miss=next((k for k in ('MEU-5','MEU-8') if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in ('MEU-5','MEU-8') if get_meu(data,k).get('execution_plan')!=PLAN or get_meu(data,k).get('status')!='approved'), None); wrong is not None and sys.exit(wrong+' status='+str(get_meu(data,wrong).get('status'))+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); print('PASS: SSOT_APPROVED')" *> C:/Temp/av-kit/ssot-approved.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-approved.txt; exit $code
```

### N. OpenAPI Drift Check

**Skipped.** `packages/api/` is not created. Basis: Out of Scope → MEU-14–16.

## Open Questions

None remaining. Forks researched and promoted to Implementation locks / sufficiency tables.

## Research References

- [SQLAlchemy 2.0 SQLite dialect — PRAGMA / check_same_thread / connect events](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html)
- [SQLite WAL](https://www.sqlite.org/wal.html)
- [Python `os.replace`](https://docs.python.org/3/library/os.html#os.replace)
- [Python `wave`](https://docs.python.org/3/library/wave.html)
- [ffprobe writers / JSON](https://ffmpeg.org/ffprobe-all.html)
- Spec: `docs/build-plan/02-infrastructure.md`, frozen `docs/build-plan/01-domain-layer.md` ports
- Local Canon: `_inspiration/DESIGN_PROPOSAL.md` §5, `_inspiration/_shared_patterns.md` §4, `docs/build-plan/07-distribution.md` FFmpeg, `.agent/docs/commands.md` 16–17
- Grouping: Session 2 MEU-5 + MEU-8 only
- Carry-forward: `docs/execution/reflections/2026-08-18-p1-domain-foundation-reflection.md` RULE-1–3
- Harness: `.agent/context/harness.local.md` (`plan_to_exec_gate: reviewer-auto`, `fresh_worker: none`)

## Explicit stop conditions

1. Plan-review round cap (3) without `approved` — HARD STOP (`create-plan` §5d).
2. Execution-review round cap (6) without `approved` — HARD STOP.
3. All independent-reviewer rungs unavailable — wait for Mat; never self-review.
4. Human approval required before any `git commit` / push / deploy.
5. Do **not** run product pytest/pyright/ruff **before** this plan is `approved` (GUARDRAILS SIGN 1). Static `Test-Path` / `rg` / `--help` only if a review loop fights about a missing tool.

## TDD / FAIL_TO_PASS

Tests first per slice (WP-5a/c/e, WP-8a/c). Save red receipts under `C:/Temp/av-kit/fail-to-pass-meu-{N}-*.txt`. Do not edit assertions to go green (G36). Red must fail for the AC reason (M5), not collection `ERROR`.
