---
project: "2026-10-29-capture-editor-repair"
date: "2026-10-29"
source: "docs/build-plan/09-screenshot-capture.md#canvas-history-chords"
meus: ["MEU-99", "MEU-100", "MEU-101"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture editor repair: undo chords, resize handles, text re-edit (Session 43)

> **Project:** `2026-10-29-capture-editor-repair`
> **Build plan:**
> - `docs/build-plan/09-screenshot-capture.md` §Canvas history chords (`:843-855`, MEU-99)
> - `docs/build-plan/09-screenshot-capture.md` §Resize handles (`:857-870`, MEU-100)
> - `docs/build-plan/09-screenshot-capture.md` §Text re-edit and scaling (`:872-883`, MEU-101)
> - `docs/build-plan/06-gui.md` §Shortcut binding (residual) (`:1444`) and `docs/build-plan/gui-actions-index.md` (`:88-89`) are Local Canon; row 9 adds a Delivered note and two Trigger cells (D-172)
>
> **Grouping:** `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md`, Session 43 (`:66-73`), MEU table `:16-18`, decisions D-158, D-159 and D-160 (`:141-143`).
> **Synthesis:** `_inspiration/capture-annotation-tools/synthesis.md` (Human-approved, USER_EXPLICIT 2026-10-29: "all recommendations are accepted"), slices 1, 2 and 3a.
> **Known issues:** none. Mat's report ("box, pixalate, eraser and text once sized cannot be resized again") is not a regression: MEU-60 deferred resize handles (09 `:390`, Human-approved 2026-09-20). MEU-100 is the registered home.
> **Status:** `draft`. Under `plan_to_exec_gate: human`. Mat's message of 2026-10-29 ("all recommendations are accepted, continue with @.agent/workflows/create-plan.md and execution upon review approval") is the execution message: execution starts when the Codex plan review returns `approved`, with no further pause (D-161).
>
> Line anchors are from `main` `1856df5`. The tree holds only this session's planning edits (`meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, 09, `build-priority-matrix.md`, the grouping), this plan folder and the untracked `_inspiration/` research.

## Goal

Three editor features users feel as broken are missing from the Capture page. Ctrl+Z does nothing on the canvas: Capture keeps its own history (`applyHistory`, `CapturePage.tsx:459`), and Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z are in `RESERVED_CHORDS` (`registry/shortcuts.ts:129-132`), so neither the registry nor the page binds them. A drawn box, highlight, pixelate or eraser mark can be moved but never resized: the gesture kinds are `drawing`, `moving` and `endpoint` (`CapturePage.tsx:114-127`) and `HitResult` has only arrow ends and bodies (`capture-hit-test.ts:10-12`). A committed text mark cannot be edited or scaled: the text draft only creates (`onTextCommit`, `CapturePage.tsx:1675-1698`).

1. **MEU-99 — `gui-capture-history-chords`.**
   - The inline Undo and Redo handlers become two page functions the buttons and the chords share (`HISTORY_ACTIONS`).
   - The editor key handler maps Ctrl/Meta+Z to undo and Ctrl/Meta+Y and Ctrl/Meta+Shift+Z to redo, only while the image or the page body has focus (`HISTORY_CHORDS`).
   - The Undo and Redo buttons show the chord (`HISTORY_HINTS`); the `RESERVED_CHORDS` comment, 06 and the actions index say where the chords live (`RESERVED_NOTE`, `INDEX_TRIGGER`).
2. **MEU-100 — `gui-capture-resize-handles`.**
   - A new pure module holds the handle geometry and the resize maths (`TRANSFORM`).
   - Hit-testing finds the selected mark's handles before any body (`HIT_ORDER`).
   - A new `resizing` gesture previews live and records one history step (`RESIZE_GESTURE`).
   - The viewport draws 8 handles (`RESIZE_HANDLES`) and shows a resize cursor on hover (`HOVER_CURSOR`).
3. **MEU-101 — `gui-capture-text-reedit`.**
   - Double-click or Enter reopens the text field on a committed text mark, and a commit replaces only its text (`TEXT_REEDIT`).
   - The plate's 4 corners scale `font_size` about the opposite corner (`TEXT_SCALE`).
4. Each MEU adds one sentence to the Capture help body (`HELP_TEXT`).

Order (grouping `:70`): MEU-99 → MEU-100 → MEU-101. They run in one tree because all three edit `CapturePage.tsx`'s key handler and gesture code and the help body. Row 0 records the baseline in `baseline.sha`; treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-10-29); no headroom MCP or binary. Scope is the Capture editor (features/capture CapturePage.tsx, CaptureViewport.tsx, capture-hit-test.ts, capture-text-metrics.ts, capture-help-content.ts) and one comment in registry/shortcuts.ts, read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). It stops (S1) if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md` §Claude Code; `.agent/context/harness.local.md` §Claude Code).
  - `native_shell: pwsh`. Every validation goes through `rtk proxy` with the receipt pattern `*> C:/Temp/av-kit/<receipt>.txt; $code=$LASTEXITCODE; Get-Content …; exit $code`.
  - `plan_to_exec_gate: human`. A reviewer `approved` does not start execution by itself. Here the user's explicit message already asks for execution on approval (D-161), so row 0 records it as the execution message.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every non-`shared` row keeps `compact_continue` as its fallback.
- **Cloud/local split: not used.** Mat's Windows host is both the driver and the target, so the gates are authoritative where they run. There is no `validate-task.sh`/`.ps1` and no `local-requests.md`. Commands are the PROFILE D6 argv (`.agent/docs/commands.md:190-210`, including the MCP ids `mcp-types`, `mcp-tests` and `mcp-build`) plus targeted file lists.
- **Working directory:** `P:/av-kit` on `main` (D-162; AGENTS.md "No branches or worktrees"). No other session is open on `main`; the 2026-10-17 grouping (Sessions 40–42) is fully approved. This session runs alone: row 0 and the gate stop (S8) if `HEAD` moves or another session's paths appear in the tree. Row 0 still runs `uv sync --frozen --all-packages`, `npm --prefix ui ci` and `npm --prefix mcp-server ci`.
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`; `.agent/skills/cli-dispatch/SKILL.md`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`. Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable, or the review ledger refuses a round on its token budget (exit 9), Mat is the fallback (PROFILE B3/B4; S7). Self-review is never allowed.
- **Never:** commit, push, upload, publish, or write to YouTube; author an `approved` verdict; send secrets to a provider.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-99` | `.agent/context/handoffs/2026-10-29-capture-editor-repair-MEU-99-handoff.md` |
| `MEU-100` | `.agent/context/handoffs/2026-10-29-capture-editor-repair-MEU-100-handoff.md` |
| `MEU-101` | `.agent/context/handoffs/2026-10-29-capture-editor-repair-MEU-101-handoff.md` |

Plan-local tooling (project artifacts, not product):

- [session-gate.ps1](session-gate.ps1) (rows 8 and H1-2)
- [identity.py](identity.py) (input identity, H1-6b)
- [red-check.py](red-check.py) (Red proof, rows 2, 4 and 6)

Rolling reviews:

- `.agent/context/handoffs/2026-10-29-capture-editor-repair-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-29-capture-editor-repair-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Execution message, §Baseline, §Census; `baseline.sha` |
| WP-1 | MEU-99 TDD: `HISTORY_ACTIONS`, `HISTORY_CHORDS`, `HISTORY_HINTS`, `RESERVED_NOTE`, its `HELP_TEXT` sentence (rows 2–3) | WP-0 | `shared` | tests + source; Red/Green receipts; `walkthrough.md` §MEU-99; `row3-ui-src.json` |
| WP-2 | MEU-100 TDD: `TRANSFORM`, `HIT_ORDER`, `RESIZE_GESTURE`, `RESIZE_HANDLES`, `HOVER_CURSOR`, its sentence (rows 4–5) | WP-1 | `shared` | tests + source; `walkthrough.md` §MEU-100; `row5-ui-src.json` |
| WP-3 | MEU-101 TDD: `TEXT_REEDIT`, `TEXT_SCALE`, its sentence (rows 6–7) | WP-2 | `compact_continue` | tests + source; `walkthrough.md` §MEU-101; compact, then re-read `task.md` and the walkthrough |
| WP-4 | Session gate and hub reconciliation (rows 8–9) | WP-3 | `shared` | gate receipts in `walkthrough.md` §Gate; `meu-status.yaml`, rendered `BUILD_PLAN.md`, 09/06 Delivered notes, index Trigger cells |
| WP-5 | H1 closeout, execution review, H2 | WP-4 | `compact_continue` | three handoffs, rolling review, reflection, metrics row |

---

## User Review Required

> [!IMPORTANT]
> These items are for the review loop and for Mat. They are not a pause point.
>
> 1. **Ctrl+Z is handled by the Capture page, not the registry or the menu (`HISTORY_CHORDS`, D-163).** The Electron default Edit menu keeps its undo/redo roles, and `RESERVED_CHORDS` keeps the three chords, so no registry entry can take them. The page's own key handler calls `preventDefault` before the menu accelerator runs (AC-66.13 proved this for the zoom keys). Synthesis D-1 ("revise 06 D-136") is met by documenting the exception in the `RESERVED_CHORDS` comment and a 06 Delivered note; the set itself is unchanged.
> 2. **Focus rule (`HISTORY_CHORDS`, D-164).** The chords act when focus is the page body or inside the Capture image (`annotationOwnsFocus()`), and never in an editable field, the text draft, an open confirm strip or any `aria-modal` dialog. That includes the Capture editor's non-editable controls, such as the toolbar buttons (09 "Focus": "a Capture editor control"): `annotationOwnsFocus()` accepts anything inside `capture-viewport` except the confirm strip and the `COLOR_FOCUS_IDS` controls, so Ctrl+Z after clicking Undo keeps undoing, as in other editors. A text field keeps its native undo. (Plan review round 1 F1.)
> 3. **Resize semantics (`TRANSFORM`, D-166).** The moved edges follow the pointer, clamped to the image the same way drawing clamps (`clampImagePoint`, `0..W-1`); the opposite edges never move, even when the moving edge lands on them (it then steps one pixel off, review round 1 F3); crossing over normalizes; width and height stay at least 1. Pixelate keeps its `block_size` (synthesis G-5: the domain has no block ≤ area rule).
> 4. **Hit priority (`HIT_ORDER`, D-167).** Arrow-end handles, then the selected mark's centre body handle (radius 5 CSS px), then its resize handles, then mark bodies. On a mark smaller than about 22 CSS px, the centre handle moves and the ring around it resizes.
> 5. **Text re-edit model (`TEXT_REEDIT`, D-169).** Double-click a text mark (Select tool), or press Enter with it selected and the image focused. The mark is hidden while its field is open; Enter commits as one undo step; unchanged text, an empty field or Escape keep the original and record nothing. Enter on a non-text mark does nothing.
> 6. **Text scale (`TEXT_SCALE`, D-170).** Four corner handles on the text plate scale `font_size` (1..400) about the opposite corner. No side handles until wrapped text exists (MEU-102).
> 7. **`TEST_AMENDMENTS` TA-1 and TA-2.** The Undo hint becomes `Undo (Ctrl+Z)` and the Redo hint `Redo (Ctrl+Y)`, which changes one Electron assertion (`capture-inbox.test.ts:1680`) and the AC-65.2 hint loop (`capture-page.behavior.test.ts:1506`). They are listed in advance. Any other contradiction the census finds stops execution (S2).
> 8. **Decision ids.** D-153 to D-157 are taken by committed Session 41/42 work and D-158 to D-160 by this session's grouping. This plan starts at D-161.
> 9. **Optional visual check.** At the commit gate, Mat may try Ctrl+Z, a corner drag and a text double-click in the dev app. This is non-blocking; the Electron tests are the gate.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once, here. ACs, task rows and tests refer to these names and never restate the values. All renderer paths are under `ui/src/renderer/src/features/capture/` unless another directory is named.

| Name | Definition | Source |
|---|---|---|
| `PREREQS` | Before any edit: the cwd is `P:/av-kit` on `main`; `git status --porcelain` lists nothing outside this plan folder, the `.agent/context/handoffs/2026-10-29-capture-editor-repair-` prefix, `_inspiration/` and the six planning hub files (`.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, `docs/build-plan/09-screenshot-capture.md`, `docs/build-plan/build-priority-matrix.md`, the 2026-10-29 grouping); no `graphify-out*/`; in `meu-status.yaml`, MEU-60, MEU-82, MEU-91 and MEU-97 are `approved` and MEU-99, MEU-100 and MEU-101 are `pending`; `CapturePage.tsx` contains `function handleEditorKey` and `kind: 'drawing' \| 'moving' \| 'endpoint'`, and `capture-toolbar.ts` contains `'capture-undo': { icon: Undo2, name: 'Undo' }` (the code this plan changes). | grouping `:66-73`; `meu-status.yaml` |
| `HISTORY_ACTIONS` | `CapturePage` defines `undo(): void` and `redo(): void` from the bodies of the inline `onUndo`/`onRedo` props (`CapturePage.tsx:1640-1671`), unchanged in effect: each returns if `txOpen`; `undo` returns if `past` is empty, else moves the current list to the front of `future`, sets the popped list on `annotations` and `annotationsRef`; `redo` mirrors it with `future[0]`; both then `setSelectedIndex(null)`, set `nudgeTargetRef` to `'body'` and `setPreview(null)`. `onUndo={undo}` and `onRedo={redo}`. `canUndo`/`canRedo` (`:1600-1601`) are unchanged. | Local Canon `applyHistory` |
| `HISTORY_CHORDS` | In `handleEditorKey` (`CapturePage.tsx:990`), straight after the `event.isComposing` return and before the Escape block: let `mod = (event.ctrlKey \|\| event.metaKey) && !event.altKey` and `key = event.key.toLowerCase()`. The chord is **undo** when `mod && key === 'z' && !event.shiftKey`, **redo** when `mod && ((key === 'z' && event.shiftKey) \|\| (key === 'y' && !event.shiftKey))`; anything else falls through unchanged. A chord acts only when all hold (`HISTORY_FOCUS`): `document.activeElement` is `null`, `document.body`, or satisfies `annotationOwnsFocus()` (which includes the Capture toolbar buttons and excludes only the confirm strip and `COLOR_FOCUS_IDS`, `CapturePage.tsx:95-112`; the Delete and nudge paths keep calling it unchanged); the active element is not an `input`, `textarea`, `select` or `[contenteditable]` element; `confirm === null`; and `document.querySelector('[aria-modal="true"]') === null`. When the focus rule fails, the handler returns without `preventDefault` (the field or menu keeps the key). When it holds, the handler calls `event.preventDefault()` and then returns without acting if `txOpen` or `gestureRef.current !== null`; otherwise it calls `undo()` or `redo()` (each is already a no-op with nothing to do). `event.repeat` is allowed (held Ctrl+Z steps back, as in other editors). The existing `recording \|\| textDraft !== null` early return stays first, so the text draft keeps native undo. | 09 §Canvas history chords; synthesis A-3, D-1, G-2; D-163, D-164 |
| `HISTORY_HINTS` | The Undo and Redo `ToolbarIconButton`s (`CaptureViewport.tsx:872-873`) gain `shortcut="Ctrl+Z"` and `shortcut="Ctrl+Y"`. By the existing prop (`ToolbarIconButton.tsx:34-43`) the tooltip label is `Undo (Ctrl+Z)` / `Redo (Ctrl+Y)`, `aria-keyshortcuts` is `Control+Z` / `Control+Y`, and `aria-label` stays `Undo` / `Redo`. Neither is added to `BOUND_CONTROLS` (they have no registry entry). | 06 §Common shortcuts "Hints"; D-171 |
| `RESERVED_NOTE` | The `RESERVED_CHORDS` doc comment (`registry/shortcuts.ts:125-129`) gains one sentence: "Capture handles Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z itself while its image has focus (D-163); they stay reserved so no registry entry takes them." The set's members are unchanged. Row 9 adds `> **Delivered (Session 43).**` after the Session 41 note in 06 (`:1457-1462`), in that note's format, naming the canvas chords and this plan. | synthesis D-1; D-163 |
| `INDEX_TRIGGER` | `docs/build-plan/gui-actions-index.md` `:88` Trigger cell `Undo overlay` → `Undo overlay; Ctrl+Z on the image`; `:89` `Redo overlay` → `Redo overlay; Ctrl+Y or Ctrl+Shift+Z on the image`. No other column and no registry entry changes. | 06 "Index"; D-172 |
| `HELP_TEXT` | In the `four-tools` section body of `capture-help-content.ts` (`:27`), insert straight after the edit sentence ("…Apply commits color.", held by the test constant `HELP_EDIT_SENTENCE` in `capture-help-content.test.ts:8-9`), in this order, separated by single spaces: **MEU-99** `Ctrl+Z undoes and Ctrl+Y or Ctrl+Shift+Z redoes while the image has focus; a text field keeps its own undo.` **MEU-100** `Drag a square handle on a selected box, highlight, pixelate or eraser mark to resize it.` **MEU-101** `Double-click a text mark, or press Enter with it selected, to edit its text; drag a corner of its plate to scale it.` Every other sentence, and the final range sentence (the test constant `RANGE_HELP_SENTENCE`, `:51-52`, which AC-89.8 requires last), is unchanged. The help tests declare one constant per new sentence beside `HELP_EDIT_SENTENCE`. | 09 residual "Tests" rows; D-171 |
| `TRANSFORM` | New `capture-transform.ts`, pure, no React. Exports: `type HandleId = 'nw' \| 'n' \| 'ne' \| 'e' \| 'se' \| 's' \| 'sw' \| 'w'`; `RESIZE_HANDLE_CSS = 8` (visible square side); `RESIZE_HIT_CSS = 12` (hit square side); `type BoxMark = Extract<Annotation, { type: 'rect' \| 'highlight' \| 'pixelate' \| 'eraser' }>`; `isBoxMark(mark): mark is BoxMark`. **`boxHandlePoints({ x, y, width, height }): Record<HandleId, ImagePoint>`**: corners at the box corners, edge handles at edge midpoints (`n` = `(x + width/2, y)`, `e` = `(x + width, y + height/2)`, and so on). **`resizeBox(mark, handle, point, imageW, imageH)`** returns a copy of `mark`: `p = clampImagePoint({ x: Math.round(point.x), y: Math.round(point.y) }, imageW, imageH)`; edges `L = x`, `T = y`, `R = x + width`, `B = y + height`; per axis the handle names a moving edge `M` and the opposite stationary edge `S` (`w`: `M = L`, `S = R`; `e`: `M = R`, `S = L`; `n`: `M = T`, `S = B`; `s`: `M = B`, `S = T`; an edge handle leaves the other axis untouched); `M = p.x` (or `p.y`); if `M === S` the moving edge steps one pixel off the stationary one, to `S + 1` for `e`/`s` and `S − 1` for `w`/`n`, or to the other side when that leaves `0..W-1` (`0..H-1`); then `x = min(S, M)`, `width = abs(M − S)` (likewise `y`, `height`), so the stationary edge never moves and width and height are at least 1; every other field (colour, `stroke_width`, `opacity`, `block_size`) is copied. **`hitResizeHandle(points, { cssX, cssY, scale, ox, oy }): HandleId \| null`** maps each point to CSS (`ox + x·scale`), keeps those with `abs(dx) ≤ RESIZE_HIT_CSS/2` and `abs(dy) ≤ RESIZE_HIT_CSS/2`, returns the nearest by Euclidean distance, a corner winning an exact tie with an edge; `points` may be partial (text uses 4). **`cursorForHandle(handle)`**: `nw`/`se` → `'nwse-resize'`, `ne`/`sw` → `'nesw-resize'`, `n`/`s` → `'ns-resize'`, `e`/`w` → `'ew-resize'`. MEU-101 adds `TEXT_SCALE`. | 09 §Resize handles "Handles", "Resize"; synthesis A-1, C-11; D-165, D-166 |
| `HIT_ORDER` | `HitResult` (`capture-hit-test.ts:10`) gains `{ kind: 'resize'; handle: HandleId; index: number }`. `hitTestMarks` (`:207`) keeps `inImageCss` first, then: (1) `selectedHandle` (arrow ends; the centre body handle) unchanged; (2) when the selected mark `isBoxMark`, `hitResizeHandle(boxHandlePoints(mark), …)`; when it is a text mark, `hitResizeHandle(textPlateHandlePoints(mark), …)` (MEU-101; until then text has no resize handles); a hit returns `{ kind: 'resize', handle, index: selectedIndex }`; (3) bodies, topmost first, unchanged. A resize hit is checked before `inImageCss` refuses only when the handle is inside the image box; a handle on the image edge is reachable from inside. | 09 §Resize handles "Hit order"; D-167 |
| `RESIZE_GESTURE` | `Gesture.kind` (`CapturePage.tsx:114`) gains `'resizing'` with `handle?: HandleId`. In `handleSurfacePointer` (`:565`), select-tool **down**: a `resize` hit selects the mark, sets `nudgeTargetRef` to `'body'`, calls `inspectMark`, `setTxOpen(true)` and stores `{ kind: 'resizing', handle, … }` with `origin = annotationsRef.current`. **move** past `DRAG_THRESHOLD_CSS`: `setPreview(resizeBox(origin[index], handle, imageRaw, imageW, imageH))` (text: `scaleTextMark`, MEU-101). **up**: below the threshold, nothing; otherwise the same next mark; if it differs from `origin[index]` (`JSON.stringify`), `applyHistory(replaceAt(origin, index, next))` once and `setSelectedIndex(index)`. **cancel** and **Escape** (the existing `:997-1012` block, which already clears `gestureRef`, `preview` and `txOpen`) restore with no history. `paintedAnnotations` (`:1300`) already substitutes the preview for `kind !== 'drawing'`. | 09 §Resize handles "History"; D-166 |
| `RESIZE_HANDLES` | `CaptureViewport` computes `resizePoints` from `selected` (already the painted list, so it follows the live preview): `boxHandlePoints(selected)` for a box mark, `textPlateHandlePoints(selected)` for text (MEU-101), else none. They render when `showBodyHandle` holds and `textDraft === null`, inside the aria-hidden marks svg after `capture-handle-body`, as `<rect data-testid="capture-handle-resize-<id>" data-handle="<id>">` of side `RESIZE_HANDLE_CSS / view.s` centred on the point, `fill="var(--color-bg)"`, `stroke="var(--color-accent)"`, `strokeWidth={1}`, `vectorEffect="non-scaling-stroke"`. An arrow, no selection, the annotated view or an open text draft renders none. `ui/tests/e2e/test-ids.ts` gains `// MEU-100 Capture resize handles (additive IDs).` and 8 constants `CAPTURE_HANDLE_RESIZE_NW = 'capture-handle-resize-nw'` … `_W`. | 09 §Resize handles "Handles"; D-165 |
| `HOVER_CURSOR` | `SurfacePointer` `move` already fires without a button. In `handleSurfacePointer`, a `move` with `gestureRef.current === null` and `tool === 'select'` runs `hitTestMarks` and sets `hoverHandle` (page state, `HandleId \| null`) to the hit's `handle` when `kind === 'resize'`, else `null`; this branch sits before the existing null-gesture return (`:704-707`). A `resizing` gesture's own `handle` takes precedence while it is open. `CaptureViewport` gains the prop `resizeCursor?: HandleId \| null` and appends ` cursor-nwse-resize` / ` cursor-nesw-resize` / ` cursor-ns-resize` / ` cursor-ew-resize` (from `cursorForHandle`) to the surface class; `panning` and `spaceHeld` cursors (`:760`) win over it. | 09 §Resize handles "Cursor"; D-168 |
| `TEXT_REEDIT` | `TextDraft` (`CaptureViewport.tsx:52`) gains `editIndex?: number`. `SurfacePointer.phase` gains `'dblclick'`, emitted by a new surface `onDoubleClick` through `emitSurface`. **Open:** (a) a `dblclick` in the select tool whose `hitTestMarks` result is a `body` hit on a text mark; (b) plain `Enter` (no Ctrl, Meta, Alt or Shift) in `handleEditorKey` when `annotationOwnsFocus()`, the selected mark is text, `gestureRef.current === null`, `!txOpen` and `confirm === null` — this path calls `preventDefault`. Both call `setSelectedIndex(i)` and `setTextDraft({ x: mark.x, y: mark.y, value: mark.text, editIndex: i })`. `Enter` with a non-text mark selected is inert (no `preventDefault`). **While open:** `CaptureViewport` omits `annotations[editIndex]` from `visibleMarks` and draws no handles for it; `dirty` (`:275-277`) counts an edit draft only when its value differs from the mark's text. **Commit** (`onTextCommit`): with `editIndex` set, an empty (trimmed) or unchanged value just closes the draft; otherwise `applyHistory(replaceAt(list, editIndex, { ...mark, text: value }))`, `setTextDraft(null)`, `commitSelection(editIndex, next)`. Only `text` changes. **Cancel**: closes with no history. A create draft (no `editIndex`) keeps today's behaviour. | 09 §Text re-edit "Re-edit", "Commit"; synthesis A-2; D-169 |
| `TEXT_SCALE` | `capture-transform.ts` adds `textPlateHandlePoints(mark): Partial<Record<HandleId, ImagePoint>>`, the 4 corners (`nw`, `ne`, `se`, `sw`) of `textBackgroundBox(mark)`, and `scaleTextMark(mark, handle, point, imageW, imageH)`: plate `P0 = textBackgroundBox(mark)`; anchor `A` = the corner opposite `handle`; `ratio = max(abs(p.x − A.x) / P0.width, abs(p.y − A.y) / P0.height)` with `p` the rounded point; `font_size = clamp(round(mark.font_size · ratio), 1, FONT_SCRUB_MAX)` (400); with `P1 = textBackgroundBox({ ...mark, font_size })`, `x`/`y` shift by the anchor corner's difference between `P0` and `P1` (so the anchor stays within 1 px), rounded and **not clamped**: text `x`/`y` are signed integers in the domain (`domain/capture.py:199-200`), the API (`TextAnnotationIn`, `schemas/captures.py:96-104`) and zod (`capture-annotate.ts:49-50`), and the glyph bearing puts the plate below and right of the origin, so a clamp would move the anchor (review round 1 F2). The pointer itself is clamped, so the moving corner stays on the image. The plate never flips: dragging past the anchor still grows from it. Only `x`, `y` and `font_size` change. | 09 §Text re-edit "Scale"; synthesis A-6, C-3; D-170 |
| `TEST_AMENDMENTS` | **TA-1** `ui/tests/e2e/capture-inbox.test.ts:1680`: `await expect(undoHint).toHaveText('Undo')` → `toHaveText('Undo (Ctrl+Z)')`. **TA-2** `ui/tests/unit/capture-page.behavior.test.ts:1495-1512` (AC-65.2): the hint assertion (`:1506`, `focusedHint(toolbarFocusTarget(id)`) compares against `HINT_OVERRIDE[id] ?? name`, with `const HINT_OVERRIDE: Record<string, string> = { 'capture-undo': 'Undo (Ctrl+Z)', 'capture-redo': 'Redo (Ctrl+Y)' }` declared beside `MEU65_TOOLBAR` (`:1438`); the `aria-label` assertion stays `toBe(name)`. Each changes only the lines it names. | Local Canon |
| `CENSUS_PATTERNS` | Row 1 greps `ui/tests`, `tests` and `mcp-server/tests` for: `Undo`, `Redo`, `capture-undo`, `capture-redo`, `onUndo`, `onRedo`, `canUndo`, `handleEditorKey`, `onEditorKey`, `HitResult`, `hitTestMarks`, `kind: 'body'`, `kind: 'handle'`, `TextDraft`, `textDraft`, `onTextCommit`, `capture-text-draft`, `HELP_EDIT_SENTENCE`, `CAPTURE_HELP_SECTIONS`, `cursor-grab`, `'moving'`, `RESERVED_CHORDS`, `Ctrl+Z`, `dblclick`, `onDoubleClick`, `capture-handle-`, `textBackgroundBox`, `endsWith`, `capture:undo`, `aria-keyshortcuts`, `BOUND_CONTROLS`, `focusedHint` and `MEU65_TOOLBAR`. Each hit gets a disposition: `TA-n`, `unaffected` with the reason, or `new-contradiction`, which triggers S2. Planning already classified as unaffected: `tooltip.test.tsx:134`, `:284`; `capture-toolbar.test.ts:85-86`; `shortcuts.test.ts:120`, `:138`, `:272` (the set is unchanged); `capture-hit-test.test.ts` AC-60.3 (no resize hit without a box selection); behaviour AC-60.4/5/6, AC-90.10, AC-91.9; E2E AC-87.6; `capture-action-row.test.ts:66`. | Local Canon (Session 35/40/41 census) |
| `PRODUCT_SCOPE` | The files this plan may change are exactly the Files Modified rows below plus the hub and state files; `session-gate.ps1` `scope-paths` holds the same allow-list. | grouping `:68` |

### MEU-99 — `gui-capture-history-chords`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Renderer `keydown` (surface `onKeyDown` and the page's `window` listener, both into `handleEditorKey`) | `HISTORY_CHORDS` | Ctrl/Meta + Z / Shift+Z / Y, no Alt; `isComposing` ignored | unmatched keys fall through unchanged; a chord outside `HISTORY_FOCUS` is not prevented |
| Electron default Edit menu undo/redo roles | unchanged | the renderer's `preventDefault` suppresses the accelerator (AC-66.13) | n/a |
| `RESERVED_CHORDS` | unchanged members | comment only (`RESERVED_NOTE`) | n/a |
| REST, OpenAPI, IPC, MCP | unchanged | no change | no change |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-99.1 | unit | Surface chords (`capture-page.behavior.test.ts`, the `openSelectedSurface()` harness). Draw two boxes; with focus on `capture-draw-surface`: `Ctrl+Z` leaves one mark, a second `Ctrl+Z` none; `Ctrl+Y` restores one, `Ctrl+Shift+Z` both; `Meta+Z` undoes one; a `keydown` with `repeat: true` also undoes. Each acting chord's event has `defaultPrevented === true`. `Ctrl+Alt+Z` changes nothing and is not prevented. | 09 "Chords"; `HISTORY_CHORDS` | Red on the baseline: `Ctrl+Z` leaves both marks |
| AC-99.2 | unit | Body focus: after drawing, `document.activeElement` blurred to `document.body`; `Ctrl+Z` dispatched on `window` undoes one step. | 09 "Focus"; `HISTORY_FOCUS` | Red on the baseline: nothing undone |
| AC-99.3 | unit | Guards: (a) with the text draft open, `Ctrl+Z` in `capture-text-draft` is not prevented and the marks are unchanged; (b) with `capture-font-size` focused, `Ctrl+Z` is not prevented; (c) with the delete confirm strip open (`confirm !== null`), nothing changes; (d) with `<div aria-modal="true">` in the document, nothing changes; (e) during a live `moving` gesture (pointer down, moved past the threshold, not up), `Ctrl+Z` is prevented and changes nothing, and the pointer-up still commits the move; (f) `isComposing: true` changes nothing; (g) with focus on the `capture-undo` button (a Capture editor control, 09 "Focus"), `Ctrl+Z` is prevented and undoes one step, while with focus on `capture-named-color` (a `COLOR_FOCUS_IDS` control) nothing changes and the event is not prevented; (h) with nothing to undo, `Ctrl+Z` is prevented and nothing throws. | 09 "Focus", "Guards"; D-164 | Without the guard, (a) would undo a committed mark |
| AC-99.4 | unit | Chord equals button: two equal fixtures, one driven by `Ctrl+Z, Ctrl+Z, Ctrl+Y` and one by `capture-undo, capture-undo, capture-redo` clicks, end with equal `annotations`, `selectedIndex === null`, and the same `capture-save` mount state; `saveBody()` after each gives equal POST bodies. | `HISTORY_ACTIONS` | Red on the baseline: the chord fixture's marks differ |
| AC-99.5 | unit | Hints: `capture-undo` has `aria-keyshortcuts="Control+Z"`, `aria-label="Undo"` and the focused hint `Undo (Ctrl+Z)` (`focusedHint`); `capture-redo` has `Control+Y`, `Redo`, `Redo (Ctrl+Y)`. TA-2 applies. | 06 "Hints"; `HISTORY_HINTS` | Red on the baseline: no `aria-keyshortcuts` |
| AC-99.6 | unit | Help (`capture-help-content.test.ts`): the Capture body contains `HELP_EDIT_SENTENCE + ' ' + <MEU-99 sentence>` (`HELP_TEXT`) and still ends with `RANGE_HELP_SENTENCE`. | `HELP_TEXT` | Red on the baseline: the sentence is absent |
| AC-99.7 | integration | Electron (`capture-inbox.test.ts`, the `installAnnotationStore`/`installBodyLedger` seams): on a shot, draw two boxes; set `window.__s43Marker = 1`; with the surface focused, `Ctrl+Z` gives one `[data-annotation-type="rect"]` (`expect.poll`), `Ctrl+Shift+Z` two, `Ctrl+Z` one, `Ctrl+Y` two; after blurring to the body, `Ctrl+Z` gives one. Save posts one rect. Then a text draft: type `abc`, press `Ctrl+Z` in it, and its value is shorter than `abc` (native undo) while the rect count is unchanged. Throughout: `pageZoomFactor(app)` is 1, the hash is `#/capture`, and `window.__s43Marker` is still 1 (no reload). TA-1 applies. | 09 "Tests" | Red on the baseline renderer: after `Ctrl+Z` two rects remain |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Which chords | Human-approved | Synthesis A-3, D-1 (Ctrl+Z; Ctrl+Y and Ctrl+Shift+Z) |
| Where they are bound | Local Canon / Research-backed | Page handler, not the registry or the menu; a renderer `preventDefault` suppresses a menu accelerator (AC-66.13; R-a) (D-163) |
| Focus | Human-approved / Local Canon | Synthesis A-3, G-2; `annotationOwnsFocus` (`CapturePage.tsx:96-112`) (D-164) |
| Hint form | Spec | 06 "Hints"; the `ToolbarIconButton shortcut` prop (MEU-97) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `HISTORY_ACTIONS`, `HISTORY_CHORDS` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `HISTORY_HINTS` |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | MEU-99 `HELP_TEXT` sentence |
| `ui/src/renderer/src/registry/shortcuts.ts` | modify | `RESERVED_NOTE` (comment only) |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-99.1–99.5; TA-2 |
| `ui/tests/unit/capture-help-content.test.ts` | modify | AC-99.6 |
| `ui/tests/unit/icon-hints.test.ts` | modify | TA-3 (row 8, D-177): AC-80.8's Undo/Redo hint text (EC-10) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-99.7; TA-1 |

### MEU-100 — `gui-capture-resize-handles`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Resized `rect`/`highlight`/`pixelate`/`eraser` marks | `TRANSFORM` (`resizeBox`) | integer `x`, `y`, `width ≥ 1`, `height ≥ 1`, inside `0..W-1`/`0..H-1` as drawing clamps | every other field copied unchanged |
| `HitResult` | `HIT_ORDER` | new `resize` kind with `HandleId` | existing kinds unchanged |
| Resize handles | `RESIZE_HANDLES` | editor-only svg rects, never in `annotations` | n/a |
| `POST /captures/{id}/annotate` body | existing annotation schema (unchanged) | resized marks validate as drawn ones | unchanged |
| REST, OpenAPI, IPC, MCP | unchanged | no change | no change |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-100.1 | unit | `TRANSFORM` points (`capture-transform.test.ts`, new; the module loaded by dynamic `import()` after `existsSync`): `RESIZE_HANDLE_CSS === 8`, `RESIZE_HIT_CSS === 12`; `boxHandlePoints({ x: 10, y: 20, width: 30, height: 40 })` is `nw (10,20)`, `n (25,20)`, `ne (40,20)`, `e (40,40)`, `se (40,60)`, `s (25,60)`, `sw (10,60)`, `w (10,40)`. | 09 "Handles"; D-165 | Red on the baseline: the module does not exist |
| AC-100.2 | unit | `resizeBox` per handle on `{ type: 'rect', x: 10, y: 20, width: 30, height: 40, color, stroke_width: 3 }` in a 100×100 image: `se` to (50,70) → `{10,20,40,50}`; `nw` to (5,5) → `{5,5,35,55}`; `ne` to (45,15) → `{10,15,35,45}`; `sw` to (0,65) → `{0,20,40,45}`; `n` to (99,10) → `{10,10,30,50}` (x unchanged); `e` to (60,0) → `{10,20,50,40}`; `s` to (0,80) → `{10,20,30,60}`; `w` to (20,99) → `{20,20,20,40}`. | 09 "Resize" | An `n` drag changes only `y` and `height` |
| AC-100.3 | unit | Normalize and clamp: `se` to (5,5) → `{5,5,5,15}`; `se` onto the opposite corner (10,20) → `{10,20,1,1}`; west and north collapse keep the stationary edge: `{x: 98, y: 20, width: 1, height: 40}` with `w` to (99,30) → `{98,20,1,40}` (east edge still 99), `{x: 10, y: 98, width: 30, height: 1}` with `n` to (20,99) → `{10,98,30,1}` (south edge still 99), `{x: 0, y: 20, width: 5, height: 40}` with `e` to (0,30) → `{0,20,1,40}` (west edge still 0), `{x: 10, y: 0, width: 30, height: 5}` with `s` to (20,0) → `{10,0,30,1}`; in every case `x + width ≤ 99` and `y + height ≤ 99`; `se` to (500,500) in 100×100 → `x + width === 99`, `y + height === 99`; a fractional point (40.6, 60.4) gives integers; a `pixelate` mark keeps `block_size`, a `highlight` keeps `color` and `opacity`, an `eraser` has only `type, x, y, width, height`. | 09 "Resize"; synthesis G-5; D-166 | A crossed drag never yields a negative width |
| AC-100.4 | unit | `hitResizeHandle` and `cursorForHandle`: for scale 0.5, 1, 1.5 and 2 (offset 7, 11), the CSS centre of each of the 8 points hits that handle; a point 5 CSS px off hits, 7 off does not; with `nw` and `n` both in range (a 4-image-px-wide box at scale 1), the nearer wins and an exact tie returns the corner. `cursorForHandle` maps all 8 as `TRANSFORM` states. | 09 "Handles"; D-165 | The 7 px point returns `null` |
| AC-100.5 | unit | `HIT_ORDER` (`capture-hit-test.test.ts`): a selected rect at scale 1 returns `{ kind: 'resize', handle: 'se', index }` at its `se` corner, while the same point with `selectedIndex: null` returns the body hit; with a second rect overlapping that corner on top, the selected mark's handle still wins; the centre of the selected mark returns the existing body-handle result; a selected arrow returns no `resize` kind anywhere. | 09 "Hit order"; D-167 | Unselected: no `resize` hit |
| AC-100.6 | unit | Behaviour (`capture-page.behavior.test.ts`, 8×8 image at scale 25): box tool `drag(25,25 → 100,100)` gives `{x:1,y:1,width:3,height:3}`; in Select, a drag from `capture-handle-resize-se`'s CSS point (100,100) to (150,175) commits `{1,1,5,6}` as one history step: one `capture-undo` click restores `{1,1,3,3}`, one `capture-redo` gives `{1,1,5,6}`. The same for a highlight (opacity kept), a pixelate (`block_size` kept) and an eraser. The saved body (`saveBody()`) carries the resized mark. | 09 "Resize", "History" | Red on the baseline: the drag moves the box instead |
| AC-100.7 | unit | Preview and abort: during the drag (moved, not up), the painted mark has the preview geometry and `annotations` (`saveBody` after a cancel) does not; `Escape` mid-drag restores `{1,1,3,3}` and `capture-undo` stays disabled for that step (no history); `pointercancel` does the same; a move below `DRAG_THRESHOLD_CSS` then up records nothing. | 09 "History"; `RESIZE_GESTURE` | Without the abort, Escape would leave the preview |
| AC-100.8 | unit | Handles and cursor: with a selected rect, 8 `capture-handle-resize-*` rects render, each `width` equal to `RESIZE_HANDLE_CSS / scale`; with a selected arrow, with no selection, and in the annotated view, none render. A pointer `move` with no button over `capture-handle-resize-ne` gives the surface class `cursor-nesw-resize`; over the box interior it has none; with Space held, `cursor-grab` wins. | 09 "Handles", "Cursor"; D-168 | Red on the baseline: no handle elements |
| AC-100.9 | unit | Undo integration: after a resize, `Ctrl+Z` (AC-99 chord) restores the original as the button does. | `HISTORY_CHORDS` + `RESIZE_GESTURE` | Red on the row 3 tree: no resize to undo |
| AC-100.10 | unit | Help: the Capture body contains `<MEU-99 sentence> + ' ' + <MEU-100 sentence>` and still ends with `RANGE_HELP_SENTENCE`. | `HELP_TEXT` | Red on the row 3 tree: absent |
| AC-100.11 | integration | Electron (`capture-inbox.test.ts`): draw a box image (1,1)→(4,4); in Select, `capture-handle-resize-se` is visible (`toBeVisible`); a real `page.mouse` drag from its centre to image point (6,7) gives one rect whose saved `annotations[0]` (`annotatePosts`) is `{x:1,y:1,width:5,height:6}` after Save; before Save, `Ctrl+Z` restores (1,1,3,3) as read from the `[data-annotation-type="rect"]` element's `x`, `y`, `width` and `height` attributes (`CaptureViewport.tsx:185-195`, image pixels) and `Ctrl+Y` reapplies (5,6). Hovering `capture-handle-resize-e` gives the surface computed `cursor: ew-resize`. | 09 "Tests" | Red on the row 3 tree: `capture-handle-resize-se` is not visible |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Handle count, size and hit size | Human-approved | Synthesis A-1, C-11 (8 handles, 8 px visible, 12 px hit) (D-165) |
| Resize maths | Human-approved / Local Canon | Synthesis A-1; the drawing clamp `clampImagePoint` (D-166) |
| `block_size` after resize | Human-approved | Synthesis G-5 answered: no domain rule ties block to area |
| Hit priority with the body handle | Local Canon | MEU-60 body handle kept first (D-167) |
| Hover cursor | Human-approved / Research-backed | Synthesis A-1; CSS `cursor` resize keywords (R-c) (D-168) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-transform.ts` | new | `TRANSFORM` (MEU-101 adds `TEXT_SCALE`) |
| `ui/src/renderer/src/features/capture/capture-hit-test.ts` | modify | `HIT_ORDER` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `RESIZE_GESTURE`, `HOVER_CURSOR` state |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `RESIZE_HANDLES`, `resizeCursor` prop |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | MEU-100 sentence |
| `ui/tests/unit/capture-transform.test.ts` | new | AC-100.1–100.4 |
| `ui/tests/unit/capture-hit-test.test.ts` | modify | AC-100.5 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-100.6–100.9 |
| `ui/tests/unit/capture-help-content.test.ts` | modify | AC-100.10 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-100.11 |
| `ui/tests/e2e/test-ids.ts` | modify | the 8 handle ids |

### MEU-101 — `gui-capture-text-reedit`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `TextDraft` | `TEXT_REEDIT` | optional `editIndex` (an index into `annotations` whose mark is text) | absent = create draft, unchanged behaviour |
| `SurfacePointer.phase` | `TEXT_REEDIT` | adds `'dblclick'` | other phases unchanged |
| Re-edited text mark | `TEXT_REEDIT` | only `text` changes | every other field copied |
| Scaled text mark | `TEXT_SCALE` | signed integer `x`, `y` (not clamped; the anchor plate corner stays put); `font_size` 1..400 | `text`, `color`, `bg_color` copied |
| REST, OpenAPI, IPC, MCP | unchanged | no change | no change |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-101.1 | unit | `TEXT_SCALE` maths (`capture-transform.test.ts`, `typeof` first): for `{ type: 'text', x: 10, y: 10, text: 'Hi', font_size: 16, color, bg_color: null }` in a 1000×1000 image, `textPlateHandlePoints` returns the 4 corners of `textBackgroundBox(mark)` and no edge keys; `scaleTextMark` with `se` dragged to `A + 2·(w0, h0)` gives `font_size 32` and the `nw` plate corner within 1 px of the original; dragging onto the anchor gives `font_size 1`; dragging far gives 400; `nw` dragged keeps the `se` corner within 1 px; only `x`, `y` and `font_size` differ from the input. Image edge (review round 1 F2): `{ x: 10, y: 0, text: 'Hi', font_size: 16 }` (plate `{10,6,15,12}`) with `se` dragged to (40,30) gives exactly `{ x: 10, y: -6, font_size: 32 }`, plate `{10,6,30,24}`; and for each of the four corners, a mark whose anchor plate corner is within 10 px of an image corner (100×100 image), dragged outward to the image edge, keeps the anchor plate corner within 1 px. | 09 "Scale"; D-170 | A 2× drag that kept `x`/`y` fixed would move the anchor corner |
| AC-101.2 | unit | Double-click (`capture-page.behavior.test.ts`): commit text `Hello`; in Select, a `dblclick` on it opens `capture-text-draft` with value `Hello`, the mark is not painted (no `[data-annotation-type="text"]`) and no `capture-handle-resize-*` renders; typing `Bye` and Enter commits one step: the list has one text mark `Bye` with the same `x`, `y`, `font_size`, `color` and `bg_color`; one `capture-undo` restores `Hello`. | 09 "Re-edit", "Commit"; D-169 | Red on the row 5 tree: `dblclick` opens no draft |
| AC-101.3 | unit | Enter path and no-ops: with the text mark selected and the surface focused, plain `Enter` opens the draft (prevented); committing the unchanged value records nothing (`capture-undo` disabled for it) and the mark is painted again; Escape after typing restores the original with no history; an emptied value restores the original with no history; with a rect selected, `Enter` opens nothing and is not prevented; while the draft is open, `dirty` is false for an unchanged value (`capture-save` not mounted on a clean shot). | 09 "Commit"; D-169 | Red on the row 5 tree: `Enter` opens no draft |
| AC-101.4 | unit | Corner scale: a selected text mark renders exactly 4 `capture-handle-resize-*` (`nw`, `ne`, `se`, `sw`); a drag of `se` away from the anchor raises `font_size` and records one step; `hitTestMarks` on the plate's `n` edge midpoint returns no `resize` hit. | 09 "Scale"; synthesis C-3 | Red on the row 5 tree: no text handles |
| AC-101.5 | unit | Help: the Capture body contains `<MEU-100 sentence> + ' ' + <MEU-101 sentence>` and still ends with `RANGE_HELP_SENTENCE`. | `HELP_TEXT` | Red on the row 5 tree: absent |
| AC-101.6 | integration | Electron (`capture-inbox.test.ts`): commit text `Note` at image (3,6) with Size 2; in Select, `dblclick` on it shows `capture-text-draft` with value `Note` (`toHaveValue`); fill `Done`, Enter; Save posts one text mark `Done` at (3,6) with `font_size 2`; then dragging the `se` plate handle outward and Save posts a `font_size` above 2. | 09 "Tests" | Red on the row 5 tree: no draft opens |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Re-edit triggers | Human-approved | Synthesis A-2 (double-click; Enter on a selected text mark) (D-169) |
| Commit and no-op rules | Human-approved / Local Canon | Synthesis A-2; `applyHistory` one step |
| Scale about the opposite corner | Human-approved | Synthesis A-6, C-3 (D-170) |
| Font bounds | Local Canon | 1..400: `FONT_SCRUB_MAX = 400` (`capture-scrub.ts:8`) is the Size scrub's ceiling; the renderer schema requires a positive int (`capture-annotate.ts:53`); the domain and API accept any int (`domain/capture.py:213-214`, `schemas/captures.py:104`) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-transform.ts` | modify | `TEXT_SCALE` |
| `ui/src/renderer/src/features/capture/capture-hit-test.ts` | modify | text plate corners in `HIT_ORDER` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `TEXT_REEDIT` open/commit; text branch of `RESIZE_GESTURE` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `TextDraft.editIndex`, `dblclick`, hidden mark, text handles |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | MEU-101 sentence |
| `ui/tests/unit/capture-transform.test.ts` | modify | AC-101.1 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-101.2–101.4 |
| `ui/tests/unit/capture-help-content.test.ts` | modify | AC-101.5 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-101.6 |

If a change needs a file not listed here, that is a scope change: record it as an Execution Correction Note and update the `scope-paths` allow-list in the same row (S5 otherwise).

### Hub and state files (rows 1, 9, H1-3, H2)

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | modify (planning; row 9) | Already carries the three residual sections and MEU rows from planning. Row 9 adds a `> **Delivered (Session 43).**` note after each residual table (`:855`, `:870`, `:883`) naming its ACs, the gate and this plan |
| `docs/build-plan/06-gui.md` | modify (row 9) | `RESERVED_NOTE` Delivered note after `:1462` |
| `docs/build-plan/gui-actions-index.md` | modify (row 9) | `INDEX_TRIGGER` |
| `.agent/context/meu-status.yaml` | modify (row 9, H2-2) | MEU-99/100/101 `execution_plan` and `ready_for_review` (row 9, before the H1-2 gate binds this file); `approved` after review (H2-2, which re-runs `layout-canon` and `queue-canon`) |
| `docs/BUILD_PLAN.md` | generated | AUTOGEN regions written only by `meu_status.py render` |
| `.agent/context/meu-registry.md` | generated | written by `meu_status.py render`; never hand-edited |
| `.agent/context/current-focus.md` | modify | the current focus names Session 43 (H1-3) |
| `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md` | modify (H2-2) | Session 43 row `approved` with this plan folder |
| `docs/execution/metrics.md` | modify | the Session 43 row (H2-3) |
| `docs/build-plan/build-priority-matrix.md` | none in execution | rows 9.25–9.27 were added in planning; the matrix has no status column |
| `docs/execution/plans/2026-09-26-framework-update-adoption/routing-census.md` | modify (row 8, D-175) | one `matches` entry for `.cursor/agents/av-kit-builder.md` line 4 (`7706fcd`'s pin), per Mat's ruling in `human-gate-decision.md` D-175 (EC-8); its own commit in the H2 draft |
| `ui/vitest.config.ts` | modify (row 8, D-176) | one `test.poolOptions.forks.execArgv: ['--no-experimental-webstorage']` entry with its comment, so the UI unit suite runs on Node 26 (EC-9), per Mat's ruling in `human-gate-decision.md` D-176; its own `chore(test)` commit in the H2 draft |

No `known-issues.yaml` edit: no known issue names these MEUs.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Changing the Electron application menu or adding a registry entry for undo/redo | out-of-scope | — | D-163: the page handles the chords; `RESERVED_CHORDS` stays |
| Multi-line text and wrap width | deferred | MEU-102 | Synthesis slice 3b; G-3 first |
| Side handles on text | deferred | MEU-102 (with wrap) | Synthesis C-3 |
| Rotation, aspect-lock (Shift) or centre (Alt) resize modifiers | out-of-scope | — | Not in synthesis A-1's MVP band |
| Redact, copy image, style flow, shapes, steps | deferred | MEU-103 … MEU-107 | Grouping Sessions 44–48 |
| Any REST, OpenAPI, IPC, MCP or Python change | out-of-scope | — | Marks keep their schema; resized and re-edited marks validate as drawn ones |

## BUILD_PLAN.md Audit

This project edits the D3 hub only through `meu_status.py` in row 9 (§Hub and state files). The validation is exact:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s43-state-render.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s43-state-render.txt; exit $code
```

```powershell
rtk proxy rg -n -e "MEU-99" -e "MEU-10[01]" -e "capture-editor-repair" -e "Delivered \(Session 43\)" docs/BUILD_PLAN.md docs/build-plan/09-screenshot-capture.md docs/build-plan/06-gui.md .agent/context/meu-status.yaml *> C:/Temp/av-kit/s43-hub-rg.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s43-hub-rg.txt; exit $code
```

Row 9's deliverable is that the `rg` receipt shows the three 09 Delivered notes and the 06 note, MEU-99/100/101 with `execution_plan` set to this plan, and the rendered `BUILD_PLAN.md` lines; and that `render --check` exits 0.

## Verification Plan

All commands run from `P:/av-kit` in `pwsh`, after `$env:ELECTRON_RUN_AS_NODE=$null` for any Electron step. Receipts go to `C:/Temp/av-kit/s43-*.txt`. The ids are PROFILE D6's (`.agent/docs/commands.md:190-210`); targeted runs are those argv with a file list.

### 1. Prerequisites and baseline (row 0)

- `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `npm --prefix mcp-server ci`.
- `PREREQS` (S1).
- `git rev-parse HEAD > docs/execution/plans/2026-10-29-capture-editor-repair/baseline.sha`.
- The baseline receipts: `py-tests`, `ui-tests`, `mcp-tests`, `ui-build`, then `ui-electron` over `capture-inbox.test.ts`. The baseline failed sets are recorded in `walkthrough.md` §Baseline. A test failing at baseline is never counted as a regression; a test passing at baseline that fails later is one. The Python baseline keeps the Sessions 35–42 rule for the environmental packaging tests (AC-24.10, AC-25.10, AC-25.7), each excused only if `s43-base-py.txt` shows it `FAILED`.

### 2. Red (rows 2, 4 and 6)

Each MEU's new and amended tests are written first. They must fail by assertion, or because a declared-new name does not exist yet (`red-check.py` `DECLARED_NEW`: `resizeBox`, `hitResizeHandle`, `boxHandlePoints`, `cursorForHandle`, `RESIZE_HANDLE_CSS`, `RESIZE_HIT_CSS`, `scaleTextMark`, `textPlateHandlePoints`, and the new module `capture-transform`).

- **Vitest imports of the new module are dynamic.** `capture-transform.test.ts` asserts `existsSync` on `capture-transform.ts` first, then `await import(…)` inside the test, then `expect(typeof t.resizeBox).toBe('function')` (or the name's expected type) before any call, so a missing file or export fails as an assertion instead of a load error or `TypeError: … is not a function`, which `red-check.py` refuses.
- **Behaviour tests assert presence before acting.** A test that drags a resize handle first asserts `screen.queryByTestId('capture-handle-resize-se')` is not `null` (by `expect`), so a missing handle fails as an assertion instead of a `TypeError` on a null element.
- **Electron tests assert `toBeVisible()` before acting on any new element**, and use `expect.poll` for every mark count, value or geometry after a chord or drag, so a missing behaviour fails by `expect` instead of a `locator.click: Timeout`, which is refused. The checker refuses only `Test timeout of Nms exceeded`, `TimeoutError` and `locator|page|frame|elementHandle.<action>: Timeout`, plus `ECONNREFUSED` and `EADDRINUSE`.
- **No pytest Red:** this plan changes no Python.
- **Row 2 (MEU-99):** Vitest `-t "AC-99"` over `capture-page.behavior.test.ts` and `capture-help-content.test.ts`, with TA-2 applied, then the UI build and Electron `--grep "AC-99"` over `capture-inbox.test.ts` with TA-1 applied, **on the baseline renderer**: the command refuses any `ui/src` change. AC-99.1, AC-99.2, AC-99.4, AC-99.5, AC-99.6 and AC-99.7 must fail by `expect` (`--require`). AC-99.3 is a guard set and is not required Red: the baseline satisfies most of it by doing nothing, and its (g) toolbar-focus subcase fails by assertion until Green (plan review round 2 note).
- **Row 4 (MEU-100):** Vitest `-t "AC-100"` over `capture-transform.test.ts`, `capture-hit-test.test.ts`, `capture-page.behavior.test.ts` and `capture-help-content.test.ts`, then the build and Electron `--grep "AC-100"` over `capture-inbox.test.ts`, **on the row 3 tree**. Row 3's command ends by writing `row3-ui-src.json` (a SHA-256 per file under `ui/src`); row 4 recomputes it and refuses any `ui/src` file that was added, removed or changed since. AC-100.1 to AC-100.11 must fail by `expect` (`--require`).
- **Row 6 (MEU-101):** Vitest `-t "AC-101"` over `capture-transform.test.ts`, `capture-hit-test.test.ts`, `capture-page.behavior.test.ts` and `capture-help-content.test.ts`, then the build and Electron `--grep "AC-101"` over `capture-inbox.test.ts`, **on the row 5 tree** (`row5-ui-src.json`). AC-101.1 to AC-101.6 must fail by `expect` (`--require`).

`RED_PROOF`: [red-check.py](red-check.py) decides each Red. Each Red command writes its child exit code to `<receipt>.exit` straight after `$code=$LASTEXITCODE`. The checker requires:

- a non-zero exit and exactly one failing-run summary (Vitest or Playwright);
- no hard setup failure anywhere in the receipt: an Electron launch failure, a test or action timeout, a refused connection or busy port, or Vitest unhandled errors;
- **every failure block is attributed:** the receipt is split into one block per failed test (Vitest `FAIL` headers, Playwright `N) title` headers), and the number of blocks equals the summary's failed count, so a failure that is not shown cannot hide. Every block carries at least one diagnostic, and **every** diagnostic in it is an assertion (`AssertionError`, `Error: expect(`) or a load/import error whose missing *subject* is exactly a declared-new name (or ends in one after a `.` or `/`). A `TypeError: … is not a function` is never attributed, even for a declared name. One unrelated diagnostic refuses the block, even beside a valid assertion;
- **`--require TITLE`**: each named test has its own failure block whose diagnostics are all assertions. A required test that passed, or failed only by a declared-new name, is refused. The title match is exact up to a non-digit (`AC-100.1` does not match `AC-100.10`).

Source-context and test-title lines never count. `red-check.py --selftest` runs its receipt fixtures, including the negative `vitest-not-a-function-is-unattributed` (R-2).

### 3. Targeted Green (rows 3, 5 and 7)

Each Green row runs its MEU's Vitest files plus the existing suites that pin the files it touches, then the build and the Electron spec whole. The task rows hold the exact commands.

- **Row 3:** `capture-page.behavior.test.ts`, `capture-page.test.ts`, `capture-help-content.test.ts`, `capture-toolbar.test.ts`, `tooltip.test.tsx`, `shortcuts.test.ts`, `common-shortcuts.test.tsx`; Electron `capture-inbox.test.ts`, `keyboard-shortcuts.test.ts` (TA-1 and TA-2 pass here).
- **Row 5:** `capture-transform.test.ts`, `capture-hit-test.test.ts`, `capture-page.behavior.test.ts`, `capture-page.test.ts`, `capture-help-content.test.ts`, `capture-annotate.test.ts`, `capture-text-metrics.test.ts`; Electron `capture-inbox.test.ts`.
- **Row 7:** the row 5 Vitest list; Electron `capture-inbox.test.ts`.

If a listed Vitest file does not exist, the row's census (row 1) records the replacement file name; a missing file is never silently dropped.

### 4. Session gate (rows 8, H1-2): `session-gate.ps1`

The plan-local [session-gate.ps1](session-gate.ps1) runs in `pwsh` from `P:/av-kit`. It writes one receipt per step (`C:/Temp/av-kit/s43-D6-<id>.txt`) and prints `<id> stage=<stage> exit=<n>` and the receipt tail. It is fail-fast in stage order: after the first non-zero step, every later step is printed as `not_run`. The steps, in order:

1. `identity-before`: `INPUT_IDENTITY` (§Validation stage contract).
2. **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, then `scope-paths` (`SCOPE_CHECK`, §5).
3. **Full:** `py-tests` (whole suite, with the baseline rule for the environmental packaging tests: a packaging test is excused only if it appears as `FAILED <id>` in the row 0 receipt `s43-base-py.txt`, and a missing receipt excuses nothing; the gate prints the excused ids), `ui-tests` (no excused id), `mcp-build`, `mcp-tests` (the build first, because the tests load `mcp-server/dist`), `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`.
4. **Runtime:** `ui-electron` (the full Electron suite, because the Capture key routing shares the `window` listener with `AppShell`), then `e2e-repeat`: `test:e2e -- tests/e2e/capture-inbox.test.ts --grep "AC-99|AC-100|AC-101" --repeat-each=10`. Any flake is a defect (S6).
5. `identity-npm`, then `identity-after`. The gate fails when `tested_state` differs between `identity-before` and `identity-after`.

The row's command is `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-29-capture-editor-repair/session-gate.ps1`, with the receipt pattern (task row 8).

The D6 `mcp-audit` runtime check is not a gate step: this plan changes no MCP action, schema or API; `mcp-build` and `mcp-tests` show the server still builds and passes.

### 5. `SCOPE_CHECK` (row 8)

- **`scope-paths`:** every path in `git diff --no-renames --name-only -z <baseline>` plus `git ls-files --others --exclude-standard -z` is a Files Modified row (product, test, hub and state files) or one of this project's artifacts (this plan folder, the handoffs, the reflection) or the pre-existing `_inspiration/` research (D-158). With `--no-renames`, a rename shows its source deletion as well as its destination, so a move out of a disallowed path is caught. `-z` keeps paths with spaces or non-ASCII names whole (R-4). The allow-list in the script is the union of the Files Modified tables; changing either means changing both. The step also fails when `git rev-parse HEAD` differs from `baseline.sha` (S8).

### 6. OpenAPI drift (G8)

No `packages/api/` file changes. `openapi.committed.json` is not regenerated, and the `openapi` D6 check (`--check`) must pass in the gate. H1-4 proves the committed file is unchanged since `baseline.sha`: added, removed and changed schemas are all empty (any change is S5).

### 7. Closeout (H1, H2)

These are the template commands with this project's paths:

- `validate_closeout_artifacts.py` per handoff, run twice: with `--handoff` + `--plan`, then with `--ac-coverage-only`;
- `durable_evidence.py --require-full`;
- the review-state parsers;
- the reflection validator, with `--decision-source` for the plan, the three handoffs and the 2026-10-29 grouping (no known issue);
- `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped: `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent (recorded `gui-refs-not-shipped`). Added and changed elements:

| Element | Kind | Change | Standard | E2E |
|---|---|---|---|---|
| `capture-undo`, `capture-redo` | toolbar icon button (changed) | `shortcut` → tooltip `Undo (Ctrl+Z)` / `Redo (Ctrl+Y)`, `aria-keyshortcuts` | 06 "Hints"; Tooltip (no `title`) | AC-99.7 (TA-1) |
| `capture-handle-resize-{nw,n,ne,e,se,s,sw,w}` | editor handle (new; aria-hidden svg, pointer only, like `capture-handle-body`) | 8 squares on a selected box mark; 4 corners on text | 09 §Resize handles | AC-100.11, AC-101.6 |
| `capture-draw-surface` | surface (changed) | resize cursor classes; `onDoubleClick` | 09 §Resize handles "Cursor"; §Text re-edit | AC-100.11, AC-101.6 |
| `capture-text-draft` | input (changed) | can open prefilled for an existing mark | 09 §Text re-edit | AC-101.6 |
| Capture help body | help text (changed) | three sentences | `HELP_TEXT` | — (unit AC-99.6, AC-100.10, AC-101.5) |

The resize handles are pointer affordances inside the aria-hidden marks layer, as the MEU-60 body handle is. Keyboard users already resize nothing today and keep the arrow-key nudge; a keyboard resize is not in synthesis A-1's MVP band (Out of Scope). G36 (no silent test guards): the chord, resize and re-edit tests assert; they never `skip`. G37: behaviour tests use `userEvent` for keys (`userEvent.keyboard('{Control>}z{/Control}')`) and the existing `drag` helper for pointers. G33–G35 surfaces are unchanged.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a graph directory, a cwd other than `P:/av-kit`, a branch other than `main`, a dirty tree outside the `PREREQS` paths, or a `PREREQS` status or symbol not as stated | Stop. Ask Mat, or re-run the context-tool gate. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` | Stop for the human with a Decision Brief naming the test or rule and the smallest amendment. No test edit. |
| S3 | `red-check.py` refuses a Red receipt (`RED_PROOF`, §2), or the row 4/6 tree check refuses the tree | Fix the test setup only (or revert the early product edit), then re-prove Red. |
| S4 | In Electron, Ctrl+Z, Ctrl+Y or Ctrl+Shift+Z on the focused image never reaches the renderer (the menu accelerator runs first), or the page reloads or zooms | Stop for a Decision Brief with the measurement. Option B is a renderer-owned application menu, which is Mat's call (D-163). |
| S5 | `SCOPE_CHECK` finds a path outside `PRODUCT_SCOPE`, or `openapi.committed.json` changes | Revert that change or stop with a Decision Brief. |
| S6 | An Electron flake in `--repeat-each` | Fix the test's waiting, never add retries; if the product is racy, stop with a brief. |
| S7 | Review cap (plan 3, execution 6), the reviewer is unavailable, or the review ledger refuses a round (exit 9) | HARD STOP with a TL;DR (create-plan §5d). Mat is the fallback reviewer; never bypass the ledger. |
| S8 | `HEAD` moves off `baseline.sha`, or a path another session owns appears in the tree during execution | Stop and ask Mat. Never commit, stash or revert another session's work. |

## Decision Log

Research engine for this plan: `native` (Claude Code reading of the Capture renderer source, the synthesis and the CSS/Electron documentation, 2026-10-29). Grouping §8 D-158, D-159 and D-160 carry forward unchanged into the reflection (stage `grouping`). Synthesis D-1, D-2 and D-3 are Mat's 2026-10-29 rulings in `_inspiration/capture-annotation-tools/synthesis.md`; only D-1 bears on this session. This plan's ids start at D-161 (User Review Required item 8).

```yaml
decision_log:
  - id: D-161
    stage: planning
    question: "When does execution start?"
    resolution: human
    class: two-way
    chosen: "On the Codex plan review's approved verdict, with no further pause; Mat's 2026-10-29 message is the execution message"
    source_tag: Human-approved
    precedents: ["plan_to_exec_gate: human (harness.local.md §Claude Code)", "USER_EXPLICIT 2026-10-29 'all recommendations are accepted, continue with @.agent/workflows/create-plan.md and execution upon review approval'"]
    research: { engine: none, sources: [] }
    reasoning: "The gate needs the user's explicit message, and Mat gave it in advance, tied to the reviewer's approval. A changes_required verdict still loops; only approved starts row 0. A second chat confirmation would add a pause Mat asked to skip."
  - id: D-162
    stage: planning
    question: "Where is the plan written and executed?"
    resolution: autonomous
    class: two-way
    chosen: "P:/av-kit on main; alone, with S8 guarding HEAD and foreign paths"
    source_tag: Local Canon
    precedents: ["AGENTS.md 'No branches or worktrees' (bb481ec)", "the 2026-10-17 grouping is fully approved; no other session is open"]
    research: { engine: none, sources: [] }
    reasoning: "AGENTS.md forbids branches and worktrees. A second session in the tree would mix the scope check and the identity hash, so this session stops if HEAD moves or another session's paths appear, instead of guessing which edits are whose. The open worktree P:/av-kit-wt/pill-palette-darker predates the rule and is not touched."
  - id: D-163
    stage: planning
    question: "Where are Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z bound?"
    resolution: autonomous
    class: two-way
    chosen: "HISTORY_CHORDS in CapturePage's existing handleEditorKey; the Electron menu and RESERVED_CHORDS are unchanged; the RESERVED_CHORDS comment and a 06 note record the exception"
    source_tag: Local Canon
    precedents: ["synthesis D-1 (Mat 2026-10-29): revise 06 D-136 so the canvas can use the chords", "AC-66.13: a renderer preventDefault suppresses the menu's zoom accelerators", "handleEditorKey already owns Delete, Escape and the arrow nudges (CapturePage.tsx:990-1040)"]
    research: { engine: native, sources: ["https://www.electronjs.org/docs/latest/api/menu#default-menu", "https://www.electronjs.org/docs/latest/api/web-contents#event-before-input-event"] }
    reasoning: "The history lives in CapturePage, so the page is the only place that can act on it. A registry entry would need the chord out of RESERVED_CHORDS, which would let any future page bind Ctrl+Z globally and break field undo everywhere. Replacing the default menu would drop DevTools, zoom and the edit roles for every page. The renderer sees the keydown before the menu accelerator, as AC-66.13 proved for the zoom keys, so preventDefault there is enough; S4 stops if Electron measures otherwise. D-1 asked to revise D-136: the revision is the documented exception, not a change to the reserved set."
  - id: D-164
    stage: planning
    question: "When may a history chord act?"
    resolution: autonomous
    class: two-way
    chosen: "HISTORY_FOCUS: focus on the body or inside the image (annotationOwnsFocus), not an editable field, no confirm, no aria-modal; prevent only when the focus rule holds; no-op during a transaction or gesture"
    source_tag: Human-approved
    precedents: ["synthesis A-3, G-2 (Mat 2026-10-29): chords on the canvas, never stealing a text field's undo", "annotationOwnsFocus already decides Delete and the nudges (CapturePage.tsx:96-112, :1013-1018)", "SHORTCUT_HANDLER's aria-modal guard (D-134)"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/isComposing"] }
    reasoning: "The same focus test that decides Delete keeps the editor consistent: a key acts on marks only when the user is on the marks. A field's Ctrl+Z belongs to the field. A pending confirm is a decision in progress, and undoing under it would change what it asks about. During a gesture the history is mid-step, so the chord is swallowed rather than undoing a step the drag is about to replace. annotationOwnsFocus accepts the Capture toolbar buttons (it excludes only the confirm strip and COLOR_FOCUS_IDS), which is what 09 'Focus' calls a Capture editor control, so Ctrl+Z keeps working after a toolbar click; reusing the predicate unchanged leaves MEU-60's Delete and nudge contract as it is (plan review round 1 F1)."
  - id: D-165
    stage: planning
    question: "How many handles, and what size?"
    resolution: human
    class: two-way
    chosen: "8 handles (corners and edge midpoints); 8 CSS px visible, 12 CSS px hit square, constant on screen at every zoom"
    source_tag: Human-approved
    precedents: ["synthesis A-1, C-11 (Mat 2026-10-29)", "HANDLE_RADIUS_CSS 5 / view.s keeps the body handle constant on screen (CaptureViewport.tsx:504)"]
    research: { engine: none, sources: [] }
    reasoning: "The synthesis settled the count and sizes from the surveyed tools. Dividing by the view scale, as the body handle already does, keeps them usable at every zoom."
  - id: D-166
    stage: planning
    question: "What does a resize do at the edges of the image and when it crosses over?"
    resolution: autonomous
    class: two-way
    chosen: "TRANSFORM resizeBox: round, clamp like drawing (clampImagePoint 0..W-1), move only the handle's edges, keep the stationary edge fixed (a coincident moving edge steps one pixel off it), normalize, copy every other field"
    source_tag: Local Canon
    precedents: ["createDrawnMark normalizes with min/abs over clamped points (CapturePage.tsx:152-155)", "clampImagePoint (capture-fit-map.ts:55)", "synthesis G-5: no block <= area rule, so block_size is kept"]
    research: { engine: none, sources: [] }
    reasoning: "A resized box should be one the drawing tool could have drawn, so it uses the same clamp and the same normalization; the backend then accepts it exactly as it accepts drawn marks. A minimum of 1 keeps a zero-area mark from vanishing mid-drag. Keeping block_size follows G-5."
  - id: D-167
    stage: planning
    question: "Which hit wins when handles and bodies overlap?"
    resolution: autonomous
    class: two-way
    chosen: "Arrow ends, then the selected mark's centre body handle, then its resize handles (nearest, corner on a tie), then bodies topmost first"
    source_tag: Local Canon
    precedents: ["selectedHandle runs before bodies today (capture-hit-test.ts:211-214)", "MEU-60 AC-60.4/5/6 pin the body handle"]
    research: { engine: none, sources: [] }
    reasoning: "The selected mark's controls must beat a body underneath, or a handle on top of another mark could never be grabbed. Keeping the existing centre handle first leaves MEU-60's move contract untouched; on a mark too small to separate them, the centre still moves and the ring resizes, so both stay reachable."
  - id: D-168
    stage: planning
    question: "How is the resize cursor shown?"
    resolution: autonomous
    class: two-way
    chosen: "HOVER_CURSOR: a button-less move in Select hit-tests and sets hoverHandle; the viewport adds a Tailwind cursor-*-resize class; pan and Space cursors win"
    source_tag: Research-backed
    precedents: ["surfaceCursor already switches classes for pan and Space (CaptureViewport.tsx:760)", "synthesis A-1"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/CSS/cursor"] }
    reasoning: "The handles sit in an aria-hidden, pointer-events-none svg, so CSS hover on them cannot work; the surface must hit-test the pointer as it already does for clicks. The four CSS resize keywords cover the eight handles. A class on the surface follows the existing pan cursor pattern."
  - id: D-169
    stage: planning
    question: "How is committed text edited again?"
    resolution: autonomous
    class: two-way
    chosen: "TEXT_REEDIT: TextDraft.editIndex; open by dblclick or plain Enter on a selected text mark; hide the mark while open; commit replaces only text as one step; unchanged, empty or Escape record nothing"
    source_tag: Human-approved
    precedents: ["synthesis A-2 (Mat 2026-10-29)", "the create draft and its Enter/Escape keys (CaptureViewport.tsx:1335-1362)", "onTextCommit (CapturePage.tsx:1675-1698)"]
    research: { engine: none, sources: [] }
    reasoning: "Reusing the existing draft keeps one text input, one set of keys and one commit path. Hiding the mark avoids two copies of the words on screen. An empty field restores rather than deletes: Delete already removes a mark, and an accidental clear should not lose it. Enter needs focus on the image so it never fires from the mark list or a field."
  - id: D-170
    stage: planning
    question: "How does a corner drag scale text?"
    resolution: autonomous
    class: two-way
    chosen: "TEXT_SCALE: ratio is the larger of the x and y stretch from the opposite plate corner; font_size rounds and clamps 1..400; x/y shift so the anchor corner stays within 1 px and are not clamped (text x/y are signed); no flip"
    source_tag: Human-approved
    precedents: ["synthesis A-6, C-3 (Mat 2026-10-29): corner handles scale the font", "textBackgroundBox is the plate the preview and bake share (capture-text-metrics.ts:40; AC-82.6)"]
    research: { engine: none, sources: [] }
    reasoning: "Text has no box of its own, only a font size, so a corner drag can only change the size, and the plate from textBackgroundBox is what the user sees. Taking the larger stretch follows the pointer on either axis. Shifting x/y keeps the opposite corner fixed, as a box resize does. A flip would mirror nothing for text, so dragging past the anchor just shrinks toward 1."
  - id: D-171
    stage: planning
    question: "What do the help and the hints say?"
    resolution: autonomous
    class: two-way
    chosen: "HELP_TEXT three sentences after HELP_EDIT_SENTENCE; HISTORY_HINTS Undo (Ctrl+Z) and Redo (Ctrl+Y)"
    source_tag: Spec
    precedents: ["06 'Hints'", "the help body lists every editor gesture (capture-help-content.ts:27)", "MEU-97 ToolbarIconButton shortcut prop"]
    research: { engine: none, sources: [] }
    reasoning: "Each new behaviour is invisible until the user is told, and the help body is where the editor's other gestures are listed. Placing the sentences after the edit sentence keeps the help in workflow order and leaves the range sentence last, which AC-89.8 pins. Ctrl+Y is the hint because it is the Windows convention; Ctrl+Shift+Z is in the help."
  - id: D-172
    stage: planning
    question: "How does the actions index record the chords?"
    resolution: autonomous
    class: two-way
    chosen: "INDEX_TRIGGER: the capture:undo and capture:redo Trigger cells name the chords; no registry entry"
    source_tag: Local Canon
    precedents: ["gui-actions-index.md :88-89 (Palette no, local)", "MEU-97 added chords to Trigger cells (AC-97.5)"]
    research: { engine: none, sources: [] }
    reasoning: "The index is where a reader looks up how an action is triggered. The rows are local and not palette-eligible, so only the Trigger cell changes; AC-23.18/AC-97.5 audit registry chords and are unaffected."
  - id: D-173
    stage: planning
    question: "How do the Red tests fail cleanly when the new module does not exist yet?"
    resolution: autonomous
    class: two-way
    chosen: "existsSync then dynamic import with typeof assertions; presence assertions before handle drags; toBeVisible and expect.poll in Electron"
    source_tag: Local Canon
    precedents: ["Session 41 D-149", "red-check.py fixture vitest-not-a-function-is-unattributed"]
    research: { engine: none, sources: [] }
    reasoning: "A static import of a missing module fails the whole file at load and hides every other test, so the new module is loaded after an existence assertion. A missing handle must fail by expect, not by a null dereference or a click timeout, which the checker refuses."
  - id: D-174
    stage: planning
    question: "Does the grouping's split candidate (MEU-101 as Session 43b) apply?"
    resolution: autonomous
    class: two-way
    chosen: "No split; row 6 (MEU-101 Red) starts after a compact (compact_continue)"
    source_tag: Local Canon
    precedents: ["grouping :73 split flag 'if the MEU-100 handoff passes ~50% context, run MEU-101 as 43b'", "Session 41 D-150"]
    research: { engine: none, sources: [] }
    reasoning: "The flag guards context size, and compact_continue resets context at the same point a split would, with the work and receipts on disk. A split would add a second plan, a second review and a second gate for the same tree. Mat can still ask for a split."
```

## Research References

- Electron default application menu and `before-input-event` (the menu's accelerators and the renderer's view of keys): https://www.electronjs.org/docs/latest/api/menu#default-menu, https://www.electronjs.org/docs/latest/api/web-contents#event-before-input-event (R-a)
- MDN `KeyboardEvent.isComposing` and `repeat`: https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/isComposing (R-b)
- MDN CSS `cursor` (`nwse-resize`, `nesw-resize`, `ns-resize`, `ew-resize`): https://developer.mozilla.org/en-US/docs/Web/CSS/cursor (R-c)
- The Human-approved synthesis `_inspiration/capture-annotation-tools/synthesis.md` (Excalidraw, tldraw, Fabric.js, Konva, Flameshot, ShareX, Greenshot survey) for A-1, A-2, A-3, A-6, C-3 and C-11.

The plan relies on three facts. AC-66.13 measured that a renderer `preventDefault` on a keydown keeps the default menu's accelerator from running, so the same holds for the edit roles (S4 if not). The four CSS resize keywords cover all eight handle directions. `textBackgroundBox` is the plate both the preview and the bake use, so scaling against it keeps the preview honest.

## Planning receipts

- **R-1 (2026-10-29).** `identity.py --selftest` (`C:/Temp/av-kit/s43-plan-R-identity.txt`): exit 0, `identity selftest: 0 failure(s)`.
- **R-2 (2026-10-29).** `red-check.py --selftest` 36 fixtures (`C:/Temp/av-kit/s43-plan-R-redcheck.txt`): exit 0, `36 fixture(s) (11 positive, 25 negative), 0 wrong`.
- **R-3 (2026-10-29).** `session-gate.ps1` parse (`C:/Temp/av-kit/s43-plan-R-gate-parse.txt`): `parse errors: 0`. The gate itself was not run during planning, because it needs the execution baseline.
- **R-4 (2026-10-29).** The `scope-paths` probe in a scratch repository, using the gate's own Python (`C:/Temp/av-kit/s43-plan-R-scope-probe.txt`): exit 0, 5 of 5 cases pass (clean tree; allowed product edits plus a new allowed file and a plan artifact; an uncommitted rename out of a disallowed path; an untracked disallowed path with a space and a non-ASCII name; a committed HEAD move, S8).
- **R-5 (2026-10-29).** `lint_task_contract.py` over `task.md` with `RECEIPTS_DIR=C:/Temp/av-kit` (`C:/Temp/av-kit/s43-plan-R-task-lint.txt`): exit 0, 26 rows, 24 fully checked, 2 `view_file` rows exempt (H1-5, H2-1).
- **R-a / R-c (2026-10-29, native).**
  - **R-a:** the Electron menu references above, together with `rg -n "setApplicationMenu" ui/src/main` (no hit), so the default menu is installed, and AC-66.13's measured suppression of the zoom accelerators.
  - **R-c:** the MDN `cursor` keywords, together with Tailwind's `cursor-nwse-resize`, `cursor-nesw-resize`, `cursor-ns-resize` and `cursor-ew-resize` utilities.

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths` (§4).
- **Targeted:** §3 after each production edit (blocking for its row).
- **Fresh full:** §4 in one pass after the last input edit, from `P:/av-kit`, `pwsh`. Row 8 runs it after the product edits. Row 9 then changes bound inputs (`meu-status.yaml`, the rendered `BUILD_PLAN.md`, the 09 and 06 Delivered notes, the index), so H1-2's run is the fresh full record the handoffs carry. It must pass; no partial, cached or reused receipt counts. Re-run all of §4 if any input changes after it (H1-6b).
- **Runtime (optional, non-blocking):** Mat's check (User Review Required item 9).
- **Input identity (`INPUT_IDENTITY`):** [identity.py](identity.py) prints the runtime identity and `tested_state`, which is HEAD plus one SHA-256. The hash covers:
  - **The work tree:** the tracked diff and the untracked (not ignored) files of the whole work tree. It excludes only this session's own closeout outputs, which no suite or gate step reads: this plan folder's `*.md`, this session's handoffs and reflection, `docs/execution/metrics.md` and `.agent/context/current-focus.md`.
    - So the lockfiles, `openapi.committed.json`, the configs and this plan's scripts are bound.
    - So are the documents the suites read: `docs/build-plan/` (`gui-actions-audit`, `capture-page`, `queue-canon`, `layout-canon`), `docs/BUILD_PLAN.md`, `meu-status.yaml` and the grouping files (`layout-canon`, `queue-canon`), and `meu-registry.md` (`state-render`).
    - Row 9 therefore runs before H1-2. The post-approval status write in H2-2 re-runs `layout-canon` and `queue-canon`.
  - **The runtime identity, observed live:**
    - the Python running it and the SHA-256 of its installed distribution set;
    - `node --version`;
    - the installed `electron` and `@playwright/test` versions;
    - the `segoeui.ttf` hash;
    - `ELECTRON_RUN_AS_NODE`.

  `--state-only` computes the same value. The gate records the state before and after it runs (§4), and each handoff's final full `evidence.v1` record carries it. H1-6b re-derives it live with `identity.py --state-only`, so any bound change refuses the old record and forces H1-2 again.
- **Evidence:** each receipt's exit code and decisive lines, pasted as `evidence.v1` in the handoffs.

## Execution Correction Notes

These are recorded during execution so that no plan-level contract changes silently. The execution review sees each item.

| Item | Change | Evidence |
|---|---|---|
| — | none yet | — |
