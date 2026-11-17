---
date: "2026-11-16"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "csd-plan-a1-2026-11-16-convert-settings-drafts"
round: 2
---

# Critical Review: convert-settings-drafts execution amendment A1

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Intent Anchor

an open capture settings edit keeps only what the user changed, follows every other saved value and saves only the changed fields; a Convert Advanced edit (CQ, scale, audio) or preset pick survives settings arriving or changing; and a Convert queue card shows a Cut's in and out points as time codes, a waiting job's current place in the queue, and, for a Cut, the encoder it really runs; and two Adds of the same file never queue the same output file (amendment A1).

Round 2: executing the revised amendment would deliver its stated intent. A1-R1-F1 and A1-R1-F2 are fixed in the plan; no new finding remains. Claude Code/Anthropic authored the plan and amendment; Codex is their independent reviewer. This is plan approval, not an implemented-product pass. The round-1 assessment and evidence below are retained as history; the current assessment is under Recheck (round 2).

## Scope

The following scope/identity records the first pass. Current hashes and recheck evidence follow in round 2.

Reviewed A1 only: the whole current plan/task for context, the amendment script and receipts, the original round-2 report, and the relevant conversion service, domain transitions, SQL repository, API wiring/routes, MCP HTTP caller, media adapter and existing service/API tests. Applied the workflow's Materiality Gate and PR-1 through PR-9. The original approved decisions and executed rows 0–4 are not reopened. D-1060 is accepted as Mat's ruling.

Working-tree identity: `main`, HEAD `b6b124a`. Reviewed SHA-256:

| File | SHA-256 |
|---|---|
| implementation-plan.md | `20a48bc01b038bd1aca9961997387eb652fe4831104b65f3ffc8238db40a25c6` |
| task.md | `eb39bc7cb89ec8f25c7d70ca725da5724c636d48b58c82680df833aa11209884` |
| services/conversion.py | `21ff80a6608b87aa7b31db2d3ef249f02503ce012e0508e51c90e6252369cbc5` |

All reviewer writes are under `C:/Temp/av-kit`. No repository file was edited. No pytest, Vitest, package operation, network request, real FFmpeg/Electron process, app interaction or process inventory/termination ran. Product execution remains the coordinator's work after amendment approval. Scratch probes used in-memory service source with precisely A1's proposed lock/held-set changes, real domain objects and independent fake collaborators; they are design counterexamples, not an implemented-product test pass.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| A1-R1-F1 | High | yes | behavior | `QUEUE_OUTPUT_RESERVED` leaves the skip branch unchanged, but `_jobs_for_path` makes a probe-error job `Failed` even when the resolver returned `skipped=True` (`conversion.py:305-320`). With job A Processing at `clip_cut.mp4`, its partial file on disk, and `skip_existing=True`, a second Add with a transient probe failure therefore creates a retryable Failed job B at A's path. After A finishes, `reset_failed(B)` keeps that path and the retry overwrites A. The scratch model reproduced Failed/shared-path → retry Done/overwritten bytes. AC-152.13/AC-152.14 omit this combination, so their normal cases can pass while the amended AC-152 output-reservation goal fails. Confidence: High. | `docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md:130`; `:150`; `docs/execution/plans/2026-11-15-convert-settings-drafts/task.md:55` | Distinguish a genuine terminal Skipped row from a probe-error Failed row before allocating its final destination. A retryable Failed row must receive an unheld, nonexisting suffixed path. Add the processing-file/probe-failure/second-Add/retry regression to A1. Preserve AC-30.1's error reporting and AC-30.2's genuine Skipped path alias unchanged. | fixed |
| A1-R1-F2 | High | yes | behavior | D-1061 says Remove and Clear free names by deleting rows, while the sole holding set comes from stored rows. Neither operation stops the active worker (`conversion.py:263-273`); `_dispatch` already holds the job and may still write its path after deletion (`:538-598`). Remove or clear A while its media call has started but has not created the output, then Add the same source: the queue snapshot and disk both look free, so B gets A's path. A completes and B subsequently overwrites it. Both operations reproduced this in the scratch model: two writer calls, same destination, final bytes from B. AC-152.15 tests only waiting removal and does not protect active-writer lifetime; this defeats AC-152.13's separate-Add uniqueness when the first job has not finished. Confidence: High. | `docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md:130`; `:209`; `:521` | Keep the active media writer's output reserved independently of whether its queue row remains, until the media operation has actually exited. Pending removal and a clear with no active writer may still free names immediately. Extend A1's regression coverage to both Remove and Clear while a worker is held before output creation, followed by another Add and completion. | fixed |

