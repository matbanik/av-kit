---
date: "2026-08-27"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-27-p9-capture-api-mcp/implementation-plan.md"
verdict: "approved"
findings_count: 0
round: 3
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
dispatch_id: "p9-capture-api-mcp-plan-r3"
---

# Critical Review: p9-capture-api-mcp

> **Review Mode**: `plan`
> **Verdict**: `approved` (Round 3; latest independent reviewer verdict)

## Intent Anchor

Executing this plan is supposed to deliver Session 17 only: MEU-37's authenticated `/api/v1/captures*` REST contract and OpenAPI update, followed by MEU-38's REST-backed `avkit_capture` compound MCP tool. It must leave MEU-39 and Session 8c untouched; as written, the scope and sequence are correct, but three unresolved public-boundary contracts mean execution would not reliably deliver the specified API contract.

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **The mandatory boundary inventory is incomplete, leaving malformed path inputs with no schema owner, format rule, 422 mapping, or negative oracle.** AGENTS.md requires every REST body/query/path surface to be inventoried with field constraints and invalid-input mapping. MEU-37 inventories selected bodies and queries but omits every `/{id}` path parameter plus the `POST /captures/requests` and cancel-body surfaces; MEU-38 collapses all action variants into one generic row. The build plan defines both shot and request IDs as UUID strings, while the live service/repository chain accepts an unconstrained `str`, so a malformed ID has no named validator producing the required 422. The AC census contains no malformed-UUID oracle. This violates the Boundary Input Contract and PR-8's observable/call-chain/negative-oracle requirement. | `AGENTS.md:218`; `AGENTS.md:222`; `AGENTS.md:224`; `AGENTS.md:226`; `implementation-plan.md:160`; `implementation-plan.md:172`; `implementation-plan.md:252`; `implementation-plan.md:259`; `docs/build-plan/09-screenshot-capture.md:218`; `docs/build-plan/09-screenshot-capture.md:242`; `packages/core/src/avkit_core/services/capture.py:190`; `packages/core/src/avkit_core/services/capture.py:237` | Enumerate every REST path/body/query surface and every MCP action variant; name the UUID/body validators, constraints, and error mapping. Add negative AC/control rows for malformed shot/request IDs and optional/empty request bodies. If malformed IDs intentionally map to 404, record a source-backed exception rather than leaving the behavior implicit. | open |
| 2 | High | High | **`DOMAIN_HTTP_CAPTURE` invents externally visible failure statuses without a supporting source, and AC-37.3 locks the most questionable choice.** The named set maps `CaptureFailedError` to 422 and `CaptureNotSupportedError` to 501, but Phase 9 only defines when those errors occur, not their HTTP statuses. Phase 4 describes 422 as request/schema/settings validation, whereas `CaptureFailedError` covers black frames, permissions, and grab failures. The plan's “fail-closed Local Canon” note proves only that unmapped errors currently become 500; it does not source either proposed status. Executing the plan would therefore publish an unsourced public error contract. This violates PR-5 and the Spec Sufficiency Gate. | `named-sets.json:55`; `named-sets.json:59`; `implementation-plan.md:180`; `implementation-plan.md:207`; `docs/build-plan/09-screenshot-capture.md:299`; `docs/build-plan/09-screenshot-capture.md:308`; `docs/build-plan/04-rest-api.md:87`; `docs/build-plan/04-rest-api.md:101` | Resolve each capture-domain error status from Local Canon, primary research, or a human-approved decision; then update the named set, sufficiency table, ACs, and negative oracles together. Keep input-validation errors distinct from environment/runtime capture failures. | open |
| 3 | High | High | **The request-status wire contract conflicts with local REST status precedent and is mislabeled as Spec.** `REQUEST_STATUS_WIRES` lowercases `pending/completed/cancelled/expired`, and AC-37.17 requires those tokens in `CaptureRequestOut`, citing Phase 9's `CaptureShotOut` field list. That source does not define request-status wire casing; Phase 9 defines the enum members as PascalCase, Phase 4's status-wire example is PascalCase, and the live conversion API emits `job.status.value` (also PascalCase). The plan also reuses the same set for the query and response without sourcing that coupling. This is an ambiguous, materially different public contract under PR-5/PR-9, not a clerical spelling error. | `named-sets.json:37`; `implementation-plan.md:167`; `implementation-plan.md:194`; `docs/build-plan/09-screenshot-capture.md:202`; `docs/build-plan/09-screenshot-capture.md:208`; `docs/build-plan/09-screenshot-capture.md:413`; `docs/build-plan/04-rest-api.md:114`; `docs/build-plan/04-rest-api.md:122`; `packages/api/src/avkit_api/routes/conversions.py:82` | Resolve query-token and response-token casing separately. Follow the PascalCase Local Canon unless a source-backed override establishes lowercase; then give each set a distinct canonical name if the contracts differ and update AC-37.5/37.17 plus MCP query tests. | open |
| 4 | Low | High | **`IMAGE_MAX_BYTES` is canonically named but its value is re-stated as `15 MiB` in multiple plan clauses.** This is one PR-9 stale-literal cluster; the JSON owner already defines `15728640`. It is clerical and does not block by itself. | `named-sets.json:41`; `implementation-plan.md:95`; `implementation-plan.md:204` | Keep the human-readable unit once beside the canonical definition, and reference `IMAGE_MAX_BYTES` everywhere else. | open |

