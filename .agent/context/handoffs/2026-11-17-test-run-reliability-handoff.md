---
date: "2026-11-17"
project: "2026-11-17-test-run-reliability"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md"
build_plan_section: "none (test-harness debt; no MEU, D-1103)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-17-queue-convert-fixes-MEU-157-handoff.md"
---

# Handoff: 2026-11-17-test-run-reliability-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. Session 90 is test and dev debt with no MEU (grouping D-1103), as Session 78 `2026-11-15-e2e-harness-hardening` was. It closes three register issues: `PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD`, `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED` and `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT`.
**Build Plan Section**: none.
**Predecessor**: [2026-11-17-queue-convert-fixes-MEU-157-handoff.md](2026-11-17-queue-convert-fixes-MEU-157-handoff.md), Session 89, committed as `79e3fa5`. Session 90 is the second and last session of the post-Session 88 triage grouping (`.agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md`).

- **The Python waits (`WORKER_WAIT`, `WAITS_NAMED`, `WAIT_SIGNALS_KEPT`, `TIME_GUARD`, D-1115).** `tests/integration/test_tts_assets.py` and `tests/integration/test_youtube_adapter.py` each define `WORKER_WAIT_S = 60.0` once (TTS `:33`, YouTube `:108`), in a three-line block after their anchor line, and their twelve 5-second worker waits read it: eleven in the TTS file, one (the join at `:942`) in the YouTube file. Every wait still returns on its signal; no sleep and no poll loop was added. Four assertion lines change only their bound (listed under Changed Files). The other 125 waits of the same pattern in other files are left, none having failed (D-1115).
- **The rejection watch (`REJECTION_WATCH`, `REJECTION_WARNING_LINE`, `MAIN_REJECTION_MARKER`, `REJECTION_FAILS_CLOSE`, `EXCEPTION_WATCH_KEPT`, D-1116, D-1117).** `ui/tests/e2e/main-error-watch.cjs` adds a `process.on('unhandledRejection')` listener that records `{ kind: 'rejection', name, message, stack }` in the same log as the exception record and writes `[avkit-e2e-main-rejection] UnhandledPromiseRejectionWarning: <stack>` to stderr. `electron-env.ts` exports `MAIN_REJECTION_MARKER` and adds `kind?: 'rejection'` to `MainErrorRecord`. `checkMainErrors` in `electron-app.ts` now fails the close on any record, exception or rejection, with the header `main-process uncaught exception(s) or unhandled rejection(s):` and the prefix `unhandled rejection: ` on each rejection. No rejection is allowlisted; one found later goes to `known-issues.yaml` with its stack (D-1116). The exception record, its marker and its globals are unchanged.
- **The dev script (`DEV_ENV_CLEARED`, `DEV_NOTICE`, `DEV_ARGS`, `DEV_SIGNALS`, `DEV_ENTRY_ONLY`, `DEV_SCRIPT`, D-1118).** `ui/scripts/electron-vite-dev.mjs` (new) removes `ELECTRON_RUN_AS_NODE` in any letter case from a copy of the environment, writes `electron-vite-dev: cleared ELECTRON_RUN_AS_NODE` to stderr when it removed one, and starts `electron-vite dev` with that environment. It ignores Ctrl+C and Ctrl+Break itself, because the console group sends them to the child too, forwards `SIGTERM`, and exits with the child's code. Importing it starts nothing. `ui/package.json:16` reads `"dev": "node ./scripts/electron-vite-dev.mjs",`; `:18` (`preview`) is unchanged.
- **Preview (`PREVIEW_REGISTERED`, D-1119).** `npm --prefix ui run preview` has the same gap. It is registered `open` as `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` and is not fixed.
- **Records (row 8, `COMMANDS_DOC`).** The three issues are resolved through `issue-resolve.py`, bound to row 0's register hash, with no `meu_links`; the preview issue is added; `known-issues.md` is rendered; `.agent/docs/commands.md` `:78` is the new dev row and `:80` the preview row; grouping row 90 (`:125`) reads `executed (Session 90)`.

**What Mat sees.** The two Python test files no longer fail when a busy host makes a fake worker take more than five seconds; a passing run is no slower (the plain run of the three files that reach the waits took 9.2 s against 10.1 s at row 0). An Electron E2E test now fails if the app's main process leaves a promise rejection unhandled, at launch, while running or during shutdown, with the rejection's stack in the failure. `npm --prefix ui run dev` opens the window from a VS Code or Cursor terminal and prints one line saying it cleared the variable. `npm --prefix ui run preview` from such a terminal still opens no window, as the register now says.

