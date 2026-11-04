# Capture overlay edit-until-Save — proposed approach (pre-plan)

Date: 2026-09-19. Coordinator draft for Codex GPT-6 Astra peer review. **Not a plan. Not an FIC. Do not implement from this file.**

Human request (USER_EXPLICIT 2026-09-19 23:34–23:55): after placing an arrow or text, **reposition** it without Undo until **Save**. Arrow **line ends** should be draggable. Text should be movable. Also put a **color selector** in the GUI so a **sampler** auto-fills the color code instead of typing hex.

MEU-59 (arrow+text geometry repair) is **approved**. This is the next human-path slice Astra already named in `docs/proposals/2026-09-19-p9-annotation-adaptation-proposal.md` §3 item 2 (“Complete editing, recovery…”), **narrowed** to move/handles + color sampling. Do not add `circle`/`marker`. Do not start MEU-50. Do not add packages.

## 1. Why the current editor forces Undo

Save already POSTs the full unsaved list. Placement is fire-and-forget:

- `CapturePage.tsx` `onPointer` on `up` **appends** a finished `arrow`/`rect`/`highlight` via `applyHistory`.
- Text: click opens `textDraft`; Enter appends a `text` mark; Esc cancels the draft only.
- `CaptureViewport.tsx` SVG is `pointer-events-none`. Later clicks cannot hit a mark.
- Color is a **text** `<input data-testid="capture-color">`, not a picker. Domain/Zod already accept `#RRGGBB` **or** seven named colors.

Undo/Redo is a renderer stack of full annotation-list snapshots (`past`/`future`). That is the only way to correct placement today.

## 2. Recommended product locks (for Astra to accept, tighten, or reject)

| Lock | Recommendation | Rationale |
|------|----------------|-----------|
| Persistence | **No API/DTO/MCP change.** Moves rewrite existing `from`/`to` or `x`/`y` (and box `x,y,width,height`) in the same draft list Save already posts. | User asked for pre-Save adjust. Bake/sidecar already store those fields. |
| Tool vs Select | **No dedicated Select tool.** Pointer-down hit-tests existing marks first (topmost / last in list). Hit → select/drag. Miss (image interior) → existing draw gesture for the active tool. Letterbox still ignored. | Fewer chrome clicks; matches “adjust the inserted object.” |
| Arrow | Select shows **two handles** (`from` and `to`). Dragging a handle updates that endpoint; shaft + Pillow-matching head follow. Optional: drag the shaft to translate both ends. | User named line ends. |
| Text | Drag the committed label (use `textBackgroundBox` plate, even if `bg_color` is empty, as the hit rect). Do **not** start a new draft when the down lands on text. While `textDraft` is open, dragging the draft field may move `{x,y}` before Enter. | User named move-until-Save. |
| Box / highlight | Same select + **move** (translate). Resize handles are **in-scope if they share the hit-test module**; otherwise move-only is acceptable and resize is a named follow-up. | Four-tool parity so Undo is not still required for boxes. |
| History | **One** undo snapshot on **pointer-up** of a completed move/resize, not on mousemove. Live preview mutates a working copy. Cancelled pointer (lost capture / Esc mid-drag) restores pre-drag geometry without a stack push. | Matches current “one gesture = one undo.” |
| Color | Replace the hex text field with `<input type="color">` **plus** a read-only/synced hex readout. Add an **eyedropper on the screenshot**: click sampler, next image-pixel click reads RGB via canvas `getImageData`, writes `#RRGGBB` into the tool color (and selected mark if one is selected). Named colors remain valid on load; picker output is always hex. | User asked for sampler → auto-populated code. |
| View | Edit only on `variant=original` with `overlayReady`. Annotated view stays bake inspection, no SVG stack, no handles. | MEU-59 AC lock. |
| Out of scope | New types, Konva/Fabric, in-picker ShapeManager, MCP new action, Phase 11 layout, changing Pillow arrowhead/text-anchor formulas. | Keep MEU small. |

