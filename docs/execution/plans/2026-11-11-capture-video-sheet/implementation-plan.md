---
project: "2026-11-11-capture-video-sheet"
date: "2026-11-11"
source: ".agent/context/grouping/2026-11-09-video-stills-session-grouping.md#session-63--capture-video-sheet-meu-135--p2"
grouping_source: ".agent/context/grouping/2026-11-09-video-stills-session-grouping.md"
meus: ["MEU-135"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Video sheet (Session 63)

> **Project:** `2026-11-11-capture-video-sheet`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Residuals registered 2026-11-09 → §Video sheet (`:1152-1170`, anchor `video-sheet`, MEU-135).
>
> **Source request.** On 2026-11-09 Mat asked whether an agent can take stills from a video through av-kit, to review meeting recordings and security camera footage, and accepted every recommendation of the video stills design (`_inspiration/video-stills/design.md`; grouping D-500). This is the second of the grouping's three sessions. Session 62 delivered probe and frames (MEU-133, MEU-134, both `approved`, commit `7403f18`). Done comes from 09's contract, not from Mat's words: each rule holds with a behaviour test, the real-FFmpeg tests pass on generated clips, and the D-504 planning probe is run and cited here.
> **Known issues:** none open for this MEU. `MCP-AUDIT-BASELINE-PENDING-CROP` stays open; `avkit_capture.sheet` joins the same pending list (D-603) and `--update-baseline` is never run. `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` is out of scope. `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` and `CAPTURE-EXIF-SCANNED-ORIENTATION` can't touch the sheet (D-604): an observation of either is recorded in the handoff and raised, never fixed here.
> **Status:** `draft`, with the gate held on 2026-11-11 (Mat's words in §User Review Required, "The gate"). `plan_to_exec_gate: human`. Two questions are Mat's (§User Review Required): D-601, the grid cap and the time limit; D-602, how label legibility is checked by eye. Mat also sets the execution budget at the gate.

## Goal

**Goal anchor:** Session 63 gives an agent one view of a span of a local video. `POST /captures/sheet` and `avkit_capture` `sheet` grab `grid × grid` cells at the midpoints of the span, each already scaled to the cell by FFmpeg, tile them left to right and top to bottom with Pillow, label each cell with its number and time, and write the grid as one new shot in the capture inbox. The response lists each cell's time, so the agent cites times from `cells`, never from the image, and zooms by calling again with a narrower span. The video is read in place and never changed, and nothing is uploaded.

Four things are missing today:

1. **No way to grab a frame at a given size.** `FramePort.grab_frame` (`packages/core/src/avkit_core/ports/capture.py:72`) and `FFmpegAdapter.grab_frame` (`packages/infrastructure/src/avkit_infra/media/adapter.py:545`) return the full-size frame. Twenty-five full 4K frames are about 25 × 12 MB decoded before Pillow could shrink them.
2. **No tiling or labels.** `CaptureAdapter` (`packages/infrastructure/src/avkit_infra/capture/adapter.py:271`) bakes annotations, views, imports and crops; nothing pastes images into a grid. `_load_font` (`:145`) resolves the annotate font.
3. **No sheet size rule.** The region view caps a long edge (`REGION_MAX_EDGE_*`, `domain/capture.py:29-31`) but nothing fits `grid × grid` cells under a token budget.
4. **No sheet surface.** No route, schema or MCP action takes a span and a grid.

The session ends when 09's §Video sheet holds with a behaviour test per rule, the real-FFmpeg tests pass, the D-504 receipt is cited, the session gate's last line is `session-gate: all steps exit 0`, D-601 and D-602 are ruled, and MEU-135 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-11). No payload is oversized: services/capture.py (1770 lines), capture/adapter.py and mcp-server/scripts/audit/plan.ts were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s63-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s63\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
  - No row runs Electron, so `ELECTRON_RUN_AS_NODE` doesn't matter here; the gate clears it anyway.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s63-plan-canonical-2026-11-11-capture-video-sheet` and `s63-execution-2026-11-11-capture-video-sheet`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290), and the `--review-state-only` receipt is rebuilt there.
  - Reviewer prompts name the ledger vocabulary up front: D-593 to D-607, AC-135.1 to AC-135.20, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). Each recheck carries a literal Prior Pass Summary with bare closure words (Session 52 RULE-1) and asks for a `### New Findings` table and bare words in its Recheck cells (`fixed`, `open`).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, the live MCP audit, `--update-baseline`, a tag, release or upload, or an `approved` verdict authored by the implementer. Video stays local: no test or row reads a video from the network or uploads one, and a URL is refused as video input. Every test clip is generated by the pinned FFmpeg from `lavfi` sources in a temp folder. Nothing touches the installed avkit MCP servers, Mat's inbox, Mat's videos or YouTube.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-135 `capture-video-sheet` | `.agent/context/handoffs/2026-11-11-capture-video-sheet-MEU-135-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-11-capture-video-sheet-plan-critical-review.md` and `.agent/context/handoffs/2026-11-11-capture-video-sheet-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, `s63-anchors.txt` |
| WP-2 | Type-only names (row 1) | WP-1 | shared | the `video_input.py` sheet stubs and constants, `ImageAnnotatePort.sheet`, `grab_frame`'s `box` keyword, the `sheet_from_video` stub, the moved `grab_frame` parameter pin |
| WP-3 | MEU-135 Red, then Green (rows 2a, 2b, 3) | WP-2 | shared | `SHEET_SIZE`, `SHEET_TIMES`, `SHEET_LABEL`, `CELL_GRAB`, `SHEET_TILE`, `SHEET_NAME`, `SHEET_CHECKS`, `SHEET_WRITE`, `SHEET_DEADLINE`, `SHEET_ROUTE`, `SHEET_MCP`; the OpenAPI snapshot with the sheet route |
| WP-4 | Records (row 6) | WP-3 | shared | The 09 note, MEU status, renders, grouping tracker |
| WP-5 | Closeout (H1, H2) | WP-4 | `compact_continue` | The handoff, review, reflection, Session 64's prompt |

**Ride flag (D-593): MEU-136 does not ride.** The grouping (`:71`) lets MEU-136 `capture-export-copy` ride if this plan comes out small. It doesn't: the sheet touches core, infrastructure (two adapters), the API and MCP, with 20 ACs, a real-FFmpeg extension, a refactor of the frames worker (D-600) and an OpenAPI regeneration. MEU-136 adds a UI action and its own E2E (grouping §3); riding would pull Electron into a session that runs none, and grouping D-505's description eval goes with MEU-136 to Session 64.

## User Review Required

> [!IMPORTANT]
> **Two questions are Mat's.** Every other choice is recorded as autonomous in §Decision Log (D-593 to D-600, D-603 to D-607), with its alternatives. The gate asks Mat to accept the plan, rule D-601 and D-602, set the execution budget, and override any autonomous choice. Only Mat's words start execution.
>
> **D-601: does the grid cap stay 5, and how long may a `sheet` call run?** (`governance-value`.) Design D-4 set `grid` 2 to 5 and grouping D-504 lets the plan lower the cap from the 5×5 probe. On the same 2 h 4K HEVC file Session 62 measured (11,285,707,465 B, 7,200,021 ms), a 5×5 sheet with each cell grabbed at 288×162 by FFmpeg's Lanczos scaler took 10.23 s for the 25 grabs (0.409 s each, the slowest 0.73 s) and 0.063 s to tile, label and save: 10.30 s in all, no failure (`C:/Temp/av-kit/s63-d504-probe-receipt.txt`). A second run at pre-keyframe times (the slowest seek) took 8.78 s (`s63-d504-prekey-run.txt`). The MCP default timeout is 30 s; `frames` already uses 120 s (`ADD_TIMEOUT_MS`, `mcp-server/src/toolsets/registry.ts:390-396`). 10.3 s isn't close to either here, but a slower disk or CPU, or longer keyframe gaps, can push it toward 30 s.
> - **A (Recommended): keep cap 5, give `sheet` the 120 s client timeout, and stop at 100 s.** `avkit_capture` `sheet` joins the `ADD_TIMEOUT_MS` list. `SHEET_DEADLINE_S = 100`, `SHEET_RETURN_S = 105` and the shared `COMMIT_WAIT_S = 6`, the values Mat ruled for frames (D-577 A, D-587), so the call answers within 111 s and one join step against the client's 120 s. Eleven times the measured time.
> - **B: lower the cap to 4, keep the 30 s default, and stop at 20 s.** At most 16 grabs per call (about 6.6 s here). `SHEET_DEADLINE_S = 20`, `SHEET_RETURN_S = 23`, `COMMIT_WAIT_S = 6`, so the call answers within 29 s. Every `5` in `SHEET_CHECKS`, `SHEET_ROUTE`, `SHEET_MCP`, `SHEET_TEXT` and their tests reads `4`, and every `6` past the cap reads `5`. An agent wanting 25 cells over an hour calls twice with half spans.
> - **C, do nothing:** keep cap 5 and the 30 s default timeout, with B's 20/23/6 deadline so a slow call fails before the client gives up. The measured 10.30 s is recorded in the handoff.
>
> **D-602: how is label legibility checked by eye?** (`human-check`.) 09's Tests row asks for labels "legible on a mostly white and a mostly black frame". AC-135.7 and AC-135.14 prove contrast: on an all-white and an all-black cell, the label box holds both near-white fill and near-black outline pixels, with a no-label control that holds none. Contrast is not readability: a test can't say whether `25 01:56:24` at 21 px on a 162 px wide 9:16 cell reads as those characters.
> - **A (Recommended): Mat looks at three rendered sheets after row 3.** Row 3 writes them to `C:/Temp/av-kit/s63/look/` from generated clips with the real adapter and the real font: `white-grid3.png` (an all-white clip, grid 3, 1446×813), `black-grid3.png` (all-black, grid 3) and `tall-grid5.png` (a 9:16 clip, grid 5, 810×1440, where the label is fitted down from 40 px to 21 px, the smallest case at the default `max_edge`). The plan-time probe sheet `C:/Temp/av-kit/s63/s63-probe-sheet-fit_lanczos.png` (real 4K footage, 5×5, 22 px labels) is there already. Mat says "legible" or names the sheet that isn't; the handoff quotes his words. Leaves unproven: sizes smaller than the default `max_edge` (at `max_edge` 200 and grid 4 or more the widest label doesn't fit even at the 8 px floor, `s63-size-probe-receipt.txt`; it is clipped to its cell).
> - **B: Mat looks only at the probe sheet now, at the gate.** One image, real footage, 16:9 grid 5 at 22 px. Leaves unproven: the white and black backgrounds and the fitted-down 9:16 label.
> - **C, do nothing:** rely on the pixel-contrast tests. Leaves unproven: that any label reads as its text to a person or a model.
>
> **What the words in the contracts mean here, and the limits they leave.**
> - **"Cell times sit at the midpoints, as in `count` frames."** `FRAME_TIMES` (`services/video_input.py:203`) with `count = grid²`: each of `grid²` equal parts of `[start, end)` gives its midpoint, rounded half-up and capped at `end − 1`, then duplicates collapse. When the span has fewer milliseconds than cells, fewer cells are drawn (D-598).
> - **"Grabbed already scaled to the cell size."** FFmpeg's `scale` filter fits the frame inside the cell box, keeping its aspect (`CELL_GRAB`), except that it never makes an edge smaller than its own rounding allows: on a degenerate source such as a 4000×2 strip, a 313×1 box returns 313×2 (plan review round 1, Q5). `SHEET_TILE`'s `thumbnail` shrinks any cell larger than the box, so the sheet's size never moves. A source smaller than the box is scaled up by FFmpeg to fit, which adds no detail. Square pixels and no rotation are assumed: a source with a non-square sample aspect or a rotation tag is fitted by its stored size, and is out of scope (§Out of Scope).
> - **"Label height scales with the cell."** 14 % of the cell height, rounded half up, at least 8 px, then made smaller until the text fits the cell width (`SHEET_LABEL`).
> - **"The long edge is at most `max_edge`, and w×h/750 ≤ 1568 tokens, or ≤ 4784 when `max_edge` > 1568."** Exactly that, in integers (`SHEET_SIZE`). 1568 tokens is the standard vision budget, and 4784 the high-resolution one, as design D-4 cites.
> - **"Spacing."** `spacing_ms` is the span divided by `grid²`, rounded half up: the distance between cell midpoints. Labels gain `.mmm` when it is under 10,000 ms.
> - **"`HHhMMmSSs` times."** Whole seconds, floored, two digits each: `start` 0 and `end` 7,200,021 give `00h00m00s` and `02h00m00s`.
>
> **The token estimate,** calibrated against Session 62 `video-probe-frames` (plan 20,835,539 over 4 rounds; execution 13,244,126: two MEUs, a new port, real-FFmpeg fixtures, the deadline machinery), Session 58 `capture-region-import` (plan 19,334,552 over 3 rounds; execution 11,719,424: the region view's Pillow render and size maths) and Session 59 (plan 23,266,843 over 3 rounds). This session has one MEU across core, two adapters, the API and MCP, 20 ACs, a real-FFmpeg extension, a refactor of the frames worker and one OpenAPI regeneration. Expect 1 to 3 plan rounds (about 10M to 21M). The plan loop opens with the default 10.5M. At the plan gate Mat sets the execution loop's budget; the opening ask is round 1 ×2 plus one recheck at about half of round 1 (Session 60 RULE-5, Session 58 RULE-4): about 11M ×2 + 5.5M ≈ 28M, 3 rounds. The citable AC family is fixed when the plan loop opens: AC-135.
>
> **The gate.** Held 2026-11-11: Mat said "plan accepted with all recommendations, proceed", which accepts the plan, rules D-601 A and D-602 A, and sets the execution budget at the ask, about 28M over 3 rounds. The plan review approved in round 1 with no finding (`.agent/context/handoffs/2026-11-11-capture-video-sheet-plan-critical-review.md`; 7,888,532 tokens). Its two nonblocking wording notes are applied: Q5 at "Grabbed already scaled" above, and Q9 in `SHEET_MCP`'s body text. Execution waits for Mat's words.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `SHEET_SIZE` | `sheet_cell_size(width: int \| None, height: int \| None, grid: int, max_edge: int) -> tuple[int, int]` in `services/video_input.py`, pure, integers only. The source size is `MediaInfo.width` and `.height`; when either is `None` or below 1 it is `SHEET_FALLBACK_SIZE = (1920, 1080)`. `tokens` is `SHEET_TOKENS_STANDARD = 1568` when `max_edge <= 1568`, else `SHEET_TOKENS_HIGH = 4784`; `budget = tokens × PIXELS_PER_TOKEN` (750). `long_src` and `short_src` are the larger and smaller source edges. `long = max_edge // grid`; then `short = max(1, half_up(long × short_src, long_src))`, and while `grid² × long × short > budget` and `long > 1`, `long` drops by 1 and `short` is computed again. The cell is `(long, short)` for a landscape or square source and `(short, long)` for a portrait one. `half_up(n, d)` is `(2n + d) // (2d)`, the one integer rounding this plan uses (Session 60 RULE-3). The sheet is `grid × cell` on each axis, so its long edge is at most `max_edge` and its area at most `budget`. Planning probe: 480 cases (8 shapes, grids 2 to 5, 15 edges including 64, 1567, 1568, 1569 and 2576), 0 failures, each maximal, since one more pixel on the long cell edge breaks a bound (`C:/Temp/av-kit/s63-size-probe-receipt.txt`). |
| `SHEET_TIMES` | The cell times are `frame_times(start, end, grid²)` (`FRAME_TIMES`), unchanged. `sheet_spacing_ms(start_ms: int, end_ms: int, grid: int) -> int` is `half_up(end − start, grid²)`. The cells are numbered 1 to `k` in time order, where `k` is the number of distinct times; `k = grid²` whenever the span is longer than `grid²` ms, and `k ≤ min(grid², span)` always (D-598). |
| `SHEET_LABEL` | `sheet_label(cell: int, timecode: str, spacing_ms: int) -> str` is `f"{cell} {timecode[:8]}"`, or `f"{cell} {timecode}"` when `spacing_ms < 10_000`, where `timecode` is `format_timecode(time_ms)` (`HH:MM:SS.mmm`). `sheet_label_px(cell_h: int) -> int` is `max(8, half_up(cell_h × 14, 100))` and `sheet_label_stroke(px: int) -> int` is `max(1, half_up(px, 10))`, both pure in `video_input.py`. The adapter draws the label at `(pad, pad)` from the cell's top-left, with `pad = max(1, size // 4)`, white fill and a black stroke, in `_load_font(size)`'s font, where `size` starts at `sheet_label_px(cell_h)` and drops by 1 while `size > 8` and the text's `getlength` plus `2 × pad` is wider than the cell. The stroke is recomputed from the final size. The label is drawn on the cell's own canvas, so it is clipped to its cell and never reaches a neighbour. |
| `CELL_GRAB` | `FramePort.grab_frame` and `FFmpegAdapter.grab_frame` gain the keyword-only `box: tuple[int, int] \| None = None`, last. With a box `(W, H)`, `_grab_once`'s argv gains `-vf`, `scale=W:H:force_original_aspect_ratio=decrease:flags=lanczos` directly after `-frames:v 1` and before `-c:v png`; `END_GAP`'s retry passes the same box. With `None` the argv is byte-identical to today's (AC-134.9 runs as a guard). The planning probe ran exactly this filter (`s63-d504-probe-receipt.txt`: every cell came back 288×162). `frames` passes no box. |
| `SHEET_TILE` | `ImageAnnotatePort.sheet(cells: Sequence[bytes], *, grid: int, cell_size: tuple[int, int], labels: Sequence[str]) -> bytes`, implemented by `CaptureAdapter`. It makes an RGB canvas of `grid × cell_w` by `grid × cell_h`, black. For each cell `i` (`len(labels) == len(cells) ≤ grid²`, else `ValueError`), it decodes the bytes with Pillow, loads them, converts to RGB, shrinks with `thumbnail(cell_size, LANCZOS)` when either edge is larger than the box (never enlarges), pastes the image centred on a black canvas of the cell size, draws `labels[i]` as `SHEET_LABEL` says, and pastes that canvas at `((i % grid) × cell_w, (i // grid) × cell_h)`. Cells past `len(cells)` stay black. It returns the PNG bytes from an in-memory buffer, with no metadata. Any decode failure raises; the error text names no path, because there is none (the input is bytes). It writes no file. |
| `SHEET_NAME` | `sheet_name(stem: str, start_ms: int, end_ms: int) -> str` in `video_input.py` is `f"{import_stem(stem)}-sheet-{a}-{b}"`, where each time is `f"{h:02d}h{m:02d}m{s:02d}s"` of the whole seconds, floored; for example `standup-sheet-00h00m00s-02h00m00s`. The suffix `.png` and the `_2`, `_3`… are added by `_import_dest` (`services/capture.py:1008`), as for frames. `import_stem` is imported inside the function, as `frame_name` does (`video_input.py:217-220`), to avoid the import cycle. |
| `SHEET_CHECKS` | `CaptureService.sheet_from_video(path, *, start=None, end=None, grid=SHEET_GRID_DEFAULT, max_edge=REGION_MAX_EDGE_DEFAULT) -> VideoSheet` checks, in order, before any grab and before any inbox write: `VIDEO_INPUT`; `start` and `end` through `TIME_PARSE`; `grid` an `int` that isn't a `bool`, 2 to 5, else `ValidationError("grid must be 2 to 5")`; `max_edge` an `int` that isn't a `bool`, 64 to 2576, else the existing `max_edge must be between 64 and 2576` (`domain/capture.py:230-232`); `FramePort.probe` with the time left, where `MediaProbeError` becomes `the file could not be probed` and no video codec gives `not a video: no video stream`; no duration gives `ValidationError("sheet needs a duration; this video has none")`; then `start` defaults to 0 and `end` to the duration, `start` at or past the duration gives `time {t} is past the end ({duration})`, `end` above it the same with `end`, and `start` at or after `end` gives `start must be before end`. Every message is fixed or built from `TIMECODE` of parsed milliseconds, and each is raised after its `except` clause has ended, so `__cause__` and `__context__` are `None`. A refused call runs no grab and writes nothing. |
| `SHEET_WRITE` | Frames' three-phase pattern (`FRAME_WRITE`, D-580), with one output. (1) Under `CAPTURE_FILE_LOCK.acquire(timeout=left)` and one unit of work: `ensure_dir(inbox)`, `dest = _import_dest(uow, inbox, sheet_name(…), ".png")` and `open(dest + ".avkit-tmp", "xb")`. (2) With the lock released: for each cell time in order, `SHEET_DEADLINE` (a), `grab_frame(resolved, ms, seek="input", timeout_s=left, box=cell_size)`, (b), and the PNG signature check, keeping the bytes in memory; then `self._annotate.sheet(cells, grid=grid, cell_size=cell_size, labels=labels)`; then the after-tiling check (b'); then `handle.write`, `close()` and `self._annotate.probe(tmp)`. (3) Under the lock again and one unit of work: (c), a fresh `_import_dest` name when `dest` is now taken, `os.replace`, `_upsert_shot(uow, dest, probe, now, CaptureSource.Video)`, (d), commit. Any failure closes the handle, unlinks the temp and any moved dest before the lock is released, and the unit of work rolls back. An empty grab, a bad signature or a passed deadline gives `ValidationError("frame grab failed at {t}")`; any other failure (tiling, the output probe, `os.replace`, the database) gives the masked `CaptureFailedError("the sheet could not be written")` (503). A temp another writer made is never opened, written or removed. FFmpeg never writes into the inbox. Frames' `_reserve_frames` and `_publish_frames` take the names, the failure times and the source as parameters so both calls share them (D-600); their behaviour for frames is unchanged. |
| `SHEET_DEADLINE` | Frames' `FRAME_DEADLINE`, with the sheet's own constants (D-601) and worker name `avkit-sheet`. The clock starts when `sheet_from_video` is called, through the injected `monotonic`. Bounded by `left`: the probe, both lock waits and each grab. Checks: (a) before each grab, `t` that cell's time; a phase 1 lock not had in time fails here with the first cell's time; (b) after each grab, `t` that cell's time; (b') after tiling, `t` the last cell's time; (c) at publish, `t` the last cell's time; (d) before the commit, under the gate lock, `t` the last cell's time. (e) The return gate: the body runs on a daemon thread named `avkit-sheet`, and the call answers by `SHEET_RETURN_S`, or by `SHEET_RETURN_S + COMMIT_WAIT_S` while a commit is finishing. The worker/return loop is moved out of `frames_from_video` into one helper, `_run_gated(worker_name, deadline_s, return_s, body)`, which both calls use (D-600); frames keeps `avkit-frames`, 100, 105 and 6. Every blocking call is listed in §Deadline inventory. |
| `SHEET_ROUTE` | `POST /captures/sheet` in `routes/captures.py`, declared after `/frames` and before `/{id}`, status 201. `CaptureSheetIn`: `path: str` (1 to 4096), `start` and `end` `TimeWire \| None = None`, `grid: Annotated[StrictInt, Field(ge=2, le=5)] = 3`, `max_edge: Annotated[StrictInt, Field(ge=REGION_MAX_EDGE_MIN, le=REGION_MAX_EDGE_MAX)] = REGION_MAX_EDGE_DEFAULT`, `extra="forbid"`. `grid` and `max_edge` aren't optional, so `null` is refused, as MCP refuses it. A schema refusal is the fixed 422 `validation_error` `Request validation failed`. `CaptureSheetOut`: `video` (`CaptureFramesVideoOut`, reused), `shot {id, path, width, height}`, `spacing_ms`, `cells [{cell, time_ms, timecode}]`, with no image bytes. |
| `SHEET_MCP` | `avkit_capture` `sheet`: `z.object({action: z.literal("sheet"), path: z.string().min(1).max(4096), start: timeValue.optional(), end: timeValue.optional(), grid: z.number().int().min(2).max(5).optional(), max_edge: z.number().int().min(64).max(2576).optional()}).strict()`, appended after `frames` in `capture.ts`, with its row `{ tool: "avkit_capture", action: "sheet", method: "POST", path: "/captures/sheet" }` after `frames`' in `ACTION_INDEX` (`registry.ts:135`). Under D-601 A it joins `ADD_TIMEOUT_MS` (`registry.ts:390-396`). Its description is `SHEET_TEXT` with its own four markers: `Workflow: call avkit_convert probe for the duration, then avkit_capture sheet to POST /captures/sheet for a grid over a span, then frames for exact stills, then image to view the sheet.` `Prerequisite: a local absolute video path and FFmpeg; the video is read in place, never changed or uploaded.` `Returns: JSON with the video's duration and size, the new shot's id, path and size, spacing_ms and each cell's number, time_ms and timecode; no image bytes.` `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.` and the body `One labelled grid image of a span (default the whole video): grid 2-5 (default 3, so 9 cells), max_edge 64-2576 (default 1568). Cells sit at the midpoints of equal parts of the span; each is the first frame at or after its time, and a time after the last video frame but before the end shows the last frame. Cite times from cells, never from the image. To zoom, call again with a narrower start and end; no state is kept between calls. Events between cells can be missed. Needs a video with a duration.` Transport parity, not identical filters: `start: null` is refused before fetch where REST reads it as absent, and a negative time is refused before fetch where REST refuses it in `TIME_PARSE`. |
| `FRAMES_TEXT` line | `FRAMES_TEXT`'s workflow line (`capture.ts:58-67`) becomes `Workflow: call avkit_convert probe for the duration, then avkit_capture sheet to find the moment, then frames to POST /captures/frames for exact stills, then image to view a frame.`, the order 09's Description row names (`:1137`, probe → sheet → frames → image). It moves pin `FRAMES_TEXT_MARKERS[0]` (`capture.test.ts:930`, AC-134.15) (D-605). |
| `NO_RAW_OUTPUT` | No new log line, error message or response field carries the video path, the sheet path or FFmpeg's stderr, except the 201 body's `video.path` and `shot.path`, which echo what the caller asked about and the shot it now owns. `sheet_from_video` logs `capture.sheet` with the cell count and the shot id only. |

### Deadline inventory (Session 62 RULE-1)

| # | Blocking call | Where | Bound |
|---|---|---|---|
| 1 | `require_local_video` (`resolve`, `is_file`) | worker | local filesystem; the return gate (e) |
| 2 | `FramePort.probe` (ffprobe) | worker | `timeout_s=left` |
| 3 | `CAPTURE_FILE_LOCK` wait, phase 1 | worker | `acquire(timeout=left)`; (a) |
| 4 | Connection checkout, phase 1 (`QueuePool`, up to 30 s) | worker | (e) |
| 5 | Each cell grab, and inside it each FFmpeg and ffprobe run (`END_GAP`) | worker | `timeout_s=left`; one deadline per grab (`FRAME_GRAB`) |
| 6 | Tiling: decode, paste, labels and PNG encode | worker | (b') after it; (e). Measured 0.063 s for 25 cells |
| 7 | Temp write and `annotate.probe` (one full decode of the sheet) | worker | (c); (e) |
| 8 | `CAPTURE_FILE_LOCK` wait, phase 3 | worker | `acquire(timeout=left)`; (c) |
| 9 | Connection checkout, phase 3 | worker | (e) |
| 10 | Commit (SQLite `busy_timeout` 5,000 ms, `engine.py:68`) | worker | `COMMIT_WAIT_S` 6 |
| 11 | The caller's `join` steps | caller | `FRAMES_JOIN_STEP_S` 0.05 s each, up to `SHEET_RETURN_S + COMMIT_WAIT_S` |

Under D-601 A the call answers within 111 s and one join step, against the client's 120 s. An abandoned worker starts no FFmpeg run, because (a) fails once the deadline has passed.

### Pins that move

| Pin | Where | From → to | Row |
|---|---|---|---|
| `grab_frame` parameters | `tests/unit/test_domain_capture.py:921` (AC-134.1) | gains `"box"` last | 1 |
| Route census | `tests/e2e/test_api_openapi.py` `ROUTE_INDEX` (after `:53`, the frames row) and the count at `:118` | gains `("POST", "/api/v1/captures/sheet")` after `captures/frames`; 76 → 77 | 2a |
| Operation count | `tests/e2e/test_api_openapi.py` AC-134.17's `76` (about `:204`, in the test at `:192-233`) | 76 → 77 | 2a |
| Operation and action counts | `tests/e2e/test_api_downloads.py:372` (`ROUTE_COUNT_AFTER`) and `:377` (`ACTION_INDEX_AFTER`) | 76 → 77 and 73 → 74, with a MEU-135 comment line after `:375`'s | 2a |
| Valid bodies | `tests/e2e/test_api_bodies.py:48` (`_valid_body`) | gains `{"path": "C:/tmp/clip.mp4"}` for sheet | 2a |
| MCP action counts | `mcp-server/tests/action-index.test.ts:44`; `capture.test.ts:113`, `:890`, `:1053`; `convert.test.ts:60`; `m7-resource.test.ts:47` (title), `:56`, `:68` (title), `:76`; `audit/coverage.test.ts:36-39` (comment and title) | 73 → 74 | 2b |
| Built-server action count | `mcp-server/tests/audit/runner-fake-backend.test.ts:65` (title) and `:79` | 73 → 74, with a MEU-135 comment line | 2b |
| Capture action count | `capture.test.ts:131`, `:902` | 12 → 13 | 2b |
| Capture actions | `capture.test.ts:23-39` (`CAPTURE_ACTIONS`) | gains `{ action: "sheet", method: "POST", path: "/captures/sheet" }` after `frames`, with a comment | 2b |
| Frames workflow line | `capture.test.ts:930` (`FRAMES_TEXT_MARKERS[0]`, AC-134.15) | the probe → frames → image line → the `FRAMES_TEXT` line above (D-605) | 2b |
| Expected rows | `mcp-server/tests/fixtures.ts:225` (`minimalInput`) and `:313` (expected body) | gain `"avkit_capture.sheet": { action: "sheet", path: "C:/tmp/clip.mp4" }` and `{ path: "C:/tmp/clip.mp4" }` | 2b |
| Pending baseline | `mcp-server/tests/audit/coverage.test.ts:21` (`BASELINE_PENDING`) | `["avkit_convert.probe", "avkit_capture.crop", "avkit_capture.frames"]` → gains `"avkit_capture.sheet"` last, with a MEU-135 comment line | 2b |
| Frames row position | `capture.test.ts:1044-1058` (AC-134.16) | unchanged: `frames` is still directly after `crop`; AC-135.19 adds `sheet` directly after `frames` | — |
| Capture shared markers | `fixtures.ts:143` (`M7_MARKERS`) | unchanged: `sheet` carries the four marker words from `SHEET_TEXT` | — |

A pin in `tests/` moves in row 2a and one in `mcp-server/tests/` in row 2b. Each Red row greps the neighbours of each count pin again (Session 59 RULE-1, Session 62 RULE-4): every literal `73`, `76` or `12` next to an action or route list in `tests/`, `mcp-server/tests/` and `ui/tests/`, every test that walks `ACTION_INDEX`, `ROUTE_INDEX` or `CAPTURE_ACTIONS`, each pin's order and adjacency, and every signature-equality test over `FramePort`, `ImageAnnotatePort` or the adapters. **Absence pins (Session 61 RULE-3):** a grep of `tests/`, `mcp-server/tests/` and `ui/tests/` for `sheet` found no hit (`C:/Temp/av-kit/s63-plan-probes.txt`), so no test asserts `sheet` is absent. `models-availability.test.ts` has no `frames` hit and doesn't move. `runner-fake-backend.test.ts` launches the built server, so row 2b builds the MCP server before its Red run and row 3 builds it before the whole MCP suite. `ci.yml:65-66` already deselects `test_video_real_ffmpeg.py`, so CI needs no change.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The video path** goes from the request to `VIDEO_INPUT`, then to FFmpeg's argv and to the 201 body's `video.path`. It is never logged and never put in an error message. Its writer: the caller only.
- **The video's stem** goes through `import_stem` into the sheet name, which reaches the inbox, the row, the 201 body's `shot.path` and the Capture page. `import_stem` keeps word characters, space and `-`, so a control character or lone surrogate never reaches a name (AC-135.5).
- **The cell times** come from `FRAME_TIMES`; they reach `cells`, the labels drawn on the image and, as `TIMECODE`, error messages. One list feeds both `cells` and `labels`, so the two can't disagree (AC-135.10).
- **`grid` and `max_edge`** reach the cell size and the response's shot size; a refused value's message echoes nothing.
- **FFmpeg's stderr** is dropped by `FRAME_GRAB`, as for frames.
- **The sheet's pixels** come from FFmpeg's cell bytes and the label text only. The PNG is written with no metadata, so no path or EXIF reaches the file.
- **The sheet path** goes to the 201 body and the row. The `capture.sheet` line logs the shot id and cell count only.

### Spec text (D3)

| File | Lines at `7403f18` | Change |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | after the §Video sheet Tests row (`:1170`) | A Delivered note naming the mechanism ids, AC-135.1 to .20, D-601 and D-602 as ruled, the D-504 receipt and this plan folder, in the format of the Session 62 note (`:1140-1150`) |

Row 6 re-reads the anchor before it writes (Session 51 RULE-3) and cites the lines as they read then. `09` is CRLF.

### MEU-135 `capture-video-sheet`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `POST /captures/sheet` body | `schemas/captures.py` `CaptureSheetIn` | `SHEET_ROUTE`; times through `TIME_PARSE` in the service | `extra="forbid"`, fixed 422 |
| MCP `avkit_capture` `sheet` | `capture.ts` | `SHEET_MCP` | `.strict()`, refused before fetch |
| 201 body | `CaptureSheetOut` | `video`, `shot`, `spacing_ms`, `cells` keys only | — |
| `FramePort.grab_frame` | `ports/capture.py` | `CELL_GRAB` | — |
| `ImageAnnotatePort.sheet` | `ports/capture.py` | `SHEET_TILE` | — |
| Inbox file and row | `CaptureService` | `SHEET_NAME`, `SHEET_WRITE`, `CaptureSource.Video` | — |

#### Acceptance Criteria

Test names start `test_ac_135_<n>_` (Python) and `AC-135.<n>` (Vitest). New Python files are LF.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-135.1 | Unit | Type characterisation of row 1's names: `ImageAnnotatePort.sheet` has keyword-only `grid`, `cell_size` and `labels`; `FramePort.grab_frame` ends with keyword-only `box` defaulting to `None`; `FFmpegAdapter.grab_frame`'s and `CaptureAdapter.sheet`'s signatures equal the protocols' in name, kind, annotation and default. In `test_domain_capture.py`. It passes from row 1 and runs as a guard. | 09 Cells | Signature drift fails |
| AC-135.2 | Unit | `SHEET_SIZE`: exact cells for 1920×1080, 1440×1080 and 1080×1920 at grids 2 to 5 and `max_edge` 64, 1568 and 2576, matching the probe receipt (16:9 at 1568: 722×406, 482×271, 361×203, 288×162; at 2576: 1263×710, 841×473, 631×355, 505×284; 4:3 at 1568: 625×469, 417×313, 312×234, 250×188; 9:16 transposed; 16:9 at 64, grid 5: 12×7); for every shape of the probe, grid and edge, the sheet's long edge is at most `max_edge`, its area at most the budget, both cell edges at least 1, and one more pixel on the long cell edge breaks a bound; 1568 uses 1568 tokens and 1569 uses 4784; `None` and 0 sizes use 16:9. In `test_video_input.py`. | 09 Size | 1569 versus 1568; missing sizes |
| AC-135.3 | Unit | `SHEET_TIMES`: `sheet_spacing_ms` half cases each way (grid 2: span 14 → 4, 13 → 3; span 2 → 1, span 1 → 0); an exhaustive loop over grids 2 to 5 and spans 1 to 60 from starts 0 and 1000 (Session 62 RULE-5) finds every cell time in `[start, end)`, the list sorted and distinct, `k == grid²` when the span is longer than `grid²`, `k == grid² − 1` when they are equal, and `k ≤ min(grid², span)` always. In `test_video_input.py`. | 09 Cells | Spans shorter than, equal to and just over the cell count |
| AC-135.4 | Unit | `SHEET_LABEL`: `sheet_label(3, "00:00:09.999", 9_999)` is `3 00:00:09.999` and with spacing 10,000 is `3 00:00:09`; the label is always a prefix-preserving form of the timecode; `sheet_label_px` of 25 → 8 (3.5 rounds to 4, floored to 8), 75 → 11 (10.5 up), 74 → 10, 57 → 8, 58 → 8, 61 → 9 (8.54); `sheet_label_stroke` of 8 → 1, 15 → 2 (1.5 up), 14 → 1, 25 → 3 (2.5 up). In `test_video_input.py`. | 09 Labels | The 9,999 / 10,000 boundary and the half cases each way |
| AC-135.5 | Unit | `SHEET_NAME`: `standup`, 0, 7,200,021 → `standup-sheet-00h00m00s-02h00m00s`; 59,999 → `00h00m59s` (floored); 359,999,999 → `99h59m59s`; stem `Łodz` keeps `Łodz`; `CON` → `import_CON`; `..` → `import`; a stem holding a lone surrogate, one holding `\x07` and an empty stem each give a name with no surrogate, no control character and a non-empty stem (Session 53 RULE-1). In `test_video_input.py`. | 09 Writes | Reserved, empty, surrogate and control-character stems |
| AC-135.6 | Unit | `SHEET_TILE` with the real `CaptureAdapter`: four solid-colour PNG cells in a grid 2 at 40×30 land at (0,0), (40,0), (0,30), (40,30) (sampled away from the label); a 20×30 cell is centred with black bars of 10 px; a 80×60 cell is shrunk to 40×30; three cells in a grid 2 leave the fourth black; a label too long for its cell doesn't change any pixel of the next cell; the output is PNG of exactly 80×60 with no `text` or `exif` info; an undecodable cell raises, and mismatched `labels` and `cells` lengths raise `ValueError`. In the new `tests/unit/test_capture_sheet_adapter.py`. | 09 Cells, Labels | Undecodable bytes; a long label |
| AC-135.7 | Unit | Label contrast: a grid 2 sheet of all-white cells and one of all-black cells at 482×271; in each cell's label box, at least 2 % of pixels are within 32 of pure white and at least 2 % within 32 of pure black; the same sheet built with empty labels has 0 % of the contrasting colour in those boxes (the control). The labels drawn are exactly those passed, read from a recording wrapper around `ImageDraw.ImageDraw.text`, with the fill white and the stroke black and at least 1 px. In `test_capture_sheet_adapter.py`. | 09 Tests | The no-label control |
| AC-135.8 | Unit | `CELL_GRAB` with a recording fake `subprocess.run`: `grab_frame(…, box=(288, 162))` puts `-vf`, `scale=288:162:force_original_aspect_ratio=decrease:flags=lanczos` directly after `-frames:v 1`; an empty input-seek grab with a box runs `END_GAP`'s packet read and then a retry whose argv carries the same `-vf`; `box=None` and no `box` give argv equal to the AC-134.9 lists. In `test_media_adapter_frames.py`. | 09 Cells | `None` unchanged |
| AC-135.9 | Unit | `SHEET_CHECKS` with a recording fake `FramePort` and a temp inbox: each refusal (`video file not found`, the URL message, a bad time, `grid` 1, 6, `True`, `3.0` and `10**18`, `max_edge` 63, 2577, `True` and `10**18`, `the file could not be probed`, `not a video: no video stream`, `sheet needs a duration; this video has none`, `start: 3` and `end: 3.001` on a 3,000 ms video, `start must be before end` for 2/1 and 1/1) runs no grab, leaves the inbox empty and adds no row; each refusal before the probe records zero probes; magnitude bounds (Session 62 RULE-2): `start` 1e308, −1e308, `"100:00:00"` and 360000 give the time message, with zero probes; `end` equal to the duration is accepted. Each error is checked by membership and type first (Session 62 RULE-3), and `__context__` is `None`. In the new `tests/unit/test_capture_sheet_service.py`. | 09 Request, Errors | Every refusal records zero grabs |
| AC-135.10 | Unit | `SHEET_WRITE` trace (Session 55 RULE-3): a recording fake `FramePort` sees one `grab_frame` per cell in time order, each with `seek="input"`, `box` equal to `sheet_cell_size(…)`, and `timeout_s` equal to the time left; a recording fake `sheet` gets the cells in the same order, `grid`, `cell_size` and labels equal to `[sheet_label(c.cell, c.timecode, spacing_ms) for c in result.cells]`; the shot is `CaptureSource.Video` with the probed sheet's size; the 201 values come from one list. In `test_capture_sheet_service.py`. | 09 Cells, Writes, Labels | Labels and cells come from one list |
| AC-135.11 | Unit | All or nothing: `b""` on the fifth of nine cells gives `frame grab failed at` the fifth time; a cell without the PNG signature gives the same; a fake `sheet` raising gives the masked `the sheet could not be written`; an `InboxPathError` from the output probe gives the same masked error; an `os.replace` raising `OSError` gives it too; in each case no `.png`, no `.avkit-tmp` and no new row exist afterwards and a pre-existing shot is unchanged. In `test_capture_sheet_service.py`. | 09 Writes | Partial failure leaves nothing |
| AC-135.12 | Unit | Never overwrite: two calls for the same video and span in two threads, held together by a `threading.Barrier` in the fake `grab_frame`, give `clip-sheet-00h00m00s-00h00m03s.png` and `…_2.png`, each holding its own call's bytes; an inbox file of that name, a row of that name with no file, and another writer's `….png.avkit-tmp` each give `_2`; the other writer's temp is left byte for byte (temps are opened `"xb"`, Session 58 RULE-1). In `test_capture_sheet_service.py`. | 09 Writes | Never an overwrite |
| AC-135.13 | Unit | `SHEET_DEADLINE` with an injected clock, as AC-134.8 does for frames: (a) the clock past the deadline before the third grab fails with the third time and starts no third grab; (b) the clock passed during the second grab fails with the second time; (b') the clock passed during tiling fails with the last time; (c) a lock held by another thread until after the call returns fails with the last time while the lock is still held, and with the lock held from before phase 1, with the first time and no temp; (d) the clock passed at `os.replace` fails before the commit and leaves nothing; every `acquire` passes a `timeout`. (e) A body blocked in the fake `sheet` past `SHEET_RETURN_S` makes the call raise the last time's message within 2 s of real time; the worker is found as `avkit-sheet` in `threading.enumerate()` and joined after; a commit that ends inside `COMMIT_WAIT_S` returns the result; one past it gives the masked error. During a `frames` call the worker is still named `avkit-frames`. `SHEET_DEADLINE_S`, `SHEET_RETURN_S` and `COMMIT_WAIT_S` hold D-601's ruled values. In `test_capture_sheet_service.py`. | D-601; D-600 | The deadline passed before, during and after the grabs, in tiling, waiting for either lock, and before the commit |
| AC-135.14 | Integration | Real FFmpeg on generated clips: a grid 2 sheet of the counter clip (320×240, 25 fps, 3 s) at `max_edge` 1568 has cells at 375, 1125, 1875 and 2625 ms, and each cell's lower half equals by Pillow pixel equality the same region of a reference made by full decode of frame `ceil(t / 40)` through the same `scale` filter; the sheet is 1250×938, within the budget; an all-white and an all-black clip pass AC-135.7's contrast check on the real sheet; the raw `.h264` stream gives `sheet needs a duration; this video has none` with zero grabs (a recording wrapper around the real adapter); each source clip's SHA-256 is the same before and after the module's calls. In `test_video_real_ffmpeg.py`, which CI deselects. | 09 Cells, Tests | The no-duration refusal with zero grabs |
| AC-135.15 | API | `POST /captures/sheet` on the real stack with a fake `FramePort` set on `services.capture._frames` (returning a solid PNG of the box size) and the real `CaptureAdapter`: 201 with exactly `{video, shot, spacing_ms, cells}`, `video` with its five keys, `shot` with exactly `{id, path, width, height}`, each cell with exactly `{cell, time_ms, timecode}`; defaults give 9 cells; the file is in the inbox root. The fixed 422 for: an extra key, a missing `path`, `grid` 1, 6, `null`, `true` and `2.5`, `max_edge` 63, 2577 and `null`, a time `true`, `null` inside a list or an object, and route-level magnitude bounds `grid` and `max_edge` of `10**18`; `start` 1e308 gives the time message (422). In the new `tests/e2e/test_api_capture_sheet.py`. | 09 Request, Response | Each schema refusal |
| AC-135.16 | API | Errors on the real stack: `video file not found` for a missing file and a self-loop symlink under a marker folder, with no probe and no grab; the URL message; past the end; `sheet needs a duration; this video has none`; `frame grab failed at {t}`; the masked 503 for `FFmpegNotFoundError` and for a write failure. Under Session 54 RULE-2 the stack builds `HealthService` first, and the marker is absent from every error body, the log ring, captured stdout and stderr, with a positive control that logs the marker once and finds it. In `test_api_capture_sheet.py`. | 09 Errors | Marker absence with a positive control |
| AC-135.17 | API | After a `sheet` call, `GET /captures` and `GET /captures/{id}` show the shot with `source` `"Video"` and the sheet's width and height; `GET /captures/{id}/image` returns its bytes; a scan of the inbox after a new file is dropped in keeps the sheet's source `"Video"`. In `test_api_capture_sheet.py`. | 09 Writes | Scan doesn't turn `Video` into `Scan` |
| AC-135.18 | MCP | `SHEET_MCP`: the schema accepts `{action, path}` and every optional key and refuses before fetch: an extra key, an empty path, `grid` 1 and 6, `grid` 2.5, `max_edge` 63 and 2577, a negative time, a 33-character time and `start: null`. The call goes to `POST /captures/sheet` with the body minus `action`, with `ADD_TIMEOUT_MS` under D-601 A (the 30 s default under B or C). The description has its own four markers, says `cite times from cells`, `narrower start and end`, `no state is kept` and `can be missed`; `FRAMES_TEXT`'s workflow line names `sheet` between `probe` and `frames`. In `capture.test.ts`. | 09 Request, Description | The refusals |
| AC-135.19 | MCP | Parity and audit: `ACTION_INDEX` has 74 rows with `sheet` directly after `frames` and `frames` still directly after `crop`; transport parity: the fake backend's 201 body reaches the tool result with the same keys; `BASELINE_PENDING` ends with `avkit_capture.sheet`; `AUDIT_PLAN` has an offline `capture.sheet` step after `capture.frames` on the shared probe clip with `grid: 2`, and the coverage test sees every action covered. In `capture.test.ts` and `audit/coverage.test.ts`. | 09 Tests | Coverage fails if the step is missing |
| AC-135.20 | API | OpenAPI: `POST /api/v1/captures/sheet` with `CaptureSheetIn` and `CaptureSheetOut` in the regenerated snapshot; 77 operations; `--check` passes; `/sheet` is declared before `/{id}` in `routes/captures.py`. In `test_api_openapi.py`. | 09 Tests | The route-order check |

Under D-601 B every `5` in AC-135.9, .15 and .18 reads `4`, every `6` reads `5`, and the description reads `2-4`. Under D-602 B or C the look in row 3 is skipped and the handoff says so.

Guards (Session 54 RULE-1, Session 55 RULE-1): `test_domain_capture.py` and `test_domain.py` (core changes), `test_capture_frames_service.py`, `test_api_capture_frames.py` and `test_media_adapter_frames.py` (frames shares the refactored worker and the grab), `test_capture_service.py`, `test_api_capture_flatten.py`, `test_api_capture_region_import.py`, `test_api_capture_crop.py`, `test_api_captures.py` and `test_filesystem_media.py` (AC-8.12's signature pin) run in rows 1 and 3. Every caller of what is extended: `grab_frame` is called by `_grab_frames` (`services/capture.py:880`) and `FFmpegAdapter.grab_frame`'s own retry; `_reserve_frames` and `_publish_frames` by `_write_frames` (`:816`) only; the gate loop by `frames_from_video` (`:642`) only.

#### Spec Sufficiency

| Behavior | Classification | Resolution |
|---|---|---|
| Request and bounds | Local Canon | 09 Request; D-599 |
| Cell times and spacing | Local Canon | 09 Cells; D-598 |
| Cell grab at size | Research-backed, probed | 09 Cells; D-595 (D-504 probe) |
| Tiling and labels | Local Canon | 09 Labels; D-594, D-597 |
| Size budget | Human-approved, probed | 09 Size; D-596 (size probe) |
| Grid cap and time limit | Human | D-601 (D-504 probe) |
| Legibility by eye | Human | D-602 |
| Write and concurrency | Local Canon | 09 Writes; D-600 |
| Name | Local Canon | 09 Writes; D-606 |
| Response | Local Canon | 09 Response; D-607 |
| MCP shape and description | Local Canon | 09 Description; D-605, D-607 |
| Audit pending list | Local Canon | D-603 (D-499 A terms) |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/services/video_input.py` | Modify | `SHEET_SIZE`, `SHEET_TIMES`, `SHEET_LABEL`'s pure parts, `SHEET_NAME`; `SHEET_GRID_MIN`, `SHEET_GRID_MAX`, `SHEET_GRID_DEFAULT`, `SHEET_TOKENS_STANDARD`, `SHEET_TOKENS_HIGH`, `PIXELS_PER_TOKEN`, `SHEET_FALLBACK_SIZE`, `SHEET_LABEL_PERCENT`, `SHEET_LABEL_MIN_PX`; `SheetCell`, `SheetShot`, `VideoSheet` |
| `packages/core/src/avkit_core/ports/capture.py` | Modify | `ImageAnnotatePort.sheet`; `FramePort.grab_frame`'s `box` |
| `packages/core/src/avkit_core/services/capture.py` | Modify | `sheet_from_video`, `_sheet_body`, `_grab_cells`, `_run_gated` (moved out of `frames_from_video`), `_reserve_frames` and `_publish_frames` parametrized; `SHEET_WORKER`, `SHEET_DEADLINE_S`, `SHEET_RETURN_S`, `SHEET_NOT_WRITTEN`, `SHEET_NO_DURATION`, `SHEET_GRID_RANGE` (`SHEET_CHECKS`, `SHEET_WRITE`, `SHEET_DEADLINE`) |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | Modify | `CELL_GRAB` in `grab_frame` and `_grab_once` |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | Modify | `SHEET_TILE`: `CaptureAdapter.sheet` and the label drawing |
| `packages/api/src/avkit_api/routes/captures.py`, `schemas/captures.py` | Modify | `SHEET_ROUTE` |
| `openapi.committed.json` | Regenerate | The sheet route |
| `mcp-server/src/toolsets/capture.ts`, `registry.ts` | Modify | `SHEET_MCP`, `SHEET_TEXT`, the `FRAMES_TEXT` line, the `ACTION_INDEX` row and the timeout list |
| `mcp-server/scripts/audit/plan.ts` | Modify | The offline `capture.sheet` step after `capture.frames` (`:1639`) |
| `tests/unit/test_capture_sheet_service.py`, `test_capture_sheet_adapter.py` | New | AC-135.6, .7, .9 to .13 |
| `tests/e2e/test_api_capture_sheet.py` | New | AC-135.15 to .17 |
| `tests/unit/test_video_input.py`, `test_media_adapter_frames.py`, `test_domain_capture.py` | Modify | AC-135.1 to .5, .8; the `grab_frame` pin |
| `tests/integration/test_video_real_ffmpeg.py` | Modify | AC-135.14 |
| `tests/e2e/test_api_openapi.py`, `test_api_downloads.py`, `test_api_bodies.py` | Modify | §Pins that move; AC-135.20 |
| `mcp-server/tests/capture.test.ts`, `convert.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `audit/coverage.test.ts`, `audit/runner-fake-backend.test.ts` | Modify | AC-135.18, .19; §Pins that move |
| `docs/build-plan/09-screenshot-capture.md` | Modify | §Spec text |

Every function a mechanism names is in this table and in the gate's scope (Session 61 RULE-4). `wiring.py` doesn't change: `CaptureService` already gets `annotate` and `frames`. Line endings at `7403f18` (`C:/Temp/av-kit/s63-plan-probes.txt`): CRLF are `ports/capture.py`, `services/capture.py`, `media/adapter.py`, `capture/adapter.py`, `routes/captures.py`, `schemas/captures.py`, `openapi.committed.json`, `capture.ts`, `registry.ts`, `scripts/audit/plan.ts`, `capture.test.ts`, `convert.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `coverage.test.ts`, `runner-fake-backend.test.ts`, `test_domain_capture.py`, `test_api_openapi.py`, `test_api_downloads.py`, `09` and the grouping. LF are `video_input.py`, `test_video_input.py`, `test_media_adapter_frames.py`, `test_video_real_ffmpeg.py`, `test_api_bodies.py`, `meu-status.yaml`, `meu-registry.md` and `docs/BUILD_PLAN.md`. Row 0 measures every file again with Python bytes, and every row writes with `newline=""` or by byte replacement. New files are LF.

