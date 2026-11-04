# Phase 4 — REST API

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: [Phase 3](03-service-layer.md) | Outputs: [Phase 5](05-mcp-server.md), [Phase 6](06-gui.md)

---

## Goal

Expose Phase 3 services over FastAPI on localhost. One route → one service method. Pydantic is the **boundary owner** (`extra="forbid"`). The API formats wire values for the GUI; it does not invent job types, tables, or session persistence.

| Source | Decision |
|--------|----------|
| Spec | [Phase 3](03-service-layer.md) command tables; [Phase 6](06-gui.md) consumed endpoints + Phase 4 route-addition list |
| Local Canon | Zorivest `create_app()` / ErrorEnvelope / Bearer; [DESIGN_PROPOSAL.md §4](../../_inspiration/DESIGN_PROPOSAL.md) start → poll |
| Research-backed | FastAPI + Pydantic v2; 422 for invalid input, not 500 |
| Human-approved | 2026-08-18: no SSE in MVP; no transcript/audio bytes in JSON; settings leaf keys |

This file **supersedes** the short route list that used to live here. [06-gui.md](06-gui.md) “Phase 4 alignment” notes are resolved below.

---

## Package layout

```
packages/api/src/avkit_api/
├── main.py              # create_app(), lifespan, middleware
├── dependencies.py      # get_*_service from app.state
├── auth.py              # Bearer check
├── errors.py            # ErrorEnvelope + exception handlers
├── schemas/
│   ├── common.py        # ErrorEnvelope, QueueRuntimeOut, pagination-free lists
│   ├── downloads.py
│   ├── transcripts.py
│   ├── tts.py
│   ├── models.py
│   ├── settings.py
│   └── health.py
└── routes/
    ├── downloads.py
    ├── transcripts.py
    ├── tts.py
    ├── models.py
    ├── settings.py
    └── health.py
```

Prefix: `/api/v1`. Bind **127.0.0.1** only (Electron + MCP on the same machine). GUI `apiFetch` uses `getBackendUrl()` + paths like `/downloads` — **base URL includes `/api/v1`**.

---

## App factory and lifespan

Same pattern as Zorivest `create_app()`:

1. Build UoW factory + port adapters (wired from infra, not imported by domain).
2. Construct the seven services from [Phase 3](03-service-layer.md).
3. Store them on `app.state`.
4. Register routers. **Declare static paths before `{id}`** (`/downloads/sabr` before `/downloads/{id}`).
5. On shutdown: cancel in-flight processors; unload TTS model; dispose engine.

`dependencies.py`: `get_download_service()`, `get_transcript_service()`, `get_tts_service()`, `get_model_service()`, `get_settings_service()`, `get_health_service()`.

---

## Auth

| Client | Token |
|--------|-------|
| Electron renderer | Ephemeral Bearer from `PythonManager` spawn (`--token NONCE`) |
| MCP | Pre-provisioned API key (same `Authorization: Bearer` header) |

Every route except `GET /api/v1/health` (liveness for spawn polling) requires a valid Bearer. Unknown/missing → **401**. Do not put the token in logs, query strings, or job rows.

CORS: localhost origins only (Electron, optional Vite). No wildcard.

---

## Middleware

| Layer | Rule |
|-------|------|
| Request-ID | Generate or accept `X-Request-ID`; bind structlog contextvars |
| ErrorEnvelope | All errors: `{ "error": { "code": str, "message": str, "details": object \| null } }` |
| Auth | Bearer as above |
| Content-Type | JSON in/out. No multipart except none in MVP (file paths, not uploads) |

### Status mapping

| HTTP | When |
|------|------|
| 200 | GET success; PUT settings; compile that finished |
| 201 | POST that created job(s) (`POST /downloads`, `POST /transcripts`, `POST /tts/generate`) |
| 202 | Start / pause / resume / cancel / stop / model download accepted (async work already running or just spawned) |
| 204 | DELETE success (remove, clear, unload, cancel TTS with no body) |
| 401 | Bad/missing Bearer |
| 404 | Unknown job / variant / namespace |
| 409 | Illegal state (start while already Processing; reset a non-Failed job; generate with no model loaded) |
| 422 | Pydantic validation or unknown settings key / step id / extra field |
| 503 | FFmpeg missing when the operation requires it; optional for generate-if-unload race |

