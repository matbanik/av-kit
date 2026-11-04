---
project: "2026-08-24-p8-conversion-engine"
date: "2026-08-24"
source: "docs/build-plan/08-video-conversion.md"
meus: ["MEU-28", "MEU-29", "MEU-30"]
status: "in_progress"
template_version: "2.0"
---

# Implementation Plan: Phase 8 Conversion Engine

> **Project**: `2026-08-24-p8-conversion-engine`
> **Build Plan Section(s)**: [08-video-conversion.md](../../../build-plan/08-video-conversion.md) §Domain + §Infrastructure + §Service layer
> **Status**: `in_progress`
> **Grouping**: [2026-08-24-p8-video-conversion-session-grouping.md](../../../../.agent/context/grouping/2026-08-24-p8-video-conversion-session-grouping.md) Session 13 — MEU-28 → MEU-29 → MEU-30

---

## Goal

Stand up the **conversion engine** only: domain types + additive `MediaPort`, eighth table `conversion_jobs` + FFmpeg encode/cut/extract/gpu/progress, and `ConversionService` sequential queue. USER_EXPLICIT 2026-08-24 `/create-plan Phase 8` starts the Phase 8 pathway after p7 `approved`. Grouping **does not** pack MEU-31–33 into this plan (fan-out exception). Do not invent MEU IDs. Do not start Session 8c (MEU-27). Do not rewrite FastAPI routers, MCP tools, or Convert-page GUI here.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (Glob 0). Headroom has no approved disposition. Planning/execution use spec + source reads and P0 exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-28 | `.agent/context/handoffs/` + `HANDOFFS[0]` |
| MEU-29 | `.agent/context/handoffs/` + `HANDOFFS[1]` |
| MEU-30 | `.agent/context/handoffs/` + `HANDOFFS[2]` |

