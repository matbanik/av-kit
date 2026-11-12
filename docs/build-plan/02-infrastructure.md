# Phase 2 — Infrastructure Layer

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: [Phase 1](01-domain-layer.md) | Outputs: [Phase 3](03-service-layer.md)

---

## Goal

Implement the ports defined in Phase 1. Map domain types onto SQLite **without inventing a second model**. Talk to yt-dlp, youtube-transcript-api, Kokoro, FFmpeg, and Hugging Face Hub behind those ports.

| Source | Decision |
|--------|----------|
| Spec | [Phase 1](01-domain-layer.md) persistable objects, UoW repos, “do not store” list |
| Local Canon | [DESIGN_PROPOSAL.md §5](../../_inspiration/DESIGN_PROPOSAL.md) (SQLite + inline migrations), [_shared_patterns.md §4–5](../../_inspiration/_shared_patterns.md), [_downloader_pseudo_logic.md](../../_inspiration/_downloader_pseudo_logic.md), [_transcript_pseudo_logic.md](../../_inspiration/_transcript_pseudo_logic.md), [_tts_pseudo_logic.md](../../_inspiration/_tts_pseudo_logic.md) |
| Research-backed | SQLAlchemy 2.x mapped columns; SQLite WAL for API **request + worker threads**; yt-dlp archive = `(extractor, id)` skip-set |
| Human-approved | 2026-08-18: seven tables, no STI `jobs`. **2026-08-24:** eighth table `conversion_jobs` is Phase 8 only ([08-video-conversion.md](08-video-conversion.md)). **2026-08-26:** `capture_shots` / `capture_requests` are Phase 9 only ([09-screenshot-capture.md](09-screenshot-capture.md)); still no unified `jobs` table |

This file **implements** Phase 1. If a column, table, or persisted flag is not in Phase 1, it does not appear here.

---

## Package layout

```
packages/infrastructure/src/avkit_infra/
├── database/
│   ├── engine.py          # SQLite URL, WAL, busy_timeout, session factory
│   ├── models.py          # SQLAlchemy ORM ↔ Phase 1 fields only
│   ├── mappers.py         # ORM row ↔ domain dataclass
│   ├── repositories.py    # Port implementations
│   ├── unit_of_work.py    # SqlAlchemyUnitOfWork
│   └── migrations.py      # Append-only ALTER TABLE list
├── youtube/
│   └── adapter.py         # YouTubeAdapter(YouTubePort)
├── transcript/
│   └── adapter.py         # TranscriptAdapter(TranscriptPort)
├── tts/
│   └── adapter.py         # KokoroAdapter(TTSPort)
├── media/
│   └── adapter.py         # FFmpegAdapter(MediaPort)
├── model_manager/
│   └── manager.py         # Hugging Face download / sideload (not a Job)
└── filesystem/
    └── writer.py          # Atomic file writes + optional progress.json export
```

**Dependency rule:** `avkit_infra` imports `avkit_core` (domain + ports). Domain never imports infra. Services (Phase 3) depend on ports; this package supplies the implementations.

---

## Database

### File and engine

| Item | Rule |
|------|------|
| One file | `{app_data}/avkit.db` — Windows `%LOCALAPPDATA%/av-kit/`, else `~/.avkit/` |
| Driver | SQLAlchemy 2.x + `sqlite+pysqlite` |
| Concurrency | `PRAGMA journal_mode=WAL`; `PRAGMA busy_timeout=5000`; `PRAGMA foreign_keys=ON` |
| Why WAL | FastAPI request threads + download/transcript/TTS **worker threads** in the **same API process** commit concurrently. MCP never opens this file ([05-mcp-server.md](05-mcp-server.md) — REST only). |
| Check-same-thread | `False` (FastAPI + worker threads). UoW still owns one session per unit of work |
| Create | `Base.metadata.create_all` on first boot, then run `migrations.py` |

Do not use Alembic. Local Canon: append-only `ALTER TABLE` list, each wrapped so a repeat is a no-op (Zorivest / DESIGN_PROPOSAL §5). Greenfield: the CREATE TABLE statements in `models.py` **are** schema v1; `migrations.py` starts empty and only grows after the first shipped schema.

### Settings key convention (locked)

Phase 1 locks leaf keys. Phase 2 stores them as:

- Column `namespace` = first segment (`downloader`, `transcript`, `tts`, `app`, `ui`)
- Column `key` = remainder (`quality`, not `downloader.quality`)
- Unique `(namespace, key)`
- `GET /api/v1/settings/{namespace}` loads all rows for that namespace

### Type mapping

| Domain | SQLite / SQLAlchemy |
|--------|---------------------|
| `str` (UUID) | `String(36)` PK |
| `str` (url, title, enum name) | `Text` or `String(n)` — store **enum `.name`** (`Pending`, `P1080`), not integers |
| `bool` | `Integer` 0/1 or `Boolean` |
| `float` progress | `Float` 0.0–1.0 |
| `float \| None` speed_bps | `Float` nullable |
| `int \| None` eta_seconds, file_size | `Integer` nullable |
| `Path \| None` | `Text` nullable — store the path string as given; do not rewrite to URI |
| `datetime` | `DateTime(timezone=True)` UTC |