## Round-1 Q1 — Rule, retry, release and skip (historical)

Accepted: Pending, Processing, Failed and Cancelled are the right persisted holding states. Both retryable states return to Pending without changing `output_path` (`domain/conversion.py:328-337`); freeing them merely because they are not running would reintroduce collisions. They do not hold a name forever without recourse: removing/clearing an inactive row releases it. Done and Skipped are terminal, so disk existence can govern their names; deleting a Done output should permit reuse. Windows `Path` equality is case-insensitive, including set membership, as required here.

Accepted: a held name with no disk file must be suffixed even with `skip_existing` enabled. Different Cuts can share a source and nominal destination while describing different requested outputs. D-1062 follows the existing within-one-Add reservation rule. Successful disk-based skipping preserves AC-30.2 exactly: its first Pending row already has a file, and its third Add must remain Skipped at that same path.

Not accepted: disk-based skip allocation is also applied before an error upgrades the new row to Failed (A1-R1-F1). Terminal Skipped aliases are harmless; retryable Failed aliases are not. Nor can deletion of a running row be treated as proof that its writer stopped (A1-R1-F2). These are new-Add collisions after A1, not a demand to migrate preexisting colliding rows.

## Round-1 Q2 — Concurrency and actual writers (historical)

Accepted: one per-service Add lock covering queue read through commit closes the two-Add race in this deployment. `wiring.py:228` constructs one service; the synchronous HTTP creation route calls `add_to_queue` (`routes/conversions.py:152-160`), and MCP uses HTTP. The product-source search found no other insertion of conversion jobs outside `add_to_queue`. Reset saves an existing job rather than inserting one, so including both retryable states is essential.

The Add lock is separate from `_lock`, which protects processor start. The worker, remove, clear and reset do not acquire it, and `MediaAdapter.probe` does not call back into the service: no lock cycle was found. Holding it across ffprobe serializes subsequent Adds for the duration of every probe. Probe defaults to no timeout (`adapter.py:452-471`), so a hung probe can stall subsequent Adds indefinitely; that is an acknowledged serialization tradeoff without a specified latency contract, not a separate blocker here. Existing database-write contention is also not eliminated by the Add lock.

Not accepted: serializing Adds alone cannot reserve an active writer whose row has been deleted. The row-lifetime assumption in `QUEUE_OUTPUT_RESERVED`, rather than a missing second Add lock, causes A1-R1-F2.

## Round-1 Q3 — AC-152.13 through AC-152.17 (historical)

Accepted as planned tests: separate `add_to_queue` calls, asserted Pending statuses and exact suffixes exercise the actual producer. AC-152.13 repeats the Cut case through a real SQLite unit of work, catching persistence/path round-trip mistakes in addition to the memory case. Status/retry guards and deleted-Done/disk-skip cases are appropriate. The new file is absent, so these remain test designs, not executed tests.

The AC-152.16 barrier sits in `probe`, after the queue snapshot. Without the lock, both callers can take the empty snapshot before either commits; with the lock, the first reaches the two-second timeout, catches `BrokenBarrierError` and finishes, then the second reads the committed reservation. The ten-second joins bound the intended fake-only scenario. The scratch model produced distinct paths with A1 and duplicate paths with held-set-only/no-lock, confirming a meaningful negative oracle. As usual, the actual test must assert two returned jobs, no thread exceptions and no surviving threads; an arbitrary host suspension beyond a timeout is not a mathematical scheduling guarantee. No separate timing blocker was demonstrated.

Not accepted as complete coverage: none of these ACs combines disk skip with probe failure and retry, or removal/clear with a writer still active before its output exists. The planned tests can all pass while the two findings remain.

