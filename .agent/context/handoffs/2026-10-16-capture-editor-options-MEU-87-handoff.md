---
date: "2026-10-16"
project: "capture-editor-options"
meu: "MEU-87"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-16-capture-editor-options/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: ".agent/context/handoffs/2026-10-16-capture-editor-options-MEU-86-handoff.md"
---

# Handoff: 2026-10-16-capture-editor-options-MEU-87-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-87 — `gui-capture-tool-lock`. A new tool lock keeps the current tool after each mark. With the lock off, the editor still switches to Select after each mark, as before.

What changed:
- **`TOOL_LOCK`.** `TOOLBAR_BUTTONS` gains `'capture-tool-lock'`, which uses the lucide `Lock` icon and is named "Keep tool after drawing". It is not added to `TOOL_BUTTON_IDS`.
  - `CaptureViewport` renders it as a `ToolbarIconButton` straight after the "Annotation tool" group.
  - It sets `pressed={toolLocked}`, so the button has `aria-pressed`, and uses the active-tool variant while on.
  - It stays enabled with or without a shot.
  - `toolLocked` is page view state: default `false`, never persisted, and not part of the overlay. Toggling it never changes `dirty`, the tool or the selection.
- **`LOCK_KEEPS_TOOL`.** With the lock on, a drawn mark and a text commit skip `commitSelection`, so the tool stays and nothing is selected. With the lock off, both paths are unchanged (AC-60.4).
- **`LOCK_PERSISTS`.** Choosing another tool keeps the lock on. Only the lock button turns it off (D-19, approved by Mat on 2026-10-16).
- **Help.** The `four-tools` help body gains "The lock button keeps the current tool after each mark."

**Test amendments applied:**
- **TA-2:** the AC-80.8 title now says "the 13 Capture toolbar buttons". The body is unchanged.
- **TA-3:** `CAPTURE_TOOL_LOCK` is added to `test-ids.ts`.

No other existing assertion changed. The lock adds no overflow, so AC-65.4 passes at the default window and the S2 stop does not apply.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-87.1 | unit | `TOOLBAR_BUTTONS['capture-tool-lock']` has the `Lock` icon and the name "Keep tool after drawing", and is not a tool | `TOOL_LOCK`; D-18 | `ui/tests/unit/capture-toolbar.test.ts:124`; negative (`TOOL_BUTTON_IDS` keeps the five tools) `:131` | ✅ |
| AC-87.2 | integration | The lock sits straight after the Annotation tool group and toggles `aria-pressed` without changing the tool or selection and without enabling Save | `TOOL_LOCK` | `ui/tests/unit/capture-page.behavior.test.ts:2565`; negative (no shot: lock enabled, tools disabled) `:2588` | ✅ |
| AC-87.3 | integration | Lock on with Box: two drags keep Box with nothing selected; two Undos remove the boxes one at a time | `LOCK_KEEPS_TOOL` | `capture-page.behavior.test.ts:2599`; negative (lock off returns to Select, AC-60.4) `:2618` | ✅ |
| AC-87.4 | integration | Lock on with Text: a commit keeps Text with nothing selected, and the next click opens a new draft | `LOCK_KEEPS_TOOL` | `capture-page.behavior.test.ts:2629`; negative (lock off selects the text) `:2646` | ✅ |
| AC-87.5 | integration | The lock survives a tool change (Box, then Arrow); turning it off restores auto-Select from the next mark | `LOCK_PERSISTS`; D-19 | `capture-page.behavior.test.ts:2656`; negative (choosing Arrow keeps the lock) `:2677` | ✅ |
| AC-87.6 | integration | Electron, real input: lock on, two Box drags give 2 rects, and `capture-tool-box` keeps `aria-pressed="true"` | Spec 09:777; `RENDERER_PIN` | `ui/tests/e2e/capture-inbox.test.ts:2408`; also in the gate's e2e-repeat ×10 | ✅ |
| AC-87.7 | unit | The `four-tools` help body contains the lock sentence | `HELP_SENTENCES`; D-20 | `ui/tests/unit/capture-help-content.test.ts:65` | ✅ |
| AC-57 (cross-ref) | regression | AC-57.5 no-shot tools stay disabled; the lock is not a tool | Local Canon | `capture-page.behavior.test.ts:1283` `AC-57.5 with no shot the tools are disabled …` | ✅ |
| AC-60 (cross-ref) | regression | AC-60.4 auto-Select after a draw is unchanged with the lock off | `LOCK_KEEPS_TOOL` | `capture-page.behavior.test.ts:601` `AC-60.4 …`; `:2618` (AC-87.3 negative) | ✅ |
| AC-65 (cross-ref) | regression | AC-65.1 `TOOL_BUTTON_IDS` keeps the five tools, and AC-65.4 `NO_OVERFLOW` holds with the lock | Local Canon | `capture-toolbar.test.ts:44` `AC-65.1 …`; `capture-inbox.test.ts:888` `AC-65.4 …` | ✅ |
| AC-80 (cross-ref) | regression | AC-80.8, amended by TA-2: the 13 Capture toolbar buttons are wrapped, untitled and hinted, with and without a shot | plan `TEST_AMENDMENTS` | `ui/tests/unit/icon-hints.test.ts:308` | ✅ |
| AC-85 (cross-ref) | — | Owned by MEU-85 | plan MEU-85 | [MEU-85 handoff](2026-10-16-capture-editor-options-MEU-85-handoff.md) | see MEU-85 |
| AC-86 (cross-ref) | — | Owned by MEU-86 | plan MEU-86 | [MEU-86 handoff](2026-10-16-capture-editor-options-MEU-86-handoff.md) | see MEU-86 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-87.1 | `AssertionError: expected undefined to be 'Keep tool after drawing'` | pass | `ui/tests/unit/capture-toolbar.test.ts:124` |
| AC-87.1 negative | passes on the baseline, as planned: it guards that `TOOL_BUTTON_IDS` keeps exactly the five tools | pass | `capture-toolbar.test.ts:131` |
| AC-87.2 to AC-87.5 (eight tests, four negatives) | `AssertionError: expected null not to be null` at the `capture-tool-lock` presence check | pass | `ui/tests/unit/capture-page.behavior.test.ts:2565`–`:2677` |
| AC-87.6 | `Error: expect(received).toBe(expected)`, expected 1, received 0 (lock count, `ELECTRON_RED`); the `RENDERER_PIN` assertion before it passed | pass (910ms) | `ui/tests/e2e/capture-inbox.test.ts:2408` |
| AC-87.7 | `AssertionError: expected 'Arrow, Box, Highlight, and Text draw …' to contain 'The lock button keeps the current too…'` | pass | `ui/tests/unit/capture-help-content.test.ts:65` |

