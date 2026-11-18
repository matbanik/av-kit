---
date: "2026-11-17"
project: "2026-11-17-test-run-reliability"
meus: []
plan_source: "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-17 Meta-Reflection

> **Date**: 2026-11-17. Planned, plan-reviewed, executed, reviewed and closed on 2026-11-17.
> **MEU(s) Completed**: none. Session 90 `test-run-reliability` is test and dev debt with no MEU (grouping D-1103), as Session 78 was. It is the second and last session of the post-Session 88 triage grouping (`.agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md` §3, row 90). It ran on `main` from `79e3fa5`.
>
> - **Worker waits** (`PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD`, `resolved`). `test_tts_assets.py` and `test_youtube_adapter.py` each define `WORKER_WAIT_S = 60.0` once, and their twelve 5-second worker waits read it; every wait still returns on its signal, and four assertion lines change only their bound (`WORKER_WAIT`, `WAITS_NAMED`, `WAIT_SIGNALS_KEPT`, `TIME_GUARD`, D-1115). Three loaded runs passed at a median host load of 100 %.
> - **Rejection watch** (`E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED`, `resolved`). The E2E main-process watch records unhandled promise rejections, `close()` fails on any of them with the stack, and the `UnhandledPromiseRejectionWarning` line still reaches stderr (`REJECTION_WATCH`, `REJECTION_WARNING_LINE`, `MAIN_REJECTION_MARKER`, `REJECTION_FAILS_CLOSE`, `EXCEPTION_WATCH_KEPT`, D-1116, D-1117). No rejection was allowlisted, and every full Electron run in the session held 0 rejection records.
> - **Dev window** (`UI-DEV-ELECTRON-RUN-AS-NODE-SILENT`, `resolved`). `npm --prefix ui run dev` runs `ui/scripts/electron-vite-dev.mjs`, which removes `ELECTRON_RUN_AS_NODE` and starts `electron-vite dev`, so the window opens from an IDE terminal (`DEV_ENV_CLEARED`, `DEV_NOTICE`, `DEV_ARGS`, `DEV_SIGNALS`, `DEV_ENTRY_ONLY`, `DEV_SCRIPT`, D-1118). `npm run preview` keeps the gap and is registered open as `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` (D-1119).
>
> **Plan Source**: `docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Row 5's full Electron runs.** The row needs three full `test:e2e` runs with the watch on. It took three attempts and two rulings (D-1122, D-1123), from about 16:55 to 18:21. Attempt 1's third run failed one real-pointer drag spec that passed alone. Attempt 2's first run failed five real-pointer specs that passed alone. Attempt 3 passed two runs, and its third run failed one capture spec on a launch-teardown timeout; that spec passed alone. No spec failed twice, and no run held a rejection record. The host was shared with other sessions' gates: during attempt 3 the load had a median of 54 % and reached 100 %.
   - **The handoff.** As in Sessions 82, 88 and 89, writing the handoff from receipts took longer than the gate.

2. **What instructions were ambiguous?**
   - **AC-12's "each run passes".** The plan's S5 rule already handled a full-run failure with no rejection record: rerun the failing spec alone once, and stop only if it fails again. The coordinator's brief added a stop after a second failing full run. The two rules gave different answers, and the stricter one stopped the row twice while S5 had not fired. D-1123 read AC-12 under S5. The execution review accepted that reading "as the plan's pre-existing S5 exception, with the failed initial full run preserved and disclosed; approval does not relabel it a clean first-pass run." Row 5's attempt 3 is three complete full runs, two clean and one with a failure resolved by S5's lone rerun. They are not three clean first passes.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as in Sessions 81, 82, 88 and 89).

4. **What was missing?**
   - **The plan itself in the plan-time `decision_sources` probe.** This is Session 89 RULE-2, carried in the start prompt. The plan-time probe (`trr90-probe.txt`) still read only the grouping and the register. At H2-2 the re-run probe refused the plan, because D-1117's `chosen` quoted the warning line with two angle-bracket tokens, which the placeholder pattern reads as unfilled slots. That one line (`:428`) now says "and the rejection's stack" and "and the rejection's message", with the same meaning. The edit came after the execution review: the plan's sha256 moved from `f5c5d09b…` to `79a8ad52…`. The plan is outside `identity.py`'s inputs, and the state did not move (`trr-decision-probe-after.txt`). The handoff's Departures disclose it (RULE-2).
   - **Two carried rules met again.** H2-5's cell writes the commit draft with `write_text`, which gives CRLF on Windows (Session 83 RULE-3), so the LF message is a separate file, `trr-commit-message.txt`. `tools/review_ledger.py state` failed closed without `RECEIPTS_DIR` (Session 82 RULE-3), so the ledger's state was read from the coordinator's receipts.
   - **AC ids inside decision text.** The H1-6 coverage check reads every `AC-n` in the plan. D-1122 and D-1123 name two earlier sessions' specs by their labels (AC-49.29, AC-81.11), so the first handoff draft was refused for AC-49 and AC-81. The handoff now names them once in prose, mapped to file and line (Session 83 RULE-1).

5. **What did you do that wasn't in the prompt?**
   - **Ran each cell from a script and marked rows by script** (`trr-make-row.py`, `trr-mark-row.py`). Each Validation cell ran verbatim from a `.ps1` file, and `task.md` stayed LF.
   - **Kept every superseded receipt.** This covers row 5's attempt-1 and attempt-2 runs and their lone reruns under their own names, and the first H1-6 to H1-6b receipts from before the reruns that followed the Codex Validation Report.
   - **Ran a load probe before the heavy rows**, under the coordinator's brief. `trr-probe.ps1` waits until the host load reads 50 % or less. It ran before row 5 attempt 3 and each of its full runs, before rows 6 and 7, and before the H1-2 gate. It ran outside the cells.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **AC-1 and AC-2** failed at Red under the 6-second slow-worker plugin, at the two registered failure sites (`assert <TranscriptStatus.Processing…> is <TranscriptStatus.Done…>` and `assert 'Downloading' == 'Idle'`). The flake is a 5-second bound, not chance.
   - **AC-9** failed at Red in the real app with `Expected: 1, Received: 0`: before the watch, a main-process rejection left no record at all.
   - **AC-6 and AC-7** failed at Red on the missing rejection record. **AC-13 and AC-14** failed at Red on the missing dev script.
   - **The base dev proof** (row 6) showed the bug as Mat sees it: with the variable set, no window, and the root process exited (`trr-dev-base-set.txt`). The control opened a window.

7. **Which tests were trivially obvious?**
   - AC-8, AC-10 and AC-11 passed at Red by design. They guard the exception record, the handled-rejection path and the stderr line, and are kept out of FAIL_TO_PASS.

8. **Did pyright/ruff catch anything meaningful?**
   - No. No Python product code changed, and `packages/`, `mcp-server/` and `tools/` were untouched (H1-4), so pyright, OpenAPI and MCP were skipped by their recorded basis. ruff format and check were clean on the two test files and the plan scripts, and the UI typecheck and `eslint --max-warnings 0` were clean.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The contract names gave the tests, the handoff and both reviews one vocabulary. The plan review's one round-1 finding (R1-F1: the dev proof adopted a reused PID) became immutable process identities and an adversarial selftest before execution. The execution review approved at round 1 with 0 findings.

10. **Was the handoff template right-sized?**
    - Yes for one no-MEU session with three issues. Row 5's attempts needed their own table, and that table belongs in the Evidence section.

11. **How many tool calls did this session take?**
    - Not counted exactly. The executor's transcript ran to a few hundred calls, rows 0 to H2-6, across several context compactions. Planning, both review dispatches and H1-7 ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-6 to one executor subagent (Claude Code, Claude Opus 5.5). It ran the plan and execution review dispatches and H1-7 to H1-7b itself, and it ruled D-1122 and D-1123 on the executor's two row-5 stops.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. No delegated result needed rework after the review.
    - Codex reviewed the plan and the execution as the independent reviewer. That is not delegation.

### Decisions Log

- The twelve 5-second worker waits in the two failing files read `WORKER_WAIT_S = 60.0`; the other 125 are left — [D-1115](../plans/2026-11-17-test-run-reliability/implementation-plan.md)
- Every unhandled main-process rejection fails the close, none is allowlisted, and a later one goes to the register with its stack — [D-1116](../plans/2026-11-17-test-run-reliability/implementation-plan.md)
- The watch writes its own `UnhandledPromiseRejectionWarning` line, so `capture-inbox.test.ts` stays byte-identical — [D-1117](../plans/2026-11-17-test-run-reliability/implementation-plan.md)
- `npm run dev` runs a wrapper script that clears the variable, prints one notice and keeps the console signal rules — [D-1118](../plans/2026-11-17-test-run-reliability/implementation-plan.md)
- `npm run preview`'s same gap is registered open, not fixed — [D-1119](../plans/2026-11-17-test-run-reliability/implementation-plan.md)
- Scripts prove the fixes: a slow-worker plugin, a loaded run, a Node child, a real Electron app and a window proof with a control — [D-1120](../plans/2026-11-17-test-run-reliability/implementation-plan.md)
- Row 5 runs a third attempt with the bar of three full runs kept — [D-1122](../plans/2026-11-17-test-run-reliability/implementation-plan.md)
- Row 5's full runs are complete under the plan's S5 rule, and later Electron runs treat a no-record failure the same way — [D-1123](../plans/2026-11-17-test-run-reliability/implementation-plan.md)

D-1100 and D-1101 (Session 89's issues) and D-1102 to D-1104 (grouping §8) are read from their own logs and are not listed. No D-1121 was needed, because no rejection record appeared, and D-1124 was not used. The `decision_sources` probe was re-run at H2-2:

- First run (`trr-decision-probe.txt`): it refused the plan over D-1117's two tokens.
- After the one-line fix (`trr-decision-probe-after.txt`):
  - the grouping, alone or with the register and the three issues, gives D-1102 to D-1104;
  - with the plan and the handoff it gives D-1102 to D-1104, D-1115 to D-1120, D-1122 and D-1123;
  - no `chosen` starts with "Pending", and no brace slot is left.

Grouping §8 holds no new row since plan time.

---

## Pattern Extraction

### Patterns to KEEP
1. **Make the flake deterministic, then show the fix under real load.** A 6-second fake-worker delay turned a load-dependent failure into a certain Red. Three runs at a median host load of 100 % then showed the 60-second bound holds where the failure came from.
2. **Prove a launch bug with a control.** The dev proof ran with the variable set and unset, at base and after the fix. The base run with the variable set had no window, and the control at base had one. This avoided a click-through (Mat's direction).
3. **Keep every attempt's receipts under its own name.** Row 5's three attempts, their lone reruns and the superseded H1-6 receipts are all kept. The reviewer could recount 226 results per full run and confirm the failures were disclosed, not rerun away.

### Patterns to DROP
1. **A brief-level stop rule that overrides a plan's stop conditions without saying so.** Here the brief stopped on a second failing full run, which was stricter than S5. Defer to the plan's S-items, or name the difference.

### Patterns to ADD
1. **A coordinator brief that adds a stop rule states how it relates to the plan's stop conditions** (RULE-1).
2. **The plan-time decision probe runs the H2-2 validator's own source list against the plan** (RULE-2).
3. **An AC that requires N passing full-suite runs says in its own text how a failure without the watched signal is handled** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time** (local time, from the receipts' mtimes, all on 2026-11-17):
  - The plan review approved at round 2 (canonical copy 16:34).
  - Row 0's baseline ended at 16:49.
  - Rows 1 and 2 (Python Red and Green) ran at 16:51, the row-3 load run ended at 16:53, and row 4's Red ended at 16:53.
  - Row 5:
    - attempt 1 ended at 17:17;
    - attempt 2 ended at 17:30;
    - attempt 3's full runs ran from about 17:38 to 18:18;
    - its final check passed at 18:21.
  - Rows 6 to 8 ran from 18:22 to 18:30.
  - The H1-2 gate ran from 18:31 to 18:44. It passed on its first run, and its Electron step took 7.1 minutes at a 9 % load.
  - The execution review approved at round 1 at about 19:00, and H1-7a and H1-7b ran at 19:01.
- **Tokens:** plan review 6,273,323 (round 1) and 7,204,924 (round 2); execution review 12,731,427 (round 1).
- **Adjusted estimate** for a test-harness session that adds a suite-wide E2E condition:
  - about 6 to 13M tokens per review round;
  - about 13 minutes per full gate run on a quiet host;
  - each full Electron run takes 7 to 17 minutes, depending on what other sessions run. Budget a row that needs three full runs at 30 to 50 minutes, and more if the host is shared.

---

## Next Session Design Rules

```
RULE-1: A coordinator brief that adds a stop or rerun rule for a row says how the rule relates to the plan's own stop conditions, and defers to them where the two differ, unless the plan is amended first.
SOURCE: Session 90 row 5 (D-1122, D-1123): the brief stopped at a second failing full run, while the plan's S5 reruns a no-record failure alone and stops only on a repeat. S5 never fired, but the brief's rule stopped the row twice and cost two extra full-suite attempts on a shared host.
EXAMPLE: before, "stop after a second failing full run"; after, "a full-run failure is handled by the plan's S5 (lone rerun, stop on a repeat); a rejection record is S10".
```

```
RULE-2: The plan-time decision_sources probe runs the H2-2 validator's decision-source list against the plan itself (plan, grouping, register and the session's issues), so a placeholder-like token in decision YAML is refused before the plan review, not at closeout.
SOURCE: Session 90 H2-2: Session 89 RULE-2 was carried, but the plan-time probe (trr90-probe.txt) still read only the grouping and register; the re-run probe refused the plan for two angle-bracket tokens in D-1117's chosen text, fixed after the execution review.
EXAMPLE: before, decision_sources([grouping, register], issues); after, decision_sources([plan, grouping, register], issues), and quoted output samples in decision YAML name a variable part in words ("and the rejection's stack").
```

```
RULE-3: An AC that requires N passing full-suite runs states in its own text how a failure without the watched signal is handled, so the executor, the coordinator and the reviewer read "passes" the same way.
SOURCE: Session 90 AC-12: "three full test:e2e runs ..., each with 0 rejection records" was read under S5 only by D-1123, and the execution review accepted it as the plan's S5 exception that does not make the runs clean first passes.
EXAMPLE: before, "each run passes with 0 records"; after, "each run holds 0 records; a failing spec with no record is rerun alone once under S5 and disclosed; N clean first passes are not required".
```

---

## Next Day Outline

1. **Next:** the post-Session 88 triage grouping is finished; Session 90 was its last queued session (grouping §8 D-1104). The next step is a new triage or grouping pass for Mat, with Session 74 and the open issues. The prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, plus Session 89's, 88's, 83's and 82's rules, carried in the start prompt. Every Electron launch now fails on an unhandled main-process rejection, so the next session that touches main-process code meets the watch in every E2E run.
4. **Codex validation scope:** each session's own plan and execution loops.
5. **Time estimate:** set by the next plan.
6. **Still open for Mat:**
   - The commit of Session 90 by the coordinator, with no push from the agent (H2-5 has the draft and the path list).
   - The real-pointer and launch-teardown flakes seen in row 5:
     - three already have issues: `DOWNLOAD-QUEUE-DRAG-OVER-MISS`, `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` and `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`;
     - no issue names the Convert drag at `convert-queue.test.ts:1182` or three of the capture specs exactly. The next triage can file them or fold them into those issues.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | A few hundred in the executor's transcript, rows 0 to H2-6; not counted exactly |
| Time to first green test | The Python Green at 16:51, the same minute as its Red; the watch's Green in row 5 and the dev script's at 18:28 |
| Tests added | 5 UI unit tests (1619 in 142 files in the gate, against 1614 in 140 at row 0): `rejection-watch.test.ts` (3) and `dev-script.test.ts` (2). 3 Electron tests in `main-rejection-watch.test.ts` (226 in the gate). Python unchanged at 3087, with two test files' waits changed |
| Codex findings | Plan review: R1 changes_required with 1 High (R1-F1), R2 approved with 0. Execution review: R1 approved, 0 findings |
| Handoff Score (X/7) | 6/7. Every AC has evidence, the gate passed on its first run, and the execution review approved at round 1 with 0 findings. AC-12 rests on the plan's S5 exception rather than three clean first passes, and the first handoff draft needed a coverage repair |
| Rule Adherence (%) | 90 (9 of 10 sampled rules followed) |
| Prompt→commit time | Planned, executed, approved and closed 2026-11-17; the coordinator commits without a push |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution; the executor never dispatched or wrote a verdict |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. H2-5 is a draft and a path list only |
| Red before Green | AGENTS.md §Testing | Yes. Rows 1, 4 and 6 failed by assertion before Green |
| Never raise a timeout past the plan, add a retry or lower the load bar | The executor brief; plan S8, S9 | Yes. `WORKER_WAIT_S` is 60, the load threshold stayed 85 %, and no spec or timeout changed for row 5's flakes |
| A rejection record is never rerun away | Plan S10 | Yes. No record appeared in any of the eight full Electron runs, the gate's included |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `eol-check: 19 scope path(s), 0 problem(s)` |
| No raw home path in tracked files | The executor brief; Session 83 | Yes. The gate's `home-path` step passed |
| Change the register only through `tools/issue_triage*` and `issue-resolve.py` | The executor brief | Yes. Row 8 |
| Stop only this session's processes, by recorded id and creation time | The executor brief; plan S11 | Yes. Other sessions' `electron.exe` processes were left running |
| The plan-time probe reads the plan as a decision source | Session 89 RULE-2 | No. The plan-time probe read the grouping and register only; H2-2 found D-1117's tokens (RULE-2) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "a3707a5b-24b9-4989-a528-bc4ea719a8a8"
  task_class: tdd
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 2
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: execution_contract
    cited: true
    influence: 3
  - id: session_discipline
    cited: true
    influence: 2
  - id: dual_agent_workflow
    cited: true
    influence: 3
  - id: commits
    cited: true
    influence: 3
  - id: validation_pipeline
    cited: true
    influence: 3
  - id: rtk_token_optimized_commands
    cited: true
    influence: 1
  - id: instruction_coverage_reflection
    cited: true
    influence: 2
loaded:
  workflows: [execution_session, issue_triage]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
    - .agent/context/handoffs/TEMPLATE.md
    - docs/execution/reflections/2026-11-17-queue-convert-fixes-reflection.md
    - docs/execution/reflections/2026-11-15-e2e-harness-hardening-reflection.md
    - .agent/context/handoffs/2026-11-17-test-run-reliability-plan-critical-review.md
    - .agent/context/handoffs/2026-11-17-test-run-reliability-implementation-critical-review.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:keep-line-endings, P1:red-before-green, P1:never-raise-timeout-or-retry-to-pass, P1:rejection-record-is-a-stop]
conflicts:
  - "The coordinator's brief stopped row 5 at a second failing full run, stricter than the plan's S5 lone-rerun rule; resolved by D-1122 and D-1123."
  - "H1-6's AC coverage check counts AC ids quoted inside decision text (AC-49.29, AC-81.11) as plan ACs; the handoff names them in prose."
note: "One no-MEU harness session; a first-run gate and a round-1 execution approval, with row 5 run three times under a brief rule stricter than S5."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "A brief-level row-5 stop rule duplicated the plan's S5 with a different answer."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 2
    execution: 1
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 1
      medium: 0
      low: 0
    - review: plan
      round: 2
      critical: 0
      high: 0
      medium: 0
      low: 0
    - review: execution
      round: 1
      critical: 0
      high: 0
      medium: 0
      low: 0
  churned_findings: 0
  finding_categories:
    boundary_validation: 1
  verdicts:
    changes_required: 1
    approved: 2
meu_work_classes: []
```

The review churn counts the ledger's recorded rounds in the session's two loops, the plan loop and `trr-execution-2026-11-17-test-run-reliability`. The plan loop's round 1 found R1-F1: the dev proof adopted a reused PID, so it could pass on an unrelated Electron window and hand that process to cleanup. Round 2 confirmed it fixed by immutable process identities and an adversarial selftest. The execution loop approved at round 1 with 0 findings (`usage=12,731,427`).