Domain errors → handler table (do not leak traceback to clients). Unhandled → 500 with generic message + request id.

---

## Boundary rules

Every request body: `model_config = ConfigDict(extra="forbid")`.

- Python `assert` is not validation.
- Partial `PUT /settings/{namespace}` still rejects unknown keys (create/update parity).
- Do not `replace(entity, **body.model_dump())` in routes; call the service with a typed command.
- Responses **never** include transcript `text`, PCM, video bytes, or cookie contents.

### Wire enums (GUI strings, not domain `.name`)

Map in schemas, not in SQLite.

| Domain | Wire |
|--------|------|
| `QualityPreset.P1080` | `1080p` (also `best`, `2160p`, `1440p`, `720p`, `480p`, `360p`, `240p`, `144p`, `lowest`) |
| `AudioFormat.Default` | `default` (and `best`, `lowest`, `low_webm`, `medium_webm`, `standard_webm`, `standard_m4a`, `standard_mp3`, `high_m4a`) |
| `DownloadStatus.Pending` | `Pending` (GUI PascalCase — keep as Phase 0 names) |
| `MediaFormat.MP3` | `MP3` / `WAV` |
| `DeviceType.Auto` | `auto` (`cuda`, `cpu`, `mps`) |
| `SABRMode.Inactive` | `inactive` (`active`, `checking`) |
| `QueueProcessorState.Idle` | `Idle` (`Processing`, `Paused`) |

`DownloadJobOut.speed`: formatted string (`"12.3 MB/s"`) or `null`.  
`DownloadJobOut.eta`: `"M:SS"` or `null`.  
Domain keeps `speed_bps` / `eta_seconds`.

---

## Shared response fragments

### `QueueRuntimeOut`

```python
state: Literal["Idle", "Processing", "Paused"]
current_job_id: str | None
```

### `ErrorEnvelope`

```python
class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, object] | None = None
```

### List envelopes

`GET /downloads` and `GET /transcripts` return **objects**, not bare arrays, so the processor state can ride along. Phase 6 must change `useQuery<DownloadJob[]>` to this envelope ([06-gui.md](06-gui.md) poll snippet).

```json
{
  "items": [ /* job outs */ ],
  "processor": { "state": "Idle", "current_job_id": null }
}
```

---

## Routes — Downloads

Static paths first.

| Method | Path | Service | Success | Notes |
|--------|------|---------|---------|-------|
| `POST` | `/downloads` | `add_to_queue` | 201 `{ items }` | Body: url, quality, audio_only, audio_format |
| `GET` | `/downloads` | `get_queue` + `get_processor_state` | 200 envelope | Poll 1s / 5s (GUI) |
| `GET` | `/downloads/sabr` | `get_sabr_status` | 200 | Session; does **not** run a check |
| `POST` | `/downloads/sabr/check` | `check_sabr` | 200 `SABRStatusOut` | Test extract |
| `POST` | `/downloads/sabr/force` | `force_sabr` | 200 | |
| `POST` | `/downloads/sabr/clear` | `clear_sabr` | 200 | |
| `POST` | `/downloads/cookies/test` | `test_cookies` | 200 `{ ok: true }` | Body: mode, browser?, profile?, cookie_file? — no cookie bytes back |
| `POST` | `/downloads/start` | `start_processing` | 202 | 409 if already Processing |
| `POST` | `/downloads/pause` | `pause_processing` | 202 | **Added** (was GUI-only) |
| `POST` | `/downloads/resume` | `resume_processing` | 202 | **Added** |
| `POST` | `/downloads/cancel` | `cancel_processing` | 202 | **Added** |
| `POST` | `/downloads/stop` | `cancel_processing` | 202 | Alias of cancel (old stub + MCP `avkit_download_stop`) |
| `PUT` | `/downloads/reorder` | `reorder_queue` | 200 `{ items }` | `{ "job_ids": ["…"] }` permutation |
| `DELETE` | `/downloads` | `clear_queue` | 204 | Jobs only; archive stays |
| `GET` | `/downloads/{id}` | `get_job` | 200 | |
| `POST` | `/downloads/{id}/reset` | `reset_failed` | 200 | 409 if not Failed |
| `DELETE` | `/downloads/{id}` | `remove_from_queue` | 204 | Files stay |
| `POST` | `/downloads/apply-defaults` | `apply_defaults_to_pending` | 200 `{ updated: int }` | Pending / QualityBlocked only |