**Edges.** A worker that really hangs now costs up to 55 s more per changed wait its test reaches before the test fails (D-1115, S9). The watch counts a rejection only when Node reports it unhandled; a handled rejection leaves no record (AC-10).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-17 ("run @.agent/skills/issue-triage/ create session grouping and continue planning and executing as orchestrator"; `implementation-plan.md:15`, D-1102, D-1104), `plan_to_exec_gate: human`; the plan review approved at round 2 (`.agent/context/handoffs/2026-11-17-test-run-reliability-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `test-run-reliability` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | pytest | With the slow-worker plugin (`AVKIT_SLOW_WORKER_S=6`), `test_ac_122_8_surrogate_title_survives_real_storage` fails at row 1 by an `AssertionError` at the row-0 `:940` (now `:943`) and passes at row 2, with a `delayed` line in both runs | Local Canon (`PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD`; grouping §3 Session 90) | `tests/integration/test_youtube_adapter.py:884` | ✅ |
| AC-2 | pytest | The same for `test_ac_62_16_model_overshoot_is_clipped_not_failed`, failing at the row-0 `:260` (now `:263`, in `_install_spacy`) | As AC-1 | `tests/integration/test_tts_assets.py:785` | ✅ |
| AC-3 | check | `wait-check.py`: no 5-second worker wait left; `WORKER_WAIT_S` defined once per file and used 11 times (TTS) and once (YouTube); only the block insert and one-for-one replaced lines; assertion lines changed exactly TTS row-0 `:955`, `:963`, `:977`, `:984`; CRLF | Local Canon (`WORKER_WAIT`, `WAITS_NAMED`, `WAIT_SIGNALS_KEPT`) | row 2 and gate `wait-check` | ✅ |
| AC-4 | check | `TIME_GUARD`: the plain run of the three files passes within the row-0 time plus 30 s | Local Canon (`TIME_GUARD`) | row 2 `trr-time-guard.txt` | ✅ |
| AC-5 | check | `load-run.py`: three runs of the three files pass at a median load of at least 85 %, with no busy child or interpreter left | Local Canon (Session 81 RULE-2) | row 3 `trr-load-run.txt` | ✅ |
| AC-6 | unit | An unhandled `Error` rejection in a child with the watch: the child lives, stderr holds the marker and the warning, the log holds one rejection record with its stack | Local Canon (`REJECTION_WATCH`, `REJECTION_WARNING_LINE`) | `ui/tests/unit/rejection-watch.test.ts:59` | ✅ |
| AC-7 | unit | A rejection with a string reason is recorded as `name: 'string'` with that string as message and stack | Local Canon (`REJECTION_WATCH`) | `ui/tests/unit/rejection-watch.test.ts:77` | ✅ |
| AC-8 | unit (guard) | An uncaught exception keeps its record without `kind` and its `[avkit-e2e-main-error]` line; passes at Red | Local Canon (`EXCEPTION_WATCH_KEPT`) | `ui/tests/unit/rejection-watch.test.ts:89` | ✅ |
| AC-9 | E2E | In the real app an unhandled main-process rejection is counted once, the process lives, and `close()` rejects with `unhandled rejection: Error: avkit-e2e-rejection-probe` and a stack line | Local Canon (`REJECTION_FAILS_CLOSE`) | `ui/tests/e2e/main-rejection-watch.test.ts:47` | ✅ |
| AC-10 | E2E (guard) | A handled rejection leaves a count of 0 and `close()` resolves; passes at Red | Local Canon (`REJECTION_FAILS_CLOSE`) | `ui/tests/e2e/main-rejection-watch.test.ts:76` | ✅ |
| AC-11 | E2E (guard) | stderr still holds `UnhandledPromiseRejectionWarning: Error: avkit-e2e-rejection-probe`; passes at Red and at Green | Local Canon (D-1117) | `ui/tests/e2e/main-rejection-watch.test.ts:95` | ✅ |
| AC-12 | check | Three full `test:e2e` runs with the watch on, each with 0 rejection records; `capture-inbox.test.ts` byte-identical to row 0 | Local Canon (the suite-wide pin row, D-1116; S10) | row 5 attempt 3 `trr-watch-green-e2e-full-1.txt` to `-3.txt`, `trr-watch-green-check.txt` | ✅ under D-1123, the plan's pre-existing S5 exception: 0 records in all three runs; run 3 had one failure with no record that passed alone, preserved and disclosed, so these are not three clean first passes (Evidence, row 5) |
| AC-13 | unit | `devEnv` removes the variable in any case and leaves its base unchanged; `DEV_NOTICE` text | Local Canon (`DEV_ENV_CLEARED`, `DEV_NOTICE`) | `ui/tests/unit/dev-script.test.ts:30` | ✅ |
| AC-14 | unit | `devArgs`, `isEntry`, `exitCodeFor` and the `dev` and `preview` scripts in `ui/package.json` | Local Canon (`DEV_ARGS`, `DEV_SIGNALS`, `DEV_ENTRY_ONLY`, `DEV_SCRIPT`) | `ui/tests/unit/dev-script.test.ts:41` | ✅ |
| AC-15 | proof | `dev-proof.py --run-as-node set`: no window at base (exit 1); window, notice and nothing left after row 7 and in the gate | Local Canon (D-1120) | rows 6 and 7; gate `dev-proof-set` | ✅ |
| AC-16 | proof (control) | `dev-proof.py --run-as-node unset`: window, no notice, nothing left, at base and after row 7 | Local Canon (D-1120) | rows 6 and 7 | ✅ |
| AC-17 | check | The three issues resolved with `verification` and `resolution_path` and no `meu_links`; the preview issue `open` once; renders pass; grouping row 90; `commands.md` `:78` and `:80`, CRLF | Local Canon (D-1103, D-1119; `COMMANDS_DOC`) | row 8 `trr-row8-check.txt`; gate `issues-render-check` | ✅ |
| Worker default (cross-ref) | guard | `tests/integration/test_tts_voice_packs.py:249` (the `stack` fixture's teardown, `built.wait_idle()`) and `:320` (`assert stack.wait_idle()["state"] == "Idle"`): unchanged lines in an unchanged file that reach the changed `wait_idle` default (`test_tts_assets.py:180`, row-0 `:177`); `:320` now waits up to 60 s for `Idle` and asserts the same | Local Canon (§Test pins) | row 2 `trr-green-two.txt`; row 3; gate `py-two` and `py-tests` | ✅ |
| TTS waits (cross-ref) | guard | `tests/integration/test_tts_assets.py:263`, `:308`, `:417`, `:518` (row-0 `:260`, `:305`, `:414`, `:515`; `stack.wait_idle()["state"] == "Idle"`) and `:967` (row-0 `:964`, `assert gated.released == [True]`): unchanged lines; the four bound-only lines are under Changed Files | Local Canon (§Test pins; `WAITS_NAMED`) | row 2; gate `py-two`, `wait-check` | ✅ |
| E2E harness unit (cross-ref) | guard | `ui/tests/unit/e2e-harness.test.ts:47`, `:60`, `:69`, `:112`, `:121` (`electronEnv`, the single `_electron` launch site, the exception record, `mainErrorRecords`, `requireScratchAppData`): unchanged and passing | Local Canon (§Test pins; `EXCEPTION_WATCH_KEPT`) | row 5 `trr-watch-green-unit.txt`; gate `ui-unit` | ✅ |
| Electron harness (cross-ref) | guard | `ui/tests/e2e/electron-harness.test.ts:50` (the watch loads before main), `:69` and `:97` (an uncaught exception after launch and during startup fails the close), `:117` (a launch without a main-process error closes cleanly; now also no rejection at launch and close): unchanged and passing | Local Canon (§Test pins) | row 5 `trr-watch-green-e2e.txt`; gate `ui-electron` | ✅ |
| `checkMainErrors` (cross-ref, suite-wide) | guard | `ui/tests/e2e/electron-app.ts` `checkMainErrors`, run by the wrapped `close()` of every app `launchElectron` starts: the close now also fails on any unhandled-rejection record, shutdown included. A new pass condition on every E2E test, with no test file changed (approved scope: grouping D-1103) | Local Canon (§Test pins; `REJECTION_FAILS_CLOSE`) | row 5 full runs (0 records in each of the seven); gate `ui-electron` | ✅ |
| Capture backend warning (cross-ref) | guard | `ui/tests/e2e/capture-inbox.test.ts:403` (stderr holds no `UnhandledPromiseRejectionWarning: Error: backend not ready`): byte-identical file; the regex still sees a rejection through `REJECTION_WARNING_LINE` | Local Canon (D-1117) | `trr-watch-green-check.txt` `capture-inbox unchanged: True`; gate `ui-electron` | ✅ |
| Row 5 flakes (cross-ref) | guard | The specs that failed in a full run with no rejection record and passed alone, cited by file and line under Evidence (row 5): `ui/tests/e2e/convert-queue.test.ts:1182`, `ui/tests/e2e/download-queue.test.ts:1319` and `ui/tests/e2e/capture-inbox.test.ts:1601`, `:1658`, `:1948`, `:2001`, `:3496`; none of them changed | Local Canon (S5, D-1122, D-1123) | the reruns alone (`trr-watch-green-e2e-full-3-rerun-ac4929.txt`, `trr-watch-green-e2e-full-1-attempt2-rerun-five.txt`, `trr-watch-green-e2e-full-3-attempt3-rerun-ac8111.txt`) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 | `E   AssertionError: assert <TranscriptStatus.Processing: 'Processing'> is <TranscriptStatus.Done: 'Done'>` (`trr-py-red.txt`, `2 failed in 12.03s`) | Row 2: `2 passed in 33.58s` (`trr-py-green.txt`) | `tests/integration/test_youtube_adapter.py:884` |
| AC-2 | `E   AssertionError: assert 'Downloading' == 'Idle'` (`trr-py-red.txt`) | Row 2: `2 passed in 33.58s` (`trr-py-green.txt`) | `tests/integration/test_tts_assets.py:785` |
| AC-6, AC-7 | `AssertionError: expected 'undefined' to be 'string' // Object.is equality` (`trr-watch-red-unit.txt`, `Tests  2 failed \| 1 passed (3)`) | Row 5: `Tests  8 passed (8)` (`trr-watch-green-unit.txt`) | `ui/tests/unit/rejection-watch.test.ts:59`, `:77` |
| AC-9 | `Error: expect(received).toBe(expected) // Object.is equality`, `Expected: 1`, `Received: 0` (`trr-watch-red-e2e.txt`, `1 failed`, `2 passed (8.3s)`) | Row 5: `8 passed (54.7s)` (`trr-watch-green-e2e.txt`) | `ui/tests/e2e/main-rejection-watch.test.ts:47` |
| AC-13, AC-14 | `AssertionError: expected false to be true // Object.is equality` (`trr-dev-red-unit.txt`, `Tests  2 failed (2)`) | Row 7: `Tests  2 passed (2)` (`trr-dev-green-unit.txt`) | `ui/tests/unit/dev-script.test.ts:30`, `:41` |

AC-8, AC-10 and AC-11 passed at Red and are guards; AC-3, AC-4, AC-5, AC-12 and AC-17 are checks; AC-15 and AC-16 are proofs.

- **Row 0 baseline** (`trr-baseline.txt`): `baseline: all steps exit 0`, `eol-check: 19 scope path(s), 0 problem(s)`. UI suite `Test Files  140 passed (140)`, `Tests  1614 passed (1614)` (`trr-base-ui.txt`); Python suite `3087 passed, 37 warnings in 261.20s (0:04:21)` (`trr-base-py.txt`); the three files that reach the waits `74 passed in 9.13s`, `wall_s: 10.1` (`trr-base-two.txt`).
- **Row 1 Red** (`trr-py-red.txt`): `2 failed in 12.03s`, child exit 1 (`trr-py-red.txt.exit`). `trr-py-red-check.txt`: `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`. `trr-py-red-sites.txt`: `delayed lines: {'test_ac_122_8_surrogate_title_survives_real_storage': True, 'test_ac_62_16_model_overshoot_is_clipped_not_failed': True} failure sites: {'youtube 940': True, 'tts 260': True}`.
- **Row 2 Green.** `trr-py-green.txt`: `2 passed in 33.58s`. `trr-wait-check.txt`: `wait-check: PASS`; TTS `'definitions': [33], 'uses': 11`, `'replaced_row0_lines': [62, 177, 227, 526, 712, 896, 938, 955, 963, 977, 984]`, `'assert_lines_changed': [955, 963, 977, 984]`, `'crlf': True`; YouTube `'definitions': [108], 'uses': 1`, `'replaced_row0_lines': [939]`, `'assert_lines_changed': []`, `'crlf': True`. `trr-green-two.txt`: `74 passed in 8.33s`, `wall_s: 9.2`. `trr-time-guard.txt`: `base wall_s: 10.1 green wall_s: 9.2 limit: 40.1`. `trr-py-eol.txt`: `eol-check: 19 scope path(s), 0 problem(s)`. `trr-py-lint.txt`: `All checks passed!`; `trr-py-format.txt`: `1 file already formatted`.
- **Row 3 load run** (`trr-load-run.txt`): `host-load: ran at 7.9 %`, `load before the runs: 100.0 %`; `run 1: exit 0 in 13 s :: 74 passed in 11.74s`, `run 2: exit 0 in 13 s :: 74 passed in 11.74s`, `run 3: exit 0 in 15 s :: 74 passed in 14.43s`; `busy children left: 0`, `busy interpreters left: 0`; `load during the runs: n=13 min=100.0 median=100.0 max=100.0`; `PASS: 3 of 3 runs passed at median load 100.0 (threshold 85.0)`.
- **Row 4 Red.** `trr-watch-red-unit.txt`: `Tests  2 failed | 1 passed (3)`; `trr-watch-red-unit-check.txt`: `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`. `trr-watch-red-e2e.txt`: AC-9 `1 failed`, `2 passed (8.3s)`; `trr-watch-red-e2e-check.txt`: `red-check: 1 receipt(s), 1 required test(s), 0 problem(s)`. `trr-watch-red-hashes.txt`: `vitest 2 failed and 1 passed: True AC-8 not failed: True guard ok lines: {'AC-10': 1, 'AC-11': 1}`, the three harness files unchanged, `CR in: []`.
- **Row 5 Green, attempt 3 (the AC-12 evidence, D-1122, D-1123).** `trr-watch-green-unit.txt`: `Test Files  2 passed (2)`, `Tests  8 passed (8)` (`rejection-watch.test.ts` and `e2e-harness.test.ts`). The build (`trr-watch-green-build.txt`): `built in 4.99s`. `trr-watch-green-e2e.txt` (`main-rejection-watch.test.ts` and `electron-harness.test.ts`): `8 passed (54.7s)`. Full runs: `226 passed (10.5m)` (`trr-watch-green-e2e-full-1.txt`), `226 passed (9.4m)` (`trr-watch-green-e2e-full-2.txt`), and `1 failed`, `225 passed (17.3m)` (`trr-watch-green-e2e-full-3.txt`). The rest of the cell, run alone after D-1123 (`run-row5-rest.ps1`): the typecheck and lint exit 0 (`trr-watch-types.txt`, `trr-watch-lint.txt`), `eol-check: 19 scope path(s), 0 problem(s)` (`trr-watch-eol.txt`), and `trr-watch-green-check.txt`: `tests unchanged since row 4: {... True, ... True} capture-inbox unchanged: True`, the three harness files changed, `rejection records per full run: {1: 0, 2: 0, 3: 0} ok lines: {'AC-9': 1, 'AC-10': 1, 'AC-11': 1}`.

**Row 5's three attempts.** Every full run's rejection-record count is the number of receipt lines that contain `unhandled rejection:`.

| Attempt | Full run | Result (receipt) | Rejection records | Failing spec, alone |
|---------|----------|------------------|-------------------|---------------------|
| 1 | 1 | `226 passed (7.1m)` (`trr-watch-green-e2e-full-1-attempt1.txt`) | 0 | — |
| 1 | 2 | `226 passed (7.3m)` (`trr-watch-green-e2e-full-2-attempt1.txt`) | 0 | — |
| 1 | 3 | `1 failed`, `225 passed (6.9m)` (`trr-watch-green-e2e-full-3-attempt1.txt`) | 0 | `convert-queue.test.ts:1182`: `1 passed (1.4s)` (`trr-watch-green-e2e-full-3-rerun-ac4929.txt`) |
| 2 | 1 | `5 failed`, `221 passed (12.5m)` (`trr-watch-green-e2e-full-1-attempt2.txt`) | 0 | the five, by title: `6 passed (12.0s)` (`trr-watch-green-e2e-full-1-attempt2-rerun-five.txt`; one title filter also matched `capture-inbox.test.ts:1481`) |
| 2 | 2, 3 | not run: the coordinator's brief stopped the row after a second failing full run | — | — |
| 3 | 1 | `226 passed (10.5m)` (`trr-watch-green-e2e-full-1.txt`) | 0 | — |
| 3 | 2 | `226 passed (9.4m)` (`trr-watch-green-e2e-full-2.txt`) | 0 | — |
| 3 | 3 | `1 failed`, `225 passed (17.3m)`, `1 error was not a part of any test` (`trr-watch-green-e2e-full-3.txt`) | 0 | `capture-inbox.test.ts:1948`: `1 passed (9.0s)` (`trr-watch-green-e2e-full-3-attempt3-rerun-ac8111.txt`) |

**The failing specs.** No spec failed twice, and none was edited.

| Spec (file:line) | Failed in | Failure | Alone | Register issue |
|------------------|-----------|---------|-------|----------------|
| `ui/tests/e2e/convert-queue.test.ts:1182` (dragging a conversion onto the third row lands the exact order) | attempt 1 run 3 | `x  104 ... (811ms)` | `1 passed (1.4s)` | none exactly; the real-pointer drag family of `DOWNLOAD-QUEUE-DRAG-OVER-MISS` (open), which names the Downloader drag |
| `ui/tests/e2e/capture-inbox.test.ts:1601` (a disabled Apply shows its reason where the pointer lands) | attempt 2 run 1 | `x   35 ... (5.8s)` | passed in `6 passed (12.0s)` | none exactly; the real-pointer capture family of `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` (open) |
| `ui/tests/e2e/capture-inbox.test.ts:1658` (a real hover shows the Arrow and Undo hints) | attempt 2 run 1 | `x   37 ... (7.0s)` | passed in `6 passed (12.0s)` | none exactly; as above |
| `ui/tests/e2e/capture-inbox.test.ts:2001` (at 100% after a pan the arrow handles track the arrow) | attempt 2 run 1 | `x   40 ... (2.0s)` | passed in `6 passed (12.0s)` | `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` (open) covers the pan-origin family; not this spec by name |
| `ui/tests/e2e/capture-inbox.test.ts:3496` (Lock on at load, R arms Box, an Alt drag then V arms Select) | attempt 2 run 1 | `x   59 ... (7.5s)` | passed in `6 passed (12.0s)` | none exactly; the real-pointer capture family |
| `ui/tests/e2e/download-queue.test.ts:1319` (dragging a row onto the third row lands the exact order, and it survives a reload) | attempt 2 run 1 | `x  130 ... (32.3s)` | passed in `6 passed (12.0s)` | `DOWNLOAD-QUEUE-DRAG-OVER-MISS` (open) |
| `ui/tests/e2e/capture-inbox.test.ts:1948` (the hotkey-in-use banner sits inside the header) | attempt 3 run 3 | `Test timeout of 60000ms exceeded.` and `Worker teardown timeout of 60000ms exceeded.` (`x   39 ... (1.0m)`) | `1 passed (9.0s)` | `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` (open): its exact signature |

The plan's D-1122 and D-1123 entries name two of these specs by the labels their own tests carry: AC-49.29 is `convert-queue.test.ts:1182` and AC-81.11 is `capture-inbox.test.ts:1948`. Those ids belong to earlier sessions' families, not to this session's AC-1 to AC-17; they are named here only so the handoff carries every id the plan text holds (the closeout validator's coverage check), and this handoff claims nothing for them beyond the row above.

