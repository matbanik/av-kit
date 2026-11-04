---
date: "2026-09-28"
project: "p11-transcript-tts"
meus: ["MEU-55", "MEU-56"]
plan_source: "docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md"
template_version: "2.0"
---

# 2026-09-28 Meta-Reflection — Phase 11 Transcript and TTS pages

> **MEUs Completed**: MEU-55, MEU-56
> **Plan Source**: docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md

## Execution Trace

### Friction Log

1. **What took longer than expected?** Getting the gate environment right. The container had no `rtk`, `pwsh` or `codex`, so the Electron binary needed a manual download (the postinstall fetch failed behind the proxy) and the sandbox had to be disabled because the container runs as root. Two frozen tests were bound to Windows (AC-51.6 CRLF, AC-41.3 `P:` drive), and the capture-picker E2E stub is Windows-only. Each needed a signed tolerance list and the user's decision (c) to move the authoritative gate to the Windows machine. The first container pre-gate also exposed a missing `out-e2e` harness build stage, which both gate scripts then gained. On Windows, one premature run (AC-49.26) and one hung run (W9-3) each needed a rerun before a clean gate. Execution review took two rounds.
2. **What instructions were ambiguous?** Review routing. The workflow dispatches external reviewers through the Codex CLI, which does not exist on the web platform. The user's direct instruction to use a Fable 5.1 subagent at high effort settled it. It is a same-vendor route, recorded with its scope in `human-review-decision.md`. The harness profile's RTK receipt contract also assumes `rtk`. Here receipts were plain redirects into `$RECEIPTS_DIR` with immediate exit capture.
3. **What instructions were unnecessary?** Repeating the full-gate evidence record in both MEU handoffs, which again had to be edited in two places each time the gate reran (three times). The peer reflection named the same slim candidate.
4. **What was missing?**
   - The initial AC-55.5 focus test covered only the successful reorder. The rejected path, where focus stayed on `body`, was found by the reviewer, not by the plan.
   - The plan's gate stage list did not include the isolated harness build that the capture E2E specs need.
   - The `amendments` guard compared against `HEAD`, so it false-flagged this plan's own test files once they were committed. It now diffs against the pre-session baseline `0f51036`.
5. **What did you do that wasn't in the prompt?**
   - Wrote both gate scripts (`validate-task.sh` for the container pre-gate, `validate-task.ps1` for Windows) and the `windows-gate-check` validator, which binds the result to a code-identical commit.
   - Recorded the failed and premature Windows runs with assessments instead of discarding them.
   - Captured per-click timing to justify the W2-5 time budget.
   - No API or payload change, and no YouTube interaction.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - The reviewer's rejected-reorder probe, turned into the regression test `AC-55.5 focus returns to the card after a rejected reorder too`. It failed on the old page with `expected <body> to be <button>`, the reviewer confirmed Red on the pre-fix tree, and it is Green after `9fb0153`.
   - The frozen W2-5 voice-PUT ledger caught the plan-stage native-radio design before any code (plan Round 1 High).
   - The shared-slot baseline fixture (AC-55.1) proved `QueueCard` without slots stays byte-identical, which was the decisive evidence for ruling out the AC-49.26 and W9-3 Windows failures.
7. **Which tests were trivially obvious?** The static source and width audits (`rg` for TODO, `transition-all`, arbitrary widths) and the reflection-marker check certify shape only. The additive `test-ids.ts` entries have no behavior of their own; the Electron specs that use them do.
8. **Did pyright/ruff catch anything meaningful?** Not applicable; UI-only work. TypeScript typecheck and ESLint passed on every gate; no product defect came from them. The behavior defect came from independent review plus Vitest.

### Workflow Signal Log

9. **Was the FIC useful as written?** Yes. The single-statement contracts (`CARD_SLOTS`, `LIST_SLOT_RESOLVER`, `VOICE_LISTBOX`, `RUN_BAR_SLOT`, `OUTPUT_ACTIONABLE`, `COMPOSITION_LOCK`) gave the reviewer exact oracles. The one blocking execution finding cited AC-55.5 directly. `ENV_BOUND_TESTS` and `ENV_BOUND_E2E`, with exact failure signatures, stopped the container from turning tolerated failures into a silent pass.
10. **Was the handoff template right-sized?** The AC tables, TEST_AMENDMENTS before → after and the evidence.v1 blocks supported review without reconstructing intent. The duplicated project-wide gate record is the compression opportunity (see slim candidate).
11. **How many tool calls did this session take?** Not reliably instrumented across two context compactions. No estimate is presented. Commands and outcomes are retained in the walkthrough, handoffs and receipts.
12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?** No `av-kit-builder` or `av-kit-verifier` delegation. Independent review ran in fresh Claude Code `Agent` subagents with `model: fable` at high effort: plan review in 3 rounds, execution review in 2. The authoritative `WINDOWS_GATE` was a human-run step on Mat's machine, executed by his local agent. Its premature first run and its hung W9-3 run were re-run, not reworked.

## Pattern Extraction

### Patterns to KEEP

1. Split the gate: a non-authoritative container pre-gate with signed, signature-matched environment tolerances, and an authoritative gate on the target OS that tolerates nothing.
2. Bind the external gate result to a commit and verify the reviewed HEAD is code-identical (`git diff <tested> HEAD -- ui/` empty) before dispatching review.
3. Assess a failing gate test for code overlap before a rerun, never label it a flake, and allow one rerun only on a documented, non-overlapping basis.

### Patterns to DROP

1. Do not start the authoritative gate before the pre-gate passes and its stage list is final (the premature `548bc2a` run could not pass the check).
2. Do not let validators classify "pre-existing" files against `HEAD` in a multi-commit session.

### Patterns to ADD

