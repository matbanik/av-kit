---
date: "2026-10-17"
project: "2026-10-16-tts-voice-panel"
meu: "MEU-79"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md"
build_plan_section: "bp11s11.13"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex via local dispatch"
predecessor: "2026-10-16-tts-voice-panel-MEU-75-handoff.md"
---

# Handoff: 2026-10-16-tts-voice-panel-MEU-79-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-79 — `gui-tts-voice-panel-layout`.
- `DEVICE_SELECT_VALUE`: `CatalogItem.devices?: string[]` (`useTtsJob.ts`). `TTSPage` derives `deviceOptions = selectedModel?.devices ?? ['auto', 'cpu']` and `effectiveDevice = deviceOptions.includes(device) ? device : 'auto'`. `device-select` lists `deviceOptions` and shows `effectiveDevice`, and Load posts `effectiveDevice`. Only a user change persists the device (D-13); the stored choice is kept for rows that offer it.
- `SEGMENT_SIZE`: `SegmentedControl` gains `size?: 'sm' | 'md'` (default `'sm'`). The inner class literal moves into `GROUP_CLASSES` unchanged, so `sm` markup is byte-identical; `md` appends ` h-9`.
- `VOICE_GRID`: `model-row` is `grid grid-cols-[minmax(0,1fr)_7rem_auto] items-end gap-2`; `model-select` and `device-select` lose their `className`; the model action button is `size="md"`. The speed row is `grid grid-cols-[minmax(0,1fr)_auto] items-end gap-2`, its label `flex min-w-0 flex-col gap-1` with the field-label span style, the slider `h-9 w-full`, and the presets `size="md"`. `format-select` sits in a `w-28` wrapper without `w-[90px]`.
- `E2E_DEVICE_SEAM` (TA-6): the `tts-generate.test.ts` seam rows carry `devices`. TA-5 needed no line change.
- No test id was added, removed or renamed.

**Build Plan Section**: `docs/build-plan/11-page-layout.md` §TTS voice panel alignment (residual) (registry 11.13; section written in row 1)
**Predecessor**: [MEU-75 handoff](2026-10-16-tts-voice-panel-MEU-75-handoff.md), whose `ModelVariantOut.devices` this MEU renders.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-79.1 | integration | `device-select` lists the selected row's `devices`: `auto, cpu` for an ONNX row, `auto, cuda, cpu` after selecting the PyTorch row; never the static four. | Spec 03:466; `DEVICE_SELECT_VALUE` | `ui/tests/unit/tts-page.behavior.test.ts:727` `AC-79.1 device options are the selected row devices, never the static four` | ✅ |
| AC-79.2 | integration | Stored `cuda` with an `['auto','cpu']` row: the select shows `auto`, Load posts `device: 'auto'`, no `PUT /settings`; the CUDA row then shows `cuda`. | D-13 | `tts-page.behavior.test.ts:737` `AC-79.2 a stored device the row lacks shows and loads as auto without a settings PUT` | ✅ |
| AC-79.3 | integration | A row without `devices` offers `auto, cpu`; no `mps`. | `DEVICE_SELECT_VALUE` | `tts-page.behavior.test.ts:754` `AC-79.3 a catalog row without devices offers auto and cpu only` | ✅ |
| AC-79.4 | integration | A 422 `ModelLoadError` from Load shows "ONNX session failed" in `error-banner` (characterization; green at Red). | `LOAD_ERROR_HTTP` | `tts-page.behavior.test.ts:761` `AC-79.4 a 422 ModelLoadError from Load shows its message in the error banner` | ✅ |
| AC-79.5 | unit | `SegmentedControl` default and `sm` keep the baseline inner class; `md` appends only ` h-9`; inner HTML identical. | `SEGMENT_SIZE` | `ui/tests/unit/layout-primitives.test.ts:306` `AC-79.5 default and sm keep the baseline inner class; md appends only h-9` | ✅ |
| AC-79.6 | integration | `VOICE_GRID` classes: grid rows, no `flex-wrap`/`flex-1`/`w-[110px]`/`w-[90px]`, `h-9` action, slider and `w-28` Format wrapper. | `VOICE_GRID` | `tts-page.behavior.test.ts:782` `AC-79.6 the voice panel uses the VOICE_GRID classes` | ✅ |
| AC-79.7 | integration | Electron `VOICE_GEOMETRY` (a): Model, Device and the action share height and bottom, the labels share a top (±0.5 px), Model is wider than Device. | Triage D-68 | `ui/tests/e2e/tts-generate.test.ts:762` `AC-79.7 model row: Model, Device and the action share height, bottom and label top` | ✅ |
| AC-79.8 | integration | Electron `VOICE_GEOMETRY` (b): voice search, Format, slider and preset group have Model's height; slider and presets share a bottom; Format has Device's width. | Triage D-68 | `tts-generate.test.ts:781` `AC-79.8 voice search, Format, slider and presets use the model control height` | ✅ |
| AC-79.9 | integration | Electron `VOICE_GEOMETRY` (c): model and speed rows do not overflow; the slider is at least 96 px; AC-64.6 green in the same run. | 11 §TTS text panel "Space"; D-14 | `tts-generate.test.ts:807` `AC-79.9 the model and speed rows never overflow and the slider keeps 96 px` | ✅ |
| AC-79.10 | integration | Electron with `E2E_DEVICE_SEAM`: 2 options for ONNX FP32, `auto, cuda, cpu` for PyTorch FP32. | `DEVICE_SELECT_VALUE` | `tts-generate.test.ts:836` `AC-79.10 device-select lists the selected row devices: 2 for ONNX FP32, 3 for PyTorch FP32` | ✅ |

