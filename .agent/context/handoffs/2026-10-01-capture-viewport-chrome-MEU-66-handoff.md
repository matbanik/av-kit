---
date: "2026-10-02"
project: "capture-viewport-chrome"
meu: "MEU-66"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-web (Claude Opus 5.5)"
reviewer: "claude-fable-5-1-subagent (user-authorized, human-review-decision.md)"
predecessor: ".agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-65-handoff.md"
---

# Handoff: 2026-10-01-capture-viewport-chrome-MEU-66-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-66 — `gui-capture-zoom`. The Capture image can be zoomed and panned.
- **Zoom inputs:** the mouse wheel (plain or with Ctrl) zooms about the cursor (`WHEEL_STEP`). The new **− / readout / + / Fit** group in the tools row and `Ctrl+=` / `Ctrl+-` / `Ctrl+0` zoom about the frame centre. The keys work in `ZOOM_KEY_SCOPE` only, and each handled key or wheel event is `preventDefault`ed.
- **Levels:** Chromium's preset ladder, 25 %–500 % (`ZOOM_LADDER`), plus Fit.
- **Pan:** Space+drag and middle-drag move a clamped offset inside the `overflow-hidden` surface (`PAN_GESTURES`). A pan creates no mark.
- **Geometry:** one transform, `VIEW_TRANSFORM` (`viewTransform` in `capture-fit-map.ts`), drives pointer mapping (`SURFACE_POINTER`), handle radii, the text draft position, the image/SVG content box (`CONTENT_BOX`) and the `ZOOM_OBSERVABLES`. At Fit it equals `fitScaleOrigin`, so MEU-59 is unchanged. Stored annotations never change.
- **Reset:** zoom returns to Fit on a shot change (`ZOOM_RESET`, `shotId` prop). It is kept across Original/Annotated, and on a resize the offsets re-clamp.
- **Help:** `ZOOM_HELP_SENTENCE` is added to the help card, and `ZOOM_PAN_HINT` is the readout's tooltip.

