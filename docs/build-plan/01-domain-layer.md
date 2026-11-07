# Phase 1 — Domain Layer

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: [Phase 0](00-overview.md) | Outputs: [Phase 2](02-infrastructure.md), [Phase 3](03-service-layer.md)

---

## Goal

Define the vocabulary every later phase uses: persistable jobs, catalogs, settings, value objects, enums, and port protocols. The domain has **zero** infrastructure imports. SQLite (Phase 2) maps these types; it does not invent a second model.

av-kit is a **job queue**, not a media library. The database stores **work records and file pointers**. Transcript bodies, audio samples, and video bytes live on disk. The GUI already treats outputs as files (`Open File` / `Open Folder` / `Open ZIP`).

| Source | Decision |
|--------|----------|
| Spec | [Phase 6 GUI](06-gui.md) queue tables, status machines, settings keys |
| Local Canon | [DESIGN_PROPOSAL.md §5](../../_inspiration/DESIGN_PROPOSAL.md), [APPLICATION_PURPOSE.md §5](../../_inspiration/APPLICATION_PURPOSE.md) (SQLite = settings, job queue, history) |
| Research-backed | MediaConvert job + output paths; InvokeAI `DownloadJob(source, destination, status)`; yt-dlp `--download-archive` as an ID skip-set; GitLab: do not design new single-table inheritance |
| Human-approved | 2026-08-18 peer review of the job-kernel proposal: keep three typed jobs; add `TranscriptItem` + `DownloadArchiveEntry`; do not add a shared `Operation` / locator algebra |

This file **supersedes** the entity field lists in [Phase 0](00-overview.md) and DESIGN_PROPOSAL §5 wherever they disagree. Phase 0 enums still apply; Phase 0 field columns are a summary only.

---

## Persistence rules

### Store in SQLite

| Kind | Objects |
|------|---------|
| Typed jobs | `DownloadJob`, `TranscriptJob`, `TTSJob` |
| Child work rows | `TranscriptItem` (not a job; not independently queued) |
| Catalogs | `DownloadArchiveEntry`, `ModelVariant` |
| Config | `Setting` |

### Do not store in SQLite

