---
project: "2026-10-16-capture-editor-options"
date: "2026-10-16"
source: "docs/build-plan/09-screenshot-capture.md#size-scrubbing"
meus: ["MEU-85", "MEU-86", "MEU-87"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture editor options — size scrub, colour swatches, tool lock (Session 37)

> **Project:** `2026-10-16-capture-editor-options`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md`:
> - §Size scrubbing (`:746-754`, MEU-85)
> - §Named colour swatches (`:756-765`, MEU-86)
> - §Tool lock (`:767-777`, MEU-87)
> - §Annotation edit until Save (MEU-60) and §Viewport toolbar icons and Options (MEU-65) as Local Canon
>
> **Grouping:** `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, Session 37 (`:133-137`), decisions D-1 to D-7 (`:215-221`).
> **Known issues:** `CAPTURE-SIZE-MOUSE-CONTROL` (`known-issues.yaml:1781`), `CAPTURE-NAMED-COLOR-SWATCHES` (`:1816`), `CAPTURE-AUTO-SELECT-AFTER-DRAW` (`:1298`).
> **Status:** `draft`. Under `plan_to_exec_gate: human`, execution starts only on the user's explicit chat message.
>
> Line anchors are from `main` `90bb409` (Sessions 34 and 36 merged), which is the worktree HEAD.

## Goal

Mat asked for three editor-option changes (2026-10-03). The 2026-10-09 triage scoped them (D-56, D-57, D-63):

1. **MEU-85: size scrub.** The Stroke and font-size fields keep their number inputs and gain three mouse and keyboard gestures:
   - dragging the field's label scrubs the value (Shift ×10, Alt fine);
   - the wheel over the field steps the value;
   - Up/Down step the value.

   The selected mark previews live while the value changes. One gesture is one undo step.
2. **MEU-86: named colour swatches.** Each option in the Named select has its colour as its background and a text colour picked for contrast. The spec allows a fallback popover in case the target ignores option backgrounds. R-1 shows that Electron on Windows paints them, so the native select stays.
3. **MEU-87: tool lock.** A lock button keeps the current tool after each mark, so several marks need no tool click each. With the lock off, the existing auto-Select after drawing (AC-60.4) stays unchanged as the default.

All three changes are in the renderer only. No domain, API, OpenAPI or MCP file changes, because the wire values (`stroke_width`, `font_size`, `color`) are unchanged.

Order (grouping `:135`): MEU-85 first, because it changes the options row and the history model, which are the riskiest parts. MEU-86 restyles one control in that row. MEU-87 adds one button and changes two create paths. The worktree baseline is the branch HEAD when execution starts; row 0 records it in `baseline.sha`. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from the s37 worktree (ls: No such file or directory, 2026-10-16); no headroom MCP or binary. Scope is the Capture renderer (ui features/capture: CapturePage.tsx, CaptureViewport.tsx, capture-toolbar.ts, capture-color.ts, capture-help-content.ts) and its tests, read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). It stops (S1) if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md` §Claude Code; `.agent/context/harness.local.md` §Claude Code).
  - `native_shell: pwsh`. Every validation goes through `rtk proxy` with the receipt pattern `*> C:/Temp/av-kit/<receipt>.txt; $code=$LASTEXITCODE; Get-Content …; exit $code`.
  - `plan_to_exec_gate: human`. A reviewer `approved` does not start execution; the user's explicit chat message does.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every row that is not `shared` keeps `compact_continue` as its fallback.
- **Cloud/local split: not used.** Mat's Windows host is both the driver and the target, so the gates are authoritative where they run.
  - There is no `validate-task.sh`/`.ps1` and no `local-requests.md`.
  - Commands are the PROFILE D6 argv (`.agent/docs/commands.md:190-210`) plus targeted file lists.
- **Working directory:** the worktree root `P:/av-kit-wt/s37-capture-editor-options` (`WT`, branch `claude/s37-capture-editor-options`).
  - D6 lists `P:/av-kit` as its default cwd; this plan runs the same argv from `WT` (D-8).
  - Row 0 creates the Python 3.12.12 virtualenv and installs the three dependency trees in `WT`.
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`; `.agent/skills/cli-dispatch/SKILL.md`).
  - Claude authored the plan, so the reviewer is from a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable, Mat is the fallback (PROFILE B3/B4). Self-review is never allowed.
- **Never:** commit, push, upload, publish, or write to YouTube; author an `approved` verdict; send secrets to a provider.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-85` | `.agent/context/handoffs/2026-10-16-capture-editor-options-MEU-85-handoff.md` |
| `MEU-86` | `.agent/context/handoffs/2026-10-16-capture-editor-options-MEU-86-handoff.md` |
| `MEU-87` | `.agent/context/handoffs/2026-10-16-capture-editor-options-MEU-87-handoff.md` |

Plan-local tooling (project artifacts, not product):

- [session-gate.ps1](session-gate.ps1): rows 8 and H1-2.
- [identity.py](identity.py): input identity, H1-6b.
- [red-check.py](red-check.py): Red proof, rows 2, 4 and 6.
- [select-popup-probe.js](select-popup-probe.js) and [select-popup-probe.png](select-popup-probe.png): planning receipt R-1.
- [contrast-probe.py](contrast-probe.py): planning receipt R-2.

Rolling reviews:

- `.agent/context/handoffs/2026-10-16-capture-editor-options-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-16-capture-editor-options-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites (`BASE_MARKERS`), baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Execution message, §Baseline, §Census; `baseline.sha`; `baseline-py-failed.txt` |
| WP-1 | MEU-85 TDD: `SCRUB_MATH`, `SCRUB_FIELD`, `SCRUB_GESTURES`, `SIZE_BURST`, help, E2E (rows 2–3) | WP-0 | `shared` | tests + source; Red/Green receipts; `walkthrough.md` §MEU-85 |
| WP-2 | MEU-86 TDD: `CONTRAST_TEXT`, `SWATCH_OPTIONS`, E2E (rows 4–5) | WP-1 | `compact_continue` | tests + source; `walkthrough.md` §MEU-86; compact, then re-read `task.md` and the walkthrough |
| WP-3 | MEU-87 TDD: `TOOL_LOCK`, `LOCK_KEEPS_TOOL`, help, E2E (rows 6–7) | WP-2 | `compact_continue` | tests + source; `walkthrough.md` §MEU-87 |
| WP-4 | Session gate and hub reconciliation (rows 8–9) | WP-3 | `shared` | gate receipts in `walkthrough.md` §Gate; 09, gui-actions-index, matrix, `docs/BUILD_PLAN.md` |
| WP-5 | H1 closeout, execution review, H2 | WP-4 | `compact_continue` | three handoffs, rolling review, reflection, metrics row |

---

## User Review Required

> [!IMPORTANT]
> These items are for the review loop and for the user's execution message. They are not a pause point.
>
> 1. **Base branch.** `WT` was cut from `main` `90bb409`, which already holds Session 34 (`ToolbarIconButton`, `optionGroups`, the contextual options row) and Session 36. Row 0 checks `BASE_MARKERS` and stops (S1) if they are missing.
> 2. **Session 39 overlap (D-9).** Session 39 (`capture-new-marks`) is planned on its own branch. It edits the same four renderer files and adds a `capture-block-size` field, and its Out of Scope table defers that field's scrub to MEU-85. This plan builds `CaptureScrubField` as a shared component, so the Block size field can adopt it.
>    - If Session 39 lands on `main` before this plan executes, row 0 finds `capture-block-size` and stops (S1). The plan then needs an amendment to cover that field, and the user chooses.
>    - If this plan lands first, Session 39 rebases on it.
> 3. **D-19 Lock persists across tool changes (product preference, two-way).** Mat approved the chosen option on 2026-10-16.
>    - **Chosen:** choosing another tool keeps the lock on, so the new tool is the one kept. Only the lock button releases it. This is how Excalidraw and tldraw behave.
>    - **Alternative:** choosing another tool also releases the lock. That reading of 09:776 ("until the lock is released or another tool is chosen") is also possible.
>    - The chosen reading treats the clause as describing when the *kept tool* changes. Mat may pick the alternative; it changes AC-87.5 only.
> 4. **D-10 Scrub limits are UI caps.** The API, domain and Zod schemas set no upper bound on `stroke_width` or `font_size` (positive ints only). So the scrub stops at 100 (stroke) and 400 (font size) as a UI convenience only. A typed value above the cap is still accepted and sent, exactly as today, and scrubbing never pulls a higher value down.
> 5. **D-15 The font-size field gains a visible label "Size".** Its scrub handle needs visible text to drag. The Stroke field already has its visible label "Stroke".
> 6. **D-16 No swatch popover.** R-1 shows that Electron 42 on Windows paints option backgrounds in the native popup, so the spec's fallback popover is not built. If the AC-86.3 Electron check of the rendered style fails, stop (S4).
> 7. **`TEST_AMENDMENTS` TA-1 to TA-4** are listed in advance. Any other contradiction the census finds stops execution (S2).
> 8. **Optional visual check.** At the commit gate, Mat may scrub a stroke, open the Named menu, and draw with the lock on in the dev app. This is non-blocking; the tests are the gate.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once, here. ACs, task rows and tests refer to these names and never restate the values.

