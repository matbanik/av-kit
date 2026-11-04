---
date: "2026-10-27"
project: "tts-sideload-load"
meus: ["MEU-98"]
plan_source: "docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-27 Meta-Reflection

> **Date**: 2026-10-27 (planned 2026-10-26, executed and closed out 2026-10-27)
> **MEU(s) Completed**: MEU-98 `svc-tts-sideload-load` (rider `TTS-SPACY-SYSPATH-STALE-DIR`; eSpeak evidence stage for `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`)
> **Plan Source**: `docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   - **Plan review.** Two rounds and 12.8M tokens. Round 1 was `changes_required`:
     - F1 High: AC-98.5(c)'s `dataclasses.replace` could never reach the adapter, because domain validation rejects the format first.
     - F2 Medium: the eSpeak probe was PATH-only.
     - F3 and F4 Low: "commit" was ambiguous, and the spaCy swap trigger was wrong.

     Mat tripled the token budget before round 2. Round 2 approved, with one Low on the review scaffolding (F5).
   - **The row 0 baseline.** It ran at `d30f62b` and found the four `test_framework_adoption.py` failures again: the rule-map pin was stale after `bb481ec`'s AGENTS.md edit. Session 41 had excused them as baseline failures (its D-154). This time Mat chose to rebind the pin (D-132). That meant a separate commit (`c34866b`) and a second row 0 run before any Red row.
   - **Tooling that fails closed when run by hand.** The gate passed because the row runner set `RECEIPTS_DIR` (ECN-3). Run directly, `lint_task_contract.py` and `review_ledger.py begin` each failed closed once without it.

2. **What instructions were ambiguous?**

   - **Where the B-10 block goes.** The plan put row 10's `### B-10` `evidence.v1` block in `walkthrough.md`. The blocked-row predicate shared by `lint_task_contract.py` and `durable_evidence` reads `task.md`, so it moved there (D-133, ECN-2).
   - **`[B]` in the handoff.** `validate_closeout_artifacts.py` treats any handoff table row containing the literal `[B]` as a blocked row. The AC-98.10 and AC-74 rows were reworded "blocked (b)".

3. **What instructions were unnecessary?**

   None cost real time. The handoff's Codex Validation Report section stays `pending` after approval, as in Session 41. The verdict lives in the review file and the ledger, so the section repeats nothing the validators read.

4. **What was missing?**

   - **A note on where blocked-row evidence lives** in the plan template's `[B]` guidance. It should name `task.md`, which is what the validators read.
   - **A decision-id allocation rule.** Session 42's plan ids (D-120 to D-131) and handoff ids (D-132, D-133) reuse numbers that Session 40's and Session 41's records already use, with other meanings. Every validator scopes ids to its decision sources, so nothing failed. A reader cross-referencing reflections still has to know which session an id belongs to.

5. **What did you do that wasn't in the prompt?**

   - **Refreshed `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`'s verification** with the D-132 rebind (`c34866b`, 91 passed after). It stays open, because the next governance edit reds the tests again.
   - **Ran the production eSpeak probe and recorded the absence durably.** `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`'s verification now points at B-10; Mat installing eSpeak NG 1.52 is the only way to run AC-74.11.

### Quality Signal Log

6. **Which tests caught real bugs?**

   - **AC-98.1 to AC-98.3, and AC-98.6 through the real Stack.** Each failed at Red because no path was persisted: `GET /models/downloaded` showed the file, and `POST /models/load` sent the adapter `path None`.
   - **AC-98.4 and AC-98.5.** Seven Reds of `AssertionError: []`: none of the four failure branches logged `tts.load_failed`.
   - **AC-98.8 and AC-98.9.** After a `tts.models_directory` change, the old install dir stayed on `sys.path` and the Dependencies card read `ready`.
   - **Codex plan review F1** (the reviewer, not a test). Without it, AC-98.5(c) would have been a Red that failed for the wrong reason, a domain `ValidationError`.

