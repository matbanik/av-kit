---
review_mode: implementation
target_plan: docs/execution/plans/2026-08-27-p9-capture-api-mcp/implementation-plan.md
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
date: 2026-08-27
template_version: 2.1
dispatch_id: p9-capture-api-mcp-exec-r2
---

# Critical Review: p9-capture-api-mcp

> **Review Mode**: `implementation`  
> **Verdict**: `changes_required`  
> **Round**: 1  
> **Dispatch ID**: `p9-capture-api-mcp-exec-r1`

## Intent Anchor

Session 17 is limited to MEU-37 REST `/captures` plus MEU-38 MCP `avkit_capture`. Capture GUI, tray, F2 overlay, NavRail `/capture`, MEU-39, Session 8c / MEU-27, and MCP `complete` / `cancel` / `register` are explicit exclusions and were not treated as missing work. The implementation satisfies most of the approved API/MCP contract and all registered gates are green, but one independently reproduced media-contract defect crosses REST and MCP and requires correction before approval.

## Findings

| Finding | Severity | Evidence and impact | Required correction |
|---|---|---|---|
| **F1 — Annotated PNG bytes inherit the original file's MIME type.** `get_capture_image()` always derives `media_type` from `shot.original_path`, even when `variant=annotated` (`packages/api/src/avkit_api/routes/captures.py:219-223`). The service deterministically writes annotations to `{stem}.annotated.png` (`packages/core/src/avkit_core/services/capture.py:305-325`) and the adapter documents/writes PNG (`packages/infrastructure/src/avkit_infra/capture/adapter.py:114-120`). With an original `photo.jpg` and `photo.annotated.png`, the independent HTTP probe returned `status=200`, `content_type=image/jpeg`, and `png_magic=True` (`C:/Temp/av-kit/p9-api-mcp-exec-r1-annotated-jpeg-mime-probe.txt`). `apiBinary()` trusts the HTTP header (`mcp-server/src/client.ts:190-215`), and the independent MCP probe consequently returned `type=image`, `mimeType=image/jpeg`, `png_data=true` (`C:/Temp/av-kit/p9-api-mcp-exec-r1-mcp-annotated-mime-probe.txt`). This violates the REST image MIME contract and MEU-38 ImageContent `mimeType` contract for supported JPEG/WebP originals. The current API test covers original PNG plus missing annotated only (`tests/e2e/test_api_captures.py:554-573`). | **High** | Reproduced through authenticated FastAPI and built MCP runtime; affects valid supported inputs, not malformed or out-of-scope behavior. | Select MIME from the resolved variant path (annotated path for `variant=annotated`) or return path/media metadata with the service payload. Add Red→Green regression coverage using a JPEG or WebP original plus `.annotated.png`, asserting HTTP `image/png` and MCP `mimeType: image/png`. |
| **F2 — AC-37.18's declared integration lifecycle is not regression-protected.** The plan classifies port + SQLAlchemy `CaptureRequestRepository.list()` plus `CaptureService.list_requests()` as `integration` (`docs/execution/plans/2026-08-27-p9-capture-api-mcp/implementation-plan.md:204`). Its matching test asserts `hasattr` and source-string presence only (`tests/e2e/test_api_captures.py:768-781`). The real SQLite wiring test exercises `GET /captures`, not `GET /captures/requests` (`tests/integration/test_api_wiring.py:13-39`), while the prior real repository round trip uses request `get()` / `get_pending_request()` but not the newly added request `list()` (`tests/unit/test_capture_adapter.py:194-213`). The fake-backed route test does verify expire/filter semantics, so no second runtime defect was reproduced; this is an IR-7 lifecycle-evidence gap. | **Medium** | The implementation at `packages/core/src/avkit_core/services/capture.py:283-292` and `packages/infrastructure/src/avkit_infra/database/repositories.py:453-478` is plausible and the full suite passes, but a future broken SQLAlchemy `list()` could remain green. | Add a real temporary-SQLite contract test that persists multiple capture requests, exercises `CaptureRequestRepository.list()` ordering, and calls authenticated `GET /captures/requests` through built `AppServices` to prove expire-then-list without dependency overrides. |

