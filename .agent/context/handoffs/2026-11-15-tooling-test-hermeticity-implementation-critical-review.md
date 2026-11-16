---
date: "2026-11-15"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tth-execution-2026-11-15-tooling-test-hermeticity"
round: 1
---

# Critical Review: 2026-11-15-tooling-test-hermeticity

> **Review Mode:** `execution`  
> **Verdict:** `approved` — the delivered changes achieve the registered intent; no findings.

## Intent Anchor

each tooling test in this scope reads only its own fixture, except one named test that is kept live on purpose. The registry tests resolve against a tracked synthetic registry in a temp registry home. The governance tests check a migrated tree whose rule-map pins and backlinks follow the bytes that tree holds, and one test still checks the tracked rule-map pins against the live instruction files (D-132). The dispatch placeholder arm builds its token at run time. A change to the machine registry, the live governance files or the instantiated project name then no longer reds them, and every assertion they make is unchanged.

**Intent achieved: yes.**

## Scope

Independent Codex review of Anthropic/Claude Code's Session 76 implementation, no MEU, on `main`, HEAD `3397e78d7342d73e99dde3b43244a55cd6be7e87`. Read the execution-review workflow, implementation plan, task and evidence handoff before reviewing the scoped delta. Compared TEST_FILE and DISPATCH_TEST with BASE, and verified both BASE SHA-256 values against `baseline-scope.json`. Read both new fixture files completely. Compared the issue register with the row-0 `register-before-resolve.yaml`, whose SHA-256 also matches the baseline anchor. Inspected the resolver/module lookup, OVERLAY, WRAPPER, VERIFIER and relevant gate/checker code.

Applied IR and relevant DR checks to delivered behavior and evidence. Approved decisions D-911 through D-918 were held fixed. D-919 and D-920 were assessed against their actual diagnostics. Session 75's implementation and Sessions 77–83 plans were excluded; the latest Session 75 review supplied only the report exemplar. H1 review-state collection and H2 remain coordinator work after this verdict, not missing implementation.

The reviewer wrote only under `C:/Temp/av-kit`. No repository or machine-registry file was edited; no commit, stage, stash, revert, push or network request was made. The coordinator publishes this report to the canonical review path.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Registry hermeticity (AC-1 to AC-5)

Accepted. `tests/tooling/test_framework_adoption.py:93–129` copies exactly TOOL_FILES from MACHINE_TOOLS, copies FIXTURE into that temp home, strictly validates that copy, and compiles the byte-copied OVERLAY in a temp project. The environment merge at `:70–78` gives the explicit fixture `AGENT_MODEL_REGISTRY` precedence over HOSTILE. The resolver and PowerShell module select that existing explicit file before their machine fallback. No registry-test path reads the machine registry or tracked compiled overlay.

The four resolver functions and wrapper function use this home for all 16 existing cases. `fixture_wrapper` at `:155–165` requires NEEDLE exactly once and performs a byte replacement only in its temp WRAPPER copy. Wrapper assertions at `:1030–1038` still require nonzero exit, an untouched fake-provider marker and the specific refusal; `bad-registry` remains `registry_not_found`. An independent HOSTILE run passed all 17 selected cases, including new AC-2.

FIXTURE is 3,804 bytes, SHA-256 `782741c0b26610b5bed82b6c7afedd78ceca9c65fa4b2dcb543803c00cf7dfde`, with eight catalog slugs and the one synthetic coordinator class. Independent `fixture-check.py` execution confirmed strict validity, unchanged validated bytes, byte-identical regeneration, YAML-subset parser agreement with `yaml.safe_load`, and the independent builder's agreement. The fixture has no prices, URLs, paths or slugs outside OVERLAY's bound/forbidden set; its permitted qualitative `price_band` fields remain.

This acceptance concerns registry data isolation. TOOL_FILES and OVERLAY intentionally remain inputs, and the generator/upkeep checker intentionally reads the live registry. It does not claim independence from changes to resolver code or overlay contracts. The two HDP live checks remain outside this change under D-912.

## Q2 — Governance fixture and live drift signal (AC-6 to AC-9, AC-14)

