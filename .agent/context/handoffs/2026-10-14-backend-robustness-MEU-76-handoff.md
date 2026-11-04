---
date: "2026-10-15"
project: "2026-10-14-backend-robustness"
meu: "MEU-76"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md"
build_plan_section: "bp04"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: "none"
---

# Handoff: 2026-10-14-backend-robustness-MEU-76-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-76 — `api-error-surface`.
- `CORS_SAFE_500`: `request_id_middleware` (main.py) catches a route exception and returns `internal_error_response(request_id)` (errors.py, new). The response is a 500 with the masked envelope, `details.request_id` and `X-Request-ID`. Because the middleware runs inside `CORSMiddleware`, an allowed origin gets `access-control-allow-origin`. The `Exception` handler stays as the backstop and returns the same response.
- `ERROR_EVENT`: one `api.unhandled_error` event on `structlog.get_logger(module="api")` per failing request. Its fields are `request_id`, `route`, `method`, `error` and `exc_info=True`. It comes from the middleware's `except`, from the backstop, or from the `DomainError` handler when an unmapped `DomainError` becomes a 500. Mapped statuses, including the 503s, are not logged.
- `CONSOLE_FIELDS_NEW`: `CONSOLE_FIELDS = ("job_id", "error", "request_id", "route")`.
- `EXTRACT_STATUS`: `ExtractError(DomainError)` maps to 422. It is raised only at the three `YouTubeAdapter._run_extract` sites, with the messages they raised before. `download()` keeps plain `DomainError`.
- `GUI_ERROR_TEXT`: `apiFetch` shows `Internal server error (request id <id>)` for an `internal_error` envelope that has a non-empty `request_id`.
- `CENSUS_SIGNATURE`: `avkit_download.add` and `avkit_transcript.add` now use `BOT_WALL = /confirm you.re not a bot/i`. `avkit_capture.capture` keeps `MASKED_500`.
- `TEST_AMENDMENTS` TA-1 was applied exactly: `DOMAIN_ERROR_TYPE_NAMES` gains `"ExtractError"` (`tests/unit/test_domain.py`, `# TA-1 (Session 33, MEU-76)`).

