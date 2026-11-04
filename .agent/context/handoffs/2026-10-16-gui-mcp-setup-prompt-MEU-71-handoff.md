---
date: "2026-10-17"
project: "gui-mcp-setup-prompt"
meu: "MEU-71"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md"
build_plan_section: "bp07"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex via local dispatch"
predecessor: "none"
---

# Handoff: 2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-71 — `gui-mcp-setup-prompt`. The Settings → MCP card shows a per-client setup prompt that the user copies into their own agent, and the MCP server entry starts from any path that reaches it.
**Build Plan Section**: [07 §MCP setup prompt](../../../docs/build-plan/07-distribution.md) (`:279-288`).
**Predecessor**: none (first MEU of Session 31b; MEU-92 follows in the same session).

The work spans main, preload, renderer and the MCP server:

- **Prompt builder (main).** `ui/src/main/mcp-setup-prompt.ts` holds `CLIENT_SET` (`MCP_CLIENTS`: Claude Code, Codex, Cursor, VS Code, Claude Desktop, Windsurf, Other), `SCOPE_RULE` (project scope only for the first four), and `buildSetupPrompt`, which writes the six `PROMPT_STEPS` and the `RESULT_LINE` around one client block: a `claude mcp add` line (`CLAUDE_CODE_BLOCK`), a TOML table (`CODEX_BLOCK`), or a JSON object (`JSON_BLOCKS`). Every block launches the app's own executable with `ELECTRON_RUN_AS_NODE=1` and names `AVKIT_APP_DATA`, never the token (`TOKEN_BOUNDARY`). `mcpServerEntry` gives the packaged `resources/mcp-server/index.mjs` or the dev `mcp-server/dist/index.js` (`SERVER_ENTRY`).
- **IPC.** A strict `get-mcp-setup-prompt` channel (`PROMPT_PAYLOAD`: `client` in `CLIENT_SET`, `scope` `user`/`project`, no other key) returns `{ text }`. `main/index.ts` wires `mcpServerLaunch` (`process.execPath` and `mcpServerEntry`), and the handler returns `LAUNCH_MISSING_ERROR` without it. The preload exposes `getMcpSetupPrompt`.
- **Renderer.** The MCP card is the token chip, a Client and a Scope select, a read-only prompt viewer, **Copy prompt** with a status line, then a closed **Advanced** disclosure holding the unchanged Copy MCP config and Pin endpoint buttons (`CARD_LAYOUT`, `ADVANCED_DISCLOSURE`). A user-only client forces and disables the scope (`SCOPE_DISABLED`).
- **MCP server.** `entry-guard.ts` `isMainModule` compares real paths, so the server starts through a junction, a drive-letter case change or the packaged layout (`ENTRY_GUARD`). The server instructions gain one setup line (`SETUP_INSTRUCTION`), and `docs/distribution/mcp.json.example` takes the `EXAMPLE_CONFIG` shape.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md) §MEU-71. **Execution authorization:** `USER_EXPLICIT` 2026-10-17 "proceed" after the go/no-go and the D-90 to D-92 ruling ([walkthrough.md](../../../docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/walkthrough.md)).

**Test amendments applied (approved in the plan):** TA-1 (registered-channel pins 20 → 21 and the census entries), TA-2 (`gui-actions-audit` IPC cell resolution and the Copy prompt help id) and TA-3 (`settings.test.ts` W4-2 and W4-3 open Advanced first). The only other change to an AC test after Red is D-94 (the AC-71.15 clipboard retry).

