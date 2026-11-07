# Phase 5 — MCP Server

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: [Phase 4](04-rest-api.md) | Parallel with: [Phase 6](06-gui.md)

---

## Goal

Give IDE agents the same capabilities as the GUI, by wrapping **existing** REST routes. No second domain, no extra URLs. File **bodies** are forbidden except the Phase 9 `avkit_capture` `image` action ([09-screenshot-capture.md](09-screenshot-capture.md)). The server is TypeScript stdio MCP; every tool is `fetch` + Bearer.

| Source | Decision |
|--------|----------|
| Spec | [Phase 4](04-rest-api.md) route index and wire enums; [APPLICATION_PURPOSE.md §4E](../../_inspiration/APPLICATION_PURPOSE.md) |
| Local Canon | [DESIGN_PROPOSAL.md](../../_inspiration/DESIGN_PROPOSAL.md) MCP ↔ FastAPI via HTTP; Zorivest toolset registry + TokenRefreshManager |
| Research-backed | MCP tools = Zod `.strict()` at the agent boundary (same job as Pydantic `extra="forbid"`) |
| Human-approved | Emerging standards **M1, M2, M3, M4, M7** (MCP rows only). [06-gui.md](06-gui.md) defers **MCP Guard** (lock/unlock) — do not invent it here |

This file **supersedes** the short tool list that used to live here. Old names (`avkit_download_add`, …) become **actions** on compound tools, not a second API.

---

## Package layout

```
mcp-server/
├── src/
│   ├── index.ts                 # StdioServerTransport, server instructions
│   ├── config.ts                # AVKIT_API_BASE, AVKIT_API_TOKEN
│   ├── client.ts                # fetch wrapper + Bearer + ErrorEnvelope
│   ├── toolsets/
│   │   ├── registry.ts          # enable/list toolsets (Zorivest pattern)
│   │   ├── download.ts          # avkit_download
│   │   ├── transcript.ts        # avkit_transcript
│   │   ├── tts.ts               # avkit_tts
│   │   ├── models.ts            # avkit_models
│   │   ├── settings.ts          # avkit_settings
│   │   ├── health.ts            # avkit_health
│   │   ├── convert.ts           # avkit_convert (Phase 8 — [08-video-conversion.md](08-video-conversion.md))
│   │   └── capture.ts           # avkit_capture (Phase 9 — [09-screenshot-capture.md](09-screenshot-capture.md))
│   └── destructive.ts           # DESTRUCTIVE_ACTIONS + confirm field
├── package.json
└── tests/
```

SDK: `@modelcontextprotocol/sdk`. Transport: **stdio** (IDE). Not HTTP MCP in MVP.

---

## Runtime

| Item | Rule |
|------|------|
| Backend | Already running FastAPI on 127.0.0.1 (Electron spawned it, or a dev `uvicorn`) |
| Auth | `Authorization: Bearer ${AVKIT_API_TOKEN}` (pre-provisioned key). **Never** the GUI nonce |
| Discovery (locked) | Resolve `api_base` in this order: (1) `AVKIT_API_BASE` if set (must include `/api/v1`), (2) `{app_data}/backend.json` field `api_base` written after bind ([07-distribution.md](07-distribution.md)), (3) fail the tool with a structured “app not running” error. Do not guess port 0 or hard-code a port. |
| App data | `AVKIT_APP_DATA` overrides default `{app_data}` when reading `backend.json` / `mcp-token.txt` |
| Client detect | Optional: Cursor / Claude / Windsurf from env for logging only — no behavior fork |

If the API is down: tool result is a structured error (`503` / fetch failed), not a hang. Agents should be told to start the app or the backend.

---

## Design rules

### Thin wrapper

Each action maps to **exactly one** Phase 4 path + method. Do not call ports, SQLite, or yt-dlp from this package.

### Zod boundary (M1)

Every field the handler reads is on the Zod schema. `.strict()` — unknown keys fail. `confirm` on destructive actions is on the schema or Zod strips it and the gate never sees it.

### API ↔ MCP parity (M2)

Every Phase 4 route has a tool action **except**:

| REST | MCP | Why |
|------|-----|-----|
| `POST /health/startup-metrics` | omit | Electron splash only |
| `GET /health` | omit as a tool (optional `avkit_health.liveness`) | Spawn probe, not an agent workflow |
| `GET /health/console` | omit | GUI console; agents do not tail the dock |