## Scope

**Correlated plan:** `docs/execution/plans/2026-08-27-p9-capture-api-mcp/implementation-plan.md` (plan review Round 3 `approved`)

**Task and named contract:**

- `docs/execution/plans/2026-08-27-p9-capture-api-mcp/task.md`
- `docs/execution/plans/2026-08-27-p9-capture-api-mcp/named-sets.json`

**Expanded handoff set:**

- `.agent/context/handoffs/2026-08-27-p9-capture-api-mcp-MEU-37-handoff.md`
- `.agent/context/handoffs/2026-08-27-p9-capture-api-mcp-MEU-38-handoff.md`

**Correlation rationale:** the task frontmatter and named `HANDOFFS` bind exactly MEU-37 + MEU-38 to Session 17. Both handoffs were loaded because REST and MCP share the image, catalog-envelope, settings, and action-parity contracts. Current files were treated as authoritative because the workspace was not assumed to be a Git repository.

**Implementation reviewed:** the user-named API routes/schemas/errors/wiring/lifespan/dependencies, core wire/service/storage port, SQLAlchemy request repository, MCP capture/registry/settings/destructive/index/client surfaces, all named Python and TypeScript tests, OpenAPI, SSOT, task, named sets, build-plan REST/MCP sections, and both MEU handoffs.

## Commands Executed

| Verification | Result | Receipt |
|---|---|---|
| Registered H1 Python gate: `uv run pytest tests/e2e tests/integration/test_api_wiring.py tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py -x --tb=short -v` | **217 passed**, 1 warning | `C:/Temp/av-kit/p9-api-mcp-exec-r1-pytest.txt` |
| MCP TypeScript gate: `npx tsc --noEmit` | pass | `C:/Temp/av-kit/p9-api-mcp-exec-r1-mcp-tsc.txt` |
| MCP tests: `npx vitest run` | **214 passed** in 9 files | `C:/Temp/av-kit/p9-api-mcp-exec-r1-mcp-vitest.txt` |
| MCP M4: `npm run build` | pass; `dist/toolsets/capture.js` exists | `C:/Temp/av-kit/p9-api-mcp-exec-r1-mcp-build.txt` |
| OpenAPI G8: `uv run python tools/export_openapi.py --check openapi.committed.json` | pass | `C:/Temp/av-kit/p9-api-mcp-exec-r1-openapi-check.txt` |
| Independent OpenAPI/source/SSOT/AppServices invariant probe | 71 total routes; 10 capture routes; static-before-ID, `capture=` sites, no queue, SSOT/hub/core locks pass | `C:/Temp/av-kit/p9-api-mcp-exec-r1-python-invariants.txt` |
| Independent built-MCP invariant probe | ACTION_INDEX 67; first 59 capture-free; 8 exact capture actions; REST-only actions absent; settings/destructive locks pass | `C:/Temp/av-kit/p9-api-mcp-exec-r1-node-invariants.txt` |
| Red-oracle MEU-37 | count **19** pass | `C:/Temp/av-kit/p9-api-mcp-exec-r1-red-oracle-py.txt` |
| Red-oracle MEU-38 | count **13** pass | `C:/Temp/av-kit/p9-api-mcp-exec-r1-red-oracle-ui.txt` |
| Scoped Ruff | all checks passed | `C:/Temp/av-kit/p9-api-mcp-exec-r1-ruff.txt` |
| Scoped Pyright | 0 errors, 0 warnings | `C:/Temp/av-kit/p9-api-mcp-exec-r1-pyright.txt` |
| Placeholder and G36 skip/todo scans | no hits | `C:/Temp/av-kit/p9-api-mcp-exec-r1-anti-placeholder.txt`; `C:/Temp/av-kit/p9-api-mcp-exec-r1-g36.txt` |
| Assertion/test census across every named test file | counts recorded; no assertion-free collected test file | `C:/Temp/av-kit/p9-api-mcp-exec-r1-test-rigor-counts.txt` |
| JPEG-original / annotated-PNG authenticated HTTP probe | **failed expected MIME assertion**: PNG bytes labeled `image/jpeg` | `C:/Temp/av-kit/p9-api-mcp-exec-r1-annotated-jpeg-mime-probe.txt` |
| Built MCP ImageContent propagation probe | **failed expected MIME assertion**: PNG data emitted with `mimeType=image/jpeg` | `C:/Temp/av-kit/p9-api-mcp-exec-r1-mcp-annotated-mime-probe.txt` |

