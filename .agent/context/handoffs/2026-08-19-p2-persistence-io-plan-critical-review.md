---
date: "2026-08-19"
review_mode: plan
target_plan: "docs/execution/plans/2026-08-19-p2-persistence-io/implementation-plan.md"
verdict: approved
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: gpt-5.6-sol
---

# Critical Review: p2-persistence-io — Round 1

## Intent Anchor

Executing this plan is supposed to create `packages/infrastructure` with a SQLite seven-table UoW plus filesystem and FFmpeg adapters for MEU-5 and MEU-8, implementing the frozen Phase 1 ports through TDD evidence. It must not pull in the MEU-6/7/9 external adapters, services, REST, MCP, or GUI work.

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| F1 | High | High | **The MEU/BUILD_PLAN state-transition controls demonstrably false-pass.** Task 13's command only serializes the current count of `p2-persistence-io` matches and has no failing assertion; the hub already contains that slug while both MEUs remain `pending` with `execution_plan: null`. H1-3 then runs `render --check`, whose implementation checks only whether generated regions differ from the current YAML, not whether MEU-5/8 became `ready_for_review` or gained the plan path. H2-2 validates reflection markers but never asserts that either MEU became `approved`. Thus all scheduled gates can pass while the plan's own state deliverables remain absent. This violates PR-4 and PR-8 and the evidence-first task contract. | `task.md:50`, `task.md:55`, `task.md:64`; `.agent/context/meu-status.yaml:166`, `.agent/context/meu-status.yaml:186`, `.agent/context/meu-status.yaml:238`, `.agent/context/meu-status.yaml:258`; `tools/meu_status.py:152`; `docs/BUILD_PLAN.md:64` | Add exact post-state assertions for both row keys at each transition: expected status, exact `execution_plan`, rendered phase state, and the rewritten Next target. H2 must assert `approved`, not merely reflection structure. | open |
| F2 | High | High | **AC-5.14 can pass a UoW that does not commit on successful context exit.** The governing spec and the plan's own lock require “commit on success; rollback on exception,” but the AC only proves that an explicit `commit()` persists and its control binding supplies only the exception-path oracle. An implementation whose `__exit__` rolls back on exceptions, closes, and otherwise does nothing would satisfy the stated AC when the test calls `commit()` explicitly, while violating the required UoW lifecycle. This is a concrete PR-4/PR-8 false pass on the core MEU-5 transaction boundary. | `implementation-plan.md:127`, `implementation-plan.md:191`, `implementation-plan.md:196`; `task.md:42`; `docs/build-plan/02-infrastructure.md:302` | Make the success oracle explicit: add within a successful `with uow:` block, do not call `commit()`, exit, then verify through a fresh UoW that the row persisted. Retain the exception rollback oracle and verify session close separately if close-on-exit remains a plan lock. | open |
| F3 | High | High | **MEU-5 does not bind the frozen storage-port signatures, despite the carry-forward exact-signature rule and live prose conflicts.** AC-5.8/5.12/5.13 enumerate method names and behavior, while only MEU-8's AC-8.12 uses `inspect.signature`. That permits storage adapters with Phase 2 prose shapes such as `reset_failed(id)`, `set(namespace, key, value, value_type)`, or `mark_downloaded(id, path, size_bytes)` to pass name/behavior checks even though the frozen ports require `reset_failed()`, `set(setting)`, and `mark_downloaded(variant_id, path)`. Such adapters are structurally incompatible with the UoW consumed by later services, so the plan can fail its frozen-port objective. This violates PR-4 and carry-forward RULE-3. | `implementation-plan.md:86`, `implementation-plan.md:90`, `implementation-plan.md:91`, `implementation-plan.md:114`, `implementation-plan.md:185`, `implementation-plan.md:189`, `implementation-plan.md:190`, `implementation-plan.md:253`; `task.md:42`; `packages/core/src/avkit_core/ports/storage.py:32`, `packages/core/src/avkit_core/ports/storage.py:88`, `packages/core/src/avkit_core/ports/storage.py:102` | Extend the MEU-5 FIC and Red tests with one exact `inspect.signature` table for every frozen storage Protocol method, including parameter names and kinds. Keep concrete-only extras outside the Protocol tables. | open |
| F4 | Low | High | **PR-9 named literals are still restated.** `HANDOFF_GLOB` is spelled out twice in the plan, and the `SCAN_*`/`REFLECTION_MARKERS` literals are defined as named sets and then recopied across the plan and task. This is clerical under the Materiality Gate and does not block by itself. | `implementation-plan.md:45`, `implementation-plan.md:103`, `implementation-plan.md:104`, `implementation-plan.md:108`, `implementation-plan.md:341`, `implementation-plan.md:367`, `implementation-plan.md:379`; `task.md:48`, `task.md:49`, `task.md:58`, `task.md:64`, `task.md:89` | Keep one canonical statement per literal cluster and reference its owner by name from the other sites. | open |
| F5 | Low | High | **The task frontmatter says `in_progress` although execution is statically unstarted.** All implementation rows are unchecked and the infrastructure package, tests, and MEU handoffs are absent, so the correct planning-state label is trivially inferable. This is a clerical PR-2 note and does not block by itself. | `task.md:5` | Use the repository's unstarted/draft status value until execution begins. | open |

## Verdict

`changes_required` — F1–F3 are evidence-backed High findings. As written, the plan can report successful closeout while MEU state never transitions, can accept a UoW that omits commit-on-success, and can accept storage adapters that do not implement the frozen Protocol signatures. Those are material failures of the planned objective, not template or wording defects.

## Scope

**Targets:**