**Build Plan Section**: `docs/build-plan/04-rest-api.md` §Unhandled errors (residual) (04:427-439, registry 4.4)
**Predecessor**: none (first MEU of Session 33). MEU-78 and MEU-77 share no product file with this MEU.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-76.1 | contract | `CORS_SAFE_500`: a `RuntimeError("boom secret")` from `GET /api/v1/health/dependencies` with an allowed `Origin` returns 500 with that origin in `access-control-allow-origin`, `X-Request-ID` set, and the exact masked body. A rejected origin gets no CORS header. Neither body contains `boom secret` or `Traceback`. | Spec 04:436 | `tests/e2e/test_api_error_surface.py:67` `test_ac_76_1_unhandled_error_is_cors_safe_masked_500`, `:86` `…_rejected_origin_gets_no_cors_header_neg` | ✅ |
| AC-76.2 | contract | Exactly one `api.unhandled_error` event, with `request_id` equal to the header, `route`, `method`, `error == "RuntimeError: boom secret"` and `exc_info`. A 404 and a 422 emit none. | Spec 04:435 | `test_api_error_surface.py:96` `test_ac_76_2_unhandled_error_emits_one_event`, `:110` `…_not_found_and_request_validation_emit_no_event_neg` | ✅ |
| AC-76.3 | unit | The Console text carries ` request_id=` and ` route=` after `error=`, in `CONSOLE_FIELDS` order. A record without those keys renders as before. | Spec 04:435 | `tests/unit/test_console_level.py:67` `test_ac_76_3_console_shows_request_id_and_route`, `:88` `…_record_without_the_keys_renders_as_today_neg` | ✅ |
| AC-76.4 | contract | An unmapped `DomainError("x")` returns the masked 500 and emits one event (`"DomainError: x"`). A mapped `FFmpegNotFoundError` returns a masked 503 and emits no event. | Spec 04:435 | `test_api_error_surface.py:120` `test_ac_76_4_unmapped_domain_error_is_masked_and_logged`, `:137` `…_mapped_503_is_masked_and_not_logged_neg` | ✅ |
| AC-76.5 | unit | `ExtractError` subclasses `DomainError`, `DOMAIN_HTTP_MAP[ExtractError] == 422`, and a route that raises it returns 422 `{"code": "ExtractError", "message": "yt-dlp says no"}`. It does not subclass `ValidationError`. | Spec 04:437 | `test_api_error_surface.py:147` `test_ac_76_5_extract_error_maps_to_422`, `:158` `…_is_not_a_validation_error_neg` | ✅ |
| AC-76.6 | integration | Through the public `extract_info`, `_run_extract` raises `ExtractError` in three cases: a non-age `DownloadError` (message and `__cause__` preserved), an `OSError` (`"yt-dlp IO failed"`), and a non-dict info (`"yt-dlp returned no info"`). The age gate still raises `AgeRestrictedError`, and a failing `download()` raises a plain `DomainError`. | Spec 04:437 | `tests/integration/test_youtube_adapter.py:692` `test_ac_76_6_extract_failures_raise_extract_error`, `:716` `…_age_gate_and_media_download_keep_their_types_neg` | ✅ |
| AC-76.7 | contract | The setup is a production `DownloadService` and `TranscriptService` over a temp SQLite, with a coordinator fake that raises `ExtractError(<bot wall>)`. Download add and transcript add then both return 422 `ExtractError` with the bot-wall message, never `internal_error` and never an event. | Spec 04:437-438 | `test_api_error_surface.py:218` `test_ac_76_7_bot_wall_on_add_is_extract_error_422` | ✅ |
| AC-76.8 | unit | A 500 `internal_error` with `request_id: "rid-1"` gives the message `Internal server error (request id rid-1)`. Without a request id the message stays as is, and a 422 keeps its envelope message. | Spec 04:436 | `ui/tests/unit/api-fetch.test.ts:127` `AC-76.8 a 500 internal_error names its request id`, `:139` `AC-76.8 [neg] …` | ✅ |
| AC-76.9 | unit | The add signatures match `ExtractError: ERROR: [youtube] x: Sign in to confirm you're not a bot` with either `'` or `’`. They do not match a bare `internal_error`, and capture still does. | Local Canon census.ts | `mcp-server/tests/audit/census-signature.test.ts:14`, `:21` `AC-76.9 [neg] …` | ✅ |

### Other plan AC references (not owned by MEU-76)

| AC | Owner | Status in MEU-76 |
|----|-------|------------------|
| AC-78.x | MEU-78 handoff | ⏳ rows 5–7 |
| AC-77.x | MEU-77 handoff | ⏳ rows 8–11 |
| AC-4.10 | existing domain suite | passes with TA-1 applied, and no other assertion changed |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (snippet) | Green Output | File:Line |
|------|----------------------|--------------|-----------|
| pytest AC-76.1 | `assert None == 'http://localhost:5173'` (`access-control-allow-origin` absent on the 500) | pass | `test_api_error_surface.py:67` |
| pytest AC-76.2 | `AssertionError: [] / assert 0 == 1` (no event) | pass | `test_api_error_surface.py:96` |
| pytest AC-76.3 | `- … request_id=rid-1 route=/api/v1/health/dependencies` / `+ Error: boom` | pass | `test_console_level.py:67` |
| pytest AC-76.4 | `assert 0 == 1` (no event for the unmapped 500) | pass | `test_api_error_surface.py:120` |
| pytest AC-76.5 (both), AC-76.6, AC-76.7 | `AssertionError: avkit_core.domain.errors.ExtractError is missing` (`PY_SYMBOLS` presence assertion) | pass | `test_api_error_surface.py:147,158,218`; `test_youtube_adapter.py:692` |
| Vitest AC-76.8 | `expected ApiError: Internal server error … to match object { …message: 'Internal server error (request id rid-1)' }` | pass | `api-fetch.test.ts:127` |
| MCP Vitest AC-76.9 (both) | `avkit_download.add straight apostrophe: expected false to be true`; `[neg]` `avkit_download.add: expected true to be false` | pass | `census-signature.test.ts:14,21` |

