---
date: "2026-11-18"
project: "2026-11-17-e2e-pointer-flakes"
meus: []
plan_source: "docs/execution/plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-18 Meta-Reflection

> **Date**: 2026-11-18. Planned on 2026-11-17; plan-reviewed, executed, reviewed and closed on 2026-11-18.
> **MEU(s) Completed**: none. Session 91 `e2e-pointer-flakes` is test-harness debt with no MEU (D-1132), the fifth and last session run of the 2026-11-17 value-triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` §3, row 91), run on `main` from `9fce270` under D-1142's order (74, 92, 93, 94, then 91).
>
> - **The shield** (`POINTER_SHIELD`, `SHIELD_OPT_OUT`; D-1149). Every E2E launch of the built app sets `setIgnoreMouseEvents(true)` on each window from the main-process diagnostics, so the real mouse can no longer reach a test window; Playwright's CDP input still arrives (AC-9), and `pointerShield: false` opts out (AC-10).
> - **The shared helpers and a settled target** (`POINTER_HELPERS_SHARED`, `SETTLE`, `SETTLED_BOX`, `POINTER_ON`; D-1147, D-1148). The five download drag helpers live once in `ui/tests/e2e/pointer-settle.ts`; a read is settled after two equal reads one frame apart, and `pointerOn` also hit-tests the point.
> - **The waits in front of unchanged expectations** (`DRAG_DRIVER_SHARED`, `SETTLED_ZOOM`, `GRAB_COMMITTED`, `POINTER_SITES`; D-1151). The convert drag uses the shared driver, the capture origin reads settle, the arrow grab waits for x2 to move, and the capture hovers hit-test first. No assertion line, timeout, retry or Playwright setting changed.
> - **The diagnostics** (`DIAG_DIR`, `PHASE_LINES`, `MAIN_DIAG`; D-1150). Each launch writes its launch, evaluate and close phases and a main-process event log under the run's own folder.
> - **The proof** (D-1145, D-1146, D-1153). Row 3's rerun reproduced 4 watched failures at 18 busy children (median load 98.0 %); row 8 passed three full runs of 232 at median load 95.4 % and the watched tests ten times, 110 of 110, at 93.9 %.
> - **The records.** `DOWNLOAD-QUEUE-DRAG-OVER-MISS` and `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` are `resolved`; the launch hang was not reproduced, so `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` stays `open` with a note; grouping row 91 is `executed`.
>
> **Plan Source**: `docs/execution/plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review**, which needed three rounds. Each blocking finding was a way the hang excuse could certify an unregistered hang:
     - Round 1's F1 (High, blocking): a split signature held only cause, phase and issue, so it excused any unwatched test with that phase.
     - Round 1's F2 (High, blocking): the close guard measured from the first launch, not the test's own clock, so a body timeout could pass as a close hang.
     - Round 2's F3 (High, blocking): an S9 rerun of row 8 reused the label's diagnostic folder, so a stale clean close from an earlier attempt could excuse a current body timeout. The fix gave each invocation its own receipts and diagnostic folders.
     - Round 3 approved.
   - **F2 held by another program.** From row 3 to row 7 another program held F2 (`RegisterHotKey` last error 1409), so AC-81.11's hotkey-in-use fixture failed every repeat before it reached its banner. Rows 4 to 7 went on as measurements (D-1152); the run then held about 90 minutes, from probe 6 at 13:53 to probe 7 at 15:24, until Mat closed the holder. Row 3 was rerun as a new invocation (D-1153) before row 8 (RULE-1).
   - The rows themselves, from the receipts' mtimes:

     | Step | Time |
     |---|---|
     | Row 0 baseline | 13:04 |
     | Row 1 Red (unit and E2E) | 13:10 |
     | Row 2 Green | 13:18 |
     | Row 3, first run (F2 held) | 13:22 to 13:33 |
     | Rows 4 to 7 (F2 held) | 13:41 to 13:53 |
     | F2 free (probe 7) | 15:24 |
     | Row 3 rerun | 15:25 to 15:43 |
     | Row 8 acceptance | 15:43 to 16:18 |
     | Row 9 registers | 16:19 |
     | H1-2 gate | 16:20 to 16:28 |

2. **What instructions were ambiguous?**
   - **A fixture that needs a free OS resource.** The plan named AC-81.11 among the watched tests but had no step for F2 being held by another program, so its failures entered row 3's burn level. D-1152 and D-1153 settled it (RULE-1).
   - **H2-6's start string.** The cell requires the prompt to start `Start Session 92`, written under D-1133's order. Under D-1142 Session 92 was already executed, so the coordinator's brief set the start string to `Grouping done after Session 91` (RULE-2; the same gap Session 94 reported as its RULE-1).

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as in Sessions 74 and 88 to 94).

