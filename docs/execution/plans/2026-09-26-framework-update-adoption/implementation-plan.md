---
project: "2026-09-26-framework-update-adoption"
date: "2026-09-26"
source: "PROJECT-PROFILE.md; upstream-assessment.md"
meus: []
status: "approved"
template_version: "2.0"
---

# Implementation Plan: Selective framework update adoption

## Goal

Make av-kit's governance executable and easier to maintain by selectively adopting the highest-value framework updates through `003929c1cafa83359f0695415bbc06074a35f92e`. This is a **non-product governance project**. Planning originally authorized investigation and a reviewed plan only. After independent Round 3 approval, the user explicitly requested `execute implementation`; that authorizes the current execution. The later `approved` message permits the two exact diagnostic assertion corrections documented in registry-readiness.md. It is not an implementation-review verdict. The active Codex driver does not inherit Cursor overrides. Current progress is in task.md and execution-evidence.md.

Read [upstream-assessment.md](upstream-assessment.md) for ranked findings, comparison limits and preserved decisions. This plan is an ordered migration, not a recursive overwrite.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Neither repository has graphify-out/graph.json or graphify-out-research/graph.json; Headroom is unavailable in the active tool surface. Source text and exact comparison evidence require direct reads."
  human_message_reference: null
```

Reevaluate before execution. No in-harness workers are required; use `compact_continue` at durable boundaries. The independent external reviewer is a separate workflow capability.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| Non-product implementation | `.agent/context/handoffs/2026-09-26-framework-update-adoption-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-09-26-framework-update-adoption-plan-critical-review.md` and `.agent/context/handoffs/2026-09-26-framework-update-adoption-implementation-critical-review.md`. Planning-session notes use this folder's `planning-walkthrough.md`, not an implementation-complete handoff. The implementation handoff is created in H1 after execution evidence exists.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Capture baseline with existing shell primitives, then Red tests, helper implementation and baseline verification | — | shared | `adoption-manifest.json`, `rule-preservation.md`, Red/Green and baseline receipts |
| WP-1 | Runnable task/closeout and durable evidence bundle | WP-0 | compact_continue | `execution-evidence.md`; save, compact, reread task and evidence |
| WP-2 | Current adopter commands, templates and staged verification | WP-1 | compact_continue | `execution-evidence.md`; save, compact, reread task and evidence |
| WP-3 | Model class resolution and profile-aware dispatch preparation | WP-2 | compact_continue | `registry-readiness.md`; save, compact, reread task and readiness |
| WP-4 | Review ledger/v2 and wrapper cutover | WP-3 | compact_continue | `execution-evidence.md`; save, compact, reread task and evidence |
| WP-5 | Consolidate instructions, backlinks and rule map | WP-4 | compact_continue | `rule-preservation.md`; save, compact, reread task and rule map |

## User Review Required

Implementation is not authorized by this planning request. Preserve the already-approved Cursor/Claude driver distinctions, egress permission, Mat fallback and YouTube read-only rule without re-interviewing those decisions. Proposed policy changes are explicit: active review loops gain the upstream ledger controls; machine reviewers become vendor-distinct; required final verification runs once against final inputs; duplicate AGENTS/GUARDRAILS instructions are consolidated. Accepting execution of this plan adopts these documented changes. An OpenAI-authored implementation may require Mat review unless a vendor-distinct machine reviewer is explicitly configured; never inherit upstream's same-vendor exception.

The planning loop uses the **existing** wrapper and current v1 contract, up to three rounds, because the planned tooling is not installed. An independent Codex review is separate-context but same-vendor under current local policy; disclose that limitation. No circular dependency on a future ledger or validator is imposed on this planning session.

## Proposed Changes

### WP-0 — Protect the destination and pin the source

Create a per-file manifest from the execution-start working tree: source SHA, source file hash, destination preimage hash, action, ownership, merge basis, and postimage hash. Include untracked files and absence markers. Persist protected product/spec/state hashes, plus separate allowlisted governance baselines. Do not stash/reset, replace user changes, fetch/pull, or write to `P:/agentic-framework`. Recheck source identity before copying; drift requires a refreshed assessment.

Bootstrap order is fixed and represented by rows 0, 1, 1a, 1b: **capture → Red → implement helper → verify baseline → port destination tools**. Row 0 uses existing PowerShell/file-read primitives to capture hashes, source identity, explicit absence markers and preimages for the allowlisted files into `adoption-manifest.json`; it does not invoke or create the future verifier. The manifest also records the two bootstrap code/test paths as absent or their actual preimages before either is written. `rule-preservation.md` is data/documentation, not executable code. Row 1 writes all migration contract tests; use fixtures/stubs to exercise unmet behavior, and make the helper-unavailable branch an explicit contract failure rather than a pytest import/collection error. Row 1a implements only `checks/verify_adoption.py`; row 1b runs V1, checking the stored execution-start manifest rather than silently overwriting it. Existing destination tools/governance remain untouched until row 2.

The verifier's `baseline` validates captured state (allowing the declared bootstrap files); `static` checks selected paths/contracts; `final` checks protected state and completed implementation evidence without requiring future H2 artifacts; `approval` checks the independent decision/ledger/dispatch correlation; `metrics` validates the appended metrics row and preserved historical prefix; `closeout` additionally requires all task rows except its own and the subsequent draft row resolved, populated metrics and structural H2 artifacts. It must reject source drift, missing selected tool dependencies, unresolved placeholders in adopted active files, cyclic task dependencies, lost project constraints, stale template copies and changes outside the allowed set. Conflicting concurrent changes cause a stop to reconcile, never a restore over newer edits. Its scripts are future deliverables, not claimed to exist today.

### WP-1 — Install the missing verification tools as one dependency bundle

Selectively port `tools/durable_evidence.py`, `tools/lint_task_contract.py`, `tools/validate_closeout_artifacts.py`, `tools/validate_json_schema.py` and `tools/tests/test_durable_evidence.py`. Run only that upstream evidence test file in WP-1 (V16), plus the installed migration contract groups in V21. The adapter/ledger/v2 pipeline tests and V5 belong to WP-4 after all their dependencies exist. Closeout review checks keep historical `implementation` mode support through the unchanged legacy checker; new workflows use the upstream `execution` mode. Do not rewrite prior verdicts or imply old receipt-only artifacts meet new evidence requirements.

New/changed handoffs embed `evidence.v1` command/procedure, result, scope, tested state and decisive output. External-error blockers carry nonzero exit and actual diagnostics; human-decision blockers carry a decision link. Shared task/handoff parsing must agree. Manual review records preserve `exit_code: null`; command records cannot use null to hide execution failure. Snapshot/cache-only evidence cannot establish final approval.

### WP-2 — Register actual commands and wire the validators

Update PROFILE D6 and commands using the existing `pyproject.toml`, `ui/package.json`, `mcp-server/package.json` and real OpenAPI export helper. Each registered check declares argv, cwd, selected scope, blocking status, expected result, shell and evidence location. Register Python pytest/pyright/ruff, UI typecheck/lint/Vitest/build/real Electron and MCP typecheck/test/build. Retain `ELECTRON_RUN_AS_NODE` clearing and current E2E fixture/output conventions. This governance project's full gate is the complete adopted tooling/regression suite plus document and protected-state checks; product suites are required when product/shared product configuration changes, not merely because governance docs changed.

Use static → targeted → full sequencing. First blocking failure stops later stages (`not_run`); relevant code/tests/config/environment/input changes invalidate evidence. Run one fresh full scoped gate before final implementation review, rerun affected gates after corrections, and never claim reusable evidence from only a commit SHA in a dirty tree. Wire actual linter/closeout commands into planning, execution, H1 and H2. Active template task linting passes `--allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier`; the adopter tests prove those class names are accepted and an unregistered class is refused. Current migration task rows omit the optional builder column. Choose existing runtime template homes as canonical; keep `.agent/templates/` copies synchronized for compatibility. Remove references to nonexistent universal validation tooling rather than installing a fake product validator.

### WP-3 — Resolve model classes without changing global pins

Use the existing shared home `P:/.agent` **read-only**, selected explicitly in the execution process with `AGENT_MODEL_REGISTRY_HOME`; inspect any existing explicit `AGENT_MODEL_REGISTRY` before choosing precedence. Do not change user/machine environment variables. Add `.agent/model-registry.local.yaml` only using the live resolver's supported overlay contract, with current approved per-harness bindings; no invented model IDs. Validate/compile the overlay into its repo-local `.json` sibling; resolutions must pass `--project P:/av-kit` (PowerShell `-Project`) so the overlay is actually consumed. Read `P:/agentic-framework/.agent/INSTANTIATE.md` and the live resolver help/schema before implementation. The packaged forwarding scripts are not a standalone registry engine. Do not run global `sync`: resolve and update only the four allowlisted av-kit agent definitions, preserving guardrails and stamping the current registry hash.

Record local registry readiness, binding resolution, author vendor and negative refusals in `registry-readiness.md`. Use **AVKIT_CLASS_MAP** below; global coordinator/builder/reviewer defaults do not preserve this project's choices. New project classes use full contracts, not `extends` (which could inherit global bindings/fallbacks). Overlay root is `extends: global`; fallback_rungs are empty for every new class. No catalog entry or global class is changed.

#### AVKIT_CLASS_MAP — single binding definition

These are observed existing catalog IDs and preserved local choices, not recommendations for new models. Re-verify against the live catalog at execution. If any ID disappears or fails its contract, stop for Mat; do not invent a replacement.

| New overlay class | Full contract | Exact harness bindings | Active callers after cutover |
|---|---|---|---|
| `avkit_coordinator` | capabilities `[orchestration, deep_reasoning, agentic_exec]`; effort_default `high`; forbid `[claude-fable-5-1]` | `cursor-task: {slug: cursor-grok-4.6, effort: xhigh}`; `claude-p: {slug: claude-opus-5, effort: high}` | PROFILE/harness/routing/delegation coordinator references; planning/workflow/lifecycle coordinator examples |
| `avkit_builder` | capabilities `[agentic_exec, bulk_edit]`; effort_default `medium`; price_ceiling_band `high`; inherit_allowed `false`; not_a_reviewer `true`; forbid `[claude-fable-5-1]` | `cursor-task: {slug: cursor-grok-4.6, effort: xhigh}`; `claude-code-agents: {slug: claude-sonnet-5, effort: medium}` | Cursor and Claude builder definitions; task builder column; subagent skill; delegated plan and execution work rows |
| `avkit_verifier` | capabilities `[agentic_exec, bulk_edit]`; effort_default `medium`; price_ceiling_band `high`; inherit_allowed `false`; not_a_reviewer `true`; forbid `[claude-fable-5-1]` | `cursor-task: {slug: composer-2.5-fast, effort: medium}`; `claude-code-agents: {slug: claude-sonnet-5, effort: medium}` | Cursor and Claude readonly verifier definitions and verification delegation examples; tool restrictions remain in agent definitions |
| `avkit_independent_reviewer` | capabilities `[code_review, agentic_exec, read_only_sandbox]`; vendor_distinct_from `author`; effort_floor `medium`; effort_default `high`; price_ceiling_band `high`; auth_mode `chatgpt-plan` | `codex-cli: {slug: gpt-5.6-sol, effort_map: {routine: medium, risk_path: high}}` | Both dispatch wrapper defaults and workflow/skill reviewer calls explicitly select this class; sole automated review rung |
| `avkit_router` | capabilities `[classification]`; effort_default `low`; price_ceiling_band `low`; not_a_reviewer `true` | `claude-code-agents: {slug: claude-haiku-4-5, effort: low}` | Existing Claude routing-only examples; never builder or independent reviewer |

**Unsupported harnesses are intentional refusals.** The observed Opus 5 catalog entry has `claude-p`, not `claude-code-agents`; do not alias it to the global Opus 4.8 entry or add an invented harness ID. The interactive Claude Code primary-driver selection remains the existing human-controlled PROFILE choice; the registry does not launch or certify that interactive main model. This coordinator class resolves only the two listed callable harness routes. Builder/verifier agent aliases remain the existing `sonnet`. A requested unsupported coordinator-agent route fails closed and is not silently converted to headless execution. Gemini and headless-Claude **reviewer** fallbacks remain unconfigured; Mat is the named fallback. Cursor fresh_worker stays none; Claude's independent smoke-backed worker setting survives.

Compile via `uv run python P:/.agent/tools/resolve_model.py validate --overlay P:/av-kit/.agent/model-registry.local.yaml --write-compiled`; read-only verification uses `--check-compiled`. Resolve each table row with `resolve CLASS --harness HARNESS --project P:/av-kit --format json`, adding `--author-vendor` for the independent-review class. The resolver path and caller arguments are fixed; CLASS/HARNESS are the finite pairs in AVKIT_CLASS_MAP. The migration verifier exercises this matrix with explicit argv arrays, compares the returned harness slug/effort to the existing approved values, and asserts refusal for an unsupported pair, a redefinition of global coordinator bindings, bad explicit registry, unknown binding and same-vendor review. The wrapper must forward `-Project` / `--project` so its project overlay is consumed; fixture tests detect a call that omits it.

**ACTIVE_ROUTING_SURFACES** are root instruction/profile files; `.agent/docs/`, `.agent/workflows/`, `.agent/roles/`, `.agent/skills/` operational Markdown/scripts; active template homes; both agent-definition directories; and the two dispatch wrappers. Run an untruncated content census for numeric model names, `model:` pins and reviewer-rung prose over that set, and save `routing-census.md` with path/line, operational-vs-historical classification and merge/exclusion action. Every operational caller points to AVKIT_CLASS_MAP classes or explicitly states that the provider route is unconfigured. Snapshot names are allowed only in the overlay, generated agent model fields/stamps, exact contract-test fixture data, and individually cited dated historical observations; do not blanket-allowlist an active document. Prior handoffs/reflections/plans and subagent verification-log remain immutable history. Add negative fixtures planting a stale live routing statement and an unconfigured fallback; both must fail, while a dated historical observation passes.

### WP-4 — Cut over review execution as one tested unit

Adopt ledger, closed vocabulary, v2 verdict schema, output adapter, both dispatch wrappers and their tests together. Begin/evaluate/record bind review kind, plan/AC intent, producer identity, schema fingerprint, finding mechanism and usage. Default round caps remain plan 3/execution 6; copy other upstream defaults from the pinned ledger exactly, documented once in the command/profile contract. Named-human `continue` records rationale/time and the particular relief; it must not reset prior rounds. A session with unknown usage is labelled unmeasured, never zero-cost. No same-vendor fallback rung or unconfigured new provider is added. Mat remains the human fallback.

Preserve raw review bytes before schema normalization; normalization is schema-aware and does not erase meaningful manual/null or invalid evidence. Validate v2 before recording; process exit 0 alone is not approval. Preserve v1 artifacts/checker for history, fail closed on ambiguous live review mode or target. Run provider-free fake-executable tests for timeout/tree termination, wrong/missing final JSON, raw backup, path/symlink resolution, policy refusals and usage. Then run the authorized independent execution review through the final route; if the current author has no eligible provider, use Mat's human gate. The old wrapper is not a policy-bypass fallback after cutover.

### WP-5 — Consolidate only after the controls exist

Merge upstream's compact AGENTS/GUARDRAILS structure with av-kit's domain, architecture dependency rule, no uploads, real Electron testing, source-backed FIC, no self-approval, user authorization, worker capability and session continuity constraints. Follow host hierarchy; remove claims that repository text outranks host system/developer instructions. Preserve the user's RTK-required routing; do not adopt upstream optional RTK as a weakening of this repo's explicit instruction.

Map every removed rule to a successor or explicit justified retirement in `rule-preservation.md`; no net new rule count. Upstream size targets (AGENTS ≤170 lines/20,000 bytes; GUARDRAILS ≤90 lines/8,000 bytes) are merge targets, not permission to discard controls. Relocate detail into owning documents, synchronize registry section IDs/backlinks and verify loader-facing bootstrap references. Scope standalone correction-workflow stop wording so it cannot interrupt a parent review loop. Keep old section IDs in historical reflections valid by retaining aliases/mappings. No optional hook installation or claim of loader certification.

### Boundary Inventory

| Surface | Schema owner | Constraints / extra fields | Error / parity |
|---|---|---|---|
| Plan/task and blocked evidence Markdown | task/closeout validators + shared evidence parser | documented columns, known statuses, complete dependencies and evidence | nonzero CLI exit on malformed/unsupported records; same blocked predicate in both consumers |
| Review JSON and manual observation | v1 legacy / v2 JSON schema, adapter, schema CLI | preserve original bytes; strict schema fields, manual null only where valid | reject before ledger record; same checks on write/read |
| Ledger and vocabulary files | review_ledger loader and vocabulary contract | closed mechanisms and immutable loop/intent/schema bindings | fail closed on invalid/drifted state, no silent recreation |
| Model registry env/file/overlay | live resolver + ModelRegistry module | exclusive location precedence, real bindings and author-vendor checks | explicit missing dependency or refusal; no fallback around explicit invalid input |
| Source/destination migration files | execution-start manifest and verifier | hash-bound allowlist, protected paths, tracked source only | nonzero on unexpected drift; no overwrite of conflicting new bytes |

No REST/MCP/UI product input is modified, so HTTP 422 and create/update endpoint parity are not applicable. CLI failure codes are tested at their real consumer boundaries.

### Acceptance Criteria / FIC

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | integration | Baseline verifier → manifest → final verifier proves pinned source and protected product/state preimages unchanged, including untracked bytes | Human-approved planning scope; Local Canon PROFILE merge notes | Change one protected fixture or upstream SHA; final refuses without rewriting it |
| AC-2 | integration | Planning/task and H1/H2 workflows invoke installed validators; new complete evidence passes; absent AC, false blocker or temp-only citation fails at actual CLI | Local Canon active templates; upstream durable_evidence and closeout/lint tools | Remove an AC or substitute exit 0 for external blocker; both consumers reject |
| AC-3 | integration | Adapter → original schema CLI → ledger preserves manual observations and exact raw bytes; invalid command/manual forms fail | Local Canon upstream pipeline tests and Sept 26 R2 review | CRLF/non-ASCII raw backup identical; required null/unknown null/invalid exit still rejected |
| AC-4 | integration | Registered governance gate runs static→targeted→full with final input identity; product commands accurately reference live manifests | Local Canon PROFILE D6, package scripts; upstream staged validation | First-stage forced failure leaves later stages not_run; test/config mutation invalidates prior result |
| AC-5 | integration | Dispatch entrypoint → project overlay → AVKIT_CLASS_MAP resolution enforces explicit location and vendor; active caller census, worker flags and local choices survive | Local Canon harness.local, PROFILE; upstream INSTANTIATE and dispatch | Bad explicit registry, unknown binding or same-vendor review refuses before fake provider launch |
| AC-6 | integration | Dispatch → schema → ledger rejects wrong target/kind/intent, schema drift, exhausted limits and malformed usage; human continuation preserves history | Local Canon upstream review_ledger, v2 schema and vocabulary | Wrong target or exhausted fixture loop cannot call fake provider; continue without human attestation rejected |
| AC-7 | integration | Historical v1 implementation reviews remain checkable; new execution-mode review is target-bound with no ambiguous fallback | Local Canon tools/check_exec_review.py; upstream review-state checker | A stale approved body under changes_required frontmatter and a different target both fail |
| AC-8 | integration | Compact entry docs, loaded references, registry IDs and templates preserve every required local rule and retire duplicates without net growth | Local Canon deletion budget, PROFILE; upstream rule-preservation approach | Drop YouTube prohibition, break a backlink or desynchronize a template fixture; static verifier fails |
| AC-9 | integration | Final implementation review follows fresh scoped gates, handoff contains all ACs, H2 follows approved review; no product status change | Local Canon H1→review→H2, non-product task template | Missing/wrong-target approval or incomplete closeout prevents completion |

The production chains and failure observables are in each AC; fixture assertions must call real CLI/adapter boundaries rather than duplicate validation code. File writes use atomic replacement where upstream provides it; retain ledger write/read consistency. The baseline is observational, not a lock: recheck hashes immediately before each mutation and refuse concurrent drift.

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Adoption scope | Human-approved | User requested important framework updates and a plan; non-product `meus: []` |
| Portable feature behavior | Local Canon | Pinned upstream files and reviewed migration; selected features defined above |
| av-kit preservation | Local Canon | PROFILE adoption merge notes, current harness override, current code/package manifests |
| Vendor routing change | Local Canon | Proposed upstream strict policy explicitly adopted only during authorized execution; Mat fallback retained |
| Validation extent | Local Canon | Upstream D6_ADOPTER_ARGV plus av-kit live package scripts; scoped governance full gate, no fabricated universal tool |
| Legacy behavior | Local Canon | Existing frontmatter checker remains for historical artifacts; new tools cover new contract |

### Files Modified

All paths below are an explicit candidate allowlist. Manifest actions and preimages are resolved at WP-0. No other active files may change without a source-backed plan amendment/review.

| Files | Action | Purpose |
|---|---|---|
| `docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py`, `docs/execution/plans/2026-09-26-framework-update-adoption/adoption-manifest.json`, `docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md`, `docs/execution/plans/2026-09-26-framework-update-adoption/registry-readiness.md`, `docs/execution/plans/2026-09-26-framework-update-adoption/execution-evidence.md` | new | Migration checks and durable proof |
| `tests/tooling/test_framework_adoption.py` | new | Adopter regression/negative contract tests |
| `tools/durable_evidence.py`, `tools/lint_task_contract.py`, `tools/validate_closeout_artifacts.py`, `tools/validate_json_schema.py`, `tools/adapt_output_schema.py`, `tools/review_ledger.py` | new | Complete evidence/review tool dependency bundle |
| `tools/tests/test_durable_evidence.py`, `tools/tests/test_review_output_pipeline.py`, `tools/tests/test_review_verdict_schema_v2.py`, `tools/tests/Test-GetPhysicalPath.ps1` | new | Ported behavioral regressions |
| `tools/Invoke-CodexDispatch.ps1`, `tools/Invoke-CodexDispatch.sh`, `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1` | merge | Registry/ledger/schema-aware dispatch and test coverage |
| `.agent/context/review-vocabulary.yaml`, `.agent/schemas/review-verdict.schema.v2.json` | new | v2 closed vocabulary/schema; retain v1 |
| `.agent/INSTANTIATE.md`, `.agent/docs/verification-principles.md`, `.agent/model-registry.local.yaml`, `.agent/model-registry.local.json` | new | Setup instructions, evidence principles, supported project overlay and compiled provenance |
| `PROJECT-PROFILE.md`, `.agent/context/harness.local.md`, `.agent/docs/harness-profiles.md`, `.agent/docs/model-routing.md`, `.agent/docs/model-delegation.md` | merge | Per-driver profile, resolved classes, human fallback; unchanged capability decisions |
| `.cursor/agents/av-kit-builder.md`, `.cursor/agents/av-kit-verifier.md`, `.claude/agents/av-kit-builder.md`, `.claude/agents/av-kit-verifier.md` | merge | Class/AUTOGEN contract; current bindings and smoke status preserved |
| `.agent/docs/commands.md`, `.agent/docs/output-evidence-policy.md`, `.agent/docs/testing-strategy.md`, `.agent/docs/context-compression.md`, `.agent/docs/artifact-naming.md` | merge | Current checks and durable evidence; preserve product testing canon |
| `.agent/skills/terminal-preflight/SKILL.md`, `.agent/skills/quality-gate/SKILL.md`, `.agent/skills/pre-handoff-review/SKILL.md`, `.agent/skills/completion-preflight/SKILL.md`, `.agent/skills/cli-dispatch/SKILL.md` | merge | Invoke real tools and updated evidence/review contracts |
| `.agent/workflows/create-plan.md`, `.agent/workflows/execution-session.md`, `.agent/workflows/tdd-implementation.md`, `.agent/workflows/meu-handoff.md`, `.agent/workflows/plan-critical-review.md`, `.agent/workflows/execution-critical-review.md`, `.agent/workflows/validation-review.md`, `.agent/workflows/cli-dispatch.md`, `.agent/workflows/plan-corrections.md`, `.agent/workflows/execution-corrections.md`, `.agent/workflows/delegated-plan-creation.md` | merge | Active workflow call chains and correction-loop consistency |
| `docs/execution/plans/PLAN-TEMPLATE.md`, `docs/execution/plans/TASK-TEMPLATE.md`, `.agent/context/handoffs/TEMPLATE.md`, `.agent/context/handoffs/REVIEW-TEMPLATE.md`, `docs/execution/reflections/TEMPLATE.md`; corresponding five `.agent/templates/` copies | merge | Evidence/staging/class contract at configured runtime homes |
| `AGENTS.md`, `GUARDRAILS.md`, `CLAUDE.md`, `.agent/schemas/registry.yaml` | consolidate | Short entry docs, retained rules and resolvable coverage IDs |
| `.agent/workflows/README.md`, `.agent/docs/development-lifecycle.md`, `.agent/docs/agentic-methodology.md`, `.agent/docs/claude-cli-fallback-lessons.md`, `.agent/docs/issue-lifecycle-guide.md`, `.agent/skills/README.md`, `.agent/skills/subagent-delegation/SKILL.md`, `.agent/workflows/session-grouping.md`, `.agent/workflows/skill-optimize.md`, `.agent/skills/skill-optimizer/SKILL.md`, `.agent/skills/cli-dispatch/tests/Test-OpenCodePoC.ps1` | selective routing merge | R1 census found active model/rung references here; preserve unrelated behavior and never run live PoC/provider tests for a static census |
| `.agent/docs/diagrams/development-lifecycle-overview.svg`, `.agent/docs/diagrams/development-lifecycle-overview.png` | regenerate together if operational labels change | Diagram labels must agree with lifecycle canon; check source labels and paired asset generation, not a fabricated loader certification |
| `docs/execution/plans/2026-09-26-framework-update-adoption/routing-census.md`, `docs/execution/plans/2026-09-26-framework-update-adoption/review-binding.json`, `docs/execution/plans/2026-09-26-framework-update-adoption/human-review-decision.md` | new when applicable | Active caller census, correlation record and genuine human-review provenance |
| Canonical handoff/reviews, implementation reflection and `docs/execution/metrics.md` | create/append | H1/review/H2 evidence; never rewrite prior rows |

Preserve `tools/check_exec_review.py`, existing issue/MEU tools and populated state, `.agent/skills/subagent-delegation/verification-log.md`, `.agent/docs/architecture.md`, `_inspiration/`, custom `/deep-research`, `packages/`, `ui/`, `mcp-server/`, `native/`, build plans and existing execution artifacts. Prior plan/task templates are not rewritten inside historical plan folders.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Product features and Phase 11 page composition | out-of-scope | — | Human-approved scope is framework adoption; current focus owns MEU-52–54 |
| Fresh-bootstrap seeds / BUILD_PLAN stub / wholesale core copy | out-of-scope | — | PROFILE adoption merge notes preserve populated product state |
| Shared registry mutation, model upgrades, new providers, worker capability flip | out-of-scope | — | PROFILE existing choices; upstream INSTANTIATE separates local catalog ownership and smoke |
| Optional M4 hooks, snapshot/lease systems, remote release and native Linux/macOS certification | out-of-scope | — | Upstream migration review explicitly excludes these; Windows adopter scope |
| Git commit/push and adoption of commit helper scripts | out-of-scope | — | AGENTS human gate; no user authorization |

## BUILD_PLAN.md Audit

WP-0 and H1-3 must explicitly verify no product spec/status drift. No BUILD_PLAN edit is expected for `meus: []`. V12 checks its execution-start hash and V13 checks rendered state. Existing unrelated drift is recorded with exact output and assigned to its owning work; do not repair it silently or claim a clean gate. Preserve current-focus's Session 24 recommendation; planning-only artifacts do not replace product focus.

## Verification Plan

These are **future execution commands**, not completed checks. Prerequisites are installed by earlier task rows. Run from `P:/av-kit`, with `RECEIPTS_DIR=C:/Temp/av-kit` in the process for ledger fixtures. No provider call is needed for V1–V18. V19 only verifies an already-produced review/decision; it never dispatches a provider. WP-0 tests run Red against absent behavior, then Green; do not change assertions to fit imported code. Existing source tests are imported before source implementation.

### V1

```powershell
rtk proxy uv run python docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py baseline --root P:/av-kit --source P:/agentic-framework --manifest docs/execution/plans/2026-09-26-framework-update-adoption/adoption-manifest.json *> C:/Temp/av-kit/framework-adopt-v1.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v1.txt; exit $code
```

### V2

```powershell
rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -q -p no:cacheprovider *> C:/Temp/av-kit/framework-adopt-v2.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v2.txt; exit $code
```

### V3

```powershell
rtk proxy uv run python tools/lint_task_contract.py --selftest *> C:/Temp/av-kit/framework-adopt-v3.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v3.txt; exit $code
```

### V4

```powershell
rtk proxy uv run python tools/validate_closeout_artifacts.py --selftest *> C:/Temp/av-kit/framework-adopt-v4.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v4.txt; exit $code
```

### V5

```powershell
rtk proxy uv run pytest tools/tests/test_durable_evidence.py tools/tests/test_review_output_pipeline.py tools/tests/test_review_verdict_schema_v2.py -q -p no:cacheprovider *> C:/Temp/av-kit/framework-adopt-v5.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v5.txt; exit $code
```

### V6

```powershell
rtk proxy uv run python tools/lint_task_contract.py --task docs/execution/plans/2026-09-26-framework-update-adoption/task.md *> C:/Temp/av-kit/framework-adopt-v6.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v6.txt; exit $code
```

### V7

```powershell
rtk proxy uv run python tools/check_exec_review.py --self-test *> C:/Temp/av-kit/framework-adopt-v7.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v7.txt; exit $code
```

### V8

```powershell
rtk proxy uv run python tools/review_ledger.py selftest *> C:/Temp/av-kit/framework-adopt-v8.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v8.txt; exit $code
```

### V9

```powershell
rtk proxy pwsh -NoProfile -File .agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1 -Test wrapper-contract -OutputDir C:/Temp/av-kit/framework-adopt-dispatch-tests *> C:/Temp/av-kit/framework-adopt-v9.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v9.txt; exit $code
```

### V10

```powershell
rtk proxy pwsh -NoProfile -File tools/tests/Test-GetPhysicalPath.ps1 *> C:/Temp/av-kit/framework-adopt-v10.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v10.txt; exit $code
```

### V11

```powershell
rtk proxy uv run python docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py static --root P:/av-kit --manifest docs/execution/plans/2026-09-26-framework-update-adoption/adoption-manifest.json *> C:/Temp/av-kit/framework-adopt-v11.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v11.txt; exit $code
```

### V12

```powershell
rtk proxy uv run python docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py final --root P:/av-kit --manifest docs/execution/plans/2026-09-26-framework-update-adoption/adoption-manifest.json *> C:/Temp/av-kit/framework-adopt-v12.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v12.txt; exit $code
```

### V13

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/framework-adopt-v13.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v13.txt; exit $code
```