### Other plan AC references (not owned by MEU-79)

| AC | Owner | Status in MEU-79 |
|----|-------|------------------|
| AC-75.1 to AC-75.10 | [MEU-75 handoff](2026-10-16-tts-voice-panel-MEU-75-handoff.md) | ✅ (rows 2–3) |
| AC-9.4 | existing `tests/integration/test_tts_models.py` | passes with MEU-75's TA-1 |
| AC-56.3 | existing `ui/tests/unit/tts-page.behavior.test.ts` | passes unchanged (TA-5: no line change) |
| AC-64.6 | existing `ui/tests/e2e/tts-generate.test.ts` | passes in the full Electron run and 10× in `e2e-repeat` |
| AC-76.4 | existing `tests/e2e/test_api_error_surface.py` | passes unchanged |
| AC-87.6, AC-87.7 | Session 37 (`capture-editor-options`), not a Session 35 AC | n/a: the plan cites them only in research note R-6, as real Session 37 receipts that `red-check.py --require` was tested against |
| AC-40.6, AC-40.30 | capture tests from an earlier session, not a Session 35 AC | n/a: the plan cites them only in §Execution Correction Notes (A-3), the clock-second race fixed in `capture-picker.test.ts` and `capture-lifecycle.test.ts` on Mat's ruling; both pass in the H1-2 gate record |
| AC-41.3 | queue-canon, an earlier session, not a Session 35 AC | n/a: the plan cites it only in §Execution Correction Notes (A-1), the one baseline-accepted `ui-tests` failure (`QUEUE-PILL-TOKEN-DRIFT`), which also failed at row 0 |
| AC-66.14 | capture-inbox E2E from an earlier session, not a Session 35 AC | n/a: the plan cites it only in §Execution Correction Notes (A-4), the pan-origin flake (`CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`) that failed post-F2 gate attempt 1; it passes in the H1-2 gate record |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (snippet) | Green Output | File:Line |
|------|----------------------|--------------|-----------|
| Vitest AC-79.1, AC-79.3 | `expected [ 'auto', 'cuda', 'cpu', 'mps' ] to deeply equal [ 'auto', 'cpu' ]` | pass | `tts-page.behavior.test.ts:727,754` |
| Vitest AC-79.2 | `expected 'cuda' to be 'auto'` | pass | `tts-page.behavior.test.ts:737` |
| Vitest AC-79.5 | the `md` inner class equals the baseline literal (no ` h-9`) | pass | `layout-primitives.test.ts:306` |
| Vitest AC-79.6 | `expected [ 'flex', 'flex-wrap', …(2) ] to include 'grid'` | pass | `tts-page.behavior.test.ts:782` |
| Electron AC-79.7 | `Error: expect(received).toEqual(expected)` `{ what: "device-select height", delta: 13.5 }` | pass | `tts-generate.test.ts:762` |
| Electron AC-79.8 | `{ what: "voice-combobox height", delta: 13.5 }` | pass | `tts-generate.test.ts:781` |
| Electron AC-79.10 | `[auto, cuda, cpu, mps]` for ONNX FP32 | pass | `tts-generate.test.ts:836` |

AC-79.4 (characterization) and AC-79.9 (the baseline rows already fit) passed at Red, as the plan allows; red-check enforced `--require AC-79.7 --require AC-79.8 --require AC-79.10` with `0 problem(s)`. The measured first mismatch at Red was `model-select` itself at 22.5 px: its `flex-1` class landed on the `<select>` inside SelectInput's column flex root, where basis 0 overrides `h-9`. `VOICE_GRID` removes that class, and Green measures 36 px on every control.

