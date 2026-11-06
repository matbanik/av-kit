---
project: "2026-11-05-transcript-failure-reason"
date: "2026-11-05"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-50--transcript-failure-reason-meu-115-meu-116--p2"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-115", "MEU-116"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: A transcript failure says why, and a block stops the run (Session 50)

> **Project:** `2026-11-05-transcript-failure-reason`
> **Build plan:** `docs/build-plan/03-service-layer.md` §Transcript failure reason (residual) (`:526-541`, MEU-115) and §Transcript block stop (residual) (`:543-555`, MEU-116). The scope is grouping §3 Session 50 (`.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:154`).
>
> **Source requests,** Mat, 2026-11-05. The Session 50 brief scopes MEU-115 then MEU-116, with fake ports and a fake clock and no YouTube request. Done means "a blocked job's card states the reason, and the Console and `console.log` each have a matching line". D-247 ruled "errors always go to a file", even with `app.log_to_file` off.
> **Known issues:** `TRANSCRIPT-FAILED-NO-REASON` (P2; triage D-218, D-234), `TRANSCRIPT-BLOCK-KEEPS-REQUESTING` (P3; D-219, D-220) and the rider `CONSOLE-FAILURE-DETAIL-LOST` (P4). `YOUTUBE-CAPTIONS-IP-BLOCK` is upstream and stays open. This session changes only how av-kit reports a block and stops on one.
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review. The plan review approved in round 2, and Mat said "Go-ahead" on 2026-11-06.
>
> Line anchors are from `main` `ed64f7e`, and the tree was clean at plan time. Only one worktree is open (`git worktree list`: `P:/av-kit ed64f7e [main]`).

## Goal

**Goal anchor:** Session 50 makes every transcript failure or skip carry one short av-kit message. That message reaches the API, the job card, the Console and `console.log`. A YouTube block pauses the job with that message before any request is made for the next video.

Four things are wrong today:

1. **The reason stops at the item.** `_fetch_item` stores it in `TranscriptItem.error_message` (`services/transcript.py:477`, `:493`). `_job_out` passes `job.error_message`, which this service never fills. No route returns items, and the service logs nothing, so a Failed card says only "Failed".
2. **The port can't say why it has no transcript.** The adapter returns `None` for `TranscriptsDisabled`, `VideoUnavailable` and `NoTranscriptFound` alike (`transcript/adapter.py:20`, `:70-82`). When it does raise, it passes on the library's multi-paragraph text (`:78`, `:88`).
3. **A block doesn't stop the run.** `_run_parent` goes on to the next video after a failure (`:415-426`), so every video is retried `max_retries` times. `transcript.requests_per_hour` has a setting (`services/settings.py:59`), and no service reads it.
4. **The Console loses failure detail (rider).**
   - `CONSOLE_FIELDS` keeps only `job_id`, `error`, `request_id` and `route` (`services/health.py:42`). So `tts.load_failed` reaches the Console without its model and with only an exception type name (`tts/adapter.py:123-127`).
   - `console.log` is written only while `app.log_to_file` is on (`health.py:157`), which D-247 overrules for errors.
   - A log from a second thread is dropped while another thread is processing one (`health.py:131-134`).

The session ends when the integration test AC-116.7 passes. It runs a real `HealthService` and `TranscriptService` with a fake caption port that blocks. The job the route builds reads `Paused` with the blocked message, the Console ring has an ERROR line with that message, and `console.log` has the line with `app.log_to_file` off.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-05). A headroom binary is on PATH but no payload here is oversized: the scope is a named list of service, adapter, route, renderer and test files, read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s50-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s50\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s50-plan-2026-11-05-transcript-failure-reason` and `s50-execution-2026-11-05-transcript-failure-reason`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290).
- **Never in these rows without Mat's words:** commit, push, a YouTube request of any kind, or an `approved` verdict authored by the implementer.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-115 `svc-transcript-failure-reason` | `.agent/context/handoffs/2026-11-05-transcript-failure-reason-MEU-115-handoff.md` |
| MEU-116 `svc-transcript-block-stop` | `.agent/context/handoffs/2026-11-05-transcript-failure-reason-MEU-116-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-05-transcript-failure-reason-plan-critical-review.md` and `.agent/context/handoffs/2026-11-05-transcript-failure-reason-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `real-log-before.json`, base suite receipts |
| WP-2 | MEU-115 core and adapter (rows 1, 2) | WP-1 | shared | Domain, port, adapter, service; 02 and 03 spec text |
| WP-3 | MEU-115 API and Console (rows 3, 4) | WP-2 | shared | Route, schema, OpenAPI, `health.py`, TTS log detail; 01, 03, 04 and 07 spec text |
| WP-4 | MEU-115 renderer (rows 5 to 7) | WP-3 | shared | Card, help, Settings and Console texts; 06 and 11 spec text; E2E receipt |
| WP-5 | S8 checkpoint, then MEU-116 (rows 8, 9) | WP-4 | `compact_continue` | Run loop, rate cap, done test; 03 run-loop text |
| WP-6 | Records (row 10) | WP-5 | shared | Hub, MEU status, register, renders |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | Handoffs, review, reflection |

**Split (S8).** The grouping marks MEU-116 as a candidate for Session 50b (`:161`). After row 7 the coordinator records its context use. If it is above about half, it stops and asks Mat whether rows 8 and 9 move to 50b. The split happens only on Mat's words.

## User Review Required

> [!IMPORTANT]
> **Read the user-facing texts in §Messages and §Renderer.** They are what the card, the Console and Settings will say. The blocked message is the one most people will see: "YouTube is blocking caption requests from this network. Try again later or from another network, then Resume."
>
> **Three existing tests change their expectations.** Each change follows the residual sections, not convenience:
> - `test_ac_7_4_disabled_missing_unavailable_return_none` (`tests/integration/test_transcript_adapter.py:170`) now expects a typed skip, not `None`, because the port reports the cause (03 §Transcript failure reason, "Port").
> - `test_ac_11_6_skip_retry_and_write` (`tests/unit/test_services.py:1292`) now expects an exhausted block to leave the item `Pending` and the job `Paused`, not `Failed` (03 §Transcript block stop, "Stop on block"). That's in MEU-116, row 8.
> - `test_ac_11_8_failed_parent_skips_zip` (`:1330`) uses a block today to make an item fail. Its fixture becomes a `DomainError`, so it still tests the Failed path it was written for (row 8).
>
> **`console.log` now gets every ERROR and CRITICAL line, and each transcript skip, with the toggle off (D-247, D-305).** The file has no rotation today, and this session adds none (§Out of Scope). Errors and skips are rare next to the INFO lines the toggle adds, so the file grows much more slowly than it does with the toggle on.
>
> **A new text, from review round 1 (F3).** A Done job with a skipped video now says so on its card: "{n} of {total} videos had no transcript. Last: No captions for this video." (`SKIPPED_JOB_MESSAGE`). Without it, a one-video job with no captions ends Done with no reason anywhere on the card.
>
> **Two choices from review round 1, each with a do-nothing option.** The plan takes option A of each. Either can change at the gate.
> - **How a skip reaches `console.log` (D-305).** D-247 rules on errors, and a skip is logged at WARNING.
>   - **A (chosen):** the skip line carries `persist=True`, which writes it to the file at any level. Nothing else changes.
>   - **B:** WARNING joins `PERSIST_LEVELS`, so every warning in the app goes to the file, `tts.generate_failed` included. That reverses D-302's scope.
>   - **C, do nothing:** a skip stays out of the file with the toggle off. The goal anchor's "or skip … `console.log`" is then unmet, and AC-115.18 loses its file assertion.
> - **Tracebacks on stdout (D-304).** Electron shows every backend stdout line in the Console, so a traceback reaches the user.
>   - **A (chosen):** `_process` hands downstream only the safe message, so no traceback is printed. The three `exc_info=True` call sites keep their error type and text, redacted, on their own line. A developer loses the stack on stdout.
>   - **B, do nothing for tracebacks:** keep them. The kept fields are still dropped, so F1's secret is gone, but the text of an exception in a traceback reaches the Console unredacted.
>
> **The token estimate,** calibrated against Session 42 `tts-sideload-load`, as the grouping asks. That session's plan review took 2 rounds and about 12.8M tokens, and its execution review 1 round and about 4.1M. Sessions 49 and 49b ran about 5M to 9M per round. This delta is two MEUs across core, adapter, route, Console and renderer, larger than Session 42's. Expect 1 to 3 plan rounds and 1 or 2 execution rounds, about 20M to 45M Codex tokens in all.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `CAUSE` | `TranscriptFailureCause`, a closed `StrEnum` in `domain/transcript.py`: `blocked`, `no_captions`, `unavailable`, `other`. |
| `SKIP` | `TranscriptSkip(cause)`, a frozen dataclass in `domain/transcript.py`. It accepts only `no_captions` or `unavailable` and raises `ValidationError` for any other cause. |
| `MESSAGE` | `failure_message(cause, reason=None) -> str` in `domain/transcript.py`, the only place the user-facing texts are written. |
| `JOB_MESSAGE` | The text a Failed job stores in `error_message`: `"{n} of {total} videos failed. Last: {MESSAGE}"`. |
| `SKIPPED_JOB_MESSAGE` | The text a Done job with at least one Skipped item stores in `error_message`: `"{n} of {total} videos had no transcript. Last: {MESSAGE}"`. |
| `SAFE_REASON` | `safe_reason(text) -> str` in `domain/transcript.py`: the first line of `text`, each URL (a `scheme://` run up to whitespace) replaced by "[link]", then cut to `REASON_LIMIT` (200). The service runs `redact_message` on the text before it. |
| `PERSIST_LEVELS` | `("ERROR", "CRITICAL")` in `services/health.py`. Lines at these levels always go to `console.log`. |
| `PERSIST_FIELD` | `"persist"` in `services/health.py`. An event with `persist=True` also always goes to `console.log`, whatever its level. The key is consumed and never shown. |
| `FIELD_LIMIT` | `300`, the most characters a Console field value keeps after it is made single-line. |
| `RATE_WINDOW` | `3600.0` seconds, the rolling window of `transcript.requests_per_hour`. |
| `DONE_TEST` | `tests/integration/test_transcript_block_done.py`, AC-116.7. |
| `DELIVERY_TEST` | `tests/integration/test_transcript_failure_delivery.py`, AC-115.18 and AC-115.19. |

