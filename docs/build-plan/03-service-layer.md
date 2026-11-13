# Phase 3 — Service Layer

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: [Phase 1](01-domain-layer.md), [Phase 2](02-infrastructure.md) | Outputs: [Phase 4](04-rest-api.md)

---

## Goal

Orchestrate ports and the unit of work. Services own **workflows, queues, and invariants**. They do not talk to yt-dlp, SQLAlchemy, or FFmpeg directly. They do not invent tables, job types, or persisted session state that Phase 1 forbade.

| Source | Decision |
|--------|----------|
| Spec | [Phase 1](01-domain-layer.md) entities/invariants; [Phase 6](06-gui.md) start/pause/resume/cancel, cards, compile, prepare |
| Local Canon | [_downloader_pseudo_logic.md](../../_inspiration/_downloader_pseudo_logic.md), [_transcript_pseudo_logic.md](../../_inspiration/_transcript_pseudo_logic.md), [_shared_patterns.md §2](../../_inspiration/_shared_patterns.md), [_text_cleanup_pseudo_logic.md Part 2](../../_inspiration/_text_cleanup_pseudo_logic.md), [_kokoro_production_settings.md](../../_inspiration/_kokoro_production_settings.md) |
| Research-backed | One UoW per short command; commit progress on a timer during long IO (Phase 2 note) |
| Human-approved | 2026-08-18: `QueueRuntime` / `SABRStatus` are in-memory; compile/zip are methods; `TranscriptItem` is a child record; no `ModelFetchJob` |

This file **uses** Phase 1 types and Phase 2 ports. If a behavior needs a new persistable column, change Phase 1 first.

---

## Package layout

```
packages/core/src/avkit_core/
├── services/
│   ├── download.py       # DownloadService + SABR session
│   ├── transcript.py     # TranscriptService
│   ├── tts.py            # TTSService
│   ├── prepare.py        # TextPreparationService (stateless)
│   ├── models.py         # ModelService
│   ├── settings.py       # SettingsService
│   └── health.py         # HealthService (dependency probe)
├── ports/                # Phase 1 only — do not add protocols here
└── domain/
```

Services live in **core**. Constructor dependencies are ports + a UoW factory. Never import `avkit_infra`.

---

## Cross-cutting rules

### Construction

```python
UoWFactory = Callable[[], UnitOfWork]
```

| Dependency | Used by |
|------------|---------|
| `UoWFactory` | All services that persist |
| `YouTubePort` | DownloadService, TranscriptService (resolve IDs) |
| `TranscriptPort` | TranscriptService |
| `TTSPort` | TTSService, ModelService (load/unload/status) |
| `MediaPort` | DownloadService (audio extract), TTSService (WAV→MP3), HealthService. **Phase 8:** also `ConversionService` ([08-video-conversion.md](08-video-conversion.md)) |
| `ScreenCapturePort` / `ImageAnnotatePort` | **Phase 9:** `CaptureService` only ([09-screenshot-capture.md](09-screenshot-capture.md)) |
| `FilesystemPort` | TranscriptService, TTSService (Phase 1 protocol) |
| `ModelCatalogPort` | ModelService (Phase 1 protocol) |

Use the Phase 1 method set only. No direct `open` / `soundfile` / `huggingface_hub` in this package.

### Unit of work

| Rule | Why |
|------|-----|
| One UoW per **command** (add, reorder, reset, compile, settings write) | Short transactions |
| Do **not** hold one session open across a full yt-dlp download or channel crawl | WAL + progress polling |
| During long work: open UoW → write progress → `commit()` → close; repeat on throttle (≈1s for downloads, per-video for transcripts) | GUI polls SQLite |
| Worker thread may call the factory freely | `check_same_thread=False` (Phase 2) |

### Queue runtime (session only)

Each of `DownloadService` and `TranscriptService` holds one `QueueRuntime` (`Idle` | `Processing` | `Paused`). Restart → `Idle`. Jobs keep their row statuses.

| Module | Pause | Cancel / Stop |
|--------|-------|----------------|
| Downloads | Finish the **current** item, then `Paused`. Items stay `Pending` / complete to `Done`/`Failed`. No `DownloadStatus.Paused` | Cancel in-flight download (`DownloadCancelledError`), processor → `Idle` |
| Transcripts | After the **current video** (or immediately at the next delay), block. Set the **parent** `TranscriptJob.status = Paused` | **Stop (locked):** parent `Processing` or `Paused` → `Cancelled`; unfinished items stay `Pending` unless already `Done`/`Skipped`/`Failed`; `current_job_id = None`; runtime `Idle`. Later `start` skips `Cancelled` and `Done`. `requeue_channel(job_id)` sets a `Cancelled` parent back to `Pending` (terminal items stay terminal). |

TTS has no queue in MVP (single job). Cancel checks between segments.

### Validation

Services assume API/MCP already ran Pydantic/Zod (`extra="forbid"`). Still enforce **invariants** here (status transitions, archive skip, SABR quality lock, voice prefix, speed range). Do not `replace(job, **raw_dict)`.

### Logging

`structlog` with `module=download|transcript|tts|models|settings`. Re-raise domain errors with context. No silent `except`.

### Threading

One background thread (or asyncio task wrapping sync ports) per module processor. GUI/API remain non-blocking: start returns immediately. Progress is visible via subsequent `get_*` reads.

---

## `DownloadService`

Session: `QueueRuntime(queue_name="downloads")` + `SABRStatus` (default `Inactive`).

### Commands

| Method | Returns | Behavior |
|--------|---------|----------|
| `add_to_queue(url, quality, audio_only, audio_format)` | `list[DownloadJob]` | Resolve URL; explode playlist/channel into N jobs; apply archive + in-queue dedup |
| `start_processing()` | `None` | `Idle`/`Paused` → `Processing`; spawn worker if needed |
| `pause_processing()` | `None` | Cooperative: finish current download, then `Paused` |
| `resume_processing()` | `None` | `Paused` → `Processing` |
| `cancel_processing()` | `None` | Cancel in-flight; processor `Idle`. Maps GUI Cancel |
| `stop_processing()` | `None` | Alias of cancel if Phase 4 still exposes `/stop`; prefer `cancel_processing` |
| `remove_from_queue(job_id)` | `None` | Delete row; files stay; archive stays |
| `clear_queue()` | `None` | `delete_all` jobs only |
| `reorder_queue(job_ids)` | `None` | Must be a permutation of current ids |
| `reset_failed(job_id)` | `DownloadJob` | `Failed` → `Pending`; clear error + progress |
| `get_queue()` | `list[DownloadJob]` | `ORDER BY queue_position` |
| `get_job(job_id)` | `DownloadJob` | Raise not-found |
| `get_processor_state()` | `QueueRuntime` | For GUI indicator |
| `get_sabr_status()` | `SABRStatus` | Session |
| `check_sabr()` | `SABRStatus` | `youtube.check_sabr_status()`; if Active, `source=Detected`; apply lock |
| `force_sabr()` | `SABRStatus` | `Active`, `source=Forced`; apply lock |
| `clear_sabr()` | `SABRStatus` | `Inactive`; `QualityBlocked` → `Pending` |
| `test_cookies(mode, browser, profile, cookie_file)` | `CookieTestResult` | `youtube.test_cookies`; no cookie bytes stored |
| `apply_defaults_to_pending()` | `int` | Count of `Pending`/`QualityBlocked` rows updated to current `downloader.quality` / audio defaults |

`stop_processing` exists because [04-rest-api.md](04-rest-api.md) still lists `/downloads/stop`. [06-gui.md](06-gui.md) uses pause / resume / cancel. Implement all four names; `/stop` = cancel.

### Add flow

```
extract_info(url)
  single video → 1 job
  playlist/channel → N jobs (flat ids; titles when cheap)
for each video_id:
  if already in queue → skip (log warn); do not insert
  if archive_tracking and archive.contains("youtube", video_id) → insert status=Skipped
  else → insert Pending
  if sabr Active and quality/audio incompatible → QualityBlocked
assign queue_position at end
```

Cookie mode for extract/download comes from settings (`downloader.cookie_*`), not from the add payload, unless the API later passes an override. Do not persist cookies.

### Worker loop

```
while runtime.state == Processing:
  job = first Pending by queue_position
  if none: runtime = Idle; break
  if pause requested: finish-or-skip new starts; runtime = Paused; break
  runtime.current_job_id = job.id
  job.status = Downloading; commit
  try:
    result = youtube.download(url, options_from(job, settings, sabr))
    if result.sabr_detected: session SABR → Active/Detected; apply_lock()
    optional MediaPort.convert for audio_only formats that need it
    job → Done; file_path, file_size; archive.add(extractor, video_id, title)
  except AgeRestrictedError: AgeRestricted
  except DownloadCancelledError: Cancelled; break to Idle
  except Exception: Failed + error_message
  commit; current_job_id = None
```

Progress hook (throttled ~1s): UoW update `progress`, `speed_bps`, `eta_seconds`, `file_size`.

`apply_lock()`: every job whose quality is not `P360`/`Lowest` (or audio not in `{StandardMp3, HighM4a}` when `audio_only`) and status in `{Pending, QualityBlocked}` → `QualityBlocked`. Clearing SABR: those `QualityBlocked` → `Pending`.

### Options for download

Build `DownloadOptions` from the job + settings: `output_dir` = `downloader.path`, cookie mode/path/browser, quality, audio flags. Never put cookie file contents on the job.