## Checklist Results

### Implementation Review (IR)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | The full 217-test API suite includes authenticated FastAPI and temporary-SQLite wiring; the independent HTTP probe exercised the live router and reproduced F1. |
| IR-2 Stub behavioral compliance | pass | No completed-deliverable placeholder/stub was found; fake list/filter/expiry and insert counters have specific assertions. |
| IR-3 Error mapping completeness | pass | `InboxPathError` / `AnnotationValidationError` map 422, grab/platform errors map 503, `ConflictError` subclasses map 409, and string IDs return 404 envelopes (`packages/api/src/avkit_api/errors.py:25-38`; 19 API contract tests pass). |
| IR-4 Fix generalization | n/a | Round 1; there is no prior implementation-review finding to recheck. |
| IR-5 Test rigor audit | fail (F1, F2) | Assertions are generally specific, but the supported cross-format annotated-image case is absent and AC-37.18's real repository/list lifecycle is static/fake-backed. Per-file grades follow. |
| IR-6 Boundary validation coverage | pass | Discriminated Pydantic members inherit strict `ApiModel`; Zod capture members are `.strict()`; malformed/extra/confirm/error cases fail before downstream work. No create/update parity surface exists. |
| IR-7 Deferral and AC-coverage integrity | fail (F2 only) | Every AC-37.* / AC-38.* ID appears in its handoff and all exclusions are source-backed or scheduled. AC-37.18 lacks its declared live integration evidence; no orphan/disguised deferral was found. |

### IR-5 Test Rigor Audit

| Test file | Grade | Rationale |
|---|---|---|
| `tests/e2e/test_api_captures.py` | 🟡 Adequate | 19 tests / 125 assertions cover positive and negative REST contracts, but miss annotated MIME for non-PNG originals and use static checks for AC-37.18. |
| `tests/e2e/test_api_openapi.py` | 🟢 Strong | Exact 71-route census, per-method/path membership, and static-before-ID regression. |
| `tests/e2e/test_api_auth.py` | 🟢 Strong | Eight tests / 38 assertions plus four negative raises cover tokens, envelopes, lifespan, request IDs, CORS, and strict `ApiModel`. |
| `tests/e2e/test_api_conversions.py` | 🟢 Strong for scoped KEEP behavior | Specific queue-envelope, conversion-cancel, settings, static-route, and wire assertions remain intact. |
| `tests/integration/test_api_wiring.py` | 🟢 Strong for G29 catalog wiring | Uses built services and temporary SQLite; verifies `/captures` is a catalog without `processor`, though F2 identifies the missing request-list path. |
| `mcp-server/tests/capture.test.ts` | 🟡 Adequate | 13 tests / 75 expectations strongly cover schema, action, envelope, confirm, query, timeout, and image shape, but the image test supplies a correct mocked MIME and cannot expose F1 across REST. |
| `mcp-server/tests/action-index.test.ts` | 🟢 Strong | Exact index/tool registration, method/path/body, and fetch-count assertions. |
| `mcp-server/tests/strict-confirm.test.ts` | 🟢 Strong | Parametric strictness and destructive-confirm checks assert TOOL_ERROR and zero fetch. |
| `mcp-server/tests/fixtures.ts` | support file audited | Capture action, destructive, and minimal-input fixtures preserve the 67-row census and eight-row capture set; it contains no collected tests. |
| `mcp-server/tests/m7-resource.test.ts` | 🟢 Strong | Exact 67-description/resource census and marker/instruction checks. |
| `mcp-server/tests/convert.test.ts` | 🟢 Strong for scoped KEEP behavior | Exact convert action/envelope/strictness/timeout/dist assertions prove capture catalog changes did not weaken queue semantics. |

