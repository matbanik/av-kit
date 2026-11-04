---
date: "2026-10-16"
project: "capture-new-marks"
meu: "MEU-90"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: ".agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-84-handoff.md"
---

# Handoff: 2026-10-16-capture-new-marks-MEU-90-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-90 — `capture-pixelate-mark`. A `pixelate` rectangle mark that turns the area under it into a mosaic.
**Build Plan Section**: [09 §Pixelate mark](../../../docs/build-plan/09-screenshot-capture.md#pixelate-mark), matrix 9.23.
**Predecessor**: [MEU-84 handoff](2026-10-14-capture-render-fidelity-MEU-84-handoff.md) (Session 36, the last capture handoff on `main`).

The pixelate mark travels every layer the four drawn marks do:

- **Domain, sidecar and transport.** `PixelateAnnotation(x, y, width, height, block_size)` is in the `Annotation` union, with `PIXELATE_BLOCK` (2 to 100, default 10). It is in the sidecar (`block_size` always written), the API (`PixelateAnnotationIn`, `extra="forbid"`, default 10), `openapi.committed.json`, the MCP Zod union (`block_size` optional), and the renderer Zod union (`block_size` required).
- **Bake.** `CaptureAdapter.bake` runs `REGION_PASS` first (`apply_region_pass`: region marks in list order) and then paints the drawn marks on top. `_apply_pixelate` is `PIXELATE_BAKE`: a per-band Pillow `reduce`, then `NEAREST` up by the block size. Save, Apply to image and the MCP flatten all go through this bake (D-22).
- **Editor.** The Pixelate tool button (`capture-tool-pixelate`, lucide `Grid3x3`) and the Block size field (`capture-block-size`, `BLOCK_CONTROL`, Mat's choice D-16). The live mosaic is a `capture-region-layer` canvas under the SVG (`REGION_PREVIEW`), fed by the TS `applyRegionPass` (`PIXELATE_QUANT`, Pillow's integer box reduce transcribed exactly). A pixelate renders as a transparent `<rect>` (`REGION_MARK_SVG`), and it is selected and moved like a box (`REGION_EDIT`).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md) §MEU-90. **Execution authorization:** `USER_EXPLICIT` 2026-10-16 "@.agent/workflows/execution-session.md  Session 39 as per session grouping" ([walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md) §Execution message). The base is `main` `90bb409`, with Sessions 34 and 36 merged on Mat's direction.

**Test amendments applied (approved in the plan; TA-6 and TA-7 approved by Mat in D-24):** the pixelate parts of TA-1 to TA-7. No other test assertion changed, apart from the AC-90.10 Red-test correction (D-26) and the AC-90.12 leak scope (D-27), which are both in this handoff's Decision Log.

