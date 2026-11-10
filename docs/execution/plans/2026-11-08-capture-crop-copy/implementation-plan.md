---
project: "2026-11-08-capture-crop-copy"
date: "2026-11-08"
source: ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md#session-59--capture-crop-copy-meu-130--p2"
grouping_source: ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md"
meus: ["MEU-130"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: An agent crops a capture into a new shot (Session 59)

> **Project:** `2026-11-08-capture-crop-copy`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Residuals registered 2026-11-08: §Crop to a new shot (`:1017-1032`, anchor `crop-to-new-shot`, MEU-130).
>
> **Source request.** Mat asked on 2026-11-08 for a crop feature on the capture page that agents can use through the GUI, MCP and API, on screenshots or any other image, agent use first (`_inspiration/capture-crop/design.md`, design D-2). Mat ruled design D-1 ("New shot (copy); source untouched"), asked for the grouping and Session 58's plan, and then asked: "can you start planning now while session 57 is finilizing its planning". The grouping (D-400 to D-406) puts the design's slice S2 here. Done comes from 09's contract, not from Mat's words: "A crop writes the region as a new PNG shot with source `Crop`, cut from the original's pixels exactly with the same box rules as a region view, carries the source's saved marks clipped to the crop with their counts reported, and never changes the source's file, sidecar or bake."
> **Known issues:** none open for this MEU. Under D-499 option A, row 6 files `MCP-AUDIT-BASELINE-PENDING-CROP`.
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review. Execution also waits for Session 58 to close (grouping §5) and for Session 57 (MEU-125, rc.2) to be `approved` (grouping D-405).
>
> **This plan is written on top of an approved plan that has not run.** Session 58 (`docs/execution/plans/2026-11-08-capture-region-import/`, approved at plan-review round 3 and committed in `8bcb4a6`) adds `resolve_region`, `CaptureSource.Import`, the `.avkit-tmp` write pattern and the region view. Every anchor here is from `main` `8bcb4a6`, read 2026-11-08, before Session 58's code exists. Session 58 will move most of them. Row 0 re-reads every target named in §Files Modified, and S11 stops the session if a Session 58 shape this plan relies on differs from Session 58's plan.

## Goal

**Goal anchor:** Session 59 lets an agent cut a region of any capture into a new shot. `POST /captures/{id}/crop` and MCP `crop` take `x`, `y`, `width` and `height` in original pixels, or in fractions with `unit: "fraction"`, and an optional `name`. The box goes through Session 58's `resolve_region`, so a crop and a region view of the same box cut the same pixels (grouping D-401). The original's pixels are saved exactly, with no resampling, as a PNG in the inbox root with metadata stripped and the ICC profile kept (a CMYK, YCbCr or LAB source converts through its profile to sRGB, D-506). The new shot has source `Crop`. The source's saved marks are carried over, moved by the crop's origin and clipped to it, and the crop gets its own sidecar and bake. The response is 201 with the new shot, the source id, the requested and applied boxes, whether the box was clamped, and how many marks were kept, clipped and dropped. The source's file, sidecar, bake and row are never changed, so no `confirm` is asked.

Four things are missing today:

1. **An agent can't keep a part of a capture.** Session 58's region view returns bytes and writes nothing (09 `:993`). To keep a region, an agent must save the view itself, outside the inbox, with the frame lost and the marks gone.
2. **No source value marks a cropped shot.** `CaptureSource` stops at `Scan` today (`packages/core/src/avkit_core/domain/enums.py:209-217`), and `Import` after Session 58.
3. **Marks don't survive a change of frame.** Saving clamps a mark's origin into the image and never shrinks it (`services/capture.py:917-952`, design L-7), and an arrow's ends are clamped one at a time, which can turn it. A crop needs real clipping, or its annotated copy loses a redaction or points an arrow the wrong way.
4. **MCP has no `crop` action.** `avkit_capture` has 10 actions (`mcp-server/tests/capture.test.ts:124`), and `ACTION_INDEX` has 70 rows (`mcp-server/tests/action-index.test.ts:41`).

The session ends when the contract's tests and 09's contract hold, the session gate passes, the audit baseline is handled as Mat ruled under D-499 (option A), and MEU-130 is `approved`.

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
  - receipts go under `C:/Temp/av-kit`, named `s59-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s59\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s59-plan-canonical-2026-11-08-capture-crop-copy` and `s59-execution-2026-11-08-capture-crop-copy`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290).
  - Reviewer prompts name the ledger vocabulary up front: D-481 to D-499, AC-130.1 to AC-130.29, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json` and anything under `.agent/fleet/hub`. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). Each recheck asks for a `### New Findings` table and for bare words in its Recheck cells (`fixed`).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, the live MCP audit, `--update-baseline`, or an `approved` verdict authored by the implementer. Capture stays local: no test or row uploads an image or reads one from the network. Tests build their images with Pillow under `tmp_path`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-130 `capture-crop-copy` | `.agent/context/handoffs/2026-11-08-capture-crop-copy-MEU-130-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-08-capture-crop-copy-plan-critical-review.md` and `.agent/context/handoffs/2026-11-08-capture-crop-copy-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, the re-read anchors |
| WP-2 | Type-only names (row 1) | WP-1 | shared | `MarkCarry`, the `clip_mark` stub, `CropResult`, the port's `crop` stub, with no behaviour |
| WP-3 | Mark carry Red, then Green (rows 2, 3) | WP-2 | shared | `MARK_CARRY`, `MARK_CLIP_BOX`, `MARK_CLIP_ARROW`, `MARK_CLIP_TEXT`, `CROP_SOURCE` |
| WP-4 | Crop Red, then Green (rows 4, 5) | WP-3 | shared | `CROP_REQUEST`, `CROP_READ`, `CROP_PIXELS`, `CROP_NAME`, `CROP_BAKE`, `CROP_CLEANUP`, `CROP_RESPONSE`, `CROP_MCP`, `BASELINE_PENDING` (under D-499 A) |
| WP-5 | Records (row 6) | WP-4 | shared | Spec notes, MEU status, the filed issue under D-499 A, renders, grouping tracker |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | The handoff, review, reflection, Session 60's prompt |

Split flag (grouping `:72`): rows 2 and 3 are pure domain. If row 3 leaves the session past about half its context, rows 4 and 5 run as Session 59b from this same plan and task, with no plan change.

## User Review Required

