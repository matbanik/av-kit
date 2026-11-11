---
date: "2026-11-10"
project: "video-probe-frames"
meu: "MEU-134"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-10-video-probe-frames-MEU-133-handoff.md"
---

# Handoff: 2026-11-10-video-probe-frames-MEU-134-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-134 `capture-video-frames`. A caller takes still frames from a local video at given times, or a count of evenly spaced frames, and gets each as a new PNG shot in the capture inbox with source `Video`.
- **REST.** `POST /api/v1/captures/frames` takes `{path, at}` or `{path, count, start?, end?}` and answers 201 with `{video, frames}`. `video` holds `path`, `duration_ms`, `width`, `height` and `fps`. Each `frames` item holds `id`, `path`, `time_ms`, `timecode`, `width` and `height`. No image bytes are returned.
- **MCP.** `avkit_capture` `frames` sends the same body, minus `action`, with `ADD_TIMEOUT_MS` (120 s) under D-577 A.
- **Rulings.**
  - D-576 A: a file with no duration takes `at` only, grabbed with output seek; `count` is refused.
  - D-577 A: at most 20 frames, a 100 s body deadline, and a 120 s client timeout.

**Build Plan Section**: [09 §Video frames](../../../docs/build-plan/09-screenshot-capture.md) (`:1121`; the Delivered note at `:1141`).
**Predecessor**: [MEU-133 handoff](2026-11-10-video-probe-frames-MEU-133-handoff.md), this session's sibling. It owns `VIDEO_INPUT`, `TIMECODE`, `RUN_UTF8` and the probe route that `frames` reuses. The grouping is `.agent/context/grouping/2026-11-09-video-stills-session-grouping.md` (Sessions 62 to 64, D-500 to D-505).

- **Core module (row 5; D-578, D-581).** `packages/core/src/avkit_core/services/video_input.py` adds:
  - `FRAMES_MAX` (`:28`) and `TIME_MAX_MS` (`:30`);
  - `VideoFrame` (`:59`) and `VideoFrames` (`:71`);
  - `parse_time` (`:161`) with `_time_ms` (`:173`), for `TIME_PARSE`;
  - `frame_times` (`:200`), for `FRAME_TIMES`;
  - `frame_name` (`:214`), for `FRAME_NAME`.
- **Ports and enum (row 1; D-574, D-582, D-588).**
  - `FrameSeek` (`packages/core/src/avkit_core/ports/capture.py:64`) and `FramePort` (`:67`), with `probe` (`:70`) and `grab_frame` (`:72`).
  - `MediaPort.probe` (`ports/media.py:30`) gains the defaulted keyword-only `timeout_s` (D-588).
  - `CaptureSource.Video = "Video"` after `Crop` (`packages/core/src/avkit_core/domain/enums.py:223`). `RegisterSourceWire` doesn't gain it.
- **Service (row 5; D-576, D-579, D-580, D-587).** In `packages/core/src/avkit_core/services/capture.py`:
  - `FRAMES_DEADLINE_S = 100` (`:116`), `FRAMES_RETURN_S = 105` (`:119`), `COMMIT_WAIT_S = 6` (`:120`) and the worker name `avkit-frames` (`:122`);
  - the constructor keywords `frames=` and `monotonic=` (`:463`, `:471`);
  - `frames_from_video` (`:642`), which runs the return gate (`:658-692`);
  - `_frames_body` (`:703`), which runs `FRAME_CHECKS` (the probe with `timeout_s` at `:737`), `NO_DURATION`, `FRAME_WRITE`'s three phases and `FRAME_DEADLINE`'s four checks (`:811`, `:893`, `:897`, `:941`, `:955`);
  - one `capture.frames` log line with the count and shot ids (`:761`).
- **Adapter (row 5; D-575).** In `packages/infrastructure/src/avkit_infra/media/adapter.py`:
  - `grab_frame` (`:545`) runs input or output seek to a pipe, with one deadline set on entry;
  - `_last_video_ms` (`:600`) is `END_GAP`'s packet read through its own bounded `subprocess.run` (UTF-8, `errors="replace"`, `:635-636`).
- **API (row 5).**
  - `TimeWire` (`packages/api/src/avkit_api/schemas/captures.py:261`), `CaptureFramesIn` (`:264`), `CaptureFramesVideoOut` (`:285`), `CaptureFrameOut` (`:295`) and `CaptureFramesOut` (`:306`).
  - The route is at `packages/api/src/avkit_api/routes/captures.py:317`, declared before `/{id}`.
  - `wiring.py:222` passes `frames=media`.
  - `openapi.committed.json` is regenerated.
- **MCP (row 5; D-577 A, D-583).**
  - `mcp-server/src/toolsets/capture.ts`: `FRAMES_TEXT` (`:58`), the map (`:84`) and the strict schema with its `.refine` (`:275-278`), after `crop`.
  - `mcp-server/src/toolsets/registry.ts`: the `ACTION_INDEX` row (`:135`) after `crop`, and `frames` in `ADD_TIMEOUT_MS` (`:392-393`).
  - `mcp-server/scripts/audit/plan.ts`: the offline `capture.frames` step with `at: [0]` on the made clip, after `capture.crop`.
- **Tests.**
  - `tests/unit/test_domain_capture.py:900`: AC-134.1.
  - `tests/unit/test_video_input.py`: AC-134.2 to .4.
  - `tests/unit/test_capture_frames_service.py` (new, LF): AC-134.5 to .8.
  - `tests/unit/test_media_adapter_frames.py`: AC-134.9.
  - `tests/integration/test_video_real_ffmpeg.py`: AC-134.10 and .11.
  - `tests/e2e/test_api_capture_frames.py` (new, LF): AC-134.12 to .14.
  - `mcp-server/tests/capture.test.ts` and `audit/coverage.test.ts`: AC-134.15 and .16.
  - `tests/e2e/test_api_openapi.py:192`: AC-134.17.
  - The pins in §Pins that move (rows 1, 4a and 4b).
- **Spec text and records (row 6).** 09's Delivered note (`docs/build-plan/09-screenshot-capture.md:1141`), MEU-134 `ready_for_review` with this plan (`.agent/context/meu-registry.md:196`), and grouping row 62 `executed`.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-10. The Codex plan review approved at round 4 ([plan-critical-review.md](2026-11-10-video-probe-frames-plan-critical-review.md)). The plan's human rulings are quoted in its decision log: D-573, D-576 and D-577, each "A", on Mat's "all recommendations are accpeted, proceed". Then Mat said:
- "start execution" (2026-11-10T22:28:44-05:00);
- "for any questions ask fable subagent and accept ruling from it" (2026-11-10T22:29:50-05:00).