The host was shared with other sessions' gates. During attempt 3 the load sampled every 30 s read `n=77`, median 54 %, maximum 100 %, with 15 samples at 85 % or more (`trr-load-during-row5-attempt3.txt`); the load probe read 13 %, 9 %, 15 % and 41 % before the attempt and its three full runs (`trr-loadprobe-row5-attempt3-pre.txt`, `-full-1.txt` to `-full-3.txt`).

- **Row 6 Red and base proofs.** `trr-dev-red-unit.txt`: `Tests  2 failed (2)`; `trr-dev-red-check.txt`: `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`; `trr-dev-red-hashes.txt`: `package.json unchanged: True script absent: True CR in the test file: False`. Base with the variable set (`trr-dev-base-set.txt`): `host-load: ran at 53.4 %`, `window: no (after 5 s; root exited)`, `notice: no`, `left: 0`, exit 1 as planned. Base control (`trr-dev-base-unset.txt`): `host-load: ran at 28.2 %`, `window: yes (after 29 s; window)`, `notice: no`, `left: 0`, `PASS: window opened, notice as expected, nothing left`. `trr-dev-base-check.txt`: `base proofs: {'set exit': 1, 'set window no': True, 'set left 0': True, 'unset exit': 0, 'unset window yes': True, 'unset notice no': True, 'unset left 0': True}`. The build `built in 7.11s` (`trr-dev-base-build.txt`).
- **Row 7 Green.** `trr-dev-green-unit.txt`: `Tests  2 passed (2)`. With the variable set (`trr-dev-set.txt`): `host-load: ran at 8.5 %`, `window: yes (after 16 s; window)`, `notice: yes`, `left: 0`, `PASS: window opened, notice as expected, nothing left`. Control (`trr-dev-unset.txt`): `host-load: ran at 9.6 %`, `window: yes (after 16 s; window)`, `notice: no`, `left: 0`, `PASS: ...`. `trr-dev-green-check.txt`: `test unchanged since row 6: True package.json lines changed: [16] line 16 as planned: True CRLF: True dev and preview values: True CR in the script: False proofs: {'set': True, 'unset': True}`. The build `built in 4.41s` (`trr-dev-green-build.txt`).
- **Row 8 records.** `trr-issue-resolve.txt`: `decision logs read: 97 of 97`, `register sha256 before=10bdf7de5fe531f65f84ef017aacfedaad3fd7f69ae2a96cffdb739b98a4e803`, `target sha256 after=b08985b23e78a7446569f97b12b15ee200a3fdbe1c5ba307eaade8d5fef47936 CRLF=0 LF=5501`, `parsed fields changed: 9`, `issue-resolve: 0 problem(s)`. `trr-issue-add.txt`: `OK: Added issue 'UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT' to known-issues.yaml`. `trr-issues-render.txt`: `Rendered known-issues.md: 44 lines`; `trr-issues-render-check.txt`: `OK: known-issues.md is up-to-date`. `trr-row8-check.txt`: `grouping lines changed: [125] row 90 as planned: True commands.md shape: True dev row: True preview row: True CRLF: True`, the three issues `True`, `preview issue open: True yaml LF: True`.
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row0.ps1 (task.md row 0's Validation cell: baseline.ps1 records baseline.sha, the dirty list and hashes, the scope and skip hashes, the line-ending baseline, the UI and Python suites and the three files that reach the waits, with the plan-local checkers and their selftests); receipts trr-baseline.txt, trr-base-ui.txt, trr-base-py.txt, trr-base-two.txt", "scope": "Row 0: the baseline at 79e3fa5 and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus row 0", "output": "trr-baseline.txt: eol-check: 19 scope path(s), 0 problem(s); dev-proof selftest: 0 failure(s); baseline: all steps exit 0. trr-base-ui.txt: Test Files  140 passed (140); Tests  1614 passed (1614). trr-base-py.txt: 3087 passed, 37 warnings in 261.20s (0:04:21). trr-base-two.txt: 74 passed in 9.13s; wall_s: 10.1."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-1-red-python", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row1.ps1 (task.md row 1's Validation cell: PYTHONPATH=the plan folder, AVKIT_SLOW_WORKER_S=6, uv run pytest -p slow_worker on the two target tests *> C:/Temp/av-kit/test-run-reliability/trr-py-red.txt, its exit code, red-check.py --require the two test names, the delayed-line and failure-site check); receipts trr-py-red.txt, trr-py-red-check.txt, trr-py-red-sites.txt", "scope": "AC-1 and AC-2 Red on the unchanged test files, with the slow-worker plugin", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 and 1", "output": "trr-py-red.txt: E   AssertionError: assert <TranscriptStatus.Processing: 'Processing'> is <TranscriptStatus.Done: 'Done'>; E   AssertionError: assert 'Downloading' == 'Idle'; 2 failed in 12.03s; child exit 1. trr-py-red-check.txt: red-check: 1 receipt(s), 2 required test(s), 0 problem(s). trr-py-red-sites.txt: delayed lines: both True; failure sites: {'youtube 940': True, 'tts 260': True}."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-2-green-python", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row2.ps1 (task.md row 2's Validation cell: the WORKER_WAIT edit by bytes, the slow-worker run of the two target tests, wait-check.py, the plain run of the three files, the TIME_GUARD check, eol-check.py, ruff format --check and ruff check); receipts trr-py-green.txt, trr-wait-check.txt, trr-green-two.txt, trr-time-guard.txt, trr-py-eol.txt, trr-py-format.txt, trr-py-lint.txt", "scope": "AC-1 and AC-2 Green; AC-3 (WORKER_WAIT, WAITS_NAMED, WAIT_SIGNALS_KEPT) and AC-4 (TIME_GUARD)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 2", "output": "trr-py-green.txt: 2 passed in 33.58s. trr-wait-check.txt: TTS definitions [33], uses 11, replaced_row0_lines [62, 177, 227, 526, 712, 896, 938, 955, 963, 977, 984], assert_lines_changed [955, 963, 977, 984], crlf True; YouTube definitions [108], uses 1, replaced_row0_lines [939], assert_lines_changed [], crlf True; wait-check: PASS. trr-green-two.txt: 74 passed in 8.33s; wall_s: 9.2. trr-time-guard.txt: base wall_s: 10.1 green wall_s: 9.2 limit: 40.1. trr-py-eol.txt: eol-check: 19 scope path(s), 0 problem(s). trr-py-format.txt: 1 file already formatted. trr-py-lint.txt: All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-3-load-run", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row3.ps1 (task.md row 3's Validation cell: uv run python docs/execution/plans/2026-11-17-test-run-reliability/load-run.py *> C:/Temp/av-kit/test-run-reliability/trr-load-run.txt); receipts trr-load-run.txt, trr-load-run-1.txt to trr-load-run-3.txt", "scope": "AC-5: three runs of the three files that reach the waits at host load of 85 % or more", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 3", "output": "trr-load-run.txt: host-load: ran at 7.9 %; load before the runs: 100.0 %; run 1: exit 0 in 13 s :: 74 passed in 11.74s; run 2: exit 0 in 13 s :: 74 passed in 11.74s; run 3: exit 0 in 15 s :: 74 passed in 14.43s; busy children left: 0; busy interpreters left: 0; load during the runs: n=13 min=100.0 median=100.0 max=100.0; PASS: 3 of 3 runs passed at median load 100.0 (threshold 85.0)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-4-red-watch", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row4.ps1 (task.md row 4's Validation cell, with ELECTRON_RUN_AS_NODE unset and a scratch AVKIT_APP_DATA: Vitest rejection-watch.test.ts, red-check.py --require AC-6 and AC-7, the build, test:e2e main-rejection-watch.test.ts, red-check.py --require AC-9, the hash and guard check); receipts trr-watch-red-unit.txt, trr-watch-red-unit-check.txt, trr-watch-red-build.txt, trr-watch-red-e2e.txt, trr-watch-red-e2e-check.txt, trr-watch-red-hashes.txt", "scope": "AC-6, AC-7 and AC-9 Red against the unchanged harness; AC-8, AC-10 and AC-11 guards pass at Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 4", "output": "trr-watch-red-unit.txt: AssertionError: expected 'undefined' to be 'string' // Object.is equality; Tests  2 failed | 1 passed (3). trr-watch-red-unit-check.txt: red-check: 1 receipt(s), 2 required test(s), 0 problem(s). trr-watch-red-e2e.txt: Expected: 1, Received: 0; 1 failed; 2 passed (8.3s). trr-watch-red-e2e-check.txt: red-check: 1 receipt(s), 1 required test(s), 0 problem(s). trr-watch-red-hashes.txt: vitest 2 failed and 1 passed: True AC-8 not failed: True guard ok lines: {'AC-10': 1, 'AC-11': 1}; harness unchanged; CR in: []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-5-attempt-1", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row5.ps1 (task.md row 5's Validation cell, attempt 1, with ELECTRON_RUN_AS_NODE unset and a scratch AVKIT_APP_DATA), then run-row5-rerun-ac4929.ps1 (the failing spec alone); receipts kept as trr-watch-green-e2e-full-1-attempt1.txt to -3-attempt1.txt and trr-watch-green-e2e-full-3-rerun-ac4929.txt", "scope": "Row 5 attempt 1: three full test:e2e runs with the watch on", "phase": "runtime", "exit_code": 1, "result": "fail", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 5 (attempt 1)", "output": "full run 1: 226 passed (7.1m); full run 2: 226 passed (7.3m); full run 3: 1 failed, 225 passed (6.9m), convert-queue.test.ts:1182; rejection records 0, 0, 0. The spec alone: 1 passed (1.4s), rejection records 0. Under the coordinator's brief the row was run again in full (attempt 2)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-5-attempt-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row5.ps1 (task.md row 5's Validation cell, attempt 2), then run-row5-rerun-five.ps1 (test:e2e tests/e2e/capture-inbox.test.ts tests/e2e/download-queue.test.ts -g with the five failing titles); receipts kept as trr-watch-green-e2e-full-1-attempt2.txt and trr-watch-green-e2e-full-1-attempt2-rerun-five.txt", "scope": "Row 5 attempt 2: the first full run; runs 2 and 3 not run", "phase": "runtime", "exit_code": 1, "result": "fail", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 5 (attempt 2)", "output": "full run 1: 5 failed, 221 passed (12.5m): capture-inbox.test.ts:1601, :1658, :2001, :3496 and download-queue.test.ts:1319; rejection records 0. The five alone: 6 passed (12.0s), rejection records 0. Stopped and reported under the coordinator's brief (a second failing full run); D-1122 ordered attempt 3."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-5-green-watch", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row5-attempt3.ps1 (task.md row 5's Validation cell, attempt 3 under D-1122, with the load probe before each full run), pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row5-attempt3-rerun-ac8111.ps1 (the failing spec alone), and pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row5-rest.ps1 (the cell from its typecheck step on: typecheck, lint, eol-check.py and the final check, under D-1123); receipts trr-watch-green-unit.txt, trr-watch-green-build.txt, trr-watch-green-e2e.txt, trr-watch-green-e2e-full-1.txt to -3.txt, trr-watch-green-e2e-full-3-attempt3-rerun-ac8111.txt, trr-watch-types.txt, trr-watch-lint.txt, trr-watch-eol.txt, trr-watch-green-check.txt", "scope": "AC-6 to AC-11 Green and AC-12: REJECTION_WATCH, REJECTION_WARNING_LINE, MAIN_REJECTION_MARKER, REJECTION_FAILS_CLOSE, EXCEPTION_WATCH_KEPT; three full test:e2e runs", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 5 (attempt 3)", "output": "trr-watch-green-unit.txt: Test Files  2 passed (2); Tests  8 passed (8). trr-watch-green-build.txt: built in 4.99s. trr-watch-green-e2e.txt: 8 passed (54.7s). trr-watch-green-e2e-full-1.txt: 226 passed (10.5m). trr-watch-green-e2e-full-2.txt: 226 passed (9.4m). trr-watch-green-e2e-full-3.txt: 1 failed; 225 passed (17.3m); capture-inbox.test.ts:1948, Test timeout of 60000ms exceeded. and Worker teardown timeout of 60000ms exceeded.; alone: 1 passed (9.0s). The attempt-3 runner exited 1 at full run 3, which D-1123 handles under S5; the rest of the cell exited 0. trr-watch-eol.txt: eol-check: 19 scope path(s), 0 problem(s). trr-watch-green-check.txt: capture-inbox unchanged: True; rejection records per full run: {1: 0, 2: 0, 3: 0}; ok lines: {'AC-9': 1, 'AC-10': 1, 'AC-11': 1}."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-6-red-dev", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row6.ps1 (task.md row 6's Validation cell, after the load probe: Vitest dev-script.test.ts, red-check.py --require AC-13 and AC-14, the hash check, dev-proof.py --run-as-node set and unset on the unchanged dev script, the base check, the build); receipts trr-dev-red-unit.txt, trr-dev-red-check.txt, trr-dev-red-hashes.txt, trr-dev-base-set.txt, trr-dev-base-unset.txt, trr-dev-base-check.txt, trr-dev-base-build.txt", "scope": "AC-13 and AC-14 Red; AC-15 and AC-16 at base (S12)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 6", "output": "trr-dev-red-unit.txt: AssertionError: expected false to be true // Object.is equality; Tests  2 failed (2). trr-dev-red-check.txt: red-check: 1 receipt(s), 2 required test(s), 0 problem(s). trr-dev-red-hashes.txt: package.json unchanged: True script absent: True CR in the test file: False. trr-dev-base-set.txt: host-load: ran at 53.4 %; window: no (after 5 s; root exited); notice: no; left: 0. trr-dev-base-unset.txt: host-load: ran at 28.2 %; window: yes (after 29 s; window); notice: no; left: 0; PASS: window opened, notice as expected, nothing left. trr-dev-base-check.txt: set exit 1, set window no True, unset exit 0, unset window yes True. trr-dev-base-build.txt: built in 7.11s."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-7-green-dev", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row7.ps1 (task.md row 7's Validation cell, after the load probe: ui/scripts/electron-vite-dev.mjs and ui/package.json:16, Vitest dev-script.test.ts, node --check, typecheck, lint, eol-check.py, dev-proof.py set and unset, the green check, the build); receipts trr-dev-green-unit.txt, trr-dev-syntax.txt, trr-dev-types.txt, trr-dev-lint.txt, trr-dev-eol.txt, trr-dev-set.txt, trr-dev-unset.txt, trr-dev-green-check.txt, trr-dev-green-build.txt", "scope": "AC-13 to AC-16 Green: DEV_ENV_CLEARED, DEV_NOTICE, DEV_ARGS, DEV_SIGNALS, DEV_ENTRY_ONLY, DEV_SCRIPT", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 7", "output": "trr-dev-green-unit.txt: Tests  2 passed (2). trr-dev-set.txt: host-load: ran at 8.5 %; window: yes (after 16 s; window); notice: yes; left: 0; PASS: window opened, notice as expected, nothing left. trr-dev-unset.txt: host-load: ran at 9.6 %; window: yes (after 16 s; window); notice: no; left: 0; PASS: window opened, notice as expected, nothing left. trr-dev-eol.txt: eol-check: 19 scope path(s), 0 problem(s). trr-dev-green-check.txt: test unchanged since row 6: True package.json lines changed: [16] line 16 as planned: True CRLF: True dev and preview values: True CR in the script: False proofs: {'set': True, 'unset': True}. trr-dev-green-build.txt: built in 4.41s."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-8-records", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-row8.ps1 (task.md row 8's Validation cell: issue-resolve.py --issue PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD --issue E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED --issue UI-DEV-ELECTRON-RUN-AS-NODE-SILENT --set-file C:/Temp/av-kit/test-run-reliability/issue-resolve-set.json --expect-sha256 from baseline-scope.json; issue_triage.py add UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT; render; render --check; the row 8 check), after trr-row8-docs.py wrote commands.md :78 and :80 and grouping :125 by bytes; receipts trr-issue-resolve.txt, trr-issue-add.txt, trr-issues-render.txt, trr-issues-render-check.txt, trr-row8-check.txt, trr-row8-docs-out.txt", "scope": "AC-17: the three issues resolved, the preview issue added, commands.md and grouping row 90", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 79e3fa5 (baseline.sha) plus rows 0 to 8", "output": "trr-issue-resolve.txt: decision logs read: 97 of 97; register sha256 before=10bdf7de5fe531f65f84ef017aacfedaad3fd7f69ae2a96cffdb739b98a4e803; target sha256 after=b08985b23e78a7446569f97b12b15ee200a3fdbe1c5ba307eaade8d5fef47936 CRLF=0 LF=5501; parsed fields changed: 9; issue-resolve: 0 problem(s). trr-issue-add.txt: OK: Added issue 'UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT' to known-issues.yaml. trr-issues-render.txt: Rendered known-issues.md: 44 lines. trr-issues-render-check.txt: OK: known-issues.md is up-to-date. trr-row8-docs-out.txt: commands.md: :78 replaced, :80 inserted; CRLF lines 225. trr-row8-check.txt: grouping lines changed: [125] row 90 as planned: True commands.md shape: True dev row: True preview row: True CRLF: True; issues resolved: all True; preview issue open: True yaml LF: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-rowH1-2.ps1 (task.md row H1-2's Validation cell, after the load probe read 4 %: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-17-test-run-reliability/session-gate.ps1 *> C:/Temp/av-kit/test-run-reliability/trr-gate-h1.txt); step receipts trr-D6-<step>.txt", "scope": "H1-2: the PROFILE D6 session gate, 27 steps from identity-before to identity-after, including the full Python suite, the full UI unit suite, the build and the full Electron E2E suite with the rejection watch on", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "79e3fa58501db96e5cce4796c5146963a00748c2+598a3a2bcdee031b522500a4189c78915d4795f7c84ef9d22c6b15feb80feca8", "output": "trr-gate-h1.txt: every step exit=0 (identity-before, ui-types, ui-lint, task-contract, scope-paths, line-endings, home-path, five selftests, py-format, py-lint, dev-script-syntax, py-two, wait-check, ui-unit, host-load, dev-proof-set, py-tests, ui-tests, ui-build, ui-electron, issues-render-check, state-render, identity-after); tested_state before and after equal; session-gate: all steps exit 0. trr-D6-host-load.txt: host-load samples: [3, 12, 7, 13, 10] mean=9; host-load: ran at 9 %. trr-D6-dev-proof-set.txt: window: yes (after 16 s; window); notice: yes; processes recorded: 19; left: 0; PASS: window opened, notice as expected, nothing left. trr-D6-py-two.txt: 74 passed in 8.18s. trr-D6-ui-unit.txt: Tests  10 passed (10). trr-D6-py-tests.txt: 3087 passed, 37 warnings in 243.99s (0:04:03). trr-D6-ui-tests.txt: Test Files  142 passed (142); Tests  1619 passed (1619). trr-D6-ui-build.txt: built in 4.20s. trr-D6-ui-electron.txt: 226 passed (7.1m); unhandled rejection: lines 0. trr-D6-issues-render-check.txt: OK: known-issues.md is up-to-date. trr-D6-state-render.txt: Drift check passed. trr-D6-identity-after.txt: tested_state 79e3fa58501db96e5cce4796c5146963a00748c2+598a3a2bcdee031b522500a4189c78915d4795f7c84ef9d22c6b15feb80feca8."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "trr-h1-3-h1-4-closeout-checks", "command": "python C:/Temp/av-kit/test-run-reliability/trr-focus-entry.py (the Session 90 paragraph on top of .agent/context/current-focus.md, by bytes, CRLF kept); pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-rowH1-3.ps1 (rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/test-run-reliability/trr-render-check.txt); pwsh -NoProfile -File C:/Temp/av-kit/test-run-reliability/run-rowH1-4.ps1 (task.md row H1-4's skip-basis check *> C:/Temp/av-kit/test-run-reliability/skip-basis-check.txt)", "scope": "H1-3 (current-focus and the state render) and H1-4 (the pyright, OpenAPI and MCP skip basis, S13)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus paragraph", "output": "trr-focus-entry.py: bytes 82440 -> 84218 CRLF 206 -> 209 bare LF 0. trr-render-check.txt: Drift check passed - SSOT loaded (156 MEUs, 12 phases), rendered regions match on-disk content. skip-basis-check.txt: packages, mcp-server or tools changes since row 0: []"}
```

### Quality Gate Results

| Step | Result (receipt) |
|------|------------------|
| Gate | `session-gate: all steps exit 0` (`trr-gate-h1.txt`); 27 steps, each `exit=0` |
| Identity | `tested_state 79e3fa58501db96e5cce4796c5146963a00748c2+598a3a2bcdee031b522500a4189c78915d4795f7c84ef9d22c6b15feb80feca8`, equal before and after (`trr-D6-identity-before.txt`, `trr-D6-identity-after.txt`) |
| Scope | `changed paths: 33 outside scope: []`; `read-never-changed files: 11 mismatch: []`; `head moved (S4): False` (`trr-D6-scope-paths.txt`) |
| Line endings | `eol-check: 19 scope path(s), 0 problem(s)` (`trr-D6-line-endings.txt`) |
| Home path | `check_home_path: ok` (`trr-D6-home-path.txt`) |
| Task contract | `2 row(s) exempt (view_file): H1-5, H2-1` (`trr-D6-task-contract.txt`) |
| Host load | `host-load: ran at 9 %` (`trr-D6-host-load.txt`) |
| Dev proof (variable set) | `window: yes (after 16 s; window)`, `notice: yes`, `left: 0`, `PASS: window opened, notice as expected, nothing left` (`trr-D6-dev-proof-set.txt`) |
| Python, three files | `74 passed in 8.18s` (`trr-D6-py-two.txt`); `wait-check: PASS` (`trr-D6-wait-check.txt`) |
| Python, full | `3087 passed, 37 warnings in 243.99s (0:04:03)` (`trr-D6-py-tests.txt`) |
| UI unit, targeted | `Tests  10 passed (10)` (`trr-D6-ui-unit.txt`) |
| UI unit, full | `Test Files  142 passed (142)`, `Tests  1619 passed (1619)` (`trr-D6-ui-tests.txt`; row 0 had 1614) |
| Build | `built in 4.20s` (`trr-D6-ui-build.txt`) |
| Electron E2E, full | `226 passed (7.1m)`, 0 `unhandled rejection:` lines (`trr-D6-ui-electron.txt`) |
| Registers | `OK: known-issues.md is up-to-date` (`trr-D6-issues-render-check.txt`); the state render's drift check passed (`trr-D6-state-render.txt`) |
| H1-3 | the state render's drift check passed after the current-focus paragraph (`trr-render-check.txt`) |
| H1-4 | `packages, mcp-server or tools changes since row 0: []` (`skip-basis-check.txt`); so pyright, OpenAPI and MCP are skipped (S13) |

The gate's Electron step passed on its first run, so D-1123's rerun rule for it was not needed.

---

## Changed Files

Counts are added / removed lines against `HEAD` `79e3fa5` (`git diff --numstat --ignore-cr-at-eol`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step, `trr-D6-line-endings.txt`).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `tests/integration/test_tts_assets.py` | `WORKER_WAIT` block at `:31-33`; eleven waits read `WORKER_WAIT_S` | +14 / -11 | CRLF kept |
| `tests/integration/test_youtube_adapter.py` | `WORKER_WAIT` block at `:106-108`; the join at `:942` | +4 / -1 | CRLF kept |
| `ui/tests/e2e/main-error-watch.cjs` | `REJECTION_WATCH`, `REJECTION_WARNING_LINE`; header comment | +17 / -2 | LF kept |
| `ui/tests/e2e/electron-env.ts` | `MAIN_REJECTION_MARKER`; `kind?: 'rejection'` on `MainErrorRecord` | +8 / -0 | LF kept |
| `ui/tests/e2e/electron-app.ts` | `REJECTION_FAILS_CLOSE` at `:59-60`; header and doc comments | +4 / -3 | LF kept |
| `ui/package.json` | `:16` only (`DEV_SCRIPT`) | +1 / -1 | CRLF kept |
| `ui/scripts/electron-vite-dev.mjs` | new: `DEV_ENV_CLEARED`, `DEV_NOTICE`, `DEV_ARGS`, `DEV_SIGNALS`, `DEV_ENTRY_ONLY` | 79 lines | LF |
| `ui/tests/unit/rejection-watch.test.ts` | new: AC-6 to AC-8 | 100 lines | LF |
| `ui/tests/unit/dev-script.test.ts` | new: AC-13, AC-14 | 66 lines | LF |
| `ui/tests/e2e/main-rejection-watch.test.ts` | new: AC-9 to AC-11 | 114 lines | LF |
| `.agent/docs/commands.md` | `COMMANDS_DOC`: `:78` rewritten, `:80` inserted | +2 / -1 | CRLF kept |
| `.agent/context/known-issues.yaml` | three issues resolved (`issue-resolve.py`); `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` added (`issue_triage.py add`) | +26 / -3 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` | +4 / -6 | LF |
| `.agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md` | row 90 (`:125`): `executed (Session 90)` and the plan folder | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 90 paragraph (H1-3) | +3 / -0 | CRLF kept |
| `docs/execution/plans/2026-11-17-test-run-reliability/` | the plan (D-1122 and D-1123 added in execution), task (row marks), the plan-local scripts (`baseline.ps1`, `identity.py`, `red-check.py`, `eol-check.py`, `issue-resolve.py`, `wait-check.py`, `load-run.py`, `slow_worker.py`, `dev-proof.py`), the row-0 records and `session-gate.ps1` | new folder | LF |