## Scope

**Targets reviewed**:

- `docs/execution/plans/2026-08-27-p9-capture-api-mcp/implementation-plan.md`
- `docs/execution/plans/2026-08-27-p9-capture-api-mcp/task.md`
- `docs/execution/plans/2026-08-27-p9-capture-api-mcp/named-sets.json`
- all four named assertion scripts in the plan folder

**Authority and live state reviewed**: Phase 9 REST/MCP, Phase 4 envelopes/status/wires, Phase 5 compound-tool rules, Session 17 grouping, harness override, Session 16 reflection design rules, the p8 conversion peer plan, live `AppServices`, `DOMAIN_HTTP_MAP`, `CaptureService`, `CaptureRequestRepository`, REST route census, MCP action census, and `isListEnvelope`.

**Out of scope**: product execution, pytest/pyright/ruff/migrations, OpenAPI export, mutating `tools/` scripts, product/test/plan edits, MEU-39, and Session 8c.

## Commands Executed

Static evidence only; every shell read wrote a receipt under `C:/Temp/av-kit/`.

- `rg -n "^" <target-or-authority>` for line-numbered reads (`review-r1-target-*.txt`, `review-r1-full-*.txt`, `review-r1-source-*.txt`).
- `rg -n <contract-patterns> ...` for live call-chain, index, source-label, scope, and repeated-literal censuses (`review-r1-live-*.txt`, `review-r1-census-*.txt`, `review-r1-sweep5-trace.txt`, `review-r1-sweep9-census.txt`).
- `Test-Path` over extracted and explicitly named artifacts (`review-r1-sweep8-existence.txt`, `review-r1-sweep8-explicit.txt`).
- `Get-Content` only to consume the canonical receipts and selected static source ranges.

No product tests, type checks, linters, migrations, OpenAPI export, or mutating repository scripts were run.

## Checklist Results

### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both files lock MEU-37 then MEU-38, H1 review, then H2; both exclude MEU-39 and Session 8c. |
| PR-2 Not-started confirmation | pass | MEU-37/38 remain `pending` with no execution plan; all task rows are unchecked; planned capture files and implementation handoffs are absent. `task.md`'s `in_progress` frontmatter reflects planning state, not completed implementation. |
| PR-3 Task contract completeness | pass | Every executable task row has task, owner, deliverable, validation, dependency, context strategy, durable output, and status fields. |
| PR-4 Validation realism | pass with static limitation | Commands are specific and receipt-bound. Semantics were inspected only; execution was forbidden by the review scope. |
| PR-5 Source-backed planning | fail | Findings 2 and 3 lock unsourced public HTTP/wire behavior. |
| PR-6 Handoff/corrections readiness | pass | Two explicit MEU handoffs, one rolling plan review, one rolling implementation review, and correction routing are named. Round-2 blast-radius rules are not applicable in Round 1. |
| PR-7 Scope discipline | pass | MEU-39 is registered and deferred to Session 18; the other out-of-scope rows cite Phase 9, grouping, or the human approval gate. No MEU-39 or Session 8c work is packed. |
| PR-8 Control reachability/totality | fail | Finding 1 demonstrates missing validators and negative oracles on external path/body boundaries. Existing MCP list-envelope and image controls do trace to live production branches. |
| PR-9 Single-statement discipline | fail (non-blocking) | Finding 4 records one threshold restatement cluster. Other route/action/status sets are owned by `named-sets.json`. |

### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The plan accurately describes current missing REST/MCP capture surfaces and live 61-route/59-action baselines. |
| DR-2 Residual old terms | pass | No stale `compound/` target or `captures` queue contract survives as an implementation target. |
| DR-3 Downstream references | pass | OpenAPI, MCP fixtures/index, SSOT, hub Next, handoffs, reflection, and metrics are all scheduled. |
| DR-4 Verification robustness | fail | Finding 1 identifies external-input regressions that the planned negative oracles cannot catch. |
| DR-5 Evidence auditability | pass | Commands and receipts are named and reproducible; all named assertion scripts and cited tools exist. |
| DR-6 Cross-reference integrity | fail | Findings 2 and 3 conflict with or exceed the cited Phase 4/9 contracts. |
| DR-7 Evidence freshness | pass | Live static evidence confirms `ROUTE_INDEX == 61`, `ACTION_INDEX == 59`, seven `AppServices(` sites, and processor-required `isListEnvelope`. |
| DR-8 Completion vs residual risk | pass | The plan makes no implementation-complete claim and keeps all execution rows unchecked. |

## Sweep Results

