---
date: "2026-10-15"
project: "tts-engine-runtime"
meu: "MEU-72"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md"
build_plan_section: "bp07"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch (tools/Invoke-CodexDispatch.ps1)"
predecessor: "2026-10-14-tts-engine-runtime-MEU-74-handoff.md"
---

# Handoff: 2026-10-14-tts-engine-runtime-MEU-72-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-72. The packaged backend speaks offline without torch or kokoro. Kokoro's `KPipeline` front end is replaced by av-kit's own G2P router and chunker. The PyInstaller spec bundles exactly the ONNX runtime chain, and the installer ships the licence notices.

- **Engine (`avkit_infra/tts/g2p.py`, new; `adapter.py`):**
  - **`G2P_ROUTE` (`KokoroG2p`):**
    - a/b go to a cached `misaki.en.G2P(trf=False, british=…, fallback=…, unk="")`, one per `british` flag. The fallback is `EspeakCliAdapter.en_fallback` (`ESPEAK_EN_FALLBACK`) only when eSpeak NG is detected, otherwise `None`.
    - Before misaki is built, `spacy.util.is_package("en_core_web_sm")` is checked, so a missing model raises `ConflictError("tts asset missing: tts_spacy_model")` instead of misaki running `spacy.cli.download`.
    - e/f/h/i/p go to `EspeakCliAdapter.phonemize` (`ESPEAK_G2P`, MEU-74).
    - Any other code (j, z) raises `ValidationError`.
  - **`CHUNK_RULE` (`split_phonemes`):** each 510-symbol window is cut after the last sentence end, else the last clause mark, else at the last space, else hard at 510. Chunks are stripped and non-empty, and order is kept. The adapter phonemizes sentence by sentence and joins with spaces before it splits.
  - **`TORCH_PATH`:**
    - `torch` is the only module-level try-import. `from kokoro import KModel` happens inside `load_model`, because kokoro's package `__init__` imports `pipeline`, which pulls in misaki's espeak binding.
    - `KModel(phonemes, ref_s, speed)` is called once per chunk, with `ref_s` = `pack[min(len(ps), 510) - 1]` as a `(1, 256)` tensor.
  - **`ONNX_FEEDS`:** unchanged in shape (`[[0, *ids, 0]]`, style `len(input_ids) - 1` clamped, speed). Both formats now read the style row from the MEU-73 `VOICE_PACK` `.bin` beside the vocab, not from `KPipeline.load_single_voice`.
  - **Empty input:** empty phonemes produce `on_progress(1.0)` and zero samples (AC-72.3).
  - **`KPipeline` is gone:** no import of it remains anywhere in `avkit_infra`.
- **`SPEC_BUNDLE` (`packaging/avkit-backend.spec`):**
  - `hiddenimports` adds onnxruntime, spacy, misaki (with `misaki.data`, `misaki.en` and `misaki.token`), num2words and its submodules, `avkit_infra.tts.g2p` and `avkit_infra.tts.espeak`.
  - `datas` is `collect_data_files("misaki")`.
  - `module_collection_mode={"num2words": "py"}` keeps num2words as replaceable source (LGPL-2.1).
  - `excludes` adds kokoro, phonemizer, espeakng_loader and `misaki.espeak`.
- **`NOTICES` (`packaging/THIRD_PARTY_NOTICES.md`, new):**
  - **Components and licences:** misaki (Apache-2.0, with the ported `MULTI_E2M`/`EN_E2M` tables named), num2words (LGPL-2.1, with replacement instructions), spaCy (MIT), onnxruntime (MIT), the downloaded Kokoro-82M weights (Apache-2.0), and FFmpeg (GPL-3.0, D-87: the `n8.1.2-44-g7c533d0f86` BtbN build, its source URLs and the shipped `resources/ffmpeg/LICENSE.txt`).
  - **Not shipped:** eSpeak NG, PyTorch and kokoro.
  - **Appendix:** the full LGPL-2.1 text.
  - **Installer:** `electron-builder.yml` copies the file to `resources/THIRD_PARTY_NOTICES.md`.