AC-152.17 runs both whole existing test files in row 4b and the targeted/full session gate. `test_conversion_service.py` is explicitly read-only and still matches its row-0 hash. The API test file is outside the allowed edit set; it is to be run unchanged. Its API fake-service tests protect routing/wire behavior; they do not independently prove the reservation algorithm.

## Round-1 Q4 — Rows, human check and gate (historical)

Accepted: 4a precedes 4b; its required Red families are AC-152.13, AC-152.14 and AC-152.16, while AC-152.15 is an already-passing guard. Existing names are callable, so the intended Reds are behavioral assertion failures. The two verbatim validation cells parse with zero PowerShell errors; their referenced tools exist, and the absent new test is an explicit creation. Child exits are captured immediately. Row 4b runs both new Python files, the whole existing service suite and the API suite, then types, lint, formatting and byte-based EOL checks.

Row 5 preserves the first-round human record and launch record, waits for Mat to quit, checks/stops only the recorded launch, relaunches and records the new tree, then requires HC-1 through HC-5. Inspection of `dev-app-procs.py:209-223` confirms termination by pid after rechecking creation time. I did not run that helper. HC-5 specifies two separate Adds before completion, different card output names and both files after completion; that is a concrete pass/fail check for the original report.

The Harness clause at plan line 65 and task's generic Processes clause at line 38 still mention executable-path stopping. They should be aligned with D-973. The amended operational row is explicit that name/path are not the stop selector, and its named helper enforces that rule; no harmful alternative process-stop command was demonstrated. This wording is not a finding.

The declared session gate includes the new file in formatting and targeted Python, the API tests in targeted Python, and both in the full `tests/` run. `session-gate.ps1` is not yet written and is explicitly created at H1-2; this is an execution obligation, not a missing undeclared tool. The blockers concern behavior that these planned checks omit.

## Round-1 Q5 — Register, scope, decisions and line endings (historical)

Accepted: row 7 checks the original register hash before adding the new issue, adds through the SSOT CLI, then binds resolution of all six issues to the post-add hash. The resolver uses an exclusive handle and verifies the hash before replacing the register (`issue-resolve.py:195-207,251-254`). It limits parsed changes to the named issues' resolution fields. Rendering remains tool-owned. This is a coherent sequential register flow, without rewriting row-0 evidence.

The amendment probe records absence of `test_convert_output_reserved.py`; my audit independently confirms it remains absent and is not a row-0 scope key. The Files Modified table and gate requirements explicitly include it as a new LF file. That establishes its baseline without altering `baseline-scope.json`.

MEU-152 is a reasonable home after Mat's D-1060 ruling: it already changes this service and covers the Convert queue. A new registry unit is unnecessary for this small service correction. D-1061's status set/lock and D-1062's successful-skip semantics need no mandatory-human hit outside the handed-over set; their behavior still needs the corrections above. D-1063 implements D-1060's authorized scope; any M-8 classification is within the stated hand-over. None requires a new M-4 shape/schema change, M-7 assertion change, gate waiver, disclosure or permission expansion. Row 5's existing M-10 remains planned.

The amended rows' declared repository outputs remain within Files Modified, the plan folder and closeout artifacts; scratch issue staging, process records and receipts stay under `C:/Temp/av-kit`. They do not authorize editing Session 82/83 content or baseline files. `conversion.py` currently has 653 CRLF and 653 LF terminators, with no bare LF; row 4b explicitly checks its CRLF preservation and the new file's LF. The in-memory reviewer model never wrote this source back.

## Round-1 Checklist Results (historical)

