# av-kit Capture annotation editor — current state (attachment)

> Attach this file to the deep research prompt. It describes the product and how every
> annotation tool behaves **today**, as of 2026-10-29. The prompt holds the research questions.

## 1. Product

av-kit is a local-only Windows desktop toolkit. The renderer is Electron + React + TypeScript,
and the backend is Python FastAPI. Its **Capture** page grabs a screen region with a hotkey (F2)
and saves it as a PNG. A filmstrip lists the shots, and an editor lets the user annotate the
selected shot.

- The editor is an **SVG overlay** on the image, shown inside a normal app page. It is not a
  full-screen overlay.
- Marks are stored as a JSON list in **original image pixel coordinates**, as integers only.
  Zoom and window resizing never change stored marks.
- **Save overlay** (Ctrl+S) writes the list and a baked `<name>.annotated.png` copy. The copy can
  be PNG, JPEG or WebP. The original file is untouched.
- **Apply to image** bakes the saved marks into the original file. It asks for confirmation first
  and copies the original to a backup folder before it overwrites. A JPEG or WebP shot gets a new
  PNG copy instead. After Apply, the marks can no longer be edited.
- **Revert image** restores the newest backup.
- Baking is done in Python with **Pillow**. The SVG preview and the Pillow bake must look
  identical.
- An **MCP server** lets AI agents read and write the same annotation list. Any change to the data
  model is also a change to the agent API, so new fields must be optional, with defaults that keep
  existing overlays rendering exactly as they do now.
- Nothing is ever uploaded.

## 2. Mark data model (all integers, in image pixels)

```
arrow     {color, stroke_width, from:[x,y], to:[x,y]}
rect      {x, y, width, height, color, stroke_width}          // the "Box" tool
highlight {x, y, width, height, color, opacity}               // the GUI always writes opacity 0.35
text      {x, y, text (1..500 chars), color, font_size, bg_color|null}
pixelate  {x, y, width, height, block_size (2..100, default 10)}
eraser    {x, y, width, height}   // fill = most common colour on a ring just outside its border
```

A color is one of red, orange, yellow, green, blue, white or black, or a `#RRGGBB` value.

## 3. Everything on the editor overlay, and how it behaves today

### Tools row (icon buttons, in this order)

Select · Arrow · Box · Highlight · Text · Pixelate · Eraser · **Lock** (keep the tool) · Undo ·
Redo · Original · Annotated · Zoom out · Zoom in · Fit. Hovering any button shows a tooltip.

### Options row (contextual: shows the groups for the active tool, or for the selected mark when the tool is Select)

| Group | Shown for | Control |
|---|---|---|
| Color | arrow, box, highlight, text | 7 named swatches + hex text field. A pick is only a **candidate** until the user presses **Apply** (or **Cancel**). While a candidate is uncommitted, other actions are blocked ("Apply or Cancel color"). There is no system picker, no eyedropper, no recent colors and no opacity control. |
| Stroke | arrow, box | Number field. Dragging the label scrubs the value (Photoshop or Blender style). Mouse wheel or Up/Down over the field also changes it, with Shift for 10× steps. Each gesture is live-previewed and counts as one undo step. Range 1–100, default 3. |
| Size + Background | text | Size works like Stroke, range 1–400, default 16. Background is a color, or none. |
| Block | pixelate | Typed number, 2–100, default 10. No scrub. |
| (nothing) | eraser | No options at all. |

Style settings are **shared across tools**: the next tool uses the current color and stroke. They
are not remembered per tool, and not saved when the app restarts.

### Marks row (actions)

Remove mark · Save overlay · Apply to image · Revert image (shown only when a backup exists) ·
Open file · Open folder · Delete shot.

### Per-tool behaviour

