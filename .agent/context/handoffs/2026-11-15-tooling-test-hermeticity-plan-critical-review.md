---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tth-plan-2026-11-15-tooling-test-hermeticity"
round: 1
---

# Critical Review: 2026-11-15-tooling-test-hermeticity

> **Review Mode**: `plan`
> **Verdict**: `approved`

## Intent Anchor

each tooling test in this scope reads only its own fixture, except one named test that is kept live on purpose. The registry tests resolve against a tracked synthetic registry in a temp registry home. The governance tests check a migrated tree whose rule-map pins and backlinks follow the bytes that tree holds, and one test still checks the tracked rule-map pins against the live instruction files (D-132). The dispatch placeholder arm builds its token at run time. A change to the machine registry, the live governance files or the instantiated project name then no longer reds them, and every assertion they make is unchanged.

Executing the plan and passing its rows would deliver this objective, with the explicitly accepted live checks and mitigated residual. No evidence-backed High or Critical delivery defect was found.

## Scope

Reviewed both complete plan files, the Session 76 grouping and issues, D-911 to D-918 and the expert-pass receipt, HDP's decision boundaries, the affected tests, OVERLAY, WRAPPER, VERIFIER and RULE_MAP, relevant machine resolver/module implementation, and the source scripts scheduled for copying. Applied PR-1 through PR-9 and the Materiality Gate. Process-paperwork findings were excluded as requested.

| Reviewed file | SHA-256 |
|---|---|
| implementation-plan.md | 8126fa00b22f18e0bf782b265f54d4905fb6bfe1d0666118856ca5436e65c141 |
| task.md | 608f6451b7a431e8c48ea3709e9e4cd2daecb50f3d8181206039e6f12478cb96 |

The plan folder currently contains those two files only. Row 0 explicitly creates the checkers; H1-2 creates the gate; row 2 creates FIXTURE and its generator. Their absence is expected unstarted work. This approval assesses their specified behavior and existing source helpers, not an implementation that already passes. Scratch probes wrote only under `C:/Temp/av-kit/tooling-test-hermeticity/review`. No test suite, dependency synchronization, provider or network request was run.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal and coverage

Accepted. The goal has explicit ACs and task rows:

| Goal clause | ACs | Rows |
|---|---|---|
| Synthetic registry validates and compiles in a temp home | AC-1, AC-2 | 0–2 |
| Four resolver functions and three wrapper cases ignore HOSTILE | AC-3, AC-4 | 1–2, H1-2 |
| Existing assertions and parametrize lists remain unchanged | AC-5 | 2, 4, H1-2 |
| Migrated pins and backlinks follow copied bytes; wrong pins still refuse | AC-6–AC-9 | 3–4 |
| One blocking test retains the tracked/live pin comparison | AC-14 | 4, H1-2 |
| Dispatch token survives instantiation and both assertions pass | AC-10 | 5–6 |
| Count, live routes and issue dispositions are checked | AC-11–AC-13 | 7–8, H1-2 |

The input-only rewiring preserves the assertions shown in current TEST_FILE. AST comparison of existing assertion nodes and decorators protects their semantics. It does not promise a frozen copy of machine tool code: TOOL_FILES are deliberately copied at run time. The two Session 86 live checks remain outside this change, as given; the plan states that residual rather than claiming complete suite isolation.

## Q2 — Fixture design and isolation

Accepted D-911. The eight-slug catalog equals OVERLAY's bound and forbidden slugs; the allowed fields contain no prices, URLs, paths or credentials. The sample is canonical LF JSON. The six catalog field names are an allowlist; the sample legitimately omits optional `efforts` for `composer-2.5-fast`. The proposed strict validator remains the runtime schema and semantic check, since overlay validation alone does not validate the registry (`resolve_model.py:523`, `:2311`, `:2356`). This introduces no new external disclosure requiring M-12 approval in the uncommitted session.

The explicit `AGENT_MODEL_REGISTRY` in `registry_home["env"]` wins over ambient HOSTILE through `run()`'s last merge (`TEST_FILE:65–74`). The copied module, registry and compiled temp overlay agree on one registry stamp. WRAPPER's explicit-file lookup precedes `AGENT_MODEL_REGISTRY_HOME` (`WRAPPER:554–563`), and replacing NEEDLE once directs its project lookup to that temp project. The bad-registry arm deliberately overrides the fixture with its absent path.

Independent scratch probes using the saved 3,804-byte sample and current TOOL_FILES passed strict validation without changing the registry, rejected a missing vendor, compiled the overlay with the fixture hash, resolved all seven binding cases, exercised both reviewer vendor outcomes, and refused unsupported harness and invented-slug inputs. All three wrapper cases returned their expected refusal with no fake-provider call.

