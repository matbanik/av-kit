---
project: "2026-10-14-capture-render-fidelity"
date: "2026-10-14"
source: "docs/build-plan/09-screenshot-capture.md#text-preview-baseline"
meus: ["MEU-82", "MEU-83", "MEU-84"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture render fidelity (Session 36)

> **Project:** `2026-10-14-capture-render-fidelity`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md`:
> - §Text preview baseline (`:706-715`, matrix 9.15, MEU-82)
> - §Arrow bake geometry (`:717-728`, matrix 9.16, MEU-83)
> - §Annotated file sync and Open file (`:730-740`, matrix 9.17, MEU-84)
> - §Annotation geometry (`:356-376`) and the MEU-59/60/66/67 tests as Local Canon
>
> **Grouping:** `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, Session 36 (`:126-131`), decisions D-1 to D-7 (`:215-221`).
> **Known issues:** `CAPTURE-TEXT-BG-PREVIEW-OFFSET` (`known-issues.yaml:1728`), `CAPTURE-BAKE-ARROW-THIN` (`:1241`), `CAPTURE-STALE-ANNOTATED-PATH` (`:1584`), `CAPTURE-OPEN-FILE-VARIANT` (`:1939`).
> **Status:** `draft`, Round 1. Under `plan_to_exec_gate: human`, execution starts only on the user's explicit chat message after the review approves.

## Goal

Three capture defects from the 2026-10-09 triage make the preview and the files disagree with what the user sees:

1. **MEU-82 — text preview baseline.** The bake places text with Pillow `anchor="la"` (top of the ascender line). The SVG preview uses `dominant-baseline="hanging"`, which Chromium puts above that line. In the viewport, the yellow plate therefore covers only the bottom of the glyphs, while the baked PNG is right (`CAPTURE-TEXT-BG-PREVIEW-OFFSET`). Fix: the preview text sits on the alphabetic baseline at `y + ascent(font_size)`. The ascent comes from the same Segoe UI metrics the bake uses (`SEGOE_ASCENT`).
2. **MEU-83 — arrow bake geometry.** The baked arrow is jagged (Pillow draws lines and polygons without anti-aliasing, `adapter.py:303-316`). Its flat-capped shaft also runs all the way to the tip, so the shaft corners poke out past the head, in both the bake and the preview (`CAPTURE-BAKE-ARROW-THIN`). Fix:
   - The shaft ends just inside the back of the head (`SHAFT_END`), in the bake and the preview alike.
   - The bake draws each arrow at 4× on a small tile and downscales it with LANCZOS (`BAKE_AA`).
   - The head is somewhat larger (`ARROW_HEAD`, D-12).
3. **MEU-84 — file and variant truth.**
   - `scan_inbox` drops rows whose original is gone, but it never re-checks `annotated_path` or `sidecar_path` (`CAPTURE-STALE-ANNOTATED-PATH`). Fix: it clears each one whose file is gone (`RECONCILE`).
   - Open file always opens the original, whatever the viewport shows (`CAPTURE-OPEN-FILE-VARIANT`). Fix: Open file opens the file the viewport shows, and Open folder reveals that same file (`VIEWED_FILE`, triage D-65, amending AC-39.12).

Order (grouping `:128-129`, one bake-fixture suite): MEU-82 first, MEU-83 second (both touch the render path, and MEU-83 reuses MEU-82's fixture tooling), MEU-84 third. The worktree baseline is the branch HEAD when execution starts; row 0 records it in `baseline.sha`. Planning started from `7861020` (origin/main). Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent (ls: No such file or directory, 2026-10-14); no headroom MCP or binary. Scope is the capture render path (CaptureViewport, capture-text-metrics, capture-arrow-head, bake adapter, services/capture.py scan_inbox, capture-commands), read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). It stops (S1) if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md` §Claude Code; `.agent/context/harness.local.md` §Claude Code, `:34-53`).
  - `native_shell: pwsh`. Every validation goes through `rtk proxy` with the receipt pattern `*> C:/Temp/av-kit/<receipt>.txt; $code=$LASTEXITCODE; Get-Content …; exit $code`.
  - `plan_to_exec_gate: human`. Reviewer `approved` does not start execution; the user's explicit chat message does.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every non-`shared` row keeps `compact_continue` as its fallback.
- **Cloud/local split: not used.** Mat's Windows host is both the driver and the target, so the gates are authoritative where they run. There is no `validate-task.sh`/`.ps1` and no `local-requests.md`. Commands are the PROFILE D6 argv (`.agent/docs/commands.md:190-210`) plus targeted file lists.
- **Working directory:** the worktree root `P:/av-kit/.claude/worktrees/s36-capture-render-fidelity` (`WT`). D6 lists `P:/av-kit` as its default cwd; this plan runs the same argv from `WT` (D-8). Row 0 runs `uv sync --frozen --all-packages` and `npm --prefix ui ci` in `WT`, because a fresh worktree `.venv` has no Pillow (planning observation 2026-10-14).
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`; `.agent/skills/cli-dispatch/SKILL.md`). The plan was authored by Claude, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable, the fallback is Mat (PROFILE B3/B4). Self-review is never allowed.
- **Never:** commit, push, upload, publish, or write to YouTube; author an `approved` verdict; send secrets to a provider.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-82` | `.agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-82-handoff.md` |
| `MEU-83` | `.agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-83-handoff.md` |
| `MEU-84` | `.agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-84-handoff.md` |

Plan-local tooling (project artifacts, not product): [session-gate.ps1](session-gate.ps1) (rows 8 and H1-2) and [identity.py](identity.py) (input identity, H1-6b).

Rolling reviews:

- `.agent/context/handoffs/2026-10-14-capture-render-fidelity-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-14-capture-render-fidelity-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Baseline, §Census; `baseline.sha` |
| WP-1 | MEU-82 TDD: ascent constants, preview baseline, bake fixture and pixel E2E (rows 2–3) | WP-0 | `shared` | tests + source; Red/Green receipts; `walkthrough.md` §MEU-82 |
| WP-2 | MEU-83 TDD: head, shaft end, tile AA bake (rows 4–5) | WP-1 | `compact_continue` | tests + source; `walkthrough.md` §MEU-83; compact, then re-read `task.md` and the walkthrough |
| WP-3 | MEU-84 TDD: reconcile, viewed file, E2E shell log (rows 6–7) | WP-2 | `compact_continue` | tests + source; `walkthrough.md` §MEU-84; compact, then re-read |
| WP-4 | Session gate and hub reconciliation (rows 8–9) | WP-3 | `shared` | gate receipts in `walkthrough.md` §Gate; `docs/build-plan/09…`, matrix, `docs/BUILD_PLAN.md` |
| WP-5 | H1 closeout, execution review, H2 | WP-4 | `compact_continue` | three handoffs, rolling review, reflection, metrics row |

---

## User Review Required

> [!IMPORTANT]
> These items are for the review loop and for the user's execution message. They are not a pause point.
>
> 1. **D-12 arrow head size (product preference).** Recommended: `ARROW_HEAD`, a longer and wider head than the current 4 / 0.40 (the D-12 brief compares the options). The head base becomes about 4.4× the stroke width (was about 3.1×). **Default if unanswered: the recommendation.** The user can reply "keep the head" in the execution message; the plan then keeps 4 / 0.40 and drops TA-1/TA-2 (the D-12 brief lists exactly what changes).
> 2. **`TEST_AMENDMENTS` TA-1 to TA-6.** Each one changes a test that pins the geometry this plan is told to change: the old head values, `hanging`, or the `<line>` end at the tip. The amendments are listed for the user in advance. Any other contradiction found by the census stops execution (S2).
> 3. **`E2E_SHELL_LOG` (D-17)** touches `ui/src/main/`. It records `openPath`/`showItemInFolder` targets only inside the existing `AVKIT_E2E=1` no-op branches, so the Electron test can see which file Open file asked for. Outside E2E, behaviour is byte-for-byte the same.
> 4. **Optional visual check.** At the commit gate, Mat may open a baked arrow and a text plate in an image viewer. This is non-blocking; the pixel tests are the gate.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once, here. ACs, task rows and tests refer to these names and never restate the values.

| Name | Definition | Source |
|---|---|---|
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the Files Modified rows below. In `adapter.py` only the arrow drawing (`ARROWHEAD_*`, `arrowhead_vertices`, new `arrow_shaft_end`, `_apply_arrow`) changes; `_apply_text`, `text_plate_box`, `_apply_rect`, `_apply_highlight` and `bake`'s format handling stay byte-identical. Row 8 proves it with `SCOPE_CHECK` (Verification Plan §5): a path allow-list over the diff against `baseline.sha`, plus an AST comparison of the frozen functions. | Spec 09:706-740; grouping `:128` |
| `SEGOE_UNITS` | `SEGOE_UI_UNITS_PER_EM = 2048`, `SEGOE_UI_ASCENDER = 2210`: the `head`/`hhea` values of `C:/Windows/Fonts/segoeui.ttf` (read with `struct`, 2026-10-14). | Research-backed D-10 |
| `SEGOE_ASCENT` | `segoeAscentPx(size)` reproduces FreeType's 26.6 ascent: `v = (SEGOE_UI_ASCENDER * size * 2048 + 0x8000) >> 16` (FT_MulFix of the ascender by the y scale `size*64*65536/2048`), then `ceil(v / 64)`. The input is `max(1, font_size)`. Equivalent closed form: `ceil(round_half_up(2210 * size / 32) / 64)`. A plain `ceil(size * 2210 / 2048)` is wrong at sizes 38, 177, 215 and 354. | Research-backed D-10; planning receipt R-1 |
| `GEOMETRY_FIXTURE` | One committed JSON file `ui/tests/e2e/fixtures/capture-geometry.json`, read by both Vitest and pytest: `segoe_ascent` maps a size to an ascent for sizes `[1, 8, 12, 16, 20, 24, 32, 38, 48, 64, 72, 96, 128, 177, 215, 354, 500]` → `[2, 9, 13, 18, 22, 26, 35, 41, 52, 70, 78, 104, 139, 191, 232, 382, 540]`; `arrows` lists `ARROW_CASES`. | Planning receipt R-1 (Pillow 12.3.0 `getmetrics()` equals these values for every size listed) |
| `TEXT_ANCHOR` | The preview `<text>` has `x = ann.x`, `y = ann.y + segoeAscentPx(ann.font_size)`, `text-anchor="start"` and `dominant-baseline="alphabetic"` (`SVG_DOMINANT_BASELINE`). The plate (`textBackgroundBox`), the text hit box, the body handle and the bake stay as they are, because they already use the `la` metrics. Worked example: `Hi` at `(10, 20)`, size 16 → text `y = 38`, plate `(10, 26, 15, 12)`, plate bottom 38. | Spec 09:712; triage D-52; D-11 |
| `TEXT_FIXTURE` | `tools/capture_bake_fixture.py` writes two committed PNGs under `ui/tests/e2e/fixtures/`: `capture-fidelity-original.png` (240×120 white RGB) and `capture-fidelity-annotated.png`, the real `CaptureAdapter.bake` of the original with `TEXT_FIXTURE_MARK` = text `"Hi"` at `(20, 30)`, size 32, colour `#000000`, `bg_color #FFD400`. A pytest compares the committed annotated PNG's decoded pixels with a fresh bake, so the fixture cannot go stale. | D-18 |
| `TEXT_PIXEL_ORACLE` | In the Electron app at the `ZOOM_1TO1` viewport transform, screenshot the viewport image box twice: the Original view (original PNG plus the SVG preview of `TEXT_FIXTURE_MARK`) and the Annotated view (the baked PNG). Decode both in the page through `createImageBitmap` and canvas `getImageData`, and map them to image pixels by the device pixel ratio. **Ink** is pixels with luma < 96. **Plate** is pixels within 40 of `#FFD400` per channel. Pass when (a) the ink bounding boxes of the two views agree within ±1 image px on all four sides, (b) the plate boxes agree within ±1 px, and (c) in each view the ink box lies inside the plate box, expanded by 1 px. | Spec 09:713 ("preview-vs-bake pixel comparison"); D-18 |
| `ZOOM_1TO1` | One image pixel is one CSS pixel: the MEU-66 zoom set to 100% (`capture-zoom` controls), and the image box located by its `data-testid`. If the 100% control is not reachable, use the fit transform and divide by its scale. The comparison is in image pixels either way. | Local Canon MEU-66 (09 §Viewport zoom) |
| `ARROW_HEAD` | `ARROWHEAD_LENGTH_FACTOR = 5`, `ARROWHEAD_ANGLE_RAD = 0.45`, `ARROWHEAD_MIN_PX = 10`, `head = max(ARROWHEAD_MIN_PX, ARROWHEAD_LENGTH_FACTOR * stroke_width)`. The vertex formula (`tip = to`, `left/right = to − head·(cos(θ ∓ angle), sin(θ ∓ angle))`) is unchanged. The values are the same in TS (`capture-arrow-head.ts`) and Python (`adapter.py`). | D-12 (default; product preference) |
| `ARROW_SHAFT_OVERLAP_PX` | `1`: how far the shaft runs past the head base toward the tip, so no background gap shows between them. | D-13 |
| `SHAFT_END` | `arrowShaftEnd(from, to, stroke)` / `arrow_shaft_end(...)`: with `L = |to − from|` and `u = (to − from)/L`, `back = head·cos(ARROWHEAD_ANGLE_RAD) − ARROW_SHAFT_OVERLAP_PX`. When `L == 0`, the shaft is `from→to` with no head (legacy, unchanged, 09:366). When `L ≤ back`, there is no shaft and only the head is drawn. Otherwise the shaft runs `from → to − u·back`. The preview `<line>` and the bake shaft use this end. The `<g data-annotation-type="arrow">` keeps `x1/y1/x2/y2 = from/to`. | Spec 09:721; Human-approved 2026-10-03 (Mat), triage D-53; D-13, D-19 |
| `SHAFT_INSIDE_HEAD` | For every stroke 1–64 and every `ARROW_CASES` direction, both flat-cap corners of the shaft end lie inside the head triangle. Proof: they need `stroke/2 ≤ head·sin(a) − overlap·tan(a)`, and with `head ≥ 5·stroke` and `a = 0.45` the right side is ≥ `2.17·stroke − 0.49`. Tested as a property in TS and Python. | D-13 |
| `ARROW_CASES` | In `GEOMETRY_FIXTURE.arrows`, each case is `{from, to, stroke, head, left, right, shaft_end}`. The cases: horizontal `(0,0)→(100,0)` s3, which must give `head 15`, `left (86.49329346470985, 6.524483011668454)`, `right (86.49329346470985, -6.524483011668454)`, `shaft_end (87.49329346470985, 0)`; plus diagonal `(700,375)→(750,400)` s4, vertical `(50,10)→(50,90)` s1, short `(0,0)→(8,0)` s4 (`shaft_end null`), and zero-length `(5,5)→(5,5)` s3 (`head null`). The other expected values are computed by the Python implementation at row 4 and pinned in the JSON. Both languages must reproduce them to `1e-9`. | D-12, D-13 |
| `BAKE_AA` | `_apply_arrow` draws each arrow through a supersampled coverage mask, in `PIXEL_CENTRE` coordinates: (1) the tile is the bounding box of `from`, the shaft end and the three head vertices, padded by `stroke/2 + 4` px (the `AA_LIMITS` halo plus 1, so the LANCZOS spread is never cut at the tile edge), rounded outward (`floor` of the minimum, `ceil` of the maximum `+ 1`, end-exclusive) and clipped to the image; (2) an `L`-mode mask of `4 × tile` size; (3) `draw.line` and `draw.polygon` on the mask in white, with every point mapped `big = 4·(p − tile_origin) + 1.5` (the centre of the pixel's 4×4 block) and `width = 4·max(1, stroke)`; (4) `mask.resize(tile_size, Image.Resampling.LANCZOS)`; (5) the solid mark colour is composited into the tile through that mask. The shaft end comes from a call to the module-level `arrow_shaft_end`, which AC-83.5's negative control patches. Pixels outside the tile are never written. A zero-area tile (an arrow fully outside the image) draws nothing. `SUPERSAMPLE = 4`. Planning receipt R-3 transcribes these steps literally. | Spec 09:722 (4× + LANCZOS); Research-backed D-14; review F1 |
| `PIXEL_CENTRE` | The pixel with index `(x, y)` is sampled at mark coordinate `(x, y)`, never `(x + 0.5, y + 0.5)`: Pillow puts an integer coordinate on a pixel centre (R-3: `polygon` over `10..20` fills columns 10 to 20, and a width-1 `line` at `y = 20` fills row 20). Every arrow oracle measures its distances from `(x, y)`. | Planning receipt R-3; review F1 |
| `AA_LIMITS` | `AA_HALO_PX = 3`: the LANCZOS support at a 4× downscale, in output pixels, so coverage may legitimately reach this far past an edge. `AA_CHANNEL_TOL = 8`: "equals" a colour means within 8 on every channel. **Coverage** of a pixel is `(255 − c)/255` on a channel `c` that is 0 in the mark colour, composited on white. | Planning receipt R-3 |
| `ARROW_TIP_ORACLE` | Bake a horizontal arrow `(20,60)→(200,60)`, stroke 12, `#FF0000`, on a white 240×120 image. Over the pixels beyond the head base (`x > 200 − head·cos(a)`, `head` and `a` from `ARROW_HEAD`), with distances from the head triangle taken at `PIXEL_CENTRE`: (a) **no leak**: no pixel more than 1 px outside the triangle has coverage ≥ 0.5; (b) **halo bound**: every pixel more than `AA_HALO_PX` outside the triangle equals white. R-3: the literal `BAKE_AA` gives 0 leak pixels and a halo maximum deviation of 0 (4 at 1 px). With the shaft drawn to the tip it gives 58 leak pixels, and the baseline code gives 53. | Spec 09:724 ("no shaft pixels beyond the head base"); review F1 |
| `EDGE_ORACLE` | Bake a diagonal arrow `(20,100)→(200,20)`, stroke 6, `#0000FF`, on white. Take the pixels whose projection on the shaft lies between `stroke/2 + 3` past `from` and `head + 3` before `to`, with `dist` their distance from the centre line at `PIXEL_CENTRE`. (a) At least 40% of the pixels with `|dist − stroke/2| ≤ 1` are blends: neither white nor the mark colour. (b) Every pixel with `dist ≤ stroke/2 − 1.5` equals the mark colour. (c) Every pixel outside the tile is byte-equal to the original. R-3: the literal `BAKE_AA` gives 641 edge pixels, a blend fraction of 0.5117 and an interior maximum deviation of 4. The baseline code gives a blend fraction of 0.0. | Spec 09:724 ("edge smoothness check"); review F1 |
| `RECONCILE` | In `scan_inbox`'s final loop (`services/capture.py:313-318`), under the existing `CAPTURE_FILE_LOCK` and uow: a shot whose original is gone is deleted (unchanged). Otherwise, if `annotated_path` is set and not `is_file()`, it becomes `None`; if `sidecar_path` is set and not `is_file()`, it becomes `None`. The two fields are checked independently. The row is saved (with `updated_at = now`) only when a field changed. | Spec 09:736; triage D-55; D-15 |
| `VIEWED_FILE` | `viewedFilePath(variant, shot)` (new pure helper, `capture-viewed-file.ts`) returns `shot.annotated_path` when `variant === 'annotated'` and `annotated_path` is a non-empty string; otherwise `shot.original_path`; `null` with no shot. `CapturePage` passes it to `setCaptureSelection` as `viewedPath`. `openCaptureFile()` opens it, and `openCaptureFolder()` reveals it (`showItemInFolder`), falling back to `inboxDir` only with no selection. The palette's `open_folder` uses the same path. | Spec 09:737; Human-approved 2026-10-09 triage D-65 (amends AC-39.12); D-16 |
| `E2E_SHELL_LOG` | A new `ui/src/main/e2e-shell.ts` exports `e2eShellLog` (an array of `{op: 'openPath' \| 'showItemInFolder', target}`) and `recordE2eShell(op, target)`. The existing `AVKIT_E2E === '1'` branches of `openPath`/`showItemInFolder` (`ui/src/main/index.ts:378-389`) call `recordE2eShell` and still return without touching `shell`. The log is exposed as `globalThis.__AVKIT_E2E_SHELL_LOG__` only when `AVKIT_E2E === '1'`. The Electron test reads it with `app.evaluate`. | D-17; precedent `ui/src/main/index.ts:372-389` (E2E branches) |
| `TEST_AMENDMENTS` | **TA-1** `ui/tests/unit/capture-arrow-head.test.ts:6-18` (AC-59.2): pinned head 12 / angle 0.4 → `ARROW_HEAD` values and `ARROW_CASES`. **TA-2** `tests/unit/test_capture_adapter.py:438-456` (`test_ac_59_2_shared_arrowhead_vertices`): the same. **TA-3** `ui/tests/unit/capture-text-metrics.test.ts:6-9` (AC-59.19): `SVG_DOMINANT_BASELINE` `'hanging'` → `'alphabetic'`. **TA-4** `ui/tests/unit/capture-page.behavior.test.ts:1834-1875` (AC-59.19): `dominant-baseline` `'hanging'` → `'alphabetic'` and text `y` → `ann.y + ascent`; the plate assertions (x10, y26, w15, h12) stay. **TA-5** `capture-page.behavior.test.ts:1741-1745` (AC-66.11): read `x2/y2` from the arrow `<g>` instead of the `<line>`; the values (`'750'`, `'400'`) stay. **TA-6** `ui/tests/e2e/capture-inbox.test.ts:1165-1169` (AC-66.14): the same change, with values `'1260'`, `'830'`. **TA-7** `capture-page.behavior.test.ts:1331-1332` (AC-65.3): read the stroke from the arrow head instead of the `<line>`, asserting that the head length (tip→left vertex of the `<polygon>` points) is 35 (`ARROW_HEAD` factor 5 × stroke 7) to `1e-9`. The drag (1,1)→(6,6) image px is shorter than the shaft back 30.52 at stroke 7, so `SHAFT_END` renders no `<line>`; the rest of the test stays (D-20, A-1). Amendments change only those assertions; every other line in those tests stays. If D-12 is answered "keep the head", TA-1/TA-2 are dropped. | D-12, D-19, D-20 (Human-approved 2026-10-16, A-1); Spec 09:366-367 (amended by row 9) |
| `CENSUS_PATTERNS` | Row 1 greps `ui/tests` and `tests` for `ARROWHEAD_`, `arrowheadVertices`, `arrowhead_vertices`, `arrowHeadPoints`, `hanging`, `dominant-baseline`, `dominantBaseline`, `SVG_DOMINANT_BASELINE`, `x2`, `y2` near `line`, `annotated_path`, `sidecar_path`, `scan_inbox`, `openPath`, `showItemInFolder`, `capture-open-file`, `capture-open-folder` and `_apply_arrow`. Each hit is dispositioned: `TA-n`, `unaffected` with the reason, or `new-contradiction`, which triggers S2. | Local Canon (Session 30 census) |
| `NEW_TESTIDS` | None. The plan adds no element; `capture-open-file`, `capture-open-folder`, `capture-view-original`, `capture-view-annotated` and `capture-annotation` keep their ids. | Local Canon |

### MEU-82 — `capture-text-baseline`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Annotation DTO `text` mark (renderer) | `annotationSchema` (`capture-annotate.ts:14-51`) | `font_size` int > 0; `x`, `y` int; `text` 1–500 | `.strict()`; unchanged |
| Annotation DTO (REST `POST /captures/{id}/annotate`) | domain `TextAnnotation` (`domain/capture.py:129-215`) + API schema | unchanged | unchanged (`extra="forbid"`) |
| `GEOMETRY_FIXTURE` JSON (test input only) | the two tests that read it | keys `segoe_ascent`, `arrows`; numbers only | a missing key fails the test |

No boundary changes. The fix is in rendering only.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-82.1 | unit | `segoeAscentPx(size)` equals `GEOMETRY_FIXTURE.segoe_ascent` for every listed size. `SEGOE_UNITS` are exported with their values. | Spec 09:713 ("unit tests for the metric constants"); D-10 | The fixture includes 38, 177, 215 and 354, where `Math.ceil(size*2210/2048)` is off by one; a test case checks that this naive formula differs at 38 |
| AC-82.2 | unit | pytest: for every `GEOMETRY_FIXTURE.segoe_ascent` size, Pillow's `ImageFont.truetype(segoeui.ttf, size).getmetrics()[0]` equals the fixture. `textbbox((x, y), "Hi", anchor="la")` bottom minus `textbbox((x, y), "Hi", anchor="ls")` bottom equals the ascent, so the baseline is at `y + ascent`. | Spec 09:712 ("the same Segoe metrics the bake uses"); D-10 | A fixture value edited by one (in a parametrised self-check of the comparator) fails |
| AC-82.3 | unit | `SVG_DOMINANT_BASELINE === 'alphabetic'`; `svgTextBaselineY({ y, font_size })` returns `y + segoeAscentPx(font_size)` (TA-3). | Spec 09:712; D-11 | `'hanging'` fails |
| AC-82.4 | integration | CapturePage behaviour (Vitest, rendered page, mark loaded through the detail fetch): a `Hi` mark at `(10, 20)`, size 16, with a plate renders `<text y="38" dominant-baseline="alphabetic">` and the plate rect `(10, 26, 15, 12)` (TA-4). Clicking inside the plate still selects the mark (hit test unchanged). | Spec 09:712 ("hit-test and selection boxes follow"); `TEXT_ANCHOR` | The baseline code renders `y="20"` and fails |
| AC-82.5 | integration | pytest: the committed `capture-fidelity-annotated.png` decodes to exactly the pixels of a fresh `CaptureAdapter.bake(capture-fidelity-original.png, [TEXT_FIXTURE_MARK])`, and the original is 240×120 all-white RGB. | D-18 | Baking the mark at `y + 1` gives different pixels (the test asserts this, so the comparator can detect a change) |
| AC-82.6 | integration | Electron: `TEXT_PIXEL_ORACLE` passes for `TEXT_FIXTURE_MARK`. The seam serves `capture-fidelity-original.png` for `variant=original` and `capture-fidelity-annotated.png` for `variant=annotated`, and the shot detail returns the mark. | Spec 09:713 ("a preview-vs-bake pixel comparison for a text mark with a plate"); triage D-52 | Red: on the baseline code the preview ink box sits above the bake's by more than 1 px (row 2 Red receipt) |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Baseline anchor | Spec | 09:712: alphabetic baseline at `y + ascent(font_size)` |
| Ascent value | Research-backed | D-10: FreeType 26.6 rounding (`SEGOE_ASCENT`), checked against Pillow for every fixture size |
| Plate and hit box | Local Canon | Unchanged; MEU-59 `textBackgroundBox` already uses the `la` table (`capture-text-metrics.ts`) |
| Pixel comparison method | Research-backed / Local Canon | D-18: committed real-bake fixture plus an in-page canvas decode; no new dependency (09:375) |
| Arial/default fallback metrics | Spec | Out of scope (below) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-segoe-metrics.ts` | modify | `SEGOE_UNITS` constants |
| `ui/src/renderer/src/features/capture/capture-text-metrics.ts` | modify | `SVG_DOMINANT_BASELINE = 'alphabetic'`; `segoeAscentPx`; `svgTextBaselineY` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | text `y` from `svgTextBaselineY` (also MEU-83) |
| `tools/capture_bake_fixture.py` | new | `TEXT_FIXTURE` writer (`--out DIR`); reused by MEU-83 tests for arrow helpers |
| `ui/tests/e2e/fixtures/capture-geometry.json` | new | `GEOMETRY_FIXTURE` |
| `ui/tests/e2e/fixtures/capture-fidelity-original.png`, `capture-fidelity-annotated.png` | new | `TEXT_FIXTURE` PNGs |
| `ui/tests/unit/capture-text-metrics.test.ts` | modify | AC-82.1, AC-82.3 (TA-3) |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-82.4 (TA-4) |
| `tests/unit/test_capture_text_metrics.py` | new | AC-82.2 |
| `tests/unit/test_capture_bake_fixture.py` | new | AC-82.5 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-82.6 |

### MEU-83 — `capture-arrow-geometry`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Arrow mark (renderer) | `annotationSchema` (`capture-annotate.ts`) | `from`/`to` int pairs; `stroke_width` int > 0 | `.strict()`; unchanged |
| Arrow mark (REST/domain) | `ArrowAnnotation` (`domain/capture.py`) | int type checks only; no positive bound (the adapter uses `max(1, stroke)`) | unchanged |

No boundary changes.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-83.1 | unit | TS: `ARROW_HEAD` and `ARROW_SHAFT_OVERLAP_PX` constants; `arrowheadVertices` and `arrowShaftEnd` reproduce every `ARROW_CASES` entry to `1e-9`, including `shaft_end: null` for the short case and no head for the zero-length case (TA-1). | Spec 09:721, 09:723; D-12, D-13 | `shaft_end = to` (baseline code) fails the horizontal case |
| AC-83.2 | unit | Python: `ARROWHEAD_*`, `ARROW_SHAFT_OVERLAP_PX`, `arrowhead_vertices` and `arrow_shaft_end` reproduce the same `ARROW_CASES` (TA-2). | Spec 09:721 ("in bake and preview alike") | The same as AC-83.1 |
| AC-83.3 | unit | `SHAFT_INSIDE_HEAD` property, in TS and in Python. | D-13 | With the end at the tip, the corners fall outside (asserted) |
| AC-83.4 | integration | CapturePage behaviour: for an arrow mark, the `<g>` keeps `x1/y1/x2/y2 = from/to` (TA-5); the `<line>` ends at `arrowShaftEnd`; the `<polygon>` points equal `arrowHeadPoints`. The short case renders no `<line>`, and the zero-length case renders a `<line>` and no `<polygon>`. Electron AC-66.14 reads the `<g>` (TA-6). | Spec 09:721; D-19 | The baseline `<line>` x2 equals `to.x` and fails |
| AC-83.5 | integration | pytest, real adapter: `ARROW_TIP_ORACLE`. | Spec 09:724 | Red on the baseline code (53 leak pixels in R-3). In Green, the same oracle on a bake with `arrow_shaft_end` monkeypatched to return `to` must fail (the negative control; 58 leak pixels in R-3) |
| AC-83.6 | integration | pytest, real adapter: `EDGE_ORACLE`. | Spec 09:722, 09:724; D-14 | Red on the baseline code (blend fraction 0.0 in R-3) |
| AC-83.7 | integration | pytest, real adapter: an arrow whose head runs past the image edge, `(20,60)→(119,60)` stroke 3 on a white 120×120 image, bakes without error and writes only inside the clipped tile. The axis pixel `round(head/2)` px behind the tip, `(111, 60)`, equals the mark colour. The tip column is not asserted: it is the triangle's zero-width apex (coverage 0.16 in R-3, 1.0 from 2 px back). An arrow tile wholly outside the image (only reachable through the domain, which has no bounds) bakes to the original pixels. | D-14; review F1 | An unclipped tile raises or writes out of bounds |
| AC-83.8 | unit | `_apply_arrow` source still calls `draw.line` and `draw.polygon` (the AC-35.13 source check stays green without amendment). It uses `Image.Resampling.LANCZOS` and `SUPERSAMPLE`, and never creates an image of the full canvas size × `SUPERSAMPLE`. | Spec 09:722; Local Canon AC-35.13 (`test_capture_adapter.py:389`) | A full-canvas supersample fails the size spy |
| AC-83.9 | integration | CapturePage behaviour: the arrow head `<polygon>` has `stroke="none"`, so it no longer inherits the `<g>`'s `stroke={color}` as a 1 px outline the bake does not draw. The `<g>` keeps `stroke` (the colour tests read it). | Human-approved 2026-10-16 D-21 (A-2); Spec 09:721 ("in bake and preview alike") | The baseline `<polygon>` has no `stroke` attribute and fails |

The flatten byte oracle (AC-67.1) bakes its expected image through the same adapter, so it follows the new drawing without change. Row 1's census confirms this.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Shaft end | Spec / Human-approved | 09:721 and Mat 2026-10-03: `tip − head·cos(angle)`, small overlap; D-13 sets the overlap to 1 px |
| Anti-aliasing method | Spec / Research-backed | 09:722 (4×, LANCZOS); D-14 tiles the supersample (a full 4K canvas at 4× would be about 530 MB of RGBA) |
| Head length/angle | Spec delegates to the plan | 09:723; D-12 brief (product preference, default `ARROW_HEAD`) |
| Preview arrow AA | Local Canon | Chromium already anti-aliases SVG; only the shaft end changes |
| Hit test | Local Canon | Unchanged: `hitArrowBody` tests the `from→to` segment (a superset of the shorter shaft) plus the head triangle |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-arrow-head.ts` | modify | `ARROW_HEAD`, `ARROW_SHAFT_OVERLAP_PX`, `arrowShaftEnd` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `<line>` to `SHAFT_END`; no `<line>` for the short case; head `<polygon>` `stroke="none"` (D-21) |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modify | `ARROWHEAD_*`, `ARROW_SHAFT_OVERLAP_PX`, `SUPERSAMPLE`, `arrow_shaft_end`, `_apply_arrow` through `BAKE_AA` |
| `ui/tests/e2e/fixtures/capture-geometry.json` | modify | `ARROW_CASES` |
| `ui/tests/unit/capture-arrow-head.test.ts` | modify | AC-83.1, AC-83.3 (TA-1) |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-83.4, AC-83.9 (TA-5, TA-7) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | TA-6 |
| `tests/unit/test_capture_adapter.py` | modify | AC-83.2, AC-83.3, AC-83.5–83.8 (TA-2) |

### MEU-84 — `capture-file-variant-sync`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| REST `GET /captures` items | `CaptureShotOut` (`schemas/captures.py:118-119`) | `annotated_path`, `sidecar_path`: `str \| None`; unchanged shape | unchanged |
| IPC `openPath` / `showItemInFolder` | preload `window.api` | an absolute path string | unchanged |
| `E2E_SHELL_LOG` | `ui/src/main/e2e-shell.ts` | `op` ∈ {`openPath`, `showItemInFolder`}; `target` string | E2E-only; not reachable outside `AVKIT_E2E=1` |

No REST shape changes, so there is no OpenAPI drift (row 8 still runs `--check`).

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-84.1 | unit | Service (`tests/unit/test_capture_service.py`, real files in `tmp_path`): `RECONCILE`. (a) Annotated file deleted, sidecar present → `annotated_path` None, `sidecar_path` kept. (b) Sidecar deleted, annotated present → the reverse. (c) Both deleted → both None. (d) Both present → the row is unchanged and not re-saved (`updated_at` unchanged). (e) Original deleted → the row is deleted (existing behaviour). | Spec 09:736; D-15 | (d) catches an implementation that re-saves every row; (a) catches clearing both fields together |
| AC-84.2 | integration | API e2e (`tests/e2e/test_api_captures.py`): annotate a shot, delete the annotated file on disk, then `GET /captures` → that item's `annotated_path` is null and `sidecar_path` is still set; `GET /captures/{id}` still returns the sidecar's annotations; `GET /captures/{id}/image?variant=annotated` → 404. | Spec 09:736 | Before the deletion, the same calls return the annotated path and 200 |
| AC-84.3 | unit | `viewedFilePath`: (`annotated`, shot with annotated path) → the annotated path; (`original`, the same shot) → the original; (`annotated`, `annotated_path` null) → the original; (`annotated`, `''`) → the original; no shot → null. | Spec 09:737-738 ("the fallback when the annotated copy is missing"); D-16 | Returning `annotated_path` unconditionally fails the null case |
| AC-84.4 | integration | CapturePage behaviour (Vitest with `window.api` spies, userEvent per G37): Original view → Open file calls `openPath(original_path)` and Open folder calls `showItemInFolder(original_path)`. Annotated view → both use `annotated_path`. The list refetches with `annotated_path: null` while the Annotated view is still chosen → both fall back to `original_path`. The palette `open_folder` command follows the same path. | Spec 09:737 (amends AC-39.12); triage D-65 | The baseline code passes `original_path` in the Annotated view and fails |
| AC-84.5 | integration | Electron (`capture-inbox.test.ts`): a seam shot with `annotated_path`; click `capture-view-annotated`, then `capture-open-file` and `capture-open-folder`; `__AVKIT_E2E_SHELL_LOG__` ends with `openPath(annotated_path)` and `showItemInFolder(annotated_path)`. After `capture-view-original`, the next two entries name `original_path`. | Spec 09:737; E2 (emerging-standards `:1167`) | Red on the baseline code (the log names the original) |
| AC-84.6 | unit | `e2e-shell.ts`: `recordE2eShell` appends in order; the `index.ts` E2E branches call it and never call `shell`; with `AVKIT_E2E` unset, `__AVKIT_E2E_SHELL_LOG__` is not defined (source check plus a module test). | D-17 | A branch that also calls `shell.openPath` fails the source check |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| What reconcile clears | Spec | 09:736: `annotated_path` and `sidecar_path` whose files are gone |
| Per-field vs both-together | Local Canon | D-15: per field, because `load_shot_annotations` reads the sidecar by name, so a sidecar with no annotated copy still holds marks |
| Where reconcile runs | Spec | 09:736 names `scan_inbox`; `list_shots` calls it on `GET /captures` |
| Open file / Open folder target | Human-approved | Triage D-65 |
| Fallback | Spec | 09:738 "the fallback when the annotated copy is missing" → the original (D-16) |
| How E2E sees the target | Local Canon | D-17: the main-process E2E branch logs; renderer `window.api` is frozen by `contextBridge` |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/services/capture.py` | modify | `RECONCILE` in `scan_inbox` |
| `ui/src/renderer/src/features/capture/capture-viewed-file.ts` | new | `viewedFilePath` |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modify | `viewedPath` in the selection; `openCaptureFile`/`openCaptureFolder` use it |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | pass `viewedPath` from `viewVariant` + `selected` |
| `ui/src/main/e2e-shell.ts` | new | `E2E_SHELL_LOG` |
| `ui/src/main/index.ts` | modify | the two E2E branches call `recordE2eShell`; expose the log under `AVKIT_E2E=1` |
| `tests/unit/test_capture_service.py` | modify | AC-84.1 |
| `tests/e2e/test_api_captures.py` | modify | AC-84.2 |
| `ui/tests/unit/capture-viewed-file.test.ts` | new | AC-84.3 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-84.4 |
| `ui/tests/unit/capture-main.behavior.test.ts` | modify | AC-84.6 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-84.5 |

### Hub and state files (row 9)

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | modify | §Annotation geometry Arrow row (`:366`): `ARROW_HEAD` values, `SHAFT_END`, 4× tile AA ("Session 36 plan D-12, D-13, D-14"). Text row (`:367`): `dominant-baseline="alphabetic"` at `y + ascent` ("Session 36 plan D-11"). §Arrow bake geometry Head row (`:723`): the chosen values |
| `docs/build-plan/build-priority-matrix.md` | modify | add rows 9.15–9.17 after the last 9.x row, if absent, in the `9.12` row format |
| `docs/BUILD_PLAN.md` | modify | Phase 9 status line (`:53`): "MEU-82–84 bound to capture-render-fidelity"; AUTOGEN regions only through `meu_status.py render` |
| `.agent/context/meu-status.yaml` | modify | MEU-82/83/84 `execution_plan` + status (H1-3) |
| `.agent/context/meu-registry.md` | generated | written by `meu_status.py render` (H1-3, H2-2); never hand-edited |
| `.agent/context/current-focus.md` | modify | the current focus names Session 36 (H1-3) |
| `.agent/context/known-issues.yaml` | modify | the four issues → `resolved` with the handoff link, after H1-7b approval (H2) |
| `.agent/context/known-issues.md` | generated | written by `issue_triage.py render` after the issue update (H2-2); never hand-edited |
| `docs/build-plan/gui-actions-index.md` | verify only | `:71-72` stay accurate (same ids, same IPC); row 9 re-runs `gui-actions-audit.test.ts` |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Ascent for the Arial/default font fallback | out-of-scope | — | 09:712 binds the anchor to "the same Segoe metrics the bake uses"; the MEU-59 renderer table is Segoe-only (`capture-segoe-metrics.ts`, `SEGOE_LA_BASE_SIZE`) |
| Anti-aliasing text, box or highlight marks in the bake | out-of-scope | — | 09:722 scopes the 4× rule to "Arrow marks"; 09:373 "does not retune rect inset or highlight `width-1` raster edges" |
| Auto-switching the view to Original when the annotated copy vanishes | out-of-scope | — | 09:737-738 define the target and "the fallback", not a view change |
| Reconcile in `get_shot` or from the Electron watcher | out-of-scope | — | 09:736 names `scan_inbox`; `list_shots` already runs it on every `GET /captures` |
| Curved arrows, other arrowhead styles | out-of-scope | — | 09 §Named deferrals (`:825-841`); 09:358 |
| Icon-button conversion of Open file / Open folder | deferred | MEU-81 | 09:697 (MEU-81, Session 34 `capture-chrome`, grouping `:112`). The testids stay, so the conversion keeps working; recorded as a merge risk (D-9) |
| A named-colour or size control change for marks | deferred | MEU-85, MEU-86 | Session 37 `capture-editor-options` (grouping `:133-137`) |

## BUILD_PLAN.md Audit

This project edits the D3 hub in task row 9 only (§Hub and state files). The validation is exact:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s36-state-render.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s36-state-render.txt; exit $code
```

```powershell
rtk proxy rg -n "MEU-82|MEU-83|MEU-84|9\.15|9\.16|9\.17|alphabetic|ARROW_SHAFT_OVERLAP|capture-render-fidelity" docs/BUILD_PLAN.md docs/build-plan/build-priority-matrix.md docs/build-plan/09-screenshot-capture.md *> C:/Temp/av-kit/s36-hub-rg.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s36-hub-rg.txt; exit $code
```

Row 9's deliverable is that the `rg` receipt shows each edit (matrix rows 9.15–9.17, the Phase 9 line, the 09 Arrow/Text rows and the Head row), and that `render --check` exits 0.

## Verification Plan

All commands run from `WT` in `pwsh`, after `$env:ELECTRON_RUN_AS_NODE=$null` for any Electron step. Receipts go to `C:/Temp/av-kit/s36-*.txt`. The ids are PROFILE D6's (`.agent/docs/commands.md:190-210`); targeted runs are those argv with a file list.

### 1. Prerequisites and baseline (row 0)

- `uv sync --frozen --all-packages`, `npm --prefix ui ci`.
- `git rev-parse HEAD > docs/execution/plans/2026-10-14-capture-render-fidelity/baseline.sha`.
- The baseline receipts: `py-tests`, `ui-tests`, `ui-build`, then `ui-electron` over `capture-inbox.test.ts`. The baseline failed sets are recorded in `walkthrough.md` §Baseline. A test failing at baseline is never counted as a regression, and a test passing at baseline that fails later is.

### 2. Red (rows 2, 4, 6)

Each MEU's new and amended tests are written first. They must fail by assertion (not by collection or import error, except for the declared new modules: `capture-viewed-file.ts`, `e2e-shell.ts`, `tools/capture_bake_fixture.py`, `arrow_shaft_end`, `segoeAscentPx`, `svgTextBaselineY`, `arrowShaftEnd`). The Red receipts are pasted in the walkthrough.

`RED_PROOF`: [red-check.py](red-check.py) decides each Red. Each Red command writes its child exit code to `<receipt>.exit` straight after `$code=$LASTEXITCODE`. The checker requires:

- a non-zero exit;
- a failing-run summary;
- a *diagnostic* line that attributes the failure: a pytest `E` line, `AssertionError:`, `Error: expect(`, or an error line naming a declared-new export;
- no setup failure: Electron launch, a test or action timeout, a refused connection, or an unrelated load or collection error.

Source-context and test-title lines never count. `red-check.py --selftest` runs nine receipt fixtures, four positive and five negative (R-5).

### 3. Targeted Green (rows 3, 5, 7)

```powershell
rtk proxy uv run pytest tests/unit/test_capture_adapter.py tests/unit/test_capture_text_metrics.py tests/unit/test_capture_bake_fixture.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py tests/e2e/test_api_capture_flatten.py -q --tb=short *> C:/Temp/av-kit/s36-py-targeted.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s36-py-targeted.txt | Select-Object -Last 25; exit $code
```

```powershell
rtk proxy npm --prefix ui run test -- tests/unit/capture-arrow-head.test.ts tests/unit/capture-text-metrics.test.ts tests/unit/capture-viewed-file.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/capture-page.test.ts tests/unit/capture-hit-test.test.ts tests/unit/capture-main.behavior.test.ts tests/unit/capture-zoom.test.ts tests/unit/capture-flatten.test.ts tests/unit/gui-actions-audit.test.ts *> C:/Temp/av-kit/s36-ui-targeted.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s36-ui-targeted.txt | Select-Object -Last 25; exit $code
```

```powershell
$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s36-ui-build.txt; if ($LASTEXITCODE -ne 0) { Get-Content C:/Temp/av-kit/s36-ui-build.txt | Select-Object -Last 25; exit $LASTEXITCODE }; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts *> C:/Temp/av-kit/s36-e2e-capture.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s36-e2e-capture.txt | Select-Object -Last 30; exit $code
```

### 4. Session gate (rows 8, H1-2): `session-gate.ps1`

The plan-local [session-gate.ps1](session-gate.ps1) runs in `pwsh` from `WT`. It writes one receipt per step (`C:/Temp/av-kit/s36-D6-<id>.txt`) and prints `<id> stage=<stage> exit=<n>` and the receipt tail. It is fail-fast in stage order: after the first non-zero step, every later step is printed as `not_run` (D6: a static failure stops targeted and full). The steps, in order:

1. `identity-before`: `INPUT_IDENTITY` (§Validation stage contract).
2. **Static:** `py-types`, `py-lint`, `py-lint-tools` (`ruff check tools/capture_bake_fixture.py`, the new fixture writer), `ui-types`, `ui-lint`, `task-contract`, then `scope-ast` and `scope-paths` (`SCOPE_CHECK`, §5). The D6 argv are exactly as in `.agent/docs/commands.md:190-210`.
3. **Full:** `py-tests`, `ui-tests`, `ui-build`, `openapi`, `state-render`.
4. **Runtime:** `ui-electron` (the full Electron suite), then `e2e-repeat`: `test:e2e -- tests/e2e/capture-inbox.test.ts --grep "AC-82.6|AC-84.5" --repeat-each=10`. Any flake is a defect (S6).
5. `identity-npm` (the installed Electron and Playwright tree), then `identity-after`. The gate fails when `tested_state` differs between `identity-before` and `identity-after`, because an input changed while it ran.

The row's command is `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-render-fidelity/session-gate.ps1`, with the receipt pattern (task row 8).

### 5. `SCOPE_CHECK` (row 8)

- **`scope-ast`:** the adapter functions that `PRODUCT_SCOPE` freezes (`text_plate_box`, `_color_rgb`, `_load_font`, `_apply`, `_apply_text`, `_apply_rect`, `_apply_highlight`, `bake`) have the same `ast.dump` at `baseline.sha` and in the working tree.
- **`scope-paths`:** every path in `git diff --name-only <baseline>` plus the untracked files is a Files Modified row (product, tool, fixture, test, hub and state files), or one of this project's artifacts (this plan folder, the handoffs, the reflection, `docs/execution/metrics.md`). The allow-list in the script is the union of the Files Modified tables; changing either one means changing both.

### 6. OpenAPI drift (G8)

No file under `packages/api/` changes (`PRODUCT_SCOPE`). The `openapi` D6 check in §4 must still pass. If it reports drift, that is a scope defect: stop (S5).

### 7. Closeout (H1, H2)

These are the template commands with this project's paths. `validate_closeout_artifacts.py` is run per handoff (three runs: `--handoff` + `--plan`, then `--ac-coverage-only`), plus `durable_evidence.py --require-full`, the review-state parsers, the reflection validator with `--decision-source` for the plan, the three handoffs, the grouping file and `.agent/context/known-issues.yaml`, with `--decision-issue` for each of the four issue ids, and `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped (`docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent; recorded `gui-refs-not-shipped`). The plan creates no element. It changes two existing elements' behaviour and two SVG marks' geometry:

| Element | Change | Standard | E2E |
|---|---|---|---|
| `capture-open-file` | target follows `VIEWED_FILE` | E2 (`emerging-standards.md:1167`) | AC-84.5 |
| `capture-open-folder` | target follows `VIEWED_FILE` | E2 | AC-84.5 |
| text mark `<text>` (output) | baseline (`TEXT_ANCHOR`) | E2 | AC-82.6 |
| arrow mark `<line>` (output) | shaft end (`SHAFT_END`) | E2 | AC-66.14 via TA-6 |

G36 (no silent test guards): the pixel and shell-log tests assert, they never `skip` on a missing font or log. G37: behaviour tests use `userEvent`. No G30–G35 surface changes.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a graph directory, MEU-39/59/67 not `approved`, or MEU-82/83/84 not `pending` | Stop. Re-run the context-tool gate with the human, or report. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` | Stop for the human with a Decision Brief naming the test and the smallest amendment. No test edit. |
| S3 | `red-check.py` refuses a Red receipt (`RED_PROOF`, §2): the exit was 0, there is no attributed diagnostic line, or there is a setup failure | Fix the test setup only, then re-prove Red. |
| S4 | `TEXT_PIXEL_ORACLE` cannot pass within ±1 px after the fix, because Chromium's Segoe raster differs from FreeType by more than that | Stop for a Decision Brief with both ink boxes (the tolerance is a fidelity contract, not a tuning knob). |
| S5 | `SCOPE_CHECK` or `openapi` finds a change outside `PRODUCT_SCOPE` | Revert that change or stop with a Decision Brief. |
| S6 | An Electron flake in `--repeat-each` | Fix the test's waiting, never add retries; if the product is racy, stop with a brief. |
| S7 | Review cap (plan 3, execution 6) or the reviewer is unavailable | HARD STOP with a TL;DR (create-plan §5d). Mat is the fallback reviewer. |

## Decision Log

Research engine for this plan: `native` (Claude Code web search, 2026-10-14). Grouping §8 D-1, D-3, D-4 and D-6 carry forward unchanged into the reflection (stage `grouping`); D-2, D-5 and D-7 do not touch this scope. This plan's ids start at D-8. "Triage D-52…D-65" are the 2026-10-09 triage decisions the spec cites.

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "Where is the plan written and executed?"
    resolution: autonomous
    class: two-way
    chosen: "Fresh worktree P:/av-kit/.claude/worktrees/s36-capture-render-fidelity on branch claude/s36-capture-render-fidelity from origin/main 7861020"
    source_tag: Local Canon
    precedents: ["MEU-67's flatten/revert code (a dependency) exists only on main; the main checkout holds uncommitted Session 31 edits (SettingsRail.tsx) that must not be touched"]
    research: { engine: none, sources: [] }
    reasoning: "A worktree isolates this session from the Session 31 working-tree edits and starts from the code MEU-84 depends on. D6 argv are unchanged; only the cwd differs."
  - id: D-9
    stage: planning
    question: "Plan Session 36 before Sessions 31-35 have executed?"
    resolution: human
    class: two-way
    chosen: "Yes; Session 36 is planned and executed now. Merge risk with Session 34 (MEU-81 icon conversion of Open file/folder) is recorded; the testids stay."
    source_tag: Human-approved
    precedents: ["grouping D-4 (two-way order); grouping :65 MEU-81 depends on MEU-80, not on MEU-84; Session 39 follows 36 for shared bake code"]
    research: { engine: none, sources: [] }
    reasoning: "No Session 31-35 MEU is a dependency of MEU-82/83/84 (09:861-863). The only overlap is CapturePage action buttons, which keep their ids."
    human_message_reference: "USER_EXPLICIT 2026-10-14 '@.agent/workflows/create-plan.md 36 capture-render-fidelity'"
  - id: D-10
    stage: planning
    question: "How is ascent(font_size) computed in TypeScript so it equals the bake?"
    resolution: autonomous
    class: two-way
    chosen: "SEGOE_ASCENT: FreeType 26.6 FT_MulFix rounding then ceil, from SEGOE_UNITS; pinned by GEOMETRY_FIXTURE and checked against Pillow getmetrics()"
    source_tag: Research-backed
    precedents: ["capture-segoe-metrics.ts (MEU-59 measured Segoe table)", "adapter.py text_plate_box uses anchor la"]
    research: { engine: native, sources: ["https://freetype.org/freetype2/docs/glyphs/glyphs-2.html — metrics in 26.6 fixed point, ascender scaled then rounded/ceiled to pixels", "https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont.getmetrics — ascent from the FreeType size metrics", "https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html — la vs ls anchors"] }
    reasoning: "Planning receipt R-1: the emulation equals Pillow 12.3.0 for sizes 1-1000 with 0 mismatches; plain ceil(size*2210/2048) mismatches at 38/177/215/354. A runtime canvas measure would follow Chromium, not the bake."
  - id: D-11
    stage: planning
    question: "Keep dominant-baseline=hanging with an offset, or switch to alphabetic?"
    resolution: autonomous
    class: two-way
    chosen: "alphabetic at y + ascent"
    source_tag: Spec
    precedents: ["09:712 'The SVG text sits on the alphabetic baseline at y + ascent(font_size)'"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/dominant-baseline — hanging is script-dependent; alphabetic is the font baseline"] }
    reasoning: "The spec fixes it; alphabetic is the one baseline both FreeType and Chromium place identically."
  - id: D-12
    stage: planning
    question: "Arrow head length factor and angle"
    resolution: human
    class: product-preference
    chosen: "Default if unanswered: ARROW_HEAD. The user may answer 'keep the head' in the execution message."
    source_tag: Research-backed
    precedents: ["09:723 'Head length/angle are set in the plan'", "known-issues CAPTURE-BAKE-ARROW-THIN 'head is also small next to a thick shaft ... consider a wider head angle or length'"]
    research: { engine: native, sources: ["https://www.vintasoft.com/docs/vsimaging-dotnet/ — line-cap arrow sizes as stroke multiples", "https://www.nevron.com/ — ArrowHeadWidthPercent", "https://www.scichart.com/documentation/ — HeadWidth/HeadLength", "https://www.mathworks.com/help/matlab/ref/annotation.html — HeadLength/HeadWidth defaults"] }
    reasoning: "See the brief below."
    human_message_reference: "pending — the execution message; default applies if it is silent"
  - id: D-13
    stage: planning
    question: "Shaft overlap into the head"
    resolution: autonomous
    class: two-way
    chosen: "ARROW_SHAFT_OVERLAP_PX = 1"
    source_tag: Human-approved
    precedents: ["Mat 2026-10-03 via triage D-53: 'tip - head*cos(angle), small overlap'"]
    research: { engine: none, sources: [] }
    reasoning: "1 px hides the AA seam between shaft and head; SHAFT_INSIDE_HEAD proves the corners stay inside the head for every stroke >= 1 (the safe maximum is about 3.4*stroke). A stroke-relative overlap adds a knob with no visible gain."
  - id: D-14
    stage: planning
    question: "How to anti-alias the baked arrow"
    resolution: autonomous
    class: two-way
    chosen: "BAKE_AA: 4x supersample of an L coverage mask on the arrow's tile, LANCZOS down, composite the solid colour through the mask"
    source_tag: Research-backed
    precedents: ["09:722 '4x and downscaled with LANCZOS'"]
    research: { engine: native, sources: ["https://pillow.readthedocs.io/en/stable/releasenotes/2.7.0.html — LANCZOS resampling", "https://mail.python.org/pipermail/image-sig/2001-March/001346.html — PIL has no AA for primitives; draw at 2-4x and downsample", "https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html — line/polygon have no antialias option"] }
    reasoning: "A full-canvas 4x RGBA of a 4K capture is about 530 MB; a tile keeps it to the arrow's box. Downscaling a mask, not colour, avoids dark fringes from resampling colour against the background."
  - id: D-15
    stage: planning
    question: "Clear annotated_path and sidecar_path together or per field?"
    resolution: autonomous
    class: two-way
    chosen: "Per field, saved only on change"
    source_tag: Local Canon
    precedents: ["services/capture.py load_shot_annotations reads the sidecar by name", "read_image raises NotFound when annotated_path is None or missing"]
    research: { engine: none, sources: [] }
    reasoning: "A sidecar without an annotated copy still holds the marks the editor loads; clearing it would hide them. Saving only on change keeps updated_at meaningful."
  - id: D-16
    stage: planning
    question: "What do Open file / Open folder do in the Annotated view when the annotated copy is missing?"
    resolution: autonomous
    class: two-way
    chosen: "Fall back to original_path for both"
    source_tag: Human-approved
    precedents: ["triage D-65 via 09:737-738 ('the fallback when the annotated copy is missing')"]
    research: { engine: none, sources: [] }
    reasoning: "Opening a missing path fails silently in shell.openPath; the original always exists for a listed shot."
  - id: D-17
    stage: planning
    question: "How does Electron E2E observe which file Open file asked for?"
    resolution: autonomous
    class: two-way
    chosen: "E2E_SHELL_LOG in the existing main-process AVKIT_E2E branches"
    source_tag: Local Canon
    precedents: ["ui/src/main/index.ts:372-389 E2E branches for readFile/openPath/showItemInFolder"]
    research: { engine: none, sources: [] }
    reasoning: "contextBridge freezes window.api, so the renderer cannot be spied in Electron; the E2E branch already exists and becomes observable without changing non-E2E behaviour."
  - id: D-18
    stage: planning
    question: "How is the preview-vs-bake pixel comparison made without a real backend in E2E?"
    resolution: autonomous
    class: two-way
    chosen: "TEXT_FIXTURE (real-adapter bake, committed, pinned fresh by pytest) served by the E2E seam; TEXT_PIXEL_ORACLE decoded in-page"
    source_tag: Local Canon
    precedents: ["capture-inbox.test.ts fetch seam serving image bytes (:101-106)", "09:375 no new image dependencies"]
    research: { engine: none, sources: [] }
    reasoning: "The E2E backend is a seam, so the bake must come from a fixture; the pytest freshness check keeps it honest. Canvas decoding avoids adding a PNG library."
  - id: D-19
    stage: planning
    question: "Which element carries the arrow's from/to for tests after the shaft is shortened?"
    resolution: autonomous
    class: two-way
    chosen: "The arrow's SVG g element (data-annotation-type=arrow) keeps x1/y1/x2/y2 = from/to; AC-66.11/66.14 read the g element (TA-5, TA-6)"
    source_tag: Local Canon
    precedents: ["CaptureViewport.tsx:118-143 already sets from/to on the SVG g element"]
    research: { engine: none, sources: [] }
    reasoning: "The SVG line element must show the shaft end (09:721); the endpoints stay inspectable without a new attribute."
  - id: D-20
    stage: execution
    question: "How should AC-65.3 check the stroke edit once short arrows render no SVG line element?"
    resolution: human
    class: two-way
    chosen: "TA-7: assert the rendered head polygon length (35 = factor 5 x stroke 7)"
    source_tag: Human-approved
    precedents: ["2026-10-02-capture-flatten-backup/human-gate-decision.md:73-85 (A-3/TA-8 at the same S2 stop)", "TA-5/TA-6 (move SVG line element reads to an element that keeps the value)"]
    research: { engine: tavily+exa, sources: ["https://testing-library.com/docs/react-testing-library/intro — assert rendered output"] }
    reasoning: "Row-1 census S2 (AC-65.3). Brief and options in walkthrough.md §Decision — S2 (row 1)."
    human_message_reference: "USER_EXPLICIT 2026-10-16 'Approve TA-7 (Recommended)'"
  - id: D-21
    stage: execution
    question: "Should MEU-83 also remove the 1 px outline the preview head inherits from the SVG g element's stroke?"
    resolution: human
    class: product-preference
    chosen: "Add to MEU-83: the head SVG polygon element gets stroke='none', new AC-83.9; the g element keeps stroke"
    source_tag: Human-approved
    precedents: [".agent/workflows/tdd-implementation.md:23 (authorized scope changes fold into plan/task/review)"]
    research: { engine: tavily+exa, sources: ["https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-width — initial 1, inherited"] }
    reasoning: "Found while dispositioning AC-65.3. Brief in walkthrough.md §Decision — S2 (row 1)."
    human_message_reference: "USER_EXPLICIT 2026-10-16 'Add to MEU-83 (Recommended)'"
```

### D-12 — Arrow head size

**Recommendation:** `ARROW_HEAD`. With the shorter shaft, the head is the arrow's most visible part. The current head base is about 3.1× the stroke, which reads as small next to a thick shaft (Mat's note in `CAPTURE-BAKE-ARROW-THIN`). About 4.4× sits between the common "medium" (3×) and "large" (5×) arrowhead presets in office drawing tools. **Reversibility:** two-way (two constants per language and the fixture). **Default if unanswered:** the recommendation.
**Precedents:** 09:366 (the current 4 / 0.4), 09:723 (the plan sets the values). **Research:** native; VintaSoft and Nevron arrow caps sized as stroke multiples; MATLAB `HeadLength`/`HeadWidth` defaults; SciChart `HeadWidth`.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| `ARROW_HEAD` (recommended) | known issue; office presets | — | — | ✅ |
| Keep 4 / 0.40 | 09:366 | No TA-1/TA-2; the existing look | The head stays small beside thick shafts, which the issue names | ⚠️ |
| Factor 6, angle 0.5 | office "large" preset | The most prominent head | Covers more of the target; hides short arrows | ❌ |

## Round 1 Review Corrections

Codex round 1 (2026-10-14, `changes_required`, 2 High blocking and 4 non-blocking findings). [Review file](../../../../.agent/context/handoffs/2026-10-14-capture-render-fidelity-plan-critical-review.md).

| Finding | Disposition | Where |
|---|---|---|
| F1 (High): the `BAKE_AA` raster and its oracles disagree | **Fixed.** The coordinate convention is now explicit (`PIXEL_CENTRE`), and the oracles allow the LANCZOS halo (`AA_LIMITS`). The tip oracle separates a leak (coverage ≥ 0.5 more than 1 px outside the head) from the filter halo (white beyond 3 px). The edge oracle's interior starts 1.5 px inside the edge. AC-83.7 probes the axis 8 px behind the clipped tip instead of the zero-width apex. The tile padding grows to `stroke/2 + 4`. R-3 transcribes `BAKE_AA` literally: the positive passes both oracles, the full-shaft negative fails with 58 leak pixels and the baseline fails with 53 (edge blend 0.0). AC-83.5 now also carries that negative control. | `BAKE_AA`, `PIXEL_CENTRE`, `AA_LIMITS`, `ARROW_TIP_ORACLE`, `EDGE_ORACLE`, AC-83.5–83.7, R-3 |
| F2 (High): final evidence survives an untested config change | **Fixed.** `tested_state` now hashes the whole work tree (tracked diff and untracked files) minus the project artifacts written after the gate, plus the live runtime identity. So the lockfiles, both UI configs, the command manifest and the font are bound. `--state-only` computes the same value. The gate records it before and after it runs. H1-6b re-derives it live. R-4 proves that each bound mutation refuses the historical record, and that artifact edits do not. | `INPUT_IDENTITY`, `identity.py`, §4, task H1-6b, R-4 |
| F3 (Medium): `red-check.py` accepts setup failures | **Fixed.** Each Red row writes `<receipt>.exit`. The checker needs a non-zero exit, a failing-run summary and a diagnostic line that attributes the failure, and it refuses launch, timeout and unrelated-import failures even when source text names a new export. R-5 covers 4 positive and 5 negative fixtures, including both of the review's receipts. | `RED_PROOF`, S3, `red-check.py`, task rows 2, 4 and 6, R-5 |
| F4 (Medium): behavioural suites run before all static checks | **Fixed.** The gate order is now: identity, every static check (including `SCOPE_CHECK`), full, runtime, then identity. Every step after the first failure prints `not_run`. | §4, `session-gate.ps1`, task rows 8 and H1-2 |
| F5 (Low): admin outputs missing from the inventory | **Fixed.** `meu-registry.md`, `current-focus.md` and `known-issues.md` are Files Modified rows and on the `scope-paths` allow-list. H2-2 checks the rendered `known-issues.md` with `issue_triage.py render --check`. | Files Modified, `session-gate.ps1`, task H2-2 |
| F6 (Low): `ARROW_HEAD` values restated | **Fixed.** User Review item 1, the D-12 `chosen`, the brief's recommendation and the option table now name `ARROW_HEAD`. The values appear only in its definition and in the `SHAFT_INSIDE_HEAD` derivation, which needs them. The alternative keeps its 4 / 0.40. | User Review, D-12 |

Blast-radius census, per hit (round-2 procedural gate PR-6). [census-r1.py](census-r1.py) sweeps each variant with `rtk proxy rg -F -n` over this plan and `task.md`, and writes one raw receipt per variant to `C:/Temp/av-kit/census-s36r2-<variant>.txt`. The script holds each variant's search term and each hit's rule. It renders the table below from those receipts, and `python census-r1.py --check` re-runs the sweep and fails on any hit without exactly one disposition. The round-1 receipts `census-s36r1-*.txt` are kept as they were. The table quotes no search term, so it never matches itself. `updated` marks a site edited by the round-1 corrections. `confirmed-consistent` marks a site checked and left as it is; rows marked "correction log row" are the F1–F6 table above.

<!-- census-table:start -->
Blast-radius census: 9 values changed, 18 variants swept, 33 sites found, 21 updated, 12 confirmed consistent. Variants with no hit: `old-grown`, `old-pad2`, `old-factor5`, `old-codepath`, `old-11ids`, `old-rendercheck`.

| Variant | Value | Hit | Disposition | Reason |
|---|---|---|---|---|
| `old-tipcol` | clipped-tip probe | `implementation-plan.md:205` | confirmed-consistent | AC-83.7 says the apex column is *not* asserted and why (F1) |
| `old-angle` | ARROW_HEAD restatement | `implementation-plan.md:118` | confirmed-consistent | the one canonical `ARROW_HEAD` definition (F6 keeps it) |
| `old-angle` | ARROW_HEAD restatement | `implementation-plan.md:121` | confirmed-consistent | the derivation needs the numeric angle; it cites `ARROW_HEAD` values, not a second definition |
| `old-exactwhite` | tip oracle halo | `implementation-plan.md:639` | confirmed-consistent | R-3 describes the round-1 reviewer's method |
| `old-halfpx` | coordinate convention | `implementation-plan.md:124` | confirmed-consistent | the convention names the rejected offset |
| `old-halfpx` | coordinate convention | `implementation-plan.md:639` | confirmed-consistent | R-3 describes the round-1 reviewer's method |
| `new-pad4` | tile padding | `implementation-plan.md:123` | updated | F1: tile padding widened |
| `new-pad4` | tile padding | `implementation-plan.md:560` | confirmed-consistent | correction log row |
| `new-halo` | tip oracle halo | `implementation-plan.md:125` | updated | F1: new halo constant |
| `new-halo` | tip oracle halo | `implementation-plan.md:126` | updated | F1: oracle uses the halo |
| `new-halo` | tip oracle halo | `implementation-plan.md:639` | updated | F1: R-3 cites the halo sensitivity |
| `new-centre` | coordinate convention | `implementation-plan.md:123` | updated | F1: bake states the convention |
| `new-centre` | coordinate convention | `implementation-plan.md:124` | updated | F1: new convention row |
| `new-centre` | coordinate convention | `implementation-plan.md:126` | updated | F1: oracle measures at pixel centre |
| `new-centre` | coordinate convention | `implementation-plan.md:127` | updated | F1: oracle measures at pixel centre |
| `new-centre` | coordinate convention | `implementation-plan.md:560` | confirmed-consistent | correction log row |
| `new-identity` | identity scope | `implementation-plan.md:367` | updated | F2/F4: gate step list |
| `new-identity` | identity scope | `implementation-plan.md:561` | confirmed-consistent | correction log row |
| `new-identity` | identity scope | `implementation-plan.md:651` | updated | F2: identity contract rewritten |
| `new-identity` | identity scope | `task.md:60` | updated | F2: H1-6b re-derives the identity live |
| `new-redproof` | Red proof | `implementation-plan.md:340` | updated | F3: Red proof paragraph |
| `new-redproof` | Red proof | `implementation-plan.md:407` | updated | F3: stop condition cites the Red proof |
| `new-redproof` | Red proof | `implementation-plan.md:562` | confirmed-consistent | correction log row |
| `new-exit` | Red proof | `task.md:41` | updated | F3: Red row 2 keeps child exits |
| `new-exit` | Red proof | `task.md:44` | updated | F3: Red row 4 keeps child exits |
| `new-exit` | Red proof | `task.md:47` | updated | F3: Red row 6 keeps child exits |
| `new-notrun` | gate order | `implementation-plan.md:365` | updated | F4: gate section |
| `new-notrun` | gate order | `implementation-plan.md:563` | confirmed-consistent | correction log row |
| `new-notrun` | gate order | `task.md:50` | updated | F4: gate row reports later steps |
| `new-notrun` | gate order | `task.md:54` | updated | F4: gate rerun reports later steps |
| `new-issuerender` | admin inventory | `implementation-plan.md:295` | updated | F5: new Files Modified row |
| `new-issuerender` | admin inventory | `implementation-plan.md:564` | confirmed-consistent | correction log row |
| `new-issuerender` | admin inventory | `task.md:67` | updated | F5: H2-2 checks the rendered issues file |
<!-- census-table:end -->

Re-verified after the round-2 edits: `lint_task_contract.py` exit 0 (26 rows), R-3 exit 0, R-4 exit 0 (including with a missing signing key), R-5 exit 0, `census-r1.py --check` exit 0.

## Round 2 Review Corrections

Codex round 2 (2026-10-14, `changes_required`, a procedural gate, no severity-rated finding). F1–F6 were not re-reviewed.

| Item | Disposition | Where |
|---|---|---|
| PR-6: the census gave totals and grouped reasons, not a disposition for each `file:line` | **Fixed.** [census-r1.py](census-r1.py) re-runs the sweep into fresh raw receipts, and the plan's §Round 1 Review Corrections now carries one row per hit, each marked `updated` or `confirmed-consistent` with its reason. `--check` fails on a hit with no rule or more than one, on a rule that matches nothing, or when the table differs from the receipts. The new sweep finds 33 hits, against 27 in round 1: the six extra are the round-1 correction log's own rows. | §Round 1 Review Corrections, `census-r1.py` |
| R-4 observation: the `identity.py` selftest fails where the inherited git config signs commits and the key is missing | **Fixed.** The scratch commit disables signing for that one command. With a missing signing key forced through `GIT_CONFIG_*`, the selftest exits 0. Without the override, the same setup fails with git exit 128, as in the review. | `identity.py`, R-4 |

## Research References

- FreeType glyph metrics: https://freetype.org/freetype2/docs/glyphs/glyphs-2.html
- Pillow text anchors: https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
- Pillow `getmetrics`: https://pillow.readthedocs.io/en/stable/reference/ImageFont.html
- Pillow `ImageDraw` (no antialias for primitives): https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
- Pillow 2.7.0 release notes (LANCZOS): https://pillow.readthedocs.io/en/stable/releasenotes/2.7.0.html
- image-sig thread on supersampling: https://mail.python.org/pipermail/image-sig/2001-March/001346.html
- MDN `dominant-baseline`: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/dominant-baseline

## Planning receipts

- **R-1 (2026-10-14).** Using `P:/av-kit/.venv` (Pillow 12.3.0) and `C:/Windows/Fonts/segoeui.ttf`: `head.unitsPerEm = 2048`, `hhea.ascender = 2210`, `hhea.descender = −514`. `getmetrics()[0]` equals the `SEGOE_ASCENT` emulation for sizes 1–1000 (0 mismatches), and equals `GEOMETRY_FIXTURE.segoe_ascent` for every listed size. The plain `ceil` form mismatches at 38, 177, 215 and 354. `textbbox(anchor="la").bottom − textbbox(anchor="ls").bottom == ascent` for "Hi" at 12–64. The scratch scripts are not committed; row 2 re-derives the fixture through the pytest.
- **R-2 (2026-10-14).** For `(0,0)→(100,0)` stroke 3 under `ARROW_HEAD`: head 15, left `(86.49329346470985, 6.524483011668454)`, shaft end x `87.49329346470985`.
- **R-3 (2026-10-14, review F1).** [aa-oracle-probe.py](aa-oracle-probe.py), run with `P:/av-kit/.venv/Scripts/python.exe aa-oracle-probe.py --pad 4` (Pillow 12.3.0), exit 0. It transcribes `BAKE_AA` literally and runs the oracles on three bakes: the positive (shaft at `SHAFT_END`), `full_aa` (`BAKE_AA` with the shaft to the tip) and `baseline` (the current adapter).
  - **Tip:** positive 0 leak pixels, halo maximum deviation 0. `full_aa` 58 leak pixels, deviation 255. `baseline` 53 leak pixels, deviation 255.
  - **Edge:** positive blend fraction 0.5117 over 641 edge pixels, interior maximum deviation 4, 0 pixels changed outside the tile. `baseline` blend fraction 0.0.
  - **Clipped `(20,60)→(119,60)` s3:** axis coverage by distance behind the tip is 0.161, 0.8, then 1.0 from 2 px back. The pixel 8 px back is `(255,0,0)`. An arrow tile wholly outside the image leaves the image unchanged.
  - `--pad 2` gives the same verdicts.
  - **The round-1 counts (117 / 34):** the review sampled at `(x + 0.5, y + 0.5)` and required exact white 1 px outside the head. Both assumptions fail a correct bake: LANCZOS coverage legitimately reaches past the edge (with the halo bound set to 1 px or 2 px, the positive bake's maximum deviation is 4 or 3; at `AA_HALO_PX = 3` it is 0).
- **R-4 (2026-10-14, review F2).** `uv run python identity.py --selftest`, exit 0. In a scratch git repository, each of `uv.lock`, `ui/package-lock.json`, `ui/tsconfig.json`, `ui/electron.vite.config.ts`, `.agent/docs/commands.md`, this plan's `session-gate.ps1` and a source file changed the state, and `evidence_problems(require_full=True)` refused the earlier full record. An untracked test file and a runtime (node) change also changed the state. Edits to this plan's `walkthrough.md`, a handoff and a `docs/build-plan` file left it unchanged. Round 2: the scratch commit disables signing for that one command. With a missing signing key forced (`commit.gpgsign=true`, `gpg.format=ssh`, an absent `user.signingkey`), the selftest still exits 0. Without the override, it fails with git exit 128.
- **R-5 (2026-10-14, review F3).** `uv run python red-check.py --selftest`, exit 0, 9 fixtures, 0 wrong.
  - **Pass:** a pytest assertion, a pytest missing declared export, a Vitest unresolved declared module, a Playwright `expect` failure.
  - **Refused:** the review's Electron-launch receipt (which names `viewedFilePath` in a test title), a locator timeout with `assert` in the source context, an unrelated `ImportError`, a run whose exit was 0, and a receipt with no `.exit` file.

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract` (§4).
- **Targeted:** §3 after each production edit (blocking for its row).
- **Fresh full:** §4 in one pass after the last edit (row 8), from `WT`, `pwsh`. It must pass; no partial, cached or reused receipt counts. Re-run all of §4 if any input changes after it (H1-6b).
- **Runtime (optional, non-blocking):** Mat's visual check (User Review Required item 4).
- **Input identity (`INPUT_IDENTITY`):** [identity.py](identity.py) prints the runtime identity and `tested_state` = HEAD + one SHA-256. The hash covers:
  - the tracked diff and the untracked (not ignored) files of the whole work tree, except the project artifacts written after the gate (this plan folder's `*.md`, `.agent/context/`, `docs/execution/reflections/`, `docs/execution/metrics.md`, `docs/build-plan/`, `docs/BUILD_PLAN.md`). So the lockfiles, `ui/tsconfig.json`, `ui/electron.vite.config.ts`, the `.agent/docs/commands.md` manifest, the fixtures and this plan's scripts are all bound;
  - the runtime identity, observed live: the Python running it, `node --version`, the installed `electron` and `@playwright/test` versions in `ui/node_modules`, the `segoeui.ttf` SHA-256 (the external input to AC-82.2, AC-82.5 and AC-82.6) and `ELECTRON_RUN_AS_NODE`.

  `--state-only` computes the same value. An unreadable input raises, so it never hashes as absent. The gate records the state before and after it runs (§4), and each handoff's final full `evidence.v1` record carries it. H1-6b re-derives it live with `identity.py --state-only`, so any bound change refuses the old record and forces H1-2 again. `identity.py --selftest` proves this in a scratch repository (R-4): each bound mutation changes the state and makes `durable_evidence.evidence_problems` refuse the earlier full record, and edits to the project artifacts leave the state unchanged.
- **Evidence:** each receipt's exit code and decisive lines, pasted as `evidence.v1` in the handoffs.
- **D9:** yes; MEU state updates through `tools/meu_status.py` (H1-3).
