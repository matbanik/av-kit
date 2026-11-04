---
project: "2026-08-19-p6-gui-shell"
date: "2026-08-19"
source: "docs/build-plan/06-gui.md"
meus: ["MEU-19"]
status: "approved"
template_version: "2.0"
---

# Implementation Plan: Phase 6 GUI Shell

> **Project**: `2026-08-19-p6-gui-shell`
> **Build Plan Section(s)**: [06-gui.md](../../../build-plan/06-gui.md) §Startup, IPC, layout, console; live-identity from [07-distribution.md](../../../build-plan/07-distribution.md)
> **Status**: `approved`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 7 — MEU-19 only

---

## Goal

Create the empty `ui/` Electron + React host: single-instance lock, live-identity orphan reap (no attach), allowlisted preload IPC, `apiFetch` to the existing `/api/v1`, AppShell + console + nav, and a **skeleton** default route. Add the missing FastAPI **runtime CLI** so PythonManager can spawn `--token` / `--mcp-token` / `--port 0` / `--app-data`. Do not implement Downloader/Transcript/TTS/Settings pages. Do not rewrite FastAPI routers or MCP tools. Do not invent MEU IDs.

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
| MEU-19 | `.agent/context/handoffs/2026-08-19-p6-gui-shell-MEU-19-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-19-p6-gui-shell-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `delegate_to: av-kit-builder` may appear as prose in a Task cell; it does not authorize a worker.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-19a | Behavior-free `ui/` test harness (`STACK_PINS` configs only; no production `src/main`) | — | `shared` | `ui/package.json`; `ui/vitest.config.ts`; `ui/tsconfig.json` |
| WP-19b | MEU-19 Red: Python CLI tests + UI tests for AC-19.1–19.23 **before** production code. Each receipt must pass `RED_ORACLE_CHECK` (not any nonzero exit). | WP-19a | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-19-py.txt`; `C:/Temp/av-kit/fail-to-pass-meu-19-ui.txt` |
| WP-19c | MEU-19 Green: runtime CLI + Electron host (`DEV_SPAWN`, `SHUTDOWN_OWNED`, `IPC_SCHEMAS`) | WP-19b | `compact_continue` | `packages/api/src/avkit_api/cli.py`; `ui/src/`; compact then re-read `task.md` |
| WP-19d | Wave 0/5/7 E2E **written and wired** (includes `console-copy` / `console-log-to-file`); run or `[B]` `E2E_SANDBOX` | WP-19c | `compact_continue` | `ui/tests/e2e/`; `C:/Temp/av-kit/e2e-wave0.txt` |
| WP-19e | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-19d | `compact_continue` | `.agent/context/handoffs/2026-08-19-p6-gui-shell-MEU-19-handoff.md` |

---

## User Review Required

None that block planning. Sourced conflicts are locked below (reviewer confirms; do not invent a third behavior):