### `DownloadCreateIn`

`url: str` (min 1), `quality: QualityWire`, `audio_only: bool = False`, `audio_format: AudioWire = "default"`. Extra forbid.

### `DownloadJobOut`

`id`, `url`, `video_id`, `title`, `quality` (wire), `audio_only`, `audio_format` (wire), `status`, `progress` (0–1), `speed` (str\|null), `eta` (str\|null), `file_size` (int\|null), `file_path` (str\|null), `error_message` (str\|null), `queue_position`, `created_at` (ISO-8601).

No `Paused` status. Processor is on the list envelope.

### `SABRStatusOut`

`mode`, `source` (`detected`\|`forced`\|null), `checked_at` (ISO\|null).

---

## Routes — Transcripts

| Method | Path | Service | Success | Notes |
|--------|------|---------|---------|-------|
| `POST` | `/transcripts` | `add_channel` | 201 `TranscriptJobOut` | `{ "channel_url": "…" }` |
| `GET` | `/transcripts` | `get_queue` + processor | 200 envelope | |
| `POST` | `/transcripts/start` | `start_processing` | 202 | |
| `POST` | `/transcripts/pause` | `pause_processing` | 202 | |
| `POST` | `/transcripts/resume` | `resume_processing` | 202 | |
| `POST` | `/transcripts/stop` | `stop_processing` | 202 | Parent → `Cancelled` (Phase 3) |
| `POST` | `/transcripts/{id}/requeue` | `requeue_channel` | 200 `TranscriptJobOut` | 409 if not `Cancelled` |
| `POST` | `/transcripts/{id}/retry` | `retry_failed_channel` | 200 `TranscriptJobOut` | 409 if not `Failed` |
| `PUT` | `/transcripts/reorder` | `reorder_queue` | 200 envelope | **Added** |
| `GET` | `/transcripts/{id}` | `get_job` | 200 | **Added** — includes aggregates |
| `DELETE` | `/transcripts/{id}` | `remove_channel` | 204 | **Added** — files stay |
| `POST` | `/transcripts/{id}/compile` | `compile_channel` | 200 `{ compiled_paths: str[] }` | |

No per-video item routes. Progress fields on the job out are enough for cards.

### `TranscriptJobOut`

`id`, `channel_url`, `channel_name`, `status` (`Pending`\|`Processing`\|`Done`\|`Failed`\|`Paused`\|`Cancelled`), `output_dir`, `video_count`, `transcripts_done` (from `progress_counts`), `word_count`, `zip_path` (str\|null), `last_title` (str\|null), `last_item_status` (str\|null), `queue_position`, `error_message`, `created_at`, `updated_at`.

Do **not** return `video_ids`, `processed_ids`, or transcript bodies. `transcripts_done` is `COUNT(items WHERE status=Done)`, not `progress.json`.

Optional nested `items: list[TranscriptItemOut]` only on `GET /{id}` if the GUI needs last-title without extra fields — prefer the denormalized `last_*` fields so list stays small.

### `TranscriptItemOut` (detail only, if included)

`video_id`, `title`, `language`, `word_count`, `path`, `status`, `error_message`, `processed_at`. No `text`.

---

## Routes — TTS

| Method | Path | Service | Success | Notes |
|--------|------|---------|---------|-------|
| `POST` | `/tts/prepare` | `TTSService.prepare` | 200 `{ cleaned_text }` | **Added** — no job row |
| `POST` | `/tts/generate` | `generate` | 201 `TTSJobOut` | Starts worker |
| `GET` | `/tts/voices` | `TTSPort.list_voices` via TTS or model service | 200 `{ items }` | |
| `GET` | `/tts/{id}` | `get_status` | 200 | Poll segments |
| `DELETE` | `/tts/{id}` | `cancel` | 204 | |

### `TTSPrepareIn`

`text: str`, `enabled_steps: list[str]` (known ids only), optional `chunk_max_chars: int`. Extra forbid. Unknown step → 422.

### `TTSGenerateIn`

`text: str` (min 1), `voice: str`, `speed: float` (0.5–2.0), `format: Literal["MP3","WAV"]`, `enabled_steps: list[str]`, `source_kind: Literal["inline","file"] = "inline"`, `source_path: str | None = None`. Extra forbid. `source_path` is metadata (filename for the card); the backend **must not** open it. File-load belongs to Electron.