- `docs/execution/plans/2026-08-19-p2-persistence-io/implementation-plan.md`
- `docs/execution/plans/2026-08-19-p2-persistence-io/task.md`

**Authorities:** `docs/build-plan/02-infrastructure.md` §Database, §ORM/UoW, §Filesystem, §Media; frozen `storage.py`, `filesystem.py`, and `media.py`; Session 2 grouping lock; approved Session 1 reflection carry-forward.

**Review type:** Unstarted plan review, round 1. Static evidence only. No product tests, type checks, lints, git operations, or implementation review were performed.

## Checklist Results

### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both targets scope MEU-5 then MEU-8 and use the same product/test/handoff outputs. |
| PR-2 Not-started confirmation | pass with Low note | `Test-Path` is false for `packages/infrastructure`, both planned integration tests, and both MEU handoffs; every task row is unchecked. F5 records frontmatter drift. |
| PR-3 Task contract completeness | pass | Every executable row provides task, owner, deliverable, validation, dependency, context strategy, durable output, and status. |
| PR-4 Validation realism | fail | F1–F3 demonstrate material false passes. |
| PR-5 Source-backed planning | pass | ACs and locks cite Spec, Local Canon/carry-forward, Research-backed sources, or the frozen ports. No unsourced behavior was elevated to a blocker. |
| PR-6 Handoff/corrections readiness | pass | Two explicit MEU handoffs and one rolling implementation-review path are named. This is round 1, so the correction-census procedural gate is not yet applicable. |
| PR-7 / C2 Scope discipline | pass | Session 2 contains only MEU-5 and MEU-8. Deferred MEU-6/7/9 and later ranges exist in `meu-status.yaml`; no external adapter, service, REST, MCP, or GUI deliverable is disguised as out of scope. |
| PR-8 Control reachability/totality | fail | F1 has no observable assertion for the required SSOT transitions; F2 omits the successful-exit transaction oracle. Other reviewed controls name production adapter/UoW entrypoints and negative outcomes. |
| PR-9 Single-statement discipline | fail, non-blocking | F4. |

### C3 / AC Coverage

| Check | Result | Evidence |
|-------|--------|----------|
| Every plan AC scheduled in task rows | pass | MEU-5 AC-5.1–5.17 are assigned across rows 1/3/5 and MEU-8 AC-8.1–8.12 across rows 7/9. |
| Multi-MEU handoff AC census scheduled | pass | H1-6a requires the complete unique plan AC set across the two canonical handoffs. |
| Integration AC lifecycle | pass at plan level | Integration-labeled ACs are assigned to the planned integration test files; execution evidence does not yet exist and was not claimed. |

### Static / Documentation Integrity

| Check | Result | Evidence |
|-------|--------|----------|
| Frozen ports were not scheduled for mutation | pass | Plan and task repeatedly prohibit core-port edits; files are review authorities only. |
| Grouping lock honored | pass | No invented MEU IDs; product work is limited to MEU-5/8. |
| Referenced executable existence | pass with expected absence | `tools/Invoke-CodexDispatch.ps1` and `tools/meu_status.py` exist. `tools/validate_closeout_artifacts.py` is absent but the plan schedules substitute marker receipts, so the Materiality Gate does not elevate the absence. `tools/validate_codebase.py` is not a dependency of this plan. |
| Review target state | pass | The canonical review file did not exist before this round; no MEU-5/8 implementation handoff exists. |

## Commands Executed

All shell output was redirected under `C:/Temp/av-kit/` and consumed after exit capture.

- `rtk read` for the workflow, review template, harness/governance context, targets, build-plan authorities, frozen ports, grouping lock, prior reflection, and command reference.
- `Test-Path` census for the infrastructure package, planned tests, MEU handoffs, and canonical review path (`review-not-started-state.json`).
- `rtk proxy rg -n` sweeps for plan/task alignment, headings and source lines, C2 MEU registration, PR-9 repeated literals, frozen signatures, state transitions, and current SSOT/hub state.
- Referenced executable extraction plus `Test-Path` (`review-sweep8-existence.json`).
- `rtk proxy uv run python tools/meu_status.py update --help` to verify the scheduled update interface only.
- Static read of `tools/meu_status.py` to establish that `render --check` delegates to drift checking rather than desired-state validation.

## Open Questions / Assumptions

None. The task-table file state, rather than the stale `in_progress` frontmatter value, was used for the unstarted-plan determination.

## Required Follow-up

Route F1–F5 through `/plan-corrections`. On round 2, the resubmission must satisfy PR-6's blast-radius gate: name the untruncated census receipt and provide a per-`file:line` disposition for every hit before content re-review.

## Residual Risk

This was deliberately a static plan review. Runtime SQLAlchemy, SQLite, filesystem, and FFmpeg behavior remains unverified until an approved plan enters execution and produces Red/Green receipts; no such execution evidence was expected or requested in this round.

---

## Corrections Applied (2026-08-19)

**Workflow**: `/plan-corrections` inline from `/create-plan` §5b  
**Agent**: coordinator (implementer) — verdict is `corrections_applied`, **not** `approved`  
**Census index**: `C:/Temp/av-kit/census-p2-plan/census-index.txt` plus the enumerated receipts in `C:/Temp/av-kit/census-p2-plan/` (manifest: `C:/Temp/av-kit/census-p2-plan/MANIFEST.txt`). **Do not** glob `C:/Temp/av-kit/census-*.txt` — that directory also contains leftover Session 1 p1-domain-foundation receipts.

Blast-radius census: **K=5** finding clusters, **V=19** fixed-string sweeps, **N=43** `file:line` hits in nonzero receipts, **M=29** updated, **N-M=14** confirmed-consistent.