Manual observer for the procedures below: `codex-independent-reviewer`. These results assess the amendment's design, not product execution.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read A1 contracts, ACs and rows 4a/4b/5–8/H1/H2 together | null | Same intended behavior, dependencies and six-issue closeout |
| PR-2 A1 not started | pass | Inspect task statuses, source and new-file existence | null | 4a/4b unchecked; source still has per-call-only reservation; new test absent |
| PR-3 Task contract | pass | `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/review/parse-rows.ps1` plus manual owner/deliverable inspection | 0 | Both verbatim cells parse; required tools exist |
| PR-4 Validation realism | fail | Compare AC-152.13–17 with both reproduced sequences | null | Probe-error retry and active deletion are untested and preserve overwrite |
| PR-5 Source-backed planning | pass | Compare D-1060–1063 with source, AC-30.2 and HDP | null | Authority and source basis are sound; implementation implications have findings |
| PR-6 Handoff/review readiness | pass | Read amended H1/H2 rows and scope inventories | null | Both MEU handoffs, 17 MEU-152 ACs and independent execution review scheduled |
| PR-7 Scope discipline | pass | Check A1 exclusions against its goal and actual writer chain | null | No migration, multiprocess lock or other-queue work demanded; findings concern new collisions inside A1 |
| PR-8 Reachability/negative oracle | fail | Trace resolver → job status → reset → media writer, and delete → running writer | null | Two reachable counterexamples remain despite Add serialization |
| PR-9 Contract consistency | pass | Compare named contracts, ACs, decisions and row consumers | null | No separate materially ambiguous rule; both findings concern concrete behavior |
| Design counterexample harness | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/convert-settings-drafts/review/a1_probe.py` | 0 | Normal sequential/concurrent cases work; no-lock negative collides; both remaining overwrites reproduced |
| PowerShell cell parsing | pass | `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/review/parse-rows.ps1` | 0 | 4a errors=0, 4b errors=0; commands never executed |
| Hash/EOL/scope audit | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/convert-settings-drafts/review/audit.py` | 0 | Exact plan/task hashes; service CRLF; existing service tests baseline-identical; A1 test absent |
| AV-1–AV-5 implementation evidence | n/a | A1 implementation has not begun | null | Test results and completed-code quality remain execution obligations |
| AV-6 source-backed criteria | pass | Review AC source column and decision precedents | null | Local Canon/Human-approved bases stated |
| Product suites and runtime | n/a | Explicitly prohibited for this review | null | No product suite or live-app command ran |

```json
{"schema_version":"evidence.v1","check_id":"csd-a1-design-counterexamples","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/convert-settings-drafts/review/a1_probe.py","cwd":"P:/av-kit","scope":"A1 in-memory lock/held model with scratch-only media and repository fakes","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"plan=20a48bc01b038bd1aca9961997387eb652fe4831104b65f3ffc8238db40a25c6;task=eb39bc7cb89ec8f25c7d70ca725da5724c636d48b58c82680df833aa11209884;service=21ff80a6608b87aa7b31db2d3ef249f02503ce012e0508e51c90e6252369cbc5","output":"probe-error second Add: Failed clip_cut.mp4 same_as_processing: True; retry: Done first file after retry: output from call 1. remove during active writer: same_path: True second_status: Pending; writer calls: 2 final bytes: output from call 2. clear_queue: same observations. positive sequential: clip_cut.mp4, clip_cut_1.mp4, clip_cut_2.mp4. positive concurrent: clip_cut.mp4, clip_cut_1.mp4, threads_finished True. negative held-without-lock: clip_cut.mp4, clip_cut.mp4 collision True. Model observations only, not product-suite execution.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"csd-a1-pwsh-parse","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/review/parse-rows.ps1","cwd":"P:/av-kit","scope":"verbatim row-4a and row-4b validation cell syntax","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"task=eb39bc7cb89ec8f25c7d70ca725da5724c636d48b58c82680df833aa11209884","output":"row 4a pwsh parse errors: 0; row 4b pwsh parse errors: 0; parse: pass; commands were parsed only, never executed","fresh":true}
```

The first model run reproduced both defects. A later rerun initially reused its scratch output files and stopped at a positive-control assertion; the harness was corrected to create a fresh scratch fixture directory per invocation. The final isolated run above exits 0 and confirms both counterexamples plus the lock's positive/negative controls. This was a scratch-fixture repair; no product expectation or source was changed. Two exploratory `rg` commands named an incorrect helper path/glob; their diagnostics are not relied on as negative evidence.

## Round-1 Verdict (historical)

`changes_required` — two High, blocking behavioral findings; no Critical finding. Correct the reservation contract and test matrix for A1-R1-F1 and A1-R1-F2, then return the amendment through plan review before A1 product edits. Preserve the original approved work, D-1060, existing assertions and row-0 evidence. No new human product fork was identified.

