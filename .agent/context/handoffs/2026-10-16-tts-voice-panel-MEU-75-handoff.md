---
date: "2026-10-17"
project: "2026-10-16-tts-voice-panel"
meu: "MEU-75"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md"
build_plan_section: "bp03s3.8"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex via local dispatch"
predecessor: "none"
---

# Handoff: 2026-10-16-tts-voice-panel-MEU-75-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-75 — `svc-tts-device-fallback`.
- `DEVICE_PROBE`: `runtime_devices(fmt)` in `tts/adapter.py` reports what the installed runtime can use. PyTorch: `Auto` and `CPU` always, `CUDA` iff `torch.cuda.is_available()`, `MPS` iff `torch.backends.mps.is_available()` (read with `getattr`), and `(Auto, CPU)` when `torch` is not installed. ONNX: `CUDA` iff `"CUDAExecutionProvider"` is in `onnxruntime.get_available_providers()`; never `MPS`. A runtime query that raises lists no such device and logs one `tts.device_probe_failed` warning (`format`, `device`, `error`), so the catalog still answers and a CPU load still works (D-21, execution review R1 F1). `KokoroAdapter(device_probe=...)` takes an injected probe and defaults to `runtime_devices`.
- `DEVICE_RESOLVE`: `_resolve` replaces `_resolve_device`. `Auto` picks CUDA, then MPS, then CPU from the probe with no log. An explicit device the probe lacks loads on CPU and logs one `tts.device_fallback` (`requested`, `actual="cpu"`, `reason="unavailable"`).
- `LOAD_FALLBACK`: `_load_pytorch` and `_load_onnx` build in locals, and the adapter fields are set only after success. PyTorch retries a failed `.to(<non-cpu>)` once on CPU (`reason="load_failed"`); the `KModel` constructor and `.eval()` are final. ONNX retries a CUDA session that raises, or whose `get_providers()` raises, on the CPU providers (`reason="load_failed"`), and a CUDA session whose active providers lack CUDA reports `cpu` (`reason="provider_fallback"`). A CPU failure logs `tts.load_failed` and raises `ModelLoadError` with the original cause and no weight path in the message. Nothing else in `load_model` escapes as a bare exception (D-21): a raising injected probe, a raising vocab resolver and an unreadable weight file (`PermissionError` from `stat`) each raise `ModelLoadError` with their cause.
- `LOAD_ERROR_HTTP`: `DOMAIN_HTTP_MAP[ModelLoadError] = 422`, so the load route returns the `ModelLoadError` code and message in place of a masked 500.
- `DEVICE_FIELD`: `TTSPort.available_devices`, `KokoroAdapter.available_devices`, `ModelService.available_devices`, and the required `ModelVariantOut.devices` (array of `auto`/`cuda`/`cpu`/`mps`) on every model-list row. `openapi.committed.json` was regenerated; only `ModelVariantOut` changed.
- `TEST_AMENDMENTS` TA-1 to TA-4 were applied as the plan states: TA-1 `test_tts_models.py` scopes a CUDA-reporting `monkeypatch.context()` to the one explicit-CUDA load in AC-9.4; TA-2 `FakeModels.available_devices` → `(Auto, CPU)`; TA-3 `TTS_PORT_METHODS` gains `available_devices`; TA-4 `FakeTTSPort.available_devices`.

