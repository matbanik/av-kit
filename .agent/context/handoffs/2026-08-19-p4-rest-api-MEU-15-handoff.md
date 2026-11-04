---
date: "2026-08-19"
project: "p4-rest-api"
meu: "MEU-15"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md"
build_plan_section: "bp04s2"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-19-p4-rest-api-MEU-14-handoff.md"
---

# Handoff: 2026-08-19-p4-rest-api-MEU-15-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-15 — downloads/SABR/cookies/`START_IF_PROCESSING`, formatters, settings namespace 404/422/`SETTINGS_UI_API_KEYS`, remaining health console/deps/metrics, HTTP `CONSOLE_LEVEL_FROM_METHOD`.
**Build Plan Section**: `docs/build-plan/04-rest-api.md` §Downloads / Settings / Health
**Predecessor**: MEU-14 factory/auth

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-15.1 | integration | `POST /downloads` 201 `{ items }`; quality `1080p` round-trips. Extra field → 422. Missing Bearer → 401. | Spec Testing | `tests/e2e/test_api_downloads.py:test_ac_15_1_create_download_round_trip_and_boundary` | ✅ |
| AC-15.2 | integration | `GET /downloads` 200 `LIST_ENVELOPE`. No item `status=Paused`. | Spec DownloadJobOut | `tests/e2e/test_api_downloads.py:test_ac_15_2_list_envelope_has_no_paused_status` | ✅ |
| AC-15.3 | integration | **Control `START_IF_PROCESSING`.** Observable: 409 envelope when fake processor is Processing. Chain: route → `get_processor_state` → return 409 **without** calling `start_processing`. | Spec 409 | `tests/e2e/test_api_downloads.py:test_ac_15_3_start_if_processing_does_not_call_start` | ✅ |
| AC-15.4 | integration | pause/resume/cancel/stop → 202; stop calls `cancel_processing`. resume while not Paused → 409. | Spec | `tests/e2e/test_api_downloads.py:test_ac_15_4_pause_resume_cancel_stop` | ✅ |
| AC-15.5 | integration | reset non-Failed → 409; unknown id → 404; DELETE `{id}` 204; DELETE collection 204 (archive stays). | Spec | `tests/e2e/test_api_downloads.py:test_ac_15_5_reset_delete_and_clear_keep_archive` | ✅ |
| AC-15.6 | integration | SABR get does not call `check_sabr`. check/force/clear return `SABRStatusOut` via `SABR_WIRE_MAP`. | Spec | `tests/e2e/test_api_downloads.py:test_ac_15_6_sabr_get_does_not_check` | ✅ |
| AC-15.7 | integration | cookies/test → `COOKIE_TEST_OUT`; `CookieTestError` → 422; no cookie bytes in body. | Spec; RULE-2 | `tests/e2e/test_api_downloads.py:test_ac_15_7_cookie_test_envelope` | ✅ |
| AC-15.8 | integration | apply-defaults → 200 `{ updated: int }`. Valid reorder forwards exact `job_ids` and returns that permutation. | Spec; exec-r1 F2 | `tests/e2e/test_api_downloads.py:test_ac_15_8_apply_defaults`; `test_ac_15_8b_reorder_forwards_job_ids` | ✅ |
| AC-15.9 | unit | `SPEED_FORMAT` / `ETA_FORMAT` / `ISO_Z` pure functions. | Spec | `tests/e2e/test_api_downloads.py:test_ac_15_9_speed_eta_iso_formatters` | ✅ |
| AC-15.10 | integration | **Control settings boundary.** unknown namespace 404; rail/extra/unknown key 422; invalid mapping commit count 0. | Spec; p3 F2 | `tests/e2e/test_api_health_settings.py:test_ac_15_10_settings_boundary` | ✅ |
| AC-15.11 | integration | GET namespace returns full defaults-filled object. | Spec | `tests/e2e/test_api_health_settings.py:test_ac_15_11_get_namespace_defaults` | ✅ |
| AC-15.12 | integration | health/dependencies auth + shape; console `after_seq`; startup-metrics 204. | Spec | `tests/e2e/test_api_health_settings.py:test_ac_15_12_health_deps_console_metrics` | ✅ |
| AC-15.13 | integration | **Control `CONSOLE_LEVEL_FROM_METHOD` (HTTP).** warning is not INFO; unknown method is INFO. | Spec ConsoleEventOut; F3 | `tests/e2e/test_api_health_settings.py:test_ac_15_13_http_console_level` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| `test_api_downloads.py` collect | `ModuleNotFoundError: avkit_api.formatters` | 9 passed | `tests/e2e/test_api_downloads.py:12` |
| `test_ac_15_10_settings_boundary` | `assert 404 == 422` (no settings route) | passed | `tests/e2e/test_api_health_settings.py:131` |

Receipts: `C:/Temp/av-kit/fail-to-pass-meu-15-downloads.txt`, `fail-to-pass-meu-15-settings.txt`. Green: `C:/Temp/av-kit/pytest-api.txt` (21 passed).

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| Red downloads | 2 | formatters missing |
| Green downloads + auth | 0 | 17 passed |
| Red settings | 1 | 404 vs 422 |
| Green auth+downloads+settings | 0 | 21 passed |
| pyright packages/api | 0 | 0 errors |
| ruff packages/api | 0 | All checks passed |

### Quality Gate Results

```
pyright: 0 errors, 0 warnings
ruff: 0 violations
pytest: 21 passed
anti-placeholder: 0 matches
```

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `avkit_api/formatters.py` | new | SPEED/ETA/ISO/SABR/quality wires |
| `avkit_api/routes/downloads.py` | new | STATIC_BEFORE_ID + START_IF_PROCESSING |
| `avkit_api/routes/settings.py` | new | namespace 404 then set_namespace |
| `avkit_api/routes/health.py` | modified | console + startup-metrics |
| `avkit_api/schemas/{downloads,settings,health}.py` | new/modified | ApiModel bodies |
| `avkit_api/main.py` | modified | include downloads + settings |
| `tests/e2e/test_api_downloads.py` | new | AC-15.1–15.9 |
| `tests/e2e/test_api_health_settings.py` | new | AC-15.10–15.13 |

```diff
+    if download.get_processor_state().state is QueueProcessorState.Processing:
+        raise ConflictError("download processor is already Processing")
+    download.start_processing()
```

---

## Codex Validation Report

_Left blank for reviewer agent._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence
3. Run Commands Executed
4. Run Quality Gate independently
5. Record findings

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | — | — | — | — | — |

### Verdict

`pending` — implementor does not author `approved`.

---

## Corrections Applied (2026-08-19)

| Finding | Change | Evidence |
|---------|--------|----------|
| F2 download reorder | Local `FakeDownload.reorder_queue` now permutes the queue and records `last_reorder`. `test_ac_15_8b_reorder_forwards_job_ids` asserts the swapped permutation on both the fake and the list envelope. | `tests/e2e/test_api_downloads.py:313` |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Transcripts / TTS / models / OpenAPI / BODY_ROUTES | planned | MEU-16 | AC-16.* |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | MEU-15 downloads/settings/health |
| H1-6 refresh | 2026-08-19 | cursor-grok-4.6 | Verification plan 288 passed; ready_for_review |
| Exec-r1 corrections | 2026-08-19 | cursor-grok-4.6 | F2 download reorder oracle |
