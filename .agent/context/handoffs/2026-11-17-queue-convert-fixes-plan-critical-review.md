---
date: "2026-11-17"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-17-queue-convert-fixes/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "qcf-plan-2026-11-17-queue-convert-fixes"
round: 2
---

# Critical Review: queue-convert-fixes

> **Review Mode:** plan
> **Verdict:** approved (round 2)

## Scope

**Intent anchor:** on the Convert and Downloader pages Cancel is disabled while the queue is Paused, and the toolbar's card Cancel, the palette's "Cancel conversions" and "Cancel downloads" and the cancel confirm all follow that one rule; Cancel stays enabled while a job runs, `Pausing…` included; one Ctrl+O on Convert opens exactly one file picker whether it is pressed before or after the lazy Convert page mounts; no service, API route, OpenAPI document or MCP tool changes; Electron E2E tests on the real backend prove both, with no network and no manual check.

Reviewed the entire working-tree implementation plan and task at HEAD `9d6d172`, their Round 1 response, all 27 ACs and 27 unstarted task rows. Rechecked the grouping's Session 89, D-1100/D-1101, cited build-plan sections, HDP, expert-pass receipt, real Cancel/browse/navigation/shortcut paths, relevant test pins and fixtures, and the inherited checker and Electron-helper sources. The target folder still contains only the two Markdown files: its scripts and tests are scheduled creations.

Claude Code/Anthropic authored the plan; Codex/OpenAI is its independent reviewer. Applied PR-1–PR-9 and the Materiality Gate within Mat's substantive scope. The original Findings table is retained verbatim as round-1 history; the round-2 summary below closes R1-F1. There are zero current findings and no Critical finding.

Only `C:/Temp/av-kit` was written. No product suite, package operation, Electron launch or network request ran. Forbidden secret paths were not opened. Git's warning about `<HOME>/.config/git/ignore` accounts for the supplied host-ignored settings entry, which was excluded without opening it. The coordinator owns canonical publication and ledger recording. Scratch scheduling probes model the proposed algorithm; effect replay in that model is not a React runtime test.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F1 | High | yes | behavior | **Two pre-mount presses can open two pickers when their callbacks straddle mount.** Confidence: High. `BROWSE_HOLD` records a request only inside `navigateAndDeliver`'s deferred callback; `BROWSE_TAKE_ON_MOUNT` consumes and clears that flag. Press Ctrl+O; let its first animation frame run; press Ctrl+O again before mount. On the next frame the first callback sets the hold and the second schedules its final callback. Mount now consumes the hold and opens picker 1. The following frame delivers the second callback to `BROWSE_ACK`, opening picker 2. A guard checking only whether a hold exists at invocation also misses this history, because neither press initially sees a hold. This violates AC-157.9 and D-1108's promised coalescing of pre-mount presses. AC-157.5 keeps the listener absent for both callbacks, and AC-157.9 presses early in a fixed chunk delay; both can pass without exercising the mount-between-callbacks history. | docs/execution/plans/2026-11-17-queue-convert-fixes/implementation-plan.md:122–125,209–213; docs/execution/plans/2026-11-17-queue-convert-fixes/task.md:49–52; ui/src/renderer/src/features/converter/convert-commands.ts:108–115 | Specify coalescing across the entire outstanding pre-mount delivery, including callbacks still waiting for their two frames, so a callback belonging to a consumed request cannot open another picker. Add a deterministic frame-controlled Red case with mount between the two callbacks and require one picker; include it in Green and the gate. Preserve mounted single-press delivery and departure cleanup. Ledger contract: AC-157 (exact AC: AC-157.9). | open |

## Q1 — Goal and proof coverage

Accepted: AC-156.1–.10 cover both rule tables, guarded commands, card/palette publication, confirm admission and cancel-only dismissal; .11/.12 require Electron proof, and .13 preserves the pins. Existing Session 88 tests preserve Cancel during `Pausing…`. AC-157.1–.14 now cover waiting/held delivery, acknowledgement, departure, StrictMode, both mount-crossing histories, before/after-mount Electron behavior, repetitions and AC-97.7 preservation. Rows 1–5 and H1-2 run the checks (`implementation-plan.md:192–218`; `task.md:46–60`).

`SERVICES_KEPT`, the scope check and H1-4's byte-hash comparison protect the backend/API/OpenAPI/MCP exclusion. There is no manual-check row. R1-F1 no longer leaves a schedule outside the prescribed proof. Nothing additional rejected; executing this plan would deliver the registered intent. This is plan approval, not an implementation pass.

