---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
---

# Critical Review: p2-external-adapters

## Intent Anchor

Session 3 was intended to deliver MEU-6, MEU-7, and MEU-9 as project-integrated external adapters behind the frozen Phase 1 ports, with deterministic mocked integration coverage, no live YouTube/Hugging Face access, no persistence ownership, and no changes to Session 2 infrastructure. The delivered layout and most contracts are present, but three independently reproduced runtime defects mean the implementation does not yet achieve the approved plan's error, progress, and device-selection intent.

## Findings

| Finding | Severity |
|---------|----------|
| **F1 — Non-finite YouTube byte counters abort the download instead of being skipped.** `_progress_hook` checks only `speed` for finiteness, then converts `downloaded_bytes` and `total_bytes` directly with `int(...)` (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:288`, `packages/infrastructure/src/avkit_infra/youtube/adapter.py:312`). The production-hook probe reproduced `ValueError: cannot convert float NaN to integer` for `downloaded_bytes=NaN` and `OverflowError: cannot convert float infinity to integer` for `total_bytes=inf` (`C:/Temp/av-kit/p2-ea-exec-r1-progress-probe.txt`). This violates the round's explicit RULE-1 requirement that progress skip NaN/inf and can turn a malformed yt-dlp progress tick into a failed download. AC-6.17's current test covers only NaN `speed` (`tests/integration/test_youtube_adapter.py:591`). **Required correction:** reject/skip every tick containing a non-finite numeric progress field before integer conversion or callback, and add NaN/inf cases for downloaded and total counters. | High |
| **F2 — An unreadable file-mode cookie source maps to generic `DomainError`, not `CookieTestError`.** The precheck distinguishes only missing/non-file paths (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:338`), while an `OSError`/`PermissionError` raised when yt-dlp opens an existing cookie file is caught by the generic IO branch and converted to `DomainError` (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:426`). The focused mocked-YoutubeDL probe returned `DomainError` with `PermissionError` as cause (`C:/Temp/av-kit/p2-ea-exec-r1-cookie-unreadable-probe.txt`). This contradicts the approved download-path cookie lock requiring missing/unreadable files to produce `CookieTestError` from `FileNotFoundError`/`OSError` (`docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md:198`). The existing test proves only the missing-file branch (`tests/integration/test_youtube_adapter.py:627`). **Required correction:** isolate cookie readability validation or otherwise preserve the cookie-source context so an unreadable cookie file raises `CookieTestError` from the original `OSError`; add an existing-but-unreadable oracle. | High |
| **F3 — PyTorch device selection is reported but never applied to the loaded model.** `load_model` resolves and stores the device string, then constructs `KModel(model=...)` without moving/evaluating it (`packages/infrastructure/src/avkit_infra/tts/adapter.py:112`); `generate` passes that existing model to `KPipeline` without a device (`packages/infrastructure/src/avkit_infra/tts/adapter.py:209`). The installed Kokoro implementation loads weights with `map_location='cpu'`, and its `KPipeline` branch for an existing `KModel` does not move it (`C:/Temp/av-kit/p2-ea-exec-r1-kokoro-device-api.txt`, `C:/Temp/av-kit/p2-ea-exec-r1-kokoro-pipeline-init.txt`). The adapter-level tracking probe requested CUDA, reported `device=cuda`, but recorded zero `model.to(...)` and zero `eval()` calls and no pipeline `device` kwarg (`C:/Temp/av-kit/p2-ea-exec-r1-tts-device-probe.txt`). This violates the Phase 2 `load_model` device contract and approved Device Auto/engine split (`docs/build-plan/02-infrastructure.md:406`, `docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md:211`). **Required correction:** apply the resolved device to the PyTorch model and verify status reflects the actual loaded device; add tracking-fake oracles for explicit/Auto CPU, CUDA, and MPS resolution without requiring hardware. | High |
| **F4 — Seven tests are weak under IR-5 because they allow the reproduced or named contract class to remain broken while green.** `test_ac_6_15_ytdlp_version_uses_library_not_cli` patches the private helper it is meant to verify (`tests/integration/test_youtube_adapter.py:552`); AC-6.17 checks only speed finiteness (`tests/integration/test_youtube_adapter.py:591`); AC-6.18 checks only a missing, not unreadable, cookie file (`tests/integration/test_youtube_adapter.py:627`); AC-7.8 checks confinement against only the YouTube peer (`tests/integration/test_transcript_adapter.py:266`); AC-9.1 accepts any ONNX `>=1.x` rather than the locked `>=1.16` floor (`tests/integration/test_tts_models.py:247`); AC-9.4 checks engine class selection but never model device application (`tests/integration/test_tts_models.py:325`); and AC-9.12 samples four directories instead of scanning all infrastructure/core import sites (`tests/integration/test_tts_models.py:554`). The current tree is clean where applicable, as shown by `C:/Temp/av-kit/p2-ea-exec-r1-confinement-scan.txt`, but these tests would false-pass future regressions. **Required correction:** strengthen these tests with direct implementation oracles and repository-wide AST/import scans. | Medium |

## Scope

**Correlation:** The explicit plan slug, task, three same-project handoffs, and SSOT all bind Session 3 to MEU-6, MEU-7, and MEU-9. The review expanded across all three handoffs and did not treat approved Session 2 persistence/media code or pending MEU-10–13 services as missing Session 3 work.

**Reviewed artifacts:**

- `docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md`
- `docs/execution/plans/2026-08-19-p2-external-adapters/task.md`
- `.agent/context/handoffs/2026-08-19-p2-external-adapters-MEU-6-handoff.md`
- `.agent/context/handoffs/2026-08-19-p2-external-adapters-MEU-7-handoff.md`
- `.agent/context/handoffs/2026-08-19-p2-external-adapters-MEU-9-handoff.md`
- `docs/build-plan/02-infrastructure.md` YouTube, Transcript, TTS, and Model manager sections
- `packages/core/src/avkit_core/ports/`
- `packages/infrastructure/src/avkit_infra/{youtube,transcript,tts,model_manager}/`
- The three adapter integration files plus the registered Session 1–2 regression files
- `.agent/context/meu-status.yaml`

The workspace is not a git repository, so verification used current file state, numbered source reads, runtime probes, AST scans, and fresh round-specific receipts rather than `git diff`.

## Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 — Live runtime evidence | Pass, contract-adjusted | The registered suite invoked production adapters and Session 1–2 implementations and passed 113 tests. External network/ML libraries were mocked as the approved plan requires; live YouTube/HF access was intentionally not used. Receipt: `C:/Temp/av-kit/p2-ea-exec-r1-pytest.txt`. |
| IR-2 — Stub behavioral compliance | Pass | No placeholders or test neutralization were found in the scoped adapter paths/tests. Receipt: `C:/Temp/av-kit/p2-ea-exec-r1-placeholder-skip-scan.txt`. The deliverables are concrete adapters, not stubs. |
| IR-3 — Error mapping completeness | Fail | F2 demonstrates an approved adapter error mapping is incomplete: unreadable cookie input becomes generic `DomainError`. REST route mapping is not in Session 3 scope. |
| IR-4 — Fix generalization | Pass for round 1 | No prior implementation-review corrections exist. Candidate defect classes were generalized across non-finite progress fields, missing/unreadable cookie paths, and explicit/Auto device paths. |
| IR-5 — Test rigor audit | Fail | All 39 tests were graded below. Thirty-two are strong; seven are weak and are consolidated in F4. |
| IR-6 — Boundary validation coverage | Fail | Cookie-file IO and yt-dlp progress payloads are external-input boundaries; F1 and F2 demonstrate unhandled boundary cases. Public frozen method signatures otherwise match exactly. |
| IR-7 — Deferral and AC-coverage integrity | Pass | Mechanical per-MEU comparison found every AC-6.*, AC-7.*, and AC-9.* (including AC-9.13) in its matching handoff, with no extras/missing IDs. MEU-10/11/12/13 are scheduled in SSOT. Receipt: `C:/Temp/av-kit/p2-ea-exec-r1-ac-ssot-probe.txt`. |

### IR-5 Test Grades — YouTube (18)

| Test | Grade | Basis |
|------|-------|-------|
| `test_ac_6_1_youtube_module_and_ytdlp_dependency` | 🟢 Strong | Imports the adapter and parses the declared dependency. |
| `test_ac_6_2_youtube_port_signatures_match` | 🟢 Strong | Compares every frozen method's parameters and return annotation. |
| `test_ac_6_3_extract_info_video_and_unique_preserve_playlist` | 🟢 Strong | Asserts exact video fields and unique-preserve playlist behavior. |
| `test_ac_6_4_extract_video_ids_playlistend_ctor` | 🟢 Strong | Covers negative, zero/omitted, and positive playlist limits. |
| `test_ac_6_5_get_formats_maps_and_rejects_incomplete_rows` | 🟢 Strong | Asserts exact DTO mapping and malformed-row rejection. |
| `test_ac_6_6_quality_selectors_exhaustive` | 🟢 Strong | Exhausts the enum and captures exact yt-dlp selector values. |
| `test_ac_6_7_audio_selectors_and_cookie_hls` | 🟢 Strong | Exhausts audio formats and distinguishes cookie HLS selection. |
| `test_ac_6_8_cookie_opts_and_unknown_mode` | 🟢 Strong | Covers all cookie modes, exact opts, byte exclusion, and fail-closed mode validation. |
| `test_ac_6_9_cancel_raises_and_continue_returns_result` | 🟢 Strong | Asserts the exact cancellation type and positive result path. |
| `test_ac_6_10_age_gate_and_unmapped_download_error` | 🟢 Strong | Asserts exact error classes and original causes for both branches. |
| `test_ac_6_11_sabr_needles_set_flag_without_raising` | 🟢 Strong | Exercises every needle and a clean negative case. |
| `test_ac_6_12_no_download_archive` | 🟢 Strong | Captures opts and asserts all forbidden archive representations are absent. |
| `test_ac_6_13_test_cookies_never_raises_cookie_error` | 🟢 Strong | Covers missing, locked, success, and none-mode DTO results. |
| `test_ac_6_14_check_sabr_status_probe` | 🟢 Strong | Asserts exact probe URL and active/inactive DTO fields. |
| `test_ac_6_15_ytdlp_version_uses_library_not_cli` | 🔴 Weak | Replaces the private version helper, so the actual library-version reader may be broken while the test stays green. |
| `test_ac_6_16_extractor_args_cookie_vs_sabr` | 🟢 Strong | Captures and compares the complete extractor-args maps. |
| `test_ac_6_17_progress_skips_nan_and_throttles` | 🔴 Weak | Covers only NaN speed; non-finite byte counters crash production code. |
| `test_ac_6_18_no_uow_and_missing_cookie_file_cause` | 🔴 Weak | Proves missing-file chaining but not the approved unreadable-file branch. |

### IR-5 Test Grades — Transcript (8)

| Test | Grade | Basis |
|------|-------|-------|
| `test_ac_7_1_transcript_module_and_version_floor` | 🟢 Strong | Parses the `>=` major floor and includes a negative `>=0.9` control. |
| `test_ac_7_2_transcript_port_signature_matches` | 🟢 Strong | Compares the frozen signature exactly. |
| `test_ac_7_3_language_order_then_en_then_list` | 🟢 Strong | Asserts ordered fetch calls, short-circuiting, English fallback, and list fallback. |
| `test_ac_7_4_disabled_missing_unavailable_return_none` | 🟢 Strong | Exercises all three mapped library errors, zero writes, and forbidden domain-error names. |
| `test_ac_7_5_retryable_request_and_ip_blocked` | 🟢 Strong | Asserts both retryable types, exact causes, and no `TooManyRequests`. |
| `test_ac_7_6_join_newlines_language_and_title_fallback` | 🟢 Strong | Asserts the complete returned DTO and explicit title path. |
| `test_ac_7_7_no_sleep_and_unrecognized_domain_error` | 🟢 Strong | Combines a no-sleep guard with exact fail-closed error chaining. |
| `test_ac_7_8_no_uow_and_library_confined_to_transcript` | 🔴 Weak | Checks only the YouTube peer; imports in other infrastructure/core paths would pass. |

### IR-5 Test Grades — TTS and Models (13)

| Test | Grade | Basis |
|------|-------|-------|
| `test_ac_9_1_layout_deps_and_kokoro_adapter_name` | 🔴 Weak | The ONNX floor check accepts `>=1.0` even though the approved floor is `>=1.16`. Layout/name/dependency checks are otherwise specific. |
| `test_ac_9_2_port_signatures_match` | 🟢 Strong | Compares every TTS and catalog method signature exactly. |
| `test_ac_9_3_list_voices_official_catalog` | 🟢 Strong | Asserts all 54 ordered IDs and every prefix/language mapping. |
| `test_ac_9_4_load_model_engine_split_every_seed` | 🔴 Weak | Proves engine-class selection for all seeds but never proves the resolved PyTorch device is applied. |
| `test_ac_9_5_unload_clears_loaded_status` | 🟢 Strong | Asserts loaded and unloaded status fields. |
| `test_ac_9_6_generate_pytorch_and_onnx_preprocess` | 🟢 Strong | Captures adapter-built ONNX feeds, exact values/dtypes/shapes, progress, PCM, and zero audio writes. |
| `test_ac_9_7_lang_code_from_voice_id` | 🟢 Strong | Captures exact pipeline lang/model/repo kwargs. |
| `test_ac_9_8_download_hf_map_returns_path_no_uow` | 🟢 Strong | Asserts exact HF mapping/call, returned path, progress, and persistence exclusion. |
| `test_ac_9_9_offline_skips_hf` | 🟢 Strong | Covers both existing variant path and existing destination with zero HF calls. |
| `test_ac_9_10_sideload_catalog_metadata_and_stat` | 🟢 Strong | Asserts all seed IDs, catalog parity, file stats, and unknown-file omission. |
| `test_ac_9_11_download_oserror_is_model_download_error` | 🟢 Strong | Asserts the domain error and original OSError cause. |
| `test_ac_9_12_library_confinement` | 🔴 Weak | Samples selected directories rather than enforcing confinement across all infrastructure/core Python files. |
| `test_ac_9_13_missing_vocab_voice_and_input_limit` | 🟢 Strong | Exercises both missing-resource causes, the 511-token rejection, and forbidden dependency strings. |

## Verified Contract Surfaces

- All frozen Protocol method signatures match the four concrete adapters; no `TTSAdapter` class exists. Receipt: `C:/Temp/av-kit/p2-ea-exec-r1-signatures.txt`.
- Required adapter directories exist. Library imports are confined to their approved directories; prohibited adapter/dependency strings and core infrastructure imports are absent. Receipt: `C:/Temp/av-kit/p2-ea-exec-r1-confinement-scan.txt`.
- YouTube cookie modes, selector maps, SABR needles/probe URL, archive exclusion, missing-cookie cause, and current speed-only finite guard pass the integration suite.
- Transcript uses the v1 instance `.fetch`/`.list` API, maps disabled/missing/unavailable to `None`, maps `RequestBlocked`/`IpBlocked` to the retryable domain error, has no sleep/file write, and uses the video ID title fallback.
- ONNX generation captures adapter-built `[[0,1,2,0]]` int64 input IDs, `(1,256)` float32 style, float32 speed, and mocked `session.run`; missing vocab/voice and input length are covered. PyTorch/ONNX engine class separation and every seed load oracle pass.
- Model download returns `Path`, performs no UoW/`mark_downloaded`, skips HF when offline files exist, and sideloads only known catalog names using file stats.
- SSOT has MEU-6/7/9 at `ready_for_review` with the exact no-trailing-slash execution-plan binding, and Phase `"2"` includes both required trailing-slash plan paths.
- Session 2 SQLite/filesystem/media regression coverage remains green within the 113-test registered gate.

## Commands Executed

All commands used `rtk proxy`, redirected all streams to fresh `C:/Temp/av-kit/p2-ea-exec-r1-*` receipts, and preserved `$LASTEXITCODE` before receipt reads.

| Command / probe | Result | Receipt |
|-----------------|--------|---------|
| Registered six-file `pytest` gate | `113 passed` | `C:/Temp/av-kit/p2-ea-exec-r1-pytest.txt` |
| `uv run pyright packages/infrastructure/ packages/core/` | `0 errors, 0 warnings, 0 informations` | `C:/Temp/av-kit/p2-ea-exec-r1-pyright.txt` |
| `uv run ruff check packages/infrastructure/ packages/core/` | `All checks passed` | `C:/Temp/av-kit/p2-ea-exec-r1-ruff.txt` |
| Frozen-signature/public-class runtime probe | All signatures match; `has_TTSAdapter=false` | `C:/Temp/av-kit/p2-ea-exec-r1-signatures.txt` |
| Production YouTube progress-hook probe | NaN speed skipped; NaN downloaded and inf total raised | `C:/Temp/av-kit/p2-ea-exec-r1-progress-probe.txt` |
| Existing-but-unreadable cookie probe | Raised `DomainError` from `PermissionError` | `C:/Temp/av-kit/p2-ea-exec-r1-cookie-unreadable-probe.txt` |
| Installed Kokoro API/source probes | KModel loads on CPU; existing-model pipeline branch does not move it | `C:/Temp/av-kit/p2-ea-exec-r1-kokoro-device-api.txt`; `C:/Temp/av-kit/p2-ea-exec-r1-kokoro-pipeline-init.txt` |
| Adapter-level PyTorch device tracking probe | Reported CUDA; zero `.to()`/`.eval()` calls; no pipeline device | `C:/Temp/av-kit/p2-ea-exec-r1-tts-device-probe.txt` |
| AST library-confinement and prohibited-string scan | No current violations | `C:/Temp/av-kit/p2-ea-exec-r1-confinement-scan.txt` |
| Per-MEU AC and SSOT probe | Exact AC coverage and bindings; both Phase 2 plans present | `C:/Temp/av-kit/p2-ea-exec-r1-ac-ssot-probe.txt` |
| Placeholder/test-neutralization scan | No hits | `C:/Temp/av-kit/p2-ea-exec-r1-placeholder-skip-scan.txt` |

## Out-of-Contract Observations

- `KModel(model=path)` without an explicit config causes the installed Kokoro library to resolve `config.json` through its default HF repo. The approved plan does not explicitly define PyTorch config-sidecar/offline ownership, so this is recorded for later contract clarification rather than treated as a finding.

## Open Questions / Assumptions

None. The three High findings are reproducible against the current tree and do not depend on live network access or unavailable hardware.

## Required Follow-Up

1. Use `/execution-corrections` to add failing regression tests first for F1–F3, then correct the production adapters without changing frozen ports or Session 2 infrastructure.
2. Strengthen the seven weak IR-5 tests described in F4.
3. Re-run the registered pytest/pyright/ruff gates and the independent probes.
4. Append round 2 to this same rolling review file; do not create a recheck/final/approved variant.

## Verdict

`changes_required` — Three High runtime/contract findings survive independent verification. The registered suite and static gates are green, but the Materiality Gate is met because malformed progress can abort downloads, unreadable cookie files map to the wrong domain error, and PyTorch device selection is not applied despite being reported.

## Residual Risk

Live YouTube, Hugging Face, CUDA, and MPS execution was not run because the approved default-suite contract requires mocked external libraries and forbids live YouTube/HF access. The findings do not rely on those unavailable live surfaces: each was reproduced with current production code plus deterministic local test doubles or installed-library source behavior.

---

## Recheck (2026-08-19) — Round 2

**Workflow**: `/execution-critical-review` recheck round 2  
**Agent**: `gpt-5.6-sol`

### Intent Anchor

This recheck independently verifies that the round-1 F1–F4 corrections make the Phase 2 YouTube, transcript, TTS, and model-manager adapters satisfy their approved runtime and test-rigor contracts without changing frozen ports or Session 2 infrastructure. The corrected implementation achieves that intent: all prior findings are fixed, the fresh six-file gate is green, and no new material failure class was found.

### Findings

| Finding | Severity |
|---------|----------|
| _None._ | — |

### Prior Finding Recheck

| Finding | Prior Status | Current Result | Evidence |
|---------|--------------|----------------|----------|
| **F1 — Non-finite YouTube progress counters** | Open — High | ✅ Fixed | `_finite_int` rejects non-finite numeric counters before conversion, and `_progress_hook` skips invalid speed/downloaded/total ticks before callback (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:227`, `packages/infrastructure/src/avkit_infra/youtube/adapter.py:300`). The independent probe exercised NaN/inf speed, downloaded bytes, and total bytes without an exception or callback, then observed the next valid callback. Receipt: `C:/Temp/av-kit/p2-ea-exec-r2-progress-probe.txt`. The direct regression oracle is at `tests/integration/test_youtube_adapter.py:595`. |
| **F2 — Existing-but-unreadable cookie mapping** | Open — High | ✅ Fixed | File-mode cookie validation opens the existing path and maps `OSError` to `CookieTestError` with the original cause; downstream file-mode `OSError` receives the same mapping (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:344`, `packages/infrastructure/src/avkit_infra/youtube/adapter.py:423`). The independent `Path.open` probe raised `CookieTestError` from `PermissionError`. Receipt: `C:/Temp/av-kit/p2-ea-exec-r2-cookie-unreadable-probe.txt`. Missing and existing-file permission cases are asserted at `tests/integration/test_youtube_adapter.py:645`. |
| **F3 — PyTorch device selection not applied** | Open — High | ✅ Fixed | `load_model` resolves the requested device, calls `KModel(...).to(resolved_device)`, then `.eval()`, while status reports the same device (`packages/infrastructure/src/avkit_infra/tts/adapter.py:29`, `packages/infrastructure/src/avkit_infra/tts/adapter.py:89`, `packages/infrastructure/src/avkit_infra/tts/adapter.py:112`). The independent tracking fake passed explicit CPU/CUDA and Auto→CUDA/MPS; ONNX constructed no `KModel`. Receipt: `C:/Temp/av-kit/p2-ea-exec-r2-tts-device-probe.txt`. Direct regression oracles are at `tests/integration/test_tts_models.py:369`. |
| **F4 — Seven weak tests** | Open — Medium | ✅ Fixed | The version test exercises the real library reader (`tests/integration/test_youtube_adapter.py:552`); progress and cookie tests cover the corrected production paths (`tests/integration/test_youtube_adapter.py:595`, `tests/integration/test_youtube_adapter.py:645`); transcript confinement scans infrastructure and core by AST (`tests/integration/test_transcript_adapter.py:278`); the ONNX dependency floor is parsed as `>=1.16` (`tests/integration/test_tts_models.py:155`, `tests/integration/test_tts_models.py:290`); device application uses tracking fakes (`tests/integration/test_tts_models.py:209`, `tests/integration/test_tts_models.py:369`); and library confinement scans all infrastructure/core Python files by AST (`tests/integration/test_tts_models.py:162`, `tests/integration/test_tts_models.py:642`). The independent version/floor/confinement probe passed. Receipt: `C:/Temp/av-kit/p2-ea-exec-r2-f4-probe.txt`. |

### Confirmed Fixes

- F1: malformed NaN/inf progress fields are ignored without aborting the download; the existing speed-only behavior remains green.
- F2: an existing cookie path that fails to open produces `CookieTestError` with an `OSError`/`PermissionError` cause.
- F3: every requested PyTorch device case is applied to the model and reflected in status; ONNX remains isolated from `KModel` construction.
- F4: all seven round-1 weak tests now contain direct implementation or repository-wide AST oracles.

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 — Live runtime evidence | Pass, contract-adjusted | The registered domain + SQLite + filesystem + adapter suite ran current production paths with approved deterministic external-library fakes: `113 passed`. Receipt: `C:/Temp/av-kit/p2-ea-exec-r2-pytest.txt`. Live YouTube/HF remained forbidden by the plan. |
| IR-2 — Stub behavioral compliance | Pass | Scoped adapters are concrete, all tests pass, and the fresh neutralization/placeholder scan found no skip, xfail, TODO, FIXME, or `NotImplementedError` hits. Receipt: `C:/Temp/av-kit/p2-ea-exec-r2-contract-scan.txt`. |
| IR-3 — Error mapping completeness | Pass | The prior cookie error-mapping gap is closed in both the pre-open and file-mode download IO paths, and the independent permission probe preserves the original cause. |
| IR-4 — Fix generalization | Pass | F1 covers speed plus both byte counters; F2 covers missing and unreadable file-mode sources; F3 covers explicit and Auto device resolution plus the ONNX negative oracle. |
| IR-5 — Test rigor audit | Pass | The seven previously weak tests are now strong direct oracles; the other 32 round-1 strong tests remain green. No neutralized tests were found. |
| IR-6 — Boundary validation coverage | Pass | External progress payload non-finites and cookie-file IO failures now have production guards, negative tests, and independent probes. |
| IR-7 — Deferral and AC-coverage integrity | Pass | Exact handoff coverage remains 18 AC-6, 8 AC-7, and 13 AC-9 entries; MEU-6/7/9 remain bound to this plan at `ready_for_review`, and the Phase 2 plan entry is present. Receipt: `C:/Temp/av-kit/p2-ea-exec-r2-ac-ssot-probe.txt`. |

### Commands Executed

Every executable used `rtk proxy`, redirected all streams to a fresh `C:/Temp/av-kit/p2-ea-exec-r2-*` receipt, and captured `$LASTEXITCODE` before reading the receipt.

| Command / Probe | Result | Receipt |
|-----------------|--------|---------|
| Registered six-file pytest gate: domain + SQLite + filesystem + YouTube + transcript + TTS/models | `113 passed` | `C:/Temp/av-kit/p2-ea-exec-r2-pytest.txt` |
| `uv run pyright packages/infrastructure/ packages/core/` | `0 errors, 0 warnings, 0 informations` | `C:/Temp/av-kit/p2-ea-exec-r2-pyright.txt` |
| `uv run ruff check packages/infrastructure/ packages/core/` | `All checks passed` | `C:/Temp/av-kit/p2-ea-exec-r2-ruff.txt` |
| Production progress-hook probe | All NaN/inf cases skipped; valid callback preserved | `C:/Temp/av-kit/p2-ea-exec-r2-progress-probe.txt` |
| Existing-but-unreadable cookie probe | `CookieTestError` from `PermissionError` | `C:/Temp/av-kit/p2-ea-exec-r2-cookie-unreadable-probe.txt` |
| PyTorch device + ONNX isolation probe | CPU/CUDA/Auto→CUDA/Auto→MPS applied and status-matched; ONNX `KModel` delta 0 | `C:/Temp/av-kit/p2-ea-exec-r2-tts-device-probe.txt` |
| Version/floor/repository-wide AST confinement probe | Real version reader, `onnxruntime>=1.16`, zero forbidden infra/core imports | `C:/Temp/av-kit/p2-ea-exec-r2-f4-probe.txt` |
| AC/SSOT probe | Exact per-MEU AC sets and plan bindings | `C:/Temp/av-kit/p2-ea-exec-r2-ac-ssot-probe.txt` |
| Frozen-oracle and neutralization/placeholder source scan | Port-method comparison oracles present; no neutralization/placeholders | `C:/Temp/av-kit/p2-ea-exec-r2-contract-scan.txt` |

### Observations

- The three MEU handoffs retain their pre-round-1 AC wording and `Corrections Applied: 0/0` sections. This is clerical historical drift and is non-blocking; the user explicitly limited round-2 writes to this rolling review file.
- The workspace is not a git repository, so review evidence is current numbered source, runtime probes, AST scans, and exact receipts rather than a diff. No product, test, plan, frozen-port, or Session 2 file was written during this review.

### Open Questions / Assumptions

None.

### Verdict

`approved` — F1–F4 are independently verified fixed, all registered gates pass, and no new High/Critical failure class survives the Materiality Gate. The live frontmatter is therefore `round: 2`, `verdict: approved`, and `findings_count: 0`.

### Residual Risk

Live YouTube, Hugging Face, CUDA, and MPS execution was not run because the approved default-suite contract forbids live external access and requires mocked hardware/library boundaries. Device behavior was verified with tracking fakes, and the round-2 verdict does not generalize beyond those declared boundaries.
