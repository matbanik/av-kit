---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md"
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
---

# Critical Review: p4-rest-api Implementation

## Intent Anchor

Session 5 was intended to expose the approved MEU-14–16 service contracts as a complete, strict FastAPI `/api/v1` boundary: authenticated routes, canonical error/list envelopes, constrained request models, safe transcript/TTS representations, asynchronous model download, a real tmp-SQLite composition-root health smoke, and a committed OpenAPI document. The delivered implementation achieves most runtime behavior, but it does not yet satisfy the approved model-download input boundary and its reorder tests leave material route behavior unprotected.

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|
| F1 | High | **The model-download boundary accepts an explicitly invalid empty variant ID and misclassifies it as a missing resource.** The approved boundary inventory requires `POST /models/download` `variant_id` to be non-empty, but `ModelDownloadIn.variant_id` is an unconstrained `str`. Independent HTTP probing with `{"variant_id":""}` reached the service and returned `404 NotFoundError`, rather than boundary-owned `422 ErrorEnvelope`. `ModelLoadIn` repeats the same unconstrained-ID pattern and also returned 404 for an empty ID. This violates the plan boundary at line 348 and IR-6/error-mapping correctness; it is a runtime contract defect, not clerical drift. Evidence: `C:/Temp/av-kit/p4-api-exec-r1-adversarial-http.txt`. | `docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md:348`; `packages/api/src/avkit_api/schemas/models.py:10`; `packages/api/src/avkit_api/schemas/models.py:13`; `packages/api/src/avkit_api/schemas/models.py:16`; `packages/api/src/avkit_api/schemas/models.py:19` | Add failing boundary tests first for empty model IDs (422 envelope and no service call), constrain the schema-owned IDs, apply the correction to both analogous model write routes, and regenerate/recheck `openapi.committed.json`. | open |
| F2 | Medium | **The reorder tests can pass when the route ignores or corrupts `job_ids`.** The download fake discards `job_ids`, and no positive download-reorder test observes the call or resulting order. The transcript fake also discards `job_ids`; its test asserts only HTTP 200. The body oracle exercises these routes only with an injected extra field, which is rejected before the route body runs. The production routes currently forward `body.job_ids`, but these tests would not catch a regression that removes or changes that forwarding, so the relevant assertions are weak under IR-2/IR-5. | `tests/e2e/test_api_downloads.py:135`; `tests/e2e/api_fakes.py:179`; `tests/e2e/test_api_transcripts.py:40`; `tests/e2e/test_api_transcripts.py:65`; `packages/api/src/avkit_api/routes/downloads.py:216`; `packages/api/src/avkit_api/routes/transcripts.py:127` | Give both fakes observable reorder behavior or call capture, then assert the exact forwarded permutation and response order for valid download and transcript reorder requests. | open |

## Scope

Reviewed the correlated plan/task pair, all three MEU handoffs, the complete `packages/api/src/avkit_api/` surface, the named core locks and G29 health guard, OpenAPI exporter/committed document, every scoped API test and shared fake, the real-wiring integration test, MEU status, and the BUILD_PLAN hub. The three handoffs correlate directly through their shared `plan_source` and MEU-14 → MEU-15 → MEU-16 sequence.

This workspace exposes no `.git` directory (`C:/Temp/av-kit/p4-api-exec-r1-workspace-probe.txt`), so the review used direct current file state and reproducible runtime evidence rather than diff metadata.

## Commands Executed

| Check | Result | Receipt |
|---|---|---|
| Required API + G29 suite | `107 passed`, exit 0 | `C:/Temp/av-kit/p4-api-exec-r1-pytest.txt` |
| Required committed OpenAPI check | exit 0; exact match | `C:/Temp/av-kit/p4-api-exec-r1-openapi.txt` |
| Focused bodies/TTS/transcripts/G29 suite | `36 passed`, exit 0 | `C:/Temp/av-kit/p4-api-exec-r1-adversarial-pytest.txt` |
| Core services + console lock regression | `66 passed`, exit 0 | `C:/Temp/av-kit/p4-api-exec-r1-core-tests.txt` |
| Independent adversarial HTTP matrix | voices 200/call count 1; compile exact keys and extra 422; source unread; no-model 409 vs invalid-speed 422; empty model IDs 404 | `C:/Temp/av-kit/p4-api-exec-r1-adversarial-http.txt` |
| Pyright API + core | `0 errors, 0 warnings`, exit 0 | `C:/Temp/av-kit/p4-api-exec-r1-pyright.txt` |
| Registered ruff scope | all checks passed, exit 0 | `C:/Temp/av-kit/p4-api-exec-r1-ruff-registered.txt` |
| Plan-to-handoff AC-set comparison | MEU-14: 9; MEU-15: 13; MEU-16: 10; all complete | `C:/Temp/av-kit/p4-api-exec-r1-ac-set-check.txt` |

