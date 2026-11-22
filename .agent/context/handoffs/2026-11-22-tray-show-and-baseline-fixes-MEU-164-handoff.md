---
date: "2026-11-22"
project: "2026-11-22-tray-show-and-baseline-fixes"
meu: "MEU-164"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/implementation-plan.md"
build_plan_section: "docs/build-plan/09-screenshot-capture.md §Tray double-click (MEU-164, matrix 9.47)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-21-transcript-job-resume-MEU-163-handoff.md"
---

# Handoff: 2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-164 Tray double-click (phase 9, matrix 9.47), registered at triage from `TRAY-DOUBLE-CLICK-NO-SHOW` (D-1363) and grouped as Session 102 with the two TECH-DEBT rows `TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE` (D-1361) and `TOOLING-PLAN-SLUG-ANCESTOR-MATCH` (D-1362) (D-1364).
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Tray double-click (`:1360`); parent canon 09 §Electron OS surface (main process), tray row (`:167`). The two debt rows have no build-plan home, as for other register debt.
**Predecessor**: [2026-11-21-transcript-job-resume-MEU-163-handoff.md](2026-11-21-transcript-job-resume-MEU-163-handoff.md), Session 101, committed as `7f34348`. Session 102 ran from `7f34348` (`baseline.sha`), and `HEAD` did not move.

- **One show function (`TRAY_SHOW_SHARED`, D-1365).** `startCaptureTray` defines `showWindow` (`ui/src/main/capture-tray.ts:16`): when the window is minimized it calls `restore()`, then `show()` and `focus()`. The Show window item's `click` (`:24`) and the new `tray.on('double-click', showWindow)` listener (`:48`) are that same function, so neither restates its steps (09 §Tray double-click, One function row, `:1367`). The tray menu keeps its four items in order, and a single click and a right-click do not change (`:1368`).
- **The E2E hook (`TRAY_E2E_HOOK`, D-1366).** Only a launch with `AVKIT_E2E=1` sets `globalThis.__AVKIT_E2E_TRAY__` to `{ tray, menu }` (`capture-tray.ts:49-52`), so Playwright can emit the real tray's `double-click` and call the Show window item from the main process. It is a main-process global, not an IPC channel (D-1369).
- **The ICC comparison (`ICC_HEADER_MASK`, D-1367).** `_same_icc_ignoring_creation` (`tests/unit/test_capture_adapter.py:1655`) compares two ICC profiles with header bytes 24 to 35, the creation date and time, masked; it needs equal lengths, a full 128-byte header and every other byte equal. AC-130.10's comparison goes through it (`:1694`), the one changed line of an existing test (M-7). Before, a profile built across a second boundary failed AC-130.10.
- **The plan slug (`PLAN_SLUG_PARENT_ONLY`, D-1368).** `plan_slug` (`tools/validate_closeout_artifacts.py:290`) reads only the plan's own folder: the parent of a `.md` plan file, else the path's last part (`:298-299`). A dated ancestor, such as a dated TEMP folder, no longer names a loose plan, so `--selftest`'s `unslugged-plan-path-is-usage` case passes under a dated TEMP.
- **Records.** MEU-164 is `ready_for_review`. `TRAY-DOUBLE-CLICK-NO-SHOW`, `TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE` and `TOOLING-PLAN-SLUG-ANCESTOR-MATCH` are resolved in the register. 09's tray row names the double-click, and §Tray double-click carries the `Delivered (Session 102)` note (`:1370`). Grouping row 102 reads `executed (Session 102)`.

