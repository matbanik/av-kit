# Pending human implementation review — Mat

Status: **pending**. No human implementation-review verdict has been received.
The earlier user `approved` message authorized only two registry-test diagnostic assertion corrections; it is not approval of this implementation.

Target: `docs/execution/plans/2026-09-26-framework-update-adoption/implementation-plan.md`
Plan SHA-256: `935f3e14fdd939c76b658c4a21ca7df4c4787387ebe12ada59b16176cc1f1599`
Tested input state: `d01f2ff035718c1abfe8529058e2e67e94c8e5361fd48650fabae317690ae1df`.
Handoff: [.agent/context/handoffs/2026-09-26-framework-update-adoption-handoff.md](../../../../.agent/context/handoffs/2026-09-26-framework-update-adoption-handoff.md).
Detailed results and deltas: [execution-evidence.md](execution-evidence.md).

## Why this decision is needed

The implementing author is OpenAI. The only configured machine class is also OpenAI and fails vendor diversity before any provider call. PROFILE B3 has no alternate; B4 names Mat. `.agent/skills/cli-dispatch/SKILL.md` §Rate-Limit Fallback Protocol says: "If vendor diversity, authentication, availability or egress prevents this route, preserve the evidence and stop for Mat (B4)." `.agent/docs/model-routing.md` §Independent-reviewer chain requires the same fallback. This is independent implementation review, not repeat permission to execute or permission to commit.

```json
{"schema_version": "evidence.v1", "check_id": "review-route-eligibility", "command": "$env:RECEIPTS_DIR='C:/Temp/av-kit'; $env:AGENT_MODEL_REGISTRY_HOME='P:/.agent'; $env:PYTHONIOENCODING='utf-8'; rtk proxy uv run python P:/.agent/tools/resolve_model.py resolve avkit_independent_reviewer --harness codex-cli --project P:/av-kit --author-vendor openai --format json *> C:/Temp/av-kit/framework-adopt-review-eligibility.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-review-eligibility.txt; exit $code", "cwd": "P:/av-kit", "scope": "configured independent reviewer eligibility for actual author vendor", "phase": "targeted", "exit_code": 1, "result": "blocked", "tested_state": "d01f2ff035718c1abfe8529058e2e67e94c8e5361fd48650fabae317690ae1df", "output": "error: vendor_diversity_violation: author vendor 'openai' equals 'gpt-5.6-sol''s vendor; avkit_independent_reviewer requires a different vendor", "fresh": true}
```

## Review request

Review AC-1 through AC-9 in the handoff against the files/evidence. Pay particular attention to exact target/intent binding, null/raw-output preservation, before-provider refusal, no-net-growth rule mapping, and preservation of local worker/domain controls. All code/gate work is ready; AC-9 remains open solely for your independent verdict and its dependent H2 closeout.

Provide a direct chat verdict for this target and tested state: approved after review, or changes required with concrete findings. A genuine reply will be recorded with USER_EXPLICIT provenance; this file itself is not approval. No new provider or same-vendor exception is inferred.

## Follow-up task H1-7 → H2

On your verdict, first verify inputs are unchanged (rerun if missing/stale), then record the real manual observation in v2 format with observer Mat and null exit, preserving your actual findings. Bind target/plan hash/intent/ledger and the rolling implementation review; run V19. Only after approved review proceed to H2 reflection, metrics, completion checks and commit-message draft. No commit/push is authorized.

## USER_EXPLICIT — scoped CLI review authorization

The user directly instructed: `I approve dispetching to review to codex cli gpt-6-astra xhigh`. This supersedes the pending Mat-only route for this review loop. It authorizes a separate Codex CLI reviewer using gpt-6-astra at xhigh, including the previously explained same-vendor exception. It is not an implementation verdict or permission to commit/push. The author remains OpenAI; no vendor identity is relabeled.

The exception is process-scoped: the production wrapper, shared registry, project overlay and default policy remain unchanged. A byte-identical registry copy and a receipt-local PowerShell module permit only this class/model/actual-author tuple when this exact authorization file hash is supplied. All remaining capability, effort, schema, ledger, output-containment and exit controls remain active. Negative probes must reject missing authorization and other models.
