---
date: "2026-11-11"
project: "capture-video-sheet"
meu: "MEU-135"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-11-capture-video-sheet/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-10-video-probe-frames-MEU-134-handoff.md"
---

# Handoff: 2026-11-11-capture-video-sheet-MEU-135-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-135 `capture-video-sheet`. A caller writes one labelled grid PNG of a span of a local video into the capture inbox, as a new shot with source `Video`, and gets each cell's time back. The sheet is for finding a moment; `frames` (MEU-134) then takes the exact stills.
- **REST.** `POST /api/v1/captures/sheet` takes `{path, start?, end?, grid?, max_edge?}` and answers 201 with `{video, shot, spacing_ms, cells}`. `video` reuses frames' five keys. `shot` holds `id`, `path`, `width` and `height`. Each `cells` item holds `cell`, `time_ms` and `timecode`. No image bytes are returned.
- **MCP.** `avkit_capture` `sheet` sends the same body, minus `action`, on `ADD_TIMEOUT_MS` (120 s) under D-601 A.
- **Rulings.**
  - D-601 A: the grid cap stays 5 (25 cells); `SHEET_DEADLINE_S` 100, `SHEET_RETURN_S` 105, `COMMIT_WAIT_S` 6; `sheet` joins `ADD_TIMEOUT_MS`.
  - D-602 A: Mat looks at three rendered sheets after row 3.

**Build Plan Section**: [09 §Video sheet](../../../docs/build-plan/09-screenshot-capture.md) (the Delivered note at `:1172`).
**Predecessor**: [MEU-134 handoff](2026-11-10-video-probe-frames-MEU-134-handoff.md), Session 62. It owns `TIME_PARSE`, `FRAME_TIMES`, `FRAME_GRAB`, `END_GAP`, `FRAME_WRITE` and the return gate that `sheet` reuses. The grouping is `.agent/context/grouping/2026-11-09-video-stills-session-grouping.md` (Sessions 62 to 64, D-500 to D-505).

- **Core module (row 3; D-596, D-597, D-598, D-606).** `packages/core/src/avkit_core/services/video_input.py` adds:
  - `SHEET_GRID_MIN`, `SHEET_GRID_MAX` and `SHEET_GRID_DEFAULT` (`:45-47`), `SHEET_TOKENS_STANDARD` and `SHEET_TOKENS_HIGH` (`:50-51`), `PIXELS_PER_TOKEN` (`:52`), `SHEET_FALLBACK_SIZE` (`:53`), `SHEET_LABEL_PERCENT` (`:55`) and `SHEET_LABEL_MIN_PX` (`:56`);
  - `SheetCell` (`:97`), `SheetShot` (`:106`) and `VideoSheet` (`:116`);
  - `sheet_cell_size` (`:277`), for `SHEET_SIZE`;
  - `sheet_spacing_ms` (`:298`), for `SHEET_TIMES`;
  - `sheet_label` (`:303`), `sheet_label_px` (`:309`) and `sheet_label_stroke` (`:314`), for `SHEET_LABEL`;
  - `sheet_name` (`:325`), for `SHEET_NAME`.