All download / transcript / tts / models / settings / dependencies routes are in the tables below. **Phase 8** `/conversions` → `avkit_convert` ([08-video-conversion.md](08-video-conversion.md)); **Phase 9** `/captures` → `avkit_capture` ([09-screenshot-capture.md](09-screenshot-capture.md)); do not implement those tools under MEU-18. Do not invent parallel paths.

### Destructive gate (M3, adapted)

This is a local single-user toolkit, not Zorivest’s GUI approval token. Destructive actions require `confirm: true` in the tool input (boolean, required on those actions). No MCP Guard / lock (deferred).

User confirmation (MEU-67, Session 30 plan D-24): the actions that delete or overwrite user files (`USER_CONFIRM_ACTIONS` = `avkit_capture.remove`, `flatten`, `revert`) also ask the person through MCP elicitation (form mode, 120 s) after `confirm: true` is parsed, and fetch only on an accept with `confirm: true`; a decline, a cancel, an error or the timeout refuse with `user_confirmation_refused` and no API call. When the client has no elicitation capability, or declines faster than a person could (250 ms; the Claude Code VS Code extension auto-declines without showing anything, `MCP-ELICITATION-VSCODE-AUTO-DECLINE`), the server asks with a native Windows Yes/No dialog instead, under the same rules (Session 30 A-11).

`DESTRUCTIVE_ACTIONS`:

- `avkit_download` → `remove`, `clear`
- `avkit_transcript` → `remove`
- `avkit_tts` → `cancel` (stops a running job; its partial output is removed)
- `avkit_convert` → `remove`, `clear` (Phase 8)
- `avkit_capture` → `remove` (Phase 9; **deletes files**), `flatten`, `revert` (MEU-67; **overwrite the image file**)

`cancel` / `stop` on queues stop work but are **not** in the set (reversible; jobs remain). `clear` is in the set (wipes the download queue).

### Descriptions (M7)

Server instructions: one-line workflow per toolset. Every tool/action description includes at least three of: `Workflow:`, `Prerequisite:`, `Returns:`, `Errors:`. Agents must be able to run add → start → list without this markdown file.

### Build (M4)

Live IDE uses `mcp-server/dist/`. After `src/` edits: `npm run build`, or `npm run dev` (tsx) while developing.

---

## Compound tools

One tool per module. `action` is a discriminated union. Wire enums match [Phase 4](04-rest-api.md) (`1080p`, `Pending`, `default`, …).

### `avkit_download`

**Workflow:** `add` → `start` → `list` (poll) → optional `pause`/`resume`/`cancel`. SABR: `sabr_get` / `sabr_check` / `sabr_force` / `sabr_clear`.  
**Prerequisite:** Backend healthy; cookies configured via `avkit_settings` if the video needs auth.

| action | REST | Notes |
|--------|------|-------|
| `add` | `POST /downloads` | `url`, `quality`, `audio_only`, `audio_format`. Returns `{ items }` (playlist → N jobs) |
| `list` | `GET /downloads` | Envelope `{ items, processor }` — not a bare array |
| `get` | `GET /downloads/{id}` | `id` required |
| `start` | `POST /downloads/start` | 202; 409 if already Processing |
| `pause` | `POST /downloads/pause` | After current item |
| `resume` | `POST /downloads/resume` | |
| `cancel` | `POST /downloads/cancel` | In-flight + processor Idle |
| `stop` | `POST /downloads/stop` | **Alias of cancel** (keeps old stub / `avkit_download_stop`) |
| `reorder` | `PUT /downloads/reorder` | `job_ids` permutation |
| `reset` | `POST /downloads/{id}/reset` | Failed only |
| `remove` | `DELETE /downloads/{id}` | Destructive; `confirm: true`; files stay |
| `clear` | `DELETE /downloads` | Destructive; `confirm: true`; archive stays |
| `sabr_get` | `GET /downloads/sabr` | Session; no probe |
| `sabr_check` | `POST /downloads/sabr/check` | Test extract |
| `sabr_force` | `POST /downloads/sabr/force` | |
| `sabr_clear` | `POST /downloads/sabr/clear` | |
| `cookies_test` | `POST /downloads/cookies/test` | mode / browser / profile / cookie_file path — never cookie bytes |
| `apply_defaults` | `POST /downloads/apply-defaults` | Update pending/blocked rows to current settings |