Green geometry at the default window (ad-hoc reading without the seam, walkthrough §MEU-79 Green): voice panel 416.7 px wide; `model-select` 262.7 / `device-select` 112 / `format-select` 112 px wide, all 36 px high; slider 223.3 px wide (floor 96) and presets 159.4 px, both 36 px high with equal bottoms; both rows `scrollWidth == clientWidth` (391).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s35-79-red","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 4 command, verbatim","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"MEU-79 Red on the row 3 tree (baseline renderer): Vitest -t AC-79 over the two unit files, ui build, Electron --grep AC-79 over tts-generate.test.ts, red-check with --require AC-79.7/.8/.10","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus the MEU-75 change and the row 4 tests (no ui/src change)","output":"Vitest 5 failed, 1 passed, 34 skipped (40) | ui build ok | Electron 3 failed (AC-79.7 delta 13.5, AC-79.8 delta 13.5, AC-79.10 four options), 1 passed | red-check: 2 receipt(s), 3 required test(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s35-79-green","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 5 command, verbatim","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"MEU-79 Green: both unit files unfiltered, ui build, the whole tts-generate.test.ts in Electron","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus the MEU-75 and MEU-79 change","output":"Vitest Test Files 2 passed (2), Tests 40 passed (40) | ui build ok | Electron 20 passed (AC-64.6, AC-79.7 to AC-79.10 included)","fresh":true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s35-79-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-tts-voice-panel/session-gate.ps1 *> C:/Temp/av-kit/s35-gate-h1.txt (task.md H1-2, verbatim)", "cwd": "P:/av-kit-wt/s35-tts-voice-panel", "scope": "D6 session gate re-run at H1-2 after the execution review R2 F2 correction (D-23), which followed the R1 F1 correction (D-21) and the row 7 hub and SSOT edits; the second post-F2 attempt, after A-4 (capture-inbox AC-66.14 flake, re-run unchanged); earlier post-R1 attempts were governed by A-2 and A-3; the fresh full record", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "6097cf59adc7835fa6062c8bd3d55c679aef4543+b4e8b8826bfc3656e7084cc3e63b7682214f97ad1d1b5ad141e4640573211051", "output": "scope-paths changed paths: 39 outside scope: [] | all steps exit 0 | py-tests exit 1 accepted by the baseline rule: failed=2 outside_baseline=[] errors=0 (pytest 2 failed, 935 passed, 1 warning; AC-24.10, AC-25.10) | ui-tests exit 1 accepted by A-1: failed=1 summary_failed=1 outside_baseline=[] unhandled=0 (Vitest Tests 1 failed | 980 passed (981); queue-canon AC-41.3) | MCP Tests 428 passed (428) | openapi --check 0 | state-render Drift check passed | Electron 161 passed (5.7m) | e2e-repeat 50 passed (2.2m) (AC-79.7 to AC-79.10 and AC-64.6 x10) | @playwright/test@1.62.1 electron@42.9.3 | identity before == after", "fresh": true}
```

### Quality Gate Results

The shared gate is `session-gate.ps1`. Row 6 passed on its first run after amendment A-1, at `tested_state 6097cf5…+38f98d80…6e09`. Row 7 then changed bound inputs (the hub docs, `meu-status.yaml` and the rendered `BUILD_PLAN.md`), so H1-2 re-ran the whole gate. Execution review round 1 then found F1 (MEU-75, D-21), and its correction changed the adapter and its tests, so H1-2 ran the whole gate again. Its first attempt failed only at `ui-electron`, on the known transcript-queue W2-5 timeout (`DOWNLOAD-QUEUE-DRAG-OVER-MISS`; W2-5 then passed 4/4 alone). Amendment A-2 re-ran the whole gate with no file change. Attempt 2 then failed at `ui-tests` on a clock-second race in `capture-picker.test.ts` AC-40.6, a test this session never touched; Mat ruled to fix the race (A-3: the two affected tests pin `Date`, and `scope-paths` allows them). Attempt 3 passed at `6097cf5…+c7e4a6b9…32e3` and was the record that execution review round 2 reviewed. Round 2 confirmed F1 fixed and found F2 (MEU-75, D-23): a failing lazy `kokoro` import escaped bare. Its correction changed the adapter and its test, so H1-2 ran the whole gate again. The first post-F2 attempt failed only at `ui-electron`, on `capture-inbox.test.ts` AC-66.14, a pan-origin flake in an earlier session's test (5/5 alone; known issue `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`). Amendment A-4 re-ran the whole gate with no file change. That run is the record above, at `tested_state 6097cf5…+b4e8b882…1051`, and `identity.py --state-only` re-derives the same state from the live tree (H1-6b).

The gate script has two changes from the approved plan. **A-3** only adds `ui/tests/unit/capture-picker.test.ts` and `ui/tests/unit/capture-lifecycle.test.ts` to the `scope-paths` allowlist. **A-1** (D-19): `ui-tests` applies the plan's baseline rule (§Verification Plan 1) the way `py-tests` already did. A Vitest exit 1 is accepted only when:
- every `FAIL` id is the one expected id, queue-canon AC-41.3, and that id also failed in row 0's `s35-base-ui.txt`;
- the summary's failed count equals the number of ids;
- nothing is unhandled.

A 9-case probe (`walkthrough.md` §Gate) passed the real receipt shape and refused every other case. AC-41.3 reads the Zorivest hexes live, and Zorivest 1f254832 changed them. The known issue `QUEUE-PILL-TOKEN-DRIFT` records it, and no Session 35 file is among the test's inputs.

| Step | Stage | Exit | Decisive line (H1-2) |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 6097cf5…+b4e8b882…1051` |
| py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract | static | 0 | pyright, ruff, tsc and eslint clean; task lint 0 |
| scope-paths | static | 0 | `changed paths: 39 outside scope: []` |
| py-tests | full | 1 → accepted | `2 failed, 935 passed, 1 warning`; `py-tests baseline rule: failed=2 outside_baseline=[] errors=0` (AC-24.10, AC-25.10) |
| ui-tests | full | 1 → accepted (A-1) | `Tests 1 failed | 980 passed (981)`; `ui-tests baseline rule: failed=1 summary_failed=1 outside_baseline=[] unhandled=0` |
| mcp-build, mcp-tests | full | 0 | `Tests 428 passed (428)` |
| ui-build, ui-harness-build, ui-picker-stub | full | 0 | — |
| openapi | full | 0 | `export_openapi --check` exit 0; H1-4: only `ModelVariantOut` changed |
| state-render | full | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` |
| ui-electron | runtime | 0 | `161 passed (5.7m)` (the full Electron suite; `SegmentedControl` is shared) |
| e2e-repeat | runtime | 0 | `50 passed (2.2m)` (AC-79.7 to AC-79.10 and AC-64.6, `--repeat-each=10`) |
| identity-npm | identity | 0 | `@playwright/test@1.62.1 electron@42.9.3` |
| identity-after | identity | 0 | `tested_state before == after` |

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modified | +32/−32 | `deviceOptions`, `effectiveDevice`; `VOICE_GRID` model and speed rows; `md` action and presets; `w-28` Format wrapper |
| `ui/src/renderer/src/components/ui/SegmentedControl.tsx` | modified | +6/−2 | `size`, `GROUP_CLASSES` |
| `ui/src/renderer/src/features/tts/useTtsJob.ts` | modified | +2 | `CatalogItem.devices?` |
| `ui/tests/unit/tts-page.behavior.test.ts` | modified (append only) | +90 | AC-79.1–.4, .6 |
| `ui/tests/unit/layout-primitives.test.ts` | modified (append only) | +32 | AC-79.5 |
| `ui/tests/e2e/tts-generate.test.ts` | modified | +134 | TA-6 seam `devices`; AC-79.7–.10 |
| `docs/build-plan/11-page-layout.md` | modified (row 1) | +21 | §TTS voice panel alignment (residual) |

```diff
-            <div data-testid="model-row" className="flex flex-wrap items-end gap-2">
+            <div data-testid="model-row" className="grid grid-cols-[minmax(0,1fr)_7rem_auto] items-end gap-2">
               <SelectInput
                 data-testid="model-select"
                 label="Model"
