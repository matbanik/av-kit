---
date: "2026-11-15"
project: "2026-11-15-tooling-test-hermeticity"
meus: []
plan_source: "docs/execution/plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-15 Meta-Reflection

> **Date**: 2026-11-15. Planned and plan-reviewed in the afternoon; executed, reviewed and closed in the evening.
> **MEU(s) Completed**: none. Session 76 `tooling-test-hermeticity`, tooling tests and their fixtures with no MEU, the second session of the post-rc.3 triage residuals grouping (`.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` §3).
>
> - **The registry tests** (`TOOLING-SHARED-REGISTRY-COUPLING`, now `mitigated`) resolve against a tracked synthetic registry in a temp registry home, with the overlay compiled there and a temp wrapper copy for the refusal test (D-911). The HDP live check `test_ac_10_…` still reads the machine registry by design (D-912).
> - **The governance fixture** (`TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`, `resolved`) rebinds the copied rule map's pins and copies new backlink targets; `test_ac_14_…` keeps D-132's live pin signal (D-915).
> - **The dispatch placeholder arm** (`CLI-DISPATCH-PLACEHOLDER-FIXTURE`, `resolved`) builds its token at run time; the suite reports 31 of 31 PASS. av-kit's copy diverges from upstream on purpose (D-913).
>
> **Plan Source**: `docs/execution/plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Row 1's red-check.** The Red itself was right (13 failed, 4 passed), but `red-check.py` reported the required tests missing: pytest pads a long parametrized test id's failure header with a single underscore on each side, and the copied pattern needed three. D-919 widened the pattern and added a long-id selftest fixture.
   - **Row 6's first suite run** exited 1 with `registry_not_found`, because the row command did not set `AGENT_MODEL_REGISTRY_HOME`, which row 0 sets for the same suite (D-920).
   - **HEAD moved after the review.** Mat ordered Session 75 committed (`661d142`) once this session's execution review had approved. D-918's scope check accepted the move (38 paths, all committed at their row-0 bytes), but HEAD is part of `tested_state`, so the H1-2 gate ran a second time to give H1-6b a full record that binds the new state.

2. **What instructions were ambiguous?**
   - **H2-2's decision list.** The row names plan D-911 to D-918 and any of D-919 to D-921, and HDP §6 lists only reversible autonomous choices. All ten are autonomous and reversible, so both readings give the same list.
   - **B-1 option 2's HEAD rule.** "Paths all in `baseline-dirty.txt` with their row-0 bytes" is ambiguous under `core.autocrlf`, where the working bytes differ from the blob bytes. The scope check compares blobs (`baseline-dirty-blobs.json`), the stricter reading.

3. **What instructions were unnecessary?**
   - H1-4's OpenAPI row, again: the session cannot touch `packages/api`.
   - H2-1's `view_file` row: H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **The row environment for the dispatch suite.** Row 0's `baseline.ps1` set `AGENT_MODEL_REGISTRY_HOME`; row 6's Validation cell did not. A row that reruns a baseline suite needs the baseline's environment (RULE-2).
   - **A plan rule for a HEAD move after the gate.** The plan covered a move during the rows (D-918) but not that `tested_state` binds HEAD, so any allowed commit after H1-2 means a second gate run before H1-6b (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **An extra row-0 record**, `baseline-dirty-blobs.json`, so the HEAD rule compares blobs.
   - **Row wrappers** `C:/Temp/av-kit/tth/row<n>.ps1` and `h1-<n>.ps1` that run each Validation cell verbatim after the row environment and the S4 check.
   - **A second gate run** (H1-2 rerun after the HEAD move), its receipts beside the first run's, which are kept under `gate-r1/`.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **`red-check.py`'s selftest gap.** Not a product bug: the oracle's own pattern was too narrow. The receipt showed real headers it missed, and the new fixture keeps it fixed.
   - **The HOSTILE Red** proved the coupling was real: under a registry that names an unknown slug, 12 cases failed by assertion before the fixture existed.
   - **`fixture-check.py`** caught `make_fixture.py`'s wrong repository root (`parents[3]`, the `tests/` folder) on its first run.

7. **Which tests were trivially obvious?**
   - AC-8 (`test_ac_8_pin_oracle_still_refuses`) passes before and after row 4 by design; it guards the verifier's refusal against the rebind, not new behaviour.

8. **Did pyright/ruff catch anything meaningful?**
   - ruff: UP012 (an unneeded `.encode("utf-8")`) and two E501 lines in `make_fixture.py`, all before placing. No logic changed. pyright was skipped; nothing under `packages/` changed.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The plan's names (`TEST_FILE`, `FIXTURE`, `HOSTILE`, `NEEDLE`, `RULE_MAP`, `RED_IDS`, `BASE`) and its 14 ACs gave the rows, the handoff and the review one vocabulary. Both reviews approved at round 1 with 0 findings.

10. **Was the handoff template right-sized?**
    - Yes. The execution notes ran to 14 bullets, each a disclosed deviation. The evidence.v1 blocks per row made H1-6b a mechanical check.

11. **How many tool calls did this session take?**
    - About 260 in the executor's transcript, rows 0 to H2-5. Planning, the review dispatch and the Session 75 commit ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-5 to one executor subagent (Claude Code, Claude Opus 5.5), and ran H1-7 to H1-7b itself. No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. No delegated result needed rework.
    - Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

- Use a tracked synthetic registry in a temp registry home for the registry tests, written by `make_fixture.py` — [D-911](../plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md)
- Keep the HDP live registry checks as they are and run `live-probe.py` once in the gate, leaving the issue `mitigated` — [D-912](../plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md)
- Fix the dispatch placeholder arm in av-kit's copy as a divergence; upstream is not edited — [D-913](../plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md)
- Leave the empty leftover temp folder for Mat, with a one-line removal command — [D-914](../plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md)
- Rebind the migrated tree's pins and copy new backlink targets, and keep D-132's live pin check in `test_ac_14_…` — [D-915](../plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md)
- Run the gate steps the plan lists and skip types, UI, MCP, OpenAPI and build with reasons — [D-916](../plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md)
- Keep the out-of-scope rows out — [D-917](../plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md)
- Bind scope checks to row 0's bytes, and let HEAD move only by commits of baseline-dirty paths at their row-0 bytes — [D-918](../plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md)
- Widen `red-check.py`'s pytest header pattern to one underscore, with a long-id selftest fixture — [D-919](../../../.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-handoff.md)
- Run row 6's dispatch suite with row 0's `AGENT_MODEL_REGISTRY_HOME` — [D-920](../../../.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-handoff.md)

---

## Pattern Extraction

### Patterns to KEEP
1. **A HOSTILE environment for the Red.** Pointing `AGENT_MODEL_REGISTRY` at a registry that names an unknown slug, in the child process only, turned "reads the machine registry" into an assertion failure before the fix and a pass after it.
2. **Byte-copy fixtures for files the tests must not edit.** `fixture_wrapper` replaces `NEEDLE` once in a temp copy of `WRAPPER`, and `rebind_instruction_pins` edits only the copied rule map, so `WRAPPER`, `RULE_MAP` and `VERIFIER` stay untouched.
3. **Content-bound baselines.** Binding every check to row 0's bytes let Session 75's commit land mid-session without a re-baseline.

### Patterns to DROP
1. **Copying a peer plan's oracle without its fixture range.** `red-check.py` came from Session 87 unchanged in logic, but this suite's test ids are much longer; a selftest fixture with this suite's longest id would have caught D-919 at plan time.

### Patterns to ADD
1. **Selftest each copied oracle on the target suite's longest id** at plan time (RULE-1).
2. **Give every row that reruns a baseline suite the baseline's environment** (RULE-2).
3. **Plan for a HEAD move after the gate:** the identity binds HEAD, so an allowed commit after H1-2 needs a second gate run before H1-6b (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget; the plan set round caps of 3 (plan) and 6 (execution).
- **Actual time (local time, from the receipts' mtimes):**
  - Execution: row 0 passed at 21:38, the registry Red at 21:40 and Green at 21:41, the governance Red at 21:44 and Green at 21:46, the dispatch Green at 21:48, the registers at 21:49, the first gate passed at about 22:00 and the handoff checks at 22:02.
  - Execution review: begun at 22:04, round 1 approved at 22:11, H1-7b at 22:16.
  - After Session 75's commit: the scope check at about 22:16, the second gate run from 22:17 to 22:23, and H1-6 to H1-6b on the final handoff at 22:24.
- **Tokens:** plan review 7,724,924 in one round; execution review 6,715,571 in one round.
- **Adjusted estimate for a tooling-only fixture session with a HOSTILE Red:** about 7M tokens per clean review round, and about 6 to 9 minutes per gate run (the full Python suite is about 4 of them). Add a gate run when HEAD can move after H1-2.

---

## Next Session Design Rules

```
RULE-1: When a plan copies an oracle script from a peer plan (red-check.py, a scope check), its selftest gains a fixture built from the target suite's real output shape, including its longest test id, at plan time.
SOURCE: Session 76 row 1: pytest wrote "_ test_registry_contract_preserves_bindings[avkit_coordinator-cursor-task-cursor-grok-4.6-xhigh] _" with one underscore per side, and the copied ^_{3,} pattern missed it (D-919).
EXAMPLE: before, red-check.py's selftest used short ids only; after, it holds a long-id fixture and the pattern is ^_+ (.+?) _+\s*$.
```

```
RULE-2: A row that reruns a suite the baseline ran carries the baseline's environment in its Validation cell, every variable the baseline set for that suite.
SOURCE: Session 76 row 6: the dispatch suite exited registry_not_found because baseline.ps1 set AGENT_MODEL_REGISTRY_HOME and the row did not (D-920).
EXAMPLE: before, row 6 ran Test-CliDispatch.ps1 with only RECEIPTS_DIR; after, the cell sets $env:AGENT_MODEL_REGISTRY_HOME='P:/.agent' first, as baseline.ps1:26 does.
```

```
RULE-3: When HEAD may move after the H1-2 gate (an allowed commit of another session), the plan says the gate runs again before H1-6b, because tested_state binds HEAD; the scope check alone does not refresh the full record.
SOURCE: Session 76: Session 75's commit 661d142 landed after the execution review; scope-check accepted it, but identity.py gave 661d142+df4a25e3… and the handoff's full record held 3397e78+7763c700….
EXAMPLE: before, H1-6b would refuse the record; after, H1-2 ran again on 661d142, the handoff's one full record binds that run, and the first run's pass is kept in the prose and under gate-r1/ (durable_evidence.py requires every passing full record to match the expected state).
```

---

## Next Day Outline

1. **Target:** Session 77 `text-scrub-residuals` (MEU-147, MEU-148), plan `docs/execution/plans/2026-11-15-text-scrub-residuals/`, plan review approved at round 2 of 3.
2. **Before it starts:** Mat decides whether Session 76 is committed first. Session 77 edits `known-issues.*`, `current-focus.md` and `metrics.md`, which hold Session 76's uncommitted changes.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-3 here, Session 75's RULE-1 (an empty New Findings table keeps its header), and Session 85's RULE-2 (unset `ELECTRON_RUN_AS_NODE` before an identity step).
5. **Codex validation scope:** Session 77's execution, loop `tsr-execution-2026-11-15-text-scrub-residuals`, cap 6.
6. **Time estimate:** set by Session 77's plan.
7. **Still open for Mat:** the D-913 upstream fix, the D-914 leftover folder, and the commit of Session 76.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 260 in the executor's transcript, rows 0 to H2-5 |
| Time to first green test | The registry Green at row 2, a minute after the Red (`tth-reg-red.txt` 13 failed, `tth-reg-green.txt` 92 passed) |
| Tests added | 5 in `tests/tooling/test_framework_adoption.py` (AC-2, AC-6, AC-7, AC-8, AC-14); the adoption file 91 to 96, pytest 2940 to 2945 at the gate (`tth-D6-py-tests.txt`) |
| Codex findings | Plan review: R1 approved, 0 findings. Execution review: R1 approved, 0 findings |
| Handoff Score (X/7) | 6/7. Every AC has evidence and both reviews approved at round 1 with 0 findings, but two rows needed a disclosed execution decision (D-919, D-920) |
| Rule Adherence (%) | 92 (11 of 12 sampled rules followed in full, 1 in part) |
| Prompt→commit time | Planned, executed, approved and closed 2026-11-15; the commit waits on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution; the executor stopped before H1-7 |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. H2-5 is a draft only |
| Red before Green | AGENTS.md §Testing | Yes. Rows 1, 3 and 5 failed by assertion before rows 2, 4 and 6 |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `TEST_FILE` and `current-focus.md` stay CRLF, `DISPATCH_TEST` BOM and CRLF, the new files and registers LF |
| No raw home path in tracked files | The executor brief | Yes. The handoff and this reflection quote none; the leftover folder is named through `$env:TEMP` |
| Never edit `OVERLAY`, `WRAPPER`, `VERIFIER`, `RULE_MAP` or `validate_closeout_artifacts.py` | Plan §Out of Scope | Yes. The tests edit only temp copies |
| Never edit P:/agentic-framework or P:/.agent | The executor brief; D-913 | Yes. `TOOL_FILES` are copied from P:/.agent at run time |
| `AGENT_MODEL_REGISTRY` only in HOSTILE's child | The executor brief | Yes. Each run set it in a `try`/`finally` that reset it to `$null` |
| The S4 scope check before each row | Plan §Stop conditions | Yes. Every row wrapper ran `scope-check.py` first |
| Unset `ELECTRON_RUN_AS_NODE` before an identity step | Session 85 RULE-2 | Partly. Every wrapper and the gate unset it, but one manual check from the Bash tool did not and gave a different state; the rerun with it unset matched |
| Run HDP on a decision; record it once | HDP §6 | Yes. D-919 and D-920 are in the handoff only |
| Accept a HEAD move only by baseline-dirty paths at row-0 bytes | D-918; B-1 option 2 | Yes. `tth-scope-headmove.txt`: 38 paths committed unchanged, `scope-check: ok` |

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
    - .agent/context/handoffs/2026-11-15-framework-small-syncs-handoff.md
    - docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:never-edit-machine-registry-or-upstream, P1:independent-review-no-self-approval, P1:red-before-green, P1:bind-checks-to-row-0-bytes]
conflicts:
  - "Task H2-2 names plan D-911 to D-918 for the Decisions Log; HDP §6 lists only reversible autonomous choices. Every one of them is autonomous and reversible, so the list is the same either way."
  - "The H1-6b row binds the full record to the current tested_state, and D-918 allows HEAD to move; after Session 75's commit the two meant a second gate run."
note: "A fixture-only session; both reviews approved at round 1 with 0 findings, and Session 75's commit after the review cost one extra gate run."
slim_candidate: ["H1-4's OpenAPI row in a session that cannot touch packages/api.", "H2-1's view_file row repeats what H2-2's validator checks."]
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
meu_work_classes: []
```

The review churn counts the ledger's recorded rounds. D-919, D-920 and the second gate run came from the rows and the HEAD move, not from a reviewer, so they are not findings here.
