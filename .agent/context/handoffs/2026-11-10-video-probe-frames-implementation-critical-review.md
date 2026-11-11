---
date: "2026-11-11"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md"
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s62-execution-2026-11-10-video-probe-frames"
round: 2
---

# Critical Review: 2026-11-10-video-probe-frames

> **Review Mode:** execution. **Verdict:** approved. **Intent achieved:** yes. Round 2: F1 fixed; no new findings. No open High or Critical findings.

## Intent Anchor

Session 62 gives an agent two read-only steps over a local video. `POST /conversions/probe` and `avkit_convert` `probe` return a video's duration, size, codecs and streams without writing a job. `POST /captures/frames` and `avkit_capture` `frames` write still frames from that video into the capture inbox as new shots, at times the agent names or evenly spaced across a span, so `image`, `crop` and `annotate` work on them. The video is read in place and never changed, and nothing is uploaded.

## Scope

Reviewed both MEU-133 and MEU-134 handoffs, the correlated plan/task, the modified tracked files against HEAD `7b9f34d4e93b9fc733277278859f2b9ec26abdb8`, and the new implementation and test files. Existing baseline plan/review artifacts were context, not newly delivered product. The author was Claude Code/Anthropic; this independent review is Codex. Applied execution-critical-review, IR-1 through IR-7, test rigor, negative-path and evidence checks.

Repository files remained unchanged. Reviewer scripts, clips, receipts and this report are under `C:/Temp/av-kit`. No suites, app/API servers, npm, network requests, inbox/app-data writes or Git mutations ran. The coordinator owns canonical report adoption and ledger recording. H2 remains subsequent authorized coordinator work.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | Medium | no | behavior | AC-134.2 / TIME_PARSE: a finite numeric time such as `1e25`, `1e100` or `1e308` passes `CaptureFramesIn`, but decimal quantization raises `decimal.InvalidOperation` before the maximum-time check. An agent supplying this out-of-range value in `at`, `start` or `end` receives the generic 500 instead of the fixed 422 refusal. Direct schema/parser probes reproduced the exception; the HTTP outcome follows the worker rethrow and existing exception handler. This affects invalid input only and writes no shots, so it does not meet the workflow's High/Critical blocking threshold. Confidence: High. | `packages/core/src/avkit_core/services/video_input.py:184` (bound checked at :168; service callers at `services/capture.py:719`; HTTP fallback at `packages/api/src/avkit_api/errors.py:155`) | Reject values beyond the supported numeric range before quantizing, or safely convert decimal arithmetic failure to the fixed validation refusal. Cover large finite values in `at`, `start` and `end`, including the route response. | fixed |

> Q1–Q7, the original checklist/evidence, verdict and follow-up below retain round 1 observations for continuity. The Round 2 recheck at the end supersedes F1's former open status and the old state/gate counts. Unchanged work was not reviewed again.

## Review Questions

### Q1 — Goal and two agent traces

Accepted. Probe goes through the strict request schema, `require_local_video`, `ConversionService.probe_file`, the unchanged ffprobe fact parser with UTF-8 decoding, and the eleven-field mapper. The successful body intentionally returns the resolved path. URL/directory/missing-file refusals are fixed and do not reach ffprobe. There is no job, queue, output-file or path-bearing log write in this flow. AC-133.1/.3/.4/.5/.7/.8 exercise these boundaries, including `Łodz.mp4` and the logging positive control.

For frames, `[0, "00:01.500", 1.5]` becomes `[0, 1500]`; `(start=10000, end=20000, count=5)` becomes `[11000, 13000, 15000, 17000, 19000]`. The adapter pipes decoded PNG bytes; the service reserves unique temps, validates the images and publishes ordinary shots with `CaptureSource.Video`. The source video is never an output argument. AC-134.5/.6/.7/.10/.12/.14 prove files, rows, source and image bytes. Existing crop/annotation methods select shots by id/path without excluding Video; the existing capture regression suites remain green. There is no missing implementation segment of the registered valid-input intent. F1 is the invalid numeric boundary exception.

