---
date: "2026-11-17"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-17-queue-pause-feedback/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "qpf-plan-2026-11-17-queue-pause-feedback"
round: 2
---

# Critical Review: queue-pause-feedback

> **Review Mode:** plan
> **Verdict:** approved (round 2)

## Scope

**Intent anchor:** on the Convert and Downloader pages the toolbar's Pause button reads "Pause after this job"; after a click it reads "Pausing…" and is disabled, and the processor status reads "Queue stops when the current job ends", until the queue reports Paused (then Resume shows) or ends in another way; Cancel still stops the running job at once; the services keep pausing between jobs; on the Transcript page "Pause" keeps its name and its waits between videos end within a second of a pause or stop (D-1090); and no API, OpenAPI document or MCP tool changes.

Reviewed the whole working-tree implementation plan, task and sole existing plan-local script at HEAD `ba6d8ef`, including the Round 1 response, 22 ACs and 26 unstarted rows. Traced the pending lifecycle through the actual queue hooks, commands, pages and Convert/Downloader worker loops; checked Transcript waits, cited tests, Electron helpers, build-plan canon, Session 88, the issue, HDP and the expert-pass receipt. Read only the requested SOURCE RECORD line of the orchestration log.

Claude Code/Anthropic authored the plan; Codex/OpenAI is the independent reviewer. Applied PR-1–PR-9 and the Materiality Gate within the user's substantive review scope. The original Findings table below is retained verbatim as round-1 history; the round-2 summary closes both findings. There are zero current findings and no Critical finding.

Only `C:/Temp/av-kit` was written. No product suite, package operation, Electron launch or network request ran; forbidden secret paths were not opened. Model probes transcribe the proposed rules and use installed Query core; they do not execute the absent React implementation. The coordinator owns canonical report publication and ledger recording.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F1 | High | yes | behavior | **Remount after queue-cache expiry erases a valid pause request.** Confidence: High. PAUSE_MARK retains only the mark indefinitely; the real queue queries retain inactive data for five minutes. Pause a job lasting longer than that, leave its page for over five minutes, then return while the same job still runs. Both pages map the initial missing queue data to Idle. PAUSE_PENDING_HOOK therefore clears the surviving mark before the first list response; Processing with the same job then returns without Pausing… or its status. This defeats PAUSE_MARK/PAUSE_STATUS and the AC-155.6, AC-155.7 and AC-155.8 lifecycle promise. Their planned tests never remount with an evicted list. | docs/execution/plans/2026-11-17-queue-pause-feedback/implementation-plan.md:110–115; ui/src/renderer/src/features/converter/ConvertPage.tsx:109–113; ui/src/renderer/src/features/downloader/DownloaderPage.tsx:180–184; ui/src/renderer/src/lib/query-client.ts:3–4 | Distinguish an unavailable/loading list from an observed Idle state before clearing a mark. Add a fake-time unmount/remount case past the real list gcTime, hold the first GET, then return Processing with the marked job; the mark and pending presentation must survive. Cover both page integrations. | open |
| R1-F2 | High | yes | behavior | **A failed refresh creates a wildcard mark that survives a completed pause/resume.** Confidence: High. Under PAUSE_MARK_SET, successful POST plus failed GET stores jobId null. Leave the page; job c1 finishes and the backend pauses, then another client resumes c2 before this page returns. No page hook observed Paused, and the real list hooks do not poll while unmounted. PAUSE_PENDING_RULE treats the null mark as pending for c2 and every subsequent Processing job. Pause stays disabled and the status promises a stop that is no longer requested. This contradicts D-1091's job-change clearing and AC-155.3/AC-155.6/AC-155.14's intended pending lifecycle; their isolated tests all permit this sequence. It concerns a pause originally sent in this window, not the accepted edge of an external pause lacking feedback. | docs/execution/plans/2026-11-17-queue-pause-feedback/implementation-plan.md:111–114; implementation-plan.md:185–188; implementation-plan.md:196; ui/src/renderer/src/features/converter/useConversionQueue.ts:65–70; ui/src/renderer/src/features/downloader/useDownloadQueue.ts:55–60 | Specify a bounded reconciliation policy for an unknown job rather than treating null as a permanent wildcard across runs. Add successful-POST/failed-GET → unmount → unseen Paused/resume → remount Processing with a later job, and prove Pause is usable. If renderer-only observations cannot distinguish the histories, state and settle that specific fallback limitation under D-1091/HDP instead of claiming the job-id guard covers it. Preserve the no-API-change constraint. | open |

