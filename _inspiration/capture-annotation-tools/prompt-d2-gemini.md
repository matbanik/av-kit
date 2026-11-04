# Gemini Deep Research — Screenshot Annotation Tools: Where User Expectations Are Heading, and the Smallest Set That Doesn't Feel Broken

## Current Capabilities (verified 2026-10-17)

You are running in Gemini Deep Research in the Gemini app. The requested model is Gemini 4 Argon.
Google does not say which model runs the app's Deep Research agent, so state the model label you
actually ran on at the top of your report.

**Available to you:** an editable research plan before the run starts, Google Search grounding,
file upload, and a cited report that can be exported to Docs.

**Known constraints:** do not use API-only features such as MCP tools, native charts or the Max
agent. Use plain Markdown tables instead of charts.

## Portal Setup

Before submitting:

1. In the model picker, select **Gemini 4 Argon** (AI Pro or Ultra plan), then choose
   **Deep Research**.
2. **Attach** `context-capture-annotation.md` from this folder. It describes av-kit's editor and
   how every tool behaves today. Read it before you research anything.
3. When the research plan appears, edit it so that areas A–G below are all still in it, then
   start.

## Context

**The product.** av-kit is a local-only Windows desktop app (Electron + React renderer, Python +
Pillow backend). Its Capture page takes a screenshot with F2 and opens it in an annotation editor
with seven tools: Select, Arrow, Box, Highlight, Text, Pixelate and Eraser. Marks are stored as
integer image-pixel JSON that AI agents can also read and write over MCP. The attached file holds
the full current behaviour and the data model.

**The problem.** Users report that a box, pixelate area, eraser area or text mark "cannot be
resized again" once drawn. That is true: only arrows have reshape handles, and every other mark
only moves. Other gaps found while checking this: a text mark's words cannot be edited again, the
canvas has no Ctrl+Z, the tools have no single-key shortcuts, and every colour change needs an
Apply click. The goal is to make the editor feel familiar to people who already use the common
screenshot annotators, while keeping it MVP-sized.

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
- ksnip and its kImageAnnotator library (GPL) are a common Flameshot replacement on Linux
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

Your slant is **trends and communities**. Find out what users of screenshot annotators actually
ask for, complain about and praise, and which behaviours have become expected in the last two
years. Look in Reddit, Hacker News, GitHub issues and discussions, Microsoft and Apple community
forums, app-store reviews and search "People also ask" questions. Give each finding a signal
strength (strong, moderate or weak) based on how many independent sources agree and how recent
they are. When communities disagree, reconcile the disagreement; do not average it.

Cover all seven areas. For each one, compare what users expect with av-kit's current behaviour in
the attached file.

- **A. Select and transform.** Resize handles for boxes, highlights, redaction areas and text
  (how many, and their hit size). What does resizing a text mark do: scale the font, or set a
  wrap width? Modifiers: Shift for aspect ratio or angle snap, Alt for from-centre. Nudge step and
  Shift+arrow. Multi-select, marquee, select all. Cursor feedback.
- **B. Shape tools.** Arrow head styles, line, ellipse, freehand pen, numbered step markers and
  callouts. Which are standard in a screenshot annotator, and which belong to diagram tools?
  Highlight: rectangle or freehand stroke, and plain alpha or multiply blend?
- **C. Text.** Single-line or multi-line. Which key commits text, and which adds a new line?
  Editing words again (double-click, Enter). Font, bold, outline or background plate, wrap and
  alignment.
- **D. Redaction.** Pixelate vs blur vs solid fill, and how safe each is against Depix-style
  recovery. Is an "eraser" that fills an area with the background colour a known pattern, and what
  do users expect a tool called "Eraser" to do? Can redaction areas be resized, and are their edges
  visible?
- **E. Style controls.** Default palette, and whether a colour applies on click or after an
  explicit Apply. Stroke and size control style (slider, presets, number field, scrub). Whether
  each tool remembers its own colour and size, and whether settings survive a restart. When a mark
  is selected, does changing a control restyle that mark, change the default for new marks, or
  both?
- **F. Toolbar, shortcuts, history and view.** Single-key tool shortcuts and any de facto standard
  mapping. Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z on the canvas, and how Electron or web apps route those
  chords to the canvas but leave them to text fields while the user types. Whether the tool stays
  active after drawing or switches back to Select. Copy, paste, duplicate, z-order and a canvas
  right-click menu. Zoom and pan conventions. Whether a before/after toggle is common.
- **G. Save, apply and export.** The usual "done" action: copy to clipboard, save or auto-save.
  Whether Ctrl+C on the canvas copies the annotated image. Editable project vs flattened image.
  Names for av-kit's three actions: Save overlay, Apply to image and Revert image.

## Required Output Structure

1. **Model and run info**: the model label and run date.
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
8. **Community signals (your slant)**: the top user requests and complaints for screenshot
   annotators, each with its signal strength, dated sources and the area (A–G) it belongs to.
   Also list behaviours that newer tools (2025–2026) handle differently from the older ones, and
   say whether users treat the newer behaviour as an improvement.

## Evidence Rules

Cite a specific URL for every claim, with a publication or commit date. Prefer posts and issues
from 2024 onward. For open-source apps, prefer the source file, docs page or release note over a
blog post. Describe GPL code's behaviour only; never quote it for reuse. Where sources conflict,
present both and say which is better-supported and why. Mark anything you inferred rather than
read as INFERRED, and anything you could not verify as UNVERIFIED rather than leaving it out.
