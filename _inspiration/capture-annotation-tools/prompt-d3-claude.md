# Claude Research — Screenshot Annotation Tools: Which Changes Earn Their Place in an MVP Editor

## Current Capabilities (verified 2026-10-17)

You are running as Claude Opus 5.5 in claude.ai Research mode, with adaptive thinking always on.

**Available to you:**
- Multi-agent research with web search: an orchestrator, parallel subagents and a citation pass.
- Uploaded files.
- Artifacts.
- Code execution.

**Known constraints:**
- Research mode needs Pro or above.
- Heavily chained questions do worse than independent branches, so the objective below is split
  into independent branches.
- Give explicit arguments in the report. Do not report hidden reasoning.

## Portal Setup

Before submitting:

1. Select **Claude Opus 5.5** in the model picker.
2. Turn **Research** on.
3. Set Effort to **Max**, or **High** if Max is not offered. Thinking is always on for this
   model, so Effort is the only dial.
4. **Attach** `context-capture-annotation.md` from this folder. It describes av-kit's editor:
   the product, the mark data model, every control on the editor and how each tool behaves today,
   and the constraints on any recommendation. Read it before you research anything.

## Context

**The product.** av-kit is a local-only Windows desktop app (Electron + React renderer, Python +
Pillow backend). Its Capture page takes a screenshot with F2 and opens it in an annotation editor
with seven tools: Select, Arrow, Box, Highlight, Text, Pixelate and Eraser. Marks are stored as
integer image-pixel JSON that AI agents can also read and write over MCP, so every data-model
change is also an agent-API change. The attached file holds the full current behaviour.

**The problem.** Users report that a box, pixelate area, eraser area or text mark "cannot be
resized again" once drawn. That is true: only arrows have reshape handles, and every other mark
only moves. Other gaps found while checking this: a text mark's words cannot be edited again, the
canvas has no Ctrl+Z, the tools have no single-key shortcuts, and every colour change needs an
Apply click. The goal is to make the editor feel familiar to people who already use the common
screenshot annotators, while keeping it MVP-sized. The team ships in small slices of about one
session each.

**Prior findings from a 2026-10-29 pass.** Verify or refute each one; do not assume them.

- Cap (open-source screen recorder): users complain that the editor switches back to Select after
  each drawing, that settings cannot be chosen before drawing, and that tools do not keep their
  own settings (github.com/CapSoftware/Cap/issues/1864).
- snypr (newer open-source annotator): boxes get 8 resize handles, arrows and lines get endpoint
  handles. For text, corner handles scale the font and side handles set a wrap width.
  Double-click edits text again. Colour is remembered per tool. Single-key tool shortcuts
  R/O/A/L/H/F/N/T/B/X (github.com/noirbizarre/snypr).
- omasnap (newer open-source annotator): V selects. Shift keeps the aspect ratio or snaps lines to
  45°, and Alt draws from the centre. Shift+arrow nudges 10 px. Double-click or Enter edits text
  again. Alt+D duplicates. Ctrl+C copies the annotated PNG. "Secure" redaction uses opaque fill or
  a randomized mosaic (github.com/tobi/omasnap).
- Playwright's trace-viewer screenshot annotator (PR #40238, 2026-04-16) added 8 resize handles.
  Enter saves text, and Shift+Enter adds a new line (github.com/microsoft/playwright/pull/40238).
- Depix-style tools are reported to recover more than 96% of pixelated text in some cases
  (screensnap.pro/blog/redact-text, updated 2026-10-12; positive.security/blog/video-depixelation).
- ksnip (GPL) and its kImageAnnotator library (LGPL-3.0) are a common Flameshot replacement on Linux
  (github.com/ksnip/ksnip).

**Reference apps.** Snipping Tool (Windows 11), ShareX, Greenshot, Flameshot, ksnip, Snagit,
CleanShot X, Shottr, Snipaste and macOS Markup. Newer open-source annotators (snypr, omasnap, Cap)
count as evidence of where the field is going. Licences: GPL apps are for behaviour only. MIT and
Apache projects (Excalidraw, Konva, Fabric.js) may be studied for implementation patterns. Closed
apps are UX baselines only.

**Definitions.**

- Platform: Windows 10 and 11 first. macOS apps count as UX evidence only.
- Users: people who capture screenshots for bug reports, notes, chat messages and how-to docs.
  They are not designers.
- Scope: annotation editing only. Capture modes, upload and OCR are out of scope.
- "MVP-must" means a user of the reference apps would call its absence broken. "MVP-should" means
  its absence causes real friction but has a workaround. "Later" is everything else.

## Research Objective

