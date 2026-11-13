---
date: "2026-11-13"
project: "capture-redact"
meu: "MEU-103"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-13-capture-redact/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-12-download-audio-extract-MEU-142-handoff.md"
---

# Handoff: 2026-11-13-capture-redact-MEU-103-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-103 `capture-redact-mark`, P2. This is the first of the five capture annotation editor sessions, Sessions 68 to 72 (grouping D-674).

- **The mark.** `RedactAnnotation {x, y, width, height, color = "#000000"}` is a new member of the `Annotation` union, appended after `EraserAnnotation`. `AnnotationType.Redact` (wire `redact`) is appended after `Eraser` (`REDACT_TYPE`, D-679).
- **Every layer reads and writes it.** These all handle it:
  - the sidecar reader and writer (`REDACT_WIRE`; `color` is required on disk, D-682);
  - the clamp (`REDACT_CLAMP`) and the crop's `clip_mark`, which uses the half-open rule (`REDACT_CLIP`, D-675);
  - the Pillow region pass (`REDACT_BAKE`) and its TS preview (`REDACT_PREVIEW`);
  - the API's `RedactAnnotationIn`, whose colour defaults to `#000000` (`REDACT_API`), and the OpenAPI snapshot;
  - the MCP zod union, which forwards the body unchanged (`REDACT_MCP`).
- **The GUI tool.** The Redact button (`capture-tool-redact`, EyeOff) takes Pixelate's slot, so `CaptureTool` keeps 8 members (`REDACT_TOOL`, D-679).
  - The tool has a Solid / Pixelate mode control, Solid on mount and not persisted (`REDACT_MODE`, `MODE_GROUPS`, D-680).
  - With a redaction mark selected, picking the other mode swaps the mark in place as one undo step (`MODE_SWAP`).
  - A redact is a box mark for the MEU-100 handles, and its chip reads `Redact N` (`REDACT_HIT`).
  - A redact or pixelate draws a dashed outline in the Original view only (`REDACT_OUTLINE`, D-684).
- **The rename.** Eraser is now "Smart eraser", with the tooltip hint `Covers an area with the surrounding colour` and chips `Smart eraser N`. Its JSON type stays `eraser` (`SMART_ERASER`, D-683).
- **Help and fixture.** The help body names Redact, its two modes and Smart eraser (`REDACT_HELP`, D-686). The region parity fixture gains 7 `redact-` cases after the crop cases (`REDACT_FIXTURE`, D-685).

The OpenAPI snapshot gains `RedactAnnotationIn` and its two union places (H1-4). No route changes. The MCP audit baseline does not change: `annotate` stays one action.

**Build Plan Section**: bp09, `docs/build-plan/09-screenshot-capture.md` §Redact mark (anchor `redact-mark`), with the build priority matrix row 9.29.

**Predecessor**: [MEU-142 handoff](2026-11-12-download-audio-extract-MEU-142-handoff.md), Session 67. The grouping is `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md` (row 44). Its decisions D-158, D-159, D-160, D-674 and D-675 carry.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-13. Codex approved the plan at round 2 (`.agent/context/handoffs/2026-11-13-capture-redact-plan-critical-review.md`). Before the review Mat set the execution budget and the rounds ("set token buget for 50M and add 2 more round just so we do no run into limits") and authorized execution ("upon plan approval auto proceed with execution"), D-688.