| Name | Definition | Source |
|---|---|---|
| `BASE_MARKERS` | Before any edit, `WT` holds the Session 34 code: `ToolbarIconButton` in `ui/src/renderer/src/features/capture/CaptureViewport.tsx` and `optionGroups` in `capture-toolbar.ts`. In `meu-status.yaml`, MEU-60, MEU-65, MEU-80 and MEU-81 are `approved`, and MEU-85, MEU-86 and MEU-87 are `pending`. No file under `ui/src` contains `capture-block-size` (Session 39 has not landed; User Review Required item 2). | User Review Required items 1–2; D-9 |
| `SCRUB_MATH` | `capture-scrub.ts` (new) defines: `SCRUB_MIN = 1`, `STROKE_SCRUB_MAX = 100`, `FONT_SCRUB_MAX = 400`, `SCRUB_PX_PER_STEP = 2`, `SCRUB_FINE_PX_PER_STEP = 8` and `SCRUB_COARSE_FACTOR = 10`. It also defines three functions. `scrubSteps(carry, dx, fine)` adds `dx` to `carry`, divides by the step width (`SCRUB_FINE_PX_PER_STEP` when `fine`, else `SCRUB_PX_PER_STEP`), truncates toward zero, and returns `{steps, carry}` with the remainder in pixels. `clampScrub(value, delta, min, max)` returns `value + delta` clamped to `[min, max]`, except that it never moves a value against the gesture: a value above `max` stays as it is for a positive delta and steps down normally for a negative one, and the same holds below `min`. `parsePositiveInt(raw)` moves here from `CapturePage.tsx` unchanged and is exported. | Spec 09:752; D-10 |
| `SCRUB_BASE` | Where a gesture starts: `parsePositiveInt` of the field's text. If the text does not parse, the start is the fallback the page passes: the selected mark's own value if one applies, else the field default (stroke 3, font size 16). | D-10; `changeStroke` / `changeFontSize` |
| `SCRUB_FIELD` | `CaptureScrubField.tsx` (new) renders a wrapper `<span className="flex shrink-0 items-center gap-1 text-xs text-fg-muted">` holding two children. The first is a handle `<span data-testid="{id}-scrub" aria-hidden="true" className="cursor-ew-resize select-none …">{label}</span>`. The second is the existing `<input>`, which keeps its `data-testid`, `aria-label`, `title`, `value` and classes. Props: `id`, `label`, `ariaLabel`, `value`, `fallback`, `max`, `onChange(text)`, `onPreview(n)`, `onCommit()`, `onCancel()`. Pointer capture is guarded as `capturePointer` does (`setPointerCapture` may be absent or throw in jsdom). The handle is not focusable, and the input stays the only tab stop. | Spec 09:752 ("keep the number field; dragging its label"); D-15 |
| `SCRUB_GESTURES` | **Drag.** A primary-button `pointerdown` on the handle calls `preventDefault`, focuses the input and captures the pointer. Each `pointermove` feeds `scrubSteps` with `fine = altKey`; the steps are multiplied by `SCRUB_COARSE_FACTOR` when `shiftKey` is held, then applied through `clampScrub` and sent to `onPreview`. `pointerup` calls `onCommit` once, if any step was applied. A press with no step selects the input text. `pointercancel`, `lostpointercapture` and Escape call `onCancel`. **Wheel.** A native `wheel` listener on the input, registered with `{passive: false}`, ignores `ctrlKey`. Otherwise it calls `preventDefault` and feeds `wheelSteps` (`capture-zoom.ts`), passing `deltaY`, or `deltaX` when `deltaY` is 0, because Chromium on Windows turns Shift+wheel into a horizontal delta. Shift multiplies by `SCRUB_COARSE_FACTOR`. The burst commits `WHEEL_RESET_MS` after the last event, or on `pointerleave` or `blur`. **Keys.** ArrowUp and ArrowDown on the input step ±1 (Shift ±10) with `preventDefault`; `keyup` of that arrow or `blur` commits, and Escape cancels. ArrowLeft and ArrowRight keep their caret behaviour. | Spec 09:752; D-11 |
| `SCRUB_ALT_GUARD` | While a drag is open, a window `keydown` and `keyup` listener calls `preventDefault` on the Alt key, so Electron's default menu bar does not take focus mid-drag. The listener is removed when the drag ends. | D-12 (Electron PR #29318) |
| `SIZE_BURST` | `CapturePage` holds `sizeBurstRef: {field: 'stroke' \| 'font', startText, origin, index} \| null`. The burst opens at the first `onPreview(n)` of a gesture and records `startText`, the field text before it. Every preview sets the field text to `String(n)`. If a mark applies (`changeStroke` / `changeFontSize` rules: a selected arrow or box for stroke, a selected text for font size), the first applicable preview stores `origin = annotationsRef.current` and `index = selectedIndex` and calls `setTxOpen(true)`; every applicable preview then replaces mark `index` in `annotations` live, without history. A preview while a pointer gesture is open (`gestureRef`) does nothing. **One owner (R1-F1).** The size burst and the nudge burst never overlap: a size preview first runs `finishNudge()`, and `nudgeSelected` first runs `finishSize()`. `finishSize()` also runs first in every other handler that writes the marks, the selected mark or the history, or opens a text draft (call-site census of `CapturePage.tsx` at baseline `90bb409`): `applyHistory` (`:408`; so every create, `changeStroke`, `changeFontSize`, `changeTextBg`, `applyColor` and `removeSelectedMark` write), `commitSelection` (`:445`), the viewport `onSelectIndex` callback (`:1355`), `handleSurfacePointer` (`:469`; the surface `pointerdown`, which also opens a text draft), `onTextCommit` (`:1329`) and `acceptConfirm` (`:869`; delete, flatten, revert and the dirty shot switch). Rule for any handler added later: if it writes `annotations`, `selectedIndex`, `past` or `future`, it runs `finishSize()` first. **Undo and Redo** are the inline `onUndo` / `onRedo` callbacks (`:1300`, `:1313`), not `applyHistory`, and they pop the render's `past` / `future`, which a `finishSize()` in the same handler would not yet have updated. So they are not finish-first paths: they are disabled while `txOpen` is true (`canUndo={past.length > 0 && !txOpen}`, and likewise `canRedo`) and also return at once when `txOpen` is true. The gate also covers an open nudge burst, which has the same stale-stack defect today; no existing test clicks Undo or Redo while a nudge key is held (nudge sites `capture-page.behavior.test.ts:759-770`, `:836-837`, `:1098-1099`, `:1356-1357`). **Shot change.** The `selectedId` reset effect (`:314`), reached by `chooseItem` (`:431`) and by `acceptConfirm`, already clears `past`, `future`, `txOpen` and `gestureRef`; it also sets `sizeBurstRef.current = null`, so a later timer or commit finds no burst and adds nothing to the new shot's history. Save and `chooseTool` stay refused while `txOpen` is true. **Finish and cancel.** `finishSize()` (on `onCommit`) clears the burst and `txOpen`; if the list differs from `origin`, it pushes `origin` onto `past` and clears `future`, which is one undo step. `cancelSize()` (on `onCancel`, and from the Escape branch of `handleEditorKey`) restores `origin` when one was stored and always restores `startText`, then clears the burst and `txOpen`. Both are idempotent: a component callback after the page has closed the burst does nothing, and a later preview opens a new burst from the field's current text. A typed `onChange` while a burst is open first runs `finishSize()`, so the typed value is the base of the next gesture. With no applicable mark, only the field text changes and the next mark uses it. **Component.** `CaptureScrubField` ends its own gesture when it sends `onCommit` or `onCancel`, ignores any later `pointerup` or timer for that gesture, and clears its timer and listeners on unmount without calling back. | Spec 09:753 ("previews live… one gesture is one undo step"); D-13; nudge burst precedent |
| `TYPED_EDITS` | Typing in either field keeps today's model: `changeStroke` / `changeFontSize` run one `applyHistory` per applied change, and invalid text is held in the field and applied to nothing. | Local Canon (MEU-60 §Annotation edit until Save); D-14 |
| `SIZE_LABELS` | The stroke handle reads "Stroke" (`capture-stroke-scrub`) and the font-size handle reads "Size" (`capture-font-size-scrub`). The input `aria-label` values stay "Stroke width" and "Font size". | D-15 |
| `CONTRAST_TEXT` | `contrastText(hex)` in `capture-color.ts` (new export) takes the WCAG 2.1 relative luminance `L` of `normalizeHex(hex)`. It returns `'#000000'` when `(L + 0.05) / 0.05 >= 1.05 / (L + 0.05)` (contrast with black is at least contrast with white), else `'#FFFFFF'`. It throws `RangeError` when `normalizeHex` returns `null`. | Spec 09:764 ("contrast-picked text colour"); D-17; R-2 |
| `SWATCH_OPTIONS` | In the Named select (`capture-named-color`), each named `<option>` has the inline style `{backgroundColor: NAMED_COLOR_HEX[name], color: contrastText(NAMED_COLOR_HEX[name])}` in place of `NATIVE_OPTION_MENU_STYLE`. The placeholder option "Named" keeps `NATIVE_OPTION_MENU_STYLE`, and the closed select keeps its G30 style (`namedMenuStyle`). The option text and values are unchanged. | Spec 09:764; G30 |
| `POPOVER_FALLBACK` | Not built. R-1 shows the native popup paints option backgrounds on the target (Electron 42.9.3, Windows). | Spec 09:764 conditional; D-16; R-1 |
| `TOOL_LOCK` | `TOOLBAR_BUTTONS` gains `'capture-tool-lock': {icon: Lock, name: 'Keep tool after drawing'}` (lucide `Lock`). It is not added to `TOOL_BUTTON_IDS`, because it is not a tool. `CaptureViewport` renders it as a `ToolbarIconButton` placed straight after the "Annotation tool" group, with `pressed={toolLocked}` (so `aria-pressed`) and the variant that `toolVariant` gives the active tool when it is on. It is enabled with or without a shot. `toolLocked` is page view state: default `false`, not persisted, not part of the overlay, so toggling it never changes `dirty`, the tool or the selection. | Spec 09:776; D-18 |
| `LOCK_KEEPS_TOOL` | With `toolLocked`, a drawn mark's create path runs `applyHistory(list)` without `commitSelection`, so the tool stays and nothing is selected. A text commit runs `applyHistory(list)` and `setTextDraft(null)` without `commitSelection`. With the lock off, both paths are unchanged (AC-60.4). | Spec 09:775-776; D-18 |
| `LOCK_PERSISTS` | Choosing another tool while the lock is on keeps `toolLocked`; only the lock button turns it off. Turning it off restores auto-Select from the next mark. | D-19 (User Review Required item 3) |
| `HELP_SENTENCES` | The help section with id `four-tools` keeps its id and title. Its body gains two sentences. One: drag the Stroke or Size label, or use the wheel or Up/Down over the field, to change the size, and each gesture is one undo step. The other: the lock button keeps the current tool after each mark. | D-20 |
| `NEW_TESTIDS` | `capture-stroke-scrub`, `capture-font-size-scrub`, `capture-tool-lock`. No existing id changes. | Local Canon |
| `ELECTRON_RED` | A new Electron test's first assertion is the count of its subject: `expect(await page.getByTestId(X).count()).toBe(1)`. So a missing control fails as an `Error: expect(` line and not as a locator timeout, which `red-check.py` refuses as a setup failure. The same rule holds in Vitest behaviour tests: `expect(screen.queryByTestId(X)).not.toBeNull()` comes before any `getByTestId(X)`. | `red-check.py` docstring |
| `RENDERER_PIN` | Electron must load the renderer this worktree built (R1-F2): `ui/src/main/index.ts:504` loads `ELECTRON_RENDERER_URL` instead whenever it is set, and `capture-inbox.test.ts` passes `process.env` through. So every command that builds or runs Electron clears it with `$env:ELECTRON_RENDERER_URL=$null` beside `$env:ELECTRON_RUN_AS_NODE=$null`, `session-gate.ps1` clears both, and `identity.py` records it and refuses (exit 2) while it is set. Each new Session 37 Electron test (AC-85.10, AC-86.3, AC-87.6) first asserts that `fileURLToPath(page.url().split('#')[0])` equals `resolve(here, '../../out/renderer/index.html')`, which passes on the baseline renderer too, so the Red still fails at its count or style assertion. | `ui/src/main/index.ts:504-508` |
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the Files Modified rows below. No file under `packages/`, `mcp-server/` or `openapi.committed.json` changes. | Grouping `:135`; D-14 |
| `TEST_AMENDMENTS` | **TA-1:** `ui/tests/unit/capture-page.behavior.test.ts` "named color menu options use dark text on a light surface" (`:1129`) asserts the orange option is `#1e293b` on `#ffffff`, which `SWATCH_OPTIONS` replaces. That test is rewritten as AC-86.2 under the AC-86.2 title, and its placeholder assertion stays. **TA-2:** `ui/tests/unit/icon-hints.test.ts` AC-80.8 title "the 12 Capture toolbar buttons" becomes "the 13 Capture toolbar buttons". Its body iterates `TOOLBAR_BUTTONS` and needs no change: the lock is enabled with no shot, so its hint is its name. **TA-3:** `ui/tests/e2e/test-ids.ts` gains `CAPTURE_STROKE_SCRUB`, `CAPTURE_FONT_SIZE_SCRUB` and `CAPTURE_TOOL_LOCK`. **TA-4 (R1-F3):** `ui/tests/unit/capture-page.behavior.test.ts` AC-57.5 (`:1253`) asserts `screen.getByTestId('capture-stroke').closest('label')?.textContent` matches `/Stroke/`, which `SCRUB_FIELD` removes (AC-85.9 requires the input outside any `<label>`). That one line becomes two: `expect(screen.getByTestId('capture-stroke-scrub').textContent).toBe('Stroke')` keeps the visible label, and `expect(screen.getByTestId('capture-stroke').getAttribute('aria-label')).toBe('Stroke width')` keeps the input's name. It is applied in row 2 and fails until row 3, like the new tests. Amendments change only those lines. | Spec 09:752, 09:764; D-15, D-18 |
| `CENSUS_PATTERNS` | Row 1 greps `ui/tests` for: `TOOLBAR_BUTTONS`, `TOOL_BUTTON_IDS`, `NO_SHOT_IDS`, `MEU65_`, `expectOptionGroups`, `capture-stroke`, `capture-font-size`, `capture-named-color`, `NATIVE_OPTION_MENU_STYLE`, `G30`, `AC-60.4`, `aria-pressed`, `capture-chrome-tools`, `expectNoOverflow`, `Annotation tool`, `four tools`, `four-tools`, `commitSelection`, `parsePositiveInt`, `option.style`, `12 Capture toolbar`, `<label`. Each hit is dispositioned as `TA-n`, as `unaffected` with the reason, or as `new-contradiction`, which triggers S2. | Local Canon (Session 36/39 census) |

