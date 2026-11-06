---
date: "2026-11-06"
project: "transcript-failure-reason"
meu: "MEU-116"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-05-transcript-failure-reason-MEU-115-handoff.md"
---

# Handoff: 2026-11-05-transcript-failure-reason-MEU-116-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-116 `svc-transcript-block-stop` (`TRANSCRIPT-BLOCK-KEEPS-REQUESTING`). A YouTube block that outlasts its retries pauses the job, with the blocked message, before any request is made for the next video. `transcript.requests_per_hour` is now enforced.
**Build Plan Section**: [03 §Transcript block stop (residual)](../../../docs/build-plan/03-service-layer.md).
**Predecessor**: the [MEU-115 handoff](2026-11-05-transcript-failure-reason-MEU-115-handoff.md), whose messages and Console lines this MEU uses.

- **Block stop (rows 8, 9; D-299).**
  - `_fetch_item` (`services/transcript.py:535`) returns True when a block outlasts `max_retries`. The video stays `Pending` with `retry_count` 0 and the blocked message, and one `transcript.blocked` ERROR line is logged (`:555`).
  - `_run_parent` (`:452`) then sets the pause and calls `_pause_parent(job.id, failure_message(blocked))` (`:692`) in one `_lock` section, and returns. So no request is made for this job's next video or any other job's.
  - `resume_processing` (`:226`) clears the job's `error_message` and starts the run again from the same video.
- **Rate cap (D-300).** `_await_request_slot` (`:621`) runs before every `get_transcript` call, retries included.
  - It reads `transcript.requests_per_hour` on each pass, and 0 turns the cap off. It drops request starts older than `RATE_WINDOW` (3600 s) on the injected `clock` (`:98`, default `time.monotonic`).
  - At the cap it sleeps in slices of at most a second, and Stop or Pause ends the wait. With the defaults and no retries it delays nothing.
- **One worker (D-306).**
  - `start_processing`, `resume_processing` and `stop_processing` check for a live worker under `_lock`. Each worker exit re-checks its flag in the same lock and marks the worker gone (`_worker_active`).
  - `_next_job` (`:433`) reads and clears the resume's pick-Processing flag under the lock. So a resume racing the worker's exit leaves exactly one worker.
