---
project: "2026-11-08-capture-region-import"
date: "2026-11-08"
source: ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md#session-58--capture-region-import-meu-128-meu-129--p2"
grouping_source: ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md"
meus: ["MEU-128", "MEU-129"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: An agent looks closer at a capture and brings in any image (Session 58)

> **Project:** `2026-11-08-capture-region-import`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Residuals registered 2026-11-08 (`:978`): §Region view (`:984-997`, anchor `region-view`, MEU-128) and §Image import (`:1001-1015`, anchor `image-import`, MEU-129).
>
> **Source request.** Mat asked on 2026-11-08 for a crop feature on the capture page that agents can use through the GUI, MCP and API, on screenshots or any other image, agent use first (`_inspiration/capture-crop/design.md`, design D-2). Mat ruled design D-1 ("New shot (copy); source untouched") and then asked: "create new session grouping and start the first create plan from it". The grouping (D-400 to D-406) puts the design's slices S1 and S3 here. Done comes from 09's two contracts, not from Mat's words: "A region of a shot comes back cut from the full-resolution image, fitted inside `max_edge`, with its frame reported, and nothing is written; without the new fields the bytes are today's. A local image becomes a new shot with source `Import` that `image`, `annotate` and the later crop work on, and its source file is never changed."
> **Known issues:** none open for these MEUs. Row 6 files `CAPTURE-EXIF-SCANNED-ORIENTATION` (D-424), which 09 `:1014`'s planning check found.
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
>
> Line anchors are from `main` `2963efe`, read 2026-11-08, except the Stage A files, which were uncommitted when read and are committed unchanged in `75617379`: `09-screenshot-capture.md` `:978-1050`, `build-priority-matrix.md`, `BUILD_PLAN.md`, `meu-registry.md`, `meu-status.yaml` `:3347-3400` and the crop grouping. Session 55 was committed after they were read, as `f69ee08`. The anchors this plan cites in files that commit changed (`tests/unit/test_domain.py:298-305`, `meu-status.yaml` `:3347` and `:3374`, the register's SHA-256) were read again at `f69ee08` and hold.

## Goal

**Goal anchor:** Session 58 lets an agent look at any part of a capture at full resolution and bring any local image into the capture inbox. `GET /captures/{id}/image` and MCP `image` take an optional region in original pixels or in fractions rounded outward. The region is clamped to the image and fitted inside `max_edge` (default 1568, at most 4× up) with Lanczos resampling. No file is written. The frame is reported in five response headers and, through MCP, in a text item before the image. `POST /captures` with `mode: import`, and MCP `capture` with `mode: import`, copy a local png, jpg, jpeg or webp into the inbox root as a new shot with source `Import`. An EXIF-rotated image is written as an upright PNG. A file already in the inbox root registers in place, and the source file is never changed.

Four things are missing today:

1. **An agent can only fetch the whole image.** `GET /captures/{id}/image` takes `variant` only (`packages/api/src/avkit_api/routes/captures.py:257-260`), and MCP forwards only `variant` and `status` as query keys (`mcp-server/src/toolsets/capture.ts:19`). A vision model resizes an image whose long edge is over its limit: 1568 px on the standard tier, and 2576 px on the high-resolution tier that Claude 4.7 and later models use (design R-1, refreshed for D-426). So a detail in a 4K screenshot reaches the agent at about 40% or 67% of its size. The design found that agents crop mostly to look closer and then throw the file away (design §4).
2. **A shot over 7,800,000 B can't be seen through MCP at all.** `registry.ts:351-356` refuses it and sends the agent to the file path, and 05 `:318` left "a downscaled preview can come later".
3. **A file outside the inbox can't become a shot.** `register_shot` (`packages/core/src/avkit_core/services/capture.py:406`) accepts only inbox paths (`_require_inbox_file`, `:827`), so an agent must copy the file in by hand and then list.
4. **No source value marks an imported shot.** `CaptureSource` stops at `Scan` (`packages/core/src/avkit_core/domain/enums.py:209-217`).

The session ends when the contract's tests and 09's two contracts hold, the session gate passes, `CAPTURE-EXIF-SCANNED-ORIENTATION` is filed, and both MEUs are `approved`.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-08). No payload is oversized: each layer's change is read directly, and the largest file, services/capture.py, was read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s58-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s58\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s58-plan-canonical-2026-11-08-capture-region-import` and `s58-execution-2026-11-08-capture-region-import`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290).
  - Reviewer prompts name the ledger vocabulary up front: D-407 to D-427, AC-128.1 to AC-128.24, AC-129.1 to AC-129.13, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json` and anything under `.agent/fleet/hub`. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, or an `approved` verdict authored by the implementer. Capture stays local: no test or row uploads an image or reads one from the network. Tests build their images with Pillow under `tmp_path`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-128 `capture-region-view` | `.agent/context/handoffs/2026-11-08-capture-region-import-MEU-128-handoff.md` |
| MEU-129 `capture-image-import` | `.agent/context/handoffs/2026-11-08-capture-region-import-MEU-129-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-08-capture-region-import-plan-critical-review.md` and `.agent/context/handoffs/2026-11-08-capture-region-import-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts |
| WP-2 | Type-only names (row 1) | WP-1 | shared | `ViewFrame`, the region stubs, the port's `view` stub, with no behaviour |
| WP-3 | MEU-128 Red, then Green (rows 2, 3) | WP-2 | shared | `REGION_RESOLVE`, `REGION_ERRORS`, `VIEW_SCALE`, `VIEW_FORMAT`, `RETURN_UNCHANGED`, `FRAME_HEADERS`, `FRAME_ITEM`, `QUERY_GET_ONLY`, `OVERSIZE_HINT` |
| WP-4 | MEU-129 Red, then Green (rows 4, 5) | WP-3 | shared | `IMPORT_MODE`, `IMPORT_ACCEPT`, `IMPORT_COPY`, `IMPORT_UPRIGHT`, `IMPORT_IN_PLACE`, `IMPORT_NAME`, `IMPORT_SOURCE` |
| WP-5 | Records (row 6) | WP-4 | shared | Spec notes, MEU status, the filed issue, renders, grouping tracker |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Two handoffs, review, reflection, Session 59's prompt |

Split flag (grouping `:68`): if MEU-128's Green (row 3) leaves the session past about half its context, rows 4 and 5 run as Session 58b from this same plan and task, with no plan change.

## User Review Required

> [!IMPORTANT]
> **Mat ruled all three questions on 2026-11-08, each as recommended** ("all recommendations accepted"; `human-gate-decision.md`, refreshed that day at Mat's request):
> - **D-425, the import size cap** (`governance-value`). Ruled: 50 MB, the design's starting point. The alternatives were 15 MiB, so every byte-copied original can be read back through `GET image` without a region (an upright PNG made from a rotated JPEG can still be larger), and do nothing, which leaves only Pillow's pixel guard. No av-kit cap on incoming files exists to follow.
> - **D-426, the view defaults** (`governance-value`; `max_edge` 1568 by default, 64 to 2576, upscale at most 4×). Ruled: as the design has them. Current Claude models keep up to 2576 px, so 1568 is a cost choice: a default view costs at most 3,136 visual tokens, and an agent passes 2576 for more. The alternatives were a 2576 default; the limits a 2026 zoom study measured (a 1024 default and at most 2×, arXiv 2610.09313); and do nothing, which scales only when the caller passes `max_edge`. The reading probe the design proposed, a model reading small text at each size, was not run.
> - **D-427, committing the crop docs before execution** (`two-way`, a hard gate). Ruled: one exact-scope docs commit of Stage A's seven files now, without this folder, the review handoff or a push (precedent D-276, `83229ea`). The alternatives were the same commit just before row 0, and do nothing, which leaves them to H2-5.
>
> Every other choice is recorded as autonomous in §Decision Log (D-407 to D-424), with its alternatives. With D-425, D-426 and D-427 ruled, the gate still asks Mat to accept the plan or override one of the others, and only Mat's words start execution.
>
> **The queue (S8).** Row 0 refuses to start until Session 55 is committed (a subject ending `(MEU-124)` among the last 40 commits, which `f69ee08` meets, and none of its paths dirty) and Session 57 (MEU-125, rc.2) is `approved`. Grouping D-405 put the crop sessions after rc.2. Only Mat's words waive that, through `baseline.ps1 -QueueWaived`.
>
> **The crop docs are committed** (D-427, ruled by Mat on 2026-11-08). `75617379` holds Stage A's edits (`09-screenshot-capture.md`, `build-priority-matrix.md`, `BUILD_PLAN.md`, `meu-registry.md`, `meu-status.yaml`), the crop grouping and `_inspiration/capture-crop/design.md`, and Mat had it pushed separately on 2026-11-08. Row 0 finds them clean, and rows 6 and H1-2 still check their SHA-256 before writing on top of them (S3), which pass, because a commit doesn't change a file. If one of them is dirty again at row 0, `baseline-dirty.txt` records it, and the H2-5 commit message names it.
>
> **What the words in the contract mean here, and the limits they leave.**
> - **A frame is always the original's pixels** (`get`'s `width` and `height`). A fraction is of the original's width and height, never of a returned view. A view's own pixels map back through `source_x = region.x + x / scale`.
> - **Fractions round outward, with a 9-place guard** (D-408). `0.1 + 0.2` of 1000 px is 300, not 301, and `0.29` of 100 px starts at 29, not 28 (`C:/Temp/av-kit/s58-plan-probes.txt`).
> - **A region is upscaled at most 4×.** A 100×50 region returns 400×200, not 1568×784. `max_edge` without a region only shrinks.
> - **Without the new fields, the body is today's,** and five headers are added. Their size comes from the row as the last list saw it. A file replaced since then reports the old size until a list runs. A region view reads the file and refuses a mismatch with 409.
> - **A view keeps the file's format.** JPEG and WebP are re-encoded at quality 90 (`LOSSY_QUALITY`), so a lossless WebP comes back lossy when it is cut or scaled.
> - **A view and `annotate` read the stored frame.** A scanned JPEG with EXIF orientation 5 to 8 is sized and marked sideways, as today. Row 6 files that as `CAPTURE-EXIF-SCANNED-ORIENTATION` (D-424). Import writes such a file upright, so an imported one is right.
> - **An import copies; it never moves or watches the source.** A byte copy keeps the file's metadata, and an upright PNG drops it. An inbox-root file registers in place and keeps the source its row already has.
> - **MCP sends the frame item only when the API sent all five headers.** A fake API without them gets the image alone, as today, so the existing tests stay as they are (D-412).
>
> **The token estimate,** calibrated against Session 54 (one service and API MEU; plan 8,541,302 tokens in 1 round, execution 7,859,970) and Session 44's MEU-111 part (the MCP image cap this MEU extends). This session has two MEUs through the domain, adapter, service, API, OpenAPI and MCP layers, with 37 ACs. Expect 1 to 2 plan rounds (about 8M to 15M) and 1 to 2 execution rounds (about 9M to 16M). The plan loop opens with the default 10.5M. If round 1 costs more than 5.25M, the gate asks Mat for the execution loop's budget (Session 52 RULE-3). The citable AC families are fixed when the plan loop opens: AC-128 and AC-129.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `REGION_RESOLVE` | `resolve_region(source_width, source_height, x, y, width, height, unit)` in `domain/capture.py` returns `(left, top, width, height, clamped)` in original px. With `px`, each value becomes a Python `int` before any sum: `right = int(x) + int(width)` and `bottom = int(y) + int(height)`, which stay exact for any finite value. With `fraction`, `left = floor(round(x·W, 9))`, `top = floor(round(y·H, 9))`, `right = ceil(round((x+width)·W, 9))` and `bottom = ceil(round((y+height)·H, 9))`. Then `right` and `bottom` are clamped to `W` and `H`, and `clamped` is whether either moved. |
| `REGION_ERRORS` | `view_frame` and `resolve_region` raise `ValidationError` (422) with the fixed, path-free messages in §Region view: domain, in the order given there. |
| `VIEW_SCALE` | With a region, `scale = min(max_edge / max(rw, rh), 4)`, with `max_edge` 1568 by default. With `max_edge` and no region, `scale = min(1, max_edge / max(W, H))`. Each returned edge is `max(1, floor(r·scale + 0.5))`. With neither, the frame is the whole image at scale 1. |
| `VIEW_FORMAT` | `CaptureAdapter.view(path, frame)` checks the file's size against the frame's source size, crops, resizes with `Image.LANCZOS`, and encodes in memory in the path's format: PNG; JPEG at `LOSSY_QUALITY`, always RGB; WebP at `LOSSY_QUALITY`. A palette image is converted to RGB, or RGBA when it has transparency, before the resize. It never calls `exif_transpose` and never writes a file. |
| `RETURN_UNCHANGED` | A frame that is the whole image at scale 1 returns `path.read_bytes()` unchanged. |
| `FRAME_HEADERS` | Every 200 from `GET /captures/{id}/image` carries `X-Capture-Source` (`W,H`), `X-Capture-Region` (`x,y,width,height`), `X-Capture-Returned` (`w,h`), `X-Capture-Scale` (`%.6f`) and `X-Capture-Clamped` (`true` or `false`). They are documented in the route's `responses` for 200. |
| `FRAME_ITEM` | MCP `image` returns a text item and then the image when all five headers parse. The text is JSON: `frame` holds `source`, `region`, `returned`, `scale` and `clamped`, and `map` holds `source_x = region.x + x / scale; source_y = region.y + y / scale`. Otherwise it returns the image alone, as today. |
| `QUERY_GET_ONLY` | `registry.ts` appends `GET_QUERY_KEYS` to the path only for a `GET` row. `GET_QUERY_KEYS` gains `x`, `y`, `width`, `height`, `unit` and `max_edge`. |
| `OVERSIZE_HINT` | The API's 413 detail and MCP's `payload_too_large` message name `max_edge (64 to 2576)` and a region as the way to get a smaller image. The caps stay 15 MiB and 7,800,000 B. |
| `IMPORT_MODE` | `POST /captures` takes `CaptureImportIn` (`mode: "import"`, `path`, `extra="forbid"`) and returns 201 with the shot. MCP `capture` takes `mode: "import"` with `path`, `.strict()`. |
| `IMPORT_ACCEPT` | `CaptureService.import_image(path)` checks, in this order: absolute; exists; a regular file; suffix in `SCAN_EXTENSIONS`; size at most `IMPORT_MAX_BYTES`; not an annotated copy in the inbox root; readable; `inspect_import` decodes the bytes in full and accepts them. Each refusal is a fixed message that names no path, and nothing is written until every check passes. |
| `IMPORT_COPY` | An accepted file outside the inbox root is copied into the inbox root under `CAPTURE_FILE_LOCK`: written to `NAME.avkit-tmp`, moved with `os.replace`, probed and registered. Any exception from the first write through the unit of work's commit removes the temporary file and, once `os.replace` has run, the copy; commits no row; and raises `CaptureFailedError` (503). It removes no file this import didn't write. The source file is only read. |
| `IMPORT_UPRIGHT` | EXIF orientation 1, or no tag: a byte copy. Orientations 2 to 8: an upright PNG through `exif_transpose`, written by `write_upright_png`. |
| `IMPORT_IN_PLACE` | A file in the inbox root registers in place: an existing row is returned with its source unchanged and its size refreshed; a file with no row gets a row with source `Import`. Nothing is copied, rotated or removed. A `probe` failure raises the fixed `InboxPathError("the image could not be opened")` (422). |
| `IMPORT_NAME` | The copy's name is the source stem with each run of characters other than letters, digits, `_`, `-` and space replaced by `_`, stripped of ` _-`, cut to 100 characters, `import` if empty, `import_` before a Windows reserved name; then the lowercased suffix, or `.png` when rotated; then `_2`, `_3` … until neither a file in the inbox root nor a row, stale rows included, holds the name, compared with `casefold()`. |
| `IMPORT_SOURCE` | `CaptureSource.Import = "Import"`, after `Scan`. The API reports `"Import"`. No wire map or migration changes. |
| `NO_RAW_CONSOLE` | No new log line is added. The only lines an import or view reaches are the existing `capture.registered` (`shot_id`, `source`) and, for an upright PNG, `capture.wrote`, whose `path` field the Console processor drops. No refusal message names a path, and no `probe` message, which does (`adapter.py:256`, `:262`), reaches a response. |

### Region view: domain (D-407, D-408, D-409)

`packages/core/src/avkit_core/domain/capture.py` (CRLF) gains, next to `CAPTURE_MIN_EDGE_PX` (`:25`):

```python
REGION_MAX_EDGE_DEFAULT = 1568
REGION_MAX_EDGE_MIN = 64
REGION_MAX_EDGE_MAX = 2576
REGION_UPSCALE_MAX = 4
```

and, after `BBox` (`:96`), a frozen dataclass in `BBox`'s style:

```python
@dataclass(frozen=True)
class ViewFrame:
    """The frame of a region view (MEU-128): source size, applied region, returned size."""

    source_width: int
    source_height: int
    x: int
    y: int
    width: int
    height: int
    returned_width: int
    returned_height: int
    scale: float
    clamped: bool
```

Its fields are plain ints, not a `BBox`: a whole-image frame of a 6 px image isn't a valid `BBox` (`CAPTURE_MIN_EDGE_PX`), and the frame describes what was done, not a request. Then three functions, all added to `__all__` (`:340`):

- `resolve_region(source_width, source_height, x, y, width, height, unit) -> tuple[int, int, int, int, bool]`: `REGION_RESOLVE`, and the value checks of `REGION_ERRORS`.
- `view_scale(width, height, max_edge, *, upscale) -> float`: `min(max_edge / max(width, height), REGION_UPSCALE_MAX if upscale else 1)`.
- `view_frame(source_width, source_height, *, x=None, y=None, width=None, height=None, unit=None, max_edge=None) -> ViewFrame`: the field checks, then `resolve_region` when a region is given, then `view_scale`, then the returned size.

The resolver, after the value checks:

```python
if unit == "px":
    left, top = int(x), int(y)
    right, bottom = left + int(width), top + int(height)
else:
    left = math.floor(round(x * source_width, 9))
    top = math.floor(round(y * source_height, 9))
    right = math.ceil(round((x + width) * source_width, 9))
    bottom = math.ceil(round((y + height) * source_height, 9))
if left >= source_width or top >= source_height:
    raise ValidationError(f"region starts outside the image, which is {source_width}x{source_height} px")
clamped = right > source_width or bottom > source_height
right, bottom = min(right, source_width), min(bottom, source_height)
```

`REGION_ERRORS`, checked in this order (the first four in `view_frame`, the rest in `resolve_region`):

| Case | Message |
|---|---|
| Some of `x`, `y`, `width`, `height`, not all four | `x, y, width and height go together: give all four or none` |
| `unit` with no region | `unit needs x, y, width and height` |
| `max_edge` outside 64 to 2576 | `max_edge must be between 64 and 2576` |
| A value is `nan` or infinite | `x, y, width and height must be finite numbers` |
| `x` or `y` below 0 | `x and y must be 0 or more` |
| `width` or `height` 0 or below | `width and height must be more than 0` |
| `px` and a value isn't whole | `with unit px, x, y, width and height are whole pixels; use unit: "fraction" for parts of the image` |
| `fraction` and a value is above 1 | `with unit fraction, x, y, width and height are between 0 and 1` |
| The region starts at or past the right or bottom edge | `region starts outside the image, which is WxH px` |
| An edge under `CAPTURE_MIN_EDGE_PX` after clamping | `region is wxh px after clamping to the image; each edge must be at least 8 px` |

`unit` defaults to `px` when a region is given. The finite check comes first because Pydantic's `float` accepts `nan` and `inf` from a query string. The 9-place guard (D-408) moves a product by at most 5e-10, so it changes a `floor` or `ceil` only for a product that close to a whole number; for a fraction sent as JSON that gap is binary error, not part of a pixel. In `px`, adding `int`s keeps `right` and `bottom` finite, so `x` and `width` of `1e308` give the "region starts outside" message, not an `OverflowError` from `int(x + width)` (`C:/Temp/av-kit/s58-corrections-verify.txt`).

### Region view: adapter, service and route (D-410, D-411)

- **`packages/core/src/avkit_core/ports/capture.py` (CRLF).** `ImageAnnotatePort` (`:18-33`) gains `view(self, path: Path, frame: ViewFrame) -> bytes`. Row 5 adds `inspect_import` and `write_upright_png` (§Image import).
- **`packages/infrastructure/src/avkit_infra/capture/adapter.py` (CRLF).** `CaptureAdapter.view`:
  1. Opens the file. An open or decode failure raises `InboxPathError("the image could not be opened")`, which names no path. Without this, an `UnidentifiedImageError` would reach `api.unhandled_error`, whose `error` field holds the path and is a Console field.
  2. If `image.size != (frame.source_width, frame.source_height)`, it raises `ConflictError("the image file changed since the captures were listed; list them again and retry")` (409).
  3. `RETURN_UNCHANGED`: a frame of `(0, 0, W, H)` at scale 1 returns `path.read_bytes()`.
  4. Converts a `P` or `PA` image first, to RGBA when it has alpha or a `transparency` entry and to RGB otherwise, because Pillow resizes a palette image with NEAREST whatever filter it is given. Then crops to the region and resizes to the returned size with `Image.LANCZOS`.
  5. Encodes by `path.suffix.lower()`: `.png` keeps the mode (RGBA, RGB, L or LA); `.jpg` and `.jpeg` save RGB JPEG at `LOSSY_QUALITY` (`:52`); `.webp` saves WebP at `LOSSY_QUALITY`, RGBA when the image has alpha. It writes to a `BytesIO`, never to disk.
- **`services/capture.py` (CRLF).** `read_image_view(shot_id, variant, *, x, y, width, height, unit, max_edge) -> tuple[bytes, ViewFrame]`. It gets the shot and resolves the variant's file with `read_image`'s own `NotFoundError`s (`:556-567`). Then it builds the frame with `view_frame(shot.width, shot.height, …)` and returns `self._annotate.view(path, frame)` with the frame. It takes no lock, as `read_image` takes none. The annotated copy is baked at the original's size (`adapter.py:265-286`), so one frame serves both variants.
- **`packages/api/src/avkit_api/routes/captures.py` (CRLF).** `get_capture_image` (`:257-274`) gains six query parameters: `x`, `y`, `width` and `height` as `float | None`, `unit` as `Literal["px", "fraction"] | None`, and `max_edge` as `int | None`. None of them has a `ge` or `le`, because the domain's messages are the contract and FastAPI's would replace them.
  - With all six unset, it keeps `get_shot` and `read_image`, and the headers come from `shot.width` and `shot.height`: region `0,0,W,H`, scale `1.000000`, clamped `false`.
  - With any of them set, it calls `read_image_view` and builds the headers from the frame.
  - The 413 check covers both paths: `image exceeds IMAGE_MAX_BYTES; pass max_edge (64 to 2576) or a region for a smaller image`. `IMAGE_MAX_BYTES` stays 15,728,640 (`:48`).
  - `responses={200: {"headers": …}}` documents the five headers. `routes/tts.py:62-67` and `routes/models.py:77` already pass `responses=`, for a 409; no route documents a response header yet, so this is the first. The `X-` names follow `X-Request-ID` (`packages/api/src/avkit_api/errors.py:50`).
  - The media type stays `_image_media_type(media_path)` (`:179`), because a view keeps the file's format.

CORS needs no `expose_headers`: the MCP server reads the headers from Node's `fetch`, which CORS doesn't limit, and the renderer doesn't read them.

### Region view: MCP (D-412, D-413)

- **`mcp-server/src/toolsets/capture.ts` (CRLF).** `GET_QUERY_KEYS` (`:19`) gains `x`, `y`, `width`, `height`, `unit` and `max_edge`. The `image` member gains `x` and `y` (`z.number().nonnegative()`), `width` and `height` (`z.number().positive()`), `unit` (`z.enum(["px", "fraction"])`) and `max_edge` (`z.number().int().min(64).max(2576)`), all optional. The zod bounds are a first filter; the API's messages stay the contract. The `image` description gains design §6.7's text: "Optional x/y/width/height returns just that region from the full-resolution image, scaled to fit max_edge (default 1568; pass 2576 for high-resolution vision). Writes no file. Coordinates are original pixels, or unit: "fraction" (0–1) when you read them off a scaled view. The first content item gives the frame: source px = region.x + x / scale." `desc()` (`:21-28`) keeps the M7 markers.
- **`registry.ts` (CRLF).** `QUERY_GET_ONLY`: `:335` becomes `const path = row.method === "GET" ? withQuery(interpolatePath(row.path, record), record) : interpolatePath(row.path, record);`. Today `withQuery` runs for every method, so once `x`, `y`, `width` and `height` are query keys, a POST `capture` region would send them twice. AC-128.19 guards that. The image branch (`:342-363`):
  - keeps the size check first, and its message gains `, or pass max_edge (64 to 2576) or x, y, width and height for a smaller image` (`OVERSIZE_HINT`);
  - parses the five headers from `binary.captureHeaders`. If all five parse, it returns the frame text item and then the image; otherwise the image alone.
- **`mcp-server/src/client.ts` (LF).** `ApiBinaryOk` (`:157`) gains `captureHeaders: Record<string, string>`, and `apiBinary`'s ok branch (`:193-250`) fills it with every response header whose name starts with `x-capture-`, lowercased.

The live audit and the stdio test find the image with `content.find` (`scripts/audit/client.ts:116`, `tests/image-over-stdio.test.ts:71`), so a text item first breaks neither. `ACTION_INDEX` stays at 70 rows, and `avkit_capture` keeps its 10 actions (AC-38.2).

### Image import (D-414 to D-420)

- **`domain/enums.py` (CRLF).** `CaptureSource` (`:209-217`) gains `Import = "Import"` after `Scan`. No migration: the column stores `.name`, as for the others (09 `:282`). No `REGISTER_SOURCE_WIRE_MAP` entry: import doesn't go through `register`.
- **`schemas/captures.py` (CRLF).** `CaptureImportIn(BaseModel)` with `model_config = ConfigDict(extra="forbid")`, `mode: Literal["import"]` and `path: str`, joins the `CaptureCreateIn` union (`:50-53`).
- **`routes/captures.py`.** `create_capture`'s chain (`:196-205`) gains `elif isinstance(body, CaptureImportIn): shot = capture.import_image(Path(body.path))`, and returns 201 as the others do.
- **`services/capture.py`.** `IMPORT_MAX_BYTES = 50_000_000` beside `SCAN_EXTENSIONS` (`:54`), as Mat ruled under D-425. `import_image(path) -> CaptureShot`:

  1. `IMPORT_ACCEPT`, with these messages:

     | Case | Error | Message |
     |---|---|---|
     | Not absolute | `InboxPathError` | `path must be absolute` |
     | Missing | `InboxPathError` | `no file at that path` |
     | Not a regular file | `InboxPathError` | `path is not a regular file` |
     | Suffix not in `SCAN_EXTENSIONS` | `InboxPathError` | `not an image av-kit can open (png, jpg, jpeg, webp)` |
     | Over the cap | `InboxPathError` | `file is N MB; the import limit is L MB`, with N = `ceil(size / 1e6)` and L = `IMPORT_MAX_BYTES // 1_000_000` read at call time (50 by default) |
     | An annotated copy in the inbox root | `InboxPathError` | `this file is an annotated copy; import its original instead` |
     | Read fails | `InboxPathError` | `the file could not be read` |
     | Pillow can't open, verify or fully decode it | `ValidationError` | `not an image av-kit can open (png, jpg, jpeg, webp)` |
     | Over the pixel limit | `ValidationError` | `image is larger than the 89478485-pixel limit` |

     Both errors are 422. The service doesn't call `probe` or `_require_inbox_file` for these checks, because their messages name the path (`adapter.py:256`, `:262`).
  2. `inspect_import(data) -> int` (the adapter) returns the EXIF orientation, 1 when there is no tag.
  3. Under `CAPTURE_FILE_LOCK` (`:67-70`, not reentrant), with one unit of work:
     - **`IMPORT_IN_PLACE`.** If the resolved file is directly in the inbox root, an existing row is returned with its source kept, and `width`, `height` and `file_size` refreshed with `replace` when the size changed. With no row, it probes and calls `_upsert_shot(…, CaptureSource.Import)`.
     - **`IMPORT_COPY`.** Otherwise `ensure_dir(inbox)`, then the name (`IMPORT_NAME`), then the temporary file `dest.with_name(dest.name + ".avkit-tmp")`. Orientation 1: `write_bytes(data)`. Orientations 2 to 8: `write_upright_png(data, tmp)`. Then `os.replace(tmp, dest)`, `probe(dest)` and `_upsert_shot(…, CaptureSource.Import)`.
     - The copy branch's `try` encloses its whole unit of work, so it covers the write, `os.replace`, `probe(dest)`, `_upsert_shot` and the commit that runs in the unit of work's `__exit__` (`packages/infrastructure/src/avkit_infra/database/unit_of_work.py:54-65`). Its `except Exception`, like `convert`'s (`:715-717`), removes the temporary file with `_unlink_if_file` and, once `os.replace` has run, the copy; no row commits; and it raises `CaptureFailedError("the import could not be written")` (503, unlogged, `internal_error`). So `probe`'s `InboxPathError`, whose message names the path, never reaches the response, and no copy is left for the next scan to fail on.
     - In the in-place branch, an `InboxPathError` from `probe` becomes `InboxPathError("the image could not be opened")` (422), and the user's file is never removed.
- **`adapter.py`.** `inspect_import(data: bytes) -> int` opens `BytesIO(data)` inside `warnings.catch_warnings()` with `warnings.simplefilter("error", Image.DecompressionBombWarning)`. It refuses `w·h > Image.MAX_IMAGE_PIXELS` (89,478,485) explicitly, because Pillow only warns between 1× and 2× the limit. Inside that guard it runs `verify()`, then reopens the bytes and calls `load()`, which decodes every pixel: `verify()` alone passed a 400×300 JPEG cut to half its length (`C:/Temp/av-kit/s58-corrections-verify.txt`). It reads EXIF tag `0x0112` from the reopened image and returns it. `DecompressionBombWarning` and `DecompressionBombError`, which `Image.open` raises for AC-129.8's two oversize PNGs (`C:/Temp/av-kit/s58-corrections-verify3.txt`), give the pixel-limit message. Any other exception from opening, `verify()` or `load()` gives the generic `ValidationError`, through `except Exception` as `grab` does (`:318-321`), because Pillow raises more than `OSError`: a damaged PNG `IDAT` raises `SyntaxError` (`C:/Temp/av-kit/s58-corrections-verify2.txt`). `write_upright_png(data, path) -> ImageProbe` opens the bytes, applies `ImageOps.exif_transpose`, converts any mode other than RGB, RGBA, L or LA to RGBA or RGB, and writes it with `_write_png` (`:358-371`).

`scan_inbox` takes `CAPTURE_FILE_LOCK` (`services/capture.py:312`), so a scan never sees a copy before its row exists. That is how 09 `:1012`'s "a scan that sees the file first does not replace it" holds. The temporary file's suffix is outside `SCAN_EXTENSIONS` too.

- **MCP `capture.ts`.** A new union member, `withDesc("capture", z.object({ action: z.literal("capture"), mode: z.literal("import"), path: z.string().min(1) }).strict())`. `httpBody` (`registry.ts:215-240`) already forwards `mode` and `path`, and the `capture` action already uses `ADD_TIMEOUT_MS`. The `capture` description gains design §6.7's sentence: "mode=import copies a local image (png, jpg, jpeg, webp; absolute path) into the capture inbox as a new shot so image, crop and annotate work on it. The source file is never changed."

### Where values go (Session 50 RULE-1, Session 53 RULE-1; D-421)

- **The region fields and the frame** are numbers. They go into the response headers and the MCP text item. They are never logged.
- **An import's `path`** is the caller's own text. No message, log line or response field repeats it. The response is the shot, whose `original_path` is the copy in the inbox.
- **The source file's stem (outside text)** becomes the copy's name and `display_name` only after `IMPORT_NAME` sanitizes it. This is Session 53 RULE-1's one target, and AC-129.4 pins it.
- **`capture.registered`** logs `shot_id` and `source` (`services/capture.py:894`) on insert only. Neither is a path.
- **`capture.wrote`** (`adapter.py:366`) logs `path`, `width` and `height` when `write_upright_png` writes. `path` isn't in `CONSOLE_FIELDS` (`packages/core/src/avkit_core/services/health.py:47-56`), so once a HealthService is built, the processor drops it before the renderer, the ring or `console.log` see it. Production builds HealthService in `build_services` before any request.
- **A 503** is answered as `internal_error` and isn't logged (`packages/api/src/avkit_api/errors.py:138-149`). A 4xx carries only the fixed message. An unhandled exception would be logged with its text, so `view` and `import_image` turn every file error into one of the messages above.
- **AC-129.11** proves the whole list through `build_services`, with HealthService built first (Session 54 RULE-2) and the D-391 reset.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | `:282` | `CaptureSource` gains `Import` |
| | `:532-538` | The `POST /captures` body table gains `import` with `path` (absolute), who: API and MCP |
| | `:577` | MCP `image` gains the region fields and `max_edge`, and the frame item |
| | `:578` | MCP `capture` gains mode `import` |
| | `:991` | Frame: the 9-place guard before `floor` and `ceil` (D-408) |
| | `:994`, `:997` | Frame report and Tests: MCP sends the frame item when the API sent all five headers, so tests that read `content[0]` from a fake without them stay unchanged (D-412) |
| | `:1007` | Request: MCP is `capture` with `mode: "import"`, not a new `import` action (D-415) |
| | `:1012` | Source: the value is `Import`, with no wire value; the scan race holds because both take `CAPTURE_FILE_LOCK`, and an in-place import keeps the row's source (D-414, D-419) |
| | `:1014` | Planning check: done as a probe, and `CAPTURE-EXIF-SCANNED-ORIENTATION` filed (D-424) |
| | after `:997` and after `:1015` | A Delivered note each, naming the mechanism ids, the ACs and this plan folder |
| `docs/build-plan/00-overview.md` | `:68` | `CaptureSource` gains `Import` |
| `docs/build-plan/05-mcp-server.md` | `:228` | Workflow gains `get` → `image` with a region, to look closer |
| | `:229` | Exception: the frame text item first; the region and `max_edge` |
| | `:318` | Above the cap: `max_edge` or a region gives a smaller image, in place of "a downscaled preview can come later" |
| | after `:229` | The design's §6.6 rows for identify and look, as a table. The crop rows wait for MEU-130 |
| | after `:330` | A Session 58 Delivered note: `OVERSIZE_HINT`, `FRAME_ITEM`, `QUERY_GET_ONLY` |

Row 6 re-reads each anchor before it writes (Session 51 RULE-3) and cites the lines as they read after rows 1 to 5. `09` and `05` are CRLF, and `00` is LF.

### MEU-128 `capture-region-view`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `GET /captures/{id}/image` query | `routes/captures.py` | `x`, `y`, `width`, `height` `float \| null`; `unit` `px \| fraction`; `max_edge` `int \| null`; the domain checks the rest | FastAPI ignores unknown query keys (unchanged) |
| Region → frame | `domain/capture.py` `view_frame`, `resolve_region` | `REGION_ERRORS` | — |
| Frame → bytes | `adapter.py` `view` | The file's size must equal the frame's source size | — |
| 200 headers | `routes/captures.py` | Five `X-Capture-*` headers | — |
| MCP `image` | `capture.ts` | x, y ≥ 0; width, height > 0; unit enum; max_edge int 64 to 2576 | `.strict()` |
| MCP query | `registry.ts` `withQuery` | `GET_QUERY_KEYS` on GET rows only | Other keys aren't sent |
| MCP result | `registry.ts` image branch | A text item and then the image when the five headers parse | — |

#### Acceptance Criteria

Pytest names are `test_ac_128_<n>_…`, and Vitest titles start `AC-128.<n>`. AC-128.1 to .5 go in `tests/unit/test_domain_capture.py`; .6 to .10 in `tests/unit/test_capture_adapter.py`; .11 to .17 in the new `tests/e2e/test_api_capture_region_import.py`; .18 to .20 and .22 to .24 in `mcp-server/tests/capture.test.ts`; .21 in `mcp-server/tests/client.test.ts`. The adapter tests build `ViewFrame` directly. The e2e tests use the real stack: `build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")`, `create_app(tokens=…, services=…, engine_dispose=…)`, a `TestClient`, and `PUT /api/v1/settings/capture` with `inbox_dir`, in AC-84.2's shape (`tests/e2e/test_api_captures.py:1009-1049`).

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-128.1 | unit | `REGION_RESOLVE`, px: `resolve_region(1000, 800, 100, 50, 200, 100, "px")` is `(100, 50, 200, 100, False)`, and `view_frame(1000, 800, x=100, y=50, width=200, height=100)` gives the same region, with `unit` defaulting to px | Local Canon: 09 `:990-991` | Yes: Red, the stub's whole image |
| AC-128.2 | unit | Fractions round outward: on 1000×800, `(0.1, 0.2, 0.3, 0.4)` is `(100, 160, 300, 320, False)`. The guard cases, x axis on a square image with `y=0`, `height=1`: W 1000 `(0.1, 0.2)` gives left 100, right 300; W 100 `(0.29, 0.5)` gives 29, 79; W 1001 `(0.1, 0.5)` gives 100, 601; W 799 `(0.1, 0.5)` gives 79, 480 | Research-backed: design D-4; D-408; `s58-plan-probes.txt` | Yes: Red, the stub |
| AC-128.3 | unit | Clamp: px `(900, 700, 300, 200)` on 1000×800 is `(900, 700, 100, 100, True)`; fraction `(0.5, 0.5, 0.7, 0.7)` is `(500, 400, 500, 400, True)`; a region inside is `clamped False` | Research-backed: design D-6; 09 `:992` | Yes: Red, the stub |
| AC-128.4 | unit | Parametrized over every `REGION_ERRORS` row (ids `partial`, `unit-alone`, `max-edge-low`, `max-edge-high`, `nan`, `inf`, `negative`, `zero-width`, `px-fraction`, `fraction-over-1`, `outside`, `px-huge`, `under-8`): `view_frame` raises `ValidationError` whose `str` equals the message, with `W` and `H` or `w` and `h` filled. `px-huge` sends `x` and `width` of `1e308` in `px` and expects the `outside` message, not an `OverflowError` | Local Canon: 09 `:991-992`; D-407 | Yes: Red, `DID NOT RAISE` |
| AC-128.5 | unit | `VIEW_SCALE`: a 100×50 region gives 400×200 at scale 4; a 4000×3000 region gives 1568×1176; `max_edge=1000` alone on 4000×3000 gives 1000×750 at 0.25; `max_edge=2576` alone on 1000×800 gives 1000×800 at 1; no fields give `(0, 0, W, H)`, returned `W×H`, scale 1, `clamped False`; a 10000×8 region at `max_edge=64` gives 64×1. The four constants equal 1568, 64, 2576 and 4 | Research-backed: design D-5 (R-1, R-4, R-5); D-409 | Yes: Red, scale 1 |
| AC-128.6 | unit | At scale 1, `view` of a 64×48 PNG with distinct pixels, frame region `(10, 8, 20, 16)` returned 20×16, decodes to exactly `image.crop((10, 8, 30, 24))` | Local Canon: 09 `:993` | Yes: Red, the whole file |
| AC-128.7 | unit | PNG: frame `(10, 8, 20, 16)` returned 80×64 decodes pixel-equal to `crop(...).resize((80, 64), Image.LANCZOS)`; a palette PNG with transparency equals the same on `convert("RGBA")`; an RGBA source keeps mode RGBA | Research-backed: design D-5 (R-5); D-410 | Yes: Red, the whole file |
| AC-128.8 | unit | A `.jpg` shot's view decodes as JPEG, mode RGB, at the returned size; a `.webp` shot's view decodes as WEBP at the returned size | Local Canon: D-410 | Yes: Red, the whole file's size |
| AC-128.9 | unit | No file is written: the folder's names, sizes and `st_mtime_ns` are the same before and after views of every kind above | Local Canon: 09 `:993` | Guard: passes in Red |
| AC-128.10 | unit | A frame whose source size is 100×80 on a 64×48 file raises `ConflictError` whose message holds no part of the path; a `.png` that holds text raises `InboxPathError("the image could not be opened")` | Local Canon: D-410 | Yes: Red, `DID NOT RAISE` |
| AC-128.11 | e2e | `RETURN_UNCHANGED` and `FRAME_HEADERS` without fields: `GET …/image` returns the file's exact bytes, today's media type, and the five headers `W,H`, `0,0,W,H`, `W,H`, `1.000000`, `false` | Local Canon: 09 `:993-994` | Yes: Red, no headers |
| AC-128.12 | e2e | A px region on a 2000×1500 PNG: default `max_edge` and `max_edge=2576` each return the headers of the frame and a body that decodes at the returned size. After `annotate` with one mark, `variant=annotated` returns the annotated file's crop | Research-backed: design D-5; 09 `:990`, `:994` | Yes: Red, the whole file |
| AC-128.13 | e2e | A fraction region past the edge returns the resolved px region in `X-Capture-Region` and `X-Capture-Clamped: true` | Research-backed: design D-4, D-6 | Yes: Red, no headers |
| AC-128.14 | e2e | `max_edge=500` alone on 2000×1000 returns 500×250 at scale `0.250000`; `max_edge=2576` alone on the same file returns its exact bytes at scale `1.000000` | Local Canon: 09 `:993` | Yes: Red, the whole file |
| AC-128.15 | e2e | 422 through the envelope: `partial`, `unit-alone`, `max-edge-low` and `outside` each return `error.code` `ValidationError` and the exact message; `unit=inch` returns `validation_error` | Local Canon: D-407 | Yes: Red, 200 |
| AC-128.16 | e2e | With the route's `IMAGE_MAX_BYTES` patched below the file's size, the 413 detail names `max_edge (64 to 2576)` on both the whole-image and the region path | Local Canon: 05 `:318`; D-411 | Yes: Red, the old detail |
| AC-128.17 | e2e | A shot's file replaced by a different size and file length: a region view returns 409 `ConflictError` with no path; after `GET /captures`, the same view returns 200 with the new `X-Capture-Source` | Local Canon: D-410 | Yes: Red, 200 with no headers |
| AC-128.18 | unit (MCP) | `image` with `x`, `y`, `width`, `height`, `unit` and `max_edge` sends each as a query key on the GET path | Local Canon: 09 `:990` | Yes: Red, zod refuses the keys |
| AC-128.19 | unit (MCP) | `capture` with `mode: "region"` and x, y, width, height sends a POST body with them and a path with no query string | Local Canon: D-413 | Guard: passes in Red |
| AC-128.20 | unit (MCP) | A fake response with the five headers gives two items: the text item, whose JSON `frame` and `map` match the headers, and then the image. The same response without `X-Capture-Scale` gives the image alone | Research-backed: design D-3 (R-4); D-412 | Yes: Red, one item |
| AC-128.21 | unit (MCP) | `apiBinary` returns `captureHeaders` holding the response's five `x-capture-*` headers, lowercased, and no other header | Local Canon: D-412 | Yes: Red, the field is absent |
| AC-128.22 | unit (MCP) | An image over `IMAGE_MAX_BYTES` returns `payload_too_large` whose message keeps today's text and adds `max_edge (64 to 2576)` | Local Canon: 09 `:995`; MEU-111 | Yes: Red, the old message |
| AC-128.23 | unit (MCP) | zod: `x: 0.25` with the other three and `unit: "fraction"` parses; `x: -1`, `width: 0`, `unit: "inch"`, `max_edge` 63, 2577 and 100.5 are each refused | Local Canon: Boundary Inventory | Yes: Red, the accept case |
| AC-128.24 | unit (MCP) | The `image` description holds `max_edge`, `2576`, `fraction` and `region.x + x / scale`, and keeps at least three M7 markers; the advertised schema lists `x`, `y`, `width`, `height`, `unit` and `max_edge` | Research-backed: design §6.7 (R-8); 09 `:996` | Yes: Red, the text is absent |

Guards that run unchanged in rows 3 and 5: AC-37.10 (`tests/e2e/test_api_captures.py:586`), whose 413 check (`:603-605`) reads only the status, AC-38.1, .2, .5, .11, .12 and .13, AC-67.17, AC-111.1 to .4, the action-index and M7 resource tests, `tests/unit/test_domain.py`, and the convert suite's 70-row index. AC-37.10 calls the route with no new field through a fake service, so it takes the unchanged path and gains only headers it doesn't read.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Fields, units and `max_edge` range | Human-approved and Research-backed | 09 `:990`; design D-2, D-5 |
| Outward rounding | Research-backed | 09 `:991`; design D-4 |
| The 9-place guard | Inferred, flagged | D-408: the probe found products that land a pixel off |
| Clamp and the 8 px minimum | Research-backed | 09 `:992`; design D-6 |
| Scale, 4× cap, Lanczos | Research-backed | 09 `:993`; design D-5 |
| Error texts | Inferred, flagged | D-407; design §6.4's style (R-8) |
| Header names and formats | Inferred, flagged | D-411: 09 `:994` names the content, not the headers |
| Frame item only with all headers | Inferred, flagged | D-412 |
| 409 on a changed file | Inferred, flagged | D-410 |
| JPEG and WebP re-encode at 90 | Local Canon | `LOSSY_QUALITY` (MEU-67) |

### MEU-129 `capture-image-import`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `POST /captures` `mode: import` | `schemas/captures.py` `CaptureImportIn` | `path: str` | `extra="forbid"` |
| `import_image(path)` | `services/capture.py` | `IMPORT_ACCEPT` | — |
| Bytes → orientation | `adapter.py` `inspect_import` | Pillow verify and a full `load()`; `w·h` ≤ 89,478,485; bomb warnings as errors; any other exception refused with the fixed message | — |
| Bytes → upright PNG | `adapter.py` `write_upright_png` | `exif_transpose`; RGB, RGBA, L or LA | — |
| `CaptureSource.Import` | `domain/enums.py` | `.name` stored and returned | — |
| MCP `capture` `mode: import` | `capture.ts` | `path: string`, at least 1 character | `.strict()` |

#### Acceptance Criteria

Pytest names are `test_ac_129_<n>_…`, and Vitest titles start `AC-129.<n>`. AC-129.1 goes in `tests/unit/test_domain_capture.py`; .2 to .11 in `tests/e2e/test_api_capture_region_import.py`; .12 and .13 in `mcp-server/tests/capture.test.ts`. Row 4 also amends the three tuples that pin `CaptureSource`: `CAPTURE_SOURCE_MEMBERS` (`tests/unit/test_domain_capture.py:18-25`), the `CaptureSource` entry in `tests/unit/test_domain.py:298-305`, and `SOURCE_OUT` (`tests/e2e/test_api_captures.py:93-100`). The first two fail by assertion in Red, as AC-129.1 does. AC-129.9 and .10 first assert `callable(getattr(service, "import_image", None))`, so a missing method prints an assertion line.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-129.1 | unit | `"Import" in CaptureSource.__members__` and it is the last member, both asserted before `CaptureSource.Import.value == "Import"` is read, so the Red is an assertion, not an `AttributeError` | Local Canon: 09 `:1012`; D-414 | Yes: Red, no member |
| AC-129.2 | e2e | `mode: import` with an extra key, and with no `path`, each return 422 `validation_error` | Local Canon: 09 `:1007` | Guard: passes in Red |
| AC-129.3 | e2e | `IMPORT_COPY`: an outside PNG returns 201 with `source` `"Import"` and an `original_path` in the inbox root whose bytes equal the source's. The source's bytes and `st_mtime_ns` are unchanged. A following `GET /captures` lists the shot once, still `Import` | Local Canon: 09 `:1008`, `:1012`; design D-9 | Yes: Red, 422 |
| AC-129.4 | e2e | `IMPORT_NAME`: importing `shot.png` twice gives `shot.png` and `shot_2.png`, and a `Shot.PNG` from another folder then gives `Shot_3.png`, because names compare with `casefold()`; a stem of `..` gives `import.png`; `a.b c#!.jpg` gives `a_b c.jpg`; `CON!.png` gives `import_CON.png`. Every source name is legal on Windows: `CON!` becomes the reserved `CON` only after sanitizing, so no test creates a device name | Local Canon: 09 `:1011`; D-420 | Yes: Red, 422 |
| AC-129.5 | e2e | `IMPORT_UPRIGHT`, parametrized over orientations 1 to 8 and no tag on a 40×30 JPEG: 1 and no tag give a byte copy named `.jpg`; 2 to 8 give a `.png` pixel-equal to `ImageOps.exif_transpose` of the source, with the row's size matching it | Research-backed: 09 `:1010`; design D-9 (R-7) | Yes: Red, 422 |
| AC-129.6 | e2e | `IMPORT_IN_PLACE`: an inbox-root file listed first (source `Scan`) imports to the same id with source `Scan`, twice; an inbox-root file with no row imports with source `Import` and no new file | Local Canon: 09 `:1008`; D-419 | Yes: Red, 422 |
| AC-129.7 | e2e | An inbox-root `x.annotated.png` returns 422 with the annotated-copy message; a file in an inbox subfolder is copied to the root | Local Canon: D-416 | Yes: Red, the generic 422 |
| AC-129.8 | e2e | Refusals, each a 422 whose message is the fixed text and holds no part of the path: relative, missing, a folder, `.gif`, text named `.png`, over the cap (with `IMPORT_MAX_BYTES` patched to 1,000,000 and a valid PNG between 1,000,001 and 2,000,000 B, giving `file is 2 MB; the import limit is 1 MB`), 10000×10000 and 14000×14000 mode-1 PNGs (the pixel-limit message), a PNG with a damaged `IDAT`, and a 400×300 JPEG cut to half its length, which `verify()` passes. After the cut JPEG, the inbox holds no new file and no `.avkit-tmp`, and a following `GET /captures` returns 200 | Local Canon: 09 `:1009`, `:1013`; D-416, D-417 | Yes: Red, the discriminator's 422 |
| AC-129.9 | e2e | Parametrized over three faults after the checks pass, each patched inside `monkeypatch.context()` and lifted before the follow-up list: `os.replace` raising `OSError`; `CaptureAdapter.probe` raising `InboxPathError` with the path in its message when called on the copy; and `SqlAlchemyUnitOfWork.commit` raising `RuntimeError` once the copy exists, so earlier commits in the request still pass. Each import returns 503 `internal_error` with no part of the path in the body; neither the temporary file, the copy nor a row is left; and a following `GET /captures` returns 200 without the shot | Local Canon: D-418 | Yes: Red, `import_image` is missing |
| AC-129.10 | e2e | With `Path.read_bytes` patched to raise `OSError` for the source, the import returns 422 `the file could not be read` | Local Canon: D-416 | Yes: Red, `import_image` is missing |
| AC-129.11 | e2e | `NO_RAW_CONSOLE` for both MEUs: with `HealthService._active` reset (D-391) and `build_services` into folders whose names hold a marker, one test registers a file before any list, imports an outside file, views a region, and triggers one import refusal and one view 422. No line of `capfd`'s stdout or stderr, the ring's messages, `console.log` or the error messages holds the marker, case-folded. Positive controls: a stdout `engine.created` line and at least two `capture.registered` lines in the ring | Local Canon: Session 50 RULE-1; Session 54 RULE-2; D-421 | Yes: Red, fewer than two `capture.registered` |
| AC-129.12 | unit (MCP) | `capture` with `mode: "import"` and `path` sends `{"mode": "import", "path": …}` as the POST body with `ADD_TIMEOUT_MS`; an extra key is refused | Local Canon: 09 `:1007`; D-415 | Yes: Red, zod refuses `import` |
| AC-129.13 | unit (MCP) | The `capture` description holds `mode=import` and `never changed`; the advertised schema's `mode` enum includes `import`, and `path` is listed | Research-backed: design §6.7 (R-8) | Yes: Red, the text is absent |

Guards that run unchanged in row 5: AC-37.x and AC-84.2 in `tests/e2e/test_api_captures.py`, the scan and register tests, the MCP capture suite's other members, and AC-38.2's 10 actions.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Request shape | Local Canon, corrected | 09 `:1007`; D-415 makes MCP `capture` `mode: import` |
| Copy, never move | Local Canon | 09 `:1008`; design D-9 |
| Accept order and messages | Local Canon and Inferred | 09 `:1009`, `:1013`; D-416 |
| Size cap | Human-approved | D-425 |
| Pixel limit as an error | Inferred, flagged | D-417 |
| Upright PNG | Research-backed | 09 `:1010`; design D-9 (R-7) |
| Name rules | Local Canon and Inferred | 09 `:1011`; D-420 |
| In-place keeps the source | Inferred, flagged | D-419 |
| `Import` with no wire value | Local Canon, corrected | 09 `:1012`; D-414 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/capture.py` | Modify | Constants, `ViewFrame`, `resolve_region`, `view_scale`, `view_frame` |
| `packages/core/src/avkit_core/domain/enums.py` | Modify | `CaptureSource.Import` |
| `packages/core/src/avkit_core/ports/capture.py` | Modify | `view`, `inspect_import`, `write_upright_png` |
| `packages/core/src/avkit_core/services/capture.py` | Modify | `read_image_view`, `import_image`, `IMPORT_MAX_BYTES` |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | Modify | `view`, `inspect_import`, `write_upright_png` |
| `packages/api/src/avkit_api/routes/captures.py` | Modify | Query parameters, headers, 413 text, import branch |
| `packages/api/src/avkit_api/schemas/captures.py` | Modify | `CaptureImportIn` |
| `openapi.committed.json` | Regenerate | §S6 |
| `mcp-server/src/toolsets/capture.ts` | Modify | Query keys, fields, the import member, descriptions |
| `mcp-server/src/toolsets/registry.ts` | Modify | `QUERY_GET_ONLY`, `FRAME_ITEM`, `OVERSIZE_HINT` |
| `mcp-server/src/client.ts` | Modify | `captureHeaders` |
| `tests/unit/test_domain_capture.py` | Modify | AC-128.1 to .5, AC-129.1, the members tuple |
| `tests/unit/test_domain.py` | Modify | The `CaptureSource` tuple |
| `tests/unit/test_capture_adapter.py` | Modify | AC-128.6 to .10 |
| `tests/e2e/test_api_captures.py` | Modify | `SOURCE_OUT` |
| `tests/e2e/test_api_capture_region_import.py` | New | AC-128.11 to .17, AC-129.2 to .11 |
| `mcp-server/tests/capture.test.ts` | Modify | AC-128.18 to .20, .22 to .24, AC-129.12, .13 |
| `mcp-server/tests/client.test.ts` | Modify | AC-128.21 |
| `docs/build-plan/09-screenshot-capture.md`, `00-overview.md`, `05-mcp-server.md` | Modify | §Spec text |

No test id is added, so `ui/tests/e2e/test-ids.ts` isn't touched (S9). No renderer file changes. Line endings (`C:/Temp/av-kit/s58-plan-probes.txt`, `s58-plan-eol.txt`): CRLF are `domain/capture.py`, `enums.py`, `ports/capture.py`, `services/capture.py`, `adapter.py`, `routes/captures.py`, `schemas/captures.py`, `openapi.committed.json`, `capture.ts`, `registry.ts`, the four Python test files above, `capture.test.ts`, `09`, `05`, the grouping and the matrix. LF are `client.ts`, `client.test.ts`, `00`, `meu-status.yaml` and the register. Every row measures with Python bytes first and writes with `newline=""`. New files are LF.

### Project files

- `docs/execution/plans/2026-11-08-capture-region-import/`: `implementation-plan.md`, `task.md`, `human-gate-decision.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `issue-file.py`, `session-gate.ps1`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, `.agent/context/known-issues.yaml` and `.agent/context/known-issues.md`, `.agent/context/triage-output.yaml`, and the grouping tracker row (`:108`).
- `.agent/context/handoffs/2026-11-08-capture-region-import-*.md`, `docs/execution/reflections/2026-11-08-capture-region-import-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Crop to a new shot | Feature | MEU-130 | Grouping D-402; reuses `resolve_region` (D-401) |
| The GUI crop tool | Feature | MEU-131 | Grouping |
| GUI import | Feature | MEU-132 | Grouping; 09 `:115` |
| Trim, extent, cover resize, tiles | Feature | None | Design §9, design D-13 |
| Geometry strings or gravity | API shape | None | Design §6.6 (R-9) |
| An ImageMagick dependency | Dependency | None | Design D-10 |
| Turning scanned EXIF-oriented files upright | Defect | Its own placement | D-424 files `CAPTURE-EXIF-SCANNED-ORIENTATION` |
| Raising the MCP 7,800,000 B or REST 15 MiB caps | Limit | None | MEU-111; `OVERSIZE_HINT` points to `max_edge` |
| Watching or moving the source file | Behaviour | None | 09 `:1008` |

## BUILD_PLAN.md Audit

MEU-128 is at `.agent/context/meu-status.yaml:3347` (phase 9, band P2, matrix item 9.35, anchor `region-view`, `pending`), and MEU-129 at `:3374` (9.36, `image-import`, `pending`). Plan time: 132 MEUs, 117 completed (116 approved, 1 closed), 15 pending (`C:/Temp/av-kit/s58-plan-meu-stats.txt`). Row 6 sets both `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at rows 6 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s58-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s58-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Checks the queue (S8): a subject among the last 40 commits ends `(MEU-124)`, no Session 55 path is dirty, and MEU-125 is `approved`, unless `-QueueWaived` is passed on Mat's words.
2. Creates `C:\Temp\av-kit\s58\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256.
3. Runs `uv sync --frozen --offline --all-packages` (plan-time dry run: `s58-uv-offline-dry-run.txt`, exit 0, "Would make no changes"), and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair is over 1024 B, because the full Python suite runs Session 54's real-FFmpeg module, and that Pillow is 13.0.0 with `MAX_IMAGE_PIXELS` 89,478,485, which D-417 and AC-129.8 rest on (S4).
4. Captures the base Python suite to `s58-base-py.txt`, the base UI suite to `s58-base-ui.txt` and the base MCP suite to `s58-base-mcp.txt`.
5. Runs `red-check.py --selftest` and `identity.py --selftest`.

`red-check.py` and `identity.py` are copies of Session 55's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds `CaptureImportIn`, `read_image_view`, `import_image`, `inspect_import` and `write_upright_png`, and keeps the selftest fixtures' names. These excuse a non-required block only: no required Red reaches them by name.
- **`identity.py`.** `PLAN` is this folder, and `NAMED_DISTRIBUTIONS` stays empty: no dependency changes. It binds the pinned FFmpeg pair by SHA-256. Its selftest binds `session-gate.ps1`, `issue-file.py`, the new e2e module, `09`, the register and its renders, and the crop grouping in place of Session 55's session-specific paths.
- **`PROJECT_ARTIFACTS`.** This plan's `*.md`, the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The registers and renders stay bound, because row 6 writes them before H1-2.

### 2. Type-only first, then Red, then Green (rows 1 to 5)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2, D-422).** The four constants, `ViewFrame`, `resolve_region` returning `(0, 0, W, H, False)`, `view_scale` returning 1.0, `view_frame` returning the whole-image frame, the port's `view`, and an adapter `view` returning `path.read_bytes()`. No service, route or MCP change. Its check runs `tests/unit/test_domain.py`, `test_domain_capture.py`, `test_capture_adapter.py`, `pyright` and `ruff` (Session 54 RULE-1).
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error and a required test that fails on a missing name. Rows 2 and 4 each hold a Python and an MCP Red receipt, one runner summary each.
- **Why each Red fails by assertion.** The region Reds call the row 1 stubs. FastAPI ignores unknown query keys, so the HTTP region Reds get today's response and fail on its headers or size. The import Reds get the discriminator's 422 and fail on the status. The MCP Reds fail because `.strict()` refuses the new keys, which the tests assert as a success. AC-128.19 and AC-129.2 are the only guards among them.
- **`--require` matches a test name up to a non-digit boundary** (`test_ac_128_1` never matches `test_ac_128_10`). A parametrized test is required by its base name and every case must fail.
  - Row 2, Python: `test_ac_128_1` to `_8` and `_10` to `_17`. MCP: `AC-128.18`, `.20`, `.21`, `.22`, `.23`, `.24`.
  - Row 4, Python: `test_ac_129_1` and `_3` to `_11`. MCP: `AC-129.12`, `.13`.
- **Guards pass in Red by design.** AC-128.9, .19 and AC-129.2 are in their rows' selection, and no Red row requires them.
- **AC-129.11 runs with HealthService built first (Session 54 RULE-2).** It sets `monkeypatch.setattr(HealthService, "_active", None)` before `build_services`, as D-391 did, reads `capfd`, and calls the returned dispose at the end. It registers a file before any list, because a scan's insert doesn't log.
- **Expectations stay immutable in Green.** No test file changes in rows 3 and 5.
- **OpenAPI.** Rows 3 and 5 regenerate `openapi.committed.json` with `tools/export_openapi.py` and check the diff against S6.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`: §1.
- `issue-file.py` (row 6): files `CAPTURE-EXIF-SCANNED-ORIENTATION` through `model.add_issue` and `model.save`, with D-424 in its `enrichment.decision_log`, and keeps a copy of the register as it was before (`C:/Temp/av-kit/s58/s58-ki-before-exif.yaml`). The plan-time dry run added 38 lines, removed none, kept LF, and left 123 issues (`C:/Temp/av-kit/s58-plan-issue-file-dry.txt`).
- `session-gate.ps1` (H1-2): below.

### Session gate (H1-2)

`session-gate.ps1` is Session 55's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s58-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `mcp-build`, `state-render`, `issues-render` |
| Runtime | `region-import` (the new e2e module on its own, so its receipt stands alone), then `ui-electron`, targeted to `ui/tests/e2e/capture-inbox.test.ts`, because the inbox page reads the image route and the source value this session changes |
| Skipped with reason | `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes) |

`py-tests` excuses only ids that row 0's receipt shows failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 6 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, or Pillow isn't 13.0.0 with `MAX_IMAGE_PIXELS` 89,478,485 | Stop: a fetch is a download and needs Mat's words, and D-417 rests on that version |
| S5 | Any network request, download or upload | Stop and tell Mat |
| S6 | `export_openapi.py` changes anything besides the six query parameters and the 200 header docs (row 3), and `CaptureImportIn` with its union entry (row 5) | Stop and find out why |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | At row 0, none of the last 40 commits is Session 55's, a Session 55 path is still dirty, or MEU-125 isn't `approved`, and Mat hasn't waived it | Stop; Mat commits Session 55 or waives the order |
| S9 | A row finds it must edit `ui/tests/e2e/test-ids.ts` | Stop, add ids in an additive block at the end, and run AC-51.6 and AC-81.13 in that row's own check |
| S10 | A path or the AC-129.11 marker reaches a Console surface or an error message in any receipt | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |

## Decision Log

> [!WARNING]
> Mat's request and design D-1 settle the scope, and the grouping (D-400 to D-406) placed these two MEUs. D-407 to D-424 didn't need Mat: each is autonomous, with its alternatives in `reasoning`. D-425, D-426 and D-427 were Mat's to rule (`human-gate-decision.md`), and Mat ruled each as recommended on 2026-11-08.
>
> Carried and not relisted in the block: every grouping §8 row, D-400 to D-406, with stage `grouping`. Of those, D-400, D-401, D-402, D-403 and D-405 bear on this session. The design's own D-1 to D-13 (`design.md:373-587`) are a separate namespace, cited here as "design D-n" in prose only. The probe (`C:/Temp/av-kit/s58-decision-issue-probe.txt`), run with this plan and the grouping as sources (Session 54 RULE-5), shows what the closeout's `--decision-issue` flag pulls in for `CAPTURE-EXIF-SCANNED-ORIENTATION`.

```yaml
decision_log:
  - id: D-407
    stage: planning
    question: "Where does the region contract live, and what does each bad region return?"
    resolution: autonomous
    class: two-way
    chosen: "REGION_RESOLVE and REGION_ERRORS: pure functions in domain/capture.py, raising ValidationError with fixed path-free messages in a fixed order; unit defaults to px"
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:990-992 — fields, frame and bounds"
      - "packages/core/src/avkit_core/domain/capture.py:25 — CAPTURE_MIN_EDGE_PX"
      - ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:63 — named services/capture.py for the resolver"
    research:
      engine: tavily
      sources:
        - "https://platform.claude.com/docs/en/build-with-claude/vision-coordinates — coordinates are read off the image the model saw"
        - "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/bounding-box-detection — models report boxes normalized to the image"
        - "https://glama.ai/mcp/servers/TOBYCAI/image-mcp/tools/crop — a crop tool that takes x, y, width and height"
        - "https://mochify.app/mcp — an image tool that clamps and reports"
    reasoning: "The grouping put the resolver in services/capture.py, but MEU-130's crop needs the same rules and the domain already holds CAPTURE_MIN_EDGE_PX and BBox, so pure functions there serve both and test without a service. FastAPI ge and le bounds would replace the messages with Pydantic's, which don't name the fix. One generic message for every bad region would leave the agent guessing which field to change."
  - id: D-408
    stage: planning
    question: "How are fractions rounded when a product lands a binary hair off a whole pixel?"
    resolution: autonomous
    class: two-way
    chosen: "Round each product to 9 places before floor or ceil"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:991 — floor and ceil with no guard"
      - "C:/Temp/av-kit/s58-plan-probes.txt — 0.1 plus 0.2 of 1000 gives 301 and 0.29 of 100 gives 28 without the guard"
    research:
      engine: none
      sources: []
    reasoning: "Without the guard, a region the caller computed exactly comes back a pixel wider or shifted, so a fraction read off a view doesn't round-trip. Rounding to nine places moves a product by at most 5e-10, so it changes a result only for a product that close to a whole number, far below a pixel for any image Pillow opens. Decimal arithmetic lost: it changes nothing for values that came from JSON floats and costs more code."
  - id: D-409
    stage: planning
    question: "How is a view scaled and resampled?"
    resolution: autonomous
    class: two-way
    chosen: "VIEW_SCALE: a region fits max_edge, upscaled at most 4x; max_edge alone only shrinks; edges round half up with a floor of 1; Lanczos"
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:993 — the scale rule"
      - "_inspiration/capture-crop/design.md:115 — section 6.1"
    research:
      engine: tavily
      sources:
        - "https://platform.claude.com/docs/en/build-with-claude/vision — images over 1568 px on the long edge (2576 px on Claude 4.7 and later) are resized"
        - "https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — screenshots are scaled and coordinates mapped back"
        - "https://doi.org/10.48550/arxiv.2502.17422 — zooming into a crop improves small-detail answers"
    reasoning: "Fitting the region to max_edge, 1568 by default and up to 2576 for a high-resolution model (D-426), gives the detail the model keeps at a cost the caller picks. The 4x cap stops a tiny region turning into blur that looks like detail. Shrinking only, when no region is given, keeps max_edge a way to fit a large shot under the caps. Nearest or bicubic lost: Lanczos is Pillow's sharpest downscale and the design's choice."
  - id: D-410
    stage: planning
    question: "What does the adapter return for a view, and what if the file changed?"
    resolution: autonomous
    class: two-way
    chosen: "VIEW_FORMAT and RETURN_UNCHANGED: keep the file's format in memory, return the file's bytes for a whole-image frame at scale 1, and raise a path-free ConflictError when the file's size differs from the row"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:52 — LOSSY_QUALITY"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:253-263 — probe names the path in its errors"
      - "packages/core/src/avkit_core/services/capture.py:309-372 — a list refreshes a changed file's size"
    research:
      engine: none
      sources: []
    reasoning: "Keeping the format keeps the route's media type right and a JPEG small. Always PNG lost: a JPEG photo view would grow several times and hit the caps sooner. Returning the file's bytes unchanged keeps today's behaviour for every caller that passes nothing. Cropping the file's real size when the row is stale would give a frame that doesn't match get, so the agent is told to list again."
  - id: D-411
    stage: planning
    question: "How does the API report the frame?"
    resolution: autonomous
    class: two-way
    chosen: "FRAME_HEADERS: five X-Capture headers on every 200, documented in the route's responses for 200"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:994 — the frame in headers"
      - "packages/api/src/avkit_api/routes/tts.py:62-67 — a route's responses argument, used for a 409 only"
      - "packages/api/src/avkit_api/errors.py:50 — X-Request-ID, the API's one custom header"
    research:
      engine: none
      sources: []
    reasoning: "Headers keep the body an image, so every existing client keeps working. One JSON header lost: a header per value is readable with curl and needs no parser. Sending them on the no-field path too gives the agent the source size without a get. Leaving them undocumented would hide them from OpenAPI readers; no route documents a header yet, so this sets the pattern."
  - id: D-412
    stage: planning
    question: "How does MCP give the agent the frame?"
    resolution: autonomous
    class: two-way
    chosen: "FRAME_ITEM: a JSON text item with frame and map before the image when all five headers parse, else the image alone; the descriptions follow design 6.7; 05 gains the identify and look rows of design 6.6"
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:994,997 — two items, and tests that read content[0] updated"
      - "mcp-server/scripts/audit/client.ts:116 — the audit finds the image with content.find"
      - "mcp-server/tests/image-over-stdio.test.ts:71 — so does the stdio test"
    research:
      engine: tavily
      sources:
        - "https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — the caller maps scaled coordinates back"
        - "https://www.anthropic.com/research/writing-tools-for-agents — return what the agent needs for its next call"
    reasoning: "An agent can't read HTTP headers through MCP, so the frame must be content, and first, so it is read before the image. Requiring all five headers keeps a fake or older API on today's one-item shape, so no existing test changes, which corrects 09:997's plan to update them. Always two items lost: it would invent a frame when the API sent none. The crop rows of design 6.6 wait for MEU-130, which ships crop."
  - id: D-413
    stage: planning
    question: "How are the new query keys kept off POST rows?"
    resolution: autonomous
    class: two-way
    chosen: "QUERY_GET_ONLY: withQuery runs only for GET rows"
    source_tag: Local Canon
    precedents:
      - "mcp-server/src/toolsets/registry.ts:335 — withQuery runs for every method"
      - "mcp-server/src/toolsets/registry.ts:215-240 — httpBody sends POST capture region's x, y, width and height"
    research:
      engine: none
      sources: []
    reasoning: "Once x, y, width and height are query keys, a POST capture region would also send them in the query, which the API ignores today but which leaks a meaning across routes. Per-action key lists lost: GET is the only method that reads a query here, so the method test is smaller and AC-128.19 pins it."
  - id: D-414
    stage: planning
    question: "Does the Import source need a wire map entry or a migration?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_SOURCE: CaptureSource.Import stored and returned by name; no wire map entry and no migration"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:282 — CaptureSource goes over the wire by name"
      - "docs/build-plan/09-screenshot-capture.md:1012 — wire import"
      - ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:63 — named domain/wire.py"
    research:
      engine: none
      sources: []
    reasoning: "The register's lowercase wire values map the register body's source field, and import doesn't use register. The column is a string, so a new name needs no migration. Adding a lowercase import wire value would create a second spelling that nothing reads. This corrects 09:1012 and the grouping."
  - id: D-415
    stage: planning
    question: "What is the import request's shape in the API and MCP?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_MODE: POST /captures mode import with path, and MCP capture with mode import, not a new MCP action"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1007 — MCP import with path"
      - "docs/build-plan/09-screenshot-capture.md:578 — MCP capture maps POST /captures by mode"
      - "_inspiration/capture-crop/design.md:196 — section 6.4 used action import"
    research:
      engine: none
      sources: []
    reasoning: "MCP capture already maps POST /captures one mode at a time, so a mode keeps one MCP action per route and leaves the 70-row action index and AC-38.2's 10 actions as they are. A new import action lost: it would add a registry row and an index row for a route that already exists. This corrects 09:1007 and design 6.4."
  - id: D-416
    stage: planning
    question: "In what order is an import path checked, and what do refusals say?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_ACCEPT: absolute, exists, regular file, suffix, size, annotated copy, read, inspect; fixed path-free messages; InboxPathError for the path and ValidationError for the content, both 422"
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1009,1013 — accepted files and error examples"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:256,262 — probe names the path"
      - "packages/api/src/avkit_api/errors.py:138-149 — 503 is internal_error and unlogged"
    research:
      engine: tavily
      sources:
        - "https://www.anthropic.com/research/writing-tools-for-agents — errors should name the fix"
    reasoning: "Cheap checks first means a folder or a 2 GB file is refused before any read. Fixed messages keep the caller's path out of logs and the Console. Reusing probe lost: its messages hold the path. One generic refusal lost: the agent couldn't tell a relative path from a bad file."
  - id: D-417
    stage: planning
    question: "How is an import's content checked and turned upright?"
    resolution: autonomous
    class: two-way
    chosen: "inspect_import: bomb warnings as errors, an explicit pixel limit, verify, a full load, then the EXIF orientation; any other exception gives the generic refusal; write_upright_png through exif_transpose and _write_png"
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1009-1010 — verify, the bomb guard, upright PNG"
      - "C:/Temp/av-kit/s58-plan-exif-probe.txt — Pillow 13.0.0, MAX_IMAGE_PIXELS 89478485, exif_transpose turns 400x300 into 300x400 for orientations 5 to 8"
      - "C:/Temp/av-kit/s58-corrections-verify.txt — verify passes a 400x300 JPEG cut to half its length and load refuses it"
      - "C:/Temp/av-kit/s58-corrections-verify2.txt — a damaged PNG IDAT raises SyntaxError, which isn't an OSError"
      - "C:/Temp/av-kit/s58-corrections-verify3.txt — Image.open raises the bomb warning and error for the 10000 and 14000 px PNGs"
    research:
      engine: tavily
      sources:
        - "https://mochify.app/mcp — an agent image tool that normalizes orientation"
    reasoning: "Pillow only warns between one and two times its pixel limit, so a 120-megapixel file would pass with a warning; turning the warning into an error and checking the product makes the limit one number. Leaving orientation to the reader lost: every later view, mark and crop would have to rotate. A byte copy of a rotated file would show sideways in Pillow and upright in Chromium. Verify alone lost (round-1 review F1): it passes a truncated JPEG that probe then refuses with the path in its message."
  - id: D-418
    stage: planning
    question: "How is the copy written so a scan or a failure never leaves a half state?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_COPY: under CAPTURE_FILE_LOCK, write NAME.avkit-tmp, os.replace, probe, register; on any exception through the unit of work's commit, remove the temporary file and, once os.replace has run, the copy, commit no row, and raise a generic CaptureFailedError"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:67-70 — CAPTURE_FILE_LOCK"
      - "packages/core/src/avkit_core/services/capture.py:312 — scan_inbox takes the lock"
      - "packages/infrastructure/src/avkit_infra/database/unit_of_work.py:54-65 — the commit runs in __exit__"
      - "packages/core/src/avkit_core/services/capture.py:715-717 — convert's except Exception removes what it wrote"
    research:
      engine: none
      sources: []
    reasoning: "Holding the lock across the name choice, the write and the row means a scan can't insert the copy as Scan and two imports can't pick the same name. Writing straight to the final name lost: a crash would leave a partial image that the next scan registers. The generic 503 keeps the OSError text, which holds the path, out of the response. Catching only OSError and CaptureFailedError lost (round-1 review F1): probe's InboxPathError and a failed commit would leave the copy and send the path."
  - id: D-419
    stage: planning
    question: "What does importing a file already in the inbox root do?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_IN_PLACE: return the existing row with its source kept and its size refreshed; register a row with source Import when none exists; never copy"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1008 — a path already in the inbox registers in place"
      - "packages/core/src/avkit_core/services/capture.py:853-895 — _upsert_shot lets the registering source win"
    research:
      engine: none
      sources: []
    reasoning: "The row's source records how the file arrived, and importing a file already there doesn't change that, so _upsert_shot's rule is bypassed here. Copying it lost: the call would stop being idempotent and the inbox would fill with duplicates. An annotated copy is refused, because a scan never registers one."
  - id: D-420
    stage: planning
    question: "How is the copy named?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_NAME: the sanitized stem, import if empty, import_ before a reserved name, the lowercased suffix or png when rotated, then _2, _3 against files and rows"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1011 — sanitized stem and a unique suffix"
      - "packages/core/src/avkit_core/services/capture.py:841 — _unique_png"
    research:
      engine: none
      sources: []
    reasoning: "Keeping the stem lets a person find the shot by its old name. Dots become underscores, so no copy ends in a derived suffix like .annotated. A random name lost: it hides where the image came from. Checking rows as well as files catches a row whose file is gone."
  - id: D-421
    stage: planning
    question: "Where are the new values written, and does the Console see them (Session 50 RULE-1)?"
    resolution: autonomous
    class: governance-value
    chosen: "Where values go: no new log line; refusals hold no path; capture.wrote's path is dropped by the Console processor; AC-129.11 proves it through build_services with markers"
    source_tag: Local Canon
    precedents:
      - "docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md:137 — Session 50 RULE-1"
      - "packages/core/src/avkit_core/services/health.py:47-56 — CONSOLE_FIELDS"
      - "packages/core/src/avkit_core/services/capture.py:894 — capture.registered"
    research:
      engine: none
      sources: []
    reasoning: "Import takes a path from outside, so the rule has a real target here. The only new outside text is the stem, which IMPORT_NAME sanitizes. One test across both MEUs costs one real stack and covers every surface."
  - id: D-422
    stage: planning
    question: "In what order do the rows add the shared names?"
    resolution: autonomous
    class: two-way
    chosen: "Row 1 adds the region constants, ViewFrame, the three stubs and the port's view stub; rows 2 and 4 fail by assertion; the import names arrive in row 5"
    source_tag: Local Canon
    precedents:
      - "Session 53 RULE-2 — a shared missing name gets a type-only row first"
      - "docs/execution/plans/2026-11-08-download-received-quality/red-check.py — a missing name is a setup failure"
    research:
      engine: none
      sources: []
    reasoning: "Without row 1, the domain and adapter Reds would fail on missing names, which red-check refuses. The import Reds reach import_image over HTTP or through a callable check, so they need no stub. Stubbing the routes too lost: the HTTP Reds already fail by assertion."
  - id: D-423
    stage: planning
    question: "Which checks does the session gate run?"
    resolution: autonomous
    class: two-way
    chosen: "Session 55's shape; the runtime stage is the new e2e module on its own, then the capture inbox E2E; no package build; mcp-audit and build-record skipped with reasons"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-download-received-quality/implementation-plan.md:390-402 — Session 55 session gate"
      - ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:66 — no Electron"
    research:
      engine: none
      sources: []
    reasoning: "The grouping said no Electron, meaning no renderer change, but the inbox page reads the image route and the source value, so one targeted E2E proves the built app still shows shots. Skipping it lost: the headers and the new source would reach the renderer unproven."
  - id: D-424
    stage: planning
    question: "The import design turns EXIF-oriented images upright, but scanned and registered files keep their stored frame. Fix the scan path in Session 58, file it, or leave it?"
    resolution: autonomous
    class: two-way
    chosen: "File it as an open TECH-DEBT issue linked to MEU-129 and fix only the import path in Session 58"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:253-263 — probe reads the stored size"
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md — D-417 upright PNG"
      - "AGENTS.md — out-of-scope findings go to the known-issues register"
    research:
      engine: none
      sources: []
    reasoning: "Changing the scan path rewrites the frame of rows already stored, which the MEU-128 and MEU-129 ACs do not cover. Leaving it unrecorded hides a defect the plan found. Filing keeps the session's scope and records the probe. Two-way."
  - id: D-425
    stage: planning
    question: "What is the import size cap?"
    resolution: human
    class: governance-value
    chosen: "IMPORT_MAX_BYTES 50,000,000, the design's starting point, as recommended"
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1009 — a tunable the plan fixes, starting from 50 MB"
      - "packages/api/src/avkit_api/routes/captures.py:48 — IMAGE_MAX_BYTES 15 MiB, outgoing"
      - "mcp-server/src/toolsets/capture.ts:12 — IMAGE_MAX_BYTES 7,800,000 B, outgoing"
      - "packages/core/src/avkit_core/services/transcript.py:45 — COMPILE_READ_MAX_BYTES 20 MiB, read as text; no cap on incoming files exists"
    research:
      engine: "pomera_web_search (tavily)"
      sources:
        - "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/image-understanding — 7 MB inline, 30 MB from storage"
        - "https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-new-file-limits — inline data raised from 20 MB to 100 MB"
        - "https://github.com/NousResearch/hermes-agent/issues/45780 — an agent's image cap raised to 25 MB"
        - "https://imageresizerai.com/blog/image-file-size-explained — a 4000 by 3000 photo as lossless PNG is about 22 MB"
        - "https://support.claude.com/en/articles/8241126-upload-files-to-claude — chat takes 500 MB per file and images up to 8000 by 8000 px"
        - "https://otio.ai/blog/ai-file-upload-limits-research-workflows — ChatGPT takes images up to 20 MB each, per OpenAI's documentation"
        - "https://github.com/ImageMagick/ImageMagick/discussions/6068 — ImageMagick limits width, height, area, memory, disk and time, never file bytes, and a stock policy sets none"
        - "https://lovelace.cluster.earlham.edu/mounts/lovelace/software/imagemagick/ImageMagick-7.1.1-41/www/security-policy.html — the sample security policy refuses an image over 8192 px wide or tall"
    reasoning: "50 MB takes any phone photo or 8K screenshot. 15 MiB would make every byte-copied original readable through image without a region (an upright PNG from a rotated JPEG can be larger: the round-1 review turned a 4,186,900 B JPEG into an 18,750,276 B PNG), but refuses large photos that a region view could still serve. Doing nothing leaves only the pixel limit, which lets a 400 MB file be read into memory; ImageMagick bounds that risk with memory, disk and time limits that av-kit doesn't have. The model-facing limits (Claude 500 MB per file, ChatGPT 20 MB per image, Gemini 100 MB inline) cap what is sent to a model, and an import only reads a local file. A new limit (HDP section 4 test 4), so governance-value. Two-way: one constant."
    human_message_reference: "USER_EXPLICIT 2026-11-08 'all recommendations accepted'"
  - id: D-426
    stage: planning
    question: "Are the view defaults 1568, 64 to 2576 and 4x right?"
    resolution: human
    class: governance-value
    chosen: "As the design has them, as recommended: max_edge 1568 by default, 64 to 2576 allowed, a region enlarged at most 4x"
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:990,993 — the range and the default"
      - "_inspiration/capture-crop/design.md:115 — section 6.1"
    research:
      engine: "pomera_web_search (tavily, exa)"
      sources:
        - "https://platform.claude.com/docs/en/build-with-claude/vision — Claude 4.7 and later keep 2,576 px and 4,784 visual tokens; other models 1,568 px and 1,568 tokens"
        - "https://platform.claude.com/docs/en/build-with-claude/vision-coordinates — coordinates are in the image the model saw"
        - "https://dev.to/gabrielanhaia/claude-reads-screenshots-at-2576px-now-the-same-png-can-cost-3x-the-tokens-4cp4 — a large PNG costs about three times the tokens on a 4.7 model"
        - "https://doi.org/10.48550/arxiv.2610.09313 — a zoom tool capped at 1,024 px and 2x; enlarging helped GPT-5.6 but not significantly Claude Sonnet 5.5, which gained most from native pixels; two of four agents failed to map crop positions back"
        - "https://doi.org/10.48550/arxiv.2502.17422 — zoomed crops help small details"
    reasoning: "Current Claude models keep 2576 px, so 1568 is a cost choice, not the long edge a model keeps. A default view costs at most 3,136 visual tokens (1,792 for 16:9), and an agent passes 2576 for more. A 2576 default costs up to 4,784 tokens on every view and enlarges mid-size regions with no new pixels. The study's 1024 and 2x would shrink whole-shot views below either tier and give up the enlargement gain one model showed. Doing nothing, scaling only when max_edge is passed, would return a 30 by 20 region at 30 by 20. The reading probe the design proposed was not run, so the numbers rest on the documents and two papers. New limits (HDP section 4 test 4), so governance-value. Two-way: four constants."
    human_message_reference: "USER_EXPLICIT 2026-11-08 'all recommendations accepted'"
  - id: D-427
    stage: planning
    question: "Are the crop docs committed before execution?"
    resolution: human
    class: two-way
    chosen: "Yes: one exact-scope docs commit of Stage A's seven files, each checked against its SHA-256 in human-gate-decision.md, without this plan folder, the review handoff or a push. The push is a separate approval. Committed as 75617379f63c0885024b2c9f0dd9fc72de854b8b, and pushed separately on Mat's direction on 2026-11-08"
    source_tag: Human-approved
    precedents:
      - "docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md:387 — D-276, Human-approved 2026-11-05: one exact-scope commit of the triage records, without the plan folder and without a push; committed as 83229ea"
      - ".agent/skills/git-workflow/SKILL.md:59 — exact-scope signed commit mode, -NoPush mandatory"
      - "AGENTS.md:102 — leave another session's files alone and commit only your own paths"
    research:
      engine: "pomera_web_search (tavily, exa)"
      sources:
        - "https://gitbybit.com/gitopedia/best-practices/atomic-commits — commit unrelated changes separately, so each commit is a logical unit that is easy to understand and to revert"
        - "https://stackoverflow.com/questions/6543913/git-commit-best-practices — a commit should hold one change only"
        - "https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution — parallel agents' uncommitted edits collide in a shared tree; each run is diffed against a known-good start"
    reasoning: "The seven files register MEU-128 to MEU-132 and place Sessions 58 to 61, and no review outcome changes them. Committing now gives row 0 a clean baseline, keeps the H2-5 commit to this session's work, and fences the files off from the parallel light-accent-contrast session, which carries a matrix rebaseline script. Committing after the plan is approved also works but leaves them exposed for the rest of the review. Doing nothing still works, because row 0 records them and rows 6 and H1-2 check their SHA-256, but the session's commit then mixes registration with code, and another session's edit would refuse a row partway through execution. The plan runs under every option. A commit is a hard gate, so Mat rules it, and the push stays a separate approval because the repository is public. Two-way while unpushed."
    human_message_reference: "USER_EXPLICIT 2026-11-08 'all recommendations accepted'"
```

## Research References

- `docs/build-plan/09-screenshot-capture.md:978-1015` (the two contracts), `:282`, `:532-538`, `:577-578`; `docs/build-plan/05-mcp-server.md:224-337`; `docs/build-plan/00-overview.md:68`.
- `_inspiration/capture-crop/design.md`: §5 research (`:94`), §6.1 to §6.7 (`:115-275`), §9 (`:327`), §11 (`:356`), §12 decisions (`:373-587`).
- The grouping file: §3 (`:61-68`), §6 (`:104-113`), §7 (`:115-124`), §8 (`:126-141`).
- Design research, read through `pomera_web_search` (tavily) when the design was written: R-1 and R-2 (the vision and vision-coordinates pages), R-3 (bounding-box detection; Qwen3-VL issue 866), R-4 (computer use), R-5 (arXiv 2502.17422), R-6 and R-7 (two agent image tools), R-8 (writing tools for agents), R-9 (ImageMagick crop usage). URLs in the design's §5.
- Session 55's plan, task and scripts (`docs/execution/plans/2026-11-08-download-received-quality/`, uncommitted at plan time), Session 54's (`docs/execution/plans/2026-11-07-convert-extract-index/`), and Session 44's MEU-111 work.
- The 2026-11-08 HDP refresh, at Mat's request: the searches `C:/Temp/av-kit/s58-hdp-d425-web1.txt`, `s58-hdp-d425-web2.txt`, `s58-hdp-d426-web1.txt`, `s58-hdp-d426-web2.txt`, `s58-hdp-d427-web1.txt` and `s58-hdp-d427-web2.txt` (`pomera_web_search`, tavily and exa); the claim map `s58-hdp-claim-map.txt`; and the sweeps `s58-hdp-d425-sweep-code.txt`, `s58-hdp-d427-sweep.txt`, `s58-hdp-d427-sweep2.txt`, `s58-hdp-d427-gitlog.txt` and `s58-d427-free.txt`. The URLs are in D-425 to D-427 and the briefs.

## Planning receipts

- `C:/Temp/av-kit/s58-plan-probes.txt`: line endings and SHA-256 of every target file, and the float cases for D-408.
- `C:/Temp/av-kit/s58-plan-eol.txt`: the line endings again for the files added later.
- `C:/Temp/av-kit/s58-plan-exif-probe.txt`: Python 3.12.12, Pillow 13.0.0, `MAX_IMAGE_PIXELS` 89,478,485. For a 400×300 JPEG with orientations 5 to 8, `probe` reports 400×300 and `exif_transpose` gives 300×400. This is 09 `:1014`'s planning check, run as a probe of the frame rather than a GUI run.
- `C:/Temp/av-kit/s58-plan-issue-file-dry.txt`: `issue-file.py` on a copy of the register. Before `1b1331dbbffb7c66…` (388,872 B), after `eb0b267de28193c4…` (391,954 B, no CRLF), 38 lines added, 0 removed, 123 issues. Row 6 reads the SHA-256 again.
- `C:/Temp/av-kit/s58-plan-meu-stats.txt`.
- `C:/Temp/av-kit/s58-uv-offline-dry-run.txt` (Session 52 RULE-2): `uv sync --frozen --offline --all-packages --dry-run` exits 0, 122 packages, "Would make no changes". This plan relies on no cached wheel, model or file except the pinned FFmpeg pair, already on disk.
- `C:/Temp/av-kit/s58-plan-stage-copies.txt`: the scripts copied from Session 55's and edited (red-check 2 edits, identity 7), 0 failures.
- `C:/Temp/av-kit/s58-plan-status3.txt`: the tree at plan time, Session 55's files and the Stage A files dirty. `C:/Temp/av-kit/s58-plan-status4.txt`: the tree after `f69ee08` and the relocation, with only the Stage A files and this folder.
- `C:/Temp/av-kit/s58-plan-identity-selftest.txt`, `C:/Temp/av-kit/s58-plan-redcheck-selftest.txt`: the scripts' selftests, run again in this folder.
- `C:/Temp/av-kit/s58-plan-task-lint.txt`: `lint_task_contract.py` on `task.md` in this folder.
- `C:/Temp/av-kit/s58-decision-issue-probe.txt`: the decision probe.
- `C:/Temp/av-kit/s58-plan-relocate.txt`: these files were first written under `C:/Temp/av-kit/s58/stage/`, because Session 55's gate bound the dirty tree, and were copied here byte for byte once `f69ee08` landed. Ledger loop `s58-plan-2026-11-08-capture-region-import`, opened on the staged path, recorded no round and is abandoned. The plan review runs in loop `s58-plan-canonical-2026-11-08-capture-region-import`, bound to this path (`C:/Temp/av-kit/s58-plan-ledger-begin-canonical.txt`).
- `C:/Temp/av-kit/s58-corrections-verify.txt`, `s58-corrections-verify2.txt` and `s58-corrections-verify3.txt`: the round-1 corrections' probes, Pillow in memory. `verify()` passes a 400×300 JPEG cut in half and `load()` refuses it; a damaged PNG `IDAT` raises `SyntaxError`; `Image.open` raises the bomb warning and error for AC-129.8's oversize PNGs; `int(x + width)` overflows at `1e308` and `int(x) + int(width)` doesn't.
- `C:/Temp/av-kit/s58-hdp-refresh.txt`: the HDP refresh's edits, and the seven Stage A files' SHA-256 read again for D-427.
- Step 4A GUI check (`gui-refs-not-shipped`, items 3 and 5): no renderer file changes. The inbox page shows an imported shot as it shows a scanned one.
- Not run at plan time: any suite, build or smoke, or the reading probe. Row 0 runs the suites.

## Validation stage contract

- **Static:** `pyright packages/`, `ruff`, the UI typecheck and lint, the MCP typecheck, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds, the OpenAPI guard and the two render checks, in the session gate.
- **Runtime:** the new e2e module on its own, and the capture inbox E2E spec on the built app.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks the handoffs' evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
