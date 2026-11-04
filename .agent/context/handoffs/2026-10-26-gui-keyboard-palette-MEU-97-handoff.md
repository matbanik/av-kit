---
date: "2026-10-26"
project: "gui-keyboard-palette"
meu: "MEU-97"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-26-gui-keyboard-palette/implementation-plan.md"
build_plan_section: "bp06"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-10-26-gui-keyboard-palette-MEU-96-handoff.md"
---

# Handoff: 2026-10-26-gui-keyboard-palette-MEU-97-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-97, `gui-common-shortcuts`. Adds the common chord set, binds each chord to the control it performs, and shows each chord in that control's hint.
**Build Plan Section**: [06 §Common shortcuts (residual)](../../../docs/build-plan/06-gui.md#common-shortcuts-residual).
**Predecessor**: [MEU-96 handoff](2026-10-26-gui-keyboard-palette-MEU-96-handoff.md). The [MEU-95 handoff](2026-10-26-gui-keyboard-palette-MEU-95-handoff.md) is the plan's first MEU.

Before this MEU, only navigation, Ctrl+B and Ctrl+K had chords. No page action had a keyboard path, and no control said which chord performed it.

- **`CHORD_TABLE`.** These go through `SHORTCUT_MAP`:
  - `download:add` and `transcript:add` take Ctrl+L on their pages.
  - `convert:browse` takes Ctrl+O on Convert.
  - `capture:save` takes Ctrl+S on Capture (stateful).
  - `page:primary` takes Ctrl+Enter.
  - `console:toggle` takes Ctrl+J and `help:toggle` takes F1.
- **`PAGE_PRIMARY`.** `PAGE_PRIMARY_CONTROL` maps each page to its primary button. `page:primary` (`palette: false`) clicks it only while it is an enabled button, and does nothing on Settings.
- **`HINTS`.** Each `BOUND_CONTROLS` control carries `aria-keyshortcuts` and names its chord: `title="<name> (<chord>)"`, or for `ToolbarIconButton` the new `shortcut` prop, which sets the tooltip label.
- **`PALETTE_ENTER`.** A modified Enter in the palette input passes through to the window handler, so Ctrl+Enter runs the page action and closes the palette.
- **`CAPTURE_SAVE_ROUTE`.** `CAPTURE_COMMANDS.save` presses an enabled `capture-save` instead of calling `saveAnnotations`, so Ctrl+S, the palette and the button all end with the shot marked saved.
- **`CAPTURE_CHORD_BUBBLE` (EC-3).** Capture's focused draw surface stops propagation for its own keys but lets a registry chord through to the shell (`isRegistryChord`).
- **Index.** The `gui-actions-index.md` Trigger cells name the chords.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-26-gui-keyboard-palette/implementation-plan.md) §MEU-97. **Execution authorization:** see the [MEU-95 handoff](2026-10-26-gui-keyboard-palette-MEU-95-handoff.md) §Scope.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-97.1 | unit | `CHORD_TABLE`: each id's chord and page; the registry map builds; no `F2`, `Ctrl+=`, `Ctrl+-`, `Ctrl+0` or `Ctrl+Plus` key | 06 "Core set", "No collisions" | `ui/tests/unit/shortcuts.test.ts` (MEU-97 describe) | ✅ |
| AC-97.2 | unit | `PAGE_PRIMARY`: an enabled primary is clicked once, a disabled one is not, Settings clicks nothing; `palette: false` | 06 "Core set" | `shortcuts.test.ts` (MEU-97 describe) | ✅ |
| AC-97.3 | unit | Page scope: `Ctrl+L` on Convert, `Ctrl+O` on Downloader and `Ctrl+S` on TTS are not handled; `Ctrl+S` on Capture runs only with `capture:save` state `true` | 06 "Page scope" | `shortcuts.test.ts` (MEU-97 describe) | ✅ |
| AC-97.4 | unit | `HINTS`: every `BOUND_CONTROLS` control carries `aria-keyshortcuts` and names its chord where it is rendered | 06 "Hints" | `common-shortcuts.test.tsx`; the five page harnesses and `settings-page.test.ts`; `capture-page.test.ts` (source text) | ✅ |
| AC-97.5 | unit | Index triggers: each `CHORD_TABLE` id's Trigger cell has its chord | 06 "Index" | `ui/tests/unit/gui-actions-audit.test.ts` (MEU-97 describe) | ✅ |
| AC-97.6 | integration | Electron: `Ctrl+L` focuses `url-input` and `channel-input` and does nothing on TTS; `Ctrl+J` toggles the console; `F1` flips the help toggle on Settings | 06 "Tests" | `ui/tests/e2e/keyboard-shortcuts.test.ts` `AC-97.6 …` | ✅ |
| AC-97.7 | integration | Electron: `Ctrl+O` on Convert stages a file and Add queues one row; on Downloader it does nothing | 06 "Core set" | `ui/tests/e2e/convert-queue.test.ts` `AC-97.7 …` | ✅ |
| AC-97.8 | integration | Electron: after one arrow, `Ctrl+S` posts one annotation set and the shot is clean; a second `Ctrl+S` and one on a clean shot post nothing | 06 "Core set" | `ui/tests/e2e/capture-inbox.test.ts` `AC-97.8 …` | ✅ |
| AC-97.9 | integration | Electron: `Ctrl+Enter` with a valid URL sends the `add-btn` `POST /downloads`, sends none with an empty URL, and from the open palette sends one, leaves the console hidden and closes the palette | 06 "Core set" | `ui/tests/e2e/download-queue.test.ts` `AC-97.9 …` | ✅ |
| AC-97.10 | unit | `PALETTE_ENTER`: `Ctrl+Enter` does not run the highlighted command and reaches `window` not prevented; plain `Enter` runs it once | 06 "Core set" | `ui/tests/unit/common-shortcuts.test.tsx` `AC-97.10 …` | ✅ |
| AC-97.11 | unit | `CAPTURE_SAVE_ROUTE`: one mark, `CAPTURE_COMMANDS.save()` posts once, `capture-save` unmounts, the state is not `true`, a second save posts nothing; AC-60.10 stays green | 06 "Core set" | `ui/tests/unit/capture-page.behavior.test.ts` `AC-97.11 …` | ✅ |
| AC-60 (cross-ref) | regression | AC-60.10's two save-refusal tests stay green under `CAPTURE_SAVE_ROUTE`; AC-60.11 was the test the S6 waiting fix freed (§Quality Gate Results) | `CAPTURE_SAVE_ROUTE` | `capture-page.behavior.test.ts` (gate `ui-tests`) | ✅ |
| AC-59 (cross-ref) | regression | AC-59.12 calls the lifted `installAnnotationStore(page)` unchanged; AC-97.8 reuses it | plan §MEU-97 | `capture-inbox.test.ts` (gate `ui-electron`) | ✅ |
| AC-95 (cross-ref) | — | Owned by the MEU-95 handoff (shortcut binding) | plan §MEU-95 | [MEU-95 handoff](2026-10-26-gui-keyboard-palette-MEU-95-handoff.md) | see MEU-95 |
| AC-96 (cross-ref) | — | Owned by the MEU-96 handoff (palette curation and the rider) | plan §MEU-96 | [MEU-96 handoff](2026-10-26-gui-keyboard-palette-MEU-96-handoff.md) | see MEU-96 |
| AC-23 (cross-ref) | regression | AC-23.18 to AC-23.20 stay green with the amended Trigger cells and the `page:primary` row | `INDEX_AMEND` | `gui-actions-audit.test.ts` (gate `ui-tests`) | ✅ |
| AC-19 (cross-ref) | regression | AC-19.17: the Ctrl+K contract, with Ctrl+Enter passing through the palette | `PALETTE_ENTER` | `ui/tests/unit/command-palette.test.ts` (gate `ui-tests`) | ✅ |
| AC-20, AC-21, AC-22, AC-33 (cross-ref) | regression | AC-20.13, AC-21.13, AC-22.19, AC-33.13: no `apiFetch` in the registry (`page:primary` only clicks) | `PAGE_PRIMARY` | `downloader-page.test.ts`, `transcript-page.test.ts`, `tts-page.test.ts`, `convert-page.test.ts` (gate `ui-tests`) | ✅ |
| AC-33, AC-39 (cross-ref) | regression | TA-4 (AC-33.2) and TA-3 (AC-39.2) are in the MEU-95 handoff | `TEST_AMENDMENTS` | [MEU-95 handoff](2026-10-26-gui-keyboard-palette-MEU-95-handoff.md) | see MEU-95 |
| AC-45, AC-46 (cross-ref) | regression | AC-45.4a and AC-46.1a: the feature palette ids and event keys are unchanged | `CONFIRM_ROUTE` | `convert-commands.test.ts`, `download-commands.test.ts` (gate `ui-tests`) | ✅ |
| AC-24, AC-25 (cross-ref) | regression | Packaging tests in the gate's `py-tests`; AC-25.7 is excused as a baseline failure, AC-24.10 and AC-25.10 are not excused | §Verification Plan baseline rule | `session-gate.ps1` `py-tests` | baseline rule |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-97.1 to AC-97.3 | `AssertionError`: no `page:primary`, no `PAGE_PRIMARY_CONTROL`, `Ctrl+S` on `/capture` not bound | pass | `shortcuts.test.ts` |
| AC-97.4 (seven files) | `AssertionError`: `BOUND_CONTROLS` absent, no `aria-keyshortcuts` | pass | `common-shortcuts.test.tsx`, the page harnesses, `capture-page.test.ts` |
| AC-97.5 | `AssertionError`: the Trigger cells lack the chords | pass | `gui-actions-audit.test.ts` |
| AC-97.10 | `AssertionError`: Ctrl+Enter ran the highlighted command | pass | `common-shortcuts.test.tsx` |
| AC-97.11 | `AssertionError: the saved shot is clean: expected <button> to be null` | pass | `capture-page.behavior.test.ts` |
| AC-97.6 | `Error: expect(`: `url-input` not focused after `Control+L` | pass | `keyboard-shortcuts.test.ts` |
| AC-97.7 | `Error: expect(`: `convert-staged-remove` count 0 after `Control+O`, expected 1 | pass | `convert-queue.test.ts` |
| AC-97.8 | `Error: expect(`: annotate POST count 0 after `Control+S`, expected 1 | pass | `capture-inbox.test.ts` |
| AC-97.9 | `Error: expect(`: `POST /downloads` count 0 after `Control+Enter`, expected 1 | pass | `download-queue.test.ts` |

