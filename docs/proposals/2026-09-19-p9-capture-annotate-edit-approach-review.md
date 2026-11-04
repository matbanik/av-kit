# Capture edit-until-Save: peer review and enhanced approach

Pre-plan advisory review of the 2026-09-19 coordinator draft. Local working-tree inspection and upstream research completed 2026-09-20. No product code, tests, plan files, or formal review verdict were produced.

## 1. Verdict on the draft

**keep-with-changes.** Keep React + SVG, the existing annotation DTO, renderer snapshot history, immutable originals, and Pillow baking. Direct manipulation answers the human's request, including two independently adjustable arrow ends. Tighten the interaction model before planning: use an explicit Select mode, separate transient previews from committed draft history, make image sampling independent of native-dialog capabilities, and define exactly when color changes affect a selected mark. Remove conditional box resizing and draggable text-entry fields. Retain a small mark list alongside the two arrow handles so overlapping marks remain reachable.

## 2. Findings

1. **High — Hit-first drawing has no reliable “start here” escape.** The draft makes every existing mark intercept drawing, including text plates and highlight interiors, but supplies no override (`docs/proposals/2026-09-19-p9-capture-annotate-edit-approach.md:25`). A large highlight could prevent starting an arrow across most of the image. Recommend Select mode; drawing tools always create, Select always edits. Auto-select a newly committed mark. This is an intentional change to the draft. ShareX itself distinguishes selection and creation and offers a modifier to draw over shapes; its intent does not establish that implicit hit-first behavior alone is sufficient. [ShareX keybinds](https://getsharex.org/keybinds/).

2. **High — “Working copy” must not become the history baseline.** `applyHistory` stores the current annotation array (`ui/src/renderer/src/features/capture/CapturePage.tsx:183`). Updating that array on every move and calling `applyHistory` at release would record an intermediate state. Keep the pre-gesture array immutable and preview separately; commit one replacement array only when geometry actually changes. The viewport currently exposes only down/up and uses mouse events, without drag capture (`ui/src/renderer/src/features/capture/CaptureViewport.tsx:40`, `:299`). Pointer capture, cancellation, and stale-event rejection are necessary work, not already-proven behavior.

3. **High — The sampler needs its own image identity/readiness check.** Detail loading and image loading are separate effects; the old `viewportSrc` is not cleared when a new image request starts (`ui/src/renderer/src/features/capture/CapturePage.tsx:85`, `:116`). `overlayReady` alone cannot prove that canvas pixels belong to the selected shot. Bind decode and sampling to shot ID, original variant, image URL, and a load epoch. Use the authenticated blob path (`ui/src/renderer/src/features/capture/capture-image.ts:15`); do not fetch an unauthenticated image URL or weaken Electron security.

4. **High — “Color input change is enough” is not a history contract.** The draft relies on a change event as a color commit (`docs/proposals/2026-09-19-p9-capture-annotate-edit-approach.md:42`). React documents that `onChange` behaves like the browser input event. Use an explicit Apply color/Cancel transaction for the app, independent of how many events the native dialog emits. [React input reference](https://react.dev/reference/react-dom/components/input).

5. **Medium — Native color well, image sampler, and desktop eyedropper are different capabilities.** The lockfile resolves Electron 42.9.3 (`ui/package-lock.json:4798`). Its source wires `OpenEyeDropper` to `ShowEyeDropper`; claiming Electron categorically lacks it would be wrong. Conversely, Chrome's color-picker documentation does not verify this app's native dialog or cross-window behavior. Guarantee an explicitly labeled **Sample original image** action; defer a separate desktop sampler. [Electron 42.9.3 source](https://github.com/electron/electron/blob/v42.9.3/shell/browser/api/electron_api_web_contents.cc#L4297), [Chrome EyeDropper documentation](https://developer.chrome.com/docs/capabilities/web-apis/eyedropper).

6. **Medium — Selection and tool settings currently have different semantics.** Existing color/stroke/font callbacks only change defaults (`ui/src/renderer/src/features/capture/CapturePage.tsx:477`). Keeping a selection while switching tools and silently rewriting its color, stroke, or font expands behavior beyond the human request. Clear selection when choosing a drawing tool; label color's target explicitly. Include selected-mark foreground color, but defer selected stroke/font/background editing.

7. **Medium — Box resizing cannot depend on whether code happens to be reusable.** The draft's “in-scope if they share the module” rule is an unresolved product decision (`docs/proposals/2026-09-19-p9-capture-annotate-edit-approach.md:28`). Lock box/highlight to translation and foreground color only; defer their resize handles. Preserve existing rectangle/highlight rendering semantics (`docs/build-plan/09-screenshot-capture.md:368`).

8. **Medium — Handles need a presentation-space contract, not merely a converted radius.** DTO geometry is integer image space, while handles must stay usable in CSS pixels. Rounded `mapPointerToImage` coordinates are unsuitable for precise screen-distance hit tests at extreme fit scales (`ui/src/renderer/src/features/capture/capture-fit-map.ts:49`). Measure hits against projected geometry in CSS space; retain FIT_MAP rounding for committed geometry. Text hit geometry must exist even without a painted background (`ui/src/renderer/src/features/capture/CaptureViewport.tsx:98`, `capture-text-metrics.ts:23`).

9. **Medium — Skipping the mark list loses the earlier accessibility and overlap safeguard.** The prior recommendation explicitly puts a mark list and simple movement ahead of complex handles (`docs/proposals/2026-09-19-p9-annotation-adaptation-proposal.md:60`). Two endpoint handles are justified by the new request; a general resize system is not. Keep a compact list of all four existing mark types with selection and Remove mark, plus keyboard movement of the selected body or endpoint.

10. **High — Text entry and destructive keyboard actions need ownership.** Text-draft pointer events currently bubble to a surface that starts a fresh text draft on down (`ui/src/renderer/src/features/capture/CaptureViewport.tsx:353`, `ui/src/renderer/src/features/capture/CapturePage.tsx:530`). Dragging the input would also conflict with caret selection. Keep entry stationary until Enter; then move the committed label. Backspace remains text editing. Scope Delete to focused annotation controls and never route it to Capture's existing file-deleting button (`CapturePage.tsx:340`).

11. **High — Extending the Save lock requires covering the command path.** The page disables its Save button using `overlayReady` (`ui/src/renderer/src/features/capture/CapturePage.tsx:320`), but `capture-commands.ts:69` checks only selected ID and parsed annotations; the palette calls it directly at line 113. The draft must not assume button state protects every Save entry point. Share one guarded GUI save operation with an explicit shot/list snapshot; exclude transient gestures, unresolved text/color edits, and stale loads. This preserves the requested lock without adding REST/MCP actions.

12. **Medium — A pre-existing boundary conflict must be recorded, not silently repaired.** The spec says drag clamp is `[0,W]×[0,H]` (`docs/build-plan/09-screenshot-capture.md:361`); the shipped GUI clamps to `W−1/H−1` and rejects rounded points at `W/H` (`ui/src/renderer/src/features/capture/capture-fit-map.ts:30`, `:55`). For this proposal, retain the code's locked mapping and make the discrepancy explicit in the later spec reconciliation. Pixel sampling must never read `W/H`. Do not alter backend clamps or MEU-59 formulas.

13. **Medium — G37 needs concrete test constraints.** The behavior suite already uses Testing Library and `userEvent.setup()` (`ui/tests/unit/capture-page.behavior.test.ts:4`, `:123`). Keep that harness. Existing raw mouse dispatch is not permission to introduce `createRoot` or bypass normal click/type/keyboard sequences. G37 requires userEvent for supported interactions (`.agent/docs/emerging-standards.md:1212`); reserve low-level events for explicitly unsupported cancellation/composition cases.

## 3. Enhanced approach

One GUI-only slice: select and translate existing marks, adjust either arrow endpoint, move committed text, and choose/sample a color that populates a visible code. Save remains the existing full-list operation. “Until Save” means edits are local until persisted; it does not remove the existing ability to reload and edit saved vectors.

These are proposed product decisions for the later plan, not newly asserted human approvals. The human directly requires arrow/text repositioning, adjustable endpoints, and sampler-to-code. Existing geometry/persistence rules are Local Canon/Spec. Selection, transaction boundaries, and accessibility choices below are research-backed adaptations whose precise av-kit behavior is specified here.

| Product lock | Disposition | Recommendation |
|---|---|---|
| React/SVG + existing FIT_MAP + Pillow; no new dependency | accepted | Reuse current geometry helpers; change no bake formulas. |
| Same strict four-type DTO; full-list Save; GUI first | accepted | No persisted selection IDs, REST changes, or MCP fork. |
| Original immutable; original-only editor; annotated view without vectors | accepted | Hide selection chrome and disable editing in annotated view. |
| `overlayReady`, generation checks, fail-closed sidecar | accepted | Extend their protection across pointer, sampler, color, and every GUI Save entry point. |
| Implicit hit-first tool behavior | changed | Add Select mode, distinct from annotation types. Draw tools create even over marks; successful creation switches to Select with the new mark selected. |
| Arrow movement | changed | Shaft/head translation is required, alongside two endpoint handles. |
| Text movement | accepted | Enter commits a label to the local list; then drag or keyboard-move it before Save. |
| Dragging the text-entry input | deferred | Keep caret/selection/IME behavior intact. No content re-editing feature in this slice. |
| Box/highlight parity | changed | Select, translate, recolor, remove. No resize handles. |
| Compact mark list | changed | Include selection and Remove mark; preserve drawing order. No layer-reordering UI. |
| Color updates selected mark | changed | Explicit Apply color updates selected `color` and the next-mark default; no selection means default only. |
| Native color event commits history | changed | Stage candidate color; Apply/Cancel defines the app transaction. |
| Image eyedropper | accepted | Required, labeled Sample original image; sampler auto-populates the candidate hex field. |
| OS/desktop eyedropper | deferred | Native dialog features are incidental; no separate desktop capture or IPC implementation. |
| Initial rubber-band preview | accepted | Render from the same transient state used for manipulation; no intermediate history entries. |
| Selected stroke/font/background controls; box resizing | deferred | Existing creation controls stay; no automatic rewriting of these selected-mark properties. |
| Phase 10/11, native-picker ink, new annotation types | deferred | No circle/marker, freehand, blur, curved arrows, layout migration, or capture-window editor. |

Keep editing state in `CapturePage.tsx`, presentation/event capture in `CaptureViewport.tsx`, and small pure helpers for hit-testing, bounded translation, and color conversion. Separate sampling into a renderer helper if useful; no new abstraction framework is needed. An array index is sufficient for ephemeral selection if Undo/Redo/delete/reload clear it and every active transaction pins its array revision.

## 4. Pointer state machine

Mode is `Select | Arrow | Box | Highlight | Text`. Interaction state is separate:

| State | Enter / transition | History | Esc |
|---|---|---|---|
| unavailable | No matching ready original image/detail, malformed sidecar, or annotated view | None; no edit/Save dispatch | No change to marks |
| idle | Select hit → pressed; draw-tool down → drawing; Text click → textDraft; color control → colorEditing | Selection/mode changes record nothing | Clear selection |
| pressed | Capture primary pointer; remember target, starting pointer, immutable list, shot/epoch/revision. Body → moving after 3 CSS px; endpoint → endpointDragging after same threshold | Click/release without movement records nothing | Release capture; retain selected mark |
| drawing | Update a transient new arrow/box/highlight; matching pointer-up validates and appends, then enters Select | One `applyHistory(next)`; invalid/zero-length gesture records nothing | Discard preview |
| moving | Compute translation from original pointer and original mark, never from the previous move event | Pointer-up replaces exactly one mark, once, only if changed | Restore pre-gesture geometry by discarding preview |
| endpointDragging | Update only the pinned `from` or `to`; head follows the unchanged helper | One replacement on valid pointer-up; collapse-to-zero cancels | Discard preview; keep selection |
| textDraft | Field owns pointer/keyboard. Non-composing Enter validates and appends text, then selects it; empty entry adds nothing | One append on valid Enter | Cancel only this draft |
| colorEditing | Candidate starts from selected foreground color or default. Well/manual field update candidate. Apply commits; Cancel discards | One replacement on Apply if selected color changes; defaults alone have no annotation history | Cancel candidate; retain selection |
| sampling | Nested under colorEditing; original-image click fills candidate then returns to colorEditing | Sampling itself records nothing | Return to colorEditing without changing candidate |
| saving | Freeze shot/list snapshot; block edits and duplicate Save until request settles | No history entry; success updates saved baseline only for matching shot/epoch | Does not pretend to cancel a POST already sent |

Use Pointer Events, one active pointer ID, primary-button filtering, and pointer capture. `pointercancel`, unexpected lost capture, window blur during a geometry drag, or viewport-transform changes cancel that gesture. Normal capture release after a completed pointer-up must not roll back its commit. Additional pointers are ignored. These are adaptations of the event lifecycle, not changes to annotation geometry. [Pointer Events specification](https://www.w3.org/TR/pointerevents3/).

`applyHistory` records the previous committed draft array, clears redo, advances the edit generation, and installs the next array. Preview state never enters that array. No-op movement, same-color Apply, cancellation, selection, and sampling must preserve redo. Undo/Redo operate only in idle; clear selection afterward to prevent index reuse. A keyboard movement burst records one entry from initial keydown through keyup; Escape cancels it like a pointer move.

While textDraft or colorEditing is open, require Enter/Apply or Esc/Cancel before changing tools, selection, view, or saving; do not silently commit on blur. A dirty thumbnail switch retains the existing confirmation, including nonempty text. While geometry is captured, defer toolbar/thumbnail actions until release or cancellation. Selection alone is never dirty.

Invalidate interaction tokens synchronously when switching shots, not only in a later effect. Stale pointer-up, decoded-image completion, sampler results, and Save completion cannot mutate another shot. Preserve `overlayReady` and `overlayEditGen`; add an image-load epoch because image readiness is independent. Save's button and existing palette command must use the same guard and immutable payload snapshot. Failure retains the draft and dirty state.

## 5. Hit-test + handle contract

- **Geometry:** DTO positions, widths, fonts, and stored deltas remain integer original-image pixels. Keep SVG `viewBox`, `xMidYMid meet`, FIT_MAP scale/origin/rounding, and no extra `devicePixelRatio` multiplication.
- **Chrome:** proposed handle radius 5 CSS px; hit radius 10 CSS px; minimum shaft/text padding 6 CSS px. Project geometry to client coordinates for hit tests. If handles are drawn inside the image-space SVG, divide chrome dimensions by fit scale and keep their border visually constant. Recompute on viewport resize; never rewrite DTO geometry.
- **Precedence:** only Select mode hit-tests marks. Visible handles of the selected arrow win; choose the nearer endpoint, with `to` winning an exact tie. Then inspect bodies in reverse array order. Selection never reorders marks. Drawing modes ignore these hits, allowing a new arrow to start on an existing mark.
- **Arrow:** hit-test the segment using half its displayed stroke plus padding, and the existing arrowhead triangle. Body drag translates both endpoints by one common bounded delta; independent endpoint clamping would distort the arrow.
- **Text:** use `textBackgroundBox` even when `bg_color` is absent, plus CSS-space hit padding. The invisible hit plate is selection geometry only; do not paint or persist a background. Keep `la`/hanging metrics and acknowledge fallback-glyph approximation.
- **Box/highlight:** box body means the stroked perimeter plus tolerance, not its entire empty interior; highlight means its filled rectangle. The mark list reaches covered shapes. Translation preserves dimensions, opacity, and stroke.
- **Bounds:** reject fresh pointer-down in the actual letterbox before testing chrome. During an already-captured drag, map unclamped input and apply bounded geometry; release outside the image can finish normally. Endpoints/text anchors use the existing GUI clamp. Bound translations as a shared delta for in-bounds geometry, without retuning text extents, arrowhead clipping, or bake edges. Do not normalize all reloaded marks as a side effect of selection.
- **Legacy/out-of-bounds data:** leave untouched on load. If a shape cannot satisfy the bounded-translation rule without resizing, reject that move visibly rather than silently deform it; arrow endpoint edits remain individually available.
- **Zero length:** new zero-length arrows add nothing. Collapsing a nonzero arrow onto itself restores its pre-drag state. Legacy zero-length arrows remain loadable and use the existing headless rendering; their coincident handle tie selects `to`, allowing recovery.
- **Keyboard access:** list entries are real labeled buttons. The selected inspector exposes Body and, for arrows, Tail/Head focus targets; arrow keys nudge the focused target by one image pixel. Delete removes only the selected mark when annotation controls own focus. Inputs, textareas, contenteditable elements, IME composition, and unrelated page controls retain their keys. Backspace never removes marks.

The spec's inclusive clamp wording versus the helper's pixel-index clamp remains the explicit conflict in finding 12. This slice must reconcile the wording without quietly changing MEU-59 behavior.

## 6. Color / sampler contract

**Native well:** use the existing browser control, plus a labeled editable color-code field and Apply color/Cancel. Preserve manual valid hex/named input; do not make typing mandatory. Display the target (“Selected arrow color” or “New marks color”). Native events update only a candidate and its preview/readout. This avoids relying on dialog close, blur, pointer-up, or React `onChange` as a commit signal.

**Image sampler:** Sample original image enters sampling mode and consumes the next valid image click without selecting, moving, or drawing. Decode the current authenticated original blob and draw it at natural dimensions onto an offscreen canvas; use the existing FIT_MAP inverse to choose an integer source pixel, then `getImageData(x,y,1,1)`. Do not rasterize the fitted viewport, include SVG marks, sample letterbox pixels, or apply DPR again. Canvas reads are in bitmap coordinates and ignore the context transform. [Canvas getImageData reference](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/getImageData).

A letterbox click stays in sampling mode with no change; Esc cancels sampling. Missing image, decode failure, null context, stale shot token, or readback/security error produces a visible failure and leaves candidate/marks unchanged. Release canvas/image resources on shot change/unmount. Use sRGB readback; output six-digit RGB only. Proposed transparent-pixel policy: reject nonopaque pixels visibly rather than silently sample hidden RGB or invent an alpha DTO.

**OS eyedropper:** Chrome documents a screen sampler and user-activation requirements; Electron 42.9.3 contains the corresponding browser integration. Neither proves the color dialog's exact Windows UI or this application's cross-window sampling behavior. No Electron GUI was launched here. A native-dialog eyedropper may be used if supplied, but acceptance must not depend on it. A dedicated `window.EyeDropper` button remains deferred, with capability detection and actual Electron verification required if later requested. [Chrome documentation](https://developer.chrome.com/docs/capabilities/web-apis/eyedropper), [pinned Electron integration](https://github.com/electron/electron/blob/v42.9.3/shell/browser/api/electron_api_web_contents.cc#L4297).

**Normalization:** picker/sample output and displayed normalized codes are uppercase `#RRGGBB`. Resolve the seven existing names for the well: red `#FF0000`, orange `#FFA500`, yellow `#FFFF00`, green `#008000`, blue `#0000FF`, white `#FFFFFF`, black `#000000`. Merely loading/selecting a named-color mark must not rewrite it or make it dirty. Apply writes normalized hex only to the targeted mark; a visually identical value is a no-op. Keep the current DTO validation (`capture-annotate.ts:6`; `packages/core/src/avkit_core/domain/capture.py:28`).

**Selection semantics:** applying a changed candidate rewrites only selected `color`, preserving geometry, text, `bg_color`, opacity, stroke, and font. It also updates the next-mark default. Without selection, Apply changes only that default. Annotation Undo restores the mark's old color, including its original named representation; it does not rewind toolbar defaults. Cancel changes neither. No HTTP request happens until Save.

**Oracles:** a known opaque pixel `(18,171,205)` produces `#12ABCD`; reading beneath a red SVG mark still returns the original pixel. Verify letterbox, fit scale, nonzero container origin, invalid/unready/stale canvas, and cancellation. Multiple native input events followed by one Apply yield one history entry; Cancel yields zero. Selecting a named green mark shows `#008000` without changing its DTO. Palette Save must not serialize an uncommitted color candidate.

## 7. Adaptation map

External sources establish intent; exact av-kit thresholds and state transitions above are proposed adaptations. No source is copied or translated.

| Behavior | Proven source | av-kit file | keep/adapt/defer | New dep? |
|---|---|---|---|---|
| Current selection distinct from current tool; visible resize nodes | [ShareX ShapeManager: CurrentShape, CurrentTool, NodesVisible](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/ShapeManager.cs) | `CapturePage.tsx`, `CaptureViewport.tsx` | adapt: Select plus two endpoint handles | No |
| Move/resize history boundary | [ShapeManager: StartRegionSelection, UpdateObjects](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/ShapeManager.cs) | `CapturePage.tsx` | adapt: stage before, record once after successful gesture | No |
| Color well plus sampled color | [ShapeManager: PickColor](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/ShapeManager.cs) | `CaptureViewport.tsx`, proposed sampler helper | adapt: original-image sampling; desktop scope deferred | No |
| Text-entry completion distinct from committed-object movement | [Flameshot TextTool: widget, move](https://github.com/flameshot-org/flameshot/blob/master/src/tools/text/texttool.cpp) | `CapturePage.tsx`, `CaptureViewport.tsx` | adapt: retain av-kit Enter/Esc semantics | No |
| Two-point drawing versus whole-object translation | [Flameshot AbstractTwoPointTool](https://github.com/flameshot-org/flameshot/blob/master/src/tools/abstracttwopointtool.cpp) | proposed geometry helper; `capture-arrow-head.ts` | adapt lifecycle; keep av-kit head formula | No |
| Arrow appearance | [Flameshot ArrowTool](https://github.com/flameshot-org/flameshot/blob/master/src/tools/arrow/arrowtool.cpp) | `capture-arrow-head.ts` | defer upstream geometry; MEU-59 stays authoritative | No |
| Pointer capture and cancellation | [W3C Pointer Events](https://www.w3.org/TR/pointerevents3/) | `CaptureViewport.tsx` | adapt | No |
| Bitmap pixel readback | [Canvas getImageData](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/getImageData) | `capture-image.ts`, proposed sampler helper, FIT_MAP | adapt | No |
| Native color events versus app commit | [React input](https://react.dev/reference/react-dom/components/input) | `CaptureViewport.tsx`, `CapturePage.tsx` | adapt: explicit Apply/Cancel | No |
| Desktop eyedropper availability | [Electron 42.9.3](https://github.com/electron/electron/blob/v42.9.3/shell/browser/api/electron_api_web_contents.cc#L4297) | no new production surface in this slice | defer | No |

All unqualified Capture filenames in this table are under `ui/src/renderer/src/features/capture/`.

ShareX takes history mementos at gesture entry; this proposal preserves the recovery intent while recording only successful av-kit edits at commit. Flameshot uses a different arrow construction and text commit shortcut. Those differences conflict with importing behavior wholesale: retain Pillow's head and av-kit's Enter/Esc contract.

## 8. Spec delta sketch

- In `09-screenshot-capture.md` Viewport tools, add Select as an editing mode, not an annotation type; draw tools create over existing marks and select their completed mark.
- Define arrow body translation, independent tail/head edits, committed-text movement, and move-only box/highlight editing.
- Specify the compact mark list, keyboard body/endpoint movement, scoped Delete, and protected text-entry/IME behavior.
- Document CSS-space handles/hit tolerances versus unchanged image-space DTO geometry and FIT_MAP.
- Explicitly reconcile inclusive boundary wording with the existing GUI pixel-index clamp; preserve backend and Pillow formulas.
- Add transient preview, one-history-entry commit, no-op/cancel rules, and pointer capture lifecycle.
- Specify native color well, editable synchronized code, Apply/Cancel, named-color reload, selected foreground/default behavior, and required original-image sampler.
- State sampler identity/decode readiness, letterbox handling, sRGB/nonopaque-pixel policy, and deferred desktop sampler.
- Extend Save/dirty rules to unresolved edit transactions, all existing GUI Save entry points, and stale shot/image completions.
- Preserve MEU-59 locks and named deferrals; name box resize, selected non-color properties, and text-content re-editing as outside this slice.
- Add test references for the new behavior without reopening Phase 10/11, native-picker annotation, REST, or MCP.

## 9. Test sketch

Suggested Red-phase IDs for the later plan; these are not implemented tests or assigned MEU numbers. Each AC must carry its source label and the local/upstream anchors above. Human-required movement/sampling is Human-approved; preserved mapping/DTO/bake behavior is Spec/Local Canon; exact interaction choices are Research-backed adaptations proposed here.

| AC ID | Layer | Failing assertion to write first |
|---|---|---|
| AC-EDIT-01 | Unit | CSS hit radii stay constant at multiple fit scales/origins; letterbox rejected; handle precedence and endpoint ties deterministic. |
| AC-EDIT-02 | Unit | Arrow translation preserves endpoint delta; endpoint edit preserves the other end; box/highlight dimensions unchanged; bounded text anchor and zero-length rules. |
| AC-EDIT-03 | Unit | Transparent text plate remains hittable; existing head vertices and text metrics are reused without changed formulas. |
| AC-EDIT-04 | RTL | Create arrow → auto-Select → move body → edit each endpoint; only targeted fields change. Choosing Arrow can start another over it. |
| AC-EDIT-05 | RTL | Commit text, move label without Undo, and Save new coordinates; field pointer events preserve draft; composing Enter/Backspace/Delete do not remove marks. |
| AC-EDIT-06 | RTL | Many move events produce one undo step; Undo restores exact start, Redo exact finish; Esc/cancel/lost capture/no-op preserve history and redo. |
| AC-EDIT-07 | RTL | Covered mark selectable through list; keyboard body/Tail/Head moves work; Remove mark differs from destructive Delete capture. |
| AC-EDIT-08 | Unit + RTL | Native/manual/sample normalization, all seven names, unchanged named reload, explicit Apply/Cancel, target-only recoloring, one history entry. |
| AC-EDIT-09 | Unit + RTL | Known pixel sampler uses original dimensions/FIT_MAP; ignores overlay; rejects letterbox/errors/nonopaque pixels; stale decode cannot affect next shot. |
| AC-EDIT-10 | RTL | Slow detail/image loads, invalid sidecar, shot switches, late pointer/color events: no edit or POST for mismatched state; test button and palette Save. |
| AC-EDIT-11 | RTL | Save uses committed full-list snapshot; blocked during text/color/drag transactions; failure keeps dirty draft; annotated view has no vectors/handles. |
| AC-EDIT-12 | One Playwright test | Real Electron: fitted image with known pixel patch → create arrow/text → drag both arrow endpoints and text → sample patch, assert exact populated hex, Apply → Save and assert full payload → reload and verify positions/color; annotated view contains no SVG marks. |

Keep `ui/tests/unit/capture-page.behavior.test.ts` on Testing Library `render/screen` and `userEvent.setup()`; use `user.pointer` for supported pointer sequences. Mock geometry and pixel-readback boundaries in jsdom, not the editing logic. Low-level cancellation/composition events need a documented support gap; no `createRoot` harness. Preserve existing MEU-59 assertions; when pointer plumbing changes, adapt event setup only.

The Playwright test belongs in the existing real-Electron Capture E2E path, with real renderer pointer capture and canvas sampling. A deterministic API seam can assert payloads, but is not proof of a real Pillow bake or native Windows color-dialog UI. Keep existing bake tests as regression coverage. This review ran none of these tests.

## 10. What not to do and smallest next MEU

Do not vendor or translate ShareX/Flameshot code; Golden Rule 5 applies (`docs/BUILD_PLAN.md:129`). Do not introduce Konva, Fabric, Paper, Sharp, OpenCV, generative editors, an additional drawing dependency, or an Electron MCP server. Do not mutate the original PNG, flatten before Save, stack vectors on an annotated PNG, change Pillow geometry, or silently turn a broken sidecar into an empty list. Do not expand this into circle/marker, box resizing, text re-editing, native-picker ink, or Phase 10/11 work.

**Smallest next MEU:** GUI edit-until-Save plus a guaranteed original-image color sampler: Select and compact mark access, arrow translation/two endpoints, committed-text movement, shared box/highlight translation, explicit color transactions, guarded existing Save, and the focused tests above. Write the FIC and all Red tests first, then implement against the same DTO and bake path. No MCP fork and no circle. The extra list and Select control resolve overlap/accessibility; they are not a general object-editor project.

## 11. Confidence + dissent

**High confidence** in the local architecture fit, DTO compatibility, explicit draft defects, and the need for transaction/identity guards. **Moderate confidence** in the proposed UX thresholds and keyboard ergonomics until tested in real Electron. Inspected the full coordinator draft, requested Capture modules, domain color contract, relevant spec sections, prior proposal, behavior-test harness, and targeted upstream sources. No Electron GUI, native color dialog, unit/RTL/Playwright suite, backend, or Pillow bake was run. Electron source support is evidence of integration, not runtime verification of this application.

The strongest case for skipping handles is substantial: a mark list plus keyboard/numeric movement and existing Undo is easier to make accessible, avoids tiny endpoint targets, and reduces pointer-state complexity. That remains a good reason to defer general box resizing and rich text editing. It does not fully answer this human's explicit endpoint-adjustment request. Two bounded arrow handles, backed by keyboard Tail/Head controls and the mark list, satisfy that request without importing an editor framework. Undo remains recovery; it should not be the primary placement-correction workflow.

The remaining product interpretation is explicit: “sampler” means a pixel from the selected original screenshot for this recommendation. Sampling arbitrary desktop applications is a separate capability, not promised by the native color well. The later plan should carry that visible scope statement rather than assume Chrome-on-web behavior.