-                className="min-w-0 flex-1"
@@
                 label="Device"
-                className="w-[110px]"
-                options={[ … 'auto', 'cuda', 'cpu', 'mps' … ]}
-                value={device}
+                options={deviceOptions.map((option) => ({ value: option, label: option }))}
+                value={effectiveDevice}
@@
-                        await postLoad(variantId, device)
+                        await postLoad(variantId, effectiveDevice)
```

```diff
-      <div className="inline-flex rounded-[var(--radius-control)] border border-border bg-surface-0 p-0.5">
+      <div className={size === 'md' ? `${GROUP_CLASSES} h-9` : GROUP_CLASSES}>
```

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

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-20
    stage: execution
    question: "Playwright prints a custom expect message in place of the `Error: expect(` header, so red-check cannot attribute the Electron Red. How do the AC-79 Electron tests name the failing pair?"
    resolution: autonomous
    class: two-way
    chosen: "No custom messages; expectNear compares { what, delta } objects so the diff names the pair under the standard expect header"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-16-tts-voice-panel/red-check.py — accepts `Error: expect(` as the Playwright diagnostic", "docs/execution/plans/2026-10-16-tts-voice-panel/walkthrough.md §MEU-79 Red — the first attempt reported 4 problems"]
    research: { engine: none, sources: [] }
    reasoning: "Changing red-check would weaken a reviewed gate; carrying the name in the received value keeps both the checker and a readable diff. The bounds (±0.5 px) are unchanged."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-17 | claude-code | Initial handoff after the H1-2 gate |
| Updated | 2026-10-17 | claude-code | H1-2 gate re-run after the MEU-75 execution review R1 F1 correction (no MEU-79 file changed); the gate record above is the re-run |
