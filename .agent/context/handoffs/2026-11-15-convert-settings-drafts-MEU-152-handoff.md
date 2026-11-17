---
date: "2026-11-16"
project: "2026-11-15-convert-settings-drafts"
meu: "MEU-152"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md"
build_plan_section: "bp08"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: ".agent/context/handoffs/2026-11-15-convert-settings-drafts-MEU-151-handoff.md"
---

# Handoff: 2026-11-15-convert-settings-drafts-MEU-152-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-152 `convert-queue-labels` (issues `CONVERT-CUT-TIME-RAW-MS`, `CONVERT-POSITIONS-NOT-RENUMBERED`, `CONVERT-CUT-ENCODER-LABEL`, triage D-809; and, by amendment A1, `CONVERT-OUTPUT-NAME-REUSED`). A Convert card shows a Cut's times as timecodes, numbers its cards 1, 2, 3 in the order shown with a waiting rank that moves up, never shows a GPU encoder for a Fast copy Cut, and a second Add of the same file never takes the first job's output name.
**Build Plan Section**: [08 §Convert queue labels (residual)](../../../docs/build-plan/08-video-conversion.md#convert-queue-labels-residual) (matrix 8.11), with the Delivered (Session 81) note at the end of that section.
**Predecessor**: MEU-151 (same session).

- **Cut times (D-969).** `convert-time.ts` gains `CONVERT_TIME_MAX_MS` and `formatConvertTime` (`CONVERT_TIMECODE`, as `format_timecode` does); `convertModeSegment` gives a Cut `HH:MM:SS.mmm–HH:MM:SS.mmm`, and drops the segment when a side does not format (`CUT_SEGMENT_TIMECODE`).
- **Positions (D-970).** `convertQueuePositions` gives each card its 1-based row in the order shown and, for a Pending job, its rank among the waiting jobs (`QUEUE_ROW_NUMBER`). `QueueCard` gains an optional `waitingPosition`, reading `Waiting - next` or `Waiting - N in line`; without it the old text stays byte for byte, so other pages' cards and `queue-slot-baseline.json` are unchanged (`WAITING_POSITION`). Stored `queue_position` values are not read or renumbered.
- **Cut encoder (D-968).** In `_dispatch`, a Cut stores `gpu_encoder` `None` for Fast copy (or no copy mode) and `"libx265"` for Reencode, and runs no GPU check (`CUT_NO_GPU_ENCODER`). Compress, Extract and the adapter are unchanged.
- **Amendment A1 (D-1060 to D-1065).** Round 1 of row 5 found that a second Add of one video overwrote the first job's file (Mat, HC-2: 'job 1 and 2 where working on the same video, looks like 2 overwrote 1. But jobs finished'). Mat chose "Fix in Session 81" (D-1060). `services/conversion.py` gains `QUEUE_OUTPUT_RESERVED` (Pending, Processing, Failed and Cancelled jobs hold their output name; a row with a probe or track error never takes the skip alias), `QUEUE_ADD_SERIAL` (one lock from the queue read to the commit) and `ACTIVE_WRITER_RESERVED` (a running media call's name stays held until the call exits, even after Remove or Clear). A1's plan review round 1 returned A1-R1-F1 and A1-R1-F2, corrected inside A1 as D-1064 and D-1065 (AC-152.18 to AC-152.20). The new issue `CONVERT-OUTPUT-NAME-REUSED` was added and resolved in row 7.
- **The real-app checks (A2, D-975).** Round 1 was Mat's look: HC-1 `pass`, HC-2 the overwrite above, HC-3 `pass` (`cs81-human-check-r1.txt`). Round 2 became Electron tests by Mat's ruling ('why are you giving me e2e tests manually! This should be done with framework and scripts! It delays the development!'): HC-1, HC-2, HC-3 and HC-5 are AC-152.21 to AC-152.24 in `ui/tests/e2e/convert-queue-labels.test.ts`, which launch the built app with a scratch profile and the real backend. The test seams are D-976. No pass is written for Mat for round 2.
- **Spec text and records (rows 6 to 8).** The 08 Delivered (Session 81) note; the four MEU-152 issues resolved through `issue-resolve.py` (`issue-resolve: 0 problem(s)`); MEU-152 `ready_for_review` (`cs81-status-152.txt`); grouping row 81 `executed (Session 81)`.

