---
date: "2026-10-15"
project: "capture-chrome"
meu: "MEU-81"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-capture-chrome/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex via local dispatch (H1-7 execution review)"
predecessor: "2026-10-14-capture-chrome-MEU-80-handoff.md"
---

# Handoff: 2026-10-14-capture-chrome-MEU-81-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-81, `gui-capture-action-row`.
- **`ACTION_BUTTONS`.** `capture-toolbar.ts` adds the 7 marks-row actions with lucide icons and names, in `ACTION_ORDER`, disjoint from `TOOLBAR_BUTTONS`: Remove mark, Save overlay, Apply to image, Revert image, Open file, Open folder, Delete shot. Each renders as a `ToolbarIconButton` (MEU-80's `TOOLTIP` wrapper). Remove mark renders from `CaptureViewport.tsx` while a mark is selected; the per-shot actions render from `CapturePage.tsx`; Delete sits last, after a vertical separator.
- **Retired controls.** The Body/Tail/Head inspector, the four-button nudge pad and Sample original are gone, along with their 8 `RETIRED_TESTIDS`. `capture-sample.ts` is deleted, and so is its sampling state in `CapturePage.tsx`.
- **`NUDGE_TARGET` and `HANDLE_LAYER`.**
  - The arrow ends now render in their own `capture-handle-layer` svg. It is a sibling of the `aria-hidden` marks svg, with the same `viewBox`, inside `capture-zoom-content`.
  - Each end is a focusable `role="button"` circle named "Arrow tail" or "Arrow head".
  - Focusing an end makes the arrow keys move that end. Focusing the surface itself, a grab, a deselect, undo, redo, a tool change or a shot change resets the target to the body.
  - The target is a ref, not React state. The window key handler must see a handle focus and a keydown dispatched in the same task.
  - Arrow keys are ignored during a live pointer gesture (AC-81.7).
- **`MARKS_ROW_LAYOUT`.** The marks row is `shrink-0` and never scrolls. Only `capture-mark-list` scrolls (`min-w-0 flex-1 overflow-x-auto`); the action slot is `shrink-0`.
- **`HEADER_STATUS`.** `capture-header` is `flex-nowrap`. The hotkey banner is mounted only when the hotkey is in use, as a child of the header (a Hotkey warning chip plus the template text), so a free hotkey reserves no band.
- **Help.** The four-tools body carries `HELP_EDIT_TEXT`; no Capture help mentions Sample.
- **Registry.** `test-ids.ts` drops the 8 `RETIRED_TESTIDS` and adds the `NEW_TESTIDS` block after the MEU-67 block; AC-51.6 is re-pinned (TA-26).
- **Product fix found by AC-81.3, in scope.** Remove mark left the removed mark's color as an unapplied candidate, so Save stayed gated ("Apply or Cancel color"). `removeSelectedMark` now resets the candidate, as the empty-click deselect already did.
- **Test amendments.** TA-1–TA-7, TA-9, TA-10, TA-13, TA-16–TA-21 and TA-26 were applied as written, each tagged. TA-4 and TA-17 delete their tests.

**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` 09:695-701 (capture action row, nudge, header status).
**Predecessor**: MEU-80 (`TOOLTIP`, `ToolbarIconButton`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-81.1 | unit | `ACTION_BUTTONS`: the 7 ids, icons and names; unique ids, disjoint from `TOOLBAR_BUTTONS`; lucide icons | Spec 09:695; D-49 | `ui/tests/unit/capture-action-row.test.ts:362` | ✅ |
| AC-81.2 | unit | Each mounted action, enabled or disabled, is icon-only inside its `{id}-tip`, untitled, in `ACTION_ORDER`, with Delete last after the separator | Spec 09:695; D-49 | `capture-action-row.test.ts:380` | ✅ |
| AC-81.3 | unit | Each icon keeps its behavior: remove one mark, Save posts once, the Apply, Revert and Delete confirms, `openPath`, `showItemInFolder` | Spec 09:701 | `capture-action-row.test.ts:423` | ✅ |
| AC-81.4 | unit | `RETIRED_CONTROLS` are absent in every state, `capture-sample` cannot be imported, and the Color options are exactly well, hex, Apply, Cancel, Named | Spec 09:696-697; D-49, D-51 | `capture-action-row.test.ts:460` | ✅ |
| AC-81.5 | unit | Body nudge from the focused surface: each key moves the mark `KEYBOARD_NUDGE_PX`; one burst is one history entry; Esc restores | Spec 09:696; `NUDGE_TARGET` | `capture-action-row.test.ts:487` | ✅ |
| AC-81.6 | unit | `HANDLE_LAYER` structure and focus; a focused end takes the nudge | `NUDGE_TARGET`, `HANDLE_LAYER` | `capture-action-row.test.ts:544` | ✅ |
| AC-81.7 | unit | Arrow keys during a live pointer gesture move nothing and add no history | D-17 | `capture-action-row.test.ts:621` | ✅ |
| AC-81.8 | unit | `MARKS_ROW_LAYOUT` classes | Spec 09:698; D-50 | `capture-action-row.test.ts:662` | ✅ |
| AC-81.9 | integration | Electron `NO_OVERFLOW_FIXTURE` at 1280×800: the marks row never overflows and every action tip stays inside it, with Delete rightmost | Spec 09:698, 09:701 | `ui/tests/e2e/capture-inbox.test.ts:1781` | ✅ (10/10 under `--repeat-each=10`) |
| AC-81.10 | unit | `HEADER_STATUS` DOM: an in-use banner sits in `capture-header`, a free hotkey mounts none, and the header is `flex-nowrap` | Spec 09:699; D-64 | `capture-action-row.test.ts:673` | ✅ |
| AC-81.11 | integration | Electron `HOTKEY_IN_USE_FIXTURE` and `HEADER_GEOMETRY`: banner inside the header; header height and viewport top equal the free run's within ±0.5 px | Spec 09:699, 09:701; D-64 | `capture-inbox.test.ts:1917` | ✅ (10/10 under `--repeat-each=10`) |
| AC-81.12 | unit | Help holds `HELP_EDIT_TEXT`; no Capture help mentions Sample | D-51 | `capture-action-row.test.ts:702` | ✅ |
| AC-81.13 | unit | Registry: `RETIRED_TESTIDS` gone, `NEW_TESTIDS` after MEU-67, AC-51.6 re-pinned | E2; D-21 | `capture-action-row.test.ts:710` | ✅ |
| AC-81.14 | integration | Electron, real input at 100% after a pan: the handles track the arrow, a grab moves the head, and Tab then the arrow keys nudge it | D-32 | `capture-inbox.test.ts:1970` | ✅ (10/10 under `--repeat-each=10`) |
| AC-81.15 | unit | Key-ownership negatives: text draft, `capture-color`, filmstrip, confirm strip | D-17; D-26 | `capture-action-row.test.ts:749` | ✅ |

### Other plan AC references (not owned by MEU-81)

| AC | Owner | Status in MEU-81 |
|----|-------|------------------|
| AC-80.x | MEU-80 handoff | pass in `gate81` (Vitest and Electron `--tags`) |
| AC-60.10, AC-60.13, AC-60.19 | `capture-page.behavior.test.ts` | pass with TA-1, TA-2, TA-3, TA-5 and TA-6 as written |
| AC-57.2, AC-57.3, AC-57.6 | `capture-page.behavior.test.ts` | pass with TA-7 and TA-9 as written |
| AC-65.3 | `capture-page.behavior.test.ts` | pass with TA-10 as written (tags added late: A-2) |
| AC-67.20 | `capture-page.behavior.test.ts:2272` | pass with TA-12 (MEU-80) and TA-13 |
| AC-60.15 | `capture-help-content.test.ts:19` | pass with TA-16 |
| AC-51.6 | `layout-primitives.test.ts:200` | pass with TA-26 (re-pinned prefix hash) |
| W9-3, AC-60.12, AC-57.10, AC-65.4 | `capture-inbox.test.ts:213,488,756,888` | pass with TA-18–TA-21; the `:756` spec failed once at `GATE` run 11, intermittently (A-16), and passes at run 12 |
| AC-39.5, AC-39.28 | existing Capture suites | pass in `gate81` |
| AC-50.1, AC-50.4 | `layout-canon.test.ts` (row 10 hub) | ⏳ row 10; pass unchanged in `gate81` |
| AC-66.14 | `capture-inbox.test.ts:1141` | pass in `gate81`; AC-81.14 reuses its middle-button pan pattern |
| AC-66.11 | existing zoom suites | pass in `gate81`; cited by the plan as a precedent for `capture-zoom-content`, untouched by MEU-81 |
| AC-41.3 | `queue-canon.test.ts` | pass in `gate81` on this Windows host (`BASELINE_RED` tolerated, not needed); untouched by MEU-81 |
| AC-44.7, AC-55.1 | queue-card suites (MEU-80's consumers) | pass in `gate81`; untouched by MEU-81 |
| AC-49.27, AC-52 | `download-queue.test.ts`, `convert-queue.test.ts` (Electron; not in `gate81`) | failed at `GATE` run 3 through MEU-80's grip hint; pass at runs 4, 5, 7, 9, 10 and 12 with TA-27 and TA-28 (A-9, MEU-80 handoff); untouched by MEU-81 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-81.1–81.4, AC-81.6, AC-81.8, AC-81.10, AC-81.12–81.13 | `AssertionError` (red-81; the `capture-action-row` setup sentinel passes) | pass | `capture-action-row.test.ts:362-710` |
| AC-81.7 | `AssertionError` (the arrow keys moved the mark mid-gesture) | pass | `capture-action-row.test.ts:621` |
| AC-81.5, AC-81.15 | guards: pass at Red by design (the plan's `CASE_EVIDENCE`) | pass | `capture-action-row.test.ts:487,749` |
| TA-1–TA-3, TA-5–TA-7, TA-9, TA-13, TA-16, TA-26 | `AssertionError` | pass | `capture-page.behavior.test.ts:716,769,806,892,905,1019,1034,1096,2272`; `capture-help-content.test.ts:19`; `layout-primitives.test.ts:200` |
| Electron AC-81.9 | `expect()`: no `capture-delete-tip` | pass | `capture-inbox.test.ts:1781` |
| Electron AC-81.11 | `expect()`: no `capture-header` | pass | `capture-inbox.test.ts:1917` |
| Electron AC-81.14 | `expect()`: Tab does not reach `capture-handle-to` | pass | `capture-inbox.test.ts:1970` |

The rest of the red detail is in `task.md` §Evidence, Row 6. TA-18–TA-21 (`capture-inbox.test.ts:213,488,756,888`) are outside `-g AC-81`, so they first ran at the gate (`--tags`).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s34-red-81","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check red-81","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"vitest-red --meu 81 and e2e-red --meu 81 per CASE_EVIDENCE","phase":"red","exit_code":0,"result":"pass","tested_state":"MEU-80 implementation + MEU-81 tests, TA rows and NEW_TESTIDS; no MEU-81 source","output":"PASS red-81. Vitest: every AC-81 case collected, red cases fail by assertion, guards AC-81.5 and AC-81.15 pass, sentinel passes. Electron: AC-81.9, AC-81.11, AC-81.14 unexpected by expect()","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s34-green-81","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check green-81","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"MEU-80 and MEU-81 Vitest files and neighbours, ui build, Electron capture-inbox + console-chrome -g AC-8[01]","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-81 implementation","output":"PASS green-81. Vitest: 264/264, every MEU-80 and MEU-81 case and TA tag passed. Electron: expected 5, unexpected = flaky = skipped = 0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s34-gate81","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check gate81","cwd":"P:/av-kit-wt/s34-capture-chrome","scope":"ui typecheck, lint, full Vitest --meu 81, ui and harness build, Electron --tags, --repeat-each=10 over AC-80.10, AC-80.11, AC-81.9, AC-81.11 and AC-81.14","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-81 final working tree (baseline 5493b14 + MEU-80 and MEU-81 diffs + plan_checks.py A-1)","output":"PASS Vitest: 822/822 passed; MEU 80, 81 cases and tags passed | PASS Electron: expected 42, unexpected = flaky = skipped = 0; named cases passed | PASS Electron: expected 10 x5 (AC-80.10, AC-80.11, AC-81.9, AC-81.11, AC-81.14 repeats) | PASS gate81","fresh":true}
```

### Corrections recorded on the way (`walkthrough.md` §Amendments)

- **A-2.** TA-10 changed `MEU65_OPTION_IDS` but row 6 tagged no test. `[TA-10]` was added to the two tests that read it. No assertion changed.
- **A-3.** The new suite's `arrowEnds(index)` used DOM order, but the viewport paints the selected mark first. The helper now finds each arrow by its stroke color. No expected value changed.
- **A-4.** AC-81.14 checked the handle width after the keys as well. The plan checks only the centre there. The focused handle is 12 px across because of the 2 px focus stroke, against 11 px at rest. The width is now checked at rest only.
- **A-5.** In one `green-81` run, `HOTKEY_IN_USE_FIXTURE` timed out at 5 s without printing `HELD`. No holder was found, and the unchanged rerun passed. In `gate81`, AC-81.11 then passed 10/10 under `--repeat-each=10`.
- **A-6.** The first `gate81` run failed one existing spec, AC-59.12: the Arrow-tool drag made no arrow. The other 41 specs passed. It did not reproduce: AC-59.12 passed 10/10 alone, and the gate's own prefix (W9-1 to W9-7, then AC-59.12) passed 40/40 under `--repeat-each=5`, on the same build. No MEU-81 code is on that path. The unchanged rerun above is the gate of record, and the failed receipts are kept (`s34-gate81-run1-ac5912.txt`). AC-59.12 passes again at `GATE` run 4.

- **A-13 / D-39, A-14 (session tooling, not MEU product).** After execution review round 2 approved, `review-check` still refused: `tools/validate_closeout_artifacts.py` read round 1's Findings table of the rolling review, where F1 is open and blocking, and `validate-task.ps1:432` omitted `--max-review-rounds`. Mat chose "Fix the validator". `parse_review` now judges a rolling review by its latest round: each round runs to the next `## Recheck` heading; round 1's open blocking findings are carried through every recheck until one closes them by whole id in a `Recheck result` cell that is only a closure status (closed, fixed, resolved, verified, accepted, accepted_risk or withdrawn, optionally joined by / or ,); each round's own Findings tables (heading level 2 to 6) add their open blocking rows; a round without its own Findings table counts as one more open blocking finding; and `TABLE_ROW` reads a row with a blank first cell as data, so a finding without an id counts and can never be closed. Execution review round 3 attempt 1 (its verdict refused by the ledger, A-14) found three false approvals in the first design and the author a fourth; all were fixed test-first. Nineteen rolling-review selftest scenarios, red in four passes (`s34-d39-red.txt`, `-red2.txt`, `-red3.txt`, `-red4.txt`) and green (`s34-d39-green4.txt`: 215 arms, 0 failures). `PRODUCT_SCOPE` excepts that one `tools/` file, which is listed in MEU-81's Files Modified; `plan_checks.py` checks the exception (`FROZEN_EXCEPT`, three scope cases). No product file changed; `GATE` run 10 reran because these files are in `IDENTITY_SCOPE`.

```json
{"schema_version": "evidence.v1", "check_id": "s34-gate", "command": "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check gate, then -Check gate-check", "cwd": "P:/av-kit-wt/s34-capture-chrome", "scope": "GATE: the 17 D6 stages (CI installs, types, lint, pytest, full Vitest, builds, MCP tests, OpenAPI drift, state render, full Electron, source audit); gate-check applies CASE_EVIDENCE, COUNT_FLOORS and TA_LATE to the raw reports", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "304F53FCD0D7FF9B5C769E431A1390B25835D58B28BD3BDFDBFC8E6CACA3621E", "output": "PASS GATE: 17/17 stages exit 0; pytest 655 passed; Vitest 824/824; Electron expected 142, unexpected = flaky = skipped = 0 | PASS gate-check", "fresh": true}
```

The authoritative full gate is `GATE` run 12 (H1-3; `walkthrough.md` §Gate), `identity_after` `304F53FCD0D7FF9B5C769E431A1390B25835D58B28BD3BDFDBFC8E6CACA3621E`. It follows A-15, a value-identical rewrite of the plan's decision text (no product file changed), and A-16: run 11 on the same tree failed one Electron spec, AC-57.10 (`capture-inbox.test.ts:756`), intermittently (1 failure in 20 isolated repeats, then 100 of 100; archived `s34-gate-run11*`). Run 10 passed at `C694AB0D…06B1DA` (archived `s34-gate-run10*`) after A-14, the D-39 validator hardening. Run 9 passed at `396D7434…9DC103` (archived `s34-gate-run9*`) after A-13 / D-39. Run 7 passed at `A55CA7AF…AEF390` (archived `s34-gate-run7*`) after the execution review round 1 corrections (F1, F2) and A-12 (run 6 refused a duplicate AC-80.3 test title; archived `s34-gate-run6*`). Run 8 was stopped by the author after its pytest stage, because the D-39 validator hardening changed an `IDENTITY_SCOPE` file mid-run; its partial log is `s34-gate-run8-aborted.txt` and it is not a gate result. Run 5 passed at `F2A550D7…FDF8C2` (archived `s34-gate-run5*`), and run 4 passed before A-10 (a plan-local `handoff-ac` fix, D-38) changed `IDENTITY_SCOPE` files. Runs 1 to 3 failed on causes outside the product code. Their archived receipts were deleted by run 5's `s34-gate-*` cleanup (execution review R1 F2; the cleanup now spares `s34-gate-run<n>*`), so they are described from the console output read at the time: A-7 (no packaged backend in the fresh worktree, built), A-8 (no FFmpeg; the pinned download URL is dead, so the verified binaries were copied from the main checkout) and A-9 (two existing keyboard-drag tests; MEU-80's handoff, TA-27 and TA-28).

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint: 0 (--max-warnings 0)
Vitest (full suite): 86 files, 822/822
ui build + harness build: pass
Electron --tags: 42 expected, 0 unexpected, 0 flaky, 0 skipped
repeat-each=10: AC-80.10 10/10, AC-80.11 10/10, AC-81.9 10/10, AC-81.11 10/10, AC-81.14 10/10
```

`GATE` run 12 (H1-3):

```
17/17 stages exit 0; pytest 655 passed; Vitest 824/824
Electron (full): 142 expected, 0 unexpected, 0 flaky, 0 skipped
```

---

## Changed Files

Shared files carry both MEUs, so their counts are against the baseline (`5493b14`) and include MEU-80's lines.

| File | Action | Lines (vs baseline) | Summary |
|------|--------|---------------------|---------|
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modified | +23 | `ACTION_BUTTONS`, `ActionButtonId` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | +90/−177 (with MEU-80) | inspector, pad and Sample removed; `HANDLE_LAYER`; `MARKS_ROW_LAYOUT`; Remove mark icon; `onHandleFocus`/`onSurfaceFocus`; Space never arms pan from a handle |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | +110/−286 (with MEU-80) | sampling removed; `nudgeTargetRef`; gesture guard on the arrow keys; `removeSelectedMark` candidate reset; icon action row; `HEADER_STATUS` |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | +1/−1 | `HELP_EDIT_TEXT` |
| `ui/src/renderer/src/features/capture/capture-sample.ts` | deleted | −38 | D-51 |
| `ui/tests/unit/capture-action-row.test.ts` | new | 1–790 | AC-81.1–81.8, AC-81.10, AC-81.12, AC-81.13, AC-81.15 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | +182/−107 (with MEU-80) | TA-1–TA-7, TA-9, TA-10, TA-13 |
| `ui/tests/unit/capture-help-content.test.ts` | modified | +3/−3 | TA-16 |
| `ui/tests/unit/capture-sample.test.ts` | deleted | −56 | TA-17 |
| `ui/tests/unit/layout-primitives.test.ts` | modified | +2/−2 | TA-26 |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | +497/−29 (with MEU-80) | AC-81.9, AC-81.11, AC-81.14; TA-18–TA-21 |
| `ui/tests/e2e/test-ids.ts` | modified | +12/−8 (with MEU-80) | `RETIRED_TESTIDS` out, MEU-81 `NEW_TESTIDS` in |
| `tools/validate_closeout_artifacts.py` | modified | +468/−10 | D-39 (session tooling, not MEU-81 product): `parse_review` judges a rolling review by its latest round; `TABLE_ROW` keeps a blank-id row; nineteen rolling-review selftest scenarios |

```diff
-        <Button size="sm" variant="ghost" data-testid="capture-remove-mark" disabled={selectedIndex === null} onClick={onRemoveMark}>
-          Remove mark
-        </Button>
-        ... Body / Tail / Head, four nudge buttons ...
+        <div className="ml-auto flex shrink-0 items-center gap-1 pl-2">
+          {selectedIndex !== null ? (
+            <ToolbarIconButton spec={ACTION_BUTTONS['capture-remove-mark']} id="capture-remove-mark" variant="ghost" onClick={onRemoveMark} />
+          ) : null}
+          {actions}
+        </div>
```

### Design notes for the reviewer

- **Why the target is a ref.** No render reads `NUDGE_TARGET`. The window key handler must see a handle focus and a keydown dispatched in one task, which TA-3 does in one `act`. With state, that keydown read the previous target.
- **Handles and pointer input.** The handle circles are `pointer-events-none`. A grab still goes through the surface hit test, which already resolves handles, and a hit on a handle sets the target to that end. A keydown on a focused handle bubbles to the surface's handler.
- **Surface focus.** A focus moving onto a handle bubbles to the surface's `onFocus` too. Only a focus whose target is the surface itself resets the target, and never during a gesture.
- **Space pan.** `spaceArmable` treats `[role="button"]` as a control, so Space on a focused handle does not arm pan.

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

- **Intermittent, cause not found (A-16).** AC-57.10's Save overlay spec (`capture-inbox.test.ts:756`) failed once at `GATE` run 11: no arrow mark after `drawArrow`. Isolated repeats on this build failed 1 in 20, then passed 100 of 100 and 130 instrumented runs; the baseline `5493b14` passed 100 of 100. That sample cannot rule out a session-side cause (this MEU rewired the toolbar buttons and the marks row). Not hardened here: a wait in the spec would hide a possible product race. Mat can decide whether a later MEU hardens `drawArrow` or investigates a dropped first drag.
- **Observation, not fixed (baseline behavior, no AC).** Undo and redo clear the selection but keep the color candidate. If a selected mark's color differed from the applied color, Save then stays gated until Apply or Cancel color. This is the same pattern AC-81.3 found for Remove mark, but undo and redo are outside every MEU-81 AC, so this MEU leaves them alone. Mat can decide whether a later MEU should apply the same reset.

---

## Decision Log

```yaml
decision_log:
  - id: D-35
    stage: execution
    question: "TA-3 dispatches a handle focus and a keydown in one act, and the keydown read the previous nudge target. Should the target be state or a ref?"
    resolution: autonomous
    class: two-way
    chosen: "A ref (nudgeTargetRef), set on handle focus, on surface focus outside a gesture, and on a handle grab, and reset to body wherever the selection or tool changes."
    source_tag: Local Canon
    precedents: ["implementation-plan.md NUDGE_TARGET: the focused handle chooses the end", "CapturePage.tsx gestureRef and annotationsRef: values read by event handlers are refs"]
    research: { engine: none, sources: [] }
    reasoning: "No render depends on the target, since the retired inspector buttons were its only reader. The key handler is an event path, and the page already keeps such values in refs. This changes no AC."
  - id: D-36
    stage: execution
    question: "AC-81.3 found that Save stays gated after Remove mark: the removed mark's color is left as an unapplied candidate. Fix it, or treat it as outside scope?"
    resolution: autonomous
    class: two-way
    chosen: "Fix in removeSelectedMark (CapturePage.tsx, in PRODUCT_SCOPE): clear the named preview and reset the candidate to the applied color, as the empty-click deselect already does."
    source_tag: Local Canon
    precedents: ["implementation-plan.md AC-81.3: Save posts annotate once after the other actions", "CapturePage.tsx select pointerdown on a miss: the existing deselect reset"]
    research: { engine: none, sources: [] }
    reasoning: "The AC requires Save to work in this sequence, the file is in PRODUCT_SCOPE, and the fix reuses the page's existing deselect reset. No test was loosened."
  - id: D-39
    stage: execution
    question: "review-check refuses the approved round 2: parse_review reads round 1's Findings table of the rolling review (F1 open, blocking). tools/ is frozen (S6). Which fix?"
    resolution: human
    class: two-way
    chosen: "Option 3: parse_review judges a rolling review by its latest round, carrying each open blocking finding through every recheck until one closes it by whole id with a closure-status cell, an unreadable round refusing; PRODUCT_SCOPE excepts tools/validate_closeout_artifacts.py only."
    source_tag: Human-approved
    precedents: ["walkthrough.md A-13 — USER_EXPLICIT Mat 2026-10-15 'Fix the validator'", "implementation-plan.md decision_log D-39"]
    research: { engine: none, sources: [] }
    reasoning: "Round 1's table never changes in a rolling review, so a first-table reader refuses every recheck approval. The latest-round reading stays fail-closed: silence, prose, a prefix id, a new blocking row, an unreadable round or a blank id all refuse. Execution review round 3 attempt 1 found three of those holes in the first design (A-14); round 3 reviews the change."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-15 | claude-code | Initial handoff after gate81 |
| Reconciled | 2026-10-15 | claude-code | H1-5: `GATE` run 5, A-7 to A-10; AC-49.27 row corrected (not in `gate81`) |
| Corrected | 2026-10-15 | claude-code | Execution review R1: F1 (Escape in the capture phase; two AC-80.3 regressions), F2 (archive cleanup; retention claims corrected); A-12 retitle; `GATE` run 7 |
| Corrected | 2026-10-15 | claude-code | A-13 / D-39: the closeout validator reads a rolling review's latest round (Mat: "Fix the validator"); `GATE` run 9 |
| Corrected | 2026-10-15 | claude-code | A-14: the D-39 parser hardened after execution review round 3 attempt 1 (exact ids, a closure-status cell, unreadable rounds refuse, blank-id rows count); `GATE` run 10 |
| Corrected | 2026-10-15 | claude-code | A-15: decision records rewritten value-identically; A-16: `GATE` run 11 failed AC-57.10 (`capture-inbox.test.ts:756`) once, intermittently; `GATE` run 12 |