| Sweep | Result |
|-------|--------|
| 1 Plan-task consistency | pass |
| 2 Status readiness | pass |
| 3 Role/ownership consistency | pass |
| 4 Validation specificity | pass with static-only limitation |
| 5 Dependency/order correctness | pass |
| 6 Source traceability | fail — Findings 2 and 3 |
| 7 Scope discipline | pass |
| 8 Referenced-artifact existence | pass — absent artifacts are scheduled outputs or explicitly declared absent; all named assert scripts and cited tools exist |
| 9 Repeated literals | fail, Low only — Finding 4 |

## Open Questions / Assumptions

- No human decision is requested in this review. The correction pass should first attempt Local Canon and primary-source resolution for Findings 2 and 3; escalate only if materially different behaviors remain plausible.
- Static evidence was authoritative for this round. Runtime correctness remains untested by explicit user instruction.

## Verdict

`changes_required` — Findings 1–3 are evidence-backed High-severity contract defects. They leave mandatory external-input behavior incomplete and publish unsourced HTTP/status-wire choices. Finding 4 is clerical and non-blocking under the Materiality Gate.

## Required Follow-up

Route corrections through `/plan-corrections`, update only the plan-folder artifacts, and return for Round 2 with the required untruncated blast-radius census plus per-hit disposition log. Do not begin execution while this verdict remains `changes_required`.

## Residual Risk

This was a static review. Approval after correction will establish plan readiness, not runtime correctness; product tests and generated OpenAPI remain execution-phase evidence.

---

## Corrections Applied — 2026-08-27 (create-plan Step 5b / plan-corrections)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 2 must re-score. Product code, tests, and `docs/build-plan/` were not modified.

**Instruction conflict (flagged, not silently picked):** `plan-corrections.md` HARD STOP says timestamp-and-stop and do not auto-chain into `/plan-critical-review`. Driving workflow is `/create-plan` Step 5b (`plan_to_exec_gate: reviewer-auto` in `.agent/context/harness.local.md`), which requires re-dispatch after the census. Re-dispatch proceeds under create-plan. `named-sets.json` is not listed in `plan-corrections.md` Write Scope; it is a create-plan Step 4 plan-folder artifact and was updated as such.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| F1 | Completed Boundary Input Contract: path `{id}` (`PATH_ID_TYPE` `str`, `PATH_ID_UNKNOWN_HTTP` 404 — Local Canon `downloads.py` `id: str`, Phase 4 404, Spec 310); empty POST `/captures/requests` + cancel `EmptyIn`; per-MCP-action Zod `.strict()` rows. Added **AC-37.19** (`not-a-uuid` → 404 not 422/500). `RED_COUNT_37` 18→19. Did **not** invent 422 for malformed ids. | named-sets.json; implementation-plan.md; task.md row 2 |
| F2 | `DOMAIN_HTTP_CAPTURE`: `CaptureFailedError` + `CaptureNotSupportedError` → **503** (04-rest-api.md line 99 analog: required backend/environment missing). InboxPath/AnnotationValidation stay 422. Rejected unsourced 422/501. AC-37.3/37.15/sufficiency/Open Questions updated together. | named-sets.json; implementation-plan.md |
| F3 | Split wires: `REQUEST_STATUS_QUERY_WIRES` lowercase (Spec 171 `?status=pending`); `REQUEST_STATUS_OUT_WIRES` Pascal (04 line 122). Deleted `REQUEST_STATUS_WIRES`. Shot Out `CAPTURE_SOURCE_OUT_WIRES` Pascal; register In stays `REGISTER_SOURCE_WIRES`. Deleted `CAPTURE_SOURCE_WIRE_MAP`. AC-37.5/37.17 negatives flipped. | named-sets.json; implementation-plan.md; task.md row 2 |
| F4 | `15 MiB` lives only as `IMAGE_MAX_BYTES_HUMAN` beside `IMAGE_MAX_BYTES`. ACs cite the integer named set. | named-sets.json; implementation-plan.md |

### Blast-radius census (Step 5c / PR-6)

Index: `C:/Temp/av-kit/census-p9am-index.txt`. Runner: `C:/Temp/av-kit/census-p9am-runner.txt`. Per-query receipts: `C:/Temp/av-kit/census-p9am-01-old-REQUEST_STATUS_WIRES.txt` … `census-p9am-25-old-source-wire-map-cite.txt`. Concat: `C:/Temp/av-kit/census-p9am-ledger.txt`.

Queries: 25 (`rg -F -n` over `implementation-plan.md`, `task.md`, `named-sets.json`). Old-value `rc=1` (gone): 01–05, 07–11, 25. Remaining hits dispositioned below.

