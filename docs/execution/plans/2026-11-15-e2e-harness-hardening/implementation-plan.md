---
project: "2026-11-15-e2e-harness-hardening"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 78; issues E2E-MAIN-PROCESS-ERRORS-UNWATCHED, E2E-ELECTRON-LAUNCH-FLAG, UI-ELECTRON-LAZY-INSTALL-RACE and CAPTURE-HINT-TEST-PRESENCE-ONLY"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: one Electron launch helper, a serial binary install and chord-value hint tests

> **Project**: `2026-11-15-e2e-harness-hardening`
> **Build Plan Section(s)**: none. This is test-harness debt with no MEU, as in Session 49b `2026-11-05-closeout-register-grammar` (D-280) and grouping D-815.
> **Status:** said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 3 (.agent/context/handoffs/2026-11-15-e2e-harness-hardening-plan-critical-review.md).

---

## Goal

**Goal anchor:** every Electron E2E launch goes through one helper that drops `ELECTRON_RUN_AS_NODE` from the environment it passes and fails the test when the main process throws an uncaught exception; Vitest installs the Electron binary once, before any worker starts; and Capture's AC-97.4 hint tests fail when the Save or Region chord is wrong.

This is Session 78 of the post-rc.3 grouping (§3, `:164-172`). Order, from the grouping: the launch helper (the flag and the main-process watch together), then the install race, then the hint test.

**`E2E-MAIN-PROCESS-ERRORS-UNWATCHED`** (`known-issues.yaml:3395`, triage D-231). Playwright watches the pages only. A main-process exception shows a modal dialog on the desktop and fails no test. At worst `app.close()` waits on the dialog until the test times out. No product file registers an `uncaughtException` or `unhandledRejection` listener (plan-time `rg` over `ui/src/main`).

**`E2E-ELECTRON-LAUNCH-FLAG`** (`known-issues.yaml:18`).
- **The sites.** The grouping says 14 `_electron.launch()` sites. The plan-time count is **21 sites in 20 files** under `ui/tests/e2e/` (`C:/Temp/av-kit/e2e-harness-hardening/launch-sites.txt`). Every one spreads `...process.env`, and there is no shared helper.
- **The failure.** With `ELECTRON_RUN_AS_NODE=1` (VS Code and Cursor terminals set it per session), `electron.exe` starts as plain Node and rejects Playwright's `--remote-debugging-port=0` (`flag-probe.txt`: `electron.exe: bad option: --remote-debugging-port=0`).
- **The dev symptom.** The issue's widened blast radius adds a second, silent symptom: `npm --prefix ui run dev` never opens a window. That one is not an E2E launch (D-939).