### MEU-85 — `gui-capture-size-scrub`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Stroke field (`capture-stroke`) → `rect`/`arrow` `stroke_width` | renderer Zod annotate schema (`capture-annotate.ts`, unchanged) | Wire: positive int, no upper bound. Scrub: `[SCRUB_MIN, STROKE_SCRUB_MAX]`, never against the gesture (`SCRUB_MATH`) | n/a (the field emits an int; the mark keeps its other fields) |
| Font-size field (`capture-font-size`) → `text` `font_size` | same | Wire: positive int, no upper bound. Scrub: `[SCRUB_MIN, FONT_SCRUB_MAX]` | n/a |

No new wire surface: the Save body, the sidecar and the API are unchanged.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-85.1 | unit | `scrubSteps`: 5 px coarse gives 2 steps with carry 1, and a further 1 px gives 1 step with carry 0. −5 px gives −2 steps with carry −1. 15 px fine gives 1 step with carry 7. The `SCRUB_MATH` constants have their values. | `SCRUB_MATH` | 1 px coarse gives 0 steps and carry 1 (no step below the width) |
| AC-85.2 | unit | `clampScrub`: 99 +10 → 100, and 1 −1 → 1, at `max` 100. At 500: +1 → 500 and −1 → 499. `parsePositiveInt` keeps its behaviour (`'12'` → 12; `' 7 '` → 7) and is exported from `capture-scrub.ts`. | `SCRUB_MATH` | `parsePositiveInt` gives `null` for `'0'`, `'-3'`, `'2.5'`, `'abc'` and `''` |
| AC-85.3 | unit | `CaptureScrubField` drag (jsdom pointer events; `setPointerCapture` polyfilled). On the handle: pointerdown, then moves totalling +20 px. Result: `onPreview` last called with 13 from text `'3'`, and `onCommit` once on pointerup. With Shift, +4 px gives 23. With Alt, +16 px gives 5. A press with no move selects the input text and calls neither `onPreview` nor `onCommit`. | `SCRUB_GESTURES`; `SCRUB_BASE` | Escape mid-drag calls `onCancel` and not `onCommit`; a secondary-button press does nothing |
| AC-85.4 | unit | `CaptureScrubField` wheel and keys (fake timers). Three wheel events with `deltaY −100` give previews 4, 5 and 6 and one `onCommit` after `WHEEL_RESET_MS`. Shift+wheel with `deltaY 0, deltaX −100` gives +10. ArrowUp gives +1, and keyup commits. Shift+ArrowDown gives −10. Unparsable text starts from `fallback`. | `SCRUB_GESTURES`; `SCRUB_BASE` | Ctrl+wheel neither previews nor calls `preventDefault`; ArrowLeft neither previews nor calls `preventDefault` |
| AC-85.5 | unit | `SCRUB_ALT_GUARD`: during a drag, a window Alt `keydown` and an Alt `keyup` both have `defaultPrevented === true`. This proves the listener, not the native menu suppression, which AC-85.10's real input covers only implicitly. | `SCRUB_ALT_GUARD` | After pointerup, neither Alt event is prevented |
| AC-85.6 | integration | Page behaviour, selected box with stroke 3. Dragging `capture-stroke-scrub` +20 px shows the box's `stroke-width` as 13 before pointerup, and `capture-save` is disabled while the drag is open. After pointerup, one Undo restores 3, and one Redo gives 13. With a selected text mark at size 16, three wheel notches over `capture-font-size` give 19; Undo is disabled until the timers pass `WHEEL_RESET_MS`, and then one Undo restores 16. | `SIZE_BURST`; Spec 09:753 | Escape mid-drag restores 3, and Undo stays disabled (no history entry) |
| AC-85.7 | integration | Page behaviour with no applicable mark (Box tool, nothing selected): dragging the stroke handle +10 px sets the field to 8 and changes no mark. Undo stays disabled. The next box drawn has `stroke_width` 8. | `SIZE_BURST` | A box already on the shot but not selected keeps `stroke_width` 3 |
| AC-85.8 | integration | Typed edits are unchanged. With a box selected, typing `5` then `7` in `capture-stroke` (one change each) takes two Undo clicks to restore 3. With a text selected, a wheel burst followed by a typed change before the burst ends gives two undo steps (the burst, then the typed change). | `TYPED_EDITS`; `SIZE_BURST` | Typed `0` changes no mark |
| AC-85.9 | integration | `SIZE_LABELS`: `capture-stroke-scrub` reads "Stroke" and `capture-font-size-scrub` reads "Size". Both are `aria-hidden` and have no `tabindex`. Tab from the color controls reaches the inputs, never the handles. The inputs keep their `aria-label`. | `SIZE_LABELS`; `SCRUB_FIELD` | `capture-stroke` is not inside a `<label>` (the handle press must not be a label click) |
| AC-85.10 | integration | Electron, real input. Draw a box, which is selected with stroke 3. Then: drag `capture-stroke-scrub` +40 px, and the box's `stroke-width` attribute reads 23 before `mouse.up`. Shift-drag +6 px gives 53. Drag +200 px, past the field's edge, gives 100 (pointer capture). Three Undo clicks give 53, 23 and 3. | Spec 09:752-753; `SCRUB_GESTURES` | Red (row 2, `ELECTRON_RED`): on the baseline renderer the handle count is 0 |
| AC-85.11 | unit | Help: the `four-tools` body contains the scrub sentence of `HELP_SENTENCES`. | `HELP_SENTENCES` | The body before the change does not contain it |
| AC-85.12 | integration | Page behaviour, fake timers, one owner (R1-F1). A selected box at stroke 3, with keyboard focus on the draw surface, not the field. (a) One wheel notch over `capture-stroke` shows `stroke-width` 4 and disables `capture-save`. Before `WHEEL_RESET_MS`, ArrowRight keydown and keyup on the window nudge the box, which first finishes the size burst. Advance the timers past `WHEEL_RESET_MS`. One Undo gives stroke 4 at the original position, a second Undo gives stroke 3, and Undo is then disabled. (b) Two boxes, A selected: one wheel notch over `capture-stroke`, then a pointerdown that selects B before `WHEEL_RESET_MS`. A keeps stroke 4 with one undo entry, B keeps stroke 3, and the later timer adds no entry. (c) An unfocused wheel notch, then Escape on the window, restores stroke 3; advancing the timers adds no entry and Undo stays disabled. (d) With one earlier undo entry, one wheel notch disables `capture-undo` and `capture-redo` until the timers pass `WHEEL_RESET_MS`; then one Undo gives stroke 3 and a second Undo reaches the earlier entry. (e) Two shots, a box on shot 1 selected: one wheel notch, then choosing shot 2 and accepting the dirty confirm before `WHEEL_RESET_MS`. After the timers pass, shot 2's Undo is disabled. | `SIZE_BURST` (one owner, idempotent finish and cancel, Undo and Redo gated, shot change discards) | A model without one owner makes the second Undo of (a) give stroke 4 again (the R1-F1 counterexample) |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Gestures | Spec / Research-backed | 09:752 drag the label, Shift ×10, Alt fine, wheel, Up/Down. Pixel sensitivity follows Base UI `NumberField.ScrubArea` (D-10) |
| Limits | Research-backed / Local Canon | The wire has no upper bound, so the caps are UI-only and never act against the gesture (D-10) |
| Live preview and undo | Spec | 09:753; `SIZE_BURST` follows the nudge burst (D-13) |
| Typed edits | Local Canon | Unchanged (D-14) |
| Shift+wheel on Windows | Research-backed | Chromium sends a horizontal delta; use `deltaX` when `deltaY` is 0 (D-11) |
| Alt during a drag | Research-backed | The Electron default menu takes focus on an Alt release; guard it during the drag (D-12) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-scrub.ts` | new | `SCRUB_MATH` |
| `ui/src/renderer/src/features/capture/CaptureScrubField.tsx` | new | `SCRUB_FIELD`, `SCRUB_GESTURES`, `SCRUB_ALT_GUARD` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | Stroke and font-size fields render through `CaptureScrubField` (`SIZE_LABELS`); new props for preview, commit and cancel |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `SIZE_BURST` (`sizeBurstRef`, `previewSize`, `finishSize`, `cancelSize`, Escape branch, finish-first calls, `canUndo` / `canRedo` gated on `txOpen`, reset effect clears the burst); `parsePositiveInt` imported from `capture-scrub.ts` |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | scrub sentence (`HELP_SENTENCES`) |
| `ui/tests/unit/capture-scrub.test.ts` | new | AC-85.1 to AC-85.5 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-85.6 to AC-85.9, AC-85.12; TA-4 |
| `ui/tests/unit/capture-help-content.test.ts` | modify | AC-85.11 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-85.10 |
| `ui/tests/e2e/test-ids.ts` | modify | TA-3 (`CAPTURE_STROKE_SCRUB`, `CAPTURE_FONT_SIZE_SCRUB`) |

### MEU-86 — `gui-capture-color-swatches`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `contrastText(hex)` input | `normalizeHex` (`capture-color.ts`) | `#RRGGBB` (any case) | anything else throws `RangeError` |