7. **Which tests were trivially obvious?**

   - **AC-98.7.** It asserts that the scan catalog ids equal the seed ids. It passes at Red by design, as a guard.
   - **The lexical no-file-I/O guard in `test_services.py`.** Codex graded it Adequate: it checks spellings, not behaviour.

8. **Did pyright/ruff catch anything meaningful?**

   No. Both were clean at every Green row and in the gate.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Yes. Every product change maps to one named contract: `SIDELOAD_RECORD`, `RECORD_RULE`, `MARK_SIGNATURE`, `REMOVED_FILE`, `LOAD_FAILURE_PATHS`, `LOG_CAUSE`, `SPACY_PATH_SWAP`, `CONTRACT_STACK`, `ESPEAK_STAGE` and `RED_TREE`. The plan review's four findings were each local to one contract or one AC. Execution review found nothing.

10. **Was the handoff template right-sized?**

    Yes, for one MEU: a 16-row AC table, with cross-reference rows for AC-9, AC-12, AC-24/25, AC-73, AC-74 and AC-75.

11. **How many tool calls did this session take?**

    Not tracked precisely. A few hundred across planning, the branch clean-up Mat asked for, execution and closeout, with at least two context compactions.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**

    None. Claude Code (Opus 5.5) ran every row.
    - **Plan review:** Codex CLI `gpt-6.1-sol` (high). Round 1 `changes_required`: F1 High (blocking), F2 Medium, F3 and F4 Low; 7,460,160 tokens. Round 2 `approved`: F5 Low; 5,340,729 tokens.
    - **Execution review:** the same route. Round 1 `approved`, 0 findings, `intent_achieved: yes`; 4,060,325 tokens.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-86 | triage | Which build-plan section and MEU own the sideload load failure? | autonomous | New MEU-98 `svc-tts-sideload-load`, matrix row 3.11: persist the sideloaded path when detected, resolve it in load, log the failure | Spec | `MODEL-SIDELOAD-LOAD-500` D-86 (carried). 02-infrastructure.md:447 already says a sideloaded file is marked downloaded, so this is a residual defect. Grouping D-98 refined the row and log level. | — |