Rolling implementation review: `.agent/context/handoffs/2026-08-24-p8-conversion-engine-implementation-critical-review.md`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `3`. Filenames: `HANDOFFS` in `named-sets.json` (do not restate).

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-28a | MEU-28 Red: `TEST_DOMAIN_CONV` AC-28.1–28.14 + expand `MEDIA_PORT_METHODS` / `QUEUE_NAMES` / `SETTING_NAMESPACES` expected sets in `TEST_DOMAIN`. Write `API_BASELINE`. Pass `RED_ORACLE_CHECK -Meu 28`. Red pytest **must not** use `-x` (oracle needs all AC failed titles). Do not add `conversion.py` yet. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-28-py.txt`; `API_BASELINE`; compact then re-read `task.md` |
| WP-28b | Green MEU-28: enums, `ConversionJob`, DTOs, ports, errors, `QUEUE_NAMES`, `SETTING_NAMESPACES`, `UNIT_LABELS`. Do not implement FFmpeg encode. | WP-28a | `compact_continue` | `packages/core/src/avkit_core/domain/conversion.py`; compact then re-read `task.md` |
| WP-28c | MEU-28 scoped gate + `HANDOFF_28` | WP-28b | `compact_continue` | `HANDOFF_28` |
| WP-29a | MEU-29 Red: `TEST_INFRA_CONV` AC-29.1–29.14 (`RED_COUNT_29`). Pass `RED_ORACLE_CHECK -Meu 29`. Do not add `conversion_jobs` yet. | WP-28c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-29-py.txt` |
| WP-29b | Green MEU-29: table + UoW + `MEDIA_PORT_ADDITIVE` + progress parse + `CANCEL_HOOK`. `convert()` unchanged. Expand `TEST_MEDIA_INT` `MEDIA_PORT_METHODS` to KEEP+ADDITIVE. | WP-29a | `compact_continue` | `packages/infrastructure/src/avkit_infra/media/adapter.py`; `models.py` |
| WP-29c | MEU-29 scoped gate + `HANDOFF_29` | WP-29b | `compact_continue` | `HANDOFF_29` |
| WP-30a | MEU-30 Red: `TEST_SVC_CONV` AC-30.1–30.13 (`RED_COUNT_30`). Pass `RED_ORACLE_CHECK -Meu 30`. Do not add `ConversionService` yet. | WP-29c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-30-py.txt` |
| WP-30b | Green MEU-30: `ConversionService` + converter `SETTINGS_KEY_TABLE` + FakeMedia/FakeUoW extensions. | WP-30a | `compact_continue` | `packages/core/src/avkit_core/services/conversion.py` |
| WP-30c | MEU-30 scoped gate + `HANDOFF_30` | WP-30b | `compact_continue` | `HANDOFF_30` |
| WP-HUB | Bind MEU-28–30 `--plan PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"8"`; rewrite hub `Next` to `HUB_NEXT_AFTER`. Grouping Session 13 ✅ is **H2 after exec `approved`**. | WP-30c | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Grouping Session 13 open decisions are already locked in `08-video-conversion.md`. Reviewer confirms these locks (does not invent a second behavior):

1. **Harness gate:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins over Cursor default `human` in `create-plan.md` §5c. After Codex `approved`, auto-continue to execution. System-injected “approved” is still not a verdict (`GUARDRAILS.md` SIGN 3).
2. **Phase 8 is three sessions.** User said “Phase 8”; grouping forbids packing MEU-31–33 here. This plan is Session 13 only. Next after H2: `HUB_NEXT_AFTER`.
3. **Do not start Session 8c / MEU-27.**
4. **Software fallback** if bundled FFmpeg lacks NVENC — not a p7 ship-gate (Spec GPU chip + grouping item 4).
5. **`convert()` stays TTS/download audio.** No `ConversionJob` rows from those paths (Spec invariants).

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (single-statement rule)

Executable owner: `docs/execution/plans/2026-08-24-p8-conversion-engine/named-sets.json`. Do not restate literals in ACs or task rows; cite the name.

| Name | Role |
|------|------|
| `QUEUE_NAME` | `QueueRuntime.queue_name` value `"conversions"` |
| `SETTING_NS` | `"converter"` added to `SETTING_NAMESPACES` (MEU-28) |
| `CONVERTER_KEYS` / `CONVERTER_DEFAULTS` | `SETTINGS_KEY_TABLE` rows (MEU-30) |
| `UNIT_LABEL_FRAMES` | `ProgressSnapshot.unit_label` for encode parse |
| `MEDIA_PORT_KEEP` / `MEDIA_PORT_ADDITIVE` | Frozen vs additive `MediaPort` methods |
| `GPU_PROBE_SIZE` | 1-frame lavfi size. Derive input as `color=black:s=` + `GPU_PROBE_SIZE` (do not store a second size literal). **256×256** (NVENC min; 128×128 fails — [MediaForge #16](https://github.com/PD-Codes/MediaForge/issues/16)) |
| `GPU_PROBE_ENCODERS` | 1-frame probe codecs |
| `CANCEL_HOOK` | `should_stop: Callable[[], bool]` on encode/cut/extract — same wiring as `YouTubeAdapter` + `DownloadService.should_stop` |
| `CONVERSION_JOB_COLUMNS` | Full `conversion_jobs` column set (Spec entity fields) |
| `WMIC_BAN` | argv/source must not contain this token |
| `API_TREE` / `API_BASELINE` | SHA256 manifest of `packages/api` written at task row 1; H1-4 fail-closed compare (no git) |
| `KIND_TOKEN` | output filename token per kind |
| `EXTRACT_CONTAINER_MAP` / `EXTRACT_UNKNOWN_EXT` | extract container |
| `COMPRESS_EXT` | `.mp4` |
| `DEFAULT_PRESET` | `Balanced` |
| `HANDOFF_*` / `RED_*` / `HUB_NEXT_AFTER` | closeout + hub |

---

## Implementation locks (research + local canon)

| Lock | Value | Source |
|------|-------|--------|
| GPU enumerate | Parse `ffmpeg -encoders` **in Python** (no shell `\| grep`) | Spec; [NVIDIA FFmpeg guide](https://docs.nvidia.com/video-technologies/video-codec-sdk/13.1/ffmpeg-with-nvidia-gpu/index.html) |
| GPU 1-frame test | `ffmpeg -hide_banner -loglevel error -f lavfi -i color=black:s={GPU_PROBE_SIZE} -frames:v 1 -an -c:v {encoder} -f null -` for each of `GPU_PROBE_ENCODERS` | Research-backed ([RedditVideoMakerBot NVENC probe](https://github.com/elebumm/RedditVideoMakerBot/pull/2259); size from `GPU_PROBE_SIZE`) |
| Cancel FFmpeg | `CANCEL_HOOK` polled in adapter Popen loop: stdin `q` then terminate. `ConversionService.should_stop` returns `_cancel`. Worker passes `should_stop=self.should_stop` into encode/cut/extract. Inflight row → `Cancelled` via `_cancel_inflight` (download pattern). | Spec 350, 412; Local Canon `download.py` 146–147, 576–593; `youtube/adapter.py` 289–301 |
| Pause | After current file finishes (`_pause` flag), not mid-GOP | Spec; Local Canon download pause |
| Start conflict | `ConflictError` if processor already `Processing` (API 409 in MEU-31) | Spec service table (download’s silent return is **not** copied) |
| UoW | New `conversion_jobs` repo; **do not** hold one UoW across the encode; commit progress on a timer | Spec; Phase 2/3 note |
| Settings | MEU-28 adds `SETTING_NS` to the frozenset. MEU-30 adds `CONVERTER_KEYS`. REST PUT is MEU-31 | Spec REST + service `output_dir` |
| `MEDIA_PORT_METHODS` split | `TEST_DOMAIN` tuple becomes KEEP+ADDITIVE in MEU-28. `TEST_MEDIA_INT` stays KEEP until MEU-29 Green implements adapter methods | Local Canon AC-4.7 / AC-8.12 |
| Output path | `{output_dir}/{stem}_{KIND_TOKEN}{ext}` then `_1`, `_2` before suffix; skip-existing → `Skipped` | Spec |
| Extract `all` | N jobs (one per audio stream) | Spec |
| Even scale | `scale=W:-2` | Spec |
| 10-bit | `p010` instead of `nv12` when `bit_depth >= 10` | Spec / inspiration |
| structlog | new methods `module="convert"`; keep `module="media"` on `convert`/`probe` | Spec |
| G29 | one tmp-SQLite smoke for `ConversionService` | Local Canon p3-services |
| 4A | skip — no renderer controls | create-plan §4A |

---

## Proposed Changes

### MEU-28 — `domain-conversion`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Python `ConversionJob` / DTO constructors | dataclasses + `require_*` | enums `.name`; `out_ms > in_ms`; no `Paused` status; compress forbids trim fields | extra fields → `TypeError` (frozen dataclass) |
| REST / MCP / GUI | — | — | **deferred** MEU-31 / MEU-32 / MEU-33 |

Python `assert` is not validation.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-28.1 | unit | StrEnums `ConversionKind`, `ConversionStatus`, `ConversionPresetId`, `CutCopyMode`, `AudioEncodeMode`, `GpuPreference` match Spec tables; persist `.name`. | Spec 224–233 | unknown member construction fails |
| AC-28.2 | unit | `ConversionStatus` has no `Paused`; constructing a job with status string `Paused` raises `ValidationError`. | Spec 285–286, 200 | `Paused` accepted → fail |
| AC-28.3 | unit | Compress job with `in_ms` or `out_ms` set raises `ValidationError`. | Spec 290 | trim-on-compress accepted → fail |
| AC-28.4 | unit | Cut job with `out_ms <= in_ms` or negative raises `InvalidTimeRangeError`. | Spec 359 | `out_ms == in_ms` accepted → fail |
| AC-28.5 | unit | `reset_failed`: only `Failed` → `Pending`; clears `error_message` and `progress`. Else `ConflictError`. | Spec 286, 294–301 | Reset from `Done` succeeds → fail |
| AC-28.6 | unit | `CONVERSION_TRANSITIONS` is exhaustive over `ConversionStatus` (every member is a key). | Spec state machine; Local Canon `DOWNLOAD_TRANSITIONS` | missing `Skipped` key → fail |
| AC-28.7 | unit | `MediaPort` keeps `MEDIA_PORT_KEEP`; adds `MEDIA_PORT_ADDITIVE`. encode/cut/extract require `on_progress` and `CANCEL_HOOK`. `TEST_DOMAIN` `MEDIA_PORT_METHODS` equals KEEP+ADDITIVE. | Spec 316–348; Local Canon YouTube `should_stop` | `encode` missing `CANCEL_HOOK` → fail |
| AC-28.8 | unit | `MediaInfo` additive optional `width`, `height`, `fps`, `bit_depth`, `field_order`, `streams` default `None`. Six-field construction still valid. Extra kwarg `codec=` still `TypeError`. | Spec 308–309 | missing new field required → fail |
| AC-28.9 | unit | `QUEUE_NAMES` includes `QUEUE_NAME`; `UNIT_LABELS` includes `UNIT_LABEL_FRAMES`. | Spec 366, 388 | `conversions` rejected by `QueueRuntime` → fail |
| AC-28.10 | unit | `SETTING_NAMESPACES` includes `SETTING_NS`. | Spec 479–487 | `Setting(namespace="converter", …)` raises → fail |
| AC-28.11 | unit | `builtin_conversion_presets()` returns five frozen presets; default id `DEFAULT_PRESET`; no SQLite table. | Spec 134–144, 314 | sixth preset or empty catalog → fail |
| AC-28.12 | unit | `ConvertOptions` fields unchanged (`CONVERT_OPTIONS_FIELDS`). | Spec 312, 291 | new required convert field → fail |
| AC-28.13 | unit | New errors `FFmpegEncodeError`, `MediaProbeError`, `InvalidTimeRangeError`, `GpuUnavailableError`; reuse `FFmpegNotFoundError`. | Spec 352–360 | `assert` used as boundary → fail |
| AC-28.14 | unit | `GPUCapabilities` session VO fields match Spec 235–250; not a table. | Spec | persist helper / `__tablename__` → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Enums, job fields, ports, errors | Spec | 08 §Domain |
| `Paused` never a job status | Local Canon | DownloadJob + Spec 285 |
| `SETTING_NS` in domain this MEU | Spec + sequencing | service needs namespace before REST |
| Additive MediaInfo defaults | Spec | keep TTS/download callers valid |
| REST/MCP/GUI validation | deferred | MEU-31–33 |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-28.2 | `ValidationError` from `__post_init__` | `ConversionJob(...)` → status check | `Paused` → zero constructed instances |
| AC-28.4 | `InvalidTimeRangeError` | `ConversionJob` / `CutOptions` ctor | `out_ms <= in_ms` → error, no object |
| AC-28.6 | `CONVERSION_TRANSITIONS.keys()` | module import | `set(ConversionStatus) - keys` nonempty → fail |
| AC-28.7 | `_protocol_methods(MediaPort)` + inspect `CANCEL_HOOK` param | `ports/media.py` | missing `encode` or missing `should_stop` → fail |
| AC-28.9 | `QueueRuntime(queue_name=QUEUE_NAME)` | `domain/queue.py` | unknown name → `ValidationError` |

Atomicity: constructors are single statements (no read-then-write). Exhaustiveness: `CONVERSION_TRANSITIONS` over owned enum.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/enums.py` | modify | conversion enums |
| `packages/core/src/avkit_core/domain/conversion.py` | new | job, presets, GPU VO, encode/cut/extract DTOs |
| `packages/core/src/avkit_core/domain/progress.py` | modify | MediaInfo fields; `UNIT_LABELS` |
| `packages/core/src/avkit_core/domain/queue.py` | modify | `QUEUE_NAMES` |
| `packages/core/src/avkit_core/domain/settings.py` | modify | `SETTING_NAMESPACES` |
| `packages/core/src/avkit_core/domain/errors.py` | modify | new error types |
| `packages/core/src/avkit_core/ports/media.py` | modify | additive Protocol; encode/cut/extract take `on_progress` + `CANCEL_HOOK` |
| `tests/unit/test_domain_conversion.py` | new | AC-28.* |
| `tests/unit/test_domain.py` | modify | `MEDIA_PORT_METHODS`, `QUEUE_NAMES` expected set |

