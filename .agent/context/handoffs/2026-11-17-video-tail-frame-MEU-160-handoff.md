---
date: "2026-11-18"
project: "2026-11-17-video-tail-frame"
meu: "MEU-160"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-17-video-tail-frame/implementation-plan.md"
build_plan_section: "docs/build-plan/09-screenshot-capture.md §Video tail packet read (MEU-160, matrix 9.45)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-17-mcp-audit-refresh-handoff.md"
---

# Handoff: 2026-11-17-video-tail-frame-MEU-160-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-160 `capture-video-tail-packet-read` (phase 9, band P2, matrix 9.45, depends on MEU-134), registered by row 1 (D-1165) from `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE`.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Video tail packet read.
**Predecessor**: [2026-11-17-mcp-audit-refresh-handoff.md](2026-11-17-mcp-audit-refresh-handoff.md), Session 92, committed as `8280586`. Session 93 is the third session of the 2026-11-17 value triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md`), run from `9c655bd`.

- **The fix (`BOUNDED_TAIL_READ`, `TAIL_DOC`, D-1166).** `FFmpegAdapter._last_video_ms` (`packages/infrastructure/src/avkit_infra/media/adapter.py`) now gives the END_GAP packet read an end. `:646` (row-0 `:644`) reads `            f"{_seek_text(start)}%+{_seek_text(time_ms + END_GAP_LOOKBACK_MS)}",`: the interval starts at `S = max(0, T - 60 s)` (unchanged) and runs for `T + 60 s`, which ffprobe counts from the first packet it reads. The docstring gains one sentence: the interval has an end of `time_ms` + 60 s past the first packet read, because an open interval reads unset fields in ffprobe. The start, the lookback, the single retry, the timeout and the decoding are unchanged (`NO_RETRY`, `TAIL_SAME_ANSWER`).
- **The cause, measured.** With the open `START%` interval, FFmpeg's `fftools/ffprobe.c` (master `3633db72`) leaves `end`, `end_is_offset` and `duration_frames` unset (`parse_read_interval` sets only `has_end`, `:3344`, on memory from `av_malloc_array`, `:3365`) and `read_interval_packets` reads them (`:1878`, `:1883`). So the read sometimes stopped after 0 or a few packets with exit 0 and empty stderr, `_last_packet_ms` got no time or a short one, and the grab past the last frame came back empty. The timeout and the tail seek are not the cause.
- **Tests (`ARGV_NAMED`, D-1167).** Two existing unit assertions change their expected interval only (Changed Files). A new parametrized unit test pins the interval at six times (AC-160.1), and a new integration guard grabs the tail of a one-keyframe 150 s clip (AC-160.8).
- **Proofs under load (`GRAB_TRACE`, `TAIL_SIGNAL`, D-1168, D-1169).** Row 2 reproduced the fault on the unchanged adapter; row 5 ran 1000 adapter sequences and five traced runs of the real-FFmpeg module under load after the fix.
- **Records (D-1165, D-1170).** MEU-160 is registered (09 §Video tail packet read, its MEUs row, matrix 9.45) and is `ready_for_review` with this plan folder; the issue is `resolved` with `meu_links: [MEU-160]` and the measured `root_cause`; 09 carries the `Delivered (Session 93)` note; grouping row 93 reads `executed (Session 93)`.

**What Mat sees.** A frame grab or a contact-sheet cell at a time past a video's last frame (a clip whose audio outlasts its video) no longer fails now and then with `frame grab failed`; it returns the last frame, as it always did when the read was whole. The two real-FFmpeg tests that failed Session 84's and Session 82's gates (`tests/integration/test_video_real_ffmpeg.py:239` and `:273`) passed in every traced run under load. Nothing else changes: no route, OpenAPI document, MCP tool, setting or schema.

**Edges.** A grab past the last frame needs the last video packet within 60 s of `T`, measured from the keyframe at or before `S`, which END_GAP's own 60 s lookback already assumes (D-575). When END_GAP fires well inside a long video, the read is bounded at about `K + T + 60 s` rather than reading to the file's end; in the tail case it covers the same span the open read did (D-1166).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-17-video-tail-frame/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-17 ("orchestrate the plan creation for all sessions and proceed with execution for each"), `plan_to_exec_gate: human`; the plan review approved (`.agent/context/handoffs/2026-11-17-video-tail-frame-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `video-tail-frame` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-160.1 | unit | `-read_intervals` in the END_GAP packet call is `S%+D` at T = 1, 59 999, 60 000, 60 001, 89 999 and 7 200 021 ms (`0.000%+60.001`, `0.000%+119.999`, `0.000%+120.000`, `0.001%+120.001`, `29.999%+149.999`, `7140.021%+7260.021`) | Research-backed (`ffprobe.c:3344`, `:1878`; D-1166) | `tests/unit/test_media_adapter_frames.py:330` (decorator `:318`; ids `t1` to `t7200021`) | ✅ |
| AC-160.2 | unit (named change) | `:289` expects `"0.000%+62.999"`; the rest of the test is unchanged | Local Canon (D-1167, `ARGV_NAMED`) | `tests/unit/test_media_adapter_frames.py:272` | ✅ |
| AC-160.3 | unit (named change) | `:313` expects `"7140.021%+7260.021"`; the retry assertion is unchanged | Local Canon (D-1167) | `tests/unit/test_media_adapter_frames.py:304` | ✅ |
| AC-160.4 | proof (Red) | `packet-stress.py --expect bad --sequences 400` at base: at least one bad sequence, every one with `TAIL_SIGNAL`, median load at least 85 %, one open-form packet read per sequence, nothing left | Local Canon (D-1127, D-1168) | row 2 `vtf-stress-bad.txt` | ✅ 5 bad in 400 on the first run; the 800-sequence rerun was not needed |
| AC-160.5 | proof | `packet-stress.py --expect clean --sequences 1000` after row 4: every sequence correct, every packet read bounded, no bad read | Local Canon (D-1169) | row 5 `vtf-stress-clean.txt` | ✅ 1000 of 1000 |
| AC-160.6 | check (base) | `load-run.py --mode base --runs 1` and `trace-check.py --mode base`: every packet record in the open form, every failed test with the signal; the log check finds `stderr=` on every `run` record and a numeric probe duration and packet time per clip | Local Canon (grouping §3 order) | row 2 `vtf-load-base.txt`, `vtf-trace-check-base.txt`, `vtf-trace-log-check.txt` | ✅ |
| AC-160.7 | check | `diff-check.py`: `adapter.py` CRLF and byte-identical outside `_last_video_ms`, whose code equals row 0's but for the one line; the unit file has the two `ARGV_NAMED` replacements and insertions only; the integration file insertions only; no other changed path under `packages/` or `tests/` | Local Canon (`BOUNDED_TAIL_READ`, `ARGV_NAMED`) | row 4 `vtf-diff-check.txt`; gate `scope-paths` | ✅ |
| AC-160.8 | integration (guard) | A one-keyframe 150 s clip at 25 fps: `frames_from_video(at=[149.999])` gives one frame at 149 999 ms whose pixels equal frame 3749 of a full decode; passes at Red (traced) and after row 4 | Research-backed (`vtf93-gop-probe.txt`; `ffprobe.c:1874-1880`; D-1166) | `tests/integration/test_video_real_ffmpeg.py:285` | ✅ |
| AC-160.9 | check | `load-run.py --mode green --runs 5`: five traced module runs pass at median load at least 85 %, nothing left; `trace-check.py --mode green --min-packets 3`: no failed test, no bad read, every interval bounded | Local Canon (D-1169) | row 5 `vtf-load-green.txt`, `vtf-trace-check-green.txt` | ✅ 5 of 5 |
| AC-160.10 | check | A failure without the signal is never a pass: it is listed, rerun once alone under the same load (`rule3/`) and stops the session (S8) | Local Canon (Session 90 RULE-3; D-1169) | rows 2 and 5 (`trace-check.py` exit 3 branch) | ✅ not triggered: no test failed in any traced run, so no `rule3/` run |
| AC-160.11 | check | MEU-160 in `meu-status.yaml`, 09 §Video tail packet read and its row, matrix 9.45; `meu-register.py` bound to row 0's hashes; renders pass; `meu-register.py --selftest` passes after rows 1 and 6 | Local Canon (D-1165) | row 1 `vtf-meu-register.txt`; row 6 `vtf-meu-register-selftest-6.txt`; gate `meu-register-selftest`, `state-render` | ✅ |
| AC-160.12 | check | The issue `resolved` with `verification`, `resolution_path`, `meu_links: [MEU-160]` and the measured `root_cause`, no other parsed difference; renders pass; MEU-160 `ready_for_review` with this plan; grouping row 93; the Delivered note | Local Canon (D-1170) | row 6 `vtf-issue-resolve.txt`, `vtf-row6-check.txt`; gate `issues-render-check` | ✅ |
| AC-160.13 | check | `eol-check.py`: every scope path keeps its row-0 line endings | Local Canon (Session 89 eol-check) | row 6 `vtf-eol-check.txt`; gate `line-endings` | ✅ |
| END_GAP unit tests (cross-ref) | guard | `tests/unit/test_media_adapter_frames.py:202` to `:455` other than the two `ARGV_NAMED` tests: the grab argv (`:202`, `:226`), a failed grab (`:251`, `:260`), the largest packet time (`:341`), no usable earlier packet or a failed packet read means no retry (`:360`, `:376`), no packet read after an empty output grab (`:387`), the time left per process and the timeouts (`:396` to `:455`); unchanged lines that read `_last_packet_ms` and the run's keyword arguments, not the interval | Local Canon (§Test pins) | row 4 `vtf-green.txt`; gate `py-frames` | ✅ |
| Real-FFmpeg frames (cross-ref) | guard | `tests/integration/test_video_real_ffmpeg.py:239` (counter clip frames match a full decode) and `:273` (long audio past the last frame), the issue's two failures; `:356` (every clip unchanged after frames): unchanged lines | Local Canon (§Test pins) | row 4 `vtf-green.txt`; row 5 five traced runs; gate `py-frames` | ✅ |
| Cited, not this plan's (cross-ref) | reference | The plan names Session 90's AC-5 (three runs at 85 % load with zero failures, `docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md`) as the precedent for AC-160.9, and Session 89's AC-156 and AC-157 families as the precedent for the AC-160.n numbering (plan §Naming). They are not criteria of this session | Local Canon (plan `:213`, `:454`, `:511`) | none: precedents only | n/a: not this plan's |
| Real-FFmpeg sheet (cross-ref) | guard | `tests/integration/test_video_real_ffmpeg.py:468` (counter sheet cells match a scaled full decode) to `:555` (every clip unchanged after sheets): CELL_GRAB cells, whose END_GAP reads are traced in row 5; unchanged lines | Local Canon (§Test pins) | row 5 five traced runs; gate `py-frames` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-160.1 | `E   AssertionError: assert '0.000%' == '0.000%+60.001'` and the five like it (`vtf-red-unit.txt`, `8 failed, 30 passed in 0.27s`) | Row 4: `60 passed, 16 warnings in 9.22s` (`vtf-green.txt`) | `tests/unit/test_media_adapter_frames.py:330` |
| AC-160.2 | the list compare of the packet argv at `:289` failed (`vtf-red-unit.txt`) | Row 4: `60 passed, 16 warnings in 9.22s` (`vtf-green.txt`) | `tests/unit/test_media_adapter_frames.py:272` |
| AC-160.3 | `E   AssertionError: assert '7140.021%' == '7140.021%+7260.021'` (`vtf-red-unit.txt`) | Row 4: `60 passed, 16 warnings in 9.22s` (`vtf-green.txt`) | `tests/unit/test_media_adapter_frames.py:304` |