> [!IMPORTANT]
> **One question is Mat's, ruled A on 2026-11-09: D-499, how the MCP audit baseline meets the new `crop` action** (`governance-value`; `human-gate-decision.md`). Adding an `ACTION_INDEX` row breaks AC-68.5 (`mcp-server/tests/audit/coverage.test.ts:78-85`), which asserts that the authoritative baseline (`.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`, 70 entries) covers exactly `ACTION_INDEX`. The baseline can't be refreshed now: the open `YOUTUBE-CAPTIONS-IP-BLOCK` makes 7 transcript rows REGRESSION, and a REGRESSION blocks `--update-baseline` (`SKILL.md:45-51`). Session 57's new release rule (`docs/execution/plans/2026-11-08-release-rc2/audit-rule.py`, uncommitted) also refuses any NEW row.
> - **A (Recommended):** `BASELINE_PENDING = ["avkit_capture.crop"]` in `coverage.test.ts`; AC-68.5 then asserts the baseline misses exactly the pending keys, each of which is in `ACTION_SET` and absent from the baseline, and has no extra key. Row 6 files `MCP-AUDIT-BASELINE-PENDING-CROP`, linked to `YOUTUBE-CAPTIONS-IP-BLOCK`, closed by the next authoritative update. The next release's audit rule has to accept the pending NEW or follow a refresh.
> - **B:** a gate-only tolerance in MEU-67's shape (`docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md` D-20, `:200`). `main`'s MCP suite stays red until the next authoritative update.
> - **C:** an authoritative refresh in this session with `baseline_carry.py`. It needs the live audit (a network run, Mat's words) and is blocked by the caption block as long as it is open.
> - **D, do nothing:** AC-68.5 fails, the session gate's `mcp-tests` step fails, and the session can't close.
>
> Every other choice is recorded as autonomous in §Decision Log (D-481 to D-498), with its alternatives. Mat ruled D-499 A on 2026-11-09 ("D-499 A"). The gate asks Mat to accept the plan or override one of the others, and only Mat's words start execution.
>
> **The queue (S8).** Row 0 refuses to start until MEU-128 and MEU-129 are `approved` with no Session 58 path dirty, and MEU-125 (Session 57) is `approved`. Only Mat's words waive that, through `baseline.ps1 -QueueWaived`. A waiver can't skip Session 58: this plan calls its code (S11).
>
> **What the words in the contract mean here, and the limits they leave.**
> - **Same box, same pixels.** The crop and `GET image` with the same box resolve the same box: `X-Capture-Region` equals `applied` for every input (AC-130.13). Where `applied`'s long edge is inside Session 58's `max_edge` range of 64 to 2576, `GET image` with `max_edge` equal to that long edge is at scale 1 and returns the crop's pixels. Outside that range the view scales by design, so the test compares the crop with the source's own pixels at `applied` instead. Rounding, the 9-place guard, the clamp and the 8 px minimum are Session 58's.
> - **A crop keeps the source's pixel mode when PNG can store it,** and is RGB or RGBA otherwise. A JPEG source gives an RGB PNG of the decoded pixels. The ICC profile is kept; EXIF, XMP and text chunks are dropped (D-482). PNG can't hold a CMYK, YCbCr or LAB image or its profile, so such a source converts through its profile to sRGB and the crop carries the sRGB profile; with no profile, or one that builds no transform, it converts plainly and carries none (D-506, amending D-482 after execution review round 1 F1).
> - **A crop reads the stored frame,** as `image` and `annotate` do. A scanned JPEG with EXIF orientation 5 to 8 is cropped sideways (`CAPTURE-EXIF-SCANNED-ORIENTATION`, filed by Session 58), and the crop, a PNG with no EXIF, is then upright as stored.
> - **Marks are clipped, not re-drawn the same.** The crop's bake is close to a pixel crop of the source's bake, not identical. The known differences, asserted in AC-130.18, correct design §6.5's list (D-486): a rect cut on any side gets a stroke along the crop edge; a pixelate cut on its left or top re-aligns its block grid, and one cut on its right or bottom averages its last partial blocks over the pixels inside; an eraser cut by the crop samples its fill from the ring inside the crop; a clipped arrow draws its head at the crop edge; a text mark whose anchor is outside is dropped even when its glyphs reach inside.
> - **Only saved marks travel.** Marks in an open editor that weren't saved aren't on disk, so they aren't carried.
> - **No `confirm`.** Nothing existing is overwritten or removed, so `crop` isn't in `DESTRUCTIVE_ACTIONS` and the IDE isn't asked.
> - **A crop of a crop works.** The source can be any shot, including one with source `Crop` or `Import`.
>
> **The token estimate,** calibrated against Session 38 `capture-new-marks` and MEU-67 `capture-flatten-backup` (each plan 2 rounds, execution 2) and Session 54 (plan 8,541,302 tokens in 1 round, execution 7,859,970). This session has one MEU through the domain, adapter, service, API, OpenAPI, MCP, the audit plan and the parity fixture, with 29 ACs. Expect 1 to 3 plan rounds (about 8M to 20M) and 1 to 2 execution rounds (about 9M to 18M). The plan loop opens with the default 10.5M. If round 1 costs more than 5.25M, the gate asks Mat for the execution loop's budget (Session 52 RULE-3). The citable AC family is fixed when the plan loop opens: AC-130. At row 0 on 2026-11-09 Mat set the execution loop's budget at 60M tokens (Mat's words: "60M"), with the cap of 6 rounds.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `CROP_REQUEST` | `POST /captures/{id}/crop` takes `CaptureCropIn` (`extra="forbid"`): `x`, `y`, `width` and `height` as `float` with no `ge` or `gt`, `unit` as `Literal["px", "fraction"] \| None`, and `name` as `str \| None`. The service resolves the box with Session 58's `resolve_region(shot.width, shot.height, x, y, width, height, unit or "px")`, so its checks and messages (Session 58 `REGION_ERRORS`, the finite, sign, whole-pixel, fraction, outside and 8 px rows) are the crop's. |
| `CROP_READ` | Under `CAPTURE_FILE_LOCK`, `crop_shot` reads the row (missing: `NotFoundError`, 404) and the source's sidecar (missing: no marks; malformed: `AnnotationValidationError("sidecar is malformed")`, 422). The adapter's `crop` refuses a file whose size differs from the row with `ConflictError` (409) and a file it can't decode with `InboxPathError("the image could not be opened")` (422), neither naming a path. |
| `CROP_PIXELS` | `ImageAnnotatePort.crop(source, box, source_size, out) -> ImageProbe` cuts `box` (`left, top, width, height`) from the original's pixels with no resampling and writes a PNG to `out`. It keeps the mode when PNG stores it (`1`, `L`, `LA`, `P`, `RGB`, `RGBA`, `I;16`), and converts any other mode to RGBA when it has alpha or a `transparency` entry and to RGB otherwise. It keeps the ICC profile and writes no EXIF, XMP or text chunk. A CMYK, YCbCr or LAB source converts through its profile to sRGB with `ImageCms` and carries the sRGB profile; with no profile, or one that builds no transform, it converts plainly to RGB and carries none (D-506). It never calls `exif_transpose` and never reuses `bake(…, [])`. |
| `CROP_NAME` | With no `name`, the crop is `{stem}-crop.png`, then `{stem}-crop_2.png` and on, where `{stem}` is the source's stem cut to 100 characters (IMPORT_NAME's cap) and stripped of trailing ` ._-`, so the longest derived name (`{stem}-crop_NNNN.annotated.webp`, `{stem}-crop_NNNN.png.avkit-tmp`) stays far under Windows' 255-character name limit. A `name` is sanitized (each character outside `[A-Za-z0-9 ._-]` removed, stripped of ` ._-`, a trailing `.png` in any case dropped, its case otherwise kept), must be 1 to 80 characters before and after, may not end in `.annotated`, gets `crop_` before a Windows reserved name, and becomes `{name}.png` with the same suffix rule. A name is free when no entry in the inbox root case-folds to `{stem}` plus any of `SCAN_EXTENSIONS`, `.ann.json`, `.annotated.png`, `.annotated.jpg`, `.annotated.webp` or `.png.avkit-tmp`, and no row's path case-folds equal. Every inbox-root entry that ends in `.avkit-tmp` also takes its name without that suffix, as Session 58's `_import_dest` does (`services/capture.py:549-570`), so a name whose temporary file is in the inbox root is taken and the crop never creates its temporary file over another writer's. The helper is `CaptureService._crop_dest(uow, inbox, stem)`, and its `inbox.iterdir()` runs inside `CROP_CLEANUP`'s `try` (D-476). |
| `CROP_SOURCE` | `CaptureSource.Crop = "Crop"`, after `Import`. The API reports `"Crop"`. No wire map entry and no migration. |
| `MARK_CARRY` | `clip_mark(mark, left, top, width, height) -> tuple[Annotation \| None, MarkCarry]` in `domain/capture.py`, with `MarkCarry = Literal["kept", "clipped", "dropped"]`, matches every `Annotation` member with `assert_never` after the last case. For any marks, kept + clipped + dropped equals their number, and every returned mark is unchanged by `_clamp_annotation(mark, width, height)`. |
| `MARK_CLIP_BOX` | Highlight, pixelate and eraser cover `[x, x+w) × [y, y+h)` (adapter `:136-147`, `:415-416`); a rect's outline covers `[x, x+w] × [y, y+h]` (adapter `:465-471`). Each is moved by `(-left, -top)` and intersected with the crop: `[0, width) × [0, height)` for the first three and `[0, width-1] × [0, height-1]` for a rect. A highlight, pixelate or eraser with zero width or height draws nothing; it is kept when its origin is inside and dropped otherwise. A rect with zero width or height is a line the bake draws, so it takes no shortcut: its inclusive intersection decides like any rect's. Inside: kept. An empty intersection: dropped. Otherwise: clipped to the intersection. |
| `MARK_CLIP_ARROW` | An arrow is moved by `(-left, -top)`. Both ends in the closed `[0, width] × [0, height]`: kept. Otherwise it is clipped with Liang–Barsky against that rectangle; each new end is `floor(v + 0.5)`, clamped to the rectangle. Rejected, or zero length after rounding: dropped. Otherwise: clipped. A clipped arrow never reverses: no component of `to_xy - from_xy` changes sign, though rounding can make one zero. |
| `MARK_CLIP_TEXT` | A text mark is moved by `(-left, -top)` and kept when its anchor is in `[0, width) × [0, height)`; otherwise dropped. It is never clipped. |
| `CROP_BAKE` | With any mark carried, the crop gets a sidecar `{"version": SIDECAR_VERSION, "annotations": annotations_to_wire(marks)}` at `_sidecar_for(crop)` and a bake at `annotated_path_for(crop, fmt)`, with `fmt` from `_annotated_format()`, and the row holds both paths. With none, neither is written. |
| `CROP_CLEANUP` | The whole crop runs under one `CAPTURE_FILE_LOCK` hold with one unit of work, and every filesystem call on the crop's paths runs inside one `try`: `_crop_dest`'s `iterdir`, `ensure_dir`, the source sidecar's read, the temporary file's create, the adapter's `crop`, `os.replace`, `probe`, `_upsert_shot(…, CaptureSource.Crop)`, the sidecar and bake writes, and the commit in the unit of work's `__exit__` (Session 58 RULE-2). The temporary file is `NAME.avkit-tmp`, created with `open("xb")`, and `tmp` is set only once that create succeeds (Session 58 RULE-1). The adapter's `crop` writes the PNG to `tmp` and its return sets `cut`; `os.replace(tmp, crop)` sets `moved`. On any exception the `except` removes `tmp` when it is set, and, only when `moved` is true, the crop, `_sidecar_for(crop)` and every `annotated_path_for(crop, fmt)`: `CROP_NAME` found each of those free under this same hold, so any of them that exists is the crop's. It removes no file this crop didn't create, so a `NAME.avkit-tmp` another writer left is never written over or removed. A `ValidationError`, `NotFoundError`, `ConflictError`, `AnnotationValidationError` or `InboxPathError` raised while `cut` is false is a refusal and is re-raised unchanged after that cleanup; each names no path, because the adapter's `crop` raises only its two fixed refusals. Every other exception, and every exception once `cut` is true, commits no row and raises `CaptureFailedError("the crop could not be written")` (503) (D-476, refining D-490). |
| `CROP_RESPONSE` | 201 with `CaptureCropOut`: `item` (the new shot), `source_id`, `requested` (`x`, `y`, `width`, `height` as sent, `unit` defaulting to `"px"`), `applied` (`x`, `y`, `width`, `height` in px), `clamped`, and `marks` (`kept`, `clipped`, `dropped`). No image bytes. |
| `CROP_MCP` | MCP `crop` is a `.strict()` member of `avkit_capture`, sent as `POST /captures/{id}/crop` with the box in the body and `ADD_TIMEOUT_MS`. It isn't destructive and asks no user confirmation. Its description is design §6.7's. `ACTION_INDEX` gains one row after `revert`, so 71 rows, and `avkit_capture` has 11 actions. |
| `BASELINE_PENDING` | Under D-499 A: `coverage.test.ts` lists `["avkit_capture.crop"]`, and AC-68.5 asserts the baseline misses exactly those keys, each in `ACTION_SET` and absent from the baseline, and has no extra key. |
| `NO_RAW_CONSOLE` | No new log line is added. The only lines a crop reaches are the existing `capture.registered` (`shot_id`, `source`) and `capture.wrote`, whose `path` field the Console processor drops. No refusal message names a path, and no `probe` message, which does (`adapter.py:256`, `:262`), reaches a response. |

### Mark carry: domain (D-485 to D-488)

`packages/core/src/avkit_core/domain/capture.py` (CRLF) gains, after the `Annotation` union (`:262-269`):

```python
MarkCarry = Literal["kept", "clipped", "dropped"]


def clip_mark(
    mark: Annotation, left: int, top: int, width: int, height: int
) -> tuple[Annotation | None, MarkCarry]:
    """MARK_CARRY: move a saved mark into a crop's frame and clip it to the crop (MEU-130)."""
```

`clip_mark` and `MarkCarry` join `__all__`. It uses `match` with one `case` per member and `assert_never(mark)` after the last, as `domain/tts.py:133` does (D-406's "every mark type on `main`" becomes a type error when a member is added without a rule). It returns a new frozen mark with `dataclasses.replace`, never mutates its input, and needs no service.

The box rule, for highlight, pixelate and eraser:

```python
x0, y0 = mark.x - left, mark.y - top
x1, y1 = x0 + mark.width, y0 + mark.height
if mark.width == 0 or mark.height == 0:
    inside = 0 <= x0 < width and 0 <= y0 < height
    return (replace(mark, x=x0, y=y0), "kept") if inside else (None, "dropped")
if x0 >= 0 and y0 >= 0 and x1 <= width and y1 <= height:
    return replace(mark, x=x0, y=y0), "kept"
cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, width), min(y1, height)
if cx0 >= cx1 or cy0 >= cy1:
    return None, "dropped"
return replace(mark, x=cx0, y=cy0, width=cx1 - cx0, height=cy1 - cy0), "clipped"
```

A rect uses the same steps on its inclusive outline, without the zero-size shortcut: inside when `x0 >= 0`, `y0 >= 0`, `x1 <= width - 1` and `y1 <= height - 1`; clipped to `min(x1, width - 1)` and `min(y1, height - 1)`; dropped when `cx0 > cx1` or `cy0 > cy1`. A rect with zero width or height is a line: `draw.rectangle([x, y, x, y + h])` paints its column (`adapter.py:471`). So a zero-width rect at `x = 20` from `y = 0` to `40`, under a crop at `(10, 10)` sized 30×30, is clipped to the column at `x = 10` from `y = 0` to `29`, not dropped, which the shortcut for the other three kinds would do. With the half-open rule a rect cut on its right would draw its right stroke at column `width`, outside the crop, and show `stroke_width - 1` columns (D-486).

The arrow rule clips `from_xy → to_xy` against `[0, width] × [0, height]` with Liang–Barsky, as `C:/Temp/av-kit/s59-plan-probes.txt` checks for eleven cases on a 100×50 crop: both inside and on the left edge are kept; a tail left, a head right, a diagonal through (ends `(7.14, 0)` and `(92.86, 50)`, rounded to `(7, 0)` and `(93, 50)`), on the top edge, a corner graze, one entering at a corner and a sliver along the bottom are clipped; one outside and one touching only a corner (zero length) are dropped. The closed rectangle matches `_clamp_annotation`'s `_clamp_int(v, 0, width)`, so a clipped arrow is a fixed point of the clamp.

### Crop: adapter, service and route (D-481 to D-484, D-489 to D-491)

- **`domain/enums.py` (CRLF).** `CaptureSource` gains `Crop = "Crop"` after `Import`. No migration: the column stores `.name` (09 `:282`). No `REGISTER_SOURCE_WIRE_MAP` entry: a crop doesn't go through `register`. 09 `:1029` says "wire `crop`"; D-484 corrects it.
- **`domain/capture.py`.** A frozen `CropResult` dataclass: `shot`, `source_id`, `requested` (`x`, `y`, `width`, `height` floats and `unit`), `applied` (`left`, `top`, `width`, `height` ints), `clamped`, `kept`, `clipped`, `dropped`.
- **`ports/capture.py` (CRLF).** `ImageAnnotatePort` (`:18-33`) gains `crop(self, source: Path, box: tuple[int, int, int, int], source_size: tuple[int, int], out: Path) -> ImageProbe`.
- **`packages/infrastructure/src/avkit_infra/capture/adapter.py` (CRLF).** `CaptureAdapter.crop`:
  1. Opens and loads the file inside one `try` that catches `Exception`, as `view` does (`adapter.py:297-304`): Pillow raises `SyntaxError`, `ValueError` and others for a damaged file, and an `OSError`'s text holds the path (Session 58 RULE-2). Any such failure raises `InboxPathError("the image could not be opened")` (D-476).
  2. If `image.size != source_size`, it raises `ConflictError("the image file changed since the captures were listed; list them again and retry")` (409), Session 58's message.
  3. Calls `image.crop((left, top, left + width, top + height))` on the image step 1 loaded. The box is inside the image, because `resolve_region` clamped it, so Pillow never pads (`s59-plan-probes.txt`: a crop past the edge pads with black).
  4. Keeps the mode in `1, L, LA, P, RGB, RGBA, I;16`, else converts to RGBA when the source has alpha or `transparency` and to RGB otherwise. A `P` crop keeps its palette and `transparency`.
  5. Saves PNG to `out` with `icc_profile=image.info.get("icc_profile")` and no `pnginfo`, `exif` or `xmp`. Plan-time probe: a crop saved this way keeps only `icc_profile` and drops `Comment` text and EXIF (`s59-plan-probes.txt`).
  6. Returns `probe(out)`. A failure of step 5's save or of this probe is raised as `OSError("the crop could not be saved")`, which names no path, so the only refusals `crop` raises are steps 1 and 2 (D-476).
- **`services/capture.py` (CRLF).** `crop_shot(shot_id, *, x, y, width, height, unit=None, name=None) -> CropResult`:
  1. `CROP_NAME`'s `name` checks first, with no lock, raising `ValidationError` (422) with: `name must be 1 to 80 characters`; `name has no usable characters; use letters, digits, space, dot, underscore or hyphen`; `name may not end in .annotated`.
  2. Under `CAPTURE_FILE_LOCK` (not reentrant, so the save is inlined, not `annotate_and_save`) with one unit of work: `CROP_READ`; `resolve_region`; the marks through `clip_mark`, counting each result; `ensure_dir(inbox)`; the name; then the steps of `CROP_CLEANUP` and `CROP_BAKE`.
  3. The `try` encloses the whole unit of work, including the commit in its `__exit__` (`packages/infrastructure/src/avkit_infra/database/unit_of_work.py:54-65`), as Session 58's `_import_copy` does (`services/capture.py:512-546`), and keeps `CROP_CLEANUP`'s `tmp`, `cut` and `moved`. Its `except Exception` removes only what this crop created, with `_unlink_if_file` (`:1145`): `tmp` when set, and the crop, `_sidecar_for(crop)` and every `annotated_path_for(crop, fmt)` only when `moved`. A refusal raised while `cut` is false is re-raised unchanged; anything else raises `CaptureFailedError("the crop could not be written")` (503, unlogged, `internal_error`) (D-476).
  4. `get_shot` and `load_shot_annotations` (`:385-404`) take no lock (`expire_stale_requests` uses only a unit of work), so `crop_shot` reads the row and sidecar itself inside its lock, through `annotations_from_sidecar` and `_sidecar_for`.
- **`packages/api/src/avkit_api/schemas/captures.py` (CRLF).** `CaptureCropIn(ApiModel)`, `CaptureCropRequestedOut`, `CaptureCropAppliedOut`, `CaptureCropMarksOut` and `CaptureCropOut`. `CaptureShotOut.source` is a `str`, so the OpenAPI enum doesn't change.
- **`packages/api/src/avkit_api/routes/captures.py` (CRLF).** `POST /captures/{id}/crop`, `status_code=201`, after the `revert` route. It maps `CropResult` to `CaptureCropOut`. Route count 73 → 74.

`scan_inbox` takes `CAPTURE_FILE_LOCK` (`services/capture.py:312`), and `.avkit-tmp` is outside `SCAN_EXTENSIONS`, so a scan never sees a crop before its row exists. If it did, `_upsert_shot` lets the registering source win (`:861-866`), so the row would still read `Crop`. AC-130.20 races a scan thread against the crop.

### Crop: MCP and the audit plan (D-492, D-493, D-499)

- **`mcp-server/src/toolsets/capture.ts` (CRLF).** A new member after `revert` (`:193-195`):

  ```ts
  withDesc("crop", z.object({
    action: z.literal("crop"),
    id: captureId,
    x: z.number().nonnegative(),
    y: z.number().nonnegative(),
    width: z.number().positive(),
    height: z.number().positive(),
    unit: z.enum(["px", "fraction"]).optional(),
    name: z.string().min(1).max(80).optional(),
  }).strict())
  ```

  `captureDescriptions` (`:33-44`) gains `crop`: "Writes the region as a NEW shot (PNG) and returns its id and paths; the source is never changed. Same coordinates as image. A box past the edge is clamped and `applied` reports what was cut. Saved marks are carried over and clipped. Like ImageMagick `-crop WxH+X+Y +repage`, without the virtual canvas." `desc()` keeps the M7 markers. The zod bounds are a first filter; the API's messages stay the contract.
- **`mcp-server/src/toolsets/registry.ts` (CRLF).** `ACTION_INDEX` gains `{ tool: "avkit_capture", action: "crop", method: "POST", path: "/captures/{id}/crop" }` after `revert` (`:132`) and before the MEU-62 comment and `download_asset` (`:133-134`). The timeout branch (`:335-340`) gains `|| (tool === "avkit_capture" && action === "crop")` for `ADD_TIMEOUT_MS`. `httpBody` forwards `x`, `y`, `width`, `height`, `unit` and `name`; row 4b checks whether it needs a new key, and Session 58's `QUERY_GET_ONLY` keeps them out of the path.
- **`mcp-server/src/destructive.ts`** is unchanged.
- **`mcp-server/scripts/audit/plan.ts` (CRLF).** A `simpleStep` `capture.crop` after `capture.revert` (`:1559-1574`, `depends_on: ["capture.flatten"]`) and before `capture.capture_interactive` (`:1575`). Args `{ action: "crop", id, x: 0, y: 0, width: 8, height: 8 }`. It registers the new id with `ctx.ledger.register("capture", id)` (pattern `:1445`), so the audit's cleanup removes it, and observes source `"Crop"` and the source's SHA-256 unchanged.
- **`mcp-server/tests/audit/coverage.test.ts` (D-499).** Under A, `BASELINE_PENDING` and the amended AC-68.5. Under B or C, AC-68.5 is amended as the ruling says.
- **The parity fixture (D-493).** `tools/capture_bake_fixture.py` appends crop cases to `region_cases()` (`:126`) with `random.Random(REGION_SEED + 1)`, so the existing cases' bytes don't change. Each case is the crop's own pixels and the wire marks `clip_mark` returns, named `crop-pixelate-sliver`, `crop-pixelate-corner`, `crop-eraser-edge` and `crop-eraser-ring`. Row 5 regenerates `ui/tests/e2e/fixtures/capture-region-pass.json` with `python tools/capture_bake_fixture.py --out ui/tests/e2e/fixtures --region`. `ui/tests/unit/capture-region-pass.test.ts` adds the names to `PIXELATE_CASES` (`:34`, checked by `toEqual` at `:105`) and `ERASER_CASES` (`:148`, `:154`). AC-90.8 (`tests/unit/test_capture_bake_fixture.py:87`, `:126`) checks that the committed fixture reproduces.

### Pins that move

| Pin | Where | From → to | Row |
|---|---|---|---|
| `ACTION_INDEX` length | `mcp-server/tests/action-index.test.ts:41`, `audit/coverage.test.ts:17-20`, `capture.test.ts:106`, `convert.test.ts:56`, `m7-resource.test.ts:47`, `:53`, `:65`, `:71` | 70 → 71 | 4b |
| Served actions from the built server | `mcp-server/tests/audit/runner-fake-backend.test.ts:76` (`summary.discovery.actions`, read from `dist/index.js`, `:12`), so row 5 and the gate build `dist` before the MCP tests | 70 → 71 | 4b |
| `avkit_capture` actions | `capture.test.ts:124`, and a `CAPTURE_ACTIONS` row (`:23-35`) | 10 → 11 | 4b |
| Route index | `tests/e2e/test_api_openapi.py` `ROUTE_INDEX` gains `("POST", "/api/v1/captures/{id}/crop")` after `revert`; its length check (`:113`) | 73 → 74 | 4a |
| Route and action counts | `tests/e2e/test_api_downloads.py` `ROUTE_COUNT_AFTER` (`:372`) and `ACTION_INDEX_AFTER` (`:374`) | 73 → 74, 70 → 71 | 4a |
| Valid bodies | `tests/e2e/test_api_bodies.py` `_valid_body` (`:13`) gains the crop path → `{"x": 0, "y": 0, "width": 8, "height": 8}`, so AC-16.9's extra key is the request's only fault | new entry | 4a |
| `CaptureSource` members | `CAPTURE_SOURCE_MEMBERS` (`tests/unit/test_domain_capture.py:18-25`), `tests/unit/test_domain.py:298-305`, `SOURCE_OUT` (`tests/e2e/test_api_captures.py:93-100`) | gains `Crop` after `Import` | 2 |

Row 0 re-reads every line here after Session 58, which adds `Import` to the three member tuples and may move the others.

### Where values go (Session 50 RULE-1, Session 53 RULE-1; D-496)

- **The box and the counts** are numbers. They go into the response. They are never logged.
- **A `name`** is the caller's own text. It becomes the crop's file name and `display_name` only after `CROP_NAME` sanitizes it; no message repeats it. This is Session 53 RULE-1's one target, and AC-130.15 pins it.
- **The source's stem** is already a file name in the inbox; it is reused only as `{stem}-crop`.
- **Saved marks** are copied from the source's sidecar into the crop's. A text mark's `text` is the user's own and goes only into the sidecar and bake, as today.
- **`capture.registered`** logs `shot_id` and `source` (`services/capture.py:894`) on insert. Neither is a path.
- **`capture.wrote`** (`adapter.py:366`) logs `path`, `width` and `height` when the bake writes. `path` isn't in `CONSOLE_FIELDS` (`packages/core/src/avkit_core/services/health.py:47-56`), so the processor drops it once a HealthService is built.
- **A 503** is answered as `internal_error` and isn't logged (`packages/api/src/avkit_api/errors.py:138-149`). A 4xx carries only its fixed message.
- **AC-130.22** proves the list through `build_services`, with HealthService built first (Session 54 RULE-2) and the D-391 reset.

### Spec text (D3)

| File | Lines at `8bcb4a6` | Change |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | `:282` | `CaptureSource` gains `Crop` |
| | the MCP action table (`:577-578` area) | A `crop` row: POST, the box, not destructive |
| | `:1029` | Source: `Crop`, with no wire value (D-484) |
| | `:1030` | Marks: the rect clips on its inclusive outline; the arrow's ends round half up (D-486, D-487) |
| | `:1032` | Tests: the known differences as corrected (D-486); the parity cases (D-493) |
| | after `:1032` | A Delivered note naming the mechanism ids, the ACs and this plan folder |
| `docs/build-plan/00-overview.md` | `:68` | `CaptureSource` gains `Crop` |
| `docs/build-plan/05-mcp-server.md` | the `avkit_capture` action list | `crop`, with the 11-action count and any 70-row count found by `grep` |
| | Session 58's §6.6 table | The crop rows of design §6.6 |
| | the capture lifecycle text | A crop is a new shot; the source is never changed |
| | after Session 58's Delivered note | A Session 59 Delivered note: `CROP_MCP`, `BASELINE_PENDING` under A |

Row 6 re-reads each anchor before it writes (Session 51 RULE-3), after Session 58 moved them, and cites the lines as they read then. `09` and `05` are CRLF, and `00` is LF.

### MEU-130 `capture-crop-copy`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `POST /captures/{id}/crop` body | `schemas/captures.py` `CaptureCropIn` | `x`, `y`, `width`, `height` `float`; `unit` `px \| fraction \| null`; `name` `str \| null`; the domain and service check the rest | `extra="forbid"` |
| Box → applied | `domain/capture.py` `resolve_region` (Session 58) | Session 58 `REGION_ERRORS` | — |
| `name` → file name | `services/capture.py` `crop_shot` | `CROP_NAME` | — |
| Mark → clipped mark | `domain/capture.py` `clip_mark` | `MARK_CLIP_BOX`, `MARK_CLIP_ARROW`, `MARK_CLIP_TEXT` | — |
| Pixels → PNG | `adapter.py` `crop` | The file's size must equal the row's | — |
| `CaptureSource.Crop` | `domain/enums.py` | `.name` stored and returned | — |
| 201 body | `schemas/captures.py` `CaptureCropOut` | `CROP_RESPONSE` | — |
| MCP `crop` | `capture.ts` | x, y ≥ 0; width, height > 0; unit enum; name 1 to 80 | `.strict()` |

#### Acceptance Criteria

Pytest names are `test_ac_130_<n>_…`, and Vitest titles start `AC-130.<n>`. AC-130.1 to .4, .6 and .7 go in `tests/unit/test_domain_capture.py`; .5 in `tests/unit/test_capture_service.py`; .8 to .11 in `tests/unit/test_capture_adapter.py`; .12 to .22 in the new `tests/e2e/test_api_capture_crop.py` (LF); .23 to .26 in `mcp-server/tests/capture.test.ts`; .27 and .28 in `mcp-server/tests/audit/coverage.test.ts`; .29 in `ui/tests/unit/capture-region-pass.test.ts`. The e2e tests use the real stack in AC-84.2's shape (`tests/e2e/test_api_captures.py:1009-1049`): `build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")`, `create_app(…)`, a `TestClient`, and `PUT /api/v1/settings/capture` with `inbox_dir`. They create shots through Session 58's `mode: import` or by `GET /captures` after writing into the inbox, and marks through `POST /captures/{id}/annotate`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-130.1 | unit | `MARK_CLIP_BOX` inside, parametrized over rect, highlight, pixelate and eraser: a mark fully inside a crop at `(100, 50)` sized 200×100 returns `"kept"`, moved by `(-100, -50)`, every other field equal | Local Canon: 09 `:1030`; D-486 | Yes: Red, the stub returns the mark unmoved |
| AC-130.2 | unit | `MARK_CLIP_BOX` partial, parametrized over the four kinds and the four sides, plus a corner: the clipped box is the intersection, `"clipped"`; for a rect the right and bottom clip to `width - 1` and `height - 1`, for the others to `width` and `height`; a box wholly outside returns `(None, "dropped")`; a zero-width highlight, pixelate or eraser with its origin inside is `"kept"`, and one with its origin outside is `"dropped"`; a zero-width rect and a zero-height rect that each cross the crop from outside are `"clipped"` to the part of their line inside (the vertical case is `(20, 0, 0, 40)` under a crop at `(10, 10)` sized 30×30, giving `(10, 0, 0, 29)`), and the same rects wholly outside are `"dropped"` | Local Canon: 09 `:1030`; D-486 | Yes: Red, the stub keeps every mark |
| AC-130.3 | unit | `MARK_CLIP_ARROW`, the eleven probe cases on a 100×50 crop at `(0, 0)`: both inside and on the left edge kept; tail left, head right, diagonal through (`(7, 0)` to `(93, 50)`), on the top edge, corner graze, entering at a corner and the bottom sliver clipped to the Liang–Barsky ends rounded half up; outside and touching only a corner (zero length) dropped. A clipped arrow never reverses: no component of `to_xy - from_xy` changes sign, though one may become zero (the bottom sliver's `(0, 49.85)` to `(1.82, 50)` rounds to `(0, 50)` to `(2, 50)`), and each end is within 0.5 of its exact Liang–Barsky end on each axis | Research-backed: design D-7; D-487; `s59-plan-probes.txt` | Yes: Red, the stub |
| AC-130.4 | unit | `MARK_CLIP_TEXT`: an anchor at `(0, 0)` and at `(width - 1, height - 1)` is kept and moved; an anchor at `x = width` or `y = -1` is dropped, even with a long text | Local Canon: 09 `:1030`; D-488 | Yes: Red, the stub keeps it |
| AC-130.5 | unit | `MARK_CARRY` invariant, over 500 marks from `random.Random(130)` across every kind, crops and positions inside, across and outside: counts sum to the input; every returned mark equals `service._clamp_annotation(mark, width, height)` for the service from the module's `_stack(tmp_path)` (`tests/unit/test_capture_service.py:108-129`; the method is an instance method, `services/capture.py:917`); no input is mutated | Local Canon: D-485; 09 `:1030` | Yes: Red, the clamp moves the stub's unmoved marks |
| AC-130.6 | unit | Every member of `typing.get_args(Annotation)` has a case: one instance of each, wholly inside a crop at `(5, 5)`, comes back `"kept"` and moved by `(-5, -5)`, and no member raises | Local Canon: grouping D-406; D-485 | Yes: Red, the stub returns each mark unmoved |
| AC-130.7 | unit | `"Crop" in CaptureSource.__members__` and it is the last member, both asserted before `CaptureSource.Crop.value == "Crop"` is read | Local Canon: 09 `:1029`; D-484 | Yes: Red, no member |
| AC-130.8 | unit | `CROP_PIXELS`: `crop` of a 64×48 PNG with distinct pixels, box `(10, 8, 20, 16)`, writes a PNG that decodes exactly to `image.crop((10, 8, 30, 24))`; the corners and centre are checked by value | Local Canon: 09 `:1027`; AC-40.26 | Yes: Red, the stub writes nothing |
| AC-130.9 | unit | Modes: a crop of a `1`, `L`, `LA`, `P` with `transparency`, `RGB`, `RGBA` and `I;16` PNG keeps the mode; a `.jpg` source gives an RGB PNG equal to the decoded crop; a `.webp` with alpha gives RGBA | Local Canon: D-482 | Yes: Red, the stub |
| AC-130.10 | unit | Metadata: a source PNG with an ICC profile, EXIF and a `Comment` text chunk gives a crop with the same `icc_profile`, no `exif`, and no text. Amended by D-506: a CMYK JPEG with a profile gives an RGB crop whose pixels are the profile's conversion to sRGB and whose `icc_profile` is sRGB's; with no profile, or a profile that builds no transform, the crop is the plain RGB conversion with no profile | Local Canon: 09 `:1027`; D-482; Human-approved: D-506 | Yes: Red, the stub |
| AC-130.11 | unit | A `source_size` of `(100, 80)` on a 64×48 file raises `ConflictError` whose message holds no part of the path, and `out` doesn't exist; a `.png` that holds text raises `InboxPathError("the image could not be opened")` | Local Canon: D-481 | Yes: Red, `DID NOT RAISE` |
| AC-130.12 | e2e | `CROP_RESPONSE` and `CROP_SOURCE`: a crop of a 200×100 PNG returns 201 with `item.source` `"Crop"`, `source_id`, `requested` with `unit` `"px"`, `applied`, `clamped` `false` and `marks` all 0. The source's bytes, `st_mtime_ns`, sidecar and row are unchanged, and `GET /captures` lists both shots once | Local Canon: 09 `:1026`, `:1031` | Yes: Red, 404 |
| AC-130.13 | e2e | D-401 parity on a 3000×1500 PNG with distinct pixels, parametrized over a px box, a fraction box, a box clamped at the right edge, an 8×8 box and a 2800×1400 box: `applied` equals `GET image`'s `X-Capture-Region` with the same box in every case. Where `applied`'s long edge is 64 to 2576 (the first three, each with a long edge of at most 1600, so the view stays far under `IMAGE_MAX_BYTES`), the crop's pixels equal `GET image` with `max_edge` set to that long edge. For the 8×8 and 2800×1400 boxes, which the view must scale, the crop's pixels equal the source's own pixels at `applied` | Local Canon: grouping D-401; 09 `:1025`; Session 58's `max_edge` bounds | Yes: Red, 404 |
| AC-130.14 | e2e | On an all-white 120×80 PNG, a box past each edge and past a corner returns `clamped` `true`, `applied` inside the image, and a crop with no black pixel | Local Canon: 09 `:1032` | Yes: Red, 404 |
| AC-130.15 | e2e | `CROP_NAME`: two crops of `shot.png` give `shot-crop.png` and `shot-crop_2.png`; with `shot-crop.ANN.JSON` already present the next is `_3`; `name: "a/b c#!.PNG"` gives `ab c.png`; `name: "CON"` gives `crop_CON.png`; `name: "#!"`, an 81-character name and `x.annotated` each return 422 with the fixed message; a shot whose file name has a 240-character stem crops with no `name` to a 201 whose crop stem is that stem's first 100 characters plus `-crop` | Local Canon: 09 `:1028`; D-483 | Yes: Red, 404 |
| AC-130.16 | e2e | Errors through the envelope: an unknown id 404; an extra key and a missing `height` 422 `validation_error`; Session 58's `outside`, `under-8` and `px-fraction` messages 422; a malformed source sidecar 422 `sidecar is malformed`; a source file replaced by a different size 409 with no path | Local Canon: D-481 | Yes: Red, 404 |
| AC-130.17 | e2e | `CROP_BAKE`: a source with one rect inside, one arrow across the edge and one text outside returns `marks` `{kept: 1, clipped: 1, dropped: 1}`; the crop's sidecar holds the two clipped marks in `clip_mark`'s output; its bake exists in the configured format; `GET image?variant=annotated` returns it. A source with no marks gives a crop with no sidecar or bake and both paths null | Local Canon: 09 `:1030`; D-489 | Yes: Red, 404 |
| AC-130.18 | e2e | The known bake differences (D-486), each asserted on a region of the crop's bake: a rect cut on each side shows its stroke along that crop edge; a pixelate cut on its left re-aligns its grid; an eraser cut by the crop fills with the ring colour inside the crop; a clipped arrow's head pixels lie at the crop edge; a text mark whose anchor is outside leaves no text pixels | Local Canon: design §6.5, as corrected by D-486 | Yes: Red, 404 |
| AC-130.19 | e2e | Redaction survives. A pixelate cut by the crop, on a 1 px black-and-white checkerboard, leaves no pixel inside its clipped box in the crop's bake equal to the crop's original pixel there; the box is chosen so every partial block is at least 2×2. An eraser cut by the crop, on a checkerboard interior inside a ring of one colour, fills its whole clipped box in the crop's bake with that ring colour, so no checkerboard pixel is left | Local Canon: 09 `:1032`; design §6.5 | Yes: Red, 404 |
| AC-130.20 | e2e | Scan race: with a thread calling `scan_inbox` in a loop while 10 crops run, each crop's row reads `Crop`, no row holds a `.avkit-tmp` path, and `GET /captures` lists each crop once | Local Canon: 09 `:1032`; D-490 | Yes: Red, 404 |
| AC-130.21 | e2e | `CROP_CLEANUP`, parametrized over four faults patched inside `monkeypatch.context()` and lifted before the follow-up list: `os.replace` raising `OSError`; `probe` on the crop raising `InboxPathError` with the path in its message; `bake` raising `OSError`; `SqlAlchemyUnitOfWork.commit` raising `RuntimeError` once the crop exists. Each returns 503 `internal_error` with no part of the path; the inbox holds the same names as before; no row is added; the source is unchanged. A second test, `keeps a temporary file it did not write`, first writes `shot-crop.png.avkit-tmp` holding another writer's bytes and is parametrized over `none`, `race` (`CaptureService._crop_dest` patched to return `shot-crop.png`), `replace` (`os.replace` raising `OSError` for the crop) and `commit` (`SqlAlchemyUnitOfWork.commit` raising `RuntimeError`): `none` returns 201 with `shot-crop_2.png`; each other case returns 503 `internal_error` with no part of the path, no row added and the inbox names unchanged; in every case that file keeps its bytes (Session 58 AC-129.9, `tests/e2e/test_api_capture_region_import.py:627`). A third test registers a source PNG, then damages its IDAT chunk in place, keeping its header and size, so Pillow raises `SyntaxError` or `ValueError`: 422 `the image could not be opened`, with no part of the path, no row added and the inbox names unchanged | Local Canon: D-490; D-476 | Yes: Red, 404 |
| AC-130.22 | e2e | `NO_RAW_CONSOLE`: with `HealthService._active` reset (D-391) and `build_services` into folders whose names hold a marker, one test crops a shot with marks, crops with a `name`, and triggers one name 422 and one box 422. No line of `capfd`'s stdout or stderr, the ring's messages, `console.log` or the error messages holds the marker, case-folded. Positive controls: a stdout `engine.created` line; the ring gains at least one `capture.registered` entry between the moment before the first crop and the moment after the last (HealthService keeps only `CONSOLE_FIELDS`, so the ring holds the event name, not `source`, `health.py:47-56`, `:207-234`); and each crop's response has `item.source` `"Crop"`. `CONSOLE_FIELDS` is not widened | Local Canon: Session 50 RULE-1; Session 54 RULE-2; D-496 | Yes: Red, no `Crop` line |
| AC-130.23 | unit (MCP) | `crop` with the box, `unit` and `name` sends them as the POST body to `/captures/{id}/crop`, with no query string, and with `ADD_TIMEOUT_MS` | Local Canon: D-492 | Yes: Red, zod refuses `crop` |
| AC-130.24 | unit (MCP) | zod: a fraction box with `name` parses; `x: -1`, `width: 0`, `unit: "inch"`, `name: ""`, an 81-character `name` and an extra key are each refused | Local Canon: Boundary Inventory | Yes: Red, the accept case |
| AC-130.25 | unit (MCP) | The `crop` description holds `NEW shot`, `never changed`, `applied`, `clipped` and `-crop WxH+X+Y +repage`, and keeps at least three M7 markers; the advertised schema lists the six fields; `crop` is in neither `DESTRUCTIVE_ACTIONS` nor the user-confirm set | Research-backed: design §6.7 (R-8); D-494 | Yes: Red, the text is absent |
| AC-130.26 | unit (MCP) | `ACTION_INDEX` has 71 rows, the `crop` row directly after `revert`, and `avkit_capture` 11 actions | Local Canon: D-492 | Yes: Red, 70 |
| AC-130.27 | unit (MCP) | `AUDIT_PLAN` has a `capture.crop` step after `capture.revert`, depending on `capture.flatten`, with the 8×8 box and a ledger registration | Local Canon: D-492 | Yes: Red, no step |
| AC-130.28 | unit (MCP) | Under D-499 A: AC-68.5's `baselineCoverage` returns `missing` equal to `BASELINE_PENDING` and `extra` empty; each pending key is in `ACTION_SET` and not in the baseline; a pending key that is in the baseline fails a helper check | Human: D-499 | Yes: Red, `missing` is empty |
| AC-130.29 | unit (UI) | The fixture's region cases include the four crop cases, and the renderer's region pass matches Pillow on each, through the existing `PIXELATE_CASES` and `ERASER_CASES` checks | Local Canon: 09 `:1032`; D-493 | Yes: Red, the case lists differ |

Guards that run unchanged in rows 3 and 5: AC-37.x and AC-84.2 in `tests/e2e/test_api_captures.py`, Session 58's region-view and import ACs, AC-38.x, AC-67.x, AC-90.8 (once row 5 regenerates the fixture), the existing parity cases and the M7 resource tests.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Request and box rules | Human-approved and Local Canon | 09 `:1025`; design D-2; Session 58 |
| New shot, source untouched | Human-approved | design D-1 |
| Exact pixels, PNG, metadata | Local Canon, detailed | 09 `:1027`; D-482 |
| Name rules | Local Canon and Inferred | 09 `:1028`; D-483 |
| `Crop` with no wire value | Local Canon, corrected | 09 `:1029`; D-484 |
| Mark clipping rules | Local Canon, detailed | 09 `:1030`; D-485 to D-488 |
| Rect on its inclusive outline | Inferred, flagged | D-486 |
| Arrow end rounding | Inferred, flagged | D-487 |
| Sidecar and bake | Local Canon | 09 `:1030`; D-489 |
| Cleanup and 503 | Inferred, flagged | D-490, Session 58 D-418's shape as its execution corrected it; D-476 |
| Response | Research-backed | 09 `:1031`; design §6.3 |
| Audit baseline | Human | D-499 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/capture.py` | Modify | `MarkCarry`, `clip_mark`, `CropResult` |
| `packages/core/src/avkit_core/domain/enums.py` | Modify | `CaptureSource.Crop` |
| `packages/core/src/avkit_core/ports/capture.py` | Modify | `crop` |
| `packages/core/src/avkit_core/services/capture.py` | Modify | `crop_shot`; the reserved-name set lifted to a module constant if Session 58 inlined it |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | Modify | `crop` |
| `packages/api/src/avkit_api/routes/captures.py` | Modify | The crop route |
| `packages/api/src/avkit_api/schemas/captures.py` | Modify | `CaptureCropIn`, `CaptureCropOut` and its parts |
| `openapi.committed.json` | Regenerate | §S6 |
| `mcp-server/src/toolsets/capture.ts` | Modify | The `crop` member and description |
| `mcp-server/src/toolsets/registry.ts` | Modify | The `ACTION_INDEX` row, the timeout branch |
| `mcp-server/scripts/audit/plan.ts` | Modify | The `capture.crop` step |
| `tools/capture_bake_fixture.py` | Modify | The crop cases |
| `ui/tests/e2e/fixtures/capture-region-pass.json` | Regenerate | The crop cases |
| `tests/unit/test_domain_capture.py` | Modify | AC-130.1 to .4, .6, .7, the members tuple |
| `tests/unit/test_domain.py` | Modify | The `CaptureSource` tuple |
| `tests/unit/test_capture_service.py` | Modify | AC-130.5 |
| `tests/unit/test_capture_adapter.py` | Modify | AC-130.8 to .11 |
| `tests/e2e/test_api_openapi.py`, `tests/e2e/test_api_bodies.py`, `tests/e2e/test_api_downloads.py` | Modify | Route pins |
| `tests/e2e/test_api_captures.py` | Modify | `SOURCE_OUT` |
| `tests/e2e/test_api_capture_crop.py` | New | AC-130.12 to .22 |
| `mcp-server/tests/capture.test.ts` | Modify | AC-130.23 to .26, the action count |
| `mcp-server/tests/action-index.test.ts`, `convert.test.ts`, `m7-resource.test.ts`, `audit/runner-fake-backend.test.ts` | Modify | 70 → 71 |
| `mcp-server/tests/audit/coverage.test.ts` | Modify | AC-130.27, .28, the 70 → 71 pin, `BASELINE_PENDING` under A |
| `ui/tests/unit/capture-region-pass.test.ts` | Modify | AC-130.29 case names |
| `docs/build-plan/09-screenshot-capture.md`, `00-overview.md`, `05-mcp-server.md` | Modify | §Spec text |

No test id is added, so `ui/tests/e2e/test-ids.ts` isn't touched (S9). No renderer source file changes. Line endings at `8bcb4a6` (`C:/Temp/av-kit/s59-plan-probes.txt`): CRLF are `domain/capture.py`, `enums.py`, `ports/capture.py`, `services/capture.py`, `adapter.py`, `routes/captures.py`, `schemas/captures.py`, `openapi.committed.json`, `capture.ts`, `registry.ts`, `plan.ts`, the Python test files above except `test_api_bodies.py`, the MCP and UI test files, `tools/capture_bake_fixture.py`, the fixture JSON, `09`, `05` and the grouping. LF are `tests/e2e/test_api_bodies.py`, `00`, `meu-status.yaml` and the register. Row 0 measures every file again with Python bytes, and every row writes with `newline=""`. New files are LF. Two regenerated files are written by their commands, not by a row: `tools/export_openapi.py` writes with `write_text` and no `newline` (`:66`), so `openapi.committed.json` stays CRLF; `tools/capture_bake_fixture.py` writes the region fixture with `newline="\n"` (`:217`), so its working copy becomes LF. Git stores both as LF (`.gitattributes` `* text=auto`; `git ls-files --eol` reads `i/lf w/crlf`), so the fixture's LF working copy changes nothing git records, and row 5 checks that `git ls-files --eol` still reads `i/lf` for it and that `git diff` shows only the added cases. The generator isn't changed to write CRLF. The region PNG pair the same command rewrites (`capture-region-original.png`, `capture-region-annotated.png`) must stay byte-identical, which row 5 checks with `git diff --quiet`.

### Project files

- `docs/execution/plans/2026-11-08-capture-crop-copy/`: `implementation-plan.md`, `task.md`, `human-gate-decision.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `issue-file.py`, `session-gate.ps1`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, `.agent/context/known-issues.yaml` and `.agent/context/known-issues.md` (under D-499 A), `.agent/context/triage-output.yaml`, and the grouping tracker row (`:109`).
- `.agent/context/handoffs/2026-11-08-capture-crop-copy-*.md`, `docs/execution/reflections/2026-11-08-capture-crop-copy-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| The GUI crop tool | Feature | MEU-131 | Grouping, Session 60 |
| GUI import | Feature | MEU-132 | Grouping, Session 61 |
| A live agent run of the `crop` description | Evaluation | Session 60's prompt carries it | D-494 |
| Crop rules for mark types added later (redact, line, ellipse, step) | Feature | MEU-103, MEU-106, MEU-107 | Grouping D-406 |
| Provenance stored on the row (source id, box) | Data | None | 09 `:1031` returns it; nothing stores it |
| Output format choice (JPEG, WebP) | API shape | None | 09 `:1027` says PNG |
| Trim, extent, cover resize, rotate, tiles | Feature | None | Design §9, design D-13 |
| Geometry strings or gravity | API shape | None | Design §6.6 (R-9) |
| An ImageMagick dependency | Dependency | None | Design D-10 |
| Cropping in place | Behaviour | None | Design D-1, ruled by Mat |
| An authoritative baseline refresh | Audit | The next release audit | D-499 |

## BUILD_PLAN.md Audit

MEU-130 is in `.agent/context/meu-status.yaml` (phase 9, band P2, matrix item 9.37, anchor `crop-to-new-shot`, `pending`); row 0 records its line after Session 58's edits. Row 6 sets it `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at rows 6 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s59-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s59-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Checks the queue (S8): MEU-128 and MEU-129 are `approved` in `meu-status.yaml` and no path of Session 58's Files Modified is dirty; MEU-125 is `approved`. `-QueueWaived` on Mat's words waives only the MEU-125 check.
2. Checks Session 58's shapes (S11): `resolve_region`, `CaptureSource.Import`, `ConflictError` from `CaptureAdapter.view`, and the `.avkit-tmp` suffix in `services/capture.py` are present, by name.
3. Creates `C:\Temp\av-kit\s59\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256.
4. Runs `uv sync --frozen --offline --all-packages`, and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair is over 1024 B and that Pillow is 13.0.0 with `MAX_IMAGE_PIXELS` 89,478,485 (S4).
5. Records the line endings and SHA-256 of every file in §Files Modified to `s59-anchors.txt`, which row 1 reads before it writes.
6. Captures the base Python suite to `s59-base-py.txt`, the base UI suite to `s59-base-ui.txt` and the base MCP suite to `s59-base-mcp.txt`.
7. Runs `red-check.py --selftest` and `identity.py --selftest`.

`red-check.py` and `identity.py` are copies of Session 58's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds `clip_mark`, `crop_shot`, `CropResult`, `CaptureCropIn`, `CaptureCropOut`, `crop` and `MarkCarry`, and keeps the selftest fixtures' names. These excuse a non-required block only: no required Red reaches them by name.
- **`identity.py`.** `PLAN` is this folder, and `NAMED_DISTRIBUTIONS` stays empty. It binds the pinned FFmpeg pair by SHA-256. Its selftest binds `session-gate.ps1`, `issue-file.py`, the new e2e module, `09`, the register and its renders, and the crop grouping.
- **`PROJECT_ARTIFACTS`.** This plan's `*.md`, the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`.

### 2. Type-only first, then Red, then Green (rows 1 to 5)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2, D-495).** `MarkCarry`, `clip_mark` returning `(mark, "kept")`, `CropResult`, the port's `crop`, and an adapter `crop` that writes nothing and returns `probe(source)`. No enum, service, route or MCP change. Its check runs `tests/unit/test_domain.py`, `test_domain_capture.py`, `test_capture_adapter.py`, `pyright` and `ruff` (Session 54 RULE-1).
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error and a required test that fails on a missing name.
- **Why each Red fails by assertion.** The domain Reds call the row 1 stub. AC-130.7 reads `__members__` first. The adapter Reds call the stub, which writes nothing. The HTTP Reds get 404 from the missing route and fail on the status. AC-130.5 compares the stub's unmoved marks with the clamp. The MCP Reds fail because `.strict()` refuses `crop` or because the counts are 70 and 10. AC-130.29 fails because the committed fixture has no crop case.
- **`--require` matches a test name up to a non-digit boundary.** A parametrized test is required by its base name: at least one of its cases must fail, and each failing case by assertion alone. A case the stub already satisfies, such as AC-130.3's arrow wholly inside, may pass in Red.
  - Row 2, Python: `test_ac_130_1` to `_7`. AC-130.5 is a `clip_mark` property, so it is written before row 3 makes `clip_mark` real; in row 4a it would already pass.
  - Row 4a, Python: `test_ac_130_8` to `_22`.
  - Row 4b, MCP: `AC-130.23` to `.28`. UI: `AC-130.29`.
- **AC-130.22 runs with HealthService built first (Session 54 RULE-2)**, as Session 58's AC-129.11 does.
- **Expectations stay immutable in Green.** No test file changes in rows 3 and 5. The fixture JSON and `openapi.committed.json` are regenerated output, written only by their commands.
- **OpenAPI.** Row 5 regenerates `openapi.committed.json` with `tools/export_openapi.py` and checks the diff against S6.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`: §1.
- `issue-file.py` (row 6, under D-499 A only): files `MCP-AUDIT-BASELINE-PENDING-CROP` through `model.add_issue` and `model.save`, with D-499 in its `enrichment.decision_log` and `YOUTUBE-CAPTIONS-IP-BLOCK` in its links, and keeps a copy of the register as it was before (`C:/Temp/av-kit/s59/s59-ki-before-baseline.yaml`). Under B, C or D it isn't run.
- `session-gate.ps1` (H1-2): below.

### Session gate (H1-2)

`session-gate.ps1` is Session 58's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s59-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests` (includes `capture-region-pass.test.ts`), `ui-build`, `openapi`, `mcp-types`, `mcp-build`, `mcp-tests` (after the build, because `runner-fake-backend.test.ts` reads the served actions from `dist`), `state-render`, `issues-render` |
| Runtime | `crop` (the new e2e module on its own, so its receipt stands alone) |
| Skipped with reason | `ui-electron` (no renderer source file and no route the renderer calls changes, and the renderer pins no source value), `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes) |

`py-tests` excuses only ids that row 0's receipt shows failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 6 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, or Pillow isn't 13.0.0 with `MAX_IMAGE_PIXELS` 89,478,485 | Stop: a fetch is a download and needs Mat's words |
| S5 | Any network request, download or upload, including the live audit | Stop and tell Mat |
| S6 | `export_openapi.py` changes anything besides the crop route, `CaptureCropIn`, `CaptureCropOut` and its three part schemas | Stop and find out why |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | At row 0, MEU-128 or MEU-129 isn't `approved`, a Session 58 path is dirty, or MEU-125 isn't `approved` and Mat hasn't waived it | Stop; Session 58 closes first, and only Mat waives the MEU-125 order |
| S9 | A row finds it must edit `ui/tests/e2e/test-ids.ts` | Stop, add ids in an additive block at the end, and run AC-51.6 and AC-81.13 in that row's own check |
| S10 | A path, a `name` or the AC-130.22 marker reaches a Console surface or an error message in any receipt | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |
| S11 | A Session 58 shape this plan relies on differs from Session 58's plan: `resolve_region`'s signature or messages, `CaptureSource.Import`'s place, the `ConflictError` message, the `.avkit-tmp` pattern, or the counts 70 and 73 | Stop; amend this plan through the plan review before row 1 |
| S12 | D-499 is unruled at row 0 | Stop; row 4b can't be written without the ruling |

## Decision Log

> [!WARNING]
> Mat's request and design D-1 settle the scope, and the grouping (D-400 to D-406) placed this MEU. D-481 to D-498 didn't need Mat: each is autonomous, with its alternatives in `reasoning`. D-499 is Mat's, ruled A on 2026-11-09 (`human-gate-decision.md`). D-476 is Mat's too, ruled A at row 0 on 2026-11-09 when S11 found the `.avkit-tmp` pattern differs from Session 58's plan. Ids D-471 to D-480 are left as headroom after Session 57's D-460 to D-470, the last block claimed on `main` or in its uncommitted plan when this plan was written (`C:/Temp/av-kit/s59-plan-dids.txt`).
>
> Carried and not relisted in the block: every grouping §8 row, D-400 to D-406, with stage `grouping`. Of those, D-401 and D-406 bear on this session (grouping `:141`). Session 58's D-407 to D-427 are carried as its plan rules them; this plan relies on D-407, D-408, D-410, D-414, D-418 and D-421. The design's own D-1 to D-13 are a separate namespace, cited here as "design D-n" in prose only. The probe (`C:/Temp/av-kit/s59-decision-issue-probe.txt`), run with this plan and the grouping as sources (Session 54 RULE-5), shows what the closeout's `--decision-issue` flag pulls in for `MCP-AUDIT-BASELINE-PENDING-CROP`.

```yaml
decision_log:
  - id: D-481
    stage: planning
    question: "How does a crop take its box, and what does it read?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_REQUEST and CROP_READ: CaptureCropIn with float fields and no bounds, resolved by Session 58's resolve_region; the row and sidecar read under CAPTURE_FILE_LOCK; a changed file is 409 and an unreadable one 422, neither naming a path"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1025 — coordinates, rounding and bounds follow Region view"
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:119-120 — REGION_RESOLVE and REGION_ERRORS"
      - "packages/core/src/avkit_core/services/capture.py:385-404 — get_shot and load_shot_annotations take no lock"
    research:
      engine: none
      sources: []
    reasoning: "Reusing resolve_region is grouping D-401: one resolver, so a crop and a view of the same box cut the same pixels. Pydantic bounds would replace Session 58's messages with its own. Reading through get_shot and load_shot_annotations would read outside the lock, so a concurrent annotate could change the sidecar between the read and the write. A crop that read the file's real size when the row is stale would cut a box the agent didn't compute, so it is told to list again, as the region view is. Two-way."
  - id: D-482
    stage: planning
    question: "How are the crop's pixels written?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_PIXELS: a new port method that cuts with no resampling, keeps the mode when PNG stores it, keeps the ICC profile and writes no EXIF, XMP or text"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1027 — exact pixels, PNG, metadata stripped"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:265-286 — bake converts to RGBA and draws"
      - "C:/Temp/av-kit/s59-plan-probes.txt — PNG saves 1, L, LA, P, RGB, RGBA and I;16; a crop keeps only what save is given"
    research:
      engine: none
      sources: []
    reasoning: "bake with no marks would convert every crop to RGBA and run the region pass, so a 1-bit or 16-bit source would change values. Stripping the ICC profile too would shift colours on a wide-gamut screenshot, and the profile describes the pixels, not the user. EXIF, XMP and text can hold a camera serial, a location or an author, which 09 says to strip. Always RGBA lost: it quadruples a grayscale crop and loses I;16 precision. Two-way."
  - id: D-483
    stage: planning
    question: "How is a crop named?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_NAME: the source stem cut to 100 characters plus -crop.png, then -crop_2.png and on; a name sanitized to [A-Za-z0-9 ._-], 1 to 80 characters, not ending in .annotated, crop_ before a reserved name; free when no inbox-root file of any shot role and no row case-folds equal"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1028 — the name contract"
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:133 — IMPORT_NAME, case-folded, reserved names prefixed"
      - "packages/core/src/avkit_core/services/capture.py:119-128 — annotated_path_for and _sidecar_for derive sibling names from the stem"
    research:
      engine: none
      sources: []
    reasoning: "A crop's sidecar and bake take names from its stem, so a name is free only when none of its sibling names exist, or the crop would adopt a stranger's sidecar. A name ending in .annotated would make the crop look like another shot's bake to the scanner. Case-folding matches Windows. Refusing a name that sanitizes to nothing, instead of falling back silently, tells the agent what was wrong. Two-way."
  - id: D-484
    stage: planning
    question: "What source value does a crop carry?"
    resolution: autonomous
    class: two-way
    chosen: "CaptureSource.Crop = 'Crop' after Import, with no wire value; 09 :1029's 'wire crop' is corrected"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/domain/enums.py:209-217 — the column stores .name"
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:134 — IMPORT_SOURCE with no wire map entry"
    research:
      engine: none
      sources: []
    reasoning: "A wire value exists only for sources that arrive through register (REGISTER_SOURCE_WIRE_MAP); a crop never does, so a wire value would be an unused entry. Reusing Import lost: it would hide which shots were cut from others. Two-way."
  - id: D-485
    stage: planning
    question: "Where does mark carrying live, and how is every mark type covered?"
    resolution: autonomous
    class: two-way
    chosen: "MARK_CARRY: a pure clip_mark in domain/capture.py, a match on every Annotation member with assert_never, returning the mark and kept, clipped or dropped; its output is a fixed point of _clamp_annotation"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/domain/tts.py:133 — assert_never after a match"
      - ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:99 — D-406, every mark type on main"
      - "packages/core/src/avkit_core/services/capture.py:917-952 — _clamp_annotation"
    research:
      engine: none
      sources: []
    reasoning: "A pure function tests without a service, and assert_never makes a mark type added later without a crop rule a pyright error, which is how D-406's rule is enforced. The fixed-point property means the crop's sidecar reads back unchanged through annotate. Clipping in the service lost: it would test only through HTTP. Two-way."
  - id: D-486
    stage: planning
    question: "How are box marks clipped, and which bake differences follow?"
    resolution: autonomous
    class: two-way
    chosen: "MARK_CLIP_BOX: highlight, pixelate and eraser half-open, a rect on its inclusive outline with no zero-size shortcut, because a zero-width or zero-height rect is a drawn line; design 6.5's differences corrected to: a rect cut on any side gets a crop-edge stroke; pixelate re-aligns on left or top and averages partial blocks on right or bottom; eraser samples the ring inside the crop"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:136-160 — region_clip and the pixelate grid at the clipped box's corner"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:408-417 — highlight fills to x + width - 1"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:463-471 — rect outlines to x + width"
      - "_inspiration/capture-crop/design.md:233-239 — the differences as first listed"
    research:
      engine: none
      sources: []
    reasoning: "Each kind is clipped on the pixels the bake draws for it, so a clipped mark covers the same crop pixels the source's did. A half-open rect would put its right and bottom stroke one column outside the crop and show stroke_width minus 1 columns, none at width 1. Design 6.5 said only left or top because it reasoned from the origin clamp; reading the adapter shows every cut side closes with a stroke, and that the pixelate's partial blocks and the eraser's ring change too. Asserting them in AC-130.18 makes them documented behaviour. Two-way."
  - id: D-487
    stage: planning
    question: "How is an arrow clipped?"
    resolution: autonomous
    class: two-way
    chosen: "MARK_CLIP_ARROW: Liang-Barsky against the closed crop, ends rounded half up and clamped, dropped when rejected or zero length; a clipped arrow never reverses, though rounding can zero one component"
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1030 — Liang-Barsky"
      - "packages/core/src/avkit_core/services/capture.py:924-935 — ends clamped to [0, width]"
    research:
      engine: none
      sources:
        - "C:/Temp/av-kit/s59-plan-probes.txt — eleven reference cases"
    reasoning: "Liang-Barsky keeps the direction, which the per-point clamp loses (design L-7). The closed rectangle matches the clamp, so a clipped arrow is a fixed point. Rounding half up rather than truncating keeps a clipped end within half a pixel of the true intersection. A zero-length arrow draws only a head with no direction, so it is dropped. Two-way."
  - id: D-488
    stage: planning
    question: "How is a text mark carried?"
    resolution: autonomous
    class: two-way
    chosen: "MARK_CLIP_TEXT: kept when the anchor is inside, half-open; dropped otherwise; never clipped"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1030 — kept when its anchor is inside"
    research:
      engine: none
      sources: []
    reasoning: "Text can't be clipped without measuring glyphs, which the domain can't do without a font. The anchor rule is the contract's, and the glyphs that reach in from an outside anchor are the known difference AC-130.18 asserts. Two-way."
  - id: D-489
    stage: planning
    question: "What does the crop write for its marks?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_BAKE: with marks, a sidecar at _sidecar_for(crop) and a bake in the configured format, both on the row; with none, neither"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1030 — the crop gets its own sidecar and bake"
      - "packages/core/src/avkit_core/services/capture.py:501-554 — annotate_and_save writes the same pair"
    research:
      engine: none
      sources: []
    reasoning: "Writing the pair as annotate_and_save does means the crop looks to every reader like a shot that was annotated, and a later annotate replaces both. Calling annotate_and_save lost: CAPTURE_FILE_LOCK isn't reentrant, and a second hold would let a scan or annotate in between the crop and its marks. An empty sidecar for no marks lost: annotate_and_save removes both when there are none. Two-way."
  - id: D-490
    stage: planning
    question: "What happens when a crop fails partway?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_CLEANUP: one lock hold and one unit of work; any exception after the first write removes every file the crop wrote, commits no row, and raises CaptureFailedError (503)"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:130 — IMPORT_COPY, D-418"
      - "packages/core/src/avkit_core/services/capture.py:715-717 — convert's except Exception"
    research:
      engine: none
      sources: []
    reasoning: "A half-written crop with no row would be picked up by the next scan as a Scan shot, and a bake without a sidecar would be an orphan. The 503 hides probe's path-bearing message. Keeping the files and returning an error lost: the agent can't tell which files are valid. Two-way."
  - id: D-491
    stage: planning
    question: "What does a crop return?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_RESPONSE: 201 with item, source_id, requested, applied, clamped and the mark counts, and no image bytes"
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1031 — the response"
      - "_inspiration/capture-crop/design.md:161-200 — section 6.3"
    research:
      engine: none
      sources: []
    reasoning: "The agent needs the new id to keep working and applied to know what was cut; requested echoes what was sent so a clamp is visible. Bytes would cost tokens the agent can spend through image. A domain CropResult keeps the service free of API types. Two-way."
  - id: D-492
    stage: planning
    question: "How does MCP expose crop?"
    resolution: autonomous
    class: two-way
    chosen: "CROP_MCP: a strict avkit_capture member, a POST ACTION_INDEX row after revert, ADD_TIMEOUT_MS, not destructive, design 6.7's description, and an audit plan step"
    source_tag: Local Canon
    precedents:
      - "mcp-server/src/toolsets/registry.ts:132-134 — revert, then the MEU-62 rows"
      - "mcp-server/src/toolsets/registry.ts:335-340 — the timeout branch"
      - "mcp-server/scripts/audit/plan.ts:1559-1575 — capture.revert, then capture_interactive"
    research:
      engine: none
      sources: []
    reasoning: "A member of avkit_capture keeps the tool count, and the crop belongs with the actions on a shot. A crop decodes and encodes a full image and may bake, so it gets the add timeout that capture uses. It overwrites nothing, so a destructive flag would ask the user for no reason. The audit plan step keeps every ACTION_INDEX row covered by the live audit. Two-way."
  - id: D-493
    stage: planning
    question: "How do the Pillow and renderer parity suites cover clipped marks?"
    resolution: autonomous
    class: two-way
    chosen: "Append four crop cases to region_cases() with REGION_SEED + 1, regenerate the fixture, and add the names to the UI case lists"
    source_tag: Local Canon
    precedents:
      - "tools/capture_bake_fixture.py:126 — region_cases"
      - "ui/tests/unit/capture-region-pass.test.ts:34,105,148,154 — the case lists"
      - "tests/unit/test_capture_bake_fixture.py:87,126 — AC-90.8"
    research:
      engine: none
      sources: []
    reasoning: "09 asks for the parity suites on clipped marks. A new seed keeps the existing cases' bytes, so the diff is only the new cases. A separate crop fixture lost: it would need its own loader and reproduction check. Two-way."
  - id: D-494
    stage: planning
    question: "How is the crop description checked?"
    resolution: autonomous
    class: two-way
    chosen: "AC-130.25 checks the markers now; a live agent run of the description is carried in Session 60's prompt"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:346 — AC-128.24 checks markers"
    research:
      engine: none
      sources: []
    reasoning: "A live agent run needs a model and network, which this session's rows don't allow. Session 60 builds the GUI on the same endpoint and is the next session to touch the tool. Two-way."
  - id: D-495
    stage: planning
    question: "Which names does row 1 add?"
    resolution: autonomous
    class: two-way
    chosen: "MarkCarry, the clip_mark stub, CropResult, the port's crop and an adapter crop that writes nothing"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:491 — Session 58's row 1"
    research:
      engine: none
      sources: []
    reasoning: "Every Red then reaches a name that exists, so it fails by assertion. The enum member waits for row 3 so AC-130.7 is a real Red. Two-way."
  - id: D-496
    stage: planning
    question: "Where do crop values go?"
    resolution: autonomous
    class: two-way
    chosen: "NO_RAW_CONSOLE and Where values go: no new log line; name sanitized before use; AC-130.22 proves it"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:135 — NO_RAW_CONSOLE"
    research:
      engine: none
      sources: []
    reasoning: "The crop adds no outside text but name, and the existing lines carry no path to the Console. Two-way."
  - id: D-497
    stage: planning
    question: "What does the session gate run?"
    resolution: autonomous
    class: two-way
    chosen: "Session 58's steps with crop as the runtime step; ui-electron, mcp-audit, build-record and the package build skipped with reasons"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:512-518 — Session 58's gate"
    research:
      engine: none
      sources: []
    reasoning: "No renderer source or renderer-called route changes, and the renderer pins no source value, so an Electron run proves nothing new; ui-tests still runs the parity test. The live audit needs network. Two-way."
  - id: D-498
    stage: planning
    question: "When can this session run?"
    resolution: autonomous
    class: two-way
    chosen: "After Session 58 closes (MEU-128 and MEU-129 approved) and Session 57 (MEU-125) is approved; only Mat waives the MEU-125 order, and nothing waives Session 58"
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:97-98 — queue and prerequisite gate"
    research:
      engine: none
      sources: []
    reasoning: "This plan calls Session 58's resolver and copies its write pattern, so it can't run first. The rc.2 order is grouping D-405, which Mat can move. Two-way."
  - id: D-499
    stage: planning
    question: "How does the MCP audit baseline meet the new crop action?"
    resolution: human
    class: governance-value
    chosen: "A, as recommended: BASELINE_PENDING = ['avkit_capture.crop'] in coverage.test.ts, AC-68.5's committed-baseline clause amended, and MCP-AUDIT-BASELINE-PENDING-CROP filed. Mat's words (2026-11-09): 'D-499 A'"
    source_tag: Human-approved
    precedents:
      - "mcp-server/tests/audit/coverage.test.ts:78-85 — AC-68.5"
      - ".agent/skills/mcp-tool-audit/SKILL.md:45-51 — BASELINE_UPDATE_RULE and BASELINE_ANNOTATION_RULE (a hand-added entry is forbidden)"
      - ".agent/context/known-issues.yaml:2931 — YOUTUBE-CAPTIONS-IP-BLOCK, open; its blast radius says 'Do not refresh the audit baseline to hide it.'"
      - "docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md:200 — D-20, a gate-only tolerance"
      - "docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md:176 — LOCAL_SEQUENCE step 1, the same-session authoritative refresh that closed D-20"
      - "docs/execution/plans/2026-11-08-release-rc2/audit-rule.py:16,405 — refuses a NEW row (uncommitted)"
    research:
      engine: exa
      sources:
        - "https://contribute.qt-project.org/quips/24/ — an ignored test is quarantine; needs an open, assigned ticket named beside the entry; narrow conditions"
        - "https://handbook.gitlab.com/handbook/engineering/testing/quarantine-process/ — an issue first; temporary"
        - "https://www.rad-ui.com/docs/contributing/flaky-test-quarantine — guard the narrowest assertion, with a tracking issue and a restore note"
        - "https://sysroot.io/blog/flaky-tests-quarantine-strategy-ci-cd-reliability — the list lives in version control, one ticket per entry"
    reasoning: "The baseline is a governed snapshot that only an authoritative run updates, and that run is blocked now. A names the gap in the test and the register, so main stays green and the next release knows what to accept. B keeps main red for the MCP suite. C needs network and is blocked. D can't close the session. A changes what AC-68.5 accepts, so Mat rules it (HDP section 4 test 4). Two-way: one constant and one issue."
    human_message_reference: null
  - id: D-476
    stage: planning
    question: "S11 at row 0: Session 58's execution changed the .avkit-tmp pattern from its plan (F1 and F2). How does this plan meet it?"
    resolution: human
    class: two-way
    chosen: "A, as recommended: amend the plan narrowly and send it through plan-review round 3 before row 1. CROP_NAME counts a name whose temporary file is in the inbox root as taken; CROP_CLEANUP creates the temporary file with open('xb') and removes only what the crop created; every filesystem call on the crop's paths sits inside the mapped try, and the adapter's crop catches Exception on open and decode as view does; AC-130.21 gains Session 58's keeps-a-temporary-file-it-did-not-write cases and a damaged-PNG case. Mat's words (2026-11-09): 'A: plan round 3 (Recommended)'"
    source_tag: Human-approved
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:512-546 — _import_copy: open('xb'), tmp set after the create, moved guards the destination"
      - "packages/core/src/avkit_core/services/capture.py:549-570 — _import_dest counts a NAME.avkit-tmp entry as taking NAME"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:297-304 — view catches Exception: Pillow raises SyntaxError, ValueError and others for a damaged file"
      - "tests/e2e/test_api_capture_region_import.py:627 — AC-129.9, keeps a temporary file it did not write"
      - "docs/execution/reflections/2026-11-08-capture-region-import-reflection.md:41-43 — RULE-1 and RULE-2"
    research:
      engine: none
      sources: []
    reasoning: "The plan was written before Session 58's execution review found that D-418's cleanup could delete another writer's temporary file (F1) and that calls outside the mapped try leaked paths (F2). Copying the corrected shape keeps the crop from repeating both. B, running the rows on the old text and fixing it in execution review, would ship code the approved plan contradicts. C, stopping the session, delays MEU-130 for a change that only follows Session 58's own correction. Two-way: it changes the plan text and one test module."
    human_message_reference: null
  - id: D-506
    stage: execution
    question: "Execution review round 1 F1: a CMYK JPEG's crop loses its ICC profile, though D-482 keeps it. PNG can't hold CMYK or a CMYK profile. How does a crop treat a source in a mode PNG can't store?"
    resolution: human
    class: two-way
    chosen: "A, as recommended: a CMYK, YCbCr or LAB source with a profile that builds a transform converts through it to sRGB with ImageCms, and the crop carries the sRGB profile; with no profile, or one that builds no transform, it converts plainly to RGB and carries none. Amends D-482, CROP_PIXELS and AC-130.10. Mat's words (2026-11-09): 'A: convert via profile (Recommended)'"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s59-exec-review-round-1.md — F1, U.S. Web Coated (SWOP) v2: 557168 ICC bytes before the crop and 0 after"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:65 (before the fix) — _CROP_ICC_DROP_MODES dropped the profile, a departure from D-482 that row 5 did not record"
      - "C:/Temp/av-kit/s59-f1-probe.txt — Pillow 13 with littlecms2: plain CMYK to RGB (148,114,80), through SWOP (157,122,93); junk bytes raise OSError, a profile for another colour space raises PyCMSError"
    research:
      engine: none
      sources: []
    reasoning: "D-482 keeps the profile because stripping it shifts colours. A CMYK profile can't sit on RGB pixels in a PNG, so the literal rule can't hold; converting through the profile is how a colour-managed viewer shows the source, and the sRGB profile then describes the crop's pixels. C, dropping it and amending the contract, keeps the colour shift. Doing nothing leaves F1 open and MEU-130 unapproved. Mat rules it because it amends an approved AC. Two-way: one adapter helper and three tests."
    human_message_reference: null
```

## Research References

- `docs/build-plan/09-screenshot-capture.md:1017-1032` (the contract), `:282`, `:577-578`; `docs/build-plan/05-mcp-server.md`; `docs/build-plan/00-overview.md:68`.
- `_inspiration/capture-crop/design.md`: §6.3 (`:161-200`), §6.5 (`:219-239`), §6.6 (`:241-256`), §6.7 (`:258-273`), L-7 (`:54`).
- The grouping file: §3 (`:70-72`), §5 (`:95-99`), §6 (`:104-111`), §7 (`:115-121`), §8 (`:126-143`).
- Session 58's plan and scripts (`docs/execution/plans/2026-11-08-capture-region-import/`), Session 38 `capture-new-marks`, MEU-67 `capture-flatten-backup`.
- Session 57's `audit-rule.py` (uncommitted, read only).

## Planning receipts

- `C:/Temp/av-kit/s59-plan-probes.txt`: line endings and SHA-256 of every target file at `8bcb4a6`, Pillow's crop and save behaviour per mode and for metadata, and the Liang–Barsky cases.
- `C:/Temp/av-kit/s59-plan-dids.txt`: the D-id and AC sweep.
- `C:/Temp/av-kit/s59-plan-stage-copies.txt`: the scripts copied from Session 58's and edited.
- `C:/Temp/av-kit/s59-plan-identity-selftest.txt`, `C:/Temp/av-kit/s59-plan-redcheck-selftest.txt`: the scripts' selftests in this folder.
- `C:/Temp/av-kit/s59-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- `C:/Temp/av-kit/s59-decision-issue-probe.txt`: the decision probe. It reads the plan, the grouping (26 decisions: D-400 to D-406 at stage `grouping`, D-481 to D-499 at `planning`), and a register copy that holds the dry-run filing.
- `C:/Temp/av-kit/s59-plan-issue-file-dry.txt`: `issue-file.py --probe` on a copy of the register: 44 lines added, 0 removed. The register itself is unchanged.
- `C:/Temp/av-kit/s59-plan-ruff-tools.txt`: `ruff check tools/capture_bake_fixture.py` passes. The whole `tools/` folder has 10 errors at `8bcb4a6`, so rows 5 and the gate lint only the one tool file this session edits.
- Step 4A GUI check (`gui-refs-not-shipped`, items 3 and 5): no renderer source file changes. The inbox page shows a crop as it shows any shot.
- Not run at plan time: any suite, build or smoke. Row 0 runs the suites after Session 58.

## Validation stage contract

- **Static:** `pyright packages/`, `ruff`, the UI typecheck and lint, the MCP typecheck, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds, the OpenAPI guard and the two render checks, in the session gate.
- **Runtime:** the new e2e module on its own.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
