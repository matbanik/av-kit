---
date: "2026-11-10"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s62-plan-canonical-2026-11-10-video-probe-frames"
round: 4
---

# Critical Review: 2026-11-10-video-probe-frames

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.

## Intent Anchor

Session 62 gives an agent two read-only steps over a local video. `POST /conversions/probe` and `avkit_convert` `probe` return a video's duration, size, codecs and streams without writing a job. `POST /captures/frames` and `avkit_capture` `frames` write still frames from that video into the capture inbox as new shots, at times the agent names or evenly spaced across a span, so `image`, `crop` and `annotate` work on them. The video is read in place and never changed, and nothing is uploaded.

## Scope

Reviewed the working-tree implementation plan and task, all four plan-local scripts, the cited core/adapter/API/MCP boundaries, affected test pins, 08's residual probe contract, 09's frames contract, the relevant design sections, grouping and MEU-133/MEU-134 by id. Independently observed branch `main`, HEAD `7b9f34d4e93b9fc733277278859f2b9ec26abdb8`. The implementation rows remain unchecked; isolated S11 confirms the new production names are absent.

Claude Code/Anthropic authored this plan. Codex is the independent reviewer and did not author it. Applied PR-1 through PR-9 and the Materiality Gate. Accepted the supplied prior approvals, design D-1–D-5, grouping D-500–D-505 and exclusions. D-573, D-576 and D-577 remain Mat's decisions; this review chooses none of them.

No repository file was edited. All reviewer scripts, generated clips, receipts and this report are under `C:/Temp/av-kit`. No product suite, baseline/session gate, backend, MCP server or network request was run. The unrelated proposal, secret/configuration paths and fleet hub were not opened.

## Findings

All three findings have **High confidence**, concern the deliverable and are **behavior** findings. None is a control-defeat finding. Their violated ledger families are F1: **AC-133**; F2 and F3: **AC-134**.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | VIDEO_INPUT omits RuntimeError from its filesystem error mapping. On the pinned Python runtime, resolving a self-referential symlink under the review directory raised RuntimeError("Symlink loop from ...") containing the input name. A resolve-before-is_file implementation following line 124 lets this escape both new entrypoints; the existing unhandled-error handler returns 500 and logs the path-bearing exception. This violates AC-133.1/AC-133.5's fixed, path-free refusals (and AC-134.13 on frames). | `docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md:124; packages/api/src/avkit_api/errors.py:77; packages/api/src/avkit_api/errors.py:155` | Specify safe symlink-loop handling, mapping the pinned runtime's resolution failure to the fixed ValidationError without exposing its context. Add service/API cases with a symlink loop and a marker, asserting 422, no probe/grab/write, and no marker in the console, stdout or stderr. | open |
| F2 | High | yes | behavior | FRAME_DEADLINE does not bound the promised call. END_GAP explicitly invokes the existing _run, whose subprocess.run has no timeout; RUN_UTF8 changes only decoding. Thus an empty input grab can enter an unbounded packet scan and return a successful final frame after the client's timeout, with no subsequent grab to trigger AC-134.8's clock check. Separately, D-577 B sets a 100 s service deadline while FRAMES_MCP retains the 30 s client timeout: a successful 40 s grab can publish shots after the agent receives a timeout. AC-134.8/.9/.15 do not exercise either schedule. | `docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md:132; docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md:139; docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md:142; packages/infrastructure/src/avkit_infra/media/adapter.py:263` | Use one remaining budget across the initial grab, packet lookup and retry, with a bounded packet subprocess and an expiry check before publication. Specify a service budget below the selected client timeout for every D-577 option, including B, without choosing Mat's option. Extend the clock/subprocess/MCP cases to prove fallback exhaustion and the 30 s branch cannot publish late. | open |
| F3 | High | yes | behavior | FRAME_TIMES can round a midpoint onto the excluded end. The exact formula gives [0,1,2,3] for (start=0,end=3,count=5), contradicting AC-134.3's three collapsed times, and [0,1] for (0,1,2), including end. On a 3 s clip, start=2.999,end=3,count=2 yields [2999,3000], so the plan schedules a grab at the video's duration despite 09's requirement to reject such a time before any grab; on an interior span it returns a frame outside the requested interval. The existing FRAME_CHECKS checks the supplied start/end but does not prevent this generated endpoint. | `docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md:134; docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md:135; docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md:242; docs/build-plan/09-screenshot-capture.md:1128` | Define millisecond quantization that stays within [start,end), such as capping rounded midpoints at end_ms-1 before deduplication. Reconcile AC-134.3's endpoint expectations during plan corrections and add a service case at the actual duration proving no generated time reaches or exceeds end. | open |

## Q1 — Goal and the two calls

**Probe:** `avkit_convert probe` → PROBE_MCP strict member → ACTION_INDEX → POST route → VIDEO_INPUT → PROBE_MAP → existing MediaPort.probe → adapter JSON/RUN_UTF8 → TIMECODE → the eleven-field 200 body. AC-133.3/.4 prove the mapping and absence of a job/queue mutation; .7 is the real adapter proof. This ordinary path is coherent, subject to F1 and Mat's D-573 ruling.

**Frames, then image:** FRAMES_MCP → FRAMES_ROUTE → FRAME_CHECKS/VIDEO_INPUT/TIME_PARSE → FRAME_TIMES → FRAME_NAME → FRAME_WRITE's reservations → FRAME_GRAB/END_GAP under FRAME_DEADLINE → VIDEO_SOURCE registration → 201 → list/get/image. For a 3,000 ms clip, count 5 gives 300, 900, 1500, 2100, 2700 ms. AC-134.5–.17 cover the refusal/write/registration/transport chain. New shots enter the existing source-independent image, crop and annotate paths; the planned guards protect those paths.

The source is used only as FFmpeg's input, FFmpeg outputs PNG to a pipe, and FRAME_WRITE owns only new inbox paths. That trace supports “read in place and never changed”; the ACs do not explicitly hash the source video before/after. Adding that assertion to the existing real test would strengthen direct behavioral evidence. No output upload is introduced. Every substantive spec rule has a planned row/AC, but F1–F3 prevent the full intent from holding for all allowed inputs. The documented D-575/D-583 departures and pending human alternatives are disclosed.

## Q2 — VIDEO_INPUT and TIME_PARSE

The URL-prefix rule preserves single-letter Windows drives and UNC paths while refusing `http:`, `file:` and `ftp:`; the length/control/surrogate checks precede filesystem work. Filesystem calls are placed inside the try, but its exception list is incomplete: **F1** is a real pinned-runtime counterexample.

TIME_PARSE's numeric/string distinction, ASCII grammar, minute/second bounds and 99:59:59.999 ceiling are coherent: `1:60`, `100:00:00`, 360000 and string `"0.0005"` fail; the maximum string succeeds. The independent Decimal probe confirms numeric 0.0005 → 1 and 1.0005 → 1001. Fixed refusal text echoes no raw time. These are sound autonomous D-578 choices.

## Q3 — PROBE_MAP, RUN_UTF8 and routing

The eleven fields match 08:623 exactly. Existing MediaInfo supplies codec-presence booleans, container, dimensions and fps; duration conversion supplies the nullable pair. `raise ... from None` suppresses the underlying probe traceback context, and mapped 422s are not logged by the existing domain handler. The fixed message, rather than exception chaining alone, keeps stderr out of the response.

Probe5 genuinely records cp1252 reader-thread UnicodeDecodeError and all-None results for the Ł name/tag, while its CJK/emoji examples happen to work. AC-133.7 therefore tests a real defect under D-573 A. Two subprocess decoding keywords preserve argv, capture, checking and return-code handling for the six existing call sites; the conversion/resolver tests use keyword-tolerant fakes. The sixth call at adapter:518 is the GPU encoder smoke, not an extract-specific probe as the brief loosely describes; extract itself reaches the existing probe. The named guards cover those surfaces. No finding reopens _run_with_progress.