### Finding disposition

| ID | Result | What changed |
|----|--------|--------------|
| F1 | updated | Task 13 / H1-3 / H2-2 now run Verification Plan §7 `SSOT_PLAN_BOUND` / `SSOT_READY` / `SSOT_APPROVED`. Those receipts assert `execution_plan == PLAN_FOLDER`, YAML `PLAN_FOLDER_SLASH`, hub `HUB_NEXT_AFTER`, forbidden leftover hub Next, plus `ready_for_review` then `render --check` (H1-3) and `approved` then `REFLECTION_MARKERS` (H2-2). Count-only `p2-persistence-io` / `build-plan-audit.json` oracles are gone. |
| F2 | updated | AC-5.14 success oracle is clean `with uow:` with **no** in-block `commit()`, then a fresh UoW `get()`. Failure oracle unchanged. UoW lock: `__exit__` commits when `exc_type is None`. Task rows 5–6 bind that oracle. |
| F3 | updated | AC-5.18 + named set `STORAGE_PROTOCOL_SIGNATURES` (`inspect.signature` vs frozen `storage.py`). Task row 5 Red tests include AC-5.18; row 6 Green is AC-5.1–AC-5.18. |
| F4 | confirmed-consistent | Canonical glob remains `HANDOFF_GLOB` at `implementation-plan.md:107`. Other hits are the named-set pointer, §6 receipt bodies, or `Get-ChildItem -Filter` copies of that owner. Wildcard is not restated in the Handoff Set prose. Clerical PR-9 leftover; not re-blocked. |
| F5 | updated | `task.md` frontmatter `status: "draft"`. No leftover `in_progress` in either plan file. |

### Blast-radius census (PR-6)

**Zero-hit old receipts** (stale gone — `updated`):

- `census-status-old.txt` — `status: "in_progress"`
- `census-in-progress-any.txt` — `in_progress`
- `census-audit-old.txt` — `build-plan-audit.json`
- `census-count-oracle-old.txt` — `matches=$matches.Count`
- `census-ac517-old.txt` — `AC-5.16–AC-5.17`
- `census-uow-noblock-new.txt` — markdown-stripped `without an in-block` (variant; live spelling uses `**without**` — see `census-inblock-new.txt`)

**Per-hit dispositions for every nonzero `file:line`:**

| Receipt | file:line | Disposition |
|---------|-----------|-------------|
| `census-status-new.txt` | `task.md:5` | updated |
| `census-status-new.txt` | `implementation-plan.md:6` | confirmed-consistent |
| `census-ssot-bound-new.txt` | `task.md:50` | updated |
| `census-ssot-bound-new.txt` | `implementation-plan.md:311` | updated |
| `census-ssot-bound-new.txt` | `implementation-plan.md:391` | updated |
| `census-ssot-bound-new.txt` | `implementation-plan.md:394` | updated |
| `census-ssot-ready-new.txt` | `implementation-plan.md:311` | updated |
| `census-ssot-ready-new.txt` | `implementation-plan.md:397` | updated |
| `census-ssot-ready-new.txt` | `implementation-plan.md:400` | updated |
| `census-ssot-ready-new.txt` | `task.md:55` | updated |
| `census-ssot-approved-new.txt` | `task.md:64` | updated |
| `census-ssot-approved-new.txt` | `implementation-plan.md:311` | updated |
| `census-ssot-approved-new.txt` | `implementation-plan.md:403` | updated |
| `census-ssot-approved-new.txt` | `implementation-plan.md:406` | updated |
| `census-ac518-range-new.txt` | `task.md:42` | updated |
| `census-ac518-new.txt` | `task.md:42` | updated |
| `census-ac518-new.txt` | `task.md:43` | updated |
| `census-ac518-new.txt` | `implementation-plan.md:89` | updated |
| `census-ac518-new.txt` | `implementation-plan.md:199` | updated |
| `census-sigs-new.txt` | `task.md:42` | updated |
| `census-sigs-new.txt` | `task.md:43` | updated |
| `census-sigs-new.txt` | `implementation-plan.md:89` | updated |
| `census-sigs-new.txt` | `implementation-plan.md:199` | updated |
| `census-uow-oracle-new.txt` | `implementation-plan.md:195` | updated |
| `census-inblock-new.txt` | `implementation-plan.md:201` | updated |
| `census-inblock-new.txt` | `task.md:42` | updated |
| `census-success-oracle-new.txt` | `task.md:42` | updated |
| `census-success-oracle-new.txt` | `implementation-plan.md:131` | updated |
| `census-render-check.txt` | `task.md:55` | updated |
| `census-render-check.txt` | `implementation-plan.md:358` | confirmed-consistent |
| `census-render-check.txt` | `implementation-plan.md:397` | confirmed-consistent |
| `census-render-check.txt` | `implementation-plan.md:400` | updated |
| `census-handoff-glob.txt` | `implementation-plan.md:45` | confirmed-consistent |
| `census-handoff-glob.txt` | `implementation-plan.md:107` | confirmed-consistent |
| `census-handoff-glob.txt` | `implementation-plan.md:363` | confirmed-consistent |
| `census-handoff-glob.txt` | `task.md:34` | confirmed-consistent |
| `census-handoff-glob.txt` | `task.md:58` | confirmed-consistent |
| `census-handoff-glob.txt` | `task.md:59` | confirmed-consistent |
| `census-glob-wildcard.txt` | `task.md:58` | confirmed-consistent |
| `census-glob-wildcard.txt` | `task.md:59` | confirmed-consistent |
| `census-glob-wildcard.txt` | `implementation-plan.md:107` | confirmed-consistent |
| `census-glob-wildcard.txt` | `implementation-plan.md:366` | confirmed-consistent |
| `census-glob-wildcard.txt` | `implementation-plan.md:372` | confirmed-consistent |

