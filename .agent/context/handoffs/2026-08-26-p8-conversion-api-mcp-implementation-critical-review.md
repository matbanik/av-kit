---
review_mode: implementation
target_plan: docs/execution/plans/2026-08-26-p8-conversion-api-mcp/implementation-plan.md
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
date: 2026-08-26
template_version: 2.1
requested_verbosity: standard
---

# Critical Review: p8-conversion-api-mcp

> **Review Mode**: `implementation`
> **Verdict**: `approved`

## Intent Anchor

Session 14 was intended to deliver the complete MEU-31 conversion REST boundary and MEU-32 `avkit_convert` MCP surface, with invalid external input rejected at the declared schema boundary and without starting MEU-33 or Session 8c. The implementation substantially delivers that surface, but one independently reproduced REST boundary violation means it does not yet satisfy the approved execution contract.

## Findings

| Finding | Severity |
|---|---|
| **F1 — `PUT /conversions/reorder` accepts the contractually invalid empty permutation.** The approved Boundary Inventory requires a **nonempty permutation** and invalid input to return 422 (`implementation-plan.md:156-160`), but `ConversionReorderIn.job_ids` has no `min_length=1` constraint (`packages/api/src/avkit_api/schemas/conversions.py:61-64`). Both the fake-backed route probe and a real `build_services` + temporary SQLite probe returned `200 {"items":[]}` for `{"job_ids":[]}` (`C:/Temp/av-kit/p8-api-mcp-exec-r1-static-auth-empty-reorder-probe.txt`; `C:/Temp/av-kit/p8-api-mcp-exec-r1-real-empty-reorder-probe.txt`). The current AC-31.7 test checks an extra key and a nonempty list only (`tests/e2e/test_api_conversions.py:412-425`), so the declared boundary can regress while all 152 tests remain green. This violates the plan boundary contract and IR-6; the concrete failure is an invalid write request being committed and reported as success instead of rejected before `reorder_queue`. | High |

## Scope

**Correlated plan:** `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/implementation-plan.md` (plan review Round 4 `approved`)

**Expanded handoff set:**

- `.agent/context/handoffs/2026-08-26-p8-conversion-api-mcp-MEU-31-handoff.md`
- `.agent/context/handoffs/2026-08-26-p8-conversion-api-mcp-MEU-32-handoff.md`

**Correlation rationale:** both handoffs name the same date/slug and plan source; the plan and named sets declare exactly MEU-31 + MEU-32 and exactly two handoffs. Session 15 / MEU-33 and Session 8c were excluded. Downloader→Convert and Convert GUI were treated as the approved deferrals, not review requirements.

**Implementation reviewed:** the user-named API, core wire, MCP toolset/registry/settings/destructive/instructions, OpenAPI, test, fixture, wiring, SSOT, and hub surfaces. The workspace was verified from current file state because repository history was not assumed available.

## Commands Executed

| Verification | Result | Receipt |
|---|---|---|
| `uv run pytest tests/e2e tests/integration/test_api_wiring.py -x --tb=short -v` | 152 passed | `C:/Temp/av-kit/p8-api-mcp-exec-r1-pytest-h1.txt` |
| `npx tsc --noEmit`; `npx vitest run`; `npm run build` | typecheck/build passed; 183 tests passed | `C:/Temp/av-kit/p8-api-mcp-exec-r1-mcp-gate.txt` |
| `uv run python tools/export_openapi.py --check openapi.committed.json` | pass; no drift | `C:/Temp/av-kit/p8-api-mcp-exec-r1-openapi-check.txt` |
| `uv run ruff check packages/api ...` | all checks passed | `C:/Temp/av-kit/p8-api-mcp-exec-r1-ruff.txt` |
| `uv run pyright packages/api` | 0 errors, 0 warnings | `C:/Temp/av-kit/p8-api-mcp-exec-r1-pyright.txt` |
| Red-oracle scripts for MEU-31 / MEU-32 | counts 22 / 11; receipts prove non-fail-fast Red runs | `C:/Temp/av-kit/p8-api-mcp-exec-r1-red-oracles.txt`; `C:/Temp/av-kit/p8-api-mcp-exec-r1-red-no-x.txt` |
| Anti-placeholder and G36 scans | clean | `C:/Temp/av-kit/p8-api-mcp-exec-r1-placeholder-g36.txt` |
| SSOT / hub exact check | MEU-31/32 `ready_for_review`; exact no-slash plan bindings; both phase-8 slash entries; unique expected `Next:` | `C:/Temp/av-kit/p8-api-mcp-exec-r1-ssot.txt` |
| Per-MEU AC and handoff marker scripts | pass | `C:/Temp/av-kit/p8-api-mcp-exec-r1-handoff-contract-checks.txt` |
| Static-route runtime order + unauthenticated static route probe | order correct; all seven static operations returned 401 | `C:/Temp/av-kit/p8-api-mcp-exec-r1-static-auth-empty-reorder-probe.txt` |
| Real temporary-SQLite empty reorder probe | reproduced 200 with empty items | `C:/Temp/av-kit/p8-api-mcp-exec-r1-real-empty-reorder-probe.txt` |

