---
date: "2026-08-19"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
review_round: 5
---

# Critical Review: p4-rest-api

> **Review Mode**: `plan`
> **Verdict**: `approved`
> **Round**: 5

---

## Intent Anchor

Executing this plan is supposed to deliver MEU-14, MEU-15, and MEU-16 in that order as a TDD-backed `packages/api` FastAPI surface with all 48 Phase 4 routes, dual Bearer auth, total request validation, frozen-service bindings, and committed OpenAPI, without pulling MCP, GUI, distribution, or adapter rewrites into Session 5. As written, it can false-pass an unreachable route, incomplete request-boundary enforcement, and an untested named core control, and it sequences the mandatory MEU quality cycles after all three MEUs instead of between them.

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **`ROUTE_INDEX` proves only path registration and false-passes a missing production binding for `GET /tts/voices`.** The Phase 4 contract requires `TTSPort.list_voices` through the TTS or model service, but the frozen `TTSService` exposes no public `list_voices` method and `ModelService` exposes none. The plan simultaneously limits core edits to the two named locks and reduces the per-route contract requirement to an OpenAPI path census. A registered stub or API-private reach into `TTSService._tts` can therefore satisfy AC-16.6/task 10-11 while violating both the service boundary and “one route -> one service method.” This is a demonstrated PR-8/C3 dead end, not a missing-path issue: the exact 48-path census passes. | `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md:193-194,216,343-345`; `docs/execution/plans/2026-08-19-p4-rest-api/task.md:49-50`; `docs/build-plan/04-rest-api.md:9,243-247,380`; `packages/core/src/avkit_core/services/tts.py:85-103,124`; `packages/core/src/avkit_core/services/models.py:59-86` | Add a source-backed, read-only public service/facade binding for voices without changing a state machine or frozen Protocol, then add a route contract oracle that proves the public call chain and `{ items: VoiceOut[] }` response. Expand C3 coverage so a path-only OpenAPI assertion is not the sole test for any required route behavior. | open |
| 2 | High | High | **The mandatory request-boundary control is not total.** The plan says every body inherits `ApiModel(extra="forbid")`, but MEU-16's Boundary Inventory omits the body-bearing `PUT /transcripts/reorder` surface entirely, and the only extra-field negative oracles cover one registered POST/download and settings. The spec requires every request body and “any POST/PUT” to reject extras. A transcript-reorder model (or another untested body model) can accept/ignore an extra key while every named Red/Green and OpenAPI test passes. This violates the mandatory Boundary Input Contract and PR-8 totality. | `AGENTS.md:218-227`; `docs/build-plan/04-rest-api.md:107,218,420`; `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md:199,246,288,297,324-333`; `docs/execution/plans/2026-08-19-p4-rest-api/task.md:47-50` | Add `PUT /transcripts/reorder` with its schema owner, `{job_ids}` constraints, extra policy, and 422 mapping to the inventory/FIC. Define one named request-body route set and a parametrized negative oracle that submits an extra field to every body-bearing POST/PUT and asserts `ERROR_ENVELOPE` 422. | open |
| 3 | High | High | **`CONSOLE_LEVEL_FROM_METHOD` has no acceptance criterion or negative oracle.** The plan names and schedules the core edit, but task 3 validates only AC-14.*, none of which mention console levels; the later health AC checks only `after_seq`. Current `ConsoleEvent` has no `level`, and `HealthService._process` discards `method_name` after using it as a message fallback. The core edit can be omitted or the API can hard-code `INFO` while all planned tests pass, violating the required `ConsoleEventOut.level` contract and PR-8. | `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md:106,193,239-246,299`; `docs/execution/plans/2026-08-19-p4-rest-api/task.md:42,45-46`; `docs/build-plan/04-rest-api.md:320-323`; `packages/core/src/avkit_core/domain/health.py:11-25`; `packages/core/src/avkit_core/services/health.py:106-125` | Add a source-labeled AC and Red test that drives known and unknown structlog `method_name` values through the production processor and asserts `DEBUG|INFO|WARNING|ERROR|CRITICAL` mapping in the health-console response. Bind the matching Green row to that AC. | open |
| 4 | High | High | **The task sequence violates the mandatory per-MEU FIC -> Red -> Green -> Quality -> handoff cycle.** After MEU-14 Green, task 4 immediately starts MEU-15; after MEU-15 Green, task 8 immediately starts MEU-16. Type/lint, anti-placeholder/contract scans, and all three MEU handoffs are deferred to the shared H1 tail. AGENTS.md requires targeted test/type/lint receipts and a handoff before starting the next MEU. Executing the table literally therefore crosses two MEU boundaries without the P1 gate or durable handoff needed for evidence-first completion/compaction. | `AGENTS.md:243-256,262-267,273-277`; `docs/execution/plans/2026-08-19-p4-rest-api/task.md:41-52,55-62` | Insert a scoped MEU gate and creation/update of the corresponding canonical handoff after each MEU Green row and before the next MEU Red row. Keep H1-6 as a final completeness/refresh check of the three existing handoffs rather than their first creation. | open |
| 5 | Low | High | **One C2 deferral row names the wrong scheduled owner.** `AVKIT_API_TOKEN` runtime/spawn belongs to MEU-17, but compound MCP tools belong to MEU-18. Both are genuinely scheduled outside Session 5, so this is a clerical reference error under the Materiality Gate and does not independently block. | `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md:377`; `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md:44-45,159-166` | Split the row or set “Deferred-to MEU” to `MEU-17, MEU-18`. | open |
| 6 | Low | High | **Several PR-9 named predicates are restated as literals.** Examples include `TTS_SPEED_MIN/MAX` restated as `0.5-2.0`, `HUB_NEXT_AFTER` restated inside command bodies, `EXEC_REVIEW_MAX_ROUND` restated as `--max-round 6`, and the `HANDOFF_GLOB` count restated in two closeout predicates. No divergent live spelling was found, so this is clerical and non-blocking. | `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md:48,96,120,124,330,393`; `docs/execution/plans/2026-08-19-p4-rest-api/task.md:53,61,64,69` | Keep the named table as canonical and reference/generate executable literals from those owners where practical. | open |

## Scope

**Targets**: `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md`; `docs/execution/plans/2026-08-19-p4-rest-api/task.md`  
**Review Type**: unstarted plan review, Round 1  
**Checklist Applied**: PR-1 through PR-9, DR-1 through DR-8, C2/C3, referenced-artifact existence, control reachability/totality, repeated-literal census, Materiality Gate  
**Authority**: `docs/build-plan/04-rest-api.md`; frozen `packages/core/src/avkit_core/services/`; `packages/core/src/avkit_core/domain/wire.py`; Session 5 grouping; `meu-status.yaml`; approved Session 4 carry-forward  
**Out of scope**: plan corrections, product code/tests, runtime quality gates, MCP/GUI/distribution implementation, adapter/port/UoW rewrites

## Commands Executed

- Full static reads of the workflow, review/task templates, both targets, Phase 4 spec, grouping/status registries, harness/project context, current focus, guardrails, frozen service signatures/controls, wire maps, and the latest peer plan-review exemplar. Receipts are under `C:/Temp/av-kit/`.
- `rg` censuses for all 48 routes, service methods, `list_voices`, request-boundary/extra-field oracles, console-level control, C2 deferrals, PR-9 literals, and prior Session 4 carry-forward locks.
- `Test-Path` confirmed `packages/api` and all MEU-14/15/16 handoffs were absent before review. It also confirmed `check_exec_review.py`, `meu_status.py`, and `Invoke-CodexDispatch.ps1` exist; both known validators and planned `export_openapi.py` are absent exactly as disclosed/scheduled.
- Exact static route comparison: `plan_count=48`, `spec_count=48`, `PASS: ROUTE_INDEX exact` (`C:/Temp/av-kit/route-index-compare.txt`).
- Help-only checks confirmed the planned `check_exec_review.py` and `meu_status.py update/render` flags. No git command and no product pytest, pyright, ruff, build, or implementation command was run.