Declaring POST /probe before /{id}, and adding it to STATIC_BEFORE_ID, is correct. D-573 B's known limitation is accurately disclosed; its related frames Unicode expectation needs the conditional note below.

## Q4 — FRAME_GRAB and END_GAP

Probe13 establishes input-seek's at-or-after behavior on CFR/VFR fixtures and the real end gap. Integer formatting gives exact millisecond arguments. The last-packet fallback is needed for valid requested times after the final video frame; D-575 states its revision of design D-7, and the description explains the exception to at-or-after.

Probe4's parser takes the **maximum numeric PTS**, ignoring N/A; that is the implementation to carry forward because B-frame packet order need not be PTS order. A read starting at an earlier keyframe does not by itself omit later packets. Independently generated a 3 s video with 90 s audio: T=80/F=20 still found last video PTS 2.96 on the pinned pair. Thus a long audio tail is not a supported finding. Missing usable PTS should produce the stated empty result rather than an invented timestamp. The single retry just before last_ms, with no recursive fallback, is sound for the measured CFR/VFR boundaries. **F2** concerns the unbounded packet subprocess, not the need for END_GAP.

## Q5 — NO_DURATION and D-576

The receipts support the claim for the probed raw H.264 stream, including T=0; they do not prove every possible no-duration format behaves identically. Probe4/4b substantiate increasing output-seek cost, including 76.4 s at 540 s on raw 4K HEVC. A's bounded output seek is appropriate in principle; B's refusal and C's loss of raw-stream at support are honestly disclosed departures. AC-134.11 distinguishes the three results.

Under D-577 A, the initial output-seek subprocess receives the remaining budget and has no END_GAP fallback. Under D-577 B, the plan's 100/30 s mismatch remains **F2**. No ruling on A/B/C is made here.

## Q6 — FRAME_WRITE and FRAME_NAME

The three-phase design reuses the approved import ownership contract correctly: reserve by xb temps under the lock; release the lock for expensive grabs; close handles before Windows replace; reacquire the lock for destination/row recheck, replace/probe/upsert and one commit. Twenty ordinary handles do not approach the normal process handle limit. Other cooperative writers see the reserved temps through _import_dest; a person-created file or row encountered later forces a new name. A directory collision fails safely instead of replacing that directory.

Tracking only successfully created temps and actually moved destinations, closing all handles and rolling back the single UoW supports all-or-nothing cleanup without touching another writer's temp. AC-134.6 probes grab/signature/probe failures; .7's barrier sits in the fake grab after phase-1 reservations, so both calls really hold temps together. FRAME_NAME retains import_stem's approved normalization and suffix rules. No new failure was established on this surface.

## Q7 — Checks, spacing and deadline

FRAME_CHECKS puts input/schema/time/count/probe/range checks ahead of grabs and inbox writes; end equal to duration is allowed as the exclusive span endpoint while at/start equal to duration are refused. The explicit AC refusal cases support that order. **F3** is the exception: generated midpoint times are not kept inside that endpoint.

The injected monotonic clock and remaining-time argument are useful, but checking only before each grab does not make the full call bounded. **F2** names the exact unbounded packet path and the inconsistent B timeout schedule. AC-134.8 currently proves only exhaustion before a later grab, so it can pass despite either late-publication case.

## Q8 — API/MCP shapes and descriptions

Strict count/time item types reject booleans, fractional counts and time objects; both schemas bound arrays and count, forbid extras and enforce the at/count shape. The refinements fit the repository's ordinary Zod union. Under A only, the timeout selection adds frames, as stated.

The schemas are not byte-for-byte identical accepted sets: Pydantic's optional nullable fields allow, for example, count with start:null, while Zod's optional non-null timeValue refuses it; MCP also rejects negative numeric times earlier than the service-backed REST path. This does not make a documented normal call fail, but parity language should distinguish transport shape/response parity from identical early filters.

FRAMES_TEXT retains Workflow/Prerequisite/Returns/Errors for AC-38.5 and AC-67.17, correctly names the available probe → frames → image workflow (D-583), and describes the end-gap exception and new-shot behavior. Both response bodies are JSON without PNG bytes. B's selected count cap must propagate into schemas/text as noted below.

## Q9 — Pins

The named enum, route, action, fixture and M7 pins are substantially correct; the semantic absence-pin claim is supported. The other __members__ test at test_domain_capture.py:610 pins Import after Scan and does not need to move. The models-assets last-row assertion also remains valid because both new rows are inserted before the existing final models row.

One additional literal was found: **mcp-server/tests/audit/runner-fake-backend.test.ts:77** still expects 71 discovered actions from the built server. Add this file to Pins that move, Files Modified, baseline anchors and the session-gate allowed set; move 71 → 72 → 73 in the corresponding Red rows. Build MCP before a Green whole-suite run that consumes dist. This is an inferable count/inventory correction, **Low and non-blocking**, not a fourth blocking finding.

## Q10 — Values and console

The intended boundaries are sound: success-body path fields are allowed; raw time is normalized before error interpolation; FFmpeg stderr is discarded; _upsert_shot's capture.registered contains only id and source. AC-133.5 builds HealthService first and includes a positive control. AC-134.13 inherits that stated Session 54 procedure and also calls for a positive control. The existing mapped 503 handler masks write errors without logging their context.

**F1** supplies an uncovered path-bearing exception that reaches api.unhandled_error and the console instead. Extend the marker oracles to that real filesystem failure. RUN_UTF8 A removes the already-demonstrated decoding traceback; B explicitly retains the pre-existing issue.

## Q11 — Reds, identity, scope and safety

Row 1 supplies the behavior names the required Reds actually call. The four schema names are declared-new in red-check.py but are created later; endpoint-based API Reds do not need to import them. Assertion-first status/schema/value checks avoid import/collection/timeout Reds. The require sets cover the new failing ACs, excluding the passing characterization AC-134.1; row 4a separately runs that guard. Both allowed selftests passed.

Existing CRLF/LF preservation is explicit, byte-aware and consistent with the supplied endings receipt; new files are LF. Identity binds code/tests/config, renders/grouping/specs, runtime and the pinned FFmpeg pair; its mutation selftest passes. The current inventory matches the allowed set except the additional count-pin file above. Baseline-dirty SHA checks protect unrelated paths; shared paths intentionally written by this plan are exempt from the later byte comparison and rely on the stated S3/S15 pre-write checks, rather than a claim that the gate alone detects every concurrent overlapping edit.

Executed only the extracted read-only S14/S8/S11 Python blocks: S14 refused all three unruled decisions, as intended; S8 read the requested MEUs correctly and verified release ancestry; S11 passed its positive/absence shapes. No demonstrated materially missing-deliverable false pass was found.

All new real-test clips are planned from lavfi under tmp_path, with the pinned pair; the new module is explicitly CI-deselected beside Extract. The optional audit steps are coverage definitions, not authorization to run the live audit. No described test needs a real user video or network. Review probes used only their own generated Temp clips.

## Non-blocking correction notes

- Apply the missing runner count/inventory/build correction in Q9.
- If Mat selects D-573 B, condition AC-134.10's Ł frame success case as well as AC-133.7's Ł probe cases; otherwise that real frames test demands the behavior B explicitly declines. If Mat selects D-577 B, propagate the chosen 10 cap through FRAMES_ROUTE, FRAMES_MCP, descriptions and boundary tests. The task already requires option-dependent edits before row 0; these are specific entries for that sweep.
- A before/after video hash in the existing real probe/frames tests would directly exercise the source-unchanged promise. No missing product write path was found by the read-only call trace.

## Checklist Results

