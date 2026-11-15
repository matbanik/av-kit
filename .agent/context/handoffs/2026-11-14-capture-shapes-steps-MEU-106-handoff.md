---
date: "2026-11-14"
project: "capture-shapes-steps"
meu: "MEU-106"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-14-capture-shapes-steps/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-14-capture-tool-flow-MEU-143-handoff.md"
---

# Handoff: 2026-11-14-capture-shapes-steps-MEU-106-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-106 `capture-line-ellipse-shapes`. Session 72 adds the Line and the Ellipse to the capture editor as forms of the arrow and the box, with Duplicate. It runs with MEU-107 in one session (D-780), grouping row 48.

- **A line is an arrow with no head (HEAD_FIELD, D-767).** `ArrowAnnotation.head` is `end` (the default), `none` or `both`. The bake draws no head or a head at each end, with the shaft shortened by `arrow_shaft_span` (HEAD_BAKE), and the preview and the hit test follow it (HEAD_PREVIEW, HEAD_HIT).
- **An ellipse is a box with `shape: "ellipse"` (SHAPE_FIELD, D-769).** The bake draws Pillow's ellipse in the box (ELLIPSE_BAKE), the preview an `<ellipse>` (ELLIPSE_PREVIEW), and the hit test the distance to the outline (ELLIPSE_HIT). A crop keeps an ellipse whose box lies inside the closed crop and drops it otherwise, never clipping it (ELLIPSE_CLIP, D-676).
- **Defaults leave the wire unchanged (DEFAULT_OMIT, D-768).** `head: "end"` and `shape: "rect"` are left out of the wire, the sidecar and the API response, so today's sidecars and bakes don't change (AC-106.30).
- **The Head and Shape controls (SHAPE_OPTIONS, D-770, D-771, D-781).** The options row shows Head (End, None, Both) for Arrow and Shape (Rectangle, Ellipse) for Box. The pick is page state, never saved (AC-106.31); with a mark selected it changes that mark.
- **Duplicate (DUPLICATE, D-777).** Ctrl+D copies the selected mark 10 px down and right, keeping it inside the image, through the page-scoped registry entry `capture:duplicate`, and selects the copy.
- **Labels and help.** `markLabel` reads `Line 1` and `Ellipse 1` (MARK_LABELS, D-778); the Annotation tools help names seven tools and holds SHAPES_HELP; `gui-actions-index.md` holds SHAPES_ACTIONS_INDEX and 09 the MEU-106 Delivered (Session 72) note (SHAPES_SPEC).

**Build Plan Section**: bp09, `docs/build-plan/09-screenshot-capture.md` §Line and ellipse and §Step mark, with the Duplicate row and the Crop rows they extend.

**Predecessor**: [MEU-143 handoff](2026-11-14-capture-tool-flow-MEU-143-handoff.md), Session 71b. The grouping is `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md` (row 48). This is the grouping's last session. These decisions carry: D-158 (human, `USER_EXPLICIT` 2026-10-29 "all recommendations are accepted"), D-159, D-160, D-674, D-675, D-676 (human, `USER_EXPLICIT` 2026-11-12 "both recommendations accpeted") and D-678.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-14.
- **The plan review.** Codex approved the plan at round 2 (`.agent/context/handoffs/2026-11-14-capture-shapes-steps-plan-critical-review.md`). Round 1 spent 12,772,041 tokens and found F1 to F4; round 2 spent 4,383,049 and rechecked all four `fixed`. The loop spent 17,155,090 tokens. The review loops have no token budget (`.agent/review-limits.json` `token_budgets: "off"`), so they stop on rounds only.
- **The gate.** Mat accepted every recommendation and said to execute (`USER_EXPLICIT` 2026-11-14 "all recommendations accepted, execute"). That rules the band, D-779 (P2 in both); the split, D-780 (one session); the toolbar route, D-781 (the Head and Shape controls and one Step button after Text with no letter); and execution, D-782, with the gate flags D-768 (DEFAULT_OMIT), D-775 (the two step leaves) and D-777 (the Ctrl+D registry entry) standing as planned.
- **During execution** no ruling was needed. The execution decisions D-783 to D-788 are autonomous and are in the plan's `decision_log`; two of them, D-785 and D-788, move pins the plan didn't list and are reported to Mat (§Departures).

**The band (D-779).** Row 6 set grouping row 48 to P2; `meu-status.yaml` already gave MEU-106 and MEU-107 `band: P2`. `s72-r6-status.txt` reads `band from D-779: P2`, with every key `True`.

**The OpenAPI and MCP change (D-767, D-768, D-769, D-775).** The committed snapshot was regenerated with `tools/export_openapi.py`, not edited by hand. It gains `head` on `ArrowAnnotationIn` and `shape` on `RectAnnotationIn` (`schemas/captures.py:92`, `:106`, each `Field(default=…, exclude_if=…)` so the default is left out of a response), `StepAnnotationIn` (`:173`) in the `AnnotationIn` union (`:187`), and `step_color` and `step_size` on `SettingsPutIn` (`schemas/settings.py:72-73`). `openapi-delta.py` pinned that delta and nothing else: `s72-r2-openapi-delta.txt` and `s72-openapi-delta-check.txt` read `openapi-delta: pass`. The MCP capture schema gains `head` (`mcp-server/src/toolsets/capture.ts:123`), `shape` (`:137`) and the step mark (`:200`, `:219`); `SETTINGS_SCHEMA` and the strict set schema gain the two step leaves (`mcp-server/src/toolsets/settings.ts:88-89`, `:165-166`). No action was added, so the MCP audit baseline doesn't change.