Accepted. `build_migrated_tree` at `:443–473` copies the manifest's bytes, adds the instruction files' one-level backlink targets and rebinds the copied RULE_MAP before returning the tree. The byte replacement at `:519–529` requires each old pin exactly once, changes only those copied pin values and hashes the copied instruction bytes. VERIFIER and the tracked RULE_MAP are untouched. The closure at `:487–509` leaves a nonexistent target missing, allowing VERIFIER to refuse it.

The original mutations run after fixture construction; they cannot be repaired by this rebind. The independent 16-case governance selection passed: the 12 existing cases, including `backlink` and `rule-map`, plus AC-6, AC-7, AC-8 and AC-14. The governance Red receipts contain the intended `rule map identity mismatch: AGENTS.md` and `broken instruction backlink: .agent/docs/fixture-new-policy.md` assertions, rather than setup errors.

`test_ac_14_tracked_rule_map_pin_matches_live_instructions` at `:635–645` calls `tracked_pin_mismatches(ROOT)` against the tracked RULE_MAP and real files, before its temp negative. That call never rebinds. Beyond its AGENTS.md negative, the reviewer separately appended one byte to each instruction file in scratch copies: each produced exactly one named mismatch. Executing each emitted Python rebind payload in its scratch tree succeeded and cleared the mismatch. Thus real instruction-byte/pin divergence cannot disappear through fixture rebinding; D-132's live signal survives with a usable command.

No claim is made that the live-pin test semantically reviews a human-approved rebind. As before, the message directs the human to check rule coverage first; VERIFIER retains its mapping, successor, registry and census checks.

## Q3 — Dispatch placeholder arm (AC-10)

Accepted. DISPATCH_TEST at `:560–574` constructs the braces and `PROJECT_NAME` separately at run time, inserts the resulting token below a fresh GUID temp base, and reaches the unchanged `Get-OutputDir` placeholder guard. The second result still checks that the fresh base was never created. The real-directory positive arm remains alongside these negatives.

The independent source checker passed: UTF-8 BOM and all-line CRLF retained; seven changed comment/assignment lines; no literal opening token in arm 2; both `Write-TestResult` lines and everything outside the permitted arm region byte-equal to BASE; no new census-pattern match. Inspection agrees with those checks.

The matching full-gate dispatch receipt reports `Total: 31 | PASS: 31 FAIL: 0 SKIP: 0`, with both placeholder results PASS; the checker reports exit 0 and `FAIL names []`. Row 0 reports exactly those two names failing, total 31, PASS 29, exit 1. This review accepted that matching runtime evidence and did not rerun the unchanged PowerShell suite or its live-provider arms.

## Q4 — Assertion preservation, Red/Green and rigor (AC-5, AC-11)

Accepted. Independent AST comparison covered all 31 existing test functions, beyond just the eight named touched functions: every assert statement and decorator list equals BASE. Parametrized case enumeration independently gives BASE 91 and current 96, with exactly the five intended new functions. `hermetic-check.py --asserts --eol` also passed.

The registry Red's recorded exit is 1: AC-2 fails for missing FIXTURE and the 12 RED_IDS fail by assertion on the hostile registry's `unknown_slug`; the four expected early-refusal cases pass. Summary: `13 failed, 4 passed, 75 deselected`. Governance Red: exit 1, two intended assertion failures. Dispatch Red: exit 1, exactly the intended pair. Their Green receipts and the matching full gate substantiate the handoff's counts. The register's `17 passed, 75 deselected` correctly quotes the earlier row-2 run; final HOSTILE has `17 passed, 79 deselected` because four governance tests were added afterward.

D-919 is sound: the actual long pytest failure titles use one underscore per side, and `^_+ (.+?) _+\s*$` recognizes those same failure blocks without dropping diagnostic attribution requirements. Independent selftest execution reports `37 fixture(s) (12 positive, 25 negative), 0 wrong`. No new test is vacuous: AC-2 verifies a fixture-derived compiled stamp and unknown-slug refusal; AC-6/7 run the real static verifier on changed copies; AC-8 corrupts a pin and requires its exact refusal; AC-14 checks live pins and an intentional mismatch.