201 even though work continues — client polls `GET /tts/{id}`. 409 if no model loaded.

### `TTSJobOut`

`id`, `source_kind`, `source_path`, `text_hash`, `text_preview`, `voice`, `speed`, `format`, `status`, `output_path`, `segments_total`, `segments_done`, `error_message`, `created_at`. **No full text.**

### `VoiceOut`

`voice_id`, `language`, `gender`, `style_description`. Do **not** expose `lang_code` as a user-set field (GUI auto-selects).

---

## Routes — Models

| Method | Path | Service | Success |
|--------|------|---------|---------|
| `GET` | `/models/available` | `list_available` | 200 `{ items: ModelVariantOut[] }` |
| `GET` | `/models/downloaded` | `list_downloaded` | 200 `{ items }` |
| `POST` | `/models/download` | `download` | 202 `{ variant }` | Body `{ "variant_id": "kokoro-onnx-fp16" }`. 409 if another download is in flight |
| `POST` | `/models/load` | `load` | 200 `ModelStatusOut` | `{ "variant_id", "device": "auto"\|"cuda"\|"cpu"\|"mps" }` |
| `POST` | `/models/unload` | `unload` | 204 | |
| `GET` | `/models/status` | `get_status` | 200 `ModelStatusOut` | Loaded model only |
| `GET` | `/models/download-runtime` | `get_download_runtime` | 200 `ModelDownloadRuntimeOut` | Session; poll 1s while `Downloading` |

### `ModelVariantOut`

`id`, `name`, `format`, `precision`, `size_bytes`, `path`, `is_downloaded`. No `is_loaded` on the variant (that is `ModelStatusOut`).

### `ModelStatusOut`

`variant_id`, `name`, `device`, `memory_bytes`, `is_loaded`. **No** download percent here.

### `ModelDownloadRuntimeOut`

`variant_id` (str\|null), `state` (`Idle`\|`Downloading`\|`Failed`), `fraction` (0–1), `error_message` (str\|null).

---

## Routes — Settings

| Method | Path | Service | Success |
|--------|------|---------|---------|
| `GET` | `/settings/{namespace}` | `get_namespace` | 200 object of **leaf keys** |
| `PUT` | `/settings/{namespace}` | `set_namespace` | 200 same shape |

`namespace` ∈ `downloader` \| `transcript` \| `tts` \| `app` \| `ui` \| **`converter` (Phase 8)** \| **`capture` (Phase 9)**. Else 404. Conversion keys: [08-video-conversion.md](08-video-conversion.md). Capture keys: [09-screenshot-capture.md](09-screenshot-capture.md).

PUT body: leaf keys only (`quality`, not `downloader.quality`). Extra forbid; unknown key → 422. Types per [06-gui.md Settings](06-gui.md). Response is the full namespace with defaults filled.

`tts.input_text` is the editor draft. Cap size in the schema (e.g. 1_000_000 chars) so a PUT cannot dump a novel into SQLite without bound.

Cookie **path** / browser name allowed. Cookie file **contents** forbidden.

`ui.rail.collapsed` / `ui.panel.console.height` may be electron-store in the GUI; if PUT is unused for those, still accept them if sent (one owner — document in implementation: Electron persist wins for geometry).

---

## Routes — Health

| Method | Path | Auth | Service | Success |
|--------|------|------|---------|---------|
| `GET` | `/health` | **no** | `liveness` | 200 `{ "status": "ok" }` |
| `GET` | `/health/dependencies` | yes | `dependencies` | 200 `{ "yt_dlp": { version, available }, "ffmpeg": { version, available, path } }` |
| `GET` | `/health/console` | yes | `console_snapshot` | 200 `{ items: ConsoleEventOut[], last_seq: int }` | Query `after_seq` (default 0). **Not SSE.** Poll when the console is expanded |

`ConsoleEventOut`: `seq` (int), `ts` (ISO-8601), `level` (`DEBUG`\|`INFO`\|`WARNING`\|`ERROR`\|`CRITICAL`), `module` (`download`\|`transcript`\|`tts`\|`models`\|`yt-dlp`\|`convert`\|`capture`\|…), `message` (redacted).
| `POST` | `/health/startup-metrics` | yes | `record_startup_metric` | 204 | Body `{ "key": "startup.window_show_ms", "value_ms": 640 }` — log only |

