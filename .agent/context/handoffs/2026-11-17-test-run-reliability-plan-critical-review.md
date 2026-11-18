---
date: "2026-11-17"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md"
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "trr-plan-2026-11-17-test-run-reliability"
round: 2
---

# Critical Review: test-run-reliability

> **Review Mode:** plan
> **Verdict:** changes_required (round 1)

**Current result: approved at round 2; R1-F1 is fixed, with no new findings.** The round-1 review below is preserved as the historical record, including its Findings table. The current assessment and evidence are in `## Recheck (round 2)`.

## Scope

**Intent anchor:** the two Python integration tests that failed under load wait on their workers' signals with a 60-second bound (`WORKER_WAIT_S`), so they pass with a worker slowed past 5 s and three times in a row on a host loaded to at least 85 %, and a plain run of the three files that reach those waits (the two, and `test_tts_voice_packs.py`, which reuses the TTS file's `Stack`) takes no more than 30 s longer than at row 0; every E2E Electron main process records an unhandled promise rejection and fails its close with the rejection's stack, as it already does for an uncaught exception, and still prints a warning line on stderr; `npm --prefix ui run dev` removes `ELECTRON_RUN_AS_NODE` itself and opens a window when the terminal sets it; no file under `ui/src/`, `packages/`, `mcp-server/` or `tools/` changes, and no API route, OpenAPI document or MCP tool changes; scripts and tests prove all three, with no manual check.

Reviewed the complete working-tree plan, task and four plan-local Python scripts; grouping Session 90 and its three issue records; the cited Python waits and importer; the Electron watch, environment, close path and existing harness tests; npm configuration and installed electron-vite spawn code; the inherited process checker and checker/issue-tool sources; HDP decisions and the expert-pass receipt. Applied PR-1 to PR-9 and the Materiality Gate. Claude Code/Anthropic authored the plan; Codex/OpenAI is the independent reviewer.

There are 17 ACs and 26 unstarted task rows. The four future script/test paths are absent as expected. No Critical finding exists. One High behavior defect in the committable dev proof prevents approval.

Only `C:/Temp/av-kit` was written. No pytest, Vitest, npm, uv sync/lock, Electron launch or network request ran. The adversarial probe used synthetic process snapshots and mocked launch/cleanup: it started or stopped no process. Forbidden files were not opened. The supplied `<HOME>/.config/git/ignore` sandbox difference accounts for the extra settings entry in git status; that file was excluded without opening it. The coordinator owns canonical publication and ledger recording.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F1 | High | yes | behavior | **The dev proof adopts a reused PID, can pass on an unrelated Electron window, and makes that unrelated process eligible for termination.** Confidence: High. `descendants()` retains recorded root identities, including an exited child. The collection loop then unconditionally replaces each retained PID's entry with the current `alive[pid]`, overwriting its creation time. A synthetic first snapshot records node child `(pid=101, created=1010, parent=100)`; a later snapshot contains unrelated Electron `(101, 5000, 999)`. The real `run()` returns 0 with `window: yes` and `left: 0`, writes the unrelated identity into its cleanup record, and the actual imported checker's `classify()` includes it among this launch's stop candidates. This defeats `DEV_PROOF` and AC-15: the launch need not have opened the observed window, and cleanup can terminate another session's app. | docs/execution/plans/2026-11-17-test-run-reliability/dev-proof.py:269-275; :191-198; :286-290 | Keep recorded PID/creation-time identities immutable. Exclude a live PID whose creation time differs from its recorded identity before updating the record, accepting a window, or passing ownership to descendants. Require an adversarial selftest covering a recorded child that exits and whose PID is reused by unrelated Electron, proving that its window cannot pass and its identity never reaches cleanup. Apply the same check to a reused launch root. Violates AC-15; the same ownership issue also affects AC-16. | open |

## Q1 — Goal and proof coverage

Accepted: AC-1 to AC-5 and rows 1 to 3 cover delayed workers, preserved assertions, the three-file time comparison and three loaded runs. AC-6 to AC-12 and rows 4/5 cover recorded rejections, stacks, stderr compatibility, unchanged exceptions and the three full E2E runs. AC-13 to AC-16 and rows 6/7 cover the environment wrapper and actual window observation. Row 8 and the gate cover registers and scope. There is no manual behavior-check row.