AC-160.8 passed at Red and is a guard; AC-160.4 to AC-160.6 and AC-160.9 are proofs and checks; AC-160.7 and AC-160.10 to AC-160.13 are checks.

- **Row 0 baseline** (`vtf-baseline.txt`): `baseline: all steps exit 0`, `eol-check: 18 scope path(s), 0 problem(s)`, `baseline-scope.json 25 paths; 3 absent`, 8 foreign dirty paths recorded in `baseline-dirty-hashes.json` and never touched. Python suite `3112 passed, 37 warnings in 288.41s (0:04:48)` (`vtf-base-py.txt`).
- **Moved citations (Session 51 RULE-3).** Row 0 found the plan's citations moved (`vtf-baseline.txt`): `test_media_adapter_frames.py:270` `def test_ac_134_9_end_gap_reads_the_last_packet_and_grabs_again(` is at `:272`; `:302` `def test_ac_134_9_end_gap_reads_from_60_seconds_before(` is at `:304`; `build-priority-matrix.md:153` `| 9.44 | MEU-146 |` is at `:154`; the issue in `known-issues.yaml` is at `:5458`, not `:5454`, so its `root_cause` was at `:5464`, not `:5461`. The asserted lines `:289` and `:313` were where the plan cites them. After row 4, `adapter.py`'s interval line is `:646`, not the plan's `:644`, because the docstring above it gained two lines.
- **Row 1 registration** (`vtf-meu-register.txt`): `.agent/context/meu-status.yaml: 150514 -> 151463 bytes`, `docs/build-plan/09-screenshot-capture.md: 158475 -> 160615 bytes`, `docs/build-plan/build-priority-matrix.md: 25754 -> 25900 bytes`, `registered MEU-160 at 9.45`. The render's drift check passed (`SSOT loaded (160 MEUs, 12 phases)`, `vtf-status-render-check-1.txt`); `meu-register selftest: 0 failure(s)` (`vtf-meu-register-selftest-1.txt`).
- **Row 2 reproduction** (`vtf-stress-bad.txt`): `host-load: ran at 17.5 %`, `busy children started: 24`, `load during: n=51 min=100.0 median=100.0 max=100.0`, `busy children left: 0`, `busy interpreters left: 0`, `RESULT: 5 bad in 400, every one with the signal (exit 0)`. The five, each with a packet read `arg=0.000% rc=0` and `stderr=''`:

  | Sequence | Clip, time | Packet read |
  |----------|------------|-------------|
  | 64 | `long_audio.mp4`, 3200 ms | empty |
  | 239 | `counter.mp4`, 2999 ms | empty |
  | 318 | `long_audio.mp4`, 3200 ms | short: `last 1560 below 2960`, so the retry grabbed an earlier frame |
  | 343 | `counter.mp4`, 2999 ms | empty |
  | 392 | `long_audio.mp4`, 3200 ms | empty |

  The module run (`vtf-load-base.txt`): `run 1: exit 0 in 23 s :: 21 passed, 16 warnings in 22.00s`, `load during the runs: n=7 min=100.0 median=100.0 max=100.0`, `busy children left: 0`, `BASE: 1 run(s), exit codes [0]`. `vtf-trace-check-base.txt`: `totals: {'packets': 2, 'bad': 0, 'failed': 0, 'wrong_arg': 0}`, `RESULT: base expectation met (exit 0)`. `vtf-trace-log-check.txt`: `run records: 96 every run record carries stderr: True probe duration and packet time per clip: {'counter.mp4': [True, True], 'long_audio.mp4': [True, True]}`.
