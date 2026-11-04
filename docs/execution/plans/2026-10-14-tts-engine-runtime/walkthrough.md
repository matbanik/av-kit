# Walkthrough — 2026-10-14-tts-engine-runtime (Session 32)

Durable evidence for `task.md`. Receipts are working data under `C:/Temp/av-kit/`. The decisive lines are copied here as `evidence.v1`.

## Execution authorization

- **USER_EXPLICIT, 2026-10-15.** Mat sent this in the Claude Code chat after the Codex plan review returned `approved` (round 3, [plan review](../../../../.agent/context/handoffs/2026-10-14-tts-engine-runtime-plan-critical-review.md)):

  > proceed

- **Gate:** under Claude Code, `plan_to_exec_gate` is `human` (`.agent/context/harness.local.md` §Claude Code; `GUARDRAILS.md` SIGN 1). This message satisfies it.
- **Context Tool Decision, execution phase:** re-evaluated 2026-10-15. The decision is `not_applicable`, so it needs no human answer.
  - **Graphify / Graphify Research:** `graphify-out/` and `graphify-out-research/` are absent in the worktree. `prereq` re-checks this.
  - **Headroom: correction to the planning record.** The planning basis said "no headroom on PATH". That was wrong: `headroom` 0.24.0 is installed at `C:/Users/Mat/AppData/Roaming/Python/Python313/Scripts/headroom`.
  - Headroom is still not eligible, for two reasons (`.agent/docs/context-tool-decision-gate.md` §Eligibility inventory):
    - The repository has no active, approved Headroom disposition. The only "pilot" mention is in the gate document itself.
    - This execution's payloads are source code, test output and exact evidence, which are all bypass classes.
  - No `user-headroom` MCP tool is exposed in this session.

## Baseline

```yaml
evidence.v1:
  command: "validate-task.ps1 -Check prereq *> C:/Temp/av-kit/s32-row0-run.txt; then -Check baseline *>> the same receipt"
  exit: 0
  scope: row 0 (plan review, MEU state, deps, Electron, context-tool re-check, pre-edit baseline)
  tested_state: "baseline.sha 78610200ea2e7efd52318ea95c3e48b6df4993ba (main @ 7861020, clean product tree)"
  decisive_output:
    - "PASS plan review approved round 3 by gpt-6.1-sol"
    - "PASS MEU state {'MEU-73': 'pending', 'MEU-74': 'pending', 'MEU-72': 'pending', 'MEU-24': 'approved', 'MEU-62': 'approved', 'MEU-64': 'approved'}"
    - "PASS prereq"
    - "pytest: 2 failed, 653 passed, 1 warning in 81.97s"
    - "PASS s32-baseline-vitest: 772 passed of 773; baseline failures tolerated: 1"
    - "PASS s32-baseline-mcp: 411 passed of 411; baseline failures tolerated: 0"
    - "PASS s32-baseline-e2e: 129 passed; baseline failures tolerated: 4"
    - "PASS baseline @ 78610200ea2e7efd52318ea95c3e48b6df4993ba"
```

Baseline failures are recorded here and not fixed:

- **pytest (2), environment-bound:**
  - `test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]` fails because there is no PyInstaller `dist/`.
  - `test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]` fails because `packaging/ffmpeg-win64/ffmpeg.exe` is missing.
  - Row 12 `PACKAGE_SMOKE` builds `dist/` and fetches FFmpeg, so both should pass in the H1-2 gate.
- **Vitest (1), external drift:** `queue-canon.test.ts` "AC-41.3 both themes declare the ported status tokens with Zorivest hexes" fails with expected `'#0891b2'` to be `'#0e7490'`.
  - The test reads `P:/zorivest/ui/src/renderer/src/globals.css`, which Zorivest commit `7b73b5b7` (2026-10-14, MEU-661) changed.
  - Earlier sessions recorded AC-41.3 as environment-bound when `P:/zorivest` was absent. This time it is a token change in another repository, outside `PRODUCT_SCOPE`.
  - `windows-gate-check` requires Vitest `failed 0`. If the drift is still present at H1-2, it becomes a human decision there.
- **Electron (4), environment-bound:** the four `capture-picker.test.ts` specs fail because `native/region-picker-stub/publish/avkit-region-picker-stub.exe` is not built. Session 30 recorded the same four.
- **Environment:** the worktree `.venv` is CPython 3.12.12, recreated with `uv venv --python 3.12.12` (`C:/Temp/av-kit/s32-venv-312.txt`) because uv first resolved a cp314 interpreter. `uv sync --all-packages --frozen` then installed from the unchanged `uv.lock`.

## Census

```yaml
evidence.v1:
  command: "validate-task.ps1 -Check census *> C:/Temp/av-kit/s32-census-run.txt"
  exit: 0
  scope: row 1 (TEST_AMENDMENTS census over tests, ui/tests, mcp-server/tests; 32 fixed-string patterns)
  tested_state: "baseline.sha 78610200ea2e7efd52318ea95c3e48b6df4993ba, no product edits"
  decisive_output:
    - "PASS census: 260 hits in C:/Temp/av-kit/s32-census.txt"
```

The receipt has 260 lines: 259 hits plus one `[rtk]` banner. Every hit is listed below by file and line.

### `tests/integration/test_tts_models.py` (40 hits)

| Lines | Disposition | Reason |
|---|---|---|
| 64-68 | TA-1 | `HF_FILE_MAP_EXPECTED` ONNX rows move to `ONNX_REPO`. |
| 226, 235, 243, 272-276, 285 | TA-2 | The `FakeKPipeline` class, `_reset_fakes` and `_patch_engines`, all within 226-285. |
| 501 | TA-2 | Within 495-505 (`test_ac_9_6` phonemes). |
| 522, 534-538 | TA-2 | Within 525-540 (the kwargs test). Line 522 is its `def` line, which stays unchanged. |
| 682, 687, 688 | TA-2 | Within 670-691. The voice error case (682) changes at row 2 and the 511-symbol case (687-688) at row 9. |
| 30 | unaffected | `TTS_PORT_METHODS`: `TTSPort` gains no method. `EspeakPort` is a separate port. |
| 202, 350-360 | unaffected | `VoiceConfig` lang codes and the catalog voice list are unchanged. |
| 394, 460, 483, 555, 562, 564, 583, 604 | unaffected | PyTorch `.pth` paths. The PyTorch `HF_FILE_MAP` row and its local path stay the same. Line 604 lies inside TA-13's range, but its `.pth` write is unchanged; only the ONNX sideload files move. |
| 547, 550 | unaffected | The import, and `HF_FILE_MAP == HF_FILE_MAP_EXPECTED`. The equality is unchanged; TA-1 changes the expected constant. |
| 571 | unaffected | "no `.bin` in `HF_FILE_MAP`" stays true, because voice packs come from `voice_packs.py` and not from `HF_FILE_MAP`. |
| 693 | unaffected | The `catalog.py` scan. `catalog.py` is not modified (plan, TEST_AMENDMENTS note). |

### `tests/integration/test_tts_assets.py` (61 hits)

| Lines | Disposition | Reason |
|---|---|---|
| 25 | TA-3b | Imports `FakeKPipeline` (row 9). |
| 564, 574 | TA-3b | `FakeKPipeline.calls` counts, within 556-582 (row 9). |
| 568, 571 | TA-9 | Within 568-582. The 409 messages are unchanged; only the voice changes (row 5). |
| 773, 815, 820, 834 | TA-3b | The `KPipeline.Result` test, 772-839 (row 9). |
| 164, 166 | TA-12 | The `put_weights` path. |
| 239, 240, 244, 249, 251, 252, 254, 255 | TA-11 | The `TtsAsset` value list and the `required_tts_assets` tuples. |
| 257 | unaffected | The unknown-voice `ValidationError` case (TA-11 says 256-257 stay unchanged). |
| 603 | TA-3a | `raise_voice` becomes a `FakeSession.run` that raises. |
| 669, 670, 671, 675, 676, 677, 681, 691 | TA-8 | The count assertions are unchanged. AC-73.12 adds the position assertion in a new test. |
| 666 | unaffected | The import line of the TA-8 test. |
| 5 | unaffected | Module docstring prose about the patched engines. It is not an assertion. |
| 93, 103, 104 | unaffected | The fixture restores the whole `sys.path` list, so it is independent of position. |
| 182 | unaffected | The `deps()` helper reads the JSON body. A new row is additive. |
| 222, 365-479 (17 lines) | unaffected | The spaCy download flow is keyed by `tts_spacy_model`, which stays a valid wire. Each read uses `.get(<key>)`. |
| 314 | unaffected | `ASSET_409_ORDER` keeps `ONNX_VOCAB` first, so the missing-vocab 409 still names `tts_onnx_vocab`. |
| 350 | unaffected | `VoiceConfig(lang_code="a")` construction. |
| 520, 521, 524, 526, 527, 531 | unaffected | Fresh and busy deps rows, read by key. The `tts_voice_packs` row is additive. |
| 731, 733, 753, 756 | unaffected | Download-body validation. `tts_spacy_model` stays valid, and the bad bodies stay bad. |

### Other Python files

