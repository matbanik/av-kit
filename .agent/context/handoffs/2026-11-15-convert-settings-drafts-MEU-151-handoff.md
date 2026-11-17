---
date: "2026-11-16"
project: "2026-11-15-convert-settings-drafts"
meu: "MEU-151"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md"
build_plan_section: "bp06"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none (first MEU of Session 81)"
---

# Handoff: 2026-11-15-convert-settings-drafts-MEU-151-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-151 `gui-settings-draft-baseline` (issues `SETTINGS-DRAFT-STALE-BASELINE` and `CONVERT-ADVANCED-EDIT-REPLACED`, triage D-808). An open capture settings edit keeps only what the user changed, follows every other saved value and saves only the changed fields; a Convert Advanced edit (CQ, scale, audio) or preset pick survives settings arriving or changing.
**Build Plan Section**: [06 §Settings drafts keep edits (residual)](../../../docs/build-plan/06-gui.md#settings-draft-baseline-residual) (matrix 6.19), with the Delivered (Session 81) note at the end of that section.
**Successor**: MEU-152 (same session; `2026-11-15-convert-settings-drafts-MEU-152-handoff.md`).

- **CAPTURE_DRAFT_CHANGED_ONLY and CAPTURE_SAVE_CHANGED_ONLY (D-966).** `useCaptureSettings.ts` keeps a `Partial` draft of only the edited leaves over the latest saved values, the shape `useConverterSettings.ts` already had (AC-112.9, RC1 D-212). A refetch reaches every leaf the user did not edit; an edit set back to the saved value leaves the draft; `save()` sends only the changed leaves, or no PUT when none is left, and a merged form that `parseSettingsPut('capture', …)` refuses rejects with `SettingsValidationError` before any PUT.
- **Per-field Convert choices (D-967).** On the Convert page the preset, CQ, scale and audio are each the user's choice once set, and each untouched field follows the current preset. Neither late settings nor a change of the saved default preset replaces an edit; a preset pick resets the three fields. The settings effect and `presetTouched` are gone from `ConvertPage.tsx`.
- **Moved pins.** AC-151.9 moves two existing pins in `capture-page.behavior.test.ts` (named in the plan) and, by Mat's ruling D-1066 after the first gate, three more: AC-107.27 (`capture-shapes.behavior.test.ts`), AC-105.23 (`capture-style-flow.behavior.test.ts`) and AC-143.30 (`capture-tool-flow.behavior.test.ts`). Each pinned the old seven-key Save after an inbox edit; each now expects only `inbox_dir`, and every other check stays, AC-143.30's `tool_lock` GET check included.
- **The real-app check (A2, D-975).** Round 1 of row 5 was Mat's look in the real app; HC-4, the capture Save, was `pass`. Round 2 became Electron tests by Mat's ruling; HC-4 is AC-151.14, which passed in all three row-5 runs and again in the gate.
- **Spec text and records (rows 6 to 8).** The 06 Delivered (Session 81) note (`cs81-notes-check.txt`: `06 CRLF: True 08 LF: True notes: 1 1`); `SETTINGS-DRAFT-STALE-BASELINE` and `CONVERT-ADVANCED-EDIT-REPLACED` resolved through the plan's `issue-resolve.py` (`cs81-issue-resolve.txt`: `issue-resolve: 0 problem(s)`); MEU-151 `ready_for_review` (`cs81-status-151.txt`).

**Residual risk for triage.** The converter Save body (`useConverterSettings`) still sends the full form (plan §Out of Scope, D-971). `CONVERT-ADVANCED-EDIT-REPLACED` has unit coverage only (AC-151.10 to AC-151.12); row 5's Electron tests do not touch the Advanced fields, and its register entry says so.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md) §MEU-151. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." The plan review approved at round 2 ([plan-critical-review.md](2026-11-15-convert-settings-drafts-plan-critical-review.md)); `plan_to_exec_gate: human`. The coordinator wrote these words into the plan's Status line (line 15) after the plan review approved it, so the reviewed plan hash no longer holds; that is disclosed here and in Departures. Amendments A1 (D-1060), A2 (D-975) and D-1066 changed the plan in place after that, each on Mat's own words.

**Receipts.** A receipt named by its file name alone is in the session's receipts folder (`RECEIPTS_DIR`, the plan's `convert-settings-drafts` folder under it). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-151.1 | unit | After an inbox edit, a refetch that changes the hotkey to `F3` reaches the form; the other five leaves follow the new answer | Local Canon (06 Draft; AC-112.9, D-212; D-966) | `ui/tests/unit/capture-settings-draft.behavior.test.ts:175` | ✅ |
| AC-151.2 | unit | Continuing AC-151.1, `save()` sends one PUT whose body equals `{ inbox_dir: 'X' }` | Local Canon (06 Draft; D-966) | `capture-settings-draft.behavior.test.ts:185` | ✅ |
| AC-151.3 | unit | An edit set back to the saved value leaves the draft; a lone such edit sends no PUT; an edit a refetch makes equal sends no PUT; by D-1067 (CS81-R1-F1) such an edit leaves the draft for good, so after refetches to `F9` and then `F3` the form shows `F3` and Save sends only `inbox_dir` | Local Canon (06 Draft; D-966; D-1067) | `capture-settings-draft.behavior.test.ts:196`, `:214`, `:231`, `:243` | ✅ |
| AC-151.4 | unit | An edit made before the first GET resolves is kept; the other six leaves come from the loaded answer | Local Canon (06 Draft; D-966) | `capture-settings-draft.behavior.test.ts:261` | ✅ |
| AC-151.5 | unit | A merged form the capture schema refuses rejects with `SettingsValidationError` and sends no PUT (guard) | Local Canon (`settings-schemas.ts:151-164`; D-966) | `capture-settings-draft.behavior.test.ts:281` | ✅ |
| AC-151.6 | unit | After a successful Save the draft is empty and a later GET change shows for every leaf (guard) | Local Canon (06 Draft; D-966) | `capture-settings-draft.behavior.test.ts:298` | ✅ |
| AC-151.7 | unit | Capture page: a refetch reaches the hotkey under an inbox edit, and Save sends only `inbox_dir` | Local Canon (06 Tests) | `ui/tests/unit/capture-page.behavior.test.ts:1236` | ✅ |
| AC-151.8 | unit | Settings page Capture card: the same sequence; the hotkey input shows the new hotkey and the PUT body is only `inbox_dir` | Local Canon (06 Tests; D-966) | `capture-settings-draft.behavior.test.ts:314` | ✅ |
| AC-151.9 | unit | The moved pins assert the partial body: `capture-page.behavior.test.ts` AC-39.4 AC-39.15 and AC-57.1 with `toEqual`; by D-1066, AC-107.27, AC-105.23 and AC-143.30 expect only `inbox_dir` | Local Canon (06 Draft; named rows, HDP §4a M-7; D-1066) | `capture-page.behavior.test.ts:377`, `:1203`; `capture-shapes.behavior.test.ts:1039`; `capture-style-flow.behavior.test.ts:886`; `capture-tool-flow.behavior.test.ts:1302` | ✅ |
| AC-151.10 | unit | With settings answered late, a CQ of 31, a scale of 720 and an audio mode set before the answer survive it, in the Add body and the command snapshot | Local Canon (06 Edit kept; RC1 D-208, AC-112.8) | `ui/tests/unit/convert-page.behavior.test.ts:571` | ✅ |
| AC-151.11 | unit | With settings loaded, each of the three edits survives a change of the saved default preset; the untouched preset follows it | Local Canon (06 Edit kept) | `convert-page.behavior.test.ts:591` | ✅ |
| AC-151.12 | unit | Untouched fields follow a default-preset change; a preset pick resets all three; a picked preset is not replaced (guard) | Local Canon (06 Edit kept; D-967) | `convert-page.behavior.test.ts:608` | ✅ |
| AC-151.13 | unit, e2e | Existing tests pass unchanged: `capture-page.test.ts`, `settings-page.test.ts`, `convert-page.test.ts`, the AC-112.8 and AC-112.9 tests, and the Electron tests `W9-3`, `AC-57.10 header` and `AC-67.24` of `capture-inbox.test.ts` | Local Canon (AC-39.x, AC-57.x, AC-67.24, AC-112.8, AC-112.9) | gate steps `meu-151-ui`, `ui-tests`, `ui-electron-capture` | ✅ |
| AC-151.14 | e2e | A2, was HC-4. In the real app with a scratch profile, saving only a new capture inbox folder sends one PUT with only `inbox_dir`; the hotkey is unchanged in the backend and the field; the Capture page's Options show the new folder and the same hotkey | Local Canon (06 Draft; D-966; D-975) | `ui/tests/e2e/capture-settings-draft.test.ts:151` | ✅ |
| AC-39.4 AC-39.15 (cross-ref) | changed test | `AC-39.4 AC-39.15 Capture page Save PUTs capture settings only when dirty`: its PUT body pin moved from `toMatchObject` to `toEqual({ inbox_dir: … })` (AC-151.9); the rest stays | MEU-39 | `capture-page.behavior.test.ts:377` | ✅ |
| AC-57.1 (cross-ref) | changed test | `AC-57.1 header row`: its PUT body pin moved the same way (AC-151.9); the rest stays | MEU-57 | `capture-page.behavior.test.ts:1203` | ✅ |
| AC-107.27 (cross-ref) | changed test (D-1066) | `AC-107.27 after a step style commit the Capture card's unsaved edit stays and its Save sends only inbox_dir`: the file's `CARD_KEYS` is `['inbox_dir']`; the unsaved-edit and value checks stay | MEU-107 | `capture-shapes.behavior.test.ts:1039` | ✅ |
| AC-105.23 (cross-ref) | changed test (D-1066) | `AC-105.23 a style PUT keeps the Capture card's unsaved edit, whose Save sends only inbox_dir`: `CARD_KEYS` the same; the style PUT, refetch and colour checks stay | MEU-105 | `capture-style-flow.behavior.test.ts:886` | ✅ |
| AC-143.30 (cross-ref) | changed test (D-1066) | `AC-143.30 after a Lock click the Capture card's unsaved edit stays, its Save sends only inbox_dir, and the GET keeps tool_lock`: `CARD_KEYS` the same; the `tool_lock` GET check stays | MEU-143 | `capture-tool-flow.behavior.test.ts:1302` | ✅ |
| AC-67.24, AC-112.8, AC-112.9 (cross-ref) | guard | Pass unchanged (AC-151.13) | MEU-67, MEU-112 | `capture-inbox.test.ts` (gate `ui-electron-capture`); `convert-page.behavior.test.ts:345-531` | ✅ |
| AC-2 (cross-ref) | guard | `e2e-harness.test.ts` AC-2 (only `electron-app.ts` names the Playwright launcher) passes unchanged; the first gate found the A2 file naming a callback parameter `_electron`, renamed `_app` (D-1066) | Session 78 harness | `ui/tests/unit/e2e-harness.test.ts` (gate `ui-tests`) | ✅ |
| AC-152 (sibling) | sibling MEU | AC-152.1 to AC-152.24, with the AC-30, AC-31, AC-45, AC-112.4 and AC-123 cross-references: the Convert queue labels, the Cut encoder and A1's output names, evidenced in the MEU-152 handoff | MEU-152 | `2026-11-15-convert-settings-drafts-MEU-152-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-151.1 | `expected 'F2' to be 'F3'` (`cs81-151-red.txt`) | Row 2: pass (`cs81-151-green.txt`) | `capture-settings-draft.behavior.test.ts:175` |
| AC-151.2 | the PUT body holds all seven leaves with the stale hotkey | Row 2: pass | `capture-settings-draft.behavior.test.ts:185` |
| AC-151.3 | three cases, each by assertion; D-1067's two-refetch case `expected 'F9' to be 'F3'` against the row-2 hook (`cs81-d1067-red.txt`) | Row 2: pass; the two-refetch case after D-1067 (`cs81-d1067-green.txt`) | `capture-settings-draft.behavior.test.ts:196`, `:214`, `:231`, `:243` |
| AC-151.4 | the six leaves keep the defaults copied into the draft | Row 2: pass | `capture-settings-draft.behavior.test.ts:261` |
| AC-151.7 | the PUT carries `hotkey: 'F2'` | Row 2: pass | `capture-page.behavior.test.ts:1236` |
| AC-151.8 | the hotkey input keeps the old value | Row 2: pass | `capture-settings-draft.behavior.test.ts:314` |
| AC-151.9 (AC-39.4 AC-39.15, AC-57.1) | the body has seven leaves, so `toEqual` fails | Row 2: pass | `capture-page.behavior.test.ts:377`, `:1203` |
| AC-151.10 | `expected [ '18', '0', 'copy' ] to deeply equal [ '31', '720', 'aac_192' ]` | Row 2: pass | `convert-page.behavior.test.ts:571` |
| AC-151.11 | the edit is replaced | Row 2: pass | `convert-page.behavior.test.ts:591` |

