---
project: "2026-08-19-p4-rest-api"
date: "2026-08-19"
source: "docs/build-plan/04-rest-api.md"
meus: ["MEU-14", "MEU-15", "MEU-16"]
status: "approved"
template_version: "2.0"
---

# Implementation Plan: Phase 4 REST API

> **Project**: `2026-08-19-p4-rest-api`
> **Build Plan Section(s)**: [04-rest-api.md](../../../build-plan/04-rest-api.md)
> **Status**: `approved`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 5 — MEU-14 → MEU-15 → MEU-16

---

## Goal

Expose approved Phase 3 services over FastAPI on `/api/v1`. One route → one service method. Pydantic is the boundary owner (`extra="forbid"`). Dual Bearer (GUI nonce + MCP token). ErrorEnvelope on every error. List envelopes `{ items, processor }`. OpenAPI committed.

Do not invent job types, tables, or session persistence. Do not rewrite Session 2 UoW, Session 3 adapters, or Session 4 service machines except the three named core locks (`TTS_NO_MODEL_CONFLICT`, `CONSOLE_LEVEL_FROM_METHOD`, `VOICES_FACADE`). Routes never import SQLAlchemy / yt-dlp. Default tests use `TestClient` + fake services. One G29 real-UoW smoke constructs the composition root (no live YouTube / HF / Kokoro).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json still absent; Headroom has no approved disposition. Execution uses exact-evidence receipts (bypass class)."
  human_message_reference: null
```

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-14 | `.agent/context/handoffs/2026-08-19-p4-rest-api-MEU-14-handoff.md` |
| MEU-15 | `.agent/context/handoffs/2026-08-19-p4-rest-api-MEU-15-handoff.md` |
| MEU-16 | `.agent/context/handoffs/2026-08-19-p4-rest-api-MEU-16-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-19-p4-rest-api-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-14a | Scaffold `packages/api` + workspace + FastAPI deps | — | `shared` | `packages/api/pyproject.toml`; `uv.lock` |
| WP-14b | MEU-14 Red: auth / envelope / health liveness / `CONSOLE_LEVEL_FROM_METHOD` (AC-14.9) | WP-14a | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-14-auth.txt` |
| WP-14c | MEU-14 Green: `create_app`, auth, errors, request-id, CORS, lifespan, `CONSOLE_LEVEL_FROM_METHOD` | WP-14b | `compact_continue` | `avkit_api/main.py`; compact then re-read `task.md` |
| WP-14d | MEU-14 `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-14c | `compact_continue` | `.agent/context/handoffs/2026-08-19-p4-rest-api-MEU-14-handoff.md`; `C:/Temp/av-kit/handoff-source-read.txt` |
| WP-15a | MEU-15 Red: downloads + SABR + cookies + apply-defaults | WP-14d | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-15-downloads.txt` |
| WP-15b | MEU-15 Green: downloads router + formatters | WP-15a | `compact_continue` | `avkit_api/routes/downloads.py` |
| WP-15c | MEU-15 Red: settings + remaining health | WP-15b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-15-settings.txt` |
| WP-15d | MEU-15 Green: settings + health routers | WP-15c | `compact_continue` | `avkit_api/routes/settings.py`; `health.py` |
| WP-15e | MEU-15 `MEU_SCOPED_GATE` (reuse `HANDOFF_SOURCE_READ`) + canonical handoff | WP-15d | `compact_continue` | `.agent/context/handoffs/2026-08-19-p4-rest-api-MEU-15-handoff.md` |
| WP-16a | MEU-16 Red: transcripts | WP-15e | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-16-transcripts.txt` |
| WP-16b | MEU-16 Green: transcripts router + aggregates | WP-16a | `compact_continue` | `avkit_api/routes/transcripts.py` |
| WP-16c | MEU-16 Red: TTS + models + OpenAPI census | WP-16b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-16-tts.txt` |
| WP-16d | MEU-16 Green: TTS/models + `TTS_NO_MODEL_CONFLICT` + `VOICES_FACADE` + `export_openapi.py` | WP-16c | `compact_continue` | `avkit_api/routes/tts.py`; `models.py`; `tools/export_openapi.py`; `openapi.committed.json` |
| WP-16e | MEU-16 `MEU_SCOPED_GATE` + `BODY_ROUTES` extra oracle + canonical handoff | WP-16d | `compact_continue` | `.agent/context/handoffs/2026-08-19-p4-rest-api-MEU-16-handoff.md` |

---

## User Review Required