Report delivered at `C:/Temp/av-kit/csd-a1-plan-review-round-1.md`; the coordinator installs the canonical report. The review's completion preflight applies to this artifact only; the 24 unchecked product-task rows remain intentionally untouched. Runtime behavior, SQLite execution of the future tests and the eventual full gate remain unverified here.

## Round-1 Report Validation (historical)

The read-only closeout parser returned `OK: review_mode=plan; round 1 of 3; verdict=changes_required; open findings=2`. Command: `rtk proxy .venv/Scripts/python.exe -B tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/csd-a1-plan-review-round-1.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/convert-settings-drafts/review/a1-report-state.json`, exit 0. Both finding ids are new to this amendment loop; no historical finding was reopened or erased.

🕐 Completed: 2026-11-16 20:03 (EST)

## Recheck (round 2)

**Date:** 2026-11-16. **Agent:** codex-independent-reviewer. **Scope:** execution amendment A1 only, including the round-1 corrections D-1064/D-1065. Original approved decisions D-966 to D-972 and executed rows 0–4 remain accepted. D-1060 is Mat's ruling. This review made no repository edits and ran no product suite, package command, network request, real media process, dev-app command or process enumeration/termination. All reviewer writes are under `C:/Temp/av-kit`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| A1-R1-F1 | open | fixed |
| A1-R1-F2 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Confirmed Fixes

- **A1-R1-F1:** `implementation-plan.md:132,153,215,575` and `task.md:54-55` now allocate a skip alias only with `allow_skip=error is None`. A probe/track error retains Failed/error reporting but gets a path outside disk, per-call and queue/writer reservations. AC-152.18 adds the partial-file/probe-error/retry sequence and a completed-file guard. In the independent scratch model, the fixed rule produces a separate path and preserves A's bytes; removing only `allow_skip` reproduces Failed/shared-path → retry/overwritten bytes.
- **A1-R1-F2:** `implementation-plan.md:134,153,216-217,591` and `task.md:54-55` now reserve the active call's output independently of its stored row. AC-152.19 requires both Remove and Clear before output creation, distinct destinations and both files' own bytes. AC-152.20 checks release after cancellation/call exit and immediate release of a removed Pending row. The scratch model preserves both files; removing only writer tracking reproduces the overwrite for both operations. Both positive and deliberately failing Red-style paths release/join their held worker.
- **Process wording:** the Harness clause at `implementation-plan.md:66` and `task.md:38` now agrees with D-973: recorded pid and creation time through the named helper, never name/path alone.

### Q1 — Rule, retry, release and skip

Accepted: `QUEUE_OUTPUT_RESERVED` reserves Pending/Processing/Failed/Cancelled rows; `reset_failed` retains the path for either retryable status (`domain/conversion.py:328-337`). A Cancelled row therefore remains protected through retry and releases on Remove/Clear after its writer exits. Done/Skipped are terminal and hold no stored reservation: disk presence blocks writing, and deleting a Done file permits its name again. A removed Pending job frees at once; a removed active job frees after its call ends, with any resulting file still protected by the disk check. This supplies a release path rather than a permanent in-memory hold. Windows `Path` equality/hash also protects case-only variants; the scratch model exercised an uppercased stored path.

Accepted: D-1062 keeps skip disk-based. A held name without a file must suffix and queue, because another Cut can request a different segment from the same source. A successful Add with a disk file may still return a terminal Skipped alias even while another row holds that path. Such a row cannot be retried and never writes; AC-30.2 expressly requires that alias. D-1064 now prevents the unsafe Failed alias without hiding AC-30.1's error. The model checked the successful Skipped alias beside the partial file and the failed-probe/retry path separately.

No remaining failure of this rule was found. Existing colliding rows remain the stated migration exclusion; this review does not widen A1 into rewriting stored data.

### Q2 — Concurrency and active-writer ordering