Returns must not include media bytes. `list`/`get` expose `file_path` pointers only.

### `avkit_transcript`

**Workflow:** `add` → `start` → `get`/`list` (poll) → `compile` if needed. Pause/resume/stop on the processor.  
**Prerequisite:** Channel URL; rate limits from settings. Resume is SQLite items, not `progress.json`.

| action | REST |
|--------|------|
| `add` | `POST /transcripts` (`channel_url`) |
| `list` | `GET /transcripts` (envelope) |
| `get` | `GET /transcripts/{id}` |
| `start` | `POST /transcripts/start` |
| `pause` | `POST /transcripts/pause` |
| `resume` | `POST /transcripts/resume` |
| `stop` | `POST /transcripts/stop` — parent → `Cancelled` |
| `requeue` | `POST /transcripts/{id}/requeue` — `Cancelled` → `Pending` |
| `retry` | `POST /transcripts/{id}/retry` — `Failed` → `Pending` |
| `reorder` | `PUT /transcripts/reorder` |
| `remove` | `DELETE /transcripts/{id}` — destructive; `confirm: true`; files stay |
| `compile` | `POST /transcripts/{id}/compile` |

**Never** return transcript body text. `get` may include item metadata (`path`, `word_count`, `status`) only.

There is no per-video queue action (Phase 1: `TranscriptItem` is a child record).

### `avkit_tts`

**Workflow:** `avkit_models` `load` → optional `prepare` → `generate` → `get` (poll) → `cancel` if needed.  
**Prerequisite:** A model must be loaded (`avkit_models.status.is_loaded`) or `generate` is 409.

| action | REST |
|--------|------|
| `prepare` | `POST /tts/prepare` — `{ text, enabled_steps }` → `{ cleaned_text }` (no job) |
| `generate` | `POST /tts/generate` — text, voice, speed, format, enabled_steps, source_kind, source_path |
| `get` | `GET /tts/{id}` |
| `cancel` | `DELETE /tts/{id}` — destructive confirm |
| `voices` | `GET /tts/voices` |

`generate` / `get` return `text_preview` + `text_hash`, **not** full text. Do not persist novels in the tool result beyond what the API returns.

### `avkit_models`

**Workflow:** `available` → `download` (poll `download_runtime`) → `load` → TTS generate → `unload`.  
**Prerequisite:** Disk + optional GPU. Not a job table.