### Plan Review (PR)

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Manual comparison of rows 0–6 and H1/H2 with plan work packages and ACs; codex-independent-reviewer | null | Same MEUs, order, routes and outputs |
| PR-2 Unstarted | pass | Isolated S11 via static_probes.py; task read | 0 | All new production names absent; rows unchecked |
| PR-3 Task contract | pass | Manual task-table inspection; codex-independent-reviewer | null | Named owners, deliverables, commands and statuses |
| PR-4 Validation realism | fail | Manual deadline call-chain and option trace plus contract_probes.py; codex-independent-reviewer | null | F2 cases escape the present clock/timeout oracles |
| PR-5 Source-backed rules | pass | Manual spec/design/grouping/decision cross-read; codex-independent-reviewer | null | Explicit sources and human departures; rulings remain pending |
| PR-6 Corrections readiness | pass | Manual Handoff Set and review-route read; codex-independent-reviewer | null | Both MEU handoffs and rolling review named; round 1 |
| PR-7 Scope discipline | pass | Manual scope comparison with accepted design/grouping; codex-independent-reviewer | null | Sheet/export/eval and named exclusions remain outside Session 62 |
| PR-8 Reachability/totality | fail | static_probes.py and manual production trace; codex-independent-reviewer | null | F1 exception classification and F2 budget gaps |
| PR-9 Single statements | fail | edge_probes.py and comparison of FRAME_TIMES/AC-134.3/spec; codex-independent-reviewer | null | F3's live interval/formula expectations disagree |

### Decisive evidence

All Python commands below ran with PYTHONDONTWRITEBYTECODE=1. Selftests also had TMP/TEMP set to C:/Temp/av-kit/s62/review. Scripts shown here are reviewer-owned Temp scripts, not product tests. Wrapper exits are separated from inner extracted-check exits.

```json
{"schema_version":"evidence.v1","check_id":"s62-review-midpoints","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s62/review/edge_probes.py","cwd":"P:/av-kit","scope":"exact FRAME_TIMES formula, Decimal rounding and generated long-audio-tail clip","phase":"targeted","exit_code":0,"result":"fail","tested_state":"main 7b9f34d4e93b9fc733277278859f2b9ec26abdb8; round-1 working-tree plan","output":"FRAME_TIMES start=0 end=3 count=5: [0, 1, 2, 3]; all_in_span=False. start=0 end=1 count=2: [0, 1]; all_in_span=False. Decimal 0.0005 ->1; 1.0005 ->1001. Generated 90 s audio/3 s video: T=80 F=20 found max_pts=2.96."}
{"schema_version":"evidence.v1","check_id":"s62-review-resolution-and-baseline-blocks","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s62/review/static_probes.py","cwd":"P:/av-kit","scope":"isolated read-only S14/S8/S11 blocks and Temp self-loop resolution","phase":"targeted","exit_code":0,"result":"fail","tested_state":"main 7b9f34d4e93b9fc733277278859f2b9ec26abdb8; pinned Python runtime","output":"isolated ruled exit=1: D-573/D-576/D-577 unruled; isolated queue exit=0; isolated shapes exit=0; VIDEO_INPUT resolve self-loop: RuntimeError covered_by_list=False message_has_input_name=True; message=Symlink loop from the Temp self-loop path. runner-fake-backend.test.ts allowed=False."}
{"schema_version":"evidence.v1","check_id":"s62-review-unbounded-run","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s62/review/contract_probes.py","cwd":"P:/av-kit","scope":"existing _run function extracted by AST and invoked with a recording fake; generated two-video-stream clip","phase":"targeted","exit_code":0,"result":"fail","tested_state":"main 7b9f34d4e93b9fc733277278859f2b9ec26abdb8; current adapter.py","output":"END_GAP existing _run subprocess keywords: capture_output=true, check=false, text=true; timeout=None. D-577 B's 100 s deadline permits a successful 40 s grab beyond the 30 s client timeout (contract schedule, not a timed live request). The two-stream fixture selected v:0 at T=0 and T=2; no stream-selection finding raised."}
{"schema_version":"evidence.v1","check_id":"s62-review-redcheck-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/red-check.py --selftest","cwd":"P:/av-kit","scope":"Red receipt parser fixtures","phase":"static","exit_code":0,"result":"pass","tested_state":"round-1 red-check.py","output":"red-check selftest: 43 fixture(s) (13 positive, 30 negative), 0 wrong: []"}
{"schema_version":"evidence.v1","check_id":"s62-review-identity-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/identity.py --selftest","cwd":"P:/av-kit","scope":"scratch repository identity mutations, including FFmpeg-pair runtime identities","phase":"static","exit_code":0,"result":"pass","tested_state":"round-1 identity.py","output":"identity selftest: 0 failure(s)"}
```

Other commands executed were bounded numbered Get-Content reads through `rtk proxy pwsh`, `rtk proxy rg -n` pin/absence sweeps in tests/, mcp-server/tests/ and ui/tests/, and read-only `rtk proxy git rev-parse HEAD` / `rtk proxy git branch --show-current`. Their receipts are `C:/Temp/av-kit/s62-review-*.txt`; decisive observations are embedded above. An exploratory rg named a nonexistent test_media.py and returned 2; that path is not an asserted plan dependency. An initial AST probe failed before invocation because generated AST locations were missing; after fixing the reviewer script, the recorded successful run above supplies the evidence.

The supplied D-504 receipts were read, not rerun: probe13's framemd5/no-duration/pipe results; probe2's 13.6/13.8 s timings; probe4/4b's packet/output-seek measurements; probe5's actual locale failure. These substantiate the plan's briefs, not implementation completion.

## Verdict

**changes_required** — the ordinary journeys are well covered, but VIDEO_INPUT can leak an invalid path into the console, FRAME_DEADLINE permits late publication, and FRAME_TIMES can schedule the excluded endpoint. Correct F1–F3 through /plan-corrections and recheck the complete rolling report in this same loop. Preserve Mat's pending D-573/D-576/D-577 decisions; approval of a corrected plan does not authorize execution.

Residual verification limit: this is an unstarted-plan review. No new product behavior, full gate or real service timeout has been executed; the report distinguishes static call-chain conclusions, supplied planning receipts and independently run Temp probes.


## Recheck (2026-11-10)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | open | partial |
| F2 | open | partial |
| F3 | open | fixed |

### Confirmed Fixes

- `implementation-plan.md:126`, `:205`, `:209`, `:247`, `:255`: VIDEO_INPUT now catches the pinned runtime's symlink-loop RuntimeError. The helper, probe API, frames service and frames API all have planned loop cases. Fixed messages and suppressed formatted context address the original unhandled 500/console leak. Probe API explicitly asserts no probe; frames cases assert no grab. F1's narrower remaining context issue is below.
- `implementation-plan.md:133`, `:134`, `:140`, `:141`, `:250`, `:251`, `:257`: FRAME_GRAB has one deadline shared by its initial subprocess, END_GAP packet read and retry. The packet read no longer uses unbounded _run. Checks after each grab and after acquiring the phase-3 lock prevent publishing bytes returned after expiry or publishing after a lock wait that has already expired. FRAME_WRITE's failure cleanup covers both checks. AC-134.8/.9 now name these schedules, and .15 selects ADD_TIMEOUT_MS under ruled D-577 A. These fix the originally named fallback and B-option mismatches; they do not finish the whole-call bound.
- `implementation-plan.md:136`, `:245`, `:247`: FRAME_TIMES caps each midpoint at end_ms-1 before sorting/deduplication. The three corrected examples agree with the formula and the collapse rule. AC-134.5 requires exactly one grab at 2999 ms for count=2, start=2.999 on a 3000 ms video. F3 is fixed at plan level.
- `implementation-plan.md:161`, `:167`, `:300`; `task.md:62`, `:63`, `:66`, `:67`; `baseline.ps1:112`, `:218`, `:315`; `session-gate.ps1:78`: the built-server discovery pin is inventoried and moves 71 -> 72 -> 73. All four task commands and baseline build MCP before running tests that consume dist/index.js. The task's estimate still says six MCP test files at :13; this is an immaterial clerical count, not a finding.
- `implementation-plan.md:211`, `:252`, `:212`, `:257`, `:258`, `:134`: source SHA-256 checks, transport-parity wording and largest-finite-PTS parsing are present. END_GAP skips N/A/blank lines and returns b"" without usable PTS. The GPU encoder smoke description is corrected at :93.
- `implementation-plan.md:18`, `:467`, `:477`, `:514`, `:524`, `:530`, `:540`; `task.md:52`: A/A/A and Mat's quoted USER_EXPLICIT ruling are recorded. Isolated S14 accepts all three. Unchosen B/C text is retained appropriately.