The Named select's values and the colour it applies are unchanged, so no wire surface is involved.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-86.1 | unit | `contrastText` gives the R-2 table for the seven named colours: red, orange, yellow and white → `#000000`; green, blue and black → `#FFFFFF`. For every named colour, the WCAG ratio of the pick is at least 4.5 (computed in the test). Lowercase input gives the same result. | `CONTRAST_TEXT`; R-2 | Red gets black, not white (a naive `L < 0.5 → white` rule gives white at 4.00:1). `contrastText('red')`, `'#FFF'` and `''` throw `RangeError` |
| AC-86.2 | integration | Page behaviour (TA-1): each named option's inline `background-color` is its `NAMED_COLOR_HEX` value, and its `color` is `contrastText` of that value. The placeholder option keeps `NATIVE_OPTION_MENU_STYLE`. The closed select keeps `namedMenuStyle`. Choosing an option still applies its colour as before. | `SWATCH_OPTIONS` | The placeholder is not painted with a named colour |
| AC-86.3 | integration | Electron: `getComputedStyle` of each named option in `capture-named-color` gives `backgroundColor` equal to its hex as `rgb(…)` and `color` equal to its contrast pick. | Spec 09:765 ("Electron check of the rendered option style") | Red (row 4): on the baseline renderer, the orange option's computed `backgroundColor` is `rgb(255, 255, 255)` |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Option background | Spec | 09:764 |
| Text colour rule | Research-backed | WCAG 2.1 relative luminance and contrast ratio; pick the higher ratio (D-17, R-2) |
| Fallback popover | Spec (conditional) | Not needed: R-1 (D-16) |
| Closed select | Local Canon | G30 unchanged |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-color.ts` | modify | `contrastText` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `SWATCH_OPTIONS` |
| `ui/tests/unit/capture-color.test.ts` | modify | AC-86.1 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-86.2 (TA-1) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-86.3 |

### MEU-87 — `gui-capture-tool-lock`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `TOOLBAR_BUTTONS['capture-tool-lock']` | `capture-toolbar.ts` `ToolbarButtonSpec` | `{icon, name}`, non-empty name | n/a |

`toolLocked` is view state: it is not part of the overlay, the Save body or any setting.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-87.1 | unit | `TOOLBAR_BUTTONS['capture-tool-lock']` has the lucide `Lock` icon and the name "Keep tool after drawing". `capture-tool-lock` is not a value of `TOOL_BUTTON_IDS`. | `TOOL_LOCK` | `Object.keys(TOOL_BUTTON_IDS)` still equals the five tools (AC-65.1 holds) |
| AC-87.2 | integration | Page behaviour: `capture-tool-lock` sits straight after the Annotation tool group and has `aria-pressed="false"`. A click toggles it to `"true"` and back. It is enabled with no shot. Toggling it changes neither the active tool nor the selection, and does not enable Save. | `TOOL_LOCK` | With no shot, the lock is not disabled (unlike the tools) |
| AC-87.3 | integration | Page behaviour: lock on with the Box tool. Two drags create two boxes. After each, `capture-tool-box` stays `aria-pressed="true"` and no mark is selected. Two Undo clicks remove them one at a time. | `LOCK_KEEPS_TOOL` | With the lock off, the first drag leaves `capture-tool-select` pressed and the new box selected (AC-60.4 unchanged) |
| AC-87.4 | integration | Page behaviour: lock on with the Text tool. Committing a text keeps `capture-tool-text` pressed with nothing selected, and a second click on the image opens a new draft. | `LOCK_KEEPS_TOOL` | With the lock off, the commit selects the new text and returns to Select |
| AC-87.5 | integration | Page behaviour: lock on, choose Box and draw, then choose Arrow and draw. Arrow stays pressed and the lock stays `"true"`. Turn the lock off and draw an arrow: the tool returns to Select with the new arrow selected. | `LOCK_PERSISTS` | Choosing Arrow does not turn the lock off |
| AC-87.6 | integration | Electron, real input: lock on, Box tool, two drags. There are 2 `rect[data-annotation-type="rect"]`, and `capture-tool-box` keeps `aria-pressed="true"`. | Spec 09:777 ("behaviour tests with and without") | Red (row 6, `ELECTRON_RED`): on the baseline renderer the lock count is 0 |
| AC-87.7 | unit | Help: the `four-tools` body contains the lock sentence of `HELP_SENTENCES`. | `HELP_SENTENCES` | The body before the change does not contain it |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Default | Human-approved | 09:775: auto-Select stays the default (triage D-63) |
| Lock semantics | Human-approved / Research-backed | 09:776; Excalidraw and tldraw keep the lock across tool changes (D-19, User Review Required item 3) |
| Visible state | Spec | `aria-pressed` (09:776) |
| Persistence | Research-backed | View state, not saved (D-18) |
| Shortcut | Local Canon | None: Capture has no tool keys (Out of Scope) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modify | `TOOL_LOCK` entry |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | the lock button; `toolLocked` and `onToggleToolLock` props |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `toolLocked` state; `LOCK_KEEPS_TOOL` in the drawn-create and text-commit paths |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | lock sentence (`HELP_SENTENCES`) |
| `ui/tests/unit/capture-toolbar.test.ts` | modify | AC-87.1 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-87.2 to AC-87.5 |
| `ui/tests/unit/capture-help-content.test.ts` | modify | AC-87.7 |
| `ui/tests/unit/icon-hints.test.ts` | modify | TA-2 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-87.6 |
| `ui/tests/e2e/test-ids.ts` | modify | TA-3 (`CAPTURE_TOOL_LOCK`) |

### Hub and state files (row 9)

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | modify | §Size scrubbing, §Named colour swatches and §Tool lock each gain a "Plan" note naming their contracts ("Session 37 plan D-10–D-19": `SCRUB_MATH` with UI-only caps; `CONTRAST_TEXT` with no popover per R-1; `LOCK_PERSISTS`) |
| `docs/build-plan/gui-actions-index.md` | modify | add `capture:tool_lock` ("Keep tool after drawing (tool lock)", local canvas, specified, 09) after `capture:tool_text` (`:79`), in that row's format |
| `docs/build-plan/build-priority-matrix.md` | modify | add rows 9.18, 9.19 and 9.20 (MEU-85, 86, 87) after 9.17 (`:74`), in the 9.17 row format, with the dependencies from 09:868-870 |
| `docs/BUILD_PLAN.md` | modify | Phase 9 status line (`:53`) gains "MEU-85–87 bound to capture-editor-options." and the date. AUTOGEN regions change only through `meu_status.py render` |
| `.agent/context/meu-status.yaml` | modify | MEU-85/86/87 `execution_plan` + status (H1-3) |
| `.agent/context/meu-registry.md` | generated | written by `meu_status.py render`; never hand-edited |
| `.agent/context/current-focus.md` | modify | the current focus names Session 37 (H1-3) |
| `.agent/context/known-issues.yaml` | modify | the three issues → `resolved` with the handoff link, after H1-7b approval (H2) |
| `.agent/context/known-issues.md` | generated | written by `issue_triage.py render` (H2-2); never hand-edited |
| `docs/execution/metrics.md` | modify | the Session 37 row (H2-3) |

`06-gui.md` needs no edit. Its help-topic row (`:325`) names "four tools", and the title stays. Its Wave 9 test count (`:1249`, **42**) was already stale before this session, so it is not this plan's count to own.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Scrub on Session 39's Block size field | deferred | MEU-90 | Session 39 owns that field. It does not exist on `main`. `CaptureScrubField` is shared so the field can adopt it (D-9) |
| Scrub on the hex field or Bg field | out-of-scope | — | 09:752 names the size fields only |
| A swatch popover | out-of-scope | — | 09:764 makes it conditional on the target ignoring option backgrounds; R-1 shows it does not (D-16) |
| A keyboard shortcut for the lock | out-of-scope | — | Capture has no tool shortcuts; 09:776 names only the visible state |
| Persisting the lock across sessions or shots | out-of-scope | — | D-18: view state, like the active tool |
| API or domain upper bounds for `stroke_width` and `font_size` | out-of-scope | — | D-10: the wire stays as it is; no MEU asks for it |
| Renaming the `four-tools` help section | out-of-scope | — | D-20; Session 39 retitles it (`HELP_TOOLS`) |
| The stale Wave 9 count in `06-gui.md:1249` | out-of-scope | — | Not created by this session and not checked by any test |

## BUILD_PLAN.md Audit

This project edits the D3 hub in task row 9 only (§Hub and state files). The validation is exact:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s37-state-render.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s37-state-render.txt; exit $code
```

