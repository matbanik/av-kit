---
date: "2026-10-16"
project: "capture-render-fidelity"
meu: "MEU-84"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: ".agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-83-handoff.md"
---

# Handoff: 2026-10-14-capture-render-fidelity-MEU-84-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-84 — `capture-file-variant-sync`. File tracking follows the files on disk, and Open file follows the view.

Two file-tracking fixes:
- **`RECONCILE` (D-15):** `scan_inbox` clears `annotated_path` and `sidecar_path` separately when their file is gone, and saves the row only when one changed. Before, a deleted annotated copy stayed listed, and `image?variant=annotated` pointed at a missing file. A sidecar without its annotated copy keeps its marks, because `load_shot_annotations` reads it by name.
- **`VIEWED_FILE` (D-16):** Open file and Open folder (buttons and the palette) use the file the viewport shows. In the Annotated view that is the annotated copy, falling back to the original when it is missing. Before, they always used the original.

Electron observes the shell target through `E2E_SHELL_LOG` (D-17). That is the existing main-process `AVKIT_E2E` branch, now recording `{op, target}`; it exists only under `AVKIT_E2E=1`. No REST shape changes, and the H1-4 check shows no diff under `packages/api/` or `openapi.committed.json`. `gui-actions-index.md` needs no change, because the action ids and IPC are the same ([walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/walkthrough.md) §Hub).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-84.1 | unit | `RECONCILE` in `scan_inbox`, real files: (a) missing annotated copy cleared, sidecar kept; (b) the reverse; (c) both cleared; (d) a complete row is not re-saved; (e) a row without its original is still deleted | Spec 09:736; D-15 | `tests/unit/test_capture_service.py::test_ac_84_1a_reconcile_clears_a_missing_annotated_copy`, `::test_ac_84_1b_…`, `::test_ac_84_1c_…`, `::test_ac_84_1d_reconcile_leaves_a_complete_row_unsaved`, `::test_ac_84_1e_…` | ✅ |
| AC-84.2 | integration | API: delete the annotated file, then `GET /captures` shows `annotated_path: null` with the sidecar kept; detail still returns the marks; `image?variant=annotated` is 404 | Spec 09:736 | `tests/e2e/test_api_captures.py::test_ac_84_2_list_reconciles_a_deleted_annotated_copy` | ✅ |
| AC-84.3 | unit | `viewedFilePath`: annotated → annotated path; original → original; `null` or `''` annotated → original; no shot → `null` | Spec 09:737-738; D-16 | `ui/tests/unit/capture-viewed-file.test.ts` `AC-84.3 …` (2) | ✅ |
| AC-84.4 | integration | Page Open file / Open folder and the palette `open_folder` follow the viewed variant and fall back to the original after a refetch drops `annotated_path` | Spec 09:737 (amends AC-39.12); triage D-65 | `ui/tests/unit/capture-page.behavior.test.ts` `AC-84.4 …` | ✅ |
| AC-84.5 | integration | Electron: `__AVKIT_E2E_SHELL_LOG__` records `openPath`/`showItemInFolder` of the annotated path in the Annotated view and of the original after switching back | Spec 09:737; E2 | `ui/tests/e2e/capture-inbox.test.ts` `AC-84.5 …` (also in the gate's `e2e-repeat`, 10×) | ✅ |
| AC-84.6 | unit | `recordE2eShell` appends in order; the `index.ts` E2E branches record and never call `shell`; the global exists only under `AVKIT_E2E=1` | D-17 | `ui/tests/unit/capture-main.behavior.test.ts` `AC-84.6 …` (3) | ✅ |
| AC-39 (cross-ref) | regression | AC-39.12 (existing IPC, disabled without a selection) stays green; its target rule is amended by AC-84.4 | Spec 09:737 | `ui/tests/unit/capture-page.test.ts` `AC-39.12 …` | ✅ |
| AC-82 (cross-ref) | — | Owned by MEU-82 (AC-59.19 TA-3/TA-4) | plan MEU-82 | [MEU-82 handoff](2026-10-14-capture-render-fidelity-MEU-82-handoff.md) | see MEU-82 |
| AC-35, AC-59, AC-65, AC-66, AC-67, AC-83 (cross-ref) | — | Owned by MEU-83 (AC-35.13, AC-59.2 TA-1/TA-2, AC-65.3 TA-7, AC-66.11/66.14 TA-5/TA-6, AC-67.1) | plan MEU-83 | [MEU-83 handoff](2026-10-14-capture-render-fidelity-MEU-83-handoff.md) | see MEU-83 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-84.1 (a, b, c), AC-84.2 | `E AssertionError` on the stale `annotated_path` / `sidecar_path` | pass | `tests/unit/test_capture_service.py:1040-1066`; `tests/e2e/test_api_captures.py:1010` |
| AC-84.1 (d, e) | pass on baseline by design: (d) is the negative guard, (e) characterises existing deletion | pass | `test_capture_service.py:1081`, `:1103` |
| AC-84.3 | `Failed to load url ../../src/renderer/src/features/capture/capture-viewed-file` (declared new) | pass | `ui/tests/unit/capture-viewed-file.test.ts:8`, `:13` |
| AC-84.4 | `expected last "spy" call to have been called with [ 'C:/shots/a.annotated.png' ]`, received `C:/shots/a.png` | pass | `ui/tests/unit/capture-page.behavior.test.ts:989` |
| AC-84.5 | `expect(received).toEqual(expected)`: `Expected: []`, `Received: null` | pass | `ui/tests/e2e/capture-inbox.test.ts:1802` |
| AC-84.6 (3) | `Cannot find module '../../src/main/e2e-shell'` (declared new, 2); `openPath: expected '…return…' to contain 'recordE2eShell('openPath', target)'` | pass | `ui/tests/unit/capture-main.behavior.test.ts:273`, `:284`, `:296` |

Every Red and Green receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/walkthrough.md) (§MEU-84 Red, §MEU-84 Green). 

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s36-84-red","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 6 command, verbatim","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"MEU-84 Red: pytest (AC-84.1, AC-84.2), Vitest (AC-84.3, 84.4, 84.6), build, Electron AC-84.5, red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1 plus MEU-82 and MEU-83 Green and the row 6 tests; no MEU-84 product code","output":"pytest 4 failed, 2 passed, 50 deselected | Vitest Test Files 3 failed (3), Tests 4 failed | 102 skipped | build exit 0 | Electron 1 failed (AC-84.5) | red-check: 3 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-84-green","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 7 command, verbatim","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"MEU-84 Green: pytest (test_capture_service, test_api_captures), Vitest (5 files), build, Electron capture-inbox, AC-84.5 repeat 10","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1 plus the MEU-82, MEU-83 and MEU-84 product changes","output":"pytest 56 passed, 1 warning | Vitest Test Files 5 passed (5), Tests 146 passed (146) | build exit 0 | Electron 30 passed | AC-84.5 --repeat-each 10: 10 passed","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-gate-row8","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-render-fidelity/session-gate.ps1 (task.md row 8, verbatim)","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"D6 session gate (attempt 5): identity, py-types, py-lint, py-lint-tools, ui-types, ui-lint, task-contract, scope-ast, scope-paths, py-tests (baseline rule G-1), ui-tests, ui-build, ui-harness-build, ui-picker-stub (G-2), openapi, state-render, ui-electron, e2e-repeat, identity-npm, identity-after","phase":"full","exit_code":0,"result":"pass","tested_state":"534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4","output":"session-gate: all steps exit 0 | py-tests 2 failed, 674 passed; baseline rule failed=2 outside_baseline=[] errors=0 | ui-tests 85 files, 815 tests passed | ui-electron 139 passed (2.8m) | e2e-repeat 20 passed (34.3s) | scope-ast frozen adapter functions changed: [] | scope-paths changed paths: 33 outside scope: [] | tested_state before == after","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-gate-h1-2","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-render-fidelity/session-gate.ps1 *> C:/Temp/av-kit/s36-gate-h1.txt (task.md H1-2, verbatim)","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"D6 session gate re-run at H1-2, the same steps as row 8","phase":"full","exit_code":0,"result":"pass","tested_state":"534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4","output":"session-gate: all steps exit 0 | py-tests 2 failed, 674 passed, 1 warning; baseline rule failed=2 outside_baseline=[] errors=0 | ui-tests 85 files, 815 tests passed | ui-electron 139 passed (2.5m) | e2e-repeat 20 passed (37.7s) | scope-ast frozen adapter functions changed: [] | scope-paths changed paths: 37 outside scope: [] | identity-npm @playwright/test@1.62.1, electron@42.9.3 | tested_state before == after","fresh":true}
```

### Quality Gate Results

The shared gate is `session-gate.ps1`, run at row 8 (attempt 5) and again at H1-2. Both runs printed the same `tested_state`. The handoffs and every row 9 hub file are project artifacts (`identity.py` `PROJECT_ARTIFACTS`), so H1-6b re-derives that state from the live tree.

**Two gate changes were made after plan approval**, both to the plan-local script only, with no test, assertion or product change. They are recorded in [walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-render-fidelity/walkthrough.md) §Gate and in the MEU-82 handoff Decision Log (D-25, D-26), and they are named in the execution review prompt:
- **G-1:** `py-tests` runs without `-x` and applies the plan's §Baseline rule. Pytest exit 1 passes only when every `FAILED` id is one of the two §Baseline packaging tests (`AC-24.10`, `AC-25.10`, which need the gitignored PyInstaller tree and ffmpeg) and nothing errors.
- **G-2:** the Electron suite's gitignored prerequisites become stages: `ui-harness-build` (AC-51.7) and `ui-picker-stub` (`capture-picker.test.ts`).

| Step | Stage | Exit | Decisive line (H1-2) |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 534beb1…+53752bff…15d4` |
| py-types, py-lint, py-lint-tools, ui-types, ui-lint, task-contract | static | 0 | `All checks passed!` (ruff) |
| scope-ast | static | 0 | `frozen adapter functions changed: []` |
| scope-paths | static | 0 | `changed paths: 37 outside scope: []` |
| py-tests | full | 1 → 0 (G-1) | `2 failed, 674 passed, 1 warning`; `baseline rule: failed=2 outside_baseline=[] errors=0` |
| ui-tests | full | 0 | `Test Files 85 passed (85)`, `Tests 815 passed (815)` |
| ui-build, ui-harness-build, ui-picker-stub | full | 0 | — |
| openapi | full | 0 | — |
| state-render | full | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` |
| ui-electron | runtime | 0 | `139 passed (2.5m)` |
| e2e-repeat | runtime | 0 | `20 passed (37.7s)` (AC-82.6 and AC-84.5, `--repeat-each=10`) |
| identity-npm | identity | 0 | `@playwright/test@1.62.1`, `electron@42.9.3` |
| identity-after | identity | 0 | `tested_state before == after` |


---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/capture.py` | modified | `RECONCILE` in `scan_inbox` |
| `ui/src/renderer/src/features/capture/capture-viewed-file.ts` | new | `viewedFilePath` |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modified | selection `viewedPath`; `openCaptureFile` / `openCaptureFolder` use it |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | passes `viewedPath` from `viewVariant` and `selected` |
| `ui/src/main/e2e-shell.ts` | new | `E2E_SHELL_LOG` (`e2eShellLog`, `recordE2eShell`) |
| `ui/src/main/index.ts` | modified | the two E2E branches call `recordE2eShell` and return |
| `tests/unit/test_capture_service.py` | modified | AC-84.1 |
| `tests/e2e/test_api_captures.py` | modified | AC-84.2 |
| `ui/tests/unit/capture-viewed-file.test.ts` | new | AC-84.3 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-84.4 |
| `ui/tests/unit/capture-main.behavior.test.ts` | modified | AC-84.6 |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | AC-84.5 |

