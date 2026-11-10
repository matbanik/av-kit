---
date: "2026-11-10"
project: "gui-capture-crop-tool"
meu: "MEU-131"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-08-capture-crop-copy-MEU-130-handoff.md"
---

# Handoff: 2026-11-10-gui-capture-crop-tool-MEU-131-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-131 `gui-capture-crop-tool`. The Capture page gains a Crop tool: a box over the whole image with 8 handles and the outside dimmed; the aspect presets Free, Original, Square, 16:9, 4:3 and 3:2 with a portrait/landscape swap; X, Y, W and H fields with nudges; and modal keys. Enter, a double-click inside the box or Save as copy sends the box to Session 59's `POST /captures/{id}/crop`. The new shot is selected and named on the status line, and the source stays. Crop is disabled while marks are unsaved. The change is renderer-only: no route, schema, Python or MCP file changes.
**Build Plan Section**: [09 §Crop tool](../../../docs/build-plan/09-screenshot-capture.md) (anchor `crop-tool`; the Entry note at `:1079` (D-508) and the Delivered note at `:1081`).
**Predecessor**: [MEU-130 handoff](2026-11-08-capture-crop-copy-MEU-130-handoff.md). This session calls MEU-130's endpoint unchanged and reuses MEU-100's handle helpers from `capture-transform.ts` without changing them.

- **Geometry (rows 1 to 3; D-511 to D-514).** `capture-crop.ts` (new, LF) is pure, with no React or DOM. It exports `CropBox` (`:9`), `AspectPresetId` (`:15`), `ASPECT_PRESETS` (`:18`), `CROP_MIN_PX` (`:28`), `roundHalfUp` (`:31`, `CROP_ROUND`), `cropEligible` (`:40`), `wholeImage` (`:45`), `clampCrop` (`:50`, `CROP_MIN`), `ratioBox` (`:59`), `fitsRatio` (`:64`), `ratioMinBox` (`:84`), `ratioLargestBox` (`:89`), `ratioFeasible` (`:94`) (`CROP_RATIO`), `moveCrop` (`:109`, `CROP_MOVE`), `nudgeCrop` (`:114`, `CROP_NUDGE`), `resizeCrop` (`:122`, `CROP_HANDLES`), `drawCrop` (`:211`, `CROP_DRAW`), `presetRatio` (`:248`), `presetFeasible` (`:273`), `applyPreset` (`:282`) (`CROP_PRESETS`), `swapCrop` (`:305`, `CROP_SWAP`) and `applyField` (`:330`, `CROP_FIELDS`). Every box it returns has whole-pixel sides of at least 8 inside the image, so the endpoint never clamps or refuses it for size.
- **Bar and overlay (row 5; D-523).** `CaptureCropBar.tsx` (new, LF; export `:112`) is a `role="group" aria-label="Crop"` (`:129`) with the Aspect select (`:133`), the swap button, the X/Y/W/H inputs, the `<output>` readout (`:170`), Reset (`:173`), Cancel (`:176`) and Save as copy (`:182`) (`CROP_BAR`). `CaptureCropOverlay.tsx` (new, LF; export `:19`) draws the dim with `fillRule="evenodd"` (`:38`), the box, the thirds while a drag is active (`:54`) and the handles, under `pointer-events-none` (`:30`) (`CROP_LOOK`).
- **Toolbar records (row 1; D-523).** `capture-toolbar.ts` gains `'capture-tool-crop': { icon: Crop, name: 'Crop' }` (`:53`), `CROP_BUTTONS` with `'capture-crop-swap'` (`:82-86`), `TOOL_BUTTON_IDS.crop` (`:98`), the `strokeApplies` case (`:120`) and the leading `optionGroups` check (`:134`) (`CROP_ENTRY`).
- **Command (row 5).** `capture-commands.ts` gains `CaptureCropResult` (`:152`) and `cropCapture` (`:158`), which posts `{x, y, width, height}` to `/captures/${encodeURIComponent(id)}/crop` (`CROP_COMMIT`).
- **Page (row 5; D-509, D-510, D-515 to D-518).** `CapturePage.tsx` holds the reasons (`:93-99`), `CropDrag` (`:105`), `CropState` (`:111`), the crop state and its refs (`:396-400`), the disabled-reason chain (`:430-439`, `CROP_UNSAVED_GATE`), the cancel effect (`:442-452`, `CROP_CANCEL`), the entry toggle (`:656-690`), `chooseCropAspect` (`:694`), `swapCropBox` (`:706`), `setCropBox` (`:717`), `resetCrop` (`:725`), the commit (`:734`, with `Saved crop as …` at `:753`; `CROP_COMMIT`, `CROP_ERRORS`), `handleCropPointer` (`:769`, `CROP_POINTER`) and `handleCropKey` (`:832`, `CROP_MODAL`), routed at `:1005` and `:1523`; the status text at `:1870`; and the viewport's crop props and bar at `:2274-2299`. Review round 1's corrections: `cropCopyRef` (`:400`) carries the copy's id from the commit (`:751`) to its detail load, which then keeps the tool the crop restored even when the copy carries marks (`:563-589`, F2); and Enter on the Crop toggle commits, since keyboard entry keeps focus there (`:857-866`, F1, D-526).
- **Viewport (row 5).** `CaptureViewport.tsx` adds `'crop'` to `CaptureTool` (`:81`), `shiftKey` to the pointer (`:103`, `:425`), the crop props (`:181-189`), the tool buttons disabled by `cropReason` (`:882-937`), the lock (`:947`), the Crop button straight after the lock (`:953-959`), Undo and Redo (`:966`, `:975`), Annotated (`:994`), the bar slot (`:1036`) and the overlay (`:1463`).
- **Tests.** `ui/tests/unit/capture-crop.test.ts` (new, LF): AC-131.1 to .10. `ui/tests/unit/capture-crop-tool.behavior.test.ts` (new, LF): AC-131.11 to .22, with a stubbed `fetch` that records each request and no image leaving the test; review round 1 added an AC-131.17 and an AC-131.18 regression and a `copyMarks` hook in the crop stub (`:232-233`, `:248`, `:304-306`). `ui/tests/e2e/capture-inbox.test.ts`: the crop seam and AC-131.23 and .24 (`CROP_ELECTRON`). `ui/tests/e2e/test-ids.ts`: the additive `// MEU-131 Capture crop tool (additive IDs).` block (`:482`). The pins in §Pins that move: `capture-toolbar.test.ts` `TOOLS` (`:24`), `expectedGroups` (`:39`), the colour invariant (`:102-108`), AC-87.1's eight tools (`:154`) and AC-90.9's loop (`:178`, with `optionGroups('crop', MARKS.pixelate)` asserted `[]` after it); `icon-hints.test.ts` `NO_SHOT_IDS` (`:56`) and AC-80.8's title, 13 → 14 (`:315`).
- **Spec text and records (row 8).** 09's two notes (`:1079`, `:1081`), MEU-131 `ready_for_review` with this plan, and grouping row 60 `executed` (`.agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:110`).