### Project files

- `docs/execution/plans/2026-11-11-capture-video-sheet/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `session-gate.ps1`, `look.py`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, and the grouping tracker row (`:103`). If another session holds any of them dirty when row 6 runs, row 6 byte-edits only MEU-135's fields and proves them with `render --check` (Session 61 RULE-5).
- `.agent/context/handoffs/2026-11-11-capture-video-sheet-*.md`, `docs/execution/reflections/2026-11-11-capture-video-sheet-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

Not this session's, and never opened: `docs/proposals/2026-11-10-download-logic-divergence-report.md`. Anything another session leaves dirty is named to Mat before any commit.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Export copy | Feature | MEU-136 (Session 64) | D-593 |
| The description eval | Eval | Session 64 | Grouping D-505 |
| Non-square sample aspect and rotation tags in the cell size | Feature | None | D-596: the stored size is used |
| Change detection, scene cuts | Feature | None | Design D-2 |
| A GUI for sheet | UI | None | Design D-5: a sheet is an ordinary shot on the Capture page |
| `_run_with_progress`'s decoding | Bug | Raised to Mat in Session 62's handoff | D-604: left alone unless Mat rules |
| A URL or remote video | Feature | None | 09 Request |
| `MCP-AUDIT-BASELINE-PENDING-CROP` and the pending actions | Audit | The next authoritative update | D-603; `--update-baseline` needs Mat's words |
| `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | MCP | Its own session | D-604 |
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`, `CAPTURE-EXIF-SCANNED-ORIENTATION` | Bug | Their own sessions | D-604: recorded if seen, never fixed here |