| File:lines | Disposition | Reason |
|---|---|---|
| `tests/e2e/test_api_health_settings.py:49-50` | TA-4 | `dependencies()` fake. It gains `tts_voice_packs` (row 2) and `tts_espeak` (row 5) as added lines. |
| `tests/e2e/test_api_health_settings.py:158` | unaffected | The test asserts only the `yt_dlp` and `ffmpeg` keys. |
| `tests/e2e/test_api_auth.py:63-64` | TA-4 | As above. |
| `tests/e2e/test_api_auth.py:138-178` (7) | unaffected | Auth checks on the route. The route is unchanged. |
| `tests/e2e/api_fakes.py:69-70` | TA-4 | As above. The whole file is in TA-4. |
| `tests/e2e/api_fakes.py:237, 266, 267, 271` | unaffected | The `list_voices` fake builds `VoiceConfig` rows with the existing fields. |
| `tests/e2e/test_api_tts_models.py:150-167` (5) | TA-14 (corrected at row 5) | Row 1 marked this unaffected because of the `lang_code` ban, but lines 156-161 also assert the exact four-key row, which AC-74.3's `available`/`reason` breaks. Re-briefed under S2 at row 5; see §Census S2b. |
| `tests/e2e/test_api_openapi.py:72, 85, 125, 126` | unaffected | Route inventory. No route is added or removed. |
| `tests/tts_asset_fakes.py:3-33` (8) | unaffected | The states come from `for asset in TtsAsset`, so `VOICE_PACKS` defaults to `ready`. |
| `tests/conftest.py:23-33` (4) | unaffected | The whole-list `sys.path` restore is independent of position. |
| `tests/unit/test_services.py:1558, 1605` | unaffected | A `VoiceConfig` construction and a port-fake `list_voices`. |
| `tests/unit/test_tts_voice_fixture.py:3, 5, 16` | TA-7 | The fixture-row parity (row 5). |
| `tests/unit/test_packaging_backend.py:13, 76, 187-208` (7) | unaffected | The spec path, the datas token ban (`.onnx`, `.pth`), and "torch in excludes / not in hiddenimports". `SPEC_BUNDLE` is a superset: it still excludes torch and adds no torch import. |
| `tests/unit/test_packaging_installer.py:86, 90` | unaffected | "no `.pth` in `extraResources`" stays true. Only `THIRD_PARTY_NOTICES.md` is added. |
| `tests/unit/test_domain_capture.py:127` | unaffected | A substring match on "excludes" in an unrelated test name. |
| `tests/unit/test_domain.py:557, 562, 566, 574` | unaffected | `VoiceConfig` constructions and the prefix rule. |
| `tests/unit/test_domain.py:1152` | unaffected | `TTS_PORT_METHODS`: `TTSPort` is unchanged. |
| **`tests/unit/test_domain.py:324`** | **new-contradiction** | `SPEC_VOICE_CONFIG_FIELDS` is the exact 5-field tuple, asserted by `test_ac_2_10` (553-554) and `test_ac_2_12` (607-610). The MEU-74 Files Modified row for `domain/tts.py` adds `VoiceConfig.available` and `reason`, which would break both. This file is not in `TEST_AMENDMENTS`. **Stop condition S2**; see §Census S2 below. |

### `ui/tests` and `mcp-server/tests`

| File:lines | Disposition | Reason |
|---|---|---|
| `ui/tests/unit/settings-page.test.ts:763-764, 836-837` | TA-5 | The fixture gains `tts_voice_packs` (row 2) and `tts_espeak` (row 5). The absent-rows case asserts the new row is absent. |
| `ui/tests/unit/settings-page.test.ts:171-603` (6), `774-830` (12) | unaffected | Route mocks, and the spaCy row's Get/Downloading behaviour, keyed by `tts_spacy_model`. |
| `ui/tests/unit/tts-page.behavior.test.ts:119-120` | unaffected | The deps fixture has two rows. `presentAssetRows` (`tts-assets.ts`) renders only the rows present, so a missing `tts_voice_packs` renders no chip. |
| `ui/tests/unit/tts-page.behavior.test.ts:142, 160, 548-579` (13) | unaffected | Route mocks, and the spaCy chip and Get flow. |
| `ui/tests/e2e/tts-generate.test.ts:56-57` | unaffected | Same reason as `presentAssetRows` above. |
| `ui/tests/e2e/tts-generate.test.ts:10, 136, 159, 201, 546, 588, 589, 605` | unaffected | The fixture load (TA-7 adds fields only), route seams, the vocab chip and the error banner text. |
| `ui/tests/e2e/settings.test.ts:52-316` (9) | unaffected | A two-row fixture rendered through `presentAssetRows`, plus route seams. |
| `ui/tests/e2e/test-ids.ts:380-388` (6) | unaffected | The existing ids are kept. `NEW_TESTIDS` are additions. |
| `ui/tests/unit/voice-combobox.test.tsx:4, 12, 36, 61`; `tts-page.test.ts:160, 183, 238, 260` | unaffected | Voice rows without `available`/`reason` (plan note: optional on the renderer, absent means available) and the `lang_code` ban. |
| `ui/tests/unit/convert-page.behavior.test.ts` (5), `downloader-page.behavior.test.ts:844`, `queue-card.test.ts:570`, `settings-rail.test.tsx:95`, `gui-actions-audit.test.ts:205-206`, `tts-run-bar.test.ts:7`, `e2e/capture-inbox.test.ts` (3), `e2e/convert-queue.test.ts` (2) | unaffected | Dependency route mocks, `aria-disabled` on other components' menus, the OpenAPI route text, and the vocab error string. |
| `mcp-server/tests/models-assets.test.ts:30` | TA-6 | `it.each` gains the third wire. |
| `mcp-server/tests/models-assets.test.ts:46, 48` | unaffected | Rejected bodies stay rejected. |
| `mcp-server/tests/tools-parity.test.ts:93-125` (5), `fixtures.ts:49, 59`, `client.test.ts:27, 93` | unaffected | Route paths and the `lang_code` strip. Voice rows without the new fields are valid (plan note). |

### Census S2

- **The hit:** `tests/unit/test_domain.py:324`.
  - `test_ac_2_10_voice_config_prefix_rule` asserts `VOICE_CONFIG_FIELDS == SPEC_VOICE_CONFIG_FIELDS` and `_field_names(VoiceConfig) == VOICE_CONFIG_FIELDS`.
  - `test_ac_2_12_vo_field_inventory` asserts the same 5-tuple.
  - The MEU-74 Files Modified row for `packages/core/src/avkit_core/domain/tts.py` adds `VoiceConfig.available: bool = True` and `reason`. The plan says "no test fixture that builds one changes", which is true for constructions, but not for these field-inventory assertions.
  - MEU-73 (rows 2-4) does not touch `VoiceConfig`. The contradiction binds at row 5.
- **Disposition:** stopped per S2 and briefed to Mat (AskUserQuestion, 2026-10-15). **USER_EXPLICIT:**

  > Separate value (Recommended)

- **Resolution (D-89, plan `decision_log`):** `VoiceConfig` keeps its five fields. `domain/tts.py` adds a frozen `VoiceAvailability(available, reason)`. `TtsService.list_voices` pairs each voice with it, and `/tts/voices` maps the pair to `VoiceOut.available`/`reason`.
  - The MEU-74 Files Modified row for `domain/tts.py` now says this. The file set, the ACs and `TEST_AMENDMENTS` are unchanged.
  - `test_domain.py:324` is now **unaffected**: no field is added to `VoiceConfig`. No `new-contradiction` remains.

### Census S2b

- **The hit:** `tests/e2e/test_api_tts_models.py:156-161`. `test_ac_16_7_voices_facade_calls_public_list_voices` asserts `body["items"][0] == {voice_id, language, gender, style_description}`. AC-74.3 and spec 03 (`03-service-layer.md:451`) put `available` and `reason` on every row, so the equality fails. The file is not in `TEST_AMENDMENTS`. Row 1 dispositioned the hit as `unaffected` on the strength of the `lang_code` assertion alone, which was wrong.
- **Disposition:** found at row 5 before any MEU-74 edit; stopped per S2 and briefed to Mat (AskUserQuestion, 2026-10-15). **USER_EXPLICIT:**

  > Add TA-14 (Recommended)

- **Resolution (D-95, plan `decision_log`):** TA-14 adds `"available": True, "reason": None` to the expected dict. The facade call count, the `lang_code` ban and the route source scans are unchanged. The file is added to the MEU-74 Files Modified table, so `ta-check` and `api-scope` fence it.

### Row 5: AC-74.7 guidance link (D-96)

- **The gap:** AC-74.7 assumed an "existing external-link path". None exists: `ui/src/main/index.ts:484-489` denies `window.open` and blocks navigation, and the preload exposes only `openPath`, `showItemInFolder` and the clipboard calls.
- **Disposition:** briefed to Mat before any AC-74.7 test was written (AskUserQuestion, 2026-10-15). **USER_EXPLICIT:**

  > URL + Copy link (Recommended)

- **Resolution (D-96):** the guidance shows the URL as text with a "Copy link" button through `window.api.writeClipboardText`. AC-74.7 is reworded in the plan; the test asserts the URL text and the clipboard write.

## MEU-73 Red

`validate-task.ps1 -Check red-73` → `PASS red-73` (log `C:/Temp/av-kit/s32-red-73-run.txt`; base `c72fc44`, see §Execution amendments).

