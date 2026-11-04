---
project: "2026-10-01-capture-viewport-chrome"
date: "2026-10-01"
source: "docs/build-plan/09-screenshot-capture.md#viewport-toolbar-icons-and-options; docs/build-plan/09-screenshot-capture.md#viewport-zoom"
meus: ["MEU-65", "MEU-66"]
status: "approved"
template_version: "2.2"
---

# Implementation Plan: Capture viewport chrome (Session 29)

> **Project:** `2026-10-01-capture-viewport-chrome`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md`:
> - §Viewport toolbar icons and Options (`:613-623`, matrix 9.10)
> - §Viewport zoom (`:627-638`, matrix 9.11)
> - §Annotation geometry (`:356-375`) and §Annotation edit until Save (`:379-401`) as locked canon
>
> **Grouping:** `.agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md`, Session 29 (`:95-101`), decisions D-1 to D-7 (`:164-176`).
> **Status:** `approved` by the independent plan review in Round 2 (user-directed Fable 5.1 subagent; `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-plan-critical-review.md`), with the non-blocking notes folded in (§Round 2 Correction Notes). Execution needs a direct user message (`plan_to_exec_gate: human`), recorded in [human-gate-decision.md](human-gate-decision.md) §Execution authorization.

## Goal

Mat's 2026-09-30 walkthrough found three problems on the Capture page:

- The viewport toolbar scrolls sideways, even maximized at 4K, and clips Select and Apply.
- The header's per-page controls are a bare "Settings" text toggle that collides with the app Settings page.
- The image cannot be zoomed.

This session fixes all three.

- **MEU-65 `gui-capture-toolbar-icons`** (UI only):
  - Tool, history and view buttons become icon buttons with tooltips and accessible names.
  - The per-tool options move to a contextual second row.
  - At the default window, neither row scrolls horizontally.
  - The header disclosure becomes an **Options** button with an icon and chevron.
- **MEU-66 `gui-capture-zoom`** (UI only):
  - The mouse wheel zooms about the cursor.
  - **+ / − / Fit** buttons sit in the new toolbar, mirrored by `Ctrl+=` / `Ctrl+-` / `Ctrl+0`.
  - Space-drag and middle-drag pan the image.
  - `FIT_MAP` gains a scale and an offset, so pointer → image mapping, handle radii and hit tests stay exact at every level. Stored annotations never change.

Order: MEU-65 first, then MEU-66 (grouping `:98`; matrix 9.10 → 9.11). The zoom controls land in MEU-65's final toolbar, and the no-overflow assertion has to keep passing once they are added.

Neither MEU touches Python, REST, MCP, settings or OpenAPI (`PRODUCT_SCOPE`). The worktree baseline is the branch HEAD when execution starts; row 0 records it in `baseline.sha`. Planning started from `0e18fbd` (the Session 27 closeout on `claude/bold-edison-b91w56`). Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent (ls: No such file or directory, 2026-10-01); no headroom on PATH (`which headroom` empty). Scope is TSX/TS renderer internals, where .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). The `prereq` check refuses if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the claude.ai/code container:
  - `native_shell: bash`; no `rtk`, no `pwsh`, no Codex CLI;
  - `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code; `.agent/docs/harness-profiles.md`);
  - `fresh_worker` is the Agent tool with `.claude/agents/`, and rows keep `compact_continue` as the fallback.
- **Reviewer:** a Fable 5.1 subagent. It is the same vendor, and the user authorized it in [human-review-decision.md](human-review-decision.md). Caps: plan 3 rounds, execution 6.
- **Gate location:** the Sessions 25–27 split ([human-gate-decision.md](human-gate-decision.md) A-1).
  - The container pre-gate is non-authoritative.
  - `WINDOWS_GATE` and the `CAPTURE_LOOK` checklist run on Mat's machine and are authoritative.
  - Container commands call tools raw, which is the unfiltered equivalent of `rtk proxy`. `validate-task.ps1` runs every stage through `rtk proxy`.
- **Receipts:** `$RECEIPTS_DIR` in the container (default `/tmp/av-kit`), `C:/Temp/av-kit/` on Windows.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-65` | `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-65-handoff.md` |
| `MEU-66` | `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-66-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Baseline, §Census; `baseline.sha` |
| WP-1 | MEU-65 TDD and handoff (rows 2–4) | WP-0 | `compact_continue` | MEU-65 handoff; compact, then re-read `task.md` and the handoff |
| WP-2 | MEU-66 TDD and handoff (rows 5–8) | WP-1 | `compact_continue` | MEU-66 handoff; compact, then re-read |
| WP-3 | Hub reconciliation (row 9) | WP-2 | `shared` | `docs/build-plan/09…`, `11…`, `gui-actions-index.md` |
| WP-4 | H1 closeout, `WINDOWS_GATE` + `CAPTURE_LOOK`, execution review, H2 | WP-3 | `compact_continue` | handoffs, gate result JSON, walkthrough, rolling review, reflection |

---

## User Review Required

> [!IMPORTANT]
> These items are for the plan-review loop and for the user's execution message. They are not a pause point before review.
>
> 1. **Execution authorization** (`plan_to_exec_gate: human`). After the reviewer approves, execution starts only on a direct user message. It is recorded in [human-gate-decision.md](human-gate-decision.md) §Execution authorization.
> 2. **`TEST_AMENDMENTS` is empty.** The design keeps every existing assertion green: `h-7` tool buttons, the visible "Color"/"Stroke" labels, `flex-nowrap` rows, `NO_SHOT_HINT` titles, the MEU-59 worked example and the `capture-draw-surface` rect contract. Row 1's census proves it before any test is written. Any contradiction it finds stops execution (Stop condition S2). No existing expectation changes without a later explicit decision.
> 3. **Decisions D-8 to D-21** (§Decision Log) are resolved autonomously and logged. The user may veto any of them in the execution message. The ones most likely to matter to you:
>    - D-14: the zoom levels are Chromium's preset browser zoom factors, 25 % to 500 %, plus Fit.
>    - D-15: pan uses Space+drag and middle-drag inside a fixed frame, with no scrollbars.
>    - D-12: Highlight shows no Stroke field, because a highlight has no stroke width.
>    - D-17: `Ctrl+=` / `Ctrl+-` / `Ctrl+0` zoom only the image while the Capture page has a shot selected.
> 4. **A known runtime risk with a prepared exit.** The app installs no application menu (`ui/src/main` never calls `Menu.setApplicationMenu`), so Electron's default menu is live. That menu's View → Zoom In / Zoom Out / Actual Size items zoom the **whole window** on the same keys. AC-66.13 has a negative oracle for this: the window's `webContents.getZoomFactor()` must stay `1`. If the renderer's `preventDefault` cannot stop the menu accelerator, Stop condition S5 brings a Decision Brief with three prepared options (§Decision Log, D-22 draft).

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here. ACs, task rows and scripts refer to these names and never restate the values (PR-9).