- **Row 3 Red** (`vtf-red-unit.txt`): `8 failed, 30 passed in 0.27s`, child exit 1: both `ARGV_NAMED` tests and the six AC-160.1 cases; `red-check: 1 receipt(s), 8 required test(s), 0 problem(s)` (`vtf-red-unit-check.txt`). The guard, traced (`vtf-red-guard.txt`): `1 passed in 11.48s`; `vtf-red-guard-check.txt`: `modal last per clip and interval: {('one_keyframe.mp4', '89.999%'): 149960}`, `RESULT: base expectation met (exit 0)`. `vtf-red-hashes.txt`: `adapter unchanged: True`, `test files LF: True`, `guard packet reads: 1`.
- **Row 4 Green** (`vtf-green.txt`): `60 passed, 16 warnings in 9.22s` (the unit file and the integration module). `vtf-diff-check.txt`: `changed under packages/ and tests/ since row 0: ['packages/infrastructure/src/avkit_infra/media/adapter.py', 'tests/integration/test_video_real_ffmpeg.py', 'tests/unit/test_media_adapter_frames.py']`, `diff-check: 0 problem(s)`. `3 files already formatted` (`vtf-green-format.txt`); `All checks passed!` (`vtf-green-lint.txt`); `test files changed since row 3: []` (`vtf-green-hashes.txt`).
- **Row 5 acceptance.** `vtf-stress-clean.txt`: `host-load: ran at 14.1 %`, `busy children started: 24`, `load before the sequences: 100.0 %`, `busy children left: 0`, `busy interpreters left: 0`, `load during: n=138 min=100.0 median=100.0 max=100.0`, `500  counter.mp4 correct; good read`, `500  long_audio.mp4 correct; good read`, `RESULT: 1000 of 1000 correct, every packet read good and bounded (exit 0)`. `vtf-load-green.txt`: `host-load: ran at 11.5 %`, `run 1: exit 0 in 25 s :: 22 passed, 16 warnings in 24.00s`, `run 2: exit 0 in 24 s :: 22 passed, 16 warnings in 23.77s`, `run 3: exit 0 in 26 s :: 22 passed, 16 warnings in 25.77s`, `run 4: exit 0 in 24 s :: 22 passed, 16 warnings in 23.53s`, `run 5: exit 0 in 25 s :: 22 passed, 16 warnings in 24.72s`, `busy children left: 0`, `busy interpreters left: 0`, `load during the runs: n=40 min=100.0 median=100.0 max=100.0`, `PASS: 5 of 5 runs passed at median load 100.0 (threshold 85.0)`. `vtf-trace-check-green.txt`: each run `packet reads 3, bad 0, interval not in the green form 0`; `totals: {'packets': 15, 'bad': 0, 'failed': 0, 'wrong_arg': 0}`; `modal last per clip and interval: {('counter.mp4', '0.000%+62.999'): 2960, ('long_audio.mp4', '0.000%+63.200'): 2960, ('one_keyframe.mp4', '89.999%+209.999'): 149960}`; `RESULT: green expectation met (exit 0)`. The busy-process snapshots before and after the row read 0 (`vtf-busy-before-row5.txt`, `vtf-busy-after-row5.txt`).
- **Row 6 records.** `vtf-issue-resolve.txt`: `decision logs read: 104 of 104`, `register sha256 before=f7d1ed0d39d1283ead38e1840d4a57dca4e91df8592069ef5d0c89f4f0291124` (row 0's hash), `target sha256 after=01b1a5b0a6645256dbf2905c9136c8b8219332f761771f711cc992757cc15159 CRLF=0 LF=5733`, `parsed fields changed: 7` (`meu_links`, `resolution_path`, `root_cause`, `status` and the three `verification` fields of the one issue), `issue-resolve: 0 problem(s)`. `Rendered known-issues.md: 39 lines` (`vtf-issues-render.txt`); `OK: known-issues.md is up-to-date` (`vtf-issues-render-check.txt`). `Updated MEU-160 → ready_for_review (updated: 2026-11-18)` (`vtf-status-160.txt`); the render's drift check passed (`vtf-status-render-check.txt`); `meu-register selftest: 0 failure(s)` (`vtf-meu-register-selftest-6.txt`); `eol-check: 18 scope path(s), 0 problem(s)` (`vtf-eol-check.txt`). `vtf-row6-check.txt`: `row 93: ['| 93 | `video-tail-frame` | MEU-160 | P3 | executed (Session 93) | `docs/execution/plans/2026-11-17-video-tail-frame/` |'] grouping LF: True 09 CRLF: True note placed once in its section: True issue resolved with MEU-160 and a measured cause: True`.
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-row0.ps1 (task.md row 0's Validation cell: baseline.ps1 records baseline.sha, the dirty list and hashes, the scope, line-ending and skip hashes, the copies, the S1 and S2 binding, the cited lines, the plan-local selftests and the base Python suite); receipts vtf-baseline.txt, vtf-base-py.txt", "scope": "Row 0: the baseline at 9c655bd and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9c655bd (baseline.sha) plus row 0", "output": "vtf-baseline.txt: eol-check: 18 scope path(s), 0 problem(s); baseline-scope.json 25 paths; 3 absent; baseline: all steps exit 0. vtf-base-py.txt: 3112 passed, 37 warnings in 288.41s (0:04:48)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-1-register", "command": "pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-row1.ps1 (task.md row 1's Validation cell: meu-register.py bound to row 0's hashes, meu_status.py render and render --check, meu_status.py get MEU-160, meu-register.py --selftest); receipts vtf-meu-register.txt, vtf-status-render-1.txt, vtf-status-render-check-1.txt, vtf-status-160-1.txt, vtf-meu-register-selftest-1.txt", "scope": "AC-160.11: MEU-160 registered at matrix 9.45 (D-1165)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9c655bd (baseline.sha) plus rows 0 and 1", "output": "vtf-meu-register.txt: .agent/context/meu-status.yaml: 150514 -> 151463 bytes; docs/build-plan/09-screenshot-capture.md: 158475 -> 160615 bytes; docs/build-plan/build-priority-matrix.md: 25754 -> 25900 bytes; registered MEU-160 at 9.45. vtf-status-render-check-1.txt: Drift check passed, SSOT loaded (160 MEUs, 12 phases), rendered regions match on-disk content. vtf-meu-register-selftest-1.txt: meu-register selftest: 0 failure(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-2-base-reproduction", "command": "pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-row2.ps1 (task.md row 2's Validation cell: packet-stress.py --expect bad --sequences 400, load-run.py --mode base --runs 1, trace-check.py --mode base, the trace-log check); receipts vtf-stress-bad.txt, vtf-load-base.txt, vtf-trace-check-base.txt, vtf-trace-log-check.txt", "scope": "AC-160.4 and AC-160.6: the fault reproduced on the unchanged adapter under load (D-1168)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9c655bd (baseline.sha) plus rows 0 to 2", "output": "vtf-stress-bad.txt: host-load: ran at 17.5 %; busy children started: 24; load during: n=51 min=100.0 median=100.0 max=100.0; busy children left: 0; busy interpreters left: 0; RESULT: 5 bad in 400, every one with the signal (exit 0); bad sequences 64, 239, 318, 343 and 392, each packet read arg=0.000% rc=0 stderr=''. vtf-load-base.txt: run 1: exit 0 in 23 s :: 21 passed, 16 warnings in 22.00s; load during the runs: n=7 min=100.0 median=100.0 max=100.0. vtf-trace-check-base.txt: totals: {'packets': 2, 'bad': 0, 'failed': 0, 'wrong_arg': 0}; RESULT: base expectation met (exit 0). vtf-trace-log-check.txt: run records: 96 every run record carries stderr: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-3-red", "command": "python C:/Temp/av-kit/video-tail-frame/row3-apply.py (the two ARGV_NAMED replacements and the AC-160.1 and AC-160.8 inserts, by bytes, LF kept); pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-row3.ps1 (task.md row 3's Validation cell: ruff format and check, pytest on the unit file, red-check.py --require the 8 tests, the traced guard run, trace-check.py --mode base, the hash check); receipts vtf-red-unit.txt, vtf-red-unit-check.txt, vtf-red-guard.txt, vtf-red-guard-check.txt, vtf-red-hashes.txt", "scope": "AC-160.1 to AC-160.3 Red on the unchanged adapter; AC-160.8 guard passes at Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9c655bd (baseline.sha) plus rows 0 to 3", "output": "vtf-red-unit.txt: E   AssertionError: assert '7140.021%' == '7140.021%+7260.021'; E   AssertionError: assert '0.000%' == '0.000%+60.001'; 8 failed, 30 passed in 0.27s; child exit 1. vtf-red-unit-check.txt: red-check: 1 receipt(s), 8 required test(s), 0 problem(s). vtf-red-guard.txt: 1 passed in 11.48s. vtf-red-guard-check.txt: modal last per clip and interval: {('one_keyframe.mp4', '89.999%'): 149960}; RESULT: base expectation met (exit 0). vtf-red-hashes.txt: adapter unchanged: True test files LF: True guard packet reads: 1."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-4-green", "command": "python C:/Temp/av-kit/video-tail-frame/row4-apply.py (BOUNDED_TAIL_READ and TAIL_DOC in adapter.py, by bytes, CRLF kept); pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-row4.ps1 (task.md row 4's Validation cell: pytest on the unit file and the integration module, diff-check.py, ruff format --check, ruff check, the test-file hash check); receipts vtf-green.txt, vtf-diff-check.txt, vtf-green-format.txt, vtf-green-lint.txt, vtf-green-hashes.txt", "scope": "AC-160.1 to AC-160.3 Green, AC-160.7 and AC-160.8 after the fix", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9c655bd (baseline.sha) plus rows 0 to 4", "output": "vtf-green.txt: 60 passed, 16 warnings in 9.22s. vtf-diff-check.txt: changed under packages/ and tests/ since row 0: the adapter, the integration module and the unit file; diff-check: 0 problem(s). vtf-green-format.txt: 3 files already formatted. vtf-green-lint.txt: All checks passed!. vtf-green-hashes.txt: test files changed since row 3: []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-5-load-proofs", "command": "pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-row5.ps1 (task.md row 5's Validation cell: packet-stress.py --expect clean --sequences 1000, load-run.py --mode green --runs 5, trace-check.py --mode green --min-packets 3 over the five runs); receipts vtf-stress-clean.txt, vtf-load-green.txt, vtf-load-run-green-1.txt to -5.txt, vtf-trace-check-green.txt", "scope": "AC-160.5, AC-160.9 and AC-160.10 under load after the fix (D-1169)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9c655bd (baseline.sha) plus rows 0 to 5", "output": "vtf-stress-clean.txt: host-load: ran at 14.1 %; busy children started: 24; busy children left: 0; busy interpreters left: 0; load during: n=138 min=100.0 median=100.0 max=100.0; RESULT: 1000 of 1000 correct, every packet read good and bounded (exit 0). vtf-load-green.txt: run 1: exit 0 in 25 s :: 22 passed, 16 warnings in 24.00s; run 2: exit 0 in 24 s :: 22 passed, 16 warnings in 23.77s; run 3: exit 0 in 26 s :: 22 passed, 16 warnings in 25.77s; run 4: exit 0 in 24 s :: 22 passed, 16 warnings in 23.53s; run 5: exit 0 in 25 s :: 22 passed, 16 warnings in 24.72s; busy children left: 0; load during the runs: n=40 min=100.0 median=100.0 max=100.0; PASS: 5 of 5 runs passed at median load 100.0 (threshold 85.0). vtf-trace-check-green.txt: totals: {'packets': 15, 'bad': 0, 'failed': 0, 'wrong_arg': 0}; RESULT: green expectation met (exit 0)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-6-records", "command": "python C:/Temp/av-kit/video-tail-frame/write-resolve-set.py (issue-resolve-set.json, LF); python C:/Temp/av-kit/video-tail-frame/row6-apply.py (the Delivered note in 09, CRLF kept, and grouping row 93, LF kept, by bytes); pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-row6.ps1 (task.md row 6's Validation cell: issue-resolve.py --expect-sha256 from baseline-scope.json, issue_triage.py render and render --check, meu_status.py update MEU-160 ready_for_review --plan, render and render --check, meu-register.py --selftest, eol-check.py, the row 6 check); receipts vtf-issue-resolve.txt, vtf-issues-render.txt, vtf-issues-render-check.txt, vtf-status-160.txt, vtf-status-render.txt, vtf-status-render-check.txt, vtf-meu-register-selftest-6.txt, vtf-eol-check.txt, vtf-row6-check.txt", "scope": "AC-160.11 to AC-160.13: the issue resolved, MEU-160 ready_for_review, the Delivered note and grouping row 93 (D-1170)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9c655bd (baseline.sha) plus rows 0 to 6", "output": "vtf-issue-resolve.txt: decision logs read: 104 of 104; register sha256 before=f7d1ed0d39d1283ead38e1840d4a57dca4e91df8592069ef5d0c89f4f0291124; target sha256 after=01b1a5b0a6645256dbf2905c9136c8b8219332f761771f711cc992757cc15159 CRLF=0 LF=5733; parsed fields changed: 7; issue-resolve: 0 problem(s). vtf-issues-render-check.txt: OK: known-issues.md is up-to-date. vtf-status-160.txt: Updated MEU-160 to ready_for_review (updated: 2026-11-18). vtf-meu-register-selftest-6.txt: meu-register selftest: 0 failure(s). vtf-eol-check.txt: eol-check: 18 scope path(s), 0 problem(s). vtf-row6-check.txt: grouping LF: True 09 CRLF: True note placed once in its section: True issue resolved with MEU-160 and a measured cause: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-rowH1-2.ps1 (task.md row H1-2's Validation cell, after the load wait read 8.2 %: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-17-video-tail-frame/session-gate.ps1 *> C:/Temp/av-kit/video-tail-frame/vtf-gate-h1.txt); step receipts vtf-D6-<step>.txt", "scope": "H1-2: the PROFILE D6 session gate, 24 steps from identity-before to identity-after, including the full Python suite; the ui-* steps other than ui-canon, openapi and mcp-* skipped with their reasons", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "9c655bdf6ac2436308e20d4b889268e051d4e19d+6b06b8a25e513a5e2073813d4eedf4a659e77acd4f791ec51559a8dec0331ea2", "output": "vtf-gate-h1.txt: every step exit=0 (identity-before, task-contract, scope-paths, line-endings, home-path, nine selftests, py-format, py-lint, py-types, py-frames, ui-canon, host-load, py-tests, issues-render-check, state-render, identity-after); tested_state before and after equal; session-gate: all steps exit 0. vtf-D6-host-load.txt: host-load samples: [11, 4, 13, 31, 8] mean=13.4; host-load: ran at 13.4 %. vtf-D6-scope-paths.txt: diff-check: 0 problem(s). vtf-D6-line-endings.txt: eol-check: 18 scope path(s), 0 problem(s). vtf-D6-py-types.txt: 0 errors, 0 warnings, 0 informations. vtf-D6-py-frames.txt: 60 passed, 16 warnings in 8.98s. vtf-D6-ui-canon.txt: Test Files  2 passed (2); Tests  14 passed (14). vtf-D6-py-tests.txt: 3119 passed, 37 warnings in 253.47s (0:04:13); py-tests: D6 argv exit 0. vtf-D6-issues-render-check.txt: OK: known-issues.md is up-to-date."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "vtf-h1-3-h1-4-closeout-checks", "command": "python C:/Temp/av-kit/video-tail-frame/focus-entry.py (the Session 93 entry on top of .agent/context/current-focus.md, by bytes, CRLF kept); pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-rowH1-3.ps1 (meu_status.py render --check, meu_status.py get MEU-160); pwsh -NoProfile -File C:/Temp/av-kit/video-tail-frame/run-rowH1-4.ps1 (task.md row H1-4's skip-basis check)", "scope": "H1-3 (current focus, the state render, MEU-160 ready_for_review) and H1-4 (the UI, OpenAPI and MCP skip basis)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus entry (identity.py excludes current-focus.md)", "output": "focus-entry.py: current-focus: bytes 88441 -> 89795 CRLF 218 -> 221 bare LF 0. vtf-render-check.txt: Drift check passed, SSOT loaded (160 MEUs, 12 phases), rendered regions match on-disk content. vtf-h13-status-160.txt: \"status\": \"ready_for_review\", \"execution_plan\": \"docs/execution/plans/2026-11-17-video-tail-frame/\". skip-basis-check.txt: changes under packages (other than adapter.py), mcp-server, tools or ui since row 0: []."}
```

### Quality Gate Results

| Step | Result (receipt) |
|------|------------------|
| Gate | `session-gate: all steps exit 0` (`vtf-gate-h1.txt`); 24 steps, each `exit=0` |
| Identity | `tested_state 9c655bdf6ac2436308e20d4b889268e051d4e19d+6b06b8a25e513a5e2073813d4eedf4a659e77acd4f791ec51559a8dec0331ea2`, equal before and after (`vtf-D6-identity-before.txt`, `vtf-D6-identity-after.txt`) |
| Task contract | `OK: 24 row(s)`; `2 row(s) exempt (view_file): H1-5, H2-1` (`vtf-D6-task-contract.txt`) |
| Scope | `diff-check: 0 problem(s)` (`vtf-D6-scope-paths.txt`) |
| Line endings | `eol-check: 18 scope path(s), 0 problem(s)` (`vtf-D6-line-endings.txt`) |
| Home path | `check_home_path: ok files=2647 allowlisted=60 nul=31` (`vtf-D6-home-path.txt`) |
| Selftests | the nine plan-script selftests, each exit 0; `meu-register selftest: 0 failure(s)` (`vtf-D6-meu-register-selftest.txt`) |
| Format, lint, types | `13 files already formatted` (`vtf-D6-py-format.txt`); `All checks passed!` (`vtf-D6-py-lint.txt`); `0 errors, 0 warnings, 0 informations` (`vtf-D6-py-types.txt`) |
| Frames, targeted | `60 passed, 16 warnings in 8.98s` (`vtf-D6-py-frames.txt`) |
| UI canon | `Test Files  2 passed (2)`, `Tests  14 passed (14)` (`vtf-D6-ui-canon.txt`) |
| Host load | `host-load: ran at 13.4 %` (`vtf-D6-host-load.txt`) |
| Python, full | `3119 passed, 37 warnings in 253.47s (0:04:13)`, `py-tests: D6 argv exit 0` (`vtf-D6-py-tests.txt`; row 0 had 3112, and rows 3 adds seven: six AC-160.1 cases and AC-160.8) |
| Registers | `OK: known-issues.md is up-to-date` (`vtf-D6-issues-render-check.txt`); the state render's drift check passed (`vtf-D6-state-render.txt`) |
| Skipped | the other `ui-*` steps, `openapi` and `mcp-*`, each printed with its reason (`vtf-gate-h1.txt`) |
| H1-3 | the state render's drift check passed after the current-focus entry (`vtf-render-check.txt`); MEU-160 `ready_for_review` (`vtf-h13-status-160.txt`) |
| H1-4 | `changes under packages (other than adapter.py), mcp-server, tools or ui since row 0: []` (`skip-basis-check.txt`) |

---

## Changed Files

Counts are added / removed lines against `HEAD` `9c655bd` (`git diff --numstat --ignore-cr-at-eol`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step, `vtf-D6-line-endings.txt`).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | `BOUNDED_TAIL_READ` at `:646`; the `TAIL_DOC` sentence in `_last_video_ms`'s docstring | +4 / -2 | CRLF kept |
| `tests/unit/test_media_adapter_frames.py` | `ARGV_NAMED` at `:289` and `:313`; AC-160.1 at `:318-339` | +25 / -2 | LF kept |
| `tests/integration/test_video_real_ffmpeg.py` | AC-160.8 at `:285` | +21 / -0 | LF kept |
| `.agent/context/meu-status.yaml` | the MEU-160 entry (row 1); `ready_for_review` with this plan (row 6) | +28 / -2 | LF kept |
| `.agent/context/meu-registry.md` | `meu_status.py render` | +1 / -0 | LF |
| `docs/BUILD_PLAN.md` | `meu_status.py render` | +3 / -3 | LF |
| `docs/build-plan/09-screenshot-capture.md` | §Video tail packet read and its MEUs row (row 1); the `Delivered (Session 93)` note (row 6) | +25 / -0 | CRLF kept |
| `docs/build-plan/build-priority-matrix.md` | the 9.45 row | +1 / -0 | CRLF kept |
| `.agent/context/known-issues.yaml` | `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` resolved (`issue-resolve.py`) | +8 / -6 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` | +3 / -4 | LF |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | row 93: MEU-160, `executed (Session 93)` and the plan folder | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 93 entry (H1-3) | +3 / -0 | CRLF kept |
| `docs/execution/plans/2026-11-17-video-tail-frame/` | the plan (Status line, see Departures), task (row marks), the plan-local scripts, the row-0 records, `red-hashes.json` and `session-gate.ps1` | new folder | LF (`red-hashes.json` CRLF, see Departures) |
| `.agent/context/handoffs/2026-11-17-video-tail-frame-MEU-160-handoff.md` | this handoff | new | LF |