**Residual risk for triage.** These were found and left, as the plan's §Out of Scope says:
- the Downloader and Transcript queues still print the stored 0-based `queue_position` (`DownloaderPage.tsx:478`, `transcript-card.ts:134`; D-971);
- whether the Downloader and TTS queues reuse an output name the same way was not checked (D-1063);
- Remove and Clear still do not stop a running media call; A1 keeps that call's name held instead (D-1065);
- stored jobs that already share an output path are not rewritten (D-1061), and stored Cut rows keep their old `gpu_encoder` until they are retried (D-968).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md) §MEU-152, §Execution amendment A1 and §Execution amendment A2. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions."; A1's product work on "Go ahead with the A1 product work." after its plan review ([amendment-a1-plan-critical-review.md](2026-11-16-convert-settings-drafts-amendment-a1-plan-critical-review.md)). The plan review approved at round 2 ([plan-critical-review.md](2026-11-15-convert-settings-drafts-plan-critical-review.md)). The plan's Status line (line 15) was changed after that review; see the MEU-151 handoff and Departures.

**Receipts.** A receipt named by its file name alone is in the session's receipts folder (`RECEIPTS_DIR`, the plan's `convert-settings-drafts` folder under it). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-152.1 | unit | `formatConvertTime` gives `HH:MM:SS.mmm` for 0, 1000, 4500, 3 723 004 and 359 999 999 | Local Canon (08 Cut times; `format_timecode`; D-969) | `ui/tests/unit/convert-queue-labels.test.ts:105` | ✅ |
| AC-152.2 | unit | `parseConvertTime(formatConvertTime(ms)) === ms`; -1, 1.5, NaN, Infinity and 360 000 000 give `null` | Local Canon (`convert-time.ts`; `TIME_MAX_MS`; D-969) | `convert-queue-labels.test.ts:114` | ✅ |
| AC-152.3 | unit | A Cut's mode segment is `00:00:01.000–00:00:04.500` (the moved pin); an out-of-range Cut drops it; a sparse Cut gives `['Cut']` | Local Canon (08 Cut times; AC-45.17 null-drop rule; D-969) | `convert-controls.test.ts:218`; `convert-queue-labels.test.ts:127` | ✅ |
| AC-152.4 | unit | `convertQueuePositions` gives rows 1, 2, 3 and waiting `null`, 1, 2 for Processing, Pending, Pending | Local Canon (08 Position; D-970) | `convert-queue-labels.test.ts:134` | ✅ |
| AC-152.5 | unit | After a finish, the first waiting job reads 1 although two cards are above it | Local Canon (08 Position; D-970) | `convert-queue-labels.test.ts:143` | ✅ |
| AC-152.6 | unit | After a remove, a gap in the stored positions still gives contiguous rows | Local Canon (08 Position; D-970) | `convert-queue-labels.test.ts:152` | ✅ |
| AC-152.7 | unit | After a move, the array order decides, not the stored position | Local Canon (08 Position; D-970) | `convert-queue-labels.test.ts:161` | ✅ |
| AC-152.8 | unit | `QueueCard` shows the row, `Waiting - next` or `Waiting - 2 in line`, and the old text without `waitingPosition`; the slot baseline keeps its row-0 hash | Local Canon (`WAITING_POSITION`; D-970) | `convert-queue-labels.test.ts:170`; `queue-card.test.ts` | ✅ |
| AC-152.9 | unit | `ConvertPage` over stored positions 0, 2, 5 shows 1, 2, 3 and the waiting texts `Waiting - next`, `Waiting - 2 in line` | Local Canon (08 Position; D-970) | `ui/tests/unit/convert-page.behavior.test.ts:1369` | ✅ |
| AC-152.10 | unit | A Fast copy Cut and a Cut with no copy mode run `Done` with `gpu_encoder` `None` and no GPU check | Local Canon (08 Cut encoder; EXTRACT_NO_ENCODER; D-968) | `tests/unit/test_convert_cut_encoder.py:41` | ✅ |
| AC-152.11 | unit | A Reencode Cut stores `libx265` with no GPU check; a Fast copy Cut with no software encoder runs `Done`; a legacy `Failed` Cut holding `hevc_nvenc`, retried, ends `Done` with `None` | Local Canon (08 Cut encoder; AC-123.6, AC-123.7 shapes; D-968) | `test_convert_cut_encoder.py:69`, `:87`, `:112` | ✅ |
| AC-152.12 | integration, e2e | Existing tests pass unchanged: `test_conversion_service.py -k "ac_123_6 or ac_123_7 or ac_123_8 or ac_112_4"`, the rest of `convert-controls.test.ts`, `queue-card.test.ts`, `convert-page.test.ts`, and the Electron file `convert-queue.test.ts` | Local Canon (AC-123.6 to AC-123.8, AC-112.4, AC-45.x) | gate steps `meu-152-py`, `meu-152-ui`, `ui-tests`, `ui-electron-convert` | ✅ |
| AC-152.13 | unit | Two separate Adds of one source give two different output paths, both `Pending`, with skip off and on (`clip_cut.mp4`, `_1`, `_2`; Compress the same); the Cut case also on SQLite in `tmp_path` | Local Canon (08:292; HC-2; D-1060, D-1061) | `tests/unit/test_convert_output_reserved.py:140`, `:169` | ✅ |
| AC-152.14 | unit | A first job that is `Processing`, `Failed` or `Cancelled` still holds its name; a `reset_failed` job keeps its path, distinct from the later job's | Local Canon (08:292; `REQUEUEABLE_CONVERSION_STATUSES`; D-1061) | `test_convert_output_reserved.py:192`, `:209` | ✅ |
| AC-152.15 | unit | Guard: with no media call running, Remove and Clear free a name; a `Done` job whose file was deleted frees it; a `Done` file on disk gives `Skipped` with skip on and `_1` with it off | Local Canon (08:292; AC-30.2's skip rule; D-1061, D-1062) | `test_convert_output_reserved.py:243` | ✅ |
| AC-152.16 | unit | Two threads Add the same source at once (a two-party barrier in `probe`); both finish within 10 s with different paths | Local Canon (`QUEUE_ADD_SERIAL`; D-1061) | `test_convert_output_reserved.py:274` | ✅ |
| AC-152.17 | integration, e2e | Existing tests pass unchanged: all of `tests/unit/test_conversion_service.py` (AC-30.2 included) and `tests/e2e/test_api_conversions.py` | Local Canon (AC-30.x, AC-31.x) | gate steps `meu-152-py`, `py-tests` | ✅ |
| AC-152.18 | unit | A1-R1-F1: a second Add whose probe fails beside a running job (or a `Done` file) is `Failed` at `_1`, never the other path; its retry leaves the first file's bytes | Local Canon (08:292; AC-30.1; D-1064) | `test_convert_output_reserved.py:303`, `:337` | ✅ |
| AC-152.19 | unit | A1-R1-F2: a running job removed (or cleared) before it creates its file still holds its name; the next Add gets `_1` and each file holds its own call's bytes | Local Canon (08:292; D-1065) | `test_convert_output_reserved.py:361` | ✅ |
| AC-152.20 | unit | Guard: a running call's name is freed when the call exits; removing a `Pending` job while another runs frees its name at once | Local Canon (D-1061, D-1065) | `test_convert_output_reserved.py:391` | ✅ |
| AC-152.21 | e2e | A2, was HC-1: a Fast copy Cut from `00:00:01.000` to `00:00:02.500` shows that range in its card while waiting and after Done | Local Canon (08 Cut times; D-969; D-975) | `ui/tests/e2e/convert-queue-labels.test.ts:382` | ✅ |
| AC-152.22 | e2e | A2, was HC-2: four Cuts read 1 to 4 with their waiting texts; after removing the third, 1 to 3; after Start, the third reads `Waiting - next` and the rows stay 1 to 3 | Local Canon (08:646; D-970; D-975) | `convert-queue-labels.test.ts:401` | ✅ |
| AC-152.23 | e2e | A2, was HC-3: a Fast copy Cut's card shows no encoder name while it waits, runs and is Done, and its stored `gpu_encoder` is null; a re-encode Cut shows `libx265` | Local Canon (08 Cut encoder; D-968; D-975) | `convert-queue-labels.test.ts:475` | ✅ |
| AC-152.24 | e2e | A2, was HC-5: two Adds of one video as Cut give `<stem>_cut.mp4` and `<stem>_cut_1.mp4` while both wait; after Done both files exist with their own durations and different SHA-256 | Local Canon (08:292; D-1060, D-1061; D-975) | `convert-queue-labels.test.ts:519` | ✅ |
| AC-45.17 (cross-ref) | changed test | `AC-45.17 convertMetaSegments returns CONVERT_META_SEGMENTS with null fields dropped`: its Cut pin moved from `1000–4500` to `00:00:01.000–00:00:04.500` (AC-152.3); the rest stays | MEU-45 | `ui/tests/unit/convert-controls.test.ts:218` | ✅ |
| AC-112.4, AC-123.6 to AC-123.8 (cross-ref) | guard | The encoder tests pass unchanged (AC-152.12) | MEU-112, MEU-123 | `tests/unit/test_conversion_service.py` (gate `meu-152-py`) | ✅ |
| AC-30.2, AC-31 (cross-ref) | guard | The skip rule and the conversion routes pass unchanged; `test_conversion_service.py` is read, never changed (AC-152.17) | MEU-30, MEU-31 | `test_conversion_service.py`, `tests/e2e/test_api_conversions.py` (gate `py-tests`) | ✅ |
| AC-151 (sibling) | sibling MEU | AC-151.1 to AC-151.14, with the AC-2, AC-39, AC-57, AC-67, AC-105, AC-107, AC-112 and AC-143 cross-references: the capture draft and Convert choices, evidenced in the MEU-151 handoff | MEU-151 | `2026-11-15-convert-settings-drafts-MEU-151-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-152.1, AC-152.2, AC-152.3 (new cases) | `convert-time exports formatConvertTime: expected 'undefined' to be 'function'` (`cs81-152-red-ui.txt`) | Row 4: pass (`cs81-152-green-ui.txt`) | `convert-queue-labels.test.ts:105`, `:114`, `:127` |
| AC-152.3 (AC-45.17 pin) | `expected [ 'Cut', '1000–4500' ] to deeply equal [ 'Cut', '00:00:01.000–00:00:04.500' ]` | Row 4: pass | `convert-controls.test.ts:218` |
| AC-152.4 to AC-152.8 | `convert-controls exports convertQueuePositions: expected 'undefined' to be 'function'` | Row 4: pass | `convert-queue-labels.test.ts:134` to `:170` |
| AC-152.9 | `expected [ '0', '2', '5' ] to deeply equal [ '1', '2', '3' ]` | Row 4: pass | `convert-page.behavior.test.ts:1369` |
| AC-152.10, AC-152.11 | `assert (… 'hevc_nvenc', 1) == (… None, 0)` (`cs81-152-red-py.txt`) | Row 4: pass (`cs81-152-green-py.txt`) | `test_convert_cut_encoder.py:41` to `:112` |
| AC-152.13, AC-152.14, AC-152.16, AC-152.18, AC-152.19 | 13 parametrized cases `FAILED` (`cs81-a1-red-py.txt`) | Row 4b: pass (`cs81-a1-green-py.txt`) | `test_convert_output_reserved.py:140` to `:361` |

- **Row 3 Red.** `cs81-152-red-ui.txt`: `Test Files  3 failed (3)` and `Tests  10 failed | 67 passed (77)`, exit 1; `cs81-152-red-ui-check.txt`: `red-check: 1 receipt(s), 10 required test(s), 0 problem(s)`. `cs81-152-red-py.txt`: `5 failed in 0.36s`, exit 1; `cs81-152-red-py-check.txt`: `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)` (the D-919 pytest header form, D-974).
- **Row 4 Green.** `cs81-152-green-ui.txt`: `Test Files  5 passed (5)` and `Tests  131 passed (131)`; `cs81-152-green-py.txt`: `5 passed in 0.35s`; `cs81-152-guards-py.txt`: `8 passed, 28 deselected in 8.14s`; `cs81-152-eol.txt`: `line-ending or fixture drift: [] bare LF in convert-controls.ts: 8`.
- **Row 4a Red (A1).** `cs81-a1-red-py.txt`: `13 failed, 6 passed in 10.55s`, exit 1; `cs81-a1-red-py-check.txt`: `red-check: 1 receipt(s), 5 required test(s), 0 problem(s)`. The six that passed are the parametrized cases of the guards AC-152.15 and AC-152.20, which pin behaviour that already held.
- **Row 4b Green (A1).** `cs81-a1-green-py.txt`: `83 passed in 13.37s`; `cs81-a1-eol.txt`: `line-ending drift: []`; `cs81-a1-ruff.txt`, `cs81-a1-pyright.txt` and `cs81-a1-format.txt` clean.
- **AC-152.21 to AC-152.24 have no Red** (plan §Execution amendment A2). HC-1 to HC-3 pin what rows 2 and 4 built; HC-5's Red against `b6b124a` would need the service file as it was before row 4b, which means changing the tree or adding a worktree, both outside this session's rules. Row 4a's unit Red proved that defect. They passed in row 5's three runs (`cs81-row5-e2e-r1.txt` to `-r3.txt`: `5 passed (1.1m)`, `5 passed (1.0m)`, `5 passed (1.9m)`) and in the gate's `ui-electron-a2`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-3-red-152", "command": "pwsh -NoProfile -File (task.md row 3's Validation cell: npm --prefix ui run test -- tests/unit/convert-queue-labels.test.ts tests/unit/convert-controls.test.ts tests/unit/convert-page.behavior.test.ts *> C:/Temp/av-kit/convert-settings-drafts/cs81-152-red-ui.txt; uv run pytest tests/unit/test_convert_cut_encoder.py *> C:/Temp/av-kit/convert-settings-drafts/cs81-152-red-py.txt; their exit codes; red-check.py --require for each); receipts cs81-152-red-ui.txt, cs81-152-red-ui-check.txt, cs81-152-red-py.txt, cs81-152-red-py-check.txt, cs81-s4-row3.txt", "scope": "MEU-152 Red: AC-152.1 to AC-152.11 against the row-2 product code", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 3", "output": "cs81-152-red-ui.txt: Test Files  3 failed (3); Tests  10 failed | 67 passed (77); exit 1. cs81-152-red-ui-check.txt: red-check: 1 receipt(s), 10 required test(s), 0 problem(s). cs81-152-red-py.txt: 5 failed in 0.36s; exit 1. cs81-152-red-py-check.txt: red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-4-green-152", "command": "pwsh -NoProfile -File (task.md row 4's Validation cell: the row-3 files, AC-152.12's unit and service guards, the slot-baseline hash check and the line-ending check); receipts cs81-152-green-ui.txt, cs81-152-green-py.txt, cs81-152-guards-py.txt, cs81-152-eol.txt, cs81-s4-row4.txt", "scope": "MEU-152 Green: CONVERT_TIMECODE, CUT_SEGMENT_TIMECODE, QUEUE_ROW_NUMBER, WAITING_POSITION, CUT_NO_GPU_ENCODER", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 4", "output": "cs81-152-green-ui.txt: Test Files  5 passed (5); Tests  131 passed (131). cs81-152-green-py.txt: 5 passed in 0.35s. cs81-152-guards-py.txt: 8 passed, 28 deselected in 8.14s. cs81-152-eol.txt: line-ending or fixture drift: [] bare LF in convert-controls.ts: 8"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-4a-red-a1", "command": "pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/row4a.ps1 (task.md row 4a's Validation cell: uv run pytest tests/unit/test_convert_output_reserved.py *> C:/Temp/av-kit/convert-settings-drafts/cs81-a1-red-py.txt, its exit code, red-check.py --require with the five titles); receipts cs81-a1-red-py.txt, cs81-a1-red-py-check.txt", "scope": "Amendment A1 Red: AC-152.13 to AC-152.16 and AC-152.18 to AC-152.20 against the row-4 product code", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 4a", "output": "cs81-a1-red-py.txt: 13 failed, 6 passed in 10.55s; exit 1. cs81-a1-red-py-check.txt: red-check: 1 receipt(s), 5 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-4b-green-a1", "command": "pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/row4b.ps1 (task.md row 4b's Validation cell: uv run pytest tests/unit/test_convert_output_reserved.py tests/unit/test_convert_cut_encoder.py tests/unit/test_conversion_service.py tests/e2e/test_api_conversions.py *> C:/Temp/av-kit/convert-settings-drafts/cs81-a1-green-py.txt, then pyright, ruff check, ruff format --check and the line-ending check); receipts cs81-a1-green-py.txt, cs81-a1-ruff.txt, cs81-a1-pyright.txt, cs81-a1-format.txt, cs81-a1-eol.txt", "scope": "Amendment A1 Green: QUEUE_OUTPUT_RESERVED, QUEUE_ADD_SERIAL, ACTIVE_WRITER_RESERVED in services/conversion.py", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 4b", "output": "cs81-a1-green-py.txt: 83 passed in 13.37s. cs81-a1-pyright.txt: 0 errors, 0 warnings, 0 informations. cs81-a1-ruff.txt: All checks passed! cs81-a1-format.txt: 2 files already formatted. cs81-a1-eol.txt: line-ending drift: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-5-electron", "command": "pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/a2-e2e-run.ps1 (task.md row 5's Validation cell: the UI build, then npm --prefix ui run test:e2e -- tests/e2e/capture-settings-draft.test.ts tests/e2e/convert-queue-labels.test.ts three times, with ELECTRON_RUN_AS_NODE unset, then the row-5 check); receipts cs81-row5-build.txt, cs81-row5-e2e-r1.txt, cs81-row5-e2e-r2.txt, cs81-row5-e2e-r3.txt, cs81-row5-verify.txt", "scope": "Row 5 (A2, D-975): AC-152.21 to AC-152.24 and AC-151.14 on the built app with scratch profiles and the real backend, three runs; round 1's words kept", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 5", "output": "cs81-row5-build.txt: built in 13.12s. cs81-row5-e2e-r1.txt: 5 passed (1.1m); cs81-row5-e2e-r2.txt: 5 passed (1.0m); cs81-row5-e2e-r3.txt: 5 passed (1.9m). cs81-row5-verify.txt: runs passing all five: [True, True, True] round 1 kept: True D-975 receipt with no invented pass: True CR in the new Electron files: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-6-8-records", "command": "pwsh -NoProfile -File (task.md rows 6, 7 and 8's Validation cells: the row-6 notes check; issue_triage.py add CONVERT-OUTPUT-NAME-REUSED, issue-resolve.py with the six issues and --expect-sha256, issue_triage.py render and render --check; meu_status.py update MEU-151 and MEU-152 ready_for_review, meu_status.py render, the row-8 check); receipts cs81-notes-check.txt, cs81-issue-add.txt, cs81-issue-resolve.txt, cs81-issues-render.txt, cs81-issues-render-check.txt, cs81-status-151.txt, cs81-status-152.txt, cs81-status-render.txt, cs81-row8-check.txt", "scope": "Rows 6 to 8: the 06 and 08 Delivered notes; the A1 issue added and six issues resolved; both MEUs ready_for_review; grouping row 81 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6b124a (baseline.sha) plus rows 0 to 8", "output": "cs81-notes-check.txt: 06 CRLF: True 08 LF: True notes: 1 1. cs81-issue-add.txt: OK: Added issue 'CONVERT-OUTPUT-NAME-REUSED' to known-issues.yaml. cs81-issue-resolve.txt: issue-resolve: 0 problem(s). cs81-issues-render.txt: Rendered known-issues.md: 49 lines. cs81-issues-render-check.txt: OK: known-issues.md is up-to-date. cs81-status-152.txt: Updated MEU-152 -> ready_for_review (updated: 2026-11-16). cs81-row8-check.txt: row 81 executed (Session 81), grouping LF True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "cs81-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/row-H1-2.ps1 (task.md H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-convert-settings-drafts/session-gate.ps1 *> C:/Temp/av-kit/convert-settings-drafts/cs81-gate-h1.txt, with ELECTRON_RUN_AS_NODE unset); the fifth run, after D-1066, D-1067 and D-1068; receipts cs81-gate-h1.txt and the cs81-D6-*.txt step receipts", "scope": "H1-2 session gate for MEU-151 and MEU-152: identity before and after; pyright, ruff check and format, the UI typecheck and lint, the task contract, scope paths, line endings, the red-check selftest; the MEU-151 UI, MEU-152 UI and MEU-152 Python targeted tests; the full Python suite, the full UI suite and build, the state and issue renders; the Convert, capture and A2 Electron E2E", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509", "output": "cs81-gate-h1.txt: session-gate: all steps exit 0; tested_state before = after (cs81-D6-identity-before.txt, cs81-D6-identity-after.txt). py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; py-format 3 files already formatted; ui-types tsc --noEmit exit 0; ui-lint eslint src/ tests/ --max-warnings 0 exit 0; task-contract OK: 28 row(s), 26 fully checked, 2 view_file exempt (H1-5, H2-1); scope-paths changed paths: 54 outside scope: [], read-never-changed mismatch: [], baseline-dirty hash mismatch: [], head moved (S4): False; line-endings files: 26 mismatch: []; red-check-selftest 45 fixture(s) (15 positive, 30 negative), 0 wrong: []; meu-151-ui Test Files  6 passed (6), Tests  301 passed (301); meu-152-ui Test Files  3 passed (3), Tests  38 passed (38); meu-152-py 83 passed in 79.28s (0:01:19); py-tests (cs81-D6-py-tests.txt) 3032 passed, 37 warnings in 775.02s (0:12:55); ui-tests Test Files  135 passed (135), Tests  1570 passed (1570); ui-build exit 0 (built in 4.32s); state-render Drift check passed (153 MEUs, 12 phases); issues-render-check OK: known-issues.md is up-to-date; ui-electron-convert (convert-queue.test.ts) 23 passed (22.2s); ui-electron-capture (capture-inbox.test.ts W9-3, AC-57.10 header, AC-67.24) 3 passed (4.6s); ui-electron-a2 (capture-settings-draft.test.ts, convert-queue-labels.test.ts) 5 passed (27.2s). Skipped: openapi and mcp-types/mcp-build/mcp-tests/mcp-audit (every packages/api/ and mcp-server/ file keeps its baseline-skip-hashes.json hash, H1-4), build-record (no build), gui-refs-not-shipped (no GUI reference image is shipped for these surfaces)"}
```