## Checklist Results

### Workflow Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both targets use MEU-14 -> MEU-15 -> MEU-16 and exclude MEU-17+. |
| PR-2 Not-started confirmation | pass | `packages/api` and all three MEU handoffs are absent; every task row is unchecked. |
| PR-3 Task contract completeness | pass | Rows contain task, owner, deliverable, validation, dependency, context strategy, durable output, and status fields. |
| PR-4 Validation realism | fail | Findings 1-4 demonstrate materially unreachable or false-passing controls and invalid MEU gate sequencing. |
| PR-5 Source-backed planning | fail | Existing AC rows have labels, but the frozen voices seam and required console/boundary behavior lack a complete source-backed FIC resolution. |
| PR-6 Handoff/corrections readiness | pass | Three canonical MEU handoff paths and one rolling implementation review are explicit. Round-2 census gate is not applicable. |
| PR-7 Scope discipline / C2 | pass with Low note | Every substantive deferral is scheduled or source-backed; Finding 5 corrects the MEU-17/18 label only. |
| PR-8 Control reachability/totality | fail | Findings 1-3 identify a dead-end producer and two controls with demonstrated negative-oracle gaps. Auth, ErrorEnvelope, START_IF_PROCESSING, atomic settings, TTS conflict, G29 boundaries, and exact route count are otherwise traceable. |
| PR-9 Single-statement discipline | fail (Low) | Finding 6 records consistent but repeated literals; no material ambiguity was found. |

### C2/C3 Results

- **C2 deferral integrity:** pass with the Low MEU-17/18 correction in Finding 5. MCP, GUI, uvicorn/distribution, and named non-MEU deferrals remain outside Session 5 on real scheduled/source bases.
- **C3 AC coverage:** fail. The path census is complete, but `/tts/voices` lacks a legal public producer/functional oracle, `CONSOLE_LEVEL_FROM_METHOD` lacks an AC, and request-body extra rejection is not total across the body-bearing route set.

### Template Information/Design Checks

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | fail (coverage) | Written AC rows are labeled, but Findings 1-3 identify required contract behaviors without complete AC coverage. |
| Validation cells are exact/runnable | fail | Existing tools/flags are real or scheduled, but Findings 1-4 show the predicates/sequence can still false-pass or violate the mandatory MEU gate. |
| BUILD_PLAN audit row present | pass | Task 14 binds MEU-14/15/16, Phase 4 plan path, and `HUB_NEXT_AFTER`. |
| Post-MEU rows present | pass with sequencing failure | H1/H2 rows exist, but Finding 4 requires per-MEU gates/handoffs before the next MEU. |
| Naming/template/frontmatter | pass | Plan/task paths, MEU IDs, template versions, and rolling handoff names are canonical. |

### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Draft/unstarted claims match disk state. |
| DR-2 Residual old terms | pass | No stale Phase 4 route slug or superseded Session 5 MEU set was found. |
| DR-3 Downstream references updated | pass with Low note | Grouping/registry references are current; Finding 5 fixes one combined C2 owner cell. |
| DR-4 Verification robustness | fail | Findings 1-4 identify controls that can escape or are scheduled after their required boundary. |
| DR-5 Evidence auditability | pass | Static receipts, line references, existence checks, and help outputs are reproducible. |
| DR-6 Cross-reference integrity | fail | The plan's two-core-edit lock and route/service contract leave `/tts/voices` without a legal producer. |
| DR-7 Evidence freshness | pass | Targets and authorities were reread from current disk state on 2026-08-19. |
| DR-8 Completion vs residual risk | pass | No implementation-complete claim is made. |

## Open Questions / Assumptions

- Frozen Protocols, adapters, UoW, and service state machines remain authoritative. Finding 1 does not authorize a Protocol or state-machine rewrite; it requires an explicit read-only public binding/facade resolution.
- The approved `SETTINGS_UI_API_KEYS={theme}`, atomic `set_namespace`, route-level `START_IF_PROCESSING`, `TTS_NO_MODEL_CONFLICT`, SABR/device lowercase wire mappings, transcript aggregate computation from `list_items`, G29 import exception, `compact_continue`, and `HUB_NEXT_AFTER=/create-plan p5-mcp-server` are accepted and are not findings.
- The disclosed absence of `tools/validate_codebase.py`, `tools/validate_closeout_artifacts.py`, and pre-MEU-16 `tools/export_openapi.py` is not a defect.

## Out-of-Contract Observations

None.

## Follow-Up Actions

1. Run `/plan-corrections` for Findings 1-6; do not begin execution.
2. Resolve the frozen-service voices binding and add functional per-route/C3 coverage beyond the 48-path OpenAPI census.
3. Make extra-field rejection total across every request-body route and add the missing transcript-reorder boundary contract.
4. Bind `CONSOLE_LEVEL_FROM_METHOD` to an AC/Red oracle and insert the per-MEU gates/handoffs before each next-MEU Red row.
5. On Round 2, provide the required untruncated blast-radius census and per-hit dispositions before content re-review.

## Residual Risk

The plan correctly preserves Session 4's frozen machines except the two named locks, resolves the Phase 4 `ui.rail` wording in favor of `{theme}`, maps SABR/device wires independently of PascalCase domain values, computes transcript aggregates from `list_items`, permits `avkit_infra` only in API composition wiring, carries all 48 authoritative paths, and keeps MEU-17+ out of execution. Those surfaces remain static plan claims until implementation and independent execution review prove them.

## Verdict

`changes_required` — Findings 1-4 are evidence-backed High defects: executing the task can register an unreachable `/tts/voices` route, accept extras on untested request bodies, omit or mis-map required console levels, and cross MEU boundaries without the mandatory quality gate/handoff. Findings 5-6 are clerical Low corrections and do not independently affect the verdict.

---

## Corrections Applied (2026-08-19)

Round-1 findings 1–6 addressed in plan/task only (no product code). Frontmatter `verdict` is `corrections_applied` — this agent does not set `approved`.

| # | Severity | Disposition |
|---|----------|-------------|
| 1 | High | Added named lock `VOICES_FACADE` (public `TTSService.list_voices()` → `TTSPort.list_voices`; no Protocol/machine rewrite). AC-16.7 is the functional oracle (`{ items: VoiceOut[] }` + call-count ≥ 1). AC-16.6 path census is explicitly not sufficient. Third allowed core edit. |
| 2 | High | Added `PUT /transcripts/reorder` to MEU-16 Boundary Inventory. Named set `BODY_ROUTES` + AC-16.9 parametrized extra-field 422 on every POST/PUT. `test_api_bodies.py`. AC-14.8 remains the `ApiModel` unit; totality waits until all routers exist. |
| 3 | High | AC-14.9 unit oracle through production `HealthService._process` (console route is MEU-15). AC-15.13 HTTP `GET /health/console` level mapping. Task 2/3/4 bind `tests/unit/test_console_level.py`; task 7 binds AC-15.10–15.13. |
| 4 | High | Inserted per-MEU scoped gate + handoff as task rows 4 / 9 / 14 (`WP-14d` / `WP-15e` / `WP-16e`). H1-6 refreshes the existing `HANDOFF_COUNT` set; it does not create it. Numeric table is 17 rows; H1-1 depends on 17. |
| 5 | Low | Split C2: MCP runtime/`AVKIT_API_TOKEN` → MEU-17; compound `avkit_*` tools → MEU-18. |
| 6 | Low | TTS generate speed cites `TTS_SPEED_MIN`/`TTS_SPEED_MAX`. Handoff closeout cites `HANDOFF_COUNT`. Exec review cap cites `EXEC_REVIEW_MAX_ROUND`. Executable `--max-round 6` and `$files.Count -ne 3` remain named-set expansions (confirmed-consistent). |