- **Row 1 Red** (`cs81-151-red.txt`): `Test Files  3 failed (3)` and `Tests  12 failed | 199 passed (211)`, exit 1 (`cs81-151-red.txt.exit`). `cs81-151-red-check.txt`: `red-check: 1 receipt(s), 10 required test(s), 0 problem(s)`. The 12 failures are the ten required titles (AC-151.3 has three). AC-151.5, AC-151.6 and AC-151.12 pin behaviour that already held and passed in Red, as the plan says.
- **Row 2 Green** (`cs81-151-green.txt`): `Test Files  6 passed (6)` and `Tests  299 passed (299)`; `cs81-151-eol.txt`: `line-ending drift: []`.
- **D-1067 Red and Green** (execution review round 1, CS81-R1-F1). The two-refetch case was added to `capture-settings-draft.behavior.test.ts` and run against the unchanged hook: `Tests  1 failed | 9 passed (10)`, `AssertionError: expected 'F9' to be 'F3'`, exit 1 (`cs81-d1067-red.txt`, `.exit`); `cs81-d1067-red-check.txt`: `red-check: 1 receipt(s), 1 required test(s), 0 problem(s)`. After the fix, the six MEU-151 files: `Test Files  6 passed (6)` and `Tests  301 passed (301)` (`cs81-d1067-green.txt`); the UI typecheck and ESLint on the two files exit 0 (`cs81-d1067-typecheck.txt`, `cs81-d1067-eslint.txt`); `cs81-d1067-eol.txt`: `line-ending drift: []`.
- **D-1066's three pins have no Red of their own.** They are existing tests that pinned the old Save; the first gate's `ui-tests` run shows each failing against the Green code (`cs81-gate-h1-run1.txt`, `cs81-D6-ui-tests-run1.txt`: `Tests  4 failed | 1565 passed (1569)`, the fourth being AC-2 below), and each passes after the change (`cs81-d1066-check.txt`: `Test Files  4 passed (4)`, `Tests  139 passed (139)`).
- **AC-151.14 has no Red** (plan §Execution amendment A2): it was written after the Green it checks. It passed in row 5's three runs (`cs81-row5-e2e-r1.txt` to `-r3.txt`: `5 passed (1.1m)`, `5 passed (1.0m)`, `5 passed (1.9m)`) and in the gate's `ui-electron-a2`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-0-baseline", "command": "pwsh -NoProfile -File (task.md row 0's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-convert-settings-drafts/baseline.ps1 *> C:/Temp/av-kit/convert-settings-drafts/cs81-baseline.txt, with ELECTRON_RUN_AS_NODE unset); receipts cs81-baseline.txt, cs81-base-py.txt, cs81-base-ui.txt", "scope": "Row 0: baseline.sha, baseline-dirty.txt, baseline-dirty-hashes.json, baseline-scope.json, baseline-eol.json, baseline-skip-hashes.json, the row-0 copies; the base Python and UI suites; the red-check and identity selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha), before row 1", "output": "cs81-baseline.txt: baseline: all steps exit 0. cs81-base-py.txt: 3008 passed, 37 warnings in 214.91s (0:03:34). cs81-base-ui.txt: Test Files  133 passed (133); Tests  1547 passed (1547)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-1-red-151", "command": "pwsh -NoProfile -File (task.md row 1's Validation cell: npm --prefix ui run test -- tests/unit/capture-settings-draft.behavior.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/convert-page.behavior.test.ts *> C:/Temp/av-kit/convert-settings-drafts/cs81-151-red.txt, its exit code to cs81-151-red.txt.exit, then red-check.py --require with the ten titles); receipts cs81-151-red.txt, cs81-151-red-check.txt, cs81-s4-row1.txt", "scope": "MEU-151 Red: AC-151.1 to AC-151.4, AC-151.7, AC-151.8, AC-151.10, AC-151.11 and the two AC-151.9 pins against the row-0 product code", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 and 1", "output": "cs81-151-red.txt: Test Files  3 failed (3); Tests  12 failed | 199 passed (211); cs81-151-red.txt.exit 1. cs81-151-red-check.txt: red-check: 1 receipt(s), 10 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-2-green-151", "command": "pwsh -NoProfile -File (task.md row 2's Validation cell: npm --prefix ui run test -- the six MEU-151 files *> C:/Temp/av-kit/convert-settings-drafts/cs81-151-green.txt, then the line-ending check); receipts cs81-151-green.txt, cs81-151-eol.txt, cs81-s4-row2.txt", "scope": "MEU-151 Green: CAPTURE_DRAFT_CHANGED_ONLY and CAPTURE_SAVE_CHANGED_ONLY in useCaptureSettings.ts; the per-field choices in ConvertPage.tsx", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 2", "output": "cs81-151-green.txt: Test Files  6 passed (6); Tests  299 passed (299). cs81-151-eol.txt: line-ending drift: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-5-electron", "command": "pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/a2-e2e-run.ps1 (task.md row 5's Validation cell: the UI build, then npm --prefix ui run test:e2e -- tests/e2e/capture-settings-draft.test.ts tests/e2e/convert-queue-labels.test.ts three times, with ELECTRON_RUN_AS_NODE unset, then the row-5 check); receipts cs81-row5-build.txt, cs81-row5-e2e-r1.txt, cs81-row5-e2e-r2.txt, cs81-row5-e2e-r3.txt, cs81-row5-verify.txt", "scope": "Row 5 (A2, D-975): AC-151.14 and AC-152.21 to AC-152.24 on the built app with scratch profiles and the real backend, three runs; round 1's words kept", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 5", "output": "cs81-row5-e2e-r1.txt: 5 passed (1.1m); cs81-row5-e2e-r2.txt: 5 passed (1.0m); cs81-row5-e2e-r3.txt: 5 passed (1.9m). cs81-row5-verify.txt: runs passing all five: [True, True, True] round 1 kept: True D-975 receipt with no invented pass: True CR in the new Electron files: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-6-8-records", "command": "pwsh -NoProfile -File (task.md rows 6, 7 and 8's Validation cells: the row-6 notes check; issue_triage.py add CONVERT-OUTPUT-NAME-REUSED, issue-resolve.py with the six issues and --expect-sha256, issue_triage.py render and render --check; meu_status.py update MEU-151 and MEU-152 ready_for_review, meu_status.py render, the row-8 check); receipts cs81-notes-check.txt, cs81-issue-add.txt, cs81-issue-resolve.txt, cs81-issues-render.txt, cs81-issues-render-check.txt, cs81-status-151.txt, cs81-status-152.txt, cs81-status-render.txt, cs81-row8-check.txt", "scope": "Rows 6 to 8: the 06 and 08 Delivered notes; the A1 issue added and six issues resolved; both MEUs ready_for_review; grouping row 81 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 8", "output": "cs81-notes-check.txt: 06 CRLF: True 08 LF: True notes: 1 1. cs81-issue-add.txt: OK: Added issue 'CONVERT-OUTPUT-NAME-REUSED' to known-issues.yaml. cs81-issue-resolve.txt: issue-resolve: 0 problem(s). cs81-issues-render.txt: Rendered known-issues.md: 49 lines. cs81-issues-render-check.txt: OK: known-issues.md is up-to-date. cs81-status-151.txt and cs81-status-152.txt: Updated MEU-151 / MEU-152 -> ready_for_review (updated: 2026-11-16). cs81-status-render.txt: Loaded 153 MEUs across 12 phases. cs81-row8-check.txt: row 81 executed (Session 81), grouping LF True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-h1-1-unchecked", "command": "pwsh -NoProfile -File (task.md H1-1's Validation cell) *> C:/Temp/av-kit/convert-settings-drafts/task-unchecked.txt", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 8", "output": "task-unchecked.txt: unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/row-H1-2.ps1 (task.md H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-convert-settings-drafts/session-gate.ps1 *> C:/Temp/av-kit/convert-settings-drafts/cs81-gate-h1.txt, with ELECTRON_RUN_AS_NODE unset); the fifth run, after D-1066, D-1067 and D-1068; receipts cs81-gate-h1.txt and the cs81-D6-*.txt step receipts", "scope": "H1-2 session gate for MEU-151 and MEU-152: identity before and after; pyright, ruff check and format, the UI typecheck and lint, the task contract, scope paths, line endings, the red-check selftest; the MEU-151 UI, MEU-152 UI and MEU-152 Python targeted tests; the full Python suite, the full UI suite and build, the state and issue renders; the Convert, capture and A2 Electron E2E", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "cs81-gate-h1.txt: session-gate: all steps exit 0; tested_state before = after (cs81-D6-identity-before.txt, cs81-D6-identity-after.txt). py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; py-format 3 files already formatted; ui-types tsc --noEmit exit 0; ui-lint eslint src/ tests/ --max-warnings 0 exit 0; task-contract OK: 28 row(s), 26 fully checked, 2 view_file exempt (H1-5, H2-1); scope-paths changed paths: 54 outside scope: [], read-never-changed mismatch: [], baseline-dirty hash mismatch: [], head moved (S4): False; line-endings files: 26 mismatch: []; red-check-selftest 45 fixture(s) (15 positive, 30 negative), 0 wrong: []; meu-151-ui Test Files  6 passed (6), Tests  301 passed (301); meu-152-ui Test Files  3 passed (3), Tests  38 passed (38); meu-152-py 83 passed in 79.28s (0:01:19); py-tests (cs81-D6-py-tests.txt) 3032 passed, 37 warnings in 775.02s (0:12:55); ui-tests Test Files  135 passed (135), Tests  1570 passed (1570); ui-build exit 0 (built in 4.32s); state-render Drift check passed (153 MEUs, 12 phases); issues-render-check OK: known-issues.md is up-to-date; ui-electron-convert (convert-queue.test.ts) 23 passed (22.2s); ui-electron-capture (capture-inbox.test.ts W9-3, AC-57.10 header, AC-67.24) 3 passed (4.6s); ui-electron-a2 (capture-settings-draft.test.ts, convert-queue-labels.test.ts) 5 passed (27.2s). Skipped: openapi and mcp-types/mcp-build/mcp-tests/mcp-audit (every packages/api/ and mcp-server/ file keeps its baseline-skip-hashes.json hash, H1-4), build-record (no build), gui-refs-not-shipped (no GUI reference image is shipped for these surfaces)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-h1-3-ssot", "command": "pwsh -NoProfile -File (task.md H1-3's Validation cell: meu_status.py render --check *> C:/Temp/av-kit/convert-settings-drafts/cs81-render-check.txt; meu_status.py get MEU-151 and MEU-152; the ready_for_review check); receipts cs81-render-check.txt, cs81-h13-status-151.txt, cs81-h13-status-152.txt, cs81-h13-check.txt", "scope": "H1-3: row 8's statuses hold and the render matches; the current-focus paragraph (CRLF, not a gated input) was added first", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "cs81-render-check.txt: Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content. cs81-h13-status-151.txt and cs81-h13-status-152.txt: status ready_for_review. cs81-h13-check.txt: MEU-151 and MEU-152 ready_for_review: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-h1-4-skip-basis", "command": "pwsh -NoProfile -File (task.md H1-4's Validation cell: the baseline-skip-hashes.json comparison of packages/api and mcp-server *> C:/Temp/av-kit/convert-settings-drafts/openapi-check.txt)", "scope": "H1-4: the basis for skipping the OpenAPI and MCP checks", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "openapi-check.txt: packages/api or mcp-server changes since row 0: []"}
```

### Quality Gate Results

- **Last line** (`cs81-gate-h1.txt`): `session-gate: all steps exit 0`.
- **Identity:** tested_state `b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509` before and after the gate (`cs81-D6-identity-before.txt`, `cs81-D6-identity-after.txt`).
- **Static:** pyright `0 errors, 0 warnings, 0 informations`; ruff check `All checks passed!`; ruff format `3 files already formatted`; the UI typecheck and lint exit 0 (`cs81-D6-ui-types.txt`, `cs81-D6-ui-lint.txt`); the task contract `OK: 28 row(s)`, 26 fully checked, 2 view_file exempt (H1-5, H2-1); scope paths `changed paths: 54 outside scope: []`, `read-never-changed mismatch: [] baseline-dirty hash mismatch: []`, `head moved (S4): False`; line endings `line-endings files: 26 mismatch: []`; the red-check selftest `45 fixture(s) (15 positive, 30 negative), 0 wrong: []`.
- **Targeted:** MEU-151 UI `Test Files  6 passed (6)` and `Tests  301 passed (301)` (`cs81-D6-meu-151-ui.txt`); MEU-152 UI `Test Files  3 passed (3)` and `Tests  38 passed (38)` (`cs81-D6-meu-152-ui.txt`); MEU-152 Python `83 passed in 79.28s (0:01:19)` (`cs81-D6-meu-152-py.txt`).
- **Fresh full:** the Python suite `3032 passed, 37 warnings in 775.02s (0:12:55)` (`cs81-D6-py-tests.txt`), which is the row-0 base of 3008 (`cs81-base-py.txt`) plus the 5 cut-encoder and 19 output-reserved cases; the UI suite `Test Files  135 passed (135)` and `Tests  1570 passed (1570)` (`cs81-D6-ui-tests.txt`), which is the row-0 base of 1547 in 133 files (`cs81-base-ui.txt`) plus the 23 new tests and the 2 new files; the UI build exits 0; the state render `Drift check passed` (153 MEUs, 12 phases); the issue render `OK: known-issues.md is up-to-date`.
- **Runtime,** with `ELECTRON_RUN_AS_NODE` unset: `convert-queue.test.ts` unchanged, `23 passed (22.2s)` (`cs81-D6-ui-electron-convert.txt`; `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE`'s AC-97.7 passed); `capture-inbox.test.ts` W9-3, AC-57.10 header and AC-67.24 unchanged, `3 passed (4.6s)` (`cs81-D6-ui-electron-capture.txt`); A2's two files `5 passed (27.2s)` (`cs81-D6-ui-electron-a2.txt`).
- **Skipped, with basis:** `openapi` and `mcp-types`, `mcp-build`, `mcp-tests`, `mcp-audit` (every `packages/api/` and `mcp-server/` file keeps its row-0 hash, H1-4: `packages/api or mcp-server changes since row 0: []`); `build-record` (no build); `gui-refs-not-shipped` (no GUI reference image is shipped for these surfaces).
- **Baseline failures excused:** 0. The first run failed at `ui-tests` (`cs81-gate-h1-run1.txt`, `Tests  4 failed | 1565 passed (1569)`); after D-1066 the gate reran in full and passed (`cs81-gate-h1-run2.txt`, `gate-run2/`). After D-1067 (CS81-R1-F1) the third run failed at `py-tests` on `test_youtube_adapter.py` AC-122.8 (`cs81-gate-h1-run3.txt`, `gate-run3/`: `1 failed, 3031 passed` in 676.19s), and the fourth on `test_tts_assets.py` AC-62.16 (`cs81-gate-h1-run4.txt`, `gate-run4/`: `1 failed, 3031 passed` in 911.43s). Both were 5-second waits under host load, in code this session does not touch; AC-122.8 passed alone three times (`cs81-d1067-py-diag.txt`). Under D-1068 the gate reran in full each time, nothing was registered, and this is the fifth run, made after the host's CPU load was measured at 10%. No step was rerun alone.
- **Processes:** a snapshot before and after the fifth run showed three new processes, all other sessions' (`gate5-procs-compare.txt`); runs 2 to 4 were the same (`gate2-procs-compare.txt`, `gate3-procs-compare.txt`, `gate4-procs-compare.txt`). None was a run's own, and none was touched.
- **After the gate:** H1-3 added the current-focus paragraph (with D-1067 and D-1068 after the fifth run), `task.md` rows were marked and these handoffs were written. `identity.py` excludes all three, so no product, test or tracked record changed after the gate; H1-6b checks that the expected state still equals the gate's.

---

## Changed Files

Counts are added / removed lines against the row-0 copies (`baseline-copies/` in the receipts folder; `git diff --no-index --numstat`), not against `HEAD`, because other sessions' uncommitted work sits in the same tree. D-1066's three files were clean at row 0, so they are counted against `HEAD`. Line endings were measured as bytes (the gate's `line-endings` step).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/src/renderer/src/features/capture/useCaptureSettings.ts` | the partial draft and the changed-only Save; D-1067's prune when the saved answer changes | +51 / -9 | CRLF kept |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | MEU-151: the four per-field choices, the settings effect and `presetTouched` gone; MEU-152: card positions from `convertQueuePositions` | +28 / -30 | CRLF kept |
| `ui/tests/unit/capture-settings-draft.behavior.test.ts` | new: AC-151.1 to AC-151.6, AC-151.8; D-1067's two-refetch case under AC-151.3 | +339 (new) | LF |
| `ui/tests/unit/capture-page.behavior.test.ts` | AC-151.7 appended; the two AC-151.9 pins | +33 / -2 | CRLF kept |
| `ui/tests/unit/convert-page.behavior.test.ts` | AC-151.10 to AC-151.12 and AC-152.9 appended; one helper | +134 / -2 | CRLF kept |
| `ui/tests/unit/capture-shapes.behavior.test.ts` | D-1066: AC-107.27's `CARD_KEYS` and title | +3 / -11 | LF kept |
| `ui/tests/unit/capture-style-flow.behavior.test.ts` | D-1066: AC-105.23's `CARD_KEYS` and title | +3 / -11 | LF kept |
| `ui/tests/unit/capture-tool-flow.behavior.test.ts` | D-1066: AC-143.30's `CARD_KEYS` and title | +3 / -11 | LF kept |
| `ui/tests/e2e/capture-settings-draft.test.ts` | new (A2): AC-151.14 | +236 (new) | LF |
| `docs/build-plan/06-gui.md` | the Delivered (Session 81) note | +7 / -0 | CRLF kept |
| `.agent/context/known-issues.yaml` | `CONVERT-OUTPUT-NAME-REUSED` added; six issues resolved (tools only) | +38 / -11 | LF kept |
| `.agent/context/known-issues.md` | the rendered issue list | +3 / -8 | LF kept |
| `.agent/context/meu-status.yaml` | MEU-151 and MEU-152 `ready_for_review` (`tools/meu_status.py`) | +10 / -10 | LF kept |
| `.agent/context/meu-registry.md` | the rendered registry | +2 / -2 | LF kept |
| `docs/BUILD_PLAN.md` | the rendered MEU status | +1 / -1 | LF kept |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | row 81 `executed (Session 81)` | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 81 paragraph (H1-3) | +3 / -0 (against `HEAD`; clean at row 0) | CRLF kept |

The MEU-152 product and test files (`convert-time.ts`, `convert-controls.ts`, `QueueCard.tsx`, `services/conversion.py`, `convert-controls.test.ts`, `convert-queue-labels.test.ts` unit and e2e, `test_convert_cut_encoder.py`, `test_convert_output_reserved.py`, `08-video-conversion.md`) are listed in the MEU-152 handoff. The plan folder holds the plan, `task.md`, the row-0 records and the plan-local scripts; `session-gate.ps1` gained D-1066's three files in its scope and line-ending lists. These two handoffs are new. Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Finding | Fix | Status |
|---|----------|----------|---------|-----|--------|

### Verdict

Pending: the H1-7 execution review (ledger loop `cs81-execution-2026-11-15-convert-settings-drafts`) has not run.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The converter Save body, which still sends the full form | out-of-scope | none | Plan §Out of Scope; RC1 D-212; D-971 |
| Electron coverage of the Convert Advanced fields | residual for triage | none | Row 5's tests do not touch them; AC-151.10 to AC-151.12 cover them in unit tests |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

### Departures and their basis

- **Status line 15.** The coordinator wrote Mat's execute words into the plan's Status line after the plan review approved it, so the reviewed plan hash no longer holds.
- **D-1066 (Mat's ruling).** The first H1-2 gate failed (`cs81-gate-h1-run1.txt`): `ui-tests` had 4 failures. Three were existing tests outside the plan's named rows that pinned the seven-key Save (AC-107.27, AC-105.23, AC-143.30); S5 stopped the session, and Mat chose "Update the 3 tests (Recommended)". The fourth was `e2e-harness.test.ts` AC-2, tripped by the A2 file's `_electron` parameter name; it was renamed `_app`. The plan, `task.md` and `session-gate.ps1` name the three files; the gate then reran in full from the start. The first run's step receipts were overwritten by the rerun, except `cs81-D6-ui-tests-run1.txt`, kept beside `cs81-gate-h1-run1.txt`.
- **CS81-R1-F1 and D-1067 (execution review round 1, after this handoff was first written).** The review (`C:/Temp/av-kit/cs81-exec-review-round-1.md`, `changes_required`) found that a draft leaf a refetch makes equal to the saved value stayed in the draft, so a second refetch could not reach it. D-1067, autonomous under Mat's hand-over (HDP §6) with `mandatory: none`, prunes the draft during render whenever the saved answer changes: each leaf equal to the new answer leaves the draft, the other changed leaves stay, and an empty draft becomes `null`. The prune runs during render, not in an effect, so no committed render shows the stale leaf. The plan's AC-151.3 text, its Decision Log note and the D-1067 YAML entry, and `task.md`'s H1-2 note, were added after that review. The second gate run's receipts are kept as `cs81-gate-h1-run2.txt` and `gate-run2/`.
- **D-1068 (gate runs 3 and 4).** After D-1067 the gate reran in full. The third run failed at `py-tests` on `tests/integration/test_youtube_adapter.py::test_ac_122_8_surrogate_title_survives_real_storage` (a 5 s thread join got `Processing`), and the fourth on `tests/integration/test_tts_assets.py::test_ac_62_16_model_overshoot_is_clipped_not_failed` (a 5 s `wait_idle` got `Downloading`), with the suite at 676 s and 911 s against the second run's 458 s while other sessions loaded the host. Neither test is in this session's files. Under D-1068, autonomous under the hand-over with `mandatory: none`, the gate reran in full each time and nothing was registered here; the coordinator registers the flakes after Session 81 commits. The fifth run, made after the host's CPU load was measured at 10%, passed and is the gate recorded above. Their receipts are kept as `cs81-gate-h1-run3.txt`, `gate-run3/`, `cs81-gate-h1-run4.txt` and `gate-run4/`.
- **Execution decisions** (in the plan's decision YAML): D-973 (row 5's process handling, by recorded pid and creation time), D-974 (red-check's D-919 pytest header form), D-975 (Mat's A2 ruling, `mandatory: [M-8]`), D-976 (the A2 test seams) D-1066 (Mat's ruling on the three pins, `mandatory: [M-7, M-8]`), D-1067 (the CS81-R1-F1 correction, `mandatory: none`) and D-1068 (the gate reruns after runs 3 and 4, `mandatory: none`). D-1060's precedent and Refs were retargeted to `cs81-human-check-r1.txt`, the round-1 file. Per H1-6 they live in the plan YAML, so the Decision Log below is `None.`.
- **The capture Electron grep.** The gate's `ui-electron-capture` step passes `-g 'W9-3.capture|AC-57.10.header|AC-67.24.Settings'`, each space written as `.`, so the pattern survives the argument passing; it requires exactly 3 passed.
- **Scratch wrappers.** Each row ran through a wrapper in the receipts folder that sets the brief's environment (with `ELECTRON_RUN_AS_NODE` unset) and copies the task cell verbatim (`row-cmd.py`).
- **Processes.** Every launch was recorded by pid and creation time and stopped only that way (D-973). Around the gate, a process snapshot before and after showed only other sessions' processes as new (`gate-procs-compare.txt`); none was touched.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-151 handoff after the H1-2 gate rerun (D-1066), H1-3 and H1-4 |
| Updated | 2026-11-16 | claude-code-local (Claude Opus 5.5) | CS81-R1-F1: D-1067's fix, its Red and Green, the AC-151.3 rows, the line references and counts, and the Departures line |
| Updated | 2026-11-17 | claude-code-local (Claude Opus 5.5) | D-1068: the gate record and results moved to the fifth run; runs 3 and 4 disclosed; H1-3 to H1-6b rerun |