## Q2 — Cancel paths

Accepted: `CANCEL_WHEN_RUNNING` reaches `CANCEL_PALETTE` and `CANCEL_GUARD` through existing readers. There is no separate toolbar Cancel or cancel chord. `CANCEL_CARD` uses the in-flight id; both services report null while Paused (`conversion.py:497–501`, `download.py:660–664`). Confirm actions call the guarded commands (`ConvertPage.tsx:993–995`, `DownloaderPage.tsx:961–963`), including a request delivered after navigating from elsewhere. `CONFIRM_CANCEL_GATE` reads the current context ref; `CONFIRM_CANCEL_CLOSE` checks only `kind === 'cancel'`, covers Idle too, and reads exactly the values named in `[confirm, cancelEnabled]`. Clear/remove confirms stay intact (`implementation-plan.md:113–121,196–203`).

`CANCEL_STALE_POLL` now explicitly cites both Start resets and Resume-to-Start paths (`conversion.py:254–278`, `download.py:433–457`; plan `:117,530`). It accurately describes the accepted renderer-cache boundary: a click admitted on cached Processing after the backend pauses can still POST a flag, which the next Start clears. It does not promise fresh backend-state gating. `TRANSCRIPT_STOP_KEPT` remains supported by its immediate paused-stop behavior (`transcript.py:275–280,739–751`). No additional route left live while the page observes Paused was found; nothing rejected.

## Q3 — Browse hold

Accepted: `BROWSE_HOLD` creates its one token before any frames run. A joined press schedules nothing. `BROWSE_TAKE_ON_MOUNT` takes either waiting or held state and clears its listener; `BROWSE_ACK` acknowledges synchronously through `preventDefault` on a cancelable event. An acknowledged event is not held again. A waiting run must still own its token before dispatch, so taking, dropping or replacing that token cannot leave a stale callback that opens another picker (`implementation-plan.md:122–125`).

`BROWSE_DROP` is installed before `navigateShell`, whose synchronous hashchange sees `/convert` and keeps a new off-page request (`shell-nav.ts:4–6`). Leaving Convert clears waiting and held state; returning does not restore it. In the scratch probe, History A, History B, held joining, mount-before-frames, mounted rapid presses, subsequent presses, effect replay, departure/return and token replacement all held. All 84 enumerated frame-boundary pairs of pre-mount presses opened one picker, with no request or drop listener remaining. Removing token identity reproduced two pickers in History B; removing drop reproduced a stale picker. AC-157.5 and .14 now pin the relevant histories using controlled frames and, for .14, the real page under StrictMode (`:209,218`; `task.md:49,52,60`). R1-F1 is fixed; no new defect found.

## Q4 — Electron proofs

Accepted as a plan: row 3a requires interception count, page absence during delay, eventual mount and no chunk/MIME failure before row 3b depends on the handler. A fresh app and first Convert visit avoid cached chunks. The race spec checks page absence before the key press, reads the main-process dialog counter after settling and requires exactly one picker. AC-157.11 waits two frames plus 150 ms and checks continued absence before departure, reaching the held drop path. S8 stops and routes back if delay or chunk loading fails; it forbids patching around the precondition (`implementation-plan.md:212–216,338–352,382`; `task.md:50–54`).

The uniform delay and 20 repeats are now correctly described as complementary to the unit-controlled straddle histories. `AC977_KEPT` retains the real-use immediate key press. Convert uses local FFmpeg jobs and real backend states, with a measured observation window; Downloader launches the real backend and uses the explicitly declared in-page seam, rather than claiming a real download without the network. Existing Session 88 tests prove Cancel during `Pausing…`. The copied cleanup records backend pid/start time and owns its Electron child handle (`queue-pause-feedback.test.ts:151–283`). Nothing additional rejected. Actual protocol feasibility and host timing remain execution obligations, guarded by S8/S7; no fresh Electron pass is claimed here.

## Q5 — Pins, registers and scope

Accepted: `PINS_NAMED` identifies exactly the two old Paused-cancel expectations (`convert-page.test.ts:429`, `downloader-page.test.ts:293`). Inspected remaining Cancel tests use Processing or check other state rules. `PAUSED_FIXTURE` changes only the new tests' list responses; it preserves the shared fixtures and existing assertions. Rows 1/3 check insertion-only edits and rows 2/4 bind test-side hashes. No further necessary assertion edit was demonstrated; execution still owes the full UI run.