- **Spec text.** 03's worker loop, One item step 3, the Resume, One worker and Rate cap paragraphs, and the MEU-116 Delivered note (rows 9, 10).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md) §MEU-116. **Execution authorization:** `USER_EXPLICIT`, 2026-11-06, "Go-ahead", given after the Codex plan review approved in round 2 (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-116.1 | unit | With `max_retries` 3 and a port that blocks every call, the first video gets exactly 3 calls and the second none. The job reads `Paused` with the blocked message, every item is `Pending`, the first has `retry_count` 0 and the message, and the runtime is `Paused`. | Research-backed (triage D-219) | `tests/unit/test_services.py:2916` | ✅ |
| AC-116.2 | unit | After AC-116.1, with the port answering, `resume_processing` finishes the job Done, and the job's and items' `error_message` are `None`. | Local Canon (03, "Resume") | `tests/unit/test_services.py:2937` | ✅ |
| AC-116.3 | unit | A `DomainError` on the first video fails it, and the second video is still requested. A guard: it passes in Red by design. | Local Canon (03, "Other failures") | `tests/unit/test_services.py:2953` | ✅ |
| AC-116.4 | unit | On the fake clock with the cap at 2, the third request waits until the first is an hour old. A retry counts as a request, and a cap of 0 never waits. A cap lowered between two requests is read for the second. During a wait, Stop or Pause takes effect within one slice, and a cap raised above the count or set to 0 ends the wait at the next slice. | Local Canon (triage D-220) | `tests/unit/test_services.py:2981`, `:2988`, `:2998`, `:3005`, `:3018` (`pause`, `stop`), `:2988` | ✅ |
| AC-116.5 | unit | With default settings, no retries and 400 videos on the fake clock, nothing sleeps beyond the delay and batch sleeps. A guard: it passes in Red by design. | Local Canon (03, "Default behaviour doesn't change") | `tests/unit/test_services.py:3066` | ✅ |
| AC-116.6 | unit | The amended AC-11.6 expects an exhausted block to leave the item Pending and the job Paused. The amended AC-11.8 makes its item fail with a `DomainError` and still skips the zip. | Local Canon (03, "Stop on block") | `tests/unit/test_services.py:1330` (AC-11.6), `:1370` (AC-11.8) | ✅ |
| AC-116.7 | integration | `DONE_TEST`: a real `HealthService` (`tmp_path`, `app.log_to_file` off) and `TranscriptService` with a blocking fake port. `_job_out` shows `Paused` with the blocked message. The ring has an ERROR `transcript.blocked` line with the message, and `console.log` has that line. | Human-approved (Mat's brief, "Done means…") | `tests/integration/test_transcript_block_done.py:14` | ✅ |
| AC-116.8 | unit | A resume that races the worker still finishes the job (D-306): (a) held after the job is published Paused, before `_run_parent` returns; (b) held at the `_sleep(0)` after it. Every video and the job end Done, the runtime ends Idle, and at most one worker ran at once. The barriers have timeouts. | Local Canon (03, "Resume"; review F4) | `tests/unit/test_services.py:3135`, `:3165` | ✅ |
| AC-116.9 | unit | With default settings, 400 videos and one retry on the first, the cap waits before the 301st start. No window of 3600 s, open at its left end, holds more than 300 of the recorded starts. | Local Canon (triage D-220; review F5) | `tests/unit/test_services.py:3072` | ✅ |
| AC-11 (cross-ref) | regression | AC-11.6 and AC-11.8 are amended under AC-116.6 (above). AC-11.1 to AC-11.10 pass in the gate | plan §User Review Required | `tests/unit/test_services.py` (gate `py-tests`) | ✅ |
| AC-115 (cross-ref) | — | Owned by the MEU-115 handoff (the failure reason, the API field, the Console rider and the card). Row 8 migrated the exhausted-block subcases of AC-115.5 and AC-115.7 to Pending and `transcript.blocked` | plan §MEU-115 | [MEU-115 handoff](2026-11-05-transcript-failure-reason-MEU-115-handoff.md); `tests/unit/test_services.py:2477`, `:2543` | see MEU-115 |
| AC-7 (cross-ref) | regression | AC-7.4 is amended under AC-115.2, owned by the MEU-115 handoff | plan §MEU-115 | `tests/integration/test_transcript_adapter.py:171` (gate `py-tests`) | see MEU-115 |
| AC-21 (cross-ref) | regression | AC-21.16 registers the `job-message` test id, owned by the MEU-115 handoff | plan §MEU-115 | `ui/tests/unit/transcript-page.test.ts` (gate `ui-tests`) | see MEU-115 |
| AC-23 (cross-ref) | regression | AC-23.16 still passes with the new `blocked` help section, owned by the MEU-115 handoff | plan §Transcript help | `ui/tests/unit/help-card.test.ts:93` (gate `ui-tests`) | see MEU-115 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-116.1, AC-116.2, AC-116.6, AC-116.7, AC-116.8 | Row 8: the second video is requested and the job ends Failed. `transcript.item_failed` lines for `first` and `second` appear, and `assert (out["status"], out["error_message"]) == ("Paused", blocked)` fails | Row 9: pass | `test_services.py:1330`, `:1370`, `:2916`, `:2937`, `:3135`, `:3165`; `test_transcript_block_done.py:14` |
| AC-116.4, AC-116.9 | Row 8: no request waits, and `clock` is not a parameter | Row 9: pass | `test_services.py:2981-3023` |
| AC-116.3, AC-116.5 | Guards: they pass in Red by design | Row 9: pass | `test_services.py:2953`, `:3066` |
| AC-115.5, AC-115.7 block subcases | Row 8: the exhausted block still reads Failed and logs `transcript.item_failed` | Row 9: pass | `test_services.py:2477`, `:2543` |

- **Row 8 Red:** 17 failed, 3 passed and 79 deselected. The 3 passes are the guards.
- `red-check.py` required 7 tests and found 0 problems. Every failure is the decisive assertion.
- **Row 9 Green:** it runs `test_services.py`, the done test, the adapter tests and the API tests in full. 113 passed, pyright reported 0 errors, and the real `console.log` was unchanged.

Receipts: `C:/Temp/av-kit/s50-block-red.txt` (with `.exit`), `s50-block-red-check.txt`, `s50-block-green.txt`, `s50-block-types.txt`, `s50-resolve.txt`, `s50-r10-*.txt`, the gate's `s50-gate-h1.txt` and `s50-D6-<id>.txt`, and `drift-check.txt` and `openapi-check.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s50-116-block-red", "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/integration/test_transcript_block_done.py -k \"ac_116_ or ac_11_6 or ac_11_8 or ac_115_5 or ac_115_7\" --tb=short -q *> C:/Temp/av-kit/s50-block-red.txt; then red-check.py --require on seven tests (task.md row 8 Validation cell, verbatim, from P:/av-kit, TMP and TEMP at C:/Temp/av-kit/s50/tmp)", "cwd": "P:/av-kit", "scope": "MEU-116 Red: AC-116.1 to AC-116.9, the amended AC-11.6 and AC-11.8, and the migrated block subcases of AC-115.5 and AC-115.7, against the run loop before the block stop", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb (baseline.sha) plus rows 1 to 8", "output": "17 failed, 3 passed, 79 deselected in 3.09s. The passes are the guards AC-116.3 and AC-116.5. Decisive, e.g. assert (out['status'], out['error_message']) == ('Paused', blocked), with transcript.item_failed logged for first and second. red-check: 1 receipt(s), 7 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-116-block-green", "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/integration/test_transcript_block_done.py tests/integration/test_transcript_adapter.py tests/e2e/test_api_transcripts.py --tb=short -q *> C:/Temp/av-kit/s50-block-green.txt, then pyright and real-log-check.py --compare (task.md row 9 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-116 Green: the block stop, the rate cap and one worker, over the whole service, adapter and API transcript suites", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 to 9", "output": "113 passed in 7.96s. pyright 0 errors. Real console.log unchanged."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-row10-hub", "command": "pwsh -NoProfile -File row-10.ps1 (task.md row 10 Validation cell, verbatim, from P:/av-kit): the issue-resolve receipt, meu_status.py render --check, issue_triage.py render --check, the issue statuses and the grouping row", "cwd": "P:/av-kit", "scope": "Row 10 hub, shared by MEU-115 and MEU-116: the 03 Delivered notes, both MEUs ready_for_review, the three issues resolved through issue-resolve.py and YOUTUBE-CAPTIONS-IP-BLOCK left open, and grouping row 50 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 to 10", "output": "issue-resolve: 9 parsed fields changed (issues[101..103] status, verification, resolution_path), 67 of 67 decision logs read, 0 problem(s). Drift check passed. Issue renders match. Statuses TRANSCRIPT-FAILED-NO-REASON resolved, TRANSCRIPT-BLOCK-KEEPS-REQUESTING resolved, CONSOLE-FAILURE-DETAIL-LOST resolved, YOUTUBE-CAPTIONS-IP-BLOCK open. Grouping row 50 names the plan."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-05-transcript-failure-reason/session-gate.ps1 *> C:/Temp/av-kit/s50-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s50-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 10 and the review round 1 corrections (run 3; run 2, s50-gate-h1-run2.txt, is the gate round 1 reviewed): identity, every static check, both full suites, the UI build, OpenAPI, the MCP types and tests, both renders, the targeted Electron specs and the real-log check, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "097e0bbcf196fdf0896d4f2e5159be03f69aa62a+ed48a1410419a8b320b81f0210ffff82c44b60427f4423224e82f613c4d3b14b", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (27 rows, 25 fully checked, 2 view_file exempt); scope-paths exit=0 (changed paths: 58, outside scope: [], head moved: False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1265 passed); ui-tests exit=0 (109 files, 1144 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-tests exit=0 (34 files, 466 passed); state-render exit=0 (126 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ui-electron exit=0 (40 passed); real-log-untouched exit=0 (real console.log unchanged); identity-after exit=0 (tested_state before = after); mcp-build, mcp-audit and build-record skipped; baseline failures excused: none; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "097e0bbcf196fdf0896d4f2e5159be03f69aa62a+ed48a1410419a8b320b81f0210ffff82c44b60427f4423224e82f613c4d3b14b", "output": "Drift check passed: SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-h1-4-openapi", "command": "rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt", "cwd": "P:/av-kit", "scope": "H1-4: packages/api changed in this session, so the committed OpenAPI document is checked against the app", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "097e0bbcf196fdf0896d4f2e5159be03f69aa62a+ed48a1410419a8b320b81f0210ffff82c44b60427f4423224e82f613c4d3b14b", "output": "exit 0; check_openapi prints nothing when openapi.committed.json matches the live schema"}
```

### Quality Gate Results

`s50-gate-h1-2` is the fresh full record, shared with MEU-115, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors, 0 warnings; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 27 rows; scope-paths found 58 changed paths, none outside scope, and HEAD 097e0bb did not move; the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** pytest 1265 passed; Vitest 1144 passed in 109 files; MCP tests 466 passed in 34 files. No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check and the MCP typecheck exited 0; the state render and the issue render match the files on disk.
- **Runtime:** the targeted Electron specs passed (40 of 40), and the real `%LOCALAPPDATA%\av-kit\logs\console.log` was unchanged.
- **Skipped:** `mcp-build` (no MCP source change), `mcp-audit` (live network and YouTube, which the brief forbids) and `build-record` (no installer build).
- **Identity:** the tested_state was the same before and after the gate: `097e0bbcf196fdf0896d4f2e5159be03f69aa62a+ed48a1410419a8b320b81f0210ffff82c44b60427f4423224e82f613c4d3b14b`.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/transcript.py` | modified | `RATE_WINDOW`, the `clock` parameter, `_request_starts`, `_await_request_slot`, `_fetch_item` returning the block, the block pause in `_run_parent`, `_pause_parent(reason)`, Resume clearing the message, `_worker_active` and the exits, entry points and `_next_job` under `_lock`. Shared with MEU-115 |
| `tests/unit/test_services.py` | modified | AC-116.1 to AC-116.6, AC-116.8, AC-116.9; AC-11.6 and AC-11.8 amended; the AC-115.5 and AC-115.7 block subcases migrated |
| `tests/integration/test_transcript_block_done.py` | new | AC-116.7 |
| `docs/build-plan/03-service-layer.md` | modified | The worker loop, One item step 3, the Resume, One worker and Rate cap paragraphs, and the Delivered note. CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml`, the grouping file, `current-focus.md` and the plan folder | modified or new | Shared with MEU-115; listed in its handoff |

```diff
-            self._fetch_item(job.id, item)
+            if self._fetch_item(job.id, item):
+                # A block that outlasted its retries stops the run: no request for the next
+                # video of this job or any other until Resume (MEU-116). Under `_lock`, so a
+                # Resume either lands after this pause or finds the job still Processing.
+                with self._lock:
+                    self._pause = True
+                    self._pause_parent(job.id, failure_message(TranscriptFailureCause.blocked))
+                return
```

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | Round 1 raised nothing against MEU-116. Its two findings, F1 and F2, are in `health.py` and are MEU-115's (see the MEU-115 handoff) | — | — | — |

### Verdict

Round 1 of loop `s50-execution-2026-11-05-transcript-failure-reason` returned `changes_required` on MEU-115's F1 and F2 ([implementation-critical-review.md](2026-11-05-transcript-failure-reason-implementation-critical-review.md)). It accepted the block stop, the resume race, the rate cap and their tests. Both findings were corrected, and round 2 returned `approved`, intent achieved `yes`, with no new findings.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `YOUTUBE-CAPTIONS-IP-BLOCK`, the block itself | out-of-scope | — | Upstream; this MEU changes only how av-kit stops on one. The issue stays open |
| A growing wait or a new setting for blocks | out-of-scope | — | 03 §Transcript block stop: "No growing wait and no new number" |
| Commit and push | out-of-scope | — | Waits for Mat's direction (H2-5) |

**Execution notes.**
- **D-306 and `_thread`.** D-306 uses a `_worker_active` flag under `_lock` rather than setting `self._thread = None` at each exit. 39 existing tests read `service._thread` twice (`if service._thread is not None: service._thread.join(...)`), so clearing it from the worker would race them. The exit rule is otherwise as planned, and a `finally` clears the flag on an exception exit.
- **Pause and Resume.** The block pause sets `_pause` and calls `_pause_parent` inside one `_lock` section, so a concurrent Resume lands either before or after the whole pause.
- **Name.** The rate-cap helper is named `_await_request_slot`.
- **Row 8 rename.** The parametrized test was renamed to `test_ac_116_4_stop_or_pause_ends_a_cap_wait`, with ids `pause` and `stop`. With the longer name, pytest printed a single-underscore failure header that `red-check.py`'s `^_{3,}` pattern could not read.
- **S8 checkpoint.** After row 7, context use was above half. Mat ruled that the session continues, so rows 8 and 9 ran in Session 50 rather than a Session 50b.
- **Review round 1 layout.** `ruff format` showed that this session's AC-116.4 signature wasn't laid out to it, so the signature now sits on one line. The test is unchanged.
- **Gate run 3.** The whole gate ran again after MEU-115's round 1 corrections, and `s50-gate-h1-2` is that run.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Initial MEU-116 handoff after H1-2 |
| Updated | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Review round 1 result, the line citations moved by the new tests, the gate rerun (run 3) |
| Reviewed | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 2 `approved`, from the canonical report |