---

## Routes — Conversions (Phase 8)

Canonical table, bodies, and GPU session: [08-video-conversion.md](08-video-conversion.md). Listed in the full index below. **Not** in MEU-15/16.

---

## Routes — Captures (Phase 9)

Canonical table, bodies, image GET, and interactive requests: [09-screenshot-capture.md](09-screenshot-capture.md). Listed in the full index below. **Not** in MEU-15/16.

---

## Full route index (authoritative)

| Method | Path |
|--------|------|
| POST | `/api/v1/downloads` |
| GET | `/api/v1/downloads` |
| GET | `/api/v1/downloads/sabr` |
| POST | `/api/v1/downloads/sabr/check` |
| POST | `/api/v1/downloads/sabr/force` |
| POST | `/api/v1/downloads/sabr/clear` |
| POST | `/api/v1/downloads/cookies/test` |
| POST | `/api/v1/downloads/start` |
| POST | `/api/v1/downloads/pause` |
| POST | `/api/v1/downloads/resume` |
| POST | `/api/v1/downloads/cancel` |
| POST | `/api/v1/downloads/stop` |
| POST | `/api/v1/downloads/apply-defaults` |
| PUT | `/api/v1/downloads/reorder` |
| DELETE | `/api/v1/downloads` |
| GET | `/api/v1/downloads/{id}` |
| POST | `/api/v1/downloads/{id}/reset` |
| DELETE | `/api/v1/downloads/{id}` |
| POST | `/api/v1/transcripts` |
| GET | `/api/v1/transcripts` |
| POST | `/api/v1/transcripts/start` |
| POST | `/api/v1/transcripts/pause` |
| POST | `/api/v1/transcripts/resume` |
| POST | `/api/v1/transcripts/stop` |
| PUT | `/api/v1/transcripts/reorder` |
| GET | `/api/v1/transcripts/{id}` |
| DELETE | `/api/v1/transcripts/{id}` |
| POST | `/api/v1/transcripts/{id}/compile` |
| POST | `/api/v1/transcripts/{id}/requeue` |
| POST | `/api/v1/transcripts/{id}/retry` |
| POST | `/api/v1/tts/prepare` |
| POST | `/api/v1/tts/generate` |
| GET | `/api/v1/tts/voices` |
| GET | `/api/v1/tts/{id}` |
| DELETE | `/api/v1/tts/{id}` |
| GET | `/api/v1/models/available` |
| GET | `/api/v1/models/downloaded` |
| POST | `/api/v1/models/download` |
| POST | `/api/v1/models/load` |
| POST | `/api/v1/models/unload` |
| GET | `/api/v1/models/status` |
| GET | `/api/v1/models/download-runtime` |
| GET | `/api/v1/settings/{namespace}` |
| PUT | `/api/v1/settings/{namespace}` |
| GET | `/api/v1/health` |
| GET | `/api/v1/health/dependencies` |
| GET | `/api/v1/health/console` |
| POST | `/api/v1/health/startup-metrics` |
| POST | `/api/v1/conversions` |
| GET | `/api/v1/conversions` |
| GET | `/api/v1/conversions/gpu` |
| POST | `/api/v1/conversions/gpu/refresh` |
| POST | `/api/v1/conversions/start` |
| POST | `/api/v1/conversions/pause` |
| POST | `/api/v1/conversions/resume` |
| POST | `/api/v1/conversions/cancel` |
| PUT | `/api/v1/conversions/reorder` |
| DELETE | `/api/v1/conversions` |
| GET | `/api/v1/conversions/{id}` |
| POST | `/api/v1/conversions/{id}/reset` |
| DELETE | `/api/v1/conversions/{id}` |
| GET | `/api/v1/captures` |
| POST | `/api/v1/captures` |
| GET | `/api/v1/captures/requests` |
| POST | `/api/v1/captures/requests` |
| POST | `/api/v1/captures/requests/{id}/complete` |
| POST | `/api/v1/captures/requests/{id}/cancel` |
| GET | `/api/v1/captures/{id}` |
| GET | `/api/v1/captures/{id}/image` |
| POST | `/api/v1/captures/{id}/annotate` |
| DELETE | `/api/v1/captures/{id}` |

