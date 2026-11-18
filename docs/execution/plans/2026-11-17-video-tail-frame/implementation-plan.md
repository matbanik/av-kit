---
project: "2026-11-17-video-tail-frame"
date: "2026-11-17"
source: "grouping .agent/context/grouping/2026-11-17-value-triage-session-grouping.md §3 Session 93; issue VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE (triage D-1127)"
meus: ["MEU-160"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
---

# Implementation Plan: give the END_GAP packet read an end, so a grab past a clip's last frame works on a busy host

> **Project**: `2026-11-17-video-tail-frame`
> **Build Plan Section(s)**: Phase 9, `docs/build-plan/09-screenshot-capture.md` §Video tail packet read (MEU-160, matrix 9.45), registered by row 1 of this plan (D-1165). It changes the END_GAP read of §Video frames (MEU-134, D-575).
> **Status**: said to execute (USER_EXPLICIT 2026-11-17 "orchestrate the plan creation for all sessions and proceed with execution for each"). `plan_to_exec_gate: human`: that message is the execution approval once the plan review approves; the plan review was approved at round 2 (.agent/context/handoffs/2026-11-17-video-tail-frame-plan-critical-review.md). Written at `HEAD` `ecfa3f3` (not pinned: rows run on the tree that Sessions 74, 91 and 92 leave). Session 93 runs fourth in the queue (D-1133: 74, 91, 92, 93, 94).

---

## Goal

**Goal anchor:** `FFmpegAdapter._last_video_ms` asks ffprobe for the packets from `S = max(0, T - 60 s)` with an end (`-read_intervals S%+D`, D = T + 60 s, which ffprobe counts from the keyframe K at or before `S`), not from `S` with no end, so the END_GAP retry finds the clip's last video packet on a host loaded to at least 85 % as on an idle one; 1000 adapter sequences under load give zero empty or short packet reads, and five traced runs of `tests/integration/test_video_real_ffmpeg.py` under load pass with zero failures; a failure that lacks the watched signal is never counted as a pass (Session 90 RULE-3); only `adapter.py:644` and its docstring change in the product, two named unit assertions change their expected interval, and no API route, OpenAPI document, MCP tool, setting or schema changes; scripts and tests prove it, with no manual check.

**Why.**

- **`VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE`** (`.agent/context/known-issues.yaml:5454`, low, TECH-DEBT P3 since D-1127). `test_ac_134_10_counter_clip_frames_match_a_full_decode` (`tests/integration/test_video_real_ffmpeg.py:239`) and `test_ac_134_10_long_audio_past_the_last_frame` (`:273`) fail now and then with `frame grab failed at 00:00:02.999` or `00:00:03.200`, more often in a full run. It failed Session 84's gate twice and Session 82's baseline once, so each time the gate had to run again. The register's cause was a hypothesis ("Not reproduced on demand; unexplained").
- **The cause, measured at plan time.** The cause is in the product, so this session has an MEU (D-1127, D-1165). FFmpeg's `fftools/ffprobe.c` (master `3633db72`) allocates the interval array with `av_malloc_array` (`:3365`), which does not zero it. For `START%` with no end, `parse_read_interval` sets only `has_end = 0` (`:3344`) and leaves `end`, `end_is_offset` and `duration_frames` holding whatever was in memory. `read_interval_packets` then reads all three (`:1818`, `:1878`, `:1883`). When they hold garbage, the read stops after 0 or a few packets and still exits 0 with empty stderr. A read with no `-read_intervals` uses a zeroed struct (`:1952`) and is always whole. The adapter's END_GAP read (`adapter.py:636-648`) is the open form `f"{_seek_text(start)}%"` (`:644`). So `_last_packet_ms` gets `None`, or a time short of the clip's, and `grab_frame` (`:545-571`) returns `b""`. `CaptureService._frames_body` then raises `frame grab failed`.
- **The product path.** The same `grab_frame` call serves `frames_from_video` (defined at `packages/core/src/avkit_core/services/capture.py:970`; its `_frames_body` makes the `grab_frame` call; reached from `POST` captures frames at `packages/api/src/avkit_api/routes/captures.py:352`) and the contact sheet's cells (CELL_GRAB, `capture.py:1228`). So a user who grabs a frame past a video's last frame (a clip whose audio outlasts its video) can get the same failure. This is D-1127's product test, so MEU-160 is registered (D-1165).

**Grouping §3 Session 93** (grouping `:111-119`):
- Order: log the grab's ffmpeg stderr and the clip duration near the tail, reproduce, then fix.
- Gate (`:117`): if the fix is in the product, the plan registers an MEU (D-1127).
- Cloud/local: local (full Python suite under load).
- **This plan's own rule** (`NO_RETRY`, `ARGV_NAMED`): no retries, no raised timeouts or loosened tolerances, and any assertion change is named with file and line. The grouping does not set it for Session 93; Session 91's gate (grouping `:94`) is the sibling precedent.
- Calibration peer: Session 90 `test-run-reliability` (its load run).

Mat, 2026-11-16: "This should be done with framework and scripts!", so nothing here is a manual check.

**What the code and the probes show** (plan-time reads at `HEAD` `ecfa3f3`; receipts under `C:/Temp/av-kit/video-tail-frame/`):

- **The END_GAP read** (`packages/infrastructure/src/avkit_infra/media/adapter.py`, CRLF, 820 lines):
  - `END_GAP_LOOKBACK_MS = 60_000` (`:48`) and `_seek_text(ms)` (`:69-71`, three decimals, no float).
  - `grab_frame` (`:545-571`): an input seek first. If that gives no bytes, it calls `_last_video_ms` and grabs again at `last_ms - 1`.
  - `_last_video_ms` (`:622-666`) builds the ffprobe argv at `:637-649`. `-read_intervals` is at `:643` and its value at `:644`. Its own bounded `subprocess.run` gives `None` on a timeout, a non-zero exit or no packet time.
  - The docstring (`:623`) says "read from 60 s before `time_ms`".
- **No load, the adapter's own calls** (`vtf93-tail-probe.txt`, 30 each): the first grab at 2999 ms and at 3200 ms is always empty (exit 0, 0 bytes, empty stderr), as END_GAP expects. The packet read gives 2960 ms and the retry at 2959 ms gives the PNG. The stderr is empty in every case, so logging stderr alone would show nothing (D-1168).
- **Under load** (`vtf93-load-probe.txt`, 24 busy children, load 100 %): 268 sequences were good and 8 were bad (6 counter, 2 long audio). Every bad one was `packet read exit 0 last None stderr ''`. No grab failed or timed out; the slowest process took 0.719 s, against the test's 100 s budget. So the timeout is not the cause.
- **Which read fails** (`vtf93-ffprobe-probe.txt`, under load, 549 each):
  - the adapter's argv: 13 empty reads;
  - run as the adapter runs it (`text=True`): 16 empty and 2 short (1560 ms, 160 ms);
  - with no `-read_intervals`: 549 of 549 whole.
- **Which forms hold:**
  - `vtf93-interval-probe2.txt`, under load: a bounded end `+100000` and a packet count `+#100000` were whole in 337 and 338 runs, while the open form was empty or short in 10 of 337.
  - `vtf93-interval-probe3.txt`, under load, 361 each: the recommended form at T = 2999 (`0.000%+62.999`) was whole every time, and so was `0.000%+120.000`. Today's form at T = 89 999 on a 90 s clip (`29.999%`) was empty or short in 14 of 361.
  - No added load (the first 40 rounds of `vtf93-interval-probe2.txt` and `vtf93-interval-probe3.txt`): the open form failed 7 of 120 (3 and 1 in probe2, 3 in probe3), about 6 %. So the fault occurs without load too; the loaded rate is no higher (inference from these counts).
  - `vtf93-interval-probe.txt` (under load, 24 busy children) was the first form survey: the open `0.000%` was short or empty in 6 of 269, while no interval and `+#1000` were whole.
- **The end is measured from the first packet read.** That packet is the keyframe at or before `S`, not `S` itself (`ffprobe.c:1874-1880`). On a 150 s clip with one keyframe (`vtf93-gop-probe.txt`, T = 149 999), `89.999%+120.000` stopped at 119 840 ms. `89.999%+209.999` (D = T + 60 s) and the open form both reached 149 960 ms. So the read ends at the earlier of the file's end and K + T + 60 s, never before T + 60 s, while an end of `T - S + 60 s` can stop short (D-1166). For T over 60 s this is more than two minutes of packets: at T = 7 200 021 ms the end is about K + 7260 s, the file's end. In the tail case END_GAP is for, that is the same span today's open read covers.
- **The tests** (both LF):
  - `tests/unit/test_media_adapter_frames.py` (542 lines) pins the argv. `test_ac_134_9_end_gap_reads_the_last_packet_and_grabs_again` (`:270`) expects `"0.000%"` at `:289`. `test_ac_134_9_end_gap_reads_from_60_seconds_before` (`:302`) expects `"7140.021%"` at `:313`.
  - `tests/integration/test_video_real_ffmpeg.py` (542 lines) builds its clips from `CLIPS` (`:38-60`) with the pinned `packaging/ffmpeg-win64` binaries (`:29-30`, n8.1.3-27-g8dca1586f4-20261031). It compares grabs with `_reference` (`:209`), a full decode, through `_pixels` (`:219`).
- **Session 90's waits** (`tests/integration/test_tts_assets.py`, `test_youtube_adapter.py`) are not touched. This fix adds no wait and changes no timeout.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-17). The change is one argv line and its docstring in packages/infrastructure/src/avkit_infra/media/adapter.py, two unit assertions and two new tests, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern, and task-cell commands run in pwsh.
  - Receipts go under `C:/Temp/av-kit/video-tail-frame/`, named `vtf-*` (the planning receipts are `vtf93-*`).
  - Every row sets `PYTHONIOENCODING=utf-8` and `RECEIPTS_DIR=C:/Temp/av-kit`, and clears `ELECTRON_RUN_AS_NODE`. No row starts Electron.
- **Processes:** `load-run.py` and `packet-stress.py` start the busy children (Session 90's `Busy`). Each child is stopped by its own handle and then checked through a handle to its real interpreter. No row stops a process by name or path; other sessions' apps and Mat's own app run on this host.
- **Working directory:** `P:/av-kit` on `main`, with no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local (the pinned Windows FFmpeg and a loaded host; grouping §3).
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), run by the coordinator with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `vtf-plan-2026-11-17-video-tail-frame` and `vtf-execution-2026-11-17-video-tail-frame`.
  - Caps come from `.agent/review-limits.json`: plan 3, execution 6, token budgets off. This plan has no `review_limits` block.
  - Claude wrote the plan, so the reviewer is from another vendor; the fallback is Mat.
  - Each dispatch writes its own run log, and its console output goes to a separate file (Session 88 RULE-2).
- **Queue (D-1133):** Session 93 is fourth, after Sessions 74, 91 and 92, and Session 94 follows.
  - **Shared files.** Session 74 changes the TTS backend in `packages/infrastructure` and may touch `tests/integration/`. Sessions 74, 91 and 92 each write `known-issues.yaml`, `known-issues.md`, the grouping tracker, `current-focus.md` and `metrics.md`; Session 74 may also write `meu-status.yaml` and the generated MEU files.
  - **What row 0 checks because of them.** It compares the three product and test files with their plan-time SHA-256 prefixes:

    | File | Plan-time SHA-256 prefix |
    |---|---|
    | `adapter.py` | `88e1246284a3` |
    | `test_media_adapter_frames.py` | `c4fc8920b64c` |
    | `test_video_real_ffmpeg.py` | `fbfe8f040d17` |

    It also re-reads every line this plan cites, checks that MEU-160 and matrix 9.45 are still free, and pins the register hashes it binds to.
  - **A moved citation** is corrected in the handoff (Session 51 RULE-3) and is not a blocker. Only a change to the END_GAP read itself stops the session (S1).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-160 (`VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE`) | `.agent/context/handoffs/2026-11-17-video-tail-frame-MEU-160-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-17-video-tail-frame-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-17-video-tail-frame-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and copied checkers (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `baseline.ps1`, `red-check.py`, `identity.py`, `eol-check.py`, `issue-resolve.py` |
| WP-2 | Register MEU-160 (row 1) | WP-1 | shared | `meu-status.yaml`, 09 §Video tail packet read, matrix 9.45, the rendered MEU files |
| WP-3 | Log and reproduce at base (row 2) | WP-2 | shared | The stress and base load-run receipts and traces |
| WP-4 | Red, then Green (rows 3 and 4) | WP-3 | shared | The new unit and integration tests, the two named assertions, `adapter.py:644` |
| WP-5 | Acceptance under load (row 5) | WP-4 | shared | The clean stress receipt, five green load runs, the trace check |
| WP-6 | Registers, the Delivered note and the grouping row (row 6) | WP-5 | shared | The issue resolved with `meu_links`, MEU-160 `ready_for_review`, grouping row 93 |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The handoff, the review, the reflection, the next session's prompt |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.** Three decisions are briefs (§Decision Log):
> - D-1165: register MEU-160;
> - D-1166: the shape of the fix;
> - D-1169: how many runs under load count as proof.
>
> Your hand-over ('orchestrate the plan creation for all sessions and proceed with execution for each', 2026-11-17, continuing 'like we did here. But use the new HDP process.', 2026-11-15) settles them on the recommendation, and they are recorded that way. Read them if you want to overrule one before execution.
>
> There is no human check row: scripts and tests prove each step. One stop is reserved for you (D-1171, S8): a test that fails under load without the watched signal would be a second cause. It is rerun once, both results are shown to you, and the session stops; it is never counted as a pass.
>
> **What changes for you:**
>
> - A frame grab at a time past a video's last frame, which happens when the audio runs on after the video (Capture's frames and contact sheet), no longer fails now and then while the machine is busy.
> - The Python suite stops failing now and then on the two tail-frame tests, so a gate no longer has to be run twice for them.
> - The fix is one FFmpeg argument. The read that finds the clip's last frame now has an end, so FFmpeg no longer reads unset values. The end is the time you asked for plus 60 s, counted from the keyframe at or before 60 s before that time, or the file's end if that comes first. For a grab past a video's last frame that is the same data the read covers today.

## Proposed Changes

### Single-statement contracts

- **`BOUNDED_TAIL_READ` (D-1166):** `_last_video_ms` passes `-read_intervals` the value `f"{_seek_text(start)}%+{_seek_text(time_ms + END_GAP_LOOKBACK_MS)}"`. `adapter.py:644` becomes exactly `            f"{_seek_text(start)}%+{_seek_text(time_ms + END_GAP_LOOKBACK_MS)}",` (12 spaces, 80 characters plus CRLF). `start` is still `max(0, time_ms - END_GAP_LOOKBACK_MS)` (`:636`), and every other argument, the timeout and the decoding are unchanged.
  - Examples: T = 2999 gives `0.000%+62.999`; T = 89 999 gives `29.999%+149.999`; T = 7 200 021 gives `7140.021%+7260.021`.
- **`TAIL_DOC`:** the docstring (`:623-627`) keeps its first line (the read starts 60 s before `time_ms`) and gains one sentence in its body, within 100 columns: the interval has an end of `time_ms` + 60 s past the first packet read, because an open interval reads unset fields in ffprobe. It must not say the read ends 60 s after `time_ms` or name a fixed span such as two minutes; both are false when the first packet is a keyframe before the start or `time_ms` is over 60 s.
- **`TAIL_SAME_ANSWER`:** for any clip whose last video packet is at or before `T + 60 s` measured from the keyframe at or before `S`, the bounded read returns the same last packet time as a whole read. A grab past the last frame needs that packet within 60 s, which END_GAP's own lookback already assumes (D-575). The one-keyframe guard (AC-160.8) shows this holds when that keyframe is far before `S`.
- **`ARGV_NAMED` (D-1167):** two existing unit assertions change, and only their expected interval:
  - `tests/unit/test_media_adapter_frames.py:289`: `        "0.000%",` becomes `        "0.000%+62.999",`;
  - `:313`: `    assert packet[packet.index("-read_intervals") + 1] == "7140.021%"` becomes `... == "7140.021%+7260.021"`.

  No other line of an existing test changes; `diff-check.py` allows only these two replacements plus inserted lines.
- **`GRAB_TRACE` (D-1168):** the plan's pytest plugin `grab_trace.py` (loaded with `-p grab_trace`, the plan folder on `PYTHONPATH`, `AVKIT_GRAB_TRACE_LOG` set) replaces the name `subprocess` inside the adapter module only.
  - It logs each ffmpeg and ffprobe run the adapter makes: the kind, the clip, the requested time, the `-read_intervals` value, the exit code, the packet count, the last packet time, the bytes, the clip's duration from the probe, the seconds taken and the stderr.
  - It changes no call, and the test's own reference decodes are not traced.
- **`TAIL_SIGNAL`:** the watched signal is a bad END_GAP packet read. That is a `kind=packet` record that exited non-zero or timed out, read no packet time, or read a last time below the reference: the full read's last time in `packet-stress.py`, or the most common last time of the same clip and interval across the traces in `trace-check.py`.
- **`NO_RETRY`:** no retry, no wait and no timeout is added. `grab_frame`'s single END_GAP retry (D-575) is unchanged, and the 100 s budget the tests pass is unchanged.

### MEU-160 rows

1. **Register (row 1).**
   - `meu-register.py --baseline-scope PLAN/baseline-scope.json` appends MEU-160 (`capture-video-tail-packet-read`, phase 9, band P2, matrix 9.45, depends on MEU-134, `pending`) to `.agent/context/meu-status.yaml` through `tools.meu_status.model.load` and `save`, and raises the P2 band's range to MEU-160.
   - It writes the `## Residuals registered 2026-11-17` section with `### Video tail packet read` (the MEU-160 blockquote and its Rule table) before `## Named deferrals (not this phase)` in `09-screenshot-capture.md`, and the MEUs-table row after the MEU-146 row (`:1370`).
   - It writes the matrix row after `| 9.44 | MEU-146 |` (`build-priority-matrix.md:153`).
   - Then `tools/meu_status.py render` writes `meu-registry.md` and `docs/BUILD_PLAN.md`, and `render --check` passes.
   - The plan-time dry run wrote all three files in scratch (`vtf93-meu-register-dryrun.txt`): YAML 149 432 to 150 381 bytes, 09 158 475 to 160 575, matrix 25 606 to 25 752. Its diff was the entry, the range and the two rows.
   - If row 0 finds MEU-160 or 9.45 taken, the next free pair goes through `--meu` and `--matrix`, and the handoff maps it.
   - Its `--selftest` never builds on the live register (plan review R1-F1). Its positive case, the taken-matrix refusal and the moved-id case run on an unregistered fixture: the three files read from git at HEAD, or, once the registration is committed, at the parent of the commit that added the slug, with the worktree's endings (YAML LF, 09 and matrix CRLF). The live tree is checked only for its own state: unregistered files build, and registered files refuse a second registration. So the selftest passes before row 1, after it and after rows 6 and H2-2; rows 1 and 6 run it after their writes. The plan-time proof ran it on scratch copies in all four states and on the repository (`vtf93-r1-selftest-proof.txt`), and the fallback revision on MEU-159's committed slug (`vtf93-r1-fallback-proof.txt`).
2. **Log and reproduce (row 2).**
   - `packet-stress.py --expect bad --sequences 400` runs the adapter's own `grab_frame` 400 times, alternating counter at 2999 ms and long audio at 3200 ms, with one busy child per CPU at 85 % or more. It must show at least one bad sequence, and every bad sequence must carry `TAIL_SIGNAL` (AC-160.4).
   - `load-run.py --mode base --runs 1` runs the real-ffmpeg module once under load with `GRAB_TRACE`, and `trace-check.py --mode base` reads it (AC-160.6). The traces show that the clip's duration and the empty stderr are logged, every packet read uses the open form, and every failed test (if any) carries the signal.
3. **Red (row 3).** The new tests and the two named assertions are written before the adapter changes:
   - AC-160.1, six cases in the unit file;
   - AC-160.2 and AC-160.3, the two `ARGV_NAMED` lines;
   - AC-160.8, the one-keyframe guard in the integration file.

   The eight unit cases fail by `AssertionError` (`red-check.py`). AC-160.8 runs traced and must pass, or fail only with the signal, at base (`trace-check.py --mode base`).
4. **Green (row 4).** `packages/infrastructure/src/avkit_infra/media/adapter.py:644` and the docstring (`BOUNDED_TAIL_READ`, `TAIL_DOC`) are written from CRLF bytes with `newline=""`. Then the whole unit file and the whole integration module pass, `diff-check.py` passes, and the test files' hashes equal row 3's (S3).
5. **Acceptance (row 5).**
   - `packet-stress.py --expect clean --sequences 1000` (AC-160.5).
   - Then `load-run.py --mode green --runs 5` and `trace-check.py --mode green --min-packets 3` over the five receipt and trace pairs (AC-160.9, AC-160.10).
6. **Registers (row 6).** The issue is resolved with `meu_links: [MEU-160]` and its confirmed `root_cause` (D-1170), and the register is rendered. A `> **Delivered (Session 93).**` note goes under 09 §Video tail packet read (CRLF). Grouping row 93 reads `executed (Session 93)`, and MEU-160 is set to `ready_for_review` with `--plan`. The SSOT is rendered, and `eol-check.py` runs.

### Test pins

Each pin is cited by file, line and description (Session 83 RULE-1).

| Pin | What it checks | After this change |
|---|---|---|
| `tests/unit/test_media_adapter_frames.py:289`, in `test_ac_134_9_end_gap_reads_the_last_packet_and_grabs_again` (`:270`) | The END_GAP packet argv at T = 2999 | **Expected interval only (`ARGV_NAMED`, AC-160.2).** Old: `"0.000%",`. New: `"0.000%+62.999",`. Every other element and the retry at `2.959` are unchanged |
| `tests/unit/test_media_adapter_frames.py:313`, in `test_ac_134_9_end_gap_reads_from_60_seconds_before` (`:302`) | The interval's start at T = 7 200 021 | **Expected interval only (`ARGV_NAMED`, AC-160.3).** Old: `== "7140.021%"`. New: `== "7140.021%+7260.021"`. The start is the same; the end is added |
| The other `test_ac_134_9_*` tests in the unit file (`:318` on) | The largest packet time wins, `N/A` lines, the timeout and the exit codes | Unchanged; they read `_last_packet_ms` and the run's keyword arguments, not the interval |
| `tests/integration/test_video_real_ffmpeg.py:239` (`test_ac_134_10_counter_clip_frames_match_a_full_decode`) and `:273` (`test_ac_134_10_long_audio_past_the_last_frame`) | A grab at 2999 and 3200 ms equals frame 74 of a full decode | Unchanged lines. They are the issue's two failures and now pass under load (AC-160.9) |
| `test_video_real_ffmpeg.py:335` (`test_ac_134_10_every_clip_is_unchanged_after_frames`) and `:534` | The module's clips are unchanged by the grabs | Unchanged. AC-160.8 builds its own clip in its own `tmp_path`, not in `CLIPS`, so these hash sets are the same |
| `test_video_real_ffmpeg.py:447` on (`test_ac_135_14_*`, the sheet) | CELL_GRAB cells against a scaled full decode | Unchanged; their END_GAP reads are traced and checked by AC-160.9 |
| Session 90's waits (`test_tts_assets.py`, `test_youtube_adapter.py`, `WORKER_WAIT_S`) | Worker waits | Not touched; no wait is added (`NO_RETRY`) |

These are the only existing assertions this plan changes (grouping §3 Gate). `diff-check.py` fails on any other changed line of an existing test.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| The ffprobe argv of `_last_video_ms` | `packages/infrastructure/src/avkit_infra/media/adapter.py` | `-read_intervals` is `S%+D`, both written by `_seek_text` (three decimals) | Internal to the adapter; no port, route or setting carries it |
| The `grab_trace` log, one tab-separated record per line | `grab_trace.py` (plan folder) | `armed`, `run` and `call` records, defined in its docstring | Test-only; loaded only by `-p grab_trace` |

The `MediaPort` signature (`packages/core/src/avkit_core/ports/capture.py:120`), the `frames` and sheet routes, the OpenAPI document, the MCP tools, the settings and the database are unchanged (M-4 clear).

### Acceptance Criteria

- **Naming.** ACs are numbered AC-160.n, the MEU-160 family, as Session 89 numbers AC-156.n and AC-157.n.
- **Test titles.** New pytest functions start `test_ac_160_<n>_`. Parametrized ids are whole bracketed words (`[t60000]`, `[t60001]`), so `red-check.py --require` never matches one id inside another.
- **Red and guards.**
  - AC-160.1 to AC-160.3 fail by assertion at Red.
  - AC-160.8 is a guard: at Red it passes, or fails only with the signal.
  - AC-160.4 is the reproduction at base, and AC-160.6 the traced base run.
- **Checks and proofs.**
  - AC-160.5 and AC-160.9 are the proofs after the fix.
  - AC-160.7, AC-160.10, AC-160.11, AC-160.12 and AC-160.13 are checks, not test titles.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-160.1 | unit | `test_ac_160_1_end_gap_read_has_an_end` in `tests/unit/test_media_adapter_frames.py`, parametrized with these ids and values: `t1` gives `0.000%+60.001`; `t59999` gives `0.000%+119.999`; `t60000` gives `0.000%+120.000`; `t60001` gives `0.001%+120.001`; `t89999` gives `29.999%+149.999`; `t7200021` gives `7140.021%+7260.021`. Each case uses `_grab_setup` with `[_Bytes(b""), _packet("0.000\n"), _Bytes(PNG)]` and `grab_frame(video, T, seek="input", timeout_s=5.0)`. It asserts that the value after `-read_intervals` in the packet call equals the expected value. | Research-backed (`ffprobe.c:3344`, `:1878`; D-1166) | In Red each value is the open form `S%` |
| AC-160.2 | unit (named change) | `test_media_adapter_frames.py:289` expects `"0.000%+62.999"`; the rest of `test_ac_134_9_end_gap_reads_the_last_packet_and_grabs_again` is unchanged. | Local Canon (D-1167, `ARGV_NAMED`) | In Red the argv holds `"0.000%"` |
| AC-160.3 | unit (named change) | `:313` expects `"7140.021%+7260.021"`; the retry assertion at `:315` is unchanged. | Local Canon (D-1167) | In Red the value is `"7140.021%"` |
| AC-160.4 | proof (Red) | `packet-stress.py --expect bad --sequences 400` exits 0 at base, under these conditions: the median load during the run is at least 85 %; every sequence made exactly one packet read, in the open form; at least one sequence is empty or wrong; every bad sequence carries `TAIL_SIGNAL`; no busy child or interpreter is left. With exit 4 (no bad sequence), it is rerun once with `--sequences 800`; a second exit 4 is S6. | Local Canon (D-1127: reproduce before fixing; D-1168) | Exit 3, a bad sequence without the signal, is S8 |
| AC-160.5 | proof | `packet-stress.py --expect clean --sequences 1000` exits 0 after row 4. The load and the busy-process checks are as in AC-160.4; every sequence is `correct`; every packet read is in the bounded form `S%+D`; no packet read is bad. | Local Canon (D-1169) | A bad sequence or a bad read gives exit 1 (S7) |
| AC-160.6 | check (base) | `load-run.py --mode base --runs 1` exits 0: the load held and no busy process was left. `trace-check.py --mode base` exits 0 over its receipt and trace: every packet record is in the open form, and every failed test carries the signal. Exit 3 goes to AC-160.10. Row 2's log check reads the same trace: every `run` record has a `stderr=` field, and `counter.mp4` and `long_audio.mp4` each have a `kind=probe` record with a numeric `duration` and a `kind=packet` record with a numeric `t`. | Local Canon (grouping §3 order: log the stderr and the duration first) | A wrong form gives exit 1 (S2) |
| AC-160.7 | check | `diff-check.py` exits 0 against row 0's copies. `adapter.py` stays CRLF and is byte-identical outside `_last_video_ms`; inside it, the code without its docstring equals row 0's with only `:644` replaced. The unit file stays LF with the two `ARGV_NAMED` replacements and insertions only. The integration file stays LF with insertions only. Every changed path under `packages/` or `tests/` is one of these three or was dirty at row 0. | Local Canon (`BOUNDED_TAIL_READ`, `ARGV_NAMED`; this plan's rule, Session 91's gate at grouping `:94` as precedent) | Any other changed line fails |
| AC-160.8 | integration (guard) | `test_ac_160_8_one_keyframe_clip_tail_frame` in `tests/integration/test_video_real_ffmpeg.py` builds its own clip in its own `tmp_path` with `FFMPEG`: `testsrc2=size=320x240:rate=25:duration=150`, `libx264` with `-g 100000 -keyint_min 100000 -sc_threshold 0`, `yuv420p`, no audio. It is marked `integration` and calls `_assert_pinned()` first. `frames_from_video(str(clip), at=[149.999])` gives one frame with `time_ms == 149999`, whose pixels equal `_reference(clip, 3749)`. At Red it passes or fails only with the signal (traced, `trace-check.py --mode base`); after row 4 it passes. | Research-backed (`vtf93-gop-probe.txt`; `ffprobe.c:1874-1880`; D-1166) | An end measured from `S` (`T - S + 60 s`) stops at 119 840 ms and the frame differs |
| AC-160.9 | check | `load-run.py --mode green --runs 5` exits 0: all five traced runs of the module pass, the median load during them is at least 85 %, and `busy children left: 0` and `busy interpreters left: 0`. `trace-check.py --mode green --min-packets 3` exits 0 over the five pairs: no failed test, no bad packet read, every interval bounded, and at least 3 packet reads per run. | Local Canon (D-1169; Session 90 AC-5, Session 81 RULE-2) | Any failure or bad read fails it (S7) |
| AC-160.10 | check | **A failure without the watched signal (Session 90 RULE-3).** A test that fails with the signal in its trace means the fix did not hold: S7, stop, with no rerun and no retry. A test that fails without the signal (`trace-check.py` exit 3 in any mode) is listed with its trace records. The module is then run once more, alone, under the same load and in the same mode (`load-run.py --mode base` or `--mode green`, with `--runs 1 --out C:/Temp/av-kit/video-tail-frame/rule3`, traced, and `trace-check.py` over it); rows 2 and 5 do this inside their own commands. A bad sequence without the signal in `packet-stress.py` (exit 3) stops at once, since its sequences are the adapter's own path and have no test to rerun. Both results go into the handoff word for word, and the session stops for Mat (S8, D-1171). It is never counted as a pass, and the five runs are not restarted to reach five passes. `trace-check.py --selftest` holds a fixture for each case (exit 1 with the signal, exit 3 without it). | Local Canon (Session 90 RULE-3; `NO_RETRY`, this plan's rule, Session 91's gate at grouping `:94` as precedent) | The selftest fixture for exit 3 |
| AC-160.11 | check | MEU-160 is in `meu-status.yaml` (`pending` at row 1), with 09 §Video tail packet read and its row, and matrix 9.45. `meu-register.py` exits 0 bound to row 0's hashes, and `tools/meu_status.py render` and `render --check` pass. `meu-registry.md` and `docs/BUILD_PLAN.md` are only rendered. | Local Canon (D-1165; Stage A's registration of MEU-158 and MEU-159) | `meu-register.py --selftest` builds the three edits on an unregistered git fixture and refuses a second run, a taken matrix item and a CR in the YAML; its live check passes before row 1, after it and after rows 6 and H2-2 (R1-F1, `vtf93-r1-selftest-proof.txt`) |
| AC-160.12 | check | `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` is `resolved`, with `verification`, `resolution_path`, `meu_links: [MEU-160]` and the confirmed `root_cause`, and no other parsed difference (`issue-resolve.py`). `issue_triage.py render` and `render --check` pass. MEU-160 is `ready_for_review` with this plan folder. Grouping row 93 reads `executed (Session 93)` with this plan folder. The Delivered note is under 09 §Video tail packet read. | Local Canon (D-1170; Session 89 row 6) | `issue-resolve.py` refuses another key, another issue and a wrong `--expect-sha256` |
| AC-160.13 | check | `eol-check.py` exits 0: every scope path keeps its row-0 line endings (CRLF: `adapter.py`, `09-screenshot-capture.md`, `build-priority-matrix.md`, `metrics.md`, `current-focus.md`; LF: both test files, `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, `known-issues.yaml`, `known-issues.md`, the grouping). | Local Canon (Session 89 eol-check) | A bare LF in a CRLF file or a CR in an LF file fails |

### Spec Sufficiency Table

| Question | Answer | Source |
|---|---|---|
| Is the cause in the test or in the product? | The product: the adapter's END_GAP ffprobe argv | `vtf93-load-probe.txt`, `vtf93-ffprobe-probe.txt`, `ffprobe.c:3344`, `:3365`, `:1878`, `:1883` |
| Does a longer timeout or a retry help? | No: the read exits 0 in under 1 s with no packets | `vtf93-load-probe.txt` (slowest 0.719 s) |
| What end does the read take? | `T + 60 s` past the first packet read, the keyframe K at or before `S`: the read ends at the earlier of the file's end and K + T + 60 s | `vtf93-gop-probe.txt`, `vtf93-interval-probe3.txt` (D-1166) |
| Is an expectation in a test wrong? | Two unit argv pins expect the open form; they change to the bounded form and are named | D-1167 |
| What counts as proof? | 1000 clean adapter sequences and 5 of 5 traced module runs at 85 % load, with zero failures | D-1169 |

### Files Modified

| Path | Line endings | Change | Row |
|---|---|---|---|
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | CRLF | `:644` (`BOUNDED_TAIL_READ`) and the docstring at `:623` (`TAIL_DOC`) | 4 |
| `tests/unit/test_media_adapter_frames.py` | LF | `:289`, `:313` (`ARGV_NAMED`); AC-160.1 inserted after `test_ac_134_9_end_gap_reads_from_60_seconds_before` | 3 |
| `tests/integration/test_video_real_ffmpeg.py` | LF | AC-160.8 inserted after `test_ac_134_10_long_audio_past_the_last_frame` | 3 |
| `.agent/context/meu-status.yaml` | LF | MEU-160 added (row 1), then `ready_for_review` (row 6); through the tools | 1, 6 |
| `docs/build-plan/09-screenshot-capture.md` | CRLF | The residuals section and the MEUs row (row 1); the Delivered note (row 6) | 1, 6 |
| `docs/build-plan/build-priority-matrix.md` | CRLF | Row 9.45 | 1 |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | LF | Rendered only | 1, 6 |
| `.agent/context/known-issues.yaml` | LF | The issue resolved through `issue-resolve.py` | 6 |
| `.agent/context/known-issues.md` | LF | Rendered only | 6 |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | LF | Row 93 (`:165` at plan time) only | 6 |
| `.agent/context/current-focus.md`, `docs/execution/metrics.md` | CRLF | Closeout (H1-3, H2-3) | H |
| The handoff, the two reviews, the reflection | LF (new) | Closeout | H |

**Read, never changed:** `packages/core/src/avkit_core/services/capture.py` (CRLF), `packages/core/src/avkit_core/ports/capture.py`, `packages/api/src/avkit_api/routes/captures.py`, `tests/conftest.py` (CRLF), Session 90's `load-run.py` (imported by path, unchanged), `packaging/ffmpeg-win64/`.

**Project files (plan folder):** `implementation-plan.md`, `task.md`, `grab_trace.py`, `load-run.py`, `trace-check.py`, `packet-stress.py`, `diff-check.py`, `meu-register.py` (all LF, written at plan time); `baseline.ps1`, `red-check.py`, `identity.py`, `eol-check.py`, `issue-resolve.py`, `session-gate.ps1` and the `baseline*` files (written in row 0 and H1-2).

**Sibling overlap:** the plan folders `2026-11-17-e2e-pointer-flakes` (91), `2026-11-17-mcp-audit-refresh` (92) and `2026-11-17-ui-small-fixes` (94) claim no file under `packages/infrastructure/src/avkit_infra/media/` or `tests/unit/test_media_adapter_frames.py`. None claims MEU-160 or matrix 9.45; Session 94 uses MEU-158 and MEU-159, which are already registered. The shared registers go through the tools, bound to row 0's hashes and to `baseline-dirty-hashes.json`.

## Out of Scope

| Item | Why |
|---|---|
| Reporting the ffprobe bug upstream | External disclosure (M-12). The handoff names it as a follow-up for Mat |
| Other `-read_intervals` users | `grep` at plan time: `_last_video_ms` is the only one in `packages/` |
| The first grab's input seek past the last frame giving no bytes | That is END_GAP's premise (D-575), not this fault (`vtf93-tail-probe.txt`: 30 of 30, no load) |
| Changing `END_GAP_LOOKBACK_MS`, the 100 s test budget or any timeout | `NO_RETRY` (this plan's rule; Session 91's gate at grouping `:94` as precedent) |
| A full Python suite under 85 % load | D-1169: the module is what the issue names; the full suite runs at row 0 and in the gate on a quiet host (D6) |
| Session 90's waits and `slow_worker` | Delivered contracts, not touched |

## BUILD_PLAN.md Audit

`docs/BUILD_PLAN.md` and `meu-registry.md` are generated by `tools/meu_status.py render` from `meu-status.yaml` and are never hand-edited. Row 1 renders MEU-160 as pending, and row 6 renders it as `ready_for_review`. `render --check` runs after each, in H1-3 and in the gate's `state-render` step.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`, in the shape of Session 90's `2026-11-17-test-run-reliability/baseline.ps1` (the newest Python-suite baseline). It copies `red-check.py`, `identity.py`, `eol-check.py` and `issue-resolve.py` from that folder, with this plan's `PLAN`, `PROJECT_ARTIFACTS`, scope, `COPIES` and selftest bound list, `SCRATCH` at `C:/Temp/av-kit/video-tail-frame/issue-resolve`, and `RESOLVE_KEYS` set to `status`, `verification`, `resolution_path`, `meu_links` and `root_cause` (Session 89's `meu_links` plus D-1170's `root_cause`):

1. It records `baseline.sha` (`HEAD`) and `git status --porcelain --untracked-files=all` (`baseline-dirty.txt`), with the hash of each dirty path (`baseline-dirty-hashes.json`). It also records the worktree list and the host load.
2. It writes `baseline-scope.json` (each §Files Modified path and each "Read, never changed" path, with its SHA-256 or `absent`), `baseline-eol.json` and `baseline-skip-hashes.json`. The skip hashes cover every tracked or untracked, not-ignored file under `packages/` other than `adapter.py`, and under `mcp-server/`, `tools/` and `ui/`; at H1-4 none may differ, be added or be removed.
3. It copies each scope file's bytes to `C:/Temp/av-kit/video-tail-frame/baseline-copies/<path>`.
4. **The S1 and S2 binding:**
   - `adapter.py` holds `OLD_ADAPTER` (`:644` at plan time) once, `start = max(0, time_ms - END_GAP_LOOKBACK_MS)` once and `END_GAP_LOOKBACK_MS = 60_000` once.
   - The unit file holds both `ARGV_NAMED` old lines once each.
   - The integration file still has the `test_ac_134_10_*` tests at their names and no `test_ac_160_`.
   - The issue is `open`, grouping row 93 is `proposed`, and MEU-160 and 9.45 are free (or the next free pair is recorded).
   - The three file prefixes are compared with the plan-time prefixes (§Harness), and each cited line is re-read. A moved line goes into the handoff.
5. It runs the host-load wait, then the full Python suite with the D6 argv without `-x` (`vtf-base-py.txt`). Failures are recorded, not fatal; the issue's tests may fail here.
6. It runs every plan script's `--selftest`.

### 2. Red, then Green

- Row 2 reproduces at base. Row 3 writes the tests and the named assertions, and `red-check.py` reads the unit Red.
- Row 3 records the SHA-256 of both test files. Row 4 changes only `adapter.py` and checks that the test files still have those hashes (S3).

### 3. Load proofs

| Proof | Command | Exit 0 means |
|---|---|---|
| Base reproduction | `packet-stress.py --expect bad --sequences 400` | The fault shows on the adapter's own path, with the signal |
| Base module run | `load-run.py --mode base --runs 1`, then `trace-check.py --mode base` | The trace logs stderr and duration; every failure has the signal |
| Fixed path | `packet-stress.py --expect clean --sequences 1000` | 1000 correct, no bad read, bounded form |
| Fixed module | `load-run.py --mode green --runs 5`, then `trace-check.py --mode green --min-packets 3` | 5 of 5 passed at 85 % load, no bad read |

Each proof waits for the host to be quiet first (Session 81 RULE-2), starts one busy child per CPU until the load reaches 85 %, and stops each child by its own handle.

### Session gate

`session-gate.ps1` (H1-2), in the shape of `2026-11-17-test-run-reliability/session-gate.ps1`, with its `Invoke-HostLoad` threshold set to 50 %. It is fail-fast; later steps print `not_run`, and the last line is `session-gate: all steps exit 0`.

| Step | Stage | Command |
|---|---|---|
| identity-before | static | `identity.py` |
| task-contract | static | `tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task PLAN/task.md` |
| scope-paths | static | `diff-check.py` |
| line-endings | static | `eol-check.py` |
| home-path | static | `tools/check_home_path.py` |
| selftests | static | `--selftest` of `red-check.py`, `identity.py`, `eol-check.py`, `grab_trace.py`, `load-run.py`, `trace-check.py`, `packet-stress.py`, `diff-check.py`, `meu-register.py` (its positive case runs on an unregistered git fixture, so it passes with MEU-160 registered; the live tree must refuse a second registration, R1-F1) |
| py-format | static | `ruff format --check` on `adapter.py`, both test files and the plan folder's Python |
| py-lint | static | `ruff check` on the same paths |
| py-types | static | `uv run pyright packages/` |
| py-frames | targeted | `pytest -q --tb=short -p no:cacheprovider tests/unit/test_media_adapter_frames.py tests/integration/test_video_real_ffmpeg.py` |
| ui-canon | targeted | `npm --prefix ui run test -- tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts`: the only UI tests that read `meu-status.yaml`, `BUILD_PLAN.md` and the build-plan documents, which rows 1 and 6 write (a grep of `ui/tests` at plan time) |
| host-load | runtime | Session 90's host-load wait: 50 % or less before the full suite |
| py-tests | full | `uv run pytest tests/ -x --tb=short -q` (D6), excusing only ids that `vtf-base-py.txt` shows failing and that this plan does not touch |
| issues-render-check | full | `tools/issue_triage.py render --check` |
| state-render | full | `tools/meu_status.py render --check` |
| identity-after | static | `identity.py`, equal to before |
| skipped | — | The other `ui-*` steps (no file under `ui/` changes), `mcp-*` and `openapi` (no route, schema or MCP file changes); the basis is H1-4's check of `baseline-skip-hashes.json` |

## Stop Conditions

- **S1:** row 0 finds the END_GAP read itself changed: `OLD_ADAPTER` is missing or occurs more than once, or `start` or `END_GAP_LOOKBACK_MS` differs. A citation that only moved is corrected in the handoff (Session 51 RULE-3) and is not a stop.
- **S2:** a base trace shows a packet interval that is not the open form (`trace-check.py --mode base` exit 1), so the base is not the code the plan read.
- **S3:** a test file's hash changes after row 3, or `diff-check.py` finds a changed line in an existing test other than the two `ARGV_NAMED` lines (that would be M-7).
- **S4:** before each row, `git status --porcelain --untracked-files=all` may list only this plan's paths and those in `baseline-dirty.txt`. Each dirty path outside the scope must still match `baseline-dirty-hashes.json`. Each §Files Modified path that no earlier row wrote must still match `baseline-scope.json`. This binds to content, not `HEAD`. Otherwise stop and ask Mat; never commit, stash or revert another session's work.
- **S5:** a load proof exits 2 (the load never reached 85 % in 60 s, or a busy child did not start) twice in a row, or a busy child or interpreter is left.
- **S6:** `packet-stress.py --expect bad` finds no bad sequence in 400 and then in 800. The fault could not be reproduced, so the fix is unproven; stop for Mat.
- **S7:** after row 4, any bad packet read, or any test failure with the signal. The fix did not hold; stop, with no rerun and no retry.
- **S8:** any test failure without the signal (`trace-check.py` or `packet-stress.py` exit 3). The AC-160.10 handling applies, then stop for Mat (D-1171).
- **S9:** the gate's `py-tests` fails on a test that passed in `vtf-base-py.txt`.
- **S10:** a row would need to read user data (the models folder, the app database, the settings file). Stop for Mat (Session 70 RULE-2). No row here needs it.
- **S11:** `red-check.py` refuses the unit Red (a failure that is not an assertion, or a required case that passed).

## Decision Log

> [!NOTE]
> **The decisions and their M hits:**
> - **Autonomous, `mandatory: none`.** D-1167, D-1168 and D-1170 each passed the §4a list and the §4 test.
> - **Briefs, below.** D-1165 hit M-8 (a new MEU and its ACs). D-1166 hit M-5 (the fix's shape is a product fork with no canon for the end of the read). D-1169 hit M-3 (how many runs under load count as proof is a threshold).
> - **Why the briefs are in the hand-over.** Mat's hand-over covers briefs whose hits are only M-3, M-5, M-6 or M-8 (HDP §6). So the three are recorded `autonomous`, with their `mandatory:` lists kept. `open_decisions` is empty, and there is no STOP item.
>
> **The M items that stay clear:**
> - M-7: the two changed assertions are named with file, line, old and new text in §Test pins, and `diff-check.py` enforces that no other existing assertion changes.
> - M-4: no API, OpenAPI, MCP, setting or schema change.
> - M-2: no user data is read or written.
> - M-12: no upstream report is sent; that is Out of Scope.
>
> **Reserved and free ids.** D-1171 is reserved for S8, which goes to Mat. D-1172 to D-1174 are free for execution.
>
> **Decisions this plan does not restate.** The grouping's decisions (D-1131 to D-1134) and the issue's triage decision (D-1127) are not restated here. H2-2 reads them through `--decision-source` on the grouping and on `known-issues.yaml`, with `--decision-issue VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE`.
>
> **The plan-time probe (Session 90 RULE-2).** `decision_sources` ran at plan time over this plan, the grouping and `known-issues.yaml` with that issue (`vtf93-decision-probe.txt`).
> - It read D-1165 to D-1170 from this plan, D-1131 to D-1134 from grouping §8, and D-1127 from the issue.
> - Each has one stage, and no id repeats.

```yaml
decision_log:
  - id: D-1165
    stage: planning
    question: "The cause is in the product. Does this session register an MEU for it?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: register MEU-160 capture-video-tail-packet-read (phase 9, band P2, matrix 9.45, depends on MEU-134) through meu-register.py and tools/meu_status.py render, with 09 section Video tail packet read and its matrix row; the issue is resolved with meu_links MEU-160 and the MEU is set ready_for_review at row 6."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:5454 — D-1127: an MEU is registered at the plan gate only if the fix is in the product"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:117 — Session 93 gate: if the fix is in the product, the plan registers an MEU"
      - "packages/core/src/avkit_core/services/capture.py:970 and :1228 — :970 is the def frames_from_video line (its _frames_body calls grab_frame) and :1228 is the sheet cell's port.grab_frame; both reach FFmpegAdapter.grab_frame"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:166 — Stage A registered MEU-158 and MEU-159 for Session 94 the same way"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-8 because it adds an MEU and its AC family. D-1127 set the test, and the plan-time probes meet it: the faulty argv is in the adapter and the same call serves a user's frames and sheet cells, so a user grab past a clip's last frame can fail as the test does. Fixing it under the no-MEU test-debt label would hide a product change from the MEU record; registering it keeps the build plan honest at the cost of one register row. Two-way: the entry can be closed or merged."
  - id: D-1166
    stage: planning
    question: "What end does the END_GAP packet read take?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: BOUNDED_TAIL_READ. adapter.py:644 becomes the interval S%+D with S = max(0, T - 60 s) and D = T + 60 s, both through _seek_text; the docstring says so (TAIL_DOC); nothing else in the adapter changes."
    source_tag: Research-backed
    precedents:
      - "packages/infrastructure/src/avkit_infra/media/adapter.py:636-648 — the END_GAP read and its open interval"
      - "C:/Temp/av-kit/video-tail-frame/ffprobe-master.c:3344, :3365, :1818, :1878, :1883 — the open interval leaves end, end_is_offset and duration_frames unset and the read uses them"
      - "C:/Temp/av-kit/video-tail-frame/vtf93-interval-probe3.txt — 0.000%+62.999 whole in 361 of 361 runs under load; the open form short or empty in 14 of 361"
      - "C:/Temp/av-kit/video-tail-frame/vtf93-gop-probe.txt — on one keyframe, T - S + 60 s stopped at 119840 ms and T + 60 s reached 149960 ms"
      - "D-575 — END_GAP looks back 60 s from T for the last packet"
    research:
      engine: web
      sources:
        - "https://github.com/FFmpeg/FFmpeg/blob/3633db723294adc5ca8e88fe44c3df14c9300d52/fftools/ffprobe.c"
        - "https://ffmpeg.org/ffprobe.html"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-5 because the end of the read is a product choice that no canon fixes. A gives the read an end, so ffprobe sets the fields it would otherwise read unset; the read runs from the keyframe K at or before S to the earlier of the file's end and K + T + 60 s, because ffprobe counts the end from the first packet it reads (ffprobe-master.c:1873-1879). In the tail case END_GAP is for, that is the same span as today's open read, so A costs nothing more; it keeps D-575's 60 s lookback. B, a far bound such as a large +N or a packet count +#N, also held under load and in the tail case reads the same span as A; A beats B only when END_GAP fires well inside a video, where B reads on to the file's end. E, an absolute end S%E with E = T + 60 s (no +), also sets every field the read uses and would bound the span to about two minutes plus one GOP, but ffprobe intervals are raw timestamps while the adapter's -ss counts from the file's start time, so on a file whose start time is far from 0 E can fall before the first packet; it was not probed, and A's offset form avoids the question. C, dropping -read_intervals, reads the whole file from its start, slow on a long video. D, an end measured from S (T - S + 60 s), is wrong on a long GOP because ffprobe measures the end from the keyframe it reads first (gop probe). Keeping the open form keeps the flake. Two-way: one line."
  - id: D-1167
    stage: planning
    question: "Which existing assertions change, and how are they named?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "ARGV_NAMED: tests/unit/test_media_adapter_frames.py:289 expects 0.000%+62.999 and :313 expects 7140.021%+7260.021; each is named in Test pins with its old and new text, and diff-check.py refuses any other changed line in an existing test."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:94 — Session 91's gate, the sibling precedent for this plan's rule: any assertion change is named in the plan (M-7)"
      - "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md — WAITS_NAMED, Session 90's named bound-only assertion changes"
    research: { engine: none, sources: [] }
    reasoning: "The two lines pin the argv that D-1166 changes, so they must change with it; what each asserts (the interval's start, the retry time) is kept and only the added end is new. Naming them with file, line, old and new text, and checking with diff-check.py that nothing else in an existing test changed, clears M-7. Two-way."
  - id: D-1168
    stage: planning
    question: "How are the grab's stderr and the clip duration logged, and how is the fault reproduced?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "GRAB_TRACE and TAIL_SIGNAL: a plan-folder pytest plugin traces every ffmpeg and ffprobe run the adapter makes, with stderr and the clip duration, without changing any call; packet-stress.py drives the adapter's own grab_frame 400 times at base and 1000 times after the fix under 85 % load; load-run.py imports Session 90's load run unchanged and adds the plugin."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:5454 — D-1127: log the frame-grab ffmpeg stderr and the clip duration near the tail"
      - "docs/execution/plans/2026-11-17-test-run-reliability/load-run.py — the busy children, the host-load wait and the verdict"
      - "C:/Temp/av-kit/video-tail-frame/vtf93-load-probe.txt — 8 of 276 sequences bad under load, all an empty packet read"
    research: { engine: none, sources: [] }
    reasoning: "The stderr is empty in every failing case (tail and load probes), so stderr alone would explain nothing; the trace logs it with the packet read's count and last time, which is where the fault shows. A failure in the module is about 3 % per tail grab under load, too rare to prove a fix in a few module runs, so the adapter's own path is driven a thousand times; the module runs then prove the tests themselves. No product file carries test logging. Two-way."
  - id: D-1169
    stage: planning
    question: "How many runs under load, with zero failures, prove the fix, and what happens to a failure without the signal?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-3]
    chosen: "A: 1000 adapter sequences with zero bad (packet-stress clean) and 5 of 5 traced module runs passing (load-run green), both at a median load of at least 85 %, with no bad packet read in any trace; the base must first show the fault in 400 sequences (or 800 on a second try). A failure with the signal stops the session (S7). A failure without it is rerun once alone under the same load, both results are disclosed, and the session stops for Mat (S8); it never counts as a pass."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md — AC-5: three runs at 85 % load with zero failures; RULE-3 from its reflection"
      - "C:/Temp/av-kit/video-tail-frame/vtf93-load-probe.txt — base rate 8 of 276 sequences"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:94 — Session 91's gate, the sibling precedent for this plan's own NO_RETRY rule: no retries and no raised timeouts"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-3 because the counts are a threshold. At the base rate of about 3 % per sequence, 1000 clean sequences would happen by chance with probability under one in 10 to the 12th, and 400 at base miss the fault with probability 0.971^400, about 7.7e-6 (1 in 130 000). The fault occurs without load too (7 of 120 open reads in the no-load rounds of interval-probe2 and interval-probe3), so the 85 % floor keeps the gate's setting, as Session 90 ran it, rather than causing the fault; the proof rests on the code reading (every field the bounded read uses is set) plus these counts. Five module runs, against Session 90's three, check the real tests and their traces. D, the same 1000 sequences with 1 to 3 module runs, was listed and not adopted: each run makes only a few END_GAP reads, so the runs add little power, but five give at least 15 traced reads of the real tests against 3 to 9 for a few minutes more under load. B, three module runs only, proves little at a 3 % rate. C, the full Python suite under load, mixes in unrelated load-sensitive tests and adds about an hour. Keeping today's check (one quiet gate run) is how the flake slipped through. A failure without the signal could be a second cause; stopping keeps it from being read as a pass."
  - id: D-1170
    stage: planning
    question: "How is the issue closed in the register?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Resolved through issue-resolve.py, bound to row 0's register hash, with status, verification, resolution_path, meu_links [MEU-160] and root_cause, which replaces the hypothesis with the measured cause; then issue_triage.py render and render --check."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-queue-convert-fixes/issue-resolve.py — Session 89 resolve with meu_links"
      - ".agent/context/known-issues.yaml:5461 — the recorded root_cause is labelled hypothesis and unexplained"
    research: { engine: none, sources: [] }
    reasoning: "Session 89 resolved its issues with meu_links and kept the recorded cause, which was right for them. Here the recorded cause is a hypothesis that the probes disprove (the timeout and the tail seek are not the cause), so leaving it would mislead a later reader; root_cause joins the keys the script may change, and nothing else does. Two-way."
open_decisions: []
```

Expert pass (fresh context): 3 briefs. Holds: D-1165, D-1169. Changed: D-1166. Not adopted: none. Receipt: `C:/Temp/av-kit/video-tail-frame/vtf93-expert-pass.txt`.

### D-1165: The cause is in the product. Does this session register an MEU for it?

**I recommend A: register a new MEU, MEU-160, for the fix and set it ready for review at the end of this session.** The independent review then approves it. The failing read is in the code that takes a frame from a video, not only in a test. Capture's frames and its contact sheet use the same code. So the fix is a product change, and the MEU makes it visible in the build plan and the MEU list. It adds one entry, a short section in the capture build-plan document and one matrix row, all written by the repo's tools.

- B: fix it as test debt with no MEU, as Session 90 did. The product change would then have no MEU entry.
- Do nothing: no MEU, and the fix is left for a later session.

Refs: `known-issues.yaml:5454` (D-1127), grouping `:117`, `capture.py:970` (`def frames_from_video`), `:1228` (the sheet cell's `port.grab_frame`), M-8.

Expert pass: holds; two wording fixes adopted: row 6 sets MEU-160 to `ready_for_review`, not closed, and `capture.py:970` is the `def frames_from_video` line.

### D-1166: What end does the read that finds a video's last frame take?

**I recommend A: give the read an end: the time asked for plus 60 seconds, counted from where the read starts.** Today the read has no end. Because of a fault in FFmpeg's `ffprobe`, a read with no end now and then stops early on a busy machine and finds nothing, so the frame grab fails. With an end the fault can't occur: 361 of 361 reads were complete under full load, against 14 of 361 failures for today's form. The read starts at the keyframe at or before 60 s before the time, and ends at the time plus 60 s past that keyframe, or at the file's end if that comes first. For a grab past a video's last frame, which is what this read is for, that is the same data today's read covers, so it costs nothing more.

- B: an end far past the clip, such as a huge time or packet count. It works too, and for a grab past the last frame it reads the same data as A. Only when the read runs well inside a long video does it read on to the end of the file, where A stops sooner.
- C: read the whole file with no interval at all. It always works, but it is slow on a long video.
- D: an end measured from 60 s before the time. It fails on a video with few keyframes: it stopped 30 s short in the probe.
- E: a fixed end time with no offset (`S%E`, E = the time plus 60 s). It would read about two minutes plus one keyframe gap. But ffprobe's interval times are the file's raw timestamps, while the grab counts from the file's start time, so on a file whose start time is far from 0 the end can fall before the first packet. It was not tested.
- Do nothing: the grab keeps failing now and then while the machine is busy.

Refs: `packages/infrastructure/src/avkit_infra/media/adapter.py:644`, `ffprobe.c:3344`, `:1873-1879`, `vtf93-interval-probe3.txt`, `vtf93-gop-probe.txt`, D-575, M-5.

Expert pass: changed from 'reads at most about two minutes of packets': that bound holds only for a time of 60 s or less, because ffprobe counts the end from the keyframe it reads first (`ffprobe.c:1873-1879`). A's value is kept; its cost is restated (the same span as today's read in the tail case), `TAIL_DOC` no longer claims an end 60 s after the time, and option E is added.

### D-1169: How many runs under load prove the fix?

**I recommend A: 1000 frame grabs and five full runs of the video tests, all with the machine at least 85 % busy and with zero failures.** Today the read fails about 3 times in 100 under load, and about as often with no added load, so the busy machine keeps the gate's setting rather than causing the fault. A thousand clean grabs would almost never happen by luck if the fault were still there, and five runs of the real tests check them as you run them. First the same check must show the fault on today's code. If a test fails for some other reason, it is rerun once, both results are shown to you and the session stops; it is never counted as passing.

- B: three runs of the video tests only, as Session 90 did. At a 3 % rate that could pass by luck.
- D: the same 1000 grabs with only 1 to 3 runs of the video tests. Each run makes only a few of these reads, so extra runs add little, but five runs check at least 15 traced reads by the real tests for a few minutes more, so A keeps five.
- C: run the whole Python suite under load. It adds about an hour and mixes in tests that are slow for other reasons.
- Do nothing: one ordinary gate run on a quiet machine, which is how the flake got through.

Refs: Session 90 AC-5 and RULE-3, `vtf93-load-probe.txt`, `vtf93-interval-probe2.txt` and `vtf93-interval-probe3.txt` (no-load rounds), `NO_RETRY` (this plan's rule; Session 91's gate, grouping `:94`, as precedent), M-3.

Expert pass: holds; corrections adopted: the miss chance at 400 is about 7.7e-6 (1 in 130 000), the 7 of 120 no-load count is from interval-probe2 and interval-probe3, the fault occurs without load, option D (1 to 3 module runs) is listed and not adopted, and the no-retry rule is cited as this plan's own with Session 91 as precedent.

## Research References

- **FFmpeg `fftools/ffprobe.c`**, master `3633db723294adc5ca8e88fe44c3df14c9300d52`, saved as `C:/Temp/av-kit/video-tail-frame/ffprobe-master.c`:
  - `parse_read_intervals` allocates the array with `av_malloc_array` (`:3365`), which does not zero it.
  - `parse_read_interval` sets `has_end = 0` and nothing else when there is no end (`:3344`).
  - `read_interval_packets` reads `end` (`:1817`), `end_is_offset` (`:1818`, `:1878`) and `duration_frames` (`:1883`).
  - A run with no `-read_intervals` builds a zeroed interval (`:1952`).

  The pinned build is `n8.1.3-27-g8dca1586f4-20261031`. The probes measured that binary itself.
- **ffprobe `-read_intervals`** (`https://ffmpeg.org/ffprobe.html`): `INTERVAL ::= [START|+START_OFFSET][%[END|+END_OFFSET]]`. A `+` end is a duration and `+#` a packet count. The code measures the duration from the first packet read after the seek (`:1874-1880`), which is the keyframe at or before START (`vtf93-gop-probe.txt`).
- **pytest plugins by name:** `-p <module>` imports a module from `sys.path` as a plugin. An autouse fixture in it runs for every test before the module's own fixtures, and `monkeypatch` undoes its patches when the test ends.
- **`GetSystemTimes` load:** `1 - idle / (kernel + user)` between two readings (Session 90's `load-run.py`).

## Planning receipts

All under `C:/Temp/av-kit/video-tail-frame/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `vtf93-dids.txt` | Highest decision ids in use; D-1165 to D-1174 unused; one worktree at `ecfa3f3` |
| `vtf93-eol.txt` | Line endings and sizes of the scope, by Python bytes |
| `vtf93-host-load.txt` | Host load samples at plan time |
| `vtf93-tail-probe.py`, `vtf93-tail-probe.txt`, `vtf93-tail-probe-100.txt` | The adapter's grabs and packet read, no load: the first grab empty, stderr empty, the read 2960 ms |
| `vtf93-load-probe.py`, `vtf93-load-probe.txt` | 268 good and 8 bad sequences at 100 % load; every bad one an empty packet read |
| `vtf93-ffprobe-probe.py`, `vtf93-ffprobe-probe.txt` | The adapter's argv empty in 13 of 549 and 18 of 549 (as run); no interval 549 of 549 whole |
| `vtf93-interval-probe.py`, `vtf93-interval-probe.txt` | First form survey under load (24 busy children): the open `0.000%` short or empty in 6 of 269 |
| `vtf93-interval-probe2.py`, `vtf93-interval-probe2.txt` | No added load (40 rounds): the open form failing 4 of 80; under load, bounded forms whole in 337 to 338 runs and the open form failing 10 |
| `vtf93-interval-probe3.py`, `vtf93-interval-probe3.txt` | No added load (40 rounds): today's form failing 3 of 40; under load, the recommended form whole in 361 of 361 and today's form on a 90 s clip failing 14 of 361 |
| `vtf93-gop-probe.py`, `vtf93-gop-probe.txt` | One keyframe: `T - S + 60 s` short (119 840 ms), `T + 60 s` whole (149 960 ms) |
| `ffprobe-master.c`, `ffprobe-commit.json` | The FFmpeg source read for the cause |
| `vtf93-meu-help.txt`, `vtf93-meu-roundtrip.txt` | `tools/meu_status.py` has no add command; `model.load` and `save` round-trip the YAML byte for byte (149 432 bytes) |
| `vtf93-meu-register-dryrun.txt` | `meu-register.py --dry-run`: the three edits in scratch, diff limited to the entry, the range and the rows |
| `vtf93-selftest-grab_trace.txt`, `-load-run.txt`, `-trace-check.txt`, `-packet-stress.txt`, `-diff-check.txt`, `-meu-register.txt` | The plan scripts' selftests, 0 failures each |
| `vtf93-r1-selftest-proof.py`, `vtf93-r1-selftest-proof.txt` | R1-F1: `meu-register.py --selftest --live` exits 0 on scratch copies before registration, registered (`pending`), `ready_for_review` and `approved`, and on the repository; the HEAD fixture equals the worktree bytes; the live files are unchanged |
| `vtf93-r1-fallback-proof.py`, `vtf93-r1-fallback-proof.txt` | R1-F1: with a committed slug (MEU-159's), the fixture is the parent of the commit that added it, slug absent, YAML LF, 09 CRLF |
| `vtf93-ruff.txt` | `ruff format --check` and `ruff check` clean on the plan folder's Python |
| `vtf93-decision-probe.txt` | The `decision_sources` probe over this plan, the grouping and the issue |
| `vtf93-expert-pass.txt` | The HDP §5a expert pass on D-1165, D-1166 and D-1169, with the coordinator's checks |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the issue, grouping §3 Session 93 and D-1127, Session 90's load run, and the code and FFmpeg reads above | `vtf-plan-2026-11-17-video-tail-frame` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-160.1 to AC-160.13 | `vtf-execution-2026-11-17-video-tail-frame` |
