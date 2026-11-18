---
project: "2026-11-17-test-run-reliability"
date: "2026-11-17"
source: "grouping .agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md §3 Session 90; issues PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD, E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED and UI-DEV-ELECTRON-RUN-AS-NODE-SILENT (D-1103)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md"
---

# Implementation Plan: wait on the workers, watch main-process rejections, and clear ELECTRON_RUN_AS_NODE for dev

> **Project**: `2026-11-17-test-run-reliability`
> **Build Plan Section(s)**: none. This is test-harness debt with no MEU, as in Session 78 `2026-11-15-e2e-harness-hardening` and grouping D-1103.
> **Status**: said to execute (USER_EXPLICIT 2026-11-17 "run @.agent/skills/issue-triage/ create session grouping and continue planning and executing as orchestrator", grouping §8 D-1102, D-1104). `plan_to_exec_gate: human`: that message is the execution approval once the plan review approves (D-1104); the plan review was approved at round 2 (.agent/context/handoffs/2026-11-17-test-run-reliability-plan-critical-review.md). Session 89 is committed (`79e3fa5`); Session 90 is the last session in the grouping's queue.

---

## Goal

**Goal anchor:** the two Python integration tests that failed under load wait on their workers' signals with a 60-second bound (`WORKER_WAIT_S`), so they pass with a worker slowed past 5 s and three times in a row on a host loaded to at least 85 %, and a plain run of the three files that reach those waits (the two, and `test_tts_voice_packs.py`, which reuses the TTS file's `Stack`) takes no more than 30 s longer than at row 0; every E2E Electron main process records an unhandled promise rejection and fails its close with the rejection's stack, as it already does for an uncaught exception, and still prints a warning line on stderr; `npm --prefix ui run dev` removes `ELECTRON_RUN_AS_NODE` itself and opens a window when the terminal sets it; no file under `ui/src/`, `packages/`, `mcp-server/` or `tools/` changes, and no API route, OpenAPI document or MCP tool changes; scripts and tests prove all three, with no manual check.

**Why.**

- **`PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD`** (`known-issues.yaml:5428`, low, P3). In the Session 81 gate two tests failed once each while the host was loaded (py-tests took 676 s and 911 s, against 457 s unloaded): `test_youtube_adapter.py::test_ac_122_8_surrogate_title_survives_real_storage` joined its worker for 5 s and then found the job `Processing` (`:939-940`), and `test_tts_assets.py::test_ac_62_16_model_overshoot_is_clipped_not_failed` gave up in `wait_idle` after 5 s (`:177`) and found the spaCy download still `Downloading` (`:260`). Each passed alone (Session 81 D-1068). The 5 s bounds are fixed, so a slow worker on a busy host outlives them.
- **`E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED`** (`:5354`, low, P4). Electron 42.11.18 keeps an unhandled promise rejection in the main process as a warning (Session 78 D-935), so the `uncaughtException` watch that Session 78 added (`ui/tests/e2e/main-error-watch.cjs:16`) never sees one, and an E2E test passes while main logs one. The issue names the next step: append `unhandledRejection` events to the same log.
- **`UI-DEV-ELECTRON-RUN-AS-NODE-SILENT`** (`:5344`, low, P4; moved from `E2E-ELECTRON-LAUNCH-FLAG` on 2026-11-15, Session 78 D-939). VS Code and Cursor terminals set `ELECTRON_RUN_AS_NODE=1`, so `electron-vite dev` starts `electron.exe` as plain Node and no window opens, with no error. The workaround is to clear the variable first.

**Grouping §3 Session 90** (grouping `:89-99`): the order is the Python waits, then the rejection watch, then the dev script; the gate rule is "a test whose wait changes keeps its assertions; any assertion change is named in the plan"; cloud/local is local (Electron E2E and the full Python suite); calibrate against Session 78 and Session 79. Mat 2026-11-16: "This should be done with framework and scripts!", so nothing here is a manual check.

**What the code shows (plan-time reads at `HEAD` `79e3fa5`, `trr90-probe.txt`):**

- **The waits.** `tests/integration/test_tts_assets.py` (CRLF, 1099 lines) has eleven 5-second waits: `:62` (`self.hold.wait(timeout=5)` in the fake wheel server), `:177` (`wait_idle(self, timeout: float = 5.0)`, the stack helper that 21 tests reach: 19 in this file and 2 in `tests/integration/test_tts_voice_packs.py`, which imports `Stack` at `:19` and calls the default from its `stack` fixture's teardown at `:249` and from the assertion at `:320`), `:227`, `:526`, `:712`, `:896` (`_poll_tts(..., timeout: float = 5.0)`), `:938` (`self.release.wait(5.0)`), and four assertions, `:955` and `:977` (`assert gated.entered.wait(5.0)`) and `:963` and `:984` (`assert tts.wait_idle(5.0) is True`). `tests/integration/test_youtube_adapter.py` (CRLF, 1159 lines) has one: `:939` `service._thread.join(timeout=5)`, followed by the assertion at `:940`. Every one of them returns as soon as its event is set or its thread ends; only the upper bound is fixed. An AST walk lists the tests that reach each line (`trr90-probe.txt`). Five other test files import from `test_youtube_adapter.py` (`tests/e2e/test_api_client_fallback.py`, `tests/integration/test_js_runtime_wiring.py`, `test_youtube_adapter_visibility.py`, `test_youtube_client_fallback.py`, `tests/unit/test_extract_options.py`), but only constants and helpers, never the test that holds `:939`, so none of them reaches a changed wait; `test_tts_voice_packs.py` is the only importer of `test_tts_assets.py`.
- **Elsewhere.** The same pattern has 137 sites in 29 files (`trr90-wait-sweep.txt`; `tests/unit/test_services.py` alone has 61). None of them has failed in a recorded run (D-1115).
- **The watch.** `main-error-watch.cjs` (LF, 25 lines) is preloaded with `-r` into every E2E main process (`electron-app.ts:69-96`). It records `{ name, message, stack }` per uncaught exception into the log `AVKIT_E2E_MAIN_ERROR_LOG` names and writes `[avkit-e2e-main-error] <stack>` to stderr; `checkMainErrors` (`electron-app.ts:46-62`) throws `'main-process uncaught exception(s):\n' + ...` from the wrapped close. `unhandledRejection` appears nowhere in it.
- **Electron and rejections** (`trr90-electron-rejection-probe.txt`). Without a listener, Electron's main process prints `(node:<pid>) UnhandledPromiseRejectionWarning: Error: avkit-probe-rejection` to stderr and exits 0; with a `process.on('unhandledRejection')` listener the listener sees the rejection and nothing is printed. So a listener silences the warning that `capture-inbox.test.ts:403` (W9-7) reads on stderr (`expect(stderr).not.toMatch(/UnhandledPromiseRejectionWarning: Error: backend not ready/)`) (D-1117).
- **Node's modes** (`trr90-node-mode-probe.txt`, Node v26.13.0): with `--unhandled-rejections=warn-with-error-code` a process with no listener prints the warning and exits 1, and one with a listener exits 0 and prints nothing, as Electron does. `warn` prints the warning even with a listener. The unit test's child process therefore runs with `warn-with-error-code`.
- **The dev launch.** `ui/package.json` (CRLF) `:16` is `"dev": "electron-vite dev",` and `:18` is `"preview": "electron-vite preview",`. electron-vite 5.0.0's `startElectron` (`ui/node_modules/electron-vite/dist/chunks/lib-q6ns0vZr.js:220-240`) spawns Electron with `{ stdio: 'inherit' }` and no `env`, so the child inherits the variable; dev calls it at `lib-7y7CgM8M.js:32` and `:74`, and preview at `lib-Dvh2Hokw.js:21`. The bin is `ui/node_modules/electron-vite/bin/electron-vite.js`. The app takes the `av-kit-ui` single-instance lock at `ui/src/main/index.ts:99`, before user data moves to `AVKIT_APP_DATA`, so a second dev app quits without a window while another runs (D-1120).
- **What checks `ui/scripts/`.** `ui/tsconfig.json` includes `src`, `tests` and three config files, and the `lint` script is `eslint src/ tests/ --max-warnings 0`, so nothing typechecks or lints `ui/scripts/`. Row 7 and the gate run `node --check` on the new script, and its exported functions are tested through a dynamic import (AC-13, AC-14).
- **The stale-build check.** `ui/tests/e2e/global-setup.ts:40-47` refuses an `out/` older than its sources. `npm run dev` writes `out/main` and `out/preload`, so every dev proof is followed by `npm --prefix ui run build` before the next Electron test (D-1120).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-17). The change touches two Python test files, the three E2E harness files and one npm script, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go under `C:/Temp/av-kit/test-run-reliability/`, named `trr-*` (planning receipts are `trr90-*`).
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE` (Session 79 RULE-3, Session 85 RULE-2, Session 88 RULE-3). The one exception is `dev-proof.py --run-as-node set`, which sets it for its own child on purpose.
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`. Playwright runs with `ELECTRON_RUN_AS_NODE` cleared.
  - Each Electron test and each dev proof stops only the processes it started, by the pid it recorded. No row stops a process by image name; other worktrees run their own apps.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local (Electron, the full Python suite and a loaded host; grouping §3 "Cloud/local: local").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), run by the coordinator, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `trr-plan-2026-11-17-test-run-reliability` and `trr-execution-2026-11-17-test-run-reliability`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
  - Each dispatch writes its own run log; the console output goes to a separate console file, never into the run log, and the row reads both tails (Session 88 RULE-2).
- **Queue:** Session 89 is committed (`79e3fa5`). Other sessions may write into `main` while this one runs, so the baselines and scope checks are path-scoped and bound to content at row 0 (§Verification Plan 1).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| All three issues (no MEU) | `.agent/context/handoffs/2026-11-17-test-run-reliability-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-17-test-run-reliability-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-17-test-run-reliability-implementation-critical-review.md`

The session has one handoff, following the no-MEU precedent `2026-11-15-e2e-harness-hardening-handoff.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local checkers (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py` |
| WP-2 | The Python waits: Red, Green and the load run (rows 1 to 3) | WP-1 | shared | `WORKER_WAIT_S` in the two test files; the slowed-worker, wait-check, time and load receipts |
| WP-3 | The rejection watch: Red, then Green and the full E2E suite (rows 4 and 5) | WP-2 | shared | `main-error-watch.cjs`, `electron-env.ts`, `electron-app.ts`, `rejection-watch.test.ts`, `main-rejection-watch.test.ts` |
| WP-4 | The dev script: Red with the base proofs, then Green with the proofs and a rebuild (rows 6 and 7) | WP-3 | shared | `ui/scripts/electron-vite-dev.mjs`, `package.json:16`, `dev-script.test.ts`, the dev-proof receipts |
| WP-5 | Registers, `commands.md` and the grouping row (row 8) | WP-4 | shared | Three issues resolved, one added, `commands.md`, grouping row 90 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.** Two decisions are briefs (D-1115 and D-1118, §Decision Log): how far the longer waits reach, and how `npm run dev` clears the variable. Your hand-over ('continue planning and executing as orchestrator', 2026-11-17, continuing 'like we did here. But use the new HDP process.', 2026-11-15) settles them on the recommendation, and they are recorded that way. Read them if you want to overrule one before execution. There is no human check row: scripts and tests prove each change in rows 1 to 7 and in the gate. One stop is reserved for you (D-1121, S10): if the new watch shows that an existing Electron test leaves a real rejection in the main process, the session stops and brings it to you rather than excusing it.
>
> **What changes for you:**
>
> - The two Python tests that failed while the machine was busy now wait up to 60 s for their background work, instead of 5 s. When the work is quick they finish as quickly as before.
> - An Electron test now fails when the app's main process leaves a promise rejection unhandled, and the failure shows the rejection's stack. The stderr line that one test reads is kept. This is a new pass condition for every existing Electron test, named in §Test pins; the full Electron suite runs three times with it before the session goes on. A rejection found after this session is registered with its stack, never excused.
> - `npm --prefix ui run dev` from a VS Code or Cursor terminal now opens the app window. It prints `electron-vite-dev: cleared ELECTRON_RUN_AS_NODE` when it removed the variable.
> - `npm --prefix ui run preview` still has the old gap; it is registered as a low known issue, not fixed here (D-1119).