| Receipt | File:Line | Disposition |
|---|---|---|
| 01–05, 07–11, 25 old | (no hit) | updated-gone |
| 06-old-15-MiB | named-sets.json:45 `IMAGE_MAX_BYTES_HUMAN` | confirmed-consistent — once-only unit label |
| 12-old-501-bare | implementation-plan.md:129, 215, 441 | confirmed-consistent — explicit prohibition / rejected option B |
| 13-new-REQUEST_STATUS_QUERY | named-sets + plan locks/AC/MCP/Open Q | updated |
| 14-new-REQUEST_STATUS_OUT | named-sets + plan + task.md:47 | updated |
| 15-new-CAPTURE_SOURCE_OUT | named-sets + plan + task.md:47 | updated |
| 16-new-IMAGE_MAX_BYTES_HUMAN | named-sets.json:45; plan named-set table:95 | updated — two sites, owner + table cite |
| 17-new-CaptureFailed-503 | named-sets.json:62 | updated; plan cites `DOMAIN_HTTP_CAPTURE` **503** (not JSON key form) |
| 18-new-CaptureNotSupported-503 | named-sets.json:63 | updated |
| 19-new-RED_COUNT_37-19 | named-sets.json:9 | updated; task/plan cite `RED_COUNT_37` by name |
| 20-new-AC-37.19 | implementation-plan.md:205, 235 | updated |
| 21-new-PATH_ID_TYPE | named-sets, plan inventory/locks/AC/Open Q, task.md:47 | updated |
| 22-new-PATH_ID_UNKNOWN_HTTP | named-sets + plan | updated |
| 23-new-EmptyIn-requests | implementation-plan.md:170 | updated; lock line 118 uses same EmptyIn without matching backtick form |
| 24-new-not-a-uuid | implementation-plan.md:205, 235 | updated |

Blast-radius census: 8 values changed (HTTP 503 pair, status-wire split, source-out set, RED_COUNT_37, PATH_ID_*, IMAGE_MAX_BYTES_HUMAN, EmptyIn inventory, AC-37.19), 25 variants swept, old stale names gone, remaining 501/`15 MiB` hits are prohibition or the once-only human label.

Round 2 must **append** to this same rolling file, set `dispatch_id: p9-capture-api-mcp-plan-r2`, `round: 2`, and re-score PR-5/PR-8/PR-9 against live plan files. Do not start product TDD while the latest **reviewer** verdict is not `approved`.

---

## Recheck (2026-08-27 — Round 2)

### Intent Anchor

Executing this plan is supposed to deliver Session 17 only: MEU-37's authenticated `/api/v1/captures*` REST/OpenAPI contract followed by MEU-38's REST-backed `avkit_capture` compound MCP tool, while leaving MEU-39 and Session 8c untouched. Round 2 cannot determine that the corrected plan is ready to deliver that objective because the mandatory PR-6 correction census does not inventory every hit for a changed public-contract value.

### Findings

No severity-rated findings were evaluated. PR-6 failed as the workflow's pre-verdict procedural gate, which is the sole non-severity path to `changes_required`.

### PR-6 Pre-Verdict Gate

| Requirement | Result | Evidence |
|---|---|---|
| Named census receipts exist | pass | `census-p9am-index.txt`, `census-p9am-runner.txt`, `census-p9am-ledger.txt`, and all 25 indexed per-query receipts returned `Test-Path=True` in `C:/Temp/av-kit/r2-pr6-all-existence.txt`. |
| Raw receipt is untruncated | pass | `C:/Temp/av-kit/census-p9am-ledger.txt` contains the complete 01–25 sequence and every indexed raw hit. |
| Every changed value and semantic variant is inventoried | **fail** | The correction changed both capture runtime errors to `503`, but the index contains only `17-new-CaptureFailed-503` and `18-new-CaptureNotSupported-503`, whose receipts match only `named-sets.json:62-63`. There is no bare/new-`503` query. The fresh fixed-string census `C:/Temp/av-kit/r2-sweep9-literals.txt` additionally finds the changed 503 contract at `task.md:47` and `implementation-plan.md:97,129,189,215,228,440`. Those hits are absent from the raw correction census. |
| Every raw hit has a per-hit disposition | **fail as a consequence** | Because the missing 503 semantic-variant hits were never inventoried, the correction log at lines 133–159 cannot assign those `file:line` hits `updated` or `confirmed-consistent`. Its F2 summary and receipt rows are coordinator claims, not a substitute for the raw census required by `plan-corrections.md` Step 5c and PR-6. |

This is not assigned `Low`, `Medium`, or `High`: PR-6 defines a missing/incomplete or undispositioned Round-2 census as a pre-verdict procedural failure. Per the Verdict Rule, corrected-content scoring stops here and this round names only that gate.

### Prior Pass Summary