Amendment A-1 (row 0a, D-89 to D-93) removed av-kit's dependency on the Zorivest checkout before the baseline. It is not MEU-71 product work; its decisions are logged here because this is the session's first handoff, and it is proposed as its own commit (D-92).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-71.1 | unit | Each client and scope pair equals its golden file; JSON and TOML blocks parse and carry `MCP_LAUNCH`; swapping `command` and `serverPath` changes every output; a Codex path with `"` keeps the TOML valid | 07 `:282`, `:288` | `ui/tests/unit/mcp-setup-prompt.test.ts` `AC-71.1 …` (6) | ✅ |
| AC-71.2 | unit | `SCOPE_RULE`: project scope names the project file and `--scope project`; user scope `--scope user`; project scope throws `PROJECT_SCOPE_ERROR` for user-only clients | 07 `:280`; D-48 | `mcp-setup-prompt.test.ts` `AC-71.2 …` (2) | ✅ |
| AC-71.3 | unit | `TOKEN_BOUNDARY`: `AVKIT_APP_DATA` and `ELECTRON_RUN_AS_NODE` in every output; no token, `AVKIT_API_TOKEN` or `${`; a `$` path throws `PATH_QUOTE_ERROR` | 07 `:283`, `:288`; D-49, D-57 | `mcp-setup-prompt.test.ts` `AC-71.3 …` (2) | ✅ |
| AC-71.4 | unit | `PROMPT_STEPS` in order and `RESULT_LINE` last; liveness never counts; `token_missing:` maps to `RESULT: failed (verify, token_missing)` | 07 `:284`, `:288`; D-52, D-53, D-58 | `mcp-setup-prompt.test.ts` `AC-71.4 …` (2) | ✅ |
| AC-71.5 | unit | `mcpServerEntry` packaged and dev paths (`SERVER_ENTRY`) | D-72 | `ui/tests/unit/mcp-server-entry.test.ts` `AC-71.5 …` (2) | ✅ |
| AC-71.6 | unit | `PROMPT_HANDLER` returns the Codex text with launch and app data, never reads the token; bad payloads, a missing launch and a user-only client at project scope return `{ ok: false }` | 07 `:288`; D-86 | `ui/tests/unit/mcp-prompt-ipc.test.ts` `AC-71.6 …` (2) | ✅ |
| AC-71.7 | unit | `PROMPT_CHANNEL` registered (21 channels, TA-1); `getMcpSetupPrompt` preload key invokes the channel; a wrong-type payload is refused | `PRELOAD_KEY`; G27 | `mcp-prompt-ipc.test.ts` `AC-71.7 …` (2); `ipc-strict-census.test.ts` (TA-1) | ✅ |
| AC-71.8 | unit | `isMainModule` true for the file, a junction, a drive-letter case change and the packaged layout; false for another file, `undefined` and a missing path | `MCP-PACKAGED-ENTRY-UNREACHABLE`; D-76 | `mcp-server/tests/entry-guard.test.ts` `AC-71.8 …` (5) | ✅ |
| AC-71.9 | integration | `node <tmp>/resources/mcp-server/index.js` through a junction answers `initialize` as `av-kit`; `liveness` succeeds; `dependencies` without a token errors `token_missing:` and the fake backend sees no `/health/dependencies` | `MCP-PACKAGED-ENTRY-UNREACHABLE`; 07 `:288`; D-88 | `mcp-server/tests/entry-spawn.test.ts:141` `AC-71.9 …` | ✅ |
| AC-71.10 | integration | The Electron binary with `ELECTRON_RUN_AS_NODE=1` on the dev entry answers `initialize` (`2025-06-18`, `av-kit`), first stdout line the response; `FUSE_PIN` holds and refuses both fixtures | 07 `:281`; D-82 | `ui/tests/unit/mcp-spawn-electron.test.ts:77`, `:98`, `:103` | ✅ |
| AC-71.11 | unit | `EXAMPLE_CONFIG` parses with `mcpServers.avkit`, `ELECTRON_RUN_AS_NODE` `"1"`, `AVKIT_APP_DATA`; no `AVKIT_API_TOKEN`, `${` or `node` command | D-79 | `mcp-server/tests/example-config.test.ts` `AC-71.11 …` (2) | ✅ |
| AC-71.12 | unit | `SERVER_INSTRUCTIONS` ends with `SETUP_INSTRUCTION`; earlier lines unchanged and in order | 07 `:287`; D-78 | `mcp-server/tests/runtime.test.ts` `AC-71.12 …` (2) | ✅ |
| AC-71.13 | integration | jsdom `SettingsPage`: `CARD_LAYOUT` order, `CLIENT_SET` labels, fetch on mount and change, `SCOPE_DISABLED`, `COPY_PROMPT`, `ADVANCED_DISCLOSURE`; `PROMPT_UNAVAILABLE` and a rejecting fetch | 07 `:286`; D-54 | `ui/tests/unit/settings-mcp-prompt.test.ts` `AC-71.13 …` (8) | ✅ |
| AC-71.14 | unit | `INDEX_ROW` resolves (TA-2) to a registered channel the preload names; the MEU-71 `NEW_TESTIDS` are in `test-ids.ts` and production source; `INDEX_ROW` appears once after `settings:pin_mcp` | 07 `:287`; AC-23.20 precedent | `ui/tests/unit/gui-actions-audit.test.ts:317`, `:336` | ✅ |
| AC-71.15 | integration | Built app: Codex prompt carries `process.execPath` and the app data path; Copy prompt fills the main-process clipboard and shows the status; Claude Desktop disables scope; Advanced starts closed; the copied JSON token appears in no setup prompt | 07 `:286`, `:288`; E2 | `ui/tests/e2e/mcp-setup-prompt.test.ts:94`, `:129` (also `--repeat-each=10` in the gate) | ✅ |
| AC-23 (cross-ref) | regression | AC-23.19 and AC-23.20 Settings index audit, amended by TA-2 | plan `TEST_AMENDMENTS` | `ui/tests/unit/gui-actions-audit.test.ts` `AC-23.19 …`, `AC-23.20 …` | ✅ |
| AC-41 (cross-ref) | regression | AC-41.3 `PILL_TOKEN_SOURCE` reads `_inspiration/zorivest/globals.css` (amendment A-1, row 0a); assertions and `PORTED_TOKENS` unchanged | D-89, D-91 | `ui/tests/unit/queue-canon.test.ts` `AC-41.3 …` (row 0a baseline) | ✅ |
| AC-92 (cross-ref) | — | Owned by MEU-92 (AC-92.1 to AC-92.4): the bundled packaged MCP server | plan MEU-92 | [MEU-92 handoff](2026-10-16-gui-mcp-setup-prompt-MEU-92-handoff.md) | see MEU-92 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-71.1 to AC-71.5, AC-71.10 | load failure on the missing `src/main/mcp-setup-prompt` (three declared new-module files) | pass | `ui/tests/unit/mcp-setup-prompt.test.ts`; `mcp-server-entry.test.ts`; `mcp-spawn-electron.test.ts` |
| AC-71.6, AC-71.7 | 4 assertion failures: the channel is unknown and the preload key is absent | pass | `ui/tests/unit/mcp-prompt-ipc.test.ts:33`, `:48`, `:69`, `:81` |
| AC-71.8 | load failure on the missing `src/entry-guard.js` (declared) | pass | `mcp-server/tests/entry-guard.test.ts` |
| AC-71.9 | the junction launch exits before `initialize`: answer kind `exit`, not `response` | pass | `mcp-server/tests/entry-spawn.test.ts:141` |
| AC-71.11 | 2 assertion failures on the old example (`"command": "node"`, no `ELECTRON_RUN_AS_NODE`) | pass | `mcp-server/tests/example-config.test.ts:11`, `:22` |
| AC-71.12 | `SERVER_INSTRUCTIONS` has 8 lines, not 9 | pass | `mcp-server/tests/runtime.test.ts:45`, `:50` |
| AC-71.13 | 8 assertion failures: the new testids are absent | pass | `ui/tests/unit/settings-mcp-prompt.test.ts:146-270` |
| AC-71.14 (with TA-2 AC-23.19, AC-23.20) | 3 assertion failures: the IPC cell resolves to no registered channel | pass | `ui/tests/unit/gui-actions-audit.test.ts:317`, `:336` |
| AC-71.15 | Electron: test 1 has no `mcp-client-select`; test 2 has no `mcp-advanced` | pass | `ui/tests/e2e/mcp-setup-prompt.test.ts:94`, `:129` |