## BUILD_PLAN.md Audit

MEU-135 is in `.agent/context/meu-status.yaml` (`:3532`, phase 9, band P2, matrix item 9.41, anchor `video-sheet`, `pending`). Row 6 sets it `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at row 6 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s63-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s63-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Checks that D-601 and D-602 carry Mat's ruling in §Decision Log (S14). **The ruling format:** once Mat rules, the entry's `chosen` starts with the option letter, as `"A: …"`, `"B: …"` or `"C: …"`, and its `human_message_reference` becomes `"USER_EXPLICIT <date> '<Mat's words>'"`. A `chosen` that starts `Pending Mat's ruling`, or a `null` reference, is unruled. Checks the queue (S8): MEU-134 is `approved` in `meu-status.yaml`, MEU-135 is `pending`, and `7403f18` (`feat(capture): probe a local video and take still frames from it`) is an ancestor of `HEAD`, which meets the grouping's "Session 62 has closed" (`:92`).
2. Checks the shapes this plan relies on, by name: `FramePort.grab_frame` without `box`, `_grab_once` with no `-vf`, `frames_from_video`'s `threading.Thread(…, name=FRAMES_WORKER…)`, `_reserve_frames`, `_publish_frames`, `_import_dest`, `CAPTURE_FILE_LOCK`, `TMP_SUFFIX`, `_upsert_shot`, `CaptureSource.Video`, `frame_times`, `import_stem`, `_load_font`, `REGION_MAX_EDGE_MIN` 64 and `MAX` 2576, `ADD_TIMEOUT_MS` and its selection naming `frames` in `registry.ts`, `BASELINE_PENDING` as the three-key list above, and the built-server count `73` in `runner-fake-backend.test.ts`; and that `sheet_from_video`, `ImageAnnotatePort.sheet`, `sheet_cell_size`, `SHEET_` names and `/sheet` are absent. The anchors step also stops when a new file of §Files Modified already exists.
3. Creates `C:\Temp\av-kit\s63\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256; the other session's proposal, if dirty, is hashed by `Get-FileHash` and never opened.
4. Runs `uv sync --frozen --offline --all-packages`, and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair is over 1024 B and runs `ffmpeg -version` offline (S4), and that Pillow is 13.0.0 and `segoeui.ttf` is in the Windows fonts folder.
5. Records the line endings and SHA-256 of every file in §Files Modified to `s63-anchors.txt`, which row 1 reads before it writes.
6. Captures the base Python suite to `s63-base-py.txt`, builds the MCP server (`s63-base-mcp-build.txt`) and captures the base MCP suite to `s63-base-mcp.txt`, and runs `ruff check packages/ tests/` to `s63-base-ruff.txt`. The suites' own failures are recorded, not fatal.
7. Runs the `red-check.py` and `identity.py` selftests, each on its own fixture copy (Session 56 RULE-4).

The scripts are copies of Session 62's, with this plan's values:

- **`red-check.py`.** Session 62's, with `DECLARED_NEW` holding `sheet_cell_size`, `sheet_spacing_ms`, `sheet_label`, `sheet_label_px`, `sheet_label_stroke`, `sheet_name`, `SheetCell`, `SheetShot`, `VideoSheet`, `SHEET_GRID_MIN`, `SHEET_GRID_MAX`, `SHEET_GRID_DEFAULT`, `SHEET_TOKENS_STANDARD`, `SHEET_TOKENS_HIGH`, `PIXELS_PER_TOKEN`, `SHEET_FALLBACK_SIZE`, `SHEET_LABEL_PERCENT`, `SHEET_LABEL_MIN_PX`, `sheet_from_video`, `SHEET_WORKER`, `SHEET_DEADLINE_S`, `SHEET_RETURN_S`, `SHEET_NOT_WRITTEN`, `SHEET_NO_DURATION`, `SHEET_GRID_RANGE`, `CaptureSheetIn`, `CaptureSheetOut`, and the selftest fixtures' names. These excuse a non-required block only. Its boundary fixture is AC-135.1 against AC-135.10. A red-check failure names the failing test (Session 50).
- **`identity.py`.** `PLAN` is this folder. `FFMPEG_PAIR` is bound, because the real-FFmpeg module reads it. Its selftest binds `session-gate.ps1`, the new test modules, `09`, the register's renders and the grouping.
- **`PROJECT_ARTIFACTS`.** This plan's `*.md`, the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`.