- **Ports (row 1; D-594, D-595).** In `packages/core/src/avkit_core/ports/capture.py`, `ImageAnnotatePort.sheet` (`:61`) and `FramePort.grab_frame`'s keyword-only `box` (`:87`, `:94`).
- **Service (row 3; D-599, D-600, D-601).** In `packages/core/src/avkit_core/services/capture.py`:
  - `SHEET_DEADLINE_S = 100` (`:152`), `SHEET_RETURN_S = 105` (`:153`), the worker name `avkit-sheet` (`:154`), and the messages `SHEET_NOT_WRITTEN` (`:156`), `SHEET_NO_DURATION` (`:157`), `SHEET_GRID_RANGE` (`:158`) and `SHEET_EDGE_RANGE` (`:160`, the view's own `max_edge` words);
  - `sheet_from_video` (`:691`) and `_run_gated` (`:713`), the worker and return-gate loop moved out of `frames_from_video` (`:667`), which now calls it too (D-600);
  - `_sheet_body` (`:774`), which runs `SHEET_CHECKS`; `_write_sheet` (`:858`) and `_grab_sheet` (`:907`), which run `SHEET_WRITE` through frames' `_reserve_frames` (`:1101`) and `_publish_frames` (`:1166`), now parametrized on names, failure times and source;
  - one `capture.sheet` log line with the cell count and the shot id (`:845`).
- **Adapters (row 3; D-594, D-595, D-597).**
  - `FFmpegAdapter.grab_frame` (`packages/infrastructure/src/avkit_infra/media/adapter.py:545`) takes `box` (`:552`) and its `END_GAP` retry keeps it (`:571`); `_grab_once` (`:574`) adds the `-vf scale=…` filter at `:593-595` (`CELL_GRAB`).
  - `CaptureAdapter.sheet` (`packages/infrastructure/src/avkit_infra/capture/adapter.py:504`) and `_draw_sheet_label` (`:164`) (`SHEET_TILE`).
- **API (row 3).**
  - `CaptureSheetIn` (`packages/api/src/avkit_api/schemas/captures.py:322`), `CaptureSheetShotOut`, `CaptureSheetCellOut` and `CaptureSheetOut` (`:355`).
  - The route is at `packages/api/src/avkit_api/routes/captures.py:353`, declared after `/frames` and before `/{id}`.
  - `wiring.py` doesn't change: `CaptureService` already gets `annotate` and `frames`.
  - `openapi.committed.json` is regenerated.
- **MCP (row 3; D-601 A, D-603, D-605, D-607).**
  - `mcp-server/src/toolsets/capture.ts`: `SHEET_TEXT` (`:71`), its map entry and the strict `sheet` member (`:310`), after `frames`; `FRAMES_TEXT`'s workflow line now reads probe → sheet → frames → image (D-605).
  - `mcp-server/src/toolsets/registry.ts`: the `ACTION_INDEX` row (`:136`) after `frames`, and `sheet` in `ADD_TIMEOUT_MS` (`:394`).
  - `mcp-server/scripts/audit/plan.ts`: the offline `capture.sheet` step with `grid: 2` on the probe clip, after `capture.frames` (`:1670`).
- **Tests.**
  - `tests/unit/test_domain_capture.py:939`: AC-135.1.
  - `tests/unit/test_video_input.py`: AC-135.2 to .5.
  - `tests/unit/test_capture_sheet_adapter.py` (new, LF): AC-135.6 and .7.
  - `tests/unit/test_media_adapter_frames.py`: AC-135.8.
  - `tests/unit/test_capture_sheet_service.py` (new, LF): AC-135.9 to .13.
  - `tests/integration/test_video_real_ffmpeg.py`: AC-135.14.
  - `tests/e2e/test_api_capture_sheet.py` (new, LF): AC-135.15 to .17.
  - `mcp-server/tests/capture.test.ts` and `audit/coverage.test.ts`: AC-135.18 and .19.
  - `tests/e2e/test_api_openapi.py:239`: AC-135.20.
  - The pins in §Pins that move (rows 1, 2a and 2b), and one order pin moved in row 3 (below, under S9).
- **Spec text and records (row 6).** 09's Delivered note (`docs/build-plan/09-screenshot-capture.md:1172`), MEU-135 `ready_for_review` with this plan (`.agent/context/meu-registry.md:197`), and grouping row 63 `executed`.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-11. The Codex plan review approved at round 1 ([plan-critical-review.md](2026-11-11-capture-video-sheet-plan-critical-review.md)). Mat then said "plan accepted with all recommendations, proceed". That accepts the plan, rules D-601 A and D-602 A, and sets the execution budget at about 28M tokens over three rounds (`implementation-plan.md:108`; the decision log quotes it at `:524` and `:539`). A commit or a push waits on Mat's own words, and the review's approval is Codex's.

**D-602 A, the look.** After row 3, `look.py` wrote three sheets into a scratch folder outside the repository (receipt `s63-r3-look.txt`):
- `white-grid3.png`: a 1280×720 white clip, grid 3, 482×271 cells, labels `1 00:00:00.556` to `9 00:00:09.444`;
- `black-grid3.png`: the same on a black clip;
- `tall-grid5.png`: a 1080×1920 clip, grid 5, 162×288 cells, labels `1 00:00:00.600` to `25 00:00:29.400`.

Mat looked at all three on 2026-11-11 and said "Yes they look right".

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The video path** goes from the request to `VIDEO_INPUT`, then to FFmpeg's and ffprobe's argv and to the 201 body's `video.path`. It is never logged and never put in an error message. Its only writer is the caller (AC-135.16).
- **The video's stem** goes through `import_stem` into the sheet name, which reaches the inbox, the row, the 201 body's `shot.path` and the Capture page. `import_stem` keeps word characters, space and `-`, so a control character or a lone surrogate never reaches a name. A reserved stem becomes `import_CON`, and an empty one becomes `import` (AC-135.5).
- **The cell times** come from `FRAME_TIMES`. One list feeds `cells`, the labels drawn on the image and, as `TIMECODE`, the error messages, so `cells` and the labels can't disagree (AC-135.10).
- **`grid` and `max_edge`** reach the cell size and the shot's size. A refused value gets a fixed message that echoes nothing (AC-135.9, AC-135.15).
- **FFmpeg's and ffprobe's stderr**, which name the path, are dropped by `FRAME_GRAB`, as for frames.
- **The sheet's pixels** come from FFmpeg's cell bytes and the label text only. The PNG is encoded in memory with no metadata, so no path, `text` chunk or EXIF reaches the file (AC-135.6).
- **The sheet path** goes to the 201 body and the row. `capture.sheet` logs the cell count and shot id only, and `_upsert_shot`'s existing `capture.registered` line logs the shot id and source name (`NO_RAW_OUTPUT`).
- **The marker check.** AC-135.16 puts the video under a marker folder and the marker in the fake's FFmpeg stderr. It drives every error on the real stack with `HealthService` built first (Session 54 RULE-2). The marker is absent from every body, the log ring, stdout and stderr, and a positive control finds it.
- **No network.** Every video was made locally with the pinned FFmpeg. A URL is refused before any probe.

### Deadline inventory, as built (Session 62 RULE-1)

| # | Blocking call | Where | Bound as built |
|---|---|---|---|
| 1 | `require_local_video` (`resolve`, `is_file`) | worker, `_sheet_body` `:785` | local filesystem; the return gate (e) |
| 2 | `FramePort.probe` (ffprobe) | worker, `:807` | `timeout_s=deadline - self._monotonic()` |
| 3 | `CAPTURE_FILE_LOCK` wait, phase 1 | worker, `_reserve_frames` | `acquire(timeout=left)`; a lock not had in time fails with the first cell's time (a) |
| 4 | Connection checkout, phase 1 | worker | (e) |
| 5 | Each cell grab, and inside it each FFmpeg and ffprobe run (`END_GAP`) | worker, `_grab_sheet` | `timeout_s=left`, checked before (a) and after (b) each grab |
| 6 | Tiling: decode, paste, labels and PNG encode | worker, `_grab_sheet` | (b') after it; (e). Measured 0.063 s for 25 cells |
| 7 | Temp write and `annotate.probe` | worker, `_grab_sheet` | (c) at publish; (e) |
| 8 | `CAPTURE_FILE_LOCK` wait, phase 3 | worker, `_publish_frames` | `acquire(timeout=left)`; (c) |
| 9 | Connection checkout, phase 3 | worker | (e) |
| 10 | Commit (SQLite `busy_timeout` 5,000 ms) | worker, `_publish_frames` | (d) before it; `COMMIT_WAIT_S` 6 |
| 11 | The caller's `join` steps | caller, `_run_gated` `:749` | `FRAMES_JOIN_STEP_S` 0.05 s each, up to `SHEET_RETURN_S + COMMIT_WAIT_S` |

Under D-601 A the call answers within 111 s and one join step, against the client's 120 s. An abandoned worker starts no new FFmpeg run, because (a) fails once the deadline has passed. AC-135.13 drives (a), (b), (b'), (c), (d), both lock waits and (e).

### Documented limits

- **A video with no duration is refused.** `sheet` needs a span, so a raw stream gives `sheet needs a duration; this video has none` before any grab. The MCP description says so, and frames' description already says to remux such a file with `avkit_convert add`.
- **A span shorter than its cells has fewer cells.** `FRAME_TIMES` collapses duplicate times, so a span of at most `grid²` ms gives `k ≤ min(grid², span)` cells, numbered 1 to `k`, and the rest stay black (D-598, AC-135.3).
- **Cells are the first frame at or after their time,** and a time between the last frame and the end shows the last frame (`END_GAP`). Events between cells can be missed. The MCP description says both.
- **An abandoned body.** When the return gate gives up at 105 s, the worker ends when its current wait ends. That wait is a grab within its own timeout, the tile, or a pool checkout. Then it removes what it made. Only a commit still running at 111 s answers the masked 503 without knowing whether the sheet was kept.
- **`CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` and `CAPTURE-EXIF-SCANNED-ORIENTATION`** were not observed in this session's runs. They are left to their own sessions (D-604).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-135.1 | unit | Type characterisation of row 1: `ImageAnnotatePort.sheet` has keyword-only `grid`, `cell_size` and `labels`; `FramePort.grab_frame` ends with keyword-only `box` defaulting to `None`; `FFmpegAdapter.grab_frame`'s and `CaptureAdapter.sheet`'s signatures equal the protocols'. It passed from row 1 and ran as a guard in row 2a | 09 Cells | `tests/unit/test_domain_capture.py:939` | ✅ |
| AC-135.2 | unit | `SHEET_SIZE`: the exact cells for 16:9, 4:3 and 9:16 at grids 2 to 5 and `max_edge` 64, 1568 and 2576; for every shape, grid and edge of the probe, the long edge within `max_edge`, the area within the budget, both cell edges at least 1, and one more pixel breaking a bound; 1568 uses 1568 tokens and 1569 uses 4784; `None` and 0 sizes use 16:9 | 09 Size; D-596 | `tests/unit/test_video_input.py:488`, `:496`, `:524`, `:545` | ✅ |
| AC-135.3 | unit | `SHEET_TIMES`: `sheet_spacing_ms`'s half cases each way; an exhaustive loop over grids 2 to 5 and spans 1 to 60 from starts 0 and 1000 keeps every time in `[start, end)`, sorted and distinct, with `k == grid²` above `grid²`, `grid² − 1` at it, and `k ≤ min(grid², span)` always | 09 Cells; D-598 | `test_video_input.py:558`, `:565` | ✅ |
| AC-135.4 | unit | `SHEET_LABEL`: the 9,999 / 10,000 ms boundary; the label keeps the timecode's prefix; `sheet_label_px` and `sheet_label_stroke` half cases each way and the 8 px floor | 09 Labels; D-597 | `test_video_input.py:600`, `:616`, `:632` | ✅ |
| AC-135.5 | unit | `SHEET_NAME`: `standup-sheet-00h00m00s-02h00m00s`; floored seconds; the 359,999,999 bound; `Łodz` kept; `CON` → `import_CON`; `..` → `import`; a lone surrogate, `\x07` and an empty stem each give a clean, non-empty stem | 09 Writes; D-606 | `test_video_input.py:651`, `:662` | ✅ |
| AC-135.6 | unit | `SHEET_TILE` with the real `CaptureAdapter`: cell positions, centring with black bars, shrinking, a missing cell left black, a long label clipped to its cell, an 80×60 PNG with no `text` or `exif`, an undecodable cell raising, and mismatched lengths raising `ValueError` | 09 Cells, Labels; D-594 | `tests/unit/test_capture_sheet_adapter.py:106` (through `:199`) | ✅ |
| AC-135.7 | unit | Label contrast on all-white and all-black 482×271 cells: at least 2 % near white and 2 % near black in each label box, 0 % in the no-label control; the drawn labels are exactly those passed, white fill, black stroke at least 1 px | 09 Tests; D-597 | `test_capture_sheet_adapter.py:219`, `:239` | ✅ |
| AC-135.8 | unit | `CELL_GRAB` with a recording fake `subprocess.run`: the `-vf scale=288:162:force_original_aspect_ratio=decrease:flags=lanczos` pair directly after `-frames:v 1`; `END_GAP`'s retry carries the same `-vf`; `box=None` and no `box` give the AC-134.9 argv | 09 Cells; D-595 | `tests/unit/test_media_adapter_frames.py:453`, `:478`, `:499`, `:521` | ✅ |
| AC-135.9 | unit | `SHEET_CHECKS`: each refusal runs no grab, leaves the inbox empty and adds no row; those before the probe record zero probes; the magnitude bounds (`1e308`, `-1e308`, `"100:00:00"`, 360000, `10**18`); `end` equal to the duration accepted; membership and type checked first, `__context__` `None` | 09 Request, Errors; D-599 | `tests/unit/test_capture_sheet_service.py:498` (through `:575`) | ✅ |
| AC-135.10 | unit | `SHEET_WRITE` trace: one `grab_frame` per cell in time order with `seek="input"`, the cell `box` and the time left; the fake `sheet` gets the cells in order and labels from `result.cells`; the shot is `Video` with the probed size | 09 Cells, Writes, Labels | `test_capture_sheet_service.py:588`, `:643`, `:662` | ✅ |
| AC-135.11 | unit | All or nothing: an empty fifth cell and a non-PNG cell give `frame grab failed at` that time; a raising `sheet`, an output-probe `InboxPathError` and an `os.replace` `OSError` give the masked error; each leaves no `.png`, no `.avkit-tmp`, no new row and a pre-existing shot unchanged | 09 Writes; D-600 | `test_capture_sheet_service.py:674` (through `:741`) | ✅ |
| AC-135.12 | unit | Never overwrite: two calls behind a `Barrier` get `clip-sheet-00h00m00s-00h00m03s.png` and `_2`, each with its own bytes; an inbox file, a row and another writer's temp each give `_2`; the other writer's temp is left byte for byte; temps are opened `"xb"` | 09 Writes | `test_capture_sheet_service.py:764` (through `:837`) | ✅ |
| AC-135.13 | unit | `SHEET_DEADLINE` with an injected clock: (a), (b), (b'), (c) with either lock held, (d); every `acquire` passes a timeout; (e) a stuck tile answers within 2 s of real time, the worker is `avkit-sheet` and is joined after, a slow commit returns, a stuck one is masked; frames' worker is still `avkit-frames`; the ruled values 100, 105 and 6 | D-600; D-601 | `test_capture_sheet_service.py:862` (through `:1110`) | ✅ |
| AC-135.14 | integration | Real FFmpeg: a grid 2 sheet of the counter clip has cells at 375, 1125, 1875 and 2625 ms, each equal by pixel to a full-decode reference through the same filter; 1250×938 within the budget; white and black clips pass AC-135.7's check; the raw `.h264` gives the no-duration message with zero grabs; every source's SHA-256 unchanged | 09 Cells, Tests | `tests/integration/test_video_real_ffmpeg.py:447`, `:478`, `:499`, `:521`, `:534` | ✅ |
| AC-135.15 | API | `POST /captures/sheet` on the real stack: 201 with exactly `{video, shot, spacing_ms, cells}` and their keys, 9 cells by default, the file in the inbox root; each schema refusal is the fixed 422, including `grid` and `max_edge` of `10**18` and `start` 1e308 | 09 Request, Response; D-607 | `tests/e2e/test_api_capture_sheet.py:191` (through `:298`) | ✅ |
| AC-135.16 | API | Errors on the real stack: not found (missing file and self-loop symlink, no probe and no grab), the URL, past the end, no duration, `frame grab failed at`, the masked 503 for `FFmpegNotFoundError` and for a write failure; the marker absent everywhere, with a positive control | 09 Errors; S54 RULE-2 | `test_api_capture_sheet.py:316` | ✅ |
| AC-135.17 | API | `GET /captures`, `GET /captures/{id}` and `/image` show the sheet with source `"Video"`, its size and bytes; a later scan keeps `"Video"` | 09 Writes | `test_api_capture_sheet.py:406` | ✅ |
| AC-135.18 | MCP | `SHEET_MCP`: every key accepted and each refusal before fetch; the body minus `action` on `ADD_TIMEOUT_MS` (D-601 A); its own four markers and the zoom advice; `FRAMES_TEXT`'s workflow names `sheet` between `probe` and `frames` (D-605) | 09 Request, Description; D-605 | `mcp-server/tests/capture.test.ts:1126`, `:1141`, `:1181`, `:1216`, `:1240` | ✅ |
| AC-135.19 | MCP | `ACTION_INDEX` has 74 rows with `sheet` after `frames` and `frames` after `crop`; transport parity of the 201 body; `BASELINE_PENDING` ends with `avkit_capture.sheet`; `AUDIT_PLAN` has the offline step after `capture.frames`; coverage fails when it is missing | 09 Tests; D-603 | `capture.test.ts:1251`, `:1270`; `mcp-server/tests/audit/coverage.test.ts:233`, `:289`, `:296` | ✅ |
| AC-135.20 | API | OpenAPI: the sheet route with `CaptureSheetIn` and `CaptureSheetOut` in the committed snapshot; 77 operations; `--check` passes; `/sheet` before `/{id}` | 09 Tests | `tests/e2e/test_api_openapi.py:239`; H1-4 | ✅ |
| AC-134 (cross-ref) | regression | MEU-134's ACs are owned by the MEU-134 handoff. Moved pins: AC-134.1's `grab_frame` parameter list gains `"box"` last (`test_domain_capture.py:921`); AC-134.15's `FRAMES_TEXT_MARKERS[0]` takes the new workflow line (D-605); AC-134.16's count 73 → 74; AC-134.17's operation count 76 → 77. AC-134.9's argv lists and every frames test ran unchanged as guards after the D-600 refactor | plan §Pins that move; D-600; D-605 | [MEU-134 handoff](2026-11-10-video-probe-frames-MEU-134-handoff.md); gate `py-tests`, `mcp-tests` | ✅ |
| AC-8 (cross-ref) | regression | AC-8.12 (`tests/integration/test_filesystem_media.py:466-467`) pins `FFmpegAdapter`'s `MediaPort` signatures to the protocol's; `grab_frame` isn't a `MediaPort` method, and the pin passes unchanged | plan Guards | gate `py-tests` | ✅ |
| AC-130 (cross-ref) | regression | AC-130.26 (crop after revert) and AC-130.28 (the baseline misses only the pending keys) failed in row 2b on the 74 count and the pending list, and pass after row 3 with `avkit_capture.sheet` in `BASELINE_PENDING` | plan §Pins that move; D-603 | `capture.test.ts`, `coverage.test.ts`; gate `mcp-tests` | ✅ |
| AC-38, AC-32 (cross-ref) | regression | AC-38.1, AC-38.2, AC-38.5 and AC-32.1 read `ACTION_INDEX_AFTER`, `CAPTURE_ACTIONS` and the shared markers; they failed in row 2b on the moved counts and pass after row 3, `sheet` carrying the four marker words from `SHEET_TEXT` | plan §Pins that move | `capture.test.ts`, `convert.test.ts`; gate `mcp-tests` | ✅ |
| AC-68 (cross-ref) | regression | AC-68.5's `AUDIT_ACTION_SET` and AC-68.1/AC-68.4's built-server discovery count 74 actions; MEU-134's order pin at `runner-fake-backend.test.ts:191` moved in row 3 under S9 (§Evidence) | plan §Pins that move; S9 | `coverage.test.ts`, `runner-fake-backend.test.ts:79`, `:190-193`; gate `mcp-tests` | ✅ |
| AC-16, AC-42 (cross-ref) | regression | AC-16.6 walks the 77 `ROUTE_INDEX` rows (the sheet row after frames), AC-16.9 sends `_valid_body`'s sheet body with an extra key, and AC-42.9 counts 77 operations and 74 actions | plan §Pins that move | `test_api_openapi.py`, `test_api_bodies.py:48`, `test_api_downloads.py:372-377`; gate `py-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-135.2 to AC-135.17, AC-135.20 (Python) | Row 2a: 196 failed, 290 passed against row 1's stubs. `DID NOT RAISE ValidationError` ×41; `assert (1, 1) == (N, N)` ×32; `{"detail":"Method Not Allowed"}` ×26; `assert N == N` ×27; `assert False` ×14; `assert None is not None` ×11; `DID NOT RAISE CaptureFailedError` ×5 | Row 3: 859 passed; gate `py-tests` 1999 passed | `test_video_input.py:488-662`, `test_capture_sheet_adapter.py:106-239`, `test_media_adapter_frames.py:453-521`, `test_capture_sheet_service.py:498-1110`, `test_video_real_ffmpeg.py:447-534`, `test_api_capture_sheet.py:191-406`, `test_api_openapi.py:239` |
| AC-135.1 | A characterisation of row 1: row 2a's guard passed 1 | Gate `py-tests` | `test_domain_capture.py:939` |
| AC-135.18, AC-135.19 (MCP) | Row 2b: Test Files 6 failed (6); Tests 23 failed, 137 passed (160). `expected [ …(73) ] to have a length of 74 but got 73` ×6; `expected [] to have a length of 1 but got +0` ×2; `expected [ …(12) ] to have a length of 13`; `expected 73 to be 74` | Row 3: 35 files, 508 passed; gate `mcp-tests` 508 passed | `capture.test.ts:1126-1270`, `coverage.test.ts:233-296` |

- **red-check.** Row 2a's receipt: 1 receipt, 17 required tests, 0 problems. Row 2b's: 1 receipt, 2 required tests, 0 problems. Every failing block is an assertion.
- **The passes in the Red runs.** Row 2a's 290 passes are MEU-133's and MEU-134's tests in the same files, the moved pins' neighbours, and the cases row 1's stubs already met. Row 2b's 137 passes are the MCP tests that don't read `sheet` or the counts. These AC-135 cases passed in Red as guards, and the handoff names them so none reads as a Red claim:
  - AC-135.3's spacing case with a span of 1, rounded down to 0, which the stub's `0` already met;
  - AC-135.8's no-box cases, which check that the argv is unchanged;
  - AC-135.13's "frames keeps its worker" case and its ruled-values case (the constants were declared in row 1);
  - one AC-135.18 refusal case, since the strict union already refused an unknown action.
- **Pre-existing families in the Red runs.** AC-38.1, .2, .5, AC-32.1, AC-130.26, .28, AC-68.1/.4, .5, AC-16.6, AC-16.9, AC-42.9 and AC-134.15 to .17 failed on the moved counts, lists and the D-605 line, as §Pins that move predicted; each has a cross-ref row.
- **S9, row 3's first MCP run.** MEU-134's order pin (`runner-fake-backend.test.ts:191`, D-591) asserted `capture.capture_interactive` directly after `capture.frames`. AC-135.19 puts `capture.sheet` there, so the pin failed once the audit step existed. It wasn't in §Pins that move: the plan's sweep listed count pins and the AC-134.16 row-position pin, not this adjacency, and row 2b couldn't trip it, because the step didn't exist until row 3. S9's action was taken: the pin moved with its AC, its neighbours were grepped, and it is named here. The adjacency it guarded is kept in two lines: `capture.frames` directly after `capture.crop`, and `capture.capture_interactive` directly after `capture.sheet`, each with a comment. This is a test edit in a Green row, disclosed for review (Session 59 RULE-1, Session 62 RULE-4).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s63-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-11-capture-video-sheet/baseline.ps1 *> C:/Temp/av-kit/s63-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit; base suites in C:/Temp/av-kit/s63-base-py.txt, s63-base-mcp.txt, s63-base-ruff.txt and s63-base-mcp-build.txt)", "scope": "Row 0: rulings D-601 and D-602 present (S14), anchors, baseline.sha and baseline-dirty.txt, line endings, the pinned FFmpeg and Pillow, base suites and the identity selftest", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7403f18 before any row", "output": "Base suites: pytest 1800 passed in 151.13s; MCP 35 files, 498 passed; ruff All checks passed!; MCP build exit 0. identity selftest: 0 failure(s). baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s63-1-types", "command": "rtk proxy uv run pytest (test_domain.py, test_domain_capture.py, test_capture_frames_service.py, test_media_adapter_frames.py, test_filesystem_media.py and the capture guards) *> C:/Temp/av-kit/s63-types-py.txt; rtk proxy uv run pyright *> C:/Temp/av-kit/s63-types-pyright.txt; rtk proxy uv run ruff check *> C:/Temp/av-kit/s63-types-ruff.txt; the caller grep *> C:/Temp/av-kit/s63/row1-callers.txt; the implementer grep *> C:/Temp/av-kit/s63-h1-implementers.txt (task.md row 1's Validation cell)", "scope": "Row 1: the shared names as wrong stubs (video_input.py's sheet names, ImageAnnotatePort.sheet, FramePort.grab_frame's box, CaptureAdapter.sheet, FFmpegAdapter.grab_frame's box), the grab_frame pin, AC-135.1, and the caller, implementer and pin grep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7403f18 plus rows 0 to 1", "output": "312 passed in 10.83s; pyright 0 errors; ruff All checks passed!; caller grep 65 lines (frames_from_video, _reserve_frames, _publish_frames and grab_frame callers and fakes); implementer grep: ImageAnnotatePort and FramePort are implemented by CaptureAdapter and FFmpegAdapter and used only by CaptureService and duck-typed test fakes; the signature-equality tests are test_domain_capture.py:917-975 and test_filesystem_media.py:466-467"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s63-2a-red-135-py", "command": "$env:TMP='C:\\Temp\\av-kit\\s63\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_video_input.py tests/unit/test_media_adapter_frames.py tests/unit/test_capture_sheet_adapter.py tests/unit/test_capture_sheet_service.py tests/e2e/test_api_capture_sheet.py tests/integration/test_video_real_ffmpeg.py tests/e2e/test_api_openapi.py tests/e2e/test_api_downloads.py tests/e2e/test_api_bodies.py --tb=short -q *> C:/Temp/av-kit/s63-py-red-135.txt; red-check.py with the 17 --require ids *> C:/Temp/av-kit/s63-py-red-135-check.txt; pytest tests/unit/test_domain_capture.py -k test_ac_135_1_ *> C:/Temp/av-kit/s63-r2a-guard.txt (task.md row 2a's Validation cell)", "scope": "MEU-135 Python Red: AC-135.2 to AC-135.17 and AC-135.20 against row 1's stubs, plus AC-135.1 as a passing guard and the moved Python pins", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7403f18 plus rows 0 to 2a", "output": "196 failed, 290 passed in 33.14s. Decisive: DID NOT RAISE ValidationError x41; assert (1, 1) == (N, N) x32; {\"detail\":\"Method Not Allowed\"} x26; assert N == N x27; assert False x14; assert None is not None x11; DID NOT RAISE CaptureFailedError x5. red-check: 1 receipt(s), 17 required test(s), 0 problem(s). AC-135.1 guard: 1 passed, 109 deselected"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s63-2b-red-135-mcp", "command": "rtk proxy npm --prefix mcp-server run build *> C:/Temp/av-kit/s63-r2b-mcp-build.txt; rtk proxy npm --prefix mcp-server run test -- tests/capture.test.ts tests/convert.test.ts tests/action-index.test.ts tests/m7-resource.test.ts tests/audit/coverage.test.ts tests/audit/runner-fake-backend.test.ts *> C:/Temp/av-kit/s63-mcp-red-135.txt; red-check.py --require AC-135.18 --require AC-135.19 *> C:/Temp/av-kit/s63-mcp-red-135-check.txt (task.md row 2b's Validation cell)", "scope": "MEU-135 MCP Red: AC-135.18, AC-135.19 and the moved MCP pins, on a fresh build", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7403f18 plus rows 0 to 2b", "output": "Test Files 6 failed (6); Tests 23 failed | 137 passed (160). Decisive: expected [ ...(73) ] to have a length of 74 but got 73 x6; expected [] to have a length of 1 but got +0 x2; expected [ ...(12) ] to have a length of 13; expected 73 to be 74. red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s63-3-green-135", "command": "$env:TMP='C:\\Temp\\av-kit\\s63\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest (row 3's 19 files: the MEU-135 tests, the frames tests, every CaptureService caller and capture guard, test_domain, test_domain_capture, test_filesystem_media and test_api_wiring) --tb=short -q -rfE *> C:/Temp/av-kit/s63-py-green-135.txt; real FFmpeg *> C:/Temp/av-kit/s63-r3-real-ffmpeg.txt; export_openapi.py --check *> C:/Temp/av-kit/s63-r3-openapi.txt; git diff -- openapi.committed.json *> C:/Temp/av-kit/s63-r3-openapi-diff.txt; pyright, ruff, MCP build, MCP test and typecheck *> C:/Temp/av-kit/s63-r3-*.txt; look.py *> C:/Temp/av-kit/s63-r3-look.txt (task.md row 3's Validation cell)", "scope": "MEU-135 Green: SHEET_SIZE, SHEET_TIMES, SHEET_LABEL, CELL_GRAB, SHEET_TILE, SHEET_NAME, SHEET_CHECKS, SHEET_WRITE, SHEET_DEADLINE with _run_gated, SHEET_ROUTE, SHEET_MCP, the FRAMES_TEXT line, NO_RAW_OUTPUT, the sheet audit step, and the D-602 look sheets", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7403f18 plus rows 0 to 3", "output": "859 passed, 16 warnings in 55.95s; real FFmpeg 21 passed in 6.69s; openapi --check exit 0; the OpenAPI delta adds only /api/v1/captures/sheet and CaptureSheetCellOut, CaptureSheetIn, CaptureSheetOut, CaptureSheetShotOut, nothing changed or removed, CRLF kept (7549 CRLF, 7549 LF); pyright 0 errors; ruff All checks passed!; MCP build exit 0; MCP Test Files 35 passed (35), Tests 508 passed (508); typecheck exit 0. look: white-grid3 and black-grid3 482x271 cells, 9 labels; tall-grid5 162x288 cells, 25 labels; three sheets written"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s63-6-records", "command": "task.md row 6 (abridged), run from P:/av-kit: the S3 check, the pre-status copies, the 09 Delivered note, MEU-135's fields byte-edited in meu-status.yaml (S15), the render; grouping row 63; then its Validation cell into C:/Temp/av-kit/s63-r6-render.txt and its status check into C:/Temp/av-kit/s63-r6-status.txt", "scope": "Row 6: the D3 spec text, MEU-135 ready_for_review with this plan, the render, and grouping row 63 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7403f18 plus rows 0 to 6", "output": "Drift check passed - SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content. ready_for_review; grouping row 63 executed; spec note: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s63-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-11-capture-video-sheet/session-gate.ps1 *> C:/Temp/av-kit/s63-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', '_sha256 ', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit; per-step receipts C:/Temp/av-kit/s63-D6-*.txt)", "scope": "H1-2: the registered D6 gate on the whole tree", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652", "output": "baseline failures excused: py [], mcp []; ui-types, ui-lint, ui-tests, ui-build, ui-electron, mcp-audit, build-record and package-build skipped with reasons; identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); task-contract exit=0 (23 rows, 21 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 43, outside scope: [], head moved (S3): False, baseline-dirty paths changed since row 0: []); red-check-selftest exit=0 (43 fixtures, 13 positive, 30 negative, 0 wrong); py-tests exit=0 (1999 passed in 163.26s); openapi exit=0; mcp-types exit=0; mcp-build exit=0; mcp-tests exit=0 (35 files, 508 passed); state-render exit=0 (142 MEUs, 12 phases); issues-render exit=0 (known-issues.md is up-to-date); status-canon exit=0 (2 files, 14 passed); real-ffmpeg exit=0 (21 passed in 6.82s); identity-after exit=0 (tested_state before = after); session-gate: all steps exit 0"}
```

### Quality Gate Results

`s63-gate-h1-2` (H1-2) is the fresh full record. Its last line is:

> session-gate: all steps exit 0

- **One run.** The gate passed every step on its first run.
- **Static checks.**
  - pyright: 0 errors, 0 warnings, 0 informations. ruff check: all checks passed.
  - lint_task_contract passed on 23 rows (21 fully checked; H1-5 and H2-1 are exempt as `view_file`).
  - scope-paths found 43 changed paths, none outside scope. HEAD `7403f18` did not move, and none of the paths in `baseline-dirty.txt` changed since row 0 (S3). Before the gate, the tree's changed paths were listed against the gate's scope paths (Session 60 RULE-4).
  - The red-check selftest read 43 fixtures (13 positive, 30 negative), with 0 wrong.
- **Suites.**
  - pytest: 1999 passed (the baseline's 1800 plus 199 new cases).
  - MCP: 508 passed in 35 files (the baseline's 498 plus 10).
  - real-ffmpeg: 21 passed (`test_video_real_ffmpeg.py`, the only module the step runs).
  - status-canon: 14 passed.
- **Build and state.**
  - `export_openapi.py --check`, the MCP typecheck and the MCP build exited 0.
  - The state render and the issue render match the files on disk.
  - H1-3's `render --check` and H1-4's `export_openapi.py --check` passed after the gate.
- **Skipped.** Each skip has a reason in the gate:
  - the UI steps: no `ui/` file changed, and status-canon runs the only UI tests that read a file this session writes;
  - `mcp-audit`: it needs the live network, which the brief forbids, and AC-135.19 covers `AUDIT_PLAN`'s new step offline;
  - `build-record`: no installer build;
  - `package-build`: no packaged surface change.
- **Identity.**
  - The tested_state was the same before and after: `7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652`.
  - The closeout records are left out of the identity, so writing them doesn't change it.
- **Warnings.** Row 3 has 16 warnings, the gate's `py-tests` 32 and its `real-ffmpeg` 16. Every one is Pillow's `getdata` deprecation, raised by the test helper at `test_capture_sheet_adapter.py:89`, which AC-135.7 and AC-135.14 both call (16 each). None comes from product code.

### The row 3 OpenAPI diff

`export_openapi.py` regenerated `openapi.committed.json`, and CRLF was kept (7549 CRLF line ends, no bare LF). Against `7403f18`, the delta (`s63-r3-openapi-diff.txt`, 196 added lines and no removed line) adds:
- the path `/api/v1/captures/sheet`;
- the schemas `CaptureSheetCellOut`, `CaptureSheetIn`, `CaptureSheetOut` and `CaptureSheetShotOut`.

It changes no path or schema, and it removes nothing.

### The rulings' D-504 receipts

- **D-601 A, cap 5 and `SHEET_DEADLINE_S` 100** (`s63-d504-probe-receipt.txt`, `s63-d504-prekey-run.txt`).
  - On the 2 h 4K HEVC file (11,285,707,465 B), a 5×5 sheet took 10.30 s: 25 grabs in 10.23 s (0.409 s mean, 0.73 s slowest), 0 failures, every cell 288×162, and the tile and save 0.063 s.
  - 25 grabs just before a keyframe took 8.78 s, the slowest 0.45 s.
  - So 25 cells fit well inside 100 s, and 100 s plus the return gate fits inside the client's 120 s.
- **D-595, `CELL_GRAB`.** The same probe ran the exact `scale=…:flags=lanczos` filter. Bicubic took 9.05 s for the same sheet, so the choice is about quality, not time. AC-135.14 proves on real FFmpeg that each scaled grab equals a full decode through the same filter.
- **D-596, `SHEET_SIZE`** (`s63-size-probe-receipt.txt`). 480 cases (8 shapes, grids 2 to 5, 15 edges), 0 failures, each maximal.
- **D-602 A.** Mat's words on the three look sheets are quoted in §Scope.

### D-600, the refactor and its guards

`frames_from_video`'s worker and return-gate loop moved into `_run_gated` (`services/capture.py:713`), and `_reserve_frames` and `_publish_frames` now take names, failure times and the source as parameters. Frames' behaviour is unchanged: `test_capture_frames_service.py`, `test_api_capture_frames.py` and `test_media_adapter_frames.py`'s AC-134 cases ran in row 3's 859 and pass in the gate's 1999, including AC-134.8's return-gate cases and AC-135.13's check that a `frames` call still runs on `avkit-frames`.

### D-605, the frames workflow line

`FRAMES_TEXT`'s workflow line was `Workflow: call avkit_convert probe for the duration, then avkit_capture frames to POST /captures/frames, then image to view a frame.` It now reads `Workflow: call avkit_convert probe for the duration, then avkit_capture sheet to find the moment, then frames to POST /captures/frames for exact stills, then image to view a frame.` That is 09's Description order (probe → sheet → frames → image). It moved pin `FRAMES_TEXT_MARKERS[0]` (AC-134.15) in row 2b, and AC-135.18 checks the new line.

### Caller and pin grep (S55 RULE-1, S59 RULE-1, Session 61 RULE-3, Session 62 RULE-4)

- **`grab_frame`.** It is called by `_grab_frames` and `_grab_sheet` in `CaptureService`, and by `FFmpegAdapter.grab_frame`'s own `END_GAP` retry, which passes `box` on. The test fakes in `test_api_capture_frames.py:80`, `test_video_real_ffmpeg.py:183` and `test_capture_frames_service.py:99` take `**kwargs` or ignore `box`, and pass unchanged.
- **`_reserve_frames` and `_publish_frames`** are called by `_write_frames` and `_write_sheet` only.
- **The gate loop.** `_run_gated` is called by `frames_from_video` and `sheet_from_video` only.
- **Implementers.** `ImageAnnotatePort` and `FramePort` are used only by `CaptureService` and the duck-typed test fakes. The signature-equality tests are `test_domain_capture.py:917-975` (AC-134.1 and AC-135.1) and `test_filesystem_media.py:466-467` (AC-8.12).
- **Count and order pins.** The count neighbours were grepped again in rows 2a and 2b, and every hit is in §Pins that move. The one order pin the sweep missed is `runner-fake-backend.test.ts:191` (S9, above).
- **Absence pins.** At plan time a grep for `sheet` in `tests/`, `mcp-server/tests/` and `ui/tests/` found no hit, so no test asserts `sheet` is absent.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/video_input.py` | modified | `SHEET_SIZE`, `SHEET_TIMES`, `SHEET_LABEL`'s pure parts, `SHEET_NAME`; the sheet constants; `SheetCell`, `SheetShot`, `VideoSheet`. LF |
| `packages/core/src/avkit_core/ports/capture.py` | modified | `ImageAnnotatePort.sheet`; `FramePort.grab_frame`'s `box` |
| `packages/core/src/avkit_core/services/capture.py` | modified | `sheet_from_video`, `_run_gated`, `_sheet_body`, `_write_sheet`, `_grab_sheet`; `_reserve_frames` and `_publish_frames` parametrized (D-600) |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | modified | `CELL_GRAB` |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `SHEET_TILE` and the label drawing |
| `packages/api/src/avkit_api/routes/captures.py`, `schemas/captures.py` | modified | `SHEET_ROUTE` |
| `openapi.committed.json` | regenerated | The sheet route and its four schemas |
| `mcp-server/src/toolsets/capture.ts`, `registry.ts` | modified | `SHEET_MCP`, `SHEET_TEXT`, the `FRAMES_TEXT` line, the `ACTION_INDEX` row and `ADD_TIMEOUT_MS` |
| `mcp-server/scripts/audit/plan.ts` | modified | The offline `capture.sheet` step |
| `tests/unit/test_capture_sheet_service.py`, `test_capture_sheet_adapter.py` | new | AC-135.6, .7, .9 to .13. LF |
| `tests/e2e/test_api_capture_sheet.py` | new | AC-135.15 to .17. LF |
| `tests/unit/test_video_input.py`, `test_media_adapter_frames.py`, `tests/integration/test_video_real_ffmpeg.py` | modified | AC-135.2 to .5, .8, .14. LF |
| `tests/unit/test_domain_capture.py` | modified | AC-135.1; the `grab_frame` pin |
| `tests/e2e/test_api_openapi.py`, `test_api_downloads.py`, `test_api_bodies.py` | modified | AC-135.20; the counts 76 → 77 and 73 → 74; `ROUTE_INDEX`; the sheet valid body |
| `mcp-server/tests/capture.test.ts`, `convert.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `audit/coverage.test.ts`, `audit/runner-fake-backend.test.ts` | modified | AC-135.18, .19; the counts 73 → 74, capture 12 → 13; `CAPTURE_ACTIONS`; `FRAMES_TEXT_MARKERS[0]` (D-605); `BASELINE_PENDING`; the order pin (S9) |
| `docs/build-plan/09-screenshot-capture.md` | modified | The Delivered note (`:1172`) |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | Only MEU-135's fields and rows, and grouping row 63 (row 6) |

Line endings were measured with Python bytes before each edit and kept:
- These files stayed CRLF: `ports/capture.py`, `services/capture.py`, `media/adapter.py`, `capture/adapter.py`, `routes/captures.py`, `schemas/captures.py`, `openapi.committed.json`, `capture.ts`, `registry.ts`, `plan.ts`, the MCP test files, `test_domain_capture.py`, `test_api_openapi.py`, `test_api_downloads.py`, 09 and the grouping.
- `video_input.py`, `test_video_input.py`, `test_media_adapter_frames.py`, `test_video_real_ffmpeg.py`, `test_api_bodies.py`, `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md` stayed LF.
- New files are LF.

```diff
 # ports/capture.py
+    def sheet(
+        self, cells: Sequence[bytes], *, grid: int, cell_size: tuple[int, int], labels: Sequence[str]
+    ) -> bytes: ...
+        box: tuple[int, int] | None = None,
 # routes/captures.py
+@router.post("/sheet", status_code=201, response_model=CaptureSheetOut)
 # registry.ts
+  { tool: "avkit_capture", action: "sheet", method: "POST", path: "/captures/sheet" },
 # runner-fake-backend.test.ts:190-193 (S9)
-    // MEU-134 (Session 62, D-591): capture.frames sits between crop and capture_interactive.
-    expect(ids.indexOf("capture.capture_interactive")).toBe(ids.indexOf("capture.frames") + 1);
+    // MEU-134 (Session 62, D-591): capture.frames sits right after crop.
+    expect(ids.indexOf("capture.frames")).toBe(ids.indexOf("capture.crop") + 1);
+    // MEU-135 (Session 63): capture.sheet sits between frames and capture_interactive.
+    expect(ids.indexOf("capture.capture_interactive")).toBe(ids.indexOf("capture.sheet") + 1);
```

The excerpt is abridged. The source is `ports/capture.py:61` and `:94`, `routes/captures.py:353`, `registry.ts:136` and `runner-fake-backend.test.ts:190-193`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-11-capture-video-sheet-implementation-critical-review.md`, on the ledger loop `s63-execution-2026-11-11-capture-video-sheet`.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | none (0 findings; 13,275,057 tokens) | `7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652` |

Codex recomputed the tested_state independently and ran its own probes:
- 2,360 size cases against a rational oracle;
- 1,800 short spans;
- 13 schema refusals;
- Pillow tiling and metadata checks;
- four real-FFmpeg scaled grabs equal to full-decode references.

It graded every test group Strong, except the new `audit/coverage.test.ts` cases, which it graded Adequate. It noted two prose slips, which are now corrected:
- the gate's `real-ffmpeg` step runs `test_video_real_ffmpeg.py` alone;
- the gate's `py-tests` step has 32 warnings.

### Verdict

`approved` by Codex in round 1, with no finding. MEU-135 moves to `approved` at H2-2.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Export copy | feature | MEU-136 (Session 64) | Grouping §3; D-593 |
| The description eval | eval | Session 64 | Grouping D-505; D-593 |
| `avkit_capture.sheet` in `BASELINE_PENDING` | known issue | The next authoritative baseline update | D-603 on D-499 A's terms; `--update-baseline` needs Mat's words |
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`, `CAPTURE-EXIF-SCANNED-ORIENTATION` | known issue | Their own sessions | D-604; not observed here; never fixed here |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2) |

**Execution notes.**
- **A failure before the times are known.** `gate.last_ms` holds 0, or the parsed `start`, until the cell times are known, as for frames. So a body abandoned before the probe ends reports `frame grab failed at 00:00:00.000`, or at `start`.
- **A grab that finds no FFmpeg.** `FFmpegNotFoundError` from a grab is masked as `the sheet could not be written` (503), as `SHEET_WRITE`'s mapping says. AC-135.16 expects the masked 503.
- **One source for the bounds.** `schemas/captures.py` imports `SHEET_GRID_MIN`, `SHEET_GRID_MAX` and `SHEET_GRID_DEFAULT` from `video_input.py` and the `REGION_MAX_EDGE_*` bounds from the domain.
- **The infrastructure imports `video_input`.** `CaptureAdapter.sheet` reads `sheet_label_px` and `sheet_label_stroke` from core's `video_input.py`. Infra already depends on core, and no layering test bars it.
- **Formatting.** `routes/captures.py:491` was not ruff-format clean at `7403f18` and was left alone. Only this session's lines were formatted.
- **The status write.** `meu_status.py update` re-wraps other MEUs' YAML, so its output was discarded, the pre-row copy restored, and only MEU-135's fields byte-edited (S15, Session 61 RULE-5). `render --check` passes.

### Departures and their basis

- **`_run_gated` takes `not_written`.** The plan names `_run_gated(worker_name, deadline_s, return_s, body)`. The built helper also takes the masked message, because frames and sheet each answer an unknown commit outcome with their own words (`the frames could not be written` and `the sheet could not be written`).
- **`_grab_sheet`, not `_grab_cells`.** The plan's Files table names `_grab_cells`. The built function is `_grab_sheet` (`services/capture.py:907`), because it grabs the cells and also tiles, writes and probes the sheet.
- **One test function, several mechanisms.** Some AC-135.13 and AC-135.11 functions drive more than one sub-case through parametrize ids, as Session 62's AC-134.8 tests do.
- **Added cases beyond the plan's list.** Huge finite times at the route, the self-loop symlink at the unit level, a span inside the video, and a check that the temp is opened exclusively.
- **The S9 order pin.** `runner-fake-backend.test.ts:191` moved in Green row 3 (§Evidence). No execution decision was needed, because S9 names the action.
- **09's look note.** 09's Delivered note says "a white, a black and a portrait 5×5 look sheet". The white and black sheets are grid 3, and only the portrait one is grid 5 (§Scope gives the sizes). The wording was left as is, because 09 is a gated input.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-11 | claude-code-local (Claude Opus 5.5) | Initial MEU-135 handoff after the H1-2 gate |