`implementation-plan.md:358` is Verification Plan §5 `render --check` as a named fragment consumed by `SSOT_READY`; it is not a standalone H1-3 pass oracle.

### Cross-doc sweep

Plan/task only. No workflow or `AGENTS.md` contract literals were renamed. Grouping Session 2 lock unchanged.

---

## PR-6 isolation (2026-08-19, after Round 2)

Round 2 stopped at PR-6 because the correction log cited `C:/Temp/av-kit/census-*.txt`, which mixed this project's 19 p2 receipts with leftover Session 1 `census-ac212-new.txt` / `census-bitrate-new.txt` / `census-convert-new.txt` / `census-glob-new.txt` / `census-media-new.txt` / `census-scan-new.txt` / `census-vcodec-new.txt` / `census-wp4a-new.txt`.

**Declared receipt set for Round 3** is only:

`C:/Temp/av-kit/census-p2-plan/`

Enumerated files (also `MANIFEST.txt` in that folder): `census-index.txt`, `census-status-old.txt`, `census-status-new.txt`, `census-in-progress-any.txt`, `census-audit-old.txt`, `census-count-oracle-old.txt`, `census-ac517-old.txt`, `census-ssot-bound-new.txt`, `census-ssot-ready-new.txt`, `census-ssot-approved-new.txt`, `census-ac518-range-new.txt`, `census-ac518-new.txt`, `census-sigs-new.txt`, `census-uow-oracle-new.txt`, `census-uow-noblock-new.txt`, `census-uow-lock-new.txt`, `census-inblock-new.txt`, `census-success-oracle-new.txt`, `census-render-check.txt`, `census-handoff-glob.txt`, `census-glob-wildcard.txt`.

`census-uow-lock-new.txt` is a zero-hit variant of the success-oracle lock (`not required for the success oracle` vs live `**not** required`). Disposition: stale phrasing gone / live spelling is `census-success-oracle-new.txt` `implementation-plan.md:131` **updated**.

No additional plan/task edits in this isolation pass. Per-hit table in “Corrections Applied (2026-08-19)” still covers every nonzero hit inside the declared set.

Coordinator frontmatter after this pass: `corrections_applied` (implementer — not an approval).

---

## Recheck (2026-08-19, Round 2)

**Workflow**: `/plan-critical-review` resubmission recheck  
**Agent**: `gpt-5.6-sol`  
**Review Mode**: `plan`

### Intent Anchor

Executing this plan is intended to deliver the Session 2 persistence and I/O infrastructure for MEU-5 and MEU-8 against the frozen storage, filesystem, and media ports. This round cannot determine whether the corrected plan would deliver that objective because the mandatory PR-6 census/log pair is not fully dispositioned.

### PR-6 Pre-Verdict Gate

`changes_required` — the census receipts are present and appear untruncated, but the correction log does not disposition every nonzero `file:line` hit covered by its cited `C:/Temp/av-kit/census-*.txt` wildcard. The wildcard contains 78 raw hits; the log dispositions 43 and leaves 35 undispositioned across eight nonzero receipts: `census-ac212-new.txt` (4), `census-bitrate-new.txt` (3), `census-convert-new.txt` (5), `census-glob-new.txt` (6), `census-media-new.txt` (5), `census-scan-new.txt` (3), `census-vcodec-new.txt` (4), and `census-wp4a-new.txt` (5). Those receipts point to `docs/execution/plans/2026-08-18-p1-domain-foundation/`, but neither `census-index.txt` nor the correction log narrows the cited wildcard so they can be excluded from the declared receipt set. Per PR-6, no corrected plan content was reviewed in Round 2.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| F1-F5 | corrections claimed | Not rechecked; PR-6 stopped content review before verdict analysis. |

### Findings

No severity-rated findings were assessed. The PR-6 failure above is the workflow's pre-verdict procedural exception, so `findings_count` is `0`.

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-6 Handoff/corrections readiness | fail | `C:/Temp/av-kit/census-*.txt` contains 78 raw `file:line` hits, while “Corrections Applied (2026-08-19)” individually dispositions only 43; exact comparison receipt: `C:/Temp/av-kit/pr6-all-hit-coverage.txt`. |
| PR-1-PR-5, PR-7-PR-9; F1-F5 | not reviewed | The PR-6 pre-verdict gate requires stopping before corrected-content review. |

### Commands Executed

Static evidence only; all shell output was redirected under `C:/Temp/av-kit/` and consumed after exit capture.

- Read `.agent/workflows/plan-critical-review.md`, `.agent/workflows/plan-corrections.md` Step 5c, `.agent/context/handoffs/REVIEW-TEMPLATE.md`, and the existing rolling review.
- Enumerated `C:/Temp/av-kit/census-index.txt` and every file matching `C:/Temp/av-kit/census-*.txt` (`C:/Temp/av-kit/pr6-prereq-inventory.txt`).
- Read the index and raw census receipts without head/first-line truncation.
- Compared every raw `file:line` hit against the correction log's per-hit table (`C:/Temp/av-kit/pr6-all-hit-coverage.txt`): 78 total, 43 dispositioned, 35 undispositioned.
- Did not run product pytest, pyright, ruff, git, or any implementation command.

### Follow-up Action

Make the declared receipt set unambiguous and complete, then ensure every nonzero `file:line` hit in that set has an `updated` or `confirmed-consistent` correction-log disposition. In particular, either isolate/name only the 19 p2 census receipts instead of citing the broad `census-*.txt` wildcard, or disposition the 35 additional hits currently included by that wildcard; then resubmit the same plan/task pair for Round 3.