## Q1 — Goal and proof coverage

Accepted: label, disabled Pausing… and status map to AC-155.1/.2/.7/.8/.10/.12; Cancel to .11 and unchanged command/card enablement; between-jobs behavior to .10 and the unchanged service loops; Transcript wording and waits to .13/.16–.18; no API/OpenAPI/MCP changes to the declared scope and H1-4's hash comparison. Rows 2/2b → 3/3b → 4 → H1-2 run those proofs, with automated Electron tests and no human-check row (`task.md:48–61`).

The remount and spent-mark regressions now have AC-155.19–.22 and are included in Red, Green and the gate. Executing the revised plan would deliver the goal under D-1091's explicit renderer-only limits. Nothing additional rejected. This is plan approval, not a claim that implementation tests have passed.

## Q2 — Pending state correctness

Accepted: `PAUSE_PENDING_HOOK`/`PAUSE_STATUS` take `queue.data?.processor`; an undefined list returns false without destroying a mark. AC-155.19 proves actual five-minute collection and a held remount GET for both kinds; .20/.21 cover each real page integration. `PAUSE_MARK_SET` makes a failed post-POST read resolve without a mark; Paused/Idle also set none. An unbound mark carries `markedAt`, binds only before the 15-second deadline, and then uses job identity; at the deadline it is spent. The hook's timer is required even without a poll (AC-155.6), and .22 replays both spent histories (`implementation-plan.md:110–115,185–204`).

Accepted: both awaited `cancelQueries` calls precede cache replacement and marking. Installed-core probes confirm that late responses from polls started before and during the direct GET cannot replace the authoritative list, even though production query functions do not consume AbortSignal. Start/resume/cancel clear after POST success; observed Paused/Idle/job change also clear. Failed jobs return to the pause-first loop; a last job can end Paused with nothing left, then Resume goes Idle. Palette and Cancel retain the intended behavior. No new binding/timer/ordering defect demonstrated.

D-1091 explicitly accepts two limits: a failed read shows no Pausing… although pause lands; an unseen resume within 15 seconds of a between-jobs mark can bind the resumed job until it ends (`implementation-plan.md:410,536–542`). The latter was reproduced, not treated as solved. External-client/reload feedback limits also remain accepted.

## Q3 — TRANSCRIPT_WAKE

Accepted: Event retains a set-before-wait wake; positive waits check pause/stop, use a monotonic deadline, and clear a spurious event under the lock before waiting again. A flag set across a clear is checked again on the next loop, so the wake cannot turn into an entire uninterruptible delay. Start/resume clear flags and event together; zero-duration waits still yield; injected sleep is untouched. Delay/batch waits reach the fetch flag check, retries return through it, and rate-cap waits retain their post-slice check (`transcript.py:217–273,487–498,568–594,655–672`; contract `implementation-plan.md:119`). No busy loop or nested-lock requirement is prescribed.

AC-155.16/.17 now synchronize on a test-side `_sleep` entry Event before sending pause/stop; this removes the fixed-offset assumption. AC-155.18 retains short real waits to check normal delay, an already-set wake, and start reset. Two-second response bounds tolerate normal host scheduling but cannot prove arbitrary host starvation; the execution runs must pass unchanged. No Transcript blocker found.

## Q4 — Electron proofs and width

Accepted as a runnable plan: local lavfi clips, software libx265 re-encode and scratch app data; the host calibration supports an approximately 28-second observation window, with up to 180 seconds to finish. The Downloader seam is installed by addInitScript followed by reload before the tested page's first list read. Both paths use Session 81's pid/start-time-bound backend stop and their own Electron process handle (`convert-queue-labels.test.ts:162–294`; `implementation-plan.md:192–197,329`). No network media or process-name cleanup is prescribed.