`CHORDS_CHECKED` correctly distinguishes enabled-primary Ctrl+Enter from the F1 event lost before subscription. Registering F1 without adding a third implementation is sound. D-1110's preserved AC-97.7 plus forced-race proof serves the goal; the handed M-5/M-6/M-8 decisions show no additional uncovered mandatory-human item. The revised token and additional regression history carry out D-1108; no new product ruling is needed.

MEU writes use `meu_status.py`; issue resolution uses the inherited `issue_triage` model adapter with named-issue field restrictions, an exclusive handle, expected hash and staged parse/difference checks. F1 uses `issue_triage.py add`; generated documents use render tools. Byte inspection confirms the named LF/CRLF/mixed files. The inherited Red and line-ending checkers implement the checks claimed and passed their fixture selftests. The new copies, baseline and session gate still require the scheduled scope/constant adaptations; absent future scripts are not represented as already verified. Nothing additional rejected.

## Checklist Results

Manual procedures were performed by `codex-independent-reviewer`; null exits identify source observations, not successful test commands.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read both complete files; trace revised ACs and dependency rows | null | Same two-MEU scope; .14 present in Red, Green and gate scope. |
| PR-2 Unstarted confirmation | pass | Inspect target folder, declared new paths and git status | null | Two plan Markdown files only; 27 rows unchecked; five future test paths absent. |
| PR-3 Task contracts | pass | Inspect each row's owner, deliverable, check and status | null | 27 unstarted work rows with concrete commands/source-read procedures. |
| PR-4 Validation realism | pass | Trace assertions, helper/checker sources and model schedules | null | Both straddles now pinned; runtime feasibility has a failing precondition and S8. |
| PR-5 Source-backed planning | pass | Compare issue/grouping rulings, canon and HDP decisions | null | D-1100 honored; no uncovered mandatory-human class demonstrated. |
| PR-6 Recheck readiness | pass | Map R1-F1 and Q2/Q4 notes to Round 1 response and revised checks | null | Contracts, ACs and rows carry the correction; process paperwork excluded by Mat's scope. |
| PR-7 Scope discipline | pass | Compare exclusions with canon and actual service/shortcut paths | null | No required deliverable concealed as an unscheduled deferral. |
| PR-8 Observable/control chain | pass | Trace Ctrl+O to request to mounted picker; Cancel to shared rule and guards | null | Token identity closes old callback path; negative controls expose duplicates/stale delivery. |
| PR-9 Named contracts | pass | Compare contract definitions, ACs and rows | null | No materially ambiguous competing live definition. |
| Scheduling probe | pass | `rtk proxy node C:/Temp/av-kit/qcf-r2-browse-probe.cjs` | 0 | 11 named cases and 84 frame-boundary schedules; both negative controls detected. |
| Inventory/bytes | pass | `rtk proxy python -B C:/Temp/av-kit/qcf-r2-inventory.py` | 0 | 27 ACs; 27 unstarted rows; 13 inherited/tool sources exist; five future test paths absent; byte kinds agree. |
| Inherited Red checker | pass | `rtk proxy python -B docs/execution/plans/2026-11-17-queue-pause-feedback/red-check.py --selftest` | 0 | 48 fixtures: 16 positive, 32 negative, zero wrong. Synthetic receipts only; no pytest/Vitest ran. |
| Inherited EOL checker | pass | `rtk proxy python -B docs/execution/plans/2026-11-17-queue-pause-feedback/eol-check.py --selftest` | 0 | 19 fixtures, zero wrong; all fixture writes under temporary review directory. |
| Product suites / Electron | n/a | Not run under the read-only review restriction | null | No implementation or execution-gate approval claimed. |

