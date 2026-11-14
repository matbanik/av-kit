---
project: "2026-11-14-capture-tool-flow"
date: "2026-11-14"
source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md#session-47--capture-style-tool-flow-meu-105--p3"
grouping_source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md"
meus: ["MEU-143"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: Capture tool lock, tool letters and draw modifiers (Session 71b)

> **Project:** `2026-11-14-capture-tool-flow`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Style and tool flow (`:970-984`, anchor `style-and-tool-flow`): the Lock row, the Letters row and the Modifiers row apart from the Pixelate scrub. The MEU table row is `:1311`, and the build priority matrix row is 9.31a.
>
> **Source request.** On 2026-10-29 Mat accepted the capture annotation editor synthesis ("all recommendations are accepted", grouping D-158). On 2026-11-13 Mat split MEU-105 (D-713, USER_EXPLICIT 2026-11-13 "A"). Session 71 delivered the style half. This session delivers the tool-flow half as MEU-143 `gui-capture-tool-flow`, which is grouping §6 row 47b (`:126`).
> **Status:** `draft`. `plan_to_exec_gate: human`. The plan review approved at round 2 (`.agent/context/handoffs/2026-11-14-capture-tool-flow-plan-critical-review.md`), after round 1 returned `changes_required` (F1, fixed). At the plan gate Mat chose the band, D-756 (USER_EXPLICIT 2026-11-14 'P2 in both (Recommended)'), and, D-757, said to execute (USER_EXPLICIT 2026-11-14 'Execute now (Recommended)'). The review loops have no token budget (`.agent/review-limits.json` `token_budgets: "off"`). Their round caps are the repository's: plan 3, execution 6.

## Goal

**Goal anchor:** Session 71b makes the capture editor fast to drive from the keyboard and from a held tool.
- Lock is on by default and is saved as the app preference `capture.tool_lock`. Turning it off is the one-shot preference: each mark returns to Select.
- Under Lock, the mark just drawn stays selected. While a tool is armed, a press on that selected mark edits it, and a press elsewhere draws.
- The letters V, A, R, H, T, X, E and C arm Select, Arrow, Box, Highlight, Text, Redact, Smart eraser and Crop. They never fire in a field.
- Shift draws a square, keeps a box's shape and snaps an arrow to 45 degrees. Alt draws a bounded mark from its centre. Shift with an arrow key nudges 10 px.

Six things are missing today (`42f02bc`):

1. **Lock is off and not saved.** It is `useState(false)` (`CapturePage.tsx:404`), so a reload starts with it off. Under Lock, a draw leaves nothing selected: `commitSelection` runs only inside `if (!toolLocked)` (`:1295`, `:2650`).
2. **An armed press always draws.** Only the Select branch of the pointer-down hit-tests (`:1215`). With Box armed, a press on the box just drawn starts a new box.
3. **No tool letters.** Every registry shortcut is a Ctrl chord or F1 (`registry/commandRegistry.ts`). The Crop button ships with the tooltip "Crop" and no `aria-keyshortcuts`, because C was deferred to this MEU (09 `:1098`, `:1109`; D-508).
4. **No field guard for letters.** `createShortcutHandler` ignores the focused element (`registry/shortcuts.ts:206-209`). A plain letter bound in the registry would fire from the text draft, the hex field and every other input.
5. **No draw modifiers.**
   - The surface pointer carries `shiftKey` only for the crop (`CaptureViewport.tsx:106-107`). `createDrawnMark` (`CapturePage.tsx:317`) takes the raw start and end points.
   - The editor nudge is always `KEYBOARD_NUDGE_PX = 1` (`:104`, `:1888-1897`).
   - Shift on a mark resize does nothing.
6. **The focused surface would run X twice.**
   - The surface's `onKeyDown` calls the page's `handleEditorKey` and then lets every registry chord bubble (`CAPTURE_CHORD_BUBBLE`, `CaptureViewport.tsx:1341-1350`).
   - The page's window listener (`CapturePage.tsx:1910-1925`) calls `handleEditorKey` again.
   - Today X is no registry chord, so it stops at the surface. Once X is bound, X with the crop open would swap the aspect twice.

Today's behaviour was read at `42f02bc` (Session 69 RULE-1). The pins are listed in §Pins that move.

The session ends when:
- every MEU-143 part of 09 §Style and tool flow holds, each with a behaviour test: the Lock row, the Letters row, and the Modifiers row's Shift, Alt and Shift+arrow;
- the session gate's last line is `session-gate: all steps exit 0`;
- MEU-143 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-14). No payload is oversized: the registry, the shortcut handler, the style store, the settings service, the API schema, the MCP settings toolset, the viewport and the page were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, the Claude Code block of `.agent/context/harness.local.md`). Execution waits for Mat's explicit words at the plan gate (D-757). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit` with the `s71b-*` names;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s71b\tmp` for the Python suite;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run, and the scripts clear it as well.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS. GUI references are not shipped (`gui-refs-not-shipped`).
- **Decisions:** every decision for Mat goes to Mat through the Human Decision Protocol (AGENTS.md §Communication Policy), with a recommendation first and a do-nothing option. No decision goes to a subagent in this session.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s71b-plan-canonical-2026-11-14-capture-tool-flow` and `s71b-execution-2026-11-14-capture-tool-flow`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Round caps are the repository's: plan 3, execution 6. Token budgets are `off` (`.agent/review-limits.json`), so the loops stop on rounds only. Mat is not asked for a budget. The coordinator reports the token estimate and each round's spend.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, so the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path. The `--review-state-only` receipt is then rebuilt there.
- **Reviewer prompts:**
  - They name the ledger vocabulary up front: D-744 to D-757, AC-143.1 to AC-143.36, and the mechanism ids in §Single-statement contracts.
  - They forbid opening:
    - `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json` and any `.env`;
    - `.claude/settings.local.json`;
    - anything under `.agent/fleet/hub`;
    - `docs/proposals/2026-11-10-download-logic-divergence-report.md`.
  - They write `<HOME>` for the home folder.
  - When a prompt asks for `tested_state`, it names `~/.config/git/ignore` and the path that file hides, `.claude/settings.local.json` (Session 51 RULE-4).
  - `## Findings` holds only the Findings table (Session 65 RULE-3).
  - Every prompt carries the literal `### New Findings` header. It also carries the Prior Pass Summary table, with the columns Finding, Prior Status and Recheck Result (Session 66 RULE-4).
  - A recheck names each prior finding by the review's own id (Session 53 RULE-3). It asks for bare words in its Recheck cells, such as `fixed` and `open` (Session 52 RULE-1, Session 57 RULE-5).
- **Never in these rows without Mat's words:**
  - a commit, a push, a tag, a release or an upload;
  - the live MCP audit or `--update-baseline`;
  - `npm run dist`;
  - an `approved` verdict written by the implementer;
  - reading any user data: the capture inbox, its sidecars, the app database or Mat's settings file (Session 70 RULE-2). Every test works from fixtures and fakes.
- **No network, no clipboard:**
  - no test or row reaches YouTube or the network;
  - no test or row writes the system clipboard (Session 57 RULE-4);
  - nothing touches the installed avkit MCP servers, and no `mcp__avkit__*` tool is called;
  - no other program is stopped. If ShareX holds a key a row needs, the row stops and asks Mat (S13).

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-143 | `.agent/context/handoffs/2026-11-14-capture-tool-flow-MEU-143-handoff.md` | only |

Rolling reviews:
- `.agent/context/handoffs/2026-11-14-capture-tool-flow-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-14-capture-tool-flow-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0 | Baseline: rulings, queue, shapes, dirty paths, anchors, base suites, selftests | shared |
| WP-2 | 1 | Type-only names: `readToolLock`, `saveCaptureToolLock`, `lockSaveFailures`, `subscribeLockSaveFailures`, `useCaptureToolLock`, `captureLockPutSchema`, `TOOL_LETTERS`, `CAPTURE_TOOL_IDS`, `lib/editable-target.ts`, the exported `FIELD_STEP_SHIFT`, `capture-modifiers.ts` and `SurfacePointer.altKey` | shared |
| WP-3 | 2 | The `tool_lock` settings row, the API leaf, the regenerated OpenAPI snapshot and the MCP leaf | shared |
| WP-4 | 3, 4 | Red, then Green (the behaviour and the help text) | shared |
| WP-5 | 5 | The actions index and 09's Delivered and Entry notes | shared |
| WP-6 | H1, H2 | Gate, handoff, review, reflection, records, next prompt | compact_continue |

## User Review Required

**Carried rulings:**
- **D-158** (USER_EXPLICIT 2026-10-29 "all recommendations are accepted", grouping §8 `:141`) accepts the synthesis that 09 §Style and tool flow encodes: A-10, A-12, A-13, C-6, C-12 and D-2 for this half.
- **D-159** (autonomous, Local Canon, `:142`) made one MEU per slice. **D-160** (autonomous, Local Canon, `:143`) is carried: the plan-time decision probe returns it (`C:/Temp/av-kit/s71b-plan-decision-probe.txt`: D-158, D-159 and D-160 from the grouping, D-744 to D-757 from this plan).
- **D-674 and D-675** (autonomous, grouping §9.8) set the session numbering and the crop rules. MEU-143 adds no mark type and no mark field, so D-675's crop rules are unchanged (AC-143.33).
- **D-678** (grouping §9.8) keeps Ctrl+C on the page key handler, with `isEditableTarget` excluded and Ctrl+C in `RESERVED_CHORDS`. This plan changes neither (AC-143.33).
- **D-713** (human, USER_EXPLICIT 2026-11-13 "A", grouping §9.9) is the split that makes this MEU.

**MEU-105 contracts this plan keeps:**
- STYLE_STORE, STYLE_DISPLAY and STYLE_DRAW: a letter shows the armed tool's style exactly as a click does, because the letter's action presses the same button (LETTERS, AC-143.16).
- SELECT_NO_STYLE (D-721): after V there is no `capture-color` field (AC-143.16).
- STYLE_TARGET (D-719): after a draw under Lock, the just-drawn mark is selected, so a style change restyles that mark and sends no PUT (AC-143.13). To set the tool's own style instead, pick the tool again, by click or letter. That clears the selection (ARMED_RECHOOSE).

**The Lock leaf joins STYLE_STORE's queue and filter (D-746).**
- `tool_lock` is one more leaf in `capture-style-store.ts`:
  - its PUT waits in the same promise chain as the style PUTs;
  - `latest` records it as it records a style leaf;
  - `fetchCaptureSettings` keeps the committed value over a GET that did not see it.
- A held GET can't put back the old Lock state, and a failed GET shows the last committed state, or `true` if nothing was committed (AC-143.9). A failed PUT shows `Couldn't save the tool lock` and refetches once the queue is empty (AC-143.10). This answers Session 71 RULE-1.

**AC-87 is superseded (D-755).** MEU-87's lock tests pin today's behaviour:
- Lock is off at load (AC-87.2);
- under Lock, nothing is selected after a draw (AC-87.3, AC-87.5) or after a text commit (AC-87.4);
- the Electron AC-87.6 clicks Lock on before it draws twice;
- the help sentence is `The lock button keeps the current tool after each mark.` (AC-87.7).

09's Lock row (C-6, D-2) changes each of these. Row 3 rewrites them as listed in §Pins that move, and AC-87.1 (the toolbar spec) holds. Mat sees this at the gate. Its do-nothing option is "keep AC-87 and ship Lock off by default", which would break the 09 Lock row.

**Band mismatch (D-756, asked at the gate).** The grouping's §3 heading (`:87`) and tracker row 47b (`:126`) say P3. `.agent/context/meu-status.yaml` gives MEU-143 `band: P2`, the same pair MEU-105 has (D-725). This plan changes neither. The gate asks Mat once:
- recommendation: "P2 in both", because `meu-status.yaml` drives the queue and the build plan;
- do-nothing option: "leave both as they are".

**OpenAPI and MCP change (D-744).** The Lock preference follows D-717's path:
- `SettingsPutIn` forbids extra keys, so it gains `tool_lock: StrictBool | None = None`, and the committed OpenAPI snapshot is regenerated, never edited by hand.
- The strict MCP `avkit_settings` set schema gains `tool_lock: z.boolean().optional()`, and `SETTINGS_SCHEMA` gains `tool_lock` with its default, so an agent can write back what get returns.
- No mark schema, sidecar, bake, annotate body or capture action changes.
- The MCP audit baseline is keyed by tool, action and status, and no action is added, so it doesn't change.
- `isolationKeys` (`mcp-server/scripts/audit/classify.ts:281`) collects only path-like string leaves, and a boolean is not one.
- `tool_lock` is a boolean, so `_reject_cookie_shaped` (string leaves) and the integer path (`integer=True`) don't apply, and no int leaf is added.

**Rulings at plan time.** None. Two questions go to Mat at the gate through the HDP: the band (D-756) and his words to execute (D-757).

