---
date: "2026-08-26"
project: "p8-conversion-api-mcp"
meu: "MEU-31"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-26-p8-conversion-api-mcp/implementation-plan.md"
build_plan_section: "bp08sREST"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-24-p8-conversion-engine-MEU-30-handoff.md"
---

# Handoff: 2026-08-26-p8-conversion-api-mcp-MEU-31-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-31 — conversion REST `/api/v1/conversions*`, `SettingsPutIn` converter leaves, `format_encode_speed`, `InvalidTimeRangeError`→422, `AppServices.conversion`, GPU lazy GET via `ensure_conversion_gpu` + `GPU_COLD_INIT`. No MCP tool. No Convert GUI.
**Build Plan Section**: `docs/build-plan/08-video-conversion.md` §REST
**Predecessor**: MEU-30 conversion engine

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-31.1 | integration | POST compress 201 `{ items }`; extra `nope` 422; Bearer required | Spec 445, 461–463 | `test_api_conversions.py` AC-31.1 | ✅ |
| AC-31.2 | integration | GET list 200 `{ items, processor }` | Spec 446 | `test_api_conversions.py` AC-31.2 | ✅ |
| AC-31.3 | integration | Sequential `GPU_LAZY_GET`: first GET detects once; second GET cache-only | Spec 250, 447 | `test_api_conversions.py` AC-31.3 | ✅ |
| AC-31.4 | integration | POST `/gpu/refresh` always re-probes | Spec 448 | `test_api_conversions.py` AC-31.4 | ✅ |
| AC-31.5 | integration | POST start 202; Processing → 409 envelope | Spec 449 | `test_api_conversions.py` AC-31.5 | ✅ |
| AC-31.6 | integration | POST pause/resume/cancel 202 | Spec 450–452 | `test_api_conversions.py` AC-31.6 | ✅ |
| AC-31.7 | integration | PUT reorder `{ job_ids }` 200 `{ items }`; extra key 422 | Spec 453 | `test_api_conversions.py` AC-31.7 | ✅ |
| AC-31.8 | integration | DELETE collection 204; `clear_queue`; files stay | Spec 454 | `test_api_conversions.py` AC-31.8 | ✅ |
| AC-31.9 | integration | GET `{id}` 200; unknown 404 envelope | Spec 456 | `test_api_conversions.py` AC-31.9 | ✅ |
| AC-31.10 | integration | POST reset 200 from Failed; else 409 | Spec 457 | `test_api_conversions.py` AC-31.10 | ✅ |
| AC-31.11 | integration | DELETE `{id}` 204; `remove`; files stay | Spec 458 | `test_api_conversions.py` AC-31.11 | ✅ |
| AC-31.12 | integration | Relative / missing / directory path and unknown preset → 422 before add | Spec 436, 467 | `test_api_conversions.py` AC-31.12 | ✅ |
| AC-31.13 | integration | Discriminated union: cut/extract required fields; cut+`preset` 422; inverted range 422 | Spec 461–465 | `test_api_conversions.py` AC-31.13 | ✅ |
| AC-31.14 | unit | `format_encode_speed(1.25)==1.25x`; not `format_speed` | Spec 473; Session 13 | `test_api_conversions.py` AC-31.14 | ✅ |
| AC-31.15 | integration | `ConversionJobOut` Spec fields; wire kind/preset/audio; no `FORBIDDEN_RESPONSE_KEYS` | Spec 471–475 | `test_api_conversions.py` AC-31.15 | ✅ |
| AC-31.16 | integration | GET/PUT `/settings/converter` 200 `CONVERTER_KEYS`; unknown leaf 422; unknown ns 404 | Spec 477–487 | `test_api_conversions.py` AC-31.16 | ✅ |
| AC-31.17 | integration | OpenAPI `CONVERT_ROUTES`; `STATIC_BEFORE_ID`; unauth 401; console `convert` | Spec 425, 488; G8 | `test_api_conversions.py` AC-31.17 | ✅ |
| AC-31.18 | integration | `AppServices.conversion`; GET list 200 tmp SQLite; lifespan conversion cancel + AC-14.7 download `cancel_calls==1`; `InvalidTimeRangeError` 422 | G29; Local Canon | `test_api_conversions.py` AC-31.18 | ✅ |
| AC-31.19 | integration | Compress `COMPRESS_OVERRIDE_FIELDS` forwarded on `ConversionAddSpec` | Spec 461–463 | `test_api_conversions.py` AC-31.19 | ✅ |
| AC-31.20 | integration | Cut `copy_mode=reencode` → Reencode; omitted → FastCopy | Spec 464 | `test_api_conversions.py` AC-31.20 | ✅ |
| AC-31.21 | integration | Extract `stream_index=2` forwarded | Spec 465 | `test_api_conversions.py` AC-31.21 | ✅ |
| AC-31.22 | unit | `GPU_COLD_ORACLE` on `ensure_conversion_gpu`; GET spy; no Barrier inside `detect_gpu` | `GPU_COLD_INIT`; Local Canon | `test_api_conversions.py` AC-31.22 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-31.1–AC-31.22 | `PASS: RED_ORACLE py MEU-31 AC-31 count=22`; 22 failed | 22 conversion tests passed inside 108 passed green suite | `C:/Temp/av-kit/fail-to-pass-meu-31-py.txt`; `C:/Temp/av-kit/pytest-meu-31-green.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-red-oracle.ps1 -Kind py -Meu 31` | 0 | `PASS: RED_ORACLE py MEU-31 AC-31 count=22` |
| `uv run pytest tests/e2e/test_api_conversions.py tests/e2e/test_api_openapi.py tests/e2e/test_api_auth.py tests/e2e/test_api_health_settings.py tests/e2e/test_api_downloads.py tests/integration/test_api_wiring.py -x` | 0 | 108 passed |
| `uv run ruff check packages/api tests/e2e/test_api_conversions.py tests/e2e/test_api_openapi.py` | 0 | All checks passed |
| `uv run pyright packages/api` | 0 | 0 errors, 0 warnings |
| `uv run python tools/export_openapi.py --check openapi.committed.json` | 0 | after `-o` regen |

