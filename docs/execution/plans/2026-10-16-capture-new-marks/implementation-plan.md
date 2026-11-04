---
project: "2026-10-16-capture-new-marks"
date: "2026-10-16"
source: "docs/build-plan/09-screenshot-capture.md#pixelate-mark"
meus: ["MEU-90", "MEU-91"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture new marks — Pixelate and Eraser (Session 39)

> **Project:** `2026-10-16-capture-new-marks`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md`:
> - §Pixelate mark (`:800-811`, matrix 9.23, MEU-90)
> - §Eraser mark (`:813-823`, matrix 9.24, MEU-91)
> - §Annotation DTO (`:335-346`), §Annotation geometry, §Viewport toolbar and Options, and the MEU-59/65/67 tests as Local Canon
>
> **Grouping:** `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, Session 39 (`:147-152`), decisions D-1 to D-7 (`:215-221`).
> **Known issues:** `CAPTURE-PIXELATE-TOOL` (`known-issues.yaml:1372`), `CAPTURE-ERASER-TOOL` (`:1333`).
> **Status:** `draft`. Plan review: round 1 `changes_required`, F1–F5 corrected 2026-10-16; round 2 `approved` by the independent reviewer (Codex `gpt-6.1-sol`), with non-blocking residuals F3, F4 and F6 open (see the rolling plan review). Under `plan_to_exec_gate: human`, execution starts only on the user's explicit chat message.
>
> Line anchors are from `main` (`c72fc44`) unless marked. Code that lands with Sessions 34 and 36 is cited by symbol (`optionGroups`, `arrow_shaft_end`, …), because its line numbers will move when those branches merge.

## Goal

Mat asked for two new capture marks (2026-10-03); the 2026-10-09 triage scoped them (D-60, D-62):

1. **MEU-90 — Pixelate.** A `pixelate` rectangle mark that turns the area under it into a mosaic. The bake shrinks the rectangle by the block size and grows it back with nearest-neighbour (`PIXELATE_BAKE`). The default block is 10 px, and the user can change it (`BLOCK_CONTROL`). The editor shows the mosaic live, while drawing and moving (`REGION_PREVIEW`).
2. **MEU-91 — Eraser.** An `eraser` rectangle mark that fills its area with one colour sampled from the pixels just outside its border (`ERASER_SAMPLE`). This works the same way for PNG, JPEG and WebP shots, with no extra button (Human-approved, triage D-62).

Both marks travel every layer the four existing marks do: the domain union and the sidecar, the REST/OpenAPI and MCP annotate schemas, the Pillow bake (and so Save, Apply to image and the MCP flatten), and the Capture page (toolbar, preview, hit test, selection, move, mark list, help).

Unlike the four drawn marks, these two **change pixels that are already in the image**. So the bake runs them first, in one region pass, and the drawn marks are painted over the result (`REGION_PASS`). The preview does the same: a canvas layer under the SVG shows the region pass, and the SVG marks sit on top.

Order (grouping `:150`): MEU-90 first, because it adds the plumbing for a pixel-changing mark through every layer; MEU-91 reuses it. The worktree baseline is the branch HEAD when execution starts; row 0 records it in `baseline.sha`. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from the s39 worktree (ls: No such file or directory, 2026-10-16); no headroom MCP or binary. Scope is the capture annotation path (domain/capture.py, services/capture.py sidecar, adapter.py bake, api schemas/routes captures, mcp-server toolsets/capture.ts, ui features/capture), read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). It stops (S1) if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md` §Claude Code; `.agent/context/harness.local.md` §Claude Code).
  - `native_shell: pwsh`. Every validation goes through `rtk proxy` with the receipt pattern `*> C:/Temp/av-kit/<receipt>.txt; $code=$LASTEXITCODE; Get-Content …; exit $code`.
  - `plan_to_exec_gate: human`. Reviewer `approved` does not start execution; the user's explicit chat message does.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every non-`shared` row keeps `compact_continue` as its fallback.
- **Cloud/local split: not used.** Mat's Windows host is both the driver and the target, so the gates are authoritative where they run. There is no `validate-task.sh`/`.ps1` and no `local-requests.md`. Commands are the PROFILE D6 argv (`.agent/docs/commands.md:190-210`, including the MCP ids `mcp-types`, `mcp-tests`, `mcp-build`) plus targeted file lists.
- **Working directory:** the worktree root `P:/av-kit-wt/s39-capture-new-marks` (`WT`, branch `claude/s39-capture-new-marks`). D6 lists `P:/av-kit` as its default cwd; this plan runs the same argv from `WT` (D-8). Row 0 runs `uv sync --frozen --all-packages`, `npm --prefix ui ci` and `npm --prefix mcp-server ci` in `WT`.
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`; `.agent/skills/cli-dispatch/SKILL.md`). The plan was authored by Claude, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable, the fallback is Mat (PROFILE B3/B4). Self-review is never allowed.
- **Never:** commit, push, upload, publish, or write to YouTube; author an `approved` verdict; send secrets to a provider.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-90` | `.agent/context/handoffs/2026-10-16-capture-new-marks-MEU-90-handoff.md` |
| `MEU-91` | `.agent/context/handoffs/2026-10-16-capture-new-marks-MEU-91-handoff.md` |

Plan-local tooling (project artifacts, not product):

- [session-gate.ps1](session-gate.ps1) (rows 6 and H1-2)
- [identity.py](identity.py) (input identity, H1-6b)
- [red-check.py](red-check.py) (Red proof, rows 2, 3a, 4 and 5a)
- [scope-ast.py](scope-ast.py) (`SCOPE_CHECK` scope-ast, rows 6 and H1-2)
- [region-pass-probe.py](region-pass-probe.py) (planning receipt R-1)

Rolling reviews:

- `.agent/context/handoffs/2026-10-16-capture-new-marks-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-16-capture-new-marks-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites (`BASE_MARKERS`), baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Execution message, §Baseline, §Census; `baseline.sha` |
| WP-1 | MEU-90 TDD: the region-mark plumbing in every layer, `PIXELATE_BAKE`, `REGION_FIXTURE`, the TS region pass, toolbar, block field, preview layer, E2E (rows 2, 3a, 3b) | WP-0 | `shared` | tests + source; Red/Green receipts; `walkthrough.md` §MEU-90 |
| WP-2 | MEU-91 TDD: the `eraser` mark on the same plumbing, `ERASER_SAMPLE` in Python and TS, E2E (rows 4, 5a, 5b) | WP-1 | `compact_continue` | tests + source; `walkthrough.md` §MEU-91; compact, then re-read `task.md` and the walkthrough |
| WP-3 | Session gate and hub reconciliation (rows 6–7) | WP-2 | `shared` | gate receipts in `walkthrough.md` §Gate; 09, 06-gui, gui-actions-index, matrix, `docs/BUILD_PLAN.md` |
| WP-4 | H1 closeout, execution review, H2 | WP-3 | `compact_continue` | two handoffs, rolling review, reflection, metrics row |

---

## User Review Required

