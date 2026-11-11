---
project: "2026-11-10-video-probe-frames"
date: "2026-11-10"
source: ".agent/context/grouping/2026-11-09-video-stills-session-grouping.md#session-62--video-probe-frames-meu-133-meu-134--p2"
grouping_source: ".agent/context/grouping/2026-11-09-video-stills-session-grouping.md"
meus: ["MEU-133", "MEU-134"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Video probe and frames (Session 62)

> **Project:** `2026-11-10-video-probe-frames`
> **Build plan:** `docs/build-plan/08-video-conversion.md` §Media probe (residual) (`:614-629`, anchor `media-probe-residual`, MEU-133) and `docs/build-plan/09-screenshot-capture.md` §Residuals registered 2026-11-09 → §Video frames (`:1119-1139`, anchor `video-frames`, MEU-134).
>
> **Source request.** On 2026-11-09 Mat asked whether an agent can take stills from a video through av-kit, to review meeting recordings and security camera footage, and accepted every recommendation of the video stills design (`_inspiration/video-stills/design.md`, D-1 to D-5; grouping D-500). This is the first of the grouping's three sessions (62 to 64). Done comes from 08's and 09's contracts, not from Mat's words: each rule holds with a behaviour test, the real-FFmpeg tests pass on generated clips, and the planning probes (grouping D-504) are run and cited here.
> **Known issues:** none open for these MEUs. `MCP-AUDIT-BASELINE-PENDING-CROP` stays open; this session adds `avkit_convert.probe` and `avkit_capture.frames` to the same pending list and never runs `--update-baseline`. `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` is out of scope. `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` and `CAPTURE-EXIF-SCANNED-ORIENTATION` are out of scope: an observation of either is recorded in the handoff and raised, never fixed here.
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review. Three questions were Mat's (§User Review Required): D-573, the FFmpeg output decoding fix; D-576, files with no duration; D-577, `FRAMES_MAX` and the request time limit. **Ruled 2026-11-10:** Mat accepted every recommendation ("all recommendations are accpeted, proceed"): D-573 A, D-576 A, D-577 A, no split, the plan-loop continue of +8.5M and an execution budget of about 30M over 3 rounds. Wherever this plan says "under B" or "under C" for these three, that text is the unchosen option.

## Goal

**Goal anchor:** Session 62 gives an agent two read-only steps over a local video. `POST /conversions/probe` and `avkit_convert` `probe` return a video's duration, size, codecs and streams without writing a job. `POST /captures/frames` and `avkit_capture` `frames` write still frames from that video into the capture inbox as new shots, at times the agent names or evenly spaced across a span, so `image`, `crop` and `annotate` work on them. The video is read in place and never changed, and nothing is uploaded.

Four things are missing today:

1. **No probe surface.** `MediaPort.probe` (`packages/core/src/avkit_core/ports/media.py:19`) reads duration, size and codecs for conversion jobs only (`services/conversion.py:275`, `:538`). No route or MCP action exposes it.
2. **FFmpeg's text output is decoded as the Windows code page.** `FFmpegAdapter._run` (`packages/infrastructure/src/avkit_infra/media/adapter.py:263-272`) calls `subprocess.run(…, text=True)` with no encoding. On this host that is cp1252, so ffprobe's UTF-8 JSON for a file named `Łodz.mp4`, or one with a `Ł` tag, fails in the reader thread and `probe` returns every field `None` (`C:/Temp/av-kit/s62/probe5-receipt.txt`). D-573 asks Mat whether to fix it here.
3. **No way to grab a frame.** Nothing in core reaches FFmpeg for a still. `CaptureService` (`services/capture.py:380`) has screen, import and crop paths only, and `CaptureSource` (`domain/enums.py:209-221`) ends at `Crop`.
4. **No frames surface.** No route, schema or MCP action takes a video path and times.

The session ends when 08's §Media probe (residual) and 09's §Video frames hold with a behaviour test per rule, the real-FFmpeg tests pass, the D-504 receipts are cited, the session gate's last line is `session-gate: all steps exit 0`, D-573, D-576 and D-577 are ruled, and MEU-133 and MEU-134 are `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-10). No payload is oversized: services/capture.py (1352 lines), adapter.py (639) and mcp-server/scripts/audit/plan.ts (1675) were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s62-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s62\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
  - No row runs Electron, so `ELECTRON_RUN_AS_NODE` doesn't matter here; the gate clears it anyway.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s62-plan-canonical-2026-11-10-video-probe-frames` and `s62-execution-2026-11-10-video-probe-frames`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290), and the `--review-state-only` receipt is rebuilt there.
  - Reviewer prompts name the ledger vocabulary up front: D-570 to D-588, AC-133.1 to AC-133.9, AC-134.1 to AC-134.17, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). Each recheck asks for a `### New Findings` table and bare words in its Recheck cells (`fixed`, `open`).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, the live MCP audit, `--update-baseline`, a tag, release or upload, or an `approved` verdict authored by the implementer. Video stays local: no test or row reads a video from the network or uploads one, and a URL is refused as video input. Every clip is generated by the pinned FFmpeg from `lavfi` sources in a temp folder. Nothing touches the installed avkit MCP servers, Mat's inbox, Mat's videos or YouTube.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-133 `convert-media-probe` | `.agent/context/handoffs/2026-11-10-video-probe-frames-MEU-133-handoff.md` |