- **`fetch_ffmpeg_windows.ps1` (D-87):** after the binary check, it copies the archive's shallowest `LICENSE.txt` to `-OutDir`. If the archive has no `LICENSE.txt`, it removes the stage and exits 6.
- **Dependencies:** `misaki[en]==0.9.4` and `num2words==0.5.14` are pinned directly in `packages/infrastructure/pyproject.toml`. Both were already in `uv.lock` through kokoro, so the lock diff is 4 lines.
- **`PACKAGE_SMOKE` (`tools/smoke_packaged_tts.py`, new; gate `package-smoke`):**
  - **`ONLINE_PROVISION`:** builds the real onedir (never `--stub-ok`) and provisions a models dir through the frozen backend.
  - **`INSTALLER_STAGE`:** `npm run dist`, the NSIS size cap, the NOTICES and FFmpeg licence staging, and `MCP_ENTRY_PROBE`.
  - **`OFFLINE_SMOKE`:** the copied backend, outside the worktree, behind a dead proxy, generates one English WAV.
  - **`NEGATIVE_PROBE`:** a voice-pack download into an empty dir must fail.
- **Test amendments applied:**
  - **TA-2** (`test_tts_models.py`): AC-9.6, AC-9.7 and AC-9.13 run through the G2P seam. `FakeKModel` gains `forward_calls` and `__call__`. `_patch_engines` stubs `kokoro.KModel` and swaps `KokoroG2p` for `FakeG2p`. `FakeKPipeline` is deleted.
  - **TA-3b** (`test_tts_assets.py`): AC-62.9 counts G2P requests on the seam fake. `_ResultLike` and `test_ac_62_16_pipeline_result_objects_carry_phonemes_and_audio` are **deleted** (baseline 770–839, walkthrough §Execution amendments, Row 9). That test's intent, that real phoneme ids reach the model and not pad tokens only, is now asserted exactly by AC-72.4.
  - `ta-check` enforces both.

**Build Plan Section**: `docs/build-plan/07-*` §"ONNX without torch", "Bundle", "Smoke"; `03-*` §TTS language runtime (G2P). Row 13 reconciles the hub.
**Predecessor**: MEU-74. It supplies `EspeakCliAdapter`, `ESPEAK_G2P`, `ESPEAK_EN_FALLBACK` and the maps. MEU-73 supplies `VOICE_PACK` and the voice-pack asset that both engines now read.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-72.1 | integration | `IMPORT_HYGIENE`: a fresh interpreter with torch, kokoro, phonemizer and espeakng_loader blocked imports the adapter and the real `misaki.en`. English and Spanish ONNX generates yield finite float32 in [-1, 1], with progress ending at 1.0. | Spec 07 "ONNX without torch"; D-71 | `tests/integration/test_tts_no_torch.py:112` | ✅ |
| AC-72.2 | unit | `G2P_ROUTE`: the English fallback only with eSpeak NG; e/f/h/i/p via `ESPEAK_G2P` + `MULTI_E2M`; j/z `ValidationError`; a missing spaCy model gives a 409 before the factory runs; misaki built once per `british` flag | D-71, D-72 | `tests/unit/test_tts_g2p.py:84`, `:111`, `:131`, `:145`, `:165` | ✅ |
| AC-72.3 | unit | `CHUNK_RULE`: non-empty, ≤ 510, order kept; sentence > clause > space; a 2,000-symbol run splits hard at 510; empty → no chunks, and generate returns empty audio with progress 1.0 | Local Canon `adapter.py:228-229`; D-78 | `test_tts_g2p.py:188`, `:196`, `:223`, `:236` | ✅ |
| AC-72.4 | unit | `ONNX_FEEDS` on a recording session: dtypes and shapes, `[[0,*ids,0]]`, style row `len(ids)-1` clamped, unknown symbols dropped, one `session.run` per chunk, real phoneme ids | Existing adapter contract; TA-3b intent | `tests/integration/test_tts_models.py:698` | ✅ |
| AC-72.5 | unit | `TORCH_PATH`: a stub `KModel` is called once per chunk with the phoneme string and a `(1,256)` style; `"kokoro.pipeline" not in sys.modules` | D-75 | `test_tts_models.py:758` | ✅ |
| AC-72.6 | unit | `SPEC_BUNDLE` parsed from the spec AST: excludes, hiddenimports, the datas call and `module_collection_mode` present; no weights, voices, spaCy model or espeak in datas | Spec 07 "Bundle" | `tests/unit/test_packaging_backend.py:263` | ✅ |
| AC-72.7 | unit | `NOTICES`: six components and licences, the LGPL-2.1 text, FFmpeg GPL-3.0 with its source URL and `resources/ffmpeg/LICENSE.txt`, eSpeak NG not shipped; `electron-builder.yml` copies it; the fetch script exits 6 without `LICENSE.txt` and copies it when present | D-76, D-87 | `tests/unit/test_packaging_installer.py:207`, `:268`, `:276` | ✅ |
| AC-72.8 | integration | `PACKAGE_SMOKE` passes with all required result fields | Spec 07 "Smoke" | `validate-task.ps1 -Check package-smoke`; `package-smoke-result.json` | ✅ online `passed`, `forbidden_dirs: []`; offline `passed`, `wav_samples` 41,400, `negative_probe.state` `Failed`, `backend_dir` `C:/temp/av-kit/s32-smoke-run/avkit-backend`, proxies set; identity `7925c50c…` at start and end. H1-2 binds it to the `windows-gate` identity. |
| AC-72.9 | integration | `INSTALLER_STAGE`: `npm run dist` 0, `assert-nsis-pack.ps1` passes, `notices_staged` and `ffmpeg_license_staged` true; `MCP_ENTRY_PROBE` recorded | Spec 07 "Smoke"; triage D-41 | same | ✅ installer 475,704,219 bytes (< 500 MB); both staged; MCP probe `unreachable` (H2-2 copies it into `MCP-PACKAGED-ENTRY-UNREACHABLE`) |