### Q2 — Probe, decoding and D-589/D-590

Accepted. `VIDEO_INPUT` covers the enumerated invalid forms and all specified filesystem exceptions. Errors are raised after the handling clause; tests assert exact messages, no cause/context and marker-free formatted exceptions. The probe mapper handles audio-only, neither-codec and no-duration facts; duration rounding is exact half-up for the declared cases. `_run` changes decoding and the optional timeout branch only; callers without a timeout still omit that keyword. The recorded caller run reports 408 passes.

D-589 adds assertions before indexing; it preserves both lookup guards. D-590's stdout `>= 1` still proves the capture can observe the deliberately logged marker; the ring still requires exactly one event, and the preceding negative checks still require zero occurrences. It does not assert that probing itself logs a line. Both rulings and their applied edits are sound.

### Q3 — Atomic writes, names and deadlines

Accepted within the approved D-577/D-587 semantics. Both file-lock acquisitions are bounded. Temp names are exclusively reserved, other writers' temps are respected, and publication rechecks destination collisions. Each failure closes/removes owned temps and removes moved destinations under the lock; the real SQLite tests check rollback and preservation of an existing shot. Scan uses the same lock, so it cannot register a transient publication during rollback.

Probe/grabs get the remaining budget. Each grab's FFmpeg, packet read and retry share one adapter deadline. Checks surround grabs and precede publication and commit. The return gate and commit gate share state under a lock, so an abandoned running worker cannot commit. The approved limits remain: a commit begun before the final check's deadline can finish later; an unresolved commit at 111 s yields a masked 503 with uncertain final persistence. This is disclosed D-587 behavior, not a new all-or-nothing promise. Tests cover both lock waits, expiry during a grab/publication, stuck decode/checkout, slow/stuck commit and exception identity. D-588 preserves AC-8.12's full signature comparison; only the FramePort caller passes `timeout_s`, while all three ConversionService MediaPort calls omit it.

### Q4 — END_GAP and NO_DURATION

Accepted. The real-FFmpeg tests use the actual adapter and compare pixels against independent full-decode references, with differing neighboring-frame positive controls. They cover 0, exact last frame 2.960 s, 2.999 s, VFR, longer audio and at-end refusal before a grab. Raw H.264 is exercised at 1 s with output seek and count refusal. Source hashes and clip-directory inventories are checked.

The reviewer additionally generated a 70 s local MP4 with only 3 s of video. Real adapter grabs at 2960, 2999, 3200, 65000 and 69999 ms all matched reference frame 74; the source SHA-256 was unchanged. This also checked END_GAP beyond a 60 s audio tail. No inbox was involved.

### Q5 — MCP and regression pins

Accepted. Request bodies match their routes, strict schemas reject extras, the frames cap is 20, frames uses 120 s and probe uses the default timeout. The intentional REST/MCP filtering differences for null/negative times are documented. Response transport tests compare complete values as well as key sets. Registry/action counts are 73 and OpenAPI operation count is 76. Shared AC-38/AC-67 markers and AC-130's Crop adjacency/value remain guarded. AC-8.12 was not relaxed.

D-591 composes with the new coverage pin: revert → crop → frames → capture_interactive. It preserves the old relative order while allowing the approved insertion. The pending baseline list and offline audit steps follow the accepted D-499 boundary; no live audit or baseline update is claimed here.

### Q6 — Test rigor and Red/Green evidence

Accepted as real evidence. Independently reran `red-check.py` against all four supplied Red receipts and their preserved exits: Python 133 required 8 tests, MCP 133 required 1, Python 134 required 14, MCP 134 required 2; each returned zero problems. AC-134.1 remains the deliberate passing type-characterisation guard. Initial reviewer attempts using dotted AC ids for Python were corrected to task.md's `test_ac_...` prefixes; those initial invocation mistakes are not deliverable defects.

