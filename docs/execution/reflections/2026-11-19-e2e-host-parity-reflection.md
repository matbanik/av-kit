---
date: "2026-11-19"
project: "2026-11-19-e2e-host-parity"
meus: ["MEU-161"]
plan_source: "docs/execution/plans/2026-11-19-e2e-host-parity/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-19 Meta-Reflection

> **Date**: 2026-11-19. Planned, plan-reviewed, executed, reviewed and closed on 2026-11-19.
> **MEU(s) Completed**: MEU-161 `capture-text-plate-metrics` (phase 9, P2, matrix 9.46), now `approved`. Session 97 `e2e-host-parity` is the second and last session of the 2026-11-18 E2E-host grouping (`.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md` §3, row 97), run on `main` from `2c41c70`.
>
> - **The text plate** (`PREVIEW_FOLLOWS_BAKE`, `PLATE_UNITS`; D-1242, D-1243). `textBackgroundBox` now measures text with a Segoe UI glyph and kerning table in font units, FreeType's 26.6 rounding and Pillow's basic-layout kerning, and returns the rectangle the bake paints (`r - l + 1`). The preview follows the bake; saved images do not change. A Pillow fixture of 2,488 painted boxes pins it, and the measured residual (1,702 of 2,448 breadth cases exact, 5 over 1 px, worst 2) is held to fixed limits and registered as `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` (low, D-1244).
> - **The fidelity frame** (`FIDELITY_FRAME`; D-1245). The three fidelity specs launch at a device scale of 1 on every host, so the dev PC, at a scale of 2, measures what the second Windows host measures.
> - **The hover spec** (`HOVER_CAPABLE`; D-1246). AC-126.8 (an earlier MEU's spec id, not this plan's) launches with a Blink setting that states a mouse-capable device and checks `(hover: hover)` before it hovers, because the second host has no pointing device.
> - **The known list** (`KNOWN_EMPTY`; D-1253). `tools/e2e_host/known-failures.json` holds no `known` entry; the two clipboard `skip` entries stay.
> - **The proof.** Two full runs on the second host through `tools/e2e_remote.py run` on no-ref snapshots of the tree (`SNAPSHOT_NO_REF`, D-1247): run 10 (`ed48964`, 232 of 232, the four former known tests in `known_now_passing`) and run 10b (`484d4ab`, the final tree, 232 of 232, gaps 0). The final gate passed all 31 steps.
> - **The records.** `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` and `E2E-HOVER-NO-POINTER-DEVICE` are `resolved`; grouping row 97 is `executed`; the grouping is done.
>
> **Plan Source**: `docs/execution/plans/2026-11-19-e2e-host-parity/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Two failed gates.** The H1-2 gate is fail-fast and runs about 16 minutes when it passes. The first run stopped at ui-tests: the repo's standards sweeps AC-44.13 and AC-43.13 (earlier MEUs' spec ids) refused two skip tokens in the new Session 97 block of `e2e-harness.test.ts` (D-1257). The second stopped at py-tests: `test_ac_11_known_tracked_list` in `tests/tooling/test_e2e_remote.py` pinned the four known entries that row 9 removed (D-1259). The third passed.
   - **A second run on the second host.** D-1257 changed a snapshot file, so row 10 ran again (S13) on a new snapshot, about 21 more minutes. Its summarize against the row-0 known list then exited 32 (`known-failures-stale`), because row 11 had already resolved the issues that list names (D-1258).
   - The rows, from the receipts' mtimes (2026-11-19):

     | Step | Time |
     |---|---|
     | Plan review round 1, changes required | 07:51 to 08:02 |
     | Plan review round 2, approved | 08:12 to 08:20 |
     | Row 0 baseline | 08:36 |
     | Row 1 diagnosis | 08:40 |
     | Rows 3 to 6 (Reds, hover fix, frame) | 08:42 to 08:48 |
     | Row 7 Green | 08:51 to 08:54 |
     | Row 10, run 1 on the second host (`ed48964`) | to 09:19 |
     | H1-2 gate 1, failed at ui-tests; D-1257 | 09:24 |
     | Row 10b, run 2 on the second host (`484d4ab`); D-1258 | to 09:54 |
     | H1-2 gate 2, failed at py-tests; D-1259 | 09:56 |
     | H1-2 gate 3, passed | 10:04 to 10:20 |
     | Execution review round 1, approved | 10:25 to 10:38 |

2. **What instructions were ambiguous?**
   - **Row 12's hub audit** asked `docs/BUILD_PLAN.md` to name the slug, which `meu_status.py render` never writes there. D-1256 checks what the generator writes.
   - **Which receipt names H1-7a and H1-7b use.** The task cells name `ehp-review-state.json` and `ehp-exec-review.txt`; the coordinator, who runs those rows, wrote `review-state.json` and `exec-review.txt`, as in Session 96. The handoff's Codex Validation Report names both.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as in Sessions 74 and 88 to 96).

4. **What was missing?**
   - **A search for tests that pin the tracked data the plan changes.** The plan emptied `known-failures.json` but did not look for tests that pin its contents; the one that did surfaced only in the gate (RULE-1).
   - **The repo-wide sweeps in the row that adds a test block.** The new harness block passed its own file at rows 3 to 7, but the standards sweeps that read every test file ran first in the gate, after the snapshot was built and run on the host (RULE-2).
   - **The order of a rerun on the host and the issue resolve.** The plan proved `known_now_passing` with the row-0 list while the issues were open (D-1253), but did not say what a later rerun proves once they are resolved (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Kept each failed gate's receipts** in `gate-1-20261119-092449/` and `gate-2-20261119-095620/` before the next gate overwrote them, and the first H1-6 receipts in `h16-pre-cvr/` before the post-review rerun.
   - **Made every hand edit with a byte-level Python script** that asserted each anchor once and checked the file's CR count afterwards.
   - **Ran a mutation receipt for D-1259** on temporary copies: the edited test still fails with one or all four known entries put back and with either skip entry changed.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The fidelity specs at a scale of 1** (row 5): on the old plate the dev PC's three specs failed with the second host's right gap of 2, so the bug reproduced locally.
   - **AC-161.5's breadth and matrix tests** (row 6 Red): `expected 5 to be greater than or equal to 1702` and `"Hi\nHi"@8` one pixel short; both pass at row 7.
   - **The standards sweeps AC-43.13 and AC-44.13** caught skip tokens in the new harness block (D-1257).
   - **`test_ac_11_known_tracked_list`** caught that the tracked known list changed (D-1259). It did its job; the plan had not named it.

7. **Which tests were trivially obvious?**
   - AC-161.3's glyph-count check; it pins the table's shape rather than find a bug.

8. **Did pyright/ruff catch anything meaningful?**
   - Only formatting and E501 in scratch runners. No product finding.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The contract names (`PREVIEW_FOLLOWS_BAKE`, `PLATE_UNITS`, `FIDELITY_FRAME`, `HOVER_CAPABLE`, `SNAPSHOT_NO_REF`, `KNOWN_EMPTY`, `PINS_NAMED`, `LOCAL_HOST_DETAILS`) gave the tests, the handoff and both reviews one vocabulary; the plan review's F1 named `PINS_NAMED` and `HOVER_CAPABLE` directly.

10. **Was the handoff template right-sized?**
    - Mostly. The Evidence section repeats the AC table's receipts at length for 15 ACs and the §Test pins cross-references (slim_candidate below).

11. **How many tool calls did this session take?**
    - Not counted exactly. The executor's transcript ran to a few hundred calls, rows 0 to H2-6, across context compactions. Planning, the review dispatches and H1-7 to H1-7b ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-6 to one executor subagent (Claude Code, Claude Opus 5.5). It ran the review dispatches and H1-7 to H1-7b itself.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. The execution review approved at round 1 with no findings.

### Decisions Log

All are `autonomous`, decided on the HDP recommendation under Mat's hand-over. **For Mat:** D-1257 (M-6) and D-1259 (M-7, a change to an existing test's expected value that no approved row named) were decided during execution under the hand-over ("make the decisions always the recommenations"; "If you do not believe you can make the decisions run HDP and take recommenations from that!"). Planning decisions with an M hit (D-1241, D-1242, D-1244, D-1247) were approved with the plan.

- Run one session, the hover fix first and alone, rather than split it (M-6, M-8) — [D-1241](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- The preview follows the bake: the plate is the rectangle Pillow paints; the bake and saved images stay (M-5) — [D-1242](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Measure with a Segoe UI glyph and kerning table in font units, FreeType rounding and Pillow kerning — [D-1243](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Pin the measured residual as limits and register it as a low issue (M-3) — [D-1244](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Run the three fidelity specs at a device scale of 1 on every host — [D-1245](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- State a mouse-capable device for AC-126.8 and check the media query before the hover — [D-1246](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Run the host suite on a no-ref snapshot commit of the tree (M-6) — [D-1247](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Diagnose from the two existing host reports and dev-PC probes, with no new host run first — [D-1248](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Put the new tests in a new plate test file and the harness block, and move AC-102.10's oracle — [D-1249](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Register MEU-161 at matrix 9.46 with the plan-local `meu-register.py` — [D-1250](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Build the plate fixture from `adapter.text_plate_box` and check the font hash on other hosts — [D-1251](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Prove only the named test lines change with `diff-check.py` — [D-1252](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Show the four former known tests passing by a second summarize with the row-0 list — [D-1253](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Run the full dev-PC E2E in the gate through `flake-run.py`, and skip suites by path basis — [D-1254](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Change exactly the §Test pins lines the bigger plate moves — [D-1255](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Check row 12's hub audit against what the generator writes — [D-1256](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Rewrite two lines of the harness block for the standards sweeps, then run row 10 again on a new snapshot (M-6, for Mat) — [D-1257](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Show AC-161.11 by run 10b's own counts and run 10's `known_now_passing`, and disclose run 10b's exit 32 — [D-1258](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)
- Set the expected known list in `test_ac_11_known_tracked_list` to `[]` and keep its other assertions (M-7, for Mat) — [D-1259](../plans/2026-11-19-e2e-host-parity/implementation-plan.md)

**Read from their own logs, not listed:**
- D-1213 and D-1214 are on the issues.
- D-1200, D-1211, D-1215 and D-1216 are grouping §8.

**The `decision_sources` probe was re-run at H2-2** (`ehp-decision-probe-h2.txt`), with the plan, the grouping and the register with both issues:
- it reads D-1200, D-1211, D-1215 and D-1216 (grouping), D-1213 and D-1214 (triage), D-1241 to D-1255 (planning) and D-1256 to D-1259 (execution), 25 ids against 21 at the end of planning (`ehp-plan-decisions-r1.txt`); the four new ids are this session's execution decisions;
- grouping §8 alone still reads the same 4 ids, and no other session added a row;
- nothing was amended in the YAML at H2; D-1259's entry was added at execution with a full `chosen` and no slot.

---

## Pattern Extraction

### Patterns to KEEP
1. **Reproduce the remote failure on the dev PC first.** Running the fidelity specs at a scale of 1 turned a second-host failure into a local Red, so rows 6 and 7 needed no host run.
2. **No-ref snapshot commits for the host run.** The host ran the exact tree without a commit on `main`, and the reviewer bound 14 snapshot files to it.
3. **Keep each failed gate's receipts.** The reviewer read all three gates in order and confirmed both failures were fail-fast and corrected, not suppressed.

### Patterns to DROP
1. **A long Evidence section that repeats the AC table's receipts.** One table with receipt paths would carry it.

### Patterns to ADD
1. **Search the tests for pins on any tracked data the plan changes** (RULE-1).
2. **Run the repo-wide test sweeps before building a snapshot for the host** (RULE-2).
3. **Order the host proof before the issue resolve, and say what a later rerun proves** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time:** about 2 hours 20 minutes from the plan review's approval (08:20) to the execution review's approval (10:38), of which about 42 minutes was the two host runs and 32 minutes the two failed gates.
- **Tokens:**

  | Item | Tokens |
  |---|---|
  | Plan review, round 1 | 13,054,307 |
  | Plan review, round 2 | 8,886,917 |
  | Execution review, round 1 | 16,853,764 |

- **Adjusted estimate** for a product fix proved on the second host: about 9M to 13M tokens for a plan review round and 17M for an execution round; about 2 hours of rows, including two 21-minute host runs, or 1.5 hours with one host run and one gate if RULE-1 and RULE-2 hold.

---

## Next Session Design Rules

```
RULE-1: A plan that changes tracked data (a list, a register or a fixture) searches tests/ and ui/tests/ for tests that pin that data's contents, ids or count, and names each one it finds in Files Modified and §Test pins with its old and new value.
SOURCE: Session 97 gate 2 failed at py-tests: test_ac_11_known_tracked_list pinned the four known entries that row 9 removed, and no plan row named it (D-1259, M-7).
EXAMPLE: before, the plan empties known-failures.json and lists only that file; after, it also lists tests/tooling/test_e2e_remote.py test_ac_11_known_tracked_list, expected known list [four entries] -> [].
```

```
RULE-2: A row that adds or changes a test block runs the repo-wide standards sweeps over test files (AC-43.13, AC-44.13 and the like) in its own Green, before any snapshot for a host run is built.
SOURCE: Session 97 gate 1 failed at ui-tests: the sweeps refused two skip tokens in the new e2e-harness block after run 10 had already used the snapshot, so row 10 ran again on the host (D-1257).
EXAMPLE: before, row 7 Green runs the six touched Vitest files; after, it also runs the standards sweep files and the snapshot is built only when they pass.
```

```
RULE-3: A plan that proves a fix by a host run against a tracked known list runs that proof before the row that resolves the issues, and states what any later rerun proves after the resolve (its own counts, not a second summarize with the old list).
SOURCE: Session 97 row 10b passed 232 of 232, but its summarize with the row-0 known list exited 32 known-failures-stale because row 11 had resolved the issues (D-1258).
EXAMPLE: before, "rerun row 10 once" after a snapshot change; after, "a rerun after row 11 is shown by its own counts and box gaps; the known_now_passing proof stays with the run before row 11".
```

---

## Next Day Outline

1. **Next:** the 2026-11-18 E2E-host grouping is done. The next step is issue triage (`.agent/skills/issue-triage/`) and a new session grouping for Mat. The prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, plus the rules Sessions 74 and 82 to 96 carried, all in the start prompt.
4. **Codex validation scope:** the next session's own loops.
5. **Time estimate:** set by the triage and grouping pass.
6. **Still open for Mat:** D-1216's host items (Smart App Control, auto sign-in, a GitHub runner), which stay his and unchanged; D-1200 (the FFmpeg report); `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` (low); D-1257 and D-1259 to read; and the commit of Session 97 by the coordinator, with no push from the agent. H2-5 has the draft and the path list.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | A few hundred in the executor's transcript, rows 0 to H2-6; not counted exactly |
| Time to first green test | Row 4 at 08:43 (AC-161.9 passing), 7 minutes after row 0; row 7 Green at 08:51 |
| Tests added | Six Vitest tests (four in the new `capture-text-plates.test.ts`, AC-161.8 and AC-161.9 in `e2e-harness.test.ts`) and one pytest test (`test_capture_text_plates.py`); eight §Test pins lines changed (D-1255) and one expected value (D-1259). Final gate: Vitest 1,639 in 146 files, Python 3,301 passed, dev-PC E2E 232 |
| Codex findings | Plan review: R1 changes required, 1 finding (F1 High, `PINS_NAMED` let an unnamed early return defeat `HOVER_CAPABLE`, fixed); R2 approved. Execution review: R1 approved, 0 findings |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the gate passed, and the execution review approved at round 1 |
| Rule Adherence (%) | 90 (9 of 10 sampled rules followed) |
| Prompt→commit time | Planned, executed, approved and closed 2026-11-19; the coordinator commits without a push |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution, and the executor never dispatched or wrote a verdict |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. The only git objects are the two no-ref snapshots; H2-5 is a draft and a path list only |
| Red before Green, by assertion | AGENTS.md §Testing | Yes. Rows 3, 4, 5 and 6 each read 0 problems in `red-check.py` |
| Never edit a test to pass (S3) | The plan's stop table | Yes, with two disclosed decisions. D-1257 rewrote two of this session's own new lines with the same matches; D-1259 changed one expected value with a mutation receipt, decided as M-7 under the hand-over |
| Change only the named test lines | The plan (`PINS_NAMED`) | Yes. `diff-check.py` passed in the gate with D-1259's path added to its allowed list |
| No host value in a tracked file | The plan (`LOCAL_HOST_DETAILS`) | Yes. The host-details scan reads bad=0 over 45 files |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. eol-check reads 28 paths, 0 problems; `metrics.md` and `current-focus.md` stay CRLF |
| An LF file is written as bytes and its CR count checked | Session 83 RULE-3 | Yes. The commit draft, the reflection and the runners read CR 0 |
| No model call or network use beyond the configured host | The brief | Yes. Only SSH and scp to the configured host |
| Run each Validation cell as written | The execution workflow | No. The H1-2 gate ran three times around D-1257 and D-1259, row 10 ran twice, and H1-7a and H1-7b wrote other receipt names; all disclosed |

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
    - docs/execution/reflections/2026-11-18-e2e-remote-host-reflection.md
    - .agent/context/handoffs/2026-11-18-e2e-remote-host-handoff.md
    - .agent/context/handoffs/2026-11-17-video-tail-frame-MEU-160-handoff.md
    - .agent/docs/e2e-remote-host.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:never-edit-a-test-to-pass, P0:keep-line-endings, P1:red-before-green, P1:hdp-recommendation-under-hand-over]
conflicts:
  - "S3 (never edit a test to pass) against a gate failure in a test that pinned data the plan changed; D-1259 changed one expected value as M-7 under the hand-over, with a mutation receipt."
  - "The task cells name ehp-review-state.json and ehp-exec-review.txt; the coordinator who runs H1-7a and H1-7b wrote review-state.json and exec-review.txt."
note: "Text plate follows the bake and the E2E suite passes 232 of 232 on the second host; two gate failures from unplanned test pins."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "The handoff's Evidence section repeats the AC table's receipts at length."]
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
  finding_categories: {weak_test: 1}
  verdicts:
    changes_required: 1
    approved: 2
meu_work_classes: [correctness]
```

The review churn counts the ledger's recorded rounds in the session's two loops. The plan loop, `ehp-plan-2026-11-19-e2e-host-parity`, used 2 of 3 rounds: round 1 found F1 (High, blocking, `PINS_NAMED` accepted an unnamed early return that defeated `HOVER_CAPABLE`) and round 2 approved with F1 fixed (`usage` 13,054,307 and 8,886,917). The execution loop, `ehp-execution-2026-11-19-e2e-host-parity`, used 1 of 6 rounds: round 1 approved with no findings and `intent_achieved=yes` (`usage` 16,853,764).