| D-94 | grouping | Do MEU-93 to MEU-97 run as one GUI session? | autonomous | No: Session 40 (MEU-94, MEU-93) and Session 41 (MEU-95 to MEU-97) | Local Canon | Grouping §8 D-94 (carried). Outside this session's scope; it fixed Session 42 as the grouping's third session. | — |
| D-95 | grouping | Session order | autonomous | 40, then 41, then 42 | Local Canon | Grouping §8 D-95 (carried). Session 42 shares no files with 40 and 41 and runs last on priority (P3). | — |
| D-96 | grouping | What happens to `QUEUE-PILL-TOKEN-DRIFT` and its MEU-92 on main? | autonomous | Out of this grouping; resolved by the Session 31b merge | Human-approved (via 31b) | Grouping §8 D-96 (carried; the reflection check reconciles every §8 row). Outside this session's scope. | — |
| D-97 | grouping | Backfill the matrix rows that registered MEUs were missing? | autonomous | Yes: 3.9, 3.10, 4.4, 9.21, 9.22 | Local Canon | Grouping §8 D-97 (carried). It made row 3.11 for MEU-98 follow without a gap. | — |
| D-98 | grouping | Do D-86's matrix row and log level still hold? | autonomous | Row 3.11 and the existing error-level `tts.load_failed` | Local Canon | Grouping §8 D-98 (carried). It became `LOAD_FAILURE_PATHS`: the new branches join the adapter's existing event, not a new warning (plan D-127). | — |
| D-99 | grouping | Which TECH-DEBT rows ride with an MEU session? | autonomous | `GUI-AUDIT-CLIPBOARD-RESOLVER` with Session 41; `TTS-SPACY-SYSPATH-STALE-DIR` with Session 42 | Local Canon | Grouping §8 D-99 (carried). The rider sits on the same models directory as MEU-98; it landed as `SPACY_PATH_SWAP` (plan D-128). | — |
| D-100 | grouping | Where does `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` run? | autonomous | A local evidence stage in Session 42 | Local Canon | Grouping §8 D-100 (carried). eSpeak NG is absent here, so row 10 is `[B]` (b), the issue stays open and the session closes, as D-100 provides (plan D-130). | — |
| D-101 | grouping | FFmpeg licence posture: LGPL build or GPL with source offer? | autonomous | Left open for its owner: Session 42 does not decide it | Local Canon | Carried from grouping §8 D-101, which is still `open` there and awaits Mat (one-way for distribution). Session 42 changes no FFmpeg build or licensing. | — |
| D-102 | grouping | Register an MEU for `TTS-JA-ZH-G2P-EXTRAS` now? | autonomous | No; the next triage | Local Canon | Grouping §8 D-102 (carried). Outside this session's scope. | — |
| D-103 | grouping | When does the independent MEU scoping review run? | human | A separate Codex dispatch after Mat confirms the grouping, before the first `/create-plan` | Human-approved | Grouping §8 D-103 (carried). It approved in round 2 (`s40-42-grouping-scoping-2026-10-24`); `PREREQS` checked it before any product edit. | Grouping §8 D-103 (USER_EXPLICIT 2026-10-24 "yes go ahead") |
| D-120 | planning | Where is the plan written and executed? | autonomous | `P:/av-kit` on `main`; no branch or worktree | Human-approved | Mat ruled out branches and worktrees on 2026-10-26 (AGENTS.md §Commits), and Session 40 had committed (plan D-120). | — |
| D-121 | planning | Which interpreter does the environment use? | autonomous | `uv sync --frozen --all-packages --python 3.12` in row 0 | Local Canon | The gate's identity hashes the interpreter and its distributions; 3.12 matches the main tree (plan D-121). | — |
| D-122 | planning | Which D6 ids does the gate run? | autonomous | The Python ids plus `state-canon`, with the input identity before and after | Local Canon | No renderer, IPC, MCP or schema file changes; the two Vitest canon suites read the state files rows 9 and H2-2 write (plan D-122). | — |
| D-123 | planning | Where is a sideloaded file recorded, and when? | autonomous | `SIDELOAD_RECORD`: a private `ModelService` step at the start of `list_available` and `load`, one explicit commit when it wrote anything | Spec | Core owns the unit of work and the scan already flows through `ModelCatalogPort`; recording in `ModelManager.sideload` would break AC-9.8 (plan D-123). | — |
| D-124 | planning | Which scanned rows are written? | autonomous | `RECORD_RULE`: not downloaded, or a different path | Local Canon | Writing only on a difference keeps repeated lists commit-free and repairs legacy rows; a size comparison would need a stat in core (plan D-124). | — |
| D-125 | planning | Does `mark_downloaded` gain a size argument? | autonomous | No; row 1 corrects the 03 wording to `mark_downloaded(id, path)` | Local Canon | The repository already records the size from the file (plan D-125). | — |
| D-126 | planning | What happens when a recorded file is removed? | autonomous | `REMOVED_FILE`: the row stays recorded; load answers 422 and logs once | Spec | 03 "Tests" names this outcome; un-marking needs a second rule nobody asked for (plan D-126). | — |
| D-127 | planning | Which load failures log, with which device and cause? | autonomous | `LOAD_FAILURE_PATHS` and `LOG_CAUSE`: one event per failure; weight-path failures on `cpu`; `error` names the cause | Spec | 03 "Logged failure" and grouping D-98; `ModelLoadError` alone would not say why (plan D-127). | — |
| D-128 | planning | How does readiness stop seeing the old spaCy folder? | autonomous | `SPACY_PATH_SWAP`: track appended entries and swap them for the current folder's on every call | Research-backed | Every readiness path already calls activate; tracking only what av-kit appended keeps user entries safe; `is_package` reads metadata on `sys.path` (plan D-128, R-a, R-b). | — |
| D-129 | planning | Where does the contract test live? | autonomous | `CONTRACT_STACK` in `test_tts_assets.py`; no new e2e file | Local Canon | The `Stack` runs the production `build_services` and `create_app`; `tests/e2e/api_fakes.py` would not reach `ModelService` (plan D-129). | — |
| D-130 | planning | How does the eSpeak stage close when eSpeak NG is absent? | autonomous | `ESPEAK_STAGE`: probe with `EspeakCliAdapter().status()`; absent gives `[B]` (b) with evidence and a fresh verification | Local Canon | Grouping D-100; plan review F2 replaced the PATH-only probe; installing eSpeak NG is Mat's machine choice (plan D-130). | — |
| D-131 | planning | How does a Red row prove it ran before its fix? | autonomous | `RED_TREE`: each Red command refuses a change to the files its Green row edits | Local Canon | Each Green row edits one product file, so a per-file diff against `baseline.sha` is enough (plan D-131). | — |
| D-132 | execution | Row 0 at `d30f62b` found four `test_framework_adoption.py` failures from the stale AGENTS.md rule-map pin. Update the pin, or carry them as baseline? | human | Update the pin, commit and push it alone (`c34866b`), and re-run row 0 there (ECN-1) | Human-approved | The AGENTS.md change was a deliberate rule; carrying four governance failures would hide later rule-map drift (MEU-98 handoff D-132). | USER_EXPLICIT 2026-10-27 "Update pin, commit+push (Recommended)" |
| D-133 | execution | The plan puts the B-10 block in `walkthrough.md`, but the blocked-row predicate reads `task.md`. Where does it go? | autonomous | In `task.md`, with the row citing B-10 and its follow-up; `walkthrough.md` mirrors the outcome (ECN-2) | Local Canon | The outcome and evidence are unchanged; only the file moves, to the one the validators read (MEU-98 handoff D-133). Execution review checked it. | — |