| MEU-134 `capture-video-frames` | `.agent/context/handoffs/2026-11-10-video-probe-frames-MEU-134-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-10-video-probe-frames-plan-critical-review.md` and `.agent/context/handoffs/2026-11-10-video-probe-frames-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, `s62-anchors.txt` |
| WP-2 | Type-only names (row 1) | WP-1 | shared | `video_input.py` stubs, `FramePort`, `FrameSeek`, `CaptureSource.Video`, the `probe_file`, `frames_from_video` and `grab_frame` stubs, the moved `CaptureSource` pins |
| WP-3 | MEU-133 Red, then Green (rows 2a, 2b, 3) | WP-2 | shared | `VIDEO_INPUT`, `TIMECODE`, `PROBE_MAP`, `RUN_UTF8`, `PROBE_ROUTE`, `PROBE_MCP`; the OpenAPI snapshot with the probe route |
| WP-4 | MEU-134 Red, then Green (rows 4a, 4b, 5) | WP-3 | shared | `TIME_PARSE`, `FRAME_TIMES`, `FRAME_NAME`, `FRAME_CHECKS`, `FRAME_GRAB`, `END_GAP`, `NO_DURATION`, `FRAME_WRITE`, `FRAME_DEADLINE`, `FRAMES_ROUTE`, `FRAMES_MCP`; the OpenAPI snapshot with both routes |
| WP-5 | Records (row 6) | WP-4 | shared | The 08 and 09 notes, MEU status, renders, grouping tracker |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | The two handoffs, review, reflection, Session 63's prompt |

MEU-133 runs first because frames calls the same probe and `video_input` module (grouping §3 order). Each Green regenerates the OpenAPI snapshot, so every row's own check passes; the commit holds one snapshot covering both routes.

**Split flag (D-570): no 62b.** The grouping (`:67`) asked for 62a/62b only if Session 59 hadn't closed when this session was planned, or if MEU-133's handoff passed about half the context. Session 59 closed (`meu-status.yaml` MEU-130 `approved`). MEU-133 is one route, one MCP member and one adapter fix over existing code (9 ACs), and the probes are already run. If the session passes about half its context before row 4, the coordinator tells Mat; nothing moves without Mat's words, because a split pays a second plan review and a second OpenAPI and registry regeneration.

## User Review Required

> [!IMPORTANT]
> **Three questions are Mat's.** Every other choice is recorded as autonomous in §Decision Log (D-570 to D-572, D-574, D-575, D-578 to D-588), with its alternatives. The gate asks Mat to accept the plan, rule D-573, D-576 and D-577, set the execution budget, and override any autonomous choice. Only Mat's words start execution.
>
> **D-573: does this session fix how FFmpeg's text output is decoded?** (`contract-departure`.) 08's Reuse rule says probe "calls the existing `MediaPort.probe` as it is". As it is, `FFmpegAdapter._run` decodes ffprobe's UTF-8 JSON as cp1252. Planning probe 5 ran the real adapter: a clip named `Łodz.mp4`, and a clip with a `Ł` title tag, both came back with every field `None`, and the reader thread printed a `UnicodeDecodeError` traceback to the backend's stderr. CJK and emoji names happened to decode (`probe5-receipt.txt`). A missing `Ł` file gave `MediaProbeError("ffprobe failed")`.
> - **A (Recommended): fix `_run` here.** Add `encoding="utf-8", errors="replace"` to `_run`'s `subprocess.run` (`RUN_UTF8`). It is two keywords and no new ffprobe code. Its six callers (`adapter.py:383`, `:398`, `:420`, `:491`, `:493`, `:518`) are FFmpeg's `-version`, convert, probe, `-encoders`, `-hwaccels` and the GPU encoder smoke (one `lavfi` frame per candidate encoder); their tests run in the row. `END_GAP`'s packet read doesn't go through `_run`, because it needs a timeout, so it decodes UTF-8 itself under either option. A real-FFmpeg test probes a `Ł` path and a `Ł` tag, and a unit test records the keywords. Conversion jobs on such files get correct durations too. `_run_with_progress` (`:274`, callers `:570`, `:608`, `:639`) reads FFmpeg's `-progress` lines and isn't changed here; whether it has the same fault is named in the handoff as an observation for Mat, not fixed.
> - **B, do nothing:** keep `probe` as it is. A video whose name or tags hold a character outside cp1252 probes as all-`None`: `probe` answers `has_video: false` and `duration_ms: null`, and `frames` refuses it with `not a video: no video stream`. The fix becomes its own known issue. AC-133.6 is withdrawn, and AC-133.7's and AC-134.10's `Ł` cases are dropped.
>
> **D-576: what do frames do with a video that has no duration?** (`contract-departure`.) 09's Errors rule says a file with no duration fails `count`, "and `at` still works". Raw camera streams (`.h264`, `.dav`) have no container duration. Planning probe 3 showed that the contract's input seek (`-ss T -i V`) returns no frame at any time on such a stream, even T=0 (`probe13-receipt.txt`). Output seek (`-i V -ss T`) decodes from the start and does return the frame, but its cost grows with T: 0.64 s at 60 s and 4.57 s at 540 s for raw 1080p H.264 (`probe4b-receipt.txt`), and 6.9 s at 60 s and 76.4 s at 540 s for raw 4K HEVC (`probe4-receipt.txt`).
> - **A (Recommended): output seek for files with no duration.** When `probe` gives no duration, `frames` grabs with output seek, under `FRAME_DEADLINE`, with no past-the-end check (there is no end to check). `count` fails with `count needs a duration; this video has none, so use at`. A time past the stream's end gives `frame grab failed at {t}`. The description tells the agent that remuxing a raw stream into a container (`avkit_convert add` with fast copy) gives it a duration and fast grabs. This keeps 09's "`at` still works".
> - **B: refuse frames with no duration.** Both shapes fail with a fixed message telling the agent to remux first. Simple and fast-failing, but it departs from 09's "`at` still works".
> - **C, do nothing:** input seek for every file, as 09's Grab rule reads. `count` fails as 09 says; every `at` on a raw stream fails with `frame grab failed at {t}`, so 09's "`at` still works" is false.
>
> **D-577: does `FRAMES_MAX` stay 20, and how long may a `frames` call run?** (`governance-value`.) Design D-4 set `FRAMES_MAX` to 20 and grouping D-504 lets the plan lower it from planning probe 2. On a 2 h 4K HEVC file (11.3 GB, keyframe every 10 s), 20 midpoint grabs took 13.6 s and 20 worst-case grabs (the last frame before each keyframe) 13.8 s, about 0.69 s each, with no failure (`probe2-receipt.txt`). The MCP client's default request timeout is 30 s (`mcp-server/src/client.ts:14`); `add`, `capture` and `crop` already use 120 s (`ADD_TIMEOUT_MS`, `:13`, chosen in `toolsets/registry.ts:388-393`). 13.8 s isn't close to 30 s on this machine, but a slower disk or CPU, or a 4K stream with longer keyframe gaps, can be.
> - **A (Recommended): keep 20, give `frames` the 120 s client timeout, and stop at 100 s.** `avkit_capture` `frames` joins the `ADD_TIMEOUT_MS` list. `FRAMES_DEADLINE_S = 100` bounds the whole call: every FFmpeg and ffprobe run in it (each grab, and `END_GAP`'s packet read and retry) gets the time left as its timeout, the time is checked again after each grab and once more just before the first shot is published, and when it runs out the call fails with `frame grab failed at {t}` and writes nothing. The server never publishes shots after the client has given up, with 20 s to spare for the publish step. `probe` keeps the 30 s default (0.07 s on the 2 h file).
> - **B: lower `FRAMES_MAX` to 10, keep the 30 s default, and stop at 25 s.** Half the frames per call; an agent wanting 20 calls twice. `FRAMES_DEADLINE_S = 25` bounds the call as under A, with 5 s to spare. The cap of 10 is carried through `FRAMES_ROUTE`, `FRAMES_MCP`, `FRAMES_TEXT` and their tests: every `20` there reads `10`, and every `21` reads `11`.
> - **C, do nothing:** keep 20 and the 30 s default timeout. `FRAMES_DEADLINE_S = 25` bounds the call as under A, so a slow call fails before the client gives up. The measured 13.8 s is recorded in the handoff.
>
> **What the words in the contracts mean here, and the limits they leave.**
> - **"Seconds as a number, or a string `SS`, `MM:SS` or `HH:MM:SS`, each with an optional `.mmm`."** A number is any JSON number from 0 up, rounded half-up to whole milliseconds; `true` and `false` aren't numbers. A string has ASCII digits only: one part is any number of seconds; two parts are minutes and two-digit seconds under 60; three parts are hours, two-digit minutes under 60 and two-digit seconds under 60. The last part may end in `.` and one to three digits. A string is at most 32 characters. Any time above `99:59:59.999` is refused. Every refusal is the fixed `a time must be seconds or HH:MM:SS.mmm`, which echoes nothing (`TIME_PARSE`, D-578).
> - **"A time at or past the end."** The end is the container's duration (`format.duration`), in whole milliseconds. A time equal to it is past the end. `end` itself may equal the duration, because the span is `[start, end)`.
> - **"Input seek `-ss T -i V -frames:v 1`."** FFmpeg returns the first decoded frame whose time is at or after T (`probe13-receipt.txt`: on a 25 fps clip, T=1.01 to 1.04 all gave the 1.04 s frame). Between the last video frame and the container's end (audio longer than video, or the last frame's own 40 ms), input seek returns nothing; `END_GAP` then returns the last video frame (D-575). The descriptions say both.
> - **"`time_ms` and `timecode`."** Each frame's `time_ms` is the time the agent asked for (or the midpoint), not the decoded frame's own time. The description says the frame is the one at or after it.
> - **"Duplicate times collapse."** Two requested times with the same whole millisecond give one frame. `count` larger than the span's milliseconds gives fewer frames than asked, and no spaced time reaches `end` (`FRAME_TIMES`).
> - **"`video_stem`."** The video's file stem through `import_stem` (`services/capture.py:166`), the same rule imports use, so a reserved name or one with only punctuation becomes `import…`.
>
> **The token estimate,** calibrated against Session 54 `convert-extract-index` (plan 8,541,302; execution 7,859,970: a convert route and real-FFmpeg tests), Session 58 `capture-region-import` (plan 19,334,552 over 3 rounds; execution 11,719,424: two capture MEUs, a new `CaptureSource` member, the import write pattern), Session 61 (plan 17,826,442 over 3 rounds; execution 11,215,121) and Session 60 (execution round 1 10,867,306, round 2 4,244,246). This session has two MEUs across core, infrastructure, the API and MCP, 26 ACs, a real-FFmpeg module and two OpenAPI regenerations. Expect 1 to 3 plan rounds (about 10M to 20M) and 2 to 3 execution rounds. The plan loop opens with the default 10.5M. At the plan gate Mat sets the execution loop's budget; the opening ask is round 1 ×2 plus one recheck at about half of round 1 (Session 60 RULE-5, Session 58 RULE-4): about 12M ×2 + 6M = 30M, 3 rounds. The citable AC families are fixed when the plan loop opens: AC-133 and AC-134.
>
> **Plan review round 1** (`.agent/context/handoffs/2026-11-10-video-probe-frames-plan-critical-review.md`, Codex, 8,410,076 tokens): `changes_required` with three blocking findings, each corrected in this plan (`C:/Temp/av-kit/s62-plan-corrections-r1.md`). F1: `VIDEO_INPUT` now maps `RuntimeError`, which a symlink loop raises. F2: `FRAME_DEADLINE` now bounds every process in the call and checks again before publishing, and the deadline sits below the client's timeout under every D-577 option. F3: `FRAME_TIMES` caps each midpoint below `end`.
>
> **Plan review round 2** (same file, Codex, 3,777,160 tokens): `changes_required`. F3 fixed; F1 partial, non-blocking; F2 partial, blocking. Each is corrected in this plan (`C:/Temp/av-kit/s62-plan-corrections-r2.md`). F2: `FramePort.probe` now gets the time left, both lock acquisitions are timed, the image probes run in phase 2, and a fourth check, (d), sits before the commit and rolls it back. F1: every fixed error is raised after its `except` clause has ended, so its `__context__` is `None` as well as its `__cause__`. Also corrected: `FramePort.probe`'s parameter is `file_path`, as `FFmpegAdapter.probe`'s is, since pyright matches a Protocol's parameter names; and row 5 now runs the tests of `_run`'s callers, because it extends `_run`.
>
> **Plan review round 3** (same file, Codex, 4,676,612 tokens): `changes_required`. F1 fixed, F3 fixed, F2 partial and blocking: the checks stop a late commit but not a late reply, because the image decode and SQLAlchemy's 30 s connection checkout have no bound. Mat then gave 3 more rounds and 30M tokens (USER_EXPLICIT 2026-11-10 "continue for another 3 rounds, add 30M tokens"; `C:/Temp/av-kit/s62-plan-continue-r3.txt`). Corrected (`C:/Temp/av-kit/s62-plan-corrections-r3.md`) by `FRAME_DEADLINE` (e), the return gate (D-587), which keeps D-577 A as ruled.
>
> **The gate.** Held 2026-11-10: Mat accepted every recommendation (§Decision Log D-573, D-576, D-577). Execution still waits for his words after the plan review approves.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `VIDEO_INPUT` | `require_local_video(text: str) -> Path` in the new `packages/core/src/avkit_core/services/video_input.py`. It refuses, with `ValidationError("path must be a local absolute file path")`: an empty string, a string over 4096 characters, one holding a control character (U+0000 to U+001F, U+007F) or a lone surrogate, a relative path, and a URL (two or more ASCII letters, digits, `+`, `.` or `-` before `:`, which keeps `C:` a drive and refuses `http:`, `file:` and `ftp:`). UNC paths are local and allowed. Every filesystem call (`Path(text)`, `is_absolute`, `resolve`, `is_file`) sits inside one `try`; an `OSError`, `ValueError`, `UnicodeError` or `RuntimeError`, a missing file and a path that isn't a regular file all give `ValidationError("video file not found")`. The `except` clause only records the failure, and the `ValidationError` is raised after the `try` statement has ended, when no exception is being handled, so its `__cause__` and `__context__` are both `None`. `raise … from None` inside the clause would only hide the path-bearing exception from a printed traceback; it would still be `__context__` (plan review round 2 F1). `RuntimeError` is there because on a symlink loop Python 3.12's `Path.resolve` raises `RuntimeError("Symlink loop from …")`, which isn't an `OSError` and carries the path in its text (`C:/Temp/av-kit/s62/probe-f1-symlink-loop.txt`); unmapped, it would be a logged 500 naming the path. It returns the resolved path. It never opens or writes the file. |
| `TIMECODE` | `format_timecode(ms: int) -> str` gives `HH:MM:SS.mmm` with two-digit hours (`TIME_PARSE` caps times below 100 h). `duration_ms(seconds: float \| None) -> int \| None` is `None` for `None`, a non-finite value or a value at or below 0, and otherwise `Decimal(repr(seconds)) * 1000` rounded half-up to an integer. Both are pure and live in `video_input.py`. |
| `PROBE_MAP` | `ConversionService.probe_file(path: str) -> VideoProbe` runs `VIDEO_INPUT`, then `self._media.probe(resolved)`. A `MediaProbeError` becomes `ValidationError("the file could not be probed")`, raised after the `except` clause has ended, as in `VIDEO_INPUT`, so ffprobe's stderr (which names the path) is neither its `__cause__` nor its `__context__`. `FFmpegNotFoundError` passes through to the existing 503. It writes no job row and starts nothing. `VideoProbe` is a frozen dataclass in `video_input.py` with the eleven response fields; `has_video` is `video_codec is not None`, `has_audio` is `audio_codec is not None`, `container` is `format_name` as `MediaInfo` gives it, and `path` is the resolved path as a string. |
| `RUN_UTF8` | Under D-573 A only. `FFmpegAdapter._run` passes `encoding="utf-8", errors="replace"` to `subprocess.run`; nothing else in it changes apart from `FRAME_PORT`'s `timeout` keyword, which every existing caller leaves unset. |
| `PROBE_ROUTE` | `POST /conversions/probe` in `routes/conversions.py`, declared before `/{id}` with `ConversionProbeIn {path: str}` (`extra="forbid"`, `min_length=1`) and `ConversionProbeOut` (200), calling `probe_file`. It is synchronous and writes nothing. `STATIC_BEFORE_ID` gains `/probe`. |
| `PROBE_MCP` | `avkit_convert` `probe`: `z.object({action: z.literal("probe"), path: z.string().min(1).max(4096)}).strict()`, appended after `gpu_refresh` in `convert.ts`, with the row `{ tool: "avkit_convert", action: "probe", method: "POST", path: "/conversions/probe" }` after `gpu_refresh`'s in `ACTION_INDEX` (`toolsets/registry.ts:121`). It keeps the 30 s default timeout. Its description is `desc("probe", "POST", "/conversions/probe")` plus `PROBE_TEXT`: `Reads a local video's duration, size, codecs and streams without changing it or writing a job. duration_ms and timecode are null for a raw stream with no duration. Use it before avkit_capture frames to pick times.` |
| `FRAME_PORT` | `FrameSeek = Literal["input", "output"]` and `class FramePort(Protocol)` in `ports/capture.py`: `probe(file_path: Path, *, timeout_s: float | None = None) -> MediaInfo` and `grab_frame(path: Path, time_ms: int, *, seek: FrameSeek, timeout_s: float) -> bytes`. `grab_frame` returns the PNG bytes, or `b""` when FFmpeg gives no frame, exits non-zero or runs past `timeout_s`. Its only raise is `FFmpegNotFoundError`. `probe`'s parameter is `file_path`, as in `MediaPort.probe` (`ports/media.py:30`) and `FFmpegAdapter.probe` (`adapter.py:403`), because pyright matches a Protocol's parameter names. `MediaPort.probe` (`ports/media.py:30`) gains the same keyword, because AC-8.12 (`tests/integration/test_filesystem_media.py:445-477`) pins the adapter's `MediaPort` signatures equal to the protocol's (D-588, an execution-time decision). `FFmpegAdapter.probe` gains the keyword `timeout_s: float | None = None` and passes it to `_run`'s new keyword `timeout: float | None = None`; `_run` passes `timeout=` to `subprocess.run` only when it isn't `None`, so its six existing callers make exactly the call they made before. In `probe`, `subprocess.TimeoutExpired` becomes `MediaProbeError("ffprobe timed out")`. `ConversionService.probe_file` passes no timeout. The existing `FFmpegAdapter` instance implements both; `wiring.py` passes `frames=media` to `CaptureService`. |
| `FRAME_GRAB` | `FFmpegAdapter.grab_frame` runs `[ffmpeg, -hide_banner, -nostdin, -v, error, -ss, T, -i, V, -frames:v, 1, -c:v, png, -f, image2pipe, pipe:1]` for `seek="input"` and `[ffmpeg, -hide_banner, -nostdin, -v, error, -i, V, -ss, T, -frames:v, 1, -c:v, png, -f, image2pipe, pipe:1]` for `seek="output"`, through `subprocess.run(…, capture_output=True, check=False, timeout=…)` in bytes mode. On entry `grab_frame` sets one deadline, `time.monotonic() + timeout_s`. Each process it starts (this grab, and `END_GAP`'s packet read and retry) gets `timeout=` the time left to that deadline, and when the time left is at or below 0 it starts nothing more and returns `b""`. `T` is `f"{ms // 1000}.{ms % 1000:03d}"`, exact with no float. FFmpeg writes to a pipe, never to the inbox. Its stderr is dropped, never logged. `FileNotFoundError` becomes `FFmpegNotFoundError`; `subprocess.TimeoutExpired` and a non-zero exit give `b""`. |
| `END_GAP` | When an input-seek grab gives `b""`, `grab_frame` reads the last video packet time with `[ffprobe, -v, error, -select_streams, v:0, -read_intervals, F%, -show_entries, packet=pts_time, -of, csv=p=0, V]` where `F` is `max(0, T − 60 s)`, through its own `subprocess.run(…, capture_output=True, check=False, text=True, encoding="utf-8", errors="replace", timeout=…)` with the time left, not through `_run`, so its timeout and decoding sit in one call. `TimeoutExpired`, a non-zero exit or no usable time gives `b""`. The last time is the largest value on stdout that parses as a finite number; `N/A` and blank lines are skipped, because B-frame packets don't arrive in time order. If its whole milliseconds are below the requested ms, it grabs again with input seek at `max(0, last_ms − 1)`, with the time left. Otherwise it returns `b""`. On the counter clip T=2.999 returns the 2.96 s frame; on a clip whose audio runs to 3.5 s and video to 3.0 s, T=3.2 returns 2.96 s (`probe13-receipt.txt`, `probe4-receipt.txt`: 0.09 s to find the last packet of the 2 h file). Output seek has no fallback. |
| `TIME_PARSE` | `parse_time(value: object) -> int` in `video_input.py` gives whole milliseconds. It takes an `int` or `float` that isn't a `bool`, is finite and is at least 0, through `Decimal(repr(value))` × 1000 rounded half-up; or a `str` of at most 32 characters matching `^(\d+)(?:\.(\d{1,3}))?$`, `^(\d+):([0-5]\d)(?:\.(\d{1,3}))?$` or `^(\d+):([0-5]\d):([0-5]\d)(?:\.(\d{1,3}))?$` with ASCII digits only (`re.ASCII`). A result above `TIME_MAX_MS = 359_999_999` is refused. Every refusal is `ValidationError("a time must be seconds or HH:MM:SS.mmm")`. |
| `FRAME_TIMES` | `frame_times(start_ms: int, end_ms: int, count: int) -> list[int]` is `min(end − 1, start + ((2i+1)·span + count) // (2·count))` for `i` in `0..count-1`, `span = end − start`: the midpoint of each of `count` equal parts, rounded half-up in integers, and capped at `end − 1` because the span is `[start, end)`. Without the cap a midpoint rounds onto `end` whenever `count` is at least `span`: (0, 3, 5) would give a 3, and `start: 2.999` on a 3 s video would grab at the duration. `FRAME_CHECKS` has already made `start` less than `end`, so `end − 1` is at least `start`. For `at`, the times are the parsed times. Either way the list is de-duplicated and sorted ascending before any check. |
| `FRAME_CHECKS` | `CaptureService.frames_from_video(path, *, at=None, count=None, start=None, end=None)` checks, in order, before any grab and before any inbox write: exactly one of `at` and `count`, and `start` and `end` only with `count` (a `ValidationError("use either at or count")` the API's schema already prevents); `VIDEO_INPUT`; each time through `TIME_PARSE`; `count` between 1 and `FRAMES_MAX`, `at` holding 1 to `FRAMES_MAX` times; `FramePort.probe`, where `MediaProbeError` becomes `the file could not be probed` and no video codec gives `not a video: no video stream`. With a duration: `start` defaults to 0 and `end` to the duration; any `at` time, or `start`, at or past the duration gives `time {t} is past the end ({duration})` with both as `TIMECODE`; `end` above the duration gives the same with `end`; then `start` at or after `end` gives `start must be before end`. With no duration: `NO_DURATION`. A refused call runs no grab and writes nothing. |
| `NO_DURATION` | Under D-576 A: with no duration, `count` gives `ValidationError("count needs a duration; this video has none, so use at")`; `at` grabs with `seek="output"` and skips the past-the-end check. Under B every call on such a file gives `ValidationError("this video has no duration; remux it into a container first")`. Under C it grabs with input seek as any other file. |
| `FRAME_NAME` | `frame_name(stem: str, ms: int) -> str` is `f"{import_stem(stem)}-t{HH}h{MM}m{SS}.{mmm}s"`, for example `standup-t00h12m05.500s`. The suffix is `.png`. `_import_dest` (`services/capture.py:604-626`) adds `_2`, `_3`… against inbox files, rows and other writers' `.avkit-tmp` names. |
| `FRAME_WRITE` | Three phases, all or nothing. Each time the call takes `CAPTURE_FILE_LOCK` it calls `CAPTURE_FILE_LOCK.acquire(timeout=left)`, where `left` is the time to `FRAME_DEADLINE`'s deadline, never a plain `with` (an ordinary wait behind another writer has no bound: plan review round 2 F2), and releases a lock it took in a `finally`; `left` at or below 0, or `acquire` returning `False`, is `FRAME_DEADLINE`'s expiry. (1) Under the lock and one unit of work: `ensure_dir(inbox)`, then for each time in order `dest = _import_dest(uow, inbox, frame_name(…), ".png")` and `open(dest + ".avkit-tmp", "xb")`, keeping every handle. Each new temp makes its own name taken for the next `_import_dest` call and for any other writer. (2) With the lock released: for each time, `grab_frame`, then `FRAME_DEADLINE`'s after-grab check, then a check that the bytes start with the PNG signature `89504e470d0a1a0a`, then `handle.write(bytes)`, `close()` and `self._annotate.probe(tmp)`, whose `ImageProbe` is kept for phase 3. So the full Pillow decode runs before the next grab's check or the publish check, never after the last check. (3) Under the lock and one unit of work: `FRAME_DEADLINE`'s publish check, then for each temp, if `dest` is now a file or a row holds it, a fresh `_import_dest` name is taken (whose taken set includes this call's own temps); then `os.replace(tmp, dest)` and `_upsert_shot(uow, dest, probe, now, CaptureSource.Video)` with the kept `ImageProbe`; then `FRAME_DEADLINE`'s commit check; then the unit of work commits once. Only the commit and the lock's release run after the commit check. Any failure in any phase closes every handle, unlinks every temp this call created and, before the lock is released, every dest it moved, lets the unit of work roll back (it rolls back on any exception, `packages/infrastructure/src/avkit_infra/database/unit_of_work.py:54-65`), and raises: an empty grab, a bad signature, an `InboxPathError` from the image probe or a passed deadline gives `ValidationError("frame grab failed at {t}")`; any other error gives `CaptureFailedError("the frames could not be written")` (503, masked). Each is raised after its `except` clause has ended, as in `VIDEO_INPUT`, so neither `__cause__` nor `__context__` holds a path. Unlinking this call's own temps needs no lock, as writing them in phase 2 doesn't, because no other writer opens, writes or removes them. A temp another writer made is never opened, written or removed. FFmpeg never writes into the inbox. |
| `FRAME_DEADLINE` | `FRAMES_DEADLINE_S` is set by D-577: 100 under A (client timeout 120 s), 25 under B or C (client timeout 30 s), so it is below the client's timeout under every option. The clock starts when `frames_from_video` is called, read through an injected `monotonic` (default `time.monotonic`), and `left` is the deadline minus the clock. Every wait the call can bound is bounded by `left`: `FRAME_CHECKS`' `FramePort.probe` gets `timeout_s=left` (`FRAME_PORT`); both lock acquisitions are `acquire(timeout=left)` (`FRAME_WRITE`); each grab gets `timeout_s=left`, and `FRAME_GRAB` bounds every process inside a grab by it, `END_GAP`'s included. It is checked at four points, and each expiry fails the call with `ValidationError("frame grab failed at {t}")` and leaves nothing (`FRAME_WRITE`'s cleanup). (a) Before each grab: at or below 0 the grab isn't started; `t` is that grab's time. A phase 1 lock not had in time fails the call here, with the first time, before any temp exists. (b) After each grab: at or below 0 the grab's bytes are dropped; `t` is that grab's time. (c) The publish check, in phase 3 once the lock is held and before the first `os.replace`: at or below 0 nothing is published; `t` is the last time. A phase 3 lock not had in time fails here too. (d) The commit check, in phase 3 after the last `_upsert_shot` and before the commit: at or below 0 every dest moved is unlinked under the lock and the unit of work rolls back; `t` is the last time. So no shot is committed after the deadline. After (d) only the commit runs, and its one wait is SQLite's `busy_timeout` of 5,000 ms (`packages/infrastructure/src/avkit_infra/database/engine.py:68`). The filesystem calls between the checks (`ensure_dir`, the name checks, the temp writes, `os.replace`) are local and wait on no other party, and each is followed by a check before anything is committed (plan review round 2 F2). (e) The return gate (D-587, plan review round 3 F2). Checks (a) to (d) stop a late commit but not a late reply, because two waits in the body have no bound of their own: the Pillow decode in `self._annotate.probe` (`packages/infrastructure/src/avkit_infra/capture/adapter.py:307-317`), and SQLAlchemy's connection checkout, whose `QueuePool` waits up to 30 s (`create_sqlite_engine` passes no pool arguments, `engine.py:78-83`; size 5, overflow 10, timeout 30.0 in `C:/Temp/av-kit/s62-plan-r3-pool-decode-probe.txt`). So `frames_from_video` runs its body (`FRAME_CHECKS` to `FRAME_WRITE`) on a daemon `threading.Thread` named `avkit-frames`, as `ConversionService` runs its worker (`packages/core/src/avkit_core/services/conversion.py:218`), and waits for it in `join(timeout=0.05)` steps, reading the elapsed time from the same injected `monotonic`. The call and its worker share one `threading.Lock` and a state: `running`, `committing` or `abandoned`. Check (d) runs under that lock: when the state is `abandoned` or no time is left, the worker fails and cleans up as in `FRAME_WRITE`; otherwise it sets `committing` and commits. When the worker ends, the call returns its result or raises the error object it raised, outside any `except` clause, so `__context__` stays `None`. When `FRAMES_RETURN_S` (105) has passed and the worker hasn't ended, the call takes the lock. In state `running` it sets `abandoned` and raises `ValidationError("frame grab failed at {t}")` with the last time, and the worker, whenever it reaches (d), commits nothing and removes what it made. In state `committing` it waits up to `COMMIT_WAIT_S` (6) more, for a commit whose one wait is the 5,000 ms `busy_timeout`, and returns the result; if the commit still hasn't ended it raises the masked `CaptureFailedError("the frames could not be written")`. Only that last case can't say what was kept: the rows are written and only SQLite's own commit is left, so the shots may still appear. Under the ruled A the call answers within 111 s and one 0.05 s step, against the client's 120 s, whatever the body is waiting on. An abandoned worker starts no FFmpeg process (check (a) fails once the deadline has passed), and it ends when its current wait ends: a grab within its own `timeout_s`, one frame's decode (0.16 s for a 7680x4320 frame in the probe above), or a checkout within 30 s. |
| `VIDEO_SOURCE` | `CaptureSource.Video = "Video"` after `Crop` in `domain/enums.py`, with the comment `# VIDEO_SOURCE (MEU-134, D-582): a still taken from a local video by POST /captures/frames.` `RegisterSourceWire` (`schemas/captures.py:19`) doesn't gain it, so no client can register a file as `Video`. A scan keeps a `Video` row's source. |
| `FRAMES_ROUTE` | `POST /captures/frames` in `routes/captures.py`, declared before `/{id}`, status 201. `CaptureFramesIn`: `path: str` (1 to 4096), `at: list[StrictInt \| StrictFloat \| StrictStr] \| None` (1 to 20 items), `count: StrictInt \| None` (1 to 20), `start` and `end` of the same union or `None`, `extra="forbid"`, and a `model_validator` that refuses both or neither of `at` and `count`, and `start` or `end` with `at`. A schema refusal is the fixed 422 `validation_error` `Request validation failed`. `CaptureFramesOut`: `video {path, duration_ms, width, height, fps}` and `frames [{id, path, time_ms, timecode, width, height}]`, with no image bytes. The `20`s are `FRAMES_MAX`; under D-577 B they read `10`. |
| `FRAMES_MCP` | `avkit_capture` `frames`: `z.object({action: z.literal("frames"), path: z.string().min(1).max(4096), at: z.array(timeValue).min(1).max(20).optional(), count: z.number().int().min(1).max(20).optional(), start: timeValue.optional(), end: timeValue.optional()}).strict()` with a `.refine` whose message is `frames takes either at or count; start and end go with count`, where `timeValue` is `z.union([z.number().nonnegative(), z.string().min(1).max(32)])`. It is appended after `crop` in `capture.ts`, and its row after `crop`'s in `ACTION_INDEX`. Under D-577 A it joins `ADD_TIMEOUT_MS` in `registry.ts:388-393`. Its description is `FRAMES_TEXT`, with its own four markers instead of capture's shared `desc`: `Workflow: call avkit_convert probe for the duration, then avkit_capture frames to POST /captures/frames, then image to view a frame.` `Prerequisite: a local absolute video path and FFmpeg; the video is read in place, never changed or uploaded.` `Returns: JSON with the video's duration and size and each new shot's id, path, time_ms and timecode; no image bytes.` `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.` and the body `Give at (1-20 times: seconds, or "HH:MM:SS.mmm") or count (1-20 evenly spaced frames, with optional start and end). Each frame is the first one at or after its time; a time after the last video frame but before the end returns the last frame. Frames are new shots, so image, crop and annotate work on them.` plus, under D-576 A, `A raw stream with no duration takes only at, and is slow; remuxing it with avkit_convert add (fast copy) gives it a duration.` Under D-577 B every `20` in the schema and `FRAMES_TEXT`'s `1-20` read `10`. Its accepted set is narrower than `FRAMES_ROUTE`'s in two places, so the ACs call it transport parity, not identical filters: the optional `timeValue` refuses `null`, which Pydantic reads as absent, and a negative number is refused before fetch, where REST refuses it in `TIME_PARSE`. |
| `NO_RAW_OUTPUT` | No new log line, error message or response field carries the video path, a frame path or FFmpeg's stderr, except the 201 and 200 bodies' own `path` fields, which echo what the caller asked about and the shots it now owns. `frames_from_video` logs `capture.frames` with the frame count and shot ids only; `_upsert_shot`'s existing `capture.registered` line carries the shot id and source name. |