Phase 4 MEU-14–16 do **not** implement `/conversions` or `/captures`. Those routes are Phase 8 ([08-video-conversion.md](08-video-conversion.md) §REST) and Phase 9 ([09-screenshot-capture.md](09-screenshot-capture.md) §REST). This index lists them so MCP/GUI have one authoritative path list.

≥ **1 contract test per route** ([testing-strategy](../../.agent/docs/testing-strategy.md)).

---

## OpenAPI

FastAPI autogen at `/openapi.json`. Title `av-kit`, version from package. Schemas must match this file. MCP and GUI consume these names — do not alias silently.

---

<a id="unhandled-errors-residual"></a>

## Unhandled errors (residual)

> **MEU-76.** Registered 2026-10-09 from `API-UNHANDLED-ERROR-OPAQUE` (widened by `TTS-MODEL-FLOW-GAPS`). `errors.py:96-106` drops the exception and returns `internal_error` with only a request id, and logs nothing. That 500 also carries no `Access-Control-Allow-Origin` (Starlette runs the `Exception` handler in `ServerErrorMiddleware`, outside `CORSMiddleware`; local probe on Starlette 1.6.0, 2026-10-09), so the renderer's fetch rejects and the GUI shows "Failed to fetch". yt-dlp `DownloadError` on download add (`services/download.py:176-177`) is one common source.

| Rule | Contract | Source |
|------|----------|--------|
| Logged | Every unhandled exception is logged once with `request_id`, route and traceback through the structlog logger; the client still receives no traceback | Triage D-45; Local Canon AGENTS §Code Quality; §Status mapping above |
| CORS-safe 500 | Unhandled errors are converted to the `internal_error` envelope inside the CORS layer, so the 500 carries the CORS headers and the GUI shows the message and request id instead of "Failed to fetch" | Triage D-67; Local Canon G15 |
| Extractor failures | yt-dlp extract failures on download add raise `ExtractError` (a `DomainError`), which maps to 422 with its message in the envelope | Triage D-45; Session 33 plan D-15 |
| Tests | Contract test: a route raising a bare exception returns 500 with `Access-Control-Allow-Origin` for an allowed origin and writes one log line; download add with a failing extractor returns the mapped error | Local Canon |

---

## What this layer must not do

| Forbidden | Why |
|-----------|-----|
| SSE / websocket progress | Deferred ([06-gui.md](06-gui.md)); poll GET |
| Return transcript text or media bytes | Files on disk. **Exception:** `GET /captures/{id}/image` is Phase 9 ([09-screenshot-capture.md](09-screenshot-capture.md)) |
| Persist SABR or processor in a new table | Session on the service |
| Accept cookie file **contents** | Path only |
| Bare `GET /downloads` array without processor | GUI needs queue state; use envelope |
| Business rules in routes | Services own transitions |
| Import SQLAlchemy / yt-dlp | Ports + services |
| `/downloads/stop` meaning something other than cancel | Phase 3 alias |

---

## Downstream planning notes

| Phase | Must follow this spec |
|-------|------------------------|
| **5 MCP** | `fetch` these paths. `avkit_download_stop` → `POST /downloads/stop`. Add tools later for pause/SABR/prepare if agents need them; do not invent parallel URLs |
| **6 GUI** | (1) Poll envelopes `{ items, processor }` not raw arrays. (2) Call pause/resume/cancel/SABR/prepare/cookies/test as above. (3) `apiFetch` base includes `/api/v1`. (4) Amend `progress.json` SoT copy (Phase 1) — cards use `transcripts_done` from this API |

---

## Testing (Phase 4)

`TestClient` + **fake services** (not live yt-dlp):

| Case | Assert |
|------|--------|
| Extra field on any POST/PUT | 422 |
| Missing Bearer on `/downloads` | 401 |
| `GET /health` without Bearer | 200 |
| Add download | 201; quality `1080p` round-trips |
| Reset non-failed | 409 |
| Unknown job | 404 |
| Settings unknown key | 422 |
| Prepare unknown step | 422 |
| Generate response has `text_preview`, not `text` |
| Compile 200 paths only |
| OpenAPI lists every row in the index |

---

## Validation commands

Registered exact-receipt forms live in [`.agent/docs/commands.md`](../../.agent/docs/commands.md). Targeted:

```bash
uv run pytest tests/e2e/ -x --tb=short -v
uv run pyright packages/api/
uv run ruff check packages/api/
```