```powershell
rtk proxy rg -n -e "MEU-8[5-7]" -e "9\.18" -e "9\.19" -e "9\.20" -e "capture-editor-options" -e "tool_lock" -e "Session 37 plan" docs/BUILD_PLAN.md docs/build-plan/build-priority-matrix.md docs/build-plan/09-screenshot-capture.md docs/build-plan/gui-actions-index.md *> C:/Temp/av-kit/s37-hub-rg.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s37-hub-rg.txt; exit $code
```

Row 9's deliverable has three parts:

- the `rg` receipt shows each edit: matrix rows 9.18–9.20, the Phase 9 line, the three 09 Plan notes, and the gui-actions-index row;
- `render --check` exits 0;
- `gui-actions-audit` passes.

## Verification Plan

All commands run from `WT` in `pwsh`, after `$env:ELECTRON_RUN_AS_NODE=$null; $env:ELECTRON_RENDERER_URL=$null` for any Electron step. Receipts go to `C:/Temp/av-kit/s37-*.txt`. The ids are PROFILE D6's (`.agent/docs/commands.md:190-210`); targeted runs use the same argv with a file list.

### 1. Prerequisites and baseline (row 0)

- `uv venv --python 3.12.12 .venv`, then `uv sync --frozen --all-packages`, `npm --prefix ui ci` and `npm --prefix mcp-server ci`. Python is pinned because Session 39's unpinned venv resolved to CPython 3.14, where spaCy fails.
- `BASE_MARKERS` and the MEU statuses (S1).
- `git rev-parse HEAD > docs/execution/plans/2026-10-16-capture-editor-options/baseline.sha`.
- The baseline receipts, in this order:
  - `py-tests`, `ui-tests`;
  - `mcp-build`, then `mcp-tests` (G-1: the tests load `mcp-server/dist`);
  - `ui-build`;
  - `ui-electron` over `capture-inbox.test.ts`.
