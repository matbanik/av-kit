---
date: "2026-10-16"
project: "capture-editor-options"
meu: "MEU-85"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-16-capture-editor-options/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: ".agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-84-handoff.md"
---

# Handoff: 2026-10-16-capture-editor-options-MEU-85-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-85 — `gui-capture-size-scrub`. You can now change the Stroke and font Size fields with the mouse or the keyboard. The mark previews live, and each gesture is one undo step.

What changed:
- **Gestures (`SCRUB_GESTURES`).** You can drag the "Stroke" or "Size" label, roll the wheel over the field, or press Up/Down in the field. Shift moves in steps of 10, and Alt makes a drag fine. The step sizes and limits are in `SCRUB_MATH` (new `capture-scrub.ts`).
- **Limits.** The scrub stops at 1–100 for stroke and 1–400 for font size. These limits apply only to the scrub, never push a value against the gesture, and leave the wire contract alone. `parsePositiveInt` moved to `capture-scrub.ts` unchanged.
- **Field (`SCRUB_FIELD`, `SIZE_LABELS`).** The new `CaptureScrubField.tsx` adds a label handle with `aria-hidden`. The `<input>` keeps its `data-testid`, `aria-label` and value, and it stays the only tab stop. While a drag is open, `SCRUB_ALT_GUARD` stops Electron's menu bar from taking focus on Alt.
- **Preview and history (`SIZE_BURST`).** `CapturePage.tsx` keeps one burst per gesture:
  - A preview edits the selected mark without adding history.
  - `finishSize()` pushes one undo step.
  - `cancelSize()` (Escape) restores the start value.
  - Every handler that writes marks, the selection or history calls `finishSize()` first.
  - While a burst is open, Undo and Redo are disabled and return early.
  - A shot change discards the burst.
- **Typed edits (`TYPED_EDITS`).** Typing in the fields works as before.
- **Help (`HELP_SENTENCES`).** The `four-tools` help section gains the scrub sentence.

**Test amendments applied:**
- **TA-3:** the e2e ids `CAPTURE_STROKE_SCRUB` and `CAPTURE_FONT_SIZE_SCRUB`.
- **TA-4:** the AC-57.5 `closest('label')` line becomes the handle text plus the input `aria-label`.