Not accepted: passing every prescribed row does not establish the window/ownership clause while R1-F1 remains. The real proof can report success on an unrelated window and target its process for cleanup. Intent is **partial**, not achieved in full.

## Q2 — Python waits

Accepted: the twelve named sites match the real files. `WORKER_WAIT` changes only the bound; `wait-check.py` checks the exact inserted blocks, substitutions, four assertion lines and CRLF. Existing polling helpers remain unchanged apart from their defaults. The signal/release distinction at TTS lines 62 and 526 is described honestly. `test_tts_voice_packs.py:249,320` reaches the shared default and is included in both timing and load runs.

The slow-worker fixture patches the real fake collaborators used by the two failing paths. Required delayed-log lines, exact assertion failure sites and two-failure Red prevent an inactive plugin from passing. The load helper starts fixed busy children and retains launcher/interpreter handles; failed or timed-out runs cannot pass its verdict. The 1800-second timeout is recorded as an internal run result of 124; the helper's overall failure exit is 1. Unchanged assertions still fail on a genuine unfinished worker, with the added delay disclosed in D-1115/S9. No further material defect found. Actual Red/Green/load/timing runs remain execution obligations.

## Q3 — Rejection watch

Accepted: preloading the listener at the single launch site reaches main before startup; appending synchronously to the existing per-launch log reaches `mainErrorRecords` and the shared close check after close/exit. The contract preserves exception records and adds one rejection record per event. The explicit compatibility warning keeps W9-7's regex meaningful. Error and string reasons, a handled rejection and a real Electron close failure have concrete oracles.

The suite-wide pin at plan line 187 honestly names the new pass condition, including shutdown. Three full E2E runs with per-run counts and S10's first-record stop are appropriate planned coverage; they are not a claim that repetition proves every possible shutdown schedule. D-1121 correctly reserves an observed product rejection for Mat rather than allowing it away. No additional blocking defect found.

## Q4 — Dev wrapper and window proof

Accepted: the wrapper removes the variable case-insensitively from a copy for its children, preserves arguments and cwd, guards imports, reports removal, and keeps preview unchanged. `exitCodeFor` specifies numeric exits and Windows null cases; the planned console-group SIGINT/SIGBREAK treatment and SIGTERM forwarding are explicit. AC-14 tests the exit mapping; actual signal delivery is not claimed as a reviewer runtime result. Registering preview separately is sound because the issue/grouping names dev, and D-1119 considers the cheaper shared-wrapper alternative.

The proof's set/unset baseline, checkout-specific Electron classification, titled `Chrome_WidgetWin_1` requirement, scratch data, and post-proof rebuild are useful. **Not accepted:** PID plus creation-time safety is lost before the inherited checker receives the record (R1-F1). Its final creation-time recheck cannot recover an original identity that the collector has already overwritten. The three existing selftests all pass, so their current coverage does not detect this concrete failure.

## Q5 — Scope, registers and safety

Accepted: no MEU is invented; Session 89 precedes this session; the handed D-1115/D-1118 briefs keep their allowed M hits, and no additional mandatory-human decision is demonstrated by their planned implementation. The named shared rejection assertion addresses the stipulated M-7 scope. Issue resolution uses the tool-backed adapter with expected hash and exclusive register handle; preview uses `issue_triage.py add`; render/check are explicit. Byte inspection confirms the listed LF/CRLF formats. Scheduled checker copies and the session gate are declared future deliverables with existing source files.

The gate runs static, targeted, runtime and full checks, preserves first failures, and binds product/API/MCP exclusions to scope/hash checks. Dev proofs openly start the real backend and claim no download/transcript/TTS action; they do **not** promise network isolation. Python paths use fakes and E2E uses its fake backend. Review itself made no network request. **Not accepted:** dev-proof process cleanup is unsafe under the reproduced ownership history; see R1-F1. No other write-scope or register defect was demonstrated.

## Checklist Results

