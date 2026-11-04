---
date: "2026-11-03"
project: "capture-editor-repair"
meu: "MEU-99"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-10-29-capture-editor-repair-MEU-99-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-99, `gui-capture-history-chords`. Ctrl+Z undoes and Ctrl+Y or Ctrl+Shift+Z redo on the Capture canvas, through the same functions as the Undo and Redo buttons.
**Build Plan Section**: [09 §Canvas history chords](../../../docs/build-plan/09-screenshot-capture.md#canvas-history-chords).
**Predecessor**: none. The [MEU-100 handoff](2026-10-29-capture-editor-repair-MEU-100-handoff.md) and the [MEU-101 handoff](2026-10-29-capture-editor-repair-MEU-101-handoff.md) are the same plan's other MEUs.

Before this MEU, Ctrl+Z did nothing on the Capture canvas. Capture keeps its own history (`applyHistory`), and Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z are in `RESERVED_CHORDS`, so neither the registry nor the page bound them; the default Edit menu's undo role targeted the focused web contents.

- **`HISTORY_ACTIONS`.** The inline Undo and Redo handlers became two page functions, `undo` and `redo`, which the buttons and the chords share.
- **`HISTORY_CHORDS`.** `handleEditorKey` maps Ctrl/Meta+Z to undo and Ctrl/Meta+Y and Ctrl/Meta+Shift+Z to redo; Alt opts out and `isComposing` is ignored. It acts only while `HISTORY_FOCUS` holds (the image, the page body or a Capture editor button). Outside it the key stays the field's or the menu's and is not prevented. A size transaction or a live pointer gesture swallows the chord (prevented, no change) until it ends.
- **`HISTORY_HINTS`.** `capture-undo` and `capture-redo` carry `aria-keyshortcuts` (`Control+Z`, `Control+Y`) and the focused hints `Undo (Ctrl+Z)` and `Redo (Ctrl+Y)`; the `aria-label` stays the name.
- **`RESERVED_NOTE`.** A two-line comment in `registry/shortcuts.ts`: Capture handles the chords itself while its image has focus (D-163), and they stay reserved. The `RESERVED_CHORDS` set is unchanged.
- **`INDEX_TRIGGER` and the 06 note** (row 9): the actions index and 06 say where the chords live.
- **`HELP_TEXT`.** The Capture help body gains the MEU-99 sentence after `HELP_EDIT_SENTENCE`.
- **`TEST_AMENDMENTS`.** TA-1 (`capture-inbox.test.ts:1680`) and TA-2 (AC-65.2) as planned; TA-3 (AC-80.8, `icon-hints.test.ts`) after the gate found a census miss (D-177, EC-10).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-29-capture-editor-repair/implementation-plan.md) §MEU-99. **Execution authorization:** `USER_EXPLICIT`, 2026-10-29, "all recommendations are accepted, continue with @.agent/workflows/create-plan.md and execution upon review approval.", met by the round 2 plan approval ([walkthrough.md](../../../docs/execution/plans/2026-10-29-capture-editor-repair/walkthrough.md) §Execution message, D-161).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-99.1 | unit | Surface chords: `Ctrl+Z` twice, `Ctrl+Y`, `Ctrl+Shift+Z`, `Meta+Z`, a repeat; each acting chord prevented; `Ctrl+Alt+Z` neither acts nor is prevented | 09 "Chords"; `HISTORY_CHORDS` | `ui/tests/unit/capture-page.behavior.test.ts` `AC-99.1 …` | ✅ |
| AC-99.2 | unit | Body focus: with focus on `document.body`, `Ctrl+Z` on `window` undoes one step | 09 "Focus"; `HISTORY_FOCUS` | `capture-page.behavior.test.ts` `AC-99.2 …` | ✅ |
| AC-99.3 | unit | Guards (a)–(h): text draft and font field keep their key, confirm strip and `aria-modal` inert, a live `moving` gesture prevents without change, composing ignored, a Capture button acts while a colour control does not, an empty history prevents without throwing | 09 "Focus", "Guards"; D-164 | `capture-page.behavior.test.ts` `AC-99.3 …` | ✅ |
| AC-99.4 | unit | Chord equals button: `Ctrl+Z, Ctrl+Z, Ctrl+Y` and the three clicks give equal `annotations`, selection, `capture-save` state and POST bodies | `HISTORY_ACTIONS` | `capture-page.behavior.test.ts` `AC-99.4 …` | ✅ |
| AC-99.5 | unit | Hints: `aria-keyshortcuts` `Control+Z`/`Control+Y`, labels `Undo`/`Redo`, focused hints `Undo (Ctrl+Z)`/`Redo (Ctrl+Y)` | 06 "Hints"; `HISTORY_HINTS` | `capture-page.behavior.test.ts` `AC-99.5 …` | ✅ |
| AC-99.6 | unit | Help: `HELP_EDIT_SENTENCE + ' ' + <MEU-99 sentence>`, body still ends with `RANGE_HELP_SENTENCE` | `HELP_TEXT` | `ui/tests/unit/capture-help-content.test.ts` `AC-99.6 …` | ✅ |
| AC-99.7 | integration | Electron: surface and body chords on two boxes, Save posts one rect, native undo inside the text draft, no zoom, no reload, hash `#/capture` | 09 "Tests" | `ui/tests/e2e/capture-inbox.test.ts` `AC-99.7 …` | ✅ |
| AC-100 (cross-ref) | — | Owned by the MEU-100 handoff (resize handles, maths, gesture and cursor) | plan §MEU-100 | [MEU-100 handoff](2026-10-29-capture-editor-repair-MEU-100-handoff.md) | see MEU-100 |
| AC-101 (cross-ref) | — | Owned by the MEU-101 handoff (text re-edit and corner scaling) | plan §MEU-101 | [MEU-101 handoff](2026-10-29-capture-editor-repair-MEU-101-handoff.md) | see MEU-101 |
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
| AC-99.1 | `{"ctrl":true} z: expected 2 to be 1` | pass | `capture-page.behavior.test.ts` |
| AC-99.2 | `expected 2 to be 1` | pass | `capture-page.behavior.test.ts` |
| AC-99.4 | chord run `selected: 1` against the button run (the chords did nothing) | pass | `capture-page.behavior.test.ts` |
| AC-99.5 | `capture-undo aria-keyshortcuts: expected null to be 'Control+Z'` | pass | `capture-page.behavior.test.ts` |
| AC-99.6 | four-tools body does not contain `HELP_EDIT_SENTENCE HISTORY_HELP_SENTENCE` | pass | `capture-help-content.test.ts` |
| AC-99.7 | `Error: expect(received).toBe(expected)`, Expected 1, Received 2 after the first surface `Control+KeyZ` | pass | `capture-inbox.test.ts` |