---

### MEU-29 — `infra-conversion`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| SQLite `conversion_jobs` | ORM row ↔ entity mapper | TEXT enum `.name`; Path as TEXT | unknown columns not written |
| FFmpeg argv | `FFmpegAdapter` builders | absolute paths; no `WMIC_BAN` | extra flags only from DTO fields |
| REST/MCP | — | — | deferred MEU-31/32 |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-29.1 | integration | Table `conversion_jobs` exists; **no** STI `jobs` table. Indexes `queue_position`, `status`. | Spec 370–378 | `jobs` table created → fail |
| AC-29.2 | integration | Greenfield CREATE in `models.py`; `migrations.py` `CREATE TABLE IF NOT EXISTS` no-op-safe. | Spec 376; Local Canon Phase 2 | second apply raises → fail |
| AC-29.3 | integration | `UnitOfWork.conversion_jobs` has add/get/list_ordered/save/reorder/delete/delete_all (download shape). | Spec 380 | missing `reorder` → fail |
| AC-29.4 | integration | `probe` fills new `MediaInfo` fields from ffprobe JSON (`-show_streams -show_format -of json`). | Spec 386 | width stays None on a video fixture → fail |
| AC-29.5 | unit | `detect_gpu` source and argv never contain `WMIC_BAN`. Parses `-encoders` in-process. | Spec 387, 395 | `WMIC_BAN` substring → fail |
| AC-29.6 | integration | 1-frame probe lavfi uses `GPU_PROBE_SIZE` and `GPU_PROBE_ENCODERS`; missing encoder ⇒ bool false, not crash. | Research-backed; Spec 387 | argv size ≠ `GPU_PROBE_SIZE` → fail |
| AC-29.7 | integration | `encode` calls `on_progress` with `ProgressSnapshot` (`UNIT_LABEL_FRAMES`); non-zero FFmpeg → `FFmpegEncodeError`. | Spec 388, 357 | no callback / `FilesystemError` only → fail |
| AC-29.8 | integration | `cut` FastCopy: `-ss` before `-i`, `-t`, `-c copy`. Reencode uses encode path + trim. | Spec 389 | `-c copy` after `-i` only (no pre-seek) as FastCopy → fail |
| AC-29.9 | integration | `extract_stream`: `-vn -sn -c:a copy -map a:{n}` + `EXTRACT_CONTAINER_MAP`. | Spec 390 | re-encode audio on default path → fail |
| AC-29.10 | integration | `convert()` still audio-only; MEU-8 regression (same argv family). | Spec 391 | video encode flags on `convert` → fail |
| AC-29.11 | unit | Scale filter uses even height (`scale=W:-2` or equivalent). | Spec 393 | odd-only `scale=1280:721` → fail |
| AC-29.12 | unit | When `CANCEL_HOOK` returns true during fake Popen, adapter writes `q` then terminate. | Spec 350 | `should_stop` true with zero stdin writes → fail |
| AC-29.13 | unit | New methods log `module="convert"`; `convert`/`probe` keep `module="media"`. | Spec 397 | all logs `media` only → fail |
| AC-29.14 | integration | `conversion_jobs` columns == `CONVERSION_JOB_COLUMNS`; round-trip a fully populated `ConversionJob` (every nullable set, enum `.name`, Path TEXT, UTC datetimes) through real UoW. | Spec 374, 257–281 | missing column or dropped `in_ms` on save → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Eighth table + UoW | Spec | 08 §Infrastructure |
| GPU probe recipe | Research-backed | NVIDIA docs + MediaForge min size |
| Progress parse | Spec | stderr `frame=`/`time=`/`speed=` |
| `convert()` frozen | Local Canon | MEU-8 |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-29.1 | sqlite `sqlite_master` names | `models.py` CREATE → engine | `"jobs" in tables` → fail |
| AC-29.5 | adapter source + captured argv | `detect_gpu` → `_run`/`Popen` | `WMIC_BAN` in argv → fail |
| AC-29.6 | probe argv contains `GPU_PROBE_SIZE` | `detect_gpu` → `color=black:s=`+size | size ≠ named-set → fail |
| AC-29.7 | `on_progress` call count + `FFmpegEncodeError` | `encode` → Popen stderr parse | returncode≠0 and no `FFmpegEncodeError` → fail |
| AC-29.12 | fake proc `stdin.write` == `q` | `encode(..., should_stop=...)` → stdin | `should_stop` true, zero writes → fail |
| AC-29.14 | PRAGMA table_info names + re-get job fields | mapper ↔ UoW | nullable `in_ms` lost → fail |