Every receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/walkthrough.md) (§Red (row 2), §Green, main and server half (row 3), §Green, renderer half (row 4), §MEU-71 gate (row 5)).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s31b-71-red","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check red71 *> C:/Temp/av-kit/s31b-run-red71.txt (task.md row 2, verbatim)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-71 Red: mcp-build, ui Vitest on the MEU-71 set, mcp-server Vitest on the MEU-71 set, vitest-red classification, ui-build, Electron -g AC-71, e2e-red","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus amendment A-1 (row 0a) and the row 2 tests","output":"PASS mcp-build | ui Vitest 9 files, 17 failed, 22 passed | mcp-server Vitest 4 files, 5 failed, 2 passed | PASS MEU-71 Vitest RED: 18 assertion failures, 0 missing-symbol | PASS ui-build | Electron -g AC-71: 2 failed | PASS MEU-71 E2E RED: ['AC-71.15'] | PASS red71","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-71-green-main","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check green71-main *> C:/Temp/av-kit/s31b-run-green71-main.txt (task.md row 3, verbatim)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-71 main and server Green: mcp-types, mcp-build, mcp-server Vitest on the MEU-71 set, ui Vitest on the main-half set","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus row 0a, the row 2 tests and the row 3 main, preload and server change","output":"PASS mcp-types | PASS mcp-build | mcp-server Vitest 12 passed of 12 | ui Vitest 40 passed of 40 | PASS green71-main","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-71-green-renderer","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check green71 *> C:/Temp/av-kit/s31b-run-green71.txt (task.md row 4, verbatim)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-71 renderer Green: mcp-build, mcp-server Vitest, ui Vitest on the full MEU-71 set, ui-build, Electron -g AC-71","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus row 0a and the whole MEU-71 change before D-94","output":"PASS mcp-build | mcp-server Vitest 12 passed of 12 | ui Vitest 56 passed of 56 | PASS ui-build | Electron -g AC-71: 2 passed, 0 skipped | PASS green71","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-71-gate-run1","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check gate71 *> C:/Temp/av-kit/s31b-run-gate71.txt (task.md row 5, verbatim; receipt kept as s31b-run-gate71-run1.txt)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-71 gate run 1: ui-types, ui-lint, mcp-types, mcp-build, full mcp-server Vitest, ui Vitest on the MEU-71 and regression sets, ui-build, Electron mcp-setup-prompt and settings, -g AC-71 --repeat-each=10","phase":"targeted","exit_code":1,"result":"fail","tested_state":"HEAD 6097cf5 plus row 0a and the whole MEU-71 change before D-94","output":"PASS ui-types | PASS ui-lint | PASS mcp-types | PASS mcp-build | PASS gate71-mcp-vitest: 438 passed of 438 | PASS gate71-ui-vitest: 157 passed of 157 | PASS ui-build | PASS gate71-e2e: expected 15 skipped 0 | repeat: 1 failed, 19 passed; mcp-setup-prompt.test.ts:113 expected the prompt text, received \"s31b-clipboard-sentinel\" | FAIL: gate71-repeat unexpected/flaky specs (flaky counts as a failure)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-71-gate-run2","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check gate71 *> C:/Temp/av-kit/s31b-run-gate71.txt (task.md row 5, verbatim; product-file manifest C:/Temp/av-kit/s31b-gate71-run2-manifest.txt)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-71 gate run 2 after D-94, from the start: ui-types, ui-lint, mcp-types, mcp-build, full mcp-server Vitest, ui Vitest on the MEU-71 and regression sets, ui-build, Electron mcp-setup-prompt and settings, -g AC-71 --repeat-each=10","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf59adc7835fa6062c8bd3d55c679aef4543 plus 52 uncommitted product paths (git diff --name-only HEAD and untracked, excluding the plan folder and handoffs); sha256 of the per-file sha256sum manifest 8d59648a24fb71ca1d01a74a1543e17c07065a32641da933b309ad8a5b401077","output":"PASS ui-types | PASS ui-lint | PASS mcp-types | PASS mcp-build | PASS gate71-mcp-vitest: 438 passed of 438 | PASS gate71-ui-vitest: 157 passed of 157 | PASS ui-build | PASS gate71-e2e: expected 15 skipped 0 | PASS gate71-repeat: expected 20 skipped 0 | PASS gate71","fresh":true}
```

### Quality Gate Results

The MEU-71 gate is `validate-task.ps1 -Check gate71` (task.md row 5). Run 1 failed only at `gate71-repeat`: a Windows clipboard-lock race that the test's own sentinel write triggers (stop S8). Mat ruled D-94 A, and run 2, from the start, passed every step, with the repeat at 20 of 20. The fresh full D6 gate (`-Check gate`, H1-2, receipt `C:/Temp/av-kit/s31b-run-gate.txt`) then passed with both MEUs in the tree: `gate-result.json` `passed: true`, 17 stages exit 0, ui Vitest 1006/1006, mcp-server 446/446, Electron 159 expected and 0 unexpected, `COUNT_FLOORS` pass. Mat's `MCP_PROMPT_LOOK` was "All looks good"; L3 was applied on Claude Desktop instead of Claude Code and ended `RESULT: connected` (walkthrough §MCP_PROMPT_LOOK). Execution review round 1 found F1: the Claude Desktop backup step named the standard `%APPDATA%` file even when step 1 chose the MSIX file. Step 1 now settles on one file and step 2 backs up "the file chosen in step 1" (new AC-71.4 negative test, Red 1 of 13 then Green 13 of 13; `claude-desktop-user.txt` golden updated; other goldens unchanged). The gate re-run after that fix is now the gate of record: ui Vitest 1007/1007, mcp-server 446/446, Electron 159 expected and 0 unexpected (walkthrough §Execution review round 1).

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/main/mcp-setup-prompt.ts` | new (181 lines) | `MCP_CLIENTS`, `MCP_CLIENT_LABELS`, `PROJECT_SCOPE_CLIENTS`, `PATH_QUOTE_ERROR`, `mcpServerEntry`, `buildSetupPrompt` and the three client block kinds |
| `ui/src/main/ipc.ts` | modified | `'get-mcp-setup-prompt'` channel and strict schema; `LAUNCH_MISSING_ERROR`; `IpcDeps.mcpServerLaunch`; the handler case |
| `ui/src/main/index.ts` | modified | `mcpServerLaunch: { command: process.execPath, serverPath: mcpServerEntry({...}) }` |
| `ui/src/main/preload.ts` | modified | `getMcpSetupPrompt` key and invoke |
| `ui/src/renderer/src/env.d.ts` | modified | optional `getMcpSetupPrompt?` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified (+125) | client and scope options, `PROMPT_UNAVAILABLE`, `GridSelect` `disabled`, prompt state and fetch, `copyMcpPrompt`, the card markup and the Advanced disclosure |
| `mcp-server/src/entry-guard.ts` | new | `isMainModule` (realpath, case-insensitive on win32, false on any error) |
| `mcp-server/src/index.ts` | modified | `isMainModule` guard replaces the suffix check; `SETUP_INSTRUCTION` appended |
| `docs/distribution/mcp.json.example` | rewritten (row 3, D-95) | `EXAMPLE_CONFIG`: app executable, `ELECTRON_RUN_AS_NODE`, `AVKIT_APP_DATA`, no token |
| `docs/build-plan/gui-actions-index.md` | modified (row 2) | `INDEX_ROW` `settings:copy_mcp_prompt` |
| `ui/tests/unit/mcp-setup-prompt.test.ts`, `fixtures/mcp-setup-prompt/*.txt` (11) | new | AC-71.1 to AC-71.4 and the golden files |
| `ui/tests/unit/mcp-server-entry.test.ts`, `mcp-prompt-ipc.test.ts`, `mcp-spawn-electron.test.ts`, `settings-mcp-prompt.test.ts` | new | AC-71.5, AC-71.6, AC-71.7, AC-71.10, AC-71.13 |
| `ui/tests/unit/clipboard-image-main.test.ts`, `ipc-strict-census.test.ts`, `login-item-ipc.test.ts`, `ipc-channels.ts` | modified | TA-1 |
| `ui/tests/unit/gui-actions-audit.test.ts` | modified | TA-2; AC-71.14 (append only) |
| `ui/tests/e2e/mcp-setup-prompt.test.ts` | new | AC-71.15; D-94 retry around the two clipboard copies |
| `ui/tests/e2e/settings.test.ts` | modified | TA-3 (two clicks on `mcp-advanced-summary`) |
| `ui/tests/e2e/test-ids.ts` | modified (append only) | MEU-71 `NEW_TESTIDS` |
| `mcp-server/tests/entry-guard.test.ts`, `entry-spawn.test.ts`, `example-config.test.ts` | new | AC-71.8, AC-71.9, AC-71.11 |
| `mcp-server/tests/runtime.test.ts` | modified (append only) | AC-71.12 |