| Round 1 finding | Corrector claim | Round 2 recheck result |
|---|---|---|
| Boundary inventory / AC-37.19 | fixed | not re-scored — PR-6 gate failed before corrected-content review |
| `DOMAIN_HTTP_CAPTURE` status mapping | fixed | not re-scored — its changed `503` semantic variants are precisely the missing census surface |
| Request/source wire split | fixed | not re-scored — PR-6 gate failed before corrected-content review |
| `IMAGE_MAX_BYTES_HUMAN` once-only label | fixed | not re-scored — PR-6 gate failed before corrected-content review |

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | not adjudicated | Pre-verdict PR-6 gate failed. |
| PR-2 Not-started confirmation | not adjudicated | Static existence receipt was collected, but corrected-content scoring stopped at PR-6. |
| PR-3 Task contract completeness | not adjudicated | Pre-verdict PR-6 gate failed. |
| PR-4 Validation realism | not adjudicated | Pre-verdict PR-6 gate failed. |
| PR-5 Source-backed planning | not re-scored | Pre-verdict PR-6 gate failed. |
| PR-6 Handoff/corrections readiness | **fail — procedural gate** | The untruncated receipts omit the changed bare/new-`503` semantic variant and therefore cannot disposition every live hit. |
| PR-7 Scope discipline / C2 | not adjudicated | Pre-verdict PR-6 gate failed. |
| PR-8 Control reachability / totality | not re-scored | Pre-verdict PR-6 gate failed. |
| PR-9 Single-statement discipline | not re-scored | The fresh repeated-literal census was used only to demonstrate the PR-6 omission. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | fail at PR-6 evidence boundary | The “25 variants swept” claim does not include the live bare/new-`503` sites. |
| DR-2 Residual old terms | not adjudicated | Pre-verdict PR-6 gate failed. |
| DR-3 Downstream references | not adjudicated | Pre-verdict PR-6 gate failed. |
| DR-4 Verification robustness | fail at PR-6 evidence boundary | The correction evidence cannot catch a stale 503 statement outside the two exact JSON-key forms. |
| DR-5 Evidence auditability | fail | The raw census and correction log do not cover every live hit of the changed 503 contract. |
| DR-6 Cross-reference integrity | not adjudicated | Pre-verdict PR-6 gate failed. |
| DR-7 Evidence freshness | pass for the procedural decision | Round 2 re-read the live correction log, index, runner, ledger, all named receipts, and a fresh fixed-string census. |
| DR-8 Completion vs residual risk | pass | No implementation-complete claim was made; execution remains blocked on plan approval. |

### Sweep Results

| Sweep | Result |
|---|---|
| 1 Plan-task consistency | collected, not adjudicated after PR-6 gate |
| 2 Status readiness | collected, not adjudicated after PR-6 gate |
| 3 Role/ownership consistency | collected, not adjudicated after PR-6 gate |
| 4 Validation specificity | collected, not adjudicated after PR-6 gate |
| 5 Dependency/order correctness | collected, not adjudicated after PR-6 gate |
| 6 Source traceability | collected, not adjudicated after PR-6 gate |
| 7 Scope discipline | collected, not adjudicated after PR-6 gate |
| 8 Referenced-artifact existence | pass for existence only — all four named assertion scripts and cited existing tools are present; `tools/validate_closeout_artifacts.py` is absent exactly as the plan states |
| 9 Repeated literals | procedural evidence — the live bare `503` cluster proves the Step 5c semantic-variant census is incomplete |

### Commands Executed

Static evidence only. Every shell command wrote all streams to a receipt under `C:/Temp/av-kit/` and captured exit status before reading the receipt.

- Full/current reads of the review workflow, terminal preflight, output-evidence policy, harness/profile/guardrails, review template, rolling review, plan-folder targets, relevant Phase 4/5/9 authority, grouping/reflection carry-forward rules, and live API/core/MCP surfaces.
- PR-6 existence and full-ledger reads: `r2-pr6-all-existence.txt`, `r2-census-core.txt`, and `r2-pr6-log-lines.txt`.
- Required Sweep 8 receipts: `r2-sweep8-path-census.txt`, `r2-sweep8-absence-context.txt`, and `r2-sweep8-existence.txt`.
- Fresh semantic-variant evidence: `r2-sweep9-literals.txt`.
- Two malformed combined `rg` attempts produced only quote/regex errors and no evidence; the same live files were then read with corrected static commands. No repository state changed.
- No pytest, pyright, ruff, migration, OpenAPI export, plan helper, or mutating `tools/` script was run. `prompt_temp.txt` was not modified or removed.

### Required Follow-up

Route one correction through `/plan-corrections`: add an unfiltered fixed-string census for bare/new `503` across `implementation-plan.md`, `task.md`, and `named-sets.json` (plus any declared semantic variants), then assign every returned `file:line` `updated` or `confirmed-consistent` in this rolling correction log. Return for Round 3; do not begin product TDD while the latest reviewer verdict is `changes_required`.

### Verdict

`changes_required` — PR-6's Round-2 procedural exception applies. The receipts are present and untruncated, but the census omits live semantic variants of the changed `503` contract, so the correction evidence is incomplete and the corrected content cannot receive an approval verdict this round.

### Residual Risk

This is a static procedural verdict, not a substantive rejection of the four coordinator corrections. Their live content remains unapproved and must be re-scored after a complete, per-hit-dispositioned correction census. No product code, tests, plan files, or unrelated handoff was modified.

---