Atomicity: each UoW `commit` is the session commit (existing). Progress commits are **short** UoW scopes (MEU-30 worker also). Fail-closed: unknown encoder line does not set NVENC true.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/src/avkit_infra/database/models.py` | modify | `ConversionJobRow` |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | modify | IF NOT EXISTS |
| `packages/infrastructure/src/avkit_infra/database/mappers.py` | modify | conversion mappers |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | modify | conversion repo |
| `packages/infrastructure/src/avkit_infra/database/unit_of_work.py` | modify | `conversion_jobs` |
| `packages/core/src/avkit_core/ports/storage.py` | modify | repo + UoW attribute |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | modify | encode/cut/extract/detect_gpu/progress/cancel |
| `tests/unit/test_ffmpeg_conversion.py` | new | AC-29.* |
| `tests/integration/test_filesystem_media.py` | modify | `MEDIA_PORT_METHODS` KEEP+ADDITIVE after adapter exists |

---

### MEU-30 — `svc-conversion`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `ConversionService.add_to_queue(paths, spec)` | Python dataclass spec (wire mapping is MEU-31) | absolute `Path`s; kind enum; cut range | unexpected spec keys → `ValidationError` |
| Settings `converter.*` | `SETTINGS_KEY_TABLE` | `CONVERTER_KEYS` / `CONVERTER_DEFAULTS` | unknown leaf → `ValidationError` (existing SettingsService) |
| REST body | — | — | deferred MEU-31 |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-30.1 | integration | `add_to_queue` N paths → N `Pending` jobs; one probe failure → that job `Failed`, others continue. | Spec 407 | one bad path aborts batch → fail |
| AC-30.2 | unit | Output `{dir}/{stem}_{KIND_TOKEN}{ext}`; collision `_1`/`_2`; `skip_existing` true + dest exists → `Skipped` (no overwrite). | Spec 289, 419 | overwrite without suffix → fail |
| AC-30.3 | integration | Worker runs **one** FFmpeg at a time (`current_job_id` single; fake media inflight counter ≤ 1). | Spec 409 | two concurrent encode calls → fail |
| AC-30.4 | unit | `start_processing` while `Processing` raises `ConflictError`. | Spec 409 | silent no-op like download → fail |
| AC-30.5 | integration | `pause_processing` finishes current file then `QueueProcessorState.Paused`; job status never `Paused`. | Spec 410, 200 | job.status=`Paused` → fail |
| AC-30.6 | integration | `cancel_processing`: sets `_cancel`; worker's `CANCEL_HOOK` (`should_stop`) makes adapter write `q` then terminate; inflight → `Cancelled` (`_cancel_inflight`); remaining `Pending`; runtime `Idle`. | Spec 412; Local Canon | remaining marked Cancelled or no stdin `q` → fail |
| AC-30.7 | unit | `SETTINGS_KEY_TABLE` has `CONVERTER_KEYS` with `CONVERTER_DEFAULTS`. | Spec 481–486 | missing `skip_existing` → fail |
| AC-30.8 | unit | TTS/download still call `MediaPort.convert` only — ConversionService not invoked from those services. | Spec 291 | `DownloadService` inserts conversion row → fail |
| AC-30.9 | integration | Progress commits use **short** UoW (commit count increases during encode; not a single enter spanning the whole encode). | Spec 421 | one `__enter__` for entire encode → fail |
| AC-30.10 | unit | `reorder_queue` permutation; `clear_queue`/`remove` delete rows not files (fake FS delete count 0). | Spec 287–288, 414–415 | clear deletes output files → fail |
| AC-30.11 | unit | Encoder override missing → software fallback unless override is hard-unavailable (`GpuUnavailableError` then fallback per Spec 360). Auto never fails the page. | Spec 190, 360 | Auto + no NVENC raises → fail |
| AC-30.12 | integration | G29 tmp-SQLite smoke: add + list via real UoW. | Local Canon p3 | Protocol name drift → fail |
| AC-30.13 | integration | Extract `all`: one input with N audio streams → N jobs, distinct `stream_index` and output paths (not N destination paths for one job). | Spec 390, 130 | one job with N paths → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Sequential GPU worker | Spec | 08 §Service |
| Pause/cancel | Local Canon | match download except start-ConflictError |
| Converter settings keys | Spec | keys this MEU; REST MEU-31 |
| `estimate_output_size` | deferred | Spec “optional; MCP may expose later” — not an unowned skip; not required on default GUI; **out-of-scope** this session (no MCP yet). Revisit MEU-32 if MCP needs it. |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-30.3 | fake `encode` inflight max | `start_processing` → `_worker` → `MediaPort.encode` | max_inflight ≥ 2 → fail |
| AC-30.4 | `ConflictError` | `ConversionService.start_processing` | second start returns None → fail |
| AC-30.6 | job statuses after cancel + adapter stdin `q` | `cancel_processing` → `should_stop` true → encode stdin `q` → `_cancel_inflight` → repo.save | inflight stays `Processing` or no `q` write → fail |
| AC-30.9 | `uow.commits` during encode | worker progress timer → `uow.commit` | commits==1 for long encode → fail |
| AC-30.2 | `output_path` name + status `Skipped` | `add_to_queue` → dest resolve | existing dest overwritten → fail |
| AC-30.13 | job count == audio stream count | `add_to_queue` extract-all → N `ConversionJob` rows | N paths, 1 job → fail |

Atomicity: each add/reorder/progress save is one UoW commit. Fail-closed: unknown `kind` in spec → `ValidationError`.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/conversion.py` | new | ConversionService; `should_stop` returns `_cancel`; worker passes `CANCEL_HOOK` into MediaPort |
| `packages/core/src/avkit_core/services/settings.py` | modify | `CONVERTER_KEYS` |
| `tests/unit/test_conversion_service.py` | new | AC-30.* |
| `tests/unit/test_services.py` | modify | `FakeUnitOfWork.conversion_jobs`; `FakeMedia` additive methods (no-ops / recorders) so existing tests keep running |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| REST `/conversions` + OpenAPI + `converter` settings HTTP | deferred | MEU-31 | grouping Session 14; Spec 425–490 |
| MCP `avkit_convert` | deferred | MEU-32 | grouping Session 14; Spec 494–513 |
| Convert page, rail, Wave 8, Settings Convert card | deferred | MEU-33 | grouping Session 15; Spec 63–211, 517–531 |
| Downloader Done → Add to Convert | out-of-scope | — | Spec 539 named deferral (would reopen MEU-20); not in MEU-33 MVP either |
| Extract → Transcript/TTS handoff | out-of-scope | — | Spec 540 “Deferred” integration, not this phase’s GUI; 08 lines 535–541 |
| Timeline / 2-pass / size-target / deinterlace / custom GOP / subtitle extract / user preset table | out-of-scope | — | Spec 541, 583–584 |
| Session 8c console polish | out-of-scope | — | MEU-27 grouping 8c; do not start |
| Invent MEU-27-as-conversion or extra IDs | out-of-scope | — | grouping MEU-28–33 only |
| Parallel GPU encodes | out-of-scope | — | Spec 581 |
| Bundle CUDA / torch | out-of-scope | — | Spec 580; 07-distribution |
| `wmic` GPU detect | out-of-scope | — | Spec 395 |
| SSE progress | out-of-scope | — | Spec 579 |
| Rewrite FastAPI/MCP/chrome this session | out-of-scope | — | grouping Session 13 layer/files |
| `CLEAN_VM` p7 install | out-of-scope | — | p7 later `[B]` |
| Shutter Encoder UI/code paste | out-of-scope | — | Spec 575; BUILD_PLAN Golden Rule 5 |