### Blast-radius census

Indexes: `C:/Temp/av-kit/census-p4-plan-r1-index.txt`, `C:/Temp/av-kit/census-p4-plan-r1-index-var.txt`.

**Blast-radius census: K=11 values changed, V=40 variants swept, N=64 sites found, M=54 updated, N-M=10 confirmed-consistent.**

Old literals (`two named locks`, `two named core`, `except two named`, `0.5-2.0`, `0.5–2.0`, `Create three complete`, `expected 3 handoffs`, `AC-16.3–16.8`, combined MCP compound/`AVKIT_API_TOKEN` row): **0 hits** (confirmed-consistent — removed).

Confirmed-consistent expansions (not stale): `first time` (H1-6 “do not create here for the first time”); `--max-round 6` (H1-7/H2-4 = `EXEC_REVIEW_MAX_ROUND`); `Count -ne 3` (H1-6/H2-4 = `HANDOFF_COUNT`); `/create-plan p5-mcp-server` (command bodies = `HUB_NEXT_AFTER`).

| Receipt | file:line | Disposition |
|---------|-----------|-------------|
| census-voices-facade-new | task.md:51–52; implementation-plan.md:23,68,109,199,353–354,367,376 | updated — `VOICES_FACADE` owner + AC-16.7 |
| census-body-routes-new | task.md:51; implementation-plan.md:69,110,252,356,368,382 | updated — `BODY_ROUTES` + AC-16.9 |
| census-handoff-count-new | task.md:64,72; implementation-plan.md:48,112 | updated — `HANDOFF_COUNT` owner |
| census-ac-14-9-new | implementation-plan.md:57,253,275,308 | updated — processor AC + pointer to AC-15.13 |
| census-ac-15-13-new | implementation-plan.md:253,308 | updated — HTTP console-level AC |
| census-ac-16-7-new | implementation-plan.md:353–354,380 | updated — voices functional oracle |
| census-ac-16-9-new | implementation-plan.md:252,356,382 | updated — extra-field totality |
| census-reorder-put-new | task.md:49; implementation-plan.md:110,338 | updated — inventory + Red row |
| census-three-named-core-new | task.md:13; implementation-plan.md:23,398 | updated — three locks |
| census-meu-18-new | implementation-plan.md:393 | updated — compound tools C2 |
| census-meu-17-var | implementation-plan.md:223,392 | confirmed-consistent — runtime/spawn stays MEU-17 |
| census-refresh-existing-new | task.md:64 | updated — H1-6 refresh not first-create |
| census-test-console-level-new | task.md:41–43; implementation-plan.md:275 | updated |
| census-test-api-bodies-new | implementation-plan.md:382; task.md:51 | updated |
| census-tts-speed-min-new | implementation-plan.md:99,340 | updated — named speed bounds |
| census-exec-review-max-round-new | task.md:67,72; implementation-plan.md:130 | updated + confirmed-consistent CLI expansion |
| census-scoped-gate-var | implementation-plan.md:59,64,69; task.md:43,48,53 | updated — per-MEU gates |
| census-list-voices-var | implementation-plan.md:109,354 | updated — public facade only |
| census-two-named-*-old | _(no plan/task hits)_ | confirmed-consistent — stale phrase removed |
| census-first-time-var | task.md:64 | confirmed-consistent — F4 refresh wording |

`[rtk]` header lines are not plan/task hits.

### Sequencing after this correction

Task order: scaffold → MEU-14 Red/Green/gate+handoff → MEU-15 Red/Green/gate+handoff → MEU-16 Red/Green/gate+handoff → G36 → scans → SSOT bind → H1 refresh → exec review → H2.

---

## Recheck (2026-08-19) — Round 2

**Workflow**: `/plan-critical-review`
**Agent**: `gpt-5.6-sol`
**Review mode**: `plan`

### Intent Anchor

Executing this plan is supposed to deliver the MEU-14–16 FastAPI surface as one source-backed, TDD-sequenced Session 5 project without crossing into MEU-17+ or rewriting frozen Session 2–4 contracts beyond the three named core locks. Round 2 must first establish that the Round 1 correction blast radius is fully auditable before the corrected content can be adjudicated.

### Findings

No severity-rated findings were evaluated in Round 2. The mandatory PR-6 pre-verdict procedural gate failed, so the workflow requires `changes_required` naming only that gate and prohibits content review of F1–F6 this round.

### PR-6 Procedural Gate

| Gate | Result | Evidence | Required correction |
|------|--------|----------|---------------------|
| Round-2 blast-radius census is untruncated and every raw `file:line` hit has an `updated` or `confirmed-consistent` disposition | **fail** | Both indexes exist and enumerate `V=40` variants; all 40 indexed receipts exist and each receipt's actual hit count matches its index. However, the indexes total **82 value-hit pairs** and **51 unique `file:line` sites**, while the correction log claims `N=64`, `M=54`, and `N-M=10` (`C:/Temp/av-kit/pr6-receipt-reconcile.txt`; correction log lines 137–169). Eight indexed sites have no explicit `file:line` disposition in the correction log: `implementation-plan.md:60,65,126,327,409` and `task.md:46,56,61` (`C:/Temp/av-kit/pr6-undispositioned-check.txt`). | Reconcile the census arithmetic to a stated counting unit, then add an explicit `updated` or `confirmed-consistent` disposition for every indexed hit, including the eight uncovered sites. Preserve the raw receipts and rerun Round 3. |

The raw receipts themselves are present and untruncated; this failure is the missing/reconcilable per-hit disposition layer required by PR-6, not a claim that a census file is absent.

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 through PR-5 | not evaluated | PR-6 is a pre-verdict gate on Round 2+. |
| PR-6 Handoff/corrections readiness | **fail** | Receipt inventory is complete, but the correction summary count is irreconcilable and eight indexed sites lack explicit dispositions. |
| PR-7 through PR-9 | not evaluated | Corrected content review is prohibited after a PR-6 procedural failure. |
| DR-1 through DR-8 | not evaluated | Same pre-verdict stop applies. |
| C2/C3 and Materiality Gate | not evaluated | F1–F6 were not adjudicated this round. The PR-6 exception is procedural and has no severity. |

### Commands Executed

- Full line-numbered static reads of `implementation-plan.md`, `task.md`, the rolling review/correction log, the plan-review workflow, review template, required role contracts, harness/project context, and guardrails.
- `Test-Path`/inventory confirmation that `packages/api/`, MEU-14–16 implementation handoffs, and the three disclosed tools are absent; only the rolling plan-review handoff exists.
- Exact reads of `C:/Temp/av-kit/census-p4-plan-r1-index.txt` and `C:/Temp/av-kit/census-p4-plan-r1-index-var.txt`.
- Indexed-receipt reconciliation: `40` variants, `82` raw value-hit pairs, `51` unique `file:line` sites, `0` missing receipts, and `0` index/receipt count mismatches (`C:/Temp/av-kit/pr6-receipt-reconcile.txt`).
- Explicit-disposition search for the eight uncovered sites (`C:/Temp/av-kit/pr6-undispositioned-check.txt`).
- No git command and no product pytest, pyright, ruff, build, or implementation command was run.