## Corrections Applied — 2026-08-27 (Round 2 follow-up / PR-6 503 census)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 3 must re-score F1–F4 **and** PR-6. Product code, tests, plan files, and `docs/build-plan/` were not modified in this pass — the Round 2 finding was a missing census query, not a missing contract.

**Instruction conflict (flagged):** `plan-corrections.md` HARD STOP vs `/create-plan` Step 5b re-dispatch. Driving workflow remains create-plan. Plan-review cap is 3; Round 3 is the last auto-dispatch.

### Finding disposition

| # | Change | Files |
|---|--------|-------|
| R2 PR-6 | Added unfiltered fixed-string census for bare `503` and declared variants (`HTTP 503`, `**503**`, JSON keys, `(503 grab/platform)`). Re-confirmed old `"CaptureFailedError": 422` and `"CaptureNotSupportedError": 501` are gone (`rc=1`). Every live `503` hit maps to `DOMAIN_HTTP_CAPTURE` grab/platform 503. | receipts only; no plan-text edit |

### Blast-radius census (Step 5c / PR-6) — 503 semantic variants

Index: `C:/Temp/av-kit/census-p9am-r3-index.txt`. Runner: `C:/Temp/av-kit/census-p9am-r3-runner.txt`. Ledger: `C:/Temp/av-kit/census-p9am-r3-ledger.txt`. Prior Round-1 receipts 01–25 remain at `C:/Temp/av-kit/census-p9am-01-*.txt` … `25-*.txt`.

| Receipt | File:Line | Disposition |
|---|---|---|
| 26-new-503-bare | named-sets.json:62 | confirmed-consistent — `DOMAIN_HTTP_CAPTURE` owner `CaptureFailedError` |
| 26-new-503-bare | named-sets.json:63 | confirmed-consistent — `DOMAIN_HTTP_CAPTURE` owner `CaptureNotSupportedError` |
| 26-new-503-bare | task.md:47 | confirmed-consistent — Green row cites `DOMAIN_HTTP_CAPTURE` (503 grab/platform) |
| 26-new-503-bare | implementation-plan.md:97 | confirmed-consistent — named-set table cites grab/platform 503 |
| 26-new-503-bare | implementation-plan.md:129 | confirmed-consistent — lock maps CaptureFailed/NotSupported to 503 |
| 26-new-503-bare | implementation-plan.md:189 | confirmed-consistent — AC-37.3 maps both errors to `DOMAIN_HTTP_CAPTURE` 503; source cites 04 line 99 |
| 26-new-503-bare | implementation-plan.md:215 | confirmed-consistent — sufficiency table 503 + reject 501/422 |
| 26-new-503-bare | implementation-plan.md:228 | confirmed-consistent — AC-37.3 control binding HTTP 503 |
| 26-new-503-bare | implementation-plan.md:440 | confirmed-consistent — Open Question option A; cons note that Phase 4 names FFmpeg |
| 27-new-HTTP-503 | implementation-plan.md:228 | confirmed-consistent — subset of 26 |
| 28-new-bold-503 | implementation-plan.md:189 | confirmed-consistent — subset of 26 (`**503**` twice on one line) |
| 29-new-json-CaptureFailed-503 | named-sets.json:62 | confirmed-consistent |
| 30-new-json-CaptureNotSupported-503 | named-sets.json:63 | confirmed-consistent |
| 31-new-503-grab-platform | task.md:47 | confirmed-consistent |
| 32-old-CaptureFailed-422 | (no hit) | updated-gone |
| 33-old-CaptureNotSupported-501 | (no hit) | updated-gone |

Bare-`503` inventory is complete: 9 lines, all `updated` from Round 1 F2 or `confirmed-consistent` with `DOMAIN_HTTP_CAPTURE`. No unmatched 503 remains in the three plan files.

Round 3 must **append** to this same rolling file, set `dispatch_id: p9-capture-api-mcp-plan-r3`, `round: 3`, pass or fail PR-6 on receipts 26–33 **and** re-score Round 1 F1–F4. This is the last auto plan-review round (cap 3).

---

## Recheck (2026-08-27 — Round 3)

**Workflow:** `/plan-critical-review` Round 3 of 3  
**Agent:** `gpt-5.6-sol`  
**Review mode:** `plan`  
**Execution performed:** none

### Intent Anchor

Executing this plan is supposed to deliver Session 17 only: MEU-37's authenticated `/api/v1/captures*` REST/OpenAPI contract followed by MEU-38's REST-backed `avkit_capture` compound MCP tool, while leaving MEU-39 and Session 8c untouched. The Round 3 PR-6 census is now complete and auditable, Round 1 F1–F4 are closed in the live plan folder, and no material control, scope, or source defect remains that would prevent the plan from delivering that objective.

### Findings

No Critical, High, Medium, or Low findings remain in Round 3. The Materiality Gate was applied before severity; no demonstrated material false-pass or ambiguous public contract remains.

### PR-6 Pre-Verdict Gate

`pass` — the correction census now satisfies the round-2+ procedural prerequisite.