**`UI-ELECTRON-LAZY-INSTALL-RACE`** (`known-issues.yaml:889`).
- **The cause.** The installed `electron` is 42.11.18. The issue was filed against 42.9.3, and the shape is unchanged. Neither has a `postinstall`. `node_modules/electron/index.js:25-52` runs `install.js` with `spawnSync` on the first `require` when `dist/` lacks the binary (`:34-36`, `:40-41`).
- **The race.** After `npm ci` removes the binary, Vitest's parallel workers each start the install and race the extraction.
- **The trigger.** `vitest.config.ts` aliases `electron` to a stub, but `ui/src/main/index.ts:6` imports `electron-store`, which Vitest leaves to Node, and `node_modules/electron-store/index.js:3` runs the real `require('electron')`. Three unit files load `src/main/index` (`g36-csp.test.ts:40`, `persist-ui.test.ts:25,37`, `single-instance.test.ts:5`), so their workers race. Separately, `mcp-spawn-electron.test.ts:16-18` (AC-71.10) reads `node_modules/electron/path.txt` itself. `install.js:94` writes that file, so after `npm ci` AC-71.10 fails on a missing file.
- **What is mitigated.** CI is mitigated by its own serial step (`.github/workflows/ci.yml:95-96`, "Install the Electron binary", after `npm ci --ignore-scripts` at `:93`; the issue's note at `known-issues.yaml:904` still says `:89-96`). A developer machine is not.

**`CAPTURE-HINT-TEST-PRESENCE-ONLY`** (`known-issues.yaml:2883`).
- **The weak test.** `ui/tests/unit/capture-page.test.ts:628` (AC-97.4 HINTS) checks only that the Save and Region shortcut props exist.
- **The issue's probe.** It bound both to `Ctrl+O` and all three checks still held.
- **The fix.** The issue says the fix "is a test change … so it needs approval". This plan gives that change its own named row (D-938, M-7).
- **The live values.** `CapturePage.tsx:2548` (`shortcut="Ctrl+S"`), `:2658` (`aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Enter')}`) and `:2659` (`title="Capture region (Ctrl+Enter)"`). The registry binds `capture:save` to `Ctrl+S` and `page:primary` to `Ctrl+Enter`. The issue's own line numbers `:1362`, `:1441` and `:1442` are stale.

**Teardown (`CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`, `known-issues.yaml:2845`, MONITORING).**
- **What changes.** The helper touches teardown: its `close()` adds a wait of at most 5 s for the process to exit, then reads the watch's error log (D-940).
- **What does not.** The original close runs first and unchanged. The bounded wait never fails by itself.
- **The effect on the hang.** The one known way a close could hang, a main-process error dialog, can no longer appear while the watch is loaded. The issue stays MONITORING, unchanged.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The change is 21 launch calls of one shape in 20 test files, three new helper files, one config line and two hint tests, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern. Receipts go under `C:/Temp/av-kit/e2e-harness-hardening/`, named `ehh-*`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, clears `ELECTRON_RUN_AS_NODE`, and points `TMP` and `TEMP` at `C:\Temp\av-kit\e2e-harness-hardening\tmp`.
  - Vitest runs from pwsh (`npm --prefix ui run test`), never from the Bash tool.
  - Every Electron run goes through `e2e-run.ps1`. It clears the variable (or, for the flag cases, sets it in a child), and stops afterwards only the processes that the run itself launched: `owned-procs.ps1` records the run's own process tree by pid and creation time, admitting a child only when its parent's recorded identity was seen alive at or after the child started and no other process was seen holding that pid in between, so a pid that an unrelated process reused never passes ownership on, even after that process exits; it stops a recorded process only when it is still alive, runs this checkout's `ui/node_modules/electron/dist` binary and started after the script did (AC-10). It never stops a process by name or by path alone, because other av-kit worktrees, other sessions and Mat's own app may be running, even from this checkout's binary.
  - No row starts the dev app. If an executor wants a manual look, it starts the app detached with `Start-Process -PassThru` and stops only that recorded process id.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local only. The grouping §3 says "local (Electron E2E)", and the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `ehh-plan-2026-11-15-e2e-harness-hardening` and `ehh-execution-2026-11-15-e2e-harness-hardening`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Session 87 runs and is committed first. Sessions 75, 76 and 77 run before this one, and Mat has not said whether each is committed after it closes. Their changes may therefore be uncommitted when this session starts. Baselines and scope checks are path-scoped and bound to content (§Verification Plan 1). Session 74 (MEU-144) is outside this run. Execution waits for Mat's message (`plan_to_exec_gate: human`).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.
- **Human checks (M-10):** none. Every AC is checked by a command, so the plan has no human-check row.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| All four issues (no MEU) | `.agent/context/handoffs/2026-11-15-e2e-harness-hardening-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-e2e-harness-hardening-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-e2e-harness-hardening-implementation-critical-review.md`

The session has one handoff, following the no-MEU precedent `2026-11-05-closeout-register-grammar-handoff.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `base-e2e-count.txt`, the BASE copies, `ehh-base-ui.txt`, `ehh-base-e2e.txt`, `ehh-base-flag.txt` |
| WP-2 | The launch helper: Red, then Green (rows 1 to 3) | WP-1 | shared | `electron-env.ts`, `electron-app.ts`, `main-error-watch.cjs`, `electron-harness.test.ts`, `ui/tests/unit/e2e-harness.test.ts` |
| WP-3 | The site migration: Red, then Green, then the whole watched suite (rows 4 to 6) | WP-2 | shared | The 20 site files, `ui/tests/unit/layout-primitives.test.ts`, `ehh-e2e-full.txt`, `ehh-e2e-flag.txt` |
| WP-4 | The install race: Red, then Green (rows 7 and 8) | WP-3 | shared | `ui/tests/unit/global-setup.ts`, `ui/tests/unit/vitest-global-setup.test.ts`, `ui/vitest.config.ts` |
| WP-5 | The hint tests: the mutant proof, Red on the mutant, then Green (rows 9 to 11) | WP-4 | shared | `capture-page.test.ts`, `capture-page.behavior.test.ts`, the mutation receipts |
| WP-6 | The register and the grouping row (row 12) | WP-5 | shared | `known-issues.yaml` and `.md`, grouping §6 row 78 |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.**
>
> - **Two choices had no settled answer in the files:** D-937 and D-939, the briefs at the end of §Decision Log. Each has only an M-6 hit, so your 2026-11-15 hand-over for this grouping covers it, and each is recorded as the agent's choice. One line from you overturns either.
> - **No spec is skipped or marked as expected to fail** (M-11).
> - **If the new watch catches a real main-process error in a passing spec,** the executor registers it as a new issue and stops, with a brief for you (D-936). It does not fix product code in this session.
>
> **What changes for you:**
>
> - **The flag.** `npm --prefix ui run test:e2e` works from a VS Code or Cursor terminal without `$env:ELECTRON_RUN_AS_NODE=$null` first.
> - **Main-process exceptions.** An uncaught exception in the main process now fails the E2E test that caused it, with the stack in the failure. It no longer shows a dialog on the desktop during a run.
> - **The install race.** `npm --prefix ui run test` straight after `npm ci` installs the Electron binary once, then starts the workers. When the install cannot finish (for example, offline), the run stops at once and names the command to run (D-937).
> - **The hint tests.** Capture's AC-97.4 hint tests fail when Save is not bound to the registry's `capture:save` chord or Region to `page:primary`.
> - **The dev symptom.** `npm --prefix ui run dev` behaves as before: it still needs the variable cleared. That symptom gets its own issue (D-939).
>
> **What this plan leaves out:**
>
> - fixing product code that the watch catches;
> - watching unhandled promise rejections in the main process (registered as a new issue, D-935);
> - timing instrumentation for the teardown hang;
> - a `postinstall` script;
> - changing `npm run dev` (§Out of Scope).

## Proposed Changes

### Single-statement contracts

- **`ENV_DROP_FLAG` (D-933, D-934):** `electronEnv(base = process.env, extra = {})` in `ui/tests/e2e/electron-env.ts` works in this order:
  1. copies `base` (never mutating it);
  2. sets `AVKIT_E2E: '1'`;
  3. merges `extra`;
  4. deletes `ELECTRON_RUN_AS_NODE` after the merge;
  5. drops every key whose value is `undefined`.
- **`ONE_LAUNCH_PATH` (D-933):** `launchElectron({ main?, env? } = {})` in `ui/tests/e2e/electron-app.ts` is the only `_electron.launch(` call under `ui/tests/e2e/`.
  - It passes `args: ['-r', MAIN_ERROR_WATCH, main ?? DEFAULT_MAIN]`, where `DEFAULT_MAIN = resolve(here, '../../out/main/index.js')`.
  - It first calls `requireScratchAppData(env)` (`SCRATCH_PROFILE`), so it never launches without a scratch profile.
  - It makes a folder `mkdtempSync(join(tmpdir(), 'avkit-e2e-main-'))` for each launch (the rows point `TMP` at `R/tmp`) and passes `env: electronEnv(process.env, { ...env, [MAIN_ERROR_LOG_ENV]: log })`, where `log` is `errors.jsonl` in that folder. If `_electron.launch` rejects, it removes the folder and rethrows the same error.
  - It returns the same `ElectronApplication` object, with `close` wrapped (`CLOSE_CHECK`).
  - No other file in `ui/tests/e2e/` names `_electron`.
- **`MAIN_ERROR_WATCH` (D-935):** `ui/tests/e2e/main-error-watch.cjs` is preloaded into the main process with `-r`.
  - It starts with `/* global process */` and loads `fs` through `process.getBuiltinModule('node:fs')`, because the lint refuses `require` in `.cjs` files (`probe/eslint-cjs.txt`).
  - It reads the log path from `AVKIT_E2E_MAIN_ERROR_LOG` (`MAIN_ERROR_LOG_ENV`), deletes that variable from `process.env`, so the app and its children never see it, and creates the file empty. The file is the error channel from the preload's start until the process exits.
  - It sets `globalThis.__avkitE2eMainErrorWatch = true` and `globalThis.__avkitE2eMainErrors = []`.
  - It registers one `process.on('uncaughtException', …)` listener. That listener pushes the error, appends one JSON line `{ name, message, stack }` (each a string; `stack` is the full `error.stack`, or `String(error)` for a non-error) to the log with `appendFileSync`, and writes `MAIN_ERROR_MARKER + ' ' + stack + '\n'` to stderr for a human reading the output. No check reads stderr.
  - `MAIN_ERROR_MARKER` is `[avkit-e2e-main-error]`, exported from `electron-env.ts`. The listener stops Electron's error dialog, and the process keeps running.
- **`SCRATCH_PROFILE` (D-933; round-1 review R1-F4):** `requireScratchAppData(env)` in `electron-env.ts` returns `env.AVKIT_APP_DATA` when it is a non-empty string whose resolved path lies inside `tmpdir()` (`path.relative(resolve(tmpdir()), resolve(value))` is not empty, does not start with `..` and is not absolute). Otherwise it throws `Error('launchElectron needs a scratch AVKIT_APP_DATA under tmpdir(): ' + String(value))`.
  - `launchElectron` calls it on the caller's own `env`, never on `process.env`, before it makes the log folder or calls `_electron.launch`. A refused call starts no process and leaves nothing to remove.
  - Why: without the override the app uses the normal profile, `LOCALAPPDATA/av-kit` (`ui/src/main/index.ts:149`). Boot creates that folder and its MCP token there (`:221`), and when the profile's backend descriptor names a live backend on this binary, it reaps that backend (`:258-260`, `live-identity.ts:74`). A fresh folder holds no descriptor, so boot spawns its own backend and signals none (`live-identity.ts:47-49`).
  - With the override, main sets `userData` to that folder (`index.ts:223`), and Electron's `sessionData` follows `userData` (`probe/sessiondata-result.txt`).
  - Every site of the row-0 content already passes one: 21 sites in 20 files at plan time, each `mkdtempSync(join(tmpdir(), 'avkit-e2e-…'))` directly or through `launchWithAppData(dir)` with such a folder (`settings.test.ts:779`; `probe/app-data-sites.txt`). `SITE_MIGRATION` keeps those keys as they are. If a row-0 site passes none, row 5 stops (S3) and adds none.
  - A refusal is a harness rule, not a product error, so `NEW_FAILURE_RULE` does not apply to it. It touches no teardown.
- **`CLOSE_CHECK` (D-935, D-940):** the log, not stderr, carries the errors. Playwright starts reading the app's stderr at spawn (`coreBundle.js:10064`) and runs main before `launch()` returns (`:45780`), so a stderr listener added after launch misses a throw during startup (round-1 review R1-F1). The wrapped `close()` is memoized, so a second call returns the same promise, and works in this order:
  1. awaits the original `close()`;
  2. waits at most 5 s for the process to exit, returning at once when `exitCode` or `signalCode` is already set (the timeout never fails by itself);
  3. reads the log; a missing log throws `Error('main-error watch never started: ' + log)`;
  4. parses it with `mainErrorRecords(text)` and removes the folder in a `finally`;
  5. throws `Error('main-process uncaught exception(s):\n' + records.map((r) => r.stack ?? r.raw).join('\n---\n'))` when there is any record, so the message holds each full stack with its `at` frames for `NEW_FAILURE_RULE`.

  `mainErrorRecords(text)` returns, in order, one entry per non-empty line: the parsed record, or `{ raw: line }` when the line is not a JSON object with a string `stack`. Nothing is dropped.
- **`SITE_MIGRATION` (D-934):** each site in the row-0 content (21 in 20 files at plan time; `baseline-sites.json` records the live count) becomes `launchElectron({ … })` with only the keys `main` and `env`, in the same order as BASE.
  - `main` is absent when BASE passed `DEFAULT_ARGS`, the default main entry `args: [resolve(here, '../../out/main/index.js')]`, compared with whitespace removed (`site-check.py:36`). Otherwise it is BASE's single `args` element.
  - `env` is BASE's `env` without `...process.env` and `AVKIT_E2E: '1'`, and is absent when nothing is left.
  - `theme-probe.ts` still exports `launchWithAppData`.
  - The capture-picker stub `spawn` keeps its own `...process.env` (it is not an Electron launch).
- **`NEW_FAILURE_RULE` (D-936):** a spec that fails only because `CLOSE_CHECK` threw is handled by the cause in its stack:
  - a defect in the three new helper files is fixed;
  - a stack in product code is registered with `issue_triage.py add`, then the executor stops with a brief for Mat (S5);
  - a spec that throws in main on purpose also stops for Mat (S5).
  No spec is skipped, marked `fixme` or as expected to fail, or put on an allow-list (M-11).
- **`INSTALL_ONCE` (D-937):** `ui/tests/unit/global-setup.ts` exports `ensureElectronBinary(requireFn = createRequire(import.meta.url), exists = existsSync): string`.
  - It calls `requireFn('electron')`, which runs `install.js` once, serially, when the binary is missing.
  - It throws an error naming `node node_modules/electron/install.js` when that `require` throws or the returned path does not exist. Otherwise it returns the path.
  - Its `export default function setup(project: TestProject): void` takes Vitest's project argument (Vitest calls `setup?.(project)`, `vitest/dist/chunks/index.1TqnEahn.js:6567`) and returns nothing. Vitest 5.0.5 throws `invalid return value in globalSetup file … Must return a function` on any other non-null return (`:6569`).
  - `setup` calls `ensureElectronBinary()` with no arguments, so the project never becomes `requireFn`, and then calls `project.provide('electronBinary', path)`.
  - The file declares `declare module 'vitest' { export interface ProvidedContext { electronBinary: string } }`, so `inject('electronBinary')` is typed.
  - `ui/vitest.config.ts` gains `globalSetup: ['./tests/unit/global-setup.ts']` and keeps its CRLF.
  - `createRequire` bypasses the config's `electron` alias, which only Vite's resolver applies. The setup file itself loads through Vite's module runner, so a plain `import 'electron'` there would get the stub.
  - No test reproduces the race by moving `ui/node_modules/electron` aside, because other sessions share that tree.
- **`HINT_VALUES` (D-938):** capture-page.test.ts's AC-97.4 HINTS test compares the source props with `chordOf('capture:save')` and `chordOf('page:primary')`. A new behavior test checks the rendered `capture-save` and `capture-region` buttons with `expectBoundHint`.

### The helper files

| File | Line endings | Exports or role |
|---|---|---|
| `ui/tests/e2e/electron-env.ts` | LF, new | `MAIN_ERROR_MARKER`, `MAIN_ERROR_LOG_ENV` (`'AVKIT_E2E_MAIN_ERROR_LOG'`), `MAIN_ERROR_WATCH` (`resolve(here, 'main-error-watch.cjs')`), `electronEnv`, `mainErrorRecords`, `requireScratchAppData` |
| `ui/tests/e2e/main-error-watch.cjs` | LF, new | `MAIN_ERROR_WATCH`. `.cjs` because `ui/package.json` is `"type": "module"` and `-r` loads CommonJS |
| `ui/tests/e2e/electron-app.ts` | LF, new | `DEFAULT_MAIN`, `launchElectron` |
| `ui/tests/e2e/electron-harness.test.ts` | LF, new | AC-5 to AC-8, five tests (AC-7 has an after-launch and a during-startup case). Each test launches with its own fresh `AVKIT_APP_DATA`, `mkdtempSync(join(tmpdir(), 'avkit-e2e-harness-'))`, and checks its profile paths (AC-19). The file never holds the text `electron.launch`, which `red-check.py` reads as a launch failure |
| `ui/tests/e2e/fixtures/startup-throw-main.mjs` | LF, new | AC-7's startup main: `/* global process */`; it reads `process.env.AVKIT_APP_DATA`, and when that is unset or empty writes `startup-throw-main: AVKIT_APP_DATA is not set` to stderr and calls `process.exit(3)` before ready; otherwise, before ready, `app.setPath('userData', join(appData, 'user-data'))` and `app.setPath('sessionData', join(appData, 'session-data'))`, so its profile and session storage stay in the test's scratch folder; then `process.nextTick(() => { throw new Error('avkit-e2e-startup-probe') })` at load; on `app.whenReady()` a hidden `BrowserWindow` loads `about:blank`; `window-all-closed` quits. It never quits by itself and uses no timer (`probe/startup-fixture2.mjs` lints clean, `probe/eslint-fixture2.txt`; the probe main's `setTimeout` fails `no-undef`, `probe/eslint-cjs2.txt`) |

- **What Playwright collects.** Its config (`testDir: './tests/e2e'`, `testMatch: ['*.test.ts', '*.spec.ts']`) collects `electron-harness.test.ts` and none of the helpers or the `.mjs` fixture.
- **What Vitest collects.** Its `include` covers `tests/unit/**/*.test.{ts,tsx}`, so it collects `e2e-harness.test.ts` and `vitest-global-setup.test.ts`, and never `tests/e2e/`.
- **The plan-time probe** (`probe/probe-result.txt`) ran the watch as a second `-r` after a first preload, in Playwright's order:
  - the watch loaded before main (`listeners=2`);
  - a thrown error printed the marker line;
  - the process kept running.
- **The startup probe** (`probe/startup-result.txt`, with `probe/startup.mjs` and `probe/watch2.cjs`, the planned watch) ran an ESM main that throws on its first tick, in Playwright's preload order:
  - the log file held one full JSON record whose stack names `startup.mjs` with its frames;
  - the main saw no `AVKIT_E2E_MAIN_ERROR_LOG`;
  - the window still loaded and the process exited 0.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| The environment of each launched E2E app | `ui/tests/e2e/electron-env.ts` | `AVKIT_E2E` is `'1'`; `ELECTRON_RUN_AS_NODE` is never set; `AVKIT_APP_DATA` is the caller's own folder inside `tmpdir()` (`SCRATCH_PROFILE`); the site's own keys are unchanged | The site's keys pass through |
| The main-process error log in E2E (`AVKIT_E2E_MAIN_ERROR_LOG`, one file per launch) | `ui/tests/e2e/main-error-watch.cjs` | Created empty at preload start; one JSON line `{ name, message, stack }` per uncaught exception until exit | Other fields are ignored; a line that is not a record is kept as `{ raw }`. Stderr is not read |
| Vitest start-up | `ui/tests/unit/global-setup.ts` | Returns the binary's path or throws before any worker starts | — |

No product file changes. Nothing changes in any API route, OpenAPI document, MCP tool shape, database schema or `ui/src` file. `CapturePage.tsx` is changed only inside rows 9 and 10, as a temporary mutant, and `mutation.py` restores its bytes and mtime there.

### Acceptance Criteria

- **Unit names.** The new Vitest tests are named `AC-<n> …` inside `describe('Session 78 E2E harness')`, and the Playwright tests are named `AC-<n> …`. `red-check.py --require AC-<n>` matches each exactly (`AC-1` never matches `AC-10`).
- **New modules fail by assertion.** A test of a module that does not exist yet first asserts `existsSync(path)`, then loads it with `await import(/* @vite-ignore */ pathToFileURL(path).href)`. Red therefore fails by assertion, never by an import error at collection (Session 52 RULE-4).
- **Changed existing assertions are named rows** (M-7):
  - AC-11 changes `ui/tests/unit/layout-primitives.test.ts:232` (row 4);
  - AC-14 changes `ui/tests/unit/capture-page.test.ts:628-639` (row 10).
  No other existing assertion changes.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | unit | `electronEnv({ ELECTRON_RUN_AS_NODE: '1', KEEP: 'k', GONE: undefined }, { ELECTRON_RUN_AS_NODE: '1', EXTRA: 'e' })`: <br>• has no `ELECTRON_RUN_AS_NODE`; <br>• has `AVKIT_E2E` `'1'`, `KEEP` `'k'` and `EXTRA` `'e'`; <br>• has no `GONE` key; <br>• leaves its base object deep-equal to a copy taken before the call. | Local Canon (`E2E-ELECTRON-LAUNCH-FLAG` blast_radius "delete ELECTRON_RUN_AS_NODE at the launch helper"; D-933, D-934) | The base-object check, and the variable passed in `extra` |
| AC-2 | unit (source) | Over every `.ts` and `.cjs` file in `ui/tests/e2e/`: <br>• only `electron-app.ts` holds `_electron`, and it holds exactly one `_electron.launch(`; <br>• `electron-env.ts` holds `...process.env` no more than once. <br>The per-file `...process.env` count is checked against the row-0 BASE copies by AC-9 rule 4, not by a fixed number here, so a sibling's appended spec cannot make it false-fail. | Local Canon (D-933; the issue's notes: "about 20 sites … with no shared helper") | Today 21 sites in 20 files (`launch-sites.txt`) |
| AC-3 | unit (subprocess) | In a `mkdtempSync` folder, `thrower.cjs` writes `String(process.env[MAIN_ERROR_LOG_ENV] === undefined)` to stdout, throws `Error('avkit-ac3-probe')` inside a `setTimeout`, and writes `alive` 50 ms later. Then: <br>• `spawnSync(process.execPath, [thrower])` exits non-zero and never prints `alive`; <br>• `spawnSync(process.execPath, ['-r', MAIN_ERROR_WATCH, thrower])` with `{ ...process.env, [MAIN_ERROR_LOG_ENV]: log }` exits 0, prints `true` and `alive`, and its stderr holds `[avkit-e2e-main-error]`; <br>• the log has exactly one line, and `JSON.parse` of it has `message` `'avkit-ac3-probe'` and a `stack` holding `thrower.cjs` and a `\n    at ` frame. <br>The folder is removed in a `finally`. | Research-backed (Node `process` `'uncaughtException'` docs: a listener replaces the default exit; `probe/probe-result.txt`, `probe/startup-result.txt`; D-935) | The run without the watch; a record without the thrower's frame |
| AC-4 | unit | `mainErrorRecords` on a text of two JSON records whose stacks span several lines (`Error: a\n    at f (x.js:1:1)\n    at g (y.js:2:2)`), one blank line and one line `not json`, returns three entries in order: the two records with `stack` unchanged, frames included, and `{ raw: 'not json' }`. On `''` it returns `[]`. | Local Canon (D-935; round-1 review R1-F3) | The blank and the malformed line |
| AC-5 | E2E | With `process.env.ELECTRON_RUN_AS_NODE = '1'` set in the worker (restored in a `finally`), `launchElectron({ env: { AVKIT_APP_DATA: <a fresh folder> } })` starts the app, the first window loads, and `app.evaluate(() => process.env.ELECTRON_RUN_AS_NODE)` is `undefined`. | Local Canon (`E2E-ELECTRON-LAUNCH-FLAG`; D-933) | BASE `launch.test.ts` under the flag fails with `bad option` (row 0, `ehh-base-flag.txt`) |
| AC-6 | E2E | In the launched main process, `globalThis.__avkitE2eMainErrorWatch` is `true` and `process.listenerCount('uncaughtException')` is at least 2 before any test action, so the watch loaded before main. | Research-backed (Playwright `_electron.launch` prepends its own `-r` loader; a second `-r` runs after it, `probe/probe-result.txt`; D-935) | — |
| AC-7 | E2E (two tests) | **After launch** (`AC-7 after launch …`): after `app.evaluate(() => { setTimeout(() => { throw new Error('avkit-e2e-probe') }) })`, `expect.poll` reads one entry in `__avkitE2eMainErrors`, and `const error = await app.close().then(() => null, (e: unknown) => e)` is an `Error` whose message matches `/avkit-e2e-probe/` and `/\n\s+at /`. <br>**During startup** (`AC-7 during startup …`): `launchElectron({ main: resolve(here, 'fixtures/startup-throw-main.mjs'), env: { AVKIT_APP_DATA: <a fresh folder> } })`, whose main throws before `launch()` resolves, still gives a first window (`await app.firstWindow()` resolves); then `app.close()` rejects with a message holding `avkit-e2e-startup-probe` and `startup-throw-main.mjs`. | Local Canon (`E2E-MAIN-PROCESS-ERRORS-UNWATCHED` root_cause; D-935; round-1 review R1-F1, R1-F3) | Today nothing fails and a dialog opens. A stderr listener added after launch lets the startup case's close resolve (R1-F1) |
| AC-8 | E2E | A launch with no main-process error closes with `await app.close()` resolving, within the test's normal timeout. | Local Canon (D-940) | AC-7 |
| AC-9 | site check | `site-check.py` exits 0. It checks rules 1 to 6 against the BASE copies: <br>1. one launch path; <br>2. the call count and order; <br>3. only `main` and `env`, with the values derived from BASE; <br>4. the `...process.env` count; <br>5. line endings kept; <br>6. `launchWithAppData` still exported. <br>`site-check.py --selftest` passes 13 of 13. Every rule reads the BASE copies of the row-0 content, never `HEAD`. | Local Canon (D-934) | The selftest's failing fixtures |
| AC-10 | E2E (suite) | The whole Electron suite, with `ELECTRON_RUN_AS_NODE` unset, exits 0 with at least `base-e2e-count.txt` + 5 passed and no failed, flaky, not-run or interrupted line. Every spec now runs under the watch. <br>**Process ownership.** Every Electron run of this plan (row 0, rows 2, 3 and 6, the gate) stops afterwards only the processes that the run itself launched: `owned-procs.ps1` records the run's own process tree by pid and creation time, admitting a child only when its parent's recorded identity was seen alive at or after the child started and no other process was seen holding that pid in between, so a pid that an unrelated process reused never passes ownership on, even after that process exits; it stops a recorded process only when it is still alive, runs this checkout's `ui/node_modules/electron/dist` binary and started after the script did. An Electron app that Mat or another session starts during the run, even from this checkout's binary, is never stopped. The stop never goes by pid alone: for each candidate it opens the pid and holds that handle, which keeps the pid from being reused, checks through the same object that `StartTime` is the recorded creation time at CIM's whole-microsecond resolution (both truncated to 10 ticks, then equal; `probe/ctime-res.txt`), and kills only that object with `Kill($false)`, never its tree. A candidate that has exited or cannot be read at the open, the start time or the kill, or whose pid now names another process, is listed as not stopped, and so is a process that is not proven the run's own. `owned-procs.ps1 -Selftest` passes 26 of 26, in row 6 and in the gate. | Local Canon (D-936, D-941; the session brief: other worktrees and apps may run; round-1 review R1-F2) | Row 0's base count. The selftest's unrelated same-path process started during the run is excluded, and its case for the old path-and-time rule shows that rule would stop it. In the selftest's four snapshots, owned 105 exits, an unrelated process reuses pid 105 and starts 106, and the reuser exits: 106 stays unowned, and the round-1 rule, which looked for a reuser in the current snapshot only, would own it (round-1 recorded review R1-F2). At the stop, a pid that now names a replacement started later is refused without a kill, and the selftest's pid-only stop kills that replacement (round-2 recorded review R2-F1) |
| AC-11 | unit (named change) | `layout-primitives.test.ts` `AC-51.7 wires a fresh, allowlisted real Electron harness …`: <br>• `:232` `expect(e2e).toContain('_electron.launch')` becomes `expect(e2e).toContain('launchElectron(')`; <br>• a new line adds `expect(readFileSync(resolve(ui, 'tests/e2e/electron-app.ts'), 'utf8')).toContain('_electron.launch')`. <br>The test's other assertions are unchanged. | Local Canon (D-933; M-7 named row 4) | Red at row 4: the BASE `layout-primitives.test.ts` E2E file holds no `launchElectron(` |
| AC-12 | unit | `ensureElectronBinary`, with injected functions: <br>• a `requireFn` returning a path for which `exists` is true returns that path; <br>• a `requireFn` that throws makes it throw a message holding `node node_modules/electron/install.js`; <br>• a path for which `exists` is false throws the same message; <br>• `ui/vitest.config.ts` holds `globalSetup: ['./tests/unit/global-setup.ts']`; <br>• the default export, called with a fake project `{ provide }` that records its calls, returns `undefined` (Vitest throws on any other non-null value); <br>• that call makes exactly one `provide('electronBinary', p)` call, where `p` exists under `ui/node_modules/electron/dist/`. A setup that passed the fake project on as `requireFn` would throw the install message instead. | Research-backed (`node_modules/electron/index.js:25-52`; Vitest 5.0.5 `index.1TqnEahn.js:6567-6569`; D-937, handed to the agent) | The two throwing cases. A setup that returns the path, or passes the project on, fails the last two |
| AC-13 | unit | `inject('electronBinary')` is a string naming a path that exists, under `ui/node_modules/electron/dist/`. This proves that the global setup ran in this same run and handed its path to the worker. | Research-backed (D-937, handed to the agent) | Red: no global setup is wired, so `inject` returns `undefined` (the `typeof` assertion) |
| AC-14 | unit (named change) | `capture-page.test.ts` `AC-97.4 HINTS capture-save passes its chord to ToolbarIconButton and capture-region carries its own`: <br>• the `region` slice ends at `page.indexOf('onClick=', regionAt)`; <br>• ``expect(save).toContain(`shortcut="${chordOf('capture:save')}"`)``; <br>• ``expect(region).toContain(`aria-keyshortcuts={ariaKeyshortcuts('${chordOf('page:primary')}')}`)``; <br>• ``expect(region).toContain(`title="Capture region (${chordOf('page:primary')})"`)``; <br>• `import { chordOf } from './helpers/bound-hint'`. <br>The `saveAt` and `regionAt` checks stay. | Local Canon (`CAPTURE-HINT-TEST-PRESENCE-ONLY` blast_radius "assert the rendered values against getCommand(...).shortcut"; D-938; M-7 named row 10) | Red on the mutant (row 10) |
| AC-15 | unit (new) | `capture-page.behavior.test.ts` `AC-97.4 HINTS rendered capture-save and capture-region carry the registry chords`, appended as the last `it` of `describe('MEU-39 capture GUI runtime (exec r1 F1 F2 F5)')` (`:190`). It does `openSelectedSurface()`, then `drag(surface, 25, 25, 150, 150)`, so Save mounts. Then: <br>• `expectBoundHint(screen.getByTestId('capture-save'), 'capture:save', focusedHint(toolbarFocusTarget('capture-save'), 'capture-save-hint') ?? '')`; <br>• `expectBoundHint(screen.getByTestId('capture-region'), 'page:primary')`. <br>It imports `expectBoundHint` from `./helpers/bound-hint`. | Local Canon (D-938; `bound-hint.ts`, the AC-97.4 pattern of the other pages) | Red on the mutant (row 10) |
| AC-16 | mutation proof | On the `mutation.py` mutant (Save `Ctrl+O`, Region aria and title `Ctrl+O`): <br>• the BASE AC-97.4 test passes (row 9, which shows the weakness); <br>• AC-14 and AC-15 fail by assertion (row 10, `red-check.py`). <br>After each row, `mutation.py restore` brings back `CapturePage.tsx`'s SHA-256 and mtime, and `mutation.py status` exits 0. | Local Canon (the issue's verification probe; D-938) | Row 9 is the negative |
| AC-17 | register | <br>• The four issues are `resolved` through `issue-resolve.py`, bound to the register hash of row 0 (or of the D-936 rebind). <br>• `issue_triage.py add` registers `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT` (low, ui; D-939) and `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED` (low, ui; D-935). <br>• `render` and `render --check` exit 0, and the register stays LF. <br>• `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` is unchanged. <br>• Grouping §6 row 78 says `executed (Session 78)` with this plan folder. | Local Canon (`issue-triage.md` §Closing; D-935, D-939, D-940) | `issue-resolve.py` refuses a register whose hash moved (S4) |
| AC-18 | E2E (flag) | With `ELECTRON_RUN_AS_NODE=1` in the shell, `launch.test.ts` and `electron-harness.test.ts` pass and no receipt line holds `bad option`. | Local Canon (`E2E-ELECTRON-LAUNCH-FLAG` root_cause; D-933) | Row 0's BASE run of `launch.test.ts` under the flag exits non-zero with `bad option` (`ehh-base-flag.txt`) |
| AC-19 | unit and E2E | **Unit** (`AC-19 …` in `e2e-harness.test.ts`): `requireScratchAppData` <br>• returns `join(tmpdir(), 'avkit-ac19')` unchanged; <br>• throws a message holding `scratch AVKIT_APP_DATA` for `{}`, for `{ AVKIT_APP_DATA: '' }`, for `{ AVKIT_APP_DATA: tmpdir() }` (the temp folder itself) and for `{ AVKIT_APP_DATA: resolve(tmpdir(), '..', 'av-kit-ac19') }`; <br>• `electron-app.ts` holds `requireScratchAppData(env` once, before its first `_electron.launch(`. <br>**E2E** (inside each of the five tests of `electron-harness.test.ts`): each test launches with its own fresh `AVKIT_APP_DATA` folder, and before its close `app.evaluate(({ app }) => [app.getPath('userData'), app.getPath('sessionData')])` returns that folder twice; in the startup case it returns `join(folder, 'user-data')` and `join(folder, 'session-data')`. So no new harness case selects the normal profile, and none can reap a backend it did not launch. | Local Canon (round-1 review R1-F4; `ui/src/main/index.ts:149`, `:221`, `:223`, `:258-260`; `live-identity.ts:47-49`, `:74`; D-933) | Row 1's Red: `electron-env.ts` does not exist. The refusals are the negatives: without them, `launchElectron()` with no env would select the normal profile |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Where the launch helper lives and what it owns | Local Canon | `ui/tests/e2e/electron-app.ts` and `electron-env.ts`, the only launch path (D-933) |
| How the flag leaves the environment | Local Canon | Deleted after the merge; no allow-list (D-934) |
| How a main-process exception reaches the test | Research-backed | A `-r` preload listener that appends each full error record to a per-launch log, which `close()` reads after the exit (D-935) |
| Which app profile a harness launch may use | Local Canon | A fresh scratch `AVKIT_APP_DATA` inside `tmpdir()`, refused otherwise (`SCRATCH_PROFILE`, AC-19) |
| Which processes a run may stop | Local Canon | Only its own recorded process tree on this checkout's binary (`owned-procs.ps1`, AC-10) |
| What happens to a spec the watch newly fails | Local Canon | `NEW_FAILURE_RULE`; never skipped (D-936) |
| How the binary is installed once | Research-backed (handed to the agent) | A Vitest `globalSetup` (D-937) |
| How the hint tests check the chord | Local Canon | Against `chordOf`, in source and rendered (D-938) |
| What happens to the `npm run dev` symptom | Local Canon (handed to the agent) | A new issue; the flag issue is resolved for E2E (D-939) |
| Whether teardown changes | Local Canon | Bounded wait plus the check; no instrumentation (D-940) |
| Which gate steps run | Local Canon | §Session gate (D-941) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `ui/tests/e2e/electron-env.ts` | new | LF | `ENV_DROP_FLAG`, `SCRATCH_PROFILE`, `MAIN_ERROR_MARKER`, `MAIN_ERROR_LOG_ENV`, `MAIN_ERROR_WATCH`, `mainErrorRecords` |
| `ui/tests/e2e/electron-app.ts` | new | LF | `ONE_LAUNCH_PATH` (calls `requireScratchAppData` first), `CLOSE_CHECK` |
| `ui/tests/e2e/main-error-watch.cjs` | new | LF | `MAIN_ERROR_WATCH` |
| `ui/tests/e2e/electron-harness.test.ts` | new | LF | AC-5 to AC-8 (five tests), each with AC-19's profile check |
| `ui/tests/e2e/fixtures/startup-throw-main.mjs` | new | LF | AC-7's startup main, with its profile in the scratch folder (AC-19) |
| `ui/tests/unit/e2e-harness.test.ts` | new | LF | AC-1 to AC-4 |
| `ui/tests/unit/global-setup.ts` | new | LF | `INSTALL_ONCE` |
| `ui/tests/unit/vitest-global-setup.test.ts` | new | LF | AC-12, AC-13 |
| `ui/vitest.config.ts` | modify | CRLF, kept | One `globalSetup` line |
| `ui/tests/e2e/capture-filmstrip-actions.test.ts`, `console-chrome.test.ts`, `mcp-setup-prompt.test.ts`, `settings.test.ts`, `startup-reveal.test.ts`, `theme-probe.ts`, `tts-generate.test.ts` | modify | CRLF, kept | `SITE_MIGRATION` |
| `ui/tests/e2e/backend-output-after-close.test.ts`, `capture-import.test.ts`, `capture-inbox.test.ts` (2 sites), `capture-picker.test.ts`, `command-palette-nav.spec.ts`, `console-panel.test.ts`, `convert-queue.test.ts`, `download-queue.test.ts`, `help-search.spec.ts`, `keyboard-shortcuts.test.ts`, `launch.test.ts`, `layout-primitives.test.ts`, `transcript-queue.test.ts` | modify | LF, kept | `SITE_MIGRATION` |
| `ui/tests/unit/layout-primitives.test.ts` | modify | CRLF, kept | AC-11, the named change to AC-51.7 |
| `ui/tests/unit/capture-page.test.ts` | modify | CRLF, kept | AC-14, the named change to AC-97.4 HINTS, and the `chordOf` import |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | CRLF, kept | AC-15 appended, and the `expectBoundHint` import |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | none (temporary mutant) | CRLF | Changed only inside rows 9 and 10 by `mutation.py` and restored to its row-0 SHA-256 and mtime; never in the diff |
| `.agent/context/known-issues.yaml` | modify (tool) | LF, kept | Four issues resolved through `issue-resolve.py`; two added through `issue_triage.py add` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modify | LF, kept | §6 row 78 only: `executed (Session 78)` and this plan folder |

**Sizes and line endings.** They were measured with Python bytes at `HEAD` `6aaf9b0` (`line-endings.txt`).

- **CRLF e2e files:** capture-filmstrip-actions 17,709 bytes, console-chrome 10,587, mcp-setup-prompt 8,369, settings 41,530, startup-reveal 2,581, theme-probe 9,295, tts-generate 42,907.
- **LF e2e files:** backend-output-after-close 1,874, capture-import 15,459, capture-inbox 175,468, capture-picker 9,262, command-palette-nav.spec 1,740, console-panel 2,087, convert-queue 71,730, download-queue 75,897, help-search.spec 2,433, keyboard-shortcuts 4,344, launch 1,925, layout-primitives 3,974, transcript-queue 28,431.
- **CRLF unit files and config:** unit `layout-primitives.test.ts` 20,110, `capture-page.test.ts` 29,260, `capture-page.behavior.test.ts` 195,766, `vitest.config.ts` 481.
- **The rest:** `CapturePage.tsx` 109,704 (CRLF); `known-issues.yaml` 455,210 (LF); the grouping 31,451 (LF).

A CRLF file is read and written with `newline=""` from CRLF text. `site-check.py` rule 5 and the gate check the endings again.

### Project files

- **Plan-local scripts**, all in this plan folder (LF):
  - `baseline.ps1`;
  - `red-check.py`, copied from `2026-11-15-framework-small-syncs` with this plan's `DECLARED_NEW` (`electron-env`, `electron-app`, `main-error-watch`, `global-setup`);
  - `identity.py`, the same copy with this plan's `PLAN`;
  - `issue-resolve.py`, copied from `2026-11-15-closeout-record-once` with `SCRATCH` at `C:/Temp/av-kit/e2e-harness-hardening`; it has no selftest;
  - `untouched-check.py`, the content-bound skip basis (`--record`, check, `--selftest` 6 of 6, including a sibling change left before row 0 that a HEAD diff would report);
  - `scope-check.py --before-row N`, run before each row and in the gate (`--before-row 13`): the S4 checks and the S2 check of every `baseline-scope.json` path that no row before N writes (`--selftest` 6 of 6);
  - `owned-procs.ps1`, the process-ownership rule of AC-10, dot-sourced by `baseline.ps1`, `e2e-run.ps1` and `session-gate.ps1` (`-Selftest` 26 of 26);
  - `site-check.py`;
  - `mutation.py`;
  - `e2e-run.ps1`;
  - `session-gate.ps1`, written at plan time and run at H1-2.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-sites.json`, `baseline-untouched.json` and `base-e2e-count.txt`.
- **Bound to content, never to `HEAD`.** No row, stop condition or closeout check compares a file with `HEAD`. Each compares with the row-0 hashes (`baseline-scope.json`, `baseline-dirty-hashes.json`, `baseline-untouched.json`) or the BASE copies, because Sessions 75 to 77 may leave scoped or read-only files changed and uncommitted. `baseline.sha` is only recorded, and `scope-check.py` accepts a moved `HEAD` whose committed paths are earlier sessions' work.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json` and the BASE copies), not to `HEAD`. In each shared file it changes only its own lines.

| File | Siblings | Rule |
|---|---|---|
| `ui/tests/unit/capture-page.behavior.test.ts` | Session 81 `convert-settings-drafts` appends AC-151.7 to the same `:190` describe and moves its pins at `:392` and `:1231` | Session 81 runs after this one. Row 10 appends at the describe's closing line, found by anchor in the live text, and touches no pin. Session 81's row 0 binds to the content this session leaves |
| `ui/tests/e2e/capture-inbox.test.ts` | Session 75 appends AC-146.19 before this session, through the file's own `launchApp` (its baseline pins `async function launchApp(` once); Session 81 runs `W9-3`, `AC-57.10 header` and `AC-67.24` after it | Row 0 copies the content Session 75 left, so `site-check.py` derives the sites from it, whatever the count. This plan changes only the `_electron.launch(` calls inside `launchApp` and the second site, keeping their keys and order (AC-9); every test body, Session 75's included, is unchanged. AC-10 runs the whole file under the watch |
| `ui/tests/unit/capture-page.test.ts`, `convert-queue.test.ts` | Session 81 runs them unchanged | AC-14 keeps the test's title. The migrated sites keep their keys and order (AC-9) |
| `ui/tests/e2e/backend-output-after-close.test.ts`, `ui/vitest.config.ts` | Session 82 `ready-handshake` runs AC-108.7 there and reads the config | Its site keeps its `env` keys. The config gains one line |
| `.agent/context/known-issues.yaml`, `known-issues.md` | Sessions 75 to 77 and 79 to 82 close their own issues; Session 83 edits the lines that name the home folder | Row 12 changes only the four issues' `status`, `verification` and `resolution_path`, and adds two issues. It names no home path and binds to the row-0 hash (S4) |
| Grouping §6 table | Every session of the grouping | Only row 78 changes |
| Decision ids | Session 79 uses D-944 to D-954 | This plan uses D-933 to D-941. D-942 and D-943 are left free for execution |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

Sessions 75, 76, 77 and 80 name none of these files.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Fixing a product error that the watch surfaces | out-of-scope | — | D-936: registered and brought to Mat |
| Watching unhandled promise rejections in the main process | out-of-scope | — | D-935: a new issue, `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED`. The plan-time probe shows that Electron 42.11.18 keeps rejections as warnings, so they never reach the watch |
| The `npm --prefix ui run dev` symptom of `ELECTRON_RUN_AS_NODE` | out-of-scope | — | D-939: a new issue, `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT` |
| Timing instrumentation for `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | out-of-scope | — | D-940 |
| A `ui` `postinstall` or `pretest` script, or changing CI's install step | out-of-scope | — | D-937 |
| Checking the swallowed `held.close().catch(() => undefined)` in `capture-inbox.test.ts:1977` | out-of-scope | — | D-935: a cleanup path after the test's own close |
| The renderer, the API, MCP, MEU-144 and the TTS model assets | out-of-scope | — | No product file changes; Session 74 is outside this run |
| A port to agentic-framework or Zorivest | out-of-scope | — | Read-only references (session brief) |

## BUILD_PLAN.md Audit

This session has no MEU, so `meu-status.yaml`, `meu-registry.md` and `docs/BUILD_PLAN.md` don't change. H1-3 confirms the render:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/e2e-harness-hardening/ehh-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-harness-hardening/ehh-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence. Every Electron run has `ELECTRON_RUN_AS_NODE` unset, except the flag runs, which set it in a child shell. A run stops only the processes it launched (`owned-procs.ps1`, AC-10), never by name or by path alone.

### 1. Baseline (row 0)

`baseline.ps1` does the following, and every step is fail-fast:

1. **Tree state.** It records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`. Sessions 75 to 77 may be listed there.
2. **Path-scoped baseline.**
   - **The sites.** It checks that exactly the 20 site files hold `_electron.launch(`; a file added to or dropped from that set is S1. The count inside them is written to `baseline-sites.json` and is not fixed at 21: Session 75 appends AC-146.19 to `capture-inbox.test.ts` before this session, and `site-check.py` derives every rule from the BASE copies of the row-0 content.
   - **The sibling-shared anchors.** In the live text, each section this plan edits or relies on occurs exactly once: the `MEU-97 capture hints (AC-97.4)` describe and its HINTS `it` in `capture-page.test.ts`, the `MEU-39 capture GUI runtime (exec r1 F1 F2 F5)` describe in `capture-page.behavior.test.ts`, the `:232` assertion in the unit `layout-primitives.test.ts`, the `include` line of `vitest.config.ts` (which has no `globalSetup` yet) and `launchWithAppData` in `theme-probe.ts`. They are compatible when present and unique; HEAD equality is not required. Otherwise S1.
   - **`baseline-untouched.json`.** `untouched-check.py --record` hashes every tracked or untracked file under `packages/`, `tests/`, `mcp-server/src`, `mcp-server/tests`, `ui/src` and `tools/`. It is the skip basis of the gate's `openapi`, `py-*` and `mcp-*` skips and of H1-4.
   - **`baseline-scope.json`.** For each existing §Files Modified path, its SHA-256; each of the eight new paths must be `absent`.
   - **`baseline-dirty-hashes.json`.** The SHA-256 of every `baseline-dirty.txt` path outside this scope, the shared state files and the other new 2026-11-15 plan folders.
   - **The BASE copies.** It copies every existing path to `C:/Temp/av-kit/e2e-harness-hardening/base/` and prints its line endings.
3. **The binary.** It checks that `ui/node_modules/electron/dist/electron.exe` exists.
4. **The builds.** It runs `npm --prefix ui run build`, the harness build (`AVKIT_PRIMITIVE_HARNESS_BUILD=1 … --outDir ui/out-e2e`) and `build:picker-stub`.
5. **Base Vitest.** It runs the base Vitest suite (`ehh-base-ui.txt`); a failure is S1.
6. **Base Electron.** It runs the base full Electron suite (`ehh-base-e2e.txt`). The passed count goes to `base-e2e-count.txt`. A failure is S1, except for one D-941 repeat.
7. **The flag negative.** It runs BASE `launch.test.ts` with `ELECTRON_RUN_AS_NODE=1` (`ehh-base-flag.txt`). The run must exit non-zero and print `bad option`, which is AC-18's negative.
8. **Selftests.** It runs the seven selftests of `red-check.py`, `identity.py`, `mutation.py`, `site-check.py`, `untouched-check.py`, `owned-procs.ps1` and `scope-check.py`, and `mutation.py status`.

Its last line is `baseline: all steps exit 0`.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.**
  - `red-check.py --require <title>` checks every AC test of the row.
  - The row writes the child exit code to `<receipt>.exit`: `e2e-run.ps1` does it for Playwright, and the row command does it for Vitest.
- **New modules fail by assertion** (§Acceptance Criteria).
- **The helper rows.**
  - Row 1 writes the whole unit file (AC-1 to AC-4 and AC-19's unit part) and runs it Red.
  - Row 2 writes the whole Playwright file (AC-5 to AC-8, five tests) and the startup fixture, and runs it Red.
  - Row 3 writes the three helper files. AC-1, AC-3, AC-4, AC-19 and AC-5 to AC-8 (with AC-19's profile checks) go Green there.
  - AC-2 stays Red until the sites move: row 4 runs it Red with AC-11, and row 5 turns both Green.
- **The install race.** Row 7 runs AC-12 and AC-13 Red; row 8 turns them Green and runs the whole Vitest suite.
- **The hint tests.**
  - Row 9 applies the mutant and runs the BASE AC-97.4 test, which passes: the weakness, shown.
  - Row 10 writes AC-14 and AC-15, applies the mutant and runs them Red.
  - Row 11 runs them Green on the real file.
  - `mutation.py restore` runs in a `finally` in rows 9 and 10.
- **Expectations stay immutable in Green.** A Green row that needs a changed expectation stops on S3. The setup of AC-15 (the drag that mounts Save) may be fixed in row 10 if its Red is a setup failure. Its two `expectBoundHint` calls may not change.
- **Line endings.** The CRLF files of §Files Modified are measured with Python bytes and written with `newline=""`.

### Session gate (H1-2)

`session-gate.ps1` (written at plan time) follows the peer's shape (`2026-11-15-framework-small-syncs/session-gate.ps1`):

- one receipt per step in `C:/Temp/av-kit/e2e-harness-hardening/`, named `ehh-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two `tested_state` values must match |
| Static | `ui-types` (`npm --prefix ui run typecheck`); `ui-lint` (`npm --prefix ui run lint`, which covers `tests/` and the `.cjs` watch); `task-contract`; `untouched-selftest`; `untouched` (`untouched-check.py`: every file under its roots has its row-0 hash); `scope-paths` (`scope-check.py --before-row 13`: every changed path is in §Files Modified, in this plan folder, in the closeout artifacts, in the shared state files, in another new plan folder or in `baseline-dirty.txt`; every `baseline-dirty.txt` path outside this scope keeps its row-0 content; and `CapturePage.tsx`, which no row writes, keeps its row-0 hash); `scope-check-selftest`; `owned-procs-selftest` (AC-10); `red-check-selftest`; `site-check-selftest`; `site-check` (AC-9); `mutation-selftest`; `mutation-status` (no mutant applied; `CapturePage.tsx` equals row 0) |
| Targeted | `register-grammar` (`tests/tooling/test_closeout_register_grammar.py`, which reads the register) |
| Fresh full | `ui-tests` (the whole Vitest suite, which now starts with `INSTALL_ONCE`); `ui-build`; `ui-harness-build`; `ui-picker-stub`; `state-render`; `issues-render` (`render --check`) |
| Runtime | `ui-electron` (the whole suite, `ELECTRON_RUN_AS_NODE` unset; at least `base-e2e-count.txt` + 5 passed and no failed, flaky, not-run or interrupted line; AC-10); `ui-electron-flag` (`launch.test.ts` and `electron-harness.test.ts` with the variable set to `1` in a child shell; a passed line and no `bad option`; AC-18). Each runs through `owned-procs.ps1`, and afterwards only a recorded `electron.exe` that the step launched and left running is stopped (AC-10) |
| Skipped, with reason | `py-types`, `py-lint` and `py-tests`: nothing under `packages/` or `tests/` changes since row 0, and the register is checked by `register-grammar`, `issues-render` and `issue-resolve.py`'s own validator pass. `mcp-*`: no MCP change since row 0. `openapi`: no `packages/api` change since row 0 (H1-4). `build-record`: no release build. Each basis is the `untouched` step, which compares with the row-0 hashes, never with `HEAD`: Sessions 75 to 77 may leave changes under `packages/`, `tests/` or `ui/src` uncommitted, and a `git diff baseline.sha` would report them as this session's |

- **Nothing is excused.** `ui-tests` and `ui-electron` excuse nothing: row 0 showed both suites passing.
- **One repeat.** D-941 allows one whole-gate repeat, and only for a known MONITORING signature in `ui-electron`:
  - the `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` test and worker teardown timeouts in `capture-inbox.test.ts`;
  - the AC-88.12 clipboard primer (`E2E-CLIPBOARD-PRIMER-EMPTY`).

  The handoff records both runs. Any other failure goes to `NEW_FAILURE_RULE`.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a base Vitest or Electron failure (beyond the one D-941 repeat), a launch-site file set other than the 20, a sibling-shared anchor missing or repeated, a `globalSetup` already in `vitest.config.ts`, a missing binary, or a BASE flag run that does not fail with `bad option` | Stop. Bring the receipt to Mat; the plan's counts or negatives no longer hold |
| S2 | A §Files Modified path that no earlier row of this plan has written no longer matches `baseline-scope.json` (`scope-check.py --before-row <n>`, before each row) | Stop. Another session changed a file this plan edits; bring the diff to Mat |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; do not move to Green, and never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, a `baseline-dirty.txt` path changes content, or `known-issues.yaml` no longer has its bound hash at row 12 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | `mutation.py restore` or `status` fails (the hash or mtime of `CapturePage.tsx` differs from row 0), or `NEW_FAILURE_RULE` finds a stack in product code or a spec that throws in main on purpose | Stop with the receipt. For the product case, register the issue first (D-936), write its sha into `ehh-register-rebind.txt`, then bring Mat a brief |
| S6 | Codex is unavailable or the ledger refuses | Mat |

## Decision Log

> [!NOTE]
> - **Autonomous items.** D-933 to D-936, D-938, D-940 and D-941 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test.
> - **Briefs.** D-937 and D-939 failed the convergence test, because the issue and the grouping point different ways and the files do not settle them. Each has a brief below. Each has only an M-6 hit, so Mat's hand-over for this grouping applies and each is recorded as `autonomous`.
> - **Earlier decisions.** D-231 (triage) is applied, not re-recorded. The grouping rows D-813 to D-817 stay in the grouping file's §8 and are not copied here. H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`), and the issues' logs through `--decision-issue`.
> - **Carry-forward.** The grouping's old "Carry-forward" wording (§9, line `:325`, "each row appears in its consuming session's reflection") is ignored under the new HDP §6: the reflection's `### Decisions Log` lists only this session's reversible autonomous choices.
> - **Free ids.** D-942 and D-943 are left free for execution.
> - **No STOP items.** This plan has no STOP item.

```yaml
decision_log:
  - id: D-933
    stage: planning
    question: "Where does the shared Electron launch helper live, and what does it own?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Two files in ui/tests/e2e: electron-env.ts builds the environment and reads the error marker, and electron-app.ts holds the only _electron.launch call, adds the -r watch and wraps close. All 21 sites call launchElectron. The AC-51.7 unit check that named _electron.launch in the layout-primitives E2E file moves to launchElectron, with a new line that checks electron-app.ts, as a named row."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:18 — E2E-ELECTRON-LAUNCH-FLAG proposes fixing the env at the launch helper instead of 14 sites"
      - ".agent/context/known-issues.yaml:18 notes — triage 2026-11-04: one launch helper also gives E2E-MAIN-PROCESS-ERRORS-UNWATCHED its place"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:166 — the 14 _electron.launch sites and a shared launch helper"
      - "ui/tests/e2e/theme-probe.ts — the existing shared launcher shape (launchWithAppData), kept as a caller"
    research: { engine: none, sources: [] }
    reasoning: "The issue, its triage note and the grouping all name one helper in ui/tests/e2e. Splitting the environment into its own file lets the Vitest unit test import it without loading Playwright. Keeping theme-probe.ts's export keeps its callers unchanged. Leaving the sites as they are and adding a lint rule lost because the main-process watch needs a launch path to hook. Two-way: the helper is test code."
  - id: D-934
    stage: planning
    question: "How does the helper keep ELECTRON_RUN_AS_NODE out of the launched app's environment?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Copy process.env, set AVKIT_E2E to 1, merge the site's own keys, then delete ELECTRON_RUN_AS_NODE and drop undefined values. Each site keeps its own keys and order and loses only the spread and AVKIT_E2E."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:18 — blast_radius: pass an explicit env allow-list (or delete ELECTRON_RUN_AS_NODE) at the launch helper"
      - "C:/Temp/av-kit/e2e-harness-hardening/launch-sites.txt — every one of the 21 sites spreads process.env and adds its own AVKIT_E2E_* keys"
    research: { engine: none, sources: [] }
    reasoning: "The issue offers both shapes. An allow-list lost because the app and its backend read many variables (PATH, SystemRoot, the TEMP folders, the sites' AVKIT_E2E_* keys), and a missed one would fail a spec for a reason unrelated to the change. Deleting after the merge also covers a site that passes the variable itself. Two-way: one line in one file."
  - id: D-935
    stage: planning
    question: "How does an uncaught exception in the main process fail the E2E test?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Preload main-error-watch.cjs with -r. It creates the per-launch log file that the helper names in AVKIT_E2E_MAIN_ERROR_LOG, deletes that variable from the app's environment, and adds one uncaughtException listener that appends the full error record (name, message, stack) to the file and writes a marked line to stderr, so Electron shows no dialog and the process keeps running. The helper reads the file after the process exits and throws from close() with each full stack. Unhandled promise rejections are not watched. A plan-time probe shows that Electron's main process keeps them as warnings, so they never reach the listener. They get a new issue, E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED."
    source_tag: Research-backed
    precedents:
      - ".agent/context/known-issues.yaml:3395 — E2E-MAIN-PROCESS-ERRORS-UNWATCHED: the error shows only as a dialog, and app.close() can wait on it"
      - "C:/Temp/av-kit/e2e-harness-hardening/probe/probe-result.txt — with a first preload in Playwright's order the watch loads before main, prints the marker and the process stays alive"
      - "C:/Temp/av-kit/e2e-harness-hardening/probe/rejection-result.txt — Electron 42.11.18 (Node 24.19.0, no rejection listener, empty execArgv): Promise.reject prints UnhandledPromiseRejectionWarning, the uncaughtException listener is not called, and the process stays alive"
      - "ui/tests/e2e/capture-inbox.test.ts:386 — W9-7 already reads stderr for a rejection on the path that needs it"
      - "ui/node_modules/playwright-core/lib/coreBundle.js:10064, :45780 — Playwright reads the child's stderr from spawn, and the Electron launch runs main before it returns, so a listener added after launch misses startup output (round-1 review R1-F1)"
      - "C:/Temp/av-kit/e2e-harness-hardening/probe/startup-result.txt — an ESM main that throws on its first tick, in Playwright's preload order: the log file holds one full JSON record naming the main file, and the main never sees the variable"
    research: { engine: native, sources: ["Node.js process docs, event uncaughtException: adding a listener replaces the default print-and-exit", "Electron docs: the main process shows an error dialog only for an uncaught exception that no listener handles", "Playwright 1.64.1 source: launchProcess attaches its stderr reader at spawn (coreBundle.js:10064), and the Electron launch runs app.initialize() before it returns (:45780)"] }
    reasoning: "The check has to see the error before the window closes and must not depend on any spec's code, so it belongs in the one launch path. A -r preload runs before main/index.js without a product change. Throwing from close() fails exactly the test that launched the app, and the full stack is in the message, so NEW_FAILURE_RULE can see where the error was thrown. The channel is a file, not stderr: Playwright consumes stderr from the spawn and runs main before launch() returns, so a listener added after launch would miss a throw during startup. Reading the preload's in-memory list through app.evaluate before close also lost, because it misses an error thrown during shutdown and needs a live app. Limits: a close() inside a finally that throws replaces an earlier test error in the report; the swallowed close at capture-inbox.test.ts:1977 is not checked, as it is a cleanup path. Rejections do not reach the watch. The plan-time probe (probe/rejection-result.txt) shows that Electron 42.11.18's main process does not use Node's default throw mode for unhandled rejections: it prints UnhandledPromiseRejectionWarning and keeps running, so the uncaughtException listener never sees one. Watching them too lost: the issue covers uncaught exceptions only, and failing a test on a rejection the app survives is a new rule for the suite, which needs its own triage. The new issue records the gap and the cheap next step: an unhandledRejection listener in the same watch that appends to the same log. Setting a Playwright fixture lost because 21 sites would have to change to a fixture form, and theme-probe.ts launches outside a test. Two-way: test code only."
  - id: D-936
    stage: planning
    question: "What does the executor do when the new watch fails a spec that passed before?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Read the stack. A defect in the three new helper files is fixed in the session. A stack in product code is registered with issue_triage.py add (low, ui, the receipt as evidence) and the session stops with a brief for Mat. A spec that throws in main on purpose also stops for Mat. No spec is skipped, marked fixme, marked as expected to fail or put on an allow-list."
    source_tag: Local Canon
    precedents:
      - ".agent/docs/human-decision-protocol.md §4a — M-11: waiving or weakening a blocking gate is human; M-7: a changed existing assertion needs its own row"
      - "C:/Temp/av-kit/dispatch/post-rc3-planner-common.md — a real product error is out of scope: register it, don't fix it"
    research: { engine: none, sources: [] }
    reasoning: "The session's job is to make the suite report what happened, not to change the product, so a product error is recorded and brought to Mat. Skipping or allow-listing the spec would weaken the gate (M-11). A helper defect is this session's own code and is fixed by the Red-Green rows. Two-way: an issue entry."
  - id: D-937
    stage: planning
    question: "How does Vitest stop its workers from racing the Electron binary install?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "A Vitest globalSetup, ui/tests/unit/global-setup.ts. Its default export takes Vitest's project and runs before any worker starts. It requires electron once through createRequire, which runs install.js serially when the binary is missing, and throws with the install command when the binary still does not exist. It then hands the path to the tests with project.provide('electronBinary', path) and returns nothing. vitest.config.ts gains one globalSetup line."
    source_tag: Research-backed
    precedents:
      - ".agent/context/known-issues.yaml:889 — UI-ELECTRON-LAZY-INSTALL-RACE: a repo-wide fix (e.g. a ui postinstall) is left to triage"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:166 — the Vitest setup for the lazy Electron install"
      - "ui/node_modules/electron/index.js:25-52 — 42.11.18 still runs install.js on the first require when dist lacks the binary"
      - "ui/src/main/index.ts:6 and ui/node_modules/electron-store/index.js:3 — the install trigger: electron-store runs the real require('electron'), past the stub alias, in g36-csp.test.ts:40, persist-ui.test.ts:25,37 and single-instance.test.ts:5"
      - "ui/tests/unit/mcp-spawn-electron.test.ts:16-18 — AC-71.10 reads node_modules/electron/path.txt itself, which install.js:94 writes, so it fails after npm ci"
      - "ui/node_modules/vitest/dist/chunks/index.1TqnEahn.js:6567-6569 — Vitest 5.0.5 calls setup(project) and throws on a non-null return that is not a function"
      - "C:/Temp/av-kit/e2e-harness-hardening/ehh-expert-pass.txt — the HDP 5a expert pass: the recommendation holds; the trigger, the setup contract, B-prime and the corrected B and C"
      - ".github/workflows/ci.yml:95-96 — CI installs dependencies with --ignore-scripts (:93), then runs install.js as its own step"
    research: { engine: native, sources: ["Vitest config docs, globalSetup: runs once in the main process before the test workers start; project.provide and inject pass a value from it to the tests", "npm docs: npm ci --ignore-scripts skips lifecycle scripts, postinstall included; ignore-scripts also skips the pre and post scripts of npm run"] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling of the same day ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set, and this item has only an M-6 hit. The deciding fact is the trigger. The unit suite loads the real electron package through electron-store (ui/src/main/index.ts:6, electron-store/index.js:3) in three files that run in parallel workers, and AC-71.10 reads path.txt itself (mcp-spawn-electron.test.ts:16-18). Both break after npm ci. A globalSetup runs once in Vitest's main process before any worker runs or collects tests, so it fixes both however the run starts: the npm script, npx vitest or the IDE's Vitest extension. CI already installs in its own step (ci.yml:95-96) and keeps it, so the build server does not decide this. A postinstall (B) lost: npm ci --ignore-scripts skips it, so CI and any machine that ignores scripts still need the step; its cost is a re-extract from the download cache on each install, not a new download. A pretest script (B-prime, node node_modules/electron/install.js) is one line and survives --ignore-scripts, but it lost because npx vitest and the IDE extension do not run it, and an ignore-scripts=true .npmrc skips pre scripts too. Mocking electron-store in tests/unit/setup.ts lost because AC-71.10 would still fail after npm ci. The setup returns nothing, because Vitest throws on a non-null return that is not a function. It hands its path to the tests through project.provide, so AC-13 proves it ran. M-6 is kept although the conflict is slight: the issue names a postinstall only as an example (known-issues.yaml:896), and the grouping names the Vitest setup. Two-way: two new files and one config line."
  - id: D-938
    stage: planning
    question: "How do the AC-97.4 hint tests check the chord values?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Change the existing source test in capture-page.test.ts so it compares the Save and Region props with chordOf('capture:save') and chordOf('page:primary'), and add a behavior test that checks the rendered buttons with expectBoundHint. Prove both with a mutant that binds both to Ctrl+O: the old test passes on it and the new tests fail. Each changed assertion has its own row."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:2883 — the fix is a test change (assert the rendered values against getCommand(...).shortcut), so it needs approval"
      - "ui/tests/unit/helpers/bound-hint.ts — chordOf and expectBoundHint, the AC-97.4 pattern the other pages' tests use"
      - ".agent/context/known-issues.yaml:2883 verification — the in-memory Ctrl+O probe that showed the weakness"
    research: { engine: none, sources: [] }
    reasoning: "The issue's own fix, with the shared helper the other pages' AC-97.4 tests already use. The change to an existing assertion is named in row 10 with the new assertion, which is the approval the issue asks for (M-7), and the plan review and Mat's execution gate read it there. Keeping the source test and only adding the rendered one lost because the source test would still pass a wrong chord. The mutant proof keeps the test from passing for the wrong reason. Two-way: test code."
  - id: D-939
    stage: planning
    question: "What happens to the npm run dev symptom of ELECTRON_RUN_AS_NODE, which the flag issue also names?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "Resolve E2E-ELECTRON-LAUNCH-FLAG for the E2E launch, and register the dev symptom as its own issue, UI-DEV-ELECTRON-RUN-AS-NODE-SILENT (low, ui), with the issue's workaround and its 2026-09-03 evidence. The dev command does not change."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:18 — the title names E2E and npm run dev; the blast_radius widened it on 2026-09-03 to the silent dev symptom"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:168 — the grouping scopes the session to a launch that drops ELECTRON_RUN_AS_NODE from the env it passes"
      - "docs/execution/plans/2026-11-15-e2e-harness-hardening/issue-resolve.py:52 — RESOLVE_KEYS: a resolve changes only status, verification and resolution_path, so the resolved issue keeps its title"
      - "C:/Temp/av-kit/e2e-harness-hardening/ehh-expert-pass.txt — the HDP 5a expert pass: the recommendation holds; B costs less than stated; M-8 is close"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling of the same day ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set, and this item has only an M-6 hit. The grouping scopes this session to the E2E launch, and the dev symptom is a different command with a different fix. A new issue keeps the symptom tracked with its workaround, and the flag issue can close on what it measured. Fixing dev too (B) lost on scope, not on cost. electron-vite 5.0.0 starts Electron with the parent's environment, so one line at the top of ui/electron.vite.config.ts that deletes ELECTRON_RUN_AS_NODE likely fixes dev. That is an inference from the expert pass and was not probed. It still changes a developer command outside this grouping row, it needs its own check that dev starts and reloads, and any edit to that config makes the E2E stale-build check (tests/e2e/global-setup.ts:40-44) ask for a rebuild. The resolved issue keeps its title, which names npm run dev, because issue-resolve.py changes only status, verification and resolution_path (:52). Its closing note is the only correction the tools allow, so it names the new issue. M-8 is close, because the session resolves only the E2E half of an issue the grouping row covers; like M-6 it is in the hand-over set. Keeping the flag issue open with a note lost because its E2E half would then show as open after it is fixed. Two-way: an issue entry."
  - id: D-940
    stage: planning
    question: "Does the helper change E2E teardown, and what does that mean for CAPTURE-E2E-LAUNCH-TEARDOWN-HANG?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes, in two small ways: the -r preload, and a wait of at most 5 s for the process to exit after the original close, which returns at once when the process has exited and never fails by itself. Close is otherwise unchanged. No timing instrumentation is added, and the teardown-hang issue stays MONITORING, unchanged."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:2845 — CAPTURE-E2E-LAUNCH-TEARDOWN-HANG: hypothesis host load; next step on a repeat is to log host process starts"
      - ".agent/context/known-issues.yaml:3395 — app.close() could wait on a main-process error dialog"
    research: { engine: none, sources: [] }
    reasoning: "The log is read after the process exits, so that an error thrown during shutdown is in it, and close waits briefly for the exit. The watch removes the one known way close could hang, the error dialog, so the hang issue loses a candidate cause but gains no evidence; its next step is still to log host process starts on a repeat. Adding timing instrumentation lost because the issue asks for it only on a repeat and it would widen the change. Two-way: a few lines."
  - id: D-941
    stage: planning
    question: "Which gate steps run, what do they excuse, and when may the Electron run repeat?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The steps of the plan's Session gate with the RC2 harness and picker-stub builds; py-types, py-lint, py-tests, mcp-*, openapi and build-record skipped with reasons; nothing excused; one whole-gate repeat only for the teardown-hang timeouts in capture-inbox or the AC-88.12 clipboard primer, both MONITORING; any other failure goes to D-936."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-release-rc2 — the full Electron suite reads the isolated harness build and the region-picker stub"
      - ".agent/context/known-issues.yaml:2845 — a teardown-hang miss fails the fail-fast gate at ui-electron, so the run has to be repeated"
      - "docs/execution/plans/2026-11-15-framework-small-syncs/session-gate.ps1 — the peer gate shape"
    research: { engine: none, sources: [] }
    reasoning: "Only ui files change, so the Python and MCP suites have nothing new to check; the register is checked by its own tool tests and render check. The one repeat follows the teardown-hang issue's own record and is limited to known signatures, so a new failure is never retried away. Two-way: a gate script."
```

Expert pass (fresh context): 2 briefs. Holds: D-937, D-939. Changed: none. Not adopted: none. Receipt: `C:/Temp/av-kit/e2e-harness-hardening/ehh-expert-pass.txt`. Both recommendations stand. Its fixes are adopted:
- D-937: the brief text, `INSTALL_ONCE`, AC-12 and AC-13;
- D-939: the brief text;
- D-935: the reasoning and the issue text, settled by the rejection probe;
- the line references.

### D-937: How should the UI test run stop its parallel workers from racing to install the Electron program?

**I recommend A: a one-time setup step in the UI test run.**
- **The problem.** Several unit tests load the app's main file. That file loads a settings package, and the settings package loads the real `electron` package, which installs the program when it is missing. Three such test files run in parallel workers, so after a clean install they race to install it. One more test reads the program's path file directly, so it fails outright until the program is installed.
- **What A does.** A setup step runs once, before any worker starts, however the tests are started: the npm script, `npx vitest` or the IDE's test panel. It loads `electron` once, which installs the program one time, in order, when it is missing. If the program still is not there afterwards, the run stops with one clear message that names the command to run. The step also hands the program's path to the tests, so one test proves that the step really ran. The build server keeps its own install step.
- **How A can fail.** The step runs only for the unit tests, so a future runner that loads `electron` in parallel outside Vitest would race again. On a machine with no network and no program, every unit test run now stops at the start instead of failing a few tests at random. A half-extracted program can still pass the check, as it can today.
- **Undo cost.** Small: delete two new files and one config line.

The other options:
- B: add an install script that runs after `npm install` in the `ui` package (the issue's example). It fixes ordinary installs. But the build server, and any machine that installs with scripts turned off, skips it, so the build server would still need its separate step. Each install would also re-extract the program from the download cache.
- B′: add a `pretest` script that runs the installer before `npm run test`. It is one line and it works when install scripts are off. But it does not run for `npx vitest` or the IDE's test panel, and a machine set to ignore scripts skips it as well.
- C: keep things as they are. The build server keeps its separate install step. A developer's first test run after a clean install fails random unrelated tests until the program is installed (the issue counts about 3 in 10).

Refs: `.agent/context/known-issues.yaml:889` (`UI-ELECTRON-LAZY-INSTALL-RACE`), `ui/src/main/index.ts:6`, `ui/node_modules/electron-store/index.js:3`, `ui/tests/unit/mcp-spawn-electron.test.ts:16-18`, `ui/node_modules/electron/index.js:25-52`, `.github/workflows/ci.yml:95-96`, grouping `:166`, M-6, AC-12, AC-13.

### D-939: The launch-flag issue also says `npm run dev` opens no window from an IDE terminal. Does this session fix that too?

**I recommend A: close the issue for the tests, and file the dev symptom as its own issue.**
- **Why.** This session's grouping row covers the test launches, and the tests are what the new helper fixes. The dev command is a different program with a different fix.
- **What A does.** A new issue keeps the dev symptom on record, with its known workaround (clear the variable first, or use a terminal opened outside the IDE) and the 2026-09-03 evidence.
- **The closed issue keeps its title.** That title still names `npm run dev`, because the register tool changes only an issue's status, its verification and its closing note. The closing note carries the correction and names the new issue.
- **How A can fail.** A developer who reads only the closed issue may think `npm run dev` is fixed too. The closing note and the new issue both say it is not.
- **Undo cost.** Small: one register entry.

The other options:
- B: also fix the dev command. One line at the top of `ui/electron.vite.config.ts` that clears the variable before electron-vite starts the app likely does it. That is an inference from reading electron-vite, not something tried. It would remove the silent failure for everyone. But it changes a developer command outside this session's grouping row, it needs its own check that dev still starts and reloads, and editing that file makes the E2E suite's stale-build check ask for a rebuild. A still wins, because the grouping scopes this session to the test launches.
- C: keep things as they are, and leave the launch-flag issue open with a note that the test half is fixed. The register then shows a fixed problem as open, and the dev symptom stays inside an issue whose title is mostly about tests.

Refs: `.agent/context/known-issues.yaml:18` (`E2E-ELECTRON-LAUNCH-FLAG`, blast_radius "WIDENED 2026-09-03"), grouping `:168`, `issue-resolve.py:52`, M-6. M-8 is close, because only the E2E half of a covered issue is resolved; like M-6 it is in the hand-over set. AC-17, AC-18.

## Research References

- **Node.js `process`, event `'uncaughtException'`.** A listener replaces the default behaviour of printing the stack and exiting. The process keeps running, which is why the watch writes a marked line and lets the test fail the close instead. Measured in `probe/probe-result.txt`.
- **Electron.** The main process shows its error dialog only for an uncaught exception that no other listener handles. With the watch loaded, no dialog opens, which is the dialog that `E2E-MAIN-PROCESS-ERRORS-UNWATCHED` says `app.close()` can wait on.
- **Playwright 1.64.1 `_electron.launch`.** It prepends its own `-r` loader and `--inspect=0 --remote-debugging-port=0`. With `ELECTRON_RUN_AS_NODE=1` the binary rejects the debugging flag (`flag-probe.txt`). A second `-r` runs after Playwright's own (`probe/probe-result.txt`). `launchProcess` attaches Playwright's own stderr reader at spawn (`coreBundle.js:10064`), and the Electron launch runs main through `app.initialize()` before it returns (`:45780`), so a listener that the helper adds after `launch()` resolves can miss output written during startup. The watch therefore writes to a log file (`probe/startup-result.txt`).
- **Vitest `globalSetup`.** It runs once in the main process before the test workers start. Vitest 5.0.5 calls `setup(project)` and throws on a non-null return that is not a function (`index.1TqnEahn.js:6567-6569`). `project.provide(key, value)` hands a value to the tests' `inject(key)`. The `electron` alias in `vitest.config.ts` applies to imports that Vite resolves. `createRequire` uses Node's resolver, so it loads the real package.
- **Electron 42.11.18, unhandled rejections.** The main process keeps rejections as warnings, not Node's default throw mode. A rejection prints `UnhandledPromiseRejectionWarning` and the app keeps running. An `uncaughtException` listener never sees it (`probe/rejection-result.txt`).
- **The `electron` package 42.11.18.** `index.js:25-52` runs `install.js` through `spawnSync` when `dist/` lacks the binary, with no lock, so parallel first requires race.

## Planning receipts

All are under `C:/Temp/av-kit/e2e-harness-hardening/` and were read-only against the repository:

| Receipt | What it shows |
|---|---|
| `launch-sites.txt` | The 21 `_electron.launch(` sites in 20 files, each with its `...process.env` spread |
| `flag-probe.txt` | `electron.exe: bad option: --remote-debugging-port=0` with `ELECTRON_RUN_AS_NODE=1` |
| `probe/probe-result.txt` (with `probe/first.cjs`, `hook.cjs`, `main.cjs`, `run.cjs`) | The watch loads after a first preload, prints the marker and keeps the process alive |
| `probe/rejection-result.txt` (with `probe/main-rej.cjs`, `run-rej.cjs`) | In Playwright's preload order with the watch, `Promise.reject` in the main process prints `UnhandledPromiseRejectionWarning`, the watch prints no marker, and the process stays alive (D-935). It ran the shared binary read-only, with a scratch `--user-data-dir` |
| `ehh-expert-pass.txt` | The HDP §5a expert pass on D-937 and D-939 (saved by the coordinator) |
| `line-endings.txt` | The endings and sizes of every file in §Files Modified |
| `mutation-anchor-probe.txt`, `mutation-selftest.txt` | Each mutant anchor is found once in `CapturePage.tsx`; the restore brings back the bytes and the mtime |
| `site-check-selftest.txt` | `site-check.py --selftest`: 13 of 13 |
| `rc-selftest.txt`, `id-selftest.txt` | The `red-check.py` and `identity.py` selftests |
| `ps1-parse.txt` | `baseline.ps1`, `session-gate.ps1`, `e2e-run.ps1` and `owned-procs.ps1` parse in pwsh |
| `probe/startup-result.txt` (with `probe/startup.mjs`, `watch2.cjs`) | The planned watch, in Playwright's preload order, logs a first-tick throw of an ESM main as one full JSON record naming the main file; the main never sees `AVKIT_E2E_MAIN_ERROR_LOG`; the window loads and the process exits 0. It ran the shared binary read-only and was stopped by its own recorded id |
| `probe/eslint-cjs.txt`, `probe/eslint-fixture.txt`, `probe/eslint-cjs2.txt` | `eslint --stdin --stdin-filename` with the ui config: the planned watch (as `tests/e2e/main-error-watch.cjs`) and the planned fixture (as `tests/e2e/fixtures/startup-throw-main.mjs`) lint clean; the probe main with a `setTimeout` fails `no-undef` |
| `probe/owned-result.txt` (with `probe/owned/`) | A real `Invoke-OwnedRun` of a child that left an orphan recorded the run's tree; the old path-and-time rule would also have stopped an unrelated process on the same path started during the run; `Stop-OwnedElectron` stopped only the orphan, and the unrelated process was then stopped by its own recorded id |
| `owned-procs-selftest.txt` | `owned-procs.ps1 -Selftest`: 26 of 26. At the stop: a pid reused by a later replacement, an exit before the open, an exit between the open and the start time, an exit after the check, sub-microsecond ticks and a one-microsecond difference, a pid-only stop as the negative, and no `Stop-Process` line in the script. Over four snapshots: the unrelated same-path process started during the run, a pid reused by an unrelated process whose child outlives it, a child started after its parent was last seen, the pinned root, an orphan and a same-time child; negatives for the old path-and-time rule and for the round-1 current-snapshot-only rule |
| `probe/ctime-res.txt` (with `probe/ctime-res.ps1`) | For 60 live user processes, CIM's `CreationDate` equals `Process.StartTime` read through a handle once the start time is truncated to whole microseconds; none differed otherwise |
| `probe/verified-stop.txt` (with `probe/verified-stop.ps1`) | The real `Invoke-VerifiedStop` on a pwsh sleeper the probe started: a wrong creation time is `mismatch` and the process lives; the right one is `stopped`; after the exit it is `gone` |
| `probe/mutant-selftest.txt` (with `probe/mutant-owned-procs.ps1`) | With the start-time check removed, the selftest fails its replacement and one-microsecond cases (24 of 26) |
| `probe/owned-real-result.txt` (with `probe/owned-real.ps1`) | A real `Invoke-OwnedRun` of a nested pwsh recorded the whole four-process tree with live CIM values; `Stop-OwnedElectron` stopped nothing |
| `probe/sessiondata-result.txt` (with `probe/sd/main.cjs`, `probe/sd-run.txt`) | This checkout's Electron, started by `Start-Process -PassThru` and waited on by its recorded id (it exited 0 by itself): after `app.setPath('userData', X)` before ready, `sessionData` is `X` too |
| `probe/app-data-sites.txt` | Every `_electron.launch(` site under `ui/tests/e2e` passes `AVKIT_APP_DATA` from `mkdtempSync(join(tmpdir(), …))`, directly or through `launchWithAppData(dir)` |
| `probe/eslint-fixture2.txt` (with `probe/startup-fixture2.mjs`) | The planned fixture with its scratch profile and its fail-closed exit lints clean with the ui config |
| `scope-check-selftest.txt` | `scope-check.py --selftest`: 6 of 6, including a sibling change to a scoped path before the row that writes it, and a mutant left in `CapturePage.tsx` |
| `untouched-selftest.txt` | `untouched-check.py --selftest`: 6 of 6 |
| `anchor-probe.txt` | Each sibling-shared anchor of row 0 occurs once in the live text |
| `probe-decision-sources.txt` | `decision_sources` reads D-231 from the issue and D-813 to D-817 from the grouping |
| `issue-triage-help.txt`, `add-help.txt` | `issue_triage.py add` takes `--id`, `--title`, `--severity`, `--component`, `--discovered`, `--root-cause` and `--blast-radius` |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the four issues, D-231 and the grouping §3 | `ehh-plan-2026-11-15-e2e-harness-hardening` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-1 to AC-19 | `ehh-execution-2026-11-15-e2e-harness-hardening` |