### Other plan AC references (not owned by MEU-72)

| AC | Owner | Status in MEU-72 |
|----|-------|------------------|
| AC-9.6, AC-9.7, AC-9.13 | existing `test_tts_models.py` (MEU-9) | pass with TA-2 (`:464`, `:515`, `:659`). AC-9.13's new tail expects two `session.run` feeds of 510 and 1 symbols, which needs `CHUNK_RULE`. |
| AC-62.9 | existing `test_tts_assets.py` (MEU-62) | pass with TA-3b. "No new G2P request" replaces "no new `KPipeline`". |
| AC-62.16 | existing `test_tts_assets.py` (MEU-62) | **deleted** by TA-3b. Its intent is in AC-72.4. |
| AC-24.9, AC-24.10, AC-25.10 | existing packaging tests | pass. AC-24.9 reads the `excludes=` literal through `ast`, so the list stays inline in `Analysis(...)`. AC-24.10 and AC-25.10 failed in the row-0 baseline for lack of a built onedir and FFmpeg, and pass after the row 9 provisioning. |
| AC-2.x | existing `test_domain.py` (MEU-2) | untouched. `VoiceConfig` keeps five fields (D-89); pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`) |
| AC-16.7 | existing `test_api_tts_models.py` (MEU-16) | untouched by MEU-72; pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`). TA-14 (D-95, MEU-74) adds `available`/`reason` to the expected voice dict. |
| AC-23.20 | existing `gui-actions-audit.test.ts` (MEU-23) | untouched by MEU-72; pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`). D-100 (row 13) adds no gui-actions-index row, because this audit cannot resolve a `writeClipboardText` settings cell. |
| AC-74.11 | MEU-74 handoff | **unverified**. eSpeak NG is not installed on this machine (walkthrough §LOCAL-ESPEAK). |
| AC-73.x, AC-74.x | MEU-73, MEU-74 handoffs | pass. `PY73`, `REG73` and `PY74` are inside `green-72` and `gate72`. |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-72.3 empty audio | today's adapter returns 2 samples for empty phonemes, where 0 are expected | pass | `test_tts_g2p.py:236` |
| AC-72.6 | the spec's `excludes` lack kokoro, phonemizer, espeakng_loader and `misaki.espeak` | pass | `test_packaging_backend.py:263` |
| AC-72.7 (3) | no `THIRD_PARTY_NOTICES.md`; the fetch script exits 0 without `LICENSE.txt` and never copies it | pass | `test_packaging_installer.py:207`, `:268`, `:276` |
| AC-72.1, 72.2 (5), 72.3 (3), 72.4, 72.5 | declared-symbol import errors (`avkit_infra.tts.g2p`); AC-72.1's subprocess stderr is the same `ModuleNotFoundError` | pass | see AC table |
| AC-9.13 (TA-2) | the adapter raises `ValidationError` at the 510 limit instead of cutting | pass | `test_tts_models.py:659` |

Red, the Green design notes and the package smoke are in [walkthrough.md](../../../docs/execution/plans/2026-10-14-tts-engine-runtime/walkthrough.md) §MEU-72 Red, §MEU-72 Green and §MEU-72 Package smoke.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s32-72-red","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check red-72 > C:/Temp/av-kit/s32-red-72-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"PY72 pytest","phase":"red","exit_code":0,"result":"pass","tested_state":"MEU-74 tree + MEU-72 tests and TA-2/TA-3b edits only; no MEU-72 production edit","output":"17 failed, 53 passed | PASS red-72 pytest: 5 decisive AC assertions, 11 declared-symbol import errors, TEST_AMENDMENTS-file failures (disposition in walkthrough): ['tests.integration.test_tts_models::test_ac_9_13_missing_vocab_voice_and_input_limit'] | PASS red-72","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-72-green","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check green-72 > C:/Temp/av-kit/s32-green-72-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"PY72 + PY74 + PY73 + REG73 pytest","phase":"green","exit_code":0,"result":"pass","tested_state":"MEU-72 implementation on base c72fc44 + MEU-73 + MEU-74","output":"294 passed | PASS pytest s32-green-72-pytest: 294 passed; baseline failures tolerated: [] | PASS green-72","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-72-gate","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check gate72 > C:/Temp/av-kit/s32-gate72-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"py lint and types, ui/mcp types, ui lint, uv lock check, PY72+PY74+PY73+REG73 pytest, full ui Vitest, OpenAPI check, ta-check","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-72 working tree after Green","output":"PASS pytest s32-gate72-pytest: 294 passed; baseline failures tolerated: [] | PASS s32-gate72-ui: 816 passed of 816 | PASS ta-check: 15 TEST_AMENDMENTS rows (TA-1..TA-14), base c72fc44 | PASS gate72","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-72-package-smoke","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check package-smoke > C:/Temp/av-kit/s32-row12-smoke-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"ONLINE_PROVISION, INSTALLER_STAGE, MCP_ENTRY_PROBE, OFFLINE_SMOKE, NEGATIVE_PROBE","phase":"integration","exit_code":0,"result":"pass","tested_state":"MEU-72 final working tree, WORKTREE_IDENTITY 7925c50c04c74fe1ebd6dd9ba94fdc4632d2e3326afeed4a0d576278e8764279 at start and end","output":"PASS PACKAGE_SMOKE: ONLINE_PROVISION + INSTALLER_STAGE + OFFLINE_SMOKE (MCP probe: unreachable)","fresh":true}
```