- **pytest (PY73 set):** 27 failed, 30 passed. 8 are decisive AC assertions; 16 are import errors on declared symbols (`voice_packs`, `ONNX_REPO`/`ONNX_REVISION`/`ONNX_LOCAL_DIR`, `variant_local_path`, `is_legacy_onnx_path`, `VOICE_PACKS`). The remaining 3 failures are in TEST_AMENDMENTS files, with these dispositions:
  - `test_ac_9_8_download_hf_map_returns_path_no_uow`: TA-1. `HF_FILE_MAP_EXPECTED` now names `onnx-community/Kokoro-82M-v1.0-ONNX`, while the catalog still names `Kokoro-82M-ONNX`. It goes green when the catalog repo changes in row 3.
  - `test_ac_9_13_missing_vocab_voice_and_input_limit`: TA-2. The voice case deletes the `af_heart` pack instead of making `FakeKPipeline` raise, and the adapter does not read packs yet (`DID NOT RAISE ModelLoadError`). It goes green when generate resolves `VOICE_PACK`.
  - `test_ac_62_1_required_assets_rule_and_closed_enums`: TA-11. `TtsAsset` lacks `tts_voice_packs`. It goes green when the enum and `required_tts_assets` gain `VOICE_PACKS`.
- **ui Vitest** (`settings-tts-runtime.test.ts` + `settings-page.test.ts`): 7 decisive (all of `AC-73.*` in the new file) and 24 passing. TA-5 is in the passing set: the edited `settings-page.test.ts` expectation holds before and after, by design. No TEST_AMENDMENTS pin fails.
- **mcp-server Vitest** (`models-assets.test.ts`): 2 decisive and 7 passing. TA-6's `AC-62.13 posts {asset: tts_voice_packs}` fails because the tool's `asset` enum does not yet accept the new value. It goes green when the MCP enum is extended in row 3.
- **TA-8:** the `sys.path.count(...) == 1` assertion is untouched. The position assertion lives in the new `test_ac_73_12_activation_appends_the_install_dir`, which fails decisively until `activate_spacy_dir` appends.
- **Passing on current code by design:** the TA-3a rewrite (forced failure via `FakeSession.run`), TA-4's `tts_voice_packs=READY` fake fields, and the `write_voice_packs` helper lines. These are setup, not behavior under test.
- **Receipts:** `C:/Temp/av-kit/s32-red-73-ui-vitest.json` and `C:/Temp/av-kit/s32-red-73-mcp-server-vitest.json`.

## MEU-73 Green

`validate-task.ps1 -Check green-73` (row command, through `rtk proxy`) → `PASS green-73` (log `C:/Temp/av-kit/s32-green-73-run.txt`): pytest 149 passed with no tolerated failures, ui Vitest 31/31, mcp-server build plus Vitest 20/20.

- **Full Python suite (outside the gate):** 677 passed, 2 failed. The 2 are `test_pack_dist_onedir_layout[AC-24.10]` and `test_nsis_pack_check_script[AC-25.10]`. They need a built onedir and installer, and both already fail in the row-0 baseline (`C:/Temp/av-kit/s32-baseline-pytest.txt`).
- **Static:** `pyright packages/` 0 errors. `ruff check packages/ tests/` is clean. ui and mcp-server `typecheck` and ui `lint` are clean. `ruff format --check` reports 3 changed files (`domain/tts.py`, `tts/adapter.py`, `test_tts_models.py`), but every hunk is in lines that were already unformatted at `c72fc44`. The gate does not run the formatter, so those lines are left alone.
- **OpenAPI:** regenerated with `tools/export_openapi.py -o`, and `--check` passes. The diff adds only `tts_voice_packs`: the `DependenciesOut` property and required entry, plus the three `asset` enums.
- **Design notes:**
  - **`useRefreshDependenciesOnSettle`:** it reads the runtime transition from the query cache's update stream (`QueryCache.subscribe`), not from rendered data. A first version keyed a `useEffect` on `useDownloadRuntime().data?.state`. It missed `Downloading → Failed` in about 3 of 5 runs, because two runtime results that land before React renders collapse into one render, so `Downloading` is never observed. That is a real product race, not only a test artefact. With the subscription, the AC-73.10 file passed 6/6 consecutive runs. `TTSPage.tsx` keeps its own settle effect, because it is not in the MEU-73 Files Modified table.
  - **PyTorch voice:** `KPipeline.__call__` is annotated `voice: str | None`, but `KPipeline.load_voice` returns a `torch.FloatTensor` argument unchanged (kokoro `pipeline.py:157-158`). The `(510, 1, 256)` tensor is typed `Any` at the call site, with a comment saying why.
  - **Docstring:** `tts/assets.py`'s module docstring said it "never imports ``huggingface_hub``". AC-73.3's source scan bans that literal string in `avkit_infra/tts/*.py`, so the sentence now says "the Hugging Face hub client". No test was changed for it.
  - **Voice-pack fetch:** `fetch_voice_pack` lives in `model_manager/voice_packs.py`. `TtsAssetAdapter` checks each fetched pack's size, deletes a wrong-size file and raises `ModelDownloadError` naming the voice. A missing or wrong-size pack is removed before its fetch, so a stale partial file cannot satisfy the fetch.

## MEU-74 Red

`validate-task.ps1 -Check red-74` → `PASS red-74` (log `C:/Temp/av-kit/s32-red-74-run.txt`; base `c72fc44`).

- **pytest (PY74 set):** 109 failed, 6 passed. Every failure is an import error on a declared symbol (`voice_availability`, `VoiceUnavailableReason`, `EspeakStatus`, `EspeakCliAdapter`, `avkit_infra.tts.espeak`, `MULTI_E2M`, `EN_E2M`, `ESPEAK_VOICE`). The API tests build `TTSService`/`HealthService` with `espeak=` only after `FakeEspeak` imports `EspeakStatus`, so none fails on a `TypeError`. No TEST_AMENDMENTS-file failure. The 6 passing are the four AC-73.7 API cases already in `test_api_tts_runtime.py` and `test_ac_64_6_voice_fixture_matches_production_catalog`. TA-7 changes the expected rows and the fixture together, so it holds before and after.
- **ui Vitest** (`voice-combobox.test.tsx`, `settings-tts-runtime.test.ts`, `settings-page.test.ts`): 6 decisive and 41 passing, with no TEST_AMENDMENTS pin failing. Three new `AC-74.*` tests pass on current code by design. They are regression guards:
  - available voices, with or without the new fields, still select;
  - an available selection keeps the plain chip;
  - an older backend without `tts_espeak` renders no eSpeak row.
- **Electron (`-g AC-74.9`):** 1 failing spec, at `expect(option).toHaveAttribute('aria-disabled', 'true')` (received `null`).
- **TA edits in this row:**
  - **TA-4:** `tts_espeak=SimpleNamespace(available=False, version=None, path=None)` in the three dependency fakes.
  - **TA-5:** the `settings-page.test.ts` deps fixture gains `tts_espeak` (present). The absent-rows case is unchanged.
  - **TA-7:** both fixtures gain `available: true, reason: null`.
  - **TA-9:** `ef_dora` replaces `jf_alpha`, with `EspeakCliAdapter.status` monkeypatched to present. The 409/201 expectations are unchanged.
  - **TA-14 (D-95):** the AC-16.7 dict gains `available`/`reason`.
- **Outside the Red run set:** `tests/e2e/test_api_tts_models.py` (TA-14) fails until row 6. The route still builds rows from bare `VoiceConfig`s, while `FakeTTS.list_voices` now returns pairs (§Execution amendments, Row 5).
- **New test IDs:** `TTS_ESPEAK_ROW`, `TTS_ESPEAK_GUIDANCE` and `VOICE_UNAVAILABLE_REASON` in `ui/tests/e2e/test-ids.ts` (additive). `VoiceCombobox` hardcodes `voice-unavailable-reason`, because `TTSPage.tsx` is not in Files Modified and so cannot pass a new test id down.
- **Receipts:** `C:/Temp/av-kit/s32-red-74-pytest.xml`, `s32-red-74-ui-vitest.json`, `s32-red-74-e2e.json`.

## MEU-74 Green

`validate-task.ps1 -Check green-74` (row command, through `rtk proxy`) → `PASS green-74` (log `C:/Temp/av-kit/s32-green-74-run.txt`): pytest 259 passed (PY74 + PY73 + REG73), no tolerated failures.