Generator reproducibility remains an execution obligation: `make_fixture.py` does not exist yet. AC-1 expressly requires byte equality with its generated temp output. I accept that contract, not an unobserved generator result. Optional new resolver defaults are a disclosed limit, not a claim that strict validation detects every possible future semantic change.

## Q3 — Governance and dispatch mechanics

Accepted D-915 and AC-14. Closure uses VERIFIER's link grammar, skip rule and fragment split; absent targets stay absent. Pin replacement is confined to the two unique 64-hex values in the copied RULE_MAP. The preimage inventory, successor anchors, size checks, ownership checks and routing census still apply (`VERIFIER:150–300`). AC-8 corrupts a pin after construction, so rebinding cannot neutralize its refusal. AC-14 separately protects the tracked pins against live instruction bytes and remains blocking.

The independent static-oracle probe confirmed the chain: current copied tree passes; an appended instruction line gives the pin mismatch; a new missing link gives the backlink refusal; copying that target and rebinding restores success; corrupting the rebound pin restores the pin refusal. This invokes `static()` directly, not the full pytest fixture/source-git path. The specified AC-14 command correctly uses `read_bytes`, an exact occurrence assertion and `write_bytes`, preserving CRLF.

Accepted D-913. Runtime brace multiplication assembles the token without storing its literal, and a GUID base makes the directory assertion independent of old runs. AC-10 requires the two Write-TestResult lines and every unrelated line to equal BASE, BOM/CRLF preservation, and rejection of newly introduced census matches. The proposed assignments contain no routing or numeric-model pattern. The actual future source checker is not yet runnable; its scheduled negative fixtures cover these promises.

## Q4 — Red/Green proof, counts and live probe

Accepted. RED_IDS has 11 collected existing titles (7 binding, 2 vendor, 1 unsupported-harness and 1 same-vendor wrapper), plus the new AC-2 title. Removing `cursor-grok-4.6` makes resolver calls fail whole-overlay validation with `unknown_slug`; that defeats the existing expected outcome assertions, while the absent FIXTURE defeats AC-2 by assertion. The remaining refusal cases may already pass, as the plan explicitly says. The inherited `red-check.py` examines each failure block and the saved nonzero child exit; setup errors cannot substitute for those required assertion failures (`red-check.py:210–265`).

Governance Red has concrete pin/backlink diagnostics; AC-8 already passes because refusal is its expected result. AC-14 needs no artificial initial Red when live pins match, and has its own appended-byte negative. Green retains the assertions and parametrize lists. Static AST inspection confirms 16 existing registry cases and 12 governance cases. The five added unparametrized tests are AC-2, AC-6, AC-7, AC-8 and AC-14, so AC-11's base + 5 is correct.

AC-12 explicitly covers the seven BASE-derived bindings, reviewer resolution with Anthropic, refusal with OpenAI, and `--check-compiled`. It closes the expert pass's missing live-route coverage. S6 correctly prevents silently repairing machine state. No live-probe, Red/Green pytest run, count checker or full session gate was claimed executed in this review; those remain required execution evidence.

## Q5 — Order, baselines, writes and registers

Accepted D-918. Row 0 captures actual working bytes as BASE and hashes shared dirty paths, independently of HEAD. S2 measures encoding, NEEDLE and pin occurrence counts rather than requiring a clean tree. S4's specified content comparisons preserve Session 75's uncommitted work; permitted HEAD movement still requires the earlier paths and bytes. `baseline-api.json` and H1-4 compare the API subtree to row 0, so Session 75's pre-existing API edits do not defeat the skip basis. The identity helper can conservatively require a gate rerun if HEAD moves; it does not turn those earlier edits into this session's output.

Independent byte inspection matched TEST_FILE's 1,072 CRLF lines/no BOM and DISPATCH_TEST's 1,133 CRLF lines/UTF-8 BOM. WRAPPER's NEEDLE and each tracked instruction pin occurred exactly once; both live hashes matched the tracked pins. Checks against BASE and explicit byte writes protect the existing mixed-ending WRAPPER and CRLF RULE_MAP copies.

Declared source/register edits are within the six listed files; other writes are the plan and closeout artifacts, scratch outputs and ordinary effects of explicitly planned dependency/test commands. TOOL_FILES and machine registry inputs are read/copied, never overwritten. The existing register resolver calls the issue-triage model, holds an exclusive Windows write handle, checks the expected content hash and parsed-field allowlist, then rendering uses `issue_triage.py`. It supports `mitigated` as well as `resolved`; the two resolved issues and the registry residual are explicitly distinguished in AC-13.

The handed decisions have no demonstrated additional non-handable M hit: assertions remain intact, the blocking pin signal remains, destructive cleanup is left optional for Mat, and no commit/push is scheduled. The latest trusted instruction supplies execution authorization after approval; generic task wording about awaiting another message does not supersede it. This session still ends uncommitted with a message draft.