- Recording the baseline:
  - The failed pytest ids are written to `baseline-py-failed.txt`, one per line, and the gate's py-tests rule reads that file.
  - Every baseline failed set is recorded in `walkthrough.md` §Baseline.
  - A test that fails at baseline is never counted as a regression; a test that passes at baseline and fails later is.

### 2. Red (rows 2, 4, 6)

Each MEU's new and amended tests are written first. They must fail either by assertion, or because a declared-new name does not exist yet. The declared-new names are those in `red-check.py` `DECLARED_NEW`:

- the `capture-scrub` module and its exports;
- the `CaptureScrubField` module;
- `contrastText`.

Two rules shape how the tests fail:

- **A new export from an existing module** (`contrastText` from `capture-color.ts`) is `undefined` under Vite SSR. So its Red reason is `TypeError: (0 , __vite_ssr_import_N__.contrastText) is not a function`. `red-check.py` accepts this only for a declared-new subject.
- **A new control is counted first** (`ELECTRON_RED`), so its absence fails an assertion and not a locator or query timeout.

Each MEU's Electron Red runs in its Red row. The baseline renderer serves the existing seam, and only the test file changes, so no backend or fixture row has to come first. The row builds the UI and runs `--grep` for its own AC.

`RED_PROOF`: [red-check.py](red-check.py) decides each Red. Each Red command writes its child exit code to `<receipt>.exit` straight after `$code=$LASTEXITCODE`. The checker requires:

- a non-zero exit;
- a failing-run summary;
- a *diagnostic* line that attributes the failure. That is an `AssertionError:` or `Error: expect(` line, or a load/import/`is not a function` error whose missing *subject* is a declared-new name. The subject comes from the error's own grammar. A declared name elsewhere on the line, such as the importing test file, does not count;
- no setup failure: an Electron launch, a test or action timeout, a refused connection, or an unrelated load or collection error.

Source-context and test-title lines never count. `red-check.py --selftest` runs 24 receipt fixtures, 9 positive and 15 negative (R-4). An error diagnostic that is neither an assertion nor a declared-new subject refuses the receipt even when another test failed by assertion, and a declared name must match the subject's whole leaf (R1-F4). The checker proves the receipt, not each test: the walkthrough's Red section lists every new-behaviour test with its first diagnostic line, and the execution review checks that list.

### 3. Targeted Green (rows 3, 5, 7)

```powershell
rtk proxy npm --prefix ui run test -- tests/unit/capture-scrub.test.ts tests/unit/capture-color.test.ts tests/unit/capture-toolbar.test.ts tests/unit/capture-help-content.test.ts tests/unit/capture-page.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/icon-hints.test.ts tests/unit/gui-actions-audit.test.ts *> C:/Temp/av-kit/s37-ui-targeted.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s37-ui-targeted.txt | Select-Object -Last 25; exit $code
```

```powershell
$env:ELECTRON_RUN_AS_NODE=$null; $env:ELECTRON_RENDERER_URL=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s37-ui-build.txt; if ($LASTEXITCODE -ne 0) { Get-Content C:/Temp/av-kit/s37-ui-build.txt | Select-Object -Last 25; exit $LASTEXITCODE }; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts *> C:/Temp/av-kit/s37-e2e-capture.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s37-e2e-capture.txt | Select-Object -Last 30; exit $code
```

### 4. Session gate (rows 8, H1-2): `session-gate.ps1`

The plan-local [session-gate.ps1](session-gate.ps1) runs in `pwsh` from `WT`.

- It writes one receipt per step (`C:/Temp/av-kit/s37-D6-<id>.txt`) and prints `<id> stage=<stage> exit=<n>` and the receipt tail.
- It is fail-fast in stage order: after the first non-zero step, every later step is printed as `not_run`.
- It sets `RECEIPTS_DIR` to `C:/Temp/av-kit`. No user or machine scope on this host sets it, and without it `lint_task_contract.py` fails closed (exit 3) because it cannot recognise the instantiated receipt paths.
- Session 37 changes no Python, API or MCP source, so the `py-*`, `mcp-*` and `openapi` steps are no-drift checks.

The steps, in order:

1. `identity-before`: `INPUT_IDENTITY` (§Validation stage contract).
2. **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, then `scope-paths` (`SCOPE_CHECK`, §5).
3. **Full:**
   - `py-tests` runs the whole suite. Exit 1 passes only when every FAILED id is in `baseline-py-failed.txt` and nothing ERRORs.
   - `ui-tests`.
   - `mcp-build`, then `mcp-tests` (G-1).
   - `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi` and `state-render`.
4. **Runtime:** `ui-electron` (the full Electron suite), then `e2e-repeat`, which runs `test:e2e -- tests/e2e/capture-inbox.test.ts --grep "AC-85.10|AC-86.3|AC-87.6" --repeat-each=10`. Any flake is a defect (S6).
5. `identity-npm`, then `identity-after`. The gate fails when `tested_state` differs between `identity-before` and `identity-after`.

The row's command is `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-editor-options/session-gate.ps1`, with the receipt pattern (task row 8). The D6 `mcp-audit` runtime check is not a gate step, because no MCP surface changes.

### 5. `SCOPE_CHECK` (row 8)

`scope-paths` takes every path in `git diff --name-only <baseline>` plus the untracked files. Each one must be either:

- a Files Modified row (product, test, hub or state file), or
- one of this project's artifacts: this plan folder, the handoffs, or the reflection.

The allow-list in `session-gate.ps1` is the union of the Files Modified tables; changing either one means changing both. Product files outside `ui/src/renderer/src/features/capture/` are therefore refused, which enforces `PRODUCT_SCOPE`.

### 6. OpenAPI drift (G8)

`packages/api/` does not change. The `openapi` D6 check (`--check`) must pass in the gate. H1-4 also proves that `openapi.committed.json` has no diff since `baseline.sha`.

### 7. Closeout (H1, H2)

These are the template commands with this project's paths:

- `validate_closeout_artifacts.py` per handoff, in two runs: `--handoff` + `--plan`, then `--ac-coverage-only`;
- `durable_evidence.py --require-full`;
- the review-state parsers;
- the reflection validator, with `--decision-source` for the plan, the three handoffs, the grouping file and `.agent/context/known-issues.yaml`, and `--decision-issue` for each of the three issue ids;
- `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped: `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent. This is recorded as `gui-refs-not-shipped`. New and changed elements:

| Element | Kind | Change | Standard | E2E |
|---|---|---|---|---|
| `capture-stroke-scrub` | scrub handle (new) | `SCRUB_FIELD`; visible "Stroke", `aria-hidden`, no tab stop | E2 (`emerging-standards.md:1167`) | AC-85.10 |
| `capture-font-size-scrub` | scrub handle (new) | `SIZE_LABELS` "Size" | E2 | AC-85.9 (behaviour) |
| `capture-stroke`, `capture-font-size` | number inputs (changed) | wheel and Up/Down steps; ids, `aria-label` and `title` kept | E2 | existing `fill` calls (`capture-inbox.test.ts:258`, `:449`, `:578`) |
| `capture-named-color` options | select options (changed) | `SWATCH_OPTIONS`; the closed select keeps G30 | G30 | AC-86.3 |
| `capture-tool-lock` | icon toggle button (new) | `TOOL_LOCK`; `aria-pressed`; hint = name (Session 34 icon-button hints) | E2 | AC-87.6; AC-65.4 overflow check at the default window |
| help section `four-tools` | output (changed) | `HELP_SENTENCES` | — | AC-85.11, AC-87.7 |

- **G36** (no silent test guards): the tests assert and never `skip`.
- **G37:** the behaviour tests use `userEvent`. Pointer gestures that need exact `clientX` deltas, modifier state and pointer capture use `fireEvent.pointer*`, as the existing drag tests in `capture-page.behavior.test.ts` do.
- **G30:** the closed select is unchanged; only the options are painted.