### Residual Risk

F1-F5 and the corrected plan/task content remain unverified in Round 2 because PR-6 prevented content review.

### Verdict

`changes_required` — PR-6 is not satisfied: the declared census wildcard contains 35 nonzero raw hits without per-`file:line` dispositions in the correction log. This is the workflow's procedural exception and is the only issue named this round.

---

## Recheck (2026-08-19, Round 3)

**Workflow**: `/plan-critical-review` resubmission recheck  
**Agent**: `gpt-5.6-sol`  
**Review Mode**: `plan`

### Intent Anchor

Executing this plan is intended to deliver the Session 2 persistence and local-I/O infrastructure for MEU-5 and MEU-8: a SQLite seven-table UoW plus filesystem and FFmpeg adapters implementing the frozen Phase 1 ports through TDD evidence. It must not pull MEU-6/7/9 or later service, REST, MCP, or GUI work into this session.

### PR-6 Pre-Verdict Gate

`pass` — the resubmission explicitly declares only `C:/Temp/av-kit/census-p2-plan/`, enumerated by `MANIFEST.txt`; no `C:/Temp/av-kit/census-*.txt` glob was used. The manifest contains 20 sweep receipts plus `census-index.txt`. All receipts were read in full. The 20 sweeps contain 43 unique nonzero `file:line` hits, and the correction log contains exactly 43 matching per-hit dispositions (`missing: 0`, `extra: 0`). Evidence: `C:/Temp/av-kit/plan-review-r3-pr6-reconciliation.txt`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| PR-6 | failed in Round 2 | Fixed — the isolated manifest is unambiguous, receipts are untruncated, and all 43 nonzero hits are individually dispositioned. |
| F1 High | correction claimed | **Still open** — status/plan checks were added, but the Phase 2 `execution_plans` and hub `Next:` placement oracles remain unanchored and materially false-pass (`implementation-plan.md:391-400`; `task.md:50,55`). |
| F2 High | correction claimed | Fixed — clean `with uow:` exit commits without an in-block `commit()`, and a fresh UoW must observe the row; the exception path must observe no row (`implementation-plan.md:131,195,201`; `task.md:42-43`). |
| F3 High | correction claimed | Fixed — `STORAGE_PROTOCOL_SIGNATURES` and AC-5.18 bind every frozen storage Protocol method to exact names, kinds, annotations, and returns, and are scheduled in Red/Green rows (`implementation-plan.md:89,199`; `task.md:42-43`). |
| F4 Low | confirmed-consistent | Remains a non-blocking PR-9 note — `HANDOFF_GLOB`, `SCAN_*`, and `REFLECTION_MARKERS` have named owners but their executable literals remain copied into plan/task commands. |
| F5 Low | correction claimed | Fixed — both plan and task frontmatter are `status: "draft"`, every task row is unchecked, and no implementation artifact exists (`implementation-plan.md:6`; `task.md:5,38-67`). |

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| F1 | High | High | **The corrected SSOT post-state controls still demonstrably false-pass materially wrong placement.** `SSOT_PLAN_BOUND` and `SSOT_READY` only require `PLAN_FOLDER_SLASH` to occur anywhere in the YAML and `HUB_NEXT_AFTER` to occur anywhere in the hub, while merely forbidding the old exact `Next:` value. They never assert that the plan path is inside phase `"2"` `execution_plans` or that `HUB_NEXT_AFTER` is the actual `Next:` field. The exact planned predicate was reproduced in memory and returned PASS with the plan path under Phase 3 and a hub containing `Roadmap mention: /create-plan p2-external-adapters` plus `Next: TBD`. Therefore task 13/H1-3 can pass while both required post-state deliverables are absent. This violates PR-4 and PR-8; it is the unresolved substance of Round-1 F1, not a new nearby predicate-shape demand. | `implementation-plan.md:306-311,387-400`; `task.md:50,55`; witness `C:/Temp/av-kit/plan-review-r3-f1-false-pass-witness.txt` | Parse the SSOT and assert that phase id `2` contains `PLAN_FOLDER_SLASH` in its `execution_plans`; anchor the hub assertion to the actual `Next:` field containing `HUB_NEXT_AFTER`. Reuse those bound checks in `SSOT_READY`. | open |

### Non-Blocking Correction Note