Never store transcript `text`, PCM, video bytes, cookies, or tokens.

### Tables (exactly these seven — Phase 2)

No `jobs`, `job_artifacts`, `queue_runtime`, `sabr_state`, `download_job_parents`. `model_variants` has **no** `is_loaded` / `device` columns.

**Phase 8 addendum (2026-08-24):** eighth table `conversion_jobs` is specified in [08-video-conversion.md](08-video-conversion.md). Implement it under MEU-29 via append-only migration — do not invent a STI `jobs` table.

**Phase 9 addendum (2026-08-26):** `capture_shots` and `capture_requests` are specified in [09-screenshot-capture.md](09-screenshot-capture.md). Implement them under MEU-35 via append-only migration — still no STI `jobs` table.

#### `download_jobs`

| Column | SQL | Null | Notes |
|--------|-----|------|-------|
| `id` | `CHAR(36)` PK | no | |
| `url` | `TEXT` | no | |
| `video_id` | `TEXT` | no | Index for queue-duplicate check |
| `title` | `TEXT` | no | |
| `quality` | `TEXT` | no | `QualityPreset.name` |
| `audio_only` | `BOOLEAN` | no | default 0 |
| `audio_format` | `TEXT` | no | `AudioFormat.name` |
| `status` | `TEXT` | no | `DownloadStatus.name` |
| `progress` | `FLOAT` | no | default 0 |
| `speed_bps` | `FLOAT` | yes | |
| `eta_seconds` | `INTEGER` | yes | |
| `file_size` | `INTEGER` | yes | bytes |
| `file_path` | `TEXT` | yes | |
| `error_message` | `TEXT` | yes | |
| `queue_position` | `INTEGER` | no | list order |
| `created_at` | `DATETIME` | no | |
| `updated_at` | `DATETIME` | no | |

Indexes: `queue_position`; `status`; `video_id`.

`delete_all` (Clear All) deletes this table only.

#### `download_archive`

| Column | SQL | Null | Notes |
|--------|-----|------|-------|
| `extractor` | `TEXT` | no | yt-dlp extractor id, usually `youtube` |
| `video_id` | `TEXT` | no | |
| `title` | `TEXT` | yes | |
| `recorded_at` | `DATETIME` | no | |

PK / unique: `(extractor, video_id)`. Survives Clear All.

#### `transcript_jobs`

| Column | SQL | Null | Notes |
|--------|-----|------|-------|
| `id` | `CHAR(36)` PK | no | |
| `channel_url` | `TEXT` | no | |
| `channel_name` | `TEXT` | no | |
| `status` | `TEXT` | no | `TranscriptStatus.name` |
| `output_dir` | `TEXT` | no | |
| `video_count` | `INTEGER` | no | default 0 |
| `word_count` | `INTEGER` | no | default 0 |
| `zip_path` | `TEXT` | yes | |
| `queue_position` | `INTEGER` | no | |
| `error_message` | `TEXT` | yes | |
| `created_at` | `DATETIME` | no | |
| `updated_at` | `DATETIME` | no | |

**No** `video_ids`, `processed_ids`, or `progress` columns.

#### `transcript_items`

| Column | SQL | Null | Notes |
|--------|-----|------|-------|
| `id` | `CHAR(36)` PK | no | |
| `job_id` | `CHAR(36)` FK → `transcript_jobs.id` ON DELETE CASCADE | no | |
| `video_id` | `TEXT` | no | |
| `title` | `TEXT` | yes | |
| `language` | `TEXT` | yes | |
| `word_count` | `INTEGER` | no | default 0 |
| `path` | `TEXT` | yes | `raw/{video_id}.md` |
| `status` | `TEXT` | no | `TranscriptItemStatus.name` |
| `error_message` | `TEXT` | yes | |
| `retry_count` | `INTEGER` | no | default 0 |
| `processed_at` | `DATETIME` | yes | |

Unique `(job_id, video_id)`. Index `(job_id, status)`.

This table is the resume store. `progress.json` is not read when rows exist.

#### `tts_jobs`

| Column | SQL | Null | Notes |
|--------|-----|------|-------|
| `id` | `CHAR(36)` PK | no | |
| `source_kind` | `TEXT` | no | `Inline` \| `File` |
| `source_path` | `TEXT` | yes | |
| `text_hash` | `TEXT` | no | |
| `text_preview` | `TEXT` | no | cap in mapper (200 chars) |
| `voice` | `TEXT` | no | |
| `speed` | `FLOAT` | no | |
| `format` | `TEXT` | no | `MediaFormat.name` |
| `status` | `TEXT` | no | `TTSStatus.name` |
| `output_path` | `TEXT` | yes | |
| `segments_total` | `INTEGER` | no | default 0 |
| `segments_done` | `INTEGER` | no | default 0 |
| `error_message` | `TEXT` | yes | |
| `created_at` | `DATETIME` | no | |
| `updated_at` | `DATETIME` | no | |

**No** full-text column.

#### `model_variants`