**The two named assertion changes (`ARGV_NAMED`).** In `tests/unit/test_media_adapter_frames.py`, and only their expected interval:

| Line | Test | Old | New |
|------|------|-----|-----|
| `:289` | `test_ac_134_9_end_gap_reads_the_last_packet_and_grabs_again` (`:272`) | `        "0.000%",` | `        "0.000%+62.999",` |
| `:313` | `test_ac_134_9_end_gap_reads_from_60_seconds_before` (`:304`) | `    assert packet[packet.index("-read_intervals") + 1] == "7140.021%"` | `    assert packet[packet.index("-read_intervals") + 1] == "7140.021%+7260.021"` |

What each asserts is otherwise unchanged: the whole packet argv and the retry at `2.959` in the first, the interval's start in the second. No other line of an existing test changed (`vtf-diff-check.txt`; gate `scope-paths`).

```diff
-        call. A timeout, a non-zero exit or no usable time gives `None`.
+        call. A timeout, a non-zero exit or no usable time gives `None`. The interval has an end
+        of `time_ms` + 60 s past the first packet read, because an open interval reads unset
+        fields in ffprobe.
-            f"{_seek_text(start)}%",
+            f"{_seek_text(start)}%+{_seek_text(time_ms + END_GAP_LOOKBACK_MS)}",
```

