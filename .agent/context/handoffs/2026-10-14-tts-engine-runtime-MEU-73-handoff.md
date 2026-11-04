---
date: "2026-10-15"
project: "tts-engine-runtime"
meu: "MEU-73"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch (tools/Invoke-CodexDispatch.ps1)"
predecessor: "none"
---

# Handoff: 2026-10-14-tts-engine-runtime-MEU-73-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-73 — Kokoro v1.0 voice packs as a managed TTS asset, plus the v1.0 ONNX repo switch.
- **The asset:** `TtsAsset.VOICE_PACKS = "tts_voice_packs"` is declared last, and `required_tts_assets` appends it for every format and lang code. `TtsAssetAdapter.state` follows `VOICE_PACKS_READY`: all 54 catalog packs at exactly 522 240 bytes.
- **The download (`VOICE_PACK_DOWNLOAD`):**
  - It fetches only missing or wrong-size packs, through an injected `fetch_pack`. The fetch is `model_manager/voice_packs.py::fetch_voice_pack`, which uses `ONNX_REPO` at `ONNX_REVISION` into `ONNX_LOCAL_DIR`.
  - Each fetched file is size-checked. A wrong-size file is deleted and raises a `ModelDownloadError` that names the voice.
  - `avkit_infra.tts` still never imports `huggingface_hub`.
- **The style source:** `KokoroAdapter._voice_pack` reads `VOICE_PACK` (`<f4`, shape 510×256) from the models directory that holds the vocab.
  - The ONNX style row is `pack[min(len(input_ids), 510) - 1]` (`ONNX_FEEDS`).
  - The PyTorch path passes the same pack as a `(510, 1, 256)` tensor to `KPipeline`. `KPipeline` itself stays until MEU-72 row 10.
  - Nothing is fetched mid-run.
- **`MODEL_CHAINS_PACKS`:** a variant download that finds packs missing continues into the pack download. The runtime switches to `asset=tts_voice_packs, variant_id=None` at that point. A pack failure leaves the variant downloaded and the runtime `Failed`, with an error naming `tts_voice_packs`.
- **Repo switch and legacy files (D-73):**
  - The `HF_FILE_MAP` ONNX rows use `ONNX_REPO`. `variant_local_path` places ONNX weights under `ONNX_LOCAL_DIR`, and the download pins `revision=ONNX_REVISION`.
  - A v0.19 file (`LEGACY_ONNX_PATH`, `{models}/onnx/*.onnx`) is ignored by sideload, which logs `model.legacy_onnx_ignored`. A row persisted there reads `is_downloaded: false`, its load returns 409 `needs a re-download (v0.19 file)`, and a re-download fetches the v1.0 weights instead of taking the fast path.
- **`activate_spacy_dir`** appends to `sys.path` and no longer prepends.
- **Wire and UI:**
  - API: `tts_voice_packs` is added to `TtsAssetWire`, `DependenciesOut` and the routes, and `openapi.committed.json` is regenerated.
  - MCP: `TTS_ASSET_WIRES` includes the new wire.
  - GUI: the Settings Dependencies card has a "Voice packs" row. `useRefreshDependenciesOnSettle` invalidates `['health','dependencies']` once whenever the runtime leaves `Downloading`.
- **Test amendments:** TA-1, the TA-2 voice error case, TA-3a, TA-6, TA-8, TA-10, TA-11, TA-12 and TA-13 were applied exactly, along with the MEU-73 halves of TA-4 and TA-5. `ta-check` enforces them.