**Execution authorization:** `USER_EXPLICIT`, 2026-11-10. The session prompt opens "Start Session 60: `gui-capture-crop-tool`, MEU-131, P2 band." After the Codex plan review approved at round 3 of 5 ([plan-critical-review.md](2026-11-10-gui-capture-crop-tool-plan-critical-review.md)), Mat ruled through the Human Decision Protocol (`plan_to_exec_gate: human`, plan §User Review Required, "The gate, 2026-11-10"): execution starts with an execution loop of 20,000,000 tokens and 3 rounds, "A: Start, 20M, 3 rounds (Recommended)"; **D-521** "A: Haiku 5.5 (Recommended)"; **D-522** "A: Look (Recommended)"; and the `_meta` known issue, "A: Register it (Recommended)". During execution Mat ruled **D-524** "A: Rebase baseline (Recommended)".

### Where values go (Session 50 RULE-1, Session 53 RULE-1)

- **The box** is four integers. It goes into the fields, the readout and the POST body, and is never logged.
- **The shot id** goes into the URL through `encodeURIComponent` (`capture-commands.ts:158`) and nowhere else. AC-131.17 posts for an id with a space and checks the encoded path.
- **`display_name`** is the new shot's own name, chosen by the endpoint's `CROP_NAME`. It goes on the status line (`CapturePage.tsx:753`), as a convert-on-apply's does.
- **An error message** is the endpoint's fixed text. It reaches the status line and `logRenderer('ERROR', …)` through the page's `run` path, as every capture error does, and names no path (Session 59 AC-130.22). No log line was added (`NO_RAW_CONSOLE`).
- **The D-521 ledger** holds the tool's arguments and results under the receipts folder's `s60/d494` root, which holds only test paths and Pillow images.

### Documented limits