**Gate flags.** At the gate Mat also sees these, each with a recommendation and its do-nothing option:
- D-745: the one-shot preference is Lock off, saved. The toolbar Lock button is its only control: the Settings card doesn't show it.
- D-748: under Lock, the just-drawn mark stays selected, and an armed press on it edits it.
- D-751: plain letters never fire from a field, a select or the palette search. Ctrl and F-key chords still do.
- D-753: what each modifier does to each tool. Corner handles keep their shape under Shift; edge handles don't.
- D-755: the AC-87 supersession above.

An AC or contract change during execution goes to Mat as a Decision Brief (S12). Its do-nothing option is "record it as a departure and keep the approved text".

**Plan review.** Approved at round 2 of 3 (`.agent/context/handoffs/2026-11-14-capture-tool-flow-plan-critical-review.md`). Round 1 (10,176,921 tokens) found F1, AC-105.2's order pin; round 2 (7,637,302 tokens) rechecked it `fixed` with no new findings. The loop spent 17,814,223 tokens, inside the 17M to 24M estimate.

**Network.** Recommendation: none, because nothing here fetches. The do-nothing option is the same, so there is no brief.

**Token estimate (report only; budgets are off).** Calibrated against:
- Session 41 `gui-keyboard-palette` (registry chords): plan 32.5M over 3 rounds (`docs/execution/metrics.md:52`);
- Session 70 `capture-text-multiline`: plan 8.6M in one round, execution 10.7M in one round;
- Session 71 `capture-style-tool-flow`: plan rounds of 9.96M, 6.81M and 7.56M; execution 19.2M, plus a 5.8M recheck.

This session is one MEU across:
- the settings service, the API schema, OpenAPI and the MCP settings toolset;
- the style store;
- the registry and the shortcut handler;
- the viewport and the page's pointer and key handlers;
- a new modifiers module.

It is about Session 71's size. The estimates:
- plan review: about 10M for round 1 and about 7M for each recheck, so about 17M to 24M for the loop;
- execution review: about 19M for round 1 and about 6M for a recheck, so about 25M.

**Word meanings.**
- A *letter* is one of V, A, R, H, T, X, E and C, pressed with no Ctrl, Alt or Meta. With Shift it is a different chord (`Shift+V`), which nothing binds.
- A *field* is any element `isEditableTarget` accepts (a textarea, a text-like input or a content-editable element) or a `<select>`:
  - the text draft and the hex field;
  - the Stroke, Size and Block size inputs;
  - the crop's X, Y, W and H fields;
  - the named-colour menu and the crop aspect menu;
  - the palette search;
  - every Settings input.
- A *bounded tool* is one whose mark is a box: Box, Highlight, Redact (Solid and Pixelate) and Smart eraser.
- *Armed* means a tool other than Select and Crop is current.
- *The just-drawn mark* is the mark that the last draw or text commit added, while its tool is still armed.
- *Lock on* means `capture.tool_lock` is `true`. *One-shot* means it is `false`.

## Proposed Changes

### Single-statement contracts

Each mechanism id below is one statement. A row cites the id; a test names the AC.

| Id | Statement | File |
|---|---|---|
| `LOCK_LEAF` | `SETTINGS_KEY_TABLE` gains `("capture", "tool_lock"): SettingSpec("boolean", True)` after `pixelate_block_size` (`services/settings.py:123-125`). `SettingsPutIn` gains `tool_lock: StrictBool \| None = None` after `pixelate_block_size`, so the API refuses `"false"`, `0` and `1` with a 422. An explicit `null` reaches the service through `exclude_unset`, and `_encode` refuses it with a 422. `SETTINGS_SCHEMA.namespaces.capture` gains `tool_lock: { type: "boolean", default: true }`, and the strict set schema gains `tool_lock: z.boolean().optional()`. `openapi.committed.json` is regenerated with `tools/export_openapi.py`. The only change it may show is `tool_lock` added to `SettingsPutIn` (D-744) | `services/settings.py`, `schemas/settings.py`, `openapi.committed.json`, `mcp-server/src/toolsets/settings.ts` |
| `LOCK_DECODE` | `_decode` doesn't change: a stored boolean reads `True` only when it is exactly `"true"`, so an empty, control-character, lone-surrogate or any other stored text reads `False`. `_encode` refuses every non-`bool` value with today's `ValidationError`, which names the key and not the value. On the UI side, `readToolLock(data: unknown): boolean` returns `false` only when `data` is an object whose `tool_lock` is exactly `false`; every other input returns `true`: `undefined`, `null`, a missing key, `true`, `"false"`, `0`, `""`, a lone surrogate or a control character (D-747) | `services/settings.py` (unchanged), `capture-tool-lock.ts` (new) |
| `LOCK_STORE` | `capture-style-store.ts` moves its queue, `latest` and failure handling into one internal core, which `saveCaptureToolStyle` and a new `saveCaptureToolLock(client: QueryClient, locked: boolean): void` share. `LeafEntry.value` widens to `string \| number \| boolean`. `saveCaptureToolLock` parses `{ tool_lock: locked }` with a new strict `captureLockPutSchema` (`settings-schemas.ts`). It records the leaf in `latest`, merges it into the cached data at once, and queues one `PUT /settings/capture` with that body alone, in the same chain as the style PUTs. On failure it raises a separate counter, read through `lockSaveFailures()` and `subscribeLockSaveFailures(listener)`. The page shows `Couldn't save the tool lock` for it, a message that names no value. The shared invalidate-once rule then refetches. `fetchCaptureSettings` keeps `tool_lock` over a GET that didn't see its commit, as it keeps a style leaf. A new `useCaptureToolLock()` returns `{ locked: boolean, setLocked(next: boolean): void, failures: number }`, with `locked = readToolLock(query.data ?? committedStyleLeaves())`. `captureStylePutSchema`, `capturePutSchema` and `TOOL_STYLE_LEAVES` don't change (D-746) | `capture-style-store.ts`, `capture-tool-lock.ts` (new), `useCaptureToolLock.ts` (new), `settings-schemas.ts`, `CapturePage.tsx` |
| `ONE_SHOT` | The toolbar Lock button (`capture-tool-lock`) shows `locked` and calls `setLocked(!locked)`. Off is the one-shot preference: each draw and each text commit returns to Select with the new mark selected, as AC-60.4 says today. The Settings Capture card doesn't show the leaf, and its 7-key form and Save body don't change (D-745) | `CapturePage.tsx`, `CaptureViewport.tsx` |
| `LOCK_SELECTS` | Under Lock, a draw that adds a mark calls `commitSelection(list.length - 1, list, tool)` and a text commit calls `commitSelection(index, list, 'text')`. The armed tool stays and the new mark becomes the selected one: its handles show, its options row shows its style (STYLE_DISPLAY), and the nudge target is its body. One-shot keeps today's `commitSelection(…)` to Select. A draw that adds nothing (a zero-size box, a zero-length arrow) changes no selection (D-748) | `CapturePage.tsx` |
| `ARMED_EDIT` | With an armed tool and a selected mark, a pointer-down first hit-tests only that mark: `hitTestMarks(…, annotations: [mark], selectedIndex: 0)`, with the index mapped back. A hit on a handle, a resize handle or the body starts the Select branch's gesture for it: an endpoint drag, a resize or a move. The gesture start moves into a shared helper both branches call. The armed tool stays. This check runs before the text tool's draft branch. A miss draws as today, and a press on an unselected mark draws over it too. The selected mark is the just-drawn one, because `chooseTool` clears the selection whenever the next tool isn't Select (D-748) | `CapturePage.tsx` |
| `ARMED_RECHOOSE` | Choosing the armed tool again, by its button or its letter, runs `chooseTool(tool)`, which clears the selection. A style change then sets the tool's own style (STYLE_TARGET's second half). Escape is unchanged: it cancels a gesture and doesn't clear the selection (D-749) | `CapturePage.tsx` (unchanged path; stated and tested) |
| `LETTERS` | `commandRegistry.ts` gains `CAPTURE_TOOL_IDS = ['capture:tool_select', 'capture:tool_arrow', 'capture:tool_box', 'capture:tool_highlight', 'capture:tool_text', 'capture:tool_redact', 'capture:tool_eraser', 'capture:tool_crop']` and one entry for each, in that order, after `capture:open_folder`. Each entry has `category: 'capture'`, `page: '/capture'`, `stateful: true`, `palette: false` and `shortcut` set to V, A, R, H, T, X, E or C. Each action clicks its `capture-tool-*` button only while that button is enabled, the PAGE_PRIMARY pattern. A new `TOOL_LETTERS: Readonly<Record<CaptureTool, string>>` in `capture-toolbar.ts` holds the same letters, keyed by tool beside `TOOL_STYLE_LEAVES`'s tools. The registry entries and the buttons both read it. The page publishes each id's state through `usePublishCommandState('/capture', …)`: enabled exactly when its button is enabled, the crop is closed, no text draft is open, the transform dialog is closed and no confirm is open. With the crop open, every letter's state is `false`, so the handler returns `false` without `preventDefault`, and the crop's own X swap runs (CROP_MODAL). `BOUND_CONTROLS` gains the eight `{ testid, commandId }` pairs in the same order (D-750) | `commandRegistry.ts`, `shortcuts.ts`, `capture-toolbar.ts`, `CapturePage.tsx` |
| `LETTER_HINTS` | Each of the eight tool buttons passes `shortcut={TOOL_LETTERS[tool]}` to `ToolbarIconButton`. Its hint reads `Name (L)`, with any spec hint after a colon, as in `Smart eraser (E): Covers an area with the surrounding colour`. The disabled hint reads `Name (L) — reason`. The button carries `aria-keyshortcuts`, and the accessible name stays the bare name. The Crop button reads `Crop (C)`, which closes 09's Entry rule (`:1098`) | `CaptureViewport.tsx` |
| `FIELD_GUARD` | `createShortcutHandler` returns `false`, with no `preventDefault`, for a chord that has no Ctrl and no Alt and whose key is one character long, when the event target passes `isEditableTarget` or is an `HTMLSelectElement`. Ctrl chords, F-keys and named keys behave as today. `isEditableTarget` moves to `lib/editable-target.ts` unchanged, and `capture-import.ts` re-exports it for its callers. The handler's doc comment says that letters don't fire from fields (D-751) | `shortcuts.ts`, `lib/editable-target.ts` (new), `capture-import.ts` |
| `CHORD_BUBBLE_ONCE` | `handleEditorKey` records each event it has handled in a module `WeakSet<KeyboardEvent>`, `handledEditorKeys`, and returns at once for an event already in it, as `handleViewKey` does with `handledViewKeys` (`CaptureViewport.tsx:827-845`). A key that the focused surface handles and then lets bubble as a registry chord runs once, not twice (D-752) | `CapturePage.tsx` |
| `MODIFIERS` | `SurfacePointer` gains `altKey: boolean`. A new `capture-modifiers.ts` exports these:<br>• `drawBounds(anchor: ImagePoint, point: ImagePoint, mods: { square: boolean; centre: boolean }, imageW: number, imageH: number): { start: ImagePoint; end: ImagePoint }`. With `square`, the box takes the longer side, cut to what fits inside the image in the drag's direction, and its ratio is `1`, as `ratioBox` gives it (CROP_RATIO). With `centre`, the anchor is the centre, and the half-extents are cut so the box stays inside the image with the centre fixed.<br>• `snapArrowEnd(fixed: ImagePoint, moving: ImagePoint, imageW: number, imageH: number): ImagePoint`, which keeps the length, rounds the angle to the nearest multiple of 45 degrees, rounds to whole pixels, and shortens the arrow along that angle until the end lies inside the image.<br>• `keepRatioResize(start: BoxMark, handle: HandleId, point: ImagePoint, imageW: number, imageH: number): BoxMark`, which applies only to a corner handle. It keeps the start box's ratio as the crop's corner does (`resizeCrop`, `capture-crop.ts:159-176`): the larger relative change of width or height drives, `ratioBox` builds the box, the opposite corner stays, and the box is cut to the image.<br>The page applies them as follows:<br>• in a bounded tool's draw, Shift gives `square` and Alt gives `centre`, and both can apply together;<br>• in an arrow draw and an arrow endpoint drag, Shift snaps, and Alt does nothing;<br>• on a corner-handle resize of a box mark, Shift keeps the ratio, while an edge handle ignores Shift;<br>• the text tool and a move ignore both.<br>`createDrawnMark` keeps its signature and receives the transformed points. The modifier is read at each move and at the up, so pressing or releasing it mid-drag takes effect at once (D-753) | `capture-modifiers.ts` (new), `CaptureViewport.tsx`, `CapturePage.tsx` |
| `SHIFT_NUDGE` | `CaptureCropBar.tsx` exports `FIELD_STEP_SHIFT` (10). In `handleEditorKey`, Shift with an arrow key nudges the selected mark, or the grabbed arrow end, by `FIELD_STEP_SHIFT` image pixels. The move is clamped as today's nudge is, and a burst is still one undo step. `CROP_NUDGE_SHIFT_PX` and the crop's nudge don't change (D-675) | `CaptureCropBar.tsx`, `CapturePage.tsx` |
| `ALT_NO_MENU` | While a drawing gesture of a bounded tool is live, the surface's Alt `keydown` and `keyup` are `preventDefault`ed. So are the first Alt `keyup` after such a gesture ends, and the Alt `keydown` that pairs with it. On Windows, Electron's default menu then doesn't take focus when Alt is released, and the next letter reaches the page. Alt with no such gesture is left alone (D-754) | `CaptureViewport.tsx` |
| `LOCK_HELP` | The Annotation tools help body (`capture-help-content.ts:27`) replaces `The lock button keeps the current tool after each mark.` with: `The lock is on by default: the tool stays armed after each mark and the new mark stays selected, so a style change restyles it and a press on it moves or resizes it; pick the tool again to set its own style. Turn the lock off to return to Select after each mark; Capture remembers the choice. Press V, A, R, H, T, X, E or C for Select, Arrow, Box, Highlight, Text, Redact, Smart eraser or Crop; letters type normally in a text field. Hold Shift to draw a square, keep a box's shape from a corner or snap an arrow to 45 degrees; hold Alt to draw a box from its centre.` It also changes `Arrow keys nudge the selected mark` to `Arrow keys nudge the selected mark (Shift+arrow by 10 px)`. No section is added | `capture-help-content.ts` |
| `FLOW_ACTIONS_INDEX` | In `gui-actions-index.md`, the Trigger cells of `capture:tool_arrow` to `capture:tool_eraser` (`:85-90`) gain their letter, for example `Arrow tool (A)`. `capture:tool_select` (`Select tool (V)`) is added before `capture:tool_arrow`, and `capture:tool_crop` (`Crop (C)`) after `capture:tool_eraser`. `capture:tool_lock` (`:91`) reads `Keep tool after drawing (tool lock); on by default; off returns to Select after each mark`, and its route reads `PUT /settings/capture` (`capture.tool_lock`). A row `capture:draw_modifiers` follows `capture:style_tool`: `Shift draws a square, keeps a box's shape or snaps an arrow to 45°; Alt draws from the centre; Shift+arrow nudges 10 px`, local canvas | `gui-actions-index.md` |
| `FLOW_SPEC` | 09 gains a `> **Delivered (Session 71b).**` note after the Session 71 note (`:984`), before `<a id="line-and-ellipse"></a>`. It names the mechanism ids, AC-143.1 to AC-143.36 and the plan folder. The Entry note (`:1109`) gains a sentence: `MEU-143 (Session 71b) delivered C and the tooltip "Crop (C)".` The rule rows don't change | `09-screenshot-capture.md` |

