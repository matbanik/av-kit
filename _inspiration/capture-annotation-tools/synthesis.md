# Capture Annotation Tools — Composite Synthesis (2026-10-29)

> **Inputs:**
> - `report_chatgpt.md` (D1). Self-labelled "Codex / ChatGPT"; model and reasoning tier UNVERIFIED. It is a source audit of 10 apps × 65 behaviours with pinned commits.
> - `report_gemini.md` (D2). Self-labelled "Claude 3.5 Sonnet / Deep Research Synthesis Engine", which is wrong for a Gemini run, so the real model is unknown. It embeds two PNGs; these were extracted and viewed separately.
> - `report_claude.md` (D3). Claude Opus 5.5 at Effort **low**, not the Max the prompt asked for. The report says its search budget ran out.
>
> The prompts asked for `output-*.md`; the human saved the results as `report_*.md`. Context file: `context-capture-annotation.md`.
>
> **Bands** follow `.agent/skills/deep-research-prompting/SKILL.md` §6:
> - **Consensus**: 2 or more providers agree.
> - **Single-source (VERIFY)**.
> - **Contradiction**: adjudicated.
> - **Gap**.
>
> **Provider codes:** **GPT**, **Gem**, **Cl**. **[local]** means I checked it in this session against the repository.

## 0. Local facts established this session

These facts override any report line that contradicts them.

| # | Fact | Evidence |
|---|---|---|
| L-1 | Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z / Ctrl+C / Ctrl+A are in `RESERVED_CHORDS` under **D-136** (autonomous, two-way). They are reserved because the Electron default menu's role accelerators run in the main process before the renderer sees the key. Canvas undo and Ctrl+C copy therefore mean **revising D-136**: a custom menu or `before-input-event` routing, not just a renderer keydown. | `ui/src/renderer/src/registry/shortcuts.ts:125-150`; `docs/execution/plans/2026-10-26-gui-keyboard-palette/implementation-plan.md:559-568` |
| L-2 | **Apply to image is disabled while the overlay is dirty** ("Save the overlay first"). It cannot bake stale marks. | `ui/src/renderer/src/features/capture/capture-flatten.ts:15,58` |
| L-3 | The clipboard plumbing exists: `window.api.writeClipboardImage` and PNG pass-through. However, the filmstrip's Copy image copies the **original** variant only. No endpoint renders **unsaved** marks: `/captures/{id}/image` serves `original \| annotated` (the saved bake). | `capture-clipboard.ts:76-78`; `CapturePage.tsx:1109-1117`; `packages/api/.../routes/captures.py:257-275` |
| L-4 | API request models are `extra="forbid"`, so an unknown field or type is rejected and never silently ignored. | `packages/api/src/avkit_api/schemas/common.py:8-11` |
| L-5 | `TextAnnotation` validates only length (1–`TEXT_MAX_CHARS`); it does **not** reject `\n`. An agent can already send multi-line text over MCP. Preview and bake behaviour for that case is untested (G-3). | `packages/core/src/avkit_core/domain/capture.py:196-215` |
| L-6 | The region pass bakes pixelate and eraser in list order **before** drawn marks, sampling the original. The renderer keeps a Segoe glyph-metrics table so SVG text matches Pillow. | `adapter.py` `apply_region_pass`; `capture-segoe-metrics.ts` |
| L-7 | The MCP and agent vocabulary already says **flatten** and **revert** (`capture flatten`, `capture revert`). | avkit MCP server instructions |

## 1. Source report quality