| Column | SQL | Null | Notes |
|--------|-----|------|-------|
| `id` | `TEXT` PK | no | Stable id, e.g. `kokoro-onnx-fp16` |
| `name` | `TEXT` | no | |
| `format` | `TEXT` | no | `PyTorch` \| `ONNX` |
| `precision` | `TEXT` | no | `FP32` \| `FP16` \| `INT8` |
| `size_bytes` | `INTEGER` | no | Catalog size |
| `path` | `TEXT` | yes | Local file when downloaded |
| `is_downloaded` | `BOOLEAN` | no | default 0 |

Seed on first boot (catalog, `is_downloaded=False` until files exist):

| id | name | format | precision | typical size |
|----|------|--------|-----------|--------------|
| `kokoro-pt-fp32` | PyTorch FP32 | PyTorch | FP32 | ~326 MB |
| `kokoro-onnx-fp32` | ONNX FP32 | ONNX | FP32 | ~326 MB |
| `kokoro-onnx-fp16` | ONNX FP16 | ONNX | FP16 | ~163 MB |
| `kokoro-onnx-int8` | ONNX INT8 | ONNX | INT8 | ~82–92 MB |

Repos: `hexgrad/Kokoro-82M` (PyTorch), `onnx-community/Kokoro-82M-v1.0-ONNX` @ `ONNX_REVISION` (ONNX weights and `voices/*.bin`). Exact filenames live in `model_manager`, not in extra columns.

#### `settings`

| Column | SQL | Null | Notes |
|--------|-----|------|-------|
| `namespace` | `TEXT` | no | |
| `key` | `TEXT` | no | leaf only |
| `value` | `TEXT` | no | serialized |
| `value_type` | `TEXT` | no | `String` \| `Number` \| `Boolean` \| `Json` |
| `updated_at` | `DATETIME` | no | |

PK: `(namespace, key)`. Defaults are **not** pre-inserted; missing key → service default from [06-gui.md](06-gui.md).

---

## ORM, mappers, repositories

### Mapping rule

ORM models are persistence records. Repositories return **domain dataclasses**. Do not leak `DownloadJobRow` into services.

`mappers.py` converts enum names ↔ enums, path strings ↔ `Path`, and truncates `text_preview`.

### Repository contracts

Implement the capabilities in [Phase 1 UoW](01-domain-layer.md). Concrete method names may tighten; behavior may not.

#### `SqlAlchemyDownloadRepository`

| Method | Behavior |
|--------|----------|
| `add(job)` | Insert |
| `get(id)` | Row or `None` |
| `list_queued()` | All rows, `ORDER BY queue_position ASC` |
| `update(job)` | Status, progress, speed, eta, paths, error, timestamps |
| `reorder(job_ids: list[str])` | Rewrite `queue_position` 0..n-1 in that order |
| `delete(id)` | Queue row only |
| `delete_all()` | `DELETE FROM download_jobs` — **not** archive |
| `reset_failed(id)` | `Failed` → `Pending`; clear `error_message`, `progress` |
| `has_video_id(video_id)` | Duplicate-in-queue check |

#### `SqlAlchemyArchiveRepository`

| Method | Behavior |
|--------|----------|
| `get(extractor, video_id)` | Entry or `None` |
| `add(entry)` | Insert; ignore conflict on unique key (idempotent Done) |
| `contains(extractor, video_id)` | Bool |

#### `SqlAlchemyTranscriptRepository`

Owns the `TranscriptJob` + `TranscriptItem` aggregate. No separate UoW attribute for items.

| Method | Behavior |
|--------|----------|
| `add_job` / `get_job` / `list_jobs` / `update_job` / `delete_job` / `reorder_jobs` | Parent CRUD; `delete_job` cascades items |
| `replace_items(job_id, items)` | After channel resolve: delete existing items, insert the resolved set, set `video_count` |
| `list_items(job_id)` | Ordered by insert / `video_id` (stable; not user-reorderable) |
| `update_item(item)` | Status, path, word_count, retry, error, `processed_at` |
| `progress_counts(job_id)` | `{total, done, skipped, failed, pending}` for card aggregates |
| `recompute_word_count(job_id)` | `SUM(item.word_count)` → parent `word_count` |

#### `SqlAlchemyTTSJobRepository`

`add`, `get`, `update` (status, segments, output_path, error), `delete`.

#### `SqlAlchemySettingsRepository`

`get(namespace, key)`, `set(namespace, key, value, value_type)`, `get_namespace(namespace)`, `set_namespace(namespace, dict)` (replace or upsert all keys in that namespace).

#### `SqlAlchemyModelRepository`

`list_all`, `get(id)`, `mark_downloaded(id, path, size_bytes)`, `list_downloaded` (`is_downloaded=True`). Never write `is_loaded`.

### Unit of work

