---
date: "2026-10-16"
project: "capture-new-marks"
meu: "MEU-91"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: ".agent/context/handoffs/2026-10-16-capture-new-marks-MEU-90-handoff.md"
---

# Handoff: 2026-10-16-capture-new-marks-MEU-91-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-91 — `capture-eraser-mark`. An `eraser` rectangle mark filled with the most common colour along its border.
**Build Plan Section**: [09 §Eraser mark](../../../docs/build-plan/09-screenshot-capture.md#eraser-mark), matrix 9.24.
**Predecessor**: [MEU-90 handoff](2026-10-16-capture-new-marks-MEU-90-handoff.md) (same session; MEU-91 builds on its `REGION_PASS`).

The eraser goes through the same layers as the pixelate:

- **Domain, sidecar and transport.** `EraserAnnotation(x, y, width, height)` is in the `Annotation` union. It is in the sidecar (four ints), the API (`EraserAnnotationIn`, `extra="forbid"`), `openapi.committed.json`, the MCP Zod union and the renderer Zod union. It has no `color`: the fill is computed, never stored.
- **Bake.** `eraser_fill(canvas, box)` is `ERASER_SAMPLE`. It takes the most frequent RGB in the 1-px ring outside the clipped rectangle, or the rectangle's own edge pixels when that ring is empty, and a tie goes to the smallest packed value. `_apply_eraser` pastes that colour at alpha 255. `apply_region_pass` runs the region marks in list order, so an eraser after a pixelate samples the mosaic.
- **Editor.** The Eraser tool button (`capture-tool-eraser`, lucide `Eraser`) has no option controls. The TS `eraserFill` and `applyRegionPass` give the live preview on the `capture-region-layer` canvas. An eraser renders as the same transparent `REGION_MARK_SVG` rect, selects and moves like a pixelate, and is labelled `Eraser n`. The help section `four-tools` is now titled "Annotation tools" and names all six tools.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md) §MEU-91. **Execution authorization:** `USER_EXPLICIT` 2026-10-16 "@.agent/workflows/execution-session.md  Session 39 as per session grouping" ([walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md) §Execution message).

**Test amendments applied (approved in the plan; TA-6 and TA-7 approved by Mat in D-24):** the eraser parts of TA-1 to TA-7. The only other test change is the AC-91.9 Red-test correction (D-28).