- **F4 / Low** — `HANDOFF_GLOB` is defined at `implementation-plan.md:107`, but the wildcard is repeated at `implementation-plan.md:366,372` and `task.md:58-59`; the `SCAN_*` and `REFLECTION_MARKERS` values likewise remain copied into their command bodies. No competing spelling implies materially different behavior, so this remains clerical under PR-9 and does not contribute to the verdict.

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both targets schedule MEU-5 then MEU-8, followed by the same H1 review barrier and H2 closeout. |
| PR-2 Not-started confirmation | pass | `packages/infrastructure`, both planned integration tests, both MEU handoffs, the implementation review, and the reflection are absent; MEU-5/8 remain `pending` with `execution_plan: null`; every task row is `[ ]`. |
| PR-3 Task contract completeness | pass | Every executable row has task, owner, deliverable, exact validation, dependency/context, durable output, and status. |
| PR-4 Validation realism | fail | F1 supplies a concrete PASS witness while the Phase 2 plan index and hub `Next:` deliverables are materially wrong. F2/F3 are resolved. |
| PR-5 Source-backed planning | pass | UoW behavior matches `02-infrastructure.md:288-302`; AC-5.18 matches frozen `storage.py`; scope/deferrals resolve to the grouping and registered MEUs. |
| PR-6 Handoff/corrections readiness | pass | Exclusive manifest: 20 sweeps plus index; 43 raw hits; 43 dispositions; zero missing/extra. |
| PR-7 Scope discipline / C2 | pass | Session 2 remains MEU-5 and MEU-8 only. Deferred items name registered MEUs; true out-of-scope rows cite local canon/spec. |
| PR-8 Control reachability/totality | fail | F1's observable is not bound to the required YAML phase or hub field. UoW commit/rollback reachability and storage signature totality now pass. |
| PR-9 Single-statement discipline | partial (Low only) | F4 remains clerical duplication with no material ambiguity. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | partial | PR-6, F2, F3, and F5 correction claims match file state; F1 is only partially corrected. |
| DR-2 Residual old terms | pass | Declared old-value receipts are zero-hit; `in_progress`, count-only, and AC-5.17 range forms are absent. |
| DR-3 Downstream references updated | pass | Task rows consume the corrected AC-5.14/AC-5.18 contracts and canonical handoff paths. |
| DR-4 Verification robustness | fail | F1 demonstrates a material false-pass in task 13/H1-3. |
| DR-5 Evidence auditability | pass | The isolated manifest and correction table reconcile exactly; no Session 1 receipt is in scope. |
| DR-6 Cross-reference integrity | pass | Frozen ports, Phase 2 spec, grouping, plan, and task agree on MEU-5/8 scope. |
| DR-7 Evidence freshness | pass | Round-3 reconciliation reproduces 43 raw hits and zero undispositioned/extra entries from the declared set. |
| DR-8 Completion vs residual risk | pass | The plan remains unstarted; no implementation-complete claim is made. |

### Commands Executed

Static review evidence only. No product pytest, pyright, ruff, build, git, or implementation command was run.

- Read the workflow, shell/evidence policy, harness/governance context, review template, latest peer exemplar, target plan/task, rolling review, Phase 2 UoW authority, frozen storage ports, Session 2 grouping, and Session 1 carry-forward reflection.
- Enumerated only `C:/Temp/av-kit/census-p2-plan/`; read `MANIFEST.txt`, `census-index.txt`, and every manifest-listed raw receipt in full.
- Reconciled raw receipt hits to correction-log dispositions (`RAW=43 LOGGED=43 MISSING=0 EXTRA=0`).
- Ran static `Test-Path` checks for unstarted outputs and referenced existing tools/templates.
- Ran exact occurrence sweeps for the hub/SSOT post-state terms and an in-memory reproduction of the scheduled F1 predicate; no repository file was mutated by the witness.

### Open Questions / Assumptions

None. The F1 witness demonstrates a concrete false-pass without requiring a product decision.

### Required Follow-up / Round Cap

This is plan-review Round 3 of 3. The `changes_required` verdict reaches the configured plan-review cap, so the workflow is at a **HARD STOP**. Do not invoke `/plan-corrections`, begin execution, or start another review round without explicit human direction.

### Residual Risk

F2 and F3 are resolved, and PR-6 is auditable. F1 still allows the planned closeout to claim the required BUILD_PLAN/SSOT transition while the plan is indexed under the wrong phase and the hub has no valid next command. Product behavior remains intentionally unverified because implementation has not started.

### Verdict

`changes_required` — PR-6 passes and F2/F3/F5 are fixed, but F1 remains an evidence-backed High finding with a reproduced material false-pass. F4 is Low only. Because this is Round 3, the plan-review cap is reached and further action requires human direction.

---

## Corrections Applied (2026-08-19, after Round 3 — human `proceed`)

**Workflow**: `/plan-corrections` after explicit human direction to continue past the plan-review cap  
**Agent**: coordinator (implementer) — verdict is `corrections_applied`, **not** `approved`  
**Declared census set (exclusive):** `C:/Temp/av-kit/census-p2-f1fix/`  
Manifest: `C:/Temp/av-kit/census-p2-f1fix/MANIFEST.txt` (only `census-*.txt` in that folder). Hit index: `C:/Temp/av-kit/census-p2-f1fix/HIT-INDEX.txt`.  
Do **not** glob `C:/Temp/av-kit/census-*.txt` or reuse `census-p2-plan/`.

Blast-radius census: **K=1** (F1 placement oracles), **V=17** sweeps, **N=36** nonzero `file:line` hits, **M=36** updated, **0** confirmed-consistent leftover substring oracles (8 zero-hit old receipts).

### Finding disposition

| ID | Result | What changed |
|----|--------|--------------|
| F1 | updated | `SSOT_PLAN_BOUND` / `SSOT_READY` now parse YAML via `tools.meu_status.model.load`: phase `id == PHASE_ID` (`'2'`) must contain `PLAN_FOLDER_SLASH` in `execution_plans`; **no other phase** may list it; `MEU-5`/`MEU-8` `execution_plan == PLAN_FOLDER`; hub has exactly one `HUB_NEXT_FIELD` whose value equals `HUB_NEXT_AFTER`. Substring YAML/hub greps and “forbid old Next” are gone. |
| F2–F5 | unchanged | Not reopened this pass. |

### Blast-radius census (PR-6)

**Zero-hit old receipts** (stale substring oracles gone — `updated`):

- `census-hub-anywhere-old.txt` — `missing HUB_NEXT_AFTER`
- `census-hub-forbid-old.txt` — `hub Next still this plan`
- `census-convertfromjson-old.txt` — `ConvertFrom-Json -InputObject`
- `census-ssot-get-old.txt` — `ssot-get-$key.json`
- `census-yaml-notmatch-old.txt` — `yaml -notmatch`
- `census-hub-notmatch-old.txt` — `hub -notmatch`
- `census-rtk-strip-old.txt` — `Strip [rtk] lines`
- `census-countonly-old.txt` — `count-only greps`