No other existing assertion changed. All changes are in the Capture renderer: the gate's `scope-paths` reports `outside scope: []`, and nothing under `packages/`, `mcp-server/` or `openapi.committed.json` changed (H1-4).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-85.1 | unit | `scrubSteps` truncates toward zero and carries the remainder (5 px → 2 steps, carry 1; 15 px fine → 1, carry 7); the `SCRUB_MATH` constants | `SCRUB_MATH`; D-10 | `ui/tests/unit/capture-scrub.test.ts:45`; negative (1 px → no step) `:58` | ✅ |
| AC-85.2 | unit | `clampScrub` clamps to `[min, max]` and never moves against the gesture (500 + 1 → 500, 500 − 1 → 499); `parsePositiveInt` is exported unchanged | `SCRUB_MATH` | `capture-scrub.test.ts:62`; negative (`'0'`, `'-3'`, `'2.5'`, `'abc'`, `''` → `null`) `:71` | ✅ |
| AC-85.3 | unit | Handle drag: +20 px from `'3'` previews 13, Shift +4 px gives 23, Alt +16 px gives 5, pointerup commits once; a press with no move selects the text | `SCRUB_GESTURES`; `SCRUB_BASE` | `capture-scrub.test.ts:136`, `:166`; negative (Escape cancels, secondary button does nothing) `:178`; R1-F1 `SCRUB_BASE`: invalid text on a selected stroke-20 box scrubs to 21, not 4 (`capture-page.behavior.test.ts:2290`) | ✅ |
| AC-85.4 | unit | Wheel and keys: three notches give 4, 5, 6 and one commit after `WHEEL_RESET_MS`; Shift + horizontal wheel +10; ArrowUp +1 with keyup commit; Shift+ArrowDown −10; unparsable text starts from `fallback` | `SCRUB_GESTURES`; D-11 | `capture-scrub.test.ts:202`, `:222`; negative (Ctrl+wheel, ArrowLeft) `:244`; R1-F1 `SCRUB_BASE`: an empty Size field on a selected size-40 text steps to 41, not 17 (`capture-page.behavior.test.ts:2310`) | ✅ |
| AC-85.5 | unit | `SCRUB_ALT_GUARD`: during a drag, window Alt keydown and keyup are prevented | `SCRUB_ALT_GUARD`; D-12 | `capture-scrub.test.ts:254`; negative (after pointerup) `:263` | ✅ |
| AC-85.6 | integration | A Stroke drag previews the selected box live and disables Save; one Undo restores 3, and Redo gives 13. A font wheel burst is one step, and Undo stays off until `WHEEL_RESET_MS` | `SIZE_BURST`; Spec 09:753 | `ui/tests/unit/capture-page.behavior.test.ts:2161`; negative (Escape restores 3, no history) `:2194`; off-label drag without pointer capture keeps scrubbing, one undo step (A-3) `:2214` | ✅ |
| AC-85.7 | integration | With no applicable mark, a drag sets only the field (8), and the next box uses it | `SIZE_BURST` | `capture-page.behavior.test.ts:2234` (an unselected box keeps 3) | ✅ |
| AC-85.8 | integration | Typed edits keep one undo step per change; a typed change ends an open wheel burst (two steps) | `TYPED_EDITS`; D-14 | `capture-page.behavior.test.ts:2250`; negative (typed `0`) `:2280` | ✅ |
| AC-85.9 | integration | The handles read "Stroke" and "Size", are `aria-hidden` with no `tabindex`, Tab reaches only the inputs, and the inputs keep their `aria-label` | `SIZE_LABELS`; `SCRUB_FIELD`; D-15 | `capture-page.behavior.test.ts:2327`; negative (input not in a `<label>`) `:2356` | ✅ |
| AC-85.10 | integration | Electron, real input: +40 px gives 23 before `mouse.up`, Shift +6 px gives 53, +200 px past the edge gives 100, and three Undos give 53, 23, 3 | Spec 09:752-753; `RENDERER_PIN` | `ui/tests/e2e/capture-inbox.test.ts:2331`; also in the gate's e2e-repeat ×10. H1-2 run 1 failed it once (one step, then frozen); A-3 fixed the cause | ✅ |
| AC-85.11 | unit | The `four-tools` help body contains the scrub sentence | `HELP_SENTENCES`; D-20 | `ui/tests/unit/capture-help-content.test.ts:55` | ✅ |
| AC-85.12 | integration | One owner (R1-F1): (a) a nudge finishes the burst first; (b) selecting another mark finishes it on the first mark only, and after a keyboard selection of a differently sized mark the next notch starts from that mark (R1-F2); (c) Escape cancels an unfocused burst; (d) Undo and Redo are held while it is open; (e) a shot change discards it | `SIZE_BURST` | `capture-page.behavior.test.ts:2364` (a), `:2390` (b), `:2412` and `:2437` (b, R1-F2: two boxes, then two texts), `:2461` (c), `:2481` (d), `:2516` (e) | ✅ |
| AC-57 (cross-ref) | regression | AC-57.5 toolbar labels, amended by TA-4: the handle text is "Stroke" and the input keeps "Stroke width" | plan `TEST_AMENDMENTS` (R1-F3) | `capture-page.behavior.test.ts:1262` `AC-57.5 toolbar: …` | ✅ |
| AC-60 (cross-ref) | regression | AC-60.4 auto-Select after a draw is unchanged; AC-60.10 Save refusal during a nudge burst still holds beside the size burst | Local Canon | `capture-page.behavior.test.ts:601` `AC-60.4 …`; `:738` `AC-60.10 …` | ✅ |
| AC-65 (cross-ref) | regression | AC-65.3 option edits (stroke on an arrow, font size on a text) and AC-65.4 `NO_OVERFLOW` hold with the scrub handles | Local Canon | `capture-page.behavior.test.ts:1544` `AC-65.3 options keep their behavior …`; `capture-inbox.test.ts:888` `AC-65.4 …` | ✅ |
| AC-80 (cross-ref) | — | AC-80.8 (TA-2) is owned by MEU-87 | plan MEU-87 | [MEU-87 handoff](2026-10-16-capture-editor-options-MEU-87-handoff.md) | see MEU-87 |
| AC-86 (cross-ref) | — | Owned by MEU-86 | plan MEU-86 | [MEU-86 handoff](2026-10-16-capture-editor-options-MEU-86-handoff.md) | see MEU-86 |
| AC-87 (cross-ref) | — | Owned by MEU-87 | plan MEU-87 | [MEU-87 handoff](2026-10-16-capture-editor-options-MEU-87-handoff.md) | see MEU-87 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-85.1 to AC-85.5 | `Failed to resolve import "../../src/renderer/src/features/capture/CaptureScrubField"` (declared new module) | pass | `ui/tests/unit/capture-scrub.test.ts:45`–`:263` |
| AC-85.6 to AC-85.9, AC-85.12 (a)–(e) | `AssertionError: expected null not to be null` at `expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()` | pass | `ui/tests/unit/capture-page.behavior.test.ts:2161`–`:2516` |
| AC-85.3, AC-85.4 `SCRUB_BASE` (R1-F1) | `AssertionError: expected [ '4' ] to deeply equal [ '21' ]`; `expected [ '17' ] to deeply equal [ '41' ]` (the field fell back to 3 and 16) | pass | `capture-page.behavior.test.ts:2290`, `:2310` |
| AC-85.12 (b) keyboard selection (R1-F2) | `AssertionError: expected [ '4', '5' ] to deeply equal [ '4', '21' ]`; `expected [ '17', '18' ] to deeply equal [ '17', '41' ]` (the field kept the first mark's burst value) | pass | `capture-page.behavior.test.ts:2412`, `:2437` |
| AC-85.6 off-label drag (A-3) | `AssertionError: expected [ '3' ] to deeply equal [ '23' ]` (moves off the label were ignored) | pass | `capture-page.behavior.test.ts:2214` |
| AC-57.5 (TA-4) | fails until row 3 with the new tests (the handle does not exist yet) | pass | `capture-page.behavior.test.ts:1262` |
| AC-85.10 | `Error: expect(received).toBe(expected)`, expected 1, received 0 (handle count, `ELECTRON_RED`); the `RENDERER_PIN` assertion before it passed | pass (1.6s) | `ui/tests/e2e/capture-inbox.test.ts:2331` |
| AC-85.11 | `AssertionError: expected 'Arrow, Box, Highlight, and Text draw …' to contain 'Drag the Stroke or Size label, or use…'` | pass | `ui/tests/unit/capture-help-content.test.ts:55` |

The Red run had 13 failed unit tests in 3 files, and `red-check.py` reported 2 receipts and 0 problems. Every Red and Green receipt is in [walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-editor-options/walkthrough.md) §MEU-85 Red and §MEU-85 Green, with its decisive lines. The same sections list the setup corrections made after Red; none of them weakened an assertion:
- the AC-85.10 handle count moved to after the box is drawn;
- `rectStrokes` sorts the rects by `x`;
- AC-85.12 (d) reselects the mark after Undo;
- `scrubDrag` rounds the handle centre to whole pixels.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s37-85-red","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 2 command, verbatim","cwd":"P:/av-kit-wt/s37-capture-editor-options","scope":"MEU-85 Red: Vitest (capture-scrub, capture-page.behavior AC-85.6-85.9 and AC-85.12, TA-4, capture-help-content AC-85.11), Electron AC-85.10, red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"base 90bb409 plus the row 2 tests (ui/src unchanged; guard clean)","output":"Vitest 3 files failed, Tests 13 failed | 93 skipped | Electron AC-85.10 failed: expected 1, received 0 | red-check: 2 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s37-85-green","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 3 command, verbatim","cwd":"P:/av-kit-wt/s37-capture-editor-options","scope":"MEU-85 Green: typecheck, targeted Vitest (8 files), build, Electron capture-inbox","phase":"green","exit_code":0,"result":"pass","tested_state":"base 90bb409 plus the MEU-85 product change (ui/src sha256 4c44299b1b304af4492af770f77e2ea353e3d6f6c3f1bb39b67e2a3f9d346629)","output":"tsc clean | Test Files 8 passed, Tests 164 passed | built | Electron capture-inbox 35 passed","fresh":true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-85-a3-red", "command": "cd ui; npx vitest run tests/unit/capture-page.behavior.test.ts -t \"leaves the label\" *> C:/Temp/av-kit/s37-a3-red.txt", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "A-3 Red: the new AC-85.6 off-label drag test against the pre-A-3 CaptureScrubField", "phase": "red", "exit_code": 1, "result": "fail", "tested_state": "H1-2 run 1 tree (tested_state 90bb409+3dab0639…87a3) plus the new test only", "output": "× AC-85.6 a drag that leaves the label without pointer capture keeps scrubbing and is one undo step | AssertionError: expected [ '3' ] to deeply equal [ '23' ] | Tests 1 failed | 110 skipped", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-85-a3-green", "command": "cd ui; npx vitest run tests/unit/capture-page.behavior.test.ts tests/unit/capture-scrub.test.ts; npx tsc --noEmit -p tsconfig.json; npx eslint src/renderer/src/features/capture/CaptureScrubField.tsx tests/unit/capture-page.behavior.test.ts", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "A-3 Green: SCRUB_DRAG_WINDOW in CaptureScrubField.tsx", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "H1-2 run 1 tree plus the A-3 test and fix", "output": "Test Files 2 passed (2) | Tests 123 passed (123) | tsc exit 0 | eslint exit 0", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-85-a3-probe-prefix", "command": "npm run build; npx playwright test <temporary probe spec, deleted> --grep S37PROBE (pre-A-3 CaptureScrubField swapped in; Element.prototype.setPointerCapture throws)", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "A-3 cause: the AC-85.10 drag in Electron with pointer capture refused, against the pre-A-3 field", "phase": "runtime", "exit_code": 1, "result": "fail", "tested_state": "pre-A-3 CaptureScrubField behaviour (handle-bound move/up), temporary probe; the fixed file was restored and rebuilt after", "output": "Expected: \"23\" | Received: \"8\" | 1 failed (the H1-2 run 1 e2e-repeat signature)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-85-a3-probe-fixed", "command": "npm run build; npx playwright test <temporary probe spec, deleted> --grep S37PROBE --repeat-each=5 (Element.prototype.setPointerCapture throws)", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "A-3 fix: the same drag with capture refused, against SCRUB_DRAG_WINDOW; then mouse.up, a later move and one Undo", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "H1-2 run 1 tree plus the A-3 test and fix", "output": "+40 px gives 23, commit gives field 23, a move after mouse.up leaves 23, one Undo gives 3 | 5 passed (46.2s)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-85-r1-red", "command": "cd ui; npx vitest run tests/unit/capture-page.behavior.test.ts -t \"AC-85.3 an invalid|AC-85.4 an invalid|AC-85.12 \\(b\\)\" *> C:/Temp/av-kit/s37-F12-red.txt", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "Execution review round 1 F1 and F2 Red: the four new regressions with CaptureViewport's pre-fix wiring restored (fallback 3 and 16, no resetKey); the unwired resetKey prop and page epoch were present and inert", "phase": "red", "exit_code": 1, "result": "fail", "tested_state": "H1-2 run 3 tree (90bb409+7f784552…24dc) plus the four tests", "output": "Tests 4 failed | 1 passed | 110 skipped (115) | AC-85.3 expected [ '4' ] to deeply equal [ '21' ] | AC-85.4 expected [ '17' ] to deeply equal [ '41' ] | AC-85.12 (b) boxes expected [ '4', '5' ] to deeply equal [ '4', '21' ] | AC-85.12 (b) texts expected [ '17', '18' ] to deeply equal [ '17', '41' ] | the passing test is the existing pointer-path (b)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s37-85-r1-green", "command": "cd ui; npx vitest run (same filter) *> C:/Temp/av-kit/s37-F12-green.txt; npm run typecheck; npm run lint; npx vitest run tests/unit/capture-page.behavior.test.ts tests/unit/capture-page.test.ts tests/unit/capture-scrub.test.ts tests/unit/capture-action-row.test.ts tests/unit/capture-toolbar.test.ts *> C:/Temp/av-kit/s37-F12-unit.txt", "cwd": "P:/av-kit-wt/s37-capture-editor-options", "scope": "Execution review round 1 F1 and F2 Green: SCRUB_BASE fallback from the selected mark; resetKey from the page's per-field sizeEpoch and the selection", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "the corrected tree, before the fresh gate", "output": "Tests 5 passed | 110 skipped (115) | typecheck exit 0 | lint (--max-warnings 0) exit 0 | Test Files 5 passed (5), Tests 180 passed (180)", "fresh": true}
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
| `ui/src/renderer/src/features/capture/capture-scrub.ts` | new | `SCRUB_MATH`; `parsePositiveInt` moved here unchanged |
| `ui/src/renderer/src/features/capture/CaptureScrubField.tsx` | new | `SCRUB_FIELD`, `SCRUB_GESTURES`, `SCRUB_ALT_GUARD`; `SCRUB_DRAG_WINDOW` (A-3): the drag follows window pointer events, so it keeps scrubbing if capture never takes effect; `resetKey` (R1-F2): a new key drops the field's own wheel or key burst without a callback |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | Stroke and Size fields through `CaptureScrubField` (`SIZE_LABELS`); preview, commit and cancel props; `fallback` is the applicable selected mark's size (R1-F1); `resetKey` is the field's epoch plus the selected index (R1-F2) |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | `SIZE_BURST`: `sizeBurstRef`, `previewSize`, `finishSize`, `cancelSize`, the finish-first calls, the Escape branch, `canUndo`/`canRedo` gated on `txOpen`, the reset effects clear the burst; `sizeEpoch`, bumped per field by `finishSize` and `cancelSize` (R1-F2) |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | scrub sentence |
| `ui/tests/unit/capture-scrub.test.ts` | new | AC-85.1 to AC-85.5 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-85.6 to AC-85.9, AC-85.12; TA-4; the A-3 off-label drag test; the R1-F1 and R1-F2 regressions |
| `ui/tests/unit/capture-help-content.test.ts` | modified | AC-85.11 |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | AC-85.10 |
| `ui/tests/e2e/test-ids.ts` | modified | TA-3 tail block (`CAPTURE_STROKE_SCRUB`, `CAPTURE_FONT_SIZE_SCRUB`; A-1) |

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

