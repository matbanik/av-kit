---
project: "2026-11-10-gui-capture-crop-tool"
date: "2026-11-10"
source: ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md#session-60--gui-capture-crop-tool-meu-131--p2"
grouping_source: ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md"
meus: ["MEU-131"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: A crop tool on the Capture page (Session 60)

> **Project:** `2026-11-10-gui-capture-crop-tool`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Crop tool (`:1060-1077`, anchor `crop-tool`, MEU-131).
>
> **Source request.** Mat asked on 2026-11-08 for a crop feature on the Capture page that agents can use through the GUI, MCP and API, agent use first (`_inspiration/capture-crop/design.md`, design D-1 ruled by Mat: "New shot (copy); source untouched"). Session 59 shipped the endpoint (`POST /captures/{id}/crop`, MEU-130, `8f29046`). The grouping (D-400 to D-406) puts slice S4, the GUI tool, here. Done comes from 09's contract, not from Mat's words: each rule of §Crop tool holds, with a behaviour test per rule and an Electron proof of a real handle drag, Save as copy and the new shot selected.
> **Known issues:** none open for this MEU. `MCP-AUDIT-BASELINE-PENDING-CROP` stays open and isn't touched. `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` (D-507) is out of scope: an observation of it is recorded in the handoff and raised, never fixed here.
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review. Two questions are Mat's (§User Review Required): D-521, the live agent run, and D-522, the human look.

## Goal

**Goal anchor:** Session 60 adds a Crop tool to the Capture page. A Crop button opens a box over the whole image with 8 handles. The user drags a handle to resize, drags inside to move or drags outside to draw a new box; Shift keeps the ratio. Six aspect presets and a swap set the ratio, and X, Y, W and H fields set the box in original px. The outside is dimmed, a thirds grid shows while dragging, and the size reads out in original px. Enter, a double-click inside the box or Save as copy sends the box to Session 59's `POST /captures/{id}/crop`. The new shot is selected and named on the status line, and the source stays. Esc or Cancel leaves; Reset returns to the whole image. While the crop is open, other tools and keys do nothing, and Crop is disabled while marks are unsaved.

Four things are missing today:

1. **No crop in the GUI.** `CaptureTool` stops at `eraser` (`ui/src/renderer/src/features/capture/CaptureViewport.tsx:65`). An agent can crop through MCP, but a person can't.
2. **No crop geometry in the renderer.** `capture-transform.ts` has the 8 handles and `resizeBox` for marks (`:1-147`), but no minimum size, ratio lock, presets or field rules for a crop box.
3. **No renderer call for the endpoint.** `capture-commands.ts` has `flattenCapture` (`:137`) and no `cropCapture`, and the renderer has no type for the 201 body.
4. **The crop description has never met a live agent.** Session 59's AC-130.25 checks its markers, and D-494 carried a live run here. At plan time it turned out that Claude Code doesn't pass the `crop` paragraph to a model at all (§User Review Required, D-521).

The session ends when 09's §Crop tool holds with a behaviour test per rule, the session gate passes, D-404 is settled (D-508), D-494 is run or ruled (D-521), and MEU-131 is `approved`.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-10). No payload is oversized: CaptureViewport.tsx (1447 lines) and CapturePage.tsx (1918 lines) were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s60-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s60\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone (`git worktree list` shows only `P:/av-kit`, 2026-11-10).
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s60-plan-canonical-2026-11-10-gui-capture-crop-tool` and `s60-execution-2026-11-10-gui-capture-crop-tool`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290), and the `--review-state-only` receipt is rebuilt there.
  - Reviewer prompts name the ledger vocabulary up front: D-508 to D-523, AC-131.1 to AC-131.24, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json` and anything under `.agent/fleet/hub`, and write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). Each recheck asks for a `### New Findings` table and for bare words in its Recheck cells (`fixed`).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind (the D-521 run is one, and runs only on Mat's ruling), a model, runtime, FFmpeg or Python package download, the live MCP audit, `--update-baseline`, a tag, release or upload, or an `approved` verdict authored by the implementer. Capture stays local: no test or row uploads an image or reads one from the network. Unit tests build images in the renderer's test setup; the Electron proof answers from a seam; the D-521 run and the look use Pillow images under `C:/Temp/av-kit/s60`. Nothing touches the installed avkit MCP servers, Mat's inbox or YouTube.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-131 `gui-capture-crop-tool` | `.agent/context/handoffs/2026-11-10-gui-capture-crop-tool-MEU-131-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-10-gui-capture-crop-tool-plan-critical-review.md` and `.agent/context/handoffs/2026-11-10-gui-capture-crop-tool-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, `s60-anchors.txt` |
| WP-2 | Type-only names (row 1) | WP-1 | shared | `capture-crop.ts` stubs, `CaptureCropResult`, the `cropCapture` stub, `'crop'` in `CaptureTool` with its exhaustive cases, the Crop button that does nothing, an empty `CROP_BUTTONS`, the empty `CaptureCropBar` and `CaptureCropOverlay`, the moved pins |
| WP-3 | Geometry Red, then Green (rows 2, 3) | WP-2 | shared | `CROP_ROUND`, `CROP_MIN`, `CROP_HANDLES`, `CROP_MOVE`, `CROP_DRAW`, `CROP_RATIO`, `CROP_PRESETS`, `CROP_SWAP`, `CROP_FIELDS`, `CROP_NUDGE`; `row3-ui-src.json` |
| WP-4 | Page and Electron Red, then Green (rows 4, 5) | WP-3 | shared | `CROP_ENTRY`, `CROP_UNSAVED_GATE`, `CROP_POINTER`, `CROP_LOOK`, `CROP_BAR`, `CROP_COMMIT`, `CROP_CANCEL`, `CROP_MODAL`, `CROP_ERRORS`, `CROP_ELECTRON`, the test-id block |
| WP-5 | Human look (row 6, under D-522) | WP-4 | shared | `LOOK_LAUNCH`, `human-check.md` |
| WP-6 | Live agent run (row 7, under D-521) | WP-4 | shared | `D494_RUN`, `s60-d494-*` receipts |
| WP-7 | Records (row 8) | WP-6 | shared | Spec notes, MEU status, renders, grouping tracker |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | The handoff, review, reflection, Session 61's prompt |

The page Red and the Electron Red share row 4, as Session 43's did: an Electron Red written after the page Green would pass at once and prove nothing. Row 4 builds the row 3 renderer and refuses to run if any `ui/src` file differs from `row3-ui-src.json`, so both Reds run on the tree before the tool exists.

Split flag (grouping `:76`), read at row 4's start. Row 3 has then built the whole geometry, presets and fields included. If the session is past about half its context at that point, the bar's aspect select, swap and fields (AC-131.15, .16 and .24) move to Session 60b from this same plan and task, with no plan change: row 4 writes the other Reds, row 5 builds the tool without those controls, and 60b adds the three ACs with their own Red and Green. D-519 keeps MEU-132 out of this session.

## User Review Required

> [!IMPORTANT]
> **Two questions are Mat's.** Every other choice is recorded as autonomous in §Decision Log (D-508 to D-520, D-523), with its alternatives. The gate asks Mat to accept the plan, rule D-521 and D-522, set the execution budget, and override any autonomous choice. Only Mat's words start execution.
>
> **D-521: how is D-494's live agent run done?** (`governance-value`.) The run checks that a model reading only `avkit_capture`'s advertised description and schema can crop a named region of a test image into a new shot. **What the model reads (found at plan time).** Claude Code gives a model the server instructions, `avkit_capture`'s top-level description and the flattened input schema (the action enum, `x`, `y`, `width`, `height`, `unit`, `name`, with no per-action text). The `crop` paragraph Session 59 wrote (`CROP_TEXT`, `mcp-server/src/toolsets/capture.ts:52`) is served only in the tool's `_meta.action_descriptions` (`mcp-server/src/toolsets/registry.ts:599-610`), which Claude Code doesn't pass to the model. This was confirmed on this session's own `avkit_capture` tool schema, loaded without calling the server. So the run tests the surface a Claude Code agent really gets, which lacks `CROP_TEXT`. `d494-harness.ts describe` prints `_meta.action_descriptions.crop` under its own heading, and `d494-run.md` takes only the sections above it (`C:/Temp/av-kit/s60-plan-d494-describe.txt`). Whether to register this as an issue is a separate question at the plan gate, with a do-nothing option; nothing here changes the description or the registry. It runs against this work tree's MCP server (`mcp-server/dist/index.js`) and backend, with app data and an inbox under `C:/Temp/av-kit/s60/d494/root`, through Session 59's audit helpers (`mcp-server/scripts/audit/backend.ts` `spawnBackend`, `client.ts` `buildLaunch`). It never starts or calls the installed avkit MCP, never reads Mat's inbox and makes no YouTube request. It is **metered and networked**: the agent is a subagent, and its tokens go to Anthropic over the network. No image is sent: the harness refuses `image`, so the model never sees pixels.
> - **A (Recommended): Haiku 5.5 (`model: haiku`), one run.** The weakest current model is the strongest test of the description: if Haiku crops correctly from the text alone, a stronger model will too. Cost: one short subagent, about 50k to 150k tokens. Pass criteria are in `D494_RUN`; a failure is recorded with its receipt and briefed to Mat, and the description is not changed in this session without Mat's words.
> - **B: Sonnet 5.5 (`model: sonnet`), one run.** A pass shows the description works for the model most agents run, but proves less about a weak reader. Cost about two to four times A's.
> - **C, do nothing:** keep AC-130.25's marker check, record the run as carried in Session 61's prompt, and leave D-494 open. Nothing is metered; the description stays unproven against a live reader.
>
> **D-522: does Mat look at the tool before the execution review?** (`human-check`.) Row 6 runs after the Electron proof is Green and before H1-7.
> - **A (Recommended): Mat looks.** Row 6 builds a test inbox and app data under `C:/Temp/av-kit/s60/look` with Pillow images (a 1600×900 landscape and a 600×1000 portrait, the landscape with saved marks) and launches the dev app detached on it (`Start-Process`, `AVKIT_APP_DATA` set, `ELECTRON_RUN_AS_NODE` cleared). It records the process ids and later stops only those. Mat crops the marked shot three ways: with the handles, with a preset and with the number fields. Mat's words go in `human-check.md`. The tests check rules; only a person can judge how the handles feel, whether the dim reads, and whether the status line is enough of a "toast".
> - **B, do nothing:** review on the Electron proof alone. Row 6 writes `human-check.md` with `decision: not-run` and Mat's ruling, launches nothing, and the execution review is the only outside check.
> - **What Mat's "no" changes.** Each finding becomes a fix row before H1-7, with its own Red where it is a rule. A finding that changes 09's contract (for example a real toast instead of the status line, D-516) goes to Mat as a brief under S59 RULE-3, with a do-nothing option, and doesn't change an AC without Mat's words.
>
> **What the words in the contract mean here, and the limits they leave.**
> - **"Crop (C)".** The registry has no page-scoped letter entries (`commandRegistry` holds only Ctrl and F-key chords, D-508), so under 09's own clause the button ships alone, with the tooltip "Crop" and no `aria-keyshortcuts`, and C arrives with MEU-105. The handoff names this as the clause's own consequence, not a departure.
> - **"A toast names the new shot."** The Capture page has no toast; its status line already names a new shot the same way after a convert-on-apply (`CapturePage.tsx:1402`, `CONVERT_ON_APPLY`). The crop uses that line: `Saved crop as {display_name}.` (D-516). D-522's look is where Mat can say no.
> - **"Other tool letters are ignored."** No tool letter exists today, so the rule is kept as: while the crop is open, every key other than Enter, Esc, the arrows and X does nothing on the page, and the other tool buttons are disabled (D-515, D-518). MEU-105's letters then inherit the rule.
> - **"Shift keeps the aspect ratio."** Under a preset, the ratio is always kept and Shift changes nothing. Under Free, Shift keeps the box's ratio at the start of the drag (D-512).
> - **"In original px".** The fields, the readout and the POST body are whole original pixels; the box never holds a fraction (D-511). Zoom changes neither.
> - **The minimum box is 8 px a side**, the endpoint's own `CAPTURE_MIN_EDGE_PX` (`packages/core/src/avkit_core/domain/capture.py:27`), which `resolve_region` applies after clamping to every image, with no exception for a small one (`:190-194`). So Crop is disabled on a shot under 8 px on either side, and a ratio the image is too small to hold at 8 px is disabled, not bent (D-511, D-513). A box the tool allows is never refused by the endpoint for size.
>
> **The token estimate,** calibrated against Session 43 `capture-editor-repair` (plan 14.9M over 2 rounds, execution 21.0M) and Session 59 (plan 23.3M over 3 rounds; execution 12.8M over 2 rounds: round 1 8,336,600, round 2 4,475,811) and Session 58's execution (round 1 7,847,133, round 2 3,872,291). This session has one renderer MEU with a pure geometry module, a page state machine, two components, 24 ACs and an Electron proof, plus a human look and a live agent run. Expect 1 to 3 plan rounds (about 10M to 24M) and 2 to 3 execution rounds (about 12M to 25M). The plan loop opens with the default 10.5M. At the plan gate Mat sets the execution loop's budget, with a recheck at about half of round 1 (Session 58 RULE-4). The citable AC family is fixed when the plan loop opens: AC-131.
>
> **The gate, 2026-11-10.** Codex approved the plan at round 3 of 5 (round 1 9,708,681, round 2 6,561,859, round 3 4,528,306; Mat raised the plan loop to 50.5M and 5 rounds). Mat ruled through the Human Decision Protocol:
> - Execution starts, and H1-7 opens the execution loop with 20,000,000 tokens and 3 rounds: "A: Start, 20M, 3 rounds (Recommended)".
> - D-521 A and D-522 A, recorded in §Decision Log.
> - At closeout, register a known issue: `_meta.action_descriptions`, where each MCP action's text lives, isn't shown to a model by Claude Code (`C:/Temp/av-kit/s60-plan-d494-describe.txt`). No fix is planned. "A: Register it (Recommended)".

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `CROP_ROUND` | `roundHalfUp(v) = Math.floor(v + 0.5)` in `capture-crop.ts`, the one rounding of the tool: 2.5 → 3, 3.5 → 4, −2.5 → −2, 2.4999 → 2. Every box the module returns has integer `x`, `y`, `width` and `height` (S59 RULE-4). |
| `CROP_MIN` | `CROP_MIN_PX = 8`, equal to `CAPTURE_MIN_EDGE_PX` (`capture.py:27`), which `resolve_region` applies after clamping to every image (`:190-194`). `cropEligible(imageW, imageH)` is `imageW ≥ 8 && imageH ≥ 8`; the page calls the other functions only for an eligible image. A crop box is `{x, y, width, height}` in whole original px with `0 ≤ x`, `0 ≤ y`, `x + width ≤ imageW`, `y + height ≤ imageH`, `width ≥ 8` and `height ≥ 8`, so it passes `resolve_region`'s px rules (`:159-194`) unclamped. `clampCrop(box, imageW, imageH)` returns the nearest such box: it rounds, cuts the size to the image, raises it to the minimum, then shifts the origin inside. |
| `CROP_HANDLES` | `resizeCrop(start, handle, dx, dy, image, ratio)` with `HandleId` from `capture-transform.ts`: a handle moves only its own edges by the rounded delta, the opposite edges stay fixed, and an edge stops at the minimum from the opposite edge and at the image edge. It never flips. |
| `CROP_MOVE` | `moveCrop(start, dx, dy, image)` keeps the size and clamps the origin inside the image. |
| `CROP_DRAW` | `drawCrop(anchor, point, image, ratio)` builds the box between two image points in any direction, normalised and clamped. A drag shorter than 8 px on an axis grows to 8 from the anchor in the drag's direction, kept inside. A down and up at the same point returns `null`, and the old box stays. With a ratio, the box is `ratioBox(s, r)` from the anchor in the drag's direction, `s` taken as a corner drag takes it and clamped to `[8, the largest s whose box fits from the anchor]`; when even `ratioMinBox(r)` doesn't fit from the anchor, the box is shifted inside. |
| `CROP_RATIO` | `ratio` is `null` (Free) or `r = w / h > 0`. Every ratio box is built from one whole driving side `s`, the height when `r ≥ 1` and the width otherwise: `ratioBox(s, r)` is `{width: roundHalfUp(s * r), height: s}` when `r ≥ 1`, otherwise `{width: s, height: roundHalfUp(s / r)}`, so its other side is never shorter than `s`. `fitsRatio(box, r)` is exact, with no tolerance: `box.width === roundHalfUp(box.height * r)` when `r ≥ 1`, otherwise `box.height === roundHalfUp(box.width / r)`. It is true exactly when the box is the `ratioBox` of its driving side, and the module builds and checks with the same expression, so the two can't disagree after rounding or in floating point. `roundHalfUp` never decreases, so on a `W × H` image the driving sides whose box fits form one range `[8, sMax]`, where `sMax` is the largest whole `s` up to the driving limit (`H` when `r ≥ 1`, else `W`) whose `ratioBox(s, r)` has its other side within the image. `ratioMinBox(r)` is `ratioBox(8, r)`; `ratioLargestBox(r, W, H)` is `ratioBox(sMax, r)`; `ratioFeasible(r, W, H)` is `sMax ≥ 8`. That is the same as `ratioMinBox(r)` fitting inside the image, and the same as `ratioLargestBox` having both sides at least 8. With a ratio, every box the module returns is a `ratioBox`. A corner drag keeps the opposite corner fixed and takes `s` from the axis the pointer moved further, in box-relative terms: the driving side directly, or the other side `v` as `roundHalfUp(v / r)` when `r ≥ 1` and `roundHalfUp(v * r)` when `r < 1`. An edge drag takes `s` from its own side the same way, and centres the other side on the box's centre, rounded with `CROP_ROUND` and shifted inside across. `s` is clamped to `[8, the largest s whose box fits the space the drag may use]`, so the box stops at the image edge and at `ratioMinBox(r)`; the start box under a ratio is itself a `ratioBox` inside that space, so the range is never empty. Under Free, Shift sets `ratio` to the start box's `width / height` for that drag; the start box is then the `ratioBox` of its own driving side, at least 8, so that ratio is feasible. An infeasible ratio is never active (`CROP_PRESETS`, `CROP_SWAP`). |
| `CROP_PRESETS` | `ASPECT_PRESETS`, in order: `free` "Free", `original` "Original" (`imageW / imageH`), `square` "Square" (1), `16:9`, `4:3`, `3:2`. `presetFeasible(preset, image, swapped)` is true for Free and otherwise `ratioFeasible(presetRatio(preset, image, swapped), imageW, imageH)`; Original unswapped is always feasible. `applyPreset(box, preset, image, swapped)` returns the box unchanged for Free and `null` for an infeasible preset, so the box and the aspect stay as they were; otherwise `ratioLargestBox` of that ratio, centred on the current box's centre with `CROP_ROUND` and shifted inside, so it fits the ratio exactly. The bar disables an infeasible preset's option (D-513). |
| `CROP_SWAP` | `swapped` flips a preset's ratio to `1 / r`, and the box is refitted with `applyPreset`. Square is unchanged. Under Free, the swap exchanges width and height about the box's centre, then clamps with `CROP_MIN`. The swap button and X do the same. When the swapped preset isn't `presetFeasible` (16:9 on a 400×10 shot; Original on a 3840×8 shot), `swapCrop` returns `null`, the swap button is disabled with the reason `Too small to swap this ratio`, and X does nothing. |
| `CROP_FIELDS` | `applyField(box, field, text, image, ratio)`: the text is trimmed and parsed as a decimal number; empty, non-numeric, `NaN` or infinite text returns `null` and the field reverts to the box. A number rounds with `CROP_ROUND`; a negative becomes 0. X or Y keeps the size and clamps the origin. W or H keeps the origin, is cut to the image from the origin and raised to the minimum; with a ratio, the typed side gives the driving side `s` as a corner drag does, the box is `ratioBox(s, r)`, and `s` is clamped to `[8, the largest s whose box fits from the origin]`, so both sides shrink to fit and never go below `ratioMinBox`; when even `ratioMinBox` doesn't fit from the origin, the origin shifts inside. |
| `CROP_NUDGE` | `nudgeCrop(box, dx, dy, image)` is `moveCrop` by whole pixels. On the surface, an arrow moves the box 1 px and Shift+arrow 10 px. In a field, ArrowUp and ArrowDown step that field's value by 1, or 10 with Shift, through `applyField`. |
| `CROP_ENTRY` | `CaptureTool` gains `'crop'`. `TOOLBAR_BUTTONS['capture-tool-crop'] = { icon: Crop, name: 'Crop' }` and `TOOL_BUTTON_IDS.crop = 'capture-tool-crop'`. The button is a `ToolbarIconButton` with no `shortcut`, placed straight after the lock and before the History group, outside the Annotation tool group, so AC-87.2 holds. Clicking it with a clean shot opens the crop: `tool` becomes `'crop'`, the view becomes Original, and the box is the whole image with the aspect Free. Clicking it again cancels. `strokeApplies('crop')` is false; `optionGroups` checks `'crop'` first, before its pixelate and eraser rules, so `optionGroups('crop', any selection)` is `[]`; and `createDrawnMark('crop', …)` returns `null`. |
| `CROP_UNSAVED_GATE` | With no shot, Crop is disabled with `NO_SHOT_HINT`. On a shot that isn't `cropEligible` (`selected.width` or `selected.height` under 8; the page reads them at `CapturePage.tsx:672`), it is disabled with the reason `Too small to crop: each side needs 8 px`. While `dirty` (`CapturePage.tsx:350`) is true, it is disabled with the reason `Save or discard your marks first`. The reasons are checked in that order, and none opens the crop. |
| `CROP_POINTER` | While the crop is open, the surface's pointer events go to the crop and never to marks. A `down` on a handle (`hitResizeHandle` with `RESIZE_HIT_CSS / view.s`) starts `CROP_HANDLES`; inside the box starts `CROP_MOVE`; outside starts `CROP_DRAW`. `SurfacePointer` gains `shiftKey`, read from the DOM event on every phase. Each `move` recomputes from the box at `down`, so a drag is one path with no drift. `up` and `cancel` end it. The cursor follows `cursorForHandle`, `move` inside the box and `crosshair` outside. |
| `CROP_LOOK` | `CaptureCropOverlay` draws, in image px under the viewport's `viewBox`: a dim path over the whole image with the box cut out (`fill-rule="evenodd"`, `fill="var(--color-bg)"` at `opacity` 0.6), the box outline (`var(--color-accent)`, `vectorEffect="non-scaling-stroke"`), the thirds lines only while a drag is active, and the 8 handles at `boxHandlePoints`, sized `RESIZE_HANDLE_CSS / view.s`. It has `pointer-events-none`. Saved marks show beneath the dim and can't be selected. |
| `CROP_BAR` | While the crop is open, `CaptureCropBar` replaces the option groups in `capture-chrome-options`: a `role="group"` named "Crop" with an Aspect `SelectInput` (G30), the swap button (`ToolbarIconButton`, `CROP_BUTTONS['capture-crop-swap'] = { icon: ArrowLeftRight, name: 'Swap portrait and landscape' }`, `shortcut="X"`), labelled X, Y, W and H inputs (`inputMode="numeric"`), an `<output>` that reads `{W} × {H} px`, Reset and Cancel (`Button` `ghost` `sm`) and Save as copy (`Button` `primary` `sm`). A field shows the box while it isn't being edited; Enter or blur applies it with `CROP_FIELDS`; Esc in a field reverts the field only. `CROP_BUTTONS` lives in `capture-toolbar.ts` beside `ACTION_BUTTONS`, as its own record apart from `TOOLBAR_BUTTONS`, because AC-80.8 expects every `TOOLBAR_BUTTONS` entry on the page. |
| `CROP_COMMIT` | Enter (focus outside a crop field), a `dblclick` whose image point is inside the box, or Save as copy calls `cropCapture(id, box)`: `POST /captures/${encodeURIComponent(id)}/crop` with body `{x, y, width, height}`, the box's integers, then `invalidateQueries(['captures'])`. On 201 the crop closes, the prior tool returns, `selectedId` becomes `item.id`, and the status line reads `Saved crop as {item.display_name}.` for that shot. The source stays in the filmstrip. A second commit while one is in flight sends nothing. |
| `CROP_ERRORS` | While the request is in flight, Save as copy is disabled with `aria-busy="true"` and the status line reads `Cropping…` (G35 T2). On an error the crop stays open with its box, the button is enabled again, and the status line shows the error's message through the page's `run` path (`CapturePage.tsx:1269`), which names no path. |
| `CROP_CANCEL` | Esc (focus outside a crop field), Cancel or a second click on Crop closes the crop with no request, and the prior tool returns. Reset sets the box to the whole image and the aspect to Free, swap off, and leaves the crop open. Selecting another shot, switching to Annotated, or the shot leaving the list cancels the crop. |
| `CROP_MODAL` | While the crop is open, the page's key handler takes Enter, Esc, the arrows and X for the crop, and does nothing else: letters, Delete, Backspace, the history chords and the text-edit Enter don't reach marks. The tool buttons, Undo, Redo, the lock and the Annotated view button are disabled with the reason `Finish or cancel the crop first`. A key in a crop field stays in the field. |
| `CROP_ELECTRON` | In `ui/tests/e2e/capture-inbox.test.ts`, a crop seam answers `POST …/crop` with 201 and the new item, and adds it to the list it serves. Playwright drags the SE handle with `page.mouse` (down, several moves, up) and clicks Save as copy. The POST body equals the dragged box within ±1 px on each value; the new thumb has `aria-current="true"`; the status line names it; the source thumb is still listed. A second test drives the bar: Square, swap, a W entry, Reset, Cancel and Esc. |
| `D494_RUN` | Under D-521 A or B. Pass means all of: at least one `crop` call succeeded (in `ledger.jsonl`, not refused, not `isError`, and its result JSON has an `item`); no `remove`, `flatten`, `revert` or `image` call went through (the harness refuses them without calling; a refused attempt is recorded and listed, not counted against the run); the last successful crop's `source_id` is chart-source's id, which `d494-harness.ts seed` writes to `seed/source-id.txt` (a crop of an earlier crop is measured in another frame, so it fails), and its `applied` box has an IoU of at least 0.9 with `seed/panel.json` `panel_px`; `inbox/chart-source.png` is byte-identical to `seed/chart-source.png`; `inbox/chart.png` exists and is that crop's `item.original_path`; the agent's saved report names that crop's `item.id`. `d494-check.py` decides it from the ledger, the files and the report. |
| `LOOK_LAUNCH` | Under D-522 A. `look-seed.py` builds `C:/Temp/av-kit/s60/look/app-data` through `build_services`, `create_app` and a `TestClient`: a `PUT /api/v1/settings/capture` with `inbox_dir` `C:/Temp/av-kit/s60/look/inbox`, the two Pillow images, `GET /captures` to register them, and `POST /captures/{id}/annotate` with a rect, an arrow and a text on the landscape. The app starts detached with `AVKIT_APP_DATA` pointing there, and `dev-app-procs.py` records and later stops only its own processes. |
| `NO_RAW_CONSOLE` | No new log line is added. A crop error reaches `logRenderer('ERROR', message)` through `run`, with the endpoint's fixed messages, which name no path (Session 59 AC-130.22). |

### Crop geometry (D-511 to D-514)

`capture-crop.ts` is pure, with no React or DOM. It imports `HandleId`, `boxHandlePoints`, `hitResizeHandle`, `cursorForHandle`, `RESIZE_HANDLE_CSS` and `RESIZE_HIT_CSS` from `capture-transform.ts` and doesn't change it, so the mark handles keep their tests (MEU-100). It exports `CropBox`, `AspectPresetId`, `ASPECT_PRESETS`, `CROP_MIN_PX`, `roundHalfUp`, `cropEligible`, `clampCrop`, `resizeCrop`, `moveCrop`, `drawCrop`, `fitsRatio`, `ratioBox`, `ratioMinBox`, `ratioLargestBox`, `ratioFeasible`, `presetRatio`, `presetFeasible`, `applyPreset`, `swapCrop`, `applyField`, `nudgeCrop` and `wholeImage`. `CROP_BUTTONS` holds lucide icon components, so it lives in `capture-toolbar.ts` with the other button records and keeps this module free of React.

`resizeBox` in `capture-transform.ts` isn't reused for the crop: it flips through zero and has no minimum or ratio, both right for marks and wrong for a crop box.

### The page (D-509, D-510, D-515 to D-518)

- **State.** `CapturePage` holds `crop: { box: CropBox; aspect: AspectPresetId; swapped: boolean; prior: CaptureTool; drag: CropDrag | null; busy: boolean } | null`. `tool === 'crop'` exactly when `crop !== null`.
- **Viewport props.** `CaptureViewport` gains `crop?: { box: CropBox; dragging: boolean } | null`, `cropBar?: ReactNode`, `cropReason?: string` (the disabled reason the other tools carry) and `cropDisabledReason?: string` (Crop's own). It renders `CaptureCropOverlay` above the handle layer and `cropBar` in place of the option groups.
- **Callers of `CaptureTool` (S55 RULE-1).** `capture-toolbar.ts:78` (`TOOL_BUTTON_IDS`), `:96` (`strokeApplies`), `:118` (`optionGroups`); `CapturePage.tsx:198` (`createDrawnMark`), `:277` (state), `:545` (`chooseTool`), `:619` (`commitSelection`); `CaptureViewport.tsx:109`, `:126` (props); `ui/tests/unit/capture-toolbar.test.ts:24`, `:37`. Row 1 greps for every `CaptureTool` use again and lists any other.

### Pins that move

| Pin | Where | From → to | Row |
|---|---|---|---|
| The tool list | `ui/tests/unit/capture-toolbar.test.ts:24` `TOOLS` | gains `'crop'` | 1 |
| AC-87.1 negative | `capture-toolbar.test.ts:146-148`, "exactly the seven tools" | eight, with `'crop'` | 1 |
| No-shot ids | `ui/tests/unit/icon-hints.test.ts:48-58` `NO_SHOT_IDS` | gains `capture-tool-crop` | 1 |
| AC-80.8 title | `icon-hints.test.ts:314`, "the 13 Capture toolbar buttons" | 14 | 1 |
| AC-65.1 oracle | `capture-toolbar.test.ts:37-52` `expectedGroups`, and the color invariant at `:94-104` | `expectedGroups` returns `[]` for `'crop'` before its pixelate rule; the invariant's `regionCase` counts `tool === 'crop'` as having no color. Every other tool's expectation is unchanged | 1 |
| AC-90.9 selected pixelate | `capture-toolbar.test.ts:160-162` | the loop runs over `TOOLS` without `'crop'`, and a new line asserts `optionGroups('crop', MARKS.pixelate)` is `[]` | 1 |
| Test ids | `ui/tests/e2e/test-ids.ts`, after the MEU-115 block (`:479-480`) | a `// MEU-131 Capture crop tool (additive IDs).` block | 4 |

The first six move in row 1, because row 1 adds `'crop'` to `CaptureTool` and `TOOLS`, the `optionGroups` case and the `TOOLBAR_BUTTONS` entry, and renders the Crop button, disabled with `NO_SHOT_HINT` when no shot is selected; the old pins would fail on that row's own check. Row 1 greps the neighbours of each pin again (S59 RULE-1): every literal `'eraser'`-ended tool list, every count of tools or toolbar buttons, every `Object.keys(TOOL_BUTTON_IDS)` and every loop over `TOOLS` that states an option group in `ui/tests`. The AC-65.1 and AC-90.9 rows keep the guards independent restatements: they add crop's leading rule from `CROP_ENTRY` and change no other tool's expectation. The AC-91.8 loop over `TOOLS` (`:178`) already expects `[]`, which crop gives (plan review round 1 F2).

### Where values go (Session 50 RULE-1, Session 53 RULE-1)

- **The box** is four integers. It goes into the fields, the readout and the POST body. It is never logged.
- **The shot id** goes into the URL through `encodeURIComponent` (S59 RULE-2) and nowhere else.
- **`display_name`** is the new shot's own name, from the endpoint's `CROP_NAME`. It goes on the status line, as a convert-on-apply's does.
- **An error message** is the endpoint's fixed text. It goes to the status line and `logRenderer`, as every capture error does.
- **The D-521 ledger** holds the tool's arguments and results under `C:/Temp/av-kit/s60/d494`, which hold only test paths.

### Spec text (D3)

| File | Lines at `8f29046` | Change |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | `:1068` (Entry) | No change to the rule; a note after the table says the button ships alone under the clause, with C in MEU-105 (D-508) |
| | after `:1077` | A Delivered note naming the mechanism ids, the ACs, the status line as the toast (D-516), the Free/Shift rule (D-512), the 8 px minimum (D-511) and this plan folder |

Row 8 re-reads each anchor before it writes (Session 51 RULE-3) and cites the lines as they read then. `09` is CRLF.

### MEU-131 `gui-capture-crop-tool`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Crop field text → box | `capture-crop.ts` `applyField` | `CROP_FIELDS` | — |
| Pointer → box | `capture-crop.ts` | `CROP_HANDLES`, `CROP_MOVE`, `CROP_DRAW`, `CROP_RATIO`, `CROP_MIN` | — |
| Box → `POST /captures/{id}/crop` body | `capture-commands.ts` `cropCapture` | four integers inside the image, each side ≥ 8 (`CAPTURE_MIN_EDGE_PX`), sent only for a `cropEligible` shot; `unit` and `name` not sent | The endpoint's `CaptureCropIn` is `extra="forbid"`; the renderer sends only the four keys |
| 201 body → renderer | `capture-commands.ts` `CaptureCropResult` | Session 59's `CaptureCropOut`; the renderer reads `item` only | Unread keys are ignored |

#### Acceptance Criteria

Vitest titles start `AC-131.<n>`. AC-131.1 to .10 go in the new `ui/tests/unit/capture-crop.test.ts` (LF). AC-131.11 to .22 go in the new `ui/tests/unit/capture-crop-tool.behavior.test.ts` (LF), whose harness is copied from `capture-page.behavior.test.ts:1-190` with a 400×200 shot and a stubbed `fetch` that records each request; no image leaves the test. AC-131.23 and .24 go in `ui/tests/e2e/capture-inbox.test.ts`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-131.1 | unit | `CROP_ROUND`: `roundHalfUp` of 2.5, 3.5, −2.5, −3.5, 2.4999 and 2.5001 is 3, 4, −2, −3, 2 and 3, a half case each way (S59 RULE-4); `clampCrop` of a box with fractional values returns integers | Inferred: D-511 | Yes: Red, the stub returns its input |
| AC-131.2 | unit | `CROP_MIN`: `cropEligible` is false for 5×300, 300×5 and 7×7 and true for 8×8; on 400×200, a box past each edge clamps inside; a 3×3 box grows to 8×8 and stays inside at a corner. A sweep over the shots 8×8, 9×17, 17×9, 400×200, 400×10, 600×1000, 1201×799, 380×608 and 3840×8 passes every box from `clampCrop`, `resizeCrop` (all 8 handles, Free and each feasible ratio), `moveCrop`, `drawCrop`, `applyPreset` and `swapCrop` (each feasible preset, both ways) and `applyField` to `endpointAccepts`, the test's restatement of `resolve_region`'s px rules (`capture.py:159-194`: whole numbers, `x` and `y` at least 0, the start inside, each edge at least 8 after clamping) with the box inside the image, so `clamped` would be false; each must pass | Local Canon: `resolve_region` and `CAPTURE_MIN_EDGE_PX`; D-511 | Yes: Red, the stub |
| AC-131.3 | unit | `CROP_HANDLES`, over all 8 handles on a 100×80 box at (50, 40) in 400×200: each moves only its edges by the delta; dragging `e` left by 200 stops at width 8, `nw` past the image corner stops at (0, 0); no case flips | Local Canon: 09 Box; D-511 | Yes: Red, the stub |
| AC-131.4 | unit | `CROP_MOVE`: a move keeps the size; a move past each edge stops at it | Local Canon: 09 Box | Yes: Red, the stub |
| AC-131.5 | unit | `CROP_DRAW`: drags right-down, left-up, right-up and left-down give the same normalised box; a 3 px drag grows to 8 toward the drag; a same-point down and up returns `null` | Local Canon: 09 Box; D-511 | Yes: Red, the stub |
| AC-131.6 | unit | `CROP_RATIO`: under 16:9, an `se` drag mostly right, one mostly down, an `e` drag and an `n` drag each give a box that `fitsRatio`, inside the image, with the edge drag centred; under Free with Shift, an `se` drag keeps the start ratio within `fitsRatio`; at the image edge the box stops and still fits; under 16:9 on 400×10 an `n` drag downward stops at `ratioMinBox`, 14×8; `fitsRatio` is exact: under 16:9 a 16×9 box fits and a 17×9 box doesn't, and `ratioBox(9, 16 / 9)` is 16×9; under swapped Original on 380×608 (`r = 1.6`) `ratioLargestBox` is 379×237 and fits; every box the AC-131.2 sweep gets from `resizeCrop`, `drawCrop` and `applyField` under a ratio `fitsRatio` | Local Canon: 09 Box; D-512 | Yes: Red, the stub |
| AC-131.7 | unit | `CROP_PRESETS`: the ids and labels in order; Original on 400×200 is 2; Square from the whole 400×200 image is 200×200 at (100, 0); 16:9 from a small box near the right edge is the largest 16:9 box inside, shifted in; Free returns the box; on 8×8, `presetFeasible` is false for 16:9, 4:3 and 3:2 both ways and true for Free, Original and Square, and `applyPreset` returns `null` for the three; on 400×10, 4:3 swapped is infeasible: `ratioMinBox` is 8×11 and `ratioLargestBox` is 7×9; on every sweep shot of AC-131.2 and every preset ratio both ways, `ratioFeasible` agrees with `ratioMinBox` fitting inside the image and with `ratioLargestBox` having both sides at least 8, `ratioLargestBox` lies inside the image and `fitsRatio`, and each feasible preset's `applyPreset` box `fitsRatio` with both sides at least 8 | Local Canon: 09 Aspect; D-513 | Yes: Red, the stub |
| AC-131.8 | unit | `CROP_SWAP`: 16:9 swapped on 400×200 fits 9:16; Square swapped is unchanged; under Free a 120×40 box at (100, 80) becomes 40×120 about its centre, then clamps; 16:9 swapped on 400×10 and Original swapped on 3840×8 are infeasible, and `swapCrop` returns `null` for each | Local Canon: 09 Aspect; D-513 | Yes: Red, the stub |
| AC-131.9 | unit | `CROP_FIELDS`: `X` "350" on a 100-wide box clamps to 300; `W` "500" from x 100 cuts to 300; `W` "3" grows to 8; `W` "2.5" is 3 and "2.4" is 2, then the minimum; "-5" is 0; "", "abc", "NaN" and "1e999" return `null`; under Square, `W` "150" sets H 150, and a W that would push H past the image shrinks both | Local Canon: 09 Numbers; D-514 | Yes: Red, the stub |
| AC-131.10 | unit | `CROP_NUDGE`: 1 and 10 px each way; at an edge the box stops | Local Canon: 09 Numbers | Yes: Red, the stub |
| AC-131.11 | unit (page) | `CROP_ENTRY`: the Crop button sits straight after the lock and before the History group, outside the Annotation tool group; its hint is `Crop` and it has no `aria-keyshortcuts`; clicking it sets `aria-pressed="true"`, shows the crop bar in place of the options with X 0, Y 0, W 400, H 200 and Free, and switches the view to Original; with no shot it is disabled with `Select a shot first` | Local Canon: 09 Entry; D-508, D-509 | Yes: Red, the stub button opens nothing |
| AC-131.12 | unit (page) | `CROP_UNSAVED_GATE`: after drawing a box mark, Crop is disabled with `Save or discard your marks first` and a click opens nothing; after Save it opens; after Undo back to the saved marks it opens; on a 5×300 shot Crop is disabled with `Too small to crop: each side needs 8 px` and a click opens nothing | Local Canon: 09 Unsaved marks | Yes: Red, Crop is enabled |
| AC-131.13 | unit (page) | `CROP_POINTER`, at zoom 1 and at a 0.5 view scale: an `se` handle drag, an inside drag, an outside drag and a Shift `se` drag change the fields to the expected image-px boxes; no mark is added, selected or moved | Local Canon: 09 Box; D-510 | Yes: Red, the fields stay 0, 0, 400, 200 |
| AC-131.14 | unit (page) | `CROP_LOOK`: the overlay's dim path has `fill-rule="evenodd"` and holds the box; the thirds group is absent at rest, present during a drag and gone after `up`; the readout reads `400 × 200 px`, and the same after zooming in and out | Local Canon: 09 Look | Yes: Red, no overlay |
| AC-131.15 | unit (page) | `CROP_BAR` aspect: the select lists Free, Original, Square, 16:9, 4:3 and 3:2 in order; Square gives 200×200 at (100, 0); 16:9 then the swap button gives a 9:16 box; X on the surface swaps back; the swap hint reads `Swap portrait and landscape (X)`; on an 8×8 shot the 16:9, 4:3 and 3:2 options are disabled; on a 400×10 shot under 16:9 the swap is disabled with `Too small to swap this ratio` and X changes nothing | Local Canon: 09 Aspect | Yes: Red, the select is empty |
| AC-131.16 | unit (page) | `CROP_BAR` fields: typing 150 in W and Enter applies it; "abc" and Enter reverts the field; Esc in a field reverts the field and keeps the crop open; ArrowUp in W adds 1 and Shift+ArrowUp 10; an arrow on the surface moves X by 1 and Shift+arrow by 10 | Local Canon: 09 Numbers; D-514 | Yes: Red, the fields don't change the box |
| AC-131.17 | unit (page) | `CROP_COMMIT` by Save as copy: one `POST` to `/api/v1/captures/{encoded id}/crop` (an id with a space is encoded) with exactly `{x, y, width, height}` as integers; on 201 the new item's thumb has `aria-current="true"`, the status line reads `Saved crop as {display_name}.`, the source thumb is still listed, the crop bar is gone and the prior tool is pressed | Local Canon: 09 Commit; D-516 | Yes: Red, the stub sends nothing |
| AC-131.18 | unit (page) | `CROP_COMMIT` by Enter and by a double-click inside the box each send one POST; a double-click outside the box sends none; Enter twice while the first is pending sends one | Local Canon: 09 Commit | Yes: Red, no POST |
| AC-131.19 | unit (page) | `CROP_ERRORS`: while a POST is pending, Save as copy is disabled with `aria-busy="true"` and the status line reads `Cropping…`; a 409 and a 422 each leave the crop open with its box and show the error's message; Save as copy is enabled again | Local Canon: G35; D-517 | Yes: Red, the crop closes |
| AC-131.20 | unit (page) | `CROP_CANCEL`: Esc, Cancel and a second Crop click each close with no request and restore the prior tool; Reset after a Square and a drag returns 0, 0, 400, 200 with Free and keeps the crop open; selecting another shot and choosing Annotated each cancel | Local Canon: 09 Cancel; D-510 | Yes: Red, the crop stays open |
| AC-131.21 | unit (page) | `CROP_MODAL`: with a saved mark and the crop open, `a`, `b`, Delete, Backspace, Ctrl+Z and Ctrl+Y change neither the marks nor the box; the tool buttons, Undo, Redo, the lock and Annotated are disabled with `Finish or cancel the crop first` | Local Canon: 09 Modal; D-515, D-518 | Yes: Red, Ctrl+Z removes the mark |
| AC-131.22 | unit | The registries: `TOOL_BUTTON_IDS.crop` is `capture-tool-crop`; `TOOLBAR_BUTTONS['capture-tool-crop']` is `{ icon: Crop, name: 'Crop' }`; `optionGroups('crop', …)` is `[]` with no selection and with each selected mark kind, the pixelate and the eraser included; `CROP_BUTTONS['capture-crop-swap']` is `{ icon: ArrowLeftRight, name: 'Swap portrait and landscape' }`, and `CROP_BUTTONS` is disjoint from `TOOLBAR_BUTTONS` and `ACTION_BUTTONS` | Local Canon: 09 Entry; D-523 | Yes: Red, `CROP_BUTTONS` is empty |
| AC-131.23 | e2e (Electron) | `CROP_ELECTRON`: a real `se` handle drag with `page.mouse` and Save as copy; the POST body equals the dragged box within ±1 px per value; the new thumb has `aria-current="true"`; the status line names it; the source is listed | Local Canon: 09 Tests | Yes: Red, the crop bar isn't visible after the Crop click |
| AC-131.24 | e2e (Electron) | The bar's controls in the real app (§4A E2): Square, swap, a W entry with Enter, Reset, Cancel, then Crop and Esc; each changes the fields as AC-131.15 to .20 say, and no POST is sent | Local Canon: 09 Tests; §4A E2 | Yes: Red, the crop bar isn't visible after the Crop click |

Guards that run unchanged in rows 3 and 5: AC-87.x, AC-100.x (mark handles), AC-65.x, AC-80.x apart from the moved title and set, AC-81.13, AC-51.6, AC-39.x and the rest of `capture-page.behavior.test.ts` and `capture-inbox.test.ts`.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Entry and C | Local Canon, by its own clause | 09 Entry; D-508 |
| Button place | Inferred | D-509 |
| Box gestures | Local Canon, detailed | 09 Box; D-510, D-511 |
| Minimum and rounding | Inferred, flagged | D-511 (Session 58's 8 px) |
| Shift and presets | Local Canon, detailed | 09 Box, Aspect; D-512, D-513 |
| Fields and nudges | Local Canon, detailed | 09 Numbers; D-514 |
| Modal keys | Local Canon, adapted | 09 Modal; D-515 |
| Toast as the status line | Inferred, flagged | D-516 |
| Errors and in flight | Local Canon | G35; D-517 |
| Other tools while open | Inferred | D-518 |
| Electron proof by seam | Local Canon | D-520 |
| Live agent run | Human | D-521 |
| Human look | Human | D-522 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-crop.ts` | New | `CROP_ROUND` to `CROP_NUDGE` |
| `ui/src/renderer/src/features/capture/CaptureCropBar.tsx` | New | `CROP_BAR` |
| `ui/src/renderer/src/features/capture/CaptureCropOverlay.tsx` | New | `CROP_LOOK` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | Modify | `'crop'`, `shiftKey`, the Crop button, the overlay, the bar slot, the disabled reasons |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | Modify | The crop state, pointer and key routing, commit, cancel |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | Modify | The Crop entry, `TOOL_BUTTON_IDS`, `strokeApplies`, `optionGroups`, `CROP_BUTTONS` |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | Modify | `cropCapture`, `CaptureCropResult` |
| `ui/tests/unit/capture-crop.test.ts` | New | AC-131.1 to .10 |
| `ui/tests/unit/capture-crop-tool.behavior.test.ts` | New | AC-131.11 to .22 |
| `ui/tests/unit/capture-toolbar.test.ts`, `ui/tests/unit/icon-hints.test.ts` | Modify | §Pins that move |
| `ui/tests/e2e/capture-inbox.test.ts` | Modify | AC-131.23, .24, the crop seam |
| `ui/tests/e2e/test-ids.ts` | Modify | The additive block |
| `docs/build-plan/09-screenshot-capture.md` | Modify | §Spec text |

Line endings at `8f29046` (`C:/Temp/av-kit/s60-plan-probes.txt`): CRLF are `CaptureViewport.tsx`, `CapturePage.tsx`, `capture-toolbar.ts`, `capture-commands.ts`, `capture-transform.ts` (read only), `test-ids.ts`, `capture-toolbar.test.ts`, `icon-hints.test.ts`, `09` and the grouping. LF are `capture-inbox.test.ts`, `meu-status.yaml`, `docs/BUILD_PLAN.md` and `meu-registry.md`. Row 0 measures every file again with Python bytes, and every row writes with `newline=""` or by byte replacement. New files are LF.

### Project files

- `docs/execution/plans/2026-11-10-gui-capture-crop-tool/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `row3-ui-src.json`, `red-check.py`, `identity.py`, `session-gate.ps1`, `hotkey-free.py`, `dev-app-procs.py`, `look-seed.py`, `look-launch.ps1`, `look-check.py`, `human-check.md`, `d494-seed.py`, `d494-harness.ts`, `d494-check.py`, `d494-run.md`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, and the grouping tracker row (`:110`).
- `.agent/context/handoffs/2026-11-10-gui-capture-crop-tool-*.md`, `docs/execution/reflections/2026-11-10-gui-capture-crop-tool-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| The C key and any tool letter | Shortcut | MEU-105 | D-404, D-508 |
| GUI image import (drop, button, paste) | Feature | MEU-132 | D-519; Session 61 |
| A help-sheet sentence for Crop | Docs | MEU-105 (it rewrites the tool help with the letters) | The `four-tools` body is pinned by AC-59.20, AC-60.15, AC-66.16, AC-85.11 and AC-89.8 (`ui/tests/unit/capture-help-content.test.ts`) |
| Rotate, straighten, flip | Feature | None | Design §9 |
| Crop in place | Behaviour | None | Design D-1, ruled by Mat |
| A crop name field | Feature | None | The endpoint names the crop; 09 asks for no field |
| A real toast component on the Capture page | UI | None unless Mat rules it under D-522 | D-516 |
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` | Bug | Its own session | D-507; recorded if seen, never fixed here |
| `MCP-AUDIT-BASELINE-PENDING-CROP` | Audit | The next authoritative update | D-499 |
| A change to the `crop` description | MCP | None unless Mat rules it after D-521 | D-521 |
| Getting `_meta.action_descriptions` text to the model (Claude Code shows only the top-level description and the schema) | MCP | None unless Mat rules it at the plan gate; whether to register it as an issue is offered there with a do-nothing option | D-521 brief; `s60-plan-d494-describe.txt` |

## BUILD_PLAN.md Audit

MEU-131 is in `.agent/context/meu-status.yaml` (`:3427`, phase 9, band P2, matrix item 9.38, anchor `crop-tool`, `pending`). Row 8 sets it `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at rows 8 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s60-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s60-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Checks that D-521 and D-522 carry Mat's ruling in §Decision Log (S14). **The ruling format:** once Mat rules, the entry's `chosen` starts with the option letter, as `"A: …"`, `"B: …"` or `"C: …"`, and its `human_message_reference` becomes `"USER_EXPLICIT <date> '<Mat's words>'"`. A `chosen` that starts `Pending Mat's ruling`, or a `null` reference, is unruled. `look-check.py` `ruling()` reads this, and `baseline.ps1` and `d494-check.py` use the same rule. Checks the queue: MEU-130 is `approved` in `meu-status.yaml`, and no path of Session 59's Files Modified is dirty.
2. Checks the shapes this plan relies on, by name: the `@router.post("/{id}/crop"` route in `packages/api/src/avkit_api/routes/captures.py` (`:397`), `CAPTURE_MIN_EDGE_PX = 8` in `packages/core/src/avkit_core/domain/capture.py` (`:27`), and `boxHandlePoints`, `hitResizeHandle`, `cursorForHandle`, `RESIZE_HANDLE_CSS` and `RESIZE_HIT_CSS` exported from `capture-transform.ts`; and that `cropCapture`, `capture-crop.ts`, `capture-tool-crop` (toolbar, viewport, test ids) and `'crop'` in `CaptureTool` (`CaptureViewport.tsx:65`) are absent. The anchors step also stops when a new file of §Files Modified already exists.
3. Creates `C:\Temp\av-kit\s60\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256.
4. Runs `uv sync --frozen --offline --all-packages`, and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair is over 1024 B and that Pillow is 13.0.0 (S4).
5. Records the line endings and SHA-256 of every file in §Files Modified to `s60-anchors.txt`, which row 1 reads before it writes.
6. Runs `hotkey-free.py`: the E2E suite registers F2 as the global hotkey (`capture-inbox.test.ts:84`), so the check registers F2 itself through `user32.RegisterHotKey`, releases it at once, and names the holder's error (1409, already registered) when it is taken; and it lists any Electron process whose path is under `P:/av-kit/ui` (Session 57 RULE-4). The backend binds port 0 (`ui/src/main/python-manager.ts:31-32`), so no port is checked.
   It is fail-fast: F2 taken is S6. **At plan time F2 was taken** (`C:/Temp/av-kit/s60-plan-hotkey-live.txt`, error 1409). Every Electron process under `P:/av-kit/ui` was an avkit MCP server, so the holder is another program, which isn't named or touched. Row 0 can't pass until F2 is free; Mat is told at the plan gate.
7. Captures the base Python suite to `s60-base-py.txt`, the base UI suite to `s60-base-ui.txt`, the base MCP suite to `s60-base-mcp.txt`, and the base Electron run of `capture-inbox.test.ts` after a build to `s60-base-e2e.txt`. The suites' own failures are recorded, not fatal; a failing renderer build stops the row.
8. Runs the `red-check.py`, `identity.py`, `dev-app-procs.py`, `hotkey-free.py`, `look-check.py` and `d494-check.py` selftests.

The scripts are copies of Session 59's (and `dev-app-procs.py` of Session 56's), with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds `cropCapture`, `CaptureCropResult`, `CaptureCropBar`, `CaptureCropOverlay`, `CropBox`, `AspectPresetId`, `ASPECT_PRESETS`, `CROP_BUTTONS`, `CROP_MIN_PX`, `roundHalfUp`, `cropEligible`, `clampCrop`, `resizeCrop`, `moveCrop`, `drawCrop`, `fitsRatio`, `ratioBox`, `ratioMinBox`, `ratioLargestBox`, `ratioFeasible`, `presetRatio`, `presetFeasible`, `applyPreset`, `swapCrop`, `applyField`, `nudgeCrop` and `wholeImage`, and keeps the selftest fixtures' names. These excuse a non-required block only: no required Red reaches them by name. `LOCATOR_DETAIL` (`Error: element(s) not found`) is read as the detail line of a `toBeVisible()` assertion that comes just before it, never as a setup failure on its own.
- **`identity.py`.** `PLAN` is this folder. Its selftest binds `session-gate.ps1`, `dev-app-procs.py`, the d494 and look scripts, the two new test modules, `test-ids.ts`, `09`, the register's renders and the grouping.
- **`PROJECT_ARTIFACTS`.** This plan's `*.md` (including `human-check.md` and `d494-run.md`), the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`.

### 2. Type-only first, then Red, then Green (rows 1 to 5)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2).** `capture-crop.ts` with every export, each returning its input box or `null`, the predicates `cropEligible`, `ratioFeasible` and `presetFeasible` returning `true`, `ratioBox`, `ratioMinBox` and `ratioLargestBox` an 8×8 box, and `ASPECT_PRESETS` empty; `CaptureCropResult` and a `cropCapture` that throws `not implemented`; `'crop'` in `CaptureTool` with its exhaustive cases (`TOOL_BUTTON_IDS.crop`, `strokeApplies`, `optionGroups`, `createDrawnMark`), the `TOOLBAR_BUTTONS` entry, an empty `CROP_BUTTONS` in `capture-toolbar.ts`, and a Crop button that does nothing; `CaptureCropBar` and `CaptureCropOverlay` returning `null`; and the pins in §Pins that move. Its check runs `npm --prefix ui run typecheck`, `lint`, and `capture-toolbar.test.ts`, `icon-hints.test.ts`, `capture-page.test.ts` and `capture-page.behavior.test.ts`.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error, a launch failure, a test or action timeout, and a required test that fails on a missing name.
- **Why each Red fails by assertion.** The geometry Reds call the row 1 stubs, which return their input. The page Reds find a Crop button that opens nothing, so the bar, overlay and POST they wait for are absent, and each assertion fails on its value. The Electron Reds click the row 1 Crop button, which opens nothing, then `await expect(bar).toBeVisible()` before any drag or click on the bar. Playwright 1.64.1 reports that as `Error: expect(locator).toBeVisible() failed`, which `red-check.py` reads as an assertion; an action on a missing element would time out and be refused as setup.
- **`--require` matches a test name up to a non-digit boundary.** Row 2: `AC-131.1` to `.10`. Row 4: `AC-131.11` to `.24`, across the Vitest and the Playwright receipt. AC-131.22's `TOOL_BUTTON_IDS` and `TOOLBAR_BUTTONS` cases already pass after row 1; its `CROP_BUTTONS` case fails.
- **Expectations stay immutable in Green.** No test file changes in rows 3 and 5.
- **Electron.** Rows 4 and 5 build the renderer and run Playwright with `ELECTRON_RUN_AS_NODE` cleared, after `hotkey-free.py`. Row 4 runs only `--grep "AC-131"`; row 5 runs the whole `capture-inbox.test.ts`.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`: §1.
- `session-gate.ps1` (H1-2): below.
- `hotkey-free.py` (rows 0, 4, 5 and H1-2): §1 item 6. `--selftest` checks the error-code reading and the path filter with fixtures, without registering a key.
- `dev-app-procs.py` (row 6): Session 56's, with its docstring line changed. `record --root-pid --out --roles electron,backend --wait 120`, `check --record [--stop]`, `--selftest`.
- `look-seed.py`, `look-launch.ps1`, `look-check.py` (row 6): `LOOK_LAUNCH`, under D-522 A. `look-launch.ps1` refuses to start when the seed's app data is missing, clears `ELECTRON_RUN_AS_NODE`, sets `AVKIT_APP_DATA`, starts `npm --prefix ui run dev` with `Start-Process` and no wait, and runs `dev-app-procs.py record`. `look-check.py` reads D-522's `chosen` from this plan and `human-check.md`: under A it requires a `decision:` of `approve`, `no` or `do-nothing` and a `human_message_reference: USER_EXPLICIT <date> '<words>'` line, and that `dev-app-procs.py check --record` lists none of this launch's processes; under B it requires `decision: not-run` with Mat's ruling quoted. It exits 0 only then. `look-check.py --selftest` runs 15 fixture cases (`s60-plan-lookcheck-selftest.txt`). `look-seed.py` was probed on a scratch root (`s60-plan-lookseed-probe.txt`).
- `d494-seed.py`, `d494-harness.ts`, `d494-check.py`, `d494-run.md` (row 7, under D-521 A or B):
  - `d494-seed.py --root <root>` (default `C:/Temp/av-kit/s60/d494/root`, refused when it holds files) writes `<root>/seed/chart-source.png`, 1200×800, with Pillow: a light background, a title band, and four panels in a 2×2 grid, the top-right panel (`x` 640, `y` 120, 520×320) filled with a solid colour and labelled "Revenue". It writes `<root>/seed/panel.json` with the image size, `panel_px` and `panel_fraction`, and prints both.
  - `d494-harness.ts` runs from `mcp-server` with `npx tsx`; its root is `AVKIT_D494_ROOT` or the default above. `seed` starts the backend with `spawnBackend(root)`, puts `inbox_dir` and `backup_dir` under the root through `PUT /api/v1/settings/capture`, copies `chart-source.png` into the inbox, lists it, and writes chart-source's shot id to `seed/source-id.txt`, refusing unless exactly one listed shot is `chart-source.png`. `describe` prints the server instructions and `avkit_capture`'s description and input schema, then, under the heading `## Not shown to the agent: _meta.action_descriptions.crop`, the `crop` text the model doesn't get (D-521). `call '<json>'` connects with `buildLaunch` to `mcp-server/dist/index.js`, makes one `avkit_capture` call, appends `{at, args, refused, isError, text}` to `ledger.jsonl`, and prints the text. It refuses `remove`, `flatten`, `revert` and `image` without calling, and logs the attempt with `refused: true`. Each command starts and stops its own backend on the same root. Probed on a scratch root: `seed` and `describe` exit 0 and a refused `image` is logged (`s60-plan-d494-probe.txt`, `s60-plan-d494-describe.txt`).
  - `d494-run.md` holds the coordinator's steps and the subagent's whole prompt. The coordinator runs the seed, the MCP build, `seed` and `describe`. It cuts the describe output at the "Not shown" heading, fills `{{DESCRIBE}}` with it, and dispatches one subagent with the model Mat ruled. The agent gets only the harness `call` command and the task: "in the test inbox there is a chart image named chart-source. It is 1200 px wide and 800 px tall. Its top-right panel spans 640 px to 1160 px across and 120 px to 440 px down. Crop that panel into a new shot named chart." It must report `new shot: <id>`. It is told not to read the repository, and that the image itself can't be viewed. That limit is recorded: the run tests the description and the arithmetic, not vision.
  - `d494-check.py --plan <plan> --root <root> --report <report>` first reads D-521's ruling with the rule in §1 item 1. Under C it prints `not run under D-521 C` and exits 0; unruled fails. Under A or B it reads `ledger.jsonl`, the seed and inbox files and the saved report (`C:/Temp/av-kit/s60-d494-report.txt`), prints PASS or FAIL per `D494_RUN` criterion, and exits 0 only when all pass. `--selftest` runs 19 fixture cases in a temporary folder, among them a crop of an earlier crop that lands on the panel's numbers in the wrong frame and a missing `source-id.txt`, both of which fail (`s60-plan-d494-check-selftest-final.txt`).

### Session gate (H1-2)

`session-gate.ps1` is Session 59's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s60-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `mcp-types`, `mcp-build`, `mcp-tests`, `state-render`, `issues-render` |
| Runtime | `hotkey-free` (`hotkey-free.py`), then `ui-electron`: `npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts` after `ui-build` |
| Skipped with reason | `py-types`, `py-lint`, `openapi` (no Python or route changes), `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes) |

`py-tests` excuses only ids that row 0's receipt shows failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 8 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, or Pillow isn't 13.0.0 | Stop: a fetch is a download and needs Mat's words |
| S5 | Any network request, download or upload outside the D-521 run as Mat ruled it, including the live audit; or the D-521 harness reaches anything but `127.0.0.1` | Stop and tell Mat |
| S6 | F2, the E2E global hotkey, is taken (error 1409 names it), or an Electron process from this work tree is running, at row 0, 4, 5 or H1-2; or row 6's `record` exits 1 | Stop and name the holder to Mat; free it only by a recorded process id, never by name |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | At row 0, MEU-130 isn't `approved` or a Session 59 path is dirty | Stop; Session 59 closes first |
| S9 | A row must edit `ui/tests/e2e/test-ids.ts` outside the additive block | Stop; ids go in the block at the end, and AC-51.6 and AC-81.13 run in that row's own check |
| S10 | A path, a box value or an error body reaches a Console surface in a way it didn't before | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |
| S11 | A row 0 shape check fails: the crop route, `CAPTURE_MIN_EDGE_PX = 8` or a `capture-transform.ts` export is missing, or a crop name already exists | Stop; amend this plan through the plan review before row 1 |
| S12 | A row would change 09's rule text, an AC or the endpoint | Stop; brief Mat with a recommendation and a do-nothing option (S59 RULE-3) |
| S13 | The D-521 run fails | Record the receipts, brief Mat; never change the description without Mat's words |
| S14 | At row 0, D-521 or D-522 has no ruling from Mat in §Decision Log | Stop; ask Mat through the Human Decision Protocol, and run rows 6 and 7 only as ruled |

## Decision Log

> [!WARNING]
> Mat's request and design D-1 settle the scope, and the grouping (D-400 to D-406) placed this MEU. D-508 to D-520, D-523 and D-525 didn't need Mat: each is autonomous, with its alternatives in `reasoning`. D-521 and D-522 are Mat's. Ids D-477 to D-479 stay as headroom; D-500 to D-507 are claimed on `main` (`C:/Temp/av-kit/s60-plan-dids.txt`), so this block starts at D-508.
>
> Carried and not relisted in the block: every grouping §8 row, D-400 to D-406, with stage `grouping`. Of those, D-401 and D-404 bear on this session. Session 59's D-481 to D-499 and D-506 are carried as it ruled them; this plan relies on D-483 (the endpoint names the crop), D-494 (the run carried here) and D-499 (the open pending baseline). The design's own D-1 to D-13 are a separate namespace, cited as "design D-n" in prose only. The probe (`C:/Temp/av-kit/s60-decision-issue-probe.txt`), run with this plan and the grouping as sources (Session 54 RULE-5), shows what the closeout's decision flags pull in.

```yaml
decision_log:
  - id: D-508
    stage: planning
    question: "Does the C key arrive with the crop tool, as D-404 asks the plan to check?"
    resolution: autonomous
    class: two-way
    chosen: "No. The registry has no page-scoped letter entries, so under 09's own clause the Crop button ships alone with the tooltip Crop and no aria-keyshortcuts, and C arrives with MEU-105"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1068 — if the registry has no page-scoped letter entries yet, C arrives with MEU-105 and the button ships alone"
      - ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:134 — D-404"
      - "C:/Temp/av-kit/s60-plan-probes.txt — commandRegistry lists only Ctrl and F-key chords; the Capture page handles no letter key"
    research:
      engine: none
      sources: []
    reasoning: "Adding C alone would start the page-scoped letter pattern that MEU-105 owns, and D-404 says not to. Showing (C) in the tooltip without a working key would promise a shortcut that does nothing. Two-way: MEU-105 adds the shortcut prop and the key in one place."
    human_message_reference: null
  - id: D-509
    stage: planning
    question: "Where does the Crop button go?"
    resolution: autonomous
    class: two-way
    chosen: "Straight after the lock and before the History group, as its own ToolbarIconButton, outside the Annotation tool group"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:839 — the group is named Annotation tool"
      - "ui/tests/unit/capture-page.behavior.test.ts:3280 — AC-87.2, the lock sits straight after that group"
    research:
      engine: none
      sources: []
    reasoning: "A crop isn't a mark, so putting it inside a group named Annotation tool would misname it to a screen reader. Placing it after the lock keeps AC-87.2 true. Before the group, it would sit between the filmstrip and the tools and split the toolbar's reading order. Two-way."
    human_message_reference: null
  - id: D-510
    stage: planning
    question: "How does the page hold the crop, and what ends it?"
    resolution: autonomous
    class: two-way
    chosen: "One crop state on CapturePage with the box in integer original px, the aspect, the swap, the prior tool, the drag and the busy flag; tool is crop exactly while it is set; it opens on the whole image in the Original view; a shot change, the Annotated view or the shot leaving the list cancels it"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1069 — the box starts as the whole image"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:286 — viewVariant; the Annotated view shows the baked file without the editable overlay"
    research:
      engine: none
      sources: []
    reasoning: "One state object keeps the open, drag and busy cases from drifting apart. Original px makes the fields, readout and body one set of numbers at any zoom. The Original view shows the overlay the crop draws on; the bake has the same size, but it can't show which marks are saved. Keeping the crop open across a shot change would aim a box at the wrong image. Two-way."
    human_message_reference: null
  - id: D-511
    stage: planning
    question: "What are the box's rounding, minimum and edge rules?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_ROUND, CROP_MIN, CROP_HANDLES, CROP_MOVE and CROP_DRAW: integers rounded half up, a minimum of 8 a side (the endpoint's CAPTURE_MIN_EDGE_PX), Crop disabled on a shot under 8 px on a side, no flip, stop at the image edge, a click with no drag keeps the box"
    source_tag: Inferred
    precedents:
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md — REGION_MIN_PX 8 and half-up rounding in resolve_region"
      - "packages/core/src/avkit_core/domain/capture.py:27, :190-194 — CAPTURE_MIN_EDGE_PX 8, applied after clamping to every image"
      - "ui/src/renderer/src/features/capture/capture-transform.ts — resizeBox flips through zero, right for marks"
    research:
      engine: none
      sources: []
    reasoning: "The endpoint refuses a box under 8 px on any image, so the tool's minimum matches it and a box the tool allows is never refused for size. A shot under 8 px on a side can't be cropped at all, so Crop says so instead of sending a request that fails (plan review round 1 F1). Integers keep the body equal to what the user sees. A flip lets a box turn inside out through zero width, which a crop box has no use for; Photos and Photoshop stop at a minimum. A click would otherwise draw a zero box and lose the user's work. Two-way."
    human_message_reference: null
  - id: D-512
    stage: planning
    question: "How do a ratio and Shift act on a drag?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_RATIO: a preset always keeps its ratio; a corner follows the axis moved further; an edge sets its side and the other side centred; under Free, Shift keeps the start ratio for that drag; every ratio box is ratioBox of one whole driving side, and fitsRatio checks exactly that"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1069 — Shift keeps the aspect ratio"
      - "_inspiration/capture-crop/design.md §7.1 — the Windows Photos and Photoshop pattern"
    research:
      engine: none
      sources: []
    reasoning: "A preset that Shift could break would make the select lie. The dominant axis is how both reference tools keep a corner drag under the pointer. Centring the other side of an edge drag keeps the box from walking off to one side. fitsRatio is exact: a ratio box is built from one driving side and its other side is that side times the ratio rounded half up, so the check and the construction are one expression and can't disagree after rounding or in floating point; feasibility, the minimum and the largest box all come from the same range of driving sides (plan review round 2 F1). Two-way."
    human_message_reference: null
  - id: D-513
    stage: planning
    question: "How do the presets and the swap place the box?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_PRESETS and CROP_SWAP: the largest box of the ratio inside the image, centred on the current box's centre and shifted inside; the swap uses 1/r and refits; Square ignores it; under Free it exchanges width and height about the centre; a preset or swap whose smallest 8 px box doesn't fit the image is disabled, never bent"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1071 — the six presets and the swap"
    research:
      engine: none
      sources: []
    reasoning: "The largest fit keeps the most of the image, so a preset never shrinks the box to something the user must drag back out. Centring on the current box keeps the user's region in view. Fitting inside the current box instead would shrink it on every change of preset. On a small or very long shot a ratio can be impossible at 8 px a side; disabling it keeps the minimum, the ratio and the image bounds all true, where bending any one would send a box the endpoint refuses or one that isn't the ratio shown (plan review round 1 F1). Two-way."
    human_message_reference: null
  - id: D-514
    stage: planning
    question: "How do the number fields read and apply text?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_FIELDS and CROP_NUDGE: Enter or blur applies; invalid text reverts; decimals round half up; negatives become 0; X and Y keep the size; W and H keep the origin; a ratio carries the other side; ArrowUp and ArrowDown step 1 or 10"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1072 — X, Y, W and H in original px; arrows nudge 1 px and Shift 10"
      - "ui/src/renderer/src/features/capture/CaptureScrubField.tsx — Up and Down step a numeric field"
    research:
      engine: none
      sources: []
    reasoning: "Applying on each keystroke would clamp a half-typed number (typing 150 passes through 1 and is raised to 8). Reverting invalid text leaves the box valid. Keeping the origin for W and H matches how both reference tools read the fields. Two-way."
    human_message_reference: null
  - id: D-515
    stage: planning
    question: "Which keys does the crop take, and what does it ignore?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_MODAL: Enter commits, Esc cancels, arrows nudge, X swaps; every other key does nothing on the page while the crop is open; a key in a crop field stays in the field"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1075 — other tool letters are ignored until Enter or Esc"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:1164-1250 — handleEditorKey takes history chords, Escape, Delete, Enter and arrows"
    research:
      engine: none
      sources: []
    reasoning: "No tool letter exists yet, so the rule is kept by making the crop own the keyboard: Delete or Ctrl+Z while cropping would change marks the user can't select, which the crop then carries. MEU-105's letters then inherit the rule. Two-way."
    human_message_reference: null
  - id: D-516
    stage: planning
    question: "What is the toast that names the new shot?"
    resolution: autonomous
    class: two-way
    chosen: "The Capture status line, as a convert-on-apply uses it: Saved crop as display_name."
    source_tag: Inferred
    precedents:
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:1402 — CONVERT_ON_APPLY selects the new copy and names it on the status line"
      - "ui/src/renderer/src/components/queue/BulkResultToast.tsx — the only toast, for bulk queue runs"
    research:
      engine: none
      sources: []
    reasoning: "The page already tells the user about a new shot on that line, so a crop that used a toast would be the only capture action that does. Moving BulkResultToast onto the page would add a second place to look and a dismiss button to test. It is flagged: D-522's look is where Mat can ask for a real toast, which would go to Mat as a brief. Two-way."
    human_message_reference: null
  - id: D-517
    stage: planning
    question: "What does the tool show while the request runs and when it fails?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_ERRORS: Save as copy disabled with aria-busy and the status line Cropping… while pending; an error keeps the crop open with its box and shows the endpoint's message through run"
    source_tag: Local Canon
    precedents:
      - ".agent/docs/emerging-standards.md — G35 T2, async feedback on the status line"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:1269 — run sets the error and logs it"
    research:
      engine: none
      sources: []
    reasoning: "Closing on an error would lose the box the user built. A 409 means the file changed under the row; the message tells the user, and Cancel then selecting the shot again reloads it. Two-way."
    human_message_reference: null
  - id: D-518
    stage: planning
    question: "What happens to the other toolbar buttons while the crop is open?"
    resolution: autonomous
    class: two-way
    chosen: "The tool buttons, Undo, Redo, the lock and Annotated are disabled with the reason Finish or cancel the crop first; a second click on Crop cancels"
    source_tag: Inferred
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1075 — the crop is modal"
    research:
      engine: none
      sources: []
    reasoning: "A tool click that silently cancelled the crop would lose the box. A disabled button with a reason says why. Zoom, the filmstrip and the action row stay enabled: zoom helps place the box, and selecting a shot cancels the crop explicitly. Two-way."
    human_message_reference: null
  - id: D-519
    stage: planning
    question: "Does MEU-132 ride with this session, and what is the split?"
    resolution: autonomous
    class: two-way
    chosen: "No. MEU-132 stays in Session 61. The split flag moves the presets and the fields to Session 60b"
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:80 — MEU-132 may ride if Session 60 is small"
      - "docs/build-plan/09-screenshot-capture.md:1079 — GUI image import needs the main process, a file dialog, paste and drop"
    research:
      engine: none
      sources: []
    reasoning: "This session isn't small: 24 ACs, two components, a state machine, a human look and a live run. MEU-132 adds main-process IPC, a dialog, paste and drop, each with its own Electron proof. Together they would pass Session 43's 21M execution. Two-way."
    human_message_reference: null
  - id: D-520
    stage: planning
    question: "How does the Electron proof reach the crop endpoint?"
    resolution: autonomous
    class: two-way
    chosen: "Through a page.route seam in capture-inbox.test.ts, as the flatten proofs do; the endpoint's own behaviour stays proven by Session 59's e2e suite"
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/capture-inbox.test.ts:1341 — installFlattenSeam"
      - "tests/e2e/test_api_capture_crop.py — AC-130.12 to .22 on the real stack"
    research:
      engine: none
      sources: []
    reasoning: "The Electron tests can't build images with Pillow, and a seam lets the proof assert the exact POST body. A real backend in the proof would test Session 59's endpoint again and need a seeded inbox. D-522's look covers the real stack by hand. Two-way."
    human_message_reference: null
  - id: D-521
    stage: planning
    question: "How is D-494's live agent run done?"
    resolution: human
    class: two-way
    chosen: "A: one Haiku 5.5 subagent against this work tree's MCP server and a Pillow test inbox, judged by D494_RUN"
    source_tag: Human
    precedents:
      - "docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md:661 — D-494 carried the run here"
      - "mcp-server/scripts/audit/backend.ts — spawnBackend runs a backend on its own app data"
    research:
      engine: none
      sources: []
    reasoning: "The run is metered and sends the prompt over the network, so it is Mat's call. A weak reader tests the description hardest. B costs more and proves less about weak readers. C, doing nothing, leaves D-494 open. The agent sees what Claude Code shows a model: the server instructions, the tool description and the flattened schema. CROP_TEXT is only in _meta.action_descriptions, which Claude Code doesn't pass on (s60-plan-d494-describe.txt), so the run tests that surface, not CROP_TEXT. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'A: Haiku 5.5 (Recommended)'"
  - id: D-522
    stage: planning
    question: "Does Mat look at the tool before the execution review?"
    resolution: human
    class: two-way
    chosen: "A: row 6 launches the dev app detached on a test inbox, and Mat crops a marked shot with the handles, a preset and the fields"
    source_tag: Human
    precedents:
      - "docs/execution/plans/2026-11-05-*/human-check.md — Session 56's human check format"
    research:
      engine: none
      sources: []
    reasoning: "A drag tool's feel, the dim and the status-line toast are judgements the tests can't make. B, doing nothing, reviews on the Electron proof alone. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'A: Look (Recommended)'"
  - id: D-523
    stage: planning
    question: "Where do the crop bar's icon buttons get their names?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_BUTTONS, a record apart from TOOLBAR_BUTTONS and ACTION_BUTTONS, rendered through ToolbarIconButton"
    source_tag: Local Canon
    precedents:
      - "ui/tests/unit/icon-hints.test.ts:314-330 — AC-80.8 expects every TOOLBAR_BUTTONS entry on the page, with and without a shot"
      - "ui/src/renderer/src/features/capture/capture-toolbar.ts:65 — ACTION_BUTTONS is a separate record for the same reason"
    research:
      engine: none
      sources: []
    reasoning: "The swap button shows only while the crop is open, so in TOOLBAR_BUTTONS it would break AC-80.8. ToolbarIconButton gives it the hint, the hidden icon and the shortcut label the other icon buttons have. Two-way."
    human_message_reference: null
  - id: D-524
    stage: execution
    question: "HEAD moved from baseline.sha 8f29046 to 237732d during execution (S3). How does the session go on?"
    resolution: human
    class: two-way
    chosen: "A: baseline.sha becomes 237732d and the six now-committed registry lines leave baseline-dirty.txt; every other line keeps its SHA-256 and the gate script is unchanged"
    source_tag: Human
    precedents:
      - "git show --stat 237732d: chore(registry): replace Fable 5.1 with Fable 5.2, only the six .agent/model-registry.local.* and .claude/.cursor agent files"
      - "baseline-dirty.txt at row 0 held those six paths as dirty; each file at 237732d hashes to its recorded SHA-256"
    research:
      engine: none
      sources: []
    reasoning: "Mat's commit landed exactly the dirty registry content row 0 recorded, byte for byte, and no MEU-131 path. Rebasing the baseline keeps S3's guard for any further move without changing a gated script. B (excuse 237732d inside the gate) changes the gate. Doing nothing stops the session at row 7. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'A: Rebase baseline (Recommended)'"
  - id: D-525
    stage: execution
    question: "AC-131.20 says choosing Annotated cancels the crop, while CROP_MODAL (D-518, AC-131.21) disables Annotated while the crop is open. Which one does row 4's test assert?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_MODAL holds: Annotated is disabled with 'Finish or cancel the crop first', and AC-131.20's test asserts the button is disabled and a click leaves the view on Original. The page still cancels the crop if the view leaves Original by any other path (the effect at CapturePage.tsx:440-450), so CROP_CANCEL's clause stays true as a guard"
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md CROP_MODAL — the Annotated view button is disabled with the reason 'Finish or cancel the crop first'"
      - "implementation-plan.md D-518 — the other tools and the Annotated view are disabled while the crop is open"
      - "ui/tests/unit/capture-crop-tool.behavior.test.ts:782 — AC-131.20's test, written in row 4"
    research:
      engine: none
      sources: []
    reasoning: "The two ACs can't both hold through the button: a disabled button can't be chosen. D-518 is the ruled design, and AC-131.21 tests it. Asserting a cancel on a click would need Annotated enabled, which breaks CROP_MODAL. Keeping the effect means any view change that doesn't come through the button still closes the crop. Doing nothing leaves AC-131.20's text and its test disagreeing in the record. Two-way: one test assertion and one AC sentence."
    human_message_reference: null
```

## Research References

- `docs/build-plan/09-screenshot-capture.md:1060-1077` (the contract), `:1017-1032` (the endpoint, Session 59).
- `_inspiration/capture-crop/design.md`: §7.1, design D-1, D-3, D-11, L-13, L-14.
- The grouping file: §3 (`:74-80`), §8 (`:126-143`), the tracker (`:110`).
- Session 59's plan and scripts (`docs/execution/plans/2026-11-08-capture-crop-copy/`), Session 56's `dev-app-procs.py` and `human-check.md`, Session 43 `capture-editor-repair`, MEU-100 resize handles.

## Planning receipts

- `C:/Temp/av-kit/s60-plan-probes.txt`: line endings and SHA-256 of every target file at `8f29046`.
- `C:/Temp/av-kit/s60-plan-dids.txt`: the D-id and AC sweep.
- `C:/Temp/av-kit/s60-plan-identity-selftest.txt`, `C:/Temp/av-kit/s60-plan-redcheck-selftest.txt`, `C:/Temp/av-kit/s60-plan-devprocs-selftest.txt`, `C:/Temp/av-kit/s60-plan-hotkey-selftest.txt`, `C:/Temp/av-kit/s60-plan-lookcheck-selftest.txt`, `C:/Temp/av-kit/s60-plan-d494check-selftest.txt`: the scripts' selftests in this folder, each 0 wrong.
- `C:/Temp/av-kit/s60-plan-hotkey-live.txt`: `hotkey-free.py` live; F2 is taken (1409) by a program outside this work tree's Electron (§1 item 6, S6).
- `C:/Temp/av-kit/s60-plan-lookseed-probe.txt`: `look-seed.py` on `C:/Temp/av-kit/s60/plan-probe-look`.
- `C:/Temp/av-kit/s60-plan-d494-probe.txt`, `C:/Temp/av-kit/s60-plan-d494-describe.txt`: `d494-seed.py` and `d494-harness.ts seed`, `describe` and a refused `call` on `C:/Temp/av-kit/s60/plan-probe-d494`.
- `C:/Temp/av-kit/s60-plan-baseline-probe.txt`: `baseline.ps1`'s ruled, queue, shapes and anchors checks run alone; ruled fails as it must before Mat rules, the other three pass.
- `C:/Temp/av-kit/s60-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- `C:/Temp/av-kit/s60-decision-issue-probe.txt`: the decision probe, with this plan and the grouping as sources.
- Step 4A GUI check (`gui-refs-not-shipped`, items 3 and 5): E2 is AC-131.23 and .24, written and wired for the Crop button, the aspect select, the swap, the four fields, Reset, Cancel and Save as copy; G30 is the `SelectInput`; G32 is tokens only (`--color-bg`, `--color-accent`, no literal colour); G33 uses the motion tokens for any transition; G34 is `Button` `primary` `sm` for Save as copy and `ghost` `sm` for Reset and Cancel; G35 is `CROP_ERRORS`.
- Not run at plan time: any suite, build, smoke, the look or the live run.

## Validation stage contract

- **Static:** the UI typecheck and lint, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds and the two render checks, in the session gate.
- **Runtime:** the Electron run of `capture-inbox.test.ts`; under D-521, the live run; under D-522, the look.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
