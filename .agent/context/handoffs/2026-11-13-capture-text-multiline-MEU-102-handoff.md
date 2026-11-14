---
date: "2026-11-13"
project: "capture-text-multiline"
meu: "MEU-102"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-13-capture-text-multiline/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-13-capture-copy-image-MEU-104-handoff.md"
---

# Handoff: 2026-11-13-capture-text-multiline-MEU-102-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-102 `capture-text-multiline`. This is the third of the five capture annotation editor sessions, Sessions 68 to 72 (grouping D-674). It is grouping slice 3b (D-159), which waited on G-3.

- **The stored text holds LF only.** `normalize_text_newlines` folds `\r\n` and `\r` to `\n`. `TextAnnotation.__post_init__` applies it first, so the 1 to `TEXT_MAX_CHARS` rule counts the stored text (TEXT_NEWLINES, D-703). `TextAnnotationIn` folds the same way in a before-validator, so `max_length` counts the folded text and the OpenAPI document does not change (TEXT_API_NEWLINES). LF, a tab and other control characters are stored as given (D-704).
- **Line spacing derives from `font_size`.** The adapter names Pillow's default line gap `TEXT_LINE_GAP = 4` and passes it as `spacing=`, so the baked bytes don't change (TEXT_LINE_GAP). The UI's pitch is `segoeAscentPx(size) + TEXT_LINE_GAP_PX` (TEXT_LINE_PITCH). No stored mark held a newline, so there is no layout version (G-3, D-702).
- **The plate is the union of the lines.** `textBackgroundBox` unions each line's unrounded glyph extents, with an empty line as a point, and rounds and clamps once; a text with no `\n` keeps today's body (TEXT_PLATE_LINES). The hit test and `scaleTextMark` read it, so a click on the second line selects the mark (AC-102.24).
- **The preview draws one `<tspan>` per line** when the text holds `\n`; a one-line mark keeps its single text child (TEXT_SVG_LINES, D-707).
- **The draft is a `<textarea>`** with the same test id, `wrap="off"` and `rows` equal to its line count. Enter commits, Shift+Enter adds a line, Enter belongs to the IME while composing, and Escape cancels (TEXT_DRAFT_KEYS, D-705, D-708). A hint below it reads `Enter to finish, Shift+Enter for a new line, Esc to cancel`, and the draft's `aria-describedby` names it (TEXT_DRAFT_HINT, D-706).
- **The MCP annotate description** states the newline rule; no action, schema or audit baseline changes (TEXT_MCP_DOC, D-711).
- **Parity data.** `capture-geometry.json` gains `segoe_line_pitch` and `text_plates` (TEXT_GEOMETRY, D-709). `tools/capture_bake_fixture.py --multiline` writes a 240×160 pair with `Hi\n\nHi\n` at size 32 (TEXT_FIXTURE_MULTILINE, D-710). The Electron fidelity seam takes the pair as an argument, and AC-102.19 checks that the preview and the bake agree line by line (TEXT_PARITY_E2E).
- **No wrap.** Lines never wrap; wrap width is Later (C-3).

The OpenAPI snapshot does not change (H1-4). The MCP audit baseline does not change.

**Build Plan Section**: bp09, `docs/build-plan/09-screenshot-capture.md` §Multi-line text, with its Delivered (Session 70) note.

**Predecessor**: [MEU-104 handoff](2026-11-13-capture-copy-image-MEU-104-handoff.md), Session 69. The grouping is `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md` (row 46). Its decisions D-158 (human, `USER_EXPLICIT` 2026-10-29 "all recommendations are accepted"), D-159, D-160, D-674 and D-675 carry.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-13. Codex approved the plan at round 1 (`.agent/context/handoffs/2026-11-13-capture-text-multiline-plan-critical-review.md`). At the gate Mat set the execution review budget, "30M (Recommended)", and said to execute, "Execute now (Recommended)" (D-712). No ruling was needed during execution.

**Band mismatch (named, not changed).** The grouping's §3 heading (`:83`) and tracker row 46 (`:124`) say P3; `.agent/context/meu-status.yaml` says `band: P2` for MEU-102. Row 6 wrote only the tracker's status and plan columns, and `meu_status.py get` still reads `('ready_for_review', 'P2')` (`s70-r6-status.txt`).

**Plan-time departure (B-4).** At plan time the stored-marks scan (`s70/b4_stored_marks_scan.py`) opened Mat's capture inbox sidecars and the app database read-only before Mat was told. The Session 70 prompt forbids that ("it reads no user's capture inbox without telling me first"). The scan printed counts only (29 shot rows, 5 sidecars, 11 text marks, 0 LF, 0 CR, 0 other control characters; `s70-b4-scan.txt`), with no path, file name or mark text, and wrote nothing. The plan's §User Review Required records it; no execution row read the inbox or the database.

