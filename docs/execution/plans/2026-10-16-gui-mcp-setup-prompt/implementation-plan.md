---
project: "2026-10-16-gui-mcp-setup-prompt"
date: "2026-10-16"
source: "docs/build-plan/07-distribution.md#mcp-setup-prompt-residual"
meus: ["MEU-71", "MEU-92"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: GUI MCP setup prompt (Session 31b)

> **Project:** `2026-10-16-gui-mcp-setup-prompt`
> **Build plan:**
> - `docs/build-plan/07-distribution.md` §MCP setup prompt (residual) (`:272-288`, MEU-71) and §MCP on a shipped machine (`:251-268`) as Local Canon
> - `docs/build-plan/06-gui.md` preload listing (`:94-101`) and the MCP / API access card row (`:1159`)
> - `docs/build-plan/05-mcp-server.md` Phase 7 row (`:329`); `docs/build-plan/gui-actions-index.md` Settings rows (`:96-97`); `docs/build-plan/build-priority-matrix.md` Phase 7 rows (`:52-54`)
>
> **Grouping:** `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, Session 31b (`:94-96`, row `:191`), decisions D-1, D-2, D-6, D-7, D-55 and D-56 (`:227-228`).
> **Known issues:** `MCP-SETUP-PROMPT` (`known-issues.yaml:1679`; triage decisions D-46 to D-54, D-57 and D-58) and `MCP-PACKAGED-ENTRY-UNREACHABLE` (`:1090`). Triage ids collide with this plan's numbering space, so they are cited in prose as "triage D-n" only.
> **User decisions (USER_EXPLICIT 2026-10-16):** "accept all" on the triage HDP recommendations (D-48 to D-58 as recorded in 07 and the two known issues). Grouping D-56 is still **open**: this plan carries its Decision Brief (§User Review Required) with MEU-92 as the recommendation, and execution does not start until Mat rules.
> **Status:** `draft`, Round 1.

## Goal

Session 31b delivers MEU-71 (a per-client MCP setup prompt that the Settings MCP card shows and copies, with no token in any block and a fixed `mcp-server` entry guard) and, under grouping D-56, MEU-92 (a self-contained `esbuild` bundle of the MCP server that the packaged app ships and `MCP_ENTRY_PROBE` proves starts from a built `win-unpacked` tree).

Mat's Session 30 `FLATTEN_LOOK` F8 (2026-10-03) found that **Copy MCP config** gives the user nothing usable:

- It copies only `{AVKIT_API_TOKEN, AVKIT_APP_DATA}` (07 `:262-264`): no command, no server path, no client placement, nothing to read.
- A Claude Code local-scope registration keyed to `P:/av-kit` never loaded in a session opened as `p:/av-kit` (`MCP-SETUP-PROMPT` root cause).
- The shipped entry cannot start. `mcp-server/src/index.ts:31-34` runs `main()` only when `process.argv[1]` ends with `/src/index.ts` or `/dist/index.js`, and the packaged copy is `resources/mcp-server/index.js`. Session 32's `MCP_ENTRY_PROBE` also found the packaged tree has no `node_modules` (`ERR_MODULE_NOT_FOUND`, `MCP-PACKAGED-ENTRY-UNREACHABLE`).

This session adds:

- **MEU-71 `gui-mcp-setup-prompt`:**
  - A pure prompt builder in main (`PROMPT_BUILDER`) for seven clients (`CLIENT_SET`), user scope by default, project scope for the four clients that have a project file (`SCOPE_RULE`).
  - Every block launches the app's own executable with `ELECTRON_RUN_AS_NODE=1` and the absolute server path in `args` (`MCP_LAUNCH`), emits `AVKIT_APP_DATA`, and never contains the token (`TOKEN_BOUNDARY`).
  - The prompt tells any agent to back up, merge, restart if needed, verify with the authenticated `avkit_health` `dependencies` action, and end with one `RESULT:` line (`PROMPT_STEPS`, `RESULT_LINE`).
  - One new IPC channel that returns only the prompt text (`PROMPT_CHANNEL`), and the Settings card: client and scope selectors, a read-only viewer, **Copy prompt**, with the existing copy/pin buttons moved under an Advanced disclosure (`CARD_LAYOUT`).
  - The realpath entry guard (`ENTRY_GUARD`), so the server starts from any path that resolves to its file, plus one server-instructions line and a rewritten `mcp.json.example`.
- **MEU-92 `dist-mcp-server-bundle`** (proposed; grouping D-56):
  - `npm --prefix mcp-server run bundle` writes `mcp-server/bundle/index.mjs` (`esbuild`, ESM, all dependencies inlined) and `LICENSES.txt` (`BUNDLE_SCRIPT`, `BUNDLE_LICENSES`).
  - `electron-builder.yml` ships `mcp-server/bundle` as `resources/mcp-server`, and `dist:prep` builds it (`PACKAGING_INPUTS`).
  - `MCP_ENTRY_PROBE` on a freshly built `win-unpacked` tree is a pass condition (p7 RULE-1), not a record.

Order: MEU-71 first (the prompt, the guard, the launch shape), then MEU-92, which changes only what the packaged path points at. If Mat declines D-56, the MEU-92 rows are dropped by a plan correction before row 0, and the packaged server path stays `resources/mcp-server/index.js` (§Decision Brief). Planning started on main at `4a97483` with the five triage files uncommitted. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ absent (2026-10-16); headroom is on PATH but has no approved Headroom disposition, and planning payloads are source code, grep output and exact anchors (bypass classes). Scope is the Settings card, three main files, the mcp-server entry and packaging config, read directly."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). The `prereq` check refuses while headroom is on PATH unless `task.md` records an execution-phase `context_tool_decision` that names it (Session 38 precedent).

## Harness, driver and reviewer route

- **Driver:** Claude Code (VS Code extension) on Mat's Windows host:
  - `native_shell: powershell`, with `rtk` on PATH. Receipts go to `C:/Temp/av-kit/`.
  - `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code; GUARDRAILS SIGN 1). The reviewer's `approved` does not start execution; Mat's chat "proceed" and the D-56 ruling do.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every row keeps `compact_continue` as the fallback.
- **Gate location:** local. The Windows host is authoritative, so there is no container pre-gate. Real Electron, the `electron-builder --win dir` build and the packaged probe run in the driver's own shell, with ELECTRON_RUN_AS_NODE removed from the parent environment (`validate-task.ps1` does this first); only the probe's child process sets it.
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1`, class `avkit_independent_reviewer` (`.agent/skills/cli-dispatch/SKILL.md`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`. The author is Anthropic and the reviewer OpenAI. Mat is the fallback if Codex is unavailable. Caps: plan 3 rounds, execution 6. Each dispatch is metered and announced before it runs. No dispatch carries secrets: the prompt forbids opening `P:/av-kit/.mcp.json`, any `mcp-token.txt` and `~/.claude.json`.
- **Receipts:** `C:/Temp/av-kit/s31b-*`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-71` | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md` |
| `MEU-92` | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-92-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | D-56 ruling, MEU-92 registration, prerequisites, dependency install, baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Execution authorization, §Baseline, §Census; `baseline.sha` |
| WP-1 | MEU-71 TDD: prompt builder, IPC, entry guard, Settings card, Electron (rows 2–4) | WP-0 | `shared` | MEU-71 tests and source; Red/Green receipts |
| WP-2 | MEU-71 targeted gate and handoff (row 5) | WP-1 | `compact_continue` | MEU-71 handoff; compact, then re-read `task.md` and the handoff |
| WP-3 | MEU-92 TDD, packaged probe and handoff (rows 6–9) | WP-2 | `compact_continue` | MEU-92 handoff; `pkg-probe-result.json`; compact, then re-read |
| WP-4 | Hub reconciliation (row 10) | WP-3 | `shared` | 05, 06, 07, matrix |
| WP-5 | H1 closeout (full D6 gate, `MCP_PROMPT_LOOK`), execution review, H2 | WP-4 | `compact_continue` | handoffs, gate receipts, walkthrough, rolling review, reflection |

---

## User Review Required

