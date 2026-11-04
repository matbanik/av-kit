---
project: "2026-08-19-p3-services"
date: "2026-08-19"
source: "docs/build-plan/03-service-layer.md"
meus: ["MEU-13", "MEU-10", "MEU-11", "MEU-12"]
status: "approved"
template_version: "2.0"
---

# Implementation Plan: Phase 3 Services

> **Project**: `2026-08-19-p3-services`
> **Build Plan Section(s)**: [03-service-layer.md](../../../build-plan/03-service-layer.md)
> **Status**: `draft`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 4 — MEU-13 → MEU-10 → MEU-11 → MEU-12

---

## Goal

Implement Phase 3 **application services** in `avkit_core/services/`. Services own workflows, in-memory queue/SABR/model-download runtimes, and status-machine writes. They talk only to frozen Phase 1 ports + a `UoWFactory`. They do not import `avkit_infra`, do not call yt-dlp/SQLAlchemy/FFmpeg/soundfile/huggingface_hub, and do not invent persistable columns or `ModelFetchJob`.

Session 2 UoW + Session 3 adapters stay frozen. Default-suite tests use **fake ports** + an in-memory UoW. One real tmp-SQLite smoke per service catches Protocol/method-name drift (G29). No live YouTube / HF / Kokoro.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json absent; Headroom has no approved disposition. Planning payloads are spec/source reads and exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before execution. Same absence basis is expected unless a graph file appears on disk.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-13 | `.agent/context/handoffs/2026-08-19-p3-services-MEU-13-handoff.md` |
| MEU-10 | `.agent/context/handoffs/2026-08-19-p3-services-MEU-10-handoff.md` |
| MEU-11 | `.agent/context/handoffs/2026-08-19-p3-services-MEU-11-handoff.md` |
| MEU-12 | `.agent/context/handoffs/2026-08-19-p3-services-MEU-12-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-19-p3-services-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB` (expected count **4**).

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-13a | MEU-13 Red: settings leaf table + extra=forbid | — | `shared` | `C:/Temp/av-kit/fail-to-pass-meu-13-settings.txt` |
| WP-13b | MEU-13 Green: `SettingsService` + `SETTINGS_KEY_TABLE` / wire maps | WP-13a | `compact_continue` | `avkit_core/services/settings.py`; compact then re-read `task.md` |
| WP-13c | MEU-13 Red: HealthService seq/ring/deps | WP-13b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-13-health.txt` |
| WP-13d | MEU-13 Green: `HealthService` + `ConsoleEvent` | WP-13c | `compact_continue` | `avkit_core/services/health.py`; `avkit_core/domain/health.py` |
| WP-10a | MEU-10 Red: add/archive/SABR/apply-defaults + `DOWNLOAD_TRANSITIONS` edges | WP-13d | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-10-queue.txt` |
| WP-10b | MEU-10 Green: `DownloadService` commands + `ExtractCoordinator` | WP-10a | `compact_continue` | `avkit_core/services/download.py`; `extract.py` |
| WP-10c | MEU-10 Red: worker pause/cancel/progress/NaN | WP-10b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-10-worker.txt` |
| WP-10d | MEU-10 Green: worker loop + hook methods | WP-10c | `compact_continue` | `avkit_core/services/download.py` |
| WP-11a | MEU-11 Red: add/start/resume/stop/requeue/retry | WP-10d | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-11-queue.txt` |
| WP-11b | MEU-11 Green: `TranscriptService` + parent/item machines | WP-11a | `compact_continue` | `avkit_core/services/transcript.py` |
| WP-11c | MEU-11 Red: fetch/compile/zip | WP-11b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-11-compile.txt` |
| WP-11d | MEU-11 Green: item fetch + compile/zip | WP-11c | `compact_continue` | `avkit_core/services/transcript.py` |
| WP-12a | MEU-12 Red: prepare steps + unknown id | WP-11d | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-12-prepare.txt` |
| WP-12b | MEU-12 Green: `TextPreparationService` | WP-12a | `compact_continue` | `avkit_core/services/prepare.py` |
| WP-12c | MEU-12 Red: TTS generate/cancel + ModelDownloadRuntime | WP-12b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-12-tts.txt` |
| WP-12d | MEU-12 Green: `TTSService` + `ModelService` | WP-12c | `compact_continue` | `avkit_core/services/tts.py`; `models.py` |

---

## User Review Required

None that block planning. Product forks below are sourced in Implementation locks (reviewer confirms the lock, does not invent a second behavior).

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `SERVICE_LAYOUT` | `services/{settings,health,download,transcript,tts,prepare,models,extract}.py` plus `domain/health.py` and `domain/wire.py` | this plan |
| `UoWFactory` | `Callable[[], UnitOfWork]` | Spec Construction |
| `SETTING_NAMESPACES` | `downloader`, `transcript`, `tts`, `app`, `ui` | frozen `settings.py` |
| `SETTINGS_KEY_TABLE` | see Implementation locks (GUI leaf keys + types + defaults; **no** dotted `ui.*`) | `06-gui.md` 978–1009; Phase 1 key-without-`.` |
| `SETTINGS_UI_API_KEYS` | `{theme}` | Spec Settings “API owns theme”; electron-store owns the rest |
| `THEME_VALUES` | `{dark, light}` | `06-gui.md` default `dark` |
| `LOG_LEVELS` | `{DEBUG, INFO, WARNING, ERROR, CRITICAL}` | `04-rest-api.md` ConsoleEventOut; `_shared_patterns.md` §1 |
| `QUALITY_WIRE_MAP` | `best→Best`, `2160p→P2160`, `1440p→P1440`, `1080p→P1080`, `720p→P720`, `480p→P480`, `360p→P360`, `240p→P240`, `144p→P144`, `lowest→Lowest` | `04-rest-api.md` 120; `06-gui.md` 439 |
| `AUDIO_WIRE_MAP` | `default→Default`, `best→Best`, `lowest→Lowest`, `low_webm→LowWebm`, `medium_webm→MediumWebm`, `standard_webm→StandardWebm`, `standard_m4a→StandardM4a`, `standard_mp3→StandardMp3`, `high_m4a→HighM4a` | `04-rest-api.md` 121 |
| `DEVICE_WIRE_MAP` | `auto→Auto`, `cuda→CUDA`, `mps→MPS`, `cpu→CPU` | `04-rest-api.md` 125 |
| `COOKIE_MODES` | `none`, `browser`, `file` | p2 lock; `06-gui.md` cookie_mode |
| `SABR_COMPAT_QUALITY` | `{QualityPreset.P360, QualityPreset.Lowest}` | Spec apply_lock |
| `SABR_COMPAT_AUDIO` | `SABR_RESTRICTED_AUDIO` (`{StandardMp3, HighM4a}`) — **allowed** set under SABR | frozen `enums.py`; Spec apply_lock |
| `DOWNLOAD_TRANSITIONS` | **extend** `Pending→{Downloading, QualityBlocked, Skipped}`; keep existing `Downloading→{Done,Failed,Cancelled,Skipped,QualityBlocked,AgeRestricted}`, `Failed→{Pending}`, `QualityBlocked→{Pending}` | p1 named graph + Phase 1 invariant 186 + Phase 3 apply_lock / archive-before-start |
| `TRANSCRIPT_PARENT_TRANSITIONS` | `Pending→{Processing}`; `Processing→{Paused, Done, Failed, Cancelled, Pending}`; `Paused→{Processing, Cancelled}`; `Cancelled→{Pending}`; `Failed→{Pending}` | Spec status machines + Stop/requeue/retry + boot recovery (`Processing→Pending`) |
| `TRANSCRIPT_ITEM_TRANSITIONS` | `Pending→{Done, Skipped, Failed}`; `Failed→{Pending}` | Spec item machine + `retry_failed_channel` |
| `TTS_TRANSITIONS` | `Pending→{Generating}`; `Generating→{Done, Failed, Cancelled}` | Spec TTS machine |
| `QUEUE_NAMES` | `{downloads, transcripts}` | frozen `queue.py` |
| `EXTRACT_CACHE_TTL_S` | `300` | Spec extract cache 5 minutes |
| `PROGRESS_COMMIT_INTERVAL_S` | `1.0` | Spec ~1s download progress |
| `CONSOLE_RING_CAPACITY` | `10000` | Spec HealthService |
| `SEQ_OWNER` | `HealthService` (one process-local counter + the structlog processor it registers). Nothing else increments `seq`. Restart → `1`. | Spec R2-4 |
| `REDACT_NEEDLES` | casefold substrings `bearer`, `cookie`, `authorization`, `avkit_token`, `mcp-token` | Spec “tokens, cookie bytes, Bearer redacted before enqueue” |
| `PREPARE_STEP_IDS` | `punctuation`, `symbols`, `numbers`, `currency`, `all_caps`, `chapter_markers`, `urls_emails`, `page_numbers`, `whitespace`, `chunk`, `kokoro` | Spec TextPreparationService |
| `PREPARE_DEFAULT_ON` | all `PREPARE_STEP_IDS` except `chapter_markers` | Spec defaults; `chapter_markers` off |
| `PREPARE_ORDER` | fixed document order of `PREPARE_STEP_IDS`; `enabled_steps` is a toggle set, not a reorder; `kokoro` last when enabled | Spec |
| `SPACY_MODEL` | `en_core_web_sm` | Spec 303; `06-gui.md` 819; inspiration §10 |
| `CHUNK_DEPENDENCY_ERROR` | `SpacyModelNotFoundError(DomainError)` — `chunk` enabled and model missing → this error only (Phase 4 maps 503). Do not fail process startup. | `07-distribution.md` 151 |
| `TTS_PROGRESS_RESOLUTION` | `1000` | p2 lock maps adapter `i/n` → `float`; frozen `Callable[[float], None]` cannot recover `i,n` |
| `LOG_FILE_APPEND_EXCEPTION` | `HealthService` may `Path.open("a", encoding="utf-8")` **only** for `{app_data}/logs/console.log` after redaction + `mkdir(parents=True)`. No other `open` in services. Do not use `read_text` (compile-only). | Spec 387 vs frozen `FilesystemPort` |
| `REQUIRED_DOWNLOAD_COMMANDS` | Spec command table: add/start/pause/resume/cancel/stop/remove/clear/reorder/`reset_failed`/get_queue/get_job/get_processor_state/get_sabr_status/check_sabr/force_sabr/clear_sabr/test_cookies/apply_defaults_to_pending | Spec 102–122 |
| `REQUIRED_TRANSCRIPT_COMMANDS` | add_channel/start/pause/resume/stop/requeue/retry_failed/remove/reorder/get_queue/get_job/list_items/compile_channel/get_processor_state/`recover_stale_processing` | Spec 188–203 + boot recovery |
| `REQUIRED_TTS_COMMANDS` | generate/prepare/cancel/get_status | Spec 314–318 |
| `TTS_SPEED_MIN` / `TTS_SPEED_MAX` | `0.5` / `2.0` | frozen `tts.py` |
| `TTS_OUTPUT_FORMATS` | `{MP3, WAV}` | frozen `tts.py` |
| `TEXT_PREVIEW_MAX` | `200` | frozen `tts.py` |
| `MODEL_DOWNLOAD_STATES` | `{Idle, Downloading, Failed}` | frozen `tts.py` |
| `SEED_VARIANT_IDS` | `kokoro-pt-fp32`, `kokoro-onnx-fp32`, `kokoro-onnx-fp16`, `kokoro-onnx-int8` | p2 lock |
| `COMPILE_READ_MAX_BYTES` | `20 * 1024 * 1024` | Research-backed bound for `FilesystemPort.read_text` (compile-only) |
| `TTS_WAV_SAMPLE_RATE` | `24000` | [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) 24 kHz |
| `TTS_MP3_CONVERT` | `ConvertOptions(codec="libmp3lame", bitrate_kbps=192, sample_rate=24000, channels=1)` | Spec generate step 9; Kokoro 24 kHz mono |
| `TRANSCRIPT_LANGUAGES_DEFAULT` | `["en"]` | Spec one-item fetch |
| `ARCHIVE_EXTRACTOR` | `"youtube"` | Phase 1 archive line |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-19-p3-services-MEU-*-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-19-p3-services` | MEU `execution_plan` (no trailing slash) |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-19-p3-services/` | phase `"3"` `execution_plans` |
| `HUB_NEXT_AFTER` | `/create-plan p4-rest-api` | grouping Session 5 |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | Codex r3 F1 pattern |
| `TEST_SERVICES` | `tests/unit/test_services.py` | Spec Validation 467 |
| `TEST_DOMAIN` | `tests/unit/test_domain.py` | Session 1; transition-graph extensions |
| `REGRESSION_TESTS` | `TEST_DOMAIN`, `tests/integration/test_sqlite_uow.py`, `tests/integration/test_filesystem_media.py`, `tests/integration/test_youtube_adapter.py`, `tests/integration/test_transcript_adapter.py`, `tests/integration/test_tts_models.py` | Sessions 1–3 |
| `SCAN_CORE_INFRA_ARGS` | `rg -n -e sqlalchemy -e yt_dlp -e fastapi -e youtube_transcript_api -e huggingface_hub -e soundfile -e onnxruntime -e kokoro -e avkit_infra packages/core/src` | p2 `SCAN_CORE_INFRA` + hexagonal; Finding 8 |
| `SCAN_OPEN_ARGS` | `rg -n -e "open\(" packages/core/src/avkit_core/services` | Finding 7; allow only `health.py` append helper |
| `SCAN_G36_ARGS` | `rg -n -e pytest.mark.skip -e pytest.mark.xfail -e pytest.skip tests/unit/test_services.py tests/unit/test_domain.py` | G36 |
| `SCAN_PLACEHOLDER_ARGS` | `rg -n -e TODO -e FIXME -e NotImplementedError packages/core/src/avkit_core/services` | anti-placeholder |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-19-p3-services-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-19-p3-services/implementation-plan.md` | `target_plan` exact match |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only | p2 Human-approved |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | completion-preflight |