| Name | Definition | Source |
|---|---|---|
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the "Files Modified" rows below, all under `ui/`. `packages/`, `mcp-server/`, `openapi.committed.json`, `tools/` and `ui/src/main/` stay byte-identical to `baseline.sha`. The one exception is behind Stop condition S5, as a separate human decision. `validate-task.sh api-scope` proves this. | Spec 09:613-638 (GUI-only rules); grouping `:97` |
| `TOOLS` | The `CaptureTool` union `'select' \| 'arrow' \| 'box' \| 'highlight' \| 'text'` (`CaptureViewport.tsx:19`). It is unchanged. | Local Canon |
| `TOOLBAR_BUTTONS` | The canonical icon list; the `validate-task.sh prereq` node check is its executable copy against the installed package. One table in `capture-toolbar.ts` (new), `as const`, typed so every `CaptureTool` appears exactly once (a `Record<CaptureTool, …>` for the tool part). Columns: test id → lucide icon → accessible name. Tools: `capture-tool-select` → `MousePointer2` → "Select"; `capture-tool-arrow` → `MoveUpRight` → "Arrow"; `capture-tool-box` → `Square` → "Box"; `capture-tool-highlight` → `Highlighter` → "Highlight"; `capture-tool-text` → `Type` → "Text". History: `capture-undo` → `Undo2` → "Undo"; `capture-redo` → `Redo2` → "Redo". View: `capture-view-original` → `Image` (imported as `ImageIcon`) → "Original"; `capture-view-annotated` → `Layers` → "Annotated". Zoom (MEU-66): `capture-zoom-out` → `ZoomOut` → "Zoom out"; `capture-zoom-in` → `ZoomIn` → "Zoom in"; `capture-zoom-fit` → `Maximize` → "Fit to view". Every name exists in the locked `lucide-react@0.400.0` (`ui/package-lock.json:7440-7441`; checked against its `dist/lucide-react.d.ts` at plan time, 2026-10-01). | Spec 09:619 ("icon set already used by the nav rail" = `lucide-react`, `NavRail.tsx:1`); D-11 |
| `ICON_BUTTON_RULE` | Each `TOOLBAR_BUTTONS` entry renders as `<Button size="sm" variant=…>` whose only child is the lucide icon with `aria-hidden="true"` (`size={16}`). It has `aria-label` = the accessible name and no visible text node. `title` is the accessible name, except that a tool button disabled for lack of a shot keeps `title = NO_SHOT_HINT` (`CaptureViewport.tsx:281`; UX2). The variant rules stay as they are today (`toolVariant`, `aria-pressed` on tools and the two view toggles). Undo, Redo and the zoom buttons are `ghost`. `size="sm"` keeps `h-7` (`Button.tsx:22`, AC-57.5 / TM-10); the `icon` prop is not used, because it drops `h-7` (`Button.tsx:58`). Electron specs locate these buttons by test id, or by `getByRole(..., {name, exact: true})`, because Playwright's name match is a case-insensitive substring by default (Review R1 observation 5). | D-9; Spec 09:619; Local Canon AC-57.5 |
| `OPTIONS_ROW` | New `div` `data-testid="capture-chrome-options"`, the second chrome row, `flex flex-nowrap items-center gap-1 min-h-9`. It holds exactly the option controls and none of the `TOOLBAR_BUTTONS`. Every option group keeps `shrink-0`, as the Color group and the Stroke label do today (`CaptureViewport.tsx:508,606`), so `NO_OVERFLOW` measures fit rather than inputs that have shrunk (Review R1 observation 3). The hex field `capture-color` gets `w-24 font-mono`, because a `#RRGGBB` value needs 7 characters and the browser-default input width would waste about 70 px. `capture-chrome-tools` holds exactly the `TOOLBAR_BUTTONS` (tools, history, view, and from MEU-66 the zoom group plus `ZOOM_READOUT`) and no option control. `capture-chrome-marks` stays the third row, unchanged. | Spec 09:620 |
| `OPTIONS_BY_TOOL` | One pure function, `optionGroups(tool, selected)` in `capture-toolbar.ts`, returns the set of option groups to render. **`color`** (`capture-color-well`, `capture-color`, `capture-color-apply`, `capture-color-cancel`, `capture-color-sample`, `capture-named-color`, with the visible "Color" label inside `role="group" aria-label="Color"`) is in the set for every member of `TOOLS`. **`stroke`** (the "Stroke" label with `capture-stroke`) is in the set when `tool ∈ {arrow, box}`, or when `tool = select` and the selection is none, an arrow or a rect. **`text`** (`capture-font-size`, `capture-text-bg`, `capture-text-bg-clear`) is in the set when `tool = text` or the selected mark is text (today's `showTextChrome`, `CaptureViewport.tsx:343`). `text` and `stroke` are never both present. The function's `switch` over `CaptureTool` is exhaustive (`assertNever`), so a new tool breaks the build. | Spec 09:620; D-12 |
| `NO_OVERFLOW` | At `DEFAULT_WINDOW`, with a shot selected, for every member of `TOOLS` and also with a selected text mark: `capture-chrome-tools.scrollWidth <= capture-chrome-tools.clientWidth` and `capture-chrome-options.scrollWidth <= capture-chrome-options.clientWidth`. Measured after `WINDOW_SETTLED`. | Spec 09:621 |
| `DEFAULT_WINDOW` | 1280 × 800 (`ui/src/main/index.ts:138`), with a fresh `AVKIT_APP_DATA`. Electron settles to about 1280 × 773 (`download-queue.test.ts:1109-1116`). | Local Canon |
| `WINDOW_SETTLED` | Before any geometry read, wait for two `requestAnimationFrame`s and then for `window.innerWidth`/`innerHeight` to be unchanged for 500 ms. This is the `windowSettled` helper pattern (`download-queue.test.ts:1117`), copied into `capture-inbox.test.ts`. | Local Canon |
| `OPTIONS_TOGGLE` | The Capture header `Disclosure` renders with title `Options`, `variant="secondary"`, a leading `SlidersHorizontal` icon (`aria-hidden`), and a trailing chevron icon. The chevron is `ChevronDown` when closed and `ChevronUp` when open; its wrapper is `data-testid="capture-settings-chevron"` with `data-state="closed\|open"`. `aria-expanded` and `aria-controls` stay as they are; `data-testid="capture-settings-toggle"`, `id="capture-settings"` and the panel content are unchanged. | Spec 09:622; D-13 |
| `DISCLOSURE_PROPS` | `Disclosure` gains three **optional** props: `variant?: ButtonVariant` (default `'ghost'`), `icon?: ReactNode` (default none), `chevron?: boolean` (default `false`). With all three omitted, the rendered DOM is byte-identical to today's. TTS, Downloader, Convert and the primitive harness pass none of them. | D-13; Local Canon AC-51.1/51.5/51.7 |
| `ZOOM_LADDER` | `[0.25, 1/3, 0.5, 2/3, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5]`, exported once from `capture-zoom.ts`. This is Chromium's `kPresetBrowserZoomFactorsArray`. | Research-backed D-14: `third_party/blink/common/page/page_zoom.cc:13-15` (chromium/src `main`, read 2026-10-01) |
| `ZOOM_STATE` | `{ kind: 'fit' } \| { kind: 'scale'; scale: number; ox: number; oy: number }`. This is view state owned by `CaptureViewport` (`useState`), never persisted and never sent anywhere. | Spec 09:637; D-16 |
| `ZOOM_STEP(state, dir, fitScale)` | `zoomStep` in `capture-zoom.ts`. Let `current` be `fitScale` for `fit`, otherwise `scale`. `in` returns the smallest `ZOOM_LADDER` value `> current + 1e-9`; `out` returns the largest value `< current - 1e-9`. It returns `null` when there is none, and that disables the button and makes the key or wheel a no-op. It also returns `null` when `fitScale` is not (finite and > 0), which fails closed. Fit stays a separate level reached only by the Fit button or `Ctrl+0`, so the reachable levels are always `ZOOM_LADDER ∪ {Fit}`. That includes Fit and 100 %. | Spec 09:634; D-14 |
| `VIEW_TRANSFORM(container, image, state)` | `viewTransform` in `capture-fit-map.ts` returns `{s, ox, oy} \| null`. For `fit` it returns exactly `fitScaleOrigin(...)`, so the MEU-59 numbers are unchanged. For `scale` (call it `z`), per axis: if `W*z <= Cw` it centres (`ox = (Cw - W*z)/2`), otherwise it clamps (`ox = min(0, max(Cw - W*z, state.ox))`); the same for `y`. Any non-finite or ≤ 0 input returns `null`, so the caller maps nothing. This is the single geometry source for `SURFACE_POINTER`, the handle radius, the text-draft position, the image/SVG content box and `ZOOM_OBSERVABLES`. | Spec 09:636; Local Canon 09:356-375 |
| `VIEW_MAP` | `mapPointerWithView(clientX, clientY, left, top, t, W, H)` and `mapImageToPointerWithView(point, left, top, t)` in `capture-fit-map.ts` use the FIT_MAP formulas from 09:363 with `t.s`, `t.ox`, `t.oy`. Out-of-image points return `null`, as `mapPointerToImage` does, and `clampImagePoint` is unchanged. The existing exports keep their signatures and outputs (AC-59.1, AC-59.18 untouched). | Spec 09:636 |
| `ZOOM_EXAMPLE` | Image `1600×900` in container `800×600`, `scale` state `{scale: 2, ox: -1000, oy: -450}` → `VIEW_TRANSFORM` `{s: 2, ox: -1000, oy: -450}`. Container point `(400, 300)` maps to image `(700, 375)`; image `(700, 375)` maps back to `(400, 300)`. The fit-only mapping of the same point gives `(800, 450)`, which is the negative oracle. | derived from 09:375 |
| `ZOOM_ABOUT(state, cursorCss, nextScale, container, image)` | `zoomAbout` in `capture-zoom.ts`. With the current transform `t` and the cursor `c` (container CSS px), it computes `i = (c - t.o)/t.s` per axis, sets the new offset to `c - i*nextScale`, and then applies `VIEW_TRANSFORM`'s centre/clamp rule. Worked example `ZOOM_ABOUT_EXAMPLE`: the `1600×900` image in `800×600` at fit (`s 0.5, ox 0, oy 75`), cursor `(400,300)` (image `(800,450)`), `ZOOM_STEP` in → `2/3`. The result is `ox = 400 - 800·2/3 = -133.33` (inside the clamp range `[-266.67, 0]`) and `oy = 0` (content height 600 = container, so centred). The cursor still maps to `(800, 450)`. | Spec 09:633 ("zooms about the cursor") |
| `ZOOM_INPUTS` | (a) **Wheel**: a native `wheel` listener on `capture-draw-surface` registered with `{passive: false}`, because React's `onWheel` is passive and cannot `preventDefault`. It always calls `preventDefault()`, with or without Ctrl, and zooms about the cursor via `WHEEL_STEP`. (b) **Buttons** `capture-zoom-in` / `capture-zoom-out` / `capture-zoom-fit` zoom about the container centre. (c) **Keys** in `ZOOM_KEY_SCOPE`: `Ctrl`+(`=` or `+` or `NumpadAdd`) → in; `Ctrl`+(`-` or `NumpadSubtract`) → out; `Ctrl`+(`0` or `Numpad0`) → Fit. Each handled key calls `preventDefault()` and zooms about the container centre. `Meta` stands in for `Ctrl` on macOS. | Spec 09:633; D-17, D-18, D-19 |
| `WHEEL_STEP` | `wheelSteps(accumulator, event)` in `capture-zoom.ts`. For `deltaMode` 1 or 2 (lines or pages) it gives one step per event, with sign `-sign(deltaY)` (up = in). For `deltaMode` 0 (pixels) it adds `deltaY` to the accumulator and emits one step each time `abs(accumulator) >= WHEEL_STEP_PX`, keeping the remainder. The accumulator resets when the sign changes or 250 ms pass without a wheel event. `WHEEL_STEP_PX = 100`. `deltaY == 0` (a horizontal-only wheel) is a no-op. | Research-backed D-18 (MDN `WheelEvent.deltaMode`); `CAPTURE_LOOK` L3 confirms one notch = one step on the target |
| `ZOOM_KEY_SCOPE` | The keys in `ZOOM_INPUTS` (c) act only when all of these hold: the Capture page is mounted, a shot is selected (`hasSelection`), `document.activeElement` is not an `input`, `textarea`, `select` or `[contenteditable]`, and no `[data-testid="capture-confirm-strip"]` is in the DOM. Otherwise they are not handled and not prevented. `ZOOM_KEY_SCOPE` governs only the zoom and Space keys; `COLOR_FOCUS_IDS` + `annotationOwnsFocus` (`CapturePage.tsx:80-107`) keep governing the MEU-60 editor keys, unchanged. One handler, `handleViewKey(event)` in `CaptureViewport`, owns the zoom keys and the Space arm/disarm of `PAN_GESTURES`. It is called from two places: a `window` `keydown`/`keyup` listener (removed on unmount), and the `capture-draw-surface` `onKeyDown`/`onKeyUp` **before** its existing `stopPropagation()` (`CaptureViewport.tsx:736-739`). That surface handler stops the event from reaching `window`, so without the second call the keys would be dead while the surface has focus. A `handled` flag on the native event prevents a double step if both paths ever see the same event. | D-17; reflection 2026-09-28 RULE-3 |
| `PAN_GESTURES` | (a) Middle-button (`button === 1`) drag on `capture-draw-surface`. The middle-button `pointerdown` / `mousedown` calls `preventDefault()`, so Chromium's middle-click autoscroll on the scrollable `main` (`AppShell.tsx:273`) never starts (Review R1 observation 1). (b) Primary-button drag while Space is held, where Space is armed only when `document.activeElement` is the surface, `body`, or inside `capture-viewport` but not a `button`, `input`, `select` or `textarea`. The Space `keydown` that arms panning calls `preventDefault()`. A pan changes `ZOOM_STATE.ox/oy` through `VIEW_TRANSFORM`'s clamp. It emits **no** `SurfacePointer`, so it creates no mark, starts no gesture, pushes no history and samples nothing. At `fit`, or on an axis that is centred, a pan is a no-op. While Space is held, the surface cursor is `grab` (`grabbing` while dragging). | Spec 09:635; Research-backed D-15 |
| `ZOOM_RESET` | `ZOOM_STATE` returns to `fit` when the `shotId` prop changes: thumb switch (including after the dirty confirm), delete, or the first selection. It is kept when Original/Annotated toggles, because both variants share the original pixel space (09:368). It is kept when the container resizes: the scale stays and the offsets are re-clamped through `VIEW_TRANSFORM`. | Spec 09:637; D-16 |
| `ZOOM_READOUT` | `data-testid="capture-zoom-level"`, a `<span>` in the zoom group with `aria-live="polite"` and `min-w-[3.5rem]`. It reads `Fit` in `fit` mode, otherwise `${Math.round(scale*100)}%`. Its `title` is the pan hint `ZOOM_PAN_HINT` = "Wheel or Ctrl+= / Ctrl+- to zoom · Ctrl+0 to fit · Space+drag or middle-drag to pan". | D-19, D-21 |
| `ZOOM_OBSERVABLES` | `capture-draw-surface` carries `data-zoom-kind` (`fit\|scale`), `data-zoom-scale`, `data-zoom-ox` and `data-zoom-oy`: the current `VIEW_TRANSFORM` `s/ox/oy`, written with `toFixed(4)`. These are read-only test and diagnostic observables; production logic never reads them back. | D-20 |
| `SURFACE_POINTER` | `surfaceFromDom` (`CaptureViewport.tsx:210-259`) builds every `SurfacePointer` from `VIEW_TRANSFORM` + `VIEW_MAP`: `scale = t.s`, `ox = t.ox`, `oy = t.oy`, and `image` / `imageClamped` from `mapPointerWithView`. `cssX`/`cssY` stay `clientX - rect.left` / `clientY - rect.top`. The container box stays `capture-draw-surface`'s `getBoundingClientRect()`. The surface is `overflow-hidden` and is never a scroll container, so rect = container, the same contract the jsdom geometry stubs use (`capture-page.behavior.test.ts:122-135,1246-1268`). The legacy `onPointer` path (`mapEvent`, the `onPointerUp`/`onMouseUp` branches) uses the same transform. `CapturePage.handleSurfacePointer` needs no change, because `hitTestMarks` already takes `scale/ox/oy` (`capture-hit-test.ts:14-24,26`). **Thresholds stay as they are:** the draw path has no drag threshold, and only a zero-length arrow or zero-area rect creates nothing (09:366; `CapturePage.tsx:135-137,149-151,651-663`). `DRAG_THRESHOLD_CSS` (3 CSS px, `CapturePage.tsx:41`) applies only to move and endpoint edits (`:671,:713`). It is measured in CSS px, so it is zoom-invariant in screen terms. No row adds or changes a threshold. `CaptureViewport.tsx` must not contain the literal `devicePixelRatio`, not even in a comment (AC-59.4 source check, `capture-page.test.ts:254`). | Spec 09:636; Local Canon MEU-60 |
| `CONTENT_BOX` | The `<img>` and `<svg>` move into one absolutely positioned content `div` `data-testid="capture-zoom-content"` with `left = t.ox`, `top = t.oy`, `width = W*t.s`, `height = H*t.s` (inline style). The `img` keeps `w-full h-full object-contain`, and the `svg` keeps `viewBox="0 0 W H"` and `preserveAspectRatio="xMidYMid meet"` (AC-59.4 source and jsdom assertions unchanged). With an exact-aspect box, `meet` maps exactly like `VIEW_MAP`. The handle radius is `HANDLE_RADIUS_CSS / t.s` (reflection 2026-09-20 RULE-1 at the zoomed scale). The text draft input sits at `mapImageToPointerWithView(textDraft, 0, 0, t)` inside the surface. | Spec 09:636; Local Canon 09:363 |
| `ZOOM_SHOT` | The Electron fixture shot for zoom cases: `sampleShot` gains an optional `{width, height}` override (default 8×8, unchanged for existing tests). The zoom specs use `2400×1600`, so Fit is below 1 at `DEFAULT_WINDOW` and every ladder step is reachable. The served bitmap stays `PNG_1X1`, because geometry comes from the JSON width/height (`CapturePage.tsx:578,1249`). | Local Canon `capture-inbox.test.ts:28-42` |
| `ZOOM_SEAM_SHOT` | The jsdom zoom fixture for AC-66.7 – AC-66.11. It is a `1600×900` shot (a spread override of the behavior test's `SHOT`), and the `capture-draw-surface` rect is stubbed to 800×600. The existing `withSurfaceSize` helper (`capture-page.behavior.test.ts:1246-1268`) is square-only, so the fixture adds a width/height variant next to it (append-only; the square helper and its callers are unchanged). Any fake `ResizeObserver` is installed **before** the render, because the viewport subscribes in a layout effect keyed on the image size and selection (`CaptureViewport.tsx:356-382`). Fit is therefore `0.5`, inside `ZOOM_LADDER`, so every step is reachable in both directions. The existing 8×8 / 200×200 setup (fit 25, above the ladder top) stays unchanged for every other test. | Local Canon `capture-page.behavior.test.ts:54-66,125-138` |
| `ZOOM_HELP_SENTENCE` | "Zoom with the mouse wheel, the + / − / Fit buttons or Ctrl+= / Ctrl+- / Ctrl+0; hold Space or the middle button and drag to pan. Zoom never changes saved marks." It is appended to the `four-tools` body in `capture-help-content.ts`; the existing sentences stay verbatim (AC-59.20, AC-60.15). | 09:155-157 HelpCard topics are a minimum; D-21 |
| `TEST_AMENDMENTS` | **Empty.** This plan approves no change to any existing test expectation. Row 1's census proves every hit is `unaffected`. | AGENTS §Testing & TDD |
| `NEW_TESTIDS` | Appended **after** the `// MEU-51 primitive harness IDs.` marker (`test-ids.ts:300`) in two new blocks, so the AC-51.6 prefix hash (`layout-primitives.test.ts:200-214`) stays valid. `// MEU-65 Capture toolbar and Options (additive IDs).`: `capture-chrome-tools`, `capture-chrome-options`, `capture-settings-chevron`. `// MEU-66 Capture viewport zoom (additive IDs).`: `capture-zoom-in`, `capture-zoom-out`, `capture-zoom-fit`, `capture-zoom-level`, `capture-zoom-content`. None of these values exists in the prefix today (`capture-chrome-tools` is used in source but unregistered). | Local Canon AC-51.6 |
| `GATED_PATHS` | The executable copy is the `gated` list in `validate-task.sh` `windows-gate-check`, and `plan_checks.py static` asserts it equals this list: `ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json docs/build-plan/06-gui.md docs/build-plan/10-queue-card-ui.md docs/build-plan/11-page-layout.md docs/build-plan/build-priority-matrix.md docs/build-plan/gui-actions-index.md docs/proposals docs/execution/plans/2026-08-28-p10-queue-card-foundations docs/execution/plans/2026-09-02-p10-queue-card-migration docs/execution/plans/2026-09-03-p10-queue-card-dnd docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md .agent/model-registry.local.json .agent/model-registry.local.yaml docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.ps1`. That is the code plus the non-code files the gate stages read, from a plan-time sweep of repo-relative paths in `ui/tests/unit` (Review R1 F3): `openapi` reads `openapi.committed.json`; `layout-canon.test.ts:14-17` reads `11-page-layout.md`, the p11 layout-canon plan, the p11 grouping and the `docs/proposals` mockups; `capture-page.test.ts:57` reads `06-gui.md`; `queue-canon.test.ts:14-18` reads `10-queue-card-ui.md`, `06-gui.md` and `build-priority-matrix.md`; the queue-card / queue-list suites read the three p10 plan folders; `gui-actions-audit.test.ts:11` reads `gui-actions-index.md`; and `test_framework_adoption.py` reads the registry overlay. **Excluded, as a rule:** `.agent/context/meu-status.yaml` and `docs/BUILD_PLAN.md`, which `state-render` and `layout-canon.test.ts:17-18` read, are SSOT. They change only at H1-3 (before the gate) and H2-2 (after approval), and cloud-local §3.4 treats those doc-only closeout edits as not reopening the gate. H2-2 (`post-review-state`) re-runs `state-render` and the doc-reading Vitest after its SSOT edits. Session 27 Review R2-3 settled the same rule. | cloud-local §3.3 item 2, §3.4 |
| `COUNT_FLOORS` | Vitest total ≥ 702 and Electron expected ≥ 118, taken from the last authoritative gate: Session 27 attempt 7, `2026-09-30-tts-repair/windows-gate-result.json`, Vitest 702/702 and e2e 117 expected + 1 unexpected = 118 specs, accepted under A-7. In the runner's own vocabulary (reflection 2026-09-30 RULE-3): Vitest `numTotalTests` ≥ 702 with `numFailedTests` 0, and Playwright `stats.expected` ≥ 118 with `unexpected` 0 and `flaky` 0. pytest reports failed == 0, and every later attempt's passed count must be ≥ the first attempt's (`pytest_floor`, carried by the `.ps1`). The executable copies are the literals in `validate-task.sh` `windows-gate-check`; `plan_checks.py static` asserts they equal 702 / 118. | cloud-local §3.3 |

**Environment-bound census** (cloud-local §4). The container pre-gate tolerates only these failures. `WINDOWS_GATE` tolerates none. This is the same set as Session 27 (`2026-09-30-tts-repair/implementation-plan.md:151-159`):

| Tier | Member | Signature / handling |
|---|---|---|
| Vitest | AC-51.6 `ui/tests/unit/layout-primitives.test.ts` | The CRLF prefix hash recomputes to `819760B9…` and new ids are unique (`vitest_env_ok` `crlf_proof`). `NEW_TESTIDS` lands after the marker, so the proof still holds. |
| Vitest | AC-41.3 `ui/tests/unit/queue-canon.test.ts` | `P:/zorivest` is absent and `styles.css` is unchanged since `f7d3134`. |
| Electron | capture-picker specs in `ui/tests/e2e/capture-picker.test.ts` | Not on Windows, the stub `.exe` is absent, and the failure is exactly the stub-missing error (`electron_env_ok`). |
| pytest | the Windows-bound tooling tests (`tests/tooling/*`) | `pytest_env_ok`: the container's failed set must be a subset of the failed set at `baseline.sha`. This session changes no Python, so any new failure is real. |
| External inputs | `P:/agentic-framework` HEAD; `P:/.agent/model-registry.json` hash | `validate-task.ps1` records both before stage 1. On attempt ≥ 2 a mismatch with the previous attempt stops before stage 1 (cloud-local §3.2). |

### MEU-65 — `gui-capture-toolbar-icons`

#### Boundary Inventory

No new external input surface. Every control stays on its existing handler (`onTool`, `onColor`, `onStroke`, `onFontSize`, `onTextBg`, `onViewVariant`, `onUndo`, `onRedo`), and the parse and validation rules downstream are unchanged (`parsePositiveInt`, `normalizeHex`, the annotate Zod/Pydantic boundary).

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| UI option inputs (`capture-color`, `capture-stroke`, `capture-font-size`, `capture-text-bg`) | unchanged: `CapturePage.tsx` `changeStroke` / `changeFontSize` / `changeTextBg`, `normalizeHex`, `parsePositiveInt` | unchanged (they move between rows; values and handlers are identical) | not applicable (no payload change; `POST /annotate` body unchanged) |
| Options disclosure | `Disclosure` (`components/ui/Disclosure.tsx`) | boolean `open` only | not user text |

#### Acceptance Criteria

Call chain for every integration AC: route `/capture` → `CapturePage` → `CaptureViewport` (`capture-chrome-tools`, `capture-chrome-options`) / `Disclosure` (`capture-settings-toggle`) → the existing handlers. The Electron cases run against the built app (`out/main/index.js`) with the `capture-inbox.test.ts` seam.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-65.1 | unit | `TOOLBAR_BUTTONS` is complete and typed: every `CaptureTool` appears exactly once, each name is a non-empty string, and the test ids are unique. `optionGroups` implements `OPTIONS_BY_TOOL` for every `TOOLS` member × selection ∈ {none, arrow, rect, highlight, text}. | Spec 09:619-620; D-11, D-12 | `optionGroups('highlight', null)` has no `stroke` and no `text`. `optionGroups('text', null)` has no `stroke`. `optionGroups('select', highlightMark)` has no `stroke`. `optionGroups('arrow', textMark)` has `text` and no `stroke`. No input returns both `text` and `stroke`. |
| AC-65.2 | integration | jsdom (`capture-page.behavior.test.ts`, page rendered with the fetch seam). Each `TOOLBAR_BUTTONS` button in `capture-chrome-tools` follows `ICON_BUTTON_RULE`: the accessible name equals the table name (`getByRole('button', {name})` resolves exactly one inside the row), there is no text node, the svg has `aria-hidden="true"`, the class has `h-7`, `aria-pressed` is on the tools and view toggles, and clicking still calls the same handler (tool change, undo/redo, variant switch). | Spec 09:619; Local Canon AC-57.5 | With no shot selected, each tool button is disabled and its `title` is `NO_SHOT_HINT` (UX2). A button whose `textContent.trim()` is non-empty fails. Undo with an empty history stays disabled and adds no history entry. |
| AC-65.3 | integration | jsdom: `capture-chrome-options` renders exactly `optionGroups(tool, selected)` and `capture-chrome-tools` contains no option id. Every `capture-color-*`, `capture-named-color`, `capture-stroke`, `capture-font-size`, `capture-text-bg`, `capture-text-bg-clear` id that the rule calls for is present with its existing behavior: Apply/Cancel color, Sample, named color, stroke edit on a selected arrow, font size on a selected text mark. | Spec 09:620, 09:623 | Tool Highlight → `queryByTestId('capture-stroke')` is null. Tool Text → `capture-stroke` is null and `capture-font-size` is present. An option id found inside `capture-chrome-tools` fails. The existing AC-59.13, AC-57.5 (incl. visible "Color"/"Stroke" text), AC-60.x and "chrome rows do not wrap" tests pass **unchanged** (`TEST_AMENDMENTS` empty). |
| AC-65.4 | integration | Electron (`capture-inbox.test.ts`, title contains `AC-65.4`): `NO_OVERFLOW` holds for every `TOOLS` member and for a selected text mark. The spec's **first** `expect` calls are the `scrollWidth`/`clientWidth` comparisons (`toBeLessThanOrEqual`), made right after a shot is selected and the window has settled, so on the pre-change layout it fails on geometry and not on a missing new id. | Spec 09:621 | **Red on the pre-change layout:** `red65` runs `require_failed_title AC-65.4 toBeLessThanOrEqual`. The R3 repro (`known-issues.yaml` CAPTURE-TOOLBAR-ICONS verification) says it overflows even at 4K. If it does not go Red in the container, Stop condition S4 applies. |
| AC-65.5 | integration | jsdom + Electron: `OPTIONS_TOGGLE`. The toggle's accessible name is "Options", it has class `btn-secondary`, a leading svg and the `capture-settings-chevron` wrapper. Clicking flips `aria-expanded` and the chevron `data-state`, and the panel (`#capture-settings-panel`) toggles `hidden`. The panel controls (`capture-inbox-path`, `capture-hotkey`, `capture-page-save`) save as before (the AC-57.10 Electron case still passes unchanged). | Spec 09:622; Human-approved (triage D-16) | The toggle's text never contains "Settings". With the panel closed, `capture-inbox-path` is not focusable (`hidden`). The chevron `data-state` always equals `aria-expanded` ("open" ⇔ "true"). |
| AC-65.6 | unit | `DISCLOSURE_PROPS`: with no new props, the `Disclosure` render equals today's. It has the ghost variant, no svg and title-only text (`layout-primitives` AC-51.1/51.5/51.7 and the TTS `Cleanup · 10 of 11 steps` exact-text assertions pass unchanged). With `variant`/`icon`/`chevron` set, it renders them. | Local Canon AC-51.1; D-13 | A default `Disclosure` with an svg child or a non-`btn-ghost` class fails. The primitive keeps importing no `features/` module and no raw hex (AC-51.5). |
| AC-65.7 | unit | `NEW_TESTIDS` (MEU-65 block) is registered after the MEU-51 marker. The source uses each id literally. | Local Canon AC-51.6 | The AC-51.6 prefix-hash test stays green in `vitest_env_ok`. A duplicate of a prior value fails it. |
| AC-65.8 | integration | Electron (added by A-5 after `CAPTURE_LOOK`): opening the Options panel does not move the Options toggle. Its bounding box before and after opening differs by ≤ 1 px, and the toggle stays on the same row as `capture-region` (equal `top` within 1 px). The panel opens under the toggle and wraps within the remaining header width. | Human-approved A-5 (Mat's observation 1) | With the old content-sized `ml-auto` section, the open panel wraps the section onto its own line and the toggle's `top` grows by more than a row. |

**Test-ID migration (MEU-65).**

| Existing ID | Migration | Detail |
|---|---|---|
| `capture-tool-select/-arrow/-box/-highlight/-text`, `capture-undo`, `capture-redo`, `capture-view-original`, `capture-view-annotated` | change | icon-only (`ICON_BUTTON_RULE`); ids and handlers unchanged |
| `capture-color-well`, `capture-color`, `capture-color-apply`, `capture-color-cancel`, `capture-color-sample`, `capture-named-color` | move | into `capture-chrome-options` (`color` group) |
| `capture-stroke`, `capture-font-size`, `capture-text-bg`, `capture-text-bg-clear` | move | into `capture-chrome-options` per `OPTIONS_BY_TOOL` |
| `capture-chrome-tools` | keep (now registered) | holds only `TOOLBAR_BUTTONS` |
| `capture-chrome-marks` and its children | keep | unchanged third row |
| `capture-settings-toggle` | change | `OPTIONS_TOGGLE` |
| new: `capture-chrome-options`, `capture-settings-chevron` | add | MEU-65 block |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Icon buttons, tooltips, aria | Human-approved + Research-backed | 09:619; D-9, D-10, D-11 |
| Which icon set | Spec | 09:619 "icon set already used by the nav rail" → `lucide-react` (`NavRail.tsx:1`) |
| Contextual options content per tool | Research-backed | 09:620; D-12 |
| No overflow measurement | Spec | 09:621 (`NO_OVERFLOW`) |
| Options button affordance | Human-approved + Research-backed | 09:622; triage D-16/D-17 (`known-issues.yaml` CAPTURE-SETTINGS-BUTTON-LABEL); D-13 |
| Toolbar keyboard model | Research-backed | D-10 (APG toolbar vs the MEU-60 arrow-key nudge) |
| Feedback tier (G35) | Local Canon | tool / view / undo / redo / Options: T0 (immediate visual state change, `aria-pressed` / `aria-expanded`); unchanged from MEU-57/60 |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | new | `TOOLBAR_BUTTONS`, `optionGroups` (`OPTIONS_BY_TOOL`) |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | icon toolbar row; `capture-chrome-options` row |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `Disclosure` → `OPTIONS_TOGGLE` (`:1132-1139`) |
| `ui/src/renderer/src/components/ui/Disclosure.tsx` | modify | `DISCLOSURE_PROPS` (additive) |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-65 block (`NEW_TESTIDS`) |
| `ui/tests/unit/capture-toolbar.test.ts` | new | AC-65.1 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify (append only) | AC-65.2, AC-65.3, AC-65.5 |
| `ui/tests/unit/layout-primitives.test.ts` | modify (append only) | AC-65.6 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify (append only + `sampleShot` optional override + `windowSettled`) | AC-65.4, AC-65.5 |

### MEU-66 — `gui-capture-zoom`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Wheel events (`WheelEvent`) | `wheelSteps` (`capture-zoom.ts`) | `deltaMode` ∈ {0,1,2}; `deltaY` finite. An unknown `deltaMode` or non-finite delta yields 0 steps (fail closed). | not a payload |
| Keyboard (`KeyboardEvent`) | `zoomKeyAction` (`capture-zoom.ts`) | closed key table `ZOOM_INPUTS` (c); anything else → `null` (not handled, not prevented) | not a payload |
| Pointer pan | `PAN_GESTURES` in `CaptureViewport.tsx` | `button` 1, or 0 with Space armed | not a payload |
| Zoom state | `ZOOM_STATE` (`useState`) | `scale` ∈ `ZOOM_LADDER`; `ox/oy` always passed through `VIEW_TRANSFORM` | never persisted or sent (`PRODUCT_SCOPE`) |

#### Acceptance Criteria

Call chain: route `/capture` → `CapturePage` → `CaptureViewport` (`ZOOM_STATE`, `ZOOM_INPUTS`) → `viewTransform` / `zoomStep` / `zoomAbout` → `surfaceFromDom` → `SurfacePointer` → `CapturePage.handleSurfacePointer` → `hitTestMarks` / gesture reducer → `POST /captures/{id}/annotate` (Save). The annotate-at-zoom oracle is the POSTed body recorded by the existing E2E fetch ledger (`capture-inbox.test.ts:382-409`).

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-66.1 | unit | `ZOOM_LADDER` equals the cited Chromium list, ascending and unique, and contains `1`. `zoomStep` implements `ZOOM_STEP`: from fit `0.5` in → `2/3`, out → `1/3`; from scale `1` in → `1.1`, out → `0.9`; from scale `5` in → `null`; from fit `20` in → `null`; from fit `0.1` out → `null`. | Research-backed D-14; Spec 09:634 | `zoomStep(fit, 'in', NaN)` and `zoomStep(fit, 'in', 0)` → `null`. A ladder edit that drops `1` or breaks the order fails the test. |
| AC-66.2 | unit | `viewTransform` in `fit` equals `fitScaleOrigin` on the MEU-59 worked example (`s 0.5, ox 0, oy 75`). In `scale` it centres an axis that fits and clamps an axis that overflows (`VIEW_TRANSFORM`). | Spec 09:636; 09:375 | `ox` beyond the range clamps to `0` or `Cw - W*z`. A zero or negative container or image, or a non-finite scale → `null`. The existing AC-59.1 / AC-59.18 tests stay unchanged and green. |
| AC-66.3 | unit | `VIEW_MAP` in both directions at zoom ≠ fit on `ZOOM_EXAMPLE`: `(400,300)` → `(700,375)`, and `(700,375)` → `(400,300)`. A round trip over a 7×7 grid of in-image points is exact to ≤ 0.5 px before rounding. | Spec 09:638 | The fit-only `mapPointerToImage` of the same point gives `(800,450)`, so a caller still using it fails the AC-66.14 oracle. A point outside the zoomed image → `null` (the letterbox rule in the centred-axis case). |
| AC-66.4 | unit | `zoomAbout` on `ZOOM_ABOUT_EXAMPLE` keeps the cursor's image point (`(800,450)`) exactly. Over a sweep of cursor points and ladder steps where no clamp applies, the image point under the cursor changes by ≤ 1 image px. | Spec 09:633 | Where the clamp applies (cursor at the image edge, zooming out), the result is still inside the clamp range and never leaves blank margin on an overflowing axis. |
| AC-66.5 | unit | **Regression lock, expected green at Red:** `hitTestMarks` is already generic in `scale/ox/oy` (`capture-hit-test.ts:26-40,206-221`). The MEU-66 handoff records this AC's Red as `green-at-baseline (lock)`; the Red-capable zoom → hit-test chain is AC-66.11. `hitTestMarks` at zoom: at `s = 4` with `ox = -300, oy = -120`, the handle and body hits use `HANDLE_RADIUS_CSS` / `HIT_RADIUS_CSS` in CSS px (the same CSS distances as AC-60.1 at `s = 1`). | Local Canon AC-60.1; Spec 09:636 | A point 11 CSS px from a shaft at `s = 4` misses. A letterbox point in a centred zoomed-out frame (`s = 0.25`) returns no hit. |
| AC-66.6 | unit | `wheelSteps` implements `WHEEL_STEP`: deltaMode 1 → ±1 per event; deltaMode 0 accumulates (`-40, -40, -40` → one step in after the third); a sign change resets; 250 ms idle resets. `zoomKeyAction` maps the `ZOOM_INPUTS` (c) table. | Research-backed D-18 | `deltaY 0` → 0 steps. `deltaMode 7` or `deltaY NaN` → 0 steps. A key without Ctrl/Meta (`=`, `-`, `0`) → `null`. `Ctrl+Shift+0` → `null`. |
| AC-66.7 | integration | jsdom (`ZOOM_SEAM_SHOT`): the zoom group in `capture-chrome-tools` has `capture-zoom-out`, `capture-zoom-level`, `capture-zoom-in` and `capture-zoom-fit` (`ICON_BUTTON_RULE`). Clicking +/− steps `ZOOM_STATE` per `ZOOM_STEP` about the container centre. The readout shows `ZOOM_READOUT`, and the `ZOOM_OBSERVABLES` change. **Zoom never touches annotations:** after any zoom sequence the `annotations` array is the same object, the history is unchanged (Undo stays disabled from a clean state), and `capture-save` (dirty-only) is not mounted. | Spec 09:633, 09:636 | At the top of the ladder `capture-zoom-in` is disabled; at `fit` `capture-zoom-fit` is disabled. With no shot, all zoom buttons are disabled with title `NO_SHOT_HINT`. A zoom that mounts `capture-save` fails. |
| AC-66.8 | integration | jsdom (`ZOOM_SEAM_SHOT`): `ZOOM_RESET`. Selecting another shot (after the dirty confirm, too) returns the readout to `Fit` and `data-zoom-kind="fit"`. Toggling Original → Annotated → Original keeps the scale. Resizing keeps the scale and re-clamps the offsets. The resize case installs a test-side fake `ResizeObserver` (jsdom has none; the viewport subscribes when it exists, `CaptureViewport.tsx:374-381`), changes the stubbed rect, and invokes the fake's callback, so the Red is the clamp assertion, not a missing trigger. | Spec 09:637 | Deleting the selected shot and selecting the next starts at `Fit`. After a resize, the `ox` that was valid before is clamped into the new range. |
| AC-66.9 | integration | jsdom (`ZOOM_SEAM_SHOT`, userEvent): `Ctrl+=`, `Ctrl+-`, `Ctrl+0` (and the `+`/Numpad variants) act per `ZOOM_INPUTS` (c), and each handled `keydown` has `defaultPrevented === true`. This holds with focus on `body` and with focus on `capture-draw-surface`, whose `onKeyDown` stops propagation. One key press moves exactly one step on either path (`handleViewKey` double-call guard). | Spec 09:633; D-17 | With focus in `capture-color`, `capture-font-size`, `capture-text-draft` or `capture-inbox-path`, the keys change nothing and are not prevented. With the confirm strip open (focus on Cancel) they change nothing (2026-09-28 RULE-3). With no shot, nothing changes. Plain `=` / `-` / `0` change nothing. |
| AC-66.10 | integration | jsdom (`ZOOM_SEAM_SHOT`): `PAN_GESTURES`. At `scale` with an overflowing axis, a middle-button drag of (−50, −30) CSS px moves `ox/oy` by that delta (clamped). Space+primary drag does the same. Neither creates a mark, starts a gesture, pushes history or samples. A plain primary drag in the Arrow tool still creates one arrow. | Spec 09:635; D-15 | At `fit`, a pan leaves the `ZOOM_OBSERVABLES` unchanged. Space while focus is on a toolbar button does not arm pan (the button is not clicked twice; `aria-pressed` behaves as for one click). Pointer-down in the letterbox of a centred axis creates nothing (09:364). |
| AC-66.11 | integration | jsdom (`ZOOM_SEAM_SHOT`): reach `ZOOM_EXAMPLE` through the real inputs. Fit is `0.5`. Ten `Ctrl+=` presses about the centre reach scale `2` (`ox -1200`, `oy -600`), and a middle-drag of `(+200, +150)` gives `ox -1000`, `oy -450`. Then a pointer-down at container `(400,300)` in the Arrow tool yields a `SurfacePointer` with `image = (700,375)`, `scale = 2`, `ox = -1000`, `oy = -450`. The rendered handle radius times `t.s` ≈ `HANDLE_RADIUS_CSS`. The text draft input's `left/top` equals `mapImageToPointerWithView`. `capture-zoom-content` has the `CONTENT_BOX` style. | Spec 09:636; reflection 2026-09-20 RULE-1 | (i) A pointer-down and pointer-up at the **same** container point in the Arrow tool at `s = 2` creates no mark (the zero-length rule, AC-59.5 at zoom). (ii) A 2 CSS px body drag of a selected mark at `s = 2` (below `DRAG_THRESHOLD_CSS`, 3 CSS px = 1.5 image px at `s = 2`) leaves the mark unchanged and pushes no history. (iii) The fit-only mapping of `(400,300)` gives `(800,450)` (the `ZOOM_EXAMPLE` negative oracle), so a stale `fitScale` consumer fails. |
| AC-66.12 | integration | Electron (`ZOOM_SHOT`): one `page.mouse.wheel(0, -WHEEL_STEP_PX)` event over the image at a cursor point steps one level up from Fit. The image pixel under the cursor, computed from `ZOOM_OBSERVABLES` before and after, moves ≤ 1 image px. `Ctrl`+wheel behaves identically. | Spec 09:633 | After the wheel, `BrowserWindow.getAllWindows()[0].webContents.getZoomFactor()` is `1` (no page zoom), and `document.scrollingElement.scrollTop` and `main.scrollTop` are unchanged (wheel prevented). |
| AC-66.13 | integration | Electron: the buttons and keys. `capture-zoom-in` ×2, `capture-zoom-out` ×1 and `capture-zoom-fit` change the readout as `ZOOM_STEP` predicts. `Control+Equal`, `Control+Minus` and `Control+Digit0` do the same in two focus states: focus on `capture-draw-surface` (the `stopPropagation` path) and focus on `body` (the `window` path). | Spec 09:633; D-17 | **Electron default-menu oracle:** after every key, `webContents.getZoomFactor()` is `1`. If it is not after the renderer prevents the key, Stop condition S5 applies. With focus in `capture-color`, `Control+Minus` leaves the readout unchanged. |
| AC-66.14 | integration | Electron annotate-at-zoom on `ZOOM_SHOT`. Step to the ladder level `1` (the readout shows `100%`). Pan with a middle-drag so the image point `(1200, 800)` is inside the frame. Draw an Arrow from the container point of image `(1200,800)` to that of `(1260,830)`, computed from `ZOOM_OBSERVABLES`. Save. The POSTed annotation (fetch ledger) has `from == [1200,800]` and `to == [1260,830]`, and the rendered SVG line has the same `x1/y1/x2/y2`. Then zoom out to Fit and draw a second arrow. Its POSTed points match the fit mapping (MEU-59 unchanged). | Spec 09:638; Local Canon AC-59.12 pattern | The container point used would map to a different image point under the fit-only mapping (asserted ≥ 50 px apart), so a mapping that ignores zoom fails. The first arrow's stored points are identical after the Fit zoom-out (stored annotations never rewrite). |
| AC-66.15 | integration | Electron: `ZOOM_RESET` and pan in the real app. Zoom in, then select another shot: the readout is `Fit`. Space+drag at `100%` moves the observables and creates no annotation (the ledger has no new POST, and `capture-annotation` count is unchanged). | Spec 09:635, 09:637 | A pan followed by Save posts nothing new (Save is not mounted because nothing is dirty). |
| AC-66.16 | unit | `ZOOM_HELP_SENTENCE` is in the `four-tools` help body; `HELP_PIXEL_SENTENCE` and `HELP_EDIT_SENTENCE` are still there verbatim. | 09:155-157; D-21 | Removing either existing sentence fails AC-59.20/60.15 (unchanged). |
| AC-66.17 | unit | `NEW_TESTIDS` (MEU-66 block) registered after the MEU-51 marker. | Local Canon AC-51.6 | as AC-65.7 |
| AC-66.18 | integration | jsdom + Electron (added by A-4 after `CAPTURE_LOOK` L5): a **mouse** click on a toolbar button (`event.detail > 0`) moves focus to `capture-draw-surface`, so a following Space+drag pans (`ZOOM_OBSERVABLES` change) and creates no mark. Keyboard activation (Enter or Space on the focused button) keeps focus on the button. | Human-approved A-4; Spec 09:635; D-15 | Keyboard: focus `capture-tool-box`, press Enter: focus stays on the button, and a later Space does not arm pan (the AC-66.10 negative still holds). Without the hand-off, the L5 sequence (click Arrow, Space+drag) draws an arrow. |
| AC-66.19 | integration | Electron (added by A-5): at `DEFAULT_WINDOW` the Capture page fills `main` and the draw surface grows into it. The page's bottom is within 1 px of `main`'s bottom, `main` does not scroll vertically, and the surface is taller than its `min-h-[200px]` floor. | Human-approved A-5 (Mat's observation 2); Local Canon (Downloader/Convert/Transcript `h-full` page columns) | With the old content-sized page column, the page ends above `main`'s bottom and the surface stays at about 200 px. |

**Test-ID migration (MEU-66).**

| Existing ID | Migration | Detail |
|---|---|---|
| `capture-draw-surface` | change | `overflow-hidden`; carries `ZOOM_OBSERVABLES`; wheel / pan listeners; rect contract unchanged |
| `capture-viewport-image`, the `svg` overlay | move | into `capture-zoom-content` (`CONTENT_BOX`) |
| `capture-handle-from/-to/-body`, `capture-text-draft` | keep | positioned by `VIEW_TRANSFORM` |
| new: `capture-zoom-in`, `capture-zoom-out`, `capture-zoom-fit`, `capture-zoom-level`, `capture-zoom-content` | add | MEU-66 block |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Wheel / Ctrl+wheel / buttons / keys | Human-approved + Research-backed | 09:633; grouping D-6 (plain wheel zooms) |
| Level ladder and bounds | Research-backed | D-14 (`ZOOM_LADDER`, Chromium) |
| Fit as a level | Spec | 09:634 "always includes `Fit` and `100%`" |
| Wheel normalization | Research-backed | D-18 |
| Pan mechanism | Research-backed + Local Canon | D-15 |
| Mapping at zoom | Spec + Local Canon | 09:636; `VIEW_TRANSFORM`, `VIEW_MAP` |
| Zoom about centre for buttons and keys | Research-backed | D-19 |
| Reset rules | Spec + Local Canon | 09:637; D-16 |
| Key scope vs inputs and the confirm strip | Local Canon | D-17; reflection 2026-09-28 RULE-3 |
| Whole-window zoom conflict | unresolved until execution | AC-66.13 oracle; Stop condition S5; D-22 draft |
| Feedback tier (G35) | Local Canon | zoom / pan: T0 (immediate re-render + `ZOOM_READOUT` `aria-live`) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-zoom.ts` | new | `ZOOM_LADDER`, `zoomStep`, `zoomAbout`, `wheelSteps`, `zoomKeyAction` |
| `ui/src/renderer/src/features/capture/capture-fit-map.ts` | modify (additive) | `viewTransform`, `mapPointerWithView`, `mapImageToPointerWithView`; existing exports unchanged |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modify | zoom rows of `TOOLBAR_BUTTONS` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `ZOOM_STATE`, `CONTENT_BOX`, `SURFACE_POINTER`, `ZOOM_INPUTS`, `PAN_GESTURES`, `ZOOM_READOUT`, `ZOOM_OBSERVABLES`; new `shotId` prop |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | passes `shotId={selectedId}` (the only change) |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | `ZOOM_HELP_SENTENCE` |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-66 block |
| `ui/tests/unit/capture-zoom.test.ts` | new | AC-66.1, AC-66.4, AC-66.6 |
| `ui/tests/unit/capture-fit-map.test.ts` | modify (append only) | AC-66.2, AC-66.3 |
| `ui/tests/unit/capture-hit-test.test.ts` | modify (append only) | AC-66.5 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify (append only) | AC-66.7 – AC-66.11 |
| `ui/tests/unit/capture-help-content.test.ts` | modify (append only) | AC-66.16 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify (append only) | AC-66.12 – AC-66.15 |
| `ui/tests/e2e/download-queue.test.ts` | modify (TA-3, A-6) | W1-8 hardening after `WINDOWS_GATE` attempt 2: `test.slow()` and two `expect.poll` seam reads, same expected counts |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Icon conversion or overflow handling for the third chrome row, `capture-chrome-marks` (mark list, Remove mark, Body/Tail/Head, nudge pad, per-shot actions) | out-of-scope | — | 09:619-621 scope the icon rule to "tool, history and view buttons" and the overflow rule to "the tools row". The mark list's "labeled buttons" are Human-approved 2026-09-20 (09:389). |
| Apply to image / flatten / revert buttons | deferred | MEU-67 | Session 30 (grouping `:103-108`); 09:642-654 |
| Zoom as a persisted setting, or zoom remembered per shot | out-of-scope | — | 09:637 "not a setting"; "reset to `Fit` on shot change" |
| Touch pinch / multi-touch gestures | out-of-scope | — | 09:633 lists wheel, buttons and keys only. A Windows precision-touchpad pinch arrives as Ctrl+wheel and is covered by `WHEEL_STEP`. |
| Command-palette entries for zoom | out-of-scope | — | 09:633 (no palette control); `gui-actions-index.md` rows are added with Palette `no` |
| Retuning the MEU-59 fit mapping, arrowhead or text-anchor formulas, or the bake | out-of-scope | — | 09:636 "stored annotations never rewrite"; 09:401 (MEU-60 locks) |
| Replacing or removing the Electron application menu | out-of-scope | — | `PRODUCT_SCOPE` (no `ui/src/main` change). It is reachable only through Stop condition S5 as a separate human decision (D-22 draft). |
| Editing the locked Phase 11 CP rows / mockup inventory in `11-page-layout.md` or `docs/proposals/2026-09-03-capture-page-layout-mockup.html` | out-of-scope | — | `layout-canon.test.ts` AC-50.1 (`:91-103`) and AC-50.4 (`:130-145`) lock them to MEU-5x owners and the mockup text. Row 9 adds a prose pointer instead (Session 27 precedent, `2026-09-30-tts-repair/implementation-plan.md` §BUILD_PLAN.md Audit item 2). |
| MCP live audit of Capture | deferred | MEU-68 | Session 28; this session changes no MCP surface (`PRODUCT_SCOPE`) |

## BUILD_PLAN.md Audit

The D3 hub is `docs/BUILD_PLAN.md` + `docs/build-plan/`. Task row 9 makes these edits, with exact validation (`validate-task.sh hub`):

1. `09-screenshot-capture.md`:
   - §Viewport tools, line 149 ("Zoom: fit-to-viewport default; scroll zoom optional in MVP …"): append a pointer to §Viewport zoom (MEU-66). The fit-mapping sentence stays.
   - §Viewport zoom "Levels" row (`:634`): fix the ladder to `ZOOM_LADDER` with its Chromium citation, tagged "Session 29 plan D-14", as the row itself requires ("fixed at plan time with a cited source").
   - §Viewport zoom: add one row each for the pan gestures, the wheel step and the key scope, tagged "Session 29 plan D-15", "… D-18" and "… D-17". Plan D-ids collide across plans, so the canon always names the plan (Review R1 F5g).
   - §Viewport toolbar icons and Options: add one row naming `OPTIONS_BY_TOOL` ("Session 29 plan D-12") and the `size="sm"` icon rule ("Session 29 plan D-9").
   - §MEUs table (`:674-687`): add the missing rows for MEU-65, MEU-66 and MEU-67 (registered in the matrix 9.10-9.12 but absent here). This is hub drift the project revealed.
2. `11-page-layout.md` §Capture page layout (`:87-89`): one prose sentence after `:89` saying the header disclosure is titled **Options** since MEU-65 and pointing to 09 §Viewport toolbar icons and Options. The CP decision rows (`:41-46`) and the mockup-inventory CP rows (`:263-286`) are **not** edited (the AC-50.1/50.4 lock). Row 9 re-runs `layout-canon.test.ts`.
3. `gui-actions-index.md`: append `capture:zoom_in`, `capture:zoom_out` and `capture:zoom_fit` after `capture:redo` (`:79`), each with Palette `no`, REST/IPC `local view`, status `specified`, source `09`. Row 9 re-runs `gui-actions-audit.test.ts`.
4. `docs/BUILD_PLAN.md`: the AUTOGEN status regions are re-rendered by `tools/meu_status.py render` (H1-3 / H2-2) and checked with `render --check`.

## Verification Plan

Every command is registered in `validate-task.sh` (container) and `validate-task.ps1` (Windows), from one stage list. The stage ids match exactly (`windows-gate-check` asserts the order).

### 0. Plan-local static verifier (planning time; re-run in `pregate`)

`python3 docs/execution/plans/2026-10-01-capture-viewport-chrome/plan_checks.py static` is stdlib-only and read-only, and runs no product code (GUARDRAILS SIGN 1 carve-out). It checks:

- the task table's structure and its dependency graph;
- that every `validate-task.sh` check invoked from `task.md` exists;
- that the `.sh` `windows-gate-check` order equals the `.ps1` stage ids;
- that `AUDIT_SRC` and the audit pattern are identical in both scripts;
- that `GATED_PATHS` and `COUNT_FLOORS` equal their executable copies;
- that every `D-n` and `AC-6x.n` named in `task.md` has a definition site (an AC table row, a `decision_log` id, a `### D-n` heading, or a grouping §8 row), not merely a prose mention;
- that `ZOOM_LADDER` here equals the Chromium array quoted in D-14.

Planning receipts are recorded in §Planning receipts below.

### 1. Prerequisites and baseline (row 0)

`validate-task.sh prereq`, then `electron-setup` and `baseline`. `baseline` writes `baseline.sha` (HEAD before any product edit) and collects the baseline pytest failed set and the Vitest and Electron receipts.

### 2. Red (per MEU)

- `red65`:
  - Vitest assertion Red (`AC-65`; the new `capture-toolbar.test.ts` may fail only with a missing-module message);
  - then the Electron Red after a fresh build;
  - then `require_failed_title … AC-65.4 toBeLessThanOrEqual`.
- `red66`:
  - Vitest assertion Red (`AC-66`; the new `capture-zoom.test.ts` may fail only with a missing-module message);
  - then the Electron Red (`AC-66`) after a fresh build.

### 3. Targeted Green (after each production edit)

`green65`, `green66-unit` and `green66` run the targeted suites plus the regression neighbours named in `validate-task.sh` (`REGCAP`: every existing capture unit suite, `layout-primitives`, `layout-canon`, `gui-actions-audit`, `e2e-wiring`, `tts-page.behavior` for the shared `Disclosure`).

### 4. Targeted MEU gates (rows 4 and 8)

`gate65` / `gate66`:

- UI typecheck, lint, Vitest (`REGCAP` + targeted) and build;
- the whole `capture-inbox.test.ts` under Electron, plus `layout-primitives.test.ts` (Disclosure harness) and `tts-generate.test.ts` (TTS Cleanup disclosure) under Electron;
- `--repeat-each=20` over the specs named by `REPEAT_GREP` (defined once in `validate-task.sh`) into `$RECEIPTS_DIR/s29-repeat-*`. These are the touched and pointer-driven specs (cloud-local §3.1 item 2; reflection 2026-09-28 ADD).

### 5. Product-scope proof (H1-4)

`validate-task.sh api-scope` proves `PRODUCT_SCOPE`:

- `git diff --name-only $(cat baseline.sha) -- packages mcp-server openapi.committed.json tools ui/src/main` is empty, and so is the matching `git status --porcelain`;
- `export_openapi.py --check` passes;
- every changed `ui/` file is in a Files Modified table.

There is no OpenAPI regeneration (G8 does not apply, since `packages/api/` is unchanged).

### 6. Container pre-gate (H1-2, non-authoritative)

`validate-task.sh pregate` runs every D6 stage that can run here:

- input identity;
- `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `plan-static`, `task-contract`;
- `pytest_env_ok`, `vitest_env_ok`;
- `ui-build`, `ui-harness-build`, `mcp-build`, `mcp-tests`, `openapi`, `state-render`;
- `electron_env_ok`;
- `source-audit` over `AUDIT_SRC`.

### 7. `WINDOWS_GATE` + `CAPTURE_LOOK` (H1-6, authoritative, local)

`validate-task.ps1 -Check windows-gate` runs the D6 stages. The canonical order is the `order` list in `validate-task.sh` `windows-gate-check`; `plan_checks.py static` asserts that the `.ps1` `$stages` ids equal it. The script records the preflight fields (schema `s29-windows-gate.v1`).

`CAPTURE_LOOK` is the human visual checklist L1–L6 in [local-requests.md](local-requests.md) §GATE. Mat runs it on the same commit after the gate and returns one line per item. `validate-task.sh look-check` refuses unless all six are recorded with a result and provenance in `walkthrough.md` §CAPTURE_LOOK. Any `fail` is a Decision Brief (cloud-local §3.5), never a silent fix.

`validate-task.sh windows-gate-check` validates the JSON:

- schema, clean tree, stage order and exits, `COUNT_FLOORS`, flaky;
- code identity over `GATED_PATHS`.

### 8. Closeout (H1-5, H1-7, H2)

- `validate_closeout_artifacts.py --ac-coverage-only` per handoff;
- `review-check`;
- the reflection validator with `--decision-source` for the plan, handoffs and grouping;
- `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped: `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent (`gui-refs-not-shipped`, create-plan §4A note). The applicable canon is used instead:

| Element | Variant / size | States | Standard | E2E |
|---|---|---|---|---|
| Tool buttons ×5 | `toolVariant` (primary/outline), `sm` | enabled, disabled+`NO_SHOT_HINT`, `aria-pressed` | G34, UX1 (segmented group), UX2, G1 | AC-65.4, AC-57.10 (existing) |
| Undo / Redo | `ghost`, `sm` | enabled / disabled | G34 | AC-57.10 (existing), AC-66.15 |
| Original / Annotated | `toolVariant`, `sm` | `aria-pressed`, Annotated disabled without a bake | G34, UX1 | AC-60.12 (existing) |
| Zoom − / + / Fit | `ghost`, `sm` | enabled / disabled at bounds / no shot | G34, UX2 | AC-66.13 |
| `ZOOM_READOUT` | text, `aria-live` | `Fit` / `N%` | G26 | AC-66.12–66.14 |
| Options toggle | `secondary`, `md` (Disclosure default size) | `aria-expanded`, chevron state | G26, G31, G34 | AC-65.5 |
| Option inputs / named select | unchanged; named select keeps `getG30Styles()` | unchanged | G30, G32 | AC-65.4 |

G32/G33 (tokens; no `transition-all`; no raw hex) are enforced by `source-audit`. Zoom is not animated (G33 forbids animating `width`/`height`/`left`/`top`). E2 is met: every new interactive element has a registered test id and an Electron assertion.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `prereq` refuses: a graph directory appeared, a dependency MEU (57, 59, 60) is not `approved`, or MEU-65/66 is not `pending` | Stop. Re-run the context-tool gate with the human, or report. |
| S2 | The census finds an existing expectation this design contradicts (`TEST_AMENDMENTS` is empty) | Stop for the human with a Decision Brief naming the test and the minimal amendment. No test edit. |
| S3 | A Red is not an assertion failure (collection or import error outside the declared new test file) | Fix the test setup only, then re-prove Red. |
| S4 | The `AC-65.4` spec does not go Red on the pre-change layout in the container | Stop MEU-65 Red. Record the measured widths, then present a Decision Brief (for example: xvfb fonts are narrower than the target's; run the Red on Windows as a `LOCAL_REPRO`). Never weaken the assertion. |
| S5 | After implementation, the AC-66.13 / AC-66.12 page-zoom oracle fails: `getZoomFactor() ≠ 1` even though the renderer prevented the key or wheel | Stop MEU-66 Green for that AC. Present D-22 (draft below), recommendation first. `ui/src/main` stays untouched until Mat answers. |
| S6 | Annotate-at-zoom (AC-66.14) can pass only by changing a fit-mode output of `capture-fit-map.ts` (AC-59.1/59.18 or the 09:375 example) | Stop. That would reopen MEU-59's locked mapping; present a Decision Brief. |
| S7 | A gate failure that is not a product defect | Handle per cloud-local §3.5: a Decision Brief and an A-n row in `human-gate-decision.md`. No self-authorized test change. |
| S8 | Review cap (plan 3, execution 6), or the reviewer is unavailable | HARD STOP with TL;DR (create-plan §5d). |

## Decision Log

Carried from the grouping (stage `grouping`, reflection carry-forward). Session 29's own row is **D-6** (wheel semantics: plain wheel zooms about the cursor, Ctrl+wheel identical), plus **D-2** and **D-5** for every session. The H2-1 reflection still carries **every** grouping §8 row, D-1 to D-7, with stage `grouping`, because `validate_closeout_artifacts.py` requires the whole §8 table when the grouping is a decision source (Session 27 Review R2-1). The triage decisions in `known-issues.yaml` (D-10 to D-13, D-16, D-17 on the three Capture issues) are cited in prose only: their ids collide with grouping and plan ids (Session 27 Review R1 F5).

Planning decisions:

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "Plan Session 29 before Session 28 (mcp-live-audit)?"
    resolution: human
    class: two-way
    chosen: "Yes — plan and run Session 29 now"
    source_tag: Human-approved
    precedents: [".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md:72 — sessions are sequenced by session, not by dependency", ".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md:135 — every dependency of MEU-65 is approved; MEU-66 waits only on MEU-65"]
    research: { engine: none, sources: [] }
    reasoning: "The user asked for Session 29 by name. Nothing in Session 29 depends on MEU-68, and grouping D-4's reason for running the audit first (a regression net for Sessions 29-31) is weakest here, because Session 29 changes no MCP or REST surface. Session 28 later baselines the same Capture MCP surface either way."
    human_message_reference: "USER_EXPLICIT 2026-10-01 '/create-plan for Session 29 (Capture viewport/chrome)'"
  - id: D-9
    stage: planning
    question: "How are the icon buttons sized and built?"
    resolution: autonomous
    class: two-way
    chosen: "Button size='sm' whose only child is an aria-hidden lucide icon (ICON_BUTTON_RULE); not the Button `icon` prop"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/components/ui/Button.tsx:22,58 — sm = h-7; icon = p-0 aspect-square (no height class)", "ui/tests/unit/capture-page.behavior.test.ts:1044-1049 — AC-57.5 pins h-7 on every tool", "docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md TM-10 — tools moved to sm/h-7"]
    research: { engine: none, sources: [] }
    reasoning: "size=sm keeps the canonical G34 variant/size and every AC-57.5/AC-39.28 height assertion green, so TEST_AMENDMENTS stays empty. The icon prop would need two TA rows and gives 28 px squares, a visual change nobody asked for. A sm icon button is about 36 px wide, so the full tools row (9 icons + zoom group) fits in roughly 560 px."
  - id: D-10
    stage: planning
    question: "role=toolbar with roving tabindex (APG), or labelled groups?"
    resolution: autonomous
    class: two-way
    chosen: "Keep role='group' + aria-label segments (UX1); no role=toolbar and no arrow-key roving"
    source_tag: Research-backed
    precedents: ["docs/build-plan/09-screenshot-capture.md:395 — Arrow keys nudge the selected mark whenever annotation controls own focus (Human-approved 2026-09-20)", "ui/src/renderer/src/features/capture/CapturePage.tsx:91-107 — annotationOwnsFocus covers every focus inside capture-viewport", ".agent/docs/emerging-standards.md UX1 — role=group segmented buttons with aria-pressed"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/ARIA/apg/patterns/toolbar/ — role=toolbar implies Left/Right arrow focus movement with roving tabindex"] }
    reasoning: "An APG toolbar takes over the arrow keys, which the Human-approved MEU-60 keyboard contract already gives to nudging the selected mark while focus is in the viewport. Announcing role=toolbar without arrow navigation would mislead screen-reader users. Labelled groups with aria-pressed are the existing UX1 canon, and spec 09:619 asks for title + aria-label + aria-pressed, all of which are kept."
  - id: D-11
    stage: planning
    question: "Which icons and accessible names?"
    resolution: autonomous
    class: two-way
    chosen: "TOOLBAR_BUTTONS (lucide 0.400.0); accessible names equal today's visible labels"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/components/layout/NavRail.tsx:1 — lucide-react is the nav rail's icon set", "ui/src/renderer/src/features/capture/capture-help-content.ts:27 — help text names Select, Undo and redo, Sample original image, Apply"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/ARIA/apg/patterns/toolbar/ — icon character is aria-hidden; the button carries the label"] }
    reasoning: "Keeping the names lets the help text, getByRole queries and the user's vocabulary stay valid while only the visual changes. The icons are lucide's literal metaphors (pointer, arrow, square, highlighter, type, undo/redo, image/layers, zoom). Every name was checked in the locked 0.400.0 typings."
  - id: D-12
    stage: planning
    question: "What does the contextual options row show for each tool?"
    resolution: autonomous
    class: two-way
    chosen: "OPTIONS_BY_TOOL — color for every tool; stroke only where a stroke_width exists (arrow, box, select with none/arrow/rect); text options for the text tool or a selected text mark"
    source_tag: Research-backed
    precedents: ["docs/build-plan/09-screenshot-capture.md:343-346 — highlight has opacity, not stroke_width; arrow/rect have stroke_width", "ui/src/renderer/src/features/capture/CapturePage.tsx:739-753 — changeStroke edits only arrow/rect", "docs/build-plan/09-screenshot-capture.md:393 — Apply color with no selection updates the next-mark default, so Select uses color", "ui/src/renderer/src/features/capture/CaptureViewport.tsx:343 — showTextChrome rule"]
    research: { engine: web_search, sources: ["https://learn.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-2013/31d796hd(v=vs.120) — tool options live in an options bar (triage D-17 source)", "https://help.syncfusion.com/xamarin/image-editor/toolbarcustomization — per-tool option panels"] }
    reasoning: "Options bars show what the active tool consumes. The only visible change from today is that Highlight (and Select on a highlight) stops showing a Stroke field it never used. Select with nothing selected keeps Stroke, because today it sets the next-mark default and the W9-3 Electron case fills it in that state. Width budget at DEFAULT_WINDOW (viewport about 810 px after the nav rail, page padding and the 200 px filmstrip): color group about 560 px with the w-24 hex field, plus stroke (about 110 px) or text options (about 200 px). Compaction lever, decided now and used only if AC-65.4 still fails on the options row at Green: the 'Sample original' button becomes a Pipette icon button with aria-label and title 'Sample original image' (ICON_BUTTON_RULE). Any use is recorded in the MEU-65 handoff Decision Log. Nothing else may be dropped or hidden to pass NO_OVERFLOW."
  - id: D-13
    stage: planning
    question: "How does the Capture header toggle become an Options button without touching the other Disclosure users?"
    resolution: autonomous
    class: two-way
    chosen: "Three optional Disclosure props (variant, icon, chevron) with defaults equal to today; Capture passes secondary + SlidersHorizontal + chevron"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/components/ui/Disclosure.tsx:16-35 — ghost Button, title only", "ui/tests/unit/tts-page.behavior.test.ts:245,253 and ui/tests/e2e/tts-generate.test.ts:464,469 — exact Cleanup toggle text", "ui/tests/unit/layout-primitives.test.ts:33-54 — AC-51.1 primitive accessible name 'Advanced'"]
    research: { engine: none, sources: [] }
    reasoning: "Changing Disclosure's default rendering would break exact-text and primitive assertions on four other pages. A capture-local fork would duplicate the aria-controls/hidden contract. Additive props keep a single primitive and leave the other users' DOM byte-identical (AC-65.6)."
  - id: D-14
    stage: planning
    question: "What is the zoom level ladder (09:634 requires bounds fixed at plan time with a cited source)?"
    resolution: autonomous
    class: two-way
    chosen: "ZOOM_LADDER = Chromium kPresetBrowserZoomFactors, 25% to 500%, plus Fit as a separate level"
    source_tag: Research-backed
    precedents: ["known-issues.yaml CAPTURE-VIEWPORT-ZOOM triage D-11 — proposed fit / 25-400% steps", "docs/build-plan/09-screenshot-capture.md:634 — must include Fit and 100%"]
    research: { engine: native, sources: ["https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/common/page/page_zoom.cc — kPresetBrowserZoomFactorsArray {0.25, 1/3, 0.5, 2/3, 0.75, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0}; min 0.25, max 5.0 (read 2026-10-01)", "https://www.photoshopessentials.com/basics/photoshop-zoom/ — editors step through fixed presets (25, 33.3, 50, 66.7, 100, 200 …)"] }
    reasoning: "The renderer is Chromium, so Ctrl+=/Ctrl+- users already know these steps from every browser. The ladder includes 100% and reaches 500% (5 screen px per image px), enough to place a mark on a single pixel of a capture. Photoshop's 3200% ceiling targets pixel editing, which Capture does not do. The triage's 25-400% proposal had no source, and this one matches it with a source. Two-way: one constant."
  - id: D-15
    stage: planning
    question: "How does the user pan a zoomed image?"
    resolution: autonomous
    class: two-way
    chosen: "PAN_GESTURES — Space+drag and middle-button drag move a clamped offset inside an overflow-hidden surface; no native scrollbars"
    source_tag: Research-backed
    precedents: ["docs/build-plan/09-screenshot-capture.md:635 — 'scrolls/drag-pans'", "ui/tests/unit/capture-page.behavior.test.ts:122-135,1246-1268 — jsdom geometry stubs the surface rect as the container", "grouping D-6 — plain wheel zooms, so the wheel cannot also scroll"]
    research: { engine: native, sources: ["https://helpx.adobe.com/photoshop/using/tool-techniques/hand-tool.html — hold Space to pan with the Hand tool", "https://www.autohotkey.com/boards/viewtopic.php?t=46697 — middle-button panning is the common convention in image/design tools"] }
    reasoning: "With plain wheel bound to zoom (grouping D-6), native scrollbars could be dragged but never wheeled. A scroll container would also make rect != container, so every SurfacePointer would need scroll offsets and the jsdom rect contract would change. A clamped offset keeps one transform (VIEW_TRANSFORM) and the existing geometry contract. Space+drag and middle-drag are the two conventions users bring from editors. The readout tooltip (ZOOM_PAN_HINT) and the help sentence name both."
  - id: D-16
    stage: planning
    question: "Who owns the zoom state, and when does it reset?"
    resolution: autonomous
    class: two-way
    chosen: "CaptureViewport owns ZOOM_STATE; it resets on a shotId change and is kept across Original/Annotated and resizes (ZOOM_RESET)"
    source_tag: Local Canon
    precedents: ["docs/build-plan/09-screenshot-capture.md:637 — reset on shot change; not a setting", "docs/build-plan/09-screenshot-capture.md:368 — original and annotated share the original pixel space"]
    research: { engine: none, sources: [] }
    reasoning: "Zoom is presentation state, and the viewport already measures the container. Keeping it there leaves CapturePage's gesture reducer untouched (it receives zoom-aware SurfacePointers). Comparing a baked view at the same zoom is the reason the Original/Annotated toggle exists."
  - id: D-17
    stage: planning
    question: "Where do Ctrl+=/Ctrl+-/Ctrl+0 apply, given G11 and the MEU-60 key scope?"
    resolution: autonomous
    class: two-way
    chosen: "ZOOM_KEY_SCOPE — a CaptureViewport window keydown, active with a shot selected, never in text-entry focus or with the confirm strip open; handled keys preventDefault"
    source_tag: Local Canon
    precedents: [".agent/docs/emerging-standards.md G11 — AppShell owns shortcuts that open modals/panels (zoom opens none)", "docs/execution/reflections/2026-09-28-p11-capture-settings-reflection.md RULE-3 — a modal-like strip is excluded from every global key handler", "ui/src/renderer/src/components/layout/AppShell.tsx:50-75 — no existing Ctrl+=/-/0 binding"]
    research: { engine: none, sources: [] }
    reasoning: "The keys mirror on-page buttons, so they belong to the page that owns the buttons (G11 covers global panels). Excluding text inputs keeps '-'/'0' typing safe in the hex and font fields. Excluding the confirm strip applies the earned RULE-3. Not using the arrow keys leaves the MEU-60 nudge contract alone."
  - id: D-18
    stage: planning
    question: "How many zoom steps does one wheel movement make (mouse notches vs touchpad streams)?"
    resolution: autonomous
    class: two-way
    chosen: "WHEEL_STEP — one step per line/page-mode event; pixel-mode deltas accumulate to WHEEL_STEP_PX = 100 per step"
    source_tag: Research-backed
    precedents: ["docs/build-plan/09-screenshot-capture.md:633 — wheel zooms about the cursor"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/API/WheelEvent/deltaMode — DOM_DELTA_PIXEL vs LINE vs PAGE", "https://developer.mozilla.org/en-US/docs/Web/API/WheelEvent/deltaY — magnitude is device-dependent"] }
    reasoning: "One step per raw event would make a precision touchpad, which emits dozens of small pixel deltas, jump the whole ladder. Accumulating pixel deltas makes a mouse notch one step while a touchpad needs a deliberate swipe. AC-66.12 drives exactly one WHEEL_STEP_PX wheel event. CAPTURE_LOOK L3 confirms one real notch = one step on Mat's Windows mouse, and its failure is a Decision Brief, not a silent retune."
  - id: D-19
    stage: planning
    question: "What point do button and keyboard zooms anchor on?"
    resolution: autonomous
    class: two-way
    chosen: "The container centre; the wheel anchors on the cursor"
    source_tag: Research-backed
    precedents: ["docs/build-plan/09-screenshot-capture.md:633 — wheel about the cursor; buttons and keys mirror it"]
    research: { engine: native, sources: ["https://www.photoshopessentials.com/basics/photoshop-zoom/ — keyboard zoom keeps the view centred; scrubby/wheel zoom follows the pointer"] }
    reasoning: "Buttons and keys have no pointer position on the image. Centre-anchoring keeps the visible middle steady, which is the editor and browser behaviour."
  - id: D-20
    stage: planning
    question: "How do Electron tests compute the aimed screen point at an arbitrary zoom/pan?"
    resolution: autonomous
    class: two-way
    chosen: "ZOOM_OBSERVABLES data attributes on capture-draw-surface, written from VIEW_TRANSFORM and never read by production code"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/capture/CaptureViewport.tsx:734 — data-overlay-ready readiness observable (CAPTURE_READY_SIGNAL)", "ui/tests/e2e/capture-inbox.test.ts:294-303 — tests re-derive FIT_MAP inline today"]
    research: { engine: none, sources: [] }
    reasoning: "Re-deriving the zoom/pan transform inside the test would copy production logic, and a shared bug would pass. Reading the transform the app actually used, then asserting on the independent observable (the POSTed pixel), keeps the oracle honest. AC-66.14's fit-only comparison guards against a transform that is self-consistent but unused."
  - id: D-21
    stage: planning
    question: "How does the user discover pan and the zoom keys?"
    resolution: autonomous
    class: two-way
    chosen: "ZOOM_PAN_HINT as the readout's title, and ZOOM_HELP_SENTENCE in the four-tools help body"
    source_tag: Local Canon
    precedents: ["docs/build-plan/09-screenshot-capture.md:155-157 — HelpCard topics are a minimum list", "ui/tests/unit/capture-help-content.test.ts:7-9 — existing sentences pinned verbatim, appending is safe"]
    research: { engine: none, sources: [] }
    reasoning: "Space-drag and middle-drag are invisible gestures. One tooltip and one help sentence document them without adding a visible control to a row whose budget is no-overflow."
```

No planning question needs the human before execution. The execution message may veto any autonomous row (User Review Required item 3).

### D-22 (draft; raised only by Stop condition S5) — the Electron default menu zooms the whole window on Ctrl+= / Ctrl+- / Ctrl+0

**Recommendation:** A — in `ui/src/main/index.ts`, handle the main window's `before-input-event` so that `Ctrl`/`Cmd` + `=`/`+`/`-`/`0` are swallowed only while the renderer has reported (over the existing preload IPC) that the Capture page has a shot selected. The renderer then performs the image zoom, and the whole-window zoom keeps working on every other page. **Reversibility:** two-way. **Default if unanswered:** C until answered (ship MEU-66 with the wheel and buttons only, and mark the keyboard-mirror rows `[B]`).
**Precedents:** `ui/src/main/index.ts:455-468` (the single BrowserWindow); `ui/src/main` has no `Menu.setApplicationMenu` (survey 2026-10-01). **Research:** native; https://www.electronjs.org/docs/latest/api/web-contents#event-before-input-event ("Calling `event.preventDefault` will prevent the page `keydown`/`keyup` events and the menu shortcuts").

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| A. Scoped `before-input-event` guard (recommended) | Electron `before-input-event` docs | — | — | ✅ |
| B. Install an app menu without the zoom roles | https://www.electronjs.org/docs/latest/api/menu#default-menu | Simplest main-process change | Removes whole-window zoom (an accessibility affordance) from every page; changes app-wide behaviour for one page | ⚠️ |
| C. Drop the keyboard mirror; keep wheel + buttons | 09:633 | No main-process change | Departs from the Human-approved spec row (`Ctrl+=` / `Ctrl+-` / `Ctrl+0`); needs a spec amendment | ❌ |

### D-29 (execution) — CAPTURE_LOOK 2 is reused for WINDOWS_GATE attempt 3/4

Defined in full in the MEU-66 handoff `decision_log` (`.agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-66-handoff.md`). TA-3 changes only `ui/tests/e2e/download-queue.test.ts`, and `ui/src` is byte-identical to `c2452aa`, the code the attempt-2 look ran on. The look is therefore not repeated (A-6).

## Round 1 Review Corrections

Plan review Round 1 (`.agent/context/handoffs/2026-10-01-capture-viewport-chrome-plan-critical-review.md`, Fable 5.1 subagent) returned `changes_required`: 1 High (blocking), 1 Medium and 3 Low, plus five non-blocking observations. All were applied as document corrections; no code changed. The blast-radius census receipt, with a disposition per hit, is [review-r1-census.md](review-r1-census.md).

| Finding | Correction |
|---|---|
| F1 High (AC-66.11 freezes a non-existent draw threshold into Red) | AC-66.11's negatives are now what MEU-59/60 actually guarantee at zoom. (i) A same-point down/up in the Arrow tool creates no mark (zero length). (ii) A 2 CSS px body drag of a selected mark leaves it unchanged and pushes no history (`DRAG_THRESHOLD_CSS` = 3 CSS px = 1.5 image px at `s = 2`). (iii) The fit-only mapping is the oracle. `SURFACE_POINTER` now states once that the draw path has no threshold (09:366) and that no row adds one. |
| F2 Medium (MEU-66 jsdom Red/Green mechanics) | (a) AC-66.5 is labelled a regression lock, expected green at Red; the MEU-66 handoff records it as `green-at-baseline (lock)`, and AC-66.11 is the Red-capable chain. (b) New `ZOOM_SEAM_SHOT` (1600×900 in an 800×600 stub, fit 0.5) is referenced by AC-66.7–66.11. (c) AC-66.8's resize case drives a test-side fake `ResizeObserver`. |
| F3 Low (`GATED_PATHS` gap; look regex) | `GATED_PATHS` now also lists `06-gui.md`, `10-queue-card-ui.md`, `build-priority-matrix.md`, `docs/proposals` and the three p10 plan folders. The "exactly" claim is replaced by the sweep it came from. The plan and `.sh` lists stay equal (`plan_checks.py`). `look-check` reads the first word after the item id; a scratch proof covers pass, fail, "fail … pass" and pending. |
| F4 Low (ref drift) | 09:369→363, 09:371→364, 09:374→368, D-12 09:394→393, `gui-actions-audit.test.ts:12`→11, and also 09:343-350→343-346 (found by the census listing). The `ZOOM_STEP` wording is fixed. Row 0 says to run `electron-setup` by hand first. Task `status: in_progress` is kept: it is the TASK-TEMPLATE default, and Session 27 used the same. |
| F5 Low (PR-9 clusters) | The icon list is canonical in `TOOLBAR_BUTTONS`; the `.sh` `prereq` check is the executable copy, and the prose restatements were removed. `local-requests.md` points at `COUNT_FLOORS` and the `.sh` `order` list. The plan points at `REPEAT_GREP`. AC-66.12 and D-18 use `WHEEL_STEP_PX`. `ZOOM_KEY_SCOPE` states it governs only the zoom and Space keys, while `COLOR_FOCUS_IDS` keeps the editor keys. Canon edits and the `hub` predicate use "Session 29 plan D-n". |
| Observations 1, 3, 4, 5 | 1: the middle-button down is `preventDefault()`ed, so there is no Chromium autoscroll. 3: every option group keeps `shrink-0`. 4: no literal `devicePixelRatio` in `CaptureViewport.tsx`. 5: Electron specs use test ids or `exact: true`. Observation 2 (S5 unlikely on Windows/Linux) is noted; the AC-66.12/66.13 oracle and S5 stay. |

`plan_checks.py static` after corrections: PASS (see §Planning receipts). Re-running its negative case on the corrected files exposed a defect in the verifier itself. Its reference check was a substring match, so the receipt prose that names the negative-case tokens counted as a definition, and 8 of 10 mutations were reported. The check now requires a definition site, and the re-run reports all ten.

## Round 2 Correction Notes (post-approval, non-blocking)

Round 2 returned `approved`: 0 Critical, 0 High, 0 Medium, no blocking finding. The PR-6 census gate passed, and all Round 1 corrections were verified against live sources, including a simulation of `ZOOM_SEAM_SHOT` → `ZOOM_EXAMPLE`. The reviewer's five clerical notes were handled before execution as follows:

| Note | Handling |
|---|---|
| R2-1 Low (`look-check` reads `pass` when a leftover `pass\|fail` template token precedes the result) | `look-check` now refuses any L-row that still contains the literal `pass|fail` before matching, so an unfilled template line can never read as a pass. |
| R2-2 Low (old/new values added to the correction log after the census) | No change: these are history lines in §Round 1 Review Corrections and the census file, dispositioned as consistent by the reviewer. |
| R2-3 Low (fixture line refs; square-only `withSurfaceSize`; fake `ResizeObserver` timing) | `ZOOM_SEAM_SHOT` now cites `:54-66,125-138`, adds a width/height variant of the helper (append-only), and requires the fake `ResizeObserver` before render. |
| R2-4 Low (task row 9 names bare D-ids) | Row 9 now names "Session 29 plan D-12/D-15/D-17/D-18", matching the `hub` predicate. |
| R2-5 Low (the AC reference check sees only literal AC ids; rows use ranges) | No change: the ranges' endpoints are literal ids and are checked. The full AC set is proven at H1-5 by `validate_closeout_artifacts.py --ac-coverage-only`. |


Run in the container on 2026-10-01 against the files in this folder. All of these tools are read-only; no product code, test or build ran.

- `python3 docs/execution/plans/2026-10-01-capture-viewport-chrome/plan_checks.py static` → `PASS static: 20 task rows; scripts and plan cross-references agree` (exit 0).
- **Negative case**, run on mutated copies in the session scratchpad. The ten mutations: a renamed `.ps1` stage, a swapped `.ps1` audit file, a changed `gated` entry, a lowered Vitest floor, a changed `ZOOM_LADDER` value, a dangling dependency (`99`), a self-cycle, an unknown check label, a reference to an undefined decision id, and a reference to an undefined AC id. Result: ten `FAIL:` lines, one per mutation (exit 1).
- `python3 tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-01-capture-viewport-chrome/task.md` → `OK: 20 row(s); 10-column table (with builder_model); … dependencies resolve and are acyclic` (exit 0).
- `bash -n docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh` → exit 0.
- Icon names: `npm pack lucide-react@0.400.0` (scratchpad). Its `dist/lucide-react.d.ts` declares every icon in `TOOLBAR_BUTTONS` and `OPTIONS_TOGGLE` (one `declare const` each). `validate-task.sh prereq` re-checks the same list against the installed package at row 0.

## Research References

- Chromium preset zoom factors: `https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/common/page/page_zoom.cc` (lines 13-15, 25-26; read 2026-10-01).
- WAI-ARIA Authoring Practices, Toolbar pattern: `https://www.w3.org/WAI/ARIA/apg/patterns/toolbar/`.
- MDN `WheelEvent.deltaMode` / `deltaY`: `https://developer.mozilla.org/en-US/docs/Web/API/WheelEvent/deltaMode`.
- Adobe Hand tool (Space to pan): `https://helpx.adobe.com/photoshop/using/tool-techniques/hand-tool.html`.
- Electron `before-input-event`: `https://www.electronjs.org/docs/latest/api/web-contents#event-before-input-event`.
- `lucide-react@0.400.0` typings (`npm pack`, `dist/lucide-react.d.ts`, 2026-10-01): see §Planning receipts.
- Triage research for both issues: `.agent/context/known-issues.yaml` CAPTURE-TOOLBAR-ICONS (D-12/D-13), CAPTURE-SETTINGS-BUTTON-LABEL (D-16/D-17), CAPTURE-VIEWPORT-ZOOM (D-10/D-11).
- `.agent/docs/cloud-local-collaboration.md` §1–§5, §9; Session 27 `validate-task.sh` / `.ps1` / `plan_checks.py` as templates (§10).

## Validation stage contract

The plan binds to PROFILE D6 (`.agent/docs/commands.md` §D6), in stages:

1. **Static:** py-types, py-lint, ui-types, ui-lint, mcp-types, plan-static, task-contract.
2. **Targeted:** the per-MEU Red/Green/gate checks.
3. **Fresh full:** the container pre-gate first (non-authoritative), then `WINDOWS_GATE` (authoritative).
4. **Runtime:** `CAPTURE_LOOK` (human visual, authoritative for L1–L6 only).

For each stage, `validate-task.sh` / `.ps1` hold the argv, cwd (repo root), scope and blocking status (all blocking). Expected results are exit 0 (with the stated `rg` exception), and receipts go under `$RECEIPTS_DIR` / `C:/Temp/av-kit`.

**Input identity** is recorded independently at pre-gate and at each Windows attempt:

- HEAD, a hash of `git status --porcelain`, and both lockfile hashes;
- the Node and Electron versions;
- `P:/agentic-framework` HEAD and the `P:/.agent` registry hash (Windows).

**Reuse is disabled:**

- Any commit touching `GATED_PATHS` after the tested SHA reopens the gate (cloud-local §3.4).
- A cached, partial or container-only result never certifies the full gate.