Attempt 1 of `package-smoke` failed in `OFFLINE_SMOKE` (a load 500, plus the spaCy model read from the real home folder). Attempt 2, above, passed after three fixes to the smoke harness, with no product change (walkthrough §Execution amendments, Row 12).

The full Python suite was run outside the gate: 803 passed, 0 failed (`C:/Temp/av-kit/s32-r10-full-pytest.txt`). The authoritative full gate is `WINDOWS_GATE` (H1-2).

**Authoritative gate (H1-2, attempt 2).** `windows-gate-result.json` and `package-smoke-result.json` are bound to one `WORKTREE_IDENTITY` (`cd879e6e…`). Attempt 1 missed `AC-63.5` and `AC-49.28` under host load; both passed 10/10 alone, with no file changed between attempts (walkthrough §Windows gate).

```json
{"schema_version": "evidence.v1", "check_id": "s32-h1-windows-gate", "command": "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check windows-gate, then -Check package-smoke, then -Check windows-gate-check (H1-2; log C:/Temp/av-kit/s32-h1-gate-run.txt)", "cwd": "P:/av-kit-wt/tts-engine-runtime", "scope": "17 PROFILE D6 stages (full pytest, full Vitest, full Electron E2E, types, lint, builds, OpenAPI, SSOT render), PACKAGE_SMOKE, and the binding check", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "Session 32 final working tree on HEAD c72fc44, WORKTREE_IDENTITY cd879e6ef3f5f16a7266c0a66afbf19f284baa6863bc2fa17c1bc599f2611e18 at start and end of the gate and the smoke", "output": "PASS WINDOWS_GATE (17/17; pytest 803/0, Vitest 816/816, Electron 138/0/0/0 flaky 0) | PASS PACKAGE_SMOKE (offline 41,400 samples, negative probe Failed, MCP probe unreachable) | PASS windows gate + package smoke @ cd879e6ef3f5", "fresh": true}
```

### Package smoke result (`package-smoke-result.json`)

Row 12 values below. The H1-2 rerun (identity `cd879e6e…`) matches them: exe 27,032,476 bytes, installer 475,703,896 bytes, 41,400 samples offline, negative probe `Failed`, MCP `unreachable`.