Manual procedures below were performed by `codex-independent-reviewer`; null exits identify source observations, not successful product tests.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read both full documents and trace rows 0-8/H1/H2 to ACs | null | Same three-issue scope, order, 17 ACs and 26 unstarted task rows. |
| PR-2 Not started | pass | Inventory target folder, future paths and git status | null | Six plan files; four new script/test paths absent; no implementation row started. |
| PR-3 Task contracts | pass | Inspect every task's owner, deliverable, validation and status | null | Concrete commands or source-read procedures; future scripts have creation rows. |
| PR-4 Validation realism | fail | Trace real `dev-proof.run()` through synthetic PID reuse | null | R1-F1: unrelated window accepted and unrelated identity passed to cleanup. |
| PR-5 Source-backed planning | pass | Compare issues, grouping, HDP decisions and expert adoption against source | null | Handed brief scope and suite-wide assertion change stated honestly. |
| PR-6 Corrections readiness | pass | Inspect target/handoff paths and current round | null | Round 1; no prior correction census applies; correction has a concrete target. |
| PR-7 Scope discipline | pass | Compare exclusions with the grouping, issue scope and file inventory | null | Preview registered; no product work concealed as a deferral. |
| PR-8 Observable/control chain | fail | Trace window identity from snapshot through cleanup classification | null | Demonstrated false success under R1-F1; other named controls reach their observables. |
| PR-9 Named contracts | pass | Compare definitions, ACs and repeated row references | null | No materially competing live definition found. |
| Wait checker selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-17-test-run-reliability/wait-check.py --selftest` | 0 | 13 checks; 0 failures. |
| Load helper selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-17-test-run-reliability/load-run.py --selftest` | 0 | 16 checks; 0 failures; no worker or pytest started. |
| Dev proof selftest | pass | `rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-17-test-run-reliability/dev-proof.py --selftest` | 0 | 24 checks; 0 failures; does not cover recorded PID reuse. |
| Adversarial PID probe | fail | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/trr_pid_probe.py` | 0 | Probe successfully reproduces the defect: proof exit 0, unrelated `(101,5000,999)` adopted and classified as a stop candidate. No process launched/stopped. |
| Inventory and bytes | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/trr_inventory.py` | 0 | 17 ACs; 26 unchecked rows; six inherited helper sources present; named byte kinds agree. |
| Product suites / real windows / CPU load | n/a | Prohibited in this read-only review | null | No execution-pass claim. |

### Durable probe evidence

All Python probe executions set `PYTHONDONTWRITEBYTECODE=1` and use `-B`. Exits were captured immediately after the RTK child and before receipt reads.

```json
{"schema_version":"evidence.v1","check_id":"trr-r1-pid-reuse","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/trr_pid_probe.py","cwd":"P:/av-kit","scope":"Real plan-local dev-proof.run with synthetic snapshots and mocked launch/window/cleanup; imported real cleanup classifier; no process started or stopped","phase":"plan-review","exit_code":0,"result":"fail","tested_state":"implementation-plan sha256 c395cdc4f2114449fe736c1c584b4660479e77c76be7a0c1b1793744bf539518; task sha256 caf440eaa7765ec6887e218d168553df589b5b730be5fedaf823916d79b797d0; dev-proof sha256 159277473f0312147aa9698aaf4dfb9a65affee6c4e14bd9868a798ad1b491c8; synthetic review only","output":"synthetic stop candidates: [(100, 1000, 90), (101, 5000, 999)]; window: yes; notice: no; left: 0; PASS: window opened, notice as expected, nothing left; proof exit: 0; original child identity: (101, 1010, 100); unrelated replacement adopted: (101, 5000, 999). Probe exit 0 means reproduction succeeded, not that DEV_PROOF is correct.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"trr-r1-plan-script-selftests","procedure":"Run each of wait-check.py, load-run.py and dev-proof.py with --selftest through rtk proxy .venv/Scripts/python.exe -B and PYTHONDONTWRITEBYTECODE=1; inspect completed receipts and preserved exits","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Existing plan-local synthetic selftests only","phase":"plan-review","exit_code":null,"result":"pass","tested_state":"Plan/task/script inventory captured by trr_inventory.py; read-only plan review, not a product gate","output":"wait-check: 13 checks, 0 failures, command exit 0; load-run: 16 checks, 0 failures, command exit 0; dev-proof: 24 checks, 0 failures, command exit 0. These passing checks do not exercise the PID-reuse history.","fresh":true}
```

## Verdict

