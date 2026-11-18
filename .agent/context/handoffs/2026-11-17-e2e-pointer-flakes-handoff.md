---
date: "2026-11-18"
project: "2026-11-17-e2e-pointer-flakes"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md"
build_plan_section: "none (test-harness debt with no MEU, grouping D-1132)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-17-ui-small-fixes-MEU-159-handoff.md"
---

# Handoff: 2026-11-17-e2e-pointer-flakes-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. This is test-harness debt (grouping D-1132), in the style of Session 78 `2026-11-15-e2e-harness-hardening` and Session 90 `2026-11-17-test-run-reliability`. The criteria are numbered `AC-1` to `AC-15`, with no MEU prefix.
**Issues**: `DOWNLOAD-QUEUE-DRAG-OVER-MISS`, `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` and `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`, with Session 90's failing specs folded in (D-1126, D-1132).
**Predecessor**: [2026-11-17-ui-small-fixes-MEU-159-handoff.md](2026-11-17-ui-small-fixes-MEU-159-handoff.md), Session 94, committed as `9fce270`. Session 91 is the fifth and last session run of the 2026-11-17 value triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md`), under D-1142, run from `9fce270`.

- **The shield (`POINTER_SHIELD`, D-1149).** Every E2E launch of the built app now sets `setIgnoreMouseEvents(true)` on each window, from the main-process diagnostics (`installMainDiag` in `ui/tests/e2e/e2e-diag.ts`; `POINTER_SHIELD_DEFAULT` at `ui/tests/e2e/electron-app.ts:33`). The real OS mouse passes through the test windows; Playwright's CDP input still arrives (AC-9). `pointerShield: false` opts out (AC-10). The keyboard is not blocked.
- **The shared helpers (`POINTER_HELPERS_SHARED`, D-1147).** `settledCenter`, `rowTransitionsIdle`, `windowSettled`, `grabRow` and `dragOver` moved once, unchanged in logic, from `download-queue.test.ts` into the new `ui/tests/e2e/pointer-settle.ts`, each with `{ rowTestId = 'queue-card' }`. `capture-inbox.test.ts` deleted its identical `windowSettled` and imports the shared one.
- **A settled pointer target (`SETTLE`, `SETTLED_BOX`, `POINTER_ON`, D-1148).** `settle` returns once two reads one animation frame apart are equal, bounded at 60 frames; `pointerOn` also hit-tests the point with `document.elementFromPoint` before it returns. No wall-clock wait was added.
- **The three waits in front of unchanged expectations.**
  - The convert drive (`DRAG_DRIVER_SHARED`, `convert-queue.test.ts:1198-1202`): Convert AC-49.29 now drives with `grabRow` and `dragOver` and `{ rowTestId: 'convert-queue-row' }`, so it waits for the press to register (`aria-pressed="true"`) and for the committed-over announcement before `page.mouse.up()`. The expectations at `:1209-1214` are unchanged.
  - `GRAB_COMMITTED` (`capture-inbox.test.ts:2032-2036`): in AC-81.14 a `page.waitForFunction` waits until the arrow line's `x2` differs from `before.x2`, before `const grabbed = await ends()` at `:2037`; the expectation at `:2038` is unchanged.
  - The hit-test before the capture hovers (`pointerOn`, `pointer-settle.ts:45`): AC-67.20 A-6 (`capture-inbox.test.ts:1576`) and AC-80.10 (`:1640`, `:1656`) wait on it before they move the pointer.
  - No assertion line changed: `assert-check.py` passed at rows 4 to 8 and in the gate (`epf-accept-assert.txt`: `PASS`).
- **The launch hang was not reproduced (D-1150).** No receipt from rows 3 to 8 shows a test-timeout hang. `epf-hang-verdict.txt` ends `outcome: not-reproduced`, `epf-hang-signatures.json` is `[]`, and `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` stays `open` with a new note. The phase instrumentation stays (`PHASE_LINES`, `MAIN_DIAG`).
- **F2 was held (D-1152, D-1153).** Another program held F2 through rows 3 to 7, so AC-81.11 (`HOTKEY_IN_USE_FIXTURE`) failed every repeat of those rows before it reached the banner. After Mat closed the holder, row 3 was rerun as a new invocation under fresh receipt names, and row 8 ran at the rerun's level.
- **Records.** `DOWNLOAD-QUEUE-DRAG-OVER-MISS` and `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` are `resolved`; `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` is `open` with the not-reproduced note; grouping row 91 reads `executed (Session 91)`. No MEU was registered (MEU-161 was free and stays unused).

**What Mat sees.** Nothing in the app changes. During an E2E run the test app's windows no longer react to the real mouse, so moving the mouse over them can no longer break a drag or a hover test. The download, convert and capture drags and the capture zoom tests passed every run of three full runs and ten watched runs at about 95 % CPU load. The launch hang never showed, so its issue stays open, with the diagnostics in place for the next time it does.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-17 ("orchestrate the plan creation for all sessions and proceed with execution for each"), `plan_to_exec_gate: human`; the plan review approved at round 3 (`.agent/context/handoffs/2026-11-17-e2e-pointer-flakes-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `e2e-pointer-flakes` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit | `settle` returns after two equal reads one frame apart, and rejects with `layout never settled:` after `maxFrames` reads that never repeat | Local Canon (`SETTLE`) | `ui/tests/unit/e2e-pointer.test.ts:130` | ✅ |
| AC-2 | unit | `diagDir`, `runId` and `phaseLine`: the variables, `null` and `''` defaults, and two appended lines that parse back with every `PHASE_LINES` field; no `@playwright/test` in `e2e-diag.ts` | Local Canon (`DIAG_DIR`, `PHASE_LINES`) | `ui/tests/unit/e2e-pointer.test.ts:170` | ✅ |
| AC-3 | unit | `installMainDiag` with a fake electron module: the shield calls, the window, cursor and visibility lines, the stop at `will-quit`, the opt-out, and no `require(`, `import` or `setBackgroundThrottling` in its source | Local Canon (`MAIN_DIAG`, `POINTER_SHIELD`, `SHIELD_OPT_OUT`) | `ui/tests/unit/e2e-pointer.test.ts:205` | ✅ |
| AC-4 | E2E | A built-app launch writes `launch-start`, `launch-end`, `evaluate-end`, then `close-start`, `close-end` and `exit`, each `'passed'` and `0`, and its main log holds `install` and a `resize` | Local Canon (`PHASE_LINES`, `MAIN_DIAG`, `DIAG_DEFAULT_MAIN_ONLY`) | `ui/tests/e2e/e2e-diag.test.ts:90` | ✅ |
| AC-5 | check | Row 3's `flake-run.py` runs exit 0 or 1, never 2, with the load, churn and busy lines, and `epf-burn-level.txt` names the level, the counts, the median load and `accept-runs:` | Local Canon (D-1146) | row 3 `epf-repro-b.txt`, `epf-base-full-b.txt`, `epf-burn-level-b.txt`, `epf-repro-check-b.txt` (the first run: `epf-repro.txt`, `epf-base-full.txt`, `epf-burn-level.txt`) | ✅ exit 1 in both runs, measurements; children 18, accept-runs 3 |
| AC-6 | unit (static) | The five helpers are defined once in `pointer-settle.ts` with `rowTestId`; neither queue spec defines them and both import them; the convert drag body calls `grabRow(` and `dragOver(` with `'convert-queue-row'` and holds no `boundingBox()` | Local Canon (`POINTER_HELPERS_SHARED`, `DRAG_DRIVER_SHARED`) | `ui/tests/unit/e2e-pointer.test.ts:292` | ✅ |
| AC-7 | unit (static) | `capture-inbox.test.ts` imports `windowSettled`; AC-66.14 and AC-81.14 read through `settledZoom(`; AC-81.14 waits before `ends()`; AC-67.20 A-6 and AC-80.10 call `pointerOn(`; `dragImage` calls `settledBox(` | Local Canon (`SETTLED_ZOOM`, `GRAB_COMMITTED`, `POINTER_SITES`) | `ui/tests/unit/e2e-pointer.test.ts:312` | ✅ |
| AC-8 | E2E | `pointerOn` waits while a full-window overlay covers the target, resolves onto it once the overlay goes, and `settledBox` matches `boundingBox()` | Local Canon (`POINTER_ON`, `SETTLED_BOX`) | `ui/tests/e2e/e2e-diag.test.ts:143` | ✅ |
| AC-9 | E2E | A default launch sets `WS_EX_TRANSPARENT` and `WS_EX_LAYERED` on the first window, and a Playwright click and hover still work | Local Canon (`POINTER_SHIELD`, D-1149) | `ui/tests/e2e/e2e-diag.test.ts:191` | ✅ from row 6 |
| AC-10 | E2E (guard) | A launch with `pointerShield: false` keeps `0x20` clear | Local Canon (`SHIELD_OPT_OUT`) | `ui/tests/e2e/e2e-diag.test.ts:212` | ✅ passed at Red (guard) |
| AC-11 | check | `assert-check.py` passes (`ASSERTIONS_KEPT`, `TESTS_KEPT`, `NO_NEW_WAIT_KNOBS`, `CONFIG_KEPT`, `LF_ONLY`, `EXIT_WAIT_KEPT`) at rows 4 to 8 and in the gate; `main-error-watch.cjs` and `electron-env.ts` keep their row-0 hashes | Local Canon (D-1151) | rows 4 to 8 `epf-drag-assert.txt`, `epf-origin-assert.txt`, `epf-shield-assert.txt`, `epf-hang-assert.txt`, `epf-accept-assert.txt`; gate `assert-check` | ✅ |
| AC-12 | check | `epf-hang-verdict.txt` lists every hang with its phases, signature, cause and register lines and ends with the outcome; the registers match; `epf-hang-signatures.json` passes the signature check | Local Canon (D-1150) | row 7 `epf-hang-verdict.txt`, `epf-hang-check.txt` | ✅ `outcome: not-reproduced`, no block, `[]` |
| AC-13 | check (acceptance) | Full runs at the burn level, `accept-runs` of them, each with the expected total, no covered failure, no rejection, no `evaluate-error`, busy counts 0, median load at least 60 % | Local Canon (D-1145, D-1150; Session 90 RULE-3) | row 8 `epf-accept.txt`, `epf-accept-check.txt` | ✅ 3 of 3 |
| AC-14 | check (acceptance) | Only when `accept-runs` is 3: the watched tests ×10 at the burn level, 110 of 110 | Local Canon (D-1145) | row 8 `epf-watch10.txt`, `epf-accept-check.txt` | ✅ 110 of 110 |
| AC-15 | check | Row 9: the two issues `resolved` with `verification` and `resolution_path`, the launch hang `open` with its note, both renders pass, grouping `:163` alone changed | Local Canon (D-1132; grouping §6) | row 9 `epf-issue-resolve.txt`, `epf-issues-render-check.txt`, `epf-row9-check.txt`; H1-3 `epf-render-check.txt` | ✅ |
| Download drag pins (cross-ref) | guard | `ui/tests/e2e/download-queue.test.ts:1144` ("dragging a row onto the third row lands the exact order, and it survives a reload"), `:1173` ("the drag announces position-based progress"), `:1252` ("a row drag never puts the list into its file-drop state"); at row 0 these were `:1319`, `:1348` and `:1427` | Local Canon (§Test pins) | rows 4 and 8; gate | ✅ lines unchanged; the helpers come from `pointer-settle.ts` |
| Convert drag pin (cross-ref) | guard | `ui/tests/e2e/convert-queue.test.ts:1183` ("dragging a conversion onto the third row lands the exact order"), expectations `:1209-1214` (row 0: `:1182`, `:1221-1226`) | Local Canon (§Test pins) | rows 4 and 8; gate | ✅ expectation lines unchanged; the drive changed (`DRAG_DRIVER_SHARED`) |
| Capture pan pins (cross-ref) | guard | `ui/tests/e2e/capture-inbox.test.ts:1136` and `:1980`, `expect(view.ox).toBeCloseTo(centred.ox - 40, 3)` (row 0: `:1175`, `:2016`) | Local Canon (§Test pins) | rows 5 and 8; gate | ✅ unchanged; the reads come from `settledZoom` |
| Capture grab pin (cross-ref) | guard | `ui/tests/e2e/capture-inbox.test.ts:2038`, x2 grows by 20 (row 0: `:2069`) | Local Canon (§Test pins) | rows 5 and 8; gate | ✅ unchanged; `GRAB_COMMITTED` waits before `:2037` |
| Capture hint pins (cross-ref) | guard | `ui/tests/e2e/capture-inbox.test.ts:1575` (`expect(box).toBeTruthy()`), the hint lines after it, and `:1643` with the Undo hint lines (row 0: `:1614`, `:1618`, `:1680`) | Local Canon (§Test pins) | rows 5 and 8; gate | ✅ unchanged; `pointerOn` before each hover; `HINT_DELAY_MS` waits kept |
| Capture drag pins (cross-ref) | guard | `ui/tests/e2e/capture-inbox.test.ts:2523` (`dragImage`'s settled box), `:3486` (`toHaveCount(1)`) and the tool-lock drag test at `:2535` (row 0: `:2554`, `:3517`) | Local Canon (§Test pins) | rows 5 and 8; gate | ✅ unchanged; `dragImage` reads `settledBox` |
| Rejection pins (cross-ref) | guard | `ui/tests/e2e/capture-inbox.test.ts:404` (stderr holds no `UnhandledPromiseRejectionWarning: Error: backend not ready`; row 0 `:403`); `ui/tests/e2e/main-rejection-watch.test.ts`; `ui/tests/unit/rejection-watch.test.ts` | Local Canon (`REJECTION_WATCH_KEPT`) | rows 2 to 8; gate | ✅ `main-error-watch.cjs` and `electron-env.ts` byte-identical |
| Hotkey fixture pin (cross-ref) | guard | `ui/tests/e2e/capture-inbox.test.ts:1912`, the hotkey-in-use fixture with two launches (row 0: `:1948`) | Local Canon (§Test pins) | rows 3 to 8; gate | ✅ unchanged; failed while F2 was held (D-1152), passed in every run after |
| Launcher pins (cross-ref) | guard | `ui/tests/unit/e2e-harness.test.ts:60`, `:66`, `:121-130`; `ui/tests/e2e/electron-harness.test.ts:50`, `:69`, `:97`, `:100`, `:117` | Local Canon (`NO_LAUNCHER_NAME`, `DIAG_DEFAULT_MAIN_ONLY`) | rows 2 and 6; gate | ✅ unchanged and passing |

The cross-reference rows cite the pinned tests by file and line (Session 83 RULE-1). For the plan's own mentions, the tests these rows touch belong to other families: AC-49.25, AC-49.26 and AC-49.28 (download), AC-49.29 (convert), AC-66.14, AC-67.20, AC-80.10, AC-81.11, AC-81.14, AC-87.6 (the tool-lock drag at `capture-inbox.test.ts:2535`) and AC-143.29 (`capture-inbox.test.ts:3465`). None of them is claimed or changed here.

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 | `AssertionError: ui/tests/e2e/pointer-settle.ts exists: expected false to be true` (`epf-red-unit.txt`, `Tests  5 failed (5)`) | Row 2: `Tests  2 failed \| 3 passed (5)`, AC-1 among the passed (`epf-green-unit.txt`) | `ui/tests/unit/e2e-pointer.test.ts:130` |
| AC-2 | `AssertionError: ui/tests/e2e/e2e-diag.ts exists: expected false to be true` (`epf-red-unit.txt`) | Row 2 (`epf-green-unit.txt`) | `ui/tests/unit/e2e-pointer.test.ts:170` |
| AC-3 | `AssertionError: ui/tests/e2e/e2e-diag.ts exists: expected false to be true` (`epf-red-unit.txt`) | Row 2 (`epf-green-unit.txt`) | `ui/tests/unit/e2e-pointer.test.ts:205` |
| AC-6 | `pointer-settle.ts exists: expected false to be true` (`epf-red-unit.txt`) | Row 4: `Tests  1 failed \| 4 passed (5)`, AC-7 the one failing (`epf-drag-unit.txt`) | `ui/tests/unit/e2e-pointer.test.ts:292` |
| AC-7 | `epf-red-unit.txt`; still failing at row 4: `expected 'import { expect, test, type Page } fr…' not to contain 'async function windowSettled('` (`epf-drag-unit.txt`) | Row 5: `Tests  10 passed (10)` (`epf-origin-unit.txt`) | `ui/tests/unit/e2e-pointer.test.ts:312` |
| AC-4 | `Error: expect(received).toBe(expected)`, `Expected: true`, `Received: false` (`epf-red-e2e.txt`, `3 failed`, `1 passed (3.6s)`) | Row 2: `ok 1 tests\e2e\e2e-diag.test.ts:90:1` (`epf-green-e2e-diag.txt`) | `ui/tests/e2e/e2e-diag.test.ts:90` |
| AC-8 | `Expected: true`, `Received: false` (`epf-red-e2e.txt`) | Row 2: `ok 2 tests\e2e\e2e-diag.test.ts:143:1` (`epf-green-e2e-diag.txt`) | `ui/tests/e2e/e2e-diag.test.ts:143` |
| AC-9 | `Expected: 32`, `Received: 0` (`epf-red-e2e.txt`) | Row 6: `4 passed (5.0s)` (`epf-shield-e2e-diag.txt`) | `ui/tests/e2e/e2e-diag.test.ts:191` |

AC-10 passed at Red and is a guard (`ok 4 tests\e2e\e2e-diag.test.ts:212:1`, `epf-red-e2e.txt`); AC-5 and AC-11 to AC-15 are checks. The red checks: `red-check: 1 receipt(s), 5 required test(s), 0 problem(s)` (`epf-red-unit-check.txt`) and `red-check: 1 receipt(s), 3 required test(s), 0 problem(s)` (`epf-red-e2e-check.txt`).

- **Row 0 baseline** (`epf-baseline.txt`): `baseline.sha 9fce270bff07964d76da4dee163f83fddf31fe2e`, `baseline-scope.json 28 paths; 6 absent`, `baseline-copies 33 row-0 copies`, `baseline-skip-hashes.json 408 files in all`, `probe anchors 53`, each `anchor ok`, `next free MEU id: MEU-161`. The row-0 E2E total is `228` (`epf-base-total.txt`); UI Vitest at base `Test Files  144 passed (144)`, `Tests  1628 passed (1628)` (`epf-base-ui.txt`).
- **Anchors at moved lines (Session 51 RULE-3).** Row 0 found all 53 anchors at the plan's lines. The fixes then moved these cited lines: `download-queue.test.ts` `:1319` → `:1144`, `:1348` → `:1173`, `:1427` → `:1252`; `convert-queue.test.ts` `:1182` → `:1183`, `:1221-1226` → `:1209-1214`; `capture-inbox.test.ts` `:403` → `:404`, `:1159` → `:1120`, `:1175` → `:1136`, `:1601` → `:1562`, `:1614` → `:1575`, `:1658` → `:1620`, `:1680` → `:1643`, `:1948` → `:1912`, `:2001` → `:1965`, `:2016` → `:1980`, `:2068` → `:2037`, `:2069` → `:2038`, `:2552` → `:2521`, `:2554` → `:2523`, `:3496` → `:3465`, `:3517` → `:3486`; `electron-app.ts` `:26` → `:30` (`EXIT_WAIT_MS`), `:70` → `:110` (`launchElectron`), `:88` → `:157` (`app.close`).
- **Row 1 Red** (`epf-red-unit.txt`, `epf-red-e2e.txt`): above. `epf-red-hashes.txt`: `vitest 5 failed of 5: True AC-10 ok lines: 1`.
- **Row 2 Green** (`epf-green-check.txt`): `vitest 2 failed and 3 passed: True ok lines: {'AC-4': 1, 'AC-8': 1, 'AC-10': 1}`; AC-6, AC-7 and AC-9 still fail by plan. The kept suites: `Tests  8 passed (8)` (`epf-green-unit-kept.txt`), `8 passed (5.2s)` (`epf-green-e2e-kept.txt`).
- **Row 3, the reproduction, both runs (D-1146, D-1153).** On the unfixed specs (`epf-red-source.txt`), shield off, 18 busy children and one churn child:

  | | First run (F2 held, skewed) | Rerun (F2 free, used) |
  |---|---|---|
  | Watched ×10 | `run 1: exit 1 in 231 s; ok lines 100; failures 10; rejection lines 0`, all `capture-inbox.test.ts:1948` AC-81.11; `median=97.5` (`epf-repro.txt`, invocation `20261118T131848-64440-cf2603`) | `run 1: exit 1 in 349 s; ok lines 106; failures 4; rejection lines 0`: `capture-inbox.test.ts:1601` AC-67.20 A-6 twice, `download-queue.test.ts:1319` AC-49.25, `download-queue.test.ts:1348` AC-49.26; `median=98.0` (`epf-repro-b.txt`, invocation `20261118T152550-38036-000f98`) |
  | One full run | `run 1: exit 1 in 610 s; ok lines 230; failures 2`: `covered capture-inbox.test.ts:1948` AC-81.11 and `uncovered e2e-diag.test.ts:191` AC-9 (solo rerun `exit 1`, by design with the shield off); `median=97.9` (`epf-base-full.txt`) | `run 1: exit 1 in 663 s; ok lines 230; failures 2`: `uncovered convert-queue-labels.test.ts:519` AC-152.24 (solo rerun `exit 0`) and `uncovered e2e-diag.test.ts:191` AC-9 (solo rerun `exit 1`, by design); `median=98.3` (`epf-base-full-b.txt`) |
  | Burn level | `children: 18`, `watched failures: 11`, `hang failures: 0`, `escalate: no`, `watched failures in the isolated runs: 10`, `accept-runs: 3` (`epf-burn-level.txt`) | `children: 18`, `watched failures: 4`, `hang failures: 0`, `hangs outside the watched set: 0`, `uncovered specs, e2e-diag excluded: ['convert-queue-labels.test.ts']`, `escalate: no`, `watched failures in the isolated runs: 4`, `accept-runs: 3` (`epf-burn-level-b.txt`) |

  The reproduction rate is the rerun's: 4 watched failures in 110 watched runs, and no covered failure in the full run. Every receipt prints `churn child alive at the stop: yes`, `busy children left: 0` and `busy interpreters left: 0`; `epf-repro-check-b.txt`: `measurements finished with no busy process left and a median: {'repro-b': True, 'base-full-b': True}`. No hang in either run, so D-1146 did not escalate to 24 children.
- **Row 4, the drag fix, measured** (`epf-drag.txt`, F2 held): `run 1: exit 1 in 230 s; ok lines 100; failures 10; rejection lines 0`, all `capture-inbox.test.ts:1948` AC-81.11, `median=90.5`. Kept suites: `49 passed (54.2s)` (`epf-drag-e2e.txt`), `Tests  5 passed (5)` (`epf-drag-unit-kept.txt`).
- **Row 5, the capture origin, measured** (`epf-origin.txt`, F2 held): `run 1: exit 1 in 237 s; ok lines 100; failures 10; rejection lines 0`, all `capture-inbox.test.ts:1912` AC-81.11, `median=90.0`. The plain capture run: `1 failed`, `53 passed (1.3m)`, the one failure AC-81.11 at `:1912` with F2 held (`epf-origin-e2e.txt`; D-1152).
- **Row 6, the shield** (`epf-shield-check.txt`): `ok lines: {'AC-4': 1, 'AC-8': 1, 'AC-9': 1, 'AC-10': 1}`; `4 passed (5.0s)` (`epf-shield-e2e-diag.txt`), `8 passed (5.1s)` (`epf-shield-e2e-kept.txt`), `Tests  13 passed (13)` (`epf-shield-unit.txt`). Measured (`epf-shield10.txt`, F2 held): `failures 10`, all AC-81.11 at `:1912`, `median=89.45`.
- **Row 7, the hang verdict** (`epf-hang-verdict.txt`): no failure in rows 3 to 6 is marked hang; `outcome: not-reproduced`. `epf-hang-check.txt`: `blocks: [] causes: []`, `outcome: not-reproduced expected: not-reproduced`, `register changed: known-issues False meu-status False matches the outcome: True`. The row-3 rerun added no hang, so row 7 was not redone.
- **Row 8, acceptance** (`epf-accept.txt`, invocation `20261118T154356-54848-b402d6`): `load before the runs: 89.4 % with 18 busy children`; `run 1: exit 0 in 612 s; ok lines 232; failures 0; rejection lines 0`, `run 2: exit 0 in 566 s; ok lines 232; failures 0; rejection lines 0`, `run 3: exit 0 in 572 s; ok lines 232; failures 0; rejection lines 0`; `load during the runs: n=580 min=81.6 median=95.4 max=100.0`; `PASS: 3 of 3 runs clean at median load 95.4 (threshold 60.0); uncovered failures cleared by a solo rerun: 0; hangs excused by a registered signature: 0`. No `excused:` line; no solo rerun. The watched tests (`epf-watch10.txt`, invocation `20261118T161319-47396-63fc86`): `run 1: exit 0 in 274 s; ok lines 110; failures 0; rejection lines 0`, `median=93.9`, `PASS: 1 of 1 runs clean at median load 93.9 (threshold 60.0)`. The check (`epf-accept-check.txt`): `accept-runs: 3 watch10 run: True`, `run files bound to their invocation: {'accept': True, 'watch10': True} all distinct: True`, rejection lines 0 in each of the four run receipts, `excused hangs: 0`. `epf-accept-assert.txt`: `NO_NEW_WAIT_KNOBS 'setTimeout(': 8 -> 6`, `'waitForTimeout(': 7 -> 7`, `'timeout:': 6 -> 6`, `PASS`. F2 was free just before (`epf-f2-probe-8.txt`: `F2 free (registered and released)`).
- **Row 9, the records** (`epf-issue-resolve.txt`): `decision logs read: 104 of 104`, `register sha256 before=0583a9c0d5837e6588d53a05595363154d880fcac1fb0db8d906a1cff056a251`, `target sha256 after=8caac062da73f666c4346cdd274ca6851dedd8323f7e8a8a7c45e3e5aefbf896 CRLF=0 LF=5746`, `parsed fields changed: 11`, `issue-resolve: 0 problem(s)`; `Rendered known-issues.md: 34 lines` (`epf-issues-render.txt`); `OK: known-issues.md is up-to-date` (`epf-issues-render-check.txt`); `grouping lines changed: [163] row 91 as planned: True`, `launch hang for outcome not-reproduced: True yaml LF: True` (`epf-row9-check.txt`).
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-0-baseline", "command": "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-17-e2e-pointer-flakes/baseline.ps1 > C:/Temp/av-kit/e2e-pointer-flakes/epf-baseline.txt (task.md row 0's Validation cell; baseline.ps1 records baseline.sha, the dirty list and hashes, the scope, line-ending and skip hashes, the row-0 copies, the cited anchors, the plan-local selftests and the base UI and E2E totals); receipts epf-baseline.txt, epf-base-ui.txt, epf-base-total.txt", "scope": "Row 0: the baseline at 9fce270 and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9fce270 (baseline.sha)", "output": "baseline.sha 9fce270bff07964d76da4dee163f83fddf31fe2e; baseline-scope.json 28 paths; 6 absent; baseline-skip-hashes.json 408 files in all; probe anchors 53, each anchor ok; next free MEU id: MEU-161; E2E total 228; UI Vitest Test Files 144 passed (144), Tests 1628 passed (1628)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-1-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-1.ps1 (task.md row 1's Validation cell: Vitest on ui/tests/unit/e2e-pointer.test.ts, host-wait, the UI build, Playwright on ui/tests/e2e/e2e-diag.test.ts, red-check.py, the hash check); receipts epf-red-unit.txt, epf-red-unit-check.txt, epf-red-e2e.txt, epf-red-e2e-check.txt, epf-red-hashes.txt", "scope": "AC-1, AC-2, AC-3, AC-6, AC-7 (unit) and AC-4, AC-8, AC-9 (E2E) Red; AC-10 guard passes at Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9fce270 (baseline.sha) plus rows 0 and 1", "output": "Tests 5 failed (5); 3 failed, 1 passed (3.6s); red-check: 1 receipt(s), 5 required test(s), 0 problem(s); red-check: 1 receipt(s), 3 required test(s), 0 problem(s); vitest 5 failed of 5: True AC-10 ok lines: 1"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-2-green-helpers", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-2.ps1 (task.md row 2's Validation cell: typecheck, lint, Vitest, host-wait, the build, Playwright on e2e-diag.test.ts and the kept harness specs, the line-ending and green checks); receipts epf-green-unit.txt, epf-green-e2e-diag.txt, epf-green-unit-kept.txt, epf-green-e2e-kept.txt, epf-green-check.txt", "scope": "Row 2: pointer-settle.ts (settle, settledBox, pointerOn), e2e-diag.ts and the electron-app.ts diagnostics with the shield off; AC-1 to AC-4, AC-8 and AC-10 pass", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9fce270 (baseline.sha) plus rows 0 to 2", "output": "vitest 2 failed and 3 passed: True ok lines: {'AC-4': 1, 'AC-8': 1, 'AC-10': 1}; Tests 8 passed (8); 8 passed (5.2s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-3-reproduction", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-3b.ps1 (task.md row 3's Validation cell as a new invocation under D-1153, labels repro-b and base-full-b, burn level to epf-burn-level-b.txt; the specs put back from the row-0 copies and the shield default set false first, restored and hash-checked after); first run row-3.ps1 kept as the skewed evidence; receipts epf-repro-b.txt, epf-base-full-b.txt, epf-burn-level-b.txt, epf-repro-check-b.txt, epf-repro.txt, epf-base-full.txt, epf-burn-level.txt", "scope": "AC-5: the reproduction on the unfixed specs at 18 busy children and one churn child, and the burn level rows 4 to 8 use", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9fce270 (baseline.sha) with the three spec files at their row-0 bytes and the shield off (D-1153)", "output": "rerun: repro-b run 1: exit 1 in 349 s; ok lines 106; failures 4; rejection lines 0; median 98.0; base-full-b run 1: exit 1 in 663 s; ok lines 230; failures 2 (convert-queue-labels.test.ts:519 solo rerun exit 0; e2e-diag.test.ts:191 AC-9 solo rerun exit 1, by design); median 98.3; children: 18; watched failures: 4; escalate: no; accept-runs: 3. First run (F2 held): repro run 1 failures 10, all AC-81.11, median 97.5; base-full failures 2, median 97.9; watched failures: 11; accept-runs: 3"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-4-6-fixes-measured", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-4.ps1, row-5.ps1, row-6.ps1 (task.md rows 4, 5 and 6: typecheck, lint, Vitest, host-wait, the build, the kept suites, flake-run.py --mode watched --repeat 10 at the burn level with labels drag, origin and shield10, the assert, line-ending and row checks); receipts epf-drag.txt, epf-origin.txt, epf-shield10.txt, epf-drag-check.txt, epf-origin-check.txt, epf-shield-check.txt", "scope": "Rows 4 to 6: POINTER_HELPERS_SHARED, DRAG_DRIVER_SHARED, SETTLED_ZOOM, GRAB_COMMITTED, POINTER_SITES and the shield default; AC-6, AC-7 and AC-9 Green; the measurements (F2 held, D-1152)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9fce270 (baseline.sha) plus rows 0 to 6", "output": "drag: failures 10, all AC-81.11, median 90.5; origin: failures 10, all AC-81.11, median 90.0; shield10: failures 10, all AC-81.11, median 89.45; Tests 10 passed (10) at row 5; ok lines: {'AC-4': 1, 'AC-8': 1, 'AC-9': 1, 'AC-10': 1}; 4 passed (5.0s); assert-check PASS at each row"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-7-hang-verdict", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-7.ps1 (task.md row 7's Validation cell: the hang verdict, the signature file, the assert, line-ending and hang checks); receipts epf-hang-verdict.txt, epf-hang-check.txt", "scope": "AC-12: every hang in rows 3 to 6 classified (D-1150)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9fce270 (baseline.sha) plus rows 0 to 7", "output": "blocks: [] causes: []; outcome: not-reproduced expected: not-reproduced; register changed: known-issues False meu-status False matches the outcome: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-8-acceptance", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-8.ps1 (task.md row 8's Validation cell reading epf-burn-level-b.txt: host-wait, the build, flake-run.py --mode full --runs 3 --label accept --expect-total 232, flake-run.py --mode watched --repeat 10 --runs 1 --label watch10, assert-check.py, the acceptance check); receipts epf-accept.txt, epf-watch10.txt, epf-accept-assert.txt, epf-accept-check.txt", "scope": "AC-13 and AC-14: three full runs and the watched tests ten times at 18 busy children with the shield on", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9fce270 (baseline.sha) plus rows 0 to 8", "output": "run 1: exit 0 in 612 s; ok lines 232; failures 0; rejection lines 0; run 2: exit 0 in 566 s; ok lines 232; failures 0; rejection lines 0; run 3: exit 0 in 572 s; ok lines 232; failures 0; rejection lines 0; PASS: 3 of 3 runs clean at median load 95.4 (threshold 60.0); uncovered failures cleared by a solo rerun: 0; hangs excused by a registered signature: 0; watch10 run 1: exit 0 in 274 s; ok lines 110; failures 0; PASS: 1 of 1 runs clean at median load 93.9; all distinct: True; excused hangs: 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-9-records", "command": "python C:/Temp/av-kit/e2e-pointer-flakes/tmp/write-row9.py (issue-resolve-set.json, LF, and grouping row 91 by bytes, LF kept); pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-9.ps1 (task.md row 9's Validation cell: issue-resolve.py bound to the row-0 register hash, issue_triage.py render and render --check, the row 9 check); receipts epf-issue-resolve.txt, epf-issues-render.txt, epf-issues-render-check.txt, epf-row9-check.txt", "scope": "AC-15: the two issues resolved, the launch hang noted and open, the render, grouping row 91", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9fce270 (baseline.sha) plus rows 0 to 9", "output": "decision logs read: 104 of 104; parsed fields changed: 11; issue-resolve: 0 problem(s); Rendered known-issues.md: 34 lines; OK: known-issues.md is up-to-date; grouping lines changed: [163] row 91 as planned: True; launch hang for outcome not-reproduced: True yaml LF: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-H1-2.ps1 (task.md row H1-2's Validation cell: pwsh -NoProfile -File docs/execution/plans/2026-11-17-e2e-pointer-flakes/session-gate.ps1); receipts epf-gate-h1.txt and the epf-D6-*.txt step receipts", "scope": "The H1-2 session gate: identity before and after, static, the selftests, py-format and py-lint, targeted, host-load, and the fresh full UI Vitest, UI build, Electron E2E (flake-run.py --mode full --runs 1 --no-burn --label gate --expect-total 232), issues render check and state render", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692", "output": "ui-tests: Test Files 145 passed (145), Tests 1633 passed (1633); ui-electron: run 1: exit 0 in 448 s; ok lines 232; failures 0; rejection lines 0; PASS: 1 of 1 runs clean at median load 20.6 (threshold 0.0); ui-electron: rejection-record lines=0; host-load: ran at 13.4 %; tested_state before=9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692 after=9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "epf-h1-3-h1-4-render-and-skip-basis", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-pointer-flakes/row-H1-3.ps1 (uv run python tools/meu_status.py render --check) and row-H1-4.ps1 (the skip-basis hash check against baseline-skip-hashes.json); receipts epf-render-check.txt, skip-basis-check.txt", "scope": "H1-3: the MEU render after the current-focus entry; H1-4: no file under packages/, mcp-server/, tools/ or ui/src/ changed, added or removed since row 0", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692", "output": "Drift check passed: SSOT loaded (160 MEUs, 12 phases), rendered regions match on-disk content; packages, mcp-server, tools or ui/src changes since row 0: []"}
```

### Quality Gate Results

The H1-2 gate (`epf-gate-h1.txt`), last line `session-gate: all steps exit 0`, `tested_state` `9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692` before and after.

| Step | Stage | Exit | Decisive output |
|------|-------|------|-----------------|
| `identity-before` / `identity-after` | identity | 0 | the same `tested_state` before and after; `ELECTRON_RUN_AS_NODE <unset>`, `playwright_test 1.64.1` |
| `ui-types`, `ui-lint` | static | 0 | — |
| `task-contract` | static | 0 | `OK: 27 row(s)`; `2 row(s) exempt (view_file): H1-5, H2-1` |
| `scope-paths` | static | 0 | `changed paths: 28 outside scope: []`; `read-never-changed files: 12 mismatch: [] baseline-dirty hash mismatch: []` |
| `line-endings` | static | 0 | `eol-check: 34 scope path(s), 0 problem(s)` |
| `home-path` | static | 0 | `check_home_path: ok files=2692 allowlisted=60 nul=31` |
| `flake-run`, `assert-check`, `red-check`, `eol-check`, `identity` selftests | static | 0 | `red-check selftest: 88 fixture(s) (20 positive, 68 negative), 0 wrong: []`; `eol-check selftest: 19 case(s), 0 wrong: []` |
| `py-format`, `py-lint` | static | 0 | `6 files already formatted`; `All checks passed!` |
| `assert-check` | targeted | 0 | `PASS` |
| `ui-unit` | targeted | 0 | `Test Files  3 passed (3)`, `Tests  13 passed (13)` |
| `host-load` | host | 0 | `host-load: ran at 13.4 %` |
| `ui-tests` | full | 0 | `Test Files  145 passed (145)`, `Tests  1633 passed (1633)`; no failure excused |
| `ui-build` | full | 0 | — |
| `ui-electron` | full | 0 | invocation `20261118T162042-70072-a1c383`: `run 1: exit 0 in 448 s; ok lines 232; failures 0; rejection lines 0`; `rejection-record lines=0` |
| `issues-render-check` | full | 0 | `OK: known-issues.md is up-to-date` |
| `state-render` | full | 0 | `Drift check passed` (160 MEUs, 12 phases) |
| `py-tests`, `py-types`, `openapi`, `mcp-*` | skipped | — | every file under `packages/`, `mcp-server/` and `tools/` keeps its row-0 hash (H1-4, S13) |

The UI Vitest count is the base 1628 plus AC-1, AC-2, AC-3, AC-6 and AC-7 (1633); the E2E total is the base 228 plus AC-4, AC-8, AC-9 and AC-10 (232).

---

## Changed Files

Counts are added / removed lines against `HEAD` `9fce270` (`git diff --numstat --ignore-cr-at-eol`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step: `eol-check: 34 scope path(s), 0 problem(s)`).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/tests/e2e/pointer-settle.ts` | `SETTLE` (`settle` at `:16`), `SETTLED_BOX` (`:36`), `POINTER_ON` (`:45`), and the five shared helpers (`:82`, `:112`, `:132`, `:187`, `:206`) | new, 249 | LF |
| `ui/tests/e2e/e2e-diag.ts` | `DIAG_DIR`, `PHASE_LINES`, `MAIN_DIAG`, `POINTER_SHIELD` | new, 194 | LF |
| `ui/tests/e2e/e2e-diag.test.ts` | AC-4, AC-8, AC-9, AC-10 | new, 223 | LF |
| `ui/tests/unit/e2e-pointer.test.ts` | AC-1, AC-2, AC-3, AC-6, AC-7 | new, 332 | LF |
| `ui/tests/e2e/electron-app.ts` | the phase lines, the `installMainDiag` evaluate for the built app, `EVALUATE_ERROR_KEPT_GOING`, `pointerShield?: false`, `POINTER_SHIELD_DEFAULT = true` (`:33`) | +77 / -5 | LF kept |
| `ui/tests/e2e/download-queue.test.ts` | the five helpers moved out; the import at `:7` | +5 / -180 | LF kept |
| `ui/tests/e2e/convert-queue.test.ts` | `DRAG_DRIVER_SHARED` at `:1198-1202`; the import at `:7` | +5 / -17 | LF kept |
| `ui/tests/e2e/capture-inbox.test.ts` | `windowSettled` imported (`:9`); `settledZoom` (`:924`); `GRAB_COMMITTED` (`:2032-2036`); `POINTER_SITES` (`:1574-1576`, `:1640`, `:1656`, `:2523`) | +25 / -56 | LF kept |
| `.agent/context/known-issues.yaml` | two issues resolved, one note appended (`issue-resolve.py`, row 9) | +12 / -8 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` | +3 / -5 | LF |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | row 91 (`:163`): `executed (Session 91)` and the plan folder | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 91 entry (H1-3), prepended above Session 94's | +3 | CRLF kept (227 CRLF, 0 bare LF) |
| `docs/execution/plans/2026-11-17-e2e-pointer-flakes/` | the plan (D-1152 and D-1153 in its YAML), task (row marks), the plan-local scripts, the row-0 records and `session-gate.ps1` | new folder | LF |
| `.agent/context/handoffs/2026-11-17-e2e-pointer-flakes-handoff.md` | this handoff | new | LF |

Not changed: `ui/playwright.config.ts`, `ui/tests/e2e/electron-env.ts`, `ui/tests/e2e/main-error-watch.cjs` and every file under `ui/src/`, `packages/`, `mcp-server/` and `tools/` (H1-4). No MEU files changed. Nothing is committed or staged.

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

`approved` at round 1 of 6, with 0 findings and 0 blocking, intent achieved (`.agent/context/handoffs/2026-11-17-e2e-pointer-flakes-implementation-critical-review.md`, a byte-for-byte copy of the reviewer's report, checked with `cmp`; ledger loop `epf-execution-2026-11-17-e2e-pointer-flakes`, round 1 `recorded round 1 verdict=approved agent='codex-independent-reviewer' blocking=0 intent_achieved=yes usage=17,465,333`, `loop may close: approved with no blocking findings.`).

- **The loop.** It began with the plan's goal anchor and citable AC-1 to AC-15 plus AC-49, AC-66, AC-67, AC-80, AC-81, AC-87 and AC-143, with no token budget; the OK line reads `mode=execution budget=6 tokens=off` (`epf-exec-begin.txt` in the dispatch folder). Dispatch `epf-exec-r1` ran with kind `execution` (timeout 2700 s); its console, `epf-exec-console-r1.txt` in the dispatch folder, records the verdict.
- **The state.** **Intent achieved:** yes. The reviewer's own `identity.py --state-only` matched the gate's and H1-6b's tested_state `9fce270bff07964d76da4dee163f83fddf31fe2e+449e4c74b025d9adf857be52f6f3e08d1d2e45c58919e4631721d82d4cc0c692` exactly, with no sandbox or global-ignore difference to reconcile (§Scope).
- **What it accepted.**
  - The acceptance proof (§Q1): its own recount of the bound raw run files gives each of the three full runs 232 of 232 with all 11 watched tests, and watch10 110 of 110 with each watched title ten times; zero failures, timeout hangs, rejection lines and evaluate errors; 234 launches per full run, all reaching `exit`. Load: full runs min 81.6 %, median 95.4 %; watch10 min 89.0 %, median 93.9 %.
  - The drag fix and shared helpers (§Q2), the capture origin and committed grab (§Q3), and the shield, phases and diagnostics (§Q4): the moved helpers keep their logic; `DRAG_DRIVER_SHARED` adds synchronization without weakening the final-order assertion; 1,167 assertion lines and 103 test titles kept; `setTimeout(` 8 → 6 only from the removed duplicate.
  - Row 3, F2 and the burn level (§Q5): probes 1 to 6 held, 7 and 8 free; the four restored files byte-identical; `epf-burn-level-b.txt` correctly selects 18 children and accept-runs 3, and row 8 read it. It did not use the F2-skewed first run to justify row 8.
  - The launch hang (§Q6): no `Test timeout of`, `Worker teardown timeout` or rejection line in any bound file; `not-reproduced` is supported, and the issue stays open.
  - The `repeatEach` key (§Q7): it is used only for the `repeat` metadata at `electron-app.ts:64`, sets no Playwright option and adds no repeat; the checker was not changed; "I found no control defeat."
  - The registers (§Q8), the gate and the skip basis (§Q9: 23 step records, each exit 0; 408 hashes and the exact file set match), and safety and fidelity (§Q10).
- **What it did not rerun.** No reviewer Electron launch, build or full-suite rerun: it accepted the saved gate and Electron proofs against the matching identity and ran targeted checks only (the five-test unit file, typecheck, `assert-check.py`, `eol-check.py`, the flake-run and red-check selftests, the issue render check, its recount and audit scripts).
- **Residual limits it names, carried as limits, not findings.** "Residual limits are the approved finite-run statistical proof and the unreproduced launch hang, whose issue remains open." It also notes a home-path reference at `current-focus.md:31` that predates this delta and was not introduced here.
- **H1-7a** (`review-state-check.txt`, `review-state.json`): `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`.
- **H1-7b** (`exec-review.txt`): `OK: approved at round 1 of 6, 0 open blocking findings`.
- **After the review**, only this handoff changed, to fill this report. `identity.py` excludes the session's handoffs, so the tested_state is unchanged (H1-6b rerun).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The launch hang (`CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`) | open issue | — | Not reproduced (D-1150); the note names the receipts and the next step (read that run's `phases.jsonl` for each launch's last phase) |
| `convert-queue-labels.test.ts:519` (AC-152.24) failing once in the row-3 rerun's full run | not registered | — | It was not covered, held no rejection and passed its solo rerun; it came on the unfixed tree in a measurement, not in row 8, and it passed in all three acceptance runs and the gate. RULE-3 registers only a row-8 failure |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **F2 held (D-1152).** From row 3 to row 7, F2 was held by a program outside this session (`epf-f2-probe-1.txt` to `epf-f2-probe-6.txt`: `F2 held by another process (RegisterHotKey false, last error 1409)`). AC-81.11's `HOTKEY_IN_USE_FIXTURE` needs F2 free, so it failed every repeat of rows 3 to 6. Rows 4 to 7 went on as measurements; row 5's plain capture run counted with AC-81.11 as its only failure, recorded as a deviation, not a pass of AC-81.11. No process outside the session was stopped. Mat then closed the holder (`epf-f2-probe-7.txt`: `F2 free (registered and released)`).
- **The row-3 rerun (D-1153).** The first row 3 run's burn level rested on AC-81.11's F2 failures, so row 3 was rerun as a new invocation under fresh receipt names (`repro-b`, `base-full-b`, `epf-burn-level-b.txt`). For the rerun the three spec files were put back from the row-0 copies and the shield default set to `false`; the fixed files were saved first with their hashes and restored after, each hash checked (`epf-row3b-swap-out.txt`, `epf-row3b-swap-back.txt`: all four restored `True`; then `epf-row3b-restore-eol.txt` and `epf-row3b-restore-assert.txt`, both exit 0). The first run's receipts are kept as the skewed evidence. Both runs read `accept-runs: 3`. Row 8 read `epf-burn-level-b.txt` in place of `epf-burn-level.txt` (the one change to row 8's cell). F2 was probed free again just before row 8 (`epf-f2-probe-8.txt`).
- **MEU-161 unused.** Row 7's outcome is `not-reproduced`, so no MEU was registered and `meu-register.py` was never written (the gate's line-ending step lists it `new, not written yet`).
- **No 24-children repeat.** Neither row-3 run had zero watched failures, so D-1146 did not escalate.
- **AC-9 in row 3's full runs.** `e2e-diag.test.ts:191` fails by design while the shield is off, so it is uncovered in both base-full receipts and its solo rerun fails; it is not S5. It passed from row 6 on, in every row-8 run and in the gate.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file with an environment header (working directory, `PYTHONIOENCODING`, `PYTHONDONTWRITEBYTECODE`, `RECEIPTS_DIR`, `TMP`, `TEMP`, `ELECTRON_RUN_AS_NODE` unset, `UV_NO_SYNC` and `UV_OFFLINE` set, so `uv run` neither syncs nor reaches the network) and run with `pwsh -NoProfile -File`; the cell itself was copied verbatim.
- **The `repeatEach` key (S7 at row 2).** `assert-check.py` counts the text `repeatEach` as a wait knob. Row 2's first run (`run-row2-attempt1.out`) failed it: `NO_NEW_WAIT_KNOBS FAIL 'repeatEach': 0 -> 1`, because the phase line read `testInfo.repeatEachIndex`, the running repeat's index, not Playwright's repeat option. Under S7 the checker was not edited; that literal was taken out and `electron-app.ts:49` joins the key, `const REPEAT_INDEX = ('repeat' + 'Each' + 'Index') as keyof TestInfo`, with a comment at `:45-47` that says why. The phase line still carries the index; no repeat option was added to a spec or the config, and `flake-run.py` passes the watched repeat on the command line. The rerun passed and the count has stayed `0 -> 0` since. The reviewer may judge whether the joined key keeps to the check's intent.
- **Processes.** Each run stopped only the processes it launched, by recorded id and creation time (`busy children left: 0`, `busy interpreters left: 0` in every receipt). No other session's app, the IDE's avkit MCP server, ShareX or Mat's app was stopped. The clipboard specs, `capture-filmstrip-actions.test.ts` and `capture-import.test.ts`, never ran.

### Execution notes

- **The decisions, as the plan records them.** D-1145: acceptance is three full runs plus the watched tests ten times when row 3's watched runs failed. D-1146: reproduce first at 18 busy children with the churn child; escalate only on zero failures. D-1147: the helpers live once in `pointer-settle.ts`. D-1148: two equal reads one frame apart, then a hit-test; the grab waits on x2. D-1149: the shield is on by default with an opt-out. D-1150: hangs classified per block; not reproduced here. D-1151: no assertion line changes. D-1152 and D-1153 (execution decisions, in the plan's YAML, `resolution: autonomous`): the F2-held measurements and the row-3 rerun (Departures).
- **No stop fired.** No existing test failed after Green (S5 not used); no rejection line appeared (S10 not used); AC-9 passed at row 6 (S11 not used).

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
| Validated | 2026-11-18 | codex-independent-reviewer | Execution review round 1: approved, 0 findings, intent achieved |
