---
project: "2026-11-13-capture-style-tool-flow"
date: "2026-11-13"
source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md#session-47--capture-style-tool-flow-meu-105--p3"
grouping_source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md"
meus: ["MEU-105"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture style on click and per-tool style (Session 71)

> **Project:** `2026-11-13-capture-style-tool-flow`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Style and tool flow (`:970-982`, anchor `style-and-tool-flow`, MEU-105), with the build priority matrix row 9.31 (`docs/build-plan/build-priority-matrix.md:129`).
>
> **Source request.** On 2026-10-29 Mat accepted the capture annotation editor synthesis ("all recommendations are accepted", grouping D-158). The grouping's §3 lists this as Session 47 (`:87-89`) and its §6 tracker as row 47 (`:125`); §9.1 runs it as Session 71 (D-674). On 2026-11-13 Mat split MEU-105 (D-713, USER_EXPLICIT 2026-11-13 "A"): this session delivers the style half, and Session 71b delivers the tool-flow half as the new MEU-143.
> **Status:** `draft`. `plan_to_exec_gate: human`. The plan review approved at round 3 (`.agent/context/handoffs/2026-11-13-capture-style-tool-flow-plan-critical-review.md`), after rounds 1 and 2 returned `changes_required` (F1, F2, F3; all fixed) and Mat added 7M for round 3 (D-728). At the plan gate Mat set the execution review budget to 33M (USER_EXPLICIT 2026-11-14 '33M (Recommended)') and said to execute (USER_EXPLICIT 2026-11-14 'Execute now (Recommended)'), with the default execution cap of 6 rounds (D-727).

## Goal

**Goal anchor:** Session 71 makes colour apply on click and gives each tool its own remembered style. A swatch applies when it is picked, the hex field applies on Enter or blur, and one click or one scrub is one undo step; the Apply/Cancel gate goes. Arrow, Box, Highlight, Text and Pixelate each keep their own style as an app preference in the `capture` settings namespace, never in mark JSON. With a mark selected, a style control restyles only that mark; with none selected, it sets the active tool's style. The Pixelate block size gets the same scrub as Stroke and Size.

Four things are missing today (`5e9ea7c`):

1. **The colour gate.** A swatch, the well and the hex field only set a candidate (`CapturePage.tsx:371`, `:460-464`). Nothing changes until Apply (`applyColor`, `:1439`), Cancel throws the candidate away (`cancelColor`), and while the candidate differs, Save is off and the status reads `Apply or Cancel color` (`COLOR_GATE_MESSAGE`, `:103`, `:2065`), and a tool change is refused (`chooseTool`, `:997`).
2. **One style for all tools.** The page holds one `color`, `stroke`, `fontSize`, `textBg` and `blockSize` (`:370-375`) for every tool, starting at `#E0AF68`, 3, 16, empty and 10, and nothing is saved: a reload starts from those values again. `applyColor` sets the global colour and the selected mark's at once.
3. **The text background well writes history on every input event.** `changeTextBg` (`:1419`) applies one history step per call, and the well's `onInput` and `onChange` both call it (`CaptureViewport.tsx:1146-1151`), so one drag in the picker makes many undo steps.
4. **No block-size scrub.** Block size is a plain number input (`CaptureViewport.tsx:1209-1220`); Stroke and Size are `CaptureScrubField`s (`:1171-1190`). The grouping's §9.3 (`:176`) names it as owed.

Today's behaviour was read at `5e9ea7c` (Session 69 RULE-1): the colour gate and its pins are in `C:/Temp/av-kit/s71/pin-sweep.txt`; Lock is off by default (`CapturePage.tsx:369`) and the shortcut registry has no tool letters, which are MEU-143's.

The session ends when:
- every MEU-105 part of 09 §Style and tool flow holds (the Colour row, the Tool style row and the Modifiers row's Pixelate scrub), each with a behaviour test;
- the split is in the records (09, the matrix, `meu-status.yaml`, the grouping);
- the session gate's last line is `session-gate: all steps exit 0`;
- MEU-105 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-13). No payload is oversized: the settings service, the API schema, the MCP settings toolset, the settings hook, the toolbar, the viewport and the page were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, `.agent/context/harness.local.md` Claude Code block). Execution waits for Mat's explicit words at the plan gate (§Status, D-727). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit` with the `s71-*` names;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s71\tmp` for the Python suite;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run, and the scripts clear it as well.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS. GUI references are not shipped (`gui-refs-not-shipped`).
- **Decisions:** every decision for Mat goes to Mat through the Human Decision Protocol (AGENTS.md §Communication Policy), with a recommendation first and a do-nothing option. No decision goes to a subagent in this session.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s71-plan-canonical-2026-11-13-capture-style-tool-flow` and `s71-execution-2026-11-13-capture-style-tool-flow`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Round caps: the ledger defaults, plan 3 and execution 6.
  - Token budgets: the plan loop opens at the budget Mat sets before its first dispatch (D-726). The execution loop opens at the budget Mat sets at the gate (`begin --token-budget`, D-727). The ledger defaults are 10.5M for a plan review and 21M for an execution review (`tools/review_ledger.py:102`).
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit`, then copied byte for byte to its canonical path, and the `--review-state-only` receipt is rebuilt there.
- **Reviewer prompts:**
  - They name the ledger vocabulary up front: D-713 to D-728, AC-105.1 to AC-105.32, and the mechanism ids in §Single-statement contracts.
  - They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and they write `<HOME>` for the home folder.
  - When a prompt asks for `tested_state`, it names `~/.config/git/ignore` and the path that file hides, `.claude/settings.local.json` (Session 51 RULE-4).
  - `## Findings` holds only the Findings table (Session 65 RULE-3).
  - Every prompt carries the literal `### New Findings` header and the Prior Pass Summary table, with the columns Finding, Prior Status and Recheck Result (Session 66 RULE-4).
  - A recheck names each prior finding by the review's own id (Session 53 RULE-3) and asks for bare words in its Recheck cells (`fixed`, `open`; Session 52 RULE-1, Session 57 RULE-5).
- **Never in these rows without Mat's words:**
  - a commit, a push, a tag, a release or an upload;
  - the live MCP audit or `--update-baseline`;
  - `npm run dist`;
  - an `approved` verdict authored by the implementer;
  - reading any user data: the capture inbox, its sidecars, the app database or Mat's settings file (Session 70 RULE-2). Every test works from fixtures and fakes.
- **No network, no clipboard:**
  - no test or row reaches YouTube or the network;
  - no test or row writes the system clipboard (Session 57 RULE-4);
  - nothing touches the installed avkit MCP servers (no `mcp__avkit__*` tool is called);
  - no other program is stopped. If ShareX holds a key a row needs, the row stops and asks Mat (S13).

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-105 | `.agent/context/handoffs/2026-11-13-capture-style-tool-flow-MEU-105-handoff.md` | only |

