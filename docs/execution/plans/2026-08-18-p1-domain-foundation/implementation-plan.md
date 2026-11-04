---
project: "2026-08-18-p1-domain-foundation"
date: "2026-08-18"
source: "docs/build-plan/01-domain-layer.md"
meus: ["MEU-1", "MEU-2", "MEU-3", "MEU-4"]
status: "complete"
template_version: "2.0"
---

# Implementation Plan: Phase 1 Domain Foundation

> **Project**: `2026-08-18-p1-domain-foundation`
> **Build Plan Section(s)**: [01-domain-layer.md](../../../build-plan/01-domain-layer.md) (Phase 1 wins over Phase 0 field summaries)
> **Status**: `complete`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 1 — MEU-1 → MEU-2 → MEU-3 → MEU-4

---

## Goal

Stand up `packages/core` as the hexagonal domain: uv workspace, closed enum/VO set, persistable job/catalog/setting types with runtime invariants, IO-shaped port protocols, and the Phase 1 domain error table. Zero infrastructure imports. No REST, MCP, GUI, or adapters.

av-kit is a **job queue**, not a media library. Domain types are work records and file pointers. Transcript bodies, PCM, and video bytes are not fields.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Re-evaluated 2026-08-19 before Step 6: graphify-out/graph.json and graphify-out-research/graph.json still absent; Headroom has no approved disposition. Execution is exact-spec TDD (exact-evidence bypass class)."
  human_message_reference: null
```

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-1 | `.agent/context/handoffs/2026-08-18-p1-domain-foundation-MEU-1-handoff.md` |
| MEU-2 | `.agent/context/handoffs/2026-08-18-p1-domain-foundation-MEU-2-handoff.md` |
| MEU-3 | `.agent/context/handoffs/2026-08-18-p1-domain-foundation-MEU-3-handoff.md` |
| MEU-4 | `.agent/context/handoffs/2026-08-18-p1-domain-foundation-MEU-4-handoff.md` |

Rolling execution review: `.agent/context/handoffs/2026-08-18-p1-domain-foundation-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

`fresh_worker: none` (`.agent/context/harness.local.md`). Every non-shared row is `compact_continue`. Metadata never grants `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | MEU-1 uv workspace + `avkit_core` layout + pytest/pyright/ruff | — | `shared` | `pyproject.toml`; `packages/core/`; `tests/unit/test_domain.py`; `C:/Temp/av-kit/pytest-domain.txt` |
| WP-4a | MEU-4 error module (`DOMAIN_ERROR_TYPES` + `CookieAccessError` alias) **before** any VO/entity constructors | WP-1 | `compact_continue` | `packages/core/src/avkit_core/domain/errors.py`; compact then re-read `task.md` + this output |
| WP-2 | MEU-2 enums + session/shared VOs | WP-4a | `compact_continue` | `packages/core/src/avkit_core/domain/{enums,progress,queue,tts,download}.py`; compact then re-read `task.md` + this output |
| WP-3 | MEU-3 persistable entities + invariants | WP-2 | `compact_continue` | entity modules + `C:/Temp/av-kit/pytest-domain.txt`; compact then re-read `task.md` + this output |
| WP-4b | MEU-4 port DTOs + Protocol signatures | WP-3 | `compact_continue` | `packages/core/src/avkit_core/ports/`; compact then re-read `task.md` + this output |
| WP-5 | H1 closeout + independent exec review + H2 | WP-4b | `compact_continue` | handoff set; rolling review; reflection; metrics; commit-message draft (no commit) |

Cursor builder pins: `{composer-2.5-fast|cursor-grok-4.5-high-fast}`. Scaffold/entity bulk may use `composer-2.5-fast`. Invariants, ports, and errors use `cursor-grok-4.5-high-fast`. Never `auto` / Fable 5.

---

## User Review Required

> No remaining human-decision fork. Planning resolutions (StrEnum values, dataclass + `__post_init__`, numpy in core, closeout-receipt substitute, no `application/` package) are source-backed below. The reviewer may overturn a recommendation; that is the review loop, not a stop-now cue.
>
> **This section is content for the review loop, NOT a cue to stop now.** After writing the plan, auto-dispatch `/plan-critical-review`.

---

## Named sets (single-statement rule)

Define each name **once** in `avkit_core.domain` (or `avkit_core.domain.errors` / ports). Every AC and task row that mentions the set refers to this name — do not restated literals at multiple sites.

| Name | Definition | Home |
|------|------------|------|
| `DownloadStatus` | `Pending`, `Downloading`, `Done`, `Failed`, `Skipped`, `QualityBlocked`, `AgeRestricted`, `Cancelled`. **No `Paused`.** | `enums.py` |
| `TranscriptStatus` | `Pending`, `Processing`, `Done`, `Failed`, `Paused`, `Cancelled` | `enums.py` |
| `TranscriptItemStatus` | `Pending`, `Done`, `Skipped`, `Failed` | `enums.py` |
| `TTSStatus` | `Pending`, `Generating`, `Done`, `Failed`, `Cancelled` | `enums.py` |
| `TTSSourceKind` | `Inline`, `File` | `enums.py` |
| `QueueProcessorState` | `Idle`, `Processing`, `Paused` | `enums.py` |
| `MediaFormat` | `MP4`, `WEBM`, `MP3`, `M4A`, `WAV`, `OPUS` | `enums.py` |
| `QualityPreset` | `Best`, `P2160`, `P1440`, `P1080`, `P720`, `P480`, `P360`, `P240`, `P144`, `Lowest` | `enums.py` |
| `AudioFormat` | `Default`, `Best`, `Lowest`, `LowWebm`, `MediumWebm`, `StandardWebm`, `StandardM4a`, `StandardMp3`, `HighM4a` | `enums.py` |
| `DeviceType` | `Auto`, `CUDA`, `MPS`, `CPU` | `enums.py` |
| `ModelFormat` | `PyTorch`, `ONNX` | `enums.py` |
| `ModelPrecision` | `FP32`, `FP16`, `INT8` | `enums.py` |
| `SABRMode` | `Inactive`, `Active`, `Checking` | `enums.py` |
| `SABRSource` | `Detected`, `Forced` | `enums.py` |
| `SettingValueType` | `String`, `Number`, `Boolean`, `Json` | `enums.py` |
| `SETTING_NAMESPACES` | `frozenset({"downloader", "transcript", "tts", "app", "ui"})` | `settings.py` |
| `QUEUE_NAMES` | `frozenset({"downloads", "transcripts"})` | `queue.py` |
| `UNIT_LABELS` | `frozenset({"bytes", "videos", "segments"})` | `progress.py` |
| `SABR_RESTRICTED_AUDIO` | `frozenset({AudioFormat.StandardMp3, AudioFormat.HighM4a})` | `enums.py` |
| `TTS_OUTPUT_FORMATS` | `frozenset({MediaFormat.MP3, MediaFormat.WAV})` | `tts.py` |
| `TTS_SPEED_MIN` / `TTS_SPEED_MAX` | `0.5` / `2.0` | `tts.py` |
| `FRACTION_MIN` / `FRACTION_MAX` | `0.0` / `1.0` | `progress.py` |
| `TEXT_PREVIEW_MAX` | `200` | `tts.py` |
| `MODEL_DOWNLOAD_STATES` | `frozenset({"Idle", "Downloading", "Failed"})` | `tts.py` — **not** a new `enums.py` member (Phase 1 enum table is closed) |
| `DOWNLOAD_TRANSITIONS` | `Pending→{Downloading}`; `Downloading→{Done,Failed,Cancelled,Skipped,QualityBlocked,AgeRestricted}`; `Failed→{Pending}`; `QualityBlocked→{Pending}` | `download.py` |
| `DOMAIN_ERROR_TYPES` | `ValidationError`, `NotFoundError`, `ConflictError`, `AgeRestrictedError`, `DownloadCancelledError`, `SABRDetectedError`, `CookieTestError`, `TranscriptsDisabledError`, `NoTranscriptFoundError`, `TranscriptRetryableError`, `FFmpegNotFoundError`, `ModelDownloadError`, `ModelLoadError`, `FilesystemError` | `errors.py` |
| `CookieAccessError` | **alias** of `CookieTestError` — not a second class | `errors.py` |
| `YOUTUBE_PORT_METHODS` | `extract_info`, `extract_video_ids`, `download`, `get_formats`, `check_sabr_status`, `test_cookies`, `ytdlp_version` | `ports/youtube.py` |
| `TRANSCRIPT_PORT_METHODS` | `get_transcript` | `ports/transcript.py` |
| `TTS_PORT_METHODS` | `load_model`, `unload_model`, `generate`, `list_voices`, `get_model_status` | `ports/tts.py` |
| `MEDIA_PORT_METHODS` | `is_available`, `ffmpeg_version`, `convert`, `probe` | `ports/media.py` |
| `FILESYSTEM_PORT_METHODS` | `write_text_atomic`, `write_progress_export`, `ensure_channel_dirs`, `write_audio_wav`, `read_text` | `ports/filesystem.py` |
| `MODEL_CATALOG_PORT_METHODS` | `download`, `sideload` | `ports/models.py` |
| `UOW_ATTRIBUTES` | `downloads`, `archive`, `transcripts`, `tts_jobs`, `settings`, `models` plus `commit` / `rollback` / context manager | `ports/storage.py` |
| `PROGRESS_SNAPSHOT_FIELDS` | `fraction`, `units_done`, `units_total`, `unit_label`, `rate`, `eta_seconds`, `error` | `progress.py` |
| `ERROR_INFO_FIELDS` | `message`, `code` | `progress.py` |
| `SABR_STATUS_FIELDS` | `mode`, `source`, `checked_at` | `download.py` |
| `QUEUE_RUNTIME_FIELDS` | `queue_name`, `state`, `current_job_id` | `queue.py` |
| `MODEL_STATUS_FIELDS` | `variant_id`, `name`, `device`, `memory_bytes`, `is_loaded` | `tts.py` |
| `MODEL_DOWNLOAD_RUNTIME_FIELDS` | `variant_id`, `state`, `fraction`, `error_message` | `tts.py` |
| `VOICE_CONFIG_FIELDS` | `voice_id`, `lang_code`, `language`, `gender`, `style_description` | `tts.py` |
| `CONVERT_OPTIONS_FIELDS` | `codec`, `bitrate_kbps`, `sample_rate`, `channels` | `progress.py` |
| `MEDIA_INFO_FIELDS` | `duration`, `container`, `video_codec`, `audio_codec`, `sample_rate`, `channels` | `progress.py` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-18-p1-domain-foundation-MEU-*-handoff.md` | this plan (Handoff Set owner) |
| `SCAN_PLACEHOLDER_ARGS` | `rg -n -e TODO -e FIXME -e NotImplementedError -e SabrDetectedError -e assert packages/core/src` | Verification Plan §4 |
| `SCAN_INFRA_ARGS` | `rg -n -e sqlalchemy -e yt_dlp -e fastapi -e youtube_transcript_api -e huggingface_hub -e soundfile packages/core/src` | Verification Plan §4 |
| `SCAN_G36_ARGS` | `rg -n -e pytest.mark.skip -e pytest.mark.xfail -e pytest.skip tests/unit/test_domain.py` | Verification Plan §4 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | Verification Plan §6 |