### Quality Gate Results

```
pytest: 108 passed (C:/Temp/av-kit/pytest-meu-31-green.txt)
H1-2 e2e+wiring: 152 passed (C:/Temp/av-kit/pytest-p8-api-mcp-h1.txt)
ruff: All checks passed (C:/Temp/av-kit/ruff-meu-31.txt)
pyright: 0 errors (C:/Temp/av-kit/pyright-meu-31.txt)
openapi --check: pass (C:/Temp/av-kit/openapi-check.txt)
anti-placeholder: 0 matches
G36 skip/only: 0 matches
RED_ORACLE py MEU-31: PASS (count=22)
SSOT: MEU-31 ready_for_review; hub Next `/create-plan p8-conversion-gui`
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/api/src/avkit_api/routes/conversions.py` | new | router | 13 routes; `ensure_conversion_gpu` lock + double-check |
| `packages/api/src/avkit_api/schemas/conversions.py` | new | In/Out | discriminated create union; `GPUCapabilitiesOut` |
| `packages/api/src/avkit_api/schemas/settings.py` | modified | SettingsPutIn | `default_preset`, `skip_existing`, `gpu_preference` |
| `packages/api/src/avkit_api/formatters.py` | modified | encode speed | `format_encode_speed`; conversion enum→wire |
| `packages/api/src/avkit_api/errors.py` | modified | map | `InvalidTimeRangeError` → 422 |
| `packages/api/src/avkit_api/wiring.py` | modified | AppServices | required `conversion`; `ConversionService` in `build_services` |
| `packages/api/src/avkit_api/main.py` | modified | factory | include conversions router; lifespan `conversion.cancel_processing` |
| `packages/api/src/avkit_api/dependencies.py` | modified | getter | `get_conversion_service` |
| `packages/core/src/avkit_core/domain/wire.py` | modified | maps | kind/preset/copy/audio-encode/gpu-pref wires |
| `tools/export_openapi.py` | modified | dummy | `conversion=` lifecycle |
| `openapi.committed.json` | modified | G8 | `ROUTE_COUNT_AFTER` |
| `tests/e2e/test_api_conversions.py` | new | AC-31.* | Red/Green contract |
| `tests/e2e/test_api_openapi.py` | modified | census | `len(ROUTE_INDEX)==61` |
| `tests/e2e/api_fakes.py` + APPSERVICES_SITES | modified | constructors | `conversion=` (auth uses a separate spy so AC-14.7 stays 1) |

```diff
 def ensure_conversion_gpu(conversion: Any) -> GPUCapabilities:
     cached = conversion.get_gpu()
     if cached is not None:
         return cached
     with _gpu_ensure_lock:
         cached = conversion.get_gpu()
         if cached is not None:
             return cached
         return conversion.detect_gpu()
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

## Corrections Applied (2026-08-26)

**Findings resolved**: 1/1 (F1 from exec r1)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | Empty reorder `{ job_ids: [] }` → 200 | `ConversionReorderIn.job_ids` `Field(min_length=1)` | AC-31.7 422 and `reorder_calls==0`; OpenAPI `minItems: 1` |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Downloader → Convert handoff | out-of-scope | — | Spec 08 lines 535–541; not MEU-33 |
| Convert GUI / NavRail `/convert` | out-of-scope | MEU-33 | grouping Session 15 |
| `avkit_convert` MCP | next row | MEU-32 | this plan WP-32 |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-26 | cursor-grok | MEU-31 Red→Green + handoff |
| H1 refresh | 2026-08-26 | cursor-grok | H1-2 152 passed; SSOT ready_for_review; OpenAPI check |
| F1 empty reorder | 2026-08-26 | cursor-grok | `job_ids` min_length=1; AC-31.7 422 + no service call |