### Adversarial Verification (AV)

| Check | Result | Evidence |
|---|---|---|
| AV-1 Failing-then-passing proof | pass | Independent Red-oracle validation accepts MEU-37 count 19 and MEU-38 count 13; the Python Red command omitted `-x`. |
| AV-2 No bypass hacks | pass | G36 scans are clean; tests use explicit status/value/fetch-count assertions rather than skipped/todo guards. |
| AV-3 Changed paths exercised by assertions | fail (F1, F2) | Main paths are asserted, but cross-format annotated MIME and the real request-list repository lifecycle are not. |
| AV-4 No skipped/xfail masking | pass | No scoped pytest/Vitest skip, xfail, todo, `xit`, or `xdescribe` hit. |
| AV-5 No unresolved placeholders | pass | No `TODO`, `FIXME`, or `NotImplementedError` hit in API or MCP source. |
| AV-6 Source-backed criteria | pass | Findings are anchored to the approved plan, Phase 9 REST/MCP spec, and delivered path/format behavior. No GUI or invented action requirement was introduced. |

### Adversarial Contract Surfaces

| Surface | Result | Evidence |
|---|---|---|
| Catalog, not queue | pass | Both capture GET envelopes are `{ items }`; `processor` is rejected; `captures` is absent from `QUEUE_NAMES`. |
| Static routes, auth, OpenAPI | pass | Quoted `"/requests"` precedes the first `/{id}`; unauthenticated catalog returns 401; all 10 `{id}` routes are in the 71-route schema. |
| Discriminated create / strict empty POSTs | pass | Register/fullscreen/region negative cases and empty interactive/cancel extra-key cases return 422; create is 201 `{ item }`. |
| HTTP map and string IDs | pass | 422 / 503 / 409 mappings and six `not-a-uuid` route families return 404 `NotFoundError`. |
| Wires, cap, default variant | pass except F1 | Lowercase query/input and Pascal output wires pass; 15 MiB cap, dual Bearer, and default original pass. Variant-specific MIME selection fails for annotated output. |
| Complete one UoW | pass | Unknown request plus valid path returns 404 with zero fake insert; successful completion returns `shot_id`. |
| Capture settings | pass | Four defaults/leaves, PUT strictness, and unknown namespace behavior pass. |
| AppServices / lifespan / G29 | pass | All named constructors use `capture=`; no capture cancel; download/conversion cancel remain once; temporary-SQLite catalog returns 200. |
| `list_requests` port/service/repository | pass in code; evidence gap F2 | Service expires then lists and port/SQLAlchemy/fakes expose `list()`; the real SQLAlchemy list path is not regression-tested. |
| MCP index and scope lock | pass | 67 rows, first 59 unchanged/capture-free, eight exact capture actions, no REST-only actions, toolsets path only. |
| Zod / confirm / envelopes / sanitize | pass | Strict extra fields and missing confirm stop before fetch; capture rejects `processor`; convert still requires it; `image_bytes` is removed. |
| ImageContent / query / timeout / dist | **fail (F1)** | Image content shape, query keys, cap, timeout, and dist pass; MIME is wrong for annotated PNG derived from JPEG/WebP originals. |
| AC coverage / deferrals | pass except F2 | All 32 AC IDs appear in matching handoffs; GUI/MEU-39 and Session 8c remain pending; MCP complete/cancel/register remain source-backed exclusions. |

## Open Questions / Assumptions