- **No C key.** Crop ships as a button with no shortcut, under 09 Entry's own clause; C comes with MEU-105's tool letters (D-508).
- **The status line is the toast.** The Capture page has no toast component; the new shot is named on the status line (D-516).
- **8 px minimum.** Crop is disabled on a shot under 8 px on a side, and a ratio the image can't hold at 8 px is disabled, not bent (D-511, D-513).
- **Unsaved marks block Crop.** The endpoint carries only saved marks, so Crop is disabled until the marks are saved or discarded (`CROP_UNSAVED_GATE`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-131.1 | unit | `CROP_ROUND`: `roundHalfUp` of 2.5, 3.5, −2.5, −3.5, 2.4999 and 2.5001; `clampCrop` returns integers | Inferred: D-511 | `ui/tests/unit/capture-crop.test.ts:149` | ✅ |
| AC-131.2 | unit | `CROP_MIN`: `cropEligible`; clamping past each edge; a 3×3 box grows to 8×8; the nine-shot sweep passes every box to `endpointAccepts` | Local Canon: `resolve_region`, `CAPTURE_MIN_EDGE_PX`; D-511 | `capture-crop.test.ts:158` | ✅ |
| AC-131.3 | unit | `CROP_HANDLES` over all 8 handles: own edges only, stops at 8 and at the image, never flips | Local Canon: 09 Box; D-511 | `capture-crop.test.ts:178` | ✅ |
| AC-131.4 | unit | `CROP_MOVE`: size kept, stops at each edge | Local Canon: 09 Box | `capture-crop.test.ts:229` | ✅ |
| AC-131.5 | unit | `CROP_DRAW`: four directions give one box; a 3 px drag grows to 8; a click returns `null` | Local Canon: 09 Box; D-511 | `capture-crop.test.ts:238` | ✅ |
| AC-131.6 | unit | `CROP_RATIO`: corner, edge and Shift drags fit the ratio exactly; 14×8 on 400×10; swapped Original on 380×608 is 379×237; every sweep box under a ratio fits | Local Canon: 09 Box; D-512 | `capture-crop.test.ts:249` | ✅ |
| AC-131.7 | unit | `CROP_PRESETS`: ids and labels in order; Square 200×200 at (100, 0); infeasible presets on 8×8 and 400×10; feasibility agrees three ways on every sweep shot | Local Canon: 09 Aspect; D-513 | `capture-crop.test.ts:305` | ✅ |
| AC-131.8 | unit | `CROP_SWAP`: 16:9 → 9:16; Square unchanged; Free swaps about the centre; two infeasible swaps return `null` | Local Canon: 09 Aspect; D-513 | `capture-crop.test.ts:355` | ✅ |
| AC-131.9 | unit | `CROP_FIELDS`: X and W clamp, round and grow; bad text returns `null`; under Square, W sets H and both shrink to fit | Local Canon: 09 Numbers; D-514 | `capture-crop.test.ts:372` | ✅ |
| AC-131.10 | unit | `CROP_NUDGE`: 1 and 10 px each way; stops at an edge | Local Canon: 09 Numbers | `capture-crop.test.ts:394` | ✅ |
| AC-131.11 | unit (page) | `CROP_ENTRY`: placement after the lock, outside the tool group; hint `Crop`, no `aria-keyshortcuts`; opens the bar at 0, 0, 400, 200, Free, view Original; disabled with no shot | Local Canon: 09 Entry; D-508, D-509 | `ui/tests/unit/capture-crop-tool.behavior.test.ts:414`, `:439` | ✅ |
| AC-131.12 | unit (page) | `CROP_UNSAVED_GATE`: dirty disables with `Save or discard your marks first`; Save and Undo-to-saved re-enable; a 5×300 shot is disabled with the size reason | Local Canon: 09 Unsaved marks | `capture-crop-tool.behavior.test.ts:450` | ✅ |
| AC-131.13 | unit (page) | `CROP_POINTER` at zoom 1 and at 0.5: `se`, inside, outside and Shift `se` drags give the expected boxes; no mark is added, selected or moved | Local Canon: 09 Box; D-510 | `capture-crop-tool.behavior.test.ts:477`, `:506`, `:521` | ✅ |
| AC-131.14 | unit (page) | `CROP_LOOK`: `fill-rule="evenodd"` dim; thirds only during a drag; readout `400 × 200 px` across zoom | Local Canon: 09 Look | `capture-crop-tool.behavior.test.ts:547` | ✅ |
| AC-131.15 | unit (page) | `CROP_BAR` aspect: order; Square; 16:9 then swap; X swaps back; the swap hint `Swap portrait and landscape (X)`; infeasible options and swap disabled | Local Canon: 09 Aspect | `capture-crop-tool.behavior.test.ts:578`, `:604` | ✅ |
| AC-131.16 | unit (page) | `CROP_BAR` fields: W 150 + Enter; "abc" reverts; Esc reverts the field only; ArrowUp ±1/±10; surface arrows move X by 1 and 10 | Local Canon: 09 Numbers; D-514 | `capture-crop-tool.behavior.test.ts:625` | ✅ |
| AC-131.17 | unit (page) | `CROP_COMMIT` by Save as copy: one POST to the encoded path with exactly the four integers; the new thumb current, `Saved crop as {display_name}.`, the source listed, the bar gone, the prior tool pressed, also when the copy carries a saved mark (review round 1 F2) | Local Canon: 09 Commit; D-516 | `capture-crop-tool.behavior.test.ts:652`, `:753` | ✅ |
| AC-131.18 | unit (page) | `CROP_COMMIT` by Enter and by a double-click inside; none outside; Enter twice while pending sends one; Enter straight after opening Crop commits, by mouse or by keyboard (review round 1 F1, D-526) | Local Canon: 09 Commit; D-526 | `capture-crop-tool.behavior.test.ts:681`, `:730` | ✅ |
| AC-131.19 | unit (page) | `CROP_ERRORS`: `aria-busy="true"` and `Cropping…` while pending; a 409 and a 422 keep the crop open with the message; the button is enabled again | Local Canon: G35; D-517 | `capture-crop-tool.behavior.test.ts:770` | ✅ |
| AC-131.20 | unit (page) | `CROP_CANCEL`: Esc, Cancel and a second Crop click close with no request and restore the prior tool; Reset keeps the crop open at 0, 0, 400, 200, Free; another shot cancels; Annotated is disabled while the crop is open (D-525) | Local Canon: 09 Cancel; D-510, D-525 | `capture-crop-tool.behavior.test.ts:809`, `:828` | ✅ |
| AC-131.21 | unit (page) | `CROP_MODAL`: `a`, `b`, Delete, Backspace, Ctrl+Z and Ctrl+Y change neither marks nor box; the tool buttons, Undo, Redo, the lock and Annotated are disabled with `Finish or cancel the crop first` | Local Canon: 09 Modal; D-515, D-518 | `capture-crop-tool.behavior.test.ts:852` | ✅ |
| AC-131.22 | unit | The registries: `TOOL_BUTTON_IDS.crop`, the `TOOLBAR_BUTTONS` entry, `optionGroups('crop', …)` is `[]` for every selection, `CROP_BUTTONS['capture-crop-swap']`, and `CROP_BUTTONS` disjoint from the other records | Local Canon: 09 Entry; D-523 | `capture-crop-tool.behavior.test.ts:887` | ✅ |
| AC-131.23 | e2e (Electron) | `CROP_ELECTRON`: a real `se` handle drag with `page.mouse` and Save as copy; the POST body is the dragged box within ±1 px; the new thumb current; the status line names it; the source listed | Local Canon: 09 Tests | `ui/tests/e2e/capture-inbox.test.ts:3111` | ✅ |
| AC-131.24 | e2e (Electron) | The bar in the real app: Square, swap, a W entry, Reset, Cancel, then Crop and Esc; no POST | Local Canon: 09 Tests; §4A E2 | `capture-inbox.test.ts:3144` | ✅ |
| AC-87 (cross-ref) | regression | The Crop button sits outside the Annotation tool group (AC-87.2 holds); AC-87.1's negative now lists exactly the eight tools, with `'crop'` (`capture-toolbar.test.ts:154`) | plan §Pins that move | gate `ui-tests` | ✅ |
| AC-100 (cross-ref) | regression | The mark handles are unchanged: `capture-transform.ts` isn't modified, and `capture-page.behavior.test.ts:3082`'s eight resize handles still pass | plan §Crop geometry | gate `ui-tests` | ✅ |
| AC-65 (cross-ref) | regression | AC-65.1's `expectedGroups` oracle returns `[]` for `'crop'` before its pixelate rule (`capture-toolbar.test.ts:39`), and the colour invariant counts `tool === 'crop'` as having no colour (`:102-108`); every other tool's expectation is unchanged | plan §Pins that move | gate `ui-tests` | ✅ |
| AC-80 (cross-ref) | regression | AC-80.8 reads "the 14 Capture toolbar buttons" (`icon-hints.test.ts:315`), and `NO_SHOT_IDS` gains `capture-tool-crop` (`:56`) | plan §Pins that move | gate `ui-tests` | ✅ |
| AC-90 (cross-ref) | regression | AC-90.9's selected-pixelate loop runs over `TOOLS` without `'crop'` (`capture-toolbar.test.ts:178`), and `optionGroups('crop', MARKS.pixelate)` is asserted `[]` | plan §Pins that move | gate `ui-tests` | ✅ |
| AC-91 (cross-ref) | regression | AC-91.8's loop over `TOOLS` already expects `[]`, which `'crop'` gives; unchanged | plan §Pins that move (plan review round 1 F2) | gate `ui-tests` | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` gains only the additive MEU-131 block (`:482`); AC-51.6 and AC-81.13 pass | plan §Pins that move | gate `ui-tests` | ✅ |
| AC-39 (cross-ref) | regression | The Capture page's E2E suite passes whole, 45 tests (the baseline's 43 plus AC-131.23 and .24) | plan §MEU-131 guards | gate `ui-electron` | ✅ |
| AC-130 (cross-ref) | regression | Session 59's endpoint is called unchanged: no Python, route, schema or OpenAPI file changes, and H1-4's `export_openapi.py --check` exits 0 | [MEU-130 handoff](2026-11-08-capture-crop-copy-MEU-130-handoff.md) | gate `py-tests`, H1-4 | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-131.1 to AC-131.10 | 10 failed of 10 against the row 1 stubs: `right-down: expected null to deeply equal …`; `expected [] to deeply equal ['free','original',…]` | Row 3: pass | `capture-crop.test.ts:149-394` |
| AC-131.11 to AC-131.22 | 16 failed and 1 passed of 17. `the crop bar opens: expected null not to be null` (11); `dirty disables Crop: expected false to be true`; `the marks stay: expected [] to deeply equal [ '60,60,60,60' ]`; `capture-crop-x rendered: expected null not to be null`; `expected undefined to be { …(3) }` | Row 5: pass | `capture-crop-tool.behavior.test.ts:414-887` |
| AC-131.18, AC-131.17 (review round 1 F1, F2) | 2 failed, 17 skipped: `a second Enter after keyboard entry commits: expected [ { …(3) } ] to have a length of 2 but got 1`; `the prior tool survives the copy load: expected 'false' to be 'true'` | `s60-10-green-review-r1`: pass | `capture-crop-tool.behavior.test.ts:730`, `:753` |
| AC-131.23, AC-131.24 | 2 failed: `Error: expect(locator).toBeVisible() failed` on the crop bar after the Crop click | Row 5: pass (45 passed) | `capture-inbox.test.ts:3111`, `:3144` |

