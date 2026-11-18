---
date: "2026-11-18"
project: "2026-11-17-tts-fp16-guard-ship"
meus: ["MEU-144"]
plan_source: "docs/execution/plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-18 Meta-Reflection

> **Date**: 2026-11-18. Planned on 2026-11-17; plan-reviewed, executed, reviewed and closed on 2026-11-18.
> **MEU(s) Completed**: MEU-144 `svc-tts-fp16-guard-ship` (P2, matrix row 3.21), registered by this session under D-1135 A. Session 74 `tts-fp16-guard-ship` is the first session of the 2026-11-17 value-triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` §3, row 74). It ran on `main` from `174bafa`.
>
> - **The guard, in memory** (`TTS-ONNX-FP16-NONFINITE-AUDIO`, `resolved`; D-1136 A, Mat). When ONNX FP16 Kokoro loads, `phase_guard.guarded_model` reads the user's downloaded file, checks Session 73's size and source hash, splices `IsNaN` and `Where` after `/decoder/decoder/generator/Div` with the standard library, checks the result against Session 73's guarded hash and hands those bytes to both ONNX Runtime sessions (`GUARD_IN_MEMORY`, `GUARD_GATE`, `GUARD_APPLIED`, `BOTH_SESSIONS`, `ONE_JOIN`). Any other file loads as shipped; a splice that refuses or a wrong result loads the file as shipped and logs one warning with no path (`GUARD_REFUSE`). Nothing in the models folder is written (`NO_FILE_WRITE`), no package is added, and FP16 stays never preselected (`PRESELECT_KEPT`).
> - **The proof.** The pre-change packaged build fails the same 12 of 149 sentence jobs as Sessions 52 and 73, with its 137 Done WAVs equal by job to Session 73's control (`BUILD_SAME`); the post-change build passes 149 of 149 with every WAV equal by job to Session 73's guarded run (`WAV_BY_JOB`), and INT8 passes 149 of 149 with every WAV equal to Session 73's INT8 run. On the real file the splice gives Session 73's exact bytes with a 329 MB peak against the 400 MB bar (`GUARD_BYTES_EQUAL`).
>
> **Plan Source**: `docs/execution/plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The handoff**, as in Sessions 82, 88, 89 and 90. It was built by a script (`build-handoff.py`) from a draft and the receipts, which filled the evidence blocks, the gate table and the host load and refused a home path or a failing step. That script had to be fixed twice: the gate's step count first matched the skipped-step lines (23, then 24, against 22 run steps), and a quoted receipt line carried an em dash read in the wrong code page ("ΓÇö").
   - **Row 0.** Its first run failed at the base ruff step on a read-only pin file that is not ruff-formatted at `174bafa` (D-1141). The rerun passed.
   - The product rows themselves were quick: from the receipts' mtimes, the control build at 07:45, Red at 07:50, Green at 07:51, the guarded smoke at 07:55, the INT8 smoke at 08:00 and the gate at 08:06.

2. **What instructions were ambiguous?**
   - **H2-6's fixed next session.** The plan wrote the next session into H2-6's check (`Start Session 91` with `e2e-pointer-flakes`). After the execution review the coordinator relayed that Session 91's plan review had stopped on a review-ledger mechanism that needs Mat, and set the queue to 92, 93, 94 and then 91. The check could not pass on the new order, so D-1142 amended the row (RULE-1).
   - **"The backend is never killed."** The plan said it; the smoke's `Backend.stop()` terminates its own child, with a kill after 20 s. The session prompt allows this, and the handoff discloses it.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as in Sessions 81, 82, 88, 89 and 90).

4. **What was missing?**
   - **A plan-time format check on read-only files.** The plan bound four pin files by hash and ran ruff on them at row 0, but nobody had run `ruff format --check` on them at plan time. One was not formatted at base, so row 0 failed on a file the session may not change (D-1141, RULE-3).
   - **A rule for the sibling sessions' files.** Sessions 91 to 94 were planned while this session ran, and their plan folders and plan reviews appeared in the tree. The plan's scope and identity checks would have bound them; D-1140 treated them as foreign.
   - **Text encoding for quoted receipts.** One receipt held a byte sequence that decoded as "ΓÇö" when quoted into the handoff; the builder now replaces it, and every new receipt is written under `PYTHONIOENCODING=utf-8`.