### V14

```powershell
rtk proxy uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-09-26-framework-update-adoption-handoff.md --plan docs/execution/plans/2026-09-26-framework-update-adoption/implementation-plan.md *> C:/Temp/av-kit/framework-adopt-v14.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v14.txt; exit $code
```

### V15

```powershell
rtk proxy uv run python tools/validate_closeout_artifacts.py --reflection docs/execution/reflections/2026-09-26-framework-update-adoption-reflection.md --reflection-template docs/execution/reflections/TEMPLATE.md --reflection-schema .agent/schemas/reflection.v1.yaml *> C:/Temp/av-kit/framework-adopt-v15.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v15.txt; exit $code
```

### V16 — WP-1 evidence tests (before the WP-4 pipeline exists)

```powershell
rtk proxy uv run pytest tools/tests/test_durable_evidence.py -q -p no:cacheprovider *> C:/Temp/av-kit/framework-adopt-v16.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v16.txt; exit $code
```

### V17 — Static lint of the adopted Python surface

```powershell
rtk proxy uv run ruff check tools/durable_evidence.py tools/lint_task_contract.py tools/validate_closeout_artifacts.py tools/validate_json_schema.py tools/adapt_output_schema.py tools/review_ledger.py tools/tests/test_durable_evidence.py tools/tests/test_review_output_pipeline.py tools/tests/test_review_verdict_schema_v2.py tests/tooling/test_framework_adoption.py docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py *> C:/Temp/av-kit/framework-adopt-v17.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v17.txt; exit $code
```