Accepted: `QUEUE_ADD_SERIAL` holds a per-service lock from queue read through commit, including probes. `wiring.py:228` constructs the single service, `routes/conversions.py:152-160` reaches Add, and MCP uses HTTP (`mcp-server/src/toolsets/registry.ts:109,392-445`). The fresh product-source writer census finds only `conversion.py:222` calling `conversion_jobs.add`; the infrastructure mapper/repository is its persistence path. Reset/reorder update existing rows. This is sufficient for the given one-process model; it does not claim cross-process exclusion.

The queue-read-then-writer-copy order in `ACTIVE_WRITER_RESERVED` is sound. Before a worker first reads a row it registers the path. If the worker reads before Add's queue snapshot, a running writer is in the set even if its row was deleted. If it reads after that snapshot, a row it can still run was in the snapshot's holding states; a row already deleted at the snapshot cannot pass the worker's subsequent `get` check. If the writer exits before the set is copied, it can no longer write; a remaining row or disk file provides its applicable protection. A stale `_next_pending` result cannot write after deletion because `_run_one` rereads the row. The model checked that early return releases its transient reservation too.

The separate `_writer_lock` protects brief set mutation/copy operations, not the media call or probes. The worker never takes `_add_lock`, and no inverse lock order or probe callback into Add was found. A slow ffprobe can stall subsequent Adds; the adapter's default probe has no timeout (`adapter.py:452-471`). That acknowledged tradeoff does not introduce a worker/start/remove lock wait or violate a specified latency requirement. Existing database contention remains separate. No new concurrency blocker was demonstrated.

### Q3 — AC-152.13 to AC-152.20 and Red cleanup

Accepted as test design: AC-152.13 uses separate production `add_to_queue` calls, exact suffixes and Pending statuses with skip off/on; the Cut case also uses the real scratch SQLite stack. The independent model produced base, `_1`, `_2` Pending paths through SQLite with both skip settings. AC-152.14 covers held/retryable states; AC-152.15 and AC-152.20 are already-passing release guards. AC-152.18 and AC-152.19 add the two missing overwrite sequences, asserting concrete paths and final file bytes. Probe and track failures share the same `error`/`allow_skip` decision, preserving both failure classifications.

AC-152.16's barrier is downstream of the queue read. Without the Add lock both callers take the empty snapshot, meet and collide; with it the first barrier wait breaks at two seconds, releases normally, commits and permits the second snapshot. A broken barrier releases subsequent waits too. The model returned exactly two jobs, no thread exception and no surviving thread, with distinct paths in the fixed model and one path when only the Add lock was removed. This is a controlled fake-only ordering, not an absolute guarantee under arbitrary host suspension longer than a test timeout. The implementation must retain these result/exception/thread-completion assertions; counting only distinct returned paths would be insufficient.

The new held-media design (`implementation-plan.md:181`, `task.md:54`) sets its event in `finally`, and its wait also observes cancellation and a ten-second deadline. Thus a failed path assertion releases the writer instead of waiting for success-only cleanup. The scratch probe deliberately raised during both pre-file and partial-file waits and joined cleanly. Actual new tests remain to be written; this review does not certify their eventual cleanup code.

AC-152.17 still runs the complete existing service/API files in row 4b, targeted Python and the full `tests/` gate. Neither file has a working-tree diff. The service suite matches its row-0 hash. The API suite is outside the allowed edit set; its fake-service tests protect route/wire behavior, while service tests prove allocation. No skipped or rewritten assertion is proposed.

### Q4 — Rows, human check and full gate

Accepted: rows 4a/4b retain Red before Green, immutable expectations, exact commands and preserved exits. The revised verbatim cells both parse with zero PowerShell errors. Red requires AC-152.13, .14, .16, .18 and .19 assertion failures; .15/.20 are guards. Row 4b runs both new Python files and both whole existing suites, then types/lint/format and byte-based CRLF/LF checks. Referenced tools exist. The absent new test and `session-gate.ps1` are explicit scheduled creations, not hidden prerequisites.

Row 5 (`task.md:57`) preserves the first human/launch records, waits for Mat to quit, stops only the recorded launch through D-973, relaunches/records and requires HC-1 through HC-5. The process helper was inspected, never run. The earlier executable-path-only wording has been removed. HC-5 has a concrete pass/fail observation: two separate Adds before completion, same file/kind, different output names and both completed files. Rows 6–8 and H1/H2 consume the revised AC/issue counts and preserve the independent execution-review gate.

