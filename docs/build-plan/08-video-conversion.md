# Phase 8 — Video Conversion

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: Phase 1–6 (MediaPort, queue pattern, GUI chrome) | Outputs: Convert page, REST `/conversions`, MCP `avkit_convert`
> **Spec date:** 2026-08-24. **Does not reopen** MEU-1–23 as incomplete. Phase 1–7 remain the shipped YouTube toolkit; this phase **adds** a fourth module.

> **Convert layout supersession:** [Phase 11 page layout canon](11-page-layout.md) governs Convert presentation in MEU-54; this spec continues to govern conversion behavior, payloads, and mutations.

---

## Goal

Give av-kit a **local file conversion** module: bulk GPU-accelerated compress, in/out cut, and audio extract. The page sits on the left rail **directly under TTS**. Users who already know Downloader should not have to learn a second interaction language.

This file is the **SSOT** for conversion domain, adapter, service, REST, MCP, and GUI. Pointers in `00`–`07` defer to this document.

| Source | Decision |
|--------|----------|
| Spec | This file; [BUILD_PLAN.md](../BUILD_PLAN.md) Phase 8 row |
| Local Canon | Downloader page flow ([06-gui.md](06-gui.md)); `MediaPort.convert`/`probe` stay for TTS/download audio; job records + file pointers ([01-domain-layer.md](01-domain-layer.md)); `{ items, processor }` envelopes ([04-rest-api.md](04-rest-api.md)); compound MCP + `action` ([05-mcp-server.md](05-mcp-server.md)); HelpCard + command registry + `gui-actions-index.md`; FFmpeg setting → bundle → PATH ([07-distribution.md](07-distribution.md)); no CUDA/torch in the installer |
| Research-backed | Steve Krug, *Don't Make Me Think, Revisited* (3rd ed., 2014) — self-evident UI, conventions, visual hierarchy, progressive disclosure, omit needless words. HandBrake-style **preset-first** default path. Shutter Encoder's function-dropdown + hidden queue is the **anti-pattern** (queue discoverability issues are documented upstream). |
| Human-approved | 2026-08-24 USER_EXPLICIT: un-defer Conversion GUI; add a rail entry below TTS; follow existing build-plan flow. Reverses the 2026-08-18 lock “no `ConversionJob` / ConversionJob GUI”. |

**Inspiration is intent, not code** ([BUILD_PLAN.md](../BUILD_PLAN.md) Golden Rule 5). [_video_conversion_pseudo_logic.md](../../_inspiration/_video_conversion_pseudo_logic.md) supplies FFmpeg behavior. Do not paste Shutter Encoder Java or its control surface.

---

## Design thesis (Krug → av-kit)