Shared by all three MEUs (listed here and in each handoff):

| File | Action | Summary |
|------|--------|---------|
| `docs/build-plan/09-screenshot-capture.md` | modified (row 9) | `:366` Arrow row, `:367` Text row, `:723` Head row |
| `docs/build-plan/build-priority-matrix.md` | modified (row 9) | rows 9.15–9.17 |
| `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md` | modified (row 9, H1-3) | Phase 9 note, `last_updated`, MEU-82/83/84 status and `execution_plan`; the rendered regions |
| `docs/execution/plans/2026-10-14-capture-render-fidelity/session-gate.ps1` | modified (G-1, G-2) | the gate changes above |
| `docs/execution/plans/2026-10-14-capture-render-fidelity/red-check.py` | modified (row 2, S3) | strips ANSI CSI escapes before matching; two selftest fixtures |
| `docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md`, `task.md`, `walkthrough.md`, `human-gate-decision.md`, `baseline.sha` | modified/new | D-20/D-21 (TA-7, AC-83.9), row status, durable evidence |

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

## Corrections Applied

None yet. The execution review has not run.

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-30
    stage: execution
    question: "Does the capture selection gain a viewedPath beside originalPath, or replace it?"
    resolution: autonomous
    class: two-way
    chosen: "Replace originalPath with viewedPath; openCaptureFolder falls back to inboxDir only with no selection"
    source_tag: Local Canon
    precedents: ["implementation-plan.md MEU-84 Files table (viewedPath in the selection)", "capture-commands.ts had originalPath as the only consumer of the selection path"]
    research: { engine: none, sources: [] }
    reasoning: "Keeping both would leave a second path a later command could pick by mistake; one field means every command follows VIEWED_FILE."
  - id: D-31
    stage: execution
    question: "Which dependencies does the CapturePage selection effect need so a refetch that drops annotated_path updates the target?"
    resolution: autonomous
    class: two-way
    chosen: "annotations, selected, selectedId and viewVariant"
    source_tag: Local Canon
    precedents: ["AC-84.4 refetch case"]
    research: { engine: none, sources: [] }
    reasoning: "The selected shot object changes on refetch and viewVariant changes on the view toggle; both feed viewedFilePath."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-84 handoff after the row 8 gate and the H1-2 re-run |