**Build Plan Section**: `docs/build-plan/03-service-layer.md` §TTS device resolution (residual) (registry 3.8)
**Predecessor**: none. MEU-79 ([handoff](2026-10-16-tts-voice-panel-MEU-79-handoff.md)) consumes `devices` in the renderer.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-75.1 | unit | `runtime_devices(PyTorch)` over the cuda/mps matrix, with `torch` patched to `None`, with a torch lacking `backends.mps`, and in a fresh interpreter with torch blocked → `(Auto, CPU)`; cuda False is never CUDA. | Spec 03:466 | `tests/integration/test_tts_device_resolution.py:187` `test_ac_75_1_pytorch_probe_matrix`; `tests/integration/test_tts_no_torch.py:150` `test_ac_75_1_pytorch_probe_without_torch_is_auto_and_cpu` | ✅ |
| AC-75.2 | unit | `runtime_devices(ONNX)` reads `get_available_providers()`: CUDA only with `CUDAExecutionProvider`; TensorRT alone is not CUDA; MPS never. | Spec 03:466 | `test_tts_device_resolution.py:210` `test_ac_75_2_onnx_probe_reads_available_providers` | ✅ |
| AC-75.3 | unit | A CPU-only probe loads an explicit `CUDA` or `MPS` PyTorch request on CPU, status `cpu`, one `tts.device_fallback` with `reason="unavailable"`; a `CPU` request and an available `CUDA` log none. | Spec 03:465; triage D-66 | `test_tts_device_resolution.py:231` `test_ac_75_3_unavailable_device_loads_on_cpu_with_one_warning`, `:255` `…_available_or_cpu_request_logs_no_fallback_neg` | ✅ |
| AC-75.4 | unit | PyTorch `LOAD_FALLBACK`: `.to("cuda")` raising retries on CPU (`load_failed`); a CPU retry failure, a constructor failure (not retried) and an `.eval()` failure each raise `ModelLoadError` with the cause, log `tts.load_failed`, leave the adapter unloaded on `cpu`, and keep the weight path out of the message. | Spec 03:465, 03:467 | `test_tts_device_resolution.py:309` `test_ac_75_4_pytorch_to_failure_retries_once_on_cpu`, `:330` `…_cpu_retry_failure_raises_model_load_error`, `:357` `…_constructor_failure_is_wrapped_and_not_retried`, `:377` `…_eval_failure_is_final` | ✅ |
| AC-75.5 | unit | ONNX `LOAD_FALLBACK`: CUDA session without the CUDA provider → `cpu`/`provider_fallback`; CUDA constructor raising and unreadable providers → CPU retry/`load_failed`; CPU constructor raising → `ModelLoadError`; a CPU-only load never reads `get_providers`. Terminal state asserted after a prior CUDA load. | Spec 03:465 | `test_tts_device_resolution.py:398` `test_ac_75_5_onnx_cuda_session_without_cuda_provider_reports_cpu`, `:420` `…_cuda_constructor_failure_retries_on_cpu`, `:443` `…_unreadable_providers_retries_on_cpu`, `:463` `…_cpu_failure_raises_model_load_error`, `:486` `…_cpu_only_loads_never_read_providers` | ✅ |
| AC-75.6 | unit | `Auto` → CUDA, else MPS, else CPU, with no `tts.device_fallback`; ONNX `Auto` on a CPU probe builds one CPU session. | `DEVICE_RESOLVE` | `test_tts_device_resolution.py:275` `test_ac_75_6_auto_prefers_cuda_then_mps_then_cpu`, `:294` `test_ac_75_6_onnx_auto_on_cpu_probe_builds_one_cpu_session` | ✅ |
| AC-75.7 | unit | `KokoroAdapter.available_devices` returns the injected probe's result; `ModelService.available_devices` returns its port's; TA-3 and TA-4 applied. | `DEVICE_FIELD` | `test_tts_device_resolution.py:500` `test_ac_75_7_adapter_available_devices_returns_the_probe`; `tests/unit/test_services.py:2201` `test_ac_75_7_model_service_available_devices_returns_the_port_value`; `tests/unit/test_domain.py` (TA-3 protocol check) | ✅ |
| AC-75.8 | integration | Every `/models/available`, `/models/downloaded` and `POST /models/download` variant carries `devices` (`['auto','cpu']`, or `['auto','cuda','cpu']` with a CUDA fake); OpenAPI requires it with the four-name enum; `device: "tpu"` is 422. | Spec 03:466 | `tests/e2e/test_api_tts_models.py:199` `test_ac_75_8_variant_payloads_carry_devices`, `:206` `test_ac_75_8_openapi_requires_devices`, `:215` `test_ac_75_8_unknown_device_is_422_neg` | ✅ |
| AC-75.9 | integration | `ModelLoadError` → 422 with its code and message; a `RuntimeError` on load stays the masked 500; contract: a real adapter with a CPU-only probe behind the load route returns `device == "cpu"` for a `cuda` request, and `/models/status` agrees. R1 F1 regressions: a raising runtime query lists no such device, with one `tts.device_probe_failed` per failed query; with ONNX enumeration raising, CPU, CUDA and Auto loads still build one CPU session (CUDA logs `reason="unavailable"`), and so does a PyTorch CUDA load with raising torch queries; a raising injected probe, vocab resolver or weight-file `stat` raises `ModelLoadError` with that cause, logs `tts.load_failed` and leaves nothing loaded; over HTTP, `/models/available` answers 200 with `auto` and `cpu`, and `cpu` and `cuda` loads answer 200 on `cpu`. R2 F2 regression: a lazy `kokoro` import that raises a non-`ImportError` (`OSError`, `RuntimeError`) raises `ModelLoadError("PyTorch model failed to load")` with that cause, logs one `tts.load_failed`, builds nothing and leaves nothing loaded; over HTTP the load answers 422 `ModelLoadError`. | Spec 03:465, 03:467, 03:468, 03:469 | `tests/e2e/test_api_error_surface.py:274` `test_ac_75_9_model_load_error_maps_to_422`, `:282` `test_ac_75_9_runtime_error_on_load_stays_masked_neg`; `test_tts_device_resolution.py:520` `test_ac_75_9_load_route_reports_the_actual_device`, `:563` `test_ac_75_9_failing_runtime_query_lists_no_such_device_neg`, `:588` `test_ac_75_9_failing_runtime_query_still_loads_on_cpu`, `:616` `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg`, `:657` `test_ac_75_9_unreadable_weight_file_is_model_load_error_neg`, `:681` `test_ac_75_9_failing_runtime_query_http_catalog_and_load`, `:730` `test_ac_75_9_engine_import_failure_is_model_load_error_neg` | ✅ |
| AC-75.10 | integration | The real probe agrees with the installed torch and onnxruntime (no hard-coded host). | 07 §GPU; R-1 | `test_tts_device_resolution.py:772` `test_ac_75_10_real_probe_agrees_with_installed_runtimes` | ✅ |