1. For every focus-restoration contract, test success, rejection and a disabled edge in the first Red pass.
2. Before an authoritative gate on a shared workstation, confirm that no other agent thread or Electron/Playwright process is running. Copy `test-results/` out immediately on any failure, before any rerun can clear it.
3. Include every build artifact an E2E suite needs (here, the isolated harness build) in the planned gate stage list, checked against the suite's global setup.

### Calibration Adjustment

- Estimated time: not recorded; no retrospective number is invented.
- Actual scope: two MEUs, five shared-component extensions, 34 Vitest and 8 Electron cases added (597 → 631, 95 → 103). The work took 3 plan and 2 execution review rounds and three Windows gate runs to reach two clean ones.
- Adjusted estimate for similar MEUs: budget one gate-environment pass (tooling, env-bound census, stage parity) before the first pre-gate when the driver's OS differs from the target OS.

## Next Session Design Rules

```text
RULE-1: A focus-restoration test must cover the rejected settle path as well as success.
SOURCE: execution Round 1 Finding 1 / AC-55.5 (focus stayed on body after a 409).
EXAMPLE: hold the PUT, prove focus is lost, release a 409, assert focus on the card's same-direction button.
```

```text
RULE-2: Run the authoritative gate on a quiet machine and preserve failure artifacts before any rerun.
SOURCE: W9-3 launch/teardown hang on c315640 run 1; error-context.md lost to later single-spec reruns.
EXAMPLE: check for other agents and Electron processes first; on failure, copy ui/test-results and the receipts out of the repo, then decide on a rerun.
```

```text
RULE-3: Guards that separate pre-existing from new files must diff against the pre-session baseline commit.
SOURCE: the amendments guard false-positive after this plan's own tests were committed.
EXAMPLE: git diff --name-only 0f51036 -- ui/tests plus git cat-file -e "0f51036:$f", not git diff HEAD.
```

## Next Day Outline

1. Start Session 26 `p11-capture-settings` (MEU-57 Capture page, MEU-58 Settings page), the Phase 11 exit that runs the phase gate.
2. Re-read the Phase 11 layout canon, the Capture and Settings page specs, and the grouping row before writing the FIC.
3. Carry forward: shared-root lookup by data attribute, async hydration yielding to user ownership, and focus tests covering rejected paths.
4. Put every gate stage, including the isolated harness build, in the plan up front. Pre-declare the env-bound census, since the capture-picker stub is Windows-only and Capture is in scope.
5. Decide the review route and gate location with the user at plan time, not mid-execution.
6. Optional follow-up (non-blocking F3): consider skipping focus restoration when the user has moved focus outside the card, in both `TranscriptPage` and `QueueList`.

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | Not reliably instrumented across the continued session |
| Time to first green test | Not measured; Red and Green receipts are retained |
| Tests added | 34 Vitest (8 slot, 16 Transcript, 10 TTS) and 8 Electron; final Windows gate 631 / 103 |
| Codex findings | Plan: R1 1 High + 2 Medium, R2 0 blocking, R3 0 blocking (approved). Execution: R1 1 Medium + 1 Low, R2 0 blocking + 1 Low (approved). Reviewer: Fable 5.1 subagent, not Codex |
| Handoff Score (X/7) | 7/7 sections populated in each MEU handoff |
| Rule Adherence (%) | 4/5 sampled rules below; no exhaustive percentage claimed |
| Prompt→commit time | Not measured |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Write tests before production corrections and keep frozen assertions | Testing & TDD Protocol | Yes; the Round 1 regression was Red before `9fb0153` and only TA-1..TA-7 were edited |
| Independent reviewer authors approval | Execution Contract | Yes; both approvals were written by fresh Fable subagents |
| Explicit human authorization for the route and gate exceptions | Human Approval Gate | Yes; `human-review-decision.md` and `human-gate-decision.md` quote the user |
| RTK redirect with all-stream receipts | Priority 0 | Partly; `rtk` was unavailable, so plain redirects into `$RECEIPTS_DIR` with immediate exit capture were used |
| Continue through H2 after approval without an intermediate stop | Execution Contract | Yes |

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-25-p11-transcript-tts-2026-09-28"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 2}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md
    - docs/execution/plans/2026-09-28-p11-transcript-tts/task.md
    - docs/execution/plans/2026-09-28-p11-transcript-tts/human-review-decision.md
    - docs/execution/plans/2026-09-28-p11-transcript-tts/human-gate-decision.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:independent-review-no-self-approval
  - P1:explicit-human-review-route-exception
  - P1:no-tolerated-failure-in-authoritative-gate
  - P1:continue-through-post-review-closeout
conflicts:
  - "The review workflow dispatches through the Codex CLI, which is absent on the web platform; the user directed a same-vendor Fable 5.1 subagent route, recorded in human-review-decision.md."
  - "The D6 fresh full gate must pass without tolerance, but two frozen unit tests and the capture-picker E2E stub are Windows-bound; the user chose (c), moving the authoritative gate to Windows with a signed container tolerance list."
  - "The Priority 0 RTK receipt contract assumes rtk, which the container lacks; receipts used plain redirects with immediate exit capture."
note: "Session 25 reached execution Round 2 approval after one rejected-reorder focus correction; authoritative Windows gate 631 Vitest / 103 Electron on c315640."
slim_candidate: ["Repeated project-wide full-gate evidence in every MEU handoff; one canonical record in the walkthrough plus references would do"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 2, low: 2}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 1}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 4}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 1, low: 1}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 1}
  churned_findings: 0
  finding_categories: {contract_drift: 3, weak_test: 1, provenance_error: 1, other: 1}
  verdicts: {changes_required: 2, approved: 3}
meu_work_classes: [mixed, mixed]
```