None that block planning. Product forks below are sourced in Implementation locks (reviewer confirms the lock, does not invent a second behavior).

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `API_PREFIX` | `/api/v1` | Spec Package layout |
| `BIND_HOST` | `127.0.0.1` (documented; `create_app` does **not** call uvicorn — spawn is MEU-19/24) | Spec Package layout |
| `API_LAYOUT` | `packages/api/src/avkit_api/{main,dependencies,auth,errors,wiring}.py` + `schemas/{common,downloads,transcripts,tts,models,settings,health}.py` + `routes/{downloads,transcripts,tts,models,settings,health}.py` + `formatters.py` | Spec Package layout |
| `AUTH_EXEMPT_PATHS` | `{GET /api/v1/health}` only | Spec Auth |
| `AUTH_TOKENS` | `frozenset[str]` passed to `create_app`; both GUI nonce and MCP key are members; empty/blank tokens rejected at factory | Spec Auth; FastAPI `secrets.compare_digest` |
| `CORS_ORIGIN_REGEX` | `^https?://(localhost\|127\.0\.0\.1)(:\d+)?$` — no `allow_origins=["*"]` | Spec CORS; [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/) |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Spec Middleware |
| `ERROR_ENVELOPE` | `{ "error": { "code": str, "message": str, "details": object \| null } }` | Spec ErrorEnvelope |
| `DOMAIN_HTTP_MAP` | `ValidationError`/`CookieTestError`/`AgeRestrictedError` → 422; `NotFoundError` → 404; `ConflictError` → 409; `FFmpegNotFoundError`/`SpacyModelNotFoundError` → 503; other `DomainError` / unhandled → 500 generic + request id | Spec Status mapping; p3 HTTP lock |
| `START_IF_PROCESSING` | Before `start_processing`, if `get_processor_state().state is Processing` → 409. Do **not** change `DownloadService.start_processing` (idempotent no-op). Transcript already raises `ConflictError`. | Spec 409; frozen download.py:249–252 |
| `SETTINGS_UI_API_KEYS` | `{theme}` — `ui.rail.collapsed` / `ui.panel.console.height` are unknown leaves → 422 | p3 approved lock; Phase 1 key-without-`.` |
| `SETTING_NAMESPACES` | `downloader`, `transcript`, `tts`, `app`, `ui` — unknown namespace → **404** at the route before `set_namespace` | Spec Settings; frozen `settings.py` |
| `SETTINGS_KEY_TABLE` | frozen Session 4 table (no dotted `ui.*`) | p3 plan |
| `TTS_INPUT_TEXT_MAX` | `1000000` | Spec Settings cap |
| `TTS_SPEED_MIN` / `TTS_SPEED_MAX` | `0.5` / `2.0` | frozen `tts.py`; Spec TTSGenerateIn |
| `PREPARE_STEP_IDS` | p3 named set | p3 plan |
| `QUALITY_WIRE_MAP` / `AUDIO_WIRE_MAP` / `DEVICE_WIRE_MAP` | frozen `domain/wire.py` — jobs store enums; schemas emit/accept wire strings | Spec Wire enums |
| `SABR_WIRE_MAP` | `Inactive→inactive`, `Active→active`, `Checking→checking`; `Detected→detected`, `Forced→forced` | Spec 126–127 vs frozen StrEnum values `Inactive`/`Detected` |
| `QUEUE_RUNTIME_WIRE` | `Idle`/`Processing`/`Paused` (enum `.value`) | Spec QueueRuntimeOut |
| `ROUTE_INDEX` | the 48 rows in `04-rest-api.md` “Full route index” | Spec 327–378 |
| `STATIC_BEFORE_ID` | downloads: `sabr`, `cookies`, `start`, `pause`, `resume`, `cancel`, `stop`, `apply-defaults`, `reorder` before `/{id}`; tts: `prepare`, `generate`, `voices` before `/{id}`; models: `available`, `downloaded`, `download`, `load`, `unload`, `status`, `download-runtime` (no `{id}`) | Spec factory step 4 |
| `FORBIDDEN_BODY_FIELDS` | transcript `text`, PCM, video bytes, cookie contents, `video_ids`, `processed_ids`, `lang_code` as user-set | Spec Boundary + TranscriptJobOut |
| `LIST_ENVELOPE` | `{ "items": [...], "processor": { "state", "current_job_id" } }` for GET `/downloads` and GET `/transcripts` | Spec List envelopes |
| `TTS_NO_MODEL_CONFLICT` | `TTSService.generate` raises `ConflictError` (not `ValidationError`) when no model is loaded | Spec 409; p3 “illegal state → ConflictError” |
| `VOICES_FACADE` | Public `TTSService.list_voices() -> list[VoiceConfig]` delegates to `TTSPort.list_voices` (read-only; no Protocol/machine edit). `GET /tts/voices` calls **only** this method and returns `{ items: VoiceOut[] }`. | Spec 243–247; frozen `TTSPort.list_voices`; F1 |
| `BODY_ROUTES` | Every `POST`/`PUT` in `ROUTE_INDEX` (including `PUT /transcripts/reorder`). Parametrized extra-field oracle: each → 422 `ERROR_ENVELOPE`. | Spec 107, 420; AGENTS Boundary Input Contract; F2 |
| `CONSOLE_LEVEL_FROM_METHOD` | `ConsoleEvent.level` = `method_name.upper()` if in `LOG_LEVEL_WIRES` else `INFO` | Spec ConsoleEventOut vs frozen VO missing `level` |
| `HANDOFF_COUNT` | `3` | `HANDOFF_GLOB` |
| `HEALTH_DEPS_PATH` | `ffmpeg.path` = `settings.get("downloader","ffmpeg_path")` or `null` if empty; `available` = version is not `None` | Spec Health; `MediaPort` has no path method |
| `COOKIE_TEST_OUT` | 200 `{ "ok": bool }` — never cookie bytes / `error_message`; `CookieTestError` → 422 | Spec cookies/test; RULE-2 |
| `SPEED_FORMAT` | `None` → `null`; else `{value:.1f} {unit}/s` with SI 1000 (`B`, `KB`, `MB`, `GB`) | Spec example `"12.3 MB/s"` |
| `ETA_FORMAT` | `None` → `null`; else `f"{m}:{s:02d}"` from `eta_seconds` (`m` may exceed 59) | Spec `"M:SS"` |
| `ISO_Z` | naive datetimes emit `…Z`; aware emit offset ISO-8601 | Spec ISO-8601 |
| `OPENAPI_COMMITTED` | repo-root `openapi.committed.json` | G8; create-plan Step 6 |
| `EXPORT_OPENAPI` | `tools/export_openapi.py` (`--check` then `-o`) — **created this session** (absent today) | G8 |
| `TEST_API` | `tests/e2e/test_api_*.py` | Spec Testing; testing-strategy `tests/e2e/` |
| `TEST_API_WIRING` | `tests/integration/test_api_wiring.py` | G29 |
| `REGRESSION_TESTS` | Session 1–4 unit/integration files (do not drop) | p3 `REGRESSION_TESTS` + `TEST_SERVICES` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-19-p4-rest-api-MEU-*-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-19-p4-rest-api` | MEU `execution_plan` (no slash) |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-19-p4-rest-api/` | phase `"4"` `execution_plans` |
| `HUB_NEXT_AFTER` | `/create-plan p5-mcp-server` | grouping Session 6 (∥ Session 7 after 5) |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | Codex r3 F1 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-19-p4-rest-api-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only | p2 Human-approved |
| `REFLECTION_MARKERS` | same p3 marker list | completion-preflight |
| `SCAN_G36_ARGS` | `rg` skip/xfail/skip on `TEST_API` + `TEST_API_WIRING` | G36 |
| `SCAN_PLACEHOLDER_ARGS` | `TODO`/`FIXME`/`NotImplementedError` under `packages/api/src` | anti-placeholder |
| `SCAN_API_LIBS_ARGS` | import-anchored `^(from\|import) .*(sqlalchemy\|yt_dlp\|youtube_transcript_api\|huggingface_hub\|soundfile\|onnxruntime\|kokoro)` under `packages/api/src` | hexagonal; p3 import-anchor |
| `SCAN_CORE_INFRA_ARGS` | unchanged p3 import-anchored scan on `packages/core/src` | p3 lock |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read.txt` written in task 4 **before** the first MEU handoff (TEMPLATE path + latest peer path + `PASS: HANDOFF_SOURCE_READ`). Rows 9/14 reuse it. Receipt `LastWriteTime` must be ≤ that MEU handoff’s `LastWriteTime`. | F4; completion-preflight |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE + completion-preflight |
| `SCAN_ANTI_DEFERRAL_ARGS` | `raise NotImplementedError` and `pass.*placeholder` on that MEU’s `MEU*_TOUCHED` | quality-gate #8 |
| `BOUNDARY_AUDIT_ARGS` | quality-gate #11a `dict[str, Any]`; #11b `replace(**` / `__dict__` update; #11c `class …(BaseModel)` except `ApiModel`; #11d `**kwargs` / `**{`. #11a–d run on `packages/api/src`. #11b and #11d **also** include that MEU’s touched core service (`health.py` for MEU-14, `tts.py` for MEU-16). | quality-gate #11; F4 r4 |
| `MEU14_TOUCHED` | `packages/api/src`; `packages/core/src/avkit_core/domain/health.py`; `packages/core/src/avkit_core/services/health.py` | MEU-14 files |
| `MEU15_TOUCHED` | `packages/api/src` | MEU-15 files |
| `MEU16_TOUCHED` | `packages/api/src`; `packages/core/src/avkit_core/services/tts.py`; `tools/export_openapi.py` | MEU-16 files |
| `MEU_SCOPED_GATE` | targeted pytest + pyright + ruff + `SCAN_PLACEHOLDER_ARGS` on `MEU*_TOUCHED` + `SCAN_ANTI_DEFERRAL_ARGS` + `SCAN_API_LIBS_ARGS` + `SCAN_CORE_INFRA_ARGS` when core is touched + `BOUNDARY_AUDIT_ARGS` + `HANDOFF_BUNDLE_MARKERS` + that MEU’s `PER_MEU_HANDOFF_AC`. Task 16 is the project-wide sweep only. | AGENTS MEU gate; F4 |

`ROUTE_INDEX` (define once; ≥1 contract test per row):

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

---

## Implementation locks (planning resolutions)

| Topic | Lock | Source |
|-------|------|--------|
| Package home | New `packages/api` (`avkit_api`). Add to uv workspace, `pythonpath`, pyright `include`, ruff `src`. Deps: `fastapi>=0.115`, `pydantic>=2`, `httpx` (TestClient), `avkit-core`, `avkit-infrastructure`. `uv sync --all-packages`. | Spec layout; architecture.md |
| Hexagonal | `packages/core` still never imports `avkit_infra` or FastAPI. `avkit_api/routes/**` never imports SQLAlchemy / yt-dlp. `wiring.py` **may** import `avkit_infra` (composition root). | Spec “must not”; p3 hexagonal |
| Frozen services | Do not rewrite machines, ports, or UoW. Allowed core edits: `TTS_NO_MODEL_CONFLICT`; `CONSOLE_LEVEL_FROM_METHOD`; `VOICES_FACADE`. | p3 carry-forward; Spec ConsoleEventOut / voices; F1 |
| Factory | `create_app(*, tokens: frozenset[str], services: AppServices \| None = None, engine_dispose: Callable[[], None] \| None = None)`. Empty token set or blank member → `ValueError`. Tests inject fakes. Production `wiring.build_services()` builds UoW + adapters + seven services + shared `ExtractCoordinator`; binds `DOWNLOAD_HOOK_WIRING` (`YouTubeAdapter(on_progress=download.on_download_progress, should_stop=download.should_stop, …)`); `playlist_end` remains adapter ctor from settings. | Spec factory; p3 `DOWNLOAD_HOOK_WIRING` |
| Lifespan | Startup: `transcript.recover_stale_processing()`. Shutdown: `download.cancel_processing()`, `transcript.stop_processing()`, `models.unload()`, `engine_dispose()` if provided. | Spec factory step 5; p3 boot recovery |
| Auth | `HTTPBearer(auto_error=False)`. Missing/unknown → **401** `ERROR_ENVELOPE` + `WWW-Authenticate: Bearer`. Compare with `secrets.compare_digest` against **each** `AUTH_TOKENS` member (FastAPI HTTP Basic pattern). Do not log the token, put it in query strings, or persist it. | Spec Auth; [FastAPI Basic Auth](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/) |
| CORS | `CORSMiddleware(allow_origin_regex=CORS_ORIGIN_REGEX, allow_credentials=True, allow_methods=["*"], allow_headers=["Authorization","Content-Type","X-Request-ID"])`. No `*`. | Spec; FastAPI CORS tutorial |
| Request-ID | Accept or mint UUID4; echo `REQUEST_ID_HEADER`; bind structlog contextvars. 500 `details` may include `request_id` only. | Spec Middleware |
| Extra forbid | Shared `class ApiModel(BaseModel): model_config = ConfigDict(extra="forbid")` for **every** request body. Python `assert` is not validation. | Spec Boundary; Pydantic v2 ConfigDict |
| Typed commands | Routes call service methods with typed args. Do not `replace(entity, **body.model_dump())`. | Spec Boundary |
| Settings PUT | Full mapping through `set_namespace` (one UoW — Session 4 RULE-1). Extra/unknown leaf → 422. Unknown namespace → 404 (`SETTING_NAMESPACES`). `tts.input_text` `Field(max_length=TTS_INPUT_TEXT_MAX)`. Cookie **path** allowed; cookie **bytes** rejected by existing service. | Spec Settings; p3 RULE-1 |
| 04 vs p3 ui geometry | `04-rest-api.md` “still accept rail/panel if sent” **yields** to approved `SETTINGS_UI_API_KEYS` + Phase 1 leaf-without-`.`. Geometry is electron-store (MEU-19/23). | Local Canon p3; 06-gui persist via `usePersistedState` |
| Downloads start 409 | `START_IF_PROCESSING`. Pause/resume/cancel/stop → 202. `POST /stop` == `cancel_processing`. | Spec routes; p3 alias |
| Reset | `reset_failed(job_id)` → 200 or 409 if not Failed (entity already raises `ConflictError`). | Spec; frozen entity |
| Cookie test | Body `mode`, optional `browser`, `profile`, `cookie_file`. Return `COOKIE_TEST_OUT`. | Spec; RULE-2 |
| Formatters | `speed`/`eta` via `SPEED_FORMAT`/`ETA_FORMAT`. Quality/audio/device via wire maps. Status PascalCase `.value`. SABR via `SABR_WIRE_MAP`. | Spec Wire enums |
| Transcript aggregates | `transcripts_done` = count of items with `Done`. `last_title` / `last_item_status` from the item with latest `processed_at` (else last in `list_items` order). No nested `items` array. Never `video_ids` / bodies. | Spec TranscriptJobOut; frozen entity has no last_* columns |
| TTS prepare | `TTSService.prepare` (not a job row). Unknown step → 422. | Spec; p3 prepare |
| TTS generate | 201 `TTSJobOut` (no full `text`). `source_path` metadata only — **never** `open`/`read_text`. 409 if no model (`TTS_NO_MODEL_CONFLICT`) or in-flight generate (existing `ConflictError`). | Spec; p3 RULE-2/3 |
| Models download | 202 `{ variant }` immediate return (p3 RULE-2). 409 if another download in flight. No service `mkdir`. | Spec; p3 |
| Health liveness | `{ "status": "ok" }` from `HealthLiveness.ok`. No auth. | Spec |
| Health deps | `{ yt_dlp: {version, available}, ffmpeg: {version, available, path} }` with `HEALTH_DEPS_PATH`. Auth required. | Spec |
| Console | Query `after_seq` default 0. 422 if negative/non-int (service already validates). Not SSE. | Spec; Human-approved 2026-08-18 |
| Startup metrics | Body `{ key, value_ms }` → `record_startup_metric`; 204. | Spec |
| OpenAPI | Title `av-kit`; version from `packages/api` package. `/openapi.json` lists every `ROUTE_INDEX` path. `EXPORT_OPENAPI` two-step. | Spec OpenAPI; G8 |
| Tests | Fake services + `TestClient`. One contract assertion per `ROUTE_INDEX` row (parametrized OpenAPI/path census counts). M5/M6/G36. | Spec Testing |
| G29 | `TEST_API_WIRING`: real tmp-SQLite UoW + adapters constructed via `wiring.build_services`; `GET /health` 200; no live network. MCP/GUI layers are MEU-17/19 — not stubs of these routes. | G29; grouping |
| Bind | Do not add a production CLI this session. | MEU-19/24 |
| Emerging skips | M1–M4/M7 MCP; G1–G7/G9–G39 GUI (except G8/G19/G28/G29/G36). Record skip. | emerging-standards adoption filter |

---

## Proposed Changes

### MEU-14 — `api-app-auth`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `Authorization` header | `auth.require_bearer` | `Bearer` + member of `AUTH_TOKENS` | missing/unknown → 401 |
| `GET /health` (no body) | — | — | — |
| Future POST/PUT (scaffold `ApiModel`) | `ApiModel` | — | `extra="forbid"` |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-14.1 | integration | `create_app` registers prefix `API_PREFIX`, title `av-kit`, and stores services on `app.state`. Getters in `dependencies.py` match Spec names. | Spec factory | missing getter → fail |
| AC-14.2 | integration | **Control `AUTH_TOKENS`.** Observable: HTTP status + `ERROR_ENVELOPE.code`. Chain: `HTTPBearer` → `compare_digest` loop → 401 handler. Negative: missing Bearer on `/health/dependencies` → 401; wrong token → 401; `GET /health` without Bearer → 200 `{status:ok}`. Token string does not appear in response body. | Spec Auth | empty token accepted at factory → fail |
| AC-14.3 | integration | **Control `ERROR_ENVELOPE`.** Observable: JSON shape on 401/422/500. Chain: handler table → `errors.py`. Negative: raw FastAPI `{"detail":…}` top-level on 401. | Spec Middleware | — |
| AC-14.4 | integration | **Control `REQUEST_ID_HEADER`.** Observable: response header equals supplied or is UUID4. Chain: middleware → structlog bind. Negative: header dropped. | Spec Middleware | — |
| AC-14.5 | integration | **Control `CORS_ORIGIN_REGEX`.** Observable: `Access-Control-Allow-Origin` on OPTIONS from `http://localhost:5173`. Negative: `https://evil.example` gets no `*`. | Spec CORS; Research-backed FastAPI CORS | — |
| AC-14.6 | unit | Factory rejects empty/blank `tokens` with `ValueError` before routes exist. | Research-backed compare_digest | blank `" "` accepted |
| AC-14.7 | integration | Lifespan startup calls `recover_stale_processing` once; shutdown calls cancel/stop/unload/dispose (fake spies). | Spec factory; p3 boot | never called |
| AC-14.8 | unit | `ApiModel` rejects an unknown field (`extra="forbid"`). Totality across live routes is `BODY_ROUTES` / AC-16.9 (after all routers exist). | Spec Boundary | extra ignored |
| AC-14.9 | unit | **Control `CONSOLE_LEVEL_FROM_METHOD` (processor).** Observable: `ConsoleEvent.level`. Chain: structlog `method_name` → `HealthService._process` (production processor; no HTTP). Negative: `warning` → `WARNING` (not `INFO`); unknown/omitted/`not-a-level` → `INFO`. HTTP envelope is AC-15.13 (console route is MEU-15). | Spec ConsoleEventOut; F3 | hard-coded INFO / edit omitted |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Dual Bearer | Spec | `AUTH_TOKENS` frozenset |
| Timing-safe compare | Research-backed | FastAPI HTTP Basic `secrets.compare_digest` |
| CORS localhost only | Spec + Research-backed | `CORS_ORIGIN_REGEX` |
| uvicorn bind | Spec | documented `BIND_HOST`; no CLI this session |
| Request-ID | Spec | UUID4 mint |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/api/pyproject.toml` | new | package + fastapi deps |
| `pyproject.toml` | modify | workspace member, pythonpath, pyright, ruff |
| `packages/api/src/avkit_api/{main,auth,errors,dependencies,wiring}.py` | new | factory stack |
| `packages/core/src/avkit_core/domain/health.py` | modify | `ConsoleEvent.level` |
| `packages/core/src/avkit_core/services/health.py` | modify | store level from `method_name` |
| `tests/e2e/test_api_auth.py` | new | AC-14.1–14.8 |
| `tests/unit/test_console_level.py` | new | AC-14.9 |

---

### MEU-15 — `api-downloads-health-settings`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `POST /downloads` | `DownloadCreateIn` | url min 1; quality ∈ `QUALITY_WIRE_MAP`; audio_format ∈ `AUDIO_WIRE_MAP` | forbid |
| `PUT /downloads/reorder` | `{ job_ids: list[str] }` | permutation (service validates) | forbid |
| `POST /downloads/cookies/test` | mode ∈ `COOKIE_MODE_WIRES` | path only | forbid |
| `PUT /settings/{namespace}` | leaf mapping | `SETTING_NAMESPACES`; keys ⊆ table; `tts.input_text` ≤ `TTS_INPUT_TEXT_MAX` | forbid |
| `GET /health/console` | query `after_seq: int = 0` | ≥ 0 | — |
| `POST /health/startup-metrics` | `{ key, value_ms }` | key min 1 | forbid |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-15.1 | integration | `POST /downloads` 201 `{ items }`; quality `1080p` round-trips. Extra field → 422. Missing Bearer → 401. | Spec Testing | extra accepted |
| AC-15.2 | integration | `GET /downloads` 200 `LIST_ENVELOPE`. No item `status=Paused`. | Spec DownloadJobOut | bare array |
| AC-15.3 | integration | **Control `START_IF_PROCESSING`.** Observable: 409 envelope when fake processor is Processing. Chain: route → `get_processor_state` → return 409 **without** calling `start_processing`. Negative: start called while Processing. | Spec 409 | — |
| AC-15.4 | integration | pause/resume/cancel/stop → 202; stop calls `cancel_processing`. resume while not Paused → 409. | Spec | stop ≠ cancel |
| AC-15.5 | integration | reset non-Failed → 409; unknown id → 404; DELETE `{id}` 204; DELETE collection 204 (archive stays — fake spy). | Spec | — |
| AC-15.6 | integration | SABR get does not call `check_sabr`. check/force/clear return `SABRStatusOut` via `SABR_WIRE_MAP`. | Spec | get runs check |
| AC-15.7 | integration | cookies/test → `COOKIE_TEST_OUT`; `CookieTestError` → 422; no cookie bytes in body. | Spec; RULE-2 | bytes leaked |
| AC-15.8 | integration | apply-defaults → 200 `{ updated: int }`. | Spec | — |
| AC-15.9 | unit | `SPEED_FORMAT` / `ETA_FORMAT` / `ISO_Z` pure functions. | Spec | `int(nan)` path |
| AC-15.10 | integration | **Control settings boundary.** Observable: status. Chain: route namespace check → `ApiModel` → `set_namespace`. Negative: unknown namespace 404; unknown/`rail` key 422; extra field 422; partial invalid mapping writes nothing (fake UoW commit count 0 — Session 4 RULE-1). | Spec; p3 F2 | rail accepted |
| AC-15.11 | integration | GET namespace returns full defaults-filled object. | Spec | — |
| AC-15.12 | integration | health/dependencies auth + shape; console `after_seq`; startup-metrics 204. | Spec | SSE used |
| AC-15.13 | integration | **Control `CONSOLE_LEVEL_FROM_METHOD` (HTTP).** Observable: `GET /health/console` item `level`. Chain: processor (AC-14.9) → `ConsoleEventOut.level`. Negative: known `warning` event is not `INFO`; unknown method_name is `INFO`. | Spec ConsoleEventOut; F3 | hard-coded INFO |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| ui.rail accept-if-sent | Local Canon overrides thin 04 “may” | `SETTINGS_UI_API_KEYS` |
| start 409 vs idempotent service | Spec + Local Canon | `START_IF_PROCESSING` |
| ffmpeg path | Spec + frozen port | `HEALTH_DEPS_PATH` |
| speed string | Spec + Research-backed SI | `SPEED_FORMAT` |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `avkit_api/routes/{downloads,settings,health}.py` | new | routers |
| `avkit_api/schemas/{downloads,settings,health,common}.py` | new | models |
| `avkit_api/formatters.py` | new | speed/eta/ISO/wire |
| `tests/e2e/test_api_downloads.py` | new | AC-15.1–15.9 |
| `tests/e2e/test_api_health_settings.py` | new | AC-15.10–15.13 |

---

### MEU-16 — `api-transcripts-tts-models`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `POST /transcripts` | `{ channel_url }` | min 1 | forbid |
| `PUT /transcripts/reorder` | `{ job_ids: list[str] }` | permutation (service validates) | forbid |
| `POST /tts/prepare` | `TTSPrepareIn` | steps ⊆ `PREPARE_STEP_IDS` | forbid |
| `POST /tts/generate` | `TTSGenerateIn` | speed ∈ [`TTS_SPEED_MIN`, `TTS_SPEED_MAX`]; format MP3/WAV; source_kind inline/file | forbid |
| `POST /models/download` | `{ variant_id }` | non-empty | forbid |
| `POST /models/load` | `{ variant_id, device }` | device ∈ `DEVICE_WIRE_MAP` | forbid |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-16.1 | integration | POST/GET transcripts envelope; start/pause/resume/stop 202; requeue/retry 409 when not Cancelled/Failed; compile 200 `{ compiled_paths }` only (no text). | Spec | text in body |
| AC-16.2 | integration | Job out has `transcripts_done`/`last_*`; never `video_ids`/`text`. | Spec | ids leaked |
| AC-16.3 | integration | prepare unknown step → 422; generate 201 has `text_preview` not `text`; `source_path` unread (fake filesystem `read_text` count 0). | Spec; p3 | file opened |
| AC-16.4 | integration | **Control `TTS_NO_MODEL_CONFLICT`.** Observable: 409. Chain: `generate` → `ConflictError` → handler. Negative: 422 for “no model loaded”. Overlap generate → 409. | Spec 409; p3 RULE-3 | ValidationError mapped 422 |
| AC-16.5 | integration | models download 202 immediate `{ variant }`; second in-flight 409; runtime poll; load/unload/status. | Spec; p3 RULE-2 | blocking download |
| AC-16.6 | integration | **Control `ROUTE_INDEX`.** Observable: OpenAPI `paths` set == `ROUTE_INDEX`. Chain: `create_app` → `/openapi.json` → census test. Negative: missing path or extra undocumented path. Path census alone does **not** satisfy AC-16.7/`VOICES_FACADE`. | Spec OpenAPI | — |
| AC-16.7 | integration | **Control `VOICES_FACADE`.** Observable: 200 `{ items: VoiceOut[] }` and fake `TTSService.list_voices` call count ≥ 1. Chain: `GET /tts/voices` → public `TTSService.list_voices` → `TTSPort.list_voices`. Negative: OpenAPI path present while public method never called; route reads `_tts`; `lang_code` user-set field. | Spec 243–247; F1 | stub path |
| AC-16.8 | integration | `EXPORT_OPENAPI --check` passes after `-o` once. `STATIC_BEFORE_ID` (Starlette match: `/tts/voices` before `/tts/{id}`). | G8; Spec factory | `{id}` steals `/voices` |
| AC-16.9 | integration | **Control `BODY_ROUTES`.** Observable: 422 `ERROR_ENVELOPE` for an extra field on **every** POST/PUT in `ROUTE_INDEX`. Chain: `ApiModel` → RequestValidationError handler. Negative: any body route returns 2xx with extra key. | Spec 107, 420; F2 | reorder extras ignored |
| AC-16.10 | integration | G29 `TEST_API_WIRING`: real UoW factory constructs; `GET /health` 200. | G29 | ImportError |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| generate no model | Spec 409 vs service ValidationError | `TTS_NO_MODEL_CONFLICT` |
| last_* fields | Spec vs frozen entity | compute from `list_items` |
| OpenAPI tool missing | Local Canon G8 | create `EXPORT_OPENAPI` |
| nested items | Spec optional | omit (prefer last_*) |
| `/tts/voices` producer | Spec + frozen `TTSPort` | `VOICES_FACADE` |
| extra-field totality | Spec + Boundary Input Contract | `BODY_ROUTES` |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `avkit_api/routes/{transcripts,tts,models}.py` | new | routers |
| `avkit_api/schemas/{transcripts,tts,models}.py` | new | models |
| `packages/core/src/avkit_core/services/tts.py` | modify | `TTS_NO_MODEL_CONFLICT` + `VOICES_FACADE` |
| `tools/export_openapi.py` | new | `--check` / `-o` |
| `openapi.committed.json` | new | committed spec |
| `tests/e2e/test_api_transcripts.py` | new | AC-16.1–16.2 |
| `tests/e2e/test_api_tts_models.py` | new | AC-16.3–16.5, AC-16.7 |
| `tests/e2e/test_api_openapi.py` | new | AC-16.6, AC-16.8 |
| `tests/e2e/test_api_bodies.py` | new | AC-16.9 `BODY_ROUTES` |
| `tests/integration/test_api_wiring.py` | new | AC-16.10 |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| SSE / websocket progress | out-of-scope | — | `04-rest-api.md` 393–394; Human-approved 2026-08-18 |
| MCP runtime / `AVKIT_API_TOKEN` spawn / discovery | deferred | MEU-17 | grouping Session 6; `meu-status.yaml` MEU-17 |
| MCP compound tools (`avkit_*`) | deferred | MEU-18 | grouping Session 6; `meu-status.yaml` MEU-18 |
| Electron `PythonManager --token` / Vite host | deferred | MEU-19 | grouping Session 7; Spec BIND spawn |
| GUI pages / `apiFetch` | deferred | MEU-20–23 | grouping Sessions 8–11 |
| NSIS / uvicorn production CLI / FFmpeg bundle | deferred | MEU-24, MEU-25 | grouping Session 12 |
| OCR / multi-file TTS / ConversionJob GUI / MCP Guard | out-of-scope | — | grouping “Named deferrals are not MEUs”; matrix deferred list |
| Rewrite adapters / ports / Session 4 machines (except the three named core locks) | out-of-scope | — | p3 approved carry-forward; grouping Session 5 |
| Accept `ui.rail.*` / `ui.panel.*` via API | out-of-scope | — | p3 `SETTINGS_UI_API_KEYS`; Phase 1 key-without-`.`; 06-gui electron-store persist |
| Live YouTube / HF / Kokoro in default suite | out-of-scope | — | Spec Testing “fake services” |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-14/15/16 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"4"`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 1–4 plan links. Do not hand-edit AUTOGEN tables — `meu_status.py render`.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p4-rest-api'; SLASH=PLAN+'/'; NEXT='/create-plan p5-mcp-server'; MEUS=('MEU-14','MEU-15','MEU-16'); data=load(); p4=next(p for p in data['phases'] if str(p['id'])=='4'); eps=list(p4.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 4 missing PLAN_FOLDER_SLASH'); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

> Classify every command through [`.agent/docs/output-evidence-policy.md`](../../../.agent/docs/output-evidence-policy.md).

### 1. API + regression tests

```powershell
rtk proxy uv run pytest tests/e2e tests/integration/test_api_wiring.py tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py -x --tb=short -v *> C:/Temp/av-kit/pytest-p4.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p4.txt | Select-Object -Last 40; exit $code
```

### 2. Types / lint

```powershell
rtk proxy uv run pyright packages/core/ packages/api/ *> C:/Temp/av-kit/pyright-p4.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/pyright-p4.txt | Select-Object -Last 40; exit $code }; rtk proxy uv run ruff check packages/core/ packages/api/ *> C:/Temp/av-kit/ruff-p4.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ruff-p4.txt | Select-Object -Last 40; exit $code
```

### 3. OpenAPI drift (G8)

```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

### 4. Scans

`SCAN_G36_ARGS`, `SCAN_PLACEHOLDER_ARGS`, `SCAN_API_LIBS_ARGS`, `SCAN_CORE_INFRA_ARGS` — rg exit 1 = clean PASS (p3 import-anchor pattern). Task rows 4/9/14 also run `SCAN_ANTI_DEFERRAL_ARGS` and `BOUNDARY_AUDIT_ARGS` on `MEU*_TOUCHED`. Task 16 remains the project-wide sweep.

### N. `CHECK_EXEC_REVIEW`

Same first-frontmatter checker as Session 4 against `EXEC_REVIEW_FILE` / `EXEC_REVIEW_TARGET`.

---

## Open Questions

None `Human-decision-required`. Sourced forks (reviewer confirms locks):

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| CORS allow list vs regex | Explicit 5173/3000 only | FastAPI CORS tutorial | Simple | Vite port drift | ⚠️ |
| | `CORS_ORIGIN_REGEX` localhost/127.0.0.1 | Spec “localhost only, no wildcard”; FastAPI `allow_origin_regex` | Covers Electron/Vite ports | Broader than one port | ✅ |
| ui.rail via API | Accept and persist | 04 line 310 “still accept if sent” | Matches 06 table rows | Breaks Phase 1 leaf-without-`.`; rewrites SETTINGS_KEY_TABLE | ❌ |
| | Reject 422 | p3 `SETTINGS_UI_API_KEYS`; 06-gui `usePersistedState` | One owner per key | 04 “may” unused | ✅ |
| generate no-model HTTP | Keep ValidationError → 422 | current tts.py | No core edit | Violates Spec 409 | ❌ |
| | `TTS_NO_MODEL_CONFLICT` | Spec 409; p3 illegal-state lock | Envelope matches GUI/MCP | One-line service edit | ✅ |
| Download start already Processing | Change service to raise | Spec 409 | Service owns it | Changes approved p3 idempotence | ❌ |
| | `START_IF_PROCESSING` at route | Spec 409 + frozen start no-op | No machine rewrite | Route branches | ✅ |

---

## Research References

- `docs/build-plan/04-rest-api.md`
- `docs/build-plan/03-service-layer.md` (command tables)
- `docs/build-plan/06-gui.md` Settings keys 978–1011
- `docs/execution/plans/2026-08-19-p3-services/implementation-plan.md` (locks)
- `docs/execution/reflections/2026-08-19-p3-services-reflection.md` RULE-1–4
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [FastAPI HTTP Basic / `secrets.compare_digest`](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/)
- [Pydantic v2 `ConfigDict(extra="forbid")`](https://docs.pydantic.dev/latest/api/config/)
- `.agent/docs/emerging-standards.md` G8, G19, G29, G36, M5, M6
- `_inspiration/DESIGN_PROPOSAL.md` start → poll