5. **What did you do that wasn't in the prompt?**
   - **Ran each cell from a script and marked rows by script** (`mkrow.py`, `mark.py`). Each Validation cell ran verbatim from a `.ps1` file with the environment header, and `task.md` stayed LF.
   - **Built the handoff from receipts by script**, which checks that every step it cites exited 0 and that no home path is in it.
   - **Added `guard-check.py --selftest`** and ran it before first use, and kept every superseded receipt (`ff-run1-*` for row 0's first run).
   - **Ran a host-load probe before H1-2**, outside the cell (`ff-host-load-h12pre.txt`: 33.4 %).
   - **Disclosed D-1142 in the handoff** after the execution review, and reran H1-6, H1-6a and H1-6b on the rebuilt handoff.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The packaged control smoke** (row 3) showed the user's defect on the pre-change build: the same 12 of 149 jobs fail with "generated audio must be finite".
   - **The 25 new tests** failed at Red by assertion (`ff-red.txt`: `25 failed`) and passed at Green. Real ONNX Runtime on a 375-byte synthetic FP16 graph gives NaN for 0/0 before the splice and `+0` after, with 1/2 bit-identical. The refusal cases pin each `SpliceError` text.
   - **`guard-check.py` on the real file** (row 6) is the one check that ties the splice to Session 73's bytes: the result hash `9037c82b…` and the 400 MB memory bar.

7. **Which tests were trivially obvious?**
   - The pass-through cases (another variant id, another size) are short by design: they guard that a file outside the gate is never read.

8. **Did pyright/ruff catch anything meaningful?**
   - No product issue. ruff found the base format drift in a pin file (D-1141), which is a base-state fact, not a defect in this session's code. pyright was clean on `phase_guard.py`, `adapter.py` and the tests.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The contract names (`GUARD_IN_MEMORY` to `WAV_BY_JOB`) gave the tests, the handoff and both reviews one vocabulary. Both reviews approved at round 1 with 0 findings.

10. **Was the handoff template right-sized?**
    - Yes for one MEU with packaged proofs. The Departures section carried most of the session's judgment calls (D-1140 to D-1142, the plan's sha moves, the stale citations), and it is the section the reviewer needs.

11. **How many tool calls did this session take?**
    - Not counted exactly. The executor's transcript ran to a few hundred calls, rows 0 to H2-6, across context compactions. Planning, both review dispatches and H1-7 to H1-7b ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-6 to one executor subagent (Claude Code, Claude Opus 5.5). It ran the plan and execution review dispatches and H1-7 to H1-7b itself, and relayed the queue change behind D-1142.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. No delegated result needed rework after the review.
    - Codex reviewed the plan and the execution as the independent reviewer. That is not delegation.

### Decisions Log

- The guard applies only to `kokoro-onnx-fp16` at Session 73's size and hashes; anything else loads as shipped, and a failed splice logs one warning with no path — [D-1137](../plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md)
- Tests run on a 375-byte synthetic FP16 graph through real ONNX Runtime, and the real file is checked by script on a `C:/Temp` copy — [D-1138](../plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md)
- The 03 section, matrix row, MEU entry, Delivered note and issue resolution are written by plan scripts bound to their row-0 hashes — [D-1139](../plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md)
- The sibling sessions' plan folders and plan reviews are foreign: recorded, never read or bound, left out of the scope checks and the commit paths — [D-1140](../plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md)
- A pin file's base format drift is recorded as base, with `adapter.py` still fatal on both ruff checks — [D-1141](../plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md)
- The next-session prompt starts Session 92, with Session 91 deferred until Mat continues its plan-review loop — [D-1142](../plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md)

D-1135 and D-1136 are Mat's rulings, D-239 and D-801 are on the issue, D-797 is Session 73's, and D-1131 to D-1134 are grouping §8; they are read from their own logs and are not listed. D-1143 and D-1144 were not used. The `decision_sources` probe was re-run at H2-2 (`ff-decision-probe.txt`):

