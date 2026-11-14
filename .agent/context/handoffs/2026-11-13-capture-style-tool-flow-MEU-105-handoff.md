---
date: "2026-11-14"
project: "capture-style-tool-flow"
meu: "MEU-105"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-13-capture-style-tool-flow/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-13-capture-text-multiline-MEU-102-handoff.md"
---

# Handoff: 2026-11-13-capture-style-tool-flow-MEU-105-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-105 `gui-capture-style-tool-flow`. This is the fourth of the five capture annotation editor sessions, Sessions 68 to 72 (grouping D-674). It is grouping slice 6 (D-159), and it holds only the style half of that slice after the split (D-713).

- **Colour applies on click.** A named pick commits at once and the menu shows `Named` again (COLOR_NAMED). The hex field commits on Enter or blur when `normalizeHex` accepts its text. Text it refuses commits nothing, blocks nothing and is never sent (COLOR_HEX). The colour well and the text background well preview on `input` and commit once on the native `change` (COLOR_WELL, TEXT_BG_WELL). The Apply and Cancel buttons, the colour gate and its status message are gone (COLOR_GATE_GONE). One pick, one well gesture or one drag is one undo step.
- **Each tool keeps its own style.** Arrow, Box, Highlight, Text and Pixelate each remember a colour and a size, as nine new `capture` settings leaves (STYLE_SETTINGS, D-714 to D-716):
  - the service refuses a colour that doesn't match `#` and six hex digits, a number that isn't a whole `int`, and a value out of range, naming the key only. An integer of any size is compared with its range before any `float()`;
  - the API refuses `3.0`, `true` and `"3"` with a 422 through `StrictInt` (STYLE_API);
  - MCP's `avkit_settings` describes and accepts the leaves (STYLE_MCP);
  - `readToolStyles` reads them back leaf by leaf with a per-leaf fallback (STYLE_MODEL);
  - one ordered write queue keeps the stored value equal to the last commit, and a GET can't install an older style over a newer one (STYLE_STORE).
- **What a commit targets (D-719).**
  - With a mark selected, a style control restyles only that mark, as one undo step (STYLE_TARGET).
  - With none selected, it saves the armed tool's style and writes no undo step. A new mark draws from its tool's saved style (STYLE_DRAW), and the fields show that style (STYLE_DISPLAY).
  - A new text draft takes the text style at once; a re-edited text mark is restyled instead (TEXT_DRAFT_STYLE).
- **Select with nothing selected shows no style field** (SELECT_NO_STYLE, D-721).
- **Pixelate block size gets the scrub handle** that Stroke and Size have, `capture-block-size-scrub`, clamped to 2 and 100 (BLOCK_SCRUB, D-722).
- **Help and the actions index.** The Annotation tools help drops `; Apply commits color` and adds the click-to-apply and per-tool sentence (STYLE_HELP). `gui-actions-index.md` gains `capture:style_mark` and `capture:style_tool` (STYLE_ACTIONS_INDEX).

The OpenAPI snapshot changes only by the nine `SettingsPutIn` leaves (H1-4). The MCP audit baseline does not change: no action is added.

**Build Plan Section**: bp09, `docs/build-plan/09-screenshot-capture.md` §Style and tool flow, with its split header note and its Delivered (Session 71) note.

**Predecessor**: [MEU-102 handoff](2026-11-13-capture-text-multiline-MEU-102-handoff.md), Session 70. The grouping is `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md` (row 47). These decisions carry: D-158 (human, `USER_EXPLICIT` 2026-10-29 "all recommendations are accepted"), D-159, D-160, D-674 and D-675.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-14.
- **The plan review.** Codex approved the plan at round 3 (`.agent/context/handoffs/2026-11-13-capture-style-tool-flow-plan-critical-review.md`). The three rounds spent 24,330,246 of the 27,000,000 tokens that Mat set with "About 20M (Recommended)" (D-726) and "Add 7M (Recommended)" (D-728).
- **The gate.** Mat set the execution review budget, "33M (Recommended)", and said "Execute now (Recommended)" (D-727).
- No ruling was needed during execution.

**The split (D-713, human).** Mat ruled "A" (`USER_EXPLICIT` 2026-11-13).
- **MEU-105 holds** the Colour row, the Tool style row and the Modifiers row's Pixelate block-size scrub.
- **The new MEU-143 `gui-capture-tool-flow`** (Session 71b, grouping row 47b, matrix row 9.31a, `pending`) holds the rest:
  - the Lock row: on by default, persisted, a one-shot preference, the just-drawn mark stays selected, and an armed press on the selected mark edits it;
  - the Letters row: V A R H T X E C, the crop X cases and the field guard;
  - the rest of the Modifiers row: Shift, Alt and Shift+arrow 10 px.
- **The records.** Rows 5 and 6 wrote the split into 09, the matrix, `meu-status.yaml` and the grouping (SPLIT_SPEC, SPLIT_MATRIX, SPLIT_STATUS, SPLIT_GROUPING). MEU-106 now depends on MEU-143 as well. MEU-107 still depends only on MEU-105 (D-724).

**Band mismatch (named, not changed).** The grouping's §3 heading and tracker row 47 say P3; `.agent/context/meu-status.yaml` says `band: P2` for MEU-105. MEU-143 copies the pair: P2 in `meu-status.yaml` and P3 in grouping row 47b (D-725). `meu_status.py get` reads `"band": "P2"` for both (`s71-h13-status.txt`, `s71-h13-status-143.txt`).

**OpenAPI and MCP change (D-717), against the prompt's expectation.** The Session 71 prompt expected the OpenAPI document and MCP to stay as they are, because tool style is never mark JSON. They change all the same, for the settings path, not for marks:
- `SettingsPutIn` forbids extra keys, so each style leaf had to be added there. The committed snapshot was regenerated with `tools/export_openapi.py`, not edited by hand. `s71-r2-openapi-delta.txt` and `openapi-delta-check.txt` both read `SettingsPutIn added: ['arrow_color', 'arrow_stroke', 'box_color', 'box_stroke', 'highlight_color', 'pixelate_block_size', 'text_bg_color', 'text_color', 'text_font_size'] rest of the document unchanged: True`.
- The MCP `avkit_settings` set schema is strict, and its get already returns every key the service holds. Without the leaves, an agent would read the style keys and then be refused when it wrote them back.
- No mark schema, sidecar, bake, annotate body or capture action changes (AC-105.30).