**Per-hit dispositions for every nonzero `file:line`:**

| Receipt | file:line | Disposition |
|---------|-----------|-------------|
| `census-chr96-new.txt` | `implementation-plan.md:403` | updated |
| `census-chr96-new.txt` | `implementation-plan.md:409` | updated |
| `census-chr96-new.txt` | `task.md:50` | updated |
| `census-chr96-new.txt` | `task.md:55` | updated |
| `census-hub-count-new.txt` | `task.md:50` | updated |
| `census-hub-count-new.txt` | `task.md:55` | updated |
| `census-hub-count-new.txt` | `implementation-plan.md:403` | updated |
| `census-hub-count-new.txt` | `implementation-plan.md:409` | updated |
| `census-hub-next-field-new.txt` | `task.md:50` | updated |
| `census-hub-next-field-new.txt` | `implementation-plan.md:90` | updated |
| `census-hub-next-field-new.txt` | `implementation-plan.md:312` | updated |
| `census-hub-next-field-new.txt` | `implementation-plan.md:398` | updated |
| `census-hub-value-new.txt` | `task.md:50` | updated |
| `census-hub-value-new.txt` | `task.md:55` | updated |
| `census-hub-value-new.txt` | `implementation-plan.md:403` | updated |
| `census-hub-value-new.txt` | `implementation-plan.md:409` | updated |
| `census-load-new.txt` | `task.md:50` | updated |
| `census-load-new.txt` | `task.md:55` | updated |
| `census-load-new.txt` | `task.md:64` | updated |
| `census-load-new.txt` | `implementation-plan.md:403` | updated |
| `census-load-new.txt` | `implementation-plan.md:409` | updated |
| `census-load-new.txt` | `implementation-plan.md:415` | updated |
| `census-other-phase-new.txt` | `task.md:50` | updated |
| `census-other-phase-new.txt` | `task.md:55` | updated |
| `census-other-phase-new.txt` | `implementation-plan.md:403` | updated |
| `census-other-phase-new.txt` | `implementation-plan.md:409` | updated |
| `census-phase-id-new.txt` | `implementation-plan.md:89` | updated |
| `census-phase-id-new.txt` | `implementation-plan.md:395` | updated |
| `census-phase2-missing-new.txt` | `task.md:50` | updated |
| `census-phase2-missing-new.txt` | `task.md:55` | updated |
| `census-phase2-missing-new.txt` | `implementation-plan.md:403` | updated |
| `census-phase2-missing-new.txt` | `implementation-plan.md:409` | updated |
| `census-yaml-substr-old.txt` | `task.md:50` | updated |
| `census-yaml-substr-old.txt` | `task.md:55` | updated |
| `census-yaml-substr-old.txt` | `implementation-plan.md:403` | updated |
| `census-yaml-substr-old.txt` | `implementation-plan.md:409` | updated |

`census-yaml-substr-old.txt` matches the new Python `SystemExit` text `phase 2 execution_plans missing PLAN_FOLDER_SLASH` (the old `$yaml -notmatch` oracle is gone; see `census-yaml-notmatch-old.txt` EXIT 1).

### Cross-doc sweep

Plan/task only. Grouping Session 2 lock unchanged. Human authorized this round after the r3 cap.

---

## Recheck (2026-08-19, Round 4 — human-authorized continuation)

**Workflow**: `/plan-critical-review` resubmission recheck  
**Agent**: `gpt-5.6-sol`  
**Review Mode**: `plan`

### Intent Anchor

Executing this plan is intended to deliver the Session 2 persistence and local-I/O infrastructure for MEU-5 and MEU-8: a SQLite seven-table UoW plus filesystem and FFmpeg adapters implementing the frozen Phase 1 ports through TDD evidence. It must not pull MEU-6/7/9 or later service, REST, MCP, or GUI work into this session.

### PR-6 Pre-Verdict Gate

`pass` — Round 4 used only the declared set `C:/Temp/av-kit/census-p2-f1fix/`; it did not glob `C:/Temp/av-kit/census-*.txt` or reuse `census-p2-plan/`. `MANIFEST.txt` names 17 unique `census-*.txt` receipts, the declared directory contains exactly those 17 census files, and every receipt was read in full. The raw receipts contain 36 unique `receipt + file:line` hits; the Round-3 correction table contains exactly 36 matching unique dispositions (`missing: 0`, `extra: 0`), and `HIT-INDEX.txt` matches every receipt. Evidence: `C:/Temp/av-kit/round4-pr6-reconciliation.json`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| PR-6 | passed in Round 3; new correction census required | Pass — the exclusive 17-receipt F1 set is complete, untruncated, indexed, and fully dispositioned. |
| F1 High | open after Round 3 | Fixed — parsed YAML binds `PLAN_FOLDER_SLASH` to phase `id == '2'`, rejects the path from every other phase, and the unique hub `Next: \`...\`` value must equal `/create-plan p2-external-adapters`; task 13 and H1-3 consume byte-identical copies of the plan commands (`implementation-plan.md:89-90,395-409`; `task.md:50,55`). |
| F2 High | fixed in Round 3 | Remains fixed; not reopened by the F1-only correction census. |
| F3 High | fixed in Round 3 | Remains fixed; not reopened by the F1-only correction census. |
| F4 Low | clerical | Remains a non-blocking PR-9 note; no competing spelling or material false-pass was demonstrated. |
| F5 Low | fixed in Round 3 | Remains fixed; plan/task are `draft` and all execution rows remain unchecked. |

### Findings