| Requirement | Result | Live evidence |
|---|---|---|
| Named raw receipts exist | pass | All indexed receipts 01–33 returned `Test-Path=True` in `C:/Temp/av-kit/plan-r3-pr6-all-01-33-existence.txt`; both prior and Round 3 index/runner/ledger files exist. |
| Raw receipt is untruncated | pass | `census-p9am-r3-index.txt`, `census-p9am-r3-runner.txt`, and `census-p9am-r3-ledger.txt` contain the complete 26–33 sequence. |
| Every changed `503` semantic variant is inventoried | pass | `26-new-503-bare` inventories all nine live bare-`503` lines across `named-sets.json`, `task.md`, and `implementation-plan.md`; receipts 27–31 cover the declared textual/JSON subsets, and 32–33 prove the old 422/501 mappings absent. |
| Every raw hit has a per-hit disposition | pass | The correction log at lines 277–294 assigns every live `file:line` hit `confirmed-consistent` and assigns both no-hit old forms `updated-gone`. The nine bare-`503` coordinates reconcile exactly with the raw receipt. |

### Round 1 F1–F4 Re-score

| Finding | Round 3 result | Live evidence |
|---|---|---|
| F1 — incomplete boundary inventory / missing malformed-ID oracle | ✅ Fixed | REST bodies, queries, and both shot/request path groups are inventoried at `implementation-plan.md:167-180`; MCP has one `.strict()` row per action at `:268-279`. `PATH_ID_TYPE=str` and `PATH_ID_UNKNOWN_HTTP=404` are owned at `named-sets.json:39-40`; AC-37.19 covers malformed and unknown IDs on every `{id}` route at `implementation-plan.md:205,235`. `RED_COUNT_37=19` is bound by `assert-red-oracle.ps1:20-24,72-125`. |
| F2 — unsourced capture-domain HTTP mappings | ✅ Fixed | `DOMAIN_HTTP_CAPTURE` maps only InboxPath/AnnotationValidation to 422 and CaptureFailed/CaptureNotSupported to 503 (`named-sets.json:59-64`). The lock, AC, sufficiency row, and control binding agree (`implementation-plan.md:129,189,215,228`), using the Phase 4 runtime-dependency 503 analog (`04-rest-api.md:87-101`). No live public mapping emits 501. |
| F3 — request/source wire ambiguity | ✅ Fixed | `REQUEST_STATUS_QUERY_WIRES` is lowercase and distinct from PascalCase `REQUEST_STATUS_OUT_WIRES`; `REGISTER_SOURCE_WIRES` is distinct from PascalCase `CAPTURE_SOURCE_OUT_WIRES` (`named-sets.json:28-38`). Plan consumers preserve the In/query vs Out split (`implementation-plan.md:91-92,127-128,191,203`), matching the lowercase poll query and Phase 4 PascalCase output precedent. |
| F4 — repeated `15 MiB` threshold | ✅ Fixed | The literal appears once only, as `IMAGE_MAX_BYTES_HUMAN` beside `IMAGE_MAX_BYTES` (`named-sets.json:44-45`). Operational clauses reference `IMAGE_MAX_BYTES`; the untruncated Sweep 9 receipt confirms no second `15 MiB` literal in the plan folder. |

### Checklist Results

#### Plan Review (PR-1 through PR-9)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Both files retain MEU-37 Red/Green/gate, then MEU-38 Red/Green/gate, hub binding, H1 independent review, and H2 closeout. Both exclude MEU-39 and Session 8c. |
| PR-2 Not-started confirmation | pass | All actionable task rows remain `[ ]`; planned REST/MCP files, MEU handoffs, implementation review, and reflection return `Test-Path=False`. MEU-37/38 remain `pending` in `meu-status.yaml`. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, exact validation, dependency, context strategy, durable output, builder model, and status. |
| PR-4 Validation realism | pass | Red oracles bind every AC ID; targeted Green/gate commands, OpenAPI check/regeneration order, anti-placeholder/G36 checks, handoff AC checks, and independent-review provenance are explicit. This review inspected but did not execute them. |
| PR-5 Source-backed planning | pass | F1–F3 now cite Spec and Local Canon at each public boundary; research-backed Pydantic/MCP rules are separately labeled. No unresolved product choice remains. |
| PR-6 Handoff/corrections readiness | pass | Two MEU handoffs and one rolling implementation-review path are explicit; receipts 01–33 plus the per-hit correction log reconcile. |
| PR-7 Scope discipline (C2) | pass | MEU-39 is registered and deferred to Session 18; the MCP omissions are sourced to the Phase 9 action table; Session 8c remains separately pending. |
| PR-8 Control reachability/totality | pass | Corrected path/error/wire controls name observable, production chain, and adversarial oracle. Live service/repository/registry reads confirm the planned producers and missing seams. No material vacuity is demonstrated. |
| PR-9 Single-statement discipline | pass | Threshold and wire sets are single-owned in `named-sets.json`; consumers reference their names. See the non-blocking correction note below for the unambiguous MCP mode subset. |