Receipts: [walkthrough.md](../../../docs/execution/plans/2026-10-26-gui-keyboard-palette/walkthrough.md) §MEU-97 Red (row 6), §MEU-97 Green (row 7), §Gate (row 8), §Hub (row 9) and Execution Correction Notes EC-3 to EC-5.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s41-97-red","command":"pwsh -NoProfile -File C:/Temp/av-kit/s41-row-6.ps1 (task.md row 6 Validation cell, verbatim, from P:/av-kit)","cwd":"P:/av-kit","scope":"MEU-97 Red: the MEU-97 unit tests in eight files, the row 5 renderer build, AC-97.6 to AC-97.9, red-check.py","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD bb481ec plus rows 1-5 and the row 6 tests; ui/src changed since row 5: []","output":"Vitest 13 failed, 331 skipped (344), every failure an AssertionError | Electron 4 failed, each by Error: expect( | red-check: 2 receipt(s), 7 required test(s), 0 problem(s) | row 6 exit=0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s41-97-green-run2","command":"pwsh -NoProfile -File C:/Temp/av-kit/s41-row-7.ps1 (task.md row 7, verbatim; receipts kept with -run2 suffixes)","cwd":"P:/av-kit","scope":"MEU-97 Green run 2, before EC-3","phase":"green","exit_code":1,"result":"fail","tested_state":"HEAD bb481ec plus rows 1-6 and the MEU-97 implementation, before CAPTURE_CHORD_BUBBLE","output":"Vitest 375 passed (375) | Electron 1 failed, 90 passed: AC-97.8 annotate POST count 0 after Control+S | probe: PROBE-FOCUS capture-draw-surface, PROBE-WINDOW-KEYS [] | S2-style stop, ruled D-155","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s41-97-green","command":"pwsh -NoProfile -File C:/Temp/av-kit/s41-row-7.ps1 (task.md row 7, verbatim)","cwd":"P:/av-kit","scope":"MEU-97 Green run 3: the row 7 Vitest set, build, the row 7 Electron specs whole","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD bb481ec plus rows 1-6, the MEU-97 implementation and EC-3","output":"Vitest 15 files, 375 passed (375) | built in 7.13s | Electron 91 passed (4.9m), AC-97.6 to AC-97.9 included (AC-97.8 2.5s) | row 7 exit=0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s41-gate-run1","command":"$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-26-gui-keyboard-palette/session-gate.ps1 *> C:/Temp/av-kit/s41-gate.txt (task.md row 8, verbatim; log kept as s41-gate-run1.txt)","cwd":"P:/av-kit","scope":"Row 8 session gate run 1","phase":"full","exit_code":3,"result":"fail","tested_state":"bb481ec7d46fdb45b47e533fc2ab83e47e31e227 plus the row 7 tree, before EC-4","output":"identity-before and the first five static steps exit=0 | task-contract stage=static exit=3: FAIL-CLOSED RECEIPTS_DIR is unset | every later step not_run reason=fail-fast | fixed by EC-4 (D-156)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s41-gate-run2","command":"$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-26-gui-keyboard-palette/session-gate.ps1 *> C:/Temp/av-kit/s41-gate.txt (task.md row 8, verbatim; log kept as s41-gate-run2.txt)","cwd":"P:/av-kit","scope":"Row 8 session gate run 2","phase":"full","exit_code":1,"result":"fail","tested_state":"bb481ec7d46fdb45b47e533fc2ab83e47e31e227 plus the row 7 tree and EC-4","output":"task-contract exit=0 | scope-paths stage=static exit=1: changed paths: 56 outside scope: ['ui/tests/unit/fixtures/chord-table.ts', 'ui/tests/unit/helpers/bound-hint.ts'] head moved (S8): False | later steps not_run | S5 stop, ruled D-157 (EC-5)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s41-gate-run3","command":"$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-26-gui-keyboard-palette/session-gate.ps1 *> C:/Temp/av-kit/s41-gate.txt (task.md row 8, verbatim; log kept as s41-gate-run3.txt)","cwd":"P:/av-kit","scope":"Row 8 session gate run 3","phase":"full","exit_code":1,"result":"fail","tested_state":"bb481ec7d46fdb45b47e533fc2ab83e47e31e227 plus the row 7 tree, EC-4 and EC-5","output":"static steps and scope-paths exit=0 | py-tests passed by the baseline rule | ui-tests exit=1: 1 failed | 1081 passed: AC-60.11 Unable to find an element by: [data-testid=\"capture-save\"] (capture-page.behavior.test.ts:806) | cause: AC-97.11's last CAPTURE_COMMANDS.save() fired two animation frames later, inside AC-60.11 | later steps not_run","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s41-gatefix-cpb","command":"cd ui; npx vitest run tests/unit/capture-page.behavior.test.ts > C:/Temp/av-kit/s41-gatefix-cpb-N.txt (N = 1..8); npx tsc --noEmit; npx eslint --max-warnings 0 tests/unit/capture-page.behavior.test.ts","cwd":"P:/av-kit/ui","scope":"S6 waiting fix: deliverSave() waits out navigateAndDeliver's two animation frames in AC-60.10 (two tests) and AC-97.11","phase":"targeted","exit_code":0,"result":"pass","tested_state":"the run 3 tree plus the capture-page.behavior.test.ts waiting fix; no product change","output":"capture-page.behavior.test.ts passed 8 of 8 runs | tsc exit 0 | eslint exit 0","fresh":true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s41-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-26-gui-keyboard-palette/session-gate.ps1 *> C:/Temp/av-kit/s41-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s41-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 fresh full session gate after row 9 (INPUT_IDENTITY): static, py/ui/mcp tests, builds, openapi, state-render, ui-electron, e2e-repeat, identity before/npm/after", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c", "output": "identity-before exit=0 | py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract, scope-paths exit=0 | py-tests baseline rule: failed=5 outside_baseline=[] errors=0 (932 passed) | ui-tests Test Files 106 passed (106), Tests 1082 passed (1082) | mcp-build exit=0 | mcp-tests Test Files 31 passed (31), Tests 446 passed (446) | ui-build, ui-harness-build, ui-picker-stub, openapi exit=0 | state-render Drift check passed | ui-electron 178 passed (4.1m) | e2e-repeat 70 passed (1.1m) | identity-npm, identity-after exit=0 | tested_state before=bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c after=bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c | session-gate: all steps exit 0", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s41-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code", "cwd": "P:/av-kit", "scope": "H1-3 SSOT render check after row 9's status writes", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c", "output": "Drift check passed — SSOT loaded (98 MEUs, 12 phases), rendered regions match on-disk content", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s41-h1-4-openapi", "command": "rtk proxy uv run python -c \"import json,pathlib,subprocess,sys; b=pathlib.Path('docs/execution/plans/2026-10-26-gui-keyboard-palette/baseline.sha').read_text().strip(); old=json.loads(subprocess.run(['git','show',b+':openapi.committed.json'],capture_output=True,text=True,check=True).stdout)['components']['schemas']; new=json.loads(pathlib.Path('openapi.committed.json').read_text(encoding='utf-8'))['components']['schemas']; added=sorted(set(new)-set(old)); removed=sorted(set(old)-set(new)); changed=sorted(k for k in set(old)&set(new) if old[k]!=new[k]); print('added:',added,'removed:',removed,'changed:',changed); sys.exit(0 if not added and not removed and not changed else 1)\" *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt,C:/Temp/av-kit/s41-D6-openapi.txt; exit $code", "cwd": "P:/av-kit", "scope": "H1-4 OpenAPI: committed schemas against baseline.sha, plus the H1-2 openapi receipt", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c", "output": "added: [] removed: [] changed: [] | H1-2 openapi stage=full exit=0", "fresh": true}
```

### Quality Gate Results

The H1-2 fresh gate is the session's full record. Row 9 changed bound inputs after row 8, so the record is H1-2, not row 8 (`INPUT_IDENTITY`). Every step exited 0. py-tests exited 1, as the plan's baseline rule allows: its 5 failures are all in the baseline set (`outside_baseline=[]`), AC-25.7 among them (`PACKAGING-MCP-SNIPPET-TOKEN-STALE`). The other step counts:

- ui Vitest: 106 files, 1082 passed.
- MCP Vitest: 31 files, 446 passed.
- Electron: 178 passed (4.1m); the e2e repeat: 70 passed (1.1m).
- `state-render`: drift check passed.
- Identity: `tested_state` `bb481ec7d46fdb45b47e533fc2ab83e47e31e227+f07e5ce8b9bb5c630abdfed1d301c89ab53de7b76f91087f4803840639409e7c` was the same before and after.

Row 8 run 4 passed whole on the pre-row-9 tree (state `c30c9b…`). It is kept as prose, not as a full record, because row 9 then changed bound inputs. Runs 1 to 3 failed and are recorded in the MEU-97 handoff (EC-4, EC-5 and the AC-60.11 waiting fix). H1-3: render check exit 0. H1-4: no OpenAPI schema added, removed or changed.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/registry/shortcuts.ts` | modified | `PAGE_PRIMARY_CONTROL`, `BOUND_CONTROLS` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modified | `CHORD_TABLE` chords; `page:primary`; `isRegistryChord` (EC-3) |
| `ui/src/renderer/src/components/layout/Header.tsx`, `components/help/HelpCard.tsx` | modified | console button and help toggle hints |
| `ui/src/renderer/src/features/capture/ToolbarIconButton.tsx` | modified | `shortcut` prop |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | `capture-save` and `capture-region` hints |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | `CAPTURE_CHORD_BUBBLE` (EC-3) |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modified | `CAPTURE_SAVE_ROUTE` |
| `ui/src/renderer/src/components/CommandPalette.tsx` | modified | `PALETTE_ENTER` |
| `DownloaderPage.tsx`, `TranscriptPage.tsx`, `TTSPage.tsx`, `ConvertPage.tsx`, `SettingsPage.tsx` | modified | the bound controls' hints |
| `ui/tests/unit/shortcuts.test.ts`, `common-shortcuts.test.tsx` (new) | modified/new | AC-97.1 to AC-97.4, AC-97.10 |
| `ui/tests/unit/fixtures/chord-table.ts`, `helpers/bound-hint.ts` | new | shared `CHORD_TABLE` rows and hint helpers (EC-5) |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-97.11; the `deliverSave()` waiting fix (S6) |
| the five page test files, `settings-page.test.ts`, `capture-page.test.ts` | modified | AC-97.4 |
| `ui/tests/unit/gui-actions-audit.test.ts` | modified | AC-97.5 |
| `ui/tests/e2e/keyboard-shortcuts.test.ts`, `convert-queue.test.ts`, `capture-inbox.test.ts`, `download-queue.test.ts` | modified | AC-97.6 to AC-97.9; `installAnnotationStore(page)` lifted from AC-59.12 |
| `docs/build-plan/gui-actions-index.md` | modified | Trigger cells name the chords |
| `docs/execution/plans/2026-10-26-gui-keyboard-palette/session-gate.ps1` | modified | EC-2, EC-4, EC-5 (plan-local tooling) |

```diff
         handleViewKey(event.nativeEvent)
         onEditorKey(event.nativeEvent)
-        event.stopPropagation()
+        // CAPTURE_CHORD_BUBBLE: a registry chord still reaches the shell's window handler.
+        if (!isRegistryChord(event.nativeEvent)) {
+          event.stopPropagation()
+        }
```

```diff
+          // PALETTE_ENTER: a modified Enter passes through to the window chord handler.
+          if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) {
+            return
+          }
```

---

## Codex Validation Report

Pending: the H1-7 Codex execution review. The verdict is recorded in `2026-10-26-gui-keyboard-palette-implementation-critical-review.md`.

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

_pending: H1-7 Codex execution review_

---

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-155
    stage: execution
    question: "Capture's focused draw surface calls stopPropagation on every key, so Ctrl+S never reaches AppShell's window handler (AC-97.8). How does a registry chord leave the surface?"
    resolution: human
    class: source-conflict
    chosen: "Registry chords bubble: the surface skips stopPropagation for a chord isRegistryChord reports, and keeps containing every other key; CaptureViewport.tsx joins the scope (EC-3)"
    source_tag: Human-approved
    precedents: ["implementation-plan.md SHELL_WIRING - one window keydown listener, never on document", "06-gui.md Common shortcuts 'Core set' - Ctrl+S saves as the button does"]
    research: { engine: none, sources: [] }
    reasoning: "Mat ruled 'Registry chords bubble (Recommended)' on 2026-10-26. A probe showed focus on capture-draw-surface and no window keydown. The surface's own handlers bind no registry chord, so letting registry chords through handles no key twice. A capture-only Ctrl+S listener would have bound a chord outside the registry, which SHELL_WIRING forbids."
  - id: D-156
    stage: execution
    question: "The gate's task-contract step fails closed (exit 3) because RECEIPTS_DIR is unset in the gate's process. How does the gate supply it?"
    resolution: autonomous
    class: two-way
    chosen: "session-gate.ps1 sets $env:RECEIPTS_DIR = $receipts before its steps (EC-4)"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-16-capture-editor-options/session-gate.ps1:22-24 - the same assignment and comment", "task.md rows pass RECEIPTS_DIR=C:/Temp/av-kit to the same lint"]
    research: { engine: none, sources: [] }
    reasoning: "The lint reads the receipt paths only through RECEIPTS_DIR. Setting it in the gate follows an earlier plan's gate exactly and weakens no check; removing the line reverts it."
  - id: D-157
    stage: execution
    question: "SCOPE_CHECK found two row 6 test-support files outside PRODUCT_SCOPE (fixtures/chord-table.ts, helpers/bound-hint.ts). Revert or admit?"
    resolution: human
    class: governance-value
    chosen: "Admit both into MEU-97's Files Modified table and the scope-paths allow-list (EC-5)"
    source_tag: Human-approved
    precedents: ["implementation-plan.md Stop Conditions S5 - revert or stop with a Decision Brief", "walkthrough.md MEU-97 Red - row 6 names both files"]
    research: { engine: none, sources: [] }
    reasoning: "Mat ruled 'Admit both, EC-5 (Recommended)' on 2026-10-26. Both are test-only and shared by the AC-97.1, AC-97.4 and AC-97.5 tests. Reverting would have inlined the same rows into several files. The miss was in recording the scope change, not in the work."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-26 | claude-code-local (Claude Opus 5.5) | Initial MEU-97 handoff after H1-2 |