4. **What was missing?**
   - **A probe of the hotkeys a fixture needs, before the runs** (RULE-1).
   - **A list of the scanner's banned tokens beside the diagnostic fields.** `assert-check.py` counts the text `repeatEach`, and the plan's own `PHASE_LINES` carries the repeat index from `testInfo.repeatEachIndex`. Row 2's first run failed `NO_NEW_WAIT_KNOBS` on that literal (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Ran each Validation cell from a `.ps1` file**, the cell copied verbatim after an environment header (`UV_NO_SYNC`, `UV_OFFLINE`, scratch `TMP` and `TEMP`, `ELECTRON_RUN_AS_NODE` unset), and marked rows with a script that keeps `task.md` LF.
   - **Made every hand edit with a byte-level Python script** that asserted each anchor once and kept the file's line endings: the register, the grouping row and the CRLF current focus. `eol-check` read 0 problems on 34 scope paths in the gate.
   - **For the row 3 rerun**, saved the fixed files with their hashes, put the three specs back from the row-0 copies with the shield default off, and restored and hash-checked all four after (D-1153).
   - **Probed F2** before each long run once it was free (probes 7 and 8), and stopped only processes this session launched, by recorded id and creation time.
   - **Two self-inflicted slips.** Row 2's first run failed S7 on the `repeatEach` literal, which I had written; I took it out and joined the key, with no checker edit. H1-6's first run refused the handoff because AC-87 and AC-143 never appeared in it; I added the pinned tests' ids in one line beside the cross-reference rows.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The Red** (row 1): the five unit tests failed on the missing modules, and AC-4, AC-8 and AC-9 failed by assertion (`Expected: 32`, `Received: 0` for the shield's style bit); AC-10 passed as a guard.
   - **The reproduction** (row 3 rerun): on the unfixed specs at 18 busy children, 4 failures in 110 watched runs, at `download-queue.test.ts:1319` and `:1348` and `capture-inbox.test.ts:1601` twice. After the fixes, row 8's three full runs and its 110 watched runs held none.
   - **The plan review's F1 to F3** each found, with a fake-`Popen` probe, a path where the hang excuse would certify an unregistered hang.
   - **`assert-check.py`** caught the `repeatEach` literal at row 2.

7. **Which tests were trivially obvious?**
   - AC-6 and AC-7 are static source checks, as the plan specified; the real proof of those edits is the full and watched runs.

8. **Did pyright/ruff catch anything meaningful?**
   - No. No product Python file changed; ruff passed on the plan folder's six scripts, and ESLint and `tsc` were clean at each row and in the gate.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The contract names gave the tests, the handoff and both reviews one vocabulary; the execution review approved at round 1 with 0 findings and used the same names.

10. **Was the handoff template right-sized?**
    - Mostly. The Test pins cross-reference rows plus the anchor-move list carry the same line numbers twice (slim_candidate below).

11. **How many tool calls did this session take?**
    - Not counted exactly. The executor's transcript ran to a few hundred calls, rows 0 to H2-6, across context compactions. Planning, the review dispatches and H1-7 to H1-7b ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-6 to one executor subagent (Claude Code, Claude Opus 5.5). It ran the review dispatches and H1-7 to H1-7b itself.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. No delegated result needed rework after review.

### Decisions Log

- Prove the fix with three full runs plus the watched tests ten times at the burn level, since row 3's watched runs failed — [D-1145](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)
- Reproduce first on the unfixed specs at 18 busy children with a churn child; escalate to 24 only on zero failures — [D-1146](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)
- Keep the drag and window-settle helpers once, in `ui/tests/e2e/pointer-settle.ts` — [D-1147](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)
- A settled target is two equal reads one frame apart and a hit-test; the grab waits for x2 to move — [D-1148](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)
- Shield every E2E launch's windows from the real mouse by default, with an opt-out — [D-1149](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)
- Classify each launch hang per block from its phase lines and change the register per block — [D-1150](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)
- No existing assertion line changes to make a spec steady — [D-1151](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)
- Go on with rows 4 to 7 as measurements while F2 was held, AC-81.11 named F2-held in each receipt (execution) — [D-1152](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)
- Rerun row 3 as a new invocation once F2 was free and take row 8's level from the rerun, keeping the first run as skewed evidence (execution) — [D-1153](../plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md)

**Read from their own logs, not listed:**
- D-1126 is on the issues.
- D-1131 to D-1134 are grouping §8.
- D-1154 is unused.