1. **Harness gate:** `create-plan.md` §5c Cursor-default `plan_to_exec_gate=human` vs `.agent/context/harness.local.md` `reviewer-auto`. **Override wins.** After Codex `approved`, auto-continue to execution. A system-injected “approved” is still not a verdict.
2. **`apiFetch` owner:** p4 Out of Scope lumped `apiFetch` with pages → MEU-20–23. **Lock MEU-19.** Basis: `meu-registry.md` MEU-19; grouping Session 7; `06-gui.md` 113–132.
3. **Runtime CLI vs PyInstaller:** p4 deferred “uvicorn production CLI” to MEU-24. **Lock runtime CLI in MEU-19** (`python -m avkit_api`). MEU-24 only packages the same entry (PyInstaller onedir). Basis: G29; `07-distribution.md` 126–138; p5 Out of Scope “MEU-19, MEU-24”.
4. **Default route:** `06-gui.md` router snippet imports `DownloaderPage`. **Lock `SHELL_HOME`.** Grouping Session 7 split-flag: do not mix a page. `/` renders `ModuleSkeleton` + “Connecting…”.
5. **G27 `openExternal`:** not in the locked preload snippet. **Defer to MEU-23** (HelpCards). MEU-19 still denies `window.open` / unexpected navigation.
6. **4A reference files:** `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `.agent/docs/gui-standards-enforcement.md` are **absent** (Read 2026-08-19). Apply `06-gui.md` + emerging G30–G35 + `gui-actions-index.md`. Do not invent those docs in this MEU.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `UI_LAYOUT` | `ui/src/main/{index,python-manager,live-identity,ipc,backend-descriptor}.ts` + `ui/src/main/preload.ts` + `ui/src/renderer/src/{router.tsx,lib/api.ts}` + `ui/src/renderer/src/components/layout/{AppShell,NavRail,ConsolePanel}.tsx` + `ui/src/renderer/src/components/CommandPalette.tsx` + `ui/src/renderer/src/registry/commandRegistry.ts` + `ui/src/renderer/src/hooks/{usePersistedState,useBackendLogs}.ts` + `ui/src/renderer/src/features/shell/ShellHome.tsx` + `ui/src/renderer/splash.html` + `ui/package.json` | Spec layout |
| `STACK_PINS` | `electron ^42.5`, `electron-vite ^5`, `react ^19`, `@tanstack/react-query ^5`, `@tanstack/react-router ^1` + `createHashHistory()`, `zustand ^5`, `tailwindcss ^4` + `@tailwindcss/vite`, `electron-store ^8`, `fuse.js ^7`, `zod ^3`, `vitest ^3`, `@playwright/test ^1.58`, `babel-plugin-react-compiler ^1` | Spec stack; Local Canon zorivest `ui/package.json` |
| `WEB_PREFS` | `{ nodeIntegration: false, contextIsolation: true, sandbox: true, webSecurity: true }` | Spec 76 |
| `IPC_CHANNELS` | `get-backend-url`, `get-token`, `startup-metric`, `show-directory-dialog`, `show-file-dialog`, `open-path`, `show-item-in-folder`, `read-clipboard-text`, `write-clipboard-text`, `read-text-file`, `copy-mcp-config`, `get-log-snapshot`, `console-log-batch` | Spec 83–101 |
| `IPC_SCHEMAS` | every renderer→main channel has a Zod `.strict()` schema (or `z.undefined()` / empty-object for no-payload). Extra keys and wrong types fail **before** dialog/FS/clipboard/spawn. `console-log-batch` is main→renderer only (not in the renderer invoke census). | r1 F2; Boundary Input Contract |
| `IPC_NO_PAYLOAD` | `{get-backend-url, get-token, show-directory-dialog, read-clipboard-text, get-log-snapshot}` — payload must be `undefined` or `{}`; anything else → reject, side-effect count 0 | r1 F2 |
| `IPC_PAYLOAD_SHAPES` | `startup-metric`: `{ key: enum STARTUP_METRIC_KEYS, value: number, timestamp: number }`; `show-file-dialog`: `{ filters?: { name: string, extensions: string[] }[] }`; `open-path` / `show-item-in-folder`: `{ target: string.min(1) }`; `write-clipboard-text`: `{ text: string }`; `read-text-file`: `{ maxBytes?: number.int().positive().max(2_097_152) }`; `copy-mcp-config`: `{ pinEndpoint?: boolean }` | Spec 83–101; r1 F2 |
| `IPC_STRICT_CENSUS` | parametrized extra-key + type-fail oracle over every renderer→main `IPC_CHANNELS` row. Each case: handler reject + dialog/FS/clipboard/spawn count `0`. | r1 F2; PR-8 |
| `PRELOAD_API` | `window.api` methods in `06-gui.md` 83–101. Never expose `ipcRenderer`. | Spec; Research-backed [context isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation) |
| `ATOMIC_REPLACE` | descriptor write = temp file in `{app_data}` + `os.replace` (single atomic replace). Not write-in-place. | Spec 07 73 “atomically”; r1 F2 adjacent |
| `SHUTDOWN_OWNED` | two producers, same retirement: (1) Electron quit / `before-quit`: SIGTERM/taskkill **only** `owned.pid`, wait until that pid exits; (2) unexpected `owned` child `exit`/`close` while Electron stays open: do **not** SIGTERM anyone else. Both paths delete or tombstone `DESCRIPTOR_PATH` and `PORT_SIBLING` so MCP cannot keep a live `api_base`. Never signal a refused/foreign pid. Backend lifespan then cancels processors (existing FastAPI lifespan). | Spec 07 124, 189–191; r1 F4; r2 F2 |
| `BIND_HOST` | `127.0.0.1` only. Never `0.0.0.0`. | Spec 07 73; p4 |
| `SPAWN_FLAGS` | `--token <GUI_NONCE> --mcp-token <PROVISIONED> --port 0 --app-data <path>` | Spec 07 126–137 |
| `PYTHON_IMAGE` | unpackaged only: one-shot resolve `uv run python -c "import sys; print(sys.executable)"` → realpath. That string is the spawn executable. Never spawn the `uv` wrapper as the owned child. | this plan r1 F3 |
| `DEV_SPAWN` | unpackaged: spawn `[PYTHON_IMAGE, "-m", "avkit_api", ...SPAWN_FLAGS]`. Packaged: spawn `PACKAGED_BACKEND` with the same flags. `owned.pid` = `ChildProcess.pid` of that spawn. Readiness requires `descriptor.pid === owned.pid` **and** `LIVE_QUERY.image === OURS_EXE`. | Spec 07 189; r1 F3 |
| `PACKAGED_BACKEND` | `{process.resourcesPath}/avkit-backend/avkit-backend.exe` | Spec 07 102 |
| `OURS_EXE` | `app.isPackaged ? realpath(PACKAGED_BACKEND) : PYTHON_IMAGE` | this plan; Spec 07 `ours.exe`; r1 F3 |
| `OURS_APP_DATA` | Phase 2 resolver: Windows `%LOCALAPPDATA%/av-kit`, else `~/.avkit/`, overridable by `--app-data` / `AVKIT_APP_DATA` | Local Canon `02-infrastructure.md` 57; p5 `DEFAULT_APP_DATA` |
| `DEFAULT_APP_DATA` | same as `OURS_APP_DATA` default | p5 |
| `AUTH_TOKENS` | `frozenset({gui_nonce, mcp_token})` passed to `create_app(tokens=…)` | p4; Spec 07 134–135 |
| `GUI_NONCE` | ephemeral UUID per Electron launch. Never written to `backend.json`. Never used as MCP token. | Spec 07 94–96 |
| `MCP_TOKEN_FILE` | `{app_data}/mcp-token.txt` — create if missing (stable). Main reads it for `--mcp-token` and `copyMcpConfig`. Renderer never receives it. | Spec 07 135; p5 `MCP_TOKEN_SOURCE` |
| `DESCRIPTOR_PATH` | `{app_data}/backend.json` | Spec 07 75 |
| `PORT_SIBLING` | `{app_data}/backend-port.txt` (digits only; not SoT) | Spec 07 94 |
| `DESCRIPTOR_SCHEMA` | keys exactly `{schema_version, pid, instance_id, executable_path, host, port, bind, api_base, app_data, started_at}`. `schema_version === 1`. `extra` refuse if pid live. | Spec 07 79–122; p5 RULE-3 |
| `DESCRIPTOR_NO_SECRETS` | file must not contain `token`, `mcp-token`, `Authorization`, or nonce/MCP values | Spec 07 94 |
| `READY_LINE` | stdout `AVKIT_READY port={n} instance={id}` after listen + atomic descriptor write | Spec 07 73 |
| `API_PREFIX` | `/api/v1` | p4 |
| `API_BASE` | `http://127.0.0.1:{port}/api/v1` published on descriptor after bind. Never expose port `0` to the renderer. | Spec 57, 136 |
| `AUTH_EXEMPT_PATHS` | `{GET /api/v1/health}` only | p4 |
| `ERROR_ENVELOPE` | `{ "error": { "code": str, "message": str, "details": object \| null } }` | p4 |
| `VOID_204_PATHS` | `{DELETE /downloads/{id}, DELETE /downloads, DELETE /transcripts/{id}, DELETE /tts/{id}, POST /models/unload, POST /health/startup-metrics}` | Spec 132 |
| `LIST_ENVELOPE` | `{ items, processor }` — `apiFetch` returns the JSON body as-is | p4 / Spec 1145 |
| `SINGLE_INSTANCE` | `app.requestSingleInstanceLock()`. Loser focuses peer via winner `second-instance` and **exits**. Loser does not spawn, attach, or kill. | Spec 07 117; Research-backed [app.requestSingleInstanceLock](https://www.electronjs.org/docs/latest/api/app#apprequestsingleinstancelockadditionaldata) |
| `LIVE_IDENTITY_PROOF` | query live pid image + cmdline. Refuse (no kill) if query fails, image ≠ `OURS_EXE`, cmdline lacks `--app-data` = `OURS_APP_DATA`, descriptor/`live` mismatch, or unsupported schema + live pid. Owned orphan = lock held + proof succeeds → SIGTERM, wait exit, spawn **new** `GUI_NONCE`. | Spec 07 105–124 |
| `LIVE_QUERY` | Windows: `QueryFullProcessImageNameW` + process command line. Linux: `/proc/{pid}/exe` + cmdline. macOS: `proc_pidpath` + `KERN_PROCARGS2`. Normalize realpath / `\\?\` / case before compare. | Spec 07 105 |
| `SECRET_PATH_DENY` | `{app_data}/mcp-token.txt`, `{app_data}/backend.json`, `{app_data}/avkit.db`, any path matching `*token*`, URLs. `{app_data}` is not a generic readable root. | Spec 104–110 |
| `READ_TEXT_EXTS` | `{.txt, .md}` only. `maxBytes` default 2 MiB. Always dialog in main; renderer cannot pass a raw path. | Spec 106–107 |
| `COPY_MCP_RESULT` | `{ ok: true }` only. Clipboard JSON from `07-distribution.md` (token stays in main). | Spec 110 |
| `SEQ_OWNER` | `HealthService` is the only `seq` allocator. GUI never assigns backend `seq`. | Spec 331; R2-4 |
| `IPC_STDOUT_ID` | stdout lines without `seq` → `source: stdout`, `id: ipc:{n}` (main counter). Never reuse backend `seq`. | Spec 333–334 |
| `CONSOLE_POLL` | `GET /health/console?after_seq=` at 500 ms expanded, 5 s collapsed. Authoritative ring. | Spec 332 |
| `CONSOLE_REDACT` | redact Bearer tokens, cookie bytes, MCP token values before display | Spec 337 |
| `STARTUP_METRIC_KEYS` | `startup.python_spawn_ms`, `startup.renderer_load_ms`, `startup.shell_paint_ms`, `startup.window_show_ms`, `startup.data_ready_ms`, `startup.lazy_preload_ms` | Spec 65–70 |
| `SHELL_HOME` | route `/` component is `ShellHome` (`ModuleSkeleton` + “Connecting to backend…”). Not `DownloaderPage`. | grouping Session 7; this plan |
| `LAZY_PLACEHOLDERS` | `/transcript`, `/tts`, `/settings` lazy-load the same `ModuleSkeleton` until MEU-21–23 | grouping; Spec 192–201 adapted |
| `SHELL_NAV` | `nav:downloader` `/` Ctrl+1; `nav:transcript` `/transcript` Ctrl+2; `nav:tts` `/tts` Ctrl+3; `nav:settings` `/settings` Ctrl+,; `nav:collapse` Ctrl+B → `ui.rail.collapsed` | Spec 261–273; `gui-actions-index.md` 9–13 |
| `SHELL_PALETTE_IDS` | `{nav:downloader, nav:transcript, nav:tts, nav:settings, nav:collapse}` registered now. `palette:open` is Ctrl+K (not palette-eligible). Page actions stay unregistered until their MEU. | Spec 283–293; grouping MEU-23 audit |
| `PERSIST_UI_KEYS` | `ui.rail.collapsed` (bool), `ui.panel.console.height` (number, default 200) via `usePersistedState` / electron-store. **Not** API settings. | Spec 273, 327; p4 `SETTINGS_UI_API_KEYS` |
| `WAVE0_TESTIDS` | `nav-downloader`, `nav-transcript`, `nav-tts`, `nav-settings`, `nav-collapse` | Spec 1099 |
| `CONSOLE_SHELL_ACTIONS` | `{console:filter, console:search, console:clear, console:copy, console:collapse}` plus yt-dlp debug toggle and `app.log_to_file` toggle. `console:copy` → IPC `write-clipboard-text`. Log-to-file → `PUT /settings/app` leaf `log_to_file` (backend persist; Spec 336). | Spec 316–336; `gui-actions-index.md` 64–68; r1 F5 |
| `WAVE5_TESTIDS` | `console-panel`, `console-filter`, `console-search`, `console-clear`, `console-copy`, `console-collapse`, `console-ytdlp-toggle`, `console-log-to-file` | Spec 1104 + r1 F5 |
| `WAVE7_TESTIDS` | `command-palette`, `command-palette-input` | Spec 1106 |
| `E2E_FILES` | `ui/tests/e2e/launch.test.ts` (3), `console-panel.test.ts` (3), `command-palette-nav.spec.ts` (2), `test-ids.ts`, `global-setup.ts`, `global-teardown.ts` | Spec 1098–1120 |
| `E2E_SANDBOX` | un-run E2E in agent sandbox → `[B]` + CI follow-up (`xvfb-run` / `windows-latest`). Tests stay written and wired. | known-issue policy; Spec 1120 |
| `G17_JSON` | `apiFetch` sets `Content-Type: application/json` unless `body instanceof FormData` | emerging G17 |
| `CSP_IMG` | renderer CSP includes `img-src 'self' http://localhost:* http://127.0.0.1:* data:` | emerging G16 |
| `REGRESSION_TESTS` | p5 H1-2 Python set (do not drop the 290) | p5 carry-forward |
| `SCAN_G36_ARGS` | `it.skip`, `describe.skip`, `test.skip`, `it.todo`, `xit`, `xdescribe`, `it.only`, `describe.only`, `test.only`, `fit`, `fdescribe` under `ui/tests/unit` and `tests/` Python | G36; r2 F3 |
| `SCAN_PLACEHOLDER_ARGS` | `TODO`, `FIXME`, `NotImplementedError` under `ui/src` and `packages/api/src/avkit_api` | anti-placeholder |
| `HANDOFF_COUNT` | `1` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-19-p6-gui-shell-MEU-19-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-19-p6-gui-shell` | MEU `execution_plan` |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-19-p6-gui-shell/` | phase `"6"` |
| `HUB_NEXT_AFTER` | `/create-plan p6-gui-downloader` | grouping pathway #8 |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | p5 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-19-p6-gui-shell-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-19-p6-gui-shell/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only; `--expected-mode implementation` | p2 Human-approved |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read.txt` written **once** before the MEU-19 handoff | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE |
| `VITEST_ALLOW_ONLY` | `ui/vitest.config.ts` has `test.allowOnly: false`. Every `npx vitest run` invocation passes `--allowOnly=false`. | G36; Vitest `allowOnly`; r2 F3 |
| `UI_ESLINT` | after Red tests exist: `npx eslint src/ tests/ --max-warnings 0` (includes `ui/tests/unit`) | G36; r2 F3 |
| `RED_ORACLE` | each FAIL_TO_PASS receipt must contain an allow-marker (`FAILED` / `AssertionError` / `ModuleNotFoundError: No module named 'avkit_api'` for Python; `FAIL` / `AssertionError` / `Cannot find module` for UI) and must not contain a deny-marker (`INTERNALERROR`, `no tests ran`, `No test files found`, `ERR_LOAD_CONFIG`, missing toolchain). Python `ERROR collecting` is allowed **only** with the `avkit_api` ModuleNotFoundError (M5). | r1 F1; r2 F1 |
| `RED_ORACLE_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-19-p6-gui-shell/assert-red-oracle.ps1 -Kind <py\|ui> -Receipt <path>` — sole executable owner of `RED_ORACLE`. | r2 F1; PR-9 |
| `HANDOFF_MARKER_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-19-p6-gui-shell/assert-handoff-markers.ps1` — the **only** executable owner of `HANDOFF_BUNDLE_MARKERS`. Task rows reference this name; they must not restate the marker list. | r1 F7; PR-9 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p5 |
| `MEU19_TOUCHED` | `UI_LAYOUT` + `packages/api/src/avkit_api/__main__.py` + CLI module + `tests/unit/test_backend_cli.py` + `tests/integration/test_backend_spawn.py` + `ui/tests/` | MEU-19 files |
| `MEU_SCOPED_GATE` | `ui`: `npx tsc --noEmit` + `npx vitest run --allowOnly=false` + `UI_ESLINT` + `npm run build`; Python: `uv run pytest tests/unit/test_backend_cli.py tests/integration/test_backend_spawn.py -x --tb=short -v` + `uv run pyright packages/api` + `uv run ruff check packages/api`; + `SCAN_PLACEHOLDER` + `SCAN_G36` + `HANDOFF_MARKER_CHECK` + AC-19.* | AGENTS MEU gate |
| `OPENAPI_CHECK` | because `packages/api/` gains a CLI module, run G8 `--check` (expect no route drift). `-o` only on FAIL. | G8 |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| Domain / services / FastAPI routes | YES | MEU-14–16 `approved`. Do not rewrite routers. |
| Dual Bearer + `ERROR_ENVELOPE` | YES | p4 `AUTH_TOKENS` |
| `GET /health` unauthenticated | YES | `health.py` 35–41 |
| `GET /health/console` + `POST /health/startup-metrics` Bearer | YES | `health.py` 67–103 |
| Runtime CLI (uvicorn + descriptor) | NO → **this MEU** | p4 deferred spawn |
| Electron main / preload / AppShell | NO → **this MEU** | `ui/` absent |
| MCP tools | YES — do not rewrite | MEU-17/18 `approved` |
| Downloader/Transcript/TTS/Settings pages | NO — **later MEUs** | grouping 8–11 |

---

## create-plan §4A — GUI Element Compliance

**Triggered:** AppShell/nav/console/palette create `<button>`, `<input>`, `<select>`, status badges in `ui/src/renderer/`.

| Check | Result |
|-------|--------|
| `docs/gui-element-reference.md` | **Absent** — use emerging G31–G35 + `06-gui.md` tokens (`bg-accent`, `text-fg`, duration tokens) |
| `docs/gui-button-index.md` / input / output indexes | **Absent** — map via table below |
| E2E written+wired | `E2E_FILES` + `WAVE0_TESTIDS` / `WAVE5_TESTIDS` / `WAVE7_TESTIDS` |
| G30–G35 / E2 | G30 on console level `<select>` (inline theme-aware styles or a local `getG30Styles` until `SelectInput` exists). G31 `bg-accent` only. G32 no raw hex in `className` (G30 inline exception). G33 duration tokens. G34 variants below. G35 tiers below. E2 = `E2E_FILES`. |
| G20 | no `window.confirm/alert/prompt` in shell |
| G11 | palette + Ctrl+K owned by `AppShell` via `av-kit:open-palette` |
| G16 | `CSP_IMG` |
| G27 | deferred MEU-23 |

| Element | Variant / size | testid | Feedback |
|---------|----------------|--------|----------|
| Nav rail items | ghost; active = `bg-accent` bar | `WAVE0_TESTIDS` | T0 route change |
| Collapse | ghost sm | `nav-collapse` | T0 persist `ui.rail.collapsed` |
| Palette trigger | secondary sm | header control; palette uses `WAVE7_TESTIDS` | T0 open |
| Console filter | G30 select | `console-filter` | T0 filter |
| Console search | text input | `console-search` | T0 filter |
| Console clear | secondary sm | `console-clear` | T1 view clear |
| Console copy | secondary sm | `console-copy` | T1 clipboard via `write-clipboard-text` |
| Console collapse | ghost sm | `console-collapse` | T0 persist height/visible |
| yt-dlp debug | checkbox | `console-ytdlp-toggle` | T0 filter |
| Log to file | checkbox | `console-log-to-file` | T1 `PUT /settings/app` `log_to_file` |
| Connection badge | status | header | T1 connected/disconnected |
| Confirmations | none in MEU-19 | — | — |

---

## MEU-19 — `gui-shell`

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| CLI argv | `avkit_api` argparse / typed parser | `SPAWN_FLAGS`; `--port` int ≥ 0; `--app-data` existing-or-creatable dir; tokens non-blank | unknown flags → exit ≠ 0 | exit 2 | n/a (no update path) | Spec 07 126–137 |
| `backend.json` write | `DESCRIPTOR_SCHEMA` | `schema_version === 1`; `pid` = os.getpid(); `api_base` contains `/api/v1`; no secrets | unknown keys refused when pid live (`LIVE_IDENTITY_PROOF`) | refuse spawn/kill | overwrite only after listen / owned-orphan | Spec 07 79–122 |
| IPC invoke payloads | `IPC_SCHEMAS` (Zod `.strict()` per renderer→main channel) | `IPC_NO_PAYLOAD` + `IPC_PAYLOAD_SHAPES`; `maxBytes` ≤ 2 MiB | `.strict()` — extra keys reject; no ignore-after-parse | structured error; `IPC_STRICT_CENSUS` side-effect count 0 | n/a | Spec 83–110; r1 F2 |
| `apiFetch` JSON | existing Pydantic routes; client parses `ERROR_ENVELOPE` | Bearer `GUI_NONCE`; `G17_JSON` | server `extra=forbid` already | throw `ApiError` with status + envelope | n/a | Spec 115–132; p4 |
| electron-store `PERSIST_UI_KEYS` | `usePersistedState` | collapsed bool; height number ≥ 80 | unknown keys persist locally only; never PUT to API | coerce / default | same keys | Spec 273, 327 |
| File dialog (`readTextFile`) | main | `READ_TEXT_EXTS`; `SECRET_PATH_DENY` | user pick of denied path → reject | error to renderer, no bytes | n/a | Spec 106–108 |

### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-19.1 | unit | **Control `SPAWN_FLAGS`.** Observable: parser result / process exit. Chain: `python -m avkit_api` → argparse → `create_app(tokens=AUTH_TOKENS)`. Negative: missing `--token` or blank `--mcp-token` → exit ≠ 0 and no listen. | Spec 07 126–137 | bind without tokens |
| AC-19.2 | integration | **Control `DESCRIPTOR_SCHEMA` + `READY_LINE` + `ATOMIC_REPLACE`.** Observable: file bytes + stdout line + bound port ≠ 0. Chain: uvicorn listen `BIND_HOST`/`--port 0` → `ATOMIC_REPLACE` `DESCRIPTOR_PATH` + `PORT_SIBLING` → print `READY_LINE`. `pid` equals the CLI process; `api_base` ends with `API_PREFIX`. | Spec 07 73–94; Research-backed [uvicorn port 0](https://uvicorn.dev/settings/) | write descriptor before listen; bind `0.0.0.0`; in-place non-atomic write |
| AC-19.3 | unit | **Control `DESCRIPTOR_NO_SECRETS`.** Observable: descriptor JSON keys/values + captured stdout/stderr. Chain: CLI write + structlog. Negative: nonce or MCP token substring appears in file or logs → fail. | Spec 07 94, 257 | echo `--token` into log |
| AC-19.4 | integration | **Control `AUTH_TOKENS` / `AUTH_EXEMPT_PATHS`.** Observable: HTTP status. Chain: spawned app → `GET /health` 200 no Bearer; `GET /health/console` 401 without Bearer; either token 200. | p4 AC-14.2; Spec 07 139 | GUI nonce rejected |
| AC-19.5 | unit | **Control `SINGLE_INSTANCE`.** Observable: spawn-count + `app.quit` / focus call. Chain: `requestSingleInstanceLock` → if false, exit; if true, `second-instance` focuses. Negative: loser still calls `spawnBackend` → fail. | Spec 07 117; [Electron app.md](https://www.electronjs.org/docs/latest/api/app) | loser SIGTERM foreign pid |
| AC-19.6 | unit | **Control `LIVE_IDENTITY_PROOF`.** Observable: decision enum `{spawn, reap_then_spawn, refuse}`. Chain: injected `LIVE_QUERY` → proof table (07 108–122) including PID-reuse (file claims our exe, live image foreign → refuse) and query failure → refuse. Negative: refuse path issues SIGTERM → fail. | Spec 07 105–124; R2-1 | kill on query fail |
| AC-19.7 | unit | **Control `WEB_PREFS` + `IPC_CHANNELS` + `IPC_SCHEMAS`.** Observable: `webPreferences` + handler registry + Zod parse errors. Chain: `BrowserWindow` ctor → `ipcMain.handle` → `IPC_SCHEMAS.parse`. Negative: unknown channel invoke resolves successfully → fail. `ipcRenderer` is not on `window`. | Spec 76–101; [context isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation); r1 F2 | expose `ipcRenderer.send` |
| AC-19.8 | unit | **Control `SECRET_PATH_DENY` + `READ_TEXT_EXTS`.** Observable: handler return / thrown code. Chain: `read-text-file` / `open-path` / `show-item-in-folder` after `IPC_SCHEMAS`. Negative: renderer-supplied raw path is read; denied secret file or `.exe` / URL succeeds → fail. | Spec 104–110 | read `mcp-token.txt` |
| AC-19.9 | unit | **Control `COPY_MCP_RESULT`.** Observable: invoke return + clipboard write happens in main. Chain: `copy-mcp-config` reads `MCP_TOKEN_FILE`. Negative: return body contains token → fail. | Spec 110; R2-2 | return token JSON to renderer |
| AC-19.10 | unit | **Control `apiFetch` + `VOID_204_PATHS` + `ERROR_ENVELOPE` + `G17_JSON`.** Observable: `Authorization` header, parsed body, thrown `ApiError`. Chain: `getBackendUrl`+`getToken` → `fetch`. Parametrized: every `VOID_204_PATHS` row returns `undefined`; one 422 envelope throws `ApiError(422, code, message)`. FormData omits JSON content-type. Negative: 204 JSON.parse crash; 422 treated as success. | Spec 115–132; G17 | `JSON.parse('')` on 204 |
| AC-19.11 | integration | **Control `SHELL_HOME` + `SHELL_NAV`.** Observable: hash path + `WAVE0_TESTIDS` present. Chain: `createHashHistory` → `AppShell` → rail. Negative: `/` mounts a Downloader URL form / `url-input` → fail. Lazy routes show skeleton, not page chrome. | grouping; Spec 159–216, 261–273 | import DownloaderPage |
| AC-19.12 | unit | **Control `SEQ_OWNER` + `IPC_STDOUT_ID`.** Observable: view-model keys. Chain: `useBackendLogs` + main stdout tail. Ring events key by `seq`; stdout-only by `ipc:*`. Clear clears view only. Negative: GUI allocates a numeric `seq` or dedups stdout against ring by `seq` → fail. | Spec 330–336; R2-4 | second seq allocator |
| AC-19.13 | unit | **Control `API_BASE` IPC.** Observable: invoke results. Chain: `get-backend-url` / `get-token` wait for descriptor/`READY_LINE`. Negative: returns `http://127.0.0.1:0` or a pre-listen URL → fail. Never `sendSync`. | Spec 57, 84–85 | `sendSync` port 0 |
| AC-19.14 | unit | **Control `STARTUP_METRIC_KEYS`.** Observable: `POST /health/startup-metrics` uses `GUI_NONCE` (not MCP token). Chain: `logStartupMetric` → main → `apiFetch` or main fetch. Negative: MCP token in Authorization → fail. | Spec 61, 07 192 | MCP Bearer on metrics |
| AC-19.15 | integration | Wave 0 E2E **written and wired** (`launch.test.ts` 3 tests, `WAVE0_TESTIDS`). Run via `npm run build && npx playwright test launch.test.ts`. Sandbox no-display → `[B]` `E2E_SANDBOX` with receipt; test files still exist. | Spec 1098–1120; E2 | missing testid |
| AC-19.16 | integration | Waves 5 and 7 **written and wired** (`WAVE5_TESTIDS`, `WAVE7_TESTIDS`). Same `[B]` rule as AC-19.15. | Spec 1104–1106; Console is MEU-19 | console panel without E2E file |
| AC-19.17 | unit | **Control `SHELL_PALETTE_IDS`.** Observable: registry id set. Chain: `commandRegistry.ts`. Negative: `download:add` (or any non-shell palette id) is registered and invoked → fail. Ctrl+K / `av-kit:open-palette` owned by `AppShell` (G11). | Spec 283–293; G11; MEU-23 audit | register page actions |
| AC-19.18 | unit | `PERSIST_UI_KEYS` round-trip; theme default dark via CSS tokens (no raw hex in `className`). Window bounds restore via electron-store. | Spec 273, 327, 1213; G32 | PUT rail.collapsed to API |
| AC-19.19 | unit | **Control `CONSOLE_SHELL_ACTIONS`.** Observable: `WAVE5_TESTIDS` + clipboard write + settings PUT. Chain: ConsolePanel → `write-clipboard-text` (`console:copy`) and `PUT /settings/app` `{ log_to_file }` (`console-log-to-file`). Also `CONSOLE_POLL` + `CONSOLE_REDACT` + yt-dlp filter + five levels. Negative: copy path never calls IPC; log-to-file only flips local state → fail. | Spec 316–336; `gui-actions-index.md` 67; r1 F5 | missing `console:copy` |
| AC-19.20 | unit | G36 / anti-placeholder on `MEU19_TOUCHED`. Deny unexpected navigation / `window.open`. `CSP_IMG` present. | G36; Spec 76; G16 | `test.skip` in unit tests |
| AC-19.21 | unit | **Control `IPC_STRICT_CENSUS`.** Observable: reject + side-effect counters (dialog/FS/clipboard/spawn). Chain: each renderer→main channel → `IPC_SCHEMAS`. Negative: extra key or wrong type still invokes `dialog.showOpenDialog` / `clipboard.write` / `spawn` → fail. | r1 F2; Boundary Input Contract | ignore extra keys |
| AC-19.22 | unit | **Control `DEV_SPAWN`.** Observable: spawn argv[0] === `PYTHON_IMAGE` (unpackaged) or `PACKAGED_BACKEND`; readiness flag. Chain: PythonManager resolve → spawn → wait descriptor. Negative: `descriptor.pid !== owned.pid` or live image ≠ `OURS_EXE` still resolves `get-backend-url` → fail. Never treat a `uv.exe` wrapper pid as owned. | Spec 07 189; r1 F3 | accept wrapper pid / mismatched descriptor |
| AC-19.23 | unit | **Control `SHUTDOWN_OWNED`.** Observable: signal target pid + descriptor existence after (a) quit and (b) unexpected owned-child exit. Chain A: `app.quit` / `before-quit` → SIGTERM `owned.pid` only → retire `DESCRIPTOR_PATH` + `PORT_SIBLING`. Chain B: owned `ChildProcess` `exit`/`close` while Electron stays open → retire the same files with no extra SIGTERM. Negative: refused foreign pid receives SIGTERM; quit leaves a live `api_base`; **or unexpected owned-child death leaves a live `api_base`** → fail. | Spec 07 124, 189–191; r1 F4; r2 F2 | crash leaves `backend.json` targeting dead port |

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Splash + parallel main window + PythonManager | Spec | `06-gui.md` 19–55 |
| Single-instance + live-identity table | Spec | `07-distribution.md` 96–124; A1/R2-1 |
| Unpackaged `OURS_EXE` | Research-backed + Local Canon | `PYTHON_IMAGE` + `DEV_SPAWN`; never own the `uv` wrapper pid |
| IPC allowlist + path rules | Spec | `06-gui.md` 74–110 |
| `apiFetch` 204 / envelope | Spec | `06-gui.md` 113–132 |
| AppShell / nav / console / palette shell | Spec + grouping | `CONSOLE_SHELL_ACTIONS` including copy + log-to-file; pages deferred |
| Owned-child shutdown / descriptor tombstone | Spec | `SHUTDOWN_OWNED` on quit **and** unexpected owned-child exit; 07 124, 189–191 |
| `SHELL_HOME` vs DownloaderPage | Local Canon | grouping Session 7 split-flag |
| Runtime CLI in this MEU | Local Canon + Spec | G29; 07 CLI; p4/p5 spawn deferral |
| Hash history + lazy placeholders | Spec adapted | TanStack hash; lazy modules are skeletons |
| E2E waves 0/5/7 | Spec | wave schedule; console/palette are shell |
| FormData content-type | Research-backed | G17 vs spec snippet — G17 wins for FormData |
| `openExternal` | Spec omit + emerging | defer MEU-23 |
| 4A indexes | Local Canon (absent) | emerging G30–G35 |
| No SSE | Spec | `CONSOLE_POLL` only |
| Dual Bearer / list envelopes | Local Canon | p4/p5 carry-forward; do not rewrite API |

### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/api/pyproject.toml` | modify | add `uvicorn` |
| `packages/api/src/avkit_api/__main__.py` | new | `SPAWN_FLAGS` entry |
| `packages/api/src/avkit_api/cli.py` | new | bind, descriptor, `READY_LINE` |
| `tests/unit/test_backend_cli.py` | new | AC-19.1/19.3 |
| `tests/integration/test_backend_spawn.py` | new | AC-19.2/19.4 |
| `ui/package.json` + ts/vite/eslint/vitest/playwright configs | new | `STACK_PINS` |
| `ui/src/main/*.ts` + `preload.ts` | new | lock, identity, IPC, spawn |
| `ui/src/renderer/**` | new | AppShell, console, apiFetch, `SHELL_HOME` |
| `ui/tests/unit/**` | new | AC-19.5–19.14, 19.17–19.23 |
| `ui/tests/e2e/**` | new | AC-19.15–19.16 |
| `docs/BUILD_PLAN.md` | modify via `meu_status.py` | bind MEU-19; `HUB_NEXT_AFTER` |
| `docs/execution/plans/2026-08-19-p6-gui-shell/assert-handoff-markers.ps1` | new | sole `HANDOFF_MARKER_CHECK` owner |
| `docs/execution/plans/2026-08-19-p6-gui-shell/assert-red-oracle.ps1` | new | sole `RED_ORACLE_CHECK` owner |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Downloader page (URL/SABR/queue/cookies) | deferred | MEU-20 | grouping Session 8; matrix 6.2 |
| Transcript page | deferred | MEU-21 | grouping Session 9; matrix 6.3 |
| TTS / models page + `~/Documents` | deferred | MEU-22 | grouping Session 10; matrix 6.4 |
| Settings / HelpCards / full action-index audit / Copy MCP button | deferred | MEU-23 | grouping Session 11; matrix 6.5; `gui-actions-index.md` 58 |
| `window.electron.openExternal` (G27) | deferred | MEU-23 | 06-gui preload omit; HelpCards |
| PyInstaller onedir / NSIS / bundled FFmpeg | deferred | MEU-24, MEU-25 | grouping Session 12; 07 packaging |
| Rewrite FastAPI routers / OpenAPI routes | out-of-scope | — | grouping Session 7; p4 approved |
| Rewrite MCP tools / ACTION_INDEX | out-of-scope | — | grouping; MEU-17/18 approved |
| SSE / OCR / multi-file TTS / MCP Guard / ConversionJob GUI | out-of-scope | — | grouping “Named deferrals are not MEUs”; `06-gui.md` 1158–1167 |
| Invent new MEU IDs | out-of-scope | — | grouping §4 |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-19 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"6"`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 1–6 plan links. Do not hand-edit AUTOGEN tables — `meu_status.py render`.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p6-gui-shell'; SLASH=PLAN+'/'; NEXT='/create-plan p6-gui-downloader'; MEUS=('MEU-19',); data=load(); p6=next(p for p in data['phases'] if str(p['id'])=='6'); eps=list(p6.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 6 missing PLAN_FOLDER_SLASH'); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

Classify every command through [`.agent/docs/output-evidence-policy.md`](../../../../.agent/docs/output-evidence-policy.md).

### 1. UI type / unit / lint / build
```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx vitest run --allowOnly=false; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx eslint src/ tests/ --max-warnings 0; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/ui-verify.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-verify.txt | Select-Object -Last 40; exit $code
```

### 2. Python CLI + regression
```powershell
rtk proxy uv run pytest tests/unit/test_backend_cli.py tests/integration/test_backend_spawn.py tests/e2e tests/integration/test_api_wiring.py tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py -x --tb=short -v *> C:/Temp/av-kit/pytest-p6-regression.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p6-regression.txt | Select-Object -Last 40; exit $code
```

### 3. OpenAPI (API package touched)
```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

### 4. `HANDOFF_MARKER_CHECK` (sole marker owner)

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-19-p6-gui-shell/assert-handoff-markers.ps1 *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code
```

### 5. E2E (written+wired; run may `[B]`)
```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx playwright test launch.test.ts console-panel.test.ts command-palette-nav.spec.ts; exit $LASTEXITCODE } *> C:/Temp/av-kit/e2e-wave0.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-wave0.txt | Select-Object -Last 40; exit $code
```

### Stop conditions

- Plan review cap 3 without `approved`
- Exec review cap 6 without `approved`
- All reviewer rungs rate-limited
- Human-decision gate
- Genuine `[B]` with receipt (E2E no-display is valid `[B]` only for the **run**, not for missing tests)

---

## Open Questions

None that block. Research-resolved locks are in **User Review Required** (items 2–6) and named sets `OURS_EXE`, `SHELL_HOME`, `SHELL_PALETTE_IDS`.

| Question | Option | Source | Pros | Cons | Rec |
|----------|--------|--------|------|------|-----|
| Unpackaged identity target | `DEV_SPAWN` + `PYTHON_IMAGE` | Electron `app.isPackaged`; 07 102; r1 F3 | same proof table; owned pid is Python | must resolve image once | ✅ |
| | Always resourcesPath exe | 07 102 literal | matches shipped path | file missing in dev → false refuse/kill | ❌ |
| | Spawn `uv run` as owned child | common DX | shorter argv | wrapper pid ≠ descriptor pid | ❌ |
| Default `/` component | `SHELL_HOME` skeleton | grouping Session 7 | no page leak | 06-gui snippet shows DownloaderPage | ✅ |
| | Full DownloaderPage now | 06-gui 169 | matches snippet | mixes MEU-20 | ❌ |
| Runtime CLI session | MEU-19 | G29; 07 CLI; p5 deferral | shell can spawn | p4 text said MEU-24 | ✅ |
| | Wait for MEU-24 | p4 Out of Scope | thinner Session 7 | G29 broken spawn | ❌ |

---

## Research References

- [Electron `requestSingleInstanceLock`](https://www.electronjs.org/docs/latest/api/app#apprequestsingleinstancelockadditionaldata)
- [Electron context isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation)
- [Uvicorn `--port 0`](https://uvicorn.dev/settings/)
- [06-gui.md](../../../build-plan/06-gui.md)
- [07-distribution.md](../../../build-plan/07-distribution.md)
- [gui-actions-index.md](../../../build-plan/gui-actions-index.md)
- `.agent/docs/emerging-standards.md` G11, G16, G17, G20, G30–G36, E2
- zorivest `P:/zorivest/ui/package.json` (`STACK_PINS`)
- p4/p5 approved plans (AUTH, envelopes, spawn deferral)