> [!IMPORTANT]
> These items are for the review loop and for the user's execution message. They are not a pause point.
>
> 1. **Base branch (prerequisite, landed 2026-10-16).** This plan builds on code from the Session 34 branch (`claude/s34-capture-chrome`, `89c2937`: `optionGroups`, the contextual options row, the icon action row) and the Session 36 branch (`claude/s36-capture-render-fidelity`, `bb0ef7e`: `arrow_shaft_end`, `tools/capture_bake_fixture.py`, the fidelity E2E seam). `WT` was cut from `main` `c72fc44`. On Mat's direction ("merge as you see fit", 2026-10-16), `main` was fast-forwarded to `89c2937` and Session 36 merged on top as `90bb409` (local checks: Vitest 839/839, pytest 676/0, Electron 144/144), and `WT` was fast-forwarded to `90bb409`. Row 0 still checks `BASE_MARKERS` and stops (S1) if they are missing. The plan's own rows merge nothing (D-9).
> 2. **D-16 Block size field (product preference, two-way) — confirmed by Mat 2026-10-16 ("confirmed").** Chosen: a separate "Block size" number field in the contextual options row, shown only for the Pixelate tool or a selected pixelate mark (`BLOCK_CONTROL`). The alternative is to reuse the Stroke field for the block size, which saves a control but gives one field two meanings.
> 3. **D-17 No colour for these marks.** Pixelate and Eraser have no colour (the eraser's colour is sampled). So the options row shows no colour control for them, which amends the Session 34 rule "Color is always present" (`optionGroups` doc comment) for these two tools only.
> 4. **`TEST_AMENDMENTS` TA-1 to TA-5.** Each one extends a test that enumerates the mark types or the tools exhaustively (four types, five tools, "four tools" in help). They are listed in advance. Any other contradiction found by the census stops execution (S2).
> 5. **Optional visual check.** At the commit gate, Mat may draw a pixelate and an eraser in the dev app and compare the Original and Annotated views. This is non-blocking; the pixel tests are the gate.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once, here. ACs, task rows and tests refer to these names and never restate the values.

| Name | Definition | Source |
|---|---|---|
| `BASE_MARKERS` | Before any edit, the branch under `WT` must contain the Session 34 and Session 36 code: `optionGroups` in `ui/src/renderer/src/features/capture/capture-toolbar.ts`, `arrow_shaft_end` in `packages/infrastructure/src/avkit_infra/capture/adapter.py`, and the file `tools/capture_bake_fixture.py`. In `meu-status.yaml`, MEU-59, MEU-67, MEU-81 and MEU-83 are `approved`, and MEU-90 and MEU-91 are `pending`. Row 0 also prints whether `89c2937` and `bb0ef7e` are ancestors of HEAD, for the record (a rebase or squash may change those ids, so the symbols decide). | User Review Required item 1; D-9 |
| `REGION_MARKS` | The mark types `pixelate` and `eraser`. They change existing image pixels inside a rectangle and have no colour. Every other type (`arrow`, `rect`, `highlight`, `text`) is a **drawn mark**. `isRegionMark(mark)` (TS) / `isinstance(mark, (PixelateAnnotation, EraserAnnotation))` (Python) is the only test for the category. | Spec 09:808, 09:820; D-10 |
| `REGION_DTO` | `pixelate`: `{type: "pixelate", x, y, width, height, block_size}`. `eraser`: `{type: "eraser", x, y, width, height}`. `x`, `y`, `width` and `height` have exactly the `rect` mark's constraints in each layer (domain: ints, size not negative; API and Zod: as the `rect` schema in that file). `block_size` is `PIXELATE_BLOCK`. Neither has `color`, `stroke_width` or `opacity`. Unknown keys: refused by the API (`extra="forbid"`) and by both Zod schemas (`.strict()`); ignored on sidecar read (09 §Annotation DTO). The sidecar always writes `block_size`, and reading a pixelate without it is the existing "missing annotation field" error. `SIDECAR_VERSION` stays 1: the change is additive, and an older build reports the existing "unsupported annotation type" error for a new mark. | Spec 09:808, 09:820, 09:335-346; D-11, D-23 |
| `PIXELATE_BLOCK` | `PIXELATE_BLOCK_MIN = 2`, `PIXELATE_BLOCK_MAX = 100`, `PIXELATE_BLOCK_DEFAULT = 10`, defined once in `domain/capture.py` and once in `capture-region-pass.ts`. API: `block_size: int = Field(default=PIXELATE_BLOCK_DEFAULT, ge=PIXELATE_BLOCK_MIN, le=PIXELATE_BLOCK_MAX)`. MCP Zod: `.int().min(2).max(100).optional()` (the API applies the default). Renderer Zod: `.int().min(2).max(100)`, required (the editor always sends it). Parity: the MCP and renderer tests read `minimum`, `maximum` and `default` of `PixelateAnnotationIn.block_size` from `openapi.committed.json` and compare them with their own values. | Spec 09:809 (default 10 px, Triage D-60); D-11 |
| `REGION_RECT` | A region mark covers the pixels `[x, x + width) × [y, y + height)` intersected with the image (`region_clip` / `regionClip`; it returns `None`/`null` when the intersection is empty). An empty intersection (zero width or height, or fully outside) changes nothing. The service still clamps `x` and `y` into the image first, as for `rect` (`_clamp_annotation`, D-23). | D-23; R-1 `clip` |
| `REGION_PASS` | Bake order: (1) every region mark, in list order, applied to the RGBA canvas; (2) every drawn mark, in list order, painted over the result by the existing painters. So a drawn mark is never pixelated or erased, whatever its place in the list, and a later region mark sees the output of earlier region marks (an eraser after a pixelate samples the mosaic). `apply_region_pass(canvas, marks)` (module function in `adapter.py`) runs step 1. `bake` calls it and then `_apply` on the drawn marks. The preview layers the same way (`REGION_PREVIEW` under the SVG). | Research-backed D-10 (ShareX draws effect shapes before the other shapes); R-1 `order` |
| `PIXELATE_QUANT` | The reference mosaic (TS `applyRegionPass`; R-1 `ref_pixelate`): blocks of `block_size × block_size` anchored at the clipped rectangle's top-left; the right and bottom blocks are partial when the size does not divide. A block of `n` pixels whose channel values sum to `sum` becomes, per channel (R, G, B and A), `((sum + n // 2) * (2**24 // n)) >> 24`: Pillow's integer box reduce, transcribed exactly, so the TS reference and the bake use the same intermediate quantization (R-1 `reduce-bands`: diff 0). It is within 1 of the exact round-half-up mean `(2·sum + n) // (2·n)` (R-1), which is the goal's bound. In TS the product is below 2^33, so it is computed in doubles as `Math.floor(((sum + Math.floor(n / 2)) * Math.floor(16777216 / n)) / 16777216)`, never with the 32-bit `>>`. | Spec 09:809; R-1; round 1 F5 |
| `PIXELATE_BAKE` | The Pillow form (`_apply_pixelate`): crop the clipped rectangle; split the bands and `reduce(block_size)` each band (Pillow's box reduce, whose partial edge blocks average only the pixels present); merge; resize ×`block_size` with `NEAREST`; crop to the rectangle size; paste back at the clipped top-left. Splitting first matters: `reduce` straight on RGBA weights the colour by alpha (R-1 `reduce-rgba`, maximum difference 105). | Spec 09:809 ("downscale by the block size, upscale with nearest-neighbour"); R-1 |
| `REGION_TOLERANCE` | Unit parity is exact (0) for both marks: the bake equals `PIXELATE_QUANT` and `ERASER_SAMPLE` byte for byte, single marks and composed region passes alike (R-1 `bake-vs-reference`, `composed`). The goal's bound: `PIXELATE_QUANT` is within 1 per channel of the exact mean (R-1). The Electron oracle (`REGION_PIXEL_ORACLE` (a)) allows 1 per channel for the pixelate and 0 for the eraser. | R-1; round 1 F5 |
| `ERASER_SAMPLE` | The eraser's fill (`eraser_fill` / `eraserFill`) is computed on the canvas as it stands at that mark in `REGION_PASS`. Take the **outer ring**: the pixels exactly 1 px outside the clipped rectangle, corners included, clipped to the image. If that ring is empty (the rectangle covers the whole image), take the **inner ring**: the rectangle's own edge pixels. The fill is the most frequent RGB value in the ring; a tie goes to the smallest packed value `(r << 16) \| (g << 8) \| b`. The rectangle is filled with that colour at alpha 255. | Spec 09:821 (Human-approved triage D-62); D-13; R-1 |
| `REGION_FIXTURE` | One committed JSON file `ui/tests/e2e/fixtures/capture-region-pass.json`, written by `tools/capture_bake_fixture.py` (new function `write_region_fixture`). `cases` lists `REGION_CASES`, each `{name, width, height, pixels, marks, expected}`: `pixels` is the input as flat RGB ints; `expected` is the RGB of the real `CaptureAdapter.bake` of that input with those marks, written as PNG and decoded. Inputs are drawn from `random.Random(39)` except where a case needs a pattern. | D-12 |
| `REGION_CASES` | `pixelate-interior` (16×12, rectangle `(2,1,11,8)`, block 3: partial blocks on the right and bottom); `pixelate-clipped` (rectangle past the right and bottom edges); `pixelate-negative-origin` (`x = −3`); `pixelate-big-block` (block 100 over a 7×5 rectangle: one block); `pixelate-empty` (width 0: no change); `eraser-stems` (flat `#F0F0F0` with two dark stems crossing the top and bottom border: fill `#F0F0F0`); `eraser-tie` (a ring split evenly between two colours: the smaller packed value); `eraser-clipped` (touching the left edge); `eraser-cover` (covering the image: inner ring); `pixelate-then-eraser` (overlapping, on the R-1 `composed` rounding-boundary pattern, whose 2×2 and 3×3 block sums land on .25, .5 and .75: the eraser samples the mosaic); `pixelate-repeat-overlap` (three overlapping pixelates, blocks 4, 3 and 5, on the same pattern: each later one reduces the earlier mosaic). `pixelate-repeat-overlap` is a row 2 case; `pixelate-then-eraser` is added with the eraser cases in row 4. | R-1 checks the same shapes, `composed` included |
| `REGION_IMAGE_FIXTURE` | `tools/capture_bake_fixture.py` also writes `ui/tests/e2e/fixtures/capture-region-original.png`, a 240×160 RGB image: the left half is the gradient `(2x, y, (x + y) mod 256)`; the right half is flat `#F0F0F0` with dark `#141414` stems crossing the eraser's border. And `capture-region-annotated.png`, the real bake of it with `REGION_IMAGE_MARKS`: a pixelate at `(10, 10, 100, 70)` block 10 and an eraser at `(140, 40, 40, 30)`. The two rectangles, and their 1-px outer rings, are disjoint (the pixelate ends at x 110; the eraser's ring starts at x 139), so neither mark's pixels depend on the other: the pixelate-only set written in row 3a and the set rewritten with the eraser in row 5a hold the same pixelate pixels. The PNGs carry no `gAMA`, `iCCP` or `sRGB` chunk, so the browser decodes the stored values unchanged. | D-12; Session 36 `TEXT_FIXTURE` precedent |
| `REGION_PREVIEW` | `CaptureViewport` renders a `<canvas data-testid="capture-region-layer">` at the image's natural size, in the same transformed box as the image, under the SVG overlay, and only while the SVG marks are shown (the Original view). Its input is the region marks of `[...annotations, preview]` in list order, so it updates while a mark is drawn or moved, before pointer-up. On each change it runs `applyRegionPass` over a copy of the `REGION_SOURCE` pixels inside the bounding box of the region rectangles grown by 1 px, writes those rectangles' pixels with `putImageData`, and leaves every other layer pixel transparent (alpha 0). With no region marks, the layer is blank. | Spec 09:810 ("previews the mosaic live"); D-14 |
| `REGION_SOURCE` | The source pixels are the Original view's own `<img>`, drawn once per image load onto an offscreen canvas and read back with `getImageData`. The `<img>` is a same-origin blob URL, so the canvas is not tainted. | D-15 |
| `REGION_PIXEL_ORACLE` | In the Electron app, with a seam serving `REGION_IMAGE_FIXTURE` (`variant=original` → the original PNG, `variant=annotated` → the annotated PNG) and returning `REGION_IMAGE_MARKS` on the detail: (a) inside each mark's rectangle, the `capture-region-layer` pixels from `getImageData` match the annotated PNG decoded in the page (`createImageBitmap` + canvas) within `REGION_TOLERANCE`, and the layer's alpha is 0 outside every rectangle; (b) at `ZOOM_1TO1`, viewport screenshots of the Original view (image + layer + SVG) and the Annotated view (the bake) agree within 2 per channel at the centre pixel of every whole block of the pixelate and at 9 points inside the eraser, mapped through the device pixel ratio; (c) **live**: while a new pixelate is being dragged on the gradient half, before pointer-up, the layer's centre pixel of the dragged rectangle differs from the original image pixel there. | Spec 09:810, 09:822 ("preview test"); D-14; Session 36 `TEXT_PIXEL_ORACLE` method |
| `REGION_E2E_RED` | How AC-90.12 and AC-91.10 first fail (round 1 F2). The region seam follows Session 36 `installFidelitySeam` (it reads both `REGION_IMAGE_FIXTURE` PNGs when installed, so the fixtures must exist: the Electron Red runs only after the backend row that generates them). Its `fetch` override also sets `window.__e2eDetailServed = true` when it returns the detail, and the page's `av-kit:capture:error` events are recorded in `window.__e2eCaptureErrors`. The test then waits with `page.waitForFunction` for the detail to be served and for either a recorded error or `data-overlay-ready="true"`, with no `waitForSelector` before it. Its first assertions are `expect(errors).toEqual([])` and `data-overlay-ready === 'true'`. A renderer that does not know the mark type refuses the detail through its annotate schema (`parseAnnotateBody` → "Invalid overlay marks"), so the test fails at that first assertion. A `waitForFunction` timeout is a setup failure, which `red-check.py` refuses. AC-90.12 is Red in row 3a (MEU-90 backend and fixtures, baseline renderer); AC-91.10 is Red in row 5a (MEU-91 backend and fixtures, MEU-90 renderer). | Session 36 seam (`capture-inbox.test.ts` `installFidelitySeam`); `CapturePage.tsx` detail load; round 1 F2 |
| `ZOOM_1TO1` | As Session 36: one image pixel is one CSS pixel (MEU-66 zoom at 100% through `capture-zoom` controls). The comparison is in image pixels. | Local Canon MEU-66 |
| `TOOLS_ADDED` | `CaptureTool` gains `pixelate` and `eraser`. `TOOLBAR_BUTTONS` gains `capture-tool-pixelate` (lucide `Grid3x3`, "Pixelate") and `capture-tool-eraser` (lucide `Eraser`, "Eraser"), placed after `capture-tool-text`; `TOOL_BUTTON_IDS` maps them. Dragging with either tool creates the mark from the drag rectangle exactly as the Box tool does (same zero-size rule); a pixelate takes the block size from `BLOCK_CONTROL`. | Spec 09:808 ("drawn, selected and moved like a box"); D-16 |
| `OPTIONS_BY_TOOL_V2` | `optionGroups(tool, selected)`, first rule that matches: (1) `tool === 'pixelate'` or `selected?.type === 'pixelate'` → `['block']`; (2) `tool === 'eraser'` or `selected?.type === 'eraser'` → `[]`; (3) the Session 34 rules unchanged (text → `['color', 'text']`; stroke applies → `['color', 'stroke']`; else `['color']`). `OptionGroup` gains `'block'`. `strokeApplies` gains explicit `pixelate`/`eraser` cases returning `false` (its `assertNever` stays exhaustive). | Session 34 `optionGroups`; D-16, D-17 |
| `BLOCK_CONTROL` | A labelled number input `data-testid="capture-block-size"`, label "Block size", `aria-label`/`title` "Block size", shown when `optionGroups` includes `'block'`. Page state `blockSize`, initial `String(PIXELATE_BLOCK_DEFAULT)`. It mirrors the Stroke field (`changeStroke`): every edit updates the field; when the value parses to an int in `PIXELATE_BLOCK` range and a pixelate mark is selected with a different `block_size`, the mark is replaced through `applyHistory` (one undo step per applied change); out-of-range or non-numeric text is held in the field and applied to nothing. A new pixelate uses the parsed value, or `PIXELATE_BLOCK_DEFAULT` when the field is invalid. Selecting a pixelate sets the field to its `block_size` (`inspectMark`). `capture-block-size` joins `COLOR_FOCUS_IDS`, so Delete and arrow keys typed in the field do not act on the mark. | Spec 09:809 ("adjustable with the size control"); D-16 |
| `REGION_MARK_SVG` | `AnnotationMark` renders a region mark as one transparent `<rect data-annotation-type="pixelate\|eraser">` (no fill, no stroke) at the mark's rectangle, so `[data-annotation-type]` selectors, the mark count and the selection box work as for other marks; the pixels come from `REGION_PREVIEW`. The `if` chain gets explicit branches, so a region mark never falls through to the text branch. | D-18 |
| `REGION_EDIT` | Hit test: a click anywhere inside a region mark's rectangle hits its body (`hitBody`, like `highlight`). Move: the body handle translates `x`, `y` within the image (`translateBody`, existing clamp). No resize handles (as `rect`/`highlight` today). Mark list label: "Pixelate n" / "Eraser n" (`markLabel`, n counted per type, as for the others). Remove mark, undo and redo work unchanged. Save sends the marks in `REGION_DTO` form. Every `switch`/`if` on the mark type in `capture-hit-test.ts`, `CapturePage.tsx` (`createDrawnMark`, `inspectMark`) and `CaptureViewport.tsx` gets explicit region cases. | Spec 09:808; D-18 |
| `HELP_TOOLS` | The help section with id `four-tools` keeps its id (links and the AC-39 test read it). Its title becomes "Annotation tools", and its body names the six tools and says that Pixelate and Eraser change the pixels under them, that drawn marks stay on top, and that the eraser picks its colour from the border. | Spec 09:157 (amended by row 7); D-20 |
| `NEW_TESTIDS` | `capture-tool-pixelate`, `capture-tool-eraser`, `capture-block-size`, `capture-region-layer`. No existing id changes. | Local Canon |
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the Files Modified rows below. In `adapter.py`, the whole module is frozen except `CaptureAdapter.bake`, `CaptureAdapter._apply` and the new region names (`region_clip`, `apply_region_pass`, `eraser_fill`, `_apply_pixelate`, `_apply_eraser`). Every other statement keeps its `ast.dump` in the same order: the module docstring and constants (`SUPERSAMPLE`, `ARROWHEAD_LENGTH_FACTOR`, `FONT_CANDIDATES`, …), the class header, and every drawn-mark painter and helper (`_apply_text`, `_apply_rect`, `_apply_highlight`, `_apply_arrow`, `text_plate_box`, `_color_rgb`, `_load_font`, `arrowhead_vertices`, `arrow_shaft_end`). Every baseline import binding stays, and a new import may not rebind a baseline name. Row 6 proves it with `SCOPE_CHECK` ([scope-ast.py](scope-ast.py), Verification Plan §5). | Spec 09:800-823; grouping `:149`; round 1 F4 |
| `TEST_AMENDMENTS` | **TA-1** `tests/unit/test_domain_capture.py:27-33`: `ANNOTATION_TYPE_MEMBERS` and `ANNOTATION_WIRE` gain `Pixelate`/`pixelate` and `Eraser`/`eraser`. **TA-2** `ui/tests/unit/capture-toolbar.test.ts` (Session 34): `TOOLS` gains `'pixelate'` and `'eraser'`; the `MARKS` record (and its key type) gains a `pixelate` and an `eraser` mark; `expectedGroups` gains the two leading `OPTIONS_BY_TOOL_V2` rules (pixelate tool or selected pixelate → `['block']`; eraser tool or selected eraser → `[]`) before its Session 34 lines, so it still states the expected groups independently for every tool × mark pair; the unconditional `` expect(got, `${tool} × ${kind} color`).toContain('color') `` (`:83`) becomes `` expect(got.includes('color'), `${tool} × ${kind} color`).toBe(!regionCase) ``, where `regionCase` is true when the tool or the selected mark is a region type; the accessible-name `toMatchObject` gains `'capture-tool-pixelate': 'Pixelate'` and `'capture-tool-eraser': 'Eraser'`. **TA-3** `ui/tests/unit/capture-page.test.ts`: `HELP_TOPICS` `'four tools'` → `'annotation tools'`, and the AC-39.8 literal id list gains `capture-tool-pixelate` and `capture-tool-eraser`. **TA-4** `ui/tests/unit/capture-page.behavior.test.ts` (Session 34 AC-65 block): `MEU65_OPTION_IDS` gains `block: ['capture-block-size']`, and each `'color' \| 'stroke' \| 'text'` type in that block (the record key, the `expectOptionGroups` parameter, its `Object.entries` cast and the AC-65.3 `cases` element type) gains `'block'`, so `expectOptionGroups` proves the Block size field present for Pixelate and absent for every other tool; `MEU65_TOOLBAR` gains `['capture-tool-pixelate', 'Pixelate']` and `['capture-tool-eraser', 'Eraser']` after the Text entry, and `MEU65_TOGGLES` gains the two ids after `capture-tool-text`; the AC-65.3 `cases` table gains `['capture-tool-pixelate', ['block']]` and `['capture-tool-eraser', []]` placed before the `capture-tool-text` case, so Text is still the active tool after the loop and the post-loop Color-group assertion stands unchanged. `ui/tsconfig.json` includes `tests`, so `ui-types` checks these types. **TA-5** `ui/tests/e2e/test-ids.ts` gains the `NEW_TESTIDS` constants (`CAPTURE_TOOL_PIXELATE`, `CAPTURE_TOOL_ERASER`, `CAPTURE_BLOCK_SIZE`, `CAPTURE_REGION_LAYER`), and the AC-65.4 NO_OVERFLOW tool loop in `capture-inbox.test.ts` (`for (const tool of ['select', 'arrow', 'box', 'highlight', 'text'])`) gains `'pixelate'` and `'eraser'`; if the tools row then overflows at the default window, that is S2, not a test edit. **TA-6** (S2 decision, 2026-10-16) `tests/unit/test_domain.py:306`: `ENUM_MEMBERS["AnnotationType"]` gains `"Pixelate"` (row 2) and `"Eraser"` (row 4), in TA-1's order, for `test_ac_2_1_strenum_members_and_values` and `test_ac_2_11_enum_closed_set_exhaustiveness`. **TA-7** (S2 decision, 2026-10-16) `ui/tests/unit/icon-hints.test.ts:48-57`: AC-80.8's `NO_SHOT_IDS` gains `'capture-tool-pixelate'` (row 2) and `'capture-tool-eraser'` (row 4) after `'capture-tool-text'`, because the new tools are disabled with no shot and carry `NO_SHOT_HINT` like every other tool. Amendments change only those lines; every other line in those tests stays. | Spec 09:808, 09:820; D-17, D-20, D-24 |
| `CENSUS_PATTERNS` | Row 1 greps `ui/tests`, `tests` and `mcp-server/tests` for `AnnotationType`, `ANNOTATION_TYPE_MEMBERS`, `ANNOTATION_WIRE`, `four tools`, `four-tools`, `TOOL_BUTTON_IDS`, `TOOLBAR_BUTTONS`, `capture-tool-`, `optionGroups`, `expectedGroups`, `OptionGroup`, `'color'`, `discriminatedUnion`, `unsupported annotation type`, `_clamp_annotation`, `_apply\b` (the bare name), `markLabel`, `hitBody`, `translateBody`, `data-annotation-type`, `annotations_to_wire`, `MEU65_`, `expectOptionGroups`, `toContain('color')`, `capture-chrome-options` and `expectNoOverflow`. Each hit is dispositioned: `TA-n`, `unaffected` with the reason, or `new-contradiction`, which triggers S2. | Local Canon (Session 30/36 census) |

### MEU-90 — `capture-pixelate-mark`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Domain `PixelateAnnotation` (`domain/capture.py`) | frozen dataclass in the `Annotation` union; `AnnotationType.Pixelate` (`enums.py:229`) | `x`, `y` int; `width`, `height` int ≥ 0; `block_size` int in `PIXELATE_BLOCK` → else `AnnotationValidationError` | n/a (constructor) |
| Sidecar wire (`services/capture.py` `_annotation_from_wire` / `_annotation_to_wire`) | `REGION_DTO` | `block_size` required on read; written always | extra keys ignored on read (09 §Annotation DTO) |
| REST `POST /captures/{id}/annotate`, `POST /captures/{id}/flatten` bodies; `GET /captures/{id}` detail | `PixelateAnnotationIn` in `AnnotationIn` (`schemas/captures.py`); `_annotations_from_in` (`routes/captures.py`) | `REGION_DTO`, `PIXELATE_BLOCK` (`ge`/`le`, default) → 422 on violation | `extra="forbid"` → 422 |
| OpenAPI (`openapi.committed.json`) | generated from the API models | new `PixelateAnnotationIn` schema in the `AnnotationIn` `oneOf`/discriminator | `additionalProperties: false` |
| MCP `avkit_capture` annotate/flatten (`mcp-server/src/toolsets/capture.ts:92`) | Zod `pixelateAnn` in the `discriminatedUnion` | `PIXELATE_BLOCK` (`optional`) | `.strict()` → refused |
| Renderer annotate body (`capture-annotate.ts`) | Zod `pixelateSchema` | `PIXELATE_BLOCK` (required) | `.strict()` |
| `REGION_FIXTURE` JSON (test input) | the pytest and Vitest that read it | `cases[]` keys as defined; ints only | a missing key fails the test |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-90.1 | unit | Domain: `PixelateAnnotation(x, y, width, height, block_size)` constructs with `PIXELATE_BLOCK` values; `AnnotationType.Pixelate.to_wire() == "pixelate"` (TA-1); `PIXELATE_BLOCK` constants have their values. | Spec 09:808; `REGION_DTO` | `block_size` 1, 101, `True`, `2.0`, and a negative width each raise `AnnotationValidationError` |
| AC-90.2 | unit | Sidecar: a pixelate round-trips through `_annotation_to_wire`/`_annotation_from_wire` with `block_size` written; an extra key is ignored; `_clamp_annotation` clamps its `x`/`y` like a `rect` and keeps `width`, `height` and `block_size`. | Spec 09:808, 09:337; D-23 | A sidecar pixelate without `block_size` reports the "missing annotation field" error |
| AC-90.3 | integration | API: `POST /captures/{id}/annotate` with a pixelate (with and without `block_size`) returns 200, the detail echoes it (default 10 filled in), and the sidecar holds it. `openapi.committed.json` carries `PixelateAnnotationIn` with `minimum 2`, `maximum 100`, `default 10`, and the `openapi` D6 check passes. | Spec 09:808; `PIXELATE_BLOCK` | 422 for `block_size` 1 and 101, for an extra `color` key, and for a missing `width` |
| AC-90.4 | unit | MCP: the annotate schema accepts a pixelate with and without `block_size` and passes it through unchanged to the API call; the bounds equal `PixelateAnnotationIn` in `openapi.committed.json`. The Red form asserts `expect(schema.safeParse(body).success).toBe(true)`. | Spec 09:811 ("MCP annotate test"); `PIXELATE_BLOCK` | `block_size` 1 and an extra `color` key are refused (`safeParse(...).success === false`) |
| AC-90.5 | unit | Bake: for each pixelate in `REGION_CASES`, `CaptureAdapter.bake` output equals `PIXELATE_QUANT` exactly (computed in the test) and is within 1 of the exact round-half-up mean; every block is uniform; every pixel outside `REGION_RECT` is byte-equal to the input; the empty case changes nothing. The same holds when the original is a JPEG or a WebP: the test decodes the original with Pillow and computes the expected mosaic from those decoded pixels. | Spec 09:809, 09:811 ("Bake fixture") | Baking with block 1 (the identity) leaves the rectangle unchanged, so the uniform-block check fails on it (the test asserts the check can fail) |
| AC-90.6 | unit | `REGION_PASS`: a `rect` mark drawn over a pixelate keeps its exact stroke colour in its stroke pixels, both when the rect is listed after the pixelate and before it; `apply_region_pass` on a list with only drawn marks returns the canvas unchanged. | D-10 | A bake that applied marks in plain list order (the test patches `apply_region_pass` to a no-op and runs `_apply` on the pixelate inline) gives a different image when the rect is listed first (the test asserts the difference) |
| AC-90.7 | unit | TS: `applyRegionPass` over every pixelate case of `REGION_FIXTURE` (`pixelate-repeat-overlap` included) equals `expected` exactly on every channel; `regionClip` matches `REGION_RECT` for the clipped, negative-origin and empty cases; drawn marks in the list are ignored. | D-12; `PIXELATE_QUANT` | A case with the expected array changed by 1 at one pixel fails the comparator (self-check) |
| AC-90.8 | unit | Fixture freshness: `write_region_fixture` into a temp dir reproduces the committed `capture-region-pass.json` exactly, and the committed `capture-region-annotated.png` decodes to exactly a fresh bake of `capture-region-original.png` with `REGION_IMAGE_MARKS`. | D-12 | Baking with block 11 instead of 10 gives different pixels (asserted) |
| AC-90.9 | unit | Toolbar: `TOOL_BUTTON_IDS.pixelate === 'capture-tool-pixelate'` with its icon and name; `optionGroups` follows `OPTIONS_BY_TOOL_V2` for the pixelate tool and for a selected pixelate (TA-2). | `TOOLS_ADDED`; `OPTIONS_BY_TOOL_V2` | `optionGroups('pixelate', null)` is not `['color', 'stroke']` (the Session 34 fallthrough) |
| AC-90.10 | integration | CapturePage behaviour (Vitest, rendered page): with the Pixelate tool, a drag creates one `pixelate` mark with the drag rectangle and `block_size` 10, shown as "Pixelate 1"; typing 24 in `capture-block-size` with it selected sets `block_size` 24, and one undo restores 10; typing 1 or 101 changes nothing; a click inside it selects it; a body drag moves it; Delete in the block field does not remove it; Save sends the mark in `REGION_DTO` form (TA-4 covers the options row). | `TOOLS_ADDED`; `BLOCK_CONTROL`; `REGION_EDIT` | A zero-size drag creates no mark |
| AC-90.11 | integration | CapturePage DOM: `capture-region-layer` exists while the Original view shows marks and is absent in the Annotated view; each pixelate renders one `<rect data-annotation-type="pixelate">` with no fill and no stroke. | `REGION_PREVIEW`; `REGION_MARK_SVG` | With a pixelate loaded, the mark is not rendered as a `<text>` (the old fallthrough) |
| AC-90.12 | integration | Electron: `REGION_PIXEL_ORACLE` (a), (b) and (c) pass for the pixelate of `REGION_IMAGE_MARKS`. | Spec 09:810 ("previews the mosaic live"), 09:811 ("preview test") | Red (row 3a, `REGION_E2E_RED`): with the MEU-90 backend and committed fixtures on the baseline renderer, the renderer refuses the detail's pixelate, so the first assertion (no capture error) fails |
| AC-90.13 | integration | Flatten: `POST /captures/{id}/flatten` with a pixelate bakes the mosaic into the image (MEU-67 path): every block of the rectangle in the flattened PNG is uniform, and pixels outside are unchanged. | Spec 09:808 (in the Annotation union, so every bake consumer); D-22 | The same request without the mark leaves the rectangle unchanged |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Mark fields and transport | Spec | 09:808: rectangle in the union, sidecar, OpenAPI and MCP; `REGION_DTO` |
| Bake algorithm | Spec | 09:809: downscale by the block size, upscale nearest-neighbour (`PIXELATE_BAKE`) |
| Block default and range | Spec / Research-backed | 09:809 default 10 px; range 2–100 (D-11: 1 is the identity; ShareX caps its pixel size; 100 covers large shots) |
| Order against drawn marks | Research-backed | D-10: region marks first, then drawn marks (ShareX draws effect shapes first) |
| Live preview | Spec | 09:810: live; D-14 canvas layer under the SVG |
| Block size control | Spec / Human preference | 09:809 "adjustable with the size control"; D-16 separate field (confirmed by Mat) |
| Selection and move | Spec | 09:808 "drawn, selected and moved like a box" (`REGION_EDIT`) |
| Colour | Local Canon | None; D-17 amends "Color is always present" for region tools |
| Alpha in the original | Local Canon | The bake writes RGB (`bake` converts at the end), so alpha parity is out of scope (D-19) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/enums.py` | modify | `AnnotationType.Pixelate`, `.Eraser` (+ `to_wire`) |
| `packages/core/src/avkit_core/domain/capture.py` | modify | `PIXELATE_BLOCK`; `PixelateAnnotation`; `EraserAnnotation` (MEU-91); `Annotation` union |
| `packages/core/src/avkit_core/services/capture.py` | modify | sidecar from/to wire; `_clamp_annotation` region branch |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modify | `region_clip`, `apply_region_pass`, `_apply_pixelate`; `bake` runs `REGION_PASS`; `_apply` skips region marks |
| `packages/api/src/avkit_api/schemas/captures.py` | modify | `PixelateAnnotationIn`, `EraserAnnotationIn` in `AnnotationIn` |
| `packages/api/src/avkit_api/routes/captures.py` | modify | `_annotations_from_in` region branches |
| `openapi.committed.json` | regenerate | `tools/export_openapi.py -o openapi.committed.json` (D-21) |
| `mcp-server/src/toolsets/capture.ts` | modify | `pixelateAnn`, `eraserAnn` in the union; description and `ANNOTATE_EXAMPLE` unchanged (D-21) |
| `ui/src/renderer/src/features/capture/capture-annotate.ts` | modify | Zod `pixelateSchema`, `eraserSchema` |
| `ui/src/renderer/src/features/capture/capture-region-pass.ts` | new | `PIXELATE_BLOCK`, `isRegionMark`, `regionClip`, `applyRegionPass`, `eraserFill` (MEU-91) |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modify | `TOOLS_ADDED`, `OPTIONS_BY_TOOL_V2` |
| `ui/src/renderer/src/features/capture/capture-hit-test.ts` | modify | `REGION_EDIT` branches |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | `HELP_TOOLS` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `CaptureTool`; `REGION_PREVIEW` canvas; `REGION_MARK_SVG`; `BLOCK_CONTROL` field |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `createDrawnMark`, `inspectMark`, `blockSize` state, `changeBlockSize`, `COLOR_FOCUS_IDS` |
| `tools/capture_bake_fixture.py` | modify | `write_region_fixture` (`REGION_FIXTURE`, `REGION_IMAGE_FIXTURE`); `main --region --out <dir>` writes only the region set. `write_fixture` and the default `main` (Session 36 `TEXT_FIXTURE`, AC-82.5) are unchanged, so regenerating never rewrites the text fixtures |
| `ui/tests/e2e/fixtures/capture-region-pass.json` | new | `REGION_FIXTURE` |
| `ui/tests/e2e/fixtures/capture-region-original.png`, `capture-region-annotated.png` | new | `REGION_IMAGE_FIXTURE` |
| `tests/unit/test_domain_capture.py` | modify | AC-90.1 (TA-1) |
| `tests/unit/test_domain.py` | modify | TA-6 (`ENUM_MEMBERS` gains `Pixelate`) |
| `tests/unit/test_capture_service.py` | modify | AC-90.2 |
| `tests/unit/test_capture_adapter.py` | modify | AC-90.5, AC-90.6 |
| `tests/unit/test_capture_bake_fixture.py` | modify | AC-90.8 |
| `tests/e2e/test_api_captures.py` | modify | AC-90.3 |
| `tests/e2e/test_api_capture_flatten.py` | modify | AC-90.13 |
| `mcp-server/tests/capture.test.ts` | modify | AC-90.4 |
| `ui/tests/unit/capture-region-pass.test.ts` | new | AC-90.7 |
| `ui/tests/unit/capture-annotate.test.ts` | modify | renderer Zod `REGION_DTO` and `PIXELATE_BLOCK` parity (part of AC-90.4's contract on the renderer side) |
| `ui/tests/unit/capture-toolbar.test.ts` | modify | AC-90.9 (TA-2) |
| `ui/tests/unit/capture-hit-test.test.ts` | modify | AC-90.10 (`REGION_EDIT` units) |
| `ui/tests/unit/capture-page.test.ts` | modify | TA-3 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-90.10, AC-90.11 (TA-4) |
| `ui/tests/unit/icon-hints.test.ts` | modify | TA-7 (`NO_SHOT_IDS` gains `capture-tool-pixelate`) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-90.12 |
| `ui/tests/e2e/test-ids.ts` | modify | TA-5 |

### MEU-91 — `capture-eraser-mark`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Domain `EraserAnnotation` | frozen dataclass in the union; `AnnotationType.Eraser` | `x`, `y` int; `width`, `height` int ≥ 0 | n/a |
| Sidecar wire | `REGION_DTO` | the four ints | extra keys ignored on read |
| REST annotate/flatten bodies, detail | `EraserAnnotationIn` in `AnnotationIn` | `REGION_DTO` → 422 on violation | `extra="forbid"` → 422 |
| OpenAPI | generated | `EraserAnnotationIn` | `additionalProperties: false` |
| MCP annotate/flatten | Zod `eraserAnn` | `REGION_DTO` | `.strict()` |
| Renderer annotate body | Zod `eraserSchema` | `REGION_DTO` | `.strict()` |

The eraser adds no new boundary pattern: it reuses MEU-90's plumbing with one more union member.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-91.1 | unit | Domain: `EraserAnnotation(x, y, width, height)` constructs; `AnnotationType.Eraser.to_wire() == "eraser"` (TA-1). | Spec 09:820 | A negative height and a `bool` x raise `AnnotationValidationError` |
| AC-91.2 | unit | Sidecar: an eraser round-trips; `_clamp_annotation` clamps it like a `rect`. | Spec 09:820 | A sidecar eraser missing `height` reports the "missing annotation field" error |
| AC-91.3 | integration | API: annotate with an eraser returns 200 and echoes it; `openapi.committed.json` carries `EraserAnnotationIn`. | Spec 09:820 | 422 for an extra `color` key and for a missing `x` |
| AC-91.4 | unit | MCP: the annotate schema accepts an eraser and passes it through unchanged. | Spec 09:820 | An eraser with `color` is refused |
| AC-91.5 | unit | Bake: for each eraser in `REGION_CASES`, the rectangle is filled with exactly `ERASER_SAMPLE` (computed in the test), and pixels outside are byte-equal. With a JPEG and a WebP original, the fill equals the ring mode of the Pillow-decoded original, and the rectangle is uniform in the PNG output. | Spec 09:821 ("for PNG, JPEG and WebP alike"), 09:823 ("Bake fixture for the sampled fill") | `eraser-stems`: a fill taken from the ring *mean* (not the mode) differs from `#F0F0F0`, and the test asserts that the mean differs, so the mode is what passes |
| AC-91.6 | unit | `REGION_PASS` order: in `pixelate-then-eraser` the eraser's fill equals the mode of the *pixelated* ring; with the list reversed, the result differs. A `text` mark over an eraser stays crisp. | D-10, D-13; R-1 `order` | The reversed-order bake differs (asserted) |
| AC-91.7 | unit | TS: `applyRegionPass` over every eraser case of `REGION_FIXTURE` (and `pixelate-then-eraser`, a composed pass that R-1 `composed` shows is byte-identical) equals `expected` exactly; `eraserFill` returns the tie-broken colour for `eraser-tie` and the inner-ring colour for `eraser-cover`. | D-12; `ERASER_SAMPLE` | Changing `expected` by 1 at one eraser pixel fails (self-check) |
| AC-91.8 | unit | Toolbar: `TOOL_BUTTON_IDS.eraser === 'capture-tool-eraser'`; `optionGroups('eraser', null)` and a selected eraser give `[]` (TA-2). | `TOOLS_ADDED`; `OPTIONS_BY_TOOL_V2` | `optionGroups('eraser', null)` is not `['color']` |
| AC-91.9 | integration | CapturePage behaviour: with the Eraser tool, a drag creates one `eraser` mark ("Eraser 1"); no option controls show; it selects, moves and removes like a pixelate; Save sends `REGION_DTO`. | `REGION_EDIT` | A zero-size drag creates no mark |
| AC-91.10 | integration | Electron: `REGION_PIXEL_ORACLE` (a) and (b) pass for the eraser of `REGION_IMAGE_MARKS` with tolerance 0 in (a): the layer's eraser pixels equal the annotated PNG's exactly. | Spec 09:823 ("preview test") | Red (row 5a, `REGION_E2E_RED`): with the MEU-91 backend and regenerated fixtures on the MEU-90 renderer, the renderer refuses the detail's eraser, so the first assertion fails |
| AC-91.11 | unit | Help: the `four-tools` section's title is "Annotation tools" and its body names Arrow, Box, Highlight, Text, Pixelate and Eraser (`HELP_TOOLS`, TA-3). | Spec 09:157 (amended) | The old "four tools" title fails |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Mark fields | Spec | 09:820 |
| Fill colour | Spec / Human-approved | 09:821 "colour sampled from the rectangle's border" (triage D-62); D-13 defines the sample (ring mode, tie rule, inner-ring fallback) |
| Lossy formats | Spec | 09:821 "for PNG, JPEG and WebP alike": the sample runs on the decoded canvas, so the rule is one rule for every format |
| Transparency eraser | Human-approved | Not this MEU: "no extra button" (09:821); out of scope |
| Order with pixelate | Research-backed | D-10/D-13: list order inside `REGION_PASS` |

#### Files Modified

The MEU-90 rows above, extended (the same files; no new product file):

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/capture.py`, `enums.py` | modify | `EraserAnnotation`, `AnnotationType.Eraser` |
| `packages/core/src/avkit_core/services/capture.py` | modify | eraser wire and clamp |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modify | `eraser_fill`, `_apply_eraser` |
| `packages/api/src/avkit_api/schemas/captures.py`, `routes/captures.py`, `openapi.committed.json` | modify | `EraserAnnotationIn` |
| `mcp-server/src/toolsets/capture.ts` | modify | `eraserAnn` |
| `ui/src/renderer/src/features/capture/capture-annotate.ts`, `capture-region-pass.ts`, `capture-toolbar.ts`, `capture-hit-test.ts`, `capture-help-content.ts`, `CaptureViewport.tsx`, `CapturePage.tsx` | modify | eraser branches, `eraserFill`, `HELP_TOOLS` |
| `tests/unit/test_domain_capture.py`, `test_capture_service.py`, `test_capture_adapter.py` | modify | AC-91.1, .2, .5, .6 |
| `tests/unit/test_domain.py` | modify | TA-6 (`ENUM_MEMBERS` gains `Eraser`) |
| `ui/tests/unit/icon-hints.test.ts` | modify | TA-7 (`NO_SHOT_IDS` gains `capture-tool-eraser`) |
| `tests/e2e/test_api_captures.py` | modify | AC-91.3 |
| `mcp-server/tests/capture.test.ts` | modify | AC-91.4 |
| `ui/tests/unit/capture-region-pass.test.ts`, `capture-toolbar.test.ts`, `capture-hit-test.test.ts`, `capture-page.behavior.test.ts`, `capture-help-content.test.ts`, `capture-annotate.test.ts` | modify | AC-91.7, .8, .9, .11 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-91.10 |

### Hub and state files (row 7)

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | modify | "four tools" → "six tools" (or "the annotation tools") at `:35`, `:46`, `:157`, `:881`; `:389` "all four types" → "all mark types"; the `AnnotationType` row (`:284`) and the §Annotation DTO table (`:335-346`) gain `pixelate` and `eraser` (`REGION_DTO`); §Pixelate mark and §Eraser mark gain a "Plan" note naming `REGION_PASS`, `PIXELATE_BLOCK`, `ERASER_SAMPLE` ("Session 39 plan D-10–D-13"). `:358` and `:371` are historical MEU-59 text and stay |
| `docs/build-plan/06-gui.md` | modify | `:325` help topics "four tools" → "annotation tools"; `:938` "arrow/box/highlight/text" → add pixelate/eraser |
| `docs/build-plan/gui-actions-index.md` | modify | add `capture:tool_pixelate` and `capture:tool_eraser` after `:79`, in the `capture:tool_text` row format |
| `docs/build-plan/build-priority-matrix.md` | modify | add rows 9.23 and 9.24 after the last 9.x row, if absent, in the `9.12` row format (`:69`) |
| `docs/BUILD_PLAN.md` | modify | Phase 9 status line (`:53`): "MEU-90–91 bound to capture-new-marks"; AUTOGEN regions only through `meu_status.py render` |
| `.agent/context/meu-status.yaml` | modify | MEU-90/91 `execution_plan` + status (H1-3) |
| `.agent/context/meu-registry.md` | generated | written by `meu_status.py render`; never hand-edited |
| `.agent/context/current-focus.md` | modify | the current focus names Session 39 (H1-3) |
| `.agent/context/known-issues.yaml` | modify | the two issues → `resolved` with the handoff link, after H1-7b approval (H2) |
| `.agent/context/known-issues.md` | generated | written by `issue_triage.py render` (H2-2); never hand-edited |
| `docs/execution/metrics.md` | modify | the Session 39 row (H2-3) |

`11-page-layout.md:285` is a historical MEU-57 row and stays.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Blur, circle, freehand, numbered callouts, curved arrows, spotlight, frames | out-of-scope | — | 09 §Named deferrals (`:832`): "Pixelate and Eraser are added by MEU-90/91" only |
| A transparency eraser (cut to alpha) | out-of-scope | — | 09:821 "no extra button"; the bake writes RGB |
| Resize handles for any rectangle mark | out-of-scope | — | 09:808 "moved like a box"; boxes have no resize today |
| A scrub/drag gesture on the Block size field | deferred | MEU-85 | Session 37 `capture-editor-options` owns the size controls' interaction (grouping `:133-137`); the field keeps its id, so MEU-85 can extend it |
| The MCP audit baseline (`.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`) | out-of-scope | — | it records pass/fail per tool action only; no action is added, so it does not change |
| Alpha-channel parity between preview and bake | out-of-scope | — | D-19: `bake` writes RGB; inbox shots are opaque |
| JPEG/WebP decode parity between Chromium and Pillow | out-of-scope | — | D-19: the oracle uses the committed PNG fixture; the lossy-format contract is proven in the bake (AC-90.5, AC-91.5) |

## BUILD_PLAN.md Audit

This project edits the D3 hub in task row 7 only (§Hub and state files). The validation is exact:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s39-state-render.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s39-state-render.txt; exit $code
```

```powershell
rtk proxy rg -n -e "MEU-9[01]" -e "9\.2[34]" -e "capture-new-marks" -e "tool_pixelate" -e "tool_eraser" -e "six tools" -e "all mark types" docs/BUILD_PLAN.md docs/build-plan/build-priority-matrix.md docs/build-plan/09-screenshot-capture.md docs/build-plan/06-gui.md docs/build-plan/gui-actions-index.md *> C:/Temp/av-kit/s39-hub-rg.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s39-hub-rg.txt; exit $code
```

Row 7's deliverable is that the `rg` receipt shows each edit (matrix rows 9.23 and 9.24, the Phase 9 line, the 09 wording and DTO rows, the 06-gui rows, the two gui-actions-index rows), a second `rg` for `four tools` over 09 and 06-gui returns only the historical lines `:358`/`:371`, and `render --check` exits 0.

## Verification Plan

All commands run from `WT` in `pwsh`, after `$env:ELECTRON_RUN_AS_NODE=$null` for any Electron step. Receipts go to `C:/Temp/av-kit/s39-*.txt`. The ids are PROFILE D6's (`.agent/docs/commands.md:190-210`); targeted runs are those argv with a file list.

### 1. Prerequisites and baseline (row 0)

- `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `npm --prefix mcp-server ci`.
- `BASE_MARKERS` and the MEU statuses (S1).
- `git rev-parse HEAD > docs/execution/plans/2026-10-16-capture-new-marks/baseline.sha`.
- The baseline receipts: `py-tests`, `ui-tests`, `mcp-tests`, `ui-build`, then `ui-electron` over `capture-inbox.test.ts`. The baseline failed sets are recorded in `walkthrough.md` §Baseline. A test failing at baseline is never counted as a regression, and a test passing at baseline that fails later is.

### 2. Red (rows 2, 3a, 4, 5a)

Each MEU's new and amended tests are written first. They must fail by assertion, or because a declared-new name does not exist yet (`red-check.py` `DECLARED_NEW`: the new domain classes, the API models, `PIXELATE_BLOCK` names, `apply_region_pass`, `region_clip`, `eraser_fill`, `applyRegionPass`, `regionClip`, `eraserFill`, `isRegionMark`, the `capture-region-pass` module).

- **Python imports of new names go inside the test function**, so a missing name fails that test with an `E ImportError` line instead of breaking collection of the whole module (which would hide the existing tests and is refused by `red-check.py` as a setup failure).
- **Zod rejections are asserted, not thrown:** `expect(schema.safeParse(body).success).toBe(true)`, so a schema that does not know the new type prints an `AssertionError`.
- The fixture writer (`write_region_fixture`) and the AC-90.7/AC-90.8 tests are written in row 2. The committed fixtures pin the *new* bake, so row 3a generates them after the adapter change (`tools/capture_bake_fixture.py --region --out ui/tests/e2e/fixtures`). In row 2, AC-90.8 fails with an `E` line (the bake refuses the unknown mark, or the committed file is missing), and AC-90.7 fails on the unresolved `capture-region-pass` module; both are diagnostic lines `red-check.py` accepts.
- **Electron Red runs after the backend Green that writes its fixtures (`REGION_E2E_RED`, round 1 F2).** Row 2 writes AC-90.12 but runs only pytest, MCP and Vitest. Row 3a lands the MEU-90 backend (domain, sidecar, API, OpenAPI, MCP, adapter, `--region`), passes the targeted pytest and MCP runs, generates the fixtures, proves no renderer file changed, builds the UI and runs AC-90.12: the seam loads, and the test fails at its first assertion. Row 3b implements the renderer, renderer Zod included. Row 4 writes the eraser Red the same way (no Electron run). Row 5a lands the eraser backend, regenerates the fixtures, proves the renderer is the row 3b renderer, and runs AC-91.10 on it. Row 5b implements the eraser renderer. From 5a to 5b, AC-90.12 is also red (its seam now serves the eraser), so 5a runs only `--grep "AC-91.10"` and 5b's full Electron run must pass both.

`RED_PROOF`: [red-check.py](red-check.py) decides each Red. Each Red command writes its child exit code to `<receipt>.exit` straight after `$code=$LASTEXITCODE`. The checker requires:

- a non-zero exit;
- a failing-run summary;
- a *diagnostic* line that attributes the failure: a pytest `E` line, `AssertionError:`, `Error: expect(`, or a load/import error whose missing *subject* is a declared-new name. The subject comes from the error's own grammar (`cannot import name 'X'`, `Cannot find module 'X'`, `Failed to resolve import "X"`, …); a declared name elsewhere on the line, such as the importing test file, does not count (round 1 F3);
- no setup failure: Electron launch, a test or action timeout, a refused connection, or an unrelated load or collection error.

Source-context and test-title lines never count. `red-check.py --selftest` runs 18 receipt fixtures, 8 positive and 10 negative (R-3).

### 3. Targeted Green (rows 3a, 3b, 5a, 5b)

Rows 3a and 5a run the pytest and MCP commands below, then the build and their Electron Red (§2). Rows 3b and 5b run the Vitest command, then the build and the whole `capture-inbox.test.ts`.

```powershell
rtk proxy uv run pytest tests/unit/test_domain_capture.py tests/unit/test_capture_service.py tests/unit/test_capture_adapter.py tests/unit/test_capture_bake_fixture.py tests/e2e/test_api_captures.py tests/e2e/test_api_capture_flatten.py -q --tb=short *> C:/Temp/av-kit/s39-py-targeted.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s39-py-targeted.txt | Select-Object -Last 25; exit $code
```

```powershell
rtk proxy npm --prefix mcp-server run test -- tests/capture.test.ts *> C:/Temp/av-kit/s39-mcp-targeted.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s39-mcp-targeted.txt | Select-Object -Last 25; exit $code
```

```powershell
rtk proxy npm --prefix ui run test -- tests/unit/capture-region-pass.test.ts tests/unit/capture-annotate.test.ts tests/unit/capture-toolbar.test.ts tests/unit/capture-hit-test.test.ts tests/unit/capture-help-content.test.ts tests/unit/capture-page.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/gui-actions-audit.test.ts *> C:/Temp/av-kit/s39-ui-targeted.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s39-ui-targeted.txt | Select-Object -Last 25; exit $code
```

```powershell
$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s39-ui-build.txt; if ($LASTEXITCODE -ne 0) { Get-Content C:/Temp/av-kit/s39-ui-build.txt | Select-Object -Last 25; exit $LASTEXITCODE }; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts *> C:/Temp/av-kit/s39-e2e-capture.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s39-e2e-capture.txt | Select-Object -Last 30; exit $code
```

### 4. Session gate (rows 6, H1-2): `session-gate.ps1`

The plan-local [session-gate.ps1](session-gate.ps1) runs in `pwsh` from `WT`. It writes one receipt per step (`C:/Temp/av-kit/s39-D6-<id>.txt`) and prints `<id> stage=<stage> exit=<n>` and the receipt tail. It is fail-fast in stage order: after the first non-zero step, every later step is printed as `not_run`. The steps, in order:

1. `identity-before`: `INPUT_IDENTITY` (§Validation stage contract).
2. **Static:** `py-types`, `py-lint`, `py-lint-tools` (`ruff check tools/capture_bake_fixture.py`), `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, then `scope-ast` and `scope-paths` (`SCOPE_CHECK`, §5).
3. **Full:** `py-tests` (whole suite; the Session 36 baseline rule for the two environmental packaging tests, `walkthrough.md` §Baseline), `ui-tests`, `mcp-build`, `mcp-tests` (G-1: the build first, because the tests load `mcp-server/dist`), `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`.
4. **Runtime:** `ui-electron` (the full Electron suite), then `e2e-repeat`: `test:e2e -- tests/e2e/capture-inbox.test.ts --grep "AC-90.12|AC-91.10" --repeat-each=10`. Any flake is a defect (S6).
5. `identity-npm`, then `identity-after`. The gate fails when `tested_state` differs between `identity-before` and `identity-after`.

The row's command is `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1`, with the receipt pattern (task row 6).

The D6 `mcp-audit` runtime check is not a gate step. It drives the live server per tool action and records pass/fail per action; this plan adds no action, and the new annotate members are proven by `mcp-tests` (AC-90.4, AC-91.4) and `mcp-build`. Its baseline therefore stays unchanged (§Out of Scope).

### 5. `SCOPE_CHECK` (row 6)

- **`scope-ast`:** [scope-ast.py](scope-ast.py) compares `adapter.py` at `baseline.sha` with the working tree. It drops only what `PRODUCT_SCOPE` lets change (`bake`, `_apply`, the new region names, and the import statements, which it compares as bindings), then requires every remaining module and `CaptureAdapter` statement, and the class header, to have the same `ast.dump` in the same order. `--selftest` runs 16 fixtures (R-4).
- **`scope-paths`:** every path in `git diff --name-only <baseline>` plus the untracked files is a Files Modified row (product, tool, fixture, test, hub and state files), or one of this project's artifacts (this plan folder, the handoffs, the reflection). The allow-list in the script is the union of the Files Modified tables; changing either one means changing both.

### 6. OpenAPI drift (G8)

`packages/api/` changes, so `openapi.committed.json` is regenerated (`uv run python tools/export_openapi.py -o openapi.committed.json`) in rows 3a and 5a, and the `openapi` D6 check (`--check`) must pass in the gate. H1-4 proves the committed diff contains only the two new schemas and their references in the `AnnotationIn` unions (any other schema change is S5).

### 7. Closeout (H1, H2)

These are the template commands with this project's paths. `validate_closeout_artifacts.py` is run per handoff (two runs: `--handoff` + `--plan`, then `--ac-coverage-only`), plus `durable_evidence.py --require-full`, the review-state parsers, the reflection validator with `--decision-source` for the plan, the two handoffs, the grouping file and `.agent/context/known-issues.yaml`, with `--decision-issue` for each of the two issue ids, and `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped (`docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent; recorded `gui-refs-not-shipped`). New and changed elements:

| Element | Kind | Change | Standard | E2E |
|---|---|---|---|---|
| `capture-tool-pixelate` | icon button (new) | `TOOLS_ADDED`; accessible name "Pixelate"; hint as the other tool buttons (Session 34 icon-button hints) | E2 (`emerging-standards.md:1167`) | AC-90.12 (tool used to draw in (c)); AC-65.4 tool loop (TA-5) |
| `capture-tool-eraser` | icon button (new) | `TOOLS_ADDED`; "Eraser" | E2 | AC-91.10; AC-65.4 tool loop (TA-5) |
| `capture-block-size` | number input (new) | `BLOCK_CONTROL`; label and `aria-label` "Block size" | E2 | AC-90.10 (behaviour); present in AC-90.12's draw step |
| `capture-region-layer` | output canvas (new) | `REGION_PREVIEW` | E2 | AC-90.12, AC-91.10 |
| pixelate/eraser mark `<rect>` (output) | SVG mark (new) | `REGION_MARK_SVG` | E2 | AC-90.11 |
| help section `four-tools` | output (changed) | `HELP_TOOLS` | — | AC-91.11 |

G36 (no silent test guards): the pixel tests assert; they never `skip`. G37: behaviour tests use `userEvent`. No G30–G35 surface changes.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a graph directory, a `BASE_MARKERS` symbol or file missing, MEU-59/67/81/83 not `approved`, or MEU-90/91 not `pending` | Stop. Ask Mat to land Sessions 34 and 36 (User Review Required item 1), or re-run the context-tool gate. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` | Stop for the human with a Decision Brief naming the test and the smallest amendment. No test edit. |
| S3 | `red-check.py` refuses a Red receipt (`RED_PROOF`, §2) | Fix the test setup only, then re-prove Red. |
| S4 | `REGION_PIXEL_ORACLE` cannot pass within its tolerances after the fix (for example Chromium alters the decoded fixture pixels) | Stop for a Decision Brief with the measured differences (the tolerance is a fidelity contract, not a tuning knob). |
| S5 | `SCOPE_CHECK` finds a change outside `PRODUCT_SCOPE`, or the OpenAPI diff contains more than the two new schemas and their union references | Revert that change or stop with a Decision Brief. |
| S6 | An Electron flake in `--repeat-each` | Fix the test's waiting, never add retries; if the product is racy, stop with a brief. |
| S7 | Review cap (plan 3, execution 6) or the reviewer is unavailable | HARD STOP with a TL;DR (create-plan §5d). Mat is the fallback reviewer. |

## Decision Log

Research engine for this plan: `native` (Claude Code web search, 2026-10-16). Grouping §8 D-1, D-3, D-4 and D-6 carry forward unchanged into the reflection (stage `grouping`); D-2, D-5 and D-7 do not touch this scope. This plan's ids start at D-8. "Triage D-60/D-62" are the 2026-10-09 triage decisions the spec cites.

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "Where is the plan written and executed?"
    resolution: autonomous
    class: two-way
    chosen: "Worktree P:/av-kit-wt/s39-capture-new-marks on branch claude/s39-capture-new-marks, cut from main c72fc44"
    source_tag: Local Canon
    precedents: ["Session 36 D-8 (worktree per session)", "the Session 34 and 36 worktrees are read-only references for this session"]
    research: { engine: none, sources: [] }
    reasoning: "A worktree isolates this session from the other open session branches. D6 argv are unchanged; only the cwd differs."
  - id: D-9
    stage: planning
    question: "Plan Session 39 now, before Sessions 34 and 36 are on main?"
    resolution: human
    class: two-way
    chosen: "Yes: plan now; execution waits until Mat lands Sessions 34 and 36 (BASE_MARKERS, S1). The plan cites their code by symbol."
    source_tag: Human-approved
    human_ref: "USER_EXPLICIT 2026-10-16 '@.agent/workflows/create-plan.md  for Session 39 as per the session grouping'"
    precedents: ["grouping :150 'After Session 36 (shared bake code)'", "grouping D-4 (two-way order)", "MEU-81 (Session 34) owns the options row this plan extends"]
    research: { engine: none, sources: [] }
    reasoning: "The user asked for the Session 39 plan now. Both prerequisite branches are approved (MEU-81, MEU-83 approved on their branches), so the code the plan extends is settled. Executing before they land would rewrite the same files twice, so row 0 enforces the order."
  - id: D-10
    stage: planning
    question: "In what order do region marks and drawn marks bake?"
    resolution: autonomous
    class: one-way
    chosen: "REGION_PASS: every region mark in list order first, then every drawn mark in list order"
    source_tag: Research-backed
    precedents: ["09:808 pixelate is a rectangle 'like a box' but it changes image pixels", "R-1 order check"]
    research: { engine: native, sources: ["https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/ShapeManager.cs", "https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/Effect/BaseEffectShape.cs", "https://getsharex.com/docs/image-editor.html"] }
    reasoning: "ShareX's editor draws its effect shapes (pixelate, blur, highlight) before the other shapes, so an arrow drawn over a pixelated area stays readable. Plain list order would let a pixelate drawn after an arrow scramble the arrow, which is never what a user wants from a redaction mark, and the preview could not show it with a canvas under the SVG. One-way: the order is visible in every baked file."
  - id: D-11
    stage: planning
    question: "What block sizes are allowed, and how is block_size carried?"
    resolution: autonomous
    class: two-way
    chosen: "PIXELATE_BLOCK: 2..100, default 10; API default, MCP optional, renderer required; sidecar always writes it"
    source_tag: Research-backed
    precedents: ["09:809 default 10 px (triage D-60)", "rect stroke_width is an int field with no API default"]
    research: { engine: native, sources: ["https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/Effect/PixelateEffectShape.cs"] }
    reasoning: "Block 1 is the identity (no redaction), so 2 is the floor. ShareX bounds its pixel size with a numeric control; 100 px covers large 4K shots while keeping one block inside any sensible rectangle. A default at the API keeps MCP calls short."
  - id: D-12
    stage: planning
    question: "How are the pixelate bake and the TS preview proven to agree?"
    resolution: autonomous
    class: two-way
    chosen: "PIXELATE_QUANT (Pillow's integer box reduce, transcribed exactly) as the TS reference, PIXELATE_BAKE in Pillow, exact unit parity for single and composed passes, REGION_TOLERANCE 1 only for the goal bound and the Electron pixelate oracle; REGION_FIXTURE and REGION_IMAGE_FIXTURE written from the real bake and pinned by a freshness test"
    source_tag: Research-backed
    precedents: ["Session 36 TEXT_FIXTURE and its freshness pytest (AC-82.5)", "R-1 reduce-bands diff 0 against PIXELATE_QUANT and 1 against the exact mean, composed passes byte-identical, reduce-rgba max diff 105", "round 1 F5"]
    research: { engine: native, sources: ["https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.reduce"] }
    reasoning: "Pillow's reduce rounds its box mean slightly differently from an exact round-half-up mean (at most 1 level, R-1). Round 1 F5 showed why a 1-level bound per operation is not enough: before ERASER_SAMPLE's mode a 1-level difference can split a frequency bucket or flip a tie, and repeated pixelates compound it. So the TS reference uses Pillow's own integer quantization, which R-1 shows equal to reduce on every channel of 400 random cases, and every pass, composed or not, is byte-identical (R-1 composed, with a sensitivity control showing an exact-mean reference would differ). The exact mean stays only as the goal's 1-level bound. Splitting the bands first avoids reduce's alpha weighting. A committed fixture from the real bake means the TS test compares against Pillow, not against a re-implementation."
  - id: D-13
    stage: planning
    question: "Which border pixels decide the eraser colour, and how?"
    resolution: autonomous
    class: two-way
    chosen: "ERASER_SAMPLE: the mode of the 1-px outer ring (clipped), smallest packed RGB on a tie, inner ring when the outer ring is empty; opaque fill; sampled after earlier region marks"
    source_tag: Research-backed
    precedents: ["09:821 'colour sampled from the rectangle's border' (Human-approved triage D-62)", "R-1 eraser checks"]
    research: { engine: native, sources: ["https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/Drawing/SmartEraserDrawingShape.cs", "https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Helpers/ImageHelpers.cs"] }
    reasoning: "ShareX's smart eraser fills with a single colour taken from the image. The mode (not the mean) ignores text strokes that cross the border, which is the common case when erasing a word from a flat UI background (R-1 eraser-stems). The tie rule makes the result deterministic across Python and TS. One rule for every format, as 09:821 requires."
  - id: D-14
    stage: planning
    question: "How does the editor show the region marks live?"
    resolution: autonomous
    class: two-way
    chosen: "REGION_PREVIEW: a natural-size canvas under the SVG, fed by applyRegionPass over the region marks of annotations plus the in-progress preview mark"
    source_tag: Research-backed
    precedents: ["09:810 'previews the mosaic live'", "Session 36 TEXT_PIXEL_ORACLE method"]
    research: { engine: none, sources: [] }
    reasoning: "SVG filters cannot reproduce a block mean exactly, and the eraser needs a sampled colour; a canvas running the same algorithm as the bake gives pixel parity within REGION_TOLERANCE. Putting it under the SVG reproduces REGION_PASS's layering. Limiting the work to the bounding box of the region rectangles keeps a pointer move cheap."
  - id: D-15
    stage: planning
    question: "Where do the preview's source pixels come from?"
    resolution: autonomous
    class: two-way
    chosen: "REGION_SOURCE: the Original view's own img element, drawn once per load to an offscreen canvas"
    source_tag: Local Canon
    precedents: ["the viewport loads the image as a same-origin blob URL (Session 36 E2E seam serves it through fetch)"]
    research: { engine: none, sources: [] }
    reasoning: "It needs no second fetch, it is exactly the image the user sees, and a blob URL does not taint the canvas."
  - id: D-16
    stage: planning
    question: "Which control sets the block size?"
    resolution: human
    class: two-way
    chosen: "BLOCK_CONTROL: a separate 'Block size' field in the options row; Mat confirmed it on 2026-10-16 (\"confirmed\", answering User Review Required item 2)"
    source_tag: Human-approved
    precedents: ["Session 34 options row shows only the groups a tool uses (OPTIONS_BY_TOOL)", "the Stroke field's edit/undo behaviour (changeStroke)"]
    research: { engine: none, sources: [] }
    reasoning: "09:809 says 'adjustable with the size control'. A field named for what it changes avoids giving Stroke two meanings; the options row already shows only relevant groups, so the extra field costs no space for other tools. Mirroring changeStroke keeps one undo step per applied change."
  - id: D-17
    stage: planning
    question: "Do region marks have a colour?"
    resolution: autonomous
    class: two-way
    chosen: "No; optionGroups returns ['block'] for pixelate and [] for eraser, amending 'Color is always present' for these tools only"
    source_tag: Spec
    precedents: ["09:808 and 09:820 list no colour field", "09:821 the eraser colour is sampled"]
    research: { engine: none, sources: [] }
    reasoning: "A colour control that changes nothing would mislead; the DTO has no colour to carry."
  - id: D-18
    stage: planning
    question: "How are region marks shown, selected and moved in the SVG?"
    resolution: autonomous
    class: two-way
    chosen: "REGION_MARK_SVG transparent rect + REGION_EDIT (body hit inside, body move, labels 'Pixelate n'/'Eraser n', no resize)"
    source_tag: Spec
    precedents: ["09:808 'drawn, selected and moved like a box'", "highlight hit test uses the padded rectangle (capture-hit-test.ts hitBody)"]
    research: { engine: none, sources: [] }
    reasoning: "A transparent rect keeps every [data-annotation-type] consumer working while the pixels come from the canvas. Hitting the whole interior matches how a user perceives a filled area."
  - id: D-19
    stage: planning
    question: "Are alpha and lossy-decode parity part of the preview contract?"
    resolution: autonomous
    class: two-way
    chosen: "No; the oracle uses an opaque PNG fixture; the lossy-format rule is proven in the bake"
    source_tag: Local Canon
    precedents: ["bake converts to RGB at the end (adapter.py bake)", "inbox shots are opaque screen captures"]
    research: { engine: none, sources: [] }
    reasoning: "Chromium and Pillow may decode JPEG slightly differently; that is not this MEU's defect to own, and 09:821's format clause is about the bake."
  - id: D-20
    stage: planning
    question: "Rename the help section id 'four-tools'?"
    resolution: autonomous
    class: two-way
    chosen: "Keep the id; change the title and body (HELP_TOOLS)"
    source_tag: Local Canon
    precedents: ["capture-help-content.test.ts looks up the section by id 'four-tools'"]
    research: { engine: none, sources: [] }
    reasoning: "An id is a stable anchor, not user text; renaming it would churn tests and links for no user-visible gain."
  - id: D-21
    stage: planning
    question: "What changes in the published schemas and MCP text?"
    resolution: autonomous
    class: two-way
    chosen: "Regenerate openapi.committed.json (two new schemas only); the MCP tool description and ANNOTATE_EXAMPLE stay unchanged"
    source_tag: Local Canon
    precedents: ["AC-59.16 pins the MCP annotate description/example", "G8 OpenAPI drift check"]
    research: { engine: none, sources: [] }
    reasoning: "The JSON schema MCP clients receive already lists the new members through the Zod union; editing the pinned example would reopen AC-59.16 for no gain."
  - id: D-22
    stage: planning
    question: "Does flatten (Apply to image) need its own region code?"
    resolution: autonomous
    class: two-way
    chosen: "No; flatten calls the same CaptureAdapter.bake, so REGION_PASS applies; AC-90.13 proves it"
    source_tag: Local Canon
    precedents: ["MEU-67 flatten path bakes through the adapter (09 §Flatten with backup)"]
    research: { engine: none, sources: [] }
    reasoning: "One bake path means one behaviour for Save, Apply to image and MCP flatten."
  - id: D-23
    stage: planning
    question: "How do clamping and clipping interact?"
    resolution: autonomous
    class: two-way
    chosen: "The service clamps x and y into the image like a rect (_clamp_annotation); the adapter then clips the rectangle (REGION_RECT)"
    source_tag: Local Canon
    precedents: ["_clamp_annotation clamps rect/highlight x,y to [0, width/height] (services/capture.py)"]
    research: { engine: none, sources: [] }
    reasoning: "Region marks behave like the other rectangles at the edges; the adapter's clip keeps a direct adapter call (fixture writer, tests) safe for any input."
  - id: D-24
    stage: execution
    question: "The row 1 census found two existing tests outside TEST_AMENDMENTS that the design breaks, and the gate ran mcp-tests before mcp-build (S2). Amend?"
    resolution: human
    class: two-way
    chosen: "Yes, all three: TA-6 (test_domain.py ENUM_MEMBERS), TA-7 (icon-hints.test.ts NO_SHOT_IDS), G-1 (session-gate.ps1 mcp-build before mcp-tests); both test files join Files Modified and the scope-paths allow-list"
    source_tag: Human-approved
    human_ref: "USER_EXPLICIT 2026-10-16 'yes, all three' (answering the S2 Decision Brief, walkthrough §S2 stop)"
    precedents: ["TA-1 amends the same AnnotationType member list in test_domain_capture.py", "RULE-1 (Session 36 reflection): every gitignored build output the suites need is its own stage"]
    research: { engine: none, sources: [] }
    reasoning: "Both tests pin closed sets that the approved design extends (REGION_MARKS, TOOLS_ADDED); the amendment adds the new members only. Building the MCP server before its tests makes the gate valid in a fresh worktree and stops it testing a stale dist."
```

## Research References

- ShareX image editor documentation: https://getsharex.com/docs/image-editor.html
- ShareX `ShapeManager.cs` (draw order): https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/ShapeManager.cs
- ShareX `BaseEffectShape.cs`: https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/Effect/BaseEffectShape.cs
- ShareX `PixelateEffectShape.cs`: https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/Effect/PixelateEffectShape.cs
- ShareX `SmartEraserDrawingShape.cs`: https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/Drawing/SmartEraserDrawingShape.cs
- ShareX `ImageHelpers.cs`: https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Helpers/ImageHelpers.cs
- Pillow `Image.reduce`: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.reduce
- MDN `CanvasRenderingContext2D.putImageData`: https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/putImageData

The plan relies on only two ShareX facts: effect shapes are drawn before the other shapes, and the smart eraser fills with one colour taken from the image. Everything else is defined here and proven by R-1.

## Planning receipts

- **R-1 (2026-10-16, re-run after round 1).** [region-pass-probe.py](region-pass-probe.py), run with `P:/av-kit/.venv/Scripts/python.exe region-pass-probe.py` (Pillow 12.3.0), exit 0, 0 problems. It transcribes `REGION_RECT`, `PIXELATE_QUANT`, `PIXELATE_BAKE` and `ERASER_SAMPLE` literally, as a pure-Python reference (the TS form) and as the Pillow form.
  - **reduce-bands:** 400 random cases (391 with partial blocks): per-band `reduce` equals `PIXELATE_QUANT` on every channel (maximum difference 0), and `PIXELATE_QUANT` is within 1 of the exact round-half-up mean.
  - **reduce-rgba:** `reduce` straight on RGBA differs by up to 105 on a colour channel (alpha weighting), so `PIXELATE_BAKE` splits the bands.
  - **bake-vs-reference:** 5 clipped, partial and oversized cases, maximum difference 0, 0 pixels changed outside the rectangle.
  - **eraser:** text stems crossing the border → `(240,240,240)`; a 6/6 tie → `(0,0,0)` (the smaller packed value); a rectangle clipped at the left edge samples an 11-px ring with minimum x 0; a rectangle covering the image falls back to the inner ring `(1,2,3)`; the Pillow form equals the reference exactly in all three comparison cases.
  - **order:** an eraser after an overlapping pixelate gives a different result from the reverse order.
  - **composed (round 1 F5):** 8 whole region passes (pixelate then an eraser whose ring is pixelated, block 2 and 3; three overlapping pixelates; pixelate, eraser, pixelate), on a rounding-boundary image and on noise: the Pillow form and the reference are byte-identical in all 8. Sensitivity control: the same reference with the exact mean instead of `PIXELATE_QUANT` differs in 6 of them, so the check can fail.
  - Planning fix: the first eraser fixture inked most of the ring (14 of 24 pixels), so the mode was the ink. The fixture, not the contract, was wrong; it now draws two stems.
- **R-2 (2026-10-16).** `identity.py --selftest`, exit 0: every bound mutation (including `mcp-server/package-lock.json` and the new `capture-region-pass.json` fixture) changes `tested_state` and makes `durable_evidence.evidence_problems` refuse the earlier full record; edits to the project artifacts leave it unchanged.
- **R-3 (2026-10-16, re-run after round 1).** `red-check.py --selftest`, exit 0, 18 fixtures, 0 wrong.
  - **Pass (8):** a pytest assertion; a pytest missing `PixelateAnnotation`; a pytest missing `apply_region_pass`; a Vitest unresolved `capture-region-pass` module; a Vitest Zod `safeParse` assertion; a Playwright `expect` failure; an ANSI-coloured Vitest assertion; a Vitest `Cannot find module '…/capture-region-pass' imported from …` line.
  - **Refused (10):** an Electron launch failure (whose title names AC-90.12); a locator timeout; an ANSI-coloured locator timeout; an unrelated `ImportError`; a pytest collection error; a run whose exit was 0; a receipt with no `.exit` file; an unrelated module imported by the new test file (the round 1 F3 witness); a misspelt name imported from a declared module; an assertion plus an unrelated unresolved import in one receipt.
- **R-4 (2026-10-16, re-run after round 1).** `session-gate.ps1` parses with 0 PowerShell parse errors; not run during planning (it needs the execution baseline). `scope-ast.py --selftest`, exit 0, 16 fixtures, 0 wrong: the permitted changes pass; a changed `SUPERSAMPLE` or `FONT_CANDIDATES`, a changed frozen method or helper, a class attribute, a new unpermitted constant or method, an import that rebinds a baseline name, a removed or retargeted baseline import, a permitted name that also reassigns a constant, a changed docstring or class base, and a removed `bake` are refused. On real source: the Session 36 `adapter.py` against itself has 0 problems; the same file with `SUPERSAMPLE` or `FONT_CANDIDATES` changed is refused; and the `main` `adapter.py` against `--base bb0ef7e` is refused (it lacks the Session 36 constants and `_apply_arrow` change), a live negative.

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `py-lint-tools`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract` (§4).
- **Targeted:** §3 after each production edit (blocking for its row).
- **Fresh full:** §4 in one pass after the last edit (row 6), from `WT`, `pwsh`. It must pass; no partial, cached or reused receipt counts. Re-run all of §4 if any input changes after it (H1-6b).
- **Runtime (optional, non-blocking):** Mat's visual check (User Review Required item 5).
- **Input identity (`INPUT_IDENTITY`):** [identity.py](identity.py) prints the runtime identity and `tested_state` = HEAD + one SHA-256. The hash covers:
  - the tracked diff and the untracked (not ignored) files of the whole work tree, except the project artifacts written after the gate (this plan folder's `*.md`, `.agent/context/`, `docs/execution/reflections/`, `docs/execution/metrics.md`, `docs/build-plan/`, `docs/BUILD_PLAN.md`). So the lockfiles (`uv.lock`, `ui/package-lock.json`, `mcp-server/package-lock.json`), the fixtures and this plan's scripts are all bound;
  - the runtime identity, observed live: the Python running it, `node --version`, the installed `electron` and `@playwright/test` versions, the `segoeui.ttf` SHA-256 and `ELECTRON_RUN_AS_NODE`.

  `--state-only` computes the same value. The gate records the state before and after it runs (§4), and each handoff's final full `evidence.v1` record carries it. H1-6b re-derives it live with `identity.py --state-only`, so any bound change refuses the old record and forces H1-2 again.
- **Evidence:** each receipt's exit code and decisive lines, pasted as `evidence.v1` in the handoffs.
- **D9:** yes; MEU state updates through `tools/meu_status.py` (H1-3).