- **Select**
  - Hit-testing runs from the topmost mark down. Highlight, pixelate and eraser count as hit
    anywhere inside their area. A box is hit only near its outline (10 CSS px). Text is hit on its
    background plate.
  - A selected **arrow** shows two endpoint handles that reshape it. **Every other mark (box,
    highlight, pixelate, eraser, text) shows one centre handle that only moves it. After drawing,
    none of those marks can be resized.** Users have reported this as a bug. Resize handles were
    deliberately left out of an earlier slice ("Select, translate, recolor, remove. No resize
    handles", approved 2026-09-20).
  - Handles have a 5 CSS px radius. Moves are clamped so a mark stays inside the image.
  - One mark is selected at a time: no marquee, no Ctrl or Shift-click multi-select, no Select All.
  - Arrow keys nudge the selection 1 px (no Shift step), or move the arrow end that was grabbed.
    A burst of nudges counts as one undo step.
  - Delete removes the selected mark. Escape cancels a drag or deselects.
- **Arrow**
  - Press and drag from tail to head.
  - Only one head style: a filled triangle scaled to the stroke width.
  - Always straight. No curve, double head or outline.
  - No modifier keys (no Shift angle snap).
- **Box**
  - Press and drag.
  - Outline only, sharp corners, no fill, no shadow.
  - No Shift (square) or Alt (from centre) modifiers.
  - There is no ellipse tool.
- **Highlight**
  - Press and drag a rectangle.
  - Filled with the current color at a fixed 0.35 alpha (plain alpha, not a multiply blend).
  - No freehand highlighter stroke.
- **Text**
  - A click places a **single-line** input. **Enter commits**, Escape cancels, and an empty commit
    is dropped.
  - Once committed, a text mark can be moved, recolored and given a new font size and background,
    but **its words cannot be edited again**. Double-click does nothing, so a typo means deleting
    the mark and retyping it.
  - Font is fixed to Segoe UI. No bold, italic, outline or shadow. No wrap width, no alignment.
  - There is no resize handle.
- **Pixelate**
  - Press and drag.
  - The area is shown as block averages of the **original pixels**.
  - Pixelate and eraser areas are drawn first, so drawn marks always sit on top of them,
    whatever order they were created in.
  - The area cannot be resized after drawing, and its edges are not shown once it is deselected.
- **Eraser**
  - Press and drag.
  - The area is filled solid with the most common colour on its border, which hides content on
    a flat UI background.
  - No options, no resizing.
  - It does **not** delete marks or strokes.
- There is **no** blur, solid black redaction, line, ellipse, freehand pen, numbered step marker,
  callout, spotlight, magnifier or crop tool.

### Tool persistence

The **Lock** toggle is off by default. With it off, the tool switches back to Select after each
mark is drawn. With it on, the tool stays.

### History

- Undo and redo are **toolbar buttons only**.
- Ctrl+Z, Ctrl+Y, Ctrl+Shift+Z, Ctrl+C, Ctrl+V, Ctrl+X and Ctrl+A are reserved for Electron's
  default Edit menu, which acts on text fields. They are not bound to undo, copy or select-all for
  marks on the canvas.
- History is kept per open image and lost when the user switches shots.
- Each finished gesture is one step.

### View

- **Original/Annotated** switches between the plain image and the image with marks.
- Zoom: mouse wheel, the + / − / Fit buttons, or Ctrl+= / Ctrl+- / Ctrl+0. Fit is the default.
- Pan: Space+drag or a middle-button drag.

### Shortcuts

- There are **no single-key tool shortcuts**.
- App-wide chords: F2 capture, Ctrl+S save overlay, and the zoom chords above.

### Mark commands

- No copy, paste or duplicate for marks.
- No z-order (bring forward or send back).
- No right-click menu on the canvas. The filmstrip has its own right-click menu: copy path, copy
  image, delete.

### Clipboard and export

- There is no "copy annotated image to clipboard" action in the editor, and no drag-out.
- There is no Save As with a chosen path.
- The page warns before the user leaves with unsaved changes.

## 4. Constraints on any recommendation

- **MVP first, but never broken-feeling.** Keep a feature if a user of Snipping Tool, ShareX,
  Greenshot, Flameshot, Snagit or macOS Markup would find its absence broken. Mark power-user
  features as Later.
- **Data model:** keep it additive and optional. Today's saved overlays and agent calls must keep
  working unchanged.
- **Preview and bake must match:** SVG on screen, Pillow on disk.
- **Licences:** ShareX, Greenshot, Flameshot and ksnip are GPL; kImageAnnotator is LGPL-3.0. Copy their
  **behaviour and rules only, never their code.** MIT/Apache projects (Excalidraw, Konva,
  Fabric.js and similar) may be studied for implementation patterns, with attribution. Closed
  apps (Snipping Tool, Snagit, CleanShot X, Shottr, Snipaste, macOS Markup) count only as UX
  baselines.
- Local-only: no upload or share targets.