**Receipts.** A receipt named by its file name alone (`s68-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s68/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **A redact's `color`.**
  - The API body's `RedactAnnotationIn.color` matches `COLOR_PATTERN` and defaults to `#000000` (`schemas/captures.py:149`). `_annotations_from_in` maps it to `RedactAnnotation` (`routes/captures.py:223`).
  - The MCP `redactAnn` (`mcp-server/src/toolsets/capture.ts:183`, in the union at `:201`) leaves `color` optional and forwards the body unchanged, so the server's 422 decides a bad colour.
  - The GUI's `createDrawnMark` writes `REDACT_SOLID_COLOR`, `#000000` (`CapturePage.tsx:324`).
  - `RedactAnnotation.__post_init__` (`domain/capture.py:413`) normalises `color` through `_require_color` and re-raises its error as `AnnotationValidationError`, so a refused colour never reaches the sidecar.
  - `_annotation_to_wire` writes the five keys (`services/capture.py:498`). `_annotation_from_wire` reads exactly those five (`:405-416`) and refuses a missing or extra key with no default.
  - The bake's `_apply_redact` (`avkit_infra/capture/adapter.py:270`) fills with `_color_rgb(color)` at alpha 255. The preview's `redactFill` (`capture-region-pass.ts:122`) fills with `displayHex(color)`'s RGB.
  - No log, stdout or Console line carries a colour string. A refusal's message is `redact size must not be negative` or the existing colour message, with no value in it.
- **A redact's box.** It is written by the API body, the MCP body, the GUI drag and handles, and the crop. It is read by:
  - `_clamp_annotation` (`services/capture.py:2146`, beside pixelate and eraser);
  - `clip_mark`'s `case RedactAnnotation():` (`domain/capture.py:470`), through `_clip_half_open`, with `_HalfOpenMark` (`:478-483`) gaining `RedactAnnotation`;
  - `region_clip` (`adapter.py:201`), which `apply_region_pass` uses in list order (`:286`);
  - `_apply`, which returns the canvas unchanged for a region mark (`:781`).
- **`redactMode`.**
  - It is page state, `useState<RedactMode>('solid')` (`CapturePage.tsx:370`), and is not persisted.
  - The viewport gets `shownRedactMode` (`:1987`): the selected redact's or pixelate's mode, else `redactMode`.
  - `optionGroups(tool, selected, mode)` (`capture-toolbar.ts:140`) reads it.
  - The SegmentedControl (`CaptureViewport.tsx:1183-1192`) calls `onRedactMode`, which is `changeRedactMode` (`CapturePage.tsx:1373-1391`, MODE_SWAP).

AC-103.10 traces one redact through all of these, from the API body to the baked pixels, with a recording wrapper on `apply_region_pass`.

### Row 1's caller grep (S55 RULE-1, S59 RULE-1, S62 RULE-4, S63 RULE-1, S66 RULE-1)

Before its edits, row 1 swept `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` at `3c5676f`. The receipt is `s68-anchors-row1.txt` (238 lines). It has one section for each of these names:
- `clip_mark`, `_clamp_annotation`, `apply_region_pass`, `region_clip`, `_annotation_from_wire` and `_annotation_to_wire`;
- `optionGroups`, `TOOL_BUTTON_IDS`, `TOOLBAR_BUTTONS`, `markLabel` and `applyRegionPass`;
- the literals `capture-tool-pixelate`, `capture-tool-eraser`, `'Eraser'` and `'Pixelate'`, and `CAPTURE_TOOL_PIXELATE`;
- `get_args(Annotation)`, `ANNOTATION_TYPE_MEMBERS`, `ANNOTATION_WIRE` and `annotateInSchema`.

Row 0's `s68-anchors.txt` holds each target's SHA-256 and line endings.

- **Every pin the plan's §Pins table names moved as the table says.** That covers the enum pins in row 1, and in row 2 the AC-130.5 and AC-130.6 kinds, the toolbar, page, icon-hint, hit-test, help and Electron pins.
- **Pins missing from the table.** Two were found while writing, and each moved with its change in row 3 (§Departures 2 and 3):
  - AC-90.11's `stroke="none"` on a loaded pixelate's rect (`capture-page.behavior.test.ts:1692`);
  - the `RESIZE_HELP_SENTENCE` constant that AC-100.10 and AC-101.5 read (`capture-help-content.test.ts:13`).
- **`CAPTURE_TOOL_PIXELATE`** (`test-ids.ts:449`) had no reader. Row 1 removed it.
- **The byte-hash guard.** Row 1 appended the MEU-103 block after the file's last line (`test-ids.ts:507-511`): `CAPTURE_TOOL_REDACT`, `CAPTURE_REDACT_MODE`, `CAPTURE_REDACT_SOLID` and `CAPTURE_REDACT_PIXELATE`. Both edits sit after the hashed prefix. AC-51.6 and AC-81.13 read `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` (`capture-action-row.test.ts:746`). Row 1's own run passed 13 tests (`s68-types-action-row.txt`).

### Row 2's Red tests (S50 RULE-2, S61 RULE-3, S66 RULE-2)

Row 2 wrote three new files, all LF:

- `tests/unit/test_capture_redact.py` (490 lines) covers AC-103.1 to .6, .8 and .10.
- `tests/e2e/test_api_capture_redact.py` (191 lines) covers AC-103.11, .12 and .25.
- `ui/tests/unit/capture-redact.behavior.test.ts` (522 lines) covers AC-103.14 to .22.

It added tests to existing files, each keeping its endings:
- AC-103.13 to `mcp-server/tests/capture.test.ts:1597`;
- AC-103.9 to `ui/tests/unit/capture-region-pass.test.ts:236`;
- AC-103.24 to `ui/tests/e2e/capture-inbox.test.ts:3180`.

It also moved the pins the plan's table names. `id-length.py` found all 66 new pytest ids within red-check's header width (`s68-r2-id-length.txt`).

### Row 3's Green changes (S55 RULE-1)

Row 3 made counted byte replacements, keeping CRLF. The backend changes are in `s68/rows/row3-backend.py` and the UI changes in `s68/rows/row3-ui.py`:

- **Domain.** `RedactAnnotation.__post_init__`, the union member and the `clip_mark` arm.
- **Service.** The sidecar read and write, and the clamp.
- **Adapter.** `_apply_redact` and the region pass.
- **API.** `RedactAnnotationIn` and its mapping, and the regenerated `openapi.committed.json` (7795 to 7847 lines).
- **MCP.** `redactAnn`.
- **UI.**
  - the annotate schema and the `RegionMark` preview;
  - the toolbar spec's `hint`, the Redact button, `TOOL_BUTTON_IDS.redact` and `optionGroups`;
  - the tooltip label (`ToolbarIconButton.tsx:37`);
  - `BoxMark` and the hit-test, and `markLabel`;
  - the mode control and MODE_SWAP;
  - the dashed outline;
  - the help body;
  - the fixture writer's `redact-` cases (`tools/capture_bake_fixture.py`).

**First run.** Row 3's first run exited 1 on ruff alone (`s68/rows/row3-run1.out`): I001 import order and two E501 lines in `tests/e2e/test_api_capture_redact.py`, and one E501 in `tools/capture_bake_fixture.py`. The fixes sorted that test file's imports, wrapped its export post over three lines, and split the fixture comment over two. No assertion changed. The rerun exited 0 (`s68/rows/row3.out`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-103.1 | type | `RedactAnnotation` has the fields `x`, `y`, `width`, `height` and `color`, in that order, with `color` defaulting to `#000000`. `AnnotationType.Redact.value == "Redact"` and `.to_wire() == "redact"`. Row 1 added the names, so it passed where row 2 wrote it | Spec: 09 Mark row | `tests/unit/test_capture_redact.py:59` | ✅ |
| AC-103.2 | behaviour | `RedactAnnotation` refuses a negative size, a non-int number and every bad colour in the input matrix (lone surrogate, control characters, `""`, `#000`, trailing space), each caught and asserted as `AnnotationValidationError`. The good colours are kept | Spec: 09 Mark row; Session 53 RULE-1 | `test_capture_redact.py:93`, `:105` | ✅ |
| AC-103.3 | behaviour | The `Annotation` union's members end `PixelateAnnotation, EraserAnnotation, RedactAnnotation`, in that order | Local Canon: D-679 | `test_capture_redact.py:116` | ✅ |
| AC-103.4 | behaviour | REDACT_WIRE: a redact writes the five keys and reads back equal. A missing `color`, an extra key or a bad value in a sidecar on disk is refused, each its own parametrize id. A sidecar with no redact keeps its bytes through a read and a write | Spec: 09 Mark row; D-682 | `test_capture_redact.py:148`, `:163`, `:178` | ✅ |
| AC-103.5 | behaviour | REDACT_CLAMP: the clamp's fixed-point test covers `"redact"`, and a redact past each edge clamps like a pixelate | Local Canon: D-485 | `test_capture_redact.py:206`; `tests/unit/test_capture_service.py:1208` | ✅ |
| AC-103.6 | behaviour | REDACT_CLIP: `clip_mark` on a redact gives `clipped`, `dropped` or `kept` as an oracle in the test (the half-open box intersection) says, a zero-size mark is kept only while its origin is inside, and each result is a fixed point of `_clamp_annotation`. The oracle disagrees with a closed-box clip on the edge cases | Local Canon: 09 Crop row; D-675 | `test_capture_redact.py:283`, `:310` | ✅ |
| AC-103.7 | check | `assert-never-probe.py`: pyright reports 0 errors on `domain/capture.py`, and exactly one `assert_never` error naming `RedactAnnotation` when the `case RedactAnnotation():` arm is removed from a copy | Local Canon: 09 Crop row | `docs/execution/plans/2026-11-13-capture-redact/assert-never-probe.py` (row 3, `s68-r3-never.txt`); gate `never-probe` | ✅ |
| AC-103.8 | behaviour | REDACT_BAKE: inside `region_clip` each pixel is the colour at alpha 255, including over a semi-transparent source, and outside it each pixel is the source's. Overlapping region marks apply in list order both ways. An arrow over a redact is drawn after it | Spec: 09 Mark row | `test_capture_redact.py:345`, `:375`, `:397` | ✅ |
| AC-103.9 | behaviour | REDACT_FIXTURE and REDACT_PREVIEW: `applyRegionPass` equals the committed Pillow bake byte for byte on every `redact-` case (7 cases). The earlier cases keep their names, order and content | Local Canon: 09 MEU-102 Parity row; D-685 | `ui/tests/unit/capture-region-pass.test.ts:236`; `tests/unit/test_capture_bake_fixture.py` (row 4) | ✅ |
| AC-103.10 | behaviour | One redact traced from the API body through the annotate service, the clamp, the sidecar file on disk, the sidecar read and the bake's `apply_region_pass` (a recording wrapper, which records it exactly once) to the annotated image's pixels | Local Canon: Session 55 RULE-3 | `test_capture_redact.py:430` | ✅ |
| AC-103.11 | behaviour | REDACT_API: annotate accepts a redact with and without `color` and stores `#000000` when it is absent. Each bad row of the input matrix gives 422 in the error envelope, one parametrize id each | Spec: 09 Mark row | `tests/e2e/test_api_capture_redact.py:88`, `:103` | ✅ |
| AC-103.12 | guard | An unknown annotation `type` gives 422 through the API and is refused from a sidecar. It passed at Red and after | Spec: 09 Mark row | `test_api_capture_redact.py:124` | ✅ |
| AC-103.13 | behaviour | REDACT_MCP: annotate forwards a redact with and without `color` unchanged. An extra field, a negative size or a non-int gives a zod error with no backend call | Spec: 09 Mark row; grouping §9.5 | `mcp-server/tests/capture.test.ts:1597` | ✅ |
| AC-103.14 | behaviour | REDACT_TOOL: the tool row holds `capture-tool-redact` (`Redact`) in Pixelate's slot, between Text and Smart eraser, and no `capture-tool-pixelate`. `TOOL_BUTTON_IDS.redact` is that id, and `CaptureTool` has 8 members | Spec: 09 Tool row | `ui/tests/unit/capture-redact.behavior.test.ts:244` | ✅ |
| AC-103.15 | behaviour | SMART_ERASER: the eraser's aria-label is `Smart eraser` and its tooltip `Smart eraser: Covers an area with the surrounding colour`. Its chip is `Smart eraser 1`, and a drawn eraser's JSON type is `eraser` | Spec: 09 Rename row | `capture-redact.behavior.test.ts:268` | ✅ |
| AC-103.16 | behaviour | Redact under Solid, checked on mount, draws one `redact` with `#000000`; under Pixelate it draws one `pixelate` with the current block size | Spec: 09 Tool row | `capture-redact.behavior.test.ts:291` | ✅ |
| AC-103.17 | behaviour | MODE_GROUPS: `optionGroups` gives each row of its rule for the redact tool under both modes, a selected redact (no `color` group), a selected pixelate, the eraser and the crop | Local Canon: D-680 | `capture-redact.behavior.test.ts:319` | ✅ |
| AC-103.18 | behaviour | MODE_SWAP: with a redact selected, Pixelate replaces it on the same box and one Undo restores it; the reverse gives `#000000`. With nothing selected a pick changes no mark. Picking the checked mode leaves the undo stack unchanged | Spec: 09 Tool row | `capture-redact.behavior.test.ts:351` | ✅ |
| AC-103.19 | behaviour | REDACT_HIT: a click inside a redact selects it, a click on the image outside it deselects it, its se handle resizes it as a box, and its chip reads `Redact 1` | Spec: 09 Tool row | `capture-redact.behavior.test.ts:399` | ✅ |
| AC-103.20 | behaviour | REDACT_OUTLINE: a redact's and a pixelate's SVG element has a `stroke-dasharray` in Original and none in Annotated, and an eraser has none. The Pillow bake of a redact has no outline pixel | Spec: 09 Outlines row | `capture-redact.behavior.test.ts:422`; `test_capture_redact.py:397` (`:420`) | ✅ |
| AC-103.21 | behaviour | REDACT_PREVIEW in the editor: the region layer shows the redact's colour inside its box during and after a drag | Spec: 09 Mark row | `capture-redact.behavior.test.ts:445` | ✅ |
| AC-103.22 | behaviour | REDACT_HELP: the help names Redact, its Solid default and its Pixelate mode, and Smart eraser; the resize sentence includes redact; the old `Pixelate and Eraser change the pixels under them` sentence is gone | Local Canon: D-686 | `capture-redact.behavior.test.ts:509` | ✅ |
| AC-103.23 | check | Spec D3: 09's AnnotationType row, the DTO row, REGION_PASS and the Delivered note; 06's tool list; the two gui-index rows. Each file keeps CRLF endings | Local Canon: D3 | row 5's check (`s68-r5-spec.txt`) | ✅ |
| AC-103.24 | behaviour | Electron: the Redact button is visible with Solid checked, and the Smart eraser tooltip shows its hint. The AC-90.12 live Pixelate drag runs through the Redact tool's Pixelate mode | Spec: 09 Tool and Rename rows; grouping §9.6 | `ui/tests/e2e/capture-inbox.test.ts:3180`; gate `ui-electron` | ✅ |
| AC-103.25 | behaviour | Crop and export end to end: a redact straddling the crop crops into a shot whose sidecar holds the clipped redact and whose annotated image is the colour in the clipped box, and the MEU-136 export bakes it the same way. The dropped case leaves no redact | Local Canon: 09 Crop row; grouping §9.5 | `test_api_capture_redact.py:144` | ✅ |
| AC-90 (cross-ref) | regression | MEU-90's region pass and parity fixture are extended, not changed: the 7 `redact-` cases follow the crop cases and every earlier case keeps its name, order and content (`s68/rows/row4.out`). AC-90.10 and AC-90.12 now reach Pixelate through the Redact tool's mode; AC-90.11's loaded pixelate gains the dashed outline (§Departures 2) | plan §Pins that move | `ui/tests/unit/capture-page.behavior.test.ts:1692`; `ui/tests/e2e/capture-inbox.test.ts`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-91 (cross-ref) | regression | MEU-91's eraser keeps its JSON type, fill and options. AC-91.8, AC-91.9 and AC-91.11 read the new name, hint and help list | plan §Pins that move | `ui/tests/unit/capture-toolbar.test.ts`, `capture-hit-test.test.ts`, `capture-help-content.test.ts`; gate `ui-tests` | ✅ |
| AC-100 (cross-ref) | regression | MEU-100's handles move and resize a redact as a box. AC-100.6's loop now draws a redact. AC-100.10 reads the resize sentence that now names redact (§Departures 3) | plan §Pins that move | `capture-page.behavior.test.ts`, `capture-help-content.test.ts:120`; gate `ui-tests` | ✅ |
| AC-101 (cross-ref) | regression | AC-101.5 reads the same resize sentence and keeps its order check (§Departures 3) | §Departures 3 | `capture-help-content.test.ts:128`; gate `ui-tests` | ✅ |
| AC-130 (cross-ref) | regression | MEU-130's crop clips a redact with the half-open rule. AC-130.5's clamp kinds and AC-130.6's union sample gain the redact | plan §Pins that move | `test_capture_service.py:1208`; `tests/unit/test_domain_capture.py`; gate `py-tests` | ✅ |
| AC-39 (cross-ref) | regression | AC-39.8 reads `capture-tool-redact` in the viewport source and no `capture-tool-pixelate` | plan §Pins that move | `ui/tests/unit/capture-page.test.ts`; gate `ui-tests` | ✅ |
| AC-65 (cross-ref) | regression | AC-65.1 to AC-65.3 read the eight tools with Redact in Pixelate's slot, the `mode` option group and the Smart eraser name | plan §Pins that move | `capture-toolbar.test.ts`, `capture-page.behavior.test.ts`; gate `ui-tests` | ✅ |
| AC-80 (cross-ref) | regression | AC-80.8 reads the 14 toolbar buttons with `capture-tool-redact` and the eraser's hint | plan §Pins that move | `ui/tests/unit/icon-hints.test.ts`; gate `ui-tests` | ✅ |
| AC-87 (cross-ref) | regression | AC-87.1's negative reads exactly eight tools in `TOOL_BUTTON_IDS` | plan §Pins that move | `capture-toolbar.test.ts`; gate `ui-tests` | ✅ |
| AC-51.6 (cross-ref) | regression | The test-ids prefix hash is unchanged: `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` | plan §Files Modified (byte-hash guard) | `ui/tests/unit/capture-action-row.test.ts:746`; gate `action-row` | ✅ |
| AC-81.13 (cross-ref) | regression | AC-81.13 reads the same prefix and hash as AC-51.6 | plan §Files Modified (byte-hash guard) | `capture-action-row.test.ts`; gate `action-row` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-103.2 to AC-103.6, AC-103.8, AC-103.10, AC-103.11, AC-103.25 (pytest) | Row 2: `58 failed, 8 passed in 5.68s`, exit 1 (`s68-py-red.txt`). Decisive lines: `assert 422 == 200` ×18; `Failed: DID NOT RAISE AnnotationValidationError` ×13 (row 1's stub); `AnnotationValidationError("unsupported annotation type: 'redact'")` ×7; `unsupported annotation type: <class '...RedactAnnotation'>` ×2; `Expected code to be unreachable, but got: RedactAnnotation(...)` ×14 (`clip_mark`'s `assert_never`); `assert (30, 32, 27, 255) == (18, 171, 52, 255)` (no fill) | Row 3: `383 passed in 16.74s` (`s68-py-green.txt`); gate `py-tests` | `test_capture_redact.py:93-430`, `test_api_capture_redact.py:88-144` |
| AC-103.14 to AC-103.22 (Vitest) | Row 2: `9 failed (9)` in `capture-redact.behavior.test.ts`, exit 1 (`s68-ui-red.txt`). Decisive lines: `capture-tool-redact is in the tools row: expected null not to be null` ×3; `expected [ 'select', 'arrow', 'box', …(5) ] to include 'redact'`; `expected { …, name: 'Eraser' } to deeply equal`; `expected 'Text 1' to be 'Redact 1'`; `expected 'false' to be 'true'`; `expected 'Six annotation tools: Arrow, Box, Hig…' to match /\bRedact\b/` | Row 3: `Tests 230 passed (230)` over 8 files (`s68-ui-green.txt`); gate `ui-tests` | `capture-redact.behavior.test.ts:244-509` |
| AC-103.13 (MCP) | Row 2: `1 failed \| 55 passed (56)`, exit 1 (`s68-mcp-red.txt`): `AssertionError: expected false to be true` (the zod union refused `redact`) | Row 3: `Tests 56 passed (56)` (`s68-mcp-green.txt`); gate `mcp-tests` | `mcp-server/tests/capture.test.ts:1597` |
| AC-103.24 (Electron) | Row 2: `1 failed`, exit 1 (`s68-e2e-red.txt`): `expect(locator).toBeVisible() failed … element(s) not found` at `await expect(redact).toBeVisible()` | Row 3: `46 passed (1.2m)` (`s68-e2e-green.txt`); gate `ui-electron` | `capture-inbox.test.ts:3180` |
| The moved pins (§Pins that move) | Row 2: pytest `2 failed, 198 passed in 11.17s` (AC-130.5, AC-130.6) and Vitest `14 failed \| 188 passed (202)` in 6 files (`s68-pins-red.txt`) | Row 3's guards and gate `py-tests`, `ui-tests` | §Pins that move |
| AC-103.9 | Not in the Red list: it passes after row 4's regeneration | Row 4: `Tests 7 passed (7)` (`s68-r4-region-ts.txt`) and the fixture writer test `5 passed in 0.33s` (`s68-r4-fixture-py.txt`) | `capture-region-pass.test.ts:236` |
| AC-103.7 | Before row 3, on the real file: `no redact case`, exit 1 (`s68-plan-never-pre.txt`) | Row 3: `assert-never-probe: pass` (`s68-r3-never.txt`); gate `never-probe` | `domain/capture.py:470` |
| AC-103.1, AC-103.12 | Row 1 met AC-103.1; AC-103.12 is a guard. Row 2's guard run: `2 passed, 64 deselected in 1.99s` (`s68-r2-guard.txt`) | Row 3 and gate `py-tests` | `test_capture_redact.py:59`, `test_api_capture_redact.py:124` |

- **red-check.** Row 2's check (`s68-red-check.txt`) reads `red-check: 4 receipt(s), 20 required test(s), 0 problem(s)`. Every failing block failed by assertion alone.
- **The 8 passes in the pytest Red run** are AC-103.1, AC-103.12, AC-103.2's good-colour cells and AC-103.6's oracle check, which needs no `clip_mark` arm.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s68-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-13-capture-redact/baseline.ps1 *> C:/Temp/av-kit/s68-baseline.txt (task.md row 0's Validation cell; base runs in C:/Temp/av-kit/s68-base-py.txt, s68-base-ui.txt, s68-base-mcp.txt, s68-base-e2e.txt, s68-base-ui-build.txt, s68-base-mcp-build.txt and s68-base-ruff.txt; outer receipt C:/Temp/av-kit/s68/rows/row0.out)", "scope": "Row 0: the D-688 words on the Status line, the queue, the shapes and absent names (S7), baseline.sha, baseline-dirty.txt, the anchors and line endings, the lock sync, the FFmpeg pair, the base runs, and the red-check, identity, id-length and assert-never-probe selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3c5676f before any row", "output": "budget and execute words found, each USER_EXPLICIT 2026-11-13; queue: {'MEU-91': 'approved', 'MEU-100': 'approved', 'MEU-142': 'approved', 'MEU-103': 'pending'}; 3c5676f is an ancestor of HEAD: True; shapes wrong (S7): []; absent redact/Smart eraser in the 21 capture files; missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; ffmpeg version n8.1.3-27-g8dca1586f4-20261031; base pytest 2369 passed, 37 warnings in 164.74s; base UI Test Files 121 passed (121), Tests 1293 passed (1293); base MCP Test Files 36 passed (36), Tests 525 passed (525); base Electron 45 passed (1.1m); base ruff over packages/ tests/ tools/: Found 10 errors (DEP-1); red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; identity selftest: 0 failure(s); id-length selftest: 4 case(s), 0 wrong; assert-never-probe selftest: 3 toy(s), 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s68-1-types", "command": "rtk proxy uv run pytest tests/unit/test_domain.py tests/unit/test_domain_capture.py (and row 1's guards) --tb=short -q -rfE *> C:/Temp/av-kit/s68-types-py.txt; export_openapi.py --check *> C:/Temp/av-kit/s68-types-openapi.txt; pyright *> C:/Temp/av-kit/s68-types-pyright.txt; ruff check packages/ tests/ tools/capture_bake_fixture.py *> C:/Temp/av-kit/s68-types-ruff.txt; npm --prefix ui run typecheck *> C:/Temp/av-kit/s68-types-ui.txt; npm --prefix ui run test -- tests/unit/capture-action-row.test.ts *> C:/Temp/av-kit/s68-types-action-row.txt (task.md row 1's Validation cell; outer receipt C:/Temp/av-kit/s68/rows/row1.out; sweep C:/Temp/av-kit/s68-anchors-row1.txt)", "scope": "Row 1: RedactAnnotation outside the union as a stub, AnnotationType.Redact and its wire name, the TS RedactAnnotation and RedactMode types, the four MEU-103 test ids, the two enum pins, CAPTURE_TOOL_PIXELATE removed, and the caller sweep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3c5676f plus rows 0 to 1", "output": "298 passed in 9.38s; export_openapi --check exit 0; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; ui typecheck exit 0; capture-action-row Tests 13 passed (13); sweep 238 lines"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s68-2-red", "command": "rtk proxy uv run pytest tests/unit/test_capture_redact.py tests/e2e/test_api_capture_redact.py --tb=short -q *> C:/Temp/av-kit/s68-py-red.txt; npm --prefix ui run test -- tests/unit/capture-redact.behavior.test.ts *> C:/Temp/av-kit/s68-ui-red.txt; npm --prefix mcp-server run test -- tests/capture.test.ts *> C:/Temp/av-kit/s68-mcp-red.txt; playwright capture-inbox.test.ts -g AC-103.24 *> C:/Temp/av-kit/s68-e2e-red.txt; the moved pins *> C:/Temp/av-kit/s68-pins-red.txt; red-check.py with the 20 --require ids *> C:/Temp/av-kit/s68-red-check.txt; the AC-103.1 and AC-103.12 guard *> C:/Temp/av-kit/s68-r2-guard.txt; id-length.py *> C:/Temp/av-kit/s68-r2-id-length.txt (task.md row 2's Validation cell; outer receipt C:/Temp/av-kit/s68/rows/row2.out)", "scope": "MEU-103 Red: AC-103.2 to .6, .8, .10, .11 and .25 in pytest, AC-103.13 in MCP, AC-103.14 to .22 in Vitest and AC-103.24 in Electron against the row 1 code, and the moved pins", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3c5676f plus rows 0 to 2", "output": "pytest 58 failed, 8 passed in 5.68s (child exit 1): assert 422 == 200 x18; DID NOT RAISE AnnotationValidationError x13; unsupported annotation type: 'redact' x7; Expected code to be unreachable, but got: RedactAnnotation(...) x14. Vitest 9 failed (9) (child exit 1): capture-tool-redact is in the tools row: expected null not to be null x3. MCP 1 failed | 55 passed (56) (child exit 1). Electron 1 failed (child exit 1): expect(locator).toBeVisible() failed. Pins: pytest 2 failed, 198 passed; Vitest 14 failed | 188 passed (202). red-check: 4 receipt(s), 20 required test(s), 0 problem(s). Guard: 2 passed, 64 deselected in 1.99s. id-length: 66 test(s), 0 too long"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s68-3-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s68/rows/row3.ps1 > C:/Temp/av-kit/s68/rows/row3.out 2>&1 (task.md row 3's Validation cell: pytest *> C:/Temp/av-kit/s68-py-green.txt, Vitest *> C:/Temp/av-kit/s68-ui-green.txt, MCP *> C:/Temp/av-kit/s68-mcp-green.txt, Electron *> C:/Temp/av-kit/s68-e2e-green.txt, pyright *> C:/Temp/av-kit/s68-r3-pyright.txt, ruff *> C:/Temp/av-kit/s68-r3-ruff.txt, assert-never-probe.py *> C:/Temp/av-kit/s68-r3-never.txt, export_openapi.py --check *> C:/Temp/av-kit/s68-r3-openapi.txt, the UI and MCP typechecks, ui lint and ui build; run 1 in C:/Temp/av-kit/s68/rows/row3-run1.out)", "scope": "MEU-103 Green: REDACT_TYPE, REDACT_WIRE, REDACT_CLAMP, REDACT_CLIP, REDACT_BAKE, REDACT_PREVIEW, REDACT_API, REDACT_MCP, REDACT_TOOL, REDACT_MODE, MODE_GROUPS, MODE_SWAP, SMART_ERASER, REDACT_OUTLINE, REDACT_HIT, REDACT_HELP, and the plan's guards", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3c5676f plus rows 0 to 3", "output": "run 1 exit 1 on ruff alone (I001 and E501); run 2: 383 passed in 16.74s; Vitest Tests 230 passed (230); MCP Tests 56 passed (56); Electron 46 passed (1.2m); pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; assert-never-probe: pass; export_openapi --check exit 0; typecheck, lint and build exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s68-4-fixture", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s68/rows/row4.ps1 > C:/Temp/av-kit/s68/rows/row4.out 2>&1 (task.md row 4's Validation cell: the writer's output checked by C:/Temp/av-kit/s68/rows/row4-check.py before the copy; pytest tests/unit/test_capture_bake_fixture.py *> C:/Temp/av-kit/s68-r4-fixture-py.txt; Vitest capture-region-pass.test.ts *> C:/Temp/av-kit/s68-r4-region-ts.txt; git diff --exit-code on the two region PNGs *> C:/Temp/av-kit/s68-r4-png.txt)", "scope": "Row 4: REDACT_FIXTURE, the 7 redact- cases appended with every earlier case's name, order and content kept, and AC-103.9", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3c5676f plus rows 0 to 4", "output": "baseline cases kept; added: redact-interior, redact-clipped, redact-negative-origin, redact-named, redact-then-pixelate, redact-over-pixelate, redact-then-eraser; 5 passed in 0.33s; Tests 7 passed (7); region PNGs unchanged: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s68-5-spec", "command": "rtk proxy uv run python -c (row 5's checks over 09, 06 and gui-actions-index.md) *> C:/Temp/av-kit/s68-r5-spec.txt (task.md row 5's Validation cell; outer receipt C:/Temp/av-kit/s68/rows/row5.out)", "scope": "Row 5 (D3, AC-103.23): 09's AnnotationType row, DTO row, REGION_PASS list and Delivered (Session 68) note; 06's tool list; the gui-index redact and Smart eraser rows; CRLF kept", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3c5676f plus rows 0 to 5", "output": "{'crlf_only': True, 'delivered_note': True, 'region_pass_list': True, 'dto_row': True, 'gui_list': True, 'index_redact': True, 'index_eraser': True}"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s68-6-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s68/rows/row6.ps1 > C:/Temp/av-kit/s68/rows/row6.out 2>&1 (task.md row 6's Validation cell: meu_status.py render --check *> C:/Temp/av-kit/s68-r6-render.txt and the status read *> C:/Temp/av-kit/s68-r6-status.txt; pre-status copies in C:/Temp/av-kit/s68/pre-status/)", "scope": "Row 6: MEU-103 ready_for_review with its execution_plan, the registry and BUILD_PLAN renders, and grouping row 44 executed with its §9.1 line", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3c5676f plus rows 0 to 6", "output": "Drift check passed - SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content; MEU-103: ready_for_review row 44: ['| 44 | `capture-redact` | MEU-103 | P2 | executed | `docs/execution/plans/2026-11-13-capture-redact/` |']"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s68-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-13-capture-redact/session-gate.ps1 *> C:/Temp/av-kit/s68-gate-h1.txt (task.md row H1-2's Validation cell; step receipts C:/Temp/av-kit/s68-D6-*.txt; outer receipt C:/Temp/av-kit/s68-h12-outer.txt)", "scope": "The plan's full gate: identity before; static py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest, id-length and never-probe; fresh full py-tests, openapi, action-row (the AC-51.6 byte-hash guard), ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render and issues-render; runtime ui-electron; identity after. mcp-audit and build-record skipped by the plan", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "3c5676f050c203d5f82255109a1642c0d920e18f+af1e9df841d5bcdc718eeffbbe91d8583417690e92917461873cf55ecbd933b1", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; task-contract OK: 24 row(s), 22 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 53 outside scope: [] head moved (S3): False, baseline-dirty paths changed since row 0 (S3): []; red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; id-length: 66 test(s), 0 too long; never-probe: unchanged copy 0 errors, mutated copy 1 error naming RedactAnnotation and Never at assert_never, assert-never-probe: pass; py-tests 2435 passed, 37 warnings in 195.15s; openapi exit 0; action-row Tests 13 passed (13); ui-tests Test Files 122 passed (122), Tests 1303 passed (1303); ui-build built in 8.54s; mcp-types and mcp-build exit 0; mcp-tests Test Files 36 passed (36), Tests 526 passed (526); state-render Drift check passed - SSOT loaded (142 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 46 passed (2.1m); tested_state before = after; session-gate: all steps exit 0"}
```

### Quality Gate Results

The H1-2 gate's last line is `session-gate: all steps exit 0` (`s68-gate-h1.txt:127`). Its first run passed.

- **Static.** pyright 0 errors, 0 warnings, 0 informations; ruff over `packages/ tests/ tools/capture_bake_fixture.py` passed (§Departures 1); UI typecheck and lint (`--max-warnings 0`) exit 0. The checks of the plan's own tooling also passed:
  - the task contract;
  - scope-paths (53 changed paths, none outside scope, head not moved);
  - the red-check selftest (49 fixtures, 0 wrong);
  - id-length (66 ids, 0 too long);
  - never-probe (the mutated copy gives exactly one `assert_never` error naming `RedactAnnotation`, AC-103.7).
- **Suites, against the Session 67 baseline.**
  - pytest 2435 passed (2369 + 66 new);
  - Vitest 1303 passed in 122 files (1293 + 10 in one new file and `capture-region-pass.test.ts`);
  - MCP 526 passed (525 + 1);
  - Electron 46 passed (45 + AC-103.24).
  - Every moved pin passes in its own file.
- **Build.** UI build ok (8.54s); MCP typecheck and build exit 0; the OpenAPI check exit 0; the state and known-issues renders match.
- **The byte-hash guard.** `action-row` passed 13 tests: AC-51.6 and AC-81.13 still read `6E569F82…870FF454`.
- **After the gate.** H1-3 (`s68-h13-check.txt`: `MEU-103 ready_for_review: True`, `drift-check.txt`) and H1-4 (`openapi-delta-check.txt`: `added lines: 52 route lines: [] names RedactAnnotationIn: True`) both exit 0. `current-focus.md` and this handoff are outside `tested_state`.
- **Skipped by the plan.** `mcp-audit` (live network and YouTube, which the brief forbids; `annotate` stays one action, so the baseline does not change) and `build-record` (no release and no package build).
- **Identity.** `tested_state` before and after: `3c5676f050c203d5f82255109a1642c0d920e18f+af1e9df841d5bcdc718eeffbbe91d8583417690e92917461873cf55ecbd933b1`. The FFprobe, Deno pin, `uv.lock` and UI lock hashes are the same before and after.
- **Warnings.** pytest reports 37 warnings, the same count as the baseline run (`s68-base-py.txt`); one is Pillow's `getdata` deprecation in `test_capture_export_adapter.py:558`. Vitest's `act(...)` stderr lines come from existing page tests and from the new behaviour file; no test fails on them.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/capture.py`, `domain/enums.py` | modified | `RedactAnnotation`, the union member, the `clip_mark` arm and `_HalfOpenMark`; `AnnotationType.Redact` and its wire name |
| `packages/core/src/avkit_core/services/capture.py` | modified | The sidecar read and write, and the clamp |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `region_clip`'s type, `_apply_redact`, the region pass and `_apply`'s skip |
| `packages/api/src/avkit_api/schemas/captures.py`, `routes/captures.py`, `openapi.committed.json` | modified | `RedactAnnotationIn`, its union place and its mapping; the regenerated snapshot |
| `mcp-server/src/toolsets/capture.ts` | modified | `redactAnn` in the annotate union |
| `ui/src/renderer/src/features/capture/capture-annotate.ts`, `capture-region-pass.ts` | modified | The redact schema, `RedactAnnotation` and `RedactMode`; the preview fill |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx`, `CapturePage.tsx`, `capture-toolbar.ts`, `ToolbarIconButton.tsx`, `capture-hit-test.ts`, `capture-transform.ts`, `capture-help-content.ts` | modified | The Redact tool, mode control and MODE_SWAP, `optionGroups`, the tooltip hint, the hit-test and chips, `BoxMark`, the dashed outline and the help body |
| `tools/capture_bake_fixture.py`, `ui/tests/e2e/fixtures/capture-region-pass.json` | modified | The `redact-` cases (row 3) and the regenerated fixture, 18 to 25 lines (row 4) |
| `ui/tests/e2e/test-ids.ts` | modified | The MEU-103 block appended; `CAPTURE_TOOL_PIXELATE` removed (row 1) |
| `tests/unit/test_capture_redact.py`, `tests/e2e/test_api_capture_redact.py`, `ui/tests/unit/capture-redact.behavior.test.ts` | new | The MEU-103 tests. LF, 490, 191 and 522 lines |
| `tests/unit/test_domain.py`, `test_domain_capture.py`, `test_capture_service.py`, `mcp-server/tests/capture.test.ts`, `ui/tests/unit/capture-toolbar.test.ts`, `capture-page.behavior.test.ts`, `capture-page.test.ts`, `icon-hints.test.ts`, `capture-hit-test.test.ts`, `capture-help-content.test.ts`, `capture-region-pass.test.ts`, `ui/tests/e2e/capture-inbox.test.ts` | modified | The moved pins, AC-103.9, AC-103.13 and AC-103.24 |
| `docs/build-plan/09-screenshot-capture.md`, `06-gui.md`, `gui-actions-index.md` | modified | Row 5's spec text (D3) |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | Only MEU-103's fields and row, and grouping row 44 with its §9.1 line (row 6) |
| `.agent/context/current-focus.md` | modified | Session 68's paragraph (H1-3) |

`git diff --stat 3c5676f`, leaving out `docs/execution/` and the handoffs: `40 files changed, 753 insertions(+), 137 deletions(-)`, plus the three new test files.

Line endings were measured with Python bytes before each edit and kept:

- **CRLF.** Every source file above, `openapi.committed.json`, the fixture JSON and writer, `test-ids.ts`, the Python and Vitest test files that existed, 09, 06, the gui index, the grouping file and `current-focus.md`.
- **LF.** `ui/tests/e2e/capture-inbox.test.ts`, `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md`.
- **New files** are LF.

```diff
 # domain/capture.py, RedactAnnotation and clip_mark (abridged)
+@dataclass(frozen=True, slots=True)
+class RedactAnnotation:
+    x: int
+    y: int
+    width: int
+    height: int
+    color: str = "#000000"
+    def __post_init__(self) -> None:
+        ...
+        if self.width < 0 or self.height < 0:
+            raise AnnotationValidationError("redact size must not be negative")
 ...
+        case RedactAnnotation():
+            return _clip_half_open(mark, left, top, width, height)
 # avkit_infra/capture/adapter.py, the region pass (abridged)
+        elif isinstance(annotation, RedactAnnotation):
+            canvas = _apply_redact(canvas, annotation)
 # schemas/captures.py
+class RedactAnnotationIn(ApiModel):
+    type: Literal["redact"]
 # capture-toolbar.ts
-  'capture-tool-pixelate': { icon: EyeOff, name: 'Pixelate' },
-  'capture-tool-eraser': { icon: Eraser, name: 'Eraser' },
+  'capture-tool-redact': { icon: EyeOff, name: 'Redact' },
+  'capture-tool-eraser': { icon: Eraser, name: 'Smart eraser', hint: 'Covers an area with the surrounding colour' },
```

The excerpt is abridged. The sources are `domain/capture.py:413-436` and `:470`, `adapter.py:270-287`, `schemas/captures.py:149-167` and `capture-toolbar.ts:50-52`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-13-capture-redact-implementation-critical-review.md`, on the ledger loop `s68-execution-2026-11-13-capture-redact` (budget 50,000,000 tokens, cap 8 rounds, D-688). The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | 0 | `3c5676f050c203d5f82255109a1642c0d920e18f+af1e9df841d5bcdc718eeffbbe91d8583417690e92917461873cf55ecbd933b1` |

### Verdict

Approved at round 1 of 8, with 0 findings and 13,213,554 tokens of the 50,000,000 budget. Codex recomputed the same tested_state, re-ran red-check (20 required tests, 0 problems) and assert-never-probe, and accepted all ten questions. The review was validated under `C:/Temp/av-kit` and copied byte for byte. H1-7a (`review-state-check.txt`) and H1-7b (`exec-review.txt`, "approved at round 1 of 8, 0 open blocking findings") exit 0.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `ruff check tools/` fails on 10 errors in `tools/issue_triage*` and `tools/meu_status*` that were there before this session | observation | None | The files are unchanged since 2026-11-03 and outside this session (§Departures 1) |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2) |

### Departures and their basis

1. **ruff's scope (DEP-1, row 1).** The plan's `ruff check packages/ tests/ tools/` fails at baseline on 10 errors that were already in `tools/issue_triage*` and `tools/meu_status*` (`s68-base-ruff.txt`). The check was narrowed to `packages/ tests/ tools/capture_bake_fixture.py`, the one tools file this session edits, in `task.md`, the plan and `session-gate.ps1`. That narrower check passes at baseline. `baseline.ps1`'s recorded, non-fatal base run keeps the wider scope. No AC changed.
2. **AC-90.11's outline pin (DEP-2, row 2 found, row 3 moved).** AC-90.11 asserted that a loaded pixelate's rect has `stroke="none"` in the Original view. `REDACT_OUTLINE` (D-684) outlines every redaction mark. The rect keeps `fill="none"` and now has a `stroke-dasharray` (`capture-page.behavior.test.ts:1705`), and the eraser keeps `stroke="none"`. The pin was missing from the plan's table. It moved in row 3 with the outline, so AC-90.11 stayed green before and after.
3. **The resize help sentence (DEP-3, row 3).** `RESIZE_HELP_SENTENCE` (`capture-help-content.test.ts:13`), which AC-100.10 and AC-101.5 read, now reads `Drag a square handle on a selected box, highlight, redact, pixelate or eraser mark to resize it.`, as `REDACT_HELP` (D-686) requires. Both tests keep their order checks. The row 3 UI probe found it, and it was missing from the plan's table.
4. **AC-103.19's click point (DEP-4, row 3).** Row 2's test clicked CSS (190,190) as empty image. On the test's 8×8 shot at 25 CSS px per pixel, VIEW_MAP (`mapPointerWithView`, MEU-59) rounds 7.6 to pixel 8, which is off the image, so the page ignores the click. Both clicks, in AC-103.19 and in AC-103.18's nothing-selected step, moved to (185,30), which is pixel (7,1): inside the image and outside every box and handle. No assertion and no source changed. An older eraser test uses 175 for the same reason.

Departures 2 to 4 changed test files in a Green row (S2). None changes an AC's text or what it asserts, so none went to the Fable subagent (S12). No execution-stage decision was added: D-679 to D-688 are the plan's, with stage `planning`.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-13 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, row 1's sweep, the Red and Green receipts, the H1-2 gate and the evidence records (H1-6) |
| Reviewed | 2026-11-13 | codex-independent-reviewer | Execution review round 1: approved, 0 findings (H1-7 to H1-7b) |