---

## Pattern Extraction

### Patterns to KEEP
1. **Fault injection on one frozen instance** (`object.__setattr__` after valid construction). It reaches a defensive branch without patching domain validation or the adapter. Codex graded it sound.
2. **Production detection in an evidence probe** (`EspeakCliAdapter().status()`), not a lookalike like `shutil.which`. The probe then means what the product means.
3. **Stop on a red baseline and ask, rather than excuse it by habit.** D-132 cost one short ruling and fixed the pin, where Session 41 carried it.

### Patterns to DROP
1. **Putting a blocked row's evidence anywhere but `task.md`.** The validators read only `task.md`.

### Patterns to ADD
1. **Set `RECEIPTS_DIR` in every shell that runs a governance tool by hand**, not only in the gate and row runner.
2. **Allocate decision ids past the highest id in any open or recent session's records**, so ids stay unique across reflections.

### Calibration Adjustment
- Estimated time: one day (Session 41's Next Day Outline).
- Actual time: planning on 2026-10-26, and execution and closeout on 2026-10-27, including the D-132 pin commit.
- Adjusted estimate for similar MEUs: a one-MEU service residual with a rider, three quarters of a day, with a two-round plan-review budget (about 6.5M tokens per round here).

---

## Next Session Design Rules

```
RULE-1: A plan's [B] outcome puts its ### B-<id> evidence.v1 block in task.md and cites it from the row's task cell.
SOURCE: ECN-2 / D-133 (the plan named walkthrough.md; the blocked-row predicate reads task.md).
EXAMPLE: "B-10 block in walkthrough.md" → "### B-10 at the end of task.md; walkthrough.md mirrors the outcome".
```

```
RULE-2: Every governance tool invocation outside the gate sets RECEIPTS_DIR=C:/Temp/av-kit first.
SOURCE: ECN-3 (lint_task_contract.py and review_ledger.py begin each failed closed once when run by hand).
EXAMPLE: "uv run python tools/review_ledger.py begin ..." → "$env:RECEIPTS_DIR='C:/Temp/av-kit'; uv run python tools/review_ledger.py begin ...".
```

```
RULE-3: A Red for a defensive branch reaches that branch with valid inputs and changes one instance after construction, never a domain-validated replace.
SOURCE: Plan review F1 (dataclasses.replace raised ValidationError before the adapter ran).
EXAMPLE: "replace(variant, format='TFLite')" → "object.__setattr__(variant, 'format', 'TFLite') on a valid ONNX variant".
```

---

## Next Day Outline

1. Target: the 2026-10-17 grouping is delivered (Sessions 40, 41 and 42 approved). The next work comes from a fresh `/issue-triage` over the open issues, including `CAPTURE-HINT-TEST-PRESENCE-ONLY` and `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`.
2. Scaffold: build on the committed Session 42 tree once Mat commits it.
3. `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` needs Mat: install eSpeak NG 1.52, then run AC-74.11 in the dev app. Row 10 can then turn `[x]`.
4. Grouping D-101 (FFmpeg licence posture) still waits on Mat.
5. Bake in RULE-1 and RULE-2 for the next plan.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (a few hundred across planning, execution and closeout) |
| Time to first green test | 2026-10-27 (row 3, the `SIDELOAD_RECORD` Green) |
| Tests added | Python 937 → 957 collected (+20): `test_services.py`, `test_tts_device_resolution.py`, `test_tts_assets.py`, `test_tts_models.py`. TA-1 extended in place. |
| Codex findings | Plan review (Codex `gpt-6.1-sol`): R1 `changes_required` (F1 High blocking; F2 Medium; F3, F4 Low); R2 approved (F5 Low). Execution review: R1 approved, 0 findings, `intent_achieved: yes`. |
| Handoff Score (X/7) | 7/7 (all plan ACs present, a fresh passing gate, review approved) |
| Rule Adherence (%) | 95 |
| Prompt→commit time | 2026-10-26 → 2026-10-27 (review approval; commit pending the human) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Rows 2, 4 and 6 were Red, with `RED_TREE` refusing early product edits |
| No test expectation change without approval | AGENTS.md §Testing & TDD | Yes. TA-1 was in the approved plan; the `raising=False` to strict fixture repair is documented in the walkthrough and graded sound by Codex |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution |
| Baseline failures are not regressions; no retry or timeout added to pass a gate | AGENTS.md §Testing & TDD | Yes. Only AC-25.7 was excused; the adoption failures were fixed on Mat's ruling, not excused |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits, P0 | Yes. All work on `main`; `c34866b` was committed on Mat's ruling; the Session 42 commit draft is for Mat |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "0d9061a3-6961-4102-90b6-b67494b14797"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: rtk_token_optimized_commands, cited: true, influence: 1}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, plan_corrections, execution_session, tdd_implementation, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: [timestamp]
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/output-evidence-policy.md
    - .agent/schemas/reflection.v1.yaml
    - .agent/schemas/review-verdict.schema.v2.json
    - docs/build-plan/03-service-layer.md
    - .agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md
    - docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md
    - docs/execution/plans/2026-10-26-tts-sideload-load/task.md
decisive_rules:
  - P1:tests-before-production-code
  - P1:independent-review-no-self-approval
  - P1:baseline-failures-are-not-regressions
  - P0:never-commit-or-push-without-human-approval
  - P0:no-branches-or-worktrees
conflicts:
  - "The plan put the B-10 evidence block in walkthrough.md; the blocked-row validators read task.md (D-133, ECN-2)."
  - "The harness asked for a Co-Authored-By trailer on commits; the user's rule forbids AI attribution trailers, so the commit draft has none."
  - "A connected docs server asked for docs to be created there; the user's rule keeps deliverables as local repo files."
note: "S42 records sideloaded model files so a listed variant loads, logs every load failure as tts.load_failed, swaps stale spaCy paths; gate passed; execution review approved r1; eSpeak absent (B-10)."
slim_candidate: ["The handoff Codex Validation Report section, which stays pending while the review file and ledger hold the verdict"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 2, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 1, low: 2}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 1}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {weak_test: 1, contract_drift: 3, other: 1}
  verdicts: {changes_required: 1, approved: 2}
meu_work_classes: [correctness]
```
