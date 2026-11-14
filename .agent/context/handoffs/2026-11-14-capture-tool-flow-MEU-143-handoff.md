---
date: "2026-11-14"
project: "capture-tool-flow"
meu: "MEU-143"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-14-capture-tool-flow/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-13-capture-style-tool-flow-MEU-105-handoff.md"
---

# Handoff: 2026-11-14-capture-tool-flow-MEU-143-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-143 `gui-capture-tool-flow`. Session 71b makes the capture editor fast to drive from the keyboard and from a held tool. It is the tool-flow half of MEU-105's slice after the split (D-713), grouping row 47b.

- **Lock is on by default and saved.** `capture.tool_lock` is a new boolean settings leaf, default `true` (LOCK_LEAF). The server reads it back as `True` only from the stored `"true"`, and the UI reads it as `false` only from the boolean `false` (LOCK_DECODE, D-747). Turning it off is the one-shot preference: each mark returns to Select (ONE_SHOT, D-745). The toolbar button is its only control; the Settings card doesn't show it.
- **The Lock leaf shares the style store's queue (LOCK_STORE, D-746).** Its PUT waits in the same chain as the style PUTs, a GET can't put back an older value, and a failed PUT shows `Couldn't save the tool lock` and refetches once the queue is empty.
- **Under Lock the just-drawn mark stays selected (LOCK_SELECTS, D-748).** While a tool is armed, a press on that selected mark moves or resizes it, and a press elsewhere draws (ARMED_EDIT). Choosing the armed tool again clears the selection, so a style change then sets the tool's own style (ARMED_RECHOOSE, D-749).
- **Tool letters (LETTERS, LETTER_HINTS, D-750).** V, A, R, H, T, X, E and C arm Select, Arrow, Box, Highlight, Text, Redact, Smart eraser and Crop, through eight page-scoped registry entries that click the tool buttons. Each hint names its letter, as in `Arrow (A)` and `Crop (C)`, and each button carries `aria-keyshortcuts`.
- **Letters never fire in a field (FIELD_GUARD, D-751).** A one-character chord with no Ctrl and no Alt is skipped when the target is editable or a `<select>`. Ctrl chords and F-keys still fire. `isEditableTarget` moved to `lib/editable-target.ts`, and `capture-import.ts` re-exports it.
- **One handling per key (CHORD_BUBBLE_ONCE, D-752).** `handleEditorKey` records the events it has handled, so X with the crop open swaps the aspect once.
- **Draw modifiers (MODIFIERS, SHIFT_NUDGE, ALT_NO_MENU, D-753, D-754).** Shift draws a square, keeps a box's shape from a corner handle and snaps an arrow to 45 degrees. Alt draws a bounded mark from its centre. Shift with an arrow key nudges 10 px (`FIELD_STEP_SHIFT`). Alt during and right after a bounded draw doesn't open the window menu.
- **Help and docs.** The Annotation tools help carries LOCK_HELP and `(Shift+arrow by 10 px)`. `gui-actions-index.md` carries FLOW_ACTIONS_INDEX, and 09 has the Delivered (Session 71b) note and the Entry note's `Crop (C)` (FLOW_SPEC).

The OpenAPI snapshot changes only by `tool_lock` in `SettingsPutIn` (D-744, H1-4). No mark type, mark field, sidecar, bake, annotate body or capture action changes, so the MCP audit baseline doesn't change.

**Build Plan Section**: bp09, `docs/build-plan/09-screenshot-capture.md` §Style and tool flow: the Lock row, the Letters row and the Modifiers row apart from the Pixelate scrub.

**Predecessor**: [MEU-105 handoff](2026-11-13-capture-style-tool-flow-MEU-105-handoff.md), Session 71. The grouping is `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md` (row 47b). These decisions carry: D-158 (human, `USER_EXPLICIT` 2026-10-29 "all recommendations are accepted"), D-159, D-160, D-674, D-675, D-678 and D-713 (human, `USER_EXPLICIT` 2026-11-13 "A").

**Execution authorization:** `USER_EXPLICIT`, 2026-11-14.
- **The plan review.** Codex approved the plan at round 2 of 3 (`.agent/context/handoffs/2026-11-14-capture-tool-flow-plan-critical-review.md`). Round 1 spent 10,176,921 tokens and found F1; round 2 spent 7,637,302 and rechecked it `fixed`. The loop spent 17,814,223 tokens. The review loops have no token budget (`.agent/review-limits.json` `token_budgets: "off"`), so they stop on rounds only.
- **The gate.** Mat ruled the band, D-756 (`USER_EXPLICIT` 2026-11-14 "P2 in both (Recommended)"), and said to execute, D-757 (`USER_EXPLICIT` 2026-11-14 "Execute now (Recommended)").
- **During execution** Mat chose to quit ShareX, which held F2 during the baseline Electron run (`USER_EXPLICIT` 2026-11-14 "I'll quit ShareX (Recommended)"). No other ruling was needed. The execution decisions D-758 to D-766 are autonomous and are in the plan's `decision_log`.

**The AC-87 supersession (D-755).** MEU-87's lock tests pinned Lock off at load and nothing selected after a locked draw. The 09 Lock row changes both, so row 3 rewrote AC-87.2 to AC-87.7 as the plan's §Pins that move says (the table below). AC-87.1, the toolbar spec, holds.

**The band (D-756).** Mat chose "P2 in both". Row 6 set grouping row 47b to P2; `meu-status.yaml` already gave MEU-143 `band: P2`. `s71b-r6-status.txt` reads `band from D-756: P2`, with every key `True`.

**The OpenAPI and MCP change (D-744).** `SettingsPutIn` forbids extra keys, so it gained `tool_lock: StrictBool | None = None` (`schemas/settings.py:70`). The committed snapshot was regenerated with `tools/export_openapi.py`, not edited by hand. `s71b-r2-openapi-delta.txt` reads `SettingsPutIn added: ['tool_lock'] rest of the document unchanged: True`. The strict MCP set schema gained `tool_lock: z.boolean().optional()` (`mcp-server/src/toolsets/settings.ts:160`), and `SETTINGS_SCHEMA` gained `tool_lock: { type: "boolean", default: true }` (`:86`). No action was added.