```python
class SqlAlchemyUnitOfWork:
    def __enter__(self) -> Self: ...
    def __exit__(self, *exc) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

On enter, bind:

- `downloads`, `archive`, `transcripts`, `tts_jobs`, `settings`, `models`

Same session for all repos in the unit. Commit on success; rollback on exception. Pattern: Zorivest `SqlAlchemyUnitOfWork` — check that tree before inventing.

---

## Domain errors adapters must raise

Implement **only** the types in [Phase 1 `domain/errors`](01-domain-layer.md). Do not invent adapter-local error classes. `CookieAccessError` is the Phase 1 alias of `CookieTestError`. Adapters must **not** leak `yt_dlp.utils.DownloadError` or youtube-transcript-api exceptions across the port.

| Error | Raised by | Service maps to |
|-------|-----------|-----------------|
| `AgeRestrictedError` | `YouTubeAdapter.download` | `DownloadStatus.AgeRestricted` |
| `DownloadCancelledError` | download + stop flag | `Cancelled` |
| `SABRDetectedError` | optional; or flag on result | session `SABRStatus` + maybe `QualityBlocked` |
| `CookieTestError` | browser locked / bad file (alias `CookieAccessError`) | 422 / Failed with message |
| `TranscriptsDisabledError` | not raised by `TranscriptAdapter` (it returns a `TranscriptSkip`) | `TranscriptItemStatus.Skipped` |
| `NoTranscriptFoundError` | not raised by `TranscriptAdapter` (it returns a `TranscriptSkip`) | `Skipped` |
| `TranscriptRetryableError` | transcript adapter: `RequestBlocked` / `IpBlocked` (a 429 raises `IpBlocked`), text "caption request blocked" | increment `retry_count` |
| `DomainError` | transcript adapter: any other error, text a `LIBRARY_REASONS` reason or the class name | `Failed` with `failure_message(other, reason)` |
| `FFmpegNotFoundError` | media adapter | disable audio formats / TTS MP3 |
| `ModelLoadError` | Kokoro adapter | `TTSStatus.Failed` / model UI error |
| `ModelDownloadError` | model manager | variant stays `is_downloaded=False` |

`TranscriptPort.get_transcript` returns a `TranscriptResult`, or a `TranscriptSkip` carrying its `TranscriptFailureCause` ([01](01-domain-layer.md)) for a video with no transcript: `TranscriptsDisabled`, `NoTranscriptFound` and a listing with no transcript give `no_captions`, and `VideoUnavailable` gives `unavailable`. `RequestBlocked` and `IpBlocked` raise `TranscriptRetryableError("caption request blocked")`; youtube-transcript-api 1.2.4 raises `IpBlocked` for an HTTP 429, so a rate limit counts as a block. Every other error raises `DomainError(reason)`, where the reason is the adapter's `LIBRARY_REASONS` text (`AgeRestricted`, `VideoUnplayable`, `PoTokenRequired`, `InvalidVideoId`, `YouTubeDataUnparsable`, `YouTubeRequestFailed`, `FailedToCreateConsentCookie`) or else the exception's class name. The library's own text never crosses the port, because it can hold a URL with a query token; the library error stays as `__cause__`. Do **not** raise `TranscriptsDisabledError` / `NoTranscriptFoundError` from this method — those names exist for adapters that cannot return a skip.

---

## YouTube adapter (`youtube/adapter.py`)

Implements `YouTubePort`. Library: `yt_dlp` (import the library; do not shell out).

### `extract_info(url, flat=False)`

- Detect video / playlist / channel / shorts ([_downloader_pseudo_logic.md §1](../../_inspiration/_downloader_pseudo_logic.md)).
- `flat=True` (playlists/channels): `PlaylistInfo` with `video_ids` only.
- `flat=False` (single video): `VideoInfo`.
- Duplicate video IDs in a playlist: unique-preserve order.

### `extract_video_ids(channel_url)`

`flat_playlist=True`, honor `playlist_end` from options/settings (`0` = no limit). Used by transcript resolve.

Returns a `VideoListing` (Session 53 MEU-122, `youtube/adapter.py:479-491`): each flat entry's ID and title, and the top-level `channel`, falling back to `uploader`. `_clean_text` (`:143`) drops control characters and collapses whitespace, and an empty result is `None`. `_listed_videos` (`:177`) keeps the first title of a repeated ID. A bare channel URL returns one nested playlist per tab; `FLAT_TABS` flattens their entries one level deep and drops anything nested further (D-358). A single video lists itself with its own title. `_playlist_from_info` (`:264`) uses the same flatten through `_flat_entries` (`:158`), so the download add queues a bare channel's videos (`BARE_CHANNEL_FLAT`, D-361).

### `download(url, options)`

Build yt-dlp opts from `DownloadOptions`:

| Concern | Rule |
|---------|------|
| Format selector | Map `QualityPreset` / `AudioFormat` (table below). SABR Active → height ≤ 360; audio only `StandardMp3` / `HighM4a` |
| Output | `options.output_dir`; yt-dlp template; return final `file_path` + `file_size` |
| Progress | `progress_hooks`: bytes, total, speed → callback. Throttle updates (inspiration: time-based) |
| Cancel | Check stop callback in hook + logger; raise `DownloadCancelledError` |
| Cookies | `None` / `cookiesfrombrowser=(browser, profile)` / `cookiefile=path`. Never persist cookie bytes |
| Archive file | Do **not** pass yt-dlp `--download-archive`. Skip is SQLite `download_archive` in the service |
| Debug | yt-dlp warning and `ERROR:` lines always log with module `yt-dlp`; with `downloader.yt_dlp_debug` on, debug and info lines also log at DEBUG. The text is in the kept, redacted `detail` field, and the setting is read at each call: [§yt-dlp log detail (residual)](#ytdlp-log-detail-residual) (MEU-139) |

**Quality → format selector** (Local Canon §2):

| Preset | Selector |
|--------|----------|
| `Best` | `bestvideo+bestaudio/best` |
| `P2160` … `P144` | `bestvideo[height<=N]+bestaudio/best[height<=N]` |
| `Lowest` | `worstvideo+worstaudio/worst` |

Audio-only: map the nine `AudioFormat` values to yt-dlp format strings from [_downloader_pseudo_logic.md §6](../../_inspiration/_downloader_pseudo_logic.md) (Opus/AAC/MP3 rungs). Missing FFmpeg: adapter still runs extractors that do not need it; formats that need convert fail with `FFmpegNotFoundError` after the download step if the service asks `MediaPort`.

### SABR

| Path | Behavior |
|------|----------|
| Passive | Custom yt-dlp logger matches each line against the phrases of [§SABR check result (residual)](#sabr-check-result-residual) (MEU-138). Set Phase 1 `DownloadResult.sabr_detected=True`. Do not write a DB row |
| `check_sabr_status()` | Test extract on a known public video; return `SABRStatus(mode, source=Detected, checked_at)` |
| Force / Clear | **Not adapter methods.** Session state on `DownloadService` |

SABR-mode client fallback: set `extractor_args` client order that avoids blocked clients ([_downloader_pseudo_logic.md §3](../../_inspiration/_downloader_pseudo_logic.md)). Cookie mode further restricts viable clients. A fixed client list goes stale as YouTube changes: [§YouTube client fallback (residual)](#youtube-client-fallback-residual) (MEU-140).

### Cookie test

Implements Phase 1 `YouTubePort.test_cookies` → `CookieTestResult` (`ok`, `error_message`) **only**. “Close browser first” / browser locked / bad file → `{ ok: false, error_message }`. Do **not** raise `CookieTestError` from `test_cookies` (that type is for download-path cookie failures). No cookie material in the return value.

---

## Transcript adapter (`transcript/adapter.py`)

Implements `TranscriptPort`. Library: `youtube_transcript_api`.

| Step | Rule |
|------|------|
| Languages | Try `languages` in order, then `en`, then any available (inspiration §2) |
| Success | `TranscriptResult(video_id, title, text, language)` — `title` may be empty; service fills from yt-dlp if needed |
| No / disabled | `None` (skip) |
| Retryable | `TranscriptRetryableError` |
| Text | Join segments with newlines. **Do not write files** in the adapter |

File write (`raw/{id}.md` + YAML frontmatter) is Phase 3 + `filesystem/writer.py`. Adapter stays a fetch port.

Rate limits (`delay_between_requests`, batch pause) are **service** concerns, not adapter sleeps inside `get_transcript` (one call = one video).

---

## TTS adapter (`tts/adapter.py`)

Implements `TTSPort`. Library: `kokoro.KPipeline`.

| Method | Rule |
|--------|------|
| `load_model` | Resolve `DeviceType.Auto` → CUDA, else MPS, else CPU. Load the variant file at `ModelVariant.path`. One loaded model at a time; loading another implies unload |
| `unload_model` | Release weights; `get_model_status().is_loaded` is False |
| `generate` | `lang_code` = first character of `voice.voice_id`. `on_progress(segment_index, segment_total)`. Return `np.ndarray` (PCM). Do not write files |
| `list_voices` | Static catalog from [_kokoro_production_settings.md §1](../../_inspiration/_kokoro_production_settings.md) (54 voices). No DB table |
| `get_model_status` | In-memory: variant id, device, `memory_bytes` if cheap to read, `is_loaded` |

Wrong `lang_code` is a programming error (voice prefix rule). Adapter derives it; callers do not pass a raw lang code.

WAV/MP3 encode is `MediaPort`, not Kokoro.

---

## Media adapter (`media/adapter.py`)

Implements `MediaPort`. FFmpeg **subprocess** (not a Python bind). Phase 2: no `ConversionJob` table. **Phase 8** adds `conversion_jobs` and `encode`/`cut`/`extract_stream`/`detect_gpu` ([08-video-conversion.md](08-video-conversion.md)); `convert()` for TTS/download stays as specified here.

| Method | Rule |
|--------|------|
| `is_available` | Resolve on every use; no cache (Session 33 plan D-16). Order **locked** with Phase 7: (1) setting `downloader.ffmpeg_path` if set and the file exists, (2) bundled `{install}/resources/ffmpeg/ffmpeg.exe`, (3) `PATH` |
| `convert` | TTS default: 80 kbps, 44.1 kHz, mono MP3 ([_shared_patterns.md §4](../../_inspiration/_shared_patterns.md)). Download audio extract uses `ConvertOptions` from the chosen `AudioFormat` |
| `probe` | `MediaInfo`: duration, container, video/audio codec, sample rate, channels |

Raise `FFmpegNotFoundError` when the binary is missing. Do not swallow.

`MediaPort.ffmpeg_version()` and `YouTubePort.ytdlp_version()` are Phase 1 methods. Health calls those — do not add a parallel helper that is not on the port.

---

## Model manager (`model_manager/manager.py`)

Implements Phase 1 `ModelCatalogPort`. Phase 3 `ModelService` uses this port + `ModelRepository`.

| Action | Rule |
|--------|------|
| Catalog | The four seeded `ModelVariant` ids |
| Download | `huggingface_hub.hf_hub_download` (or snapshot) for that variant’s repo/file. `on_progress(fraction)` **in memory only** |
| Success | `models.mark_downloaded(id, path, size_bytes)` |
| Sideload | If user dropped a `.pth` / `.onnx` in `tts.models_directory`, detect and mark downloaded ([_tts_pseudo_logic.md](../../_inspiration/_tts_pseudo_logic.md)) |
| Offline | If file already at `path`, skip network |
| Failure | `ModelDownloadError`; leave `is_downloaded=False` |

Default dest: `~/.avkit/models/` (setting `tts.models_directory`). Voices may still land in the HF hub cache; that is Hugging Face’s layout, not extra SQLite rows.

---

## Filesystem adapter (`filesystem/writer.py`)

Implements Phase 1 `FilesystemPort`. Services must not open files ad hoc or import `soundfile`.

| Function | Rule |
|----------|------|
| `write_text_atomic(path, text)` | Write temp + replace. Used for `raw/{id}.md` |
| `write_progress_export(output_dir, video_ids_done)` | Optional `progress.json` **export**. Never used as resume input when `transcript_items` exist ([Phase 1 conflict](01-domain-layer.md#spec-conflict-progressjson)) |
| `ensure_channel_dirs(output_dir)` | `raw/`, `compiled/` |
| `write_audio_wav(path, samples, sample_rate)` | PCM → WAV. TTSService must use this, not `soundfile` |
| `read_text(path, max_bytes)` | **Compile only** (`raw/*.md` / `compiled/*.md` under a channel `output_dir`). Reject oversize. Never used for TTS file-load |

Zip compile stays Phase 3 (stdlib `zipfile`); no extra infra service required.

---

## What this layer must not do

| Forbidden | Why |
|-----------|-----|
| Persist `QueueRuntime` or `SABRStatus` | Session only (Phase 1) |
| Persist `is_loaded` / `device` | `ModelStatus` is runtime |
| Unified `jobs` table or STI | Three unlike workers |
| Store `TranscriptResult.text` | File only |
| yt-dlp `--download-archive` file as SoT | `download_archive` table |
| Read `progress.json` to resume | `transcript_items` |
| Embed cookies / tokens in rows or logs | Settings store mode + path only |
| Rate-limit inside `get_transcript` | Service loop |
| Invent `ModelFetchJob` | Port/service calls |
| Invent `ConversionJob` **in Phase 2 MEUs** | Convert-page jobs are Phase 8 (`conversion_jobs`) |
| Invent `CaptureShot` **in Phase 2 MEUs** | Capture inbox rows are Phase 9 (`capture_shots`) |
| Copy inspiration GUI code | Intent docs only; write adapters fresh |

---

## Logging

`structlog` with a module key: `youtube`, `transcript`, `tts`, `media`, `model_manager`, `yt-dlp`, `convert`, `capture`. Correlation ID from contextvars when the API sets it (Phase 4). No `print`, no `console.log`.

---

## Downstream planning notes

| Phase | Must follow this spec |
|-------|------------------------|
| **3 Services** | Open a UoW per command. Archive lookup before download; `add` archive on `Done`. Sequential queue + in-memory `QueueRuntime`. Compile/zip after items. Model download → manager + `mark_downloaded`. Do not hold a session across a long yt-dlp call without committing progress updates on a schedule |
| **4 REST** | Health dependencies = `MediaPort.is_available` + yt-dlp version helper. Settings namespace query uses leaf keys |
| **5 MCP** | REST only — this process is the sole SQLite owner |
| **6 GUI** | Poll job rows; format `speed_bps` / `eta_seconds` in the API. Test Cookies uses `YouTubePort.test_cookies` |
| **7 Dist** | FFmpeg probe order above; do not bundle Kokoro weights |

Phase 1 already defines `test_cookies`, `sabr_detected`, `FilesystemPort`, `ModelCatalogPort`, version helpers, and `domain/errors`. Implement those contracts; do not invent a second port set.

---

## Testing (Phase 2)

| Kind | What |
|------|------|
| DB integration | `tmp_path` SQLite: CRUD, cascade delete items, `delete_all` leaves archive, unique archive key, settings namespace |
| Mapper | Enum / Path / preview truncation |
| YouTube adapter | Mock `yt_dlp.YoutubeDL`; assert format selector, cookie opts, SABR log strings, cancel hook |
| Transcript adapter | Mock API; language fallback; `None` vs retryable |
| Media adapter | Missing binary → `FFmpegNotFoundError`; skip live FFmpeg unless marked integration |
| Model manager | Mock `hf_hub_download`; sideload existing file |

Do not hit live YouTube or Hugging Face in the default suite.

---

## Residuals registered 2026-11-10

> Registered 2026-11-10 from the download comparison with P:/yt-dlp_GUI ([report](../proposals/2026-11-10-download-logic-divergence-report.md)) and the known issues filed from it (triage D-529 to D-534). Grouping: [`2026-11-10-download-reliability-session-grouping.md`](../../.agent/context/grouping/2026-11-10-download-reliability-session-grouping.md), D-535 to D-543.

<a id="sabr-check-result-residual"></a>

### SABR check result (residual)

> **MEU-138.** From `SABR-CHECK-MISSES-CURRENT-MESSAGES`. `check_sabr_status` (`youtube/adapter.py:555-561`) and the passive scan (`_YtDlpLogger._scan`, `:315-340`) match only the three phrases in [§SABR](#sabr), and yt-dlp 2026.10.26 says none of them. On 2026-11-10 the check returned Inactive while yt-dlp printed "Some android client https formats have been skipped as they are missing a URL … SABR-only streaming experiment". The page hides an Inactive result (`DownloaderPage.tsx:664`), and nothing on the path logs.

| Rule | Contract | Source |
|------|----------|--------|
| Phrases | The passive scan and the check match `forcing sabr`, `missing a url`, `require a gvs po token` and `sabr` as whole words, case-insensitively: `sabr` matches "SABR-only" but not "Sabrina", and a line about PO Tokens alone doesn't match. This covers the three old phrases. The set lives in one constant both paths use. | Human-approved: D-623, D-624 (Mat, 2026-11-11); Local Canon: P:/yt-dlp_GUI `detect_sabr_mode` (`youtube_downloader.py:3717`); measured 2026-11-10; grouping D-541; D-629 |
| Shown | The Downloader page states the result of every check, Active or Inactive, with its `checked_at` time; a failed check states its error. | Local Canon: grouping D-541 |
| Log | Check, Force and Clear each log one line with the result (`download.sabr_check`, `download.sabr_force`, `download.sabr_clear`), with the matched phrase in a kept field. | Local Canon: MEU-115's one-line-per-outcome rule; grouping D-541 |
| Spec | [§SABR](#sabr) Passive and [06 §SABR detection sources](06-gui.md) name this section instead of the old phrases. | Local Canon |
| Tests | Unit: each phrase, case, and a line with none; a captured 2026.10.26 warning line is Active. Renderer: Inactive and Active both shown with a time. Route: each SABR action logs once. No live YouTube. | Local Canon |

> **Delivered (Session 65).**
> - `SABR_PHRASES` (`youtube/adapter.py:93`) holds `forcing sabr`, `missing a url`, `require a gvs po token` and `sabr`, and `sabr_phrase` (`:347`) returns the first one found as a whole word in the case-folded line, or `None`. `SABR_LOG_NEEDLES` is gone (`SABR_MATCH`, D-623, D-624). A failure whose text holds a phrase is `refused` (AC-138.2).
> - `_YtDlpLogger` (`:386`) scans every line it gets: the first line with a phrase sets `matched_phrase`, which never changes after, and `sabr_detected` is a read-only property (`SABR_SCAN`). `check_sabr_status` (`:661`) returns the phrase on Active, and `SABRStatus.matched_phrase` (01 §`SABRStatus`) keeps it; it is not on the wire (`SABR_STATUS_PHRASE`, `SABR_RESULT`, D-626).
> - `check_sabr`, `force_sabr` and `clear_sabr` (`services/download.py:413`, `:440`, `:450`) each log one line: `download.sabr_check` with `Active, matched '<phrase>'` or `Inactive, no phrase matched`, or at ERROR with the cleaned error before it is re-raised; `download.sabr_force` `Active, forced`; `download.sabr_clear` `Inactive, cleared` (`SABR_LOG`). The phrase comes from `SABR_PHRASES`, never from yt-dlp's text.
> - `sabrResultText` (`sabr-panel.ts:21`) gives the panel's text for checking, Active, Inactive and not checked, with the local time of the check, force or clear; the `sabr-status` panel is no longer hidden (`SABR_SHOWN`, D-635).
> - AC-138.1 to AC-138.8. Plan `docs/execution/plans/2026-11-11-download-failure-visibility/`.

<a id="ytdlp-log-detail-residual"></a>

### yt-dlp log detail (residual)

> **MEU-139.** From `YTDLP-LOG-TEXT-DROPPED`. `_YtDlpLogger` logs only when `downloader.yt_dlp_debug` is on and puts the text in `message`, which `CONSOLE_FIELDS` (`services/health.py:47-62`) drops. The setting has no control and is read once at startup (`api/wiring.py:149`).

| Rule | Contract | Source |
|------|----------|--------|
| Warnings and errors | yt-dlp warning and error lines always log at WARNING and ERROR, with the text in the kept `detail` field, whatever the debug setting. | Local Canon: [§Logging](#logging); grouping D-543 |
| Debug lines | With `downloader.yt_dlp_debug` on, info and debug lines also log at DEBUG with the text in `detail`. | Spec: [§download](#downloadurl-options) Debug row; grouping D-543 |
| Redaction | The kept text goes through the Console redaction Session 50 set up (D-247): one line, home folder as `~`, cookie values never kept. | Local Canon: 03 [§Transcript failure reason](03-service-layer.md#transcript-failure-reason-residual) Console fields row |
| Live | The adapter reads the setting per download and per check, so a change applies without a restart, as `LIVE_SOURCE` does for ffmpeg. | Local Canon: `api/wiring.py:151` |
| Control | Settings → Downloader's existing "yt-dlp debug" switch (leaf `yt_dlp_debug`, `SettingsPage.tsx:724-733`) controls the setting. | Local Canon: grouping D-543; D-630 |
| Tests | Unit: a warning logs with `detail` when debug is off; a debug line logs only when on; a line holding a home path and a cookie-looking value is redacted. Renderer: the switch saves the setting. | Local Canon |

> **Delivered (Session 65).**
> - `_YtDlpLogger` (`youtube/adapter.py:386`) logs event `yt-dlp` with module `yt-dlp` and the text only in `detail`, after `scrub_line` (03 §Download failure reason): a warning at WARNING and an `ERROR:` line at ERROR always; debug, info and an error line without the prefix at DEBUG only when debug is on (D-632). A line that cleans to nothing logs nothing, and there is no `message` field (`YTDLP_LINE`).
> - `YouTubeAdapter` takes `yt_dlp_debug: Callable[[], bool] | None`. `_debug_now` (`:453`) reads it once per public call (download, extract, listing, SABR check, cookie test); no source, a raising source and any answer but `True` read as off. `_base_opts` (`:500`) sets `quiet` and `verbose` from the logger. `api/wiring.py:159` passes a `# LIVE_SOURCE` lambda over the setting, so a `PUT /settings` applies to the next call with no restart (`YTDLP_LIVE`).
> - The control is Settings → Downloader's existing "yt-dlp debug" switch (D-630).
> - AC-139.1 to AC-139.9, and AC-122.16 now checks that with debug off a title reaches no Console line. Plan `docs/execution/plans/2026-11-11-download-failure-visibility/`.

<a id="youtube-client-fallback-residual"></a>

### YouTube client fallback (residual)

> **MEU-140.** From `DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT`. `_cookie_opts` (`youtube/adapter.py:412-435`) pins `tv`, `web_safari`, `web` with cookies and `android`, `tv`, `ios` with hls/dash skipped without them. On 2026-11-10 gKcOjnDJfzk failed on the pin and extracted with yt-dlp's own client choice; only `visionos` worked alone. The video selector has no catch-all, and the add-time extract uses none of the download's cookie or client options.

| Rule | Contract | Source |
|------|----------|--------|
| Client choice | Per grouping D-539 (ruled A, 2026-11-10): the first attempt sets no `player_client` in either cookie mode, so yt-dlp picks its own clients; on a client-side error (reload page, no formats, SABR-only, requested format not available) it retries once with today's cookie pin (`tv`, `web_safari`, `web`), and both attempts log. | Human-approved: grouping D-539 (Mat, 2026-11-10) |
| Catch-all | The video selector ends with `/best`, so a video with formats but none at the height still downloads, and the received height (MEU-124) shows the difference. | Local Canon: P:/yt-dlp_GUI selector ends in `/worst` (`youtube_downloader.py:1029-1044`); grouping D-539 |
| Add-time check | The add-time extract uses the same cookie and client options as the download. | Local Canon: report R7 |
| Tests | Unit with a mocked `YoutubeDL`: the retry runs once and only on the listed errors; a cancel or cookie error never retries; both attempts log. A recorded live probe on one video is a manual check, not part of the suite. | Local Canon |

<a id="ytdlp-js-runtime-residual"></a>

### yt-dlp JS runtime (residual)

> **MEU-141.** From `YTDLP-NO-JS-RUNTIME`. av-kit sets no `js_runtimes`, deno is not on PATH, the `.venv` has no `yt_dlp_ejs`, and `packaging/avkit-backend.spec` collects no solver script, so every extract runs on yt-dlp's JS-less path.

| Rule | Contract | Source |
|------|----------|--------|
| Runtime | Per grouping D-540 (ruled A, 2026-11-10): ship `deno.exe` in the Windows installer and resolve it as ffmpeg is resolved (the setting, then the bundled file, then PATH), passing it through `js_runtimes`; the plan measures its size against the installer budget, and Deno's MIT notice goes in `LICENSES.txt`. | Human-approved: grouping D-540 (Mat, 2026-11-10) |
| Solver | The dependency is `yt-dlp[default]`, so the `yt-dlp-ejs` version yt-dlp pins comes with it, and its scripts are collected into the packaged backend. | Research-backed: yt-dlp EJS wiki (github.com/yt-dlp/yt-dlp/wiki/EJS) |
| Health | The Health page names the runtime in use, or says none was found and what that costs. | Local Canon: 02 [§Logging](#logging), Health dependency rows |
| Tests | Unit: runtime lookup order and the none-found result; a packaged smoke that the solver module imports in the onedir. | Local Canon |

---

## Validation commands

Registered exact-receipt forms live in [`.agent/docs/commands.md`](../../.agent/docs/commands.md). Targeted:

```bash
uv run pytest tests/integration/ -x --tb=short -v
uv run pyright packages/infrastructure/
uv run ruff check packages/infrastructure/
```