| Report | Grade | Strengths | Weaknesses |
|---|---|---|---|
| GPT (D1) | **A** | The best evidence discipline. Every count uses Y/P/N/U with U never folded into "no". It pinned commits and line ranges for snypr, omasnap and Playwright, and checked every prior finding one claim at a time. It has the only complete data-model table with backward-compatibility rules, plus concrete interaction rules (resize, text, routing, clipboard, flatten). It has 24 dated complaint sources. It corrected the licence: kImageAnnotator is LGPL-3.0. | Its model and tier are unknown. It says outright that it did not audit the repo, so G3 "Apply can use stale marks" is wrong (L-2). Its effort labels are coarse. |
| Cl (D3) | **B+** | The clearest strategy: rulings, a shared transform module, an ERRC grid, ordered slices and an honest counter-argument. It gave Bishop Fox / Unredacter as the primary Depix source, and found that ShareX's "Smart Eraser" matches av-kit's eraser. | It ran at **low effort**, and its search budget ran out. Many matrix cells are U. It marked Cap #1864 and Playwright #40238 UNVERIFIED, but GPT verified both from primary sources. |
| Gem (D2) | **B-** | The strongest community-signal section (§8), with issue numbers such as Excalidraw #4267 / PR #7999, ksnip PR #759, Flameshot #3812 and ShareX #2984. It has the most concrete parity flags (wrap = HIGH, seeded PRNG = HIGH) and a usable handle-geometry diagram (image2). | Its model label is wrong. Its adoption scores are inflated (10/10, 9.5/10). Its image1 says av-kit already keeps the active tool armed, which is false: Lock is off by default. It calls omasnap "FULLY VERIFIED" at `tobi/omasnap`, but GPT and Cl both find the repo at `omacom/omasnap`. Its MVP-must list is the widest of the three, as it promotes shortcuts, wrap and scrambled pixelate. |

**Weighting:** GPT counts first for facts. Cl counts first for sequencing and rulings. Gem counts as corroboration and for community demand; on its own it does not support a fact.

## 2. Prior findings: verdicts

| Prior claim | GPT | Cl | Gem | Composite |
|---|---|---|---|---|
| Cap #1864: the editor resets to Select, settings cannot be set before drawing, no per-tool memory | VERIFIED; one author, 2026-05-21 | UNVERIFIED; similar complaints in tobyshot #27, CanvasCraft #1, Screendrop #51 | cited | **Verified as one dated complaint**, not as prevalence. |
| snypr: 8 box handles, endpoint handles, text corners scale font and sides set wrap, double-click re-edit, per-tool colour, R/O/A/L/H/F/N/T/B/X | All VERIFIED (commit `5c7b3e4`). Per-tool colour lasts the session only. Handles are 8 visible / 12 hit, in document px. | CONFIRMED | cited | **Verified.** Note: snypr **returns to Select** after drawing (GPT, Cl). It is a counterexample to sticky tools. |
| omasnap: V, Shift, Alt, Shift+arrow 10 px, double-click/Enter re-edit, Alt+D, Ctrl+C copies the PNG, "secure" redaction | All VERIFIED at **`omacom/omasnap`**. Handles: 5 px radius, 9 px hit. The randomized mosaic takes ≤ 6 colours from source aggregates, so "no source information" is **REFUTED**. | partial; features are in the omacom README | "FULLY VERIFIED" at tobi/omasnap | **Verified at omacom/omasnap**; the prior pass's `tobi/` URL was wrong. The mosaic is **not** information-free. |
| Playwright PR #40238: 8 handles, Enter saves, Shift+Enter newline | VERIFIED: merged 2026-04-16 (merge `1898141d`). It is in **packages/dashboard**, not trace-viewer. Handles are 10×10 CSS px. Nudge is 5 px, and Shift makes it 1 px. | UNVERIFIED, "do not cite" | cited | **Verified**, with the package corrected. Cite GPT's pinned links. |
| Depix recovers more than 96% | PARTIAL: only for specific configurations (the 2016 HMM paper, Table 4) | unsupported; a vendor blog | flagged | **The "> 96%" figure is UNVERIFIED as a general claim.** That averaging pixelation is weak is verified, with Bishop Fox's Unredacter as the primary source. |
| ksnip / kImageAnnotator: GPL, a common Flameshot replacement | PARTIAL: ksnip is GPL, **kImageAnnotator is LGPL-3.0**. "Common" is not quantified. | — | — | Correct `context-capture-annotation.md` line 167 at the next edit. Both stay behaviour-only. |

## 3. Band A — Consensus (safe to implement)

### A-1 Area marks resize with 8 handles (GPT, Cl, Gem — all MVP-must)

- **Which marks:** rect, highlight, pixelate and eraser get 8 handles. The body moves the mark.
- **Feedback:** directional cursors.
- **Pointer handling:** pointer input is converted to image space. Crossed handles are normalized ("flip"). The result is clamped to the image, rounded to integers at commit, and has at least 1 px per side.
- **Undo:** one drag is one undo step, Escape cancels the drag, and a no-op drag records nothing.
- **Export:** handles never export.