### Extract cache and lock (session only)

| Rule | Why |
|------|-----|
| One in-flight `extract_info` / `extract_video_ids` at a time (mutex) | yt-dlp is not re-entrant; inspiration semaphore |
| Cache `extract_info` results **5 minutes** keyed by normalized URL | Avoid re-hitting YouTube when the user re-adds or Test Cookies / SABR check just ran |
| Cache is memory-only; restart empties it | Not a table |

Changing Settings `downloader.quality` does **not** rewrite existing queue rows. `apply_defaults_to_pending()` (REST `POST /downloads/apply-defaults`) updates only `Pending` / `QualityBlocked` jobs. Already-selected rows keep their stored quality unless the user applies.

---

## `TranscriptService`

Session: `QueueRuntime(queue_name="transcripts")`.

### Commands

| Method | Returns | Behavior |
|--------|---------|----------|
| `add_channel(channel_url)` | `TranscriptJob` | Resolve name + ids; insert parent + items |
| `start_processing()` | `None` | Runtime `Idle` → `Processing`. Worker selects **`Pending` parents only**. 409 if already `Processing` |
| `pause_processing()` | `None` | After current video; parent `Paused`; runtime `Paused` |
| `resume_processing()` | `None` | Only if runtime is `Paused` (or a parent is `Paused`). That parent `Paused` → `Processing`. 409 otherwise |
| `stop_processing()` | `None` | **Locked Stop:** parent `Processing`/`Paused` → `Cancelled`; unfinished items stay `Pending`; `current_job_id = None`; runtime `Idle` |
| `requeue_channel(job_id)` | `TranscriptJob` | `Cancelled` → `Pending` only. Terminal items unchanged. 409 if not `Cancelled` |
| `retry_failed_channel(job_id)` | `TranscriptJob` | `Failed` → `Pending`. Done/Skipped items stay terminal; Failed items → `Pending`. 409 if parent is not `Failed` |
| `remove_channel(job_id)` | `None` | Delete job (cascade items); **files stay** |
| `reorder_queue(job_ids)` | `None` | Channel order |
| `get_queue()` | `list[TranscriptJob]` | Aggregates filled (`video_count`, `word_count`) |
| `get_job(job_id)` | `TranscriptJob` + item counts / last title | For `GET /transcripts/{id}` |
| `list_items(job_id)` | `list[TranscriptItem]` | Not a GUI table; used for progress |
| `compile_channel(job_id)` | `list[Path]` | Write `compiled/*_volN.md` |
| `get_processor_state()` | `QueueRuntime` | |

### Add flow

1. Reject duplicate `channel_url` already in queue.
2. `youtube.extract_info` / `extract_video_ids` with `transcript.playlist_end` (`0` = all).
3. `ChannelInfo` → `channel_name`.
4. `output_dir` = `{transcript.output_dir}/{slug(extract title)}`: the slug comes from `extract_info`'s title, not the listed channel name (`SLUG_SOURCE`, Session 53 D-349).
5. `filesystem.ensure_channel_dirs`.
6. Insert `TranscriptJob` (`Pending`, `video_count=N`, `word_count=0`).
7. `replace_items` with one `TranscriptItem` per id (`Pending`).
8. Do **not** read `progress.json`.

### Worker loop

```
for job in list_jobs() ordered by queue_position:
  if stop requested:
    if job.status in {Processing, Paused}: job.status = Cancelled; commit
    runtime = Idle; current_job_id = None; return
  if job.status != Pending: continue   # skip Done, Cancelled, Failed, Paused
  job.status = Processing; commit
  for item in list_items(job) where status == Pending:
    wait for pause event (if set: job.status = Paused; runtime = Paused; return)
    if stop requested:
      job.status = Cancelled; commit   # in-flight item stays Pending unless already terminal
      runtime = Idle; current_job_id = None; return
    honor delay_between_requests
    every batch_size: sleep pause_between_batches
    fetch + write one item (below)   # each request first waits for the rate cap
    if the item's block outlasted max_retries:   # MEU-116
      under _lock: pause requested; job.status = Paused
      job.error_message = failure_message(blocked); runtime = Paused; return
  if all items terminal:
    if any item Failed:
      job.status = Failed   # do not compile/zip; do not promote to Done
      job.error_message = JOB_MESSAGE   # "{n} of {total} videos failed. Last: {message}"
    else:
      compile_channel(job.id)
      zip_raw(job.id)
      job.status = Done; zip_path set
      job.error_message = SKIPPED_JOB_MESSAGE if any item Skipped else None
                          # "{n} of {total} videos had no transcript. Last: {message}"
  optional write_progress_export(done video_ids)
```

`start` never picks `Paused` (that is `resume`) or `Failed` (that is `retry_failed_channel`) or `Cancelled` (that is `requeue_channel`).

