---
date: "2026-11-18"
project: "2026-11-18-eval-describe-raw-bytes"
meus: []
plan_source: "docs/execution/plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-18 Meta-Reflection

> **Date**: 2026-11-18. Planned, plan-reviewed, executed, reviewed and closed on 2026-11-18.
> **MEU(s) Completed**: none. Session 95 `eval-describe-raw-bytes` is eval tooling and run-book debt with no MEU (D-1196). It is the only session of the 2026-11-18 register-residuals grouping (`.agent/context/grouping/2026-11-18-eval-describe-session-grouping.md` §3, row 95), run on `main` from `3e61b5b`.
>
> - **The capture** (`RAW_CAPTURE`, `NO_OVERWRITE`, `NAMED_REFUSAL`; D-1201 A, D-1203, D-1204). `docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py` runs Session 64's harness `describe` in a subprocess and writes its stdout bytes unchanged. It refuses an empty capture, a BOM, bytes that are not UTF-8, a CR byte, cp437 mojibake, a CUT count other than one, a failing and a timed-out harness, with exit 1 and a named reason. It never overwrites, and a write or close that fails removes the file it created (`write_new`, the execution review's F1).
> - **One guard** (`ONE_GUARD`; D-1201 A). The script loads `MOJIBAKE` and `CUT` from Session 92's `eval-rerun.py` by path and holds no pattern of its own; `eval-rerun.py` is unchanged.
> - **The run book** (`STEP3_NAMES_SCRIPT`). `eval-run.md` step 3 runs `eval-describe.py capture`, with a dated note; 5,748 to 6,980 bytes, LF only.
> - **The proof.** Both old redirect forms reproduced the mojibake at row 1, and the new `check` refuses both receipts and Session 64's own. A capture on the real harness is byte-identical to an independent direct read (36,533 bytes).
> - **The records.** `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` is `resolved`; grouping row 95 is `executed`; the nine bound record files keep their row-0 hashes.
>
> **Plan Source**: `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The H1-2 gate's host-load wait.** Run 1 (stamp `20261118-215027`) passed every step up to `edr-old-refused` and stopped at `host-load: still above the 50 % bar after 619 s` (79.6 %). Programs outside this session held the load; a second wait read 93.8 %. Run 2 ran the cell unchanged at 39.6 % and passed.
   - **The execution review's F1.** Round 1 found that a write or close failure after the exclusive create left a partial `OUT` that `check` accepted. The correction (CVR round 1) went Red, then Green, then ran the gate a third time.
   - The rows themselves, from the receipts' mtimes:

     | Step | Time |
     |---|---|
     | Plan review round 1, approved | 21:06 |
     | Row 0 baseline (run twice) | 21:24 |
     | Row 1 Red | 21:36 |
     | Rows 2 to 5 | 21:37 to 21:39 |
     | Row 6 audit | 21:41 |
     | H1-2 gate run 1, stopped at host load | 22:00 |
     | H1-2 gate run 2, passed | 22:31 |
     | H1-3 to H1-6b | 22:32 to 22:36 |
     | Execution review round 1, changes required | 22:55 |
     | CVR round 1 Red and Green | 22:59 to 23:00 |
     | H1-2 gate run 3, passed | 23:10 |
     | Execution review round 2, approved | 23:26 |

2. **What instructions were ambiguous?**
   - **Who updates a count that a correction moves.** The CVR raised the test count from 25 to 29, and `current-focus.md`'s Session 95 entry quoted 25. The file was outside the CVR's scope, so the executor named it and the coordinator made the change (RULE-2).

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as in Sessions 74 and 88 to 94).

4. **What was missing?**
   - **A failed write in the plan's Boundary Inventory.** AC-6 covered overwrite, refusal and timeout, but not a write or close error after the exclusive create; the reviewer found it by injecting ENOSPC (RULE-1).
   - **A receipt format for hashes.** `rtk proxy` adds a `[rtk] No hook installed` line to redirected output, so a hash receipt written by a redirect carries a line the later comparison does not expect (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Ran each Validation cell from a `.ps1` file**, the cell copied verbatim after an environment header (`PYTHONIOENCODING`, `PYTHONDONTWRITEBYTECODE`, `RECEIPTS_DIR`, scratch `TMP` and `TEMP`, `ELECTRON_RUN_AS_NODE` unset), and marked rows with a script that keeps `task.md` LF.
   - **Made every hand edit with a byte-level Python script** that kept the file's line endings, and wrote the CVR hash receipt from Python rather than a redirect.
   - **Kept each superseded run's receipts** in their own folders (`gate-run1`, `gate-run2`, `h1-6-run1`, `h1-6-run2`) before a rerun overwrote them in place.
   - **Two self-inflicted slips.** Row 0's first run stopped on 22 E501 lines in `red-check.py` as copied from Session 83; they were wrapped, formatting only. A scratch script tripped ruff FURB167 and was fixed after it had run.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The Red** (row 1): all 25 tests failed by their first assertion before the script existed, and both old redirect forms (`edr-old.ps1`, one `pwsh -NoProfile -File` run) reproduced the mojibake.
   - **The execution review's ENOSPC injection** found F1. The new test `test_ac_6_capture_write_failure_leaves_no_file` failed in its four cases (`4 failed, 25 passed`) before `write_new`, and passed after.
   - **The live check** (row 3, AC-9) compared the capture with an independent `npx tsx` read and found them equal.

7. **Which tests were trivially obvious?**
   - AC-1's clean pass and AC-7's usage errors; they pin the interface rather than find a bug.

8. **Did pyright/ruff catch anything meaningful?**
   - No product code changed. Ruff caught only formatting in scratch and copied scripts (E501 in `red-check.py`, FURB167 in a scratch script).

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The contract names gave the tests, the handoff and both reviews one vocabulary, and the reviewer named F1 by `RAW_CAPTURE`.

10. **Was the handoff template right-sized?**
    - Mostly. The CVR's Departures sub-bullets repeat what the Quality Gate and History tables already carry (slim_candidate below).

11. **How many tool calls did this session take?**
    - Not counted exactly. The executor's transcript ran to a few hundred calls, rows 0 to H2-6, across context compactions. Planning, the review dispatches and H1-7 to H1-7b ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b, the CVR and H2-1 to H2-6 to one executor subagent (Claude Code, Claude Opus 5.5). It ran the review dispatches and H1-7 to H1-7b itself.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. The executor's work needed one correction after review (F1).

### Decisions Log

- Put the capture script beside `eval-run.md` and import Session 92's guard by path, so no record file and no Session 92 file changes — [D-1201](../plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md)
- Keep the tests as a pytest file in this plan folder, run by path; each asserts the script exists first — [D-1202](../plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md)
- Run Node on tsx's CLI with no shell, and exit "build first" when `dist/index.js` is missing — [D-1203](../plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md)
- Never overwrite; use new `s95-*` roots and keep Session 64's roots and receipts — [D-1204](../plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md)
- Resolve the issue with `issue-resolve.py`, bound to the row-0 register hash — [D-1205](../plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md)
- Assert both old redirect forms in the Red, run in one `pwsh -NoProfile -File` script — [D-1206](../plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md)

**Read from their own logs, not listed:**
- D-1196 is on the issue.
- D-1198 to D-1200 are grouping §8.
- D-1207 to D-1210 are unused; execution needed no decision.

**The `decision_sources` probe was re-run at H2-2** (`edr-decision-probe-h2.txt`), with the plan, the grouping and the register with the issue:
- it reads D-1196 (triage), D-1198 to D-1200 (grouping) and D-1201 to D-1206 (planning), the same ten ids as at plan time (`edr-decision-probe.txt`, byte-identical);
- grouping §8 alone still reads D-1198 to D-1200;
- nothing was amended, so no `chosen` and no brace slot changed.

---

## Pattern Extraction

### Patterns to KEEP
1. **Reuse a guard by import, not by copy.** One pattern in one file; the stub-guard test proves the script refuses with whatever the loaded module holds.
2. **Prove the old form fails before the fix.** Row 1 ran both old redirects in a clean `pwsh -NoProfile -File` and counted the mojibake, so the fix proves a change.
3. **Keep each superseded run's receipts in its own folder.** The reviewer could read gate runs 1 to 3 side by side.

### Patterns to DROP
1. **Restating a correction in three places.** The CVR's Departures sub-bullets, the Quality Gate row and the History row say the same thing; one place could hold it.

### Patterns to ADD
1. **List every failure after create as a boundary for a file-writing step** (RULE-1).
2. **Name, in the correction row, each file that quotes a count the correction changes** (RULE-2).
3. **Write hash and state receipts from Python, not through a redirect of `rtk proxy`** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time:** about 2 hours 20 minutes from the plan review's approval (21:06) to the execution review's approval (23:26), of which about 30 minutes was the host-load wait.
- **Tokens:**

  | Item | Tokens |
  |---|---|
  | Plan review, round 1 | 4,080,773 |
  | Execution review, round 1 | 8,778,484 |
  | Execution review, round 2 | 6,147,283 |

- **Adjusted estimate** for a small tooling fix with a live check: about 4M tokens for a plan review round and 6M to 9M for an execution round; about 1 hour of rows when the host is quiet.

---

## Next Session Design Rules

```
RULE-1: A plan step that writes a file lists, in its Boundary Inventory, a write or close error after the file is created, and an AC tests that the step leaves no partial file.
SOURCE: Session 95 execution review round 1, F1 (High): the reviewer injected ENOSPC after the CUT line, and capture exited 2 but left 23,154 of 36,533 bytes in OUT, which check accepted.
EXAMPLE: before, AC-6 covers overwrite, refusal and timeout; after, AC-6 adds "a write or close error removes the file it created" with a fault-injecting file object.
```

```
RULE-2: A correction (CVR) row that changes a count another closeout file quotes names each such file and who updates it.
SOURCE: Session 95 CVR round 1 raised the tests from 25 to 29 while current-focus.md's Session 95 entry still said 25 tests pass; the file was outside the CVR's scope and the coordinator changed it before round 2.
EXAMPLE: before, the CVR edits the script and the test file only; after, it also lists current-focus.md's test count, updated by the coordinator and recorded in the handoff.
```

```
RULE-3: A receipt that a later step parses (a hash, a tested_state) is written by Python, never by redirecting rtk proxy output into it.
SOURCE: Session 95 CVR: rtk proxy writes "[rtk] No hook installed" into redirected output, so a redirected hash receipt would hold a line edr-tests does not expect; the executor wrote cvr1-test-sha.txt from Python.
EXAMPLE: before, rtk proxy uv run python -c "print(sha)" > edr-test-sha.txt; after, the script writes the file itself in mode xb and the cell reads it back.
```

---

## Next Day Outline

1. **Next:** the 2026-11-18 grouping is done; Session 95 was its only session. The next step is a new triage or grouping pass for Mat over what the register still holds: the ten rows the grouping left out (§1) and D-1200. The prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, plus the rules Sessions 74 and 82 to 94 carried, all in the start prompt. `eval-describe.py` is how `describe` is captured from now on.
4. **Codex validation scope:** the next session's own loops.
5. **Time estimate:** set by the next triage.
6. **Still open for Mat:** D-1200 (the FFmpeg report), and the commit of Session 95 by the coordinator, with no push from the agent. H2-5 has the draft and the path list.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | A few hundred in the executor's transcript, rows 0 to H2-6; not counted exactly |
| Time to first green test | Row 2 Green at 21:37, one minute after the row 1 Red |
| Tests added | 29 plan-local pytest tests in `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py` (25 at row 1, 4 at the CVR). Python, UI and MCP suites unchanged |
| Codex findings | Plan review: R1 approved, 0 findings. Execution review: R1 changes required, 1 finding (F1, High, fixed); R2 approved, 0 new findings |
| Handoff Score (X/7) | 6/7. Every AC has evidence and the gate passed, but the execution review needed a correction round |
| Rule Adherence (%) | 90 (9 of 10 sampled rules followed) |
| Prompt→commit time | Planned, executed, approved and closed 2026-11-18; the coordinator commits without a push |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution, and the executor never dispatched or wrote a verdict |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. H2-5 is a draft and a path list only |
| Red before Green, by assertion | AGENTS.md §Testing | Yes. Row 1 and the CVR Red each read 0 problems in `red-check.py` |
| Never edit a test to pass (S3) | The plan's stop table | Yes. The test file's hash equals its last Red's in the gate |
| Records kept (`RECORDS_KEPT`) | The plan | Yes. The nine record files keep their row-0 hashes |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `current-focus.md` and `metrics.md` stay CRLF, every other scope file LF |
| An LF file is written as bytes and its CR count checked | Session 83 RULE-3 | Yes. The commit draft, the reflection and the new scripts read CR 0 |
| No model call, eval run or network use | The brief | Yes. The harness ran `describe` only, over scratch roots |
| Stop only processes this session launched | The brief | Yes. No process was stopped by this session |
| Run each Validation cell as written | The execution workflow | No. Row 0 ran twice after a formatting fix to a copied script, and gate run 1 stopped at host load; both disclosed |

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
  workflows: [execution_session]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
    - .agent/context/handoffs/TEMPLATE.md
    - docs/execution/reflections/2026-11-17-e2e-pointer-flakes-reflection.md
    - docs/execution/reflections/2026-11-17-mcp-audit-refresh-reflection.md
    - .agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-plan-critical-review.md
    - .agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-implementation-critical-review.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:never-edit-a-test-to-pass, P0:keep-line-endings, P1:red-before-green, P1:records-kept]
conflicts:
  - "The CVR's file scope left out current-focus.md, which quoted the test count the CVR changed; the coordinator updated it and the handoff records it as a coordinator edit."
note: "A raw-byte describe capture with Session 92's guard; one review finding on a failed write, fixed Red then Green."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "The handoff's CVR Departures sub-bullets repeat the Quality Gate and History rows."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 1
    execution: 2
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 0
      medium: 0
      low: 0
    - review: execution
      round: 1
      critical: 0
      high: 1
      medium: 0
      low: 0
    - review: execution
      round: 2
      critical: 0
      high: 0
      medium: 0
      low: 0
  churned_findings: 0
  finding_categories: {boundary_validation: 1}
  verdicts:
    changes_required: 1
    approved: 2
meu_work_classes: []
```

The review churn counts the ledger's recorded rounds in the session's two loops. The plan loop approved at round 1 with 0 findings (`usage` 4,080,773). The execution loop, `edr-execution-2026-11-18-eval-describe-raw-bytes`, used 2 of 6 rounds: round 1 found F1 (High, fixed by the CVR round 1 correction) and round 2 approved with no new findings (`usage` 8,778,484 and 6,147,283).