### Open Questions / Assumptions

- `N` is not defined in the correction log as value-hit pairs, unique `file:line` sites, or another auditable unit. Round 3 needs that definition and a reproducible count.
- No inference is made about whether F1–F6 are substantively fixed; the current plan text was reread, but PR-6 prevents a content verdict this round.

### Follow-Up Actions

1. Use `/plan-corrections` to repair only the PR-6 correction log/census disposition evidence.
2. Do not begin execution.
3. Resubmit Round 3 with reconciled counts and a per-hit disposition for every indexed site.

### Residual Risk

The corrected plan may or may not resolve the six Round 1 findings. Until the census count and per-hit disposition layer reconcile, Round 2 cannot distinguish complete blast-radius correction from omitted variants without violating PR-6.

### Verdict

`changes_required` — PR-6's Round-2 procedural exception applies. The census receipts are complete, but the correction log's `N=64` claim does not reconcile with the indexed receipts and eight indexed `file:line` sites are undispositioned. This verdict contains zero severity-rated findings; F1–F6 remain unadjudicated this round.

---

## Corrections Applied — PR-6 reconcile (2026-08-19)

Doc-only repair of the correction log. Plan/task files were not edited in this pass. Frontmatter `verdict` is `corrections_applied` — this agent does not set `approved`.

### Counting unit (auditable)

| Symbol | Definition | Value |
|--------|------------|-------|
| `V` | Indexed variants (rows in `census-p4-plan-r1-index.txt` + `census-p4-plan-r1-index-var.txt`) | `40` |
| `N_PAIRS` | Raw value-hit pairs (one receipt line matching `implementation-plan.md` or `task.md`) | `82` |
| `N` | Unique `file:line` sites across those pairs | `51` |
| `M` | Unique sites dispositioned `updated` | `44` |
| `N-M` | Unique sites dispositioned `confirmed-consistent` | `7` |

**Blast-radius census: K=11 values changed, V=40 variants swept, N=51 unique `file:line` sites found, M=44 updated, N-M=7 confirmed-consistent.**

Zero-hit variants (`11`): the nine stale old literals plus `first-creation-var` and `two-named-var`. These are not sites. Disposition: confirmed-consistent (phrase absent).

Machine table: `C:/Temp/av-kit/census-p4-r2-unique-sites.txt`, `C:/Temp/av-kit/census-p4-r2-disposition-all.txt`, `C:/Temp/av-kit/census-p4-r2-disposition-check.txt` (`DISP_ROWS=51`, `MISSING=` empty).

The eight Round-2 uncovered sites are now explicit:

| file:line | Disposition | Note |
|-----------|-------------|------|
| implementation-plan.md:60 | updated | WP-15a depends on WP-14d |
| implementation-plan.md:65 | updated | WP-16a depends on WP-15e |
| implementation-plan.md:126 | confirmed-consistent | `HUB_NEXT_AFTER` named-set owner (r1) |
| implementation-plan.md:327 | updated | files table AC-15.10–15.13 |
| implementation-plan.md:409 | confirmed-consistent | SSOT command expands `HUB_NEXT_AFTER` |
| task.md:46 | updated | MEU-15 Red AC-15.10–15.13 |
| task.md:56 | confirmed-consistent | task 17 command expands `HUB_NEXT_AFTER` |
| task.md:61 | confirmed-consistent | H1-3 command expands `HUB_NEXT_AFTER` |

### Per-hit dispositions — all 51 unique sites

| file:line | Disposition | Note |
|-----------|-------------|------|
| implementation-plan.md:23 | updated | three named core locks + `VOICES_FACADE` |
| implementation-plan.md:48 | updated | `HANDOFF_COUNT` owner prose |
| implementation-plan.md:57 | updated | WP-14b AC-14.9 |
| implementation-plan.md:59 | updated | WP-14d scoped gate |
| implementation-plan.md:60 | updated | WP-15a depends WP-14d |
| implementation-plan.md:64 | updated | WP-15e scoped gate |
| implementation-plan.md:65 | updated | WP-16a depends WP-15e |
| implementation-plan.md:68 | updated | WP-16d `VOICES_FACADE` |
| implementation-plan.md:69 | updated | WP-16e `BODY_ROUTES` |
| implementation-plan.md:99 | confirmed-consistent | `TTS_SPEED_MIN`/`MAX` owner (r1) |
| implementation-plan.md:109 | updated | `VOICES_FACADE` named set |
| implementation-plan.md:110 | updated | `BODY_ROUTES` named set |
| implementation-plan.md:112 | updated | `HANDOFF_COUNT` named set |
| implementation-plan.md:126 | confirmed-consistent | `HUB_NEXT_AFTER` owner (r1) |
| implementation-plan.md:130 | confirmed-consistent | `EXEC_REVIEW_MAX_ROUND` owner (r1) |
| implementation-plan.md:199 | updated | frozen-services three locks |
| implementation-plan.md:223 | confirmed-consistent | G29 MEU-17/19 mention (r1) |
| implementation-plan.md:252 | updated | AC-14.8 `BODY_ROUTES` pointer |
| implementation-plan.md:253 | updated | AC-14.9 |
| implementation-plan.md:275 | updated | `test_console_level.py` |
| implementation-plan.md:308 | updated | AC-15.13 |
| implementation-plan.md:327 | updated | health-settings files AC-15.10–15.13 |
| implementation-plan.md:338 | updated | `PUT /transcripts/reorder` inventory |
| implementation-plan.md:340 | updated | TTS generate named speed bounds |
| implementation-plan.md:353 | updated | AC-16.6 not sufficient for voices |
| implementation-plan.md:354 | updated | AC-16.7 `VOICES_FACADE` |
| implementation-plan.md:356 | updated | AC-16.9 `BODY_ROUTES` |
| implementation-plan.md:367 | updated | voices producer sufficiency |
| implementation-plan.md:368 | updated | extra-field totality sufficiency |
| implementation-plan.md:376 | updated | `tts.py` `VOICES_FACADE` |
| implementation-plan.md:380 | updated | TTS tests AC-16.7 |
| implementation-plan.md:382 | updated | `test_api_bodies.py` |
| implementation-plan.md:392 | updated | C2 MEU-17 runtime row |
| implementation-plan.md:393 | updated | C2 MEU-18 tools row |
| implementation-plan.md:398 | updated | OOS three named locks |
| implementation-plan.md:409 | confirmed-consistent | SSOT command expands `HUB_NEXT_AFTER` |
| task.md:13 | updated | estimate three named core locks |
| task.md:41 | updated | MEU-14 Red AC-14.1–14.9 |
| task.md:42 | updated | MEU-14 Green console tests |
| task.md:43 | updated | MEU-14 scoped gate |
| task.md:48 | updated | MEU-15 scoped gate |
| task.md:46 | updated | MEU-15 Red AC-15.10–15.13 |
| task.md:49 | updated | transcripts reorder Red |
| task.md:51 | updated | MEU-16 Red VOICES/BODY |
| task.md:52 | updated | MEU-16 Green VOICES |
| task.md:53 | updated | MEU-16 scoped gate |
| task.md:56 | confirmed-consistent | task 17 expands `HUB_NEXT_AFTER` |
| task.md:61 | confirmed-consistent | H1-3 expands `HUB_NEXT_AFTER` |
| task.md:64 | updated | H1-6 refresh `HANDOFF_COUNT` |
| task.md:67 | updated | H1-7 cites `EXEC_REVIEW_MAX_ROUND` |
| task.md:72 | updated | H2-4 `HANDOFF_COUNT` + `EXEC_REVIEW_MAX_ROUND` |