Recorded counts match: Red Python 71 failed/163 passed and 151 failed/200 passed; Red MCP 17 failed/126 passed and 19 failed/131 passed. Green Python 312 then 770; Green MCP 491 then 498 in 35 files. Full gate: Python 1792, MCP 498 in 35 files, real FFmpeg 23. The gate excuses no baseline failures. Full suites were inspected and reused after identity verification, not rerun by the reviewer.

Each new test function and each changed assertion was audited. Grades below apply to every reviewed test in the named group unless qualified; no trivially passing test was found. F1 identifies a missing extreme-value case, not fabricated Red/Green evidence.

| Test files/group | IR-5 grade | Basis |
|---|---|---|
| `test_video_input.py`, `test_conversion_probe.py` | Strong | Exact values/messages, exception linkage, source preservation, no jobs and no calls on refusals; numeric range coverage misses F1. |
| `test_media_adapter_frames.py` | Strong | Exact argv and decoding, timeout propagation, failures, packet ordering and no retry after expiry. |
| `test_capture_frames_service.py` | Strong | Actual SQLite rollback, all-owned-file inventories, existing-file preservation, barrier concurrency, bounded waits and abandoned workers. |
| `test_api_conversion_probe.py`, `test_api_capture_frames.py` | Strong | Real service/wiring/database/image stack with bounded fakes at media ports; exact bodies, stored rows/files and positive-controlled absence checks. |
| `test_video_real_ffmpeg.py` | Strong | Real binaries, pixel references, neighbor distinction and source hashes. |
| `test_api_openapi.py`, changed API body/route/count pins, `test_domain.py`, `test_domain_capture.py` | Strong | Exact schema/reference/order/census or enum/signature assertions; additions preserve existing checks. |
| MCP `convert.test.ts`, `capture.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, changed fixture tables and runner order/discovery pins | Strong | Exact schema refusals before fetch, bodies, response parity, timeout selection, counts and relative order. |
| New audit `coverage.test.ts` cases | Adequate | Missing-step negative control and exact frames call/cleanup registration; the fake-context execution test does not independently assert the observer's success classification. |

### Q7 — Freshness, records and generated files

Accepted. Recomputed state exactly matches both handoffs and the gate:

`7b9f34d4e93b9fc733277278859f2b9ec26abdb8+eb0ad8111e0de603143b55d4bd3be55581f7f9dc158fc7372d4348aa504ea75b`

`ELECTRON_RUN_AS_NODE` was unset. A scratch `core.excludesFile` excluded only `.claude/settings.local.json`, preserving the harness's existing Git configuration. That secret file was never opened or hashed. UV initially could not use `<HOME>/AppData/Local/uv/cache`; redirecting UV's cache to reviewer scratch with offline mode resolved the environment error. No dependency sync/download ran.

Handoff evidence records agree with inspected receipts and decisive suite summaries. Direct Git/JSON comparison adds only the two paths and six new schemas, with no existing path/schema changes or removals. There are 76 operations. The row-6 diff is confined to the two MEU entries/rows, BUILD_PLAN Total and grouping row 62. All 38 modified tracked files retain their declared LF/CRLF convention. Delivered notes describe the implementation and its accepted limits; F1 qualifies the broad TIME_PARSE refusal claim. Pending review statuses and H2 omissions are intentional.

## Checklist Results

These are observed review checks; `pass` records that the stated audit/evidence check completed, not an assertion that F1 is absent.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| IR-1 real runtime evidence | pass | Codex inspected real-FFmpeg tests and gate receipts, then ran the independent local FFmpeg probe below. | null | Actual adapter and pixel references; recorded 23 passes; independent long-audio probe succeeded. |
| IR-2 collaborator behavior | pass | Codex read fake ports/UoW fixtures and corresponding assertions. | null | Scripted ports preserve inputs; atomicity tests use real SQLite and real rollback. |
| IR-3 error mappings | pass | Codex traced schemas, service exceptions and API handlers. | null | Listed 422/503 bodies are asserted; F1 is the non-blocking outlier. |
| IR-4 prior execution findings | n/a | First execution-review round. | null | No previous execution finding to recheck. |
| IR-5 assertion audit | pass | Codex read all new test files and changed test/pin diffs. | null | Grades and the untested F1 boundary are recorded above; no Weak tests. |
| IR-6 boundary audit | pass | Codex inspected Pydantic/Zod constraints, negative tests and independently probed schema/parser inputs. | null | Explicit strict schemas and refusal cases; F1 reproduced. |
| IR-7 scope/AC integrity | pass | Codex compared all 9 probe and 17 frames ACs with both handoffs, tests and accepted grouping boundaries. | null | No missing AC row or disguised required deferral. |
| DR scope and decisions | pass | Codex compared plan contracts, rulings and current diff. | null | D-588 through D-591 sound; accepted D-573/D-576/D-577 implemented. |
| PR evidence and freshness | pass | `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-review-run.ps1 -Mode identity` | 0 | Exact registered tested_state reproduced. |
| PR generated files and records | pass | `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-review-run.ps1 -Mode evidence` plus read-only record diff inspection | 0 | Two paths/six schemas only; 76 operations; line-ending mismatches `[]`; counts agree. |

### Decisive reviewer evidence

The following wrapper commands used all-stream scratch receipts, preserved child exits and read completed output. Their scratch scripts are inspectable alongside this report.

```json
{"schema_version":"evidence.v1","check_id":"s62-review-identity","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-review-run.ps1 -Mode identity","cwd":"P:/av-kit","scope":"Current D6 input identity with ELECTRON_RUN_AS_NODE unset and only the documented local settings path excluded","phase":"static","exit_code":0,"result":"pass","tested_state":"7b9f34d4e93b9fc733277278859f2b9ec26abdb8+eb0ad8111e0de603143b55d4bd3be55581f7f9dc158fc7372d4348aa504ea75b","output":"7b9f34d4e93b9fc733277278859f2b9ec26abdb8+eb0ad8111e0de603143b55d4bd3be55581f7f9dc158fc7372d4348aa504ea75b"}
```

```json
{"schema_version":"evidence.v1","check_id":"s62-review-time-and-path-probe","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-review-run.ps1 -Mode probe","cwd":"P:/av-kit","scope":"Independent TIME_PARSE, FRAME_TIMES, FRAME_NAME, VIDEO_INPUT and request-schema observations","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7b9f34d4e93b9fc733277278859f2b9ec26abdb8+eb0ad8111e0de603143b55d4bd3be55581f7f9dc158fc7372d4348aa504ea75b","output":"DEDUP [0, 1500]; SPAN [11000, 13000, 15000, 17000, 19000]; NAME Łodz-t00h00m01.500s; six PATH_REFUSAL observations had cause/context None. F1 reproduced: TIME 1e+25 => InvalidOperation; also 1e+100 and 1e+308; SCHEMA_ACCEPTS each value. This probe records the defect rather than certifying those inputs as correct."}
```

```json
{"schema_version":"evidence.v1","check_id":"s62-review-red-receipts","procedure":"Run s62-review-run.ps1 modes red133py, red133mcp, red134py and red134mcp separately; inspect each preserved exit and red-check summary against the supplied historical Red receipt and its .exit file.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"All required Python and MCP Red families; AC-134.1 excluded by design","phase":"red","exit_code":null,"result":"pass","tested_state":"7b9f34d4e93b9fc733277278859f2b9ec26abdb8+eb0ad8111e0de603143b55d4bd3be55581f7f9dc158fc7372d4348aa504ea75b","output":"Each command exited 0. red-check: 1 receipt(s), respectively 8, 1, 14 and 2 required test(s), 0 problem(s) in every case."}
```

```json
{"schema_version":"evidence.v1","check_id":"s62-review-real-end-gap","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-review-run.ps1 -Mode ffmpeg","cwd":"P:/av-kit","scope":"Real pinned adapter against reviewer-generated 70 s local MP4 with 3 s video; all files under review-tmp","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7b9f34d4e93b9fc733277278859f2b9ec26abdb8+eb0ad8111e0de603143b55d4bd3be55581f7f9dc158fc7372d4348aa504ea75b","output":"GENERATE_EXIT 0; PROBE 70.0 160 120; GRAB 0 bytes 11064; GRAB 2960, 2999, 3200, 65000, 69999 each bytes 14422 and last_frame_equal True; SOURCE_UNCHANGED True. The first frame differed from the reference last frame, as expected."}
```

## Verdict

**approved — intent achieved: yes.** The valid local-video probe and still-frame workflows are implemented and supported by fresh, matching gate evidence and independent probes. F1 is a real, bounded invalid-input error-mapping defect; it is Medium and non-blocking under this loop's Verdict Rule. No evidence-backed High or Critical finding prevents approval.

## Follow-up and residual risk

Address F1 with a numeric range guard and regression coverage. Any resulting code/test change invalidates affected evidence and needs the corresponding checks; this reviewer made no correction. Retain the accepted raw-stream cost, requested-time semantics, `_run_with_progress` decoding limit and D-587 uncertain-commit outcome. Full suites were not rerun during this read-only review. This report does not claim H2 completion or supply commit/push authorization.

## Recheck (Round 2)

**Date:** 2026-11-11. **Reviewer:** codex-independent-reviewer (Codex; independent of Claude Code/Anthropic). **Scope:** F1 and D-592 only, the three-file correction, targeted updates to the two work handoffs, and matching evidence. No repository file was edited. All new reviewer files are under `C:/Temp/av-kit`. No suite, app/API, network, MCP server, Git mutation or process termination ran.

### Corrections Applied

- Checked `video_input.py:31-33,184-187` against `C:/Temp/av-kit/s62/pre-d592/video_input.py`: only the documented constant/comment and `or abs(value) > _FLOAT_SECONDS_GUARD` were added. The magnitude guard is 1e9 s and precedes Decimal conversion/quantization, as D-592 requires. The existing negative/nonfinite refusals remain.
- Checked `tests/unit/test_video_input.py:353-367`: `1e25`, `1e100`, `1e308`, `-1e25`; exact `ValidationError` type, fixed message and no cause/context. Catching `Exception` makes a wrong exception fail at an assertion; it does not swallow a failure. Grade: Strong.
- Checked `tests/e2e/test_api_capture_frames.py:352-374`: huge `at` (including a valid first item), `start`, and `end`; exact 422/error body, no grabs, empty inbox, zero rows and unchanged source bytes on the existing real stack. Grade: Strong. All three caller fields use the corrected parser (`services/capture.py:719-721`).
- Checked both Red attempts and the final Red/Green receipts. The refused first attempt remains disclosed; the accepted Red has exit 1, 7 failed/1 passed, with three exact-type and four HTTP assertions. Negative `-1e25` already passed. The independent red-check rerun passes for both required test names. Green exit 0 has 349 passed in 7.95 s, clean ruff, three files already formatted and pyright 0 errors/warnings/informations.
- Checked the updated gate receipt and its step details: 16 executed stages exit 0, Python 1800 passed, MCP 498 in 35 files, real FFmpeg 23 passed; 57 changed paths, outside scope `[]`, no moved HEAD or altered baseline-dirty inputs. `session-gate: all steps exit 0` is the last line. These are inspected coordinator results, not reviewer suite reruns.
- Checked the MEU-134 handoff's AC-134.2/.13 rows, FAIL_TO_PASS, D-592 Red/Green records, gate record, changed-file/departure notes and D-592 decision against the corrections and receipts. Checked the MEU-133 handoff's shared gate/quality/departure updates. Both full-gate records bind to the current state. The nonfinite receipt has three fixed 422/no-grab/empty-inbox observations and a disclosed SQLite cleanup PermissionError/exit 1; it is not represented as a successful executable check.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Boundary and Fix Generalization

F1 is fixed for huge finite inputs in each of `at`, `start` and `end`. Every finite float above 1e9 returns the parser's refusal sentinel before Decimal; every negative finite float is already refused by the existing negative check. For the remaining nonnegative floats through 1e9, Python's shortest float representation has at most 17 significant digits and multiplying by 1000 stays within the default 28-digit Decimal precision. The largest quantized integer has 13 digits (1,000,000,000,000); even the smallest subnormal rounds safely to zero. Thus quantization cannot reproduce F1 anywhere in this remaining interval. Default Decimal precision was observed as 28; no new decimal-context policy is introduced.

Independent probes compared 9,325 nonnegative finite floats with the pre-fix parser: deterministic random values across the supported and guard intervals, powers of two and adjacent representable values through the subnormal range, rounding thresholds and the guard boundary. All outcomes matched, including exact errors and linkage. A Decimal spy confirms exactly 1e9 still reaches quantization while the next representable larger float does not. Ten boundary/extreme values, including the largest finite float and a huge negative, yield the exact unchained refusal through each request field.

`TIME_MAX_MS` still tests the rounded milliseconds: every result greater than 359,999,999 is refused. Existing half-up semantics are unchanged: 359999.999 and 359999.9994 seconds both round to 359,999,999 ms; 359999.9995 and 360000 seconds are refused. Consequently, a literal claim that every raw float above 359999.999 seconds is rejected would overstate the pre-existing contract. This correction preserves that accepted rounding behavior; no new finding is raised on unchanged semantics.

### IR-5 and Adversarial Checks

Both new test functions are Strong. Reviewer-only scratch variants that (a) keep only the old sign check or (b) put the magnitude refusal after quantization reproduce `InvalidOperation` on each of 1e25, 1e100 and 1e308. Those outputs fail the unit test's exact-type assertion; the preserved pre-fix API Red separately proves HTTP 500 fails the route assertions. The negative case's Red pass is correctly disclosed: it preserves the existing sign behavior, and does not alone distinguish `abs(value) > guard` from a positive-only upper guard when `value < 0` already refuses negatives. Direct source inspection confirms D-592's requested magnitude expression.

AV-1 through AV-6 pass for the delta: decisive failing/passing proof, no assertion bypass or masking skips, explicit assertions on the changed behavior, no placeholder, and sourced D-592 authority. Q1–Q7 stand for unchanged work; only the old extreme-time qualification and old evidence identity/counts are superseded here. No new concrete behavioral failure was found.

### Current Tested State

`7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651`

**Equals expected: yes.** Recomputed using `uv run --no-sync python -B docs/execution/plans/2026-11-10-video-probe-frames/identity.py --state-only`, with `ELECTRON_RUN_AS_NODE` unset, bytecode disabled, offline UV/cache and TMP/TEMP under reviewer scratch. A process-local Git `core.excludesFile` contains only `/.claude/settings.local.json`; existing harness Git configuration entries are preserved. That file was never opened or hashed. This reconciles the sandbox's missing user ignore file without changing repository Git configuration. Both handoffs' gate records and the gate's before/after states equal this value. D-592 Red/Green deliberately retain their historical pre-fix/fix phase descriptions.

### Round 2 Checklist and Decisive Evidence

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| F1 / AC-134.2 and AC-134.13: refusal and unchanged accepted times | pass | rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-r2-run.ps1 -Mode probe | 0 | 10 finite boundary/extreme values across at/start/end give the exact unchained ValidationError. 9,325 nonnegative floats through 1e9 match pre-fix results. 1e9 reaches Decimal; its next larger float does not. Both wrong-fix variants reproduce InvalidOperation for all three positive huge cases. |
| IR-5: D-592 Red evidence | pass | rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-r2-run.ps1 -Mode red | 0 | red-check: 1 receipt(s), 2 required test(s), 0 problem(s). Preserved Red exit 1: 7 failed, 1 passed; three exact-type failures and four HTTP 500 != 422 failures. The negative case already passed. |
| Current tested_state | pass | rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-r2-run.ps1 -Mode identity | 0 | 7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651; equals expected. ELECTRON_RUN_AS_NODE unset; scratch Git exclusion contains only /.claude/settings.local.json, which was never opened or hashed. |
| D-592 and full-gate evidence matches receipts | pass | rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-r2-run.ps1 -Mode records | 0 | Both handoffs gate records match current identity and receipts: 16 executed stages exit 0, Python 1800, MCP 498/35, real FFmpeg 23; 57 paths, none outside scope. D-592 Red/Green records match; Green exit 0, 349 passed; ruff/format/pyright clean. Nonfinite probe cleanup exit 1 remains disclosed. |
| Delta inspection / D-592 / IR-5 / AV-1 through AV-6 | pass | Compare video_input.py against the pre-D592 copy; inspect both added test functions and targeted handoff corrections, ruling and source call sites. | null | Only the documented guard/comment changed in product code. Both added tests are Strong: exact exception/body and no-write assertions, no bypasses/skips/placeholders. D-592 supplies authority. No new behavioral defect found; round 1 Q1-Q7 stand for unchanged work. |


```json
{"schema_version": "evidence.v1", "check_id": "s62-r2-boundary-and-mutations", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-r2-run.ps1 -Mode probe", "cwd": "P:/av-kit", "scope": "F1 / AC-134.2 and AC-134.13: refusal and unchanged accepted times", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651", "output": "10 finite boundary/extreme values across at/start/end give the exact unchained ValidationError. 9,325 nonnegative floats through 1e9 match pre-fix results. 1e9 reaches Decimal; its next larger float does not. Both wrong-fix variants reproduce InvalidOperation for all three positive huge cases."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s62-r2-red-check", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-r2-run.ps1 -Mode red", "cwd": "P:/av-kit", "scope": "IR-5: D-592 Red evidence", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651", "output": "red-check: 1 receipt(s), 2 required test(s), 0 problem(s). Preserved Red exit 1: 7 failed, 1 passed; three exact-type failures and four HTTP 500 != 422 failures. The negative case already passed."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s62-r2-current-identity", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-r2-run.ps1 -Mode identity", "cwd": "P:/av-kit", "scope": "Current tested_state", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651", "output": "7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651; equals expected. ELECTRON_RUN_AS_NODE unset; scratch Git exclusion contains only /.claude/settings.local.json, which was never opened or hashed."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s62-r2-receipt-crosscheck", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s62-r2-run.ps1 -Mode records", "cwd": "P:/av-kit", "scope": "D-592 and full-gate evidence matches receipts", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651", "output": "Both handoffs gate records match current identity and receipts: 16 executed stages exit 0, Python 1800, MCP 498/35, real FFmpeg 23; 57 paths, none outside scope. D-592 Red/Green records match; Green exit 0, 349 passed; ruff/format/pyright clean. Nonfinite probe cleanup exit 1 remains disclosed."}
```

### Verdict

**approved — intent achieved: yes. F1 fixed; no new findings.** The correction removes the huge-finite-time 500 while preserving previously accepted times. Matching current identity, historical assertion failures, regression passes and gate receipts support approval. The complete rolling report is for coordinator adoption and ledger recording; no repository status or H2 artifact is changed here. Full suites were not rerun. The accepted round 1 residual limits remain.