### V18 — Static types of the adopted Python surface

```powershell
rtk proxy uv run pyright tools/durable_evidence.py tools/lint_task_contract.py tools/validate_closeout_artifacts.py tools/validate_json_schema.py tools/adapt_output_schema.py tools/review_ledger.py tools/tests/test_durable_evidence.py tools/tests/test_review_output_pipeline.py tools/tests/test_review_verdict_schema_v2.py tests/tooling/test_framework_adoption.py docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py *> C:/Temp/av-kit/framework-adopt-v18.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v18.txt; exit $code
```

The complete scoped full gate is V17, V18, then V2–V13 on final adoption state, plus V14 before review and V15 after approval. V9 explicitly selects `wrapper-contract`; the script's default `all` invokes live providers and is forbidden for this fixture gate. V10 is fixture-only. Missing prerequisites produce explicit blockers, never fabricated passes. Resolve upstream baseline lint/type findings in the port, never suppress them globally. New check runner assertions are validated by V2. Store actual full argv and per-stage results durably. Before WP-4, run only the checks whose dependencies have been installed; this restriction does not reduce the final full gate.

### V19 — Exact independent approval gate

The three complete executable V19 commands are in both H1-7 and H2-4 task validation cells. Run them as separate invocations in order; any failure stops the sequence. It runs review-state extraction, approved-state validation, then the verifier's `approval` mode, stopping at the first nonzero exit. It never accepts an absent/wrong-mode/wrong-target/over-cap/non-approved review. The initial effective cap is six. A genuine human ledger continuation must first amend the cap literal in both V19 task cells to the exact `rounds_allowed()` value from the ledger and record that authorization; V19's correlation check refuses any mismatch. This is an explicit future human amendment, never automatic cap relief or a new ledger.

