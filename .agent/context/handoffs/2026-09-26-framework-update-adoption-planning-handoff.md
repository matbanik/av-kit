---
date: "2026-09-26"
project: "framework-update-adoption-planning"
meu: "none"
status: "complete"
action_required: "EXECUTE_ON_USER_DIRECTION"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-26-framework-update-adoption/implementation-plan.md"
build_plan_section: "non-product governance planning"
agent: "Codex planner"
reviewer: "independent Codex CLI"
predecessor: "2026-08-17-agentic-framework-adoption-handoff.md"
---

# Handoff: Framework update adoption planning

## Scope

Inspect `P:/agentic-framework`, compare important updates with the current av-kit working tree, and create a reviewed adoption plan. This is a planning-session handoff, **not** the implementation handoff named by the future H1 task. No product MEU is executed or marked complete.

## Acceptance Criteria

The implementation plan's criteria are fully represented below to preserve the handoff's AC inventory. Their behavior is planned, not implemented. Planning acceptance is the source-backed assessment, actionable plan/task pair and independent plan review.

| AC | Type | Description | Source | Test(s) | Status |
|---|---|---|---|---|---|
| AC-1 | integration | Source and dirty destination preservation | Plan WP-0 | Future migration verifier; not run | Planned |
| AC-2 | integration | Runnable task/closeout and durable evidence | Plan WP-1/2 | Future validator negative cases; not run | Planned |
| AC-3 | integration | Raw/manual review output survives pipeline | Plan WP-4 | Future adapter/schema/ledger cases; not run | Planned |
| AC-4 | integration | Current commands and ordered final gates | Plan WP-2 | Future stage/invalidation fixtures; not run | Planned |
| AC-5 | integration | Registry/class resolution and local profile preservation | Plan WP-3 | Future binding/refusal fixtures; not run | Planned |
| AC-6 | integration | Persistent bounded review lifecycle | Plan WP-4 | Future ledger/dispatch fixtures; not run | Planned |
| AC-7 | integration | Historical review compatibility | Plan WP-1/4 | Future old/new review boundary checks; not run | Planned |
| AC-8 | integration | Compact instructions preserve required controls | Plan WP-5 | Future rule/backlink/template checks; not run | Planned |
| AC-9 | integration | Independent implementation review and complete closeout | Plan H1/H2 | Future complete closeout checks; not run | Planned |

<!-- CACHE BOUNDARY -->

## Evidence

### FAIL_TO_PASS

Not applicable to this docs-only planning session; no production code or tests were written. The planned implementation explicitly requires Red-first migration tests and actual negative cases before feature activation.

### Commands Executed

All commands used RTK proxy, all-stream receipts, immediate exit capture and propagation. Full receipt names and decisive output appear in `upstream-assessment.md` and `planning-walkthrough.md` beside the plan.

| Command body | Exit | Key output |
|---|---:|---|
| `git -C P:/agentic-framework rev-parse HEAD` | 0 | `003929c1cafa83359f0695415bbc06074a35f92e` |
| `git -C P:/agentic-framework status --short` | 0 | Empty status; no source writes performed |
| `git status --short` | 0 | Existing unrelated governance/UI/test/spec changes recorded before planning writes |
| `python C:/Temp/av-kit/adoption_inventory.py` | 0 | 130 tracked source files compared; 17 missing, 74 different, 38 equal, 1 binary |
| `python C:/Temp/av-kit/check_adoption_plan_docs.py` | 0 | 11 required sections; 21 rows all unstarted; 9 ACs; dependencies/columns/inventory valid |
| `codex login status`; `codex --version` | 0 each | ChatGPT login; 0.157.0 |

### Quality Gate Results

Planning document inspection passed. Product pytest/pyright/ruff/Vitest/Electron suites were not run: the user requested a plan, and current SIGN 1 prohibits pre-approval project execution. Independent review status is recorded below. No absent future validator is claimed to have passed.

## Changed Files

| File | Action | Summary |
|---|---|---|
| `docs/execution/plans/2026-09-26-framework-update-adoption/implementation-plan.md` | new | Selective five-package migration plus baseline; preservation, contracts, validation and rollback |
| Same folder `task.md` | new | Future implementation/H1/review/H2 rows; no execution claim |
| Same folder `upstream-assessment.md`, `upstream-inventory.json`, `planning-walkthrough.md` | new | Ranked comparison and durable planning evidence |
| Rolling plan-critical-review | reviewer-owned | Independent findings/verdict; never self-authored |
| This planning handoff and planning reflection | new | Honest planning closeout and instruction coverage |

No existing production, instruction, state or metrics file is intentionally changed by the planner. Product focus remains on Phase 11 Session 24.

## Codex Validation Report

The first attempt ended without a verdict. Replacement round 1 returned three High findings. The independent response passed an installed-jsonschema validation and target/verdict/count checks, although the wrapper itself exited 1 because its schema-validation helper is absent. Round 2 completed with wrapper exit 0 and one procedural correction-census finding; it did not adjudicate the substantive corrections. The correction log now individually dispositions 48 sites covering all 84 raw matches, verified against actual plan/task text. Round 3 independently approved the plan with zero findings; wrapper and child exit were both 0. The target-bound frontmatter and dispatch status were verified. This completes planning only; all 21 execution rows remain unstarted. The reviewer is separate-context, same-vendor; this limitation is disclosed and permitted by the current local preference-based routing policy. The proposed stricter vendor policy has not been activated.

## Corrections Applied (2026-09-26)

Before a reviewer verdict, static verification corrected the draft's test dependency order and replaced default dispatch-test `all` with explicit `wrapper-contract`. The overlay's compiled JSON/provenance output and exact lint/type commands were added. See planning walkthrough for source evidence and interruption handling.

After Round 1, the plan added an ordered bootstrap, exact target-bound approval commands, full-contract add-only model classes and expanded active-routing coverage. Round 2 changed audit documentation only. See the rolling review's correction log for each site's disposition; no independent approval is claimed by the planner.

## Deferred Items

No requested planning deliverable is silently deferred. Implementation is a separately authorized next phase with all 21 task rows unstarted, not an evidence-gated blocker or completed adoption.

## History

| Event | Date | Agent | Detail |
|---|---|---|---|
| Assessment and plan created | 2026-09-26 | Codex planner | Current local source pinned; dirty destination preserved |
| Independent review dispatched | 2026-09-26 | Codex planner | Interrupted original attempt; replacement round 1 uses existing wrapper |

| Independent plan review approved | 2026-09-26 | Independent Codex CLI | Round 3 approved, zero findings; adoption execution remains subject to explicit user direction |