### 2. Type-only first, then Red, then Green (rows 1 to 3)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2).** In `video_input.py`: every sheet constant at its value, `sheet_cell_size` returning `(1, 1)`, `sheet_spacing_ms` and `sheet_label_px` and `sheet_label_stroke` returning 0, `sheet_label` and `sheet_name` returning `""`, and the three dataclasses. In `ports/capture.py`: `ImageAnnotatePort.sheet` and `FramePort.grab_frame`'s `box`. `FFmpegAdapter.grab_frame` gains `box` and ignores it; `CaptureAdapter.sheet` returns `b""`. `CaptureService.sheet_from_video` returns an empty `VideoSheet`, and the `SHEET_*` constants hold D-601's ruled values. The `grab_frame` pin moves. No route, schema or MCP change, and no refactor of the frames worker yet. Its check runs `test_domain_capture.py`, `test_domain.py`, `test_capture_frames_service.py`, `test_media_adapter_frames.py`, `test_capture_service.py`, `test_filesystem_media.py`, `ruff` and `pyright` on the touched packages.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error, an import error, a fixture error and a required test that fails on a missing name. The Reds call row 1's stubs, whose values are wrong, or post to a route that answers 404 or 405, so each fails on a status or value assertion. The integration Red generates its clips in a module fixture first; a clip that fails to generate is a setup failure and stops the row.
- **`--require` matches a test name up to a non-digit boundary.** Rows 2a and 2b: `AC-135.2` to `.20`, across the pytest and Vitest receipts. AC-135.1 is a characterisation of row 1 and must pass in row 2a.
- **Expectations stay immutable in Green.** No test file changes in row 3. The count pins move in the Red rows, so they fail in the Red receipt and pass in Green.
- **The real-FFmpeg module.** Rows 2a and 3 run it explicitly; it reads only `packaging/ffmpeg-win64/` and writes only under pytest's `tmp_path`. Under D-602 A, row 3 then renders the three look sheets with a plan-local script into `C:/Temp/av-kit/s63/look/`, outside the repo, and the coordinator asks Mat to look.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`: §1.
- `session-gate.ps1` (H1-2): below.
- `look.py` (row 3's last step, under D-602 A only): generates a white and a black 1280×720 clip and a 1080×1920 clip with the pinned FFmpeg, and writes `white-grid3.png`, `black-grid3.png` and `tall-grid5.png` to `C:/Temp/av-kit/s63/look/` through the real `FFmpegAdapter.grab_frame` with the cell box and `CaptureAdapter.sheet` with the `SHEET_LABEL` labels. It builds no `CaptureService`, so it writes no inbox file and no row, and nothing in the repository. `identity.py` binds it.

### Session gate (H1-2)

`session-gate.ps1` is Session 62's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s63-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`. Before it runs, the coordinator lists every changed path against the gate's scope (Session 60 RULE-4).

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types` (`pyright`), `py-lint` (`ruff check packages/ tests/`), `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests`, `openapi` (`export_openapi.py --check openapi.committed.json`), `mcp-types`, `mcp-build`, `mcp-tests`, `state-render`, `issues-render`, `status-canon` (`ui/tests/unit/layout-canon.test.ts` and `queue-canon.test.ts`, which read `meu-status.yaml` and `docs/BUILD_PLAN.md` directly, and row 6 changes both) |
| Runtime | `real-ffmpeg`: `pytest tests/integration/test_video_real_ffmpeg.py` |
| Skipped with reason | `ui-types`, `ui-lint`, the rest of `ui-tests`, `ui-build` and `ui-electron` (no `ui/` file changes; `status-canon` runs the only UI tests that read a file this session writes), `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes) |