**What Mat sees.** A double-click on the av-kit tray icon now brings the window back, as the tray menu's Show window item does: from hidden, it is shown and focused; from minimized, it is restored and shown. The Show window item now also restores a minimized window, as a second launch of av-kit already did. The menu, a single click and a right-click are unchanged. The session gate now runs the full pytest with nothing deselected: the two failures that Session 101's gate had to excuse are fixed.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-22 ("add an issue where if icon in system tray is double clicked the "Show window" action needs to be executed. Than proceed with you recommendations"), read with Mat's 2026-11-18 hand-over and D-1364; `plan_to_exec_gate: human`. The plan review approved at round 2 of loop `tsb-plan-2026-11-22-tray-show-and-baseline-fixes` with no findings open; F1 to F3 were fixed (`.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `2026-11-22-tray-show-and-baseline-fixes` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-164.1 | unit | After `startCaptureTray`: one tray; the template's labels are `['Show window', 'Capture region', 'Open inbox folder', 'Quit']`; the built menu is the context menu; exactly one `double-click` listener and no other event; that listener is the Show window item's `click` (`toBe`) | Human-approved (Mat 2026-11-22, D-1363); `TRAY_SHOW_SHARED` | `ui/tests/unit/capture-tray.test.ts:106` | ✅ |
| AC-164.2 | unit | The shared function on a minimized window records `['restore', 'show', 'focus']`; on one that is not minimized, `['show', 'focus']`; neither reaches `onRegion` or `shell.showItemInFolder` | D-1365 | `ui/tests/unit/capture-tray.test.ts:116`, `:131` | ✅ |
| AC-164.3 | unit | With `AVKIT_E2E` unset, `globalThis.__AVKIT_E2E_TRAY__` stays undefined; with `'1'`, it holds the created tray and the built menu | `TRAY_E2E_HOOK`; D-1366 | `ui/tests/unit/capture-tray.test.ts:141`, `:146` | ✅ |
| AC-164.4 | integration | Electron, scratch `AVKIT_APP_DATA`: the hidden window is visible and focused after a `double-click` on the hooked tray, and visible again after the Show window item's `click()` | Human-approved (D-1363); D-1366 | `ui/tests/e2e/tray-double-click.test.ts:92` | ✅ |
| AC-164.5 | integration | Electron: a minimized window is not minimized and is visible after a `double-click` | D-1365; D-1366 | `ui/tests/e2e/tray-double-click.test.ts:103` | ✅ |
| AC-164.6 | check | The §Test pins pass with their row-0 hashes and node sources | Local Canon | rows 2 and 5 `pins-unchanged`, row 5 `tsb-row5-pins.txt`, row 6 `tsb-row6-reveal.txt`; gate `pins-unchanged`, `named-edits`, `slug-edit`, `ui-tray`, `ui-tests`, `py-tests`, `e2e-startup-reveal` | ✅ |
| AC-164.7 | check | 09's tray row holds the plan's text, §Tray double-click holds the Delivered note, no other line of 09 changed, and 09 stays CRLF | Local Canon (09 §Electron OS surface) | row 7 `tsb-row7-canon-check.txt`; gate `canon`, `line-endings` | ✅ |
| AC-164.8 | unit (pytest) | `_same_icc_ignoring_creation` is True for equal profiles and for any change inside bytes 24 to 35; the guard: False for a change at byte 23, 36 or 100, a shorter copy, `None` on either side and two equal 100-byte strings; AC-130.10 passes through it | TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE (D-1361); D-1367 | `tests/unit/test_capture_adapter.py:1699`; guard `:1716` | ✅ (`icc_compare_sees_other_bytes` passed at Red, guard) |
| AC-164.9 | unit (pytest) | `plan_slug` of a loose plan under a dated ancestor raises `Usage`; the guard: the plan file and its folder give the slug, and a bare `loose-plan.md` raises `Usage`; `--selftest` under a dated TEMP exits 0 | TOOLING-PLAN-SLUG-ANCESTOR-MATCH (D-1362); D-1368 | `tests/tooling/test_closeout_plan_slug.py:27`, `:44`; guard `:34` | ✅ (`plan_path_gives_its_slug` passed at Red, guard) |
| AC-130.10 (cross-ref) | guard | The one changed line of an existing test (M-7, D-1367): the profile comparison uses `_same_icc_ignoring_creation`. Not a criterion of this plan | Human-approved hand-over (D-1367, M-7) | `tests/unit/test_capture_adapter.py:1694`; row 1 and 2 `named-edits`; gate `named-edits`, `py-debt`, `py-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-164.8 `test_ac_164_8_icc_compare_ignores_creation_time` | `AssertionError: 24`, `assert False` on the first changed-time copy (`tsb-row1-red.txt`, `3 failed, 2 passed, 49 deselected in 0.48s`) | Row 2: `11 passed, 139 deselected in 31.04s` (`tsb-row2-green.txt`) | `tests/unit/test_capture_adapter.py:1699` |
| AC-164.9 `test_ac_164_9_loose_plan_under_dated_ancestor_is_usage` | `Failed: DID NOT RAISE Usage` (`tsb-row1-red.txt`) | Row 2 (`tsb-row2-green.txt`) | `tests/tooling/test_closeout_plan_slug.py:27` |
| AC-164.9 `test_ac_164_9_selftest_under_dated_temp` | `assert 1 == 0` on the selftest's return code (`tsb-row1-red.txt`) | Row 2 (`tsb-row2-green.txt`) | `tests/tooling/test_closeout_plan_slug.py:44` |
| AC-164.1 | `AssertionError: expected [] to deeply equal [ 'double-click' ]` (`tsb-row3-red.txt`, `Tests  4 failed \| 1 passed (5)`) | Row 5: `Tests  5 passed (5)` (`tsb-row5-green.txt`) | `ui/tests/unit/capture-tray.test.ts:106` |
| AC-164.2 (both tests) | `AssertionError: expected 'undefined' to be 'function'`, twice (`tsb-row3-red.txt`) | Row 5 (`tsb-row5-green.txt`) | `ui/tests/unit/capture-tray.test.ts:116`, `:131` |
| AC-164.3 with `AVKIT_E2E=1` | `AssertionError: expected undefined to be FakeTray{ image: {}, …(3) }` (`tsb-row3-red.txt`) | Row 5 (`tsb-row5-green.txt`) | `ui/tests/unit/capture-tray.test.ts:146` |
| AC-164.4 | `Error: expect(tray hook)` (`tsb-row4-red.txt`, `2 failed`; `tsb-row4-reason.txt`) | Row 6: `6 passed (4.4s)` over 3 runs (`tsb-row6-tray.txt`) | `ui/tests/e2e/tray-double-click.test.ts:92` |
| AC-164.5 | `Error: expect(tray hook)` (`tsb-row4-red.txt`, `tsb-row4-reason.txt`) | Row 6 (`tsb-row6-tray.txt`) | `ui/tests/e2e/tray-double-click.test.ts:103` |

`test_ac_164_8_icc_compare_sees_other_bytes` and `test_ac_164_9_plan_path_gives_its_slug` passed at Red and are guards (`tsb-row1-red.txt` `PASSED` on both). AC-164.3's unset case (`:141`) passed at Red, as the unchanged tray sets no hook; it is the negative of the `'1'` case. AC-164.6 and AC-164.7 are checks. Every Red failed by assertion, never by a missing module or a TypeError: the Vitest file asserts `typeof listener === 'function'` before it calls the listener, and the E2E spec asserts the hook with the message `expect(tray hook)`. `red-check` passed each Red: `tsb-row1-red-check.txt` (3 required, 2 allowed passes, 0 problems), `tsb-row3-red-check.txt` (3 required, 0 problems) and `tsb-row4-red-check.txt` (2 required, 0 problems).

- **Row 0 baseline** (`tsb-baseline.txt`): `baseline: all steps exit 0`; `eol-check: 20 scope path(s), 0 problem(s)`. Base suites: pytest `3343 passed, 37 warnings in 521.05s (0:08:41)` (`tsb-base-py.txt`); UI Vitest `Test Files  150 passed (150)`, `Tests  1669 passed (1669)` (`tsb-base-ui.txt`). The two Session 101 failures did not occur in this base run; both are timing- or path-dependent (D-1361, D-1362), which is why each fix carries a test that forces the failing case.
- **Row 1 Red** (`tsb-row1-red.txt`): `3 failed, 2 passed, 49 deselected in 0.48s`; `named-edits red: tests/unit/test_capture_adapter.py: added ['_same_icc_ignoring_creation', 'test_ac_164_8_icc_compare_ignores_creation_time', 'test_ac_164_8_icc_compare_sees_other_bytes'], removed [], changed ['test_ac_130_10_cmyk_icc_to_srgb']`; `row-check named-edits: 0 problem(s)` (`tsb-row1-named.txt`).
- **Row 2 Green** (`tsb-row2-green.txt`): `11 passed, 139 deselected in 31.04s`; `row-check named-edits: 0 problem(s)`; `slug-edit: tools/validate_closeout_artifacts.py: added [], removed [], changed ['plan_slug']`, `row-check slug-edit: 0 problem(s)`; `row-check pins-unchanged: 0 problem(s)`; `row-check red-unchanged: 0 problem(s)`; `eol-check: 20 scope path(s), 0 problem(s)`.
- **Row 3 Red** (`tsb-row3-red.txt`): `Tests  4 failed | 1 passed (5)`.
- **Row 4 Red** (`tsb-row4-red.txt`, host load `host-load: ran at 18.0 %` in `tsb-row4-load.txt`): `2 failed`; `red-reason AC-164.4 hidden: first assertion 'Error: expect(tray hook)'; needle True`, the same for `AC-164.5 minimized`, `row-check red-reason: 0 problem(s)` (`tsb-row4-reason.txt`).
- **Row 5 Green** (`tsb-row5-green.txt`): `Test Files  1 passed (1)`, `Tests  5 passed (5)`; the unit pins `Test Files  4 passed (4)`, `Tests  63 passed (63)` (`tsb-row5-pins.txt`); `row-check pins-unchanged: 0 problem(s)`, `row-check red-unchanged: 0 problem(s)`; types and lint exit 0; `eol-check: 20 scope path(s), 0 problem(s)`.
- **Row 6 Electron** (`tsb-row6-runs.txt`, host load `host-load: ran at 16.0 %` before the tray runs and `17.0 %` before startup-reveal): `e2e-count tsb-row6-tray.txt: 6 AC-164 ok lines, passed [6], want 6`; `e2e-count tsb-row6-reveal.txt: passed [2]`; `row-check e2e-count: 0 problem(s)`; `row-check red-unchanged: 0 problem(s)` (`tsb-row6-redhash.txt`).
- **Row 7 canon and status** (`tsb-row7-*.txt`): `row-check canon: 0 problem(s)`; the three issues `changed fields ['resolution_path', 'status', 'verification']; status resolved`, `row-check register: 0 problem(s)`; `issue-resolve: 0 problem(s)` with `parsed fields changed: 12`; `Updated MEU-164 → ready_for_review (updated: 2026-11-22)`; `Drift check passed — SSOT loaded (164 MEUs, 12 phases)`.
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-0-baseline", "command": "pwsh -NoProfile -File docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/baseline.ps1 (task.md row 0's Validation cell: baseline.sha, the dirty list and hashes, the scope, line-ending and pin records, the cited anchors, the free-id check, the plan-local selftests and the base pytest and UI suites); receipts C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-baseline.txt, tsb-base-py.txt, tsb-base-ui.txt", "scope": "Row 0: the baseline at 7f34348 and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7f34348 (baseline.sha) plus row 0", "output": "tsb-baseline.txt: eol-check: 20 scope path(s), 0 problem(s); baseline: all steps exit 0. tsb-base-py.txt: 3343 passed, 37 warnings in 521.05s (0:08:41). tsb-base-ui.txt: Test Files  150 passed (150); Tests  1669 passed (1669)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-1-2-debt", "command": "pwsh -NoProfile -File of task.md rows 1 and 2's Validation cells (debt-edit.py; pytest on test_capture_adapter.py, test_closeout_plan_slug.py and test_framework_adoption.py; red-check.py; row-check named-edits, slug-edit, pins-unchanged, red-unchanged; eol-check); receipts C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-row1-*.txt, tsb-row2-*.txt", "scope": "AC-164.8 and AC-164.9 Red with their guards passing, then Green; AC-130.10 through the helper", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7f34348 (baseline.sha) plus rows 0 to 2", "output": "tsb-row1-red.txt: 3 failed, 2 passed, 49 deselected in 0.48s. tsb-row1-red-check.txt: red-check: 1 receipt(s), runner pytest, 3 required test(s), 2 allowed pass(es), 0 step target(s), 0 problem(s). tsb-row2-green.txt: 11 passed, 139 deselected in 31.04s. tsb-row2-named-edits.txt, tsb-row2-slug-edit.txt, tsb-row2-pins-unchanged.txt, tsb-row2-red-unchanged.txt: 0 problem(s). tsb-row2-eol.txt: eol-check: 20 scope path(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-3-4-red-tray", "command": "pwsh -NoProfile -File of task.md rows 3 and 4's Validation cells (Vitest on capture-tray.test.ts; host-wait, the UI build, Playwright on tray-double-click.test.ts; red-check.py; row-check red-reason; red-record); receipts C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-row3-red.txt, tsb-row3-red-check.txt, tsb-row4-red.txt, tsb-row4-reason.txt, tsb-row4-red-check.txt, tsb-row4-load.txt", "scope": "AC-164.1 to AC-164.3 Red on the unchanged tray; AC-164.4 and AC-164.5 Red in real Electron", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7f34348 (baseline.sha) plus rows 0 to 4", "output": "tsb-row3-red.txt: Tests  4 failed | 1 passed (5). tsb-row3-red-check.txt: red-check: 1 receipt(s), runner any, 3 required test(s), 0 allowed pass(es), 0 step target(s), 0 problem(s). tsb-row4-red.txt: 2 failed. tsb-row4-reason.txt: red-reason AC-164.4 hidden ... needle True; red-reason AC-164.5 minimized ... needle True; row-check red-reason: 0 problem(s). tsb-row4-red-check.txt: red-check: 1 receipt(s), runner playwright, 2 required test(s), 0 allowed pass(es), 0 step target(s), 0 problem(s). tsb-row4-load.txt: host-load: ran at 18.0 %."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-5-green-tray", "command": "pwsh -NoProfile -File of task.md row 5's Validation cell (tray-green.py on capture-tray.ts; Vitest on capture-tray.test.ts and the four unit pins, typecheck, lint, row-check pins-unchanged and red-unchanged, eol-check); receipts C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-row5-*.txt", "scope": "AC-164.1 to AC-164.3 Green; the unit pins of AC-164.6", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7f34348 (baseline.sha) plus rows 0 to 5", "output": "tsb-row5-green.txt: Test Files  1 passed (1); Tests  5 passed (5). tsb-row5-pins.txt: Test Files  4 passed (4); Tests  63 passed (63). tsb-row5-pins-unchanged.txt: row-check pins-unchanged: 0 problem(s). tsb-row5-red-unchanged.txt: row-check red-unchanged: 0 problem(s). tsb-row5-eol.txt: eol-check: 20 scope path(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-6-electron", "command": "pwsh -NoProfile -File of task.md row 6's Validation cell (the UI build, host-wait before each run, Playwright --repeat-each 3 on tray-double-click.test.ts and startup-reveal.test.ts once, row-check e2e-count and red-unchanged); receipts C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-row6-*.txt", "scope": "AC-164.4 and AC-164.5 Green, 3 runs of 3; the startup-reveal pin of AC-164.6", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7f34348 (baseline.sha) plus rows 0 to 6", "output": "tsb-row6-tray.txt: 6 passed (4.4s). tsb-row6-reveal.txt: 2 passed (2.0s). tsb-row6-runs.txt: e2e-count tsb-row6-tray.txt: 6 AC-164 ok lines, passed [6], want 6; e2e-count tsb-row6-reveal.txt: passed [2]; row-check e2e-count: 0 problem(s). tsb-row6-load-tray.txt: host-load: ran at 16.0 %. tsb-row6-load-reveal.txt: host-load: ran at 17.0 %."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-7-canon", "command": "pwsh -NoProfile -File of task.md row 7's Validation cell (canon-edit.py, issue-resolve.py, crlf.py, issue_triage.py render, meu_status.py set and render, row-check canon and register); receipts C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-row7-*.txt", "scope": "AC-164.7; the three issues resolved; MEU-164 ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7f34348 (baseline.sha) plus rows 0 to 7", "output": "tsb-row7-canon-check.txt: row-check canon: 0 problem(s). tsb-row7-issue.txt: parsed fields changed: 12; issue-resolve: 0 problem(s). tsb-row7-register.txt: row-check register: 0 problem(s). tsb-row7-status.txt: Updated MEU-164 → ready_for_review (updated: 2026-11-22). tsb-row7-render-check.txt: Drift check passed — SSOT loaded (164 MEUs, 12 phases)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-h1-2-gate", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/session-gate.ps1 *> C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-gate-h1.txt (task.md row H1-2's Validation cell); step receipts C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-D6-*.txt", "scope": "H1-2: the registered verification plan, identity before and after, static, targeted, host-load, fresh full with nothing deselected and the two Electron suites, with the named skips", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c", "fresh": true, "snapshot": false, "output": "tsb-gate-h1.txt: tested_state before=7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c after=7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c; session-gate: all steps exit 0. tsb-D6-ui-tests.txt: Test Files  151 passed (151); Tests  1674 passed (1674). tsb-D6-py-tests.txt: 3348 passed, 37 warnings in 302.45s (0:05:02). tsb-D6-e2e-tray-double-click.txt: 2 passed (2.2s). tsb-D6-e2e-startup-reveal.txt: 2 passed (2.0s). tsb-D6-host-load.txt: host-load: ran at 19.1 %."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-h1-2-recheck", "command": "uv run --no-sync python docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/identity.py --state-only with ELECTRON_RUN_AS_NODE unset, compared with the gate's tested_state line; receipt C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-identity-recheck-h1-2.txt", "scope": "H1-2: the gate's tested_state re-derived after the gate process exited, before the row was marked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c", "output": "tsb-identity-recheck-h1-2.txt: 7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c, equal to the gate's tested_state; HEAD 7f34348d77be9c126e804aaf10344a921f127869"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-h1-3-focus", "command": "uv run --no-sync python of the H1-3 focus script (a byte write that asserts the top entry and CRLF) and a read-back into C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-focus-write-h1-3.txt, then pwsh -NoProfile -File of task.md row H1-3's Validation cell; receipts tsb-render-check.txt, tsb-h13-status.txt, tsb-h13-check.txt in the same folder", "scope": "H1-3: the Session 102 entry on top of current-focus.md; MEU-164 ready_for_review from row 7, with no new status write", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c", "output": "tsb-focus-write-h1-3.txt: current-focus.md: 263 lines; CRLF only: True; starts with the Session 102 paragraph: True. tsb-render-check.txt: Drift check passed — SSOT loaded (164 MEUs, 12 phases), rendered regions match on-disk content. tsb-h13-check.txt: MEU-164 ready_for_review: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-h1-4-no-deselect", "command": "pwsh -NoProfile -File of task.md row H1-4's Validation cell (as corrected, Departures); receipt C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-no-deselect.txt; probe C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-h1-4-probe.txt", "scope": "H1-4: no executable line of session-gate.ps1 holds --deselect, it has one py-tests step, and tsb-D6-py-tests.txt ends with a passed summary that names no failed and no error", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c", "output": "tsb-no-deselect.txt: deselect in gate code: [] py-tests steps: 1 summary: 3348 passed, 37 warnings in 302.45s (0:05:02). tsb-h1-4-probe.txt: real gate: pass; py-tests argv with --deselect: refused; $pytest base with --deselect: refused; py-tests step removed: refused"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsb164-h1-5-sources", "command": "view_file of .agent/context/handoffs/TEMPLATE.md and 2026-11-21-transcript-job-resume-MEU-163-handoff.md (also the newest handoff by mtime), with sha256 into C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-source-read-h1-5.txt", "scope": "H1-5: the template and the precedent read before this handoff", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c", "output": "tsb-source-read-h1-5.txt: 1e013a15c3cecfc3c290b051a6e1e6c0ed07ad661f14a936fe786a92d06702be TEMPLATE.md; e2e142d50aa4c4b5d513b81c9531d9c00fee8018ae5baf9bccb909642625942a 2026-11-21-transcript-job-resume-MEU-163-handoff.md; newest *-handoff.md by mtime: 2026-11-21-transcript-job-resume-MEU-163-handoff.md (the named peer itself)"}
```