All shortened plan/task/script citations above and below refer to `docs/execution/plans/2026-11-10-video-probe-frames/`.

### Remaining Findings

- **F2 — High, blocking, behavior; AC-134; partial.** FRAME_DEADLINE still cannot bound the whole frames call or ensure that registration finishes before the agent's 120 s timeout. FRAME_CHECKS calls FramePort.probe before grabbing (`implementation-plan.md:132`, `:137`); the reused FFmpegAdapter.probe calls _run at `packages/infrastructure/src/avkit_infra/media/adapter.py:420`, whose subprocess.run at :265 has no timeout. RUN_UTF8 expressly changes only decoding (`implementation-plan.md:129`). Both FRAME_WRITE lock acquisitions are ordinary waits (`implementation-plan.md:140`; actual lock: `packages/core/src/avkit_core/services/capture.py:97`). Checking after acquiring the lock prevents a late publish but cannot make the wait return within the budget. Finally, after check (c), every replace, full PNG image load, upsert and commit runs without another check or enforced duration (`implementation-plan.md:140`, `:141`; image.load at `packages/infrastructure/src/avkit_infra/capture/adapter.py:313`). A concrete permitted schedule is check (c) at 99 s, first replace at 99 s, a 22 s first image probe, then the second replace and commit at 121 s. The agent has timed out and can retry even though the first call commits shots. Twenty seconds of nominal headroom is not a bound on these operations. A slow initial probe or held capture lock can also keep the synchronous request alive past the client timeout. AC-134.8/.9/.15 cover the corrected paths but omit the initial probe, bounded lock acquisition and expiry inside publication. Preserve D-577 A; carry the remaining budget into the frames metadata probe, use timed lock acquisition, and specify deadline-aware publication/finalization with rollback rather than an assumed 20 s maximum. Add deterministic cases for each omitted stage, including expiry during an image probe before a later replace/commit. Keep this as F2, not a new finding.
- **F1 — Medium, non-blocking, behavior; AC-133; partial.** VIDEO_INPUT's specified `raise ValidationError(...) from None` hides context when a traceback is formatted; it does not remove `exc.__context__`. A real self-loop on Python 3.12.12 produced the fixed message, cause=None and suppress_context=True, but context remained RuntimeError containing the marker. Thus a service caller inspecting the exception still receives the raw path, contrary to R1's explicit context-free check. AC-133.1 checks only cause and suppression (`implementation-plan.md:126`, `:205`); its current assertions pass this counterexample. Raise the fixed exception after leaving the filesystem except block and assert context is None, as well as cause/message. Explicitly record zero probes as well as zero grabs for the frames loop cases at :247/:255. The original API 500 and ordinary console traceback leak are addressed; no remaining HTTP/console disclosure was demonstrated, so this residual is downgraded and does not gate approval.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new findings.

### R1 — VIDEO_INPUT

Accepted the expected filesystem exception mapping on pinned Python 3.12.12, including RuntimeError, and the four new symlink cases with console positive controls. Did not accept the stronger claim that from None removes __context__: the independent real-symlink probe proves otherwise. The frames cases require zero grabs but do not explicitly assert zero probes. These are the remaining F1 qualifications; the original logged-500 mechanism is corrected. No new service or API test was executed in this plan recheck.

### R2 — Whole-call deadline and cleanup

Accepted the grab-local single budget, bounded END_GAP run, before/after-grab checks, lock-acquired pre-publication check, selected 100/120 values and planned cleanup on (b)/(c). AC-134.8 now covers those three checkpoints; .9 covers packet timeout, exhausted retry budget and decreasing subprocess timeouts; .15 covers the selected MCP timeout. Did not accept a bound on initial metadata probing, either lock wait, name/inbox enumeration, temp writes, phase-3 PNG decode/DB work or cleanup. There is no check during the phase-3 loop. F2 remains blocking for the concrete late-commit schedule above. Cleanup after an observed (b)/(c) failure is coherent; its wall time is not itself bounded.

### R3 — FRAME_TIMES

Accepted. For integer start<end, span>=1 and count>=1, the nonnegative rounded offset is at least zero and end-1 is at least start; their minimum is therefore at least start and at most end-1. This proves the bound for all permitted spans/counts, beyond the enumerated samples. Independent execution passed all three examples and 6,400 combinations of four starts, spans 1..80 and counts 1..20. AC-134.3's smaller exhaustive loop and AC-134.5's service case are suitable planned coverage. The service case is not an executed implementation result.

### R4 — Round-1 notes

Accepted the pin inventory, allowed set and build ordering; source hashes in AC-133.7/AC-134.10; transport parity in AC-133.8/AC-134.15/AC-134.16; and END_GAP's largest-finite-PTS/N/A/blank/empty semantics. Read the actual command rows rather than inferring the builds from their prose. Baseline records the build exit and proceeds rather than failing immediately on a build failure; its output is not proof of a successful build. The later task rows and final gate enforce their builds. No product failure or new blocker was established on this note.

### R5 — Regressions and rulings

Accepted A/A/A without reopening Mat's choices. The pre-ruling diff changes only the status/ruling records and task ruling note. Stop Conditions are byte-equivalent as decoded text to the pre-correction version, and the exact --require sequence is unchanged. The new loop/hash/deadline assertions can still be assertion-first against row 1's existing stubs; API Reds still assert status before inspecting bodies. The built-server count Red has a freshly built server with the new action still absent, so its moved expectation fails by assertion. No correction-induced missing import/collection dependency was identified. Plan-folder files are LF. Identity still binds the whole non-artifact diff and untracked inputs, so the additional runner test is covered; its permitted scratch selftest passed. S14, executed alone as read-only Python, reports all three A rulings true and exits 0. Supplied task-lint (26 rows) and decision-source receipts were read, not rerun. F2 is the substantive remaining contradiction in the ruled plan.

### Checklist Results

| Check | Result | Command / procedure | Exit | Decisive observation |
|---|---|---|---|---|
| R1 path/exception boundary | partial | rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s62/review/r2_probes.py | 0 | Python 3.12.12 real symlink: fixed message and hidden formatted context, but context_has_marker=True |
| R2 deadline totality | fail | Same r2_probes.py plus manual FRAME_CHECKS/FRAME_WRITE call trace; codex-independent-reviewer | 0 for probe; null for manual | Existing _run timeout absent; ordinary lock wait exceeds scaled client window; literal phase-3 schedule replaces/commits at 121 s |
| R3 midpoint bounds | pass | Same r2_probes.py | 0 | Three exact examples and 6400 range cases pass; general integer-bound proof above |
| R4 notes/build ordering | pass | Same r2_probes.py and manual parser/hash/parity comparison; codex-independent-reviewer | 0 for probe; null for manual | Four task rows and baseline build before test; pin in all inventories; parser semantics explicit |
| R5 rulings/regression comparison | pass | Same r2_probes.py; rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s62/review/r2_diff_check.py | 0 each | Exact --require sequence retained; all files LF; isolated S14 all ruled=True; stop conditions unchanged |
| Red-check selftest | pass | rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/red-check.py --selftest | 0 | 43 fixtures, 13 positive/30 negative, 0 wrong |
| Identity selftest | pass | rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/identity.py --selftest | 0 | 0 failures; scratch-only mutation probes |
| Product/full/runtime validation | n/a | Deliberately not run in this read-only planning review | null | No pytest, Vitest, baseline, session gate, backend, MCP server or network request |

Commands ran with PYTHONDONTWRITEBYTECODE=1; Python output encoding was UTF-8; selftests used TMP/TEMP under `C:/Temp/av-kit/s62/review`. The probe's exit 0 means its diagnostic assertions completed, not that F1/F2 passed. Its phase-3 schedule is a model of the specified plan, not an executed new service. The lock probe uses a real lock and a scaled 120 ms client window; it demonstrates the ordinary wait's lack of a timeout. No reviewer FFmpeg run was needed this round.