**The `decision_sources` probe was re-run at H2-2** (`epf-decision-probe.txt`), with the plan, the handoff, the grouping and the register with the three issues:
- it reads D-1126 (triage), D-1131 to D-1134 (grouping), D-1145 to D-1151 (planning) and D-1152 and D-1153 (execution);
- `expected ids missing: []`, and D-1152 and D-1153 are the only ids beyond the plan-time set, as expected;
- `chosen starting with Pending: []`;
- `brace slots left in the decision YAML: []`;
- grouping §8 alone still reads D-1131 to D-1134, as at plan time.

---

## Pattern Extraction

### Patterns to KEEP
1. **Reproduce on the unfixed tree under the acceptance load before any fix.** Row 3's rerun gave a real failure rate (4 in 110) on the same specs and level that row 8 then passed, so the acceptance proves a change, not a quiet host.
2. **Give each invocation its own receipts and diagnostic folders.** The plan review's F3 showed why: a reused folder lets a stale clean close excuse a current hang.
3. **Swap back by hash.** The row 3 rerun's temporary byte swaps were saved, restored and checked file by file, and the reviewer found the four files byte-identical.

### Patterns to DROP
1. **Citing every moved pin twice.** The anchor-move list and the cross-reference rows hold the same lines; one table could carry both the row-0 and the current line.

### Patterns to ADD
1. **Probe the OS resources a fixture needs before the measurement rows** (RULE-1).
2. **Read the next-session start string from the queue receipt** (RULE-2).
3. **Check a plan's own diagnostic field names against the scanner's banned tokens** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time** (local time, from the receipts' mtimes):

  | Step | Time |
  |---|---|
  | Plan review round 1, changes required (F1, F2) | 07:54 |
  | Plan review round 2, changes required (F3) | 08:15 |
  | Plan review round 3, approved | 09:00 |
  | Rows 0 to 7 | 13:04 to 13:53 |
  | Held for F2 | 13:53 to 15:24 |
  | Row 3 rerun, rows 8 and 9 | 15:25 to 16:19 |
  | The H1-2 gate, first run, at a 13.4 % host load | 16:20 to 16:28 |
  | Execution review approved at round 1 (`epf-exec-console-r1.txt`) | 16:51 |

- **Tokens:**

  | Item | Tokens |
  |---|---|
  | Plan review, round 1 | 13,106,526 |
  | Plan review, round 2 | 7,445,977 |
  | Plan review, round 3 | 7,980,215 |
  | Execution review, round 1 | 17,465,333 |

- **Adjusted estimate** for a load-flake session with a reproduction and a busy-host acceptance:
  - about 8M to 13M tokens for a plan review round, and 17M for the execution review;
  - about 3 hours of rows when nothing holds a resource: about 20 minutes for each reproduction, 35 minutes for the acceptance, and 8 minutes for the gate.

---

## Next Session Design Rules

```
RULE-1: A plan whose watched or acceptance tests use an OS-wide resource (a global hotkey, a port, the clipboard) probes that resource free in row 0 and again before each measurement row, and names the stop when another program holds it.
SOURCE: Session 91 D-1152 and D-1153: F2 was held by another program from row 3 to row 7, so AC-81.11 failed every repeat and its failures entered row 3's burn level; row 3 had to be rerun after Mat closed the holder.
EXAMPLE: before, row 3 runs the watched tests with no hotkey check; after, row 0 and rows 3 and 8 each write an F2 probe receipt and stop on "F2 held by another process".
```

```
RULE-2: Session 94 RULE-1 again: the next-session row reads its start string from the queue receipt, not from a session id written into the plan at plan time.
SOURCE: Session 91 H2-6: the cell requires startswith('Start Session 92'), written under D-1133, while D-1142 ran Session 92 before 91 and the grouping is done; the executor ran a copy with only that string changed to 'Grouping done after Session 91', at the coordinator's direction.
EXAMPLE: before, pt.startswith('Start Session 92'); after, the cell checks the start string that epf-close-queue.txt names.
```

```
RULE-3: When a plan adds a diagnostic field, check its source spelling against the plan's own text scanners (assert-check BANNED tokens) at plan time, and name the allowed spelling in the plan.
SOURCE: Session 91 row 2: PHASE_LINES reads testInfo.repeatEachIndex, and assert-check.py counts 'repeatEach' as a wait knob; the first run failed NO_NEW_WAIT_KNOBS 0 -> 1, and the key had to be joined from parts (electron-app.ts:49), which the execution review accepted in Q7.
EXAMPLE: before, the plan names the repeat field with no spelling; after, the plan says "the repeat index is read through a joined key, because assert-check counts the literal".
```

---

## Next Day Outline

1. **Next:** the 2026-11-17 grouping is done; Session 91 was its last session. The next step is a new triage or grouping pass for Mat over what the register still holds, including the nine rows the grouping left out (§1) and the open launch hang. The prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, plus the rules Sessions 92 to 94 carried, all in the start prompt. New E2E specs that launch through `launchElectron` get the shield by default.
4. **Codex validation scope:** the next session's own loops.
5. **Time estimate:** set by the next triage.
6. **Still open for Mat:** the commit of Session 91 by the coordinator, with no push from the agent. H2-5 has the draft and the path list.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | A few hundred in the executor's transcript, rows 0 to H2-6; not counted exactly |
| Time to first green test | Row 2 Green at 13:18, eight minutes after the row 1 Red |
| Tests added | UI unit 1628 to 1633 (+5) in 144 to 145 files: `ui/tests/unit/e2e-pointer.test.ts`. Electron 228 to 232 (+4): `ui/tests/e2e/e2e-diag.test.ts` |
| Codex findings | Plan review: R1 changes required, 2 findings (F1, F2, both High, fixed); R2 changes required, 1 finding (F3, High, fixed); R3 approved. Execution review: R1 approved, 0 findings |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the gate passed on its first run, and the execution review approved at round 1 with 0 findings |
| Rule Adherence (%) | 90 (9 of 10 sampled rules followed) |
| Prompt→commit time | Planned 2026-11-17; executed, approved and closed 2026-11-18; the coordinator commits without a push |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution, and the executor never dispatched or wrote a verdict |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. H2-5 is a draft and a path list only |
| Red before Green, by assertion | AGENTS.md §Testing | Yes. The Red checks read 5 and 3 required tests, 0 problems |
| No assertion line changes (S3, D-1151) | The plan's stop table | Yes. `assert-check.py` passed at rows 4 to 8 and in the gate |
| Undo the edit that broke a check; never edit the checker (S7) | The plan's stop table | Yes. The `repeatEach` literal was taken out; `assert-check.py` is unchanged |
| Reproduce before the fix, at the acceptance load | D-1146 | Yes. Row 3 and its rerun ran on the unfixed specs |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `eol-check: 34 scope path(s), 0 problem(s)` |
| Stop only processes this session launched, by id and creation time | The brief | Yes. Every receipt reads `busy children left: 0`; nothing else was stopped |
| Run each Validation cell as written | The execution workflow | No. Row 8 read `epf-burn-level-b.txt` under D-1153, and H2-6's start string was changed at the coordinator's direction; both disclosed |
| Never run the clipboard specs | The brief | Yes. `capture-filmstrip-actions.test.ts` and `capture-import.test.ts` never ran |

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
    - docs/execution/reflections/2026-11-17-ui-small-fixes-reflection.md
    - .agent/context/handoffs/2026-11-17-e2e-pointer-flakes-plan-critical-review.md
    - .agent/context/handoffs/2026-11-17-e2e-pointer-flakes-implementation-critical-review.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:never-edit-a-test-to-pass, P0:keep-line-endings, P1:red-before-green, P1:reproduce-before-fix]