### IR-5 test audit

All cases of each parametrized function share the rating shown. Strong means specific behavior/diagnostics, paired paths or concrete state assertions; Adequate marks inherited tests relying on exit status or substring checks. No Weak test was found in the delivered delta.

| Test function (prefix `test_` omitted) | Rating |
|---|---|
| ac_2_fixture_registry_home_compiles | Strong |
| verifier_bootstrap_accepts_captured_bytes | Adequate |
| verifier_bootstrap_refuses_drift_without_restoring | Strong |
| verifier_bootstrap_refuses_source_revision_change | Strong |
| verifier_bootstrap_rejects_path_escape | Strong |
| verifier_bootstrap_new_unlisted_file_refused | Strong |
| verifier_bootstrap_declared_bootstrap_exception | Strong |
| evidence_contract_real_cli_selftests | Strong |
| evidence_contract_missing_ac_rejected | Strong |
| legacy_review_checker_remains_compatible | Adequate |
| review_pipeline_target_bound_approval | Adequate |
| review_pipeline_raw_bytes_and_null_semantics | Strong |
| review_pipeline_ledger_adversarial_selftest | Strong |
| validation_stages_stop_and_bind_inputs | Strong |
| registry_contract_preserves_bindings | Adequate |
| registry_contract_vendor_independence | Adequate |
| registry_contract_unsupported_harness_refused | Strong |
| review_pipeline_governance_static_oracles | Strong |
| governance_preservation_and_routing_inventory | Strong |
| ac_6_pin_follows_the_copied_instructions | Strong |
| ac_7_backlink_closure_copies_new_targets | Strong |
| ac_8_pin_oracle_still_refuses | Strong |
| ac_14_tracked_rule_map_pin_matches_live_instructions | Strong |
| review_pipeline_approval_rejects_uncorrelated_claims | Adequate |
| review_pipeline_closeout_requires_real_completion | Adequate |
| registry_contract_bad_configuration_refused | Adequate |
| review_pipeline_correlated_approval_positive | Strong |
| review_pipeline_valid_continuation_preserves_approval | Strong |
| review_pipeline_ledger_binds_exact_plan | Strong |
| review_pipeline_complete_approval_tampering | Strong |
| review_pipeline_wrapper_refuses_before_provider | Strong |
| validation_stages_live_runtime_inputs | Strong |
| registry_contract_registered_task_command | Strong |
| review_pipeline_approval_with_nonblocking_findings | Strong |
| review_pipeline_explicit_vendor_exception | Strong |
| registry_contract_generic_class_census | Strong |
| DISPATCH_TEST arm 2 and adjacent real-directory control | Strong |

## Q5 — Live probe and registers (AC-12, AC-13)

Accepted from source, receipts and independent register comparison. `live-probe.py` reads the seven original binding cases from BASE by AST, clears `AGENT_MODEL_REGISTRY` in each child, resolves against the real project, checks the reviewer with both author vendors and uses `--check-compiled` without writes. The gate receipt has all seven expected routes, reviewer/anthropic exit 0, reviewer/openai exit 1, compiled-overlay validation exit 0 and `live-probe: ok`. Source additionally requires `gpt-6.1-sol` and `vendor_diversity_violation` on the respective reviewer paths. This was existing session evidence, not a new reviewer live-probe run.

The row-0 register copy matches its recorded SHA-256. Exactly 13 parsed field changes are present, confined to status, verification and resolution_path of the three named issues. Registry coupling is `mitigated`, explicitly retaining the HDP compiled-stamp residual; governance coupling and the placeholder issue are `resolved` with their deliberate remaining live-pin/manual-folder conditions stated. The verification summaries match their named receipts. Both register files retain LF, and the matching gate's render check reports `OK: known-issues.md is up-to-date`. No other parsed issue-register change belongs to Session 76.

## Q6 — Safety, tested state and evidence fidelity

