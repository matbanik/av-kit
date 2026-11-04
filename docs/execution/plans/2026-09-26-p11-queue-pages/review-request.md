---
project: "2026-09-26-p11-queue-pages"
action_required: "CODEX_CLI_INDEPENDENT_REVIEW"
reviewer: "Codex CLI gpt-6-astra high"
author_vendor: "openai"
reviewer_vendor: "openai"
status: "authorized_for_dispatch"
---

# Session 24 independent implementation review request

This is the implementer's review package, not a review verdict. The user explicitly authorized one separate-context Codex CLI review using `gpt-6-astra` at high reasoning under a scoped same-vendor exception. The actual OpenAI author and reviewer identities remain disclosed; no approval is claimed before the reviewer returns a valid verdict.

## Exact review-loop intent

`Deliver Session 24 queue-page composition for MEU-52, MEU-53, and MEU-54 while preserving existing queue behavior, caller IDs, request contracts, and scroll geometry.`

The reviewer must quote that sentence verbatim in `intent_anchor`.

## Exact target and revision

- Target: [implementation-plan.md](implementation-plan.md), with MEU-52, MEU-53 and MEU-54 in scope.
- Plan SHA-256: `36fa3e8122ef111bdc07ae28b3be2ee9eac0d14d2f59e2493e5bbac5acfdc6ec`.
- Git base: `d6cd5a3c8f22847b2d6fe5152fdbfbe6eb9ee173`. This is a dirty worktree, so HEAD alone does not identify the implementation.
- Actual tested source/runtime revision: `sha256:d6697cd3e5f3648ec30e26647ae0980fba8773059fd82cb9d9f08e4ed7ebfc14`; all selected file hashes and runtime/environment identity are in [validation-state.json](validation-state.json), produced independently by [validation-state.py](validation-state.py). The before/after manifests matched.
- Evidence and execution history: [walkthrough.md](walkthrough.md). After Round 2 corrections, the final fresh gate was run by [run-validation.ps1](run-validation.ps1): **597 Vitest tests, 95 real Electron tests, typecheck, lint and both ordinary/isolated builds passed**. Before/after identity matched; compare its final evidence state to the manifest.
- Task and remaining ordering: [task.md](task.md). H2 begins only after a target-bound independent approval.

## Review scope

Read all three handoffs, including their AC tables, implementation references, historical Red/Green evidence and final-gate link:

- [MEU-52 shared queue header](../../../../.agent/context/handoffs/2026-09-26-p11-queue-pages-MEU-52-handoff.md).
- [MEU-53 Downloader Zone 1](../../../../.agent/context/handoffs/2026-09-26-p11-queue-pages-MEU-53-handoff.md).
- [MEU-54 Convert Zone 1](../../../../.agent/context/handoffs/2026-09-26-p11-queue-pages-MEU-54-handoff.md).

Product changes are the shared `QueueHeaderRow`, two page compositions, optional carried conversion encoder metadata, and selected radio styling. Test changes cover the component, both page behavior suites, real Electron queue waves, additive test IDs, unit TSX discovery, and the seven source assertions below. No API change is claimed. The separate framework adoption project is not part of this implementation review.

## Round 3 correction scope

Rounds 1 and 2 are preserved in the [rolling implementation review](../../../../.agent/context/handoffs/2026-09-26-p11-queue-pages-implementation-critical-review.md), with raw Round 2 JSON at `C:/Temp/av-kit/dispatch/p11q-astra-r2/final.json`. Round 2 marked both earlier cookie lifecycle findings fixed and reported one blocking issue:

- R2-1: the shared focus fallback hardcoded Downloader's `queue-card` row test ID, so it could not find Convert's `convert-queue-row` after gate release.

The correction gives the rendered list root its own ref, then resolves the moved row by `data-job-id` inside that list. It is independent of caller test IDs and scoped against another mounted queue. A new real Electron seam holds the reorder response, waits for dnd-kit to settle, deliberately moves focus to the document body, then releases either a successful or rejected response. Both Convert cases assert the moved row's actual handle regains focus after gate release; the rejected case also asserts order remains server-authoritative. The existing Downloader AC-49.27 case remains green. Recheck this behavior and retain R1-1/R1-2 as fixed.

## Human-approved test migration

After each failing assertion and its proposed replacement was explained in chat, Mat replied “ok go ahead.” The changes are limited to adapting the old source-shape contract to the approved composition:

| Earlier check | New protection |
|---|---|
| AC-47.5a direct selection-header mounts | Both pages mount `QueueHeaderRow` and pass total, selected count and callback; the shared header forwards them to `QueueSelectionHeader`. Existing tri-state assertions remain. |
| AC-33.3 literal task-radio IDs | All three task values, generated caller IDs, selected value, state setter and primitive native-radio semantics are checked. Queue/staging retention assertions remain. |
| AC-33.5 400-character source proximity | Compress branch contains the controlled Advanced disclosure with the preserved ID. Existing wire/catalog/refresh assertions remain. |
| Convert old summary wrapper | Shared header precedes the list, composes summary and toolbar, and keeps the established region/list-scroller checks. Real Electron checks geometry/reorder. |
| AC-46.5 direct toolbar import | Import and mount are followed through `QueueHeaderRow`; deleted-table and dependency-removal assertions remain. |
| Downloader old summary wrapper | Same shared-header ancestry and existing region/list-scroller protections as Convert. |
| AC-51.7 no product primitive imports | Positive adoption checks for Downloader/Convert, continued restriction for the four pages awaiting adoption, and unchanged isolated Electron harness checks. |

## Specific review attention

Check exact create/Save payloads, one POST for Add/Enter, local duplicate-path removal, configured Advanced initialization, caller-owned native input IDs, all-count status details, processor state, and queue scrolling/reorder. Confirm the seven source-test replacements preserve the relevant protection using the runtime assertions. Review the disclosed test setup repairs, two later responsive tests, and first full-Electron timeout followed by successful reruns. Validate the final fresh gate against its independently captured input state rather than relying on earlier counts.

## Reviewer route and scoped exception

Current [model-routing.md](../../../../.agent/docs/model-routing.md) normally requires a separate context, no authorship, and a different vendor. [cli-dispatch/SKILL.md](../../../../.agent/skills/cli-dispatch/SKILL.md) therefore refused the ordinary machine route shown below. The direct user message recorded in [human-review-decision.md](human-review-decision.md) authorizes this exact target/loop/model/effort as a one-loop exception. The dispatch keeps `author_vendor: openai` and `reviewer_vendor: openai`; it does not relabel either side or create a reusable fallback.

```json
{"schema_version":"evidence.v1","check_id":"p11q-reviewer-eligibility","command":"rtk proxy uv run python P:/.agent/tools/resolve_model.py resolve avkit_independent_reviewer --harness codex-cli --project P:/av-kit --author-vendor openai --format json","cwd":"P:/av-kit","scope":"configured independent reviewer eligibility for the actual OpenAI author","phase":"targeted","exit_code":1,"result":"blocked","tested_state":"project registry overlay with actual author vendor openai and configured GPT-5.6-sol reviewer","output":"error: vendor_diversity_violation: author vendor 'openai' equals 'gpt-5.6-sol''s vendor; avkit_independent_reviewer requires a different vendor","fresh":true}
```

## Reviewer procedure and output contract

Perform `.agent/workflows/execution-critical-review.md` as an independent reviewer. Inspect the actual diff, plan, task, walkthrough, three MEU handoffs, validation manifest, final receipts, source, tests, and runtime evidence. Assess every AC and IR-1 through IR-7, including the seven human-approved assertion migrations. Do not modify repository files. Return only one JSON object conforming to `.agent/schemas/review-verdict.schema.v2.json` with:

- `review_mode: "execution"`, `loop_id: "p11q-execution-review-2026-09-26"`, `round: 3`, and the exact target-plan path above;
- `agent: "codex-cli-gpt-6-astra-independent-reviewer"`, which differs from the registered producer;
- `requested_verbosity: "detailed"` and the exact intent sentence above in `intent_anchor`;
- evidence-backed checklist results with actual commands or explicit manual procedures;
- `approved` only when there are no blocking findings and intent is achieved;
- for any blocking finding, a concrete violated registered contract, exact file/line evidence, and an actionable correction. Use the ledger-registered IDs emitted for this loop rather than inventing an identifier.

The user authorization permits the dispatch and same-vendor exception. It is not evidence that the implementation is correct. The implementing agent must not author, rewrite, or fabricate the reviewer verdict.

## Continuation after the verdict

After valid approval, resume task H1-6 and H2: record the review outcome, write the reflection with instruction coverage, update MEU-52–54 to approved through SSOT, render/check the views, advance grouping/hub/focus to Session 25, record metrics, and run completion-preflight. No commit or push is included.
