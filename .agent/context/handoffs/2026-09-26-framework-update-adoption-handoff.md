---
date: "2026-09-26"
project: "2026-09-26-framework-update-adoption"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-26-framework-update-adoption/implementation-plan.md"
build_plan_section: "non-product governance"
agent: "Codex implementor (OpenAI)"
reviewer: "Codex CLI GPT-6 Astra xhigh; USER_EXPLICIT same-vendor exception; approved Round 2 after Round 1 corrections"
predecessor: "2026-09-26-framework-update-adoption-planning-handoff.md"
---

# Handoff: framework update adoption implementation

## Scope

Selective adoption from pinned clean source `003929c1cafa83359f0695415bbc06074a35f92e`: executable evidence/task/closeout checks, staged validation, add-only local model classes, ledger/v2 review pipeline, compact governance. Non-product `meus: []`; no product/SSOT changes. Predecessor: [planning handoff](2026-09-26-framework-update-adoption-planning-handoff.md). Independent plan Round 3 approved; direct user `execute implementation` authorized execution. Independent Round 2 approved; all H1/H2 rows and required closeout artifacts are complete.

## Acceptance Criteria

All tests below are real CLI/contract integration cases in `tests/tooling/test_framework_adoption.py`; helper paths mean the plan's `checks/verify_adoption.py`.

| AC | Type | Description / implementation reference | Source | Test(s) | Status |
|---|---|---|---|---|---|
| AC-1 | integration | Pinned source, protected/preimage allowlist; helper:94 | Human-approved scope; Local Canon PROFILE | `test_verifier_bootstrap_*`; live final gate | Verified |
| AC-2 | integration | Durable evidence and actual task/handoff validation; tools/durable_evidence.py:182, tools/validate_closeout_artifacts.py:337 | Local Canon templates/tools | `test_evidence_contract_real_cli_selftests`, `test_evidence_contract_missing_ac_rejected` | Verified |
| AC-3 | integration | Schema-aware normalization preserves raw bytes/manual null; tools/adapt_output_schema.py | Local Canon pipeline | `test_review_pipeline_raw_bytes_and_null_semantics`; tools/tests/test_review_output_pipeline.py | Verified |
| AC-4 | integration | Actual D6 commands, static→targeted→fresh full with input identity; commands.md:188, helper:468 | Local Canon PROFILE/package manifests | `test_validation_stages_stop_and_bind_inputs`; full gate below | Verified; independently approved Round 2 |
| AC-5 | integration | Project overlay preserves bindings/flags; wrappers defaults ps1:26/sh:25; model-routing.md:17 | Local Canon harness/PROFILE; upstream | `test_registry_contract_*`, `test_review_pipeline_wrapper_refuses_before_provider` | Verified; independently approved Round 2 |
| AC-6 | integration | Ledger exact target/intent/schema/limits/usage; tools/review_ledger.py:735,803 | Local Canon upstream ledger/vocabulary | `test_review_pipeline_ledger_adversarial_selftest`, `test_review_pipeline_ledger_binds_exact_plan`, `test_review_pipeline_valid_continuation_preserves_approval` | Verified |
| AC-7 | integration | Legacy v1 checker intact, v2 exact-target approval; closeout validator:458, helper:302 | Local Canon legacy and new review checks | `test_legacy_review_checker_remains_compatible`, `test_review_pipeline_target_bound_approval`, `test_review_pipeline_complete_approval_tampering` | Verified |
| AC-8 | integration | Compact roots, all registry IDs/rules/templates and routing census; helper:147,203 | Local Canon deletion budget/PROFILE; upstream | `test_review_pipeline_governance_static_oracles`, `test_governance_preservation_and_routing_inventory` | Verified |
| AC-9 | integration | Fresh H1 gates/handoff complete; independent review and H2 still required; helper:428 | Local Canon H1→review→H2 | `test_review_pipeline_closeout_requires_real_completion`, `test_review_pipeline_correlated_approval_positive`; Round 1 R1-F3 and dependent H2 outstanding | Verified; review and H2 complete |

<!-- CACHE BOUNDARY -->

## Evidence

### FAIL_TO_PASS

| Test | Red output | Green output | File:Line |
|---|---|---|---|
| Initial 45 migration cases | 44 failed, 1 passed; intended absent contracts, not collection errors | Expanded suite 64 passed | tests/tooling/test_framework_adoption.py:85 |
| Exact ledger target | plan.md.bak accepted incorrectly: 1 failed, 1 passed | Both target cases pass | same file:626; tools/review_ledger.py:847 |
| Rule/routing inventory | 4 failed, 1 passed: invalid inputs reported static success | All ten static oracles pass | same file:372; helper:203 |
| Approval ledger target | Wrong ledger plan still reported approval: 1 failed | Target corruption rejected | same file:695; helper:302 |
| Valid human continuation fixture | REFUSE: invalid human continuation; 1 failed | Real ledger continue accepted, history retained | same file:595; helper:302 |