**The four bound-only assertion edits (`WAITS_NAMED`).** In `tests/integration/test_tts_assets.py`, and only their bound changes:

| Line now (row 0) | Old | New |
|------------------|-----|-----|
| `:958` (`:955`) | `assert gated.entered.wait(5.0)` | `assert gated.entered.wait(WORKER_WAIT_S)` |
| `:966` (`:963`) | `assert tts.wait_idle(5.0) is True` | `assert tts.wait_idle(WORKER_WAIT_S) is True` |
| `:980` (`:977`) | `assert gated.entered.wait(5.0)` | `assert gated.entered.wait(WORKER_WAIT_S)` |
| `:987` (`:984`) | `assert tts.wait_idle(5.0) is True` | `assert tts.wait_idle(WORKER_WAIT_S) is True` |

What each asserts is unchanged: the gated generate was entered, and the TTS service went idle. No other assertion line in either file changed (`trr-wait-check.txt`: TTS `'assert_lines_changed': [955, 963, 977, 984]`, YouTube `[]`), including the row-0 `:260`, `:940` and `:964`. The other replaced lines are non-assertion waits: TTS row-0 `:62` (now `:65`, the fake upstream's hold), `:177` (now `:180`, `wait_idle`'s default), `:227`, `:526`, `:712`, `:896` (`_poll_tts`'s default) and `:938` (the release wait), and YouTube row-0 `:939` (the join). `tests/integration/test_tts_voice_packs.py:249` and `:320` reach the changed `wait_idle` default with their text unchanged (the cross-reference row above). The suite-wide `checkMainErrors` condition is its own cross-reference row. Line numbers in the cross-reference rows are the current files' unless marked row 0; the plan's §Test pins gives them at `HEAD` `79e3fa5`.

**The constant block** (both files; the text is `wait-check.py`'s `CONSTANT_BLOCK`):

```text
# Upper bound for a fake worker's signal. Each wait returns as soon as its signal arrives,
# so the bound only matters on a loaded host (PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD, Session 90).
WORKER_WAIT_S = 60.0
```

**`checkMainErrors`** (`ui/tests/e2e/electron-app.ts:59-60`): old `'main-process uncaught exception(s):\n' + records.map((r) => r.stack ?? r.raw).join('\n---\n')`; new `'main-process uncaught exception(s) or unhandled rejection(s):\n' + records.map((r) => (r.kind === 'rejection' ? 'unhandled rejection: ' : '') + (r.stack ?? r.raw)).join('\n---\n')`.

**`ui/package.json:16`**: old `    "dev": "electron-vite dev",`; new `    "dev": "node ./scripts/electron-vite-dev.mjs",`.

Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No findings: the round 1 review's Findings table is empty.

### Verdict

`approved` at round 1 of 6, with 0 findings and 0 blocking, intent achieved (`.agent/context/handoffs/2026-11-17-test-run-reliability-implementation-critical-review.md`, a byte-for-byte copy of the reviewer's report; ledger loop `trr-execution-2026-11-17-test-run-reliability`, round 1 `verdict=approved agent='codex-independent-reviewer' blocking=0 intent_achieved=yes usage=12,731,427`). The loop began with the plan's goal anchor and AC list and no `--token-budget` (OK line `mode=execution budget=6 tokens=off`; `review_ledger.py state` read `rounds 0/6` before the round). Dispatch `trr-exec-r1` ran with `-Kind execution`; its console is `trr-exec-console-r1.txt` in the dispatch folder. The reviewer's own `identity.py --state-only` (with `ELECTRON_RUN_AS_NODE` unset) returned the gate's tested_state `79e3fa58501db96e5cce4796c5146963a00748c2+598a3a2bcdee031b522500a4189c78915d4795f7c84ef9d22c6b15feb80feca8` exactly (review §Q7). The review schema has no top-level `tested_state` property, so its value is recorded in the checklist evidence. It accepted WORKER_WAIT, WAITS_NAMED, WAIT_SIGNALS_KEPT and TIME_GUARD (§Q2); REJECTION_WATCH, REJECTION_WARNING_LINE, MAIN_REJECTION_MARKER, REJECTION_FAILS_CLOSE and EXCEPTION_WATCH_KEPT (§Q3); DEV_ENV_CLEARED, DEV_NOTICE, DEV_ARGS, DEV_SIGNALS, DEV_ENTRY_ONLY, DEV_SCRIPT, DEV_PROOF and PREVIEW_REGISTERED (§Q4); and AC-17 and COMMANDS_DOC (§Q6). Its independent comparison found all 221 baseline skip hashes unchanged (S13) and its recount found 226 unique sequential results in each inspected full receipt (§Q5). On row 5 it wrote that D-1122 was "permissible but unnecessary under S5", and that D-1123 is "accepted as the plan's pre-existing S5 exception, with the failed initial full run preserved and disclosed; approval does not relabel it a clean first-pass run." Row 5's attempt 3 is therefore three complete full runs, two clean and one with a failure resolved by S5's lone rerun, not three clean first passes. Residuals it names: the disclosed intermittent pointer and launch-teardown flakes and the registered preview gap. H1-7a: `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0` (`review-state-check.txt`, `review-state.json`). H1-7b: `OK: approved at round 1 of 6, 0 open blocking findings` (`exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The other 125 five-second waits of the same pattern in other test files | out-of-scope | — | None has failed; D-1115 |
| `npm --prefix ui run preview` with `ELECTRON_RUN_AS_NODE` set | registered | `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` (open) | D-1119 |
| The real-pointer and launch-teardown flakes seen in row 5's full runs | existing issues | `DOWNLOAD-QUEUE-DRAG-OVER-MISS`, `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`, `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` (all open) | No spec failed twice; S5 did not fire (D-1123). The Convert drag at `convert-queue.test.ts:1182` and the three capture specs that no issue names exactly are left for the next triage to file or fold in |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **Status line.** The coordinator wrote the execution approval into the plan's Status line (`implementation-plan.md:15`) before execution began; that is the only change since the plan review, and the plan's sha256 moved from `7299e6159b3a…` to `57a13aeb1251…`. D-1122 and D-1123 were then added to the plan's decision YAML; the plan's sha256 was then `f5c5d09b2f2a2c15520ee0df4fc06b11d86ad05cbdf594f236ae82257fe53be2`, the value the execution review read. After the review, at H2-2, the decision-source reader refused the plan because D-1117's `chosen` held two angle-bracket tokens it reads as template slots; that one line (`:428`) now says "and the rejection's stack" and "and the rejection's message" in their place, with the same meaning, and the plan's sha256 is `79a8ad52ad5284e2d869abd214629e805958ff0460dc44d1730a8e2496f03a5f`. The plan is outside `identity.py`'s inputs, and the state did not move (`trr-decision-probe-after.txt`). `task.md` changed only by its row marks. The plan review's sha256 is `3939ffb08149f24c8bf0840cc0ec0fb9e4d5495ce7a2d8434dacb809978b77b8`.
- **Row 5 ran in three attempts (D-1122, D-1123).** Attempt 1's third full run failed one spec that passed alone; under the coordinator's brief (a single failure that passes alone gets one full rerun of the row) the row ran again. Attempt 2's first full run failed five specs that passed alone, and the brief's rule (stop after a second failing full run) stopped it; its runs 2 and 3 were not run. D-1122 ordered attempt 3 with a load probe before each full run. Attempt 3's third run failed one spec that passed alone, and the brief's rule stopped it again. D-1123 ruled that row 5's full runs are complete under the plan's own S5 rule and that the rest of the cell runs without rerunning the full suites. Every attempt's receipts are kept under their own names, and every full run held 0 rejection records.
- **`run-row5-rest.ps1` (D-1123).** The rest of row 5's cell (typecheck, lint, `eol-check.py` and the final check) ran from a separate script, built from the cell with its own environment prefix by `trr-make-row5-rest.py`; the unit, build, targeted E2E and full runs were not rerun. The attempt-3 runner itself exited 1 at full run 3.
- **The load probe.** A load probe (`trr-probe.ps1`: wait until the host load reads 50 % or less, 30 s apart) ran before row 5 attempt 3 and each of its full runs, before rows 6 and 7 and before the H1-2 gate, under the coordinator's brief. It is outside the cells; the cells' own host-load steps ran as written.
- **`py-tests` in the gate** runs `uv run --no-sync pytest tests/ -x`, so the gate does not re-sync the environment while other sessions use it; the argv is otherwise D6's.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file (an environment header, then the cell) and run with `pwsh -NoProfile -File`.
- **Two foreign AC ids in prose.** The H1-6 validator's coverage check refused the first draft because the plan's D-1122 and D-1123 text names AC-49.29 and AC-81.11. The handoff names them once, in prose under the row-5 failing-specs table, mapped to their file and line; no AC table row carries them (Session 83 RULE-1).
- **Execution decisions** D-1122 and D-1123 are in the plan's decision YAML, each `resolution: autonomous`, `class: two-way`, `mandatory: none`; D-1115 to D-1120 are the plan's. So the Decision Log below is `None.`.

### Execution notes

- **Lesson for H2-2's reflection.** The coordinator's brief told the executor to stop at a second failing full run, which was stricter than the plan's S5 rule (a failure with no rejection record is rerun alone once, and only a repeat failure stops). That stricter rule stopped row 5 twice when S5 had not fired, cost a second and third attempt of the full suite on a shared host, and needed D-1122 and D-1123 to resolve. A brief that adds a stop rule should say how it relates to the plan's own stop conditions, or defer to them.
- **The decisions.** D-1115: the twelve waits become `WORKER_WAIT_S = 60.0` and the other 125 are left. D-1116: every rejection fails the close, none allowlisted; a rejection found later goes to `known-issues.yaml` with its stack. D-1117: the compatibility line keeps `UnhandledPromiseRejectionWarning` on stderr, and `capture-inbox.test.ts` stays byte-identical. D-1118: the wrapper script. D-1119: preview is registered, not fixed. D-1120: the proofs. D-1122: attempt 3 of row 5. D-1123: row 5's full runs are complete under S5; the gate and any later Electron run treat a rejection record as S10 and rerun a no-record failure alone once.
- **Processes.** Each proof and run stopped only the processes it recorded, by id and creation time. The eight `electron.exe` processes that were running before this session's Electron runs belong to other sessions; none was stopped.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-17 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
| Reviewed | 2026-11-17 | codex-independent-reviewer | H1-7 execution review round 1: `approved`, 0 findings; the Codex Validation Report is filled from it |