The declared session gate includes `test_convert_output_reserved.py` in formatting and targeted Python, `test_api_conversions.py` in targeted Python, and both in the fresh full Python suite (`implementation-plan.md:377-379`). The executor must implement that gate and later bind its evidence to the actual changed state. This plan review neither ran it nor treated existing rows 0–4 receipts as proof of A1.

### Q5 — Register, scope, decisions and line endings

Accepted: row 7 checks S4 against the original register hash, adds `CONVERT-OUTPUT-NAME-REUSED` through the SSOT CLI, reads the resulting hash, then resolves all six against that post-add hash. The resolver's exclusive handle/hash check and parsed-field restriction remain intact (`issue-resolve.py:195-254`). The add is intentional authorized scope; the old baseline is not rewritten. This is a sequential flow with fail-fast exits, not a claimed single transaction across both operations.

The original A1 probe records the new test's absence before A1. The current audit confirms it is still absent and not a `baseline-scope.json` key; Files Modified explicitly declares the new LF file and the gate includes it. That establishes the amendment's new-file baseline without falsifying row-0 evidence. Source SHA-256 is unchanged since round 1/post-row-4 and has 653 CRLF terminators, zero bare LF. Row 4b measures that property and the new test's LF; the full gate preserves the other declared line endings.

MEU-152 is a sound home for the authorized Convert queue/service correction. D-1061–D-1065 serve D-1060 and the existing suffix/retry/error contracts. No mandatory-human hit outside M-3/M-5/M-6/M-8 was found: there is no schema or public shape change, existing assertion rewrite, quality waiver, permission expansion or new disclosure. The writer correction preserves Remove/Clear's existing behavior; it does not add a new stop operation. Their ordinary implementation choices and possible M-8 acceptance bookkeeping are covered by the stated hand-over. Row 5's M-10 remains the explicit human action already planned. The amended rows' declared writes remain within Files Modified, the plan folder, closeout artifacts and `C:/Temp/av-kit`; sibling Sessions 82/83 remain excluded.

### Current identity and observed evidence

| File | SHA-256 |
|---|---|
| implementation-plan.md | `1b2d711ce16191763795e387e511004c6b37e4fceb3b69b9a35f259b70efc3bf` |
| task.md | `f2ebe98b5e39c200d45623488e4fddb181dcd6480d05e518293bb4e5a2ea8256` |
| services/conversion.py | `21ff80a6608b87aa7b31db2d3ef249f02503ce012e0508e51c90e6252369cbc5` |

## Checklist Results

Manual observer: `codex-independent-reviewer`. These results assess the current amendment's design; historical round-1 failures above are resolved by this recheck.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare revised contracts, ACs and rows 4a–8/H1/H2 | null | Same three mechanisms, test families and six-issue flow |
| PR-2 A1 unstarted | pass | Inspect source hash, task statuses and new-file existence | null | 4a/4b unchecked; service unchanged; test absent |
| PR-3 Task contract | pass | Parse current 4a/4b cells and inspect owners/dependencies | null | Zero syntax errors; explicit outputs and acyclic dependencies |
| PR-4 Validation realism | pass | Trace new regression negatives and run scratch design controls | null | Both prior overwrites reproduced by removing only their fixes |
| PR-5 Source-backed decisions | pass | Compare D-1060–D-1065 with 08:292, domain retry rules and HDP M-list | null | Sound corrections under Mat's ruling; no unhanded M hit |
| PR-6 Correction/review readiness | pass | Trace both original finding ids through revised contracts/tests/closeout | null | Both fixed; rolling independent review and handoffs preserved |
| PR-7 Scope discipline | pass | Compare amended exclusions against source and requested intent | null | Existing-row migration and stopping removed calls are unnecessary to the enqueue fix |
| PR-8 Reachability/negative oracle | pass | Trace HTTP/MCP → Add → repository → worker/media; model both negative controls | null | No other insertion path; reservation lifetime reaches actual writer |
| PR-9 Contract consistency | pass | Compare named rules, decisions, ACs and task consumers | null | No materially divergent live behavior found |
| AV-6 Source-backed criteria | pass | Inspect revised AC sources | null | Local Canon/Human-approved bases named |
| AV-1–AV-5 implementation checks | n/a | A1 implementation has not begun | null | Future code/tests require execution verification |
| Product suites and app | n/a | Explicit review restrictions | null | No product-suite, live-app or network command ran |