```json
{"schema_version":"evidence.v1","check_id":"s62-r2-corrected-contracts","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s62/review/r2_probes.py","cwd":"P:/av-kit","scope":"corrected path/deadline/formula contracts, task build ordering, LF, require sets, isolated S14","phase":"targeted","exit_code":0,"result":"fail","tested_state":"main 7b9f34d4e93b9fc733277278859f2b9ec26abdb8; implementation-plan.md sha256 8239e7e8a4a9a2431335014a255231980021dcc530d1277a06bfda0ea06754a0; task.md sha256 db358150e94786c24349231b26fed986c8d5578833d12bf88d09906e7b7804a1","output":"Python 3.12.12. F1 real_symlink=True; cause=None; suppress_context=True; context_type=RuntimeError; context_has_marker=True; formatted_trace_has_marker=False. F2 existing _run timeout_present=False; phase3 modeled replaces=[99.0,121.0], commit=121.0; real ordinary lock completed_in_client_window=False. R3 examples=[0,1,2],[0],[2999]; 6400 range cases passed. R4 all four MCP rows build before tests. R5 requires unchanged, all plan files LF; D-573/D-576/D-577 ruled=True, isolated S14 exit=0."}
{"schema_version":"evidence.v1","check_id":"s62-r2-redcheck-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/red-check.py --selftest","cwd":"P:/av-kit","scope":"permitted scratch parser selftest","phase":"static","exit_code":0,"result":"pass","tested_state":"red-check.py sha256 4ba9e462a9cacc9d2095fccd7f9e0f640588d271aa767a0c92164a260af8e6dd","output":"red-check selftest: 43 fixture(s) (13 positive, 30 negative), 0 wrong: []"}
{"schema_version":"evidence.v1","check_id":"s62-r2-identity-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/identity.py --selftest","cwd":"P:/av-kit","scope":"permitted scratch identity selftest","phase":"static","exit_code":0,"result":"pass","tested_state":"identity.py sha256 72d1f596ab4bf4fcd6eca44687c2a866313e2db73a29b116c18a799bc72d7196; baseline.ps1 sha256 b7cbc05d46fafea49692ad688f86514e569bca2d8f26e3da9ba4bf00f3d019dc; session-gate.ps1 sha256 8ae1449281e838c85c055982109a282f567230f258345fd8c5e59debf27c1e16","output":"identity selftest: 0 failure(s)"}
```

### Verdict

**changes_required** — one open blocking finding, F2 (High, AC-134). F1 is partial with a non-blocking Medium residual; F3 is fixed. No new findings. Intent achieved: partial. The ordinary probe/frames journeys, source preservation, endpoint correction and ruled A/A/A choices are accepted; the promised whole-call deadline and prevention of post-timeout registration remain unfulfilled.

This is an unstarted-plan verdict. All review writes are under `C:/Temp/av-kit`; no repository file was edited. Round 1's report body and original Findings table remain unchanged above. This recheck supersedes its pending-ruling/current-status statements only for the present round.


## Recheck (2026-11-10, round 3)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | partial | fixed |
| F2 | partial | partial |
| F3 | fixed | fixed |

### Confirmed Fixes

All shortened plan/task citations in this section refer to `docs/execution/plans/2026-11-10-video-probe-frames/`. These are plan-level conclusions; the new services and tests have not been implemented or executed.

- `implementation-plan.md:128`, `:130`, `:207`, `:209`: VIDEO_INPUT and PROBE_MAP now raise their fixed errors after leaving the exception handler. AC-133.1 and AC-133.3 explicitly require both `__cause__` and `__context__` to be `None`. An independent Python 3.12.12 probe of this specified pattern, including a real Temp self-loop symlink, confirms both links are absent and the formatted exception contains no marker. F1 is fixed.
- `implementation-plan.md:249`, `:257`: AC-134.5 requires zero metadata probes for the refusals preceding FramePort.probe, including the symlink loop; AC-134.13 requires no probe and no grab for its missing-file and loop cases. These address F1's remaining probe-count qualification.
- `implementation-plan.md:134`, `:143`, `:253`; `task.md:59`, `:67`: FRAME_PORT carries the remaining time through `probe(file_path, *, timeout_s=None)` to `_run(timeout=...)`, then conditionally to `subprocess.run`. TimeoutExpired has a fixed MediaProbeError mapping. The existing probe_file path leaves the timeout unset. AC-134.9 checks explicit timeout forwarding, the failure mapping and omission of the keyword for existing calls.
- `implementation-plan.md:135`, `:136`, `:142`, `:143`, `:252`, `:253`: FRAME_GRAB/END_GAP retain their shared decreasing process budget; both FRAME_WRITE lock acquisitions now use `acquire(timeout=left)` and release only locks acquired by this call. A failed acquisition becomes expiry. Checks (a) and (b), acquired-lock publish check (c), and the new pre-commit check (d) are explicitly ordered. AC-134.8 names both held-lock schedules and expiry during publication.
- `implementation-plan.md:142`, `:250`, `:252`: the image probe runs on the closed temp in phase 2 and its ImageProbe is reused in phase 3. Check (d) follows all replaces/upserts. The cleanup contract closes owned handles, removes owned temps, removes moved destinations before releasing the publication lock, and raises inside the transactional boundary so the UoW rolls back. The existing UoW supports that rollback at `packages/infrastructure/src/avkit_infra/database/unit_of_work.py:54`. Thus the earlier 99 s image-decode / 121 s successful late-commit schedule is corrected: it must now fail before publication. This fixes late commitment in that schedule, but not its late response; see F2 below.
- `implementation-plan.md:138`, `:247`, `:249`: FRAME_TIMES and the AC-134.3/.5 endpoint cases are unchanged by this correction. F3 remains fixed.
- `implementation-plan.md:291`, `:364`; `task.md:59`, `:67`: the adapter extension is inventoried; row 1 introduces and ignores the two optional keywords; row 5 includes the four requested existing-caller test modules. No correction-induced import/collection failure was identified. Existing pin movement, MCP build ordering, hashes, parity and marker contracts accepted in round 2 remain intact.

### Remaining Findings

- **F2 — High, blocking, High confidence, deliverable, behavior; violates AC-134 (AC-134.8 / FRAME_DEADLINE, ruled D-577 A); partial.** `implementation-plan.md:142` still calls `self._annotate.probe(tmp)` synchronously with no timeout. Its real implementation performs a full `image.load()` at `packages/infrastructure/src/avkit_infra/capture/adapter.py:307-317`. Moving it before (c) prevents a subsequent late publish, but does not interrupt a slow decode. A valid specified schedule is (b) at 99 s, image probing taking 22 s, then refusal/cleanup at 121 s. The agent's 120 s client deadline has already elapsed; the promised response within 105 s is false even though no shot commits. The deterministic review model executes exactly this ordering and confirms no publication but a late return.

  There is also a concrete database wait outside `left`, rather than merely a hypothetical slow disk: `_import_dest` calls `uow.capture_shots.list()` (`packages/core/src/avkit_core/services/capture.py:616-619`), and `_upsert_shot` calls `get_by_path()` (`:1255`). These issue synchronous Session queries at `packages/infrastructure/src/avkit_infra/database/repositories.py:443-446` and `:461-464`. The actual engine configuration at `packages/infrastructure/src/avkit_infra/database/engine.py:78-83` creates a QueuePool with a **30 s connection-acquisition timeout**, separate from SQLite's 5,000 ms busy_timeout. With the real project engine functions extracted unchanged and pointed at a new Temp database, holding its 15 available connections kept another query blocked past a scaled 120 ms client window; it returned only when a connection was released. At phase 3 time 99 s, pool exhaustion can therefore hold the first query until 129 s before (d) can reject it. The capture-file lock does not bound other users of the database pool. This is the same unfinished whole-call deadline finding F2, not a new id.

  `implementation-plan.md:143` consequently cannot derive its 105 s return bound from the FFmpeg/capture-lock timeouts plus the final commit's busy_timeout. AC-134.6/.8/.9 (`:250`, `:252`, `:253`) now cover image-probe exceptions, the two lock timeouts, four checkpoint schedules and bounded subprocesses, but do not exercise deadline exhaustion inside image probing or database connection acquisition. **Recommendation:** retain the accepted A/A/A choices and corrected rollback/ownership rules; give synchronous image validation and database acquisition/work an enforceable remaining-time bound, without allowing detached work to publish after return. Add deterministic slow-image-probe and exhausted-pool cases asserting timely return, no later publication and no owned PNG/temp/row. A check after either operation alone cannot establish that bound. Final round 3 is exhausted; preserve this finding for Mat rather than starting another machine-review round.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new findings.