| action | REST |
|--------|------|
| `available` | `GET /models/available` (each variant carries `devices`, `available` and `reason`) |
| `downloaded` | `GET /models/downloaded` |
| `download` | `POST /models/download` `{ variant_id }` (409 with the reason for a variant this build can't run) |
| `download_runtime` | `GET /models/download-runtime` |
| `load` | `POST /models/load` `{ variant_id, device }` |
| `unload` | `POST /models/unload` |
| `status` | `GET /models/status` |

### `avkit_settings`

**Workflow:** `get` a namespace → `set` leaf keys.  
**Prerequisite:** Namespace ∈ `downloader` \| `transcript` \| `tts` \| `app` \| `ui`.

| action | REST |
|--------|------|
| `get` | `GET /settings/{namespace}` |
| `set` | `PUT /settings/{namespace}` leaf-key object, `.strict()` |

Unknown keys → 422 (pass through ErrorEnvelope). Cookie **paths** only.

### `avkit_health`

| action | REST |
|--------|------|
| `dependencies` | `GET /health/dependencies` |

Optional `liveness` → `GET /health` (no auth). Omit `startup-metrics`.

### `avkit_convert` (Phase 8)

Canonical action table: [08-video-conversion.md](08-video-conversion.md) §MCP. Implement under MEU-32, not MEU-18.

**Workflow:** `add` (absolute paths) → `start` → `list` until processor `Idle`.  
**Prerequisite:** FFmpeg available (`avkit_health.dependencies`). Local files only.

### `avkit_capture` (Phase 9)

Canonical action table: [09-screenshot-capture.md](09-screenshot-capture.md) §MCP. Implement under MEU-38, not MEU-18.

**Workflow:** `capture` or `capture_interactive` → `image` → `annotate`.  
**Exception:** `image` returns PNG bytes (vision), up to the cap in [§Image size limit (residual)](#image-size-limit-residual). List/get stay path-only.

---

## Name map (old stub → this spec)

| Old tool name | Now |
|---------------|-----|
| `avkit_download_add` | `avkit_download` action `add` |
| `avkit_download_start` | `avkit_download` action `start` |
| `avkit_download_stop` | `avkit_download` action `stop` |
| `avkit_download_status` / `_list` | `avkit_download` action `list` or `get` |
| `avkit_transcript_add` | `avkit_transcript` action `add` |
| `avkit_transcript_start` | `avkit_transcript` action `start` |
| `avkit_transcript_status` | `avkit_transcript` action `get` / `list` |
| `avkit_transcript_compile` | `avkit_transcript` action `compile` |
| `avkit_tts_generate` | `avkit_tts` action `generate` |
| `avkit_tts_voices` | `avkit_tts` action `voices` |
| `avkit_tts_model_status` | `avkit_models` action `status` |
| `avkit_tts_model_load` | `avkit_models` action `load` |
| `avkit_settings_get` / `_set` | `avkit_settings` |

Do not register the old names as a second set (duplicate tools confuse agents).

---

## Client (`client.ts`)

```typescript
async function api<T>(method: string, path: string, body?: unknown): Promise<T>
```

- Prefix with `AVKIT_API_BASE` (already `/api/v1`).
- JSON + Bearer.
- Non-OK: throw or return `{ ok: false, status, error }` matching ErrorEnvelope — pick one and use it everywhere.
- Timeouts on long `add` (playlist extract) should be generous; `start`/`generate` return quickly (202/201) and agents **poll** `list`/`get`. No SSE.

---

## Server instructions (required text)

Publish on the MCP server so agents see it without this file. Minimum:

1. av-kit is a local YouTube **read/consume** toolkit. Never upload or write to YouTube.
2. Downloads: `avkit_download` add → start → list until processor `Idle`. Pause is queue-level; items have no `Paused` status.
3. Transcripts: add channel → start → get. Output is files (`output_dir`); tools return paths and counts, not transcript text.
4. TTS: load a model first; prepare is preview only; generate returns the job at once; poll get; cancel stops a running job.
5. Destructive actions require confirm: true. Download, transcript and convert remove/clear keep files on disk. Capture remove deletes the shot's files; capture flatten overwrites the image file (after a backup when capture.flatten_backup is on; a JPEG/WebP shot gets a new PNG copy instead); capture revert overwrites it from its newest backup. These three capture actions also ask the user in the IDE and are refused unless the user accepts; call them only when the user explicitly asked.
6. Settings use leaf keys (`quality`, not `downloader.quality`) and namespace.
7. Convert (Phase 8): `avkit_convert` add (absolute paths) → start → list. Sequential; GPU is auto. Never upload to YouTube.
8. Capture (Phase 9): `avkit_capture` capture / capture_interactive → image → annotate. Desktop app must be running for interactive overlay. Never upload to YouTube.

---

## Optional MCP resource

`avkit://settings/schema` — JSON of namespaces + keys + types + defaults from [06-gui.md](06-gui.md). Reference it from `avkit_settings` descriptions (M7). Not a second settings store.

---

<a id="mcp-live-audit-residual"></a>

## MCP live audit (residual)

> **MEU-68.** Registered 2026-09-30 from known issue `MCP-LIVE-AUDIT-WORKFLOW`. `mcp-server/tests` stub HTTP with `vi.fn()` and call `handleTool` in-process. `tools-parity` and `action-index` compare the surface against the hand-written tables in `mcp-server/tests/fixtures.ts`. Nothing drives the real server as an IDE client against the live API with real state. Adapt the Zorivest protocol in `_zorivest_mcp_tool_audit_skill.md`, which isn't published with this repository: the shape transfers, the domains do not. Reconciled 2026-10-01 against `ACTION_INDEX` (plan `2026-10-01-mcp-live-audit`, D-5).

| Rule | Contract | Source |
|------|----------|--------|
| Deliverables | `.agent/workflows/mcp-audit.md`, `.agent/skills/mcp-tool-audit/SKILL.md`, the runner `mcp-server/scripts/audit/` (`npm --prefix mcp-server run audit`), and a committed `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` (`mcp-audit-baseline.v1`). The report is written to `.agent/context/MCP/mcp-tool-audit-report.md` | Local Canon (Zorivest skill §Phase 5, §Related Files) |
| Client | The runner connects to the **built** server (`dist/index.js`) over stdio with the env `copyMcpConfig` writes (`AVKIT_API_TOKEN`, `AVKIT_APP_DATA`, with discovery through `backend.json`), using the SDK `Client`. It never imports toolset modules | Research-backed (SDK client; Inspector CLI was the alternative) |
| Backend | An **isolated** backend: the runner spawns `python -m avkit_api` with a throwaway app-data folder, and every output-path setting is moved under it and re-read before any lifecycle call (ISOLATION_GUARD). It never attaches to the user's running app | Human-approved 2026-10-01 (H-2) |
| Phase 1 Discovery | `tools/list` must serve the 8 `COMPOUND_TOOLS`; the action set is `_meta.action_descriptions`, compared with `ACTION_INDEX` in `registry.ts` and with the baseline. New, removed, ghost and unexpected entries are findings, and removed counts as a REGRESSION. A tool whose advertised `inputSchema` does not expose its actions is a finding | Zorivest §Phase 1; Local Canon `registry.ts` |
| Phase 2 Lifecycles | download `add→apply_defaults→reorder→list/get→start→cancel→reset→start→pause→resume→stop→remove→clear`; transcript `add→list/get→reorder→start→pause→resume→stop→requeue→retry→compile→remove`; tts `voices→prepare→generate→get→cancel`; convert `add→list/get→start→cancel→reset→reorder→start→pause→resume→cancel→remove→clear`; capture `capture→list→get→image→annotate→flatten→revert→capture_interactive→list_requests→remove` (MEU-67: `annotate→flatten→revert`); models `available→download→downloaded→load→status→unload`; settings `get→set→set (restore)`. Each step asserts **observable state** through the REST API or the filesystem (job row, output file, sidecar), not the envelope | Zorivest §Phase 2; Local Canon G25 ([emerging-standards](../../.agent/docs/emerging-standards.md)) |
| Destructive | Every destructive action runs with `confirm: true` on disposable fixtures, **and** the audit proves the same call without `confirm`, and with `confirm: false`, is refused with the state unchanged (`destructive.ts`) | Spec §Destructive actions |
| Phase 3 Functional | `avkit_health.liveness/dependencies`, `avkit_download.cookies_test/sabr_get/sabr_check/sabr_force/sabr_clear`, `avkit_convert.gpu/gpu_refresh`, `avkit_models.download_runtime`, with minimal valid params; record status / error / notes | Zorivest §Phase 3 |
| Phase 4 Regression | PASS→FAIL = REGRESSION, FAIL→FAIL = known issue (id), FAIL→PASS = FIXED (baseline updated), new = added. Only an authoritative Windows run with clean cleanup and no regression may write the baseline | Zorivest §Phase 4 |
| Cleanup | Every created job, shot, request, file and setting change is removed or restored before the report; residuals are listed as findings | Zorivest §Cleanup Contract |
| Where it runs | The authoritative run is a **local Windows stage** (real Kokoro model, ffmpeg, screen capture, network) recorded per [`cloud-local-collaboration.md`](../../.agent/docs/cloud-local-collaboration.md). The Linux container runs the same runner against a real spawned backend as a **non-authoritative subset**: proven environment-bound actions are `skip_env`, and the report header says so. The Vitest fake-backend suite covers the negative oracles | Local Canon |
| Evidence | One record per call (`actions.jsonl`) plus a summary JSON (`mcp-audit-summary.v1`) that the task/handoff validators can bind to (`evidence.v1`). The report header states the date, agent, backend version, commit, and tool/action counts. Tokens never appear in any output | Local Canon AGENTS §Artifact Naming |

<a id="image-size-limit-residual"></a>

## Image size limit (residual)

> **MEU-111.** Registered 2026-11-03 from known issue `MCP-IMAGE-OVER-STDIO-LIMIT`; Mat added it to release candidate 1 on 2026-11-04. `avkit_capture image` sends the file as base64 in one JSON line. The MCP TypeScript SDK's stdio client closes the transport when a line outgrows `STDIO_DEFAULT_MAX_BUFFER_SIZE` (10 MiB), and the client then loses every tool until it reconnects. The server doesn't crash. Measured with SDK 1.30.0 and 1.32.2: 7,860,000 B returns the image and 7,880,000 B closes the connection.

| Rule | Contract | Source |
|------|----------|--------|
| Cap | `IMAGE_FITS_STDIO`: `avkit_capture image` never sends an image the SDK's stdio reader can't take. The MCP cap is 7,800,000 B: 10,400,000 B of base64, leaving 85,760 B of the buffer for the envelope. | Known issue; measured limit above |
| Above the cap | A `payload_too_large` tool error that tells the agent to read `original_path` or `annotated_path` from `avkit_capture get`. The connection still answers later calls. An oversize shot can't be seen through MCP as an image; a downscaled preview can come later. | Known issue |
| SDK guard | A test imports `STDIO_DEFAULT_MAX_BUFFER_SIZE` from `@modelcontextprotocol/sdk/shared/stdio.js` and checks the cap's base64 length plus the envelope reserve against it, so an SDK release that lowers the buffer fails that test. | This section |
| REST | Stays at 15 MiB ([09 §REST API](09-screenshot-capture.md#rest-api)). OpenAPI and `tools/list` don't change: no description names the cap. | Phase 9 |
| Live audit | `capture.image` and `capture.image.annotated` pass on that refusal only when the REST image is larger than the cap. A refused smaller image, or a lost connection, fails the step. | §MCP live audit (residual) |
| Not tested | MCP clients other than the SDK's. | Known issue |

> **Delivered (Session 44).**
> - `IMAGE_MAX_BYTES` in `mcp-server/src/toolsets/capture.ts` is 7,800,000 B. `registry.ts` refuses a larger file with `payload_too_large`, naming `original_path` and `annotated_path`.
> - `tests/image-over-stdio.test.ts` runs the built server over real stdio with the SDK's client: a file at the cap arrives, and a larger one is refused while the connection keeps answering.
> - The live audit's `capture.image` steps accept that refusal only for a shot over the cap (`scripts/audit/plan.ts`, `tests/audit/capture-image-step.test.ts`).
> - AC-111.1 to AC-111.4.
> - Gate: the shared `session-gate.ps1` record in the MEU-111 handoff.
> - Plan `docs/execution/plans/2026-11-03-release-rc1/`.

## What this layer must not do

| Forbidden | Why |
|-----------|-----|
| Call yt-dlp / SQLite / Kokoro directly | Hexagonal; REST is the boundary |
| Return transcript text or video bytes | Phase 1 / 4. **Exception:** `avkit_capture.image` PNG only ([09-screenshot-capture.md](09-screenshot-capture.md)) |
| Invent routes or job types **outside Phase 4 index / Phase 8 / Phase 9** | `/conversions` + `avkit_convert` are Phase 8; `/captures` + `avkit_capture` are Phase 9 |
| MCP Guard / lock / unlock | Deferred ([06-gui.md](06-gui.md)) |
| Duplicate old `avkit_download_add` tools | Compound `action` only |
| `startup-metrics` tool | Electron only |
| Store the Bearer token in tool results or logs | Auth |
| SSE | Poll GET |

---

## Downstream planning notes

| Phase | Must follow this spec |
|-------|------------------------|
| **6 GUI** | Poll the same envelopes MCP uses (`{ items, processor }`). MCP mutations must show up via `refetchInterval` (emerging **G5**) |
| **7 Dist** | Ship the self-contained `mcp-server/bundle` (`index.mjs` + `LICENSES.txt`) as `resources/mcp-server`; the Settings MCP card's setup prompt registers it per client (the app executable with `ELECTRON_RUN_AS_NODE=1`, `AVKIT_APP_DATA`, no token). See [07 §MCP setup prompt (residual)](07-distribution.md#mcp-setup-prompt-residual) |

---

## Testing (Phase 5)

Vitest + mocked `fetch`:

| Case | Assert |
|------|--------|
| Each action | Method + path + JSON body match Phase 4 |
| Extra Zod key | Rejected before fetch (`.strict()`) |
| `remove` / `clear` without `confirm` | Rejected; no fetch |
| `list` download | Parses envelope, not a raw array |
| ErrorEnvelope 422/409 | Surfaced as tool error text with `code` + `message` |
| M7 | Descriptions contain Workflow / Prerequisite / Returns / Errors (rg gate; adapt path to `toolsets/` not `compound/`) |

No live YouTube in the default suite.

---

## Validation commands

Registered exact-receipt forms live in [`.agent/docs/commands.md`](../../.agent/docs/commands.md). Targeted:

```bash
npx tsc --noEmit
npx vitest run
```

After source edits for a live IDE: `npm run build` (M4) unless using `npm run dev`.
