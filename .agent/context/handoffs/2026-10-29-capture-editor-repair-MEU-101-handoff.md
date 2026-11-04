---
date: "2026-11-03"
project: "capture-editor-repair"
meu: "MEU-101"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-10-29-capture-editor-repair-MEU-100-handoff.md"
---

# Handoff: 2026-10-29-capture-editor-repair-MEU-101-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-101, `gui-capture-text-reedit`. A committed text mark can be edited again by double-click or Enter, and scaled by its plate corners.
**Build Plan Section**: [09 §Text re-edit and scaling](../../../docs/build-plan/09-screenshot-capture.md#text-re-edit-and-scaling).
**Predecessor**: [MEU-100 handoff](2026-10-29-capture-editor-repair-MEU-100-handoff.md). The [MEU-99 handoff](2026-10-29-capture-editor-repair-MEU-99-handoff.md) is the plan's first MEU.

Before this MEU, a committed text mark could be neither edited nor scaled: the text draft only created marks (`onTextCommit`).

- **`TEXT_REEDIT`.** `TextDraft` gains `editIndex`, and `SurfacePointer.phase` gains `'dblclick'`, emitted by the surface's `onDoubleClick`. A select-tool double-click on a text body, or plain Enter on a selected text mark (prevented), opens the draft with the mark's text. While it is open the viewport paints neither the mark nor its handles, and Undo, Redo and mark removal are inert so the index cannot drift. Commit replaces only `text` in place as one history step; an empty or unchanged draft and Escape record nothing, and an unchanged draft is not dirty.
- **`TEXT_SCALE`.** `capture-transform.ts` adds `textPlateHandlePoints` (the four corners of `textBackgroundBox`) and `scaleTextMark`: `ratio` is the larger of the pointer's distances from the anchor corner over the plate's width and height, `font_size` is clamped to 1..`FONT_SCRUB_MAX` (400), and `x`/`y` shift so the anchor corner stays within 1 px. `x`/`y` are not clamped, since text origins are signed integers (review round 1 F2).
- **Text branch of `HIT_ORDER`, `RESIZE_GESTURE` and `RESIZE_HANDLES`.** A selected text mark has four corner handles (no edge handles); a corner drag routes to `scaleTextMark` through the same threshold, preview and history.
- **`HELP_TEXT`.** The MEU-101 sentence follows the MEU-100 one.

This handoff also carries the session's gate attempts 1 to 3 and the two session-wide rulings they needed (D-175, D-176), because they landed after MEU-101's Green.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md) §MEU-101. **Execution authorization:** `USER_EXPLICIT`, 2026-10-29, "all recommendations are accepted, continue with @.agent/workflows/create-plan.md and execution upon review approval.", met by the round 2 plan approval ([walkthrough.md](../../../docs/execution/plans/2026-10-29-capture-editor-repair/walkthrough.md) §Execution message, D-161).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-101.1 | unit | `TEXT_SCALE` maths: four plate corners and no edge keys; `se` at 2× gives `font_size` 32 with `nw` fixed; onto the anchor gives 1, far gives 400; only `x`, `y`, `font_size` change; the image-edge case `{x:10,y:-6,font_size:32}`; each corner keeps its anchor near an image corner | 09 "Scale"; D-170 | `capture-transform.test.ts` `AC-101.1 …` | ✅ |
| AC-101.2 | unit | Double-click opens the draft with `Hello`, hides the mark and its handles; `Bye` + Enter replaces only the text as one step; one Undo restores `Hello` | 09 "Re-edit", "Commit"; D-169 | `capture-page.behavior.test.ts` `AC-101.2 …` | ✅ |
| AC-101.3 | unit | Enter opens the draft (prevented); unchanged, Escape and emptied values record nothing; Enter on a rect does nothing; an unchanged draft is not dirty | 09 "Commit"; D-169 | `capture-page.behavior.test.ts` `AC-101.3 …` | ✅ |
| AC-101.4 | unit | Corner scale: exactly 4 handles on a selected text mark; an `se` drag raises `font_size` in one step; the plate's `n` edge midpoint is no `resize` hit; after the scale the Size field shows the new `font_size` and ArrowUp steps from it (review F1, EC-11) | 09 "Scale"; synthesis C-3 | `capture-page.behavior.test.ts` `AC-101.4 …`, including `AC-101.4 after a corner scale … [review F1]` | ✅ |
| AC-101.5 | unit | Help: `<MEU-100 sentence> + ' ' + <MEU-101 sentence>`, body still ends with `RANGE_HELP_SENTENCE` | `HELP_TEXT` | `capture-help-content.test.ts` `AC-101.5 …` | ✅ |
| AC-101.6 | integration | Electron: double-click `Note` shows the draft, `Done` + Enter, Save posts `Done` at (3,6) size 2; a plate corner drag then posts a `font_size` above 2 (the `nw` corner, EC-6) | 09 "Tests" | `capture-inbox.test.ts` `AC-101.6 …` | ✅ |
| AC-99 (cross-ref) | — | Owned by the MEU-99 handoff (chords, focus, hints and help for undo/redo) | plan §MEU-99 | [MEU-99 handoff](2026-10-29-capture-editor-repair-MEU-99-handoff.md) | see MEU-99 |
| AC-100 (cross-ref) | — | Owned by the MEU-100 handoff (resize handles, maths, gesture and cursor) | plan §MEU-100 | [MEU-100 handoff](2026-10-29-capture-editor-repair-MEU-100-handoff.md) | see MEU-100 |
| AC-23 (cross-ref) | regression | AC-23.18 GUI actions audit reads `gui-actions-index.md`, whose `capture:undo`/`capture:redo` Trigger cells row 9 changed (`INDEX_TRIGGER`) | `INDEX_TRIGGER` | `ui/tests/unit/gui-actions-audit.test.ts` (gate `ui-tests`) | ✅ |
| AC-97 (cross-ref) | regression | AC-97.5 (the audit's bound-chord rows) and AC-97.8 (Capture's Ctrl+S save seam) hold beside the page's new history chords | plan §MEU-99 Boundary Inventory | `gui-actions-audit.test.ts` (gate `ui-tests`); `ui/tests/e2e/capture-inbox.test.ts` AC-97.8 (gate `ui-electron`) | ✅ |
| AC-60 (cross-ref) | regression | AC-60.3 hit test (no resize hit without a selection; text plate centre stays body); AC-60.4/5/6 move and arrow-endpoint gestures unchanged by `HIT_ORDER` | `HIT_ORDER`; `CENSUS_PATTERNS` | `ui/tests/unit/capture-hit-test.test.ts`, `capture-page.behavior.test.ts` (gate `ui-tests`) | ✅ |
| AC-65 (cross-ref) | regression | TA-2 amends AC-65.2: the Undo/Redo focused hints compare against `HINT_OVERRIDE[id] ?? name`; `aria-label` stays the name | `TEST_AMENDMENTS` TA-2 | `capture-page.behavior.test.ts` (gate `ui-tests`) | ✅ |
| AC-66 (cross-ref) | regression | AC-66.13: the renderer's `preventDefault` still suppresses the default Edit menu accelerator, which `HISTORY_CHORDS` relies on (D-163) | plan §MEU-99 Boundary Inventory | `capture-inbox.test.ts` AC-66.13 (gate `ui-electron`) | ✅ |
| AC-80 (cross-ref) | regression | TA-3 amends AC-80.8 (`HINT_OVERRIDE`, D-177); TA-1 amends the AC-80.10 line (`capture-inbox.test.ts:1680`, `Undo (Ctrl+Z)`) | `TEST_AMENDMENTS` TA-1, TA-3 | `ui/tests/unit/icon-hints.test.ts` (gate `ui-tests`); `capture-inbox.test.ts` AC-80.10 (gate `ui-electron`) | ✅ |
| AC-82 (cross-ref) | regression | AC-82.6: the text plate is still `textBackgroundBox`, the box `TEXT_SCALE` and the text handles use | `TEXT_SCALE` | `capture-inbox.test.ts` AC-82.6 (gate `ui-electron`) | ✅ |
| AC-87 (cross-ref) | regression | AC-87.6 (a §Baseline-set Electron flake) passed in the H1-2 run | §Verification Plan baseline rule | `capture-inbox.test.ts` AC-87.6 (gate `ui-electron`) | ✅ |
| AC-89 (cross-ref) | regression | AC-89.8: the Capture help body still ends with `RANGE_HELP_SENTENCE` after the three `HELP_TEXT` sentences | `HELP_TEXT` | `ui/tests/unit/capture-help-content.test.ts` (gate `ui-tests`) | ✅ |
| AC-90 (cross-ref) | regression | AC-90.10: with `selectedIndex` null no handle exists, so hits are unchanged | `HIT_ORDER` | `capture-hit-test.test.ts`, `capture-page.behavior.test.ts` (gate `ui-tests`) | ✅ |
| AC-91 (cross-ref) | regression | AC-91.9: the same `selectedIndex: null` rule for the new marks' hits | `HIT_ORDER` | `capture-hit-test.test.ts`, `capture-page.behavior.test.ts` (gate `ui-tests`) | ✅ |
| AC-24, AC-25 (cross-ref) | regression | Packaging tests in the gate's `py-tests`. AC-25.7 fails at baseline (`PACKAGING-MCP-SNIPPET-TOKEN-STALE`), so it is excused; AC-24.10 and AC-25.10 passed at baseline and are not excused | §Verification Plan baseline rule | `session-gate.ps1` `py-tests` | baseline rule |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-101.1 | `expected 'undefined' to be 'function'` (`textPlateHandlePoints` is new) | pass | `capture-transform.test.ts` |
| AC-101.2 | `the draft opens with the text: expected undefined to be 'Hello'` | pass | `capture-page.behavior.test.ts` |
| AC-101.3 | `Enter on a text mark is prevented: expected false to be true` | pass | `capture-page.behavior.test.ts` |
| AC-101.4 | `four corners: expected [] to deeply equal [ 'ne', 'nw', 'se', 'sw' ]` | pass | `capture-page.behavior.test.ts` |
| AC-101.5 | four-tools body does not contain `RESIZE_HELP_SENTENCE TEXT_EDIT_HELP_SENTENCE` | pass | `capture-help-content.test.ts` |
| AC-101.6 | `Error: expect(received).toBe(expected)`, Expected 1, Received 0 (`capture-text-draft` count after the double-click) | pass | `capture-inbox.test.ts` |
| AC-101.4 [review F1] (EC-11) | `AssertionError: Size after the scale: expected '2' to be '4'` | pass | `capture-page.behavior.test.ts:3244` |