The receipt for both is `s62-exec-authorization.txt` (lines 2 and 3), with HEAD `7b9f34d`. Under the second, D-588 to D-592 were ruled by a Fable subagent. That delegation covers execution questions only. It doesn't cover a commit or a push, which wait on Mat's own words, or the review's approval, which is Codex's.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The video path** goes from the request to `VIDEO_INPUT`, then to FFmpeg's and ffprobe's argv and to the 201 body's `video.path`. It is never logged and never put in an error message. Its only writer is the caller (AC-134.13).
- **The video's stem** goes through `import_stem` into the frame names. The names reach the inbox, the rows, the 201 body and the Capture page. `import_stem` keeps word characters, space and `-`, so a control character or a lone surrogate never reaches a name. A reserved stem becomes `import_CON`, and an empty one becomes `import` (AC-134.4).
- **A requested time** reaches an error message only as the `TIMECODE` of the parsed milliseconds, never as the caller's text. A refused time gives the fixed `a time must be seconds or HH:MM:SS.mmm`, which echoes nothing (AC-134.2).
- **The duration** reaches the past-the-end message as `TIMECODE`, for example `time 00:00:03.000 is past the end (00:00:03.000)`.
- **FFmpeg's and ffprobe's stderr**, which name the path, are dropped. `FRAME_GRAB` discards stderr, and `END_GAP` reads stdout only.
- **The frame bytes** go from FFmpeg's stdout pipe to the call's own `.avkit-tmp` file. They are then checked for the PNG signature, decoded by the image probe and moved into place. FFmpeg never writes into the inbox.
- **Frame paths** go to the 201 body and the rows. `capture.frames` logs the count and shot ids only, and `_upsert_shot`'s existing `capture.registered` line logs the shot id and source name (`NO_RAW_OUTPUT`).
- **The marker check.** AC-134.13 puts the video under a marker folder and the marker in the fake's FFmpeg stderr. It drives every error on the real stack with `HealthService` built first (Session 54 RULE-2). The marker is absent from every body, the log ring, stdout and stderr, and a positive control finds it.
- **No network.** Every video was made locally with the pinned FFmpeg. A URL is refused before any probe.

### Documented limits

- **A raw stream is slow.** With no duration, an `at` grab uses output seek, which decodes from the start (D-576 A).
  - `probe4b-receipt.txt` (1080p raw H.264): T=60 took 639 ms, T=300 took 2565 ms and T=540 took 4568 ms.
  - `probe4-receipt.txt` (4K raw HEVC): T=60 took 6.9 s and T=540 took 76.4 s.
  - A late time on a large raw stream can therefore pass `FRAMES_DEADLINE_S` and fail with `frame grab failed at`. The MCP description says to remux such a file with `avkit_convert add`.