## Checklist Results

### Implementation Review (IR)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | `tests/integration/test_api_wiring.py:13-32` and independent real temporary-SQLite probes exercised the production composition root without dependency overrides. |
| IR-2 Stub behavioral compliance | pass | API/MCP fakes were inspected against live behavior; the real wiring smoke verified the queue/list persistence boundary. |
| IR-3 Error mapping completeness | pass | `DOMAIN_HTTP_MAP` covers validation, invalid time range, not-found, and conflict paths (`packages/api/src/avkit_api/errors.py:21-30`); route tests assert 422/404/409 envelopes. |
| IR-4 Fix generalization | pass | Round 1; no prior implementation-review correction surface exists. Named-set and whole-surface scans found no analogous missing `AppServices.conversion` site. |
| IR-5 Test rigor audit | fail (F1) | AC-31.7 omits the declared nonempty boundary and false-passes the reproduced behavior. Other scoped tests are graded below. |
| IR-6 Boundary validation coverage | fail (F1) | `ConversionReorderIn.job_ids` accepts an empty list and real REST returns 200 instead of the declared 422. Extra-field, discriminated-create, path, settings, and MCP strict/confirm negatives pass. |
| IR-7 Deferral and AC coverage integrity | pass | Both handoffs contain every matching AC ID; marker/AC scripts pass. Integration-typed ACs use e2e/contract tests. GUI is MEU-33; Downloader→Convert correctly uses deferred-to `—`. |

### IR-5 Test Rigor Audit

| Test file | Grade | Rationale |
|---|---|---|
| `tests/e2e/test_api_conversions.py` | 🔴 Weak on AC-31.7; otherwise 🟢 Strong | Strong value/error/spy assertions across AC-31.1–31.22, but reorder omits the declared empty-list negative and allowed the live defect to pass. |
| `tests/e2e/test_api_openapi.py` | 🟢 Strong | Exact route-set equality, count 61, per-method census, and export check. |
| `tests/e2e/test_api_auth.py` | 🟢 Strong | Specific auth/envelope/CORS/request-id/lifespan assertions; download and conversion shutdown use separate spies across the scoped tests. |
| `tests/e2e/api_fakes.py` | 🟡 Adequate support fixture | No tests by design; observable fakes support the e2e contract suite. |
| `tests/integration/test_api_wiring.py` | 🟢 Strong | Real temporary SQLite and production composition-root smoke, including conversion list 200. |
| `mcp-server/tests/convert.test.ts` | 🟢 Strong overall | Exact action rows, strict-before-fetch, confirm-before-fetch, sanitized list envelope, settings, instructions, and kind-specific forwarded bodies. AC-32.8's source/dist checks are supplemented by the independently executed build gate. |
| `mcp-server/tests/action-index.test.ts` | 🟢 Strong | Exact KEEP slice, 59-row registry, registered tool census, method/path/body and fetch-count assertions. |
| `mcp-server/tests/strict-confirm.test.ts` | 🟢 Strong | Whole-index strictness and destructive/non-destructive fetch-count matrix. |
| `mcp-server/tests/fixtures.ts` | 🟡 Adequate support fixture | Exact 46-row KEEP and 13-row convert fixtures; no tests by design. |
| `mcp-server/tests/m7-resource.test.ts` | 🟢 Strong | Exact 59-key parity, registered descriptions, marker counts, settings resource and converter presence. |

### Contract and Documentation Checks