The `approval` verifier reads `review-binding.json`, which records the canonical report path, loop ID `framework-update-adoption-execution`, final plan/AC identity, report round and raw final-verdict/status hashes and locations. It loads the ledger through the installed ledger loader, requires the last round's target/kind/intent/schema/producer and verdict to agree, requires successful schema/ledger recording and no unresolved blocking findings, and cross-checks the actual wrapper `status.json`/raw verdict bytes rather than trusting copied strings. It invokes the existing ledger `rounds_allowed()` predicate; do not duplicate its arithmetic. For Mat's human-review route, validate the explicit trusted user decision recorded with its real chat reference in `human-review-decision.md`, named observer, target/revision and manual evidence; no machine dispatch is claimed or fabricated. A file that merely asserts USER_EXPLICIT is insufficient: the orchestrator must have received that decision through the trusted user channel. The reviewer, not the implementor, supplies the substantive verdict.

AC-9 tests call V19 with fixtures for missing/changes_required/stale-body/wrong-target/over-cap reports, forged or mismatched dispatch status, wrong loop intent, invalid continuation, and missing human decision. Positive machine and genuine-human-shaped fixture records must also pass; fixtures never authorize a real execution. H1 final mode checks only H1 prerequisites; the distinct `closeout` mode is used at H2-4 so reflection/metrics cannot form a dependency cycle before review.