### Messages (D-292)

`MESSAGE` returns exactly these texts:

| Cause | Text |
|---|---|
| `blocked` | "YouTube is blocking caption requests from this network. Try again later or from another network, then Resume." |
| `no_captions` | "No captions for this video." |
| `unavailable` | "This video is unavailable." |
| `other` | "Couldn't get captions: {reason}." The reason comes from the adapter (below). With no reason, it reads "Couldn't get captions." |

The library's own text is never shown. The adapter turns the library's other errors into a short reason from a named map, `LIBRARY_REASONS`:

| Library class | Reason |
|---|---|
| `AgeRestricted` | "the video is age-restricted" |
| `VideoUnplayable` | "the video can't be played" |
| `PoTokenRequired` | "YouTube asked for a PO token" |
| `InvalidVideoId` | "the video ID isn't valid" |
| `YouTubeDataUnparsable` | "YouTube's reply couldn't be read" |
| `YouTubeRequestFailed` | "the request to YouTube failed" |
| `FailedToCreateConsentCookie` | "YouTube's consent page couldn't be passed" |
| Any other `CouldNotRetrieveTranscript` | its class name |

An exception that isn't the library's (a `requests` transport error, a JSON or XML parse error) gives its class name as the reason. Its text is never kept, because it can hold a URL with a query token (F2). An av-kit `DomainError` raised elsewhere keeps `SAFE_REASON` of its text, after `redact_message`. With no text, the reason is the exception's class name. The library class names are those of youtube-transcript-api 1.2.4, the locked version (`uv run python -c …`, 2026-11-05).

### Port and adapter (MEU-115, D-291)

- **Port.** `TranscriptPort.get_transcript` returns `TranscriptResult | TranscriptSkip` instead of `TranscriptResult | None`. Its docstring says a skip carries its cause. The adapter and the tests' `FakeCaptions` are the only implementers (`grep`, 2026-11-05).
- **Skips.** `TranscriptsDisabled` and `NoTranscriptFound` become `SKIP(no_captions)`. `VideoUnavailable` becomes `SKIP(unavailable)`. So does the listing fallback finding no transcript at all, as `no_captions`.
- **Block.** `RequestBlocked` and `IpBlocked` still raise `TranscriptRetryableError`, with a short fixed text ("caption request blocked") and the library error kept as `__cause__`. In youtube-transcript-api 1.2.4, an HTTP 429 raises `IpBlocked` (`_transcripts.py:95-96`), so a rate-limit answer already counts as a block.
- **Other.** Every other exception raises `DomainError(reason)` per §Messages, with `__cause__` kept. The reason is a `LIBRARY_REASONS` text or a class name, never exception text. `TranscriptRetryableError` and `DomainError` raised inside the adapter pass through as today.
- **Validation.** The argument checks at `:52-55` are unchanged.

### Service: storing and logging the message (MEU-115, D-292, D-295)

In `_fetch_item`:

- **A skip** is saved `Skipped` with `error_message = MESSAGE(skip.cause)`, and logs `transcript.item_skipped` at WARNING with `persist=True`, so it reaches `console.log` with the toggle off (D-305).
- **A `DomainError`** is saved `Failed` with `error_message = MESSAGE(other, reason)`, where the reason is `SAFE_REASON(redact_message(str(error)))` (§Messages), and logs `transcript.item_failed` at ERROR.
- **A block that exhausts `max_retries`** is saved `Failed` with `MESSAGE(blocked)` and logs `transcript.item_failed` at ERROR. MEU-116 then replaces this outcome (§Block stop).
- **A retry** in progress stores `MESSAGE(blocked)` on the item and logs nothing. Each line of the three above carries `job_id`, `video_id` and `error=` the stored message.
- **Done** clears `error_message`, as today (`:519`).

In `_run_parent`, a job ending `Failed` stores `JOB_MESSAGE` in `error_message`. In `JOB_MESSAGE`, `n` is the count of Failed items, `total` the job's item count, and `Last` the message of the Failed item processed last. A job ending `Done` with at least one Skipped item stores `SKIPPED_JOB_MESSAGE` the same way, with `n` the count of Skipped items. A one-video job with no captions therefore ends Done with "1 of 1 videos had no transcript. Last: No captions for this video." (F3). A Done job with no Skipped item keeps `error_message` `None`. The outcomes themselves don't change: which videos end Done, Skipped or Failed is as today.

`retry_failed_channel` already clears `error_message` on the job and its items (`:257`, `:267`).

### API (MEU-115, D-293)

- **Schema.** `TranscriptJobOut` gains `last_item_message: str | None` (`schemas/transcripts.py`).
- **Route.** `_aggregates` already picks the latest item (`routes/transcripts.py`). `_job_out` sets `last_item_message` to that item's `error_message` when its status is `Failed` or `Skipped`, and `None` otherwise. `error_message` passes the job's own, which this session now fills.
- **Docs and contract.** `04-rest-api.md:227` lists the field. `openapi.committed.json` is regenerated (`tools/export_openapi.py -o openapi.committed.json`), and the `openapi` check must show only this field as new (S6).
- **MCP.** `mcp-server/src/toolsets/transcript.ts` passes the job JSON through, and its oracle reads only `status`, `transcripts_done` and `last_item_status`. So MCP changes no code, and `mcp-types` and `mcp-tests` run as guards.

### Console (MEU-115 rider, D-296, D-297, D-298)

In `services/health.py`:

- **Kept fields.** `CONSOLE_FIELDS` becomes `("job_id", "video_id", "variant_id", "device", "error", "detail", "request_id", "route")`, in that order. Each value is turned into one line (every run of line breaks becomes one space). Each URL becomes "[link]" by the same rule `SAFE_REASON` uses, so the two share one helper. The value is then redacted with `redact_message` and cut to `FIELD_LIMIT`. The whole message is then redacted again, as today. The comment above the tuple says why each field is there.
- **TTS load detail.** `_log_load_failed` (`tts/adapter.py:123-127`) adds `detail=` the first line of the exception's text (of the cause for a `ModelLoadError` with a cause, as `error` already does). An empty text adds no `detail`.
- **Downstream sees only the safe message (F1, D-304).** Today `_process` returns the event with its original fields, and structlog's later renderer prints them to stdout. Electron forwards every stdout line to the visible Console (`ui/src/main/index.ts:270-275`), so a secret in `detail` or `error` reaches the user as a second line. After composing, `_process` empties the mapping it returns. It keeps only `event` (the redacted message), `seq` and `exc_info=False`, so `set_exc_info` adds no traceback for an `exception` call. The stdout renderer then prints exactly what the ring holds. A traceback from `exc_info=True` no longer reaches stdout (three call sites: `errors.py:87`, `tts.py:346-354`). Their ERROR or WARNING line still carries the error type and text, redacted. Tests that assert `exc_info` use `capture_logs`, which bypasses `_dispatch`, so they are unaffected (`test_api_error_surface.py:112`, `test_tts_async.py:535`).
- **Errors always to the file (D-247).** A line whose level is in `PERSIST_LEVELS`, or whose event carries `PERSIST_FIELD` true, is appended to `{app_data}/logs/console.log` whatever `app.log_to_file` holds. The toggle adds every other line.
- **Levels.** `exception` maps to ERROR, `fatal` to CRITICAL and `warn` to WARNING (`LEVEL_ALIASES`). Today all three fall to INFO (`:142-143`).
- **The file append never raises.** `_append_console_log` catches `OSError`, so a locked or read-only file can't fail the call that logged. The ring and stdout still get the line. The append runs under its own lock, so lines from two threads don't interleave.
- **Two threads both reach the ring.** The re-entrancy guard becomes thread-local (`threading.local`), in place of the shared `_processing` flag. A log raised while processing a log, on the same thread, is still passed through unprocessed, as today. A log from another thread at the same moment is now processed instead of dropped.

The ring stays in memory and clears when the app closes. With errors in the file, a failure's detail outlives the close.

`tts.generate_failed` stays at WARNING (`services/tts.py:344-349`). The job's `error_message` already shows the reason on the TTS page (TTS-GENERATE-FAILED-SILENT D-3), and re-levelling other warnings is out of scope.

### Renderer (MEU-115, D-294)

- **Types.** `TranscriptListItem` (`useTranscriptQueue.ts:8-22`) gains `error_message: string | null` and `last_item_message: string | null`.
- **Card line three** (`TranscriptPage.tsx` `CardDetail`, `:114-133`):
  - On a `Failed`, `Paused` or `Done` card with an `error_message`, line three is a `job-message` line holding the message, in place of the output tree. A Done card has one only when a video was skipped (`SKIPPED_JOB_MESSAGE`). The kebab menu's "Open folder" (`:97`) keeps the folder reachable.
  - On a `Processing` card with a `last_title` or a `last_item_message`, the `last-title` line reads "Last: {title} {status} · {message}", leaving out any part that is null. An item with no title still shows its status and message.
  - Every other card is as today, the ordinary Done card with no skip among them.
- **Test ids.** `job-message` is added to the page's test-id list (`transcript-page.test.ts:36-48`) and as `JOB_MESSAGE` to `ui/tests/e2e/test-ids.ts:102-105`.
- **Transcript help.** A new `blocked` section, after `rate`: "When YouTube blocks caption requests, the job pauses with that reason and makes no more requests. Resume tries again; another network often works sooner." The existing topics stay, so `help-card.test.ts` AC-23.16 still passes.
- **Settings and Console texts.** These say that errors always go to the file:
  - **Settings hint** (`SettingsPage.tsx:1041-1072`): "Errors are always written to this file. Turn on Log to file to write every Console line there too." "Persist to {path}" stays, as two tests pin it (`settings-page.test.ts:409`, `settings-rail.test.tsx:510-512`).
  - **Settings help** (`settings-help-content.ts:22`): "Errors are always written to {app_data}/logs/console.log; Log to file adds every other line. That path is not configurable…", with the rest of the sentence kept.
  - **Console panel** (`ConsolePanel.tsx:209-211`): "Errors always go to {path}. Turn this on for every line."

### Block stop and the rate cap (MEU-116, D-299, D-300)

**Block stop.**

- **When a video's retries run out.** A `TranscriptRetryableError` uses the same retry loop and `retry_delay` as today. When `max_retries` is exhausted, `_fetch_item` doesn't fail the item. It saves it `Pending`, with `retry_count` back to 0 and `error_message = MESSAGE(blocked)`, logs `transcript.blocked` at ERROR (`job_id`, `video_id`, `error=`), and reports the block to `_run_parent`.
- **The job pauses.** `_run_parent` then calls `_pause_parent(job.id, MESSAGE(blocked))`. That moves the job `Processing → Paused` with that `error_message`, and sets `self._pause = True`. The worker's existing check at `:361` then pauses before `_next_job`, so no request is made for the next video of this job or any other.
- **Resume.** `resume_processing` clears the job's `error_message` when it moves the job back to `Processing`. The `Pending` videos run as after any pause, and a video that finishes Done clears its own message (`:519`).
- **A pause without a reason.** `_pause_parent(job_id)` with no reason leaves `error_message` as it is, so a user's pause shows no message.
- **A resume that races the worker (F4, D-306).** Today the worker resets `_pick_processing = False` after `_run_parent` returns (`:373`). The worker also decides to exit without the lock that `resume_processing` holds when it checks the thread (`:225-236`). So a resume that lands after the pause is published, but before the worker exits, either loses its selection flag or finds a live thread that then exits. Either way the job reads Processing while the runtime reads Idle or Paused. A user's pause has the same window today, and the block stop makes it routine. The worker and the two entry points therefore share one rule under `self._lock`:
  - `_next_job` reads and clears `_pick_processing` under the lock when it selects a job, and the reset at `:373` goes. A resume during `_run_parent` sets the flag after the clear, so the next selection picks the Processing job.
  - Each worker exit (pause, stop, idle) re-checks its flag under the lock. In the same critical section it writes the runtime and sets `self._thread = None`. A pause exit whose `_pause` was cleared by a resume goes round the loop instead of exiting.
  - `resume_processing` and `start_processing` write their flags and check `self._thread` in one critical section. So either the worker sees the resume before it exits, or the resume sees `None` and starts a new worker. At most one worker runs. `self._lock` is a plain `threading.Lock` (`:98`), so nothing called inside these sections may take it again.
- **Other failures.** A `DomainError` still ends that video `Failed`, and the run goes on (03 §Transcript block stop, "Other failures").

**Rate cap.**

- **Clock.** `TranscriptService.__init__` takes `clock: Callable[[], float] | None = None`, defaulting to `time.monotonic`.
- **What counts.** The service keeps a deque of request start times, counting every call to `get_transcript`, retries included.
- **Before each request:**
  - read `transcript.requests_per_hour`;
  - if it is 0, the cap is off;
  - otherwise drop entries at or before `now − RATE_WINDOW`, and while the count is at or above the cap, sleep `min(1.0, oldest + RATE_WINDOW − now)`, then re-check `_stop` and `_pause` and read the cap again.