`SETTINGS_KEY_TABLE` (define once; persist leaf `key` only):

| namespace | key | type | default |
|-----------|-----|------|---------|
| downloader | `path` | string | `~/Downloads/av-kit` |
| downloader | `ffmpeg_path` | string | `""` |
| downloader | `quality` | string | `1080p` |
| downloader | `audio_only` | boolean | `false` |
| downloader | `audio_format` | string | `default` |
| downloader | `cookie_mode` | string | `none` |
| downloader | `cookie_browser` | string | `chrome` |
| downloader | `cookie_browser_profile` | string | `""` |
| downloader | `cookie_file_path` | string | `""` |
| downloader | `archive_tracking` | boolean | `true` |
| downloader | `yt_dlp_debug` | boolean | `false` |
| transcript | `output_dir` | string | `~/Documents/Transcripts` |
| transcript | `requests_per_hour` | number | `300` |
| transcript | `delay_between_requests` | number | `6` |
| transcript | `max_retries` | number | `3` |
| transcript | `retry_delay` | number | `30` |
| transcript | `batch_size` | number | `50` |
| transcript | `pause_between_batches` | number | `300` |
| transcript | `playlist_end` | number | `0` |
| transcript | `max_words_per_document` | number | `490000` |
| tts | `models_directory` | string | `~/.avkit/models` |
| tts | `voice` | string | `am_eric` |
| tts | `speed` | number | `1.0` |
| tts | `output_format` | string | `MP3` |
| tts | `output_path` | string | `~/Documents` |
| tts | `device` | string | `auto` |
| tts | `chunk_max_chars` | number | `250` |
| tts | `input_text` | string | `""` |
| app | `log_level` | string | `INFO` |
| app | `log_to_file` | boolean | `false` |
| app | `console_visible` | boolean | `true` |
| ui | `theme` | string | `dark` |