## Proposed Changes

### Single-statement contracts

- **`WORKER_WAIT` (D-1115):** each of the two test files defines `WORKER_WAIT_S = 60.0` once, in a three-line block (two comment lines and the definition) straight after its anchor line (`test_tts_assets.py:30` `VOCAB = ...`; `test_youtube_adapter.py:105` `PROGRESS_MIN_INTERVAL_S = 0.25`), and every 5-second worker wait in the file reads it instead of its literal: eleven in the TTS file, one in the YouTube file. Of the TTS eleven, nine wait on the worker or a service directly and two (`:62` in `WheelServer.fetch` and `:526`) wait on the fake upstream's release gate, which the worker's request is held on; all eleven read `WORKER_WAIT_S`. The block's text is `wait-check.py`'s `CONSTANT_BLOCK`.
- **`WAITS_NAMED`:** four assertion lines change, and only their bound: `test_tts_assets.py:955` and `:977` (`assert gated.entered.wait(5.0)` becomes `assert gated.entered.wait(WORKER_WAIT_S)`) and `:963` and `:984` (`assert tts.wait_idle(5.0) is True` becomes `assert tts.wait_idle(WORKER_WAIT_S) is True`). What each asserts is unchanged. No other assertion line in either file changes, including `:260`, `:940` and `:964`.
- **`WAIT_SIGNALS_KEPT`:** every changed wait still returns as soon as its event is set, its thread ends or its state is reached; no `sleep` is added and no wait is replaced by a poll loop. The line diff against row 0 holds only the inserted block and the one-for-one replaced lines (`wait-check.py`).
- **`TIME_GUARD`:** a plain run of the three files that reach the changed waits (`test_tts_assets.py`, `test_youtube_adapter.py`, `test_tts_voice_packs.py`; no plugin) finishes within the row-0 time (`trr-base-two.txt`, the same three files; the receipt keeps its name) plus 30 s, so a wait that now runs to its new bound on a passing test is caught.
- **`REJECTION_WATCH` (D-1116):** `main-error-watch.cjs` adds `globalThis.__avkitE2eMainRejections = []` and a `process.on('unhandledRejection', (reason) => ...)` listener that pushes the reason and appends one JSON line `{ kind: 'rejection', name, message, stack }` to the same log, with the fields computed from the reason by the exception record's rules (`name`: the reason's `name` or `typeof reason`; `message`: its `message` or `String(reason)`; `stack`: its `stack` or `String(reason)`).
- **`REJECTION_WARNING_LINE` (D-1117):** the listener also writes `[avkit-e2e-main-rejection] UnhandledPromiseRejectionWarning: <stack>` and a newline to stderr, so a reader of stderr still finds `UnhandledPromiseRejectionWarning: Error: <message>` (W9-7, `capture-inbox.test.ts:403`), which the listener would otherwise silence.
- **`MAIN_REJECTION_MARKER`:** `electron-env.ts` exports `MAIN_REJECTION_MARKER = '[avkit-e2e-main-rejection]'` beside `MAIN_ERROR_MARKER`.
- **`REJECTION_FAILS_CLOSE` (D-1116):** `MainErrorRecord` gains `kind?: 'rejection'`; `checkMainErrors` throws when there is any record, with the header `'main-process uncaught exception(s) or unhandled rejection(s):\n'`, and each rejection's text is prefixed `unhandled rejection: ` before its stack. `mainErrorRecords` is unchanged. A handled rejection leaves no record. `checkMainErrors` runs after `close()` and a 5 s exit wait, so a rejection during shutdown (a main-process fetch to the fake E2E backend `http://127.0.0.1:9/api/v1` that `ui/src/main/index.ts:482` publishes, or a poll cut off by the exit) counts too. This is a new pass condition on every existing E2E test, named as one suite-wide row in §Test pins.
- **`EXCEPTION_WATCH_KEPT`:** the `uncaughtException` listener, its record `{ name, message, stack }` (no `kind`), its `[avkit-e2e-main-error]` line, `__avkitE2eMainErrors` and `__avkitE2eMainErrorWatch` are unchanged; the Session 78 tests at `e2e-harness.test.ts:69` and `:112` and `electron-harness.test.ts:50`, `:69`, `:97` and `:117` pass unchanged.
- **`DEV_ENV_CLEARED` (D-1118):** `ui/scripts/electron-vite-dev.mjs` exports `devEnv(base)`, which returns `{ env, cleared }`: `env` is a new object with every key of `base` except those whose upper-cased name is `ELECTRON_RUN_AS_NODE`, and `cleared` is whether one was removed; `base` is not changed.
- **`DEV_NOTICE`:** the script exports `DEV_NOTICE = 'electron-vite-dev: cleared ELECTRON_RUN_AS_NODE'` and writes it and a newline to stderr when `cleared` is true, before it starts electron-vite.
- **`DEV_ARGS`:** the script exports `devArgs(extra)`, which returns `[<ui>/node_modules/electron-vite/bin/electron-vite.js, 'dev', ...extra]`; run as the entry, it spawns `process.execPath` with `devArgs(process.argv.slice(2))` and `{ stdio: 'inherit', env, cwd: <ui> }`, and exits 1 on a spawn error.
- **`DEV_SIGNALS`:** while the child runs, the entry installs no-op `SIGINT` and `SIGBREAK` listeners (Ctrl+C and Ctrl+Break reach the whole console group, so the child gets them itself and the wrapper must not end first and leave electron-vite or Electron behind) and forwards `SIGTERM` to the child with `child.kill('SIGTERM')`. It exits only from the child's `'exit'` event, with `process.exit(exitCodeFor(code, signal))`, and never re-raises a signal on itself (on win32 `process.kill(process.pid, sig)` is an abrupt terminate with no 128+n code). The script exports `exitCodeFor(code, signal, platform = process.platform)`: `code` when it is a number; otherwise, off win32, `128 + os.constants.signals[signal]` when `signal` names a known signal; otherwise 1. So on win32 it is `code ?? 1`.
- **`DEV_ENTRY_ONLY`:** the script exports `isEntry(argv1, moduleUrl)`, true only when `argv1` is defined and resolves to the module's own file path (compared without case on win32); the spawn runs only when `isEntry(process.argv[1], import.meta.url)`, so importing the module in a test starts nothing.
- **`DEV_SCRIPT`:** `ui/package.json:16` becomes `    "dev": "node ./scripts/electron-vite-dev.mjs",`; no other line of the file changes, and `:18` (`preview`) stays as it is.
- **`PREVIEW_REGISTERED` (D-1119):** `npm run preview` has the same gap (`lib-Dvh2Hokw.js:21`); row 8 registers `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` (`open`, low, ui) and does not fix it.
- **`DEV_PROOF` (D-1120):** `dev-proof.py` runs `load-run.py`'s host-load wait first, waits out only another av-kit dev app (an Electron main process whose executable is under an av-kit `ui/node_modules/electron/dist/`, in `P:/av-kit` or a `P:/av-kit-wt/<name>` worktree; other projects' Electron apps use another lock and are counted and ignored), starts `npm --prefix ui run dev` with the variable set (or removed), detects a visible, titled top-level window of class `Chrome_WidgetWin_1` owned by the launch's Electron process (a native error dialog, class `#32770`, never counts), stops only the processes it recorded, and is followed by a build before any Electron test. A recorded (id, creation time) never changes: the launch's root must be the script's own child started after the launch began, and a live process that holds a recorded id with another creation time is never written into the record, never counts as the launch's (its window can't pass) and passes no ownership on; a window passes only when its owner still has its recorded identity in a snapshot taken after the windows were listed.
- **`COMMANDS_DOC`:** `.agent/docs/commands.md` (CRLF) `:78`, the dev row of the IMPORTANT table, says the dev script clears the variable itself since Session 90, and one row is inserted after `:79` for `npm --prefix ui run preview`, still silent, naming `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`. The rest of the admonition (`:70-77`, `:79-83`) is unchanged.

### The Python waits (rows 1 to 3)

1. **Red (row 1).** No file changes. The plugin `slow_worker.py` (this plan folder, loaded with `-p slow_worker` and `PYTHONPATH` set to the plan folder, `AVKIT_SLOW_WORKER_S=6`) patches `WheelServer.fetch` (`test_tts_assets.py:51-65`) and `FakeCaptions.get_transcript` (`tests/unit/test_services.py:1151`, in the YouTube module only) to sleep 6 s before calling the original, and logs `armed <nodeid>` and `delayed <nodeid> <target>`. On the two target tests, a 6 s worker outlives the 5 s waits, so `test_ac_122_8_surrogate_title_survives_real_storage` fails at `:940` and `test_ac_62_16_model_overshoot_is_clipped_not_failed` fails at `:260` (in `_install_spacy`), both by `AssertionError`.
2. **Green (row 2).** The `WORKER_WAIT` edit, written from CRLF text with `newline=""`. The plan-time dry run applied it in memory (`trr90-wait-dryrun.txt`): the TTS definition lands at line 33 and the YouTube one at line 108; the replaced row-0 lines are TTS `[62, 177, 227, 526, 712, 896, 938, 955, 963, 977, 984]` and YouTube `[939]`; the assertion lines changed are `[955, 963, 977, 984]`; every line stays CRLF and none is over 100 characters; `ruff format --check` and `ruff check` pass on the edited TTS text (`trr90-wait-dryrun-ruff.txt`). The same plugin run then passes, with `delayed` lines for both tests.
3. **Load run (row 3).** `load-run.py` waits for the host to be quiet, starts one busy child per CPU until the load reaches 85 %, runs the three files three times under that load, and stops every child it started by its own handle, then checks through a handle that each child's real interpreter is gone (the venv `python.exe` is a launcher; `trr90-load-run-kill-check.txt`).

### The rejection watch (rows 4 and 5)

4. **Red (row 4).** Two new LF test files, written before any harness change: `ui/tests/unit/rejection-watch.test.ts` (AC-6 to AC-8) and `ui/tests/e2e/main-rejection-watch.test.ts` (AC-9 to AC-11).
5. **Green (row 5).** `main-error-watch.cjs` (`REJECTION_WATCH`, `REJECTION_WARNING_LINE`; its header comment names the rejection record too), `electron-env.ts` (`MAIN_REJECTION_MARKER`, `kind?` on `MainErrorRecord`) and `electron-app.ts` (`REJECTION_FAILS_CLOSE`; its header comment at `:1-3` and the launch's doc comment name rejections too). All three are LF and stay LF.

### The dev script (rows 6 and 7)

6. **Red (row 6).** One new LF test file, `ui/tests/unit/dev-script.test.ts` (AC-13, AC-14). The base proofs run on the unchanged dev script: with the variable set, `dev-proof.py` must report `window: no` and exit 1 (AC-15 at base); with it removed, a window and exit 0 (AC-16 at base). Then `npm --prefix ui run build` restores `out/`.
7. **Green (row 7).** `ui/scripts/electron-vite-dev.mjs` (new, LF) and `ui/package.json:16` (CRLF, kept). The two proofs run again, and then the build.

### Registers, `commands.md` and the grouping (row 8)

8. **The three issues** are resolved through `issue-resolve.py`, bound to row 0's register hash, from `C:/Temp/av-kit/test-run-reliability/issue-resolve-set.json`. Each entry holds only `status: "resolved"`, `verification` (`last_checked` 2026-11-17, a `method` naming the receipts, a `result` quoting their summary lines) and `resolution_path`, which starts `Fixed in Session 90 on 2026-11-17 (plan docs/execution/plans/2026-11-17-test-run-reliability): ` and then says:
   - `PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD`: the two files read `WORKER_WAIT_S = 60.0` at their twelve 5-second waits, four assertion lines change only their bound, the slowed-worker Red and Green (rows 1 and 2), three passing runs of the three files that reach the waits at 85 % load (row 3) and `TIME_GUARD`; the other 125 waits of the pattern are left, none having failed (D-1115). Receipts: `trr-py-red.txt`, `trr-py-green.txt`, `trr-wait-check.txt`, `trr-green-two.txt`, `trr-load-run.txt`.
   - `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED`: `REJECTION_WATCH`, `REJECTION_WARNING_LINE` and `REJECTION_FAILS_CLOSE`; three full `test:e2e` runs passed with the watch on and no rejection record; a rejection found later is registered with its stack and never allowlisted. Receipts: `trr-watch-red-unit.txt`, `trr-watch-red-e2e.txt`, `trr-watch-green-unit.txt`, `trr-watch-green-e2e.txt`, `trr-watch-green-e2e-full-1.txt` to `-3.txt`.
   - `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT`: `ui/scripts/electron-vite-dev.mjs` and `ui/package.json:16`; the window proof with the variable set and its control; preview registered as `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` (D-1119). Receipts: `trr-dev-base-set.txt`, `trr-dev-base-unset.txt`, `trr-dev-set.txt`, `trr-dev-unset.txt`, `trr-dev-green-unit.txt`.
9. **The preview issue** is added with `tools/issue_triage.py add` (`open`, low, ui, discovered 2026-11-17):
   - title: `npm run preview opens no window when ELECTRON_RUN_AS_NODE is set in the IDE terminal`;
   - root cause: `electron-vite preview starts Electron through the same startElectron as dev (ui/node_modules/electron-vite/dist/chunks/lib-Dvh2Hokw.js:21, lib-q6ns0vZr.js:220-240), which spawns it with no env, so the ELECTRON_RUN_AS_NODE=1 that VS Code and Cursor terminals set makes electron.exe start as plain Node and no window opens, with no error. Session 90 fixed dev with ui/scripts/electron-vite-dev.mjs and left preview (D-1119).`;
   - blast radius: `Developer machines only: npm --prefix ui run preview from an IDE terminal. Workaround: clear the variable first, or use a terminal opened outside the IDE.`
10. **`commands.md`** (CRLF). Line `:78` becomes the first line below, and the second is inserted after `:79`, so it is the new `:80`:

    ```text
    > | `npm --prefix ui run dev` | Clears it itself since Session 90: `ui/scripts/electron-vite-dev.mjs` removes the variable, prints `electron-vite-dev: cleared ELECTRON_RUN_AS_NODE` and starts `electron-vite dev`, so the window opens. |
    > | `npm --prefix ui run preview` | **Silent**, as `dev` was. Tracked as `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`. |
    ```

11. **Grouping row 90** (`:125`, LF) becomes the line below, in the form of row 89 (`:124`). No other row changes.

    ```text
    | 90 | `test-run-reliability` | — | P3 | executed (Session 90) | `docs/execution/plans/2026-11-17-test-run-reliability/` |
    ```

### Test pins

Each pin is cited by file, line and description (Session 83 RULE-1: no other family's AC ids are copied here as this plan's).

| Pin | What it checks | After this change |
|---|---|---|
| `tests/integration/test_youtube_adapter.py:940`, in `test_ac_122_8_surrogate_title_survives_real_storage` (`:881`) | The transcript job is `Done` after the worker is joined | Unchanged line; the join before it (`:939`) reads `WORKER_WAIT_S` |
| `tests/integration/test_tts_assets.py:260`, in `_install_spacy` (`:255`), and `:305`, `:414`, `:515` | `stack.wait_idle()["state"] == "Idle"` | Unchanged lines; `wait_idle`'s default (`:177`) becomes `WORKER_WAIT_S` |
| `tests/integration/test_tts_voice_packs.py:249`, the `stack` fixture's teardown (`:236`), reached by `test_ac_73_15_legacy_row_reads_not_downloaded_and_load_is_refused` (`:293`) and `test_ac_73_16_redownload_over_a_legacy_row_fetches_v1` (`:311`) | `built.wait_idle()` lets the background spaCy download finish before `sys.path` is restored (no assertion) | Unchanged line in an unchanged file; the default it uses (`test_tts_assets.py:177`) becomes `WORKER_WAIT_S` |
| `tests/integration/test_tts_voice_packs.py:320`, in `test_ac_73_16_redownload_over_a_legacy_row_fetches_v1` | `assert stack.wait_idle()["state"] == "Idle"` | Unchanged line in an unchanged file; the same default becomes `WORKER_WAIT_S`. What it asserts is unchanged; it now waits up to 60 s for `Idle` |
| `test_tts_assets.py:955`, `:977` | `assert gated.entered.wait(5.0)` | **Bound only (`WAITS_NAMED`).** Old: `wait(5.0)`. New: `wait(WORKER_WAIT_S)`. The assertion is the same: the gated generate was entered |
| `test_tts_assets.py:963`, `:984` | `assert tts.wait_idle(5.0) is True` | **Bound only (`WAITS_NAMED`).** Old: `wait_idle(5.0)`. New: `wait_idle(WORKER_WAIT_S)`. The assertion is the same: the TTS service went idle |
| `test_tts_assets.py:964` | `assert gated.released == [True]` (the release wait at `:938` returned before its bound) | Unchanged line; the wait at `:938` reads `WORKER_WAIT_S`, so the list still holds `True` only when the release came |
| `ui/tests/unit/e2e-harness.test.ts:69` ("the watch keeps a process alive on an uncaught exception and logs its full record") and `:112` ("mainErrorRecords keeps every non-empty line, multi-line stacks included") | The exception record and the log reader | Unchanged (`EXCEPTION_WATCH_KEPT`); `mainErrorRecords` is not edited |
| `ui/tests/unit/e2e-harness.test.ts:47`, `:60`, `:121` | `electronEnv`, the single `_electron` launch site, `requireScratchAppData` | Unchanged; the new E2E file loads `electron-app.ts` and never names `_electron` |
| `ui/tests/e2e/electron-harness.test.ts:50` ("the main-error watch is loaded before main") | `__avkitE2eMainErrorWatch` and `listenerCount('uncaughtException') >= 2` | Unchanged |
| `ui/tests/e2e/electron-harness.test.ts:69` and `:97` (an uncaught exception after launch and during startup fails the close) | The close message holds the probe text, a stack line, and the startup file | Unchanged; the new header still precedes the stack |
| `ui/tests/e2e/electron-harness.test.ts:117` ("a launch without a main-process error closes cleanly") | `close()` resolves | Unchanged, and now also proves the real app leaves no unhandled rejection at launch and close (S10 if not) |
| **Every E2E test** (all of `ui/tests/e2e/*.test.ts`): `ui/tests/e2e/electron-app.ts` `checkMainErrors` (`:46-62`), run by the wrapped `close()` of every app that `launchElectron` starts | Old: the close fails when the main process logged an uncaught exception | **New suite-wide pass condition (`REJECTION_FAILS_CLOSE`; approved scope: grouping D-1103, issue `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED`).** New: the close also fails on any unhandled-rejection record, launch to exit, shutdown included. No test file changes. Proved by three full `test:e2e` runs at row 5 with a rejection-record count of 0 in each (AC-12) and by the gate's `ui-electron`; any record is S10 |
| `ui/tests/e2e/capture-inbox.test.ts:403` (W9-7) | stderr holds no `UnhandledPromiseRejectionWarning: Error: backend not ready` | Byte-identical file (AC-12); the regex still sees a rejection through `REJECTION_WARNING_LINE`, and the close now also fails on it |
| `ui/scripts/playwright-with-outputfile.mjs`, `ui/tests/e2e/global-setup.ts` | The E2E entry and the stale-build check | Unchanged |

A test whose wait changes keeps its assertions (grouping §3 Session 90 Gate); the four assertion lines whose bound changes are named above, and the two voice-pack lines that reach the changed default are named though their text doesn't change. The one shared assertion that every E2E test runs, `checkMainErrors`, gains its rejection condition through the suite-wide row above. Any other existing test that fails after Green is S5, an M-7 question, not a fix; an E2E test that fails on `unhandled rejection:` is S10.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| The E2E main-error log (`AVKIT_E2E_MAIN_ERROR_LOG`), one JSON object per line | `main-error-watch.cjs`, read by `mainErrorRecords` in `electron-env.ts` | Exception: `name`, `message`, `stack` (strings). Rejection: `kind: 'rejection'` and the same three strings | No other field; the exception record gets no `kind` |
| The main process's stderr lines | `main-error-watch.cjs` | `[avkit-e2e-main-error] <stack>` (unchanged) and `[avkit-e2e-main-rejection] UnhandledPromiseRejectionWarning: <stack>` | Test-only; the packaged app never loads the watch |
| `electron-vite-dev.mjs` exports | `ui/scripts/electron-vite-dev.mjs` | `devEnv`, `devArgs`, `isEntry`, `exitCodeFor`, `DEV_NOTICE` | Dev tooling only; not bundled into the app |

No API route, OpenAPI document, MCP tool shape, backend service, persisted setting or database schema changes (M-4 kept clear).

### Acceptance Criteria

- **Titles.** Vitest and Playwright titles start `AC-<n> ` (the number, then a space), so `red-check.py --require AC-1` never matches `AC-10`. AC-1 and AC-2 are existing pytest functions, required by function name.
- **New names fail by assertion at Red.** `rejection-watch.test.ts` loads `electron-env.ts` through a dynamic import and AC-6 and AC-7 assert `typeof MAIN_REJECTION_MARKER === 'string'` first; `dev-script.test.ts` asserts `existsSync(SCRIPT)` first and loads the script through a dynamic import. So no Red fails by a missing export or a module-not-found error (Session 52 RULE-4).
- **Guards pass at Red:** AC-8, AC-10 and AC-11. They guard against a Green that changes the exception record, counts a handled rejection, or loses the stderr warning.
- **AC-3, AC-4, AC-5, AC-12 and AC-17 are checks**, not test titles; rows 2, 3, 5 and 8 run them.
- **AC-15 and AC-16 are script proofs** (`dev-proof.py`), run at base in row 6 and after the change in row 7 and in the gate.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1 | pytest | Under `-p slow_worker` with `AVKIT_SLOW_WORKER_S=6`, `tests/integration/test_youtube_adapter.py::test_ac_122_8_surrogate_title_survives_real_storage` fails at row 1 by an `AssertionError` at `:940` and passes at row 2; the plugin log holds a `delayed` line for it in both runs. | Local Canon (`PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD`; grouping §3 Session 90) | In Red the 5 s join returns with the job `Processing` |
| AC-2 | pytest | The same for `tests/integration/test_tts_assets.py::test_ac_62_16_model_overshoot_is_clipped_not_failed`, failing at row 1 by an `AssertionError` at `:260` (in `_install_spacy`). | As AC-1 | In Red `wait_idle` returns after 5 s with the download `Downloading` |
| AC-3 | check | `wait-check.py` passes: no 5-second worker wait is left in either file; `WORKER_WAIT_S = 60.0` is defined once per file and used 11 times (TTS) and once (YouTube); the diff against row 0 holds only the `CONSTANT_BLOCK` insert after the anchor and the one-for-one replaced lines; the assertion lines changed are exactly TTS `:955`, `:963`, `:977`, `:984`; every line is CRLF. | Local Canon (`WORKER_WAIT`, `WAITS_NAMED`, `WAIT_SIGNALS_KEPT`; grouping §3 Gate) | A sixth changed assertion, a sleep, a missed literal or a bare LF fails it |
| AC-4 | check | `TIME_GUARD`: the plain run of the three files at row 2 (`trr-green-two.txt`: `test_tts_assets.py`, `test_youtube_adapter.py`, `test_tts_voice_packs.py`; no plugin) passes and its wall time is at most the row-0 time of the same three files (`trr-base-two.txt`) plus 30 s. | Local Canon (`TIME_GUARD`) | A wait that now runs to 60 s on a passing test pushes the time over |
| AC-5 | check | `load-run.py` passes: the load reached 85 % before the runs, all three runs of the three files passed, the median load sampled during the runs is at least 85 %, and it reports `busy children left: 0` and `busy interpreters left: 0`. | Local Canon (the issue's "under load"; Session 81 RULE-2) | A run that fails under load, or a load below 85 %, fails it |
| AC-6 | unit | `ui/tests/unit/rejection-watch.test.ts` (`// @vitest-environment node`): a child `process.execPath --unhandled-rejections=warn-with-error-code -r <MAIN_ERROR_WATCH> <tmp>/rejector.cjs`, with the log variable set, where `rejector.cjs` rejects `new Error('avkit-ac6-probe')` unhandled and prints `alive` after 50 ms: the child exits 0 with `alive` on stdout; stderr holds `MAIN_REJECTION_MARKER` and `UnhandledPromiseRejectionWarning: Error: avkit-ac6-probe`; the log holds exactly one record, `{ kind: 'rejection', name: 'Error', message: 'avkit-ac6-probe', stack }`, whose `stack` contains `rejector.cjs` and a newline followed by four spaces and `at `. | Local Canon (`REJECTION_WATCH`, `REJECTION_WARNING_LINE`; the issue's next step) | In Red the child exits 1 and the log is empty |
| AC-7 | unit | The same child with `Promise.reject('avkit-ac7-text')`: one record with `kind: 'rejection'`, `name: 'string'`, and `message` and `stack` both `'avkit-ac7-text'`. | Local Canon (`REJECTION_WATCH`) | In Red the log is empty |
| AC-8 | unit (guard) | The same child shape with an uncaught `new Error('avkit-ac8-probe')` thrown from a timer: the record's keys are exactly `name`, `message`, `stack` (no `kind`), and stderr holds `[avkit-e2e-main-error] Error: avkit-ac8-probe`. Passes at Red. | Local Canon (`EXCEPTION_WATCH_KEPT`) | A Green that adds `kind` to exceptions or drops the old marker fails it |
| AC-9 | E2E | `ui/tests/e2e/main-rejection-watch.test.ts` (loads `electron-app.ts` dynamically, as `electron-harness.test.ts:16-21` does; never names `_electron`): a fresh app with a scratch `AVKIT_APP_DATA`; after `firstWindow()`, `app.evaluate` schedules `setTimeout(() => { void Promise.reject(new Error('avkit-e2e-rejection-probe')) })`; a loop of `app.evaluate` calls reads `globalThis.__avkitE2eMainRejections?.length ?? 0` every 10 ms for up to 5 s; `expect(count).toBe(1)`; the child's `exitCode` is `null`; then `close()` rejects with an `Error` whose message contains `unhandled rejection: Error: avkit-e2e-rejection-probe` and matches a newline, spaces and `at `. | Local Canon (`REJECTION_FAILS_CLOSE`; the issue) | In Red the count stays 0 and the test fails by assertion |
| AC-10 | E2E (guard) | The same app with `const p = Promise.reject(new Error('avkit-e2e-handled')); p.catch(() => undefined)` in the timer: after 1 s the count is 0 and `close()` resolves. Passes at Red. | Local Canon (`REJECTION_FAILS_CLOSE`: a handled rejection leaves no record) | A watch that records handled rejections fails it |
| AC-11 | E2E (guard) | The same unhandled rejection as AC-9 with the child's stderr collected from launch: within 30 s stderr holds `UnhandledPromiseRejectionWarning: Error: avkit-e2e-rejection-probe`; `close()` is then awaited with its error caught. Passes at Red (Electron's own warning) and at Green (`REJECTION_WARNING_LINE`). | Local Canon (D-1117; W9-7, `capture-inbox.test.ts:403`) | A listener without the compatibility line fails it |
| AC-12 | check | The full `npm --prefix ui run test:e2e` runs three times at row 5 with the watch on (`trr-watch-green-e2e-full-1.txt` to `-3.txt`); each run passes, and each run's rejection-record count (receipt lines containing `unhandled rejection:`) is printed and is 0; `capture-inbox.test.ts` is byte-identical to row 0. | Local Canon (`EXCEPTION_WATCH_KEPT`, the suite-wide pin row, D-1116; S10) | An existing test that leaves a rejection, even one only at shutdown and only in some runs, fails here (S10) |
| AC-13 | unit | `ui/tests/unit/dev-script.test.ts` (`// @vitest-environment node`): `devEnv({ ELECTRON_RUN_AS_NODE: '1', electron_run_as_node: '1', PATH: 'p' })` returns `env` with only `PATH`, and `cleared: true`; the base object still has its three keys; `devEnv({ PATH: 'p' })` returns `cleared: false`; `DEV_NOTICE` is exactly `'electron-vite-dev: cleared ELECTRON_RUN_AS_NODE'`. | Local Canon (`DEV_ENV_CLEARED`, `DEV_NOTICE`; the issue's workaround) | In Red the script does not exist |
| AC-14 | unit | `devArgs(['--x'])` is `[<path>, 'dev', '--x']` with `<path>` existing and ending in `electron-vite/bin/electron-vite.js`; `isEntry(SCRIPT, url)` is true, also with the path upper-cased on win32, and false for another file and for `undefined`; `exitCodeFor(0, null)` is 0 and `exitCodeFor(3, null)` is 3; `exitCodeFor(null, 'SIGTERM', 'win32')` and `exitCodeFor(null, null, 'win32')` are 1; `exitCodeFor(null, 'SIGINT', 'linux')` is 130 and `exitCodeFor(null, null, 'linux')` is 1; `ui/package.json`'s `scripts.dev` is `node ./scripts/electron-vite-dev.mjs` and `scripts.preview` is `electron-vite preview`. | Local Canon (`DEV_ARGS`, `DEV_SIGNALS`, `DEV_ENTRY_ONLY`, `DEV_SCRIPT`) | In Red the script does not exist and `scripts.dev` is `electron-vite dev` |
| AC-15 | proof | `dev-proof.py --run-as-node set --expect window --expect-notice yes` exits 0 with `window: yes`, `notice: yes` and `left: 0` after row 7; at base (row 6) it exits 1 with `window: no`. | Local Canon (`UI-DEV-ELECTRON-RUN-AS-NODE-SILENT`; D-1120) | At base no window opens |
| AC-16 | proof (control) | `dev-proof.py --run-as-node unset --expect window --expect-notice no` exits 0 with `window: yes`, `notice: no` and `left: 0`, at base (row 6) and after row 7. | Local Canon (D-1120: the proof can see a window) | A proof that cannot see a window fails here, at base |
| AC-17 | check | The three issues are `resolved` with `verification` and `resolution_path` and no `meu_links`; `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` is present once, `open`, low, ui, discovered 2026-11-17; `issue_triage.py render` and `render --check` pass; grouping row 90 reads `executed (Session 90)` with this plan folder; `commands.md` has the new dev row at `:78` and the preview row at `:80`, and stays CRLF. | Local Canon (D-1103, D-1119; `COMMANDS_DOC`) | A missing row or a changed line ending fails it |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| How long a test waits for its worker | Local Canon | Up to 60 s, returning on the signal, in the two failing files (D-1115) |
| Which assertions may change | Local Canon | Only the bound inside four named assertions (grouping §3 Gate; `WAITS_NAMED`) |
| How the flake is reproduced | Local Canon | A plugin delays the fake worker past 5 s; a load run proves three passes at 85 % (D-1120) |
| What the watch does with a rejection | Local Canon | Records it, fails the close with its stack, and keeps a warning line on stderr (D-1116, D-1117; the issue's next step) |
| How dev clears the variable | Local Canon | A wrapper script removes it and starts electron-vite (D-1118) |
| Preview | Local Canon | Registered, not fixed (D-1119) |
| How the behaviour is proved | Human-approved | Scripts and tests in the gate (Mat 2026-11-16); design D-1120 |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `tests/integration/test_tts_assets.py` | modify | CRLF, kept | `WORKER_WAIT`: the block after `:30` and eleven waits |
| `tests/integration/test_youtube_adapter.py` | modify | CRLF, kept | `WORKER_WAIT`: the block after `:105` and the join at `:939` |
| `ui/tests/e2e/main-error-watch.cjs` | modify | LF, kept | `REJECTION_WATCH`, `REJECTION_WARNING_LINE` |
| `ui/tests/e2e/electron-env.ts` | modify | LF, kept | `MAIN_REJECTION_MARKER`; `kind?` on `MainErrorRecord` |
| `ui/tests/e2e/electron-app.ts` | modify | LF, kept | `REJECTION_FAILS_CLOSE` |
| `ui/package.json` | modify | CRLF, kept | `:16` only (`DEV_SCRIPT`) |
| `ui/scripts/electron-vite-dev.mjs` | new | LF | `DEV_ENV_CLEARED`, `DEV_NOTICE`, `DEV_ARGS`, `DEV_SIGNALS`, `DEV_ENTRY_ONLY` |
| `ui/tests/unit/rejection-watch.test.ts` | new | LF | AC-6 to AC-8 |
| `ui/tests/unit/dev-script.test.ts` | new | LF | AC-13, AC-14 |
| `ui/tests/e2e/main-rejection-watch.test.ts` | new | LF | AC-9 to AC-11 |
| `.agent/docs/commands.md` | modify | CRLF, kept | `COMMANDS_DOC`: `:78` rewritten, one row inserted after `:79` |
| `.agent/context/known-issues.yaml` | modify (script, tool) | LF, kept | Row 8: three issues resolved; `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` added, `open` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md` | modify | LF, kept | Row 90 (`:125`) only: `executed (Session 90)` and this plan folder |

**Line endings** were measured with Python bytes (`trr90-probe.txt`, at `HEAD` `79e3fa5`). CRLF: the two Python test files, `test_tts_voice_packs.py` (338 lines, read only), `ui/package.json`, `commands.md`, `playwright-with-outputfile.mjs`, `tests/unit/test_services.py`, `tests/conftest.py`, and the state files `current-focus.md` and `metrics.md`. LF: `main-error-watch.cjs`, `electron-env.ts`, `electron-app.ts`, `e2e-harness.test.ts`, `electron-harness.test.ts`, `capture-inbox.test.ts`, the registers, the generated file, the grouping and the four new files. A CRLF file is read and written with `newline=""` from CRLF text. `eol-check.py` checks every scope path in rows 2, 5 and 7 and in the gate. A new LF file is written as bytes and its CR count checked (Session 83 RULE-3).

### Project files

- **Plan-local scripts**, all in this plan folder:
  - written at plan time: `slow_worker.py` (the pytest plugin), `wait-check.py` (AC-3), `load-run.py` (AC-5) and `dev-proof.py` (AC-15, AC-16), each with a `--selftest` where it has logic to test (`trr90-selftest-*.txt`: 0 failures each);
  - written in row 0: `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py`, copied in shape from `2026-11-17-queue-convert-fixes/`;
  - written in H1-2: `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`.
- **Read, never changed (bound in `baseline-scope.json`):** `ui/tests/e2e/capture-inbox.test.ts`, `ui/tests/unit/e2e-harness.test.ts`, `ui/tests/e2e/electron-harness.test.ts`, `ui/scripts/playwright-with-outputfile.mjs`, `ui/tests/e2e/global-setup.ts`, `tests/unit/test_services.py`, `tests/conftest.py`, `tests/integration/test_tts_voice_packs.py` (CRLF), `docs/execution/plans/2026-11-15-convert-settings-drafts/dev-app-procs.py`, `ui/src/main/index.ts`, `ui/electron.vite.config.ts`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `known-issues.yaml`, `known-issues.md` | Any triage session | `issue-resolve.py` changes only the three named issues and binds to a hash (S4); row 8 adds one issue through `issue_triage.py add` |
| Grouping §6 table | None queued after Session 90 | Only row 90 changes |
| `ui/tests/e2e/` harness files | Every Electron spec launches through them | Their tests and the full `test:e2e` run in row 5 and the gate |
| `commands.md` | Any session that edits commands | Only `:78` and the inserted row |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| The other 125 five-second waits in 27 files (`trr90-wait-sweep.txt`) | out-of-scope | — | D-1115: none has failed in a recorded run; a sweep is a different change |
| `npm run preview` with the variable set | out-of-scope (registered) | — | D-1119: row 8 registers `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` |
| Excusing an existing E2E test that leaves a rejection | out-of-scope | — | D-1116 and S10: never allowlisted; stop for Mat (D-1121 reserved) |
| `commands.md:79` (the stale `test:e2e` row) and `:81-83` (the `E2E-ELECTRON-LAUNCH-FLAG` text) | out-of-scope | — | Not this session's issues; only the dev row and a preview row change |
| Changing Electron's or Node's unhandled-rejections mode in the app | out-of-scope | — | M-4: product behaviour; the watch is test-only |
| A `sleep` or retry in any test | out-of-scope | — | `WAIT_SIGNALS_KEPT` |

## BUILD_PLAN.md Audit

This session has no MEU, so `meu-status.yaml`, `meu-registry.md` and `docs/BUILD_PLAN.md` don't change. H1-3 confirms the render:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/test-run-reliability/trr-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/test-run-reliability/trr-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` follows `2026-11-17-queue-convert-fixes/baseline.ps1`:

1. **Tree state.** `baseline.sha` (`HEAD`) and `baseline-dirty.txt` (`git status --porcelain --untracked-files=all`).
2. **Path-scoped baseline, bound to content.**
   - `baseline-scope.json`: the SHA-256 of each §Files Modified path and each §Project files "Read, never changed" path, or `absent`; the four new files must be `absent`.
   - `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`.
   - `baseline-eol.json`: for each scope path, its kind (`CRLF`, `LF`, `MIXED`), its CRLF and bare-LF counts.
   - `baseline-skip-hashes.json`: the SHA-256 of every tracked or untracked, not-ignored file under `packages/`, `mcp-server/` and `tools/`; at the gate none may differ, and none may be added or removed (H1-4).
   - A copy of each scope file's bytes under `C:/Temp/av-kit/test-run-reliability/baseline-copies/<path>`, which `wait-check.py`, `eol-check.py` and AC-12 compare against.
   - The S2 binding: the `trr90-probe.txt` anchors each counted once (the eleven TTS waits and the YouTube join at their lines, the two anchor lines, `process.on('uncaughtException'` in the watch, the close header in `electron-app.ts`, the dev and preview lines in `package.json`, W9-7's regex in `capture-inbox.test.ts`), `unhandledRejection` absent from the watch, the three issues `open`, `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` absent, and grouping row 90 `proposed`.
3. **Base receipts.** The host-load wait (Session 81 RULE-2) runs first. Then: the full Vitest run (`trr-base-ui.txt`, pwsh in `ui/`); the full Python suite with the D6 argv without `-x` (`trr-base-py.txt`); and a timed plain run of the three `TIME_GUARD` files (`trr-base-two.txt`, with the wall time on its last line). Failures in the first two are recorded, not fatal, and the gate excuses only those ids (the Session 49b baseline rule); `trr-base-two.txt` must pass.
4. **Plan-local scripts.**
   - `red-check.py` and `identity.py` are copied from `2026-11-17-queue-convert-fixes/` with this plan's `PLAN`, `PROJECT_ARTIFACTS` (the handoff, the reviews, the reflection, `metrics.md`, `current-focus.md`) and `DECLARED_NEW` (`devEnv`, `devArgs`, `isEntry`, `exitCodeFor`, `DEV_NOTICE`, `MAIN_REJECTION_MARKER`); `red-check.py`'s boundary fixtures are renamed so that `AC-1` is checked against `AC-10` to `AC-17`. Its pytest reading keeps a `PytestUnhandledThreadExceptionWarning` in the warnings summary as neither a failure nor a setup failure (the YouTube Red's slowed worker runs on past `:940` into the next test), with a selftest fixture that holds one beside a `2 failed` summary. `identity.py` clears `ELECTRON_RUN_AS_NODE` (Session 88 RULE-3), and its other-plan skip covers untracked `docs/execution/plans/2026-11-1[5-7]-<slug>/` folders other than this one.
   - `issue-resolve.py` is copied with `SCRATCH` at `C:/Temp/av-kit/test-run-reliability/issue-resolve`; `RESOLVE_KEYS` is `status`, `verification` and `resolution_path` (no `meu_links`: no MEU).
   - `eol-check.py` is copied with this plan's scope and `baseline-copies/`.
   - The `red-check.py`, `identity.py`, `eol-check.py`, `wait-check.py`, `load-run.py` and `dev-proof.py` selftests run, and `ruff format --check` and `ruff check` run on the plan folder's Python (Session 82 RULE-1).
5. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read (Session 83 RULE-2). `dev-proof.py` never opens a file in its scratch app data, which holds an `mcp-token.txt`.

If any step except the first two base receipts fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names `test_ac_122_8_surrogate_title_survives_real_storage` and `test_ac_62_16_model_overshoot_is_clipped_not_failed` (row 1, pytest), AC-6 and AC-7 (row 4, Vitest), AC-9 (row 4, Playwright) and AC-13 and AC-14 (row 6, Vitest). Row 1 also checks the plugin log has a `delayed` line for each target, that each failure is an `AssertionError` at `:940` or `:260` (for the YouTube target only the `:940` assertion counts), and that the pytest summary reads `2 failed` with no `error`. A thread-exception warning from the worker that outlives the YouTube test is not a setup failure.
- **Guards pass at Red:** row 4 checks that no failure line names `AC-8 `, that the Vitest `Tests` line reads `2 failed | 1 passed`, and that the Playwright receipt has an `ok` line for AC-10 and AC-11 (count pattern `^ +ok +[0-9]+ `, Session 89 RULE-1).
- **Expectations stay immutable in Green** (S3). Rows 4 and 6 record the hashes of the test files they write; rows 5 and 7 check them. Row 2 changes no expectation other than the four named bounds (`wait-check.py`).
- **Line endings** are checked by `eol-check.py` after each Green.

### 3. Load and dev proofs (rows 3, 6 and 7)

- **`load-run.py`** (row 3, AC-5): the host-load wait; one busy child per CPU until the load reaches 85 % within 60 s (else exit 2, S8); each child prints its interpreter's `os.getpid()` before it spins, and the script holds a handle to that interpreter (the venv `python.exe` is a launcher whose child is the real interpreter, `tr90-ep-launcher-probe.txt`), kept only when the id, parent id and creation time read through that handle show the launcher itself or a child of the launcher created no earlier than it (a reused id is refused, exit 2, and never terminated); three runs of `python -m pytest -q --tb=short -p no:cacheprovider` on the three `TIME_GUARD` files, each into `trr-load-run-<i>.txt`, with the load sampled about every 3 s, and a run over 1800 s ends as code 124; in a `finally` every launcher is killed by its own handle, then each interpreter is waited on for up to 10 s and stopped through its own handle if still running; it prints `busy children left: 0`, `busy interpreters still running after the launcher kill: N` and `busy interpreters left: 0`. Exit 0 needs all three runs passing, a median sample of at least 85 % and nothing left. The stop was checked at plan time with `--kill-check --children 2` (`trr90-load-run-kill-check.txt`: 2 interpreters, none the launcher itself; 0 still running after the launcher kill; 0 left).
- **`dev-proof.py`** (rows 6 and 7, the gate; AC-15, AC-16): first the host-load wait, imported from `load-run.py` (a first run's Vite compile counts against the 180 s, `index.ts:490`, `:526`); then a preflight waits up to 600 s while another av-kit dev app could hold the `av-kit-ui` lock, then exits 2 (S11). Such an app is an Electron main process (no `--type=`, not an MCP server, not an E2E launch) whose executable is under an av-kit `ui/node_modules/electron/dist/`, in `P:/av-kit` or a `P:/av-kit-wt/<name>` worktree; other projects' Electron apps, such as a zorivest lane app, use another lock and are ignored. Each preflight line prints `foreign av-kit dev apps: N; other Electron main processes (ignored): M`. The launch runs `cmd.exe /d /c npm --prefix ui run dev` from `P:/av-kit` with `CREATE_NO_WINDOW`, `AVKIT_E2E` removed and `AVKIT_APP_DATA` in a scratch folder; once a second it snapshots the process tree with Session 81's `dev-app-procs.py` (loaded after its SHA-256 prefix `03053bc97a32` is checked), and looks for a visible, titled top-level window of class `Chrome_WidgetWin_1` owned by an Electron process of the launch (`EnumWindows`, `GetClassNameW`; a native error dialog, class `#32770`, never counts). Each process enters the record once, as (id, creation time), and that entry never changes; a later holder of a recorded id (another creation time) is left out of the record and the tree, so its window can't pass and `--stop` can't pick it, and a window counts only if its owner keeps its recorded identity in a fresh snapshot after the windows were listed. The root must be the script's own child, started after the launch began. It stops at a window, the launch ending, or 180 s; then `dev-app-procs.py check --record R --stop` stops the recorded tree, and the script checks for up to 30 s that none of it is left. It prints `window:`, `notice:` and `left:` and exits 0 when the window and notice match the expectation and nothing is left.
- **After each dev proof** `npm --prefix ui run build` runs before any Electron test (the stale-build check, `global-setup.ts:40-47`).

### Session gate (H1-2)

`session-gate.ps1` follows `2026-11-17-queue-convert-fixes/session-gate.ps1`: one receipt per step in `C:/Temp/av-kit/test-run-reliability/`, named `trr-D6-<step>`; fail-fast, with later steps printed as `not_run`; the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content); `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `red-check-selftest`, `eol-check-selftest`, `wait-check-selftest`, `load-run-selftest`, `dev-proof-selftest`; `py-format` (`ruff format --check` on the TTS file and this plan folder's Python; the YouTube file is not format-clean at base, `trr90-ruff-base.txt`); `py-lint` (`ruff check` on both test files and this plan folder's Python); `dev-script-syntax` (`node --check ui/scripts/electron-vite-dev.mjs`) |
| Targeted | `py-two` (the three `TIME_GUARD` files, plain); `wait-check`; `ui-unit` (`rejection-watch.test.ts`, `dev-script.test.ts`, `e2e-harness.test.ts`) |
| Host load | `host-load`: samples `Win32_Processor.LoadPercentage` five times; above 60 % it waits, re-sampling every 30 s for up to 10 minutes, and records the value it ran at (Session 81 RULE-2). It never fails the gate |
| Runtime | `dev-proof-set` (`dev-proof.py --run-as-node set --expect window --expect-notice yes`), before `ui-build` |
| Fresh full | `py-tests` (the D6 argv); `ui-tests` (full Vitest); `ui-build`; `ui-electron` (the full `test:e2e`); `issues-render-check` (`issue_triage.py render --check`); `state-render` (`meu_status.py render --check`) |
| Skipped, with reason | `py-types`, `openapi`, `mcp-*`: every file under `packages/`, `mcp-server/` and `tools/` keeps its `baseline-skip-hashes.json` hash, and none was added or removed (H1-4) |

`ui-tests` excuses only ids that `trr-base-ui.txt` shows failing. If `py-tests` stops on an id that `trr-base-py.txt` shows failing, the step runs the D6 argv again without `-x` and passes when its failures are a subset of the base ids.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a `trr90-probe.txt` anchor missing or counted twice, `unhandledRejection` in the watch, an issue not `open`, the preview issue present, or row 90 not `proposed` | Stop; another session moved this ground. Bring the probe to Mat |
| S3 | A Red receipt fails `red-check.py` (including a Red that passes on old code, a module-not-found error or a collection error), a guard fails at Red, or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, a `baseline-dirty.txt` path changes content, or `known-issues.yaml` lacks its expected hash when `issue-resolve.py` runs | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test fails after Green (M-7) | Stop: an M-7 question, not a fix. An Electron failure that holds no rejection record is first rerun once alone; only a repeat failure stops. A failure on `unhandled rejection:` is S10 |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | Row 1's plugin log has no `delayed` line for a target, or a target fails somewhere other than `:940` or `:260`, or by anything other than an `AssertionError` | Stop and route back to the plan: the Red does not reproduce the issue |
| S8 | `load-run.py` cannot reach 85 % (exit 2), or a run fails under load | Rerun once; if it fails again, stop and bring the receipts to Mat. Never lower the threshold or raise `WORKER_WAIT_S` past 60 s to pass |
| S9 | `TIME_GUARD` is exceeded | Rerun the timed run once after the host-load wait; if it is still over, stop and route back (a wait is running to its bound). A hung worker now costs up to 55 s more per changed wait its test reaches (D-1115), so a slow run, not a quick failure, is how a real hang shows |
| S10 | Any rejection record (a receipt line containing `unhandled rejection:`) in any of the three full `test:e2e` runs at row 5, in a rerun, or in the gate's `ui-electron` | Stop at the first record. Never rerun it away, allowlist it or catch it in the watch; bring the record and its stack to Mat as D-1121 (fix the source, or keep the watch report-only). The S5 rerun-once rule does not apply to a rejection record |
| S11 | `dev-proof.py` exits 2: another av-kit dev app holds the lock for 600 s, or the launch could not start | Stop and tell Mat which process holds it; never stop a process the script didn't start |
| S12 | The base proofs don't discriminate: at row 6 the `set` proof opens a window, or the `unset` control does not | Stop and route back: the proof cannot show the fix |
| S13 | A file under `packages/`, `mcp-server/` or `tools/` changes | Stop: this session changes no product, API or tool file |

## Decision Log

> [!NOTE]
> D-1116, D-1117, D-1119 and D-1120 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-1115 hit M-3 and M-8, and D-1118 hit M-5 and M-8, so they are briefs (below). No other M item is hit: no API, OpenAPI or MCP change (M-4 clear), no user data written (M-2 clear), and the four assertion lines whose bound changes are named with their files, lines, old and new text in §Test pins, with what each asserts unchanged (M-7 clear). D-1116's §4a check considered M-7, since `REJECTION_FAILS_CLOSE` adds a pass condition to the shared close that every existing E2E test runs: it is answered by the named suite-wide row in §Test pins (`electron-app.ts` `checkMainErrors`, its old and new condition), a row of this plan that names the tests and the new assertion, within the approved scope of grouping D-1103 for `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED`, so D-1116 stays `mandatory: none`. The two `test_tts_voice_packs.py` lines that reach D-1115's changed default are named there too. Mat's hand-over covers M-3, M-5, M-6 and M-8 briefs (HDP §6), so the two are recorded `autonomous` with their `mandatory:` lists kept; `open_decisions` is empty and there is no STOP item. D-1121 is reserved for S10, which would go to Mat; D-1122 to D-1124 are left free for execution.
>
> **Why Session 90 is inside the hand-over.** Mat's 2026-11-17 message asked for the triage, the grouping and then "continue planning and executing as orchestrator" (grouping §8 D-1102), continuing his 2026-11-15 hand-over ('like we did here. But use the new HDP process.'), and Session 90 is §3 of that grouping (this plan's `grouping_source`). That message is dated 2026-11-17, the same day as this brief set, so the hand-over is not carried from an earlier brief set (HDP §6 scopes a hand-over to one brief set), and `plan_to_exec_gate: human` puts the briefs in front of Mat again before execution. Each handed brief's reasoning starts with the same sentence, word for word: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'."
>
> **Earlier rows are not copied here.** The grouping rows D-1102 to D-1104 live in the grouping file's §8; the three issues hold no decision rows of their own. H2-2 reads them through `--decision-source` on the grouping and on `.agent/context/known-issues.yaml`, with `--decision-issue` for each of the three issues. `decision_sources` was probed at plan time (`trr90-probe.txt`): the grouping alone gives D-1102 to D-1104, and with the register and the three issues it gives the same three. Under HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices.

```yaml
decision_log:
  - id: D-1115
    stage: planning
    question: "Which five-second waits become longer, and by how much?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-3, M-8]
    chosen: "A: WORKER_WAIT_S = 60.0 is defined once in each of the two failing files and every 5-second worker wait there reads it: eleven in test_tts_assets.py, one in test_youtube_adapter.py. Each wait still returns on its signal; four assertion lines change only their bound (WAITS_NAMED); the wait_idle default also reaches two tests in test_tts_voice_packs.py (:249, :320), which is read and never changed; TIME_GUARD keeps a plain run of the three files within 30 s of its row-0 time."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:5428 — the two failures under load, each at a 5-second bound, and Session 81 D-1068 (both passed alone)"
      - ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md:89-99 — Session 90 order and gate: a test whose wait changes keeps its assertions"
      - "tests/integration/test_tts_assets.py:177 — wait_idle's 5.0 default, reached by 21 tests: 19 in the file and 2 in tests/integration/test_tts_voice_packs.py (:249, :320)"
      - "tests/integration/test_youtube_adapter.py:939-940 — the join and the Done assertion"
      - "C:/Temp/av-kit/test-run-reliability/trr90-wait-sweep.txt — 137 sites in 29 files, 12 of them in the two failing files"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-3 because how long a test may wait is a preference about suite time against flakiness; M-8 because it reaches beyond the two failing lines to every 5-second wait in their files. The waits return on their signal, so a longer bound costs time only when a test would have failed anyway. The two failing paths alone (B) leave ten waits in the same files with the same fault, two of them shared helpers. A sweep of all 137 sites (C) touches 29 files with no recorded failure. 60 s is twelve times the old bound; the plugin's 6 s delay and the load run at 85 % show it holds, and TIME_GUARD shows passing tests don't run to it. The cost of a real hang: there is no pytest-timeout, so a hung worker still fails its test, but up to 55 s later per changed wait the test reaches. The deepest test (test_ac_77_10_generate_returns_generating_then_cancel_reaches_cancelled) reaches 5 of the 12 lines, and a wait_idle line can be passed more than once, so one hung test can cost several minutes; the unasserted waits (:227, :548, :566, :627, :712, :839, :845-846, :1024) also run to 60 s before the assertion after them fails. The load run's --run-timeout of 1800 s ends a hung run as code 124 (a failure), and the gate's py-tests runs with -x, so the first hung test stops it. Two-way: one constant per file."
  - id: D-1116
    stage: planning
    question: "What does the E2E watch do with an unhandled rejection in the main process?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "REJECTION_WATCH and REJECTION_FAILS_CLOSE: main-error-watch.cjs adds an unhandledRejection listener that records { kind: 'rejection', name, message, stack } in the same log and in globalThis.__avkitE2eMainRejections, and the wrapped close fails on any record, prefixing a rejection with 'unhandled rejection: '. Every rejection fails the close; none is allowlisted. It is a new pass condition on every existing E2E test, named as one suite-wide row in Test pins (electron-app.ts checkMainErrors) within grouping D-1103's approved scope; three full test:e2e runs at row 5 each show a rejection-record count of 0 (AC-12). Any record in Session 90 is S10, brought to Mat as D-1121. A rejection found after Session 90 is registered in known-issues with its stack and is never allowlisted."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:5354 — the issue's next step: append unhandledRejection events to the same log"
      - "ui/tests/e2e/main-error-watch.cjs:16 — the uncaughtException listener and its record"
      - "ui/tests/e2e/electron-app.ts:46-62 — checkMainErrors fails the close on any record; it runs after close() and a 5 s exit wait"
      - ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md §8 D-1103 — E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED is in Session 90's scope"
      - "C:/Temp/av-kit/test-run-reliability/trr90-electron-rejection-probe.txt — Electron keeps a rejection as a warning; a listener sees it"
    research: { engine: none, sources: [] }
    reasoning: "The issue names the mechanism, and the exception watch is its model: the same log, the same close. A report-only watch would leave the gap the issue describes, since a warning on stderr never fails a test. An allowlist would hide exactly the rejections the watch is for. If the full suite shows a real rejection today, that is a product finding, not a harness choice, so it stops for Mat. checkMainErrors reads after close() and a 5 s exit wait, so a rejection during shutdown counts, and one may show only in some runs; one passing run cannot rule that out, so row 5 runs the suite three times and S10 fires on any record in any run. A later sighting goes to known-issues with its stack rather than an allowlist, so the watch keeps meaning what it says. M-7 was considered: the new condition is on a shared assertion that every E2E test runs, and the suite-wide Test pins row names it, which HDP §4a accepts as an approved plan row. Two-way: one listener and one prefix."
  - id: D-1117
    stage: planning
    question: "The new listener silences Electron's own warning; how does a test that reads stderr keep working?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "REJECTION_WARNING_LINE: the listener writes '[avkit-e2e-main-rejection] UnhandledPromiseRejectionWarning: ' and the rejection's stack to stderr, so a regex for 'UnhandledPromiseRejectionWarning: Error: ' and the rejection's message still matches; capture-inbox.test.ts stays byte-identical."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/capture-inbox.test.ts:403 — W9-7 reads stderr for a 'backend not ready' rejection warning"
      - "C:/Temp/av-kit/test-run-reliability/trr90-electron-rejection-probe.txt — with a listener nothing is printed"
      - "ui/tests/e2e/main-error-watch.cjs:24 — the exception watch writes its own marker line the same way"
    research: { engine: none, sources: [] }
    reasoning: "Without the line, W9-7 would pass whether or not the rejection happened, which turns a guard into a no-op. Editing W9-7 instead would change an existing test (M-7) for a harness change. The line costs nothing and the close now fails on the same rejection too. Two-way: one write."
  - id: D-1118
    stage: planning
    question: "How should npm run dev clear ELECTRON_RUN_AS_NODE?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5, M-8]
    chosen: "A: ui/scripts/electron-vite-dev.mjs removes the variable from a copy of the environment (any case), prints 'electron-vite-dev: cleared ELECTRON_RUN_AS_NODE' when it did, and starts electron-vite's own bin with 'dev' under the same Node; ui/package.json:16 runs it. Its functions are exported and tested; the spawn runs only when it is the entry. While the child runs it ignores SIGINT and SIGBREAK (the child gets the console's Ctrl+C itself), forwards SIGTERM, and exits only from the child's exit with exitCodeFor(code, signal), which is code ?? 1 on win32 and never re-raises a signal (DEV_SIGNALS)."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:5344 — the issue and its workaround: clear the variable first"
      - "ui/node_modules/electron-vite/dist/chunks/lib-q6ns0vZr.js:220-240 — startElectron spawns with no env, so the child inherits the variable"
      - "ui/tests/e2e/electron-env.ts — electronEnv drops the variable for the E2E launch (Session 78)"
      - ".agent/docs/commands.md:70-83 — the IMPORTANT admonition and its dev row"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-5 because it picks a mechanism among several workable ones; M-8 because it adds a script to the UI package. A wrapper changes only the dev command and uses electron-vite's public bin. A line in electron.vite.config.ts (B) depends on the config being loaded in the same process before the spawn, which is an internal detail; build also loads the config; and a config edit makes the E2E stale-build check refuse out/ until a rebuild. Refusing with a message (C) still leaves the developer to clear it. Two-way: one script and one package line."
  - id: D-1119
    stage: planning
    question: "npm run preview has the same gap; is it fixed here?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Registered, not fixed: row 8 adds UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT (open, low, ui, discovered 2026-11-17), and commands.md gets a preview row naming it. package.json:18 is unchanged."
    source_tag: Local Canon
    precedents:
      - "ui/node_modules/electron-vite/dist/chunks/lib-Dvh2Hokw.js:21 — preview calls the same startElectron"
      - "docs/execution/plans/2026-11-17-queue-convert-fixes/implementation-plan.md — D-1109 registered the one other gap it found and did not fix it"
      - "docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md — D-939 moved the dev gap to its own issue instead of widening Session 78"
    research: { engine: none, sources: [] }
    reasoning: "The issue and the grouping name dev only. Options: A, register it (chosen). B, the cheaper fix: the same wrapper takes a dev|preview argument and package.json:18 runs it with preview; it is a small change, but it widens the session past its three issues, and preview needs its own window proof against a built app and its own Red. C, leave it unrecorded. Recording the gap keeps it visible at no risk, and the next triage can group B. Two-way: one register row."
  - id: D-1120
    stage: planning
    question: "How do scripts prove the three fixes without a manual check?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The Python Red and Green run the two target tests under a pytest plugin that delays the fake worker 6 s (slow_worker.py); load-run.py runs the three TIME_GUARD files three times with every CPU busy to at least 85 %; the watch is proved by a Node child in Vitest and a real Electron app in Playwright; dev-proof.py runs the host-load wait, waits out only another av-kit dev app that would hold the single-instance lock (an executable under an av-kit ui/node_modules/electron/dist/; other projects' Electron apps are counted and ignored), starts npm run dev with the variable set and removed, looks for a visible titled window of class Chrome_WidgetWin_1 owned by the launch's Electron process, and stops only the processes it recorded; every dev proof is followed by a build. The dev proofs start the real app and its real backend with empty scratch app data; no network-free claim is made for them."
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/test-run-reliability/trr90-plugin-collect.txt — the plugin's fixture attaches to both target tests"
      - "C:/Temp/av-kit/test-run-reliability/trr90-node-mode-probe.txt — warn-with-error-code exits 1 without a listener and 0 with one"
      - "C:/Temp/av-kit/test-run-reliability/trr90-selftest-dev-proof.txt, trr90-selftest-load-run.txt, trr90-selftest-wait-check.txt — 0 failures each"
      - "C:/Temp/av-kit/test-run-reliability/trr90-load-run-kill-check.txt — the busy children's interpreters (not the launchers) are all gone after the stop"
      - "ui/src/main/index.ts:99 — the av-kit-ui single-instance lock"
      - "ui/tests/e2e/global-setup.ts:40-47 — the stale-build check that npm run dev's out/ would trip"
      - "docs/execution/plans/2026-11-15-convert-settings-drafts/dev-app-procs.py — Session 81's snapshot and stop-by-record checker"
    research: { engine: none, sources: [] }
    reasoning: "Mat asked for framework and scripts, not click-throughs (2026-11-16). The flake depends on load, so a test that only runs alone can't show it; a fixed worker delay makes the Red deterministic, and the load run shows the fix holds where it failed. A window is the dev bug's only symptom, so the proof looks for one, with the unset run as its control. The lock and out/ are the two ways a dev launch can disturb the rest of the session, and both are handled. The lock is keyed on the av-kit-ui user data, so only an av-kit dev app can hold it; counting every electron.exe would make another project's app (a zorivest lane app) cost a 600 s wait and a false S11. An error dialog is a visible titled window too, so the class check keeps it from passing as the app. The dev proof drops AVKIT_E2E, so the real backend starts (ui/src/main/index.ts:234-266); the plan does not trace its startup for outbound calls, so it claims only that the proof starts no download, transcript or TTS action. Two-way: plan-local scripts."
  - id: D-1122
    stage: execution
    question: "Row 5's full test:e2e runs failed twice on real-pointer tests that pass alone (attempt 1 run 3: AC-49.29; attempt 2 run 1: five tests), with no rejection record. Does row 5 run again?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Rerun row 5 once more in full (attempt 3), with the load probe before each full run and the attempt-1 and attempt-2 receipts kept under their own names; the row-5 pass bar of three passing full runs is kept; any rejection record is S10; a failure in attempt 3 is rerun alone, recorded and brought to the coordinator, with no fourth attempt; all three attempts and every failing test are disclosed in the handoff"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md S5 — an Electron failure without a rejection record is rerun once alone; only a repeat failure stops"
      - "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md S10 — a rejection record is never rerun away"
      - ".agent/context/known-issues.yaml DOWNLOAD-QUEUE-DRAG-OVER-MISS and CAPTURE-ZOOM-PAN-ORIGIN-FLAKE — the registered real-pointer flake families"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The coordinator ruled on the executor's row-5 stop. The four full runs held 0 rejection records, so S10 did not fire; each failing test passed when rerun alone (convert-queue.test.ts:1182 AC-49.29; capture-inbox.test.ts:1601, :1658, :2001, :3496; download-queue.test.ts:1319); all six are real-pointer hover or drag tests in families already registered as flaky (DOWNLOAD-QUEUE-DRAG-OVER-MISS, CAPTURE-ZOOM-PAN-ORIGIN-FLAKE). No expectation changes, so M-7 is not hit, and the row-5 bar of three full runs is kept, not lowered. Rejected: accepting attempt 1's two of three, which lowers the approved bar; registering a new flake issue first, which changes row 8's register scope, so the failures are disclosed instead; doing nothing, which leaves the session halted. Two-way: one more run of an approved row."
  - id: D-1123
    stage: execution
    question: "Attempt 3 of row 5 passed two full test:e2e runs and failed one spec in the third (capture-inbox.test.ts:1948 AC-81.11, timeout and worker teardown) that passed alone, with no rejection record in any run. Is row 5's full-run evidence complete?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 5's full runs are complete under the plan's own S5 rule: attempt 3 is the AC-12 evidence; the rest of row 5's cell (typecheck, lint, eol-check.py and the final check) runs from a separate script without rerunning the unit, build, targeted E2E or full runs; then rows 6 to H1-6b continue. In the H1-2 gate and any later Electron run, a rejection record is S10; a failure with no record is rerun alone once, and if it passes the whole gate is rerun once after the load probe reads 50 % or less; a second gate failure on a spec that passes alone is recorded and reported to the coordinator; a spec that fails twice is S5"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-test-run-reliability/task.md row 5 and implementation-plan.md S5 — a full run that fails with no record is handled by the S5 rule: the failing spec is rerun once alone, and only a repeat failure stops"
      - "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md D-1122 — attempt 3 of row 5, the bar of three full runs kept"
      - ".agent/context/known-issues.yaml CAPTURE-E2E-LAUNCH-TEARDOWN-HANG — capture-inbox launch or close stalls past the 60 s test timeout under load, then a worker teardown timeout; no assertion fails"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The coordinator ruled on the executor's attempt-3 stop. Row 5's cell and S5 both say a full run that fails with no record is handled by the S5 rule: the failing spec is rerun once alone, and only a repeat failure stops. No spec failed twice across the seven full runs of the three attempts, and each of the seven failing specs passed alone, so S5 never fired; the stop after a second failing run came from the coordinator's brief and was stricter than the plan. Attempt 3 is the AC-12 evidence: full runs 1 and 2 gave 226 passed, full run 3 gave 225 passed and 1 failed (capture-inbox.test.ts:1948 AC-81.11, test timeout and worker teardown timeout, the signature of the open CAPTURE-E2E-LAUNCH-TEARDOWN-HANG), which passed alone in 8.4 s, and every run held 0 rejection records. AC-12's each run passes is read as passes, with a no-record failure handled by S5; the execution reviewer judges whether that holds. No expectation changes, so no M item is hit. Rejected: a fourth full attempt, because other sessions' gates load the host and the same flakes recur; bringing it to Mat, because the plan already defines the handling and no M item is hit; doing nothing, which leaves the session halted. Two-way: the evidence and its reading are disclosed for review."
open_decisions: []
```

**Expert pass (HDP §5a, fresh context): adopted in full.** Receipt: `C:/Temp/av-kit/test-run-reliability/tr90-expert-pass.txt` (advisory, not the independent review), with the probes `tr90-ep-launcher-probe.txt` and `tr90-ep-kill-probe.txt`. It found no High, five Mediums and seven Lows; every one is adopted and none is rejected. Its brief results: D-1115 widened, D-1118 changed, D-1116 changed, D-1117 holds, D-1119 holds, D-1120 changed; D-1116 was the one autonomous decision it judged closest to a brief, and it stays autonomous through the named suite-wide row (M2).

| Finding | Change in this plan |
|---|---|
| M1: `test_tts_voice_packs.py:249` and `:320` reach the `:177` default | §What the code shows counts 21 tests and names the other importers (none reaches a changed wait); two §Test pins rows; the file joins "Read, never changed", `baseline-scope.json` and the CRLF list; `TIME_GUARD`, AC-4, `trr-base-two.txt`, `trr-green-two.txt`, `load-run.py` `FILES` and the gate's `py-two` run three files; D-1115 and its brief say 21 tests; the goal anchor names the three files |
| M2: one run can't prove no shutdown rejection; a new pass condition on every E2E test | `REJECTION_FAILS_CLOSE` says shutdown rejections count; one suite-wide §Test pins row for `electron-app.ts` `checkMainErrors` as approved scope (grouping D-1103); AC-12 and row 5 run the full `test:e2e` three times with a rejection-record count per run; S10 fires on any record in any run, rerun or gate; D-1116 adds the after-session rule (known-issues with the stack, never allowlisted) and records M-7 as answered by the named row; the Decision NOTE says so |
| M3: the wrapper's Ctrl+C and exit code on Windows | New contract `DEV_SIGNALS` (no-op `SIGINT`/`SIGBREAK` listeners while the child runs, `SIGTERM` forwarded, exit only from the child's `'exit'`, no re-raise); `exitCodeFor` exported and in `DECLARED_NEW` and §Boundary Inventory; AC-14 gains six `exitCodeFor` cases; D-1118 chosen updated |
| M4: the foreign-app filter counts every `electron.exe` | `dev-proof.py` `classify()`: foreign only when the executable is under an av-kit `ui/node_modules/electron/dist/` (`P:/av-kit` or `P:/av-kit-wt/<name>`); others counted as "other" and ignored; the preflight prints both counts; selftest cases for the main tree, a worktree, a zorivest lane exe, an `av-kit-backup` look-alike and a missing exe; S11 and D-1120 reworded |
| M5: the dev proofs' "no network" is unproven | The claim is narrowed, not proved: `task.md` and D-1120 say the dev proofs start the real app and backend (`ui/src/main/index.ts:234-266`) with empty scratch app data, start no download, transcript or TTS action, and make no network-free claim |
| L1: any titled window passes | `counts_as_app_window()` requires class `Chrome_WidgetWin_1` (`GetClassNameW`); a `#32770` dialog, an untitled or a hidden window never counts; selftest cases |
| L2: "left" counts launcher handles only | Each busy child prints its interpreter's `os.getpid()`; `load-run.py` holds a handle per interpreter, waits on it after the launcher kill, stops a survivor through it and prints `busy interpreters left`; AC-5 needs 0; `--kill-check` ran at plan time (`trr90-load-run-kill-check.txt`, exit 0) |
| L3: a real hang fails later | D-1115 states the worst case (up to 55 s more per changed wait reached; the deepest test reaches 5 of 12; the unasserted waits listed), the 1800 s `--run-timeout` (code 124) and the gate's `-x`; S9 notes it; the brief says it in plain words |
| L4: the YouTube Red's worker runs on | §2 Red, then Green: only the `:940` assertion counts for the YouTube target, the summary must read `2 failed` with no `error`, and `red-check.py` keeps a `PytestUnhandledThreadExceptionWarning` as neither a failure nor a setup failure, with a selftest fixture; rows 0 and 1 carry it |
| L5: D-1119 should list the cheaper fix | D-1119's reasoning lists B: the same wrapper with a dev or preview argument and `package.json:18`; registering stays the choice |
| L6: `:62` and `:526` are release waits | `WORKER_WAIT` says nine waits are on the worker or a service and two on the fake upstream's release gate; all eleven still read `WORKER_WAIT_S`, and `wait-check.py` still expects 11 |
| L7: a first-run Vite compile on a busy host | `dev-proof.py` imports `load-run.py`'s `host_load_wait()` and runs it before the preflight; §3 Load and dev proofs and D-1120 say so |

The AC count stays 17 and the task row count stays 26. The decision ids stay D-1115 to D-1120, D-1121 reserved for S10, D-1122 to D-1124 free. No item goes to Mat.

**Round 1 response (Codex plan review, `C:/Temp/av-kit/trr-plan-review-round-1.md`, `changes_required`, one finding).** R1-F1 is fixed in the plan's proof script; it is a correction to `dev-proof.py` under `DEV_PROOF` (D-1120), so no decision id is added and no AC or row changes.

| Finding | Change in this plan |
|---|---|
| R1-F1 (High): the dev proof adopts a reused id, can pass on an unrelated Electron window and hands that process to `--stop` | `dev-proof.py`: new `collect()` keeps each recorded (id, creation time) unchanged (`setdefault`, never overwritten); a live process holding a recorded id with another creation time is dropped from the ownership roots before `descendants()`, is not counted as running, so its window can't pass, and never enters the record, so the inherited `classify()` can't make it a stop candidate. New `root_is_launch()`: the launch's root must be the script's own child, created no earlier than one second before the launch (Popen also holds its handle, so the id can't be reused during the proof). New `still_same()`: a window passes only when its owner keeps its recorded identity in a snapshot taken after `EnumWindows`. The selftest drives the real `run()` on synthetic snapshots (launch, windows, checker, host-load wait and scratch removal replaced; no process started): the review's history `(101, 1010, parent 100)` then `(101, 5000, parent 999)` with that id's window shown gives `window: no`, exit 1, the record keeps `(101, 1010, 100)` and the stranger is not among `classify()`'s candidates; the launch's own Electron window passes; an id reused while the windows were listed fails and stays out of cleanup; a launch id held by another parent or an older process is a setup failure with an empty record. The reviewer's probe, adapted only so its synthetic root is the script's child, now reports exit 1 and no stranger (`trr90-r1-probe-adapted.txt`); the unadapted probe stops at the new root check (`trr90-r1-reviewer-probe-rerun.txt`). The docstring, `DEV_PROOF` and §3 Load and dev proofs say so |
| The same pattern in `load-run.py` | The busy child's printed interpreter id was opened by id and later terminated through that handle; an id reused between the print and `OpenProcess` would have been adopted. New `process_identity()` reads id, parent id and creation time through the handle (`NtQueryInformationProcess`, `GetProcessTimes`), and `owned_interpreter()` keeps the handle only for the launcher itself or a child of the launcher created no earlier than it; otherwise the handle is closed, nothing is terminated and the run exits 2. Seven selftest cases plus a live read of the script's own identity; `--kill-check --children 2` rerun at plan time: 2 interpreters accepted, 0 left, exit 0. `wait-check.py` and `slow_worker.py` hold no process ids |

The goal anchor, the 17 ACs, the 26 task rows and the decision ids are unchanged. No item goes to Mat.

### D-1115: Which five-second waits become longer, and by how much?

**I recommend A: give the two test files that failed one 60-second limit for their background work, used by every 5-second wait in them.** Twice, while the machine was busy, a test gave up after 5 seconds on work that would have finished, and failed. The waits stop as soon as the work is done, so a longer limit only costs time when a test would have failed anyway. A changes 12 waits in the two files, including the two that failed and the shared helper that 21 tests use (19 in the TTS file and 2 in the voice-pack file that borrows it). A check makes sure only the limit changed: what each test checks stays the same, and a plain run of the three files takes no more than 30 seconds longer than before. If a background job really hangs, its test still fails, but up to about a minute later for each wait it passes.

- B: change only the two waits that failed. Ten waits in the same files keep the same 5-second limit, two of them shared helpers.
- C: change all 137 waits of this kind in 29 test files. None of the others has failed in a recorded run.
- Do nothing: the full Python suite keeps failing now and then when the machine is busy.

Refs: `known-issues.yaml:5428`, `test_tts_assets.py:177`, `:260`, `test_youtube_adapter.py:939-940`, `trr90-wait-sweep.txt`, grouping §3 Session 90 Gate, M-3, M-8.

### D-1118: How should `npm run dev` clear ELECTRON_RUN_AS_NODE?

**I recommend A: run `npm run dev` through a small script that removes the variable and then starts electron-vite.** In a VS Code or Cursor terminal the variable is set, and today `npm run dev` then opens no window and shows no error. With A the window opens, and the script says it cleared the variable. Nothing else about the dev command changes.

- B: remove it inside `electron.vite.config.ts`. It works only because electron-vite happens to load the config before it starts Electron, the build loads it too, and the edit makes the Electron tests refuse the current build until a rebuild.
- C: stop with a message telling you to clear the variable. You still have to clear it yourself.
- Do nothing: keep clearing the variable by hand, as `commands.md` says.

Refs: `known-issues.yaml:5344`, `ui/package.json:16`, `lib-q6ns0vZr.js:220-240`, `.agent/docs/commands.md:70-83`, M-5, M-8.

## Research References

- **Node `--unhandled-rejections`:** `warn` always prints the warning; `warn-with-error-code` prints it and sets exit code 1 unless an `unhandledRejection` listener handles it, in which case nothing is printed (Node v26.13.0, `trr90-node-mode-probe.txt`). Electron's main process behaves like the second (`trr90-electron-rejection-probe.txt`).
- **`process.on('unhandledRejection', (reason, promise))`:** the reason is whatever the promise rejected with, not always an `Error`; the record's fields fall back to `typeof reason` and `String(reason)` (AC-7).
- **pytest plugins by name:** `-p <module>` imports a module from `sys.path` as a plugin; an autouse fixture in it runs for every test, before the module's own fixtures, and `monkeypatch` undoes its patches when the test ends.
- **Win32 `EnumWindows`, `IsWindowVisible`, `GetWindowThreadProcessId`, `GetClassNameW`:** list top-level windows, their owning process ids and their class; a console window belongs to `conhost.exe`, so it never counts as the app's; an Electron `BrowserWindow` has class `Chrome_WidgetWin_1` and a native message box `#32770`.
- **Node signals on Windows:** Ctrl+C and Ctrl+Break reach every process attached to the console as `SIGINT` and `SIGBREAK`; a process with no listener ends at once. `process.kill(pid, sig)` on win32 ends the target abruptly, with no 128+n exit code, and a child's `'exit'` can report `code` and `signal` both `null`; hence `DEV_SIGNALS` and `exitCodeFor`.
- **Python venv launcher:** the venv `python.exe` on this host starts the base interpreter as its child; killing the launcher stopped the interpreter in the expert's probe (`tr90-ep-launcher-probe.txt`, `tr90-ep-kill-probe.txt`), and `load-run.py` now checks each interpreter by its own handle (`trr90-load-run-kill-check.txt`).
- **`GetSystemTimes`:** idle, kernel and user times; kernel time includes idle time, so load is `1 - idle / (kernel + user)` between two readings (`load-run.py`).

## Planning receipts

All under `C:/Temp/av-kit/test-run-reliability/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `trr90-probe.py`, `trr90-probe.txt` | `HEAD` `79e3fa5`, one worktree, only this plan folder untracked; line endings, sizes and SHA-256 prefixes of the scope; the four new files and the handoff absent; the row-0 anchors with their lines; the tests that reach each 5-second wait; the three issues `open`, the preview issue absent; grouping row 90 `proposed`; highest decision id in use D-1114; `decision_sources` on the grouping alone and with the register and the three issues (D-1102 to D-1104) |
| `trr90-wait-sweep.txt` | 137 five-second wait sites in 29 test files |
| `trr90-wait-dryrun.py`, `trr90-wait-dryrun.txt` | The `WORKER_WAIT` edit applied in memory: definition lines, replaced lines, assertion lines, CRLF, no problems |
| `trr90-wait-dryrun-ruff.py`, `trr90-wait-dryrun-ruff.txt` | `ruff format --check` and `ruff check` pass on the edited TTS text |
| `trr90-ruff-base.txt`, `trr90-ruff.txt` | Ruff at base (the YouTube file is not format-clean at base) and on this plan folder's Python |
| `trr90-plugin-collect.txt` | The plugin's fixture attached to both target tests (collection only) |
| `trr90-electron-rejection-probe.txt` | Electron 42 prints the rejection warning without a listener and nothing with one; exit 0 both ways |
| `trr90-node-mode-probe.txt` | Node's `warn` and `warn-with-error-code` modes, with and without a listener |
| `trr90-selftest-dev-proof.txt`, `trr90-selftest-load-run.txt`, `trr90-selftest-wait-check.txt` | The plan-time scripts' selftests, 0 failures each (rerun after the expert-pass adoption and after round 1: 13, 24 and 32 checks) |
| `tr90-expert-pass.txt` | The HDP §5a expert pass (fresh context, advisory): no High, M1 to M5, L1 to L7 |
| `tr90-ep-launcher-probe.txt`, `tr90-ep-kill-probe.txt`, `tr90-ep-kill-probe.py` | The expert's probes: the venv `python.exe` is a launcher; killing it stopped the interpreter |
| `trr90-load-run-kill-check.txt` | L2's plan-time check, `load-run.py --kill-check --children 2`, rerun after round 1 with the interpreter identity check: 2 interpreters accepted, none the launcher itself, 0 still running after the launcher kill, 0 left, exit 0 |
| `trr90-r1-probe-adapted.py`, `trr90-r1-probe-adapted.txt`, `trr90-r1-reviewer-probe-rerun.txt` | R1-F1: the reviewer's reuse probe against the fixed script (adapted root: exit 1, `window: no`, record keeps `(101, +10, 100)`, no stranger among the stop candidates; unadapted: setup failure at the root check) |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the three issues, grouping §3 Session 90 and D-1103, Session 78's harness, and the code reads above | `trr-plan-2026-11-17-test-run-reliability` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-1 to AC-17 | `trr-execution-2026-11-17-test-run-reliability` |