**Resume** moves the Paused job back to `Processing` and clears its `error_message`. A pause without a reason (the user's) leaves `error_message` as it is.

**One worker (D-306).** `start_processing`, `resume_processing` and `stop_processing` set their flags and check for a live worker in one critical section under `_lock`. Each worker exit (pause, stop, idle) re-checks its flag under the same lock and, in that section, writes the runtime and marks the worker gone (`_worker_active`). So a resume either reaches the worker before it exits or finds none and starts one, and at most one worker runs. `_next_job` reads and clears the resume's pick-Processing flag under the lock. `_lock` is a plain `threading.Lock`, so nothing called inside these sections takes it again.

**Rate cap (MEU-116).** Before each `get_transcript` call, retries included, the service reads `transcript.requests_per_hour`. `0` turns the cap off. Otherwise it drops request starts at or before `now − RATE_WINDOW` (3600 s, on the injected `clock`, default `time.monotonic`). While the count is at or above the cap it sleeps `min(1.0, oldest + RATE_WINDOW − now)`, then re-checks stop and pause and reads the cap again, so a stop or pause ends the wait within a second and a changed cap applies at once. With the defaults and no retries the cap delays nothing.

**Boot recovery:** API lifespan sets any parent still `Processing` → `Pending` (crash). `Paused` stays `Paused` until `resume`.

**One item**

1. `result = transcripts.get_transcript(video_id, languages)` (languages from settings later; default `["en"]`).
2. `TranscriptSkip(cause)` → `Skipped` (no file), `error_message = failure_message(cause)`; log `transcript.item_skipped` at WARNING with `persist=True`, so it reaches `console.log` with the toggle off.
3. `TranscriptRetryableError` → sleep `retry_delay`, `retry_count++`, `error_message = failure_message(blocked)`, retry until `max_retries`. A retry in progress logs nothing. The exhausted block leaves the item `Pending` with `retry_count = 0` and that message, logs `transcript.blocked` at ERROR and pauses the job (worker loop, MEU-116).
4. `DomainError` → `Failed`, `error_message = failure_message(other, reason)`, where the reason is `safe_reason(redact_message(str(error)))`, or the class name when that is empty; log `transcript.item_failed` at ERROR.
5. Success → write `{output_dir}/raw/{video_id}.md` via `write_text_atomic` (YAML frontmatter per [06-gui.md](06-gui.md)); set `path`, `word_count`, `title`, `language`, `Done`, `processed_at`, and clear `error_message`.
6. Discard `result.text`. `recompute_word_count`. Commit.

Each `transcript.item_skipped`, `transcript.item_failed` and `transcript.blocked` line carries `job_id`, `video_id` and `error=` the stored message (MEU-115, MEU-116).

Frontmatter fields: `video_id`, `title`, `channel`, `url`, `date` (upload date if known, else omit or today — prefer yt-dlp date when the item title fetch has it).

Resume after process restart: items already `Done`/`Skipped`/`Failed` are not fetched again. Only `Pending`.

### Compile

Read each `Done` item’s `path` (the `.md` body, not SQLite text). Build:

- H1: channel name
- TOC linking to each video
- H2 + transcript per video
- Split when word count would exceed `transcript.max_words_per_document` (default 490_000)
- Names: `{channel_slug}_vol1.md`, `_vol2.md` under `compiled/`

Do not persist a path list; discover `compiled/*.md`. `compile_channel` may run again (overwrite volumes).

### Zip

`zipfile` of `raw/*.md` → `{channel_slug}_raw.zip`. Set `job.zip_path`. Automatic on `Done`; compile endpoint does not require zip.

---

## `TextPreparationService`

Stateless. No UoW. No job row.

```python
def prepare(text: str, enabled_steps: list[str], chunk_max_chars: int | None = None) -> str: ...
```

Step ids (GUI checkboxes). Defaults match [06-gui.md](06-gui.md):

| id | Default |
|----|---------|
| `punctuation` | on |
| `symbols` | on |
| `numbers` | on |
| `currency` | on |
| `all_caps` | on |
| `chapter_markers` | **off** |
| `urls_emails` | on |
| `page_numbers` | on |
| `whitespace` | on |
| `chunk` | on |
| `kokoro` | on (always last when enabled) |

OCR Part 1 is **deferred** ([06-gui.md](06-gui.md)). Do not implement it here.

`chunk` uses spaCy sentence-aware splits at `chunk_max_chars` (setting `tts.chunk_max_chars`, default 250). `kokoro`: spell numbers, space acronyms, sentences &lt; 25 words, straight quotes, no ellipses ([_kokoro_production_settings.md §3](../../_inspiration/_kokoro_production_settings.md)).

Unknown step id → 422-class domain validation error. Order is fixed; `enabled_steps` is a set of toggles, not a reorder.

---

## `TTSService`

MVP: one generation at a time. No batch queue ([06-gui.md](06-gui.md) deferred).

| Method | Returns | Behavior |
|--------|---------|----------|
| `generate(text, voice, speed, format, enabled_steps, source_kind, source_path)` | `TTSJob` | Create row `Pending`/`Generating`; run worker |
| `prepare(...)` | `str` | Delegate to `TextPreparationService` |
| `cancel(job_id)` | `None` | Cooperative between segments → `Cancelled` |
| `get_status(job_id)` | `TTSJob` | |

### Generate flow

1. Reject empty text. Speed in `[0.5, 2.0]`. Format `MP3` or `WAV`.
2. Require `ModelStatus.is_loaded` (else fail fast — GUI disables Generate).
3. Resolve `VoiceConfig` from `tts.list_voices()`; first letter of `voice` is lang_code (adapter already derives).
4. `text_hash` = SHA-256 of raw input. `text_preview` = first 200 chars. **Do not persist `text`.** `source_path` is display metadata only — **do not** `read_text` it. The `text` argument is the sole body.
5. Insert `TTSJob`. Editor draft remains settings `tts.input_text` (API/settings), not this row.
6. `cleaned = prepare(text, enabled_steps)`.
7. `samples = tts.generate(cleaned, voice, speed, on_progress)` → update `segments_done`/`segments_total` each callback (short UoW).
8. `filesystem.write_audio_wav(wav_path, samples, sample_rate)`. **No** `soundfile` / `open` in this service.
9. If `format == MP3`: `media.convert(wav, mp3, tts_defaults)`; `output_path` = mp3.
10. `Done` or `Failed` + `error_message`.

Cancel: set a flag the `on_progress` callback checks; adapter/generate should honor it between segments.

---

## `ModelService`

| Method | Returns | Behavior |
|--------|---------|----------|
| `list_available()` | `list[ModelVariant]` | Repo catalog (seeded rows), plus `sideload` scan of `tts.models_directory` |
| `list_downloaded()` | `list[ModelVariant]` | `is_downloaded=True` |
| `download(variant_id)` | `ModelVariant` | Spawn one worker; return immediately. Owns `ModelDownloadRuntime` |
| `load(variant_id, device)` | `None` | `tts.load_model`; not persisted |
| `unload()` | `None` | `tts.unload_model` |
| `get_status()` | `ModelStatus` | Loaded-model snapshot |
| `get_download_runtime()` | `ModelDownloadRuntime` | In-flight HF fetch (or Idle) |

**`ModelDownloadRuntime` (locked):** at most one download. `download()` while `state=Downloading` → `ConflictError` (409). On start: `variant_id`, `Downloading`, `fraction=0`. Callbacks update `fraction`. Success → `mark_downloaded`, then `Idle`. Failure → `Failed` + `error_message`, variant stays not downloaded. Process restart → `Idle`. Load of variant A may proceed while B is not downloading; do not bind per-row GUI percent to `ModelStatus` — bind it to `get_download_runtime()` matching that row’s `variant_id`.

Do not create `ModelFetchJob` rows. Failed download → `ModelDownloadError`.

---

## `SettingsService`

| Method | Behavior |
|--------|----------|
| `get(namespace, key)` | Typed value or default from [06-gui.md](06-gui.md) key table |
| `set(namespace, key, value)` | Validate type/range; persist leaf key |
| `get_namespace(namespace)` | All keys; fill defaults for missing |
| `set_namespace(namespace, mapping)` | Upsert known keys; **reject unknown keys** (`extra=forbid` equivalent) |

Namespaces: `downloader`, `transcript`, `tts`, `app`, `ui`. Unknown namespace → validation error.

Do not store window geometry here if Electron already uses electron-store for it; `ui.*` keys that the API owns (theme) may live here. Prefer one owner per key (GUI plan: some `ui.*` are electron-store). Phase 3 persists whatever Phase 4 `PUT /settings/{namespace}` sends after validation against the GUI key table.

Cookie **paths** and browser name are settings. Cookie **bytes** are never settings.

---

## `HealthService`

Used by Phase 4/6. Thin.

| Method | Behavior |
|--------|----------|
| `liveness()` | Process up |
| `dependencies()` | `MediaPort.ffmpeg_version` + `YouTubePort.ytdlp_version` |
| `record_startup_metric(key, value_ms)` | structlog event only — no table |
| `console_snapshot(after_seq: int)` | Next `ConsoleEvent`s from the in-process ring (Phase 4 `/health/console`) |

`ConsoleEvent`: `{ seq: int, ts: datetime, level, module, message }`. Ring capacity **10_000**; drop oldest.

**`seq` ownership (locked):** a single process-local counter on `HealthService` (or the structlog processor it registers). Every app log is redacted, assigned the next `seq`, appended to the ring, and emitted to stdout as that same JSON object. Nothing else increments `seq`. Restart → counter returns to 1; clients treat a decreased `seq` as a new instance. Uvicorn / non-JSON stdout is **not** given a backend `seq` (Phase 6 `ipc:{n}`).

Tokens, cookie bytes, and Bearer values are redacted **before** enqueue. Each `CONSOLE_FIELDS` value (`job_id`, `video_id`, `variant_id`, `device`, `error`, `detail`, `request_id`, `route`) is made one line, each URL becomes "[link]", and it is redacted and cut to `FIELD_LIMIT` (300) before the whole message is redacted again. A line at a `PERSIST_LEVELS` level (`ERROR`, `CRITICAL`), or whose event carries `persist=True`, is always appended to `{app_data}/logs/console.log`; when `app.log_to_file` is true, every other line is appended too. The `persist` key is never shown. The append catches `OSError` and runs under its own lock. The method names `exception`, `fatal` and `warn` log at `ERROR`, `CRITICAL` and `WARNING`. The event handed on to structlog's stdout renderer holds only the safe message, its `seq` and `exc_info=False`, so no unkept field and no traceback reach stdout.

---

## Status machines (service-enforced)

**Download item** — Phase 1 machine. Service is the only writer of `status`.

**Download processor:** `Idle → Processing ⇄ Paused → Idle`.

**Transcript parent:** `Pending → Processing ⇄ Paused → Done | Failed | Cancelled`.

**Transcript item:** `Pending → Done | Skipped | Failed` (retries stay `Pending` until terminal).

**TTS job:** `Pending → Generating → Done | Failed | Cancelled`.

Illegal transitions raise a domain error (not a silent no-op).

---

<a id="tts-runtime-assets-residual"></a>

## TTS runtime assets (residual)

> **MEU-62.** Registered 2026-09-30 from known issue `TTS-GENERATE-FAILED-SILENT`. On the target machine TTS produced no audio: the ONNX vocab is never wired (`packages/api/src/avkit_api/wiring.py:167` constructs `KokoroAdapter()` without `onnx_vocab_path`, so `_load_onnx_vocab` raises "ONNX vocab file is missing" for every ONNX variant) and the spaCy `en_core_web_sm` model the Kokoro pipeline needs is not installed. The failure was invisible: `TTSService.generate` marks the job `Failed` without a log line and the GUI never shows `error_message` (GUI half → MEU-63). Human-approved 2026-09-30 (triage D-22): both assets are **managed downloads**, not installer payload.

| Rule | Contract | Source |
|------|----------|--------|
| Vocab (every variant) | **D-8:** every variant, ONNX and PyTorch, needs Kokoro's `config.json` (`ONNX_VOCAB_REPO` / `ONNX_VOCAB_FILE`, from `hexgrad/Kokoro-82M`). `ModelService.download` fetches it after the weights when it is missing or invalid. PyTorch passes it as `KModel(config=…)`, so the load never reaches Hugging Face. A variant without a valid vocab is `downloaded: false`, and `POST /models/load` refuses it with 409. **D-9:** there is one file, `{tts.models_directory}/config.json` (`VOCAB_LOCATION`). It is resolved per call through `resolve_vocab_path(…)`, which `wiring.py` passes to `KokoroAdapter(vocab_path=…)`; this replaces the earlier "wiring passes `onnx_vocab_path`". | Human-approved D-22; plan D-8, D-9 |
| spaCy model | `en_core_web_sm` is a managed download, triggered on the first load of **any variant** or from Settings → Dependencies "Get" (**D-10**). **D-11:** one wheel is pinned per installed spaCy major.minor (`SPACY_MODEL_PIN`). It is sha256-verified, extracted with a zip-slip guard and an atomic `os.replace` into `{models_directory}/spacy/<name>-<version>/`, and put on `sys.path` at startup and after a download. It is never bundled in the installer, and nothing runs `pip` at runtime. | Human-approved D-22; plan D-10, D-11; [02 §Model manager](02-infrastructure.md#model-manager-model_managermanagerpy) |
| Required assets | **D-10:** `required_tts_assets(format, voice, steps)` always returns the vocab. It adds the spaCy model for English voices (lang code `a`/`b`), or for any voice when the enabled prepare steps include `chunk` (default-on). | plan D-10 |
| Asset download | **D-12:** `POST /models/download` takes exactly one of `{variant_id}` or `{asset}` (`tts_onnx_vocab` / `tts_spacy_model`). The download runtime reports `asset`. MCP gets `avkit_models.download_asset` on the same path. No new route is added. | plan D-12 |
| Readiness | `HealthService.dependencies` gains the `tts_onnx_vocab` and `tts_spacy_model` rows. **D-14:** a row is `{available, version, state}` with `state` ∈ `ready` / `missing` / `downloading`, a superset of the existing rows. The GUI card renders the rows without new IPC. | plan D-14; Local Canon [06 §Dependencies / readiness](06-gui.md#dependencies--readiness--mcp-settings-cards) |
| Fail fast | `generate` checks `required_tts_assets` **before** it creates the job, and raises `ConflictError("tts asset missing: <name>")` → 409 with the asset name. No job row, no partial WAV. | Spec (this section); Boundary Input Contract |
| Logging | `TTSService.generate` emits `tts.generate` (job_id, voice, variant), `tts.generate_done` (job_id, output) and `tts.generate_failed` (job_id, error) through the existing `module=tts` logger. **D-13:** the Console appends `CONSOLE_FIELDS` (`job_id=`, `error=`) to the event text, after redaction. Other events are unchanged. | Local Canon AGENTS §Code Quality; plan D-13 |
| `error_message` | Every `Failed` job carries a non-empty `error_message`. This covers the catch-all path too (AC-62.11): an unexpected exception in the background worker marks the job `Failed` with `"<Type>: <message>"`; nothing is re-raised (Session 33 plan D-19). | Local Canon G25; plan AC-62.11 |
| Scope | No new REST route (D-12 widens an existing body); readiness fields extend existing schemas with an OpenAPI diff committed; ffmpeg divergence (Settings vs Convert vs Downloader) is a separate issue, not this MEU (now [MEU-78](#ffmpeg-resolution-residual)) | Spec |

Tests: unit for the download-with-vocab path and the fail-fast check (fake adapter), contract test for the readiness rows and the 409, regression that an ONNX load with a present vocab yields samples.

<a id="tts-voice-assets-residual"></a>

## TTS voice assets (residual)

> **MEU-73.** Registered 2026-10-09 from `TTS-VOICE-PACK-LAZY-FETCH`, `SETTINGS-TTS-ASSET-ROW-STALE` and `TTS-SPACY-SYSPATH-PREPEND`. Kokoro fetches `voices/<id>.pt` from Hugging Face inside `generate` (`tts/adapter.py:183-185`), so the first run per voice needs network and fails mid-job offline. The Settings Dependencies card never refreshes after an asset download, and `activate_spacy_dir` prepends a user-writable directory to `sys.path`.

> **Delivered (Session 32).** D-74: voice packs are one managed asset, `tts_voice_packs`, holding all 54 `voices/<id>.bin` files from `onnx-community/Kokoro-82M-v1.0-ONNX` @ `ONNX_REVISION`. They are fetched all at once, chained after any model download and by the Settings Get button, and both formats read them. The Settings Dependencies card refreshes when the download runtime settles, and `activate_spacy_dir` appends. Plan `docs/execution/plans/2026-10-14-tts-engine-runtime/`.

| Rule | Contract | Source |
|------|----------|--------|
| Voice packs managed | A voice pack is a managed asset on the MEU-62 path: fetched on first selection of a voice (or with the model), stored under `{tts.models_directory}`, reported ready/missing; `generate` with a missing pack raises the MEU-62 fail-fast 409 naming the pack, never a mid-run fetch | Human-approved D-22 extended by triage D-42 |
| Settings refresh | The Settings Dependencies query is invalidated when the shared download runtime leaves `Downloading`, as the TTS page already does | Triage D-43; Session 27 D-28 |
| spaCy path | `activate_spacy_dir` appends to `sys.path` instead of `insert(0, …)` | `TTS-SPACY-SYSPATH-PREPEND` (Session 27 review F3) |
| Tests | Unit: missing pack → 409 before a job row; download path stores the pack; Settings query invalidation; `sys.path` order | Local Canon Phase 3 testing |

<a id="tts-language-runtime-residual"></a>

## TTS language runtime (residual)

> **MEU-74.** Registered 2026-10-09 from `TTS-NON-ENGLISH-G2P-DEPS`. Voices with lang codes e/f/h/i/p use `misaki.espeak.EspeakG2P` (needs espeak-ng); j/z need the `misaki[ja]`/`[zh]` extras. Only the English spaCy model is managed, so those voices fail at pipeline construction.

> **Delivered (Session 32).** D-71: `EspeakCliAdapter` calls a user-installed eSpeak NG CLI as a subprocess (text on stdin), with misaki's Apache-2.0 maps ported and attributed. phonemizer, espeakng_loader and `misaki.espeak` are never imported. `/tts/voices` carries `available`/`reason`, `/health/dependencies` carries `tts_espeak`, and ja/zh stay `language_unsupported` (D-70). Plan `docs/execution/plans/2026-10-14-tts-engine-runtime/`.

| Rule | Contract | Source |
|------|----------|--------|
| Never bundle | espeak-ng (GPL-3.0) is never shipped in the installer or the backend bundle | Human-approved 2026-10-09 triage D-61; Local Canon 09 §ShareX source map (no GPL code) |
| Detect | A user-installed espeak-ng is detected at runtime and reported as a Dependencies readiness row (`tts_espeak`) with install guidance | Human-approved D-61 |
| Voice availability | `/tts/voices` marks each voice `available` with a `reason` when its G2P runtime is missing; the TTS page lists those voices disabled with the reason; `generate` with an unavailable voice is a 409 before any job row | Human-approved D-61; Boundary Input Contract |
| ja / zh extras | The licence and size of `misaki[ja]`/`[zh]` are assessed in the plan; until then j/z voices follow the availability rule | Human-approved D-61 |
| Tests | Unit for the availability flag with and without espeak-ng (fake probe), contract test for the 409 and the readiness row, behaviour test for disabled voices | Local Canon |

<a id="tts-device-resolution-residual"></a>

## TTS device resolution (residual)

> **MEU-75.** Registered 2026-10-09 from `TTS-MODEL-FLOW-GAPS` (reproduced locally). The TTS page offers `auto/cuda/cpu/mps` statically (`TTSPage.tsx:468-485`); `_resolve_device` returns `cuda` when asked even if `torch.cuda.is_available()` is false (`tts/adapter.py:43-44`); with a CPU torch build `KModel.to('cuda')` raises `AssertionError` and the load fails with no reason.

| Rule | Contract | Source |
|------|----------|--------|
| Fallback | A requested device the runtime cannot use falls back to CPU for PyTorch as it already does for ONNX (`tts/adapter.py:179-183`), logs `tts.device_fallback` (requested, actual) and the model status reports the actual device | Triage D-66; Local Canon 07 §GPU (detect at runtime) |
| Device list | The available devices come from the runtime (`auto` and `cpu` always; `cuda`/`mps` only when detected) and the TTS page lists only those | Triage D-66 |
| Errors | Any load failure the adapter cannot map raises `ModelLoadError` with the cause, never a bare exception | Local Canon AGENTS §Code Quality |
| Tests | Unit: cuda requested on a CPU torch → loads on CPU with the log line; device list with and without CUDA (fake probe); contract test for the status device | Local Canon |

> **Delivered (Session 35).** D-9–D-12: `DEVICE_PROBE` reads what the installed runtime can use (`auto` and `cpu` always; `cuda` from `torch.cuda.is_available()` or the ONNX `CUDAExecutionProvider`; `mps` for PyTorch only). `DEVICE_RESOLVE` sends a request the runtime cannot serve to CPU with `tts.device_fallback`, and the status reports the actual device. `LOAD_FALLBACK` retries a failed PyTorch move to `cuda`/`mps`, or a failed ONNX CUDA session, on CPU; an ONNX session that silently dropped CUDA reports `cpu`; a CPU failure raises `ModelLoadError` with the cause; `LOAD_ERROR_HTTP` maps it to 422. `DEVICE_FIELD` adds `devices` to every model-list row. Plan `docs/execution/plans/2026-10-16-tts-voice-panel/`.

<a id="tts-async-generation-residual"></a>

## TTS async generation (residual)

> **MEU-77.** Registered 2026-10-09 from `MCP-TTS-GENERATE-SYNCHRONOUS`. `POST /tts/generate` synthesizes inline and returns only when the job is Done/Failed (`routes/tts.py:54-69`, `services/tts.py:113-200`). MCP calls it with a 30 s timeout (`mcp-server/src/client.ts:14`), so longer texts report `fetch_failed` while the job keeps running, and a running job cannot be cancelled because its id is unknown.

| Rule | Contract | Source |
|------|----------|--------|
| Queue and return | `POST /tts/generate` validates, creates the job and returns it at once (`Queued`/`Running`); synthesis runs in the background | Triage D-44; Local Canon (download, transcript and conversion queues) |
| Cancel | `DELETE /tts/{id}` stops a running job between segments and marks it `Cancelled`; no partial output file remains | Triage D-44 |
| One at a time | A second generate while one runs keeps the existing 409 | Local Canon §TTSService |
| Status | The returned job is `Generating`, which refines `Queued`/`Running` above: the single-job service admits and starts in one step, so nothing waits in a queue | Session 33 plan D-18 |
| Restart | Startup marks every leftover `Generating` job `Failed` with `interrupted by restart`; shutdown refuses new jobs, cancels the running one and waits up to 10 s, and skips the model unload and database dispose if the worker is still busy | Session 33 plan `RESTART_RECOVERY`, `SHUTDOWN_STOP` |
| Clients | MCP `avkit_tts.generate` returns the job; the audit baseline gains the poll and cancel steps; the GUI run bar polls the job | Triage D-44; [05 §MCP live audit](05-mcp-server.md#mcp-live-audit-residual) |
| OpenAPI | Response status/semantics change is committed with an OpenAPI diff | Spec 04 §OpenAPI |
| Tests | Service unit (returns before synthesis ends, cancel mid-run), contract tests, MCP tests, an Electron run-bar case | Local Canon |

<a id="ffmpeg-resolution-residual"></a>

## FFmpeg resolution (residual)

> **MEU-78.** Registered 2026-10-09 from `FFMPEG-RESOLUTION-DIVERGENCE`. One adapter resolves ffmpeg once at startup and latches the result for Convert, TTS and the health check (`wiring.py:160-161`, `media/adapter.py:211-223`); the Downloader never receives it (`wiring.py:144-149`, no `ffmpeg_location`), and the Dependencies card shows the raw setting rather than the resolved binary (`routes/health.py:26-33`).

| Rule | Contract | Source |
|------|----------|--------|
| One resolver | One resolver (configured → bundled → PATH) feeds Convert, TTS MP3, the health check and yt-dlp (`ffmpeg_location`) | Triage D-40 |
| Live setting | Changing `downloader.ffmpeg_path` re-resolves without a backend restart; a missing binary is not latched | Triage D-40 |
| No cache | ffmpeg and ffprobe are resolved on every use, and `detect_gpu()` probes the binary resolved at that call; nothing is cached by path | Session 33 plan D-16 |
| Truthful card | The Dependencies row reports the resolved path and version, and checks ffprobe beside it | Triage D-40 |
| Tests | Unit for the resolver order and re-resolve; the downloader passes `ffmpeg_location`; contract test for the reported path | Local Canon |

<a id="tts-sideload-load-residual"></a>

## TTS sideload load (residual)

> **MEU-98.** Registered 2026-10-17 from `MODEL-SIDELOAD-LOAD-500`. `list_available()` unions the sideload scan of `tts.models_directory` (`services/models.py:117-118`), so a dropped file shows as downloaded, but the scan never persists its path and `load()` reads only the database row (`models.py:141-150`). The adapter's `_require_weight_path` (`tts/adapter.py:133-142`) then raises `ModelLoadError`, which answers 422 "model weight file is missing" (`errors.py:36`) with nothing logged: the call (`adapter.py:247`) sits outside the try that logs load failures.

| Rule | Contract | Source |
|------|----------|--------|
| Mark downloaded | A sideloaded `.pth`/`.onnx` found in `tts.models_directory` is recorded with `mark_downloaded(id, path)`, as a managed download is; the repository records the file size | Spec 02 §Model manager (Sideload), triage D-86; D-125 |
| Record on scan | `list_available()` and `load()` record a scanned file whose id has a catalog row; there is no write when the row is already recorded at that path, and an id with no row stays display-only | Spec §ModelService; D-125 |
| Load resolves | `load()` uses the recorded path for a sideloaded variant, so a variant listed as downloaded can be loaded; legacy and vocab checks are unchanged | Spec §ModelService, triage D-86 |
| Logged failure | Every load failure, including a missing weight file, logs `tts.load_failed` with the variant and cause before the 422, as the adapter's other load failures do (`adapter.py:123-124`) | Triage D-86; Local Canon AGENTS §Code Quality |
| spaCy directory change | After `tts.models_directory` changes, the next readiness check removes the spaCy entries av-kit appended to `sys.path` for the old directory and appends the new directory's; entries av-kit did not add are never touched | Known issue `TTS-SPACY-SYSPATH-STALE-DIR`; D-128 |
| Tests | Unit: a sideloaded file is listed, persisted and loads; a file removed after the scan returns the 422 and the log line; contract test for `GET /models/downloaded` then `POST /models/load`; a `tts.models_directory` change swaps the spaCy `sys.path` entry on the next readiness check | Local Canon |

> **Delivered (Session 42).**
> - `ModelService` records a scanned file before it reads the catalog, in both `list_available()` and `load()` (`SIDELOAD_RECORD`). A row already recorded at that path is not written again, and a scanned id with no row stays display-only (`RECORD_RULE`). The scan stays the port's; core touches no files.
> - The TTS adapter logs one `tts.load_failed` per failed load, including a missing or unreadable weight file, a missing runtime and an unsupported format. A `ModelLoadError` with a cause logs the cause's type (`LOG_CAUSE`).
> - `activate_spacy_dir` tracks the `sys.path` entries it appended. On a `tts.models_directory` change it removes the old directory's entries and appends the new ones; entries it did not append are never touched (`SPACY_PATH_SWAP`, rider `TTS-SPACY-SYSPATH-STALE-DIR`).
> - AC-98.1 to AC-98.9; AC-98.10 is the eSpeak evidence stage.

<a id="transcript-failure-reason-residual"></a>

## Transcript failure reason (residual)

> **MEU-115.** Registered 2026-11-04 from `TRANSCRIPT-FAILED-NO-REASON`, with rider `CONSOLE-FAILURE-DETAIL-LOST`. The reason is stored per video in `TranscriptItem.error_message` (`services/transcript.py:477`) and goes no further: `_job_out` passes `job.error_message`, which this service never fills, no route returns items, and the service logs nothing. A video with no captions is silent too. The adapter returns `None` for both `TranscriptsDisabled` and `VideoUnavailable` (`NONE_ERRORS`), so today the port can't tell them apart.

| Rule | Contract | Source |
|------|----------|--------|
| Causes | Each failure or skip maps to one short av-kit message: blocked, no captions, unavailable, or other with its reason. The blocked message names a next step: try later or on another network. The library's own multi-paragraph text is not shown. | Local Canon: triage D-218 |
| Port | The transcript port reports the cause, so no captions and unavailable are told apart. | Local Canon: triage D-218 |
| API | The job the API returns carries the message when its last item failed or was skipped. A job ending `Failed` fills `error_message`. | Local Canon: triage D-218 |
| Card | The Transcript job card states the message. | Local Canon: triage D-218 |
| Log | Each failure or skip logs one line with the same message, so the Console has a line that matches the card. | Local Canon: triage D-218 |
| Console fields (rider) | The Console ring and `console.log` keep the model and the error text, after checking that redaction still holds. Errors always go to a file, even with `app.log_to_file` off, and the plan says how. | Local Canon: known issue `CONSOLE-FAILURE-DETAIL-LOST`; Mat's ruling, grouping D-247 |
| Done | A blocked job's card states the reason and the Console has a matching line. | Local Canon: triage D-218 |
| Tests | Unit for each cause, with no real network; a contract test for the route; a renderer test for the card; a redaction test for the kept fields. | Local Canon |

> **Delivered (Session 50).**
> - The port reports the cause: a skip is a `TranscriptSkip` (no captions or unavailable), and a block raises `TranscriptRetryableError` with the short text "caption request blocked" (D-291). `failure_message` writes the four user texts in one place, and `safe_reason` keeps an other reason to one redacted line with links removed (D-292).
> - Each skip and failure stores its message on the video and logs `transcript.item_skipped` (WARNING, persisted) or `transcript.item_failed` (ERROR) with it. A Failed job stores `JOB_MESSAGE` and a Done job with a skip stores `SKIPPED_JOB_MESSAGE` (D-295). The API returns `error_message` and `last_item_message` (D-293), and the card shows the message on line three (D-294).
> - Rider `CONSOLE-FAILURE-DETAIL-LOST`: the Console keeps `error`, `detail`, `device` and `variant_id` as single redacted lines, stdout gets only the safe message, and ERROR lines always reach `console.log` (D-296 to D-298, D-304, D-305; Mat's ruling D-247).
> - AC-115.1 to AC-115.19. Plan `docs/execution/plans/2026-11-05-transcript-failure-reason/`.

<a id="transcript-block-stop-residual"></a>

## Transcript block stop (residual)

> **MEU-116.** Registered 2026-11-04 from `TRANSCRIPT-BLOCK-KEEPS-REQUESTING`. `_run_parent` (`services/transcript.py:415-426`) goes on to the next video after a failure, so a block is retried `max_retries` times per video. Calculated from the defaults, not measured: a 100-video channel makes 300 attempts over about 2.75 hours. `transcript.requests_per_hour` has a Settings control, a schema and an MCP setting, and no service reads it.

| Rule | Contract | Source |
|------|----------|--------|
| Stop on block | When one video exhausts `max_retries` on `TranscriptRetryableError`, the run stops. That video and the rest stay `Pending`, and the job goes `Paused` with the reason. No growing wait and no new number. | Research-backed: triage D-219 |
| Resume | `resume_processing` picks up the `Pending` videos, as it does after any pause. | Spec §TranscriptService |
| Other failures | A failure that isn't a block ends that video `Failed` and the run goes on, as the run loop does today. | Spec §TranscriptService |
| Rate cap | `transcript.requests_per_hour` is enforced as a rolling cap over real requests. Default behaviour doesn't change: 6 s apart with a 300 s pause after 50 is already about 300 an hour. | Local Canon: triage D-220 |
| Tests | Unit with a fake port and clock: a block on the first video makes `max_retries` attempts and no request for the next video, then the job reads `Paused` with the reason; resume finishes the rest; a lowered cap delays the next request and the default cap delays nothing. | Local Canon |

> **Delivered (Session 50).**
> - A block that outlasts `max_retries` leaves its video `Pending` with `retry_count` 0, logs `transcript.blocked` at ERROR and pauses the job with the blocked message, so no request is made for any further video until Resume. Resume clears the job's message (D-299).
> - `requests_per_hour` is a rolling cap over every request, retries included, on an injected clock, in waits of at most a second that Stop and Pause end and that read the cap again (D-300, `RATE_WINDOW`).
> - The worker's exits and `start`, `resume` and `stop` share one rule under `_lock`, so a Resume racing the worker's exit leaves exactly one worker (D-306).
> - AC-116.1 to AC-116.9, with AC-11.6 and AC-11.8 amended under AC-116.6. Plan `docs/execution/plans/2026-11-05-transcript-failure-reason/`.

<a id="tts-build-capability-residual"></a>

## TTS build capability (residual)

> **MEU-117.** Registered 2026-11-04 from `TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME`. The installed backend has no torch or kokoro, so `_load_pytorch` (`tts/adapter.py:340-350`) always raises "PyTorch runtime is not bundled", yet `/models/available` offers the variant and `POST /models/download` fetches 327 MB for it. Mat ruled D-217 on 2026-11-04, which supersedes D-236 and closes `TTS-PYTORCH-RUNTIME-SETTINGS-DOWNLOAD`.

| Rule | Contract | Source |
|------|----------|--------|
| Capability | Whether a variant can run comes from whether its runtime imports in this process, from the same adapter that reports `DEVICE_PROBE`. Torch without kokoro counts as unavailable. | Human-approved: triage D-217 |
| Listed | `GET /models/available` still lists every seeded variant. A variant this build can't run has `available: false` and a `reason` that names a next step, such as choosing an ONNX model. `ModelVariantOut` in 04 gains the two fields. | Human-approved: triage D-217; same shape as the Voice availability rule in [§TTS language runtime](#tts-language-runtime-residual) |
| Refused | `POST /models/download` for that variant answers 409 before any download starts. | Human-approved: triage D-217 |
| Page | The TTS page shows the row disabled with the reason, and `defaultModelSelection` skips it. | Human-approved: triage D-217 |
| Existing file | A PyTorch file already on disk stays there and is listed disabled. There is no delete route. | Human-approved: triage D-217 |
| Load | `POST /models/load` of that variant keeps its 422, and its message carries the same reason. | Local Canon: 01 §Domain errors (`ModelLoadError`) |
| Dev | `npm run dev`, which runs the repo's `.venv` with torch, keeps loading and generating with the variant. | Human-approved: triage D-217 |
| MCP | `avkit_models` actions `available` and `download` read the same routes, so MCP gets the same fields and the same 409. | Local Canon: `mcp-server/src/toolsets/models.ts` |
| Not built | No bundled torch, no runtime download and no `KModel` import workaround. espeak is never downloaded or bundled. | Human-approved: triage D-217, D-237 |
| Done | An installed build cannot start the download of a model it cannot load, and the dev venv still loads and generates with it. | Human-approved: triage D-217 |
| Tests | Unit with the runtime present and absent; a contract test for the listed fields and the 409, with no job and no file written; a renderer test for the disabled row and the selection; the packaged smoke checks the 409 on a real build. | Local Canon |

> **Delivered (Session 51).**
> - `runtime_imports` in `tts/adapter.py` (`RUNTIME_PROBE`) reports whether a format's runtime imports in this process. PyTorch without torch answers no without importing kokoro, and a failed kokoro import logs `tts.runtime_probe_failed` with the class name only. The adapter asks it once per format under a lock, through `TTSPort.runtime_present` (`RUNTIME_PRESENT`, D-309).
> - `MODEL_REASONS` and `ModelAvailability` in `domain/tts.py` hold the two fixed reason texts (D-310), and the adapter's own refusal now uses the PyTorch text (D-312, option A).
> - Before any work, `ModelService.download` answers 409 `ConflictError` and `load` answers 422 `ModelLoadError` with the reason, and each logs `model.download_refused` or `model.load_refused` (`MODEL_REFUSAL`, D-311). Every route that returns a variant carries `available` and `reason` (`MODEL_FIELDS`), and the MCP `available` and `download` descriptions name them (D-318).
> - The TTS page lists an unavailable row disabled with its reason, and `defaultModelSelection` skips it (D-320).
> - `tools/smoke_packaged_tts.py --phase capability` (`CAPABILITY_SMOKE`) proved the listing, both refusals and their log lines on a fresh frozen build. The dev venv still loads and generates with the PyTorch variant (`DEV_CHECK`) (D-315, D-316).
> - AC-117.1 to AC-117.16. Plan `docs/execution/plans/2026-11-06-tts-build-capability/`.

<a id="tts-load-keeps-model-residual"></a>

## TTS load keeps the current model (residual)

> **MEU-119.** Registered 2026-11-04 from `TTS-FAILED-LOAD-DROPS-MODEL`. `load_model` calls `self.unload_model()` first (`tts/adapter.py:251`), before it checks the weight path, the device or the runtime, so any failed load leaves nothing loaded.

| Rule | Contract | Source |
|------|----------|--------|
| Order | `load_model` checks the weight path, the device and the runtime before `unload_model`. No load-before-unload. | Local Canon: triage D-221 |
| Failed check | Load A, fail a load of B on one of those checks, and status still shows A. | Local Canon: triage D-221 |
| After the unload | A failure after the unload, while building the model or session, still leaves nothing loaded on `cpu`. | Local Canon: triage D-221 (no load-before-unload); MEU-75 AC-75.4, AC-75.5 |
| Amended expectation | `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg` (`tests/integration/test_tts_device_resolution.py:616-640`) loads a model, fails the device probe and asserts nothing is loaded. D-221 reverses that for a failed check, and the docstring at `tts/adapter.py:241-243` says the same. The plan names both as an amended expectation, as AGENTS §Testing requires. Independent review approved this one amendment on 2026-11-04 (grouping scoping review, round 1). It keeps the `ModelLoadError`, cause, logging and path-redaction assertions; the vocab branch at `:641-653` starts unloaded and needs no change. | Local Canon: triage D-221; AGENTS |
| Open for the plan | `test_ac_75_9_engine_import_failure_is_model_load_error_neg` (`:735-752`) asserts nothing is loaded after an engine import fails. If the runtime check above moves those imports before the unload, that test conflicts with Failed check. The review's approval doesn't cover it, so the plan names how it's handled and takes that to independent review or Mat before changing it. | Local Canon: AGENTS; grouping scoping review, round 1 |
| Tests | Unit: load A, then fail B on the missing weight, the failing probe and the missing runtime, with status showing A each time and no unload called; a constructor failure still reads unloaded; a contract test for `/models/load` then `/models/status`. | Local Canon |

> **Delivered (Session 52).**
> - `LOAD_CHECKS`: `load_model` runs the weight check, the device probe, the format check and the runtime check before `unload_model` (`tts/adapter.py:302-331`, the unload at `:332`). The runtime check reads MEU-117's `runtime_present` memo (D-322). A runtime probe that raises logs only its class and raises "TTS runtime probe failed" (D-323).
> - `LOAD_KEEPS`: a load that fails one of `LOAD_CHECKS` leaves A loaded on its device. AC-119.1 to AC-119.5 pin it for each check, AC-119.6 pins one runtime probe per load, and AC-119.9 pins it over `/models/load` then `/models/status` (`tests/e2e/test_api_model_load_keeps.py`).
> - The D-221 limit: a failure after the unload, while the model or session is built, still leaves nothing loaded on `cpu` (AC-119.7, AC-119.8). The docstring says so (`adapter.py:289-294`, D-325).
> - The amended test: `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg` now asserts A still loaded on `cuda` (`tests/integration/test_tts_device_resolution.py:647`). Its `ModelLoadError`, cause, logging and path assertions stay, and the vocab half (`:649-661`) is unchanged.
> - D-324 A′: `test_ac_75_9_engine_import_failure_is_model_load_error_neg` and `test_ac_98_5_kokoro_import_logs` pass a runtime probe that says yes (`:749`, `:865`). That is setup only: every assertion stays, and the two tests pin the import failure after the unload.
> - `HOME_SCRUB` (D-335): `console_field` replaces the home folder with `~` before the link, redaction and length rules (`services/health.py:96-126`), so the missing-weight `detail` reads `~\.avkit\models\…`. The six log sites and AC-115.9 are unchanged (AC-119.10). An 8.3 short form of the home folder isn't matched, so a `tts.models_directory` saved in that form reaches `detail` as saved. Mat ruled that the short form is matched in a row of its own with a Red, in a later plan (D-337, 2026-11-07); it is filed as `CONSOLE-HOME-SCRUB-SHORT-FORM`.
> - The registered text above cites the 2026-11-04 tree. At `b6c3895` the unload was at `adapter.py:299` and the docstring at `:289-291`; the tests were at `:620-643` (amended), `:645-657` (the vocab half) and `:738-756` (the open test).
> - AC-119.1 to AC-119.10. Plan `docs/execution/plans/2026-11-06-tts-load-fp16/`.

<a id="tts-onnx-fp16-audio-residual"></a>

## TTS ONNX FP16 audio (residual)

> **MEU-121.** Registered 2026-11-04 from `TTS-ONNX-FP16-NONFINITE-AUDIO`. FP16 returned no finite samples on 11 of 140 sentence runs, measured in the dev venv on the files a fresh download gets. `_as_float32_pcm` correctly refuses that audio (`tts/adapter.py:148-161`), so the whole generate call fails. FP32 and INT8 from the same pinned revision had no failures. The cause is unknown and isn't length. A fresh install preselects FP16 only through catalog order (`tts-controls.ts:104-121`); that was read from the code, not run on a fresh install.

| Rule | Contract | Source |
|------|----------|--------|
| Preselection | Until the cause is known, a fresh install preselects ONNX INT8 and not FP16: where the selection falls back by catalog order, INT8 comes first. ONNX FP32 is the alternative. | Human-approved: triage D-239 |
| Listening check | Mat listens to the INT8 sample before this ships. | Human-approved: triage D-239 |
| Cause | Look for the cause, with the failing sentences as a fixed test set. | Human-approved: triage D-239 |
| Test set | The sentences, the 96-word passage and the probe go in the plan folder, because `C:/Temp` isn't durable. | Local Canon: known issue `TTS-ONNX-FP16-NONFINITE-AUDIO` notes |
| FP16 outcome | If FP16 can't be made to work, what happens to the variant comes back to Mat. Nothing here removes or disables it. | Human-approved: triage D-239 |
| Done | The preselected model generates the 40 test sentences and the 96-word passage on a packaged build with no failure, and the cause or the outcome for FP16 is recorded. | Human-approved: triage D-239 |
| Tests | Renderer unit for `defaultModelSelection`, with nothing downloaded and with several rows downloaded; the packaged check above. | Local Canon |

> **Delivered (Session 52).**
> - `PRESELECT_ORDER` is `['kokoro-onnx-int8', 'kokoro-onnx-fp32']` (`ui/src/renderer/src/features/tts/tts-controls.ts:108`). `defaultModelSelection` (`:118`) ranks the runnable rows by it for the first-downloaded and first-row fallbacks (`:132`), so a fresh install preselects INT8 (AC-121.1 to AC-121.5, and AC-121.6 on the built app). FP16 is still offered, and a fresh install keeps it when it is the only downloaded row (D-330).
> - The listening check: Mat chose INT8 after hearing the sample (D-331, 2026-11-07).
> - `SENTENCE_SMOKE` (`tools/smoke_packaged_tts.py --phase sentences`), on a fresh onedir: FP16 failed 12 of 149 jobs, every one on "generated audio must be finite". They were the rate probe's 11 sentences and the 96-word passage (AC-121.7). INT8 passed all 149 (AC-121.8).
> - The spike (`fp16-spike.py`, AC-121.9) stopped at `done`. No setting it tried stopped the failures. ORT 1.31.1 with default settings reproduced the probe's 11 failures (E0). Each graph optimization level (E1: 15, 16 and 16 failures) and a single intra-op thread (E4: 16) changed which pairs failed, but some still failed each time. Turning off the memory arena (E4) gave E0's 11. E2 (ORT 1.24.4 and 1.29.0) didn't run, because those wheels aren't in the offline cache. E3 tried small style and speed changes around each failing sentence, and most of them passed. E5 found where every failing pair first goes non-finite: the output of `/decoder/decoder/generator/Div`, whose two inputs are both finite. So FP16 divides by a zero or near-zero denominator there. What happens to FP16 is Mat's decision (D-239).
> - D-336 (Mat, 2026-11-07): FP16 stays as shipped, offered and never preselected while INT8 or FP32 can run, and `TTS-ONNX-FP16-NONFINITE-AUDIO` stays open. The guarded phase computation is MEU-127, spike first.
> - Review round 1 F2 (D-340, D-343): the sentences smoke counts a WAV's frames only when its payload holds every frame the header declares (`tools/smoke_packaged_tts.py:357-365`), so a header-only or truncated file fails AC-121.8. `tests/tooling/test_smoke_packaged_tts.py` covers both and a complete file.
> - The registered text above cites the 2026-11-04 tree. At `b6c3895`, `_as_float32_pcm` was at `adapter.py:179-192` and the catalog-order fallback at `tts-controls.ts:104-125`.
> - AC-121.1 to AC-121.9. Plan `docs/execution/plans/2026-11-06-tts-load-fp16/`.

<a id="transcript-source-metadata-residual"></a>

## Transcript source metadata (residual)

> **MEU-122.** Registered 2026-11-04 from `TRANSCRIPT-TITLE-IS-VIDEO-ID` and `TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME`, one MEU because both come from one enumeration (grouping D-241). `FetchedTranscript` has no title, so the adapter's fallback to the video ID always wins (`transcript/adapter.py:42-44`). `add_channel` uses `info.title` as the channel name (`services/transcript.py:137,151`), which for a channel's videos tab is the tab's playlist title. `add_channel` already runs a flat enumeration and keeps only the IDs (`extract_video_ids`).

| Rule | Contract | Source |
|------|----------|--------|
| Title | Each video's title comes from the flat enumeration `add_channel` already runs and is stored per item, with no extra request per video. The video ID stays as the fallback only. | Local Canon: triage D-223 |
| Stored title | Fetching an item keeps its stored title rather than replacing it with the result's (`services/transcript.py:516`). | Local Canon: triage D-223 |
| Channel name | `channel_name` comes from the same enumeration, falling back to today's title. | Local Canon: triage D-224 |
| Slug | The existing output folder slug stays unchanged. | Local Canon: triage D-224 |
| Tests | Unit with fake enumeration output: titles are stored and reach the files and the compiled headings; a missing title falls back to the ID; a missing channel falls back to today's title; the slug is unchanged; the fake counts no extra request. | Local Canon |

> **Delivered (Session 53).**
> - The registered text above cites the 2026-11-04 tree. At `9093d95`, the title fallback was at `transcript/adapter.py:63-65`, the channel name at `services/transcript.py:158,161`, and the fetched title at `:611`.
> - `extract_video_ids` returns a `VideoListing` of IDs and titles with the channel name (`ports/youtube.py:25`, `domain/download.py:268`, `:280`), from the same flat enumeration and with no extra request per video (AC-122.1 to AC-122.4, AC-122.12). A bare channel's tabs are flattened (`FLAT_TABS`, AC-122.18).
> - `add_channel` stores each listed title on its item (`services/transcript.py:153`), and the ID is the fallback only (AC-122.8, AC-122.9). The channel name is the listing's, falling back to the extract title (`:169`, AC-122.10). The folder, the compiled volumes and the raw zip keep the extract title's slug (`:160-163`, `:347`, `:381`, AC-122.11).
> - A fetch keeps the stored title (`:611`, AC-122.13). The front matter quotes the title and channel, and the Contents label escapes backslashes and square brackets (`:752-770`, AC-122.14).
> - The "Last:" label comes only from a processed item (`routes/transcripts.py:35`, AC-122.15).
> - Titles don't reach the Console (AC-122.16), and a SQL error's text holds no bound value (`database/engine.py:82`, AC-122.17).
> - Shapes measured live once under D-353 (`C:/Temp/av-kit/s53-shapes.txt`). AC-122.1 to AC-122.18. Plan `docs/execution/plans/2026-11-07-transcript-metadata/`.

<a id="tts-fp16-phase-guard-residual"></a>

## TTS FP16 phase guard (residual)

> **MEU-127.** Registered 2026-11-07 from `TTS-ONNX-FP16-NONFINITE-AUDIO` on Mat's D-336 ruling (Session 52). In Session 52's spike (E5), every failing FP16 pair first went non-finite at the output of `/decoder/decoder/generator/Div`, whose two inputs were finite. That node is the exported `atan2` of the phase, `Div(imag, real)`, so in FP16 `real` reaches zero or near zero there. FP32 and INT8 don't fail.

| Rule | Contract | Source |
|------|----------|--------|
| Spike first | A spike counts the zero and near-zero denominators at that node on the failing pairs, patches the phase computation in a copy of the FP16 graph so it no longer divides by them, reruns the 149 `--phase sentences` jobs on the patched graph, and Mat listens to its output. | Human-approved: D-336 |
| FP16 stays | Until then FP16 stays as shipped: offered, never preselected while INT8 or FP32 can run (D-330, D-331). | Human-approved: D-336 |
| Upstream | Nothing is posted to the model's Hugging Face discussion. | Human-approved: D-336 |
| Outcome | What ships, a patched graph or nothing, comes back to Mat with the spike's counts. | Human-approved: D-336 |
| Tests | The packaged `--phase sentences` smoke on the patched FP16 graph, 149 jobs, each WAV with its full payload (AC-121.8). | Local Canon |

<a id="download-failure-reason-residual"></a>

## Download failure reason (residual)

> **MEU-137.** Registered 2026-11-10 from `DOWNLOAD-FAILED-NO-REASON` (triage D-531; grouping D-535). The reason is stored (`services/download.py:544-549`) and served (`routes/downloads.py:56`), but `DownloaderPage.tsx:476-485` builds each card without `errorMessage`, so `QueueCard.tsx:277` shows the placeholder, and the failure branches log nothing. Mat's gKcOjnDJfzk job showed Failed with an empty Console on 2026-11-10.

| Rule | Contract | Source |
|------|----------|--------|
| Card | The Downloader card shows the job's `error_message` on a Failed or AgeRestricted row, as the Transcript card does. | Local Canon: [§Transcript failure reason](#transcript-failure-reason-residual) Card row; `TTS-GENERATE-FAILED-SILENT` |
| Message | A failure stores one short av-kit message per cause: YouTube refused the request (reload page, SABR-only, bot check), no format at that quality, cookies failed, file write failed, or other with yt-dlp's first line. yt-dlp's multi-line text is not stored whole. | Local Canon: triage D-218 pattern |
| Log | A job logs `download.started`, `download.done` and `download.failed`; the failure line is ERROR with the message in `error` and yt-dlp's raw line, redacted, in `detail`. | Local Canon: [§Transcript failure reason](#transcript-failure-reason-residual) Log and Console rows (D-247) |
| Done | A failed download's card states the reason and the Console has a matching line. | Local Canon |
| Tests | Unit for each cause with a mocked port; a renderer test for the card; a test that the failure line keeps `error` and `detail` through redaction. | Local Canon |

> **Delivered (Session 65).**
> - `DownloadFailureCause` (`domain/enums.py:145`) is `refused`, `no_format`, `cookies`, `write_failed` and `other`, and `download_failure_message` (`domain/download.py:109`) is the only place the stored texts are written; only `other` carries yt-dlp's reason (`FAILURE_CAUSE_ENUM`, `FAILURE_MESSAGE`).
> - `classify_download_error` (`youtube/adapter.py:356`) takes the cause from `FAILURE_CAUSE_NEEDLES` (`:95`) or a SABR phrase, and the detail from yt-dlp's first non-empty line without its `ERROR: ` prefix; a `no_format` result with SABR seen is `refused` (D-636). `download` raises `DownloadFailedError` (01 §Domain errors) with them (`:621`), and an `OSError` outside cookie file mode as `write_failed` with only its type name and `strerror`, never the filename (`:627`, D-637) (`FAILURE_CAUSE`, `FAILURE_RAISE`).
> - `clean_line` (`domain/download.py:121`) and `scrub_line` (`services/download.py:118`) make the one line a site keeps: control and format characters gone, the home folder as `~` even when a tab, line break or dropped character splits it, links and cookie-looking values redacted, and never a raise (`CLEAN_LINE`, `SCRUB_LINE`, D-627).
> - `_run_one` (`services/download.py:604`) logs `download.started` (`:621`) and `download.done` (`:696`) at INFO, and `download.failed` at ERROR (`:629`, `:658`) with the stored message in `error` and the cleaned raw line in `detail`; AgeRestricted keeps its text and Cancelled logs nothing new (`FAILURE_LOG`, D-633, D-634, D-638).
> - The Downloader card shows `error_message` (`useDownloadQueue.ts:21`, `DownloaderPage.tsx:485`; `CARD_REASON`).
> - AC-137.1 to AC-137.11. Plan `docs/execution/plans/2026-11-11-download-failure-visibility/`.

<a id="download-audio-extract-residual"></a>

## Download audio extract (residual)

> **MEU-142.** Registered 2026-11-10 from `DOWNLOAD-MP3-NOT-CONVERTED` (triage D-534; grouping D-542). `StandardMp3` maps to plain `bestaudio` (`youtube/adapter.py:61`), and in cookie mode every audio format maps to `COOKIE_AUDIO_SELECTOR` (`:113-115`). Before Session 67, `DownloadService` got no `MediaPort` (its construction, now `api/wiring.py:175-181`), so the MP3 convert in [02 §Media adapter](02-infrastructure.md#media-adapter-mediaadapterpy) was never built.

| Rule | Contract | Source |
|------|----------|--------|
| Convert | When the job's audio format is `StandardMp3`, the service converts the downloaded file with `MediaPort.convert` to MP3 and stores the MP3 as the job's file, in any cookie mode. The source file is removed after a good convert. | Spec: 02 §Media adapter `convert` row; [§Construction](#construction) `MediaPort` row; grouping D-542 |
| No row | The convert creates no `ConversionJob` row. | Spec: [08 §`ConversionJob` — persistable](08-video-conversion.md#conversionjob--persistable) |
| No ffmpeg | Without ffmpeg the job fails with the `FFmpegNotFoundError` message on its card (MEU-137), and the downloaded file stays. | Spec: 02 §download, audio-only paragraph |
| Tests | Unit with a fake `MediaPort`: MP3 converts, other formats do not, a failed convert keeps the source; one real-ffmpeg integration test on a generated clip, deselected on CI. | Local Canon |

> **Delivered (Session 67).**
> - `DownloadService` takes `media: MediaPort`, a required keyword after `youtube`, and `build_services` passes it the one `FFmpegAdapter` that the other services hold (`MEDIA_PORT`, D-664).
> - The Convert rule applies to audio-only jobs, the only jobs whose audio format the adapter reads (`youtube/adapter.py:752`). `AUDIO_EXTRACT` maps `StandardMp3` to `.mp3` with `libmp3lame` at 192 kbps, and `_run_one` converts after the download when the source is not already an `.mp3` (`AUDIO_EXTRACT`, `EXTRACT_TRIGGER`, D-665).
> - The MP3 takes a new name beside the source, `-2`, `-3` and so on when a name is taken, so no existing file is overwritten (`MP3_RESERVE`, D-666). The Done row with the MP3 is committed before the source is removed; a row removed during the convert keeps both files; a file that cannot be removed logs `download.source_kept` or `download.partial_kept` (`CONVERT_DONE`, `ROW_GONE`, `KEPT_LOGS`, D-667).
> - A failed convert keeps the source, removes only the MP3 it reserved and fails the job with the not-found, write-failed or `MP3 convert failed` card; the Console detail is the last line of FFmpeg's text with paths masked, or `[REDACTED]` (`CONVERT_FAIL`, `SOURCE_KEPT`, `FAIL_DETAIL`, `LAST_LINE`, D-668).
> - A cancel during the convert lets the job finish Done, and the convert writes no `ConversionJob` row (`CONVERT_CANCEL`, `NO_CONVERSION_ROW`, D-669). CI deselects the real-FFmpeg test (`CI_DESELECT`, D-670).
> - Tests: AC-142.1 to AC-142.19. Plan `docs/execution/plans/2026-11-12-download-audio-extract/`.

## What this layer must not do

| Forbidden | Why |
|-----------|-----|
| Persist `QueueRuntime` / `SABRStatus` | Phase 1 |
| Import `avkit_infra` | Hexagonal |
| Store transcript/audio/video bytes in SQLite | Pointers only |
| Read `progress.json` to resume | `TranscriptItem` |
| Pass yt-dlp `--download-archive` | Archive repo |
| `Paused` on `DownloadJob.status` | Queue-level only |
| Treat `TranscriptItem` as a queued job (reorder/cancel one video) | No GUI for that |
| `Operation` enum / generic job kernel | Phase 1 drop |
| OCR Part 1, SSE, multi-file TTS batch | Deferred |
| Convert-page queue / `ConversionService` | Phase 8 — [08-video-conversion.md](08-video-conversion.md); do not add under MEU-10–13 |
| Capture inbox / `CaptureService` | Phase 9 — [09-screenshot-capture.md](09-screenshot-capture.md); do not add under MEU-10–13 |
| Hold UoW across an entire channel crawl | Phase 2 |
| Log or save cookie contents | Settings = mode + path |

---

## Downstream planning notes

| Phase | Must follow this spec |
|-------|------------------------|
| **4 REST** | One route → one service method. Include `POST /transcripts/{id}/requeue`, `GET /models/download-runtime`, `GET /health/console`. `/downloads/stop` = `cancel_processing`. Format `speed_bps` / `eta_seconds` in the schema layer |
| **5 MCP** | Same methods; no extra job types; no SQLite |
| **6 GUI** | Poll `get_queue` / `get_job`; processor + SABR + `ModelDownloadRuntime` from session getters |

---

## Testing (Phase 3)

Unit tests with **fake ports** + in-memory or tmp UoW:

| Case | Assert |
|------|--------|
| Add playlist | N jobs; duplicate video_id skipped |
| Archive hit | New job `Skipped`; Clear All keeps archive |
| SABR force | Incompatible Pending → `QualityBlocked`; clear → `Pending` |
| Download pause | After current Done, runtime `Paused`; other items still `Pending` |
| Cancel | In-flight `Cancelled`; runtime `Idle` |
| Transcript resume | `Done` items not fetched again |
| Transcript Stop | Parent `Cancelled`; leftover items `Pending`; start skips that row until requeue |
| Transcript requeue | `Cancelled` → `Pending`; 409 otherwise |
| Transcript retry failed | `Failed` → `Pending`; Failed items reset; 409 otherwise |
| Transcript start vs resume | Start ignores Paused/Failed; resume 409 unless Paused |
| Retryable then fail | `retry_count` then `Failed` |
| Compile split | Two volumes when over max words |
| Zip | `zip_path` set; raw files unchanged |
| TTS generate | Job has hash/preview, not full text; MP3 calls `MediaPort.convert` |
| Prepare | Disabled steps omitted; unknown id errors |
| Settings | Unknown key rejected |

No live YouTube / HF / Kokoro in the default unit suite.

---

## Validation commands

Registered exact-receipt forms live in [`.agent/docs/commands.md`](../../.agent/docs/commands.md). Targeted:

```bash
uv run pytest tests/unit/test_services.py -x --tb=short -v
uv run pyright packages/core/
uv run ruff check packages/core/
```