## Checklist Results

### Implementation Review (IR-1..IR-7)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | `tests/integration/test_api_wiring.py:13` constructs `build_services` with tmp SQLite and runs real `/health`; reproduced in both the 107- and 36-test receipts. |
| IR-2 Stub behavioral compliance | fail | Most fakes preserve round trips and conflicts, but both reorder fakes discard their input; see F2. |
| IR-3 Error mapping completeness | pass | Global domain/HTTP/validation handlers are installed; representative 401/404/409/422/500 envelopes pass. The empty-ID 404 is a schema-boundary failure recorded separately in F1. |
| IR-4 Fix generalization | fail | The unconstrained model-ID pattern occurs in both `ModelDownloadIn` and `ModelLoadIn`; F1 requires correcting analogous write boundaries together. Named core locks themselves are generalized and their direct tests pass. |
| IR-5 Test rigor audit | fail | `test_api_auth.py` 🟢; `test_api_downloads.py` 🟡 (reorder not exercised positively); `test_api_health_settings.py` 🟢; `test_api_transcripts.py` 🟡 (reorder status-only); `test_api_tts_models.py` 🟡 (no empty-ID negative); `test_api_openapi.py` 🟢; `test_api_bodies.py` 🟢; `test_api_wiring.py` 🟢. Shared `api_fakes.py` is 🟡 because reorder is a no-op. F2 captures the material weakness. |
| IR-6 Boundary validation coverage | fail | Extra fields are comprehensively rejected across all POST/PUT routes, but the approved non-empty model-download ID constraint is missing and untested; reproduced as downstream 404 in F1. |
| IR-7 Deferral and AC coverage integrity | pass | Exact comparison found all 9/13/10 AC IDs in their matching handoffs. Deferred MEU-17–25 entries are registered and pending in `meu-status.yaml`; no orphan/disguised deferral found. |

### Documentation Review (DR-1..DR-8)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | fail | The handoff set claims complete boundary delivery, but F1 contradicts the approved boundary inventory. Other central claims reproduced successfully. |
| DR-2 Residual old/forbidden terms | pass | Runtime probes confirm transcript compile exposes only `compiled_paths`, transcript jobs omit `video_ids`/`text`, TTS emits `text_preview`, and voices omit `lang_code`. |
| DR-3 Downstream references updated | pass | MEU-14–16 are consistently `ready_for_review`; BUILD_PLAN Phase 4 is in progress and links Session 5. |
| DR-4 Verification robustness | fail | Existing checks miss empty model IDs and do not prove reorder forwarding/effect; F1/F2. |
| DR-5 Evidence auditability | pass | Required commands reproduced with named receipts and propagated exit codes. |
| DR-6 Cross-reference integrity | pass | Route census is exactly 48; live OpenAPI equals the committed document; plan/handoffs/status point to the same Session 5 project. |
| DR-7 Evidence freshness | pass | Reproduced `107 passed`; committed OpenAPI check and registered type/lint gates are current and green. |
| DR-8 Completion vs residual risk | fail | MEU-16 is marked complete without acknowledging the boundary defect in F1; approval would be a false completion claim until corrected. |

## Non-blocking Observations

An intentionally widened ruff run over the scoped test files found five import-order violations; the registered product/tool ruff scope passes. Under the materiality gate this is non-blocking and is not counted as a finding.

## Verdict

`changes_required` — F1 is an evidence-backed High runtime boundary/contract defect. F2 is a Medium test-rigor weakness that should be corrected in the same execution-corrections round. The remaining requested behavior—including dual Bearer, ErrorEnvelope, all-body extra rejection, list envelopes, transcript/TTS redaction, `TTS_NO_MODEL_CONFLICT`, `VOICES_FACADE`, asynchronous 202 model download, G29 health wiring, and committed OpenAPI—was independently reproduced as passing.

## Follow-up Actions

