# Capture crop — agent-first design

> **Date:** 2026-11-08 · **Status:** inspiration design, not a plan. MEU ids, ACs and the build-plan
> rows are assigned when a planning session adopts it. · **Research:** `pomera_web_search`
> (tavily, exa), receipts `C:/Temp/av-kit/crop-research-{1..14}-*.md`. Local sweep receipts
> `C:/Temp/av-kit/crop-sweep.txt` and `crop-magick-usage.txt`. Pillow probe receipt
> `crop-pillow-probe.txt`. · **Human decisions:** one, D-1 (§13), ruled 2026-11-08: a crop writes
> a new shot and leaves the source untouched.

## 1. The ask

> "web search and create design in _inspiration for crop feature in the capture page. ImageMagic
> is currently being used as the tool on this system by AI agents. I want the agent to be able to
> use it in av-kit in the GUI, MCP and API so it works on screenshots or any ohter images provided.
> Agentic utility goes first, GUI for human is second. Pick the most widely known UI and operation
> in the GUI, for agentic do the web research and use reasoning to establish what would be the best
> choice." (Mat, 2026-11-08)

The request rules out "no crop feature". It also supersedes the earlier agent opinion that crop is
out of scope (`report_claude.md:234`). That opinion's concern still applies: the agent coordinate
contract must survive. §6.1 answers it.

## 2. The shape in one screen

Agents crop for two different reasons, and the design keeps them apart.

| Agent need | What av-kit adds | API | MCP (`avkit_capture`) | GUI |
|---|---|---|---|---|
| **Look closer.** Read small text, check a detail. This is the most common local use (§4). | **Region view.** Returns the region's pixels, scaled to a known size. Writes no file. | `GET /captures/{id}/image?x&y&width&height&unit&max_edge` | `image` gains region fields | Zoom (exists) |
| **Make a deliverable.** A tight screenshot for a doc, a listing or a report. | **Crop.** Writes a new shot; the source is untouched (D-1, Human-approved). | `POST /captures/{id}/crop` | `crop` | Crop tool, key **C** |
| **Work on any image**, not only av-kit captures. | **Import.** Copies a local image into the inbox as a shot. | `POST /captures` `{mode:"import"}` | `import` | Drag and drop, **Import image…**, Ctrl+V |

One rule ties these together: **every coordinate is in the shot's original pixels.** The optional
`unit: "fraction"` is a convenience for agents that read positions off a scaled view. Every
response echoes the result in pixels.

The GUI follows the Windows Photos and Photoshop crop pattern:

- a box that starts as the whole image, with 8 handles;
- the area outside the box dimmed, with a rule-of-thirds grid while dragging;
- an aspect-ratio dropdown;
- Enter commits as **Save as copy**, Esc cancels.

## 3. Local facts

| # | Fact | Evidence |
|---|---|---|
| L-1 | av-kit has no crop operation in the API, MCP or GUI. The capture page has no crop tool. | `context-capture-annotation.md:119`; route list `packages/api/src/avkit_api/routes/captures.py:183-309`; `CaptureTool` union `ui/src/renderer/src/features/capture/CaptureViewport.tsx:65` |
| L-2 | MCP cannot bring in an outside image. `capture` grabs only the screen (fullscreen or region). The API's `register` mode accepts only a path already inside the inbox. | `mcp-server/src/toolsets/capture.ts:126-148`; `services/capture.py:406-413`, `:827-839` (`path is outside the capture inbox`) |
| L-3 | Listing scans the inbox root and registers any `.png/.jpg/.jpeg/.webp` it finds (source `Scan`). An agent with a shell can already copy a file into the inbox, but it must know `inbox_dir`. | `services/capture.py:54`, `:374-383` |
| L-4 | When a file is registered twice, the registering source wins over a `Scan` row. A file written by crop or import keeps its own source even if a scan sees it first. | `services/capture.py:853-895` (comment at `:863`) |
| L-5 | The MCP `image` action returns one image content item. Past 7.8 MB it fails and tells the agent to open the file. There is no region or size control. | `capture.ts:12`, `:153-162`; `registry.ts:124`, `:342-361` |
| L-6 | Marks are stored in **original-image pixels** in the sidecar `{stem}.ann.json`. The bake `{stem}.annotated.*` is rebuilt from it. | `domain/capture.py:134-259`; `services/capture.py:758-777` |
| L-7 | Saving clamps a mark's **origin** into the image and never shrinks its size. Arrow endpoints are clamped one at a time, which can change an arrow's direction. Crop therefore needs its own geometric clipping (§6.5). | `services/capture.py:917-952` |
| L-8 | The MVP lock says "Original PNG: Immutable after save". Flatten is the one governed exception: it takes a backup first, and a JPEG/WebP shot gets a `{stem}-converted.png` copy instead. Destructive MCP actions need `confirm: true` and the user's acceptance in the IDE. | `docs/build-plan/09-screenshot-capture.md:66`; `services/capture.py:586-635`, `:747-756`; `capture.ts:185-196` |
| L-9 | The copy-naming precedent is `{stem}-converted.png`, then `_2` and so on. The next free name is checked against both the file system and the catalog rows. | `services/capture.py:65-66`, `:747-756` |
| L-10 | Convert already accepts any local absolute path from an agent. Import would follow that precedent. | `mcp-server/src/toolsets/convert.ts:12` |
| L-11 | The minimum edge is 8 px for grabs, region grabs and the overlay. | `domain/capture.py:25`, `:95-116`; `capture.ts:136-148` |
| L-12 | `CaptureSource` has six members: Hotkey, Gui, McpFullscreen, McpRegion, McpInteractive, Scan. The register wire map accepts `hotkey`, `gui` and `scan`. | `domain/enums.py:209-217`; `domain/wire.py:89-93` |
| L-13 | The GUI already has box handles: handle points, resize, hit-testing and cursors. A crop box can reuse them. | `features/capture/capture-transform.ts:28`, `:61`, `:82`, `:105` |
| L-14 | The planned tool letters are V, A, R, H, T, X (Redact) and E, with L, O and N later. **C is free.** Shortcuts go through the page-scoped shortcut registry and never fire inside inputs. None of these letter keys is built yet. | `_inspiration/capture-annotation-tools/synthesis.md:134`, `:218` |
| L-15 | Precedent for a render without a file: MEU-104's planned `POST /captures/{id}/render` bakes posted marks and writes nothing. | `09-screenshot-capture.md:939` |
| L-16 | An earlier proposal already named the agent risk: "translate any model-view downscaling explicitly, preserve crop origin". | `docs/proposals/2026-09-19-p9-annotation-adaptation-proposal.md:233` |
| L-17 | Pillow 13.0.0 `Image.crop` pads out-of-bounds areas with **black** and raises no error. A box past the edge must be clamped first, or the crop silently grows a black border. | `C:/Temp/av-kit/crop-pillow-probe.txt` (`13.0.0 (10, 10) (255, 255, 255) (0, 0, 0)`) |
| L-18 | The Pillow adapter already crops and pastes, for pixelate and eraser. No ImageMagick dependency exists or is needed. | `packages/infrastructure/src/avkit_infra/capture/adapter.py:152-160`, `:184` |