The lock and the "Size" label add width to the toolbar and options rows. If AC-65.4 (`expectNoOverflow`) then fails at the default window, that is S2, not a test edit.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a graph directory, a missing `BASE_MARKERS` symbol, `capture-block-size` in `ui/src`, MEU-60/65/80/81 not `approved`, or MEU-85/86/87 not `pending` | Stop. Ask Mat: land Sessions 34 and 36 first, or amend the plan for Session 39's field, or re-run the context-tool gate. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS`, or AC-65.4 overflows | Stop for the human with a Decision Brief naming the test and the smallest amendment. No test edit. |
| S3 | `red-check.py` refuses a Red receipt (`RED_PROOF`, §2) | Fix the test setup only, then re-prove Red. |
| S4 | AC-86.3 shows the target does not apply option styles, or AC-85.10 cannot get pointer capture in Electron | Stop for a Decision Brief: build `POPOVER_FALLBACK`, or change the drag model. |
| S5 | `SCOPE_CHECK` finds a change outside the Files Modified rows, or `openapi.committed.json` changed | Revert that change or stop with a Decision Brief. |
| S6 | An Electron flake under `--repeat-each` | Fix the test's waiting and never add retries. If the product is racy, stop with a brief. |
| S7 | Review cap reached (plan 3, execution 6), or the reviewer is unavailable | HARD STOP with a TL;DR (create-plan §5d). Mat is the fallback reviewer. |

## Decision Log

The research engine for this plan is `native` (Claude Code web search, 2026-10-16).