#### Docs Review (DR-1 through DR-8)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | pass | Round 2 follow-up claims match the live 26–33 receipts; the plan files themselves were unchanged during that receipt-only correction. |
| DR-2 Residual old terms | pass | Fresh fixed-string sweep returns `RG_RC=1` for `REQUEST_STATUS_WIRES`, `CAPTURE_SOURCE_WIRE_MAP`, the old 422/501 JSON mappings, and `mcp_fullscreen`. |
| DR-3 Downstream references updated | pass | Plan, task, named sets, red oracle, OpenAPI/index targets, handoffs, reflection, metrics, and reviewer-dispatch controls agree on the corrected owners. |
| DR-4 Verification robustness | pass | AC-37.19, AC-37.3, AC-37.5/37.17, AC-38.3/38.7/38.11/38.12 and their controls catch the corrected boundary and wire regressions. |
| DR-5 Evidence auditability | pass | Every static command used a P0 receipt; raw PR-6 and Sweep 8/9 evidence remains re-openable under `C:/Temp/av-kit/`. |
| DR-6 Cross-reference integrity | pass | Phase 9 REST/MCP, Phase 4 status/wire canon, Phase 5 compound-tool rules, grouping, prior reflection rules, and live source seams agree with the plan. |
| DR-7 Evidence freshness | pass | All review targets, authority files, live source/index seams, correction logs, and census receipts were re-read from current disk state in Round 3. |
| DR-8 Completion vs residual risk | pass | The artifact approves plan readiness only; all execution rows remain unchecked and no implementation-complete claim is made. |

### Sweep Results

| Sweep | Result |
|---|---|
| 1 Plan-task consistency | pass |
| 2 Status readiness | pass — unstarted |
| 3 Role/ownership consistency | pass |
| 4 Validation specificity | pass by static inspection |
| 5 Dependency/order correctness | pass |
| 6 Source traceability | pass |
| 7 Scope discipline | pass |
| 8 Referenced-artifact existence | pass — all relied-on scripts/tools/configs exist; absent entries are scheduled outputs or the explicitly acknowledged unused `tools/validate_closeout_artifacts.py`; `tests/capture.test.ts` is relative to `Push-Location mcp-server` |
| 9 Repeated literals | pass with non-blocking correction note |

### Non-Blocking Correction Note

The MCP-only capture-mode subset `fullscreen` / `region` is repeated in explanatory plan clauses instead of receiving a separate named-set owner. The surrounding `POST_MODES`, REST-only-register rule, per-action Zod row, and AC-38.13 make the governing behavior unambiguous, so this is clerical under the Materiality Gate and does not enter the findings count or block approval.

### Commands and Receipts

Only static `Get-Content`, `rg`, and `Test-Path` evidence was used. Key Round 3 receipts:

- protocol/context: `plan-r3-terminal-preflight.txt`, `plan-r3-protocol-template.txt`, `plan-r3-runtime-context.txt`, `plan-r3-session-roles.txt`
- targets/authority/live state: `plan-r3-implementation-001-263.txt`, `plan-r3-implementation-264-458.txt`, `plan-r3-task-named-sets.txt`, `plan-r3-primary-authority.txt`, `plan-r3-grouping-reflection-exact.txt`, `plan-r3-live-source.txt`, `plan-r3-repo-appservices.txt`
- PR-6: `plan-r3-correction-log.txt`, `plan-r3-pr6-receipts.txt`, `plan-r3-pr6-all-01-33-existence.txt`
- Sweeps: `plan-r3-sweeps1-7.txt`, `plan-r3-sweep2-not-started.txt`, `plan-r3-sweep8-explicit.txt`, `plan-r3-sweep8-paths-raw.txt`, `plan-r3-sweep8-existence-all.txt`, `plan-r3-sweep9-live.txt`, `plan-r3-sweep9-old-terms.txt`
- assertion-script reads: `plan-r3-script-red-oracle.txt`, `plan-r3-closeout-scripts.txt`

No pytest, pyright, ruff, migration, OpenAPI export, assertion helper, product command, or mutating `tools/` script was run. No provenance receipt was deleted or rewritten; dispatch `prompt_temp.txt` remains preserved.

### Open Questions / Assumptions

- No human product decision is required by this review.
- Static evidence establishes plan readiness, not runtime correctness.

### Required Follow-up

No `/plan-corrections` pass is required. This review workflow stops after recording the Round 3 verdict and does not modify or execute the approved plan.

### Verdict

`approved` — PR-6 passes, Round 1 F1–F4 are fixed in the live plan folder, Sweeps 1–9 and PR-1–PR-9 / DR-1–DR-8 reveal no High/Critical delivery-level defect, and `findings_count: 0`.

### Residual Risk

This is a static plan review. Runtime REST/MCP behavior, OpenAPI regeneration, boundary failures, binary image handling, repository listing, and the independent execution-review dispatch still require the execution receipts named by the plan.