### R1 — Deadline, cleanup and deterministic coverage

Accepted: the initial FramePort.probe timeout chain; both timed capture-lock acquisitions; each grab and END_GAP's shared bounded subprocess budget; the move of image decoding to phase 2; and checks (a) through (d). For an observed (c)/(d) expiry or lock-acquisition failure, FRAME_WRITE explicitly cleans only this call's owned paths and rolls back its rows; a phase-1 lock failure creates no temp, and a phase-3 lock failure removes its temps without needing that lock. AC-134.6/.8/.9 specify deterministic probes for those failures, including cleanup after the second replace and continued ownership of another writer's temp.

Did not accept the whole-call return-time claim. Image decoding still has no bound, and database connection acquisition has an independent 30 s pool wait. A later check can prevent commitment but cannot make the response precede the client timeout. The final commit's 5,000 ms SQLite contention timeout is accepted as its stated lock-contention limit; it is not a limit on earlier pool acquisition or all prior synchronous work. No new product service or commit was run. F2 remains partial/blocking.

### R2 — Error links and early refusals

Accepted in full at plan level. VIDEO_INPUT/PROBE_MAP use the requested outside-except pattern; AC-133.1/.3 require both links absent; AC-134.5/.13 record zero probes at the appropriate early boundaries. The independent real-symlink/error-pattern probe passes. No residual F1 finding remains, and no claim is made that the planned service/API tests have run.

### R3 — `_run`, compatibility and Reds

Accepted. AST inspection finds six existing `_run` sites: ffmpeg_version at adapter.py:383, convert at :398, probe at :420, and detect_gpu at :491, :493 and :518. The optional timeout keyword defaults to None and is omitted from subprocess.run unless set. Executing an AST model of precisely the specified `_run` changes with a recording subprocess fake preserves `check=False`, `capture_output=True` and `text=True`; adds only RUN_UTF8's UTF-8/replace keywords for old calls; and forwards `timeout=2.5` only for an explicit timeout. This is a plan model, not execution of a changed adapter.

Row 5's added modules cover the existing convert/probe/GPU call families; resolver and conversion fakes already accept subprocess keywords. `test_domain_conversion.py` also protects the existing media protocol inventory. The four added modules alone do not directly call ffmpeg_version; row 5 already runs the new `test_media_adapter_frames.py`, whose AC-133.6/AC-134.9 explicitly check the `-version` subprocess call and supply the direct keyword oracles. The complete row-5 list therefore covers the six sites. Row 1's ignored optional keywords make later timeout assertions fail on behavior, rather than a missing-keyword import/collection problem. The new FramePort and extended FFmpegAdapter.probe both use `file_path`, `Path`, the optional keyword-only `timeout_s: float | None = None`, and MediaInfo; the implementation also remains compatible with MediaPort's smaller signature. Structural compatibility is accepted; pyright itself was deliberately not run. RUN_UTF8 remains scoped to `_run`; `_run_with_progress` is untouched.

### R4 — Correction regressions, scope and rulings

Accepted. Compared both working-tree documents with the supplied pre-corr-r2 copies. The exact `--require` sequence and the complete Stop Conditions block are unchanged. F3's ACs and the accepted pin/hash/parity/console guards are retained. The adapter's Files Modified row now explicitly names FRAME_PORT's extended probe/_run functions; its other named implementation files remain inventoried. No mechanism acquired an out-of-inventory implementation target. All six top-level plan files are LF. The four scripts have the same hashes reported in round 2; both permitted selftests pass again. Their scratch mutations are not repository changes.

Executed only S14's extracted read-only Python string: D-573, D-576 and D-577 each report `ruled=True` with `A:` and `USER_EXPLICIT 2026-11-10`. Accepted Mat's supplied ruling, no split and execution budget; B/C text remains the unchosen alternative. Read, but did not rerun, the coordinator's 26-row task-lint receipt. No regression-induced finding was established. The unchanged explanatory phrase in END_GAP about `_run` lacking timeout is stale after FRAME_PORT's explicit extension; its own bounded subprocess contract is unambiguous and no behavior depends on that phrase.

### Checklist Results

| Check | Result | Command / procedure | Exit | Decisive observation |
|---|---|---|---|---|
| R1 whole-call return bound | fail | `rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s62/review/r3_probes.py`; manual call trace by codex-independent-reviewer | 0 for diagnostics; null for manual | Image-stage schedule returns at 121 s without publishing; real engine has QueuePool timeout 30 s independently of busy_timeout 5000 ms; exhausted pool blocks beyond scaled client window |
| R1 checkpoint cleanup and specified coverage | pass | Manual FRAME_WRITE/FRAME_DEADLINE, AC-134.6/.8/.9 and real UoW trace; codex-independent-reviewer | null | All four checkpoints, both timed capture locks, owned-path removal and exception rollback are specified; remaining slow-stage tests are identified in F2 |
| R2 context and early-probe refusals | pass | Same r3_probes.py | 0 | Real symlink pattern: cause=None, context=None, formatted_marker=False; both AC assertions and zero-probe clauses present |
| R3 adapter compatibility and row ordering | pass | Same r3_probes.py plus manual existing-caller/test inspection; codex-independent-reviewer | 0 for model; null for manual | Six sites; optional keyword absent on old calls; explicit 2.5 forwarded; matching file_path; ignored row-1 keywords; four caller modules in row 5 |
| R4 regressions and ruled entries | pass | Same r3_probes.py | 0 | Exact requires and Stop Conditions unchanged; six files LF; script hashes unchanged; isolated S14 all A/ruled=True |
| Red-check selftest | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/red-check.py --selftest` | 0 | 43 fixtures: 13 positive, 30 negative, 0 wrong |
| Identity selftest | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/identity.py --selftest` | 0 | 0 failures; permitted scratch-only mutations |
| Product/full/runtime validation | n/a | Not run under the explicit read-only planning-review scope | null | No pytest, Vitest, session gate, baseline, application, MCP server, FFmpeg or network request |

All Python commands used `PYTHONDONTWRITEBYTECODE=1`; selftests used TMP/TEMP under `C:/Temp/av-kit/s62/review`. The diagnostic command's exit 0 means its assertions about the observed counterexample completed; it does not mean the deadline contract passed. The pool experiment executes the unchanged project engine functions against a new Temp database with real SQLAlchemy connections; it is not a running backend or implemented frames request. The 99/121 and 99/129 schedules are contract counterexamples, not measured full-duration service calls.