**changes_required** — R1-F1 is a reproduced High defect against AC-15 and `DEV_PROOF`: the automated window proof can pass without its launch opening a window and can target another session's process. Preserve original process identities and add the adversarial regression before execution. No other blocking defect was found. The repository remains unchanged; runtime implementation evidence is still owed after plan approval.


## Recheck (round 2)

**Date:** 2026-11-17. **Agent:** codex-independent-reviewer. **Verdict:** approved.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Confirmed fixes

- **R1-F1 / DEV_PROOF:** `dev-proof.py:217-242` builds ownership roots only from still-matching identities or exited processes, retains first observations with `setdefault`, and excludes a mismatched live holder from running IDs. Its window cannot pass, its identity never enters the record, and it cannot confer ownership on its children. The inherited classifier's identity filter therefore receives the original creation times. The independent reuse probe also included the stranger's child; neither entered the record or stop candidates.
- **Launch root:** `dev-proof.py:208-214,299,325-330` requires the root's parent PID to equal this script's PID and a creation time no earlier than one second before launch; the retained Popen handle binds the launched root. Wrong-parent and old-root histories exit 2 with an empty record. The independent boundary probe accepts the exact floor and rejects floor minus one, a missing root and another parent.
- **Post-listing confirmation:** `dev-proof.py:245-249,331-336` intersects window owners with recorded running Electron IDs, then confirms the owner's creation time in a snapshot taken after window listing. The real-run selftest refuses replacement during listing and retains the old identity for cleanup; a genuine launch window passes.
- **Same-pattern correction:** `load-run.py:108-158,273-288` reads interpreter identity through the opened handle and retains it only for the launcher or its sufficiently recent child. An unrelated holder is closed and refused. Besides the seven ownership cases and live self-identity read, the independent probe drove actual `Busy.start()` with mocked Win32 operations: it returned false, retained no handle, closed the refused handle exactly once and never called termination. The supplied plan-time kill-check receipt says two interpreters accepted and zero left; this review did not repeat its process launch.

The correction remains within D-1120 and existing AC-15/AC-16 and process-safety obligations. The goal anchor matches round 1 verbatim; there are still 17 ACs and 26 unchecked rows. `task.md` has the same SHA-256 as the round-1 reviewed state. No new decision or acceptance change is needed.

### Q1 — Goal and proof coverage

Accepted: the unchanged AC/row mapping covers all goal clauses: delayed-worker Red/Green, three loaded runs, the three-file timing comparison, rejection recording and failed close with stderr compatibility, set/unset dev window proofs, and scope guards. With R1-F1 fixed, no demonstrated false window success remains. Executing the plan successfully would deliver the stated intent. No remaining objection; this is plan approval, not a claim that implementation has run.

### Q2 — Python waits

Accepted: twelve bound substitutions preserve assertions and existing signal/poll behavior; the shared Stack callers in `test_tts_voice_packs.py` remain included in timing and load coverage. Red must show both delayed targets at their named assertion sites, so an inactive plugin cannot qualify. The timeout remains a run result of 124 that makes the helper fail, and genuine unfinished workers still fail retained assertions. The handle identity correction safely rejects unrelated interpreter PIDs. No new defect found.

### Q3 — Rejection watch

Accepted: the single launch path preloads the watch, its synchronous log reaches the shared close check, and the plan keeps exception records and the warning text consumed by W9-7. Error/string and handled/unhandled cases have automated oracles. The suite-wide pins row honestly names the changed expectation; three full runs, per-run rejection counts and S10 cover surfaced shutdown rejections without excusing them. No new defect found; runtime confirmation remains in rows 4/5 and the gate.

### Q4 — Dev script and identity safety

Accepted: the environment copy, case-insensitive removal, argument/cwd forwarding, entry guard, numeric/null exit mapping and console-group signal rules remain explicit. Preview remains separately registered under D-1119. The revised immutable identities, validated root and post-listing confirmation satisfy the R1-F1 correction and the new adversarial cases. The cleanup record does not adopt the reproduced stranger. No new defect found. Real dev launch and signal behavior were not executed in this read-only review.

### Q5 — Scope, registers and safety