Your slant is **strategy and differentiation**. Decide which changes a small team should make,
in what order, and which familiar features it should deliberately leave out. Where the reference
apps disagree, rule on it and explain why.

Work these areas as **independent branches**. For each one, compare the reference apps with
av-kit's current behaviour in the attached file.

- **Branch A. Select and transform.** Resize handles for boxes, highlights, redaction areas and
  text (how many, and their hit size). What does resizing a text mark do: scale the font, or set a
  wrap width? Modifiers: Shift for aspect ratio or angle snap, Alt for from-centre. Nudge step and
  Shift+arrow. Multi-select, marquee, select all. Cursor feedback.
- **Branch B. Shape tools.** Arrow head styles, line, ellipse, freehand pen, numbered step markers
  and callouts. Which are standard in a screenshot annotator, and which belong to diagram tools?
  Highlight: rectangle or freehand stroke, and plain alpha or multiply blend?
- **Branch C. Text.** Single-line or multi-line. Which key commits text, and which adds a new
  line? Editing words again (double-click, Enter). Font, bold, outline or background plate, wrap
  and alignment.
- **Branch D. Redaction.** Pixelate vs blur vs solid fill, and how safe each is against
  Depix-style recovery. Is an "eraser" that fills an area with the background colour a known
  pattern, and what do users expect a tool called "Eraser" to do? Can redaction areas be resized,
  and are their edges visible?
- **Branch E. Style controls.** Default palette, and whether a colour applies on click or after an
  explicit Apply. Stroke and size control style (slider, presets, number field, scrub). Whether
  each tool remembers its own colour and size, and whether settings survive a restart. When a mark
  is selected, does changing a control restyle that mark, change the default for new marks, or
  both?
- **Branch F. Toolbar, shortcuts, history and view.** Single-key tool shortcuts and any de facto
  standard mapping. Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z on the canvas, and how Electron or web apps
  route those chords to the canvas but leave them to text fields while the user types. Whether the
  tool stays active after drawing or switches back to Select. Copy, paste, duplicate, z-order and
  a canvas right-click menu. Zoom and pan conventions. Whether a before/after toggle is common.
- **Branch G. Save, apply and export.** The usual "done" action: copy to clipboard, save or
  auto-save. Whether Ctrl+C on the canvas copies the annotated image. Editable project vs
  flattened image. Names for av-kit's three actions: Save overlay, Apply to image and Revert
  image.

Then synthesize across the branches:

1. **Rulings on the contested choices.** At minimum, rule on:
   - the tool-lock default (stay on the tool, or switch back to Select);
   - the colour Apply/Cancel gate (keep it, or apply on click);
   - text resize (font scale or wrap width);
   - pixelate vs blur vs solid fill as the default redaction;
   - what the Eraser tool should do, and what it should be called;
   - the Save overlay / Apply to image naming.
2. **A shared transform module.** Should one handle module serve box, highlight, pixelate, eraser
   and text? What should it cover, and what is a sensible first slice?
3. **An ERRC grid** (Eliminate / Reduce / Raise / Create) for av-kit's editor compared with the
   industry baseline.
4. **The strongest counter-argument** to your MVP-must list, and the evidence that would change
   it.

## Required Output Structure

1. **Model and run info**: the model, effort and run date.
2. **Behaviour matrix**: one row per behaviour across areas A–G, one column per reference app, plus
   an "av-kit today" column and a "count" column. Cite each cell, or mark it UNVERIFIED.
3. **Industry baseline**: for each area, the behaviour most apps share, in 3–6 bullets.
4. **Gap list**: each place where av-kit differs from the baseline, rated *broken-feeling*,
   *friction* or *nice-to-have*, with the evidence behind the rating.
5. **Recommended spec**: for each area, MVP-must, MVP-should and Later items. Each item gets a
   one-line user-visible behaviour and an effort estimate (S, M or L) for the stack in the
   attached file.
6. **Data-model impact**: the new mark fields each item needs, each optional with a default that
   renders existing overlays unchanged. Flag any item the Pillow bake would find hard to match.
7. **Non-goals**: features you considered and left out, each with a one-line reason.
8. **Strategy (your slant)**:
   - the rulings on the contested choices;
   - the shared transform module;
   - the ERRC grid;
   - an ordered list of slices of about one session each, with shared work first and
     dependencies named;
   - the strongest counter-argument.

## Evidence Rules

Cite a specific URL for every claim, with a publication or commit date. For open-source apps,
prefer the source file, docs page or release note over a blog post. Describe GPL code's behaviour
only; never quote it for reuse. Where sources conflict, present both and say which is
better-supported and why. Mark anything you inferred rather than read as INFERRED, and anything
you could not verify as UNVERIFIED rather than leaving it out.
