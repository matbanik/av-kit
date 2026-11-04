---
date: "2026-08-19"
project: "p3-services"
meu: "MEU-12"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-19-p3-services/implementation-plan.md"
build_plan_section: "bp03s3.3"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-19-p3-services-MEU-11-handoff.md"
---

# Handoff: 2026-08-19-p3-services-MEU-12-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-12 — `TextPreparationService` + `TTSService` + `ModelService`. `SPACY_MODEL=en_core_web_sm`; missing model → `SpacyModelNotFoundError` (chunk step only). `TTS_PROGRESS_RESOLUTION=1000`. Hash/preview only; `source_path` unread. RULE-3: no torch in core. No `ModelFetchJob`.
**Build Plan Section**: `docs/build-plan/03-service-layer.md` §TTS + Prepare + Models
**Predecessor**: MEU-11 transcript

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-12.1 | unit | Disabled steps omitted; `PREPARE_ORDER`; kokoro last when enabled; unknown id → ValidationError | Spec Prepare | `test_ac_12_1_prepare_order_and_unknown` | ✅ |
| AC-12.2 | unit | chunk uses mocked `spacy.load(SPACY_MODEL)`; missing → `CHUNK_DEPENDENCY_ERROR`; kokoro transforms | Spec 303 | `test_ac_12_2_chunk_and_kokoro` | ✅ |
| AC-12.3 | unit | Generate hash/preview only; require loaded model; `read_text` count 0 | Spec; R2-6 | `test_ac_12_3_and_12_4_generate_hash_and_mp3` | ✅ |
| AC-12.4 | unit | WAV `write_audio_wav`; MP3 also `MediaPort.convert`; no soundfile | Spec | `test_ac_12_3_and_12_4_generate_hash_and_mp3` | ✅ |
| AC-12.5 | unit | `segments_done=clamp(round(f*1000),0,1000)`; non-finite skipped; cancel between callbacks | Spec 328 | `test_ac_12_5_progress_resolution_and_cancel` | ✅ |
| AC-12.6 | unit | Illegal TTS edge → Conflict; empty/speed/format/not loaded → ValidationError | Spec | `test_ac_12_6_validation_and_illegal_edge` | ✅ |
| AC-12.7 | unit | ModelDownloadRuntime `state` + `fraction`; second download → Conflict; restart-equivalent Idle | Spec 349 | `test_ac_12_7_model_download_runtime` | ✅ |
| AC-12.8 | unit | Catalog ∪ sideload; load/unload/get_status delegate TTSPort; no torch import | Spec; RULE-3 | `test_ac_12_8_list_load_no_torch` | ✅ |
| AC-12.9 | integration | G29 real tmp UoW TTSJob add (hash/preview only) | G29 | `test_ac_12_9_g29_real_tmp_uow_tts` | ✅ |
| AC-12.10 | unit | `get_status(job_id)` row; missing → NotFound | Spec 318 | `test_ac_12_10_get_status` | ✅ |

Domain graph: `test_ac_12_tts_transition_graph`. `SpacyModelNotFoundError` in `DOMAIN_ERROR_TYPES`.

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| `test_ac_12_1_prepare_order_and_unknown` | `ModuleNotFoundError: avkit_core.services.prepare` | 102/171 passed | `tests/unit/test_services.py:1331` |
| `test_ac_12_3_and_12_4_generate_hash_and_mp3` | `ModuleNotFoundError: avkit_core.services.models` | passed | `tests/unit/test_services.py:1473` |

Receipts: `C:/Temp/av-kit/fail-to-pass-meu-12-prepare.txt` (historical). `fail-to-pass-meu-12-tts.txt` reconstructed after green by hiding `tts.py`/`models.py`.

Do **not** force `segments_done=1000` on Done — last callback wins (AC-12.5 expects 250 after `f=0.25`).

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `uv sync --all-packages` | 0 | `spacy>=3.7` |
| H1-2 registered suite | 0 | 171 passed |
| pyright / ruff | 0 | clean |

### Quality Gate Results

```
pyright: 0 errors, 0 warnings
ruff: 0 violations
pytest: 171 passed
SCAN_OPEN: no open( in tts.py/models.py/prepare.py
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/tts.py` | modified | 31–35 | `TTS_TRANSITIONS` |
| `packages/core/src/avkit_core/domain/errors.py` | modified | 80–81, 206 | `SpacyModelNotFoundError` |
| `packages/core/src/avkit_core/services/prepare.py` | new | 1–254 | mocked `spacy.load`; degrade chunk only |
| `packages/core/src/avkit_core/services/tts.py` | new | 1–220 | hash/preview; resolution 1000 |
| `packages/core/src/avkit_core/services/models.py` | new | 1–144 | runtime `fraction`; dest `mkdir` |
| `packages/core/pyproject.toml` | modified | deps | `spacy>=3.7` |
| `tests/unit/test_services.py` | modified | AC-12.* | |
| `tests/unit/test_domain.py` | modified | error names + TTS graph | |

```diff
+SPACY_MODEL = "en_core_web_sm"
+CHUNK_DEPENDENCY_ERROR = SpacyModelNotFoundError
+segments_done = clamp(round(f * 1000), 0, 1000)
+# ModelService.download: no torch string; ConflictError while another thread holds
```

NSIS spaCy model bundle remains MEU-25.

---

## Codex Validation Report

_Left blank for reviewer agent._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | — | — | — | — |

### Verdict

`pending` — independent Codex `/execution-critical-review`

---

## Corrections Applied (2026-08-19)

**Findings resolved**: 0/0 (pre-review)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| — | — | — | — |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| TTS/models REST | Phase 4 | MEU-16 | grouping Session 5 |
| spaCy model in NSIS | Phase 7 | MEU-25 | `en_core_web_sm` |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | Initial MEU-12 handoff |
| Submitted for review | 2026-08-19 | cursor-grok-4.6 | Pending Codex exec review |