Accepted: tool-backed issue resolution/add/render, narrow file inventory, line-ending checks, scope/hash guards and staged fail-fast gate remain consistent with Session 90. The Python tests use fakes and E2E uses its fake backend; the dev proof explicitly starts the real app/backend and makes no network-free claim. Repository HEAD is `79e3fa5`; status contains only the target plan folder after excluding the supplied host-ignore discrepancy, whose file was never opened. This review made no network request, wrote no repository file and launched/stopped no app or worker. No additional scope or safety defect found.

### Checklist Results (round 2)

Source observations below were made by `codex-independent-reviewer`; their exits are null. The historical round-1 failed checks above do not describe the current state.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 / PR-2 / PR-3 | pass | Read plan/task and inventory ACs, rows, future paths and git status | null | 17 ACs, 26 unstarted rows; same order/scope; planned executables have creation rows and inherited sources exist. |
| PR-4 / PR-8 | pass | Trace actual run/collect/root/window/record/classify and Busy.start; run synthetic probes | null | Prior reproduced false success is refused, genuine own window passes, and unrelated identities do not reach cleanup. |
| PR-5 / PR-7 / PR-9 | pass | Cross-check grouping Session 90, three issues, decisions, contracts and expert adoption against source | null | No unsupported scope cut or materially conflicting live contract found. |
| PR-6 substantive correction readiness | pass | Compare R1 response and changed scripts with original finding | null | R1-F1 corrected; related interpreter-handle adoption also covered. No paperwork defect is used as a delivery blocker. |
| Plan-local selftests and independent identity probes | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/trr-r2-probe.py` with PYTHONDONTWRITEBYTECODE=1 | 0 | 13 wait + 24 load + 32 dev checks pass; additional descendant/root/Busy.start probes pass. |
| Current inventory and bytes | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/trr-r2-inventory.py` | 0 | 17 ACs; 26 unchecked rows; four expected future files absent; six helper sources present; eight source byte classifications match; only plan-folder changes. |
| Rolling report structure | pass | `rtk proxy .venv/Scripts/python.exe -B tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/trr-plan-review-round-2.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/test-run-reliability/review/round-2-state.json` | 0 | OK: review_mode=plan; round 2 of 3; verdict=approved; open findings=0. |
| Product suites / real dev windows / loaded test runs | n/a | Excluded by this read-only review's scope | null | Required execution evidence remains owed after approval. |

### Durable evidence (round 2)

```json
{"schema_version": "evidence.v1", "check_id": "trr-r2-identity-recheck", "command": "rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/trr-r2-probe.py", "cwd": "P:/av-kit", "scope": "Plan-local selftests and synthetic ownership probes; PYTHONDONTWRITEBYTECODE=1; scratch output redirected to C:/Temp/av-kit/test-run-reliability/review; no process launch or termination", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "implementation-plan.md sha256 7299e6159b3a36c5aede50d83e66e96da3142c535b9a22d3b709528ef7a2bb04; task.md sha256 caf440eaa7765ec6887e218d168553df589b5b730be5fedaf823916d79b797d0; dev-proof.py sha256 745182eaf791052989900fabf33b7a70a7dc2d6c716a90a2641e610dda42b013; load-run.py sha256 491bac4be43d2f44cc267eeba39371df812af757a4eab8728a6c5c0959b348c1", "output": "wait-check selftest: 13 checks, 0 failures; load-run selftest: 24 checks, 0 failures; dev-proof selftest: 32 checks, 0 failures. Recorded child reused by unrelated Electron: exit 1, window no, original identity retained, stranger excluded from classify stop candidates. Own window: exit 0. Reuse during window listing: exit 1. Wrong-parent/old root: exit 2, empty record. Independent probes: reused child and its descendants refused; genuine orphan remains discoverable; root time boundary/wrong parent/missing root checked; actual Busy.start closes and refuses unrelated interpreter handle without termination. ROUND 2 PROBES PASS; no process launched or stopped.", "fresh": true}
```

### Verdict

**approved** — R1-F1 is fixed; no new High or Critical delivery defect was demonstrated. Intent achieved: **yes**, for this plan-review target: successful execution of the prescribed rows would establish the registered goal. Runtime implementation and execution approval remain later stages. The report is saved at `C:/Temp/av-kit/trr-plan-review-round-2.md`; canonical publication and ledger recording belong to the coordinator.