### Pins that move

| Pin | Where | From → to | Row |
|---|---|---|---|
| Last `CaptureSource` member | `tests/unit/test_domain_capture.py:884-892` (AC-130.7) | `Crop` last → `Crop` present and directly before `Video`; the last member is checked by AC-134.1 | 1 |
| Member tuple | `tests/unit/test_domain_capture.py:18-27` (`CAPTURE_SOURCE_MEMBERS`, read at `:120-121`) | gains `"Video"` | 1 |
| Member tuple | `tests/unit/test_domain.py:298-307` | gains `"Video"` | 1 |
| Source wire list | `tests/e2e/test_api_captures.py:92-101` (`SOURCE_OUT`) | gains `"Video"` | 1 |
| Route census | `tests/e2e/test_api_openapi.py:14-90` (`ROUTE_INDEX`) and `:114` | gains `("POST", "/api/v1/conversions/probe")` after `gpu/refresh`, then `("POST", "/api/v1/captures/frames")` after `captures/requests/{id}/cancel`; 74 → 75 → 76 | 2, 4 |
| Operation count | `tests/e2e/test_api_downloads.py:372` (`ROUTE_COUNT_AFTER`) | 74 → 75 → 76, with a comment line per MEU | 2, 4 |
| Action count | `tests/e2e/test_api_downloads.py:375` (`ACTION_INDEX_AFTER`) | 71 → 72 → 73 | 2, 4 |
| Valid bodies | `tests/e2e/test_api_bodies.py:13-47` (`_valid_body`) | gains `{"path": "C:/tmp/clip.mp4"}` for probe, then `{"path": "C:/tmp/clip.mp4", "count": 3}` for frames | 2, 4 |
| Convert routes | `tests/e2e/test_api_conversions.py:42-56`, `:57` | `CONVERT_ROUTES` gains the probe row; `STATIC_BEFORE_ID` gains `"/probe"` | 2 |
| MCP action counts | `mcp-server/tests/action-index.test.ts:42`; `capture.test.ts:109`, `:885`; `convert.test.ts:57`; `m7-resource.test.ts:54`, `:72`; `audit/coverage.test.ts:33-34` | 71 → 72 → 73 | 2, 4 |
| Built-server action count | `mcp-server/tests/audit/runner-fake-backend.test.ts:77` (`summary.discovery.actions`, read from the built `dist/index.js`) | 71 → 72 → 73, with a comment line per MEU | 2, 4 |
| Per-tool counts | `capture.test.ts:121` and `convert.test.ts:74` (convert 13 → 14); `capture.test.ts:127`, `:897` (capture 11 → 12) | as shown | 2, 4 |
| Expected rows and keys | `convert.test.ts:36` (rows), `:137` (`CONVERTER_KEYS`); `capture.test.ts:186` (`CAPTURE_KEYS`), `:441-443`; `fixtures.ts:76`, `:142` (`M7_MARKERS`), `:212`, `:298` | gain the new action as each file lists actions | 2, 4 |
| Pending baseline | `mcp-server/tests/audit/coverage.test.ts:18` (`BASELINE_PENDING`) | `["avkit_capture.crop"]` → gains `"avkit_convert.probe"`, then `"avkit_capture.frames"` | 2, 4 |
| Capture shared markers | `capture.test.ts:58` (`M7`), used at `:168` (AC-38.5) and `:438-449` (AC-67.17) | unchanged: `frames` still carries the four marker words, from `FRAMES_TEXT` | — |