No severity-rated findings. Under the Verdict Rule, the structured finding set is empty for an `approved` verdict.

### Non-Blocking Correction Note

- **F4 / Low** — named owners remain at `implementation-plan.md:109-114`, while executable handoff/scan/reflection literals are still copied into command bodies such as `implementation-plan.md:365,377` and `task.md:58-59,64`. This is clerical PR-9 duplication only; the copies do not state materially different behavior and therefore do not block approval.

### F1 Adversarial Verification

The corrected predicate was reproduced against six static witnesses. The valid Phase-2/unique-Next case passed. Phase-3-only placement, duplicate cross-phase placement, the exact Round-3 roadmap-mention plus `Next: TBD` witness, a wrong backticked Next value, and duplicate Next fields all failed for the expected reason. Evidence: `C:/Temp/av-kit/round4-f1-bound-witness.txt`.

Plan/task consumption was also compared directly: the `SSOT_PLAN_BOUND` Python command at `implementation-plan.md:403` is byte-identical to task 13 at `task.md:50`; the `SSOT_READY` Python command at `implementation-plan.md:409` is byte-identical to H1-3 at `task.md:55`, and both H1-3 copies retain `render --check`. Evidence: `C:/Temp/av-kit/round4-f1-consumption.json`.

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both targets retain MEU-5 then MEU-8, followed by the same H1 review barrier and H2 closeout; the F1 commands are identical across plan/task. |
| PR-2 Not-started confirmation | pass | 26 semantic task rows exist, zero are checked or in progress, and the infrastructure package, planned tests, MEU handoffs, implementation review, and reflection are absent. MEU-5/8 remain `pending` with `execution_plan: null`. Evidence: `round4-not-started.json`, `round4-current-ssot-state.json`. |
| PR-3 Task contract completeness | pass | Every executable row retains task, owner, deliverable, exact validation, dependencies/context, durable output, and unchecked status. |
| PR-4 Validation realism | pass | F1's corrected commands reject the reproduced material false-pass; F2/F3 remain resolved. No High/Critical false-passing gate remains. |
| PR-5 Source-backed planning | pass | The F1 correction changes only the review-requested SSOT/hub placement oracles; underlying UoW, frozen-port, and scope sources remain unchanged. |
| PR-6 Handoff/corrections readiness | pass | 17 manifest receipts, 36 raw hits, 36 dispositions, zero missing/extra entries, and an exact matching hit index. |
| PR-7 Scope discipline / C2 | pass | The grouping lock remains Session 2 = MEU-5 and MEU-8 only (`grouping/...md:14,114-115`); no external-adapter or later-layer work entered the plan. |
| PR-8 Control reachability/totality | pass | `tools.meu_status.model.load` parses the SSOT; phase membership, cross-phase exclusion, exact MEU plan values, and the unique hub Next value are asserted. The former concrete false-pass is rejected. |
| PR-9 Single-statement discipline | partial (Low only) | F4 remains clerical duplication with no material ambiguity. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass with Low note | F1's correction claim matches live plan/task state and the six-witness reproduction; F4 remains explicitly partial/clerical. |
| DR-2 Residual old terms | pass | All eight old-oracle receipts are zero-hit; the four hits in `census-yaml-substr-old.txt` are the documented new failure message, not the removed raw-YAML predicate. |
| DR-3 Downstream references updated | pass | Task 13 and H1-3 consume the corrected bound commands; H2-2 retains the independent approved-status check. |
| DR-4 Verification robustness | pass | The original Phase-3-only and hub `Next: TBD` false-pass no longer passes. |
| DR-5 Evidence auditability | pass | The exclusive manifest, raw receipts, hit index, and per-hit correction table reconcile exactly. |
| DR-6 Cross-reference integrity | pass | Plan, task, grouping, SSOT model loader, and hub Next target agree on the Session 2 transition. |
| DR-7 Evidence freshness | pass | Round-4 receipts were regenerated from the declared F1 set and current target files. |
| DR-8 Completion vs residual risk | pass | This approves planning readiness only; implementation remains unstarted and no implementation-complete claim is made. |

### Commands Executed

Static plan-review evidence only. No product pytest, pyright, ruff, build, git, or implementation command was run.

- Read the plan-review workflow, terminal/evidence policy, governance/profile context, review template, reviewer role, latest peer plan-review exemplar, target plan/task, rolling review, correction-census contract, grouping lock, and SSOT loader/getter definitions.
- Enumerated only `C:/Temp/av-kit/census-p2-f1fix/`; read `MANIFEST.txt`, `HIT-INDEX.txt`, and every manifest-listed receipt in full.
- Reconciled manifest membership, raw receipt hits, hit-index entries, and correction-log dispositions (`17/17` receipts; `36/36` hits; zero missing/extra).
- Ran static `Test-Path` and task-state checks for unstarted outputs and referenced tools.
- Compared plan/task F1 command bodies and ran the six-case in-memory bound-check witness.
- Read current MEU/hub state through `tools.meu_status.model.load` without mutation.

### Open Questions / Assumptions

None. The human's explicit `proceed` authorized Round 4 after the Round-3 cap; it did not authorize implementation, product tests, commits, or any write outside this review handoff.

### Residual Risk

This is a static pre-execution review. SQLAlchemy, SQLite, filesystem, and FFmpeg behavior remains intentionally unverified until execution begins. F4 leaves minor repeated-literal auditability drift, but no competing value or demonstrated material false-pass remains.

### Verdict

`approved` — PR-6 passes, F1's parsed and field-bound checks reject the Round-3 material false-pass, F2/F3/F5 remain fixed, and no evidence-backed High/Critical finding remains. F4 is Low/clerical only and does not contribute to the verdict.