- **Why slices.** A stop or pause during a long cap wait takes effect within a second, and a raised cap ends the wait.
- **Fractional caps.** A cap below 1 allows one request an hour and never deadlocks, because an empty deque always passes.
- **With no retries, the default cap delays nothing.** It is 300 an hour. With the default 6 s between requests and a 300 s pause after every 50, request k (from 0) starts at `6k + 300·floor(k/50)`, so 50 requests take 600 s and any hour holds at most 300 of them. The entry at exactly `now − RATE_WINDOW` is dropped, so the 301st request at 3600 s passes. AC-116.5 pins this over 400 videos on the fake clock.
- **A retry can make the default cap wait (F5).** A retry is a request, as D-220 asks, and it adds `retry_delay` but also a start. With one retry on the first video and success after it, the 301st start would fall at 3324 s, so the cap waits about 276 s before it. That wait is the cap doing its job, not a regression. AC-116.9 pins it, and it checks independently that no rolling hour holds more than 300 starts.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/02-infrastructure.md` | `:320-327` | The adapter's error table: skips by cause, the short block text, `LIBRARY_REASONS`; "returns None" goes |
| `docs/build-plan/03-service-layer.md` | `:217-240`, `:250-252` | The worker loop and "One item" steps: messages, log lines, block pause, rate cap (row 9 for the MEU-116 parts) |
| `docs/build-plan/03-service-layer.md` | `:388` | "When `app.log_to_file` is true…" becomes the `PERSIST_LEVELS` and `PERSIST_FIELD` rule, and says the event handed to stdout holds only the safe message |
| `docs/build-plan/03-service-layer.md` | both residual sections | Delivered notes (row 10) |
| `docs/build-plan/04-rest-api.md` | `:227` | `TranscriptJobOut` gains `last_item_message` |
| `docs/build-plan/01-domain-layer.md` | `:41` | "Settings toggle only" becomes errors always, the toggle for the rest |
| `docs/build-plan/07-distribution.md` | `:55` | "# if app.log_to_file" becomes "# errors always; every line if app.log_to_file" |
| `docs/build-plan/06-gui.md` | `:347`, `:363`, `:690`, `:1007`, `:1077` | The card's line three (Failed, Paused, and Done with a skip), `job-message`, the help `blocked` section and the log-file texts |
| `docs/build-plan/11-page-layout.md` | `:32` | TR5 names the `job-message` line on a Failed or Paused card, or a Done card with a skip. The TR inventory rows (TR 10 `last-title`, TR 11 `output-tree`) don't change, because `layout-canon.test.ts` reads mockup inventories, not page source |

### MEU-115 `svc-transcript-failure-reason`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `TranscriptPort.get_transcript` return | `domain/transcript.py` (`TranscriptResult`, `TranscriptSkip`) | `TranscriptSkip.cause` is `no_captions` or `unavailable`; any other cause raises `ValidationError` | Frozen dataclass; no other fields |
| `GET /transcripts`, `GET /transcripts/{id}` → `TranscriptJobOut` | `packages/api/src/avkit_api/schemas/transcripts.py` | `last_item_message: str \| None`, set only when the latest item is Failed or Skipped; `error_message: str \| None` | Response model; unchanged policy |
| Console event message | `services/health.py` | `CONSOLE_FIELDS` order; each value single-line, redacted and at most `FIELD_LIMIT` characters | Keys not in `CONSOLE_FIELDS` stay off the message |
| The event `_process` hands downstream (stdout, then Electron's Console) | `services/health.py` | Only `event` (the redacted message), `seq` and `exc_info=False` | Every other key is dropped, `persist` and the raw field values among them |
| `{app_data}/logs/console.log` | `services/health.py` | One JSON line per event, `{seq, message, module, level}`; ERROR and CRITICAL always, as is an event with `persist=True`; the rest only with `app.log_to_file` | Unchanged |

#### Acceptance Criteria

Pytest names are `test_ac_115_<n>_…`. Vitest and Playwright titles begin `AC-115.<n>`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-115.1 | unit | `MESSAGE` returns the four texts of §Messages exactly, "Couldn't get captions." with no reason, and `SKIP` refuses `blocked` and `other`. `SAFE_REASON` keeps the first line, turns each URL into "[link]" and cuts to `REASON_LIMIT` (`tests/unit/test_domain.py`). | Local Canon (triage D-218) | Today `failure_message` and `TranscriptSkip` don't exist: import fails inside the test, which asserts on it |
| AC-115.2 | integration | The adapter returns `SKIP(no_captions)` for `TranscriptsDisabled`, `NoTranscriptFound` and an empty listing, and `SKIP(unavailable)` for `VideoUnavailable` (`tests/integration/test_transcript_adapter.py`; AC-7.4 amended to match). | Local Canon (03 §Transcript failure reason, "Port") | Today all four return `None` |
| AC-115.3 | integration | `RequestBlocked` and `IpBlocked` raise `TranscriptRetryableError` whose text is "caption request blocked", with the library error as `__cause__`. | Local Canon (triage D-218, "not the library's text") | Today the text is the library's multi-paragraph message |
| AC-115.4 | integration | Each `LIBRARY_REASONS` class raises `DomainError` with its reason; another library class gives its class name; a non-library error gives its class name and none of its text (a `requests.ConnectionError` whose text holds `https://example.invalid/caption?token=SYNTHETIC_API_MARKER` gives "ConnectionError"). `__cause__` is kept in each case. | Local Canon (triage D-218) | Today the text is the library's |
| AC-115.5 | unit | `_fetch_item` stores `MESSAGE` on each Skipped and Failed item (skip, `DomainError`, exhausted block), and the item outcomes are as today (`tests/unit/test_services.py`). | Local Canon (triage D-218) | Today a skip stores `None` and a failure stores the raw text |
| AC-115.6 | unit | A job ending Failed stores `JOB_MESSAGE` with the right count, total and last message. A job ending Done with a Skipped item stores `SKIPPED_JOB_MESSAGE`; a Done job with none keeps `None`. | Local Canon (03 §Transcript failure reason, "API") | Today `error_message` stays `None` |
| AC-115.7 | unit | Each skip logs one `transcript.item_skipped` WARNING, each failure one `transcript.item_failed` ERROR, each with `job_id`, `video_id` and `error=` the stored message; a retry logs nothing. | Local Canon (03, "Log") | Today the service logs nothing |
| AC-115.8 | e2e | `GET /transcripts` returns `last_item_message` for a latest item that is Failed or Skipped, `None` for one that is Pending or Done, and the job's `error_message` (`tests/e2e/test_api_transcripts.py`); `openapi` shows only this field as new. | Local Canon (03, "API"; 04 `:227`) | Today the field is absent |
| AC-115.9 | unit | The Console message carries the new `CONSOLE_FIELDS` in order. A value with line breaks is one line, and one over `FIELD_LIMIT` is cut to it. `tts.load_failed` carries `variant_id`, `device`, `error` and `detail` (`tests/unit/test_services.py`; `tests/integration/test_tts_device_resolution.py`). | Local Canon (`CONSOLE-FAILURE-DETAIL-LOST`) | Today `video_id`, `variant_id`, `device` and `detail` are dropped |
| AC-115.10 | unit | Through the production wiring, a secret in a kept field (`detail="Authorization: Bearer abc"`, a cookie in `error`, a token in `video_id`, a `https://…?token=` URL in `detail`) or in a field that isn't kept appears in none of the ring, the complete captured stdout or `console.log`. The wiring is a real `HealthService` that installs its processor into structlog's configured chain, and a `structlog.get_logger()` call that runs every downstream processor and renderer. Every captured stdout line is checked as well: the downstream renderer prints each event once more, from the safe event, so no line may hold a marker, a traceback or a key besides `event` and `seq` (review round 2's clarification). | Local Canon (`CONSOLE-FAILURE-DETAIL-LOST`, "after checking that redaction still holds") | A guard: the new fields must not open a hole. Its Red is the missing fields, so it fails on the field assertion that sits beside the secret check |
| AC-115.11 | unit | With `app.log_to_file` off, an ERROR line, an `exception` line and a WARNING line with `persist=True` reach `console.log`, and a plain WARNING and an INFO line don't. `exception` reads ERROR in the ring, and `persist` appears in no message. | Human-approved (D-247: "yes they should go to file") | Today nothing is written with the toggle off, and `exception` reads INFO |
| AC-115.12 | unit | When the append raises `OSError`, the logging call returns, and the ring and stdout have the line. | Local Canon (D-296) | Today the `OSError` propagates to the caller |
| AC-115.13 | unit | Two threads log at the same moment, with the first held inside processing by a barrier, and both lines reach the ring. | Local Canon (D-298) | Today the second line is dropped |
| AC-115.14 | unit | A Failed card with `error_message` shows `job-message` with the text and no `output-tree`. So does a Paused card with `error_message`, and so does a Done card with `error_message` (a skip). A Processing card with `last_item_message` shows it in `last-title`, including when `last_title` is null. A Done card with no `error_message` is unchanged (`ui/tests/unit/transcript-page.behavior.test.ts`). | Local Canon (03, "Card"; D-294) | Today no `job-message` exists |
| AC-115.15 | unit | The Settings hint, the Settings help and the Console panel say errors always go to the file (`ui/tests/unit/failure-reason-copy.test.ts`). | Human-approved (D-247) | Today they say the file is written only with the toggle on |
| AC-115.16 | unit | The transcript help has a `blocked` section saying the job pauses and Resume tries again (same file). | Local Canon (triage D-218, "names a next step") | Today there is no `blocked` section |
| AC-115.17 | e2e | In Electron, through the transcript seam, a Failed job with `error_message` shows `job-message` with the text (`ui/tests/e2e/transcript-queue.test.ts`). | Local Canon (E2: an E2E assertion for a changed output element) | Row 5's AC-115.14 Red is the negative; this row runs after Green |
| AC-115.18 | integration | `DELIVERY_TEST`: a real `HealthService` (`tmp_path`, `app.log_to_file` off) and `TranscriptService` run a one-video job whose `FakeCaptions` answer is `SKIP(no_captions)`. `_job_out` shows `Done` with `error_message` = `SKIPPED_JOB_MESSAGE` ("1 of 1 videos had no transcript. Last: No captions for this video.") and `last_item_message` "No captions for this video.". The ring has a WARNING `transcript.item_skipped` line with the message, and `console.log` has that line. The card's Done case is AC-115.14, on the same text. | Local Canon (triage D-218: Skipped gets the same treatment; the goal anchor's "or skip") | Today the job's message is `None`, the item's is `None`, and a WARNING never reaches the file with the toggle off |
| AC-115.19 | integration | `DELIVERY_TEST`, no secret end to end. The real adapter, with `YouTubeTranscriptApi` monkeypatched to raise `requests.ConnectionError("… https://example.invalid/caption?token=SYNTHETIC_API_MARKER")`, runs inside a real `TranscriptService` and `HealthService`. So does a `FakeCaptions` `DomainError` whose text holds `https://example.invalid/x?token=SYNTHETIC_DOMAIN_MARKER` and `Authorization: Bearer SYNTHETIC_BEARER_MARKER`. No marker appears in any item's `error_message`, in `_job_out`, in the ring, in the complete captured stdout or in `console.log`. | Local Canon (triage D-218, "not the library's text"; `CONSOLE-FAILURE-DETAIL-LOST`, redaction holds) | Today the service stores a `DomainError`'s raw text, so the domain markers reach the item, the API and the logs |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| The four causes and that the library text is not shown | Local Canon | Triage D-218; 03 §Transcript failure reason |
| The exact message texts | Local Canon | D-292, shown to Mat at the plan gate |
| Which library classes exist and that 429 is `IpBlocked` | Research-backed | youtube-transcript-api 1.2.4 source, measured at plan time |
| Where the job-level message lives | Local Canon | 03, "A job ending `Failed` fills `error_message`" |
| Errors in the file with the toggle off | Human-approved | D-247 |
| Kept fields and redaction | Local Canon | `CONSOLE-FAILURE-DETAIL-LOST`; `redact_message` fails closed |
| What stdout and Electron's Console receive | Local Canon | D-304; `ui/src/main/index.ts:270-275` forwards every stdout line |
| A skip in the file, and on a Done card | Local Canon | Triage D-218 (Skipped gets the same treatment); D-305; the goal anchor |
| The card's line three | Local Canon | TR5 (`11-page-layout.md:32`) amended per D-294 |