conflicts:
  - "H2-6's check requires the prompt to start 'Start Session 92' (D-1133's order), while under D-1142 Session 92 was already executed and the grouping is done; the brief set 'Grouping done after Session 91'."
  - "assert-check.py counts the text 'repeatEach' as a wait knob, while the plan's PHASE_LINES carries the running repeat index; the key was joined from parts (S7) and the execution review accepted it."
note: "Three load flakes reproduced at 18 busy children, then fixed with a pointer shield and settle waits; acceptance and execution review clean."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "The handoff's anchor-move list repeats the cross-reference rows' line numbers."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 3
    execution: 1
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 2
      medium: 0
      low: 0
    - review: plan
      round: 2
      critical: 0
      high: 1
      medium: 0
      low: 0
    - review: plan
      round: 3
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
  finding_categories: {boundary_validation: 3}
  verdicts:
    changes_required: 2
    approved: 2
meu_work_classes: []
```

The review churn counts the ledger's recorded rounds in the session's two loops, `epf-plan-2026-11-17-e2e-pointer-flakes` and `epf-execution-2026-11-17-e2e-pointer-flakes`. The plan loop approved at round 3 after F1 and F2 (round 1) and F3 (round 2) (`usage` 13,106,526, 7,445,977 and 7,980,215); the execution loop approved at round 1 with 0 findings (`usage` 17,465,333).