Rolling reviews: `.agent/context/handoffs/2026-11-13-capture-style-tool-flow-plan-critical-review.md` and `.agent/context/handoffs/2026-11-13-capture-style-tool-flow-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0 | Baseline: rulings, queue, shapes, dirty paths, anchors, base suites, selftests | shared |
| WP-2 | 1 | Type-only names: `SettingSpec.pattern` and `integer`, `capture-tool-style.ts`'s exported names, `useCaptureToolStyles`, `CaptureScrubField`'s `min`, `CAPTURE_BLOCK_SIZE_SCRUB` | shared |
| WP-3 | 2 | The settings rows, the API leaves, the regenerated OpenAPI snapshot and the MCP leaves | shared |
| WP-4 | 3, 4 | Red, then Green (the behaviour and the help text) | shared |
| WP-5 | 5 | The actions index and 09's split note, MEU row and Delivered note | shared |
| WP-6 | 6 | The split records, status and grouping | shared |
| WP-7 | H1, H2 | Gate, handoff, review, reflection, next prompt | compact_continue |

## User Review Required

**Carried rulings:**
- D-158 (USER_EXPLICIT 2026-10-29 "all recommendations are accepted", grouping §8 `:141`) accepts the synthesis that 09 §Style and tool flow encodes (A-8, A-9, A-10, A-12, A-13, B-12; C-4, C-6, C-12; D-2).
- D-159 (autonomous, Local Canon, `:142`) made one MEU per slice; MEU-105 is slice 6. D-713 now splits that slice in two. D-160 (autonomous, Local Canon, `:143`) is carried, because the decision probe returns it (`C:/Temp/av-kit/s71-plan-decision-probe.txt`).
- D-674 and D-675 (autonomous, grouping §9.8) set the session number and the crop rules. MEU-105 adds no mark type and no mark field, so D-675's crop rules are unchanged (AC-105.30).
- D-676 is Session 72's and D-677 was Session 69's. D-678 (Ctrl+C on the page key handler) sits beside the tool letters, which are now MEU-143's, so this session doesn't touch that handler.

**The split (D-713, human).** Mat ruled "A" (USER_EXPLICIT 2026-11-13 "A"). The do-nothing option, one session for all five rule rows, was not chosen.
- **This session, MEU-105:** the Colour row, the Tool style row, and the Modifiers row's Pixelate block-size scrub.
- **Session 71b, MEU-143 `gui-capture-tool-flow`:** the Lock row (on by default, persisted, a one-shot preference, the just-drawn mark stays selected, an armed press on the selected mark edits it), the Letters row (V A R H T X E C, the crop X cases, the field guard) and the rest of the Modifiers row (Shift, Alt, Shift+arrow 10 px).
- Rows 5 and 6 write the split into 09, the matrix, `meu-status.yaml` and the grouping (SPLIT_SPEC, SPLIT_MATRIX, SPLIT_STATUS, SPLIT_GROUPING). MEU-106 gains MEU-143 as a dependency, because its Ctrl+D is a page-scoped registry entry built on MEU-143's letters (§9.3 `:174`). MEU-107 stays on MEU-105 only: a step mark needs per-tool style, not letters (D-724).

**Band mismatch.** The grouping's §3 heading (`:87`) and tracker row 47 (`:125`) say P3; `.agent/context/meu-status.yaml:2748` says `band: P2`. This plan changes neither. MEU-143 copies the pair: P2 in `meu-status.yaml` and P3 in the grouping's new row 47b (D-725). The handoff names the mismatch.

**OpenAPI and MCP change (D-717).** The Session 71 prompt expected them to stay as they are, because tool style is never mark JSON. They change all the same, for the settings path, not for marks:
- `PUT /settings/capture` takes `SettingsPutIn` (`schemas/settings.py`), which forbids extra keys, so each style leaf has to be added there, and the committed OpenAPI snapshot changes with it (regenerated, never hand-edited).
- The MCP `avkit_settings` set schema is strict (`mcp-server/src/toolsets/settings.ts:153`, `:163`), and its get already returns every key the service holds. Without the new leaves, an agent would read the style keys and be refused when it wrote them back. `SETTINGS_SCHEMA` gains the leaves as well, so the resource describes what get returns.
- No mark schema, sidecar, bake, annotate body or capture action changes. The MCP audit baseline is keyed by tool, action and status, and no action is added, so the baseline doesn't change. `isolationKeys` (`scripts/audit/classify.ts:281`) collects only path-like string leaves, and none of the new leaves is path-like, so AC-141.16 and AC-68.8 stay as they are.

**Rulings at plan time.** One question goes to Mat through the HDP before the first plan dispatch: the plan review budget (D-726). The plan gate asks one more: the execution review budget and his words to execute (D-727).

**Gate flags.** At the gate Mat also sees, each with a recommendation and its do-nothing option:
- D-714: tool style lives in nine `capture` settings leaves, read and written through the existing settings path;
- D-719: a change with a mark selected restyles only that mark (today's Apply also set the shared colour), and a tool-style change is a preference, not an undo step;
- D-721: the Select tool with nothing selected shows no style controls (today it shows Color and Stroke, which then set the one shared style);
- the band mismatch above.

An AC or contract change during execution goes to Mat as a Decision Brief (S12). Its do-nothing option is "record it as a departure and keep the approved text".

**Plan review.** Round 1 (Codex, 9,956,487 tokens): `changes_required`, with F1 (High: two commits to one leaf could be stored out of order) and F2 (Medium: an integer of 401 digits reached `float()` and raised `OverflowError`). Both are fixed above: STYLE_STORE's write queue with AC-105.32, and STYLE_SETTINGS's integer range check with AC-105.3 and AC-105.4. Round 2 (Codex, 6,811,240 tokens): `changes_required`; F1 and F2 fixed, and a new F3 (High: the failure refetch could install the old style over a commit made while it was pending). F3 is fixed above: `capture-style-store.ts`'s shared `queryFn` keeps every style leaf a GET did not see committed, with two more schedules in AC-105.32. Round 2's notes are fixed too: the API refuses with 422, not 400 (AC-105.4 and the boundary inventory), and H1-6a counts 32 ACs. Mat added 7M to the plan review budget for round 3 (D-728). Round 3 (Codex, 7,562,519 tokens): `approved`, with F1, F2 and F3 fixed, both notes corrected and no new findings; the loop spent 24,330,246 of 27,000,000 tokens.

**Network.** Recommendation: none, because nothing here fetches. The do-nothing option is the same. There is no brief.

**Token estimate.** Calibrated against:
- Session 41 `gui-keyboard-palette` (registry chords): plan 32.5M over 3 rounds (`docs/execution/metrics.md:52`);
- Session 69 `capture-copy-image`: plan 12.8M in one round against a 10.5M budget, execution 9.8M in one round (`:77`);
- Session 70 `capture-text-multiline`: plan 8.6M in one round, execution 10.7M in one round (`:78`).

This session is one MEU across the settings service, the API schema, OpenAPI, the MCP settings toolset, a new UI model and hook, the toolbar, the viewport and the page, plus the split's records. After the split it is smaller than Session 41 and larger than Session 70:
- plan review: about 13M for round 1 and about 6.5M for one recheck (Session 58 RULE-4), so the plan loop asks Mat for about 20M; the 10.5M default would stop before a recheck;
- execution review: about 13M for round 1, so the Session 60 RULE-5 figure is about 33M (13M × 2 plus a 6.5M recheck).

**Word meanings.**
- A *style tool* is one of `arrow`, `box`, `highlight`, `text` and `pixelate`. It is the key of a tool's remembered style. The Redact tool in Pixelate mode is the `pixelate` style tool; Select, Smart eraser, Crop and Redact in Solid mode have none.
- A *tool style* is a style tool's remembered values: a colour for Arrow, Box, Highlight and Text, a stroke for Arrow and Box, a font size and a background for Text, and a block size for Pixelate.
- A *leaf* is one key in the `capture` settings namespace, such as `arrow_color`.
- *The fields* are the options row's controls: the colour well, the hex field, the named menu, Stroke, Size, Bg and its Clear, and Block size.
- A *commit* is the event that makes a change final: a named pick, Enter or blur in the hex field, the well's native `change` event, a scrub's release, Enter or blur in a number field, a Clear click. A *preview* is any change before its commit, such as the well's `input` events or a scrub drag.
- *One undo step* is one entry that Ctrl+Z (MEU-99) takes back.

## Proposed Changes

### Single-statement contracts

Each mechanism id below is one statement. A row cites the id; a test names the AC.

| Id | Statement | File |
|---|---|---|
| `STYLE_SETTINGS` | `SettingSpec` (`services/settings.py:33-42`) gains `pattern: str \| None = None`, which `_encode` applies with `re.fullmatch` to a string value, and `integer: bool = False`, which makes `_encode` refuse a number that is not an `int` (a `float`, even `3.0`) and then compare that `int` with `min_number` and `max_number` before any `float()` conversion, so an integer of any size outside the range is refused as out of range and never raises `OverflowError` (round 1 F2); a row without `integer` keeps today's path. Each refusal is today's `ValidationError` naming the key, never the value. `SETTINGS_KEY_TABLE` gains nine `capture` rows after `annotated_format`: `arrow_color`, `box_color`, `highlight_color` and `text_color`, each `SettingSpec("string", "#E0AF68", pattern=COLOR_HEX)`; `arrow_stroke` and `box_stroke`, each `SettingSpec("number", 3, min_number=1, max_number=100, integer=True)`; `text_font_size`, `SettingSpec("number", 16, min_number=1, max_number=400, integer=True)`; `text_bg_color`, `SettingSpec("string", "", pattern=COLOR_HEX_OR_EMPTY)`; and `pixelate_block_size`, `SettingSpec("number", 10, min_number=2, max_number=100, integer=True)`. `COLOR_HEX = "#[0-9A-Fa-f]{6}"` and `COLOR_HEX_OR_EMPTY = "(#[0-9A-Fa-f]{6})?"` (D-714, D-715, D-716) | `services/settings.py` |
| `STYLE_API` | `SettingsPutIn` (`schemas/settings.py`) gains the four colour leaves and `text_bg_color` as `str \| None = None`, and `arrow_stroke`, `box_stroke`, `text_font_size` and `pixelate_block_size` as `StrictInt \| None = None`, so the API refuses `3.0`, `true` and `"3"` with a 422 before the service sees them (`C:/Temp/av-kit/s71-pydantic-int-probe.txt`). The route (`routes/settings.py:34`) doesn't change. `openapi.committed.json` is regenerated with `tools/export_openapi.py`, never edited by hand (Session 69 RULE-2; D-717) | `schemas/settings.py`, `openapi.committed.json` |
| `STYLE_MCP` | `SETTINGS_SCHEMA.namespaces.capture` (`mcp-server/src/toolsets/settings.ts:67-75`) gains the nine leaves with their types and defaults, and `settingsLeaves` (`:93-140`) gains `z.string().optional()` for each colour leaf and `z.number().int().optional()` for each number leaf. No action, description or audit baseline changes (D-717) | `mcp-server/src/toolsets/settings.ts` |
| `STYLE_MODEL` | A new `capture-tool-style.ts` exports `type StyleTool = 'arrow' \| 'box' \| 'highlight' \| 'text' \| 'pixelate'`, `type ToolStyle = { color?: string; stroke?: number; fontSize?: number; textBg?: string; blockSize?: number }`, `type ToolStyles = Readonly<Record<StyleTool, ToolStyle>>`, `TOOL_STYLE_DEFAULTS: ToolStyles` (arrow and box `{ color: '#E0AF68', stroke: 3 }`, highlight `{ color: '#E0AF68' }`, text `{ color: '#E0AF68', fontSize: 16, textBg: '' }`, pixelate `{ blockSize: 10 }`), `TOOL_STYLE_LEAVES: Readonly<Record<StyleTool, Readonly<Partial<Record<keyof ToolStyle, string>>>>>` (the leaf for each field), `styleToolFor(tool: CaptureTool, mode: RedactMode): StyleTool \| null`, `styleToolOfMark(mark: Annotation): StyleTool \| null` and `readToolStyles(data: unknown): ToolStyles`. `styleToolFor` maps `arrow`, `box`, `highlight` and `text` to themselves, `redact` to `pixelate` under the Pixelate mode and to `null` under Solid, and `select`, `eraser` and `crop` to `null`, through an exhaustive `switch` that fails the type check on a new tool. `styleToolOfMark` maps `arrow` to `arrow`, `rect` to `box`, `highlight`, `text` and `pixelate` to themselves, and `redact` and `eraser` to `null`, the same way. `readToolStyles` reads each leaf on its own: a colour leaf is kept only when it fully matches `#` and six hex digits (`text_bg_color` also when it is empty), a number leaf only when it is an integer in its row's range, and any other value (missing, the wrong type, a lone surrogate, a control character, an empty colour, a float, out of range) falls back to that leaf's default alone. Colours are kept as read; the fields show them in upper case (`displayHex`) | `capture-tool-style.ts` (new) |
| `STYLE_STORE` | A new `useCaptureToolStyles()` reads `CAPTURE_SETTINGS_KEY` through the same query as `useCaptureSettings` (one cache entry, one GET) and returns `{ styles: ToolStyles, saveToolStyle(tool: StyleTool, patch: ToolStyle): void }`. A new module `capture-style-store.ts` holds the shared write state at module scope: a counter that goes up at every commit and every settled PUT, and `latest`, which keeps for each style leaf its last committed value, that commit's number and, once its PUT has succeeded, the counter at that moment. It exports `fetchCaptureSettings()`, which becomes the `queryFn` of `CAPTURE_SETTINGS_KEY` in both hooks: it reads the counter when its GET starts and, when the response arrives, replaces each style leaf whose `latest` entry had not succeeded by then with that entry's value; other keys pass through as sent. So no GET, whether a window refocus, the Settings card's save or the failure refetch, can install a style older than a commit it did not see (round 2 F3). It also exports `resetCaptureStyleStore()`, which empties that state for tests. `saveToolStyle` maps the patch to its leaves through `TOOL_STYLE_LEAVES`, parses that body with `captureStylePutSchema` (a strict partial `zod` object of the nine leaves in `settings-schemas.ts`), records each leaf in `latest`, merges them into the cached data at once (`setQueryData`), and queues one `PUT /settings/capture` with only those leaves. The queue is one promise chain at module scope, shared by every caller: each PUT starts only after the one before it settles, success or failure, so the server applies style writes in commit order and the last successful commit to a leaf is the one stored (round 1 F1). A success marks each of its leaves' entries that still hold this commit as succeeded. A failure sets the page status to `Couldn't save the tool style`, which names no value, deletes each of its leaves' entries that still hold this commit, so the next GET shows the stored value, and marks the queue failed; when the last queued PUT settles with the queue marked failed, the hook invalidates the query once and clears the mark. `capturePutSchema` and the Settings card's 7-key form don't change; its query only gains the shared `queryFn` (D-720) | `capture-style-store.ts` (new), `useCaptureToolStyles.ts` (new), `useCaptureSettings.ts`, `settings-schemas.ts` |
| `STYLE_DISPLAY` | With a mark selected, the fields show that mark's values (today's `inspectMark`, `CapturePage.tsx:1080`). With none selected, they show `styles[styleToolFor(tool, redactMode)]`, loaded again whenever the tool, the Redact mode, the selection or the loaded styles change; a field that holds invalid text keeps it until its commit or a tool change. A field the style tool has no value for keeps its group hidden, as `optionGroups` already decides | `CapturePage.tsx` |
| `STYLE_TARGET` | A commit with a mark selected restyles only that mark, as one undo step, and leaves every tool style as it is: `applyColor` no longer sets the shared colour. A commit with no mark selected and a style tool active calls `saveToolStyle` for that tool and field, and writes no undo step. A preview never calls `saveToolStyle`. A commit whose value equals the current one does nothing (D-719) | `CapturePage.tsx` |
| `STYLE_DRAW` | `createDrawnMark` (`CapturePage.tsx:282`) takes its colour, stroke, font size, background and block size from `styles[styleToolFor(tool, redactMode)]`, not from the fields, so a field holding invalid text never reaches a new mark. A solid redact and an eraser draw as today | `CapturePage.tsx` |
| `COLOR_NAMED` | The named menu (`capture-named-color`) commits on pick and then shows `Named` again (a controlled `value=""`). `namedPreview` goes | `CaptureViewport.tsx`, `CapturePage.tsx` |
| `COLOR_HEX` | The hex field (`capture-color`) holds its own text while typing and commits on Enter or blur when `normalizeHex` accepts the text. Text it refuses (including a lone surrogate, a control character and empty text) commits nothing and blocks nothing: Save, a tool change and the other fields work, and on blur or Escape the field shows the current colour again | `CaptureViewport.tsx`, `CapturePage.tsx` |
| `COLOR_WELL` | The colour well (`capture-color-well`) previews on each native `input` event (`onInput`): the selected mark's colour changes on screen with no undo step, or, with none selected, the fields show the colour with no PUT. A native `change` listener, added through a ref, commits once: one undo step for a mark, one `saveToolStyle` for a tool. Its React `onChange` is a no-op kept for the controlled-input rule, because React's `onChange` fires on `input` events too | `CaptureViewport.tsx`, `CapturePage.tsx` |
| `TEXT_BG_WELL` | The text background well (`capture-text-bg`) follows COLOR_WELL: previews on `input`, commits once on the native `change`. Clear (`capture-text-bg-clear`) is one commit. `changeTextBg` no longer writes a step per call | `CaptureViewport.tsx`, `CapturePage.tsx` |
| `COLOR_GATE_GONE` | `colorDirty`, `colorBaseline`, `candidate`, `applyEnabled`, `applyColor`'s gate role, `cancelColor`, `COLOR_GATE_MESSAGE` and the Apply and Cancel buttons go, with the viewport's `colorApplyEnabled`, `colorCancelEnabled`, `onColorApply` and `onColorCancel` props. `chooseTool` and `canSave` lose their colour checks. `CAPTURE_COLOR_APPLY` and `CAPTURE_COLOR_CANCEL` stay in `test-ids.ts`, whose hashed prefix holds them (`:228-229`) | `CapturePage.tsx`, `CaptureViewport.tsx` |
| `TEXT_DRAFT_STYLE` | While a new text draft is open, a colour, size or background commit sets the `text` tool style and the draft shows it at once; the committed mark takes it. While a saved text mark is re-edited (MEU-101), the commit restyles that mark instead, as one undo step (Session 55 RULE-1 names the text tool as a caller) | `CapturePage.tsx` |
| `BLOCK_SCRUB` | `CaptureScrubFieldProps` gains `min?: number`, defaulting to `SCRUB_MIN`, which `clampScrub` uses in place of `SCRUB_MIN`. Block size becomes `<CaptureScrubField id="capture-block-size" label="Block size" ariaLabel="Block size" min={PIXELATE_BLOCK_MIN} max={PIXELATE_BLOCK_MAX} …>`, so the input keeps the id `capture-block-size` and the handle is `capture-block-size-scrub`. `SizeBurst.field` gains `'block'`, so a drag on a selected pixelate is one undo step and Escape restores it, as Stroke and Size do today (MEU-85). `test-ids.ts` appends `// MEU-105 Capture style (additive IDs).` and `CAPTURE_BLOCK_SIZE_SCRUB = 'capture-block-size-scrub'` after the MEU-102 block (D-722) | `CaptureScrubField.tsx`, `CaptureViewport.tsx`, `CapturePage.tsx`, `test-ids.ts` |
| `SELECT_NO_STYLE` | `optionGroups('select', null, mode)` returns `[]`: with Select and nothing selected there is no tool whose style a control could set. Every other case is unchanged (D-721) | `capture-toolbar.ts` |
| `STYLE_HELP` | The Annotation tools help body (`capture-help-content.ts:27`) drops `; Apply commits color` (the sentence ends after `tabbed to`), changes `Drag the Stroke or Size label` to `Drag the Stroke, Size or Block size label`, and adds, after the Smart eraser sentence: `A swatch applies when you pick it, and a typed hex colour applies on Enter. With a mark selected, a style control changes only that mark; with none selected, it sets the current tool's own colour and size, which Capture remembers.` No section is added | `capture-help-content.ts` |
| `STYLE_ACTIONS_INDEX` | `gui-actions-index.md` gains two rows after `capture:tool_lock` (`:91`): `capture:style_mark` (Color, Stroke, Size, Bg and Block size with a mark selected; local canvas) and `capture:style_tool` (the same controls with no mark selected, saved per tool; `PUT /settings/capture`) | `gui-actions-index.md` |
| `SPLIT_SPEC` | 09's §Style and tool flow header note (`:974`) names the split: MEU-105 holds the Colour and Tool style rows and the Modifiers row's Pixelate scrub, and MEU-143 holds the Lock and Letters rows and the rest of Modifiers (D-713). The rule rows don't change. The MEU table gains `\| MEU-143 \| gui-capture-tool-flow \| [Style and tool flow](#style-and-tool-flow) \| MEU-87, MEU-99, MEU-100, MEU-105 \|` after its last row, MEU-136 (`:1308`), and the MEU-106 row's dependencies (`:1299`) gain MEU-143. The two "C arrives with MEU-105" sentences (`:1096`, `:1107`) say MEU-143. A `> **Delivered (Session 71).**` note follows the rule table (`:980`), before `<a id="line-and-ellipse"></a>` (`:982`) | `09-screenshot-capture.md` |
| `SPLIT_MATRIX` | The matrix gains row `9.31a` (`MEU-143`, `gui-capture-tool-flow`, the same 09 link, `MEU-87, MEU-99, MEU-100, MEU-105`) after row 9.31 (`:129`), in the `6.2a` shape (`:63`). Row 9.32's dependencies gain MEU-143. The P2 band line (`:15`) reads `MEU-14–143` | `build-priority-matrix.md` |
| `SPLIT_STATUS` | `meu-status.yaml` gains a MEU-143 entry after MEU-142, by hand: `band: P2`, `matrix_item: '9.31a'`, the 09 anchor, status `pending`, depends on MEU-87, MEU-99, MEU-100 and MEU-105. MEU-105's `description` names only its half. MEU-106's `depends_on` and `dependencies_raw` gain MEU-143. The P2 `summary_bands` range reads `MEU-14–143` and appends `; 2026-11-13 capture style split MEU-143`. `meu_status.py render` then writes `meu-registry.md` and `docs/BUILD_PLAN.md` | `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` |
| `SPLIT_GROUPING` | Grouping §6 row 47 gains the note `(style half; MEU-143 split out by D-713)`, a row `47b` follows it (`capture-tool-flow`, MEU-143, P3, `pending`, `—`), and a new §9.9 states D-713: the §9.3 bullets on letters, X, Ctrl+D, Ctrl+C and the Shift constants are now MEU-143's, and only the Pixelate scrub bullet stays MEU-105's | grouping file |