### MEU-116 `svc-transcript-block-stop`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `transcript.requests_per_hour` | `services/settings.py:59` | Number, min 0, default 300; 0 is off; read before each request | Unchanged |
| `TranscriptService(clock=…)` | `services/transcript.py` | `Callable[[], float]`, default `time.monotonic` | Keyword-only |
| A blocked job as the API returns it | `TranscriptJobOut` | `status: Paused`, `error_message` = `MESSAGE(blocked)` until resume | Unchanged |

#### Acceptance Criteria

Pytest names are `test_ac_116_<n>_…`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-116.1 | unit | With `max_retries` 3 and a port that blocks every call, the first video gets exactly 3 calls and the second none. The job reads `Paused` with `MESSAGE(blocked)`, every item is `Pending`, the first has `retry_count` 0 and the message, and the runtime is `Paused`. | Research-backed (triage D-219) | Today the second video is requested and the job ends Failed |
| AC-116.2 | unit | After AC-116.1, with the port now answering, `resume_processing` finishes the job Done. The job's and the items' `error_message` are `None`. | Local Canon (03 §Transcript block stop, "Resume") | Today the job is Failed, so resume refuses (`ConflictError`) |
| AC-116.3 | unit | A `DomainError` on the first video fails it, and the second video is still requested. | Local Canon (03, "Other failures") | A guard: true today, and fails if the block stop catches all failures |
| AC-116.4 | unit | On the fake clock, with the cap at 2, the third request waits until the first is an hour old. A retry counts as a request. A cap of 0 never waits. A cap lowered between two requests is read for the second. During a cap wait, a stop or a pause takes effect within one slice (at most 1 s of fake time), and a cap raised above the count or set to 0 ends the wait at the next slice. | Local Canon (triage D-220) | Today no request waits |
| AC-116.5 | unit | With default settings, no retries and 400 videos on the fake clock, no sleep beyond the delay and batch sleeps happens. | Local Canon (03, "Default behaviour doesn't change") | A guard: true today, and fails if the cap's window or boundary is wrong |
| AC-116.6 | unit | The amended AC-11.6 expects an exhausted block to leave the item Pending and the job Paused. The amended AC-11.8 makes its item fail with a `DomainError` and still skips the zip. | Local Canon (03, "Stop on block") | AC-11.6 as amended fails today, as AC-116.1 does |
| AC-116.7 | integration | `DONE_TEST`: a real `HealthService` (`tmp_path`, `app.log_to_file` off) and `TranscriptService` with a blocking fake port. `_job_out` shows `Paused` with the message, the ring has an ERROR `transcript.blocked` line with the message, and `console.log` has that line. | Human-approved (Mat's brief, "Done means…") | Today the job ends Failed with no message and nothing is logged |
| AC-116.8 | unit | A resume that races the worker still finishes the job (D-306). The barriers have timeouts, so a Red fails by assertion and never hangs. (a) The fake port raises `TranscriptRetryableError` on every call until the test switches it to answer. A wrapper on `_pause_parent` holds the worker after the job is published Paused, before `_run_parent` returns. The test calls `resume_processing`, sets the port to answer and releases the worker. (b) The same, but the fake sleep holds the worker at its `_sleep(0)` after `_run_parent` returns. In both, every video ends Done, the job ends Done, the runtime ends Idle and at most one worker thread ran at once. | Local Canon (03 §Transcript block stop, "Resume"; review F4) | Today (a) leaves the job Processing and the runtime Idle with `_pick_processing` False, and the block stop doesn't exist, so the barrier's wait fails its assertion |
| AC-116.9 | unit | With default settings, 400 videos and one retry on the first video (then success) on the fake clock, the cap waits before the 301st start. In the list of start times the fake port records, no window of 3600 s, open at its left end, holds more than 300 starts. | Local Canon (triage D-220: retries count; review F5) | Today nothing waits, and 301 starts fall within one hour |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Stop the run after one blocked video, with no growing wait | Research-backed | Triage D-219 |
| What resume does | Local Canon | `resume_processing` (`services/transcript.py:207-236`) |
| Rolling cap over real requests | Local Canon | Triage D-220; a sliding-window log, D-300 |
| The window's boundary | Local Canon | D-300, pinned by AC-116.5 (no retries) and AC-116.9 (one retry) |
| A resume during the worker's pause exit | Local Canon | D-306, pinned by AC-116.8 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/transcript.py` | modify | `CAUSE`, `SKIP`, `MESSAGE`, `SAFE_REASON` |
| `packages/core/src/avkit_core/ports/transcript.py` | modify | Return type and docstring |
| `packages/infrastructure/src/avkit_infra/transcript/adapter.py` | modify | Skips, block text, `LIBRARY_REASONS` |
| `packages/core/src/avkit_core/services/transcript.py` | modify | Messages, logs, `JOB_MESSAGE`, `SKIPPED_JOB_MESSAGE`; block stop, worker selection and exit under the lock, clock and cap (row 9) |
| `packages/core/src/avkit_core/services/health.py` | modify | Fields, the safe downstream event, `PERSIST_LEVELS`, `PERSIST_FIELD`, `LEVEL_ALIASES`, the append, the thread-local guard |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | `detail=` on `tts.load_failed` |
| `packages/api/src/avkit_api/schemas/transcripts.py` | modify | `last_item_message` |
| `packages/api/src/avkit_api/routes/transcripts.py` | modify | `_job_out` |
| `openapi.committed.json` | modify | Regenerated |
| `ui/src/renderer/src/features/transcript/useTranscriptQueue.ts` | modify | Two fields |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modify | `job-message`, `last-title` text |
| `ui/src/renderer/src/features/transcript/transcript-help-content.ts` | modify | `blocked` section |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | Log-file hint |
| `ui/src/renderer/src/features/settings/settings-help-content.ts` | modify | Console help text |
| `ui/src/renderer/src/components/layout/ConsolePanel.tsx` | modify | Log-file text |
| `tests/unit/test_domain.py` | modify | AC-115.1 |
| `tests/integration/test_transcript_adapter.py` | modify | AC-115.2 to AC-115.4; AC-7.4 amended |
| `tests/unit/test_services.py` | modify | AC-115.5 to AC-115.7, AC-115.9 to AC-115.13, AC-116.1 to AC-116.6, AC-116.8, AC-116.9; AC-11.6 and AC-11.8 amended |
| `tests/integration/test_tts_device_resolution.py` | modify | AC-115.9's `detail` |
| `tests/e2e/test_api_transcripts.py` | modify | AC-115.8 |
| `tests/e2e/api_fakes.py` | modify | `FakeTranscript` items can carry a status and message, if AC-115.8 needs it |
| `tests/integration/test_transcript_block_done.py` | create | AC-116.7 |
| `tests/integration/test_transcript_failure_delivery.py` | create | AC-115.18, AC-115.19 |
| `ui/tests/unit/transcript-page.behavior.test.ts` | modify | AC-115.14 |
| `ui/tests/unit/transcript-page.test.ts` | modify | `job-message` test id |
| `ui/tests/unit/failure-reason-copy.test.ts` | create | AC-115.15, AC-115.16 |
| `ui/tests/e2e/test-ids.ts` | modify | `JOB_MESSAGE` |
| `ui/tests/e2e/transcript-queue.test.ts` | modify | AC-115.17 |
| `docs/build-plan/01-domain-layer.md`, `02-infrastructure.md`, `03-service-layer.md`, `04-rest-api.md`, `06-gui.md`, `07-distribution.md`, `11-page-layout.md` | modify | §Spec text |
| `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md` | modify | Row 10, H2-2 |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md`, `.agent/context/triage-output.yaml` | modify | Row 10 |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modify | §6 row 50 (`:240`) gets the plan folder and status |
| `.agent/context/current-focus.md` | modify | H1-3 |

Every file keeps its line endings: measured with Python bytes, written with `newline=""`.

### Project files

Plan-local scripts, listed in §Verification Plan: `baseline.sha`, `baseline-dirty.txt`, `baseline.ps1`, `red-check.py`, `identity.py`, `real-log-check.py`, `issue-resolve.py`, `session-gate.ps1`. State: `docs/execution/metrics.md`, the two handoffs, the rolling reviews and the reflection.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| `YOUTUBE-CAPTIONS-IP-BLOCK`, the block itself | out-of-scope | — | Upstream; 03 §Transcript block stop changes only the stop |
| A growing wait or a new setting for blocks | out-of-scope | — | 03 §Transcript block stop: "No growing wait and no new number" |
| Re-levelling other warnings, `tts.generate_failed` included | out-of-scope | — | D-302; the TTS page already shows that reason (TTS-GENERATE-FAILED-SILENT D-3) |
| Keeping the Console ring across a restart | out-of-scope | — | D-247 puts errors in the file, which survives the close; the ring stays in memory |
| Rotating or capping `console.log` | out-of-scope | — | Not in the brief or the residual sections; a question for Mat |
| A route that returns items | out-of-scope | — | 03 §Transcript failure reason asks for the message on the job, not items |
| Real titles and channel names | deferred | MEU-122 | Grouping §3 Session 53; it follows this session on `services/transcript.py` |
| `mcp-audit` | out-of-scope | — | It touches the network and YouTube; the brief forbids YouTube requests |

## BUILD_PLAN.md Audit

Row 10 adds Delivered notes to both residual sections in `03-service-layer.md`. It sets MEU-115 and MEU-116 to `ready_for_review` with this `execution_plan` through `tools/meu_status.py`, then renders `docs/BUILD_PLAN.md`. The check:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s50-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s50-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. Runs `real-log-check.py --record`. It writes the size, modification time and SHA-256 of `%LOCALAPPDATA%\av-kit\logs\console.log` to `real-log-before.json`, or records that the file is absent.
3. Runs `uv sync --frozen --all-packages` and `npm --prefix ui ci`, then captures the base Python suite to `s50-base-py.txt` and the base UI suite to `s50-base-ui.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s50\tmp`.
4. Runs `red-check.py --selftest` and `identity.py --selftest`.

`red-check.py` and `identity.py` are copies of Session 49b's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds every AC test name this plan adds.
- **`identity.py`.** `PLAN` is this folder.
- **`PROJECT_ARTIFACTS`.** It holds this plan's `*.md`, the two handoffs, the review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The registers and renders stay bound, because row 10 writes them before H1-2.

### 2. Red then Green (rows 1 to 9)

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error, and it refuses a required test that fails on a missing name. So a required test first asserts that the new name exists: `hasattr` on the imported module, or `"clock" in inspect.signature(TranscriptService).parameters`. Only then does it use the name. A test that expects no exception (AC-115.12) catches it and asserts on the result. `DECLARED_NEW` lists the new names (`TranscriptFailureCause`, `TranscriptSkip`, `failure_message`, `LIBRARY_REASONS`, `REASON_LIMIT`, `PERSIST_LEVELS`, `LEVEL_ALIASES`, `FIELD_LIMIT`, `RATE_WINDOW`, `clock`, `safe_reason`, `PERSIST_FIELD`), so a test that isn't required may still fail on one of them.
- **The skip fixture moves with the port.** In row 1, `test_ac_11_6_skip_retry_and_write` changes its skip from `None` to `TranscriptSkip(no_captions)`. The import goes inside the test body. Only the fixture changes, and its assertions stay as they are until row 8. Row 2's Green changes the service's `result is None` branch to `isinstance(result, TranscriptSkip)`, so the transcript slice of `test_services.py` passes again.
- **`--require` matches exactly.** `red-check.py:209` won't let `test_ac_115_1` match `test_ac_115_10`.
- **Guards pass in Red by design.** These are AC-116.3 and AC-116.5. Row 8 doesn't require them.
- **AC-115.17 has no Red of its own.** It is the E2E check in row 7, after row 6 is Green, and its negative is row 5's AC-115.14 Red.
- **Expectations stay immutable in Green.** The three amended tests change in their Red rows (1 and 8), each with the §User Review Required basis.
- **Row 8 also migrates MEU-115's block subcases.** AC-115.5 and AC-115.7 pin the exhausted-block outcome as Failed in row 3, and §Service says MEU-116 replaces it. Row 8 changes only those subcases to Pending, the job Paused and a `transcript.blocked` line. Their skip and `DomainError` expectations stay as they are. Row 8's selection includes them, and row 9 runs them in full.
- **F1 to F5 of review round 1 each have a test that fails today.** F1 is AC-115.10 on complete stdout and F2 is AC-115.19. F3 is AC-115.6, AC-115.14 and AC-115.18, F4 is AC-116.8 and F5 is AC-116.9.
- **No YouTube.** Every test uses a fake port, `FakeCaptions`, or a monkeypatched `YouTubeTranscriptApi`, as `test_transcript_adapter.py` already does. Any test that would build the real client without a patch is S5.

### 3. The real log stays untouched

`real-log-check.py --compare real-log-before.json` exits 1 if the real `console.log` changed. It runs at the end of rows 2, 4, 7 and 9, and in the session gate (`real-log-untouched`). Every `HealthService` in the tests uses `tmp_path` (`grep`, 2026-11-05: `test_services`, `test_console_level`, `test_uow_commit_log`, `test_api_tts_runtime`). Wiring builds it with `app_data=root` (`wiring.py:205`), and the E2E app runs with its own app data, so the check is a guard against a test that points elsewhere (S4).

### Plan-local scripts

Written with their rows and kept in this plan folder:

- `baseline.ps1`, `red-check.py`, `identity.py`, `real-log-check.py` (row 0)
- `issue-resolve.py` (row 10). It is Session 49b's `register-rewrite.py` `--mode resolve`, taking `--issue` once per issue. It keeps the exclusive handle, `--expect-sha256`, the staged save and the `--set-file` refusal of any other key, and it accepts parsed differences only under `status`, `verification` and `resolution_path` of the named issues.
- `session-gate.ps1` (H1-2)

### Session gate (H1-2)

`session-gate.ps1` is Session 49b's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s50-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `state-render`, `issues-render` |
| Runtime | `ui-electron` targeted to `transcript-queue`, `settings` and `console-chrome` specs; `real-log-untouched` |
| Skipped, with reason | `mcp-build`: no MCP source change. `mcp-audit`: live network and YouTube, which the brief forbids. `build-record`: no installer build. |

`py-tests` and `ui-tests` excuse only ids that row 0's receipts show failing, as Session 49b did.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`, or a path outside `baseline-dirty.txt` and this plan appears | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S4 | `real-log-check.py --compare` reports a change to the real `console.log` | Stop; find the test that wrote it before anything else runs |
| S5 | Any step would make a real YouTube request | Stop before it runs; bring it to Mat |
| S6 | `openapi` drifts beyond the new `last_item_message` | Stop; report the diff to Mat |
| S7 | Codex is unavailable or the ledger refuses | Mat |
| S8 | After row 7, context use is above about half | Ask Mat whether rows 8 and 9 move to Session 50b |

## Decision Log

> [!WARNING]
> No decision here needs a separate Decision Brief file: Mat's brief and D-247 settle the scope, and the message texts are shown at the plan gate. D-304 and D-305, added after review round 1, each list their options in §User Review Required, a do-nothing option among them. Carried from the grouping and not relisted in the block, because the grouping's rows hold them: every §8 row, D-240 to D-250, D-267, D-277 and D-280, with stage `grouping`. Of those, D-242 puts the Console fields rider in MEU-115, and D-247 rules that errors always go to a file. The closeout check reads all of them, and D-246 stays as a withdrawn row. The triage decisions D-218, D-234, D-219 and D-220 are in `.agent/context/known-issues.yaml` under `TRANSCRIPT-FAILED-NO-REASON` and `TRANSCRIPT-BLOCK-KEEPS-REQUESTING`. `CONSOLE-FAILURE-DETAIL-LOST` holds no decision log, and the check accepts that (`C:/Temp/av-kit/s50/probe-issue-decisions.txt`).

```yaml
decision_log:
  - id: D-291
    stage: planning
    question: "How does the transcript port report why it has no transcript?"
    resolution: autonomous
    class: two-way
    chosen: "get_transcript returns TranscriptResult or TranscriptSkip; TranscriptSkip carries a closed TranscriptFailureCause that is no_captions or unavailable; a block still raises TranscriptRetryableError and every other failure DomainError"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:536 — the port reports the cause, so no captions and unavailable are told apart", "packages/core/src/avkit_core/ports/transcript.py — None means no transcript today"]
    research: { engine: none, sources: [] }
    reasoning: "A typed skip keeps the exception path for real failures and lets the service map a cause without parsing text. A skip exception would also work but makes an ordinary no-captions video take the error path, and an enum on TranscriptResult would mix a transcript with its absence."
  - id: D-292
    stage: planning
    question: "What does each cause say, and where is the text written?"
    resolution: autonomous
    class: two-way
    chosen: "One failure_message function in the domain holds the four texts; the adapter maps the library's other errors to short reasons from a named map and keeps the library error as __cause__; an error that isn't the library's gives only its class name; an av-kit DomainError's text passes redact_message then safe_reason (first line, URLs to [link], 200 characters); a Failed job stores 'N of TOTAL videos failed. Last: MESSAGE' and a Done job with a skip 'N of TOTAL videos had no transcript. Last: MESSAGE', the upper-case names standing for the count, the total and the last message"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml — TRANSCRIPT-FAILED-NO-REASON D-218: blocked, no captions, unavailable, other with its reason", "packages/infrastructure/src/avkit_infra/transcript/adapter.py:78 — the library text reaches the item today"]
    research: { engine: "uv run python (installed package)", sources: ["youtube-transcript-api 1.2.4 _errors.py — the exception classes", "youtube-transcript-api 1.2.4 _transcripts.py:95-96 — HTTP 429 raises IpBlocked"] }
    reasoning: "One function keeps the card, the API and the Console saying the same words. The blocked text names the next step, as D-218 asks. Class-name fallbacks keep an unknown library error short without showing its paragraphs. A transport error's text can hold a URL with a query token, which redact_message doesn't recognise (review round 1, F2), so it is never kept. A Done job carries its skips because otherwise a one-video job with no captions ends with no reason on its card (F3)."
  - id: D-293
    stage: planning
    question: "How does the API carry the message?"
    resolution: autonomous
    class: two-way
    chosen: "TranscriptJobOut gains last_item_message, set from the latest item when it is Failed or Skipped; error_message carries the job's own message"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:537 — the job carries the message when its last item failed or was skipped", "packages/api/src/avkit_api/routes/transcripts.py — _aggregates already picks the latest item"]
    research: { engine: none, sources: [] }
    reasoning: "The route already reads the latest item for last_title and last_item_status, so one more field costs nothing. A route returning items would be a new surface the residual section doesn't ask for."
  - id: D-294
    stage: planning
    question: "Where does the card show the message?"
    resolution: autonomous
    class: two-way
    chosen: "A Failed, Paused or Done card with error_message shows a job-message line in place of the output tree (a Done job has one only after a skip); a Processing card adds last_item_message to its last-title line, title or not; TR5 names the job-message line"
    source_tag: Local Canon
    precedents: ["docs/build-plan/11-page-layout.md:32 — TR5, line three", "ui/src/renderer/src/features/transcript/TranscriptPage.tsx:97 — Open folder in the kebab menu keeps the folder reachable"]
    research: { engine: none, sources: [] }
    reasoning: "Line three is where the card already says what is happening. Replacing the output tree only when there is a message keeps every other card as it is, and the folder stays one click away."
  - id: D-295
    stage: planning
    question: "What does the service log?"
    resolution: autonomous
    class: two-way
    chosen: "One line per outcome: transcript.item_skipped at WARNING, transcript.item_failed at ERROR and transcript.blocked at ERROR, each with job_id, video_id and error set to the stored message; a retry logs nothing"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:539 — each failure or skip logs one line with the same message"]
    research: { engine: none, sources: [] }
    reasoning: "The same text in the line and on the card is what makes them match. Logging each retry would add a line per attempt for the same cause."
  - id: D-296
    stage: planning
    question: "How do errors always reach the file?"
    resolution: autonomous
    class: two-way
    chosen: "Lines at ERROR or CRITICAL, and events with persist=True, are always appended to console.log; app.log_to_file adds every other line; exception maps to ERROR, fatal to CRITICAL and warn to WARNING; the append catches OSError and runs under its own lock"
    source_tag: Human-approved
    precedents: ["packages/core/src/avkit_core/services/health.py:157 — the file is written only with the toggle on today", ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md — D-247"]
    research: { engine: none, sources: [] }
    reasoning: "D-247 rules that errors go to the file. A second file for errors would also meet it but splits one log in two, and the Console's own path and texts already name console.log. Swallowing OSError keeps a locked file from failing the work that logged."
    human_message_reference: "USER_EXPLICIT 2026-11-05 'D-247: yes they should go to file'"
  - id: D-297
    stage: planning
    question: "Which fields does the Console keep, and how is redaction kept?"
    resolution: autonomous
    class: two-way
    chosen: "video_id, variant_id, device and detail join CONSOLE_FIELDS; each value is made single-line, its URLs become [link], it is redacted, then cut to 300 characters, and the whole message is redacted as today; tts.load_failed adds detail, the first line of the exception text"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml — CONSOLE-FAILURE-DETAIL-LOST: keep the model and the error text after checking redaction", "packages/core/src/avkit_core/services/health.py:46-62 — redact_message fails closed"]
    research: { engine: none, sources: [] }
    reasoning: "The model is variant_id and device, and the error text is detail. Redacting each value before the cut means a cut can't leave half a needle and the secret after it. The limit keeps one bad value from filling a Console row."
  - id: D-298
    stage: planning
    question: "Is the dropped-line race fixed here?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: a thread-local re-entrancy guard replaces the shared _processing flag"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/health.py:131-134 — a second thread's line is dropped while another is processing"]
    research: { engine: "pomera_web_search (tavily)", sources: ["https://www.structlog.org/en/stable/standard-library.html — processors run in the logging thread", "https://uptrace.dev/blog/python-logging — thread-local state in logging"] }
    reasoning: "The transcript worker logs from its own thread, so its error could be dropped while a request thread is logging, and the Console line the Done check needs would be missing. The guard exists only to stop recursion, which is per thread."
  - id: D-299
    stage: planning
    question: "How does a block stop the run?"
    resolution: autonomous
    class: two-way
    chosen: "The same retry loop; once max_retries is exhausted the item stays Pending with retry_count 0 and the blocked message, the job goes Paused with that message, and the worker's pause check runs before the next request; resume clears the job's message; a DomainError still fails only that video"
    source_tag: Research-backed
    precedents: [".agent/context/known-issues.yaml — TRANSCRIPT-BLOCK-KEEPS-REQUESTING D-219", "packages/core/src/avkit_core/services/transcript.py:361 — the worker pauses before _next_job"]
    research: { engine: none, sources: ["Carried from triage D-219"] }
    reasoning: "Reusing the pause path means resume, stop and the runtime state already work. Resetting retry_count gives the video its full retries after resume; keeping it would fail the video on its first attempt."
  - id: D-300
    stage: planning
    question: "How is requests_per_hour enforced?"
    resolution: autonomous
    class: two-way
    chosen: "A sliding-window log of request start times over 3600 s, retries included, on an injected clock; before each request, entries at or before now minus 3600 are dropped and the service sleeps in slices of at most 1 s while the count is at or above the cap, re-reading the cap and the stop and pause flags; 0 turns it off"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml — TRANSCRIPT-BLOCK-KEEPS-REQUESTING D-220: a rolling cap over real requests", "packages/core/src/avkit_core/services/settings.py:59 — requests_per_hour, min 0, default 300"]
    research: { engine: "pomera_web_search (tavily)", sources: ["https://raphaeldelio.com/2025/01/22/sliding-window-log-rate-limiter-redis-java — a log of timestamps over a rolling window", "https://www.crackthat.io/p/build-rate-limiter-python-sliding-window — a deque evicting timestamps outside the window"] }
    reasoning: "A timestamp log is exact at this scale, a few hundred entries. A token bucket would allow bursts the setting's name doesn't promise. Short slices keep stop and pause responsive during a wait of up to an hour. The default settings wait for nothing only without retries; a retry is a start, so a run with retries can meet the cap, which is what D-220 asks (review round 1, F5)."
  - id: D-301
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "Identity; static py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths and red-check-selftest; full py-tests, ui-tests, ui-build, openapi, mcp-types, mcp-tests, state-render and issues-render; runtime ui-electron for the transcript, settings and console specs plus real-log-untouched; mcp-build, mcp-audit and build-record skipped for the reasons in the plan"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:190-207 — the D6 stages", "AGENTS.md:82 — one fresh full scoped gate before final review"]
    research: { engine: none, sources: [] }
    reasoning: "The session changes core, infrastructure, the API contract and the renderer. MCP passes the job through, so its types and tests run as guards and its build has nothing new. mcp-audit would call YouTube."
  - id: D-302
    stage: planning
    question: "Does tts.generate_failed move to ERROR?"
    resolution: autonomous
    class: two-way
    chosen: "No; it stays at WARNING, and no other warning is re-levelled"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/tts.py:344-349 — the warning and its job error_message", ".agent/context/known-issues.yaml — TTS-GENERATE-FAILED-SILENT D-3: the TTS page shows the reason"]
    research: { engine: none, sources: [] }
    reasoning: "The reason already persists on the job and the page. Moving it to ERROR would put it in the file too, which is a reasonable later change, but it reaches past the transcript and Console scope this session holds."
  - id: D-303
    stage: planning
    question: "When does MEU-116 split into Session 50b?"
    resolution: autonomous
    class: two-way
    chosen: "Only on Mat's words, asked at the S8 checkpoint after row 7 when context use is above about half"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:161 — MEU-116 is a 50b candidate past about 50% context"]
    research: { engine: none, sources: [] }
    reasoning: "The grouping sets the threshold, and a split changes the session's records, so Mat decides it."
  - id: D-304
    stage: planning
    question: "What does HealthService hand to structlog's later processors?"
    resolution: autonomous
    class: two-way
    chosen: "Only event (the redacted message), seq and exc_info=False; every other key is dropped, so the stdout line Electron forwards to the Console holds only what the ring holds, and no traceback is printed"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/health.py:159-161 — the original fields go downstream today", "ui/src/main/index.ts:270-275 — every backend stdout line reaches the visible Console", "packages/core/src/avkit_core/services/health.py:99-111 — the processor is inserted ahead of the configured chain"]
    research: { engine: none, sources: [] }
    reasoning: "Redacting the composed message protects the ring and the file but not the renderer that prints the raw fields after it (review round 1, F1). Dropping the keys is fail-closed. Redacting each value in place would leave tracebacks, whose exception text redact_message can't fully clean. A developer loses the stack on stdout; the option to keep it is at the gate. At the execution gate on 2026-11-06 Mat replied 'Go-ahead' to the options shown with A recommended, so A stands."
  - id: D-305
    stage: planning
    question: "How does a transcript skip reach console.log with the toggle off?"
    resolution: autonomous
    class: two-way
    chosen: "transcript.item_skipped stays WARNING and carries persist=True; HealthService appends any event with persist=True, consumes the key and never shows it"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml — TRANSCRIPT-FAILED-NO-REASON D-218: Skipped gets the same treatment", "the goal anchor — every failure or skip reaches console.log"]
    research: { engine: none, sources: [] }
    reasoning: "A skip isn't an error, so ERROR would mislabel it. Adding WARNING to PERSIST_LEVELS would send every warning to the file and undo D-302's scope. A flag on the one event is the narrowest change that meets the anchor; the other options, and doing nothing, are at the gate. At the execution gate on 2026-11-06 Mat replied 'Go-ahead' to the options shown with A recommended, so A stands."
  - id: D-306
    stage: planning
    question: "How does a resume that lands during the worker's pause exit keep its work?"
    resolution: autonomous
    class: two-way
    chosen: "_next_job consumes _pick_processing under self._lock at selection and the reset after _run_parent goes; each worker exit re-checks its flag and clears self._thread inside the lock; resume_processing and start_processing set their flags and check the thread in one critical section"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/transcript.py:373 — the unconditional reset", "packages/core/src/avkit_core/services/transcript.py:225-236 — resume checks the thread under the lock", "packages/core/src/avkit_core/services/transcript.py:355-383 — the worker exits without it"]
    research: { engine: none, sources: [] }
    reasoning: "The block stop publishes Paused while the worker is still alive, so a quick Resume lands in the window the review demonstrated (round 1, F4). Deciding the exit and the thread handle under the same lock means either the worker sees the resume or the resume starts a new worker. It also closes the same window a user's pause has today."
```

## Research References

- youtube-transcript-api 1.2.4, the installed package: `_errors.py` (exception classes) and `_transcripts.py:95-96` (HTTP 429 raises `IpBlocked`). Primary source.
- Sliding window log: https://raphaeldelio.com/2025/01/22/sliding-window-log-rate-limiter-redis-java and https://www.crackthat.io/p/build-rate-limiter-python-sliding-window. Blogs.
- structlog with the standard library: https://www.structlog.org/en/stable/standard-library.html. Official.
- Thread-local state in Python logging: https://uptrace.dev/blog/python-logging. Blog.

## Planning receipts

All under `C:/Temp/av-kit/s50/`. Each probe was read-only with respect to the repository.

- **`probe_issue_decisions.py`, `probe-issue-decisions.txt`** (exit 0). Through the closeout check's own reader, `known-issues.yaml` gives `TRANSCRIPT-FAILED-NO-REASON` [D-218, D-234], `TRANSCRIPT-BLOCK-KEEPS-REQUESTING` [D-219, D-220] and `CONSOLE-FAILURE-DETAIL-LOST` [] with no refusal. An issue the file doesn't hold is refused. So H2-2 passes all three `--decision-issue` flags and the register as a source.
- **The library's exception classes**, listed from the installed 1.2.4 package (2026-11-05).
- **GUI check (create-plan Step 4A): `gui-refs-not-shipped`.** The five reference files that §4A names are absent (`ls`, 2026-11-05), so items 1, 2 and 4 are skipped. Items 3 and 5 still apply:
  - **E2.** The changed output elements are `job-message` (new) and `last-title` (new text). `job-message` is registered as a test id (row 5) and as `JOB_MESSAGE` (row 6). AC-115.14 asserts both elements, and AC-115.17 asserts `job-message` in Electron (row 7).
  - **G32.** The new line uses no raw hex. Any colour is a token class, as on the card's other lines.
  - **G30, G31, G33, G34 and G35** don't apply. The session adds no `<select>`, accent, transition, button or user action, so there is no feedback tier to assign. Help and hint texts change; their controls don't.
- **Not run at plan time:** any test, and any write to the repository.

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths`, `red-check-selftest`.
- **Targeted:** each row's test files, Red then Green; `openapi` in row 4; the E2E spec in row 7; `real-log-check.py --compare` in rows 2, 4, 7 and 9.
- **Fresh full:** `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `state-render`, `issues-render`.
- **Runtime:** `ui-electron` (targeted), `real-log-untouched`.
- **Identity:** from `identity.py`, independent of the receipts.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