Execution review round 1 (Codex `gpt-6.1-sol`, `changes_required`, [canonical review](2026-10-16-capture-editor-options-implementation-critical-review.md)) found two blocking defects, both in MEU-85. Both were confirmed by Red before the fix.

| Finding | Confirmed | Correction |
|---|---|---|
| F1 (High) AC-85.3/AC-85.4 `SCRUB_BASE`: the viewport always passed `fallback` 3 and 16, so invalid field text scrubbed a stroke-20 box to 4 and a size-40 text to 17 | yes: Red `expected [ '4' ] to deeply equal [ '21' ]`, `expected [ '17' ] to deeply equal [ '41' ]` | `CaptureViewport.tsx` passes the applicable selected mark's `stroke_width` (arrow or box) or `font_size` (text), else 3 and 16. Tests `capture-page.behavior.test.ts:2290`, `:2310` |
| F2 (High) AC-85.12 (b): the field kept its own burst value after the page finished the burst, so keyboard-selecting a stroke-20 mark between notches scrubbed it from the first mark's 4 to 5 | yes: Red `expected [ '4', '5' ] to deeply equal [ '4', '21' ]`; the two-text variant `expected [ '17', '18' ]` | An explicit boundary: `CapturePage.tsx` bumps a per-field `sizeEpoch` in `finishSize` and `cancelSize`; `CaptureViewport.tsx` passes that epoch plus the selected index as `resetKey`; `CaptureScrubField.tsx` clears its wheel timer, accumulator, key and burst value on a new key, with no callback and without ending a drag. Per-field, so the field that is driving is not reset when `previewSize` finishes the other field's burst. Tests `:2412`, `:2437` |

The two F1 tests focus the input before the key events, as a real keypress would; unfocused, the page's window key handler read ArrowUp as a nudge of the selected box. The round 1 E4 note was also applied: walkthrough §Gate A-3 now says the 97 are scrub observations, and that the loaded run's suite reported 39 passed and 1 timeout. The fresh full gate is H1-2 run 4 (Quality Gate Results).

## Deferred Items

None.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-85 handoff after the row 8 gate |
| Amended | 2026-10-16 | claude-code-local (Claude Opus 5.5) | A-3 (S6, Mat chose option 1): H1-2 run 1 failed AC-85.10 once; `SCRUB_DRAG_WINDOW` fix, unit test and probes; H1-2 re-run |
| Corrected | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Execution review round 1 F1 and F2: `SCRUB_BASE` fallback from the selected mark; `resetKey` boundary; four regressions; H1-2 run 4 |