| Check | Result | Evidence |
|---|---|---|
| REST static-before-id and auth | pass | `packages/api/src/avkit_api/routes/conversions.py:149-270`; independent runtime order/401 probe. First `/{id}` occurrence is the route at line 249, not the module docstring. |
| Create union, wire maps, formatter, paths, settings | pass | Discriminated `ApiModel` members, named wire maps, `format_encode_speed`, pre-service file validation, and converter namespace negatives all pass the scoped tests. |
| GPU lazy GET / concurrency oracle | pass | Module lock + double-check at `routes/conversions.py:47-63`; AC-31.3/31.22 and the 152-test run passed. |
| Queue control / delete/reset/get | pass except F1 | Status/envelope and files-stay contracts pass; reorder empty-list validation is the blocking exception. |
| OpenAPI census | pass | `len(ROUTE_INDEX)==61`, committed export check clean, console `convert` covered. |
| MCP parity / strict / confirm / settings / M7 / M4 | pass | ACTION_INDEX 59 with KEEP 46, 13 convert rows, no stop/second URL space, destructive sets, converter settings, instructions, build, and `dist/toolsets/convert.js` all verified. |
| SSOT and scope lock | pass | MEU-31/32 exact status/plan binding, both phase-8 plan entries, unique next command; no Session 15 or Session 8c execution was performed. |
| Handoff claims / AC coverage | pass except F1 evidence gap | Every plan AC appears in its matching handoff; reproduced gate counts match the claimed 152/183. F1 shows AC-31.7 evidence is not exhaustive for its declared boundary. |

## Open Questions / Assumptions

- The approved plan's `nonempty permutation` rule at `implementation-plan.md:159` is treated as the execution contract. If Local Canon is instead intended to allow an empty reorder on an empty queue, the contract must be explicitly corrected and independently reviewed; the current implementation and evidence do not match the approved plan as written.

## Required Follow-up

Use `/execution-corrections` for F1 only. Enforce the nonempty `job_ids` boundary before `reorder_queue`, add a Red→Green negative contract test that proves 422 and no service call for `[]`, and apply the same declared constraint to the MCP reorder schema if REST/MCP boundary parity is retained. Re-run the registered API, OpenAPI, MCP, Red-evidence, and review checks. Do not start MEU-33, Session 15, or Session 8c.

## Verdict

`changes_required` — one evidence-backed High external-input contract defect remains. The otherwise green Python, MCP, OpenAPI, type, lint, Red-oracle, handoff, and SSOT checks do not override the independently reproduced 200 response for input the approved plan declares invalid.

## Residual Risk

The review concentrated on the declared Session 14 REST/MCP contract and independently exercised the production composition root for list/reorder behavior. Convert GUI, NavRail `/convert`, Downloader→Convert, and other approved deferrals were not treated as missing implementation.

---

## Corrections Applied (2026-08-26) — after Round 1 F1

Implementer corrections. Frontmatter verdict is `corrections_applied` until independent Codex recheck. Not an `approved` verdict.

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Empty `PUT /conversions/reorder` `{ job_ids: [] }` returned 200 | `ConversionReorderIn.job_ids = Field(min_length=1)`; MCP `z.array(z.string().min(1)).min(1)`; OpenAPI `minItems: 1` regen | Red: empty reorder 200 (`C:/Temp/av-kit/f1-red-ac-31-7.txt`; `C:/Temp/av-kit/f1-red-ac-32-3.txt`). Green: AC-31.7 422 + `reorder_calls==0`; AC-32.3 schema/handleTool fetch 0. H1 pytest **152 passed**; vitest **183 passed**; pyright 0 errors; OpenAPI `--check` after `-o`. |

Do not start MEU-33 / Session 15 / Session 8c.

---

## Recheck (2026-08-26) — Round 2

**Workflow**: `/execution-critical-review` recheck  
**Agent**: `gpt-5.6-sol`

### Intent Anchor

This recheck was supposed to determine whether the Round 1 F1 boundary defect is fixed in current REST, OpenAPI, test, production-wiring, and MCP behavior without starting MEU-33, Session 15, or Session 8c. The current implementation achieves that intent: empty reorder arrays are rejected before the service/fetch boundary on both surfaces, and no new High/Critical behavioral finding appeared in the registered verification gates.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 — empty `PUT /conversions/reorder` accepted with HTTP 200 | `corrections_applied`, pending independent verification | ✅ Fixed — REST and MCP reject the empty array before downstream work |

### Independent F1 Verification