None. F1 follows directly from supported original extensions, the deterministic `.annotated.png` output, and the REST/MCP media contract. Current file state was reviewed directly because Git history was not assumed available.

## Required Follow-up

Use `/execution-corrections` for F1 and F2. Write the failing regression tests before production changes, preserve all current tests, then rerun the registered 217-test API gate, TypeScript/Vitest/build chain, OpenAPI G8, Ruff/Pyright, Red-oracle, placeholder/G36, handoff, and SSOT checks before an independent Round 2 recheck.

Corrections must remain inside Session 17 / MEU-37 + MEU-38. Do not start Capture GUI, tray, F2 overlay, NavRail `/capture`, MEU-39, Session 8c / MEU-27, or add MCP `complete`, `cancel`, or `register` actions.

## Verdict

`changes_required` — F1 is an independently reproduced High REST/MCP media-contract defect on valid supported inputs. F2 is a Medium lifecycle-test gap and does not independently control the verdict. The green 217-test API suite, 214-test MCP suite, type/lint/build gates, Red-oracle receipts, AC coverage, OpenAPI, and SSOT bindings do not override PNG bytes being mislabeled as JPEG/WebP across both delivered interfaces.

## Residual Risk

The review exercised authenticated FastAPI behavior, built MCP runtime behavior, temporary-SQLite wiring, exact OpenAPI/action/SSOT invariants, and every named test file. It did not perform a live unattended desktop screen grab because F1 is reproducible without OS capture and GUI/tray/overlay behavior belongs to MEU-39. A live MCP process connected to a separately running API was not required to demonstrate F1 because both sides were exercised independently and the header propagation path is direct.

---

## Corrections Applied — 2026-08-27 after Round 1

Implementer (not the reviewer). Verdict remains `corrections_applied` until an independent Round 2 pass. Red: `C:/Temp/av-kit/pytest-p9-exec-r1-corrections-red.txt` (AC-37.10 MIME + AC-37.18 naive/aware expire TypeError). Targeted green: `C:/Temp/av-kit/pytest-p9-exec-r1-corrections-green.txt` (4 passed). Full H1 pytest: `C:/Temp/av-kit/pytest-p9-api-mcp-h1-corrections.txt` (**217 passed**). MCP: `C:/Temp/av-kit/mcp-p9-api-mcp-h1-corrections.txt` (**214 passed**). OpenAPI `--check`: `C:/Temp/av-kit/openapi-check-corrections.txt`. Ruff/Pyright: `C:/Temp/av-kit/ruff-p9-exec-r1-corrections.txt` / `C:/Temp/av-kit/pyright-p9-exec-r1-corrections.txt`.

| Finding | Fix | Tests |
|---------|-----|-------|
| F1 | `get_capture_image` derives `media_type` from the resolved variant path (`annotated_path` for `variant=annotated`, else `original_path`). MCP `apiBinary` sniffs PNG/JPEG/WebP magic so a lying `Content-Type` cannot emit PNG bytes as `image/jpeg`. | AC-37.10 JPEG/WebP original + `.annotated.png` asserts HTTP `image/png`; AC-38.11 annotated fetch with JPEG header + PNG bytes asserts `mimeType: image/png`. |
| F2 | AC-37.18 now persists two request rows on real tmp SQLite, asserts `CaptureRequestRepository.list()` `created_at` desc, then authenticated `GET /captures/requests` through built `AppServices` (expire-then-list, no overrides). Sibling: `expire_stale_requests` compared mapper UTC-aware `expires_at` to naive `datetime.now()` and raised `TypeError`; `_now()` / `_as_utc()` normalize both sides. AC-35.4 now calls request `list()`. | `test_ac_37_18_list_requests_port`; `test_ac_35_4_round_trip_columns`; `test_ac_36_7_expire_stale_from_list_and_get` remains green. |

Scope lock held: no MEU-39 / Session 8c / MCP complete/cancel/register. Plan and `task.md` were not edited.

---

## Round 2 Recheck — 2026-08-27