```diff
-const entry = process.argv[1]?.replaceAll("\\", "/");
-if (entry?.endsWith("/src/index.ts") || entry?.endsWith("/dist/index.js")) {
+if (isMainModule(process.argv[1], import.meta.url)) {
   void main();
 }
```

```diff
+    case 'get-mcp-setup-prompt': {
+      // The prompt names the app data folder, never the token: the server reads the token itself.
+      if (deps.mcpServerLaunch === undefined) {
+        return { ok: false, error: LAUNCH_MISSING_ERROR }
+      }
+      const { client, scope } = parsed.data as { client: McpClient; scope: McpScope }
+      try {
+        const text = buildSetupPrompt({ client, scope, ...deps.mcpServerLaunch, appData })
+        return { ok: true, value: { text } }
+      } catch (error) {
+        return { ok: false, error: error instanceof Error ? error.message : String(error) }
+      }
+    }
```

Amendment A-1 (row 0a, its own proposed commit per D-92): `_inspiration/zorivest/` (three copies and `PROVENANCE.md`), `ui/tests/unit/queue-canon.test.ts`, `docs/build-plan/10-queue-card-ui.md`, `docs/build-plan/gui-actions-index.md:3`, `docs/BUILD_PLAN.md` golden rule 4, `.agent/docs/cloud-local-collaboration.md`, `.agent/context/known-issues.yaml` and its rendered `.md`.