The session gate covers both MEUs. Its record and the gate decision (D-30) are in the [MEU-90 handoff](2026-10-16-capture-new-marks-MEU-90-handoff.md). The gate records are repeated below because this handoff must stand on its own evidence.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-91.1 | unit | `EraserAnnotation(x, y, width, height)` constructs; `AnnotationType.Eraser.to_wire() == "eraser"` (TA-1); a negative size, a `bool` and a float are refused | Spec 09:820 | `tests/unit/test_domain_capture.py::test_ac_91_1_eraser_annotation_is_a_rectangle` | ✅ |
| AC-91.2 | unit | Sidecar round-trip; extra key ignored; `_clamp_annotation` clamps like a `rect`; a missing `height` is the "missing annotation field" error | Spec 09:820 | `tests/unit/test_capture_service.py::test_ac_91_2_eraser_sidecar_round_trip_and_clamp` | ✅ |
| AC-91.3 | integration | API annotate with an eraser returns 200 and echoes it; `EraserAnnotationIn` in `openapi.committed.json`; 422 for `color`, `block_size` and a missing `x` | Spec 09:820 | `tests/e2e/test_api_captures.py::test_ac_91_3_annotate_eraser_round_trip_and_refusals`; gate `openapi` | ✅ |
| AC-91.4 | unit | MCP annotate accepts an eraser and forwards it unchanged; `color` and `block_size` refused. Renderer Zod parity | Spec 09:820 | `mcp-server/tests/capture.test.ts` `AC-91.4 …`; `ui/tests/unit/capture-annotate.test.ts` `AC-91.4 …` | ✅ |
| AC-91.5 | unit | For each eraser case of `REGION_CASES` the rectangle is exactly `ERASER_SAMPLE` (independent `_ring`/`_ring_mode` oracle) and outside is byte-equal; the `eraser-stems` ring mean is asserted to differ; JPEG and WebP originals fill with the decoded ring mode | Spec 09:821, 09:823 | `tests/unit/test_capture_adapter.py::test_ac_91_5_eraser_fill_is_the_ring_mode` | ✅ |
| AC-91.6 | unit | `REGION_PASS` order: in `pixelate-then-eraser` the fill is the mode of the pixelated ring and the reversed list differs; a `text` mark over an eraser stays crisp in either list position | D-10, D-13 | `test_capture_adapter.py::test_ac_91_6_eraser_samples_the_pixelated_ring_and_text_stays_crisp` | ✅ |
| AC-91.7 | unit | TS `applyRegionPass` equals `expected` exactly for every eraser case and `pixelate-then-eraser`, with a comparator self-check; `eraserFill` gives the stems, tie and cover colours | D-12; `ERASER_SAMPLE` | `ui/tests/unit/capture-region-pass.test.ts` `AC-91.7 …` (2) | ✅ |
| AC-91.8 | unit | `TOOL_BUTTON_IDS.eraser === 'capture-tool-eraser'`, icon and name; `optionGroups('eraser', null)` and a selected eraser give `[]`; the pixelate tool with a selected eraser stays `['block']` (TA-2) | `TOOLS_ADDED`; `OPTIONS_BY_TOOL_V2` | `ui/tests/unit/capture-toolbar.test.ts` `AC-91.8 …` | ✅ |
| AC-91.9 | integration | An Eraser drag makes one `eraser` mark, "Eraser 1", with no option controls; it selects, moves and is removed like a pixelate; a click on the image off the mark deselects; Save sends `REGION_DTO`; a zero-size drag makes no mark | `REGION_EDIT` | `ui/tests/unit/capture-page.behavior.test.ts` `AC-91.9 …`; `ui/tests/unit/capture-hit-test.test.ts` `AC-91.9 …` | ✅ |
| AC-91.10 | integration | Electron `REGION_PIXEL_ORACLE` (a), with tolerance 0, and (b) for the eraser of `REGION_IMAGE_MARKS` | Spec 09:823 | `ui/tests/e2e/capture-inbox.test.ts` `AC-91.10 REGION_PIXEL_ORACLE …` (also in the gate's `e2e-repeat`, 10×) | ✅ |
| AC-91.11 | unit | Help section `four-tools` is titled "Annotation tools", and its body names Arrow, Box, Highlight, Text, Pixelate and Eraser (`HELP_TOOLS`, TA-3) | Spec 09:157 (amended) | `ui/tests/unit/capture-help-content.test.ts` `AC-91.11 …` | ✅ |
| AC-90 (cross-ref) | — | Owned by MEU-90 (AC-90.1 to AC-90.13); MEU-91 reuses its `REGION_PASS`, `REGION_PREVIEW` and `REGION_EDIT` | plan MEU-90 | [MEU-90 handoff](2026-10-16-capture-new-marks-MEU-90-handoff.md) | see MEU-90 |
| AC-39 (cross-ref) | regression | AC-39.8 tool id list amended by TA-3 (`capture-tool-eraser`); AC-39.13 `HELP_TOPICS` `'annotation tools'` | plan `TEST_AMENDMENTS` | `ui/tests/unit/capture-page.test.ts` `AC-39.8 …`, `AC-39.13 …` | ✅ |
| AC-59 (cross-ref) | regression | AC-59.16 MCP annotate description and example, unaffected (D-21) | walkthrough §Census | `mcp-server/tests/capture.test.ts` `AC-59.16 …` (gate `mcp-tests`) | ✅ |
| AC-65 (cross-ref) | regression | AC-65.1 and AC-65.3 options row with the eraser (`[]`) before Text (TA-2, TA-4); AC-65.4 NO_OVERFLOW tool loop with `eraser` (TA-5) | plan `TEST_AMENDMENTS` | `capture-toolbar.test.ts` `AC-65.1 …`; `capture-page.behavior.test.ts` `AC-65.3 …`; `capture-inbox.test.ts` `AC-65.4 …` | ✅ |
| AC-80 (cross-ref) | regression | AC-80.8 disabled-tool hint, amended by TA-7 (`NO_SHOT_IDS` gains `capture-tool-eraser`) | D-24 | `ui/tests/unit/icon-hints.test.ts` `AC-80.8 …` | ✅ |
| AC-82 (cross-ref) | regression | AC-82.5 `TEXT_FIXTURE` freshness: `write_fixture` and the default `main` are unchanged | plan Files Modified | `tests/unit/test_capture_bake_fixture.py::test_ac_82_5_writer_reproduces_the_committed_pngs` and the other two `test_ac_82_5_*` (gate `py-tests`) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-91.1, AC-91.2, AC-91.6 | `E   ImportError: cannot import name 'EraserAnnotation' from 'avkit_core.domain.capture'` (declared new) | pass | `tests/unit/test_domain_capture.py:440`; `tests/unit/test_capture_service.py:1153`; `tests/unit/test_capture_adapter.py:1178` |
| AC-91.5 | `E   ImportError: cannot import name 'eraser_fill' from 'avkit_infra.capture.adapter'` | pass | `test_capture_adapter.py:1132` |
| AC-91.3 | `E   ImportError: cannot import name 'EraserAnnotationIn' from 'avkit_api.schemas.captures'` | pass | `tests/e2e/test_api_captures.py:1117` |
| AC-91.4 (MCP) | `AssertionError: expected false to be true` (`captureSchema` refuses the eraser body) | pass | `mcp-server/tests/capture.test.ts:526` |
| AC-91.4 (renderer) | `expected null not to be null` (`parseAnnotateBody` refuses the eraser) | pass | `ui/tests/unit/capture-annotate.test.ts:100` |
| AC-91.7 (2) | `typeof eraserFill` is `'undefined'` | pass | `ui/tests/unit/capture-region-pass.test.ts:151`, `:173` |
| AC-91.8 | `TOOL_BUTTON_IDS.eraser` is `undefined` | pass | `ui/tests/unit/capture-toolbar.test.ts:155` |
| AC-91.9 | hit test: `markLabel` is not `Eraser 1`; page: no `capture-tool-eraser` (null) | pass | `ui/tests/unit/capture-hit-test.test.ts:242`; `ui/tests/unit/capture-page.behavior.test.ts:1663` |
| AC-91.10 | `expect(errors).toEqual([])`, received `["Invalid overlay marks"]` (`REGION_E2E_RED`, row 5a) | pass: (a) `{"worst":0,"opaqueInside":true,"leaks":0}`, (b) `{"viewWorst":0}` | `ui/tests/e2e/capture-inbox.test.ts:2577` |
| AC-91.11 | the title is still `'four tools'` | pass | `ui/tests/unit/capture-help-content.test.ts:52` |

Every Red and Green receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md) (§MEU-91 Red, §MEU-91 Green backend, §MEU-91 Electron Red, §MEU-91 Green renderer). `red-check.py` accepted every Red receipt (`0 problem(s)`).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s39-91-red","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 4 command, verbatim","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"MEU-91 Red: pytest -k ac_91, MCP and UI Vitest -t AC-91, red-check on the three receipts","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 90bb409 plus the MEU-90 product change and the row 4 tests","output":"pytest 5 failed, 97 deselected (ImportError on EraserAnnotation, eraser_fill, EraserAnnotationIn) | MCP 1 failed, 21 skipped | UI 6 failed, 106 skipped | red-check: 3 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-91-green-backend","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 5a command, verbatim","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"MEU-91 backend Green (domain, sidecar, API, OpenAPI, MCP, adapter, --region fixtures), no renderer change, build, then the Electron Red of AC-91.10","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 90bb409 plus the MEU-90 change and the MEU-91 backend change","output":"pytest 122 passed | export_openapi --check exit 0 | MCP Test Files 1 passed (1), Tests 22 passed (22) | ui/src unchanged | built in 5.01s | Electron AC-91.10 1 failed at expect(errors).toEqual([]), received [\"Invalid overlay marks\"] | red-check: 1 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-91-green-renderer","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 5b command, verbatim","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"MEU-91 renderer Green: Vitest (region pass, annotate, toolbar, hit test, help, help content, page, behaviour), build, the whole capture-inbox.test.ts","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 90bb409 plus the MEU-90 and MEU-91 product change","output":"Vitest Test Files 8 passed (8), Tests 158 passed (158) | built in 7.45s | Electron 36 passed (1.2m) | AC-90.12 (a) {\"worst\":0,\"opaqueInside\":true,\"leaks\":0} (b) {\"viewWorst\":0} | AC-91.10 (a) {\"worst\":0,\"opaqueInside\":true,\"leaks\":0} (b) {\"viewWorst\":0}","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-91-gate-row6","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1 (task.md row 6, verbatim; run 5)","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"D6 session gate at row 6, run 5: identity, static (py-types, py-lint, py-lint-tools, ui-types, ui-lint, mcp-types, task-contract, scope-ast, scope-paths), full (py-tests, ui-tests, mcp-build, mcp-tests, ui-build, ui-harness-build, ui-picker-stub, openapi, state-render), runtime (ui-electron, e2e-repeat), identity-npm, identity-after","phase":"full","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986","output":"scope-paths changed paths: 47 | all steps exit 0 (py-tests exit 1 accepted by the baseline rule: failed=2 outside_baseline=[] errors=0) | pytest 2 failed (AC-24.10, AC-25.10), 687 passed | Vitest Test Files 88 passed (88), Tests 854 passed (854) | MCP Test Files 23 passed (23), Tests 413 passed (413) | openapi --check 0 | state-render Drift check passed | scope-ast 0 problem(s) | scope-paths outside scope: [] | Electron 146 passed | e2e-repeat 20 passed, every run {\"worst\":0,\"opaqueInside\":true,\"leaks\":0} and {\"viewWorst\":0} | identity before == after","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-91-gate-h1-2","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1 *> C:/Temp/av-kit/s39-gate-h1.txt (task.md H1-2, verbatim)","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"D6 session gate re-run at H1-2 after the row 7 hub edits (project artifacts outside INPUT_IDENTITY); the fresh full record","phase":"full","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986","output":"scope-paths changed paths: 54 (the row 7 hub files added) | all steps exit 0 (py-tests exit 1 accepted by the baseline rule: failed=2 outside_baseline=[] errors=0) | pytest 2 failed (AC-24.10, AC-25.10), 687 passed | Vitest Test Files 88 passed (88), Tests 854 passed (854) | MCP Test Files 23 passed (23), Tests 413 passed (413) | openapi --check 0 | state-render Drift check passed | scope-ast 0 problem(s) | scope-paths outside scope: [] | Electron 146 passed | e2e-repeat 20 passed, every run {\"worst\":0,\"opaqueInside\":true,\"leaks\":0} and {\"viewWorst\":0} | identity before == after","fresh":true}
```

### Quality Gate Results

The shared gate is `session-gate.ps1`. It ran at row 6 (run 5 is the passing run) and again at H1-2, and both printed the same `tested_state`. The hub files, the SSOT and these handoffs are project artifacts (`identity.py` `PROJECT_ARTIFACTS`), so H1-6b re-derives that state from the live tree.

The gate script has one plan change, G-1 (Mat approved it in D-24): `mcp-build` runs before `mcp-tests`, because the MCP tests load `mcp-server/dist`. The pytest §Baseline rule is the Session 36 one, unchanged.

| Step | Stage | Exit | Decisive line (H1-2) |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 90bb409…+6ff3a847…b986` |
| py-types, py-lint, py-lint-tools, ui-types, ui-lint, mcp-types, task-contract | static | 0 | pyright 0 errors; ruff, tsc and eslint clean |
| scope-ast | static | 0 | `scope-ast: adapter outside PRODUCT_SCOPE: 0 problem(s)` |
| scope-paths | static | 0 | `changed paths: 54 outside scope: []` |
| py-tests | full | 1 → accepted | `2 failed, 687 passed, 1 warning`; `py-tests baseline rule: failed=2 outside_baseline=[] errors=0` |
| ui-tests | full | 0 | `Test Files 88 passed (88)`, `Tests 854 passed (854)` |
| mcp-build, mcp-tests | full | 0 | `Test Files 23 passed (23)`, `Tests 413 passed (413)` |
| ui-build, ui-harness-build, ui-picker-stub | full | 0 | — |
| openapi | full | 0 | `export_openapi --check` exit 0; H1-4: `added: ['EraserAnnotationIn', 'PixelateAnnotationIn'] removed: [] changed without a new-schema reference: []` |
| state-render | full | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` |
| ui-electron | runtime | 0 | `146 passed (2.9m)` |
| e2e-repeat | runtime | 0 | `20 passed (1.2m)` (AC-90.12 and AC-91.10, `--repeat-each=10`): every run `{"worst":0,"opaqueInside":true,"leaks":0}`, `{"viewWorst":0}` |
| identity-npm | identity | 0 | `@playwright/test@1.62.1`, `electron@42.9.3` |
| identity-after | identity | 0 | `tested_state before == after` |

Row 6 needed five runs. Run 1 failed py-types, which was fixed in `eraser_fill` (D-29). Run 2 failed task-contract because `RECEIPTS_DIR` was not set in the launching shell. Runs 3 and 4 each failed one or two drag-reorder Electron tests outside Capture (AC-49.25 and W2-5, then AC-49.29) that pass in isolation. That was Mat's decision, D-30. The details are in [walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md) §Session gate.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/enums.py` | modified | `AnnotationType.Eraser` → `"eraser"` |
| `packages/core/src/avkit_core/domain/capture.py` | modified | `EraserAnnotation`; the `Annotation` union |
| `packages/core/src/avkit_core/services/capture.py` | modified | sidecar `eraser` from/to wire; `_clamp_annotation` region branch takes the eraser |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `eraser_fill` (`ERASER_SAMPLE`, reads the RGB crop's bytes: D-29), `_apply_eraser`; `apply_region_pass`, `_apply` and `region_clip` take the eraser |
| `packages/api/src/avkit_api/schemas/captures.py`, `routes/captures.py` | modified | `EraserAnnotationIn` in `AnnotationIn`; `_annotations_from_in` |
| `openapi.committed.json` | regenerated | `EraserAnnotationIn`, its two `anyOf` entries and two discriminator mappings |
| `mcp-server/src/toolsets/capture.ts` | modified | `eraserAnn` in the union; description and `ANNOTATE_EXAMPLE` unchanged (D-21) |
| `ui/src/renderer/src/features/capture/capture-region-pass.ts` | modified | `eraserFill`; `isRegionMark` and `applyRegionPass` take the eraser |
| `ui/src/renderer/src/features/capture/capture-annotate.ts` | modified | `eraserSchema` |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modified | `capture-tool-eraser`; `OPTIONS_BY_TOOL_V2` rule 2; `strokeApplies` |
| `ui/src/renderer/src/features/capture/capture-hit-test.ts` | modified | eraser body hit, `Eraser n` label |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx`, `CapturePage.tsx` | modified | `CaptureTool` `'eraser'`; `REGION_MARK_SVG` for the eraser; `createDrawnMark`/`inspectMark` eraser cases |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | `four-tools` title "Annotation tools"; body names the six tools (`HELP_TOOLS`) |
| `tools/capture_bake_fixture.py` | modified | `REGION_IMAGE_MARKS` gains the eraser; five `ERASER_SAMPLE` cases |
| `ui/tests/e2e/fixtures/capture-region-pass.json`, `capture-region-annotated.png` | regenerated (row 5a) | 11 cases, 82,320 B; the annotated PNG carries the eraser (931 B) |
| `tests/unit/test_domain_capture.py`, `test_domain.py` | modified | AC-91.1; TA-1, TA-6 |
| `tests/unit/test_capture_service.py`, `test_capture_adapter.py` | modified | AC-91.2, AC-91.5, AC-91.6 |
| `tests/e2e/test_api_captures.py` | modified | AC-91.3 |
| `mcp-server/tests/capture.test.ts` | modified | AC-91.4 |
| `ui/tests/unit/capture-region-pass.test.ts`, `capture-annotate.test.ts`, `capture-toolbar.test.ts`, `capture-hit-test.test.ts`, `capture-page.test.ts`, `capture-page.behavior.test.ts`, `capture-help-content.test.ts`, `icon-hints.test.ts` | modified | AC-91.4, AC-91.7, AC-91.8, AC-91.9, AC-91.11; TA-2, TA-3, TA-4, TA-7 |
| `ui/tests/e2e/capture-inbox.test.ts`, `test-ids.ts` | modified | AC-91.10; AC-90.12 (a) leak scope (D-27); TA-5 |

Shared by both MEUs (listed here and in the MEU-90 handoff):

| File | Action | Summary |
|------|--------|---------|
| `docs/build-plan/09-screenshot-capture.md`, `06-gui.md`, `gui-actions-index.md`, `build-priority-matrix.md`, `docs/BUILD_PLAN.md` | modified (row 7) | "six tools" wording, the DTO and `AnnotationType` rows, the Plan rows, `capture:tool_pixelate`/`capture:tool_eraser`, matrix 9.23 and 9.24, the Phase 9 line |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `.agent/context/current-focus.md` | modified (H1-3) | MEU-90/91 status and `execution_plan`; the rendered registry; the current focus |
| `docs/execution/plans/2026-10-16-capture-new-marks/` | new | plan, task, walkthrough, `baseline.sha`, `session-gate.ps1` (G-1 from D-24), `identity.py`, `red-check.py`, `scope-ast.py`, `region-pass-probe.py` |

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

None needed. The Codex execution review (`gpt-6.1-sol`, ledger round 1 of 6, `dispatch-20261016192157-3185`, recorded) approved with no blocking finding: [implementation-critical-review.md](2026-10-16-capture-new-marks-implementation-critical-review.md). Its one finding, F1 (Low, non-blocking), says the AC-90.10 deselect sub-check is vacuous. It is deferred, not corrected (see Deferred Items). The first round 1 attempt was refused by the dispatcher on the verdict schema before the ledger recorded it, and the round was resubmitted unchanged in substance; the review file's Orchestrator Note records this.

## Deferred Items

None. The AC-80.8 title still says "the 12 Capture toolbar buttons" while there are now 14, because TA-7 allows only the `NO_SHOT_IDS` lines. It is recorded as a follow-up in [walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md) §MEU-91 Red.

---

## Decision Log

```yaml
decision_log:
  - id: D-28
    stage: execution
    question: "The row 4 AC-91.9 deselect step clicked at (190, 190), which maps to image pixel 8 on the 8 x 8 test image, off the image, so the page ignored it and the chip stayed pressed; is the product or the test wrong?"
    resolution: autonomous
    class: two-way
    chosen: "Correct the test click to (175, 175), which maps to pixel 7: on the image and off the mark; the deselect assertion is unchanged"
    source_tag: Local Canon
    precedents: ["mapPointerWithView rounds 190 / 25 = 7.6 to 8 (CaptureViewport.tsx)", "CapturePage ignores a pointerdown with no image point before the Select branch"]
    research: { engine: none, sources: [] }
    reasoning: "A test-authoring error: the plan's REGION_EDIT asks for a deselect by a click on empty image, and (190, 190) is not on the image. A probe before the fix showed the chip still pressed with the Select tool active; after the fix the deselect really happens. Recorded in walkthrough §MEU-91 Green renderer."
  - id: D-29
    stage: execution
    question: "The row 6 gate's py-types step (pyright) refused eraser_fill's Image.load() pixel access (Optional PixelAccess; a float | tuple pixel type); how is it fixed without changing behaviour?"
    resolution: autonomous
    class: two-way
    chosen: "Read the RGB crop's bytes with area.tobytes() and index (row * width + col) * 3; the same values, no cast or type ignore"
    source_tag: Local Canon
    precedents: ["the crop is already convert('RGB'), so three bytes per pixel", "AGENTS: no type-ignore to silence a checker"]
    research: { engine: none, sources: [] }
    reasoning: "A product change after row 5a, inside PRODUCT_SCOPE (eraser_fill is an allowed name). Afterwards pyright reports 0 errors, test_capture_adapter.py passes 27, and a fresh --region fixture run is byte-identical to the committed fixtures, so the fill values are unchanged. Because it changes tested_state, the gate was re-run (row 6) and H1-2 re-runs it again."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-91 handoff after the row 6 gate and the H1-2 re-run |