**Workflow**: `/execution-critical-review`  
**Agent**: `gpt-5.6-sol`  
**Dispatch ID**: `p9-capture-api-mcp-exec-r2`

### Intent Anchor

Session 17 was required to deliver MEU-37 REST `/captures` plus MEU-38 MCP `avkit_capture`, including truthful variant/image MIME and a persisted expire-then-list request lifecycle. The delivered work now achieves that intent; Capture GUI/tray/F2/NavRail, Session 18 / MEU-39, Session 8c / MEU-27, and MCP `complete` / `cancel` / `register` remain explicit exclusions and were not treated as missing work.

### Scope and Correlation

The plan/task/named-set contract under `docs/execution/plans/2026-08-27-p9-capture-api-mcp/` binds exactly MEU-37 and MEU-38 to the two same-slug work handoffs. Round 2 rechecked the current files directly because Git availability was not assumed. Primary correction scope was the API variant MIME path, UTC expiry comparison, SQLAlchemy request-list ordering, MCP image magic sniffing, and their Python/TypeScript regression tests. The Round 1 passing REST/MCP surfaces were spot-checked for regression.

### Findings

| Finding | Severity | Evidence | Status |
|---------|----------|----------|--------|
| No surviving Round 2 finding. | — | Both prior findings are fixed; no new evidence-backed High/Critical behavioral or contract defect was found. | — |

### Prior Findings Recheck (IR-4)

| Finding | Severity | Prior Status | Round 2 evidence | Recheck Result |
|---------|----------|--------------|------------------|----------------|
| **F1 — annotated PNG MIME** | High | open | REST chooses MIME from the resolved variant path (`packages/api/src/avkit_api/routes/captures.py:213-229`); JPEG and WebP originals with `.annotated.png` assert HTTP `image/png` (`tests/e2e/test_api_captures.py:555-622`). MCP recognizes PNG/JPEG/WebP magic before returning the declared type (`mcp-server/src/client.ts:160-190`, `mcp-server/src/client.ts:223-249`), and AC-38.11 proves PNG bytes override a mocked `image/jpeg` header (`mcp-server/tests/capture.test.ts:236-262`). Fresh full gates pass. | **Fixed** |
| **F2 — request-list lifecycle evidence** | Medium | open | The port exposes `list()` (`packages/core/src/avkit_core/ports/storage.py:141-152`); SQLAlchemy orders `created_at DESC` (`packages/infrastructure/src/avkit_infra/database/repositories.py:453-478`); the service expires then lists and UTC-normalizes both naive and aware timestamps (`packages/core/src/avkit_core/services/capture.py:271-292`, `packages/core/src/avkit_core/services/capture.py:368-375`). AC-37.18 persists two real SQLite rows, verifies ordering, and calls authenticated `GET /captures/requests` through built `AppServices` without a dependency override (`tests/e2e/test_api_captures.py:816-874`). AC-35.4 calls repository `list()` (`tests/unit/test_capture_adapter.py:149-215`), and AC-36.7 remains green. | **Fixed** |

The preserved correction Red receipt is valid: `C:/Temp/av-kit/pytest-p9-exec-r1-corrections-red.txt` records the old JPEG mislabel and naive/aware `TypeError` as two failures before the production fixes, while AC-35.4 remained green.

### Commands Executed