**Receipts.** A receipt named by its file name alone (`s70-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s70/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **A text mark's `text`.**
  - The draft's `onChange` passes `event.target.value` to `onTextDraftChange` as typed, `\n` included (`CaptureViewport.tsx:1560`). Enter without Shift calls `onTextCommit` (`:1566`); a composing Enter returns first (`:1563`).
  - The API body goes through `TextAnnotationIn._fold_newlines` (`schemas/captures.py:126-130`), which folds a `str` and returns any other value unchanged, so a non-`str` still gets today's 422.
  - `_annotations_from_in` builds a `TextAnnotation`, whose `__post_init__` folds again (`domain/capture.py:366`) through `normalize_text_newlines` (`:345`). The function is idempotent, so `_clip_text`'s `replace` changes nothing.
  - The sidecar, the bake (`_apply_text`, `spacing=TEXT_LINE_GAP` at `adapter.py:893`) and the preview see LF only. No log, response body or Console line echoes the text; AC-102.5's 422 case asserts that.
- **The line pitch.**
  - The UI: `segoeLinePitchPx` (`capture-text-metrics.ts:28`) returns `segoeAscentPx(size) + TEXT_LINE_GAP_PX` (`:25`).
  - The bake: Pillow's line spacing with `spacing=TEXT_LINE_GAP` (`adapter.py:71`, `:151`, `:893`).
  - `segoe_line_pitch` in `capture-geometry.json` pins both to the same numbers at the 17 sizes (AC-102.7, AC-102.9).
- **The plate.** `textBackgroundBox` (`capture-text-metrics.ts:58`) reads `textLines` (`:33`) and the pitch; the SVG's tspans (`CaptureViewport.tsx:334`) use the same pitch from `svgTextBaselineY(ann)`.

AC-102.16 traces one two-line mark through the renderer half, from the draft's keydowns to the recorded save POST body. AC-102.17 traces the Python half with a recording wrapper, from an annotate body holding `\r\n` to the sidecar's text and the baked pixels (Session 55 RULE-3).

### Row 1's caller grep (S55 RULE-1, S59 RULE-1, S62 RULE-4, S63 RULE-1, S66 RULE-1)

Before its edits, row 1 swept `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` at `4e35af9` (`s70/row1-sweep.txt`, 145 lines) and appended the hits to `s70-anchors.txt` (169 lines). Row 0's part of the same file holds each target's SHA-256 and line endings. The sweep has a section for each of these:
- the callers and pins of `text_plate_box`, `_apply_text`, `TextAnnotation(`, `TextAnnotationIn`, `TEXT_MAX_CHARS`, `textBackgroundBox`, `segoeAscentPx` and `svgTextBaselineY`;
- every reader of `capture-text-draft`, with its cast, `tagName`, `type` or `size`;
- every reader of `capture-geometry.json` and `capture-fidelity-`, `installFidelitySeam` and `fidelityBoxes`;
- every pin on the annotate description.

The plan's §Pins that move is `None.`, and the sweep agrees: no hit needed a change.
- **The pins the plan named** hold as it says: the `as HTMLInputElement` casts at `capture-page.behavior.test.ts:359`, `:431`, `:641` and `:3127`; `capture-text-metrics.test.ts:27`; `test_capture_adapter.py:612` and `:618`; AC-59.16 at `mcp-server/tests/capture.test.ts:370`; `isEditableTarget` (`capture-import.ts:137`).
- **Hits the plan didn't name.** Each passes unchanged; none is a pin that moves:
  - the Electron `.fill` and `.press('Enter')` calls on the draft at `capture-inbox.test.ts:431`, `:560`, `:882`, `:2890` and `:2983`;
  - `capture-action-row.test.ts:769`, and `capture-copy-image.behavior.test.ts:487` and `:591`;
  - the `{Enter}` typing at `capture-page.behavior.test.ts:560`, `:682`, `:1599`, `:3163` and `:3289`, which still commits through TEXT_DRAFT_KEYS;
  - the five readers of `capture-geometry.json`: `test_capture_adapter.py:35`, `test_capture_text_metrics.py:15`, `capture-arrow-head.test.ts:19`, `capture-page.behavior.test.ts:75` and `capture-text-metrics.test.ts:8`. They read existing keys, which did not change.
- **The byte-hash guard.** Row 1 appended the MEU-102 block after the file's last line (`test-ids.ts:516-517`): `CAPTURE_TEXT_DRAFT_HINT`. AC-51.6 reads `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` (`capture-action-row.test.ts:754-756`; `s70/ac51-6-note.txt`). Row 1's own run passed 13 tests (`s70-types-action-row.txt`).

### Row 2's data (D-709, D-710)

Row 2 added TEXT_FIXTURE_MULTILINE to `tools/capture_bake_fixture.py` (CRLF) and ran `--multiline` to write the pair (`s70-r2-fixture-write.txt`). It wrote `segoe_line_pitch` and `text_plates` into `capture-geometry.json` (CRLF), each value read from Pillow through `text_plate_box`, with every other key's bytes unchanged. `s70-r2-data.txt` reads `{'crlf_only': True, 'pitch_sizes': True, 'plates': True, 'pair_240x160': True}`. It appended AC-102.8 to `tests/unit/test_capture_bake_fixture.py` (CRLF), and that file passed `56 passed in 0.96s` (`s70-r2-fixture-py.txt`).

### Row 3's Red tests (S50 RULE-2, S61 RULE-3, S66 RULE-2)

Row 3 wrote three new files, all LF:

- `tests/unit/test_capture_text_lines.py` (198 lines) covers AC-102.1 (Python), .2, .3, .4, .6, .7 and .23.
- `tests/e2e/test_api_capture_text_lines.py` (156 lines) covers AC-102.5 and .17.
- `ui/tests/unit/capture-text-lines.behavior.test.ts` (448 lines) covers AC-102.1 (TypeScript), .9 to .16, .18 and .24.

It added tests to existing files, each keeping its endings:
- AC-102.21 to `mcp-server/tests/capture.test.ts:1658` (CRLF);
- AC-102.19 and AC-102.20 to `ui/tests/e2e/capture-inbox.test.ts:2371` and `:2394` (LF). TEXT_PARITY_E2E's seam change (`installFidelitySeam(page, shot, fixture = FIDELITY_FIXTURE)` at `:2130`, and `inkRows` in `fidelityBoxes`) went in with them, so AC-82.6 calls the seam with the default pair.

`id-length.py` found all 19 new pytest ids within red-check's header width (`s70-r3-id-length.txt`).

### Row 4's Green changes (S55 RULE-1)

Row 4 made counted byte replacements, keeping each file's endings:

- **Domain.** `normalize_text_newlines`'s body and its call in `TextAnnotation.__post_init__` (TEXT_NEWLINES).
- **API.** `TextAnnotationIn._fold_newlines` (TEXT_API_NEWLINES); `openapi.committed.json` unchanged.
- **UI.** The bodies of `segoeLinePitchPx` and `textLines`, and the multi-line branch of `textBackgroundBox` (`capture-text-metrics.ts`); the tspans, the textarea with its keys and the hint (`CaptureViewport.tsx`).
- **MCP.** The annotate description's sentence (`mcp-server/src/toolsets/capture.ts:101`).

**First runs.** Row 4's first targeted runs (`s70/quick-py.txt`: `19 passed in 2.29s`; `s70/quick-mcp.txt`: `Tests 58 passed (58)`) passed. The UI run (`s70/quick-ui.txt`) gave `Tests 1 failed | 10 passed (11)`: AC-102.12, `AssertionError: expected [ 'Hi', 'Hi' ] to deeply equal [ 'Hi' ]`. The test read the second committed mark as `textMarks()[1]`, but the DOM order of two marks at one point is not the commit order. The test now matches the marks by content (§Departures 1). Row 4's command then exited 0. Its first Electron run had one failure, AC-100.11, which passed three times alone and in the full rerun (§Departures 2).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-102.1 | type | The exact signatures: `normalize_text_newlines(text: str) -> str`, the adapter's `TEXT_LINE_GAP == 4`, `write_multiline_fixture(out_dir: Path) -> tuple[Path, Path]`, `TEXT_LINE_GAP_PX === 4`, `segoeLinePitchPx(fontSize: number): number`, `textLines(text: string): string[]` and `CAPTURE_TEXT_DRAFT_HINT === 'capture-text-draft-hint'`. Rows 1 and 2 added the names, so it passed where row 3 wrote it | Local Canon: D-701 | `tests/unit/test_capture_text_lines.py:66`; `ui/tests/unit/capture-text-lines.behavior.test.ts:292` | ✅ |
| AC-102.2 | behaviour | TEXT_NEWLINES: a `TextAnnotation` built with `Hi\r\nHi`, `Hi\rHi` and `Hi\r\n\r\nHi` stores `Hi\nHi`, `Hi\nHi` and `Hi\n\nHi`, one parametrize id per case | Spec: 09 Model row; Local Canon: D-703 | `test_capture_text_lines.py:87` | ✅ |
| AC-102.3 | guard | LF, a tab and other control characters are stored as given; a non-`str` text and empty text raise `AnnotationValidationError` | Local Canon: D-704 | `test_capture_text_lines.py:95` | ✅ |
| AC-102.4 | behaviour | The length rule counts the folded text: 250 `a\r\n` pairs are accepted by the domain and by `TextAnnotationIn`; 251 pairs are refused by both | Local Canon: D-703 | `test_capture_text_lines.py:115` | ✅ |
| AC-102.5 | behaviour | TEXT_API_NEWLINES: annotate with `Hi\r\nHi` gives 200 and the sidecar stores `Hi\nHi`; a non-`str` text gives 422 with no echo of the value; the OpenAPI document equals the committed one | Spec: 09 Model row; Local Canon: D-703 | `tests/e2e/test_api_capture_text_lines.py:110` | ✅ |
| AC-102.6 | behaviour | A bake of `Hi\r\nHi` and of `Hi\rHi` gives bytes equal to the bake of `Hi\nHi`, at sizes 16 and 32, with and without `bg_color` | Spec: 09 Parity row; Local Canon: D-703 | `test_capture_text_lines.py:144` | ✅ |
| AC-102.7 | guard | TEXT_GEOMETRY: each `segoe_line_pitch` entry equals Pillow's `getbbox("A")` bottom plus `TEXT_LINE_GAP`, and each `text_plates` box equals `text_plate_box` for its case | Spec: 09 Parity row; Local Canon: D-709 | `test_capture_text_lines.py:164` | ✅ |
| AC-102.8 | guard | TEXT_FIXTURE_MULTILINE: `write_multiline_fixture` writes a 240×160 white original and its real bake equal to the committed `capture-fidelity-multiline-annotated.png`; `--multiline` writes only that pair; the default and `--region` runs write today's files | Local Canon: D-710 | `tests/unit/test_capture_bake_fixture.py:151`, `:175` | ✅ |
| AC-102.9 | behaviour | TEXT_LINE_PITCH: `segoeLinePitchPx(size)` equals `segoe_line_pitch[size]` for every size in the file, and `textLines('Hi\n\nHi\n')` is `['Hi', '', 'Hi', '']` | Spec: 09 Model row | `capture-text-lines.behavior.test.ts:303` | ✅ |
| AC-102.10 | behaviour | TEXT_PLATE_LINES: `textBackgroundBox` equals each `text_plates` box; for each multi-line text in the input matrix at sizes 8, 16, 32 and 64 it equals the union of its lines' unrounded extents, rounded and clamped once; a text with no `\n` gives today's box | Spec: 09 Parity row | `capture-text-lines.behavior.test.ts:314` | ✅ |
| AC-102.11 | behaviour | TEXT_SVG_LINES: `Hi\n\nHi` at `(10, 20)`, size 16, renders one `<text>` with three `<tspan>` children at `x` 10 and `y` 38, 60 and 82; `Hi` has no `<tspan>` | Spec: 09 Parity row; Local Canon: D-707 | `capture-text-lines.behavior.test.ts:338` | ✅ |
| AC-102.12 | behaviour | TEXT_DRAFT_KEYS: `Hi`, Shift+Enter, `Hi`, Enter in a new draft commits one mark `Hi\nHi`; Enter alone after `Hi` commits `Hi` | Spec: 09 Keys row | `capture-text-lines.behavior.test.ts:351` (§Departures 1) | ✅ |
| AC-102.13 | behaviour | The draft is a `<textarea>` with `wrap="off"` and `rows` equal to its line count, at least 1 | Spec: 09 Keys row, Parity row (C-3) | `capture-text-lines.behavior.test.ts:368` | ✅ |
| AC-102.14 | guard | Enter during IME composition neither commits nor closes the draft; Escape closes it with no mark | Spec: 09 Keys row | `capture-text-lines.behavior.test.ts:378` | ✅ |
| AC-102.15 | behaviour | TEXT_DRAFT_HINT: while the draft is open, `capture-text-draft-hint` reads exactly `Enter to finish, Shift+Enter for a new line, Esc to cancel` and the draft's `aria-describedby` names it; with no draft it is absent | Spec: 09 Keys row; Local Canon: D-706 | `capture-text-lines.behavior.test.ts:392` | ✅ |
| AC-102.16 | behaviour | One two-line mark traced from the draft's keydowns through `onTextDraftChange`, `onTextCommit` and `annotationsRef.current` to the recorded save POST body, which holds `Hi\nHi` exactly once | Session 55 RULE-3; Spec: 09 Keys row | `capture-text-lines.behavior.test.ts:405` | ✅ |
| AC-102.17 | behaviour | One mark traced from an annotate body holding `Hi\r\nHi` through `TextAnnotationIn`, `_annotations_from_in` and a recording `TextAnnotation` wrapper (one record) to the sidecar's `Hi\nHi` and an annotated PNG equal to the bake of `Hi\nHi` | Session 55 RULE-3; Spec: 09 Model row | `test_api_capture_text_lines.py:128` | ✅ |
| AC-102.18 | behaviour | Re-editing a saved mark `Hi\nHi` (Select-mode double-click, MEU-101) opens the draft with the value `Hi\nHi` | Spec: 09 Keys row; MEU-101 TEXT_REEDIT | `capture-text-lines.behavior.test.ts:423` | ✅ |
| AC-102.19 | behaviour | Electron: with the multi-line pair, the Original view's plate and ink box agree with the Annotated view's within 1 px at 100%, the image is 240×160, and each view has exactly 2 ink row runs whose ends agree within 1 px | Spec: 09 Parity row | `ui/tests/e2e/capture-inbox.test.ts:2371`; gate `ui-electron` | ✅ |
| AC-102.20 | guard | AC-82.6 passes unchanged through the parameterised seam; the default pair gives 1 ink run in each view | Local Canon: MEU-82 TEXT_PIXEL_ORACLE | `capture-inbox.test.ts:2394`, `:2267`; gate `ui-electron` | ✅ |
| AC-102.21 | behaviour | TEXT_MCP_DOC: the annotate description holds the D-711 sentence with backslash-n as two characters, holds neither `circle` nor `marker`, and the tool's actions are unchanged | Local Canon: D-711 | `mcp-server/tests/capture.test.ts:1658` | ✅ |
| AC-102.22 | check | Spec D3: 09's Delivered (Session 70) note after the §Multi-line text table, naming AC-102.1 to AC-102.24 and the plan folder; 09 keeps CRLF | Local Canon: D3 | row 5's check (`s70-r5-spec.txt`) | ✅ |
| AC-102.23 | guard | MARK_CLIP_TEXT: a crop keeps a multi-line text mark whose anchor is inside and moves it by the crop's origin with its text unchanged; a mark whose anchor is outside is dropped | Local Canon: D-675 | `test_capture_text_lines.py:187` | ✅ |
| AC-102.24 | behaviour | A Select-mode click inside the second line of `Hi\nHi` and outside the first selects the mark; a click below the last line selects nothing | Spec: 09 Parity row | `capture-text-lines.behavior.test.ts:439` | ✅ |
| AC-82 (cross-ref) | regression | AC-82.6 (TEXT_PIXEL_ORACLE) passes through the parameterised seam with the default pair; the seam's new `fixture` argument defaults to today's pair and mark | plan TEXT_PARITY_E2E; AC-102.20 | `capture-inbox.test.ts:2267`; `s70-r3-guard-e2e.txt`; gate `ui-electron` | ✅ |
| AC-90 (cross-ref) | regression | AC-90.8's default and `--region` fixture runs write today's files byte for byte; `--multiline` is exclusive with `--region` | plan TEXT_FIXTURE_MULTILINE; AC-102.8 | `tests/unit/test_capture_bake_fixture.py`; `s70-r2-fixture-py.txt`; gate `py-tests` | ✅ |
| AC-101 (cross-ref) | regression | MEU-101's re-edit (TEXT_REEDIT) opens the textarea with the stored text; its own tests pass with the draft as a textarea | plan AC-102.18 | `capture-page.behavior.test.ts`; gate `ui-tests` | ✅ |
| AC-59 (cross-ref) | regression | AC-59.16's annotate description pin (the two examples, no `circle` or `marker`) holds with the new sentence | plan §Pins that move | `mcp-server/tests/capture.test.ts:370`; gate `mcp-tests` | ✅ |
| AC-51.6 (cross-ref) | regression | The test-ids prefix hash is unchanged: `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` | plan §Files Modified (byte-hash guard) | `capture-action-row.test.ts:754-756`; gate `action-row` | ✅ |
| AC-81 (cross-ref) | regression | AC-81.13 hashes the same `test-ids.ts` prefix as AC-51.6 and still reads the same hash; the MEU-102 block sits after the hashed prefix | plan §Files Modified (byte-hash guard) | `capture-action-row.test.ts`; `s70-types-action-row.txt`; gate `action-row` | ✅ |
| AC-100 (cross-ref) | regression | AC-100.11 failed once in row 4's first Electron run and passed in three runs alone, in row 4's full rerun and in the gate (§Departures 2) | §Departures 2 | `capture-inbox.test.ts:3045`; `s70-r4-ac100-11-rerun.txt`; gate `ui-electron` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-102.2, .4, .5, .6 and .17 (pytest) | Row 3: `12 failed, 7 passed in 2.12s`, exit 1 (`s70-py-red.txt`). Decisive lines: `assert ['Hi\r\nHi'] == ['Hi\nHi']` and pixel differences against the `Hi\nHi` bake | Row 4: `377 passed in 22.58s` (`s70-py-green.txt`); gate `py-tests` | `test_capture_text_lines.py:87-144`, `test_api_capture_text_lines.py:110-128` |
| AC-102.9 to .13, .15, .16, .18, .24 (Vitest) | Row 3: `Tests 9 failed \| 2 passed (11)`, exit 1 (`s70-ui-red.txt`). Decisive lines: `size 1: expected +0 to be 6`; `"Hi\nHi"@8: expected { x: 10, y: 23, width: 19, height: 6 } to deeply equal { x: 10, y: 23, width: 8, height: 19 }`; `expected [] to have a length of 3 but got +0`; `Shift+Enter keeps the draft open: expected null not to be null`; `expected 'INPUT' to be 'TEXTAREA'`; `onTextDraftChange holds both lines: expected undefined to be 'Hi\nHi'`; `inside the second line, outside the first: expected false to be true` | Row 4: `Tests 196 passed (196)` over 7 files (`s70-ui-green.txt`); gate `ui-tests` | `capture-text-lines.behavior.test.ts:303-439` |
| AC-102.21 (MCP) | Row 3: `Tests 1 failed \| 57 skipped (58)`, exit 1 (`s70-mcp-red.txt`): `expected 'Workflow: call avkit_capture annotate…' to contain 'A text mark\'s text may hold \n to st…'` | Row 4: `Tests 58 passed (58)` (`s70-mcp-green.txt`); gate `mcp-tests` | `mcp-server/tests/capture.test.ts:1658` |
| AC-102.19 (Electron) | Row 3: `1 failed`, exit 1 (`s70-e2e-red.txt`): `Expected length: 2` / `Received length: 1` / `Received array: [{"bottom": 51, "top": 28}]` | Row 4: `49 passed (1.2m)` (`s70-e2e-green.txt`); gate `ui-electron` | `capture-inbox.test.ts:2371` |
| AC-102.1, .3, .7, .8, .14, .20, .23 | Guards, and AC-102.1 met by rows 1 and 2. AC-102.8 passed where row 2 wrote it (`s70-r2-fixture-py.txt`: `56 passed in 0.96s`). Row 3's guard runs: pytest `4 passed, 13 deselected in 0.14s` (`s70-r3-guard.txt`: AC-102.1, .3, .7, .23), Vitest `Tests 2 passed \| 9 skipped (11)` (`s70-r3-guard-ui.txt`: AC-102.1, .14), Electron `2 passed (5.8s)` (`s70-r3-guard-e2e.txt`: AC-82.6 and AC-102.20) and `1 passed (3.1s)` (`s70-r3-guard-e2e20.txt`: AC-102.20) | Row 4's runs and the gate | `test_capture_text_lines.py:66`, `:95`, `:164`, `:187`; `capture-text-lines.behavior.test.ts:292`, `:378`; `capture-inbox.test.ts:2394` |
| AC-102.22 | Row 5's check exits 1 before row 5 (plan §Verification Plan) | Row 5: all five keys `True` (`s70-r5-spec.txt`) | row 5 |

- **red-check.** Row 3's check (`s70-red-check.txt`) reads `red-check: 4 receipt(s), 16 required test(s), 0 problem(s)`. Every required failing block failed by assertion alone.
- **The passes in the Red runs.** pytest: AC-102.1, AC-102.3, AC-102.4's 251-pair case, AC-102.6's two CRLF cases without `bg_color`, AC-102.7 and AC-102.23. Vitest: AC-102.1 and AC-102.14. AC-102.6's CRLF cases without a plate pass at HEAD because Pillow draws no ink for the CR glyph, so the bytes already matched; with `bg_color` the plate widens (the plan's probe gives `(10, 26, 27, 60)` against `(10, 26, 25, 60)`), and those cases failed (§Departures 4).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-0-baseline", "command": "$env:RECEIPTS_DIR='C:/Temp/av-kit'; $env:PYTHONIOENCODING='utf-8'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-13-capture-text-multiline/baseline.ps1 *> C:/Temp/av-kit/s70-baseline.txt (task.md row 0's Validation cell, run as C:/Temp/av-kit/s70/rows/row0.ps1; base runs in C:/Temp/av-kit/s70-base-py.txt, s70-base-ui.txt, s70-base-mcp.txt, s70-base-e2e.txt, s70-base-ui-build.txt, s70-base-mcp-build.txt and s70-base-ruff.txt)", "scope": "Row 0: the D-712 words, the queue, the absent names and new files, the shapes (S7), baseline.sha, baseline-dirty.txt, the anchors and line endings, the lock syncs, the FFmpeg pair, the base runs, and the red-check, identity and id-length selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 4e35af9 before any row", "output": "budget: execution review budget to 30M (USER_EXPLICIT 2026-11-13 '30M (Recommended)'); queue: {'MEU-82': 'approved', 'MEU-101': 'approved', 'MEU-104': 'approved', 'MEU-102': 'pending'}; 4e35af9 is an ancestor of HEAD: True; absent names and labels: lines [] in each of the 12 files; shapes wrong (S7): []; missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; ffmpeg version n8.1.3-27-g8dca1586f4-20261031; base pytest 2459 passed, 37 warnings in 169.25s; base UI Tests 1322 passed; base MCP Tests 527 passed; base Electron 47 passed (1.1m); base ruff All checks passed!; red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; identity selftest exit 0; id-length selftest: 4 case(s), 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-1-types", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s70/rows/row1.ps1 > C:/Temp/av-kit/s70/rows/row1.out.txt 2>&1 (task.md row 1's Validation cell: pytest *> C:/Temp/av-kit/s70-types-py.txt; export_openapi.py --check *> C:/Temp/av-kit/s70-types-openapi.txt; pyright *> C:/Temp/av-kit/s70-types-pyright.txt; ruff *> C:/Temp/av-kit/s70-types-ruff.txt; npm --prefix ui run typecheck *> C:/Temp/av-kit/s70-types-ui.txt; capture-text-metrics.test.ts *> C:/Temp/av-kit/s70-types-metrics.txt; capture-action-row.test.ts *> C:/Temp/av-kit/s70-types-action-row.txt; sweep C:/Temp/av-kit/s70/row1-sweep.txt appended to C:/Temp/av-kit/s70-anchors.txt)", "scope": "Row 1: the type-only names (normalize_text_newlines as identity, TEXT_LINE_GAP, TEXT_LINE_GAP_PX, segoeLinePitchPx and textLines stubs, CAPTURE_TEXT_DRAFT_HINT) and the caller sweep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 4e35af9 plus rows 0 to 1", "output": "226 passed in 5.48s; export_openapi --check exit 0; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; ui typecheck exit 0; capture-text-metrics Tests 4 passed (4); capture-action-row Tests 13 passed (13); sweep 145 lines, anchors 169 lines"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-2-data", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s70/rows/row2.ps1 > C:/Temp/av-kit/s70/rows/row2.out.txt 2>&1 (task.md row 2's Validation cell: test_capture_bake_fixture.py *> C:/Temp/av-kit/s70-r2-fixture-py.txt; the data check *> C:/Temp/av-kit/s70-r2-data.txt; capture-text-metrics.test.ts *> C:/Temp/av-kit/s70-r2-metrics.txt; ruff *> C:/Temp/av-kit/s70-r2-ruff.txt; the pair written to ui/tests/e2e/fixtures, C:/Temp/av-kit/s70-r2-fixture-write.txt)", "scope": "Row 2: TEXT_FIXTURE_MULTILINE in the tool and the committed pair, TEXT_GEOMETRY's segoe_line_pitch and text_plates, AC-102.8", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 4e35af9 plus rows 0 to 2", "output": "56 passed in 0.96s; {'crlf_only': True, 'pitch_sizes': True, 'plates': True, 'pair_240x160': True}; capture-text-metrics Tests 4 passed (4); ruff All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-3-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s70/rows/row3.ps1 > C:/Temp/av-kit/s70/rows/row3.out.txt 2>&1 (task.md row 3's Validation cell: pytest tests/unit/test_capture_text_lines.py tests/e2e/test_api_capture_text_lines.py *> C:/Temp/av-kit/s70-py-red.txt; Vitest capture-text-lines.behavior.test.ts *> C:/Temp/av-kit/s70-ui-red.txt; MCP capture.test.ts -t AC-102 *> C:/Temp/av-kit/s70-mcp-red.txt; playwright capture-inbox.test.ts -g AC-102.19 *> C:/Temp/av-kit/s70-e2e-red.txt; red-check.py with the 16 --require ids *> C:/Temp/av-kit/s70-red-check.txt; the guards *> C:/Temp/av-kit/s70-r3-guard.txt, s70-r3-guard-ui.txt, s70-r3-guard-e2e.txt, s70-r3-guard-e2e20.txt; id-length.py *> C:/Temp/av-kit/s70-r3-id-length.txt; ruff *> C:/Temp/av-kit/s70-r3-ruff.txt; ui build *> C:/Temp/av-kit/s70-r3-ui-build.txt)", "scope": "MEU-102 Red: AC-102.2, .4 to .6 and .17 in pytest, AC-102.9 to .13, .15, .16, .18 and .24 in Vitest, AC-102.21 in MCP and AC-102.19 in Electron against the row 2 code; the AC-102.1, .3, .7, .14, .20 and .23 guards (AC-102.8 passed in row 2)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 4e35af9 plus rows 0 to 3", "output": "pytest 12 failed, 7 passed in 2.12s (child exit 1): assert ['Hi\\r\\nHi'] == ['Hi\\nHi']; pixel differences. Vitest Tests 9 failed | 2 passed (11) (child exit 1): size 1: expected +0 to be 6; expected 'INPUT' to be 'TEXTAREA'; Shift+Enter keeps the draft open: expected null not to be null. MCP Tests 1 failed | 57 skipped (58) (child exit 1). Electron 1 failed (child exit 1): Expected length: 2, Received length: 1. red-check: 4 receipt(s), 16 required test(s), 0 problem(s). Guards: 4 passed, 13 deselected in 0.14s; Tests 2 passed | 9 skipped (11); 2 passed (5.8s); 1 passed (3.1s). id-length: 19 test(s), 0 too long; ruff All checks passed!; ui build built in 4.29s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-4-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s70/rows/row4.ps1 > C:/Temp/av-kit/s70/rows/row4.out.txt 2>&1 (task.md row 4's Validation cell: pytest *> C:/Temp/av-kit/s70-py-green.txt, Vitest *> C:/Temp/av-kit/s70-ui-green.txt, MCP *> C:/Temp/av-kit/s70-mcp-green.txt, Electron *> C:/Temp/av-kit/s70-e2e-green.txt, pyright *> C:/Temp/av-kit/s70-r4-pyright.txt, ruff *> C:/Temp/av-kit/s70-r4-ruff.txt, export_openapi.py --check *> C:/Temp/av-kit/s70-r4-openapi.txt, the UI and MCP typechecks, ui lint and ui build *> C:/Temp/av-kit/s70-r4-ui-types.txt, s70-r4-mcp-types.txt, s70-r4-ui-lint.txt, s70-r4-ui-build.txt; the first targeted runs in C:/Temp/av-kit/s70/quick-py.txt, s70/quick-ui.txt and s70/quick-mcp.txt; the first full Electron run kept as C:/Temp/av-kit/s70-e2e-green-run1-ac100-11-flake.txt and the AC-100.11 rerun, C:/Temp/av-kit/s70/rows/rerun100.ps1, in C:/Temp/av-kit/s70-r4-ac100-11-rerun.txt)", "scope": "MEU-102 Green: TEXT_NEWLINES, TEXT_API_NEWLINES, TEXT_LINE_PITCH, TEXT_PLATE_LINES, TEXT_SVG_LINES, TEXT_DRAFT_KEYS, TEXT_DRAFT_HINT and TEXT_MCP_DOC, every caller and test row 1 recorded, and the plan's guards", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 4e35af9 plus rows 0 to 4", "output": "quick runs: 19 passed in 2.29s; Tests 1 failed | 10 passed (11), AC-102.12 expected [ 'Hi', 'Hi' ] to deeply equal [ 'Hi' ] (§Departures 1); Tests 58 passed (58). Electron run 1: 1 failed (AC-100.11, Expected - 2 / Received + 2), 48 passed (§Departures 2); AC-100.11 alone with --repeat-each 3: 3 passed (3.7s). Row 4: pytest 377 passed in 22.58s; Vitest Tests 196 passed (196) in 7 files; MCP Tests 58 passed (58); Electron 49 passed (1.2m); pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; export_openapi --check exit 0; typecheck and lint exit 0; ui build built in 4.12s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-5-spec", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s70/rows/row5.ps1 > C:/Temp/av-kit/s70/rows/row5.out.txt 2>&1 (task.md row 5's Validation cell *> C:/Temp/av-kit/s70-r5-spec.txt)", "scope": "Row 5 (D3, AC-102.22): 09's Delivered (Session 70) note after the Multi-line text rule table, before the redact-mark anchor; CRLF kept", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 4e35af9 plus rows 0 to 5", "output": "{'crlf_only': True, 'note_in_section': True, 'names_acs': True, 'plan_folder': True, 'one_note': True}"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-6-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s70/rows/row6.ps1 > C:/Temp/av-kit/s70/rows/row6.out.txt 2>&1 (task.md row 6's Validation cell: meu_status.py render --check *> C:/Temp/av-kit/s70-r6-render.txt and the status read *> C:/Temp/av-kit/s70-r6-status.txt; pre-status copies in C:/Temp/av-kit/s70/pre-status/)", "scope": "Row 6: MEU-102 ready_for_review with its execution_plan, the registry and BUILD_PLAN renders, and grouping row 46 executed, noting Session 70; band columns unchanged", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 4e35af9 plus rows 0 to 6", "output": "Drift check passed - SSOT loaded (142 MEUs, 12 phases); MEU-102: ('ready_for_review', 'P2') row 46: ['| 46 | `capture-text-multiline` | MEU-102 | P3 | executed (Session 70) | `docs/execution/plans/2026-11-13-capture-text-multiline/` |']"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-13-capture-text-multiline/session-gate.ps1 *> C:/Temp/av-kit/s70-gate-h1.txt (task.md row H1-2's Validation cell, run as C:/Temp/av-kit/s70/rows/rowH1-2.ps1; step receipts C:/Temp/av-kit/s70-D6-*.txt; outer receipt C:/Temp/av-kit/s70/rows/rowH1-2.out.txt)", "scope": "The plan's full gate: identity before; static py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest and id-length; fresh full py-tests, openapi, action-row (the AC-51.6 byte-hash guard), ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render and issues-render; runtime ui-electron; identity after. mcp-audit and build-record skipped by the plan", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; task-contract OK: 24 row(s), 22 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 32 outside scope: [] head moved (S3): False; red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; id-length: 19 test(s), 0 too long; py-tests 2480 passed, 37 warnings in 186.30s; openapi exit 0; action-row Tests 13 passed (13); ui-tests Test Files 124 passed (124), Tests 1333 passed (1333); ui-build built in 4.18s; mcp-types and mcp-build exit 0; mcp-tests Test Files 36 passed (36), Tests 528 passed (528); state-render Drift check passed - SSOT loaded (142 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 49 passed (1.2m); tested_state before = after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s70-h1-3-h1-4", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s70/rows/rowH1-3.ps1 > C:/Temp/av-kit/s70/rows/rowH1-3.out.txt 2>&1 (meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; meu_status.py get MEU-102 *> C:/Temp/av-kit/s70-h13-status.txt; check *> C:/Temp/av-kit/s70-h13-check.txt); pwsh -NoProfile -File C:/Temp/av-kit/s70/rows/rowH1-4.ps1 > C:/Temp/av-kit/s70/rows/rowH1-4.out.txt 2>&1 (export_openapi.py --check *> C:/Temp/av-kit/openapi-check.txt; git diff --stat against baseline.sha *> C:/Temp/av-kit/openapi-delta.txt; check *> C:/Temp/av-kit/openapi-delta-check.txt)", "scope": "H1-3 the MEU status read after the gate; H1-4 the OpenAPI snapshot check and its delta from baseline.sha: none", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95", "output": "MEU-102 ready_for_review: True; openapi --check exit 0; openapi delta from baseline: only rtk's banner line, no openapi.committed.json"}
```

### Quality Gate Results

The H1-2 gate's last line is `session-gate: all steps exit 0` (`s70-gate-h1.txt:120`). It passed on its first run.

- **Static.** pyright 0 errors, 0 warnings, 0 informations; ruff passed; UI typecheck and lint (`--max-warnings 0`) exit 0. The checks of the plan's own tooling also passed:
  - the task contract (24 rows, 22 fully checked, H1-5 and H2-1 exempt);
  - scope-paths (32 changed paths, none outside scope, head not moved);
  - the red-check selftest (49 fixtures, 0 wrong);
  - id-length (19 ids, 0 too long).
- **Suites, against the Session 70 baseline** (`s70-base-*.txt`).
  - pytest 2480 passed (`s70-D6-py-tests.txt`; 2459 + 21: the 19 tests in the two new files and AC-102.8's two tests);
  - Vitest 1333 passed in 124 files (`s70-D6-ui-tests.txt`; 1322 + 11 in the new file);
  - MCP 528 passed (`s70-D6-mcp-tests.txt`; 527 + AC-102.21);
  - Electron 49 passed (`s70-D6-ui-electron.txt`; 47 + AC-102.19 and AC-102.20).
- **Build.** UI build ok (4.18s, `s70-D6-ui-build.txt`); MCP typecheck and build exit 0; the OpenAPI check exit 0; the state and known-issues renders match.
- **The byte-hash guard.** `action-row` passed 13 tests (`s70-D6-action-row.txt`): AC-51.6 still reads `6E569F82…870FF454`.
- **After the gate.** H1-3 (`s70-h13-check.txt`: `MEU-102 ready_for_review: True`; `drift-check.txt`) and H1-4 (`openapi-delta-check.txt`: the delta holds only rtk's banner, so `openapi.committed.json` is unchanged from `baseline.sha`) both exit 0. H1-4's first run stopped on a `UnicodeEncodeError` (cp1252) while printing rtk's banner; it passed when rerun with `PYTHONIOENCODING=utf-8` set. `current-focus.md` and this handoff are outside `tested_state`.
- **Skipped by the plan.** `mcp-audit` (live network and YouTube, which the brief forbids; no action changed, so the audit baseline does not change) and `build-record` (no release and no package build).
- **Identity.** `tested_state` before and after: `4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95` (`s70-D6-identity-before.txt`, `s70-D6-identity-after.txt`).
- **Warnings.** pytest reports 37 warnings, the same count as the baseline run (`s70-base-py.txt`). No test fails on a warning.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/capture.py` | modified | `normalize_text_newlines` and its call in `TextAnnotation.__post_init__` (TEXT_NEWLINES) |
| `packages/api/src/avkit_api/schemas/captures.py` | modified | `TextAnnotationIn._fold_newlines` (TEXT_API_NEWLINES) |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `TEXT_LINE_GAP` and `spacing=` in `text_plate_box` and `_apply_text` (TEXT_LINE_GAP) |
| `tools/capture_bake_fixture.py`, `ui/tests/e2e/fixtures/capture-fidelity-multiline-original.png`, `capture-fidelity-multiline-annotated.png` | modified, new | TEXT_FIXTURE_MULTILINE and the pair it wrote |
| `ui/tests/e2e/fixtures/capture-geometry.json` | modified | `segoe_line_pitch` and `text_plates` (TEXT_GEOMETRY) |
| `ui/src/renderer/src/features/capture/capture-text-metrics.ts` | modified | `TEXT_LINE_GAP_PX`, `segoeLinePitchPx`, `textLines` and the multi-line `textBackgroundBox` (TEXT_LINE_PITCH, TEXT_PLATE_LINES) |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | The tspans, the textarea and the hint (TEXT_SVG_LINES, TEXT_DRAFT_KEYS, TEXT_DRAFT_HINT) |
| `ui/tests/e2e/test-ids.ts` | modified | The MEU-102 block appended (row 1) |
| `mcp-server/src/toolsets/capture.ts` | modified | The annotate description's sentence (TEXT_MCP_DOC) |
| `tests/unit/test_capture_text_lines.py`, `tests/e2e/test_api_capture_text_lines.py`, `ui/tests/unit/capture-text-lines.behavior.test.ts` | new | The MEU-102 tests. LF, 198, 156 and 448 lines |
| `tests/unit/test_capture_bake_fixture.py`, `mcp-server/tests/capture.test.ts`, `ui/tests/e2e/capture-inbox.test.ts` | modified | AC-102.8, AC-102.21, AC-102.19 and AC-102.20, and the seam's fixture argument (TEXT_PARITY_E2E) |
| `docs/build-plan/09-screenshot-capture.md` | modified | Row 5's Delivered (Session 70) note (D3) |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | Only MEU-102's fields and row, and grouping row 46 (row 6) |
| `.agent/context/current-focus.md` | modified | Session 70's paragraph (H1-3) |

`git diff --stat 4e35af9`, leaving out `docs/execution/` and the handoffs: `18 files changed, 545 insertions(+), 161 deletions(-)`, plus the three new test files and the two new PNGs.

Line endings were measured with Python bytes before each edit and kept:

- **CRLF.** `domain/capture.py`, `schemas/captures.py`, `adapter.py`, `tools/capture_bake_fixture.py`, `capture-geometry.json`, `capture-text-metrics.ts`, `CaptureViewport.tsx`, `test-ids.ts`, `mcp-server/src/toolsets/capture.ts`, `mcp-server/tests/capture.test.ts`, `test_capture_bake_fixture.py`, 09, the grouping file and `current-focus.md`.
- **LF.** `ui/tests/e2e/capture-inbox.test.ts`, `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md`.
- **New files** are LF; the PNGs are binary.

```diff
 # domain/capture.py (abridged)
+def normalize_text_newlines(text: str) -> str:
+    return text.replace("\r\n", "\n").replace("\r", "\n")
     def __post_init__(self) -> None:
+        if isinstance(self.text, str):
+            object.__setattr__(self, "text", normalize_text_newlines(self.text))
 # schemas/captures.py
+    @field_validator("text", mode="before")
+    @classmethod
+    def _fold_newlines(cls, value: object) -> object:
+        return normalize_text_newlines(value) if isinstance(value, str) else value
 # CaptureViewport.tsx, the text child and the draft's keys (abridged)
+        {ann.text.includes('\n')
+          ? textLines(ann.text).map((line, index) => (
+              <tspan key={index} x={ann.x}
+                y={svgTextBaselineY(ann) + index * segoeLinePitchPx(ann.font_size)}>
+                {line}
+              </tspan>
+            ))
+          : ann.text}
+                if (event.key === 'Enter' && !event.shiftKey) {
```

The excerpt is abridged. The sources are `domain/capture.py:345-366`, `schemas/captures.py:126-130` and `CaptureViewport.tsx:332-342`, `:1563-1568`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-13-capture-text-multiline-implementation-critical-review.md`, on the ledger loop `s70-execution-2026-11-13-capture-text-multiline` (budget 30,000,000 tokens, cap 6 rounds, D-712). The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | 0 (intent achieved: yes; 10,712,142 of 30,000,000 tokens) | `4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95` |

### Verdict

approved in round 1 of 6 with no findings. The report was validated under `C:/Temp/av-kit` and copied byte for byte (sha256 `3db4eaeb18c592bf6529eaf03ada729fc357c7026ba7e2326f7ac833e64ddbb7`); H1-7a wrote `C:/Temp/av-kit/review-state.json` and H1-7b reported `OK: approved at round 1 of 6, 0 open blocking findings` (`C:/Temp/av-kit/exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `ruff check tools/` fails on errors in `tools/issue_triage*` and `tools/meu_status*` that were there before this session | observation | None | Session 68 DEP-1; this plan lints only the files it edits |
| The band mismatch: grouping P3, `meu-status.yaml` P2 | observation | Mat | Session 70 prompt: named, not changed |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2) |

### Departures and their basis

1. **AC-102.12 changed during Green (row 4, S2).** Row 4 says no test file changes (S2), and S2 says to stop. The coordinator edited the test and did not stop. The first UI run (`s70/quick-ui.txt`) failed only AC-102.12's second half, `AssertionError: expected [ 'Hi', 'Hi' ] to deeply equal [ 'Hi' ]`. The test read the mark that `Enter alone after Hi` commits as `textMarks()[1]`. Both marks sit at one point, and the DOM order of the marks is not their commit order, so index 1 was the first mark. The line `expect(linesOf(textMarks()[1] as Element)).toEqual(['Hi'])` became `expect(textMarks().map((el) => linesOf(el)).sort()).toEqual([['Hi'], ['Hi', 'Hi']])`, with the comment "Both marks sit at one point and the DOM order is not the commit order: match by content." The assertion still requires exactly two marks, one `Hi\nHi` and one `Hi`. No AC text and no source changed for it.
2. **AC-100.11 failed once (row 4).** Row 4's first full Electron run (`s70-e2e-green-run1-ac100-11-flake.txt`) gave 1 failed, 48 passed: AC-100.11 at `capture-inbox.test.ts:3045`, a deep-equality check whose array read `[1, 1, 3, 3]` where `[1, 1, 5, 6]` was expected, after `Timeout 5000ms exceeded while waiting on the predicate`. MEU-102 doesn't touch the code it reads. Alone with `--repeat-each 3` it passed 3 of 3 (`s70-r4-ac100-11-rerun.txt`), the full rerun passed 49 (`s70-e2e-green.txt`) and the gate passed 49. No earlier handoff records this failure. It is recorded as a timing flake, not fixed.
3. **AC-102.8 compares decoded pixels.** As AC-90.8 does, the test compares the decoded image (mode, size and pixel data, through `_pixels`) with the committed PNG, not the file bytes, so a different PNG encoder version cannot fail it. The AC text says "bytes".
4. **AC-102.6's CRLF cases without `bg_color` passed at Red.** Pillow draws no ink for the CR glyph, so `Hi\r\nHi` already baked the same pixels as `Hi\nHi` when there is no plate. The cases with `bg_color` failed at Red (the plate was 2 px wider), and so did the lone-CR cases. red-check required the failing ids only.
5. **The AC-82.6 filter also matched AC-102.20.** Row 3's guard run `-g 'AC-82\.6 '` matched both AC-82.6 and AC-102.20, whose title holds "AC-82.6 passes" (`s70-r3-guard-e2e.txt`: `2 passed`). Row 3 also ran AC-102.20 alone (`s70-r3-guard-e2e20.txt`: `1 passed`).
6. **H1-4's first run** stopped on a `UnicodeEncodeError` printing rtk's banner under cp1252, before its check ran. The rerun with `PYTHONIOENCODING=utf-8` passed. No file changed between the runs.
7. **B-4 at plan time.** See §Scope. No execution row read the inbox or the database.

Departure 1 changed a test file after row 3 (S2). No departure changed an AC's text. No execution-stage decision was needed, so the plan's YAML ends at D-712.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-13 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, row 1's sweep, the Red and Green receipts, the H1-2 gate and the evidence records (H1-6) |
| Execution review | 2026-11-13 | codex-independent-reviewer | Round 1 approved, 0 findings, 10,712,142 tokens; H1-7a and H1-7b passed |