- **Full Python suite (outside the gate):** 786 passed, 2 failed. The 2 are the baseline packaging cases `test_pack_dist_onedir_layout[AC-24.10]` and `test_nsis_pack_check_script[AC-25.10]`, as at MEU-73 Green. `tests/e2e/test_api_tts_models.py` (TA-14) is green again now that the route maps the pairs.
- **Static:** `pyright packages/` 0 errors. `ruff check packages/ tests/` is clean. `ruff format` was applied only to the two test files new in this plan (`test_espeak_adapter.py`, `test_api_tts_runtime.py`). It changed line wrapping only: two long string constants gained parentheses, with the same values, and long signatures were split. `domain/tts.py`'s remaining format hunks (lines 63-67 and the `illegal tts transition` raise) are baseline lines, as at MEU-73 Green.
- **OpenAPI:** regenerated with `tools/export_openapi.py -o`, and `--check` passes. The diff adds `EspeakOut` (`available`, `version`, `path`), `DependenciesOut.tts_espeak` (required), and `VoiceOut.available` plus `VoiceOut.reason` (an `espeak_missing`/`language_unsupported` enum or null).
- **Decisions:** D-97 (`TtsRuntimeError` lives in `avkit_infra/tts/espeak.py`, because `domain/errors.py` is not in Files Modified) and D-98 (the parity test's `sys.modules` line became an import scan; §Execution amendments, Row 6).
- **Design notes:**
  - **Availability:** `TTSService.list_voices` pairs each `VoiceConfig` with `voice_availability(lang_code, espeak_available)` (D-89). `generate` runs the same check after the unknown-voice check and before the asset check, and raises `ConflictError("voice unavailable: <voice> (<reason>)")`, so no job row is written (`ASSET_409_ORDER`). Either service built without an `EspeakPort` treats eSpeak NG as absent.
  - **Detection:** `EspeakCliAdapter.status` resolves the executable on every call: `PATH` first, then `%ProgramFiles%` and `%ProgramFiles(x86)%` `eSpeak NG\espeak-ng.exe`. `--version` runs only for a new `(path, mtime_ns)`. A failed probe is not cached, so an install made while the app runs is seen on the next call without a restart.
  - **Wire reason:** the route maps `VoiceUnavailableReason` through a `_REASON_WIRES` dict to the `Literal` that `VoiceOut.reason` declares, the same way `routes/health.py` `_ASSET_WIRES` does. The route source still never contains the string `lang_code` (AC-16.7 scan).
  - **Upstream port:** `MULTI_E2M`, `EN_E2M` and the post-processing are ported from misaki 0.9.4 `espeak.py` (Apache-2.0), with the attribution in the module docstring. The parity test compares both tables with the installed source through `ast.literal_eval`, never by importing it.

### MEU-74 GUI (row 7)

`validate-task.ps1 -Check green-74-ui` → `PASS green-74-ui` (log `C:/Temp/av-kit/s32-green-74-ui-run.txt`): ui Vitest 47/47 (`UI74`), the UI builds, and Electron `tts-generate.test.ts` 15/15, including AC-74.9. `api-scope` passes (45 changed product files, all listed; `ta-check` clean). ui `typecheck` and `lint` are clean after D-99.

- **`VoiceCombobox`:** an unavailable voice (`available: false`) is still listed and still reachable by the arrow keys, Home and End. It is an `aria-disabled` option with `cursor-not-allowed`, and click, input Enter, option Enter and Space do not select it. It does not use `pointer-events: none`, which would make user-event throw instead of testing the guard. Each such option shows its `voice-unavailable-reason` text from `VOICE_REASON_TEXT`. An unavailable current selection renders its own warning-tone chip with the reason, because `StatusChip` takes a text label only and is outside the file set. A row without the fields is available.
- **Settings:** `tts-espeak-row` appears only when the backend sends `tts_espeak`. The chip reads "Detected" or "Not installed". When detected, the row shows the version number taken from the `--version` line, with the path as its tooltip. When absent, `tts-espeak-guidance` names the five languages and shows the releases URL as selectable text with a "Copy link" button (`window.api.writeClipboardText`, D-96). There is no Get button.

## MEU-72 Red

`validate-task.ps1 -Check red-72` (row command, through `rtk proxy`) → `PASS red-72` (log `C:/Temp/av-kit/s32-red-72-run.txt`; base `c72fc44`).

- **pytest (PY72 set):** 17 failed, 53 passed.
  - **5 decisive AC assertions:**
    - `test_ac_72_3_empty_phonemes_generate_empty_audio`: today's adapter returns 2 samples for empty phonemes, where 0 are expected.
    - AC-72.6: the spec's `excludes` lack `kokoro`, `phonemizer`, `espeakng_loader` and `misaki.espeak`.
    - The three AC-72.7 cases: there is no `THIRD_PARTY_NOTICES.md`, and the fetch script exits 0 without `LICENSE.txt` and never copies it.
  - **11 declared-symbol import errors:** the five AC-72.2 tests, three AC-72.3 tests, AC-72.4 and AC-72.5 (`avkit_infra.tts.g2p`). AC-72.1 is counted here too, because its subprocess's stderr is the same `ModuleNotFoundError`.
  - **1 TEST_AMENDMENTS-file failure:** `test_ac_9_13_missing_vocab_voice_and_input_limit` (TA-2). Its new tail sets 511 phonemes and expects two `session.run` feeds of 510 and 1 symbols. Today's adapter raises `ValidationError` on the 510 limit instead of cutting. It goes green when generate runs `CHUNK_RULE`.
- **TA-2 in `test_tts_models.py`:**
  - AC-9.6 sets its phonemes through `set_phonemes("ab")`.
  - AC-9.7 checks that the G2P, not a `KPipeline`, receives `b` for `bf_alice` (`g2p_lang_codes()`, counted from before the call).
  - AC-9.13's tail is described above.
  - `FakeKModel` gains `forward_calls` and a `__call__(phonemes, ref_s, speed)` that records the call and returns two samples. AC-72.5 does not use it; it uses its own `StubKModel`. The fake is there for the row-10 seam switch, where `_patch_engines` stubs `kokoro.KModel` with it.
- **TA-3b in `test_tts_assets.py`:** the import drops `FakeKPipeline` and adds `g2p_lang_codes`. AC-62.9 counts G2P requests on the seam fake, not `KPipeline` constructions, with the same "no new request" assertion. `_ResultLike` and `test_ac_62_16_pipeline_result_objects_carry_phonemes_and_audio` are deleted (baseline 770-839, §Execution amendments, Row 9). The deletion is for the MEU-72 handoff. The intent (the model receives real phoneme ids, not pad tokens only) is now asserted by AC-72.4's exact `input_ids`.
- **G2P_SEAM helpers (`tests/tts_g2p_fakes.py`):** `set_phonemes`, `g2p_lang_codes` and `G2pSeam.session` read the fake that `_patch_engines` installed on `avkit_infra.tts.adapter`, through `_active_g2p_fake()`. They do not import it from the test module. pytest collects `tests/integration/test_tts_models.py` as the top-level module `test_tts_models` (there is no `tests/__init__.py`, and `pythonpath` includes `.`). `from tests.integration.test_tts_models import ...` therefore loads a second copy with its own fake classes. A first version imported `FakeKPipeline` that way, and AC-9.7 failed with `assert []`, because the calls were recorded on the other copy. Today `_active_g2p_fake()` returns `adapter_mod.KPipeline`. Row 10's seam switch makes it return the `KokoroG2p` fake, so every test that uses the helpers follows without edits.
- **New test files:**
  - `test_tts_no_torch.py` (AC-72.1) runs a fresh interpreter. It sets `sys.modules[...] = None` for `torch`, `kokoro`, `phonemizer` and `espeakng_loader`, imports the real `misaki.en`, and generates one English and one Spanish ONNX clip. A probe confirmed that `misaki.en` imports with torch blocked.
  - `test_tts_g2p.py` holds AC-72.2 and AC-72.3. It uses a recording `misaki_factory`, a fake espeak `run` and a monkeypatched `spacy.util.is_package`.
- **Packaging tests:** AC-72.6 and AC-72.7 are appended to `test_packaging_backend.py` and `test_packaging_installer.py`, with no existing line changed. The fetch cases build a synthetic pinned zip in `tmp_path` and run the script with `-ExtractOnly`.
- **ta-check:** passes (base `c72fc44`, 15 TA rows).
- **Environment provisioning:** `pytest-red` has no baseline tolerance, so the two env-bound baseline failures (`test_pack_dist_onedir_layout[AC-24.10]`, `test_nsis_pack_check_script[AC-25.10]`) would have failed the gate. The environment was provisioned instead of weakening the gate (§Execution amendments, Row 9).
- **Receipts:** `C:/Temp/av-kit/s32-red-72-pytest.xml`, `s32-red-72-pytest.txt`, `s32-red-72-pytest-verdict.txt`.

## MEU-72 Green

`validate-task.ps1 -Check green-72` (row command, through `rtk proxy`) → `PASS green-72` (log `C:/Temp/av-kit/s32-green-72-run.txt`): pytest 294 passed (PY72 + PY74 + PY73 + REG73), no tolerated failures.

- **Full Python suite (outside the gate):** 803 passed, 0 failed (log `C:/Temp/av-kit/s32-r10-full-pytest.txt`). The two baseline packaging failures (AC-24.10, AC-25.10) pass because of the row 9 provisioning.
- **Static:** `pyright packages/` 0 errors (`s32-r10-pyright.txt`). `ruff check packages/ tests/ tools/smoke_packaged_tts.py` is clean. `ta-check` passes (base `c72fc44`). `ruff format` would rewrap one `InferenceSession(...)` call in `adapter.py`. The baseline file has the same hunk, so it was not applied.
- **Stop condition S3 did not fire:** AC-72.1 passes with the real `misaki.en` imported in a fresh interpreter where torch, kokoro, phonemizer and espeakng_loader are blocked.
- **Engine (`avkit_infra/tts/g2p.py`, `adapter.py`):**
  - **`G2P_ROUTE`:** `KokoroG2p` sends `a`/`b` to a cached `misaki.en.G2P(trf=False, british=...)`. The `fallback` is an `EspeakCliAdapter.en_fallback` only when eSpeak NG is detected, else `None`, and `unk=""`. It checks `spacy.util.is_package("en_core_web_sm")` before it builds the English G2P, so a missing model raises `ConflictError("tts asset missing: tts_spacy_model")` instead of letting spaCy try a download. `e`/`f`/`h`/`i`/`p` go to `espeak.phonemize`. Any other code is a `ValidationError`.
  - **`CHUNK_RULE`:** `split_phonemes(ps, 510)` cuts each window after the last sentence end. Failing that, it cuts after the last clause mark, then at the last space, then hard at 510. The adapter phonemizes sentence by sentence and joins the results with spaces before it splits.
  - **`TORCH_PATH`:** `torch` is the only try-import. `from kokoro import KModel` runs inside `load_model`, so the frozen ONNX backend never imports kokoro. kokoro's package `__init__` imports `pipeline`, which pulls in misaki's espeak binding, so a module-level import would defeat the exclusion. Each chunk's style row is `pack[min(len(ps), 510) - 1]`. The ONNX path keeps its `max(min(len(input_ids), 510) - 1, 0)`. `input_ids` holds the phoneme ids without the two pad tokens and after unknown symbols are dropped. The two indexes therefore agree unless a chunk holds symbols the vocab lacks. Then the ONNX row is lower by the number of dropped symbols. This is noted for the handoff (corrected at the row 12 self-review: an earlier wording said `ids` counted the pad tokens).
  - `generate` checks that the format's engine is loaded before it runs G2P. Empty phonemes give `on_progress(1.0)` and a zero-length float32 array (AC-72.3). Every `KPipeline` import is gone.
- **`G2P_SEAM` switch:** `_patch_engines` installs a `types.ModuleType("kokoro")` stub with `KModel=FakeKModel` in `sys.modules`, and sets `avkit_infra.tts.adapter.KokoroG2p` to `FakeG2p`. `FakeKPipeline` is deleted. `_active_g2p_fake()` now returns `adapter_mod.KokoroG2p`, so `set_phonemes`, `g2p_lang_codes` and `G2pSeam` follow the switch. No test body changed.
  - **Fixture placement:** `FakeKModel.__call__` (added in row 9) moved above `eval`. With it last in the class, the diff deleted baseline line 225 (a blank separator before `FakeKPipeline`), and that line falls outside TA-2's `226-285`. With the move, the class keeps its two original separators, and the removal is `226-` onward only. No assertion is involved.
- **`SPEC_BUNDLE` (`packaging/avkit-backend.spec`):**
  - `hiddenimports` adds onnxruntime, spacy, misaki (with `misaki.data`, `misaki.en` and `misaki.token`), num2words and its submodules, `avkit_infra.tts.g2p` and `avkit_infra.tts.espeak`.
  - `datas` is `collect_data_files("misaki")`.
  - `module_collection_mode={"num2words": "py"}` keeps num2words as replaceable `.py` files (LGPL-2.1).
  - `excludes` adds kokoro, phonemizer, espeakng_loader and `misaki.espeak`. The list is written inline in `Analysis(...)`. A first version assigned it to a module-level `excludes` name, and AC-24.9 failed with `'torch' in []`, because that test reads the `excludes=` keyword's literal through `ast`.
  - pyinstaller-hooks-contrib already has hooks for spacy, thinc, srsly, langcodes and onnxruntime (PyInstaller 6.22.2).
- **Dependencies:** `packages/infrastructure/pyproject.toml` pins `misaki[en]==0.9.4` and `num2words==0.5.14` directly. Both were already in the lock through kokoro. The `uv.lock` diff is the 4 direct-dependency lines. `uv lock` rewrote the file with LF, so the CRLF endings were restored byte for byte.
- **`NOTICES` (`packaging/THIRD_PARTY_NOTICES.md`):**
  - **Shipped components, with licences:** misaki (Apache-2.0, with the ported `MULTI_E2M`/`EN_E2M` tables named), num2words (LGPL-2.1, with replacement instructions for `resources/avkit-backend/_internal/num2words/`), spaCy (MIT) and onnxruntime (MIT).
  - **Not shipped:** the Kokoro-82M weights (Apache-2.0, downloaded on demand). The header also says that eSpeak NG, PyTorch and kokoro are not shipped.
  - **FFmpeg (D-87):** GPL-3.0, the `n8.1.2-44-g7c533d0f86` BtbN build, the source URLs, and the shipped `resources/ffmpeg/LICENSE.txt`.
  - **Appendix:** the full LGPL-2.1 text, copied verbatim from num2words' `COPYING`.
  - `electron-builder.yml` copies the file to `resources/THIRD_PARTY_NOTICES.md`.
  - **Not listed:** transitive MIT/BSD dependencies of spaCy (thinc, srsly, cymem and others). They are a handoff follow-up.
- **`fetch_ffmpeg_windows.ps1` (D-87):**
  - **Licence copy:** after the binary check, the script takes the shallowest `LICENSE.txt` in the archive and copies it to `OutDir/LICENSE.txt`.
  - **No licence:** a missing licence removes the stage and exits 6.
  - **Exit-code fix:** the message is written with `[Console]::Error.WriteLine`. A first version used `Write-Error`, which under `$ErrorActionPreference = 'Stop'` throws, so the process exited 1 before `exit 6`. The script's existing exit-2/3/4 paths still use `Write-Error`, and their tests only check for a nonzero exit. That latent bug is for the handoff.
  - **Provisioned:** the script was rerun with `-ExtractOnly` on the row 9 cached pin. `packaging/ffmpeg-win64` now holds `LICENSE.txt`.
- **`tools/smoke_packaged_tts.py`:**
  - `--phase online` (`ONLINE_PROVISION`): builds with `package_backend.py`, never `--stub-ok`. It refuses an exe under 1 MB and lists any forbidden `_internal` dirs. It then starts the frozen backend and downloads `kokoro-onnx-int8`, the vocab, the spaCy model and the voice packs into `--models-dir`. A 409 "already ready" counts as ready.
  - `--phase offline` (`OFFLINE_SMOKE` + `NEGATIVE_PROBE`):
    - runs the copied `--backend-dir` from its parent folder, with fresh `app-data`, `HF_HOME` and `XDG_CACHE_HOME`;
    - points every proxy variable (upper and lower case) at `http://127.0.0.1:9`, with `NO_PROXY` set to localhost;
    - deliberately leaves `HF_HUB_OFFLINE` unset;
    - loads ONNX int8 on CPU and generates one English WAV;
    - then starts a voice-pack download into an empty folder, which must end `Failed` with an error.
  - Its own HTTP client never uses a proxy.
  - **Terminal status:** the plan says a job "polls to Completed". The real `TTSStatus` success value is `Done` (`Pending`/`Generating`/`Done`/`Failed`/`Cancelled`), so the smoke waits for `Done`. This corrects the plan's wording only.

## MEU-72 Package smoke

`validate-task.ps1 -Check package-smoke` (row command, through `rtk proxy`) → `PASS PACKAGE_SMOKE: ONLINE_PROVISION + INSTALLER_STAGE + OFFLINE_SMOKE (MCP probe: unreachable)` on attempt 2 (log `C:/Temp/av-kit/s32-row12-smoke-run.txt`; result `package-smoke-result.json`, `WORKTREE_IDENTITY` `7925c50c…8764279` at start and end, HEAD `c72fc44`). The run took 2 min 30 s (13:27:48 to 13:30:18). Attempt 1 failed in `OFFLINE_SMOKE` (§Execution amendments, Row 12).

- **`ONLINE_PROVISION`** (36 s):
  - `package_backend.py` exit 0 in 34.0 s. `avkit-backend.exe` is 27,032,476 bytes, `forbidden_dirs: []`, and `_internal/num2words/*.py` ships as source, as NOTICES says.
  - The frozen backend ran with a fresh HOME. `kokoro-onnx-int8` was `already_downloaded`, the vocab and voice packs were `already_ready` in `C:/Temp/av-kit/s32-smoke-models`, and the spaCy model `downloaded` into `s32-smoke-models/spacy/en_core_web_sm-3.8.0` (Idle, no error). All three assets ended `ready`.
- **`INSTALLER_STAGE`:**
  - `npm run dist` exit 0, and `assert-nsis-pack.ps1` exit 0. The installer is 475,704,219 bytes, under the 500 MB cap, so S6 did not fire.
  - `notices_staged: true` (`resources/THIRD_PARTY_NOTICES.md`) and `ffmpeg_license_staged: true` (`resources/ffmpeg/LICENSE.txt`), so S8 (licence) did not fire.
  - **`MCP_ENTRY_PROBE`:** `unreachable`. `node resources/mcp-server/index.js` exits 1 in 0.11 s with `ERR_MODULE_NOT_FOUND: Cannot find package '@modelcontextprotocol/sdk'`. The packaged `mcp-server` folder has no `node_modules`, which matches the second half of the `MCP-PACKAGED-ENTRY-UNREACHABLE` title. H2-2 copies this into the issue (`unreachable` → `open`).
- **`OFFLINE_SMOKE`** (43 s, `C:/Temp/av-kit/s32-smoke-offline.json`):
  - The backend runs from the copy `C:/temp/av-kit/s32-smoke-run/avkit-backend`, outside the worktree, with cwd `s32-smoke-run`.
  - It gets fresh `app-data`, `HF_HOME`, `XDG_CACHE_HOME` and HOME. `HTTP(S)_PROXY` and `ALL_PROXY`, upper and lower case, point at `http://127.0.0.1:9`, and `NO_PROXY` is `127.0.0.1,localhost`.
  - `register`: `downloaded` (Idle, no error). This is the download fast path over the provisioned file, with no network.
  - The ONNX int8 model loaded on CPU. `generate "Hello from av-kit."` with `af_heart` reached `Done` in 1.9 s and wrote `out/<id>.wav` inside the output folder: **41,400 samples at 24 kHz** (1.7 s; the floor is 8,000).
- **`NEGATIVE_PROBE`:** a `tts_voice_packs` download into an empty `probe-models` folder ended `Failed` with "voice pack af_heart download failed: An error happened while trying to locate the file on the Hub and we cannot find the requested files in the local cache…". The dead proxy blocked it, so S8 (network) did not fire.
- **Stop conditions:** S4 (frozen spaCy or misaki data) did not fire. Both attempts loaded and ran misaki and spaCy in the frozen backend, and attempt 1 failed for a reason in the smoke harness, not the spec. S6, S7 (the `ONNX_REVISION` download was not reached, because the variant was already provisioned) and S8 did not fire either.

## LOCAL-ESPEAK

**Unverified (AC-74.11, plan `LOCAL-ESPEAK`, S5).** eSpeak NG is not installed on this machine on 2026-10-15:

- `which espeak-ng` finds nothing on PATH.
- Neither `%ProgramFiles%/eSpeak NG` nor `%ProgramFiles(x86)%/eSpeak NG` exists.
- `EspeakCliAdapter().status()` returns `EspeakStatus(available=False, version=None, path=None)`.

The live Spanish (`ef_dora`) and French (`ff_siwis`) generates were therefore not run. The real-CLI checks of `ESPEAK_G2P` (the `e` in `este` and U+0303 in `bon`) and the `tts_espeak` version row were not done either. What *is* covered:

- AC-74.6 tests the exact argv, stdin and output mapping against a fake runner.
- `ESPEAK_MAP_PARITY` pins the maps to the installed misaki tables.
- The MEU-74 live probe confirms the "not installed" path end to end: 13 `espeak_missing` voices, and `tts_espeak` nulls.

H2-2 files an issue for the live espeak CLI path, per the plan.

## Windows gate

H1-2 on the final tree (HEAD `c72fc44`, uncommitted work). `WORKTREE_IDENTITY` is `cd879e6e…2611e18` at the start and end of both the gate and the package smoke, in both attempts. Preflight: `agentic-framework` HEAD `e387dec`, agent registry `A7C95972…`, `drift: false`. Log `C:/Temp/av-kit/s32-h1-gate-run.txt`.

- **Attempt 1 (13:41–13:48): `FAIL`, Electron 136 expected / 2 unexpected.** The 15 stages before Electron passed (pytest 803/0, Vitest 816/816). Two specs missed:
  - `AC-63.5` (`tts-generate.test.ts:580`): the `error-banner` was not found within 5 s. The page snapshot still showed the job `Generating · Segments 1/2`, so the 1 s job poll had not yet read the seam's `Failed`. The test file is unchanged since `c72fc44`, and the spec passed in the baseline, Green-74 and gate74 runs.
  - `AC-49.28` (`download-queue.test.ts:1387`): 60 s test timeout on a spec that takes about 2 s. Known issue `DOWNLOAD-QUEUE-DRAG-OVER-MISS` (open) records the same intermittent miss.
  - **Host:** other sessions were active on the machine (78 node, 69 python, 2 codex and 1 pytest processes).
  - **Probe:** both specs re-run alone with `--repeat-each 5`: 10/10 pass, at the usual 1.8–2.8 s and 6.6–7.1 s (`C:/Temp/av-kit/s32-h1-flake-probe.txt`). No file changed between attempts.
  - Attempt 1 artifacts: `s32-h1-windows-gate-result-attempt1.json`, `s32-h1-gate-run-attempt1.txt`, `s32-win-e2e-attempt1.json` (all in `C:/Temp/av-kit/`).
- **Attempt 2 (13:50–13:58): `PASS`.**
  - `windows-gate`: 17/17 stages exit 0 (318 s). pytest 803/0, Vitest 816/816, Electron 138 expected / 0 unexpected / 0 skipped / 0 flaky (`windows-gate-result.json`).
  - `package-smoke`: `PASS PACKAGE_SMOKE` (`package-smoke-result.json`). Online: exe 27,032,476 bytes, variant downloaded. Installer: 475,703,896 bytes under the cap, `dist` and `assert-nsis-pack` exit 0, NOTICES and FFmpeg `LICENSE.txt` staged. Offline: 41,400 samples generated from the backend copy under the dead proxy; the negative probe `Failed`. MCP probe: `unreachable` (exit 1, `ERR_MODULE_NOT_FOUND`), the same as row 12.
  - `windows-gate-check`: `PASS windows gate + package smoke @ cd879e6ef3f5` (both JSONs bound to one identity, `COUNT_FLOORS` met, zero flaky).
- These results supersede row 12's package smoke (`7925c50c…`, before the row 13 edits) as the authoritative evidence for the handoffs.

## Split

Row 8, D-82. The session token counter reads 12,536,236 left of 15,000,000, so 2,463,764 tokens are used (16.4%). That includes the "+7M" extension Mat approved. The coordinator's context has been compacted during the session. The latest compaction came during row 8, after the row 6 and row 7 evidence was on disk, and work resumed from that evidence. Usage is below the ~50% threshold, so **no split**: rows 9 onward continue in this session on the same plan, task table, gate and review loop.

## Execution amendments

### Row 2: TA-3a range 597-610 → 597-611

- **What changed:** the TA-3a row in `implementation-plan.md` now names `tests/integration/test_tts_assets.py:597-611`.
- **Why:** line 611 (`assert "error=ONNX voice pack is missing" in line`) asserts the message of the very failure TA-3a replaces. With failure forced by a `FakeSession.run` that raises `RuntimeError("session boom")`, the console line carries `error=RuntimeError: session boom`, so 611 must change with 603-610. The plan's range stopped one line short.
- **Also inside the range:** the session failure is a non-domain exception, so the route answers 500 (the AC-62.11 path), not 201. Lines 604-606 send the request through a `TestClient(..., raise_server_exceptions=False)` via `_generate_with`, assert 500, and read the failed job id from `tts_jobs` (`_failed_job_id`). The console-line assertions (`job_id=<id>` and the redaction case) are unchanged.
- **Added helpers (added lines, no baseline line changes):** `_session_boom` and `_failed_job_id` after the test; `PackServer` and the `Stack` patch of `avkit_infra.model_manager.voice_packs.hf_hub_download` (separate from `HubServer`, because AC-62.2 asserts the hub saw only `config.json`); `write_voice_packs(...)` setup lines in `_load_ready_variant`, `test_ac_62_5`, `test_ac_62_16`, and in `test_tts_models.py` `test_ac_9_6`/`test_ac_9_7`. Each seeds the packs a finished `tts_voice_packs` download leaves, so generate reaches the code under test past `ASSET_409_ORDER`.
- **Scope:** no new TA id, no AC change, no product file. `ta-check` enforces the new range.

### Row 2: Stop condition S1 — branch fast-forwarded to `c72fc44`

- **What happened:** after row 0, outside this session, `claude/s32-tts-engine-runtime` was fast-forwarded from `7861020` to `c72fc44`. The reflog shows `merge main: Fast-forward` at 2026-10-15 09:50 -0400, and every av-kit worktree is now at `c72fc44`. That commit merges Session 31 (`2026-10-10-gui-polish-residuals`) into `main`. This is S1 as written ("`main` moved past `7861020` with Session 31 merged"). The only difference is that it landed during row 2, not before row 0. No MEU-73 product file had changed yet, and the Red test files were already on disk.
- **What Session 31 brought:** UI, docs and `.agent` files only. There are no Python, MCP or TTS UI changes. `SettingsPage.tsx` gained section layout/emphasis props (`sectionFrameProps`, `useTailSpacer`, `currentSection`), and none of them overlap the MEU-73 TTS card. Its Vitest changes moved two files that TA-5's diff had been computed against (`app-shell-wiring.test.ts`, `chrome-zorivest.test.ts`).
- **`baseline.sha`:** re-pointed from `7861020` to `c72fc44`, so `ta-check` and `api-scope` diff against the tree MEU-73 actually builds on. The old value is kept outside the repo at `C:/Temp/av-kit/s32-baseline-7861020.sha`. After the change, `ta-check` passes (base `c72fc44`).
- **`COUNT_FLOORS` re-derived:** Session 31's gate (`0cfa40a`: 775 / 131 / 629) was measured before Session 30 merged, so neither gate alone covers `c72fc44`. The floors are the larger of the two gates and a measurement of the merged tree before any MEU-73 product change:
  - **Vitest:** 800 total, 0 failed without this plan's new file. The run had 807 total with only the 7 Red tests of `settings-tts-runtime.test.ts` failing (`C:/Temp/av-kit/s32-s1-vitest.json`).
  - **Playwright:** 137. The full run had 133 expected and 4 unexpected (`C:/Temp/av-kit/s32-s1-e2e.json`). All 4 unexpected were `capture-picker.test.ts`, failing only because the region-picker sidecar stub was not built in this worktree. After `npm --prefix ui run build:picker-stub`, that spec passed 4/4 (`C:/Temp/av-kit/s32-s1-e2e-picker.json`). The gate builds the stub as its own stage.
  - **pytest:** stays at 655. Session 31 changed no Python, and its 629 predates Session 30's tests.
  - **Files updated:** the plan `COUNT_FLOORS` row, the `windows-gate-check` literals (800 / 137 / 655), and the `plan_checks.py` selftest's "changed floor" mutation string. `plan_checks.py static` and `selftest` pass.
- **`prereq` guard:** S1's check now looks for Session 31 commits on `main` after `c72fc44`, not after `7861020`. Otherwise every later re-run of `prereq` would stop on the merge this amendment already handles.
- **Row-0 baseline receipts:** kept as written. They now over-tolerate, because AC-41.3 (`ui/tests/unit/settings-page.test.ts`), which failed at `7861020`, passes at `c72fc44`. The expected H1-2 AC-41.3 tolerance is therefore likely no longer needed.
- **Scope:** no AC, TA id or MEU boundary changed. The edits are confined to `baseline.sha`, the floors, the guard, and this record.

### Row 3: AC-73.10 test setup waits for the first `Downloading` result

- **What changed:** in `ui/tests/unit/settings-tts-runtime.test.ts`, the two tests that start in `Downloading` now call a new setup helper, `waitForRuntimeDownloading()`, after `runtimeCalls > 0` and before they flip `runtimeState`. The helper waits until the runtime query's cached data has `state: 'Downloading'`. No assertion or expected value changed.
- **Why:** `runtimeCalls > 0` is true as soon as the first fetch starts. A `refetchQueries` issued while that first fetch is in flight is deduped into it by TanStack Query (no data yet, so nothing is cancelled). The cache then never holds the flipped state until the next 1 s poll, which lands just past `vi.waitFor`'s 1 s default (the failing run took 1033-1046 ms). This is a setup race in the test, which AGENTS.md allows as a fixture repair. It is separate from the product race fixed in the hook (§MEU-73 Green).
- **Scope:** a new file of this plan, so there is no baseline line and no TA id.

### Row 5: `FakeTTS.list_voices` returns `(VoiceConfig, availability)` pairs

- **What changed:** in `tests/e2e/api_fakes.py`, `FakeTTS.list_voices` now returns `[(VoiceConfig(am_eric…), SimpleNamespace(available=True, reason=None))]`. It is marked `MEU-74 (D-89)`.
- **Why:** under D-89, `TTSService.list_voices` returns each voice with its availability, and the route maps the pair to `VoiceOut`. The REST fake stands in for the service, so it must return the service's shape. `am_eric` is lang `a`, which is always available, so the pair is fixed.
- **Scope:** `api_fakes.py` is already a TA-4 file. No assertion changes; this is fake setup. Until row 6 changes the route, `test_api_tts_models.py::test_ac_16_7` fails with `AttributeError`. That file is outside the red-74 run set and goes green in row 6.

### Row 6: the parity test checks espeak.py imports, not `sys.modules` (D-98)

- **The failure:** `test_ac_74_6_espeak_map_parity_with_installed_misaki` ended with `assert "misaki.espeak" not in sys.modules`. Importing `avkit_infra.tts.espeak` runs the `avkit_infra.tts` package init, which imports `KokoroAdapter`, then `kokoro`, whose `pipeline.py:5` does `from misaki import en, espeak`. Confirmed in a bare interpreter: `import avkit_infra.tts.espeak` leaves `misaki.espeak` in `sys.modules`. The expectation is wrong, not the adapter.
- **Disposition:** a proven wrong expectation (AGENTS.md:57), briefed to Mat before any change (AskUserQuestion, 2026-10-15). **USER_EXPLICIT:**

  > AST import scan (Recommended)

- **Resolution (D-98):** the line is replaced with an AST scan of `avkit_infra/tts/espeak.py`: no `Import`/`ImportFrom` of `misaki`, `phonemizer` or `espeakng_loader`. The two table-parity assertions are unchanged, and the unused `import sys` is dropped. MEU-72 `IMPORT_HYGIENE` keeps the runtime `sys.modules` check, in a fresh interpreter.

### Row 7: `useVoices` rows typed `VoiceOut[]` (D-99)

- **The break:** with `available?: boolean` on `VoiceOut`, `npm --prefix ui run typecheck` failed with TS2352 at `TTSPage.tsx:126`. That line casts the `useVoices()` rows, typed `Array<Record<string, string>>`, to `VoiceOut[]`, and a string record no longer overlaps a type that has a boolean field.
- **Resolution (D-99, autonomous, Local Canon):** `useTtsJob.ts` `useVoices` now fetches `{ items: VoiceOut[] }`, through a type-only import. There is no runtime change, and `TTSPage.tsx` is untouched. `useTtsJob.ts` was already a plan file (MEU-73), so `api-scope` passed anyway. It is now also listed in the MEU-74 Files Modified table.

### Row 8: the voice-pack `stack` fixture waits for the background spaCy download (setup repair)

- **The failure:** the first `gate74` run failed 12 `test_tts_assets.py` tests (AC-62.5 to AC-62.16) with "tts asset already ready: tts_spacy_model" and `'ready' == 'missing'`. The same 259-test set passed in `green-74` and on 3 of 5 local reruns, so the failure depended on timing.
- **Cause, shown with a scratchpad pytest plugin that reports `sys.path` and `sys.modules` after each test:** `test_ac_73_16_redownload_over_a_legacy_row_fetches_v1` calls `/models/load`. The load starts the spaCy download in the background (AC-62.7). The `stack` fixture in `test_tts_voice_packs.py` restored `sys.path` on teardown without waiting for that download. When the download finished late, `activate_spacy_dir` appended the test's tmp `models/spacy/en_core_web_sm-3.8.0` to the restored process-wide `sys.path`. Every later `test_tts_assets.py` test then saw spaCy as ready.
- **Repair:** the fixture teardown calls `built.wait_idle()` before closing the client. The runtime stays `Downloading` until `activate_spacy_dir` has run, so the append lands on the test's own `sys.path` copy. The teardown also drops `en_core_web_sm*` from `sys.modules`, the same way `test_tts_assets.py` `isolated_path` does. No assertion or expected value changed, and the product code is unchanged. After the repair, the gate's pytest list passed 5 of 5 runs with no leak reported.
- **Lint:** `ruff check` also reported I001 (import order) in `test_ac_73_3_fetch_voice_pack_pins_the_v1_repo_and_revision`, in the same file. `ruff check --fix` reordered the two imports.
- **Line endings:** `assets.py`, `test_tts_models.py` and `ui/tests/e2e/fixtures/tts-voices.json` had been rewritten to LF by earlier edit scripts. They are restored to the CRLF checkout form. This is a byte-only change: `git diff` is unchanged, and the four affected pytest files pass.

### Row 9: TA-3b deletion range 772-839 → 770-839

- **The refusal:** with `_ResultLike` and AC-62.16 deleted, `ta-check` reported that baseline lines 770-771 had changed outside TA-3b. Those are the two blank separator lines before `class _ResultLike`. Because the deleted block ended the file, the separators go with it. Keeping them would leave two trailing blank lines.
- **Amendment:** TA-3b's range in `implementation-plan.md` now reads `25, 556-582, 770-839`. Only blank lines are added to the range, and no assertion is involved. `ta-check` then passes.

### Row 9: test environment provisioned for `red-72` (and later rows)

- **Why:** `pytest-red` has no baseline tolerance. AC-24.10 needs `packaging/dist/avkit-backend`, and AC-25.10 needs the pinned FFmpeg in `packaging/ffmpeg-win64`. Both are gitignored build outputs, absent in this worktree, and both failures are already recorded in the row-0 baseline.
- **Backend:** `uv run --frozen python tools/package_backend.py` exit 0 (log `C:/Temp/av-kit/s32-r9-pack-backend.txt`). This builds the current, pre-Green spec. Row 12 rebuilds it.
- **FFmpeg:** `tools/fetch_ffmpeg_windows.ps1` failed with **404 Not Found**. The pinned BtbN release `autobuild-2026-08-24-13-10` is no longer published (`curl -sI` also returns 404, 2026-10-15). A cached copy at `C:/Temp/av-kit/ffmpeg-dl/ffmpeg-pin.zip` has SHA256 `5efb8182…90bdab`, which equals the script's pin. It was copied to `packaging/ffmpeg-win64/ffmpeg-pin.zip`, and the script was rerun with `-ExtractOnly` (exit 0, log `C:/Temp/av-kit/s32-r9-fetch-ffmpeg.txt`). The SHA check still ran. The archive contains `LICENSE.txt`, which matters for AC-72.7's copy rule.
- **Follow-up:** the pin URL is dead for any fresh checkout. That is outside MEU-72's scope (the AC-72.7 fetch cases use a synthetic archive), so it is recorded for the MEU-72 handoff and the closeout as a new issue rather than changed here.

### Row 12: package smoke attempt 1 → 2 (smoke harness fixes, no product change)

Attempt 1 (log `C:/Temp/av-kit/s32-row12-smoke-run-attempt1.txt`, offline JSON `s32-smoke-offline-attempt1.json`) passed `ONLINE_PROVISION` and `INSTALLER_STAGE`, then failed `OFFLINE_SMOKE`: `POST /models/load` returned 500. Three fixes to `tools/smoke_packaged_tts.py`, which is new in this plan:

- **(a) The offline load 500: register the variant first.**
  - **Cause:** in a fresh app-data, the `kokoro-onnx-int8` DB row has `path=None`, so `load` raises `ModelLoadError("model weight file is missing")` from `_require_weight_path`. `GET /models/downloaded` still lists the variant as downloaded, because it unions in sideloaded files found under `models_directory`.
  - **Confirmed** from source as well as the frozen exe (`scratchpad/r12_load_repro_src.py`, `r12_load_probe.py`).
  - **Pre-existing:** the baseline `load` and `_require_weight_path` are unchanged by this plan.
  - **Smoke fix:** the offline phase first calls `POST /models/download {variant_id}` and requires the `downloaded` result. That takes the existing fast path, which finds the provisioned file and records its path with no network (the dead proxy proves it). Then it loads.
  - **New issue candidate (H2-2):** a sideloaded variant is listed as downloaded but cannot be loaded. `ModelLoadError` maps to a 500 `internal_error`, and nothing is logged at uvicorn's `warning` level.
- **(b) spaCy came from Mat's home folder: give each backend a fresh HOME.**
  - **Cause:** with a fresh app-data, `models_directory` defaults to `~/.avkit/models`. At startup the backend puts that folder's `spacy/en_core_web_sm-3.8.0` (present in Mat's real profile) on `sys.path`. A later `PUT models_directory` never takes it off. Attempt 1's online phase therefore reported the spaCy model `already_ready` without provisioning `s32-smoke-models`.
  - **Smoke fix:** `_fresh_home` points HOME and USERPROFILE at an empty folder for both phases (`s32-smoke-online-home`, `s32-smoke-run/home`). Attempt 2 downloaded spaCy into `s32-smoke-models` as intended.
  - **New issue candidate (H2-2):** a stale spaCy `sys.path` entry survives a `models_directory` change. This is the same mechanism as the Row 8 test leak, here in the product.
