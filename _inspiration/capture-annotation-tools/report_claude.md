# av-kit Capture editor: what to fix, in what order, and what to leave out

The first thing to fix is to give every box-shaped mark (box, highlight, pixelate, eraser and text) the same 8 resize handles, add Ctrl+Z / Ctrl+Y on the canvas and let users edit a text mark's words again. After that, remove the colour Apply gate and add a solid-fill redaction tool as the default. Pixelation in av-kit today is a plain average over fixed blocks, and that is exactly what Depix attacks: Debian ITP bug #1029078 (2023-01-17) describes Depix as attacking "the common linear box filter. A linear box filter takes a box of pixels, and overwrites the pixels with the average value of all pixels in the box."

**Model and run info:** Claude (Anthropic); exact model build not exposed to the agent · Effort: low · Run date: Thursday 2026-10-29.

## TL;DR

- **Must fix first:** av-kit falls short of the baseline in four places users would call broken: marks can't be resized, text can't be edited again, the canvas has no Ctrl+Z, and the only redaction is deterministic pixelation. ShareX's docs and Greenshot's help both say you can move and resize existing shapes, and both document Ctrl+Z / Ctrl+Y and double-click to edit text.\[1\] Resizing needs no data-model change, because box-shaped marks already store x, y, width and height.
- **Rulings:** stay on the tool after drawing (Lock on by default) and keep the new mark selected. Apply colour on click. Text corner handles scale the font; a wrap-width side handle comes Later. Solid fill is the default redaction. Rename "Eraser" to "Smart Eraser" (ShareX's name for the same behaviour).\[1\] Rename the save actions to Save / Flatten into original… / Restore original.
- **Evidence quality:** snypr and Greenshot behaviour is confirmed from primary docs. omasnap is only partly confirmed: the features are in the omacom/omasnap README, not the 15-commit tobi/omasnap snapshot. The Cap issue #1864 and Playwright PR #40238 claims could not be verified. The ">96%" depixelation figure appears only in a vendor blog with no primary source behind it. The primary demonstration is Bishop Fox's open-source Unredacter, which BleepingComputer reports "reconstructing original text in its entirety and correctly from the given pixelated input."

---

## 1. Model and run info

- Model: Claude (Anthropic). The agent cannot see the exact build string.
- Effort: low.
- Run date: 2026-10-29.
- Research limits: the search budget ran out. One verification subagent was used, for the Cap and Playwright items. macOS Markup, Snagit (Windows) and ksnip/kImageAnnotator are thinly sourced, so many of their cells are UNVERIFIED.

## 2. Behaviour matrix

### 2a. Verdicts on the prior findings (2026-10-29 pass)

| Prior finding | Verdict | Evidence |
|---|---|---|
| Cap #1864: editor switches back to Select after each drawing, settings can't be chosen before drawing, tools don't keep their own settings | **UNVERIFIED** | Fetching the URL directly was refused, and neither the lead nor the subagent got it from search. The subagent found nearby Cap issues: #1862 ("Automatically close Editor window after clicking 'Copy to Clipboard'", bot comment dated May 21, 2026) and #1733 ("Make possible to copy from text in screenshot mode").\[2\]\[3\] Neither matches. The same complaint does exist in other projects: TobiasRoland123/tobyshot issue #27 says "After taking a screenshot and adding an annotation, TobyShot currently switches back to Select (the pointer). Keep the tool I used active…".\[4\] Others are SAIDEEPBHANGE/CanvasCraft #1 ("Pencil tool automatically switches to selection mode after drawing"), wadjakorn/capz PR #118 ("sticky" tools) and fayazara/Screendrop #51.\[5\]\[6\]\[7\] Cap's own release notes only add "Draw freehand before copying or saving screenshots".\[8\] |
| snypr: 8 box handles, arrow/line endpoints, text corners scale font and sides set wrap, double-click re-edits, colour per tool, keys R/O/A/L/H/F/N/T/B/X | **CONFIRMED**, with two qualifiers | The README (MIT; AUR package first submitted 2026-08-14; release 0.4.1 on 2026-09-22) says box shapes "get eight handles", "the corner handles scale the font size while the side handles set a wrap width", and "Double-click a text annotation to re-open its editor".\[9\]\[10\]\[11\] Qualifier 1: each tool remembers its own colour/style only "across switches within a session", so it is not persisted. Qualifier 2: there is also C (Crop), and "after you commit a shape the editor returns to Select mode automatically".\[11\] |
| omasnap (github.com/tobi/omasnap): V, Shift aspect/45°, Alt centre, Shift+arrow 10 px, double-click/Enter re-edit, Alt+D, Ctrl+C PNG, secure redaction | **PARTIALLY CONFIRMED** | The tobi/omasnap README is a 15-commit snapshot. It confirms V, double-click to re-edit text, Ctrl+Z, Ctrl+Shift+Z/Ctrl+Y, Ctrl+C "Copy PNG only", and "Creation tools return to Select after one placement".\[12\] The rest (Shift 1:1/45°, Alt from centre, Shift+arrow 10 px, Enter on selected text, Alt+D duplicate, "secure redaction with opaque or randomized non-spatial mosaic output") is in the **omacom/omasnap** README: MIT, 570 stars, releases in August 2026.\[13\]\[14\] Tobias Lütke's X post of 2026-08-22 also lists "Actually secure redactions".\[15\] |
| Playwright PR #40238 (2026-04-16): 8 resize handles, Enter saves text, Shift+Enter new line | **UNVERIFIED** | Fetching the URL directly was refused, and the subagent's searches did not find it. Related items that did turn up: PR #32248 ("feat(trace viewer): show Screenshot instead of Snapshot", 2024), PR #43321 (trace-viewer frame fit, bot comment 2026-10-13), and `playwright-cli show --annotate`, where the user "draws boxes on the live page and types comments".\[16\]\[17\]\[18\] Release dates are v1.59.0 on 2026-04-01 and v1.62.0 on 2026-07-24.\[19\] Do not cite the PR. |
| Depix-style tools recover >96% of pixelated text in some cases | **PARTIALLY CONFIRMED, weakly sourced** | screensnap.pro/blog/redact-text (published 2026-07-09, updated 2026-10-12) says "researchers have rebuilt pixelated text with over 96% accuracy" and "Security researchers have reported over 96% accuracy on common fonts", but names no study.\[20\] It is a vendor blog that promotes its own product. positive.security/blog/video-depixelation (Fabian Bräunlein, 2022-01-25) does **not** give a 96% figure. It describes Depix (2020) as taking "a De Bruijn sequence with expected characters with the same font settings as the blurred image", and it shows a separate multi-frame method for video.\[21\]\[22\] Treat 96% as unsupported, and the underlying risk as well-supported: Bishop Fox's open-source Unredacter is reported by BleepingComputer as "reconstructing original text in its entirety and correctly from the given pixelated input." |
| ksnip and kImageAnnotator (GPL) are a common Flameshot replacement on Linux | **PARTIALLY CONFIRMED** | The ksnip CHANGELOG confirms that kImageAnnotator is its annotation library and records the tool-switch history (see row F4).\[23\] The "common Flameshot replacement" claim is UNVERIFIED. The GPL licence is taken from the attachment and was not re-read here. |

### 2b. Matrix

Columns: **ST** Snipping Tool (Win 11) · **SX** ShareX · **GS** Greenshot · **FS** Flameshot · **KS** ksnip · **SG** Snagit · **CS** CleanShot X · **SH** Shottr · **SP** Snipaste · **MM** macOS Markup · then the newer OSS apps **SN** snypr and **OM** omasnap (evidence only, not counted) · **av** av-kit today · **#** = number of the 10 reference apps confirmed to share the behaviour. U = UNVERIFIED. Each cell names its source. Sources: SX = ShareX "Image Editor" docs page (getsharex.com, ©2026) and ShareX changelog. GS = Greenshot Help page (getgreenshot.org, help version 1.2.10). FS = DefKey Flameshot list and Gentoo wiki (secondary). KS = ksnip CHANGELOG. SG = TechSmith "Snagit Shortcuts for Windows" PDF (Feb 2024) and Snagit Mac shortcuts PDF. CS = CleanShot changelog and features pages, and the pie-menu shortcut list (secondary). SH = Shottr site and v1.9.3 release page. SP = Snipaste site, changelog v2.4–v2.6 and download page. ST = Windows Central guide, ElevenForum Redact-text tutorial, Microsoft Learning Center (secondary/vendor). SN = snypr README. OM = omacom/omasnap README.

| Behaviour | ST | SX | GS | FS | KS | SG | CS | SH | SP | MM | SN | OM | av today | # |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 Box-like marks resizable after drawing | U | Y (SX: "move it, resize it") | Y (GS: "move or resize existing shapes") | U | U | U | Y (Podfeet 2022: blur "move it around or resize") | U | U | U | Y, 8 handles | Y | **N**: centre move handle only | 3 |
| A2 Text resize semantics | U | U | Text drawn as a sized box (GS) | U | U | U | "easier way to resize Text" (CS changelog), mode U | Font-size slider grows label (Podfeet 2023) | U | U | Corners scale font, sides wrap | Width handle wraps; wheel scales | **None** | n/a |
| A3 Shift keeps aspect while resizing | U | U | Y (GS) | U | U | U | U | U | U | U | U | Y | N | 1 |
| A4 Shift constrains while drawing | U | Y, line 45° (SX) | Y, square; lines 15° steps (GS) | U | U | U | U | U | U | U | U | Y, 1:1 and 45° | N | 2 |
| A5 From-centre modifier | U | U | **Ctrl** (GS) | U | U | U | U | U | U | U | U | **Alt** | N | 1 |
| A6 Nudge 1 px / Shift 10 px | U | Y 1/10 (SX) | Y arrows (+Shift, step U) (GS) | U | U | U | U | U | Arrow keys move (SP v1.13.2) | U | Shift = larger | Y 1/10 | 1 px, no Shift | 3 |
| A7 Multi-select | U | U | Shift-click (GS) | U | U | Select all Cmd+A (SG Mac) | U | U | U | U | U | Marquee | **N** | 2 |
| B1 Ellipse | Shapes (ST, oval U) | Y | Y (E) | Y (C circle) | U | U | Y (E) | Y ovals | Y | U | Y | Y | **N** | 6 |
| B2 Line | U | Y | Y | Y (D) | U | U | Y (L) | U | Linestrip | U | Y | Y | **N** | 5 |
| B3 Freehand pen | Y (ballpoint) | Y | Y | Y (P) | U | U | Y (D) | Y | Y | U | Y | Y | **N** | 7 |
| B4 Numbered step markers | U | Y (N) | U | U | U | Y (1) | Y counter (C) | Y | U | U | Y | Y | **N** | 4 |
| B5 Callout / speech balloon | U | Y (O) | U | U | U | Y Callout | U | Pointer labels | U | U | N | N | **N** | 2 |
| B6 Highlight form | Stroke | Rect region | Rect "highlight text" | Marker stroke (M) | U | U | Smart text highlighter | Highlighter | Marker pen | U | Y | Stroke, text-snapping | Rect, 0.35 alpha | n/a |
| C1 Text words editable again | U | Y "editable text" | Y double-click | U | U | U | U | U | Y "easy text re-edit" (v2.6) | U | Y double-click | Y double-click / Enter | **N** | 3 |
| C2 Enter commits, Shift+Enter newline | U | U | Y (GS) | U | U | U | U | U | U* | U | U | Shift+Enter always adds line | Enter commits, single line | 1 |
| C3 Text styling beyond colour/size | U | Bold/italic/underline/outline | U | U | U | U | 6 styles | U | Outline option | U | U | 3 fonts, outline, pill | Background only | 3 |
| D1 Pixelate | U | Y (P) | Y Pixelize | Y (B) | U | U | Y | Y | Y Mosaic | U | N | Y randomized | Y deterministic | 6 |
| D2 Blur | U | Y (B) | Y | U | U | U | Y Gaussian option | Y | Y Gaussian | U | Y | N | **N** | 5 |
| D3 Opaque/solid redaction tool | Y Redact text (Ctrl+R), Quick redact | Filled rectangle | U | U | U | U | Y "Black Out" redaction style (CS changelog) | Y "erase" | U | U | Y (X, solid black) | Y | **N** | 4 |
| D4 Randomized pixelate labelled anti-depix | N | N | N | N | U | U | Y | U | U | U | N | Y | **N** | 1 |
| D5 Fill-with-surrounding-colour tool | U | Y **Smart Eraser** (W) | U | U | U | U | U | U | Eraser (behaviour U) | U | N | N | Y "Eraser" | 1 |
| E1 Control change restyles selected mark AND sets next default | U | Y adjust options on selection (SX) | Y (GS) | U | U | U | U | U | U | U | Y | Y per-layer colour | Selected mark only, via Apply | 2 |
| E2 Explicit Apply/Cancel for colour | none found | none found | N (INFERRED) | none found | U | U | U | U | U | U | N | N (keys 1–8 set colour) | **Y** | 0 found |
| E3 Colour remembered per tool | U | U | U | U | U | U | U | U | Y PRO "separate colors for different shapes" default on (v2.4) | U | Y (session) | U | **N**, shared | 1 |
| E4 Size by keys or wheel | U | U | U | Wheel thickness (FS) | U | U | `[` `]` (secondary) | Cmd+[ ] (review) | Wheel, 1/2, [ ] (v2.4) | U | U | Wheel | Scrub, wheel, Up/Down on field | 4 |
| F1 Single-key tool shortcuts | U | Y | Y | Y | U | Y (A, S, 1) | Y | Y (V, A, T) | Y (T, B, E) | U | Y | Y | **N** | 7 |
| F2 R/A/T/E/L/F/H map | — | R A T E L F H, V select | R A T E L F H | R A T, C circle, D line | U | A, S square | A T E L, V move, P pixelate | V A T | T, B pencil, E eraser | U | R A T L H F, O ellipse | R A T L F H E, V | none | n/a |
| F3 Canvas Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z | U | Y all three | U | Ctrl+Z, Ctrl+Shift+Z | U | Cmd+Z / Cmd+Shift+Z (Mac) | Y (keys U) | U | Undo/redo (keys U) | U | Ctrl+Z only | Y all three | **Toolbar only** | 3 |
| F4 Tool stays active after drawing | U | U | INFERRED stays | U | **Y by default** since 1.10 | U | U | **Y** ("keeps selected tool") | U | U | N (back to Select) | N (back to Select) | N unless Lock on | 2 |
| F5 Duplicate | U | Ctrl+D | U | U | U | Ctrl+click | U | Opt+drag | U | U | U | Alt+D | **N** | 3 |
| F6 Z-order | U | Home/PgUp/PgDn/End | U | U | U | Ctrl+Shift+F/B | U | Selected goes to front | U | U | U | U | **N** (redaction always below) | 3 |
| F7 Canvas right-click menu | U | Y | U | U | U | U | U | U | U | U | U | Right-click = back to Select | **N** | 1 |
| F8 Copy/paste marks | U | Ctrl+C / Ctrl+V | Ctrl+V pastes image | U | U | U | U | Cmd+C / Cmd+V | Ctrl+Shift+C/V | U | U | U | **N** | 4 |
| F9 Zoom/pan | U | Ctrl+wheel, middle-drag | U | U | U | U | U | Z + click | U | U | U | Ctrl+wheel, middle-drag, +/−/0 | Wheel, Ctrl+=/−/0, Space/middle-drag | 1 |
| F10 Before/after toggle | U | U | U | U | U | U | U | U | U | U | U | U | Y | 0 found |
| G1 Copy annotated image shortcut | U | Ctrl+Shift+C | Ctrl+Shift+C | Ctrl+C | U | U | U | Cmd+C / Esc copies PNG | U | U | Save to clipboard sink | Ctrl+C | **N** | 4 |
| G2 "Flatten" names baking marks into pixels | U | Y Ctrl+Shift+F | U | U | U | Y Ctrl+Shift+T | U | U | U | U | U | U | "Apply to image" | 2 |
| G3 Editable project kept | U | Editable until flattened | "Save objects to file" | U | U | U | U | U | U | U | U | Recents keep layers | Y overlay JSON | 2 |
| G4 Save As with path | U | Ctrl+Shift+S | Ctrl+Shift+S | Ctrl+S dialog | U | Cmd+Shift+S (Mac) | U | Cmd+Shift+S | U | U | U | Ctrl+Shift+S | **N** | 5 |

*C2 Snipaste: a third-party re-implementation PR (taida957789/ScreenPaste #6) says Snipaste's text box uses "Esc and Enter commit, Shift+Enter adds a line".\[24\] That is secondhand, so the cell stays U.

## 3. Industry baseline

**A. Select and transform**
- Once drawn, shapes can be selected, moved **and resized**: ShareX docs, Greenshot help, snypr (8 handles), omasnap.\[1\]\[11\]\[25\]
- Shift constrains while drawing (square, angle snap). Greenshot snaps lines in 15° steps; ShareX and omasnap use 45°.\[1\]\[14\]\[25\]
- Arrow keys nudge the selection, and Shift gives a bigger step (10 px in ShareX and omasnap).\[1\]
- From-centre is split: Greenshot uses Ctrl, omasnap uses Alt. Multi-select by Shift-click (Greenshot) or marquee (omasnap) is common but not universal.\[14\]\[25\]

**B. Shape tools**
- Standard set: rectangle, ellipse, arrow, line, freehand, text, highlight (6–7 of the 10 have each).
- Numbered steps are mainstream in the newer and commercial tools (ShareX, Snagit, CleanShot X, Shottr).\[1\]\[26\]\[27\]\[28\] Callouts appear mostly in ShareX and Snagit.\[1\]\[29\]
- Highlight comes in two forms: a rectangle region (ShareX, Greenshot) or a stroke/marker (Snipping Tool, Flameshot, Snipaste, CleanShot X).\[1\]\[30\]\[31\] No source documents a multiply blend (UNVERIFIED).

**C. Text**
- Text stays editable after commit, by double-click (Greenshot, snypr, omasnap; Snipaste "easy text re-edit").\[11\]\[14\]\[25\]\[32\]
- Enter commits and Shift+Enter adds a line (Greenshot help; omasnap uses Shift+Enter for new lines).\[14\]\[25\]
- Basic styling (bold, outline, background plate) is common in ShareX, CleanShot X and omasnap.\[1\]\[33\]

**D. Redaction**
- Pixelate (6/10) and blur (5/10) are the usual obfuscation tools. Solid redaction appears in Snipping Tool (OCR "Redact text", Ctrl+R), CleanShot X (its changelog lists "Added Black Out redaction tool style"), Shottr ("erase"), snypr and omasnap.
- Two apps randomize pixelation specifically to defeat depixelation: CleanShot X ("Added randomization to Pixelate tool to prevent depixelization") and omasnap.\[14\]\[33\]
- The "fill with surrounding colour" tool exists, and ShareX calls it **Smart Eraser**: "Paint over an area using a sampled nearby color".\[1\]

**E. Style controls**
- Changing an option restyles the selected element and also sets the default for the next one (Greenshot: "change the options for an existing element after selecting it, but also for the next element"; snypr).\[11\]\[25\]
- No reference app was found with an explicit Apply/Cancel colour gate.
- Size is changed by keys or wheel in most apps (`[`/`]`, mouse wheel, 1/2).\[34\]\[35\]
- Per-tool colour memory exists (Snipaste PRO default, snypr per session).\[35\] It is not universal.\[11\]

**F. Toolbar, shortcuts, history, view**
- Single-key tool shortcuts are near-universal (7/10). The ShareX/Greenshot map (R, E, L, A, F, T, H, plus V for select) is the de facto standard.\[1\]
- Canvas Ctrl+Z / Ctrl+Y (and Ctrl+Shift+Z) are standard in ShareX, Flameshot and omasnap.\[1\]\[14\]\[36\]
- Duplicate, z-order and copy/paste of marks are common in the fuller editors (ShareX, Snagit, Shottr).\[1\]\[26\]\[27\]
- Zoom with Ctrl+wheel and pan with middle-drag (ShareX, omasnap).\[1\]\[14\]

**G. Save, apply, export**
- Copying the annotated image to the clipboard is a first-class action, on Ctrl+Shift+C (Greenshot, ShareX) or Ctrl+C (Flameshot, Shottr, omasnap).\[1\]\[14\]\[25\]\[36\]
- "Flatten" is the name for baking marks into pixels (ShareX Ctrl+Shift+F, Snagit Ctrl+Shift+T).\[1\]\[27\]
- Save As with a chosen path is standard (5/10).

## 4. Gap list

| Gap | Rating | Evidence |
|---|---|---|
| Box, highlight, pixelate, eraser and text cannot be resized | **broken-feeling** | User reports in the attachment. ShareX, Greenshot and CleanShot X resize. snypr and omasnap ship it. |
| Text words cannot be edited again | **broken-feeling** | Greenshot, ShareX, Snipaste, snypr and omasnap all re-edit. A typo forces delete-and-retype. |
| No canvas Ctrl+Z / Ctrl+Y | **broken-feeling** | ShareX, Flameshot and omasnap bind these, and every Windows user expects Ctrl+Z. The attachment says the chords go to Electron's Edit menu. |
| Colour Apply/Cancel gate blocks other actions | **friction** (borders on broken) | No reference app found with a gate. Greenshot and snypr apply directly. |
| No copy-annotated-image action | **broken-feeling** for chat and bug-report users | Greenshot, ShareX, Flameshot, Shottr and omasnap all have one. |
| Only deterministic pixelation; no solid redaction | **broken-feeling (security)** | Depix works on a linear box filter (positive.security, 2022-01-25).\[21\]\[37\] Depix author Sipke Mellema explains why fixed-block averaging is attackable: "pixelizing the same values will result in the same pixelated block, and pixelizing the same text using the same block locations will result in the same block values" (quoted by SyncedReview, 2020-12-11). av-kit's pixelation uses fixed blocks over the original pixels. CleanShot X and omasnap randomize; Snipping Tool, snypr and omasnap offer solid fill. |
| No single-key tool shortcuts | **friction** | 7/10 have them. |
| Tool reverts to Select by default | **friction** | Contested (see rulings). ksnip and Shottr moved to keeping the tool. |
| Shared style across tools, not persisted | **friction** | Snipaste and snypr remember per tool. |
| "Eraser" fills instead of erasing | **friction** (expectation mismatch) | Snipping Tool's eraser removes ink (Wikipedia: "pens, an eraser, and a highlighter"). ShareX names the fill behaviour "Smart Eraser".\[1\]\[30\] |
| No Shift 10 px nudge, Shift aspect or Alt centre modifiers | **friction** | ShareX, Greenshot and omasnap have them. |
| Redaction edges invisible after deselect | **friction** | You can't find a pixelate area on a flat background to fix it. Same-coloured pixelate is invisible (INFERRED). |
| No ellipse, line or freehand | **friction** | 5–7/10 have each. |
| No step markers | **nice-to-have** (friction for how-to docs) | 4/10, all fuller editors. |
| No duplicate, z-order, right-click menu or mark copy/paste | **nice-to-have** | Mainly ShareX, Snagit and Shottr. |
| No multi-select | **nice-to-have** | Greenshot and omasnap. |
| No Save As | **nice-to-have** | The file and folder buttons are a workaround. |
| No callout, blur or spotlight | **nice-to-have** | Mostly the commercial apps. |

## 5. Recommended spec

Effort is for Electron + React/TS SVG overlay, FastAPI + Pillow bake, integer JSON, and the MCP schema: S ≈ under half a session, M ≈ one session, L ≈ more than one.

**A. Select and transform**
- MVP-must: 8 handles (4 corners, 4 edges) on rect, highlight, pixelate, eraser and redact; drag to resize, with integer clamping to the image. **M**
- MVP-must: handles drawn about 8 CSS px with a hit radius of about 10 CSS px (today 5 px), plus resize cursors (nwse, nesw, ns, ew) and a move cursor over the body. INFERRED sizing, matching av-kit's existing 10 px box-outline hit. **S**
- MVP-should: Shift locks aspect while resizing and gives a square while drawing; Alt draws or resizes from the centre (omasnap; Greenshot's Ctrl conflicts with Windows Ctrl+click habits). **S**
- MVP-should: Shift+arrow nudges 10 px. **S**
- Later: Shift-click multi-select, marquee, Ctrl+A select all. **L**

**B. Shape tools**
- MVP-should: Shift snaps the arrow to 45° (ShareX and omasnap; Greenshot uses 15°). **S**
- MVP-should: Line tool (an arrow with no head). **S**
- MVP-should: Ellipse tool. **M** (see bake flag)
- Later: numbered step marker. **M**
- Later: freehand pen. **M**
- Later: arrow head styles. **S**
- Later: highlight multiply blend. **M**
- Non-goal: callouts.

**C. Text**
- MVP-must: double-click a text mark, or press Enter with it selected, to edit its words in place; Esc cancels. **M**
- MVP-must: multi-line text, where Enter commits and Shift+Enter adds a line (Greenshot). **M**
- MVP-must: text corner handles scale font_size (snypr). **S**, after the transform module.
- MVP-should: bold toggle. **S**
- Later: side handles set a wrap width. **L**
- Later: outline style. **M**
- Later: alignment. **S**

**D. Redaction**
- MVP-must: a new **Redact** tool (opaque solid fill, black by default), first in the redaction group. **M**
- MVP-must: redaction areas keep a dashed editor-only outline when deselected. It is not baked. **S**
- MVP-should: rename Eraser to "Smart Eraser" with the tooltip "Cover with the surrounding colour". **S**
- MVP-should: Pixelate tooltip and options say "Hides from casual view; not secure for passwords". **S**
- Later: randomized pixelate (seeded noise per block). Dark Reading reports that Bishop Fox's Dan Petro found Depix's "results to be very sensitive to noise in the input image", which supports adding noise, but Petro still says "The only secure way to redact text is a black bar that completely covers the text." **M**
- Non-goal: blur.

**E. Style controls**
- MVP-must: a colour click applies immediately: to the selected mark (one undo step) and as the active tool's default. Remove Apply/Cancel. **S**
- MVP-should: each tool remembers its colour and size, saved to settings so they survive a restart. **S**
- MVP-should: `[` / `]` change stroke or size. **S**
- Later: recent colours, eyedropper. **M**

**F. Toolbar, shortcuts, history, view**
- MVP-must: canvas Ctrl+Z undo, Ctrl+Y and Ctrl+Shift+Z redo when focus is not in a text field. **S–M**
- MVP-should: single keys V Select, A Arrow, R Box, H Highlight, T Text, P Pixelate, X Redact, W Smart Eraser, with tooltips showing the key. This follows the ShareX map. X and W are ShareX/snypr precedents for Redact and Smart Eraser.\[1\] **S**
- MVP-should: Lock on by default, and the mark just drawn stays selected with its handles. **S**
- MVP-should: Ctrl+D duplicate. **S**
- Later: z-order (Home/End/PgUp/PgDn). **M**
- Later: right-click menu. **M**
- Later: mark copy/paste. **M**
- Keep: Original/Annotated toggle (no reference app was found with it, but it is cheap and useful for checking redactions).

**G. Save, apply, export**
- MVP-must: **Copy image**: Ctrl+Shift+C always copies the baked PNG; Ctrl+C does too when no text field has focus. **M** (needs the bake, then Electron `clipboard.writeImage`).
- MVP-should: rename the three actions (see rulings). **S**
- Later: Save As… (Ctrl+Shift+S). **S**
- Later: drag-out. **M**

## 6. Data-model impact

Every field is optional, and its default renders today's overlays unchanged.

| Item | New fields (default) | Pillow-parity risk |
|---|---|---|
| Resize handles (rect, highlight, pixelate, eraser) | **None**: they edit the existing x, y, width, height | None |
| Text corner scaling | **None**: edits font_size (keep 1–400) | Low |
| Multi-line text | Allow `\n` inside `text` (default: no `\n`); optional `line_height` (int px; default = Pillow's `multiline_text` spacing used today) | **Medium.** SVG `<tspan dy>` and Pillow `multiline_text(spacing=…)` must share one line-height formula. Document it in the MCP schema. |
| Bold | `bold: bool` (false) | Medium: needs the same Segoe UI Bold file on both sides. |
| Wrap width (Later) | `wrap_width: int\|null` (null = no wrap) | **Hard.** Line breaking depends on glyph metrics and kerning. Mitigation: break lines in Python with Pillow's measurement, then store the explicit breaks. |
| Redact tool | New mark type `redact {x, y, width, height, color}` (color default "black") | None (solid rectangle). Additive type, but older agents won't know it, so version the MCP tool description. |
| Randomized pixelate (Later) | `pixelate.mode: "average"\|"random"` ("average"); `seed: int` (fixed when the mark is created) | Medium: SVG must render the same per-block noise, so precompute the block colours in Python and send them to the renderer. |
| Arrow line / head styles | `arrow.head: "triangle"\|"none"` ("triangle") | Low |
| Ellipse | New type `ellipse {x, y, width, height, color, stroke_width}` | **Medium-hard.** Pillow `ellipse()` is not anti-aliased, unlike SVG. Supersample (draw at 4× and downscale) or accept tiny edge differences. |
| Highlight multiply (Later) | `highlight.blend: "alpha"\|"multiply"` ("alpha") | Medium: SVG `mix-blend-mode` vs `ImageChops.multiply`, with alpha compositing order to match. |
| Step marker (Later) | New type `step {x, y, number, color, size}` | Medium (circle anti-aliasing and centred digits). |
| Per-tool style memory, Lock default, shortcuts, clipboard | **None** in marks (app settings only) | None |
| Blur (non-goal) | none | **Hard.** SVG `feGaussianBlur stdDeviation` and Pillow `GaussianBlur(radius)` use different kernels and edge handling. |

## 7. Non-goals

- **Blur tool**: weaker than solid fill for secrets, and hard to match between SVG and Pillow.
- **Callouts and speech balloons**: diagram territory. A box plus text covers it.
- **Freehand pen in MVP**: a polyline data model, plus smoothing parity, for little value in bug reports.
- **Spotlight, magnifier, emoji, cursor stamps**: polish features from ShareX and CleanShot X with no "broken" signal.
- **Multi-select and marquee in MVP**: an L-sized interaction model, and Greenshot users get by with single selection plus duplicate.
- **Mark copy/paste across shots**: Ctrl+C is reserved for "copy image", the higher-value meaning for these users.
- **Crop and cut-out**: these change the image geometry and would break the coordinate contract with agents. Out of scope too.
- **Text rotation and arrow curves**: they need a transform matrix in the data model, a large API change.
- **Auto-OCR redaction (Snipping Tool's Quick redact)**: OCR is out of scope.\[38\]

## 8. Strategy

### 8.1 Rulings on the contested choices

1. **Tool-lock default: stay on the tool.** Make Lock on by default and keep the mark just drawn selected with its handles, so a colour click fixes it at once. Esc or V returns to Select.
   - Against: the two newest OSS editors switch back (snypr: "after you commit a shape the editor returns to Select mode automatically"; omasnap: "Creation tools return to Select after one placement").\[11\]\[12\]
   - For: ksnip tried switching back and reversed it ("Make switch 'to select tool after drawing item' by default disabled", release 1.10.0).\[23\] Shottr changed to "keeps selected tool after the object is created (it's quicker now to add multiple arrows, counters, etc.)".\[39\] tobyshot PR #29 and Screendrop #51 show users asking for this.\[7\]\[40\]
   - What tips it: auto-select of the new mark answers the "fix what I just drew" need that motivates switching back (wadjet PR #199, LorcanChinnock/shot #157).\[41\]\[42\]
   - Better supported: staying, because two apps moved *toward* it after real use.
2. **Colour gate: remove it and apply on click.** No reference app has an Apply/Cancel step. Greenshot applies options to the selected element and to the next one.\[25\] Each click is one undo step, so Undo replaces Cancel.
3. **Text resize: corners scale the font now; a wrap width comes Later.** snypr defines both (corners scale the font, sides set a wrap width), and omasnap uses a width handle.\[11\]\[14\] Font scaling maps onto the existing `font_size` with zero parity risk. Wrap needs identical line breaking in SVG and Pillow, so ship explicit Shift+Enter lines first.
4. **Default redaction: solid fill.**
   - Depix assumes a linear box filter and matching font settings (positive.security, 2022).\[21\]\[37\] av-kit's pixelate is block averages of the original pixels over fixed blocks, and Depix author Sipke Mellema explains why that is attackable: "pixelizing the same values will result in the same pixelated block, and pixelizing the same text using the same block locations will result in the same block values" (SyncedReview, 2020-12-11).
   - CleanShot X added randomization "to prevent depixelization".\[33\] Dan Petro, Lead Researcher at Bishop Fox and author of Unredacter, concludes in his post "Never Use Text Pixelation To Redact Sensitive Information" (quoted by Ax Sharma in BleepingComputer): "The bottom line is that when you need to redact text, use black bars covering the whole text."
   - Keep pixelate as a labelled "not secure" option, and add randomization Later.
5. **Eraser: keep the behaviour and rename it "Smart Eraser".**
   - ShareX ships the identical behaviour under that name ("Paint over an area using a sampled nearby color"; gHacks 2020-09-16 notes it "only works well with a single solid color background").\[1\]\[43\]
   - A bare "Eraser" means remove strokes in Snipping Tool, the Windows default, so the plain name misleads (INFERRED from Snipping Tool's pen/eraser toolset).\[30\]
   - Don't present it as redaction. On a non-flat background it can leave a visible patch.
6. **Naming:** "Save overlay" → **Save** (Ctrl+S; keeps marks editable and writes the annotated copy). "Apply to image" → **Flatten into original…**, the industry verb in ShareX ("Flatten annotations into the image") and Snagit (Flatten).\[1\]\[27\] "Revert image" → **Restore original**. Add **Copy image** next to them.

### 8.2 Shared transform module

Yes: one module should serve rect, highlight, pixelate, eraser, redact and text. All six are axis-aligned boxes in integer image pixels.

- **Input:** a mark's box (x, y, w, h) plus a "kind" capability flag. Text uses `scaleFont` instead of `resizeBox`.
- **Output:** a new box, or a new font_size.
- **Scope:**
  - hit-testing handles in CSS px and converting to image px at the current zoom;
  - 8 handles, plus the arrow's existing 2-endpoint mode, behind the same interface;
  - modifiers (Shift aspect, Alt centre);
  - min size (1 px; 2 × block_size for pixelate) and clamping to the image;
  - integer rounding in one place;
  - cursor feedback;
  - committing one undo step per drag;
  - keyboard nudge (1 / 10 px).
- **Exposed to MCP:** the same clamp and round rules, so agent-written and user-resized marks validate the same way.
- **First slice:** corner and edge resize for rect, highlight, pixelate and eraser, with the cursor, clamping and one undo step per drag. No modifiers, no text. This closes the reported bug with **no data-model change**.

### 8.3 ERRC grid

| Eliminate | Reduce |
|---|---|
| The colour Apply/Cancel gate. The name "Eraser" for a fill. Deterministic pixelation as the only privacy tool. Ctrl+Z/Y being swallowed by the Edit menu on the canvas. | Three similar save buttons down to Save / Copy image / Flatten. The Lock toggle becomes a preference (default on). Typed-only block size becomes presets. Choices per tool (no blur, no callouts). |
| **Raise** | **Create** |
| Redaction safety (solid by default, warning on pixelate, randomized pixelate Later). One consistent transform model across all box marks. Keyboard parity with the ShareX/Greenshot map. Undo coverage (canvas chords, every restyle). | Preview equals bake, guaranteed for humans and agents, as a stated contract per mark type. Agent-safe transforms (MCP shares the clamp and round rules). Editor-only outlines on redaction areas, plus the existing Original/Annotated toggle as a "check my redactions" step that no reference app was found to offer. |

### 8.4 Ordered slices (about one session each)

1. **Input router (shared).** One keydown handler on the editor root that ignores events whose target is `input`, `textarea` or `contentEditable`. Bind Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z / Delete / Esc / single keys there. Replace Electron's `role: 'undo'`/`'redo'` Edit-menu items with custom accelerators that send IPC to the renderer, which then routes to the text field or the canvas by focus. Menu roles act on the focused webContents' editing commands (flaviocopes Electron course; electron/electron #15728), so they never reach an SVG canvas (INFERRED).\[44\]\[45\] No dependencies. **M**
2. **Transform module, slice 1** (8 handles for rect, highlight, pixelate, eraser; cursors; one undo step per drag). Depends on 1 for Esc and undo. **M**
3. **Colour on click, plus per-tool style memory** (persisted), restyling the selection. Depends on 1. **S**
4. **Text editing:** double-click or Enter re-edit, multi-line with Shift+Enter, corner font scaling. Depends on 2 and 3. Pillow line-height parity tests. **M**
5. **Redact tool, plus the Smart Eraser rename, editor-only outlines and the pixelate warning.** New `redact` type in the JSON schema, Pillow and MCP. Depends on 2. **M**
6. **Copy image and the renames** (Ctrl+Shift+C / Ctrl+C → bake → `clipboard.writeImage`; Save / Flatten into original… / Restore original). Depends on 1. **S–M**
7. **Tool-lock default on, auto-select the new mark, Shift and Alt modifiers, Shift+arrow 10 px.** Depends on 2 and 3. **S**
8. **Should-tier shapes:** Line (head "none"), Shift 45° snap, Ellipse with supersampled Pillow bake, Ctrl+D duplicate. Depends on 2. **M**
9. **Later:** step markers, randomized pixelate, wrap width, z-order and right-click menu, multi-select.

### 8.5 Strongest counter-argument

The case against: av-kit's users are Windows people whose real baseline is **Snipping Tool**, a pen-and-shapes editor.\[30\] Snipping Tool's ink isn't resizable and it isn't known to have single-key tool shortcuts (both UNVERIFIED). So "broken" for this audience may be a lower bar than ShareX/Greenshot parity, and the two most carefully designed new editors (snypr, omasnap) deliberately switch back to Select after each mark. On this view the true MVP-must is only resize, Ctrl+Z and Copy image. Text re-edit and the Redact tool could wait.

Why the list still stands:
- Resize and text re-edit come from av-kit's own user reports, not from parity.
- Redaction is a silent failure: the user can't see that pixelation is reversible. Snipping Tool itself ships solid "Redact text".\[38\]\[46\]\[47\]\[48\]

What would change the list:
- Session telemetry showing marks are rarely adjusted after drawing (for example, under 5% of marks are deleted and redrawn).
- A five-user test with Snipping-Tool-only users showing that nobody tries to resize or re-edit.
- An agent-API review showing most redactions are created by agents, not people. In that case the MCP default matters more than the UI default.

## Sources

1. [Image Editor - ShareX](https://getsharex.com/docs/image-editor.html)
2. [\[UX/Feature Request\]: Automatically close Editor window after clicking "Copy to Clipboard" · Issue #1862 · CapSoftware/Cap · GitHub](https://github.com/CapSoftware/Cap/issues/1862)
3. [Make possible to copy from text in screenshot mode · Issue #1733 · CapSoftware/Cap · GitHub](https://github.com/CapSoftware/Cap/issues/1733)
4. [Keep annotation tools active and edit existing annotations without switching to Select · Issue #27 · TobiasRoland123/tobyshot · GitHub](https://github.com/TobiasRoland123/tobyshot/issues/27)
5. [Pencil tool automatically switches to selection mode after drawing · Issue #1 · SAIDEEPBHANGE/CanvasCraft · GitHub](https://github.com/SAIDEEPBHANGE/CanvasCraft/issues/1)
6. [fix(editor): one Esc deselects and returns to Select (CP-0069) by capz-bot · Pull Request #118 · wadjakorn/capz · GitHub](https://github.com/wadjakorn/capz/pull/118)
7. [Feature request: Keep annotation tools active after drawing · Issue #51 · fayazara/Screendrop · GitHub](https://github.com/fayazara/Screendrop/issues/51)
8. [Releases · CapSoftware/Cap · GitHub](https://github.com/CapSoftware/Cap/releases)
9. [Release 0.4.1 · noirbizarre/snypr · GitHub](https://github.com/noirbizarre/snypr/releases/tag/0.4.1)
10. [AUR (en) - snypr-bin](https://aur.archlinux.org/packages/snypr-bin)
11. [GitHub - noirbizarre/snypr: A GTK4-based screenshot, annotation, and live-drawing tool for Hyprland](https://github.com/noirbizarre/snypr)
12. [GitHub - tobi/omasnap: Native Wayland screenshot and annotation editor for Omarchy and Hyprland](https://github.com/tobi/omasnap)
13. [Releases · omacom/omasnap · GitHub](https://github.com/omacom/omasnap/releases)
14. [GitHub - omacom/omasnap: Native Wayland screenshot and annotation editor for Omarchy and Hyprland](https://github.com/omacom/omasnap)
15. [tobi lutke on X: "omasnap update: \~70 PRs since I first shared it 📝 Multiline text ✂️ Cut out sections 🔎 Spotlight + magnifier 📌 Screenshots pinnable across workspaces 🛡️ Actually secure redactions 🎨 Editable vector annotations 🔍 OCR ↩️ Crash-proof undo ⚡ Native Wayland capture Still one ti… / X](https://x.com/tobi/status/2090988868539470143)
16. [feat(trace viewer): show Screenshot instead of Snapshot by Skn0tt · Pull Request #32248 · microsoft/playwright · GitHub](https://github.com/microsoft/playwright/pull/32248)
17. [fix(trace-viewer): fit the browser frame to phone-sized snapshots by pavelfeldman · Pull Request #43321 · microsoft/playwright · GitHub](https://github.com/microsoft/playwright/pull/43321)
18. [playwright-cli/skills/playwright-cli/SKILL.md at main · microsoft/playwright-cli · GitHub](https://github.com/microsoft/playwright-cli/blob/main/skills/playwright-cli/SKILL.md)
19. [Releases · microsoft/playwright · GitHub](https://github.com/microsoft/playwright/releases)
20. [How to Redact Text in Screenshots & PDFs Safely (2026)](https://www.screensnap.pro/blog/redact-text)
21. [Recovering redacted information from pixelated videos | Positive Security](https://positive.security/blog/video-depixelation)
22. [Experts explain what 'technology to remove corrections such as mosaics' is - GIGAZINE](https://gigazine.net/gsc_news/en/20220126-redacted-information-pixelated-videos/)
23. [ksnip/CHANGELOG.md at master · ksnip/ksnip · GitHub](https://github.com/ksnip/ksnip/blob/master/CHANGELOG.md)
24. [feat: implement Snipaste's shortcuts, with every in-app key rebindable by windasd · Pull Request #6 · taida957789/ScreenPaste · GitHub](https://github.com/taida957789/ScreenPaste/pull/6)
25. [Help](https://getgreenshot.org/help/)
26. [Shottr v1.9.3 is out!](https://shottr.cc/newversion.html)
27. [Capture Shortcuts Global Capture Print Screen Start a Region Selection Shift](https://www.techsmith.com/blog/wp-content/uploads/2024/02/Snagit-Shortcuts-for-Windows.pdf)
28. [CleanShot X shortcuts for Mac](https://www.pie-menu.com/shortcuts/cleanshot)
29. [Copyright © 2024 TechSmith Corporation. All rights reserved. Snagit Help](https://www.techsmith.com/learn/wp-content/uploads/2025/01/Snagit-Help-2024-EN.pdf)
30. [Snipping Tool](https://en.wikipedia.org/wiki/Snipping_Tool)
31. [Snipaste](https://www.snipaste.com/)
32. [Changelog](https://docs.snipaste.com/changelog)
33. [CleanShot X](https://cleanshot.com/changelog)
34. [CleanShot X Keyboard Shortcuts: The Complete Guide for Mac — KeyScreen Blog](https://keyscreenapp.com/cleanshot-x-keyboard-shortcuts)
35. [Snipaste Downloads](https://www.snipaste.com/download.html)
36. [Flameshot keyboard shortcuts ‒ DefKey](https://defkey.com/flameshot-shortcuts)
37. [New Unredacter Tool Extracts Text From Pixelized Images](https://latesthackingnews.com/2022/02/20/new-unredacter-tool-can-extract-text-from-pixelized-images/)
38. [How to get started with the Snipping Tool app in Windows 11](https://www.windowscentral.com/how-get-started-snipping-tool-app-windows-11)
39. [Shottr](https://shottr.cc/)
40. [Keep annotation tools active and edit annotations without switching to Select by TobiasRoland123 · Pull Request #29 · TobiasRoland123/tobyshot · GitHub](https://github.com/TobiasRoland123/tobyshot/pull/29)
41. [Editor: toolbar changes should update the annotation just drawn · Issue #157 · LorcanChinnock/shot · GitHub](https://github.com/LorcanChinnock/shot/issues/157)
42. [fix(macos): a placed Annotation stays selected for editing by mia-riezebos · Pull Request #199 · mia-cx/wadjet · GitHub](https://github.com/mia-cx/wadjet/pull/199)
43. [ShareX update brings a Smart Eraser, new hotkeys and more - gHacks Tech News](https://www.ghacks.net/2020/09/16/sharex-update-brings-a-smart-eraser-new-hotkeys-and-more/)
44. [Add an application menu — Electron Course](https://flaviocopes.com/courses/electron/add-an-application-menu/)
45. [Calling Cmd+Z (webContents.undo()) and Shift+Cmd+Z (webContents.redo()) have no effect inside a \<webview\> tag · Issue #15728 · electron/electron · GitHub](https://github.com/electron/electron/issues/15728)
46. [How to Black out (Redact) Text in a Screenshot with Snipping Tool - La De Du](https://ladedu.com/how-to-blacken-out-text-in-a-screenshot-with-snipping-tool/)
47. [How to Redact Text in Snipping Tool (Windows 11)](https://framed-shot.com/guides/how-to-redact-in-snipping-tool/)
48. [Redact Text on Captured Screenshot Image with Snipping Tool app in Windows 11](https://www.elevenforum.com/t/redact-text-on-captured-screenshot-image-with-snipping-tool-app-in-windows-11.17985/)