---

## BUILD_PLAN.md Audit

This project **does** require hub updates after execution (H1-3 / WP-HUB): bind MEU-28–30 `execution_plan`; append `docs/execution/plans/2026-08-24-p8-conversion-engine/` to phase `"8"` `execution_plans`; set unique hub `Next:` to `HUB_NEXT_AFTER` (`/create-plan p8-conversion-api-mcp`). Do not hand-edit AUTOGEN tables.

Planning-time check (no SSOT writes until H1):

```powershell
uv run python -c "from pathlib import Path; import re,sys; t=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), t); print('hub_next', hits); sys.exit(0 if hits else 1)" *> C:/Temp/av-kit/build-plan-audit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.txt; exit $code
```

Execution validation is the `SSOT_PLAN_BOUND` command in `task.md` row 10.

---

## Verification Plan

### 1. MEU-28 unit
```powershell
uv run pytest tests/unit/test_domain_conversion.py tests/unit/test_domain.py -x --tb=short -v *> C:/Temp/av-kit/pytest-meu-28.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-meu-28.txt | Select-Object -Last 40; exit $code
```

### 2. MEU-29 unit + media integration
```powershell
uv run pytest tests/unit/test_ffmpeg_conversion.py tests/integration/test_filesystem_media.py -x --tb=short -v *> C:/Temp/av-kit/pytest-meu-29.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-meu-29.txt | Select-Object -Last 40; exit $code
```

