---
date: "2026-11-06"
project: "transcript-failure-reason"
meu: "MEU-115"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-05-transcript-failure-reason-MEU-115-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-115 `svc-transcript-failure-reason` (`TRANSCRIPT-FAILED-NO-REASON`, with the rider `CONSOLE-FAILURE-DETAIL-LOST`). Every transcript failure or skip now carries one short av-kit message, and that message reaches the API, the job card, the Console and `console.log`.
**Build Plan Section**: [03 §Transcript failure reason (residual)](../../../docs/build-plan/03-service-layer.md).
**Predecessor**: none. The [MEU-116 handoff](2026-11-05-transcript-failure-reason-MEU-116-handoff.md) is the same plan's other MEU.

- **Port and adapter (rows 1, 2; D-291).** A skip is a `TranscriptSkip` with cause `no_captions` or `unavailable` (`domain/transcript.py:191`), not `None`. A block raises `TranscriptRetryableError("caption request blocked")` (`adapter.py:30`), and every other library error raises `DomainError` with a short reason from `LIBRARY_REASONS` (`adapter.py:34`) or the class name only. The library's text never leaves the adapter, and `__cause__` is kept.
- **Messages (D-292).** `failure_message` (`domain/transcript.py:204`) writes the four user texts in one place. `safe_reason` (`:224`) keeps an other reason to its first line, with links replaced by "[link]", cut to `REASON_LIMIT` (200). The service runs `redact_message` before it.
- **Service (rows 3, 4; D-295).** Each skip and failure stores its message on the item and logs one `transcript.item_skipped` WARNING (with `persist=True`) or `transcript.item_failed` ERROR with `job_id`, `video_id` and `error=`. A Failed job stores `JOB_MESSAGE`, and a Done job with a skip stores `SKIPPED_JOB_MESSAGE`.
- **API (D-293).** `TranscriptJobOut` gains `last_item_message` (`schemas/transcripts.py:36`), set only when the latest item is Failed or Skipped, and `_job_out` passes the job's `error_message` (`routes/transcripts.py:55`). `openapi.committed.json` was regenerated, with this field as the only addition.
- **Console rider (D-296 to D-298, D-304, D-305; Mat's ruling D-247).**
  - `CONSOLE_FIELDS` (`health.py:47`) keeps `job_id`, `video_id`, `variant_id`, `device`, `error`, `detail`, `request_id` and `route`. `console_field` (`:93`) makes each value one redacted line of at most `FIELD_LIMIT` (300) characters.
  - The event handed to stdout holds only the safe message and `seq`, so no traceback or raw field is printed.
  - ERROR and CRITICAL lines (`PERSIST_LEVELS`, `:60`) and any line with `persist=True` (`PERSIST_FIELD`, `:62`) always reach `console.log`. The toggle adds the rest. `exception` reads ERROR (`LEVEL_ALIASES`, `:64`).
  - A failed append never raises (`_append_console_log`, `:210`). A thread-local guard (`:131`) replaces the shared busy flag, so a second thread's line is no longer dropped.
  - `tts.load_failed` carries `detail=` (`tts/adapter.py:133`).
  - **Review round 1 corrections (D-307, D-308).** `redact_message` (`:73`) maps each case-folded position back to the original character it came from (`:81`), so a prefix that folds longer, such as "ß", no longer moves the cut past the secret (F2). `_ensure_processor` (`:136`) inserts the Console processor right after `merge_contextvars` (`:144`), so a request's bound `request_id` is in the event before the safe message is built, and it shows as a kept Console field, redacted (F1).
- **Renderer (rows 5 to 7; D-294).** The card's line three shows `job-message` for a Failed, Paused or Done job with `error_message` (`TranscriptPage.tsx:116-126`), and while Processing the latest item's message replaces the last title. The transcript help gains a `blocked` section, and the Settings hint, the Settings help and the Console panel say errors always go to the file.
- **Spec text.** 01, 02, 03, 04, 06, 07 and 11 were updated as §Spec text lists. 03 gained the MEU-115 Delivered note (row 10).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md) §MEU-115. **Execution authorization:** `USER_EXPLICIT`, 2026-11-06, "Go-ahead", given after the Codex plan review approved in round 2 (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-115.1 | unit | `failure_message` returns the four texts exactly, and "Couldn't get captions." with no reason. `TranscriptSkip` refuses `blocked` and `other`. `safe_reason` keeps the first line, turns each URL into "[link]" and cuts to `REASON_LIMIT`. | Local Canon (triage D-218) | `tests/unit/test_domain.py:1591` | ✅ |
| AC-115.2 | integration | The adapter returns a no-captions skip for `TranscriptsDisabled`, `NoTranscriptFound` and an empty listing, and an unavailable skip for `VideoUnavailable`. AC-7.4 is amended to match. | Local Canon (03, "Port") | `tests/integration/test_transcript_adapter.py:315`; amended AC-7.4 at `:171` | ✅ |
| AC-115.3 | integration | `RequestBlocked` and `IpBlocked` raise `TranscriptRetryableError("caption request blocked")` with the library error as `__cause__`. | Local Canon (triage D-218) | `tests/integration/test_transcript_adapter.py:349` | ✅ |
| AC-115.4 | integration | Each `LIBRARY_REASONS` class gives its reason, another library class its class name, and a non-library error its class name with none of its text (the `requests.ConnectionError` token URL gives "ConnectionError"). `__cause__` is kept. | Local Canon (triage D-218) | `tests/integration/test_transcript_adapter.py:366` | ✅ |
| AC-115.5 | unit | `_fetch_item` stores the message on each Skipped and Failed item; the item outcomes are as planned. The exhausted-block subcase was migrated in row 8 to Pending, as MEU-116 rules. | Local Canon (triage D-218) | `tests/unit/test_services.py:2477` | ✅ |
| AC-115.6 | unit | A Failed job stores `JOB_MESSAGE` with the right count, total and last message. A Done job with a Skipped item stores `SKIPPED_JOB_MESSAGE`, and one without keeps `None`. | Local Canon (03, "API") | `tests/unit/test_services.py:2513` | ✅ |
| AC-115.7 | unit | Each skip logs one `transcript.item_skipped` WARNING, each failure one `transcript.item_failed` ERROR, each with `job_id`, `video_id` and `error=`. A retry logs nothing. The block subcase now logs `transcript.blocked` (row 8). | Local Canon (03, "Log") | `tests/unit/test_services.py:2543` | ✅ |
| AC-115.8 | e2e | `GET /transcripts` returns `last_item_message` for a latest item that is Failed or Skipped, `None` for Pending or Done, and the job's `error_message`. The `openapi` check passes with this field as the only addition. | Local Canon (03, "API"; 04) | `tests/e2e/test_api_transcripts.py:109`; gate `openapi` | ✅ |
| AC-115.9 | unit | The Console message carries `CONSOLE_FIELDS` in order. A multi-line value becomes one line, and one over `FIELD_LIMIT` is cut. `tts.load_failed` carries `variant_id`, `device`, `error` and `detail`. | Local Canon (`CONSOLE-FAILURE-DETAIL-LOST`) | `tests/unit/test_services.py:2639`; `tests/integration/test_tts_device_resolution.py:890` | ✅ |
| AC-115.10 | unit | Through the production wiring, a secret in a kept field or an unkept field reaches none of the ring, the complete captured stdout or `console.log`. Every stdout line holds only `event` and `seq`. A prefix that case-folds longer still redacts, and a context-bound value reaches no stdout line raw (review round 1, F1 and F2). | Local Canon (`CONSOLE-FAILURE-DETAIL-LOST`) | `tests/unit/test_services.py:2684`, `:2746`, `:2755` | ✅ |
| AC-115.11 | unit | With `app.log_to_file` off, an ERROR line, an `exception` line and a WARNING line with `persist=True` reach `console.log`, and a plain WARNING and an INFO line don't. `exception` reads ERROR, and `persist` appears in no message. | Human-approved (D-247) | `tests/unit/test_services.py:2792` | ✅ |
| AC-115.12 | unit | An `OSError` from the append doesn't reach the caller, and the ring and stdout have the line. | Local Canon (D-296) | `tests/unit/test_services.py:2826` | ✅ |
| AC-115.13 | unit | Two threads log at once, the first held in processing, and both lines reach the ring. | Local Canon (D-298) | `tests/unit/test_services.py:2844` | ✅ |
| AC-115.14 | unit | `job-message` shows on a Failed, Paused and Done card with `error_message`, with no `output-tree`. A Processing card shows `last_item_message` in `last-title`, also when `last_title` is null. A Done card without a message is unchanged. | Local Canon (03, "Card"; D-294) | `ui/tests/unit/transcript-page.behavior.test.ts:561`; test id in `ui/tests/unit/transcript-page.test.ts` (AC-21.16) | ✅ |
| AC-115.15 | unit | The Settings hint, the Settings help and the Console panel say errors always go to the file. | Human-approved (D-247) | `ui/tests/unit/failure-reason-copy.test.ts:22` | ✅ |
| AC-115.16 | unit | The transcript help has a `blocked` section, after `rate`, saying the job pauses and Resume tries again. | Local Canon (triage D-218) | `ui/tests/unit/failure-reason-copy.test.ts:39` | ✅ |
| AC-115.17 | e2e | In Electron, through the transcript seam, a Failed job with `error_message` shows `job-message` with the text. | Local Canon (E2) | `ui/tests/e2e/transcript-queue.test.ts:636` (row 7; gate `ui-electron`) | ✅ |
| AC-115.18 | integration | `DELIVERY_TEST`: a real `HealthService` (toggle off) and `TranscriptService` run a one-video job that skips. The job reads Done with "1 of 1 videos had no transcript. Last: No captions for this video." and `last_item_message` "No captions for this video.". The ring has the WARNING `transcript.item_skipped` line, and `console.log` has it too. | Local Canon (triage D-218; goal anchor) | `tests/integration/test_transcript_failure_delivery.py:99` | ✅ |
| AC-115.19 | integration | `DELIVERY_TEST`, no secret end to end. The real adapter with a token URL in a `requests.ConnectionError`, and a `FakeCaptions` `DomainError` holding a token URL and a bearer, leave no marker in any item, `_job_out`, the ring, the complete stdout or `console.log`. So does a bearer after 64 "ß" (review round 1, F2). | Local Canon (triage D-218; `CONSOLE-FAILURE-DETAIL-LOST`) | `tests/integration/test_transcript_failure_delivery.py:125`, `:157` | ✅ |
| AC-7 (cross-ref) | regression | AC-7.4 is amended under AC-115.2: renamed `test_ac_7_4_disabled_missing_unavailable_return_typed_skips`, it expects typed skips, not `None`. AC-7.1 to AC-7.8 pass in the gate | plan §User Review Required | `tests/integration/test_transcript_adapter.py:171` (gate `py-tests`) | ✅ |
| AC-21 (cross-ref) | regression | AC-21.16 registers the new `job-message` test id on the page and in `test-ids.ts` | plan §Files Modified | `ui/tests/unit/transcript-page.test.ts` (gate `ui-tests`) | ✅ |
| AC-23 (cross-ref) | regression | AC-23.16 still passes: the transcript help gains a `blocked` section after `rate` and keeps every existing topic | plan §Transcript help | `ui/tests/unit/help-card.test.ts:93` (gate `ui-tests`) | ✅ |
| AC-116 (cross-ref) | — | Owned by the MEU-116 handoff (the block stop and the rate cap), which also carries the amended AC-11.6 and AC-11.8 under AC-116.6 | plan §MEU-116 | [MEU-116 handoff](2026-11-05-transcript-failure-reason-MEU-116-handoff.md) | see MEU-116 |
| AC-11 (cross-ref) | regression | AC-11.6 and AC-11.8 are amended under AC-116.6, owned by the MEU-116 handoff | plan §MEU-116 | `tests/unit/test_services.py:1330`, `:1370` (gate `py-tests`) | see MEU-116 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-115.1 to AC-115.4, amended AC-7.4 | Row 1: the new names are missing from the domain and the adapter, and the four library errors return `None` or the library's text | Row 2: pass | `test_domain.py:1591`, `test_transcript_adapter.py:171`, `:315-366` |
| AC-115.5 to AC-115.13, AC-115.18, AC-115.19 | Row 3: the items store `None` or raw text, nothing is logged, `video_id`, `device` and `detail` are dropped (`assert details(logs) == [(variant.id, "cpu", "RuntimeError", "cpu move failed")]`), and nothing reaches `console.log` with the toggle off | Row 4: pass | `test_services.py:2477-2793`, `test_tts_device_resolution.py:890`, `test_transcript_failure_delivery.py:99`, `:125` |
| AC-115.14 to AC-115.16, AC-21.16 | Row 5: no `job-message` element or test id, the old log-file copy, no `blocked` help section | Row 6: pass | `transcript-page.behavior.test.ts:561`, `failure-reason-copy.test.ts:22`, `:39` |
| AC-115.17 | No Red of its own: its negative is row 5's AC-115.14 Red | Row 7: pass in Electron | `transcript-queue.test.ts:636` |
| AC-115.10, AC-115.19 (review round 1, F1 and F2) | The bearer after a folding prefix is kept (`assert redact_message(secret) == prefix + " [REDACTED]"` fails), and stdout prints `request_id='Bearer SYNTHETIC_CONTEXT_MARKER'` | Pass after D-307 and D-308 | `test_services.py:2746`, `:2755`, `test_transcript_failure_delivery.py:157` |

- **Row 1 Red:** 5 failed and 58 deselected. `red-check.py` required 5 tests and found 0 problems.
- **Row 3 Red:** 12 failed and 107 deselected. `red-check.py` required 11 tests and found 0 problems.
- **Row 5 Red:** 4 failed and 38 passed in 3 files. `red-check.py` required AC-115.14 to AC-115.16 and found 0 problems.
- **Review round 1 corrections Red:** 5 failed and 100 deselected, each by assertion. `red-check.py` required 3 tests and found 0 problems.
- Every failure is the decisive assertion, never a collection or import error, because each test first asserts that the new name exists.
- **Green:**
  - Row 2: 78 passed.
  - Row 4: 187 passed, over the Console, TTS and API suites as well.
  - Row 6: 8 files, 116 passed.
  - Row 7: the UI build, then 11 of 11 Electron E2E tests in `transcript-queue`.
  - Rows 2, 4, 7 and 9 each confirmed that the real `console.log` was unchanged.
  - Review round 1 corrections: 203 passed over the transcript, Console, TTS and API suites, and pyright found 0 errors in `health.py`.

Receipts: `C:/Temp/av-kit/s50-port-red.txt` (with `.exit`), `s50-port-red-check.txt`, `s50-port-green.txt`, `s50-svc-red.txt` (with `.exit`), `s50-svc-red-check.txt`, `s50-svc-green.txt`, `s50-ui-red.txt` (with `.exit`), `s50-ui-red-check.txt`, `s50-ui-green.txt`, `s50-r7-build.txt`, `s50-r7-e2e.txt`, `s50-resolve.txt`, `s50-r10-*.txt`, `s50-f12-red.txt` (with `.exit`), `s50-f12-red-check.txt`, `s50-f12-green.txt`, `s50-f12-pyright.txt`, the gate's `s50-gate-h1.txt` and `s50-D6-<id>.txt`, and `drift-check.txt` and `openapi-check.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-port-red", "command": "rtk proxy uv run pytest tests/unit/test_domain.py tests/integration/test_transcript_adapter.py -k \"ac_115_1 or ac_115_2 or ac_115_3 or ac_115_4 or ac_7_4\" --tb=short -q *> C:/Temp/av-kit/s50-port-red.txt; then red-check.py --require on the five tests (task.md row 1 Validation cell, verbatim, from P:/av-kit, TMP and TEMP at C:/Temp/av-kit/s50/tmp)", "cwd": "P:/av-kit", "scope": "MEU-115 Red, port and adapter: AC-115.1 to AC-115.4 and the amended AC-7.4 against the unchanged domain and adapter, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb (baseline.sha) plus row 1", "output": "5 failed, 58 deselected in 0.17s. red-check: 1 receipt(s), 5 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-port-green", "command": "rtk proxy uv run pytest tests/unit/test_domain.py tests/integration/test_transcript_adapter.py tests/unit/test_services.py -k \"domain or adapter or ac_7_ or ac_11_ or ac_115_1 or ac_115_2 or ac_115_3 or ac_115_4\" --tb=short -q *> C:/Temp/av-kit/s50-port-green.txt (task.md row 2 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-115 Green, port and adapter, with the transcript slice of test_services.py and the real-log check", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 and 2", "output": "78 passed, 60 deselected in 4.83s. Real console.log unchanged."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-svc-red", "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/integration/test_tts_device_resolution.py tests/e2e/test_api_transcripts.py tests/integration/test_transcript_failure_delivery.py -k \"ac_115_5 or ... or ac_115_13 or ac_115_18 or ac_115_19\" --tb=short -q *> C:/Temp/av-kit/s50-svc-red.txt; then red-check.py --require on eleven tests (task.md row 3 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-115 Red, service, API and Console: AC-115.5 to AC-115.13, AC-115.18 and AC-115.19", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 to 3", "output": "12 failed, 107 deselected in 2.30s. Decisive assertions, e.g. assert details(logs) == [(variant.id, 'cpu', 'RuntimeError', 'cpu move failed')] and assert (out['status'], out['error_message'], out.get('last_item_message')) == (...). red-check: 1 receipt(s), 11 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-svc-green", "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/unit/test_console_level.py tests/unit/test_uow_commit_log.py tests/integration/test_tts_device_resolution.py tests/integration/test_transcript_failure_delivery.py tests/e2e/test_api_transcripts.py tests/e2e/test_api_tts_runtime.py tests/e2e/test_api_error_surface.py tests/unit/test_tts_async.py --tb=short -q *> C:/Temp/av-kit/s50-svc-green.txt (task.md row 4 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-115 Green, service, API and Console, with the other suites that read health.py, and the real-log check", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 to 4", "output": "187 passed in 7.66s. Real console.log unchanged."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-ui-red", "command": "rtk proxy npm --prefix ui run test -- tests/unit/transcript-page.behavior.test.ts tests/unit/transcript-page.test.ts tests/unit/failure-reason-copy.test.ts *> C:/Temp/av-kit/s50-ui-red.txt; then red-check.py --require AC-115.14 --require AC-115.15 --require AC-115.16 (task.md row 5 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-115 Red, renderer: AC-115.14 to AC-115.16 and the AC-21.16 test id", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 to 5", "output": "Test Files 3 failed (3); Tests 4 failed | 38 passed (42). red-check: 1 receipt(s), 3 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-ui-green", "command": "rtk proxy npm --prefix ui run test -- tests/unit/transcript-page.behavior.test.ts tests/unit/transcript-page.test.ts tests/unit/failure-reason-copy.test.ts tests/unit/help-card.test.ts tests/unit/settings-page.test.ts tests/unit/settings-rail.test.tsx tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts *> C:/Temp/av-kit/s50-ui-green.txt (task.md row 6 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-115 Green, renderer, with the help, Settings and canon suites", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 to 6", "output": "Test Files 8 passed (8); Tests 116 passed (116)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-e2e", "command": "rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s50-r7-build.txt; then rtk proxy npm --prefix ui run test:e2e -- tests/e2e/transcript-queue.test.ts *> C:/Temp/av-kit/s50-r7-e2e.txt, then real-log-check.py --compare (task.md row 7 Validation cell, verbatim, from P:/av-kit, ELECTRON_RUN_AS_NODE cleared)", "cwd": "P:/av-kit", "scope": "MEU-115 AC-115.17 in Electron through the transcript seam, with the rest of transcript-queue", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 to 7", "output": "UI build exit 0. 11 passed (24.2s), including AC-115.17 a Failed job with an error message shows it in job-message. Real console.log unchanged."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-row10-hub", "command": "pwsh -NoProfile -File row-10.ps1 (task.md row 10 Validation cell, verbatim, from P:/av-kit): the issue-resolve receipt, meu_status.py render --check, issue_triage.py render --check, the issue statuses and the grouping row", "cwd": "P:/av-kit", "scope": "Row 10 hub, shared by MEU-115 and MEU-116: the 03 Delivered notes, both MEUs ready_for_review, the three issues resolved through issue-resolve.py and YOUTUBE-CAPTIONS-IP-BLOCK left open, and grouping row 50 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 1 to 10", "output": "issue-resolve: 9 parsed fields changed (issues[101..103] status, verification, resolution_path), 67 of 67 decision logs read, 0 problem(s). Drift check passed. Issue renders match. Statuses TRANSCRIPT-FAILED-NO-REASON resolved, TRANSCRIPT-BLOCK-KEEPS-REQUESTING resolved, CONSOLE-FAILURE-DETAIL-LOST resolved, YOUTUBE-CAPTIONS-IP-BLOCK open. Grouping row 50 names the plan."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-f12-red", "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/integration/test_transcript_failure_delivery.py -k \"case_folding_prefix or context_bound_values\" --tb=short -q *> C:/Temp/av-kit/s50-f12-red.txt, the exit code to s50-f12-red.txt.exit, then red-check.py --require on the three tests *> C:/Temp/av-kit/s50-f12-red-check.txt (from P:/av-kit, TMP and TEMP at C:/Temp/av-kit/s50/tmp)", "cwd": "P:/av-kit", "scope": "Review round 1 corrections Red: the F1 and F2 regressions under AC-115.10 and AC-115.19, against health.py before D-307 and D-308", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 097e0bb plus rows 0 to 10 and the new tests", "output": "5 failed, 100 deselected in 0.65s, each by assertion: the three folding prefixes, the context-bound request_id on stdout and the fold end to end. red-check: 1 receipt(s), 3 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s50-115-f12-green", "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/unit/test_domain.py tests/integration/test_transcript_failure_delivery.py tests/integration/test_transcript_block_done.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_device_resolution.py tests/e2e/test_api_transcripts.py --tb=short -q *> C:/Temp/av-kit/s50-f12-green.txt; then rtk proxy uv run pyright packages/core/src/avkit_core/services/health.py *> C:/Temp/av-kit/s50-f12-pyright.txt (from P:/av-kit, TMP and TEMP at C:/Temp/av-kit/s50/tmp)", "cwd": "P:/av-kit", "scope": "Review round 1 corrections Green: D-307 and D-308 in health.py, over the transcript, Console, TTS and API suites", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "097e0bbcf196fdf0896d4f2e5159be03f69aa62a+ed48a1410419a8b320b81f0210ffff82c44b60427f4423224e82f613c4d3b14b", "output": "203 passed in 13.78s. pyright: 0 errors, 0 warnings, 0 informations."}
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

`s50-gate-h1-2` is the fresh full record, and its last line is:

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
| `packages/core/src/avkit_core/domain/transcript.py` | modified | `TranscriptFailureCause`, `TranscriptSkip`, `failure_message`, `safe_reason`, `REASON_LIMIT` |
| `packages/core/src/avkit_core/ports/transcript.py` | modified | The port returns `TranscriptResult \| TranscriptSkip`; docstring names the errors |
| `packages/infrastructure/src/avkit_infra/transcript/adapter.py` | modified | Typed skips, `BLOCKED_TEXT`, `LIBRARY_REASONS`, class-name fallback; `__cause__` kept |
| `packages/core/src/avkit_core/services/transcript.py` | modified | Item and job messages, the three log lines; shared with MEU-116, which adds the block stop and the cap |
| `packages/core/src/avkit_core/services/health.py` | modified | `CONSOLE_FIELDS`, `console_field`, `FIELD_LIMIT`, the safe downstream event, `PERSIST_LEVELS`, `PERSIST_FIELD`, `LEVEL_ALIASES`, the guarded append, the thread-local guard; the folded-offset map in `redact_message` and the processor after `merge_contextvars` (D-307, D-308) |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | `detail=` on `tts.load_failed` |
| `packages/api/src/avkit_api/schemas/transcripts.py`, `routes/transcripts.py`, `openapi.committed.json` | modified | `last_item_message` and `error_message` on the job; OpenAPI regenerated |
| `ui/src/renderer/src/features/transcript/useTranscriptQueue.ts`, `TranscriptPage.tsx`, `transcript-help-content.ts` | modified | The two fields, `job-message`, the `last-title` text, the `blocked` help section |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx`, `settings-help-content.ts`, `ui/src/renderer/src/components/layout/ConsolePanel.tsx` | modified | Errors always go to the file (D-247) |
| `tests/unit/test_domain.py`, `tests/integration/test_transcript_adapter.py`, `tests/unit/test_services.py`, `tests/integration/test_tts_device_resolution.py`, `tests/e2e/test_api_transcripts.py` | modified | AC-115.1 to AC-115.13, with the AC-115.10 regressions for F1 and F2; AC-7.4 amended and renamed |
| `tests/integration/test_transcript_failure_delivery.py` | new | AC-115.18, AC-115.19, with the F2 fold end to end |
| `ui/tests/unit/transcript-page.behavior.test.ts`, `transcript-page.test.ts`, `ui/tests/e2e/test-ids.ts`, `ui/tests/e2e/transcript-queue.test.ts` | modified | AC-115.14, the test id, AC-115.17 |
| `ui/tests/unit/failure-reason-copy.test.ts` | new | AC-115.15, AC-115.16 |
| `ui/tests/unit/icon-hints.test.ts` | modified | Deviation: not in Files Modified. Its `transcriptItem` fixture gained the two new fields, because typecheck failed without them (TS2739) |
| `docs/build-plan/01`, `02`, `03`, `04`, `06`, `07`, `11` | modified | §Spec text; 03's Delivered note. CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md` | modified | MEU-115 and MEU-116 `ready_for_review` (row 10), shared with MEU-116 |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | Three issues resolved through `issue-resolve.py` (row 10), shared with MEU-116 |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modified | Row 50 `executed` with the plan folder. CRLF kept |
| `.agent/context/current-focus.md` | modified | Session 50 entry on top (H1-3). CRLF kept |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `identity.py`, `red-check.py`, `real-log-check.py`, `real-log-before.json`, `issue-resolve.py`, `session-gate.ps1`, `task.md` | new or modified | The plan's scripts and records, shared with MEU-116 |

```diff
-            return None
+            return TranscriptSkip(TranscriptFailureCause.no_captions)
         except RETRYABLE_ERRORS as exc:
-            raise TranscriptRetryableError(str(exc) or "transcript request blocked") from exc
-        except NONE_ERRORS:
-            return None
-        except NoTranscriptFound:
-            return None
+            raise TranscriptRetryableError(BLOCKED_TEXT) from exc
+        except NO_CAPTIONS_ERRORS:
+            return TranscriptSkip(TranscriptFailureCause.no_captions)
+        except VideoUnavailable:
+            return TranscriptSkip(TranscriptFailureCause.unavailable)
         except DomainError:
             raise
         except Exception as exc:
-            raise DomainError(str(exc) or "transcript fetch failed") from exc
+            raise DomainError(LIBRARY_REASONS.get(type(exc), type(exc).__name__)) from exc
```

The excerpt is abridged. The adapter at `adapter.py:30-107` is the source.

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
| F1 | High | A context-bound `request_id` reached structlog's rendered stdout line raw, because the Console processor ran before `merge_contextvars` (AC-115.10) | `health.py:136`; `main.py:89` | Run the processor after the merge | fixed (D-307); closed in round 2 |
| F2 | High | `redact_message` cut the original at the case-folded offset, so a prefix that folds longer ("ß" * 64) moved the cut past the secret (AC-115.10, AC-115.19) | `health.py:73`; `transcript.py:565` | Map folded positions to the original | fixed (D-308); closed in round 2 |

### Verdict

Round 1 of loop `s50-execution-2026-11-05-transcript-failure-reason` returned `changes_required` with two High findings, F1 and F2, both under AC-115 ([implementation-critical-review.md](2026-11-05-transcript-failure-reason-implementation-critical-review.md)). Both were corrected with Red-first tests and a fresh gate. Round 2 returned `approved`, intent achieved `yes`, with F1 and F2 `fixed` and no new findings.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Rotating or capping `console.log` | out-of-scope | — | Plan §Out of Scope; a question for Mat |
| Re-levelling other warnings, `tts.generate_failed` included | out-of-scope | — | D-302 |
| Pre-existing `ruff format` complaints in `tests/unit/test_services.py` (`:906`, `:1400`, `:1578`) | out-of-scope | — | They fail at `HEAD` too; `py-lint` runs `ruff check`, which passes. The review round laid out this session's own two hunks (the AC-116.4 signature and the AC-115.10 assertion) to `ruff format` |
| Commit and push | out-of-scope | — | Waits for Mat's direction (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files from the task cells, because the cells' `*>` needs PowerShell.
- **Row 1 TMP.** The first row 1 run used the default `TMP` and was rerun with `TMP` and `TEMP` at `C:/Temp/av-kit/s50/tmp`.
- **Baseline.** Row 0's `npm ci` became a lock-sync check.
- **AC-115.13.** It uses a `threading.Event` as its barrier.
- **Row 7 S3 check.** Its `git status` ran right after the row instead of before it, and the tree held only the baseline files and this session's.
- **Gate run 1.** It failed at `ui-tests` on AC-51.6 and AC-81.13 (`s50-gate-h1-run1.txt`, `s50-D6-ui-tests-run1.txt`). Both hash the part of `ui/tests/e2e/test-ids.ts` before the MEU-51 marker, and row 6 had put `JOB_MESSAGE` beside `LAST_TITLE`, inside that part. Row 6's targeted suite didn't include those two files.
  - The fix moved `JOB_MESSAGE` into a new `// MEU-115 Transcript failure reason (additive IDs).` block at the end of the file, as earlier MEUs did. The four affected files then passed (68 tests, `s50-h12-testids-fix.txt`).
  - The gate was rerun in full (run 2, kept as `s50-gate-h1-run2.txt`). Run 1's `py-tests` had already passed, 1260 tests.
- **Review round 1.** Codex found F1 and F2. Row 4 had recorded the `request_id` case as a residual; round 1 showed it was a leak on stdout, so it was fixed here, not deferred. Each fix had its Red first (`s50-115-f12-red`).
- **Gate run 3.** The whole gate ran again after the corrections, and `s50-gate-h1-2` is that run.
- **S8 checkpoint.** After row 7, context use was above half. Mat ruled that the session continues ("do not worry about context just continue"), so rows 8 and 9 stayed in Session 50.

---

## Decision Log

```yaml
decision_log:
  - id: D-307
    stage: execution
    question: "Review round 1 F1: the Console processor ran before merge_contextvars, so a request_id bound from a client header reached the rendered stdout line raw. Where does the processor run, and what does the Console show for bound context?"
    resolution: autonomous
    class: two-way
    chosen: "_ensure_processor inserts _dispatch right after structlog.contextvars.merge_contextvars when the chain has it, else first. The bound context is in the event before the safe message is built, so a request_id shows as a kept Console field, redacted and cut by console_field."
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/main.py:89 binds request_id from the client header", "packages/core/src/avkit_core/services/health.py:47 CONSOLE_FIELDS already keeps request_id", "D-304 hands stdout only the safe message and seq"]
    research: { engine: none, sources: [] }
    reasoning: "Running after the merge makes the existing safe-event rule cover bound context, and no later processor merges it again. Stripping the value in the middleware would leave any other bound key open. A guard after the renderer's own processors would print the fields on stdout before redaction. Showing request_id is what CONSOLE_FIELDS already names. The round 2 recheck tests it."
  - id: D-308
    stage: execution
    question: "Review round 1 F2: redact_message found a needle in the case-folded string and cut the original at that offset, so a prefix that folds longer moved the cut past the secret. How is the cut placed?"
    resolution: autonomous
    class: two-way
    chosen: "Build an origins list that maps each case-folded position to the index of the original character it came from, and cut the original at origins[min(hits)]."
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/health.py:73 redact_message matches REDACT_NEEDLES in message.casefold()", "packages/core/src/avkit_core/services/transcript.py:565 runs safe_reason(redact_message(str(exc)))"]
    research: { engine: none, sources: [] }
    reasoning: "The search stays on the full case fold, so every needle form the old code found is still found, and the fail-closed matching is unchanged. Only the cut moves to the right place. A regex with re.IGNORECASE uses simple case folding and would miss forms the full fold matches."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Initial MEU-115 handoff after H1-2 |
| Corrected | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Review round 1 F1 and F2 fixed (D-307, D-308), the Red and Green evidence added, the gate rerun (run 3) |
| Reviewed | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 2 `approved`; F1 and F2 closed, from the canonical report |