- **Row 4's passing test** is AC-131.11's no-shot case (`:433`): the row 1 stub button was already disabled with no shot, which the plan allows. Every failure is an assertion; `red-check.py` required the 14 ids and found 0 problems.
- **Review round 1's Red ran on the approved round 1 renderer**, before `CapturePage.tsx` changed. The mouse half of the AC-131.18 regression passed and its keyboard half failed, which places F1 on keyboard entry; `red-check.py --require AC-131.17 --require AC-131.18` found 0 problems.
- **Row 4 ran on the row 3 renderer.** The row's own check found `ui/src changed since row 3: []` against `row3-ui-src.json` (172 files).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-10-gui-capture-crop-tool/baseline.ps1 *> C:/Temp/av-kit/s60-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "Row 0: rulings, anchors, baseline.sha and baseline-dirty.txt, dependency locks, line endings, hotkey, base suites and the plan-local selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8f29046 before any row", "output": "Base suites: pytest 1564 passed; Vitest 114 files, 1193 passed; MCP 35 files, 485 passed; Electron capture-inbox 43 passed. d494-check selftest: 0 wrong. baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-1-types", "command": "rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/s60-types-tsc.txt; rtk proxy npm --prefix ui run lint *> C:/Temp/av-kit/s60-types-lint.txt; rtk proxy npm --prefix ui run test -- tests/unit/capture-toolbar.test.ts tests/unit/icon-hints.test.ts tests/unit/capture-page.test.ts tests/unit/capture-page.behavior.test.ts *> C:/Temp/av-kit/s60-types-ui.txt (task.md row 1's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "Row 1: the shared names with no behaviour, the six pins of §Pins that move, and the CaptureTool caller grep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8f29046 plus rows 0 to 1", "output": "tsc --noEmit clean; eslint --max-warnings 0 clean; Test Files 4 passed (4); Tests 181 passed (181)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-2-red-geometry", "command": "rtk proxy npm --prefix ui run test -- tests/unit/capture-crop.test.ts *> C:/Temp/av-kit/s60-red-geometry.txt; then red-check.py --require AC-131.1 ... --require AC-131.10 C:/Temp/av-kit/s60-red-geometry.txt *> C:/Temp/av-kit/s60-red-geometry-check.txt (task.md row 2's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "Geometry Red: AC-131.1 to AC-131.10 against the row 1 stubs", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8f29046 plus rows 0 to 2", "output": "tests/unit/capture-crop.test.ts (10 tests | 10 failed). Test Files 1 failed (1); Tests 10 failed (10). Decisive: right-down: expected null to deeply equal …; expected [] to deeply equal ['free','original',…]. red-check: 1 receipt(s), 10 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-3-green-geometry", "command": "rtk proxy npm --prefix ui run test -- tests/unit/capture-crop.test.ts tests/unit/capture-transform.test.ts tests/unit/capture-toolbar.test.ts *> C:/Temp/av-kit/s60-green-geometry.txt; then typecheck *> C:/Temp/av-kit/s60-r3-tsc.txt, lint *> C:/Temp/av-kit/s60-r3-lint.txt and the row3-ui-src.json snapshot (task.md row 3's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "Geometry Green: CROP_ROUND, CROP_MIN, CROP_HANDLES, CROP_MOVE, CROP_DRAW, CROP_RATIO, CROP_PRESETS, CROP_SWAP, CROP_FIELDS and CROP_NUDGE", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8f29046 plus rows 0 to 3", "output": "Test Files 3 passed (3); Tests 23 passed (23). tsc clean; eslint clean. row3-ui-src.json holds 172 ui/src files."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-4-red-page", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test -- tests/unit/capture-crop-tool.behavior.test.ts *> C:/Temp/av-kit/s60-red-page.txt; the row 3 ui/src comparison *> C:/Temp/av-kit/s60-red-tree.txt; the byte-hash guards *> C:/Temp/av-kit/s60-red-bytehash.txt; hotkey-free.py; build; npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts --grep \"AC-131\" *> C:/Temp/av-kit/s60-red-e2e.txt; then red-check.py with the 14 --require ids over both *> C:/Temp/av-kit/s60-red-page-check.txt (task.md row 4's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "Page and Electron Red: AC-131.11 to AC-131.24 against the row 3 renderer, whose Crop button opens nothing", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8f29046 plus rows 0 to 4", "output": "Vitest: Tests 16 failed | 1 passed (17). Decisive: the crop bar opens: expected null not to be null (11); dirty disables Crop: expected false to be true; the marks stay: expected [] to deeply equal [ '60,60,60,60' ]; capture-crop-x rendered: expected null not to be null. Electron: 2 failed, each Error: expect(locator).toBeVisible() failed. ui/src changed since row 3: []. Guards: layout-primitives and capture-action-row 28 passed. F2 free; 0 Electron processes. red-check: 2 receipt(s), 14 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-5-green-page", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test -- tests/unit/capture-crop.test.ts tests/unit/capture-crop-tool.behavior.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/capture-page.test.ts tests/unit/capture-toolbar.test.ts tests/unit/icon-hints.test.ts tests/unit/capture-transform.test.ts tests/unit/capture-hit-test.test.ts tests/unit/capture-action-row.test.ts tests/unit/capture-help-content.test.ts tests/unit/layout-primitives.test.ts *> C:/Temp/av-kit/s60-green-page.txt; then typecheck *> C:/Temp/av-kit/s60-r5-tsc.txt, lint *> C:/Temp/av-kit/s60-r5-lint.txt, build *> C:/Temp/av-kit/s60-r5-build.txt, hotkey-free.py *> C:/Temp/av-kit/s60-r5-hotkey.txt and the whole capture-inbox.test.ts *> C:/Temp/av-kit/s60-green-e2e.txt (task.md row 5's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "Page Green: CROP_ENTRY, CROP_UNSAVED_GATE, CROP_POINTER, CROP_LOOK, CROP_BAR, CROP_COMMIT, CROP_ERRORS, CROP_CANCEL, CROP_MODAL and CROP_ELECTRON", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8f29046 plus rows 0 to 5", "output": "Test Files 11 passed (11); Tests 262 passed (262). tsc clean; eslint --max-warnings 0 clean; renderer built. F2 free: RegisterHotKey succeeded and was released; electron processes from this work tree: 0; hotkey-free: ok. Electron: 45 passed (1.1m)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-6-look", "command": "rtk proxy uv run python docs/execution/plans/2026-11-10-gui-capture-crop-tool/look-check.py *> C:/Temp/av-kit/s60-look-check.txt (task.md row 6's Validation cell, after look-seed.py, look-launch.ps1 and Mat's look in the detached dev app)", "scope": "D-522 A: Mat's look at the crop tool in the dev app on Pillow images, recorded in human-check.md", "phase": "manual", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8f29046 plus rows 0 to 6", "output": "dev-app-procs: 0 of this launch's left, 0 not this launch's. PASS D-522: ruled A. PASS human_message_reference quotes Mat (USER_EXPLICIT <date> '<words>'). PASS decision under A: approve. PASS dev-app-procs.py check --record exit 0. look-check: ok. human-check.md: decision approve; human_message_reference USER_EXPLICIT 2026-11-10 'Approve (Recommended)'."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-7-d494", "command": "rtk proxy uv run python docs/execution/plans/2026-11-10-gui-capture-crop-tool/d494-check.py --plan docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md --root C:/Temp/av-kit/s60/d494/root --report C:/Temp/av-kit/s60-d494-report.txt *> C:/Temp/av-kit/s60-d494-check.txt (task.md row 7's Validation cell, after d494-run.md's steps and one Haiku 5.5 subagent run under D-521 A)", "scope": "D-521 A: a Haiku 5.5 agent, given only avkit_capture's advertised server instructions, description and schema, crops the named panel of a Pillow chart into a new shot through the test harness", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 237732d (D-524) plus rows 0 to 7", "output": "PASS D-521: ruled A. PASS successful crop calls: 1 of 2 ledger entries. PASS remove/flatten/revert/image calls that went through: none. PASS the measured crop's source_id '68b3ea0a-c41b-48c7-87e1-0c3d0b9e55d2' is chart-source's id. PASS IoU of applied {'x': 640, 'y': 120, 'width': 520, 'height': 320} with panel {'x': 640, 'y': 120, 'width': 520, 'height': 320}: 1.000 (needs 0.9). PASS inbox/chart-source.png is byte-identical to the seed. PASS inbox/chart.png exists and is the new shot's file. PASS the report names the new shot id '362e168b-9f90-4bc5-bb7c-c4b586f4e3a7'. d494-check: ok"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-8-records", "command": "task.md row 8 (abridged), run from P:/av-kit: the two 09 notes; tools/meu_status.py update MEU-131 ready_for_review --plan and render; grouping row 60; then its Validation cell through an extracted .ps1 into C:/Temp/av-kit/s60-r8-render.txt and its status check", "scope": "Row 8: the D3 spec text, MEU-131 ready_for_review with this plan, the render, and grouping row 60 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 237732d plus rows 0 to 8", "output": "Drift check passed — SSOT loaded (136 MEUs, 12 phases), rendered regions match on-disk content. ready_for_review ['| 60 | `gui-capture-crop-tool` | MEU-131 | P2 | executed | `docs/execution/plans/2026-11-10-gui-capture-crop-tool/` |'] spec note: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-9-red-review-r1", "command": "rtk proxy npx vitest run tests/unit/capture-crop-tool.behavior.test.ts -t (the two new tests' names), run from P:/av-kit/ui > C:/Temp/av-kit/s60-f1f2-red.txt 2>&1; then red-check.py --require AC-131.17 --require AC-131.18 C:/Temp/av-kit/s60-f1f2-red.txt > C:/Temp/av-kit/s60-f1f2-red-check.txt 2>&1", "scope": "Review round 1 Red: the AC-131.18 keyboard-entry Enter (F1) and the AC-131.17 copy-with-marks tool (F2) regressions against the round 1 renderer", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "237732dab235e7f6a5d478b329822b3601e4f3c4+0afdf67a4e96fb3757e5098d3deab1dbc7d05b2956b97684cc52b1f95d29e6d6 plus the two new tests", "output": "Test Files 1 failed (1); Tests 2 failed | 17 skipped (19). Decisive: a second Enter after keyboard entry commits: expected [ { …(3) } ] to have a length of 2 but got 1; the prior tool survives the copy load: expected 'false' to be 'true'. The vitest run exits 1; red-check: 1 receipt(s), 2 required test(s), 0 problem(s), exit 0."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-10-green-review-r1", "command": "rtk proxy npm --prefix ui run test -- (row 5's 11 unit files) > C:/Temp/av-kit/s60-f1f2-green.txt 2>&1; rtk proxy npm --prefix ui run typecheck > C:/Temp/av-kit/s60-f1f2-tsc.txt 2>&1; rtk proxy npm --prefix ui run lint > C:/Temp/av-kit/s60-f1f2-lint.txt 2>&1", "scope": "Review round 1 Green: cropCopyRef and the Enter-on-toggle commit in CapturePage.tsx (D-526)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "237732dab235e7f6a5d478b329822b3601e4f3c4+b959397ccfcf118bff4060d4202364340f760b52e83ede65958556828618e7f5", "output": "Test Files 11 passed (11); Tests 264 passed (264), row 5's 262 plus the two new tests. tsc --noEmit clean; eslint src/ tests/ --max-warnings 0 clean."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s60-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-10-gui-capture-crop-tool/session-gate.ps1 *> C:/Temp/av-kit/s60-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'tested_state', '_sha256 ', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "H1-2: the registered D6 gate on the whole tree", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "237732dab235e7f6a5d478b329822b3601e4f3c4+b959397ccfcf118bff4060d4202364340f760b52e83ede65958556828618e7f5", "output": "baseline failures excused: py [], ui [], mcp [], e2e []; py-types, py-lint, openapi, mcp-audit, build-record and package-build skipped with reasons; identity-before exit=0; ui-types exit=0; ui-lint exit=0; task-contract exit=0 (26 rows, 24 fully checked, 2 view_file exempt); scope-paths exit=0 (changed paths: 40, outside scope: [], head moved (S3): False); red-check-selftest exit=0 (40 fixtures, 12 positive, 28 negative, 0 wrong); py-tests exit=0 (1564 passed); ui-tests exit=0 (116 files, 1222 passed); ui-build exit=0; mcp-types exit=0; mcp-build exit=0; mcp-tests exit=0 (35 files, 485 passed); state-render exit=0 (136 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); hotkey-free exit=0 (F2 free, 0 Electron processes); ui-electron exit=0 (45 passed (1.1m)); identity-after exit=0 (tested_state before = after); session-gate: all steps exit 0"}
```

### Quality Gate Results

`s60-gate-h1-2` (H1-2, rerun on the whole tree after review round 1's corrections) is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 26 rows (24 fully checked, H1-5 and H2-1 `view_file` exempt); scope-paths found 40 changed paths (round 1's 38 plus this handoff and `current-focus.md`), none outside scope, and HEAD `237732d` did not move (S3); the red-check selftest read 40 fixtures with 0 wrong.
- **Suites:** pytest 1564 passed, the baseline's count (no Python change); Vitest 1222 passed in 116 files (the baseline's 1193 in 114 plus AC-131.1 to .22, 29 tests in 2 new files, two of them review round 1's regressions); MCP 485 passed in 35 files, the baseline's count; Electron `capture-inbox.test.ts` 45 passed (the baseline's 43 plus AC-131.23 and .24). No baseline failure was excused.
- **Build and state:** the UI build, the MCP typecheck and the MCP build exited 0; the state render (136 MEUs) and the issue render match the files on disk. H1-3's `render --check` and H1-4's `export_openapi.py --check` passed after the gate.
- **Runtime:** F2 was free and no Electron process ran from this work tree before `ui-electron`. The E2E crop seam answers `POST …/crop` inside the renderer with a 1×1 PNG; no test reads or writes the network.
- **Skipped:** `py-types` and `py-lint` (no Python change), `openapi` (no route or schema change; H1-4 checked it after the gate), `mcp-audit` (live network, which the brief forbids), `build-record` (no installer build) and `package-build` (no packaged surface change; MEU-125 ran the package build and its smokes).
- **Identity:** the tested_state was the same before and after the gate: `237732dab235e7f6a5d478b329822b3601e4f3c4+b959397ccfcf118bff4060d4202364340f760b52e83ede65958556828618e7f5`. It is re-derived with `ELECTRON_RUN_AS_NODE` unset, as H1-6b's cell does. The handoffs, reviews, `task.md`, `implementation-plan.md`, `human-check.md`, `d494-run.md` and the other closeout records are artifacts the identity leaves out, so writing them doesn't change it.
- **Round 1's gate.** The rerun wrote to the same receipt paths, so round 1's `s60-gate-h1.txt` and its `s60-D6-*.txt` step receipts were overwritten and can't be shown. Round 1 reviewed that gate at tested_state `237732dab235e7f6a5d478b329822b3601e4f3c4+0afdf67a4e96fb3757e5098d3deab1dbc7d05b2956b97684cc52b1f95d29e6d6`, with the same steps passing: Vitest 1220 in 116 files, scope-paths 38 changed paths, and the other counts as above.

### Row 1's caller and pin grep (S55 RULE-1, S59 RULE-1)

Re-run on the gated tree:

- **`CaptureTool` uses:** `CapturePage.tsx:63`, `:116`, `:254`, `:333`, `:892`, `:966`; `CaptureViewport.tsx:81`, `:127`, `:144`; `capture-toolbar.ts:30`, `:89`, `:90`, `:109`, `:133`; `capture-crop-tool.behavior.test.ts:26`, `:901`; `capture-toolbar.test.ts:18`, `:24`, `:37`. Each handles `'crop'` or is a type position.
- **Tool lists ending in `'eraser'`:** `ui/tests/e2e/capture-inbox.test.ts:876` loops over the mark tools, and leaves crop out on purpose; `ui/tests/unit/capture-page.behavior.test.ts:2972` pairs `capture-tool-eraser` with `'eraser'`. Neither is a pin of all tools.
- **`Object.keys` / `Object.values(TOOL_BUTTON_IDS)`:** `capture-crop-tool.behavior.test.ts:875` (filters out `capture-tool-crop` to list the buttons the crop disables); `capture-toolbar.test.ts:60`, `:151`, `:155`.
- **Counts:** only `capture-page.behavior.test.ts:3082`, which counts eight resize handles, not tools.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/capture/capture-crop.ts` | new | `CROP_ROUND` to `CROP_NUDGE`. LF |
| `ui/src/renderer/src/features/capture/CaptureCropBar.tsx` | new | `CROP_BAR`. LF |
| `ui/src/renderer/src/features/capture/CaptureCropOverlay.tsx` | new | `CROP_LOOK`. LF |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | The crop state, the disabled-reason chain, pointer and key routing, commit, errors and cancel; review round 1's `cropCopyRef` and Enter-on-toggle commit |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | `'crop'`, `shiftKey`, the Crop button, the overlay, the bar slot and the disabled reasons |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modified | The Crop entry, `TOOL_BUTTON_IDS.crop`, `strokeApplies`, `optionGroups`, `CROP_BUTTONS` |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modified | `CaptureCropResult`, `cropCapture` |
| `ui/tests/unit/capture-crop.test.ts` | new | AC-131.1 to .10. LF |
| `ui/tests/unit/capture-crop-tool.behavior.test.ts` | new | AC-131.11 to .22, with review round 1's two regressions and the `copyMarks` stub hook. LF |
| `ui/tests/unit/capture-toolbar.test.ts`, `ui/tests/unit/icon-hints.test.ts` | modified | §Pins that move (row 1) |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | The crop seam, AC-131.23 and .24 |
| `ui/tests/e2e/test-ids.ts` | modified | The additive MEU-131 block |
| `docs/build-plan/09-screenshot-capture.md` | modified | The Entry note (D-508) and the Delivered note (row 8) |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, the grouping file | modified | MEU-131 `ready_for_review`; grouping row 60 `executed` (row 8) |

Line endings were measured with Python bytes before each edit and kept: the CRLF sources, `test-ids.ts`, the two unit pin files, 09 and the grouping stayed CRLF; `capture-inbox.test.ts`, `meu-status.yaml`, `BUILD_PLAN.md` and `meu-registry.md` stayed LF. New files are LF.

```diff
 // capture-commands.ts
+export async function cropCapture(id: string, box: CropBox): Promise<CaptureCropResult> {
+  return apiFetch<CaptureCropResult>(`/captures/${encodeURIComponent(id)}/crop`, {
+    method: 'POST',
+    body: JSON.stringify({ x: box.x, y: box.y, width: box.width, height: box.height }),
+  })
+}
 // capture-toolbar.ts
+  'capture-tool-crop': { icon: Crop, name: 'Crop' },
+export const CROP_BUTTONS = {
+  'capture-crop-swap': { icon: ArrowLeftRight, name: 'Swap portrait and landscape' },
+}
 // CapturePage.tsx
+        setNotice({ shotId: result.item.id, text: `Saved crop as ${result.item.display_name}.` })
```

The excerpt is abridged; `capture-commands.ts:152-168`, `capture-toolbar.ts:53-134` and `CapturePage.tsx:396-866` are the source.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Round 1 ([implementation-critical-review.md](2026-11-10-gui-capture-crop-tool-implementation-critical-review.md)) approved at tested_state `237732dab235e7f6a5d478b329822b3601e4f3c4+0afdf67a4e96fb3757e5098d3deab1dbc7d05b2956b97684cc52b1f95d29e6d6` with two non-blocking findings, F1 (AC-131.18: Enter straight after keyboard entry closed the crop with no POST) and F2 (AC-131.17: a copy that carries marks ended on Select). Both were fixed Red first; the review file's Corrections Applied section is the author's account. Round 2 approved F1 and F2 as `fixed`, with no new findings and `intent_achieved: yes`, at tested_state `237732dab235e7f6a5d478b329822b3601e4f3c4+b959397ccfcf118bff4060d4202364340f760b52e83ede65958556828618e7f5`. The ledger refused round 2 at first on its reserve rule (10,867,306 spent plus the same reserved, over 20,000,000), and Mat added 10,000,000 ("B: +10M, dispatch"). Round 2 used 4,244,246 tokens: 15,111,552 of 30,000,000 over two rounds. During round 2 a parallel session added an untracked proposal, `docs/proposals/2026-11-10-download-logic-divergence-report.md`. The reviewer showed that leaving out only that file restores the gate's exact state, so no Session 60 input changed; the file isn't this plan's and stays out of its commit.

### Verdict

`approved` at round 2 of 6, 0 open findings (H1-7a and H1-7b, on the canonical review copied byte for byte from the validated report).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The C key for Crop and the other tool letters | out-of-scope | MEU-105 | D-404, D-508 |
| GUI image import (drop, button, paste) | out-of-scope | MEU-132, Session 61 `gui-capture-image-import` | D-519 |
| A help-sheet sentence for Crop | out-of-scope | MEU-105 (it rewrites the tool help with the letters) | AC-59.20, AC-60.15, AC-66.16, AC-85.11 and AC-89.8 pin the `four-tools` body |
| Claude Code doesn't show `_meta.action_descriptions` to the model | out-of-scope | Filed at closeout as `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` (P3, open) under D-528, on Mat's plan-gate ruling, "A: Register it (Recommended)"; no fix is planned | `known-issues.yaml` is a gated input outside this plan's scope paths, so it is filed after the review, as Session 59 filed D-507 |
| A change to the `crop` description after the D-521 run | out-of-scope | — | Only on Mat's words (plan §Out of Scope) |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

**Execution notes.**
- **AC-131.20 and CROP_MODAL (D-525).** AC-131.20's text says choosing Annotated cancels the crop, but `CROP_MODAL` (D-518, AC-131.21) disables Annotated while the crop is open, so it can't be chosen. Row 4's test asserts the button is disabled and a click leaves the view on Original (`capture-crop-tool.behavior.test.ts:828`). The cancel effect (`CapturePage.tsx:442-452`) still closes the crop if the view leaves Original by any other path.
- **No-shot reason.** Crop's no-shot reason is the page constant `CROP_NO_SHOT`, `Select a shot first` (`CapturePage.tsx:94`), the same text as the viewport's `NO_SHOT_HINT` (`CaptureViewport.tsx:449`).
- **The Aspect select's layout.** `SelectInput` renders its label above the control. In the bar it sits in a `span` whose child `div` is set to a row (`CaptureCropBar.tsx:130`), so the label and the select share the bar's line. `SelectInput` is unchanged.
- **D-524.** HEAD moved from `8f29046` to `237732d` (Mat's commit `chore(registry): replace Fable 5.1 with Fable 5.2`) before row 7. That commit touched only the six registry and agent files `baseline-dirty.txt` held, each at its recorded SHA-256, and no MEU-131 path. On Mat's ruling `baseline.sha` became `237732d` and the six lines left `baseline-dirty.txt`; the gate script is unchanged.
- **The D-521 run.** One Haiku 5.5 subagent, given only the advertised server instructions, `avkit_capture`'s description and its schema, made one `list` call and one `crop` call with `unit: "px"`, and named the new shot. Its feedback: the description and the server instructions never mention `crop`; `crop`'s inputs appear only in the schema; and the `unit` enum doesn't say which value is the default. The `_meta.action_descriptions.crop` text wasn't in the prompt. The description isn't changed here (plan §Out of Scope).
- **The D-522 look.** Mat looked at the tool in the detached dev app, on Pillow images seeded by `look-seed.py`, and approved ("Approve (Recommended)"). `dev-app-procs.py` recorded the launch's 14 processes and stopped only those.
- **`CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`.** Not seen in this session: no row put an unprobeable file in an inbox.
- **Review round 1 corrections (D-526).** F1 held only for keyboard entry: a mouse click on Crop already moves focus to the draw surface through A-4 (`CaptureViewport.tsx:868-874`). Enter on the Crop toggle now commits; Enter on any other button stays that button's, and Space on the toggle still closes the crop (AC-131.20). F2 is fixed by `cropCopyRef`, which is cleared only when the copy's load lands, so React StrictMode's second effect run still sees it. Only `CapturePage.tsx` and the behaviour test changed.
- **A parallel session's file (D-527).** At 12:46 a parallel session added the untracked `docs/proposals/2026-11-10-download-logic-divergence-report.md`. `identity.py` hashes every untracked file, so the live state became `237732dab235e7f6a5d478b329822b3601e4f3c4+0e4c4be2284fe826582ddb5e079c1efb8c52280ba1a94896060ba8c4a29d59a6`, and H1-6b, rerun after round 2 was recorded here, refused. On Mat's ruling the check ran again with its expected state taken from `identity.py`, imported unchanged, with only that path added to its exclusions in memory. The tree then held 42 paths: the gate's 40, the canonical review (copied after scope-paths ran) and the proposal. The reduced state is exactly the gate's `237732dab235e7f6a5d478b329822b3601e4f3c4+b959397ccfcf118bff4060d4202364340f760b52e83ede65958556828618e7f5`, as Codex's round 2 also showed. The file wasn't opened, moved or changed, and it isn't part of this session's commit.
- **No network.** No row and no gate step made a network request apart from the D-521 subagent's own model calls. Every image is built with Pillow or in the renderer's test setup.

### Departures and their basis

- **D-508.** Crop ships as a button with no C key, under 09 Entry's own clause; the 09 Entry note (`:1079`) records it. C comes with MEU-105.
- **D-516.** 09 asks for "a toast names the new shot". The Capture page has no toast, so the status line names it, as a convert-on-apply does. The Delivered note (`:1081`) records it.

---

## Decision Log

```yaml
decision_log:
  - id: D-524
    stage: execution
    question: "HEAD moved from baseline.sha 8f29046 to 237732d during execution (S3). How does the session go on?"
    resolution: human
    class: two-way
    chosen: "A: baseline.sha becomes 237732d and the six now-committed registry lines leave baseline-dirty.txt; every other line keeps its SHA-256 and the gate script is unchanged"
    source_tag: Human-approved
    precedents:
      - "git show --stat 237732d: chore(registry): replace Fable 5.1 with Fable 5.2, only the six .agent/model-registry.local.* and .claude/.cursor agent files"
      - "baseline-dirty.txt at row 0 held those six paths as dirty; each file at 237732d hashes to its recorded SHA-256"
    research:
      engine: none
      sources: []
    reasoning: "Mat's commit landed exactly the dirty registry content row 0 recorded, byte for byte, and no MEU-131 path. Rebasing the baseline keeps S3's guard for any further move without changing a gated script. B (excuse 237732d inside the gate) changes the gate. Doing nothing stops the session at row 7. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'A: Rebase baseline (Recommended)'"
  - id: D-525
    stage: execution
    question: "AC-131.20 says choosing Annotated cancels the crop, while CROP_MODAL (D-518, AC-131.21) disables Annotated while the crop is open. Which one does row 4's test assert?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_MODAL holds: Annotated is disabled with 'Finish or cancel the crop first', and AC-131.20's test asserts the button is disabled and a click leaves the view on Original. The page still cancels the crop if the view leaves Original by any other path (the effect at CapturePage.tsx:442-452), so CROP_CANCEL's clause stays true as a guard"
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md CROP_MODAL — the Annotated view button is disabled with the reason 'Finish or cancel the crop first'"
      - "implementation-plan.md D-518 — the other tools and the Annotated view are disabled while the crop is open"
      - "ui/tests/unit/capture-crop-tool.behavior.test.ts:828 — AC-131.20's test, written in row 4"
    research:
      engine: none
      sources: []
    reasoning: "The two ACs can't both hold through the button: a disabled button can't be chosen. D-518 is the ruled design, and AC-131.21 tests it. Asserting a cancel on a click would need Annotated enabled, which breaks CROP_MODAL. Keeping the effect means any view change that doesn't come through the button still closes the crop. Doing nothing leaves AC-131.20's text and its test disagreeing in the record. Two-way: one test assertion and one AC sentence."
    human_message_reference: null
  - id: D-526
    stage: execution
    question: "Review round 1 F1: after keyboard entry focus stays on the Crop button, so Enter reaches the button and closes the crop with no POST. Is it fixed by moving focus on entry or by making Enter on the toggle commit?"
    resolution: autonomous
    class: two-way
    chosen: "Enter on the Crop toggle commits while the crop is open; Enter on any other button stays that button's, and Space on the toggle still closes the crop. Focus is not moved on entry"
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md CROP_COMMIT — Enter (focus outside a crop field) commits"
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:868-874 — A-4: a mouse click on a toolbar button focuses the surface; keyboard activation keeps focus on the button"
    research:
      engine: none
      sources: []
    reasoning: "The Crop toggle isn't a crop field, so CROP_COMMIT's Enter applies to it. Moving focus on entry would break A-4's keyboard rule for one button. Space still toggles, as a second Crop click does under AC-131.20. Doing nothing leaves AC-131.18 false for keyboard users. Two-way: one condition in handleCropKey."
    human_message_reference: null
  - id: D-527
    stage: closeout
    question: "After round 2, a parallel session's untracked proposal (docs/proposals/2026-11-10-download-logic-divergence-report.md) changed the live identity, and H1-6b refused. How does closeout check the evidence?"
    resolution: human
    class: two-way
    chosen: "A: rerun H1-6b's checker with the expected state from identity.py with only that path left out, after confirming it is the only path outside the gate's list; the file stays untouched and out of this commit"
    source_tag: Human-approved
    precedents:
      - "the round 2 review's check review-r2-concurrent-input: leaving out only that file restores the gate's exact state"
      - "memory parallel-sessions-share-main: another session can write into main; use exact scope in a dirty tree"
    research:
      engine: none
      sources: []
    reasoning: "The file isn't this session's, so moving or deleting it isn't the session's to do. Rerunning the gate would count it outside scope. Leaving out only that one path proves every Session 60 input is unchanged. Doing nothing leaves the refused receipt and stops closeout. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'A: Exclude it (Recommended)'"
  - id: D-528
    stage: closeout
    question: "Claude Code doesn't show a model _meta.action_descriptions, where each MCP action's text lives (found while planning D-521). Register it as a known issue, or leave it as the plan's observation?"
    resolution: human
    class: two-way
    chosen: "A: register it as MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL, P3, open, linked to MEU-131, no fix planned; filed in known-issues.yaml at closeout"
    source_tag: Human-approved
    precedents:
      - "mcp-server/src/toolsets/registry.ts:599-610: action text is registered only under _meta.action_descriptions"
      - "C:/Temp/av-kit/s60-plan-d494-describe.txt: the crop text sits under the heading not shown to the agent"
      - "plan User Review Required, The gate, 2026-11-10: Mat's ruling"
    research:
      engine: none
      sources: []
    reasoning: "The session is renderer-only and changes no MCP text, so the gap is out of scope. Registering keeps the probe and the D-521 run's feedback for a plan of its own. Doing nothing leaves it in a plan note the register doesn't show. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-10 plan gate 'A: Register it (Recommended)'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-10 | claude-code-local (Claude Opus 5.5) | Initial MEU-131 handoff after the H1-2 gate |
| Corrections | 2026-11-10 | claude-code-local (Claude Opus 5.5) | Review round 1 F1 and F2 fixed Red first (D-526); the H1-2 gate rerun at the new tested_state; awaiting the round 2 recheck |
| Approved | 2026-11-10 | codex-independent-reviewer (recorded by claude-code-local) | Execution review round 2 approved, F1 and F2 fixed, 0 open findings |