**Build Plan Section**: `docs/build-plan/03-*` §TTS residuals ("Voice packs managed", "Settings refresh", "spaCy path"). Row 13 reconciles the hub.
**Predecessor**: none. This is the first MEU of Session 32. MEU-74 builds on `ASSET_409_ORDER` and on `/health/dependencies`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-73.1 | unit | `VOICE_PACKS` declared last; `required_tts_assets` order `(ONNX_VOCAB, SPACY_MODEL, VOICE_PACKS)` / `(ONNX_VOCAB, VOICE_PACKS)` (TA-11) | Spec 03 "Voice packs managed" | `tests/unit/test_tts_voice_packs_service.py:61`, `:67` | ✅ |
| AC-73.2 | integration | `state(VOICE_PACKS)` follows `VOICE_PACKS_READY` (54 × 522 240 → ready; one missing or 522 239 → missing) | Spec 03; D-74 | `tests/integration/test_tts_voice_packs.py:68` | ✅ |
| AC-73.3 | integration | Fetches only missing or wrong-size packs; `revision=ONNX_REVISION`; monotonic progress to 1.0; a wrong-size pack is deleted and the error names the voice; `avkit_infra.tts` never imports `huggingface_hub` | Spec 03; AC-9.12 | `test_tts_voice_packs.py:91`, `:118`, `:130` | ✅ |
| AC-73.4 | unit | A missing pack → `ConflictError("tts asset missing: tts_voice_packs")` with no job row; the vocab 409 still comes first | Spec 03; MEU-62 | `test_tts_voice_packs_service.py:77`, `:91` | ✅ |
| AC-73.5 | integration | ONNX style row read from `VOICE_PACK`; with `hf_hub_download` patched to raise, generate yields finite samples | Spec 03; TTS-VOICE-PACK-LAZY-FETCH | `test_tts_voice_packs.py:168` | ✅ |
| AC-73.6 | unit | `MODEL_CHAINS_PACKS`: `asset=tts_voice_packs` while `Downloading`, then `Idle`; packs present → no fetch; a pack failure keeps the variant and fails the runtime | Spec 03; D-74 | `test_tts_voice_packs_service.py:105`, `:124`, `:137` | ✅ |
| AC-73.7 | integration | `POST /models/download {"asset":"tts_voice_packs"}` → 202; `/health/dependencies` reports it; an unknown asset → 422 | Spec 03 | `tests/e2e/test_api_tts_runtime.py:39`, `:50`, `:62` | ✅ |
| AC-73.8 | unit | ONNX rows use `ONNX_REPO`, `revision=ONNX_REVISION`, `local_dir=ONNX_LOCAL_DIR`; PyTorch row unchanged (TA-1) | D-73 | `tests/integration/test_tts_models.py:706` | ✅ |
| AC-73.9 | integration | Sideload ignores `LEGACY_ONNX_DIR/*.onnx` and logs it; finds `ONNX_LOCAL_DIR/onnx/model_quantized.onnx`; an elsewhere `model_fp16.onnx` still maps | D-73 | `test_tts_voice_packs.py:206` | ✅ |
| AC-73.10 | integration | `useRefreshDependenciesOnSettle` invalidates dependencies exactly once on `Downloading → Idle` and `Downloading → Failed`; never on steady `Idle` | Spec 03 "Settings refresh"; D-43 | `ui/tests/unit/settings-tts-runtime.test.ts:153`, `:158`, `:173`, `:184` | ✅ |
| AC-73.11 | integration | "Voice packs" row (`tts-asset-row-tts_voice_packs`); Get when missing posts `{asset:"tts_voice_packs"}`; no Get when ready | Spec 03 | `settings-tts-runtime.test.ts:194`, `:199`, `:213` | ✅ |
| AC-73.12 | unit | `activate_spacy_dir` appends (`sys.path[-1]`), keeps existing order, idempotent | Spec 03 "spaCy path" | `tests/integration/test_tts_assets.py:740` | ✅ |
| AC-73.13 | unit | MCP `TTS_ASSET_WIRES` includes `tts_voice_packs`; `download_asset` accepts it and rejects an unknown wire (TA-6) | Spec 03; D-84 | `mcp-server/tests/models-assets.test.ts:59`, `:64` | ✅ |
| AC-73.14 | integration | `openapi.committed.json` regenerated; `export_openapi.py --check` passes | G8 | gate stage `openapi` in `gate73` | ✅ |
| AC-73.15 | integration | On a migrated SQLite database with a v0.19 row, `GET /models` shows `is_downloaded: false`, and load returns 409 `needs a re-download (v0.19 file)` | D-73 | `test_tts_voice_packs.py:268`, `:287` | ✅ |
| AC-73.16 | integration | Re-download over a legacy row fetches the v1.0 weights once (no fast path); the row path becomes `variant_local_path(...)` | D-73 | `test_tts_voice_packs.py:305` | ✅ |