- **(c) The result JSON was unreadable by PowerShell.** The recorded proxy dictionary held `HTTP_PROXY` and `http_proxy` both, and `ConvertFrom-Json` rejects keys that differ only in case. The smoke still sets both forms but records only the upper-case keys plus `NO_PROXY`, and adds `proxy_lower_case_set: true`.

No assertion, gate check or product file changed. The gate's checks on the result (`gate_lib.py` `package-smoke`) are the same in both attempts.

### Row 13: hub reconciliation and D-100

`validate-task.ps1 -Check hub` → `PASS hub` on attempt 2 (log `C:/Temp/av-kit/s32-hub-run.txt`): `PASS hub reconciliation (02, 03 x2, 06, 07, 11, matrix)` and `PASS s32-hub-doc-suites: 10 passed of 10`.

- **Hub edits:**
  - `02-infrastructure.md`: the ONNX repo is `onnx-community/Kokoro-82M-v1.0-ONNX` @ `ONNX_REVISION`.
  - `03-service-layer.md`: a "Delivered (Session 32)" line under each residual section (MEU-73, D-74; MEU-74, D-71).
  - `07-distribution.md`: a "Delivered (Session 32)" line under Packaged ONNX (MEU-72).
  - `06-gui.md`: the Settings Dependencies row lists the TTS assets, eSpeak NG, Get and Copy link.
  - `11-page-layout.md`: the Voice picker row describes unavailable voices.
  - `build-priority-matrix.md`: rows 3.6 (MEU-73), 3.7 (MEU-74) and 7.4 (MEU-72).
