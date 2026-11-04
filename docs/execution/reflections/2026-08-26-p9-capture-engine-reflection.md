---
date: "2026-08-27"
project: "p9-capture-engine"
meus: ["MEU-34", "MEU-35", "MEU-36"]
plan_source: "docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md"
template_version: "2.0"
---

# 2026-08-27 Meta-Reflection

> **Date**: 2026-08-27
> **MEU(s) Completed**: MEU-34, MEU-35, MEU-36
> **Plan Source**: docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   Exec r1 Highs after a green 302-test gate. Scan treated `{stem}.annotated.png` as a second original. `complete_request` registered the PNG before validating the request, so unknown/cancelled/expired IDs left orphan `capture_shots` rows. `CaptureRequest(Completed, shot_id=None)` constructed cleanly. All three were invisible to the first AC suite.

2. **What instructions were ambiguous?**
   H1-4 hashed the entire `packages/api` tree including `__pycache__`, so a skip-G8 check failed after pytest recompiled bytecode with no source drift (27 `.py` hashes identical). H1-7 required `prompt_temp.txt` while `Invoke-CodexDispatch.ps1` deleted it after a successful run.

3. **What instructions were unnecessary?**
   Packing MEU-37–39, Session 8c / MEU-27, OpenAPI `-o`, live unattended mss of the developer desktop, and adding `"captures"` to `QUEUE_NAMES`.

4. **What was missing?**
   Scan exclusion for `ANNOTATED_SUFFIX`. One-UoW validate-then-upsert on `complete_request`. Domain invariant: Completed requires `shot_id`. Live `apply_migrations` twice and UoW save/delete (F4). Wrapper keep of `prompt_temp.txt` for dispatch provenance.

5. **What did you do that wasn't in the prompt?**
   After plan r5 `approved` (harness.local `reviewer-auto`) and user `(a)` / `continue`, executed MEU-34–36 TDD, H1, exec r1 F1–F4, r2, and H2 in one pass. Filtered OpenAPI skip to source files. Restored r2 `prompt_temp.txt` from the PromptFile copy and stopped the wrapper from deleting it.

### Quality Signal Log

6. **Which tests caught real bugs?**
   Codex r1 real tmp-SQLite + Pillow probes: bake then scan listed `original.annotated.png`; unknown `complete_request` left `orphan.png`; Completed with `shot_id=None` constructed. After the fix, `test_ac_36_1_scan_skips_annotated_derivative`, `test_ac_36_8_failed_complete_does_not_orphan_shot` (unknown/cancelled/expired), `test_ac_34_5` negative, and `test_ac_36_9_real_sqlite_bake_scan_one_original` locked those paths.

7. **Which tests were trivially obvious?**
   First-pass AC-36.1 seeding only `a.png` / `b.gif` / nested PNG. AC-36.8 happy-path complete/cancel without a failed-complete side-effect assertion. AC-34.5 constructing only the valid Completed form.

8. **Did pyright/ruff catch anything meaningful?**
   No. Both stayed 0 on the correction set. They did not catch F1–F3.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   Named-set locks (no queue name `captures`, mss `monitors[0]`, `BLACK_LUM_MAX`, sidecar version, local `TIMESTAMP_FORMAT`, no service `mkdir`) were precise. Bake→scan identity and complete-request atomicity were in the spec/plan but not forced as negative oracles until Codex.

10. **Was the handoff template right-sized?**
    Adequate. Completeness claims for scan/complete outran the lifecycle until r1. Corrections Applied on the rolling review was the right place for F1–F4 citations.

11. **How many tool calls did this session take?**
    High hundreds across plan r5, MEU-34–36 TDD, H1, exec r1 F1–F4, r2, H2.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    `fresh_worker: none` — compact_continue. Independent review: Codex GPT-5.6-sol FullAccess (plan r5 `approved`, exec r1 `changes_required` F1–F4, exec r2 `approved`). No builder dispatch.

---

## Pattern Extraction

### Patterns to KEEP
1. Named-set ownership of `SCAN_EXTENSIONS`, `ANNOTATED_SUFFIX`, `REQUEST_TTL_S`, `HUB_NEXT_AFTER`, `API_BASELINE`.
2. Fake mss in unit tests; real Pillow probe/bake + tmp-SQLite for G29 and bake→scan.
3. Dispatch `-DispatchId` into rolling-review frontmatter; `assert-exec-review-dispatch.ps1` binds `status.json` + `final.md`.

### Patterns to DROP
1. Hashing `__pycache__` / `*.pyc` as an OpenAPI/API-tree skip oracle.
2. Deleting `prompt_temp.txt` after a successful Codex dispatch when a later assert requires it.
3. `complete_request` calling `register_shot` in a separate UoW before request validation.
4. Inbox scan that accepts every `.png`, including deterministic `{stem}.annotated.png` derivatives.

### Patterns to ADD
1. Skip `ANNOTATED_SUFFIX` in `scan_inbox` before probe/upsert; assert bake→scan leaves one original row.
2. Validate the capture request, then upsert the shot, then complete — in one UoW; assert unknown/cancelled/expired leave `capture_shots` empty.
3. `CaptureRequest` Completed requires `shot_id`; Pending may be `None`.
4. Compare API-tree skip on source files only; keep `prompt_temp.txt` for provenance.

