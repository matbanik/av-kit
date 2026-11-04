---
date: "2026-08-19"
project: "p4-rest-api"
meu: "MEU-14"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md"
build_plan_section: "bp04s1"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-19-p3-services-MEU-12-handoff.md"
---

# Handoff: 2026-08-19-p4-rest-api-MEU-14-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-14 — `packages/api` factory, dual Bearer (`AUTH_TOKENS`), `ERROR_ENVELOPE`, request-id, localhost CORS, lifespan spies, `ApiModel(extra="forbid")`, and `CONSOLE_LEVEL_FROM_METHOD` on `ConsoleEvent.level`.
**Build Plan Section**: `docs/build-plan/04-rest-api.md` §factory / Auth / Middleware / Health liveness
**Predecessor**: Session 4 MEU-12/13 services (frozen machines; this MEU only adds `ConsoleEvent.level` + processor mapping)

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-14.1 | integration | `create_app` registers prefix `API_PREFIX`, title `av-kit`, and stores services on `app.state`. Getters in `dependencies.py` match Spec names. | Spec factory | `tests/e2e/test_api_auth.py:test_ac_14_1_factory_prefix_title_and_getters` | ✅ |
| AC-14.2 | integration | **Control `AUTH_TOKENS`.** Observable: HTTP status + `ERROR_ENVELOPE.code`. Chain: `HTTPBearer` → `compare_digest` loop → 401 handler. Negative: missing Bearer on `/health/dependencies` → 401; wrong token → 401; `GET /health` without Bearer → 200 `{status:ok}`. Token string does not appear in response body. | Spec Auth | `tests/e2e/test_api_auth.py:test_ac_14_2_auth_tokens_and_health_exempt` | ✅ |
| AC-14.3 | integration | **Control `ERROR_ENVELOPE`.** Observable: JSON shape on 401/422/500. Chain: handler table → `errors.py`. Negative: raw FastAPI `{"detail":…}` top-level on 401. | Spec Middleware | `tests/e2e/test_api_auth.py:test_ac_14_3_error_envelope_on_401_422_500` | ✅ |
| AC-14.4 | integration | **Control `REQUEST_ID_HEADER`.** Observable: response header equals supplied or is UUID4. Chain: middleware → structlog bind. Negative: header dropped. | Spec Middleware | `tests/e2e/test_api_auth.py:test_ac_14_4_request_id_echo_or_uuid4` | ✅ |
| AC-14.5 | integration | **Control `CORS_ORIGIN_REGEX`.** Observable: `Access-Control-Allow-Origin` on OPTIONS from `http://localhost:5173`. Negative: `https://evil.example` gets no `*`. | Spec CORS; Research-backed FastAPI CORS | `tests/e2e/test_api_auth.py:test_ac_14_5_cors_localhost_not_wildcard` | ✅ |
| AC-14.6 | unit | Factory rejects empty/blank `tokens` with `ValueError` before routes exist. | Research-backed compare_digest | `tests/e2e/test_api_auth.py:test_ac_14_6_factory_rejects_empty_or_blank_tokens` | ✅ |
| AC-14.7 | integration | Lifespan startup calls `recover_stale_processing` once; shutdown calls cancel/stop/unload/dispose (fake spies). | Spec factory; p3 boot | `tests/e2e/test_api_auth.py:test_ac_14_7_lifespan_startup_and_shutdown_spies` | ✅ |
| AC-14.8 | unit | `ApiModel` rejects an unknown field (`extra="forbid"`). Totality across live routes is `BODY_ROUTES` / AC-16.9 (after all routers exist). | Spec Boundary | `tests/e2e/test_api_auth.py:test_ac_14_8_api_model_forbids_extra` | ✅ |
| AC-14.9 | unit | **Control `CONSOLE_LEVEL_FROM_METHOD` (processor).** Observable: `ConsoleEvent.level`. Chain: structlog `method_name` → `HealthService._process` (production processor; no HTTP). Negative: `warning` → `WARNING` (not `INFO`); unknown/omitted/`not-a-level` → `INFO`. HTTP envelope is AC-15.13 (console route is MEU-15). | Spec ConsoleEventOut; F3 | `tests/unit/test_console_level.py:test_ac_14_9_console_level_from_method` | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| `tests/e2e/test_api_auth.py` collect | `ModuleNotFoundError: No module named 'avkit_api.dependencies'` | 9 passed | `tests/e2e/test_api_auth.py:12` |
| `test_ac_14_9_console_level_from_method` | not collected after `-x` on auth import | passed | `tests/unit/test_console_level.py:37` |