| Verification | Result | Receipt |
|---|---|---|
| Registered H1 Python gate: `uv run pytest tests/e2e tests/integration/test_api_wiring.py tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py -x --tb=short -v` | **217 passed**, 1 warning | `C:/Temp/av-kit/p9-api-mcp-exec-r2-pytest.txt` |
| MCP `npx tsc --noEmit` | pass | `C:/Temp/av-kit/p9-api-mcp-exec-r2-mcp-tsc.txt` |
| MCP `npx vitest run` | **214 passed** in 9 files | `C:/Temp/av-kit/p9-api-mcp-exec-r2-mcp-vitest.txt` |
| MCP `npm run build` | pass | `C:/Temp/av-kit/p9-api-mcp-exec-r2-mcp-build.txt` |
| OpenAPI G8 `--check openapi.committed.json` | pass | `C:/Temp/av-kit/p9-api-mcp-exec-r2-openapi-check.txt` |
| Python invariants | 71 routes; 10 capture routes; static-before-ID, 422/503 map, all `AppServices.capture=`, and no lifespan capture cancel pass | `C:/Temp/av-kit/p9-api-mcp-exec-r2-python-invariants.txt` |
| Built MCP invariants | ACTION_INDEX 67; first 59 capture-free; eight exact capture actions; REST-only actions absent | `C:/Temp/av-kit/p9-api-mcp-exec-r2-node-invariants.txt` |
| Red oracle MEU-37 / MEU-38 | counts **19** / **13**, pass | `C:/Temp/av-kit/p9-api-mcp-exec-r2-red-oracle-py.txt`; `C:/Temp/av-kit/p9-api-mcp-exec-r2-red-oracle-ui.txt` |
| Scoped Ruff / Pyright | all checks passed / 0 errors and warnings | `C:/Temp/av-kit/p9-api-mcp-exec-r2-ruff.txt`; `C:/Temp/av-kit/p9-api-mcp-exec-r2-pyright.txt` |
| Placeholder and G36 scans | clean | `C:/Temp/av-kit/p9-api-mcp-exec-r2-anti-placeholder.txt`; `C:/Temp/av-kit/p9-api-mcp-exec-r2-g36.txt` |
| Handoff AC and marker validators | pass | `C:/Temp/av-kit/p9-api-mcp-exec-r2-handoff-ac-check.txt`; `C:/Temp/av-kit/p9-api-mcp-exec-r2-handoff-marker-check.txt` |
| Fresh assertion census | all scoped files have substantive assertions; no assertion-free test surface found | `C:/Temp/av-kit/p9-api-mcp-exec-r2-test-rigor-counts.txt` |
| `check_exec_review.py --self-test` and live review-file check | pass; `latest execution review approved` | `C:/Temp/av-kit/p9-api-mcp-exec-r2-review-selftest.txt`; `C:/Temp/av-kit/p9-api-mcp-exec-r2-review-check.txt` |
| Dispatch-binding check inside reviewer turn | outer dispatch not yet finalized: `status.json` absent | `C:/Temp/av-kit/p9-api-mcp-exec-r2-dispatch-check.txt` |

### Round 1 Passing-Surface Spot Checks