### Quality Gate Results

- **Last line** (`cs81-gate-h1.txt`): `session-gate: all steps exit 0`.
- **Identity:** tested_state `b6b124ab3e8882afaf02a7f493a7259237571758+9c4a723cc008d20e80d5b16772dac5f28cf523a36dd173ff9756230062f9b509` before and after the gate (`cs81-D6-identity-before.txt`, `cs81-D6-identity-after.txt`).
- **Static:** pyright `0 errors, 0 warnings, 0 informations`; ruff check `All checks passed!`; ruff format `3 files already formatted`; the UI typecheck and lint exit 0 (`cs81-D6-ui-types.txt`, `cs81-D6-ui-lint.txt`); the task contract `OK: 28 row(s)`, 26 fully checked, 2 view_file exempt (H1-5, H2-1); scope paths `changed paths: 54 outside scope: []`, `read-never-changed mismatch: [] baseline-dirty hash mismatch: []`, `head moved (S4): False`; line endings `line-endings files: 26 mismatch: []`; the red-check selftest `45 fixture(s) (15 positive, 30 negative), 0 wrong: []`.
- **Targeted:** MEU-151 UI `Test Files  6 passed (6)` and `Tests  301 passed (301)` (`cs81-D6-meu-151-ui.txt`); MEU-152 UI `Test Files  3 passed (3)` and `Tests  38 passed (38)` (`cs81-D6-meu-152-ui.txt`); MEU-152 Python `83 passed in 79.28s (0:01:19)` (`cs81-D6-meu-152-py.txt`).
- **Fresh full:** the Python suite `3032 passed, 37 warnings in 775.02s (0:12:55)` (`cs81-D6-py-tests.txt`), which is the row-0 base of 3008 (`cs81-base-py.txt`) plus the 5 cut-encoder and 19 output-reserved cases; the UI suite `Test Files  135 passed (135)` and `Tests  1570 passed (1570)` (`cs81-D6-ui-tests.txt`), which is the row-0 base of 1547 in 133 files (`cs81-base-ui.txt`) plus the 23 new tests and the 2 new files; the UI build exits 0; the state render `Drift check passed` (153 MEUs, 12 phases); the issue render `OK: known-issues.md is up-to-date`.
- **Runtime,** with `ELECTRON_RUN_AS_NODE` unset: `convert-queue.test.ts` unchanged, `23 passed (22.2s)` (`cs81-D6-ui-electron-convert.txt`; `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE`'s AC-97.7 passed); `capture-inbox.test.ts` W9-3, AC-57.10 header and AC-67.24 unchanged, `3 passed (4.6s)` (`cs81-D6-ui-electron-capture.txt`); A2's two files `5 passed (27.2s)` (`cs81-D6-ui-electron-a2.txt`).
- **Skipped, with basis:** `openapi` and `mcp-types`, `mcp-build`, `mcp-tests`, `mcp-audit` (every `packages/api/` and `mcp-server/` file keeps its row-0 hash, H1-4: `packages/api or mcp-server changes since row 0: []`); `build-record` (no build); `gui-refs-not-shipped` (no GUI reference image is shipped for these surfaces).
- **Baseline failures excused:** 0. The first run failed at `ui-tests` (`cs81-gate-h1-run1.txt`, `Tests  4 failed | 1565 passed (1569)`); after D-1066 the gate reran in full and passed (`cs81-gate-h1-run2.txt`, `gate-run2/`). After D-1067 (CS81-R1-F1) the third run failed at `py-tests` on `test_youtube_adapter.py` AC-122.8 (`cs81-gate-h1-run3.txt`, `gate-run3/`: `1 failed, 3031 passed` in 676.19s), and the fourth on `test_tts_assets.py` AC-62.16 (`cs81-gate-h1-run4.txt`, `gate-run4/`: `1 failed, 3031 passed` in 911.43s). Both were 5-second waits under host load, in code this session does not touch; AC-122.8 passed alone three times (`cs81-d1067-py-diag.txt`). Under D-1068 the gate reran in full each time, nothing was registered, and this is the fifth run, made after the host's CPU load was measured at 10%. No step was rerun alone.
- **Processes:** a snapshot before and after the fifth run showed three new processes, all other sessions' (`gate5-procs-compare.txt`); runs 2 to 4 were the same (`gate2-procs-compare.txt`, `gate3-procs-compare.txt`, `gate4-procs-compare.txt`). None was a run's own, and none was touched.
- **After the gate:** H1-3 added the current-focus paragraph (with D-1067 and D-1068 after the fifth run), `task.md` rows were marked and these handoffs were written. `identity.py` excludes all three, so no product, test or tracked record changed after the gate; H1-6b checks that the expected state still equals the gate's.

---

## Changed Files

Counts are added / removed lines against the row-0 copies (`baseline-copies/` in the receipts folder; `git diff --no-index --numstat`), not against `HEAD`, because other sessions' uncommitted work sits in the same tree. Line endings were measured as bytes (the gate's `line-endings` step).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/src/renderer/src/features/converter/convert-time.ts` | `CONVERT_TIME_MAX_MS`, `formatConvertTime` | +21 / -0 | CRLF kept |
| `ui/src/renderer/src/features/converter/convert-controls.ts` | the Cut segment as timecodes; `convertQueuePositions` | +32 / -5 | MIXED kept (8 bare-LF lines unchanged, new lines CRLF) |
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | `waitingPosition` and its text | +12 / -1 | CRLF kept |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | card positions from `convertQueuePositions` (MEU-151's changes are in the same count) | +28 / -30 | CRLF kept |
| `packages/core/src/avkit_core/services/conversion.py` | `CUT_NO_GPU_ENCODER`; A1's three contracts | +74 / -29 | CRLF kept |
| `ui/tests/unit/convert-queue-labels.test.ts` | new: AC-152.1 to AC-152.8 | +191 (new) | LF |
| `ui/tests/unit/convert-controls.test.ts` | the AC-152.3 pin (AC-45.17) | +1 / -1 | CRLF kept |
| `ui/tests/unit/convert-page.behavior.test.ts` | AC-152.9 (MEU-151's tests are in the same count) | +134 / -2 | CRLF kept |
| `tests/unit/test_convert_cut_encoder.py` | new: AC-152.10, AC-152.11 | +127 (new) | LF |
| `tests/unit/test_convert_output_reserved.py` | new (A1): AC-152.13 to AC-152.16, AC-152.18 to AC-152.20 | +417 (new) | LF |
| `ui/tests/e2e/convert-queue-labels.test.ts` | new (A2): AC-152.21 to AC-152.24; the `_app` parameter (D-1066) | +562 (new) | LF |
| `docs/build-plan/08-video-conversion.md` | the Delivered (Session 81) note | +8 / -0 | LF kept |

The shared records (`known-issues.yaml` and `.md`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, the grouping file, `current-focus.md`) and MEU-151's files are listed in the MEU-151 handoff. `tests/unit/test_conversion_service.py`, `ui/tests/unit/fixtures/queue-slot-baseline.json`, `ui/tests/e2e/convert-queue.test.ts` and `ui/tests/e2e/capture-inbox.test.ts` were read, never changed (the gate's `scope-paths`: `read-never-changed mismatch: []`). Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Finding | Fix | Status |
|---|----------|----------|---------|-----|--------|

### Verdict

Pending: the H1-7 execution review (ledger loop `cs81-execution-2026-11-15-convert-settings-drafts`) has not run.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Downloader and Transcript cards print the stored 0-based position | residual for triage | none | Plan §Out of Scope; D-971 |
| Downloader and TTS output names not checked for reuse | residual for triage | none | Plan §Out of Scope; D-1063 |
| Remove and Clear do not stop a running media call | out-of-scope | none | Plan §Out of Scope; D-1065 |
| Stored rows that already share a path, and stored Cut `gpu_encoder` values | out-of-scope | none | Plan §Out of Scope; D-1061, D-968 |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

### Departures and their basis

- **A1 and A2 were added mid-execution** on Mat's words (D-1060, D-975), each amending the plan in place. A1 went through its own plan review first; A2 has no separate round, and the H1-7 review covers it.
- **No Red for AC-152.21 to AC-152.24** (above). In A2's first run AC-152.22 failed on the test's own expectation (it named the second job next while the first still waited); the expectation was corrected before any pass, with no product change.
- **Bounded waits and r2.** Of the three runs that followed, r2 failed: AC-152.21 hit the 240 s test timeout on a loaded machine and the worker its 60 s teardown timeout; nothing it launched was left running. Every child run, backend request and app close then got its own time limit and a timed `[s81-e2e]` line, an afterEach closes an app a timed-out test left open, and a close that hangs kills the Electron process through its own handle. r3's close hung once and was killed that way. A possible `app.close` hang may deserve its own issue; none was registered.
- **Test seams (D-976).** The A2 file answers the native folder dialog through the app's IPC seam and cleans the spawned backend up by its own pid. In the first gate the file's `app.evaluate` callback named its parameter `_electron`, which `e2e-harness.test.ts` AC-2 counts as a second launcher; it is now `_app` (D-1066), and nothing the test checks changed.
- **`_run_one` re-indent.** `ACTIVE_WRITER_RESERVED`'s `try`/`finally` re-indents `_run_one`'s body, so the `conversion.py` count includes moved lines; the new parameters have keyword defaults, and the file was formatted with `ruff format` (`cs81-a1-format.txt`: `2 files already formatted`).
- **`CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE`.** That registered flake in `convert-queue.test.ts` did not fire in the gate; it is not this session's.
- **Execution decisions** D-973 to D-976 and D-1066 to D-1068 are in the plan's decision YAML, and D-1060's precedent and Refs point at `cs81-human-check-r1.txt`. So the Decision Log below is `None.`.
- **The first gate failed** (`cs81-gate-h1-run1.txt`); see the MEU-151 handoff. The gate then reran in full.
- **Gate runs 3 and 4 (D-1068).** After D-1067 (CS81-R1-F1, a MEU-151 fix) the gate reran in full. The third run failed at `py-tests` on `test_youtube_adapter.py` AC-122.8 and the fourth on `test_tts_assets.py` AC-62.16, each a 5-second wait under host load in code this session does not touch (`cs81-gate-h1-run3.txt`, `gate-run3/`, `cs81-gate-h1-run4.txt`, `gate-run4/`). Nothing was registered here, and the fifth run, made after the host's CPU load was measured at 10%, passed; it is the gate recorded above. See the MEU-151 handoff.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-16 | claude-code-local (Claude Opus 5.5) | Initial MEU-152 handoff after the H1-2 gate rerun (D-1066), H1-3 and H1-4 |
| Updated | 2026-11-17 | claude-code-local (Claude Opus 5.5) | D-1068: the gate record and results moved to the fifth run, after D-1067; runs 3 and 4 disclosed; H1-3 to H1-6b rerun |