Receipt: `C:/Temp/av-kit/fail-to-pass-meu-14-auth.txt`. Green: `C:/Temp/av-kit/pytest-api.txt` (9 passed). Session 4 health regression `ac_13*`: 12 passed.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `uv sync --all-packages` | 0 | `avkit-api==0.1.0`, `fastapi==0.141.1` |
| `uv run python -c "import avkit_api"` | 0 | `PASS: avkit_api import` |
| Red pytest auth+console | 1 | collect `ModuleNotFoundError` |
| Green pytest auth+console | 0 | 9 passed |
| `pyright packages/api/ packages/core/` | 0 | 0 errors, 0 warnings |
| `ruff check packages/api/ packages/core/` | 0 | All checks passed |
| health `ac_13*` regression | 0 | 12 passed |

### Quality Gate Results

```
pyright: 0 errors, 0 warnings
ruff: 0 violations
pytest: 9 passed (MEU-14 targeted)
anti-placeholder: 0 matches
anti-deferral: 0 matches
SCAN_API_LIBS: 0 matches
SCAN_CORE_INFRA: 0 matches
#11a: 0; #11b: 0; #11c: ApiModel only; #11d: 0
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/api/pyproject.toml` | new | 1–24 | workspace package + FastAPI deps |
| `packages/api/src/avkit_api/main.py` | new | 47–82 | `create_app`, CORS, request-id, health router |
| `packages/api/src/avkit_api/auth.py` | new | 15–37 | `compare_digest` over every `AUTH_TOKENS` member |
| `packages/api/src/avkit_api/errors.py` | new | 21–99 | `ERROR_ENVELOPE` + `DOMAIN_HTTP_MAP` |
| `packages/api/src/avkit_api/dependencies.py` | new | 8–35 | Spec getter names |
| `packages/api/src/avkit_api/wiring.py` | new | 23–37 | `AppServices`; `build_services` RuntimeError until MEU-16 |
| `packages/api/src/avkit_api/routes/health.py` | new | 31–60 | liveness + dependencies |
| `packages/core/src/avkit_core/domain/health.py` | modified | 18–32 | `ConsoleEvent.level` |
| `packages/core/src/avkit_core/services/health.py` | modified | 116–117 | `CONSOLE_LEVEL_FROM_METHOD` |
| `tests/e2e/test_api_auth.py` | new | 106–247 | AC-14.1–14.8 |
| `tests/unit/test_console_level.py` | new | 37–56 | AC-14.9 |
| `pyproject.toml` | modified | 12–40 | workspace member + pythonpath/pyright/ruff |

```diff
 class ConsoleEvent:
     timestamp: datetime
+    level: str
```

```diff
+        candidate = method_name.upper()
+        level = candidate if candidate in LOG_LEVEL_WIRES else "INFO"
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | — | — | — | — | — |

### Verdict

`pending` — implementor does not author `approved`.

---

## Corrections Applied (2026-08-19)

_None yet._

**Findings resolved**: 0/0

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Remaining health/console/settings HTTP | planned | MEU-15 | AC-15.10–15.13 |
| `BODY_ROUTES` extra totality | planned | MEU-16 | AC-16.9 |
| `wiring.build_services` composition root | planned | MEU-16 | AC-16.10 |
| Downloads / transcripts / TTS / models routers | planned | MEU-15, MEU-16 | ROUTE_INDEX |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | MEU-14 factory/auth/envelope + console level |
| Submitted for review | 2026-08-19 | cursor-grok-4.6 | Awaits project exec review after MEU-16 |
| H1-6 refresh | 2026-08-19 | cursor-grok-4.6 | Verification plan 288 passed; ready_for_review |