### 3. MEU-30 unit
```powershell
uv run pytest tests/unit/test_conversion_service.py tests/unit/test_services.py -x --tb=short -v *> C:/Temp/av-kit/pytest-meu-30.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-meu-30.txt | Select-Object -Last 40; exit $code
```

### 4. Types / lint (touched packages)
```powershell
uv run pyright packages/core packages/infrastructure *> C:/Temp/av-kit/pyright-p8-engine.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/pyright-p8-engine.txt | Select-Object -Last 40; exit $code }; uv run ruff check packages/core packages/infrastructure tests/unit/test_domain_conversion.py tests/unit/test_ffmpeg_conversion.py tests/unit/test_conversion_service.py *> C:/Temp/av-kit/ruff-p8-engine.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ruff-p8-engine.txt | Select-Object -Last 20; exit $code
```

### 5. OpenAPI
**Skip this session** — no `API_TREE` edits. H1-4 runs `assert-openapi-skip.ps1` against `API_BASELINE` (written at row 1). Missing baseline or hash drift → fail (G8 required). Do not use git.

### 6. Regression (H1-2)
```powershell
uv run pytest tests/unit tests/integration -x --tb=short -v *> C:/Temp/av-kit/pytest-p8-engine-h1.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p8-engine-h1.txt | Select-Object -Last 40; exit $code
```