### Pins that move

The plan-time sweep (`C:/Temp/av-kit/s71/pin-sweep.txt`) read every caller and pin of `optionGroups`, the Apply and Cancel test ids, `COLOR_GATE_MESSAGE` and its text, the Apply/Cancel props, `capture-block-size`, the help sentences and the capture settings keys. Row 2 moves the two key-set pins (AC-36.12 and AC-38.6) and row 3 (Red) moves the rest, so Green changes no test file (S2):

| Pin | File and line | Ending | Change |
|---|---|---|---|
| AC-60.8 (Apply writes, Cancel writes nothing) | `ui/tests/unit/capture-page.behavior.test.ts:690-710` | CRLF | the hex field commits on Enter, the well commits on `change`, and there is no Cancel |
| AC-60.8 (the gate status) | `:1085-1093` | CRLF | Save stays on with invalid hex text, and the status never reads `Apply or Cancel color` |
| AC-60.8 (Apply off until the candidate differs) | `:1128-1150` | CRLF | the named pick paints the mark at once |
| AC-60.13 (the Select tool shows Apply and Cancel) | `:818-819` | CRLF | asserts the buttons are absent |
| MEU65_OPTION_IDS | `:1471-1477` | CRLF | the colour group is `capture-color-well`, `capture-color`, `capture-named-color` |
| AC-81.4 (the colour group's ids, in order) | `ui/tests/unit/capture-action-row.test.ts:490` | CRLF | the same three ids, in that order (Session 59 RULE-1) |
| The help sentence | `capture-action-row.test.ts:68`, `ui/tests/unit/capture-help-content.test.ts:9` | CRLF | ends after `tabbed to.` |
| AC-85.11 (the scrub sentence) | `capture-help-content.test.ts:77` | CRLF | names Block size |
| AC-65.1 (the expected table) | `ui/tests/unit/capture-toolbar.test.ts:55-67`, `:108-128` | CRLF | `select` with nothing selected gives `[]`; the `regionCase` colour rule counts it |
| The select-shows-stroke line | `capture-toolbar.test.ts:138` | CRLF | `optionGroups('select', null)` equals `[]` |
| AC-60.12 (typed hex, Apply) | `ui/tests/e2e/capture-inbox.test.ts:600-602` | LF | presses Enter in the hex field instead of clicking Apply |
| AC-36.12 (the capture key set) | `tests/unit/test_capture_service.py:20-36`, `:400-420` | CRLF | `CAPTURE_KEYS` and `CAPTURE_DEFAULTS` gain the nine leaves |
| AC-38.6 (the MCP capture keys) | `mcp-server/tests/capture.test.ts:45-63`, `:194-206` | CRLF | the same nine leaves and defaults |

These were read and hold:
- `ui/tests/unit/capture-crop-tool.behavior.test.ts:903` (crop gives `[]`) and AC-103.17 (`capture-redact.behavior.test.ts:319-345`, no select-with-nothing row).
- AC-37.13 (`tests/e2e/test_api_captures.py:743`) reads a fake that holds only today's seven keys.
- The MEU-67 subset checks (`tests/e2e/test_api_capture_flatten.py:131-136`, `:508`) use `<=` and `in`.
- AC-39.4 (`capture-page.behavior.test.ts:372`), AC-57.1 (`:1196`) and the Electron card test (`capture-inbox.test.ts:691-697`) count PUTs only around card edits, where no style changes.
- The block group in MEU65_OPTION_IDS (`capture-page.behavior.test.ts:1480`), the block field reads (`:1641`) and AC-103.x (`capture-redact.behavior.test.ts:307`) read the input by its id, which BLOCK_SCRUB keeps.

Before writing, row 1 sweeps `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` again for these names and for the literal text this plan rewrites (`Apply or Cancel color`, `Apply commits color`, `Drag the Stroke or Size label`, `>Apply<`, `>Cancel<`), and for exact-signature pins of `SettingSpec(`, `CaptureScrubFieldProps`, `optionGroups(` and the viewport's colour props. It records the hits with each file's ending in `s71-anchors.txt` (Session 55 RULE-1, Session 59 RULE-1, Session 62 RULE-4, Session 63 RULE-1, Session 66 RULE-1, Session 68 RULE-2). A pin found then and missing here goes into the handoff as a departure.

**Enum-keyed maps (Session 68 RULE-1).** `StyleTool` is new, so each map keyed by it gets every entry in row 1: `TOOL_STYLE_DEFAULTS` and `TOOL_STYLE_LEAVES`. `styleToolFor` and `styleToolOfMark` switch over `CaptureTool` and `Annotation['type']` with `assertNever`, so a new tool or mark type fails the type check there.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers | Rule |
|---|---|---|---|
| A tool's style | `saveToolStyle` (a commit with nothing selected), an agent's `avkit_settings` set, the Settings API | `SettingsPutIn`, `SettingsService._encode`, the app database, `get_namespace`, `readToolStyles`, `STYLE_DISPLAY`, `STYLE_DRAW` | refused at the API (`StrictInt`, extra keys) and the service (`pattern`, `integer`, range); read back leaf by leaf with a fallback (AC-105.7); no error, status line or Console line names the value (S6) |
| A mark's colour, stroke, font size, background, block size | a commit with that mark selected | the undo history, the save POST body, the sidecar, the bake | unchanged mark fields; no style key enters mark JSON (AC-105.30) |
| The hex field's text | the user's typing | `normalizeHex` at the commit | text it refuses applies nothing and is never sent (AC-105.9) |

These functions sit between the user's click and the port, and two traces cover them with recording fakes (Session 55 RULE-3):
- AC-105.20: one named pick with an arrow selected, through the viewport's `onNamedColor`, the page's commit, `annotationsRef.current` and `parseAnnotateBody`, to the recorded save POST body;
- AC-105.21: one hex commit with Arrow armed and nothing selected, through `saveToolStyle` and `captureStylePutSchema`, to the recorded `PUT /settings/capture` body `{ "arrow_color": "#12ABCD" }`, and then to the next drawn arrow's colour in the save body;
- AC-105.22 traces the Python half: the API body, `SettingsPutIn`, `SettingsService.set_namespace` (a recording wrapper), the stored value and the next GET.

### Spec text (D3)

| File | Change |
|---|---|
| `docs/build-plan/09-screenshot-capture.md` | SPLIT_SPEC, and a `> **Delivered (Session 71).**` note after the §Style and tool flow rule table (`:980`) naming the mechanism ids, AC-105.1 to AC-105.32, that Lock, Letters and the other modifiers are MEU-143's, and the plan folder. The rule rows don't change |
| `docs/build-plan/gui-actions-index.md` | STYLE_ACTIONS_INDEX |

### MEU-105 `gui-capture-style-tool-flow`

**Boundary inventory.**

| Boundary | Input | Refusal |
|---|---|---|
| API `PUT /settings/capture` | the nine style leaves | `SettingsPutIn` gives 422 for an extra key, a non-string colour and a number that is not a strict `int`; the service gives today's `ValidationError`, which `DOMAIN_HTTP_MAP` (`packages/api/src/avkit_api/errors.py:29`) answers with 422, for a colour that doesn't match its pattern, an out-of-range number and a cookie-shaped value, naming the key only; an integer of any size outside its range gets that 422 too, never a 500 (STYLE_SETTINGS) |
| MCP `avkit_settings` set, namespace `capture` | the same leaves | the strict input schema refuses an unknown key, a non-string colour, a float and a bool; the API then applies its own rules |
| Settings read-back | the stored values, which another writer or a hand edit of the database can change | `readToolStyles` falls back leaf by leaf (AC-105.7) |
| GUI | the fields | not a trust boundary; the server refuses what the client lets through |

**Input matrix (Session 64 RULE-1).** The prompt's matrix (each letter × crop open or closed × a field focused or not, and each modifier × each bounded tool) belongs to MEU-143 after the split. This session's matrix is each style control × whether a mark is selected × the active tool and mode:

| Control | Mark selected | Arrow / Box armed | Highlight armed | Text armed (no draft / new draft / re-edit) | Redact Pixelate armed | Select, Eraser, Crop, Redact Solid, nothing selected |
|---|---|---|---|---|---|---|
| Colour (named, hex, well) | restyles the mark, one step | sets `arrow_color` or `box_color` | sets `highlight_color` | sets `text_color` / sets `text_color` and the draft / restyles the mark | hidden | hidden |
| Stroke | restyles an arrow or box | sets `arrow_stroke` or `box_stroke` | hidden | hidden | hidden | hidden |
| Size, Bg, Clear | restyle a text mark | hidden | hidden | set `text_font_size` or `text_bg_color` / the same and the draft / restyle the mark | hidden | hidden |
| Block size | restyles a pixelate | hidden | hidden | hidden | sets `pixelate_block_size` | hidden |

The "hidden" cells are what `optionGroups` decides today, except Select with nothing selected (SELECT_NO_STYLE). A selected mark's groups follow the mark, as today: an arrow selected while Text is armed shows Color and Stroke, and restyles the arrow.

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-105.1 | type | The exact signatures: `SettingSpec`'s `pattern: str \| None = None` and `integer: bool = False`; `StyleTool`, `ToolStyle`, `ToolStyles`, `TOOL_STYLE_DEFAULTS`, `TOOL_STYLE_LEAVES`, `styleToolFor(tool: CaptureTool, mode: RedactMode): StyleTool \| null`, `styleToolOfMark(mark: Annotation): StyleTool \| null`, `readToolStyles(data: unknown): ToolStyles`; `useCaptureToolStyles()`; `fetchCaptureSettings(): Promise<CapturePut>` and `resetCaptureStyleStore(): void`; `CaptureScrubFieldProps.min?: number`; `CAPTURE_BLOCK_SIZE_SCRUB === 'capture-block-size-scrub'` (Session 66 RULE-1) | Local Canon: D-714 | passes where row 3 writes it (row 1 adds the names) |
| AC-105.2 | behaviour | STYLE_SETTINGS: `SETTINGS_KEY_TABLE` holds the nine `capture` rows with their defaults, and `get_namespace("capture")` returns them on a fresh store, one parametrize id per leaf | Spec: 09 Tool style row; Local Canon: D-715, D-716 | a fresh store's `arrow_stroke` is the `int` 3, not `3.0` |
| AC-105.3 | behaviour | `_encode` refuses `#12ABC`, `12ABCD`, `#12ABCDE`, `red` and an empty string for a colour leaf, accepts an empty `text_bg_color`, refuses `3.5`, `3.0`, `True`, 0 and 101 for `arrow_stroke` and 1 and 101 for `pixelate_block_size`, refuses `10**400` for `arrow_stroke` with `ValidationError`, not `OverflowError`, and each `ValidationError` message holds the key and not the value | Local Canon: D-714 | `3.0` is refused |
| AC-105.4 | behaviour | STYLE_API: `PUT /settings/capture` with the nine leaves gives 200 and a GET returns them; `3.0`, `true` and `"3"` for a number leaf and `5` for a colour leaf give 422; `#GGGGGG` gives 422; `10**400` for `arrow_stroke` gives 422, not 500; an unknown key gives 422; no response body echoes a refused value; the OpenAPI document equals the regenerated committed snapshot | Local Canon: D-717 | the `"3"` case |
| AC-105.5 | behaviour | STYLE_MCP: `SETTINGS_SCHEMA.namespaces.capture` lists today's seven keys and the nine leaves with their defaults; the set schema accepts `{ namespace: "capture", arrow_color: "#12ABCD", arrow_stroke: 5 }` and refuses `arrow_stroke: 2.5`, `arrow_stroke: true` and `arrow_color: 5`; the tool's actions are unchanged | Local Canon: D-717 | the float case |
| AC-105.6 | behaviour | STYLE_MODEL: `styleToolFor` gives the table above for every `CaptureTool` × `RedactMode`, and `styleToolOfMark` gives it for every mark type, one assertion per pair; `TOOL_STYLE_DEFAULTS` and `TOOL_STYLE_LEAVES` have an entry for every `StyleTool` | Spec: 09 Tool style row; Local Canon: D-715 | Redact Solid gives `null` |
| AC-105.7 | behaviour | `readToolStyles` keeps each valid leaf and replaces only the bad one with its default: a missing leaf, a number for a colour, `#12ABC`, an empty `arrow_color`, a lone surrogate (`'#12AB\uD800'`), a control character (`'#12AB\u0007D'`), `2.5`, `0` and `101` for `arrow_stroke`, and `1` for `pixelate_block_size`; an empty `text_bg_color` is kept; `undefined` and `null` give `TOOL_STYLE_DEFAULTS` (Session 53 RULE-1) | Local Canon: D-716 | the lone-surrogate case keeps the other leaves |
| AC-105.8 | behaviour | COLOR_NAMED: with an arrow selected, picking `orange` in the named menu paints it `#FFA500` at once, as one undo step: Ctrl+Z gives back the old colour; the menu shows `Named` again; no element with the id `capture-color-apply` or `capture-color-cancel` exists | Spec: 09 Colour row | Ctrl+Z restores the old colour |
| AC-105.9 | behaviour | COLOR_HEX: with an arrow selected, typing `#12abcd` changes nothing until Enter, and Enter paints `#12ABCD` as one step; the same on blur; `#12abc`, empty text, a lone surrogate and a control character paint nothing, leave Save on and the tool buttons working, and blur shows the current colour again; Escape restores it too (Session 53 RULE-1) | Spec: 09 Colour row | the invalid cases |
| AC-105.10 | behaviour | COLOR_WELL: with an arrow selected, three `input` events on the well show each colour on the mark and add no undo step, and one `change` event adds exactly one; a `change` whose colour equals the mark's adds none | Spec: 09 Colour row (one click or scrub is one undo step) | the equal-colour case |
| AC-105.11 | behaviour | TEXT_BG_WELL: with a text mark selected, three `input` events and one `change` on the Bg well add exactly one undo step, and Clear adds one more | Spec: 09 Colour row | today's per-event steps (fails at Red) |
| AC-105.12 | behaviour | STYLE_TARGET: with one of two arrows selected, a colour commit and a stroke commit restyle only that arrow, send no `PUT /settings/capture`, and the next drawn arrow still has the arrow tool's style | Spec: 09 Tool style row; Local Canon: D-719 | the other arrow is unchanged |
| AC-105.13 | behaviour | With Arrow armed and nothing selected, a hex commit sends one PUT whose body is exactly `{ arrow_color }`, a Stroke drag sends one PUT at its release whose body is exactly `{ arrow_stroke }`, no undo step is written, and the box, highlight, text and pixelate styles are unchanged | Spec: 09 Tool style row; Local Canon: D-719, D-720 | the drag's previews send no PUT |
| AC-105.14 | behaviour | STYLE_DRAW: after setting a different style on each of Arrow, Box, Highlight, Text and Pixelate, each newly drawn mark carries its own tool's style and none of the others' | Spec: 09 Tool style row | a box drawn after the arrow change keeps the box colour |
| AC-105.15 | behaviour | STYLE_DISPLAY: switching from Arrow to Box to Text shows each tool's style in the fields; selecting a mark shows the mark's values; clearing the selection shows the tool's again | Spec: 09 Tool style row | — |
| AC-105.16 | behaviour | A page mounted on a GET that holds `arrow_color: '#123456'` and `arrow_stroke: 7` shows them with Arrow armed and draws an arrow with them; a GET with `arrow_color: 'nope'` shows `#E0AF68` (the preference is read back from disk, Session 53 RULE-1) | Spec: 09 Tool style row (app preference) | the `nope` case |
| AC-105.17 | behaviour | TEXT_DRAFT_STYLE: in a new text draft, a colour commit sends one PUT `{ text_color }`, the draft shows the colour, and the committed mark has it; re-editing a saved text mark, a colour commit restyles that mark as one step and sends no PUT | Spec: 09 Tool style row; Session 55 RULE-1 | the re-edit sends no PUT |
| AC-105.18 | behaviour | BLOCK_SCRUB: `capture-block-size-scrub` exists in the block group; a drag on it with a pixelate selected is one undo step and clamps to 2 and 100; Escape mid-drag restores the old size; with Redact in Pixelate mode and nothing selected, one drag sends one PUT `{ pixelate_block_size }` | Spec: 09 Modifiers row (B-12); Local Canon: D-722 | the clamp at 2 |
| AC-105.19 | behaviour | SELECT_NO_STYLE: `optionGroups('select', null, mode)` is `[]` for both modes, and the page with Select armed and nothing selected shows none of the style fields | Local Canon: D-721 | `optionGroups('select', arrow)` is still `['color', 'stroke']` |
| AC-105.20 | behaviour | One named pick traced with recording fakes from the viewport's `onNamedColor` through the page's commit and `annotationsRef.current` to the recorded save POST body, whose arrow colour is `#FFA500` and which holds the arrow exactly once | Session 55 RULE-3 | the body holds the mark once |
| AC-105.21 | behaviour | One hex commit with Arrow armed traced through `saveToolStyle` and `captureStylePutSchema` to the recorded PUT body `{ "arrow_color": "#12ABCD" }`, then to the next drawn arrow's colour in the save POST body | Session 55 RULE-3 | exactly one PUT |
| AC-105.22 | behaviour | One API body `{ "arrow_color": "#12ABCD", "arrow_stroke": 5 }` traced through `SettingsPutIn`, `SettingsService.set_namespace` (a recording wrapper), the stored values and the next GET | Session 55 RULE-3 | the wrapper records one call |
| AC-105.23 | behaviour | The Settings card: after a style PUT, the Capture card's unsaved edit stays, and its Save sends a body with exactly today's seven keys; a GET after it still returns the style leaves | Session 55 RULE-1 (the settings store's callers) | the card body has no style key |
| AC-105.24 | behaviour | STYLE_HELP: the Annotation tools body holds the new sentence exactly, holds `Drag the Stroke, Size or Block size label`, and doesn't hold `Apply commits color` | Spec: 09 Colour and Tool style rows | the old sentence is absent |
| AC-105.25 | check | STYLE_ACTIONS_INDEX: `capture:style_mark` and `capture:style_tool` follow `capture:tool_lock`, in that order; `gui-actions-audit.test.ts` passes | Local Canon: GUI actions index | row 5's check exits 1 before row 5 |
| AC-105.26 | behaviour | Electron: with an arrow selected, picking `orange` in the named menu repaints it with no Apply button on the page, and Save posts `#FFA500`; with Arrow armed and nothing selected, a hex Enter sends one `PUT /settings/capture` holding `arrow_color`, and the next drawn arrow has that colour | Spec: 09 Colour and Tool style rows | the Apply button has count 0 |
| AC-105.27 | guard | The Redact mode is not saved (D-680): a mode change sends no PUT; a solid redact and an eraser draw as today; the crop shows no style group | Local Canon: D-680 | — |
| AC-105.28 | guard | MEU-85's Stroke and Size scrubs (one step per gesture, Escape restores) and MEU-99's Ctrl+Z and Ctrl+Y pass unchanged | Local Canon: MEU-85, MEU-99 | — |
| AC-105.29 | check | The split records: 09's header note, MEU table row and the two MEU-143 sentences; matrix row 9.31a and the band line; the MEU-143 entry, MEU-106's dependency and the P2 band in `meu-status.yaml`; grouping row 47b and §9.9; `meu_status.py render --check` passes; 09, the matrix and the grouping keep CRLF and `meu-status.yaml` LF | Human-approved: D-713 | row 6's check exits 1 before row 6 |
| AC-105.30 | guard | No style key enters mark JSON: after a style commit, the save POST body's marks hold exactly today's keys for their type, and `AnnotateIn`, the sidecar and the bake are unchanged; `clip_mark` (D-675) is unchanged | Spec: 09 Tool style row (never mark JSON); Local Canon: D-675 | — |
| AC-105.31 | behaviour | A failed style PUT (500) shows `Couldn't save the tool style` in the status, names no value there or on the Console, and refetches once the style queue is empty, so the fields show the stored style again | Session 50 RULE-1; Local Canon: D-720 | the status names no value |
| AC-105.32 | behaviour | STYLE_STORE's queue: with Arrow armed and nothing selected, two `arrow_color` commits made while the fake server holds the first PUT pending send the second PUT only after the first settles; the fake receives the two bodies in commit order; the fields show the second colour throughout; after both settle the fake's stored value is the second colour and a remounted page shows it. With the first PUT failing (500) while the second is held, no GET is sent until the second settles, then exactly one, and the fields show the second colour. With the first PUT failing (500), the GET that follows held, a second commit made, the GET then answering with the old stored colour and the second PUT succeeding, the fields and the next drawn arrow show the second colour, and so does a later GET. With a PUT held, a refetch the test starts (it invalidates `CAPTURE_SETTINGS_KEY`) answering with the old colour leaves the fields on the new colour, before and after the PUT succeeds. Each test settles every held request and calls `resetCaptureStyleStore()` before the next | Review: plan round 1 F1, round 2 F3; Local Canon: D-720 | a second PUT sent before the first settles fails the test |

**Guards.** These pass after rows 1, 2 and 4:
- Python: `tests/unit/test_capture_service.py`, `tests/e2e/test_api_health_settings.py`, `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_flatten.py`, `tests/e2e/test_api_js_runtime.py` (it reads `SETTINGS_KEY_TABLE`) and `tests/e2e/test_api_openapi.py`. No row edits `packages/core/src/avkit_core/domain`;
- MCP: `mcp-server/tests/capture.test.ts`, `settings-runtime.test.ts`, `tools-parity.test.ts`, `action-index.test.ts` and the `tests/audit/` suite;
- UI: `capture-toolbar.test.ts`, `capture-page.behavior.test.ts`, `capture-action-row.test.ts`, `capture-help-content.test.ts`, `capture-redact.behavior.test.ts`, `capture-crop-tool.behavior.test.ts`, `capture-text-lines.behavior.test.ts`, `capture-page.test.ts`, `capture-flatten.test.ts`, `settings-path-fields.test.tsx` and `gui-actions-audit.test.ts`.

**Spec sufficiency.** Every MEU-105 rule has an AC:

| Rule | ACs |
|---|---|
| Colour | AC-105.8 to .11, .20, .24, .26 |
| Tool style | AC-105.2 to .7, .12 to .17, .19, .21 to .23, .27, .30 to .32 |
| Modifiers (Pixelate scrub only) | AC-105.18, .28 |
| The split | AC-105.29 |

Lock, Letters and the rest of Modifiers have no AC here; they are MEU-143's.

### Files Modified

The endings come from the plan-time check (`C:/Temp/av-kit/s71/pin-sweep.txt` and the Python byte count in this session); row 0 records them again, with SHA-256, in `s71-anchors.txt`.

| File | Endings | Rows |
|---|---|---|
| `packages/core/src/avkit_core/services/settings.py` (`STYLE_SETTINGS`) | CRLF | 1, 2 |
| `packages/api/src/avkit_api/schemas/settings.py` (`STYLE_API`) | CRLF | 2 |
| `openapi.committed.json` (regenerated) | as the generator writes | 2 |
| `mcp-server/src/toolsets/settings.ts` (`STYLE_MCP`) | CRLF | 2 |
| `ui/src/renderer/src/features/capture/capture-tool-style.ts` (new, `STYLE_MODEL`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/useCaptureToolStyles.ts` (new, `STYLE_STORE`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/capture-style-store.ts` (new, `STYLE_STORE`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/useCaptureSettings.ts` (`STYLE_STORE`'s shared `queryFn`) | CRLF | 4 |
| `ui/src/renderer/src/features/settings/settings-schemas.ts` (`captureStylePutSchema`) | CRLF | 4 |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` (`SELECT_NO_STYLE`) | CRLF | 4 |
| `ui/src/renderer/src/features/capture/CaptureScrubField.tsx` (`BLOCK_SCRUB`'s `min`) | CRLF | 1, 4 |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` (`COLOR_NAMED`, `COLOR_HEX`, `COLOR_WELL`, `TEXT_BG_WELL`, `COLOR_GATE_GONE`, `BLOCK_SCRUB`) | CRLF | 4 |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` (`STYLE_DISPLAY`, `STYLE_TARGET`, `STYLE_DRAW`, `COLOR_*`, `TEXT_DRAFT_STYLE`, `BLOCK_SCRUB`) | CRLF | 4 |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` (`STYLE_HELP`) | CRLF | 4 |
| `ui/tests/e2e/test-ids.ts` (the MEU-105 block, after the MEU-102 block) | CRLF | 1 |
| `ui/tests/unit/capture-page.behavior.test.ts`, `capture-action-row.test.ts`, `capture-help-content.test.ts`, `capture-toolbar.test.ts` (moved pins) | CRLF | 3 |
| `tests/unit/test_capture_service.py`, `mcp-server/tests/capture.test.ts` (moved pins; AC-105.5 appended to the MCP file) | CRLF | 2 |
| `ui/tests/e2e/capture-inbox.test.ts` (AC-60.12 moved; AC-105.26 appended) | LF | 3 |
| `tests/unit/test_capture_style_settings.py`, `tests/e2e/test_api_capture_style.py` (new; AC-105.2 to .4 and .22) | LF | 2 |
| `ui/tests/unit/capture-tool-style.test.ts`, `ui/tests/unit/capture-style-flow.behavior.test.ts` (new) | LF | 3 |
| `docs/build-plan/gui-actions-index.md` (`STYLE_ACTIONS_INDEX`) | CRLF | 5 |
| `docs/build-plan/09-screenshot-capture.md` (`SPLIT_SPEC`, the Delivered note) | CRLF | 5 |
| `docs/build-plan/build-priority-matrix.md` (`SPLIT_MATRIX`) | CRLF | 6 |
| `.agent/context/meu-status.yaml` (`SPLIT_STATUS`), and `meu-registry.md` and `docs/BUILD_PLAN.md` through `render` | LF | 6 |
| the grouping file (`SPLIT_GROUPING`, tracker row 47) | CRLF | 6 |

Before it writes, each row measures the file's endings with Python bytes, and then writes in that ending. A scratch script that edits a tracked file fails on mixed endings (Session 63 RULE-3), and every doc write ends with a check for lone CR and for a line ending that differs from the file's own (Session 70 RULE-5).

**Byte-hash guard (Session 50).** AC-51.6 and AC-81.13 hash `ui/tests/e2e/test-ids.ts` up to `// MEU-51 primitive harness IDs.` (`:292`). `CAPTURE_COLOR_APPLY` and `CAPTURE_COLOR_CANCEL` (`:228-229`) sit inside that prefix, so they stay, unused (COLOR_GATE_GONE). Row 1 appends the MEU-105 block after the MEU-102 block (`:516-517`), so the expected hash stays unchanged. Row 1 runs `ui/tests/unit/capture-action-row.test.ts` as its own check and names the hash it reads in the handoff. No row edits `layout-primitives`.

### Project files

These project files are written:
- `.agent/context/meu-status.yaml` (LF), `.agent/context/meu-registry.md` (LF) and `docs/BUILD_PLAN.md` (LF);
- the grouping file (CRLF; tracker row 47 at `:125`, §9.9 appended after `:206`);
- the handoff, the two rolling reviews and the reflection;
- `docs/execution/metrics.md` (CRLF) and `.agent/context/current-focus.md` (CRLF);
- this folder's plan, task and scripts.

## Out of Scope

| Item | Basis |
|---|---|
| Lock on by default, persisted, one-shot; the just-drawn mark staying selected; an armed press editing the selected mark | MEU-143 (D-713) |
| The letters V A R H T X E C, the crop X cases and the field guard | MEU-143 (D-713) |
| Shift aspect and 45-degree snaps, Alt from the centre, Shift+arrow 10 px | MEU-143 (D-713) |
| Saving the Redact mode | D-680 keeps it unsaved |
| A style for Select, Smart eraser, Crop or Solid redact | D-715 |
| Style controls on the Settings page | D-714: the toolbar is where a tool's style is set |
| Any mark type, mark field, sidecar or bake change | 09 Tool style row; AC-105.30 |
| The band mismatch between the grouping (P3) and `meu-status.yaml` (P2) | Session 71 prompt: named, not changed |
| Members-only URLs or ids, `npm run dist`, the live MCP audit | Session 71 prompt |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at baseline and after rows 6 and H2-2. MEU-105 is `pending`, with its dependencies MEU-87, MEU-99 and MEU-100 `approved` (`C:/Temp/av-kit/s71/queue-id-probe.txt`). Row 6 adds MEU-143 by hand and then runs `render` to write the two generated files.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. **Rulings (S9).** Checks that this plan's single `> **Status:**` line carries the budget and execute words, each with a `USER_EXPLICIT` quote, and stops if not.
2. **Queue (S8).** Checks that MEU-87, MEU-99 and MEU-100 are `approved`, that MEU-105 and MEU-106 are `pending`, that no MEU-143 entry exists yet, and that `5e9ea7c` is an ancestor of `HEAD`.
3. **Shapes (S7, Session 61 RULE-3).** Checks by name the shapes this plan relies on:
   - `SettingSpec`, its `allow_negative` field, `_encode`, the `annotated_format` row and `COOKIE_NEEDLES`;
   - `SettingsPutIn` and its `annotated_format` leaf;
   - `SETTINGS_SCHEMA`'s capture namespace and `settingsLeaves`' `annotated_format`;
   - `CAPTURE_SETTINGS_KEY`, `CaptureForm` and `capturePutSchema`;
   - `optionGroups` and its select-with-nothing stroke rule;
   - `COLOR_GATE_MESSAGE`, `colorDirty`, `applyColor`, `cancelColor`, `changeTextBg`, `inspectMark`, `createDrawnMark`, `SizeBurst` and `chooseTool` in `CapturePage.tsx`;
   - `capture-color-apply`, `capture-color-cancel`, `capture-named-color`, `capture-color-well`, `capture-text-bg` and `capture-block-size` in `CaptureViewport.tsx`;
   - `CaptureScrubFieldProps`, `SCRUB_MIN` and `clampScrub`;
   - the Annotation tools help sentence;
   - `capture:tool_lock` in the actions index;
   - the test-ids hash boundary and the MEU-102 block;
   - 09's anchor and the §Style and tool flow header note.

   It then checks that none of `StyleTool`, `TOOL_STYLE_DEFAULTS`, `TOOL_STYLE_LEAVES`, `styleToolFor`, `styleToolOfMark`, `readToolStyles`, `useCaptureToolStyles`, `saveToolStyle`, `fetchCaptureSettings`, `resetCaptureStyleStore`, `capture-style-store`, `captureStylePutSchema`, `arrow_color`, `box_stroke`, `text_font_size`, `pixelate_block_size`, `capture-block-size-scrub`, `CAPTURE_BLOCK_SIZE_SCRUB`, `capture:style_mark`, `capture:style_tool`, `Couldn't save the tool style`, `MEU-143` and `AC-105` appears in the target files, and that the seven new files don't exist.
4. **Records.** Creates `C:\Temp\av-kit\s71\tmp`. Records `baseline.sha`, `baseline-dirty.txt` (each dirty path's porcelain line and SHA-256) and `s71-anchors.txt` (every target's endings and SHA-256). It hashes `docs/proposals/2026-11-10-download-logic-divergence-report.md` and never opens it.
5. **Installs.** Installs from the lock with `uv sync --frozen --offline --all-packages` and proves that both `node_modules` trees match their locks (S4).
6. **FFmpeg pair.** Checks the pinned FFmpeg pair, as the identity script binds it.
7. **Base runs.** Captures the base Python, UI and MCP suites, the UI build, the capture Electron spec and `ruff check packages/ tests/`. These are recorded and are not fatal.
8. **Selftests.** Runs the `red-check.py`, `identity.py` and `id-length.py` selftests, each on its own fixtures (Session 56 RULE-4).

### 2. Type-only first, then data, then Red, then Green

**Row 1 (Session 53 RULE-2)** adds the names with no behaviour:
- `SettingSpec.pattern` and `SettingSpec.integer`, with their defaults, not yet read by `_encode`;
- `capture-tool-style.ts` with the types, both maps filled with every entry, and stubs: `styleToolFor` and `styleToolOfMark` return `null`, `readToolStyles` returns `TOOL_STYLE_DEFAULTS`;
- `useCaptureToolStyles.ts`, a stub that returns `TOOL_STYLE_DEFAULTS` and a `saveToolStyle` that does nothing, not yet called;
- `capture-style-store.ts`, a stub whose `fetchCaptureSettings` is today's plain GET with no overlay and whose `resetCaptureStyleStore` does nothing, not yet called;
- `CaptureScrubFieldProps.min?: number`, not yet read;
- `CAPTURE_BLOCK_SIZE_SCRUB` in `test-ids.ts`.

**Row 2 (data)** writes STYLE_SETTINGS's nine rows and `_encode`'s two checks, STYLE_API, the regenerated OpenAPI snapshot and STYLE_MCP. These are the data the Red tests read: so every key a Red test names exists before row 3 (Session 69 RULE-4), and the Python and MCP style tests that row 3 adds pass there as guards. The two key-set pins, AC-36.12 (`test_capture_service.py`) and AC-38.6 (`mcp-server/tests/capture.test.ts`), would fail on the new keys, so row 2 moves them with the data and adds AC-105.2 to .5 and .22, which have to pass there. Row 2 is not a Green row, so S2 doesn't apply to it. Row 3 moves the UI and Electron pins.

**Row 3 (Red)** edits the moved pins and requires only new-behaviour tests (Session 66 RULE-2):
- Vitest (UI): AC-105.6, .7, .8 to .21, .23, .24, .31 and .32 (AC-105.20 fails at Red because today a named pick needs Apply before the mark changes);
- Playwright: AC-105.26.

These are not in the Red list:
- AC-105.1 tests what rows 1 and 2 add, so it must pass where it is written.
- AC-105.2 to .5 and .22 test row 2's data and pass where they are written.
- AC-105.27, .28 and .30 are guards that pass throughout.
- AC-105.25 is row 5's check and AC-105.29 is row 6's.

**Red-check (Session 50).** A Red row passes only when `red-check.py` reads each receipt and names each failing required test as an assertion failure. A required test that fails on a missing name is refused (the `vitest-required-ac-105-6-stub-name` fixture). Every Red test:
- asserts that a name exists before it patches or calls it (Session 52 RULE-4);
- catches an exception and asserts its type (Session 62 RULE-3);
- asserts length or membership before indexing (Session 62 RULE-3);
- finds a mark by its content, never by DOM index (Session 70 RULE-1);
- states every click on the image in image pixels, inside the image after VIEW_MAP's rounding (Session 68 RULE-3);
- in Electron, asserts `await expect(locator).toBeVisible()` before it clicks.

`id-length.py` checks every new pytest id against red-check's header width of 71 characters (Session 67 RULE-4). Row 2 runs `ruff check` on the two new pytest files (Session 68 RULE-4).

**Rows 4 and 5 (Green)** change no test file. Row 4 writes the behaviour and STYLE_HELP, row 5 STYLE_ACTIONS_INDEX and 09's text, and row 6 the other split records.

**Where the tests go.**
- `tests/unit/test_capture_style_settings.py` (row 2): AC-105.1 (Python), .2 and .3.
- `tests/e2e/test_api_capture_style.py` (row 2): AC-105.4 and .22.
- `mcp-server/tests/capture.test.ts`, appended (row 2): AC-105.5.
- `ui/tests/unit/capture-tool-style.test.ts` (row 3): AC-105.1 (TS), .6, .7, .19's `optionGroups` half and .24.
- `ui/tests/unit/capture-style-flow.behavior.test.ts` (row 3): AC-105.8 to .18, .19's page half, .20, .21, .23, .27, .28, .30, .31 and .32, on its own render harness modelled on `capture-text-lines.behavior.test.ts`, with a recording fake server for the GET, the PUT and the save POST. The AC-105.28 and .30 guards drive today's paths, a Stroke scrub on a selected arrow and then Save, so they pass at Red.
- `ui/tests/e2e/capture-inbox.test.ts`, appended (row 3): AC-105.26.

### Plan-local scripts

The folder's `baseline.ps1`, `red-check.py`, `identity.py`, `id-length.py` and `session-gate.ps1` are adapted from Session 70's, with the `s71` names and this plan's paths.

| Script | What it does | Plan-time result |
|---|---|---|
| `id-length.py` | checks pytest id widths | selftest: 4 cases, 0 wrong (`C:/Temp/av-kit/s71-plan-idlen-selftest.txt`) |
| `red-check.py` | reads the Red receipts | selftest: 58 fixtures (18 positive, 40 negative), 0 wrong (`C:/Temp/av-kit/s71-plan-rc-selftest.txt`). It includes the AC-105.1 boundary against AC-105.10 to AC-105.19, AC-105.2 against AC-105.20, the stub-name refusal (a declared new name that isn't a function is refused too) and the AC-105.26 launch-failure refusal |
| `identity.py` | binds the tested state | selftest: 0 failures, 48 bound mutations detected (`C:/Temp/av-kit/s71-plan-identity-selftest.txt`) |
| `baseline.ps1` | row 0 | parses; its rulings, queue, shapes and anchors blocks ran alone (`C:/Temp/av-kit/s71-plan-shapes-dryrun.txt`): rulings fails as it should until the gate words are in (D-713 already reads as ruled), queue passes, every shape matches once and every absent name is absent, and all 25 targets are anchored |
| `session-gate.ps1` | H1-2 | parses; it runs nothing at plan time |

### Session gate (H1-2)

`session-gate.ps1` runs each step with its own receipt (`s71-D6-<id>.txt`) and exit code:

| Step | Command |
|---|---|
| Identity before | `identity.py` |
| Static | pyright, `ruff check packages/ tests/`, UI typecheck and lint, `lint_task_contract.py`, the scope-paths check (S3; the MCP audit baseline is refused), the `red-check.py` selftest, `id-length.py` on the two new pytest files |
| Byte-hash guard | `npm --prefix ui run test -- tests/unit/capture-action-row.test.ts` on its own |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s71\tmp`; only the Python ids that the base receipt shows failing are excused), `export_openapi.py --check` (equal to the snapshot row 2 regenerated), the whole UI suite and build, the MCP typecheck, build and suite, `meu_status.py render --check`, `issue_triage.py render --check` |
| Runtime | the capture Electron spec `ui/tests/e2e/capture-inbox.test.ts` (AC-105.26, AC-60.12) |
| Identity after | `identity.py`, which must equal the before value |
| Skipped with reason | `mcp-audit` (network and the installed servers), `build-record` (no release and no package build) |

The handoff copies this session's counts from the receipts (Session 63 RULE-2). The base counts are Python 2480, UI 1333 in 124 files, MCP 528 and Electron 49 (Session 70's gate); row 0 runs them again and the handoff copies them from the receipt.

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | A required Red test passes before its Green | fix the test; never weaken the Green |
| S2 | A Green row needs a test file change | stop; a moved pin goes into the handoff as a departure, and to Mat if it changes an AC (S12) |
| S3 | `HEAD` moves, or a path outside this plan and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path this plan doesn't write changes its SHA-256 | stop and ask Mat; never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` or a `node_modules` check fails at baseline | stop and ask Mat |
| S5 | A test or row reaches YouTube or the network, writes the system clipboard, or reads any user data (the capture inbox, its sidecars, the app database or Mat's settings file) | stop |
| S6 | A raw value (a refused colour or number, a user's path) reaches a log, stdout, a response body, the status line or the Console | fix it in the row or ask (Session 50 RULE-1) |
| S7 | A shape this plan relies on is missing, or a new name exists at baseline | stop and re-plan |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | The Status line lacks the budget or execute words | stop at row 0 |
| S10 | Codex is unavailable or the ledger refuses a round | Mat reviews |
| S11 | A status file is dirty from another session | copy it to `C:/Temp/av-kit/s71/pre-status/`, byte-edit only this session's fields, and prove them with `render --check` and a diff (Session 61 RULE-5) |
| S12 | A contract or AC in this plan needs to change | record a departure before the gate. One that changes an AC goes to Mat as a Decision Brief whose do-nothing option is "record it as a departure and keep the approved text" (Session 59 RULE-3) |
| S13 | A program other than this session's holds a resource that a row needs (a port, a file lock, a key such as ShareX's F2) | stop and ask Mat; never stop another program (Session 57 RULE-4) |

## Decision Log

> [!WARNING]
> D-713 records Mat's split ruling. D-714 to D-725 are autonomous, and each lists its alternatives in `reasoning`. D-726, D-727 and D-728 record Mat's budget rulings, and are filled in when he rules; D-728 came after D-727 was reserved, so it follows it. D-713 and up were free at plan time (`C:/Temp/av-kit/s71/id-probe.txt`; the only `D-71x` hits were Session 70's D-710 to D-712 and its prose naming D-716 as free).
>
> Carried, and not relisted in the block:
> - D-158: human, `USER_EXPLICIT 2026-10-29 "all recommendations are accepted"`, grouping §8 `:141`;
> - D-159: autonomous, Local Canon, `:142`;
> - D-160: autonomous, Local Canon, `:143` (the probe returns it);
> - D-674 and D-675: autonomous, stage `grouping`, §9.8.
>
> The reflection carries these and every id the decision probe returns (Session 54 RULE-5). The probe reads only the grouping's §8, so D-674 and D-675 (§9.8) are carried by hand.

```yaml
decision_log:
  - id: D-713
    stage: planning
    question: "Does MEU-105 split, and how?"
    resolution: human
    class: two-way
    chosen: "A: MEU-105 keeps the Colour row, the Tool style row and the Modifiers row's Pixelate scrub for Session 71; a new MEU-143 gui-capture-tool-flow takes the Lock row, the Letters row and the rest of the Modifiers row for Session 71b"
    recommendation: "Split as A, because the five rows were estimated above Session 41's three-round plan cost and the two halves touch different code: the style half the settings path and the options row, the flow half the registry and the pointer handlers"
    source_tag: Human-approved
    precedents:
      - ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md:89 - the split flag is candidate, six behaviours"
      - "docs/execution/metrics.md:52 - Session 41's registry chords plan took 32.5M over 3 rounds"
    research:
      engine: none
      sources: []
    reasoning: "Mat chose A through the HDP. The do-nothing option, one session for all five rows, was not chosen. A split is a scope change, so the session prompt sent it to Mat. Two-way: MEU-143 can be folded back before Session 71b plans."
    human_message_reference: "USER_EXPLICIT 2026-11-13 'A'"
  - id: D-714
    stage: planning
    question: "Where does a tool's style live?"
    resolution: autonomous
    class: two-way
    chosen: "Nine leaves in the capture settings namespace, through SETTINGS_KEY_TABLE, the Settings API and the MCP settings toolset, read by a hook that shares the capture settings query"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:980 - each tool remembers its own style as an app preference, never mark JSON"
      - "packages/core/src/avkit_core/services/settings.py:93-99 - the capture rows"
      - "ui/src/renderer/src/features/capture/useCaptureSettings.ts:13 - CAPTURE_SETTINGS_KEY"
    research:
      engine: none
      sources: []
    reasoning: "The existing settings path is the app's preference store, validated per key and readable by agents. One JSON string leaf lost: it hides every field from SettingSpec's checks and from the MCP schema. Browser storage lost: it is not an app preference, it lives only in one renderer profile, and an agent can't read it. Showing the leaves on the Settings page lost: the toolbar is where a style is set, and a second editor for the same values adds sync rules. Two-way."
    human_message_reference: null
  - id: D-715
    stage: planning
    question: "Which tools have a style, with which fields?"
    resolution: autonomous
    class: two-way
    chosen: "Arrow and Box: colour and stroke; Highlight: colour; Text: colour, font size and background; Pixelate (the Redact tool in Pixelate mode): block size. Select, Smart eraser, Crop and Solid redact have none"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-toolbar.ts:140-164 - optionGroups shows exactly these fields per tool"
      - "Session 68 D-680 - the Redact mode stays unsaved"
    research:
      engine: none
      sources: []
    reasoning: "A tool's style is what its options row shows, so the store mirrors optionGroups. A style for Solid redact or the eraser lost: they have no field to remember. Saving the Redact mode lost: D-680 keeps it unsaved, and a mode is a tool choice, not a style. Two-way."
    human_message_reference: null
  - id: D-716
    stage: planning
    question: "What are the defaults?"
    resolution: autonomous
    class: two-way
    chosen: "Today's single values for every tool: #E0AF68, stroke 3, font size 16, no background, block size 10"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:370-375 - today's starting values"
      - "packages/core/src/avkit_core/domain/capture.py:39 - PIXELATE_BLOCK_DEFAULT is 10"
    research:
      engine: none
      sources: []
    reasoning: "A fresh install draws exactly as today until the user changes a tool. Distinct colours per tool lost: they change what every existing user sees on the first mark with no request for it. Two-way."
    human_message_reference: null
  - id: D-717
    stage: planning
    question: "Do OpenAPI and MCP change?"
    resolution: autonomous
    class: two-way
    chosen: "Yes, for the settings path only: SettingsPutIn gains the nine leaves and the snapshot is regenerated; SETTINGS_SCHEMA and the strict set schema gain them; no mark schema, capture action or audit baseline changes"
    source_tag: Local Canon
    precedents:
      - "packages/api/src/avkit_api/schemas/settings.py - SettingsPutIn forbids extra keys"
      - "mcp-server/src/toolsets/settings.ts:153 - the set input is strict"
      - "scripts/audit/classify.ts:281 - isolationKeys takes only path-like leaves"
    research:
      engine: none
      sources: []
    reasoning: "The prompt expected no change because style is never mark JSON, and no mark-facing surface changes. The settings surfaces must change: the API refuses an unknown key, and the MCP set would refuse a key its get returns. Leaving MCP out lost: an agent would read leaves it can't write. Two-way."
    human_message_reference: null
  - id: D-718
    stage: planning
    question: "Which events commit a colour?"
    resolution: autonomous
    class: two-way
    chosen: "A named pick; Enter or blur in the hex field with valid text; the well's native change event, after input events that only preview; a commit equal to the current value does nothing; invalid hex text applies nothing, blocks nothing, and blur or Escape shows the current colour again"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:979 - swatches apply on click, the hex field on Enter or blur, one click or scrub is one undo step"
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:1091-1100 - the well calls onColor on both input and change"
    research:
      engine: none
      sources: []
    reasoning: "The picker fires input events while the user drags and one change when it closes, so committing on change gives one step per pick. React's onChange fires on input events too, so the commit needs the native change listener. Committing on every input lost: one drag would make dozens of undo steps. Two-way."
    human_message_reference: null
  - id: D-719
    stage: planning
    question: "What does a change restyle?"
    resolution: autonomous
    class: two-way
    chosen: "With a mark selected, only that mark, as one undo step, and no tool style changes; with none selected and a style tool active, that tool's style, as a preference write and no undo step"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:980 - with a mark selected a control restyles only that mark"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:1439 - applyColor sets the shared colour and the selected mark"
    research:
      engine: none
      sources: []
    reasoning: "The rule says only that mark, so today's double write goes. Undo covers marks on the open image (MEU-99), not preferences, so a tool change is not an undo step. Also setting the tool's style when a mark is restyled lost: the rule says only that mark. Two-way."
    human_message_reference: null
  - id: D-720
    stage: planning
    question: "When is a tool style written, and what if the write fails?"
    resolution: autonomous
    class: two-way
    chosen: "One PUT per commit holding only the changed leaves, sent one at a time in commit order through a queue every caller shares, the cache updated at once and every GET of the capture namespace keeping each style leaf a commit it did not see changed, nothing on a preview; a failure shows Couldn't save the tool style, names no value and refetches once the queue is empty"
    source_tag: Local Canon
    precedents:
      - "packages/api/src/avkit_api/routes/settings.py:34 - the PUT merges a partial body"
      - "ui/src/renderer/src/features/capture/useCaptureSettings.ts:89-97 - the card's save"
      - "ui/src/renderer/src/lib/query-client.ts:4 - staleTime 0, so a refocus refetches"
    research:
      engine: none
      sources: []
    reasoning: "A partial body can't overwrite another leaf, so two quick commits don't race on each other's keys. Writing the response into the cache lost: an older response could land after a newer optimistic value. A PUT per preview lost: a scrub drag would send dozens. Plan review round 1 F1: a partial body alone still let two commits to the same leaf race, so the older could be stored last while the screen showed the newer; the queue sends each PUT only after the one before it settles. Coalescing queued commits into one body lost: it breaks one PUT per commit for no gain at toolbar speed. Plan review round 2 F3: the failure refetch, and any refocus or card refetch, could still answer with a value older than a newer commit and replace it in the cache. Filtering in the shared query function fixes every such read at one place. Cancelling queries on each commit lost: it would also cancel the Settings card's refetch after its save. Two-way."
    human_message_reference: null
  - id: D-721
    stage: planning
    question: "What does the Select tool show with nothing selected?"
    resolution: autonomous
    class: two-way
    chosen: "No style controls"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-toolbar.ts:121 - select with nothing selected shows stroke today"
      - "ui/tests/unit/capture-toolbar.test.ts:138 - the pin that moves"
    research:
      engine: none
      sources: []
    reasoning: "With per-tool style, a control under Select with nothing selected has no tool to set. The do-nothing option, keep Color and Stroke there, lost: they would change nothing, which reads as broken. Making them set the last-used tool lost: the user can't see which tool that is. Flagged at the gate. Two-way."
    human_message_reference: null
  - id: D-722
    stage: planning
    question: "How does the Pixelate scrub work?"
    resolution: autonomous
    class: two-way
    chosen: "CaptureScrubField with a new optional min prop, min 2 and max 100, the input id capture-block-size kept, the handle capture-block-size-scrub, and a block burst in SizeBurst so a drag is one undo step"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CaptureScrubField.tsx:82 - clampScrub uses SCRUB_MIN"
      - ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md:176 - the scrub is owed"
    research:
      engine: none
      sources: []
    reasoning: "Reusing the scrub field gives the same drag, wheel, keys and undo as Stroke and Size. A separate block scrub lost: two scrub behaviours to keep alike. Keeping the input id keeps every existing pin. Two-way."
    human_message_reference: null
  - id: D-723
    stage: planning
    question: "What does a style change do while a text draft is open?"
    resolution: autonomous
    class: two-way
    chosen: "A new draft: it sets the text tool's style and the draft shows it; a re-edit of a saved mark: it restyles that mark as one undo step"
    source_tag: Local Canon
    precedents:
      - "Session 70 prompt - a per-tool colour or size change reaches the text draft and its hint"
      - "MEU-101 TEXT_REEDIT - a saved text mark opens in the draft"
    research:
      engine: none
      sources: []
    reasoning: "A new draft is not a mark yet, so the change is the text tool's; a re-edited mark is selected, so the change is the mark's, as D-719 says. Treating both as the mark lost: a new draft has no mark to restyle. Two-way."
    human_message_reference: null
  - id: D-724
    stage: planning
    question: "Which later MEUs depend on MEU-143?"
    resolution: autonomous
    class: two-way
    chosen: "MEU-106 gains MEU-143, because its Ctrl+D is a page-scoped registry entry beside the letters; MEU-107 stays on MEU-105 only, because a step mark needs a tool style, not letters"
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md:174 - Ctrl+D is a page-scoped registry entry"
      - "docs/build-plan/09-screenshot-capture.md:1006 - the step mark rows name no letter"
    research:
      engine: none
      sources: []
    reasoning: "A dependency should name what the later MEU builds on. MEU-107 on MEU-143 too lost: it would wait on letters it doesn't use. Two-way."
    human_message_reference: null
  - id: D-725
    stage: planning
    question: "Which band does MEU-143 take?"
    resolution: autonomous
    class: two-way
    chosen: "P2 in meu-status.yaml and P3 in the grouping's row 47b, the pair MEU-105 has"
    source_tag: Local Canon
    precedents:
      - "Session 71 prompt - name the mismatch and leave both as they are"
      - ".agent/context/meu-status.yaml:2748 - MEU-105 band P2"
    research:
      engine: none
      sources: []
    reasoning: "The split half keeps its parent's records, so the mismatch stays one mismatch for Mat to settle once. Choosing one band for MEU-143 lost: it would settle the mismatch for one MEU without Mat. Two-way."
    human_message_reference: null
  - id: D-726
    stage: planning
    question: "What is the plan review budget?"
    resolution: human
    class: two-way
    chosen: "About 20M: round 1 and one recheck"
    recommendation: "About 20M: the round 1 estimate of 13M plus a 6.5M recheck"
    source_tag: Human-approved
    precedents:
      - "tools/review_ledger.py:102 - the plan review default is 10.5M"
      - "Session 58 RULE-4 - a recheck is about half its first round"
    research:
      engine: none
      sources: []
    reasoning: "The do-nothing option is the 10.5M default, which stops before a recheck."
    human_message_reference: "USER_EXPLICIT 2026-11-13 'About 20M (Recommended)'"
  - id: D-727
    stage: planning
    question: "What is the execution review budget, and does execution start?"
    resolution: human
    class: two-way
    chosen: "An execution review budget of 33M with the default cap of 6, and execute now"
    recommendation: "An execution review budget of about 33M (the round 1 estimate of 13M twice plus a 6.5M recheck, Session 60 RULE-5) with the default cap of 6"
    source_tag: Human-approved
    precedents:
      - "Session 71 prompt - at the plan gate, ask for the execution budget"
      - "tools/review_ledger.py:102 - the execution review default is 21M"
      - "GUARDRAILS.md SIGN 3 - direct human execution authorization satisfies the plan-to-execution gate"
    research:
      engine: none
      sources: []
    reasoning: "The do-nothing options are the 21M default and not executing."
    human_message_reference: "USER_EXPLICIT 2026-11-14 '33M (Recommended)' and 'Execute now (Recommended)'"
  - id: D-728
    stage: planning
    question: "Round 3 needs more plan review budget than D-726 set. How much is added?"
    resolution: human
    class: two-way
    chosen: "Add 7M, so the plan review budget is 27M and round 3 can recheck F3"
    recommendation: "Add 7M: one recheck the size of round 2, which used 6,811,240 tokens"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s71-plan-ledger-continue.txt - the ledger continue by Mat, 16,767,727 of 27,000,000"
      - "Session 58 RULE-4 - a recheck is about half its first round"
    research:
      engine: none
      sources: []
    reasoning: "Round 2 left 3,232,273 tokens and the ledger reserves the last round's 6,811,240 before a round. Adding 4M, the minimum, lost: a long round 3 could pass it. The do-nothing option was to stop with the plan unapproved and F3's fix unchecked."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'Add 7M (Recommended)'"
```

## Research References

- No web research: every rule comes from 09, the grouping's §8 and §9, the code at `5e9ea7c` and the plan-time probes.

## Planning receipts

| Receipt | What it holds |
|---|---|
| `C:/Temp/av-kit/s71/id-probe.txt` | D-713 and up, the AC-105 and AC-143 families and MEU-143 were free |
| `C:/Temp/av-kit/s71/queue-id-probe.txt` | `HEAD` `5e9ea7c`; MEU-87, MEU-99 and MEU-100 `approved`; MEU-105 and MEU-106 `pending` |
| `C:/Temp/av-kit/s71/pin-sweep.txt` | the callers and pins of every name and literal this plan touches |
| `C:/Temp/av-kit/s71-pydantic-int-probe.txt` | `StrictInt \| None` refuses `3.0`, `true` and `"3"` |
| `C:/Temp/av-kit/s71-rule1-today.txt` | today's colour and settings tests pass at `5e9ea7c` |
| `C:/Temp/av-kit/s71-plan-shapes-dryrun.txt` | `baseline.ps1`'s rulings, queue, shapes and anchors blocks run alone at `5e9ea7c` (rulings exit 1 until the gate words are in; the others exit 0) |
| `C:/Temp/av-kit/s71-plan-rc-selftest.txt`, `C:/Temp/av-kit/s71-plan-identity-selftest.txt`, `C:/Temp/av-kit/s71-plan-idlen-selftest.txt` | the three selftests |
| `C:/Temp/av-kit/s71-plan-decision-probe.txt` | the decision probe: the grouping alone gives D-158 to D-160; the plan with the grouping gives D-713 to D-728 (`planning`) and D-158 to D-160 (`grouping`); the plan alone is refused (HDP-18); every source is unchanged |
| `C:/Temp/av-kit/s71-plan-task-lint.txt` | `lint_task_contract.py` on `task.md`, with `RECEIPTS_DIR=C:/Temp/av-kit` |

No suite or build ran at plan time, apart from the two test files in `s71-rule1-today.txt`.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `npm --prefix ui run typecheck`, `ui-lint`, `lint_task_contract.py`, the scope-paths check, the `red-check.py` selftest and `id-length.py`.
- **Targeted:** each row's own files. `red-check.py` reads the Red receipts, and `capture-action-row.test.ts` runs on its own in the row that touches `test-ids.ts`.
- **Fresh full:** the session gate runs the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds and the capture Electron spec.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the pinned FFmpeg pair and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