The 700-pixel containment/no-horizontal-scroll checks cover all three states; AC-155.15 measures Clear finished's x coordinate within 0.5 px on both pages and checks label overflow. These measure TOGGLE_WIDTH's visible promise. Three row-4 runs and the final gate, with S7/S8 stops, remain necessary execution evidence. No new Electron design defect found; actual layout fit and runtime timing were not run here.

## Q5 — Pins, registration and scope

Accepted: the fixture's header label and two width classes are the sole existing expectation edit. Toolbar pins read the label constant; page tests read their initial status before clicking and retained ids afterwards; Transcript's existing whole-duration pins inject sleep. Source inspection found no additional required expectation edit; full UI/Python checks remain prescribed. Current CRLF/mixed/LF byte counts match the plan.

The sole existing plan-local script, `register-meu-155.py`, uses `tools.meu_status.model`; its selftest, wrong-hash refusal and scratch dry run passed independently again. It adds 27 LF register lines, one phase-10 anchor and one matrix row, with docs CRLF and MEU-155 pending at 10.10. Future checker scripts and their source copies are explicitly scheduled and present where required. Resolution uses the copied issue_triage model adapter with a hash/difference restriction; the new issue uses `issue_triage.py add`, followed by render checks (`task.md:46,55–56`).

D-1090/D-1091's handed-over choices, their revised limits and D-1092–D-1097's reversible choices serve the goal; no additional M hit outside the allowed hand-over classes was demonstrated. Cancel-while-Paused remains an existing, explicitly registered follow-up. Nothing additional rejected.

## Checklist Results

Manual observations were made by `codex-independent-reviewer`; null exits below are manual source traces, not successful shell exits.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read both whole files and trace ACs to rows | null | 22 ACs, 26 unstarted rows, including all four new regression ACs in Red/Green/gate. |
| PR-2 Unstarted scope | pass | Inspect git status, HEAD, plan folder and declared new paths | null | HEAD ba6d8ef; only the plan folder is relevant dirty work; four new product/test files absent. Host-ignored settings entry excluded without opening. |
| PR-3 Task contract | pass | Inspect task owners, deliverables, dependencies and exact validation cells | null | Implementation and closeout stages have executable validation or explicit source-read procedures. |
| PR-4 Validation realism | pass | Trace required tool/helper paths and observable assertions | null | 14 named sources exist; new tools are scheduled creations; automated Electron, hook/page remounts and wait-entry tests cover behavior. |
| PR-5 Source-backed planning | pass | Compare grouping, issue, SOURCE RECORD line, canon and HDP decisions | null | Supplied rulings honored; no unsourced product choice or additional mandatory-human exception demonstrated. |
| PR-6 Recheck readiness | pass | Compare prior findings, Round 1 response and revised definitions/ACs/rows | null | Both ids map to executable correction checks; handoff/review path remains explicit. Process paperwork excluded by user scope. |
| PR-7 Scope discipline | pass | Compare exclusions with worker code, canon and rulings | null | No required deliverable disguised as an unscheduled deferral. |
| PR-8 Observable/control chain | pass | Trace toolbar/palette → commands/cache → hook/page and Transcript flags → waits | null | Both prior histories corrected; no new dead-end producer or materially false-passing gate demonstrated. |
| PR-9 Named contracts | pass | Compare single-statement contracts, AC descriptions and task references | null | No materially ambiguous live behavior definition; canonical contracts resolve stale prose estimates. |
| Round-2 lifecycle/core probe | pass | rtk proxy node C:/Temp/av-kit/queue-pause-feedback/review/round2-pending-probe.mjs | 0 | Both kinds: collected-list remount, failed-read fallback, deadline boundary, binding, retirement, both poll cancellations; disclosed ambiguity reproduced. |
| Registration probe | pass | rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/queue-pause-feedback/review/registration-probe.py | 0 | Selftest ok; wrong hash refused; scratch dry run ok; pending at 10.10; LF/CRLF preserved. |
| Inventory/bytes | pass | rtk proxy python -B C:/Temp/av-kit/queue-pause-feedback/review/round2-inventory.py | 0 | 22 distinct ACs, 26 unstarted rows, 14 sources present, four new files absent; byte kinds match. |
| Product suites / Electron | n/a | Not run: read-only plan-review scope | null | No execution-gate or implementation approval claimed. |