Every receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-29-capture-editor-repair/walkthrough.md): §Baseline (row 0), §Census (row 1), §MEU-101 Red, §MEU-101 Green, §Gate (row 8), §Hub (row 9) and §Execution Correction Notes.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s43-101-red", "command": "pwsh -NoProfile -File row-6.ps1 (task.md row 6 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-101 Red: AC-101 Vitest, the row 5 tree check, build, Electron AC-101, red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1856df5 plus rows 1-5 and the row 6 tests; ui/src equal to row5-ui-src.json", "output": "Vitest 5 failed, every failure an AssertionError | ui/src changed since row 5: [] | Electron 1 failed: AC-101.6 Expected 1, Received 0 | red-check: 2 receipt(s), 6 required test(s), 0 problem(s) | row 6 exit=0", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-101-green-oom", "command": "pwsh -NoProfile -File row-7.ps1 (task.md row 7 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-101 Green, first attempt", "phase": "green", "exit_code": 1, "result": "blocked", "tested_state": "HEAD 1856df5 plus rows 1-6 and the MEU-101 implementation", "output": "a Vitest worker hit Fatal process out of memory before any test ran; about 0.5 GB commit free, held by other sessions' processes; rerun whole once memory came back", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-101-green", "command": "pwsh -NoProfile -File row-7.ps1 (task.md row 7 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-101 Green: the row 7 Vitest set, build, capture-inbox Electron spec whole", "phase": "green", "exit_code": 1, "result": "fail", "tested_state": "HEAD 1856df5 plus rows 1-6 and the MEU-101 implementation", "output": "Vitest 7 files, 203 passed | built, CapturePage chunk 168.51 kB | Electron (7.9m) 39 passed, 4 failed: AC-67.20 (:1463, order-dependent) and AC-87.6 (:2420) in the row 0 baseline set, W9-3 (:213) and W9-4 (:276) Test timeout of 60000ms exceeded; AC-101.6 passed", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-101-green-w9-rerun", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts --grep \"W9-3|W9-4\" --repeat-each=5 > C:/Temp/av-kit/s43-101-green-w9-rerun.txt 2>&1", "cwd": "P:/av-kit", "scope": "the two row 7 timeouts, five repeats", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1856df5 plus rows 1-6 and the MEU-101 implementation", "output": "10 passed (34.7s)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-gate-attempt1", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-29-capture-editor-repair/session-gate.ps1 *> C:/Temp/av-kit/s43-gate.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s43-gate.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE'; exit $code", "cwd": "P:/av-kit", "scope": "row 8 session gate, attempt 1", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "1856df5048af928ea74ce83393678c17534cb59b+ad1c9c2188df5fa222f77a4e9239dcebd60b131d8bb6f5322a5f44f518a993b9", "output": "identity-before through task-contract exit=0 | scope-paths exit=1: outside scope ['.agent/model-registry.local.json', '.claude/agents/av-kit-builder.md', '.claude/agents/av-kit-verifier.md', '.cursor/agents/av-kit-builder.md', '.cursor/agents/av-kit-verifier.md'], another writer's registry sync (S8, EC-7) | every later step not_run (receipt kept as s43-gate-attempt1.txt)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-gate-attempt2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-29-capture-editor-repair/session-gate.ps1 *> C:/Temp/av-kit/s43-gate.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s43-gate.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE'; exit $code", "cwd": "P:/av-kit", "scope": "row 8 session gate, attempt 2, after Mat committed the registry sync as 7706fcd (EC-7)", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+29ad39b8d5a0cacaaf607057d62c5598ceddf9f16d00714b40a6568fbfa8653e", "output": "scope-paths exit=0 (registry sync (EC-7) ok: True) | py-tests exit=1: 3 failed, 954 passed; AC-25.7 baseline plus two test_framework_adoption.py ids, REFUSE: uncensused model pin: .cursor/agents/av-kit-builder.md (D-175, EC-8) | every later step not_run (s43-gate-attempt2.txt)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-175-adoption", "command": "rtk proxy uv run pytest \"tests/tooling/test_framework_adoption.py::test_review_pipeline_governance_static_oracles\" \"tests/tooling/test_framework_adoption.py::test_governance_preservation_and_routing_inventory\" -q > C:/Temp/av-kit/s43-175-adoption.txt 2>&1", "cwd": "P:/av-kit", "scope": "the two adoption tests after the D-175 census entry", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "7706fcd plus the D-175 routing-census.md entry", "output": "10 passed in 14.18s", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-gate-attempt3", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-29-capture-editor-repair/session-gate.ps1 *> C:/Temp/av-kit/s43-gate.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s43-gate.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE'; exit $code", "cwd": "P:/av-kit", "scope": "row 8 session gate, attempt 3, after D-175", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+0ede1df5a9395d5b054e55567fd2d8d57f68f29e68cd0f3b4dc152025d5e874e", "output": "py-tests exit=1 by the baseline rule (1 failed, 956 passed; AC-25.7) | ui-tests exit=1: 35 failed, 1071 passed (1106); 34 TypeError: Cannot read properties of undefined (reading 'clear'|'getItem') on Node 26.13.0 (D-176, EC-9) and AC-80.8 expected 'Undo' (D-177, EC-10) | every later step not_run (s43-gate-attempt3.txt)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-ls-nowebstorage", "command": "$env:NODE_OPTIONS='--no-experimental-webstorage'; rtk proxy npm --prefix ui run test -- <the five storage test files> > C:/Temp/av-kit/s43-ls-nowebstorage.txt 2>&1", "cwd": "P:/av-kit", "scope": "D-176 probe: the five storage files with Node 26 webstorage off", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "7706fcd plus the attempt 3 tree", "output": "Test Files 5 passed (5), Tests 61 passed (61)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-ui-nowebstorage", "command": "$env:NODE_OPTIONS='--no-experimental-webstorage'; rtk proxy npm --prefix ui run test > C:/Temp/av-kit/s43-ui-nowebstorage.txt 2>&1", "cwd": "P:/av-kit", "scope": "D-176 probe: the whole UI unit suite with Node 26 webstorage off", "phase": "targeted", "exit_code": 1, "result": "fail", "tested_state": "7706fcd plus the attempt 3 tree", "output": "Test Files 1 failed | 106 passed (107), Tests 1 failed | 1105 passed (1106); the one failure is AC-80.8 (D-177)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-mcp-node26", "command": "rtk proxy npm --prefix mcp-server run build; rtk proxy npm --prefix mcp-server run test > C:/Temp/av-kit/s43-mcp-node26.txt 2>&1", "cwd": "P:/av-kit", "scope": "D-176 Node 26 impact review: the MCP build and suite", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "7706fcd plus the attempt 3 tree", "output": "Test Files 31 passed (31), Tests 446 passed (446)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-f1-red", "command": "cd ui; rtk proxy npx vitest run tests/unit/capture-page.behavior.test.ts -t \"review F1\" > C:/Temp/av-kit/s43-f1-red.txt 2>&1", "cwd": "P:/av-kit", "scope": "H1-7 round 1 F1 Red: the new Size-after-scale test before the fix (EC-11)", "phase": "red", "exit_code": 1, "result": "fail", "tested_state": "the H1-2 attempt 3 tree (7706fcd…+7c3a3dee…) plus the F1 test; CapturePage.tsx unchanged", "output": "Test Files 1 failed (1), Tests 1 failed | 134 skipped (135); AssertionError: Size after the scale: expected '2' to be '4'", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-f1-green", "command": "cd ui; rtk proxy npx vitest run tests/unit/capture-page.behavior.test.ts -t \"review F1\" > C:/Temp/av-kit/s43-f1-green.txt 2>&1", "cwd": "P:/av-kit", "scope": "H1-7 round 1 F1 Green: the same test after inspectMark(gesture.index) (EC-11)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "the F1 test plus the EC-11 inspectMark line in CapturePage.tsx", "output": "Test Files 1 passed (1), Tests 1 passed | 134 skipped (135)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-f1-vitest", "command": "cd ui; rtk proxy npx vitest run tests/unit/capture-transform.test.ts tests/unit/capture-hit-test.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/capture-help-content.test.ts tests/unit/icon-hints.test.ts > C:/Temp/av-kit/s43-f1-vitest.txt 2>&1; rtk proxy npm run typecheck > C:/Temp/av-kit/s43-f1-typecheck.txt 2>&1; rtk proxy npm run lint > C:/Temp/av-kit/s43-f1-lint.txt 2>&1", "cwd": "P:/av-kit", "scope": "the five Capture unit files, ui typecheck and ui lint after EC-11", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "the F1 test plus the EC-11 inspectMark line in CapturePage.tsx", "output": "Test Files 5 passed (5), Tests 164 passed (164) | typecheck exit=0 | lint exit=0", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-gate-h1-2-attempt1", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-29-capture-editor-repair/session-gate.ps1 *> C:/Temp/av-kit/s43-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s43-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 fresh full session gate, attempt 1 (receipts kept as s43-gate-h1-attempt1.txt and s43-h1-2-attempt1-ui-electron.txt)", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+7c3a3dee7ed2cc0b6fb41d60a4e7776a2d48c6a64d0bdbeffb3de7847705f543", "output": "identity-before through state-render exit=0 (py-tests by the baseline rule) | ui-electron exit=1: 178 passed, 3 failed (18.4m at 100% CPU from other processes), each Test timeout of 60000ms exceeded: command-palette-nav.spec.ts:31 and :40, console-chrome.test.ts:30 (C1-1) | e2e-repeat, identity-npm, identity-after not_run (fail-fast)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-h1-2-rerun-timeouts", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/command-palette-nav.spec.ts tests/e2e/console-chrome.test.ts --repeat-each=3 > C:/Temp/av-kit/s43-h1-2-rerun-timeouts.txt 2>&1", "cwd": "P:/av-kit", "scope": "the two specs holding the H1-2 attempt 1 timeouts, three repeats, on the same tree", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+7c3a3dee7ed2cc0b6fb41d60a4e7776a2d48c6a64d0bdbeffb3de7847705f543", "output": "39 passed (5.0m)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-gate-h1-2-attempt2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-29-capture-editor-repair/session-gate.ps1 *> C:/Temp/av-kit/s43-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s43-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 fresh full session gate, attempt 2 (receipts kept as s43-gate-h1-attempt2.txt and s43-h1-2-attempt2-ui-electron.txt)", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+7c3a3dee7ed2cc0b6fb41d60a4e7776a2d48c6a64d0bdbeffb3de7847705f543", "output": "identity-before through state-render exit=0 (py-tests by the baseline rule) | ui-electron exit=1: 178 passed, 3 failed (22.0m, CPU still loaded by other processes): capture-inbox.test.ts:2615 AC-90.12 and transcript-queue.test.ts:268 W2-4 Test timeout of 60000ms exceeded, convert-queue.test.ts:1584 AC-97.7 toHaveCount(1) Received 0 after its 5000ms expect timeout | e2e-repeat, identity-npm, identity-after not_run (fail-fast)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-h1-2-rerun2-timeouts", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts tests/e2e/convert-queue.test.ts tests/e2e/transcript-queue.test.ts --grep 'AC-90.12|AC-97.7|W2-4' --repeat-each=3 > C:/Temp/av-kit/s43-h1-2-rerun2-timeouts.txt 2>&1", "cwd": "P:/av-kit", "scope": "the three H1-2 attempt 2 failures, three repeats, on the same tree, CPU back to about 10%", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+7c3a3dee7ed2cc0b6fb41d60a4e7776a2d48c6a64d0bdbeffb3de7847705f543", "output": "9 passed (19.5s)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-29-capture-editor-repair/session-gate.ps1 *> C:/Temp/av-kit/s43-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s43-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 fresh full session gate after row 9 and the H1-7 round 1 fix (EC-11) (INPUT_IDENTITY): static, py/ui/mcp tests, builds, openapi, state-render, ui-electron, e2e-repeat, identity before/npm/after", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+bc2de358fe30b9c57b19eb63aaee171de3024f053f4c8bb0d59ecfda392a6dc0", "output": "identity-before exit=0 | py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract, scope-paths exit=0 (changed paths: 50 outside scope: []) | py-tests baseline rule: failed=1 outside_baseline=[] errors=0 (956 passed) | ui-tests Test Files 107 passed (107), Tests 1107 passed (1107) | mcp-build exit=0 | mcp-tests Test Files 31 passed (31), Tests 446 passed (446) | ui-build, ui-harness-build, ui-picker-stub, openapi exit=0 | state-render Drift check passed | ui-electron 181 passed (4.9m) | e2e-repeat 30 passed (59.1s) | identity-npm, identity-after exit=0 | tested_state before=7706fcde2cb6eef547c3b4243857afeace68f24c+bc2de358fe30b9c57b19eb63aaee171de3024f053f4c8bb0d59ecfda392a6dc0 after=7706fcde2cb6eef547c3b4243857afeace68f24c+bc2de358fe30b9c57b19eb63aaee171de3024f053f4c8bb0d59ecfda392a6dc0 | session-gate: all steps exit 0 (H1-2 attempt 4, after EC-11)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code", "cwd": "P:/av-kit", "scope": "H1-3 SSOT render check after row 9's status writes, re-run after the EC-11 gate", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+bc2de358fe30b9c57b19eb63aaee171de3024f053f4c8bb0d59ecfda392a6dc0", "output": "Drift check passed — SSOT loaded (107 MEUs, 12 phases), rendered regions match on-disk content", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-h1-4-openapi", "command": "rtk proxy uv run python -c \"import json,pathlib,subprocess,sys; b=pathlib.Path('docs/execution/plans/2026-10-29-capture-editor-repair/baseline.sha').read_text().strip(); old=json.loads(subprocess.run(['git','show',b+':openapi.committed.json'],capture_output=True,text=True,check=True).stdout)['components']['schemas']; new=json.loads(pathlib.Path('openapi.committed.json').read_text(encoding='utf-8'))['components']['schemas']; added=sorted(set(new)-set(old)); removed=sorted(set(old)-set(new)); changed=sorted(k for k in set(old)&set(new) if old[k]!=new[k]); print('added:',added,'removed:',removed,'changed:',changed); sys.exit(0 if not added and not removed and not changed else 1)\" *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt,C:/Temp/av-kit/s43-D6-openapi.txt; exit $code", "cwd": "P:/av-kit", "scope": "H1-4 OpenAPI: committed schemas against baseline.sha, plus the H1-2 openapi receipt, re-run after the EC-11 gate", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "7706fcde2cb6eef547c3b4243857afeace68f24c+bc2de358fe30b9c57b19eb63aaee171de3024f053f4c8bb0d59ecfda392a6dc0", "output": "added: [] removed: [] changed: [] | H1-2 openapi stage=full exit=0", "fresh": true}
```

### Quality Gate Results

The H1-2 fresh gate is the session's full record. Row 9 changed bound inputs after row 8, and the H1-7 round 1 fix (EC-11) changed them again, so the record is the H1-2 run on the fixed tree (`INPUT_IDENTITY`). Every step exited 0 except py-tests, which exited 1 as the plan's baseline rule allows: its one failure is the row 0 baseline AC-25.7 (`PACKAGING-MCP-SNIPPET-TOKEN-STALE`, `outside_baseline=[]`). The other step counts:

- ui Vitest: 107 files, 1107 passed on Node 26.13.0, with the D-176 worker flag.
- MCP Vitest: 31 files, 446 passed.
- Electron: 181 passed (4.9m); the e2e repeat (`--repeat-each=10` over AC-99, AC-100 and AC-101): 30 passed (59.1s).
- `scope-paths`: 50 changed paths, none outside scope.
- `state-render`: drift check passed.
- Identity: `tested_state` `7706fcde2cb6eef547c3b4243857afeace68f24c+bc2de358fe30b9c57b19eb63aaee171de3024f053f4c8bb0d59ecfda392a6dc0` was the same before and after.

H1-2 ran four times, and only `ui-electron` ever failed. Attempts 1 to 3 ran on the round 0 tree (`7706fcd…+7c3a3dee…`). Attempt 1 hit three 60 s timeouts in the palette and console specs, which no MEU touched, with the CPU at 100% from other processes; the run took 18.4 minutes, against 4.8 in row 8 attempt 4. Attempt 2, still under load (22.0 minutes), failed three other tests the same way: AC-90.12, W2-4 and AC-97.7's 5 s expect. Each set then passed alone (39 of 39, then 9 of 9), and attempt 3 passed whole once the CPU was back near 10% (every step exit 0, Electron 181 passed (4.1m), receipt `s43-gate-h1-attempt3.txt`). The H1-7 round 1 fix (EC-11, MEU-101) then changed `CapturePage.tsx` and its behaviour test, so attempt 3 is kept as prose, not as a full record. The record above is attempt 4, on the fixed tree.

Row 8 attempt 4 passed whole on the pre-row-9 tree (state `7706fcd…+40f1f572…`). It is kept as prose, not as a full record, because row 9 then changed bound inputs. Attempts 1 to 3 failed and are recorded in the MEU-101 handoff (EC-7 to EC-10, D-175 to D-177). H1-3: render check exit 0. H1-4: no OpenAPI schema added, removed or changed.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/capture/capture-transform.ts` | modified | `TEXT_SCALE` (`textPlateHandlePoints`, `scaleTextMark`) |
| `ui/src/renderer/src/features/capture/capture-hit-test.ts` | modified | text plate corners in `HIT_ORDER` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | `TEXT_REEDIT` open and commit; the text branch of `RESIZE_GESTURE`; history and removal inert while an edit draft is open; `inspectMark(gesture.index)` after a gesture commit, so Size follows a corner scale (EC-11, review F1) |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | `TextDraft.editIndex`, `dblclick`, the hidden edited mark, text handles |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | MEU-101 sentence |
| `ui/tests/unit/capture-transform.test.ts` | modified | AC-101.1 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-101.2 to AC-101.4, plus the review F1 Size-after-scale test |
| `ui/tests/unit/capture-help-content.test.ts` | modified | AC-101.5 |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | AC-101.6 |
| `docs/execution/plans/2026-09-26-framework-update-adoption/routing-census.md` | modified | D-175: one appended `matches` entry for `.cursor/agents/av-kit-builder.md` line 4 (+7 lines); session-wide, its own `chore(registry)` commit |
| `ui/vitest.config.ts` | modified | D-176: `test.poolOptions.forks.execArgv: ['--no-experimental-webstorage']` with its comment (+4 lines); session-wide, its own `chore(test)` commit |

```diff
+            const editIndex = textDraft.editIndex
+            if (editIndex !== undefined) {
+              // TEXT_REEDIT: the new text replaces the mark's in place as one step; every other field stays.
+              const mark = annotationsRef.current[editIndex]
+              setTextDraft(null)
+              if (mark?.type === 'text') {
+                const list = replaceAt(annotationsRef.current, editIndex, { ...mark, text: textDraft.value })
+                applyHistory(list)
+                commitSelection(editIndex, list)
+              }
+              return
+            }
```

All three MEUs share the plan folder and the hub files in the plan's §Hub and state files table (rows 1 and 9, H1-3 and H2): the three 09 Delivered notes, the 06 `RESERVED_NOTE` note, the `gui-actions-index.md` Trigger cells (`INDEX_TRIGGER`), `meu-status.yaml` and the rendered `BUILD_PLAN.md`, `build-priority-matrix.md` and `meu-registry.md`. Two session-wide test-infrastructure files are not MEU product: `docs/execution/plans/2026-09-26-framework-update-adoption/routing-census.md` (D-175, EC-8) and `ui/vitest.config.ts` (D-176, EC-9). Both are in the MEU-101 handoff, and the H2 commit draft gives each its own commit ahead of the Session 43 commits.

---

## Codex Validation Report

Round 1 (2026-11-03): `changes_required`, one blocking finding (F1, MEU-101), recorded in `2026-10-29-capture-editor-repair-implementation-critical-review.md`. F1 was fixed as EC-11 and H1-2 re-ran on the fixed tree. Round 2 is pending.

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| F1 | High | After a text corner scale the Size inspector kept the old `font_size`, so ArrowUp from it shrank the mark (AC-101.4) | `CapturePage.tsx` gesture commit | Re-inspect the mark after the commit and add a regression | fixed (EC-11): `inspectMark(gesture.index)` after the commit; Red `expected '2' to be '4'`, then Green; H1-2 re-ran |

### Verdict

_pending: H1-7 Codex execution review, round 2_

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Drop the D-176 worker flag with the Vitest 5 upgrade, which fixes Node 26's `localStorage` global ([vitest#10867](https://github.com/vitest-dev/vitest/issues/10867)); a Vitest 4+ upgrade must move the key, since Vitest 4 removed `poolOptions` | follow-up | — (no MEU yet; D-176 authorizes no `known-issues.yaml` entry) | D-176 |
| Side handles and wrap width on text | deferred | MEU-102 | plan §Out of Scope; synthesis C-3 |


---

## Decision Log

```yaml
decision_log:
  - id: D-175
    stage: execution
    question: "Gate attempt 2 failed two test_framework_adoption.py tests on 7706fcd's uncensused builder pin (.cursor/agents/av-kit-builder.md line 4, sha a559daa5...). How is it fixed?"
    resolution: human
    class: externally-blocked
    chosen: "Census the pin: one appended routing-census.md matches entry for the builder's line 4 with the verifier's fields, the path in the scope-paths allow-list and the Hub table (EC-8), and its own chore(registry) commit ahead of the S43 commits"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-10-02-capture-flatten-backup/human-gate-decision.md A-14 - a pin change updated the census hashes, classification unchanged", "docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md A-2 - stale adoption records rebound field by field"]
    research: { engine: web, sources: ["https://tessl.io/registry/testland/golden-file-conventions/files", "https://tessl.io/registry/testland/flaky-test-quarantine", "https://cwiki.apache.org/confluence/display/KAFKA/KIP-1090+Flaky+Test+Management"] }
    reasoning: "Mat ruled 'D-175 census' on 2026-11-03. The census already accepts that line hash for the sibling verifier file, so the entry is the narrowest fix and explains the change that caused it; excusing the ids would pass a deterministic regression. The two tests then gave 10 passed."
  - id: D-176
    stage: execution
    question: "Gate attempt 3 failed 34 UI unit tests because WinGet moved Node from 24 to 26.13.0 after the baseline and Node 26's own localStorage global hides jsdom's. Where is it fixed?"
    resolution: human
    class: source-conflict
    chosen: "In the suite: ui/vitest.config.ts gains test.poolOptions.forks.execArgv ['--no-experimental-webstorage'] with a comment naming the Vitest 5 fix; the path joins the allow-list and Hub table (EC-9); its own chore(test) commit"
    source_tag: Human-approved
    precedents: ["Session 26 A17 (2026-09-28-p11-capture-settings walkthrough) - environment drift fixed at its cause", "D-175 - an out-of-scope fix ships as its own commit"]
    research: { engine: web, sources: ["https://github.com/vitest-dev/vitest/issues/10867", "https://nodejs.org/en/blog/release/v26.0.0", "https://electronjs.org/blog/electron-42-0"] }
    reasoning: "Mat ruled 'D-176: recommendation accepted' on 2026-11-03 after a Node 26 impact review, which found only the UI unit suite affected (MCP 446 passed on Node 26; Electron bundles Node 24). The flag repairs npm --prefix ui run test for every session, keeps the gate's D6 commands as written, and is removed by deleting one line."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-03 | claude-code-local (Claude Opus 5.5) | Initial MEU-101 handoff after H1-2 |
| Updated | 2026-11-03 | claude-code-local (Claude Opus 5.5) | H1-7 round 1 (`changes_required`, F1 in MEU-101) fixed as EC-11; H1-2, H1-3 and H1-4 re-ran on the fixed tree |
