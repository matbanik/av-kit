---
date: "2026-08-19"
project: "p4-rest-api"
meu: "MEU-16"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-19-p4-rest-api/implementation-plan.md"
build_plan_section: "bp04s3"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-19-p4-rest-api-MEU-15-handoff.md"
---

# Handoff: 2026-08-19-p4-rest-api-MEU-16-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-16 — transcripts aggregates + TTS/models routers, `TTS_NO_MODEL_CONFLICT`, `VOICES_FACADE`, `BODY_ROUTES` extra oracle, `EXPORT_OPENAPI` + `openapi.committed.json`, G29 `build_services`.
**Build Plan Section**: `docs/build-plan/04-rest-api.md` §Transcripts / TTS / Models / OpenAPI
**Predecessor**: MEU-15 downloads/settings/health

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-16.1 | integration | POST/GET transcripts envelope; start/pause/resume/stop 202; requeue/retry 409 when not Cancelled/Failed; compile 200 `{ compiled_paths }` only (no text). Valid reorder forwards exact `job_ids` and returns that permutation. | Spec | `tests/e2e/test_api_transcripts.py:test_ac_16_1_transcript_lifecycle_and_conflicts` | ✅ |
| AC-16.2 | integration | Job out has `transcripts_done`/`last_*`; never `video_ids`/`text`. | Spec | `tests/e2e/test_api_transcripts.py:test_ac_16_2_aggregates_without_video_ids_or_text` | ✅ |
| AC-16.3 | integration | prepare unknown step → 422; generate 201 has `text_preview` not `text`; `source_path` unread (fake filesystem `read_text` count 0). | Spec; p3 | `tests/e2e/test_api_tts_models.py:test_ac_16_3_prepare_generate_preview_and_unread_source` | ✅ |
| AC-16.4 | integration | **Control `TTS_NO_MODEL_CONFLICT`.** Observable: 409. Chain: `generate` → `ConflictError` → handler. Negative: 422 for “no model loaded”. Overlap generate → 409. | Spec 409; p3 RULE-3 | `tests/e2e/test_api_tts_models.py:test_ac_16_4_no_model_and_overlap_are_409` | ✅ |
| AC-16.5 | integration | models download 202 immediate `{ variant }`; second in-flight 409; runtime poll; load/unload/status. Empty `variant_id` on download and load is schema-owned 422 `ERROR_ENVELOPE` (not 404). | Spec; p3 RULE-2; exec-r1 F1 | `tests/e2e/test_api_tts_models.py:test_ac_16_5_model_download_runtime_and_load`; `test_ac_16_5_empty_variant_id_is_422` | ✅ |
| AC-16.6 | integration | **Control `ROUTE_INDEX`.** Observable: OpenAPI `paths` set == `ROUTE_INDEX`. Chain: `create_app` → `/openapi.json` → census test. Negative: missing path or extra undocumented path. Path census alone does **not** satisfy AC-16.7/`VOICES_FACADE`. | Spec OpenAPI | `tests/e2e/test_api_openapi.py:test_ac_16_6_openapi_path_census`; `test_ac_16_6_each_route_index_row` | ✅ |
| AC-16.7 | integration | **Control `VOICES_FACADE`.** Observable: 200 `{ items: VoiceOut[] }` and fake `TTSService.list_voices` call count ≥ 1. Chain: `GET /tts/voices` → public `TTSService.list_voices` → `TTSPort.list_voices`. Negative: OpenAPI path present while public method never called; route reads `_tts`; `lang_code` user-set field. | Spec 243–247; F1 | `tests/e2e/test_api_tts_models.py:test_ac_16_7_voices_facade_calls_public_list_voices` | ✅ |
| AC-16.8 | integration | `EXPORT_OPENAPI --check` passes after `-o` once. `STATIC_BEFORE_ID` (Starlette match: `/tts/voices` before `/tts/{id}`). | G8; Spec factory | `tests/e2e/test_api_openapi.py:test_ac_16_8_export_check_and_static_before_id` | ✅ |
| AC-16.9 | integration | **Control `BODY_ROUTES`.** Observable: 422 `ERROR_ENVELOPE` for an extra field on **every** POST/PUT in `ROUTE_INDEX`. Chain: `ApiModel` → RequestValidationError handler. Negative: any body route returns 2xx with extra key. | Spec 107, 420; F2 | `tests/e2e/test_api_bodies.py:test_ac_16_9_extra_field_is_422` | ✅ |
| AC-16.10 | integration | G29 `TEST_API_WIRING`: real UoW factory constructs; `GET /health` 200. | G29 | `tests/integration/test_api_wiring.py:test_ac_16_10_build_services_health` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| `test_api_transcripts.py` collect | `ModuleNotFoundError: No module named 'tests'` | 2 passed | `tests/e2e/test_api_transcripts.py:9` |
| `test_ac_16_8` | `ValueError: '/api/v1/tts/voices' is not in list` | passed | `tests/e2e/test_api_openapi.py:105` |
| `test_ac_16_10` | `RecursionError` (`HealthService._process` → `settings.get` → UoW log) | passed | `packages/core/src/avkit_core/services/health.py:114` |
| `test_ac_16_5_empty_variant_id_is_422` | `assert 404 == 422` (empty `variant_id` reached `NotFoundError`) | passed | `packages/api/src/avkit_api/schemas/models.py:15`; `tests/e2e/test_api_tts_models.py:129` |

