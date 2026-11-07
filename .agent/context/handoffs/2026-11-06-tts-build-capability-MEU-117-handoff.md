---
date: "2026-11-06"
project: "tts-build-capability"
meu: "MEU-117"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-06-tts-build-capability-MEU-117-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-117 `svc-tts-build-capability` (`TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME`, P2, triage D-217). A variant whose runtime doesn't import in this process is listed with `available: false` and a fixed reason. Its download answers 409 before any work, its load answers 422 with the same reason, and the TTS page lists it disabled and never selects it. D-237 (espeak is never downloaded or bundled) still binds, and nothing here downloads or bundles it.
**Build Plan Section**: [03 §TTS build capability (residual)](../../../docs/build-plan/03-service-layer.md).
**Predecessor**: none. The [MEU-118 handoff](2026-11-06-tts-build-capability-MEU-118-handoff.md) is the same plan's other MEU; it reads the `devices` and `available` this MEU lists.

- **Capability source (rows 1, 2; D-309).**
  - `runtime_imports` (`tts/adapter.py:103`, `RUNTIME_PROBE`) answers whether a format's runtime imports here. ONNX is always present. For PyTorch it returns `False` when `torch` doesn't import, before any kokoro import request, so `IMPORT_HYGIENE` (AC-72.1) holds in the packaged build.
  - With torch present, a failed `kokoro` import returns `False` and logs one `tts.runtime_probe_failed` WARNING (`:119`) with `format` and `error`, the class name only; the exception text never leaves the adapter.
  - `KokoroAdapter.runtime_present` (`:274`, `RUNTIME_PRESENT`) asks the injected probe at most once per format, under a lock. A probe that raises stores nothing. `TTSPort.runtime_present` is the port method (`ports/tts.py:45`).
- **Reasons (D-310, D-312 option A).** `MODEL_REASONS` (`domain/tts.py:336`) holds the two fixed texts, "This build can't run PyTorch models. Choose an ONNX model." and "This build can't run ONNX models. Reinstall av-kit.". `ModelAvailability` (`:343`) is `available` with `reason` set exactly when not available, and `model_availability` (`:357`) builds it. The adapter's own PyTorch refusals now raise that same text (`tts/adapter.py:342`, `:350`), so the amended AC-98.5 and AC-115.9 tests expect it.
- **Service (rows 3, 4; D-311, `MODEL_REFUSAL`).**
  - `ModelService.availability` (`services/models.py:111`, `AVAILABILITY`) reads the port.
  - `load` raises `ModelLoadError(reason)` after `NotFoundError` and before the legacy and vocab checks, and logs `model.load_refused` with `variant_id` and `detail` (`:165-166`). So the port is never called and no spaCy download starts.
  - `download` warms the probe before the lock, because the first PyTorch probe imports kokoro. Under the lock the in-flight 409 comes first with today's text (`:232`), then `NotFoundError`, then `ConflictError(reason)` with `model.download_refused` (`:239-240`), all before `_start_locked`. So no job starts and no file is written.
- **API (`MODEL_FIELDS`, D-318).** `ModelVariantOut` gains `available` and `reason` (`schemas/models.py:51-52`), and `_variant_out` (`routes/models.py:43`) fills them for every route that returns a variant (`:56-57`). `CONFLICT_409` and the download docstring name the variant this build can't run. `openapi.committed.json` was regenerated: the two new fields, the download description and the two 409 descriptions that share `CONFLICT_409` changed.
- **MCP (D-318).** The `avkit_models` `available` description names `devices`, `available` and `reason`, and `download`'s names the 409 (`mcp-server/src/toolsets/models.ts:17-30`). The JSON passes through unchanged.
- **Renderer (rows 5 to 7; D-320).**
  - `SelectInput` gains `disabled?` on an option (`SelectInput.tsx:9`, `:62`), and the option keeps `style={g30}`, so AC-94.2 to AC-94.4 still pass.
  - `CatalogItem` gains `available` and `reason` (`useTtsJob.ts:60`, `:62`). The TTS page lists an unavailable row disabled, labelled "PyTorch FP32 — {reason}" (`TTSPage.tsx:467-478`).
  - `defaultModelSelection` (`tts-controls.ts:111`) skips an unavailable row in the chosen, first-downloaded and first-row rules, keeps the loaded row, and counts a row without `available` as available.
- **Packaged and dev checks (rows 8, 9; D-315, D-316).**
  - `tools/smoke_packaged_tts.py --phase capability` (`CAPABILITY_SMOKE`, `phase_capability` at `:533`) runs a fresh onedir copied outside the checkout, offline behind dead proxies, with a 16-byte stub `kokoro-v1_0.pth` and no download. It checks `listed_fields`, `download_refused`, `load_refused` and `logged` (`:583-585`).
  - `dev-pytorch-check.py` (`DEV_CHECK`) loads `kokoro-pt-fp32` on `cpu` from the repo's `.venv` and generates a WAV. `models-snapshot.py` shows the real models folder unchanged (159 files).