> [!IMPORTANT]
> These items record what Mat's "proceed" covers and what the next report must surface. They are not a pause point before review.
>
> 1. **Grouping D-56 Decision Brief (needs a ruling before row 0).** See §Decision Brief below. Recommendation: accept MEU-92 into Session 31b.
> 2. **`TEST_AMENDMENTS` TA-1 to TA-3** (contracts table). The new channel raises the registered-channel count pins from 20 to 21 and adds census entries (TA-1). The audit test maps the new IPC cell to its channel and registers the Copy prompt help id (TA-2). Two Settings E2E steps open the Advanced disclosure before using `copy-mcp-btn` / `pin-mcp-btn`; their assertions do not change (TA-3; 07 `:285` "existing copy/pin assertions unchanged"). Any other contradiction stops execution (S2).
> 3. **Autonomous decisions, logged for veto:**
>    - D-73: the Claude Code block is `claude mcp remove` then `claude mcp add` at the chosen scope, not `add-json`, so a stale entry never survives and the command reads on one line.
>    - D-74: the server key is `avkit` in every client (today's `mcp.json.example` uses `av-kit`).
>    - D-79: `docs/distribution/mcp.json.example` is rewritten to the generic block (executable plus `ELECTRON_RUN_AS_NODE`, no token). It is the only shipped example and still shows `node` and `AVKIT_API_TOKEN`.
>    - D-81: the backup name is `<file>.avkit-backup-<UTC yyyyMMddTHHmmssZ>`; the agent chooses the timestamp when it runs.
>    - D-86: the prompt channel never reads the token; the main process knows the launch command and server path from a new `mcpServerLaunch` dependency.

### Decision Brief — grouping D-56

- **Question:** who makes the packaged `mcp-server` dependencies present and proves `MCP_ENTRY_PROBE` starts? Triage D-50 assumed MEU-72 kept this, but Session 32 closed MEU-72 with it out of scope (`2026-10-14-tts-engine-runtime/implementation-plan.md:418`), so it has no owner (grouping `:228`).
- **Options:**
  1. **(Recommended)** A new MEU-92 `dist-mcp-server-bundle` in Session 31b after MEU-71, with `MCP_ENTRY_PROBE` on a built `win-unpacked` tree as a pass condition (p7 RULE-1).
  2. Ship `mcp-server/node_modules` (`npm ci --omit=dev` into `resources/mcp-server`) instead of a bundle. Larger tree, no licence file to build, but it puts a second `node_modules` in the installer and depends on install layout.
  3. Leave it unowned: MEU-71's prompt works in dev only, and the packaged prompt points at a server that cannot start.
- **Recommendation:** option 1. MEU-71's prompt is only correct on a shipped machine if the packaged entry starts. A bundle is one file plus a licence file and is independent of `node_modules` layout. The probe makes "it starts" a test, not a claim.
- **Reversibility:** two-way. The bundle is additive config; reverting it restores `../mcp-server/dist`.
- **Default if unanswered:** execution does not start. Row 0's first step records the ruling in the grouping D-56 row. If Mat declines, the plan is corrected to drop rows 6–9 and the MEU-92 ACs, `SERVER_ENTRY` keeps `index.js`, and the correction is re-reviewed.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here. ACs, task rows and scripts refer to these names and never restate the values (PR-9).

| Name | Definition | Source |
|---|---|---|
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the Files Modified rows below. `packages/`, `tools/`, `native/`, `openapi.committed.json` and `docs/build-plan/11-page-layout.md` stay byte-identical to `baseline.sha`. In `ui/src/main/`, only `ipc.ts`, `index.ts`, `preload.ts` and the new `mcp-setup-prompt.ts` change. Nothing else in the repository changes except this plan's closeout outputs (the plan directory, the session's handoffs and reflection, and the rendered `meu-registry.md` / `known-issues.md` / `known-issues-archive.md`). `validate-task.ps1 -Check scope` proves this against every path changed since `baseline.sha`. A Files Modified path ending in `/` covers the files under it. | Grouping `:94-96`; 07 `:272-288` |
| `CLIENT_SET` | In this order: `claude-code` (Claude Code), `codex` (Codex), `cursor` (Cursor), `vscode` (VS Code), `claude-desktop` (Claude Desktop), `windsurf` (Windsurf (community)), `generic` (Other MCP client). Exported from `mcp-setup-prompt.ts` as `MCP_CLIENTS`. | 07 `:282`; triage D-51 |
| `SCOPE_RULE` | `scope` is `user` (default) or `project`. `project` is valid only for `claude-code` (`.mcp.json`), `cursor` (`.cursor/mcp.json`), `codex` (`.codex/config.toml`) and `vscode` (`.vscode/mcp.json`). `PROMPT_BUILDER` throws `Error(PROJECT_SCOPE_ERROR)` for `project` with any other client. No block ever emits Claude Code's `local` scope or omits `--scope`. | 07 `:280`; triage D-48 |
| `PROJECT_SCOPE_ERROR` | `<label> has no project-scope config; use user scope` (with the client label). | D-74 |
| `SERVER_KEY` | The entry name `avkit` in every block and command. | D-74 |
| `MCP_LAUNCH` | `command` = the app executable (`process.execPath` in main); `args` = `[serverPath]` (one element, absolute); `env` = `{ ELECTRON_RUN_AS_NODE: "1", AVKIT_APP_DATA: appData }` in that order. No `npx`, no bare `node`, no other env key. | 07 `:281`; triage D-50 |
| `SERVER_ENTRY` | `mcpServerEntry({ packaged, resourcesPath, dirname })` in `mcp-setup-prompt.ts`. Packaged: `join(resourcesPath, 'mcp-server', 'index.mjs')` (MEU-92's bundle; `index.js` if D-56 is declined). Dev: `resolve(dirname, '../../../mcp-server/dist/index.js')`, where `dirname` is the built main's `__dirname` (`ui/out/main`). It does no file I/O. | `python-manager.ts:56` `packagedBackendPath` precedent; D-72 |
| `PROMPT_BUILDER` | `buildSetupPrompt({ client, scope, command, serverPath, appData })` in the new `ui/src/main/mcp-setup-prompt.ts`. Pure: no I/O, no clock, no token parameter. Returns the prompt text, `\n` line ends, built from `PROMPT_STEPS` around the client block (`CLAUDE_CODE_BLOCK`, `CODEX_BLOCK`, `JSON_BLOCKS`). Throws `PROJECT_SCOPE_ERROR` per `SCOPE_RULE`, and `Error(PATH_QUOTE_ERROR)` from the Claude Code block when `command`, `serverPath` or `appData` contains `"`, `$` or a backtick. | 07 `:278-286`; D-71 |
| `PATH_QUOTE_ERROR` | `a path contains a quote, $ or backtick; use the Other MCP client block`. | D-73 |
| `CLAUDE_CODE_BLOCK` | Two commands, each one line, with `S` = `user` or `project`: `claude mcp remove avkit --scope S` (the prompt says a "not found" result is fine), then `claude mcp add avkit --scope S -e ELECTRON_RUN_AS_NODE=1 -e "AVKIT_APP_DATA=<appData>" -- "<command>" "<serverPath>"`. `-e` is variadic, so `--` ends the options before the command (receipt `C:/Temp/av-kit/s31b-claude-mcp-add-help.txt`, CLI 2.1.296). Config file named for the backup: `~/.claude.json` (user) or `.mcp.json` in the repository root (project). | Claude Code `claude mcp add --help`; triage D-48; D-73 |
| `CODEX_BLOCK` | TOML for `~/.codex/config.toml` (user) or `.codex/config.toml` (project): a `[mcp_servers.avkit]` table with `command = <q>` and `args = [<q>]`, then a `[mcp_servers.avkit.env]` table with `ELECTRON_RUN_AS_NODE = "1"` and `AVKIT_APP_DATA = <q>`, where `<q>` is `JSON.stringify` of the value (a valid TOML basic string: `\\`, `\"` and `\uXXXX` escapes). The merge step says to replace both tables and keep every other table. | Codex config reference; triage D-51 |
| `JSON_BLOCKS` | `JSON.stringify(obj, null, 2)` of one object per client, holding only `SERVER_KEY` under the client's container. Cursor: `{"mcpServers":{"avkit":{command,args,env}}}` in `~/.cursor/mcp.json` or `.cursor/mcp.json`. VS Code: `{"servers":{"avkit":{"type":"stdio",command,args,env}}}` in the user `mcp.json` (`%APPDATA%\Code\User\mcp.json`, or the "MCP: Open User Configuration" command) or `.vscode/mcp.json`. Claude Desktop: `mcpServers` in `%APPDATA%\Claude\claude_desktop_config.json`, plus the note that the MSIX install keeps it at `%LOCALAPPDATA%\Packages\Claude_*\LocalCache\Roaming\Claude\claude_desktop_config.json`. Windsurf: `mcpServers` in `~/.codeium/windsurf/mcp_config.json`. Generic: `mcpServers`, with one sentence naming the three fields for clients that use another shape. | 07 `:282`; client docs (§Research References); triage D-51 |
| `TOKEN_BOUNDARY` | No prompt contains the token, the string `AVKIT_API_TOKEN`, or `${`. Every block contains `AVKIT_APP_DATA` with the app's resolved `appData` and `ELECTRON_RUN_AS_NODE`. The server reads `{app_data}/mcp-token.txt` itself (`mcp-server/src/config.ts:32-37`). | 07 `:283`; triage D-49, D-57 |
| `PROMPT_STEPS` | The prompt, in order: (1) a title line naming the client and scope; (2) **Find** the config file (or, for Claude Code, the commands); (3) **Back up** that file to `BACKUP_NAME` before changing it, or skip the backup if it does not exist yet; (4) **Merge** only the `SERVER_KEY` entry and keep every other entry; the block follows; (5) `If the tools do not appear, quit and reopen <client label>, then reply Ready.`; (6) **Verify** by calling `avkit_health` with `action: "dependencies"`; it must return successfully, and a `liveness` result never counts; (7) `RESULT_LINE`. | 07 `:284`; triage D-52, D-53, D-58 |
| `BACKUP_NAME` | `<file>.avkit-backup-<UTC yyyyMMddTHHmmssZ>`, the timestamp taken by the agent when it runs. | D-81 |
| `RESULT_LINE` | The prompt's last instruction: end the reply with exactly one line, `RESULT: connected` or `RESULT: failed (<step>, <error>)`, `<step>` ∈ {`backup`, `merge`, `restart`, `verify`}. When the verify call returns an error whose text starts with `<code>:` (the server's `toToolError` form, `client.ts:71`), `<error>` is that code (for example `token_missing`, `app_not_running`). | 07 `:284`; D-80 |
| `PROMPT_CHANNEL` | The renderer-to-main channel `get-mcp-setup-prompt`, appended after `write-clipboard-image` in `RENDERER_TO_MAIN_CHANNELS`, so the list has 21 entries. | 07 `:286`; D-86 |
| `PROMPT_PAYLOAD` | `z.object({ client: z.enum(MCP_CLIENTS), scope: z.enum(['user', 'project']) }).strict()`. An unknown client, a missing scope or an extra key returns `{ ok: false }` before any dependency is used. | `ipc.ts:79` strict precedent |
| `PROMPT_HANDLER` | The `handleIpc` case: without `deps.mcpServerLaunch` it returns `{ ok: false, error: LAUNCH_MISSING_ERROR }`. Otherwise it returns `{ ok: true, value: { text } }` with `text = buildSetupPrompt({ client, scope, ...deps.mcpServerLaunch, appData })` (`appData` from `ipc.ts:314`), or `{ ok: false, error: message }` when the builder throws. It never calls `deps.readMcpToken` and touches no `effects` counter. | D-86 |
| `LAUNCH_MISSING_ERROR` | `the MCP server launch is not configured`. | D-86 |
| `LAUNCH_DEP` | `IpcDeps.mcpServerLaunch?: { command: string; serverPath: string }`. `index.ts` wires `{ command: process.execPath, serverPath: mcpServerEntry({ packaged: app.isPackaged, resourcesPath: process.resourcesPath, dirname: __dirname }) }`. | `index.ts:394` deps precedent; D-72, D-86 |
| `PRELOAD_KEY` | `getMcpSetupPrompt: (opts: { client: string; scope: 'user' \| 'project' }) => ipcRenderer.invoke('get-mcp-setup-prompt', opts)`, appended to `API_KEYS`. `env.d.ts` declares it optional (`getMcpSetupPrompt?`) returning `Promise<{ text: string }>`, so existing `window.api` mocks need no edit. | `env.d.ts:31` `writeClipboardImage?` precedent |
| `CARD_LAYOUT` | The Settings MCP card (`SettingsPage.tsx:1160-1174`), top to bottom: the unchanged `mcp-token-present` chip; `GridSelect` `mcp-client-select` (label `Client`, `CLIENT_SET` order and labels) and `mcp-scope-select` (label `Scope`; `User (all projects)` / `This project only`); a read-only `<textarea data-testid="mcp-setup-prompt" readOnly aria-label="MCP setup prompt">` holding the prompt for the current pair; `Button` `mcp-copy-prompt-btn` (`Copy prompt`); a polite status `<p data-testid="mcp-prompt-status" role="status">`; then `ADVANCED_DISCLOSURE`. The prompt is fetched on mount and on each client or scope change. | 07 `:286`; triage D-54; D-75 |
| `ADVANCED_DISCLOSURE` | `<details data-testid="mcp-advanced">` (closed by default) with `<summary data-testid="mcp-advanced-summary">Advanced</summary>` around the unchanged `copy-mcp-btn` and `pin-mcp-btn` (same labels, handlers and testids). | 07 `:286`; triage D-54 |
| `SCOPE_DISABLED` | `GridSelect` gains an optional `disabled` prop passed to its `<select>`. When the client is `claude-desktop`, `windsurf` or `generic`, the scope is forced to `user` and `mcp-scope-select` is disabled. | `SCOPE_RULE`; D-75 |
| `COPY_PROMPT` | **Copy prompt** calls `window.api.writeClipboardText(text)` with the viewer's exact text, then sets `mcp-prompt-status` to `Copied the <client label> setup prompt.` Fetch and copy failures go through `runSettingsAction('general', …)`. When `window.api.getMcpSetupPrompt` is undefined the viewer shows `PROMPT_UNAVAILABLE` and Copy is disabled. | `SettingsPage.tsx:422-426` `copyMcp` precedent; D-87 |
| `PROMPT_UNAVAILABLE` | `The setup prompt is not available in this window.` | D-87 |
| `ENTRY_GUARD` | `isMainModule(argv1, importMetaUrl)` in the new `mcp-server/src/entry-guard.ts`: `false` when `argv1` is undefined or either side fails to resolve; otherwise it compares `realpathSync.native(argv1)` with `realpathSync.native(fileURLToPath(importMetaUrl))`, case-insensitively on `win32`. `index.ts:31-34` becomes `if (isMainModule(process.argv[1], import.meta.url)) { void main() }`. Node resolves the main module's realpath by default, so a junction or symlink to the file matches, and an import from a test does not. | `MCP-PACKAGED-ENTRY-UNREACHABLE`; Node `--preserve-symlinks-main`; D-76 |
| `SETUP_INSTRUCTION` | The line `Setup: the desktop app's Settings → MCP card shows a per-client setup prompt.` appended as the last element of `SERVER_INSTRUCTIONS`. | 07 `:287`; D-78 |
| `EXAMPLE_CONFIG` | `docs/distribution/mcp.json.example` becomes the generic `JSON_BLOCKS` shape with placeholder values `<path to av-kit.exe>`, `<av-kit resources>\\mcp-server\\index.mjs` and `<app data folder>`, `SERVER_KEY` `avkit`, `ELECTRON_RUN_AS_NODE` `"1"`, and no `AVKIT_API_TOKEN`. | D-79 |
| `FUSE_PIN` | `ui/electron-builder.yml` contains no `runAsNode: false` and no `electronFuses` block that disables it. | 07 `:281` ("A test pins Electron's RunAsNode fuse on"); D-82 |
| `NEW_TESTIDS` | MEU-71: `mcp-client-select`, `mcp-scope-select`, `mcp-setup-prompt`, `mcp-copy-prompt-btn`, `mcp-prompt-status`, `mcp-advanced`, `mcp-advanced-summary`, appended to `ui/tests/e2e/test-ids.ts` as one block. MEU-92 adds none. | E2; `test-ids.ts:45-51` |
| `INDEX_ROW` | `` | `settings:copy_mcp_prompt` | Copy prompt | no | IPC `getMcpSetupPrompt` + `writeClipboardText` (no token) | specified | 07 / 06 | `` inserted after `settings:pin_mcp` (`gui-actions-index.md:97`) in row 2 (D-77). | 07 `:287`; AC-23.20 |
| `MCP_ENTRY_PROBE` | `plan_checks.py mcp-probe`: spawn the given command with the parent environment plus `ELECTRON_RUN_AS_NODE=1`, write one `initialize` request (`protocolVersion` `2025-06-18`), read stdout for up to 10 s, then kill. It records `result`, `exit_code`, `stderr_tail` (last 800 chars), `first_stdout` (first 300) and `seconds` in the named JSON. PASS only when a JSON-RPC line arrived and the first stdout line contains `"name":"av-kit"`. | Session 32 `gate_lib.py:540-573`, now a pass condition (p7 RULE-1); D-84 |
| `BUNDLE_SCRIPT` | `"bundle": "tsx scripts/bundle.ts"` in `mcp-server/package.json`. `scripts/bundle.ts` calls `esbuild.build({ entryPoints: ['src/index.ts'], bundle: true, platform: 'node', format: 'esm', target: 'node22', metafile: true, outfile: 'bundle/index.mjs', banner: { js: "import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);" } })`, then writes `bundle/LICENSES.txt` from `BUNDLE_LICENSES`. `esbuild` is a devDependency pinned to exactly `0.28.2`. `tsconfig.scripts.json` already includes `scripts/**/*.ts`, so `mcp-types` checks it. | esbuild API; D-83 |
| `BUNDLE_LICENSES` | `collectLicenses(metafile, root)` in the new `mcp-server/scripts/bundle-licenses.ts`: for every metafile input under `node_modules/<name>` (scoped names included) it reads that package's `package.json` `name`, `version`, `license` and its `LICENSE*` / `LICENCE*` / `COPYING*` file, and returns one section per package, sorted by name. A package with no licence file throws `Error('no licence file for <name>')`. | D-85 |
| `PACKAGING_INPUTS` | `ui/electron-builder.yml:35-36` `- from: ../mcp-server/dist` → `- from: ../mcp-server/bundle` (`to: mcp-server` unchanged); `ui/package.json:20` `dist:prep` gains ` && npm --prefix ../mcp-server run bundle` at its end; `.gitignore` gains `mcp-server/bundle/` after `mcp-server/dist/` (`:17`). | 07 `:253`; D-83 |
| `PKG_PROBE` | `-Check pkg-probe`: assert `PACKAGING_INPUTS`; `npm --prefix ui run dist:prep`; `npx electron-builder --win dir --x64` in `ui/`; assert `ui/dist/win-unpacked/resources/mcp-server/index.mjs` is byte-equal to `mcp-server/bundle/index.mjs` and `LICENSES.txt` is present; run `MCP_ENTRY_PROBE` with `ui/dist/win-unpacked/av-kit.exe` on the in-place entry, then on a copy of `resources/mcp-server/` at `C:/Temp/av-kit/s31b-pkg-probe/mcp-server/` (no `node_modules` above it). Both must pass. Results go to `pkg-probe-result.json`. | p7 RULE-1; D-84 |
| `PKG_EVIDENCE` | `pkg-probe-result.json` (schema `s31b-pkg-probe.v2`) records the SHA-256 of every file in `plan_checks.py` `PKG_FILES`: `av-kit.exe`, the packaged `index.mjs` and `LICENSES.txt`, the source `mcp-server/bundle/index.mjs` and `LICENSES.txt`, `ui/electron-builder.yml`, and both `package.json` / `package-lock.json` pairs. `plan_checks.py pkg-current` (and `floors`) re-hash them and refuse the proof when any is missing or changed, when `passed` is not true, or when the file has no `identity`. So a later bundle, packaging or lockfile edit, or a removed packaged entry, needs a fresh row 8. Selftest negatives cover each case. | p7 RULE-1; D-84 |
| `TEST_AMENDMENTS` | **TA-1:** the 20 → 21 registered-channel pins at `ui/tests/unit/clipboard-image-main.test.ts:101`, `ipc-strict-census.test.ts:54` and `login-item-ipc.test.ts:50-51`; `PROMPT_CHANNEL` entries in the census valid-payload (`~:25`) and type-failure (`~:48`) tables; `ui/tests/unit/ipc-channels.ts` gains `PROMPT_CHANNEL` after `'write-clipboard-image'` (`:21`), not in `IPC_NO_PAYLOAD`. **TA-2:** `ui/tests/unit/gui-actions-audit.test.ts`: `resolveIpcChannel` (`:66-77`) gains a first line mapping a cell that names `getMcpSetupPrompt` to `get-mcp-setup-prompt` (AC-23.20 at `:182-215` resolves every non-REST Settings row), and `SETTINGS_HELP_TESTIDS` (`:29-46`) gains `{ testid: 'mcp-copy-prompt-btn', indexId: 'settings:copy_mcp_prompt' }`. **TA-3:** `ui/tests/e2e/settings.test.ts` W4-2 (`:149-150`) and W4-3 (`:179-180`) each gain one step that clicks `mcp-advanced-summary` before their existing `copy-mcp-btn` / `pin-mcp-btn` assertions and clicks; no assertion changes. No other existing expectation changes. | MEU-61 / Session 38 TA precedent; S2 |
| `COUNT_FLOORS` | Computed by `plan_checks.py floors` against `baseline-counts.json` (row 0), over the ui Vitest JSON, the mcp-server Vitest JSON and the Playwright JSON. Each Vitest run: `numFailedTests` 0, and `numPassedTests` ≥ its baseline + the passing tests whose name carries an `AC-71.n` / `AC-92.n` id. Playwright: `unexpected` and `flaky` 0, `skipped` ≤ baseline, `expected` ≥ baseline + passing AC specs. Every Vitest AC appears in a passing test name (`AC-71.1` never matches `AC-71.12`); AC-71.15 appears in a passing spec title; AC-92.4 is satisfied by a current `pkg-probe-result.json` (`PKG_EVIDENCE`). | G36; Session 38 precedent |
| `MCP_PROMPT_LOOK` | Mat's manual check on the dev app (launched detached with `Start-Process`, ELECTRON_RUN_AS_NODE removed). L1: the MCP card shows Client, Scope, the prompt and Copy prompt; Advanced is closed and opens to the two old buttons. L2: Scope greys out for Claude Desktop, Windsurf and Other. L3: Copy prompt (Claude Code, user scope), paste into a new Claude Code session opened as `p:/av-kit` (lowercase), let it apply: the reply ends `RESULT: connected` and `/mcp` lists `avkit`. L4: the prompt text is readable in dark and light themes and shows no token. L5 (optional): the Codex block applied by Codex lists the av-kit tools. Claude never opens the config files Mat's agent edits. | Session 30/38 look precedent; `MCP-SETUP-PROMPT` F8 |