### Other plan AC references (not owned by MEU-73)

| AC | Owner | Status in MEU-73 |
|----|-------|------------------|
| AC-74.x | MEU-74 handoff | pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`) |
| AC-72.x | MEU-72 handoff | pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`); AC-72.8 by `PACKAGE_SMOKE` |
| AC-16.7 | existing `test_api_tts_models.py` (MEU-16) | untouched by MEU-73; pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`). TA-14 (D-95, MEU-74) adds `available`/`reason` to the expected voice dict. |
| AC-23.20 | existing `gui-actions-audit.test.ts` (MEU-23) | untouched by MEU-73; pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`). D-100 (row 13) adds no gui-actions-index row, because this audit cannot resolve a `writeClipboardText` settings cell. |
| AC-9.x | existing `test_tts_models.py` (MEU-9) | pass. AC-9.8 carries TA-1, AC-9.13's voice case carries TA-2, and AC-9.6/9.7 gained `write_voice_packs` setup lines. AC-9.12's import rule still holds. |
| AC-62.x | existing `test_tts_assets.py` (MEU-62) and `models-assets.test.ts` | pass. TA-3a, TA-8, TA-10, TA-11 and TA-12/13 are applied, and AC-62.13 carries TA-6. |
| AC-2.x | existing `test_domain.py` (MEU-2) | untouched by MEU-73. `VoiceConfig` keeps five fields under D-89, so AC-2.10/2.12 stay unaffected. |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| pytest AC-73.x (8 decisive) | AC assertion failures on the old code (for example, `state(VOICE_PACKS)`, `sys.path[-1]`, and the legacy row still downloaded) | pass | see AC table |
| pytest AC-73.x (16 import errors) | declared symbols absent: `voice_packs`, `ONNX_REPO`/`ONNX_REVISION`/`ONNX_LOCAL_DIR`, `variant_local_path`, `is_legacy_onnx_path`, `VOICE_PACKS` | pass | see AC table |
| TA-1 `test_ac_9_8_download_hf_map_returns_path_no_uow` | `HF_FILE_MAP_EXPECTED` names the v1.0 repo, but the catalog did not | pass | `test_tts_models.py` |
| TA-2 `test_ac_9_13_missing_vocab_voice_and_input_limit` | `DID NOT RAISE ModelLoadError` (the adapter did not read packs) | pass | `test_tts_models.py` |
| TA-11 `test_ac_62_1_required_assets_rule_and_closed_enums` | `TtsAsset` lacked `tts_voice_packs` | pass | `test_tts_assets.py` |
| ui Vitest AC-73.10/73.11 (7) | all 7 failed on `expect()`; the other 24 passed | pass, 31/31 | `settings-tts-runtime.test.ts` |
| mcp-server Vitest AC-73.13 (2) | the `asset` enum rejected `tts_voice_packs` (TA-6 pin `AC-62.13`) | pass, 20/20 | `models-assets.test.ts:59,64` |

