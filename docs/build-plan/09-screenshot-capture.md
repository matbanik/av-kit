# Phase 9 — Screenshot Capture

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: Phase 1–6 (ports, settings, Electron chrome) | Outputs: Capture page, REST `/captures`, MCP `avkit_capture`, tray + global hotkey + native region picker
> **Spec date:** 2026-08-26. **Does not reopen** MEU-1–33 as incomplete. Phase 1–8 remain the shipped YouTube toolkit + Convert; this phase **adds** a fifth module.

> **Capture layout supersession:** [Phase 11 page layout canon](11-page-layout.md) governs Capture presentation in MEU-57; this spec continues to govern picker, annotation, IPC, and persistence behavior.

---

## Goal

Give av-kit a **local screenshot inbox**: capture a region with a global hotkey, land a PNG in a folder, review it in a filmstrip, and annotate with arrow / box / highlight / text — from the GUI **and** from MCP. The page sits on the left rail **directly under Convert**.

This file is the **SSOT** for capture domain, adapter, service, REST, MCP, Electron OS surface, and GUI. Pointers in `00`–`08` defer to this document.

| Source | Decision |
|--------|----------|
| Spec | This file; [BUILD_PLAN.md](../BUILD_PLAN.md) Phase 9 row |
| Local Canon | Job records + file pointers ([01-domain-layer.md](01-domain-layer.md)); `{ items }` catalogs vs `{ items, processor }` queues ([04-rest-api.md](04-rest-api.md)); compound MCP + `action` ([05-mcp-server.md](05-mcp-server.md)); HelpCard + command registry + `gui-actions-index.md`; Electron spawn / single-instance / IPC allowlist ([06-gui.md](06-gui.md)); Windows-first installer ([07-distribution.md](07-distribution.md)); Convert as the prior “new module” pattern ([08-video-conversion.md](08-video-conversion.md)) |
| Research-backed | Steve Krug, *Don't Make Me Think, Revisited* (3rd ed., 2014). ShareX host (tray + hotkey + region overlay + save-to-folder) as **intent**, not C# ([ShareX/ShareX](https://github.com/ShareX/ShareX); file map below). Agent annotate schema from [vapvarun/image-annotator-mcp](https://github.com/vapvarun/image-annotator-mcp) + [aamar-shahzad/mcp-screenshot-server](https://github.com/aamar-shahzad/mcp-screenshot-server). Windows grab from [sethbang/mcp-screenshot-server](https://github.com/sethbang/mcp-screenshot-server). Overlay UX from Shotik/Flameshot-style freeze + drag-rect. Viewport from nomacs **Paint on Image** (canvas tools on the current image — not the Plugins menu). Native region picker rationale from [electron/electron#40515](https://github.com/electron/electron/issues/40515) — transparent, always-on-top `BrowserWindow` overlays on Windows render black or click-through, which is why the region picker is a native helper rather than a Chromium window |
| Human-approved | 2026-08-26 USER_EXPLICIT: write this Phase 9 spec in the Convert pattern. MVP = F2 region → inbox folder → filmstrip + arrow/box/highlight/text; GUI + MCP; tray so the hotkey stays registered. Same day: pin the ShareX source map in this file. Defaults below are the planning locks unless a later USER_EXPLICIT changes them. **2026-08-27 USER_EXPLICIT:** the Chromium region overlay is replaced by a native C# WinForms (.NET 8) sidecar, `avkit-region-picker.exe` — see [§Native region picker (helper process)](#native-region-picker-helper-process). The Chromium overlay path is **deleted with no fallback** |