```json
{"schema_version": "evidence.v1", "check_id": "qcf-r2-browse-schedules", "command": "rtk proxy node C:/Temp/av-kit/qcf-r2-browse-probe.cjs", "cwd": "P:/av-kit", "scope": "Scratch transcription of proposed request lifecycle and real two-frame navigation schedule; no React/product execution", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9d6d172; plan sha256 c5eb7bdd7ed5bdddef38021d3dea13038ef66efc61cc5c6916a9b0ad65d32d7d; task sha256 f9e17914ad667eeaa854c17fe5589cc61e431902b283e6a62e08ea46e3cb13eb; read-only plan review, not a product-gate identity", "output": "History A: 1 picker; History B: 1; held joining: 1; mount before frames: 1; effect replay: 1; mounted rapid presses: 1; separate requests: 2; held/waiting departure-return: 0; token replacement: 1; off-page invocation: 1. All 84 frame-boundary pre-mount schedules: 1, no residual request/drop listener. Missing identity: 2 pickers; missing drop: stale picker.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "qcf-r2-inventory", "command": "rtk proxy python -B C:/Temp/av-kit/qcf-r2-inventory.py", "cwd": "P:/av-kit", "scope": "Plan/task ACs, unstarted work rows, explicit source/new-test paths and named byte kinds", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9d6d172; plan sha256 c5eb7bdd7ed5bdddef38021d3dea13038ef66efc61cc5c6916a9b0ad65d32d7d; task sha256 f9e17914ad667eeaa854c17fe5589cc61e431902b283e6a62e08ea46e3cb13eb; read-only plan review, not a product-gate identity", "output": "HEAD 9d6d172; 27 unique ACs; 27 unstarted task rows; 13 inherited/tool source paths present; five future test paths absent; plan folder holds implementation-plan.md and task.md only. LF/CRLF/mixed inventory agrees; both named old Paused-cancel pins still read true.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "qcf-r2-red-check-source", "command": "rtk proxy python -B docs/execution/plans/2026-11-17-queue-pause-feedback/red-check.py --selftest", "cwd": "P:/av-kit", "scope": "Inherited checker synthetic fixtures, writes confined to temporary review directory", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9d6d172; plan sha256 c5eb7bdd7ed5bdddef38021d3dea13038ef66efc61cc5c6916a9b0ad65d32d7d; task sha256 f9e17914ad667eeaa854c17fe5589cc61e431902b283e6a62e08ea46e3cb13eb; read-only plan review, not a product-gate identity", "output": "red-check selftest: 48 fixture(s) (16 positive, 32 negative), 0 wrong: []", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "qcf-r2-eol-check-source", "command": "rtk proxy python -B docs/execution/plans/2026-11-17-queue-pause-feedback/eol-check.py --selftest", "cwd": "P:/av-kit", "scope": "Inherited checker byte fixtures, writes confined to temporary review directory", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9d6d172; plan sha256 c5eb7bdd7ed5bdddef38021d3dea13038ef66efc61cc5c6916a9b0ad65d32d7d; task sha256 f9e17914ad667eeaa854c17fe5589cc61e431902b283e6a62e08ea46e3cb13eb; read-only plan review, not a product-gate identity", "output": "eol-check selftest: 19 case(s), 0 wrong: []", "fresh": true}
```

## Verdict

**approved** — R1-F1 is fixed in the plan; no new material defect was found. The prescribed implementation and checks deliver the stated intent. Execution still owes the real StrictMode page tests, chunk-delay feasibility probe, Electron repeats and fresh full scoped gate. No repository file was modified.

Non-blocking clerical carry-forward: `task.md:65` describes the correct 13/14 family counts, but its inline command still uses `n == 13` for both. Use the corresponding family count there. This is an inferable stale count that would fail closed, not a missing product behavior or a new finding.

## Recheck (round 2)

Date: 2026-11-17. Workflow: `/plan-critical-review`. Agent: `codex-independent-reviewer`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |

### Confirmed Fixes

- R1-F1: press-time token allocation and joining prevent a second deferred run; taking waiting state on mount invalidates its old run (`implementation-plan.md:122–125,529`; `task.md:52`).
- R1-F1 proof: AC-157.5 controls frames around a stand-in mount; AC-157.14 replays Histories A/B on the real page under StrictMode, including a later press that must still open its own picker. Red explicitly requires .14; Green and the gate run its file (`implementation-plan.md:209,218`; `task.md:49,52,60`).
- Prior Q2 note: the residual now cites both reset paths and Resume delegation (`implementation-plan.md:117,530`).
- Prior Q4 note: AC-157.9 states the Electron timing limit and delegates mount-straddle proof to .5/.14 (`implementation-plan.md:213,531`).

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Verdict

**approved**. Intent achieved: **yes**, for this unstarted plan's prescribed behavior and proofs. Zero current blocking findings. Completion preflight applied to the review artifact: canonical task was reread, the 27 execution/closeout rows remain unstarted, and execution belongs to the coordinator. Runtime results remain to be established by execution.

Completed: 2026-11-17 12:09 EST.
