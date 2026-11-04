---
date: "2026-08-19"
project: "p2-external-adapters"
meu: "MEU-9"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
build_plan_section: "bp02s2.5"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-19-p2-external-adapters-MEU-7-handoff.md"
---

# Handoff: 2026-08-19-p2-external-adapters-MEU-9-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-9 — `KokoroAdapter` (`TTSPort`) + `ModelCatalogAdapter` (`ModelCatalogPort`). Hybrid ONNX preprocess. No UoW. No `mark_downloaded`.
**Build Plan Section**: `docs/build-plan/02-infrastructure.md` §TTS + Model manager
**Predecessor**: MEU-7 transcript adapter

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-9.1 | integration | `tts/` + `model_manager/` importable; deps kokoro/hf/onnxruntime≥1.16; public class `KokoroAdapter` | Spec 38, 400 | `test_ac_9_1_layout_deps_and_kokoro_adapter_name` | ✅ |
| AC-9.2 | integration | Signatures match frozen TTS + catalog ports | frozen ports | `test_ac_9_2_port_signatures_match` | ✅ |
| AC-9.3 | integration | `list_voices()` length 54; ids `KOKORO_VOICE_IDS`; prefix/`LANG_BY_PREFIX` | Spec 409 | `test_ac_9_3_list_voices_official_catalog` | ✅ |
| AC-9.4 | integration | Every `SEED_VARIANT_IDS` member: PT→KModel; ONNX→InferenceSession not KModel; missing weight chained | Spec 406; RULE-2 | `test_ac_9_4_load_model_engine_split_every_seed` | ✅ |
| AC-9.5 | integration | `unload_model` → `is_loaded is False` | Spec 407 | `test_ac_9_5_unload_clears_loaded_status` | ✅ |
| AC-9.6 | integration | PT generate + ONNX `ONNX_PREPROCESS` captured `session.run` kwargs; finite progress; zero WAV | Spec 408; Human-approved | `test_ac_9_6_generate_pytorch_and_onnx_preprocess` | ✅ |
| AC-9.7 | integration | `lang_code` from `voice.voice_id[0]` | Spec 408, 412 | `test_ac_9_7_lang_code_from_voice_id` | ✅ |
| AC-9.8 | integration | `download` mocked `hf_hub_download` with `HF_FILE_MAP`; returns Path; no UoW | Spec 440–441 | `test_ac_9_8_download_hf_map_returns_path_no_uow` | ✅ |
| AC-9.9 | integration | Existing `variant.path` or dest file skips HF | Spec 444 | `test_ac_9_9_offline_skips_hf` | ✅ |
| AC-9.10 | integration | Sideload maps suffixes to seed ids; `CATALOG_METADATA` + `stat()` size; no DB | Spec 443 | `test_ac_9_10_sideload_catalog_metadata_and_stat` | ✅ |
| AC-9.11 | integration | HF/OS failure → `ModelDownloadError` from `OSError` | Spec 321; RULE-2 | `test_ac_9_11_download_oserror_is_model_download_error` | ✅ |
| AC-9.12 | integration | hf only under `model_manager/`; kokoro/onnxruntime only under `tts/` | SCAN_ADAPTER_LIBS | `test_ac_9_12_library_confinement` | ✅ |
| AC-9.13 | integration | Missing vocab/voice → `ModelLoadError` from `FileNotFoundError`; `input_ids>510` → `ValidationError`; no `kokoro-onnx` | RULE-2; Human-approved | `test_ac_9_13_missing_vocab_voice_and_input_limit` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| `test_ac_9_1_layout_deps_and_kokoro_adapter_name` | `ModuleNotFoundError: avkit_infra.tts` | passed | `tests/integration/test_tts_models.py` |

Receipts: `C:/Temp/av-kit/fail-to-pass-meu-9-tts.txt`, `fail-to-pass-meu-9-models.txt`.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `uv sync --all-packages` | 0 | kokoro, huggingface_hub, onnxruntime≥1.16 |
| `uv run pytest tests/integration/test_tts_models.py` (+ regression) | 0 | 113 passed |
| ONNX preprocess oracle | 0 | `input_ids == [[0,1,2,0]]` for phonemes `"ab"` vocab `{a:1,b:2}` |

### Quality Gate Results

```
pyright: 0 errors, 0 warnings
ruff: 0 violations
pytest: 113 passed
SCAN_SOUNDFILE: 0 matches
SCAN_CORE_INFRA: 0 matches
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | new | full | `KokoroAdapter` |
| `packages/infrastructure/src/avkit_infra/tts/voices.py` | new | full | 54 voices + catalog maps (lib-scan path bind) |
| `packages/infrastructure/src/avkit_infra/tts/__init__.py` | new | full | export `KokoroAdapter` |
| `packages/infrastructure/src/avkit_infra/model_manager/catalog.py` | new | full | re-export `CATALOG_METADATA`/`HF_FILE_MAP` |
| `packages/infrastructure/src/avkit_infra/model_manager/manager.py` | new | full | `ModelCatalogAdapter` |
| `packages/infrastructure/src/avkit_infra/model_manager/__init__.py` | new | full | package export |
| `packages/infrastructure/pyproject.toml` | modified | deps | kokoro, huggingface_hub, onnxruntime≥1.16 |
| `tests/integration/test_tts_models.py` | new | full | AC-9.* including ONNX kwargs capture |
| `tools/check_exec_review.py` | existing | — | plan-review gate (unchanged this MEU) |

```diff
+class KokoroAdapter:
+    def generate(self, text, voice, speed, on_progress) -> np.ndarray: ...
+class ModelCatalogAdapter:
+    def download(self, variant, dest_dir, on_progress) -> Path: ...
```

`CATALOG_METADATA` literals live under `tts/voices.py` so substring `kokoro` SCAN_ADAPTER_LIBS allow-path `tts` matches; `model_manager/catalog.py` re-exports. Session 2 `database/engine.py` seed ids still contain `kokoro-*` (frozen; not a library import).

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
| `mark_downloaded` / ModelDownloadRuntime persistence | frozen 2-arg mark; grouping Session 4 | MEU-12 | Spec 436, 442 |
| WAV/MP3 encode | out of this adapter | MEU-8 MediaPort already exists | Spec 414 |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | Initial MEU-9 handoff |
| Submitted for review | 2026-08-19 | cursor-grok-4.6 | Pending Codex exec review |