**Receipts.** A receipt named by its file name alone (`s71-*.txt`, `drift-check.txt`, `openapi-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s71/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **A tool's style.**
  - **Writers.** `saveToolStyle`, from a commit with no mark selected; an agent's `avkit_settings` set; the Settings API.
  - **The page's two commit paths.** `commitColor` (`CapturePage.tsx:1563`) calls `saveToolStyle` at `:1597`. `saveSizeStyle` (`:1482`) calls it at `:1492`. Its callers are the Stroke, Block size and Size commits (`:1407`, `:1429`, `:1471`) and a scrub's release (`:1730`).
  - **The client store.** `saveCaptureToolStyle` (`capture-style-store.ts:76`) maps the patch through `TOOL_STYLE_LEAVES` (`capture-tool-style.ts:28`), parses the body with `captureStylePutSchema` (`settings-schemas.ts:99`), merges it into the cache at once, and chains one `PUT /settings/capture` on the shared queue.
  - **The API.** `SettingsPutIn` takes the leaves as `str | None` and `StrictInt | None` (`schemas/settings.py:59-68`). `SettingsService._encode` (`services/settings.py:148`) applies the `integer` branch (`:157`) before any `float()`, the range check, and the `pattern` check (`:182`).
  - **Readers.** `fetchCaptureSettings` (`capture-style-store.ts:29`) is the shared `queryFn` of `CAPTURE_SETTINGS_KEY` in both hooks (`useCaptureSettings.ts:76`). It keeps any style leaf whose last commit had not succeeded when its GET started. `readToolStyles` (`capture-tool-style.ts:103`) falls back leaf by leaf. `toolStyles` (`CapturePage.tsx:398`) feeds STYLE_DISPLAY and STYLE_DRAW (`createDrawnMark`, `:317`), keyed by `styleToolFor(tool, redactMode)` (`:467`).
  - **Failures.** A failed PUT sets `STYLE_SAVE_FAILED` (`:106`, `Couldn't save the tool style`), which names no value. It drops its own leaves from the store, and the query is refetched once the queue is empty (AC-105.31).
- **A mark's colour, stroke, font size, background and block size.** A commit with that mark selected writes them, as one undo step. They reach the save POST body through `annotationsRef.current`, as before. No style key enters mark JSON (AC-105.30).
- **The hex field's text.** The viewport holds the typed text. `normalizeHex` runs at the commit (Enter or blur), and text it refuses is never sent (AC-105.9). The well's native `change` listener is added through a ref (`CaptureViewport.tsx:666`, `:678`). The named menu stays controlled at `value=""` (`:1169`).

Three traces use recording fakes (Session 55 RULE-3):
- AC-105.20 follows a named pick to the save POST body;
- AC-105.21 follows a hex commit to the recorded PUT body `{ "arrow_color": "#12ABCD" }` and the next arrow's colour;
- AC-105.22 follows the API body through `SettingsPutIn` and a recording `set_namespace` wrapper to the next GET.

### Row 1's sweep (S55 RULE-1, S59 RULE-1, S62 RULE-4, S63 RULE-1, S66 RULE-1, S68 RULE-2)

**What the sweep covered.**
- Before its edits, row 1 swept `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` at `5e9ea7c` (`s71-r1-pin-sweep.txt`, 373 lines). It appended the hits to `s71-anchors.txt` (451 lines), whose row 0 part holds each target's SHA-256 and line endings.
- The sweep has one section per name row 1 lists. These are every caller and pin of `optionGroups(`, `SettingSpec(`, `SETTINGS_KEY_TABLE`, `SettingsPutIn`, `settingsLeaves`, `SETTINGS_SCHEMA`, `capturePutSchema`, `CaptureScrubFieldProps`, `clampScrub`, `createDrawnMark`, `inspectMark`, `changeTextBg`, `applyColor`, `cancelColor` and the four colour props.
- It also has a section for every reader of the eight colour, background and block-size test ids, for the five literal strings, for `CAPTURE_COLOR_APPLY`, `CAPTURE_COLOR_CANCEL` and `COLOR_GATE_MESSAGE`, and for the capture key-set pins.

**The pins the plan named.** They moved as the plan says (the table below). These hold as the plan says:
- `capture-crop-tool.behavior.test.ts:903` (crop gives `[]`);
- the `<=` and `in` subset checks in `tests/e2e/test_api_capture_flatten.py:136` and `:508`;
- the `annotated_format` readers in the settings and card tests.

**A pin the plan didn't name.** `capture-page.behavior.test.ts:1566`, in the AC-65.3 test at `:1563`, expected `['capture-tool-select', ['color', 'stroke']]`. That expectation is keyed by the tool button's test id, so the name sweep did not list it. Row 3 moved it to `['capture-tool-select', []]` for SELECT_NO_STYLE (§Departures 1).

**The byte-hash guard.** Row 1 appended `// MEU-105 Capture style (additive IDs).` and `CAPTURE_BLOCK_SIZE_SCRUB = 'capture-block-size-scrub'` after the MEU-102 block (`test-ids.ts:519-520`), past the hashed prefix. AC-51.6 reads `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` (`capture-action-row.test.ts:755-756`), unchanged. Row 1's own run passed 13 tests (`s71-types-action-row.txt`: `Tests  13 passed (13)`), and so did row 3's hash run (`s71-r3-hash.txt`: `Tests  1 passed | 12 skipped (13)`) and the gate's `action-row` step (`s71-D6-action-row.txt`: `Tests  13 passed (13)`).

### The moved pins, before and after

| Pin | File and line now | Ending | Before | After | Row |
|---|---|---|---|---|---|
| AC-36.12 (the capture key set) | `tests/unit/test_capture_service.py:20`, `:39`, `:419` | CRLF | `CAPTURE_KEYS` and `CAPTURE_DEFAULTS` held today's seven keys | they gain the nine leaves and their defaults | 2 |
| AC-38.6 (the MCP capture keys) | `mcp-server/tests/capture.test.ts:46`, `:65`, `:213` | CRLF | the same seven keys | the same nine leaves and defaults | 2 |
| AC-60.8 (hex and well commits) | `ui/tests/unit/capture-page.behavior.test.ts:692` | CRLF | Apply wrote the colour and Cancel wrote nothing | the hex field commits on Enter, the well on `change`, and there is no Cancel | 3 |
| AC-60.8 (the gate status) | `:1088` | CRLF | invalid hex text turned Save off with `Apply or Cancel color` | Save stays on, and the status never reads `Apply or Cancel color` | 3 |
| AC-60.8 (no Apply) | `:1137` | CRLF | Apply was off until the candidate differed | a named pick paints the selected mark at once | 3 |
| AC-60.8 (the load arms Select) | `:723` | CRLF | read `hexBefore` from `capture-color` and expected it not to be green | expects `capture-color` to be absent until the mark is picked | 4 (§Departures 3) |
| AC-60.13 (Select's controls) | `:815` | CRLF | the Select tool showed Apply and Cancel | asserts the buttons are absent | 3 |
| MEU65_OPTION_IDS (the colour group) | `capture-page.behavior.test.ts`, the MEU-65 block at `:1440` | CRLF | well, hex, Apply, Cancel, Named | `capture-color-well`, `capture-color`, `capture-named-color` | 3 |
| AC-65.3 (the Select row) | `:1566` | CRLF | `['capture-tool-select', ['color', 'stroke']]` | `['capture-tool-select', []]` | 3 (§Departures 1) |
| AC-81.4 (the colour ids, in order) | `ui/tests/unit/capture-action-row.test.ts:490`; title at `:470` | CRLF | five ids, Apply and Cancel among them | the same three ids, in that order; the title says "well, hex, Named" | 3 (§Departures 2) |
| The help sentence | `capture-action-row.test.ts:68`, `ui/tests/unit/capture-help-content.test.ts:9` | CRLF | `…tabbed to; Apply commits color.` | ends after `tabbed to.` | 3 |
| AC-85.11 (the scrub sentence) | `capture-help-content.test.ts:77`, test at `:80` | CRLF | `Drag the Stroke or Size label` | `Drag the Stroke, Size or Block size label` | 3 |
| AC-65.1 (the expected table) and the select line | `ui/tests/unit/capture-toolbar.test.ts:112`, `:143` | CRLF | `optionGroups('select', null)` contained `stroke` | `select` with nothing selected gives `[]` | 3 |
| AC-60.12 (typed hex) | `ui/tests/e2e/capture-inbox.test.ts:602` | LF | clicked `capture-color-apply` | presses Enter in `capture-color` | 3 |

### Row 2's data (D-714 to D-717)

- **What row 2 wrote.** STYLE_SETTINGS, STYLE_API (with the regenerated snapshot), STYLE_MCP and the two key-set pins.
- **The new pytest files** are LF:
  - `tests/unit/test_capture_style_settings.py` (147 lines) holds AC-105.1 (Python), .2 and .3;
  - `tests/e2e/test_api_capture_style.py` (118 lines) holds AC-105.4 and .22.
- **The MCP test.** AC-105.5 was appended to `mcp-server/tests/capture.test.ts:1718` (CRLF).
- **The runs.**
  - pytest `245 passed in 20.13s` (`s71-r2-py.txt`);
  - MCP `Tests  301 passed (301)` (`s71-r2-mcp.txt`);
  - pyright `0 errors, 0 warnings, 0 informations` (`s71-r2-pyright.txt`);
  - ruff `All checks passed!` on the two new files (`s71-r2-ruff.txt`);
  - `id-length: 73 test(s), 0 too long` (`s71-r2-id-length.txt`).

### Row 3's Red tests (S50 RULE-2, S61 RULE-3, S66 RULE-2)

Row 3 wrote two new files, both LF:
- `ui/tests/unit/capture-tool-style.test.ts` (232 lines) holds AC-105.1 (TypeScript), .6, .7, .19's `optionGroups` half and .24;
- `ui/tests/unit/capture-style-flow.behavior.test.ts` (1074 lines; 1145 after the execution round 1 corrections) holds AC-105.8 to .18, .19's page half, .20, .21, .23, .27, .28, .30, .31 and .32, with a recording fake server for `GET` and `PUT /settings/capture` and the save POST.

It appended AC-105.26 to `ui/tests/e2e/capture-inbox.test.ts:3397` (LF), and it moved the UI pins in the table above. `s71-r3-moved.txt` reads `Tests  15 failed | 153 passed (168)` over 4 files, exit 1. Those are the moved pins, which fail against the row 2 code, as expected before Green.

### Row 4's Green changes (S55 RULE-1)

Row 4 changed these files, keeping each file's endings:
- **Model and store.** STYLE_MODEL's bodies (`capture-tool-style.ts`), STYLE_STORE (`capture-style-store.ts`, `useCaptureToolStyles.ts`, `useCaptureSettings.ts`) and `captureStylePutSchema` (`settings-schemas.ts`).
- **Toolbar and scrub.** SELECT_NO_STYLE (`capture-toolbar.ts:148`) and BLOCK_SCRUB's `min` (`CaptureScrubField.tsx:20`, `:53`).
- **Viewport.** COLOR_NAMED, COLOR_HEX, COLOR_WELL, TEXT_BG_WELL, COLOR_GATE_GONE and BLOCK_SCRUB (`CaptureViewport.tsx`).
- **Page.** STYLE_DISPLAY, STYLE_TARGET, STYLE_DRAW, the colour commits, TEXT_DRAFT_STYLE, BLOCK_SCRUB's `SizeBurst` field and COLOR_GATE_GONE (`CapturePage.tsx`).
- **Help.** STYLE_HELP (`capture-help-content.ts`).
- **Unchanged.** `openapi.committed.json` did not change from row 2 (`s71-r4-openapi.txt`, exit 0).

**First runs.** The first broad UI run over `tests/unit/capture` and `tests/unit/settings` had one failure: AC-60.8 at `capture-page.behavior.test.ts:723`, `TestingLibraryElementError: Unable to find an element by: [data-testid="capture-color"]`. A shot that loads with marks arms Select, and SELECT_NO_STYLE hides the fields. The pin moved (§Departures 3), and the rerun passed 676 tests in 46 files. That run's receipt was not kept in `RECEIPTS_DIR`; row 4's command then exited 0 with the receipts below.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-105.1 | type | The exact signatures: `SettingSpec.pattern` and `SettingSpec.integer`; `StyleTool`, `ToolStyle`, `ToolStyles`, `TOOL_STYLE_DEFAULTS`, `TOOL_STYLE_LEAVES`, `styleToolFor`, `styleToolOfMark`, `readToolStyles`; `useCaptureToolStyles()`; `fetchCaptureSettings` and `resetCaptureStyleStore`; `CaptureScrubFieldProps.min`; `CAPTURE_BLOCK_SIZE_SCRUB`. Row 1 added the names, so it passed where it was written | Local Canon: D-714 | `tests/unit/test_capture_style_settings.py:36`; `ui/tests/unit/capture-tool-style.test.ts:109` | ✅ |
| AC-105.2 | behaviour | STYLE_SETTINGS: the nine `capture` rows with their defaults, returned by `get_namespace("capture")` on a fresh store, one id per leaf; `arrow_stroke` is the `int` 3 | Spec: 09 Tool style row; Local Canon: D-715, D-716 | `test_capture_style_settings.py:46`, `:54`, `:63` | ✅ |
| AC-105.3 | behaviour | `_encode` refuses the bad colours, `3.5`, `3.0`, `True`, 0 and 101 for `arrow_stroke`, 1 and 101 for `pixelate_block_size`, and `10**400` with `ValidationError`, not `OverflowError`; accepts an empty `text_bg_color`; each message holds the key, not the value | Local Canon: D-714 | `test_capture_style_settings.py:73` to `:143` (`10**400` at `:134`) | ✅ |
| AC-105.4 | behaviour | STYLE_API: the nine leaves give 200 and a GET returns them; `3.0`, `true`, `"3"`, a number for a colour, `#GGGGGG`, `10**400` and an unknown key give 422, not 500; no body echoes a refused value; the OpenAPI document equals the committed snapshot | Local Canon: D-717 | `tests/e2e/test_api_capture_style.py:64`, `:74`, `:85` | ✅ |
| AC-105.5 | behaviour | STYLE_MCP: `SETTINGS_SCHEMA.namespaces.capture` lists the seven keys and the nine leaves with defaults; the set schema accepts the valid body and refuses `2.5`, `true` and a number colour; the actions are unchanged | Local Canon: D-717 | `mcp-server/tests/capture.test.ts:1718` | ✅ |
| AC-105.6 | behaviour | STYLE_MODEL: `styleToolFor` for every tool × mode and `styleToolOfMark` for every mark type; both maps have every `StyleTool` | Spec: 09 Tool style row; Local Canon: D-715 | `capture-tool-style.test.ts:145`, `:162` | ✅ |
| AC-105.7 | behaviour | `readToolStyles` keeps each valid leaf and replaces only the bad one: missing, wrong type, short hex, empty colour, lone surrogate, control character, a float, out of range; an empty `text_bg_color` is kept; `undefined` and `null` give the defaults | Local Canon: D-716 | `capture-tool-style.test.ts:170`, `:203` | ✅ |
| AC-105.8 | behaviour | COLOR_NAMED: a named `orange` pick paints the selected arrow `#FFA500` as one step that Ctrl+Z takes back; the menu shows `Named`; no Apply or Cancel element exists | Spec: 09 Colour row | `ui/tests/unit/capture-style-flow.behavior.test.ts:489` | ✅ |
| AC-105.9 | behaviour | COLOR_HEX: typed text applies only on Enter or blur, as one step; refused text paints nothing, leaves Save on and the tools working, and blur or Escape shows the current colour | Spec: 09 Colour row | `capture-style-flow.behavior.test.ts:504` | ✅ |
| AC-105.10 | behaviour | COLOR_WELL: three `input` events add no step and one `change` adds exactly one; an equal colour adds none | Spec: 09 Colour row | `capture-style-flow.behavior.test.ts:543`, `:561` | ✅ |
| AC-105.11 | behaviour | TEXT_BG_WELL: three `input` events and one `change` on the Bg well add one step; Clear adds one more | Spec: 09 Colour row | `capture-style-flow.behavior.test.ts:569` | ✅ |
| AC-105.12 | behaviour | STYLE_TARGET: with one of two arrows selected, a colour and a stroke commit restyle only it, send no style PUT, and the next arrow keeps the tool's style | Spec: 09 Tool style row; Local Canon: D-719 | `capture-style-flow.behavior.test.ts:593` | ✅ |
| AC-105.13 | behaviour | With Arrow armed and nothing selected, a hex commit sends one PUT `{ arrow_color }`, a Stroke drag one PUT `{ arrow_stroke }` at release, no undo step, other tools unchanged | Spec: 09 Tool style row; Local Canon: D-719, D-720 | `capture-style-flow.behavior.test.ts:610` | ✅ |
| AC-105.14 | behaviour | STYLE_DRAW: each newly drawn mark carries its own tool's style and none of the others' | Spec: 09 Tool style row | `capture-style-flow.behavior.test.ts:648` | ✅ |
| AC-105.15 | behaviour | STYLE_DISPLAY: the fields follow the armed tool, a selected mark, and the tool again after the selection clears | Spec: 09 Tool style row | `capture-style-flow.behavior.test.ts:696` | ✅ |
| AC-105.16 | behaviour | A page mounted on stored `#123456` and stroke 7 shows and draws them; a stored `nope` shows `#E0AF68` | Spec: 09 Tool style row | `capture-style-flow.behavior.test.ts:722`, `:736` | ✅ |
| AC-105.17 | behaviour | TEXT_DRAFT_STYLE: in a new draft a colour commit sends one PUT `{ text_color }` and the mark takes it; a re-edit restyles the mark as one step with no PUT; a Bg commit and Clear show on the open draft, new or re-edited (execution round 1 F2) | Spec: 09 Tool style row; Session 55 RULE-1; Review: execution round 1 F2 | `capture-style-flow.behavior.test.ts:743`, `:776` | ✅ |
| AC-105.18 | behaviour | BLOCK_SCRUB: the handle exists in the block group; a drag on a selected pixelate is one step clamped to 2 and 100; Escape restores; with Pixelate armed one drag sends one PUT `{ pixelate_block_size }` | Spec: 09 Modifiers row (B-12); Local Canon: D-722 | `capture-style-flow.behavior.test.ts:811`, `:839` | ✅ |
| AC-105.19 | behaviour | SELECT_NO_STYLE: `optionGroups('select', null, mode)` is `[]` for both modes, and the page shows no style field; a selected arrow still gives `['color', 'stroke']` | Local Canon: D-721 | `capture-tool-style.test.ts:213`, `:220`; `capture-style-flow.behavior.test.ts:851` | ✅ |
| AC-105.20 | behaviour | Trace: one named pick through `onNamedColor`, the page's commit and `annotationsRef.current` to the save POST body, `#FFA500`, the arrow once | Session 55 RULE-3 | `capture-style-flow.behavior.test.ts:862` | ✅ |
| AC-105.21 | behaviour | Trace: one hex commit through `saveToolStyle` and `captureStylePutSchema` to the PUT body `{ "arrow_color": "#12ABCD" }`, then to the next arrow's colour in the save body | Session 55 RULE-3 | `capture-style-flow.behavior.test.ts:875` | ✅ |
| AC-105.22 | behaviour | Trace: one API body through `SettingsPutIn`, a recording `set_namespace` wrapper (one call), the stored values and the next GET | Session 55 RULE-3 | `test_api_capture_style.py:95` | ✅ |
| AC-105.23 | behaviour | The Settings card: after a style PUT the card's unsaved edit stays, its Save sends exactly the seven keys, and a later GET still returns the style leaves | Session 55 RULE-1 | `capture-style-flow.behavior.test.ts:892` | ✅ |
| AC-105.24 | behaviour | STYLE_HELP: the new sentence exactly, `Drag the Stroke, Size or Block size label`, and no `Apply commits color` | Spec: 09 Colour and Tool style rows | `capture-tool-style.test.ts:224` | ✅ |
| AC-105.25 | check | STYLE_ACTIONS_INDEX: `capture:style_mark` and `capture:style_tool` follow `capture:tool_lock`; `gui-actions-audit.test.ts` passes | Local Canon: GUI actions index | row 5's check (`s71-r5-spec.txt`, `s71-r5-actions.txt`) | ✅ |
| AC-105.26 | behaviour | Electron: a named pick repaints the selected arrow with no Apply button and Save posts `#FFA500`; with Arrow armed a hex Enter sends one style PUT and the next arrow has the colour | Spec: 09 Colour and Tool style rows | `ui/tests/e2e/capture-inbox.test.ts:3397`; gate `ui-electron` | ✅ |
| AC-105.27 | guard | The Redact mode is not saved (D-680); a solid redact and an eraser draw as today; the crop shows no style group | Local Canon: D-680 | `capture-style-flow.behavior.test.ts:1089` | ✅ |
| AC-105.28 | guard | MEU-85's Stroke and Size scrubs and MEU-99's Ctrl+Z and Ctrl+Y pass unchanged | Local Canon: MEU-85, MEU-99 | `capture-style-flow.behavior.test.ts:1110` (§Departures 4) | ✅ |
| AC-105.29 | check | The split records in 09, the matrix, `meu-status.yaml` and the grouping; `render --check` passes; endings kept | Human-approved: D-713 | row 6's check (`s71-r6-status.txt`, `s71-r6-render.txt`) | ✅ |
| AC-105.30 | guard | No style key enters mark JSON; `AnnotateIn`, the sidecar, the bake and `clip_mark` (D-675) are unchanged | Spec: 09 Tool style row; Local Canon: D-675 | `capture-style-flow.behavior.test.ts:1136` | ✅ |
| AC-105.31 | behaviour | A failed style PUT shows `Couldn't save the tool style`, names no value there or on the Console, and refetches once the queue is empty | Session 50 RULE-1; Local Canon: D-720 | `capture-style-flow.behavior.test.ts:922` | ✅ |
| AC-105.32 | behaviour | STYLE_STORE's queue: commits reach the server in order; a failure followed by a held commit sends one GET after both; a stale GET answer never replaces a newer commit, with or without a failure first; a commit made while the first GET is held, or after it fails, reaches the next drawn mark (execution round 1 F1) | Review: plan round 1 F1, round 2 F3, execution round 1 F1; Local Canon: D-720 | `capture-style-flow.behavior.test.ts:948`, `:977`, `:1003`, `:1032`, `:1053`, `:1074` | ✅ |
| AC-36 (cross-ref) | regression | AC-36.12's capture key set gains the nine leaves and their defaults, in table order | plan §Pins that move; STYLE_SETTINGS | `tests/unit/test_capture_service.py:419`; `s71-r2-py.txt`; gate `py-tests` | ✅ |
| AC-37 (cross-ref) | regression | Held, not moved: AC-37.13 reads a fake that holds only the seven card keys, so the new leaves don't reach it | plan §Pins that move ("These were read and hold") | `tests/e2e/test_api_captures.py:737`; gate `py-tests` | ✅ |
| AC-38 (cross-ref) | regression | AC-38.6's MCP capture keys gain the same nine leaves and defaults | plan §Pins that move; STYLE_MCP | `mcp-server/tests/capture.test.ts:213`; `s71-r2-mcp.txt`; gate `mcp-tests` | ✅ |
| AC-39 (cross-ref) | regression | Held, not moved: AC-39.4 counts the card's capture PUTs only around card edits, where no style changes | plan §Pins that move ("These were read and hold") | `capture-page.behavior.test.ts:373`; gate `ui-tests` | ✅ |
| AC-57 (cross-ref) | regression | Held, not moved: AC-57.1's header row and the Electron Settings card test count PUTs only around card edits | plan §Pins that move ("These were read and hold") | `capture-page.behavior.test.ts:1199`; `capture-inbox.test.ts:669`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-60 (cross-ref) | regression | AC-60.8, AC-60.12 and AC-60.13 move from the Apply/Cancel gate to click-to-apply; AC-60.8's load check moved in Green | plan §Pins that move; COLOR_GATE_GONE; §Departures 3 | `capture-page.behavior.test.ts:692`, `:718`, `:815`, `:1088`, `:1137`; `capture-inbox.test.ts:468`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-65 (cross-ref) | regression | AC-65.1's table gives `[]` for Select with nothing selected; AC-65.3's Select row expects `[]` | plan SELECT_NO_STYLE; §Departures 1 | `capture-toolbar.test.ts:112`, `:143`; `capture-page.behavior.test.ts:1563`; gate `ui-tests` | ✅ |
| AC-68 (cross-ref) | regression | Held, not moved: AC-68.8's isolation keys stay the seven output paths, because no new leaf is path-like | plan §User Review Required (D-717) | `mcp-server/tests/audit/isolation.test.ts:29`; gate `mcp-tests` | ✅ |
| AC-81 (cross-ref) | regression | AC-81.4's colour group is well, hex, Named in that order; AC-81.13 still re-pins AC-51.6's hash | plan §Pins that move; §Departures 2 | `capture-action-row.test.ts:470`, `:490`, `:720`; gate `action-row` | ✅ |
| AC-85 (cross-ref) | regression | AC-85.11's scrub sentence names Block size; the Stroke and Size scrubs keep one step per gesture | plan BLOCK_SCRUB, STYLE_HELP; AC-105.28 | `capture-help-content.test.ts:80`; gate `ui-tests` | ✅ |
| AC-99 (cross-ref) | regression | MEU-99's Ctrl+Z and Ctrl+Y step the new style commits as one entry each; AC-99.7 passes in Electron | AC-105.8, AC-105.28 | `capture-inbox.test.ts:2966`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-100 (cross-ref) | regression | AC-100.11 passed in row 4's Electron run and in the gate; it did not fail this session | Session 71 prompt | `capture-inbox.test.ts:3045`; `s71-e2e-green.txt`; gate `ui-electron` | ✅ |
| AC-101 (cross-ref) | regression | MEU-101's text re-edit: a colour commit while re-editing restyles that mark, with no style PUT; AC-101.6 passes in Electron | AC-105.17; TEXT_DRAFT_STYLE | `capture-inbox.test.ts:3100`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-103 (cross-ref) | regression | Held, not moved: AC-103.17's MODE_GROUPS table has no select-with-nothing row, and the redact block-size reads find the input by its id, which BLOCK_SCRUB keeps | plan §Pins that move ("These were read and hold") | `ui/tests/unit/capture-redact.behavior.test.ts:307`, `:319`; gate `ui-tests` | ✅ |
| AC-141 (cross-ref) | regression | Held, not moved: AC-141.16's audit input and output keys stand, because no new leaf is path-like | plan §User Review Required (D-717) | `mcp-server/tests/audit/isolation.test.ts:82`; gate `mcp-tests` | ✅ |
| AC-143 (cross-ref) | reserved | The AC-143 family is reserved for MEU-143 (Session 71b, D-713). This session writes no AC-143 row and no AC-143 test | plan §Planning receipts (`s71/id-probe.txt`) | None | ⏳ Session 71b |
| AC-51.6 (cross-ref) | regression | The test-ids prefix hash is unchanged: `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` | plan §Files Modified (byte-hash guard) | `capture-action-row.test.ts:755-756`; `s71-r3-hash.txt`; gate `action-row` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-105.6 to .21, .23, .24, .31 and .32 (Vitest) | Row 3: `Tests  28 failed \| 6 passed (34)`, exit 1 (`s71-ui-red.txt`). Decisive lines: `arrow × solid: expected null to be 'arrow'`; `expected 16 to be 24`; `expected <button…> to be null`; `expected '#E0AF68' to be '#12ABCD'`; `expected [] to have a length of 1 but got +0`; `capture-block-size-scrub: expected null not to be null`; `capture-color: expected <input…> to be null`; `solid: expected [ 'color', 'stroke' ] to deeply equal []`; `expected 'Apply or Cancel color' to contain 'Couldn\'t save the tool style'`; `expected 'Six annotation tools…' to contain 'A swatch applies when you pick it…'` | Row 4: `Tests  337 passed (337)` over 15 files (`s71-ui-green.txt`); gate `ui-tests` | `capture-tool-style.test.ts:145-224`; `capture-style-flow.behavior.test.ts:489-1032` |
| AC-105.17 Bg draft, AC-105.32 held and failed first GET (execution round 1 F1, F2) | `Tests  3 failed \| 26 skipped (29)`, exit 1 (`s71-fix-r1-red.txt`). Decisive lines: `the new draft shows the Bg: expected '' to be '#112233'`; `before the GET answers: expected '#E0AF68' to be '#12ABCD'`; `with no settings loaded: expected '#E0AF68' to be '#12ABCD'`. red-check: `1 receipt(s), 3 required test(s), 0 problem(s)` (`s71-fix-r1-red-check.txt`) | `Tests  29 passed (29)` for the whole file (`s71-fix-r1-green.txt`); gate `ui-tests` | `capture-style-flow.behavior.test.ts:776`, `:1053`, `:1074` |
| AC-105.26 (Electron) | Row 3: `1 failed`, exit 1 (`s71-e2e-red.txt`): `expect(locator).toHaveCount(expected) failed`, `Expected: 0` / `Received: 1` for the Apply button | Row 4: `50 passed (1.1m)` (`s71-e2e-green.txt`); gate `ui-electron` | `capture-inbox.test.ts:3397` |
| AC-105.1 to .5, .22, .27, .28, .30 | Met by rows 1 and 2, or guards. Row 2's tests passed where written (`s71-r2-py.txt`: `245 passed in 20.13s`; `s71-r2-mcp.txt`: `Tests  301 passed (301)`). Row 3's guard runs: AC-105.1 TS `Tests  1 passed \| 7 skipped (8)` (`s71-r3-guard-1.txt`), AC-105.27 and .28 `Tests  2 passed \| 24 skipped (26)` (`s71-r3-guard-27-28.txt`), AC-105.30 `Tests  1 passed \| 25 skipped (26)` (`s71-r3-guard-30.txt`) | Row 4's runs and the gate | `test_capture_style_settings.py:36-143`; `test_api_capture_style.py:64-95`; `capture.test.ts:1718`; `capture-tool-style.test.ts:109`; `capture-style-flow.behavior.test.ts:1089`, `:1110`, `:1136` |
| AC-105.25, AC-105.29 | Row 5's and row 6's checks exit 1 before their rows (plan §Verification Plan) | Row 5: all 11 keys `True` (`s71-r5-spec.txt`) and `Tests  19 passed (19)` (`s71-r5-actions.txt`); row 6: all 13 keys `True` (`s71-r6-status.txt`) | rows 5 and 6 |

- **red-check.** Row 3's check (`s71-red-check.txt`) reads `red-check: 2 receipt(s), 21 required test(s), 0 problem(s)`. The 21 required ids are AC-105.6 to .21, .23, .24, .26, .31 and .32, and every required failing block failed by assertion alone. The round 1 corrections' check (`s71-fix-r1-red-check.txt`) reads `red-check: 1 receipt(s), 3 required test(s), 0 problem(s)`; its `.exit` file holds the `exit=1` the run printed from `$LASTEXITCODE`. This table cites no other id as failing at Red.
- **The passes in the Red runs.** The 6 Vitest passes in `s71-ui-red.txt` are AC-105.1 (TypeScript), AC-105.10's equal-colour case, AC-105.19's selected-arrow case, AC-105.27, AC-105.28 and AC-105.30. The two negatives pass at HEAD because they assert behaviour today's code already has.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-0-baseline", "command": "$env:RECEIPTS_DIR='C:/Temp/av-kit'; $env:PYTHONIOENCODING='utf-8'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-13-capture-style-tool-flow/baseline.ps1 *> C:/Temp/av-kit/s71-baseline.txt (task.md row 0's Validation cell, written to a .ps1 from the cell text and run with pwsh -NoProfile -File; base runs in C:/Temp/av-kit/s71-base-py.txt, s71-base-ui.txt, s71-base-mcp.txt, s71-base-e2e.txt, s71-base-ui-build.txt, s71-base-mcp-build.txt and s71-base-ruff.txt)", "scope": "Row 0: the D-727 words, the queue, the absent names and new files, the shapes (S7), baseline.sha, baseline-dirty.txt, the anchors and line endings, the lock syncs, the FFmpeg pair, the base runs, and the identity and id-length selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c before any row", "output": "budget: execution review budget to 33M (USER_EXPLICIT 2026-11-14 '33M (Recommended)'); queue: MEU-87, MEU-99 and MEU-100 approved, MEU-105 and MEU-106 pending, MEU-143 None; 5e9ea7c is an ancestor of HEAD: True; absent names lines [] in each file; shapes wrong (S7): []; missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; ffmpeg version n8.1.3-27-g8dca1586f4-20261031; base pytest 2480 passed, 37 warnings in 165.14s; base UI Test Files 124 passed (124), Tests 1333 passed (1333); base MCP Tests 528 passed (528) in 36 files; base Electron 49 passed (1.2m); base ruff All checks passed!; base UI build built in 3.77s; identity selftest 0 failures; id-length selftest: 4 case(s), 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-1-types", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71-r1-cmd.ps1 > C:/Temp/av-kit/s71-r1-run.txt 2>&1 (task.md row 1's Validation cell: pytest *> C:/Temp/av-kit/s71-types-py.txt; export_openapi.py --check *> C:/Temp/av-kit/s71-types-openapi.txt; pyright *> C:/Temp/av-kit/s71-types-pyright.txt; ruff *> C:/Temp/av-kit/s71-types-ruff.txt; npm --prefix ui run typecheck *> C:/Temp/av-kit/s71-types-ui.txt; ui lint *> C:/Temp/av-kit/s71-types-ui-lint.txt; the three UI files *> C:/Temp/av-kit/s71-types-ui-tests.txt; capture-action-row.test.ts *> C:/Temp/av-kit/s71-types-action-row.txt; sweep C:/Temp/av-kit/s71-r1-pin-sweep.txt appended to C:/Temp/av-kit/s71-anchors.txt)", "scope": "Row 1: the type-only names (SettingSpec.pattern and integer read by nothing, the capture-tool-style.ts stubs and both maps, the useCaptureToolStyles and capture-style-store stubs, CaptureScrubFieldProps.min, CAPTURE_BLOCK_SIZE_SCRUB) and the caller sweep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c plus rows 0 to 1", "output": "157 passed in 16.22s; export_openapi --check exit 0; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; ui typecheck and lint exit 0; Test Files 3 passed (3), Tests 155 passed (155); capture-action-row Tests 13 passed (13); sweep 373 lines, anchors 451 lines"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-2-settings", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71-r2-cmd.ps1 > C:/Temp/av-kit/s71-r2-run.txt 2>&1 (task.md row 2's Validation cell: pytest *> C:/Temp/av-kit/s71-r2-py.txt; export_openapi.py --check *> C:/Temp/av-kit/s71-r2-openapi.txt; the delta check *> C:/Temp/av-kit/s71-r2-openapi-delta.txt; pyright *> C:/Temp/av-kit/s71-r2-pyright.txt; ruff on the two new files *> C:/Temp/av-kit/s71-r2-ruff.txt; id-length.py *> C:/Temp/av-kit/s71-r2-id-length.txt; mcp typecheck *> C:/Temp/av-kit/s71-r2-mcp-types.txt; MCP tests *> C:/Temp/av-kit/s71-r2-mcp.txt)", "scope": "Row 2: STYLE_SETTINGS, STYLE_API with the regenerated snapshot, STYLE_MCP, the AC-36.12 and AC-38.6 pins, AC-105.1 (Python), .2 to .5 and .22", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c plus rows 0 to 2", "output": "245 passed in 20.13s; export_openapi --check exit 0; SettingsPutIn added: ['arrow_color', 'arrow_stroke', 'box_color', 'box_stroke', 'highlight_color', 'pixelate_block_size', 'text_bg_color', 'text_color', 'text_font_size'] rest of the document unchanged: True; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; id-length: 73 test(s), 0 too long; mcp typecheck exit 0; Test Files 20 passed (20), Tests 301 passed (301)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-3-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71-r3-cmd.ps1 > C:/Temp/av-kit/s71-r3-run.txt 2>&1 (task.md row 3's Validation cell: Vitest capture-tool-style.test.ts and capture-style-flow.behavior.test.ts *> C:/Temp/av-kit/s71-ui-red.txt; playwright capture-inbox.test.ts -g AC-105.26 *> C:/Temp/av-kit/s71-e2e-red.txt; red-check.py with the 21 --require ids *> C:/Temp/av-kit/s71-red-check.txt; the guards *> C:/Temp/av-kit/s71-r3-guard-1.txt, s71-r3-guard-27-28.txt, s71-r3-guard-30.txt; the hash run *> C:/Temp/av-kit/s71-r3-hash.txt; the moved pins *> C:/Temp/av-kit/s71-r3-moved.txt; ui build *> C:/Temp/av-kit/s71-r3-ui-build.txt; the AC-105.28 retry in C:/Temp/av-kit/s71-r3-g28-try.txt)", "scope": "MEU-105 Red: AC-105.6 to .21, .23, .24, .31 and .32 in Vitest and AC-105.26 in Electron against the row 2 code; the AC-105.1, .27, .28 and .30 guards; the AC-51.6 hash; the moved pins failing before Green", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c plus rows 0 to 3", "output": "Vitest Test Files 2 failed (2), Tests 28 failed | 6 passed (34) (child exit 1): arrow × solid: expected null to be 'arrow'; expected '#E0AF68' to be '#12ABCD'; capture-block-size-scrub: expected null not to be null. Electron 1 failed (child exit 1): toHaveCount Expected: 0 Received: 1. red-check: 2 receipt(s), 21 required test(s), 0 problem(s). Guards: Tests 1 passed | 7 skipped (8); Tests 2 passed | 24 skipped (26); Tests 1 passed | 25 skipped (26); hash Tests 1 passed | 12 skipped (13). Moved pins: Tests 15 failed | 153 passed (168) in 4 files (child exit 1, expected before Green). ui build built in 3.50s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-4-green", "command": "pwsh -NoProfile -File row4.ps1 (task.md row 4's Validation cell, written to a .ps1 from the cell text: npm --prefix ui run typecheck *> C:/Temp/av-kit/s71-r4-ui-types.txt; ui lint *> C:/Temp/av-kit/s71-r4-ui-lint.txt; Vitest over the 15 recorded files *> C:/Temp/av-kit/s71-ui-green.txt; ui build *> C:/Temp/av-kit/s71-r4-ui-build.txt; Electron capture-inbox.test.ts *> C:/Temp/av-kit/s71-e2e-green.txt; pytest *> C:/Temp/av-kit/s71-py-green.txt; export_openapi.py --check *> C:/Temp/av-kit/s71-r4-openapi.txt; MCP capture.test.ts *> C:/Temp/av-kit/s71-mcp-green.txt)", "scope": "MEU-105 Green: STYLE_MODEL, STYLE_STORE, SELECT_NO_STYLE, BLOCK_SCRUB, COLOR_NAMED, COLOR_HEX, COLOR_WELL, TEXT_BG_WELL, COLOR_GATE_GONE, STYLE_DISPLAY, STYLE_TARGET, STYLE_DRAW, TEXT_DRAFT_STYLE and STYLE_HELP; every caller and test row 1 recorded; the plan's guards", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c plus rows 0 to 4", "output": "first broad run: 1 failed, AC-60.8 TestingLibraryElementError: Unable to find an element by: [data-testid=\"capture-color\"] (§Departures 3); rerun Test Files 46 passed (46), Tests 676 passed (676). Row 4: typecheck and lint exit 0; Test Files 15 passed (15), Tests 337 passed (337); ui build built in 3.61s; Electron 50 passed (1.1m); pytest 223 passed in 21.28s; export_openapi --check exit 0; MCP Tests 59 passed (59)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-5-spec", "command": "pwsh -NoProfile -File row5.ps1 (task.md row 5's Validation cell, written to a .ps1 from the cell text: the spec and index check *> C:/Temp/av-kit/s71-r5-spec.txt; gui-actions-audit.test.ts *> C:/Temp/av-kit/s71-r5-actions.txt)", "scope": "Row 5 (D3, AC-105.25, SPLIT_SPEC): STYLE_ACTIONS_INDEX, 09's split header note, the MEU-143 table row, MEU-106's dependency, the two MEU-143 sentences and the Delivered (Session 71) note; CRLF kept", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c plus rows 0 to 5", "output": "{'index_crlf': True, 'index_order': True, 'crlf_09': True, 'header_names_143': True, 'row_143_after_136': True, 'meu106_deps': True, 'c_letter': True, 'note_in_section': True, 'names_acs': True, 'plan_folder': True, 'one_note': True}; Test Files 1 passed (1), Tests 19 passed (19)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-6-status", "command": "pwsh -NoProfile -File row6.ps1 (task.md row 6's Validation cell, written to a .ps1 from the cell text: the status and split check *> C:/Temp/av-kit/s71-r6-status.txt; meu_status.py render --check *> C:/Temp/av-kit/s71-r6-render.txt; the canon tests *> C:/Temp/av-kit/s71-r6-canon.txt; pre-status copies in C:/Temp/av-kit/s71/pre-status/)", "scope": "Row 6 (AC-105.29, SPLIT_MATRIX, SPLIT_STATUS, SPLIT_GROUPING): MEU-105 ready_for_review with its execution_plan, MEU-143 pending, MEU-106's dependency, the P2 band range, matrix row 9.31a, grouping rows 47 and 47b and §9.9, the registry and BUILD_PLAN renders", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c plus rows 0 to 6", "output": "{'meu105': True, 'meu106_deps': True, 'meu143': True, 'p2_band': True, 'status_lf': True, 'row47': True, 'row47b': True, 'sec_9_9': True, 'grouping_crlf': True, 'matrix_31a': True, 'matrix_32': True, 'matrix_band': True, 'matrix_crlf': True}; Drift check passed - SSOT loaded (143 MEUs, 12 phases); Test Files 2 passed (2), Tests 14 passed (14)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-fix-r1-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71/fix-r1-red.ps1 > C:/Temp/av-kit/s71-fix-r1-red.txt 2>&1 (npx vitest run tests/unit/capture-style-flow.behavior.test.ts -t with the three new titles, from P:/av-kit/ui with ELECTRON_RUN_AS_NODE removed); red-check.py with the three --require titles > C:/Temp/av-kit/s71-fix-r1-red-check.txt", "scope": "Execution round 1 F1 and F2, Red: the AC-105.17 Bg draft test and the two AC-105.32 first-GET tests against the code Codex reviewed in round 1", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c plus rows 0 to 6 and the three new tests", "output": "Tests 3 failed | 26 skipped (29) (child exit 1): the new draft shows the Bg: expected '' to be '#112233'; before the GET answers: expected '#E0AF68' to be '#12ABCD'; with no settings loaded: expected '#E0AF68' to be '#12ABCD'. red-check: 1 receipt(s), 3 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-fix-r1-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71/fix-r1-green.ps1 > C:/Temp/av-kit/s71-fix-r1-green.txt 2>&1 (npx vitest run tests/unit/capture-style-flow.behavior.test.ts, from P:/av-kit/ui with ELECTRON_RUN_AS_NODE removed)", "scope": "Execution round 1 F1 and F2, Green: committedStyleLeaves and subscribeCommittedStyleLeaves in capture-style-store.ts, the hook's fallback in useCaptureToolStyles.ts, and the draft background in CaptureViewport.tsx", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e9ea7c plus rows 0 to 6 and the round 1 corrections", "output": "Test Files 1 passed (1), Tests 29 passed (29), exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; pwsh -NoProfile -File docs/execution/plans/2026-11-13-capture-style-tool-flow/session-gate.ps1 > C:/Temp/av-kit/s71-gate-h1-r1fix.txt 2>&1 (task.md row H1-2's gate, rerun after the execution round 1 corrections, with RECEIPTS_DIR=C:/Temp/av-kit and PYTHONIOENCODING=utf-8; step receipts C:/Temp/av-kit/s71-D6-*.txt; the first run's receipts are kept in C:/Temp/av-kit/s71/gate-r0/)", "scope": "The plan's full gate: identity before; static py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest and id-length; fresh full py-tests, openapi, action-row (the AC-51.6 byte-hash guard), ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render and issues-render; runtime ui-electron; identity after. mcp-audit and build-record skipped by the plan", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "5e9ea7c520e02e856babe21d5116677a53bd108e+dabfe448a5cd0746c0f3e02b7c52214ac88f296fdf836e70f166be3d55597adc", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; ui-types and ui-lint exit 0; task-contract OK: 24 row(s), 22 row(s) fully checked, 2 row(s) exempt (view_file): H1-5, H2-1; scope-paths changed paths: 45 outside scope: [] head moved (S3): False; red-check selftest: 58 fixture(s) (18 positive, 40 negative), 0 wrong; id-length: 73 test(s), 0 too long; py-tests 2553 passed, 37 warnings in 154.43s; openapi exit 0; action-row Tests 13 passed (13); ui-tests Test Files 126 passed (126), Tests 1370 passed (1370); ui-build built in 4.23s; mcp-types and mcp-build exit 0; mcp-tests Test Files 36 passed (36), Tests 529 passed (529); state-render Drift check passed - SSOT loaded (143 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 50 passed (1.3m); tested_state before = after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71-h1-3-h1-4", "command": "pwsh -NoProfile -File h13.ps1 (task.md row H1-3's Validation cell: meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; meu_status.py get MEU-105 *> C:/Temp/av-kit/s71-h13-status.txt; meu_status.py get MEU-143 *> C:/Temp/av-kit/s71-h13-status-143.txt; check *> C:/Temp/av-kit/s71-h13-check.txt); pwsh -NoProfile -File h14.ps1 (task.md row H1-4's Validation cell: export_openapi.py --check *> C:/Temp/av-kit/openapi-check.txt; delta check against baseline.sha *> C:/Temp/av-kit/openapi-delta-check.txt)", "scope": "H1-3 the MEU-105 and MEU-143 status reads after the gate; H1-4 the OpenAPI snapshot check and its delta from baseline.sha: the nine SettingsPutIn leaves only; rerun after the gate rerun", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "5e9ea7c520e02e856babe21d5116677a53bd108e+dabfe448a5cd0746c0f3e02b7c52214ac88f296fdf836e70f166be3d55597adc", "output": "Drift check passed - SSOT loaded (143 MEUs, 12 phases); MEU-105 ready_for_review: True MEU-143 pending: True; openapi --check exit 0; SettingsPutIn added: ['arrow_color', 'arrow_stroke', 'box_color', 'box_stroke', 'highlight_color', 'pixelate_block_size', 'text_bg_color', 'text_color', 'text_font_size'] rest of the document unchanged: True"}
```

### Quality Gate Results

The H1-2 gate's last line is `session-gate: all steps exit 0`. It passed on its first run (`s71-gate-h1.txt:120`, receipts kept in `C:/Temp/av-kit/s71/gate-r0/`), and again after the execution round 1 corrections (`s71-gate-h1-r1fix.txt:119`). The figures below are the rerun's.

- **Static.** pyright `0 errors, 0 warnings, 0 informations` (`s71-D6-py-types.txt`); ruff `All checks passed!` (`s71-D6-py-lint.txt`); UI typecheck and lint (`--max-warnings 0`) exit 0. The checks of the plan's own tooling also passed:
  - the task contract: `24 row(s)`, `22 row(s) fully checked`, `2 row(s) exempt (view_file): H1-5, H2-1` (`s71-D6-task-contract.txt`);
  - scope-paths: `changed paths: 45 outside scope: []`, `head moved (S3): False` (`s71-D6-scope-paths.txt`);
  - the red-check selftest: `58 fixture(s) (18 positive, 40 negative), 0 wrong` (`s71-D6-red-check-selftest.txt`);
  - id-length: `73 test(s), 0 too long` (`s71-D6-id-length.txt`).
- **Suites, against the Session 71 baseline** (`s71-base-*.txt`):
  - pytest `2553 passed, 37 warnings in 154.43s` (`s71-D6-py-tests.txt`). The baseline had 2480, so 73 tests are new, and id-length checked 73 new ids;
  - Vitest `Tests  1370 passed (1370)` in 126 files (`s71-D6-ui-tests.txt`). The baseline had 1333 in 124 files; the two new files hold the 34 tests of row 3's Red run and the 3 of the round 1 corrections;
  - MCP `Tests  529 passed (529)` (`s71-D6-mcp-tests.txt`): the baseline's 528 plus AC-105.5;
  - Electron `50 passed (1.3m)` (`s71-D6-ui-electron.txt`): the baseline's 49 plus AC-105.26. AC-100.11 passed.
- **Build.** UI build `built in 4.23s` (`s71-D6-ui-build.txt`); MCP typecheck and build exit 0; the OpenAPI check exit 0; the state and known-issues renders match.
- **The byte-hash guard.** `action-row` passed `Tests  13 passed (13)` (`s71-D6-action-row.txt`), so AC-51.6 still reads `6E569F82…870FF454`.
- **After the gate.**
  - H1-3 and H1-4 were run again after the gate rerun, with the same results.
  - H1-3 exits 0. `s71-h13-check.txt` reads `MEU-105 ready_for_review: True MEU-143 pending: True`; `drift-check.txt` passed.
  - H1-4 exits 0. `openapi-delta-check.txt` shows only the nine `SettingsPutIn` leaves, with the rest unchanged.
  - `current-focus.md` and this handoff are outside `tested_state`.
- **Skipped by the plan.** `mcp-audit` was skipped because it needs the live network and YouTube, which the brief forbids. No action changed, so the audit baseline does not change. `build-record` was skipped because there is no release and no package build.
- **Identity.** `tested_state` before and after the rerun: `5e9ea7c520e02e856babe21d5116677a53bd108e+dabfe448a5cd0746c0f3e02b7c52214ac88f296fdf836e70f166be3d55597adc` (`s71-D6-identity-before.txt`, `s71-D6-identity-after.txt`). The first run's was `5e9ea7c520e02e856babe21d5116677a53bd108e+00d1e9c8c9d98494d81511972f28e4acf9c0c23abee55be4a7a209aff85da0f3`.
- **Warnings.** pytest reports 37 warnings, the same count as the baseline run (`s71-base-py.txt`). No test fails on a warning.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/settings.py` | modified | `COLOR_HEX`, `COLOR_HEX_OR_EMPTY`, `SettingSpec.pattern` and `integer`, the nine rows, `_encode`'s checks (STYLE_SETTINGS) |
| `packages/api/src/avkit_api/schemas/settings.py`, `openapi.committed.json` | modified | The nine `SettingsPutIn` leaves and the regenerated snapshot (STYLE_API) |
| `mcp-server/src/toolsets/settings.ts` | modified | `SETTINGS_SCHEMA` and `settingsLeaves` entries (STYLE_MCP) |
| `ui/src/renderer/src/features/capture/capture-tool-style.ts`, `capture-style-store.ts`, `useCaptureToolStyles.ts` | new | STYLE_MODEL and STYLE_STORE. LF, 126, 189 and 37 lines (149 and 33 before the execution round 1 corrections) |
| `ui/src/renderer/src/features/capture/useCaptureSettings.ts`, `ui/src/renderer/src/features/settings/settings-schemas.ts` | modified | The shared `queryFn` and `captureStylePutSchema` (STYLE_STORE) |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | STYLE_DISPLAY, STYLE_TARGET, STYLE_DRAW, the colour commits, TEXT_DRAFT_STYLE, BLOCK_SCRUB's burst field, COLOR_GATE_GONE |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | COLOR_NAMED, COLOR_HEX, COLOR_WELL, TEXT_BG_WELL, COLOR_GATE_GONE, BLOCK_SCRUB; TEXT_DRAFT_STYLE's background on the open draft (execution round 1 F2) |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts`, `CaptureScrubField.tsx`, `capture-help-content.ts` | modified | SELECT_NO_STYLE, BLOCK_SCRUB's `min`, STYLE_HELP |
| `ui/tests/e2e/test-ids.ts` | modified | The MEU-105 block appended (row 1) |
| `tests/unit/test_capture_style_settings.py`, `tests/e2e/test_api_capture_style.py`, `ui/tests/unit/capture-tool-style.test.ts`, `ui/tests/unit/capture-style-flow.behavior.test.ts` | new | The MEU-105 tests. LF, 147, 118, 232 and 1145 lines (1074 before the execution round 1 corrections) |
| `tests/unit/test_capture_service.py`, `mcp-server/tests/capture.test.ts`, `ui/tests/e2e/capture-inbox.test.ts`, `ui/tests/unit/capture-page.behavior.test.ts`, `capture-action-row.test.ts`, `capture-help-content.test.ts`, `capture-toolbar.test.ts` | modified | The moved pins, AC-105.5 and AC-105.26 |
| `docs/build-plan/09-screenshot-capture.md`, `docs/build-plan/gui-actions-index.md` | modified | SPLIT_SPEC and the Delivered (Session 71) note; STYLE_ACTIONS_INDEX (row 5) |
| `docs/build-plan/build-priority-matrix.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | SPLIT_MATRIX, SPLIT_STATUS and SPLIT_GROUPING; MEU-105's status and plan; grouping row 47 `executed (Session 71)` (row 6) |
| `.agent/context/current-focus.md` | modified | Session 71's paragraph (H1-3) |

`git diff --stat 5e9ea7c`, leaving out `docs/execution/` and the handoffs, reads `27 files changed, 841 insertions(+), 206 deletions(-)`. The seven new files above come on top of that.

Line endings were measured with Python bytes before each edit, and each file kept its endings:

- **CRLF.** `services/settings.py`, `schemas/settings.py`, `openapi.committed.json`, `mcp-server/src/toolsets/settings.ts`, `mcp-server/tests/capture.test.ts`, `test_capture_service.py`, `CapturePage.tsx`, `CaptureViewport.tsx`, `CaptureScrubField.tsx`, `capture-help-content.ts`, `capture-toolbar.ts`, `useCaptureSettings.ts`, `settings-schemas.ts`, `test-ids.ts`, `capture-action-row.test.ts`, `capture-help-content.test.ts`, `capture-page.behavior.test.ts`, `capture-toolbar.test.ts`, 09, `gui-actions-index.md`, the matrix, the grouping file and `current-focus.md`.
- **LF.** `ui/tests/e2e/capture-inbox.test.ts`, `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md`.
- **New files** are LF.

```diff
 # services/settings.py, _encode (abridged)
+        if spec.integer:
+            if isinstance(value, bool) or not isinstance(value, int):
+                raise ValidationError(f"{key} must be a whole number")
+            # compared as int before any float(): a huge integer is out of range, not an OverflowError
 # capture-toolbar.ts, optionGroups (abridged)
+  // SELECT_NO_STYLE (MEU-105, D-721): with Select and nothing selected no tool's style could be set.
 # CapturePage.tsx, commitColor (abridged)
+    saveToolStyle(styleTool, field === 'color' ? { color: hex } : { textBg: hex })
```

The excerpt is abridged and paraphrased. The sources are `services/settings.py:148-185`, `capture-toolbar.ts:148` and `CapturePage.tsx:1563-1597`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-13-capture-style-tool-flow-implementation-critical-review.md`, on the ledger loop `s71-execution-2026-11-13-capture-style-tool-flow` (budget 33,000,000 tokens, cap 6 rounds, D-727; 53,000,000 after D-729). The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | changes_required | F1 (High, blocking, AC-105.32): a commit made while the first settings GET was pending, or after it failed, did not reach the next drawn mark. F2 (Medium, non-blocking, AC-105.17): an open text draft did not show the Bg colour. Both fixed (§Departures 7) | `5e9ea7c520e02e856babe21d5116677a53bd108e+00d1e9c8c9d98494d81511972f28e4acf9c0c23abee55be4a7a209aff85da0f3` |
| 2 | approved | F1 and F2 rechecked `fixed`; no new findings; intent achieved (ledger usage 5,837,998 tokens, 25,055,302 of 53,000,000 in all) | `5e9ea7c520e02e856babe21d5116677a53bd108e+dabfe448a5cd0746c0f3e02b7c52214ac88f296fdf836e70f166be3d55597adc` |

### Verdict

Round 1 returned changes_required. Round 2 returned approved, with 0 open findings, at the tested_state above. H1-7a (`C:/Temp/av-kit/review-state-check.txt`) reads `OK: review_mode=execution; round 2 of 6; verdict=approved; open findings=0`, and H1-7b (`C:/Temp/av-kit/exec-review.txt`) reads `OK: approved at round 2 of 6, 0 open blocking findings`.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| MEU-143 `gui-capture-tool-flow`: Lock, Letters and the rest of Modifiers | split | Session 71b | D-713 (`USER_EXPLICIT` 2026-11-13 "A"); grouping row 47b |
| `_reject_cookie_shaped` calls `str(value)` before the range check, so an `int` of more than 4300 digits handed straight to `_encode` raises `ValueError: Exceeds the limit (4300 digits)` | observation | None | Probed after the gate (`s71-bigint-probe.txt`). At the API, 401 digits gives 422 `arrow_stroke is out of range`, 4300 digits gives 422 for the cookie-byte limit, and 4301 or more gives 400 `There was an error parsing the body` from the body parser before any app code, the same as `tts` `speed`. No path gives a 500, and AC-105.3 and AC-105.4's `10**400` cases hold. The path was there before this session, and no code changed after the gate |
| AC-60.12's title still reads `typed hex, Apply`, while its body now presses Enter | observation | Session 71b | Row 3 moved the body as the plan says (`capture-inbox.test.ts:602`); a title edit now would change a gated input after H1-2 |
| `ruff check tools/` fails on errors in `tools/issue_triage*` and `tools/meu_status*` that were there before this session | observation | None | Session 68 DEP-1; this plan lints only the files it edits |
| The band mismatch: grouping P3, `meu-status.yaml` P2 (MEU-105 and MEU-143) | observation | Mat | Named, not changed (D-725) |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2) |

### Departures and their basis

1. **A pin the plan didn't name (row 3).** `capture-page.behavior.test.ts:1566`, in the AC-65.3 test at `:1563`, expected `['capture-tool-select', ['color', 'stroke']]`. Row 1's name sweep did not list it, because the line names the tool button's test id, not `optionGroups`. Row 3 moved it to `['capture-tool-select', []]` for SELECT_NO_STYLE, before Green. No AC text changed.
2. **AC-81.4's title (row 3).** After the Red run, the title "and the Color options are well, hex, Apply, Cancel, Named" became "and the Color options are well, hex, Named" (`capture-action-row.test.ts:470`). Only the title changed; the ids line at `:490` moved as the plan says. This came before Green.
3. **AC-60.8's load check moved during Green (row 4, S2).** Row 4 says no test file changes (S2), and S2 says to stop. The coordinator edited the test and did not stop.
   - **The failure.** The first broad run failed `TestingLibraryElementError: Unable to find an element by: [data-testid="capture-color"]` at `capture-page.behavior.test.ts:723`. A shot that loads with marks arms Select, and SELECT_NO_STYLE (D-721) hides the fields until a mark is picked. The test read the hex field before the pick.
   - **The change.** The `hexBefore` read and its `not.toBe(NAMED_COLOR_HEX.green)` were removed. `expect(screen.queryByTestId('capture-color')).toBeNull()` was added, with the comment "SELECT_NO_STYLE (MEU-105, D-721): the load arms Select, so no colour field shows before the pick."
   - **Unchanged.** The rest of the test (the pick loads the well, and the DTO and Save stay as they were) is the same. No AC text and no source changed for it.
4. **AC-105.28's mid-drag read (row 3).** The guard first failed at the mid-drag field read. The test now reads the scrub preview the way `capture-page.behavior.test.ts` reads it, and the retry and the row's guard run passed: `Tests  2 passed | 24 skipped (26)` (`s71-r3-g28-try.txt`, `s71-r3-guard-27-28.txt`). The first failing run's output was not kept. This was before Green, and the AC text did not change.
5. **The big-integer path.** See §Deferred Items. This is an observation; no code changed.
6. **`matrix_item` quoting (row 6).** SPLIT_STATUS writes `matrix_item: '9.31a'`. The YAML writer stored it unquoted (`meu-status.yaml:3754`, `matrix_item: 9.31a`). That still loads as the string `9.31a`, which `meu_status.py get` prints as `"matrix_item": "9.31a"` (`s71-h13-status-143.txt`), and the render check passed.

7. **Post-review corrections (execution round 1).** Codex's round 1 report (`2026-11-13-capture-style-tool-flow-implementation-critical-review.md`) found two defects; both were fixed Red first, after the gate, and the gate was run again.
   - **F1.** `saveCaptureToolStyle` wrote its commit into the query cache only when the cache held data, so a commit made while the first `GET /settings/capture` was pending, or after it failed, was sent but the next mark drew with the default. The cache is still left empty, because a partial object there would make the Settings card show a loaded form. Instead, `capture-style-store.ts` keeps a snapshot of the committed leaves (`committedStyleLeaves`, `subscribeCommittedStyleLeaves`), changed on each commit, on each leaf a failed PUT drops and on reset, and `useCaptureToolStyles` reads the styles from it while the query has no data. Tests: `capture-style-flow.behavior.test.ts:1053`, `:1074` (AC-105.32).
   - **F2.** TEXT_DRAFT_STYLE said the draft shows the background, but the draft's style carried only the colour and size. `CaptureViewport.tsx` now adds the valid `textBg` as the draft's `backgroundColor`; with none, the textarea keeps its `bg-bg` class. Test: `capture-style-flow.behavior.test.ts:776` (AC-105.17).
   - **A test edit after Red.** In the held-GET test, `await chooseTool('arrow')` was added before the second draw, because the page leaves Arrow after a draw. The Red failure was at the first draw's assertion, which comes before the added line. No AC text changed.

Departure 3 changed a test file during Green (S2). No departure changed an AC's text. One execution-stage decision was made, D-729 (§Decision Log): Mat chose "Add 20M" over the recommended 7M, so the execution review budget is 53M (`C:/Temp/av-kit/s71-exec-ledger-continue.txt`: `rounds 1/6  tokens 19,217,304/53,000,000`).

---

## Decision Log

```yaml
decision_log:
  - id: D-729
    stage: execution
    question: "Execution round 1 returned changes_required, and round 2 needs more review budget than D-727 set. How much is added?"
    resolution: human
    class: two-way
    chosen: "Add 20M, so the execution review budget is 53M and covers round 2 and most likely a round 3"
    recommendation: "Add 7M: the budget becomes 40M, which covers round 2 even at round 1's full cost"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s71-exec-review-round-1.md - round 1, changes_required, F1 blocking and F2 non-blocking"
      - "tools/review_ledger.py:494 - after a refusal, a human may continue the loop with extra tokens"
      - "D-728 - the plan loop's continue by Mat"
    research:
      engine: none
      sources: []
    reasoning: "Round 1 used 19,217,304 tokens, and the ledger reserves the last round's cost before a round, so round 2 was refused until the budget grew by at least 5,434,608. Mat chose 20M over the recommended 7M, which leaves room for a round 3 without asking again. The do-nothing option was to stop with MEU-105 unapproved and the F1 and F2 fixes unchecked."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'Add 20M'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-14 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, row 1's sweep, the moved pins, the Red and Green receipts, the H1-2 gate and the evidence records (H1-6) |
| Round 1 corrections | 2026-11-14 | claude-code-local (Claude Opus 5.5) | F1 and F2 fixed Red first; the gate rerun passed; the review copied to its canonical path; D-729 |
| Round 2 approved | 2026-11-14 | claude-code-local (Claude Opus 5.5) | Codex approved round 2; the report copied byte for byte to its canonical path; H1-7a and H1-7b pass |