**Receipts.** A receipt named by its file name alone (`s71b-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s71b/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The Lock preference.**
  - **Writers.** The toolbar Lock button; an agent's `avkit_settings` set; the Settings API.
  - **The page.** `useCaptureToolLock()` (`CapturePage.tsx:415`) feeds the button. Its `onToggleToolLock` (`:2657`) calls `setLocked(!locked)`.
  - **The client store.** `saveCaptureToolLock` (`capture-style-store.ts:218`) parses `{ tool_lock }` with `captureLockPutSchema` (`settings-schemas.ts:115`, strict) and hands the leaf to `commitLeaves` (`capture-style-store.ts:150`), the core it shares with `saveCaptureToolStyle`. That records the leaf in `latest` (`:18`), merges it into the cache at once and chains one `PUT /settings/capture` on the shared queue. A failure raises the lock counter, read through `lockSaveFailures` (`:229`) and `subscribeLockSaveFailures` (`:234`). The page shows `LOCK_SAVE_FAILED` (`CapturePage.tsx:110`, `Couldn't save the tool lock`), which names no value.
  - **The API and the service.** `SettingsPutIn.tool_lock` (`schemas/settings.py:70`) refuses `"false"`, `0` and `1` with a 422. `SETTINGS_KEY_TABLE` holds `("capture", "tool_lock"): SettingSpec("boolean", True)` (`services/settings.py:127`). `_encode` (`:150`) refuses every non-`bool`, `null` included, with a `ValidationError` that names the key only. `_decode` (`:189`) is unchanged and reads `True` only from `"true"`.
  - **Readers.** `fetchCaptureSettings` (`capture-style-store.ts:47`) keeps the committed `tool_lock` over a GET that didn't see it. `readToolLock` (`capture-tool-lock.ts:6`) returns `false` only for `{ tool_lock: false }`. `useCaptureToolLock` (`useCaptureToolLock.ts:20`) reads `readToolLock(query.data ?? committed)` (`:24`), so a failed or held GET shows the last committed value, or `true`.
- **The armed tool.** The tool buttons, the letters (through the buttons), LOCK_SELECTS and one-shot write it. It is never saved. Under Lock a draw calls `commitSelection(list.length - 1, list, toolLocked ? tool : 'select')` (`CapturePage.tsx:1382`), and a text commit does the same with `'text'` (`:2741`). ARMED_EDIT's gesture start is shared with the Select branch through `startEditGesture` (`:1195`).
- **The letters.** `TOOL_LETTERS` (`capture-toolbar.ts:108`) holds the eight letters. The registry entries (`CAPTURE_TOOL_IDS`, `commandRegistry.ts:62`) and the buttons' `shortcut` props (`CaptureViewport.tsx:995` onward) read it. The page publishes each entry's state through `usePublishCommandState('/capture', …)` (`CapturePage.tsx:581`). FIELD_GUARD is the check at `shortcuts.ts:235`, and `BOUND_CONTROLS` gains the eight pairs (`:41` onward).
- **The modifier keys.** The pointer's `shiftKey` and `altKey` (`SurfacePointer.altKey`, `CaptureViewport.tsx:109`, filled at `:480`) and the key event's `shiftKey`. `drawBounds` (`CapturePage.tsx:1229`), `snapArrowEnd` (`:1232`, `:1250`) and `keepRatioResize` (`:301`) apply them. The nudge step is `event.shiftKey ? FIELD_STEP_SHIFT : KEYBOARD_NUDGE_PX` (`:1976`). They are never stored, and no letter, modifier or Lock value enters mark JSON (AC-143.34).

Two traces use recording fakes (Session 55 RULE-3):
- AC-143.21 follows one `A` keydown through `createShortcutHandler` with a recording `getState`, the `capture:tool_arrow` action and the button click, to `aria-pressed="true"` and the hex field showing `#123456`;
- AC-143.22 follows one Lock click to the recorded PUT body `{ "tool_lock": false }`. Its Python half follows the API body through `SettingsPutIn` and a recording `set_namespace` wrapper to the stored `"false"` and the next GET's `false`.

### Row 1's sweep (S55 RULE-1, S59 RULE-1, S62 RULE-4, S63 RULE-1, S66 RULE-1, S68 RULE-2)

**What the sweep covered.**
- Before its edits, row 1 swept `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` at `42f02bc` (`s71b/row1-sweep.txt`, 455 lines). It appended the hits to `s71b-anchors.txt` (515 lines), whose row 0 part holds each target's SHA-256 and line endings.
- The sweep has one section per name row 1 lists, each hit with its file's ending: every caller and exact-signature pin of `SurfacePointer`, `createShortcutHandler`, `BOUND_CONTROLS`, `isEditableTarget`, `CAPTURE_PALETTE_IDS`, `toolLocked` and `KEYBOARD_NUDGE_PX`; the literal text the plan rewrites (`The lock button keeps`, `Arrow keys nudge the selected mark`, `typed hex, Apply`, `'Crop'` and the bare tool hints); and every fake that answers `/settings/capture`.

**The pins the plan named** moved as the plan says (the table below). These hold as the plan says: AC-87.1 (`capture-toolbar.test.ts:168-175`), the accessible-name lookups, AC-97.4, AC-19.17, AC-23.18, AC-95.5, AC-39.14 and the crop X tests (`capture-crop-tool.behavior.test.ts:598-600`, `:620-622`).

**A pin the plan didn't name.** AC-65.2's negative test (`capture-page.behavior.test.ts:1554`) read each no-shot hint as `Name — Select a shot first`. LETTER_HINTS puts the letter before the reason, so the test now expects `Select (V) — Select a shot first` (D-764, §Departures 1). It failed at Red with `expected 'Select — Select a shot first' to be 'Select (V) — Select a shot first'` (`s71b-ui-red.txt`).

**The test fakes.** `tool_lock: false` was added to the `GET /settings/capture` fake of each harness whose tests draw and are about something else, so their draws still return to Select. Counted from the added lines against `42f02bc`:
- unit: `capture-page.behavior` 5, `capture-filmstrip-actions.behavior` 2, and 1 each in `capture-action-row`, `capture-copy-image.behavior`, `capture-crop-tool.behavior`, `capture-import.behavior`, `capture-redact.behavior`, `capture-style-flow.behavior`, `capture-text-lines.behavior` and `icon-hints`;
- Electron: `capture-inbox` 7, and 1 each in `capture-picker`, `capture-filmstrip-actions` and `capture-import`.

The new MEU-143 tests and the rewritten AC-87 tests set the leaf themselves.

**The two clipboard specs were not run.** `ui/tests/e2e/capture-filmstrip-actions.test.ts` and `ui/tests/e2e/capture-import.test.ts` write the real clipboard (Session 57 RULE-4). Row 3 added the `tool_lock: false` line to each one's settings fake, and no row or gate step ran them. The UI typecheck and lint cover both files; their behaviour under the new default is unproven by a run. `capture-picker.test.ts` was run in row 4 (`s71b-e2e-picker.txt`: `4 passed (10.8s)`).

**The byte-hash guard.** No `test-ids.ts` line was added. AC-51.6 reads `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` (`capture-action-row.test.ts:757`), unchanged. Row 1's run passed (`s71b-types-action-row.txt`: `Tests  13 passed (13)`), and so did row 3's hash run (`s71b-r3-hash.txt`: `Tests  1 passed | 12 skipped (13)`) and the gate's `action-row` step (GATE_ACTION_ROW).

### The moved pins, before and after

| Pin | File and line now | Ending | Before | After | Row |
|---|---|---|---|---|---|
| AC-36.12 (the capture key set) | `tests/unit/test_capture_service.py:39`, `:58`, `:446`; test at `:422` | CRLF | `CAPTURE_KEYS` and `CAPTURE_DEFAULTS` ended at `pixelate_block_size` | they gain `tool_lock`, default `True` | 2 |
| AC-38.6 (the MCP capture keys) | `mcp-server/tests/capture.test.ts:65`, `:84`; test at `:216` | CRLF | the same sixteen keys | the same leaf and default | 2 |
| AC-105.2 (the style rows' order) | `tests/unit/test_capture_style_settings.py:52-53`; test at `:46` | LF | the nine style leaves were the last keys | they stay exact and contiguous after `annotated_format`, and `tool_lock` is the only key after them | 2 |
| AC-105.5 (the nine leaves' schema) | `capture.test.ts:1735`; test at `:1721` | CRLF | `CAPTURE_KEYS.slice(7)` | `CAPTURE_KEYS.slice(7, 16)` | 2 |
| AC-87.2 and its negative | `ui/tests/unit/capture-page.behavior.test.ts:3323`, `:3346` | CRLF | Lock off at load | `aria-pressed="true"` at load; a click sends one PUT `{ tool_lock: false }`; with no shot it stays enabled | 3 |
| AC-87.3 and its negative | `:3358`, `:3377` | CRLF | under Lock nothing selected after a draw | Box stays with each new box selected; two Undos remove them one at a time; one-shot returns to Select with the box selected | 3 |
| AC-87.4 and its negative | `:3389`, `:3406` | CRLF | under Lock nothing selected after a text commit | Text stays with the new text selected; a click away opens a new draft | 3 |
| AC-87.5 and its negative | `:3417`, `:3438` | CRLF | the lock survived a tool change with nothing selected | the drawn arrow is selected; turning it off restores auto-Select | 3 |
| AC-87.6 (Electron) | `ui/tests/e2e/capture-inbox.test.ts:2570` | LF | clicked Lock on before two draws | asserts Lock pressed at load and doesn't click it; Box stays and the second box is selected | 3 |
| AC-87.7 (the lock help sentence) | `ui/tests/unit/capture-help-content.test.ts:93` | CRLF | `The lock button keeps the current tool after each mark.` | LOCK_HELP's first sentence; the old one is absent | 3 |
| The nudge help words | `capture-action-row.test.ts:68`, `capture-help-content.test.ts:9`, `:108` | CRLF | `Arrow keys nudge the selected mark, or the arrow end…` | `Arrow keys nudge the selected mark (Shift+arrow by 10 px), or the arrow end…` | 3 |
| AC-80.8 and AC-80.9 (icon hints) | `ui/tests/unit/icon-hints.test.ts:77-83`, `:350`; tests at `:338`, `:358` | CRLF | bare tool hints | `Name (L)`, the eraser's `Smart eraser (E): …`; no-shot `${spec.name} (L) — ${NO_SHOT_HINT}` | 3 |
| MEU-65 HINT_OVERRIDE | `capture-page.behavior.test.ts:1469` and the lines before it | CRLF | bare tool hints | the same lettered hints | 3 |
| AC-65.2's no-shot hints | `capture-page.behavior.test.ts:1554` | CRLF | `Select — Select a shot first` | `Select (V) — Select a shot first` | 3 (§Departures 1) |
| SMART_HINT | `ui/tests/unit/capture-redact.behavior.test.ts:43` | LF | `Smart eraser: Covers…` | `Smart eraser (E): Covers an area with the surrounding colour` | 3 |
| AC-131.11 and AC-131.12 (the Crop hint) | `ui/tests/unit/capture-crop-tool.behavior.test.ts:424`, `:448`, `:456`, `:473` | LF | `Crop`, `Crop — reason` | `Crop (C)` with `aria-keyshortcuts`; `Crop (C) — reason` | 3 |
| The Electron tool hints | `capture-inbox.test.ts:1686`, `:3355` | LF | `Arrow`; `Smart eraser: …` | `Arrow (A)`; `Smart eraser (E): …` | 3 |
| AC-60.12's title | `capture-inbox.test.ts:478` | LF | `typed hex, Apply` | `typed hex, Enter`; the body already pressed Enter | 3 |
| The `GET /settings/capture` fakes | the harnesses listed above | as each file | no `tool_lock` | `tool_lock: false` | 3 |

### Row 2's data (D-744)

- **What row 2 wrote.** LOCK_LEAF in the service, the API schema (with the regenerated snapshot) and the MCP settings toolset, and the four key-set pins above.
- **The new pytest files** are LF:
  - `tests/unit/test_capture_tool_lock.py` (105 lines) holds AC-143.1 (Python), .2 and .3;
  - `tests/e2e/test_api_capture_tool_lock.py` (123 lines) holds AC-143.4 and AC-143.22's Python half.
- **The MCP test.** AC-143.5 was appended to `mcp-server/tests/capture.test.ts:1750` (CRLF).
- **The runs.**
  - pytest `267 passed in 24.00s` (`s71b-r2-py.txt`);
  - MCP `Tests  302 passed (302)` over 20 files (`s71b-r2-mcp.txt`);
  - pyright `0 errors, 0 warnings, 0 informations` (`s71b-r2-pyright.txt`);
  - ruff `All checks passed!` (`s71b-r2-ruff.txt`);
  - `id-length: 22 test(s), 0 too long` (`s71b-r2-id-length.txt`).

### Row 3's Red tests (S50 RULE-2, S61 RULE-3, S66 RULE-2)

Row 3 wrote two new UI test files, both LF:
- `ui/tests/unit/capture-tool-lock.test.ts` (282 lines) holds AC-143.1 (TypeScript), .6, .15 and the unit halves of .23 to .26;
- `ui/tests/unit/capture-tool-flow.behavior.test.ts` (1392 lines) holds AC-143.7 to .14, .16 to .21, AC-143.22's UI half, the page halves of .23 to .28, and .30, .33 and .34. Its render harness has a recording fake server for `GET` and `PUT /settings/capture` and the save POST, and mounts the registry handler through `createShortcutHandler` with the real `listCommands()`.

It added AC-143.31 to `capture-help-content.test.ts:105` beside the moved AC-87.7, and appended AC-143.29 to `ui/tests/e2e/capture-inbox.test.ts:3500` (LF). It moved the pins in the table above.

### Row 4's Green changes (S55 RULE-1)

Row 4 changed these files, keeping each file's endings:
- **Model and store.** LOCK_DECODE (`capture-tool-lock.ts`), LOCK_STORE (`capture-style-store.ts`, `useCaptureToolLock.ts`).
- **Modifiers.** `capture-modifiers.ts` (122 lines): `drawBounds`, `snapArrowEnd` and `keepRatioResize`. `keepRatioResize` reuses the crop's ratio helpers, so `capture-crop.ts` now exports `largestDriving`, `drivingFromWidth` and `drivingFromHeight`, with no body changed (D-766, §Departures 3).
- **Registry and handler.** LETTERS' eight entries (`commandRegistry.ts`), BOUND_CONTROLS and FIELD_GUARD (`shortcuts.ts`).
- **Viewport.** LETTER_HINTS, `SurfacePointer.altKey`, ALT_NO_MENU and the Lock button's state (`CaptureViewport.tsx`).
- **Page.** ONE_SHOT, LOCK_SELECTS, ARMED_EDIT with `startEditGesture`, the published letter state, CHORD_BUBBLE_ONCE, MODIFIERS and SHIFT_NUDGE (`CapturePage.tsx`).
- **Help.** LOCK_HELP (`capture-help-content.ts`).
- **Unchanged.** `openapi.committed.json` did not change from row 2 (`s71b-r4-openapi.txt`, exit 0).

Row 4 also corrected two set-up defects in the Red flow tests, with no AC change (D-765, §Departures 2).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-143.1 | type | The exact signatures: `readToolLock`, `saveCaptureToolLock`, `lockSaveFailures`, `subscribeLockSaveFailures`, `useCaptureToolLock`, `captureLockPutSchema`, `TOOL_LETTERS`, `CAPTURE_TOOL_IDS`, `isEditableTarget` from `lib/editable-target.ts` and its re-export, `FIELD_STEP_SHIFT === 10`, `drawBounds`, `snapArrowEnd`, `keepRatioResize` and `SurfacePointer.altKey`. Row 1 added the names, so it passed where it was written | Local Canon: D-746, D-750, D-753 | `tests/unit/test_capture_tool_lock.py:46`; `ui/tests/unit/capture-tool-lock.test.ts:59` | ✅ |
| AC-143.2 | behaviour | LOCK_LEAF: `("capture", "tool_lock")` with the default `True` after `pixelate_block_size`; a fresh store returns the `bool` `True` | Spec: 09 Lock row; Local Canon: D-744 | `test_capture_tool_lock.py:58`, `:66` | ✅ |
| AC-143.3 | behaviour | LOCK_DECODE: `False` stores `"false"` and reads `False`; `""`, `"\x07"`, a lone surrogate, `"TRUE"` and `"1"` read `False`, `"true"` reads `True`; `_encode` refuses `"false"`, `0`, `1` and `None`, naming the key and not the value | Local Canon: D-747 | `test_capture_tool_lock.py:72`, `:81`, `:88`, `:95` | ✅ |
| AC-143.4 | behaviour | The API: `{ "tool_lock": false }` gives 200 and a GET returns `false`; `"false"`, `0`, `1` and `null` give 422; no body echoes a refused value; the OpenAPI document equals the committed snapshot | Local Canon: D-744 | `tests/e2e/test_api_capture_tool_lock.py:48`, `:59`, `:73`, `:80` | ✅ |
| AC-143.5 | behaviour | The MCP leaf: `tool_lock` with default `true` after `pixelate_block_size`; the set schema accepts `false` and refuses `"false"` and `0`; the actions are unchanged | Local Canon: D-744 | `mcp-server/tests/capture.test.ts:1750` | ✅ |
| AC-143.6 | behaviour | `readToolLock` returns `false` only for `{ tool_lock: false }`, and `true` for every other input listed | Local Canon: D-747 | `capture-tool-lock.test.ts:116` | ✅ |
| AC-143.7 | behaviour | LOCK_DEFAULT on the page: on without `tool_lock`, off on `false`, on on a lone surrogate; a locked Box drag keeps Box with the new box selected and its colour shown | Spec: 09 Lock row | `ui/tests/unit/capture-tool-flow.behavior.test.ts:692` | ✅ |
| AC-143.8 | behaviour | ONE_SHOT: a Lock click sends one PUT of exactly `{ tool_lock: false }` and shows off before it settles; a remount shows off; a one-shot Box drag returns to Select with the box selected; a second click sends `true` | Spec: 09 Lock row | `capture-tool-flow.behavior.test.ts:707` | ✅ |
| AC-143.9 | behaviour | LOCK_STORE: held GET, failed GET, the order of two clicks, and the queue shared with a style commit | Session 71 RULE-1; Local Canon: D-746 | `capture-tool-flow.behavior.test.ts:733`, `:748`, `:767`, `:787` | ✅ |
| AC-143.10 | behaviour | A failed Lock PUT shows `Couldn't save the tool lock`, names no value in the status or the Console, refetches once and shows the stored value; a failed style PUT still shows its own message alone | Session 50 RULE-1; Local Canon: D-746 | `capture-tool-flow.behavior.test.ts:805` | ✅ |
| AC-143.11 | behaviour | ARMED_EDIT: under Lock a drag on the just-drawn box moves or resizes it with Box still armed; an arrow end and a text mark move the same way | Spec: 09 Lock row | `capture-tool-flow.behavior.test.ts:838` | ✅ |
| AC-143.12 | behaviour | Under Lock a drag elsewhere draws and selects a new box; a drag on an unselected earlier mark draws over it and doesn't select it | Spec: 09 Lock row | `capture-tool-flow.behavior.test.ts:880` | ✅ |
| AC-143.13 | behaviour | STYLE_TARGET under Lock and ARMED_RECHOOSE: a hex commit restyles the just-drawn arrow with no PUT; re-choosing Arrow, by click or A, clears the selection; the next commit sends `{ arrow_color }`; Escape leaves the selection | Spec: 09 Lock and Tool style rows; Local Canon: D-719, D-749 | `capture-tool-flow.behavior.test.ts:896` | ✅ |
| AC-143.14 | behaviour | LOCK_SELECTS for text: under Lock a text commit keeps Text with the text selected and a click away opens a new draft; one-shot returns to Select with the text selected | Spec: 09 Lock row | `capture-tool-flow.behavior.test.ts:927` | ✅ |
| AC-143.15 | behaviour | The orders: the eight registry entries after `capture:open_folder`, `TOOL_LETTERS`, none in the palette, the eight BOUND_CONTROLS pairs after `capture-save`, and the toolbar order unchanged | Local Canon: D-750 | `capture-tool-lock.test.ts:134` | ✅ |
| AC-143.16 | behaviour | LETTERS: each of V, A, R, H, T, X, E and C arms its tool as its button does, shows the tool's own style, draws with it, and is `defaultPrevented`; after V there is no `capture-color` | Spec: 09 Letters row; Local Canon: D-719, D-721 | `capture-tool-flow.behavior.test.ts:954` (eight ids) | ✅ |
| AC-143.17 | behaviour | LETTER_HINTS: `Name (L)`, the eraser's and the crop's hints, `aria-keyshortcuts`, the bare accessible name; with no shot `Name (L) — Select a shot first`, and a letter does nothing and isn't prevented | Spec: 09 Letters and Entry rows | `capture-tool-flow.behavior.test.ts:990` (§Departures 2) | ✅ |
| AC-143.18 | behaviour | FIELD_GUARD: `varhtxecVARHTXEC` types into the draft, the hex, the number fields, the named menu and the palette search, with no tool change; Ctrl+S and F1 still work from the hex field | Spec: 09 Letters row | `capture-tool-flow.behavior.test.ts:1015` | ✅ |
| AC-143.19 | behaviour | With the crop open on 16:9 one `x` swaps the aspect once and leaves Redact unarmed; with the crop closed X arms Redact | Spec: 09 Letters row; Local Canon: D-752 | `capture-tool-flow.behavior.test.ts:1052` | ✅ |
| AC-143.20 | behaviour | Letters do nothing with the crop open, an `aria-modal` dialog open, or on a held key | Local Canon: D-750, D-760; CROP_MODAL | `capture-tool-flow.behavior.test.ts:1070` | ✅ |
| AC-143.21 | behaviour | Trace: one `A` keydown through `createShortcutHandler`, the `capture:tool_arrow` action and one button click, to `aria-pressed="true"` and `#123456` | Session 55 RULE-3 | `capture-tool-flow.behavior.test.ts:1113` | ✅ |
| AC-143.22 | behaviour | Trace: one Lock click to the PUT body `{ "tool_lock": false }`; the Python half through `SettingsPutIn` and a recording `set_namespace` (one call) to the stored `"false"` and the next GET | Session 55 RULE-3 | `capture-tool-flow.behavior.test.ts:1133`; `test_api_capture_tool_lock.py:97` | ✅ |
| AC-143.23 | behaviour | Shift draw, one id per bounded tool: a 40×40 square and a square cut to the image; `drawBounds` unit cases; without Shift the plain box | Spec: 09 Modifiers row; Local Canon: D-753, D-758 | `capture-tool-lock.test.ts:208`; `capture-tool-flow.behavior.test.ts:1155` (five ids) | ✅ |
| AC-143.24 | behaviour | Shift resize: a corner keeps 2:1 (60×30), without Shift 60×24, an edge handle ignores Shift; `keepRatioResize` unit cases | Spec: 09 Modifiers row; Local Canon: D-753, D-759 | `capture-tool-lock.test.ts:226`; `capture-tool-flow.behavior.test.ts:1171` | ✅ |
| AC-143.25 | behaviour | Shift arrow: the end snaps to the horizontal and to 45°, an endpoint drag snaps about the fixed end; `snapArrowEnd` unit cases, the end kept inside the image | Spec: 09 Modifiers row; Local Canon: D-753, D-758 | `capture-tool-lock.test.ts:247`; `capture-tool-flow.behavior.test.ts:1191` | ✅ |
| AC-143.26 | behaviour | Alt draw, one id per bounded tool: from the centre, Shift+Alt a square from the centre, the half-extents cut at the edge; the arrow, text and a move ignore Alt | Spec: 09 Modifiers row; Local Canon: D-753 | `capture-tool-lock.test.ts:270`; `capture-tool-flow.behavior.test.ts:1206` (five ids), `:1219` | ✅ |
| AC-143.27 | behaviour | SHIFT_NUDGE: Shift+arrow 10 px, plain 1 px, a burst is one step, the edge clamps, the crop's Shift nudge unchanged, the 10 is `FIELD_STEP_SHIFT` | Spec: 09 Modifiers row; Local Canon: D-675 | `capture-tool-flow.behavior.test.ts:1236`, `:1273` (§Departures 2) | ✅ |
| AC-143.28 | behaviour | ALT_NO_MENU: Alt during a bounded drag and the first Alt `keyup` after it are prevented; a plain Alt isn't | Local Canon: D-754 | `capture-tool-flow.behavior.test.ts:1285` | ✅ |
| AC-143.29 | behaviour | Electron: Lock on at load, R arms Box, a box drag keeps Box with the box selected, an Alt drag then V arms Select, `a` in the hex changes no tool, a Lock click sends one PUT with `tool_lock: false` | Spec: 09 Lock, Letters and Modifiers rows | `ui/tests/e2e/capture-inbox.test.ts:3500`; gate `ui-electron` | ✅ |
| AC-143.30 | behaviour | The Settings card: after a Lock PUT its unsaved edit stays, its Save sends exactly the seven keys, and a later GET still returns `tool_lock` | Session 55 RULE-1; Local Canon: D-745 | `capture-tool-flow.behavior.test.ts:1310` | ✅ |
| AC-143.31 | behaviour | LOCK_HELP: the new sentences and `(Shift+arrow by 10 px)` exactly, and not the old lock sentence | Spec: 09 Lock, Letters and Modifiers rows | `ui/tests/unit/capture-help-content.test.ts:105` | ✅ |
| AC-143.32 | check | FLOW_ACTIONS_INDEX: `capture:tool_select` and `capture:tool_crop` placed, each Trigger names its letter, `capture:tool_lock` names its route, `capture:draw_modifiers` follows `capture:style_tool`; `gui-actions-audit.test.ts` passes | Local Canon: GUI actions index | row 5's check (`s71b-r5-spec.txt`, `s71b-r5-actions.txt`) | ✅ |
| AC-143.33 | guard | Unchanged: Ctrl+C, Ctrl+V, Ctrl+Z, Ctrl+Y, Ctrl+S, F1, Delete, Enter re-edit and Escape; the crop's keys; MEU-85, MEU-99 and MEU-105's tests; no mark type or field change | Local Canon: D-675, D-678 | `capture-tool-flow.behavior.test.ts:1334`, `:1366` | ✅ |
| AC-143.34 | guard | No letter, modifier or Lock value enters mark JSON: after a locked draw and a Shift draw the save body's marks hold today's keys | Spec: 09 Tool style row | `capture-tool-flow.behavior.test.ts:1380` | ✅ |
| AC-143.35 | check | AC-60.12's title reads `typed hex, Enter`, and no title in `capture-inbox.test.ts` holds `Apply,` | Session 71b prompt | row 3's check (`s71b-r3-ac35.txt`) | ✅ |
| AC-143.36 | check | FLOW_SPEC: 09's Delivered (Session 71b) note follows the Session 71 note and names AC-143.1 to AC-143.36; the Entry note names `Crop (C)`; 09 keeps CRLF | Local Canon: 09 Delivered notes | row 5's check (`s71b-r5-spec.txt`) | ✅ |
| AC-19 (cross-ref) | regression | Held, not moved: AC-19.17 uses `arrayContaining`, and the letter entries are `palette: false` | plan §Pins that move ("These were read and hold") | `ui/tests/unit/command-palette.test.ts`; gate `ui-tests` | ✅ |
| AC-23 (cross-ref) | regression | Held, not moved: AC-23.18's palette audit uses `toContain`, and no letter entry is in the palette | plan §Pins that move | `ui/tests/unit/gui-actions-audit.test.ts:157`; gate `ui-tests` | ✅ |
| AC-36 (cross-ref) | regression | AC-36.12's capture key set gains `tool_lock` with the default `True` | plan §Pins that move; LOCK_LEAF | `tests/unit/test_capture_service.py:422`; `s71b-r2-py.txt`; gate `py-tests` | ✅ |
| AC-38 (cross-ref) | regression | AC-38.6's MCP capture keys gain the same leaf and default | plan §Pins that move; LOCK_LEAF | `mcp-server/tests/capture.test.ts:216`; `s71b-r2-mcp.txt`; gate `mcp-tests` | ✅ |
| AC-39 (cross-ref) | regression | Held, not moved: AC-39.14's `CAPTURE_PALETTE_IDS` is unchanged | plan §Pins that move | `ui/tests/unit/capture-page.test.ts:342`; gate `ui-tests` | ✅ |
| AC-51.6 (cross-ref) | regression | The test-ids prefix hash is unchanged: `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` | plan §Files Modified (byte-hash guard) | `capture-action-row.test.ts:757`; `s71b-r3-hash.txt`; gate `action-row` | ✅ |
| AC-60 (cross-ref) | regression | One-shot keeps AC-60.4's return to Select with the new mark selected (AC-143.8, AC-143.14). AC-60.12's title is `typed hex, Enter` (AC-143.35). AC-60.15's help test failed at Red on the moved nudge words and passed at Green | plan §Pins that move; ONE_SHOT | `capture-inbox.test.ts:478`; `capture-help-content.test.ts:25`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-65 (cross-ref) | regression | AC-65.2's hint and no-shot hint carry the letter; the accessible name stays bare | plan LETTER_HINTS; D-764; §Departures 1 | `capture-page.behavior.test.ts:1516`, `:1554`; gate `ui-tests` | ✅ |
| AC-66 (cross-ref) | regression | AC-66.16's help test reads the moved nudge words; it failed at Red and passed at Green | plan §Pins that move (the nudge help words) | `capture-help-content.test.ts:35`; gate `ui-tests` | ✅ |
| AC-67 (cross-ref) | regression | AC-67.20's hover hint failed once in the baseline rerun at `42f02bc`, before any change, and passed in the next baseline run, in row 4 and in the gate (§Departures 4) | Session 71b baseline | `capture-inbox.test.ts:1605`; `s71b-base-e2e-rerun.txt`, `s71b-base-e2e-rerun2.txt`; gate `ui-electron` | ✅ |
| AC-80 (cross-ref) | regression | AC-80.8 and AC-80.9's HINT_OVERRIDE carries the eight lettered hints and the lettered no-shot line | plan §Pins that move | `ui/tests/unit/icon-hints.test.ts:338`, `:358`; gate `ui-tests` | ✅ |
| AC-81 (cross-ref) | regression | AC-81.12's help test reads the moved nudge words. AC-81.13 still re-pins AC-51.6's hash. AC-81.11 failed in the first baseline run because ShareX held F2 (§Departures 4) | plan §Pins that move | `capture-action-row.test.ts:713`, `:721`; `capture-inbox.test.ts:1952`; gate `action-row`, `ui-electron` | ✅ |
| AC-87 (cross-ref) | superseded | AC-87.2 to AC-87.7 rewritten for Lock on by default with the just-drawn mark selected (D-755); AC-87.1 holds | Human-approved: D-755 at the plan gate; plan §Pins that move | `capture-page.behavior.test.ts:3323` to `:3438`; `capture-inbox.test.ts:2570`; `capture-help-content.test.ts:93`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-89 (cross-ref) | regression | AC-89.8's help test reads the moved nudge words; it failed at Red and passed at Green | plan §Pins that move (the nudge help words) | `capture-help-content.test.ts:61`; gate `ui-tests` | ✅ |
| AC-95 (cross-ref) | regression | AC-95.5 holds: Ctrl chords and F1 fire from fields, which FIELD_GUARD keeps; AC-143.18 checks Ctrl+S and F1 from the hex field | plan FIELD_GUARD | `ui/tests/unit/shortcuts.test.ts:229`; gate `ui-tests` | ✅ |
| AC-97 (cross-ref) | regression | Held, not moved: AC-97.4 uses `toContainEqual`, so the eight new BOUND_CONTROLS pairs don't break it | plan §Pins that move | `ui/tests/unit/common-shortcuts.test.tsx:49`; `capture-page.test.ts:628`; gate `ui-tests` | ✅ |
| AC-99 (cross-ref) | regression | MEU-99's history steps each locked draw, ARMED_EDIT gesture and Shift nudge burst as one entry; AC-99.6's help test failed at Red on the moved nudge words and passed at Green; AC-99.7 passes in Electron | AC-143.11, AC-143.27, AC-143.33 | `capture-help-content.test.ts:128`; `capture-inbox.test.ts:2979`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-100 (cross-ref) | regression | AC-100.11 passed in row 4's Electron run and in the gate; it did not fail this session, so S15 did not apply | Session 71b prompt | `capture-inbox.test.ts:3058`; `s71b-e2e-green.txt`; gate `ui-electron` | ✅ |
| AC-103 (cross-ref) | regression | AC-103.15's SMART_HINT reads `Smart eraser (E): …` | plan §Pins that move | `ui/tests/unit/capture-redact.behavior.test.ts:43`, `:269`; gate `ui-tests` | ✅ |
| AC-105 (cross-ref) | regression | MEU-105's style contracts hold: STYLE_STORE's queue now also carries `tool_lock`; STYLE_DISPLAY and STYLE_DRAW follow a letter as a click; SELECT_NO_STYLE after V; STYLE_TARGET restyles the just-drawn mark. AC-105.2's order pin and AC-105.5's loop moved in row 2 | plan §User Review Required (MEU-105 contracts); §Pins that move | `test_capture_style_settings.py:46`; `capture.test.ts:1721`; `capture-style-flow.behavior.test.ts`; gate `py-tests`, `mcp-tests`, `ui-tests` | ✅ |
| AC-131 (cross-ref) | regression | AC-131.11 and AC-131.12's Crop hint reads `Crop (C)` with `aria-keyshortcuts`; this closes 09's Entry rule | plan LETTER_HINTS; §Pins that move | `capture-crop-tool.behavior.test.ts:415`, `:440`, `:451`; gate `ui-tests` | ✅ |
| AC-81.13 (cross-ref) | regression | Re-pins AC-51.6's hash, unchanged | plan §Files Modified (byte-hash guard) | `capture-action-row.test.ts:721`; gate `action-row` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-143.6 to .28 (Vitest) and AC-143.31, with the rewritten AC-87.2 to .5 and AC-87.7 | Row 3: `Test Files  4 failed (4)`, `Tests  59 failed \| 141 passed (200)`, exit 1 (`s71b-ui-red.txt`, `.exit` holds `1`). Decisive lines: `expected 'false' to be 'true'` (AC-87.2 to .5, AC-143.9); `no tool_lock: on: expected 'false' to be 'true'` (AC-143.7); `expected [] to have a length of 1 but got +0` (AC-143.8, .9, .22); `expected '' to contain 'Couldn\'t save the tool lock'` (AC-143.10); `Box stays armed: expected false to be true` (AC-143.11); `v is prevented: expected false to be true` (AC-143.16); `capture-tool-select: expected 'Select' to be 'Select (V)'` (AC-143.17); `the registry ran the letter: expected undefined to be true` (AC-143.21); `a 40x40 square: expected [ 10, 10, 40, 20 ] to deeply equal [ 10, 10, 40, 40 ]` (AC-143.23); `expected 'Six annotation tools: …' to contain 'The lock is on by default: …'` (AC-87.7, AC-143.31) | Row 4: `Test Files  24 passed (24)`, `Tests  468 passed (468)` (`s71b-ui-green.txt`); gate `ui-tests` | `capture-tool-flow.behavior.test.ts:692-1285`; `capture-tool-lock.test.ts:116-270`; `capture-page.behavior.test.ts:3323-3438`; `capture-help-content.test.ts:93`, `:105` |
| AC-143.29 and AC-87.6 (Electron) | Row 3: `1 failed` each, exit 1 (`s71b-e2e-red-143.txt`, `s71b-e2e-red-87.txt`): `expect(locator).toHaveAttribute(expected) failed`, `Expected: "true"` / `Received: "false"` for Lock's `aria-pressed` at load | Row 4: `51 passed (1.3m)` (`s71b-e2e-green.txt`); gate `ui-electron` | `capture-inbox.test.ts:3500`, `:2570` |
| The moved hint and help pins | Row 3: `Test Files  4 failed \| 6 passed (10)`, `Tests  6 failed \| 152 passed (158)`, exit 1 (`s71b-r3-moved.txt`): AC-81.12, AC-131.11 (two tests), AC-131.12, AC-103.15 and AC-80.8, for example `expected 'Crop' to be 'Crop (C)'` and `capture-tool-select-hint text: expected 'Select' to be 'Select (V)'`. In `s71b-ui-red.txt` the AC-65.2 hint tests and the AC-60.15, AC-66.16, AC-89.8 and AC-99.6 help tests failed too, on the lettered hints and the moved nudge words | Row 4: `s71b-ui-green.txt`; gate `ui-tests` | `capture-action-row.test.ts:713`; `capture-crop-tool.behavior.test.ts:415-473`; `capture-redact.behavior.test.ts:269`; `icon-hints.test.ts:338`; `capture-page.behavior.test.ts:1516`, `:1554`; `capture-help-content.test.ts:25-128` |
| AC-143.1 to .5, .15's registry half, .30, .33, .34, .35 | Met by rows 1 and 2, or guards that pass where written. Row 2: `267 passed in 24.00s` (`s71b-r2-py.txt`), `Tests  302 passed (302)` (`s71b-r2-mcp.txt`). Row 3's guards: AC-143.1 `Tests  1 passed \| 6 skipped (7)` (`s71b-r3-guard-1.txt`), AC-143.30 `Tests  1 passed \| 44 skipped (45)` (`s71b-r3-guard-30.txt`), AC-143.33 `Tests  2 passed \| 43 skipped (45)` (`s71b-r3-guard-33.txt`), AC-143.34 `Tests  1 passed \| 44 skipped (45)` (`s71b-r3-guard-34.txt`); AC-143.35 `titles holding Apply,: []` (`s71b-r3-ac35.txt`) | Row 4's runs and the gate | `test_capture_tool_lock.py:46-95`; `test_api_capture_tool_lock.py:48-97`; `capture.test.ts:1750`; `capture-tool-lock.test.ts:59`, `:134`; `capture-tool-flow.behavior.test.ts:1310`, `:1334`, `:1366`, `:1380` |
| AC-143.32, AC-143.36 | Row 5's check exits 1 before row 5 (plan §Verification Plan) | Row 5: all 12 keys `True` (`s71b-r5-spec.txt`) and `Tests  19 passed (19)` (`s71b-r5-actions.txt`) | row 5 |

- **red-check.** Row 3's check (`s71b-red-check.txt`) reads `red-check: 3 receipt(s), 31 required test(s), 0 problem(s)`. The 31 required ids are AC-143.6 to AC-143.29 and AC-143.31, AC-87.2 to AC-87.5, AC-87.6 and AC-87.7. Every required failing block failed by assertion alone.
- **The passes in the Red run.** The 141 Vitest passes in `s71b-ui-red.txt` are AC-143.1, AC-143.15, AC-143.30, AC-143.33 and AC-143.34 and the existing `capture-page.behavior.test.ts` and `capture-help-content.test.ts` tests that the change doesn't touch. AC-143.15 passed at Red because row 1 had added the registry entries, `TOOL_LETTERS` and BOUND_CONTROLS as type-only names with their final values; red-check doesn't require it.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71b/row0.ps1 > C:/Temp/av-kit/s71b/row0.outer.txt 2>&1 (task.md row 0's Validation cell, written to a .ps1 from the cell text: baseline.ps1 *> C:/Temp/av-kit/s71b-baseline.txt; base runs in C:/Temp/av-kit/s71b-base-py.txt, s71b-base-ui.txt, s71b-base-mcp.txt, s71b-base-e2e.txt, s71b-base-ui-build.txt, s71b-base-mcp-build.txt and s71b-base-ruff.txt; Electron reruns C:/Temp/av-kit/s71b/row0-e2e-rerun.ps1 *> C:/Temp/av-kit/s71b-base-e2e-rerun.txt and s71b-base-e2e-rerun2.txt; notes C:/Temp/av-kit/s71b/row0-notes.txt)", "scope": "Row 0: the D-757 words, the queue, the shapes (S7), baseline.sha, baseline-dirty.txt, the anchors and line endings, the lock syncs, the FFmpeg pair, the base runs, and the identity, id-length and red-check selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 42f02bc before any row", "output": "execute: said to execute (USER_EXPLICIT 2026-11-14 'Execute now (Recommended)'); queue: MEU-87, MEU-99, MEU-100 and MEU-105 approved, MEU-143, MEU-106 and MEU-107 pending; 42f02bc is an ancestor of HEAD: True; shapes wrong (S7): []; missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; ffmpeg version n8.1.3-27-g8dca1586f4-20261031; base pytest 2608 passed, 37 warnings in 229.24s; base UI Test Files 126 passed (126), Tests 1370 passed (1370); base MCP Tests 529 passed (529) in 36 files; base Electron first run 1 failed, 49 passed (1.4m) (AC-81.11, ShareX held F2); rerun 1 failed, 49 passed (1.4m) (AC-67.20 toBeVisible); rerun2 50 passed (1.2m); base ruff All checks passed!; red-check selftest: 68 fixture(s) (21 positive, 47 negative), 0 wrong; identity selftest: 0 failure(s); id-length selftest: 4 case(s), 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-1-types", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71b/row1.ps1 > C:/Temp/av-kit/s71b/row1.outer.txt 2>&1 (task.md row 1's Validation cell: npm --prefix ui run typecheck *> C:/Temp/av-kit/s71b-types-ui.txt; ui lint *> C:/Temp/av-kit/s71b-types-ui-lint.txt; the UI files *> C:/Temp/av-kit/s71b-types-ui-tests.txt; capture-action-row.test.ts *> C:/Temp/av-kit/s71b-types-action-row.txt; sweep C:/Temp/av-kit/s71b/row1-sweep.txt appended to C:/Temp/av-kit/s71b-anchors.txt)", "scope": "Row 1: the type-only names (readToolLock, saveCaptureToolLock, lockSaveFailures, subscribeLockSaveFailures, useCaptureToolLock, captureLockPutSchema, TOOL_LETTERS, CAPTURE_TOOL_IDS, lib/editable-target.ts, the exported FIELD_STEP_SHIFT, capture-modifiers.ts, SurfacePointer.altKey) and the caller sweep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 42f02bc plus rows 0 to 1", "output": "ui typecheck and lint exit 0; Test Files 10 passed (10), Tests 247 passed (247); capture-action-row Tests 13 passed (13); sweep 455 lines, anchors 515 lines"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-2-settings", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71b/row2.ps1 > C:/Temp/av-kit/s71b/row2.outer.txt 2>&1 (task.md row 2's Validation cell: pytest *> C:/Temp/av-kit/s71b-r2-py.txt; export_openapi.py --check *> C:/Temp/av-kit/s71b-r2-openapi.txt; the delta check *> C:/Temp/av-kit/s71b-r2-openapi-delta.txt; pyright *> C:/Temp/av-kit/s71b-r2-pyright.txt; ruff *> C:/Temp/av-kit/s71b-r2-ruff.txt; id-length.py *> C:/Temp/av-kit/s71b-r2-id-length.txt; mcp typecheck *> C:/Temp/av-kit/s71b-r2-mcp-types.txt; MCP tests *> C:/Temp/av-kit/s71b-r2-mcp.txt)", "scope": "Row 2: LOCK_LEAF in the service, the API with the regenerated snapshot, and MCP; the AC-36.12, AC-38.6, AC-105.2 and AC-105.5 pins; AC-143.1 (Python), .2 to .5 and .22's Python half", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 42f02bc plus rows 0 to 2", "output": "267 passed in 24.00s; export_openapi --check exit 0; SettingsPutIn added: ['tool_lock'] rest of the document unchanged: True; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; id-length: 22 test(s), 0 too long; mcp typecheck exit 0; Test Files 20 passed (20), Tests 302 passed (302)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-3-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71b/row3.ps1 > C:/Temp/av-kit/s71b/row3.outer.txt 2>&1 (task.md row 3's Validation cell: Vitest capture-tool-lock.test.ts, capture-tool-flow.behavior.test.ts, capture-help-content.test.ts and capture-page.behavior.test.ts *> C:/Temp/av-kit/s71b-ui-red.txt; ui build *> C:/Temp/av-kit/s71b-r3-ui-build.txt; playwright capture-inbox.test.ts -g AC-143.29 *> C:/Temp/av-kit/s71b-e2e-red-143.txt; -g AC-87.6 *> C:/Temp/av-kit/s71b-e2e-red-87.txt; red-check.py with the 31 --require ids *> C:/Temp/av-kit/s71b-red-check.txt; the guards *> C:/Temp/av-kit/s71b-r3-guard-1.txt, s71b-r3-guard-30.txt, s71b-r3-guard-33.txt, s71b-r3-guard-34.txt; the AC-143.35 check *> C:/Temp/av-kit/s71b-r3-ac35.txt; the hash run *> C:/Temp/av-kit/s71b-r3-hash.txt; the moved pins *> C:/Temp/av-kit/s71b-r3-moved.txt)", "scope": "MEU-143 Red: AC-143.6 to .29 and .31 and the rewritten AC-87.2 to .7 against the row 2 code; the AC-143.1, .30, .33 and .34 guards; AC-143.35; the AC-51.6 hash; the moved pins failing before Green", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 42f02bc plus rows 0 to 3", "output": "Vitest Test Files 4 failed (4), Tests 59 failed | 141 passed (200) (child exit 1): no tool_lock: on: expected 'false' to be 'true'; v is prevented: expected false to be true; a 40x40 square: expected [ 10, 10, 40, 20 ] to deeply equal [ 10, 10, 40, 40 ]. ui build built in 3.73s. Electron AC-143.29 1 failed and AC-87.6 1 failed (child exit 1 each): toHaveAttribute Expected: \"true\" Received: \"false\". red-check: 3 receipt(s), 31 required test(s), 0 problem(s). Guards: Tests 1 passed | 6 skipped (7); Tests 1 passed | 44 skipped (45); Tests 2 passed | 43 skipped (45); Tests 1 passed | 44 skipped (45). AC-143.35 titles holding Apply,: []. Hash Tests 1 passed | 12 skipped (13). Moved pins: Test Files 4 failed | 6 passed (10), Tests 6 failed | 152 passed (158) (child exit 1, expected before Green)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-4-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71b/row4.ps1 > C:/Temp/av-kit/s71b/row4-console.txt 2>&1 (task.md row 4's Validation cell, written to a .ps1 from the cell text: npm --prefix ui run typecheck *> C:/Temp/av-kit/s71b-r4-ui-types.txt; ui lint *> C:/Temp/av-kit/s71b-r4-ui-lint.txt; Vitest over the 24 recorded files *> C:/Temp/av-kit/s71b-ui-green.txt; ui build *> C:/Temp/av-kit/s71b-r4-ui-build.txt; Electron capture-inbox.test.ts *> C:/Temp/av-kit/s71b-e2e-green.txt; Electron capture-picker.test.ts *> C:/Temp/av-kit/s71b-e2e-picker.txt; pytest *> C:/Temp/av-kit/s71b-py-green.txt; export_openapi.py --check *> C:/Temp/av-kit/s71b-r4-openapi.txt; MCP capture.test.ts *> C:/Temp/av-kit/s71b-mcp-green.txt)", "scope": "MEU-143 Green: LOCK_DECODE, LOCK_STORE, ONE_SHOT, LOCK_SELECTS, ARMED_EDIT, ARMED_RECHOOSE, LETTERS, LETTER_HINTS, FIELD_GUARD, CHORD_BUBBLE_ONCE, MODIFIERS, SHIFT_NUDGE, ALT_NO_MENU and LOCK_HELP; every caller and test row 1 recorded; the plan's guards", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 42f02bc plus rows 0 to 4", "output": "typecheck and lint exit 0; Test Files 24 passed (24), Tests 468 passed (468); ui build built in 3.68s; Electron 51 passed (1.3m); picker 4 passed (10.8s); pytest 245 passed in 19.42s; export_openapi --check exit 0; MCP Tests 60 passed (60)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-5-spec", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71b/row5.ps1 > C:/Temp/av-kit/s71b/row5-console.txt 2>&1 (task.md row 5's Validation cell, written to a .ps1 from the cell text: the spec and index check *> C:/Temp/av-kit/s71b-r5-spec.txt; gui-actions-audit.test.ts *> C:/Temp/av-kit/s71b-r5-actions.txt)", "scope": "Row 5 (D3, AC-143.32, AC-143.36): FLOW_ACTIONS_INDEX, 09's Delivered (Session 71b) note and the Entry note's Crop (C); CRLF kept", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 42f02bc plus rows 0 to 5", "output": "{'index_crlf': True, 'index_order': True, 'letters': True, 'lock_row': True, 'modifiers_row': True, 'crlf_09': True, 'note_after_71': True, 'one_note': True, 'names_acs': True, 'names_mechanisms': True, 'plan_folder': True, 'entry_note': True}; Test Files 1 passed (1), Tests 19 passed (19)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-6-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71b/row6.ps1 > C:/Temp/av-kit/s71b/row6-console.txt 2>&1 (task.md row 6's Validation cell, written to a .ps1 from the cell text: the status check *> C:/Temp/av-kit/s71b-r6-status.txt; meu_status.py render --check *> C:/Temp/av-kit/s71b-r6-render.txt; the canon tests *> C:/Temp/av-kit/s71b-r6-canon.txt; pre-status copies in C:/Temp/av-kit/s71b/pre-status/)", "scope": "Row 6: MEU-143 ready_for_review with its execution_plan, the D-756 band in grouping row 47b, the registry and BUILD_PLAN renders", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 42f02bc plus rows 0 to 6", "output": "band from D-756: P2 {'d756_ruled': True, 'meu143': True, 'status_lf': True, 'row47b': True, 'grouping_crlf': True}; Drift check passed - SSOT loaded (143 MEUs, 12 phases), rendered regions match on-disk content; Test Files 2 passed (2), Tests 14 passed (14)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; pwsh -NoProfile -File docs/execution/plans/2026-11-14-capture-tool-flow/session-gate.ps1 > C:/Temp/av-kit/s71b-gate-h1.txt 2>&1 (task.md row H1-2's gate, rerun after D-766 added capture-crop.ts to the allowed set, with RECEIPTS_DIR=C:/Temp/av-kit and PYTHONIOENCODING=utf-8; console C:/Temp/av-kit/s71b/h1-2-console.txt; step receipts C:/Temp/av-kit/s71b-D6-*.txt; the first run's receipts are kept in C:/Temp/av-kit/s71b/gate-r0/)", "scope": "The plan's full gate: identity before; static py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest and id-length; fresh full py-tests, openapi, action-row (the AC-51.6 byte-hash guard), ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render and issues-render; runtime ui-electron (capture-inbox.test.ts); identity after. mcp-audit and build-record skipped by the plan", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "42f02bcd7baddfbd8e0002ba2c36b44d9d649cf5+b79888cd4375e1c3d856b8bd5274fe7e4c713c1d23aabe02127660f42e6d90c9", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; ui-types and ui-lint exit 0; task-contract OK: 24 row(s), 22 row(s) fully checked, 2 row(s) exempt (view_file): H1-5, H2-1; scope-paths changed paths: 57 outside scope: [] head moved (S3): False; baseline-dirty paths changed since row 0 (S3): []; red-check selftest: 68 fixture(s) (21 positive, 47 negative), 0 wrong; id-length: 22 test(s), 0 too long; py-tests 2630 passed, 37 warnings in 178.75s; openapi exit 0; action-row Tests 13 passed (13); ui-tests Test Files 128 passed (128), Tests 1423 passed (1423); ui-build built in 3.80s; mcp-types and mcp-build exit 0; mcp-tests Test Files 36 passed (36), Tests 530 passed (530); state-render Drift check passed - SSOT loaded (143 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 51 passed (1.2m); tested_state before = after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s71b-h1-3-h1-4", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s71b/h1-3.ps1 (task.md row H1-3's Validation cell: meu_status.py render --check *> C:/Temp/av-kit/s71b-drift-check.txt; meu_status.py get MEU-143 *> C:/Temp/av-kit/s71b-h13-status.txt; check *> C:/Temp/av-kit/s71b-h13-check.txt); pwsh -NoProfile -File C:/Temp/av-kit/s71b/h1-4.ps1 (task.md row H1-4's Validation cell: export_openapi.py --check *> C:/Temp/av-kit/s71b-openapi-check.txt; delta check against baseline.sha *> C:/Temp/av-kit/s71b-openapi-delta-check.txt)", "scope": "H1-3 the MEU-143 status read after the gate; H1-4 the OpenAPI snapshot check and its delta from baseline.sha: tool_lock in SettingsPutIn only", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "42f02bcd7baddfbd8e0002ba2c36b44d9d649cf5+b79888cd4375e1c3d856b8bd5274fe7e4c713c1d23aabe02127660f42e6d90c9", "output": "Drift check passed - SSOT loaded (143 MEUs, 12 phases), rendered regions match on-disk content; MEU-143 ready_for_review: True; openapi --check exit 0; SettingsPutIn added: ['tool_lock'] rest of the document unchanged: True"}
```

### Quality Gate Results

The H1-2 gate's last line is `session-gate: all steps exit 0` (`s71b-gate-h1.txt:120`). It passed on its second run. The first run stopped at scope-paths with exit 1, because `capture-crop.ts` wasn't in the allowed set (D-766, §Departures 3); its receipts are kept in `s71b/gate-r0/`. The figures below are the second run's.

- **Static.** pyright `0 errors, 0 warnings, 0 informations` (`s71b-D6-py-types.txt`); ruff `All checks passed!` (`s71b-D6-py-lint.txt`); UI typecheck and lint (`--max-warnings 0`) exit 0. The checks of the plan's own tooling also passed:
  - the task contract: `24 row(s)`, `22 row(s) fully checked`, `2 row(s) exempt (view_file): H1-5, H2-1` (`s71b-D6-task-contract.txt`);
  - scope-paths: `changed paths: 57 outside scope: []`, `head moved (S3): False`, and `baseline-dirty paths changed since row 0 (S3): []` (`s71b-D6-scope-paths.txt`);
  - the red-check selftest: `68 fixture(s) (21 positive, 47 negative), 0 wrong` (`s71b-D6-red-check-selftest.txt`);
  - id-length: `22 test(s), 0 too long` (`s71b-D6-id-length.txt`).
- **Suites, against the Session 71b baseline** (`s71b-base-*.txt`):
  - pytest `2630 passed, 37 warnings in 178.75s` (`s71b-D6-py-tests.txt`). The baseline had `2608 passed` (`s71b-base-py.txt`), so 22 tests are new, and id-length checked 22 new ids;
  - Vitest `Tests  1423 passed (1423)` in `128 passed (128)` files (`s71b-D6-ui-tests.txt`). The baseline had `Tests  1370 passed (1370)` in 126 files (`s71b-base-ui.txt`); the two new files are `capture-tool-lock.test.ts` and `capture-tool-flow.behavior.test.ts`;
  - MCP `Tests  530 passed (530)` (`s71b-D6-mcp-tests.txt`): the baseline's `529 passed` (`s71b-base-mcp.txt`) plus AC-143.5;
  - Electron `51 passed (1.2m)` (`s71b-D6-ui-electron.txt`): the baseline's `50 passed (1.2m)` (`s71b-base-e2e-rerun2.txt`) plus AC-143.29. AC-67.20, AC-81.11 and AC-100.11 passed.
- **Build.** UI build `built in 3.80s` (`s71b-D6-ui-build.txt`); MCP typecheck and build exit 0; the OpenAPI check exit 0 (`s71b-D6-openapi.txt`); the state render `Drift check passed` and the known-issues render `OK: known-issues.md is up-to-date`.
- **The byte-hash guard.** `action-row` passed `Tests  13 passed (13)` (`s71b-D6-action-row.txt`), so AC-51.6 still reads `6E569F82…870FF454`.
- **After the gate.**
  - H1-3 exits 0. `s71b-h13-check.txt` reads `MEU-143 ready_for_review: True`; `s71b-drift-check.txt` reads `Drift check passed`.
  - H1-4 exits 0. `s71b-openapi-delta-check.txt` reads `SettingsPutIn added: ['tool_lock'] rest of the document unchanged: True`.
  - `current-focus.md` and this handoff are outside `tested_state`.
- **Skipped by the plan.** `mcp-audit` was skipped because it needs the live network and YouTube, which the brief forbids. No action changed, so the audit baseline doesn't change. `build-record` was skipped because there is no release and no package build.
- **Identity.** `tested_state` before and after: `42f02bcd7baddfbd8e0002ba2c36b44d9d649cf5+b79888cd4375e1c3d856b8bd5274fe7e4c713c1d23aabe02127660f42e6d90c9` (`s71b-D6-identity-before.txt`, `s71b-D6-identity-after.txt`).
- **Warnings.** pytest reports 37 warnings, the same count as the baseline run (`s71b-base-py.txt`). No test fails on a warning.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/settings.py` | modified | The `tool_lock` row (LOCK_LEAF) |
| `packages/api/src/avkit_api/schemas/settings.py`, `openapi.committed.json` | modified | `SettingsPutIn.tool_lock` and the regenerated snapshot (LOCK_LEAF, D-744) |
| `mcp-server/src/toolsets/settings.ts` | modified | `SETTINGS_SCHEMA` and the set schema's `tool_lock` (LOCK_LEAF) |
| `ui/src/renderer/src/features/capture/capture-tool-lock.ts`, `useCaptureToolLock.ts`, `capture-modifiers.ts`, `ui/src/renderer/src/lib/editable-target.ts` | new | LOCK_DECODE, LOCK_STORE's hook, MODIFIERS and FIELD_GUARD's `isEditableTarget`. LF, 11, 33, 122 and 27 lines |
| `ui/src/renderer/src/features/capture/capture-style-store.ts`, `ui/src/renderer/src/features/settings/settings-schemas.ts` | modified | LOCK_STORE's shared core and `captureLockPutSchema` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | ONE_SHOT, LOCK_SELECTS, ARMED_EDIT, the published letter state, CHORD_BUBBLE_ONCE, MODIFIERS, SHIFT_NUDGE |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | LETTER_HINTS, `SurfacePointer.altKey`, ALT_NO_MENU, the Lock button |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts`, `CaptureCropBar.tsx`, `capture-crop.ts`, `capture-import.ts`, `capture-help-content.ts` | modified | `TOOL_LETTERS`; the exported `FIELD_STEP_SHIFT`; the three exported ratio helpers (D-766); the `isEditableTarget` re-export; LOCK_HELP |
| `ui/src/renderer/src/registry/commandRegistry.ts`, `shortcuts.ts` | modified | LETTERS' eight entries; BOUND_CONTROLS and FIELD_GUARD |
| `tests/unit/test_capture_tool_lock.py`, `tests/e2e/test_api_capture_tool_lock.py`, `ui/tests/unit/capture-tool-lock.test.ts`, `ui/tests/unit/capture-tool-flow.behavior.test.ts` | new | The MEU-143 tests. LF, 105, 123, 282 and 1392 lines |
| `tests/unit/test_capture_service.py`, `tests/unit/test_capture_style_settings.py`, `mcp-server/tests/capture.test.ts` | modified | The key-set and order pins; AC-143.5 |
| `ui/tests/e2e/capture-inbox.test.ts`, `ui/tests/unit/capture-page.behavior.test.ts`, `capture-help-content.test.ts`, `capture-action-row.test.ts`, `icon-hints.test.ts`, `capture-redact.behavior.test.ts`, `capture-crop-tool.behavior.test.ts` | modified | The moved pins, AC-143.29, AC-143.31 and the `tool_lock: false` fakes |
| `ui/tests/unit/capture-copy-image.behavior.test.ts`, `capture-filmstrip-actions.behavior.test.ts`, `capture-import.behavior.test.ts`, `capture-style-flow.behavior.test.ts`, `capture-text-lines.behavior.test.ts`, `ui/tests/e2e/capture-filmstrip-actions.test.ts`, `capture-import.test.ts`, `capture-picker.test.ts` | modified | The `tool_lock: false` fakes only |
| `docs/build-plan/09-screenshot-capture.md`, `docs/build-plan/gui-actions-index.md` | modified | FLOW_SPEC and FLOW_ACTIONS_INDEX (row 5) |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | MEU-143 `ready_for_review` with its plan; grouping row 47b's band P2 (D-756) and status (row 6) |
| `.agent/context/current-focus.md` | modified | Session 71b's paragraph (H1-3) |

`git diff --stat 42f02bc`, without `docs/execution/` and the handoffs, reads `40 files changed, 692 insertions(+), 177 deletions(-)`. The eight new source and test files above are untracked, so they aren't in that count.

Line endings were measured with Python bytes before each edit, and each file kept its endings:

- **CRLF.** `services/settings.py`, `schemas/settings.py`, `openapi.committed.json`, `mcp-server/src/toolsets/settings.ts`, `mcp-server/tests/capture.test.ts`, `test_capture_service.py`, `CapturePage.tsx`, `CaptureViewport.tsx`, `capture-help-content.ts`, `capture-toolbar.ts`, `settings-schemas.ts`, `capture-action-row.test.ts`, `capture-help-content.test.ts`, `capture-page.behavior.test.ts`, `icon-hints.test.ts`, 09, `gui-actions-index.md`, the grouping file and `current-focus.md`.
- **LF.** `capture-style-store.ts`, `capture-crop.ts`, `capture-import.ts`, `CaptureCropBar.tsx`, `commandRegistry.ts`, `shortcuts.ts`, `test_capture_style_settings.py`, the Electron specs, the LF unit harnesses, `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md`.
- **New files** are LF.

```diff
 # capture-style-store.ts, saveCaptureToolLock (abridged)
+export function saveCaptureToolLock(client: QueryClient, locked: boolean): void {
+  const parsed = captureLockPutSchema.safeParse({ tool_lock: locked })
+  commitLeaves(client, { tool_lock: parsed.data.tool_lock }, lockFailureListeners, …)
 # CapturePage.tsx, LOCK_SELECTS (abridged)
+        commitSelection(list.length - 1, list, toolLocked ? tool : 'select')
 # CapturePage.tsx, SHIFT_NUDGE (abridged)
+    const step = event.shiftKey ? FIELD_STEP_SHIFT : KEYBOARD_NUDGE_PX
```

The excerpt is abridged. The sources are `capture-style-store.ts:218-223`, `CapturePage.tsx:1382` and `:1976`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-14-capture-tool-flow-implementation-critical-review.md`, on the ledger loop `s71b-execution-2026-11-14-capture-tool-flow` (cap 6 rounds; no token budget, `token_budgets: "off"`). The estimate is about 25M tokens (plan §User Review Required). The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | 0 (0 blocking); intent achieved: yes; 12,910,076 tokens | `42f02bcd7baddfbd8e0002ba2c36b44d9d649cf5+b79888cd4375e1c3d856b8bd5274fe7e4c713c1d23aabe02127660f42e6d90c9`, recomputed by the reviewer with `identity.py --state-only` |

### Verdict

`approved` at round 1 of 6, with no findings (`.agent/context/handoffs/2026-11-14-capture-tool-flow-implementation-critical-review.md`, a byte-for-byte copy of `C:/Temp/av-kit/s71b-exec-review-round-1.md`). The ledger recorded round 1 `approved`, blocking 0, intent achieved yes, usage 12,910,076 tokens, against the estimate of about 25M. H1-7a reads `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0` (`s71b-review-state-check.txt`) and H1-7b reads `OK: approved at round 1 of 6, 0 open blocking findings` (`s71b-exec-review.txt`). The reviewer ran its own API and storage probe, red-check with the 31 ids (`0 problem(s)`), the OpenAPI and render checks, and an audit of 35 receipts and the line endings of the 40 modified files; it ran no test suite, GUI or clipboard spec.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The two clipboard Electron specs, `capture-filmstrip-actions.test.ts` and `capture-import.test.ts`, were not run after their fakes gained `tool_lock: false` | observation | Mat | Session 57 RULE-4: they write the real clipboard. They typecheck and lint in the gate |
| `ruff check tools/` fails on errors in `tools/issue_triage*` and `tools/meu_status*` that were there before this session | observation | None | Session 68 DEP-1; this plan lints only the files it edits |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2) |

### Departures and their basis

1. **A pin the plan didn't name (row 3, D-764).** AC-65.2's negative test (`capture-page.behavior.test.ts:1554`) read the no-shot tool hints without letters. §Pins that move didn't list it, because it builds the hint from the spec name. Row 3 moved it to the lettered form that LETTER_HINTS states, before Green. It failed at Red (§FAIL_TO_PASS). No AC text changed.
2. **Two set-up defects in the Red flow tests, fixed during Green (row 4, S2, D-765).** Row 4 says no test file changes (S2). Both edits fix how a test reaches its state; neither changes what it asserts or an AC's text.
   - **AC-143.17's no-shot half** (`capture-tool-flow.behavior.test.ts:990`) mounted the page on a catalog with a shot, and the page selects the newest shot, so there was no no-shot state. It now serves an empty catalog, as AC-65.2 does.
   - **AC-143.27's burst** (`:1236`) read the mark after Undo with nothing selected, because Undo clears the selection. It now selects the mark again after each Undo, and it checks that the plain burst reached the edge.
3. **A file the plan didn't list (row 4, D-766).** `keepRatioResize` keeps the ratio the way the crop's corner does, so row 4 exported `largestDriving`, `drivingFromWidth` and `drivingFromHeight` from `capture-crop.ts` rather than copying them. The H1-2 gate's first run refused the path at scope-paths (exit 1; receipts kept in `s71b/gate-r0/`). The plan's file list and the gate's allowed set now name it, and the gate was run again. Only the `export` keyword was added; no body, behaviour or AC changed.
4. **The baseline Electron runs (row 0).** At `42f02bc`, before any change:
   - the first run had `1 failed` and `49 passed (1.4m)` (`s71b-base-e2e.txt`): AC-81.11, because ShareX held F2. Mat chose to quit ShareX (`USER_EXPLICIT` 2026-11-14 "I'll quit ShareX (Recommended)");
   - the rerun, started while ShareX was closing, passed AC-81.11 and had `1 failed` and `49 passed (1.4m)` (`s71b-base-e2e-rerun.txt`): AC-67.20's hover hint, `expect(locator).toBeVisible() failed` for `capture-apply-image-hint`. It passed in the first run;
   - the second rerun passed `50 passed (1.2m)` (`s71b-base-e2e-rerun2.txt`), the base count.

   AC-67.20 is a pointer-position test. It passed in row 4's run (`51 passed (1.3m)`, `s71b-e2e-green.txt`) and in the gate. AC-100.11 didn't fail in any run.

No departure changed an AC's text. The execution decisions D-758 to D-766 are autonomous and two-way, and they are in the plan's `decision_log`.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-14 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, row 1's sweep, the moved pins, the Red and Green receipts, the H1-2 gate and the evidence records (H1-6) |
| Reviewed | 2026-11-14 | codex-independent-reviewer | Execution review round 1 `approved`, 0 findings (H1-7, H1-7a, H1-7b) |