## 4. How agents crop here today

The source is every distinct shell command that invoked `magick` in this machine's Claude Code
transcripts (receipt `C:/Temp/av-kit/crop-magick-usage.txt`, script in the session scratchpad).

| Operation | Commands | What it was for |
|---|---|---|
| Any `magick` call | 77 | Across ebay (22), matbanik-info (21), zorivest (12), av-kit (9), creative-writing (8), carmen (4), windows-os (1) |
| `identify` (read dimensions) | 30 | Checking size before choosing coordinates |
| `-resize` | 21 | Mostly thumbnails, plus upscaling crops |
| `-crop` | 12 | — |
| `-crop` then `-resize` | 7 | **Look closer**: `-crop 600x200+550+560 +repage -resize 200%` to read a stamp on a listing photo (ebay) |
| `+repage` | 9 | Clearing the virtual canvas after a crop, a well-known footgun |
| `-gravity` | 9 | Edge crops such as `-gravity South -crop …` on rendered PDF pages (carmen) |
| `-extent` | 6 | Cover-crop thumbnails |
| `-trim` | 0 | — |

The three patterns:

1. **Inspect.** Crop a region, upscale it, look at it, throw the file away.
2. **Deliverable.** Crop screenshots into named files for a document, for example
   `-crop 960x940+0+100 +repage -strip slot-exemption-form.png` (creative-writing). One source was on
   the Desktop, outside any inbox.
3. **Iterate.** Re-crop from the untouched raw until it is right, never cropping a crop.

Each pattern maps to one capability in §2: region view, crop to a new shot, and import.

## 5. Research findings