### Quality Gate Results

On the final tree, from `identity-before` to `identity-after`, at `HEAD` `7f34348`; the last line of `tsb-gate-h1.txt` is `session-gate: all steps exit 0`, and the gate's `tested_state` equals the identity re-derived after it (`tsb-identity-recheck-h1-2.txt`). The host load before the fresh full stage read `host-load: ran at 19.1 %` (`tsb-D6-host-load.txt`). The gate ran once.

| Step | Stage | Result | Decisive line | Receipt |
|------|-------|--------|---------------|---------|
| `identity-before` | identity | exit 0 | `tested_state 7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c` | `tsb-D6-identity-before.txt` |
| `ui-types` | static | exit 0 | `tsc --noEmit`, exit 0 | `tsb-D6-ui-types.txt` |
| `ui-lint` | static | exit 0 | `eslint src/ tests/ --max-warnings 0`, exit 0 | `tsb-D6-ui-lint.txt` |
| `py-types` | static | exit 0 | `0 errors, 0 warnings, 0 informations` | `tsb-D6-py-types.txt` |
| `py-lint` | static | exit 0 | `All checks passed!` | `tsb-D6-py-lint.txt` |
| `py-format` | static | exit 0 | `16 files already formatted` | `tsb-D6-py-format.txt` |
| `task-contract` | static | exit 0 | `OK: 25 row(s); 10-column table (with builder_model); 23 row(s) fully checked`; `2 row(s) exempt (view_file): H1-5, H2-1` | `tsb-D6-task-contract.txt` |
| `scope-paths` | static | exit 0 | `changed paths: 43 outside scope: [] other sessions plan files skipped: 0`; `read-never-changed files: 17 mismatch: [] baseline-dirty hash mismatch: []`; `head moved (S4): False` | `tsb-D6-scope-paths.txt` |
| `line-endings` | static | exit 0 | `eol-check: 20 scope path(s), 0 problem(s)` | `tsb-D6-line-endings.txt` |
| `home-path` | static | exit 0 | `check_home_path: ok files=2980 allowlisted=60 nul=45` | `tsb-D6-home-path.txt` |
| `pins-unchanged` | static | exit 0 | `110 node(s) besides test_ac_130_10_cmyk_icc_to_srgb`; `138 node(s) besides plan_slug`; `row-check pins-unchanged: 0 problem(s)` | `tsb-D6-pins-unchanged.txt` |
| `named-edits` | static | exit 0 | `added ['_same_icc_ignoring_creation', 'test_ac_164_8_icc_compare_ignores_creation_time', 'test_ac_164_8_icc_compare_sees_other_bytes'], removed [], changed ['test_ac_130_10_cmyk_icc_to_srgb']`; `row-check named-edits: 0 problem(s)` | `tsb-D6-named-edits.txt` |
| `slug-edit` | static | exit 0 | `added [], removed [], changed ['plan_slug']`; `row-check slug-edit: 0 problem(s)` | `tsb-D6-slug-edit.txt` |
| `canon` | static | exit 0 | `canon: tray row at 167; Delivered note after line 1368: 6 line(s)`; `row-check canon: 0 problem(s)` | `tsb-D6-canon.txt` |
| `red-unchanged` | static | exit 0 | `row-check red-unchanged: 0 problem(s)` | `tsb-D6-red-unchanged.txt` |
| `red-check-selftest` | static | exit 0 | `red-check selftest: 122 fixture(s) (35 positive, 87 negative), 0 wrong: []` | `tsb-D6-red-check-selftest.txt` |
| `eol-check-selftest` | static | exit 0 | `eol-check selftest: 24 case(s), 0 wrong: []` | `tsb-D6-eol-check-selftest.txt` |
| `row-check-selftest` | static | exit 0 | `row-check selftest: 0 wrong: []` | `tsb-D6-row-check-selftest.txt` |
| `py-debt` | targeted | exit 0 | `9 passed, 45 deselected in 22.78s` | `tsb-D6-py-debt.txt` |
| `closeout-selftest` | targeted | exit 0 | `RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms, so the tool is not refusing everything]`, under the dated `tmp-dated` TEMP | `tsb-D6-closeout-selftest.txt` |
| `ui-tray` | targeted | exit 0 | `Test Files  5 passed (5)`; `Tests  68 passed (68)` | `tsb-D6-ui-tray.txt` |
| `host-load` | host | exit 0 | `host-wait: ok (19.1 %, limit 50 %)` | `tsb-D6-host-load.txt` |
| `ui-tests` | full | exit 0 | `Test Files  151 passed (151)`; `Tests  1674 passed (1674)`; `baseline ui failures excused: []` | `tsb-D6-ui-tests.txt` |
| `py-tests` | full | exit 0 | `3348 passed, 37 warnings in 302.45s (0:05:02)`; `baseline py failures excused: []`, nothing deselected | `tsb-D6-py-tests.txt` |
| `ui-build` | full | exit 0 | `built in 4.19s` | `tsb-D6-ui-build.txt` |
| `e2e-tray-double-click` | runtime | exit 0 | `host-wait: ok (9.5 %, limit 50 %)`; `2 passed (2.2s)`; `other outcomes=False`; `rejection-record lines=0` | `tsb-D6-e2e-tray-double-click.txt` |
| `e2e-startup-reveal` | runtime | exit 0 | `host-wait: ok (8.7 %, limit 50 %)`; `2 passed (2.0s)`; `other outcomes=False`; `rejection-record lines=0` | `tsb-D6-e2e-startup-reveal.txt` |
| `state-render` | full | exit 0 | `Drift check passed — SSOT loaded (164 MEUs, 12 phases)` | `tsb-D6-state-render.txt` |
| `issues-render` | full | exit 0 | `OK: known-issues.md is up-to-date` | `tsb-D6-issues-render.txt` |
| `identity-after` | identity | exit 0 | the same `tested_state` as `identity-before` | `tsb-D6-identity-after.txt` |
| `e2e-other` | runtime | skipped | only the tray module changed in the app; tray-double-click runs the tray, and startup-reveal covers the launch and reveal | `tsb-gate-h1.txt` |
| `mcp-tests` | full | skipped | no mcp-server file changed | `tsb-gate-h1.txt` |
| `openapi` | full | skipped | no API file changed | `tsb-gate-h1.txt` |
| the gate | all | pass | `session-gate: all steps exit 0` | `tsb-gate-h1.txt` |

