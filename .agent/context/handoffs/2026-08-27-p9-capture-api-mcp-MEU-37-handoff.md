---
date: "2026-08-27"
project: "p9-capture-api-mcp"
meu: "MEU-37"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-27-p9-capture-api-mcp/implementation-plan.md"
build_plan_section: "docs/build-plan/09-screenshot-capture.md §REST"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-26-p9-capture-engine-MEU-36-handoff.md"
---

# Handoff: 2026-08-27-p9-capture-api-mcp-MEU-37-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-37 — capture REST `/api/v1/captures*`, `SettingsPutIn` `CAPTURE_KEYS`, `DOMAIN_HTTP_CAPTURE` (422 path/annotation, 503 grab/platform), `AppServices.capture`, `list_requests` + repo `list()`, OpenAPI `ROUTE_COUNT_AFTER` 71. Not a queue (`{ items }` only). No MCP tool. No Capture GUI. Session 8c stays human-gated.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §REST
**Predecessor**: MEU-36 capture service/engine

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-37.1 | integration | GET `/captures` 200 `{ items }`; no `processor`; dual Bearer; `list_shots` | Spec 390 | `test_api_captures.py` AC-37.1 | ✅ |
| AC-37.2 | integration | POST `mode=register` 201 `{ item }`; `REGISTER_SOURCE_WIRES` → `CaptureSource`; extra `nope` 422 | Spec 391, 407 | `test_api_captures.py` AC-37.2 | ✅ |
| AC-37.3 | integration | POST fullscreen 201; `CaptureFailedError`/`CaptureNotSupportedError` → 503 | Spec 408; 04-rest-api.md 99 | `test_api_captures.py` AC-37.3 | ✅ |
| AC-37.4 | integration | POST region edge ≥ 8 → 201 `BBox`; width 7 → 422 | Spec 409 | `test_api_captures.py` AC-37.4 | ✅ |
| AC-37.5 | integration | GET `/requests` expires then `{ items }`; `?status=pending` lowercase In, Pascal Out; unknown 422 | Spec 171, 392, 357 | `test_api_captures.py` AC-37.5 | ✅ |
| AC-37.6 | integration | POST `/requests` empty 201; extra 422; second Pending 409 `CaptureRequestConflictError` | Spec 257, 393 | `test_api_captures.py` AC-37.6 | ✅ |
| AC-37.7 | integration | POST complete `{ path }` 200 + `shot_id`; extra 422; unknown UUID + valid path 404, `shot_inserts==0` | Spec 394; RULE-2 | `test_api_captures.py` AC-37.7 | ✅ |
| AC-37.8 | integration | POST cancel 200; empty/`EmptyIn` body | Spec 395 | `test_api_captures.py` AC-37.8 | ✅ |
| AC-37.9 | integration | GET shot metadata 200 path strings, no PNG bytes; unknown 404 | Spec 396 | `test_api_captures.py` AC-37.9 | ✅ |
| AC-37.10 | integration | GET image `variant=original` 200 MIME; unauth 401; missing annotated 404; oversize 413; default original | Spec 397, 514 | `test_api_captures.py` AC-37.10 | ✅ |
| AC-37.11 | integration | POST annotate 200; empty array ok; extra 422; unknown color 422 | Spec 398, 272 | `test_api_captures.py` AC-37.11 | ✅ |
| AC-37.12 | integration | DELETE 204; fake `remove`; unknown 404 | Spec 399 | `test_api_captures.py` AC-37.12 | ✅ |
| AC-37.13 | integration | GET/PUT `/settings/capture` `CAPTURE_KEYS`; unknown leaf 422; unknown ns 404 | Spec 417–427 | `test_api_captures.py` AC-37.13 | ✅ |
| AC-37.14 | integration | OpenAPI `CAPTURE_ROUTES`; static `/requests` before `/{id}`; unauth 401; console module `capture`; `ROUTE_INDEX` 71 | Spec 386, 428, 430; G8 | `test_api_captures.py` AC-37.14; `test_api_openapi.py` len==71 | ✅ |
| AC-37.15 | integration | `build_services.capture`; tmp SQLite GET 200; download `cancel_calls==1`; conversion cancel; no capture cancel; `DOMAIN_HTTP_CAPTURE`; all `APPSERVICES_SITES` `capture=` | G29; Local Canon lifespan | `test_api_captures.py` AC-37.15 | ✅ |
| AC-37.16 | integration | Discriminated union: register sans path / fullscreen+`x` / region sans height → 422 | Spec 401–411 | `test_api_captures.py` AC-37.16 | ✅ |
| AC-37.17 | integration | Shot Out fields + Pascal `source`; request Out + Pascal `status`; no `FORBIDDEN_RESPONSE_KEYS` | Spec 413–415 | `test_api_captures.py` AC-37.17 | ✅ |
| AC-37.18 | integration | Port + SQLAlchemy `list()`; `CaptureService.list_requests`; engine fakes implement `list` | Spec 392; G29 | `test_api_captures.py` AC-37.18 | ✅ |
| AC-37.19 | integration | `{id}: str`; `not-a-uuid` GET/DELETE/complete/cancel/image/annotate → 404 `NotFoundError`, not 422/500 | Local Canon downloads; Spec 310 | `test_api_captures.py` AC-37.19 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-37.1–AC-37.19 | `PASS: RED_ORACLE py MEU-37 AC-37 count=19`; Red pytest non-zero | 19 capture tests passed inside 158 passed green suite | `C:/Temp/av-kit/fail-to-pass-meu-37-py.txt`; `C:/Temp/av-kit/pytest-meu-37-green.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-red-oracle.ps1 -Kind py -Meu 37` | 0 | `PASS: RED_ORACLE py MEU-37 AC-37 count=19` |
| row 2 pytest (captures + openapi + auth + health + conversions + wiring + capture unit) | 0 | 158 passed (`C:/Temp/av-kit/pytest-meu-37-green.txt`) |
| `uv run ruff check packages/api tests/e2e/test_api_captures.py tests/e2e/test_api_openapi.py` | 0 | All checks passed |
| `uv run pyright packages/api` | 0 | 0 errors, 0 warnings |
| `uv run python tools/export_openapi.py --check openapi.committed.json` | 0 | after `-o` regen (`C:/Temp/av-kit/openapi-check-meu-37.txt`) |
| anti-placeholder `packages/api/src` | 0 | 0 matches |
| G36 skip/xfail on `test_api_captures.py` | 0 | 0 matches |