This handoff also carries the session's shared gate record and the gate decision (D-30), since the gate covers both MEUs.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-90.1 | unit | `PixelateAnnotation` constructs with `PIXELATE_BLOCK` values; `AnnotationType.Pixelate.to_wire() == "pixelate"` (TA-1); block 1, 101, `True`, `2.0` and a negative width are refused | Spec 09:808; `REGION_DTO` | `tests/unit/test_domain_capture.py::test_ac_90_1_pixelate_annotation_and_block_bounds` | ✅ |
| AC-90.2 | unit | Sidecar round-trip with `block_size` written; extra key ignored; `_clamp_annotation` clamps like a `rect`; a missing `block_size` is the "missing annotation field" error | Spec 09:808, 09:337; D-23 | `tests/unit/test_capture_service.py::test_ac_90_2_pixelate_sidecar_round_trip_and_clamp` | ✅ |
| AC-90.3 | integration | API annotate with and without `block_size` (default 10 echoed, sidecar holds it); `PixelateAnnotationIn` bounds in `openapi.committed.json`; 422 for block 1 and 101, an extra `color` and a missing `width` | Spec 09:808; `PIXELATE_BLOCK` | `tests/e2e/test_api_captures.py::test_ac_90_3_annotate_pixelate_round_trip_and_bounds`; gate `openapi` | ✅ |
| AC-90.4 | unit | MCP annotate accepts a pixelate with and without `block_size` and forwards it unchanged; bounds equal the committed OpenAPI; block 1 and `color` refused. Renderer Zod parity | Spec 09:811; `PIXELATE_BLOCK` | `mcp-server/tests/capture.test.ts` `AC-90.4 …`; `ui/tests/unit/capture-annotate.test.ts` `AC-90.4 …` | ✅ |
| AC-90.5 | unit | The bake equals `PIXELATE_QUANT` exactly and is within 1 of the exact mean; blocks uniform; outside byte-equal; empty case unchanged; JPEG and WebP originals; block 1 fails the uniform check | Spec 09:809, 09:811 | `tests/unit/test_capture_adapter.py::test_ac_90_5_pixelate_bake_equals_pixelate_quant` | ✅ |
| AC-90.6 | unit | `REGION_PASS`: a rect over a pixelate keeps its stroke colour in either list position; drawn-only list unchanged; plain list order differs | D-10 | `test_capture_adapter.py::test_ac_90_6_region_pass_runs_before_drawn_marks` | ✅ |
| AC-90.7 | unit | TS `applyRegionPass` equals `expected` on every channel for every pixelate case (`pixelate-repeat-overlap` included); `regionClip`; drawn marks ignored; comparator self-check | D-12; `PIXELATE_QUANT` | `ui/tests/unit/capture-region-pass.test.ts` `AC-90.7 …` (3) | ✅ |
| AC-90.8 | unit | `write_region_fixture` reproduces the committed `capture-region-pass.json`; the committed annotated PNG equals a fresh bake; block 11 differs; `--region` writes only the region set | D-12 | `tests/unit/test_capture_bake_fixture.py::test_ac_90_8_region_fixture_reproduces_the_committed_set`, `::test_ac_90_8_main_region_writes_only_the_region_set` | ✅ |
| AC-90.9 | unit | `TOOL_BUTTON_IDS.pixelate`, icon and name; `optionGroups` follows `OPTIONS_BY_TOOL_V2` (TA-2); not the Session 34 `['color', 'stroke']` fallthrough | `TOOLS_ADDED`; `OPTIONS_BY_TOOL_V2` | `ui/tests/unit/capture-toolbar.test.ts` `AC-90.9 …`; TA-2 `AC-65.1 …` | ✅ |
| AC-90.10 | integration | Pixelate drag makes one block-10 mark "Pixelate 1"; Block size 24 applies as one undo step, 1 and 101 change nothing; click selects; body drag moves; Delete in the field keeps the mark; Save sends `REGION_DTO`; a zero-size drag makes no mark | `TOOLS_ADDED`; `BLOCK_CONTROL`; `REGION_EDIT` | `ui/tests/unit/capture-page.behavior.test.ts` `AC-90.10 …`; `ui/tests/unit/capture-hit-test.test.ts` `AC-90.10 …` (`REGION_EDIT` units) | ✅ |
| AC-90.11 | integration | `capture-region-layer` in the Original view only; one transparent `<rect data-annotation-type="pixelate">`; never a `<text>` | `REGION_PREVIEW`; `REGION_MARK_SVG` | `capture-page.behavior.test.ts` `AC-90.11 …` | ✅ |
| AC-90.12 | integration | Electron `REGION_PIXEL_ORACLE` (a), (b) and (c) for the pixelate of `REGION_IMAGE_MARKS` | Spec 09:810, 09:811 | `ui/tests/e2e/capture-inbox.test.ts` `AC-90.12 REGION_PIXEL_ORACLE …` (also in the gate's `e2e-repeat`, 10×) | ✅ |
| AC-90.13 | integration | Flatten with a pixelate bakes the mosaic (uniform blocks, outside unchanged); without the mark the rectangle is unchanged | Spec 09:808; D-22 | `tests/e2e/test_api_capture_flatten.py::test_ac_90_13_flatten_bakes_the_mosaic` | ✅ |
| AC-91 (cross-ref) | — | Owned by MEU-91 (AC-91.1 to AC-91.11) | plan MEU-91 | [MEU-91 handoff](2026-10-16-capture-new-marks-MEU-91-handoff.md) | see MEU-91 |
| AC-39 (cross-ref) | regression | AC-39.8 tool id list in the viewport, amended by TA-3 (`capture-tool-pixelate`, and `capture-tool-eraser` in MEU-91) | plan `TEST_AMENDMENTS` | `ui/tests/unit/capture-page.test.ts` `AC-39.8 …` | ✅ |
| AC-59 (cross-ref) | regression | AC-59.16 MCP annotate description and example, unaffected (D-21: description and `ANNOTATE_EXAMPLE` unchanged) | walkthrough §Census | `mcp-server/tests/capture.test.ts` `AC-59.16 …` (gate `mcp-tests`) | ✅ |
| AC-65 (cross-ref) | regression | AC-65.1 and AC-65.3 options row (TA-2, TA-4: `block` group for Pixelate only); AC-65.4 NO_OVERFLOW tool loop with `pixelate` (TA-5) | plan `TEST_AMENDMENTS` | `capture-toolbar.test.ts` `AC-65.1 …`; `capture-page.behavior.test.ts` `AC-65.3 …`; `capture-inbox.test.ts` `AC-65.4 …` | ✅ |
| AC-80 (cross-ref) | regression | AC-80.8 disabled-tool hint, amended by TA-7 (`NO_SHOT_IDS` gains `capture-tool-pixelate`) | D-24 | `ui/tests/unit/icon-hints.test.ts` `AC-80.8 …` | ✅ |
| AC-82 (cross-ref) | regression | AC-82.5 `TEXT_FIXTURE` freshness: `write_fixture` and the default `main` are unchanged, so the text fixtures are never rewritten | plan Files Modified (`tools/capture_bake_fixture.py`) | `tests/unit/test_capture_bake_fixture.py::test_ac_82_5_writer_reproduces_the_committed_pngs` and the other two `test_ac_82_5_*` (gate `py-tests`) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-90.1, AC-90.2, AC-90.5, AC-90.8 (2), AC-90.13 | `E   ImportError: cannot import name 'PixelateAnnotation' from 'avkit_core.domain.capture'` (declared new) | pass | `tests/unit/test_domain_capture.py:406`; `tests/unit/test_capture_service.py:1116`; `tests/unit/test_capture_adapter.py:962`; `tests/unit/test_capture_bake_fixture.py:87`, `:126`; `tests/e2e/test_api_capture_flatten.py:653` |
| AC-90.6 | `E   ImportError: cannot import name 'apply_region_pass' from 'avkit_infra.capture.adapter'` | pass | `test_capture_adapter.py:1004` |
| AC-90.3 | `E   ImportError: cannot import name 'PixelateAnnotationIn' from 'avkit_api.schemas.captures'` | pass | `tests/e2e/test_api_captures.py:1056` |
| AC-90.4 (MCP) | `AssertionError: expected false to be true` (`captureSchema.safeParse(body).success`) | pass | `mcp-server/tests/capture.test.ts:479` |
| AC-90.4 (renderer) | `AssertionError: expected null not to be null` (`parseAnnotateBody` refuses the pixelate) | pass | `ui/tests/unit/capture-annotate.test.ts:72` |
| AC-90.7 (3) | `Error: Cannot find module '../../src/renderer/src/features/capture/capture-region-pass'` (declared new) | pass | `ui/tests/unit/capture-region-pass.test.ts:102`, `:121`, `:131` |
| AC-90.9 | `AssertionError: expected undefined to be 'capture-tool-pixelate'` | pass | `ui/tests/unit/capture-toolbar.test.ts:137` |
| AC-90.10 | `expected 'Text 1' to be 'Pixelate 1'` (hit test); `expected null not to be null` (no `capture-tool-pixelate`) | pass | `ui/tests/unit/capture-hit-test.test.ts:215`; `ui/tests/unit/capture-page.behavior.test.ts:1580` |
| AC-90.11 | `AssertionError: expected 'false' to be 'true'` (the detail's pixelate is refused; the overlay is never ready) | pass | `capture-page.behavior.test.ts:1636` |
| AC-90.12 | `expect(errors).toEqual([])`, received `["Invalid overlay marks"]` (`REGION_E2E_RED`, row 3a) | pass: (a) `{"worst":0,"opaqueInside":true,"leaks":0}`, (b) `{"viewWorst":0}`, (c) `{"liveRgba":[91,105,151,255],"sourceRgb":[100,110,160]}` | `ui/tests/e2e/capture-inbox.test.ts:2482` |

Every Red and Green receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md) (§MEU-90 Red, §MEU-90 Green backend, §MEU-90 Electron Red, §MEU-90 Green renderer). `red-check.py` accepted every Red receipt (`0 problem(s)`).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s39-90-red","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 2 command, verbatim","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"MEU-90 Red: pytest -k ac_90 over the six Python files, MCP and UI Vitest -t AC-90, red-check on the three receipts","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 90bb409 baseline product code plus the row 2 tests","output":"pytest 8 failed, 109 deselected (ImportError on declared-new names) | MCP Tests 1 failed | 20 skipped | UI Test Files 5 failed (5), Tests 5 failed | 101 skipped | red-check: 3 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-90-green-backend","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 3a command, verbatim","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"MEU-90 backend Green (domain, sidecar, API, OpenAPI, MCP, adapter, --region fixtures), no renderer change, build, then the Electron Red of AC-90.12","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 90bb409 plus the MEU-90 backend change","output":"pytest 117 passed, 1 warning | export_openapi --check exit 0 | MCP Test Files 1 passed (1), Tests 21 passed (21) | no renderer file changed | built in 4.32s | Electron AC-90.12 1 failed at expect(errors).toEqual([]), received [\"Invalid overlay marks\"] | red-check: 1 receipt(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-90-green-renderer","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 3b command, verbatim","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"MEU-90 renderer Green: Vitest (region pass, annotate, toolbar, hit test, help, page, behaviour, gui-actions-audit), build, the whole capture-inbox.test.ts","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 90bb409 plus the MEU-90 product change","output":"Vitest Test Files 7 passed (7), Tests 147 passed (147) | built in 10.48s | Electron 35 passed (1.5m) | AC-90.12 (a) {\"worst\":0,\"opaqueInside\":true,\"leaks\":0} (b) {\"viewWorst\":0} (c) {\"liveRgba\":[91,105,151,255],\"sourceRgb\":[100,110,160]}","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-90-gate-row6","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1 (task.md row 6, verbatim; run 5)","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"D6 session gate at row 6, run 5: identity, static (py-types, py-lint, py-lint-tools, ui-types, ui-lint, mcp-types, task-contract, scope-ast, scope-paths), full (py-tests, ui-tests, mcp-build, mcp-tests, ui-build, ui-harness-build, ui-picker-stub, openapi, state-render), runtime (ui-electron, e2e-repeat), identity-npm, identity-after","phase":"full","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986","output":"scope-paths changed paths: 47 | all steps exit 0 (py-tests exit 1 accepted by the baseline rule: failed=2 outside_baseline=[] errors=0) | pytest 2 failed (AC-24.10, AC-25.10), 687 passed | Vitest Test Files 88 passed (88), Tests 854 passed (854) | MCP Test Files 23 passed (23), Tests 413 passed (413) | openapi --check 0 | state-render Drift check passed | scope-ast 0 problem(s) | scope-paths outside scope: [] | Electron 146 passed | e2e-repeat 20 passed, every run {\"worst\":0,\"opaqueInside\":true,\"leaks\":0} and {\"viewWorst\":0} | identity before == after","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-90-gate-h1-2","command":"$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1 *> C:/Temp/av-kit/s39-gate-h1.txt (task.md H1-2, verbatim)","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"D6 session gate re-run at H1-2 after the row 7 hub edits (project artifacts outside INPUT_IDENTITY); the fresh full record","phase":"full","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986","output":"scope-paths changed paths: 54 (the row 7 hub files added) | all steps exit 0 (py-tests exit 1 accepted by the baseline rule: failed=2 outside_baseline=[] errors=0) | pytest 2 failed (AC-24.10, AC-25.10), 687 passed | Vitest Test Files 88 passed (88), Tests 854 passed (854) | MCP Test Files 23 passed (23), Tests 413 passed (413) | openapi --check 0 | state-render Drift check passed | scope-ast 0 problem(s) | scope-paths outside scope: [] | Electron 146 passed | e2e-repeat 20 passed, every run {\"worst\":0,\"opaqueInside\":true,\"leaks\":0} and {\"viewWorst\":0} | identity before == after","fresh":true}
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
| `packages/core/src/avkit_core/domain/enums.py` | modified | `AnnotationType.Pixelate` → `"pixelate"` |
| `packages/core/src/avkit_core/domain/capture.py` | modified | `PIXELATE_BLOCK_MIN/MAX/DEFAULT`; `PixelateAnnotation`; the `Annotation` union |
| `packages/core/src/avkit_core/services/capture.py` | modified | sidecar `pixelate` from/to wire (`block_size` required, always written); `_clamp_annotation` region branch |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `region_clip`, `_apply_pixelate`, `apply_region_pass`; `bake` runs `REGION_PASS` first; `_apply` skips region marks (`PRODUCT_SCOPE`, proven by `scope-ast`) |
| `packages/api/src/avkit_api/schemas/captures.py`, `routes/captures.py` | modified | `PixelateAnnotationIn` in `AnnotationIn`; `_annotations_from_in` |
| `openapi.committed.json` | regenerated | `PixelateAnnotationIn`, its two `anyOf` entries and two discriminator mappings |
| `mcp-server/src/toolsets/capture.ts` | modified | `pixelateAnn` in the union; description and `ANNOTATE_EXAMPLE` unchanged (D-21) |
| `ui/src/renderer/src/features/capture/capture-region-pass.ts` | new | `PIXELATE_BLOCK`, `isRegionMark`, `regionClip`, `applyRegionPass` (`PIXELATE_QUANT`) |
| `ui/src/renderer/src/features/capture/capture-annotate.ts` | modified | `pixelateSchema` |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modified | `capture-tool-pixelate`; `OptionGroup` `'block'`; `OPTIONS_BY_TOOL_V2` rule 1; `strokeApplies` |
| `ui/src/renderer/src/features/capture/capture-hit-test.ts` | modified | pixelate body hit, `Pixelate n` label |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | `CaptureTool` `'pixelate'`; `capture-block-size`; `REGION_SOURCE`; `REGION_PREVIEW` (`capture-region-layer`); `REGION_MARK_SVG` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | `blockSize`, `changeBlockSize`, `createDrawnMark`/`inspectMark` pixelate cases, `COLOR_FOCUS_IDS` |
| `tools/capture_bake_fixture.py` | modified | `write_region_fixture`, `REGION_CASES`, `REGION_IMAGE_FIXTURE`; `main --region`; `write_fixture` unchanged |
| `ui/tests/e2e/fixtures/capture-region-pass.json`, `capture-region-original.png`, `capture-region-annotated.png` | new | `REGION_FIXTURE`, `REGION_IMAGE_FIXTURE` (rewritten with the eraser in row 5a) |
| `tests/unit/test_domain_capture.py`, `test_domain.py` | modified | AC-90.1; TA-1, TA-6 |
| `tests/unit/test_capture_service.py`, `test_capture_adapter.py`, `test_capture_bake_fixture.py` | modified | AC-90.2, AC-90.5, AC-90.6, AC-90.8 |
| `tests/e2e/test_api_captures.py`, `test_api_capture_flatten.py` | modified | AC-90.3, AC-90.13 |
| `mcp-server/tests/capture.test.ts` | modified | AC-90.4 |
| `ui/tests/unit/capture-region-pass.test.ts` | new | AC-90.7 |
| `ui/tests/unit/capture-annotate.test.ts`, `capture-toolbar.test.ts`, `capture-hit-test.test.ts`, `capture-page.test.ts`, `capture-page.behavior.test.ts`, `icon-hints.test.ts` | modified | AC-90.4, AC-90.9, AC-90.10, AC-90.11; TA-2, TA-3, TA-4, TA-7 |
| `ui/tests/e2e/capture-inbox.test.ts`, `test-ids.ts` | modified | AC-90.12 (`installRegionSeam`, `openRegionShot`); TA-5 |

MEU-91 extends the same files (see its handoff). Shared by both MEUs (listed here and in the MEU-91 handoff):

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

Execution review F1 (Low, non-blocking) is the first of the two observations below; follow-up recommended. Two test-quality observations outside every AC are recorded for a later session in [walkthrough.md](../../../docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md): the AC-90.10 "click on empty image deselects" step passes without the click doing anything, because Undo has already cleared the selection (§MEU-91 Green renderer); and the AC-80.8 title still says "the 12 Capture toolbar buttons" while there are now 14, because TA-7 allows only the `NO_SHOT_IDS` lines (§MEU-91 Red).

---

## Decision Log

```yaml
decision_log:
  - id: D-25
    stage: execution
    question: "Row 0 failed at uv sync because the worktree venv was CPython 3.14 and spacy has no cp314 wheel; how is the environment fixed?"
    resolution: autonomous
    class: two-way
    chosen: "Recreate the gitignored worktree .venv with uv venv --clear --python 3.12.12 and re-run row 0 unchanged"
    source_tag: Local Canon
    precedents: ["Session 36 D-22 (the same fix in the s36 worktree)", "uv.lock resolves for CPython 3.12.12; P:/av-kit/.venv is 3.12.12"]
    research: { engine: none, sources: [] }
    reasoning: "The lockfile already names the interpreter; recreating the venv changes no lockfile, pyproject or test. identity.py binds the Python version, so the gate records it."
  - id: D-26
    stage: execution
    question: "The row 2 AC-90.10 hit-test line expected translateBody to keep the whole rectangle inside the image (x 40), but REGION_EDIT says the existing clamp, which clamps the origin (x 90); which is right?"
    resolution: autonomous
    class: two-way
    chosen: "Correct the test expectation to x 90; the rest of the assertion (size and block_size kept) is unchanged"
    source_tag: Local Canon
    precedents: ["plan REGION_EDIT 'translateBody, existing clamp'", "translateBody clamps the origin with clampImagePoint for rect and highlight (capture-hit-test.ts)"]
    research: { engine: none, sources: [] }
    reasoning: "A test-authoring error in row 2, not a contract change: the plan pins the existing clamp, and rect and highlight behave the same way. Recorded in walkthrough §MEU-90 Green renderer."
  - id: D-27
    stage: execution
    question: "When the eraser joined REGION_IMAGE_MARKS (row 4), AC-90.12 (a) counted the eraser's opaque layer pixels as pixelate leaks; what is the leak rule?"
    resolution: autonomous
    class: two-way
    chosen: "AC-90.12 (a) checks alpha 0 outside every region mark, the same rule as AC-91.10 (a); the comparison inside the pixelate is unchanged"
    source_tag: Local Canon
    precedents: ["plan REGION_PIXEL_ORACLE (a) 'the layer's alpha is 0 outside every rectangle'", "REGION_IMAGE_FIXTURE rewritten with the eraser in row 5a"]
    research: { engine: none, sources: [] }
    reasoning: "The plan's oracle already says 'outside every rectangle'; the row 2 test counted only the pixelate because the fixture held only the pixelate then. Without the change the test would fail on correct eraser pixels. Recorded in walkthrough §MEU-91 Red."
  - id: D-30
    stage: execution
    question: "Gate runs 3 and 4 failed at ui-electron on drag-reorder tests outside Capture (AC-49.25 and W2-5, then AC-49.29), each landing the row one place too far; they pass in isolation and no Session 39 change reaches the queue pages. Re-run, compare against main, fix the drag race, or stop?"
    resolution: human
    class: two-way
    chosen: "Re-run, hands off: reopen DOWNLOAD-QUEUE-DRAG-OVER-MISS with the misses and re-run the gate with no human input on the machine"
    source_tag: Human-approved
    precedents: ["known issue DOWNLOAD-QUEUE-DRAG-OVER-MISS (open, MONITORING): 'reopen with their output on the next miss'", "Session 36 reflection: unrelated E2E failures repeated in isolation before being treated as non-regressions"]
    research: { engine: none, sources: [] }
    reasoning: "Isolated repeats pass (AC-49.25/26 8/8, W2-5 4/4, AC-49.29 20/20), the A-4 diagnostics show the window focused (not the A-7 human-input case), and the plan's S6 any-flake rule covers the Capture e2e-repeat step, which never failed. The fail-fast gate cannot pass with a miss, so the choice between a re-run and a drag-race fix outside the plan was Mat's."
    human_message_reference: "USER_EXPLICIT 2026-10-16 'Re-run, hands off (Recommended)'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-90 handoff after the row 6 gate and the H1-2 re-run |