1. Route corrections through `/execution-corrections`; write the empty-ID negative tests before changing schemas.
2. Strengthen both reorder route tests with exact call/order assertions.
3. Re-run the required 107-test command, core lock tests, OpenAPI export/check, pyright, and registered ruff scope, then append Round 2 to this rolling review file.

## Update (2026-08-19, round 2)

### Intent Anchor

This recheck asks whether the corrected MEU-14–16 implementation now delivers the approved strict FastAPI `/api/v1` boundary without the round-1 empty-model-ID contract defect or reorder false-pass risk. The current implementation achieves that intent: both model write schemas own empty-ID rejection, both reorder routes have observable exact-permutation oracles, and the surrounding API, core locks, real-wiring smoke, OpenAPI, type, lint, and state contracts remain green.

### Round-1 Findings Recheck

| Finding | Recheck result | Evidence |
|---|---|---|
| F1 — empty model `variant_id` reached a downstream 404 | ✅ Fixed | `ModelDownloadIn` and `ModelLoadIn` both use `Field(min_length=1)` (`packages/api/src/avkit_api/schemas/models.py:15,21`). Independent HTTP probes returned 422 canonical envelopes for download and load and left `models.downloading` false; committed OpenAPI reports `minLength: 1` for both schemas. Receipts: `C:/Temp/av-kit/p4-api-exec-r2-runtime-probes.txt`, `C:/Temp/av-kit/p4-api-exec-r2-openapi-constraints.txt`. |
| F2 — download/transcript reorder tests could pass without forwarding/effect | ✅ Fixed | Production routes forward `body.job_ids` (`packages/api/src/avkit_api/routes/downloads.py:216`, `packages/api/src/avkit_api/routes/transcripts.py:127`). The download oracle asserts the fake call and response order (`tests/e2e/test_api_downloads.py:313-334`); the transcript oracle does the same before deletion (`tests/e2e/test_api_transcripts.py:17-74`). Independent valid-permutation probes reproduced both effects. Receipts: `C:/Temp/av-kit/p4-api-exec-r2-runtime-probes.txt`, `C:/Temp/av-kit/p4-api-exec-r2-transcript-reorder-probe.txt`. |

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|
| — | — | No findings survived generate→verify and the materiality gate. | — | — | — |

### Checklist Results

#### Implementation Review (IR-1..IR-7)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | `tests/integration/test_api_wiring.py:13-28` constructs `build_services` against tmp SQLite with no dependency overrides and proves `/health` plus DB creation. It passed inside the reproduced 109-test suite. |
| IR-2 Stub behavioral compliance | pass | The corrected reorder fakes permute their stored queues and record `last_reorder` (`tests/e2e/api_fakes.py:180-183,424-427`; the download-local fake at `tests/e2e/test_api_downloads.py:136-139`). Exact fake and response-list orders passed for both resources. Other scoped lifecycle/state fakes remain exercised by the 109-test suite. |
| IR-3 Error mapping completeness | pass | `RequestValidationError` owns schema failures and emits the canonical 422 envelope (`packages/api/src/avkit_api/errors.py:56-64`); domain mapping remains centralized at `errors.py:20-29,66-85`. The empty download/load probes returned exactly `error.{code,message,details}`, not FastAPI `detail`, and the suite retains representative 401/404/409/422/500 assertions. |
| IR-4 Fix generalization | pass | F1 was generalized across both analogous model write schemas and regenerated OpenAPI. F2 was generalized across both download and transcript reorder surfaces, with exact forwarding and returned-order oracles. Named core locks remain green in the 66-test direct regression receipt. |
| IR-5 Test rigor audit | pass | `test_api_auth.py` 🟢; `test_api_bodies.py` 🟢; `test_api_downloads.py` 🟢; `test_api_health_settings.py` 🟢; `test_api_openapi.py` 🟢; `test_api_transcripts.py` 🟢; `test_api_tts_models.py` 🟢; `test_api_wiring.py` 🟢. Assertions exercise specific status, envelope, state, call-count, exact-order, redaction, census, and real-wiring outcomes. No 🔴 test or skip/xfail guard was found. Assertion inventory: `C:/Temp/av-kit/p4-api-exec-r2-test-assertion-audit.txt`; scan: `C:/Temp/av-kit/p4-api-exec-r2-static-scans.txt`. |
| IR-6 Boundary validation coverage | pass | The every-body-route extra-field oracle remains green, and the corrected empty-ID test asserts download/load 422 envelopes plus no download mutation (`tests/e2e/test_api_tts_models.py:129-147`). The live and committed schemas agree on both `minLength: 1` constraints. |
| IR-7 Deferral and AC-coverage integrity | pass | Exact comparison found all plan ACs in their handoffs: MEU-14 = 9, MEU-15 = 13, MEU-16 = 10. MEU-17–25 exist and remain `pending`; MEU-14–16 remain `ready_for_review`; hub Next remains `/create-plan p5-mcp-server`. Receipt: `C:/Temp/av-kit/p4-api-exec-r2-ac-ssot-audit.txt`. |