Krug’s first law: **don’t make me think** — pages must be self-evident ([sensible.com](https://sensible.com/dont-make-me-think/); O’Reilly ch. 1). Applied here:

| Krug rule | Convert-page consequence |
|-----------|--------------------------|
| Conventions are your friend | Reuse Downloader: Help → status chip → input → options → **Add** → queue table → counts → Start / Pause / Resume / Cancel / reorder / Remove / Clear All |
| Visual hierarchy | One cyan primary (**Add**). Queue is the largest region. GPU/encoder is a **chip**, not a form. Advanced is collapsed. |
| Limit choices / mindless clicks | **One rail item**, not three. Task is a segmented control: Compress \| Cut \| Extract. Five named presets, default **Balanced**. |
| Progressive disclosure (G26 HelpCard + Advanced) | CQ, scale, audio re-encode, GPU override live under **Advanced**. HelpCard at top (What / how / pitfalls). |
| Omit needless words | No “Choose function”, no FFmpeg flag names (`hevc_nvenc`, `-cq`, `-preset p4`) on the default surface. |
| Obvious beats fewer-but-puzzling clicks | Add then Start (same as Downloader). Do **not** hide the queue behind a hamburger next to Start (Shutter Encoder anti-pattern). |
| You-are-here navigation | Rail item `Convert`, shortcut `Ctrl+4`, route `/convert`, active cyan bar. |

**Rejected layouts**

| Layout | Why it fails Krug / Local Canon |
|--------|----------------------------------|
| Three rail items (Compress / Cut / Extract) | Makes the user decide *which app* conversion is. Settings/Collapse stay pinned; primary rail already has three modules. |
| Shutter-style function dropdown | Dozens of codecs; queue is a hidden mode. |
| HandBrake clone (preset tree + Video/Audio/Dimensions tabs) | A second app language. av-kit users already learned the Downloader queue. |
| Wizard (file → preset → review → start) | Extra thought-bearing steps. Downloader is one page. |
| Inner **routes** for Compress/Cut/Extract | [06-gui.md](06-gui.md) §Module Internal Navigation: no internal tab routing. Segmented control is page-local layout, not a route. |

**Current GUI to match** (shipped shell): dark `#282a36`, cyan `#8be9fd` active/primary, red destructive, Help accordion, dense form, table, footer actions. Convert must use the same tokens (G31/G32) — no per-page accent fork.

---

## Module Internal Navigation (Phase 6 amendment)

| Position | Icon | Label | Route | Shortcut | Notes |
|----------|------|-------|-------|----------|-------|
| Top (4th) | 🎬 (Lucide `Film`) | Convert | `/convert` | `Ctrl+4` | Below TTS, above the Settings pin |

`Ctrl+1`–`Ctrl+3` and `Ctrl+,` / `Ctrl+B` unchanged. Command palette category adds `convert`. Console module tag: `[Convert]`.

---

## Convert Page (`/convert`)

> **Source**: [_video_conversion_pseudo_logic.md](../../_inspiration/_video_conversion_pseudo_logic.md) (pipeline, presets, GPU, cut, extract). **Layout**: Local Canon Downloader + Research-backed Krug.

### Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  Convert                                                              Convert  Ctrl+4│
├──────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─ Help (collapsed) ──────────────────────────────────────────────────────────────┐ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ TASK ────────────────────────────────────────────── Encoder: NVIDIA NVENC ─────┐ │
│  │  (●) Compress    ( ) Cut    ( ) Extract                                         │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ FILES ─────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                 │ │
│  │     Drop video files here          or  [Browse…]                                │ │
│  │                                                                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ PRESET (visible when Compress) ────────────────────────────────────────────────┐ │
│  │  [ Archival ]  [ High Quality ]  [ Balanced ★ ]  [ Sharing ]  [ Mobile ]        │ │
│  │  Balanced — H.265, good size, keeps audio.                                      │ │
│  │  ▸ Advanced   CQ · Scale · Audio                                                │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ CUT (visible when Cut) ────────────────────────────────────────────────────────┐ │
│  │  In  [00:00:00.000]    Out  [00:00:00.000]   [□] Apply these times to every file│ │
│  │  (●) Fast (copy)   ( ) Accurate (re-encode)                                     │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ EXTRACT (visible when Extract) ────────────────────────────────────────────────┐ │
│  │  (●) First audio stream    ( ) All audio streams                                │ │
│  │  Container is chosen from the codec (AAC→.m4a, PCM→.wav, …). No re-encode.      │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  Output folder: [ ~/Videos/av-kit ] [Browse…]     [□] Skip files that already exist  │
│                                                                                      │
│  [  Add  ]                                                                           │
│                                                                                      │
│  ┌─ QUEUE ─────────────────────────────────────────────────────────────────────────┐ │
│  │  #  Status   File                  Kind       Preset/mode    Size    Progress   │ │
│  │  1  🔄       lecture.mp4           Compress   Balanced       1.2 GB  ███░ 42%   │ │
│  │  2  ⏳       lecture.mp4           Extract    a:0 → .m4a     —       —          │ │
│  │  Summary: 2 items — 1 processing, 1 pending                                     │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  [Start] [Pause] [Resume] [Cancel]  [Up] [Down] [Top] [Bottom]  [Reset]              │
│  [Remove] [Clear All]               [Open file] [Open folder]                        │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

**Scan path (top → bottom, Krug “billboard”):** what am I doing (task) → drop files → named preset or times → Add → watch the queue → Start.

### Task control (G21)

Three radio-style segments, **direct selection**, not a cycle button. Changing task changes the options card only; it does **not** clear the queue. Each queue row stores its own `kind` from the moment it was added.

### Files input

| Control | Behavior | Source |
|---------|----------|--------|
| Drop zone | Multi-file drop. Renderer never reads bytes; preload exposes absolute paths | Local Canon TTS `readTextFile` / Downloader IPC |
| Browse | IPC `showOpenDialog` `{ multiSelections, openFile }` with video/audio filters | Local Canon Settings Browse |
| Add | `POST /conversions` with those paths + current task options | Spec |

Reject empty Add (no paths) with inline validation — do not POST. Paths must be absolute; API 422 if relative or missing (`extra="forbid"`).

### Compress presets (default surface)

Built-in catalog (not a SQLite table). Same names as inspiration. Default **Balanced**.

| Preset `name` | Codec (resolved) | CQ / CRF | Audio | NVENC preset | Scale | Description (one line, shown under chips) |
|---------------|------------------|----------|-------|--------------|-------|-------------------------------------------|
| `Archival` | H.265 | 18 | Copy | p7 | source | Maximum quality, larger files |
| `HighQuality` | H.265 | 22 | AAC 128k | p4 | source | Personal library |
| `Balanced` | H.265 | 25 | AAC 128k | p4 | source | Best quality-to-size ★ default |
| `Sharing` | H.265 | 28 | AAC 128k | p4 | source | Smaller, still watchable |
| `Mobile` | H.265 | 30 | AAC 96k | p4 | 720p | Small files |

Software fallback uses `-crf` with the same numbers (`libx265`). Do not show `p4` / `hevc_nvenc` unless Advanced is open.

**Advanced (collapsed)** — Compress only:

| Control | Values | Default |
|---------|--------|---------|
| CQ slider | 18–32, step 1 | preset’s CQ |
| Scale | Source, 1080p, 720p, 480p | preset’s scale |
| Audio | Copy, AAC 128k, AAC 192k, AAC 96k | preset’s audio |
| Encoder override | Auto, NVIDIA, AMD, Intel, Software | Auto (`converter.gpu_preference`) |

Changing a preset **resets** Advanced to that preset’s values (mindless undo). Editing Advanced does not rename the chip; the row stores the resolved numeric options.

### Cut

| Control | Rule | Source |
|---------|------|--------|
| In / Out | `HH:MM:SS.mmm` (or seconds). Converted to ms for FFmpeg `-ss` / `-t` | Spec / inspiration |
| Apply to every file | Same in/out on each Add in this batch | Spec |
| Fast (copy) | `-c copy` — may snap to keyframes. Default. HelpCard explains this | Research-backed (FFmpeg copy seek) |
| Accurate (re-encode) | Uses the Balanced compress encode path for the trimmed span | Spec |

No timeline player in MVP (named deferral). Numeric fields are enough for the stated user intent (“cut at specific times”).

### Extract

| Control | Rule | Source |
|---------|------|--------|
| First audio stream | `map a:0`, container from codec table | Spec |
| All audio streams | One `ConversionJob` **per stream** (N rows) | Local Canon playlist → N `DownloadJob` |
| Container map | PCM→`.wav`, AAC→`.m4a`, AC3→`.ac3`, EAC3→`.eac3`, Opus→`.opus`, Vorbis→`.oga`, MP3→`.mp3`, MP2→`.mp2`, WMA→`.wma`; unknown → `.mka` | Spec (inspiration) |
| Video-only / subtitles | **Deferred** | — |

No re-encode on the default extract path (`-c:a copy`).

### GPU chip

| Display | Meaning |
|---------|---------|
| `Encoder: NVIDIA NVENC` (or AMF / QSV) | 1-frame GPU test passed this session |
| `Encoder: Software (libx265)` | No usable GPU encoder in this FFmpeg build or test failed |
| `Encoder: Checking…` | First probe in flight |
| `FFmpeg missing` | Same as Settings → Dependencies; Add/Start disabled |

Chip is **not** a dropdown on the default surface. Override lives in Advanced + Settings. Detection: `ffmpeg -encoders` then a 1-frame encode test (inspiration). **Do not** call deprecated `wmic`. Never bundle CUDA/torch ([07-distribution.md](07-distribution.md)). NVENC uses the **installed GPU driver** + whatever the bundled FFmpeg was compiled with. If the bundle lacks `hevc_nvenc`, show Software — do not fail the page.

### Queue table

Columns: `#`, Status, File (stem + ext), Kind, Mode (preset name, `in–out`, or `a:N → ext`), Size (output if known else input), Progress, Speed, ETA.

Statuses (no SABR/age): `Pending`, `Processing`, `Done`, `Failed`, `Cancelled`, `Skipped`.

`Skipped` = skip-existing setting and destination already present.

`Paused` is **processor** state only (`QueueProcessorState`), never a job status (Local Canon DownloadJob).

Summary line: counts by status, matching Downloader.

Footer actions: same verbs and destructive red as Downloader. Open file / Open folder via existing IPC.

Poll `GET /conversions` at 1 s while `processor=Processing`, 5 s when Idle (G5). Envelope `{ items, processor }`.

### HelpCard topics (minimum)

What Convert does; presets vs Advanced; GPU auto / software fallback; Fast cut vs Accurate; extract containers; sequential GPU (one file at a time); Add then Start.

---

## Domain

### Package

```
packages/core/src/avkit_core/domain/conversion.py   # ConversionJob, preset catalog, option DTOs
```

Enums live in `domain/enums.py` (MEU-28 extends MEU-2). Session VOs may live in `domain/progress.py` / `domain/queue.py`.

### Enums

| Enum | Values | Persist |
|------|--------|---------|
| `ConversionKind` | `Compress`, `Cut`, `Extract` | yes (`.name`) |
| `ConversionStatus` | `Pending`, `Processing`, `Done`, `Failed`, `Cancelled`, `Skipped` | yes |
| `ConversionPresetId` | `Archival`, `HighQuality`, `Balanced`, `Sharing`, `Mobile` | yes; Cut/Extract store `None` |
| `CutCopyMode` | `FastCopy`, `Reencode` | yes when kind=Cut |
| `AudioEncodeMode` | `Copy`, `Aac96`, `Aac128`, `Aac192` | yes when kind=Compress |
| `GpuPreference` | `Auto`, `Nvidia`, `Amd`, `Intel`, `Software` | settings + optional job override |

### `GPUCapabilities` (session VO — not a table)

Held on `ConversionService`, analogous to `SABRStatus`.

| Field | Type |
|-------|------|
| `nvidia_nvenc` | `bool` |
| `amd_amf` | `bool` |
| `intel_qsv` | `bool` |
| `vulkan` | `bool` |
| `software_h265` | `bool` |
| `software_h264` | `bool` |
| `recommended_encoder` | `str` | FFmpeg codec name, e.g. `hevc_nvenc` or `libx265` |
| `checked_at` | `datetime \| None` |

Restart → empty until first `detect_gpu()` (page mount or `GET /conversions/gpu`).

### `ConversionJob` — persistable

One row per output. Many files on Add → **N jobs** (Local Canon playlist explode). Cut and Extract are **the same table** with `kind` — one queue, one mental model. This does **not** unify with `DownloadJob` / `TTSJob` (01 “unlike workers stay unlike”).

| Field | Type | Persist | Source |
|-------|------|---------|--------|
| `id` | `str` (UUID) | yes | Spec |
| `kind` | `ConversionKind` | yes | Spec |
| `input_path` | `Path` | yes | Spec |
| `output_path` | `Path` | yes | Resolved on add |
| `display_name` | `str` | yes | Input stem + ext |
| `preset_id` | `ConversionPresetId \| None` | yes | Compress |
| `cq` | `int \| None` | yes | Resolved CQ/CRF |
| `scale_height` | `int \| None` | yes | `None` = source; Mobile default 720 |
| `audio_mode` | `AudioEncodeMode \| None` | yes | Compress |
| `gpu_encoder` | `str \| None` | yes | Resolved FFmpeg codec name at Start (may be null until then) |
| `in_ms` | `int \| None` | yes | Cut |
| `out_ms` | `int \| None` | yes | Cut; exclusive end. Duration = out − in |
| `copy_mode` | `CutCopyMode \| None` | yes | Cut |
| `stream_index` | `int \| None` | yes | Extract audio index |
| `status` | `ConversionStatus` | yes | Spec |
| `progress` | `float` | yes | 0.0–1.0 |
| `speed_bps` | `float \| None` | yes | From FFmpeg `speed=` when derivable; else null |
| `eta_seconds` | `int \| None` | yes | From duration × remaining |
| `file_size` | `int \| None` | yes | Output bytes when Done; input size after probe |
| `duration_seconds` | `float \| None` | yes | Probe |
| `width` / `height` | `int \| None` | yes | Probe |
| `error_message` | `str \| None` | yes | Spec |
| `queue_position` | `int` | yes | Reorder |
| `created_at` / `updated_at` | `datetime` | yes | Spec |
| `gpu_preference` | `GpuPreference \| None` | yes | Compress. The job's own encoder choice; null = the setting at Start |

**Invariants**

- `Paused` is never a job status.
- Reset: `Failed` → `Pending` (clear `error_message`, `progress`).
- Clear All deletes `conversion_jobs` rows only; **does not delete media files**.
- Remove deletes the row; files stay.
- Duplicate destination: auto-suffix `_1`, `_2` unless `converter.skip_existing` then `Skipped`.
- Compress with `in_ms`/`out_ms` set is illegal — Cut owns trimming. (User can Cut then Compress as two rows.)
- TTS WAV→MP3 and download audio extract **must not** insert `ConversionJob` rows. They keep calling `MediaPort.convert(ConvertOptions)` (Phase 1–3 contract).

**State machine**

```
Pending ──→ Processing ──→ Done
                │
                ├──→ Failed ──→ Pending (Reset)
                ├──→ Cancelled
                └──→ Skipped (existing output)
```

### DTOs (not tables)

| Type | Role |
|------|------|
| `StreamInfo` | `index`, `codec_type`, `codec_name`, `language`, `channels`, `sample_rate` |
| `MediaInfo` | **Extend** existing: optional `width`, `height`, `fps`, `bit_depth`, `field_order`, `streams: list[StreamInfo]`. All new fields default `None` so TTS/download callers stay valid |
| `VideoEncodeOptions` | Compress: codec, cq, nvenc_preset, scale_height, audio_mode, hwaccel |
| `CutOptions` | in_ms, out_ms, copy_mode |
| `ExtractOptions` | stream_index, output_container |
| `ConvertOptions` | **Unchanged** — audio-only TTS/download convert |

Built-in presets: frozen catalog function `builtin_conversion_presets() -> tuple[ConversionPreset, ...]` (like voice catalog). No `conversion_presets` table in MVP.

### Ports — additive `MediaPort`

Keep `is_available`, `ffmpeg_version`, `convert`, `probe`. Add:

```python
class MediaPort(Protocol):
    def is_available(self) -> bool: ...
    def ffmpeg_version(self) -> str | None: ...
    def convert(self, input_path: Path, output_path: Path, options: ConvertOptions) -> None: ...
    def probe(self, file_path: Path) -> MediaInfo: ...
    def detect_gpu(self) -> GPUCapabilities: ...
    def encode(
        self,
        input_path: Path,
        output_path: Path,
        options: VideoEncodeOptions,
        on_progress: Callable[[ProgressSnapshot], None],
    ) -> None: ...
    def cut(
        self,
        input_path: Path,
        output_path: Path,
        options: CutOptions,
        on_progress: Callable[[ProgressSnapshot], None],
    ) -> None: ...
    def extract_stream(
        self,
        input_path: Path,
        output_path: Path,
        options: ExtractOptions,
        on_progress: Callable[[ProgressSnapshot], None],
    ) -> None: ...
```

`on_progress` is required (GUI ETA). Implementations must be cancellable via the existing worker cooperative-cancel pattern (send `q` to FFmpeg stdin, then terminate if needed) — Spec (inspiration).

### Domain errors

| Error | When |
|-------|------|
| `FFmpegNotFoundError` | Already exists — reuse |
| `FFmpegEncodeError` | Non-zero FFmpeg after start |
| `MediaProbeError` | Probe failed (corrupt / not media) |
| `InvalidTimeRangeError` | `out_ms <= in_ms` or negative |
| `GpuUnavailableError` | Encoder override requested but test failed — service **falls back** to software unless override is a hard Software miss |

Do not use `assert` for boundary checks.

### QueueRuntime

Extend `queue_name` union with `"conversions"`. Same in-memory rules: restart → `Idle`; job statuses survive.

---

## Infrastructure

### Eighth table `conversion_jobs`

Phase 2 locked “exactly these seven”. **Phase 8 exception (dated 2026-08-24):** append-only migration adds `conversion_jobs`. Still **no** STI `jobs` table.

Greenfield CREATE in `models.py` plus `migrations.py` no-op-safe `ALTER`/`CREATE IF NOT EXISTS` for existing DBs (Local Canon Phase 2 migrations).

Columns match the entity field table (TEXT enum names, Path as TEXT, floats, UTC datetimes). Indexes: `queue_position`, `status`.

UoW grows `conversion_jobs: ConversionJobRepository` with the same CRUD/reorder/`delete_all` shape as downloads.

### `FFmpegAdapter` extensions

| Method | Rule |
|--------|------|
| `probe` | Fill new `MediaInfo` fields via ffprobe JSON (`-show_streams -show_format -of json`) |
| `detect_gpu` | Parse `ffmpeg -encoders`; for each candidate (`hevc_nvenc`, `hevc_amf`, `hevc_qsv`) run a 1-frame test; cache for the process |
| `encode` | Prefer zero-copy GPU path when `VideoEncodeOptions` and capabilities allow; else software. Parse stderr `frame=` / `time=` / `speed=` into `ProgressSnapshot` |
| `cut` | FastCopy: `-ss` before `-i`, `-t`, `-c copy`. Reencode: encode path with trim |
| `extract_stream` | `-vn -sn -c:a copy -map a:{n}` + container from map |
| `convert` | **Unchanged** TTS/download audio |

Even dimensions on scale (`scale=W:-2`). 10-bit: `p010` instead of `nv12` when `bit_depth >= 10` (inspiration).

Do not shell-out to `wmic`.

structlog module key: `convert` (and keep `media`).

---

## Service layer

`ConversionService` in `packages/core/src/avkit_core/services/conversion.py`.

| Method | Behavior |
|--------|----------|
| `add_to_queue(paths, spec)` | Probe each path; build output path; insert N jobs `Pending`. Probe failure → that job `Failed` with message; do not abort the rest |
| `get_queue` / `get_job` | Rows + processor |
| `start_processing` | Sequential **one FFmpeg at a time** (GPU is single-instance — Spec). 409 if already Processing |
| `pause_processing` | After current file finishes (Local Canon download pause) |
| `resume_processing` | Continue Pending |
| `cancel_processing` | Cooperative cancel in-flight; remaining stay Pending (download pattern) — **or** mark in-flight Cancelled. Match DownloadService cancel semantics exactly |
| `reorder_queue` | Permutation of ids |
| `reset_failed` | Failed → Pending |
| `remove` / `clear_queue` | Rows only |
| `detect_gpu` / `get_gpu` | Session VO |
| `estimate_output_size` | Optional; not required on the default GUI. MCP may expose later |

Output path: `{converter.output_dir}/{stem}_{kind_token}{ext}` with collision suffix. Compress ext `.mp4`. Cut keeps container when FastCopy else `.mp4`. Extract uses codec map.

Worker must not hold one UoW across the whole encode; commit progress on a timer (Phase 2/3 note).

---

## REST API

Prefix `/api/v1`. Static paths before `{id}`. Dual Bearer. `extra="forbid"`. Invalid → **422**, not 500. Lists: `{ items, processor }`.

### Boundary inventory

| Surface | Schema owner | Extra | Error |
|---------|--------------|-------|-------|
| REST body/query | Pydantic `ConversionCreateIn` et al. | forbid | 422 |
| MCP `avkit_convert` | Zod `.strict()` | strict | 422 via REST |
| GUI form | Zod in renderer + REST | — | inline + G15 envelope |
| File paths | Absolute paths from IPC only | — | 422 if not absolute / not a file |
| Settings `converter` | Existing settings PUT | forbid | 422 unknown key |

Python `assert` is not validation.

### Routes

| Method | Path | Service | Success | Notes |
|--------|------|---------|---------|-------|
| `POST` | `/conversions` | `add_to_queue` | 201 `{ items }` | Body below |
| `GET` | `/conversions` | queue + processor | 200 envelope | Poll |
| `GET` | `/conversions/gpu` | `get_gpu` | 200 `GPUCapabilitiesOut` | Does not re-run the 1-frame test |
| `POST` | `/conversions/gpu/refresh` | `detect_gpu` | 200 | Re-probe |
| `POST` | `/conversions/start` | start | 202 | 409 if Processing |
| `POST` | `/conversions/pause` | pause | 202 | |
| `POST` | `/conversions/resume` | resume | 202 | |
| `POST` | `/conversions/cancel` | cancel | 202 | |
| `PUT` | `/conversions/reorder` | reorder | 200 `{ items }` | `{ job_ids }` |
| `DELETE` | `/conversions` | clear | 204 | Files stay |
| `GET` | `/conversions/{id}` | get | 200 | |
| `POST` | `/conversions/{id}/reset` | reset | 200 | 409 if not Failed |
| `DELETE` | `/conversions/{id}` | remove | 204 | Files stay |

### `ConversionCreateIn`

`paths: list[str]` (min 1), `kind: Literal["compress","cut","extract"]` (wire lowercase, API maps to enum `.name` like quality wire), plus kind-specific optional fields:

- compress: `preset` (wire `balanced` default), optional `cq`, `scale_height`, `audio_mode`, `gpu_preference`
- cut: `in_ms`, `out_ms` (ints ≥ 0, `out_ms > in_ms`), `copy_mode` (`fast_copy` default)
- extract: `stream_mode` (`first` \| `all`), optional `stream_index` (required if not `all`/`first`)

Extra forbid. Unknown preset → 422.

Wire mapping follows Phase 4 quality/audio: GUI strings ≠ domain `.name` where needed; document the map in OpenAPI.

### `ConversionJobOut`

All persistable fields needed by the table: `id`, `kind`, `input_path`, `output_path`, `display_name`, `preset_id`, `cq`, `scale_height`, `audio_mode`, `gpu_encoder`, `in_ms`, `out_ms`, `copy_mode`, `stream_index`, `status`, `progress`, `speed`, `eta`, `file_size`, `duration_seconds`, `width`, `height`, `error_message`, `queue_position`, `created_at`. Format speed/eta as GUI strings at the schema layer (Local Canon DownloadJobOut).

No media bytes.

### Settings namespace

`namespace` ∈ existing set **plus** `converter`. Else 404.

| Dotted docs name | Leaf key | Type | Default | Notes |
|------------------|----------|------|---------|-------|
| `converter.output_dir` | `output_dir` | string | `~/Videos/av-kit` | Browse |
| `converter.default_preset` | `default_preset` | string | `balanced` | Compress chips |
| `converter.skip_existing` | `skip_existing` | bool | `true` | |
| `converter.gpu_preference` | `gpu_preference` | string | `auto` | Advanced + Settings |

Health console `module` union adds `convert`.

G8: regenerate committed OpenAPI after these routes.

---

## MCP

New compound tool `avkit_convert` (M2 parity with REST). No second URL space. Zod `.strict()`. Destructive `remove` / `clear` require `confirm: true` (M3).

**Workflow:** `add` → `start` → `list` (poll) → optional pause/resume/cancel. GPU: `gpu` / `gpu_refresh`.

| action | REST |
|--------|------|
| `add` | `POST /conversions` |
| `list` | `GET /conversions` |
| `get` | `GET /conversions/{id}` |
| `start` / `pause` / `resume` / `cancel` | matching POSTs |
| `reorder` | `PUT /conversions/reorder` |
| `reset` | `POST /conversions/{id}/reset` |
| `remove` | `DELETE /conversions/{id}` |
| `clear` | `DELETE /conversions` |
| `gpu` | `GET /conversions/gpu` |
| `gpu_refresh` | `POST /conversions/gpu/refresh` |

Returns paths and status, never media bytes. Instructions file: Convert is **local files only**; still never upload to YouTube.

---

## GUI implementation notes

| Item | Rule |
|------|------|
| Route | lazy `/convert` like Transcript/TTS |
| Nav | `SHELL_PRIMARY_NAV` 4th item; testid `nav-convert` |
| Page | `ui/src/renderer/src/features/converter/ConvertPage.tsx` |
| Help | `converter-help-content.ts` + HelpCard |
| Commands | `converter-commands.ts`; AppShell listens (G11) |
| Palette | `convert:add`, `convert:start`, `convert:pause`, `convert:resume`, `convert:cancel`, `convert:clear` |
| Tokens | G31/G32/G34 — shared Button variants |
| Drag-drop | Preload allowlist only |
| E2E | Wave **8** `gui-convert` — `[B]` + CI if no display |

Settings page: new **Convert** card (output dir, default preset, skip existing, GPU preference) + Browse.

---

## Integration (named deferrals — not this phase’s GUI)

| Handoff | Status |
|---------|--------|
| Downloader Done row → Add to Convert | Deferred (would reopen MEU-20) |
| Extract audio → Transcript / TTS | Deferred |
| Timeline player / split-equal segments / 2-pass / target file size / deinterlace / custom GOP / subtitle extract / user-saved presets table | Deferred |

Resolution **is** in MVP via Mobile 720p + Advanced scale. 2-pass and size-target stay out of the default UI (Krug: extra modes that require bitrate math).

---

<a id="output-folder-residual"></a>

## Output folder (residual)

> **MEU-109.** Registered 2026-11-03 from known issue `CONVERT-OUTPUT-DIR-MISSING`. Nothing creates the `converter.output_dir` folder, so on a fresh profile the first Convert job fails and the user reads only "ffmpeg exited 4294967294".

| Rule | Contract | Source |
|------|----------|--------|
| Create | `OUTPUT_PARENT`: `encode`, `cut` and `extract_stream` create `output_path.parent` before starting FFmpeg. | Known issue; precedent `capture/adapter.py:359` |
| Existing folder | Left alone, and its contents survive. | This section |
| Can't create | The job ends `Failed` with an error naming the path, and FFmpeg never starts. The `OSError` reaches the existing `_process` failure path. | `conversion.py:468-472` |
| Layer | The fix belongs in the infrastructure adapter. Core services don't touch the filesystem for this. | Precedent `capture/adapter.py:359,375` |

> **Delivered (Session 44).**
> - `_ensure_output_parent` in `packages/infrastructure/src/avkit_infra/media/adapter.py` creates the folder before FFmpeg starts, in `encode`, `cut` and `extract_stream`.
> - `tests/unit/test_ffmpeg_conversion.py` and `tests/unit/test_conversion_service.py`, AC-109.1 to AC-109.5. The packaged smoke ran a real first conversion into a missing folder.
> - Gate: the shared `session-gate.ps1` record in the MEU-109 handoff.
> - Plan `docs/execution/plans/2026-11-03-release-rc1/`.

<a id="job-encoder-choice-residual"></a>

## Encoder choice per job (residual)

> **MEU-112.** Registered 2026-11-04 from known issue `CONVERT-JOB-GPU-PREFERENCE-IGNORED`, on Mat's ruling to fix it before RC1. `POST /conversions` accepts `gpu_preference` and the page has an Encoder dropdown, but nothing reads the value, so a job always runs what the `converter.gpu_preference` setting says.

| Rule | Contract | Source |
|------|----------|--------|
| Stored | A Compress job stores the request's `gpu_preference`. Null means the request sent none. Cut and Extract jobs store null. | This section |
| Resolved | `_dispatch` passes the job's value to `_resolve_encoder`. Null means the setting, read when the job runs. An explicit value wins, including Auto over a non-auto setting. | This section |
| Kept | The value survives a re-queue and a restart, because it lives on the row. | This section |
| Upgrade | `conversion_jobs` gets a nullable last column. `COLUMN_MIGRATIONS` adds it to an existing database after reading `PRAGMA table_info`, so a repeat does nothing and rows stay intact. | `tests/integration/test_sqlite_uow.py:254` keeps `MIGRATIONS` self-guarding |
| Page | The page and the command snapshot send the dropdown when it differs from the saved setting, including Auto over a saved non-auto value, and omit it when they match. | This section |
| Dropdown | A choice made in the dropdown stays the choice when settings arrive late or change afterwards, and it is sent when the saved setting isn't known yet. A dropdown nobody touched shows the setting and sends nothing. | This section |
| API response | Unchanged. `gpu_encoder` already shows what ran. | §`ConversionJobOut` |

> **Delivered (Session 44).**
> - `ConversionJob.gpu_preference` in `packages/core/src/avkit_core/domain/conversion.py`, stored by `_jobs_for_path` and read by `_dispatch` and `_resolve_encoder` in `services/conversion.py`. The column and its `COLUMN_MIGRATIONS` step are in `packages/infrastructure/src/avkit_infra/database/`.
> - `ConvertPage.tsx` keeps only what the user picked, and `perJobGpuPreference` in `convert-commands.ts` decides what Add and the command snapshot send: a pick goes out unless it equals a known saved setting.
> - The draft in `useConverterSettings.ts` holds only the fields the user edited, so every other field, including the encoder the page compares against, follows the saved settings while an edit is open.
> - `tests/unit/test_conversion_service.py`, `tests/unit/test_ffmpeg_conversion.py` and `ui/tests/unit/convert-page.behavior.test.ts`, AC-112.1 to AC-112.6, AC-112.8 and AC-112.9. `tools/smoke_packaged_rc.py` proved AC-112.7 on the packaged and installed backends: a Software job ran `libx265` on a PC where the default job ran `hevc_nvenc`.
> - Gate: the shared `session-gate.ps1` record in the MEU-112 handoff.
> - Plan `docs/execution/plans/2026-11-03-release-rc1/`.

<a id="extract-stream-index-residual"></a>

## Extract stream index (residual)

> **MEU-123.** Registered 2026-11-04 from `CONVERT-EXTRACT-STREAM-INDEX-MISMATCH`, with rider `CONVERT-EXTRACT-ENCODER-LABEL`. `media/adapter.py:634-635` passes `-map a:{stream_index}`, which counts audio tracks only, while `services/conversion.py` treats the same number as ffprobe's index across all streams: `_output_ext` at `:386` and the All audio streams plan at `:328`. So First audio stream on a normal video looks up the picture's codec and falls back to `.mka`, and All audio streams asks for tracks that don't exist.

| Rule | Contract | Source |
|------|----------|--------|
| One meaning | `stream_index` is audio-relative everywhere. | Local Canon: triage D-227; §Extract table (`map a:0`) |
| Extension | `_output_ext` looks the codec up by audio position, so AAC from a normal video comes out as `.m4a`, as the Extract table says. | Local Canon: triage D-227 |
| All audio streams | The plan sends audio positions. | Local Canon: triage D-227 |
| Encoder label (rider) | An Extract job saves no `gpu_encoder`, because it's a stream copy that uses no encoder. | Local Canon: known issue `CONVERT-EXTRACT-ENCODER-LABEL` |
| Tests | Both modes against a real `.mp4`, with one audio track and with two. | Local Canon: triage D-227 |

---

## MEUs

| MEU | Slug | Section | Depends on |
|-----|------|---------|------------|
| MEU-28 | `domain-conversion` | Domain + ports + errors | MEU-4 |
| MEU-29 | `infra-conversion` | `conversion_jobs` + FFmpegAdapter methods | MEU-28, MEU-5, MEU-8 |
| MEU-30 | `svc-conversion` | ConversionService | MEU-29 |
| MEU-31 | `api-conversion` | REST + settings namespace + OpenAPI | MEU-30, MEU-14 |
| MEU-32 | `mcp-convert` | `avkit_convert` | MEU-31, MEU-17 |
| MEU-33 | `gui-convert` | Rail + page + Help + Wave 8 | MEU-31, MEU-19, MEU-26 |
| MEU-109 | `convert-output-folder` | [§Output folder (residual)](#output-folder-residual) | MEU-29 |
| MEU-112 | `convert-job-gpu-preference` | [§Encoder choice per job (residual)](#job-encoder-choice-residual) | MEU-30, MEU-33 |
| MEU-123 | `convert-extract-stream-index` | [§Extract stream index (residual)](#extract-stream-index-residual) | MEU-29, MEU-30 |

---

## Exit criteria

- Domain: `ConversionJob` invariants + MediaPort additive methods tested; TTS/download `convert()` still works (regression).
- Infra: eighth table; probe JSON; GPU detect without `wmic`; progress parse; cancel.
- Service: sequential worker; skip-existing; suffix; pause/cancel match download semantics.
- API: every route has ≥1 contract test; extra field → 422; list envelope; OpenAPI committed.
- MCP: action table parity; confirm on destructive.
- GUI: Convert under TTS; Ctrl+4; segmented task; presets; drop/browse; queue actions; HelpCard; action-index audit; Wave 8 written and wired.

---

## What this layer must not do

| Forbidden | Why |
|-----------|-----|
| Paste Shutter Encoder UI/code | Golden Rule 5 |
| Three rail items for Compress/Cut/Extract | Krug + 06 nav |
| `ConversionJob` for TTS MP3 or yt-dlp audio extract | Phase 1–3 |
| STI `jobs` table | Phase 1 |
| SSE for encode progress | Poll GET |
| Bundle CUDA / ship NVENC as a CUDA wheel | Phase 7 |
| Parallel encodes on one GPU | Spec sequential |
| Relative paths from the renderer | 422 |
| `wmic` GPU detect | Deprecated; FFmpeg probe is enough |
| Timeline / 2-pass / size-target in MVP | Named deferrals |

---

## Validation commands

Registered receipts in [`.agent/docs/commands.md`](.agent/docs/commands.md). Per-MEU: scoped pytest/pyright/ruff or vitest/tsc/eslint as the touched package requires. Phase gate (full repo) only when exiting a later ship train — not as the MEU-28 unit gate.