### Incremental migration test selectors

All tests live in `tests/tooling/test_framework_adoption.py` and are written in row 1. Test names include the selector labels below; no conditional skip or import-failure substitution is allowed. Imports of future tooling occur within the relevant tested subprocess boundary, so initial Red is an assertion about unmet behavior, not collection failure. Each intermediate row runs only its installed feature contracts. V2 runs **all** groups after the complete port. The bootstrap helper may parse the full manifest but must not mark absent later features passed.

#### V20 — verifier_bootstrap

```powershell
rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -q -p no:cacheprovider -k "verifier_bootstrap" *> C:/Temp/av-kit/framework-adopt-v20.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v20.txt; exit $code
```

#### V21 — verifier_bootstrap or evidence_contract or legacy_review

```powershell
rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -q -p no:cacheprovider -k "verifier_bootstrap or evidence_contract or legacy_review" *> C:/Temp/av-kit/framework-adopt-v21.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v21.txt; exit $code
```

#### V22 — registry_contract

```powershell
rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -q -p no:cacheprovider -k "registry_contract" *> C:/Temp/av-kit/framework-adopt-v22.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v22.txt; exit $code
```

#### V23 — validation_stages

```powershell
rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -q -p no:cacheprovider -k "validation_stages" *> C:/Temp/av-kit/framework-adopt-v23.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v23.txt; exit $code
```