The docstring line at row-0 `:626` becomes the three that follow it, and row-0 `:644` becomes `:646` (`git diff -U0 --ignore-cr-at-eol`). Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No findings: the round 1 review's Findings table is empty.

### Verdict

`approved` at round 1 of 6, with 0 findings and 0 blocking, intent achieved (`.agent/context/handoffs/2026-11-17-video-tail-frame-implementation-critical-review.md`, a byte-for-byte copy of the reviewer's report, checked with `cmp`; ledger loop `vtf-execution-2026-11-17-video-tail-frame`, round 1 `verdict=approved agent='codex-independent-reviewer' blocking=0 intent_achieved=yes usage=10,355,927`, `loop may close: approved with no blocking findings.`).

- **The loop.** It began with the plan's goal anchor and citable AC-5, AC-156, AC-157 and AC-160, with no token budget; the OK line reads `mode=execution budget=6 tokens=off` (`vtf-exec-begin.txt` in the dispatch folder). Dispatch `vtf-exec-r1` ran with kind `execution` (timeout 2700 s); its console, `vtf-exec-console-r1.txt` in the dispatch folder, ends with exit 0.
- **The state.** The reviewer's own identity matched the gate's tested_state `9c655bdf6ac2436308e20d4b889268e051d4e19d+6b06b8a25e513a5e2073813d4eedf4a659e77acd4f791ec51559a8dec0331ea2` exactly (review frontmatter and §Scope, record `review-lightweight-checks`); no state adjustment was needed.
- **What it accepted.**
  - BOUNDED_TAIL_READ, TAIL_DOC and TAIL_SAME_ANSWER (§Q2): the end is K + T + 60 s from the first packet read (`ffprobe-master.c:1874-1887`, `:3308-3345`), so in the tail case it lies past T for any keyframe K at or after 0; the lookback, stream, deadline, subprocess options, decoding and single fallback are unchanged.
  - ARGV_NAMED and the tests (§Q3): only `:289` and `:313` of existing test lines changed; the Red is eight genuine assertion failures; AC-160.8 guards against a shorter `T - S + 60 s` duration and is stated not to be a deterministic regression test for the old flake, which the argv assertions and the stress comparison prove.
  - GRAB_TRACE, TAIL_SIGNAL and NO_RETRY (§Q4): its own log probe confirmed the 5 bad base sequences (four empty, one short), all 1000 green reads at 2960 ms with bounded arguments, and 3 correct packet reads in each of the five green module runs; both RULE-3 fixtures exit 3; every busy launcher and interpreter was cleaned up.
  - The registers (§Q5): only the target issue changed, in its five allowed fields; only grouping row 93 changed.
  - The gate (§Q6) and the scope and fidelity (§Q7): 24 steps, all exit 0; the 629 skip-basis hashes and the 8 foreign hashes match row 0; every disclosed departure was judged sound.
- **What it did not rerun.** A load run or the full suite. It accepted the saved gate and load proofs against the matching identity and ran only targeted checks (`38 passed in 0.17s`, the diff and eol checks, the nine selftests, both render checks) and read-only probes (`PROBE PASS`).
- **Residuals it names.** A grab well inside a longer file is bounded rather than read to the end, within the approved TAIL_SAME_ANSWER condition; the load proofs are finite, on the pinned binaries.
- **H1-7a** (`review-state-check.txt`, `review-state.json`): `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`.
- **H1-7b** (`exec-review.txt`): `OK: approved at round 1 of 6, 0 open blocking findings`.
- **After the review**, only this handoff changed, to fill this report. `identity.py` excludes the handoffs, so the tested_state is unchanged (H1-6b below).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| An upstream FFmpeg report: `-read_intervals START%` reads `end`, `end_is_offset` and `duration_frames` unset (`fftools/ffprobe.c:3344`, `:3365`, `:1878`, `:1883` at master `3633db72`) | follow-up for Mat | — | Not sent (M-12; Out of Scope). The report would carry the citations, the plan-time probes and row 2's counts; whether to file it, and under whose name, is Mat's call |
| Other `-read_intervals` callers | out-of-scope | — | `_last_video_ms` is the only open interval in the adapter (D-1166) |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **Status line and queue order.** The coordinator wrote the execution approval into the plan's Status line before execution began; that is the plan's only change since the plan review, and its sha256 moved from `92d51947…` to `be8734878d202f85c0fbc7ff7867dc877e32f97db1e2a7bf7f58b7d54a0fb770`. That Status line still says Session 93 runs fourth; under D-1142 the queue is 74, 92, 93, 94, then 91, so Session 93 ran third, after 74 (`cba97fe`) and 92 (`8280586`). `task.md` changed only by its row marks; its sha256 at approval was `a70b433ffc3bf914252c486b907eb8f4d63edd38be414cd3f8a7386533664ac3`.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file (an environment header setting the working directory, `TMP` and `TEMP`, `RECEIPTS_DIR` and clearing `ELECTRON_RUN_AS_NODE`, then the cell verbatim) and run with `pwsh -NoProfile -File`. The hand edits of rows 3, 4 and 6 were made by scripts that wrote bytes and asserted each anchor occurred once.
- **The load wait.** Under the coordinator's brief, a wait until the host load read 50 % or less ran before each Red, each proof and the gate (`vtf-hostwait-row2.txt` to `vtf-hostwait-row5.txt`, `vtf-hostwait-h12.txt`; each read under 17 %). It is outside the cells; the cells' own load steps ran as written.
- **The pre-row scope check.** Under the brief, a read-only S4 check ran before each row from row 1 (`vtf-s4-pre-row1.txt` to `vtf-s4-pre-row6.txt`, each `0 problem(s)`): HEAD equal to `baseline.sha`, every dirty path in scope, the plan folder or row 0's dirty list, the read-only paths unchanged, the foreign dirty paths at their row-0 hashes, and every scope path no earlier row wrote at its row-0 hash. Its first version, run before rows 1 and 2, lacked the last two checks; the full version ran before row 2 completed (`vtf-s4-pre-row2-full.txt`, 0 problems); row 2 writes no file in the checkout.
- **The busy-process snapshots.** Under the brief, read-only snapshots of the busy children before and after rows 2 and 5 recorded 0 each time (`vtf-busy-before-row2.txt`, `vtf-busy-after-row2.txt`, `vtf-busy-before-row5.txt`, `vtf-busy-after-row5.txt`).
- **`red-hashes.json` is CRLF.** Row 3's own command writes `red-hashes.json` with `Path.write_text`, which on Windows writes CRLF (4 CR, 4 LF). It is the plan's command, not an edit of mine, and row 4 reads the file back as JSON, so the hashes held.
- **The `resolution_path` and `last_checked` date.** The plan's row 6 text begins "Fixed in Session 93 on 2026-11-17"; the session ran on 2026-11-18, so the register says 2026-11-18, as Session 92's entries do. The MEU-160 entry's `note` keeps the plan's "Registered 2026-11-17" text from `meu-register.py`.
- **The gate.** `session-gate.ps1` follows Session 90's shape. Its `ui-canon` step runs Vitest from `ui/` through the step's working directory. Its base-failure excuse list is empty, because row 0's Python suite had no failure.
- **Execution decisions.** None was needed: no stop fired, D-1171 (S8) was not used, and D-1172 to D-1174 are unused. D-1165 to D-1170 are the plan's. So the Decision Log below is `None.`.

### Execution notes

- **The decisions.** D-1165: MEU-160 registered, because the cause is in the product. D-1166: the bounded read `S%+D` with D = T + 60 s, with the FFmpeg citations above and the plan-time gop probe (`vtf93-gop-probe.txt`) behind AC-160.8. D-1167: the two named assertion changes. D-1168: the trace plugin and the stress driver. D-1169: 1000 sequences and five module runs under load, after 400 at base showed the fault. D-1170: the issue resolved with `meu_links` and the measured `root_cause`.
- **Processes.** Each proof stopped only the busy children it started, by id and creation time, and every snapshot after a proof read 0.
- **The base module run passed.** Row 2's one traced module run under load had no failure (`21 passed`); the fault showed in the adapter sequences (5 of 400), which is why D-1168 drives the adapter directly rather than relying on module runs.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
| Reviewed | 2026-11-18 | codex-independent-reviewer | Execution review round 1: `approved`, 0 findings, intent achieved |
| Updated | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Codex Validation Report filled; H1-6, H1-6a and H1-6b rerun |