#### Documentation Review (DR-1..DR-8)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | pass | Both correction claims were independently reproduced from current code and runtime receipts; no `.git` metadata was assumed. |
| DR-2 Residual old/forbidden terms | pass | API representations still omit forbidden transcript/TTS/cookie fields; the 109-test contract suite remains green. |
| DR-3 Downstream references updated | pass | MEU status, Phase 4 execution-plan binding, and BUILD_PLAN Next are mutually consistent; `meu_status.py render --check` passes. |
| DR-4 Verification robustness | pass | Empty IDs now have direct negative route oracles; both reorder routes have exact input and response-order assertions; OpenAPI drift is checked byte-for-byte. |
| DR-5 Evidence auditability | pass | Every round-2 command used an isolated `C:/Temp/av-kit/p4-api-exec-r2-*` receipt with preserved exit status. |
| DR-6 Cross-reference integrity | pass | The plan, task, three MEU handoffs, rolling review, SSOT binding, and committed/live OpenAPI all identify the same Session 5 delivery. |
| DR-7 Evidence freshness | pass | Reproduced current totals are 109 API/G29 tests and 66 named-core-lock regression tests; OpenAPI, pyright, ruff, and SSOT drift checks all exit 0. |
| DR-8 Completion vs residual risk | pass | The handoffs record both corrections and no known delivered AC remains unproven. The whitespace-only model-ID encoding noted below is explicitly non-blocking under the nearby-mutation rule. |

### Commands and Round-2 Receipts

| Check | Result | Receipt |
|---|---|---|
| Required API + real-wiring suite | `109 passed`, exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-pytest.txt` |
| Named core locks/services | `66 passed`, exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-core-locks.txt` |
| Committed OpenAPI drift | exact match, exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-openapi.txt` |
| OpenAPI model-ID constraints | both `minLength: 1`, exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-openapi-constraints.txt` |
| Pyright API + core | `0 errors, 0 warnings`, exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-pyright.txt` |
| Registered ruff API + core | all checks passed, exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-ruff.txt` |
| Independent empty-ID, download reorder, voices probes | 422/422 canonical envelopes; no model mutation; exact reorder; public voices call delta 1 | `C:/Temp/av-kit/p4-api-exec-r2-runtime-probes.txt` |
| Independent transcript reorder probe | exact fake and response permutation, exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-transcript-reorder-probe.txt` |
| AC/SSOT/BUILD_PLAN audit | 9/13/10 ACs; current/future states and hub Next correct | `C:/Temp/av-kit/p4-api-exec-r2-ac-ssot-audit.txt` |
| SSOT rendered-region drift | 25 MEUs / 8 phases; drift check passed | `C:/Temp/av-kit/p4-api-exec-r2-ssot-render-check.txt` |
| Test assertion-strength inventory | every scoped test enumerated | `C:/Temp/av-kit/p4-api-exec-r2-test-assertion-audit.txt` |
| G36/placeholders/forbidden imports | zero matches in each class | `C:/Temp/av-kit/p4-api-exec-r2-static-scans.txt` |
| Workspace metadata probe | `.git` absent | `C:/Temp/av-kit/p4-api-exec-r2-workspace-probe.txt` |
| Review checker self-test | exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-check-selftest.txt` |
| Approved rolling-frontmatter check | exit 0 | `C:/Temp/av-kit/p4-api-exec-r2-check-review.txt` |

### Residual Risk / Non-blocking Observation

`Field(min_length=1)` rejects the exact empty-string contract defect but does not strip whitespace-only IDs. That is another encoding of the same ID-constraint mutation, so it is recorded as residual risk and is non-blocking under the round-2 nearby-mutation rule.

### Verdict

`approved` — both round-1 findings are independently verified fixed, no new material contract or runtime defect survived verification, and all required/current validation receipts are green. `findings_count: 0`.