The `CaptureSource` pins move in row 1, because row 1 adds `Video` and the old pins would fail on that row's own check. In the Row column, 2 means rows 2a (Python) and 2b (MCP), and 4 means rows 4a and 4b: a pin in `tests/` moves in 2a or 4a, and a pin in `mcp-server/tests/` in 2b or 4b. Each Red row greps the neighbours of each count pin again (S59 RULE-1): every literal `71`, `72`, `74` or `75` next to an action or route list in `tests/`, `mcp-server/tests/` and `ui/tests/`, and every test that walks `ACTION_INDEX`, `ROUTE_INDEX` or `CaptureSource.__members__`. **Absence pins (Session 61 RULE-3):** a grep of `tests/`, `mcp-server/tests/` and `ui/tests/` for tests that assert `probe`, `frames` or `Video` are absent found none; the only `frames` hits are conversion `UNIT_LABELS` (`test_domain.py:392`, `test_domain_conversion.py:247-257`, `test_conversion_service.py:22`, `test_ffmpeg_conversion.py:484`), which are unrelated and don't move. `capture.test.ts`'s `CAPTURE_ROUTES` in `test_api_captures.py:63-74` is a subset check (`:764`) and doesn't move. `runner-fake-backend.test.ts` launches the built server, so rows 2b and 4b build the MCP server before their Red run (the Red then fails on the count, because the build has no new action yet), and rows 3 and 5 build it before the whole MCP suite. The planning grep missed this pin; plan review round 1 found it (Q9).

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The video path** goes from the request to `VIDEO_INPUT`, then to FFmpeg's argv and to the 200 or 201 body's `video.path` / `path`. It is never logged and never put in an error message. Its writers: the caller only.
- **The video's stem** goes through `import_stem` into frame names, which reach the inbox, the rows, the 201 body and the Capture page. Its writer is the caller's file name; `import_stem` keeps word characters, space and `-`, so a control character or lone surrogate never reaches a name.
- **ffprobe's stdout** becomes `MediaInfo` fields. `container`, `video_codec` and `audio_codec` reach the 200 body; they come from the file's own header, and `RUN_UTF8`'s `errors="replace"` turns undecodable bytes into U+FFFD. They are never logged.
- **ffprobe's and FFmpeg's stderr**, which name the path, are dropped: `PROBE_MAP` raises its fixed error after the `except` clause has ended, so nothing is chained, `FRAME_GRAB` discards stderr, and `END_GAP` reads stdout only.
- **A requested time** reaches error messages only as `TIMECODE` of the parsed milliseconds, never as the caller's text. A refused time's message echoes nothing.
- **The duration** reaches the past-the-end message as `TIMECODE`.
- **Frame paths** go to the 201 body and the rows. The `capture.frames` line logs ids only.

### Spec text (D3)

| File | Lines at `7b9f34d` | Change |
|---|---|---|
| `docs/build-plan/08-video-conversion.md` | after `:629` (the Tests row) | A Delivered note naming `PROBE_MAP`, `PROBE_ROUTE`, `PROBE_MCP`, `RUN_UTF8` as D-573 ruled, AC-133.1 to .9 and this plan folder, in the format of the MEU-123 note above it |
| `docs/build-plan/09-screenshot-capture.md` | after the §Video frames Tests row (`:1139`) | A Delivered note naming the mechanism ids, AC-134.1 to .17, D-575, D-576 and D-577 as ruled, the description's workflow line (D-583) and this plan folder, in the format of the Session 60 and 61 notes |

Row 6 re-reads each anchor before it writes (Session 51 RULE-3) and cites the lines as they read then. `08` is LF and `09` is CRLF.

### MEU-133 `convert-media-probe`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `POST /conversions/probe` body | `schemas/conversions.py` `ConversionProbeIn` | `path` 1 to 4096 characters; `VIDEO_INPUT` | `extra="forbid"`, fixed 422 |
| MCP `avkit_convert` `probe` | `convert.ts` | `path` 1 to 4096 | `.strict()`, refused before fetch |
| 200 body | `ConversionProbeOut` | exactly the eleven 08 fields | — |
| ffprobe JSON → `MediaInfo` | `adapter.py` `probe` (unchanged parse) | `RUN_UTF8` under D-573 A | — |

#### Acceptance Criteria