### Calibration Adjustment
- Estimated time: one Session 16 TDD + one exec pass
- Actual time: plan r5 + TDD + exec r1 F1–F4 + r2
- Adjusted estimate: write bake→scan and failed-complete negatives in Red, not after review

---

## Next Session Design Rules

```
RULE-1: Deterministic derivative files in the inbox (`ANNOTATED_SUFFIX`) are not originals; prove with bake then scan.
SOURCE: exec r1 F1 (AC-36.1 / AC-36.9)
EXAMPLE: scan_inbox skips names ending `.annotated.png`; test asserts ['original.png']
```

```
RULE-2: Mutating complete/register of an interactive request is one UoW; failed complete must not insert a shot.
SOURCE: exec r1 F2 (AC-36.8 / one-UoW lock)
EXAMPLE: unknown UUID + valid PNG → NotFoundError and capture_shots == []
```

```
RULE-3: Status/optional-field invariants live in the domain constructor, not only the happy-path test.
SOURCE: exec r1 F3 (AC-34.5 / spec shot_id yes when Completed)
EXAMPLE: CaptureRequest(Completed, shot_id=None) raises ValidationError
```

---

## Next Day Outline

1. `/create-plan p9-capture-api-mcp` (MEU-37–38). Do not pack MEU-39.
2. Session 8c `p6-gui-console-polish` (MEU-27) stays human-gated — do not start unless Mat asks
3. Do not invent MEU IDs; OpenAPI regen is MEU-37 (G8)
4. Human commit gate: draft only at `C:/Temp/av-kit/commit-draft-p9-capture-engine.txt`

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | high hundreds (plan r5 + MEU-34–36 TDD + H1 + exec r1/r2 + H2) |
| Time to first green test | Red oracles 13/14/14; first engine gate 302 passed; post-r1 305 passed |
| Tests added | AC-34.1–13, AC-35.1–14, AC-36.1–14 plus r1 F1–F4 regressions |
| Codex findings | plan r5 0 High at approval; exec r1 F1–F3 High + F4 Medium; r2 0 structured findings |
| Handoff Score (X/7) | 7/7 after r2 (markers + AC set + runtime citations) |
| Rule Adherence (%) | ~86 (P0 redirect, no self-review, no auto-commit; skip-oracle pycache and prompt_temp deletion until r2) |
| Prompt→commit time | no commit (human gate) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Redirect every shell stream to C:/Temp/av-kit | AGENTS.md §P0 | Yes |
| Never self-review; dispatch Codex | AGENTS.md §Execution Contract | Yes |
| Never auto-commit | AGENTS.md §Commits | Yes |
| Anti-premature-stop: H1→review→H2 one pass | AGENTS.md §Execution Contract | Yes |
| Tests first; do not neutralize | AGENTS.md §TDD | Yes (r1 added negatives; existing asserts unchanged) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "2386137e-1b7d-495c-a5b1-da0610d2062a"
  task_class: tdd
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: execution_contract
    cited: true
    influence: 3
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: dual_agent_workflow
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 2
  - id: windows_shell_powershell
    cited: true
    influence: 2
  - id: instruction_coverage_reflection
    cited: true
    influence: 2
  - id: session_discipline
    cited: true
    influence: 2
  - id: code_quality
    cited: true
    influence: 1
  - id: artifact_naming_convention
    cited: true
    influence: 2
  - id: pre_handoff_self_review_mandatory
    cited: true
    influence: 1
  - id: communication_policy
    cited: true
    influence: 1
  - id: rtk_token_optimized_commands
    cited: true
    influence: 1
loaded:
  workflows:
    - create_plan
    - execution_critical_review
    - execution_corrections
  roles:
    - orchestrator
    - coder
    - tester
  skills:
    - terminal_preflight
    - quality_gate
    - completion_preflight
    - cli_dispatch
    - timestamp
  refs:
    - AGENTS.md
    - .agent/context/harness.local.md
    - .agent/context/grouping/2026-08-26-p9-screenshot-capture-session-grouping.md
    - docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md
    - docs/build-plan/09-screenshot-capture.md
review_churn:
  rounds_to_approval:
    plan: 5
    execution: 2
  findings_per_round:
    - { round: 1, critical: 0, high: 3, medium: 1, low: 0 }
    - { round: 2, critical: 0, high: 0, medium: 0, low: 0 }
  churned_findings: 0
  finding_categories:
    contract_drift: 3
    weak_test: 1
  verdicts:
    changes_required: 1
    approved: 1
meu_work_classes:
  - correctness
  - correctness
  - correctness
decisive_rules:
  - "P0:redirect-to-file"
  - "P1:independent-codex-review"
  - "P1:tests-first-no-neutralize"
  - "P1:anti-premature-stop-H1-review-H2"
  - "P2:session-16-meu-34-36-only"
conflicts:
  - "create-plan.md Cursor default plan_to_exec_gate=human vs harness.local.md reviewer-auto; harness.local won after plan r5 approved"
  - "Invoke-CodexDispatch CompressOnSuccess deleted prompt_temp.txt vs assert-exec-review-dispatch.ps1 requiring it; wrapper now keeps the file"
  - "assert-openapi-skip hashed __pycache__ bytecode vs 'no API_TREE edits'; skip now compares source files only"
slim_candidate:
  - dual_agent_workflow
  - rtk_token_optimized_commands
overthinking_observed: false
note: "Exec r1 Highs were real; prompt_temp deletion and pycache hashing were harness false-fails, not product defects."
```