| Requirement | Result | Current-state evidence |
|---|---|---|
| Pydantic array minimum | pass | `ConversionReorderIn.job_ids` is `Field(min_length=1)` at `packages/api/src/avkit_api/schemas/conversions.py:61-64`. |
| Committed OpenAPI minimum | pass | `ConversionReorderIn.job_ids` contains `"minItems": 1` at `openapi.committed.json:552-568`; export `--check` exited 0. |
| Fake-backed AC-31.7 | pass | `tests/e2e/test_api_conversions.py:414-432` asserts empty input returns 422, `reorder_calls == 0`, and a valid request increments the counter once; the targeted test passed. |
| Real production composition | pass | A fresh `build_services` + temporary SQLite + `create_app` probe returned `422` with code `validation_error`, not 200. Receipt: `C:/Temp/av-kit/p8-api-mcp-exec-r2-real-empty-reorder-probe.txt`. |
| MCP reorder schema | pass | `mcp-server/src/toolsets/convert.ts:91-94` uses `z.array(z.string().min(1)).min(1)`. |
| MCP parse/dispatch negative | pass | `mcp-server/tests/convert.test.ts:79-107` asserts failed `safeParse`, error from `handleTool`, and fetch count 0 for empty `job_ids`; targeted AC-32.3 and the full Vitest suite passed. |

### Commands Executed

| Verification | Result | Receipt |
|---|---|---|
| Static current-state F1 source/test/OpenAPI sweep | required constraints and assertions present | `C:/Temp/av-kit/p8-api-mcp-exec-r2-f1-static-evidence.txt` |
| `uv run pytest tests/e2e/test_api_conversions.py::test_ac_31_7_reorder -x --tb=short -v` | 1 passed | `C:/Temp/av-kit/p8-api-mcp-exec-r2-ac31-7.txt` |
| `npx vitest run tests/convert.test.ts -t "AC-32.3"` | 1 passed | `C:/Temp/av-kit/p8-api-mcp-exec-r2-ac32-3.txt` |
| Real `build_services` + temporary SQLite empty-reorder probe | HTTP 422 `validation_error` | `C:/Temp/av-kit/p8-api-mcp-exec-r2-real-empty-reorder-probe.txt` |
| `uv run pytest tests/e2e tests/integration/test_api_wiring.py -x --tb=short -v` | 152 passed | `C:/Temp/av-kit/p8-api-mcp-exec-r2-pytest.txt` |
| `npx tsc --noEmit` | exit 0 | `C:/Temp/av-kit/p8-api-mcp-exec-r2-tsc.txt` |
| `npx vitest run` | 183 passed | `C:/Temp/av-kit/p8-api-mcp-exec-r2-vitest.txt` |
| `npm run build` | exit 0 | `C:/Temp/av-kit/p8-api-mcp-exec-r2-mcp-build.txt` |
| `uv run python tools/export_openapi.py --check openapi.committed.json` | exit 0; no drift | `C:/Temp/av-kit/p8-api-mcp-exec-r2-openapi-check.txt` |
| `uv run ruff check packages/api/src/avkit_api/schemas/conversions.py tests/e2e/test_api_conversions.py` | all checks passed | `C:/Temp/av-kit/p8-api-mcp-exec-r2-ruff.txt` |
| `uv run pyright packages/api` | 0 errors, 0 warnings | `C:/Temp/av-kit/p8-api-mcp-exec-r2-pyright.txt` |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-4 Fix generalization | pass | REST schema/OpenAPI/test/runtime and the parity MCP schema/test all enforce the same nonempty-array rule. |
| IR-5 Test rigor | pass | Corrected AC-31.7 and AC-32.3 assert the rejected result and the absence of downstream calls, then the full suites pass. |
| IR-6 Boundary validation | pass | Empty REST input maps to 422 before `reorder_queue`; empty MCP input fails Zod before fetch. |
| Registered regression gates | pass | Python, MCP type/test/build, OpenAPI, Ruff, and Pyright receipts are all green. |

### Findings

None. F1 is independently reproduced as fixed, and the Round 2 sweeps produced no new evidence-backed High/Critical behavioral finding.

### Open Questions / Assumptions

None. Current file state and fresh receipts were used; implementer correction labels were not treated as evidence. Git history/status was unavailable because this workspace is not a Git repository, which does not affect the direct-state/runtime verdict.

### Verdict

`approved` — F1 is fixed across REST, committed OpenAPI, fake-backed negative behavior, real temporary-SQLite composition, and MCP schema/dispatch behavior. With all registered gates passing and no new High/Critical behavioral finding, the Materiality Gate requires approval with `findings_count: 0`.

### Residual Risk

No residual F1 risk was reproduced. This was a correction recheck scoped to F1 plus the user-registered regression gates; MEU-33, Session 15, and Session 8c were not started or reviewed as delivery requirements.