### Other plan AC references (not owned by MEU-75)

| AC | Owner | Status in MEU-75 |
|----|-------|------------------|
| AC-79.1 to AC-79.10 | [MEU-79 handoff](2026-10-16-tts-voice-panel-MEU-79-handoff.md) | ✅ (rows 4–5) |
| AC-9.4 | existing `tests/integration/test_tts_models.py` | passes with TA-1 applied; no other assertion changed |
| AC-56.3 | existing `ui/tests/unit/tts-page.behavior.test.ts` | passes unchanged (TA-5: no line change; `cpu` is inside the default `['auto','cpu']`) |
| AC-64.6 | existing `ui/tests/e2e/tts-generate.test.ts` | passes in the gate's full Electron run and in `e2e-repeat` (×10) |
| AC-76.4 | existing `tests/e2e/test_api_error_surface.py` | passes unchanged: it raises a base `DomainError`, which `LOAD_ERROR_HTTP` does not map |
| AC-87.6, AC-87.7 | Session 37 (`capture-editor-options`), not a Session 35 AC | n/a: the plan cites them only in research note R-6, as real Session 37 receipts that `red-check.py --require` was tested against |
| AC-40.6, AC-40.30 | capture tests from an earlier session, not a Session 35 AC | n/a: the plan cites them only in §Execution Correction Notes (A-3), the clock-second race fixed in `capture-picker.test.ts` and `capture-lifecycle.test.ts` on Mat's ruling; both pass in the H1-2 gate record |
| AC-41.3 | queue-canon, an earlier session, not a Session 35 AC | n/a: the plan cites it only in §Execution Correction Notes (A-1), the one baseline-accepted `ui-tests` failure (`QUEUE-PILL-TOKEN-DRIFT`), which also failed at row 0 |
| AC-66.14 | capture-inbox E2E from an earlier session, not a Session 35 AC | n/a: the plan cites it only in §Execution Correction Notes (A-4), the pan-origin flake (`CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`) that failed post-F2 gate attempt 1; it passes in the H1-2 gate record |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (snippet) | Green Output | File:Line |
|------|----------------------|--------------|-----------|
| AC-75.3–.7 adapter tests (14) | `TypeError: KokoroAdapter.__init__() got an unexpected keyword argument 'device_probe'` | pass | `test_tts_device_resolution.py:231-500` |
| AC-75.1, AC-75.2, AC-75.10 | `ImportError: cannot import name 'runtime_devices'` (the torch-blocked subprocess surfaces it as `assert 1 == 0` on its return code) | pass | `test_tts_device_resolution.py:187,210,772`; `test_tts_no_torch.py:150` |
| AC-75.7 service | `AttributeError: 'ModelService' object has no attribute 'available_devices'` | pass | `test_services.py:2201` |
| AC-75.8 (2) | `assert None == ['auto', 'cpu']` (`.get("devices")`); `'devices' in required` | pass | `test_api_tts_models.py:199,206` |
| AC-75.9 map | `assert None == 422` (`DOMAIN_HTTP_MAP.get(ModelLoadError)`) | pass | `test_api_error_surface.py:274` |
| AC-75.9 R1 F1 (4) | `RuntimeError: provider enumeration failed` (probe and CPU load); `RuntimeError: probe failed` (bare, not `ModelLoadError`); HTTP `assert 500 == 200` with the `internal_error` body | pass | `test_tts_device_resolution.py:563,588,616,681` |
| AC-75.9 R1 F1 sibling (1) | `PermissionError: access denied` (bare, from the weight-file `stat`) | pass | `test_tts_device_resolution.py:657` |
| AC-75.9 R2 F2 (1) | `OSError: engine dependency DLL initialization failed` (bare, from the lazy `kokoro` import) | pass | `test_tts_device_resolution.py:730` |