Test names start `test_ac_133_<n>_` (Python) and `AC-133.<n>` (Vitest). New Python files are LF.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-133.1 | Unit | `VIDEO_INPUT`: an absolute drive path to a file and a UNC-shaped absolute path to a file (a `tmp_path` file reached through `\\?\`) are accepted and resolved; each refusal gives its fixed message and names no part of the input. In `tests/unit/test_video_input.py`. | 08 Input | Empty, 4097 characters, `relative/clip.mp4`, `http://x/clip.mp4`, `file:///C:/clip.mp4`, `ftp:x`, a lone surrogate, `\x07`, NUL, a missing file, a directory, and a self-loop symlink with a marker name (`video file not found`, with `__cause__` and `__context__` both `None` and the marker absent from `traceback.format_exception` of it; where `os.symlink` is refused, a patched `Path.resolve` raising `RuntimeError("Symlink loop from MARKER")`): each refused with the exact message |
| AC-133.2 | Unit | `TIMECODE`: `format_timecode` of 0, 999, 1000, 3,599,999, 359,999,999; `duration_ms` of 3.0, 7200.021, 3.0005 (→ 3001, exact half up), 3.0004 (→ 3000), and `None`, NaN, inf, 0 and −1 → `None`. In `test_video_input.py`. | 08 Response | The exact-half and below-half cases |
| AC-133.3 | Unit | `PROBE_MAP` with a recording fake `MediaPort`: the eleven fields from a `MediaInfo`; `has_video` and `has_audio` from the codecs; a `MediaProbeError` whose text holds a marker becomes `the file could not be probed` with `__cause__` and `__context__` both `None`; `FFmpegNotFoundError` passes through; no job row is written and the queue is unchanged. In the new `tests/unit/test_conversion_probe.py`. | 08 Request, Errors | Probe failure text never in the raised error |
| AC-133.4 | API | `POST /conversions/probe` on the real stack (`build_services`, a fake `MediaPort` set on `services.conversion._media`): 200 with exactly the eleven keys and the fake's values; `duration_ms` and `timecode` null when the fake gives no duration; an extra key, a missing `path`, `path: ""` and a non-string `path` give the fixed 422; no conversion row exists after any call. In the new `tests/e2e/test_api_conversion_probe.py`. | 08 Request, Response | The four schema refusals |
| AC-133.5 | API | Errors: `video file not found` (422) for a missing file under a marker folder and for a self-loop symlink there, with the fake `MediaPort` recording no `probe` call; `path must be a local absolute file path` for a URL; `the file could not be probed` for a `MediaProbeError` whose text holds the marker; the masked 503 `internal_error` for `FFmpegNotFoundError`. Under Session 54 RULE-2 the stack builds `HealthService` first, and the marker is absent from every response body, the log ring (`/api/v1/health/console`), captured stdout and stderr, with a positive control that logs the marker once and finds it in the ring. | 08 Errors | Marker absence with a positive control |
| AC-133.6 | Unit | `RUN_UTF8` (D-573 A): a recording fake `subprocess.run` sees `encoding="utf-8"`, `errors="replace"`, `text=True` and `capture_output=True` on a `probe` call and on `version`'s `-version` call; invalid UTF-8 bytes in the fake's stdout don't raise. Under D-573 B this AC is withdrawn and noted in the handoff. In the new `tests/unit/test_media_adapter_frames.py`. | D-573 | Invalid bytes in stdout |
| AC-133.7 | Integration | Real FFmpeg, through `ConversionService.probe_file` with a real `FFmpegAdapter(configured_path=packaging/ffmpeg-win64/ffmpeg.exe)`: the counter clip with audio (`duration_ms` 3000, 320×240, `fps` 25, both streams), the counter clip with no audio (`has_audio` false), a raw `.h264` stream (`duration_ms` and `timecode` null, `has_video` true), and, under D-573 A, a copy named `Łodz.mp4` and a clip with a `Ł` title tag (both with `duration_ms` 3000). Each source clip's SHA-256 is the same before and after the module's calls (the video is read in place and never changed). In the new `tests/integration/test_video_real_ffmpeg.py`, which CI deselects. | 08 Tests; D-573 | The `Ł` path and tag; the raw stream's nulls |
| AC-133.8 | MCP | `PROBE_MCP`: the schema accepts `{action, path}` and refuses an extra key, an empty path and a missing path before fetch; the `ACTION_INDEX` row is after `gpu_refresh`; the call goes to `POST /conversions/probe` with body exactly `{path}` and the default timeout; the description carries the four M7 markers and `PROBE_TEXT`; transport parity: the fake backend's 200 body reaches the tool result with the same eleven keys. In `mcp-server/tests/convert.test.ts`. | 08 Request, Tests | The three refusals |
| AC-133.9 | API | OpenAPI: `POST /api/v1/conversions/probe` is in the regenerated `openapi.committed.json` with `ConversionProbeIn` and `ConversionProbeOut`; `export_openapi.py --check` passes; `/probe` is declared before `/{id}` in `routes/conversions.py`. In `tests/e2e/test_api_openapi.py`. | 08 Tests | The route-order check |

Guards: the existing `test_ffmpeg_conversion.py`, `test_ffmpeg_resolver.py`, `test_conversion_service.py`, `test_api_conversions.py` and `test_extract_real_ffmpeg.py` (the last locally only) run in row 3 because `_run` changes (Session 55 RULE-1).

#### Spec Sufficiency

| Behavior | Classification | Resolution |
|---|---|---|
| Path refusals and messages | Local Canon | 08 Input; D-571 |
| Probe failure mapping | Inferred | D-572 |
| Non-cp1252 names and tags | Human | D-573 (probe 5) |
| Response fields | Local Canon | 08 Response; D-585 |
| Timeout | Human | D-577 (probe stays at the default) |

### MEU-134 `capture-video-frames`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `POST /captures/frames` body | `schemas/captures.py` `CaptureFramesIn` | `FRAMES_ROUTE`; times through `TIME_PARSE` in the service | `extra="forbid"`, fixed 422 |
| MCP `avkit_capture` `frames` | `capture.ts` | `FRAMES_MCP` | `.strict()` and `.refine`, refused before fetch |
| 201 body | `CaptureFramesOut` | `video` and `frames` keys only | — |
| `FramePort` | `ports/capture.py` | `FRAME_PORT` | — |
| Inbox files and rows | `CaptureService` | `FRAME_NAME`, `FRAME_WRITE`, `VIDEO_SOURCE` | — |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-134.1 | Unit | `VIDEO_SOURCE` and `FRAME_PORT`: `Video` is the last `CaptureSource` member with value `"Video"`, directly after `Crop`; `"video"` isn't in `RegisterSourceWire`'s args; `FramePort` names `probe` and `grab_frame` with `grab_frame`'s keyword-only `seek` and `timeout_s`; `FFmpegAdapter` has both with matching signatures. A characterisation of row 1's names; it passes at row 4 and runs as a guard. In `test_domain_capture.py`. | 09 Source, Grab | A register body with `source: "video"` is a 422 |
| AC-134.2 | Unit | `TIME_PARSE`: `0`, `1`, `1.5`, `"75"`, `"1:15"`, `"01:02:03.5"` (→ 3,723,500), `"0.0005"` refused (four digits), `0.0005` → 1 (exact half up), `0.0004` → 0, `1.0005` → 1001, `"99:59:59.999"` → 359,999,999. In `test_video_input.py`. | 09 Times | `True`, −1, NaN, inf, `"1:60"`, `"1:2"`, `"1:00:60"`, `"a"`, `""`, `"١"` (Arabic digit), a lone surrogate, `"\x00"`, 33 characters, `"100:00:00"`, `360000`: each the fixed message, which echoes no input |
| AC-134.3 | Unit | `FRAME_TIMES`: (0, 3000, 3) → [500, 1500, 2500]; (0, 7,200,021, 20) → probe 2's list; (0, 3, 5) → [0, 1, 2] (the last midpoint's 3 is capped to 2, then duplicates collapse); the half-up case (0, 1, 2) → [0]; (2999, 3000, 2) → [2999]; an exhaustive loop over `count` 1 to 20 and spans 1 to 40 from starts 0 and 1000 finds every time in `[start, end)`; `at` duplicates collapse and sort. In `test_video_input.py`. | 09 Spacing | Duplicates, unsorted input and a midpoint that would round onto `end` |
| AC-134.4 | Unit | `FRAME_NAME`: `standup` at 725,500 → `standup-t00h12m05.500s`; 0 → `-t00h00m00.000s`; 359,999,999 → `-t99h59m59.999s`; stem `Łodz` keeps `Łodz`; stem `CON` → `import_CON`; stem `..` → `import`. In `test_video_input.py`. | 09 Name | Reserved and empty stems |
| AC-134.5 | Unit | `FRAME_CHECKS` with a recording fake `FramePort` and a temp inbox: each refusal (`video file not found`, a URL, a bad time, 21 times, `count` 0 and 21, `the file could not be probed`, `not a video: no video stream`, `time 00:00:03.000 is past the end (00:00:03.000)` for `at: [3]` on a 3,000 ms video, the same for `start: 3`, `end` 3.001 s, `start must be before end` for `start: 2, end: 1` and `start: 1, end: 1`, `NO_DURATION`'s `count` message, and `video file not found` for a self-loop symlink) runs no `grab_frame`, leaves the inbox empty and adds no row, and each refusal that comes before `FramePort.probe` in `FRAME_CHECKS`' order (`video file not found`, the URL, the self-loop symlink, the bad time, 21 times, `count` 0 and 21) records zero probes too; `end` equal to the duration is accepted, and `count: 2, start: 2.999` on the 3,000 ms video records exactly one grab, at 2,999 ms. In the new `tests/unit/test_capture_frames_service.py`. | 09 Times, Errors | Every refusal records zero grabs |
| AC-134.6 | Unit | `FRAME_WRITE` all or nothing: a fake that returns `b""` on the third of four times gives `frame grab failed at {t}` with the third time's timecode; a fake whose third answer lacks the PNG signature gives the same; a fake `_annotate.probe` raising `InboxPathError` with a marker on the second temp gives `frame grab failed at {t}` with the second time, with no marker in the error and `__context__` `None`; an `os.replace` raising `OSError` on the second temp in phase 3 gives the masked `CaptureFailedError`, and the first dest it moved is unlinked; in each case the inbox holds no `.png`, no `.avkit-tmp` and no new row afterwards, and a pre-existing shot's file and row are unchanged. In `test_capture_frames_service.py`. | 09 Writes | Partial failure leaves nothing |
| AC-134.7 | Unit | Concurrency and names: two `frames_from_video` calls for the same video and time run in two threads, with a `threading.Barrier` inside the fake `grab_frame` so both hold their temps at once; one shot is `clip-t00h00m01.000s.png` and the other `clip-t00h00m01.000s_2.png`, and neither file is overwritten (each holds its own call's bytes). A third call with an inbox file of that name, a fourth with a row of that name and no file, and a fifth with another writer's `clip-t00h00m01.000s.png.avkit-tmp` each get `_2`; the other writer's temp is left byte for byte. In `test_capture_frames_service.py`. | 09 Tests, Name | Never an overwrite |
| AC-134.8 | Unit | `FRAME_DEADLINE` with an injected clock: the fake `FramePort.probe` gets `timeout_s` equal to the time left, and so does each `grab_frame`. (a) When the clock passes `FRAMES_DEADLINE_S` before the third grab, the call fails with the third time's `frame grab failed at`, starts no third grab and writes nothing. (b) When the fake advances the clock past it during the second grab and returns a valid PNG, the call fails with the second time's message and writes nothing. (c) With the fake clock leaving 0.05 s when phase 3 starts and another thread holding `CAPTURE_FILE_LOCK` until after the call returns, the call fails with the last time's message while the lock is still held (the wait was bounded), and no shot, temp or row exists; the same with the lock held from before phase 1 gives the first time's message, starts no grab and creates no temp. (d) When a wrapper around the capture module's `os.replace` advances the clock past the deadline at the second replace, the call fails with the last time's message before the commit, and afterwards no `.png`, temp or row exists (the moved dests were unlinked and the unit of work rolled back). A recording wrapper put in place of `CAPTURE_FILE_LOCK` shows that every `acquire` the call makes passes a `timeout`. (e) The return gate, with the worker found by its name `avkit-frames` in `threading.enumerate()` and joined after each case. A fake `_annotate.probe` that sets the clock past `FRAMES_RETURN_S` and then blocks on an `Event` makes the call raise the last time's `frame grab failed at` within 2 s of real time while the worker is still blocked; after the `Event` is set and the worker joined, no `.png`, temp or row exists. The same holds for a fake unit-of-work factory whose phase 3 `__enter__` sets the clock and blocks, as an exhausted pool does. A fake commit that sets the clock past `FRAMES_RETURN_S`, sleeps 0.2 s and returns gives the call's normal result with every shot; one that sets it past `FRAMES_RETURN_S + COMMIT_WAIT_S` and blocks gives the masked `CaptureFailedError` within 2 s. A `ValidationError` the worker raises reaches the caller as the same object, with `__context__` `None`. `FRAMES_DEADLINE_S` is 100, `FRAMES_RETURN_S` 105 and `COMMIT_WAIT_S` 6 under D-577 A (D-587). In `test_capture_frames_service.py`. | D-577; D-587 | The deadline passed before a grab, during one, while waiting for either lock, and between publishing and the commit; a body stuck in a decode, a checkout or a commit |
| AC-134.9 | Unit | `FRAME_GRAB` and `END_GAP` with a recording fake `subprocess.run`: the exact argv for input and output seek, `timeout=` passed, `T` formatted exactly (1 → `0.001`, 725,500 → `725.500`); a non-zero exit and `TimeoutExpired` give `b""`; `FileNotFoundError` gives `FFmpegNotFoundError`; an empty input-seek grab runs the ffprobe packet read with `-read_intervals` `0.000%` for T=2.999 and then grabs at 2.959; an empty output-seek grab runs no ffprobe; a last packet at or after T runs no second grab. With `time.monotonic` patched in the adapter, the grab, the packet read and the retry each get `timeout=` the time left to the one deadline set on entry, and the packet read never runs without a `timeout=`; a `TimeoutExpired` on the packet read gives `b""` and no retry; no time left after the packet read starts no retry and gives `b""`. Packet stdout `1.000\nN/A\n\n2.960\n2.920\n` gives a retry at 2.959 (the largest time), and stdout of only `N/A` gives `b""` with no retry. `FFmpegAdapter.probe(file_path, timeout_s=2.5)` passes `timeout=2.5` to `subprocess.run`, and a `TimeoutExpired` gives `MediaProbeError("ffprobe timed out")`; `probe(file_path)` and `version()`'s `-version` call pass no `timeout` keyword at all. In `test_media_adapter_frames.py`. | 09 Grab; D-575 | The fallback's three branches, its timeout and its parser; the probe's timeout |
| AC-134.10 | Integration | Real FFmpeg on generated clips, each grab compared by Pillow pixel equality with a full-decode reference frame (`-vf select=eq(n\,N)`): counter clip at 0 (frame 0), 1.0 (frame 25), 1.02 (frame 26, at or after), 2.96 (frame 74, the last) and 2.999 (frame 74, `END_GAP`); the VFR clip at 1.05 (the 1.08 frame) and 2.05 (the 2.08 frame), each within one frame interval after T; the long-audio clip at 3.2 (frame 74); `at: [3.0]` on the counter clip is refused before any FFmpeg run (a recording wrapper around the real adapter counts zero `grab_frame` calls); under D-573 A only, a `Łodz.mp4` copy's frame name starts `Łodz-t` (under B that case is dropped, because the probe reads such a file as all-`None`); each source clip's SHA-256 is the same before and after the module's calls. In `test_video_real_ffmpeg.py`. | 09 Tests | The past-end refusal with zero grabs |
| AC-134.11 | Integration | `NO_DURATION` on the raw `.h264` stream: under D-576 A, `at: [1.0]` gives frame 25 by pixel equality and `count: 2` gives the fixed message; under B both are refused; under C, `at: [1.0]` gives `frame grab failed at 00:00:01.000`. In `test_video_real_ffmpeg.py`. | 09 Errors; D-576 | `count` refused |
| AC-134.12 | API | `POST /captures/frames` on the real stack with a fake `FramePort` set on `services.capture._frames`: `at` and `count` shapes give 201 with exactly `{video, frames}`, `video` with exactly its five keys and `frames` items with exactly their six; frames are in time order; the files exist in the inbox root. The fixed 422 for: both `at` and `count`, neither, `start` with `at`, 21 `at` items, an empty `at`, `count` 0, 21, `true` and `1.5`, a time `true`, `null` or an object, and an extra key. In the new `tests/e2e/test_api_capture_frames.py`. | 09 Request, Response | Each schema refusal |
| AC-134.13 | API | Errors on the real stack: `video file not found` (422) for a missing file and for a self-loop symlink under the marker folder, with no probe and no grab, and the URL message (422), past the end (422, the timecode message), `frame grab failed at {t}` (422), the masked 503 for `FFmpegNotFoundError` and for a write failure. The video sits under a marker folder and the fake's FFmpeg stderr holds the marker; under Session 54 RULE-2 the marker is absent from every error body, the log ring, captured stdout and stderr, with a positive control. In `test_api_capture_frames.py`. | 09 Errors | Marker absence with a positive control |
| AC-134.14 | API | After a `frames` call, `GET /captures` and `GET /captures/{id}` show each frame with `source` `"Video"` and its width and height; `GET /captures/{id}/image` returns its bytes; a scan of the inbox (`GET /captures` again after a new file is dropped in) keeps the frames' source `"Video"`. In `test_api_capture_frames.py`. | 09 Source, Response | Scan doesn't turn `Video` into `Scan` |
| AC-134.15 | MCP | `FRAMES_MCP`: the schema accepts both shapes and refuses before fetch: both `at` and `count`, neither, `start` with `at`, 21 times, `count` 21, a negative number, a 33-character time, an extra key. The call goes to `POST /captures/frames` with the body minus `action`, with `ADD_TIMEOUT_MS` under D-577 A and the 30 s default under B or C. `start: null` with `count` is refused before fetch (transport parity, as `FRAMES_MCP` says). The description has its own four markers, not capture's shared `Prerequisite:` line, says `at or after`, and names `avkit_convert probe` in its workflow. In `mcp-server/tests/capture.test.ts`. | 09 Request, Description | The refusals |
| AC-134.16 | MCP | Parity and audit: `ACTION_INDEX` has 73 rows with `frames` after `crop`; transport parity: the fake backend's 201 body reaches the tool result with the same keys; `BASELINE_PENDING` lists the two new actions; `AUDIT_PLAN` has an offline step for each new action (`convert.probe` on a `makeVideo` clip, `capture.frames` with `at: [0]`), and the coverage test sees every action covered. In `capture.test.ts` and `audit/coverage.test.ts`. | 09 Tests | Coverage fails if a step is missing |
| AC-134.17 | API | OpenAPI: `POST /api/v1/captures/frames` with `CaptureFramesIn` and `CaptureFramesOut` in the regenerated snapshot; 76 operations; `--check` passes; `/frames` is declared before `/{id}` in `routes/captures.py`. In `test_api_openapi.py`. | 09 Tests | The route-order check |

Under D-577 B, every `20` in AC-134.5, .12 and .15 reads `10`, every `21` reads `11`, and the description reads `1-10`.

Guards: `test_capture_service.py`, `test_api_capture_flatten.py` (both build `CaptureService` without `frames`), `test_api_capture_region_import.py`, `test_api_capture_crop.py`, `test_api_captures.py`, `test_domain_capture.py` and `test_domain.py` (Session 54 RULE-1, because `domain/enums.py` and `ports/capture.py` change) run in rows 1 and 5.

#### Spec Sufficiency

| Behavior | Classification | Resolution |
|---|---|---|
| Time grammar | Local Canon | 09 Times; D-578 |
| Seek and end gap | Research-backed, probed | 09 Grab; D-575 (probes 1, 4) |
| Files with no duration | Human | D-576 (probe 3) |
| Frame count and time limit | Human | D-577 (probe 2) |
| Error order and messages | Local Canon | 09 Errors; D-579 |
| Write and concurrency | Local Canon | 09 Writes; D-580 |
| Names | Local Canon | 09 Name; D-581 |
| Source member | Local Canon | 09 Source; D-582 |
| MCP shape and description | Local Canon | 09 Description; D-583 |
| Real-FFmpeg fixtures | Local Canon | D-584 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/services/video_input.py` | New | `VIDEO_INPUT`, `TIMECODE`, `TIME_PARSE`, `FRAME_TIMES`, `FRAME_NAME`, `VideoProbe`, `FRAMES_MAX`, `TIME_MAX_MS` |
| `packages/core/src/avkit_core/ports/capture.py` | Modify | `FRAME_PORT` |
| `packages/core/src/avkit_core/ports/media.py` | Modify | `FRAME_PORT` (D-588) |
| `packages/core/src/avkit_core/domain/enums.py` | Modify | `VIDEO_SOURCE` |
| `packages/core/src/avkit_core/services/conversion.py` | Modify | `PROBE_MAP` |
| `packages/core/src/avkit_core/services/capture.py` | Modify | `frames=` and `monotonic=` constructor keywords; `FRAME_CHECKS`, `NO_DURATION`, `FRAME_WRITE`, `FRAME_DEADLINE` |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | Modify | `RUN_UTF8`, `FRAME_PORT` (`probe`'s `timeout_s`, `_run`'s `timeout`), `FRAME_GRAB`, `END_GAP` |
| `packages/api/src/avkit_api/routes/conversions.py`, `schemas/conversions.py` | Modify | `PROBE_ROUTE` |
| `packages/api/src/avkit_api/routes/captures.py`, `schemas/captures.py` | Modify | `FRAMES_ROUTE` |
| `packages/api/src/avkit_api/wiring.py` | Modify | `frames=media` (`:217-222`) |
| `openapi.committed.json` | Regenerate | Both routes |
| `mcp-server/src/toolsets/convert.ts`, `capture.ts`, `registry.ts` | Modify | `PROBE_MCP`, `FRAMES_MCP`, the two `ACTION_INDEX` rows and the timeout list |
| `mcp-server/scripts/audit/plan.ts` | Modify | Two offline steps (AC-134.16) |
| `tests/unit/test_video_input.py`, `test_conversion_probe.py`, `test_media_adapter_frames.py`, `test_capture_frames_service.py` | New | AC-133.1 to .3, .6; AC-134.2 to .9 |
| `tests/e2e/test_api_conversion_probe.py`, `test_api_capture_frames.py` | New | AC-133.4, .5; AC-134.12 to .14 |
| `tests/integration/test_video_real_ffmpeg.py` | New | AC-133.7, AC-134.10, .11 |
| `tests/unit/test_domain_capture.py`, `test_domain.py`; `tests/e2e/test_api_captures.py`, `test_api_openapi.py`, `test_api_downloads.py`, `test_api_bodies.py`, `test_api_conversions.py` | Modify | §Pins that move; AC-134.1, AC-133.9, AC-134.17 |
| `mcp-server/tests/convert.test.ts`, `capture.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `audit/coverage.test.ts`, `audit/runner-fake-backend.test.ts` | Modify | AC-133.8, AC-134.15, .16; §Pins that move |
| `.github/workflows/ci.yml` | Modify | `--deselect tests/integration/test_video_real_ffmpeg.py` after the extract module's (`:59-67`) |
| `docs/build-plan/08-video-conversion.md`, `docs/build-plan/09-screenshot-capture.md` | Modify | §Spec text |

Line endings at `7b9f34d` (`C:/Temp/av-kit/s62-plan-probes.txt`): CRLF are `enums.py`, `ports/capture.py`, `services/capture.py`, `services/conversion.py`, `adapter.py`, `routes/conversions.py`, `routes/captures.py`, `schemas/captures.py`, `schemas/conversions.py`, `wiring.py`, `capture.ts`, `convert.ts`, `toolsets/registry.ts`, `scripts/audit/plan.ts`, the MCP test files above, `test_domain_capture.py`, `test_domain.py`, `test_api_captures.py`, `test_api_openapi.py`, `test_api_downloads.py`, `test_api_conversions.py`, `openapi.committed.json`, `09` and the grouping. LF are `test_api_bodies.py`, `ci.yml`, `08`, `meu-status.yaml`, `docs/BUILD_PLAN.md` and `meu-registry.md`. The probes receipt listed `registry.ts` under a wrong path; it is `mcp-server/src/toolsets/registry.ts` (CRLF, 630 lines). Row 0 measures every file again with Python bytes, and every row writes with `newline=""` or by byte replacement. New files are LF.

### Project files

- `docs/execution/plans/2026-11-10-video-probe-frames/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `session-gate.ps1`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, and the grouping tracker row (`:102`). If another session holds any of them dirty when row 6 runs, row 6 byte-edits only MEU-133's and MEU-134's fields and proves them with `render --check` (Session 61 RULE-5).
- `.agent/context/handoffs/2026-11-10-video-probe-frames-*.md`, `docs/execution/reflections/2026-11-10-video-probe-frames-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

Not this session's, and never opened: `docs/proposals/2026-11-10-download-logic-divergence-report.md`. Anything another session leaves dirty is named to Mat before any commit.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Contact sheet (`sheet`) | Feature | MEU-135 (Session 63) | Grouping §3 |
| Export copy | Feature | MEU-136 (Session 64) | Grouping §3 |
| The description eval | Eval | Session 64 | Grouping D-505 |
| Change detection, scene cuts | Feature | None | Design D-2 |
| A GUI for probe or frames | UI | None | Design D-5: frames are ordinary shots on the Capture page |
| `_run_with_progress`'s decoding | Bug | Raised to Mat in the handoff | D-573 |
| A URL or remote video | Feature | None | 08 and 09 Input |
| `MCP-AUDIT-BASELINE-PENDING-CROP` and the two new pending actions | Audit | The next authoritative update | D-499; `--update-baseline` needs Mat's words |
| `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | MCP | Its own session | Not this session's |
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`, `CAPTURE-EXIF-SCANNED-ORIENTATION` | Bug | Their own sessions | Recorded if seen, never fixed here |

## BUILD_PLAN.md Audit

MEU-133 is in `.agent/context/meu-status.yaml` (`:3479`, phase 8, band P2, matrix item 8.10, anchor `media-probe-residual`, `pending`) and MEU-134 at `:3505` (phase 9, matrix item 9.40, anchor `video-frames`, `pending`). Row 6 sets both `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at row 6 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s62-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s62-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Checks that D-573, D-576 and D-577 carry Mat's ruling in §Decision Log (S14). **The ruling format:** once Mat rules, the entry's `chosen` starts with the option letter, as `"A: …"`, `"B: …"` or `"C: …"`, and its `human_message_reference` becomes `"USER_EXPLICIT <date> '<Mat's words>'"`. A `chosen` that starts `Pending Mat's ruling`, or a `null` reference, is unruled. Checks the queue (S8): MEU-130 is `approved` in `meu-status.yaml`, MEU-133 and MEU-134 are `pending`, and the rc.3 release record commit `b1d174b` (`docs(release): record the 0.1.0-rc.3 tag and release`) is an ancestor of `HEAD`, which meets grouping D-503's "after the rc.3 release closes".
2. Checks the shapes this plan relies on, by name: `MediaPort.probe`, `FFmpegAdapter._run` with `text=True` and no `encoding=`, `_require_ffmpeg`, `import_stem`, `_import_dest`, `CAPTURE_FILE_LOCK`, `TMP_SUFFIX`, `_upsert_shot`, `CaptureSource.Crop` as the last member, `ADD_TIMEOUT_MS` and its selection in `registry.ts`, `BASELINE_PENDING` as `["avkit_capture.crop"]`, and the built-server count `71` in `runner-fake-backend.test.ts`; and that `video_input.py`, `FramePort`, `grab_frame`, `probe_file`, `frames_from_video`, `/probe` and `/frames` are absent. The anchors step also stops when a new file of §Files Modified already exists.
3. Creates `C:\Temp\av-kit\s62\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256; the other session's proposal, if dirty, is hashed by `Get-FileHash` and never opened.
4. Runs `uv sync --frozen --offline --all-packages`, and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair is over 1024 B and runs `ffmpeg -version` offline (S4), and that Pillow is 13.0.0.
5. Records the line endings and SHA-256 of every file in §Files Modified to `s62-anchors.txt`, which row 1 reads before it writes.
6. Captures the base Python suite to `s62-base-py.txt`, builds the MCP server (`s62-base-mcp-build.txt`) and captures the base MCP suite to `s62-base-mcp.txt`, and runs `ruff check packages/ tests/` to `s62-base-ruff.txt`. The suites' own failures are recorded, not fatal.
7. Runs the `red-check.py` and `identity.py` selftests.

The scripts are copies of Session 61's and 58's, with this plan's values:

- **`red-check.py`.** Session 61's, with `DECLARED_NEW` holding `video_input`, `require_local_video`, `format_timecode`, `duration_ms`, `parse_time`, `frame_times`, `frame_name`, `VideoProbe`, `FRAMES_MAX`, `TIME_MAX_MS`, `FramePort`, `FrameSeek`, `grab_frame`, `probe_file`, `frames_from_video`, `FRAMES_DEADLINE_S`, `FRAMES_RETURN_S`, `COMMIT_WAIT_S`, `ConversionProbeIn`, `ConversionProbeOut`, `CaptureFramesIn`, `CaptureFramesOut`, and the selftest fixtures' names. These excuse a non-required block only. Its boundary fixture is AC-134.1 against AC-134.10.
- **`identity.py`.** `PLAN` is this folder. `FFMPEG_PAIR` is bound, because the real-FFmpeg module reads it. Its selftest binds `session-gate.ps1`, the new test modules, `08`, `09`, the register's renders and the grouping.
- **`PROJECT_ARTIFACTS`.** This plan's `*.md`, the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`.

### 2. Type-only first, then Red, then Green (rows 1 to 5)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2).** `video_input.py` with every name: `require_local_video` returning `Path(text)`, `format_timecode` returning `""`, `duration_ms` and `parse_time` returning 0, `frame_times` returning `[]`, `frame_name` returning `stem`, `VideoProbe` with its fields, `FRAMES_MAX = 20`, `TIME_MAX_MS = 359_999_999`; `FrameSeek` and `FramePort`; `CaptureSource.Video`; `FFmpegAdapter.grab_frame` returning `b""`, with `FFmpegAdapter.probe`'s `timeout_s=None` and `_run`'s `timeout=None` keywords added and ignored; `ConversionService.probe_file` returning a `VideoProbe` of `None`s; `CaptureService.__init__` gaining `frames: FramePort | None = None` and `monotonic: Callable[[], float] | None = None`, and `frames_from_video` returning an empty result; `FRAMES_DEADLINE_S` at D-577's ruled value, with `FRAMES_RETURN_S` 105 and `COMMIT_WAIT_S` 6 (D-587); `wiring.py` passing `frames=media`; and the `CaptureSource` pins in §Pins that move. No route, schema or MCP change. Its check runs `test_domain_capture.py`, `test_domain.py` (Session 54 RULE-1), `test_api_captures.py`, `test_capture_service.py`, `test_api_capture_flatten.py`, `test_api_wiring.py`, `ruff` and `pyright` on the touched packages.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error, an import error, a fixture error and a required test that fails on a missing name. The Reds call row 1's stubs, whose values are wrong, or post to a route that answers 404 or 405, so each fails on a status or value assertion. The integration Reds generate their clips in a module fixture first; a clip that fails to generate is a setup failure and stops the row.
- **`--require` matches a test name up to a non-digit boundary.** Rows 2a and 2b: `AC-133.1` to `.9`, across the pytest and Vitest receipts (AC-133.6 is withdrawn under D-573 B). Rows 4a and 4b: `AC-134.2` to `.17`. AC-134.1 is a characterisation of row 1 and must pass in row 4.
- **Expectations stay immutable in Green.** No test file changes in rows 3 and 5. The count pins move in the Red rows, so they fail in the Red receipt and pass in Green.
- **The real-FFmpeg module.** Rows 2 to 5 run it explicitly; it reads only `packaging/ffmpeg-win64/` and writes only under pytest's `tmp_path`.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`: §1.
- `session-gate.ps1` (H1-2): below.

### Session gate (H1-2)

`session-gate.ps1` is Session 58's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s62-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types` (`pyright`), `py-lint` (`ruff check packages/ tests/`), `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests`, `openapi` (`export_openapi.py --check openapi.committed.json`), `mcp-types`, `mcp-build`, `mcp-tests`, `state-render`, `issues-render`, `status-canon` (`ui/tests/unit/layout-canon.test.ts` and `queue-canon.test.ts`, which read `meu-status.yaml` and `docs/BUILD_PLAN.md` directly, and row 6 changes both) |
| Runtime | `real-ffmpeg`: `pytest tests/integration/test_video_real_ffmpeg.py tests/integration/test_extract_real_ffmpeg.py` (the extract module because `_run` changes) |
| Skipped with reason | `ui-types`, `ui-lint`, the rest of `ui-tests`, `ui-build` and `ui-electron` (no `ui/` file changes; `status-canon` runs the only UI tests that read a file this session writes), `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes) |

`py-tests` excuses only ids that row 0's receipt shows failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 6 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, `ffmpeg -version` fails, or Pillow isn't 13.0.0 | Stop: a fetch is a download and needs Mat's words |
| S5 | Any network request, download or upload, including the live audit | Stop and tell Mat |
| S6 | A real-FFmpeg test is slower than 60 s, or a clip fails to generate | Stop and tell Mat with the receipt; don't raise a timeout to make it pass |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | At row 0, MEU-130 isn't `approved`, MEU-133 or MEU-134 isn't `pending`, or `b1d174b` isn't an ancestor of `HEAD` | Stop; the queue is wrong |
| S9 | A count pin outside §Pins that move fails because of a new route or action | Add it to the row with its AC, grep its neighbours, and name it in the handoff |
| S10 | A path, FFmpeg's stderr or a caller's raw time reaches a log line, an error body or the console in a way it didn't before | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |
| S11 | A row 0 shape check fails, or a new name already exists | Stop; amend this plan through the plan review before row 1 |
| S12 | A row would change 08's or 09's rule text, an AC, or an existing route's behaviour | Stop; brief Mat with a recommendation and a do-nothing option (S59 RULE-3) |
| S13 | A pixel comparison in AC-134.10 fails because FFmpeg returns a different frame than `probe13-receipt.txt` recorded | Stop and tell Mat with the frame numbers; the description's `at or after` sentence may be wrong |
| S14 | At row 0, D-573, D-576 or D-577 has no ruling from Mat in §Decision Log | Stop; ask Mat through the Human Decision Protocol |
| S15 | At row 6, `meu-status.yaml`, `meu-registry.md` or `BUILD_PLAN.md` changes any line outside MEU-133's and MEU-134's entries and rows | Stop and tell Mat |

## Decision Log

> [!WARNING]
> Mat's request and design D-1 to D-5 settle the scope, and the grouping (D-500 to D-505) placed these MEUs. D-570 to D-572, D-574, D-575 and D-578 to D-588 didn't need Mat: each is autonomous, with its alternatives in `reasoning`. D-573, D-576 and D-577 are Mat's. D-550 to D-569 are claimed (`C:/Temp/av-kit/s62-plan-dids.txt`), so this block starts at D-570.
>
> Carried and not relisted in the block: every grouping §8 row, D-500 to D-505, with stage `grouping`. Of those, D-500 to D-504 bear on this session; the reflection carries all six, because the closeout validator reads every §8 row of the declared grouping. The design's own D-1 to D-20 are a separate namespace, cited as "design D-n" in prose only. The probe (`C:/Temp/av-kit/s62-plan-decision-probe.txt`), run with this plan and the grouping as sources (Session 54 RULE-5), shows what the closeout's decision flags pull in.

```yaml
decision_log:
  - id: D-570
    stage: planning
    question: "Does Session 62 split into 62a (MEU-133) and 62b (MEU-134)?"
    resolution: autonomous
    class: two-way
    chosen: "No split. Both MEUs run in this session, MEU-133 first; the coordinator tells Mat if the session passes half its context before row 4"
    source_tag: Local Canon
    precedents:
      - "grouping :67 — split only if Session 59 hasn't closed, or if MEU-133's handoff passes about half the context"
      - "meu-status.yaml — MEU-130 approved (Session 59 closed)"
    research:
      engine: none
      sources: []
    reasoning: "The first trigger is false and the second can't be judged before execution. MEU-133 is small (one route, one MCP member, a two-keyword adapter fix), and the planning probes that would have filled a 62a are done. A split would pay a second plan review and a second OpenAPI and registry regeneration. Two-way."
    human_message_reference: null
  - id: D-571
    stage: planning
    question: "Where do path checks, timecodes and time parsing live, given that probe, frames and Session 63's sheet all need them?"
    resolution: autonomous
    class: two-way
    chosen: "A new core module services/video_input.py with VIDEO_INPUT, TIMECODE, TIME_PARSE, FRAME_TIMES and FRAME_NAME as pure functions; both services import it"
    source_tag: Local Canon
    precedents:
      - "09 :1149 — sheet's times, errors and video input follow §Video frames"
      - "services/capture.py:166 — import_stem is a module-level pure function both import and crop reuse"
    research:
      engine: none
      sources: []
    reasoning: "One module keeps the three actions' messages identical, which 09 requires of sheet. Putting the helpers in capture.py would make the conversion service import the capture service. Putting them in the domain layer would mix filesystem checks into domain code, which has none today. Two-way."
    human_message_reference: null
  - id: D-572
    stage: planning
    question: "What does a probe failure return, given that MediaProbeError isn't in DOMAIN_HTTP_MAP and carries ffprobe's stderr?"
    resolution: autonomous
    class: two-way
    chosen: "PROBE_MAP: MediaProbeError becomes ValidationError('the file could not be probed'), raised after the except clause so nothing is chained (422); FFmpegNotFoundError keeps its masked 503"
    source_tag: Local Canon
    precedents:
      - "packages/api/src/avkit_api/errors.py — an unmapped DomainError is a logged 500, and a 4xx body is str(exc)"
      - "adapter.py:421-422 — MediaProbeError(result.stderr or 'ffprobe failed'); stderr names the path"
      - "C:/Temp/av-kit/s62/probe5-receipt.txt — a missing file gives MediaProbeError"
    research:
      engine: none
      sources: []
    reasoning: "Mapping MediaProbeError itself in DOMAIN_HTTP_MAP would put ffprobe's stderr, and so the path, in a 422 body. Leaving it unmapped would log a 500 with the path. A fixed message at the service is the only form that names no path, and 422 tells the agent the file is the problem. Two-way."
    human_message_reference: null
  - id: D-573
    stage: planning
    question: "Does this session fix FFmpegAdapter._run's cp1252 decoding of ffprobe's UTF-8 output, though 08 says probe reuses MediaPort.probe as it is?"
    resolution: human
    class: two-way
    chosen: "A: RUN_UTF8 (encoding utf-8, errors replace) with real Ł path and tag tests"
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/s62/probe5-receipt.txt — Łodz.mp4 and a Ł tag give all-None MediaInfo and a reader-thread UnicodeDecodeError; CJK and emoji happened to decode"
      - "adapter.py:263-272 — text=True with no encoding"
      - "08 :623 — Reuse: calls the existing MediaPort.probe as it is"
    research:
      engine: none
      sources: []
    reasoning: "Python's text mode uses the locale code page on Windows, and ffprobe writes UTF-8 JSON, so any byte cp1252 leaves undefined (0x81, 0x8d, 0x8f, 0x90, 0x9d) breaks the read. A is two keywords and no new ffprobe code, and conversion jobs gain correct durations on such files too. B keeps 08's words exactly but leaves a silent wrong answer on a common European file name. It is Mat's because it changes existing behaviour that 08 says to reuse as it is."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'all recommendations are accpeted, proceed'"
  - id: D-574
    stage: planning
    question: "What is FramePort's shape?"
    resolution: autonomous
    class: two-way
    chosen: "FRAME_PORT: probe(file_path, *, timeout_s=None) -> MediaInfo, bounded through a new _run timeout keyword, and grab_frame(path, time_ms, *, seek, timeout_s) -> bytes; b'' means no frame; FFmpegNotFoundError is its only raise; the existing FFmpegAdapter instance implements it"
    source_tag: Local Canon
    precedents:
      - "09 :1129 — a narrow FramePort (probe, grab_frame) that the existing FFmpegAdapter instance implements"
      - "C:/Temp/av-kit/s62/probe13-receipt.txt — a pipe grab gives the PNG on stdout, and a past-the-end grab exits 0 with 0 bytes"
    research:
      engine: none
      sources: []
    reasoning: "Returning bytes keeps FFmpeg from writing into the inbox, so FRAME_WRITE owns every inbox file. b'' for every no-frame case lets the service give one fixed message, since FFmpeg's exit code doesn't separate them (a past-the-end grab exits 0). seek and timeout_s are keywords because NO_DURATION and FRAME_DEADLINE set them per call. A port that writes a file would let FFmpeg create names the service hasn't reserved. Two-way."
    human_message_reference: null
  - id: D-575
    stage: planning
    question: "What does a time between the last video frame and the container's end return, where input seek gives nothing?"
    resolution: autonomous
    class: two-way
    chosen: "END_GAP: after an empty input-seek grab, ffprobe reads the last video packet time from T − 60 s and the grab runs again just before it, both within the grab's timeout; the description says a time after the last video frame returns the last frame"
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/s62/probe13-receipt.txt — counter clip T=2.97 to 3.0 and long-audio T=2.999 to 3.49 give NO FRAME"
      - "C:/Temp/av-kit/s62/probe4-receipt.txt — the last packet of the 2 h file is found in 0.09 s from 7195 s"
      - "09 :1137 — the Tests row asks for the last frame"
    research:
      engine: none
      sources: []
    reasoning: "Without it, a valid time inside the duration fails with 'frame grab failed', and a count whose last midpoint falls in the gap fails the whole call. Moving the past-the-end check to the last video packet would refuse times the contract allows. Output seek near the end decodes the whole file. The fallback runs only on an empty grab, inside the same timeout (its packet read is its own bounded process, written when _run had no timeout: plan review round 1 F2), and is a design D-7 revision with evidence, which design D-6 to D-20 allow. Two-way."
    human_message_reference: null
  - id: D-576
    stage: planning
    question: "How do frames handle a video with no duration, where input seek returns no frame at all?"
    resolution: human
    class: two-way
    chosen: "A: output seek under the deadline, no end check, count refused"
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/s62/probe13-receipt.txt — raw.h264: duration None; input seek gives NO FRAME at every T"
      - "C:/Temp/av-kit/s62/probe4-receipt.txt, probe4b-receipt.txt — output seek 0.64 s to 4.57 s on raw 1080p H.264, 6.9 s to 76.4 s on raw 4K HEVC"
      - "09 :1135 — a file with no duration fails count, and at still works"
    research:
      engine: none
      sources: []
    reasoning: "09's Grab rule (input seek) and Errors rule (at still works) can't both hold on a raw stream, so either rule's text moves. A keeps the agent's ability to grab from security camera streams, which design §1 names, at a cost the deadline bounds. B and C are simpler but depart from 'at still works'. It is Mat's because each option changes one of 09's rules."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'all recommendations are accpeted, proceed'"
  - id: D-577
    stage: planning
    question: "Does FRAMES_MAX stay 20, and how long may a frames call run?"
    resolution: human
    class: two-way
    chosen: "A: keep FRAMES_MAX 20, the 120 s client timeout (ADD_TIMEOUT_MS), FRAMES_DEADLINE_S 100"
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/s62/probe2-receipt.txt — 20 grabs of a 2 h 4K HEVC file in 13.6 s and 13.8 s, no failure"
      - "mcp-server/src/client.ts:13-14 — ADD_TIMEOUT_MS 120000, DEFAULT_TIMEOUT_MS 30000"
      - "grouping D-504 — a plan may lower a cap from its measurement and names it at the human gate"
    research:
      engine: none
      sources: []
    reasoning: "13.8 s is under half of 30 s here, so lowering FRAMES_MAX isn't forced. A gives a slower machine four times the margin and the deadline stops writes after the client gives up. B halves each call's reach. C keeps today's timeout with a deadline that still prevents late writes. Under every option the deadline is below the client's timeout and bounds every process in the call, so no shot is published after the client gives up (plan review round 1 F2). It is Mat's because FRAMES_MAX is design D-4's human-approved number and the timeout list is a governance value."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'all recommendations are accpeted, proceed'"
  - id: D-578
    stage: planning
    question: "What exactly does a time accept?"
    resolution: autonomous
    class: two-way
    chosen: "TIME_PARSE: a non-bool finite number at least 0, rounded half-up to ms through Decimal(repr); or an ASCII-digit string of at most 32 characters in SS, M:SS or H:MM:SS form with SS and MM under 60 and up to three decimals; at most 99:59:59.999; one fixed message that echoes nothing"
    source_tag: Local Canon
    precedents:
      - "09 :1126 — seconds as a number, or SS, MM:SS or HH:MM:SS with an optional .mmm"
      - "Session 59 — exact half-up integer rounding with exact-half tests"
      - "Session 53 RULE-1 — outside text gets lone-surrogate, control-character and empty regressions"
    research:
      engine: none
      sources: []
    reasoning: "Decimal(repr) rounds what the agent wrote rather than the float's binary value, so 1.0005 is 1001 ms. ASCII digits keep str.isdigit's other scripts out. The 100 h cap keeps timecodes and names at two-digit hours and bounds an output seek. Echoing the input would put outside text in an error. Accepting fractions beyond ms in strings would add a rounding rule 09 doesn't name. Two-way."
    human_message_reference: null
  - id: D-579
    stage: planning
    question: "In what order are frames requests checked, and what does each failure return?"
    resolution: autonomous
    class: two-way
    chosen: "FRAME_CHECKS order; input, time and grab failures are 422 ValidationError with 09's fixed messages; write failures are the masked 503 CaptureFailedError; every check runs before any grab"
    source_tag: Local Canon
    precedents:
      - "09 :1135 — the Errors row's fixed messages"
      - "services/capture.py:567-601 — IMPORT_COPY maps every write failure to the fixed 503"
    research:
      engine: none
      sources: []
    reasoning: "Checking everything before the first grab is what lets 'rejected before any grab' hold and keeps a refused call from writing. A grab failure is a property of the file and time, so it is the caller's to fix (422); a write failure is av-kit's (503), masked so its OSError text never reaches the body. Two-way."
    human_message_reference: null
  - id: D-580
    stage: planning
    question: "How are frames written, given that 20 grabs can take 14 s or more and CAPTURE_FILE_LOCK serialises every capture write?"
    resolution: autonomous
    class: two-way
    chosen: "FRAME_WRITE: reserve names and create xb temps under the lock, grab and write with the lock released, then replace and register under the lock in one unit of work; all or nothing"
    source_tag: Local Canon
    precedents:
      - "09 :1131 — .avkit-tmp, then os.replace under CAPTURE_FILE_LOCK, then register; a failed grab leaves no partial shot"
      - "services/capture.py:604-626 — _import_dest treats another writer's temp as taken"
      - "Session 58 RULE-1 — temps by open('xb'); a name with a temp is taken; the plan says how the exclusive create and the tool's write fit together"
    research:
      engine: none
      sources: []
    reasoning: "Holding the lock through the grabs would block every other capture action, the scanner included, for up to the deadline. Grabbing first into memory would hold up to 20 4K PNGs at once. Creating the temps first makes their names taken for any concurrent writer, so two calls get _2 without holding the lock while FFmpeg runs, and FFmpeg writes only to a pipe. The re-check in phase 3 covers a file a person drops by hand in between. Two-way."
    human_message_reference: null
  - id: D-581
    stage: planning
    question: "How is a frame's file named?"
    resolution: autonomous
    class: two-way
    chosen: "FRAME_NAME: import_stem(video stem) + -tHHhMMmSS.mmms + .png, then _2 through _import_dest"
    source_tag: Local Canon
    precedents:
      - "09 :1132 — the video stem, -tHHhMMmSS.MMMs and .png (slots in capitals), then _2"
      - "services/capture.py:166 — import_stem"
    research:
      engine: none
      sources: []
    reasoning: "import_stem already makes outside stems safe and handles reserved names, so frames and imports agree. A new sanitiser would drift from it. Two-way."
    human_message_reference: null
  - id: D-582
    stage: planning
    question: "Where does CaptureSource.Video go, and can a client register a file as Video?"
    resolution: autonomous
    class: two-way
    chosen: "VIDEO_SOURCE: after Crop, value 'Video', not in RegisterSourceWire; AC-130.7 moves"
    source_tag: Local Canon
    precedents:
      - "09 :1133 — new CaptureSource.Video with no register wire value, added after Crop"
      - "tests/unit/test_domain_capture.py:884-892 — AC-130.7 asserts Crop is last"
    research:
      engine: none
      sources: []
    reasoning: "09 settles both. AC-130.7's last-member check becomes 'Crop directly before Video', and AC-134.1 checks Video is last, so the order guard is kept. Two-way."
    human_message_reference: null
  - id: D-583
    stage: planning
    question: "Where do the MCP members go, and what does frames' workflow line name, given that sheet doesn't exist until Session 63?"
    resolution: autonomous
    class: two-way
    chosen: "probe after gpu_refresh, frames after crop, in the schemas and ACTION_INDEX; frames has its own four markers; its workflow reads probe → frames → image, and Session 63 adds sheet"
    source_tag: Local Canon
    precedents:
      - "09 :1136 — its own markers; workflow probe → sheet → frames → image"
      - "mcp-server/src/toolsets/capture.ts:33-40 — the shared desc's Prerequisite names screen grabs and inbox files"
    research:
      engine: none
      sources: []
    reasoning: "Naming sheet before it exists would send an agent to an action the server refuses. Appending keeps every existing action's position and test. The shared capture Prerequisite doesn't fit a video path, as 09 says. The departure from 09's workflow words is temporary and Session 63's plan restores them. Two-way."
    human_message_reference: null
  - id: D-584
    stage: planning
    question: "How do the real-FFmpeg tests get clips and check frames?"
    resolution: autonomous
    class: two-way
    chosen: "tests/integration/test_video_real_ffmpeg.py generates the counter, long-audio, no-audio, VFR and raw clips with the pinned FFmpeg in a module tmp folder, compares each grab with a full-decode reference frame by Pillow pixel equality, and is deselected on CI"
    source_tag: Local Canon
    precedents:
      - "tests/integration/test_extract_real_ffmpeg.py — generated clips, pinned binaries, CI-deselected"
      - "C:/Temp/av-kit/s62/probes/probe1_3_seek_rawstream.py — the clip generators and the framemd5 ground truth"
    research:
      engine: none
      sources: []
    reasoning: "Generated clips are small and need no download. Pixel equality against a full decode proves which frame was grabbed, where comparing PNG bytes would tie the test to the encoder's settings. The 2 h file isn't generated in the suite: probe 2 is a planning measurement, not a test. Two-way."
    human_message_reference: null
  - id: D-585
    stage: planning
    question: "Where do probe's eleven response fields come from?"
    resolution: autonomous
    class: two-way
    chosen: "From MediaInfo as the adapter parses it: container is format_name, has_video and has_audio are codec presence, duration_ms is TIMECODE's half-up ms, path is the resolved input"
    source_tag: Local Canon
    precedents:
      - "08 :622 — the eleven fields"
      - "packages/core/src/avkit_core/domain/progress.py:100-114 — MediaInfo"
    research:
      engine: none
      sources: []
    reasoning: "08's Reuse rule rules out new parsing, so each field maps from an existing one. Echoing the resolved path tells the agent which file it got when it passed a relative-looking UNC or a path with dots. Two-way."
    human_message_reference: null
  - id: D-586
    stage: planning
    question: "How long may the plan-local gate's real-FFmpeg step run, and does CI run it?"
    resolution: autonomous
    class: two-way
    chosen: "The gate runs both real-FFmpeg modules locally; CI deselects the new one beside the extract module; a test slower than 60 s is S6"
    source_tag: Local Canon
    precedents:
      - ".github/workflows/ci.yml:59-67 — --deselect tests/integration/test_extract_real_ffmpeg.py"
    research:
      engine: none
      sources: []
    reasoning: "CI fetches no FFmpeg, as Session 54 found, so the module can't run there. Running it in the gate keeps it a blocking check locally. Two-way."
    human_message_reference: null
  - id: D-587
    stage: planning
    question: "How does a frames call answer before the client's 120 s timeout when the image decode or the database checkout has no bound of its own?"
    resolution: autonomous
    class: two-way
    chosen: "FRAME_DEADLINE (e): the body runs on a worker thread; the call waits up to FRAMES_RETURN_S 105, then abandons a running worker, or waits COMMIT_WAIT_S 6 more for one that has passed check (d); check (d) and the abandon share one lock, so an abandoned worker commits nothing"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/conversion.py:218 — a daemon worker thread in a core service"
      - "packages/infrastructure/src/avkit_infra/database/engine.py:78-83 — create_engine with no pool arguments, so QueuePool waits up to 30 s"
    research:
      engine: none
      sources: []
    reasoning: "Plan review round 3 F2: checks (a) to (d) stop a late commit but not a late reply. Bounding each wait instead needs a pixel cap for Pillow and an engine-wide pool_timeout that changes every route, and a lower FRAMES_DEADLINE_S would depart from Mat's D-577 A. The gate bounds the reply whatever the body waits on and keeps D-577 A's 100 s and 120 s. Its one uncertain answer is a commit still running at 111 s, masked as 503. Two-way."
    human_message_reference: null
  - id: D-588
    stage: execution
    question: "AC-8.12 pins FFmpegAdapter's MediaPort method signatures equal to MediaPort's; how does FFmpegAdapter.probe gain timeout_s without failing it?"
    resolution: autonomous
    class: two-way
    chosen: "A: MediaPort.probe gains the same defaulted keyword-only timeout_s, float or None, default None; no MediaPort caller passes it"
    source_tag: Local Canon
    precedents:
      - "tests/integration/test_filesystem_media.py:445-477 — test_ac_8_12 asserts the adapter's MediaPort signatures equal the protocol's, name, kind, annotation and default"
      - "packages/core/src/avkit_core/ports/media.py:30 — def probe(self, file_path: Path), returning MediaInfo"
    research:
      engine: none
      sources: []
    reasoning: "Found at row 1 of execution: the plan gave FFmpegAdapter.probe the keyword and missed AC-8.12's pin. Options: A, widen MediaPort.probe with the same defaulted keyword; B, relax AC-8.12 to allow extra defaulted keywords, which edits an approved MEU's test; C, a second probe method on FramePort only, which adds ffprobe code against 08:624 and Local Canon L-2; D, do nothing, which fails AC-8.12 in the gate. A keeps every route's behaviour and every AC's text. 08:624 Reuse, calls the existing MediaPort.probe as it is, is read as binding the MEU-133 call site, which stays probe(file_path) with the same ffprobe command. Ruled by the Fable subagent under Mat's standing delegation, USER_EXPLICIT 2026-11-10 'for any questions ask fable subagent and accept ruling from it' (C:/Temp/av-kit/s62-exec-authorization.txt), and disclosed to the execution review rather than a fifth plan round. Two-way."
    human_message_reference: null
```

## Research References

- `docs/build-plan/08-video-conversion.md:614-629` and `docs/build-plan/09-screenshot-capture.md:1115-1139` (the contracts).
- `_inspiration/video-stills/design.md`: §6.1 to §6.3, §6.6, §8, §11 and design D-1 to D-20.
- The grouping file: §3 (`:59-67`), §6 tracker, §8 (`:122-127`).
- Session 61's plan and scripts (`docs/execution/plans/2026-11-10-gui-capture-image-import/`), Session 58's (`2026-11-08-capture-region-import/`), Session 54's (`convert-extract-index`).

## Planning receipts

- `C:/Temp/av-kit/s62-plan-probes.txt`: line endings and SHA-256 of the target files at `7b9f34d`.
- `C:/Temp/av-kit/s62-plan-dids.txt`: the D-id and AC sweep; D-570 up, AC-133 and AC-134 are free.
- `C:/Temp/av-kit/s62/probe2-receipt.txt` (`probes/probe2_hevc_timing.py`): planning probe 2 (D-504). A 2 h 4K HEVC file (`duration 7200.021`, 11,285,707,465 B, keyframe every 250 frames) probed in 0.07 s; 20 midpoint grabs in 13.6 s and 20 pre-keyframe grabs in 13.8 s, mean 0.69 s, `failures=0`. The grabs wrote files with `-c:v png`; the pipe form `FRAME_GRAB` uses was checked separately in probe 1/3.
- `C:/Temp/av-kit/s62/probe13-receipt.txt` (`probes/probe1_3_seek_rawstream.py`): planning probes 1 and 3 (D-504). framemd5 ground truth for the counter, long-audio, no-audio, VFR and raw clips; input seek returns the first frame at or after T; the end gap; raw `.h264` has no duration and input seek returns no frame; a pipe PNG at T=1.0 is 26,846 B with the PNG signature, and at T=3.2 exits 0 with 0 B.
- `C:/Temp/av-kit/s62/probe4-receipt.txt` (`probes/probe4_end_bounds.py`) and `probe4b-receipt.txt`: durations per clip; the last video packet time without decoding (0.11 s on the counter clip, 0.09 s on the 2 h file from 7195 s); output seek cost on raw 4K HEVC and raw 1080p H.264.
- `C:/Temp/av-kit/s62/probe5-receipt.txt` (`probes/probe5_unicode_probe.py`): the real adapter on `Ł`, CJK and emoji paths and a `Ł` tag (D-573).
- `C:/Temp/av-kit/s62/probe-f1-symlink-loop.txt` (`probes/symlink_loop_probe.py`, after plan review round 1): on Python 3.12.12, `resolve()` and `resolve(strict=True)` on a self-loop symlink raise `RuntimeError`, which isn't an `OSError`, with the link's name in its text; `is_file()` returns a bool (F1).
- `C:/Temp/av-kit/s62/ffmpeg-encoders.txt`: the pinned FFmpeg is n8.1.3 with `libx264`, `libx265` and `png`.
- `C:/Temp/av-kit/s62-plan-identity-selftest.txt`, `s62-plan-redcheck-selftest.txt`: the scripts' selftests.
- `C:/Temp/av-kit/s62-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- `C:/Temp/av-kit/s62-plan-decision-probe.txt` (`probes/decision_probe.py`, which calls the validator's own `decision_sources`): the decision probe, with this plan and the grouping as sources. The plan alone is refused (HDP-18: it declares `grouping_source`). Plan and grouping give 24 decisions, D-500 to D-505 from §8 and D-570 to D-588. Adding `known-issues.yaml` without `--decision-issue` is a usage error, and with one open issue the flag is accepted and the count stays 23. Its first run refused D-581, whose precedent spelled the frame name with brace slots; that line now spells them in capitals (Session 54 RULE-5).
- Not run at plan time: any suite or build.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python and MCP suites, the OpenAPI check, the MCP build and the two render checks, in the session gate.
- **Runtime:** the real-FFmpeg modules on generated clips.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the runtime and the FFmpeg pair. The gate records it before and after, and H1-6b checks each handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