`py-tests` excuses only ids that row 0's receipt shows failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 6 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, `ffmpeg -version` fails, Pillow isn't 13.0.0, or `segoeui.ttf` is missing | Stop: a fetch is a download and needs Mat's words |
| S5 | Any network request, download or upload, including the live audit | Stop and tell Mat |
| S6 | A real-FFmpeg test is slower than 60 s, or a clip fails to generate | Stop and tell Mat with the receipt; don't raise a timeout to make it pass |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | At row 0, MEU-134 isn't `approved`, MEU-135 isn't `pending`, or `7403f18` isn't an ancestor of `HEAD` | Stop; the queue is wrong |
| S9 | A count pin outside §Pins that move fails because of the new route or action | Add it to the row with its AC, grep its neighbours, and name it in the handoff |
| S10 | A path, FFmpeg's stderr or a caller's raw time reaches a log line, an error body or the console in a way it didn't before | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |
| S11 | A row 0 shape check fails, or a new name already exists | Stop; amend this plan through the plan review before row 1 |
| S12 | A row would change 09's rule text, an AC, or an existing route's behaviour (frames included, after the D-600 refactor) | Stop; brief Mat with a recommendation and a do-nothing option (Session 59 RULE-3) |
| S13 | AC-135.14's pixel comparison fails because the scaled grab differs from the scaled full-decode reference | Stop and tell Mat with the cell and frame numbers; `CELL_GRAB`'s filter may differ from the reference path |
| S14 | At row 0, D-601 or D-602 has no ruling from Mat in §Decision Log | Stop; ask Mat through the Human Decision Protocol |
| S15 | At row 6, `meu-status.yaml`, `meu-registry.md` or `BUILD_PLAN.md` changes any line outside MEU-135's entries and rows | Stop and tell Mat |