#### V24 — review_pipeline

```powershell
rtk proxy uv run pytest tests/tooling/test_framework_adoption.py -q -p no:cacheprovider -k "review_pipeline and not governance_static_oracles" *> C:/Temp/av-kit/framework-adopt-v24.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/framework-adopt-v24.txt; exit $code
```

## Open Questions

No product behavior question prevents plan review. Execution prerequisites are explicit: source unchanged, shared resolver and current bindings available, and a vendor-distinct reviewer or Mat. Registry/catalog remediation that changes approved choices is a human decision, not an implicit adoption step. No external web research is necessary to compare these pinned local implementations; model availability must be probed at execution rather than inferred from model names in documentation.

## Stop Conditions and Rollback

Stop on source/destination drift, missing required dependency, invalid input/evidence, no eligible independent reviewer, material unresolved policy conflict or exhausted review limits. Persist the exact failure and linked follow-up before using `[B]`. Stop at the existing plan-review three-round cap. Human continuation is not inferred from elapsed time.

Rollback is per manifest entry to the captured **working-tree preimage**, never `git reset --hard`, `git clean`, or a HEAD restore. Only revert a file whose current hash still equals this migration's postimage; otherwise stop to reconcile concurrent edits. Remove only newly created files listed by exact path with verified postimages. Keep evidence of the attempted migration and any review history. No recursive cleanup or source-repo mutation.