The `_neg` / `[neg]` tests that do not depend on a new symbol passed at Red. Before any test ran, red-guard confirmed the 7 MEU-76 product files were unchanged versus `baseline.sha`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s33-row2-red76", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check red76", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 2: MEU-76 Red over AC-76.1-76.9 (pytest, ui Vitest, MCP Vitest); red-guard first", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ddd11171ceb3ce307a6a735a5b77094b7d456d39 plus MEU-76 test edits only; red-guard: 7 MEU-76 product files unchanged vs baseline.sha", "output": "pytest failed 8, passed 24 | vitest failed 1, passed 3 | mcp failed 2 | PASS red76 (RED_RULE)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-row3-green76", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check green76", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 3: MEU-76 Green over AC-76.1-76.9 plus TA-1 (pytest MEU-76 files and test_domain.py, ui Vitest, MCP Vitest)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ddd11171ceb3ce307a6a735a5b77094b7d456d39 plus MEU-76 test and product edits and TA-1", "output": "PASS green pytest MEU-76: passed 83 | PASS green vitest MEU-76: passed 4 | PASS green mcp MEU-76: passed 2 | PASS green76", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-row4-gate76", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate76", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 4: MEU-76 targeted gate (pyright, ruff, ui typecheck and lint, mcp typecheck, openapi --check, pytest tests/, ui Vitest, MCP Vitest, source audit, product snapshot)", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "MEU-76 final working tree (baseline ddd1117 + MEU-76 diff + TA-1)", "output": "py-types, py-lint (All checks passed!), ui-types, ui-lint, mcp-types, openapi exit 0 | PASS suite pytest: passed 668 | PASS suite vitest: passed 802 | PASS suite mcp: passed 413 | source-audit rg exit 1 (no hits) | PASS snapshot of 25 product files | PASS gate76", "fresh": true}
```

The first `green76` run failed on AC-76.2 alone, with `route == '/health/dependencies'`. In FastAPI 0.141 (Starlette 1.6), `include_router` wraps the router in an `_IncludedRouter`. The matched `APIRoute.path_format` is therefore relative to the include prefix, and `root_path` stays empty. `_route` (errors.py) now recovers the prefix from the route's own `path_regex`: it is the part of the URL path before the suffix that the regex matches. A probe of `/api/v1/transcripts/abc` logged `/api/v1/transcripts/{id}`.

The first `gate76` run failed two steps:
- **py-lint:** two E501 lines in the new tests. They were wrapped, and the assertion text is unchanged.
- **pytest:** AC-24.10 and AC-25.10 failed because the fresh worktree had no gitignored packaging outputs. The environment was provisioned (walkthrough §MEU-76 Gate), and no test or product file changed.

The rerun above is the gate of record. The authoritative full gate is `WINDOWS_GATE` (H1-3).

Final evidence on the whole Session 33 tree (walkthrough §Audit, §Windows gate), rerun after the R1 F1 correction and the A-14 plan rewording: the H1-2 MCP audit of record (`s33-h1-2-audit-r3`) passed 99/99 with `tts.cancel` FIXED and every other action unchanged, `AUDIT_FINGERPRINT` 49d577f4bc8c5ea65e22676d96e83050ef41bd5e37f1c7d28efec93f59a56ce7. H1-3 `WINDOWS_GATE` (`s33-h1-3-windows-gate-r2`) passed 17/17 stages: pytest 724/0, Vitest 804/804, Electron 139/0/0/0, MCP 423/423, source audit 0 hits, `GATE_FINGERPRINT` 300cc234644b17997d1e6e7f2c3a7e6ffc3d0a41bb37b9e6252db41799b26f80 before and after. H1-4 `gate-check` (`s33-h1-4-gate-check-r2`) passed. The earlier `s33-h1-2-audit-final` and `s33-h1-3-windows-gate` runs are superseded.

### Quality Gate Results

```
pyright packages/: 0 errors
ruff check packages/ tests/: All checks passed!
ui typecheck / lint, mcp typecheck: exit 0
openapi --check: exit 0 (no route or schema change in MEU-76)
pytest tests/: 668 passed
ui Vitest: 802 passed
MCP Vitest: 413 passed (baseline 411 + 2 AC-76.9)
source audit over the MEU-76 files: 0 hits
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/errors.py` | modified | +5 | `ExtractError`; appended to `DOMAIN_ERROR_TYPES` |
| `packages/api/src/avkit_api/errors.py` | modified | +60/−9 | `ExtractError: 422`; `REQUEST_ID_HEADER`; `_route`; `log_unhandled_error`; `internal_error_response`; event for unmapped 500; backstop |
| `packages/api/src/avkit_api/main.py` | modified | +10/−2 | middleware `except Exception` (`CORS_SAFE_500`); imports `REQUEST_ID_HEADER` from errors.py |
| `packages/core/src/avkit_core/services/health.py` | modified | +1/−1 | `CONSOLE_FIELDS_NEW` |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modified | +7/−6 | `_run_extract` raises `ExtractError`; non-dict check before `_info_dict` |
| `ui/src/renderer/src/lib/api.ts` | modified | +6/−1 | `GUI_ERROR_TEXT` |
| `mcp-server/scripts/audit/census.ts` | modified | +5/−4 | `BOT_WALL` for the two add members; `:8` comment names ExtractError |
| `tests/e2e/test_api_error_surface.py` | new | 1–240 | AC-76.1, 76.2, 76.4, 76.5, 76.7 |
| `tests/unit/test_console_level.py` | modified (append only) | +30 | AC-76.3 |
| `tests/integration/test_youtube_adapter.py` | modified (append only) | +51 | AC-76.6 |
| `ui/tests/unit/api-fetch.test.ts` | modified (append only) | +54 | AC-76.8 |
| `mcp-server/tests/audit/census-signature.test.ts` | new | 1–27 | AC-76.9 |
| `tests/unit/test_domain.py` | modified (TA-1 only) | +1 | `"ExtractError"` |

```diff
         try:
             response = await call_next(request)