Only two original registry diagnostic assertions changed, with the user's explicit approval recorded in registry-readiness.md; all other changes to existing tests were setup/formatting, not weakened assertions. New cases cover discovered defects. Detailed boundary history is in [execution evidence](../../../docs/execution/plans/2026-09-26-framework-update-adoption/execution-evidence.md).

### Commands Executed

The 15 exact gate commands, preserved exits and decisive outputs are embedded in execution-evidence.md under Round 1 corrections. RTK/P0 process receipts are retained; the prior gate was archived before refreshing. Current full evidence:

```json
{"schema_version": "evidence.v1", "check_id": "round2-fresh-full-gate", "command": "$env:RECEIPTS_DIR='C:/Temp/av-kit'; $env:AGENT_MODEL_REGISTRY_HOME='P:/.agent'; $env:PYTHONIOENCODING='utf-8'; rtk proxy uv run python docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py stages --stage-config C:/Temp/av-kit/framework-adopt-gate-config.json --output C:/Temp/av-kit/framework-adopt-gate-result.json *> C:/Temp/av-kit/astra-r2-full-gate.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/astra-r2-full-gate.txt -Tail 40; exit $code", "cwd": "P:/av-kit", "scope": "complete scoped adoption gate after R1 corrections; 993 file inputs plus live runtime/task identity", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "f80ab222080e34641d0ed90937a2118c31b2e3ba7b31be562424880fa8d95e72", "output": "Ruff clean; Pyright 0 errors/warnings; 26 targeted passed; 91 migration passed; 21 pipeline passed and 11 subtests; linter 50/0 failures; closeout 59/0; ledger 105/0; wrapper 27 PASS/0 FAIL/1 inapplicable; physical path 3 measured/0 failures/1 macOS-only unmeasured; 21 task rows checked; static/final checks pass; 904 protected hashes unchanged; SSOT 61 MEUs/12 phases match.", "fresh": true}
```

### Quality Gate Results

Ruff clean; Pyright 0 errors/warnings; 26 targeted passed; 91 migration passed; 21 pipeline passed and 11 subtests; linter 50/0 failures; closeout 59/0; ledger 105/0; wrapper 27 PASS/0 FAIL/1 inapplicable; physical path 3 measured/0 failures/1 macOS-only unmeasured; 21 task rows checked; static/final checks pass; 904 protected hashes unchanged; SSOT 61 MEUs/12 phases match.

Product/Electron/OpenAPI suites remain an explicit scope skip: no product or shared product configuration changed. Runtime identity now measures the actual process and selected registry, executable bytes, dependency versions and normalized task inputs on every check; a saved JSON description cannot establish freshness. Unknown runtime inputs refuse reuse. Earlier green evidence is historical and does not substitute for this corrected full gate.

## Changed Files

The complete per-file delta inventory (including all modified/new paths, pre/postimage identities and compact diff excerpts) is in execution-evidence.md §Changed-file delta inventory. It is relative to the captured starting worktree, preserving earlier user changes.

| File family | Action | Summary |
|---|---|---|
| tools/durable_evidence.py, lint_task_contract.py, validate_closeout_artifacts.py, validate_json_schema.py | add/modify | Executable evidence, task and closeout validation |
| tools/review_ledger.py, adapt_output_schema.py, Invoke-CodexDispatch.ps1/.sh; review schema/vocabulary | add/modify | Exact target/intent/usage binding and preserved raw review output |
| tools/tests/, tests/tooling/test_framework_adoption.py; cli-dispatch fixture tests | add/modify | Positive/adversarial provider-free coverage |
| .agent/model-registry.local.yaml/.json; four .cursor/.claude agent definitions | add/modify | Five local classes; existing loader fields/readonly limits retained |
| .agent/docs/, workflows/, skills/, runtime/templates | modify | Current D6 commands, class routing, review and evidence lifecycle; five template pairs synchronized |
| AGENTS.md, GUARDRAILS.md, CLAUDE.md, registry.yaml, PROJECT-PROFILE.md | modify | Compact local controls, host hierarchy, current routing and D6 |
| Current adoption plan folder and this handoff | add/modify | Immutable baseline, mappings/census, test evidence, pending human review |