## Research References

- Local audit: `upstream-assessment.md` and `upstream-inventory.json`.
- Pinned framework: `core/AGENTS.md`, `core/GUARDRAILS.md`, `core/.agent/docs/verification-principles.md`, `core/.agent/docs/output-evidence-policy.md`, `core/tools/`, `core/templates/`.
- Registry: package `.agent/INSTANTIATE.md`, `.agent/docs/model-classes.md`; live shared resolver/schema, read-only.
- Upstream migration rolling Round 2 review and `docs/execution/plans/2026-09-26-governance-migration/rule-preservation.md`.
- av-kit: `PROJECT-PROFILE.md`, `.agent/context/harness.local.md`, current commands/templates, `tools/check_exec_review.py`, current package manifests, latest Phase 11 reflection.


### Execution command correction (source-backed WP-2)

The installed task linter rejected escaped pipes and nested `pwsh -Command` scriptblocks. Row 0 and artifact-read/metrics/draft checks now use Python argv with preserved exits; V19 is three sequential exact commands in each owning task cell. Predicate, target, cap, authorization and dependency order are unchanged. This corrects executable presentation under the approved AC-2 contract; the gate was not weakened. Receipt: `C:/Temp/av-kit/framework-adopt-v6-initial.txt`.

## Execution sequencing clarification (WP-4)