## Checklist Results

Results concern plan readiness. Manual observer: `codex-independent-reviewer`; manual exits are null.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare both complete files, goal, ACs and rows | null | Same scope and registry → governance → dispatch → live/register sequence |
| PR-2 Not started | pass | Inspect plan inventory, current affected files and task statuses | null | Two planning files; implementation rows unchecked; fixture/generator absent |
| PR-3 Task contracts | pass | Inspect row owners, deliverables, dependencies and validation commands | null | Explicit creation of currently absent helpers |
| PR-4 Validation realism | pass | Trace planned observations through resolver/module, wrapper and verifier | null | Scratch positives and negatives support the mechanics |
| PR-5 Source backing | pass | Compare grouping, issues, D-132, expert pass and HDP with choices | null | Scope and accepted exceptions preserved |
| PR-6 Corrections readiness | pass | Inspect explicit handoff and review targets | null | One non-MEU scope; round 1 |
| PR-7 Scope discipline | pass | Compare exclusions with grouping and goal | null | No required goal behavior disguised as deferred work |
| PR-8 Controls and negatives | pass | Inspect assertion preservation, Red parser, pin mutation and register guard | null | No demonstrated material false-pass |
| PR-9 Single-statement discipline | pass | Compare named contracts, ACs and task references | null | Governing behavior is unambiguous |
| Independent mechanics probe | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/tooling-test-hermeticity/review/probe.py` | 0 | Strict/compile/routes and governance positive/negative probes passed; watched repository bytes unchanged |
| Wrapper refusals | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/tooling-test-hermeticity/review/wrapper-probe.py` | 0 | Three expected refusals; provider_called=False for each |
| Actual implementation suites and future checker selftests | n/a | Not run under read-only plan review | null | Must run during execution after the scheduled files exist |

```json
{"schema_version":"evidence.v1","check_id":"tth-review-source-trace","procedure":"Read both complete planning files and trace AC-1 through AC-14 against current affected tests, resolver/module, wrapper, verifier, source checker scripts, grouping, issue records and HDP; inspect task status and scheduled file creation.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 76 plan readiness","phase":"plan","exit_code":null,"result":"pass","tested_state":"plan-sha256:8126fa00b22f18e0bf782b265f54d4905fb6bfe1d0666118856ca5436e65c141;task-sha256:608f6451b7a431e8c48ea3709e9e4cd2daecb50f3d8181206039e6f12478cb96","output":"14 ACs cover the goal; registry issue remains mitigated; existing assertions and parametrize lists must remain; new scripts and fixture are scheduled implementation, not existing passes. No High/Critical delivery defect demonstrated.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"tth-review-mechanics","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/tooling-test-hermeticity/review/probe.py","cwd":"P:/av-kit","scope":"scratch registry home and direct governance static oracle; saved synthetic sample with current machine TOOL_FILES","phase":"plan","exit_code":0,"result":"pass","tested_state":"plan-sha256:8126fa00b22f18e0bf782b265f54d4905fb6bfe1d0666118856ca5436e65c141;task-sha256:608f6451b7a431e8c48ea3709e9e4cd2daecb50f3d8181206039e6f12478cb96","output":"existing registry cases=16 PASS; existing governance cases=12 PASS; binding cases=7 PASS; strict=yes compiled=unchecked; fixture unchanged; missing vendor refused; temp overlay compiles and stamp equals fixture SHA; seven routes and both reviewer vendor cases pass; unsupported harness and invented slug refused; live instruction pins match; governance static positive, appended-byte negative, missing-backlink negative, rebound positive and wrong-pin negative pass; watched repository files unchanged.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"tth-review-wrapper-refusals","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/tooling-test-hermeticity/review/wrapper-probe.py","cwd":"P:/av-kit","scope":"scratch WRAPPER copy, temp project and fixture registry; fake provider sentinel","phase":"plan","exit_code":0,"result":"pass","tested_state":"plan-sha256:8126fa00b22f18e0bf782b265f54d4905fb6bfe1d0666118856ca5436e65c141;task-sha256:608f6451b7a431e8c48ea3709e9e4cd2daecb50f3d8181206039e6f12478cb96","output":"same-vendor exit=1 vendor_diversity_violation provider_called=False; unknown-class exit=1 unknown_class provider_called=False; bad-registry exit=1 registry_not_found provider_called=False. 3/3 expected refusals; no provider invoked.","fresh":true}
```

## Verdict

`approved` — The plan would deliver the registered intent. No corrective finding is required before execution. Execute the scheduled checker/selftest and Red/Green obligations; retain AC-14, the Session 86 live checks, the mitigated registry residual and the uncommitted closeout boundary.