Receipts: `C:/Temp/av-kit/fail-to-pass-meu-16-transcripts.txt`, `fail-to-pass-meu-16-tts.txt`, `fail-to-pass-p4-exec-r1.txt`. Green: `C:/Temp/av-kit/pytest-api.txt` (109 passed after F1/F2 oracles).

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| Red transcripts | 2 | `No module named 'tests'` |
| Green transcripts | 0 | 2 passed |
| Red TTS/OpenAPI/bodies/wiring | 1 | STATIC_BEFORE_ID + RecursionError |
| Green e2e + wiring | 0 | 107 passed (pre-r1); 109 passed after F1/F2 oracles |
| `export_openapi.py -o` then `--check` | 0 | committed file written; `ModelDownloadIn`/`ModelLoadIn` `minLength: 1` |
| pyright packages/api packages/core | 0 | 0 errors |
| ruff packages/api packages/core tools/export_openapi.py | 0 | All checks passed |

### Quality Gate Results

```
pyright: 0 errors, 0 warnings
ruff: 0 violations
pytest: 109 API + 288 verification-plan (H1-2 pre-oracle; API suite refreshed)
anti-placeholder: 0 matches
MEU_SCOPED_GATE: PASS
```

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `avkit_api/routes/transcripts.py` | new | Aggregates from `list_items`; `{id}` paths |
| `avkit_api/routes/tts.py` | new | prepare/generate/voices before `/{id}` |
| `avkit_api/routes/models.py` | new | 202 download; runtime; load/unload |
| `avkit_api/schemas/{transcripts,tts,models}.py` | new | ApiModel extra-forbid |
| `avkit_api/wiring.py` | modified | `build_services` composition root + hook box |
| `avkit_api/main.py` | modified | include transcripts/tts/models; unpack `build_services` |
| `avkit_core/services/tts.py` | modified | `TTS_NO_MODEL_CONFLICT` + `VOICES_FACADE` |
| `avkit_core/services/health.py` | modified | processor re-entrancy guard for G29 |
| `tools/export_openapi.py` | new | `--check` / `-o` dummy-service export |
| `openapi.committed.json` | new | G8 committed schema |
| `tests/e2e/test_api_{transcripts,tts_models,openapi,bodies}.py` | new | AC-16.1–16.9 |
| `tests/e2e/api_fakes.py` | new | shared TestClient fakes |
| `tests/integration/test_api_wiring.py` | new | AC-16.10 |
| `pyproject.toml` | modified | pytest `pythonpath` includes `.` |

```diff
+    def list_voices(self) -> list[VoiceConfig]:
+        return self._tts.list_voices()
```

```diff
+        if not status.is_loaded:
+            raise ConflictError("a TTS model must be loaded")
```

```diff
+        with self._lock:
+            if self._processing:
+                return event_dict
+            self._processing = True
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

| Finding | Change | Evidence |
|---------|--------|----------|
| F1 empty `variant_id` 404 | `ModelDownloadIn` and `ModelLoadIn` use `Field(min_length=1)`; empty download/load return 422 `ERROR_ENVELOPE` and leave `models.downloading` false. Regenerated `openapi.committed.json`. | `C:/Temp/av-kit/fail-to-pass-p4-exec-r1.txt`; `test_ac_16_5_empty_variant_id_is_422` |
| F2 transcript reorder | `FakeTranscript.reorder_queue` permutes + `last_reorder`; `test_ac_16_1` asserts `[created_id, JOB_A]` on both the fake and the list envelope. | `tests/e2e/test_api_transcripts.py`; `tests/e2e/api_fakes.py` |

**Findings resolved**: 2/2 from exec-r1 (F2 download half is on the MEU-15 handoff).

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | Initial MEU-16 handoff |
| Submitted for review | 2026-08-19 | cursor-grok-4.6 | Awaits H1-7 Codex |
| Exec-r1 corrections | 2026-08-19 | cursor-grok-4.6 | F1 empty-ID 422; F2 transcript reorder oracle |