AC-99.3 is not required Red: (e), (f), (g) and (h) failed by assertion on the baseline, and (a)–(d) are negatives that hold before the feature exists (plan §Verification row 2).

Every receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-29-capture-editor-repair/walkthrough.md): §Baseline (row 0), §Census (row 1), §MEU-99 Red, §MEU-99 Green, §Gate (row 8), §Hub (row 9) and §Execution Correction Notes.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s43-99-red-run1", "command": "pwsh -NoProfile -File row-2.ps1 (task.md row 2 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-99 Red, first run: AC-99 Vitest, the baseline renderer build, Electron AC-99, red-check.py", "phase": "red", "exit_code": 1, "result": "fail", "tested_state": "HEAD 1856df5 (baseline.sha) plus the row 2 tests, TA-1 and TA-2; ui/src unchanged since baseline.sha", "output": "red-check: required test AC-99.7 did not fail by assertion alone: ['Error: surface Control+KeyZ'] (a custom expect message hid the expect( line; EC-1)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-99-red", "command": "pwsh -NoProfile -File row-2.ps1 (task.md row 2 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-99 Red after EC-1 (step labels moved into test.step): AC-99 Vitest, the baseline renderer build, Electron AC-99, red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1856df5 (baseline.sha) plus the row 2 tests, TA-1 and TA-2; ui/src unchanged since baseline.sha", "output": "Vitest 7 failed, 2 passed (2 files failed), every failure an AssertionError | Electron 1 failed: AC-99.7 Expected 1, Received 2 after the first surface Control+KeyZ | red-check: 2 receipt(s), 6 required test(s), 0 problem(s) | row 2 exit=0", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-99-green", "command": "pwsh -NoProfile -File row-3.ps1 (task.md row 3 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-99 Green: the row 3 Vitest set, build, capture-inbox and keyboard-shortcuts Electron specs whole, then the ui/src snapshot", "phase": "green", "exit_code": 1, "result": "fail", "tested_state": "HEAD 1856df5 plus rows 1-2 and the MEU-99 implementation", "output": "Vitest 7 files, 200 passed | built, CapturePage chunk 158.69 kB | Electron 41 passed, 2 failed: AC-80.10 (:1641, capture-undo-hint gone after toBeVisible) and AC-81.11 (:1930, F2 held by another process), both in the row 0 baseline set; AC-99.7 passed | the command exits before its snapshot step (EC-2)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-99-green-rerun-8010", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts --grep \"AC-80.10\" > C:/Temp/av-kit/s43-99-green-rerun-8010.txt 2>&1", "cwd": "P:/av-kit", "scope": "AC-80.10 alone on the row 3 tree: the TA-1 line", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1856df5 plus rows 1-2 and the MEU-99 implementation", "output": "1 passed (3.7s): the disabled Undo hint reads Undo (Ctrl+Z); the full-run miss is the baseline hover flake", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s43-99-snapshot", "command": "the row 3 Validation cell's last step (the ui/src SHA-256 snapshot), verbatim, alone", "cwd": "P:/av-kit", "scope": "row 3 snapshot written alone on the unchanged tree (EC-2)", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1856df5 plus rows 1-2 and the MEU-99 implementation; ui/src unedited since the row 3 run", "output": "row 3 ui/src files: 167 (row3-ui-src.json)", "fresh": true}
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
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | `HISTORY_ACTIONS` (`undo`/`redo`), `HISTORY_CHORDS` (`historyChord`, `historyOwnsFocus`, the `handleEditorKey` branch) |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | `HISTORY_HINTS` (`shortcut` on the Undo/Redo buttons) |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | MEU-99 `HELP_TEXT` sentence |
| `ui/src/renderer/src/registry/shortcuts.ts` | modified | `RESERVED_NOTE` (comment only, +2 lines) |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-99.1 to AC-99.5; TA-2 |
| `ui/tests/unit/capture-help-content.test.ts` | modified | AC-99.6 |
| `ui/tests/unit/icon-hints.test.ts` | modified | TA-3 (D-177, EC-10) |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | AC-99.7; TA-1 |

```diff
+/** HISTORY_CHORDS (D-163): Ctrl/Meta+Z undoes; Ctrl/Meta+Y and Ctrl/Meta+Shift+Z redo; Alt opts out. */
+function historyChord(event: KeyboardEvent): 'undo' | 'redo' | null {
+  if (!(event.ctrlKey || event.metaKey) || event.altKey) { return null }
+  const key = event.key.toLowerCase()
+  if (key === 'z') { return event.shiftKey ? 'redo' : 'undo' }
+  if (key === 'y' && !event.shiftKey) { return 'redo' }
+  return null
+}
@@ handleEditorKey
+    const history = historyChord(event)
+    if (history !== null) {
+      // Outside HISTORY_FOCUS the key stays the field's or the menu's: no preventDefault.
+      if (confirm !== null || !historyOwnsFocus()) { return }
+      event.preventDefault()
+      // A size transaction or a live pointer gesture owns the marks until it ends.
+      if (txOpen || gestureRef.current !== null) { return }
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
| — | — | No finding in this MEU in round 1 | — | — | — |

### Verdict

_pending: H1-7 Codex execution review, round 2_

---

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-177
    stage: execution
    question: "Gate attempt 3 found AC-80.8 (icon-hints.test.ts) still expecting the Undo/Redo hint text 'Undo'/'Redo', a row 1 census miss beside TA-2 (S2). How is it handled?"
    resolution: human
    class: governance-value
    chosen: "TA-3: declare HINT_OVERRIDE for capture-undo/capture-redo in icon-hints.test.ts and compare AC-80.8's two loops against HINT_OVERRIDE[id] ?? spec.name; nothing else in the file changes (EC-10)"
    source_tag: Human-approved
    precedents: ["implementation-plan.md TEST_AMENDMENTS TA-2 - the same hint change amended in AC-65.2", "human-gate-decision.md D-177 - the brief and its authorized items"]
    research: { engine: none, sources: [] }
    reasoning: "Mat ruled 'D-177: recommendation accepted' on 2026-11-03. MEU-99's HISTORY_HINTS changes the hint on purpose (synthesis D-1); AC-80.8 asserts what TA-2 already amended in another file. Dropping the shortcut would undo AC-99.5 and the D-1 ruling, and excusing the test would pass a deterministic failure."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-03 | claude-code-local (Claude Opus 5.5) | Initial MEU-99 handoff after H1-2 |
| Updated | 2026-11-03 | claude-code-local (Claude Opus 5.5) | H1-7 round 1 (`changes_required`, F1 in MEU-101) fixed as EC-11; H1-2, H1-3 and H1-4 re-ran on the fixed tree |