Evidence: GPT A01 is 7/10 verified, and av-kit's own users reported the gap. One **shared transform module** covers every bounded mark (Cl). Text joins it with corner-only handles (A-6). Handle sizing is ruled in C-11.

### A-2 Text words can be edited again (GPT, Cl, Gem — all MVP-must)

- Double-click a text mark, or press Enter on a selected one, to edit it in place.
- Escape restores the words and the geometry from before the edit.
- The whole edit is one history transaction.

Evidence: GPT C03 is 9/10.

### A-3 Canvas undo/redo from the keyboard (GPT, Cl, Gem — all MVP-must)

- **Canvas:** Ctrl+Z undoes. Ctrl+Y and Ctrl+Shift+Z redo.
- **Text fields:** they keep their native undo.
- **Routing:** one focus-aware command owner, so the menu and the renderer never both run a command (GPT R06/R07, Cl slice 1).

Evidence: GPT F02 is 9/10. **[local L-1]:** this changes D-136. It is the shared prerequisite for Ctrl+C (A-4) and for single-key shortcuts (A-12).

### A-4 Copy the current annotated image (GPT, Cl, Gem — all MVP-must)

- A **Copy image** button copies the flattened PNG of the **current, unsaved** marks.
- The editor stays open.

Evidence: GPT G01 is 9/10. **[local L-3]:** the clipboard path exists, but nothing renders unsaved marks. The chord is ruled in C-5, and the render path is open question G-6.

### A-5 Solid opaque redaction is available, and pixelate is labelled as visual-only (GPT, Cl, Gem)

All three agree that averaging pixelation leaves recoverable signal and that an opaque fill is the safe choice. GPT D03 is 8/10. The default and the data shape are contested (C-1, C-2).

### A-6 Text corner handles scale the font (GPT A5, Cl, Gem)

- **Corners:** change the integer `font_size`, never the stored scale.
- **Sides:** no side handles until wrap exists (C-3).

Evidence: snypr verified; ShareX #8882 (2026-10-07) asks for this exact behaviour.

### A-7 Multi-line text: Enter commits, Shift+Enter adds a line (GPT C2, Cl, Gem)

- **Keys:** Enter commits and Shift+Enter adds a line, which keeps av-kit's current Enter behaviour (Playwright verified). Show the hint while editing.
- **IME:** Enter belongs to the IME during composition.
- **Bake:** explicit newlines only; no automatic wrap (C-3).

### A-8 Colour applies on click; the Apply/Cancel gate goes (GPT E1, Cl, Gem)

- **Swatches:** apply immediately.
- **Hex field:** applies on Enter or blur. Invalid input stays in the field without blocking the editor.
- **Undo:** one click or one scrub is one undo entry.

No source found an Apply gate in any reference app. The priority is contested (C-4); the effort is S.

### A-9 Each tool remembers its own style, across restarts (GPT E2, Cl, Gem)

- **Selection:** with a mark selected, a control restyles only that mark. With nothing selected, it sets that tool's defaults (GPT E3).
- **Storage:** the defaults are an app preference, never mark JSON.

Evidence: Flameshot #4957 (2026-09-16), Cap #1864, and a CleanShot X Reddit thread (2024-10-06).

### A-10 The tool stays armed after drawing by default (GPT F2, Cl, Gem)

- **Default:** turn Lock on by default.
- **Back to Select:** Escape or V.
- **Opt-out:** keep a one-shot preference.

GPT F04 is 6/10, the only verified majority for this behaviour. snypr is the counterexample. The detail is ruled in C-6.

### A-11 Rename the Eraser (GPT, Cl, Gem)

The Snipping Tool, the Windows baseline, uses Eraser to **delete annotations** (GPT D04). av-kit's tool fills an area with the surrounding colour, which ShareX calls **Smart Eraser** (Cl). The name is ruled in C-10. The JSON type `eraser` and its algorithm stay unchanged (GPT D2).

### A-12 Single-key tool shortcuts, off while typing (GPT F3, Cl, Gem)

GPT F01 is 7/10, but there is no de facto letter map, so av-kit documents its own (C-12). Shortcuts go through the existing shortcut registry (MEU-95/96/97) as page-scoped entries. They never fire in input, textarea or contentEditable targets.