The first scratch core probe wrongly expected a cancelled fetchQuery promise to reject; this installed core can instead resolve reverted cached data. Corrected only that probe oracle to inspect fetchStatus and final cache content. The original failed receipt is retained; the corrected run above passed. No product defect or changed product-test expectation is inferred from that scratch mistake.

```json
{"schema_version": "evidence.v1", "check_id": "qpf-round2-pending-model", "command": "rtk proxy node C:/Temp/av-kit/queue-pause-feedback/review/round2-pending-probe.mjs", "cwd": "P:/av-kit", "scope": "proposed lifecycle model plus locally installed Query core; no React or product suite", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD ba6d8ef; working-tree plan sha256 f73b03c26f3654bdf3278d39951613f17c7e75d1d29fe41855ebab6c6f46eec9; read-only plan review, not a product-gate identity", "output": "Both kinds: collected list preserves mark; failed read sets none; unbound true at 14999 ms, false at 15000 ms; bound mark survives expiry, clears on next job; late polls before/during GET dropped; accepted unseen-resume ambiguity reproduced.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "qpf-round2-registration", "command": "rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/queue-pause-feedback/review/registration-probe.py", "cwd": "P:/av-kit", "scope": "plan-local register script, dry-run outputs only in scratch", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD ba6d8ef; working-tree plan sha256 f73b03c26f3654bdf3278d39951613f17c7e75d1d29fe41855ebab6c6f46eec9; read-only plan review, not a product-gate identity", "output": "selftest: ok; wrong hash returned 1; dry-run returned 0; 27 LF register lines; docs CRLF; one anchor, one matrix row; MEU-155 pending, 10.10, dependencies MEU-45 and MEU-46.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "qpf-round2-inventory", "command": "rtk proxy python -B C:/Temp/av-kit/queue-pause-feedback/review/round2-inventory.py", "cwd": "P:/av-kit", "scope": "plan/task source paths and named file bytes", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD ba6d8ef; working-tree plan sha256 f73b03c26f3654bdf3278d39951613f17c7e75d1d29fe41855ebab6c6f46eec9; read-only plan review, not a product-gate identity", "output": "22 distinct ACs; 26 unstarted rows; 14 named sources exist; four new implementation/test files absent; CRLF and mixed counts match the plan; exactly one old Pause fixture label.", "fresh": true}
```

## Verdict

**approved** — the prescribed implementation and checks now deliver the stated intent under the explicitly disclosed D-1091 limits. Both prior High findings are fixed in the plan; no new finding. Execution still owes the real hook/page tests, wait tests, three Electron runs and fresh scoped gate. No repository file was modified.

## Recheck (round 2)

Date: 2026-11-17. Workflow: `/plan-critical-review`. Agent: `codex-independent-reviewer`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |
| R1-F2 | open | fixed |

### Confirmed Fixes

- R1-F1: undefined observed processor preserves the mark; both real queue-hook GC/remount probes and page integrations are explicitly required (`implementation-plan.md:112,115,188,201–203,516`; `task.md:48,50,59`).
- R1-F2: failed read makes no mark; a null-id mark has a timestamp, binds before 15 seconds, and expires otherwise; .22 tests the missed-pause/resume history for both kinds. The remaining short-window ambiguity is named in the HDP brief (`implementation-plan.md:110–113,185,188,196,204,410,541–542`; `task.md:48,50`).
- Prior Q2 note: two awaited cancellations prevent stale poll writes around the direct read; .4/.5 require a late-poll check (`implementation-plan.md:113,186–187,518`). The independent installed-core probe also held a poll started during that read.
- Prior Q3 note: test-side wait-entry Events replace fixed offsets for pause and stop (`implementation-plan.md:198–199,519`).

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Verdict

**approved**. Intent achieved: **yes**, for this unstarted plan's prescribed behavior and proofs. Zero current blocking findings. Residual runtime uncertainty is actual host scheduling, Electron fit/timing and the yet-unwritten hook implementation; the execution rows test these rather than this review claiming they have already passed.