Red, the TA dispositions and the Green design notes are in [walkthrough.md](../../../docs/execution/plans/2026-10-14-tts-engine-runtime/walkthrough.md) §MEU-73 Red and §MEU-73 Green.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s32-73-red","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check red-73 *> C:/Temp/av-kit/s32-red-73-run.txt","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"PY73 pytest, ui Vitest settings-tts-runtime + settings-page, mcp-server Vitest models-assets","phase":"red","exit_code":0,"result":"pass","tested_state":"baseline c72fc44 + MEU-73 tests and TA edits only; no MEU-73 production edit","output":"PASS red-73 pytest: 8 decisive AC assertions, 16 declared-symbol import errors, TEST_AMENDMENTS-file failures: test_ac_9_8, test_ac_9_13, test_ac_62_1 | PASS red-73 ui Vitest: 7 decisive, 24 passing | PASS red-73 mcp-server Vitest: 2 decisive, 7 passing; TA pin AC-62.13 failing | PASS red-73","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-73-green","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check green-73 *> C:/Temp/av-kit/s32-green-73-run.txt","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"PY73 pytest, ui Vitest (MEU-73 files), mcp-server build + Vitest models-assets + tools-parity","phase":"green","exit_code":0,"result":"pass","tested_state":"MEU-73 implementation on base c72fc44","output":"PASS pytest s32-green-73-pytest: 149 passed; baseline failures tolerated: [] | PASS s32-green-73-ui: 31 passed of 31 | PASS s32-green-73-mcp: 20 passed of 20 | PASS green-73","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-73-gate","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check gate73 *> C:/Temp/av-kit/s32-gate73-run.txt","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"pyright, ruff, ui/mcp typecheck and lint, PY73 pytest, full ui Vitest and full mcp-server Vitest against the baseline, OpenAPI two-step, ta-check","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-73 final working tree (base c72fc44 + MEU-73 diff)","output":"PASS pytest s32-gate73-pytest: 149 passed; baseline failures tolerated: [] | PASS s32-gate73-ui: 807 passed of 807 | PASS s32-gate73-mcp: 414 passed of 414 | PASS ta-check: existing test edits stay inside the 14 TEST_AMENDMENTS rows' ranges (TA-1..TA-13); append-only files only grew (base c72fc44) | PASS gate73","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-73-api-scope","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check api-scope *> C:/Temp/av-kit/s32-api-scope-73-run.txt","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"PRODUCT_SCOPE against baseline.sha (tracked + untracked), OpenAPI check, ta-check","phase":"static","exit_code":0,"result":"pass","tested_state":"MEU-73 final working tree (base c72fc44 + MEU-73 diff)","output":"PASS PRODUCT_SCOPE: 30 changed product files since c72fc44, all listed | PASS ta-check (base c72fc44) | PASS api-scope","fresh":true}
```

The full Python suite was run outside the gate: 677 passed and 2 failed. The two failures are `test_pack_dist_onedir_layout[AC-24.10]` and `test_nsis_pack_check_script[AC-25.10]`. Both need a built onedir and installer, and both already fail in the row-0 baseline. The authoritative full gate is `WINDOWS_GATE` (H1-2).

**Authoritative gate (H1-2, attempt 2).** `windows-gate-result.json` and `package-smoke-result.json` are bound to one `WORKTREE_IDENTITY` (`cd879e6e…`). Attempt 1 missed `AC-63.5` and `AC-49.28` under host load; both passed 10/10 alone, with no file changed between attempts (walkthrough §Windows gate).

```json
{"schema_version": "evidence.v1", "check_id": "s32-h1-windows-gate", "command": "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check windows-gate, then -Check package-smoke, then -Check windows-gate-check (H1-2; log C:/Temp/av-kit/s32-h1-gate-run.txt)", "cwd": "P:/av-kit-wt/tts-engine-runtime", "scope": "17 PROFILE D6 stages (full pytest, full Vitest, full Electron E2E, types, lint, builds, OpenAPI, SSOT render), PACKAGE_SMOKE, and the binding check", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "Session 32 final working tree on HEAD c72fc44, WORKTREE_IDENTITY cd879e6ef3f5f16a7266c0a66afbf19f284baa6863bc2fa17c1bc599f2611e18 at start and end of the gate and the smoke", "output": "PASS WINDOWS_GATE (17/17; pytest 803/0, Vitest 816/816, Electron 138/0/0/0 flaky 0) | PASS PACKAGE_SMOKE (offline 41,400 samples, negative probe Failed, MCP probe unreachable) | PASS windows gate + package smoke @ cd879e6ef3f5", "fresh": true}
```

### Quality Gate Results

```
pyright packages/: 0 errors
ruff check packages/ tests/: clean (ruff format drift is pre-existing at c72fc44, not gated)
ui + mcp-server typecheck, ui lint: clean
pytest PY73: 149 passed
ui Vitest full: 807/807 (COUNT_FLOORS 800)
mcp-server Vitest full: 414/414
OpenAPI: regenerated; --check passes; diff adds only tts_voice_packs
ta-check: 14 TA rows, base c72fc44
PRODUCT_SCOPE: 30 files, all listed
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/tts.py` | modified | +14/−1 | `VOICE_PACKS`, `LEGACY_ONNX_DIR`, `is_legacy_onnx_path`, `required_tts_assets` |
| `packages/core/src/avkit_core/domain/health.py` | modified | +1 | `tts_voice_packs` |
| `packages/core/src/avkit_core/services/health.py` | modified | +1 | maps the pack state |
| `packages/core/src/avkit_core/services/models.py` | modified | +51/−21 | legacy rows read not downloaded; legacy load 409; `MODEL_CHAINS_PACKS` |
| `packages/infrastructure/src/avkit_infra/tts/voices.py` | modified | +46 | `ONNX_REPO`/`ONNX_REVISION`/`ONNX_LOCAL_DIR`, pack constants, `variant_local_path`, `voice_pack_path`, `voice_pack_ready` |
| `packages/infrastructure/src/avkit_infra/tts/assets.py` | modified | +64/−5 | `VOICE_PACKS` state and `_download_packs`; `fetch_pack` injection; `activate_spacy_dir` appends |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | +40/−18 | `_voice_pack`; ONNX style row from the pack; PyTorch voice tensor |
| `packages/infrastructure/src/avkit_infra/model_manager/manager.py` | modified | +32/−8 | v1.0 repo, revision and `local_dir`; legacy skip in the fast path and sideload |
| `packages/infrastructure/src/avkit_infra/model_manager/voice_packs.py` | new | 1–33 | `fetch_voice_pack` |
| `packages/api/src/avkit_api/{schemas/health.py,schemas/models.py,routes/health.py,wiring.py}` | modified | +6/−2 | wire, dependencies field, `fetch_pack` injection |
| `openapi.committed.json` | modified | +9/−6 | `tts_voice_packs` only |
| `ui/src/renderer/src/features/tts/{tts-assets.ts,useTtsJob.ts}` | modified | +33/−3 | Voice packs wire and label; `useRefreshDependenciesOnSettle` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | +4 | calls the hook; `tts_voice_packs` row type |
| `mcp-server/src/toolsets/models.ts` | modified | +1/−1 | `TTS_ASSET_WIRES` |
| tests | new / modified | see `git diff --stat` | `test_tts_voice_packs.py`, `test_tts_voice_packs_service.py`, `test_api_tts_runtime.py`, `tts_g2p_fakes.py`, `settings-tts-runtime.test.ts` (new); TA edits and `write_voice_packs` setup lines in existing files |

```diff
+        if self._assets.state(TtsAsset.VOICE_PACKS, dest_dir) is not AssetState.READY:
+            variant_id, target_asset = None, TtsAsset.VOICE_PACKS
+            on_progress(0.0)
+            try:
+                self._assets.download(TtsAsset.VOICE_PACKS, dest_dir, on_progress)
+            except Exception as exc:
+                message = f"{TtsAsset.VOICE_PACKS.value} download failed: {exc}"
+                raise ModelDownloadError(message) from exc
```

```diff
-        pack = pipeline.load_single_voice(voice.voice_id)
-        ...
-        if style.shape[1] != 256:
-            style = np.resize(style, (1, 256)).astype(np.float32)
+        # ONNX_FEEDS: the style row is indexed by the token count, after unknowns are dropped.
+        pack = self._voice_pack(voice.voice_id)
+        style = pack[max(min(len(input_ids), PACK_ROWS) - 1, 0)].reshape(1, STYLE_DIM)
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

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-90
    stage: execution
    question: "Row 2: TA-3a names test_tts_assets.py:597-610, but line 611 asserts the message of the failure TA-3a replaces. Widen the range or leave 611 failing?"
    resolution: autonomous
    class: two-way
    chosen: "Widen TA-3a to 597-611. The forced FakeSession.run failure is a non-domain 500, sent through raise_server_exceptions=False, and the failed job id is read from tts_jobs."
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-tts-engine-runtime/walkthrough.md §Execution amendments Row 2 — TA-3a range"]
    research: { engine: none, sources: [] }
    reasoning: "Line 611 checks the error text of the exact failure being replaced, so it must change with 603-610. The plan's range stopped one line short. No AC or new TA id changes, and ta-check enforces the new range."
  - id: D-91
    stage: execution
    question: "Stop condition S1 fired during row 2: the branch was fast-forwarded to c72fc44, the Session 31 merge. How do the baseline and COUNT_FLOORS follow?"
    resolution: autonomous
    class: two-way
    chosen: "Re-point baseline.sha to c72fc44, re-derive COUNT_FLOORS as 800 / 137 / 655, and move the prereq S1 guard to c72fc44."
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-tts-engine-runtime/walkthrough.md §Execution amendments Row 2 S1 — measurements and receipts"]
    research: { engine: none, sources: [] }
    reasoning: "No MEU-73 product file had changed yet, so ta-check and api-scope must diff against the tree MEU-73 builds on. The floors are the larger of Session 31's gate and a measurement of the merged tree."
  - id: D-92
    stage: execution
    question: "AC-73.10 Downloading tests flaked because a refetch issued while the first fetch is in flight is deduped into it. Is a setup change allowed?"
    resolution: autonomous
    class: two-way
    chosen: "Add the setup helper waitForRuntimeDownloading() before the state flip. No assertion or expected value changes."
    source_tag: Local Canon
    precedents: ["AGENTS.md — assertions immutable in Green; fixture repairs may fix setup"]
    research: { engine: none, sources: [] }
    reasoning: "The flipped state otherwise arrives at the next 1 s poll, just past vi.waitFor's 1 s default. Only the setup is synchronised, and the assertions are untouched."
  - id: D-93
    stage: execution
    question: "The useEffect-keyed settle hook missed Downloading to Failed in about 3 of 5 runs. Keep it or change the mechanism?"
    resolution: autonomous
    class: two-way
    chosen: "useRefreshDependenciesOnSettle subscribes to QueryCache 'updated' events for the runtime query and invalidates on a Downloading exit."
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/tts/useTtsJob.ts — useRefreshDependenciesOnSettle"]
    research: { engine: none, sources: [] }
    reasoning: "When React batches two runtime results into one render, Downloading is never rendered. That is a real product race, so the cache event stream is the reliable source. The test passed 6/6 consecutive runs after the change."
  - id: D-94
    stage: execution
    question: "pyright rejects a torch tensor for KPipeline's voice parameter, which is annotated str | None. How should the PyTorch voice be typed?"
    resolution: autonomous
    class: two-way
    chosen: "Type the (510, 1, 256) tensor Any at the call site, with a comment citing kokoro load_voice."
    source_tag: Research-backed
    precedents: ["kokoro pipeline.py:157-158 — load_voice returns a FloatTensor argument unchanged"]
    research: { engine: none, sources: [] }
    reasoning: "The runtime accepts the tensor; only the annotation is narrow. A cast at the one call site keeps pyright at 0 errors without a suppression comment. KPipeline is removed in MEU-72 anyway."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-15 | claude-code | Initial handoff after gate73 and api-scope |
| Reconciled | 2026-10-15 | claude-code | H1-5: added the authoritative H1-2 gate record (`WINDOWS_GATE` 17/17 + `PACKAGE_SMOKE` @ `cd879e6e`) |