```diff
- substring plan target acceptance / unbound review ledger
+ resolved exact target in ledger begin/record and approval correlation
- hard-coded live model prose and unconfigured reviewer fallbacks
+ avkit classes, project overlay, vendor-distinct reviewer or Mat
- long duplicated root rules and receipt-only closeout claims
+ preserved rule mapping, compact entrypoints and durable evidence
```

## Codex Validation Report

Independent Codex CLI GPT-6 Astra/xhigh **Round 2: approved**. The [rolling report](2026-09-26-framework-update-adoption-implementation-critical-review.md) retains original findings and independent correction dispositions. The wrapper recorded the genuine verdict exactly once. V19 correlates target, plan hash, report/raw/status hashes, ledger intent/round/author separation and the exact user-authorized same-vendor exception. No implementer-authored approved verdict was created.

### Recheck Protocol

No further review is pending for this completed target. Any future relevant input change invalidates the current evidence and requires its applicable validation/review. The one-loop same-vendor exception does not change standing routing policy.

## Corrections Applied (2026-09-26)

| Finding | Implementer correction | Evidence |
|---|---|---|
| R1-F1 / AC-4 | Live runtime and normalized task contract recomputed before/after/reuse | Changed environment/registry/task validation refuse; unchanged/task status only pass |
| R1-F2 / AC-5 | Planner and registered D6 command use local class allowlist; census also checks generic callers | Three local classes pass; global builder/coordinator and unknown class refuse; two planted global callers fail static |
| R1-F3 / AC-9 | Approved verdict requires zero blocking findings and consistent actual total count | Complete real-ledger approval with one Low finding passes; wrong count refuses |
| R1-F4 / AC-8 | Setup link resolves to existing local routing instructions | .agent/docs/model-delegation.md points to model-routing.md |
| User-authorized exception | Exact quote/hash/target/loop/model/effort/vendors and real successful dispatch required | 13 positive/refusal cases; ordinary vendor policy unchanged |

Round 2 regression Red: 11 failed/14 passed; additional generic census Red: 2 failed. Green: full migration suite 91 passed. No existing assertion was weakened. Test-only type/format setup fixes preserved expected values. These are implementer correction claims awaiting independent recheck, not self-approval.

## Deferred Items

No required adoption work is deferred. All 21 task rows are complete, the independent review is approved and H2 artifacts are validated. R2-F1 remains a Low nonblocking observation: the wrapper fixture's logical-name replacement can alter a lowercase av-kit temporary parent path. The rolling report records the reproduction and recommended follow-up; no fix or portable-fixture certification is claimed. No product/Electron behavior is certified by this governance-only scope. No commit/push is authorized or performed.

## History

| Event | Date | Agent | Detail |
|---|---|---|---|
| Execution authorized | 2026-09-26 | User | execute implementation after independent plan Round 3 |
| Assertion corrections authorized | 2026-09-26 | User | approved only the two documented diagnostic assertions |
| H1 implementation/validation | 2026-09-26 | Codex implementor | WP-0–5 and fresh scoped gate passed |
| Human review package prepared | 2026-09-26 | Codex implementor | Mat review pending; H2 not started |

Template/exemplar read before writing: current handoff template 2.2 and latest peer 2026-09-26-p11-queue-pages-planning-handoff.md. Concurrent peer artifacts/current-focus remain protected.

## Independent review update — Round 1

The user directly authorized a separate Codex CLI GPT-6 Astra/xhigh review. It returned changes_required: R1-F1 live-environment freshness (AC-4), R1-F2 remaining global class callers (AC-5), R1-F3 rejection of supported nonblocking approval findings (AC-9), plus R1-F4 a broken setup-document link. The reviewer verified 904 protected hashes unchanged. Sandbox uv-cache/Git-ownership refusals limited some independent reruns and are disclosed in the [canonical reviewer-authored report](2026-09-26-framework-update-adoption-implementation-critical-review.md). Earlier green suites remain historical execution evidence, not proof that these newly reproduced cases pass.

Dispatch and child exit 0; real v2 verdict recorded exactly once, round 1/6. That initial reservation refusal was subsequently relieved by the direct user message `second round is approved`; +1,209,268 was recorded by Mat, preserving all history. Corrections above are applied and freshly validated; independent Round 2 and H2 remain pending.

## Final closeout

All 21 task rows are complete. Reflection and its Instruction Coverage YAML, preserved-prefix metrics row, commit-message draft and exact approval binding passed their registered checks. The fresh full gate remains bound to f80ab222080e34641d0ed90937a2118c31b2e3ba7b31be562424880fa8d95e72. Current-focus and concurrent Session 24 state remained protected.