**Inspiration is intent, not code** ([BUILD_PLAN.md](../BUILD_PLAN.md) Golden Rule 5). Do not paste ShareX, Shotik, nomacs, or MCP-server source. Rewrite against this FIC. ShareX files to **read for flow** (not copy) are pinned in [ShareX source map](#sharex-source-map-read-rewrite).

---

## Design thesis (Krug → av-kit)

Krug’s first law: **don’t make me think** — pages must be self-evident. Applied here:

| Krug rule | Capture-page consequence |
|-----------|--------------------------|
| Conventions are your friend | Same shell tokens, HelpCard, Browse, Open file / Open folder, destructive red, Settings card. **Not** a Downloader queue: capture is an inbox, not Start/Pause/Resume work |
| Visual hierarchy | One cyan primary (**Capture region**). Filmstrip + viewport fill the page. Hotkey/inbox are a one-line header, not a form |
| Limit choices | **One rail item.** Six tools only on the canvas toolbar |
| Progressive disclosure (G26) | Color / stroke live on the tool when it is selected. No plugin manager, no nested menus |
| Omit needless words | No “After capture tasks”, no ShareX filename tokens, no FFmpeg/GPU chrome |
| Obvious beats fewer-but-puzzling clicks | F2 (or the page button) → drag → file appears in the filmstrip. Click thumb → annotate → Save |
| You-are-here navigation | Rail item `Capture`, shortcut `Ctrl+5`, route `/capture`, active cyan bar |

**Rejected layouts**

| Layout | Why it fails Krug / Local Canon |
|--------|----------------------------------|
| Downloader-shaped queue (Add → Start → Pause) | There is no sequential worker. Fake Start is a second language |
| nomacs **Plugins ▸ Page Extraction ▸ Draw to Page** | Nested menus hide the six tools. Paint belongs **on** the image |
| ShareX after-capture task graph | Uploaders, OCR, “run action” are out of MVP |
| Annotate during the snip overlay | Two canvases. Overlay selects a rectangle; annotation is the Capture page / MCP |
| Inner routes for Inbox / Editor | [06-gui.md](06-gui.md) §Module Internal Navigation: no internal tab routing |

**Current GUI to match** (shipped shell): dark `#282a36`, cyan `#8be9fd` active/primary, red destructive, Help accordion. Capture must use the same tokens (G31/G32) — no per-page accent fork.

---

## MVP lock (defaults)

| Topic | Lock | Source |
|-------|------|--------|
| Product | Fifth in-repo module (not a separate app) | Human-approved 2026-08-26 |
| OS | Windows 10/11 only in this phase | Local Canon Phase 7 Windows-first |
| Default hotkey | `F2` (Electron accelerator). Configurable. Register failure is visible (ShareX often owns F2) | Human-approved (user’s ShareX habit) |
| Inbox default | `~/Pictures/av-kit` | Spec. User may point `inbox_dir` at an existing ShareX folder |
| After capture | Always save PNG to inbox. Clipboard copy **off** by default | Spec |
| Annotated naming | Sibling `{stem}.annotated.png` next to the original | Spec |
| Sidecar | `{stem}.ann.json` next to the original (annotation list) | Spec |
| Original PNG | Immutable after save. Annotate never overwrites it | Spec |
| Close main window | Minimize to tray (process stays — hotkey requires it) | Spec |
| Tools | Arrow, box (rect), highlight, text overlay | Human-approved |
| Auto-triggers in MVP | Hotkey, GUI button, MCP `capture` / `capture_interactive`, inbox watcher → filmstrip refresh | Spec |

---

## Module Internal Navigation (Phase 6 amendment)

| Position | Icon | Label | Route | Shortcut | Notes |
|----------|------|-------|-------|----------|-------|
| Top (5th) | 📷 (Lucide `Camera`) | Capture | `/capture` | `Ctrl+5` | Below Convert, above the Settings pin |

`Ctrl+1`–`Ctrl+4` and `Ctrl+,` / `Ctrl+B` unchanged. Command palette category adds `capture`. Console module tag: `[Capture]`.

---

## Capture Page (`/capture`)

> **Layout**: Research-backed Krug + nomacs viewport intent. **Not** Downloader queue.

### Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  Capture                                                              Capture  Ctrl+5│
├──────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─ Help (collapsed) ──────────────────────────────────────────────────────────────┐ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  Inbox: [ ~/Pictures/av-kit          ] [Browse…]   Hotkey: F2  [Change…]             │
│  Status: Hotkey registered · 12 images                                               │
│                                                                                      │
│  [  Capture region  ]                                                                │
│                                                                                      │
│  ┌─ FILMSTRIP ──┐  ┌─ VIEWPORT ────────────────────────────────────────────────────┐ │
│  │ newest ↑     │  │  [Arrow] [Box] [Highlight] [Text]   color · stroke            │ │
│  │ [thumb]      │  │  [Undo] [Redo] [Save annotated]                               │ │
│  │ [thumb] ★    │  │                                                               │ │
│  │ [thumb]      │  │           (selected image + vector overlay)                   │ │
│  │ …            │  │                                                               │ │
│  └──────────────┘  └───────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  [Open file] [Open folder] [Delete…]                                                 │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

**Scan path:** Help → where files go / which key captures → **Capture region** → pick a thumb → mark the image → Save.

Empty inbox: viewport shows a short empty state (“Press F2 or Capture region”). Do not show a drop-zone as the primary path (hotkey is the path). Import of files already in `inbox_dir` happens via scan, not a second Add flow.

### Inbox + hotkey header

| Control | Behavior | Source |
|---------|----------|--------|
| Inbox path | Bound to `capture.inbox_dir`. Browse = IPC `showDirectoryDialog` then Settings PUT | Local Canon Settings Browse |
| Hotkey | Shows the current accelerator. Change opens a recorder (press a key). PUT `capture.hotkey`. If Electron `globalShortcut.register` fails, the message shows inline in the Capture header row (MEU-81, Human-approved triage D-64): “F2 is in use — quit ShareX or pick another key” | Spec |
| Capture region | Same as F2: ask Electron main to spawn the native region picker | Spec |

Reject relative inbox paths (API 422). Path must be absolute.

### Filmstrip

- Newest first (`created_at` desc, then filename).
- Selected thumb has the cyan bar.
- Click selects; does not open an OS viewer.
- Poll `GET /captures` at 1 s while the page is visible if a pending interactive request exists, else 5 s — **or** refresh immediately on IPC `captures:inbox-changed` (watcher). No SSE.
- Envelope is `{ items }` (catalog), **not** `{ items, processor }`.

### Viewport tools

| Tool | Pointer gesture | Baked result |
|------|-----------------|--------------|
| Select | Click a mark or the mark list; drag body or arrow handles | No bake until Save — edits the draft list |
| Arrow | Drag from tail to head (creates even over existing marks) | Line + arrowhead |
| Box | Drag rectangle | Stroke rect, no fill (fill_opacity 0) |
| Highlight | Drag rectangle | Semi-transparent fill, no stroke required |
| Text | Click to place, type, Enter commit, Esc cancel | Label with optional opaque background |

Overlay is **vector on the canvas** until Save. After a mark is in the draft, Select (or auto-Select after create) can move it — including independently adjusting an arrow’s `from`/`to` — without Undo. Save POSTs the full annotation list; the service writes sidecar + bakes `{stem}.annotated.png`. See [§Annotation edit until Save](#annotation-edit-until-save).

Undo/Redo is session-local to the open image (stack in the renderer). Switching thumbs discards unsaved overlay after a confirm if dirty.

Zoom: fit-to-viewport default; scroll zoom optional in MVP if it ships with the canvas; **not** a named deferral blocker — fit-to-viewport is enough. Fit-to-viewport **must** map pointer events into original-image pixels — see [§Annotation geometry (arrow + text)](#annotation-geometry-arrow-text). Since MEU-66 the viewport also zooms and pans: see [§Viewport zoom](#viewport-zoom) (MEU-66).

### Destructive Delete

Unlike Convert **Clear** (rows only, files stay), Capture **Delete** removes the row **and** the original + sidecar + annotated files. The inbox **is** the product. Confirm dialog. MCP `remove` requires `confirm: true` (M3).

### HelpCard topics (minimum)

What Capture does; F2 vs ShareX conflict; inbox folder; original vs `.annotated.png`; six tools; MCP can see the PNG; close-to-tray keeps the hotkey; never uploads.

---

## Electron OS surface (main process)

This surface **cannot** live in FastAPI. FastAPI cannot hold a global hotkey while another app is focused, and it cannot put a fullscreen region picker on screen.

| Concern | Owner | Rule |
|---------|-------|------|
| Tray icon | Electron main | Always created while the app runs. Menu: Show window, Capture region, Open inbox folder, Quit |
| Close-to-tray | Electron main | Window `close` hides; does not quit. Quit only from tray or app menu |
| Single instance | Existing | Second launch focuses the running app (already locked) |
| `globalShortcut` | Electron main | Register `capture.hotkey` after settings load. Unregister on change/quit |
| Region select + freeze + grab | **Native region-picker helper** (`avkit-region-picker.exe`, C# WinForms .NET 8, spawned by Electron main) | Opaque frozen-bitmap fullscreen topmost window on the **display under the cursor**; drag rect; Enter or mouse-release confirms; Esc cancels; a region below `PICKER_MIN_EDGE_PX` on either edge cancels. PerMonitorV2 DPI, physical pixels. No annotation tools. See [§Native region picker (helper process)](#native-region-picker-helper-process) |
| Write PNG | Helper writes, Electron main publishes | The helper writes the cropped PNG to the **staging path Electron gives it** (`--out`, inside `inbox_dir`, see [§Result publication](#result-publication)). Electron main runs the black/empty pixel guard on that file, then publishes it as `{inbox_dir}/{yyyy-MM-dd_HH-mm-ss}.png` (**local** clock, ShareX-like) by claiming the name rather than overwriting, and `POST /captures` with the absolute path |
| Inbox watcher | Electron main | `fs.watch` (or equivalent) on `inbox_dir` → IPC to renderer `captures:inbox-changed` |
| Interactive MCP | Electron main | Poll `GET /captures/requests?status=pending` at 500 ms while any Pending exists (or on an interval always ≤ 1 s). Spawn the region-picker helper; on complete `POST /captures/requests/{id}/complete` with path; on Esc `…/cancel` |

Preload allowlist **adds** (do not expose Node to the renderer):

| Channel | Direction | Purpose |
|---------|-----------|---------|
| `capture-region` | invoke | Spawn the native region picker (GUI button) |
| `get-hotkey-status` | invoke | `{ registered: bool, accelerator: str, error?: str }` |
| `captures:inbox-changed` | on | Invalidate filmstrip query |

`nodeIntegration: false`, `contextIsolation: true`, `sandbox: true` unchanged.

There is **no overlay window and no overlay preload**. The region rectangle is never marshalled across an IPC boundary: the helper selects, crops and writes the PNG itself, and Electron main learns the outcome from the helper’s exit code plus the staged file. The full contract is [§Native region picker (helper process)](#native-region-picker-helper-process); what Electron does with the result is [§Result publication](#result-publication).

**DPI / multi-monitor:** capture the display under the cursor (ShareX “restrict to active monitor” intent). Do not stitch the virtual desktop in MVP.

**Permission:** if the capture bitmap is empty/black, log `[Capture]` and surface “Screen capture blocked” — do not silently save a black PNG as success.

---

### Native region picker (helper process)

The picker is a separate Windows process, not a Chromium window. A transparent, always-on-top
`BrowserWindow` is not a reliable region selector on Windows
([electron/electron#40515](https://github.com/electron/electron/issues/40515)), and a Chromium-side
screen grab races the very window that is already on screen. The helper freezes first and shows
second, which is the ordering that makes a freeze-frame correct.

**Constants.** `PICKER_MIN_EDGE_PX`, `PICKER_EXIT_CONFIRM`, `PICKER_EXIT_ERROR`,
`PICKER_EXIT_CANCEL`, `PICKER_READY_MARKER`, `PICKER_STAGING_PREFIX`. Their values are declared
once, in the MEU-40 plan folder’s `named-sets.json`, and are referred to here by name only.

| Item | Rule |
|------|------|
| Binary | `avkit-region-picker.exe` — .NET 8 **self-contained** `win-x64` WinForms publish from `native/region-picker/` |
| Build | `dotnet publish native/region-picker -c Release -r win-x64 --self-contained true -o native/region-picker/publish`, run before `electron-builder` |
| Invocation | `avkit-region-picker.exe --out <staging-path>`. Electron chooses the path; the helper never names or timestamps the final file |
| Outcome | `PICKER_EXIT_CONFIRM` — a region meeting `PICKER_MIN_EDGE_PX` was confirmed and the cropped PNG is at `--out`. `PICKER_EXIT_CANCEL` — the user cancelled (Esc, or released below `PICKER_MIN_EDGE_PX`); no file. `PICKER_EXIT_ERROR` — bad argv, unwritable `--out` parent, or GDI failure; reason on stderr; no file. **Any other exit code is not part of the contract** and Electron fails closed on it |
| Readiness | From the handler for the form’s **first `Shown` event** the helper writes `PICKER_READY_MARKER` on its own line to stdout and flushes. This is the only start-of-picker event Electron can observe, and it is what makes `picker_startup_ms` a measurement rather than a guess. The helper never reads stdin |
| Display | `Screen.FromPoint(Cursor.Position)` at launch, physical pixels. PerMonitorV2 is declared in `app.manifest` and takes effect before any `Screen` query or bitmap allocation |
| UX | Opaque freeze-frame, dimmed shade outside the drag rect, crosshair cursor, live rubber band, mouse-release or Enter confirms, Esc cancels. No annotation tools |
| Packaged path | `{process.resourcesPath}/region-picker/avkit-region-picker.exe`; dev path `native/region-picker/publish/avkit-region-picker.exe`; env override `AVKIT_REGION_PICKER_PATH` (dev/test only) |
| Concurrency | Electron main enforces a single in-flight picker; further `capture-region` triggers are ignored until it exits |
| Structure | `RegionForm` (WinForms shell) delegates every input event to `PickerController`, which owns drag state and calls `RectMath` for all geometry. Neither `RegionForm` nor `Program` reimplements that math |

**Pixels and coordinates.** Everything below is in **physical device pixels**; there are no
logical/DIP coordinates anywhere in the helper.

1. PerMonitorV2 precedes everything — a process that becomes DPI-aware late has already been
   handed virtualized coordinates.
2. `bounds = Screen.FromPoint(Cursor.Position).Bounds`. `bounds.X` and `bounds.Y` **may be
   negative** and neighbouring monitors may run at different scale factors. No code may assume
   the target’s origin is `(0,0)`.
3. **Freeze before the window exists:** allocate a `Format32bppArgb` bitmap of `bounds.Size`, blit
   `bounds` into it with `SRCCOPY | CAPTUREBLT`, and only then construct and show the form with that
   bitmap. `CAPTUREBLT` is required, not optional — without it layered windows appear as holes in the
   frozen frame. The blit goes to `gdi32!BitBlt` through P/Invoke rather than through
   `Graphics.CopyFromScreen`: that overload validates its argument against the `CopyPixelOperation`
   enum and throws `InvalidEnumArgumentException` for `SourceCopy | CaptureBlt`, since the OR of the
   two is not itself a declared member — the managed wrapper cannot express what this helper needs.
4. GDI writes no meaningful alpha, so alpha is forced to fully opaque for every pixel before the
   bitmap is used or saved.
5. The form sits at `bounds`, so `local = physical - bounds.Location`. Clamping happens in
   **local** space, before the crop.
6. The cursor is not drawn.
7. Output is a 32-bpp opaque PNG at `--out`, with no resampling, scaling or colour conversion:
   the saved image’s size equals the clamped selection exactly.
8. **Known limitation — HDR/scRGB:** `BitBlt` performs no colour management, so on a wide-gamut
   display the bytes GDI returns can differ from what the eye saw. Follow-up `CAPTURE-HDR-COLOR`.

### Result publication

Electron passes `--out` as a staging path **inside the inbox directory**:
`{inbox_dir}/{PICKER_STAGING_PREFIX}{uuid}.tmp`. The staging name is dot-prefixed and
non-`.png`, so neither the inbox watcher nor the filmstrip’s PNG listing can surface it.

1. **The pixel guard runs on the staged file**, before publication. An all-black or empty PNG is
   `[Capture] Screen capture blocked` — never a silent success.
2. **Publication never clobbers.** `{yyyy-MM-dd_HH-mm-ss}` resolves to the second, so two
   captures in one second collide. Publication **claims** a name — `{base}.png`, `{base}_2.png`,
   `{base}_3.png`, … — with `fs.linkSync`, treating `EEXIST` as “taken, try the next”, then
   unlinks the staging file. `link` fails rather than overwrites; `rename` does not.
3. **The inbox watcher decides by set difference, not by event name.** `fs.watch` may report
   `filename === null`, and an event for an Electron-owned path may arrive after suppression is
   lifted; neither can be matched against a path. The watcher therefore recomputes the inbox’s
   PNG set and emits `captures:inbox-changed` only when that set differs from the last emitted
   set, with the claimed path inserted before the link is attempted. The baseline set is seeded
   from the first listing without notifying.
4. **Registration failure keeps the PNG.** If `POST /captures` fails the file stays in the inbox
   and the user is told where it is; the capture is never deleted to make a failure tidy.

---

## Domain

### Package

```
packages/core/src/avkit_core/domain/capture.py   # CaptureShot, CaptureRequest, annotations
packages/core/src/avkit_core/ports/capture.py    # ScreenCapturePort, ImageAnnotatePort
```

Enums live in `domain/enums.py` (MEU-34 extends MEU-2). Do **not** add `"captures"` to `QueueRuntime.queue_name` — this module is not a processor queue.

### Enums

| Enum | Values | Persist |
|------|--------|---------|
| `CaptureSource` | `Hotkey`, `Gui`, `McpFullscreen`, `McpRegion`, `McpInteractive`, `Scan` | yes (`.name`) |
| `CaptureRequestStatus` | `Pending`, `Completed`, `Cancelled`, `Expired` | yes |
| `AnnotationType` | `Arrow`, `Rect`, `Highlight`, `Text`, `Pixelate`, `Eraser` | sidecar JSON + API (wire lowercase) |

No `CaptureStatus` job machine. Presence of `annotated_path` is the annotated flag.

### `CaptureShot` — persistable

One row per **original** file in the inbox. Scan upserts by resolved `original_path` (unique).

| Field | Type | Persist | Source |
|-------|------|---------|--------|
| `id` | `str` (UUID) | yes | Spec |
| `original_path` | `Path` | yes | Unique |
| `annotated_path` | `Path \| None` | yes | Set on bake |
| `sidecar_path` | `Path \| None` | yes | `{stem}.ann.json` |
| `display_name` | `str` | yes | Filename |
| `width` / `height` | `int` | yes | Probe |
| `file_size` | `int` | yes | Original bytes |
| `source` | `CaptureSource` | yes | Spec |
| `created_at` / `updated_at` | `datetime` | yes | Spec |

**Invariants**

- SQLite stores **pointers only** — no PNG bytes, no thumbnail blobs.
- `original_path` must resolve **inside** `capture.inbox_dir` (after `resolve()`; reject `..` / junction escape) — 422.
- Scan never deletes rows whose files still exist. If the file is gone, `list` omits it **or** the service marks it missing and `GET` 404s — **omit from list, leave row until Delete** (simpler: **prune missing files from list response and delete the row** on scan). Lock: **scan deletes rows whose original file is missing** (inbox is source of files).
- Baking does not modify `original_path` bytes.
- Convert / TTS / download must **not** insert `CaptureShot` rows.

### `CaptureRequest` — persistable (short-lived)

Used so MCP `capture_interactive` can wait without a reverse RPC into Electron.

| Field | Type | Persist |
|-------|------|---------|
| `id` | `str` (UUID) | yes |
| `status` | `CaptureRequestStatus` | yes |
| `shot_id` | `str \| None` | yes when Completed |
| `created_at` | `datetime` | yes |
| `expires_at` | `datetime` | yes — default now + 120 s |

**State machine**

```
Pending ──→ Completed (path posted)
    │
    ├──→ Cancelled (Esc / user)
    └──→ Expired (ttl; service expires on read)
```

Only **one** Pending request at a time. Second `POST /captures/requests` while Pending → **409**.

### Annotation DTO (not a table)

Sidecar `{ "version": 1, "annotations": [ ... ] }`. Extra keys in sidecar → ignore on read, forbid on write API (`extra="forbid"`).

Wire objects (pixel space of the **original** image):

| `type` | Fields |
|--------|--------|
| `arrow` | `from: [x,y]`, `to: [x,y]`, `color`, `stroke_width` |
| `rect` | `x`, `y`, `width`, `height`, `color`, `stroke_width` |
| `highlight` | `x`, `y`, `width`, `height`, `color`, `opacity` (0–1) |
| `text` | `x`, `y`, `text` (1–500 chars), `color`, `font_size`, `bg_color` (optional) |
| `pixelate` | `x`, `y`, `width`, `height`, `block_size` (2–100, default 10); no `color` (`REGION_DTO`) |
| `eraser` | `x`, `y`, `width`, `height`; no `color`: the fill is sampled from the border (`REGION_DTO`) |

Colors: named `red`, `orange`, `yellow`, `green`, `blue`, `white`, `black` **or** `#RRGGBB`. Unknown → 422.

Integers must be inside image bounds after bake clamp (service clamps to `[0, width]` / `[0, height]` rather than 500). Empty `annotations` array on save is allowed (removes annotated output + sidecar).

`GET /captures/{id}` (shot detail) returns the validated sidecar list as `annotations` (empty array when no sidecar). Catalog `GET /captures` does **not** include the array. A malformed sidecar or unknown `type` is an error on detail GET — never an empty list that Save could silently erase. Extra **top-level** sidecar keys remain ignored on read (`extra="forbid"` still applies to write API).

<a id="annotation-geometry-arrow-text"></a>

### Annotation geometry (arrow + text)

MEU-59 repairs the shipped four-tool editor so **arrow** and **text** land on the pixels the human aimed at, and so the SVG preview matches the Pillow bake. It does **not** add types. Circle, numbered callouts, freehand, blur, curved arrows, spotlight, and frames stay in [Named deferrals](#named-deferrals-not-this-phase). Human-approved 2026-09-19: implement arrow pointer + text, not circle/marker.

| Rule | Contract | Source |
|------|----------|--------|
| Coordinate space | Original image pixels, origin at the PNG top-left. DTO integers, stroke widths, and `font_size` use that space. Desktop / picker coordinates stop at capture. Do **not** multiply renderer pointers by `devicePixelRatio` again | Spec (this section); [CSS `object-fit: contain`](https://developer.mozilla.org/en-US/docs/Web/CSS/object-fit); [SVG `preserveAspectRatio`](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/preserveAspectRatio) |
| Fit model | For original `W×H` in a container `Cw×Ch`: `s = min(Cw/W, Ch/H)`, `ox = (Cw - W*s)/2`, `oy = (Ch - H*s)/2`. Pointer: `x = round((clientX - left - ox) / s)`, same for `y`. Equivalent: one SVG `viewBox="0 0 W H"` with `preserveAspectRatio="xMidYMid meet"` and the inverse of `getScreenCTM()` | Research-backed (MDN); Local Canon (this section) |
| Letterbox | Pointer-down in the empty margin is ignored. A drag that starts on-image clamps to `[0,W]×[0,H]`. Cancelled pointer does not commit | Research-backed |
| Resize / zoom | Window resize and optional zoom change only the presentation transform. Stored annotations do not rewrite | Spec zoom sentence above |
| Arrow | Drag tail → head. Preview and bake share the head: `head = max(10, 5 * stroke_width)`, angle `0.45` rad, filled triangle at `to`, with no outline. The shaft ends at the back of the head plus `ARROW_SHAFT_OVERLAP_PX = 1` (`to − u·(head·cos(angle) − 1)`); an arrow shorter than that draws only the head. The bake draws each arrow at 4× on its own tile and downscales it with LANCZOS. Zero-length GUI gesture creates **no** mark. Bake of a legacy zero-length shaft draws the line and skips the head | Spec viewport tools; Local Canon (`ARROWHEAD_*` in the bake adapter); Session 36 plan D-12, D-13, D-14 |
| Text | Click to place; type; Enter commits; Esc cancels. `text` 1–500; composing IME Enter does not commit. Pillow `ImageDraw.text` / `textbbox` use explicit `anchor="la"` ([Pillow text anchors](https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html)). SVG preview uses `text-anchor="start"` and `dominant-baseline="alphabetic"` at `y + ascent` (the Segoe `la` ascent the bake uses) plus the optional `bg_color` rectangle from the same bbox (Session 36 plan D-11). Font fallback remains Segoe UI → Arial → default. `font_size` is a visible control (not a hardcoded 16). Empty `bg_color` means no plate | Spec viewport tools + bake notes; Research-backed (Pillow) |
| Edit vs bake | The editor always draws vectors on the **original**. After Save, the human may inspect `variant=annotated` **without** stacking SVG on the baked PNG. Selecting a shot loads `GET /captures/{id}` `annotations` as both draft and saved baseline | Spec sidecar + `read_image` variants |
| Dirty | Unsaved overlay **or** a nonempty text draft is dirty. Thumb switch still uses the existing confirm | Spec dirty-thumb; Human-approved repair |
| Save | POST the full list. Renderer parse failure is visible (no silent return). Extra keys → no POST / API 422. Original PNG stays immutable | Spec annotate; Boundary Input Contract |
| Box / highlight | Keep existing bake semantics. They use the same fit mapping so they still land in image space. This MEU does not retune rect inset or highlight `width-1` raster edges | Spec four tools; Human-approved arrow+text focus |
| Dependencies | No Konva, Fabric, Sharp, Paper, svg.js, OpenCV, or generative editors | Human-approved 2026-09-19 research lock |
| MCP | Same annotation DTO. No new action. `get` inherits detail `annotations`; `annotate` unchanged. Descriptions may show one arrow+text example after GUI bake agreement | Spec MCP workflow |

Worked fit example: original `1600×900` in container `800×600` → `s = 0.5`, `oy = 75`. Container point `(400, 300)` maps to image `(800, 450)`, not `(400, 300)`.

<a id="annotation-edit-until-save"></a>

### Annotation edit until Save

MEU-60 adds **edit-after-place** on the Capture page so a human can reposition marks until Save. It does **not** add types, REST fields, or MCP actions. Human-approved 2026-09-20: implement the Astra enhanced approach (`docs/proposals/2026-09-19-p9-capture-annotate-edit-approach-review.md`) in full for in-scope locks. MEU-59 geometry, bake formulas, and sidecar contracts stay.

| Rule | Contract | Source |
|------|----------|--------|
| Select mode | `Select` is an editing mode, not an annotation `type`. Draw tools (Arrow/Box/Highlight/Text) **create** even when the pointer is over an existing mark. A successful create switches to Select with the new mark selected | Human-approved 2026-09-20; Research-backed ([ShareX keybinds](https://getsharex.org/keybinds/)) |
| Arrow edit | Selected arrow shows two CSS-constant handles at `from` and `to`. Body/shaft drag translates both ends by one bounded delta. Endpoint drag updates only that end; collapsing a nonzero arrow to zero length cancels | Human-approved 2026-09-20 |
| Text edit | Enter commits the draft (stationary field). Then drag or keyboard-nudge the committed label. Do not drag the text-entry input. `textBackgroundBox` is the hit plate even when `bg_color` is empty — do not paint or persist a background for that | Human-approved 2026-09-20; Local Canon `TEXT_MODULE` |
| Box / highlight | Select, translate, recolor, remove. No resize handles in this MEU; MEU-100 adds them ([Resize handles](#resize-handles)) | Human-approved 2026-09-20 (Astra deferral accepted); Human-approved 2026-10-29 synthesis A-1 |
| Mark list | Compact list of all mark types, drawing order, labeled buttons. Selects covered marks. Remove mark deletes the selected annotation only — never Capture file Delete | Human-approved 2026-09-20 |
| History | Transient preview is not the undo baseline. One `applyHistory` on successful pointer-up / Enter / Apply color. No-op, Esc and lost capture do not push history or clear redo | Local Canon `applyHistory`; Research-backed (W3C Pointer Events) |
| Pointer | Pointer Events + capture. States: `unavailable`, `idle`, `pressed`, `drawing`, `moving`, `endpointDragging`, `textDraft`, `colorEditing`, `saving`. Drag threshold 3 CSS px. Edit only on original view with overlay + image-load epoch ready | Human-approved 2026-09-20; MEU-59 `overlayReady` |
| Hit-test | Only Select mode hit-tests marks. Handles of the selected arrow win (`to` on a tie). Then reverse-array bodies. Project geometry to CSS for hit radii (handle 5 CSS px, hit 10 CSS px, padding 6 CSS px). Letterbox pointer-down is ignored. Committed DTO integers stay `clampImagePoint` `[0, W-1]×[0, H-1]` — this MEU does not retune MEU-59 mapping | Local Canon `FIT_MAP`; Human-approved 2026-09-20 |
| Color | Native color well + labeled hex field + Apply / Cancel. Candidate is not history. Apply writes uppercase `#RRGGBB` to selected `color` (and the next-mark default); with no selection, Apply updates the default only. Loading a named color must not rewrite the DTO or mark dirty. Named well mapping: red `#FF0000`, orange `#FFA500`, yellow `#FFFF00`, green `#008000`, blue `#0000FF`, white `#FFFFFF`, black `#000000` | Human-approved 2026-09-20; Domain `NAMED_COLORS` |
| Sampler | Removed by MEU-81 (Human-approved 2026-10-03, triage D-51) | Human-approved 2026-09-20; triage D-51 |
| Keyboard | Arrow keys nudge the selected mark 1 image pixel. They move the whole mark, or the arrow end whose handle was grabbed or has keyboard focus (`NUDGE_TARGET`); focus on the draw surface itself returns to the whole mark. Arrow keys move nothing during a live pointer gesture or while focus is in a text field, the filmstrip or a confirm strip. Delete removes the selected mark only when annotation controls own focus. Backspace in the text draft edits text. Esc: clear selection (idle), cancel draft, cancel color candidate, cancel in-progress geometry | Human-approved 2026-09-20; Human-approved 2026-10-03, triage D-49; Session 34 plan D-17 |
| Save | POST the committed list only. Button and `capture:save` command share one guard: matching shot, overlay ready, image epoch, no open text/color/geometry transaction. Failure keeps dirty draft | Local Canon MEU-59 fail-closed; Human-approved 2026-09-20 |
| Rubber-band | First-draw preview uses the same transient layer as moves; mouseup commits | Human-approved 2026-09-20 |
| Dependencies | No Konva, Fabric, Sharp, Paper, svg.js, OpenCV, or generative editors | Human-approved 2026-09-19 research lock (still in force) |
| MCP / REST | Same DTO. No new action or fields | Spec MCP + annotate |

This MEU does **not** retune Pillow arrowhead or text-anchor formulas, does not stack SVG on `variant=annotated`, and does not start Phase 11 layout (MEU-50 / MEU-57).

### Ports

```python
class ScreenCapturePort(Protocol):
    def capture_fullscreen(self, output_path: Path) -> ImageProbe: ...
    def capture_region(self, output_path: Path, bbox: BBox) -> ImageProbe: ...

class ImageAnnotatePort(Protocol):
    def probe(self, path: Path) -> ImageProbe: ...
    def bake(
        self,
        original_path: Path,
        annotations: Sequence[Annotation],
        output_path: Path,
    ) -> ImageProbe: ...
```

`BBox` = `x, y, width, height` in **virtual desktop** pixels (same space as `mss` monitors). `ImageProbe` = `width`, `height`, `file_size`.

The interactive region picker is **not** on these ports (Electron).

Do not use `assert` for boundary checks.

### Domain errors

| Error | When |
|-------|------|
| `CaptureNotSupportedError` | Non-Windows in this phase for OS grab |
| `CaptureFailedError` | Empty/black frame, permission, mss failure |
| `InboxPathError` | Path outside inbox / not a file / not an image |
| `HotkeyConflictError` | Not thrown by Python — Electron-only; do not invent a REST 409 for F2 |
| `AnnotationValidationError` | Unknown type/color, empty text, negative sizes |
| `CaptureRequestConflictError` | Second Pending request |

Reuse `NotFoundError` for unknown id.

---

## Infrastructure

### Ninth + tenth tables

Phase 2 locked seven tables; Phase 8 added `conversion_jobs`. **Phase 9 exception (dated 2026-08-26):** append-only migration adds `capture_shots` and `capture_requests`. Still **no** STI `jobs` table.

Greenfield CREATE in `models.py` plus `migrations.py` no-op-safe `CREATE IF NOT EXISTS`.

| Table | Indexes |
|-------|---------|
| `capture_shots` | unique `original_path`, `created_at` |
| `capture_requests` | `status`, `expires_at` |

UoW grows `capture_shots` + `capture_requests` repositories (CRUD; `get_by_path`; `get_pending_request`).

### Adapter `CaptureAdapter`

| Method | Rule |
|--------|------|
| `capture_fullscreen` | Windows: `mss` or Pillow `ImageGrab`. Save PNG. Probe size |
| `capture_region` | Same, crop `bbox`. Reject width/height < 8 px |
| `probe` | Pillow open; reject non-image |
| `bake` | Pillow `ImageDraw`. Deterministic: stroke widths as given; text uses a documented font fallback (Segoe UI → Arial → default). Tests pin pixels on a fixture PNG |

structlog module key: `capture`.

Dependencies: `pillow`, `mss` in `packages/infrastructure` (MEU-35). Do not import them from `packages/core`.

---

## Service layer

`CaptureService` in `packages/core/src/avkit_core/services/capture.py`.

| Method | Behavior |
|--------|----------|
| `scan_inbox` | List `*.png`, `*.jpg`, `*.jpeg`, `*.webp` in `inbox_dir` (**non-recursive**). Upsert shots; delete rows whose file vanished |
| `list_shots` | `scan_inbox` then return shots newest first |
| `get_shot` | 404 if missing |
| `register_shot(path, source)` | Verify inbox containment + probe; insert. 409 if path already registered (idempotent return of existing row is allowed if file unchanged) |
| `capture_fullscreen` / `capture_region` | Write under inbox with timestamp name; register `McpFullscreen` / `McpRegion` |
| `request_interactive` | Insert Pending; 409 if one Pending |
| `complete_request` / `cancel_request` | Electron callbacks |
| `expire_stale_requests` | Pending past `expires_at` → Expired (called from list/get) |
| `annotate_and_save(id, annotations)` | Write sidecar JSON; bake annotated PNG; set `annotated_path` |
| `read_image(id, variant)` | Return file bytes for `original` \| `annotated` (404 if annotated missing) |
| `remove(id)` | Delete files (original, sidecar, annotated) then row |

Output timestamp pattern: `yyyy-MM-dd_HH-mm-ss.png`. Collision: `…_2.png`, `…_3.png`.

Worker: **no** `QueueRuntime`. Grabs are synchronous in the request (fullscreen/region should complete in seconds). Region-picker wait is polling, not a queue Start.

---

## REST API

Prefix `/api/v1`. Static paths before `{id}`. Dual Bearer. `extra="forbid"`. Invalid → **422**, not 500.

### Boundary inventory

| Surface | Schema owner | Extra | Error |
|---------|--------------|-------|-------|
| REST body/query | Pydantic `CaptureRegisterIn`, `CaptureCreateIn`, `AnnotateIn`, … | forbid | 422 |
| MCP `avkit_capture` | Zod `.strict()` | strict | 422 via REST |
| GUI form | Zod in renderer + REST | — | inline + G15 envelope |
| Region-picker result | Main process only (exit code + staged file) then REST register | — | — |
| File paths | Absolute, inside inbox | — | 422 |
| Settings `capture` | Settings PUT | forbid | 422 unknown key |
| Image bytes | `GET …/image` | — | 404 / 413 if over cap |

Python `assert` is not validation.

### Routes

| Method | Path | Service | Success | Notes |
|--------|------|---------|---------|-------|
| `GET` | `/captures` | `list_shots` | 200 `{ items }` | Catalog envelope — **no** `processor` |
| `POST` | `/captures` | `register_shot` or create-from-mode | 201 `{ item }` | Body below |
| `GET` | `/captures/requests` | pending + expire | 200 `{ items }` | Query `status` |
| `POST` | `/captures/requests` | `request_interactive` | 201 | 409 if Pending exists |
| `POST` | `/captures/requests/{id}/complete` | complete | 200 | Body `{ "path": "..." }` |
| `POST` | `/captures/requests/{id}/cancel` | cancel | 200 | |
| `GET` | `/captures/{id}` | get | 200 | metadata + paths + `annotations` list; **no** bytes. Malformed sidecar → 422 |
| `GET` | `/captures/{id}/image` | `read_image` | 200 `image/png` (or jpeg) | Query `variant=original\|annotated`. Cap 15 MiB → 413 |
| `POST` | `/captures/{id}/annotate` | bake | 200 shot | Body `{ "annotations": [ ... ] }` |
| `DELETE` | `/captures/{id}` | remove | 204 | **Deletes files.** MCP confirm |

### `POST /captures` body

Discriminated by `mode` (wire lowercase):

| `mode` | Fields | Who |
|--------|--------|-----|
| `register` | `path` (absolute), `source` (`hotkey` \| `gui` \| `scan`) | Electron after write |
| `fullscreen` | (none) | MCP / API grab |
| `region` | `x`, `y`, `width`, `height` (ints ≥ 0, width/height ≥ 8) | MCP bbox |

Extra forbid. `register` is what the region-picker path uses — the API does not grab in that mode.

### `CaptureShotOut`

List/create rows: `id`, `original_path`, `annotated_path`, `sidecar_path`, `display_name`, `width`, `height`, `file_size`, `source`, `created_at`, `updated_at`. Paths as strings. No base64. No `annotations` array on the catalog.

Detail `GET /captures/{id}` uses the same fields **plus** `annotations` (validated sidecar list, or `[]`).

### Settings namespace

`namespace` ∈ existing set **plus** `capture`. Else 404.

| Dotted docs name | Leaf key | Type | Default | Notes |
|------------------|----------|------|---------|-------|
| `capture.inbox_dir` | `inbox_dir` | string | `~/Pictures/av-kit` | Browse |
| `capture.hotkey` | `hotkey` | string | `F2` | Electron accelerator |
| `capture.copy_to_clipboard` | `copy_to_clipboard` | bool | `false` | After successful save |
| `capture.close_to_tray` | `close_to_tray` | bool | `true` | |

Health console `module` union adds `capture`.

G8: regenerate committed OpenAPI after these routes.

---

## MCP

New compound tool `avkit_capture` (M2 parity with REST). No second URL space. Zod `.strict()`. Destructive `remove` requires `confirm: true` (M3), and so do `flatten` and `revert` (MEU-67); all three also need the person to accept an elicitation prompt in the IDE, or a native Windows dialog when the IDE cannot ask (user confirmation, §Flatten with backup).

**Phase 5 exception (dated 2026-08-26):** Phase 5 forbids returning media bytes for transcripts/videos. **`avkit_capture` action `image` MAY return MCP image content** (the PNG) so a vision model can place annotations. Cap matches REST 15 MiB. `list` / `get` still return paths only.

**Workflow:** `capture` (fullscreen or bbox) **or** `capture_interactive` (poll `list_requests` until completed) → `image` → `annotate` → done. Inbox review: `list` → `image` → `annotate`.

| action | REST |
|--------|------|
| `list` | `GET /captures` |
| `get` | `GET /captures/{id}` |
| `image` | `GET /captures/{id}/image` |
| `capture` | `POST /captures` mode `fullscreen` \| `region` |
| `capture_interactive` | `POST /captures/requests` then poll |
| `list_requests` | `GET /captures/requests` |
| `annotate` | `POST /captures/{id}/annotate` |
| `remove` | `DELETE /captures/{id}` |
| `flatten` | `POST /captures/{id}/flatten` |
| `revert` | `POST /captures/{id}/revert` |

Do not add a second MCP server inside Electron. Do not call `mss` from `mcp-server/`.

Instructions file addition: Capture is **local screen + local files**. Still never upload to YouTube. `capture_interactive` needs the desktop app running (tray). Fullscreen/region bbox works if the API process can see the session desktop.

---

## GUI implementation notes

| Item | Rule |
|------|------|
| Route | lazy `/capture` like Convert |
| Nav | `SHELL_PRIMARY_NAV` 5th item; testid `nav-capture` |
| Page | `ui/src/renderer/src/features/capture/CapturePage.tsx` |
| Help | `capture-help-content.ts` + HelpCard |
| Commands | `capture-commands.ts`; AppShell listens (G11) |
| Palette | `nav:capture`, `capture:region`, `capture:save`, `capture:open_folder` |
| Tokens | G31/G32/G34 — shared Button variants |
| Filmstrip images | Authenticated `GET …/image` → blob URL. Never `<img src="file://">` |
| E2E | Wave **9** `gui-capture` — `[B]` + CI if no display (`E2E-SANDBOX-NODISPLAY`) |
| Tray | Main-process; not a React route |

Settings page: new **Capture** card (inbox dir, hotkey, copy to clipboard, close to tray) + Browse; since MEU-67 also `flatten_backup` ("Back up the original before Apply to image"), `backup_dir` (with Browse) and `annotated_format` ("Save overlay format").

---

## Residuals registered 2026-09-30

Three residual MEUs from the 2026-09-30 GUI walkthrough (known issues `CAPTURE-TOOLBAR-ICONS`, `CAPTURE-SETTINGS-BUTTON-LABEL`, `CAPTURE-VIEWPORT-ZOOM`, `CAPTURE-FLATTEN-WITH-BACKUP`). They build on MEU-57's page composition and MEU-59/60's geometry and edit model; none reopens those contracts.

<a id="viewport-toolbar-icons-and-options"></a>

### Viewport toolbar icons and Options

> **MEU-65.** `CaptureViewport.tsx` `capture-chrome-tools` is a `flex-nowrap overflow-x-auto` row of text buttons (Select, Arrow, Box, Highlight, Text, Undo, Redo, Original, Annotated, Color + hex, Apply, Cancel, Sample original (Sample removed by MEU-81), Named, font size, Bg, Clear, stroke). At the default window it overflows and shows a horizontal scrollbar. The header's per-page controls are a `Disclosure` titled **Settings**, colliding with the app Settings page.

| Rule | Contract | Source |
|------|----------|--------|
| Icon buttons | Tool, history and view buttons become icon buttons with `title` + `aria-label`; the active tool carries `aria-pressed="true"`; icons come from the icon set already used by the nav rail | Human-approved 2026-09-30 ("icons and tool tips instead of full function names"); Research-backed APG toolbar pattern |
| Contextual options | Color well/hex/Apply/Cancel/Sample (Sample removed by MEU-81)/Named, font size, Bg/Clear and stroke move to a second row rendered only for the tool that uses them; the row keeps every existing `capture-color-*`, `capture-font-size`, `capture-text-bg*`, `capture-stroke` test id | Research-backed (image-editor options bars); Spec test-ID keep |
| No overflow | At the default window size used by the Electron waves the tools row has no horizontal scroll; an E2E assertion checks `scrollWidth <= clientWidth` | Spec |
| Options button | The header `Disclosure` is titled **Options**, rendered as a secondary button with a sliders/gear icon and chevron, `aria-expanded` bound to open state; `capture-settings-toggle` keeps | Human-approved 2026-09-30; Research-backed (options vs Settings convention) |
| Icon size | Each icon button is `size="sm"` (`h-7`, the canonical toolbar height) whose only child is its `aria-hidden` lucide icon; `aria-label` and `title` carry the old visible name, except that a tool disabled without a shot keeps the "Select a shot first" hint | Session 29 plan D-9 |
| Options per tool | The options row shows Color for every tool; Stroke only where a `stroke_width` exists (Arrow, Box, or Select with nothing, an arrow or a box selected); font size and Bg/Clear for the Text tool or a selected text mark. Text options and Stroke never show together (`OPTIONS_BY_TOOL`) | Session 29 plan D-12; Spec 09:343-346 |
| Unchanged | Tool semantics, Select-mode editing, Save guard, mark list, and MEU-59/60 geometry | Local Canon §Annotation geometry / §Annotation edit until Save |

<a id="viewport-zoom"></a>

### Viewport zoom

> **MEU-66.** The viewport only fits the shot to the container; there is no zoom state, wheel handler or +/- control. Large shots cannot be inspected or annotated at pixel precision.

| Rule | Contract | Source |
|------|----------|--------|
| Controls | Wheel over the image zooms about the cursor (Ctrl+wheel identical); `+`, `−` and `Fit` buttons sit in the viewport toolbar (MEU-65 layout); keyboard `Ctrl+=` / `Ctrl+-` / `Ctrl+0` mirror them | Human-approved 2026-09-30 ("mouse wheel and + and - buttons"); Research-backed (Windows Photos / IrfanView wheel-zoom) |
| Levels | `Fit` plus the ladder 0.25, 1/3, 0.5, 2/3, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5 (25 %–500 %, includes `100%`). This is Chromium's `kPresetBrowserZoomFactorsArray` (`third_party/blink/common/page/page_zoom.cc`); stepping past either end is a no-op | Spec; Session 29 plan D-14 |
| Pan | When the image exceeds the container it scrolls/drag-pans; pointer-down in the letterbox still creates nothing | Local Canon §Annotation geometry Letterbox rule |
| Pan gestures | Space+drag and middle-button drag move a clamped offset inside a fixed, `overflow-hidden` frame with no scrollbars. An axis whose image fits is centred; an overflowing axis never shows blank margin. A pan creates no mark, gesture, history entry or sample (Sample removed by MEU-81) | Session 29 plan D-15 |
| Wheel step | Line- or page-mode wheel events step one level each; pixel-mode deltas accumulate to 100 px per step, resetting on a sign change or after 250 ms idle. Every wheel event over the image is prevented, with or without Ctrl, so the page neither scrolls nor zooms | Session 29 plan D-18 |
| Key scope | `Ctrl+=` / `Ctrl+-` / `Ctrl+0` (and `+`, NumpadAdd, NumpadSubtract, Numpad0; Meta on macOS) act only on the Capture page with a shot selected, never while focus is in a text input or a confirm strip is open, and the handled key is prevented. Buttons and keys zoom about the frame centre, the wheel about the cursor | Session 29 plan D-17 |
| Mapping | `FIT_MAP` gains scale and offset for the zoom/pan state so pointer → image mapping, handle radii and hit tests stay exact at every level; **stored annotations never rewrite** | Local Canon §Annotation geometry "Resize / zoom" |
| Persistence | Zoom is view state: reset to `Fit` on shot change; not a setting | Spec |
| Tests | Unit tests for the mapping at zoom ≠ fit (both directions) and Electron cases for wheel, buttons and annotate-at-zoom landing on the aimed pixel | Local Canon MEU-59 test pattern |

<a id="flatten-with-backup"></a>

### Flatten with backup

> **MEU-67.** `annotate_and_save` always writes `{stem}.annotated.png` + sidecar and never touches the original. Human-approved 2026-09-30: add a permanent apply ("flatten") that bakes into the original **after** saving a backup to a backup folder, both governed by settings, with a revert.

| Rule | Contract | Source |
|------|----------|--------|
| Flatten | `POST /captures/{id}/flatten` (body `{}` , `extra="forbid"`): copy `original_path` → `{backup_dir}/{stem}.{YYYYMMDD-HHMMSS}.png`, bake the **saved** annotations over `original_path`, delete `{stem}.annotated.png` and the sidecar, return `CaptureShotOut` with `annotations: []` plus `backup_path`. 409 when there are no saved annotations or when `capture.flatten_backup` is on and the backup could not be written | Human-approved 2026-09-30; Local Canon §Service layer; Boundary Input Contract |
| Revert | `POST /captures/{id}/revert` restores the newest backup for that stem over `original_path` and returns the shot; 404 when no backup exists | Human-approved ("in case user will want to revert") |
| Settings | `capture.flatten_backup: bool = true`, `capture.backup_dir: str` default `{inbox}/.avkit-backup`; no retention cap (the user prunes) — no new governance number | Human-approved ("This needs to be also a setting"); Spec |
| MCP | `avkit_capture.flatten` and `avkit_capture.revert`, both destructive → `confirm: true` required | Spec §Destructive actions [05](05-mcp-server.md) |
| GUI | **Apply to image** button beside Save, enabled only when the shot has saved annotations and the overlay is not dirty; inline confirm strip names the backup path; **Revert** appears when a backup exists; `capture-status` reports success/failure | Local Canon [11 §Capture page layout](11-page-layout.md#capture-page-layout) confirm strips |
| Invariants | Original bytes are recoverable from the backup after a flatten; `probe` dimensions unchanged; the filmstrip thumbnail refreshes; the inbox watcher ignores the backup dir | Spec |
| Tests | Service unit tests (backup written before bake, failure leaves original untouched), contract tests for both routes and the 409/404 cases, MCP tests for confirm handling, one Electron case flatten → revert | Local Canon Phase 9 testing |
| Inputs and convert | Flatten works on PNG in place. A JPEG or WebP shot is converted on Apply: the saved marks are baked into a new `{stem}-converted.png` shot (then `_n` on a name clash), with the usual backup rule; the JPEG/WebP file, its annotated copy, sidecar and row are never touched. Other suffixes are 409 | Session 30 plan D-10; Session 30 plan D-22 |
| Backup name and newest | `{stem}.{YYYYMMDD-HHMMSS}.png`, then `_n` when that name exists; the newest backup is chosen by the parsed (timestamp, n), never by mtime | Session 30 plan D-9 |
| Backup folder | `capture.backup_dir` `""` (the default) means `{inbox}/.avkit-backup`, resolved at use time; any other value must be absolute after `~` expansion and must not be the inbox itself (409 at flatten) | Session 30 plan D-11 |
| Detail field | `GET /captures/{id}`, flatten and revert return `backup_path` (the newest backup or `null`); list items keep their key set | Session 30 plan D-13 |
| Revert keeps the backup | Revert copies the backup over the original (the backup stays) and re-bakes the annotated copy when saved marks remain | Session 30 plan D-14 |
| Save overlay format | `capture.annotated_format` `png` \| `jpeg` \| `webp` (default `png`; lossy quality 90) chooses the annotated copy's format when Save overlay runs; one annotated sibling exists at a time, and the inbox scan skips all three | Session 30 plan D-23 |
| User confirmation (MCP) | `avkit_capture.remove`, `flatten` and `revert` also ask the person through MCP elicitation and run only on an accept with `confirm: true`; decline, cancel, an error or the 120 s timeout refuse with `user_confirmation_refused`; a client without elicitation, or a decline under 250 ms (an auto-decline), falls back to a native Windows Yes/No dialog | Session 30 plan D-24, A-11 |

---

## Residuals registered 2026-10-09

Twelve residual MEUs from Mat's Session 29/30 looks and the 2026-10-09 triage (`known-issues.yaml` decisions D-40 to D-69). They build on MEU-65/66/67; none reopens MEU-59/60 geometry except where a row says so with its Human-approved source.

<a id="icon-button-hints"></a>

### Icon-button hints

> **MEU-80.** `CAPTURE-TOOLTIPS-NOT-SHOWN`: no native `title` tooltip appears anywhere in the dev app (nav rail and Capture, local check 2026-10-09), although the titles are in the DOM. Session 30 A-10 proved a rendered `role="tooltip"` works where `title` does not.

| Rule | Contract | Source |
|------|----------|--------|
| Scope | Every icon-only function button (an image, no visible words) shows a hint on hover and on keyboard focus, including while disabled; labelled controls such as nav-rail items are out of scope | Human-approved 2026-10-09 triage D-69 |
| Primitive | One shared renderer tooltip (portaled, fixed-position, `role="tooltip"`, `aria-describedby`) generalises the A-10 wrapper; disabled buttons get a focusable wrapper so the hint still shows | Triage D-48; Session 30 A-10 |
| Root cause first | The plan's first row reproduces the missing native tooltips on the target; a one-line environment fix is recorded if found, and the primitive still ships for icon-only buttons | Triage D-48 |
| Hint text and timing | The hint reads the control's accessible name, or `name — reason` while it is disabled for a reason (`HINT_TEXT`). Hover shows it after 400 ms and keyboard focus at once; blur, Escape or a press hides it; leaving hides it after a 120 ms grace unless the pointer moves into the hint; a hint shown by focus stays until blur or Escape (`HINT_TIMING`) | Session 34 plan D-9, D-10 |
| Root-cause finding | No environment cause: Chromium draws the native `title` tooltip on an enabled button, but `Button.tsx` `disabled:pointer-events-none` means a disabled button never receives hover, so its `title` never shows. MEU-80's focusable wrapper fixes it in the product; nothing outside the product was needed | Session 34 plan D-14 |
| Tests | Unit for show/hide on hover and focus; Electron real-hover visibility for an enabled and a disabled icon button | Local Canon Session 30 AC-67.35 pattern |

<a id="capture-action-row"></a>

### Capture action row

> **MEU-81.** `CAPTURE-ACTION-ROW-ICONS`, `CAPTURE-MARKS-ROW-SQUEEZED`, `CAPTURE-SAMPLE-ORIGINAL-UNLABELED`, `CAPTURE-HOTKEY-BANNER-GAP`. The second chrome row (`CaptureViewport.tsx:886-987`) overflows at 1280×800 once Apply to image and Revert join it and can shrink to 28 px; the Sample original eyedropper is unexplained; the always-mounted hotkey banner leaves an empty ~48 px band.

| Rule | Contract | Source |
|------|----------|--------|
| Icons | Per-shot and per-mark actions become icon buttons through `ToolbarIconButton` with `aria-label` and the MEU-80 hint: Remove mark, Save overlay, Apply to image, Revert, Open file, Open folder; Delete shot is red at the far right after a separator | Human-approved 2026-10-03 (Mat), triage D-49 |
| Removed | Body/Tail/Head and the four nudge buttons are removed for every mark type; arrow keys nudge the selected mark or the focused endpoint; the drag handles stay | Human-approved 2026-10-03, D-49 (amends MEU-60 ACs) |
| No eyedropper | The Sample original button and its sampling state are removed; hex and Named cover colour choice | Human-approved 2026-10-03, triage D-51 (amends AC-60 sampling ACs) |
| Row size | The row is `shrink-0` and has no horizontal scroll at the default window (NO_OVERFLOW assertion as AC-65.4) | Triage D-50 |
| Hotkey status | The hotkey status shows inline in the Capture header row; the reserved banner band is gone and nothing shifts when a message appears | Human-approved 2026-10-09 triage D-64 (amends AC-57.3) |
| Endpoint nudge | The arrow's two end handles are focusable buttons (“Arrow tail”, “Arrow head”) in a handle layer over the marks. Grabbing or focusing one makes the arrow keys move that end; focus on the draw surface itself returns to the whole mark | Session 34 plan D-17 |
| Marks row layout | The marks row is `shrink-0` and never scrolls; only the mark-chip list scrolls (`min-w-0 flex-1 overflow-x-auto`), and the action slot is `shrink-0` | Session 34 plan D-18 |
| Tests | Behaviour tests for each icon action and keyboard nudge; Electron NO_OVERFLOW and header-status geometry at the default window | Local Canon |

<a id="text-preview-baseline"></a>

### Text preview baseline

> **MEU-82.** `CAPTURE-TEXT-BG-PREVIEW-OFFSET`: the bake is right, but the SVG preview places text with `dominant-baseline="hanging"`, which Chromium puts above the ascender line, so the plate covers only the bottom of the glyphs in the viewport.

| Rule | Contract | Source |
|------|----------|--------|
| One anchor | The SVG text sits on the alphabetic baseline at `y + ascent(font_size)` from the same Segoe metrics the bake uses, so preview, plate and bake share one anchor; hit-test and selection boxes follow | Triage D-52; Local Canon §Annotation geometry |
| Tests | A preview-vs-bake pixel comparison for a text mark with a plate; unit tests for the metric constants | Triage D-52 |

<a id="arrow-bake-geometry"></a>

### Arrow bake geometry

> **MEU-83.** `CAPTURE-BAKE-ARROW-THIN`: the baked arrow is jagged (no anti-aliasing, `adapter.py:303-316`) and its flat-capped shaft runs to the tip, so its corners poke past the head in both bake and preview.

| Rule | Contract | Source |
|------|----------|--------|
| Shaft end | The shaft ends at the back of the head (tip − head·cos(angle), small overlap), in bake and preview alike | Human-approved 2026-10-03 (Mat), triage D-53 |
| Anti-aliasing | Arrow marks are drawn at 4× and downscaled with LANCZOS in the bake | Triage D-54; Research-backed (Pillow has no AA for lines/polygons) |
| Head | `head = max(10, 5 * stroke_width)`, angle `0.45` rad, within the §Annotation geometry stroke contract | Triage D-54; Session 36 plan D-12 |
| Tests | Bake fixture: no shaft pixels beyond the head base; edge smoothness check; preview geometry unit tests | Local Canon MEU-59 tests |

<a id="annotated-file-sync-and-open-file"></a>

### Annotated file sync and Open file

> **MEU-84.** `CAPTURE-STALE-ANNOTATED-PATH`, `CAPTURE-OPEN-FILE-VARIANT`. `scan_inbox` drops rows whose original is gone but never re-checks `annotated_path`/`sidecar_path`; Open file always opens `original_path` whatever the viewport shows (`capture-commands.ts:117-123`).

| Rule | Contract | Source |
|------|----------|--------|
| Reconcile | `scan_inbox` clears `annotated_path` and `sidecar_path` whose files are gone | Triage D-55 |
| Open what you see | Open file opens the file the viewport shows (Annotated view → the annotated copy; Original view → the original); Open folder reveals the same file | Human-approved 2026-10-09 triage D-65 (amends AC-39.12) |
| Tests | Service test for the reconcile; behaviour tests for both views and the fallback when the annotated copy is missing | Local Canon |

<a id="size-scrubbing"></a>

### Size scrubbing

> **MEU-85.** `CAPTURE-SIZE-MOUSE-CONTROL`: stroke width and font size are bare number fields.

| Rule | Contract | Source |
|------|----------|--------|
| Gestures | Keep the number field; dragging its label scrubs the value (Shift ×10, Alt fine), the wheel over the field steps it, Up/Down step it | Mat's request 2026-10-03; triage D-56 (Research-backed scrub pattern) |
| Edit model | The selected mark previews live while scrubbing; one gesture is one undo step | Triage D-56; Local Canon §Annotation edit until Save |
| Tests | Unit for the scrub math and limits; behaviour test for one undo per gesture | Local Canon |
| Plan | `SCRUB_MATH`: 2 px per step (8 px with Alt), Shift ×10, wheel steps through `wheelSteps`; the limits 1–100 (stroke) and 1–400 (font) are UI-only scrub caps, and typed values keep their rules. `CaptureScrubField` is shared, so the Block size field can adopt it. A gesture is one `SIZE_BURST`: Escape restores its start, and Undo and Redo stay off while it is open | Session 37 plan D-10–D-15 |

<a id="named-colour-swatches"></a>

### Named colour swatches

> **MEU-86.** `CAPTURE-NAMED-COLOR-SWATCHES`: the Named select shows plain names.

| Rule | Contract | Source |
|------|----------|--------|
| Swatches | Each option uses its colour as background with a contrast-picked text colour; if the target ignores option backgrounds, a swatch popover replaces the native select | Triage D-57; Local Canon G30 |
| Tests | Unit for the contrast helper; Electron check of the rendered option style | Local Canon |
| Plan | `CONTRAST_TEXT` picks black or white by the higher WCAG 2.1 contrast ratio (red, orange, yellow and white get black). Electron 42 on Windows paints option backgrounds (R-1), so no swatch popover is built; the placeholder and the closed select keep the G30 menu style | Session 37 plan D-16–D-17 |

<a id="tool-lock"></a>

### Tool lock

> **MEU-87.** `CAPTURE-AUTO-SELECT-AFTER-DRAW`: after each mark the tool returns to Select (AC-60.4), so several marks need a tool click each.

| Rule | Contract | Source |
|------|----------|--------|
| Default unchanged | Auto-Select after drawing stays the default (AC-60.4) | Human-approved 2026-10-09 triage D-63 |
| Lock | A tool lock keeps the current tool after each mark until the lock is released or another tool is chosen; its state is visible (`aria-pressed`) | Human-approved D-63; Research-backed (Excalidraw / tldraw tool lock) |
| Tests | Behaviour tests with and without the lock | Local Canon |
| Plan | `TOOL_LOCK` is a toolbar toggle after the tool group ("Keep tool after drawing"), page view state that is never persisted. `LOCK_PERSISTS`: choosing another tool keeps the lock on, so the new tool is kept; only the lock button releases it | Session 37 plan D-18–D-19 |

<a id="filmstrip-context-menu"></a>

### Filmstrip context menu

> **MEU-88.** `CAPTURE-FILMSTRIP-CONTEXT-MENU`: Mat asked for a thumbnail right-click menu.

| Rule | Contract | Source |
|------|----------|--------|
| Items | Copy full path, Copy image, Delete; Delete reuses the existing confirm | Mat's request 2026-10-03; triage D-58 |
| Clipboard | Path and image copies run in the main process through preload IPC (`clipboard.writeText` / `writeImage`) | Triage D-58; Local Canon G27 |
| Index | New actions are added to the gui-actions-index at plan time | Local Canon |
| Tests | Behaviour tests per item; main-process clipboard test; keyboard access (context-menu key) | Local Canon |
| Copy image source | Copy image copies the shot's original (`variant=original`). The renderer fetches it through the authorized image route and re-encodes a non-PNG file to PNG; main decodes the PNG bytes with `nativeImage.createFromBuffer` and calls `clipboard.writeImage` (strict `write-clipboard-image` channel) | Session 38 plan D-10, D-11 |

<a id="filmstrip-multi-select"></a>

### Filmstrip multi-select

> **MEU-89.** `CAPTURE-FILMSTRIP-MULTISELECT` (after MEU-88).

| Rule | Contract | Source |
|------|----------|--------|
| Selection | Shift-click selects a range from the current shot; the editor shows the last-clicked shot | Mat's request 2026-10-03; triage D-59 |
| Batch delete | With more than one selected, the context menu shows only Delete, with one confirm naming the count; removes run in order and report per-shot failures | Mat's request; triage D-59 |
| Tests | Behaviour tests for range selection, the batch confirm and a partial failure | Local Canon |
| Anchor and order | The anchor is the last plain-clicked shot, or the editor's shot when there is none, and stays fixed across Shift-clicks; the range is the inclusive slice in filmstrip order. DELETEs run one at a time in that order with encoded ids, continue past failures and refresh the catalog once; the selection moves to the newest survivor if the editor's shot went | Session 38 plan D-15, D-18 |
| Checkboxes | Each thumb has a checkbox to its left. Ticking it adds or removes that shot without changing the editor's shot; Shift-click on a thumb or a box selects a range; a plain thumb click clears the ticks. The batch menu, confirm and deletes apply to the ticked set in filmstrip order | Mat's request 2026-10-16; Session 38 plan D-25 |

<a id="pixelate-mark"></a>

### Pixelate mark

> **MEU-90.** `CAPTURE-PIXELATE-TOOL`: Mat asked for a mosaic mark (2026-10-03).

| Rule | Contract | Source |
|------|----------|--------|
| Mark | A new `pixelate` rectangle in the Annotation union, sidecar and OpenAPI/MCP annotate schema; drawn, selected and moved like a box | Mat's request; Local Canon §Annotation DTO |
| Bake | Downscale the rectangle by the block size, upscale with nearest-neighbour; default block 10 px, adjustable with the size control | Triage D-60 (Research-backed: ShareX/Greenshot pixel size) |
| Preview | The editor previews the mosaic live | Mat's request |
| Tests | Bake fixture, schema contract tests, MCP annotate test, preview test | Local Canon |
| Plan | `REGION_PASS`: region marks (pixelate, eraser) are applied first in list order, then the drawn marks are painted on top, in the bake and the preview alike. `PIXELATE_BLOCK`: `block_size` 2–100, default 10 | Session 39 plan D-10, D-11, D-12 |

<a id="eraser-mark"></a>

### Eraser mark

> **MEU-91.** `CAPTURE-ERASER-TOOL` (after MEU-90's new-mark plumbing).

| Rule | Contract | Source |
|------|----------|--------|
| Mark | A new `eraser` rectangle in the Annotation union, sidecar and OpenAPI/MCP schema | Mat's request 2026-10-03 |
| Fill | The area is filled with the colour sampled from the rectangle's border, for PNG, JPEG and WebP alike; no extra button | Human-approved 2026-10-09 triage D-62 |
| Tests | Bake fixture for the sampled fill, schema contract tests, preview test | Local Canon |
| Plan | `ERASER_SAMPLE`: the fill is the most frequent RGB in the 1-px ring outside the clipped rectangle (its own edge pixels when that ring is empty), a tie going to the smallest packed value; it is sampled on the canvas as `REGION_PASS` leaves it at that mark, so an eraser after a pixelate samples the mosaic | Session 39 plan D-10, D-13 |

## Residuals registered 2026-10-29

Nine residual MEUs from the Human-approved capture annotation synthesis (`_inspiration/capture-annotation-tools/synthesis.md`, accepted by Mat on 2026-10-29: all recommendations, D-1 to D-3). They bring the editor to the behaviour users expect from other annotation tools while keeping the MVP scope. Grouping: `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md`.

<a id="canvas-history-chords"></a>

### Canvas history chords

> **MEU-99.** Synthesis slice 1 (M-1, A-3; D-1 revises 06 D-136). Ctrl+Z does nothing on the canvas today: the default Edit menu's undo role targets the focused web contents, and Capture keeps its own history.

| Rule | Contract | Source |
|------|----------|--------|
| Chords | On the Capture editor, Ctrl+Z undoes one step; Ctrl+Y and Ctrl+Shift+Z redo one step (Meta counts as Ctrl). The renderer handles them and calls `preventDefault`, which keeps the Electron menu accelerator from running; the application menu and `RESERVED_CHORDS` are unchanged | Human-approved 2026-10-29 synthesis D-1, A-3; Local Canon AC-66.13 (a renderer `preventDefault` suppresses the menu accelerator) |
| Focus | The chords act only when focus is the page body or a Capture editor control (`annotationOwnsFocus`), never in an editable field, the text draft, an open confirm or any `aria-modal` dialog. A text field keeps its native undo | Human-approved 2026-10-29 synthesis A-3, G-2 |
| Guards | No-op while a transaction or a gesture is open, during IME composition, or with nothing to undo or redo. One chord is one step, the same as one button click | Local Canon `applyHistory` |
| Hints | The Undo and Redo buttons show `Undo (Ctrl+Z)` and `Redo (Ctrl+Y)` and carry `aria-keyshortcuts` | 06 §Common shortcuts "Hints" |
| Tests | Behaviour tests for each chord, focus case and guard; Electron proof that a canvas chord undoes, a text draft keeps native undo, and the page does not reload or zoom | Local Canon |

> **Delivered (Session 43).**
> - `CapturePage` handles Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z (Meta counts as Ctrl) while `annotationOwnsFocus`, with `preventDefault`; one chord is one `applyHistory` step, and an open transaction, gesture, IME composition, text field or dialog keeps the chord inert.
> - The Undo and Redo buttons show `Undo (Ctrl+Z)` and `Redo (Ctrl+Y)` with `aria-keyshortcuts`. The menu and `RESERVED_CHORDS` members are unchanged.
> - AC-99.1 to AC-99.7.
> - Gate: `session-gate.ps1`, all steps exit 0 (walkthrough §Gate).
> - Plan `docs/execution/plans/2026-10-29-capture-editor-repair/`.

<a id="resize-handles"></a>

### Resize handles

> **MEU-100.** Synthesis slice 2 (M-2, A-1, C-11). Supersedes the MEU-60 "No resize handles in this MEU" row for area marks.

| Rule | Contract | Source |
|------|----------|--------|
| Handles | A selected box, highlight, pixelate or eraser mark shows 8 handles (4 corners, 4 edge midpoints), 8 CSS px visible and 12 CSS px hit, constant on screen at every zoom, with a contrasting outline. Handles are editor-only and never saved or baked | Human-approved 2026-10-29 synthesis A-1, C-11 |
| Resize | Dragging a handle moves only its edges; the opposite edge or corner stays fixed. Crossing over normalizes the box, the result is clamped to the image, width and height stay at least 1 image px, and every coordinate stays an integer. Every other field (colour, stroke, `block_size`) is kept | Human-approved 2026-10-29 synthesis A-1 |
| History | The drag previews live; pointer-up records one `applyHistory` step when the box changed; Escape or a lost pointer restores the original with no history | Local Canon `applyHistory` |
| Hit order | The selected mark's handles win over any mark body; corners win ties with edges. Unselected marks show no handles; arrows keep their end handles | Local Canon |
| Cursor | Hovering a handle shows the matching resize cursor (`nwse`, `nesw`, `ns`, `ew`) | Human-approved 2026-10-29 synthesis A-1 |
| Tests | Unit tests for the resize maths and handle hit-testing at several zooms; behaviour tests per mark type; Electron proof of a real handle drag, Save and Undo | Local Canon |

> **Delivered (Session 43).**
> - `capture-transform.ts` (`resizeBox`, `boxHandlePoints`) resizes a selected box, highlight, pixelate or eraser mark from 8 handles, 8 CSS px visible and 12 CSS px hit at every zoom; the opposite edge stays fixed, the box normalizes, clamps to the image and stays at least 1 px.
> - The drag previews live and records one step on pointer-up; Escape or a lost pointer restores it. Handles win over bodies, corners over edges, and each shows its resize cursor.
> - AC-100.1 to AC-100.11.
> - Gate: `session-gate.ps1`, all steps exit 0 (walkthrough §Gate).
> - Plan `docs/execution/plans/2026-10-29-capture-editor-repair/`.

<a id="text-re-edit-and-scaling"></a>

### Text re-edit and scaling

> **MEU-101.** Synthesis slice 3a (M-3, A-2, A-6). Users reported that committed text cannot be changed.

| Rule | Contract | Source |
|------|----------|--------|
| Re-edit | Double-clicking a text mark in Select mode, or Enter with a text mark selected, reopens the text field prefilled with its words; the mark is hidden while it is edited | Human-approved 2026-10-29 synthesis A-2 |
| Commit | Enter replaces the text as one undo step; unchanged text records nothing; Escape or an empty field restores the original with no history | Human-approved 2026-10-29 synthesis A-2 |
| Scale | A selected text mark shows 4 corner handles on its plate (`textBackgroundBox`). Dragging one scales `font_size` about the opposite corner, clamped to 1..400, and moves `x`/`y` so that corner stays put (within 1 px). One drag is one undo step. No side handles until wrap exists | Human-approved 2026-10-29 synthesis A-6, C-3 |
| Tests | Behaviour tests for both re-edit paths, no-op, Escape and empty commits, and the scale maths; Electron proof of a double-click re-edit and Save | Local Canon |

> **Delivered (Session 43).**
> - A Select-mode double-click on a text mark, or plain Enter with it selected, reopens the text field with its words and hides the mark; Enter replaces the text as one step, and unchanged text, an empty field or Escape record nothing.
> - `scaleTextMark` scales `font_size` (1..400) from the 4 plate corners about the opposite corner, one drag one step.
> - AC-101.1 to AC-101.6.
> - Gate: `session-gate.ps1`, all steps exit 0 (walkthrough §Gate).
> - Plan `docs/execution/plans/2026-10-29-capture-editor-repair/`.

<a id="multi-line-text"></a>

### Multi-line text

> **MEU-102.** Synthesis slice 3b (A-7). Open question G-3: what the preview and the bake do today with an agent-sent `\n`; the plan settles it first.

| Rule | Contract | Source |
|------|----------|--------|
| Keys | Enter commits and Shift+Enter adds a line; Enter belongs to the IME during composition. The field shows the hint while editing | Human-approved 2026-10-29 synthesis A-7 |
| Model | `text` gains defined `\n` semantics; line spacing derives from `font_size` with no new field, unless G-3 shows stored marks need a layout version | Human-approved 2026-10-29 synthesis §7 data-model changes |
| Parity | The Segoe metrics table extends to multiple lines, and bake fixtures prove the preview and the bake agree. No automatic wrap (wrap width is Later, C-3) | Human-approved 2026-10-29 synthesis A-7, C-3 |

<a id="redact-mark"></a>

### Redact mark

> **MEU-103.** Synthesis slice 4 (M-5, A-5, A-11, A-16; C-1, C-2, C-10). A pixelated secret fails silently, so solid redaction becomes the default.

| Rule | Contract | Source |
|------|----------|--------|
| Mark | A new `redact {x, y, width, height, color="#000000"}` type in the Annotation union, sidecar, OpenAPI and MCP schemas, baked in the region pass at full opacity; an older server rejects the unknown type | Human-approved 2026-10-29 synthesis C-1, C-2 |
| Tool | One Redact tool with a Solid / Pixelate toggle, Solid by default; switching a selected mark replaces it as one undo step. Redact marks get the MEU-100 handles | Human-approved 2026-10-29 synthesis C-2 |
| Rename | Eraser is shown as "Smart eraser" with the tooltip "Covers an area with the surrounding colour"; the JSON type `eraser` and its algorithm are unchanged | Human-approved 2026-10-29 synthesis C-10, D-3 |
| Outlines | Redaction marks show a dashed editor-only outline, never baked | Human-approved 2026-10-29 synthesis A-16 |

<a id="copy-image-and-action-names"></a>

### Copy image and action names

> **MEU-104.** Synthesis slice 5 (M-4, A-4, A-15; C-5, C-14, B-1; G-6 option a).

| Rule | Contract | Source |
|------|----------|--------|
| Copy image | A Copy image button and canvas Ctrl+C put the image with the current, possibly unsaved, marks on the clipboard. It is rendered by a new `POST /captures/{id}/render` that bakes the posted marks exactly as Save would, without writing a file. Text fields keep native copy | Human-approved 2026-10-29 synthesis C-5, G-6(a) |
| Labels | The action row reads "Save annotations", "Flatten into image…" and "Restore backup…"; the dirty-flatten confirm offers "Save and flatten" | Human-approved 2026-10-29 synthesis C-14, B-1 |

<a id="style-and-tool-flow"></a>

### Style and tool flow

> **MEU-105.** Synthesis slice 6 (A-8, A-9, A-10, A-12, A-13, B-12; C-4, C-6, C-12; D-2).

| Rule | Contract | Source |
|------|----------|--------|
| Colour | Swatches apply on click; the hex field applies on Enter or blur; one click or scrub is one undo step. The Apply/Cancel gate goes | Human-approved 2026-10-29 synthesis A-8 |
| Tool style | Each tool remembers its own style as an app preference, never mark JSON. With a mark selected a control restyles only that mark | Human-approved 2026-10-29 synthesis A-9 |
| Lock | Lock is on by default and persisted, with a one-shot preference; the just-drawn mark stays selected, and while a tool is armed a press on the selected mark edits it while a press elsewhere draws | Human-approved 2026-10-29 synthesis C-6, D-2 |
| Letters | V Select, A Arrow, R Box, H Highlight, T Text, X Redact, E Smart eraser, as page-scoped registry entries that never fire in a field | Human-approved 2026-10-29 synthesis C-12, A-12 |
| Modifiers | Shift constrains aspect or square and snaps arrows to 45 degrees; Alt draws from the centre; Shift+arrow nudges 10 px. Pixelate block size gets a scrub | Human-approved 2026-10-29 synthesis A-13, B-12 |

<a id="line-and-ellipse"></a>

### Line and ellipse

> **MEU-106.** Synthesis slice 7 (A-14, B-7, C-13). Amends the named deferral of circles.

| Rule | Contract | Source |
|------|----------|--------|
| Line | `arrow.head?: "end" | "none" | "both"`, default `"end"`; Line is an arrow with `head: "none"` | Human-approved 2026-10-29 synthesis C-13 |
| Ellipse | `rect.shape?: "rect" | "ellipse"`, default `"rect"`, with the MEU-100 handles | Human-approved 2026-10-29 synthesis A-14 |
| Duplicate | Ctrl+D duplicates the selected mark with an offset, clamped, and selects the copy | Human-approved 2026-10-29 synthesis B-7 |

<a id="step-mark"></a>

### Step mark

> **MEU-107.** Synthesis slice 8 (C-8). Amends the named deferral of numbered callouts.

| Rule | Contract | Source |
|------|----------|--------|
| Mark | A new `step {x, y, number, color, size}` type through every layer, so an agent reads the number directly; the badge text is centred in the preview and the bake alike | Human-approved 2026-10-29 synthesis C-8 |

## Named deferrals (not this phase)

| Feature | Why |
|---------|-----|
| macOS / Linux region picker + hotkey | Windows-first; the helper is `win-x64` and mss-on-Linux is not a ship gate |
| Window / fullscreen GUI buttons | F2 region is the user loop |
| In-overlay arrows (ShareX ShapeManager) | Annotation is the Capture page / MCP |
| Freehand, blur, curved arrows, spotlight, frames, callouts | Four tools only; Pixelate and Eraser are added by MEU-90/91 (Mat's 2026-10-03 request, 2026-10-09 triage). Ellipse and Line (MEU-106), numbered steps (MEU-107) and solid Redact (MEU-103) are registered by the 2026-10-29 capture editor residuals |
| Timer / window-focus / clipboard-watch auto-capture | Not the F2 loop |
| ShareX uploaders, after-upload, OCR, GIF, video, scrolling capture | Out of product |
| Downloader / Convert → Capture handoff | Would reopen those pages |
| Recursive inbox scan / subfolders | Flat inbox |
| SSE | Poll + `fs.watch` IPC |
| MCP Guard | Still deferred (06) |
| Session 8c / MEU-27 | Human-gated; do not pack into Phase 9 |

---

## MEUs

| MEU | Slug | Section | Depends on |
|-----|------|---------|------------|
| MEU-34 | `domain-capture` | Domain + ports + errors | MEU-4 |
| MEU-35 | `infra-capture` | `capture_shots` / `capture_requests` + adapter | MEU-34, MEU-5 |
| MEU-36 | `svc-capture` | CaptureService | MEU-35 |
| MEU-37 | `api-capture` | REST + settings namespace + OpenAPI | MEU-36, MEU-14 |
| MEU-38 | `mcp-capture` | `avkit_capture` | MEU-37, MEU-17 |
| MEU-39 | `gui-capture` | Tray, F2, overlay, rail, page, Help, Wave 9 | MEU-37, MEU-19, MEU-26 |
| MEU-40 | `native-region-picker` | Native region picker helper + Electron integration; retires the Chromium overlay MEU-39 shipped | MEU-39 |
| MEU-59 | `gui-capture-annotate-arrow-text` | Fit-to-viewport mapping, arrow+text preview/bake agreement, sidecar reload on GET detail | MEU-39, MEU-40 |
| MEU-60 | `gui-capture-annotate-edit-until-save` | Select-mode edit until Save: arrow ends/body, move text/box/highlight, mark list, Apply color + original-image sampler | MEU-59 |
| MEU-65 | `gui-capture-toolbar-icons` | [Viewport toolbar icons and Options](#viewport-toolbar-icons-and-options) | MEU-57, MEU-60 |
| MEU-66 | `gui-capture-zoom` | [Viewport zoom](#viewport-zoom) | MEU-59, MEU-65 |
| MEU-67 | `capture-flatten-backup` | [Flatten with backup](#flatten-with-backup) | MEU-38, MEU-60 |
| MEU-80 | `gui-icon-button-hints` | [Icon-button hints](#icon-button-hints) | MEU-65, MEU-67 |
| MEU-81 | `gui-capture-action-row` | [Capture action row](#capture-action-row) | MEU-80, MEU-67 |
| MEU-82 | `capture-text-baseline` | [Text preview baseline](#text-preview-baseline) | MEU-59 |
| MEU-83 | `capture-arrow-geometry` | [Arrow bake geometry](#arrow-bake-geometry) | MEU-59, MEU-67 |
| MEU-84 | `capture-file-variant-sync` | [Annotated file sync and Open file](#annotated-file-sync-and-open-file) | MEU-39, MEU-67 |
| MEU-85 | `gui-capture-size-scrub` | [Size scrubbing](#size-scrubbing) | MEU-65 |
| MEU-86 | `gui-capture-color-swatches` | [Named colour swatches](#named-colour-swatches) | MEU-65 |
| MEU-87 | `gui-capture-tool-lock` | [Tool lock](#tool-lock) | MEU-60, MEU-65 |
| MEU-88 | `gui-capture-filmstrip-menu` | [Filmstrip context menu](#filmstrip-context-menu) | MEU-57 |
| MEU-89 | `gui-capture-filmstrip-multiselect` | [Filmstrip multi-select](#filmstrip-multi-select) | MEU-88 |
| MEU-90 | `capture-pixelate-mark` | [Pixelate mark](#pixelate-mark) | MEU-59, MEU-67 |
| MEU-91 | `capture-eraser-mark` | [Eraser mark](#eraser-mark) | MEU-90 |
| MEU-99 | `gui-capture-history-chords` | [Canvas history chords](#canvas-history-chords) | MEU-60, MEU-97 |
| MEU-100 | `gui-capture-resize-handles` | [Resize handles](#resize-handles) | MEU-60, MEU-91 |
| MEU-101 | `gui-capture-text-reedit` | [Text re-edit and scaling](#text-re-edit-and-scaling) | MEU-82, MEU-100 |
| MEU-102 | `capture-text-multiline` | [Multi-line text](#multi-line-text) | MEU-101 |
| MEU-103 | `capture-redact-mark` | [Redact mark](#redact-mark) | MEU-91, MEU-100 |
| MEU-104 | `capture-copy-image-actions` | [Copy image and action names](#copy-image-and-action-names) | MEU-81, MEU-99 |
| MEU-105 | `gui-capture-style-tool-flow` | [Style and tool flow](#style-and-tool-flow) | MEU-87, MEU-99, MEU-100 |
| MEU-106 | `capture-line-ellipse-shapes` | [Line and ellipse](#line-and-ellipse) | MEU-100, MEU-105 |
| MEU-107 | `capture-step-mark` | [Step mark](#step-mark) | MEU-105 |

---

## Exit criteria

- Domain: `CaptureShot` invariants + ports tested; no `QueueRuntime` for captures; Convert/TTS unaffected (regression).
- Infra: ninth/tenth tables; bake on a fixture PNG; Windows grab unit-tested with a fake port in service tests (live mss is integration-only).
- Service: inbox scan upsert/prune; path containment; interactive 409; delete removes files.
- API: every route has ≥1 contract test; extra field → 422; `{ items }` has no `processor`; OpenAPI committed; image GET is authenticated.
- MCP: action table parity; confirm on `remove`; `image` returns image content.
- GUI: Capture under Convert; Ctrl+5; filmstrip + six tools; Save bakes; tray + F2 documented; action-index audit; Wave 9 written and wired.

---

## What this layer must not do

| Forbidden | Why |
|-----------|-----|
| Paste ShareX / nomacs / Shotik / MCP-server code | Golden Rule 5 |
| Downloader Start/Pause queue on Capture | Not queued work |
| nomacs plugin-menu IA | Tools on the canvas |
| Python `keyboard` / native hotkey hooks | Electron owns F2 |
| Second MCP transport in Electron | Thin REST wrapper |
| STI `jobs` table | Phase 1 |
| PNG bytes in SQLite | Pointers only |
| Overwrite original PNG on annotate | Spec |
| Upload / YouTube write | Project context |
| SSE | Poll + watcher |
| Implement under MEU-1–33 | This phase only |
| Start Session 8c (MEU-27) | Human-gated |
| Paste ShareX C# (GPL-3.0) into Electron/Python | Read the map below; rewrite |

---

## ShareX source map (read, rewrite)

> **Human-approved 2026-08-26** USER_EXPLICIT: pin the ShareX files that encode the F2 region → save-to-folder flow so implementors rewrite them against this FIC.
>
> Repo: [ShareX/ShareX](https://github.com/ShareX/ShareX) (`develop`). License **GPL-3.0**. Reading for control flow is allowed. **Pasting or translating C# into av-kit is forbidden** (Golden Rule 5). av-kit stays MIT-shaped Electron + FastAPI; the region select **and** the grab are `avkit-region-picker.exe` (WinForms + GDI `BitBlt`), Electron registers the result, persist is `POST /captures`.

ShareX sequence we re-implement (shape only). **F2 analog is `RectangleLight`, not `RectangleRegion`.** Default `RectangleRegion` opens `RegionCaptureForm` + `ShapeManager` (in-overlay arrows/text) — that is deferred; annotation is the Capture page / MCP.

```
HotkeyManager
  → TaskHelpers.ExecuteJob(HotkeyType.RectangleLight)
    → new CaptureRegion(RegionCaptureType.Light).Capture(...)
      → freeze bitmap + RegionCaptureLightForm (drag rect, Esc)
        → crop / GetAreaImage
          → AfterCaptureTasks.SaveImageToFile
```

av-kit sequence (locked elsewhere in this file):

```
Electron globalShortcut(F2)
  → spawn avkit-region-picker.exe on the display under the cursor
    → drag rect → crop PNG → write inbox
      → POST /captures  source=hotkey
```

| Step | ShareX file | Steal (logic only) | Skip | av-kit home |
|------|-------------|--------------------|------|-------------|
| Global hotkey | [`ShareX/HotkeyManager.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX/HotkeyManager.cs) | Register / unregister; fire one job on key | WinForms message-loop host | Electron `globalShortcut`; setting `capture.hotkey` |
| Tray / lifetime | [`ShareX/Forms/MainForm.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX/Forms/MainForm.cs) | Hidden host so the hotkey stays alive while the main UI is closed | Avalonia/WinForms dual UI | Tray + close-to-tray |
| Hotkey → region job | [`ShareX/TaskHelpers.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX/TaskHelpers.cs) (`HotkeyType.RectangleLight` → `new CaptureRegion(RegionCaptureType.Light).Capture(...)`) | Dispatch: one hotkey = light region picker | Full `HotkeyType` enum (window, GIF, upload, OCR, default `RectangleRegion`) | Main: F2 / `capture-region` IPC → spawn the helper |
| Capture job class | [`ShareX/CaptureHelpers/CaptureRegion.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX/CaptureHelpers/CaptureRegion.cs) | `RegionCaptureType.Light` → `RegionCaptureLightForm`; cancel if dialog ≠ OK | `Default` (full editor), `Transparent`, Avalonia path | Helper selects + crops, then `POST /captures` |
| Overlay helpers (skip Default) | [`ShareX.ScreenCaptureLib/RegionCaptureTasks.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/RegionCaptureTasks.cs) | Light/transparent helpers return a rect; empty = cancel | `GetRegionImage` / `GetRectangleRegion` (those construct `RegionCaptureForm`) | Helper `RegionForm`; Esc = cancel |
| **Closest overlay to MVP** | [`ShareX.ScreenCaptureLib/Forms/RegionCaptureLightForm.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Forms/RegionCaptureLightForm.cs) | Freeze-frame brush, drag rect, min size (~5 px; we lock **8 px**), Esc, `ShowInTaskbar = false`, optional lock cursor to active monitor | Its GDI pen palette and cursor-locking options | The helper’s `RegionForm` (this is the analog — **no annotation toolbar**) |
| Full overlay | [`ShareX.ScreenCaptureLib/Forms/RegionCaptureForm.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Forms/RegionCaptureForm.cs) | — | Entire file for MVP | Deferred |
| In-overlay shapes | [`ShareX.ScreenCaptureLib/Shapes/ShapeManager.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/ShapeManager.cs) | — | Arrows/text **on the snip** | Capture page / MCP `annotate` |
| Bitmap grab | [`ShareX.ScreenCaptureLib/Screenshot.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Screenshot.cs) (`CaptureRectangle`, `CaptureActiveMonitor`) | Crop to selected rect; reject 0×0 | GDI `BitBlt` / `CaptureBlt`, cursor/shadow/taskbar hide | Helper `ScreenCaptureSource` (`BitBlt` + `CAPTUREBLT`) then crop; Python `mss` for MCP bbox |
| Cursor’s monitor | [`ShareX.HelpersLib/Helpers/CaptureHelpers.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX.HelpersLib/Helpers/CaptureHelpers.cs) (`GetActiveScreenBounds` = `Screen.FromPoint(cursor)`) | Picker + grab on the display under the cursor, not the virtual desktop stitch | `GetScreenBounds2/3/4` experiments | Spec: display under cursor |
| After-capture save | `TaskHelpers` `GetScreenshotsFolder` / `SaveImageAsFile`; flag `SaveImageToFile` in [`ShareX/Enums.cs`](https://github.com/ShareX/ShareX/blob/develop/ShareX/Enums.cs) (`AfterCaptureTasks`) | Confirm → write PNG to inbox; no upload | `ShowAfterCaptureWindow`, uploaders, OCR, `PerformActions`, `AfterUploadTasks`, filename `%mo-%d-%y` token parser | Timestamp `{yyyy-MM-dd_HH-mm-ss}.png` + `POST /captures` `mode=register` |

**Read first for MEU-40 (native region picker):** `CaptureRegion.cs` (`RegionCaptureType.Light` only) + `RegionCaptureLightForm.cs` + `CaptureHelpers.GetActiveScreenBounds`.

**Read first for MEU-39 (hotkey/tray):** `HotkeyManager.cs` + `MainForm.cs` tray lifetime + `TaskHelpers` `RectangleLight` case only.

**Do not open for MVP implementation:** `ShapeManager`, `ScrollingCaptureManager`, `UploadersLib`, `RegionCaptureForm` editor modes, `CaptureWindow` / `CaptureFullscreen` / `CaptureLastRegion` GUI buttons, `HotkeyType.RectangleRegion` (full editor).

---

## Validation commands

Registered receipts in [`.agent/docs/commands.md`](../../.agent/docs/commands.md). Per-MEU: scoped pytest/pyright/ruff or vitest/tsc/eslint as the touched package requires. Phase gate (full repo) only when exiting a later ship train — not as the MEU-34 unit gate.