V24 excludes `governance_static_oracles` until WP-5 supplies the compact root instructions. The original selector inadvertently included the later work package, creating a dependency cycle. All review-tool tests still run in WP-4; V2 in H1 includes every governance oracle and all new regression cases. This is a command-order correction under the approved WP dependency order, not a changed assertion or acceptance criterion.


## Execution review corrections — Round 1

The independent GPT-6 Astra/xhigh review returned changes_required. The direct user message `second round is approved` authorizes the second review after corrections, including the minimum ledger extension needed to admit that round; it is not an implementation verdict. Original scope, immutable baseline and AC IDs are unchanged. The earlier explicit Astra/xhigh instruction remains a one-loop exception; standing model policy is preserved.

| Finding/source | Correction and regression contract | Validation |
|---|---|---|
| R1-F1 / AC-4 / Local Canon | Compute live process environment, registry selection/content, runtime/executable hashes, installed versions and live normalized task inputs before/after validation and reuse. A saved environment JSON alone is insufficient. Changed environment/registry/task validation rejects reuse; task completion cells alone do not. | New live-runtime positive/refusal tests; fresh static → targeted → full gate |
| R1-F2 / AC-5 / Local Canon | Planner pins and the actual registered task command use avkit_builder/avkit_coordinator/avkit_verifier; concrete canonical-template tasks accept each and reject global/unknown classes. Census includes generic class callers and rejects newly introduced global dispatch instructions. | Registered-command matrix and planted generic-caller regressions |
| R1-F3 / AC-9 / Local Canon v2 | Accept genuine approved zero-blocking verdicts with nonblocking findings; preserve exact total findings and correlate report, raw verdict and ledger. Refuse mismatched counts and existing blocking/tampered cases. | Complete real-ledger approval fixture with one Low finding, plus count mismatch |
| R1-F4 / AC-8 / Local Canon | Correct setup guidance link to the existing local routing authority. | Resolve link on disk and review sibling references |
| USER_EXPLICIT Astra/xhigh authorization / Human-approved | Adoption-only approval binding recognizes the exact user quote and recorded hash, same target/loop/model/effort/actual vendors and successful dispatch; missing, changed or mismatched authorization refuses. No registry/wrapper standing-policy change. | 13-case positive/refusal matrix; ordinary same-vendor refusal tests remain unchanged |

Correction work uses the existing approved plan as its contract. The production-only correction workflow's generic file restrictions do not exclude this explicitly authorized governance deliverable; changes stay within its captured allowlist. No product/SSOT changes, baseline recapture, commit or push.