- **D-100 (autonomous, Local Canon):** the D-96 Copy link button had no test id. It now has `data-testid="tts-espeak-copy-link-btn"`, registered as `TTS_ESPEAK_COPY_LINK_BTN` in `ui/tests/e2e/test-ids.ts`. `settings-tts-runtime` and `capture-flatten` Vitest pass 18/18 after it (log `C:/Temp/av-kit/s32-row13-vitest.txt`).
- **Attempt 1** also added a `settings:copy_espeak_link` row to `gui-actions-index.md`. `gui-actions-audit` AC-23.20 failed on it: `resolveIpcChannel` (`ui/tests/unit/gui-actions-audit.test.ts:66-77`) has no `writeClipboardText` mapping. The test is immutable here, so the row was removed and D-100 amended. The existing Settings "Copy log path" button has no index row for the same reason. Both go to the closeout as one follow-up.

### H1-6: execution review round 1, and F1

Codex `gpt-6.1-sol` (effort `high`, dispatch `s32-exec-r1`) returned **approved** in round 1 with one Low, non-blocking finding. The report is copied verbatim to `.agent/context/handoffs/2026-10-14-tts-engine-runtime-implementation-critical-review.md`. `-Check review-check -Arg implementation` → `PASS implementation review approved round 1 by gpt-6.1-sol` (log `C:/Temp/av-kit/s32-exec-review.txt`).