### MEU-71 — `gui-mcp-setup-prompt`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| IPC `get-mcp-setup-prompt` (renderer → main) | zod in `ui/src/main/ipc.ts` `schemas` | `PROMPT_PAYLOAD` | `.strict()`: an extra key returns `{ ok: false }` |
| IPC `write-clipboard-text` (existing, reused) | zod `ipc.ts:79` | `{ text: string }` | `.strict()` (unchanged) |
| IPC `copy-mcp-config` (existing, unchanged) | zod `ipc.ts:85` | `{ pinEndpoint?: boolean }` | `.strict()` (unchanged) |
| MCP server process entry (`argv[1]`) | `mcp-server/src/entry-guard.ts` | `ENTRY_GUARD` | n/a |
| MCP server env (read by the server) | `mcp-server/src/config.ts` (unchanged) | `AVKIT_APP_DATA` override, `backend.json`, `mcp-token.txt` | n/a |
| Client config files (written by the user's agent, not the app) | each client | `CLAUDE_CODE_BLOCK`, `CODEX_BLOCK`, `JSON_BLOCKS` | merge only `SERVER_KEY` |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-71.1 | unit | For each client in `CLIENT_SET` at user scope, and for the four project-scope clients at project scope, `buildSetupPrompt` with fixed inputs (paths containing spaces and backslashes) equals the golden file `ui/tests/unit/fixtures/mcp-setup-prompt/<client>-<scope>.txt` (line ends normalised). The JSON and TOML blocks parse (JSON.parse; a minimal TOML table check), and their command, args and env equal `MCP_LAUNCH`. | 07 `:282`, `:288` ("golden output per client block") | Swapping `command` and `serverPath` in the input changes the output (no golden passes by accident); `CODEX_BLOCK` with a path containing `"` keeps the TOML string valid (`\"`). |
| AC-71.2 | unit | `SCOPE_RULE`: project scope names the project file for each of the four clients, and the Claude Code commands carry `--scope project`; user scope carries `--scope user`. | 07 `:280`; triage D-48 | `project` with `claude-desktop`, `windsurf` or `generic` throws `PROJECT_SCOPE_ERROR`. No output contains `--scope local` or a `claude mcp add` without `--scope`. |
| AC-71.3 | unit | `TOKEN_BOUNDARY`: every output contains `AVKIT_APP_DATA` with the given `appData` and `ELECTRON_RUN_AS_NODE`. | 07 `:283`, `:288`; triage D-49, D-57 | With a fixture token string present in the test, no output contains it, `AVKIT_API_TOKEN` or `${`. A Claude Code input whose path contains `$` throws `PATH_QUOTE_ERROR`. |
| AC-71.4 | unit | `PROMPT_STEPS` appear in order in every output (find, back up with `BACKUP_NAME`, merge only `avkit`, the conditional restart line with the client label, verify with `avkit_health` `"dependencies"`), and the output ends with `RESULT_LINE`, naming the four steps. | 07 `:284`; triage D-52, D-53, D-58 | The verify text says `liveness` never counts and maps an error starting `token_missing:` to `RESULT: failed (verify, token_missing)` (07 `:288` negative case). |
| AC-71.5 | unit | `mcpServerEntry` returns `join(resourcesPath, 'mcp-server', 'index.mjs')` when packaged and `resolve(dirname, '../../../mcp-server/dist/index.js')` in dev (`SERVER_ENTRY`). | D-72 | A dev `dirname` of `<repo>/ui/out/main` resolves to `<repo>/mcp-server/dist/index.js`; packaged never yields a `dist` path. |
| AC-71.6 | unit | `handleIpc('get-mcp-setup-prompt', { client: 'codex', scope: 'user' }, deps)` with `mcpServerLaunch` and `appData` returns `{ ok: true, value: { text } }`, where `text` contains `[mcp_servers.avkit]`, the given command, server path and app data (`PROMPT_HANDLER`). A `readMcpToken` spy is called 0 times, and the text does not contain the spy's token. | 07 `:288` ("the token never reaches the renderer"); D-86 | `{ client: 'zed', scope: 'user' }`, `{ client: 'codex' }`, `{ client: 'codex', scope: 'user', token: 'x' }` each return `{ ok: false }`; no `mcpServerLaunch` returns `LAUNCH_MISSING_ERROR`; `{ client: 'generic', scope: 'project' }` returns `{ ok: false }` with `PROJECT_SCOPE_ERROR`. |
| AC-71.7 | unit | `PROMPT_CHANNEL` is registered: `listRegisteredChannels()` equals the test-side list, 21 entries (TA-1). `getPreloadApiKeys()` contains `getMcpSetupPrompt`, and the preload source maps it to `invoke('get-mcp-setup-prompt', opts)`. | `PRELOAD_KEY`; G27 | The census type-failure table rejects `PROMPT_CHANNEL` payloads of the wrong type (TA-1). |
| AC-71.8 | unit | `isMainModule` (`ENTRY_GUARD`) is true for the file's own path, for a path through a directory junction to it, for a drive-letter case change on win32, and for a packaged-layout temp file `<tmp>/resources/mcp-server/index.mjs`. | `MCP-PACKAGED-ENTRY-UNREACHABLE`; D-76 | False for another file, an undefined `argv1` and a path that does not exist. |
| AC-71.9 | integration (process) | With `mcp-server/dist` built, a junction `<tmp>/resources/mcp-server` → `mcp-server/dist` (`fs.symlinkSync(target, path, 'junction')`) and `node <tmp>/resources/mcp-server/index.js` with `AVKIT_APP_DATA` = a temp dir whose `backend.json` points at an in-test `node:http` backend and no token: `initialize` returns `serverInfo.name` `av-kit`, `avkit_health` `liveness` succeeds against the fake backend, and `dependencies` returns an error whose text starts `token_missing:`. | `MCP-PACKAGED-ENTRY-UNREACHABLE`; 07 `:288`; D-88 | Under today's guard the process never answers `initialize` (assertion Red, not a load error). The fake backend records no `/health/dependencies` request. |
| AC-71.10 | integration (process) | The Electron binary from `ui/node_modules/electron` started with `ELECTRON_RUN_AS_NODE=1` and `[mcpServerEntry({ packaged: false, …, dirname: <ui>/out/main })]` answers `initialize` (`protocolVersion` `2025-06-18`) with `serverInfo.name` `av-kit` (`MCP_LAUNCH` in dev). `FUSE_PIN` holds. | 07 `:281`; D-82 | The `FUSE_PIN` check, a function in the test applied to the real file and to fixture texts, refuses a fixture holding `runAsNode: false` and one holding an `electronFuses` block that sets it false. The child's first stdout line is the JSON-RPC response (no Electron app output first). |
| AC-71.11 | unit | `EXAMPLE_CONFIG`: `docs/distribution/mcp.json.example` parses as JSON with `mcpServers.avkit`, `env.ELECTRON_RUN_AS_NODE` `"1"` and an `AVKIT_APP_DATA` key. | D-79 | It contains no `AVKIT_API_TOKEN`, `${` or `"command": "node"`. |
| AC-71.12 | unit | `SERVER_INSTRUCTIONS` ends with `SETUP_INSTRUCTION`; the existing `runtime.test.ts:20-27` assertions still pass. | 07 `:287`; D-78 | The earlier lines are unchanged and in order (append-only). |
| AC-71.13 | integration | jsdom `SettingsPage`: `CARD_LAYOUT` order; the client select lists `CLIENT_SET` labels in order; choosing Codex calls `getMcpSetupPrompt({ client: 'codex', scope: 'user' })` and shows its text; choosing Claude Desktop forces `user` and disables scope (`SCOPE_DISABLED`); Copy prompt calls `writeClipboardText` once with the viewer's text and shows the status (`COPY_PROMPT`); `copy-mcp-btn` and `pin-mcp-btn` sit inside `mcp-advanced`, and `mcp-token-present` outside it. Queries use `queryBy*` with explicit `expect(...).not.toBeNull()`, so Red is by assertion. | 07 `:286`; triage D-54 | `getMcpSetupPrompt` undefined → `PROMPT_UNAVAILABLE` and Copy disabled; a rejecting `getMcpSetupPrompt` shows the settings error and no copy happens. |
| AC-71.14 | unit | `gui-actions-index.md` holds `INDEX_ROW`; its IPC cell resolves (TA-2) to a registered channel that the preload source names; `mcp-copy-prompt-btn` is in `test-ids.ts` and production source; every MEU-71 `NEW_TESTIDS` id is in `test-ids.ts` and production source. | 07 `:287`; AC-23.20 precedent | Before `PROMPT_CHANNEL` exists the resolution fails (the Red). |
| AC-71.15 | integration (Electron) | In the built app, Settings → MCP: (a) choose Codex: the viewer holds `[mcp_servers.avkit]`, `command` equals the app's `process.execPath` (read through `electronApp.evaluate`) and `AVKIT_APP_DATA` equals the app's app-data path; (b) Copy prompt → main `clipboard.readText()` equals the viewer text and `mcp-prompt-status` shows the copied line; (c) choose Claude Desktop: `mcp-scope-select` is disabled; (d) Advanced is closed, `copy-mcp-btn` is hidden until `mcp-advanced-summary` is clicked; then Copy MCP config puts JSON with a non-empty `AVKIT_API_TOKEN` T on the clipboard. | 07 `:286`, `:288` ("Electron case for select, view and copy"); E2 | (e) No viewer text for any client in `CLIENT_SET` contains T. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Viewable, copyable prompt | Spec | 07 `:279` |
| Scope default and project destinations | Spec | 07 `:280`; `SCOPE_RULE` |
| Launch command shape | Spec | 07 `:281`; `MCP_LAUNCH` |
| Per-client block shapes and paths | Research-backed | Client docs; `CLAUDE_CODE_BLOCK`, `CODEX_BLOCK`, `JSON_BLOCKS` (D-73, D-74) |
| Token boundary | Spec | 07 `:283`; `TOKEN_BOUNDARY` |
| Prompt steps and result line | Spec | 07 `:284`; `PROMPT_STEPS`, `RESULT_LINE` (D-80, D-81) |
| Where the server path comes from | Local Canon | `packagedBackendPath` precedent; `SERVER_ENTRY` (D-72) |
| How the renderer gets the prompt without the token | Local Canon | New strict channel; `PROMPT_HANDLER` (D-86) |
| Card layout and Advanced disclosure | Spec | 07 `:286`; `CARD_LAYOUT`, `ADVANCED_DISCLOSURE` |
| Entry guard | Research-backed | Node main-module realpath; `ENTRY_GUARD` (D-76) |
| RunAsNode fuse | Spec | 07 `:281`; `FUSE_PIN` (D-82) |
| MCP README | Local Canon | No MCP README exists; 05 and `mcp.json.example` carry the placement (D-78) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/main/mcp-setup-prompt.ts` | new | `CLIENT_SET`, `PROMPT_BUILDER`, the client blocks, `SERVER_ENTRY` |
| `ui/src/main/ipc.ts` | modify | `PROMPT_CHANNEL`, `PROMPT_PAYLOAD`, `LAUNCH_DEP`, `PROMPT_HANDLER` |
| `ui/src/main/index.ts` | modify | Wire `LAUNCH_DEP` |
| `ui/src/main/preload.ts` | modify | `PRELOAD_KEY` |
| `ui/src/renderer/src/env.d.ts` | modify | Optional `getMcpSetupPrompt?` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | `CARD_LAYOUT`, `ADVANCED_DISCLOSURE`, `SCOPE_DISABLED` (`GridSelect` `disabled`), `COPY_PROMPT` |
| `mcp-server/src/entry-guard.ts` | new | `ENTRY_GUARD` |
| `mcp-server/src/index.ts` | modify | Use `isMainModule`; `SETUP_INSTRUCTION` |
| `docs/distribution/mcp.json.example` | modify | `EXAMPLE_CONFIG` |
| `ui/tests/unit/mcp-setup-prompt.test.ts` | new | AC-71.1–71.4 |
| `ui/tests/unit/fixtures/mcp-setup-prompt/` | new | Eleven golden files (seven user, four project) for AC-71.1 |
| `ui/tests/unit/mcp-server-entry.test.ts` | new | AC-71.5 |
| `ui/tests/unit/mcp-prompt-ipc.test.ts` | new | AC-71.6, AC-71.7 (imports only existing modules; Red by assertion) |
| `ui/tests/unit/mcp-spawn-electron.test.ts` | new | AC-71.10 (imports `mcpServerEntry`, so it is a declared new-module file) |
| `ui/tests/unit/settings-mcp-prompt.test.ts` | new | AC-71.13 (`/** @vitest-environment jsdom */`; mocks `window.api`, not the card) |
| `ui/tests/unit/clipboard-image-main.test.ts` | modify | TA-1 |
| `ui/tests/unit/ipc-strict-census.test.ts` | modify | TA-1 |
| `ui/tests/unit/login-item-ipc.test.ts` | modify | TA-1 |
| `ui/tests/unit/ipc-channels.ts` | modify | TA-1 |
| `ui/tests/unit/gui-actions-audit.test.ts` | modify | TA-2; AC-71.14 (append only) |
| `ui/tests/e2e/mcp-setup-prompt.test.ts` | new | AC-71.15 (Electron) |
| `ui/tests/e2e/settings.test.ts` | modify | TA-3 |
| `ui/tests/e2e/test-ids.ts` | modify (append only) | MEU-71 `NEW_TESTIDS` block |
| `mcp-server/tests/entry-guard.test.ts` | new | AC-71.8 (imports `entry-guard.ts`, a declared new-module file) |
| `mcp-server/tests/entry-spawn.test.ts` | new | AC-71.9 (node builtins only; Red by assertion) |
| `mcp-server/tests/example-config.test.ts` | new | AC-71.11 |
| `mcp-server/tests/runtime.test.ts` | modify (append only) | AC-71.12 |
| `docs/build-plan/gui-actions-index.md` | modify (row 2) | `INDEX_ROW` (D-77) |

### MEU-92 — `dist-mcp-server-bundle` (proposed; grouping D-56)

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Build script `npm --prefix mcp-server run bundle` | `mcp-server/scripts/bundle.ts` | `BUNDLE_SCRIPT` | n/a |
| Packaged tree `resources/mcp-server/` | `ui/electron-builder.yml` `extraResources` | `PACKAGING_INPUTS` | Only `index.mjs` and `LICENSES.txt` |
| Packaged process (`av-kit.exe` + ELECTRON_RUN_AS_NODE) | Electron | `MCP_LAUNCH`, `FUSE_PIN` | n/a |

No new IPC, REST or MCP tool surface.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-92.1 | integration (process) | `mcp-server/bundle/index.mjs` exists after `bundle`; a copy of `bundle/` in a temp directory with no `node_modules` above it, run as `node <copy>/index.mjs`, answers `initialize` with `serverInfo.name` `av-kit`. | `MCP-PACKAGED-ENTRY-UNREACHABLE`; D-83 | Red: before the bundle exists, the existence assertion fails (not a load error). The copied bundle never resolves a module from the repository (it runs from the temp copy). |
| AC-92.2 | unit | `collectLicenses` returns one section per `node_modules` package in a fixture metafile, sorted, with name, version, licence id and licence text; scoped packages resolve. `bundle/LICENSES.txt` names every package in the real build's metafile. | D-85 | A fixture package with no licence file throws `no licence file for <name>`. |
| AC-92.3 | unit | `PACKAGING_INPUTS` and `BUNDLE_SCRIPT` hold: `electron-builder.yml` copies `../mcp-server/bundle` to `mcp-server` and no longer names `../mcp-server/dist`; `dist:prep` ends with `&& npm --prefix ../mcp-server run bundle`; `.gitignore` has `mcp-server/bundle/`; `mcp-server/package.json` has the `bundle` script and `esbuild` exactly `0.28.2`. | 07 `:253`; D-83 | Each pin fails on today's files (assertion Red). |
| AC-92.4 | runtime (packaged) | `PKG_PROBE` passes: a fresh `win-unpacked` build holds the byte-equal bundle and `LICENSES.txt`, and `av-kit.exe` with ELECTRON_RUN_AS_NODE starts the in-place entry and the hermetic copy, each answering `initialize` as `av-kit` (`MCP_ENTRY_PROBE`). | p7 RULE-1; grouping D-56; D-84 | Red evidence is Session 32's recorded `ERR_MODULE_NOT_FOUND` on `MCP-PACKAGED-ENTRY-UNREACHABLE` (`known-issues.yaml:1105`); this AC is excluded from the Vitest Red and proved by `pkg-probe`. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Packaged dependencies present | Human decision pending | Grouping D-56 (§Decision Brief) |
| Bundle format and runtime | Research-backed | esbuild ESM with a `createRequire` banner for CJS dependencies (D-83) |
| Licence notices for inlined code | Research-backed | Metafile-driven `LICENSES.txt` (D-85) |
| Proof the shipped entry starts | Local Canon | p7 RULE-1; `PKG_PROBE` (D-84) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `mcp-server/scripts/bundle.ts` | new | `BUNDLE_SCRIPT` |
| `mcp-server/scripts/bundle-licenses.ts` | new | `BUNDLE_LICENSES` |
| `mcp-server/package.json`, `mcp-server/package-lock.json` | modify | `bundle` script; `esbuild` `0.28.2` (exact) |
| `ui/electron-builder.yml` | modify | `PACKAGING_INPUTS` (`from: ../mcp-server/bundle`) |
| `ui/package.json` | modify | `dist:prep` runs `bundle` |
| `.gitignore` | modify | `mcp-server/bundle/` |
| `mcp-server/tests/bundle.test.ts` | new | AC-92.1, AC-92.3 (node builtins only; Red by assertion) |
| `mcp-server/tests/bundle-licenses.test.ts` | new | AC-92.2 (imports `bundle-licenses.ts`, a declared new-module file) |

### Shared (both MEUs)

| File | Action | Summary |
|------|--------|---------|
| `docs/build-plan/07-distribution.md` | modify (plan time; rows 0 and 10) | Plan time: the Docs row names this plan's placement (D-77, D-78). Row 0: `:283` "owned per grouping D-56" names MEU-92, and the new `mcp-server-bundle-residual` anchor section. Row 10: `:253` ships `resources/mcp-server/` |
| `docs/build-plan/06-gui.md` | modify (row 10) | Preload listing gains the `getMcpSetupPrompt` line; the MCP card row (`:1159`) names the prompt and the Advanced disclosure |
| `docs/build-plan/05-mcp-server.md` | modify (row 10) | `:329` Phase 7 row: ship the bundle; setup prompt in Settings; no `AVKIT_API_TOKEN` in client config |
| `docs/build-plan/build-priority-matrix.md` | modify (row 10) | Rows 7.3 (MEU-71) after 7.2 and 7.5 (MEU-92) after 7.4 |
| `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md` (rendered) | modify | `execution_plan` (plan time); MEU-92 registration (row 0); status at H1/H2 |
| `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md` | modify (plan time; rows 0, H1, H2) | Session 31b plan folder; the D-56 ruling; row status |
| `.agent/context/current-focus.md`, `.agent/context/known-issues.yaml`, `docs/execution/metrics.md` | modify (H1/H2) | Focus, issue resolution, metrics row |

### Amendment A-1 (row 0a; D-89 to D-93)

| File | Action | Summary |
|------|--------|---------|
| `_inspiration/zorivest/` | new (row 0a) | `globals.css` and `gui-actions-index.md` at Zorivest `61243baf`, `05n-agent-connect.md` at `ca693695`, and `PROVENANCE.md` (D-89, D-90, D-91) |
| `ui/tests/unit/queue-canon.test.ts` | modify (row 0a) | AC-41.3 `PILL_TOKEN_SOURCE` reads `_inspiration/zorivest/globals.css`; its assertions and `PORTED_TOKENS` are unchanged |
| `docs/build-plan/10-queue-card-ui.md` | modify (row 0a) | `:64` and §Status token table: av-kit owns its pill palette, seeded from the copy |
| `docs/build-plan/gui-actions-index.md` | modify (row 0a) | `:3`: the Zorivest twin pointer becomes provenance (the copy) |
| `docs/BUILD_PLAN.md` | modify (row 0a) | Golden rule 4: patterns originally from Zorivest; do not consult the Zorivest checkout |
| `.agent/docs/cloud-local-collaboration.md` | modify (row 0a) | AC-41.3 leaves `ENV_BOUND_TESTS` |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` (rendered) | modify (row 0a) | `QUEUE-PILL-TOKEN-DRIFT` resolved; its re-port path overturned |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| The app writing client config files itself | out-of-scope | — | 07 `:279` (a prompt the user's agent applies); triage D-46 |
| macOS and Linux config paths | out-of-scope | — | 07 §Platforms: Windows is the Phase 7 gate; the generic block covers other hosts |
| `AVKIT_API_BASE` pin in the prompt | out-of-scope | — | 07 `:264` (the client reads `backend.json`); the pin stays on `pin-mcp-btn` under Advanced |
| MCP Guard / lock | out-of-scope | — | 07 `:268` (deferred, 06) |
| NSIS installer probe | out-of-scope | — | `PKG_PROBE` uses the `dir` target, which builds the same `resources/` tree; the installer smoke stays with MEU-25's known issues |
| Shipping `mcp-server/node_modules` | out-of-scope | — | D-56 option 2, not recommended; D-83 |
| Token rotation or display | out-of-scope | — | 06 `:1159` ("Never display the token") |

---

## BUILD_PLAN.md Audit

This project changes these build-plan homes:

1. **Plan time:** `meu-status.yaml` `execution_plan` for MEU-71, then render. The 07 Docs row (`:287`) names this plan's placement: `INDEX_ROW` lands in row 2 with its Red test (D-77), because AC-23.20 would fail on a row whose channel is not yet registered; there is no MCP README, so 05 and `mcp.json.example` carry the placement (D-78).
2. **Row 0 (after the D-56 ruling):** MEU-92 registered in `meu-status.yaml` (modelled on MEU-91: phase `'7'`, band P2, matrix item `7.5`, `build_ref` `07-distribution.md#mcp-server-bundle-residual`, depends on MEU-25 and MEU-71), the P2 band range extended to MEU-92, the 07 anchor section written, then render.
3. **Row 10:** 05 `:329`, 06 preload listing and `:1159`, 07 `:253`, the matrix rows.
4. **H1/H2:** MEU statuses through `meu_status.py`, never by hand in `BUILD_PLAN.md`.

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s31b-build-plan-audit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s31b-build-plan-audit.txt; exit $code
```

---

## Verification Plan

> [!IMPORTANT]
> Every command runs through `rtk proxy` and writes to `C:/Temp/av-kit/`. `validate-task.ps1` holds the exact procedure for each check and removes ELECTRON_RUN_AS_NODE from its own environment first.

### 0. Task contract (planning time; re-run at H2)

```powershell
rtk proxy uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/task.md *> C:/Temp/av-kit/s31b-task-lint.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s31b-task-lint.txt; exit $code
```

### 1. Prerequisites and baseline (row 0)

`-Check prereq`: no graph directory; headroom only with the execution-phase decision; the grouping D-56 row is ruled; MEU-23 and MEU-25 `approved`; MEU-71 and MEU-92 `pending` with `execution_plan`; `npm ci` in `ui/` and `mcp-server/` and the Electron binary. `-Check baseline` writes `baseline.sha` and the ui Vitest, mcp-server Vitest and Playwright counts.

### 2. Red (rows 2, 6)

`-Check red71` / `-Check red92` build `mcp-server/dist` first (AC-71.9 and AC-71.10 spawn it), then run the MEU's ui and mcp-server test files. They pass only when every failure is an assertion in that MEU's ACs, a TA pin, or a declared new-module file's missing symbol (S4). `red71` also builds the app and runs the `AC-71` Electron spec, which must fail on an `expect()`. AC-92.4 is runtime-only and proved by `pkg-probe`.

### 3. Green (rows 3–4, 7–8)

`-Check green71-main` (main, preload and mcp-server halves), `-Check green71` (renderer and Electron), `-Check green92` (bundle, then the MEU-92 files), `-Check pkg-probe` (`PKG_PROBE`).

### 4. Targeted gates (rows 5, 9)

`-Check gate71` / `-Check gate92`: `ui-types`, `ui-lint`, `mcp-types`, the MEU's files plus the IPC/settings regression set and the full mcp-server suite, build, the Electron specs (`mcp-setup-prompt`, `settings`) and `--repeat-each=10` on `AC-71`.

### 5. Full D6 gate (H1-2)

`-Check gate` runs PROFILE D6's UI and MCP stages fresh and in order: `npm ci` (ui and mcp-server) + Electron `install.js`, `ui-types`, `ui-lint`, `mcp-types`, `mcp-build`, `mcp-bundle`, `pkg-current` (`PKG_EVIDENCE` against the fresh bundle), `ui-build`, the primitive-harness build, the region-picker stub (D-93), `mcp-tests` (JSON), `ui-tests` (JSON), `ui-electron` (JSON), `state-render`, `task-contract`, then the source audit over the changed source files. It checks `COUNT_FLOORS` and records input identity (§Validation stage contract). `py-*`, `openapi` and `mcp-audit` are skipped on the `scope` basis (nothing under `packages/` or `openapi.committed.json` changes; no MCP tool surface changes, and `mcp-server/scripts/audit/run.ts` audits tool surfaces, not the server instructions); the receipt records the skip. No MCP lint script exists, and none is invented.

### 6. Product scope (H1-4)

`-Check scope` takes every path changed since `baseline.sha` (committed, uncommitted and untracked). Each must be a Files Modified path, under a listed directory, or a closeout output. It refuses any change under `packages/`, `tools/`, `native/`, `openapi.committed.json` or `docs/build-plan/11-page-layout.md`, and any `ui/src/main/` file outside the four named. `plan_checks.py selftest` holds negative cases for each.

### 7. Closeout (H1-5 to H2)

Through `tools/validate_closeout_artifacts.py` (`--handoff`, `--reflection`) and `lint_task_contract.py`, with the exact commands in `task.md`.

### 8. OpenAPI drift (G8)

Not applicable: `packages/api/` is outside `PRODUCT_SCOPE`, which `scope` proves.

---

## GUI Element Compliance Check

The §4A reference files are not shipped (`gui-refs-not-shipped`, as in Sessions 29/30/38). Feedback tiers follow the local usage: T0 is an immediate visual state change, T1 an inline status message.

| Element | Variant / size | States | Feedback tier (G35) | Standard | E2E |
|---|---|---|---|---|---|
| Client select (`mcp-client-select`) | `GridSelect` (G30) | seven options | T0 (viewer text changes) | G30 | AC-71.15 |
| Scope select (`mcp-scope-select`) | `GridSelect` (G30) | user / project / disabled | T0 | G30 | AC-71.15 |
| Prompt viewer (`mcp-setup-prompt`) | read-only textarea, mono | loaded / unavailable | T0 | G33 (no raw colours) | AC-71.15 |
| Copy prompt (`mcp-copy-prompt-btn`) | `Button` secondary sm | enabled / disabled | T1 (`mcp-prompt-status`) | G35 | AC-71.15 |
| Advanced disclosure (`mcp-advanced`) | native `<details>` | closed / open | T0 | native semantics | AC-71.15 |
| Copy MCP config / Pin (existing) | unchanged | unchanged | unchanged | 06 `:1159` | AC-71.15, settings W4-2/W4-3 |

The `source-audit` stage enforces G32/G33. E2 is met: every new interactive element has a registered test id and an Electron assertion.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `prereq` refuses: a graph directory, headroom without an execution-phase decision, grouping D-56 unruled, or an MEU in the wrong state | Stop. Re-run the context-tool gate or ask for the ruling. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` | Stop for the human with a Decision Brief naming the test and the minimal amendment. No test edit. |
| S3 | The Electron binary with ELECTRON_RUN_AS_NODE does not run the server (AC-71.10), or the fuse is off | Stop Green. Decision Brief with the spawn evidence; never fall back to bare `node` in the prompt. |
| S4 | A Red is not an assertion failure (collection or import error outside the declared new-module files) | Fix the test setup only, then re-prove Red. |
| S5 | The host refuses the directory junction, or `realpathSync.native` does not equate the junction path with the file | Stop. Decision Brief with the evidence; the guard design is re-reviewed. |
| S6 | The bundle does not start (a dependency's dynamic `require` or ESM interop) or a dependency has no licence file | Stop MEU-92 Green. Decision Brief: an esbuild `external` plus a copied package, or D-56 option 2. |
| S7 | `electron-builder --win dir` fails for a reason outside this plan (signing, the region-picker `dotnet` step, disk) | Record the evidence and present a Decision Brief; never mark row 8 `[x]`. |
| S8 | A gate failure that is not a product defect (environment, flaky infrastructure) | Record the evidence and present a Decision Brief; never mark the row `[x]`. |
| S9 | Review cap (plan 3, execution 6), or the reviewer is unavailable | HARD STOP with TL;DR (create-plan §5d). |

## Amendment A-1 (execution, 2026-10-17)

Row 0's first baseline stopped under S8: AC-41.3 read Zorivest's working tree, which had moved (walkthrough §S8 stop). Mat directed "decouple anything to do with zorivest and create our own copy of files" and then ruled D-90, D-91 and D-92 (USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1' (answering the HDP briefs, walkthrough §Mat's direction and the HDP re-run)).

- **Row 0a (new, before the baseline):** the copies and `PROVENANCE.md`, AC-41.3 on the copy, the four canon pointers rewritten, `QUEUE-PILL-TOKEN-DRIFT` resolved. Red is `s31b-0a-red-queue-canon.txt` (AC-41.3 failing on the live file). `-Check decouple` validates it:
  - `plan_checks.py decouple`: each copy matches its `PROVENANCE.md` row by LF sha256, size and git blob id, and nothing unlisted sits beside them; no Zorivest checkout path in the code or live canon under `DECOUPLE_SCAN`, except the golden-rule-4 prohibition; AC-41.3 names the copy; the issue is resolved with evidence under this plan;
  - the queue-canon Vitest, then the `issue_triage.py` and `meu_status.py` render checks.
- **Baseline:** row 0 now depends on 0a. Its clean-tree guard allows exactly `ui/tests/unit/queue-canon.test.ts`, so `baseline.sha` stays `6097cf5` and the baseline counts include AC-41.3 passing on the copy.
- **Picker stub (D-93):** `baseline` and `gate` build the gitignored region-picker stub (`build:picker-stub`) before the Electron suite.
- **Scope:** the Amendment A-1 Files Modified table. No product source, no `styles.css` hex and no frozen path changes, so nothing visible changes.
- **Review and commit:** H1-7 reviews A-1 with the rest. At closeout A-1 is proposed as its own commit ahead of the MEU-71/92 commit. It holds the copies, the test line, the canon pointers and the issue; files both commits touch are staged by hunk, and this plan folder goes with the MEU-71/92 commit. Session 35 picks A-1 up when it merges `main`.
- **Not changed:** closed plans, handoffs, reflections and earlier decision records keep their Zorivest citations as history (D-91 A).

## Decision Log

Research engine for this plan: `native` (Claude Code `WebSearch` and the local Claude Code CLI help, 2026-10-16), plus the zorivest `QF-SETUP` build docs reviewed earlier this session. Grouping rows D-1, D-2, D-6, D-7, D-55 and D-56 are carried forward and listed in the reflection with stage `grouping`; D-56 is ruled at row 0. The triage decisions D-46 to D-58 on the two known issues are cited in prose only. This plan's ids start at D-71.

```yaml
decision_log:
  - id: D-71
    stage: planning
    question: "Where is the prompt text built, and from what inputs?"
    resolution: autonomous
    class: two-way
    chosen: "A pure buildSetupPrompt in ui/src/main/mcp-setup-prompt.ts with no token input, no I/O and no clock (PROMPT_BUILDER)"
    source_tag: Local Canon
    precedents: ["ui/src/main/python-manager.ts:56 - pure path helpers in main", "docs/build-plan/07-distribution.md:288 - golden output per client block"]
    research: { engine: none, sources: [] }
    reasoning: "Golden tests need a deterministic function. Building it in main keeps the executable path and app data out of renderer code, and leaving the token out of the signature makes the token boundary structural, not a filter."
  - id: D-72
    stage: planning
    question: "How does main know the server path in dev and packaged modes?"
    resolution: autonomous
    class: two-way
    chosen: "mcpServerEntry({ packaged, resourcesPath, dirname }): resources/mcp-server/index.mjs packaged, ../../../mcp-server/dist/index.js from ui/out/main in dev (SERVER_ENTRY)"
    source_tag: Local Canon
    precedents: ["ui/src/main/python-manager.ts:56 - packagedBackendPath(resourcesPath)", "ui/electron-builder.yml:35-36 - extraResources to mcp-server"]
    research: { engine: none, sources: [] }
    reasoning: "It mirrors the backend helper, is testable without Electron, and keeps one switch for the MEU-92 file name."
  - id: D-73
    stage: planning
    question: "Which Claude Code command form, and how are paths quoted?"
    resolution: autonomous
    class: two-way
    chosen: "claude mcp remove avkit --scope S, then claude mcp add avkit --scope S -e ELECTRON_RUN_AS_NODE=1 -e \"AVKIT_APP_DATA=path\" -- \"exe\" \"server\"; double quotes, and a path holding a double quote, $ or backtick raises PATH_QUOTE_ERROR (CLAUDE_CODE_BLOCK)"
    source_tag: Research-backed
    precedents: ["C:/Temp/av-kit/s31b-claude-mcp-add-help.txt - CLI 2.1.296: -e, --env is variadic; --scope defaults to local", "known-issues MCP-SETUP-PROMPT - the failed F8 entry was local scope"]
    research: { engine: native, sources: ["https://docs.anthropic.com/en/docs/claude-code/mcp - claude mcp add, scopes user/project/local, -e env, -- before the command"] }
    reasoning: "Remove-then-add replaces any stale entry, including the F8 one. A variadic -e would swallow the command without the -- separator. Double quotes keep spaces and backslashes literal in both PowerShell and bash; the three refused characters are the ones either shell would expand."
  - id: D-74
    stage: planning
    question: "Entry name and per-client shapes"
    resolution: autonomous
    class: two-way
    chosen: "Key avkit everywhere; Codex TOML [mcp_servers.avkit] plus an env table; Cursor, Claude Desktop, Windsurf and generic use mcpServers; VS Code uses servers with type stdio (CODEX_BLOCK, JSON_BLOCKS, SERVER_KEY)"
    source_tag: Research-backed
    precedents: ["docs/build-plan/07-distribution.md:282 - the client list and shapes", "mcp-server tool names are avkit_* - the key matches the tool prefix"]
    research: { engine: native, sources: ["https://developers.openai.com/codex/mcp - [mcp_servers.name] with command, args, env", "https://docs.cursor.com/context/model-context-protocol - mcpServers in ~/.cursor/mcp.json or .cursor/mcp.json", "https://code.visualstudio.com/docs/copilot/chat/mcp-servers - servers with type stdio in mcp.json", "https://modelcontextprotocol.io/quickstart/user - claude_desktop_config.json mcpServers", "https://docs.windsurf.com/windsurf/cascade/mcp - ~/.codeium/windsurf/mcp_config.json"] }
    reasoning: "One key across clients lets the merge step say 'only avkit'. A hyphen-free key avoids clients that normalise or reject hyphens in TOML bare keys."
  - id: D-75
    stage: planning
    question: "How is scope shown for clients without a project file?"
    resolution: autonomous
    class: two-way
    chosen: "GridSelect gains an optional disabled prop; scope is forced to user and disabled for claude-desktop, windsurf and generic (SCOPE_DISABLED)"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/settings/SettingsPage.tsx:189-222 - GridSelect"]
    research: { engine: none, sources: [] }
    reasoning: "Hiding the select would shift the layout per client; disabling keeps it stable and states the reason. The builder still throws on an invalid pair, so the UI rule and the IPC rule cannot drift apart silently."
  - id: D-76
    stage: planning
    question: "How should the server decide it is the entry point?"
    resolution: autonomous
    class: two-way
    chosen: "isMainModule compares realpathSync.native of argv[1] and of import.meta.url, case-insensitive on win32, false on any error (ENTRY_GUARD)"
    source_tag: Research-backed
    precedents: ["mcp-server/src/index.ts:31-34 - suffix guard that misses resources/mcp-server/index.js", "known-issues MCP-PACKAGED-ENTRY-UNREACHABLE"]
    research: { engine: native, sources: ["https://nodejs.org/api/cli.html#--preserve-symlinks-main - by default Node resolves the main module to its real path", "https://nodejs.org/api/fs.html#fsrealpathsyncnativepath-options - native realpath"] }
    reasoning: "A suffix list breaks on every new layout (packaged, bundled, junctioned). Comparing real paths is layout-free, and returning false on error keeps test imports from starting the server."
  - id: D-77
    stage: planning
    question: "When does the gui-actions-index Copy prompt row land?"
    resolution: autonomous
    class: two-way
    chosen: "In row 2, with its Red test, not at plan time (INDEX_ROW)"
    source_tag: Local Canon
    precedents: ["ui/tests/unit/gui-actions-audit.test.ts:182-215 - AC-23.20 resolves every non-REST settings row to a registered channel", "docs/build-plan/07-distribution.md:287 - 'gui-actions-index gains the Copy prompt row at plan time'"]
    research: { engine: none, sources: [] }
    reasoning: "A plan-time row would turn main red (AC-23.20) until the channel exists. Landing it with the Red keeps main green and the row still precedes the code; the 07 Docs row is amended to say so."
  - id: D-78
    stage: planning
    question: "07 asks the MCP README to name the placement. Which README?"
    resolution: autonomous
    class: two-way
    chosen: "No MCP README exists; 05 :329, mcp.json.example and SETUP_INSTRUCTION carry it, and the 07 Docs row is amended"
    source_tag: Local Canon
    precedents: ["mcp-server/ has no README (ls 2026-10-16)", "docs/build-plan/05-mcp-server.md:329 - the Phase 7 row"]
    research: { engine: none, sources: [] }
    reasoning: "Writing a new README would add a fourth place to keep in sync. The server instructions reach agents directly, which is where a placement hint helps."
  - id: D-79
    stage: planning
    question: "What happens to docs/distribution/mcp.json.example?"
    resolution: autonomous
    class: two-way
    chosen: "Rewrite it to the generic block with placeholders, key avkit, ELECTRON_RUN_AS_NODE and no token (EXAMPLE_CONFIG)"
    source_tag: Local Canon
    precedents: ["docs/distribution/mcp.json.example - command node, the RESOURCES-variable path to mcp-server/index.js, AVKIT_API_TOKEN"]
    research: { engine: none, sources: [] }
    reasoning: "The example contradicts the token boundary and the launch rule. Leaving it would teach the shape this MEU removes."
  - id: D-80
    stage: planning
    question: "How does the agent report failure codes?"
    resolution: autonomous
    class: two-way
    chosen: "The verify step maps an error text starting with code: to RESULT: failed (verify, code) (RESULT_LINE)"
    source_tag: Local Canon
    precedents: ["mcp-server/src/client.ts:71 - toToolError writes code: message", "docs/build-plan/07-distribution.md:284 - error is the server's error code"]
    research: { engine: none, sources: [] }
    reasoning: "The code is already the first token of every tool error, so the agent copies it rather than paraphrasing."
  - id: D-81
    stage: planning
    question: "Backup file name"
    resolution: autonomous
    class: two-way
    chosen: "file.avkit-backup-yyyyMMddTHHmmssZ in UTC, chosen by the agent at run time (BACKUP_NAME)"
    source_tag: Local Canon
    precedents: ["docs/build-plan/07-distribution.md:284 - file.avkit-backup-UTC"]
    research: { engine: none, sources: [] }
    reasoning: "A basic ISO timestamp sorts by name and has no characters that Windows file names reject."
  - id: D-82
    stage: planning
    question: "How is the launch shape proved without a packaged build in MEU-71?"
    resolution: autonomous
    class: two-way
    chosen: "A ui Vitest spawns the repo's Electron binary with ELECTRON_RUN_AS_NODE=1 on the dev server entry, plus a static FUSE_PIN on electron-builder.yml"
    source_tag: Research-backed
    precedents: ["docs/build-plan/07-distribution.md:281 - a test pins the RunAsNode fuse on"]
    research: { engine: native, sources: ["https://www.electronjs.org/docs/latest/api/environment-variables#electron_run_as_node - starts the process as a normal Node.js process", "https://www.electronjs.org/docs/latest/tutorial/fuses - runAsNode fuse"] }
    reasoning: "The same binary family ships in the installer; the fuse pin catches the one config change that would break it. MEU-92's packaged probe then covers av-kit.exe itself."
  - id: D-83
    stage: planning
    question: "Bundle or ship node_modules, and in what format?"
    resolution: autonomous
    class: two-way
    chosen: "esbuild 0.28.2 (exact), ESM, platform node, target node22, a createRequire banner, output mcp-server/bundle/index.mjs, run by tsx so it is typechecked (BUNDLE_SCRIPT)"
    source_tag: Research-backed
    precedents: ["mcp-server/package.json - type module", "mcp-server/tsconfig.scripts.json - includes scripts/**/*.ts"]
    research: { engine: native, sources: ["https://esbuild.github.io/api/#format-esm - ESM output", "https://esbuild.github.io/api/#banner - banner injection", "https://esbuild.github.io/api/#metafile - inputs per package"] }
    reasoning: "One file with no install step is the smallest packaged surface. The banner gives inlined CommonJS dependencies a require. Electron 42's Node runs node22-level ESM."
  - id: D-84
    stage: planning
    question: "Is MCP_ENTRY_PROBE a record or a pass condition?"
    resolution: autonomous
    class: two-way
    chosen: "A pass condition on a fresh electron-builder --win dir build, in place and on a hermetic copy (PKG_PROBE), bound to the hashes of the files it proved (PKG_EVIDENCE)"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-tts-engine-runtime/gate_lib.py:540-573 - record-only probe", "p7 RULE-1 - packaged behaviour is proved on a built tree"]
    research: { engine: none, sources: [] }
    reasoning: "Session 32 recorded the failure and no one owned it. The hermetic copy proves the bundle does not borrow modules from the repository. Plan review round 1 (F1) showed that a bare passed flag lets row 9 and the full gate accept a proof of bytes that have since changed, so every consumer re-hashes the bound files."
  - id: D-85
    stage: planning
    question: "How are licences of inlined dependencies shipped?"
    resolution: autonomous
    class: two-way
    chosen: "collectLicenses reads the esbuild metafile and writes LICENSES.txt next to the bundle; a missing licence fails the build (BUNDLE_LICENSES)"
    source_tag: Research-backed
    precedents: ["mcp-server/package.json - @modelcontextprotocol/sdk and zod are MIT"]
    research: { engine: native, sources: ["https://esbuild.github.io/api/#legal-comments - legal comments do not cover full licence texts"] }
    reasoning: "Inlining removes the packages' own LICENSE files from the shipped tree, so their notices must travel with the bundle. Driving it from the metafile covers transitive packages without a hand list."
  - id: D-86
    stage: planning
    question: "How does the renderer get the prompt without the token crossing IPC?"
    resolution: autonomous
    class: two-way
    chosen: "A strict get-mcp-setup-prompt channel whose handler builds the text from a mcpServerLaunch dependency and appData, never calling readMcpToken (PROMPT_CHANNEL, PROMPT_HANDLER, LAUNCH_DEP)"
    source_tag: Local Canon
    precedents: ["ui/src/main/ipc.ts:138 - readMcpToken dependency used by copy-mcp-config", "docs/build-plan/06-gui.md:1159 - never display the token"]
    research: { engine: none, sources: [] }
    reasoning: "The prompt needs paths only main knows; returning text over a new channel keeps the token out of the renderer, and the spy test makes that checkable."
  - id: D-87
    stage: planning
    question: "How does Copy prompt write the clipboard?"
    resolution: autonomous
    class: two-way
    chosen: "The existing writeClipboardText with the viewer's text (COPY_PROMPT)"
    source_tag: Local Canon
    precedents: ["ui/src/main/ipc.ts:389-394 - write-clipboard-text"]
    research: { engine: none, sources: [] }
    reasoning: "The text is already in the renderer for display; a second main-side copy channel would duplicate an existing one."
  - id: D-88
    stage: planning
    question: "How is the entry guard proved on a packaged-like layout before MEU-92?"
    resolution: autonomous
    class: two-way
    chosen: "An mcp-server test junctions tmp/resources/mcp-server to mcp-server/dist and runs node on index.js through it, with a fake backend and no token"
    source_tag: Research-backed
    precedents: ["known-issues MCP-PACKAGED-ENTRY-UNREACHABLE - resources/mcp-server/index.js never started"]
    research: { engine: native, sources: ["https://nodejs.org/api/fs.html#fssymlinksynctarget-path-type - type junction on Windows needs no elevation"] }
    reasoning: "It reproduces the packaged file name without a packaged build, is Red under today's guard, and also proves the liveness/dependencies split the prompt relies on."
  - id: D-89
    stage: execution
    question: "What shape does av-kit's copy of the Zorivest files take?"
    resolution: autonomous
    class: two-way
    chosen: "Copies under _inspiration/zorivest/, each the blob at a named Zorivest commit (git show of that commit and path, never the working tree), with a PROVENANCE.md row of source path, commit, date, git blob id and LF sha256; AC-41.3 reads the copy with its assertions unchanged"
    source_tag: Local Canon
    precedents: ["_inspiration/_zorivest_mcp_tool_audit_skill.md - Mat committed a copy so av-kit stopped extracting it from the Zorivest checkout (MCP-LIVE-AUDIT-WORKFLOW, 2026-09-30)", "known-issues QUEUE-PILL-TOKEN-DRIFT, Session 37 A-4 and the 2026-10-14 BASELINE_RED - AC-41.3 broke three times as Zorivest moved"]
    research: { engine: pomera, sources: ["https://testrigor.com/blog/hermetic-testing/ - a failure should mean a code defect, not an external factor", "https://github.com/open-mercato/open-mercato/pull/4277 - committed canonical globals.css snapshot with a per-token drift check", "RevealUI 942c83a - canonical tokens.css mirror with MANIFEST.sha256 and a parity test"] }
    reasoning: "Precedent and research converge on a committed snapshot with recorded provenance. It is two-way, changes nothing a user sees, and sets no threshold, so it needs no ruling."
  - id: D-90
    stage: execution
    question: "Which version of Zorivest's globals.css becomes av-kit's copy?"
    resolution: human
    class: two-way
    chosen: "61243baf, the commit before Zorivest MEU-662: it holds exactly the hexes av-kit ships, so decoupling changes nothing visible"
    source_tag: Human-approved
    human_ref: "USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1' (answering the HDP briefs, walkthrough §Mat's direction and the HDP re-run)"
    precedents: ["walkthrough §S8 stop - 1f254832 (MEU-662) changed the light status and accent hexes; 61243baf still holds every PORTED_TOKENS hex", "docs/build-plan/10-queue-card-ui.md:118-120 - pill labels are text-fg, worst case 6.61:1"]
    research: { engine: pomera, sources: ["https://webaim.org/articles/contrast/ - WCAG 1.4.3 text 4.5:1, 1.4.11 non-text 3:1", "https://testparty.ai/ - 1.4.11 holds status icons to 3:1"] }
    reasoning: "The pill hue colours only the icon and a 10% fill, and #ea580c (about 3.56:1) and #16a34a (about 3.30:1) on white clear 1.4.11, so the darker palette fixes no failing criterion; adopting it later is an ordinary av-kit change."
  - id: D-91
    stage: execution
    question: "How far does 'decouple anything to do with zorivest' go?"
    resolution: human
    class: two-way
    chosen: "A: remove every dependency and keep the history. AC-41.3 reads the copy; 10-queue-card-ui.md :64 and §Status token table, gui-actions-index.md :3 and BUILD_PLAN golden rule 4 make av-kit the owner with Zorivest as provenance only; cloud-local-collaboration drops AC-41.3 from ENV_BOUND_TESTS; globals.css and gui-actions-index.md are copied at 61243baf and 05n-agent-connect.md at ca693695; QUEUE-PILL-TOKEN-DRIFT closes with its re-port path overturned; closed plans, handoffs, reflections and decision records stay untouched"
    source_tag: Human-approved
    human_ref: "USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1' (answering the HDP briefs, walkthrough §Mat's direction and the HDP re-run)"
    precedents: ["C:/Temp/av-kit/s31b-zv-active-paths.txt - one runtime read (queue-canon.test.ts:12) and four canon pointers", "AGENTS/BUILD_PLAN golden rule 5 - inspiration is intent, not code (against copying every cited source file)"]
    research: { engine: none, sources: [] }
    reasoning: "Fixing only the test would leave the canon saying the palette is whatever the Zorivest checkout declares, so the next Zorivest change would couple av-kit again; a full scrub would copy dozens of source files and erase where patterns came from."
  - id: D-92
    stage: execution
    question: "How does the decoupling reach main?"
    resolution: human
    class: two-way
    chosen: "Amendment A-1 in Session 31b: a new row 0a before the baseline, reviewed by H1-7, proposed at closeout as its own commit ahead of the MEU-71/92 commit; Session 35 picks it up when it merges main"
    source_tag: Human-approved
    human_ref: "USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1' (answering the HDP briefs, walkthrough §Mat's direction and the HDP re-run)"
    precedents: ["Session 37 amendment A-4 - an S8-class baseline failure resolved by a Mat-approved amendment", "Session 39 D-24 - an execution-stage stop resolved by an amendment that added files to Files Modified and the scope allow-list"]
    research: { engine: none, sources: [] }
    reasoning: "A separate mini-session would block 31b for a full plan-and-review cycle on a small change, and carrying AC-41.3 as a baseline failure again would defer what Mat asked for and weaken the gate."
  - id: D-93
    stage: execution
    question: "The fresh worktree lacked the gitignored region-picker stub, so four capture-picker specs failed in the S8 evidence run. Does the plan build it?"
    resolution: autonomous
    class: two-way
    chosen: "baseline and gate run npm --prefix ui run build:picker-stub before the Electron suite (Invoke-PickerStub, gate-picker-stub)"
    source_tag: Local Canon
    precedents: ["RULE-1 (Session 36 reflection): every gitignored build output the suites need is its own stage", "Session 39 G-1 - mcp-build moved before mcp-tests so the gate is valid in a fresh worktree"]
    research: { engine: none, sources: [] }
    reasoning: "The repo's own script writes only ignored output; without the stage the baseline and gate depend on whatever an earlier session left in native/**/publish/."
```

---

## Research References

- Claude Code MCP: https://docs.anthropic.com/en/docs/claude-code/mcp
- Codex MCP config: https://developers.openai.com/codex/mcp
- Cursor MCP: https://docs.cursor.com/context/model-context-protocol
- VS Code MCP servers: https://code.visualstudio.com/docs/copilot/chat/mcp-servers
- Claude Desktop config: https://modelcontextprotocol.io/quickstart/user
- Windsurf MCP: https://docs.windsurf.com/windsurf/cascade/mcp
- MCP lifecycle (`initialize`, 2025-06-18): https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle
- Electron `ELECTRON_RUN_AS_NODE`: https://www.electronjs.org/docs/latest/api/environment-variables#electron_run_as_node
- Electron fuses: https://www.electronjs.org/docs/latest/tutorial/fuses
- Node main-module symlinks: https://nodejs.org/api/cli.html#--preserve-symlinks-main
- Node `fs.symlinkSync` junctions: https://nodejs.org/api/fs.html#fssymlinksynctarget-path-type
- esbuild API (format, banner, metafile): https://esbuild.github.io/api/

## Validation stage contract

The checks bind to PROFILE D6 (`.agent/docs/commands.md` ~`:190-235`):

- **Static:** `ui-types`, `ui-lint`, `mcp-types` and the `source-audit`.
- **Targeted:** the Red/Green files and the per-MEU gates.
- **Fresh full:** `-Check gate` (H1-2). It runs all UI and MCP stages from `npm ci`, and covers `state-render` and `task-contract`. `pkg-current` re-checks `PKG_EVIDENCE` after the fresh bundle. The `py`, `openapi` and `mcp-audit` stages are skipped on the `scope` basis.
- **Runtime:** `PKG_PROBE` (row 8) and `MCP_PROMPT_LOOK` (manual, Mat).

Every check runs in `pwsh` from the worktree root (`P:/av-kit-wt/s31b-gui-mcp-setup-prompt`) and writes raw receipts under `C:/Temp/av-kit/s31b-*`. The handoffs carry `evidence.v1` records.

Input identity is obtained independently by `-Check gate`. It records `git rev-parse HEAD`, the uncommitted product paths (`git status --porcelain --untracked-files=all -- ui mcp-server docs`) with a SHA-256 of each one's working-tree content, untracked files included, the SHA-256 of `ui/package-lock.json` and `mcp-server/package-lock.json`, `node --version` and the installed Electron version, in `gate-result.json`. The execution review reads the gate receipt for the commit under review. Any code change after the gate re-runs `-Check gate` before the next review round. Intermediate reuse is disabled: partial runs never satisfy the full gate.