**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Viewport zoom (09:627-638, matrix 9.11)
**Predecessor**: MEU-65 (the icon toolbar the zoom group joins; `ToolbarIconButton`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-66.1 | unit | `ZOOM_LADDER` = Chromium presets; `zoomStep` steps from fit and scale, null past the ends or for an invalid fit scale | Research-backed D-14; Spec 09:634 | `ui/tests/unit/capture-zoom.test.ts` `AC-66.1 …` (3) | ✅ |
| AC-66.2 | unit | `viewTransform` = `fitScaleOrigin` at fit; centres a fitting axis, clamps an overflowing one; invalid input → null | Spec 09:636; 09:375 | `ui/tests/unit/capture-fit-map.test.ts` `AC-66.2 …` (3) | ✅ |
| AC-66.3 | unit | `VIEW_MAP` both ways on `ZOOM_EXAMPLE`; 7×7 round trip ≤ 0.5 px; out-of-image → null; fit-only gives (800,450) | Spec 09:638 | `capture-fit-map.test.ts` `AC-66.3 …` (3) | ✅ |
| AC-66.4 | unit | `zoomAbout` keeps the cursor point on `ZOOM_ABOUT_EXAMPLE`; ≤ 1 image px where no clamp applies; clamp leaves no blank margin | Spec 09:633 | `capture-zoom.test.ts` `AC-66.4 …` (3) | ✅ |
| AC-66.5 | unit | `hitTestMarks` at s = 4 with a panned origin keeps CSS radii; letterbox misses (regression lock) | Local Canon AC-60.1 | `ui/tests/unit/capture-hit-test.test.ts` `AC-66.5 …` (2) — `green-at-baseline (lock)` | ✅ |
| AC-66.6 | unit | `wheelSteps` (line/page per event, pixel accumulation, sign/idle reset, invalid → 0) and `zoomKeyAction` | Research-backed D-18 | `capture-zoom.test.ts` `AC-66.6 …` (4) | ✅ |
| AC-66.7 | integration | jsdom (`ZOOM_SEAM_SHOT`): the zoom group follows `ICON_BUTTON_RULE`; +/− step about the centre; the readout and observables change; annotations, history and Save untouched; bounds and no-shot disable | Spec 09:633, 09:636 | `ui/tests/unit/capture-page.behavior.test.ts` `AC-66.7 …` (2) | ✅ |
| AC-66.8 | integration | jsdom: `ZOOM_RESET` on a shot change (also after the dirty confirm); Original/Annotated keeps the scale; a resize re-clamps `ox` (fake `ResizeObserver`) | Spec 09:637 | `capture-page.behavior.test.ts` `AC-66.8 …` (2) | ✅ |
| AC-66.9 | integration | jsdom: the keys from body and from the focused surface, one step per press, `defaultPrevented`; none in text-entry focus, with the confirm strip, without a shot, or without Ctrl | Spec 09:633; D-17 | `capture-page.behavior.test.ts` `AC-66.9 …` (2) | ✅ |
| AC-66.10 | integration | jsdom: middle-drag and Space+drag pan the clamped offset with no mark, history or Save; a plain drag still draws; no pan at Fit; Space on a toolbar button does not arm; a letterbox press creates nothing | Spec 09:635; D-15 | `capture-page.behavior.test.ts` `AC-66.10 …` (2) | ✅ |
| AC-66.11 | integration | jsdom: `ZOOM_EXAMPLE` via ten Ctrl+= and a middle-drag; the arrow lands on (700,375)→(750,400); handle r × s = 5; text draft at (400,300); `CONTENT_BOX` style; a viewport-level `SurfacePointer` reports image (700,375), s 2, origin (−1000,−450); zero-length and 2 CSS px drags change nothing | Spec 09:636 | `capture-page.behavior.test.ts` `AC-66.11 …` (3) | ✅ |
| AC-66.12 | integration | Electron (`ZOOM_SHOT`): one wheel step (and Ctrl+wheel) steps one level about the cursor (TA-1 per-axis oracle); `getZoomFactor()` = 1; no scroll | Spec 09:633 | `ui/tests/e2e/capture-inbox.test.ts` `AC-66.12 …` | ✅ |
| AC-66.13 | integration | Electron: buttons and Ctrl+= / Ctrl+- / Ctrl+0 from the surface and from body (TA-2 sequence); `getZoomFactor()` = 1 after every key; inert in `capture-color` | Spec 09:633; D-17 | `capture-inbox.test.ts` `AC-66.13 …` | ✅ |
| AC-66.14 | integration | Electron: an arrow at 100 % POSTs `[1200,800]→[1260,830]` and renders the same; a Fit arrow POSTs the fit mapping; the first arrow is unchanged | Spec 09:638 | `capture-inbox.test.ts` `AC-66.14 …` | ✅ |
| AC-66.15 | integration | Electron: a shot change resets to Fit; Space+drag at 100 % pans with no annotation, no Save, no POST | Spec 09:635, 09:637 | `capture-inbox.test.ts` `AC-66.15 …` | ✅ |
| AC-66.16 | unit | `ZOOM_HELP_SENTENCE` in the four-tools body; the earlier sentences stay | 09:155-157; D-21 | `ui/tests/unit/capture-help-content.test.ts` `AC-66.16 …` | ✅ |
| AC-66.17 | unit | MEU-66 test ids registered after the MEU-51 marker and used in the source | Local Canon AC-51.6 | `capture-page.behavior.test.ts` `AC-66.17 …` (moved from `capture-zoom.test.ts`, see D-26) | ✅ |
| AC-66.18 | integration | jsdom + Electron (A-4, `CAPTURE_LOOK` L5): a mouse click on a toolbar button focuses the surface, so Space+drag then pans with no mark; keyboard activation keeps focus on the button and does not arm pan | Human-approved A-4; Spec 09:635 | `capture-page.behavior.test.ts` `AC-66.18 …` (2); `capture-inbox.test.ts` `AC-66.18 after a mouse click on the Arrow tool…` | ✅ |
| AC-66.19 | integration | Electron (A-5): at `DEFAULT_WINDOW` the Capture page fills `main` and the surface grows past its 200 px floor | Human-approved A-5 | `capture-inbox.test.ts` `AC-66.19 the Capture page fills main…` | ✅ |

### Other plan AC references (not owned by MEU-66)

| AC | Owner | Status in MEU-66 |
|----|-------|------------------|
| AC-65.x | MEU-65 handoff | ✅ predecessor; `capture-toolbar.test.ts` and the AC-65 specs pass with the zoom rows added |
| AC-59.x, AC-60.x, AC-57.x, AC-39.x | existing Capture suites | pass unchanged at Fit |
| AC-51.x, AC-41.x | existing suites | untouched; AC-51.6 and AC-41.3 are declared env-bound Vitest members |
| AC-50.x | existing layout-canon suite | untouched by MEU-66 (row 9 owns the doc edits) |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| Vitest AC-66.2, AC-66.3 (6) | `expected 'undefined' to be 'function'` | pass | `ui/tests/unit/capture-fit-map.test.ts` (`MEU-66 VIEW_TRANSFORM and VIEW_MAP`) |
| Vitest AC-66.16 | `expected 'Arrow, Box, Highlight, and Text draw …' to contain 'Zoom with the mouse wheel, …'` | pass | `capture-help-content.test.ts` |
| Vitest AC-66.7 – AC-66.11 (11) | `Unable to find an element by: [data-testid="capture-zoom-in"]` / `"capture-zoom-level"` | pass | `capture-page.behavior.test.ts` (`MEU-66 Capture viewport zoom`) |
| Vitest AC-66.1, 66.4, 66.6 | suite load `Cannot find module '…/capture-zoom'` (declared new module) | pass | `ui/tests/unit/capture-zoom.test.ts` |
| Electron AC-66.12 | `Expected: "fit" Received: null` | pass | `capture-inbox.test.ts` (`AC-66.12`) |
| Electron AC-66.13 – 66.15 | timeout waiting for `capture-zoom-in` / `capture-zoom-level` | pass | `capture-inbox.test.ts` |

AC-66.5 passed at Red, as the plan states (`green-at-baseline (lock)`). Every Red failure is in [walkthrough.md](../../../docs/execution/plans/2026-10-01-capture-viewport-chrome/walkthrough.md) §MEU-66 Red.

**Test amendments during Green (Human-approved, A-3 in human-gate-decision.md).**
- **TA-1:** AC-66.12's cursor oracle is per axis. An overflowing axis keeps the cursor pixel within 1 px; a fitting axis is centred. With Fit ≈ 0.24, the first step (25 %) leaves the 600 px image narrower than the ~810 px frame, so `VIEW_TRANSFORM` centres x. The Red-time oracle measured a 669 px x move.
- **TA-2:** AC-66.13's key loop presses Ctrl+= twice before Ctrl+-. The first step up from Fit is already the ladder's bottom (25 %), where Ctrl+- is a correct no-op.
- **Two setup details, recorded in A-3:** a sub-pixel tolerance on the centred offset, because the observables carry 4 decimals; and two animation frames before `readZoom`.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s29-66-red","command":"bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh red66","cwd":"/home/user/av-kit","scope":"UNIT66 Vitest, fresh build, Electron capture-inbox -g AC-66","phase":"targeted","exit_code":0,"result":"pass","tested_state":"9f5ecb3 (MEU-65) + MEU-66 tests and ids only; no MEU-66 production edit","output":"PASS AC-66 RED: 7 failing AC-66 assertions, 69 passing | PASS AC-66 E2E RED: 4 failing AC-66 specs","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s29-66-green-unit","command":"bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh green66-unit","cwd":"/home/user/av-kit","scope":"capture-zoom, capture-fit-map, capture-hit-test Vitest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"row 6 tree (capture-zoom.ts, capture-fit-map.ts additions)","output":"PASS s29-66-green-unit: 24 passed of 24, env-bound tolerated: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s29-66-green","command":"bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh green66","cwd":"/home/user/av-kit","scope":"UNIT65 + UNIT66 + REGCAP Vitest, ui build, Electron capture-inbox -g AC-66","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-66 final working tree after A-3","output":"PASS s29-66-green: 188 passed of 189, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 '] | PASS s29-66-green-build | PASS s29-66-green-e2e: 4 passed, env-bound tolerated: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s29-66-gate","command":"bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh gate66","cwd":"/home/user/av-kit","scope":"ui typecheck, lint, UNIT65+UNIT66+REGCAP Vitest, ui build, harness build, Electron capture-inbox (whole file), Electron layout-primitives + tts-generate, repeat-each=20 over REPEAT_GREP","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-66 final working tree (9f5ecb3 + MEU-66 diff, after A-3)","output":"PASS s29-66-typecheck | PASS s29-66-lint | PASS s29-66-vitest: 188 passed of 189, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 '] | PASS s29-66-build | PASS s29-66-harness-build | PASS s29-66-e2e: 19 passed, env-bound tolerated: [] | PASS s29-66-e2e-disclosure: 15 passed, env-bound tolerated: [] | PASS repeat-each=20 66-capture (stats expected 240, unexpected 0, flaky 0)","fresh":true}
```

The authoritative full gate is `WINDOWS_GATE` (H1-6).

**Stop condition S5 did not fire in the container.** After every Ctrl+= / Ctrl+- / Ctrl+0 (from the surface and from body) and after each wheel step, `webContents.getZoomFactor()` is 1 (AC-66.12, AC-66.13), so the renderer's `preventDefault` keeps Electron's default-menu zoom accelerators from acting. The authoritative check on the Windows target is `WINDOWS_GATE` (`ui-electron`) plus `CAPTURE_LOOK` L4.

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint: 0
Vitest UNIT65 + UNIT66 + REGCAP: 188/189 (AC-51.6 env-bound)
ui build + harness build: pass
Electron capture-inbox: 19 passed; Disclosure neighbours: 15 passed
repeat-each=20 (AC-65|AC-66|AC-59.12|AC-60.12|AC-57.10): 240 expected, 0 unexpected, 0 flaky
source audit (PREFIX_AUDIT over AUDIT_SRC): 0 hits; no literal devicePixelRatio in CaptureViewport.tsx
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/capture/capture-zoom.ts` | new | 1–147 | `ZOOM_LADDER`, `zoomStep`, `zoomAbout`, `wheelSteps` (+ `WHEEL_STEP_PX`, `WHEEL_IDLE`), `zoomKeyAction`, `ZOOM_PAN_HINT` |
| `ui/src/renderer/src/features/capture/capture-fit-map.ts` | modified (additive) | +89 | `ViewState`, `ViewTransform`, `viewTransform`, `mapPointerWithView(Unclamped)`, `mapImageToPointerWithView`; existing exports unchanged |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | +357/−102 | zoom state and reset, measured frame, `liveView`-based pointer mapping, `stepZoom`/`panBy`, `handleViewKey` (window + surface paths, `WeakSet` once-guard), native non-passive wheel listener, zoom group and readout, `ZOOM_OBSERVABLES`, `CONTENT_BOX`, `overflow-hidden`, grab cursor |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modified | +6 | zoom rows (`ZoomOut`, `ZoomIn`, `Maximize`) |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | +1 | `shotId={selectedId}` |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modified | +1/−1 | `ZOOM_HELP_SENTENCE` appended |
| `ui/tests/e2e/test-ids.ts` | modified | +7 | MEU-66 block |
| `ui/tests/unit/capture-zoom.test.ts` | new | — | AC-66.1, 66.4, 66.6 |
| `ui/tests/unit/capture-fit-map.test.ts` | modified (append) | +104 | AC-66.2, 66.3 |
| `ui/tests/unit/capture-hit-test.test.ts` | modified (append) | +35 | AC-66.5 |
| `ui/tests/unit/capture-help-content.test.ts` | modified (append) | +12 | AC-66.16 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified (append; node imports) | +519 | AC-66.7–66.11, AC-66.17, `withSurfaceRect` |
| `ui/tests/e2e/capture-inbox.test.ts` | modified (append) | +309 | AC-66.12–66.15 (TA-1, TA-2) |
| `ui/tests/e2e/download-queue.test.ts` | modified (TA-3, A-6) | +7/−2 | W1-8 only: `test.slow()` and two one-shot seam reads become `expect.poll` (same counts) |