Accepted. TEST_FILE remains CRLF without BOM; DISPATCH_TEST remains BOM plus CRLF; both new fixture files and both issue-register files remain LF. Independent byte checks passed. Scoped diffs and the gate's content-bound scope result support the disclosed scope; there is no product implementation change in this session. HEAD is unchanged. The review did not find an undisclosed repository mutation, a machine-registry write or a personal email/home-folder path introduced by this scoped delta. This is an inspection of delivered state and saved execution evidence, not a forensic proof of every historical filesystem operation.

D-920 is sound and accurately disclosed: the first dispatch run refused with `registry_not_found: no ModelRegistry.psm1 at any S2 location`; setting `AGENT_MODEL_REGISTRY_HOME=P:/.agent` matches row 0 and the gate. It does not alter fixture env precedence or assertions. The other disclosed deviations introduce no demonstrated contract failure.

**tested_state:** `3397e78d7342d73e99dde3b43244a55cd6be7e87+7763c70010433b1d4e80bff928d9f00598ee9ec3136fc1b69bac24a5eabecaa8`.

The reviewer's `identity.py --state-only` result equals the gate exactly after supplying a child-only `core.excludesFile` containing the one host ignore entry. A separate read-only filename-set comparison proved that default sandbox visibility differs only by `.claude/settings.local.json`; that file was never opened. Thus the raw visibility discrepancy is solely the stated ignore difference, and the comparable tested-state value has no remaining difference. Existing sandbox `safe.directory` settings were preserved. ELECTRON_RUN_AS_NODE was unset.

The gate starts and ends with this same state, and its last line is `session-gate: all steps exit 0`. Decisive totals are 96 adoption passes, 17 HOSTILE passes, dispatch 31/31 PASS, full Python 2,945 passes, and closeout selftest 231 arms/0 failures. The full suite was not rerun during review. The v2 verdict carries tested_state in its summary and identity checklist because the checked-in schema does not define a top-level tested_state property.

## Checklist Results

| Check | Result | Observation |
|---|---|---|
| IR-1 runtime / AC-2 to AC-4, AC-6 to AC-9, AC-14 | pass | Independent 17-case HOSTILE and 16-case governance runs passed |
| IR-2 stub compliance | n/a | No new application stub; fake provider is a refusal sentinel and remains uncalled |
| IR-3 error mapping | n/a | No API route change |
| IR-4 generalization / AC-1, AC-10 | pass | One registry-home helper covers all 16 cases; runtime token protects the arm from instantiation |
| IR-5 rigor / AC-5, AC-11 | pass | All 36 current Python test functions audited; all 31 existing assert/decorator sets unchanged; 91 + 5 = 96 |
| IR-6 boundary validation | pass | Strict fixture validation plus unknown-slug and refusal negatives; no public input surface added |
| IR-7 delivered AC coverage | pass | AC-1 through AC-14 supported; intentional D-912 residual accurately retained |
| DR claim, evidence and freshness | pass | Scoped diffs, issue field comparison, Red/Green receipts and exact matching input identity |
| D-919 / D-920 | pass | Actual failure-header padding and dispatch environment diagnostic support both choices |

### Reviewer command evidence

All commands ran from `P:/av-kit` through `rtk proxy` with all streams redirected under `C:/Temp/av-kit/tth/exec-review`. Python bytecode was disabled. Pytest used `-p no:cacheprovider`, TMP/TEMP under the review's `tmp`, and isolated `--basetemp` subfolders there. `UV_OFFLINE=1` and `UV_NO_SYNC=1` prevented network/sync; uv's cache was redirected to the review folder. The exact invocations and independent comparison/probe code are retained in `run-probes.ps1`, `state.ps1` and `facts.py` there.