- **Spec text.** 03, 04, 05 and 06 were updated as §Spec text lists. 03 gained the MEU-117 Delivered note (row 13).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md) §MEU-117. **Execution authorization:** `USER_EXPLICIT`, 2026-11-06, "proceed", given after the Codex plan review approved in round 1 ([plan-critical-review.md](2026-11-06-tts-build-capability-plan-critical-review.md)), accepting every gate default (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-117.1 | unit | `model_availability(PyTorch, False)` is `available` false with `MODEL_REASONS[PyTorch]`, and `(fmt, True)` is available with `reason` `None` for both formats. `MODEL_REASONS` has a key for every `ModelFormat` and holds the §Reasons texts exactly. `ModelAvailability(True, "x")`, `(False, None)` and `(False, "")` raise `ValidationError`. AC-4.7 is amended to list `runtime_present`. | Human-approved (triage D-217: a reason that names a next step) | `tests/unit/test_domain.py:1642`; amended AC-4.7 at `:1326` | ✅ |
| AC-117.2 | integration | `runtime_imports`: ONNX gives `True`. With `torch` patched to `None`, PyTorch gives `False`, logs nothing and makes no kokoro import request. A kokoro `ImportError("SYNTHETIC_IMPORT_MARKER")` gives `False` and one `tts.runtime_probe_failed` WARNING with `format` `PyTorch` and `error` `ImportError`, with the marker in no field. An `OSError` gives `error` `OSError`. A fake `kokoro` holding `KModel` gives `True` and no log. | Human-approved (triage D-217: "torch without kokoro counts as unavailable") | `tests/integration/test_tts_device_resolution.py:955` | ✅ |
| AC-117.3 | integration | `runtime_present` calls the injected probe once per format across 8 threads released together by a barrier (with a timeout) and returns its answer. With no probe injected, it calls the module's `runtime_imports`. | Local Canon (D-309) | `tests/integration/test_tts_device_resolution.py:990` | ✅ |
| AC-117.4 | integration | The amended `test_ac_98_5_torch_absent_logs` and `test_ac_98_5_kokoro_import_logs` expect `MODEL_REASONS[PyTorch]` with the same log line and cause. The amended `test_ac_115_9_load_failed_carries_detail` expects it as `detail`. | Local Canon (03 §TTS build capability, "Load") | `tests/integration/test_tts_device_resolution.py:838`, `:855`, `:902` | ✅ |
| AC-117.5 | integration | In a subprocess with `torch`, `phonemizer` and `espeakng_loader` blocked and kokoro importable, `KokoroAdapter().runtime_present(PyTorch)` is `False` and `(ONNX)` is `True`, and a `sys.meta_path` recorder sees no request for `kokoro`. | Local Canon (`IMPORT_HYGIENE`, AC-72.1) | `tests/integration/test_tts_no_torch.py:201` | ✅ |
| AC-117.6 | unit | `ModelService.download` with PyTorch absent raises `ConflictError` with the reason. The runtime stays `Idle`, `FakeCatalog.entered` is never set, and one `model.download_refused` WARNING carries `variant_id` and `detail`. The in-flight 409 comes first with today's text, an unknown id raises `NotFoundError`, and with the format present the download starts as today. | Human-approved (triage D-217: 409 before any download starts) | `tests/unit/test_services.py:3201` | ✅ |
| AC-117.7 | unit | `ModelService.load` of an unavailable variant raises `ModelLoadError` with the reason before the legacy and vocab checks (the fixture's vocab is missing). The port's `load_model` isn't called, no spaCy download starts, and one `model.load_refused` WARNING is logged. An unknown id still raises `NotFoundError`. | Local Canon (03, "Load"; 01 §Domain errors) | `tests/unit/test_services.py:3244` | ✅ |
| AC-117.8 | e2e | Through a real `ModelService` with PyTorch absent and a stub `kokoro-v1_0.pth`: `GET /models/available` lists the PyTorch row with `available: false`, the reason and `is_downloaded: true`, and each ONNX row available with `reason: null`; `/models/downloaded` carries the same fields. `POST /models/download` gives 409 `ConflictError` with the reason, the runtime reads `Idle`, the catalog wasn't entered and the folder is unchanged. `POST /models/load` gives 422 `ModelLoadError`. With PyTorch present, the download gives 202 and the catalog is entered once. | Human-approved (triage D-217; the brief's contract test "with no job and no file written") | `tests/e2e/test_api_model_capability.py:85`, `:127` | ✅ |
| AC-117.9 | e2e | In `openapi.committed.json`, `ModelVariantOut` has `available` (boolean) and `reason` (string or null), and the `/models/download` 409 description names the variant this build can't run. | Local Canon (04 `ModelVariantOut`) | `tests/e2e/test_api_tts_models.py:226`; gate `openapi` | ✅ |
| AC-117.10 | unit | `available`'s description names `devices`, `available` and `reason`, and `download`'s names the 409 for a variant this build can't run. Both keep the four markers. | Local Canon (03, "MCP") | `mcp-server/tests/models-availability.test.ts:23` | ✅ |
| AC-117.11 | unit | A guard: a mocked `available` answer with `available: false` and a `reason` comes back unchanged, and a mocked download 409 gives `TOOL_ERROR` "ConflictError: {reason}" after one fetch. | Local Canon (03, "MCP": the same fields and 409) | `mcp-server/tests/models-availability.test.ts:37` | ✅ |
| AC-117.12 | unit | With the PyTorch row unavailable, the TTS page's PyTorch option is disabled, labelled "PyTorch FP32 — {reason}", an ONNX row is selected, and every option keeps the G30 style. | Human-approved (triage D-217: "shows the row disabled with the reason") | `ui/tests/unit/tts-page.behavior.test.ts:889` | ✅ |
| AC-117.13 | unit | `defaultModelSelection` skips an unavailable chosen row, the first-downloaded and first-row rules skip unavailable rows, the loaded row is kept, it returns `null` when no row is available, and a row without `available` counts as available. | Human-approved (triage D-217: "`defaultModelSelection` skips it") | `ui/tests/unit/tts-model-selection.test.ts:14` | ✅ |
| AC-117.14 | e2e | In Electron, through the TTS seam with an unavailable PyTorch row, the model select's PyTorch option is disabled with the reason in its label, and an ONNX row is selected. | Local Canon (E2) | `ui/tests/e2e/tts-generate.test.ts:891` (row 7; gate `ui-electron`) | ✅ |
| AC-117.15 | smoke | `CAPABILITY_SMOKE` on a fresh onedir copied outside the checkout passes all four checks. | Human-approved (the brief's Done; 03, "Tests") | `tools/smoke_packaged_tts.py:533` (row 8; gate `package-build`, `smoke-capability`) | ✅ |
| AC-117.16 | smoke | `DEV_CHECK` loads `kokoro-pt-fp32` on `cpu` from the repo's `.venv` and generates a WAV of more than 8000 samples, with `available: true` listed. | Human-approved (triage D-217, "Dev") | `docs/execution/plans/2026-11-06-tts-build-capability/dev-pytorch-check.py` (row 9; gate `dev-pytorch`) | ✅ |
| AC-4 (cross-ref) | regression | AC-4.7 is amended under AC-117.1 to list `runtime_present` in the port's method set. AC-4.1 to AC-4.7 pass in the gate | plan §MEU-117 | `tests/unit/test_domain.py:1326` (gate `py-tests`) | ✅ |
| AC-98 (cross-ref) | regression | The two AC-98.5 tests are amended under AC-117.4 to expect `MODEL_REASONS[PyTorch]`. The rest of AC-98 passes in the gate | plan §MEU-117 | `tests/integration/test_tts_device_resolution.py:838`, `:855` (gate `py-tests`) | ✅ |
| AC-115 (cross-ref) | regression | AC-115.9's last block is amended under AC-117.4 to expect the reason as `detail` | plan §MEU-117 | `tests/integration/test_tts_device_resolution.py:902` (gate `py-tests`) | ✅ |
| AC-72 (cross-ref) | regression | AC-72.1 still passes: an ONNX generate without torch or kokoro, and `runtime_imports` returns before any kokoro import | plan §Capability source | `tests/integration/test_tts_no_torch.py:112` (gate `py-tests`) | ✅ |
| AC-94 (cross-ref) | regression | AC-94.2 to AC-94.4 still pass: the disabled option keeps `style={g30}` | plan §Renderer | `ui/tests/unit/theme-selects.test.tsx:202`, `:235`, `:265` (rows 6, 11; gate `ui-tests`) | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged, so the byte-hash tests AC-51.6 and AC-81.13 pass | plan §Files Modified | `ui/tests/unit/layout-primitives.test.ts:200`, `ui/tests/unit/capture-action-row.test.ts:710` (gate `ui-tests`) | ✅ |
| AC-118 (cross-ref) | — | Owned by the MEU-118 handoff (the Settings device options and the TTS page's device floor) | plan §MEU-118 | [MEU-118 handoff](2026-11-06-tts-build-capability-MEU-118-handoff.md) | see MEU-118 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-117.1 to AC-117.5, amended AC-4.7, AC-98.5 ×2, AC-115.9 | Row 1: "avkit_core.domain.tts has no ModelAvailability" and "has no MODEL_REASONS"; AC-4.7's method set lacks `runtime_present`; `runtime_imports` and `runtime_present` are missing | Row 2: pass | `test_domain.py:1326`, `:1642`; `test_tts_device_resolution.py:838-990`; `test_tts_no_torch.py:201` |
| AC-117.6 to AC-117.9 | Row 3: "DID NOT RAISE ConflictError"; the load gives `('kokoro-pt-fp32', 'ConflictError', 'tts asset missing: tts_onnx_vocab')`, not `ModelLoadError` with the reason; the listed rows and `ModelVariantOut` have no `available` | Row 4: pass | `test_services.py:3201`, `:3244`; `test_api_model_capability.py:85`, `:127`; `test_api_tts_models.py:226` |
| AC-117.10, AC-117.11 | Row 3: neither description names the fields or the 409. AC-117.11 is a guard and passes by design | Row 4: pass | `models-availability.test.ts:23`, `:37` |
| AC-117.12, AC-117.13 | Row 5: the PyTorch option is enabled with the label "PyTorch FP32 — downloaded"; `defaultModelSelection` returns `kokoro-pt-fp32` (e.g. "expected 'kokoro-pt-fp32' to be null") | Row 6: pass | `tts-page.behavior.test.ts:889`, `tts-model-selection.test.ts:14` |
| AC-117.14 | No Red of its own: its negative is row 5's AC-117.12 Red | Row 7: pass in Electron | `tts-generate.test.ts:891` |
| AC-117.15 | Row 8: the same phase on the pre-session onedir (`C:/Temp/av-kit/s51/backend-before`) stopped at `listed_fields`, each row reading `available: '<absent>'`, before any download request | Row 8: PASS on a fresh onedir | `tools/smoke_packaged_tts.py:533` |
| AC-117.16 | A guard: row 0's `--baseline` run passed, and the strict run fails if the probe reports PyTorch absent in the dev venv | Row 9: PASS strict | `dev-pytorch-check.py` |

- **Row 1 Red:** 8 failed, 2 passed and 79 deselected. The 2 passes are AC-117.2's and AC-117.3's ONNX-only subcases, outside `--require`. `red-check.py` required 8 tests and found 0 problems.
- **Row 3 Red:** 5 failed and 110 deselected, then 2 failed and 2 passed in the MCP file. The MCP passes are the AC-117.11 guards. `red-check.py` required 4 pytest tests and 1 MCP test, and found 0 problems in each.
- **Row 5 Red:** 6 failed and 32 passed in 2 files. `red-check.py` required AC-117.12 and AC-117.13 and found 0 problems.
- Every failure is the decisive assertion, never a collection or import error: each test first asserts that the new name or field exists.
- **Green:**
  - Row 2: 191 passed over the domain, adapter, no-torch and service suites; pyright 0 errors.
  - Row 4: 330 passed over the service, API, OpenAPI, asset and device suites; pyright 0 errors. MCP: 4 files, 95 passed.
  - Row 6: 6 files, 93 passed, with the G30 and palette suites; the UI typecheck passed.
  - Row 7: the UI build, then 22 of 22 Electron E2E tests in `tts-generate`.
  - Row 8: `PASS: smoke_packaged_tts capability`. Row 9: `PASS: dev-pytorch-check strict`, `wav_samples` 41400, and the models folder unchanged (159 files, 0 changes).

Receipts: `C:/Temp/av-kit/s51-port-red.txt` (with `.exit`), `s51-port-red-check.txt`, `s51-port-green.txt`, `s51-port-types.txt`, `s51-svc-red.txt` (with `.exit`), `s51-svc-red-check.txt`, `s51-mcp-red.txt` (with `.exit`), `s51-mcp-red-check.txt`, `s51-svc-green.txt`, `s51-mcp-green.txt`, `s51-mcp-types.txt`, `s51-ui-red.txt` (with `.exit`), `s51-ui-red-check.txt`, `s51-ui-green.txt`, `s51-ui-types.txt`, `s51-r7-build.txt`, `s51-r7-e2e.txt`, `s51-smoke-red.txt` (with `.exit` and `.json`), `s51-r8-build.txt`, `s51-smoke-green.txt` (with `.json`), `s51-r9-dev.txt`, `s51-r9-models.txt`, `s51-resolve.txt`, `s51-r13-*.txt`, the gate's `s51-gate-h1.txt` and `s51-D6-<id>.txt`, and `drift-check.txt` and `openapi-check.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-port-red", "command": "rtk proxy uv run pytest tests/unit/test_domain.py tests/integration/test_tts_device_resolution.py tests/integration/test_tts_no_torch.py -k \"ac_117_1 or ac_117_2 or ac_117_3 or ac_117_5 or ac_4_7 or ac_98_5 or ac_115_9\" --tb=short -q *> C:/Temp/av-kit/s51-port-red.txt; then red-check.py --require on the eight tests (abridged from task.md row 1's Validation cell, run from P:/av-kit, TMP and TEMP at C:/Temp/av-kit/s51/tmp)", "cwd": "P:/av-kit", "scope": "MEU-117 Red, domain and adapter: AC-117.1 to AC-117.5 and the amended AC-4.7, AC-98.5 x2 and AC-115.9 against the unchanged domain and adapter, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a (baseline.sha) plus row 1", "output": "8 failed, 2 passed, 79 deselected. Decisive, e.g. AssertionError: avkit_core.domain.tts has no ModelAvailability, and AC-4.7's method set lacks 'runtime_present'. red-check: 1 receipt(s), 8 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-port-green", "command": "rtk proxy uv run pytest tests/unit/test_domain.py tests/integration/test_tts_device_resolution.py tests/integration/test_tts_no_torch.py tests/unit/test_services.py --tb=short -q *> C:/Temp/av-kit/s51-port-green.txt; then rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s51-port-types.txt (abridged from task.md row 2's Validation cell, run from P:/av-kit, TMP and TEMP at C:/Temp/av-kit/s51/tmp)", "cwd": "P:/av-kit", "scope": "MEU-117 Green, domain and adapter, with the whole service suite", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 and 2", "output": "191 passed in 8.94s. pyright: 0 errors, 0 warnings, 0 informations."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-svc-red", "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/e2e/test_api_model_capability.py tests/e2e/test_api_tts_models.py -k \"ac_117_6 or ac_117_7 or ac_117_8 or ac_117_9\" --tb=short -q *> C:/Temp/av-kit/s51-svc-red.txt; then red-check.py --require on the four tests; then rtk proxy npm --prefix mcp-server run test -- tests/models-availability.test.ts *> C:/Temp/av-kit/s51-mcp-red.txt and red-check.py --require AC-117.10 (abridged from task.md row 3's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-117 Red, service, API and MCP: AC-117.6 to AC-117.11 against the unchanged service, routes and toolset", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 3", "output": "pytest: 5 failed, 110 deselected. Decisive, e.g. Failed: DID NOT RAISE ConflictError, and ('kokoro-pt-fp32', 'ConflictError', 'tts asset missing: tts_onnx_vocab') != ('kokoro-pt-fp32', 'ModelLoadError', \"This build can't run PyTorch models. Choose an ONNX model.\"). red-check: 1 receipt(s), 4 required test(s), 0 problem(s). MCP: Tests 2 failed | 2 passed (4); the passes are the AC-117.11 guards. red-check: 1 receipt(s), 1 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-svc-green", "command": "rtk proxy uv run pytest tests/unit/test_services.py tests/e2e/test_api_model_capability.py tests/e2e/test_api_tts_models.py tests/e2e/test_api_bodies.py tests/e2e/test_api_error_surface.py tests/e2e/test_api_openapi.py tests/e2e/test_api_tts_runtime.py tests/integration/test_tts_assets.py tests/integration/test_tts_voice_packs.py tests/integration/test_tts_device_resolution.py --tb=short -q *> C:/Temp/av-kit/s51-svc-green.txt; then pyright packages/, the OpenAPI export, and the MCP tests, typecheck and the models-availability file (abridged from task.md row 4's Validation cell, run from P:/av-kit, TMP and TEMP at C:/Temp/av-kit/s51/tmp)", "cwd": "P:/av-kit", "scope": "MEU-117 Green, service, API and MCP, with the API, OpenAPI, asset and device suites", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 4", "output": "330 passed in 22.98s. pyright 0 errors. MCP: Test Files 4 passed (4); Tests 95 passed (95)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-ui-red", "command": "rtk proxy npm --prefix ui run test -- tests/unit/tts-page.behavior.test.ts tests/unit/tts-model-selection.test.ts *> C:/Temp/av-kit/s51-ui-red.txt; then red-check.py --require AC-117.12 --require AC-117.13 (abridged from task.md row 5's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-117 Red, renderer: AC-117.12 and AC-117.13 against the unchanged page and selection", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 5", "output": "Tests 6 failed | 32 passed (38). Decisive, e.g. expected 'kokoro-pt-fp32' to be null, and expected [ 'PyTorch FP32 — downloaded', …(1) ] to deeply equal [ …(2) ]. red-check: 1 receipt(s), 2 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-ui-green", "command": "rtk proxy npm --prefix ui run test -- tests/unit/tts-page.behavior.test.ts tests/unit/tts-model-selection.test.ts tests/unit/tts-page.test.ts tests/unit/tts-run-bar.test.ts tests/unit/theme-selects.test.tsx tests/unit/palette-curation.test.tsx *> C:/Temp/av-kit/s51-ui-green.txt; then rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/s51-ui-types.txt (abridged from task.md row 6's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-117 Green, renderer, with the TTS page, run bar, G30 and palette suites", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 6", "output": "Test Files 6 passed (6); Tests 93 passed (93). Typecheck exit 0."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-e2e", "command": "rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s51-r7-build.txt; then rtk proxy npm --prefix ui run test:e2e -- tests/e2e/tts-generate.test.ts *> C:/Temp/av-kit/s51-r7-e2e.txt (abridged from task.md row 7's Validation cell, run from P:/av-kit, ELECTRON_RUN_AS_NODE cleared)", "cwd": "P:/av-kit", "scope": "MEU-117 AC-117.14 in Electron through the TTS seam, with the rest of tts-generate", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 7", "output": "UI build exit 0. 22 passed (33.1s), including AC-117.14 an unavailable PyTorch row is a disabled option with the reason, and an ONNX row is selected."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-smoke", "command": "rtk proxy uv run python tools/smoke_packaged_tts.py --phase capability --backend-dir C:/Temp/av-kit/s51/backend-before/avkit-backend --models-dir C:/Temp/av-kit/s51/smoke-models-before --out C:/Temp/av-kit/s51-smoke-red.json *> C:/Temp/av-kit/s51-smoke-red.txt (required to exit 1 at listed_fields); then rtk proxy uv run python tools/package_backend.py *> C:/Temp/av-kit/s51-r8-build.txt, the fresh onedir copied to C:/Temp/av-kit/s51/backend, and the same phase on it *> C:/Temp/av-kit/s51-smoke-green.txt (abridged from task.md row 8's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-117 AC-117.15, CAPABILITY_SMOKE: Red on the pre-session onedir, then Green on a fresh frozen build copied outside the checkout, offline behind dead proxies, with a 16-byte stub kokoro-v1_0.pth and no download", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 8", "output": "Red: exit 1, FAIL: smoke_packaged_tts capability, failed_check listed_fields, every row available '<absent>'. Green: listed_fields kokoro-pt-fp32 available false with \"This build can't run PyTorch models. Choose an ONNX model.\" and is_downloaded true, the ONNX rows available true with reason null; download_refused 409 ConflictError with the reason, runtime_state Idle, files_unchanged true; load_refused 422 ModelLoadError with the reason, stub_bytes 16; logged model.download_refused and model.load_refused. PASS: smoke_packaged_tts capability."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-117-dev", "command": "rtk proxy uv run python docs/execution/plans/2026-11-06-tts-build-capability/dev-pytorch-check.py *> C:/Temp/av-kit/s51-r9-dev.txt; then models-snapshot.py --compare models-before.json *> C:/Temp/av-kit/s51-r9-models.txt (abridged from task.md row 9's Validation cell, run from P:/av-kit, TMP and TEMP at C:/Temp/av-kit/s51/tmp)", "cwd": "P:/av-kit", "scope": "MEU-117 AC-117.16, DEV_CHECK in the repo's .venv, and the real models folder untouched", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 9", "output": "kokoro-pt-fp32 listed available true, loaded on cpu, wav_samples 41400. PASS: dev-pytorch-check strict. models-snapshot: 159 file(s) recorded, 0 change(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-row13-hub", "command": "task.md row 13's Validation cell, run from P:/av-kit through an extracted .ps1 (abridged): the issue-resolve receipt check, rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s51-r13-render.txt, rtk proxy uv run python tools/issue_triage.py render --check *> C:/Temp/av-kit/s51-r13-issues.txt, the two issue statuses and the grouping row", "cwd": "P:/av-kit", "scope": "Row 13 hub, shared by MEU-117 and MEU-118: the 03 and 06 Delivered notes, both MEUs ready_for_review, both issues resolved through issue-resolve.py, and grouping row 51 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 13", "output": "issue-resolve: 10 parsed fields changed (issues[82] and issues[98] status, verification, resolution_path), 67 of 67 decision logs read, 0 problem(s). Drift check passed. OK: known-issues.md is up-to-date. Statuses TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME resolved, TTS-DEVICE-OPTIONS-IN-CPU-BUILD resolved. Grouping tracker names the plan: True."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-06-tts-build-capability/session-gate.ps1 *> C:/Temp/av-kit/s51-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s51-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 13 and the AC-118.2 setup-sync fix (run 2; run 1 failed at ui-tests, see Execution notes): identity, every static check, both full suites, the UI build, OpenAPI, the MCP types, tests and build, both renders, the targeted Electron specs, the package build, the capability smoke on a fresh copy of the onedir outside the checkout, the strict dev PyTorch check and the models snapshot, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (30 rows, 28 fully checked, 2 view_file exempt); scope-paths exit=0 (changed paths: 53, outside scope: [], head moved: False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1274 passed); ui-tests exit=0 (112 files, 1163 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-tests exit=0 (35 files, 470 passed); mcp-build exit=0; state-render exit=0 (126 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ui-electron exit=0 (45 passed: settings 23, tts-generate 22); package-build exit=0; smoke-capability exit=0 (PASS: smoke_packaged_tts capability, failed_check null); dev-pytorch exit=0 (PASS: dev-pytorch-check strict, kokoro-pt-fp32 on cpu, wav_samples 41400); models-untouched exit=0 (159 files, 0 changes); identity-after exit=0 (tested_state before = after); mcp-audit and build-record skipped; baseline failures excused: py [], ui [], mcp []; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/drift-check.txt 2>&1 (H1-3's cell, run from Git Bash, so its *> became > 2>&1)", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here; row 13 set both MEUs ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62", "output": "Drift check passed: SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-h1-4-openapi", "command": "rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json > C:/Temp/av-kit/openapi-check.txt 2>&1 (H1-4's cell, run from Git Bash, so its *> became > 2>&1)", "cwd": "P:/av-kit", "scope": "H1-4: packages/api changed in this session, so the committed OpenAPI document is checked against the app", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62", "output": "exit 0; check_openapi prints nothing when openapi.committed.json matches the live schema"}
```

### Quality Gate Results

`s51-gate-h1-2` is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors, 0 warnings; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 30 rows (28 fully checked, 2 `view_file` exempt); scope-paths found 53 changed paths, none outside scope, and HEAD 71d0d3a did not move; the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** pytest 1274 passed (baseline 1265); Vitest 1163 passed in 112 files (baseline 1144 in 109); MCP tests 470 passed in 35 files (baseline 466 in 34). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render and the issue render match the files on disk.
- **Runtime:** the targeted Electron specs passed (45 of 45: `settings` 23, `tts-generate` 22). `package-build` built the onedir, and `smoke-capability` passed on a fresh copy of it outside the checkout. `dev-pytorch` passed strict (`kokoro-pt-fp32` on `cpu`, 41400 samples), and the real models folder was unchanged (159 files).
- **Skipped:** `mcp-audit` (live network and YouTube, which the brief forbids) and `build-record` (no installer build).
- **Identity:** the tested_state was the same before and after the gate: `71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62`. After H1-3 and H1-4, `identity.py --state-only` re-derives the same value.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/tts.py` | modified | `MODEL_REASONS`, `ModelAvailability`, `model_availability` |
| `packages/core/src/avkit_core/ports/tts.py` | modified | `TTSPort.runtime_present` |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | `runtime_imports`, the injected probe, `runtime_present`; the PyTorch refusals use `MODEL_REASONS` (D-312) |
| `packages/core/src/avkit_core/services/models.py` | modified | `availability`; the download 409 and load 422 refusals with their log lines |
| `packages/api/src/avkit_api/schemas/models.py`, `routes/models.py`, `openapi.committed.json` | modified | `available` and `reason`, `_variant_out`, `CONFLICT_409` and the download docstring; OpenAPI regenerated |
| `mcp-server/src/toolsets/models.ts` | modified | The `available` and `download` descriptions |
| `tools/smoke_packaged_tts.py` | modified | `phase_capability` and `--phase capability`; the docstring names the phase |
| `ui/src/renderer/src/components/ui/SelectInput.tsx`, `features/tts/useTtsJob.ts`, `tts-controls.ts`, `TTSPage.tsx` | modified | `disabled` on an option, the two catalog fields, the selection rule, the disabled row and label. `TTSPage.tsx` is shared with MEU-118 (`DEVICE_FLOOR`) |
| `tests/unit/test_domain.py`, `tests/integration/test_tts_device_resolution.py`, `test_tts_no_torch.py`, `tests/unit/test_services.py`, `tests/e2e/api_fakes.py`, `test_api_tts_models.py` | modified | AC-117.1 to AC-117.7 and AC-117.9; AC-4.7, AC-98.5 x2 and AC-115.9 amended; `FakeTTSPort.runtime_present`, `FakeModels.availability` |
| `tests/e2e/test_api_model_capability.py`, `mcp-server/tests/models-availability.test.ts`, `ui/tests/unit/tts-model-selection.test.ts` | new | AC-117.8, AC-117.10, AC-117.11, AC-117.13 |
| `ui/tests/unit/tts-page.behavior.test.ts`, `ui/tests/e2e/tts-generate.test.ts` | modified | AC-117.12, AC-117.14. The behavior file also holds MEU-118's AC-118.4 |
| `docs/build-plan/03`, `04`, `05`, `06` | modified | §Spec text; 03's Delivered note. CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md` | modified | MEU-117 and MEU-118 `ready_for_review` (row 13), shared with MEU-118 |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | Two issues resolved through `issue-resolve.py` (row 13), shared with MEU-118 |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modified | Row 51 `executed` with the plan folder. CRLF kept |
| `.agent/context/current-focus.md` | modified | Session 51 entry on top (H1-3). CRLF kept |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `identity.py`, `red-check.py`, `models-snapshot.py`, `models-before.json`, `dev-pytorch-check.py`, `issue-resolve.py`, `session-gate.ps1`, `task.md` | new or modified | The plan's scripts and records, shared with MEU-118 |

```diff
     def download(self, variant_id: str) -> ModelVariant:
         dest_dir = models_directory(self._settings)
+        # Warm the runtime probe before the lock: the first PyTorch probe imports kokoro.
+        with self._uow_factory() as uow:
+            row = uow.models.get(variant_id)
+        if row is not None:
+            self._tts.runtime_present(row.format)
         with self._lock:
             if self._runtime.state == "Downloading":
                 raise ConflictError("a model download is already in progress")
             ...
                 raise NotFoundError(f"model variant {variant_id} not found")
+            reason = self.availability(variant.format).reason
+            if reason is not None:
+                log.warning("model.download_refused", variant_id=variant.id, detail=reason)
+                raise ConflictError(reason)
             self._start_locked(variant, None, dest_dir)
```

The excerpt is abridged. `services/models.py:216-243` is the source.

---

## Codex Validation Report

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

Round 1 of loop `s51-execution-2026-11-06-tts-build-capability` returned `approved`, intent achieved `yes`, with no findings ([implementation-critical-review.md](2026-11-06-tts-build-capability-implementation-critical-review.md)). Its Q8 records two notes, neither a finding:

- **Identity.** In the reviewer's sandbox, `identity.py --state-only` listed `.claude/settings.local.json` as untracked and gave another value. That file dates from 2026-10-10 and is ignored by the user-level `~/.config/git/ignore`, which the sandbox doesn't read. With that one path left out, the reviewer reproduced the gate's tested_state exactly, and this shell's `identity.py --state-only` gives it unchanged.
- **Register note.** The register-resolve execution note below named the wrong issue for `.issues[82]`. It is `TTS-DEVICE-OPTIONS-IN-CPU-BUILD`, and the note is corrected.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `07-distribution.md:226` | out-of-scope | — | Mat's plan-gate ruling ("proceed" with the defaults): it stays out of this session |
| The rc.2 repeat of the packaged smoke | dependency | MEU-125 | D-315: this session runs it once; MEU-125 repeats it at the rc.2 gate |
| Load order and FP16 audio | dependency | Session 52 (MEU-119 to MEU-121) | The grouping's Session 52 follows and needs this one |
| Pre-existing pyright error in `tools/smoke_packaged_tts.py:414` (`__doc__.splitlines`, reportOptionalMemberAccess) | out-of-scope | — | It is at `HEAD` too, and `tools/` is outside the pyright include; `py-types` runs `pyright packages/`, which passes |
| Commit and push | out-of-scope | — | Waits for Mat's direction (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files from the task cells, because the cells' `*>` needs PowerShell.
- **Baseline.** Row 0's `npm ci` became a lock-sync check, because the avkit MCP server held `ui/node_modules/electron` open.
- **Spec anchors.** The plan's §Spec text said 03's anchor at `:588` becomes `tts/adapter.py:298-308`. The edit used `:340-350`, the refusals' lines after the change. The plan cites `_DEVICE_ORDER` at `adapter.py:67`; it is at `:71`.
- **Shared 409 text.** `CONFLICT_409` is also the `/models/load` 409 description. An unavailable variant there gives 422, and the load's 409 still covers the legacy file and the missing vocab. The OpenAPI diff therefore shows two changed 409 descriptions plus the download description ("Accept a variant or TTS-asset download immediately.\n\n409 if one is in flight, or the variant can't run in this build."), all within the §Spec text change.
- **Register resolve.** The first `issue-resolve.py` dry run refused with ".issues[82]: keys differ", because `TTS-DEVICE-OPTIONS-IN-CPU-BUILD` had no `resolution_path`. The script gained `set_fields`, which puts a missing key before `category`, and `differences` reports an added key at its own path, which must still be a named issue's `RESOLVE_KEYS`. A dry run to `--target` passed before the real write.
- **Gate run 1.** It failed at `ui-tests` on one test, `AC-118.2 a CUDA report offers auto, cuda and cpu` (`s51-gate-h1-run1.txt`, `s51-D6-ui-tests-run1.txt`). The select listed `auto, cpu`, the page's list before the report arrives. TanStack Query tells its observers about a new state on a `setTimeout(0)`, and the test's setup sync, `settled()`, flushed only a microtask after it saw the state, so the assertion could run before the page re-rendered. Only the CUDA test can see the stale render, because the CPU tests' early and final lists are both `auto, cpu`. Row 11's full suite had passed (1163).
  - The fix changes only that setup sync (`ui/tests/unit/settings-tts-device.test.ts:100-108`): after the state check it waits for a `setTimeout(0)` inside `act`. No assertion and no source file changed. The file then passed 15 runs of 15 on its own (`s51-h1-2-flake-loop.txt`) and the full UI suite twice (112 files, 1163 passed each, `s51-h1-2-ui-full-1.txt` and `-2.txt`).
  - The whole gate was rerun (run 2), and `s51-gate-h1-2` is that run. Run 1's static steps and `py-tests` (1274) had passed.
- **H1-3 and H1-4.** They ran from Git Bash, so each cell's `*>` became `> 2>&1`. The first `identity.py --state-only` after them read another value, because that shell had `ELECTRON_RUN_AS_NODE=1`, which the runtime identity hashes. With it unset, as the gate and H1-6b set it, the value equals the gate's.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Initial MEU-117 handoff after H1-2 |
| Reviewed | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 1 `approved`, from the canonical report; the register-resolve note corrected per its Q8 |