### Pins that move

The plan-time reads cover:
- the AC-87 lock tests;
- the tool hint pins (`icon-hints.test.ts`, `capture-page.behavior.test.ts`'s HINT_OVERRIDE, `capture-redact.behavior.test.ts`'s SMART_HINT, the crop hints and the Electron hints);
- the help sentence;
- the capture key sets;
- AC-60.12's title;
- every test fake that answers `GET /settings/capture`.

Row 2 moves the four key-set pins, and row 3 (Red) moves the rest, so Green changes no test file (S2):

| Pin | File and line | Ending | Change |
|---|---|---|---|
| AC-36.12 (the capture key set) | `tests/unit/test_capture_service.py:20-36`, `:400-420` | CRLF | `CAPTURE_KEYS` and `CAPTURE_DEFAULTS` gain `tool_lock` (default `True`) |
| AC-38.6 (the MCP capture keys) | `mcp-server/tests/capture.test.ts:45-63`, `:194-206` | CRLF | the same leaf and default. Its `:226` loop compares defaults only, so it covers `tool_lock` once the keys move and doesn't change |
| AC-105.2 (the style rows follow `annotated_format`) | `tests/unit/test_capture_style_settings.py:46-50` | LF | the nine style leaves stay exact and contiguous after `annotated_format` (`keys[start:start + len(STYLE_DEFAULTS)] == list(STYLE_DEFAULTS)`), and a separate assertion makes `tool_lock` the only key after them |
| AC-105.5 (the nine style leaves' schema) | `mcp-server/tests/capture.test.ts:1732` | CRLF | the loop over `CAPTURE_KEYS.slice(7)` becomes `CAPTURE_KEYS.slice(7, 16)`, so its nine-leaf `types` map covers every key it checks and the test still means what its title says. AC-143.5 checks `tool_lock`'s entry |
| AC-87.2 and its negative | `ui/tests/unit/capture-page.behavior.test.ts:3292-3325` | CRLF | the lock shows `aria-pressed="true"` at load on a GET without `tool_lock`. A click turns it off and sends one PUT `{ tool_lock: false }`; it still changes no tool, selection or Save. With no shot it stays enabled |
| AC-87.3 and its negative | `:3326-3355` | CRLF | under Lock, a Box drag keeps Box with the new box selected, and a second drag elsewhere selects the second box. Two Undos remove them one at a time. One-shot returns to Select with the box selected (AC-60.4) |
| AC-87.4 and its negative | `:3356-3382` | CRLF | under Lock, a text commit keeps Text with the new text selected, and a click away from it opens a new draft. One-shot is unchanged |
| AC-87.5 and its negative | `:3383-3410` | CRLF | the lock survives a tool change, and the drawn arrow is selected. Turning it off restores auto-Select from the next mark |
| AC-87.6 (Electron) | `ui/tests/e2e/capture-inbox.test.ts:2558` | LF | asserts Lock pressed at load and doesn't click it; the two Box drags keep Box, and the second box is selected |
| AC-87.7 (the lock help sentence) | `ui/tests/unit/capture-help-content.test.ts:87-92` | CRLF | `LOCK_HELP_SENTENCE` is LOCK_HELP's first sentence; the old sentence is absent |
| The nudge help words | `ui/tests/unit/capture-action-row.test.ts:68` (it holds `Arrow keys nudge the selected mark, or the arrow end you grabbed or tabbed to.`), and any `capture-help-content.test.ts` line row 1's sweep finds | CRLF | `Arrow keys nudge the selected mark (Shift+arrow by 10 px), or the arrow end you grabbed or tabbed to.` |
| AC-80.8 and AC-80.9 (icon hints) | `ui/tests/unit/icon-hints.test.ts:63-67`, `:324`, `:332` | CRLF | HINT_OVERRIDE gains the eight tool hints `Name (L)`, with the eraser's `Smart eraser (E): …`. The no-shot line reads `${spec.name} (L) — ${NO_SHOT_HINT}` for the tool ids |
| MEU-65 HINT_OVERRIDE | `capture-page.behavior.test.ts:1455-1460` | CRLF | the same tool hints |
| SMART_HINT | `ui/tests/unit/capture-redact.behavior.test.ts:43` | LF | `Smart eraser (E): Covers an area with the surrounding colour` |
| AC-131.x (the Crop hint) | `ui/tests/unit/capture-crop-tool.behavior.test.ts:423-424`, `:447`, `:455`, `:472` | LF | `Crop (C)`, with `aria-keyshortcuts` present; `Crop (C) — reason` |
| The Electron tool hints | `capture-inbox.test.ts:1675` (`Arrow`), `:3342` (the eraser) | LF | `Arrow (A)`; `Smart eraser (E): …` |
| AC-60.12's title | `capture-inbox.test.ts:468` | LF | `typed hex, Apply` becomes `typed hex, Enter`; the body already presses Enter |
| The test fakes of `GET /settings/capture` | the unit harnesses in `capture-page.behavior`, `capture-redact.behavior`, `capture-crop-tool.behavior`, `capture-text-lines.behavior`, `capture-style-flow.behavior`, `capture-copy-image.behavior`, `capture-filmstrip-actions.behavior`, `capture-import.behavior`, `capture-action-row` and `icon-hints`; the Electron seams in `capture-inbox`, `capture-filmstrip-actions`, `capture-import` and `capture-picker` | as each file | `tool_lock: false` is added where a test is about something else, so its draws still return to Select. The new MEU-143 tests and the rewritten AC-87 tests set the leaf themselves |

These were read and hold:
- AC-87.1 (`ui/tests/unit/capture-toolbar.test.ts:168-175`): the lock spec's icon and name `Keep tool after drawing`;
- the accessible-name lookups `getByRole('button', { name: 'Arrow' })`, because the aria-label stays the bare name;
- AC-97.4 (`ui/tests/unit/common-shortcuts.test.tsx:49`), which uses `toContainEqual`, so the new BOUND_CONTROLS pairs don't break it;
- AC-19.17 (`command-palette.test.ts:3`) and AC-23.18 (`gui-actions-audit.test.ts:157`), which use `arrayContaining` and `toContain`. The letter entries are `palette: false`, so the palette lists none of them;
- AC-95.5 (F1 and Ctrl chords from a field), which FIELD_GUARD keeps;
- AC-39.14 (`capture-page.test.ts:107`), whose `CAPTURE_PALETTE_IDS` this plan doesn't change;
- the crop X tests (`capture-crop-tool.behavior.test.ts:598-600`, `:620-622`), which hold. AC-143.19 adds their inverse.

Before writing, row 1 sweeps `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` again (Session 55 RULE-1, Session 59 RULE-1, Session 62 RULE-4, Session 63 RULE-1, Session 66 RULE-1, Session 68 RULE-2). It looks for:
- these names;
- the literal text this plan rewrites: `The lock button keeps`, `Arrow keys nudge the selected mark`, `typed hex, Apply`, `'Crop'`, and the bare tool hints;
- exact-signature pins of `SurfacePointer`, `createShortcutHandler`, `BOUND_CONTROLS`, `isEditableTarget` and `CAPTURE_PALETTE_IDS`;
- every fake that answers `/settings/capture`.

It records the hits with each file's ending in `s71b-anchors.txt`. A pin found then and missing here goes into the handoff as a departure.

**Enum-keyed maps (Session 68 RULE-1).** `TOOL_LETTERS` is keyed by `CaptureTool` and gets all eight entries in row 1. A new `CaptureTool` then fails the type check there. It sits in `capture-toolbar.ts`, beside `TOOL_STYLE_LEAVES`'s tool switch.

**Order pins (Sessions 59 and 63).** These orders are pinned:
- the toolbar order: the Annotation tool group (Select, Arrow, Box, Highlight, Text, Redact, Smart eraser), then Lock, Crop, then History. It doesn't change (AC-143.15).
- the registry order: the eight letter entries follow `capture:open_folder` in CAPTURE_TOOL_IDS order (AC-143.15).
- the BOUND_CONTROLS order: the eight pairs follow `capture-save` in the same order (AC-143.15).

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers | Rule |
|---|---|---|---|
| The Lock preference | `saveCaptureToolLock` (the toolbar button), an agent's `avkit_settings` set, the Settings API | `SettingsPutIn`, `SettingsService._encode`, the app database, `_decode`, `get_namespace`, `fetchCaptureSettings`, `readToolLock`, the page | refused at the API (`StrictBool`) and the service (`isinstance(value, bool)`); read back as `True` only from `"true"` on the server, and as `false` only from `false` in the UI (AC-143.3, AC-143.6); no error, status line or Console line names a value (S6) |
| The armed tool | the tool buttons, the letters (through the buttons), LOCK_SELECTS, one-shot | the toolbar, STYLE_DISPLAY, STYLE_DRAW, the pointer handlers | not saved (D-680 kept the Redact mode unsaved; the tool follows) |
| The modifier keys | the pointer event's `shiftKey` and `altKey`, the key event's `shiftKey` | `capture-modifiers.ts`, the nudge | never stored |

Two traces cover the functions between the user's input and the port, using recording fakes (Session 55 RULE-3):
- AC-143.21 traces one `A` keydown on the focused surface. It goes through `createShortcutHandler` (a recording `getState`), the `capture:tool_arrow` action, the `capture-tool-arrow` click and `chooseTool`. It ends at the button's `aria-pressed="true"` and the hex field showing the arrow tool's saved colour.
- AC-143.22 traces one Lock click. It goes through `onToggleToolLock`, `setLocked`, `saveCaptureToolLock` and `captureLockPutSchema`, to the recorded PUT body `{ "tool_lock": false }`. Its Python half traces the API body through `SettingsPutIn` and `SettingsService.set_namespace` (a recording wrapper) to the stored `"false"` and the next GET's `false`.

### Spec text (D3)

| File | Change |
|---|---|
| `docs/build-plan/09-screenshot-capture.md` | FLOW_SPEC |
| `docs/build-plan/gui-actions-index.md` | FLOW_ACTIONS_INDEX |

### MEU-143 `gui-capture-tool-flow`

**Boundary inventory.**

| Boundary | Input | Refusal |
|---|---|---|
| API `PUT /settings/capture` | `tool_lock` | `SettingsPutIn` gives 422 for `"false"`, `0`, `1` and an extra key. The service refuses `null` with today's `ValidationError`, which `DOMAIN_HTTP_MAP` answers with 422 and which names the key only |
| MCP `avkit_settings` set, namespace `capture` | `tool_lock` | the strict input schema refuses a string, a number and an unknown key; the API then applies its own rules |
| Settings read-back | the stored value, which another writer or a hand edit of the database can change | `_decode` reads `True` only from `"true"`; `readToolLock` reads `false` only from `false` (AC-143.3, AC-143.6, AC-143.7) |
| Keyboard | a letter, a modifier | not a trust boundary. FIELD_GUARD keeps letters out of fields, and MODAL_GUARD keeps them out of modals |
| GUI | the Lock button, the pointer | not a trust boundary; the server refuses what the client lets through |

**Input matrix (Session 64 RULE-1).** First, each letter against the crop state and the focus:

| Letter | Crop closed, surface focused | Crop closed, a field focused | Crop open, surface focused | Crop open, a crop field focused | No shot | A text draft open | A confirm or the transform dialog open |
|---|---|---|---|---|---|---|---|
| V A R H T E | arms its tool (AC-143.16) | types into the field (AC-143.18) | nothing, no `preventDefault` (AC-143.20) | types (AC-143.18) | nothing (AC-143.17) | types into the draft (AC-143.18) | nothing (AC-143.20) |
| X | arms Redact; the crop stays closed (AC-143.19) | types (AC-143.18) | swaps the aspect once; Redact stays unarmed (AC-143.19) | types (AC-143.18) | nothing | types | nothing |
| C | opens the crop (AC-143.16) | types | nothing; the crop stays open (AC-143.20) | types | nothing | types | nothing |

"A field" covers each kind in §Word meanings. AC-143.18 types the eight letters into the text draft, the hex field, the Stroke, Size and Block size inputs, the named menu and the palette search.

Then each modifier against each tool:

| Modifier | Box, Highlight, Redact Solid, Redact Pixelate, Smart eraser (draw) | Arrow (draw) | Arrow (endpoint drag) | A box mark (corner resize) | A box mark (edge resize) | Text, a move | A selected mark (arrow key) |
|---|---|---|---|---|---|---|---|
| Shift | square (AC-143.23) | snaps to 45° (AC-143.25) | snaps to 45° about the fixed end (AC-143.25) | keeps the ratio (AC-143.24) | ignored (AC-143.24) | ignored (AC-143.26) | nudges 10 px (AC-143.27) |
| Alt | from the centre (AC-143.26) | ignored (AC-143.26) | ignored | ignored | ignored | ignored (AC-143.26) | — |
| Shift+Alt | a square from the centre (AC-143.26) | snaps | snaps | keeps the ratio | ignored | ignored | — |

AC-143.23 and AC-143.26 run one parametrize id per bounded tool, five ids each.

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-143.1 | type | The exact signatures (Session 66 RULE-1):<br>• `readToolLock(data: unknown): boolean`;<br>• `saveCaptureToolLock(client: QueryClient, locked: boolean): void`;<br>• `lockSaveFailures(): number` and `subscribeLockSaveFailures(listener: () => void): () => void`;<br>• `useCaptureToolLock(): { locked: boolean; setLocked(next: boolean): void; failures: number }`;<br>• `captureLockPutSchema` (strict `{ tool_lock: boolean }`);<br>• `TOOL_LETTERS: Readonly<Record<CaptureTool, string>>`;<br>• `CAPTURE_TOOL_IDS` (8 ids);<br>• `isEditableTarget(target: EventTarget \| null): boolean` from `lib/editable-target.ts`, re-exported by `capture-import.ts`;<br>• the exported `FIELD_STEP_SHIFT === 10`;<br>• `drawBounds`, `snapArrowEnd` and `keepRatioResize` as in MODIFIERS;<br>• `SurfacePointer.altKey: boolean` | Local Canon: D-746, D-750, D-753 | passes where row 3 writes it (row 1 adds the names) |
| AC-143.2 | behaviour | LOCK_LEAF: `SETTINGS_KEY_TABLE` holds `("capture", "tool_lock")` with the default `True` after `pixelate_block_size`. `get_namespace("capture")` on a fresh store returns `tool_lock` as the `bool` `True` | Spec: 09 Lock row (on by default, persisted); Local Canon: D-744 | it is `True`, not `"true"` |
| AC-143.3 | behaviour | LOCK_DECODE (Session 53 RULE-1). `set_namespace` with `tool_lock: False` stores `"false"`, and the next read is `False`. A stored value written straight to the test database reads `False` for each of `""`, `"\x07"`, `"\ud800"` (a lone surrogate), `"TRUE"` and `"1"`, one parametrize id each, and `"true"` reads `True`. `_encode` refuses `"false"`, `0`, `1` and `None` with a `ValidationError` whose message holds the key and not the value | Local Canon: D-747 | the lone-surrogate case reads `False` and raises nothing |
| AC-143.4 | behaviour | The API:<br>• `PUT /settings/capture` with `{ "tool_lock": false }` gives 200, and a GET returns `false`;<br>• `"false"`, `0`, `1` and `null` give 422;<br>• no response body echoes a refused value;<br>• the OpenAPI document equals the regenerated committed snapshot, and against the base snapshot the only change is `tool_lock` added to `SettingsPutIn` | Local Canon: D-744 | the `"false"` case |
| AC-143.5 | behaviour | The MCP leaf: `SETTINGS_SCHEMA.namespaces.capture` lists `tool_lock` with the default `true` after `pixelate_block_size`. The set schema accepts `{ namespace: "capture", tool_lock: false }` and refuses `tool_lock: "false"` and `tool_lock: 0`. The tool's actions are unchanged | Local Canon: D-744 | the string case |
| AC-143.6 | behaviour | `readToolLock` returns:<br>• `true` for `undefined`, `null`, `{}`, `{ tool_lock: true }`, `{ tool_lock: "false" }`, `{ tool_lock: 0 }`, `{ tool_lock: "" }`, `{ tool_lock: "\uD800" }` and `{ tool_lock: "\u0007" }`;<br>• `false` only for `{ tool_lock: false }` (Session 53 RULE-1) | Local Canon: D-747 | `"false"` reads `true` |
| AC-143.7 | behaviour | LOCK_DEFAULT on the page:<br>• mounted on a GET without `tool_lock`, the lock shows `aria-pressed="true"`;<br>• on `tool_lock: false` it shows `"false"`;<br>• on `tool_lock: "\uD800"` it shows `"true"`;<br>• under Lock, a Box drag keeps Box pressed, the new box is selected, and the options row shows the box's colour | Spec: 09 Lock row | the `false` GET |
| AC-143.8 | behaviour | ONE_SHOT:<br>• a Lock click sends one PUT whose body is exactly `{ tool_lock: false }`, and the button shows `"false"` before the PUT settles;<br>• a remount on the fake's stored value shows `"false"`;<br>• with the lock off, a Box drag returns to Select with the box selected;<br>• a second click sends `{ tool_lock: true }` | Spec: 09 Lock row (one-shot preference) | the remount |
| AC-143.9 | behaviour | LOCK_STORE:<br>• **Held GET.** With the page's GET held, a Lock click shows `"false"` at once. The held GET then answers `tool_lock: true`, and the button still shows `"false"`.<br>• **Failed GET.** With the GET failing (500) and nothing committed, the button shows `"true"`. After a click whose PUT succeeds, a failing refetch still shows `"false"`.<br>• **Order.** Two clicks while the first PUT is held send the second PUT only after the first settles, and the fake receives `false` and then `true`.<br>• **Shared queue.** An `arrow_color` commit and a Lock click made while the first PUT is held go out one after the other, in commit order.<br>Each test settles every held request and calls `resetCaptureStyleStore()` | Session 71 RULE-1; Local Canon: D-746 | a PUT sent before the one ahead of it settles fails the test |
| AC-143.10 | behaviour | A failed Lock PUT (500) shows `Couldn't save the tool lock` in the status, and the status and the Console name no value. Once the queue is empty, the page refetches once, and the button shows the stored value again. A failed style PUT still shows `Couldn't save the tool style` alone | Session 50 RULE-1; Local Canon: D-746 | the status names no value |
| AC-143.11 | behaviour | ARMED_EDIT. Under Lock, with Box armed and box A just drawn and selected:<br>• a drag on A's body moves A as one undo step and adds no mark;<br>• a drag on A's corner handle resizes A;<br>• Box stays pressed throughout.<br>With Arrow armed and an arrow just drawn, a drag on its end handle moves that end. With Text armed and a text mark just committed, a drag on it moves it and opens no draft | Spec: 09 Lock row (a press on the selected mark edits it) | the mark count is unchanged after the body drag |
| AC-143.12 | behaviour | Under Lock, with Box armed and box A selected, a drag elsewhere draws box B, B becomes the selected mark, and A is unchanged. A drag that starts on an unselected earlier mark C draws a new box over C and doesn't select C | Spec: 09 Lock row (a press elsewhere draws) | C is not selected |
| AC-143.13 | behaviour | STYLE_TARGET under Lock and ARMED_RECHOOSE:<br>• after a locked arrow draw, a hex commit restyles the just-drawn arrow as one undo step and sends no `PUT /settings/capture`;<br>• a click on `capture-tool-arrow`, or the letter A, clears the selection;<br>• a hex commit then sends one PUT `{ arrow_color }`, and the next arrow has that colour;<br>• Escape after a locked draw leaves the selection | Spec: 09 Lock and Tool style rows; Local Canon: D-719, D-749 | the first commit sends no PUT |
| AC-143.14 | behaviour | LOCK_SELECTS for text: under Lock, a text commit keeps Text with the new text mark selected. A click away from it opens a new draft. With the lock off, a text commit returns to Select with the text selected | Spec: 09 Lock row | the one-shot case |
| AC-143.15 | behaviour | The orders:<br>• the registry holds the eight letter entries right after `capture:open_folder`, in CAPTURE_TOOL_IDS order, each with `page: '/capture'`, `stateful: true`, `palette: false` and its shortcut;<br>• `TOOL_LETTERS` equals `{ select: 'V', arrow: 'A', box: 'R', highlight: 'H', text: 'T', redact: 'X', eraser: 'E', crop: 'C' }`;<br>• `paletteCommands(…, '/capture', all true)` lists none of them;<br>• `BOUND_CONTROLS` holds the eight pairs after `capture-save`, in order;<br>• the toolbar's control order (the Annotation tool group, then Lock, Crop, then History) is unchanged (Sessions 59 and 63) | Local Canon: D-750 | the palette lists none |
| AC-143.16 | behaviour | LETTERS. With a shot open and the surface focused, each of V, A, R, H, T, X, E and C, one parametrize id each, has this effect:<br>• it arms its tool, and the button shows `aria-pressed="true"`; C opens the crop bar;<br>• the options row equals what a click on that button gives;<br>• with each style tool's saved colour set to a different value, the hex field shows the armed tool's own colour (STYLE_STORE, STYLE_DISPLAY);<br>• after V there is no `capture-color` element (SELECT_NO_STYLE);<br>• a mark drawn after the letter carries the tool's style (STYLE_DRAW);<br>• each letter's keydown is `defaultPrevented` | Spec: 09 Letters row; Local Canon: D-719, D-721 | after V, `capture-color` is absent |
| AC-143.17 | behaviour | LETTER_HINTS:<br>• each tool button's hint reads `Name (L)`, the eraser's reads `Smart eraser (E): Covers an area with the surrounding colour`, and the crop's reads `Crop (C)`;<br>• each button carries `aria-keyshortcuts` equal to its letter, and its accessible name is the bare name;<br>• with no shot, each hint reads `Name (L) — Select a shot first`, and a letter changes nothing and isn't `defaultPrevented` | Spec: 09 Letters row (titles name their letters); 09 Entry row (`Crop (C)`) | the no-shot letter isn't prevented |
| AC-143.18 | behaviour | FIELD_GUARD. Typing `varhtxecVARHTXEC` changes no tool, opens no crop and is not `defaultPrevented` in any of these:<br>• the open text draft, which then holds that text;<br>• the hex field, the Stroke, Size and Block size inputs, and the named menu (a focused `<select>`);<br>• the palette search, opened on the capture page.<br>From the hex field, Ctrl+S still saves and F1 still toggles help (AC-95.5) | Spec: 09 Letters row (never fire in a field) | the draft holds the typed text |
| AC-143.19 | behaviour | The crop X cases, with the surface focused:<br>• crop open on a 16:9 box: one `x` keydown swaps the aspect exactly once, giving the swapped fields and not the original (CHORD_BUBBLE_ONCE); Redact stays unarmed, and the crop bar stays;<br>• crop closed: X arms Redact, and the crop bar stays absent.<br>The existing crop X tests (`capture-crop-tool.behavior.test.ts:598-600`, `:620-622`) pass unchanged | Spec: 09 Letters row (both sides tested); Local Canon: D-752 | the swap runs once |
| AC-143.20 | behaviour | Guards on the letters:<br>• with the crop open, V, A, R, H, T, E and C change nothing, leave the crop open and aren't `defaultPrevented`;<br>• with a confirm open (an `aria-modal` dialog), every letter does nothing (MODAL_GUARD);<br>• with the transform dialog open, every letter does nothing;<br>• a held letter (`repeat`) does nothing | Local Canon: D-750; CROP_MODAL | C with the crop open |
| AC-143.21 | behaviour | Trace (Session 55 RULE-3): one `A` keydown traced through `createShortcutHandler` (a recording `getState` that returns the page's published state), the `capture:tool_arrow` action and the `capture-tool-arrow` click, to `aria-pressed="true"` and the hex field showing the arrow tool's saved `#123456`. The recording `getState` saw `capture:tool_arrow: true` | Session 55 RULE-3 | the button was clicked exactly once |
| AC-143.22 | behaviour | Trace (Session 55 RULE-3): one Lock click traced through `saveCaptureToolLock` and `captureLockPutSchema` to the recorded PUT body `{ "tool_lock": false }`. The Python half traces the API body `{ "tool_lock": false }` through `SettingsPutIn`, `SettingsService.set_namespace` (a recording wrapper), the stored `"false"` and the next GET's `false` | Session 55 RULE-3 | the wrapper records one call |
| AC-143.23 | behaviour | Shift draw, one id per bounded tool (Box, Highlight, Redact Solid, Redact Pixelate, Smart eraser) on a 100×80 shot:<br>• a Shift drag from (10, 10) to (50, 30) draws a 40×40 mark at (10, 10);<br>• a Shift drag from (90, 70) to (30, 60) draws a 60×60 square cut to what fits in the drag's direction, a 60×60 at (30, 10);<br>• `drawBounds` unit cases cover all four drag directions and a drag that leaves the image.<br>Without Shift, the same drag gives the plain box | Spec: 09 Modifiers row (Shift constrains square); Local Canon: D-753 | the plain drag |
| AC-143.24 | behaviour | Shift resize:<br>• with a 40×20 box at (10, 10) selected, a Shift drag of its bottom-right handle from (50, 30) to (70, 34) gives a 60×30 box at (10, 10): the width changed by half and the height by a fifth, so the width drives and 2:1 holds;<br>• without Shift it gives 60×24;<br>• a Shift drag of the right edge handle gives the same box as without Shift;<br>• `keepRatioResize` unit cases cover the four corners and a corner pulled past the image edge | Spec: 09 Modifiers row (aspect); Local Canon: D-753 | the edge handle ignores Shift |
| AC-143.25 | behaviour | Shift arrow:<br>• a Shift arrow drag from (10, 10) to (50, 22) ends at (52, 10), on the horizontal, with its length of 41.76 rounded;<br>• a drag to (40, 38) ends on the 45° line;<br>• a Shift drag of a selected arrow's end snaps about the fixed end;<br>• `snapArrowEnd` unit cases cover the eight directions and an end that leaves the image, which is shortened along its angle and stays inside | Spec: 09 Modifiers row (45 degrees); Local Canon: D-753 | the end stays inside the image |
| AC-143.26 | behaviour | Alt draw, one id per bounded tool:<br>• an Alt drag from (30, 30) to (40, 35) draws a 20×10 mark at (20, 25);<br>• Shift+Alt from (30, 30) to (40, 35) draws a 20×20 square at (20, 20);<br>• an Alt drag from (5, 5) to (20, 10) keeps the centre (5, 5) and cuts the half-extents to 5 and 5.<br>An Alt arrow drag and an Alt text click behave as without Alt, and so does a Shift or Alt move | Spec: 09 Modifiers row (Alt from the centre); Local Canon: D-753 | the arrow ignores Alt |
| AC-143.27 | behaviour | SHIFT_NUDGE:<br>• with a mark selected, Shift+ArrowRight moves it 10 px and ArrowRight 1 px;<br>• a burst of Shift+ArrowRight keydowns is one undo step;<br>• a Shift nudge at the image edge clamps;<br>• with the crop open, Shift+ArrowRight moves the crop by `CROP_NUDGE_SHIFT_PX`, as today;<br>• the page imports the 10 from `FIELD_STEP_SHIFT` | Spec: 09 Modifiers row (Shift+arrow 10 px); Local Canon: D-675 | the plain nudge stays 1 px |
| AC-143.28 | behaviour | ALT_NO_MENU:<br>• during a bounded-tool drag, the Alt `keydown` and `keyup` on the surface are `defaultPrevented`;<br>• after an Alt drag ends, the first Alt `keyup` is `defaultPrevented`;<br>• an Alt `keydown` and `keyup` with no gesture before them are not | Local Canon: D-754 | the plain Alt isn't prevented |
| AC-143.29 | behaviour | Electron, on a seam without `tool_lock`:<br>• Lock shows `aria-pressed="true"` at load;<br>• R on the focused surface arms Box;<br>• a box drag keeps Box pressed with the new box selected;<br>• an Alt drag draws a second box, then V arms Select (ALT_NO_MENU);<br>• typing `a` into the hex field changes no tool;<br>• a Lock click sends one `PUT /settings/capture` holding `tool_lock: false`.<br>Every locator is checked with `toBeVisible()` before it is clicked | Spec: 09 Lock, Letters and Modifiers rows | V arms Select after the Alt drag |
| AC-143.30 | behaviour | The Settings card. After a Lock PUT, the Capture card's unsaved edit stays, and its Save sends a body with exactly today's seven keys. A GET after it still returns `tool_lock` | Session 55 RULE-1 (the settings store's callers); Local Canon: D-745 | the card body has no `tool_lock` |
| AC-143.31 | behaviour | LOCK_HELP: the Annotation tools body holds the new sentences exactly and `(Shift+arrow by 10 px)`, and doesn't hold `The lock button keeps the current tool after each mark.` | Spec: 09 Lock, Letters and Modifiers rows | the old sentence is absent |
| AC-143.32 | check | FLOW_ACTIONS_INDEX:<br>• `capture:tool_select` sits before `capture:tool_arrow`, and `capture:tool_crop` after `capture:tool_eraser`;<br>• each tool row's Trigger names its letter;<br>• `capture:tool_lock` names `PUT /settings/capture`;<br>• `capture:draw_modifiers` follows `capture:style_tool`;<br>• `gui-actions-audit.test.ts` passes | Local Canon: GUI actions index | row 5's check exits 1 before row 5 |
| AC-143.33 | guard | Unchanged behaviour:<br>• Ctrl+C (D-678), Ctrl+V, Ctrl+Z and Ctrl+Y, Ctrl+S, F1, Delete, Enter re-edit and Escape;<br>• the crop's Enter, Escape, arrows and Shift+arrow;<br>• MEU-85's scrubs, MEU-99's history and MEU-105's style tests;<br>• no mark type or field changes, and `clip_mark` is unchanged (D-675). | Local Canon: D-675, D-678 | — |
| AC-143.34 | guard | No letter, modifier or Lock value enters mark JSON: after a locked draw and a Shift draw, the save POST body's marks hold exactly today's keys for their type | Spec: 09 Tool style row (never mark JSON) | — |
| AC-143.35 | check | AC-60.12's title reads `typed hex, Enter`, and no test title in `ui/tests/e2e/capture-inbox.test.ts` holds `Apply,` | Session 71b prompt | row 3's check exits 1 before row 3 |
| AC-143.36 | check | FLOW_SPEC: 09's Delivered (Session 71b) note follows the Session 71 note and names AC-143.1 to AC-143.36. The Entry note names `Crop (C)`. 09 keeps CRLF | Local Canon: 09 Delivered notes | row 5's check exits 1 before row 5 |

**Guards.** These pass after rows 1, 2 and 4:
- Python: `tests/unit/test_capture_service.py`, `tests/unit/test_capture_style_settings.py`, `tests/e2e/test_api_health_settings.py`, `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_flatten.py`, `tests/e2e/test_api_capture_style.py`, `tests/e2e/test_api_js_runtime.py` (it reads `SETTINGS_KEY_TABLE`) and `tests/e2e/test_api_openapi.py`. No row edits `packages/core/src/avkit_core/domain`.
- MCP: `mcp-server/tests/capture.test.ts`, `settings-runtime.test.ts`, `tools-parity.test.ts`, `action-index.test.ts` and the `tests/audit/` suite.
- UI: `capture-toolbar.test.ts`, `capture-page.behavior.test.ts`, `capture-action-row.test.ts`, `capture-help-content.test.ts`, `capture-redact.behavior.test.ts`, `capture-crop-tool.behavior.test.ts`, `capture-text-lines.behavior.test.ts`, `capture-style-flow.behavior.test.ts`, `capture-tool-style.test.ts`, `capture-page.test.ts`, `capture-flatten.test.ts`, `common-shortcuts.test.tsx`, `command-palette.test.ts`, `icon-hints.test.ts`, `settings-path-fields.test.tsx` and `gui-actions-audit.test.ts`.

**Spec sufficiency.** Every MEU-143 rule has an AC:

| Rule | ACs |
|---|---|
| Lock: on by default, persisted | AC-143.2 to .10, .22, .29, .30 |
| Lock: one-shot preference | AC-143.8, .14 |
| Lock: the just-drawn mark stays selected | AC-143.7, .13, .14 |
| Lock: an armed press on the selected mark edits it; elsewhere draws | AC-143.11, .12 |
| Letters: V A R H T X E C as page-scoped entries | AC-143.15, .16, .21, .29 |
| Letters: never fire in a field | AC-143.18, .29 |
| Letters: C, the crop's deferred letter | AC-143.16, .17, .36 |
| Letters: X both sides | AC-143.19, .20 |
| Letters: titles name their letters | AC-143.17 |
| Modifiers: Shift square, aspect, 45° | AC-143.23 to .25 |
| Modifiers: Alt from the centre | AC-143.26, .28, .29 |
| Modifiers: Shift+arrow 10 px with `FIELD_STEP_SHIFT` | AC-143.27 |
| Docs | AC-143.31, .32, .36 |

### Files Modified

The endings come from the plan-time Python byte count. Row 0 records them again, with SHA-256, in `s71b-anchors.txt`.

| File | Endings | Rows |
|---|---|---|
| `packages/core/src/avkit_core/services/settings.py` (`LOCK_LEAF`) | CRLF | 2 |
| `packages/api/src/avkit_api/schemas/settings.py` (`LOCK_LEAF`) | CRLF | 2 |
| `openapi.committed.json` (regenerated) | as the generator writes (CRLF today) | 2 |
| `mcp-server/src/toolsets/settings.ts` (`LOCK_LEAF`) | CRLF | 2 |
| `ui/src/renderer/src/features/capture/capture-tool-lock.ts` (new, `LOCK_DECODE`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/useCaptureToolLock.ts` (new, `LOCK_STORE`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/capture-modifiers.ts` (new, `MODIFIERS`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/capture-crop.ts` (exports `largestDriving`, `drivingFromWidth` and `drivingFromHeight`; D-766) | LF | 4 |
| `ui/src/renderer/src/lib/editable-target.ts` (new, `FIELD_GUARD`) | LF | 1 |
| `ui/src/renderer/src/features/capture/capture-import.ts` (the re-export) | LF | 1 |
| `ui/src/renderer/src/features/capture/capture-style-store.ts` (`LOCK_STORE`) | LF | 1, 4 |
| `ui/src/renderer/src/features/settings/settings-schemas.ts` (`captureLockPutSchema`) | CRLF | 1 |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` (`TOOL_LETTERS`) | CRLF | 1 |
| `ui/src/renderer/src/features/capture/CaptureCropBar.tsx` (the exported `FIELD_STEP_SHIFT`) | LF | 1 |
| `ui/src/renderer/src/registry/commandRegistry.ts` (`LETTERS`) | LF | 1, 4 |
| `ui/src/renderer/src/registry/shortcuts.ts` (`LETTERS`' BOUND_CONTROLS, `FIELD_GUARD`) | LF | 4 |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` (`LETTER_HINTS`, `MODIFIERS`' `altKey`, `ALT_NO_MENU`, `ONE_SHOT`) | CRLF | 1, 4 |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` (`ONE_SHOT`, `LOCK_SELECTS`, `ARMED_EDIT`, `LETTERS`' state, `CHORD_BUBBLE_ONCE`, `MODIFIERS`, `SHIFT_NUDGE`) | CRLF | 4 |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` (`LOCK_HELP`) | CRLF | 4 |
| `tests/unit/test_capture_service.py`, `mcp-server/tests/capture.test.ts` (moved pins, with AC-105.5's loop bounded; AC-143.5 appended to the MCP file) | CRLF | 2 |
| `tests/unit/test_capture_style_settings.py` (AC-105.2's order pin) | LF | 2 |
| `tests/unit/test_capture_tool_lock.py` (new; AC-143.1 Python, .2, .3) and `tests/e2e/test_api_capture_tool_lock.py` (new; AC-143.4, .22's Python half) | LF | 2 |
| `ui/tests/unit/capture-tool-lock.test.ts` (new; AC-143.1, .6, .15, .23 to .26's unit halves) | LF | 3 |
| `ui/tests/unit/capture-tool-flow.behavior.test.ts` (new; AC-143.7 to .14, .16 to .21, .22's UI half, .23 to .28's page halves, .30, .33, .34) | LF | 3 |
| the moved pins and test fakes in §Pins that move | as each file | 3 |
| `ui/tests/e2e/capture-inbox.test.ts` (AC-87.6 moved, AC-60.12's title, AC-143.29 appended) | LF | 3 |
| `docs/build-plan/gui-actions-index.md` (`FLOW_ACTIONS_INDEX`) | CRLF | 5 |
| `docs/build-plan/09-screenshot-capture.md` (`FLOW_SPEC`) | CRLF | 5 |

Before it writes, each row measures the file's endings with Python bytes and then writes in that ending. A scratch script that edits a tracked file fails on mixed endings (Session 63 RULE-3). Every doc write ends with a check for lone CR and for a line ending that differs from the file's own (Session 70 RULE-5).

**Byte-hash guard (Session 50).** AC-51.6 and AC-81.13 hash `ui/tests/e2e/test-ids.ts` up to `// MEU-51 primitive harness IDs.` (`:292`). This plan adds no test id: the Lock, the tool buttons, the crop bar and the status line all exist. So `test-ids.ts` and `layout-primitives` don't change. If a row finds it needs an id, the id goes after the MEU-105 block (`:519-520`), and the row records a departure. The session gate still runs `ui/tests/unit/capture-action-row.test.ts` on its own, and the handoff names the hash it reads.

### Project files

These project files are written:
- `.agent/context/meu-status.yaml` (LF), `.agent/context/meu-registry.md` (LF) and `docs/BUILD_PLAN.md` (LF), at H2, through `meu_status.py`;
- the grouping file (CRLF): row 47b (`:126`) becomes `executed (Session 71b)` with this plan folder;
- the handoff, the two rolling reviews and the reflection;
- `docs/execution/metrics.md` (CRLF) and `.agent/context/current-focus.md` (CRLF);
- `C:/Temp/av-kit/session-72-prompt.md` (Session 72 `capture-shapes-steps`, MEU-106 and MEU-107);
- this folder's plan, task and scripts.

## Out of Scope

| Item | Basis |
|---|---|
| Escape returning to Select (A-10's other half) | 09's Lock row doesn't name it. V does the same in one key, and Escape keeps today's cancel role (D-749) |
| The Lock preference on the Settings page | D-745: the toolbar button is its control |
| A letter for Lock, Undo or the Redact mode | 09's Letters row names eight tools only |
| Matching letters on non-Latin layouts | `chordFromEvent` reads `event.key`. A layout whose letter key gives another character doesn't match, as with every registry chord today |
| Shift or Alt on the text tool, a move, or an edge resize | D-753 |
| Ctrl+C and Ctrl+V | D-678: they stay on the page key handler |
| Any mark type, mark field, sidecar or bake change | D-675; AC-143.33, AC-143.34 |
| The band mismatch between the grouping (P3) and `meu-status.yaml` (P2) | asked once at the gate (D-756); this plan changes neither |
| Members-only URLs or ids, `npm run dist`, the live MCP audit | Session 71b prompt |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at baseline and after H2-2. MEU-143 is `pending` (`meu-status.yaml:3750`), with MEU-87, MEU-99, MEU-100 and MEU-105 `approved` (`C:/Temp/av-kit/s71b-prereq-status.txt`). H2 sets it to `approved` through `meu_status.py` after Codex approves.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. **Rulings (S9).** Checks that this plan's single `> **Status:**` line carries the execute words with a `USER_EXPLICIT` quote, and stops if not.
2. **Queue (S8).** Checks:
   - MEU-87, MEU-99, MEU-100 and MEU-105 are `approved`;
   - MEU-143, MEU-106 and MEU-107 are `pending`;
   - `42f02bc` is an ancestor of `HEAD`.
3. **Shapes (S7, Session 61 RULE-3).** Checks by name the shapes this plan relies on:
   - `SettingSpec`, `_encode`'s boolean branch, `_decode`'s `stored == "true"` and the `pixelate_block_size` row;
   - `SettingsPutIn`'s `pixelate_block_size` leaf;
   - `SETTINGS_SCHEMA`'s capture namespace and `settingsLeaves`' `pixelate_block_size`;
   - in `capture-style-store.ts`: `LeafEntry`, `saveCaptureToolStyle`, `fetchCaptureSettings`, `committedStyleLeaves` and `resetCaptureStyleStore`;
   - `captureStylePutSchema` and `capturePutSchema`;
   - `createShortcutHandler`, its "focused element is ignored" comment, `chordFromEvent`, `BOUND_CONTROLS` and `PAGE_PRIMARY_CONTROL`;
   - `CAPTURE_PALETTE_IDS`, `SHORTCUT_ONLY_IDS`, `capture:open_folder` and `isRegistryChord`;
   - in `CapturePage.tsx`: `useState(false)` for `toolLocked`, the two `if (!toolLocked)` sites, `commitSelection`, `chooseTool`, `handleEditorKey`, `KEYBOARD_NUDGE_PX`, `CROP_NUDGE_SHIFT_PX`, `createDrawnMark` and `hitTestMarks`;
   - `SurfacePointer`'s `shiftKey`, `handledViewKeys` and `CAPTURE_CHORD_BUBBLE` in `CaptureViewport.tsx`;
   - `FIELD_STEP_SHIFT` (not exported) in `CaptureCropBar.tsx`;
   - `ratioBox` in `capture-crop.ts`, and `resizeBox` and `isBoxMark` in `capture-transform.ts`;
   - `isEditableTarget` in `capture-import.ts`;
   - `ToolbarIconButton`'s `shortcut`;
   - the lock help sentence;
   - `capture:tool_lock` in the actions index;
   - the test-ids hash boundary and the MEU-105 block;
   - 09's anchor and its Session 71 Delivered note.

   It then checks that none of the following appears in the target files, and that the eight new files don't exist:
   - the names `tool_lock`, `readToolLock`, `saveCaptureToolLock`, `lockSaveFailures`, `useCaptureToolLock`, `captureLockPutSchema`, `TOOL_LETTERS`, `CAPTURE_TOOL_IDS`, `handledEditorKeys`, `drawBounds`, `snapArrowEnd`, `keepRatioResize`, `altKey: boolean`, `capture:tool_select`, `capture:tool_crop` and `capture:draw_modifiers`;
   - the texts `Couldn't save the tool lock` and `AC-143.`.
4. **Records.** Creates `C:\Temp\av-kit\s71b\tmp`, and records:
   - `baseline.sha`;
   - `baseline-dirty.txt`, with each dirty path's porcelain line and SHA-256;
   - `s71b-anchors.txt`, with every target's endings and SHA-256.

   It hashes `docs/proposals/2026-11-10-download-logic-divergence-report.md` and never opens it.
5. **Installs.** Installs from the lock with `uv sync --frozen --offline --all-packages` and proves that both `node_modules` trees match their locks (S4).
6. **FFmpeg pair.** Checks the pinned FFmpeg pair, as the identity script binds it.
7. **Base runs.** Captures these, recorded and not fatal:
   - the base Python, UI and MCP suites;
   - the UI build;
   - the capture Electron spec;
   - `ruff check packages/ tests/`.
8. **Selftests.** Runs the `red-check.py`, `identity.py` and `id-length.py` selftests, each on its own fixtures (Session 56 RULE-4).

### 2. Type-only first, then data, then Red, then Green

**Row 1 (Session 53 RULE-2)** adds the names with no behaviour:
- `capture-tool-lock.ts`, whose stub `readToolLock` returns `false` (today's default);
- `useCaptureToolLock.ts`, a stub that returns `{ locked: false, setLocked: () => {}, failures: 0 }`, not yet called;
- in `capture-style-store.ts`: `saveCaptureToolLock`, a no-op, plus `lockSaveFailures` (returns 0) and `subscribeLockSaveFailures` (returns a no-op unsubscribe);
- `captureLockPutSchema` in `settings-schemas.ts`;
- `TOOL_LETTERS` with all eight entries, not yet read;
- `CAPTURE_TOOL_IDS` in `commandRegistry.ts`, with no entries added;
- `lib/editable-target.ts`, holding `isEditableTarget` moved unchanged, with the re-export;
- the exported `FIELD_STEP_SHIFT`;
- `capture-modifiers.ts`, whose stubs return the plain points and the plain resize;
- `SurfacePointer.altKey`, filled from the event and not yet read.

**Row 2 (data)** writes LOCK_LEAF's row, the API leaf, the regenerated OpenAPI snapshot and the MCP leaf:
- These are the data the Red tests read, so every key a Red test names exists before row 3 (Session 69 RULE-4).
- The Python and MCP Lock tests that row 2 adds pass there, as guards.
- Four key-set pins would fail on the new key, so row 2 moves them with the data: AC-36.12 (`test_capture_service.py`), AC-38.6 (`mcp-server/tests/capture.test.ts`), AC-105.2's order pin (`test_capture_style_settings.py:46-50`) and AC-105.5's style loop (`capture.test.ts:1732`).
- It adds AC-143.2 to .5 and the Python half of .22, which have to pass there.
- Row 2 is not a Green row, so S2 doesn't apply to it.

**Row 3 (Red)** edits the moved pins and the test fakes, and requires only new-behaviour tests (Session 66 RULE-2):
- Vitest (UI): AC-143.6 to .21, the UI half of .22, .23 to .28, .31 and the rewritten AC-87.2 to .5 and .7. For example, AC-143.7 fails at Red because the stub `readToolLock` gives `false`, and AC-143.19's inverse case fails because X isn't bound yet.
- Playwright: AC-143.29 and the rewritten AC-87.6.
- The check AC-143.35, which row 3 itself makes pass by renaming AC-60.12's title.

These are not in the Red list:
- AC-143.1 tests what rows 1 and 2 add, so it must pass where it is written.
- AC-143.2 to .5 and the Python half of .22 test row 2's data, and pass where they are written.
- AC-143.30, .33 and .34 are guards that pass throughout.
- AC-143.32 and .36 are row 5's checks.

**Red-check (Session 50).** A Red row passes only when `red-check.py` reads each receipt and names each failing required test as an assertion failure. A required test that fails on a missing name is refused (the `vitest-required-ac-143-7-stub-name` fixture). Every Red test:
- asserts that a name exists before it patches or calls it (Session 52 RULE-4);
- catches an exception and asserts its type (Session 62 RULE-3);
- asserts length or membership before indexing (Session 62 RULE-3);
- finds a mark by its content, never by DOM index (Session 70 RULE-1);
- states every press on the image in image pixels, inside the image after VIEW_MAP's rounding (Session 68 RULE-3);
- in Electron, asserts `await expect(locator).toBeVisible()` before it clicks.

`id-length.py` checks every new pytest id against red-check's header width of 71 characters (Session 67 RULE-4). Row 2 runs `ruff check` on the two new pytest files (Session 68 RULE-4).

**Rows 4 and 5 (Green)** change no test file. Row 4 writes the behaviour and LOCK_HELP. Row 5 writes FLOW_ACTIONS_INDEX and FLOW_SPEC.

**Where the tests go.**
- `tests/unit/test_capture_tool_lock.py` (row 2): AC-143.1 (Python), .2 and .3.
- `tests/e2e/test_api_capture_tool_lock.py` (row 2): AC-143.4 and the Python half of .22.
- `mcp-server/tests/capture.test.ts`, appended (row 2): AC-143.5.
- `ui/tests/unit/capture-tool-lock.test.ts` (row 3): AC-143.1 (TS), .6, .15 and the unit halves of .23 to .26.
- `ui/tests/unit/capture-tool-flow.behavior.test.ts` (row 3): AC-143.7 to .14, .16 to .21, the UI half of .22, the page halves of .23 to .28, and .30, .33 and .34. It runs on its own render harness, modelled on `capture-style-flow.behavior.test.ts`, with a recording fake server for the GET, the PUT and the save POST. The registry handler is mounted through `AppShell`'s `createShortcutHandler` with the real `listCommands()`, so the letters travel the real path.
- `capture-help-content.test.ts` (row 3): AC-143.31 beside the moved AC-87.7.
- `ui/tests/e2e/capture-inbox.test.ts`, appended (row 3): AC-143.29.

### Plan-local scripts

The folder's `baseline.ps1`, `red-check.py`, `identity.py`, `id-length.py` and `session-gate.ps1` are adapted from Session 71's, with the `s71b` names and this plan's paths.

| Script | What it does | Plan-time result |
|---|---|---|
| `id-length.py` | checks pytest id widths | selftest (`C:/Temp/av-kit/s71b-plan-idlen-selftest.txt`) |
| `red-check.py` | reads the Red receipts | selftest (`C:/Temp/av-kit/s71b-plan-rc-selftest.txt`), including:<br>• the AC-143.1 boundary against AC-143.7 to AC-143.21;<br>• AC-143.2 against AC-143.22;<br>• the stub-name refusal, under which a declared new name that isn't a function is refused too;<br>• the AC-143.29 launch-failure refusal |
| `identity.py` | binds the tested state | selftest (`C:/Temp/av-kit/s71b-plan-identity-selftest.txt`) |
| `baseline.ps1` | row 0 | parses. Its rulings, queue, shapes and anchors blocks ran alone (`C:/Temp/av-kit/s71b-plan-shapes-dryrun.txt`) |
| `session-gate.ps1` | H1-2 | parses; it runs nothing at plan time |

### Session gate (H1-2)

`session-gate.ps1` runs each step with its own receipt (`s71b-D6-<id>.txt`) and exit code:

| Step | Command |
|---|---|
| Identity before | `identity.py` |
| Static | pyright; `ruff check packages/ tests/`; UI typecheck and lint; `lint_task_contract.py`; the scope-paths check (S3; the MCP audit baseline is refused); the `red-check.py` selftest; `id-length.py` on the two new pytest files |
| Byte-hash guard | `npm --prefix ui run test -- tests/unit/capture-action-row.test.ts`, on its own |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s71b\tmp`; only the Python ids that the base receipt shows failing are excused); `export_openapi.py --check` (equal to the snapshot row 2 regenerated); the whole UI suite and build; the MCP typecheck, build and suite; `meu_status.py render --check`; `issue_triage.py render --check` |
| Runtime | the capture Electron spec `ui/tests/e2e/capture-inbox.test.ts` (AC-143.29, AC-87.6, AC-60.12) |
| Identity after | `identity.py`, which must equal the before value |
| Skipped with reason | `mcp-audit` (network and the installed servers); `build-record` (no release and no package build) |

The handoff copies this session's counts from the receipts (Session 63 RULE-2). Row 0 runs the base counts again, and the handoff copies them from the receipt.

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | A required Red test passes before its Green | fix the test; never weaken the Green |
| S2 | A Green row needs a test file change | stop. A moved pin goes into the handoff as a departure, and to Mat if it changes an AC (S12) |
| S3 | `HEAD` moves; or a path outside this plan and `baseline-dirty.txt` changes; or a `baseline-dirty.txt` path this plan doesn't write changes its SHA-256 | stop and ask Mat. Never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` or a `node_modules` check fails at baseline | stop and ask Mat |
| S5 | A test or row reaches YouTube or the network, writes the system clipboard, or reads any user data (the capture inbox, its sidecars, the app database or Mat's settings file) | stop |
| S6 | A raw value (a refused setting, a user's path) reaches a log, stdout, a response body, the status line or the Console | fix it in the row or ask (Session 50 RULE-1) |
| S7 | A shape this plan relies on is missing, or a new name exists at baseline | stop and re-plan |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | The Status line lacks the execute words | stop at row 0 |
| S10 | Codex is unavailable or the ledger refuses a round | Mat reviews |
| S11 | A status file is dirty from another session | copy it to `C:/Temp/av-kit/s71b/pre-status/`, byte-edit only this session's fields, and prove them with `render --check` and a diff (Session 61 RULE-5) |
| S12 | A contract or AC in this plan needs to change | record a departure before the gate. One that changes an AC goes to Mat as a Decision Brief whose do-nothing option is "record it as a departure and keep the approved text" (Session 59 RULE-3) |
| S13 | A program other than this session's holds a resource that a row needs, such as a port, a file lock or a key like ShareX's F2 | stop and ask Mat. Never stop another program (Session 57 RULE-4) |
| S14 | AC-143.29's Alt step fails in Electron: after an Alt drag, V doesn't arm Select because the window menu took focus | stop. Record both attempts and send Mat a Decision Brief: remove the default menu (`Menu.setApplicationMenu(null)`), or record a departure that drops the Alt step. The do-nothing option is the departure |
| S15 | AC-100.11 fails again in a run | record both attempts in the handoff and tell Mat |

## Decision Log

> [!WARNING]
> D-744 to D-755 are autonomous, and each lists its alternatives in `reasoning`. D-756 and D-757 record Mat's gate rulings, and are filled in when he rules. D-744 and up were free at plan time (`C:/Temp/av-kit/s71b-did-probe.txt`).
>
> Carried, and not relisted in the block:
> - D-158: human, `USER_EXPLICIT 2026-10-29 "all recommendations are accepted"`, grouping §8 `:141`;
> - D-159: autonomous, Local Canon, `:142`;
> - D-160: autonomous, Local Canon, `:143` (the plan-time probe returns it);
> - D-674 and D-675: autonomous, stage `grouping`, §9.8;
> - D-678: autonomous, stage `grouping`, §9.8;
> - D-713: human, `USER_EXPLICIT 2026-11-13 "A"`, §9.9.
>
> The reflection carries these and every id the decision probe returns (Session 54 RULE-5). The probe reads only the grouping's §8, so D-674, D-675, D-678 and D-713 are carried by hand.

```yaml
decision_log:
  - id: D-744
    stage: planning
    question: "Where does the Lock preference live?"
    resolution: autonomous
    class: two-way
    chosen: "One boolean leaf capture.tool_lock, default true, through SETTINGS_KEY_TABLE, SettingsPutIn (StrictBool), the regenerated OpenAPI snapshot and the MCP settings toolset, read through the shared capture settings query"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:981 - Lock is on by default and persisted"
      - "Session 71 D-714 and D-717 - per-tool style lives in capture leaves, and the API and MCP gain them"
      - "packages/core/src/avkit_core/services/settings.py:105 - flatten_backup is a capture boolean leaf"
    research:
      engine: none
      sources: []
    reasoning: "The tool style already lives in the capture namespace, so the Lock preference sits beside it. Browser storage lost: it isn't an app preference, it lives in one renderer profile, and an agent can't read it. Folding the lock into a style leaf lost: it isn't a style. Leaving MCP out lost: an agent would read a key it can't write. Two-way."
    human_message_reference: null
  - id: D-745
    stage: planning
    question: "What is the one-shot preference, and where is it set?"
    resolution: autonomous
    class: two-way
    chosen: "Lock off, saved; the toolbar Lock button is its only control; the Settings card doesn't show it"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:981 - on by default and persisted, with a one-shot preference"
      - "Session 71 D-714 - the toolbar is where a tool's style is set"
      - "ui/tests/unit/capture-page.behavior.test.ts:3345 - one-shot today returns to Select (AC-60.4)"
    research:
      engine: none
      sources: []
    reasoning: "The one-shot preference is today's lock-off behaviour, so saving the button's state gives it with no second control. A separate Settings toggle lost: it would be a second editor of the same leaf, with sync rules. A third mode lost: 09 names two. Two-way."
    human_message_reference: null
  - id: D-746
    stage: planning
    question: "Does the Lock leaf join STYLE_STORE's queue and filter?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: one shared queue and latest map, a saveCaptureToolLock beside saveCaptureToolStyle, its own failure counter and status Couldn't save the tool lock, and the same GET filter"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-style-store.ts - one write queue and a GET filter for every style leaf (Session 71 F1, F3)"
      - "Session 71 RULE-1 - name whether a new leaf joins the store, with held-GET and failed-GET ACs"
    research:
      engine: none
      sources: []
    reasoning: "The Lock leaf shares the capture namespace and its PUT route, so a separate queue would let a Lock PUT and a style PUT race, and a GET would put back an old Lock state, the Session 71 F3 failure. Writing it through the Settings card's save lost: that form holds seven keys and sends them together. One shared failure status lost: it would name the wrong preference. Two-way."
    human_message_reference: null
  - id: D-747
    stage: planning
    question: "How is a bad stored Lock value read back?"
    resolution: autonomous
    class: two-way
    chosen: "The server keeps _decode: only 'true' reads True, so a bad stored value reads False (one-shot); the UI reads false only from the boolean false, so a missing or wrong-typed value reads true"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/settings.py:187-189 - _decode for a boolean is stored == 'true'"
      - "Session 53 RULE-1 - lone-surrogate, control-character and empty regressions for a value read back from disk"
    research:
      engine: none
      sources: []
    reasoning: "_decode is shared by twelve boolean leaves, so changing it for one leaf would change what eleven others read. A stored value can only be corrupt through a hand edit of the database, and then one-shot is a safe reading. The UI's true-unless-false keeps the 09 default for a server that doesn't send the leaf, such as an older fixture. A per-spec decode default lost: it adds a field for one leaf. Two-way."
    human_message_reference: null
  - id: D-748
    stage: planning
    question: "Under Lock, what is selected after a mark, and what does an armed press on it do?"
    resolution: autonomous
    class: two-way
    chosen: "The just-drawn mark stays selected with the tool still armed; an armed press first hit-tests only that selected mark and edits it on a hit (move, resize, endpoint), and otherwise draws, even over another mark"
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:981 - the just-drawn mark stays selected; a press on the selected mark edits it while a press elsewhere draws"
      - "ui/src/renderer/src/features/capture/capture-hit-test.ts:226 - hitTestMarks takes the selected index and gives handles first"
    research:
      engine: none
      sources: []
    reasoning: "The rule names exactly the selected mark, so hit-testing only it keeps every other press a draw. Hit-testing every mark lost: a press on an old mark would select it instead of drawing, against 'a press elsewhere draws'. Text before the edit check lost: a press on a just-committed text would open a new draft over it. Two-way."
    human_message_reference: null
  - id: D-749
    stage: planning
    question: "Under Lock, how does the user set the armed tool's style instead of the just-drawn mark's?"
    resolution: autonomous
    class: two-way
    chosen: "Pick the tool again, by its button or its letter: chooseTool clears the selection, and STYLE_TARGET then sets the tool; Escape keeps its cancel role"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:1057-1067 - chooseTool clears the selection for any tool but Select"
      - "Session 71 D-719 - with a mark selected a control restyles only that mark"
    research:
      engine: none
      sources: []
    reasoning: "The path exists today and needs no new rule, only a test. Escape clearing the selection lost: Escape cancels a live gesture, a preview and a nudge burst, and adding a deselect would change those pins. A separate Deselect control lost: no row names it. Two-way."
    human_message_reference: null
  - id: D-750
    stage: planning
    question: "How are the letters bound?"
    resolution: autonomous
    class: two-way
    chosen: "Eight page-scoped, stateful, palette:false registry entries after capture:open_folder, whose actions click the enabled tool button; the page publishes each enabled exactly when its button is enabled, the crop is closed, no text draft, transform dialog or confirm is open; TOOL_LETTERS holds the letters; BOUND_CONTROLS gains the pairs"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:982 - letters are page-scoped registry entries; tool letters are ignored under CROP_MODAL"
      - "ui/src/renderer/src/registry/commandRegistry.ts:494-509 - page:primary clicks the page's enabled button"
      - "ui/src/renderer/src/registry/shortcuts.ts:227-229 - a stateful entry that isn't enabled returns false without preventDefault"
    research:
      engine: none
      sources: []
    reasoning: "Clicking the button runs the same chooseTool, crop entry and style display a click does, so the MEU-105 contracts hold with no second path. A page key handler lost: 09 says registry entries, and the shell's MODAL_GUARD and hints come with the registry. Palette entries lost: eight tool letters would crowd the palette with commands the toolbar already shows. Two-way."
    human_message_reference: null
  - id: D-751
    stage: planning
    question: "How do letters stay out of fields?"
    resolution: autonomous
    class: two-way
    chosen: "createShortcutHandler skips a chord with no Ctrl or Alt whose key is one character, when the target passes isEditableTarget or is a select; isEditableTarget moves to lib/editable-target.ts unchanged, with a re-export"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-import.ts:132 - isEditableTarget, the paste and Ctrl+C guard (D-678)"
      - "AC-95.5 - Ctrl and F-key chords fire from fields"
    research:
      engine: none
      sources: []
    reasoning: "The guard sits where every chord passes, so a later letter on any page gets it too. A per-entry flag lost: every future letter would need it and one missed flag types a command into a field. Adding select to isEditableTarget lost: it would change the paste and Ctrl+C callers. Guarding Ctrl chords too lost: AC-95.5 keeps them firing from fields. Two-way."
    human_message_reference: null
  - id: D-752
    stage: planning
    question: "How is the double run of a bubbled surface key prevented?"
    resolution: autonomous
    class: two-way
    chosen: "handleEditorKey records each handled event in a WeakSet and returns at once for an event it has seen, as handleViewKey does"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:827-845 - handledViewKeys"
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:1341-1350 - CAPTURE_CHORD_BUBBLE lets registry chords bubble"
    research:
      engine: none
      sources: []
    reasoning: "The precedent fixes the same double path for the view keys. Stopping X's bubble at the surface lost: the registry would then never see X with the crop closed. Removing the window listener lost: it handles keys when the surface isn't focused. Two-way."
    human_message_reference: null
  - id: D-753
    stage: planning
    question: "What does each modifier do to each tool?"
    resolution: autonomous
    class: two-way
    chosen: "Shift: a square for a bounded draw (the longer side, cut to the image), the start ratio for a corner resize, a 45-degree snap that keeps the length for an arrow draw or endpoint drag; Alt: from the centre for a bounded draw only; Shift+Alt combine; Shift+arrow nudges by FIELD_STEP_SHIFT; edge handles, text and moves ignore both"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:983 - Shift constrains aspect or square and snaps arrows to 45 degrees; Alt draws from the centre; reuse FIELD_STEP_SHIFT and CROP_RATIO"
      - "ui/src/renderer/src/features/capture/capture-crop.ts:59 - ratioBox"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:977-979 - the crop's Shift keeps the start ratio"
    research:
      engine: none
      sources: []
    reasoning: "The longer side follows the pointer furthest, as the crop's Shift draw does. The shorter side lost: the box would lag behind the pointer. An edge handle under Shift lost: keeping the ratio from one edge needs a second anchor rule, and no row asks for it. Alt on an arrow lost: an arrow from its centre has no use the rows name. New constants lost: the row says to reuse the crop's. Two-way."
    human_message_reference: null
  - id: D-754
    stage: planning
    question: "How does Alt avoid opening the window menu?"
    resolution: autonomous
    class: two-way
    chosen: "preventDefault the surface's Alt keydown and keyup during a bounded draw and the first Alt keyup after it; an Electron AC proves V still arms Select after an Alt drag; if it fails, stop and brief Mat (S14)"
    source_tag: Local Canon
    precedents:
      - "ui/src/main/index.ts:481-494 - the main window sets no autoHideMenuBar, and ui/src/main calls no setApplicationMenu and handles no before-input-event, so Electron's default menu is present (plan-time read)"
    research:
      engine: none
      sources: []
    reasoning: "Windows gives the menu bar focus when Alt is released alone, and the next letter would go to a menu mnemonic. Removing the application menu lost here: it changes the whole app's chrome, which is Mat's call (S14 asks). Ignoring it lost: the first letter after an Alt drag would be lost. Two-way."
    human_message_reference: null
  - id: D-755
    stage: planning
    question: "What happens to MEU-87's lock tests?"
    resolution: autonomous
    class: two-way
    chosen: "AC-87.2 to AC-87.7 are rewritten in row 3 to the Lock row (on at load, the just-drawn mark selected, the new help sentence); AC-87.1 holds; the other capture tests' fakes set tool_lock false so their draws still return to Select"
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:981 - the Lock row (C-6, D-2) changes the default and the selection"
      - "ui/tests/unit/capture-page.behavior.test.ts:3292-3410 - AC-87.2 to AC-87.5"
    research:
      engine: none
      sources: []
    reasoning: "09's Lock row is the approved contract and AC-87 pinned the earlier one, so the pins move with it. Keeping AC-87 lost: the Lock row would not hold. Changing every other test to expect Lock behaviour lost: most draw once and check something else, and one-shot keeps their meaning. Flagged at the gate. Two-way."
    human_message_reference: null
  - id: D-756
    stage: planning
    question: "Which band do MEU-143 and the grouping row 47b take?"
    resolution: human
    class: two-way
    chosen: "P2 in both: the grouping's §3 heading and tracker row 47b change to P2 at row 6; meu-status.yaml keeps P2"
    recommendation: "P2 in both: meu-status.yaml drives the queue and the build plan, so the grouping row follows it"
    source_tag: Human-approved
    precedents:
      - "Session 71b prompt - name the mismatch, change neither, ask once at the gate"
      - "Session 71 D-725 - MEU-143 copied MEU-105's pair, P2 and P3"
    research:
      engine: none
      sources: []
    reasoning: "Mat chose the recommendation through the HDP at the plan gate. The do-nothing option, leaving both as they are, and P3 in both were not chosen. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'P2 in both (Recommended)'"
  - id: D-757
    stage: planning
    question: "Does execution start?"
    resolution: human
    class: two-way
    chosen: "Execute now, with the repository's round cap of 6 and no token budget"
    recommendation: "Execute now, with the repository's round cap of 6 and no token budget"
    source_tag: Human-approved
    precedents:
      - "GUARDRAILS.md SIGN 3 - direct human execution authorization satisfies the plan-to-execution gate"
      - ".agent/review-limits.json - token_budgets off, execution rounds 6"
    research:
      engine: none
      sources: []
    reasoning: "Mat said to execute at the plan gate after the round 2 approval, having seen the gate flags D-745, D-748, D-751, D-753 and D-755 and the execution estimate of about 25M. The do-nothing option, not executing, was not chosen. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'Execute now (Recommended)'"
  - id: D-758
    stage: execution
    question: "Where does a clamp stop at the image edge in drawBounds, snapArrowEnd and keepRatioResize?"
    resolution: autonomous
    class: two-way
    chosen: "Image points are clamped to [0, W-1] and [0, H-1], so a box that runs off the right edge ends at the last pixel column (AC-143.23 [80, 10, 19, 19], AC-143.24 68x34, AC-143.25 x = 99)"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-fit-map.ts:55-60 - clampImagePoint stops a point at imageW - 1 and imageH - 1"
      - "ui/tests/unit/capture-tool-lock.test.ts:208-268 - AC-143.23 to AC-143.25"
    research:
      engine: none
      sources: []
    reasoning: "The plan's cases named the edge but not which side of the last pixel. Clamping to W lost: today's draw path stops at W-1, and the modifier helpers must give the same box as a plain drag that reaches the edge. Two-way."
    human_message_reference: null
  - id: D-759
    stage: execution
    question: "Which keepRatioResize cases does AC-143.24 pin?"
    resolution: autonomous
    class: two-way
    chosen: "The axis with the larger relative change drives, as the crop's CROP_RATIO resize does; the four corners, a height-driven se case and a past-the-edge case keep 2:1, and the e handle resizes plainly"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-crop.ts:166-169 - resizeCrop with a ratio is driven by the larger relative change"
      - "ui/tests/unit/capture-tool-lock.test.ts:226-245 - AC-143.24"
    research:
      engine: none
      sources: []
    reasoning: "The plan said to reuse CROP_RATIO's rule, and two of the drafted cases had been worked by the larger absolute change. Using the absolute change lost: a mark and a crop would keep their ratio differently under the same drag. Two-way."
    human_message_reference: null
  - id: D-760
    stage: execution
    question: "How does AC-143.20 test that a modal blocks the letters when today's page has no transform dialog?"
    resolution: autonomous
    class: two-way
    chosen: "The test mounts an aria-modal element with focus inside it and checks that no letter changes the tool; the guard keys on aria-modal, not on a named dialog"
    source_tag: Local Canon
    precedents:
      - "ui/tests/unit/capture-tool-flow.behavior.test.ts:1091-1093 - the stand-in"
      - "implementation-plan.md FIELD_GUARD - a modal blocks the letters"
    research:
      engine: none
      sources: []
    reasoning: "The transform dialog the plan names comes with a later MEU. Waiting for it lost: the guard would ship untested. Testing a named testid lost: it would not exist. Two-way."
    human_message_reference: null
  - id: D-761
    stage: execution
    question: "How does the flow harness see a failed or held settings read?"
    resolution: autonomous
    class: two-way
    chosen: "The harness sets retry false on CAPTURE_SETTINGS_KEY and resets the defaults after each test, so a failed GET settles at once"
    source_tag: Local Canon
    precedents:
      - "ui/tests/unit/capture-tool-flow.behavior.test.ts:433 - setQueryDefaults"
    research:
      engine: none
      sources: []
    reasoning: "React Query retries a failed read three times with back-off, so the failed-read cases waited past the test timeout. Fake timers lost: they stall the pointer helpers. Test-only. Two-way."
    human_message_reference: null
  - id: D-762
    stage: execution
    question: "How do the flow tests hit a box and read marks in list order?"
    resolution: autonomous
    class: two-way
    chosen: "Test boxes are 40x20, so the centre is within the 10 px outline hit; painted() puts the selected mark, which the viewport paints first, back in its list place"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-hit-test.ts - HIT_RADIUS_CSS 10 on an outline rect"
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:943-953 - the selected mark is painted first"
    research:
      engine: none
      sources: []
    reasoning: "A 40x40 box's centre is 20 px from its outline and misses, and the selected-first paint made the last-drawn reads pick the wrong mark. Changing the hit test or the paint order lost: both are shipped behaviour outside this MEU. Test-only. Two-way."
    human_message_reference: null
  - id: D-763
    stage: execution
    question: "How do AC-143.18 and AC-143.33 check that Ctrl+S still saves?"
    resolution: autonomous
    class: two-way
    chosen: "They count CAPTURE_EVENTS.save events and check that the key's default is prevented"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/components/layout/AppShell.tsx:189-195, 242 - AppShell bridges the save event to CAPTURE_COMMANDS.save"
    research:
      engine: none
      sources: []
    reasoning: "The page harness does not mount AppShell, so no annotate POST follows the key. Mounting AppShell lost: it brings the whole shell into a page test. The bridge itself is covered by its own tests. Test-only. Two-way."
    human_message_reference: null
  - id: D-764
    stage: execution
    question: "What about the AC-65.2 no-shot hint that LETTER_HINTS changes?"
    resolution: autonomous
    class: two-way
    chosen: "AC-65.2's negative test (capture-page.behavior.test.ts:1554-1564) now expects the hint with its letter before the reason, as LETTER_HINTS says; logged as a plan gap, since §Pins that move did not list it"
    source_tag: Spec
    precedents:
      - "implementation-plan.md LETTER_HINTS - a disabled tool's hint is 'Name (L) - reason'"
      - "implementation-plan.md §Pins that move - row 1's sweep missed this pin"
    research:
      engine: none
      sources: []
    reasoning: "The pin composes the disabled hint from the toolbar table, so it moves with LETTER_HINTS. Keeping it lost: LETTER_HINTS could not hold. The reviewer sees it as a moved pin outside the planned list. Two-way."
    human_message_reference: null
  - id: D-765
    stage: execution
    question: "Row 4 (Green) found two set-up defects in the Red flow tests. What happens to them under S2?"
    resolution: autonomous
    class: two-way
    chosen: "Fix the set-up and log a departure; no AC changes. AC-143.17's no-shot half serves an empty catalog, as AC-65.2 does, because the page selects the newest shot. AC-143.27 selects the mark again after each Undo, because Undo clears the selection, and it checks that the plain burst reached the edge"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:612-620 - the page selects the newest shot when none is selected"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:1848-1863 - undo sets selectedIndex to null"
      - "ui/tests/unit/capture-page.behavior.test.ts:1554-1557 - AC-65.2 gets its no-shot state from an empty catalog"
      - "implementation-plan.md S2 - a Green test change is a departure, and goes to Mat only if it changes an AC (S12)"
    research:
      engine: none
      sources: []
    reasoning: "With a one-shot catalog the no-shot half had a shot, so it could never pass. After Undo the nudges moved nothing, so the edge check passed without testing anything. Changing the page lost: auto-select and Undo's deselect are shipped behaviour outside this MEU. The AC wording and the expected values stay the same. Two-way."
    human_message_reference: null
  - id: D-766
    stage: execution
    question: "The H1-2 gate's scope-paths step refused capture-crop.ts. Row 4 exported three of its private helpers so keepRatioResize could share the crop's ratio math, and the plan's file list didn't name the file. What happens?"
    resolution: autonomous
    class: two-way
    chosen: "Keep the exports and add the file to the plan's file list and the gate's allowed set (S12 departure). Only the keyword export is added to largestDriving, drivingFromWidth and drivingFromHeight; no body, behaviour or AC changes"
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md MODIFIERS - keepRatioResize keeps the ratio as the crop's corner does (resizeCrop, capture-crop.ts:159-176)"
      - "implementation-plan.md S12 - a contract change is recorded as a departure before the gate; only an AC change goes to Mat"
      - "implementation-plan.md S3 - guards against other sessions' changes; this path was written by this session's row 4 at 15:10"
    research:
      engine: none
      sources: []
    reasoning: "Calling resizeCrop lost: it applies CROP_MIN_PX and measures to the image width, not the last pixel, so the AC-143 resize results would change. Copying the helpers into capture-modifiers.ts lost: two copies of the crop's ratio math could drift. The export is the smallest change that keeps one source. Two-way."
    human_message_reference: null
```

## Research References

- No web research: every rule comes from 09, the grouping's §8 and §9, the code at `42f02bc` and the plan-time probes.

## Planning receipts

| Receipt | What it holds |
|---|---|
| `C:/Temp/av-kit/s71b-head.txt` | `HEAD` `42f02bc`, a clean tree |
| `C:/Temp/av-kit/s71b-next-queue.txt` | the queue: MEU-127, MEU-143, MEU-107 |
| `C:/Temp/av-kit/s71b-prereq-status.txt` | MEU-87, MEU-99, MEU-100 and MEU-105 `approved`; MEU-143 `pending`, P2 |
| `C:/Temp/av-kit/s71b-did-probe.txt` | D-744 and up are free |
| `C:/Temp/av-kit/s71b-ac-probe.txt` | AC-143 appears only as the reservation |
| `C:/Temp/av-kit/s71b-plan-shapes-dryrun.txt` | `baseline.ps1`'s rulings, queue, shapes and anchors blocks, run alone at `42f02bc` |
| `C:/Temp/av-kit/s71b-plan-rc-selftest.txt`, `C:/Temp/av-kit/s71b-plan-identity-selftest.txt`, `C:/Temp/av-kit/s71b-plan-idlen-selftest.txt` | the three selftests |
| `C:/Temp/av-kit/s71b-plan-decision-probe.txt` | the decision probe: the grouping alone; the plan with the grouping; the plan alone, which is refused (HDP-18); every source unchanged |
| `C:/Temp/av-kit/s71b-plan-task-lint.txt` | `lint_task_contract.py` on `task.md`, with `RECEIPTS_DIR=C:/Temp/av-kit` |

No suite or build ran at plan time.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `npm --prefix ui run typecheck`, `ui-lint`, `lint_task_contract.py`, the scope-paths check, the `red-check.py` selftest and `id-length.py`.
- **Targeted:** each row's own files. `red-check.py` reads the Red receipts.
- **Fresh full:** the session gate runs the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds and the capture Electron spec.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the pinned FFmpeg pair and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