```
online:  build exit 0 in 34.0 s; exe 27,032,476 bytes; forbidden_dirs []; spaCy downloaded into the smoke models dir
         (fresh HOME); variant/vocab/voice packs already provisioned; all three assets ready
install: dist exit 0; nsis assert exit 0; installer 475,704,219 bytes (< 500 MB); notices_staged true;
         ffmpeg_license_staged true
mcp:     unreachable, exit 1 in 0.11 s: ERR_MODULE_NOT_FOUND '@modelcontextprotocol/sdk'
         (resources/mcp-server has no node_modules)
offline: backend_dir C:/temp/av-kit/s32-smoke-run/avkit-backend (outside the worktree); proxies http://127.0.0.1:9;
         register downloaded; generate Done in 1.9 s; 41,400 samples @ 24 kHz inside out/
negative: Failed: "voice pack af_heart download failed: An error happened while trying to locate the file on the Hub…"
```

### Quality Gate Results

```
pyright packages/: 0 errors
ruff check packages/ tests/ tools/smoke_packaged_tts.py: clean (ruff format drift in one adapter.py call is pre-existing at c72fc44, not gated)
pytest PY72 + PY74 + PY73 + REG73: 294 passed
full Python suite: 803 passed, 0 failed
ui Vitest full: 816/816
OpenAPI: --check passes (MEU-72 adds no wire change)
ta-check: 15 TA rows (TA-1..TA-14), base c72fc44
package-smoke: PASS (attempt 2)
```

---

## Changed Files

Line counts are cumulative since `c72fc44`. Where an earlier MEU touched the same file, the counts include it.

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/infrastructure/src/avkit_infra/tts/g2p.py` | new | 1–116 | `KokoroG2p` (`G2P_ROUTE`), `split_phonemes` (`CHUNK_RULE`), `MAX_PHONEMES`, `SPACY_MODEL` |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | +96/−68 | the `KPipeline` removal; `g2p=` injection; `_phoneme_chunks`, `_torch_chunk`, `_voice_pack`; the lazy `KModel` import |
| `packaging/avkit-backend.spec` | modified | +32/−2 | `SPEC_BUNDLE` |
| `packaging/THIRD_PARTY_NOTICES.md` | new | 1–218 | `NOTICES` |
| `ui/electron-builder.yml` | modified | +3 | stages the NOTICES file |
| `tools/fetch_ffmpeg_windows.ps1` | modified | +12 | copies `LICENSE.txt`; exit 6 without it |
| `packages/infrastructure/pyproject.toml`, `uv.lock` | modified | +2; +4 | direct pins for misaki[en] and num2words (CRLF kept) |
| `tools/smoke_packaged_tts.py` | new | 1–434 | `PACKAGE_SMOKE` online and offline phases |
| `tests/tts_g2p_fakes.py` | new | 1–128 | `FakeG2p`, `set_phonemes`, `g2p_lang_codes`, `G2pSeam` (`G2P_SEAM`) |
| `tests/integration/test_tts_no_torch.py`, `tests/unit/test_tts_g2p.py` | new | 1–132; 1–261 | AC-72.1; AC-72.2 and AC-72.3 |
| `tests/integration/test_tts_models.py` | modified | +204/−55 | TA-2 and the seam switch; AC-72.4 and AC-72.5 appended |
| `tests/integration/test_tts_assets.py` | modified | +83/−86 | TA-3b (plus MEU-73's TA-3a) |
| `tests/unit/test_packaging_backend.py`, `test_packaging_installer.py` | modified | +82; +112 | AC-72.6; AC-72.7 (append only) |

```diff
+        chunks = self._phoneme_chunks(text, lang_code)
+        total = len(chunks)
+        if total == 0:
             on_progress(1.0)
             return np.array([], dtype=np.float32)
+        pieces: list[np.ndarray] = []
+        if session is not None:
+            for index, chunk in enumerate(chunks, start=1):
+                pieces.append(self._onnx_chunk(chunk, voice, speed, session))
+                on_progress(index / total)
+        else:
+            pack = self._voice_pack(voice.voice_id)
+            for index, chunk in enumerate(chunks, start=1):
+                pieces.append(self._torch_chunk(chunk, pack, speed))
+                on_progress(index / total)
         return np.concatenate(pieces)