```json
{"schema_version":"evidence.v1","check_id":"s62-r3-contract-recheck","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s62/review/r3_probes.py","cwd":"P:/av-kit","scope":"corrected plan contracts, real Temp symlink and SQLAlchemy pool, proposed _run AST model, document regressions and isolated S14","phase":"targeted","exit_code":0,"result":"fail","tested_state":"main 7b9f34d4e93b9fc733277278859f2b9ec26abdb8; implementation-plan.md sha256 7246e9d2eb56210f529ca5e9dd5c9d3875d3c48571378b89bc4b42e27d4a43d7; task.md sha256 d7eb631f8099847a1259314ec3eedbcf8f050fed4aa2a21774bc739ad3a88bab","output":"F1 VIDEO_INPUT/PROBE_MAP cause=None context=None formatted_marker=False; real_symlink=True. F2 image schedule after_grab=99 probe_returns=121 publish=False commit=False cleanup_empty=True return_after_client=True. Actual project engine: QueuePool pool_timeout=30.0 pool_size=5 max_overflow=10; busy_timeout_ms=5000; exhausted-pool query_finished_in_120ms_window=False, query_elapsed_s=0.125, query_result=1 after release. Six _run sites; old-call kwargs preserved apart from ruled UTF-8/replace, explicit timeout=2.5 forwarded. Requires and Stop Conditions unchanged, six files LF, isolated S14 all three A ruled=True."}
{"schema_version":"evidence.v1","check_id":"s62-r3-redcheck-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/red-check.py --selftest","cwd":"P:/av-kit","scope":"permitted scratch parser selftest","phase":"static","exit_code":0,"result":"pass","tested_state":"red-check.py sha256 4ba9e462a9cacc9d2095fccd7f9e0f640588d271aa767a0c92164a260af8e6dd","output":"red-check selftest: 43 fixture(s) (13 positive, 30 negative), 0 wrong: []"}
{"schema_version":"evidence.v1","check_id":"s62-r3-identity-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-10-video-probe-frames/identity.py --selftest","cwd":"P:/av-kit","scope":"permitted scratch identity selftest","phase":"static","exit_code":0,"result":"pass","tested_state":"identity.py sha256 72d1f596ab4bf4fcd6eca44687c2a866313e2db73a29b116c18a799bc72d7196; baseline.ps1 sha256 b7cbc05d46fafea49692ad688f86514e569bca2d8f26e3da9ba4bf00f3d019dc; session-gate.ps1 sha256 8ae1449281e838c85c055982109a282f567230f258345fd8c5e59debf27c1e16","output":"identity selftest: 0 failure(s)"}
```

### Verdict

**changes_required** — one open High blocking finding, F2 (AC-134), remains partial. F1 is fixed; F3 remains fixed; no new findings. Intent achieved: partial. The normal read-only probe/frames workflow, source preservation, no-upload constraint, corrected publication rollback and Mat's A/A/A decisions are accepted. The promised response before the agent's timeout still lacks bounds on synchronous image/database stages.

This is the last allowed round, 3 of 3. Preserve the rolling report and evidence and return the unresolved F2 to Mat under the review-cap outcome; do not reset the loop or initiate a fourth review. This is an unstarted-plan review, not execution approval. The report is written only to `C:/Temp/av-kit/s62-plan-review-round-3.md`; the coordinator owns its canonical copy. No repository file was edited, and the prior report body, original Findings table and round-2 recheck remain byte-for-byte unchanged above.


## Recheck (2026-11-10, round 4)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | fixed | fixed |
| F2 | partial | fixed |
| F3 | fixed | fixed |

### Confirmed Fixes

All shortened plan/task citations below refer to `docs/execution/plans/2026-11-10-video-probe-frames/`. These are conclusions about an unstarted plan, not implemented service behavior. Claude Code/Anthropic authored the plan and corrections; Codex independently reviewed them.

- **F2 fixed:** `implementation-plan.md:145`, `:254`, `:681`; `task.md:59`, `:67`. FRAME_DEADLINE (e)/D-587 puts the complete FRAME_CHECKS-to-FRAME_WRITE body behind a return gate. The shared state lock makes the abandon versus check-(d) transition atomic. A running worker is abandoned at 105 s; a worker already committing receives only the remaining interval to 111 s. AC-134.8 (e) requires blocked decode, blocked checkout, completing commit, overrunning commit and worker-error cases, with every named worker joined afterward. This closes the late-reply counterexamples from round 3 while retaining D-577 A's 100 s work deadline, 20-frame cap and 120 s client timeout.
- **F1 remains fixed:** `implementation-plan.md:128`, `:130`, `:209`, `:251`, `:259`. VIDEO_INPUT/PROBE_MAP retain RuntimeError mapping and outside-except fixed errors; AC-133.1/.3 retain absent exception links, and AC-134.5/.13 retain the early refusal/no-probe/no-grab assertions. These accepted contracts were not changed by this correction.
- **F3 remains fixed:** `implementation-plan.md:140`, `:249`, `:251`. FRAME_TIMES still caps quantized midpoints at `end - 1`, deduplicates and sorts; the exhaustive interval and actual-duration cases remain unchanged.
- **Correction compatibility:** `implementation-plan.md:292`, `:360`, `:366`; `task.md:59`, `:67`, `:80`, `:85`; `red-check.py:78`. Both new constants are declared in row 1 and DECLARED_NEW; the service remains in the existing Files Modified/gate scope; decision references include D-587. Required Red sequences, the Stop Conditions block and the three unchanged plan scripts retain their prior bytes. The six top-level plan files are LF.

### Remaining Findings

None.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### R1 — Return bound, races, cleanup and coverage

Accepted FRAME_DEADLINE (e) and AC-134.8 (e). The state lock serializes the two decisions: either the caller changes `running` to `abandoned`, preventing the worker from crossing (d), or the worker changes `running` to `committing`, preventing the caller from declaring abandonment after commitment has been admitted. `abandoned` has no transition back to `running` or `committing`. The lock protects these decisions, not the slow operation itself: holding it across a commit, cleanup or join would fail the explicitly required blocked-commit oracle.

The answer is the worker's result or error if it finishes; the last normalized time's `frame grab failed at` if abandoned; and the masked CaptureFailedError/503 if a committing worker remains unfinished at the final cutoff. The 6 s interval must end at elapsed 111 s, not restart after each poll. With that absolute cutoff and 0.05 s polling, the specified algorithmic bound is 111.05 s, below 120 s. AC-134.8 (e)'s commit fake that jumps beyond `FRAMES_RETURN_S + COMMIT_WAIT_S` and stays blocked distinguishes that behavior from a fresh six-second wait against a frozen injected clock.

The independent thread/SQLite model exercised eight schedules: normal result; blocked decode; blocked phase-3 checkout; abandon before (d); commit finishing; commit overrunning; worker error; and commit error. Every worker was released and joined. All abandoned schedules ended with zero rows, no owned destination or temp, and the capture lock released. Completing and overrunning commits each retained their one successful shot; the latter first returned the specified masked error. Both forwarded-error cases preserved object identity and `__context__ is None`. This models the specified mechanism; it does not execute a new CaptureService.

Abandonment is cooperative. A blocked decode retains this call's temp until it resumes; a phase-3 checkout can retain CAPTURE_FILE_LOCK until that wait returns (the existing pool timeout is 30 s). That temporarily delays other capture writers; the gate does not claim to cancel their underlying wait. After resumption, checkpoints and FRAME_WRITE cleanup prevent publication/commit and remove owned paths before releasing a held capture lock. The scanner takes the same capture lock and excludes `.avkit-tmp` by extension (`packages/core/src/avkit_core/services/capture.py:401`, `:406`), so it cannot turn those reservations or locked, uncommitted destinations into durable shots. No FFmpeg process is started after abandonment: the call's work deadline has already passed and check (a) refuses another grab; a process already running retains its own remaining-budget timeout. No concrete permanent abandoned-worker write or resource leak was established.

I do not accept instantaneous cancellation or immediate cleanup at the caller's return; neither is what (e)'s joined-worker tests assert. A commit still in progress at the final cutoff may finish later and retain shots, exactly as (e) discloses. This is the requested committing/503 outcome, not an abandoned worker committing. The model is not a measured 111 s production request or an operating-system scheduling guarantee.

### R2 — D-587, architecture and error/refusal contracts

Accepted. A core-service daemon thread has the cited local precedent (`packages/core/src/avkit_core/services/conversion.py:218`). Database engine/session factories can be reused by the worker: SQLite is configured with `check_same_thread=False` (`packages/infrastructure/src/avkit_infra/database/engine.py:21`), and each unit of work creates its session in `__enter__` and closes it on exit (`packages/infrastructure/src/avkit_infra/database/unit_of_work.py:40`, `:54`). The plan moves the whole body, rather than sharing an active session concurrently between caller and worker. Both threads read the same injected monotonic clock; Event-controlled fakes provide the deterministic schedules without a 105 s test sleep.