### Quality Gate Results

```
pytest green: 158 passed (C:/Temp/av-kit/pytest-meu-37-green.txt)
pytest gate: 101 passed (C:/Temp/av-kit/pytest-meu-37-gate.txt)
ruff: All checks passed (C:/Temp/av-kit/ruff-meu-37.txt)
pyright: 0 errors (C:/Temp/av-kit/pyright-meu-37.txt)
openapi --check: pass (C:/Temp/av-kit/openapi-check-meu-37.txt)
anti-placeholder: 0 matches
G36 skip/only: 0 matches
RED_ORACLE py MEU-37: PASS (count=19)
IMAGE_MAX_BYTES: 15728640 (captures.py:42); IMAGE_MAX_BYTES_HUMAN "15 MiB" remains named-set only
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/api/src/avkit_api/routes/captures.py` | new | router | 10 routes; `_REQUESTS_PATH` before `/{id}`; `IMAGE_MAX_BYTES` 15728640; path `id: str` |
| `packages/api/src/avkit_api/schemas/captures.py` | new | In/Out | discriminated `mode` union `extra=forbid`; arrow `from`/`to` aliases |
| `packages/api/src/avkit_api/schemas/settings.py` | modified | SettingsPutIn | `inbox_dir`, `hotkey`, `copy_to_clipboard`, `close_to_tray` |
| `packages/api/src/avkit_api/errors.py` | modified | map | InboxPath/AnnotationValidation 422; CaptureFailed/NotSupported 503 |
| `packages/api/src/avkit_api/wiring.py` | modified | AppServices | required `capture`; `CaptureAdapter` + `CaptureService` |
| `packages/api/src/avkit_api/main.py` | modified | factory | include captures router; **no** lifespan capture cancel |
| `packages/api/src/avkit_api/dependencies.py` | modified | getter | `get_capture_service` |
| `packages/core/src/avkit_core/domain/wire.py` | modified | maps | `REGISTER_SOURCE_WIRE_MAP`; `REQUEST_STATUS_QUERY_MAP` |
| `packages/core/src/avkit_core/ports/storage.py` | modified | port | `CaptureRequestRepository.list()` |
| `packages/core/src/avkit_core/services/capture.py` | modified | service | `list_requests` expire-then-list; no `mkdir` |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | modified | repo | SQLAlchemy request `list()` |
| `tools/export_openapi.py` | modified | dummy | `capture=` lifecycle |
| `openapi.committed.json` | modified | G8 | `ROUTE_COUNT_AFTER` 71 |
| `tests/e2e/test_api_captures.py` | new | AC-37.* | Red/Green contract |
| `tests/e2e/test_api_openapi.py` | modified | census | `len(ROUTE_INDEX)==71` |
| `tests/e2e/test_api_conversions.py` + remaining `APPSERVICES_SITES` | modified | constructors | `capture=` keyword |

```diff
 _REQUESTS_PATH = "/requests"
 @router.get(_REQUESTS_PATH, response_model=CaptureRequestListOut)
 def list_capture_requests(...):
     mapped = None if status is None else REQUEST_STATUS_QUERY_MAP[status]
     rows = capture.list_requests(status=mapped)
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/execution-critical-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | pending independent review | — | — | open |

### Verdict

`pending` — implementer does not author the verdict

## Corrections Applied (2026-08-27)

**Findings resolved**: Green-phase contract mismatches (not reviewer findings)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | AC-37.14 `requests_pos < id_pos` hit docstring/`complete` `/{id}` first | `_REQUESTS_PATH = "/requests"`; docstring without `/{id}` | AC-37.14 passed |
| 2 | AC-37.14 FakeHealth `console_snapshot` arity | `after_seq` default 0, filter `seq > after_seq` | console 200 + module `capture` |
| 3 | AC-37.15 conversions site used `"capture":` dict key | explicit `capture=` on `AppServices(...)` | all `APPSERVICES_SITES` pass |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| `avkit_capture` MCP compound tool | next row | MEU-38 | this plan WP-38 |
| Capture GUI / NavRail `/captures` | out-of-scope | MEU-39 | grouping Session 18 |
| Session 8c GUI console polish | human-gated | MEU-27 | grouping Session 8c stays ⬜ pending |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| H1 refresh | 2026-08-27 | cursor-grok | H1-2 217 pytest + 214 vitest; SSOT ready_for_review; OpenAPI check |
| Exec r1 corrections | 2026-08-27 | cursor-grok | F1 variant-path MIME; F2 real SQLite list/expire; 217 pytest |
