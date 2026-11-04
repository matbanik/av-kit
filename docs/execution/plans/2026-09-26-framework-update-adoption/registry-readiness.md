# Registry readiness — implementation checkpoint

WP-3 is in progress, not complete. The project overlay adds five fully declared classes without overriding global classes or modifying `P:/.agent`. No provider call, worker smoke, model upgrade or capability-flag change is claimed.

## Observed checks

`rtk proxy uv run python P:/.agent/tools/resolve_model.py validate --overlay .agent/model-registry.local.yaml --write-compiled` exited 0: five added classes, zero tightened classes and zero extra allowlist paths. Only the project's compiled sibling was written.

V22, `rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -q -p no:cacheprovider -k registry_contract`, exited 1: **11 passed, 2 failed, 32 deselected**. Receipt: `C:/Temp/av-kit/framework-adopt-v22.txt`.

All seven binding checks passed: Cursor coordinator/builder retain their approved Grok loader value; Cursor verifier retains Composer; Claude coordinator resolves on claude-p, builder/verifier on claude-code-agents retain Sonnet, and router retains Haiku. Anthropic-authored work resolves the configured Codex reviewer. Negative overlay tests reject global-policy loosening, unknown slugs and invalid explicit registry paths.

The two failing tests have incorrect diagnostic expectations. Both underlying refusal behaviors already return nonzero, as required:

```text
OpenAI author: exit 1; stdout empty; stderr:
error: vendor_diversity_violation: author vendor 'openai' equals 'gpt-5.6-sol''s vendor; avkit_independent_reviewer requires a different vendor

Unsupported coordinator harness: exit 1; stdout empty; stderr:
error: unresolvable_on_harness: 'avkit_coordinator' has no binding on 'claude-code-agents'. It is bound on: claude-p, cursor-task. No substitute is chosen from another class
```

The live resolver raises `vendor_diversity_violation` at `P:/.agent/tools/resolve_model.py:735`, raises `unresolvable_on_harness` for missing bindings in `resolve()`, and writes RegistryError diagnostics to stderr in `main()`. `split_the_review` describes a different resolver condition; expecting it for vendor rejection was a test-authoring mistake.

## Human decision: two assertion corrections approved

The user's direct chat reply **`approved`**, immediately following the request to approve the exact diff below, authorizes only these two diagnostic assertion corrections. They have been applied. V22 rerun: **13 passed, 32 deselected**, exit 0; `C:/Temp/av-kit/framework-adopt-v22-approved.txt`. The nonzero-exit predicates remain intact. This decision does not approve implementation review, additional assertion changes, provider changes or commits. The following paragraphs preserve the original decision context.

The approved plan freezes Red assertions and keeps the shared resolver read-only. The repository TDD rule also prohibits editing assertions to make a run pass. No assertion has been changed. A direct user authorization is requested for this source-backed correction; it preserves the behavioral refusal and successful binding predicates.

Proposed exact diff in `tests/tooling/test_framework_adoption.py`:

```diff
-    assert ("split_the_review" if expected else "gpt-5.6-sol") in result.stdout
+    assert ("vendor_diversity_violation" if expected else "gpt-5.6-sol") in (
+        result.stderr if expected else result.stdout
+    )

-    assert result.returncode != 0 and "unresolvable_on_harness" in result.stdout
+    assert result.returncode != 0 and "unresolvable_on_harness" in result.stderr
```

The preceding vendor test's nonzero-exit assertion remains unchanged. Do not merge stderr into stdout or alter shared code to disguise the mismatch. Follow-up: after the user's decision, apply only an explicitly authorized correction, record its provenance here, rerun V22 and complete task row 4's routing census. No approval is inferred from this file or from test fixtures.

## Current edits and remaining work

The overlay and four agent definitions preserve model fields, tools and readonly restrictions; provenance markers sit outside YAML. Global sync is forbidden here because its filename convention selects global builder/verifier classes. Local class resolution must be explicit. The agent definition stamps do not certify a live loader or worker smoke.

The caller migration, wrapper bundle and root consolidation are now applied. The final routing census enumerates all active surfaces and individually classifies retained historical observations. The shared resolver/registry remain read-only; actual harness flags and smoke evidence are unchanged. WP-5/H1 validation passed and the implementation handoff is ready. Independent implementation review is pending Mat; no H2 completion or approval is claimed.

The implementing author is OpenAI. Under the approved vendor-distinct contract, the only configured machine reviewer is ineligible; PROFILE B3 has no alternate and B4 names Mat. This is a later review gate after H1, distinct from the already-approved test-correction decision. No reviewer verdict has been authored or dispatched for implementation.

## Authorized execution review update

The user explicitly authorized separate Codex CLI GPT-6 Astra/xhigh review, then Round 2 after its changes_required verdict. This is a one-loop same-vendor exception; no global registry, overlay binding or standing wrapper policy changed. Actual vendor identities are preserved. Round 1 caller findings were corrected; the refreshed full suite has 91 passing migration tests, including registered project-class dispatch/refusal coverage. Review and H2 remain pending.

## Final adoption status

Independent Astra/xhigh Round 2 approved the corrected implementation. The actual v2 decision is bound to the report, plan, ledger and dispatch status, with the direct user exception preserved. H2 is complete. Standing global/project routing remains unchanged by the one-loop exception.