---

## Recheck (2026-08-19) — Round 3 of 3 (plan-review cap)

**Workflow**: `/plan-critical-review`  
**Agent**: `gpt-5.6-sol`  
**Review mode**: `plan`

### Intent Anchor

Executing this plan is supposed to deliver MEU-14–16 as a TDD-sequenced FastAPI Session 5 project, with each MEU completing its own Red → Green → scoped quality gate → durable handoff cycle before the next MEU begins, while preserving the three named core locks and excluding MEU-17+. The corrected plan now binds the voices, body-route, and console-level controls, but its per-MEU gates still allow materially incomplete work to cross MEU boundaries.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **F4 remains only partially corrected: rows 4/9/14 are not the mandatory complete per-MEU scoped gate.** They run targeted pytest, pyright, and ruff and then validate only four handoff marker strings. The required per-MEU anti-placeholder and contract-consistency/boundary checks are still deferred to shared rows 15–16 after MEU-16. Therefore a MEU-14 or MEU-15 deliverable containing `TODO`/`FIXME`/`NotImplementedError`, a deferred stub, or an unvalidated boundary bypass can pass its named gate, receive a handoff, and start the next MEU. That is the same sequencing false-pass identified in Round 1, not a new nearby-mutation demand: AGENTS requires the scoped gate after each MEU to include type, lint, test, anti-placeholder, and contract-consistency checks. The handoff-order portion also remains invalid because the first handoffs are created in rows 4/9/14, while the mandatory template/latest-peer read does not occur until H1-5; the marker-only predicates do not prove a complete evidence bundle. | `docs/execution/plans/2026-08-19-p4-rest-api/task.md:43,48,53,55,63-65`; `AGENTS.md:141-145,275-278`; `.agent/skills/quality-gate/SKILL.md:3,43-65,114-117` | Add touched-file anti-placeholder/anti-deferral and boundary/contract-consistency checks to each of rows 4/9/14 before its handoff and next-MEU dependency can pass. Put the handoff template/latest-peer read before the first per-MEU handoff (or make it an explicit prerequisite for each), and validate the complete evidence bundle rather than marker presence alone. Keep row 16 as a final project-wide sweep and H1-6 as the refresh/count check. | open |

### PR-6 Procedural Gate

| Gate | Result | Evidence |
|------|--------|----------|
| Round-2+ blast-radius census is untruncated, auditable, and every unique `file:line` hit has a disposition | **pass** | The unchanged indexes contain `V=40`. `census-p4-r2-unique-sites.txt` defines the counting unit as unique `file:line` and reports `N_PAIRS=82`, `N_SITES=51`. `census-p4-r2-disposition-all.txt` reports `N=51`, `M=44`, `N-M=7`; `census-p4-r2-disposition-check.txt` reports `DISP_ROWS=51`, `UNIQUE=51`, `MISSING=` empty, `EXTRA=` empty. The correction log at lines 244–327 carries all 51 per-site dispositions. |

PR-6 therefore no longer blocks content review. The failed Round-2 `N=64` sentence was not reused as evidence.

### F1–F6 Adjudication Against Current Disk State

| Prior finding | Result | Current evidence |
|---------------|--------|------------------|
| F1 `VOICES_FACADE` / functional oracle | **fixed** | `VOICES_FACADE` defines a public `TTSService.list_voices()` delegation and route-only binding (`implementation-plan.md:109,199`). AC-16.6 explicitly excludes path census as sufficient; AC-16.7 names the route → service → port chain, response observable, fake-service call oracle, and private `_tts` negative (`implementation-plan.md:353-354,367,376,380`; `task.md:51-52`). The frozen `TTSPort.list_voices` seam exists at `packages/core/src/avkit_core/ports/tts.py:29`. |
| F2 `BODY_ROUTES` / transcript reorder | **fixed** | `BODY_ROUTES` owns every POST/PUT and requires a parametrized 422 `ERROR_ENVELOPE` oracle (`implementation-plan.md:110,356`). `PUT /transcripts/reorder` is present in `ROUTE_INDEX` and the MEU-16 Boundary Inventory (`implementation-plan.md:166,338`), with Red/test-file bindings (`task.md:49,51`; `implementation-plan.md:382`). |
| F3 console-level producer + HTTP | **fixed** | AC-14.9 exercises the production `HealthService._process` producer with known and unknown method names; AC-15.13 exercises the HTTP console projection (`implementation-plan.md:253,308`). The unit/e2e files and Red/Green/gate rows are bound (`implementation-plan.md:275,327`; `task.md:41-43,46-48`). |
| F4 per-MEU gate + handoff | **still open (High)** | Rows 4/9/14 and H1-6 now have the intended positions/count semantics, but the scoped gate content and pre-handoff source-read ordering remain incomplete as Finding 1 demonstrates. |
| F5 MEU-17 vs MEU-18 C2 split | **fixed** | Runtime/token/discovery is deferred to MEU-17 and compound tools to MEU-18 (`implementation-plan.md:392-393`), matching grouping rows 44–45 and registered SSOT entries. No new MEU IDs were invented. |
| F6 named owners / executable expansions | **fixed** | `HANDOFF_COUNT`, `HUB_NEXT_AFTER`, and `EXEC_REVIEW_MAX_ROUND` remain canonical owners (`implementation-plan.md:112,126,130`). `$files.Count -ne 3`, `--max-round 6`, and `/create-plan p5-mcp-server` occur only as consistent executable expansions (`task.md:56,61,64,67,72`; `implementation-plan.md:409`); no divergent live value was found. |

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both targets implement MEU-14 → MEU-15 → MEU-16; route comparison is exact at 48/48 with no one-sided rows. |
| PR-2 Not-started confirmation | pass | `packages/api/` and MEU-14–16 implementation handoffs are absent; all 30 task rows are unchecked. |
| PR-3 Task contract completeness | pass | Static census found 30 task rows and zero malformed/missing-status rows. |
| PR-4 Validation realism | **fail** | Finding 1 demonstrates a per-MEU scoped gate that materially false-passes missing required quality checks and incomplete handoff evidence. |
| PR-5 Source-backed planning | pass | Static census found 32 AC rows and zero missing Source cells; F1–F3 corrections are source-bound. |
| PR-6 Handoff/corrections readiness | pass | Reconciled 51-site disposition evidence is complete; three canonical MEU handoff paths and rolling implementation review are explicit. |
| PR-7 Scope discipline / C2 | pass | F5 split matches grouping and SSOT; all plan-mentioned MEU IDs found by the static census are registered. |
| PR-8 Control reachability/totality | pass for F1–F3; fail for gate control | `VOICES_FACADE`, `BODY_ROUTES`, and `CONSOLE_LEVEL_FROM_METHOD` now name producers, observables, and negative oracles. Finding 1 demonstrates the remaining gate-control dead end. |
| PR-9 Single-statement discipline | pass | F6 literals are consistent executable expansions of named owners, not ambiguous live contracts. |