## Decision Log

> [!WARNING]
> Mat's request and the video stills design settle the scope, and the grouping (D-500 to D-505) placed this MEU. D-593 to D-600 and D-603 to D-607 didn't need Mat: each is autonomous, with its alternatives in `reasoning`. D-601 and D-602 are Mat's. D-589 to D-592 are claimed (`C:/Temp/av-kit/s63-plan-dids.txt`), so this block starts at D-593.
>
> Carried and not relisted in the block: every grouping §8 row, D-500 to D-505, with stage `grouping`. Of those, D-502 and D-504 bear on this session; the reflection carries all six, D-500 as human (`USER_EXPLICIT 2026-11-09 'all recommendations accepted, proceed'`) and D-501 to D-505 as autonomous, because the closeout validator reads every §8 row of the declared grouping. The design's own D-1 to D-20 are a separate namespace, cited as "design D-n" in prose only. The probe (`C:/Temp/av-kit/s63-plan-decision-probe.txt`), run with this plan and the grouping as sources (Session 54 RULE-5), shows what the closeout's decision flags pull in.

```yaml
decision_log:
  - id: D-593
    stage: planning
    question: "Does MEU-136 capture-export-copy ride with Session 63?"
    resolution: autonomous
    class: two-way
    chosen: "No. MEU-135 runs alone; MEU-136 and the grouping D-505 description eval stay in Session 64"
    source_tag: Local Canon
    precedents:
      - "grouping :71 — MEU-136 may ride if the plan comes out small; decided when Session 63 is planned"
      - "grouping D-505 — the description eval runs with the last session of the grouping"
    research:
      engine: none
      sources: []
    reasoning: "The plan isn't small: 20 ACs across core, two adapters, the API and MCP, a frames worker refactor and an OpenAPI regeneration, calibrated near Session 62's 13.2M execution. MEU-136 is a UI action with its own Electron E2E, which this session otherwise doesn't run. Riding would add a second surface and a second review subject to one loop. Two-way."
    human_message_reference: null
  - id: D-594
    stage: planning
    question: "Where do the tiling and the labels run?"
    resolution: autonomous
    class: two-way
    chosen: "A new ImageAnnotatePort.sheet method, implemented by CaptureAdapter, that takes the cells as PNG bytes and returns the sheet as PNG bytes"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:145 — _load_font, the annotate font 09 names"
      - "packages/core/src/avkit_core/ports/capture.py:19 — ImageAnnotatePort already holds view, crop and write_upright_png"
      - "pyproject.toml:37 — pyright covers packages only; the test fakes are duck-typed"
    research:
      engine: none
      sources: []
    reasoning: "Core has no Pillow, so tiling can't run in the service. A new SheetPort would add a wiring keyword and a second adapter object for one method, where ImageAnnotatePort already owns every other Pillow operation and the font. Returning bytes keeps every inbox write in the service's FRAME_WRITE pattern. Only CaptureAdapter implements the protocol. Two-way."
    human_message_reference: null
  - id: D-595
    stage: planning
    question: "How is each cell grabbed at the cell size?"
    resolution: autonomous
    class: two-way
    chosen: "FramePort.grab_frame and FFmpegAdapter.grab_frame gain a keyword-only box, default None; with a box, the argv gains -vf scale=W:H:force_original_aspect_ratio=decrease:flags=lanczos after -frames:v 1, END_GAP's retry included; with None the argv is unchanged"
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/s63-d504-probe-receipt.txt — this filter gave 288x162 cells for all 25 grabs of the 4K file in 10.23 s; bicubic 9.00 s"
      - "09 :1163 — ffmpeg grabs each cell already scaled to the cell size"
      - "tests/unit/test_domain_capture.py:921 — the grab_frame parameter pin, which gains box"
    research:
      engine: none
      sources: []
    reasoning: "Scaling in FFmpeg keeps 25 full 4K frames out of Python memory. Lanczos costs 1.2 s more than bicubic over 25 cells and gives sharper small cells; either is far under the deadline. A separate grab_cell method would duplicate END_GAP. Making box keyword-only and defaulted leaves every frames call byte-identical, which AC-134.9 keeps proving. A source smaller than the cell is scaled up to fit; a min expression to stop that needs filter quoting and leaves small sources in wide black bars. Two-way."
    human_message_reference: null
  - id: D-596
    stage: planning
    question: "How is the cell size computed so the sheet meets 09's size rule?"
    resolution: autonomous
    class: two-way
    chosen: "SHEET_SIZE: long = max_edge // grid, short = half_up of long times the source's short-to-long ratio, then long drops by 1 while grid squared times long times short exceeds tokens times 750; tokens is 1568 when max_edge is at most 1568, else 4784; orientation follows the source; a missing size is 16:9"
    source_tag: Human-approved
    precedents:
      - "09 :1165 — long edge at most max_edge, w x h / 750 at most 1568 tokens, or 4784 when max_edge exceeds 1568"
      - "C:/Temp/av-kit/s63-size-probe-receipt.txt — 480 cases, 0 failures, each maximal"
      - "Session 60 RULE-3 — one integer construction for grid, max_edge and the token cap"
    research:
      engine: none
      sources: []
    reasoning: "Integers only, so no float rounding can push a sheet one pixel over the budget. Decrementing the long edge keeps the aspect and stops at the largest legal cell, which the probe proves for every shape tried. Sample aspect and rotation are left out: MediaInfo gives the stored size, and fitting by it is what the grab's scale filter does too. Two-way."
    human_message_reference: null
  - id: D-597
    stage: planning
    question: "What does each label say, how big is it, and where is it drawn?"
    resolution: autonomous
    class: two-way
    chosen: "Cell number, a space, and HH:MM:SS, with .mmm when spacing_ms is under 10000; 14 percent of the cell height, half up, at least 8 px, made smaller until it fits the cell width; stroke a tenth of the size, half up, at least 1; white fill, black stroke, top-left, drawn on the cell's own canvas"
    source_tag: Research-backed
    precedents:
      - "09 :1164 — number and HH:MM:SS, .mmm when the spacing is under 10 s, outlined text in the _load_font font, height scales with the cell"
      - "C:/Temp/av-kit/s63-size-probe-receipt.txt — the widest label fits at every grid at the default max_edge; 9:16 grid 5 fits at 21 px"
      - "C:/Temp/av-kit/s63/s63-probe-sheet-fit_lanczos.png — 22 px labels on real 4K footage"
    research:
      engine: none
      sources: []
    reasoning: "White with a black outline reads on both light and dark frames, which is what the legibility test checks. Drawing on the cell canvas clips a label that can't fit at the 8 px floor (max_edge 200 and grid 4 or more) to its own cell, so it never covers a neighbour's picture. Top-left keeps the label off the centre of the frame. Two-way."
    human_message_reference: null
  - id: D-598
    stage: planning
    question: "What happens when the span has fewer milliseconds than cells?"
    resolution: autonomous
    class: two-way
    chosen: "Follow 09 literally: FRAME_TIMES with count grid squared, duplicates collapse, cells lists the distinct times numbered 1 to k, and the remaining cells stay black"
    source_tag: Local Canon
    precedents:
      - "09 :1163 — cell times sit at the midpoints, as in count frames"
      - "packages/core/src/avkit_core/services/video_input.py:203 — frame_times caps at end minus 1 and de-duplicates"
    research:
      engine: none
      sources: []
    reasoning: "A refusal would add an error 09 doesn't list, and stretching the times would break the midpoint rule. With a span equal to the cell count the last midpoint caps onto the one before it, so k is one less; with a longer span k is the full count. The sheet keeps its full size, so the size rule is unchanged. Two-way."
    human_message_reference: null
  - id: D-599
    stage: planning
    question: "What are the sheet's new messages and schema bounds?"
    resolution: autonomous
    class: two-way
    chosen: "New fixed messages: sheet needs a duration; this video has none; grid must be 2 to 5; the sheet could not be written (masked 503). Reused: every VIDEO_INPUT, TIME_PARSE and frames message, frame grab failed at T, and max_edge must be between 64 and 2576. The schema makes grid and max_edge non-optional StrictInt with ge and le, defaults 3 and 1568"
    source_tag: Local Canon
    precedents:
      - "09 :1162 — times, errors and video input follow Video frames"
      - "packages/core/src/avkit_core/domain/capture.py:230-232 — the max_edge message"
      - "packages/api/src/avkit_api/schemas/captures.py:264 — CaptureFramesIn, StrictInt with ge and le"
    research:
      engine: none
      sources: []
    reasoning: "The no-duration message drops frames' 'so use at', which has no meaning for sheet. Non-optional fields refuse null at REST as MCP's optional number refuses it, so the two agree. The service range-checks again and refuses bools, because it is callable without the schema. A tiling or output-probe failure is masked like any other write failure, since its cause names nothing the agent can act on. Two-way."
    human_message_reference: null
  - id: D-600
    stage: planning
    question: "How does sheet get frames' deadline and all-or-nothing write without copying them?"
    resolution: autonomous
    class: two-way
    chosen: "Move frames' worker and return-gate loop into one helper, _run_gated, parametrized by worker name, deadline and return time; parametrize _reserve_frames and _publish_frames on names, failure times and source; sheet reserves one name, grabs every cell in memory, tiles, checks the deadline again, writes and probes one temp, then publishes"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:642-700 — frames_from_video's worker and return gate"
      - "packages/core/src/avkit_core/services/capture.py:852 and :914 — _reserve_frames and _publish_frames"
      - "09 :1166 — through the Video frames write pattern"
    research:
      engine: none
      sources: []
    reasoning: "A copy of the 60-line gate loop would let the two drift; a shared helper keeps D-587's answer-by guarantee in one place, and AC-134.8 keeps proving it for frames. No test names the private helpers (grep at plan time), so the refactor moves no pin. Holding 25 small cells in memory is about 4 MB at 288x162 and avoids 25 temps. The added check after tiling stops a slow tile from publishing late. Two-way."
    human_message_reference: null
  - id: D-601
    stage: planning
    question: "Does the grid cap stay 5, and how long may a sheet call run?"
    resolution: human
    class: two-way
    chosen: "A: keep cap 5, the 120 s client timeout (ADD_TIMEOUT_MS), SHEET_DEADLINE_S 100, SHEET_RETURN_S 105, COMMIT_WAIT_S 6"
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/s63-d504-probe-receipt.txt — 5x5 sheet of the 2 h 4K HEVC file in 10.30 s, no failure"
      - "C:/Temp/av-kit/s63-d504-prekey-run.txt — 25 pre-keyframe grabs in 8.78 s"
      - "mcp-server/src/toolsets/registry.ts:390-396 — ADD_TIMEOUT_MS selection, frames already on it"
      - "grouping D-504 — a plan may lower a cap from its measurement and names it at the human gate"
    research:
      engine: none
      sources: []
    reasoning: "This is a governance value that design D-4 set with Mat, and D-504 says a change to it is named at the human gate, so it is Mat's. 10.3 s is about a third of 30 s here, so lowering the cap isn't forced. A gives a slower machine about ten times the margin with the values Mat ruled for frames. B keeps the default timeout at the cost of 16 cells per call. C keeps today's timeout with a deadline that still prevents late writes. Under every option the call answers before the client gives up. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-11 'plan accepted with all recommendations, proceed'"
  - id: D-602
    stage: planning
    question: "How is label legibility checked by eye?"
    resolution: human
    class: two-way
    chosen: "A: Mat looks at three rendered sheets (white grid 3, black grid 3, 9:16 grid 5) in C:/Temp/av-kit/s63/look/ after row 3"
    source_tag: Local Canon
    precedents:
      - "09 :1170 — labels legible on a mostly white and a mostly black frame"
      - "C:/Temp/av-kit/s63/s63-probe-sheet-fit_lanczos.png — the plan-time probe sheet"
    research:
      engine: none
      sources: []
    reasoning: "Legible is a judgment a pixel test can't make: the contrast tests prove fill and outline are both present, not that the characters read. Only Mat can say a label reads, so it is Mat's. A costs a minute and covers the two backgrounds 09 names and the smallest default label. B covers real footage only. C relies on contrast alone. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-11 'plan accepted with all recommendations, proceed'"
  - id: D-603
    stage: planning
    question: "Does avkit_capture.sheet join the audit's pending list, and how is it covered?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: BASELINE_PENDING gains avkit_capture.sheet after frames on D-499 A's terms, never --update-baseline; AUDIT_PLAN gains an offline capture.sheet step after capture.frames on the shared probe clip with grid 2"
    source_tag: Local Canon
    precedents:
      - "mcp-server/tests/audit/coverage.test.ts:15-21 — D-499 A and the three pending keys in ACTION_INDEX order"
      - "mcp-server/scripts/audit/plan.ts:1639 — the capture.frames step"
      - "known-issues MCP-AUDIT-BASELINE-PENDING-CROP — the authoritative update stays blocked"
    research:
      engine: none
      sources: []
    reasoning: "The committed baseline can't gain the action without a live, authoritative run, which needs Mat's words and is blocked by YOUTUBE-CAPTIONS-IP-BLOCK. The pending list is the ruled way to serve a new action meanwhile. Grid 2 keeps the offline step to four grabs of the 2 s clip. Two-way."
    human_message_reference: null
  - id: D-604
    stage: planning
    question: "Do the capture known issues, MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL or _run_with_progress belong in this session?"
    resolution: autonomous
    class: two-way
    chosen: "No. Neither capture issue can touch the sheet, the descriptions issue is its own session, and _run_with_progress is left alone unless Mat rules"
    source_tag: Local Canon
    precedents:
      - "known-issues CAPTURE-EXIF-SCANNED-ORIENTATION :4520 — a scanned JPEG's EXIF; the sheet is a PNG written with no metadata"
      - "known-issues CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST :4603 — the sheet is probed before publish and its temp ends .avkit-tmp"
      - "known-issues MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL :4643"
    research:
      engine: none
      sources: []
    reasoning: "Fixing unrelated issues here would widen the review subject. The sheet is written through the frames pattern, so it adds no new way to hit either capture issue. An observation of any of them goes in the handoff. Two-way."
    human_message_reference: null
  - id: D-605
    stage: planning
    question: "What do the sheet and frames descriptions say?"
    resolution: autonomous
    class: two-way
    chosen: "SHEET_TEXT with its own four markers and the body in SHEET_MCP; FRAMES_TEXT's workflow line becomes probe, then sheet to find the moment, then frames, then image, which moves the AC-134.15 literal at capture.test.ts:930"
    source_tag: Local Canon
    precedents:
      - "09 :1137 — workflow probe, sheet, frames, image"
      - "09 :1168 — cite times from cells, zoom by narrowing, no state, events between samples can be missed"
      - "09 :1147 — Session 62's note says Session 63 adds sheet to the workflow line"
    research:
      engine: none
      sources: []
    reasoning: "09 names the four-step workflow and Session 62's note deferred sheet's place in it to this session, so the frames line changing is the contract, not a change to it. The pin moves in row 2b with its reason in the handoff; AC-134.15's text, which says the line names avkit_convert probe, still holds. Two-way."
    human_message_reference: null
  - id: D-606
    stage: planning
    question: "How are the sheet's start and end written in its name?"
    resolution: autonomous
    class: two-way
    chosen: "VIDEO_STEM-sheet-START-END.png with each time as two-digit hours, minutes and seconds, floored, then _2 through _import_dest"
    source_tag: Local Canon
    precedents:
      - "09 :1166 — HHhMMmSSs times, then _2"
      - "packages/core/src/avkit_core/services/video_input.py:217 — frame_name and import_stem"
    research:
      engine: none
      sources: []
    reasoning: "Flooring keeps the name a prefix-true reading of the span; rounding could name a second the span doesn't reach. Two sheets of spans that differ only below a second share a name and get _2, which never overwrites. Two-way."
    human_message_reference: null
  - id: D-607
    stage: planning
    question: "What exactly does the 201 body hold, and what is logged?"
    resolution: autonomous
    class: two-way
    chosen: "video reuses frames' five-key shape; shot holds id, path, width and height from the probed sheet; spacing_ms; cells hold cell, time_ms and timecode; capture.sheet logs the cell count and shot id only"
    source_tag: Local Canon
    precedents:
      - "09 :1167 — the response shape, no image bytes"
      - "packages/api/src/avkit_api/schemas/captures.py:285 — CaptureFramesVideoOut"
    research:
      engine: none
      sources: []
    reasoning: "Reusing the video shape keeps one meaning for video in both capture responses. The probed size, not the computed one, is what the file holds. Logging no path keeps NO_RAW_OUTPUT. Two-way."
    human_message_reference: null
```