| Surface | Result | Evidence |
|---|---|---|
| Catalog `{ items }`, no `processor`; convert list still requires `processor` | pass | Capture and queue predicates remain separate (`mcp-server/src/toolsets/registry.ts:222-235`, `mcp-server/src/toolsets/registry.ts:315-325`); convert regression assertions remain specific (`mcp-server/tests/convert.test.ts:150-166`). |
| Static `/requests` before `/{id}` | pass | Router registers `/requests` at `packages/api/src/avkit_api/routes/captures.py:164-182` before the first `/{id}` route at `packages/api/src/avkit_api/routes/captures.py:206-229`; structured probe passed. |
| Discriminated create and strict boundaries | pass | `CaptureCreateIn` uses a `mode` discriminator (`packages/api/src/avkit_api/schemas/captures.py:41-43`), and `ApiModel` forbids extras (`packages/api/src/avkit_api/schemas/common.py:8-11`); the 19 current API AC tests pass. |
| 422 / 503 / 409 / 404 mappings | pass | Capture 422/503 entries remain in `DOMAIN_HTTP_MAP` (`packages/api/src/avkit_api/errors.py:25-38`); the full API gate covers conflict and malformed/unknown string-ID envelopes. |
| `AppServices.capture=` and lifespan | pass | `AppServices` retains the capture leaf (`packages/api/src/avkit_api/wiring.py:56-67`); every named constructor passed the AST probe, while lifespan cancels download/conversion only (`packages/api/src/avkit_api/main.py:45-46`). |
| MCP action scope and count | pass | Built ACTION_INDEX is 67 with exactly `list,get,image,capture,capture_interactive,list_requests,annotate,remove` (`mcp-server/src/toolsets/registry.ts:51-118`); `complete`, `cancel`, and `register` are absent. |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | AC-37.18 uses real temporary SQLite plus built services and authenticated FastAPI without dependency overrides; the full 217-test gate passed. |
| IR-2 Stub behavioral compliance | pass | No completed-deliverable placeholder/stub was found; real repository ordering and service expiry behavior are value-asserted. |
| IR-3 Error mapping completeness | pass | Current 422/503 map, conflict 409, and unknown string-ID 404 behavior pass the registered suite. |
| IR-4 Fix generalization | pass | F1 is corrected at both REST and MCP boundaries with JPEG/WebP/PNG coverage; F2 covers port, SQL repository, service UTC normalization, built wiring, and route behavior. |
| IR-5 Test rigor audit | pass | No weak test remains on the corrected paths. Per-file grades follow. |
| IR-6 Boundary validation | pass | Pydantic discriminated members inherit `extra="forbid"`; capture Zod actions remain strict; malformed/extra/confirm cases stop before downstream work. |
| IR-7 Deferral and AC coverage | pass | Both handoff AC sets validate; all exclusions are source-backed and no orphan/disguised deferral was found. |
| AV-1 through AV-6 | pass | Valid Red receipts, no bypass/skip masking, changed paths asserted, placeholders absent, and all criteria remain source-backed. |

### IR-5 Test Rigor Grades

| Test file(s) | Grade | Rationale |
|---|---|---|
| `tests/e2e/test_api_captures.py` | Strong | 19 tests / 143 assertions now include cross-format annotated MIME and real SQLite expire-then-list through built services. |
| `tests/unit/test_capture_adapter.py`; `tests/unit/test_capture_service.py` | Strong | Real persistence round trips, request `list()`, transition/expiry behavior, image variants, and failure paths have specific value assertions. |
| `tests/e2e/test_api_openapi.py`; `test_api_auth.py`; `test_api_health_settings.py`; `test_api_conversions.py`; `tests/integration/test_api_wiring.py` | Strong for scoped surfaces | Exact route/auth/settings/envelope/wiring/lifecycle assertions remained green. |
| `mcp-server/tests/capture.test.ts` | Strong | 13 tests / 78 expectations include lying-header magic sniff, exact base64/MIME, oversize, strictness, query, action, and envelope behavior. |
| `mcp-server/tests/action-index.test.ts`; `strict-confirm.test.ts`; `m7-resource.test.ts`; `convert.test.ts`; `client.test.ts` | Strong for scoped surfaces | Exact action/parity, fetch-count, description, queue-envelope, client error/redaction, and build-facing behavior remained green. |
| `mcp-server/tests/fixtures.ts` | support file audited | The capture fixtures preserve the 67-row/eight-action census; no collected tests live in this file. |

### Open Questions / Assumptions

None. Current files and fresh receipts were authoritative; no Git diff was required.

### Verdict

`approved` — Round 1 F1 and F2 are fixed with direct file evidence, valid Red→Green regression protection, and fresh independent runtime verification. `findings_count` is 0 because no new evidence-backed finding survived the generate→verify pass.

### Follow-up and Residual Risk

No `/execution-corrections` follow-up is required. The outer orchestrator must rerun `assert-exec-review-dispatch.ps1` after this reviewer turn finalizes and creates `C:/Temp/av-kit/dispatch/p9-capture-api-mcp-exec-r2/status.json`; the in-turn missing-status result is orchestration timing, not a product finding. This review did not perform H2 closeout, start Session 18 / MEU-39, start Session 8c / MEU-27, or add any REST-only MCP action. GUI/tray/F2/overlay behavior remains outside Session 17; no live desktop capture was needed to verify the corrected API/MCP contracts.