The two `_neg` tests (AC-75.8 `tpu` → 422 and AC-75.9 masked 500) passed at Red, as bounds that already held. Red: `23 failed, 2 passed, 147 deselected`; red-check `0 problem(s)`. The R1 F1 rows were written after execution review round 1, before the correction. Their Red runs were `4 failed, 1 passed, 17 deselected` (the pass is the existing AC-75.9 route test) and `1 failed, 1 passed, 21 deselected` (`-k unreadable` also selects the existing AC-75.5 unreadable-providers test). The R2 F2 row was written after execution review round 2, before its correction; its Red run was `1 failed, 23 deselected`.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s35-75-red","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 2 command, verbatim","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"MEU-75 Red: pytest -k ac_75 over the MEU-75 test files with TA-1 to TA-4, then red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 baseline product code plus the row 2 tests and TA-1 to TA-4","output":"pytest 23 failed, 2 passed, 147 deselected (TypeError device_probe x14, ImportError runtime_devices x5, AttributeError available_devices x1, assertion x3) | red-check: 1 receipt(s), 0 required test(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s35-75-green","command":"RECEIPTS_DIR=C:/Temp/av-kit pwsh: task.md row 3 command, verbatim","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"MEU-75 Green: the seven row pytest files unfiltered, export_openapi --check, renderer guard, mcp-server build and tests","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus the MEU-75 product and test change","output":"pytest 172 passed, 1 warning | export_openapi --check exit 0 | no change under ui/src | mcp tsc no errors | MCP Test Files 26 passed (26), Tests 428 passed (428)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s35-75-f1-red","command":"rtk proxy uv run pytest tests/integration/test_tts_device_resolution.py -k ac_75_9 -q --tb=line -p no:cacheprovider > C:/Temp/av-kit/s35-f1-red-py.txt 2>&1 (then -k unreadable > C:/Temp/av-kit/s35-f1-red2-py.txt)","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"Execution review R1 F1 Red: the five new AC-75.9 regressions against the round 1 adapter","phase":"red","exit_code":1,"result":"fail","tested_state":"round 1 reviewed tree (6097cf5 plus the MEU-75/79 change) plus the five new tests","output":"4 failed, 1 passed, 17 deselected (RuntimeError provider enumeration failed; RuntimeError probe failed; HTTP 500 internal_error) | 1 failed, 1 passed, 21 deselected (PermissionError access denied)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s35-75-f1-green","command":"rtk proxy uv run pytest tests/integration/test_tts_device_resolution.py tests/integration/test_tts_no_torch.py tests/integration/test_tts_models.py tests/e2e/test_api_tts_models.py tests/e2e/test_api_error_surface.py -q --tb=short -p no:cacheprovider > C:/Temp/av-kit/s35-f1-green-py.txt 2>&1","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"Execution review R1 F1 Green: the MEU-75 adapter, no-torch, model and API test files unfiltered, after the D-21 correction; ruff check packages/ tests/ and pyright packages/ clean","phase":"green","exit_code":0,"result":"pass","tested_state":"round 1 reviewed tree plus the D-21 adapter correction and its tests","output":"60 passed, 1 warning | ruff All checks passed! | pyright 0 errors","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s35-75-f2-red","command":"rtk proxy uv run pytest tests/integration/test_tts_device_resolution.py -k engine_import_failure -q --tb=line -p no:cacheprovider > C:/Temp/av-kit/s35-f2-red-py.txt 2>&1","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"Execution review R2 F2 Red: the new AC-75.9 engine-import regression against the round 2 adapter","phase":"red","exit_code":1,"result":"fail","tested_state":"round 2 reviewed tree (6097cf5 plus the MEU-75/79 change and the R1 correction) plus the new test","output":"1 failed, 23 deselected (OSError engine dependency DLL initialization failed)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s35-75-f2-green","command":"rtk proxy uv run pytest tests/integration/test_tts_device_resolution.py tests/integration/test_tts_no_torch.py tests/integration/test_tts_models.py tests/e2e/test_api_tts_models.py tests/e2e/test_api_error_surface.py -q --tb=short -p no:cacheprovider > C:/Temp/av-kit/s35-f2-green-py.txt 2>&1","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"Execution review R2 F2 Green: the same five test files unfiltered after the D-23 correction; ruff check packages/ tests/, ruff format --check on the two files and pyright packages/ clean","phase":"green","exit_code":0,"result":"pass","tested_state":"round 2 reviewed tree plus the D-23 adapter correction and its test","output":"61 passed, 1 warning | ruff All checks passed! | 2 files already formatted | pyright 0 errors","fresh":true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s35-75-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; RECEIPTS_DIR=C:/Temp/av-kit rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-tts-voice-panel/session-gate.ps1 *> C:/Temp/av-kit/s35-gate-h1.txt (task.md H1-2, verbatim)", "cwd": "P:/av-kit-wt/s35-tts-voice-panel", "scope": "D6 session gate re-run at H1-2 after the execution review R2 F2 correction (D-23), which followed the R1 F1 correction (D-21) and the row 7 hub and SSOT edits; the second post-F2 attempt, after A-4 (capture-inbox AC-66.14 flake, re-run unchanged); earlier post-R1 attempts were governed by A-2 and A-3; the fresh full record", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "6097cf59adc7835fa6062c8bd3d55c679aef4543+b4e8b8826bfc3656e7084cc3e63b7682214f97ad1d1b5ad141e4640573211051", "output": "scope-paths changed paths: 39 outside scope: [] | all steps exit 0 | py-tests exit 1 accepted by the baseline rule: failed=2 outside_baseline=[] errors=0 (pytest 2 failed, 935 passed, 1 warning; AC-24.10, AC-25.10) | ui-tests exit 1 accepted by A-1: failed=1 summary_failed=1 outside_baseline=[] unhandled=0 (Vitest Tests 1 failed | 980 passed (981); queue-canon AC-41.3) | MCP Tests 428 passed (428) | openapi --check 0 | state-render Drift check passed | Electron 161 passed (5.7m) | e2e-repeat 50 passed (2.2m) (AC-79.7 to AC-79.10 and AC-64.6 x10) | @playwright/test@1.62.1 electron@42.9.3 | identity before == after", "fresh": true}
```

### Quality Gate Results

The shared gate is `session-gate.ps1`. Row 6 passed on its first run after amendment A-1, at `tested_state 6097cf5…+38f98d80…6e09`. Row 7 then changed bound inputs (the hub docs, `meu-status.yaml` and the rendered `BUILD_PLAN.md`), so H1-2 re-ran the whole gate. Execution review round 1 then found F1 (MEU-75, D-21), and its correction changed the adapter and its tests, so H1-2 ran the whole gate again. Its first attempt failed only at `ui-electron`, on the known transcript-queue W2-5 timeout (`DOWNLOAD-QUEUE-DRAG-OVER-MISS`; W2-5 then passed 4/4 alone). Amendment A-2 re-ran the whole gate with no file change. Attempt 2 then failed at `ui-tests` on a clock-second race in `capture-picker.test.ts` AC-40.6, a test this session never touched; Mat ruled to fix the race (A-3: the two affected tests pin `Date`, and `scope-paths` allows them). Attempt 3 passed at `6097cf5…+c7e4a6b9…32e3` and was the record that execution review round 2 reviewed. Round 2 confirmed F1 fixed and found F2 (MEU-75, D-23): a failing lazy `kokoro` import escaped bare. Its correction changed the adapter and its test, so H1-2 ran the whole gate again. The first post-F2 attempt failed only at `ui-electron`, on `capture-inbox.test.ts` AC-66.14, a pan-origin flake in an earlier session's test (5/5 alone; known issue `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`). Amendment A-4 re-ran the whole gate with no file change. That run is the record above, at `tested_state 6097cf5…+b4e8b882…1051`, and `identity.py --state-only` re-derives the same state from the live tree (H1-6b).

The gate script has two changes from the approved plan. **A-3** only adds `ui/tests/unit/capture-picker.test.ts` and `ui/tests/unit/capture-lifecycle.test.ts` to the `scope-paths` allowlist. **A-1** (D-19): `ui-tests` applies the plan's baseline rule (§Verification Plan 1) the way `py-tests` already did. A Vitest exit 1 is accepted only when:
- every `FAIL` id is the one expected id, queue-canon AC-41.3, and that id also failed in row 0's `s35-base-ui.txt`;
- the summary's failed count equals the number of ids;
- nothing is unhandled.

A 9-case probe (`walkthrough.md` §Gate) passed the real receipt shape and refused every other case. AC-41.3 reads the Zorivest hexes live, and Zorivest 1f254832 changed them. The known issue `QUEUE-PILL-TOKEN-DRIFT` records it, and no Session 35 file is among the test's inputs.

| Step | Stage | Exit | Decisive line (H1-2) |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 6097cf5…+b4e8b882…1051` |
| py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract | static | 0 | pyright, ruff, tsc and eslint clean; task lint 0 |
| scope-paths | static | 0 | `changed paths: 39 outside scope: []` |
| py-tests | full | 1 → accepted | `2 failed, 935 passed, 1 warning`; `py-tests baseline rule: failed=2 outside_baseline=[] errors=0` (AC-24.10, AC-25.10) |
| ui-tests | full | 1 → accepted (A-1) | `Tests 1 failed | 980 passed (981)`; `ui-tests baseline rule: failed=1 summary_failed=1 outside_baseline=[] unhandled=0` |
| mcp-build, mcp-tests | full | 0 | `Tests 428 passed (428)` |
| ui-build, ui-harness-build, ui-picker-stub | full | 0 | — |
| openapi | full | 0 | `export_openapi --check` exit 0; H1-4: only `ModelVariantOut` changed |
| state-render | full | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` |
| ui-electron | runtime | 0 | `161 passed (5.7m)` (the full Electron suite; `SegmentedControl` is shared) |
| e2e-repeat | runtime | 0 | `50 passed (2.2m)` (AC-79.7 to AC-79.10 and AC-64.6, `--repeat-each=10`) |
| identity-npm | identity | 0 | `@playwright/test@1.62.1 electron@42.9.3` |
| identity-after | identity | 0 | `tested_state before == after` |

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | +175/−43 | `runtime_devices`, `_query` (`tts.device_probe_failed`), `DeviceProbe`, `device_probe=`, `_resolve` (guarded in `load_model`), `_require_weight_path` (`stat` guarded), `_load_pytorch` (vocab resolved inside the guard; a lazy `kokoro` import that fails to initialize is a `ModelLoadError`), `_load_onnx`, `available_devices`, fallback and load-failed logs |
| `packages/core/src/avkit_core/ports/tts.py` | modified | +5/−1 | `TTSPort.available_devices` |
| `packages/core/src/avkit_core/services/models.py` | modified | +4/−1 | `ModelService.available_devices` |
| `packages/api/src/avkit_api/schemas/models.py` | modified | +4 | `DeviceWire`, required `ModelVariantOut.devices` |
| `packages/api/src/avkit_api/routes/models.py` | modified | +25/−5 | `_DEVICE_TO_WIRE`; `_variant_out(variant, devices)` at every call site |
| `packages/api/src/avkit_api/errors.py` | modified | +2 | `ModelLoadError: 422` |
| `openapi.committed.json` | regenerated | +15/−1 | `ModelVariantOut.devices` and its `required` entry only |
| `tests/integration/test_tts_device_resolution.py` | new | 1–789 | AC-75.1–.7, .9 contract, R1 F1 and R2 F2 regressions, .10 |
| `tests/integration/test_tts_no_torch.py` | modified (append only) | +30 | AC-75.1 torch-blocked interpreter |
| `tests/unit/test_services.py` | modified | +15/−1 | AC-75.7 service half; TA-4 |
| `tests/e2e/test_api_tts_models.py` | modified (append only) | +55/−1 | AC-75.8 |
| `tests/e2e/test_api_error_surface.py` | modified (append only) | +51/−2 | AC-75.9 |
| `tests/e2e/api_fakes.py` | modified (TA-2 only) | +6 | `FakeModels.available_devices` |
| `tests/integration/test_tts_models.py` | modified (TA-1 only) | +5/−1 | CUDA-reporting context for the one explicit-CUDA load |
| `tests/unit/test_domain.py` | modified (TA-3 only) | +8/−1 | `TTS_PORT_METHODS` gains `available_devices` |

```diff
 DOMAIN_HTTP_MAP: dict[type[DomainError], int] = {
     ExtractError: 422,
+    ModelLoadError: 422,
     NotFoundError: 404,
```

```diff
-def _variant_out(variant: Any) -> ModelVariantOut:
+def _variant_out(variant: Any, devices: tuple[DeviceType, ...]) -> ModelVariantOut:
     path = None if variant.path is None else str(variant.path)
     return ModelVariantOut(
@@
         is_downloaded=variant.is_downloaded,
+        devices=[_DEVICE_TO_WIRE[device] for device in devices],
     )
```

```diff
             try:
                 moved = loaded.to(target)
             except Exception:
                 if target == "cpu":
                     raise
                 _log_fallback(variant, target, "load_failed")
                 tried = "cpu"
                 moved = loaded.to("cpu")
             model = moved.eval() if hasattr(moved, "eval") else moved
         except Exception as exc:
             _log_load_failed(variant, tried, exc)
             raise ModelLoadError("PyTorch model failed to load") from exc
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
  - id: D-19
    stage: execution
    question: "The gate fails fast at ui-tests on queue-canon AC-41.3, which already failed at baseline because of an external Zorivest commit. How does row 6 apply the plan's baseline rule?"
    resolution: autonomous
    class: two-way
    chosen: "Amendment A-1: session-gate.ps1 applies the plan §1 baseline rule to ui-tests as it already did for py-tests (expected id excused only if row 0's s35-base-ui.txt shows it FAIL; summary count must match; no unhandled error)"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md:285 — a test failing at baseline is never counted as a regression", "docs/execution/plans/2026-10-16-capture-editor-options/ui-baseline-rule.ps1 — Session 37 A-4, Mat chose the same ui-tests rule on 2026-10-16", ".agent/context/known-issues.yaml QUEUE-PILL-TOKEN-DRIFT — open, the fix is a separate re-port"]
    research: { engine: none, sources: [] }
    reasoning: "The plan's own rule and row 6 text already require baseline failures to be listed and not counted; the script implemented that for py only. Re-porting the Zorivest hexes is outside PRODUCT_SCOPE, and leaving the gate as it was would stop every runtime step as not_run. The rule is narrow (one listed id, verified against the row 0 receipt), disclosed in walkthrough §Gate, and reversible."
  - id: D-21
    stage: execution
    question: "Execution review R1 F1: a runtime availability query that raises escaped load_model and the catalog as a bare RuntimeError (HTTP 500). What does a failing query do?"
    resolution: autonomous
    class: two-way
    chosen: "DEVICE_PROBE treats a raising query as that device absent and logs tts.device_probe_failed; Auto and CPU stay listed, so the catalog answers and a CPU load works, and an explicit request for the device falls back through DEVICE_RESOLVE (reason unavailable). load_model wraps anything else that could escape bare (a raising injected probe, vocab resolver or weight-file stat) in ModelLoadError with its cause"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:469 — any load failure the adapter cannot map raises ModelLoadError with the cause, never a bare exception", "docs/build-plan/03-service-layer.md:465-467 — a device the runtime cannot use falls back to CPU, logged", "docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md:131 — load_model raises ModelLoadError only", ".agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md F1 — keep the CPU path usable where possible"]
    research: { engine: none, sources: [] }
    reasoning: "A device whose availability cannot be read cannot be used, which is the unavailable case the plan already routes to CPU with a logged reason; failing the whole load or the catalog instead would block a CPU load that works, which F1 reproduced. A new 4xx or a retry was rejected: neither the spec nor the plan asks for one. The weight-file stat and vocab resolver are the two other statements in load_model outside a guard (sibling sweep), so they get the same wrapping."
  - id: D-23
    stage: execution
    question: "Execution review R2 F2: the lazy kokoro import in _load_pytorch caught only ImportError, so a dependency that fails to initialize (an OSError from a native DLL, say) escaped as a bare exception (HTTP 500). What does that failure do?"
    resolution: autonomous
    class: two-way
    chosen: "_load_pytorch keeps ImportError as the not-bundled ModelLoadError and maps any other exception from the import to ModelLoadError('PyTorch model failed to load') with its cause, after one tts.load_failed log; nothing is loaded"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:469 — any load failure the adapter cannot map raises ModelLoadError with the cause, never a bare exception", "docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md:131 — load_model raises ModelLoadError only", ".agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md F2 — include lazy engine import and initialization in the terminal load-error guard"]
    research: { engine: none, sources: [] }
    reasoning: "The engine is installed but cannot start, so the load fails on this host; that is a terminal load failure, the same class as a constructor failure, so it takes the same message and log. Keeping ImportError separate preserves the existing not-bundled reason. Retrying on CPU was rejected: the import has no device. Sweep: this was the only load-time import in the adapter; the module-level torch import runs at sidecar start, outside the load path."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-17 | claude-code | Initial handoff after the H1-2 gate |
| Corrected | 2026-10-17 | claude-code | Execution review R1 F1 (D-21): five Red-first AC-75.9 regressions, adapter correction, H1-2 gate re-run; the gate record above is the re-run |
| Corrected | 2026-10-17 | claude-code | Execution review R2 F2 (D-23): one Red-first AC-75.9 engine-import regression, adapter correction, H1-2 gate re-run (after A-4); the gate record above is that re-run |