| Docs check | Result | Evidence |
|------------|--------|----------|
| DR-1 Claim-to-state match | pass | Draft/unstarted state matches disk. |
| DR-2/DR-3 Residual terms and downstream references | pass | PR-6 has zero missing/extra dispositions; F5/F6 references are current. |
| DR-4 Verification robustness | **fail** | Finding 1. |
| DR-5 Evidence auditability | pass | Static receipts under `C:/Temp/av-kit/` reproduce counts, path existence, route equality, and F1–F6 source checks. |
| DR-6 Cross-reference integrity | **fail** | Task gate rows do not implement the per-MEU gate contract in AGENTS/quality-gate canon. |
| DR-7 Evidence freshness | pass | Targets, correction log, PR-6 receipts, source contracts, grouping, SSOT, and current core seams were reread on 2026-08-19. |
| DR-8 Completion vs residual risk | pass | No implementation-complete claim is made. |

### Commands Executed

- Full static reads of the workflow, review template, role contracts, harness/project/guardrail context, both targets, rolling review history, output policy, command registry, quality-gate skill, relevant Phase 4 source lines, grouping/SSOT entries, and current TTS/health service seams.
- Exact PR-6 reads: `C:/Temp/av-kit/census-p4-plan-r1-index.txt`, `census-p4-plan-r1-index-var.txt`, `census-p4-r2-unique-sites.txt`, `census-p4-r2-disposition-all.txt`, and `census-p4-r2-disposition-check.txt`.
- Static censuses: 32 AC rows / 0 missing sources; 30 task rows / 30 unchecked / 0 malformed; 48 spec routes / 48 plan routes / no differences; referenced executables existence; MEU-ID registration; F6 literal sites.
- No git command and no product pytest, pyright, ruff, build, implementation, or OpenAPI export command was run.

### Open Questions / Assumptions

- None require a product decision. The required fix is procedural/validation scope already stated by AGENTS and the quality-gate canon.
- The disclosed absence of `tools/validate_codebase.py`, `tools/validate_closeout_artifacts.py`, and pre-MEU-16 `tools/export_openapi.py` remains non-finding: the first two are explicitly absent/fallback-routed, and `export_openapi.py` is scheduled in MEU-16.

### Follow-Up Actions

1. **HARD STOP:** this is Round 3 of 3 and the verdict remains `changes_required`; do not run `/plan-corrections` or begin execution without direct human direction.
2. If the human authorizes another correction/review cycle, repair Finding 1 only, preserve F1–F3/F5–F6, and provide a new blast-radius census/disposition layer.

### Residual Risk

The corrected voices, body-route, console-level, C2, and named-literal contracts are plan-complete but remain unexecuted. The active blocking risk is procedural and material: earlier MEUs can still cross into later work before the repository’s full scoped gate and handoff-quality requirements are satisfied.

### Verdict

`changes_required` — one evidence-backed High finding remains. F4 is not fully corrected because rows 4/9/14 omit mandatory per-MEU anti-placeholder and contract-consistency/boundary checks and create handoffs before the required template/latest-peer source read; the later shared scans and H1 refresh do not repair the per-MEU sequencing false-pass. Because this is the third and final plan-review round, the review cap is reached and the workflow must stop for human direction.

---

## Corrections Applied — F4 complete gate (2026-08-19)

Human-authorized extra cycle after the 3-round cap (`USER_EXPLICIT`: continue until `approved`). Plan/task only. Frontmatter `verdict` is `corrections_applied` — this agent does not set `approved`. F1–F3 and F5–F6 were left untouched.

| # | Action |
|---|--------|
| F4 | Named `MEU_SCOPED_GATE`: targeted pytest + pyright + ruff + placeholder + anti-deferral + API-libs + core-infra (when core touched) + quality-gate #11a–d on `MEU*_TOUCHED`. |
| F4 | Named `HANDOFF_SOURCE_READ`: written in task 4 **before** the first handoff. Rows 9/14 reuse it. Validation fails if receipt `LastWriteTime` is after that MEU handoff. |
| F4 | Named `HANDOFF_BUNDLE_MARKERS` (TEMPLATE + completion-preflight): `Quality Gate Results`, `Commands Executed`, `## Evidence` in addition to the four prior markers. Also applied to H1-6 / H2-4 refresh. |
| F4 | H1-5 now **proves** the row-4 receipt; it is not the first template read. Task 16 remains the project-wide sweep only. |

### Blast-radius census

Counting unit: unique `file:line` in the two plan files.

**Blast-radius census: K=9 values changed, V=16 variants swept, N=21 unique `file:line` sites found, M=21 updated, N-M=0 confirmed-consistent.**

Zero-hit old phrases (not sites): `PASS: MEU-14/15/16 handoff`, `view_file: .agent/context/handoffs/TEMPLATE.md` — confirmed-consistent removed.

Indexes: `C:/Temp/av-kit/census-p4-r4-index.txt`, `census-p4-r4-unique-sites.txt`, `census-p4-r4-disposition-all.txt`, `census-p4-r4-disposition-check.txt` (`DISP_ROWS=21`, `MISSING=` empty).

| file:line | Disposition | Note |
|-----------|-------------|------|
| implementation-plan.md:59 | updated | WP-14d `MEU_SCOPED_GATE` + `HANDOFF_SOURCE_READ` |
| implementation-plan.md:64 | updated | WP-15e |
| implementation-plan.md:69 | updated | WP-16e |
| implementation-plan.md:137 | updated | `HANDOFF_TEMPLATE` |
| implementation-plan.md:138 | updated | `HANDOFF_SOURCE_READ` |
| implementation-plan.md:139 | updated | `HANDOFF_BUNDLE_MARKERS` |
| implementation-plan.md:140 | updated | `SCAN_ANTI_DEFERRAL_ARGS` |
| implementation-plan.md:141 | updated | `BOUNDARY_AUDIT_ARGS` |
| implementation-plan.md:142 | updated | `MEU14_TOUCHED` |
| implementation-plan.md:143 | updated | `MEU15_TOUCHED` |
| implementation-plan.md:144 | updated | `MEU16_TOUCHED` |
| implementation-plan.md:145 | updated | `MEU_SCOPED_GATE` |
| implementation-plan.md:447 | updated | Verification Plan per-MEU scans |
| task.md:43 | updated | row 4 full MEU-14 gate |
| task.md:48 | updated | row 9 full MEU-15 gate |
| task.md:53 | updated | row 14 full MEU-16 gate |
| task.md:63 | updated | H1-5 reuses row-4 source-read |
| task.md:64 | updated | H1-6 bundle markers |
| task.md:72 | updated | H2-4 bundle markers |
| task.md:91 | updated | row 16 is sweep not per-MEU gate |
| task.md:93 | updated | sequencing: source-read before first handoff |

---

## Recheck (2026-08-19) — Round 4 (human-authorized after cap)

**Workflow**: `/plan-critical-review`  
**Agent**: `gpt-5.6-sol`  
**Review mode**: `plan`

### Intent Anchor

Executing this plan is supposed to deliver MEU-14–16 as a TDD-sequenced FastAPI Session 5 project whose complete scoped quality gate and durable evidence handoff finish before the next MEU begins. The Round-4 correction closes the source-read ordering and handoff-bundle portions of F4, but two per-MEU gate commands still omit a touched service file from blocking quality-gate check #11d.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **F4 remains open because rows 4 and 14 false-pass blocking boundary audit #11d on their touched core services.** The plan defines `BOUNDARY_AUDIT_ARGS` as running `**kwargs` / `**{` against `packages/api/src` **plus that MEU's touched core service file**, matching quality-gate #11d's `touched-service-files` scope. However, the actual #11d commands in both rows scan only `packages/api/src`; neither scans `packages/core/src/avkit_core/services/health.py` (MEU-14) nor `packages/core/src/avkit_core/services/tts.py` (MEU-16). A #11d match in either edited service is therefore invisible while the row can emit its scoped-gate PASS, write the MEU handoff, and unlock the next dependency. This is the same incomplete per-MEU gate from F4, with a named unobserved file and concrete false-pass, not a new nearby-mutation demand. | `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md:141-145`; `docs/execution/plans/2026-08-19-p4-rest-api/task.md:43,53`; `.agent/skills/quality-gate/SKILL.md:61-76` | Add the corresponding touched core service path to the #11d `rg` command in rows 4 and 14. Keep row 9 API-only because MEU-15 touches no core service. Regenerate the Round-5 census/dispositions for the changed sites. | open |