Shared by both MEUs: the plan folder `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/` and the hub files listed in the plan's §Shared table (row 10 and H1/H2).

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
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
    precedents: ["walkthrough §S8 stop - 1f254832 (MEU-662) changed the light status and accent hexes; 61243baf still holds every PORTED_TOKENS hex", "docs/build-plan/10-queue-card-ui.md:118-120 - pill labels are text-fg, worst case 6.61:1"]
    research: { engine: pomera, sources: ["https://webaim.org/articles/contrast/ - WCAG 1.4.3 text 4.5:1, 1.4.11 non-text 3:1", "https://testparty.ai/ - 1.4.11 holds status icons to 3:1"] }
    reasoning: "The pill hue colours only the icon and a 10% fill, and #ea580c (about 3.56:1) and #16a34a (about 3.30:1) on white clear 1.4.11, so the darker palette fixes no failing criterion; adopting it later is an ordinary av-kit change."
    human_message_reference: "USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1'"
  - id: D-91
    stage: execution
    question: "How far does 'decouple anything to do with zorivest' go?"
    resolution: human
    class: two-way
    chosen: "A: remove every dependency and keep the history. AC-41.3 reads the copy; the four canon pointers make av-kit the owner with Zorivest as provenance only; AC-41.3 leaves ENV_BOUND_TESTS; QUEUE-PILL-TOKEN-DRIFT closes with its re-port path overturned; closed plans, handoffs, reflections and decision records stay untouched"
    source_tag: Human-approved
    precedents: ["one runtime read (queue-canon.test.ts:12) and four canon pointers found by the row 0a census", "AGENTS/BUILD_PLAN golden rule 5 - inspiration is intent, not code (against copying every cited source file)"]
    research: { engine: none, sources: [] }
    reasoning: "Fixing only the test would leave the canon saying the palette is whatever the Zorivest checkout declares, so the next Zorivest change would couple av-kit again; a full scrub would copy dozens of source files and erase where patterns came from."
    human_message_reference: "USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1'"
  - id: D-92
    stage: execution
    question: "How does the decoupling reach main?"
    resolution: human
    class: two-way
    chosen: "Amendment A-1 in Session 31b: a new row 0a before the baseline, reviewed by H1-7, proposed at closeout as its own commit ahead of the MEU-71/92 commit; Session 35 picks it up when it merges main"
    source_tag: Human-approved
    precedents: ["Session 37 amendment A-4 - an S8-class baseline failure resolved by a Mat-approved amendment", "Session 39 D-24 - an execution-stage stop resolved by an amendment that added files to Files Modified and the scope allow-list"]
    research: { engine: none, sources: [] }
    reasoning: "A separate mini-session would block 31b for a full plan-and-review cycle on a small change, and carrying AC-41.3 as a baseline failure again would defer what Mat asked for and weaken the gate."
    human_message_reference: "USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1'"
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
  - id: D-94
    stage: execution
    question: "gate71 run 1 failed 1 of 10 AC-71.15 repeats: after Copy prompt the clipboard still held the test's sentinel, because a Windows clipboard listener reacting to the sentinel write held the lock and the copy was dropped silently (stop S8). How is the test fixed?"
    resolution: human
    class: two-way
    chosen: "A: in both AC-71.15 tests the click and the clipboard read run inside expect(...).toPass({ timeout: 10_000 }), so a dropped copy is clicked again; the assertions are unchanged, and test 2's retry also treats an empty read as a lost race"
    source_tag: Human-approved
    precedents: ["ui/tests/e2e/capture-filmstrip-actions.test.ts:188-198 - clipboard listeners lock the clipboard after every write; the test retries until the read settles", "implementation-plan.md S8 - a non-product gate failure stops for a Decision Brief"]
    research: { engine: none, sources: [] }
    reasoning: "A repeated click is a real product write, so retrying replaces a write the OS dropped without weakening the oracle; a broken Copy prompt still times out. Dropping the sentinel would leave test 2 unable to tell a fresh copy from an old clipboard, a read-back retry in the app would change an existing channel outside the plan, and re-running unchanged keeps a 1-in-20 failure in every later gate."
    human_message_reference: "USER_EXPLICIT 2026-10-17 'A'"
  - id: D-95
    stage: execution
    question: "Row 3's green71-main runs example-config.test.ts (AC-71.11), but the plan assigns EXAMPLE_CONFIG to row 4; where is the example written?"
    resolution: autonomous
    class: two-way
    chosen: "Write docs/distribution/mcp.json.example to the EXAMPLE_CONFIG shape in row 3, and leave it unchanged in row 4"
    source_tag: Local Canon
    precedents: ["validate-task.ps1 $mcp71 - green71-main runs entry-guard, entry-spawn, example-config and runtime", "walkthrough §Green, main and server half (row 3) - the sequencing note"]
    research: { engine: none, sources: [] }
    reasoning: "Row 3 could not go green with the old example. The file is documentation with no runtime reader, so moving it one row earlier changes no behaviour, and the alternative (editing the gate's test set) would weaken row 3's check."
  - id: D-96
    stage: execution
    question: "The renderer needs the CLIENT_SET labels for the Client select; does it import them from src/main/mcp-setup-prompt.ts?"
    resolution: autonomous
    class: two-way
    chosen: "The renderer keeps its own MCP_CLIENT_OPTIONS copy of CLIENT_SET; AC-71.13 pins the renderer list and AC-71.1 the main list, both against CLIENT_SET"
    source_tag: Local Canon
    precedents: ["ui/src/main/mcp-setup-prompt.ts imports node:path, which the sandboxed renderer bundle cannot load", "PRODUCT_SCOPE - no new shared module outside the listed files"]
    research: { engine: none, sources: [] }
    reasoning: "Importing main code would pull node:path into the renderer, and a new shared module is outside PRODUCT_SCOPE; two pinned copies cannot drift without a test failing."
  - id: D-99
    stage: execution
    question: "Execution review round 2 was refused on tokens: round 1 used 11,498,809 of the 21M budget, and the ledger reserves one round's actual cost. How large is the execution-review budget?"
    resolution: human
    class: governance-value
    chosen: "A total execution-review budget of 50M: 29M added through tools/review_ledger.py continue, with Mat's sentence as --said"
    source_tag: Human-approved
    precedents: ["walkthrough.md Execution review round 1 - the round-1 cost and the ledger refusal", "tools/review_ledger.py MIN_RATIONALE - a continue needs the owner's own sentence of at least 20 characters"]
    research: { engine: none, sources: [] }
    reasoning: "Round 2 rechecks the blocking F1 fix, so stopping the loop would leave it unreviewed; a smaller raise could refuse round 3 the same way. Round 2 then used 3,825,102 tokens, 15,323,911 in all."
    human_message_reference: "USER_EXPLICIT 2026-10-17 'Approved: raise the execution review budget to 50M total.'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-17 | claude-code-local (Claude Opus 5.5) | Initial MEU-71 handoff after gate71 run 2 |