- **Ledger record.** The dispatcher was started from `P:/av-kit`, so its sibling `P:/av-kit/tools/review_ledger.py` resolved the verdict's relative `target_plan` against `P:/av-kit`, not the worktree. It refused with `target-plan-mismatch` and consumed no round. The unchanged `final.json` and `events.jsonl` were then recorded with the worktree's `tools/review_ledger.py record`. This is the same call the dispatcher makes (`Invoke-CodexDispatch.ps1:1275`), now with the worktree's ledger script. Result: `OK: recorded round 1 verdict=approved ... blocking=0 intent_achieved=yes` (log `C:/Temp/av-kit/dispatch/s32-exec-r1/ledger-record-worktree.txt`). The verdict was not edited.
- **F1 (Low, clerical).** Row 4's evidence names D-90..D-94, which the MEU-73 handoff defines but the plan's `decision_log` did not, so `plan_checks.py static` rejected them. The selftest's "undefined decision" case also injected D-99, which D-99 itself now defines.
  - Fix: the five D-90..D-94 entries were copied verbatim from the MEU-73 handoff into the plan's `decision_log`, before D-95. The selftest now injects `D-999`.
  - `plan_checks.py` is outside `GATED_PATHS`, so H1-2 is not reopened.
  - `-Check plan-static` → `PASS plan-static`, including `PASS selftest undefined decision` (log `C:/Temp/av-kit/s32-f1-plan-static.txt`).