| # | Finding | Label | Source |
|---|---|---|---|
| R-1 | Claude returns coordinates in the **resized** image it saw, not the original. The standard tier caps the long edge at 1568 px and about 1568 tokens; the high-resolution tier (4.7 and later) caps it at 2576 px and 4784 tokens. Tokens are ceil(w/28)·ceil(h/28). A 1920×1080 screenshot is seen at 1456×819 on the standard tier. | Official doc | [Vision](https://platform.claude.com/docs/en/build-with-claude/vision), [Coordinates and bounding boxes](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates) |
| R-2 | Anthropic's own coordinate guide maps model coordinates back through **relative** values: `x / resized_w`. | Official doc | [Coordinates and bounding boxes](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates) |
| R-3 | Other models use different conventions. Gemini uses `[y_min, x_min, y_max, x_max]` normalized to 0–1000. Qwen2.5-VL uses absolute pixels of its resized input. Qwen2-VL and Qwen3-VL use 0–1000. Only a fraction of the image means the same thing to all of them. | Official doc, issue thread | [Google Cloud bbox docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/bounding-box-detection), [Qwen issue #866](https://github.com/QwenLM/Qwen3-VL/issues/866), [ms-swift Qwen3-VL](https://swift.readthedocs.io/en/v4.0/BestPractices/Qwen3-VL-Best-Practice.html) |
| R-4 | Claude's computer-use `zoom` takes a region in screenshot pixels, crops it from the **full-resolution** capture, and fits it into the screenshot frame with the aspect ratio kept. The zoomed image is never a new coordinate frame. | Official doc and reference code | [Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), [computer.py](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/computer_use_demo/tools/computer.py) |
| R-5 | Cropping and upscaling the relevant region measurably improves MLLM perception of small details, training-free. OpenAI's o3 crops and zooms as part of its reasoning. | Paper, vendor | [ViCrop, arXiv 2502.17422](https://doi.org/10.48550/arxiv.2502.17422), [arXiv 2310.16033](https://doi.org/10.48550/arxiv.2310.16033), [Thinking with images](https://openai.com/index/thinking-with-images) |
| R-6 | MCP crop tools converge on the same contract. The region is x/y/width/height (or left/top). The output is a **new file** and the source is untouched. Out-of-bounds boxes are **clamped**. Paths go in and out, not inline bytes. | Vendor practice | [image-mcp `crop`](https://glama.ai/mcp/servers/TOBYCAI/image-mcp/tools/crop) ("write it to a NEW file (source unchanged)… automatically clamped"), [sharp-mcp](https://github.com/greatSumini/sharp-mcp), [imagician](https://github.com/flowy11/imagician), [mcp-image-tools](https://pypi.org/project/mcp-image-tools/) |
| R-7 | Mochify's crop takes "four numbers, fractions of the upright picture from the top-left corner, never pixels". A box past the edge "is trimmed to the picture". | Vendor practice | [Mochify MCP](https://mochify.app/mcp) |
| R-8 | Tool design: consolidate actions instead of adding tools, return high-signal and token-efficient responses, write actionable errors, and evaluate descriptions with real tasks. | Vendor guidance | [Writing effective tools for agents](https://www.anthropic.com/research/writing-tools-for-agents) |
| R-9 | ImageMagick's `-crop WxH+X+Y` keeps a virtual-canvas offset unless followed by `+repage`. Without `+X+Y` it **tiles** the image into many outputs. `-gravity` persists into later operations. | Official examples | [ImageMagick crop usage](https://imagemagick.org/Usage/crop) |
| R-10 | The Windows Photos crop flow: Edit (Ctrl+E), crop opens by default, drag the corner handles, pick from an aspect-ratio dropdown (16:9, 4:3, square…), then **"Save as copy" to preserve the original, or "Save" to overwrite**. Snipping Tool also has a crop button. | How-to, vendor | [screensnap](https://www.screensnap.pro/blog/crop-screenshot-windows), [BatchPhoto](https://www.batchphoto.com/blog/top-10-tools-to-crop-photos-on-windows), [Snipping Tool](https://support.microsoft.com/en-us/windows/apps/use-snipping-tool-to-capture-screenshots) |
| R-11 | Photoshop's crop: **C** selects the tool, **X** swaps width and height, **O** cycles overlays such as the rule of thirds, Enter commits. With **Delete Cropped Pixels** off, the crop is non-destructive and can be re-adjusted. | Expert how-to | [Julieanne Kost](https://jkost.com/blog/2017/05/essential-tips-for-cropping-in-photoshop-cc.html), [Photoshop Essentials](https://www.photoshopessentials.com/basics/how-to-crop-images-photoshop-cc) |

Swept but not cited: macOS Preview and Google Photos (receipt 8 returned only off-topic results).
Lightroom's R/X/A keys are general knowledge, not sourced here. Neither changes a choice below.

## 6. Agent design (first priority)

### 6.1 One coordinate frame

- **The frame is always the shot's original pixels.** That is the frame `get` reports
  (`width`, `height`) and the frame marks are stored in (L-6). A view image is never a frame, which
  matches computer-use `zoom` (R-4).
- **Pixels are canonical.** Integers, origin top-left, `x`/`y`/`width`/`height`, which is the same
  shape as `capture` region (L-11), `BBox` and every MCP crop precedent (R-6).
- **`unit: "fraction"` is optional.** Values run from 0 to 1 against the original's width and
  height. Use it when the coordinates come from looking at a scaled image. Models scale differently
  and use different number conventions (R-1, R-3); a fraction means the same in all of them (R-2,
  R-7).
  - Conversion rounds outward: `left = floor(x·W)`, `top = floor(y·H)`,
    `right = ceil((x+width)·W)`, `bottom = ceil((y+height)·H)`. The result is then clamped. Rounding
    outward never cuts off what the agent asked for.
- **Every response echoes the applied box in pixels**, plus the scale for views. The agent never
  has to guess how a coordinate was understood.
- **This answers the concern in `report_claude.md:234`.** A crop never changes an existing shot's
  geometry. The crop is a new shot with its own frame, and the response gives its offset in the
  source (`applied.x`, `applied.y`), so source px = crop px + offset.

### 6.2 S1 — region view (`image` gains a region)

This extends the existing action instead of adding a `zoom` action (R-8: fewer, richer actions).
It writes no file.

```ts
// avkit_capture image — new optional fields
{
  action: "image", id, variant?: "original" | "annotated",
  x?: number, y?: number, width?: number, height?: number,  // all four or none
  unit?: "px" | "fraction",                                 // default "px"
  max_edge?: number                                         // 64..2576
}
```

| Rule | Value |
|---|---|
| No region, no `max_edge` | Exactly today's behaviour: the full image at native size. Existing callers see no change apart from the frame item below. |
| Region given | Crops the region from the full-resolution `variant`, then fits it inside `max_edge`. The default `max_edge` is **1568** (R-1 standard tier). Upscaling is capped at **4×** so a tiny region doesn't turn into a big blur that costs tokens. Resampling is Lanczos. The cap and the filter are tunables to confirm with a reading probe at planning. |
| `max_edge` without a region | Downscales the whole image to fit. This also fixes today's 7.8 MB failure for large shots (L-5). |
| Validation | Same as crop (§6.3): clamp, report the clamp, and reject an empty region or an edge under 8 px. |
| Response | Two content items. First, a short text item: `{"frame":{"source":[W,H],"region":{"x":…,"y":…,"width":…,"height":…},"returned":[w,h],"scale":s,"clamped":false},"map":"source_x = region.x + x / scale"}`. Second, the image. |
| API | The same parameters as GET query keys, added to `GET_QUERY_KEYS`. Frame metadata goes in response headers (`X-Capture-Region`, `X-Capture-Scale`), and MCP builds the text item from them. |

High-resolution models can pass `max_edge: 2576`. The description says so.

### 6.3 S2 — `crop`

```ts
// avkit_capture crop
{ action: "crop", id, x: number, y: number, width: number, height: number,
  unit?: "px" | "fraction", name?: string }
```

```http
POST /captures/{id}/crop
{"x": 0, "y": 100, "width": 960, "height": 940}

201
{
  "item":      { …the new shot, same shape as POST /captures… },
  "source_id": "…",
  "requested": {"x": 0, "y": 100, "width": 960, "height": 940, "unit": "px"},
  "applied":   {"x": 0, "y": 100, "width": 960, "height": 940},
  "clamped":   false,
  "marks":     {"kept": 2, "clipped": 1, "dropped": 0}
}
```

| Rule | Value | Why |
|---|---|---|
| What it writes | A **new shot** (D-1, Human-approved 2026-11-08). The source file, sidecar and bake are untouched. | R-6, R-10 "Save as copy", §4 pattern 3, L-8 |
| Pixels | The original's pixels, exact, with no resampling. The crop's marks are rebuilt on top as its own sidecar and bake (§6.5). | Iteration needs exact pixels. AC-40.26 already sets the "exact crop" bar for the picker. |
| Bounds | `x`, `y` ≥ 0 (schema). A box past the right or bottom edge is **clamped**, with `clamped: true` and `applied` reported. An empty result or an edge under 8 px is **rejected**. | R-6, R-7; L-11; L-17 (never pad with black) |
| Pixel values | Integers when `unit` is `px`. The API rejects fractional px with a message that points to `unit: "fraction"`. | Catches a model that sends 0–1 values without the unit |
| Output file | Always PNG, metadata stripped, in the inbox root. Default name `{stem}-crop.png`, then `_2`… (checked against files and rows like L-9). With `name`, the file is `{name}.png`, sanitized to `[A-Za-z0-9 ._-]`, 1–80 characters, with the same unique suffix. | L-9; §4 pattern 2 names its files; `-strip` habit |
| Source | New `CaptureSource.Crop` (wire `crop`). | L-12; provenance shows in `list` |
| Confirm | None. The action only adds files and never overwrites. | L-8: `confirm` is only for destructive actions |
| Concurrency | Runs under `CAPTURE_FILE_LOCK`, like every capture write. | Existing rule |
| Response | JSON with path pointers, no image bytes. The agent calls `image` on the new id to look. | R-6, R-8; convert's "never media bytes" |

### 6.4 S3 — `import`

```ts
// avkit_capture import
{ action: "import", path: string }      // absolute local path
```

```http
POST /captures
{"mode": "import", "path": "C:/Users/Mat/Desktop/2026-11-07_13-16-09.png"}
201 { "item": { …new shot, source "Import"… } }
```

| Rule | Value | Why |
|---|---|---|
| Copy, never reference | The file is copied into the inbox root. The source file is never moved, changed or watched. | L-2, L-3: av-kit owns the inbox |
| Already in the inbox | Registers in place and returns the row, so the call is idempotent. | L-4 |
| Accepted files | Absolute path; resolves to a regular file; `.png/.jpg/.jpeg/.webp` (the `SCAN_EXTENSIONS`); Pillow `verify()` passes; size ≤ an import cap (a tunable, for example 50 MB); Pillow's decompression-bomb guard stays on. | L-3; L-10 |
| Orientation | EXIF orientation 1 or no tag: a byte copy that keeps the format. Any other orientation: write an **upright PNG** so every pixel frame matches what a viewer shows. | R-7 ("fractions of the upright picture"); Chromium honours EXIF orientation but Pillow's raw frame does not |
| Name | The source stem, sanitized, with the unique suffix. | L-9 |
| Source | New `CaptureSource.Import` (wire `import`). | L-12 |
| Errors | Each names the fix, for example "path must be absolute", "not an image av-kit can open (png, jpg, jpeg, webp)", "file is 212 MB; the import limit is 50 MB". | R-8 |

### 6.5 Marks on a crop

The source's **saved** marks are carried into the new shot, translated by `(-applied.x, -applied.y)`.
They stay editable, and the crop's annotated bake keeps any redaction (pixelate or eraser) that
covered the area. Dropping the marks would leave a crop whose annotated view silently loses its
redaction.

| Mark | Rule |
|---|---|
| rect, highlight, pixelate, eraser | Intersected with the crop. Dropped if the intersection is empty. |
| arrow | Kept if both ends are inside. If not, clipped to the crop with Liang–Barsky, which keeps the direction, unlike L-7's per-point clamp. Dropped if no part is inside. |
| text | Kept if its anchor is inside; the text can run off the edge like any text near an edge. Dropped if the anchor is outside. |

The response counts `kept`, `clipped` and `dropped`. The crop's bake is therefore close to a pixel
crop of the source's bake, but not identical. The differences are known and tested (§11):

- A rect outline cut on its left or top edge gets a stroke along the crop edge, because saving
  clamps origins (L-7).
- A pixelate cut on its left or top edge re-aligns its block grid. It is still pixelated.
- A clipped arrow draws its head at the crop edge.
- A text mark whose anchor is outside but whose glyphs reach inside is dropped.

### 6.6 ImageMagick to av-kit

This table goes into the tool documentation, because agents arrive knowing ImageMagick.

| ImageMagick | av-kit |
|---|---|
| `magick identify -format "%wx%h" in.png` | `get` → `width`, `height` |
| `magick in.png -crop 640x360+100+50 +repage out.png` | `crop {x:100, y:50, width:640, height:360}` |
| `-crop 600x200+550+560 +repage -resize 200%` (to look) | `image {x:550, y:560, width:600, height:200}` (no file; 2× fits inside 1568) |
| `-gravity South -crop 100%x35%+0+0 +repage` | `crop {unit:"fraction", x:0, y:0.65, width:1, height:0.35}` |
| `-gravity center -crop 50%x50%+0+0 +repage` | `crop {unit:"fraction", x:0.25, y:0.25, width:0.5, height:0.5}` |
| `-crop 640x360` (no offset: tiles!) | Not expressible. `x` and `y` are required. |
| `-trim`, `-extent`, `-resize WxH^` (cover) | Deferred (§9) |

There are no geometry strings, no gravity and no virtual canvas: each of those is a footgun (R-9),
and four named numbers can't be misread.

### 6.7 Draft MCP descriptions

These are written in the style of `captureDescriptions` (`capture.ts:33-44`).

- **image.** "…Optional x/y/width/height returns just that region from the full-resolution image,
  scaled to fit `max_edge` (default 1568; pass 2576 for high-resolution vision). Writes no file.
  Coordinates are original pixels, or `unit: "fraction"` (0–1) when you read them off a scaled view.
  The first content item gives the frame: source px = region.x + x / scale."
- **crop.** "…Writes the region as a NEW shot (PNG) and returns its id and paths; the source is
  never changed. Same coordinates as image. A box past the edge is clamped and `applied` reports
  what was cut. Saved marks are carried over and clipped. Like ImageMagick
  `-crop WxH+X+Y +repage`, without the virtual canvas."
- **import.** "…Copies a local image (png, jpg, jpeg, webp; absolute path) into the capture inbox
  as a new shot so image, crop and annotate work on it. The source file is never changed."

## 7. GUI design (second priority)

### 7.1 Crop tool

```
 toolbar  [V][A][R][H][T][X][E]  [C ⧉ Crop]  │ 🔒 │ ↶ ↷ │ Original Annotated │ − + ⤢
 options  Aspect [Free ▾] [⇄]  X [   0] Y [ 100] W [ 960] H [ 940] px  [Reset] [Cancel] [Save as copy ⏎]
 ┌───────────────────────────────────────────────────────────────┐
 │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
 │░░░░░■━━━━━━━━━━━━━━━━━■━━━━━━━━━━━━━━━━━■░░░░░░░░░░░░░░░░░░░░░░│
 │░░░░░┃          ┆           ┆            ┃░░░░░░░░░░░░░░░░░░░░░░│
 │░░░░░■┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄■░░  ░ dimmed outside   │
 │░░░░░┃          ┆           ┆            ┃░░  ┆ thirds grid,     │
 │░░░░░■━━━━━━━━━━━━━━━━━■━━━━━━━━━━━━━━━━━■░░    while dragging   │
 │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
 └───────────────────────────────────────────────────────────────┘
                                           960 × 940 px
```

| Element | Behaviour | Precedent |
|---|---|---|
| Entry | Toolbar button with the lucide `Crop` icon and the tooltip "Crop (C)". **C** goes through the shortcut registry once the letter map is built (L-14). | Photoshop C (R-11); C is free in C-12 |
| Start | The box covers the whole image, with 8 handles (corners and sides) reusing `capture-transform.ts` (L-13). | Windows Photos (R-10) |
| Pointer | Drag a handle to resize, drag inside to move, drag outside to draw a new box. Shift keeps the aspect ratio while dragging. | Photoshop, Windows Photos |
| Look | The outside is dimmed. A rule-of-thirds grid appears only while dragging. The size reads out in original px. | Photoshop overlay (R-11) |
| Aspect | Dropdown: Free, Original, Square, 16:9, 4:3, 3:2. ⇄ or **X** swaps portrait and landscape. | Windows Photos list (R-10); Photoshop X (R-11) |
| Numbers | X / Y / W / H fields in original px, the same numbers an agent would send. Arrow keys nudge 1 px, Shift+arrow 10 px. | Matches the agent contract (§6.1) |
| Commit | **Enter**, a double-click inside the box, or **Save as copy**. A toast names the new shot, which becomes selected; the source stays in the filmstrip. | Windows Photos "Save as copy" (R-10) |
| Cancel | **Esc** or Cancel. Reset returns the box to the full image. | Photoshop, Windows Photos |
| Modal | While the crop is open, the other tool letters are ignored until Enter or Esc, so X can swap the aspect as in Photoshop instead of switching to Redact. | Photoshop overloads X inside crop |
| Unsaved marks | Crop is disabled while marks are unsaved, with the tooltip "Save or discard your marks first". The crop uses saved marks, exactly as the API does. | Keeps one code path for GUI and agents |

`CaptureTool` gains `'crop'`. The type check on `TOOL_BUTTON_IDS` then forces the new button
(`capture-toolbar.ts:78`).

### 7.2 Import

| Entry | Behaviour |
|---|---|
| Drag and drop | Drop image files on the capture page. Each one calls `import` with its path. Non-images show an error toast. |
| **Import image…** | Button with the lucide `ImagePlus` icon. Opens a file dialog filtered to png/jpg/jpeg/webp, multi-select. |
| Ctrl+V | Pastes a clipboard image, for example from Win+Shift+S. Electron main writes it to the inbox as `{yyyy-MM-dd_HH-mm-ss}.png` and registers it as `gui`, the same publication path as the hotkey. |

## 8. Data and file contract

| Item | Change |
|---|---|
| `CaptureSource` | Add `Crop` and `Import`. Add wire values `crop` and `import`. |
| Catalog row | No schema change. Provenance (which source a crop came from, and where) is returned by `crop` but **not persisted** in v1 (§9). |
| Inbox files | `{stem}-crop.png` or `{name}.png`, plus its sidecar and bake when marks were carried. Import writes `{stem}.{ext}` (or `.png` when rotated). |
| Existing shots | Never modified by S1, S2 or S3. |
| API models | `CaptureCropIn` (x, y, width, height, unit, name; `extra="forbid"`), `CaptureImportIn` (mode, path), `CaptureCropOut`. |
| MCP | `crop` and `import` union members (`.strict()`); region fields on `image`; registry rows for `POST /captures/{id}/crop` and import. |

## 9. Deferred and rejected

| Item | Status | Why |
|---|---|---|
| `-trim` (auto-crop uniform borders) | Deferred | 0 uses locally (§4) |
| Resize, cover-crop thumbnails, `-extent` | Deferred | That is image conversion, not crop. 6 uses. A later `resize` belongs with format output. |
| Output format option (JPEG/WebP crops) | Deferred | PNG is lossless and matches the `-converted.png` precedent (L-9). The size risk is in §11. |
| Persisted provenance (`derived_from`, offset) | Deferred | Needs a schema migration. The response already carries it. |
| `unit: "fraction"` on `annotate` | Follow-up | It would help in the same way, but it is separate from crop. |
| Rotate, flip, straighten | Deferred | Outside the ask. Windows Photos groups them with crop, so it is a natural next step. |
| Geometry strings (`WxH+X+Y`) | **Rejected** | R-9 footguns. Named numbers can't be misread. |
| An ImageMagick dependency | **Rejected** | Pillow already does every step (L-18). |
| Inline image bytes as crop input | **Rejected** | R-6 converges on paths. Import covers outside files. |
| Returning image bytes from `crop` | **Rejected** | One extra `image` call when needed. Keeps the response small (R-8). |

## 10. Slices

| Slice | Scope | Depends on |
|---|---|---|
| **S1** Region view | API query parameters and headers, MCP `image` fields and frame item, `max_edge`, tests | — |
| **S3** Import | API `mode: import`, MCP `import`, `CaptureSource.Import`, EXIF handling, tests | — |
| **S2** Crop | Core crop and mark clipping, naming, `CaptureSource.Crop`, API, MCP, tests | — (D-1 ruled: new shot) |
| **S4** GUI crop tool | §7.1 | S2 |
| **S5** GUI import | §7.2 | S3 |

The suggested order is S1, S3, S2, S4, S5. S1 serves the most common use (§4). With D-1 ruled,
no slice waits on a human decision. Next free MEU id on `main` today is MEU-128. Check open worktrees before
claiming ids.

## 11. Risks and tests

| Risk | Test or guard |
|---|---|
| Crop not pixel-exact | Assert output pixels equal `source.crop(box)` at the four corners and the centre on a synthetic pattern (the AC-40.26 style). |
| Black padding past the edge (L-17) | A box past each edge is clamped. Assert no black pixel appears in a crop of an all-white image. |
| Fraction rounding off by one | Thirds on odd sizes (for example 1001×667). Assert outward rounding and that applied px covers the requested area. |
| Clipped marks drift from the preview | Run the existing Pillow-versus-SVG parity suites on clipped rect, highlight, pixelate, eraser, arrow and text. |
| Redaction weakened at an edge | A pixelate cut down to a sliver narrower than its block still averages the sliver. Assert no source pixel survives unchanged inside an intersected pixelate. |
| Known bake differences surprise someone | Assert each §6.5 difference explicitly, so it is documented behaviour, not an accident. |
| Large PNG from a JPEG photo | A 6000×4000 JPEG crop can exceed the MCP image limit. S1's `max_edge` is the answer; the description says so. |
| EXIF orientation | Fixtures for all 8 orientations. The upright PNG matches what Chromium displays. **Open check:** do JPEGs scanned today with orientation ≠ 1 already show marks in the wrong place? Probe it at planning. |
| Name race | Two crops at once produce `-crop` and `-crop_2`, not one overwrite (file and row check under the lock). |
| Scan registers the file first | L-4 makes the crop's source win. Test it. |
| MCP content shape change | `image` now returns a text item before the image. Update tests that read `content[0]`. |
| Tool descriptions mislead agents | A small eval (R-8): read small text in a 4K screenshot; crop a described area into a deliverable; import a Desktop file and crop it. |

## 12. Decision log

```yaml
decision_log:
  - id: D-1
    stage: planning
    question: "What does a crop write?"
    resolution: human
    class: product-preference
    chosen: "New shot (copy); source untouched"
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:66 — Original PNG immutable after save"
      - "packages/core/src/avkit_core/services/capture.py:747-756 — flatten of a JPEG/WebP writes a new PNG copy"
      - "_inspiration/capture-annotation-tools/report_claude.md:234 — crop was out of scope for fear of breaking the agent coordinate contract"
    research:
      engine: exa
      sources:
        - "https://glama.ai/mcp/servers/TOBYCAI/image-mcp/tools/crop — new file, source unchanged, clamped"
        - "https://github.com/greatSumini/sharp-mcp — x/y/width/height, output_path"
        - "https://www.screensnap.pro/blog/crop-screenshot-windows — Windows Photos Save as copy vs Save (tavily)"
        - "https://jkost.com/blog/2017/05/essential-tips-for-cropping-in-photoshop-cc.html — non-destructive crop option (tavily)"
    reasoning: "Mat chose the recommended option from the Decision Brief in section 13. Copy-only matches every MCP crop precedent and Windows Photos Save as copy, needs no exception to the immutable-original lock and no IDE confirmation. The in-place, non-destructive and write-nothing options lost on the grounds in the brief."
    human_message_reference: "USER_EXPLICIT 2026-11-08 'D-1:  New shot (copy); source untouched'"

  - id: D-2
    stage: planning
    question: "Is crop in scope for capture?"
    resolution: human
    class: product-preference
    chosen: "In scope across API, MCP and GUI; agent first"
    source_tag: Human-approved
    precedents:
      - "_inspiration/capture-annotation-tools/report_claude.md:234 — agent opinion that crop was out of scope (superseded)"
    research:
      engine: none
      sources: []
    reasoning: "Mat's explicit request."
    human_message_reference: "USER_EXPLICIT 2026-11-08 'I want the agent to be able to use it in av-kit in the GUI, MCP and API so it works on screenshots or any ohter images provided'"

  - id: D-3
    stage: planning
    question: "Which coordinate frame do crop and region view use?"
    resolution: autonomous
    class: two-way
    chosen: "Original-image pixels only; a view image is never a frame"
    source_tag: Research-backed
    precedents:
      - "packages/core/src/avkit_core/domain/capture.py:134-259 — marks stored in original px"
      - "docs/proposals/2026-09-19-p9-annotation-adaptation-proposal.md:233 — translate downscaling explicitly, preserve crop origin"
    research:
      engine: tavily
      sources:
        - "https://platform.claude.com/docs/en/build-with-claude/vision-coordinates — Claude answers in the resized frame"
        - "https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — zoom crops from full resolution; zoom image is not a frame"
    reasoning: "One frame shared with get, marks and capture region. A per-view frame would multiply the downscale mistakes L-16 warned about."

  - id: D-4
    stage: planning
    question: "Pixels only, or also fractions?"
    resolution: autonomous
    class: two-way
    chosen: "Pixels canonical; optional unit fraction (0-1), echoed back as applied pixels"
    source_tag: Research-backed
    precedents:
      - "mcp-server/src/toolsets/capture.ts:136-148 — capture region is integer x/y/width/height"
    research:
      engine: tavily
      sources:
        - "https://platform.claude.com/docs/en/build-with-claude/vision-coordinates — map back via x / resized_w"
        - "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/bounding-box-detection — 0-1000 yxyx"
        - "https://github.com/QwenLM/Qwen3-VL/issues/866 — Qwen2.5-VL absolute px vs 0-1000"
        - "https://mochify.app/mcp — fractions of the upright picture (exa)"
    reasoning: "Pixels match every precedent and the GUI fields. Fractions are the only unit that does not depend on how a model scaled the image. Normalized 0-1000 was rejected because it is one vendor's convention, not a shared one."

  - id: D-5
    stage: planning
    question: "Separate zoom action, or region fields on image?"
    resolution: autonomous
    class: two-way
    chosen: "Region and max_edge on image; no file; default max_edge 1568, upscale cap 4x"
    source_tag: Research-backed
    precedents:
      - "mcp-server/src/toolsets/capture.ts:19 — GET_QUERY_KEYS is the place to extend"
      - "docs/build-plan/09-screenshot-capture.md:939 — render without writing a file"
    research:
      engine: tavily
      sources:
        - "https://www.anthropic.com/research/writing-tools-for-agents — consolidate; token-efficient responses"
        - "https://doi.org/10.48550/arxiv.2502.17422 — crop and zoom improves small-detail perception (exa)"
    reasoning: "Looking closer is the most common local use and needs no file. One action keeps the tool surface small. 1568 is the standard-tier cap; the 4x cap stops tiny regions from becoming large blurred images that cost tokens."

  - id: D-6
    stage: planning
    question: "Out-of-bounds boxes: clamp or reject?"
    resolution: autonomous
    class: two-way
    chosen: "Clamp and report applied plus clamped; reject empty results or edges under 8 px"
    source_tag: Research-backed
    precedents:
      - "packages/core/src/avkit_core/domain/capture.py:25 — CAPTURE_MIN_EDGE_PX = 8"
      - "C:/Temp/av-kit/crop-pillow-probe.txt — Pillow pads black instead of failing"
    research:
      engine: exa
      sources:
        - "https://glama.ai/mcp/servers/TOBYCAI/image-mcp/tools/crop — automatically clamped"
        - "https://mochify.app/mcp — trimmed to the picture"
    reasoning: "A model a few pixels off still gets a useful crop, and the echoed box shows it what happened. A crop that would come out empty or tiny is a coordinate mistake, so it is rejected with a message."

  - id: D-7
    stage: planning
    question: "What happens to the source's marks on a crop?"
    resolution: autonomous
    class: two-way
    chosen: "Carry saved marks, translated and geometrically clipped; report kept, clipped, dropped"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:917-952 — save clamps only origins, so crop needs its own clipping"
    research:
      engine: none
      sources: []
    reasoning: "Dropping marks loses redaction in the crop's annotated view. Burning them in would put marks into the new original. Carrying them keeps both views and keeps them editable."

  - id: D-8
    stage: planning
    question: "Crop output format and name?"
    resolution: autonomous
    class: two-way
    chosen: "PNG, metadata stripped; {stem}-crop.png then _2; optional sanitized name"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:65-66, 747-756 — {stem}-converted.png naming"
    research:
      engine: none
      sources: []
    reasoning: "Lossless and consistent with the flatten copy. Agents name deliverables (section 4), so name is optional."

  - id: D-9
    stage: planning
    question: "How does an outside image get in?"
    resolution: autonomous
    class: two-way
    chosen: "Import copies into the inbox; byte copy, or an upright PNG when EXIF rotates; idempotent for inbox paths"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:827-839 — register accepts inbox paths only"
      - "mcp-server/src/toolsets/convert.ts:12 — agents already pass local absolute paths"
    research:
      engine: exa
      sources:
        - "https://mochify.app/mcp — boxes are fractions of the upright picture"
    reasoning: "Referencing files in place would break the inbox ownership the catalog relies on. Writing an upright file removes a frame mismatch between Chromium and Pillow."

  - id: D-10
    stage: planning
    question: "ImageMagick or Pillow; geometry strings or fields?"
    resolution: autonomous
    class: two-way
    chosen: "Pillow; named fields only; document the ImageMagick mapping"
    source_tag: Research-backed
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:152-160 — Pillow crop and paste already in use"
    research:
      engine: tavily
      sources:
        - "https://imagemagick.org/Usage/crop — +repage, tiling without offset, persistent gravity"
    reasoning: "No new dependency. The ImageMagick footguns stay out, and the mapping table lets agents translate what they know."

  - id: D-11
    stage: planning
    question: "Which GUI crop pattern?"
    resolution: autonomous
    class: two-way
    chosen: "Windows Photos and Photoshop pattern: full-image box, 8 handles, dimmed outside, thirds while dragging, aspect dropdown, X swap, Enter commits as Save as copy, Esc cancels, key C"
    source_tag: Research-backed
    precedents:
      - "_inspiration/capture-annotation-tools/synthesis.md:218 — C-12 letter map leaves C free"
      - "ui/src/renderer/src/features/capture/capture-transform.ts:28-105 — box handles to reuse"
    research:
      engine: tavily
      sources:
        - "https://www.screensnap.pro/blog/crop-screenshot-windows — Windows Photos crop flow"
        - "https://jkost.com/blog/2017/05/essential-tips-for-cropping-in-photoshop-cc.html — C, X, O, Enter"
    reasoning: "Windows Photos is the crop most Windows users have seen. Photoshop supplies the keys power users expect. Both agree on handles, aspect presets and Enter/Esc."

  - id: D-12
    stage: planning
    question: "GUI import entry points?"
    resolution: autonomous
    class: two-way
    chosen: "Drag and drop, an Import image... button, and Ctrl+V paste"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:172 — main publishes {yyyy-MM-dd_HH-mm-ss}.png into the inbox and registers it"
    research:
      engine: tavily
      sources:
        - "https://support.microsoft.com/en-us/windows/apps/use-snipping-tool-to-capture-screenshots — Snipping Tool copies to the clipboard"
    reasoning: "These are the three ways a desktop user brings an image to an app. Paste reuses the hotkey's publication path."

  - id: D-13
    stage: planning
    question: "What is deferred?"
    resolution: autonomous
    class: two-way
    chosen: "trim, resize/cover, format option, persisted provenance, annotate unit fraction, rotate/flip"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/crop-magick-usage.txt — trim 0, extent 6, crop 12, identify 30"
    research:
      engine: none
      sources: []
    reasoning: "Keep the first slices to what agents here actually do. Each deferral can be added later without breaking the contract."
```

## 13. Decision Brief

### D-1: What does a crop write?   [product-preference] [planning]

**Ruling (Mat, 2026-11-08):** "D-1:  New shot (copy); source untouched". The recommended option.
The brief below is kept as the record.

**Recommendation:** Write a **new shot** and leave the source untouched. Every MCP crop tool found
does this, and so does Windows Photos' "Save as copy". The agents on this machine already work
this way, re-cropping from the untouched raw. It needs no exception to the "Original PNG immutable"
lock and no IDE confirmation, so an agent can crop as freely as it can view.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ New shot (copy); source untouched | — | — | `09-screenshot-capture.md:66`; `services/capture.py:747-756`; [image-mcp crop](https://glama.ai/mcp/servers/TOBYCAI/image-mcp/tools/crop); [Windows Photos](https://www.screensnap.pro/blog/crop-screenshot-windows) |
| ⚠️ Copy by default, plus an in-place "Crop image…" (backup first, IDE confirm, like flatten) | Matches Windows Photos' second button ("Save" overwrites). No extra file when someone only wants to trim one screenshot. | A second exception to the immutable-original lock. Revert must also restore the sidecar, or the translated marks land on the uncropped image. Agents get an IDE confirmation on every in-place crop. Roughly one more slice of work (backup, revert, confirm). | [Windows Photos](https://www.screensnap.pro/blog/crop-screenshot-windows); `services/capture.py:586-635` |
| ⚠️ Non-destructive crop: store a crop box on the shot and apply it when baking | No new files. The crop stays adjustable. Marks never need translating or clipping, so the §6.5 bake differences disappear. Matches Photoshop with Delete Cropped Pixels off. | One crop per shot: two deliverables from one screenshot still need copies. The annotated image would be cropped while `original_path` and the marks stay uncropped, which is exactly the frame split that `report_claude.md:234` warned about. Preview, bake and flatten all need crop-aware parity work. An agent that opens `original_path` gets the uncropped file. | [Photoshop Essentials](https://www.photoshopessentials.com/basics/how-to-crop-images-photoshop-cc); `report_claude.md:234` |
| ❌ Write nothing: ship region view and import, no file-writing crop | Smallest. No new files and no lock question. The region view covers the most common agent use (§4). | Deliverable crops (§4 pattern 2) still need ImageMagick, and agents without a shell can't produce one. No GUI crop, so it falls short of the request for crop "in the GUI, MCP and API". | `C:/Temp/av-kit/crop-magick-usage.txt` |

The full status quo (no crop at all) is not listed: Mat asked for crop in the GUI, MCP and API.

**Precedent:** The flatten copy for JPEG/WebP (`services/capture.py:747-756`) already chose
"write a sibling, don't overwrite" when an in-place write was awkward. The immutable-original lock
(`09-screenshot-capture.md:66`) has one governed exception, flatten. The recommendation adds none.
**Research:** tavily and exa via `pomera_web_search`. MCP crop tools (image-mcp, sharp-mcp,
imagician) write new files. Windows Photos offers both "Save as copy" and "Save". Photoshop offers
a non-destructive crop. Receipts `C:/Temp/av-kit/crop-research-5-mcp-crop.md`, `-7-`, `-9-`.
**Reversibility / risk:** two-way. Copy-only can gain an in-place option later without changing
the agent contract. Going the other way, removing an in-place crop agents rely on, is harder. If
copy-only turns out wrong, the cost is extra files in the inbox, which the user can delete.
**If you do not answer:** The design keeps copy-only as the working assumption. S1 (region view)
and S3 (import) can be planned and built now; S2 and S4 are planned on copy-only and held at the
plan gate until you confirm. (Superseded by the ruling above.)

## 14. Sources

**Official documentation**
- Claude vision: https://platform.claude.com/docs/en/build-with-claude/vision
- Claude coordinates and bounding boxes: https://platform.claude.com/docs/en/build-with-claude/vision-coordinates
- Claude computer use tool: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
- Computer-use reference code: https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/computer_use_demo/tools/computer.py
- Gemini bounding boxes: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/bounding-box-detection
- ImageMagick crop usage: https://imagemagick.org/Usage/crop
- Snipping Tool: https://support.microsoft.com/en-us/windows/apps/use-snipping-tool-to-capture-screenshots

**Papers and vendor research**
- MLLMs Know Where to Look (ViCrop): https://doi.org/10.48550/arxiv.2502.17422
- Small visual details in zero-shot VQA: https://doi.org/10.48550/arxiv.2310.16033
- OpenAI, Thinking with images: https://openai.com/index/thinking-with-images
- Anthropic, Writing effective tools for agents: https://www.anthropic.com/research/writing-tools-for-agents

**Practice**
- image-mcp `crop`: https://glama.ai/mcp/servers/TOBYCAI/image-mcp/tools/crop
- sharp-mcp: https://github.com/greatSumini/sharp-mcp
- imagician: https://github.com/flowy11/imagician
- mcp-image-tools: https://pypi.org/project/mcp-image-tools/
- Mochify MCP: https://mochify.app/mcp
- Qwen coordinate conventions: https://github.com/QwenLM/Qwen3-VL/issues/866, https://swift.readthedocs.io/en/v4.0/BestPractices/Qwen3-VL-Best-Practice.html
- Windows Photos crop: https://www.screensnap.pro/blog/crop-screenshot-windows, https://www.batchphoto.com/blog/top-10-tools-to-crop-photos-on-windows
- Photoshop crop: https://jkost.com/blog/2017/05/essential-tips-for-cropping-in-photoshop-cc.html, https://www.photoshopessentials.com/basics/how-to-crop-images-photoshop-cc