`ui-tests` is the row-0 base (`Test Files  150 passed (150)`, `Tests  1669 passed (1669)`, `tsb-base-ui.txt`) plus the new file `ui/tests/unit/capture-tray.test.ts` with its 5 tests. `py-tests` is the row-0 base (`3343 passed, 37 warnings in 521.05s (0:08:41)`, `tsb-base-py.txt`) plus the 5 new pytest tests (the two AC-164.8 tests and the three in `tests/tooling/test_closeout_plan_slug.py`), with nothing deselected: 3348 passed. H1-4 (`tsb-no-deselect.txt`): `deselect in gate code: [] py-tests steps: 1 summary: 3348 passed, 37 warnings in 302.45s (0:05:02)`.

---

## Changed Files

Counts are added / removed lines against `HEAD` `7f34348` (`git diff --numstat --ignore-cr-at-eol HEAD`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/src/main/capture-tray.ts` | `TRAY_SHOW_SHARED`: `showWindow` (`:16`), the menu item (`:24`), the listener (`:48`); `TRAY_E2E_HOOK` (`:49-52`) | +16 / -7 | LF kept |
| `tests/unit/test_capture_adapter.py` | `ICC_HEADER_MASK`: `_same_icc_ignoring_creation` (`:1655`), AC-130.10's one line (`:1694`), AC-164.8 (`:1699`, `:1716`) | +45 / -1 | CRLF kept |
| `tools/validate_closeout_artifacts.py` | `PLAN_SLUG_PARENT_ONLY`: `plan_slug` (`:290`, the folder lines `:298-299`) | +5 / -4 | CRLF kept |
| `tests/tooling/test_closeout_plan_slug.py` | AC-164.9 | new, 59 | LF |
| `ui/tests/unit/capture-tray.test.ts` | AC-164.1 to AC-164.3 | new, 153 | LF |
| `ui/tests/e2e/tray-double-click.test.ts` | AC-164.4 and AC-164.5 | new, 109 | LF |
| `docs/build-plan/09-screenshot-capture.md` | §Tray double-click and the MEU row at triage; the tray row (`:167`) and the `Delivered (Session 102)` note (`:1370`) in row 7 | +24 / -1 | CRLF kept |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, `docs/build-plan/build-priority-matrix.md` | MEU-164 registered at triage and `ready_for_review` (row 7); `meu_status.py render` | +26/-2, +1/-0, +3/-3, +1/-0 | kept |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` | the three issues registered at triage and resolved (row 7) | +124/-0, +3/-3 | CRLF kept (restored, Departures) |
| `.agent/context/triage-output.yaml` | the Session 102 triage | +106 / -16 | CRLF kept |
| `.agent/context/grouping/2026-11-22-tray-show-and-baseline-fixes-session-grouping.md` | the grouping (D-1364); row 102 `executed (Session 102)` | new, 129 | LF |
| `.agent/context/current-focus.md` | the Session 102 entry (H1-3) | +3 / -0 | CRLF kept |
| `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/` | the plan (D-1369 and D-1370 in its YAML), task (row marks and the corrected H1-4 check, Departures), the row-0 records, the plan-local scripts and `session-gate.ps1` | new folder | LF |
| `.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-plan-critical-review.md` | the plan review | new | LF |
| `.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff.md` | this handoff | new | LF |

**The shared function.** `capture-tray.ts` (LF):

```diff
+  const showWindow = (): void => {
+    if (opts.window.isMinimized()) {
+      opts.window.restore()
+    }
+    opts.window.show()
+    opts.window.focus()
+  }
   const menu = Menu.buildFromTemplate([
-    {
-      label: 'Show window',
-      click: () => {
-        opts.window.show()
-        opts.window.focus()
-      },
-    },
+    { label: 'Show window', click: showWindow },
 ...
   tray.setContextMenu(menu)
+  tray.on('double-click', showWindow)
```

**The mask.** `test_capture_adapter.py` (CRLF), `:1655`: `return a[:24] + a[36:] == b[:24] + b[36:]`, after `None`, length and header-size checks. **The slug.** `validate_closeout_artifacts.py` (CRLF), `:298`: `folder = parts[-2] if parts[-1].endswith(".md") and len(parts) > 1 else parts[-1]`, in place of the loop over every ancestor.

Nothing is committed or staged. `ui/out/` was rebuilt and is gitignored.

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

No findings. Codex's execution review (`.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-implementation-critical-review.md`, loop `tsb-execution-2026-11-22-tray-show-and-baseline-fixes`, round 1 of 6) answered Q1 to Q7 with no finding of any severity. It derived the same `tested_state` as the gate (`7f34348d77be9c126e804aaf10344a921f127869+e1a863c71f3d51c29aadd0c810aac7dc7e21df4f91c14e17aef0f7bbd182e70c`), re-ran the targeted pytest (`6 passed, 45 deselected in 0.26s`; `3 passed in 0.35s`), the plan's check modes and selftests (0 problems each), and an audit of the git state and scope (outside allowed scope `[]`). It accepted the corrected H1-4 check: the `$pytest` base and the `py-tests` step hold no `--deselect`, which agrees with its own argv inspection.

### Verdict

`approved` at round 1, `intent_achieved=yes`, 0 blocking findings (ledger `usage` 10,729,222). H1-7a: `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0` (`review-state-check.txt`). H1-7b: `OK: approved at round 1 of 6, 0 open blocking findings` (`exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A single click on the tray icon showing the window | out-of-scope | — | 09 §Tray double-click, Menu row: a single click and a right-click keep today's behavior |
| A double-click that hides a visible window (toggle) | out-of-scope | — | Mat asked for the Show window action only (D-1363) |
| An E2E-only build or IPC channel for the tray | out-of-scope | — | D-1366, D-1369: the hook is a main-process global set only by an `AVKIT_E2E=1` launch |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **D-1369 and D-1370 (execution, autonomous, `mandatory: none`; in the plan's YAML).** D-1369 applies the plan review's round 2 wording note: the M-4 note and the tray-start fact say the hook exists only in a launch with `AVKIT_E2E=1`, with no separate E2E build. D-1370: row 0's free-id check reads a `D-1365..D-1399` match preceded by `to ` or `..` as the upper end of another session's claimed range, not a use (`tsb-baseline.txt`: `D-1365..D-1399 range ends outside this session's files (not a use): 11`); every other match outside this session's files stays S2.
- **Row 7 register line endings.** `issue-resolve.py` and `tools/issue_triage.py render` wrote `known-issues.yaml` and `known-issues.md` with LF over their CRLF working copies (`core.autocrlf=true`). `crlf.py` converted both back to CRLF by bytes with no content change and found `triage-output.yaml` already CRLF (`tsb-row7-crlf.txt`: `now CRLF only=True` for each of the three), and `issue_triage.py render --check` and `row-check.py register` passed after it.
- **The gate's TEMP.** The gate runs under an undated TEMP (`s102-tmp`), so no dated ancestor reaches any test by accident; only the `closeout-selftest` step sets TEMP and TMP to the dated `tmp-dated` folder, to prove D-1368 in the real CLI, and restores them after.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file and run with `pwsh -NoProfile -File`, with `PYTHONIOENCODING=utf-8`, `RECEIPTS_DIR=C:/Temp/av-kit` and `ELECTRON_RUN_AS_NODE` cleared. Edits to CRLF files were made by bytes and checked by `eol-check.py`. Every Electron run used a scratch `AVKIT_APP_DATA` and waited for the host load at or below 50 %.
- **The H1-4 check.** The row's first check read `session-gate.ps1` as one string and failed because the gate's comment (`:18`) and its `Write-Output` line (`:132`) both say "holds no --deselect"; the py-tests argv (`:180`) and the `$pytest` base (`:149`) hold none (receipt moved to `superseded/h1-4/`). The row's text names the py-tests step, so the cell was corrected by a byte edit of `task.md` (outside `tested_state`): no executable line of the gate may hold `--deselect` (comments and `Write-Output` lines are skipped), the gate must have exactly one py-tests step, and the receipt-summary check is unchanged. A probe on edited copies (`tsb-h1-4-probe.txt`) shows the corrected check refuses a `--deselect` in the py-tests argv or in `$pytest`, and a missing py-tests step. The gate was not re-run, because no gated input changed.
- **Processes.** Each Electron run stopped only the app it launched. No other session's app, the IDE's avkit MCP server or Mat's app was stopped.

### Execution notes

- **The plan decisions.** D-1365: the shared function restores a minimized window, so the Show window item restores too. D-1366: Vitest with a mocked `electron` proves the listener, the function and the hook; an Electron spec reaches the real tray through the E2E-only hook. D-1367 (M-7): AC-130.10 compares the profiles with the creation time masked. D-1368: `plan_slug` reads only the plan's own folder, and the debt rows' ACs are AC-164.8 and AC-164.9 in the MEU's family.
- **The §Test pins.** `ui/tests/unit/app-icon.test.ts`, `ui/tests/unit/capture-main.behavior.test.ts`, `ui/tests/unit/capture-page.test.ts`, `ui/tests/unit/login-item-ipc.test.ts`, `ui/tests/e2e/startup-reveal.test.ts` and `tests/tooling/test_framework_adoption.py` keep their row-0 hashes (gate `pins-unchanged`). In `tests/unit/test_capture_adapter.py` every top-level node keeps its row-0 source except AC-130.10 (`:1667`), whose one line `:1694` changed (D-1367); `pins-unchanged: tests/unit/test_capture_adapter.py: 110 node(s) besides test_ac_130_10_cmyk_icc_to_srgb`. In `tools/validate_closeout_artifacts.py` every top-level node except `plan_slug` keeps its source (`138 node(s) besides plan_slug`). `ui/src/main/index.ts` is not edited.
- **Stops.** No stop condition was met. No expectation was edited at Green (S3), and no other existing test failed after a Green (S5).

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-22 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