### PR-6 Procedural Gate

| Gate | Result | Evidence |
|------|--------|----------|
| Round-4 blast-radius census is fresh, untruncated, auditable, and every unique `file:line` hit has a disposition | **pass** | Independent reconciliation of the 16 indexed raw receipts produced `V=16`, `N_PAIRS=51`, and `N_SITES=21`; all receipt hit counts match the index, all 21 sites match `census-p4-r4-unique-sites.txt`, and all 21 have dispositions with no missing or extra sites. Receipt: `C:/Temp/av-kit/plan-review-r4-pr6-reconcile.txt`. The Round-2 `N=64` and Round-3 `N=51` values were not reused as this cycle's counting unit. |

PR-6 therefore permits content adjudication in Round 4.

### F1–F6 Adjudication Against Current Disk State

| Prior finding | Result | Current evidence |
|---------------|--------|------------------|
| F1 `VOICES_FACADE` | **fixed; no regression** | Public service facade, route-to-service-to-port chain, response oracle, and private `_tts` negative remain in the named set and AC-16.7. |
| F2 `BODY_ROUTES` | **fixed; no regression** | The every-POST/PUT 422 envelope oracle and transcript reorder boundary remain present. |
| F3 `CONSOLE_LEVEL_FROM_METHOD` | **fixed; no regression** | AC-14.9 still covers the production processor and AC-15.13 the HTTP projection. |
| F4 per-MEU gate + handoff | **still open (High)** | Placeholder, anti-deferral, API-libs, core-infra, and #11a–c are present. #11d is present but under-scoped in rows 4 and 14 as Finding 1 demonstrates. `HANDOFF_SOURCE_READ` ordering, `HANDOFF_BUNDLE_MARKERS`, H1-5 reuse, and row-16 project sweep are corrected. |
| F5 MEU-17 / MEU-18 split | **fixed; no regression** | Runtime/token/discovery and compound tools remain assigned to their registered MEUs. |
| F6 named owners / executable expansions | **fixed; no regression** | Named owners and their consistent executable expansions remain unchanged. |

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both targets retain MEU-14 → MEU-15 → MEU-16 and the same three handoff paths. |
| PR-2 Not-started confirmation | pass | `packages/api/` is absent; no MEU-14–16 implementation handoff exists; all task rows remain unchecked. |
| PR-3 Task contract completeness | pass | Task rows retain owner, deliverable, validation, dependency, strategy, durable outputs, and status. |
| PR-4 Validation realism | **fail** | Finding 1 demonstrates a blocking per-MEU audit that can pass without inspecting a required touched service. |
| PR-5 Source-backed planning | pass | No regression was found in the source-labeled FIC or the corrected F1–F3 controls. |
| PR-6 Handoff/corrections readiness | pass | Fresh 21-site Round-4 census and disposition layer reconcile exactly. |
| PR-7 Scope discipline / C2 | pass | F5 remains fixed; no new MEU or deferral regression was found. |
| PR-8 Control reachability/totality | **fail for gate control** | The #11d observable has no path to either touched core service in rows 4/14. Other previously corrected controls remain reachable. |
| PR-9 Single-statement discipline | pass | No regression in F6 named owners or executable expansions. |

| Docs check | Result | Evidence |
|------------|--------|----------|
| DR-1 Claim-to-state match | pass | Draft/unstarted claims match current disk state. |
| DR-2/DR-3 Residual terms and downstream references | pass | The Round-4 census has no missing/extra sites; prior fixed references remain present. |
| DR-4 Verification robustness | **fail** | Finding 1. |
| DR-5 Evidence auditability | pass | Raw census receipts, reconciliation output, exact task-row command extracts, and existence checks are reproducible under `C:/Temp/av-kit/`. |
| DR-6 Cross-reference integrity | **fail** | `BOUNDARY_AUDIT_ARGS` promises touched-core-service coverage that task rows 4/14 do not execute for #11d. |
| DR-7 Evidence freshness | pass | The targets and all Round-4 census receipts were reread from current disk on 2026-08-19. |
| DR-8 Completion vs residual risk | pass | No implementation-complete claim is made. |

### Commands Executed

- Full static reads of the plan-review workflow, review template, reviewer role, harness/project/guardrail context, both target files, rolling review history, output-evidence policy, and quality-gate skill.
- Not-started checks confirmed `packages/api/` and MEU-14–16 implementation handoffs are absent.
- Fresh PR-6 reconciliation across the 16 indexed raw receipts: `V=16`, `N_PAIRS=51`, `N_SITES=21`, `DISP_ROWS=21`, no missing receipts, count mismatches, site differences, or disposition differences (`C:/Temp/av-kit/plan-review-r4-pr6-reconcile.txt`).
- Exact row extraction confirmed both #11d commands target only `packages/api/src` (`C:/Temp/av-kit/plan-review-r4-f4-11d-segments.txt`) while the named plan contract requires the touched core service too (`C:/Temp/av-kit/plan-review-r4-f4-contradiction.txt`).
- `rtk git status --short` was attempted but the workspace is not a Git worktree (`fatal: not a git repository`); no mutation resulted.
- No product pytest, pyright, ruff, build, implementation, OpenAPI export, or plan-correction command was run.

### Open Questions / Assumptions

- None require a product decision. The required #11d scope is already explicit in both the plan's named set and the quality-gate skill.
- Human authorization permits this extra review round despite the prior cap; it does not authorize this reviewer to patch the plan or chain into `/plan-corrections`.

### Follow-Up Actions

1. Run `/plan-corrections` for Finding 1 only; preserve F1–F3/F5–F6 and the corrected source-read/marker/row-16 portions of F4.
2. Add `packages/core/src/avkit_core/services/health.py` to row 4's #11d scan and `packages/core/src/avkit_core/services/tts.py` to row 14's #11d scan.
3. Produce a fresh Round-5 blast-radius census and per-site dispositions, then rerun `/plan-critical-review`.

### Residual Risk

The plan remains unexecuted. Its handoff source-read ordering, seven-marker bundle checks, prior F1–F3/F5–F6 corrections, and project-wide final sweep are plan-complete; the remaining risk is that MEU-14 or MEU-16 can cross its handoff boundary while a blocking #11d match exists in the edited core service file.

### Verdict

`changes_required` — one evidence-backed High finding remains. F4's per-MEU gate still false-passes quality-gate #11d for the touched core service in rows 4 and 14. PR-6 passes, and no regression was found in F1–F3/F5–F6 or in F4's source-read ordering, handoff-bundle markers, H1-5 reuse, and row-16 sweep semantics.

---

## Corrections Applied — F4 #11d core paths (2026-08-19)

Human-authorized extra cycle. Finding 1 from Round 4 only. Frontmatter `verdict` is `corrections_applied`.

| # | Action |
|---|--------|
| F4 #11d | Row 4 #11d now scans `packages/api/src` **and** `packages/core/src/avkit_core/services/health.py`. |
| F4 #11d | Row 14 #11d now scans `packages/api/src` **and** `packages/core/src/avkit_core/services/tts.py`. |
| F4 #11d | `BOUNDARY_AUDIT_ARGS` now states #11b and #11d include the touched core service. |