FRAME_WRITE still owns normalization and rollback; the worker boundary must catch/store the resulting error and the caller raises it outside an exception handler. That is compatible with VIDEO_INPUT/PROBE_MAP's outside-except pattern and NO_RAW_OUTPUT. It does not permit an unhandled daemon-thread traceback containing an input path. AC-134.6's marker-bearing image-probe refusal and AC-134.13's API console/body/stdout/stderr oracles remain applicable, including their early no-probe/no-grab clauses (`implementation-plan.md:149`, `:252`, `:259`). The explicit same-error-object/context oracle closes the new transport boundary.

No contradictory earlier mechanism or AC was found. Checks (a)-(d) govern admission to publication/commit; (e) independently bounds the caller's wait and expressly documents the exceptional in-progress-commit result. FRAME_WRITE cleanup still applies to worker failures and abandonment, with final resource assertions after join. Stop Conditions S5/S10/S12 remain unchanged: this decision authorizes no network activity, raw-output leak or silent existing-route change. I do not treat the coordinator's 0.162 s decode measurement as a universal decode bound, or busy_timeout as a universal operation bound; the new return gate is what removes that dependency.

### R3 — Regressions and ruled choices

Accepted. Reviewed the exact three-file diff against `C:/Temp/av-kit/s62/pre-corr-r3/`, then the changed contracts and referenced code. Row 1 declares FRAMES_RETURN_S and COMMIT_WAIT_S before behavioral Reds, and red-check.py declares both names without relaxing required failures. Both permitted selftests pass: Red checker 43 fixtures, 13 positive/30 negative, zero wrong; identity zero failures. D-570 through D-587 are consecutive, 18 plan decisions; with the six given grouping decisions the coordinator's updated probe reports 24. Its receipt was read, not rerun.

The return gate lives in the already inventoried `services/capture.py`; no new production path is missing from gate scope. baseline.ps1, session-gate.ps1 and identity.py retain the round-3 hashes. All six plan files have no CR bytes. Task rows remain unstarted; the script counted 26, matching the read coordinator lint receipt. Executed only baseline.ps1's extracted S14 Python string: the current plan passes all three A/USER_EXPLICIT rulings; a Temp-only copy lacking one USER_EXPLICIT ruling is correctly refused with exit 1. baseline.ps1 itself was not run. No accepted prior Red, ownership, endpoint, midpoint, UTF-8, pin or source-preservation contract was removed.

Mat's continuation receipt allows round 4 of 6 and adds 30M tokens; it supersedes the historical cap statement at the end of round 3. D-573 A, D-576 A and D-577 A stand. There is no new human ruling in this review.

### Checklist Results

| Check | Result | Command / procedure | Exit | Decisive observation |
|---|---|---|---|---|
| R1 return gate and state schedules | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B C:/Temp/av-kit/s62/review/r4_probes.py`; manual contract trace by codex-independent-reviewer | 0 for model; null for manual | Eight isolated schedules; abandoned workers leave zero rows/owned files after join; completing/overrunning commit outcomes distinguished; forwarded errors preserve identity/context |
| R2 codebase fit and unchanged refusal contracts | pass | Manual comparison of FRAME_WRITE/FRAME_DEADLINE/NO_RAW_OUTPUT, AC-134.6/.13, engine/session/thread precedent and stop conditions; codex-independent-reviewer | null | Whole body owns worker-local UoWs; no raw traceback allowance; earlier refusal/cleanup oracles retained |
| R3 regression and S14 checks | pass | Same r4_probes.py, exact saved-copy diffs and manual changed-row inspection | 0 for probes; null for manual | Required Red sequences and stop conditions unchanged; 26 rows; six LF files; D-570..D-587; S14 positive exit 0 and missing-ruling negative exit 1 |
| Red-check selftest | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-11-10-video-probe-frames/red-check.py --selftest` | 0 | 43 fixtures (13 positive, 30 negative), 0 wrong |
| Identity selftest | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-11-10-video-probe-frames/identity.py --selftest` | 0 | 0 failures; scratch-only mutations |
| Product/full/runtime/network validation | n/a | Excluded by this read-only planning-review request | null | No pytest, Vitest, baseline/session gate, backend, MCP server, FFmpeg or network request run |

Python commands used `PYTHONDONTWRITEBYTECODE=1`; selftests set TMP/TEMP under `C:/Temp/av-kit/s62/review`. All new files are under that Temp review directory or the requested report path. The coordinator's pool/decode receipt ends with exit 1 when FFmpeg refuses its largest generated image: its smaller-image timings and recorded pool settings are observations, not a successful universal bound. No finding depends on treating that failed probe as a passing gate.

```json
{"schema_version":"evidence.v1","check_id":"s62-r4-return-gate-and-regressions","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B C:/Temp/av-kit/s62/review/r4_probes.py","cwd":"P:/av-kit","scope":"isolated proposed return-gate model with threads and Temp SQLite, static correction regressions and extracted S14 only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main 7b9f34d4e93b9fc733277278859f2b9ec26abdb8; implementation-plan.md sha256 239445dd28dea8c388e60bea43c832003cdb03ecd301312ac0b7101bf7ce79a5; task.md sha256 c7fc79b8399106a6cb607686eaba33258c2ab0b94bcfec0bc935cca691da7e92","output":"MODEL ONLY: eight schedules pass, all workers joined. decode/checkout/abandon-before-d return ValidationError with zero rows and no owned files after join. commit-finishes returns shots; commit-overruns returns CaptureFailedError and can retain one shot after release. worker-error/commit-error preserve error identity and context=None. Constants declared, required Reds and stop conditions unchanged, 26 task rows, six LF files, D-570..D-587 consecutive. Extracted S14 current A/A/A exits 0; Temp missing-ruling fixture exits 1 as expected."}
{"schema_version":"evidence.v1","check_id":"s62-r4-redcheck-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-11-10-video-probe-frames/red-check.py --selftest","cwd":"P:/av-kit","scope":"permitted plan-local parser selftest","phase":"static","exit_code":0,"result":"pass","tested_state":"red-check.py sha256 20456b8de35913da54b38e010a0d5b0835d1f67fd285fac22223920a394aee26","output":"red-check selftest: 43 fixture(s) (13 positive, 30 negative), 0 wrong: []"}
{"schema_version":"evidence.v1","check_id":"s62-r4-identity-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B docs/execution/plans/2026-11-10-video-probe-frames/identity.py --selftest","cwd":"P:/av-kit","scope":"permitted plan-local identity selftest","phase":"static","exit_code":0,"result":"pass","tested_state":"identity.py sha256 72d1f596ab4bf4fcd6eca44687c2a866313e2db73a29b116c18a799bc72d7196; baseline.ps1 sha256 b7cbc05d46fafea49692ad688f86514e569bca2d8f26e3da9ba4bf00f3d019dc; session-gate.ps1 sha256 8ae1449281e838c85c055982109a282f567230f258345fd8c5e59debf27c1e16","output":"identity selftest: 0 failure(s)"}
```

### Verdict

**approved** — zero open blocking findings. F2 is fixed at plan level; F1 and F3 remain fixed; no new findings. Intent achieved: yes. Executing the corrected plan delivers the registered local probe-to-frames workflow with the ruled values, source preservation and no upload. The return gate addresses round 3's slow-body failures without pretending that abandoning a worker cancels its operation.

This is independent approval of the unstarted plan, not a claim of implemented behavior or authorization to begin execution. Mat's execution gate remains. Report: `C:/Temp/av-kit/s62-plan-review-round-4.md`; the coordinator owns the canonical copy. No repository file was edited. The round-3 report body, original Findings table and both earlier Recheck sections are unchanged above; only frontmatter and this appended section differ.