Unknown namespace, unknown key, wrong type, out-of-range number, unknown enum wire, or extra mapping key → `ValidationError`. Cookie **bytes** are never a value.

---

## Implementation locks (planning resolutions)

| Topic | Lock | Source |
|-------|------|--------|
| Package home | Services live in `packages/core/src/avkit_core/services/`. Do **not** create `avkit_core/application/`. | Spec Package layout; architecture lists both — Phase 3 file wins |
| Hexagonal | Never `import avkit_infra` from core. Constructor deps = ports + `UoWFactory` (+ `ExtractCoordinator` + `HealthService` app_data path). | Spec Construction; p2 RULE carry-forward |
| Frozen ports | Do not edit `avkit_core/ports/**`. Extra repo methods (`has_video_id`, bulk `reset_failed()`) are **not** on the Protocol — services must not call them. | p1 freeze; `ports/storage.py` |
| Single graph | Status writes go through entity `transition()` (or `DownloadJob.reset_failed()`). Do not `replace(job, status=…)` for machine edges. | p1 AC-3.3; Spec “illegal transitions raise” |
| `DOWNLOAD_TRANSITIONS` extension | Add `Pending → QualityBlocked` (apply_lock / add-time uses insert; lock of existing Pending uses transition) and `Pending → Skipped` (archive re-check before start). Do **not** invent a second service-only graph. | Phase 1 invariant 186; Spec apply_lock + archive-before-start; p1 “one graph” |
| `reset_failed(job_id)` | `get` → `DownloadJob.reset_failed()` → `save`. Do **not** call `DownloadRepository.reset_failed()` (bulk-all-Failed, no id). | Spec command table; frozen Protocol; Session 2 repo impl |
| Dedup | In-queue skip = `video_id` already in `list_ordered()`. Do not call non-Protocol `has_video_id`. | Spec add flow; frozen Protocol |
| Archive skip | If `downloader.archive_tracking` and `archive.get(ARCHIVE_EXTRACTOR, video_id)` → **insert** `Skipped` (not a transition). Clear All / remove must not delete archive rows. | Spec add flow + Phase 1 |
| SABR session | In-memory `SABRStatus` on `DownloadService` only. Default `Inactive`. `check_sabr` / `force_sabr` / result.`sabr_detected` → `Active` + `apply_lock`. `clear_sabr` → `Inactive` and `QualityBlocked → Pending`. | Spec; Human-approved 2026-08-18 |
| `apply_lock` | Jobs in `{Pending, QualityBlocked}` whose quality ∉ `SABR_COMPAT_QUALITY` (or `audio_only` and format ∉ `SABR_COMPAT_AUDIO`) → `QualityBlocked`. Compatible Pending stay Pending. | Spec apply_lock |
| Settings quality rewrite | Changing settings does **not** rewrite queue rows. Only `apply_defaults_to_pending()` updates `Pending`/`QualityBlocked` from current `downloader.quality` / audio defaults. | Spec 178 |
| Wire maps | Settings store **GUI wire strings**. Domain jobs store enums. Codecs live in `domain/wire.py` so Phase 4 schemas import them (map is not SQLite). Unknown wire → `ValidationError` (fail-closed). | `04-rest-api.md` 114–126; extra=forbid |
| Dotted `ui.*` | `ui.rail.collapsed` and `ui.panel.console.height` are **unknown keys** here (electron-store, MEU-19/23). Only `ui.theme`. | Phase 1 `key` without `.`; Spec “one owner per key” |
| `playlist_end` | Frozen `extract_video_ids(channel_url)` has no end arg. Service **slices** the returned list when `transcript.playlist_end > 0`. Adapter ctor `playlist_end` remains MEU-14 composition. | p2 lock; frozen Protocol |
| `DOWNLOAD_HOOK_WIRING` | Frozen `YouTubePort.download` has no progress/stop. `DownloadService` exposes `on_download_progress(downloaded: int, total: int \| None, speed: float \| None)` and `should_stop() -> bool`. Fakes call those methods. **MEU-14** binds `YouTubeAdapter(on_progress=…, should_stop=…, playlist_end=…, yt_dlp_debug=…)`. | p2 ctor lock; Spec worker progress; G29 |
| Progress NaN (RULE-1) | `on_download_progress` skips the UoW write when downloaded/total/speed is non-finite. Do not `int(nan)`. | p2 exec F1; Next Session RULE-1 |
| Cookie errors (RULE-2) | `test_cookies` / download cookie failures: re-raise `CookieTestError` with `__cause__` intact. Do not wrap as `DomainError`. | p2 exec F2 |
| Device `.to()` (RULE-3) | `ModelService.load` calls `TTSPort.load_model` only. Do not import `torch` or call `.to()/.eval()` in core. | p2 exec F3; frozen port |
| Extract coordinator | One shared `ExtractCoordinator` (mutex + `EXTRACT_CACHE_TTL_S` memory cache keyed by stripped URL). Injected into Download + Transcript. Restart empties cache. | Spec extract cache/lock |
| Worker | One `threading.Thread` per module processor (daemon). Injectable `sleep` (default `time.sleep`) so tests do not wait real delays. `start_*` returns immediately. | Spec Threading |
| HTTP codes | Services raise `ValidationError` / `NotFoundError` / `ConflictError`. Phase 4 maps 422/404/409. Do not return status ints. | Spec Validation; `04-rest-api.md` |
| Transcript Stop | Parent `Processing`/`Paused` → `Cancelled`; unfinished items stay `Pending`; terminal items unchanged; `current_job_id=None`; runtime `Idle`. | Spec R2-3 |
| Transcript start vs resume | `start` selects **Pending parents only** (`ConflictError` if runtime already `Processing`). `resume` only from runtime/parent `Paused`. `retry_failed_channel` only from parent `Failed`. `requeue_channel` only from parent `Cancelled`. | Spec commands |
| Boot recovery | `TranscriptService.recover_stale_processing()`: parents still `Processing` → `Pending`. `Paused` stays. API lifespan (MEU-14) **calls this method** — it does not open a repo itself. | Spec Boot recovery; G29 |
| Compile / zip | Compile reads Done item `path`s via `filesystem.read_text(..., max_bytes=COMPILE_READ_MAX_BYTES)`. Split volumes at `transcript.max_words_per_document`. Names `{channel_slug}_volN.md` under `compiled/`. Zip **Done item paths** with stdlib `zipfile` (explicitly allowed); do not add a list-dir port. Set `job.zip_path`. Failed parent: no compile/zip. | Spec Compile/Zip; Spec “no direct open” except named `zipfile` |
| `progress.json` | Optional `write_progress_export` after item/job progress. **Never** read it to resume. | Spec add flow / worker |
| Prepare | Unknown step id → `ValidationError`. Disabled ids omitted. `PREPARE_ORDER` fixed. **`chunk` uses spaCy `SPACY_MODEL`** for sentence boundaries, then packs to `chunk_max_chars` (default 250) and comma-splits oversized sentences (min 3 words) per inspiration §10. Missing model → `CHUNK_DEPENDENCY_ERROR` only (Phase 7 degrade; do not fail startup). Tests mock `spacy.load`. Add `spacy` to core deps (`uv sync --all-packages`). Bundling the model file into NSIS is MEU-25. `kokoro` step: spell numbers, space acronyms, split sentences > 25 words, straight quotes, no ellipses. | Spec 303; `06-gui.md` 819; `07-distribution.md` 151 |
| TTS body | `text` argument is the sole body. `text_hash` = SHA-256 hex of **raw** input. `text_preview` = first `TEXT_PREVIEW_MAX` chars. Do not persist `text`. Do not `read_text(source_path)` (R2-6). Empty text / speed outside range / format ∉ `TTS_OUTPUT_FORMATS` / model not loaded → `ValidationError`. | Spec generate flow |
| TTS cancel | Cooperative flag checked in `on_progress` → job `Cancelled`. | Spec |
| Model download runtime | At most one HF fetch. `download()` while `Downloading` → `ConflictError`. Success → `models.mark_downloaded(variant_id, path)` then `Idle`. Failure → runtime `Failed` + `ModelDownloadError`; variant stays not downloaded. Process restart → `Idle`. No `ModelFetchJob`. | Spec ModelService |
| Sideload merge | `list_available` = catalog rows ∪ `catalog.sideload(models_directory)` (in-memory merge; persist only when `download` succeeds via `mark_downloaded`). | Spec list_available |
| Health seq | structlog processor registered by `HealthService` assigns the next `seq`, redacts `REDACT_NEEDLES`, appends to a `deque(maxlen=CONSOLE_RING_CAPACITY)`, emits the same JSON to stdout. `record_startup_metric` is a log event (gets a seq). Uvicorn/non-JSON stdout is not given a backend seq (Phase 6). | Spec; [structlog processors](https://www.structlog.org/en/stable/processors.html) |
| `app.log_to_file` | When true, `LOG_FILE_APPEND_EXCEPTION`: after redaction, append one UTF-8 line to `{app_data}/logs/console.log`. Existing file is preserved (append, not overwrite). False/default: no file write. `SCAN_OPEN` must show `open(` only in `health.py`’s append helper. | Spec 387; Finding 7 |
| structlog dep | Add `structlog` to `packages/core` deps. `uv sync --all-packages`. | Spec Logging |
| Fake UoW | In-memory dict repos implementing the **Protocol method set only**. | Spec Testing |
| G29 smoke | One tmp-SQLite test per service constructs the Session 2 UoW factory and exercises one write (`settings.set` / `downloads.add` / `transcripts.add_job` / `tts_jobs.add`) so a missing Protocol method fails. | G29 |
| Live network | Forbidden in the default suite. | Spec Testing 458 |
| `uv sync` | After dep adds: `uv sync --all-packages`. | p2 Next Day Outline |
| Types | No `assert` for user-visible failures. | code-quality; Python `-O` |

---

## Proposed Changes

### MEU-13 — `svc-settings-health`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `SettingsService.set(namespace, key, value)` | `SETTINGS_KEY_TABLE` + wire maps | type/range/enum per row | unknown key/namespace → `ValidationError` |
| `SettingsService.set_namespace(namespace, mapping)` | same | same; create/update parity | extra mapping key → `ValidationError` (forbid) |
| `HealthService.console_snapshot(after_seq)` | `after_seq: int >= 0` | — | non-int → `ValidationError` |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-13.1 | unit | `get`/`get_namespace` fill defaults from `SETTINGS_KEY_TABLE` when no row exists. | Spec Settings; `06-gui.md` 978–1009 | missing key still returns default, not `None` |
| AC-13.2 | unit | `set` / `set_namespace` persist leaf keys; values round-trip with declared types. | Spec; Local Canon Phase 2 Setting | boolean stored as bool, not `"true"` leak into `get` |
| AC-13.3 | unit | Unknown namespace, unknown key, extra mapping key, wrong type, unknown quality/audio/device/theme/log_level wire, `tts.speed` outside `[TTS_SPEED_MIN, TTS_SPEED_MAX]`, negative transcript counts, `playlist_end < 0` → `ValidationError`. | Spec extra=forbid; Boundary Input | `set_namespace("downloader", {"quality":"1080p","nope":1})` accepted → fail |
| AC-13.4 | unit | Dotted keys `rail.collapsed` / `panel.console.height` under `ui` → `ValidationError`. Cookie-byte-shaped values rejected (length + `HTTP_COOKIE`/`#HttpOnly_` needles). | Local Canon Phase 1 key; Spec “cookie bytes never settings” | `ui` + `theme` still works |
| AC-13.5 | unit | **Control `SEQ_OWNER`.** Observable: `ConsoleEvent.seq`. Chain: `HealthService` structlog processor ← any `structlog.get_logger(module=…).info/error`. Two log events → `seq` 1 then 2. Negative: a second allocator (test monkeypatch of a module-level counter outside `HealthService`) is not used; `console_snapshot` after restart-equivalent new instance starts at 1. | Spec R2-4 | two services incrementing seq independently → fail |
| AC-13.6 | unit | Ring drops oldest after `CONSOLE_RING_CAPACITY`. `console_snapshot(after_seq)` returns only `seq > after_seq`. | Spec | `after_seq` equal to last seq returns `[]` |
| AC-13.7 | unit | **Control redact.** Observable: `ConsoleEvent.message` and stdout JSON. Chain: processor before enqueue. Negative: a log containing `Bearer abc` stores `[REDACTED]`, never `abc`. | Spec | cookie file contents in message survive → fail |
| AC-13.8 | unit | `liveness()` is process-up (`ok=True`). `dependencies()` returns `ffmpeg_version` + `ytdlp_version` from `MediaPort` / `YouTubePort` (None allowed). `record_startup_metric` emits a structured log (gets a seq) and writes **no** table row. | Spec HealthService | metric insert into settings/jobs → fail |
| AC-13.9 | integration | G29 smoke: real tmp UoW `settings.set` then `get` matches. | G29; Session 2 UoW | fake-only pass with missing `SettingsRepository.set` on real UoW → fail |
| AC-13.10 | unit | **Control `LOG_FILE_APPEND_EXCEPTION`.** Observable: `{app_data}/logs/console.log` bytes. Chain: log event → processor redact → `_append_console_log` when `app.log_to_file` is true. Restart-equivalent second append keeps the first line. Negative: secret survives; `read_text` used; `open(` outside `health.py`; overwrite instead of append. | Spec 387 | — |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Leaf key table + defaults | Spec + Local Canon `06-gui.md` | `SETTINGS_KEY_TABLE` |
| extra=forbid / create-update parity | Spec; `04-rest-api.md` 110 | AC-13.3 |
| Dotted ui keys | Local Canon Phase 1 + Spec one-owner | reject; MEU-19 |
| seq ownership | Spec R2-4 | `SEQ_OWNER` |
| Redaction needles | Spec + Research-backed structlog processor | `REDACT_NEEDLES` |
| ConsoleEvent persistable? | Spec “in-process ring” | non-persistable VO in `domain/health.py` |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/wire.py` | new | `QUALITY_WIRE_MAP`, `AUDIO_WIRE_MAP`, `DEVICE_WIRE_MAP`, theme/log_level wires |
| `packages/core/src/avkit_core/domain/health.py` | new | `ConsoleEvent`, `DependencyHealth`, `HealthLiveness` |
| `packages/core/src/avkit_core/services/settings.py` | new | `SettingsService` |
| `packages/core/src/avkit_core/services/health.py` | new | `HealthService` |
| `packages/core/pyproject.toml` | modify | `structlog` dep |
| `TEST_SERVICES` | new | AC-13.* |

---

### MEU-10 — `svc-download`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `add_to_queue(url, quality, audio_only, audio_format)` | method types | `url` non-empty; `QualityPreset` / `AudioFormat` / bool | extra kwargs rejected by signature |
| `test_cookies(mode, browser, profile, cookie_file)` | `COOKIE_MODES` + Path \| None | unknown mode → `ValidationError` | no cookie-byte param |
| `reorder_queue(job_ids)` | permutation of current ids | else `ValidationError` | — |
| `reset_failed(job_id)` | UUID + `Failed` | else `ConflictError` / `NotFoundError` | — |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-10.1 | unit | `extract_info`: `VideoInfo` → 1 job; `PlaylistInfo` → N jobs; title fallback `video_id`. | Spec add flow | playlist of 3 inserts 1 → fail |
| AC-10.2 | unit | Duplicate `video_id` already in queue is skipped (warn log), not inserted. | Spec | second add of same id increases count → fail |
| AC-10.3 | unit | Archive hit + `archive_tracking` → insert `Skipped`. Tracking off → `Pending`. `clear_queue` keeps archive. | Spec; Phase 1 | Clear All deletes archive → fail |
| AC-10.4 | unit | **Control `apply_lock`.** Observable: `DownloadJob.status`. Chain: `force_sabr` / `check_sabr` Active / worker `sabr_detected` → `apply_lock` → `save`. Incompatible `Pending` → `QualityBlocked` via `DOWNLOAD_TRANSITIONS`. `P360`/`Lowest` stay `Pending`. `clear_sabr` → those `QualityBlocked` → `Pending`. | Spec apply_lock | `replace` without transition accepts `Done → QualityBlocked` → fail |
| AC-10.5 | unit | SABR Active at add-time inserts incompatible jobs as `QualityBlocked` (constructor insert, not illegal transition). | Spec add flow | insert uses `Downloading` → fail |
| AC-10.6 | unit | `apply_defaults_to_pending` updates only `Pending`/`QualityBlocked`; returns count; `Downloading`/`Done` unchanged. | Spec 178 | Done quality rewritten → fail |
| AC-10.7 | unit | Processor: `Idle→Processing⇄Paused→Idle`. `pause` finishes current then `Paused`; other items stay `Pending` (no `DownloadStatus.Paused`). `cancel`/`stop_processing` (alias) → in-flight `Cancelled`, runtime `Idle`. | Spec queue runtime + commands | item status `Paused` → fail |
| AC-10.8 | unit | Worker: first Pending by `queue_position`; `Downloading` + commit; `youtube.download(options_from(job, settings, sabr))`; Done + archive.add; `AgeRestrictedError` → `AgeRestricted`; `DownloadCancelledError` → `Cancelled` + Idle; other `DomainError` → `Failed` + message. | Spec worker | UoW held across fake download (no commit before download returns) → fail |
| AC-10.9 | unit | **Control progress finite.** Observable: persisted `progress`/`speed_bps`. Chain: `on_download_progress` → short UoW. Negative: NaN/inf downloaded/total/speed → no save / no exception. | Spec; RULE-1 | `int(nan)` raises → fail |
| AC-10.10 | unit | Cookie settings build `DownloadOptions` (mode/path/browser only). `CookieTestError` from `OSError` propagates with `__cause__`. `test_cookies` does not persist bytes. | Spec; RULE-2 | `__cause__` dropped → fail |
| AC-10.11 | unit | **Control extract mutex+cache (download side).** Observable: FakeYouTube `extract_info` in-flight max. Chain: `add_to_queue` → injected `ExtractCoordinator`. Same stripped URL within `EXTRACT_CACHE_TTL_S` → 1 call. Concurrent download adds: overlap 0. Cross-service overlap is AC-11.15 (MEU-11 owns `add_channel`). | Spec extract cache/lock | two overlapping extract_info → fail |
| AC-10.12 | unit | `reorder_queue` requires a permutation; `remove_from_queue` deletes row, files/archive stay; `get_job` missing → `NotFoundError`; illegal transition → `ConflictError`. | Spec | non-permutation accepted → fail |
| AC-10.13 | unit | `Pending → Skipped` via `transition` when archive hits before start; `Done → QualityBlocked` still `ConflictError`. | Local Canon extended graph | second graph in service dict → fail |
| AC-10.14 | integration | G29 smoke: real tmp UoW add + list_ordered. | G29 | Protocol miss → fail |
| AC-10.15 | unit | `reset_failed(job_id)`: only that Failed row → Pending (error/progress cleared) via `DownloadJob.reset_failed`; other Failed rows unchanged; missing → `NotFoundError`; not Failed → `ConflictError`. Fake repo `reset_failed()` (bulk) call count stays 0. | Spec 113; Finding 3 | bulk repo method used → fail |
| AC-10.16 | unit | `REQUIRED_DOWNLOAD_COMMANDS` getters: `get_queue` is `list_ordered`; `get_processor_state` returns session `QueueRuntime`; `get_sabr_status` does not call `check_sabr_status`. | Spec 114–117 | get_sabr_status hits YouTube → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Pending→QualityBlocked missing from p1 table | Spec apply_lock + p1 invariant 186 vs p1 AC-3.3 | **extend** named `DOWNLOAD_TRANSITIONS` (one graph) |
| Progress hooks not on Protocol | Local Canon p2 ctor | `DOWNLOAD_HOOK_WIRING`; MEU-14 binds adapter |
| `reset_failed` arity | Spec job_id vs Protocol bulk | entity method + save |
| Playlist titles | Spec “when cheap” | `PlaylistInfo` has no per-id titles → `video_id` fallback |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/download.py` | modify | `DOWNLOAD_TRANSITIONS` Pending edges |
| `packages/core/src/avkit_core/services/extract.py` | new | `ExtractCoordinator` |
| `packages/core/src/avkit_core/services/download.py` | new | `DownloadService` |
| `TEST_DOMAIN` | modify | new legal/illegal edges |
| `TEST_SERVICES` | modify | AC-10.* |

---

### MEU-11 — `svc-transcript`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `add_channel(channel_url)` | non-empty URL | duplicate URL → `ConflictError` | — |
| `requeue_channel` / `retry_failed_channel` / `resume_processing` | parent status machine | wrong status → `ConflictError` | — |
| `reorder_queue(job_ids)` | permutation of channel ids | else `ValidationError` | — |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-11.1 | unit | Add: reject duplicate URL; resolve ids (slice `playlist_end`); `ChannelInfo` name; `output_dir={transcript.output_dir}/{slug}`; `ensure_channel_dirs`; parent `Pending` + `replace_items` Pending; do not read `progress.json`. | Spec add flow | resume from progress.json → fail |
| AC-11.2 | unit | `start` picks Pending parents only; `ConflictError` if runtime already Processing. Ignores Paused/Failed/Cancelled/Done. | Spec start vs resume | start resumes Paused → fail |
| AC-11.3 | unit | `resume` only from Paused (runtime or parent); else `ConflictError`. Parent `Paused→Processing`. | Spec | resume from Failed succeeds → fail |
| AC-11.4 | unit | **Control Stop.** Observable: parent `Cancelled`, leftover items `Pending`, terminal items unchanged, runtime `Idle`, `current_job_id is None`. Chain: `stop_processing`. Negative: Stop rewrites `Done` items → fail. | Spec R2-3 | — |
| AC-11.5 | unit | `requeue_channel`: `Cancelled→Pending` only; terminal items stay. Else `ConflictError`. `retry_failed_channel`: parent `Failed→Pending`; Failed items → Pending via `TRANSCRIPT_ITEM_TRANSITIONS`; Done/Skipped stay. | Spec | requeue from Pending → fail |
| AC-11.6 | unit | Item fetch: `None` → Skipped (no file); `TranscriptRetryableError` → sleep `retry_delay` via injected sleep, `retry_count++`, then Failed at `max_retries`; success → atomic raw md + frontmatter (`video_id`, `title`, `channel`, `url`, `date` if known) via `write_text_atomic`; discard `result.text`; `recompute_word_count`; short UoW. | Spec one item | text stored on job row → fail |
| AC-11.7 | unit | Delay/`batch_size`/`pause_between_batches` honored via injected sleep (counts, not wall clock). Pause after current video. | Spec worker | real 300s sleep in unit test → fail |
| AC-11.8 | unit | All items terminal: any Failed → parent Failed, **no** compile/zip; else compile + zip + Done + `zip_path`. | Spec worker | Failed parent still zipped → fail |
| AC-11.9 | unit | Compile: H1/TOC/H2; split when words would exceed `max_words_per_document`; `{slug}_vol1.md`, `_vol2.md`; overwrite on re-run; uses `read_text` compile-only. | Spec Compile | compile reads SQLite text body → fail |
| AC-11.10 | unit | Zip uses Done item paths; raw files unchanged. | Spec Zip | raw deleted → fail |
| AC-11.11 | unit | `recover_stale_processing`: Processing parents → Pending via `TRANSCRIPT_PARENT_TRANSITIONS`; Paused unchanged. | Spec Boot recovery | Paused reset; raw `replace` without transition → fail |
| AC-11.12 | unit | `remove_channel` cascade items, files stay. Parent illegal edge → `ConflictError`. | Spec | files deleted → fail |
| AC-11.13 | integration | G29 smoke: real tmp UoW add_job + list_items. | G29 | — |
| AC-11.14 | unit | `REQUIRED_TRANSCRIPT_COMMANDS` remaining: `reorder_queue` permutation; `get_queue` ordered with aggregates; `get_job` + counts; `list_items`; `get_processor_state`; `compile_channel` callable on Done items independently of auto-Done. Missing job → `NotFoundError`. | Spec 198–203; Finding 3 | — |
| AC-11.15 | unit | **Control shared extract mutex (cross-service).** Observable: combined FakeYouTube in-flight max for `extract_info` + `extract_video_ids`. Chain: one injected `ExtractCoordinator` into `DownloadService` **and** `TranscriptService`. Overlap `add_to_queue` with `add_channel` → in-flight max == 1. | Spec extract cache/lock; Finding 4 | transcript calls port directly → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| playlist_end vs frozen port | Local Canon p2 | slice in service |
| ChannelInfo vs extract DTO | Spec | build from PlaylistInfo/VideoInfo |
| Zip without list_dir | Spec zipfile + item paths | zip known Done paths |
| Frontmatter date | Spec prefer yt-dlp date | omit when unknown |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/transcript.py` | modify | `transition` + `TRANSCRIPT_*_TRANSITIONS` |
| `packages/core/src/avkit_core/services/transcript.py` | new | `TranscriptService` |
| `TEST_DOMAIN` / `TEST_SERVICES` | modify | AC-11.* |

---

### MEU-12 — `svc-tts-models`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `TextPreparationService.prepare(text, enabled_steps, chunk_max_chars)` | `PREPARE_STEP_IDS` | unknown id → `ValidationError` | extra step id forbid |
| `TTSService.generate(...)` | speed/format/voice/text | empty text / range / format / not loaded | `source_path` metadata only |
| `ModelService.download(variant_id)` | catalog id | unknown → `NotFoundError`; in-flight → `ConflictError` | no fetch-job body |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-12.1 | unit | Disabled steps omitted; order is `PREPARE_ORDER`; `kokoro` last when enabled; unknown id → `ValidationError`. | Spec Prepare | enabled_steps reorder changes output order → fail |
| AC-12.2 | unit | `chunk` uses mocked `spacy.load(SPACY_MODEL)` sentence boundaries then packs to `chunk_max_chars` (default 250). Missing model → `CHUNK_DEPENDENCY_ERROR` (other steps still run if `chunk` disabled). `kokoro` step: numbers spelled, acronyms spaced, sentences ≤ 25 words, straight quotes, no `...`. | Spec 303; `06-gui.md` 819; `07-distribution.md` 151 | missing model silently uses regex → fail |
| AC-12.3 | unit | Generate: hash/preview only (not full text); require `ModelStatus.is_loaded`; resolve `VoiceConfig` from `list_voices`; `source_path` not read (`FilesystemPort.read_text` call count 0). | Spec; R2-6 | `read_text(source_path)` → fail |
| AC-12.4 | unit | WAV via `write_audio_wav`; MP3 also calls `MediaPort.convert` with `TTS_MP3_CONVERT`; `output_path` = mp3. No `soundfile`. `open(` only via `LOG_FILE_APPEND_EXCEPTION` in health. | Spec | service writes mp3 itself → fail |
| AC-12.5 | unit | **Control `TTS_PROGRESS_RESOLUTION`.** Observable: `TTSJob.segments_done` / `segments_total`. Chain: `TTSPort.generate(..., on_progress)` → service mapper → short UoW. On start `segments_total=1000`, `segments_done=0`. Finite `f` in `[0,1]` → `segments_done = clamp(round(f * 1000), 0, 1000)`. `f=0.25` → 250/1000; `f=1.0` → 1000/1000. Non-finite skipped (RULE-1). `f` outside `[0,1]` → `ValidationError`. Cancel between callbacks → `Cancelled`. | Spec 328; p2 fraction mapping; Finding 6 | raw `f` stored as done; NaN written |
| AC-12.6 | unit | Illegal TTS edge → `ConflictError`. Empty text / speed/format invalid / not loaded → `ValidationError`. | Spec | — |
| AC-12.7 | unit | **Control ModelDownloadRuntime.** Observable: `state` **and** `fraction`. Chain: `ModelCatalogPort.download(..., on_progress)` → runtime. Start `Downloading` + `fraction=0`. Intermediate finite `0.4` persists `0.4`. Success → `mark_downloaded` + `Idle`. Failure → `Failed` + not downloaded. Second `download` while Downloading → `ConflictError`. Non-finite / `>1` / `<0` callback skipped or `ValidationError` (fail-closed). Restart-equivalent new service → `Idle`. | Spec 349; Finding 5 | callback discarded, fraction stays 0 through a 0.4 tick → fail |
| AC-12.8 | unit | `list_available` = catalog ∪ sideload; `list_downloaded` filters `is_downloaded`. `load`/`unload`/`get_status` (model) delegate to `TTSPort`. No torch import. | Spec; RULE-3 | — |
| AC-12.9 | integration | G29 smoke: real tmp UoW TTSJob add (hash/preview only). | G29 | full text column → fail |
| AC-12.10 | unit | `TTSService.get_status(job_id)` returns the row; missing → `NotFoundError`. | Spec 318; Finding 3 | — |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| spaCy vs rules | Spec 303 + `06-gui.md` 819 + Phase 7 degrade | `SPACY_MODEL` + `CHUNK_DEPENDENCY_ERROR`; bundle file → MEU-25 |
| source_path | Spec R2-6 | never read |
| mark_downloaded | Local Canon frozen `(variant_id, path)` | p2 lock |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/tts.py` | modify | `TTSJob.transition` + `TTS_TRANSITIONS` |
| `packages/core/src/avkit_core/domain/errors.py` | modify | `SpacyModelNotFoundError` (`CHUNK_DEPENDENCY_ERROR`) |
| `packages/core/pyproject.toml` | modify | `spacy` dep (`uv sync --all-packages`) |
| `packages/core/src/avkit_core/services/prepare.py` | new | `TextPreparationService` (`SPACY_MODEL`) |
| `packages/core/src/avkit_core/services/tts.py` | new | `TTSService` |
| `packages/core/src/avkit_core/services/models.py` | new | `ModelService` |
| `TEST_SERVICES` | modify | AC-12.* |

---

## Control-binding register (PR-8)

| AC | Observable | Production chain | Negative oracle |
|----|------------|------------------|-----------------|
| AC-13.3 | `ValidationError` from `set_namespace` | `SettingsService.set_namespace` → key check vs `SETTINGS_KEY_TABLE` | extra key accepted |
| AC-13.5 | `ConsoleEvent.seq` | app log → HealthService processor → ring | shared/stolen counter; seq not monotonic |
| AC-13.7 | redacted `message` | processor before enqueue | secret survives |
| AC-10.4 | `job.status` | `force_sabr`/`check_sabr`/`sabr_detected` → `apply_lock` → `save` | P360 blocked; Done blocked; bypass `transition` |
| AC-10.9 | row `progress`/`speed_bps` | `on_download_progress` → UoW | NaN written or raised |
| AC-10.11 | extract call count / in-flight | `add_to_queue` → `ExtractCoordinator` | overlap or cache miss inside TTL |
| AC-11.15 | combined extract in-flight max | shared coordinator: `add_to_queue` plus `add_channel` | transcript bypasses lock |
| AC-11.4 | parent/items/runtime | `stop_processing` | Done items rewritten |
| AC-13.10 | `{app_data}/logs/console.log` | processor → `_append_console_log` | secret / overwrite / `read_text` |
| AC-10.15 | selected job status | `reset_failed` → entity method → `save` | bulk repo `reset_failed()` called |
| AC-12.3 | `read_text` call count | `TTSService.generate` | source_path read |
| AC-12.5 | `segments_done`/`segments_total` | `on_progress` → `TTS_PROGRESS_RESOLUTION` | unmapped float stored |
| AC-12.7 | `ModelDownloadRuntime.fraction` | catalog `on_progress` | callback ignored |

Atomicity: every read-then-write uses one `UnitOfWork` context + `commit()` (short command or one progress tick). Extract cache uses one `threading.Lock`. Seq increment is a single `+= 1` on `HealthService` under that processor’s lock.

Open-world: unrecognized settings wire / prepare step / cookie mode → `ValidationError` (fail-closed). Unrecognized download exception that is not a domain type → `Failed` + message, chained.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| REST factory, Bearer, envelopes, `/downloads/*` routes | deferred | MEU-14, MEU-15 | grouping Session 5; `04-rest-api.md` |
| Transcript/TTS/models routes + OpenAPI | deferred | MEU-16 | grouping Session 5 |
| MCP runtime/tools | deferred | MEU-17, MEU-18 | grouping Session 6 |
| GUI / electron-store `ui.rail.*` / `ui.panel.*` | deferred | MEU-19, MEU-23 | `06-gui.md` electron-store; Phase 3 theme-only |
| `YouTubeAdapter` ctor bind (`on_progress`, `should_stop`, `playlist_end`, `yt_dlp_debug`) | deferred | MEU-14 | p2 ctor lock; G29 composition root |
| API lifespan calling `recover_stale_processing` | deferred | MEU-14 | Spec “API lifespan”; method itself is in-scope AC-11.11 |
| SSE | out-of-scope | — | `BUILD_PLAN.md` Deferred; Spec “What this layer must not do” |
| OCR Part 1 | out-of-scope | — | Spec TextPreparation “OCR deferred”; `06-gui.md` |
| Multi-file TTS batch | out-of-scope | — | Spec TTS “no batch queue”; `06-gui.md` deferred |
| MCP Guard / ConversionJob GUI | out-of-scope | — | `BUILD_PLAN.md` Deferred |
| Port / adapter / UoW rewrites | out-of-scope | — | grouping Session 4; p2 complete |
| `ModelFetchJob` / persist `QueueRuntime` / persist `SABRStatus` | out-of-scope | — | Phase 1; Spec forbidden table |
| `--download-archive` / resume from `progress.json` | out-of-scope | — | Spec forbidden |
| NSIS bundle of `en_core_web_sm` | deferred | MEU-25 | `07-distribution.md` 151 (bundle **or** degrade); degrade/`CHUNK_DEPENDENCY_ERROR` is in-scope AC-12.2 |
| Live YouTube / HF / Kokoro in default suite | out-of-scope | — | Spec Testing 458 |

---

## G29 wiring checklist (this session)

| Layer | Ready? | Notes |
|-------|--------|-------|
| DB / repos / UoW | YES | Session 2 `approved` |
| YouTube / transcript / TTS / catalog adapters | YES | Session 3 `approved` |
| Filesystem / Media | YES | Session 2 `approved` |
| Services | THIS PLAN | fake-port unit + one real UoW smoke each |
| API composition root + hook bind | NO | MEU-14 (deferred row above) |
| MCP | NO | MEU-17–18 |
| GUI | NO | MEU-19–23 |

---

## BUILD_PLAN.md Audit

This project **does** update hub/index text: bind MEU-10–13 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"3"` `execution_plans`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 1–3 plan links. Do not hand-edit AUTOGEN tables — `meu_status.py update --plan` + `render`.

```powershell
rtk proxy pwsh -NoProfile -Command { $matches=@(Select-String -Path docs/BUILD_PLAN.md -Pattern 'p3-services'); [pscustomobject]@{matches=$matches.Count; lines=@($matches.LineNumber)} | ConvertTo-Json -Depth 3 } *> C:/Temp/av-kit/build-plan-audit.json; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.json; exit $code
```

---

## Verification Plan

### 1. Targeted services
```powershell
rtk proxy uv run pytest tests/unit/test_services.py tests/unit/test_domain.py -x --tb=short -v *> C:/Temp/av-kit/pytest-services.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-services.txt | Select-Object -Last 40; exit $code
```

### 2. Regression
```powershell
rtk proxy uv run pytest tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py -x --tb=short -v *> C:/Temp/av-kit/pytest-p3.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p3.txt | Select-Object -Last 40; exit $code
```

### 3. Types / lint
```powershell
rtk proxy uv run pyright packages/core/ *> C:/Temp/av-kit/pyright-core.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/pyright-core.txt | Select-Object -Last 40; exit $code }; rtk proxy uv run ruff check packages/core/ *> C:/Temp/av-kit/ruff-core.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ruff-core.txt | Select-Object -Last 20; exit $code
```

### 4. Scans
`SCAN_PLACEHOLDER_ARGS`, `SCAN_CORE_INFRA_ARGS`, `SCAN_G36_ARGS`, `SCAN_OPEN_ARGS` — rg exit 1 = clean PASS (same pattern as Session 3). `SCAN_OPEN` may hit `health.py` only (`LOG_FILE_APPEND_EXCEPTION`).

```powershell
rtk proxy rg -n -e TODO -e FIXME -e NotImplementedError packages/core/src/avkit_core/services *> C:/Temp/av-kit/anti-placeholder-services.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-placeholder-services.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-placeholder-services.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_PLACEHOLDER clean'; exit 0
```

```powershell
rtk proxy rg -n -e sqlalchemy -e yt_dlp -e fastapi -e youtube_transcript_api -e huggingface_hub -e soundfile -e onnxruntime -e kokoro -e avkit_infra packages/core/src *> C:/Temp/av-kit/anti-infra-core.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-infra-core.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-infra-core.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_CORE_INFRA clean'; exit 0
```

```powershell
rtk proxy rg -n -e "open\(" packages/core/src/avkit_core/services *> C:/Temp/av-kit/scan-open-services.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/scan-open-services.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/scan-open-services.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') -and ($_ -notmatch 'services[\\/]health\.py') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_OPEN clean (health.py append allowed)'; exit 0
```

### 5. OpenAPI
Skip: `packages/api/` absent (MEU-14–16).

### 6. SSOT / closeout
Same `SSOT_PLAN_BOUND` / `SSOT_READY` / `SSOT_APPROVED` / `PER_MEU_HANDOFF_AC` / `CHECK_EXEC_REVIEW` / `CLOSEOUT_GATE` / `REFLECTION_MARKERS` pattern as Session 3, with `PLAN_FOLDER`, phase `"3"`, MEUs `MEU-13,MEU-10,MEU-11,MEU-12`, `HUB_NEXT_AFTER`, `HANDOFF_GLOB` count 4.

---

## Open Questions

Resolved in locks (not human-blocking):

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| Pending→QualityBlocked vs p1 table | A. Extend `DOWNLOAD_TRANSITIONS` | Phase 1 invariant 186; p1 AC-3.3 one graph | Single machine | Touches Session 1 module | ✅ |
| | B. Service `replace()` | — | No domain edit | Second graph (p1 forbid) | ❌ |
| Prepare chunker | A. spaCy `SPACY_MODEL` + `CHUNK_DEPENDENCY_ERROR` if missing | Spec 303; `06-gui.md` 819; `07-distribution.md` 151 | Matches controlling canon | Model not in NSIS until MEU-25 | ✅ |
| | B. rule-based splitter | inspiration §10 algorithm only | No model | Contradicts Phase 3/6/7 (Finding 1) | ❌ |
| Dotted ui keys | A. Reject | Phase 1 key rule; Spec one-owner | Matches domain | GUI must use electron-store | ✅ |
| | B. Allow dots in key | `06-gui.md` table | Matches docs literally | Breaks frozen Setting invariant | ❌ |

---

## Research References

- [03-service-layer.md](../../../build-plan/03-service-layer.md)
- [01-domain-layer.md](../../../build-plan/01-domain-layer.md) invariant 186; ports
- [04-rest-api.md](../../../build-plan/04-rest-api.md) wire enums 114–126
- [06-gui.md](../../../build-plan/06-gui.md) settings key table 974–1011
- [_downloader_pseudo_logic.md](../../../../_inspiration/_downloader_pseudo_logic.md) SABR / 5 min cache
- [_transcript_pseudo_logic.md](../../../../_inspiration/_transcript_pseudo_logic.md) rate limits / frontmatter
- [_text_cleanup_pseudo_logic.md](../../../../_inspiration/_text_cleanup_pseudo_logic.md) §10
- [_kokoro_production_settings.md](../../../../_inspiration/_kokoro_production_settings.md) §3
- [structlog processors](https://www.structlog.org/en/stable/processors.html)
- [spaCy sentence segmentation](https://spacy.io/usage/linguistic-features#sbd)
- p2 reflection RULE-1/2/3; p2 plan `DOWNLOAD_HOOK_WIRING` / `playlist_end` ctor
- Session 1 `DOWNLOAD_TRANSITIONS` lock

## Emerging standards in this plan

Apply: M5, M6, G19, G24, G28, G29, G36. Skip MCP/GUI/OpenAPI rows (M1–M4, M7, G1–G18, G8, G30–G35, E2) — no those surfaces. G8 skip recorded in Verification Plan §5.

## Stop conditions

- Plan review cap 3 without `approved` → HARD STOP.
- Execution: DONE only when every `task.md` row is `[x]`/`[B]`, exec review `approved`, closeout artifacts exist.
- ~50% context: grouping split flag = finish MEU-13+10+11, compact, continue MEU-12 in the same plan (do not invent a new MEU).
- Do not start Session 5 in this project.