- with the plan, the grouping and the register it reads D-1131 to D-1134 (grouping), D-1135 to D-1139 (planning), D-1140 to D-1142 (execution) and D-801;
- with Session 73's plan added it also reads D-797;
- no `chosen` starts with "Pending", and no brace slot is left outside the quoted `SpliceError` texts.

Grouping §8 holds no new row since plan time.

---

## Pattern Extraction

### Patterns to KEEP
1. **Measure the user's failure on the shipped build before the fix.** Row 3's control smoke reproduced the 12 of 149 failures on a pre-change packaged build, so the post-change 149 of 149 is a comparison, not a claim.
2. **Bind the result to the bytes a human approved.** The guard returns the spliced graph only when it hashes to the graph Mat listened to in Session 73, and every packaged WAV is compared job by job with that run.
3. **Build the handoff from receipts by script.** The builder refuses a failing step or a home path, so the handoff's numbers are the receipts' numbers.

### Patterns to DROP
1. **A next-session name fixed in a closeout check.** The queue can change after the plan review (here because of another session's stop); a check that hardcodes the next session needs an execution decision to move.

### Patterns to ADD
1. **H2-6's check reads the next runnable session from the queue receipt** (RULE-1).
2. **Receipts quoted into a handoff are written and read as UTF-8** (RULE-2).
3. **A plan that binds read-only files runs the gate's format and lint steps on them at plan time** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time** (local time, from the receipts' mtimes):
  - The plan review approved at round 1 (canonical copy 2026-11-18 07:13).
  - Row 0's baseline (its rerun) ended at 07:43.
  - Rows 2 and 3 (control build and smoke) ran from 07:45 to 07:48; Red at 07:50 and Green at 07:51.
  - Rows 7 and 8 (guarded build and smoke, INT8 smoke) ran from 07:52 to 08:00.
  - The H1-2 gate passed on its first run at 08:06, at a 29 % host load.
  - The execution review approved at round 1 at 08:21.
- **Tokens:** plan review 8,363,442 (round 1); execution review 9,551,781 (round 1).
- **Adjusted estimate** for a one-MEU session with a packaged before-and-after proof: about 8 to 10M tokens per review round; about 5 minutes per packaged build and sentence smoke on a quiet host; about 5 minutes for the full Python suite.

---

## Next Session Design Rules

```
RULE-1: A plan's next-session row checks the prompt against the next runnable session named in its own queue receipt, not against a session id written into the plan, and says what to do when the grouping's queue has been reordered.
SOURCE: Session 74 H2-6: the check required 'Start Session 91'; after the execution review Session 91's plan review stopped on a ledger mechanism that needs Mat and the queue became 92, 93, 94, 91, so D-1142 had to amend the row and the plan after review.
EXAMPLE: before, pt.startswith('Start Session 91'); after, pt.startswith('Start Session ' + next_id) where next_id is read from ff-close-queue.txt, with a deferred session named in the prompt.
```

```
RULE-2: Every receipt that a handoff quotes is written under PYTHONIOENCODING=utf-8 and read as UTF-8, and the handoff builder refuses mojibake sequences (for example "ΓÇ") rather than passing them through.
SOURCE: Session 74 H1-6: a state-render line quoted into the handoff came through as "ΓÇö" for an em dash; the builder now replaces it, and the handoff had to be rebuilt and H1-6 to H1-6b rerun.
EXAMPLE: before, the builder copies a receipt line as read; after, it decodes as UTF-8 and stops on a known mojibake sequence.
```

```
RULE-3: A plan that binds files read-only and runs ruff on them at baseline runs the same ruff format --check and ruff check on those files at plan time, and records any base drift in the plan before row 0.
SOURCE: Session 74 row 0 (D-1141): tests/integration/test_tts_models.py, a read-only pin file, is not ruff-formatted at 174bafa (as 25 other files are not), so the first baseline run failed on a file the session may not change.
EXAMPLE: before, the plan names the pin files and row 0 finds the drift; after, the plan says "test_tts_models.py format drift at base: recorded, not fatal; adapter.py fatal on both checks".
```

---

## Next Day Outline