| Thing | Where it lives | Why |
|-------|----------------|-----|
| Transcript text, audio PCM, video bytes | Files under the job destination | Job row holds `path` only |
| `progress.json` as source of truth | Optional **write-through export** under the channel folder | Resume is `TranscriptItem` rows. See [Spec conflict](#spec-conflict-progressjson) |
| Console log lines | `{app_data}/logs/console.log` | Errors (`PERSIST_LEVELS`) and lines flagged `persist=True` always; every other line only with the `app.log_to_file` toggle |
| Window geometry, rail, console height | electron-store | UI persist, not domain |
| Cookie contents, Bearer tokens | Never | Jobs may record cookie *mode* via settings, not secrets |
| `POST /tts/prepare` preview | Stateless response | Not a job |
| Queue processor `Idle/Processing/Paused` | In-memory `QueueRuntime` on the service | Restart → processor `Idle`; item statuses survive |
| SABR restricted / checking / forced | In-memory `SABRStatus` on `DownloadService` | Session control unless a later setting is added |
| `ModelVariant.is_loaded` / `device` | Runtime `ModelStatus` from `TTSPort` | Process death drops VRAM residency |
| Full pasted TTS body | Editor draft = `tts.input_text` setting; job stores hash + preview | See `TTSJob` |
| A generic `jobs` or `job_artifacts` table | — | Three unlike workers; known output shapes |
| `ModelFetchJob` | — | Model download is a port/service call + `ModelDownloadRuntime` |
| `ConversionJob` (before Phase 8) | — | **Superseded 2026-08-24.** TTS/download `MediaPort.convert` still must not create conversion rows. Convert-page queue **does** persist `ConversionJob` — [08-video-conversion.md](08-video-conversion.md) |
| Shared `Operation` / `SourceLocator` / `DestinationLocator` kernel | — | Over-built for three module-shaped pages |

### Unlike workers, not one table

GUI, REST, and MCP are module-shaped. Status machines differ. Do **not** collapse `DownloadJob` / `TranscriptJob` / `TTSJob` / `ConversionJob` / `CaptureShot` into one discriminator table. “Unified queue” in APPLICATION_PURPOSE means shared UX (start / pause / resume) where a queue exists, not one SQL table. `ConversionJob` is Phase 8 ([08-video-conversion.md](08-video-conversion.md)). `CaptureShot` is Phase 9 ([09-screenshot-capture.md](09-screenshot-capture.md)) and is **not** a queue job.

---

## Package layout

```
packages/core/src/avkit_core/
├── domain/
│   ├── download.py      # DownloadJob, DownloadArchiveEntry, VideoInfo, PlaylistInfo, …
│   ├── transcript.py    # TranscriptJob, TranscriptItem, ChannelInfo, TranscriptResult
│   ├── tts.py           # TTSJob, ModelVariant, VoiceConfig, ModelStatus
│   ├── settings.py      # Setting
│   ├── progress.py      # ProgressSnapshot, ErrorInfo (shared VOs, not tables)
│   ├── queue.py         # QueueProcessorState, QueueRuntime (session, not tables)
│   └── enums.py
└── ports/
    ├── youtube.py
    ├── transcript.py
    ├── tts.py
    ├── media.py
    ├── filesystem.py
    ├── models.py
    └── storage.py
```

---

## Enums (`domain/enums.py`)

Values match [Phase 0](00-overview.md) unless this section adds a member.

| Enum | Values | Notes |
|------|--------|-------|
| `DownloadStatus` | `Pending`, `Downloading`, `Done`, `Failed`, `Skipped`, `QualityBlocked`, `AgeRestricted`, `Cancelled` | No `Paused`. Pause is `QueueProcessorState`. |
| `TranscriptStatus` | `Pending`, `Processing`, `Done`, `Failed`, `Paused`, `Cancelled` | `Paused` is the durable **channel** badge when the processor paused mid-batch. Not workflow “waiting-children”. |
| `TranscriptItemStatus` | `Pending`, `Done`, `Skipped`, `Failed` | Child row only. No `Paused`, no `queue_position`. |
| `TTSStatus` | `Pending`, `Generating`, `Done`, `Failed`, `Cancelled` | |
| `TTSSourceKind` | `Inline`, `File` | Paste vs Load File |
| `QueueProcessorState` | `Idle`, `Processing`, `Paused` | Session only. One instance per module queue (download, transcript). |
| `MediaFormat` | `MP4`, `WEBM`, `MP3`, `M4A`, `WAV`, `OPUS` | Container / encode target |
| `QualityPreset` | `Best`, `P2160`, `P1440`, `P1080`, `P720`, `P480`, `P360`, `P240`, `P144`, `Lowest` | GUI quality dropdown |
| `AudioFormat` | `Default`, `Best`, `Lowest`, `LowWebm`, `MediumWebm`, `StandardWebm`, `StandardM4a`, `StandardMp3`, `HighM4a` | GUI audio-only dropdown. SABR restricts to `StandardMp3`, `HighM4a`. |
| `DeviceType` | `Auto`, `CUDA`, `MPS`, `CPU` | Load argument only; not a `ModelVariant` column |
| `ModelFormat` | `PyTorch`, `ONNX` | |
| `ModelPrecision` | `FP32`, `FP16`, `INT8` | |
| `SABRMode` | `Inactive`, `Active`, `Checking` | Session VO |
| `SABRSource` | `Detected`, `Forced` | How Active was set |
| `SettingValueType` | `String`, `Number`, `Boolean`, `Json` | |

Do **not** add a domain `Operation` enum (`DOWNLOAD`, `COMPILE_MARKDOWN`, …). Those names are service methods and port calls.

---

## Shared value objects (not tables)

### `ProgressSnapshot`

Read/API DTO for polling. Jobs may expose the same numbers as fields; this type is for a uniform poll shape, not a table.

| Field | Type | Notes |
|-------|------|-------|
| `fraction` | `float` | 0.0–1.0 |
| `units_done` | `int` | Bytes, videos, or segments |
| `units_total` | `int \| None` | Unknown until probe / resolve |
| `unit_label` | `str` | `"bytes"` \| `"videos"` \| `"segments"` |
| `rate` | `float \| None` | bytes/s or items/s |
| `eta_seconds` | `int \| None` | |
| `error` | `ErrorInfo \| None` | |

### `ErrorInfo`

| Field | Type |
|-------|------|
| `message` | `str` |
| `code` | `str \| None` |

### `SABRStatus`

Held on `DownloadService`, not persisted.

| Field | Type |
|-------|------|
| `mode` | `SABRMode` |
| `source` | `SABRSource \| None` | Set when `Active` |
| `checked_at` | `datetime \| None` |

### `QueueRuntime`

In-memory per module. **Not** a SQLite row. Restart leaves it `Idle` until Start.

| Field | Type |
|-------|------|
| `queue_name` | `str` | `"downloads"` \| `"transcripts"` |
| `state` | `QueueProcessorState` |
| `current_job_id` | `str \| None` |

If a later phase needs “resume paused across restart”, add a **setting** (e.g. `downloader.processor_paused`). Do not add a `queue_runtime` table in Phase 1–2.

---

## Persistable entities

### `DownloadJob` — `domain/download.py`

One row per video in the downloader queue. Playlist / channel paste **explodes into N jobs** at add-time. No `parent_id` until the GUI groups by playlist.

| Field | Type | Persist | Source |
|-------|------|---------|--------|
| `id` | `str` (UUID) | yes | Spec |
| `url` | `str` | yes | Spec |
| `video_id` | `str` | yes | Spec |
| `title` | `str` | yes | Spec |
| `quality` | `QualityPreset` | yes | Spec |
| `audio_only` | `bool` | yes | Spec — this **is** extract-audio; not a separate job type |
| `audio_format` | `AudioFormat` | yes | Spec |
| `status` | `DownloadStatus` | yes | Spec |
| `progress` | `float` | yes | 0.0–1.0 |
| `speed_bps` | `float \| None` | yes | Spec (GUI formats as `"12.3 MB/s"`) |
| `eta_seconds` | `int \| None` | yes | Spec (GUI formats as `"2:30"`) |
| `file_size` | `int \| None` | yes | bytes |
| `file_path` | `Path \| None` | yes | destination pointer |
| `error_message` | `str \| None` | yes | Spec (omitted from original Phase 1 stub) |
| `queue_position` | `int` | yes | Reorder persist |
| `created_at` | `datetime` | yes | |
| `updated_at` | `datetime` | yes | |

**Invariants**

- `Paused` is never a `status`. Processor pause does not rewrite item rows except the in-flight item completing to `Done` or `Failed`.
- `Skipped` is set when `DownloadArchiveEntry` already has this `video_id` and `downloader.archive_tracking` is on.
- SABR Active: incompatible quality/audio → `QualityBlocked`. Clearing SABR resets those rows to `Pending`.
- Reset: `Failed` → `Pending` (and clear `error_message`, `progress`).
- Clear All deletes queue rows only. It must **not** delete `DownloadArchiveEntry` rows.

**Per-item state machine** (Spec — [06-gui.md](06-gui.md)):

```
Pending ──→ Downloading ──→ Done
                │              ↑
                ├──→ Failed ───┘ (via Reset)
                ├──→ Cancelled
                ├──→ Skipped (duplicate/archive)
                ├──→ QualityBlocked (SABR)
                └──→ AgeRestricted
```

#### Download value objects / port DTOs (not tables)

| Type | Fields | Notes |
|------|--------|-------|
| `VideoInfo` | `video_id`, `title`, `duration`, `formats: list[FormatInfo]` | `YouTubePort.extract_info` |
| `PlaylistInfo` | `playlist_id`, `title`, `video_ids` | Flat extract; service inserts N jobs |
| `ListedVideo` | `video_id`, `title` (single-spaced text without controls or lone surrogates, or `None`) | One entry of the flat enumeration (Session 53 MEU-122, `TEXT_CLEAN`) |
| `VideoListing` | `videos: tuple[ListedVideo, ...]`, `channel_name` (as `title`, or `None`) | `YouTubePort.extract_video_ids`; no `video_id` repeats (`LISTING`) |
| `FormatInfo` | `format_id`, `ext`, `height`, `abr`, `vcodec`, `acodec` | |
| `DownloadOptions` | `quality`, `audio_only`, `audio_format`, `output_dir`, cookie fields as **paths/mode only** | Never embed cookie bytes |
| `DownloadResult` | `file_path`, `file_size`, `video_id`, `title` | |

---

### `DownloadArchiveEntry` — `domain/download.py`

Skip catalog. Not job history. Matches yt-dlp `--download-archive` (extractor + id). DESIGN_PROPOSAL §5 specified this table; the original Phase 1 stub omitted it.

| Field | Type | Persist | Source |
|-------|------|---------|--------|
| `extractor` | `str` | yes | Research-backed — yt-dlp archive line (`youtube`) |
| `video_id` | `str` | yes | Local Canon |
| `title` | `str \| None` | yes | Convenience for UI; not required to skip |
| `recorded_at` | `datetime` | yes | |

**Invariants**

- Unique `(extractor, video_id)`.
- Written when a download reaches `Done`.
- Looked up on add (and before start) to mark `Skipped`.
- Survives queue Clear All / Remove.

---

### `TranscriptJob` — `domain/transcript.py`

**Parent** channel batch. The GUI card is this row plus aggregates from `TranscriptItem`.

| Field | Type | Persist | Source |
|-------|------|---------|--------|
| `id` | `str` (UUID) | yes | Spec |
| `channel_url` | `str` | yes | Spec |
| `channel_name` | `str` | yes | Resolved on add |
| `status` | `TranscriptStatus` | yes | Includes `Paused` (channel badge) |
| `output_dir` | `Path` | yes | Channel folder root |
| `video_count` | `int` | yes | Denormalized: `COUNT(items)` after resolve |
| `word_count` | `int` | yes | Denormalized: sum of item `word_count` |
| `zip_path` | `Path \| None` | yes | Set when auto-zip completes |
| `queue_position` | `int` | yes | Channel reorder |
| `error_message` | `str \| None` | yes | Parent-level failure |
| `created_at` | `datetime` | yes | |
| `updated_at` | `datetime` | yes | |

**Dropped vs original stub:** `video_ids`, `processed_ids`, stored `progress` float. Live progress = `COUNT(items WHERE status=Done) / video_count`. Last-processed title = latest item `processed_at`. Batch N/M and ETA are **service-computed** from settings + remaining items, not columns.

**On-disk layout** (pointers only; files are not rows):

```
{output_dir}/
├── raw/{video_id}.md
├── compiled/{channel_name}_volN.md    # discover; do not persist a path list
├── progress.json                      # optional export; see conflict
└── {channel_name}_raw.zip             # zip_path
```

**Commands on this entity (Phase 3, not new job types)**

| Command | Effect |
|---------|--------|
| Resolve | `YouTubePort.extract_video_ids` → `VideoListing` → insert `TranscriptItem` rows, each with its listed title → set `video_count` |
| Compile | `POST /transcripts/{id}/compile` — write `compiled/*.md`; not a new job row |
| Zip | Automatic on channel `Done` — set `zip_path` |
| Pause / Resume / Stop | Session `QueueRuntime` + this job’s `status` (`Processing` ↔ `Paused`) |

Remove from queue does **not** delete files (Spec — GUI confirmation).

---

### `TranscriptItem` — `domain/transcript.py`

One **child record** per video. Replaces `progress.json` as the resume store. Not a child job: the GUI has no per-video queue, no per-item reorder, no per-item cancel. The parent loop walks items sequentially with rate limits.

| Field | Type | Persist | Source |
|-------|------|---------|--------|
| `id` | `str` (UUID) | yes | Human-approved |
| `job_id` | `str` | yes | FK to `TranscriptJob` |
| `video_id` | `str` | yes | Spec |
| `title` | `str \| None` | yes | Filled when known |
| `language` | `str \| None` | yes | Chosen transcript language |
| `word_count` | `int` | yes | 0 until `Done` |
| `path` | `Path \| None` | yes | `raw/{video_id}.md` pointer |
| `status` | `TranscriptItemStatus` | yes | |
| `error_message` | `str \| None` | yes | |
| `retry_count` | `int` | yes | Capped by `transcript.max_retries` |
| `processed_at` | `datetime \| None` | yes | Set on terminal status |

**Invariants**

- Unique `(job_id, video_id)`.
- `Done` requires `path` pointing at an existing write (service writes the file, then commits the row).
- `Skipped` = no transcript / disabled (inspiration errors), not a download-archive hit.
- Deleting the parent deletes items (cascade). Files on disk stay unless a later cleanup command exists (MVP: leave files).

#### Transcript value objects / port DTOs (not tables)

| Type | Fields | Notes |
|------|--------|-------|
| `ChannelInfo` | `channel_id`, `name`, `url`, `video_count` | Resolution DTO |
| `TranscriptResult` | `video_id`, `title`, `text`, `language` | **Port return only.** `text` is written to `{video_id}.md` and then discarded from memory. Never persist `text`. |

---

### `TTSJob` — `domain/tts.py`

One generation run. MVP is single text → single output ([06-gui.md](06-gui.md) deferred multi-file batch).

| Field | Type | Persist | Source |
|-------|------|---------|--------|
| `id` | `str` (UUID) | yes | Spec |
| `source_kind` | `TTSSourceKind` | yes | Human-approved |
| `source_path` | `Path \| None` | yes | Required when `File` |
| `text_hash` | `str` | yes | Identity of the run input |
| `text_preview` | `str` | yes | Short prefix only (cap in implementation, e.g. 200 chars) |
| `voice` | `str` | yes | `VoiceConfig.voice_id` |
| `speed` | `float` | yes | 0.5–2.0 |
| `format` | `MediaFormat` | yes | `MP3` or `WAV` |
| `status` | `TTSStatus` | yes | |
| `output_path` | `Path \| None` | yes | Destination pointer |
| `segments_total` | `int` | yes | |
| `segments_done` | `int` | yes | |
| `error_message` | `str \| None` | yes | |
| `created_at` | `datetime` | yes | |
| `updated_at` | `datetime` | yes | |

**Invariants**

- Do **not** persist full input text on this row. Generate still *receives* full text at the API (`POST /tts/generate`).
- Editor resume after restart is settings key `tts.input_text` (Spec). That is the draft, not the job.
- WAV→MP3 via `MediaPort.convert` is a **phase of this job**, not a `ConversionJob`.
- Cleanup preview (`POST /tts/prepare`) creates no row.

---

### `ModelVariant` — `domain/tts.py`

Asset catalog for Kokoro files. Not a job. Model download updates this row + in-memory percent; there is no `ModelFetchJob` and no install-queue page.

| Field | Type | Persist | Source |
|-------|------|---------|--------|
| `id` | `str` | yes | Stable variant id |
| `name` | `str` | yes | e.g. `ONNX FP16` |
| `format` | `ModelFormat` | yes | |
| `precision` | `ModelPrecision` | yes | |
| `size_bytes` | `int` | yes | Catalog / on-disk size |
| `path` | `Path \| None` | yes | Local file when downloaded |
| `is_downloaded` | `bool` | yes | |

**Dropped vs original stub:** durable `is_loaded`, `device`. Runtime truth is `ModelStatus` from `TTSPort.get_model_status()`. Optional later setting: `tts.autoload_last_variant_id`.

#### TTS value objects (not tables)

| Type | Fields | Notes |
|------|--------|-------|
| `VoiceConfig` | `voice_id`, `lang_code`, `language`, `gender`, `style_description` | Catalog; lang_code first letter must match voice prefix (Kokoro rule) |
| `ModelStatus` | `variant_id \| None`, `name`, `device`, `memory_bytes`, `is_loaded` | Session snapshot of the **loaded** model |
| `ModelDownloadRuntime` | `variant_id \| None`, `state` (`Idle`\|`Downloading`\|`Failed`), `fraction` (0–1), `error_message \| None` | Session only. One in-flight HF fetch. Restart → `Idle`. Not a `ModelFetchJob`. |

---

### `Setting` — `domain/settings.py`

| Field | Type | Persist |
|-------|------|---------|
| `namespace` | `str` | yes (`downloader`, `transcript`, `tts`, `app`, `ui`) |
| `key` | `str` | yes (**leaf only** — `quality`, never `downloader.quality`. Logical `namespace.leaf` is documentation.) |
| `value` | `str` | yes (serialized) |
| `value_type` | `SettingValueType` | yes |
| `updated_at` | `datetime` | yes |

Canonical key list lives in [06-gui.md Settings](06-gui.md). Domain does not duplicate every default here; services validate against that table.

---

## Relationships

```
DownloadJob ──────── (lookup) ──► DownloadArchiveEntry   (extractor + video_id)
TranscriptJob 1 ───◄ N TranscriptItem
TTSJob  (no children in MVP)
ModelVariant  (catalog; TTSJob.voice / load target are ids, not FKs required)
Setting  (unrelated key/value)
```

Aggregates for persistence:

| Aggregate root | Children | Delete behavior |
|----------------|----------|-----------------|
| `DownloadJob` | none | Remove row; files stay; archive stays |
| `TranscriptJob` | `TranscriptItem` | Cascade items; files stay |
| `TTSJob` | none | Remove row; output file stays |

---

## Spec conflict: `progress.json`

| Location | What it says |
|----------|----------------|
| This file | `TranscriptItem` is source of truth for resume |
| Golden Rule 4 ([00-overview.md](00-overview.md)) | Durable app state in SQLite, not JSON |
| Inspiration `_transcript_pseudo_logic.md` | Per-channel `progress.json` |
| [06-gui.md](06-gui.md) card field, output tree, exit criterion ~line 1112 | Still requires `progress.json` |

**Resolution for implementation planning**

1. Phase 1–3 implement SQLite `TranscriptItem` as the only read path for resume.
2. Phase 2/3 **may** write `progress.json` as a derived export (processed video IDs) for folder portability.
3. Never read `progress.json` back when the job already has item rows.
4. **Phase 6 must amend** the card source (“Derived from `progress.json`”), the output-tree comment, and the exit criterion in the same change that wires the transcript page — or keep the export file and describe it as export-only.

Do not leave both as competing sources of truth.

---

## Port protocols

Ports stay IO-shaped. They return DTOs, not persisted graphs. **This section is the canonical port set.** Phase 2 implements these protocols; Phase 3 must not invent extra ports or fall back to direct `open` / `soundfile` / `huggingface_hub` imports.

#### `ports/youtube.py`

```python
class YouTubePort(Protocol):
    def extract_info(self, url: str, flat: bool = False) -> VideoInfo | PlaylistInfo: ...
    def extract_video_ids(self, channel_url: str) -> VideoListing: ...
    def download(self, url: str, options: DownloadOptions) -> DownloadResult: ...
    def get_formats(self, video_id: str) -> list[FormatInfo]: ...
    def check_sabr_status(self) -> SABRStatus: ...
    def test_cookies(self, mode: str, browser: str | None, profile: str | None, cookie_file: Path | None) -> CookieTestResult: ...
    def ytdlp_version(self) -> str | None: ...
```

`DownloadResult` includes `sabr_detected: bool` (adapter observed SABR in this extract/download). `CookieTestResult` is `{ ok: bool, error_message: str | None }` — never cookie bytes.

#### `ports/transcript.py`

```python
class TranscriptPort(Protocol):
    def get_transcript(self, video_id: str, languages: list[str]) -> TranscriptResult | None: ...
```

`None` means no transcript (service maps to `TranscriptItemStatus.Skipped`). Adapter raises typed domain errors for retryable failures (Phase 2).

#### `ports/tts.py`

```python
class TTSPort(Protocol):
    def load_model(self, variant: ModelVariant, device: DeviceType) -> None: ...
    def unload_model(self) -> None: ...
    def generate(self, text: str, voice: VoiceConfig, speed: float, on_progress: Callable) -> np.ndarray: ...
    def list_voices(self) -> list[VoiceConfig]: ...
    def get_model_status(self) -> ModelStatus: ...
```

`generate` returns samples; the service writes the file via `FilesystemPort.write_audio_wav` and optionally calls `MediaPort.convert`. The array is not persisted. Services must not import `soundfile`.

#### `ports/media.py`

```python
class MediaPort(Protocol):
    def is_available(self) -> bool: ...
    def ffmpeg_version(self) -> str | None: ...
    def convert(self, input_path: Path, output_path: Path, options: ConvertOptions) -> None: ...
    def probe(self, file_path: Path) -> MediaInfo: ...
```

`ConvertOptions` / `MediaInfo` are media DTOs (`codec`, `duration`, `sample_rate`, …). Used inside download audio extract and TTS encode. **Phase 8** extends `MediaInfo` with optional video/stream fields and adds `encode` / `cut` / `extract_stream` / `detect_gpu` on this port without changing `convert()`. Convert-page work uses `ConversionJob` ([08-video-conversion.md](08-video-conversion.md)).

FFmpeg probe order is locked in [07-distribution.md](07-distribution.md): setting `downloader.ffmpeg_path` → bundled binary → `PATH`.

#### `ports/filesystem.py`

```python
class FilesystemPort(Protocol):
    def write_text_atomic(self, path: Path, text: str) -> None: ...
    def write_progress_export(self, output_dir: Path, video_ids_done: list[str]) -> None: ...
    def ensure_channel_dirs(self, output_dir: Path) -> None: ...
    def write_audio_wav(self, path: Path, samples: np.ndarray, sample_rate: int) -> None: ...
    def read_text(self, path: Path, *, max_bytes: int) -> str: ...
```

`read_text` is for **compile only** (existing `raw/*.md` / `compiled/*.md` under a channel `output_dir`). `max_bytes` is mandatory. TTS file-load is **Electron IPC** ([06-gui.md](06-gui.md)); the API receives the resulting `text`. The service must not re-read `source_path`.

#### `ports/models.py`

```python
class ModelCatalogPort(Protocol):
    def download(self, variant: ModelVariant, dest_dir: Path, on_progress: Callable[[float], None]) -> Path: ...
    def sideload(self, models_dir: Path) -> list[ModelVariant]: ...
```

Progress callbacks are memory-only (`ModelDownloadRuntime`). No `ModelFetchJob`.

#### `ports/storage.py`

```python
class UnitOfWork(Protocol):
    downloads: DownloadRepository
    archive: ArchiveRepository
    transcripts: TranscriptRepository  # jobs + items (same aggregate)
    tts_jobs: TTSJobRepository
    settings: SettingsRepository
    models: ModelRepository
    def __enter__(self) -> Self: ...
    def __exit__(self, ...) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

**Repository method contracts** (Phase 2 implements; names may tighten but the capabilities must exist):

| Repository | Must support |
|------------|----------------|
| `DownloadRepository` | add, get, list ordered by `queue_position`, update status/progress, reorder, delete, delete_all, reset_failed |
| `ArchiveRepository` | get `(extractor, video_id)`, add on Done, list (optional) |
| `TranscriptRepository` | add/get/list/reorder/delete jobs; replace/list/update items by `job_id`; counts for progress |
| `TTSJobRepository` | add, get, update progress/status, delete |
| `SettingsRepository` | get/set key, get/set namespace |
| `ModelRepository` | list catalog, get, mark downloaded + path |

`TranscriptItem` does **not** need its own UoW attribute if `TranscriptRepository` owns the aggregate.

---

## Domain errors (`domain/errors.py`)

Adapters and services raise these. Routes map them to HTTP (Phase 4). Do not use bare `Exception` or `assert` for user-visible failures.

| Type | Typical HTTP | When |
|------|--------------|------|
| `ValidationError` | 422 | Unknown settings key, step id, speed range, empty text |
| `NotFoundError` | 404 | Unknown job / variant / namespace |
| `ConflictError` | 409 | Illegal status transition; start while Processing; generate with no model |
| `AgeRestrictedError` | — (service maps to `AgeRestricted`) | yt-dlp age gate |
| `DownloadCancelledError` | — (service maps to `Cancelled`) | User cancel during yt-dlp |
| `SABRDetectedError` | — (service may flip session SABR) | Informational from adapter. **This spelling only** — not `SabrDetectedError` |
| `CookieTestError` | 200 `{ ok: false }` or 422 | Cookie probe failed |
| `CookieAccessError` | alias of `CookieTestError` | Browser locked / unreadable cookie file. **Do not** define a second class in Phase 2 |
| `TranscriptsDisabledError` | — (item `Skipped`) | Channel/video has transcripts disabled |
| `NoTranscriptFoundError` | — (item `Skipped`) | No caption track in requested languages |
| `TranscriptRetryableError` | — (service retries) | Transient fetch |
| `FFmpegNotFoundError` | 503 | Binary missing after probe order |
| `ModelDownloadError` | 422/503 | HF fetch failed; variant stays not downloaded |
| `ModelLoadError` | 422/503 | Missing file or unsupported torch |
| `FilesystemError` | 500 | Atomic write / read failed |

---

## Downstream planning notes

Use these when writing Phase 2–6 plans. Do not implement them in Phase 1.

| Phase | Must follow this spec |
|-------|------------------------|
| **2 Infrastructure** | Tables: `download_jobs`, `download_archive`, `transcript_jobs`, `transcript_items`, `tts_jobs`, `model_variants`, `settings`. No `jobs`, `job_artifacts`, `queue_runtime`, `sabr_state`. `model_variants` has no `is_loaded` / `device` columns. Implement **every** port in this file (including `FilesystemPort`, `ModelCatalogPort`, `test_cookies`, `sabr_detected`, version helpers). |
| **3 Services** | `QueueRuntime` lives on `DownloadService` / `TranscriptService`. Compile and zip are methods on `TranscriptService`. Model download updates `ModelVariant` + `ModelDownloadRuntime`. Archive lookup before download. Transcript **Stop** → parent `Cancelled` (see Phase 3). No direct file/library IO. |
| **4 REST** | Existing module routes stay. Job JSON may format `speed_bps` / `eta_seconds` as GUI strings. Add item progress on `GET /transcripts/{id}` (already a Phase 6 addition). |
| **5 MCP** | Tools wrap jobs, not file bodies. |
| **6 GUI** | Amend `progress.json` wording (see conflict). Bind cards to item aggregates. Do not invent a per-video transcript table. |

---

## Explicitly out of scope (do not add in Phase 1)

- `SourceLocator`, `DestinationLocator`, `JobIdentity`, `Operation`, generic `JobArtifact`
- `ModelFetchJob`
- `ConversionJob` **as a Phase 1–7 entity** (Phase 8 adds it; TTS/download convert still must not use it)
- `CaptureShot` **as a Phase 1–8 entity** (Phase 9 adds it)
- Persistable `QueueRuntime`, persistable `SABRState`
- `DownloadJob.parent_id`
- Log / cookie-snapshot / window-geometry entities
- `TranscriptResult.text` as a column

---

## Phase 8 addendum (2026-08-24)

Canonical conversion types, additive `MediaPort` methods, and `ConversionJob` invariants: [08-video-conversion.md](08-video-conversion.md). Do not implement them under MEU-1–4.

`QueueRuntime.queue_name` gains `"conversions"`.

---

## Phase 9 addendum (2026-08-26)

Canonical capture types, `ScreenCapturePort` / `ImageAnnotatePort`, and `CaptureShot` invariants: [09-screenshot-capture.md](09-screenshot-capture.md). Do not implement them under MEU-1–4.

Do **not** add `"captures"` to `QueueRuntime.queue_name` — Capture is a catalog, not a processor queue.

---

## Validation commands

Registered exact-receipt forms live in [`.agent/docs/commands.md`](../../.agent/docs/commands.md). Targeted:

```bash
uv run pytest tests/unit/test_domain.py -x --tb=short -v
uv run pyright packages/core/
uv run ruff check packages/core/
```