**StrEnum values:** each member’s value equals its spec name (`Pending = "Pending"`). Do **not** use `enum.auto()` — in 3.11 `StrEnum` + `auto()` lower-cases the name ([`enum.StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum)), which would silently diverge from Phase 0/1 wire names.

**No `Operation` enum.** Those names are service/port calls (`01-domain-layer.md` line 105).

## Implementation locks (planning resolutions)

| Topic | Lock | Source |
|-------|------|--------|
| Types | `@dataclass(frozen=True)` + `__post_init__` raising `ValidationError`. Type hints are not validation. No `assert`. | Spec errors table; Local Canon `.agent/docs/code-quality.md` Boundary Validation; Research-backed [PEP 557](https://peps.python.org/pep-0557/); [assert is stripped under `-O`](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) |
| Extra fields | Unexpected constructor kwargs → `TypeError` (dataclass). Invalid values → `ValidationError`. | Local Canon extra-field policy (dataclass equivalent of `extra="forbid"`). Pydantic stays at Phase 4 REST (`MEU-14`) |
| Enums | `enum.StrEnum`, Python `>=3.11`, explicit values | Research-backed [What's New in 3.11 — StrEnum](https://docs.python.org/3.11/whatsnew/3.11.html) |
| numpy | Core runtime dependency — `TTSPort.generate` and `FilesystemPort.write_audio_wav` name `np.ndarray` | Spec `01-domain-layer.md` lines 457, 485 |
| `DownloadResult.sabr_detected` | Required `bool`. Port paragraph wins over the shorter VO table. | Spec lines 210 vs 440 |
| Cookie fields | `DownloadOptions` carries `mode`, `browser`, `profile`, `cookie_file` only — never cookie bytes | Spec lines 209, 440 |
| `ConvertOptions` | `CONVERT_OPTIONS_FIELDS`: `codec: str`, `bitrate_kbps: int \| None`, `sample_rate: int \| None`, `channels: int \| None` | Spec line 474 ellipsis; Local Canon `02-infrastructure.md` lines 425–426 (TTS 80 kbps / download `AudioFormat`); Local Canon `_shared_patterns.md` §4 (80 kbps, 44.1 kHz, mono) |
| `MediaInfo` | `MEDIA_INFO_FIELDS`: `duration`, `container`, `video_codec`, `audio_codec`, `sample_rate`, `channels` (all nullable except types as floats/ints/strs). Phase 1’s single word `codec` is the video/audio codec **pair** — do not also keep a third `codec` field. | Spec line 474 ellipsis; Local Canon `02-infrastructure.md` line 426 (`probe` → duration, container, video/audio codec, sample rate, channels) |
| Error module sequencing | Full `domain/errors.py` (`DOMAIN_ERROR_TYPES` + alias) is WP-4a, **after MEU-1 and before MEU-2**. VO/entity constructors may raise `ValidationError` / `ConflictError` only after that module exists. | Spec lines 532–553; review F1 |
| `errors.py` | Create even though the layout tree omits it | Spec lines 532–553 win over the tree (lines 61–79) |
| `application/` | Do **not** create | Spec package layout omits it. `architecture.md` is target-state later; Phase 1 wins |
| Tests | All Phase 1 tests live in / are collected by `tests/unit/test_domain.py` | Spec Validation commands lines 581–588. `testing-strategy.md` split files are the full-repo tree, not this receipt |
| Closeout validator | `tools/validate_closeout_artifacts.py` is **not** in this tree (same class as `validate_codebase.py`, `commands.md` line 16–17). Use completion-preflight marker receipts. Do not invent a tools MEU. | Local Canon |
| MEU gate | pytest + pyright + ruff + anti-placeholder `rg` — **not** `validate_codebase.py` | Local Canon `commands.md` line 16–17 |
| Production entrypoint (PR-8) | Phase 1 product surface **is** `avkit_core.domain` constructors and `avkit_core.ports` Protocols. Services (`MEU-10+`) call these; adapters (`MEU-5–9`) implement Protocols. Controls are not test-only. | Spec Goal + ports section |
| Atomicity | Constructors and `reset_failed` / transition helpers are a **single validation statement** in `__post_init__` / method body. No read-then-write persistence in Phase 1 — no transaction/CAS required. | create-plan atomicity corollary |

### Repository Protocol signatures (capability table → names)

Phase 2 implements these. Phase 1 freezes the capabilities (`01-domain-layer.md` lines 517–526). Names may tighten later only if every capability remains.

```python
class DownloadRepository(Protocol):
    def add(self, job: DownloadJob) -> None: ...
    def get(self, job_id: str) -> DownloadJob | None: ...
    def list_ordered(self) -> list[DownloadJob]: ...
    def save(self, job: DownloadJob) -> None: ...
    def reorder(self, job_ids: list[str]) -> None: ...
    def delete(self, job_id: str) -> None: ...
    def delete_all(self) -> None: ...
    def reset_failed(self) -> None: ...

class ArchiveRepository(Protocol):
    def get(self, extractor: str, video_id: str) -> DownloadArchiveEntry | None: ...
    def add(self, entry: DownloadArchiveEntry) -> None: ...
    def list(self) -> list[DownloadArchiveEntry]: ...

class TranscriptRepository(Protocol):
    def add_job(self, job: TranscriptJob) -> None: ...
    def get_job(self, job_id: str) -> TranscriptJob | None: ...
    def list_jobs_ordered(self) -> list[TranscriptJob]: ...
    def save_job(self, job: TranscriptJob) -> None: ...
    def reorder_jobs(self, job_ids: list[str]) -> None: ...
    def delete_job(self, job_id: str) -> None: ...
    def replace_items(self, job_id: str, items: list[TranscriptItem]) -> None: ...
    def list_items(self, job_id: str) -> list[TranscriptItem]: ...
    def save_item(self, item: TranscriptItem) -> None: ...
    def count_items(self, job_id: str) -> int: ...
    def count_items_with_status(self, job_id: str, status: TranscriptItemStatus) -> int: ...

class TTSJobRepository(Protocol):
    def add(self, job: TTSJob) -> None: ...
    def get(self, job_id: str) -> TTSJob | None: ...
    def save(self, job: TTSJob) -> None: ...
    def delete(self, job_id: str) -> None: ...

class SettingsRepository(Protocol):
    def get(self, namespace: str, key: str) -> Setting | None: ...
    def set(self, setting: Setting) -> None: ...
    def get_namespace(self, namespace: str) -> list[Setting]: ...
    def set_namespace(self, namespace: str, settings: list[Setting]) -> None: ...

class ModelRepository(Protocol):
    def list_catalog(self) -> list[ModelVariant]: ...
    def get(self, variant_id: str) -> ModelVariant | None: ...
    def mark_downloaded(self, variant_id: str, path: Path) -> None: ...
```

`TranscriptItem` has **no** UoW attribute (`01-domain-layer.md` line 528).

---

## Proposed Changes

### MEU-1 `domain-scaffold`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| None (scaffold only) | — | — | — |

Phase 1 has no REST/MCP/UI/file-import write surface. Constructor boundaries start in MEU-2/3.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1.1 | unit | Root uv workspace exists: `pyproject.toml` with `[tool.uv.workspace] members = ["packages/core"]`, `requires-python = ">=3.11"`. Dev group includes pytest, pyright, ruff, pyyaml, jsonschema. | Spec layout; Local Canon `meu_status.py` deps in `tools/requirements.txt`; Research-backed StrEnum needs 3.11 | Missing member or `requires-python` below 3.11 fails the scaffold test |
| AC-1.2 | unit | Every path in `01-domain-layer.md` lines 61–79 exists as a Python module (docstring-only until later MEUs), **plus** `domain/errors.py`. No `application/` package. | Spec package layout + errors section | `Test-Path` miss or `application/` exists → fail |
| AC-1.3 | unit | `import avkit_core` succeeds. Package has **zero** imports of `sqlalchemy`, `yt_dlp`, `fastapi`, `youtube_transcript_api`, `huggingface_hub`, `soundfile`. | Spec Goal “zero infrastructure imports”; Golden Rule 1 | Any of those names in `packages/core` source → fail |
| AC-1.4 | unit | `tests/unit/test_domain.py` is collectable; tests use `@pytest.mark.unit`. | Spec Validation commands; Local Canon `testing-strategy.md` markers | Unmarked test or missing file → fail |
| AC-1.5 | unit | `numpy` is declared on `avkit-core` (needed by MEU-4 signatures). | Spec `np.ndarray` on ports | `import numpy` from the core env fails → fail |
| AC-1.6 | unit | Registered receipts exit 0: pytest `tests/unit/test_domain.py`, pyright `packages/core/`, ruff `packages/core/`. | Spec lines 581–588 | Nonzero exit → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| uv vs poetry vs hatch | Local Canon | Repo already uses `uv run` in `commands.md` and discovery receipts |
| Where to put pytest/pyright/ruff config | Research-backed | `[tool.pytest.ini_options]`, `[tool.pyright]`, `[tool.ruff]` on the workspace root (uv workspace default) |
| Create domain files empty vs later | Spec | Layout tree is MEU-1 deliverable; later MEUs fill modules |
| `application/` from architecture.md | Spec | Phase 1 layout omits it — do not create |
| `validate_codebase.py` MEU gate | Local Canon | Not in tree — use pytest/pyright/ruff |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `pyproject.toml` | new | Workspace + tool config + dev group |
| `packages/core/pyproject.toml` | new | `avkit-core` + numpy |
| `packages/core/src/avkit_core/__init__.py` | new | Package export |
| `packages/core/src/avkit_core/domain/__init__.py` | new | Domain package |
| `packages/core/src/avkit_core/domain/{download,transcript,tts,settings,progress,queue,enums,errors}.py` | new | Docstring stubs |
| `packages/core/src/avkit_core/ports/__init__.py` | new | Ports package |
| `packages/core/src/avkit_core/ports/{youtube,transcript,tts,media,filesystem,models,storage}.py` | new | Docstring stubs |
| `tests/conftest.py` | new | Register `unit` / `integration` / `e2e` markers |
| `tests/unit/test_domain.py` | new | Scaffold + later MEU tests (single gate file) |

#### Control binding (MEU-1)

| AC | Observable | Call chain | Negative oracle |
|----|------------|------------|-----------------|
| AC-1.3 | `SCAN_INFRA_ARGS` hit count on `packages/core/src` | Production package `avkit_core` (imported by later adapters/services) | Any listed infra name → fail (zero is the only passing count) |
| AC-1.2 | `application/` directory existence | Workspace layout consumed by uv/pyright | Directory present → fail |

---

### MEU-4a `domain-errors` (before enums/VOs)

MEU-4 ownership is unchanged (no new MEU ID). Only the **error classes** move earlier so MEU-2/3 constructors have a live producer.

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Domain error constructors | `DOMAIN_ERROR_TYPES` | message required | N/A |

#### Acceptance Criteria

AC-4.10, AC-4.11, and AC-4.12 (defined under MEU-4 below) are **executed in WP-4a**. Ports/DTOs stay in WP-4b.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/errors.py` | modify | Full `DOMAIN_ERROR_TYPES` + `CookieAccessError` alias |
| `tests/unit/test_domain.py` | modify | Error-table tests (AC-4.10–AC-4.12) |

---

### MEU-2 `domain-enums-vos`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| VO constructors (`ProgressSnapshot`, `ErrorInfo`, `SABRStatus`, `QueueRuntime`, `ModelStatus`, `ModelDownloadRuntime`, `VoiceConfig`) | dataclass `__post_init__` → `ValidationError` | Named sets + ranges below | Unexpected kwargs → `TypeError` |

Invalid input → `ValidationError` (HTTP 422 mapping is `MEU-14`, not this phase). Create/update parity: `dataclasses.replace` re-runs `__post_init__`; do not add a raw `replace(obj, **dict)` helper.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-2.1 | unit | Every enum in the Named sets table exists as `StrEnum` with **exactly** those members and PascalCase string values. | Spec lines 83–103 | Extra member, missing member, or `auto()` lower-case value → fail |
| AC-2.2 | unit | `Paused` is **not** a `DownloadStatus` member. `"Paused" in DownloadStatus` is false. | Spec line 89 | Constructing `DownloadStatus("Paused")` succeeds → fail |
| AC-2.3 | unit | No `Operation` symbol in `avkit_core`. | Spec line 105 | `Operation` importable → fail |
| AC-2.4 | unit | `ProgressSnapshot` exposes **exactly** `PROGRESS_SNAPSHOT_FIELDS`. `fraction` in `[FRACTION_MIN, FRACTION_MAX]`; `unit_label` ∈ `UNIT_LABELS`; `units_done >= 0`; `units_total` is `int \| None` and if int then `>= 0`; `rate` is `float \| None` and if float then `>= 0`; `eta_seconds` is `int \| None` and if int then `>= 0`; `error` is `ErrorInfo \| None`. | Spec lines 111–123 | Missing `units_total`/`rate`/`eta_seconds`/`error`; extra field; `fraction=1.1`; `unit_label="percent"`; negative `units_total` → `TypeError`/`ValidationError` |
| AC-2.5 | unit | `ErrorInfo` exposes **exactly** `ERROR_INFO_FIELDS`. `message` is non-empty `str`; `code` is `str \| None`. | Spec lines 125–130 | `message=""` or missing `code` slot → `ValidationError`/`TypeError` |
| AC-2.6 | unit | `SABRStatus` exposes **exactly** `SABR_STATUS_FIELDS`. `mode` ∈ `SABRMode`; when `mode is Active`, `source` is not `None`; `checked_at` is `datetime \| None`. | Spec lines 132–140 | `Active` + `source=None`; missing `checked_at`; extra field → `ValidationError`/`TypeError` |
| AC-2.7 | unit | `QueueRuntime` exposes **exactly** `QUEUE_RUNTIME_FIELDS`. `queue_name` ∈ `QUEUE_NAMES`; `state` ∈ `QueueProcessorState`; `current_job_id` is `str \| None`. | Spec lines 142–150 | `queue_name="tts"`; missing `current_job_id` → `ValidationError`/`TypeError` |
| AC-2.8 | unit | `ModelStatus` exposes **exactly** `MODEL_STATUS_FIELDS`: `variant_id: str \| None`, `name: str`, `device: str`, `memory_bytes: int` (≥0), `is_loaded: bool`. | Spec line 364 | `memory_bytes=-1` or missing `is_loaded` → `ValidationError`/`TypeError` |
| AC-2.9 | unit | `ModelDownloadRuntime` exposes **exactly** `MODEL_DOWNLOAD_RUNTIME_FIELDS`. `state` ∈ `MODEL_DOWNLOAD_STATES`; `fraction` in `[FRACTION_MIN, FRACTION_MAX]`; `variant_id` is `str \| None`; `error_message` is `str \| None`. No `ModelFetchJob` type exists. | Spec lines 365, 570–573 | `state="Queued"`; missing `variant_id`/`error_message`; `ModelFetchJob` symbol → fail |
| AC-2.10 | unit | `VoiceConfig` exposes **exactly** `VOICE_CONFIG_FIELDS`. First character of `lang_code` equals first character of `voice_id` (Kokoro prefix rule). | Spec line 363; Local Canon `_kokoro_production_settings.md` | `voice_id="af_bella"` + `lang_code="j"`; extra field → `ValidationError`/`TypeError` |
| AC-2.11 | unit | Closed-set exhaustiveness: a `match` / member-set equality test binds each enum to its Named set so adding a member without updating the test fails. Open-world strings fail closed (`ValidationError` / `ValueError` wrapped). | create-plan exhaustiveness corollary | Silent default branch for unknown string → fail |
| AC-2.12 | unit | A single inventory test binds each VO type to its Named field set so adding/removing a Phase 1 field fails the suite. Unexpected kwargs → `TypeError`. | Spec VO tables + extra-field lock | Constructing `ProgressSnapshot` without `error=` succeeds; unknown kwarg accepted → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| StrEnum vs Enum | Research-backed | StrEnum 3.11+; explicit values (not `auto()`) |
| `ModelDownloadRuntime.state` as enum | Spec | String union in the VO table — use `MODEL_DOWNLOAD_STATES`, do not extend the enum table |
| Voice prefix rule | Spec + Local Canon | First-letter match; do not invent a fuller phoneme table |
| `QueueRuntime` persistable? | Spec | Session only; no table (lines 46, 142–152) |
| VO field completeness | Spec | Every Phase 1 VO column is a Named field set (`PROGRESS_SNAPSHOT_FIELDS`, …). AC-2.4–AC-2.12 and AC-2.12 inventory bind them. |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/enums.py` | modify | All Phase 1 enums + `SABR_RESTRICTED_AUDIO` |
| `packages/core/src/avkit_core/domain/progress.py` | modify | `ProgressSnapshot`, `ErrorInfo`, fraction/unit constants |
| `packages/core/src/avkit_core/domain/queue.py` | modify | `QueueRuntime`, `QUEUE_NAMES` |
| `packages/core/src/avkit_core/domain/tts.py` | modify | `VoiceConfig`, `ModelStatus`, `ModelDownloadRuntime` |
| `packages/core/src/avkit_core/domain/download.py` | modify | `SABRStatus` lives with download session types (spec groups it with download) |
| `tests/unit/test_domain.py` | modify | Enum/VO tests |

#### Control binding (MEU-2)

| AC | Observable | Call chain | Negative oracle |
|----|------------|------------|-----------------|
| AC-2.2 | Exception type + `Paused not in DownloadStatus` | `DownloadStatus.__new__` / constructor (public `avkit_core.domain` API) | `DownloadStatus("Paused")` returns a member → fail |
| AC-2.4 | `ValidationError` | `ProgressSnapshot(...)` → `__post_init__` | `fraction=1.1` accepted → fail |
| AC-2.6 | `ValidationError` | `SABRStatus(...)` | `Active` without source accepted → fail |
| AC-2.7 | `ValidationError` | `QueueRuntime(...)` | `queue_name="tts"` accepted → fail |
| AC-2.10 | `ValidationError` | `VoiceConfig(...)` | mismatched prefix accepted → fail |
| AC-2.12 | `TypeError` / dataclass fields() | public VO constructors in `avkit_core.domain` | missing required Phase 1 field or extra kwarg accepted → fail |

---

### MEU-3 `domain-entities`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Persistable constructors: `DownloadJob`, `DownloadArchiveEntry`, `TranscriptJob`, `TranscriptItem`, `TTSJob`, `ModelVariant`, `Setting` | dataclass `__post_init__` → `ValidationError` | Field tables + invariants in `01-domain-layer.md` | Unexpected kwargs → `TypeError` |
| `DownloadJob.reset_failed` | same `__post_init__` on the returned instance | Only from `Failed`; clears `error_message` + `progress` | Calling on `Done` → `ConflictError` |

HTTP mapping is `MEU-14`. Create/update parity: mutation helpers re-validate; no `replace(obj, **raw)`.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-3.1 | unit | `DownloadJob` has exactly the persistable fields in Spec lines 164–180 (`id` UUID-format `str`, `url`/`video_id`/`title` non-empty, `quality`/`audio_format`/`status` enums, `audio_only: bool`, `progress` in `[FRACTION_MIN, FRACTION_MAX]`, `queue_position >= 0`, datetimes present). | Spec | Missing field or extra persistable field (`parent_id`, `Paused` status) → fail |
| AC-3.2 | unit | `DownloadJob.status` cannot be `Paused` (enum closed + constructor). | Spec line 184 | `status="Paused"` → `ValidationError` |
| AC-3.3 | unit | `DOWNLOAD_TRANSITIONS` is enforced by `DownloadJob.transition(new_status)` (or equivalent named method). Illegal edge → `ConflictError`. | Spec lines 190–199 + QualityBlocked reset line 186 | `Done → Failed` accepted → fail |
| AC-3.4 | unit | `reset_failed` maps `Failed → Pending` and clears `error_message` and `progress` to `0.0`. | Spec line 187 | `error_message` survives reset → fail |
| AC-3.5 | unit | `DownloadArchiveEntry` fields per lines 219–223; unique-key fields `extractor` + `video_id` are non-empty. No job-history fields. | Spec | empty `video_id` → `ValidationError` |
| AC-3.6 | unit | `TranscriptJob` has the fields in lines 239–251 and **does not** have `video_ids`, `processed_ids`, or a stored progress float. | Spec lines 239–253 | those dropped fields present → fail |
| AC-3.7 | unit | `TranscriptJob.status` **may** be `Paused` (channel badge). | Spec line 243 | `Paused` rejected → fail |
| AC-3.8 | unit | `TranscriptItem` fields per lines 283–294; `job_id` + `video_id` non-empty; `word_count`/`retry_count` ≥ 0; `Done` requires `path is not None`. Uniqueness `(job_id, video_id)` is a documented aggregate invariant (repo-enforced in `MEU-5`; constructor still rejects empty keys). | Spec lines 296–301 | `status=Done` + `path=None` → `ValidationError` |
| AC-3.9 | unit | `TTSJob` fields per lines 317–332; `speed` in `[TTS_SPEED_MIN, TTS_SPEED_MAX]`; `format` ∈ `TTS_OUTPUT_FORMATS`; `text_preview` length ≤ `TEXT_PREVIEW_MAX`; `source_kind=File` requires `source_path`; no full-text field. | Spec lines 334–339 | `speed=2.1` or `text` field or File without path → `ValidationError` |
| AC-3.10 | unit | `ModelVariant` fields per lines 347–355; **no** `is_loaded` or `device` columns. | Spec lines 357–358 | those fields present → fail |
| AC-3.11 | unit | `Setting.namespace` ∈ `SETTING_NAMESPACES`; `key` is **leaf only** (reject `"."` in key). | Spec lines 369–377 | `key="downloader.quality"` → `ValidationError` |
| AC-3.12 | unit | No persistable `QueueRuntime`, `SABRState`, `ModelFetchJob`, `ConversionJob`, `SourceLocator`, `JobArtifact`. | Spec lines 570–577 | any of those types exist as persistable entities → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| UUID format | Research-backed | `uuid.UUID(id)` in `__post_init__` — Spec says `str` (UUID) |
| `text_hash` algorithm | Spec | Store a non-empty `str`; do not invent sha256-at-construction (hashing is a service/`MEU-12` concern when text is received) |
| Unique `(extractor, video_id)` / `(job_id, video_id)` | Spec | Documented; SQL unique in `MEU-5`; domain rejects empty parts |
| `DownloadJob` explosion of playlists | Spec | Service/`MEU-10` inserts N jobs — not a Phase 1 constructor loop |
| Transition helper vs services-only | Spec state machine | Named `DOWNLOAD_TRANSITIONS` + method so Phase 3 cannot invent a second graph |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/download.py` | modify | `DownloadJob`, `DownloadArchiveEntry`, `DOWNLOAD_TRANSITIONS` |
| `packages/core/src/avkit_core/domain/transcript.py` | modify | `TranscriptJob`, `TranscriptItem` |
| `packages/core/src/avkit_core/domain/tts.py` | modify | `TTSJob`, `ModelVariant` |
| `packages/core/src/avkit_core/domain/settings.py` | modify | `Setting`, `SETTING_NAMESPACES` |
| `tests/unit/test_domain.py` | modify | Entity invariant tests |

#### Control binding (MEU-3)

| AC | Observable | Call chain | Negative oracle |
|----|------------|------------|-----------------|
| AC-3.2 | `ValidationError`; `job.status` | `DownloadJob(...)` public constructor | `status="Paused"` stored → fail |
| AC-3.3 | `ConflictError` | `DownloadJob.transition` | `Done.transition(Failed)` succeeds → fail |
| AC-3.4 | `status`, `error_message`, `progress` on returned job | `DownloadJob.reset_failed` | leftover error or nonzero progress → fail |
| AC-3.8 | `ValidationError` | `TranscriptItem(...)` | `Done` without `path` accepted → fail |
| AC-3.9 | `ValidationError` | `TTSJob(...)` | `speed=0.49` or preview length 201 accepted → fail |
| AC-3.11 | `ValidationError` | `Setting(...)` | dotted key accepted → fail |

---

### MEU-4 `domain-ports-errors`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Port DTOs: `VideoInfo`, `PlaylistInfo`, `FormatInfo`, `DownloadOptions`, `DownloadResult`, `CookieTestResult`, `ChannelInfo`, `TranscriptResult`, `ConvertOptions`, `MediaInfo` | dataclass `__post_init__` → `ValidationError` | Field locks below | Unexpected kwargs → `TypeError` |
| Domain error constructors | `DOMAIN_ERROR_TYPES` classes | message required | N/A (exceptions) |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-4.1 | unit | Port DTO fields: `VideoInfo(video_id, title, duration: float \| None, formats: list[FormatInfo])`; `PlaylistInfo(playlist_id, title, video_ids: list[str])`; `FormatInfo(format_id, ext, height: int \| None, abr: float \| None, vcodec: str \| None, acodec: str \| None)`. | Spec lines 204–208 | missing `formats` / extra cookie-bytes field → fail |
| AC-4.2 | unit | `DownloadOptions` has `quality`, `audio_only`, `audio_format`, `output_dir`, `mode: str`, `browser: str \| None`, `profile: str \| None`, `cookie_file: Path \| None`. No cookie-byte field. | Spec lines 209, 440 | `cookies: bytes` field exists → fail |
| AC-4.3 | unit | `DownloadResult` has `file_path`, `file_size`, `video_id`, `title`, **`sabr_detected: bool`** (required). | Spec line 440 (wins over line 210) | construct without `sabr_detected` → TypeError/`ValidationError` |
| AC-4.4 | unit | `CookieTestResult` is `{ok: bool, error_message: str \| None}`. | Spec line 440 | cookie payload field → fail |
| AC-4.5 | unit | `ChannelInfo(channel_id, name, url, video_count)`; `TranscriptResult(video_id, title, text, language)` exists as a **port return only** — not a persistable entity / table type. | Spec lines 307–308 | `TranscriptResult` listed as persistable or `text` appears on `TranscriptItem` → fail |
| AC-4.6 | unit | `ConvertOptions` exposes **exactly** `CONVERT_OPTIONS_FIELDS`. `MediaInfo` exposes **exactly** `MEDIA_INFO_FIELDS`. No single leftover `codec` field on `MediaInfo` (video/audio are split). Unknown kwargs → `TypeError`. | Spec line 474 ellipsis; Local Canon `02-infrastructure.md:425-426`; `_shared_patterns.md` §4 | missing `channels`/`bitrate_kbps`/`container`/`video_codec`; extra unknown field → `TypeError`/`ValidationError` |
| AC-4.7 | unit | Each Protocol in the layout tree exposes **exactly** the Named method set with the signatures in Spec lines 429–515, including `FilesystemPort.read_text(self, path: Path, *, max_bytes: int) -> str` and `TTSPort.generate(...) -> np.ndarray`. `on_progress` for catalog is `Callable[[float], None]`; TTS `generate` uses the same callable type (catalog port is the typed source). | Spec Port protocols | missing `test_cookies` / `ytdlp_version` / `read_text` / `sabr_detected` usage → fail |
| AC-4.8 | unit | `FilesystemPort` has no general-purpose read other than `read_text` (compile-only; `max_bytes` mandatory keyword-only). | Spec lines 479–489 | optional `max_bytes` or extra `read_bytes` → fail |
| AC-4.9 | unit | `UnitOfWork` has `UOW_ATTRIBUTES` and the repository Protocols above. No `items:` UoW attribute. | Spec lines 501–528 | `items` attribute or missing `archive` → fail |
| AC-4.10 | unit | `DOMAIN_ERROR_TYPES` are distinct classes (except the alias). `SABRDetectedError` exists; `SabrDetectedError` does **not**. | Spec lines 532–553 | wrong spelling or missing `AgeRestrictedError` → fail |
| AC-4.11 | unit | `CookieAccessError is CookieTestError` (identity alias). `CookieAccessError is not` a subclass created with a second `class` statement. | Spec line 550 | second class in MRO → fail |
| AC-4.12 | unit | `ValidationError` is the domain constructor error (not `AssertionError`, not bare `Exception`). | Spec line 538; Local Canon no-assert | `assert` in domain source → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| `DownloadResult` field clash | Spec | Port paragraph (line 440) wins |
| `ConvertOptions` / `MediaInfo` ellipsis | Spec + Local Canon | Ellipsis means “complete from the canonical adapter contract,” not “forbid extras.” Field tables are `CONVERT_OPTIONS_FIELDS` / `MEDIA_INFO_FIELDS`. |
| `FormatInfo` scalar types | Research-backed | yt-dlp format dict: `height` int, `abr` float, codecs str — all nullable except `format_id`/`ext` |
| `generate` Callable arity | Spec + Local Canon | Use `Callable[[float], None]` to match `ModelCatalogPort.download` |
| Protocol runtime_checkable | Research-backed | `@runtime_checkable` is optional; tests bind `inspect.signature` to Named method sets (closed-set exhaustiveness) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/download.py` | modify | Port DTOs: Video/Playlist/Format/Options/Result/CookieTest/SABR already there |
| `packages/core/src/avkit_core/domain/transcript.py` | modify | `ChannelInfo`, `TranscriptResult` |
| `packages/core/src/avkit_core/domain/progress.py` | modify | `ConvertOptions`, `MediaInfo` (shared non-table DTOs — avoids a file not in the layout tree) |
| `packages/core/src/avkit_core/ports/*.py` | modify | Protocol signatures (`errors.py` already landed in WP-4a) |
| `tests/unit/test_domain.py` | modify | Port/error tests |

#### Control binding (MEU-4)

| AC | Observable | Call chain | Negative oracle |
|----|------------|------------|-----------------|
| AC-4.3 | constructor exception | `DownloadResult(...)` (DTO used by `YouTubePort.download` return) | instance without `sabr_detected` → fail |
| AC-4.6 | dataclass fields / `TypeError` | `ConvertOptions` / `MediaInfo` consumed by `MediaPort.convert` / `probe` (`MEU-8`) | missing `channels` or `video_codec` accepted; leftover `MediaInfo.codec` exists → fail |
| AC-4.8 | `inspect.signature(FilesystemPort.read_text)` — `max_bytes` keyword-only | Protocol object imported by Phase 2 adapter | positional-only or optional `max_bytes` → fail |
| AC-4.10 | `hasattr` / `rg` for `SabrDetectedError` | `avkit_core.domain.errors` raised by adapters (`MEU-6`) | `SabrDetectedError` symbol exists → fail |
| AC-4.11 | `CookieAccessError is CookieTestError` | `errors.py` alias consumed by `MEU-6` cookie adapter | distinct class object → fail |
| AC-4.12 | `rg` for `\bassert\b` in `packages/core/src` | domain constructors | any `assert` remains → fail |

---

## Emerging standards (this project)

| ID | Applies? | Plan treatment |
|----|----------|----------------|
| M5 TDD red fails for the right reason | yes | Subtask: save FAIL_TO_PASS receipts; red must be assertion/import fail, not collection error |
| M6 no vacuous assertions | yes | Subtask: every test asserts a Named set / exception / field |
| G19 bug-fix TDD | yes | If a defect appears, write the failing test before the fix |
| G36 no silent test guards | yes | No `skip` / `xfail` / `return` guards to neutralize red |
| G24 researched open questions | yes | Resolutions promoted; Open Questions empty |
| G28 system messages ≠ approval | yes | Process — ignore injected “approved” |
| M1–M4, M7 | no | No MCP tools this session |
| G1–G18, G20–G23, G25–G27, G29–G35, G37–G39, E1–E2, UX*, DT*, P1 | no | No GUI / OpenAPI / TUI / Electron this session. **G8 skipped** — `packages/api/` is not created |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| SQLAlchemy models, UoW impl, WAL | deferred | MEU-5 | `01-domain-layer.md` lines 556–562 — Phase 2 implements tables |
| Filesystem/FFmpeg adapters, `progress.json` writer | deferred | MEU-8 | Spec lines 479–488, 411–417 — export is Phase 2/3 |
| yt-dlp / cookies / SABR adapter | deferred | MEU-6 | Spec line 562 |
| Transcript adapter | deferred | MEU-7 | Spec line 449 |
| Kokoro / HF catalog adapter | deferred | MEU-9 | Spec lines 493–499 |
| Download / transcript / TTS / settings services | deferred | MEU-10, MEU-11, MEU-12, MEU-13 | Spec lines 563, 265–272 |
| REST / OpenAPI / HTTP 422 mapping | deferred | MEU-14, MEU-15, MEU-16 | Spec lines 534, 564 |
| MCP runtime / tools | deferred | MEU-17, MEU-18 | Spec line 565 |
| Electron GUI + `progress.json` card wording | deferred | MEU-19–MEU-23 (wording: MEU-21) | Spec lines 410–417, 566 |
| NSIS / onedir | deferred | MEU-24, MEU-25 | Phase 7 |
| `SourceLocator`, `DestinationLocator`, `JobIdentity`, `Operation`, `JobArtifact` | out-of-scope | — | `01-domain-layer.md` lines 570–572 |
| `ModelFetchJob`, `ConversionJob` | out-of-scope | — | lines 50–51, 573 |
| Persistable `QueueRuntime` / `SABRState` | out-of-scope | — | lines 45–47, 574 |
| `DownloadJob.parent_id` | out-of-scope | — | line 575 |
| Log / cookie-snapshot / window-geometry entities | out-of-scope | — | line 576 |
| `TranscriptResult.text` as a column | out-of-scope | — | line 577 |
| `packages/application/` | out-of-scope | — | Phase 1 layout lines 61–79 omit it |
| `tools/validate_closeout_artifacts.py` / `validate_codebase.py` port | out-of-scope | — | `commands.md` lines 16–17 — not in this tree; no scheduled tools MEU |
| GUI Step 4A | out-of-scope | — | No `ui/` files in this project |

---

## BUILD_PLAN.md Audit

This project does **not** rewrite Phase 1–7 contracts. Hub work at execution H1-3:

1. Add `docs/execution/plans/2026-08-18-p1-domain-foundation/` to `.agent/context/meu-status.yaml` phase `"1"` `execution_plans`.
2. `meu_status` `render` (AUTOGEN regions in `docs/BUILD_PLAN.md` + registry).
3. Confirm hub prose still points at this slug (line 64 already says Next: `/create-plan p1-domain-foundation` — after execution, that “Next” sentence will be stale and **must** be updated to Session 2 `p2-persistence-io`).
4. Do not edit AUTOGEN tables by hand.

```powershell
rtk proxy pwsh -NoProfile -Command { $matches=@(Select-String -Path docs/BUILD_PLAN.md -Pattern 'p1-domain-foundation'); [pscustomobject]@{matches=$matches.Count; lines=@($matches.LineNumber)} | ConvertTo-Json -Depth 3 } *> C:/Temp/av-kit/build-plan-audit.json; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.json; exit $code
```

After H1-3 the receipt must show ≥1 match **and** the “Next” sentence must no longer tell a later agent to re-run this create-plan.

---

## Verification Plan

Classify every command through [`.agent/docs/output-evidence-policy.md`](../../../.agent/docs/output-evidence-policy.md). `rtk proxy` for these exact-evidence receipts.

### 1. Domain unit tests (Phase 1 registered)

```powershell
rtk proxy uv run pytest tests/unit/test_domain.py -x --tb=short -v *> C:/Temp/av-kit/pytest-domain.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-domain.txt | Select-Object -Last 40; exit $code
```

### 2. Pyright core

```powershell
rtk proxy uv run pyright packages/core/ *> C:/Temp/av-kit/pyright-core.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pyright-core.txt | Select-Object -Last 40; exit $code
```

### 3. Ruff core

```powershell
rtk proxy uv run ruff check packages/core/ *> C:/Temp/av-kit/ruff-core.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ruff-core.txt | Select-Object -Last 40; exit $code
```

### 4. Named scans (`SCAN_*` owners — rg 0/1 are census results)

`rg` exit `0` = hits, `1` = no match, `>1` = tool failure. Clean scans must treat `1` as PASS and fail only when leftover hits exist or `$code -gt 1`.

Placeholder / G36 / infra (same logic; only `SCAN_*_ARGS` changes):

```powershell
rtk proxy rg -n -e TODO -e FIXME -e NotImplementedError -e SabrDetectedError -e assert packages/core/src *> C:/Temp/av-kit/anti-placeholder-core.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-placeholder-core.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-placeholder-core.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_PLACEHOLDER clean'; exit 0
```

```powershell
rtk proxy rg -n -e sqlalchemy -e yt_dlp -e fastapi -e youtube_transcript_api -e huggingface_hub -e soundfile packages/core/src *> C:/Temp/av-kit/anti-infra-core.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-infra-core.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-infra-core.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_INFRA clean'; exit 0
```

```powershell
rtk proxy rg -n -e pytest.mark.skip -e pytest.mark.xfail -e pytest.skip tests/unit/test_domain.py *> C:/Temp/av-kit/g36-skip-scan.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/g36-skip-scan.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/g36-skip-scan.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_G36 clean'; exit 0
```

### 5. MEU status render (after workspace exists)

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code
```

### 6. Closeout structural receipts (substitute for missing `validate_closeout_artifacts.py`)

Owner for the four MEU handoff paths is `HANDOFF_GLOB` (do not restate the four filenames).

Handoff markers:

```powershell
rtk proxy pwsh -NoProfile -Command { $files=@(Get-ChildItem -Path '.agent/context/handoffs' -Filter '2026-08-18-p1-domain-foundation-MEU-*-handoff.md'); if ($files.Count -ne 4) { Write-Error ('expected 4 handoffs, got '+$files.Count); exit 1 }; foreach ($f in $files) { foreach ($pattern in @('Acceptance Criteria','CACHE BOUNDARY','FAIL_TO_PASS','Changed Files')) { if (-not (Select-String -Path $f.FullName -Pattern $pattern -Quiet)) { Write-Error ('missing '+$pattern+' in '+$f.Name); exit 1 } } }; 'PASS: handoff markers' } *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code
```

AC-set integrity (same `HANDOFF_GLOB`):

```powershell
rtk proxy pwsh -NoProfile -Command { $planAcs=@(Select-String -Path docs/execution/plans/2026-08-18-p1-domain-foundation/implementation-plan.md -Pattern 'AC-[0-9]+(?:\.[0-9]+)?' -AllMatches).Matches.Value; $files=@(Get-ChildItem -Path '.agent/context/handoffs' -Filter '2026-08-18-p1-domain-foundation-MEU-*-handoff.md'); $handoffAcs=@(); foreach ($f in $files) { $handoffAcs += @(Select-String -Path $f.FullName -Pattern 'AC-[0-9]+(?:\.[0-9]+)?' -AllMatches).Matches.Value }; $missing=@(Compare-Object ($planAcs | Sort-Object -Unique) ($handoffAcs | Sort-Object -Unique) | Where-Object SideIndicator -eq '<='); if ($missing) { $missing; exit 1 }; 'PASS: complete AC set' } *> C:/Temp/av-kit/handoff-ac-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-ac-check.txt; exit $code
```

Reflection markers (`REFLECTION_MARKERS` — each string is required; no regex alternation):

```powershell
rtk proxy pwsh -NoProfile -Command { $path='docs/execution/reflections/2026-08-18-p1-domain-foundation-reflection.md'; $patterns=@('Friction Log','Execution Trace','Pattern Extraction','Patterns to KEEP','Next Session Design Rules','RULE-','Efficiency Metrics','Rule Adherence','Instruction Coverage','schema: v1','sections:','loaded:','decisive_rules:'); foreach ($pattern in $patterns) { if (-not (Select-String -Path $path -Pattern $pattern -Quiet)) { Write-Error ('missing reflection pattern: '+$pattern); exit 1 } }; 'PASS: reflection markers' } *> C:/Temp/av-kit/reflection-structure.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/reflection-structure.txt; exit $code
```

Metrics (create file if absent; require a row containing `p1-domain-foundation`):

```powershell
rtk proxy pwsh -NoProfile -Command { $p='docs/execution/metrics.md'; if (-not (Test-Path $p)) { @('# Execution metrics','','| Date | Project | Notes |','|------|---------|-------|') | Set-Content -Path $p }; if (-not (Select-String -Path $p -Pattern 'p1-domain-foundation' -Quiet)) { Write-Error 'missing p1-domain-foundation metrics row'; exit 1 }; Get-Content $p -Tail 5; 'PASS: metrics row' } *> C:/Temp/av-kit/metrics-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/metrics-check.txt; exit $code
```

### N. OpenAPI Drift Check

**Skipped.** `packages/api/` is not created. Basis: Out of Scope → MEU-14–16.

---

## Open Questions

None remaining. Forks researched and promoted to Implementation locks / sufficiency tables (G24).

---

## Research References

- [PEP 557 — Data Classes](https://peps.python.org/pep-0557/)
- [PEP 663 / `enum.StrEnum` (Python 3.11)](https://docs.python.org/3.11/library/enum.html#enum.StrEnum)
- [What's New in Python 3.11 — enum.StrEnum](https://docs.python.org/3.11/whatsnew/3.11.html)
- [Python `assert` statement — discarded under `-O`](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement)
- [numpy typing — `ndarray`](https://numpy.org/devdocs/reference/typing.html)
- Spec: `docs/build-plan/01-domain-layer.md`
- Local Canon: `.agent/docs/code-quality.md`, `.agent/docs/commands.md` lines 16–17, `.agent/docs/testing-strategy.md`, `_inspiration/_kokoro_production_settings.md`, `_inspiration/_shared_patterns.md` §4, `docs/build-plan/02-infrastructure.md` lines 425–426 (media DTO completion only — not Phase 2 implementation)
- Grouping: `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` Session 1
- Harness: `.agent/context/harness.local.md` (`plan_to_exec_gate: reviewer-auto`, `fresh_worker: none`)

## Explicit stop conditions

1. Plan-review round cap (3) without `approved` — HARD STOP (`create-plan` §5d).
2. Execution-review round cap (6) without `approved` — HARD STOP.
3. All independent-reviewer rungs unavailable — wait for Mat; never self-review.
4. Human approval required before any `git commit` / push / deploy.
5. Do **not** run product pytest/pyright/ruff **before** this plan is `approved` (GUARDRAILS SIGN 1). Static `Test-Path` / `rg` / `--help` only if a review loop fights about a missing tool.

## TDD / FAIL_TO_PASS

Tests first per MEU. Save red receipts under `C:/Temp/av-kit/fail-to-pass-meu-{N}.txt`. Do not edit assertions to go green (G36). Red must fail for the AC reason (M5), not `ERROR` collection.