- **H2-1 placeholder respelling.** The reflection validator's placeholder pattern matched `<c>` in D-71 and `<id>` in D-74. In the plan's `decision_log` they now read `--tie=CHAR` and `voices/VOICE_ID.bin`. The meaning is unchanged.

## Closeout (H2)

- **H2-1** reflection: `docs/execution/reflections/2026-10-14-tts-engine-runtime-reflection.md`. The closeout validator reconciles 38 recorded decisions against 38 Decisions Log rows (`s32-reflection-run.txt`).
- **H2-2** `POST_REVIEW_STATE` (`s32-post-review.txt`):
  - MEU-73/74/72 are `approved`, the grouping marks Session 32 `approved`, and focus and metrics are updated.
  - Five TTS issues are resolved, with `windows-gate-result.json` and `package-smoke-result.json` as evidence.
  - `TTS-JA-ZH-G2P-EXTRAS`, `FFMPEG-GPL-BUILD` and `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` are filed as open.
  - `MCP-PACKAGED-ENTRY-UNREACHABLE` is `open`, because the probe returned unreachable. Seven candidates are filed.
- **H2-3** `plan-static`: `plan_checks.py static` and `selftest` and `lint_task_contract.py` (`s32-closeout.txt`). Rows 0–13 and H1-1 to H2-3 are `[x]`.

Merge note: the branch base `c72fc44` is `main`'s current tip, so the commit fast-forwards `main`. Nothing is committed: Mat commits from the draft below.

### Commit-message draft

```
feat(tts): offline engine runtime without GPL code (Session 32, MEU-73/74/72)

MEU-73: the 54 Kokoro v1.0 voice packs are one managed asset,
tts_voice_packs, fetched with the other TTS assets rather than lazily at
first use (D-74). The ONNX model comes from
onnx-community/Kokoro-82M-v1.0-ONNX at a pinned revision, and legacy
v0.19 paths are refused (D-73). Settings Dependencies refreshes when a
download settles, and the spaCy model dir is appended to sys.path, not
prepended.

MEU-74: every voice reports available/reason from a closed
VOICE_REASON set, carried as a VoiceAvailability value beside the
unchanged VoiceConfig (D-89). Non-English voices phonemize through a
user-installed eSpeak NG CLI run as a subprocess, with misaki's
Apache-2.0 maps ported (D-71). Japanese and Mandarin are marked
unavailable (D-70). Settings shows the eSpeak NG download URL with a
Copy link button (D-96).

MEU-72: av-kit's own KokoroG2p and chunking replace KPipeline, so the
frozen backend ships the ONNX runtime without torch. The frozen backend
and everything it loads in process carry no GPL code (D-87).
THIRD_PARTY_NOTICES lists the bundled licences, including num2words
(LGPL-2.1) as replaceable source and the separately shipped GPL FFmpeg.

Windows gate attempt 2 at WORKTREE_IDENTITY cd879e6e: 17/17 stages,
pytest 803/0, Vitest 816/816, Electron 138/0/0/0. PACKAGE_SMOKE
generated speech offline from the installer's own backend with every
proxy at a dead port, and the negative probe proved the denial. The
plan review was approved in round 3 and the execution review in round
1 (Codex gpt-6.1-sol). TEST_AMENDMENTS TA-1 to TA-14 were approved.

Resolves TTS-VOICE-PACK-LAZY-FETCH, SETTINGS-TTS-ASSET-ROW-STALE,
TTS-SPACY-SYSPATH-PREPEND, TTS-NON-ENGLISH-G2P-DEPS and
TTS-PACKAGED-RUNTIME-EXCLUDED. Files TTS-JA-ZH-G2P-EXTRAS,
FFMPEG-GPL-BUILD and TTS-ESPEAK-LIVE-PATH-UNVERIFIED.
```