```diff
-function surfaceFromDom(event, phase, pointerId, imageWidth, imageHeight): SurfacePointer | null {
-  const fit = fitScaleOrigin({ containerW: box.width, containerH: box.height, imageW: imageWidth, imageH: imageHeight })
+function surfaceFromDom(event, phase, pointerId, imageWidth, imageHeight, zoom: ZoomState): SurfacePointer | null {
+  const { box, view } = liveView(target, imageWidth, imageHeight, zoom)
   ...
-    scale: fit.s,
+    scale: view?.s ?? 0,
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Corrections Applied (2026-10-02, after WINDOWS_GATE attempt 1 and CAPTURE_LOOK)

**Findings resolved**: 2/2 MEU-66 items (L5 fail, A-4; Mat's observation 2, A-5).

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | L5: a mouse click on a tool left focus on the button, so `spaceArmable()` refused Space and Space+drag drew a mark (Red: jsdom `activeElement` was the button; Electron `toBeFocused` failed on the surface) | `CaptureViewport.tsx`: the `capture-chrome-tools` row's click handler focuses the surface (`preventScroll`) when `event.detail > 0` and the target is a button | AC-66.18 jsdom ×2 and Electron pass; the keyboard negative (Enter on `capture-tool-box` keeps focus; Space draws a rect, no pan) passes |
| 2 | Observation 2: the frame stayed at about 200 px with empty space below (Red: `pageBottom 574` vs `mainBottom 773`, `surfaceHeight 200`) | `CapturePage.tsx`: the page column is `min-h-full` and the content row is `flex-1`, the same pattern as the Downloader, Convert and Transcript pages' `h-full` columns | AC-66.19 passes; AC-65.4 (no overflow) and the AC-57 layout specs pass unchanged |

Filed instead of fixed (A-5): `CAPTURE-BAKE-ARROW-THIN` (bake in frozen `packages/`) and `CAPTURE-AUTO-SELECT-AFTER-DRAW` (a Human-approved rule; needs a decision).

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-26
    stage: execution
    question: "Where does the AC-66.17 test-id check live, given row 6's check runs capture-zoom.test.ts before the viewport uses the ids?"
    resolution: autonomous
    class: two-way
    chosen: "Move the AC-66.17 test, unchanged, from capture-zoom.test.ts to capture-page.behavior.test.ts (run by green66 and gate66)"
    source_tag: Local Canon
    precedents: ["implementation-plan.md MEU-66 Files Modified — capture-zoom.test.ts owns AC-66.1, 66.4, 66.6 only", "task.md row 6 — green66-unit runs capture-zoom/fit-map/hit-test before row 7 wires the viewport"]
    research: { engine: none, sources: [] }
    reasoning: "AC-66.17 reads CaptureViewport.tsx, which only gains the ids in row 7, so it cannot pass at row 6. The plan's file table does not assign it to capture-zoom.test.ts. Moving it before Green, with its assertions unchanged, keeps each row's check honest."
  - id: D-27
    stage: execution
    question: "How do the window and surface key paths avoid a double zoom step for one key press?"
    resolution: autonomous
    class: two-way
    chosen: "A module-level WeakSet<Event> of native events handleViewKey already acted on (the plan's 'handled flag on the native event')"
    source_tag: Local Canon
    precedents: ["implementation-plan.md ZOOM_KEY_SCOPE — a handled flag prevents a double step", "ui/src/renderer/src/features/capture/CaptureViewport.tsx surface onKeyDown stopPropagation"]
    research: { engine: none, sources: [] }
    reasoning: "A WeakSet marks the event without mutating a DOM object or widening the KeyboardEvent type, and it frees entries with the event."
  - id: D-28
    stage: execution
    question: "Which box do the observables and content box use, and which does pointer mapping use?"
    resolution: autonomous
    class: two-way
    chosen: "Pointer mapping, stepZoom and panBy read the surface's live getBoundingClientRect; the observables, handle radius and content box read the measured frame (layout effect + ResizeObserver)"
    source_tag: Local Canon
    precedents: ["CaptureViewport.tsx (before MEU-66) — surfaceFromDom used the live rect; the handle radius used the measured fitScale", "ui/tests/unit/capture-page.behavior.test.ts bindSurface — jsdom tests stub the live rect per element"]
    research: { engine: none, sources: [] }
    reasoning: "This keeps the existing split, so every MEU-59/60 jsdom test that stubs only the live rect still maps exactly. The measured frame matches the live rect once the ResizeObserver has run."
  - id: D-29
    stage: execution
    question: "Does WINDOWS_GATE attempt 3 need a fresh CAPTURE_LOOK after TA-3?"
    resolution: autonomous
    class: two-way
    chosen: "No. The attempt-2 look (L1-L6 all pass, run on code identical to c2452aa) is reused for attempt 3, because TA-3 changes only ui/tests/e2e/download-queue.test.ts and ui/src is byte-identical"
    source_tag: Local Canon
    precedents: ["local-requests.md §GATE — CAPTURE_LOOK checks rendered product behaviour", "git diff c2452aa..66c7bfd -- ui/src is empty"]
    research: { engine: none, sources: [] }
    reasoning: "The look exercises product code, not the Electron test files. Repeating it on byte-identical renderer code would add a human step without new evidence. walkthrough.md records which commit each look ran on."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-02 | claude-code-web | Initial handoff after gate66 |