1. **Next:** Session 92 `mcp-audit-refresh` (`docs/execution/plans/2026-11-17-mcp-audit-refresh/`), then Sessions 93 and 94; Session 91 `e2e-pointer-flakes` runs last, deferred until Mat continues its plan-review loop (D-1142). The prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, plus Session 90's, 89's, 88's, 83's and 82's rules, carried in the start prompt. Session 93 owns `tests/integration/` and will find `test_tts_phase_guard_load.py` there. Session 94 now runs before Session 91, against grouping §2's soft order (the shared `ui/tests/e2e/`), so its gate may meet the pointer flakes.
4. **Codex validation scope:** each session's own plan and execution loops.
5. **Time estimate:** set by the next plan.
6. **Still open for Mat:**
   - The commit of Session 74 by the coordinator, with no push from the agent (H2-5 has the draft and the path list).
   - Session 91's plan-review loop, stopped on a review-ledger mechanism.
   - Redacting the raw home prefix in the 24 tracked files and the two `known-issues.yaml` hits, as its own docs-only change.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | A few hundred in the executor's transcript, rows 0 to H2-6; not counted exactly |
| Time to first green test | Green at 07:51, one minute after Red |
| Tests added | 25 Python tests (3112 in the gate, against 3087 at row 0): 21 in `tests/unit/test_tts_phase_guard.py` and 4 in `tests/integration/test_tts_phase_guard_load.py`, with the synthetic graph builder `tests/tts_onnx_synthetic.py` |
| Codex findings | Plan review: R1 approved, 0 findings. Execution review: R1 approved, 0 findings |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the gate passed on its first run, and both reviews approved at round 1 with 0 findings |
| Rule Adherence (%) | 90 (9 of 10 sampled rules followed) |
| Prompt→commit time | Planned 2026-11-17; executed, approved and closed 2026-11-18; the coordinator commits without a push |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution; the executor never dispatched or wrote a verdict |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. H2-5 is a draft and a path list only |
| Red before Green | AGENTS.md §Testing | Yes. Row 4's 25 tests failed by assertion before Green |
| Nothing in the user's models folder is written; models only from Session 73's copies | The executor brief; `NO_FILE_WRITE` | Yes. The models copy's hashes never changed, and no download ran |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `eol-check: 18 scope path(s), 0 problem(s)` |
| No raw home path in tracked files | The executor brief; Session 83 | Yes. The gate's `home-path` step passed |
| Change the registers only through `tools/meu_status.py`, `tools/issue_triage*` and the plan scripts | The executor brief | Yes. Rows 1 and 9, H2-2 |
| Stop only this session's processes, by recorded id and creation time | The executor brief; S13 | Yes. Each smoke stopped only its own backend child; other sessions' processes were left running |
| Never open another session's plan folder | The executor brief; D-1140 | Yes. The sibling folders were recorded by path only; D-1142 took Session 91's stop from the coordinator's relay |
| A plan's closeout checks hold without amendment after the plan review | The plan-review approval of the plan's text | No. H2-6's check named Session 91 and had to be amended after the execution review (D-1142, RULE-1) |

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
    - docs/execution/reflections/2026-11-17-test-run-reliability-reflection.md
    - docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md
    - .agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-plan-critical-review.md
    - .agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-implementation-critical-review.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:keep-line-endings, P0:never-write-user-models, P1:red-before-green, P1:never-touch-sibling-sessions]
conflicts:
  - "H2-6's check fixed Session 91 as next; the coordinator's relayed queue (92, 93, 94, 91) superseded it; resolved by D-1142."
  - "Row 0 ran ruff on read-only pin files that the session may not change; one was unformatted at base; resolved by D-1141."
note: "One MEU with packaged before-and-after proofs; first-run gate and round-1 approvals on both loops."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "A next-session id fixed in H2-6's check duplicates the queue receipt it already reads."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 1
    execution: 1
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
      high: 0
      medium: 0
      low: 0
  churned_findings: 0
  finding_categories: {}
  verdicts:
    approved: 2
meu_work_classes: [correctness]
```

The review churn counts the ledger's recorded rounds in the session's two loops, `ff-plan-2026-11-17-tts-fp16-guard-ship` and `ff-execution-2026-11-17-tts-fp16-guard-ship`. Both approved at round 1 with 0 findings (`usage=8,363,442` and `usage=9,551,781`).