### A-13 Modifiers and nudge (GPT A3/A4, Cl, Gem)

- **Shift:** constrains aspect ratio or a square while creating and resizing, and snaps lines and arrows to 45°.
- **Alt:** draws from the centre.
- **Arrow keys:** 1 px, or 10 px with Shift.

Playwright's 5 px default with Shift for 1 px is the counterexample; omasnap and av-kit's existing 1 px decide it.

### A-14 Line and Ellipse are the next shapes (GPT B2, Cl slice 8, Gem)

Line is an arrow with no head, and Ellipse is a rect with `shape: ellipse`. GPT counts B02 at 8/10 and B03 at 9/10. They come after the repair loop. Field names are ruled in C-13.

### A-15 Clearer action names (GPT G2, Cl, Gem)

The word "Flatten" is agreed, and it matches the MCP vocabulary [local L-7]. Exact labels are ruled in C-14.

### A-16 Editor-only redaction outlines (Cl, GPT D3)

Each redaction area shows a dashed editor-only outline, with an optional "show all redaction areas" view. Neither is ever exported.

### A-17 Keep what already works (GPT "already adequate", Cl, Gem)

- **Geometry and data:** integer image-space geometry, arrow endpoints, editable JSON/MCP.
- **Keys:** 1 px nudge, Delete/Escape.
- **Undo:** grouped gesture undo.
- **Styling:** font-size scrub, text background plate.
- **View:** wheel/keyboard zoom, Space/middle-button pan, the Original/Annotated toggle (GPT F11 is 1/10, but it is useful and costs nothing).
- **Safety:** the unsaved-leave warning and the backups.

### A-18 Shared non-goals (GPT §7, Cl, Gem)

Leave out:
- rotation and skew
- diagram connectors and auto-layout
- rich text and a font picker
- stickers, magnifier, spotlight, beautifiers
- a layer panel
- a canvas-library rewrite (Konva and Fabric are patterns to study, not dependencies)
- OCR auto-redact
- blur sold as a security feature

### A-19 Parity risks (GPT §6, Gem)

- **Text layout** is the biggest risk: browser and Pillow measure, place baselines and wrap differently.
- **Wrap** is HIGH risk.
- **Ellipse antialiasing and stroke alignment** are MEDIUM.
- **Solid mask edges:** Pillow's rectangle is inclusive, so define half-open coverage `[x, x+w)`.

Every model change ships with old-fixture tests that omit the new fields (GPT acceptance checks).

## 4. Band B — Single-source (VERIFY)