```json
{"schema_version":"evidence.v1","check_id":"csd-a1-r2-design-model","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/convert-settings-drafts/review/a1_r2_probe.py","cwd":"P:/av-kit","scope":"A1 source transformed only in memory; scratch fakes, files and SQLite databases","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"plan=1b2d711ce16191763795e387e511004c6b37e4fceb3b69b9a35f259b70efc3bf;task=f2ebe98b5e39c200d45623488e4fddb181dcd6480d05e518293bb4e5a2ea8256;service=21ff80a6608b87aa7b31db2d3ef249f02503ce012e0508e51c90e6252369cbc5","output":"probe-error/retry fixed collision=False first bytes=call 1; no-skip-fix collision=True first bytes=call 2. Remove and Clear fixed collision=False; no-writer-fix collision=True; every worker finished. Cancel/call exit, Pending remove and stale selected row release names. Forced Red cleanup finishes both partial/pre-file writers. Barrier fixed returned=2 distinct=2; no-add-lock returned=2 distinct=1; no surviving threads. Pending/Processing/Failed/Cancelled Windows case folding passes. Scratch SQLite separate Adds with skip False and True produce Pending base,_1,_2. MODEL PASS; not product implementation evidence.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"csd-a1-r2-pwsh-parse","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/convert-settings-drafts/review/parse-rows.ps1","cwd":"P:/av-kit","scope":"current verbatim row 4a and 4b validation syntax","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"task=f2ebe98b5e39c200d45623488e4fddb181dcd6480d05e518293bb4e5a2ea8256","output":"row 4a pwsh parse errors: 0; row 4b pwsh parse errors: 0; required Reds include test_ac_152_18 and test_ac_152_19; Green runs both whole existing suites. Commands parsed only, never executed.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"csd-a1-r2-audit","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/convert-settings-drafts/review/audit.py","cwd":"P:/av-kit","scope":"plan/task identity, safe source/test hashes, new-file baseline and referenced tools","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"plan=1b2d711ce16191763795e387e511004c6b37e4fceb3b69b9a35f259b70efc3bf;task=f2ebe98b5e39c200d45623488e4fddb181dcd6480d05e518293bb4e5a2ea8256","output":"Plan 646 lines LF; task 105 lines LF. Service SHA unchanged from round 1; CRLF=653 LF=653. Existing service tests baseline_match=True. New A1 test exists=False baseline has key=False. Invoked tools and existing plan scripts present; session-gate.ps1 absent, explicitly created at H1-2. 24 unchecked execution rows remain; reviewer makes no implementation-complete claim.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"csd-a1-r2-existing-tests","command":"rtk proxy git diff -- tests/unit/test_conversion_service.py tests/e2e/test_api_conversions.py","cwd":"P:/av-kit","scope":"existing service/API tests required unchanged by AC-152.17","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"service_tests=f16ea9aca43e0ff8e1a2ca7b3f1ab12940726aa575f08724060e8481a0d56427;api_tests=1972bb18c6f0a3a9705d0a92acb4d09ae8c026496ae2b4f390d95a62537bd2ce","output":"Empty unfiltered diff: neither file changed in the working tree.","fresh":true}
```

## Verdict

`approved` — both prior High behavioral findings are fixed in the amendment; no new High/Critical finding or unresolved human product decision was found. Intent achieved: yes, as a plan. Continue with A1's authorized Red/Green rows, the full repeated human check, session gate and independent execution review. This verdict does not authorize a push or certify code that has not been written.

Report: `C:/Temp/av-kit/csd-a1-plan-review-round-2.md`. The coordinator copies the complete report to the canonical path. Remaining risk is implementation fidelity, actual test cleanup and measured runtime behavior; those remain execution obligations rather than reasons to block this clean plan.

🕐 Completed: 2026-11-16 20:40 (EST)