- Grouping §8 D-1, D-3, D-4 and D-6 carry forward unchanged into the reflection, with stage `grouping`. D-2, D-5 and D-7 do not touch this scope.
- This plan's ids start at D-8.
- "Triage D-56/D-57/D-63" are the 2026-10-09 triage decisions that the spec cites.

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "Where is the plan written and executed?"
    resolution: autonomous
    class: two-way
    chosen: "Worktree P:/av-kit-wt/s37-capture-editor-options on branch claude/s37-capture-editor-options, cut from main 90bb409"
    source_tag: Local Canon
    precedents: ["Session 36 D-8 and Session 39 D-8 (worktree per session)"]
    research: { engine: none, sources: [] }
    reasoning: "A worktree isolates this session from the open Session 39 branch. D6 argv are unchanged; only the cwd differs."
  - id: D-9
    stage: planning
    question: "How does this plan coordinate with Session 39, which edits the same renderer files and adds a Block size field?"
    resolution: autonomous
    class: two-way
    chosen: "Plan and execute on main as it is (Session 39 not landed). CaptureScrubField is a shared component. Row 0 stops (S1) if capture-block-size appears in ui/src, so the plan is amended before it runs on a base it did not plan for."
    source_tag: Local Canon
    precedents: ["Session 39 Out of Scope defers the Block size scrub to MEU-85", "grouping D-4 session order 37 before 39"]
    research: { engine: none, sources: [] }
    reasoning: "The grouping orders 37 before 39, so this plan should not assume Session 39's field. A stop on the marker is cheaper than a silent half-integration, and a shared component lets whichever session lands second adopt the scrub with one line."
  - id: D-10
    stage: planning
    question: "What are the scrub step widths and limits?"
    resolution: autonomous
    class: two-way
    chosen: "SCRUB_MATH: 2 px per step, 8 px per step with Alt, ×10 with Shift; UI caps 1..100 (stroke) and 1..400 (font size) that never move a value against the gesture; wire bounds unchanged"
    source_tag: Research-backed
    precedents: ["capture-annotate.ts stroke_width and font_size are z.number().int().positive() with no upper bound", "API and domain accept any positive int"]
    research: { engine: native, sources: ["https://base-ui.com/react/components/number-field"] }
    reasoning: "Base UI's NumberField.ScrubArea moves one step per pixelSensitivity pixels (default 2) and uses modifier keys for larger and smaller steps, which matches 09:752. A 2 px step lets a 100-px drag cover a useful stroke range. A cap is needed to make a drag past the field edge predictable, but the wire has no cap, so a typed larger value must survive a scrub; hence clamping never acts against the gesture. 400 covers a 4K headline; 100 covers any useful stroke."
  - id: D-11
    stage: planning
    question: "How does Shift+wheel step by 10 on Windows?"
    resolution: autonomous
    class: two-way
    chosen: "Use deltaX when deltaY is 0, through the existing wheelSteps accumulator"
    source_tag: Research-backed
    precedents: ["capture-zoom.ts wheelSteps (WHEEL_STEP_PX, WHEEL_RESET_MS)"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/API/Element/wheel_event"] }
    reasoning: "Chromium on Windows reports Shift+wheel as a horizontal scroll (deltaX, deltaY 0). Reading deltaX in that case makes Shift+wheel work instead of doing nothing. Reusing wheelSteps keeps pixel-mode and line-mode wheels consistent with zoom."
  - id: D-12
    stage: planning
    question: "Alt is the fine modifier, but Electron's menu bar takes focus on an Alt press and release. What then?"
    resolution: autonomous
    class: two-way
    chosen: "SCRUB_ALT_GUARD: preventDefault on Alt keydown and keyup while a drag is open"
    source_tag: Research-backed
    precedents: ["09:752 'Alt fine'"]
    research: { engine: native, sources: ["https://github.com/electron/electron/pull/29318"] }
    reasoning: "Electron lets the page suppress the default Alt menu toggle by preventing the key event. Guarding only during a drag leaves Alt's normal menu behaviour everywhere else. Playwright key events do not reach the native menu, so this is proven by a unit test only."
  - id: D-13
    stage: planning
    question: "How is one gesture one undo step?"
    resolution: autonomous
    class: two-way
    chosen: "SIZE_BURST: store the origin list at the first applicable step, update live without history, push the origin once on commit if anything changed, restore on cancel; txOpen during the burst; one owner: each burst finishes the other first, and every handler that writes the marks, the selected mark or the history finishes the size burst first (round 1 F1); Undo and Redo are disabled while txOpen, and a shot change discards the burst (round 2 call-site census)"
    source_tag: Local Canon
    precedents: ["CapturePage nudge burst (nudgeBurstRef, finishNudge, Escape restore)", "09 §Annotation edit until Save"]
    research: { engine: none, sources: [] }
    reasoning: "The arrow-key nudge already coalesces a key burst into one undo step with txOpen blocking Save and tool changes; txOpen now also disables Undo and Redo, for both bursts. Using the same shape keeps one model for transient edits and reuses the Escape path."
  - id: D-14
    stage: planning
    question: "Do typed edits in the size fields change?"
    resolution: autonomous
    class: two-way
    chosen: "No: TYPED_EDITS keep one applyHistory per applied change"
    source_tag: Local Canon
    precedents: ["changeStroke and changeFontSize (MEU-60)"]
    research: { engine: none, sources: [] }
    reasoning: "09:753 speaks about gestures; typed edits already work and have tests. Changing them would widen scope with no request."
  - id: D-15
    stage: planning
    question: "What is the scrub handle, and does the font-size field get a visible label?"
    resolution: autonomous
    class: two-way
    chosen: "SCRUB_FIELD: an aria-hidden span handle beside the input (not a label element), shared by both fields; the font-size field shows 'Size'"
    source_tag: Research-backed
    precedents: ["the Stroke field is a label element with visible 'Stroke'", "the font-size input has no visible label today"]
    research: { engine: native, sources: ["https://base-ui.com/react/components/number-field"] }
    reasoning: "A label element's click focuses its input and would race the drag. A span handle with pointer capture is what Base UI's ScrubArea renders. The handle duplicates the input's accessible name, so it is aria-hidden, and the input stays the only tab stop. Dragging needs visible text, so the font field gains 'Size'."
  - id: D-16
    stage: planning
    question: "Native select options or a swatch popover?"
    resolution: autonomous
    class: two-way
    chosen: "Native options with inline background and text colour; no popover"
    source_tag: Research-backed
    precedents: ["09:764 makes the popover conditional on the target ignoring option backgrounds", "R-1 probe"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option"] }
    reasoning: "Option styling support varies by platform, which is why the spec has a fallback. R-1 opened a real select in Electron 42.9.3 on Windows and captured the popup. Every option showed its own background and text colour. The target honours option styles, so the popover would be dead code."
  - id: D-17
    stage: planning
    question: "Which text colour goes on each swatch?"
    resolution: autonomous
    class: two-way
    chosen: "CONTRAST_TEXT: black or white, whichever has the higher WCAG 2.1 contrast ratio (black on a tie)"
    source_tag: Research-backed
    precedents: ["R-2: every pick reaches 4.5:1; a naive L<0.5 rule would put white on red at 4.00:1"]
    research: { engine: native, sources: ["https://www.w3.org/TR/WCAG21/#dfn-relative-luminance", "https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio"] }
    reasoning: "Comparing the two real ratios is the standard rule and needs no tuned threshold. Its crossover is L≈0.179, which R-2 shows puts red (L 0.213) on black at 5.25:1. The simpler half-luminance threshold fails AA for red."
  - id: D-18
    stage: planning
    question: "Where does the lock live and how is it stored?"
    resolution: autonomous
    class: two-way
    chosen: "TOOL_LOCK: a ToolbarIconButton after the Annotation tool group, in TOOLBAR_BUTTONS but not TOOL_BUTTON_IDS; page view state, default off, not persisted"
    source_tag: Research-backed
    precedents: ["AC-65.1 requires TOOL_BUTTON_IDS keys to equal the tools", "Session 34 icon-button hints iterate TOOLBAR_BUTTONS"]
    research: { engine: native, sources: ["https://github.com/excalidraw/excalidraw", "https://tldraw.dev/reference/editor/TLInstance"] }
    reasoning: "Excalidraw shows its lock as a toolbar toggle beside the tools and keeps it as app state. tldraw keeps isToolLocked on the instance record. Being in TOOLBAR_BUTTONS gives the lock the shared icon, name and hint; keeping it out of TOOL_BUTTON_IDS keeps it from being treated as a tool. Not persisting it matches the active tool, which is not persisted either."
  - id: D-19
    stage: planning
    question: "Does choosing another tool release the lock?"
    resolution: autonomous
    class: two-way
    chosen: "No (LOCK_PERSISTS): the lock stays on and keeps the newly chosen tool; only the lock button releases it. Flagged for Mat (User Review Required item 3); Mat approved it 2026-10-16."
    source_tag: Research-backed
    precedents: ["09:776 'until the lock is released or another tool is chosen'"]
    research: { engine: native, sources: ["https://github.com/excalidraw/excalidraw", "https://tldraw.dev/reference/editor/TLInstance"] }
    reasoning: "In Excalidraw and tldraw the lock is a mode that survives tool changes. Read that way, 09:776 lists the two events that end the current tool being kept. The other reading would make a user re-lock after every tool change, which defeats the lock for mixed annotation. The choice is two-way and changes only AC-87.5."
  - id: D-20
    stage: planning
    question: "How is help updated?"
    resolution: autonomous
    class: two-way
    chosen: "HELP_SENTENCES appended to the four-tools body; id and title kept"
    source_tag: Local Canon
    precedents: ["capture-help-content tests read the section by id and use toContain on the body", "Session 39 HELP_TOOLS retitles the section"]
    research: { engine: none, sources: [] }
    reasoning: "Appending keeps every existing assertion green and leaves the retitle to Session 39, so the two sessions touch different parts of the section."
```

## Research References

- Base UI NumberField (ScrubArea, `pixelSensitivity`, modifier steps): https://base-ui.com/react/components/number-field
- WCAG 2.1 relative luminance: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
- WCAG 2.1 contrast ratio: https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
- Electron PR #29318 (page can prevent the Alt menu toggle): https://github.com/electron/electron/pull/29318
- Excalidraw (tool lock): https://github.com/excalidraw/excalidraw
- tldraw `TLInstance.isToolLocked`: https://tldraw.dev/reference/editor/TLInstance
- MDN `Element.setPointerCapture`: https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture
- MDN `wheel` event: https://developer.mozilla.org/en-US/docs/Web/API/Element/wheel_event
- MDN `<option>`: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option

## Planning receipts

- **R-1 (2026-10-16).** [select-popup-probe.js](select-popup-probe.js), run with the worktree's Electron 42.9.3 (Chrome 148) on Windows. It opens a `<select>` styled like `capture-named-color`, whose seven options carry the `SWATCH_OPTIONS` styles, clicks it open, and captures the screen ([select-popup-probe.png](select-popup-probe.png)). The native popup paints every option with its own background and text colour. So `POPOVER_FALLBACK` is not built (D-16).
- **R-2 (2026-10-16).** [contrast-probe.py](contrast-probe.py), exit 0:

  | Colour | Hex | L | Pick | Ratio |
  |---|---|---|---|---|
  | red | `#FF0000` | 0.2126 | `#000000` | 5.25 |
  | orange | `#FFA500` | 0.4817 | `#000000` | 10.63 |
  | yellow | `#FFFF00` | 0.9278 | `#000000` | 19.56 |
  | green | `#008000` | 0.1544 | `#FFFFFF` | 5.14 |
  | blue | `#0000FF` | 0.0722 | `#FFFFFF` | 8.59 |
  | white | `#FFFFFF` | 1.0000 | `#000000` | 21.00 |
  | black | `#000000` | 0.0000 | `#FFFFFF` | 21.00 |

  The boundary is L = 0.1791, and no pick is below 4.5:1. White on red would be 4.00:1.
- **R-3 (2026-10-16).** `identity.py --selftest`, exit 0. Every bound mutation changes `tested_state` and makes `durable_evidence.evidence_problems` refuse the earlier full record. That covers the lockfiles, `capture-scrub.ts`, and `baseline-py-failed.txt`. Edits to the project artifacts leave it unchanged. Re-run after the round 1 corrections: it also refuses a set `ELECTRON_RENDERER_URL` (`RENDERER_PIN`).
- **R-4 (2026-10-16).** `red-check.py --selftest`, exit 0, 24 fixtures, 0 wrong (re-run after the round 1 corrections).
  - **Pass (9):**
    - a pytest assertion;
    - a Vitest unresolved `capture-scrub` module;
    - a Vitest unresolved `CaptureScrubField` component;
    - a Vitest `contrastText … is not a function` (Vite SSR);
    - a Vitest behaviour assertion;
    - a Playwright count assertion (`Expected: 1 / Received: 0`);
    - a Playwright `expect` failure;
    - an ANSI-coloured Vitest assertion;
    - a Vitest `Cannot find module '…/capture-scrub' imported from …` line.
  - **Refused (15):**
    - an Electron launch failure;
    - a locator timeout;
    - an ANSI-coloured locator timeout;
    - an unrelated `ImportError`;
    - an assertion beside an undeclared `normalizeHex … is not a function`;
    - an unrelated module imported by the new test file;
    - a misspelt name imported from a declared module;
    - an assertion beside an unrelated unresolved import;
    - an assertion beside an unclassified `TypeError`;
    - a declared name that is only a prefix of the missing name;
    - an assertion beside a Testing Library element miss;
    - a declared module that is only a prefix of the unresolved import;
    - a pytest collection error;
    - a run whose exit was 0;
    - a receipt with no `.exit` file.
- **R-5 (2026-10-16).** `session-gate.ps1` parses with 0 PowerShell parse errors. It was not run during planning, because it needs the execution baseline.
- **R-6 (2026-10-16, round 1 F5).** A scratch-repo fixture runs the `scope-paths` step of `session-gate.ps1` after `git mv .agent/roles/reviewer.md` into this plan folder. Default `git diff --name-only` lists only the destination. The step, which now uses `--no-renames -z`, lists `.agent/roles/reviewer.md` outside scope and exits 1. Receipt `C:/Temp/av-kit/s37-r6-scope-rename.txt`.

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract` (§4).
- **Targeted:** §3 after each production edit (blocking for its row).
- **Fresh full:** §4 in one pass after the last edit (row 8), from `WT`, in `pwsh`. It must pass; no partial, cached or reused receipt counts. Re-run all of §4 if any input changes after it (H1-6b).
- **Runtime (optional, non-blocking):** Mat's visual check (User Review Required item 8).
- **Input identity (`INPUT_IDENTITY`):** [identity.py](identity.py) prints the runtime identity and `tested_state`, which is HEAD plus one SHA-256. The hash covers:
  - the tracked diff and the untracked (not ignored) files of the whole work tree, except the project artifacts written after the gate. Those are this plan folder's `*.md`, `.agent/context/`, `docs/execution/reflections/`, `docs/execution/metrics.md`, `docs/build-plan/` and `docs/BUILD_PLAN.md`. So the lockfiles, `baseline-py-failed.txt` and this plan's scripts are all bound;
  - the runtime identity, observed live: the Python running it, `node --version`, the installed `electron` and `@playwright/test` versions, the `segoeui.ttf` SHA-256, `ELECTRON_RUN_AS_NODE` and `ELECTRON_RENDERER_URL` (`RENDERER_PIN`: a set value refuses with exit 2).

  `--state-only` computes the same value. The gate records the state before and after it runs (§4), and each handoff's final full `evidence.v1` record carries it. H1-6b re-derives it live with `identity.py --state-only`, so any bound change refuses the old record and forces H1-2 again.
- **Evidence:** each receipt's exit code and decisive lines, pasted as `evidence.v1` in the handoffs.
- **D9:** yes; MEU state updates go through `tools/meu_status.py` (H1-3).