- **A time between the last frame and the end returns the last frame** (`END_GAP`). On `counter25.mp4`, T=2.970 to 3.000 gave no frame with input seek (`probe13-receipt.txt`). The fallback reads the last packet time and grabs at that time minus 1 ms.
- **Frames are the first at or after their time.** They are not the nearest frame. The MCP description says `at or after`.
- **An abandoned body.** When the return gate gives up at 105 s, the worker ends when its current wait ends. That wait is a grab within its own timeout, one frame's decode, or a pool checkout within 30 s. Then it removes what it made (D-587). Only a commit still running at 111 s answers the masked 503 without knowing whether the shots were kept.
- **`CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` and `CAPTURE-EXIF-SCANNED-ORIENTATION`** were not observed in this session's runs. They are left to their own sessions.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-134.1 | unit | `VIDEO_SOURCE` and `FRAME_PORT`: `Video` is the last `CaptureSource` member, directly after `Crop`; `"video"` isn't a `RegisterSourceWire` arg (a register body with it is a 422); `FramePort` names `probe` and `grab_frame` with keyword-only `seek` and `timeout_s`; `FFmpegAdapter`'s signatures match. A characterisation of row 1, passing at row 4a as a guard | 09 Source, Grab | `tests/unit/test_domain_capture.py:900`; `tests/e2e/test_api_capture_frames.py:258` | ✅ |
| AC-134.2 | unit | `TIME_PARSE`: seconds, `M:SS` and `H:MM:SS.mmm` forms with exact half-up rounding (`0.0005` → 1, `0.0004` → 0, `1.0005` → 1001, `"99:59:59.999"` → 359,999,999); `True`, −1, NaN, inf, `"1:60"`, `"1:2"`, `"a"`, `""`, an Arabic digit, a lone surrogate, NUL, 33 characters, `"100:00:00"` and `360000` each give the fixed message, which echoes no input; a finite float far past the cap (`1e25`, `1e100`, `1e308`, `-1e25`) gives the same message, not `decimal.InvalidOperation`, with nothing chained (D-592) | 09 Times; D-578; D-592 | `tests/unit/test_video_input.py:277`, `:284`, `:343`, `:356`, `:370` | ✅ |
| AC-134.3 | unit | `FRAME_TIMES`: (0, 3000, 3) → [500, 1500, 2500]; the 2 h list; the end cap (0, 3, 5) → [0, 1, 2]; (2999, 3000, 2) → [2999]; an exhaustive loop keeps every time in `[start, end)`; `at` duplicates collapse and sort | 09 Spacing | `test_video_input.py:390`, `:396`; `tests/unit/test_capture_frames_service.py:506` | ✅ |
| AC-134.4 | unit | `FRAME_NAME`: `standup-t00h12m05.500s`, the 0 and 359,999,999 bounds, `Łodz` kept, `CON` → `import_CON`, `..` → `import` | 09 Name; D-581 | `test_video_input.py:438` | ✅ |
| AC-134.5 | unit | `FRAME_CHECKS`: each refusal runs no grab, leaves the inbox empty and adds no row; those before the probe record zero probes; `end` equal to the duration is accepted; `count: 2, start: 2.999` on 3,000 ms grabs once, at 2,999 | 09 Times, Errors; D-579 | `test_capture_frames_service.py:378`, `:397`, `:442`, `:465`, `:476`, `:484`, `:494`, `:514` | ✅ |
| AC-134.6 | unit | `FRAME_WRITE` all or nothing: an empty or non-PNG third grab, an image-probe refusal on the second temp, and an `os.replace` failure on the second temp each leave no `.png`, no `.avkit-tmp` and no new row, and a pre-existing shot unchanged; the messages carry no marker and nothing is chained | 09 Writes; D-580 | `test_capture_frames_service.py:540`, `:553`, `:571` | ✅ |
| AC-134.7 | unit | Concurrency and names: two calls at once behind a `Barrier` get `clip-t00h00m01.000s.png` and `_2`, each with its own bytes; an inbox file, a row and another writer's `.avkit-tmp` of that name each give `_2`, and the other writer's temp is left byte for byte | 09 Tests, Name | `test_capture_frames_service.py:599`, `:636`, `:645`, `:658` | ✅ |
| AC-134.8 | unit | `FRAME_DEADLINE` with an injected clock: the probe and each grab get the time left; (a) before a grab, (b) during one, (c) both lock waits bounded, (d) between publish and commit; every `acquire` passes a timeout; (e) the return gate abandons a stuck decode and a stuck checkout within 2 s of real time, waits for a slow commit, masks a stuck one, and passes the worker's own `ValidationError` with `__context__` `None`; the ruled values 100, 105 and 6 | D-577; D-587 | `test_capture_frames_service.py:672` (through `:949`) | ✅ |
| AC-134.9 | unit | `FRAME_GRAB` and `END_GAP` with a recording fake `subprocess.run`: the exact argv for both seeks; `T` formatted exactly; failure and timeout give `b""`; `FileNotFoundError` gives `FFmpegNotFoundError`; the packet read's interval, parser (largest time, `N/A` skipped) and retry; one deadline for every process; `probe`'s `timeout_s` and `ffprobe timed out`; no `timeout` keyword when none is given | 09 Grab; D-575 | `tests/unit/test_media_adapter_frames.py:202` (through `:432`) | ✅ |
| AC-134.10 | integration | Real FFmpeg, by Pillow pixel equality with a full-decode reference: the counter clip at 0, 1.0, 1.02, 2.96 and 2.999 (`END_GAP`); the VFR clip at 1.05 and 2.05; the long-audio clip at 3.2; `at: [3.0]` refused with zero grabs; the `Łodz.mp4` name starts `Łodz-t`; every source's SHA-256 unchanged | 09 Tests; D-584 | `tests/integration/test_video_real_ffmpeg.py:234`, `:253`, `:268`, `:280`, `:293`, `:330` | ✅ |
| AC-134.11 | integration | `NO_DURATION` on the raw `.h264` under D-576 A: `at: [1.0]` gives frame 25 by pixel equality, and `count: 2` gives the fixed message | 09 Errors; D-576 | `test_video_real_ffmpeg.py:305`, `:319` | ✅ |
| AC-134.12 | API | `POST /captures/frames` on the real stack: both shapes give 201 with exactly `{video, frames}` and their keys, in time order, with the files in the inbox; each schema refusal is the fixed 422 | 09 Request, Response | `tests/e2e/test_api_capture_frames.py:177`, `:231`, `:247` | ✅ |
| AC-134.13 | API | Errors on the real stack: not found (missing file and self-loop symlink, no probe and no grab), the URL, past the end, `frame grab failed at`, the masked 503 for `FFmpegNotFoundError` and for a write failure; the marker absent everywhere, with a positive control; a huge finite `at`, `start` or `end` is the fixed 422 with no grab, no file and no row (D-592) | 09 Errors; S54 RULE-2; D-592 | `test_api_capture_frames.py:273`, `:362` | ✅ |
| AC-134.14 | API | `GET /captures`, `GET /captures/{id}` and `/image` show each frame with source `"Video"`, size and bytes; a later scan keeps `"Video"` | 09 Source, Response | `test_api_capture_frames.py:380` | ✅ |
| AC-134.15 | MCP | `FRAMES_MCP`: both shapes accepted and each refusal before fetch; the body minus `action` with `ADD_TIMEOUT_MS` (D-577 A); `start: null` refused (transport parity); its own four markers, `at or after` and `avkit_convert probe` in its workflow | 09 Request, Description; D-583 | `mcp-server/tests/capture.test.ts:948`, `:994`, `:1026` | ✅ |
| AC-134.16 | MCP | `ACTION_INDEX` has 73 rows with `frames` after `crop`; transport parity of the 201 body; `BASELINE_PENDING` lists both new actions; `AUDIT_PLAN` has an offline step for each; coverage fails when the frames step is missing | 09 Tests; D-583 | `capture.test.ts:1042`, `:1057`; `mcp-server/tests/audit/coverage.test.ts:166`, `:216` | ✅ |
| AC-134.17 | API | OpenAPI: the frames route with `CaptureFramesIn` and `CaptureFramesOut` in the committed snapshot; 76 operations; `--check` passes; `/frames` before `/{id}` | 09 Tests | `tests/e2e/test_api_openapi.py:192`; H1-4 | ✅ |
| AC-133 (cross-ref) | cross-reference | MEU-133's ACs, AC-133.1 to AC-133.9, are owned and evidenced by the MEU-133 handoff. `frames` reuses its `VIDEO_INPUT` (AC-133.1), `TIMECODE` (AC-133.2) and the `video_probe` mapping (AC-133.3) | plan §MEU-133 | [MEU-133 handoff](2026-11-10-video-probe-frames-MEU-133-handoff.md) | ✅ |
| AC-8 (cross-ref) | regression | AC-8.12 (`tests/integration/test_filesystem_media.py:445-477`) pins `FFmpegAdapter`'s `MediaPort` signatures equal to the protocol's; with `probe`'s `timeout_s` on both sides (D-588) it passes | plan `FRAME_PORT`; D-588 | gate `py-tests` | ✅ |
| AC-130 (cross-ref) | regression | AC-130.7's member-order pin moves from `Crop` last to `members[members.index("Crop") + 1] == "Video"`; AC-134.1 checks the last member | plan §Pins that move | `tests/unit/test_domain_capture.py:884-892`; gate `py-tests` | ✅ |
| AC-38 (cross-ref) | regression | AC-38.5's shared capture markers (`capture.test.ts:168`) are unchanged: `frames` carries the four marker words from `FRAMES_TEXT` | plan §Pins that move | `capture.test.ts:168`; gate `mcp-tests` | ✅ |
| AC-67 (cross-ref) | regression | AC-67.17's description check (`capture.test.ts:438-449`) is unchanged and passes with `frames` | plan §Pins that move | `capture.test.ts:438-449`; gate `mcp-tests` | ✅ |
| AC-68 (cross-ref) | regression | AC-68.5's `AUDIT_ACTION_SET` and AC-68.1/AC-68.4's built-server discovery count 73 actions; `BASELINE_PENDING` gains `avkit_capture.frames`; MEU-130's order pin moves to `capture_interactive` after `frames` (D-591) | plan §Pins that move; D-591 | `mcp-server/tests/audit/coverage.test.ts`, `runner-fake-backend.test.ts:77`, `:189`; gate `mcp-tests` | ✅ |
| AC-4 (cross-ref) | regression | AC-4.12 bans `assert` in core source; `capture.py`'s new code uses explicit checks instead | `tests/unit/test_domain.py` AC-4.12 | gate `py-tests` | ✅ |
| AC-16, AC-31 (cross-ref) | regression | AC-16.6 walks the 76 `ROUTE_INDEX` rows and AC-31.17 the static-before-id routes; both assert `path in paths` first (D-589, MEU-133's handoff) | D-589 | `test_api_openapi.py:121-122`, `test_api_conversions.py:637-639`; gate `py-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-134.2 to AC-134.14, AC-134.17 (Python) | Row 4a: 151 failed, 200 passed against row 1's stubs and row 3's tree. `DID NOT RAISE ValidationError` ×53; `{"detail":"Method Not Allowed"}` ×22; `assert 405 == 422` ×19; `assert 0 == 1` ×11; `assert [] == ['ffmpeg', 'ffprobe']` ×8; `assert b'' == b'\x89PNG…frame'` ×6 | Row 5: 770 passed; gate `py-tests` 1800 passed (after D-592) | `test_video_input.py:277-438`, `test_capture_frames_service.py:378-949`, `test_media_adapter_frames.py:202-432`, `test_video_real_ffmpeg.py:234-330`, `test_api_capture_frames.py:177-380`, `test_api_openapi.py:192` |
| AC-134.1 | A characterisation of row 1: row 4a's guard passed 1 | Gate `py-tests` | `test_domain_capture.py:900` |
| AC-134.15, AC-134.16 (MCP) | Row 4b: Test Files 6 failed; Tests 19 failed, 131 passed (150). `expected [ …(72) ] to have a length of 73 but got 72`; `expected [] to have a length of 1 but got +0`; the `frames` body `expected false to be true` | Row 5: 35 files, 498 passed; gate `mcp-tests` 498 passed | `capture.test.ts:948-1057`, `coverage.test.ts:166`, `:216` |
| AC-134.2, AC-134.13 (D-592) | `s62-d592-red.txt`: 7 failed, 1 passed. `assert <class 'decimal.InvalidOperation'> is ValidationError` ×3; `assert 500 == 422` ×4. `minus-1e25` passed already, because a negative is refused before the Decimal step | `s62-d592-green.txt`: 349 passed; gate `py-tests` 1800 passed | `test_video_input.py:356`, `test_api_capture_frames.py:362` |

- **red-check.** Row 4a's receipt: 1 receipt, 14 required tests, 0 problems. Row 4b's: 1 receipt, 2 required tests, 0 problems. Every failing block is an assertion.
- **The passes in the Red runs.** Row 4a's 200 passes are MEU-133's tests (Green since row 3), the moved pins' neighbours and the cases row 1's stubs already met. Row 4b's 131 passes are the MCP tests that don't read `frames`.
- **D-591, row 5's first MCP run.** AC-134.16 (`coverage.test.ts:171`) puts `capture.frames` directly after `capture.crop`. MEU-130's order pin (`runner-fake-backend.test.ts:189`, D-492) put `capture.capture_interactive` there. Both can't hold. Under the Fable ruling A, only `:189` changed, with a comment naming D-591. It now asserts `capture_interactive` directly after `frames`. The plan's pin sweep covered count pins, not order pins. Row 4b couldn't trip this pin because the step didn't exist until row 5. This is a test edit in a Green row, disclosed here.
- **Repeat runs.** The concurrency, deadline and return-gate tests ran five more times in row 5, at 67 passed each time.
- **D-592, after execution review round 1.** Codex approved round 1 with one non-blocking finding, F1: a huge finite float time reached `_time_ms`, whose Decimal quantize raised `InvalidOperation`, so `frames` answered the generic 500. Under the Fable ruling A, two new tests went Red first.
  - red-check refused the first Red run, because the unit cases failed by an escaping `InvalidOperation` with no assertion line (receipts `s62-d592-red-run1-refused.txt`, `s62-d592-red-check-run1.txt`). The unit test now catches any exception and asserts its type is `ValidationError`, as D-589 did, and the rerun passed red-check.
  - The Green guard is one condition in `_time_ms` (`video_input.py:184`): a float above `_FLOAT_SECONDS_GUARD`, 1e9 s, returns `None` before the Decimal step. That is far above `TIME_MAX_MS` and far below Decimal's 28-digit context, so no accepted time changes.
  - Fable's constraint 3 asked whether inf and NaN are reachable. `json.loads` accepts `Infinity` and `NaN`, and a probe through the real stack gave the fixed 422 for `Infinity`, `NaN` and `-Infinity`, with no grab and an empty inbox (`s62-d592-inf-probe.txt`). The probe script exited 1 after printing the three results, because its temp folder's cleanup hit the still-open SQLite file. `math.isfinite` already refused them, so no issue is filed.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-10-video-probe-frames/baseline.ps1 *> C:/Temp/av-kit/s62-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit; base suites in C:/Temp/av-kit/s62-base-py.txt, s62-base-mcp.txt, s62-base-ruff.txt and s62-base-mcp-build.txt)", "scope": "Row 0: rulings, anchors, baseline.sha and baseline-dirty.txt, line endings, the offline FFmpeg probe, base suites and the identity selftest", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d before any row", "output": "Base suites: pytest 1565 passed in 120.62s; MCP 35 files, 485 passed; ruff All checks passed!; MCP build exit 0. Identity selftest: 0 failures, every artifact state_unchanged=True. baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-1-types", "command": "rtk proxy uv run pytest (test_domain.py, test_domain_capture.py, test_api_captures.py and the MediaPort pin files) *> C:/Temp/av-kit/s62-types-py.txt; rtk proxy uv run pyright *> C:/Temp/av-kit/s62-types-pyright.txt; rtk proxy uv run ruff check *> C:/Temp/av-kit/s62-types-ruff.txt; the caller grep *> C:/Temp/av-kit/s62-r1-callers.txt (task.md row 1's Validation cell)", "scope": "Row 1: the shared names as wrong stubs (video_input.py, FramePort, MediaPort.probe's timeout_s under D-588, CaptureSource.Video), the CaptureSource pins, and the caller and pin grep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 1", "output": "241 passed in 7.37s; pyright 0 errors; ruff All checks passed!; caller grep 121 lines (CaptureService(, ConversionService(, _run( callers, CaptureSource and MediaPort pins)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-4a-red-134-py", "command": "rtk proxy uv run pytest tests/unit/test_video_input.py tests/unit/test_media_adapter_frames.py tests/unit/test_capture_frames_service.py tests/e2e/test_api_capture_frames.py tests/integration/test_video_real_ffmpeg.py tests/e2e/test_api_openapi.py tests/e2e/test_api_downloads.py tests/e2e/test_api_bodies.py --tb=short -q *> C:/Temp/av-kit/s62-py-red-134.txt; red-check.py with the 14 --require ids *> C:/Temp/av-kit/s62-py-red-134-check.txt; pytest tests/unit/test_domain_capture.py -k test_ac_134_1_ *> C:/Temp/av-kit/s62-r4a-guard.txt (task.md row 4a's Validation cell)", "scope": "MEU-134 Python Red: AC-134.2 to AC-134.14 and AC-134.17 against row 1's stubs, plus AC-134.1 as a passing guard", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 4a", "output": "151 failed, 200 passed in 21.06s. Decisive: DID NOT RAISE ValidationError x53; {\"detail\":\"Method Not Allowed\"} x22; assert 405 == 422 x19; assert 0 == 1 x11; assert [] == ['ffmpeg', 'ffprobe'] x8. red-check: 1 receipt(s), 14 required test(s), 0 problem(s). AC-134.1 guard: 1 passed, 108 deselected"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-4b-red-134-mcp", "command": "rtk proxy npm --prefix mcp-server run build *> C:/Temp/av-kit/s62-r4b-mcp-build.txt; rtk proxy npm --prefix mcp-server run test -- tests/capture.test.ts tests/convert.test.ts tests/action-index.test.ts tests/m7-resource.test.ts tests/audit/coverage.test.ts tests/audit/runner-fake-backend.test.ts *> C:/Temp/av-kit/s62-mcp-red-134.txt; red-check.py --require AC-134.15 --require AC-134.16 *> C:/Temp/av-kit/s62-mcp-red-134-check.txt (task.md row 4b's Validation cell)", "scope": "MEU-134 MCP Red: AC-134.15, AC-134.16 and the moved MCP pins, on a fresh build", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 4b", "output": "Test Files 6 failed (6); Tests 19 failed | 131 passed (150). Decisive: expected [ ...(72) ] to have a length of 73 but got 72 x4; expected [] to have a length of 1 but got +0 x2. red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-5-green-134", "command": "rtk proxy uv run pytest (row 5's 22 files: the MEU-133 and MEU-134 tests, every CaptureService caller and capture guard, test_domain, test_domain_capture, test_api_wiring and the conversion guards) --tb=short -q -rfE *> C:/Temp/av-kit/s62-py-green-134.txt; real FFmpeg *> C:/Temp/av-kit/s62-r5-real-ffmpeg.txt; export_openapi.py --check *> C:/Temp/av-kit/s62-r5-openapi.txt; git diff -- openapi.committed.json *> C:/Temp/av-kit/s62-r5-openapi-diff.txt; pyright, ruff, MCP build, MCP test and typecheck *> C:/Temp/av-kit/s62-r5-*.txt and C:/Temp/av-kit/s62-mcp-green-134.txt (task.md row 5's Validation cell, after D-591)", "scope": "MEU-134 Green: TIME_PARSE, FRAME_TIMES, FRAME_NAME, FRAME_CHECKS, NO_DURATION, FRAME_GRAB, END_GAP, FRAME_WRITE, FRAME_DEADLINE with the return gate, FRAMES_ROUTE, FRAMES_MCP, NO_RAW_OUTPUT and the frames audit step", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 5", "output": "770 passed in 38.19s; real FFmpeg 23 passed in 4.04s; openapi --check exit 0; the OpenAPI delta adds only /api/v1/captures/frames and CaptureFrameOut, CaptureFramesIn, CaptureFramesOut, CaptureFramesVideoOut, nothing changed or removed, CRLF kept (7354 CRLF, 7354 LF); pyright 0 errors; ruff All checks passed!; MCP Test Files 35 passed (35), Tests 498 passed (498); typecheck exit 0. FFmpegAdapter callers: 267 passed. Concurrency and deadline repeats: 67 passed, five times"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-6-records", "command": "task.md row 6 (abridged), run from P:/av-kit: the S3 check, the pre-status copies, the 08 and 09 Delivered notes, tools/meu_status.py update MEU-133 and MEU-134 ready_for_review --plan, the S15 byte-edit route and render; grouping row 62; then its Validation cell into C:/Temp/av-kit/s62-r6-render.txt and its status check into C:/Temp/av-kit/s62-r6-status.txt", "scope": "Row 6: the D3 spec text, MEU-133 and MEU-134 ready_for_review with this plan, the render, and grouping row 62 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 6", "output": "Drift check passed - SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content. status ['ready_for_review', 'ready_for_review']; grouping row 62 executed; spec notes True True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-10-video-probe-frames/session-gate.ps1 *> C:/Temp/av-kit/s62-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', '_sha256 ', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit; per-step receipts C:/Temp/av-kit/s62-D6-*.txt; rerun after D-592, the first run's receipt kept as C:/Temp/av-kit/s62-gate-h1-pre-d592.txt)", "scope": "H1-2: the registered D6 gate on the whole tree, shared by MEU-133 and MEU-134", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651", "output": "baseline failures excused: py [], mcp []; ui-types, ui-lint, ui-tests, ui-build, ui-electron, mcp-audit, build-record and package-build skipped with reasons; identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); task-contract exit=0 (26 rows, 24 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 57, outside scope: [], head moved (S3): False, baseline-dirty paths changed since row 0: []); red-check-selftest exit=0 (43 fixtures, 13 positive, 30 negative, 0 wrong); py-tests exit=0 (1800 passed in 142.05s); openapi exit=0; mcp-types exit=0; mcp-build exit=0; mcp-tests exit=0 (35 files, 498 passed); state-render exit=0 (142 MEUs, 12 phases); issues-render exit=0 (known-issues.md is up-to-date); status-canon exit=0 (2 files, 14 passed); real-ffmpeg exit=0 (23 passed in 4.24s); identity-after exit=0 (tested_state before = after); session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-d592-red", "command": "rtk proxy uv run pytest on the two D-592 tests (tests/unit/test_video_input.py::test_ac_134_2_huge_finite_times_get_the_fixed_refusal and tests/e2e/test_api_capture_frames.py::test_ac_134_13_huge_finite_times_get_the_fixed_refusal) > C:/Temp/av-kit/s62-d592-red.txt 2>&1; red-check.py with --require for both > C:/Temp/av-kit/s62-d592-red-check.txt (the refused first run kept as C:/Temp/av-kit/s62-d592-red-run1-refused.txt and C:/Temp/av-kit/s62-d592-red-check-run1.txt)", "scope": "D-592 Red: execution review round 1 F1, a huge finite float time, at the unit and API levels", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 6, the D-592 tests and no fix", "output": "7 failed, 1 passed in 6.77s. Decisive: assert <class 'decimal.InvalidOperation'> is ValidationError x3; assert 500 == 422 x4. minus-1e25 passed, because a negative is refused before the Decimal step. red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-d592-green", "command": "rtk proxy uv run pytest tests/unit/test_video_input.py tests/e2e/test_api_capture_frames.py tests/unit/test_capture_frames_service.py tests/unit/test_conversion_probe.py tests/e2e/test_api_conversion_probe.py tests/unit/test_domain.py tests/unit/test_domain_capture.py -p no:cacheprovider -q > C:/Temp/av-kit/s62-d592-green.txt 2>&1; ruff check and ruff format --check on the three changed files > C:/Temp/av-kit/s62-d592-ruff.txt 2>&1; pyright video_input.py > C:/Temp/av-kit/s62-d592-pyright.txt 2>&1", "scope": "D-592 Green: _time_ms refuses a float above _FLOAT_SECONDS_GUARD (1e9 s) before the Decimal step; the time, frames and probe tests and test_domain (a core edit, Session 54 RULE-1)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 6 and the D-592 fix", "output": "349 passed in 7.95s; ruff check exit 0; ruff format --check exit 0; pyright 0 errors, 0 warnings, 0 informations; video_input.py, test_video_input.py and test_api_capture_frames.py stay LF (0 CRLF)"}
```

### Quality Gate Results

`s62-gate-h1-2` (H1-2) is the fresh full record for both MEUs. Its last line is:

> session-gate: all steps exit 0

- **The rerun after D-592.** The first H1-2 run passed at `7b9f34d+eb0ad811…` (receipt `s62-gate-h1-pre-d592.txt`). Execution review round 1 approved with one finding, F1, and its fix under D-592 changed `video_input.py` and two test files. So the gate ran again on the whole tree, and this section and the `s62-gate-h1-2` record describe that run.
- **Static checks.**
  - pyright: 0 errors, 0 warnings, 0 informations. ruff check: all checks passed.
  - lint_task_contract passed on 26 rows (24 fully checked; H1-5 and H2-1 are exempt as `view_file`).
  - scope-paths found 57 changed paths, none outside scope. That is the first run's 54 plus the two handoffs and `current-focus.md`, written after it. HEAD `7b9f34d` did not move, and none of the paths in `baseline-dirty.txt` changed since row 0 (S3).
  - The red-check selftest read 43 fixtures (13 positive, 30 negative), with 0 wrong.
- **Suites.**
  - pytest: 1800 passed (the baseline's 1565 plus 235 new cases for the two MEUs, 8 of them D-592's).
  - MCP: 498 passed in 35 files (the baseline's 485 plus 13).
  - real-ffmpeg: 23 passed (`test_video_real_ffmpeg.py`'s 15 and `test_extract_real_ffmpeg.py`'s 8).
  - status-canon: 14 passed.
- **Build and state.**
  - `export_openapi.py --check`, the MCP typecheck and the MCP build exited 0.
  - The state render and the issue render match the files on disk.
  - H1-3's `render --check` and H1-4's `export_openapi.py --check` passed after the gate.
- **Skipped.** Each skip has a reason in the gate:
  - the UI steps: no `ui/` file changed;
  - `mcp-audit`: it needs the live network, which the brief forbids, and AC-134.16 covers `AUDIT_PLAN`'s new steps offline;
  - `build-record`: no installer build;
  - `package-build`: no packaged surface change.
- **Identity.**
  - The tested_state was the same before and after: `7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651`.
  - The closeout records are left out of the identity, so writing them doesn't change it.

### The row 5 OpenAPI diff

`export_openapi.py` regenerated `openapi.committed.json`, and CRLF was kept (7354 CRLF line ends, no bare LF). Against row 3's file, the delta (`r5-openapi-delta.txt`) adds:
- the path `/api/v1/captures/frames`;
- the schemas `CaptureFrameOut`, `CaptureFramesIn`, `CaptureFramesOut` and `CaptureFramesVideoOut`.

It changes no path or schema, and it removes nothing.

### The rulings' D-504 receipts

- **D-575, `END_GAP`** (`probe13-receipt.txt`, `probe4-receipt.txt`).
  - On `counter25.mp4` (75 frames, the last at 2.960 s, duration 3.000), input seek gave frame 1.04 for T=1.010 to 1.040. It gave no frame for T=2.970 to 3.000.
  - On a clip whose audio runs to 3.5 s, T=2.999, 3.2 and 3.49 gave no frame.
  - The last video packet's time was found in 0.04 to 0.11 s. On the 2 h 4K HEVC file, a read from 7195.0 gave 7199.981 in 0.09 s.
  - AC-134.10 proves the fallback on real FFmpeg: 2.999 returns frame 74, and on the long-audio clip 3.2 returns frame 74.
- **D-576 A, `NO_DURATION`** (`probe13-receipt.txt`, `probe4-receipt.txt`, `probe4b-receipt.txt`).
  - A raw `.h264` has format `h264` and no duration. Every input seek on it gave no frame.
  - Output seek works but is slow: 639 to 4568 ms on 1080p H.264, and 6.9 to 76.4 s on 4K HEVC.
  - AC-134.11 proves `at: [1.0]` returns frame 25 by pixel equality, and that `count` is refused.
- **D-577 A, `FRAMES_MAX` 20 and `FRAMES_DEADLINE_S` 100** (`probe2-receipt.txt`).
  - On a 2 h 4K HEVC file (11.29 GB), the probe took 0.07 s.
  - 20 midpoint grabs took 13.6 s in all, and 20 grabs just before a keyframe took 13.8 s (mean 0.69 s), with 0 failures.
  - So 20 frames fit well inside 100 s, and 100 s plus the return gate fits inside the client's 120 s.
- **D-583, the workflow line.** `FRAMES_TEXT` reads `Workflow: call avkit_convert probe for the duration, then avkit_capture frames to POST /captures/frames, then image to view a frame.` Session 63 adds `sheet`.

### Caller and pin grep (S55 RULE-1, S59 RULE-1, Session 61 RULE-3)

- **`CaptureService(`** is built in `wiring.py` (with `frames=media`, `:222`) and in the capture test fixtures. `test_capture_service.py`, `test_api_capture_flatten.py`, `test_api_capture_region_import.py`, `test_api_capture_crop.py` and `test_api_captures.py` build it without `frames`. All of them ran in row 5's 770 and pass in the gate.
- **`FFmpegAdapter`'s callers** ran in row 5's caller set (267 passed).
- **`CaptureSource` pins.** These moved in row 1:
  - `test_domain_capture.py:18-27` and `:884-892` (AC-130.7);
  - `test_domain.py:298-307`;
  - `test_api_captures.py`'s `SOURCE_OUT`.
- **Count and order pins.** The count neighbours were grepped again in rows 4a and 4b, and every hit is in §Pins that move. The one order pin the sweep missed is D-591's.
- **Absence pins.** A grep for tests asserting that `frames` or `Video` is absent found none. The `frames` hits in conversion `UNIT_LABELS` are unrelated.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/video_input.py` | new | `TIME_PARSE`, `FRAME_TIMES`, `FRAME_NAME`, `VideoFrame`, `VideoFrames`, `FRAMES_MAX`, `TIME_MAX_MS`, `_FLOAT_SECONDS_GUARD` (D-592) (and MEU-133's names). LF |
| `packages/core/src/avkit_core/ports/capture.py`, `ports/media.py` | modified | `FRAME_PORT`; `MediaPort.probe`'s `timeout_s` (D-588) |
| `packages/core/src/avkit_core/domain/enums.py` | modified | `VIDEO_SOURCE` |
| `packages/core/src/avkit_core/services/capture.py` | modified | `frames=` and `monotonic=`; `frames_from_video` and `_frames_body` |
| `packages/core/src/avkit_core/services/conversion.py` | modified | Row 5: `probe_file` returns `video_probe` |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | modified | `FRAME_GRAB`, `END_GAP` (and MEU-133's `RUN_UTF8`) |
| `packages/api/src/avkit_api/routes/captures.py`, `schemas/captures.py`, `wiring.py` | modified | `FRAMES_ROUTE`; `frames=media` |
| `openapi.committed.json` | regenerated | The frames route and its four schemas |
| `mcp-server/src/toolsets/capture.ts`, `registry.ts` | modified | `FRAMES_MCP`, its `ACTION_INDEX` row and `ADD_TIMEOUT_MS` |
| `mcp-server/scripts/audit/plan.ts` | modified | The offline `capture.frames` step |
| `tests/unit/test_capture_frames_service.py` | new | AC-134.3, .5 to .8. LF |
| `tests/e2e/test_api_capture_frames.py` | new | AC-134.1 (register), .12 to .14; AC-134.13's huge-time cases (D-592). LF |
| `tests/unit/test_video_input.py`, `test_media_adapter_frames.py`, `tests/integration/test_video_real_ffmpeg.py` | new | AC-134.2 to .4, .9, .10, .11 (and MEU-133's); AC-134.2's huge-time cases in `test_video_input.py` (D-592). LF |
| `tests/unit/test_domain_capture.py`, `test_domain.py`, `tests/e2e/test_api_captures.py` | modified | AC-134.1; the `CaptureSource` pins |
| `tests/e2e/test_api_openapi.py`, `test_api_downloads.py`, `test_api_bodies.py` | modified | AC-134.17; the counts 75 → 76 and 72 → 73; the frames valid body |
| `mcp-server/tests/capture.test.ts`, `convert.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `audit/coverage.test.ts`, `audit/runner-fake-backend.test.ts` | modified | AC-134.15, .16; the counts 72 → 73, capture 11 → 12; `BASELINE_PENDING`; the order pin (D-591) |
| `docs/build-plan/09-screenshot-capture.md` | modified | The Delivered note (`:1141`) |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | Only MEU-133's and MEU-134's fields and rows, and grouping row 62 (row 6) |

Line endings were measured with Python bytes before each edit and kept:
- These files stayed CRLF: `enums.py`, `ports/capture.py`, `services/capture.py`, `adapter.py`, `routes/captures.py`, `schemas/captures.py`, `wiring.py`, `capture.ts`, `registry.ts`, `plan.ts`, the MCP test files, `test_domain_capture.py`, `test_domain.py`, `test_api_captures.py`, `test_api_openapi.py`, `test_api_downloads.py`, `openapi.committed.json` and 09.
- `test_api_bodies.py` stayed LF.
- New files are LF.

```diff
 # enums.py
+    # VIDEO_SOURCE (MEU-134, D-582): a still taken from a local video by POST /captures/frames.
+    Video = "Video"
 # ports/capture.py
+FrameSeek = Literal["input", "output"]
+class FramePort(Protocol):
+    def probe(self, file_path: Path, *, timeout_s: float | None = None) -> MediaInfo: ...
+    def grab_frame(self, path: Path, time_ms: int, *, seek: FrameSeek, timeout_s: float) -> bytes: ...
 # routes/captures.py
+@router.post("/frames", status_code=201, response_model=CaptureFramesOut)
 # runner-fake-backend.test.ts:189 (D-591)
-    expect(ids.indexOf("capture.capture_interactive")).toBe(ids.indexOf("capture.crop") + 1);
+    // MEU-134 (Session 62, D-591): capture.frames sits between crop and capture_interactive.
+    expect(ids.indexOf("capture.capture_interactive")).toBe(ids.indexOf("capture.frames") + 1);
```

The excerpt is abridged. The source is `enums.py:222-223`, `ports/capture.py:64-72`, `routes/captures.py:317` and `runner-fake-backend.test.ts:189-190`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-10-video-probe-frames-implementation-critical-review.md`, on the ledger loop `s62-execution-2026-11-10-video-probe-frames`.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | F1 (Medium, non-blocking): a huge finite float time, such as `1e25`, passed `CaptureFramesIn`, and `_time_ms`'s Decimal quantize raised `InvalidOperation`, so `frames` answered the generic 500 instead of the fixed 422. Fixed under D-592 | `7b9f34d4e93b9fc733277278859f2b9ec26abdb8+eb0ad8111e0de603143b55d4bd3be55581f7f9dc158fc7372d4348aa504ea75b` |
| 2 | approved, `intent_achieved: yes` | F1 `fixed`; no new findings. Codex compared 9,325 non-negative floats up to 1e9 with the pre-fix parser and all matched. A guard on sign only, or one placed after the quantize, still raised `InvalidOperation` on 1e25, 1e100 and 1e308. 2,484,514 tokens | `7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651` |

### Verdict

Approved at round 2 of 6, with 0 open findings (H1-7a and H1-7b, `C:/Temp/av-kit/review-state-check.txt` and `exec-review.txt`). The canonical review is a byte-for-byte copy of Codex's report, SHA-256 `6d866fbb5a20eede…`. MEU-133 and MEU-134 move to `approved` at H2-2.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Contact sheet (`sheet`) | feature | MEU-135 (Session 63) | Grouping §3 |
| Export copy | feature | MEU-136 (Session 64) | Grouping §3 |
| The description eval | eval | Session 64 | Grouping D-505 |
| `avkit_capture.frames` in `BASELINE_PENDING` | known issue | The next authoritative baseline update | D-499; `--update-baseline` needs Mat's words |
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`, `CAPTURE-EXIF-SCANNED-ORIENTATION` | known issue | Their own sessions | Not observed here; never fixed here |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2) |

**Execution notes.**
- **A failure before the times are known.** `gate.last_ms` holds 0, or the parsed `start`, until the frame times are known. So a body abandoned before the probe ends reports `frame grab failed at 00:00:00.000`, or at `start`.
- **A grab that finds no FFmpeg.** `FFmpegNotFoundError` from a grab is masked as `CaptureFailedError` (503 `internal_error`), as `FRAME_WRITE`'s mapping says. AC-134.13 expects the masked 503.
- **One source for the bounds.** `schemas/captures.py` imports `FRAMES_MAX` and `MAX_PATH_CHARS` from `video_input.py`.
- **No `assert` in core.** Two asserts in `capture.py` became explicit checks, because AC-4.12 bans `assert` in core source.
- **Formatting.** `capture.py` and `routes/captures.py` were not ruff-format clean at `7b9f34d`. Only this session's lines were formatted. `adapter.py` was clean at `7b9f34d` and is clean now. `schemas/captures.py`, `conversion.py` and `video_input.py` are clean.
- **Shared rows.** Rows 0, 1 and 6 and the H1-2 gate serve both MEUs; their records are in both handoffs.

### Departures and their basis

- **D-588** (the plan's Decision Log, `implementation-plan.md:697-711`): `MediaPort.probe` gains `timeout_s` so AC-8.12 holds. It was ruled at row 1 by the Fable subagent.
- **D-591** (below): MEU-130's order pin moved in Green row 5.
- **D-592** (below): after execution review round 1, `_time_ms` refuses a float above 1e9 s before the Decimal step. Two tests were added after approval and went Red first.
- **Row 4a, where AC-134.3's `at` case lives.** The `at` de-duplication is a service behaviour, because `video_input.py` has no `at` function. Its test is in `test_capture_frames_service.py:506`.
- **Row 4a, refusals checked by type.** 21 times, `count` 0 and `count` 21 assert the `ValidationError` type only, because the plan fixes no message for them.
- **Row 4a, a real unit of work.** The service tests use a real SQLite unit of work with hooks, so the rollback they check is real.
- **Row 4a, added cases.**
  - Cases beyond the plan's list: a bad `start`, `end` with `at`, `start` as an object, the path schema refusals, and a register body with source `video` (tagged AC-134.1).
  - A parametrize id `count-start-end` was renamed `range`, because red-check's pytest header parse didn't read it.
- **Row 4a, files left unformatted.** `ruff format --check` flags `test_api_openapi.py` and `test_api_downloads.py`, from before row 4a. They were left alone.
- **Row 5, the shared mapping.** `video_probe(resolved, info)` moved into `video_input.py`, so `PROBE_MAP` has one writer, and `conversion.py` was touched again.
- **Row 5, `_run`'s calls.** `_run` makes two explicit `subprocess.run` calls, because pyright rejects a `**dict` splat.
- **Row 6, where the 08 note sits.** The 08 Delivered note sits after the Tests row at `:627`, not at the `:629` the plan cited.

---

## Decision Log

```yaml
decision_log:
  - id: D-591
    stage: execution
    question: "Row 5: AC-134.16 (coverage.test.ts:171) puts capture.frames directly after capture.crop, and MEU-130's order pin (runner-fake-backend.test.ts:189, D-492) puts capture.capture_interactive there. Both can't hold. How does row 5 go on?"
    resolution: autonomous
    class: two-way
    chosen: "A: move the old pin to assert capture_interactive directly after capture.frames, with a comment naming D-591; a test edit in a Green row, disclosed to the execution review"
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md AC-134.16 — frames after crop in ACTION_INDEX and AUDIT_PLAN"
      - "mcp-server/tests/audit/runner-fake-backend.test.ts:187-188 — MEU-130's D-492 line, which pins crop's insertion between revert and capture_interactive"
    research:
      engine: none
      sources: []
    reasoning: "AC-134.16 is the plan-approved statement. The D-492 line guarded the adjacency as of Session 59; it isn't a ruling that nothing may be inserted. The plan's pin sweep covered count pins, not order pins, and row 4b couldn't trip it because the step didn't exist until row 5. B, moving frames after capture_interactive, inverts an approved AC to protect an incidental assertion; C, a plan amendment, spends a halt and a re-review on a one-line move; doing nothing leaves row 5 failing. Ruled by the Fable subagent under Mat's standing delegation, USER_EXPLICIT 2026-11-10 'for any questions ask fable subagent and accept ruling from it'. Two-way: one test line."
    human_message_reference: null
  - id: D-592
    stage: execution
    question: "Execution review round 1, F1 (Medium, non-blocking): a finite float time such as 1e25 makes _time_ms's Decimal quantize raise InvalidOperation, so frames answers the generic 500 instead of the fixed 422. Fix now with a recheck round (A), record it as a known issue and do nothing now (B), or fix without a recheck (C)?"
    resolution: autonomous
    class: two-way
    chosen: "A: fix now, with a recheck round; guard on magnitude far above the cap (abs(value) > 1e9 s) before the Decimal step, with a negative case; F1 only"
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md TIME_PARSE and AC-134.2 — every time refusal is the one fixed message"
      - "C:/Temp/av-kit/s62-exec-review-round-1.md F1 — the reproduction at video_input.py:184"
    research:
      engine: none
      sources: []
    reasoning: "The plan's contract names a single fixed 422 for every time refusal, and this 500 is reachable through the public API on a caller-supplied value, so B would knowingly ship a contract departure that a short guard removes. The budget, about 19M left against about 5M for a recheck, covers an independent recheck. C is rejected because code changed after approval leaves the tested_state stale. The guard sits far above TIME_MAX_MS and far below Decimal's 28-digit context, so no accepted value changes. Infinity, NaN and -Infinity reach the route through json.loads and were already the fixed 422 (s62-d592-inf-probe.txt), so constraint 3 adds no issue. Ruled by the Fable subagent (C:/Temp/av-kit/s62-fable-d592.txt) under Mat's standing delegation, USER_EXPLICIT 2026-11-10 'for any questions ask fable subagent and accept ruling from it'. Two-way: one guard line."
    human_message_reference: null
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-10 | claude-code-local (Claude Opus 5.5) | Initial MEU-134 handoff after the H1-2 gate |
| Updated | 2026-11-11 | claude-code-local (Claude Opus 5.5) | Execution review round 1 approved with F1; D-592 fixed it; the H1-2 gate reran |