| # | Claim | Provider | Status / action |
|---|---|---|---|
| B-1 | Apply bakes stale saved marks, rated broken-feeling (G3) | GPT | **Refuted [local L-2]**: Apply is disabled while dirty. The real issue is friction: Save, then Flatten, is two steps. Flatten can offer "Save and flatten" inside its confirm dialog. |
| B-2 | Keep undo history across shot switches (F5) | GPT | Not measured against competitors. Later. |
| B-3 | Export image… with a path chooser (G4) | GPT | Later; Save already writes `.annotated.png`. |
| B-4 | Store multi-line text behind `text.layout_version` so old marks are never re-laid out | GPT | **[local L-5]**: the validator already accepts `\n`. Check whether any stored mark contains `\n` (G-3). If none does, define `\n` semantics directly and skip the version field. |
| B-5 | Seeded scrambled pixelate (xorshift32, ±1 cell shuffle, ±4 jitter) as an MVP-must | Gem | **Rejected** (C-1). The omasnap source shows a mosaic still leaks aggregate colour (GPT), and a shared PRNG is a HIGH parity risk (Gem's own flag). |
| B-6 | Manipulate existing marks while a draw tool is armed | Gem | Adopted narrowly (C-6). |
| B-7 | Ctrl+D duplicate (offset, clamp, select the copy) and a small canvas context menu | GPT F4, Cl slice 8 | Two sources, so it is really consensus-level, but neither calls it a must. MVP-should, in the shapes slice. Ctrl+D is not in `RESERVED_CHORDS`. |
| B-8 | Flameshot #4598 asks for a windowed editor | Gem | Out of scope; av-kit's editor is already windowed. |
| B-9 | ShareX #2984: users expect Ctrl+C to copy the image | Gem | Supports C-5. |
| B-10 | Pixelate minimum size is 2 × `block_size` | Cl | Not adopted. A smaller area is still one valid cell. Keep 1 px. |
| B-11 | Greenshot #540: handles and heads are tiny on high DPI | GPT | Supports screen-constant handle sizing (C-11). Test at 150% and 200% (G-4). |
| B-12 | Pixelate gets the same scrub control as font size (E4) | GPT | Cheap; fold it into the style slice. |

## 5. Band C — Contradictions (adjudicated)

| # | Topic | Positions | Ruling |
|---|---|---|---|
| C-1 | Default redaction | Cl: solid fill. GPT: solid, with pixelate kept as an explicitly visual mode. Gem: seeded scramble **and** solid, both must. | **Solid black is the default for new redactions.** Pixelate stays as an explicitly labelled "visual blur" mode. No scrambled mosaic. Two of three agree, and Bishop Fox, the primary source, says to use black bars. The mosaic is not information-free (GPT, from omasnap's source) and adds PRNG parity work. |
| C-2 | Data shape for solid redaction | Cl: new `redact` type. GPT: `pixelate.mode` + `fill_color`. Gem: `rect.fill_color`. | **New `redact {x, y, width, height, color="#000000"}` type**, baked in the region pass. A type name the agent API can read beats "pixelate with mode solid". An older server rejects an unknown type outright [L-4], never draws a weaker mark. `rect.fill_color` would bake in the drawn-mark pass and mixes "decorate" with "destroy". The toolbar shows one **Redact** tool with a Solid / Pixelate toggle. Switching a selected mark replaces it, as one undo step. |
| C-3 | Text wrap width (side handles) | Gem: must. GPT: should, with side handles only once wrap exists. Cl: Later. | **Later, as its own slice after multi-line.** Wrap is the top parity risk (Gem, GPT), and explicit newlines (A-7) cover bug-report labels. Demand is real (Snipaste #2200, Excalidraw #4267), so it is first in Later. |
| C-4 | Priority of colour-on-click and single-key shortcuts | Gem: must. GPT, Cl: should. | **Should.** The toolbar is a workaround. Both are S effort, so they ship early anyway (slice 5). |
| C-5 | Copy-image chord | Cl: Ctrl+Shift+C always, Ctrl+C when no text field has focus. Gem: Ctrl+C. GPT: Ctrl+C on the canvas always, even with a mark selected; no object copy in MVP. | **Ctrl+C on the canvas copies the image. Text fields keep native copy.** There is no mark copy/paste, so Ctrl+C has one meaning (omasnap, ShareX #2984). Once slice 1 owns routing, Claude's reason for the Ctrl+Shift+C alias (a menu-reserved Ctrl+C) no longer applies. |
| C-6 | How a sticky tool behaves | Cl: Lock on, and the new mark stays selected. Gem: Lock on, and existing marks can be moved while armed. GPT: tool stays active, Escape or V selects, one-shot option. | **Lock is on by default and persisted. The just-drawn mark stays selected.** While a tool is armed, a press on the **selected** mark's handles or body edits it, and a press anywhere else draws. Gem's "any existing mark" variant would stop users drawing a box inside a highlight. |
| C-7 | Multiply highlight | Gem: should. Cl, GPT: Later (B09 is 2/10). | **Later.** No majority, and the blend parity is medium to hard. |
| C-8 | Numbered steps | GPT: should (8/10). Gem: should. Cl: Later. | **MVP-should, after the repair slices.** The count is strong for how-to screenshots. It is a new `step` type, not a text badge: an agent reads its number directly. |
| C-9 | Freehand pen | GPT: should (10/10). Gem, Cl: Later. | **Later.** It needs a new path kind with cap, join and simplification parity. No av-kit report asks for it. Revisit if users do. |
| C-10 | Eraser name | Cl: "Smart Eraser" (the ShareX precedent). Gem: "Smart Erase". GPT: "Clean up". | **"Smart eraser"**, with the tooltip "Covers an area with the surrounding colour". Windows ShareX users already know the name for the same behaviour, and "smart" signals it is not Snipping Tool's delete-eraser. "Clean up" is a reasonable alternative (D-3). |
| C-11 | Handle size | snypr 8 visible / 12 hit (document px). omasnap 5 radius / 9 hit. Playwright 10×10 CSS. GPT proposes 8 / 16 CSS. Cl ~8 / ~10. Gem 5 / 12. | **8 CSS px visible, 12 CSS px hit, constant on screen at every zoom**, with a contrasting outline. This is the median of the verified sources; tune it after a high-DPI check (G-4). |
| C-12 | Letter map | Gem: V/A/R/H/T/P/E/L. GPT: V/A/B/H/T/R/E. snypr: R rect, O ellipse, X solid redact, B blur. | **V Select · A Arrow · R Box (rectangle) · H Highlight · T Text · X Redact · E Smart eraser**, plus later **L Line · O Ellipse · N Step**. R for rectangle matches snypr and Gem. X for redact matches snypr's solid redact and frees R. |
| C-13 | Arrow-head field | Cl, Gem: `arrow.head`. GPT: `start_head` + `end_head`. | **`arrow.head?: "end" \| "none" \| "both"`, default `"end"`.** One field covers Line and a later double-headed arrow. |
| C-14 | Action labels | Cl: Save / Flatten into original… / Restore original. GPT: Save annotations / Flatten into image… / Restore last backup…. Gem: renames plus Save As. | **Save annotations · Flatten into image… · Restore backup…** "Restore original" is wrong: Revert restores the **newest** backup, which need not be the pristine capture (GPT). The labels match MCP `flatten`/`revert` [L-7]. |

## 6. Gaps

- **G-1** All three reports are source audits. No one tested the ten apps hands-on, so every count is a lower bound for the surveyed versions (GPT).
- **G-2 [local]** Will a custom application menu or a `before-input-event` route keep native undo and copy working in **every other page's** text fields? This needs a test before D-136 changes.
- **G-3 [local]** What do the SVG preview and the Pillow bake do today with an agent-sent `text` containing `\n` (L-5)? It is probably already a parity bug. Settle it before slice 3b.
- **G-4 [local]** Check handle hit size at Windows display scaling of 100%, 150% and 200%.
- **G-5** Does `PixelateAnnotation` already enforce `block_size` ≤ the area? It matters for resize clamping.
- **G-6** How to render for Copy image:
  - **(a)** A backend `POST /captures/{id}/render` takes the current marks and returns a PNG. It is exactly what Save would produce and adds one round-trip.
  - **(b)** Rasterize the SVG preview in the renderer. It is instant, but it inherits every parity gap.
  - Recommendation: **(a)**.
- **G-7** Cross-shot history retention (B-2) was not measured against competitors.

## 7. Composite spec

### MVP-must: "doesn't feel broken"

| # | Behaviour | Effort | Source |
|---|---|---|---|
| M-1 | Canvas Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z through a focus-aware router | M | A-3, L-1 |
| M-2 | 8-handle resize for box, highlight, pixelate, eraser and redact, with cursors | M | A-1, C-11 |
| M-3 | Text re-edit: double-click or Enter, Escape restores | M | A-2 |
| M-4 | Copy image of the current marks (button and canvas Ctrl+C) | M | A-4, C-5, G-6 |
| M-5 | Solid Redact as the default, with Pixelate as a labelled mode | M | A-5, C-1, C-2 |

### MVP-should: real friction with a workaround

- **Text:** corner font scaling (A-6); multi-line text (A-7).
- **Style:** colour on click (A-8); per-tool persisted style (A-9); pixelate scrub (B-12).
- **Tools:** Lock on by default with the selected-mark rule (C-6); letter shortcuts (C-12); Shift / Alt / Shift+arrow (A-13).
- **Naming:** Smart eraser rename (C-10); action renames and "Save and flatten" in the confirm (C-14, B-1).
- **Redaction:** dashed redaction outlines (A-16).
- **Shapes:** Line and Ellipse with 45° snap (A-14); Ctrl+D (B-7); numbered steps (C-8).

### Later, with their triggers

| Item | Trigger |
|---|---|
| Wrap width and side handles | First in Later (C-3) |
| Bold and alignment | — |
| Multiply highlight | — |
| Freehand pen | A user asks for it |
| Blur as a visual effect | — |
| Multi-select, marquee, Ctrl+A | — |
| Z-order (needs a render version) | — |
| Callouts | Text-plus-arrow becomes a repeated complaint |
| Recent colours and eyedropper | — |
| Export with a path chooser | — |
| Cross-shot history | — |

### Non-goals

These are the A-18 items.

### Data-model changes

All of them are optional, and their defaults render existing overlays unchanged. TS types, the Python domain, API schemas, MCP schemas and both renderers change together (GPT compatibility contract).

| Item | Change | Parity |
|---|---|---|
| M-2, A-6, A-13, colour, shortcuts, Lock, Copy image, renames | **None**: existing geometry and `font_size`; tool defaults are app preferences | Low |
| M-5 | New `redact {x, y, width, height, color="#000000"}`, region pass, alpha 255, half-open coverage | Low |
| A-7 | `text` gains defined `\n` semantics; line spacing is derived from `font_size` (no field) unless G-3 shows stored marks need `layout_version` | **High**: extend the Segoe metrics table to multi-line, plus fixtures |
| A-14 | `arrow.head?: "end" \| "none" \| "both"` = `"end"`; `rect.shape?: "rect" \| "ellipse"` = `"rect"` | Low (head); medium (ellipse) |
| C-8 | New `step {x, y, number, color, size}` | Medium (badge text centring) |
| Later | `text.wrap_width?`, `text.bold?`, `text.align?`, `highlight.blend?`, a new `path` type | Hard (wrap, bold, blend) |

## 8. Ordered slices (about one session each)

| # | Slice | Depends on | Covers |
|---|---|---|---|
| 1 | **Input router.** Replace the Edit-menu roles with routed commands, or use `before-input-event`. Canvas Ctrl+Z / Y / Shift+Z; text fields stay native everywhere. Revise D-136. | — | M-1, G-2 |
| 2 | **Transform module.** 8 handles for every bounded mark, cursors, normalize and clamp, one undo per drag, Escape cancels, screen-constant sizes. | — | M-2, C-11 |
| 3a | **Text re-edit and corner scaling.** No model change. | 2 | M-3, A-6 |
| 3b | **Multi-line text.** Shift+Enter, `\n` semantics, Segoe metrics for multiple lines, bake fixtures. | 3a, G-3 | A-7 |
| 4 | **Redaction.** The `redact` type through every layer, a Redact tool with a Solid/Pixelate toggle, Smart eraser rename, dashed outlines. | 2 | M-5, A-11, A-16 |
| 5 | **Copy image and actions.** A render endpoint for unsaved marks, button plus canvas Ctrl+C, renames, "Save and flatten". | 1 | M-4, C-14, B-1 |
| 6 | **Style and tool flow.** Colour on click, per-tool persisted style, Lock on by default with the selected-mark rule, letter shortcuts, Shift/Alt/Shift+arrow, pixelate scrub. | 1, 2 | A-8, A-9, A-10, A-12, A-13 |
| 7 | **Shapes.** Line, Ellipse, 45° snap, Ctrl+D. | 2, 6 | A-14, B-7 |
| 8 | **Steps.** | 6 | C-8 |

Slices 1–5 are the MVP-must set. If the team stops after slice 5, nothing in the editor feels broken; the remaining slices remove friction.

**Strongest counter-argument (Cl):** Snipping Tool is the real Windows baseline, so a smaller MVP would be resize, Ctrl+Z and Copy image. Redaction (slice 4) stays in anyway: a pixelated secret fails silently, and the user never learns that it leaked. Text re-edit stays because av-kit's own users reported it.

**What would change the order:** if G-2 shows menu re-routing breaks text fields elsewhere, slice 1 shrinks to a Capture-only `before-input-event` filter. If G-3 shows `\n` already bakes as multiple lines, slice 3b is partly a bug fix and moves up.

## 9. Decisions for you

The recommendations above are mine; the human-decision protocol (precedent sweep plus web research) has **not** been run on them. Three choices change behaviour you or agents already rely on:

- **D-1: Revise D-136?** Slice 1 changes how Ctrl+Z / Y / C reach the app: the Electron default Edit menu becomes routed. **Recommendation: yes.** Without it, M-1 and M-4 cannot use the conventional chords.
- **D-2: Flip Lock to on by default** (C-6)? Users who rely on the auto-return to Select will notice. **Recommendation: yes, with the one-shot preference.**
- **D-3: Name of the eraser:** "Smart eraser" (recommended) or "Clean up".

If you do not answer, the rulings in §5 stand, and each slice's plan records its decision.
