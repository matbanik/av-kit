---
project: "2026-08-19-p5-mcp-server"
date: "2026-08-19"
source: "docs/build-plan/05-mcp-server.md"
meus: ["MEU-17", "MEU-18"]
status: "approved"
template_version: "2.0"
---

# Implementation Plan: Phase 5 MCP Server

> **Project**: `2026-08-19-p5-mcp-server`
> **Build Plan Section(s)**: [05-mcp-server.md](../../../build-plan/05-mcp-server.md)
> **Status**: `approved`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 6 — MEU-17 → MEU-18

---

## Goal

Give IDE agents the same capabilities as the GUI by wrapping **existing** `/api/v1` routes. New `mcp-server/` TypeScript package: stdio MCP, thin `fetch` + Bearer, Zod `.strict()` at the agent boundary. Six compound tools, `action` discriminated unions, `ACTION_INDEX` = 46, destructive `confirm: true`. No SQLite, yt-dlp, Kokoro, ports, or GUI files. Do not rewrite FastAPI routers. Do not invent MEU IDs. Do not start Session 7.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent; Headroom has no approved disposition. Planning and execution use exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-17 | `.agent/context/handoffs/2026-08-19-p5-mcp-server-MEU-17-handoff.md` |
| MEU-18 | `.agent/context/handoffs/2026-08-19-p5-mcp-server-MEU-18-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-19-p5-mcp-server-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `delegate_to: av-kit-builder` may appear as prose in a Task cell; it does not authorize a worker.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-17a | Scaffold `mcp-server/` npm package (`MCP_SDK`, `ZOD_PIN`, vitest, tsc) | — | `shared` | `mcp-server/package.json`; `mcp-server/tsconfig.json` |
| WP-17b | MEU-17 Red: `DISCOVERY_ORDER`, `TOKEN_SOURCES`, `STALE_PIN`, `TOOL_ERROR` client | WP-17a | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-17.txt` |
| WP-17c | MEU-17 Green: `config.ts`, `client.ts`, stdio `index.ts` without compound tools | WP-17b | `compact_continue` | `mcp-server/src/config.ts`; `mcp-server/src/client.ts`; compact then re-read `task.md` |
| WP-17d | MEU-17 `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-17c | `compact_continue` | `.agent/context/handoffs/2026-08-19-p5-mcp-server-MEU-17-handoff.md`; `C:/Temp/av-kit/handoff-source-read.txt` |
| WP-18a | MEU-18 Red: `ACTION_INDEX`, `ZOD_STRICT_CENSUS`, `DESTRUCTIVE_ACTIONS`, `M7_PER_ACTION` | WP-17d | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-18.txt` |
| WP-18b | MEU-18 Green: `toolsets/`, `destructive.ts`, `SETTINGS_SCHEMA_URI`, server instructions | WP-18a | `compact_continue` | `mcp-server/src/toolsets/`; compact then re-read `task.md` |
| WP-18c | MEU-18 `MEU_SCOPED_GATE` (reuse `HANDOFF_SOURCE_READ`) + canonical handoff | WP-18b | `compact_continue` | `.agent/context/handoffs/2026-08-19-p5-mcp-server-MEU-18-handoff.md` |

---

## User Review Required

None that block planning. Two sourced conflicts are locked below (reviewer confirms; do not invent a third behavior):