```

```diff
+        # misaki's `G2P.__init__` would otherwise run `spacy.cli.download`, a network install.
+        if not spacy.util.is_package(SPACY_MODEL):
+            raise ConflictError("tts asset missing: tts_spacy_model")
+        factory = self._misaki_factory or _misaki_g2p_class()
+        fallback = self._espeak.en_fallback(british) if self._espeak.status().available else None
+        built = factory(trf=False, british=british, fallback=fallback, unk="")
```

---

## Codex Validation Report

_Left blank for the reviewer agent, which fills this section during `/validation-review`._

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

**New issue candidates for H2-2.** All were found during MEU-72 and all are outside its Files Modified or AC fence:

- **The FFmpeg pin URL returns 404.** BtbN no longer publishes `autobuild-2026-08-24-13-10` (checked 2026-10-15). A fresh checkout cannot run `fetch_ffmpeg_windows.ps1`. This worktree used a cached archive whose SHA matches the pin, through `-ExtractOnly`.
- **The installer ships the 168 MB `ffmpeg-pin.zip`.**
  - The fetch script downloads the archive into `-OutDir` (`tools/fetch_ffmpeg_windows.ps1:22`, unchanged since baseline) and never removes it.
  - `electron-builder.yml` copies the whole `packaging/ffmpeg-win64` folder, so `resources/ffmpeg/ffmpeg-pin.zip` is in `win-unpacked`.
  - The 475.7 MB size-cap pass includes it, so the cap check is conservative.
  - Likely fix: delete the archive after extraction, or filter it in `extraResources`.
- **A sideloaded variant is listed but cannot load.** With a fresh app-data and a provisioned models dir, `/models/downloaded` reports `kokoro-onnx-int8` through the sideload union. `POST /models/load` then fails with `ModelLoadError("model weight file is missing")` (the DB row's `path` is `None`). That surfaces as a 500 `internal_error`, with no log line at uvicorn's `warning` level. The behaviour predates this plan. The smoke registers through the download fast path first.
- **A stale spaCy `sys.path` entry survives a `models_directory` change.** At startup, the default `~/.avkit/models/spacy/...` is put on `sys.path`, and a later `PUT models_directory` does not remove it. The spaCy model then reads as ready from the old folder. It is the same mechanism as the Row 8 test leak.
- **`fetch_ffmpeg_windows.ps1` exit codes 2, 3 and 4 are never returned.** Their `Write-Error` throws under `$ErrorActionPreference = 'Stop'`, so the process exits 1 first. The tests only check for a nonzero exit. The new exit-6 path avoids the problem with `[Console]::Error.WriteLine`.
- **NOTICES omits spaCy's transitive MIT/BSD dependencies** (thinc, srsly, cymem, preshed, murmurhash, wasabi, catalogue, langcodes and others), which also ship in `_internal`.

**Notes for the reviewer (no action proposed):**

- **Style index:** the torch path indexes the style row by phoneme-string length (as kokoro does). ONNX indexes it by `len(input_ids)` after unknown symbols are dropped. They differ only when a chunk holds symbols the vocab lacks.
- **The English G2P is cached per `british` flag with the fallback it was built with.** If eSpeak NG is installed while the backend runs, English keeps no fallback until a restart. Spanish and the other eSpeak NG languages pick up the install at once (MEU-74's detection cache).
- **AC-74.11 LOCAL-ESPEAK is unverified.** eSpeak NG is not installed here. H2-2 files the issue the plan requires.
- **`MCP_ENTRY_PROBE` is `unreachable`.** H2-2 records it in `MCP-PACKAGED-ENTRY-UNREACHABLE` (`unreachable` → `open`).
- **Done vs Completed:** the plan says a TTS job "polls to Completed", but the real success value of `TTSStatus` is `Done`. The smoke waits for `Done`, and only the plan's wording is corrected.

---

## Decision Log

```yaml
decision_log: []
```

MEU-72 made no new execution decisions. It implements the plan's D-71, D-72, D-75, D-76, D-78 and D-87 as written. The deviations that needed recording are walkthrough amendments, because none changes an assertion, an expected value or the plan's design:

- the TA-3b range `770-839` (Row 9);
- the environment provisioning for `red-72`, including the FFmpeg 404 (Row 9);
- the inline `excludes` that AC-24.9 requires (§MEU-72 Green);
- the `FakeKModel.__call__` placement (§MEU-72 Green);
- the smoke harness fixes (Row 12).

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-15 | claude-code | Initial handoff after gate72 and package-smoke (attempt 2) |
| Reconciled | 2026-10-15 | claude-code | H1-5: added the authoritative H1-2 gate record (`WINDOWS_GATE` 17/17 + `PACKAGE_SMOKE` @ `cd879e6e`) |