## Research References

- `docs/build-plan/09-screenshot-capture.md:1152-1170` (the contract) and `:1115-1150` (§Video frames and its Delivered note).
- `_inspiration/video-stills/design.md`: §6.4, §6.6, §11 and design D-4, D-9 to D-14.
- The grouping file: §3 (`:69-71`), §6 tracker (`:103`), §8 (`:118-133`).
- Session 62's plan and scripts (`docs/execution/plans/2026-11-10-video-probe-frames/`), Session 58's (`2026-11-08-capture-region-import/`).

## Planning receipts

- `C:/Temp/av-kit/s63-plan-probes.txt` (`C:/Temp/av-kit/s63/plan_probes.py`): `HEAD`, line endings and SHA-256 of the target files at `7403f18`, and the `sheet` absence grep over the three test trees (0 hits).
- `C:/Temp/av-kit/s63-plan-dids.txt`: the D-id and AC sweep; D-593 up and AC-135 are free.
- `C:/Temp/av-kit/s63-d504-probe-receipt.txt` (`C:/Temp/av-kit/s63/probe_sheet_timing.py`): the D-504 probe. FFmpeg `packaging/ffmpeg-win64/ffmpeg.exe` SHA-256 `c46215f8889634396f0ac0acac738ef2145175e5b6caf28b3daa8ac9a9980c5f`; video `C:/Temp/av-kit/s62/probe2/hevc4k_2h.mp4`, 11,285,707,465 B; 25 cells from 144,000 to 7,056,021 ms; Lanczos: grabs 10.23 s, 0.409 s each, slowest 0.73 s, 0 failures, cells 288×162, tile and save 0.063 s, total 10.30 s; bicubic: 9.00 s, 0.047 s, 9.05 s. The sheets are `C:/Temp/av-kit/s63/s63-probe-sheet-fit_lanczos.png` and `…_bicubic.png`.
- `C:/Temp/av-kit/s63-d504-prekey-run.txt` (`C:/Temp/av-kit/s63/probe_prekey.py`): 25 grabs just before each keyframe, 8.78 s, slowest 0.45 s, 0 failures.
- `C:/Temp/av-kit/s63-size-probe-receipt.txt` (`C:/Temp/av-kit/s63/probe_sheet_size.py`): `SHEET_SIZE` over 480 cases, 0 failures, each maximal; label sizes fitted with the real font.
- `C:/Temp/av-kit/s63-plan-identity-selftest.txt`, `s63-plan-redcheck-selftest.txt`: the scripts' selftests.
- `C:/Temp/av-kit/s63-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- `C:/Temp/av-kit/s63-plan-decision-probe.txt` (`C:/Temp/av-kit/s63/decision_probe.py`, which calls the validator's own `decision_sources`): the decision probe, with this plan and the grouping as sources.
- Not run at plan time: any suite or build.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python and MCP suites, the OpenAPI check, the MCP build and the two render checks, in the session gate.
- **Runtime:** the real-FFmpeg module on generated clips.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the runtime and the FFmpeg pair. The gate records it before and after, and H1-6b checks each handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