Exact command extract: `C:/Temp/av-kit/census-p4-r5-11d-extract.txt`.

### Blast-radius census

**Blast-radius census: K=2 values changed, V=6 variants swept, N=7 unique `file:line` sites found, M=3 updated, N-M=4 confirmed-consistent.**

Counting unit: unique `file:line`. Indexes: `C:/Temp/av-kit/census-p4-r5-index.txt`, `census-p4-r5-unique-sites.txt`, `census-p4-r5-disposition-all.txt`, `census-p4-r5-disposition-check.txt` (`DISP_ROWS=7`, `MISSING=` empty). Old api-only 11d-14 command: 0 hits.

| file:line | Disposition | Note |
|-----------|-------------|------|
| implementation-plan.md:141 | updated | `BOUNDARY_AUDIT_ARGS` #11d + core |
| implementation-plan.md:142 | confirmed-consistent | `MEU14_TOUCHED` already listed `health.py` |
| implementation-plan.md:144 | confirmed-consistent | `MEU16_TOUCHED` already listed `tts.py` |
| implementation-plan.md:282 | confirmed-consistent | MEU-14 files table `health.py` |
| implementation-plan.md:385 | confirmed-consistent | MEU-16 files table `tts.py` |
| task.md:43 | updated | row 4 #11d + `health.py` |
| task.md:53 | updated | row 14 #11d + `tts.py` |

---

## Recheck (2026-08-19) — Round 5 (human-authorized after cap)

**Workflow**: `/plan-critical-review`  
**Agent**: `gpt-5.6-sol`  
**Review mode**: `plan`

### Intent Anchor

Executing this plan is supposed to deliver MEU-14–16 as an unstarted, TDD-sequenced FastAPI Session 5 project whose complete scoped quality gate and durable evidence handoff finish before the next MEU begins. This round adjudicates only the Round-4 #11d defect and checks for regression in the already-fixed F4 source-read, bundle, H1-5, and row-16 pieces; it does not reopen F1–F3 or F5–F6.

### Findings

No High or Critical findings. The Round-4 finding is fixed on current disk.

### Prior Finding Adjudication

| Prior finding | Prior status | Recheck result | Current evidence |
|---------------|--------------|----------------|------------------|
| F4 #11d omitted touched core service files in task rows 4 and 14 | open (High) | **fixed** | Row 4's exact #11d command scans `packages/api/src` plus `packages/core/src/avkit_core/services/health.py`; row 14 scans `packages/api/src` plus `packages/core/src/avkit_core/services/tts.py` (`task.md:43,53`; `C:/Temp/av-kit/p4-r5-independent-11d-unstarted.txt`). This matches `BOUNDARY_AUDIT_ARGS` (`implementation-plan.md:141-145`) and quality-gate #11d's touched-service scope (`.agent/skills/quality-gate/SKILL.md:62-76`). |

### PR-6 Procedural Gate

| Gate | Result | Evidence |
|------|--------|----------|
| Round-5 blast-radius census is fresh, untruncated, auditable, and every unique `file:line` hit has a disposition | **pass** | This cycle's receipts report `V=6`, `N_PAIRS=9`, `N_SITES=7`, `N=7`, `M=3`, `N-M=4`, `DISP_ROWS=7`, and empty `MISSING`. `census-p4-r5-unique-sites.txt` inventories all nine variant/site pairs across seven unique sites; the rolling correction log and `census-p4-r5-disposition-all.txt` disposition all seven sites. The Round-4 `N=21` was not reused. Receipts: `C:/Temp/av-kit/census-p4-r5-index.txt`, `census-p4-r5-unique-sites.txt`, `census-p4-r5-disposition-all.txt`, and `census-p4-r5-disposition-check.txt`. |

PR-6 therefore permits content adjudication in Round 5.

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass (scoped) | The named `BOUNDARY_AUDIT_ARGS` contract and rows 4/14 now agree on #11d touched-service coverage. |
| PR-2 Not-started confirmation | pass | `packages/api/` and the MEU-14–16 handoffs are absent; all 17 numbered task rows remain `[ ]`. |
| PR-3 Task contract completeness | pass (carried forward) | No targeted regression signal; this settled surface was not reopened. |
| PR-4 Validation realism | pass | The prior concrete false-pass is closed because both #11d commands inspect their required touched service file. |
| PR-5 Source-backed planning | pass (carried forward) | F1–F3 were not reopened; no regression was found on the corrected F4 surface. |
| PR-6 Handoff/corrections readiness | pass | Fresh seven-site Round-5 census and disposition layer reconcile exactly. |
| PR-7 Scope discipline / C2 | pass (carried forward) | F5 was not reopened; no regression signal was found. |
| PR-8 Control reachability/totality | pass for adjudicated control | The #11d observable now reaches `services/health.py` in MEU-14 and `services/tts.py` in MEU-16. |
| PR-9 Single-statement discipline | pass (carried forward) | F6 was not reopened; no regression signal was found. |

| Docs check | Result | Evidence |
|------------|--------|----------|
| DR-1 Claim-to-state match | pass | The correction log's two command-scope claims match current `task.md`. |
| DR-2/DR-3 Residual terms and downstream references | pass (scoped) | The seven-site census contains the named-set definition, touched-file inventories, and both corrected task rows with no missing disposition. |
| DR-4 Verification robustness | pass | Independent extraction from current `task.md` confirms both required core paths rather than relying on the correction claim alone. |
| DR-5 Evidence auditability | pass | Exact command extracts, census receipts, disposition check, and not-started receipt are reproducible under `C:/Temp/av-kit/`. |
| DR-6 Cross-reference integrity | pass | `BOUNDARY_AUDIT_ARGS`, `MEU14_TOUCHED`, `MEU16_TOUCHED`, and task rows 4/14 agree. |
| DR-7 Evidence freshness | pass | All Round-5 receipts and target extracts were read from current disk on 2026-08-19. |
| DR-8 Completion vs residual risk | pass | The plan is described as approved for execution, not implemented. |

### Commands Executed

- Read the plan-review workflow, review template, reviewer role, harness/project/guardrail context, output-evidence policy, quality-gate #11 source, both targets' adjudicated surfaces, rolling review history, and all Round-5 census/disposition receipts.
- Independently extracted both #11d commands from current `task.md`; the exact segments and core-path assertions are in `C:/Temp/av-kit/p4-r5-independent-11d-unstarted.txt`.
- Confirmed `packages/api/` and all MEU-14–16 implementation handoffs are absent, and confirmed all 17 numbered task rows remain unchecked.
- No product pytest, pyright, ruff, build, implementation, OpenAPI export, or plan-correction command was run.

### Open Questions / Assumptions

- None. The #11d scope is explicit in the plan and quality-gate skill.
- The user explicitly authorized Round 5 after the plan-review round cap.

### Follow-Up Actions

- None required by this review. Do not chain into another workflow from `/plan-critical-review`.

### Residual Risk

The plan remains unexecuted, so implementation correctness is not established by this plan review. Within the authorized Round-5 scope, the prior #11d false-pass is closed and no regression was found in F4's already-corrected source-read ordering, handoff-bundle markers, H1-5 reuse, or row-16 sweep pieces.

### Verdict

`approved` — zero findings. The Round-4 High finding is fixed: both per-MEU #11d commands now scan the corresponding touched core service file, the fresh Round-5 PR-6 census/dispositions reconcile, and the plan remains genuinely unstarted.