**Receipts.** A receipt named by its file name alone (`s72-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s72/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers, as built | Rule |
|---|---|---|---|
| `head` | the Head control (`CaptureViewport.tsx:1399-1402`, page state `CapturePage.tsx:466`), an agent's `avkit_capture annotate`, the API | the UI schema (`capture-annotate.ts:21`), the MCP schema (`capture.ts:123`), `ArrowAnnotationIn.head` (`schemas/captures.py:92`), `_annotations_from_in` (`routes/captures.py:160`), `_annotation_from_wire` (`services/capture.py:364`), `ArrowAnnotation.head` (`domain/capture.py:303`), the sidecar, `_clip_arrow` (`:626`), `_apply_arrow` (`adapter.py:941`), the preview (`data-head`, `CaptureViewport.tsx:271`) | refused outside the Literal at every boundary; left out at `end` (`_annotation_to_wire`, `services/capture.py:467`); no message names the value |
| `shape` | the Shape control (`CaptureViewport.tsx:1414-1417`, page state `CapturePage.tsx:467`), the agent, the API | the same chain: `capture-annotate.ts:35`, `capture.ts:137`, `schemas/captures.py:106`, `services/capture.py:374`, `RectAnnotation.shape` (`domain/capture.py:326`), `_clip_ellipse` (`:595`) or `_clip_rect` (`:570`), `_apply_rect` (`adapter.py:997`, ellipse `:1008`), the preview `<ellipse>` (`CaptureViewport.tsx:308`) | the same; left out at `rect` (`services/capture.py:480`) |
| A step mark | the Step tool and Duplicate (`CapturePage.tsx`, `nextStepNumber` in `capture-step.ts:37`), the agent, the API | `stepSchema` (`capture-annotate.ts:99`), `stepAnn` (`capture.ts:200`), `StepAnnotationIn` (`schemas/captures.py:173`), `_annotations_from_in` (`routes/captures.py:236`), `StepAnnotation` (`domain/capture.py:468`), `_annotation_from_wire` (`unexpected step field(s)`, `services/capture.py:425`), `_clamp_annotation` (`:2168`), `_clip_step` (`domain/capture.py:609`), `_apply_step` (`adapter.py:890`), the preview, `markLabel` (`capture-hit-test.ts:393`) | strict at every boundary: integer fields refuse `bool`, floats and strings; the colour refuses an empty, control-character and lone-surrogate value; the number stops at 999 (`STEP_NUMBER_MAX`, `capture-step.ts:8`) |
| `step_color`, `step_size` | the options row through STYLE_STORE, the agent's `avkit_settings` set, the Settings API | `SettingsPutIn` (`schemas/settings.py:72-73`), `SettingsService` (`services/settings.py:129-130`), the app database, `fetchCaptureSettings` (`settings-schemas.ts:111-112`), `readToolStyles` (`capture-tool-style.ts:111`), the page | refused at the API (pattern, `StrictInt`, 12 to 200) and in the service; a bad stored value reads back as the default in `readToolStyles` (AC-107.17) |
| The pick | the Head and Shape controls | `createDrawnMark` (`CapturePage.tsx:361`) | page state; never saved (AC-106.31) |

Three traces cover the functions between the user's input and the port with recording fakes (Session 55 RULE-3). AC-106.29 and AC-107.20 are each split into a Python half and an MCP half that share one literal body (D-783, §Departures 1). AC-107.16 traces one step colour commit to the recorded PUT body.

### Row 1's sweep (S55 RULE-1, S59 RULE-1, S62 RULE-4, S63 RULE-1, S66 RULE-1, S68 RULE-2)

Row 1 swept `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` before writing and recorded each hit with its file's ending (`s72/sweep.py`; 433 lines appended to `s72-anchors.txt`, 500 lines in all). The hits per name:

| Name or literal | Hits | Name or literal | Hits |
|---|---|---|---|
| `ArrowAnnotation(` | 17 | `RectAnnotation(` | 23 |
| `_annotation_from_wire` | 15 | `_annotation_to_wire` | 9 |
| `_clamp_annotation` | 12 | `clip_mark` | 30 |
| `_annotations_from_in` | 7 | `createDrawnMark` | 7 |
| `hitBody` | 4 | `translateBody` | 16 |
| `markLabel` | 11 | `styleToolFor` | 11 |
| `styleToolOfMark` | 8 | `TOOL_BUTTON_IDS` | 17 |
| `TOOL_LETTERS` | 13 | `Six annotation tools` | 2 |
| `box, highlight, redact, pixelate or eraser` | 2 | the `/settings/capture` fakes | 80 |
| the tool-list literals | 6 | the mark-type lists | 3 |
| the capture key lists (`tool_lock`) | 119 | | |

Each caller's tests ran at its row (S55 RULE-1): the row 1 UI files (`s72-types-ui-tests.txt`, `Tests  280 passed (280)` in 12 files), the row 1 Python files (`s72-types-py.txt`, `275 passed in 6.44s`), the row 2 Python, MCP and UI files (`s72-r2-py.txt` `527 passed, 1 deselected in 45.24s`; `s72-r2-mcp.txt` `Tests  305 passed (305)`; `s72-r2-ui.txt` `Tests  242 passed (242)`), and the row 4 set (§Row 4). The sweep missed one tail pin, AC-103.3's union order, which row 4 met without moving a test (D-787, §Departures 5); and the plan's §Pins that move missed AC-99.6's adjacency and AC-143.4's OpenAPI pin (D-785, D-788). No fake asserts the full capture key set apart from the moved pins below.

### The moved pins, before and after

`Before` is the plan's line at `5db3623`; `After` is the line now.

| Pin | File and line now | Ending | Before | After | Row |
|---|---|---|---|---|---|
| `AnnotationType` members | `tests/unit/test_domain.py:326-327`; `tests/unit/test_domain_capture.py:33`, `:42`, `:52` | CRLF | no `Step` (`test_domain.py:316-317`, `test_domain_capture.py:32-41`) | `Step = "step"` after Redact | 1 |
| AC-130.6's sample of every mark | `tests/unit/test_domain_capture.py:869` (step `:889`) | CRLF | no step mark | one step mark; Red (`s72-r2-ac130-6.txt`, `1 failed in 0.10s`) until row 4 | 2 |
| The clamp kinds | `tests/unit/test_capture_service.py:1243` (import `:1235`) | CRLF | no `step` (`:1208`, `:1247`) | gains `step` after redact | 2 |
| AC-36.12, the capture key set | `tests/unit/test_capture_service.py:41-42`, `:62-63`, `:429` | CRLF | ends at `tool_lock` | gains `step_color` (`#E0AF68`) and `step_size` (32) | 2 |
| AC-105.2, the keys after the style rows | `tests/unit/test_capture_style_settings.py:54` | LF | `["tool_lock"]` | `["tool_lock", "step_color", "step_size"]` | 2 |
| AC-143.2, the keys after `pixelate_block_size` | `tests/unit/test_capture_tool_lock.py:63` | LF | `["tool_lock"]` | `["tool_lock", "step_color", "step_size"]` | 2 |
| AC-143.4, the OpenAPI pin (D-788) | `tests/e2e/test_api_capture_tool_lock.py:82` | LF | the working tree's snapshot | the snapshot at `5db3623` | 2 |
| AC-38.6, the MCP capture keys | `mcp-server/tests/capture.test.ts:67`, `:88`, `:221` | CRLF | ends at `tool_lock` | the two step leaves and defaults; AC-105.5's `slice(7, 16)` (`:1740`) holds | 2 |
| `TOOL_LETTERS`' key type | `ui/tests/unit/capture-tool-lock.test.ts:84` | LF | `Record<CaptureTool, string>` | `Record<LetterTool, string>` | 1 |
| AC-103.14, the toolbar order | `ui/tests/unit/capture-redact.behavior.test.ts:245`, `:252`, `:273` | LF | `8 tools`, `slice(4, 7)` | `9 tools`, `slice(5, 8)` = Step, Redact, Smart eraser | 1 |
| AC-65.1 and AC-87.1 negative, the tool list | `ui/tests/unit/capture-toolbar.test.ts:26`, `:30`, `:42`, `:70`, `:180` | CRLF | no `step`; `eight tools` | `step` after `text`; `nine tools`; the step options rule (row 3) | 1, 3 |
| AC-80.8, the no-shot and hint tables | `ui/tests/unit/icon-hints.test.ts:54`, `:84` | CRLF | no Step button | `capture-tool-step`, `Step: Places the next number` | 1 |
| AC-105.1, AC-105.6, AC-105.7, the style tables | `ui/tests/unit/capture-tool-style.test.ts:117`, `:160`, `:177`, `:185`, `:218` | LF | no `step` | `DEFAULTS.step`, `LEAVES.step`, `FULL_STYLES.step`; `FOR_TOOL` and `OF_MARK` give `'step'` (row 3) | 1, 2, 3 |
| The resize help sentence | `ui/tests/unit/capture-help-content.test.ts:14` | CRLF | `box, highlight, redact, pixelate or eraser` | `box, ellipse, highlight, redact, pixelate or eraser` | 3 |
| AC-99.6, the help adjacency (D-785) | `ui/tests/unit/capture-help-content.test.ts:132` (`DUPLICATE_HELP_SENTENCE` `:17`) | CRLF | edit sentence, then history | edit, then Ctrl+D, then history | 3 |
| The chord table | `ui/tests/unit/fixtures/chord-table.ts:16` | LF | no Duplicate | `['capture:duplicate', 'Ctrl+D', '/capture']`; AC-97.1 (`shortcuts.test.ts:312`) and AC-97.5 (`gui-actions-audit.test.ts:485`) Red until rows 4 and 5 | 3 |
| The geometry fixture | `ui/tests/e2e/fixtures/capture-geometry.json:65`, `:70` | CRLF | no `arrow_both`, no `steps` | both keys, from HEAD_BAKE's and STEP_BAKE's formulas | 2 |

These held, as the plan read: AC-19.17 (`command-palette.test.ts:3`), AC-23.18 (`gui-actions-audit.test.ts:157`), AC-97.4 (`common-shortcuts.test.tsx:49`), AC-131.21 (`capture-crop-tool.behavior.test.ts:853`), AC-81.1 (`capture-action-row.test.ts:365`), AC-90.9 and AC-91.8 (`capture-toolbar.test.ts:197`, `:215`), the registry letter slice (AC-143.15, `capture-tool-lock.test.ts:134`) and AC-103.3 (`test_capture_redact.py:116`; D-787). `test-ids.ts` gained 12 lines after line 518 only, so AC-51.6 and AC-81.13 read `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` (`s72-r3-hash.txt`, `Tests  1 passed | 12 skipped (13)`; the gate's `s72-D6-action-row.txt`, `Tests  13 passed (13)`).

### Row 2's data

- **The geometry fixture** gained `arrow_both` and `steps` (12 size and number pairs), computed by a scratch script from HEAD_BAKE's and STEP_BAKE's formulas (`s72/r2_geometry_probe.py`). AC-106.8, AC-106.9, AC-107.10 and AC-107.12 read it; its old readers (`test_capture_adapter.py:35`, `capture-arrow-head.test.ts:19`) read the old keys only and held.
- **The bakes at the defaults don't change.** Row 0 probed today's bakes before any change (`s72-baseline.txt`): `af685c76ffcd76beed861e6cd79175d1222b97fa0fb9ebcd27064518661ba3fe 120x60 end-arrow` and `9ce84cf453ac76c5407e9a1a3d40e368ee42e8e1a9de784f473bed70c02a89fd 80x60 rect`. AC-106.30 pins both hashes after Green (`s72-r3-guard-py-test_ac_106_30.txt`, `2 passed, 108 deselected in 0.16s`).
- **`assert_never`.** `assert-never-probe.py` shows pyright needs both new cases: `one error naming StepAnnotation and Never at assert_never: True` (domain) and `one error naming StepAnnotationIn and Never at assert_never: True` (route) (`s72-r2-never.txt`, `s72-D6-never-probe.txt`).
- **id-length.** `s72-r2-id-length.txt` reads `47 test(s), 0 too long`.

### Row 3's Red tests (S50 RULE-2, S61 RULE-3, S66 RULE-2)

Row 3 wrote the four new Python files, the two new Vitest files, the help, toolbar, style, chord and audit pins, and the two Electron tests, against the row 2 code.
- Python: `69 failed, 82 passed in 17.71s` (`s72-py-red.txt`, exit 1); MEU-106 31 failures and MEU-107 38.
- Vitest: `Test Files  7 failed (7)`, `Tests  73 failed | 93 passed (166)` (`s72-ui-red.txt`, exit 1); MEU-106 55, MEU-107 11 and the moved pins 7 (AC-65.1, AC-97.1, AC-97.5, AC-99.6, AC-100.10, AC-101.5, AC-105.6).
- Electron: AC-106.28 `1 failed`, `expect(locator).toBeVisible() failed` (`s72-e2e-red-106.txt`); AC-107.24 `1 failed`, `expect(locator).toHaveCount(expected) failed` (`s72-e2e-red-107.txt`).
- red-check: `red-check: 4 receipt(s), 45 required test(s), 0 problem(s)` (`s72-red-check.txt`): 17 Python, 26 Vitest and 2 Electron ids.
- The guards passed on the Red tree: AC-106.14, AC-106.31, AC-107.27 and AC-107.29 each `Tests  1 passed | 59 skipped (60)` (`s72-r3-guard-106.14.txt`, `s72-r3-guard-106.31.txt`, `s72-r3-guard-107.27.txt`, `s72-r3-guard-107.29.txt`); AC-106.16 `9 passed, 101 deselected in 0.05s`, AC-106.30 `2 passed, 108 deselected in 0.16s` and AC-107.28 `7 passed, 103 deselected in 0.19s` (`s72-r3-guard-py-*.txt`); AC-107.13 `Tests  1 passed | 59 skipped (60)` (`s72-ui-107-13.txt`). id-length `151 test(s), 0 too long` (`s72-r3-id-length.txt`); the UI build `built in 4.09s` (`s72-r3-ui-build.txt`).

### Row 4's Green changes (S55 RULE-1)

Green changed source only, apart from D-787's union order, which needed no test change. Every caller row 1 recorded ran in row 4's set:
- pytest `759 passed in 46.70s` (`s72-py-green.txt`);
- Vitest `Tests  547 passed (547)` in 26 files (`s72-ui-green.txt`);
- Electron `53 passed (1.3m)` (`s72-e2e-green.txt`);
- MCP `Tests  78 passed (78)` in 3 files (`s72-mcp-green.txt`);
- pyright `0 errors` (`s72-r4-pyright.txt`), the UI build `built in 3.90s` (`s72-r4-ui-build.txt`), the OpenAPI check exit 0 (`s72-r4-openapi.txt`), UI typecheck and lint exit 0.

Row 5 wrote the spec text (`s72-r5-spec.txt`, every key `True`; `s72-r5-actions.txt`, `Tests  19 passed (19)`), and row 6 the status (`s72-r6-status.txt`; `s72-r6-render.txt` `Drift check passed`; `s72-r6-canon.txt` `Tests  14 passed (14)`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-106.1 | type | The exact signatures (Session 66 RULE-1): Python: `ArrowHead = Literal["end", "none", "both"]`, `BoxShape = Literal["rect", "ellipse"]`, `ArrowAnnotation.head: ArrowHead = "end"` (last field), `RectAnnotation.shape: BoxShape = "rect"` (last field) … | Local Canon: D-767, D-769, D-771, D-777 | `tests/unit/test_capture_shapes.py:81, :99`; `ui/tests/unit/capture-shapes.test.ts:32` | ✅ |
| AC-106.2 | behaviour | HEAD_FIELD: `ArrowAnnotation` defaults `head` to `"end"` and accepts `"none"` and `"both"`. | Spec: 09 Line row | `tests/unit/test_capture_shapes.py:178, :188` | ✅ |
| AC-106.3 | behaviour | SHAPE_FIELD: the same for `RectAnnotation.shape`, with `"rect"` the default and `"ellipse"` accepted. | Spec: 09 Ellipse row | `tests/unit/test_capture_shapes.py:204, :216` | ✅ |
| AC-106.4 | behaviour | DEFAULT_OMIT on the wire: `_annotation_to_wire` of a default arrow and a default rect holds no `head` and no `shape` key; a `"none"` arrow and an `"ellipse"` rect hold them; `_annotation_from_wire` reads a missing key as the default, reads the explicit default, and refuses `"x"`, `""` and `null` … | Local Canon: D-768 | `tests/unit/test_capture_shapes.py:232, :242, :254, :283, :295` | ✅ |
| AC-106.5 | behaviour | The API and OpenAPI: `POST /captures/{id}/annotate` with a `"none"` arrow and an `"ellipse"` rect gives 200, and the next GET returns both values; a default arrow's response holds no `head` key and a default rect's no `shape` key; `"x"`, `""`, `null` and `1` give 422 for each field, and no body echoes the value … | Local Canon: D-767, D-768, D-769 | `tests/e2e/test_api_capture_shapes.py:66, :82, :96, :119` | ✅ |
| AC-106.6 | behaviour | MCP: the annotate schema accepts an arrow with `head: "both"` and a rect with `shape: "ellipse"`, and refuses `head: "End"`, `head: null`, `shape: "circle"` and `shape: 1`. | Local Canon: D-767, D-769 | `mcp-server/tests/capture.test.ts:1772` | ✅ |
| AC-106.7 | behaviour | UI zod: `annotateInSchema` accepts the same values and refuses the same, plus `head: "\uD800"` | Local Canon: D-767, D-769 | `ui/tests/unit/capture-shapes.test.ts:49` | ✅ |
| AC-106.8 | behaviour | HEAD_BAKE on a 120×60 white image, stroke 3, from (10, 30) to (110, 30): `"end"` bakes to the same bytes as the base adapter (a SHA-256 taken at row 0); `"none"` has ink at (108, 30) and no head ink outside the stroke band; `"both"` has head ink at both ends, and its head vertices equal the fixture's `arrow_both` within 1e-9 … | Spec: 09 Line row | `tests/unit/test_capture_shapes.py:316, :325, :337, :347, :362, :380` | ✅ |
| AC-106.9 | behaviour | HEAD_PREVIEW: `arrowShaftSpan` equals the fixture's `arrow_both` shaft and the `arrows` shaft ends within 1e-9. | Spec: 09 Line row | `ui/tests/unit/capture-shapes.behavior.test.ts:617`; `ui/tests/unit/capture-shapes.test.ts:177` | ✅ |
| AC-106.10 | behaviour | HEAD_HIT through `hitTestMarks` at 1:1 on a (100, 100) to (300, 100) arrow, stroke 20, whose heads reach 90 px back from each tip (probe `C:/Temp/av-kit/s72-plan-r2-geometry-probe.txt`), one id per head: `"end"`: (240, 125), inside the end head and 25 px off the shaft, hits; (160, 125), where a start head would be, misses … | Spec: 09 Line row; Local Canon: D-767 | `ui/tests/unit/capture-shapes.test.ts:225, :230` | ✅ |
| AC-106.11 | behaviour | ELLIPSE_BAKE: an `"ellipse"` rect (10, 10, 60, 40), stroke 3, on white: the corner pixel (11, 11) stays white, the top centre (40, 11) is ink, and the baked image equals Pillow's `draw.ellipse` over the same box and width | Spec: 09 Ellipse row | `tests/unit/test_capture_shapes.py:398` | ✅ |
| AC-106.12 | behaviour | ELLIPSE_PREVIEW: an `"ellipse"` mark renders one `<ellipse data-shape="ellipse">` with the `cx`, `cy`, `rx` and `ry` the box gives, and no `<rect>`. | Spec: 09 Ellipse row | `ui/tests/unit/capture-shapes.behavior.test.ts:643` | ✅ |
| AC-106.13 | behaviour | ELLIPSE_HIT through `hitTestMarks`, one id per case, presses in CSS px with the image at `ox = oy = 0` (distances from probe `C:/Temp/av-kit/s72-plan-r2-geometry-probe.txt`): a (10, 10, 200, 120) ellipse at 1:1: the outline at (110, 10) hits; the box corner (11, 11), 29.8 px from the outline, misses; the centre (110, 70) misses … | Spec: 09 Ellipse row (MEU-100 handles) | `ui/tests/unit/capture-shapes.test.ts:269` | ✅ |
| AC-106.14 | guard | The ellipse's handles: a selected ellipse shows the box's eight handles. | Spec: 09 Ellipse row | `ui/tests/unit/capture-shapes.behavior.test.ts:676` | ✅ |
| AC-106.15 | behaviour | ELLIPSE_CLIP, one parametrize id per row of the ellipse matrix: inside and touching are kept and moved; straddling, outside and one past are dropped. | Spec: 09 Crop row; Human-approved: D-676 | `tests/unit/test_capture_shapes.py:425, :450` | ✅ |
| AC-106.16 | guard | HEAD_CLIP, one parametrize id per cell of the head matrix (9 ids): the kept and clipped arrows keep their `head`, a clipped arrow's moved end lies on the crop edge, and the outside cases drop | Spec: 09 Crop row; Local Canon: D-675 | `tests/unit/test_capture_shapes.py:473` | ✅ |
| AC-106.17 | behaviour | Crop end to end: `POST /captures/{id}/crop` on a shot whose sidecar holds a `"none"` arrow, a straddling `"both"` arrow, an inside ellipse and a straddling ellipse gives a sidecar with the line, the clipped `"both"` arrow and the inside ellipse, and not the straddling ellipse | Spec: 09 Crop row | `tests/e2e/test_api_capture_shapes.py:135` | ✅ |
| AC-106.18 | behaviour | SHAPE_OPTIONS display: with Arrow armed and nothing selected, `capture-arrow-head` shows End pressed after the stroke control; with Box armed, `capture-box-shape` shows Rectangle pressed; with Highlight, Text, Redact, Eraser, Step or Select armed and nothing selected, neither control exists … | Local Canon: D-771 | `ui/tests/unit/capture-shapes.behavior.test.ts:695` | ✅ |
| AC-106.19 | behaviour | Draw with a pick: with Arrow armed, a None pick and a drag give a mark `{ type: 'arrow', …, head: 'none' }`; with Box armed, an Ellipse pick and a drag give `shape: 'ellipse'`. | Spec: 09 Line and Ellipse rows; Local Canon: D-768, D-771 | `ui/tests/unit/capture-shapes.behavior.test.ts:727` | ✅ |
| AC-106.20 | behaviour | A pick with a mark selected: with an arrow selected, Both changes its `head` as one undo step, Undo restores `"end"`, and no `PUT /settings/capture` is sent. | Local Canon: D-771; MEU-105 STYLE_TARGET | `ui/tests/unit/capture-shapes.behavior.test.ts:753` | ✅ |
| AC-106.21 | behaviour | Modifiers, one parametrize id per cell of the modifier matrix that names an AC: a Shift Line drag from (10, 10) to (50, 22) ends at (52, 10) and keeps `head: "none"`; a Shift Ellipse drag from (10, 10) to (50, 30) draws a 40×40 ellipse; an Alt Ellipse drag from (30, 30) to (40, 35) draws (20, 25, 20, 10); Shift+Alt draws (20 … | Spec: 09 Line and Ellipse rows (the MEU-143 modifiers apply) | `ui/tests/unit/capture-shapes.behavior.test.ts:862` | ✅ |
| AC-106.22 | behaviour | DUPLICATE's entry: the registry holds `capture:duplicate` right after `capture:tool_crop`, with `shortcut: 'Ctrl+D'`, `page: '/capture'`, `stateful: true`, `palette: false` and the label `Duplicate mark`; `RESERVED_CHORDS` doesn't hold `Ctrl+D`, and `buildShortcutMap(listCommands())` doesn't throw … | Spec: 09 Duplicate row (a page-scoped registry entry) | `ui/tests/unit/capture-shapes.test.ts:275` | ✅ |
| AC-106.23 | behaviour | DUPLICATE per mark type, one parametrize id each for arrow, line, rect, ellipse, highlight, text, redact, pixelate, eraser and step: with the mark selected and the surface focused, Ctrl+D appends a copy 10 px down and right with every other field equal, selects the copy, is `defaultPrevented`, and is one undo step. | Spec: 09 Duplicate row | `ui/tests/unit/capture-shapes.behavior.test.ts:882` | ✅ |
| AC-106.24 | behaviour | DUPLICATE at the edges, one parametrize id per row of the Ctrl+D matrix after the first (the ellipse row gives four ids, and each filled-box row one per type): Ctrl+D on the selected mark appends exactly the matrix's copy, with every other field equal, so no copy's far extent leaves the image and no copy moves left … | Spec: 09 Duplicate row (clamped) | `ui/tests/unit/capture-shapes.behavior.test.ts:941` | ✅ |
| AC-106.25 | behaviour | DUPLICATE guards: with nothing selected, Ctrl+D copies nothing and is not `defaultPrevented`; with the crop open, a text draft open, or an `aria-modal` element focused, it copies nothing; from the hex field with a mark selected, it is `defaultPrevented` and copies nothing (FIELD_GUARD's statement for Ctrl+D); during a live drag … | Spec: 09 Duplicate row; Session 72 prompt (FIELD_GUARD) | `ui/tests/unit/capture-shapes.behavior.test.ts:960` | ✅ |
| AC-106.26 | behaviour | MARK_LABELS: after an arrow, a line, a box and an ellipse are drawn, the mark labels read `Arrow 1`, `Line 1`, `Box 1` and `Ellipse 1` | Local Canon: D-778 | `ui/tests/unit/capture-shapes.test.ts:301` | ✅ |
| AC-106.27 | behaviour | SHAPES_HELP: the Annotation tools body holds each new sentence exactly, starts `Seven annotation tools`, holds the moved resize sentence, and still holds every MEU-143 sentence; `Six annotation tools` is absent | Spec: 09 Line, Ellipse, Duplicate and Step rows | `ui/tests/unit/capture-help-content.test.ts:166` | ✅ |
| AC-106.28 | behaviour | Electron, on a seam with `tool_lock: false`: A arms Arrow; a None pick and a drag draw a line; R arms Box; an Ellipse pick and a drag draw an ellipse; with the ellipse selected, Ctrl+D adds a second ellipse and selects it; Save POSTs three marks, the line with `head: "none"` and both ellipses with `shape: "ellipse"`. | Spec: 09 Line, Ellipse and Duplicate rows | `ui/tests/e2e/capture-inbox.test.ts:3597` | ✅ |
| AC-106.29 | behaviour | Trace (Session 55 RULE-3): one MCP annotate traced through the MCP schema, the API body, `_annotations_from_in` (a recording wrapper), the domain marks, the sidecar JSON (`head: "none"`, `shape: "ellipse"`) and the bake, where a pixel at the line's far end is ink and the ellipse's box corner is not | Session 55 RULE-3 | `tests/e2e/test_api_capture_shapes.py:192`; `mcp-server/tests/capture.test.ts:1862` | ✅ |
| AC-106.30 | guard | Unchanged behaviour: MEU-100's handles, MEU-105's style tests, MEU-143's tool-flow tests, every `"end"` arrow bake and every `"rect"` bake byte for byte, Ctrl+C (D-678), and `_clip_rect` for `shape: "rect"` | Local Canon: D-675, D-678 | `tests/unit/test_capture_shapes.py:494, :505` | ✅ |
| AC-106.31 | guard | No pick, `head` or `shape` value reaches the capture settings: after a None pick, an Ellipse pick and a draw, the recorded PUTs are empty | Local Canon: D-771 | `ui/tests/unit/capture-shapes.behavior.test.ts:1029` | ✅ |
| AC-106.32 | check | SHAPES_ACTIONS_INDEX: `capture:tool_step` follows `capture:tool_eraser`; `capture:arrow_head` and `capture:box_shape` follow `capture:style_tool`; `capture:duplicate` follows `capture:redo` and its Trigger names `Ctrl+D`; `gui-actions-audit.test.ts` passes | Local Canon: GUI actions index | row 5's check (`s72-r5-spec.txt`; `s72-r5-actions.txt`) | ✅ |
| AC-106.33 | check | SHAPES_SPEC for MEU-106: 09's Delivered (Session 72) note follows `:992`, names AC-106.1 to AC-106.34 and the plan folder, and 09 keeps CRLF | Local Canon: 09 Delivered notes | row 5's check (`s72-r5-spec.txt`; `s72-r5-actions.txt`) | ✅ |
| AC-106.34 | guard | `assert_never` in `_annotations_from_in`: `assert-never-probe.py` runs pyright on a scratch copy of `routes/captures.py` with the `StepAnnotationIn` branch removed, and pyright reports an error at the `assert_never` line | Local Canon: D-772; D-675 | `tests/unit/test_capture_shapes.py:528` | ✅ |
| AC-107 (cross-ref) | sibling | The other MEU of this session; its rows are in its own handoff: AC-107.1, AC-107.2, AC-107.3, AC-107.4, AC-107.5, AC-107.6, AC-107.7, AC-107.8, AC-107.9, AC-107.10, AC-107.11, AC-107.12, AC-107.13, AC-107.14, AC-107.15, AC-107.16, AC-107.17, AC-107.18, AC-107.19, AC-107.20, AC-107.21, AC-107.22, AC-107.23, AC-107.24, AC-107.25, AC-107.26, AC-107.27, AC-107.28, AC-107.29, AC-107.30 | plan §MEU-107 | the MEU-107 handoff | ✅ |
| AC-19.17 (cross-ref) | guard | The palette list uses `arrayContaining`; `capture:duplicate` is `palette: false`, so it holds | MEU-19 | `ui/tests/unit/command-palette.test.ts:3`; gate `s72-D6-ui-tests.txt` | ✅ |
| AC-23.18 (cross-ref) | guard | The audit's `toContain` holds with the Duplicate entry | MEU-23 | `ui/tests/unit/gui-actions-audit.test.ts:157`; gate `s72-D6-ui-tests.txt` | ✅ |
| AC-36.12 (cross-ref) | regression | The capture key set gains `step_color` and `step_size` after `tool_lock` (moved at row 2) | MEU-36 | `tests/unit/test_capture_service.py:429`; gate `s72-D6-py-tests.txt` | ✅ |
| AC-38.6 (cross-ref) | regression | The MCP capture keys gain the two step leaves; AC-105.5's `slice(7, 16)` holds | MEU-38 | `mcp-server/tests/capture.test.ts:221`, `:1740`; gate `s72-D6-mcp-tests.txt` | ✅ |
| AC-51.6 (cross-ref) | guard | `test-ids.ts`' prefix hash is unchanged: `6E569F82…870FF454` | MEU-51 | `s72-r3-hash.txt`; gate `s72-D6-action-row.txt` | ✅ |
| AC-65.1 (cross-ref) | regression | OPTIONS_BY_TOOL gives a step `['color', 'size']` (moved at row 3, Red, then Green) | MEU-65 | `ui/tests/unit/capture-toolbar.test.ts:42`, `:70`; `s72-ui-red.txt`; `s72-ui-green.txt` | ✅ |
| AC-67.20 (cross-ref) | regression | S15: the hover hint passed in the baseline, row 4 and the gate; it didn't fail | MEU-67 | `ui/tests/e2e/capture-inbox.test.ts:1605`; `s72-D6-ui-electron.txt` | ✅ |
| AC-80.8, AC-80.9 (cross-ref) | regression | The no-shot and hint tables gain the Step button (moved at row 1) | MEU-80 | `ui/tests/unit/icon-hints.test.ts:341`, `:361`; gate `s72-D6-ui-tests.txt` | ✅ |
| AC-81.1, AC-81.11, AC-81.13 (cross-ref) | guard | `ACTION_BUTTONS` stays disjoint from the toolbar; F2 passed; the byte hash holds | MEU-81 | `ui/tests/unit/capture-action-row.test.ts:365`, `:721`; `capture-inbox.test.ts:1952` | ✅ |
| AC-87.1 (cross-ref) | regression | The toolbar spec holds; its negative's sorted list gains `step` and reads `nine tools` (moved at row 1) | MEU-87 | `ui/tests/unit/capture-toolbar.test.ts:173`, `:180` | ✅ |
| AC-90.9 (cross-ref) | guard | The loop over `TOOLS` holds with Step: a selected pixelate wins | MEU-90 | `ui/tests/unit/capture-toolbar.test.ts:197` | ✅ |
| AC-91.8 (cross-ref) | guard | The loop over `TOOLS` holds with Step: a selected eraser wins | MEU-91 | `ui/tests/unit/capture-toolbar.test.ts:215` | ✅ |
| AC-97.1, AC-97.4, AC-97.5 (cross-ref) | regression | The chord table gains `capture:duplicate` `Ctrl+D` `/capture`; AC-97.1 and AC-97.5 were Red until rows 4 and 5; AC-97.4's bound controls hold | MEU-97 | `ui/tests/unit/shortcuts.test.ts:312`; `gui-actions-audit.test.ts:485`; `common-shortcuts.test.tsx:49` | ✅ |
| AC-99.6 (cross-ref) | regression | The help adjacency now reads edit, Ctrl+D, history (D-785; reported to Mat) | MEU-99 | `ui/tests/unit/capture-help-content.test.ts:132` | ✅ |
| AC-100.10, AC-100.11 (cross-ref) | regression | The history help sentence follows; S15's Electron test didn't fail | MEU-100 | `capture-help-content.test.ts:141`; `capture-inbox.test.ts:3058` | ✅ |
| AC-101.5 (cross-ref) | regression | The resize help sentence names `ellipse` | MEU-101 | `ui/tests/unit/capture-help-content.test.ts:149` | ✅ |
| AC-103.3, AC-103.14 (cross-ref) | regression | The union's last three hold (D-787); the toolbar order is Step, Redact, Smart eraser (moved at row 1) | MEU-103 | `tests/unit/test_capture_redact.py:116`; `ui/tests/unit/capture-redact.behavior.test.ts:245` | ✅ |
| AC-105.1, AC-105.2, AC-105.5, AC-105.6, AC-105.7 (cross-ref) | regression | The style contracts gain the step tool: defaults, leaves, key order and STYLE_MODEL (AC-105.6 Red, then Green) | MEU-105 | `ui/tests/unit/capture-tool-style.test.ts:117`, `:160`, `:185`; `tests/unit/test_capture_style_settings.py:46` | ✅ |
| AC-130.6 (cross-ref) | regression | Every mark kind has a crop rule: the sample gains a step (Red at row 2, Green at row 4) | MEU-130 | `tests/unit/test_domain_capture.py:869`; `s72-r2-ac130-6.txt` | ✅ |
| AC-131.21 (cross-ref) | guard | The crop wait list disables the Step button with the crop's reason | MEU-131 | `ui/tests/unit/capture-crop-tool.behavior.test.ts:853` | ✅ |
| AC-143.2, AC-143.4, AC-143.15 (cross-ref) | regression | The lock key order gains the step leaves; the OpenAPI pin reads the `5db3623` snapshot (D-788; reported to Mat); the letter slice holds | MEU-143 | `tests/unit/test_capture_tool_lock.py:63`; `tests/e2e/test_api_capture_tool_lock.py:48`, `:82`; `capture-tool-lock.test.ts:134` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| `test_ac_106_2_arrow_refuses_a_bad_head` (AC-106.2) | `empty: None` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:178, :188` |
| `test_ac_106_3_rect_refuses_a_bad_shape` (AC-106.3) | `empty: None` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:204, :216` |
| `test_ac_106_4_other_values_are_written` (AC-106.4) | `assert None == 'none'` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:232, :242, :254, :283, :295` |
| `test_ac_106_4_wire_reads_missing_default_and_set_values` (AC-106.4) | `assert ArrowAnnotati...3, head='end') == ArrowAnnotati..., head='none')` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:232, :242, :254, :283, :295` |
| `test_ac_106_4_wire_refuses_a_bad_value` (AC-106.4) | `head-x: None` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:232, :242, :254, :283, :295` |
| `test_ac_106_5_none_arrow_and_ellipse_round_trip` (AC-106.5) | `assert [{'type': 'ar...th': 20, ...}] == [{'type': 'ar...th': 20, ...}]` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/e2e/test_api_capture_shapes.py:66, :82, :96, :119` |
| `test_ac_106_8_both_heads_draw_at_each_end` (AC-106.8) | `((20, 26), (255, 254, 254))` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:316, :325, :337, :347, :362, :380` |
| `test_ac_106_8_both_shaft_span_matches_the_fixture` (AC-106.8) | `({'from': [10, 30], 'to': [110, 30], 'stroke': 3, 'head': 15, ...}, ((10.0, 30.0), (97.49329346470985, 30.0)))` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:316, :325, :337, :347, :362, :380` |
| `test_ac_106_8_none_head_draws_no_head` (AC-106.8) | `((100, 26), (255, 0, 0))` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:316, :325, :337, :347, :362, :380` |
| `test_ac_106_8_short_both_arrow_has_two_heads_and_no_shaft` (AC-106.8) | `assert ((10.0, 30.0), (17.493293464709847, 30.0)) is None` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:316, :325, :337, :347, :362, :380` |
| AC-106.9 (Vitest) | `end: data-head: expected null to be 'end'` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:617`; `ui/tests/unit/capture-shapes.test.ts:177` |
| AC-106.10 (Vitest) | `expected { kind: 'body', index: +0 } to deeply equal null` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.test.ts:225, :230` |
| `test_ac_106_11_ellipse_bakes_as_pillow_draws_it` (AC-106.11) | `(255, 0, 0)` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:398` |
| AC-106.12 (Vitest) | `the ellipse is an <ellipse>: expected 'rect' to be 'ellipse'` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:643` |
| AC-106.13 (Vitest) | `expected { kind: 'body', index: +0 } to deeply equal null` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.test.ts:269` |
| `test_ac_106_15_ellipse_is_kept_or_dropped` (AC-106.15) | `('touching', (RectAnnotation(x=20, y=20, width=19, height=9, color='red', stroke_width=2, shape='ellipse'), 'clipped'))` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/unit/test_capture_shapes.py:425, :450` |
| `test_ac_106_17_crop_keeps_line_drops_straddling_ellipse` (AC-106.17) | `assert {'kept': 2, '... 'dropped': 0} == {'kept': 2, '... 'dropped': 1}` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/e2e/test_api_capture_shapes.py:135` |
| AC-106.18 (Vitest) | `the Head control: expected null not to be null` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:695` |
| AC-106.19 (Vitest) | `capture-arrow-head-none: expected null not to be null` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:727` |
| AC-106.20 (Vitest) | `capture-arrow-head-both: expected null not to be null` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:753` |
| AC-106.21 (Vitest) | `capture-arrow-head-none: expected null not to be null` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:862` |
| AC-106.22 (Vitest) | `expected 'settings:check_deps' to be 'capture:duplicate'` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.test.ts:275` |
| AC-106.23 (Vitest) | `Ctrl+D is prevented: expected false to be true` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:882` |
| AC-106.24 (Vitest) | `Ctrl+D is prevented: expected false to be true` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:941` |
| AC-106.25 (Vitest) | `the hex field: prevented: expected false to be true` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.behavior.test.ts:960` |
| AC-106.26 (Vitest) | `expected [ 'Arrow 1', 'Arrow 2', 'Box 3', …(1) ] to deeply equal [ 'Arrow 1', 'Line 1', 'Box 1', …(1) ]` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-shapes.test.ts:301` |
| AC-106.27 (Vitest) | `expected false to be true` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | `ui/tests/unit/capture-help-content.test.ts:166` |
| `test_ac_106_29_mcp_annotate_traced_to_sidecar_and_bake` (AC-106.29) | `assert [{'type': 'ar...th': 60, ...}] == [{'type': 'ar...th': 60, ...}]` (`s72-py-red.txt`) | passed (`s72-py-green.txt`; gate) | `tests/e2e/test_api_capture_shapes.py:192`; `mcp-server/tests/capture.test.ts:1862` |
| AC-106.28 (Electron) | `1 failed`, `expect(locator).toBeVisible() failed` (`s72-e2e-red-106.txt`) | passed (`s72-e2e-green.txt`; gate) | `ui/tests/e2e/capture-inbox.test.ts:3597` |
| AC-99.6 (moved pin) | `expected 'Six annotation tools: Arrow, Box, Hig…' to contain 'Select a mark to move it or drag an a…'` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | §The moved pins |
| AC-100.10 (moved pin) | `expected 'Six annotation tools: Arrow, Box, Hig…' to contain 'Ctrl+Z undoes and Ctrl+Y or Ctrl+Shif…'` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | §The moved pins |
| AC-101.5 (moved pin) | `expected 'Six annotation tools: Arrow, Box, Hig…' to contain 'Drag a square handle on a selected bo…'` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | §The moved pins |
| AC-97.1 (moved pin) | `capture:duplicate: expected undefined to be defined` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | §The moved pins |
| AC-97.5 (moved pin) | `capture:duplicate: expected [] to have a length of 1 but got +0` (`s72-ui-red.txt`) | passed (`s72-ui-green.txt`; gate) | §The moved pins |

- red-check read the four Red receipts and found every required id failing: `red-check: 4 receipt(s), 45 required test(s), 0 problem(s)` (`s72-red-check.txt`).
- The ACs not listed passed where they were written (row 2 or row 3) and are guards, type rows or checks; red-check didn't require them.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s72/run-row0.ps1 > C:/Temp/av-kit/s72-row0-console.txt 2>&1 (task.md row 0's Validation cell: baseline.ps1 *> C:/Temp/av-kit/s72-baseline.txt; base runs in C:/Temp/av-kit/s72-base-*.txt)", "scope": "Row 0: the execute words, the queue, the shapes (S7), baseline.sha, baseline-dirty.txt, the anchors and line endings, the lock syncs, the FFmpeg pair, the base runs and bakes, and the selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5db3623 before any row", "output": "execute words 'all recommendations accepted, execute'; D-782 ruled True; queue MEU-100, MEU-105 and MEU-143 approved, MEU-106 and MEU-107 pending; 5db3623 is an ancestor of HEAD: True; shapes wrong (S7): []; ui lock sync 651/0/0; mcp lock sync 133/0/0; ffmpeg n8.1.3-27-g8dca1586f4-20261031; base pytest 2630 passed, 37 warnings in 229.00s; base UI Test Files 128, Tests 1423 passed (1423); base MCP 530 passed in 36 files; base Electron 51 passed (1.5m); base ruff All checks passed!; bakes af685c76…ba3fe 120x60 end-arrow and 9ce84cf4…a89fd 80x60 rect; red-check selftest 71 fixture(s) (21 positive, 50 negative), 0 wrong; identity selftest 0 failure(s); id-length 4 case(s), 0 wrong; assert-never-probe 7 case(s), 0 wrong; openapi-delta 8 case(s), 0 wrong; baseline: all steps exit 0"}
```
```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-1-types", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s72/row1-validate.ps1 > C:/Temp/av-kit/s72-r1-validate-console.txt 2>&1 (task.md row 1's Validation cell: ui typecheck *> C:/Temp/av-kit/s72-types-ui.txt; ui lint *> C:/Temp/av-kit/s72-types-ui-lint.txt; the UI files *> C:/Temp/av-kit/s72-types-ui-tests.txt; capture-action-row.test.ts *> C:/Temp/av-kit/s72-types-action-row.txt; pytest *> C:/Temp/av-kit/s72-types-py.txt; pyright *> C:/Temp/av-kit/s72-types-pyright.txt; ruff *> C:/Temp/av-kit/s72-types-ruff.txt; sweep appended to C:/Temp/av-kit/s72-anchors.txt)", "scope": "Row 1: the type-only names (ArrowHead, BoxShape, StepAnnotation, AnnotationType.Step, the TS names, LetterTool, the Step toolbar entry and the enum-keyed maps) and the caller sweep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5db3623 plus rows 0 to 1", "output": "ui typecheck and lint exit 0; Tests 280 passed (280) in 12 files; capture-action-row Tests 13 passed (13); pytest 275 passed in 6.44s; pyright 0 errors; ruff All checks passed!; sweep 433 lines, anchors 500 lines"}
```
```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-2-data", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s72/row2-validate.ps1 (task.md row 2's Validation cell: pytest *> C:/Temp/av-kit/s72-r2-py.txt; AC-130.6 *> C:/Temp/av-kit/s72-r2-ac130-6.txt; MCP tests *> C:/Temp/av-kit/s72-r2-mcp.txt; UI tests *> C:/Temp/av-kit/s72-r2-ui.txt; pyright *> C:/Temp/av-kit/s72-r2-pyright.txt; ruff *> C:/Temp/av-kit/s72-r2-ruff.txt and C:/Temp/av-kit/s72-r2-ruff-all.txt; id-length *> C:/Temp/av-kit/s72-r2-id-length.txt; export_openapi --check *> C:/Temp/av-kit/s72-r2-openapi.txt; openapi-delta *> C:/Temp/av-kit/s72-r2-openapi-delta.txt; assert-never-probe *> C:/Temp/av-kit/s72-r2-never.txt; ui and mcp typecheck and lint *> C:/Temp/av-kit/s72-r2-ui-types.txt, C:/Temp/av-kit/s72-r2-ui-lint.txt, C:/Temp/av-kit/s72-r2-mcp-types.txt)", "scope": "Row 2: the fields, the wire, the clamp, the API with the regenerated snapshot, MCP, the UI schemas, the settings leaves, the geometry fixture and the key-set pins", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5db3623 plus rows 0 to 2", "output": "527 passed, 1 deselected in 45.24s; AC-130.6 1 failed in 0.10s (Red by intent until row 4); MCP Tests 305 passed (305) in 20 files; UI Tests 242 passed (242) in 8 files; pyright 0 errors; ruff All checks passed!; id-length 47 test(s), 0 too long; openapi --check exit 0; openapi-delta: pass; one error naming StepAnnotation and Never at assert_never: True; one error naming StepAnnotationIn and Never at assert_never: True; typecheck and lint exit 0"}
```
```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-3-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s72/row3-validate.ps1 > C:/Temp/av-kit/s72/row3-validate.out.txt 2>&1 (task.md row 3's Validation cell: id-length *> C:/Temp/av-kit/s72-r3-id-length.txt; pytest *> C:/Temp/av-kit/s72-py-red.txt; Vitest *> C:/Temp/av-kit/s72-ui-red.txt; ui build *> C:/Temp/av-kit/s72-r3-ui-build.txt; playwright -g AC-106.28 *> C:/Temp/av-kit/s72-e2e-red-106.txt; -g AC-107.24 *> C:/Temp/av-kit/s72-e2e-red-107.txt; red-check.py with the 45 --require ids *> C:/Temp/av-kit/s72-red-check.txt; guards *> C:/Temp/av-kit/s72-r3-guard-*.txt; AC-107.13 *> C:/Temp/av-kit/s72-ui-107-13.txt; the hash run *> C:/Temp/av-kit/s72-r3-hash.txt)", "scope": "MEU-106 and MEU-107 Red against the row 2 code, the moved pins failing before Green, the guards, the AC-51.6 hash", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5db3623 plus rows 0 to 3", "output": "pytest 69 failed, 82 passed in 17.71s (child exit 1); Vitest Test Files 7 failed (7), Tests 73 failed | 93 passed (166) (child exit 1); Electron AC-106.28 1 failed toBeVisible, AC-107.24 1 failed toHaveCount (child exit 1 each); red-check: 4 receipt(s), 45 required test(s), 0 problem(s); guards Tests 1 passed | 59 skipped (60) x4; Python guards 9, 2 and 7 passed; AC-107.13 Tests 1 passed | 59 skipped (60); hash Tests 1 passed | 12 skipped (13); id-length 151 test(s), 0 too long; ui build built in 4.09s"}
```
```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-4-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s72/row4-validate.ps1 > C:/Temp/av-kit/s72/row4-validate.out.txt 2>&1 (task.md row 4's Validation cell: pytest *> C:/Temp/av-kit/s72-py-green.txt; Vitest *> C:/Temp/av-kit/s72-ui-green.txt; Electron capture-inbox.test.ts *> C:/Temp/av-kit/s72-e2e-green.txt; MCP *> C:/Temp/av-kit/s72-mcp-green.txt; pyright *> C:/Temp/av-kit/s72-r4-pyright.txt; ui build *> C:/Temp/av-kit/s72-r4-ui-build.txt; export_openapi --check *> C:/Temp/av-kit/s72-r4-openapi.txt; ui typecheck and lint *> C:/Temp/av-kit/s72-r4-ui-types.txt, C:/Temp/av-kit/s72-r4-ui-lint.txt)", "scope": "MEU-106 and MEU-107 Green: every mechanism of both MEUs, every caller row 1 recorded, the guards", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5db3623 plus rows 0 to 4", "output": "pytest 759 passed in 46.70s; Vitest Test Files 26 passed (26), Tests 547 passed (547); Electron 53 passed (1.3m); MCP Tests 78 passed (78) in 3 files; pyright 0 errors; ui build built in 3.90s; openapi --check exit 0; typecheck and lint exit 0"}
```
```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-5-spec", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s72/row5-validate.ps1 > C:/Temp/av-kit/s72/row5-validate.out.txt 2>&1 (task.md row 5's Validation cell: the spec and index check *> C:/Temp/av-kit/s72-r5-spec.txt; gui-actions-audit.test.ts *> C:/Temp/av-kit/s72-r5-actions.txt)", "scope": "Row 5 (D3, AC-106.32, AC-106.33, AC-107.30): SHAPES_ACTIONS_INDEX, 09's two Delivered (Session 72) notes; CRLF kept", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5db3623 plus rows 0 to 5", "output": "{'index_crlf': True, 'tool_step': True, 'shape_rows': True, 'style_tool_step': True, 'duplicate': True, 'crlf_09': True, 'two_notes': True, 'note_106_place': True, 'note_107_place': True, 'note_106_acs': True, 'note_107_acs': True, 'note_106_mech': True, 'note_107_mech': True, 'plan_folder': True}; Tests 19 passed (19)"}
```
```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-6-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s72/row6-validate.ps1 > C:/Temp/av-kit/s72/row6-validate.out.txt 2>&1 (task.md row 6's Validation cell: the status check *> C:/Temp/av-kit/s72-r6-status.txt; meu_status.py render --check *> C:/Temp/av-kit/s72-r6-render.txt; the canon tests *> C:/Temp/av-kit/s72-r6-canon.txt; pre-status copies in C:/Temp/av-kit/s72/pre-status/)", "scope": "Row 6: MEU-106 and MEU-107 ready_for_review, the D-779 band in grouping row 48, the registry and BUILD_PLAN renders", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5db3623 plus rows 0 to 6", "output": "band from D-779: P2 {'d779_ruled': True, 'meu106': True, 'meu107': True, 'status_lf': True, 'row48': True, 'grouping_crlf': True}; Drift check passed; Test Files 2 passed (2), Tests 14 passed (14)"}
```
```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; pwsh -NoProfile -File docs/execution/plans/2026-11-14-capture-shapes-steps/session-gate.ps1 > C:/Temp/av-kit/s72-gate-h1.txt 2>&1 (task.md row H1-2's gate, with RECEIPTS_DIR=C:/Temp/av-kit and PYTHONIOENCODING=utf-8; step receipts C:/Temp/av-kit/s72-D6-*.txt; the scope listing before the run C:/Temp/av-kit/s72-h12-scope-list.txt)", "scope": "The plan's full gate: identity before; static py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract, scope-paths, red-check-selftest, id-length, never-probe and openapi-delta; fresh full py-tests, openapi, action-row (the AC-51.6 byte-hash guard), ui-tests, ui-build, mcp-build, mcp-tests, state-render and issues-render; runtime ui-electron (capture-inbox.test.ts); identity after. mcp-audit and build-record skipped by the plan", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; ui-types, ui-lint and mcp-types exit 0; task-contract OK: 24 row(s), 22 row(s) fully checked, 2 row(s) exempt (view_file): H1-5, H2-1; scope-paths changed paths: 65 outside scope: [] head moved (S3): False; baseline-dirty []; red-check selftest: 71 fixture(s) (21 positive, 50 negative), 0 wrong; id-length: 151 test(s), 0 too long; never-probe pass; openapi-delta: pass; py-tests 2781 passed, 37 warnings in 193.32s; openapi exit 0; action-row Tests 13 passed (13); ui-tests Test Files 130 passed (130), Tests 1532 passed (1532); ui-build built in 4.08s; mcp-build exit 0; mcp-tests Tests 535 passed (535) in 36 files; state-render Drift check passed; issues-render OK: known-issues.md is up-to-date; ui-electron 53 passed (1.3m); tested_state before = after; session-gate: all steps exit 0"}
```
```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s72-h1-3-h1-4", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s72/rowH1-3-validate.ps1 > C:/Temp/av-kit/s72/h1-3.out.txt 2>&1 (task.md row H1-3's Validation cell: meu_status.py render --check *> C:/Temp/av-kit/s72-drift-check.txt; get MEU-106 and MEU-107 *> C:/Temp/av-kit/s72-h13-status-106.txt, C:/Temp/av-kit/s72-h13-status-107.txt; check *> C:/Temp/av-kit/s72-h13-check.txt); pwsh -NoProfile -File C:/Temp/av-kit/s72/rowH1-4-validate.ps1 > C:/Temp/av-kit/s72/h1-4.out.txt 2>&1 (task.md row H1-4's Validation cell: export_openapi.py --check *> C:/Temp/av-kit/s72-openapi-check.txt; openapi-delta against baseline.sha *> C:/Temp/av-kit/s72-openapi-delta-check.txt)", "scope": "H1-3 the MEU-106 and MEU-107 status read after the gate; H1-4 the OpenAPI snapshot check and its delta from baseline.sha: head, shape, StepAnnotationIn, step_color and step_size only", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c", "output": "Drift check passed - SSOT loaded (143 MEUs, 12 phases), rendered regions match on-disk content; MEU-106 and MEU-107 ready_for_review: True; openapi --check exit 0; openapi-delta: pass"}
```

### Quality Gate Results

The H1-2 gate's last line is `session-gate: all steps exit 0` (`s72-gate-h1.txt:132`). It passed on its first run, after the allowed set gained `tests/e2e/test_api_capture_tool_lock.py` (D-788; `s72-h12-scope-list.txt`).

- **Static.** pyright `0 errors, 0 warnings, 0 informations` (`s72-D6-py-types.txt`); ruff `All checks passed!` (`s72-D6-py-lint.txt`); UI typecheck and lint (`--max-warnings 0`) and the MCP typecheck exit 0. The plan's own tooling passed:
  - the task contract: `24 row(s)`, `22 row(s) fully checked`, `2 row(s) exempt (view_file): H1-5, H2-1` (`s72-D6-task-contract.txt`);
  - scope-paths: `changed paths: 65 outside scope: []`, `head moved (S3): False`, baseline-dirty `[]` (`s72-D6-scope-paths.txt`);
  - the red-check selftest: `71 fixture(s) (21 positive, 50 negative), 0 wrong` (`s72-D6-red-check-selftest.txt`);
  - id-length: `151 test(s), 0 too long` (`s72-D6-id-length.txt`);
  - `assert-never-probe: pass` (`s72-D6-never-probe.txt`) and `openapi-delta: pass` (`s72-D6-openapi-delta.txt`).
- **Suites, against the Session 72 baseline** (`s72-base-*.txt`):
  - pytest `2781 passed, 37 warnings in 193.32s` (`s72-D6-py-tests.txt`). The baseline had `2630 passed` (`s72-base-py.txt`), so 151 tests are new, and id-length checked 151 new ids;
  - Vitest `Tests  1532 passed (1532)` in `130 passed (130)` files (`s72-D6-ui-tests.txt`). The baseline had `Tests  1423 passed (1423)` in 128 files (`s72-base-ui.txt`), so 109 tests are new; the two new files are `capture-shapes.test.ts` and `capture-shapes.behavior.test.ts`;
  - MCP `Tests  535 passed (535)` (`s72-D6-mcp-tests.txt`): the baseline's `530 passed` (`s72-base-mcp.txt`) plus AC-106.6, AC-107.7, AC-107.26 and the two trace halves of AC-106.29 and AC-107.20;
  - Electron `53 passed (1.3m)` (`s72-D6-ui-electron.txt`): the baseline's `51 passed (1.5m)` (`s72-base-e2e.txt`) plus AC-106.28 and AC-107.24. AC-67.20, AC-81.11 and AC-100.11 passed.
- **Build.** UI build `built in 4.08s` (`s72-D6-ui-build.txt`); MCP build exit 0; the OpenAPI check exit 0 (`s72-D6-openapi.txt`); the state render `Drift check passed` and the known-issues render `OK: known-issues.md is up-to-date`.
- **The byte-hash guard.** `action-row` passed `Tests  13 passed (13)` (`s72-D6-action-row.txt`), so AC-51.6 still reads `6E569F82…870FF454`.
- **After the gate.**
  - H1-3 exits 0. `s72-h13-check.txt` reads `MEU-106 and MEU-107 ready_for_review: True`; `s72-drift-check.txt` reads `Drift check passed`.
  - H1-4 exits 0. `s72-openapi-check.txt` exit 0 and `s72-openapi-delta-check.txt` reads `openapi-delta: pass`.
  - `current-focus.md` and the handoffs are outside `tested_state`.
- **Skipped by the plan.** `mcp-audit` was skipped because it needs the live network and YouTube, which the brief forbids. No action changed, so the audit baseline doesn't change. `build-record` was skipped because there is no release and no package build.
- **Identity.** `tested_state` before and after: `5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c` (`s72-D6-identity-before.txt`, `s72-D6-identity-after.txt`).
- **Warnings.** pytest reports 37 warnings, the same count as the baseline run (`s72-base-py.txt`). No test fails on a warning.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/capture.py` | modified | `ArrowHead`, `BoxShape`, `head`, `shape`, `StepAnnotation` (after Text in the union, D-787), `_clip_ellipse`, `_clip_step`, `clip_mark`'s new cases |
| `packages/core/src/avkit_core/domain/enums.py` | modified | `AnnotationType.Step` and its wire name |
| `packages/core/src/avkit_core/services/capture.py` | modified | the wire reads and writes `head`, `shape` and the step (DEFAULT_OMIT); `_clamp_annotation`'s step |
| `packages/core/src/avkit_core/services/settings.py` | modified | `step_color` and `step_size` |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | HEAD_BAKE, ELLIPSE_BAKE, STEP_BAKE (`StepLayout`, `step_badge_layout`, `step_text_color`) |
| `packages/api/src/avkit_api/schemas/captures.py`, `schemas/settings.py`, `routes/captures.py` | modified | `head`, `shape`, `StepAnnotationIn`, the two settings leaves, the route's step case |
| `openapi.committed.json` | modified | regenerated: the delta `openapi-delta.py` pins |
| `mcp-server/src/toolsets/capture.ts`, `settings.ts` | modified | the MCP schemas |
| `ui/src/renderer/src/features/capture/capture-shapes.ts` | new | `ARROW_HEADS`, `BOX_SHAPES`, `shapeOption`, `duplicateMark` |
| `ui/src/renderer/src/features/capture/capture-step.ts` | new | `stepBadgeLayout`, `stepTextColor`, `nextStepNumber`, `STEP_NUMBER_MAX` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx`, `CaptureViewport.tsx` | modified | the picks, the Head and Shape controls, the Step tool and badge, Duplicate, the ellipse and head previews |
| `ui/src/renderer/src/features/capture/capture-annotate.ts`, `capture-arrow-head.ts`, `capture-hit-test.ts`, `capture-tool-style.ts`, `capture-toolbar.ts`, `capture-commands.ts`, `capture-help-content.ts` | modified | the UI schema, `arrowShaftSpan`, HEAD_HIT, ELLIPSE_HIT, STEP_HIT, `markLabel`'s per-kind count, the step style, the Step button, the duplicate event, SHAPES_HELP |
| `ui/src/renderer/src/features/settings/settings-schemas.ts`, `ui/src/renderer/src/registry/commandRegistry.ts` | modified | the two step leaves; `capture:duplicate` `Ctrl+D` |
| `tests/unit/test_capture_shapes.py`, `tests/unit/test_capture_step.py`, `tests/e2e/test_api_capture_shapes.py`, `tests/e2e/test_api_capture_step.py` | new | the Python tests of both MEUs |
| `ui/tests/unit/capture-shapes.test.ts`, `ui/tests/unit/capture-shapes.behavior.test.ts` | new | the Vitest tests of both MEUs |
| the 15 moved-pin test files, `mcp-server/tests/capture.test.ts`, `ui/tests/e2e/capture-inbox.test.ts`, `ui/tests/e2e/test-ids.ts`, `ui/tests/e2e/fixtures/capture-geometry.json` | modified | §The moved pins; the MCP tests and traces; the two Electron tests; 12 new test ids; `arrow_both` and `steps` |
| `docs/build-plan/09-screenshot-capture.md`, `docs/build-plan/gui-actions-index.md` | modified | the two Delivered (Session 72) notes; SHAPES_ACTIONS_INDEX |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file, `.agent/context/current-focus.md` | modified | ready_for_review, the renders, row 48 `executed (Session 72)` P2, the focus paragraph |

`git diff --shortstat 5db3623` outside the plan folder and the handoffs reads `46 files changed, 1488 insertions(+), 108 deletions(-)`, with eight new files (`test_capture_shapes.py` 543 lines, `test_capture_step.py` 561, `test_api_capture_shapes.py` 232, `test_api_capture_step.py` 229, `capture-shapes.ts` 67, `capture-step.ts` 45, `capture-shapes.behavior.test.ts` 1318, `capture-shapes.test.ts` 354).

- **CRLF kept:** the grouping file, both build-plan docs, the MCP sources and `capture.test.ts`, `openapi.committed.json`, the API and core sources and `adapter.py`, `test_capture_service.py`, `test_domain.py`, `test_domain_capture.py`, `CapturePage.tsx`, `CaptureViewport.tsx`, `capture-annotate.ts`, `capture-arrow-head.ts`, `capture-commands.ts`, `capture-help-content.ts`, `capture-hit-test.ts`, `capture-toolbar.ts`, `settings-schemas.ts`, `capture-geometry.json`, `test-ids.ts`, `capture-help-content.test.ts`, `capture-toolbar.test.ts`, `icon-hints.test.ts`, `current-focus.md`.
- **LF kept:** `meu-registry.md`, `meu-status.yaml`, `BUILD_PLAN.md`, `test_api_capture_tool_lock.py`, `test_capture_style_settings.py`, `test_capture_tool_lock.py`, `capture-tool-style.ts`, `commandRegistry.ts`, `capture-inbox.test.ts`, `capture-redact.behavior.test.ts`, `capture-tool-lock.test.ts`, `capture-tool-style.test.ts`, `chord-table.ts`.
- **New files LF.**

```diff
@@ clip_mark
         case RectAnnotation():
+            if mark.shape == "ellipse":
+                return _clip_ellipse(mark, left, top, width, height)
             return _clip_rect(mark, left, top, width, height)
@@
+        case StepAnnotation():
+            return _clip_step(mark, left, top, width, height)
         case _:
             assert_never(mark)
@@ _clip_ellipse (D-676) and _clip_step (D-675)
+    x0, y0 = mark.x - left, mark.y - top
+    if x0 >= 0 and y0 >= 0 and x0 + mark.width <= width and y0 + mark.height <= height:
+        return replace(mark, x=x0, y=y0), "kept"
+    return None, "dropped"
+
+    x0, y0 = mark.x - left, mark.y - top
+    if 0 <= x0 < width and 0 <= y0 < height:
+        return replace(mark, x=x0, y=y0), "kept"
+    return None, "dropped"
```

The excerpt is abridged. The sources are `packages/core/src/avkit_core/domain/capture.py:510-540`, `:595` and `:609`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution of both MEUs in one rolling report, `2026-11-14-capture-shapes-steps-implementation-critical-review.md`, on the ledger loop `s72-execution-2026-11-14-capture-shapes-steps` (cap 6 rounds; no token budget, `token_budgets: "off"`). The estimate is about 14M tokens for round 1 and about 21M in all (plan §User Review Required). The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | 0 (0 blocking); spent 12,389,041 tokens | `5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c`, recomputed by the reviewer |

### Verdict

**approved** at round 1 of 6, with no findings (`.agent/context/handoffs/2026-11-14-capture-shapes-steps-implementation-critical-review.md`). The ledger recorded `verdict=approved`, `blocking=0`, `intent_achieved=yes`. The reviewer recomputed `tested_state` and found it equal to the gate's, reproduced the End-arrow and Rect bake hashes and AC-51.6's hash, ran `red-check.py` with the 45 required ids (`4 receipt(s), 45 required test(s), 0 problem(s)`), and ran its own probe of the domain, wire, API, crop, bake and settings (`188 assertions passed`). H1-7a reads `round 1 of 6; verdict=approved; open findings=0` (`s72-review-state-check.txt`) and H1-7b `approved at round 1 of 6, 0 open blocking findings` (`s72-exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The two clipboard Electron specs, `capture-filmstrip-actions.test.ts` and `capture-import.test.ts`, were not run | observation | Mat | Session 57 RULE-4: they write the real clipboard. They typecheck and lint in the gate; neither file changed |
| `ruff check tools/` fails on errors in `tools/issue_triage*` and `tools/meu_status*` that were there before this session | observation | None | Session 68 DEP-1; this plan lints only the files it edits |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2) |

### Departures and their basis

1. **The trace split (D-783).** The plan reads AC-106.29 and AC-107.20 each as one test from the MCP schema to the bake. Each is two halves that share one literal body. The Python half (`tests/e2e/test_api_capture_shapes.py:192`, `tests/e2e/test_api_capture_step.py:174`) posts the body to the API through `_annotations_from_in` (a recording wrapper), the sidecar and the bake. The MCP half (`mcp-server/tests/capture.test.ts:1862`, `:1881`) parses the same marks through the capture schema, runs the tool and pins the POST body equal to them. One process can't run the MCP tool and the FastAPI app with the bake.
2. **`markLabel`'s third argument (D-784).** AC-106.26 (`Line 1`, `Ellipse 1`) and AC-107.19 (`Step 4` is the step's own number) need a per-kind count, which `markLabel(mark, index)` can't give. It takes an optional third argument `marks` (`capture-hit-test.ts:393`); the two-argument callers keep working.
3. **AC-99.6's pin moved (D-785; reported to Mat).** SHAPES_HELP puts the Ctrl+D sentence after the nudge sentence, between `HELP_EDIT_SENTENCE` and `HISTORY_HELP_SENTENCE`, which AC-99.6 pinned as adjacent. The test now pins `${HELP_EDIT_SENTENCE} ${DUPLICATE_HELP_SENTENCE} ${HISTORY_HELP_SENTENCE}` (`capture-help-content.test.ts:132`). The placement is the approved plan text, and AC-99.6's intent, both sentences present in that order, holds. The plan's §Pins that move didn't list it.
4. **The jsdom halves (D-786).** `capture-shapes.test.ts` runs in the node environment, so it holds the pure halves of AC-106.9 and AC-107.11 (`arrowShaftSpan` against the fixture; `stepBadgeLayout` and `stepTextColor`). The rendered halves are in `capture-shapes.behavior.test.ts` (`:617`, `:657`) under the same ids.
5. **The union position (D-787).** STEP_TYPE says only that `StepAnnotation` joins the `Annotation` union. Appending it last broke AC-103.3 (`tests/unit/test_capture_redact.py:116`), which pins the union's last three as Pixelate, Eraser and Redact. Step sits after Text, and no test changed. Row 1's sweep missed this tail pin.
6. **AC-143.4's OpenAPI pin moved (D-788; reported to Mat).** `test_api_capture_tool_lock.py` compared MEU-143's baseline snapshot with the working tree's `openapi.committed.json`, so row 2's planned additions failed it though MEU-143's own delta didn't change. It now compares that baseline with the snapshot at `5db3623`, the commit that landed MEU-143 (`:82`); this session's additions are pinned by `openapi-delta.py` (H1-4). The gate's allowed set gained the file before H1-2 (`s72-h12-scope-list.txt`).

No departure changed an AC's text. The execution decisions D-783 to D-788 are autonomous and two-way, and they are in the plan's `decision_log`. Neither S15 test (AC-100.11, AC-67.20) failed in any run.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-14 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, row 1's sweep, the moved pins, the Red and Green receipts, the H1-2 gate and the evidence records (H1-6) |
| Reviewed | 2026-11-14 | codex (H1-7 execution review) | Round 1 approved, 0 findings, 12,389,041 tokens; H1-7a and H1-7b pass |