```json
{"schema_version":"evidence.v1","check_id":"tth-review-fixture","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-15-tooling-test-hermeticity/fixture-check.py","cwd":"P:/av-kit","scope":"AC-1","phase":"static","exit_code":0,"result":"pass","tested_state":"3397e78d7342d73e99dde3b43244a55cd6be7e87+7763c70010433b1d4e80bff928d9f00598ee9ec3136fc1b69bac24a5eabecaa8","output":"strict validate exit 0; regenerated bytes equal True; parser equals yaml.safe_load True; independent build equals True; fixture-check: 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"tth-review-hostile","command":"rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -k 'preserves_bindings or vendor_independence or unsupported_harness or bad_configuration or wrapper_refuses or test_ac_2_' -p no:cacheprovider --basetemp C:/Temp/av-kit/tth/exec-review/tmp/hostile --tb=short -q","cwd":"P:/av-kit","scope":"AC-2 to AC-4; child AGENT_MODEL_REGISTRY=C:/Temp/av-kit/tth/red-home/model-registry.json","phase":"targeted","exit_code":0,"result":"pass","tested_state":"3397e78d7342d73e99dde3b43244a55cd6be7e87+7763c70010433b1d4e80bff928d9f00598ee9ec3136fc1b69bac24a5eabecaa8","output":"17 passed, 79 deselected in 3.67s"}
```

```json
{"schema_version":"evidence.v1","check_id":"tth-review-governance","command":"rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -k 'test_ac_6_ or test_ac_7_ or test_ac_8_ or test_ac_14_ or static_oracles or preservation_and_routing or generic_class_census' -p no:cacheprovider --basetemp C:/Temp/av-kit/tth/exec-review/tmp/governance --tb=short -q","cwd":"P:/av-kit","scope":"AC-6 to AC-9, AC-14","phase":"targeted","exit_code":0,"result":"pass","tested_state":"3397e78d7342d73e99dde3b43244a55cd6be7e87+7763c70010433b1d4e80bff928d9f00598ee9ec3136fc1b69bac24a5eabecaa8","output":"16 passed, 80 deselected in 21.20s"}
```

```json
{"schema_version":"evidence.v1","check_id":"tth-review-facts","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/tth/exec-review/facts.py","cwd":"P:/av-kit","scope":"BASE anchors, all existing assertions/decorators, case counts, issue delta, ignore visibility, both live-pin repair commands in scratch, Red receipts","phase":"targeted","exit_code":0,"result":"pass","tested_state":"3397e78d7342d73e99dde3b43244a55cd6be7e87+7763c70010433b1d4e80bff928d9f00598ee9ec3136fc1b69bac24a5eabecaa8","output":"31 existing test functions: every assert/decorator unchanged; BASE 91/current 96; BASE anchors match; 13 allowed issue field changes; ignore-only visibility difference is the unopened local settings file; both single-byte drift probes detected and emitted repair payloads executed successfully in scratch; facts: all assertions pass"}
```

| Other independent command | Exit | Decisive output |
|---|---|---|
| `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-15-tooling-test-hermeticity/hermetic-check.py --asserts --eol` | 0 | Eight touched functions' asserts/decorators equal; six EOL checks ok; 0 problems |
| `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-15-tooling-test-hermeticity/dispatch-check.py --source` | 0 | Arm 2, seven changed lines; 0 problems |
| `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-15-tooling-test-hermeticity/red-check.py --selftest` | 0 | 37 fixtures, 12 positive/25 negative, 0 wrong |
| `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/tth/exec-review/state.ps1` | 0 | `identity.py --state-only` equals the full-gate state above |

Reviewer setup failures were corrected only in scratch: the initial pytest launch exited 2 because the default uv cache was inaccessible, then passed with the cache redirected; an initial identity launch exited 1 because its temporary git config replaced sandbox safe-directory entries, then passed after appending the ignore override while preserving those entries. Neither failure was treated as implementation Red or a finding. Successful static checks were not repeated just to regenerate a summary.

## Verdict

**approved** — no evidence-backed behavioral or contract defect was found. The deliverable achieves the registered intent, preserves existing assertions and retains D-132's live drift signal. No correction request or open question remains for this review round.

Residuals remain exactly as approved: live HDP registry checks can red after a machine bump; overlay rebindings require fixture regeneration; governance edits still require a checked live-pin rebind; the upstream placeholder defect and old empty temp folder remain Mat's separate actions. The coordinator can collect the verdict and proceed to H2. Commit/push authorization is unchanged.

🕐 Completed: 2026-11-15 22:11 (EST)