Live rubber-band **while first drawing** (preview line before mouseup) is **recommended in-scope**: same pointer path, currently missing, and it reduces Undo for the *initial* gesture too.

## 3. Interaction sketch

1. Original view, overlay ready, tool = Arrow. Drag empty image → rubber-band → mouseup commits arrow (existing, plus preview).
2. Click near an endpoint (hit radius in **CSS/screen pixels**, converted through FIT_MAP so small fitted images stay grabbable) → select that arrow, show handles.
3. Drag handle → live geometry; mouseup → `applyHistory` once.
4. Switch to Text. Click empty → draft as today. Enter commits. Click+drag the label → move; mouseup → one history step.
5. Color well changes **next** marks. If a mark is selected, color/stroke/font also rewrite **that** mark (one history step on change commit / pointer-up, not on every slider tick — color input `change` event is enough).
6. Eyedropper: toolbar button; cursor indicates sample; click image pixel → `#RRGGBB` into color state (and selected mark). Click letterbox cancels sample. Esc cancels sample.
7. Delete/Backspace with a selection removes that mark (one history step). Esc clears selection; does not Undo.
8. Dirty/thumb-switch confirm unchanged; include selection-only moves (already dirty via list inequality).

## 4. Implementation shape (GUI-only)

New small modules next to FIT_MAP (no new packages):

- `capture-hit-test.ts` — given image point + list + handle radius, return `{ index, kind: 'body' | 'from' | 'to' | 'nw' | … }`.
- Reuse `capture-fit-map.ts`, `capture-arrow-head.ts`, `capture-text-metrics.ts`.

`CaptureViewport.tsx`:

- Keep SVG `viewBox` + `xMidYMid meet`.
- Either keep `pointer-events-none` on SVG and hit-test in the existing surface handlers (**preferred**, one mapping path), or enable pointer events only on handle circles. Do not mix two coordinate systems.
- Draw handles only for `selectedIndex` on original view.
- `type="color"` + hex text + sampler button. Keep `data-testid="capture-color"` on the hex/value surface tests already use, or dual-bind tests.

`CapturePage.tsx`:

- `selectedIndex: number | null`.
- Pointer machine: `idle | drawing | moving | sampling`.
- Clear selection on tool change? **Proposal: keep selection** so you can recolor a mark after switching tools. Astra should confirm.
- `overlayReady` / `overlayEditGen` remain; never edit another shot’s marks.

Tests first (G36/G37): unit hit-test + FIT_MAP handle radius; RTL behavior for select/drag/save payload; Playwright: drag `from`/`to`, drag text, color input writes `#` + six hex, Save body matches. Do not neutralize MEU-59 tests.

## 5. Spec delta sketch (for a later plan — do not edit spec in the review run)

`docs/build-plan/09-screenshot-capture.md` Viewport tools: overlay remains vector until Save; **click selects; handles edit draft geometry; Save still POSTs the full list.** Color control is a picker + optional image sampler, not a raw hex-only field.

## 6. Risks the reviewer must address

1. Astra §3.2 preferred “accessible mark list + simple move **before** complex resize-handles.” This draft jumps to handles because the human named endpoints. Is a list still required in v1?
2. Screen-space vs image-space handle size under fit-to-viewport (the MEU-59 letterbox case).
3. Hit-test vs starting a new arrow when marks overlap.
4. `getImageData` vs Electron `<input type="color">` OS eyedropper — which is the sampler the human meant, and is the canvas path enough on Windows?
5. Applying color to the selected mark vs only to the next draw.
6. Whether box/highlight resize belongs in the same MEU.
7. Keyboard: Delete selected vs browser Backspace in the text draft.
8. G37: `capture-page.behavior.test.ts` is a Testing Library file — new pointer tests must not regress to `createRoot`.

## 7. What this is not

Not MEU-59 reopen. Not circle/marker. Not Phase 11. Not a second MCP schema. Not Konva. Not in-region-picker ink.