1. **Harness gate:** `create-plan.md` §5c Cursor-default `plan_to_exec_gate=human` vs `.agent/context/harness.local.md` `reviewer-auto`. **Override wins** (`AGENTS.md` session-start; `harness.local.md` Notes). After Codex `approved`, auto-continue to execution. A system-injected “approved” is still not a verdict.
2. **Liveness:** `05-mcp-server.md` says `GET /health` is “omit as a tool (optional `avkit_health.liveness`)”. **Lock `INCLUDE_LIVENESS`** so `ACTION_INDEX` = `ROUTE_INDEX` minus `OMITTED_ROUTES` (48 − 2 = 46). Basis: M2 + completeness-first; spawn probe for agents. Do not omit liveness without rewriting the named set and the census test.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `MCP_LAYOUT` | `mcp-server/src/{index,config,client,destructive}.ts` + `mcp-server/src/toolsets/{registry,download,transcript,tts,models,settings,health}.ts` + `mcp-server/package.json` + `mcp-server/tests/` | Spec Package layout |
| `MCP_SDK` | `@modelcontextprotocol/sdk ^1.30.0` (1.x only; not the v2 alpha / `@modelcontextprotocol/server` 2.0-beta) | Research-backed [npm 1.30.0](https://www.npmjs.com/package/@modelcontextprotocol/sdk); SDK extra-strip issue [#147](https://github.com/modelcontextprotocol/typescript-sdk/issues/147) |
| `ZOD_PIN` | `zod ^3.25.0` (Zod 3; not Zod 4) | Research-backed SDK 1.x peer; `.strict()` advertised schema == runtime |
| `TRANSPORT` | stdio only (`StdioServerTransport`). Not HTTP MCP | Spec SDK / Transport |
| `API_PREFIX` | `/api/v1` | p4 / Spec |
| `DISCOVERY_ORDER` | Resolve `api_base`: (1) `AVKIT_API_BASE` if set and contains `/api/v1`, then `STALE_PIN` if a live descriptor exists; (2) `{app_data}/backend.json` field `api_base`; (3) `APP_NOT_RUNNING`. Never guess port 0. Never hard-code a port. | Spec Runtime; `07-distribution.md` 220–236 |
| `DEFAULT_APP_DATA` | Windows `%LOCALAPPDATA%/av-kit`; else `~/.avkit/` | Local Canon `02-infrastructure.md` line 57 |
| `APP_DATA_OVERRIDE` | `AVKIT_APP_DATA` replaces `DEFAULT_APP_DATA` when reading `backend.json` / `mcp-token.txt` | Spec Runtime |
| `TOKEN_SOURCES` | (1) `AVKIT_API_TOKEN` if set and non-blank; (2) contents of `{app_data}/mcp-token.txt` trimmed; (3) `TOKEN_MISSING` for authenticated actions | Spec Auth; `07-distribution.md` 226–234 |
| `MCP_TOKEN_SOURCE` | Stable MCP key only. **Never** the GUI nonce. **Never** a field on `backend.json` | Spec Auth; p4 `AUTH_TOKENS`; `07-distribution.md` “Never write the GUI nonce or MCP token into this file” |
| `AUTH_EXEMPT_ACTIONS` | `{avkit_health.liveness}` only — may run with no token once `api_base` is known | Spec `GET /health` no auth; p4 `AUTH_EXEMPT_PATHS` |
| `STALE_PIN` | If `AVKIT_API_BASE` is set **and** `{app_data}/backend.json` exists **and** the pin’s host+port ≠ descriptor `host`+`port` (or parsed `api_base` host+port) → `TOOL_ERROR` with code `stale_pin` and **no fetch** | Local Canon `07-distribution.md` 236 |
| `APP_NOT_RUNNING` | Structured `TOOL_ERROR` code `app_not_running` when neither a valid pin nor `backend.json` `api_base` exists | Spec Discovery step 3 |
| `TOKEN_MISSING` | Structured `TOOL_ERROR` code `token_missing` when an authenticated action has no `TOKEN_SOURCES` value | Spec Auth |
| `FETCH_FAILED` | Structured `TOOL_ERROR` code `fetch_failed` (include HTTP status when present) on network/timeout/non-OK without a parseable `ERROR_ENVELOPE` | Spec “503 / fetch failed, not a hang” |
| `ERROR_ENVELOPE` | `{ "error": { "code": str, "message": str, "details": object \| null } }` | p4 named set; Spec Client |
| `TOOL_ERROR` | Public handler contract: `{ content: [{ type: "text", text }], isError: true }` whose `text` includes `ERROR_ENVELOPE.code` and `ERROR_ENVELOPE.message` (or the structured discovery/token/stale-pin/fetch codes above). Internal `client.ts` may use a Result type; do **not** leak `{ok:false}` as a second public contract. Extra Zod keys never reach `fetch`. | Research-backed [MCP tools errors](https://modelcontextprotocol.io/specification/2025-06-18/server/tools); [SDK errors](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/servers/errors.md) |
| `ADD_TIMEOUT_MS` | `120000` for `avkit_download.add` / `avkit_transcript.add` only | Spec Client “generous add”; Research-backed `AbortSignal.timeout` |
| `DEFAULT_TIMEOUT_MS` | `30000` for every other `fetch` | Spec Client; start/generate return quickly |
| `COMPOUND_TOOLS` | `{avkit_download, avkit_transcript, avkit_tts, avkit_models, avkit_settings, avkit_health}` | Spec Compound tools |
| `OMITTED_ROUTES` | `{POST /api/v1/health/startup-metrics, GET /api/v1/health/console}` | Spec M2 table |
| `INCLUDE_LIVENESS` | `avkit_health` action `liveness` → `GET /api/v1/health` (no auth required) | Spec optional + M2; this plan lock |
| `ROUTE_INDEX` | the 48 method/path rows in `04-rest-api.md` “Full route index” (p4 named set) | Spec / p4 |
| `ACTION_INDEX` | the 46 `(tool, action, method, path)` rows in the table below = `ROUTE_INDEX` minus `OMITTED_ROUTES` | this plan |
| `DESTRUCTIVE_ACTIONS` | `{avkit_download.remove, avkit_download.clear, avkit_transcript.remove, avkit_tts.cancel}` — each requires `confirm: true` on the Zod schema; reject **before fetch** if missing/false | Spec M3 adapted |
| `NON_DESTRUCTIVE_STOPS` | `{avkit_download.cancel, avkit_download.stop, avkit_transcript.stop}` — **not** in `DESTRUCTIVE_ACTIONS` | Spec M3 “queue cancel/stop are not in the set” |
| `ZOD_STRICT` | Every `ACTION_INDEX` action input schema is `.strict()`. Unknown keys fail before `fetch` | Spec Zod boundary (M1) |
| `ZOD_STRICT_CENSUS` | Parametrized extra-key oracle over **all 46** `ACTION_INDEX` rows (reads, writes, and `DESTRUCTIVE_ACTIONS` with `confirm: true` plus an unknown key). Each case: `TOOL_ERROR` + fetch count `0`. Do not subset to write actions. | PR-8; r1 F1 |
| `VARIANT_ID_MIN` | `variant_id` `z.string().min(1)` on `avkit_models.download` and `avkit_models.load` | p4 RULE-1 / F1 |
| `QUALITY_WIRES` | `best,2160p,1440p,1080p,720p,480p,360p,240p,144p,lowest` | frozen `wire.py` |
| `AUDIO_WIRES` | `default,best,lowest,low_webm,medium_webm,standard_webm,standard_m4a,standard_mp3,high_m4a` | frozen `wire.py` |
| `DEVICE_WIRES` | `auto,cuda,cpu,mps` | frozen `wire.py` |
| `COOKIE_MODE_WIRES` | `none,browser,file` | frozen `wire.py` |
| `OUTPUT_FORMAT_WIRES` | `MP3,WAV` | frozen `wire.py` |
| `SETTING_NAMESPACES` | `downloader,transcript,tts,app,ui` | p4 / Spec |
| `SETTINGS_UI_API_KEYS` | `{theme}` — `ui.rail.collapsed` / `ui.panel.console.height` are unknown leaves → API 422, surfaced as `TOOL_ERROR` | p4 lock |
| `SETTINGS_SCHEMA_URI` | `avkit://settings/schema` — JSON of namespaces + leaf keys + types + defaults from `06-gui.md` 978–1009 **except** `ui.rail.collapsed` and `ui.panel.console.height`. Referenced from `avkit_settings` descriptions (M7). Not a second store. | Spec Optional MCP resource; p4 UI-key lock |
| `LIST_ENVELOPE` | `{ items, processor }` for download/transcript `list` | p4 / Spec |
| `VOICES_FACADE` | `avkit_tts.voices` → `GET /tts/voices` only; public list; no user-set `lang_code` | p4 `VOICES_FACADE` |
| `FORBIDDEN_RESULT_FIELDS` | transcript body text, media bytes, cookie bytes, full TTS `text`, `video_ids`, user-set `lang_code` | Spec What this layer must not do; p4 `FORBIDDEN_BODY_FIELDS` |
| `OLD_TOOL_NAMES` | `avkit_download_add`, `avkit_download_start`, `avkit_download_stop`, `avkit_download_status`, `avkit_download_list`, `avkit_transcript_add`, `avkit_transcript_start`, `avkit_transcript_status`, `avkit_transcript_compile`, `avkit_tts_generate`, `avkit_tts_voices`, `avkit_tts_model_status`, `avkit_tts_model_load`, `avkit_settings_get`, `avkit_settings_set` — must **not** be registered | Spec Name map |
| `SERVER_INSTRUCTIONS` | the six numbered bullets in `05-mcp-server.md` “Server instructions (required text)” | Spec |
| `M7_MARKERS` | `Workflow:`, `Prerequisite:`, `Returns:`, `Errors:` | emerging M7 |
| `M7_GATE_PATH` | `mcp-server/src/toolsets/` (not `compound/`) | Spec Testing; emerging M7 path adapt |
| `ACTION_DESCRIPTIONS` | Exported map with exactly 46 keys (`${tool}.${action}` for every `ACTION_INDEX` row). Each value is the registered description string for that action (Zod `.describe` / tool metadata — not a comment). Compound-tool top-level descriptions are additional, not a substitute. | Spec 95–97; r1 F2 |
| `M7_PER_ACTION` | Every `ACTION_DESCRIPTIONS` value contains ≥ 3 **distinct** `M7_MARKERS` (case-insensitive). File-level `rg` on `M7_GATE_PATH` is supplementary only and is **not** the gate. | emerging M7; Spec “every tool/action description”; r1 F2 |
| `M7_FILE_SCAN` | Supplementary `rg` on `M7_GATE_PATH` for `M7_MARKERS`. Passing `M7_FILE_SCAN` alone does not satisfy AC-18.7. | r1 F2 |
| `TEST_MCP` | `mcp-server/tests/` | Spec Testing |
| `REGRESSION_TESTS` | p4 H1-2 pytest set (do not drop the 109 API/G29 tests) | p4 carry-forward |
| `SCAN_MCP_LIBS_ARGS` | import-anchored `sqlalchemy`, `yt_dlp`, `youtube_transcript_api`, `avkit_infra`, `avkit_core`, `better-sqlite`, `sqlite3` under `mcp-server/src` | Spec Thin wrapper |
| `SCAN_G36_ARGS` | `it.skip`, `describe.skip`, `test.skip`, `it.todo`, `xit`, `xdescribe` under `TEST_MCP` | G36 |
| `SCAN_PLACEHOLDER_ARGS` | `TODO`, `FIXME`, `NotImplementedError` under `mcp-server/src` | anti-placeholder |
| `HANDOFF_COUNT` | `2` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-19-p5-mcp-server-MEU-*-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-19-p5-mcp-server` | MEU `execution_plan` (no slash) |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-19-p5-mcp-server/` | phase `"5"` `execution_plans` |
| `HUB_NEXT_AFTER` | `/create-plan p6-gui-shell` | grouping pathway #7 |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | p4 Codex r3 F1 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-19-p5-mcp-server-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only; `--expected-mode implementation` | p2 Human-approved; script allow-list |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read.txt` written **once** before the first MEU handoff (`TEMPLATE=`, `PEER=`, `PASS: HANDOFF_SOURCE_READ`). Later handoffs reuse it. Receipt `LastWriteTime` must be ≤ that MEU handoff’s `LastWriteTime`. | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE + completion-preflight |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p4 |
| `MEU17_TOUCHED` | `mcp-server/package.json`; `mcp-server/tsconfig.json`; `mcp-server/vitest.config.ts`; `mcp-server/src/index.ts`; `mcp-server/src/config.ts`; `mcp-server/src/client.ts`; `mcp-server/tests/` | MEU-17 files |
| `MEU18_TOUCHED` | `mcp-server/src/destructive.ts`; `mcp-server/src/toolsets/`; `mcp-server/src/index.ts`; `mcp-server/tests/` | MEU-18 files |
| `MEU_SCOPED_GATE` | `npx tsc --noEmit` + `npx vitest run` from `mcp-server/` + `npm run build` (M4) + `SCAN_PLACEHOLDER_ARGS` + `SCAN_MCP_LIBS_ARGS` + `SCAN_G36_ARGS` + `HANDOFF_BUNDLE_MARKERS` + that MEU’s AC-IDs. MEU-18 vitest must include `ZOD_STRICT_CENSUS` and `M7_PER_ACTION` (`ACTION_DESCRIPTIONS`). `M7_FILE_SCAN` is supplementary only. | AGENTS MEU gate; r1 F1–F2 |
| `OPENAPI_SKIP_BASIS` | G8 skipped unless any file under `packages/api/` is created or modified. Default: MCP-only; no API files. | G8; create-plan Step 6 |

`ACTION_INDEX` (define once; ≥1 mocked-fetch assertion per row — method + path):

| Tool | action | Method | Path |
|------|--------|--------|------|
| `avkit_download` | `add` | POST | `/downloads` |
| `avkit_download` | `list` | GET | `/downloads` |
| `avkit_download` | `get` | GET | `/downloads/{id}` |
| `avkit_download` | `start` | POST | `/downloads/start` |
| `avkit_download` | `pause` | POST | `/downloads/pause` |
| `avkit_download` | `resume` | POST | `/downloads/resume` |
| `avkit_download` | `cancel` | POST | `/downloads/cancel` |
| `avkit_download` | `stop` | POST | `/downloads/stop` |
| `avkit_download` | `reorder` | PUT | `/downloads/reorder` |
| `avkit_download` | `reset` | POST | `/downloads/{id}/reset` |
| `avkit_download` | `remove` | DELETE | `/downloads/{id}` |
| `avkit_download` | `clear` | DELETE | `/downloads` |
| `avkit_download` | `sabr_get` | GET | `/downloads/sabr` |
| `avkit_download` | `sabr_check` | POST | `/downloads/sabr/check` |
| `avkit_download` | `sabr_force` | POST | `/downloads/sabr/force` |
| `avkit_download` | `sabr_clear` | POST | `/downloads/sabr/clear` |
| `avkit_download` | `cookies_test` | POST | `/downloads/cookies/test` |
| `avkit_download` | `apply_defaults` | POST | `/downloads/apply-defaults` |
| `avkit_transcript` | `add` | POST | `/transcripts` |
| `avkit_transcript` | `list` | GET | `/transcripts` |
| `avkit_transcript` | `get` | GET | `/transcripts/{id}` |
| `avkit_transcript` | `start` | POST | `/transcripts/start` |
| `avkit_transcript` | `pause` | POST | `/transcripts/pause` |
| `avkit_transcript` | `resume` | POST | `/transcripts/resume` |
| `avkit_transcript` | `stop` | POST | `/transcripts/stop` |
| `avkit_transcript` | `requeue` | POST | `/transcripts/{id}/requeue` |
| `avkit_transcript` | `retry` | POST | `/transcripts/{id}/retry` |
| `avkit_transcript` | `reorder` | PUT | `/transcripts/reorder` |
| `avkit_transcript` | `remove` | DELETE | `/transcripts/{id}` |
| `avkit_transcript` | `compile` | POST | `/transcripts/{id}/compile` |
| `avkit_tts` | `prepare` | POST | `/tts/prepare` |
| `avkit_tts` | `generate` | POST | `/tts/generate` |
| `avkit_tts` | `get` | GET | `/tts/{id}` |
| `avkit_tts` | `cancel` | DELETE | `/tts/{id}` |
| `avkit_tts` | `voices` | GET | `/tts/voices` |
| `avkit_models` | `available` | GET | `/models/available` |
| `avkit_models` | `downloaded` | GET | `/models/downloaded` |
| `avkit_models` | `download` | POST | `/models/download` |
| `avkit_models` | `download_runtime` | GET | `/models/download-runtime` |
| `avkit_models` | `load` | POST | `/models/load` |
| `avkit_models` | `unload` | POST | `/models/unload` |
| `avkit_models` | `status` | GET | `/models/status` |
| `avkit_settings` | `get` | GET | `/settings/{namespace}` |
| `avkit_settings` | `set` | PUT | `/settings/{namespace}` |
| `avkit_health` | `dependencies` | GET | `/health/dependencies` |
| `avkit_health` | `liveness` | GET | `/health` |

Count = 18 + 12 + 5 + 7 + 2 + 2 = **46**. Paths are relative to the resolved `api_base` (already includes `API_PREFIX`). `avkit_download.stop` is an **alias of cancel** (same REST `POST /downloads/stop`).

---

## Implementation locks (planning resolutions)

| Topic | Lock | Source |
|-------|------|--------|
| Package home | New `mcp-server/` npm package (repo has no product root `package.json`). Scripts: `build` (`tsc`), `dev` (`tsx src/index.ts`), `test` (`vitest run`), `typecheck` (`tsc --noEmit`). `"type": "module"`. | Spec layout; M4 |
| SDK / Zod | `MCP_SDK` + `ZOD_PIN`. Always `.strict()` so advertised JSON Schema matches runtime. | Research-backed npm 1.30.0; SDK #147 |
| Hexagonal | `mcp-server/src` never imports SQLAlchemy, yt-dlp, Kokoro, `avkit_infra`, or `avkit_core`. HTTP client only. | Spec Thin wrapper |
| Frozen API | Do not modify `packages/api/` unless a real MCP-blocking API bug is reproduced first (then TDD the API and expect OpenAPI `--check`). Default: `OPENAPI_SKIP_BASIS`. | grouping Session 6; G8 |
| Discovery | `DISCOVERY_ORDER` + `STALE_PIN` + `APP_NOT_RUNNING`. Pin without descriptor (dev uvicorn) is allowed. Pin that mismatches a live descriptor is not. | Spec; 07 236 |
| Token | `TOKEN_SOURCES`. Never log the token, never put it in tool results, never read a GUI nonce file. | Spec Auth |
| Client | `api<T>(method, path, body?)` prefixes `api_base`, JSON, Bearer (except `AUTH_EXEMPT_ACTIONS`), `AbortSignal.timeout`. Non-OK: parse `ERROR_ENVELOPE` when present else `FETCH_FAILED`. Handlers always return `TOOL_ERROR` (explicit `isError: true`, not a JSON-RPC protocol error). | Spec Client; MCP spec errors |
| Timeouts | `ADD_TIMEOUT_MS` / `DEFAULT_TIMEOUT_MS`. Agents poll `list`/`get`. No SSE. | Spec |
| Tools | `COMPOUND_TOOLS` only. `action` is a Zod discriminated union. Wire enums = `QUALITY_WIRES` / `AUDIO_WIRES` / `DEVICE_WIRES` / `COOKIE_MODE_WIRES` / `OUTPUT_FORMAT_WIRES`. | Spec |
| Confirm | `confirm: z.literal(true)` on `DESTRUCTIVE_ACTIONS`. Missing/false → `TOOL_ERROR` before fetch. `NON_DESTRUCTIVE_STOPS` have no confirm field. | Spec M3; M1 |
| Liveness | `INCLUDE_LIVENESS`. Do not register `OMITTED_ROUTES` or `OLD_TOOL_NAMES`. | this plan; Spec M2 / Name map |
| Results | Pass through API JSON (list envelopes, `text_preview`/`text_hash`, `file_path` pointers). Strip/reject `FORBIDDEN_RESULT_FIELDS` if a mock or envelope ever includes them (assert in tests). | Spec |
| Settings | Namespace ∈ `SETTING_NAMESPACES`. Unknown key → API 422 → `TOOL_ERROR`. `SETTINGS_UI_API_KEYS`. Cookie **paths** only. | Spec; p4 |
| Resource | Register `SETTINGS_SCHEMA_URI`. Reference it from `avkit_settings` descriptions. | Spec; M7 |
| Instructions | `SERVER_INSTRUCTIONS` published on the MCP server. | Spec |
| Tests | Vitest + mocked `fetch`. No live YouTube. Red must fail for the right reason (M5). `ZOD_STRICT_CENSUS` and missing-confirm tests must fail if `.strict()` / confirm is removed (M6). | Spec Testing; M5/M6/G36 |
| Reorder | Tests assert the exact forwarded `job_ids` on the mock fetch body **and** the list envelope. | p4 RULE-2 |
| Empty IDs | Empty `variant_id` / job `id` rejected by Zod (`min(1)`) as `TOOL_ERROR` before fetch — not a 404. | p4 RULE-1 |
| Health | Do not re-open HealthService re-entrancy (RULE-3). MCP only `fetch`es `/health*`. | p4 RULE-3 |
| Bind / CLI | Do not add a production Python CLI (MEU-19/24). | p4 lock; grouping |
| Emerging | Add M1, M2, M3, M4, M5, M6, M7 as task rows. Skip TUI/trading/Go. Skip G8 unless API files change. | emerging-standards adoption filter |
| 4A | Skip — no `ui/src/renderer/` elements. | create-plan §4A |

---

## Proposed Changes

### MEU-17 — `mcp-runtime`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Env `AVKIT_API_BASE` | `config.resolveApiBase` | must contain `/api/v1`; URL parseable | invalid → `TOOL_ERROR` (`invalid_api_base`); no fetch |
| Env `AVKIT_API_TOKEN` | `config.resolveToken` | non-blank after trim | blank treated as unset |
| Env `AVKIT_APP_DATA` | `config.resolveAppData` | existing or created-by-test temp dir | used as `{app_data}` |
| File `{app_data}/backend.json` | `config.readDescriptor` | `schema_version: 1`; `api_base` required when used; **no** token/nonce fields consumed | missing/invalid → fall through `DISCOVERY_ORDER`; credential fields ignored |
| File `{app_data}/mcp-token.txt` | `config.resolveToken` | trimmed contents | missing → `TOKEN_MISSING` for authenticated calls |
| HTTP `fetch` (client) | `client.api` | JSON + Bearer except `AUTH_EXEMPT_ACTIONS`; timeouts named above | non-OK → `ERROR_ENVELOPE` or `FETCH_FAILED` |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-17.1 | unit | **Control `DISCOVERY_ORDER`.** Observable: returned `api_base` string or `TOOL_ERROR.code`. Chain: `resolveApiBase` → env → descriptor → fail. Negative: unset env + missing descriptor → `app_not_running`; never `http://127.0.0.1:0` or a hard-coded port. | Spec Runtime | guessed port |
| AC-17.2 | unit | **Control `STALE_PIN`.** Observable: `TOOL_ERROR.code === stale_pin` and mock `fetch` call count `0`. Chain: `resolveApiBase` compares pin host+port to descriptor. Negative: pin `http://127.0.0.1:9/api/v1` vs descriptor port `51234` still fetches. Pin without descriptor is allowed (dev uvicorn). | Local Canon 07 236 | fetch on dead pin |
| AC-17.3 | unit | **Control `TOKEN_SOURCES` / `MCP_TOKEN_SOURCE`.** Observable: Authorization header value on an authenticated `api()` call. Chain: `resolveToken` → `client.api` header. Negative: GUI nonce string used when `mcp-token.txt` and env differ; token substring appears in `TOOL_ERROR` text or logs. Blank env falls through to file. | Spec Auth | nonce leaked |
| AC-17.4 | unit | `AVKIT_APP_DATA` overrides `DEFAULT_APP_DATA` for both descriptor and token paths. | Spec Runtime | default path used when override set |
| AC-17.5 | unit | `AVKIT_API_BASE` without `/api/v1` → `invalid_api_base`; no fetch. | Spec Discovery (1) | suffix optional |
| AC-17.6 | integration | **Control `TOOL_ERROR` / `FETCH_FAILED`.** Observable: handler-shaped result `isError===true` and text includes `fetch_failed` or HTTP `503` / envelope `code`. Chain: mocked `fetch` reject or 503 → `client.api` → (MEU-17 exposes a test helper / future health call). Negative: uncaught hang (AbortSignal never set) or public `{ok:false}` object as the tool result. | Spec Client; Research-backed MCP errors | hang / dual contract |
| AC-17.7 | unit | Authenticated call without token → `token_missing` and fetch count `0`. `AUTH_EXEMPT_ACTIONS` (liveness helper) may call `GET /health` with no Bearer once `api_base` is known. | Spec Auth; p4 exempt path | 401 invented locally |
| AC-17.8 | unit | **Control hexagonal.** Observable: `SCAN_MCP_LIBS_ARGS` receipt empty. Chain: package source only. Negative: any `MEU17_TOUCHED` src import of sqlite/yt-dlp/`avkit_core`. | Spec Thin wrapper | infra import |
| AC-17.9 | unit | Stdio server constructs with `TRANSPORT` and `SERVER_INSTRUCTIONS` text present (tools may be empty until MEU-18). | Spec index.ts | HTTP MCP transport |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| api_base order | Spec | `DISCOVERY_ORDER` |
| stale pin | Local Canon 07 | `STALE_PIN` |
| throw vs `{ok:false}` | Research-backed | `TOOL_ERROR` (`isError: true`) |
| SDK major | Research-backed | `MCP_SDK` 1.30.0 / 1.x |
| default app_data | Local Canon 02 | `DEFAULT_APP_DATA` |
| GUI nonce | Spec + p4 | `MCP_TOKEN_SOURCE` |
| Timeouts | Spec + Research-backed | `ADD_TIMEOUT_MS` / `DEFAULT_TIMEOUT_MS` |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `mcp-server/package.json` | new | `MCP_SDK`, `ZOD_PIN`, vitest, typescript, tsx, `@types/node` |
| `mcp-server/tsconfig.json` | new | ESM, strict, `outDir: dist` |
| `mcp-server/vitest.config.ts` | new | node environment |
| `mcp-server/src/index.ts` | new | `StdioServerTransport` + `SERVER_INSTRUCTIONS` |
| `mcp-server/src/config.ts` | new | discovery + token |
| `mcp-server/src/client.ts` | new | `fetch` wrapper |
| `mcp-server/tests/config.test.ts` | new | AC-17.1–17.5, 17.7 |
| `mcp-server/tests/client.test.ts` | new | AC-17.6 |
| `mcp-server/tests/runtime.test.ts` | new | AC-17.8–17.9 |

---

### MEU-18 — `mcp-tools`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `avkit_download` input | Zod discriminated `action` | `QUALITY_WIRES` / `AUDIO_WIRES`; url min 1; `id` min 1; `job_ids` string[]; `cookies_test` mode ∈ `COOKIE_MODE_WIRES` (path only); `confirm: true` on remove/clear | `ZOD_STRICT` — extra key → `TOOL_ERROR` before fetch |
| `avkit_transcript` input | Zod discriminated `action` | `channel_url` min 1; `id` min 1; `job_ids`; `confirm: true` on remove | `ZOD_STRICT` |
| `avkit_tts` input | Zod discriminated `action` | speed 0.5–2.0; format ∈ `OUTPUT_FORMAT_WIRES`; `id` min 1; `confirm: true` on cancel | `ZOD_STRICT` |
| `avkit_models` input | Zod discriminated `action` | `VARIANT_ID_MIN`; device ∈ `DEVICE_WIRES` | `ZOD_STRICT` |
| `avkit_settings` input | Zod discriminated `action` | namespace ∈ `SETTING_NAMESPACES`; `set` leaf object `.strict()` | `ZOD_STRICT`; unknown leaf → API 422 → `TOOL_ERROR` |
| `avkit_health` input | Zod discriminated `action` | `dependencies` \| `liveness` | `ZOD_STRICT` |
| MCP resource `SETTINGS_SCHEMA_URI` | static JSON in `settings.ts` | keys = 06-gui 978–1009 minus rail/panel | read-only; not a write surface |

Invalid MCP input → `TOOL_ERROR` (not HTTP). HTTP 422/409 from API → `TOOL_ERROR` with envelope `code`+`message`. Create/update parity: `set` uses the same leaf invariants as REST PUT (unknown/`rail` key is 422).

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-18.1 | integration | **Control `ACTION_INDEX`.** Observable: registered tool names == `COMPOUND_TOOLS` and action-union members == 46 `ACTION_INDEX` rows. Chain: `registry` → `listTools` / exported action table → census test. Negative: missing action, extra action, or `OLD_TOOL_NAMES` registered; `OMITTED_ROUTES` exposed. | Spec M2; this plan | 45 or 47 |
| AC-18.2 | integration | Each `ACTION_INDEX` row: mocked `fetch` is called with that method and `api_base + path` (id interpolated). Body JSON matches the Zod-parsed input (no extra keys). | Spec Testing | wrong path |
| AC-18.3 | integration | **Control `ZOD_STRICT` / `ZOD_STRICT_CENSUS`.** Observable: for **every** `ACTION_INDEX` row, valid minimal input plus one unknown key → `TOOL_ERROR` + fetch count `0` (destructive rows include `confirm: true` and still reject the extra key). Chain: Zod `.strict()` parse → handler; no `fetch`. Negative: any row strips the extra key and fetches (including `avkit_download.remove` with `confirm:true` + unknown key). | Spec M1; M6; r1 F1 | extra stripped |
| AC-18.4 | integration | **Control `DESTRUCTIVE_ACTIONS`.** Observable: missing or `confirm:false` → `TOOL_ERROR` + fetch count `0` for each of the four actions. Chain: Zod `confirm` → `destructive.ts` gate → handler. Negative: `remove` without confirm still DELETEs. `NON_DESTRUCTIVE_STOPS` succeed without `confirm`. | Spec M3; M1; M6 | gate dead |
| AC-18.5 | integration | Download/transcript `list` parses `LIST_ENVELOPE` (not a bare array). | Spec | bare array accepted |
| AC-18.6 | integration | API 422/409 JSON `ERROR_ENVELOPE` surfaces as `TOOL_ERROR` whose text includes `code` and `message`. | Spec Testing | raw HTML / missing code |
| AC-18.7 | integration | **Control `M7_PER_ACTION`.** Observable: `ACTION_DESCRIPTIONS` has exactly 46 keys matching `ACTION_INDEX`; each value contains ≥ 3 distinct `M7_MARKERS`; `SERVER_INSTRUCTIONS` present; `avkit_settings` (tool or `set`/`get` descriptions) references `SETTINGS_SCHEMA_URI`. Chain: exported `ACTION_DESCRIPTIONS` → registered tool/action metadata. Negative: a file-level `M7_FILE_SCAN` pass while any action description is a one-liner without three markers. | emerging M7; Spec 95–97; r1 F2 | per-file false-pass |
| AC-18.8 | integration | **Control `FORBIDDEN_RESULT_FIELDS`.** Observable: tool result text/JSON must not contain transcript body, cookie bytes, media bytes, full TTS `text`, `video_ids`, or user-set `lang_code` when the mock API returns those fields. Chain: handler result mapper. Negative: mock `{text:"SECRET"}` appears in the tool result. | Spec must-not | leak |
| AC-18.9 | unit | **Control `VARIANT_ID_MIN`.** Observable: empty `variant_id` → `TOOL_ERROR` + fetch `0` on download and load (schema-owned, not 404). | p4 RULE-1 | empty forwarded |
| AC-18.10 | integration | `SETTINGS_SCHEMA_URI` resource read returns the locked key table (namespaces + types + defaults; no rail/panel). | Spec resource; p4 UI keys | rail key present |
| AC-18.11 | integration | `avkit_tts.voices` → `GET /tts/voices` only (`VOICES_FACADE`). | p4 F1 | other path |
| AC-18.12 | integration | **Control reorder (RULE-2).** Observable: mock fetch body `job_ids` equals the exact input permutation for download and transcript `reorder`; list envelope unchanged. Negative: handler drops/re-sorts ids. | p4 RULE-2 | permutation lost |
| AC-18.13 | integration | `avkit_settings.set` unknown/`rail` key → API 422 → `TOOL_ERROR`. Theme-only `ui` leaf allowed. | p4 `SETTINGS_UI_API_KEYS` | rail accepted locally |
| AC-18.14 | integration | `stop` on downloads calls `POST /downloads/stop` (alias of cancel). Cookies test never sends cookie bytes. | Spec | stop ≠ stop path |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Route parity | Spec M2 + this lock | `ACTION_INDEX` = 46 with `INCLUDE_LIVENESS` |
| Confirm shape | Spec (boolean, not Zorivest token) | `confirm: true` |
| MCP Guard | Spec + grouping named deferral | out-of-scope (not a MEU) |
| Resource | Spec optional + M7 + completeness-first | include `SETTINGS_SCHEMA_URI` |
| Error shape | Research-backed | `TOOL_ERROR` |
| Empty IDs | Local Canon p4 RULE-1 | `VARIANT_ID_MIN` |
| Voices | Local Canon p4 | `VOICES_FACADE` |
| ui geometry | Local Canon p4 | omit from schema resource |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `mcp-server/src/destructive.ts` | new | `DESTRUCTIVE_ACTIONS` + confirm gate |
| `mcp-server/src/toolsets/registry.ts` | new | enable/list + export `ACTION_DESCRIPTIONS` (46 keys) |
| `mcp-server/src/toolsets/{download,transcript,tts,models,settings,health}.ts` | new | compound tools |
| `mcp-server/src/index.ts` | modify | register tools + resource + instructions |
| `mcp-server/tests/action-index.test.ts` | new | AC-18.1–18.2, 18.14 |
| `mcp-server/tests/strict-confirm.test.ts` | new | AC-18.3 (`ZOD_STRICT_CENSUS` all 46) + AC-18.4 + AC-18.9 |
| `mcp-server/tests/tools-parity.test.ts` | new | AC-18.5–18.6, 18.8, 18.11–18.13 |
| `mcp-server/tests/m7-resource.test.ts` | new | AC-18.7 (`M7_PER_ACTION` + `ACTION_DESCRIPTIONS`) + AC-18.10 |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| MCP Guard / lock / unlock | out-of-scope | — | `05-mcp-server.md` 274; grouping “Named deferrals are not MEUs”; `06-gui.md` defers Guard |
| HTTP MCP transport | out-of-scope | — | `05-mcp-server.md` 43 “Not HTTP MCP in MVP” |
| SSE / websocket progress | out-of-scope | — | `05-mcp-server.md` 278; Phase 5 “What this layer must not do” |
| `POST /health/startup-metrics` tool | out-of-scope | — | Spec M2 table (Electron splash) |
| `GET /health/console` tool | out-of-scope | — | Spec M2 table (GUI dock) |
| `OLD_TOOL_NAMES` as a second tool set | out-of-scope | — | Spec Name map 231 |
| Electron `PythonManager` / Vite / `ui/` | deferred | MEU-19 | grouping Session 7; `meu-status.yaml` MEU-19 |
| GUI pages / `apiFetch` / Copy MCP button | deferred | MEU-20–23 | grouping Sessions 8–11 |
| Ship `mcp-server/dist` in NSIS / Copy MCP default `mcp.json` | deferred | MEU-24, MEU-25 | grouping Session 12; `07-distribution.md` 218–236 |
| Production Python CLI / uvicorn spawn | deferred | MEU-19, MEU-24 | p4 bind lock; grouping |
| Rewrite FastAPI routers / Session 2–4 machines | out-of-scope | — | grouping Session 6; p4 carry-forward |
| Live YouTube / HF / Kokoro in default suite | out-of-scope | — | Spec Testing “No live YouTube” |
| Invent MEU IDs / start Session 7 in this plan | out-of-scope | — | grouping; USER_EXPLICIT Session 6 only |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-17/18 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"5"`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 1–5 plan links. Do not hand-edit AUTOGEN tables — `meu_status.py render`.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p5-mcp-server'; SLASH=PLAN+'/'; NEXT='/create-plan p6-gui-shell'; MEUS=('MEU-17','MEU-18'); data=load(); p5=next(p for p in data['phases'] if str(p['id'])=='5'); eps=list(p5.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 5 missing PLAN_FOLDER_SLASH'); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

> Classify every command through [`.agent/docs/output-evidence-policy.md`](../../../.agent/docs/output-evidence-policy.md).

### 1. MCP tests + types + M4 build

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location mcp-server; npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx vitest run; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/mcp-verify.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/mcp-verify.txt | Select-Object -Last 40; exit $code
```

### 2. Python regression (do not drop p4)

```powershell
rtk proxy uv run pytest tests/e2e tests/integration/test_api_wiring.py tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py -x --tb=short -v *> C:/Temp/av-kit/pytest-p5-regression.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p5-regression.txt | Select-Object -Last 40; exit $code
```

### 3. M7 + hexagonal + G36 + placeholder

`M7_PER_ACTION` is proven by `npx vitest run` (AC-18.7 / `ACTION_DESCRIPTIONS`). The `rg` below is `M7_FILE_SCAN` only — supplementary, not the gate.

```powershell
rtk proxy rg -i -e "workflow:|prerequisite:|returns:|errors:" mcp-server/src/toolsets *> C:/Temp/av-kit/m7-mcp.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/m7-mcp.txt; exit $code
```

`SCAN_MCP_LIBS_ARGS`, `SCAN_G36_ARGS`, `SCAN_PLACEHOLDER_ARGS` — rg exit 1 = clean PASS (same p4 0/1 rule). Task rows 4/7 also run these on `MEU*_TOUCHED`.

### 4. OpenAPI (G8)

Skip with `OPENAPI_SKIP_BASIS` unless `packages/api/` changed. If it changed:

```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

### N. `CHECK_EXEC_REVIEW`

Same first-frontmatter checker as Session 5 against `EXEC_REVIEW_FILE` / `EXEC_REVIEW_TARGET` / `EXEC_REVIEW_MAX_ROUND`. `tools/validate_closeout_artifacts.py` is **not** in this tree — H1/H2 use named marker receipts + `CHECK_EXEC_REVIEW` (p4 pattern).

---

## Open Questions

None `Human-decision-required`. Sourced forks (reviewer confirms locks):

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| Client error shape | Throw / `{ok:false}` as public contract | Spec Client “pick one” | Matches some REST clients | Model never sees JSON-RPC throws; dual contract | ❌ |
| | `TOOL_ERROR` (`isError: true`) | [MCP tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools); [SDK errors](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/servers/errors.md) | Model can retry; one public shape | Handlers must wrap | ✅ |
| SDK major | v2 alpha / new `@modelcontextprotocol/server` | npm 2.0-beta | Newer protocol | Zod 4 extra-strip risk (SDK #147); unstable | ❌ |
| | `MCP_SDK` 1.x `^1.30.0` + `ZOD_PIN` 3 | [npm 1.30.0](https://www.npmjs.com/package/@modelcontextprotocol/sdk) | Stable; `.strict()` matches schema | Not newest major | ✅ |
| `GET /health` tool | Omit liveness (`ACTION_INDEX`=45) | Spec “omit as a tool” | Strict reading of omit | Agents cannot probe spawn; M2 incomplete | ❌ |
| | `INCLUDE_LIVENESS` (`ACTION_INDEX`=46) | Spec “optional liveness”; M2 except `OMITTED_ROUTES` | Exact 48−2; spawn probe | Uses the optional branch | ✅ |
| Settings resource | Skip optional resource | Spec “Optional” | Fewer files | M7 says reference the resource | ❌ |
| | Include `SETTINGS_SCHEMA_URI` | Spec + M7 + completeness-first | Agents discover keys | Must stay in sync with 06-gui minus rail/panel | ✅ |

---

## Research References

- `docs/build-plan/05-mcp-server.md`
- `docs/build-plan/04-rest-api.md` (route index)
- `docs/build-plan/07-distribution.md` (descriptor + Copy MCP + stale pin)
- `docs/build-plan/02-infrastructure.md` (`DEFAULT_APP_DATA`)
- `docs/build-plan/06-gui.md` 978–1009 (settings key table)
- `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md` (named sets)
- `docs/execution/reflections/2026-08-19-p4-rest-api-reflection.md` RULE-1–3
- `.agent/docs/emerging-standards.md` M1–M7
- [MCP tools / `isError`](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [SDK server errors](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/servers/errors.md)
- [npm `@modelcontextprotocol/sdk` 1.30.0](https://www.npmjs.com/package/@modelcontextprotocol/sdk)
- [SDK issue #147 extra keys](https://github.com/modelcontextprotocol/typescript-sdk/issues/147)