---

## Open Questions

None remaining. Grouping’s five human confirms are locked in Spec (rail label, one table, numeric in/out, software fallback, start-after-p7). GPU probe fork (wmic vs lavfi vs fixture mp4) is resolved **Research-backed** in Implementation locks — not a human gate.

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| GPU 1-frame input | lavfi `color=black:s=` + `GPU_PROBE_SIZE` | [MediaForge #16](https://github.com/PD-Codes/MediaForge/issues/16); [NVENC probe PR](https://github.com/elebumm/RedditVideoMakerBot/pull/2259) | no fixture file; NVENC min size | lavfi must exist in bundled FFmpeg (GPL BtbN yes) | ✅ |
| | inspiration `wmic` + `test.mp4` | `_video_conversion_pseudo_logic.md` 73–77 | hardware enum | Spec forbids wmic; needs fixture | ❌ |
| | 128×128 nullsrc | MediaForge old | tiny | NVENC init fails | ❌ |

---

## Emerging standards (this session)

| ID | Apply? | How |
|----|--------|-----|
| G8 | no | `API_TREE` hash == `API_BASELINE`; G8 applies in MEU-31 |
| G29 | yes | AC-30.12 |
| M2/M3/M7 | no | MCP is MEU-32 |
| G5/G11/G21/G31 | no | GUI is MEU-33 |
| UX2 | n/a | no renderer |

---

## Stop conditions

- Plan review round cap 3 without `approved`
- All reviewer rungs unavailable
- Reviewer human-decision question
- During execution: `[B]` only with external-error receipt (missing ffmpeg binary for live encode tests may `[B]` the **live** probe with a fake/Popen unit still green)

---

## Research References

- [08-video-conversion.md](../../../build-plan/08-video-conversion.md)
- [_video_conversion_pseudo_logic.md](../../../_inspiration/_video_conversion_pseudo_logic.md) (intent, not code)
- [NVIDIA FFmpeg with GPU](https://docs.nvidia.com/video-technologies/video-codec-sdk/13.1/ffmpeg-with-nvidia-gpu/index.html)
- [MediaForge NVENC min frame size](https://github.com/PD-Codes/MediaForge/issues/16)
- Local Canon: `DownloadService` pause/cancel; `FFmpegAdapter.convert/probe`; `SETTINGS_KEY_TABLE`; p3-services G29