In the Red run, 10 unit tests failed and 1 guard passed, across 3 files. `red-check.py` reported 2 receipts and 0 problems. The guard read `ui/src` as the row 5 hash `9c3682b0…`.

One test changed after Red. The AC-87.2 negative now uses the suite's no-shot setup, as AC-57.5 and AC-65.2 do. No assertion changed, and in the Red run that test had already failed earlier, at the lock presence check. Every receipt is in [walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-editor-options/walkthrough.md) §MEU-87 Red and §MEU-87 Green.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s37-87-red","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 6 command, verbatim","cwd":"P:/av-kit-wt/s37-capture-editor-options","scope":"MEU-87 Red: Vitest (capture-toolbar AC-87.1, capture-page.behavior AC-87.2-87.5, capture-help-content AC-87.7, icon-hints TA-2), Electron AC-87.6, red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"base 90bb409 plus MEU-85 and MEU-86 (ui/src sha256 9c3682b0a24aa0b48c1ed6c560c6072771803f3daabeebd03c8af1e01eb03ad0) and the row 6 tests","output":"Vitest 3 files failed, Tests 10 failed | 1 passed | 111 skipped | Electron AC-87.6 failed: expected 1, received 0 | red-check: 2 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s37-87-green","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 7 command, verbatim","cwd":"P:/av-kit-wt/s37-capture-editor-options","scope":"MEU-87 Green: typecheck, targeted Vitest (8 files), build, Electron capture-inbox","phase":"green","exit_code":0,"result":"pass","tested_state":"base 90bb409 plus the MEU-85, MEU-86 and MEU-87 product changes","output":"tsc clean | Test Files 8 passed, Tests 178 passed | built | Electron capture-inbox 37 passed","fresh":true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-gate-h1-2-run1", "command": "$env:ELECTRON_RUN_AS_NODE=$null; $env:ELECTRON_RENDERER_URL=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-editor-options/session-gate.ps1 *> C:/Temp/av-kit/s37-gate-h1.txt (task.md H1-2, verbatim; run 1, archived as s37-gate-h1-run1.txt)", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "D6 session gate, H1-2 run 1, at the row 8 run 3 tested_state (before A-3)", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "90bb40977e487f4893a1c586c2c20b8f78ef105f+3dab0639e1c9cf76cd09e0e0055069ec42b14fb84651177246fb18afe42187a3", "output": "every step through ui-electron exit 0 | e2e-repeat exit=1: AC-85.10 toHaveAttribute Received \"8\" (expected \"23\") | 1 failed, 29 passed (36.7s) | identity-npm and identity-after not_run (fail-fast) | S6; fixed by A-3", "fresh": false}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-gate-h1-2-run2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; $env:ELECTRON_RENDERER_URL=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-editor-options/session-gate.ps1 *> C:/Temp/av-kit/s37-gate-h1.txt (task.md H1-2, verbatim; run 2, archived as s37-gate-h1-run2.txt)", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "D6 session gate, H1-2 run 2, on the A-3 tree (before A-4)", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "90bb40977e487f4893a1c586c2c20b8f78ef105f+85fb01616ad9131e0ecef67c62cebe3d353753fc774244ef963e0efd1d7a0b8e", "output": "every step through scope-paths exit 0 | py-tests baseline rule pass | ui-tests exit=1: queue-canon.test.ts AC-41.3 Expected \"#ea580c\" Received \"#9a3412\" | 1 failed, 878 passed (879) | later steps not_run (fail-fast) | external: Zorivest 1f254832 (MEU-662); A-4 and known issue QUEUE-PILL-TOKEN-DRIFT", "fresh": false}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; $env:ELECTRON_RENDERER_URL=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-editor-options/session-gate.ps1 *> C:/Temp/av-kit/s37-gate-h1.txt (task.md H1-2, verbatim; run 4, after the execution review round 1 corrections)", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "D6 session gate, H1-2 run 4 after execution review round 1 (F1, F2): identity, py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract, scope-paths, py-tests (baseline rule), ui-tests (baseline rule), mcp-build, mcp-tests, ui-build, ui-harness-build, ui-picker-stub, openapi, state-render, ui-electron, e2e-repeat, identity-npm, identity-after", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "90bb40977e487f4893a1c586c2c20b8f78ef105f+5b04639a56a3e580f8a41cad881a7a5043c191d1ea867dc5ae6f251dd774fa93", "output": "session-gate: all steps pass | py-tests 2 failed, 674 passed, 1 warning; baseline rule failed=2 outside_baseline=[] errors=0 | ui-tests Test Files 1 failed | 87 passed (88), Tests 1 failed | 882 passed (883); baseline rule failed=1 summary_failed=1 outside_baseline=[] unhandled=0 (AC-41.3 only) | mcp-tests 411 passed (411) | ui-electron 147 passed (3.3m) | e2e-repeat 30 passed (50.4s) | scope-paths changed paths: 42 outside scope: [] | identity-npm @playwright/test@1.62.1, electron@42.9.3 | tested_state before == after", "fresh": true}
```

### Quality Gate Results

The shared gate is `session-gate.ps1`. The gate of record is H1-2 run 4, after the execution review round 1 corrections (F1, F2), at `tested_state` `90bb40977e487f4893a1c586c2c20b8f78ef105f+5b04639a56a3e580f8a41cad881a7a5043c191d1ea867dc5ae6f251dd774fa93`. The handoffs and the row 9 hub and state files are excluded from that identity, so H1-6b re-derives it from the live tree.

Earlier runs are recorded in [walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-editor-options/walkthrough.md) §Gate:
- **A-1, row 8 run 1, `ui-tests`.** TA-3 had put the new ids inside the `test-ids.ts` prefix that AC-51.6 and AC-81.13 pin by hash. The ids moved, unchanged, to a tail block, and no assertion changed.
- **A-2, row 8 run 2, `ui-electron`.** The untouched Convert test W8-12 failed once with `Target crashed`. It then passed 20/20 alone and 147/147 in run 3.
- **Row 8 run 3** passed every step at `90bb409…+3dab0639…87a3`.
- **A-3, H1-2 run 1, `e2e-repeat`** (S6; record `s37-gate-h1-2-run1`). AC-85.10 failed once: one 10 px step, then the drag froze (`Received "8"`). With pointer capture refused, the pre-A-3 field reproduces exactly that value. Mat chose to harden the drag: `SCRUB_DRAG_WINDOW` follows window pointer events. The MEU-85 handoff holds the A-3 Red, Green and probe records.
- **A-4, H1-2 run 2, `ui-tests`** (record `s37-gate-h1-2-run2`). AC-41.3 (`queue-canon.test.ts`) failed: it reads Zorivest's `globals.css` live, and Zorivest `1f254832` (MEU-662) darkened three light status-pill hexes during the run. Session 37 touches none of its inputs, and av-kit `main` fails it too. Mat chose a ui-tests baseline rule (`baseline-ui-failed.txt`, `ui-baseline-rule.ps1`, probed 6/6) and known issue `QUEUE-PILL-TOKEN-DRIFT`. No product or test file changed for A-4.
- **H1-2 run 3** passed every step at `90bb409…+7f784552…24dc` and was the round 1 gate of record. The round 1 corrections changed `CaptureScrubField.tsx`, `CaptureViewport.tsx`, `CapturePage.tsx` and `capture-page.behavior.test.ts`, so run 4 replaces it; its receipts are archived as `s37-gate-h1-run3.txt` and `s37-gate-run3/`. Run 3 has no evidence record here: `durable_evidence.py --require-full` admits a passing full gate only at the current `tested_state`. Its observations were pytest `2 failed, 674 passed, 1 warning` (baseline rule), Vitest `Tests 1 failed | 878 passed (879)` (AC-41.3 only), MCP 411/411, Electron `147 passed (4.2m)`, repeat `30 passed (32.5s)`, `changed paths: 39 outside scope: []`.

The table below is run 4.

| Step | Stage | Exit | Decisive line (H1-2) |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 90bb409…+5b04639a…fa93` |
| py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract | static | 0 | — |
| scope-paths | static | 0 | `changed paths: 42 outside scope: []` |
| py-tests | full | 1 → pass (baseline rule) | `2 failed, 674 passed, 1 warning`; `baseline rule: failed=2 outside_baseline=[] errors=0` |
| ui-tests | full | 1 → pass (baseline rule, A-4) | `Test Files 1 failed \| 87 passed (88)`, `Tests 1 failed \| 882 passed (883)`; `ui-tests baseline rule: failed=1 summary_failed=1 outside_baseline=[] unhandled=0` (AC-41.3 only; +4 R1 regressions) |
| mcp-build, mcp-tests | full | 0 | `Tests 411 passed (411)` |
| ui-build, ui-harness-build, ui-picker-stub | full | 0 | — |
| openapi | full | 0 | — |
| state-render | full | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` |
| ui-electron | runtime | 0 | `147 passed (3.3m)` |
| e2e-repeat | runtime | 0 | `30 passed (50.4s)` (AC-85.10, AC-86.3 and AC-87.6, `--repeat-each=10`) |
| identity-npm | identity | 0 | `@playwright/test@1.62.1`, `electron@42.9.3` |
| identity-after | identity | 0 | `tested_state before == after` |

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modified | `Lock` import; `capture-tool-lock` entry (`TOOL_LOCK`) |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | the lock button; `toolLocked` and `onToggleToolLock` props |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | `toolLocked` state; `LOCK_KEEPS_TOOL` in the drawn-create and text-commit paths |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | lock sentence |
| `ui/tests/unit/capture-toolbar.test.ts` | modified | AC-87.1 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-87.2 to AC-87.5 |
| `ui/tests/unit/capture-help-content.test.ts` | modified | AC-87.7 |
| `ui/tests/unit/icon-hints.test.ts` | modified | TA-2 (title only) |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | AC-87.6 |
| `ui/tests/e2e/test-ids.ts` | modified | TA-3 tail block (`CAPTURE_TOOL_LOCK`; A-1) |

Shared by all three MEUs (listed in each handoff):

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx`, `CapturePage.tsx`, `capture-help-content.ts` | modified | each MEU's part is listed above (`CaptureScrubField.tsx`, including A-3, is MEU-85's) |
| `ui/tests/unit/capture-page.behavior.test.ts`, `capture-help-content.test.ts`, `ui/tests/e2e/capture-inbox.test.ts`, `test-ids.ts` | modified | each MEU's tests are listed above |
| `docs/build-plan/09-screenshot-capture.md` | modified (row 9) | three Plan notes (`:755`, `:767`, `:780`) |
| `docs/build-plan/gui-actions-index.md` | modified (row 9) | `capture:tool_lock` row |
| `docs/build-plan/build-priority-matrix.md` | modified (row 9) | rows 9.18–9.20 |
| `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md` | modified (row 9, H1-3) | Phase 9 note; MEU-85/86/87 status and `execution_plan`; the rendered regions |
| `.agent/context/known-issues.yaml`, `known-issues.md` | modified (A-4) | new open issue `QUEUE-PILL-TOKEN-DRIFT`; the md is re-rendered |
| `docs/execution/plans/2026-10-16-capture-editor-options/` | new | plan, task, walkthrough, `session-gate.ps1`, `identity.py`, `red-check.py`, `contrast-probe.py`, `select-popup-probe.*`, `baseline.sha`, `baseline-py-failed.txt`, `baseline-ui-failed.txt` and `ui-baseline-rule.ps1` (A-4) |

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
|----|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Corrections Applied

Execution review round 1 (Codex `gpt-6.1-sol`, `changes_required`, [canonical review](2026-10-16-capture-editor-options-implementation-critical-review.md)) found no MEU-87 defect; its two findings were in MEU-85 (see the [MEU-85 handoff](2026-10-16-capture-editor-options-MEU-85-handoff.md)). No MEU-87 product line changed; the MEU-87 test line references in the AC table moved by the inserted MEU-85 regressions. The shared gate was re-run in full on the corrected tree (H1-2 run 4), and the Quality Gate Results above record it.

## Deferred Items

None.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-87 handoff after the row 8 gate and the H1-2 re-run |
| Amended | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Execution review round 1: no MEU-87 finding; shared gate re-run as H1-2 run 4 |
