# ChatGPT Deep Research — Screenshot Annotation Tools: What Users Expect, and the Smallest Set That Doesn't Feel Broken

## Current Capabilities (verified 2026-10-17)

You are running in ChatGPT Deep Research. The requested model is GPT-6 Astra (the Pro reasoning
option, shown as "GPT-6 Pro" in some pickers) at the highest reasoning tier the plan offers.
OpenAI does not say which model runs Deep Research, so state the model label and reasoning tier
you actually ran on at the top of your report.

**Available to you:** clarifying questions and an editable research plan before the run starts,
live progress, site prioritization, file upload, read-only app and MCP connectors, and a cited
report that can be exported as Markdown, Word or PDF.

**Known constraints:** a run takes from a few minutes to about 30 minutes. Connectors are
read-only. Usage is metered by the in-product counter.

## Portal Setup

Before submitting:

1. In the composer, choose `+` → **Deep research**.
2. Select GPT-6 Astra ("GPT-6 Pro") if the picker offers it. Pick the highest reasoning tier.
   Leave Deep Research on its default model.
3. **Attach** `context-capture-annotation.md` from this folder. It describes av-kit's editor and
   how every tool behaves today. Read it before you research anything.
4. Use **prioritize** sites, not restrict, so the open web stays in scope. Prioritize:
   github.com, getsharex.com, getgreenshot.org, flameshot.org, ksnip.org, support.microsoft.com,
   support.apple.com, techsmith.com, cleanshot.com, shottr.cc, snipaste.com, excalidraw.com,
   konvajs.org, fabricjs.com, reddit.com, news.ycombinator.com.
5. When the clarifying questions appear, answer them from "Answers to likely clarifying
   questions" below. When the research plan appears, check that areas A–G are all still in it
   before you start.

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

**Answers to likely clarifying questions.**

- Platform: Windows 10 and 11 first. macOS apps count as UX evidence only.
- Users: people who capture screenshots for bug reports, notes, chat messages and how-to docs.
  They are not designers.
- Scope: annotation editing only. Capture modes, upload and OCR are out of scope.
- "MVP-must" means a user of the reference apps would call its absence broken. "MVP-should" means
  its absence causes real friction but has a workaround. "Later" is everything else.
- Length: as long as the matrix needs, with a short summary on top.

## Research Objective

Your slant is **competition and breadth**. Survey as many reference apps as you can for every
area below, count how many do each behaviour, and use that count as the main evidence for the
industry baseline. Quote dated user complaints from issue trackers, forums and reviews where a
behaviour is missing or done badly.

Cover all seven areas. For each one, compare the reference apps with av-kit's current behaviour
in the attached file.

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

1. **Model and run info**: the model label, reasoning tier and run date.
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
8. **Competitive extras (your slant)**: the apps users most often name as "the one to beat" for
   annotation, and the complaints that show up most often across issue trackers and reviews, with
   dated quotes.

## Evidence Rules

Cite a specific URL for every claim, with a publication or commit date. For open-source apps,
prefer the source file, docs page or release note over a blog post. Describe GPL code's behaviour
only; never quote it for reuse. Where sources conflict, present both and say which is
better-supported and why. Mark anything you inferred rather than read as INFERRED, and anything
you could not verify as UNVERIFIED rather than leaving it out.