+        except Exception as exc:
+            # CORS_SAFE_500: answered here, inside CORSMiddleware, so the 500 carries CORS.
+            log_unhandled_error(request, exc)
+            response = internal_error_response(request_id)
         finally:
             structlog.contextvars.unbind_contextvars("request_id")
```

```diff
-            raise DomainError(str(exc) or "yt-dlp download failed") from exc
+            raise ExtractError(str(exc) or "yt-dlp download failed") from exc
         except OSError as exc:
-            raise DomainError("yt-dlp IO failed") from exc
-        if not isinstance(info, dict):
-            raise DomainError("yt-dlp returned no info")
-        return info, logger
+            raise ExtractError("yt-dlp IO failed") from exc
+        if not isinstance(raw, dict):
+            raise ExtractError("yt-dlp returned no info")
+        return _info_dict(raw), logger
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-32
    stage: execution
    question: "Where does _route get the include prefix for the log line and GUI_ERROR_TEXT?"
    resolution: autonomous
    class: two-way
    chosen: "Derive it from the public route path_regex, not FastAPI's private effective-route context"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/errors.py:57 — _route"]
    research: { engine: none, sources: [] }
    reasoning: "path_regex is public API on every Starlette route; the private context key can change between FastAPI versions and would break the log field silently."
  - id: D-33
    stage: execution
    question: "Does GUI_ERROR_TEXT also apply to a masked 503?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: the masked 503 carries the same internal_error code and request id, and the contract keys on the code"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:130 — GUI_ERROR_TEXT"]
    research: { engine: none, sources: [] }
    reasoning: "Keying on the status would show a raw body for one internal_error response and the friendly text for another; keying on the code gives one rule for both."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-15 | claude-code | Initial handoff after gate76 |
| Corrected | 2026-10-16 | claude-code | Decision Log rewritten as the canonical `decision_log` YAML, one entry per former bullet (D-43); final evidence points at the A-14 reruns (`s33-h1-2-audit-r3`, `s33-h1-3-windows-gate-r2`) |
