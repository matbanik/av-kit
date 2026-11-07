---
date: "2026-11-07"
project: "tts-load-fp16"
meu: "MEU-119"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-06-tts-load-fp16-MEU-119-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-119 `svc-tts-load-keeps-model` (`TTS-FAILED-LOAD-DROPS-MODEL`, triage D-221), with D-335's home-folder scrub. A load whose weight, device, format or runtime check fails now leaves the loaded model in place, and a failed load's `detail` (and every other Console field) shows the home folder as `~`.
**Build Plan Section**: [03 §TTS load order (residual)](../../../docs/build-plan/03-service-layer.md), Delivered note at `:627`.
**Predecessor**: none. The [MEU-120 handoff](2026-11-06-tts-load-fp16-MEU-120-handoff.md) and the [MEU-121 handoff](2026-11-06-tts-load-fp16-MEU-121-handoff.md) are the same plan's other MEUs.

- **Load order (rows 1, 2; D-322, `LOAD_CHECKS`, `LOAD_KEEPS`).**
  - `load_model` (`tts/adapter.py:286`) now runs four checks before `self.unload_model()` (`:332`): the weight path (`:302-306`), the device probe (`:307-312`), the format (`:313-316`) and the runtime through `self.runtime_present` (`:317-331`). A load that fails one keeps the loaded model, its id and its device. The docstring (`:287-301`) says so.
  - Each failure still logs one `tts.load_failed` before it leaves (`LOAD_FAILURE_PATHS`). The missing-weight, device, format and absent-runtime lines are unchanged (`_log_load_failed`).
  - A raising runtime probe raises `ModelLoadError("TTS runtime probe failed")` from the cause, and its log line carries the cause's class as `error` and no `detail` (D-323), because a probe's text can hold a local path.
  - An absent runtime raises `ModelLoadError(MODEL_REASONS[format])`, MEU-117's text.
  - After the unload, nothing changes: the model or session is built in locals and assigned once every stage succeeds, so a `KModel` or CPU-session failure leaves nothing loaded on `cpu` (AC-119.7, AC-119.8 guards).
  - The runtime check reads MEU-117's memo (`RUNTIME_PRESENT`, `:274`), so a load through the API probes nothing new, and a direct caller probes once (AC-119.6).
- **Test setup (D-324, A′).** `_adapter` (`tests/integration/test_tts_device_resolution.py:132`) takes an optional `runtime_probe`. Two existing tests pass `lambda _fmt: True` as setup only: `test_ac_75_9_engine_import_failure_is_model_load_error_neg` (`:743`, A′ at `:749`) and `test_ac_98_5_kokoro_import_logs` (`:860`, A′ at `:865`). Their assertions are unchanged. Without it the new runtime check would refuse the load before the import failure they test.
- **Home-folder scrub (rows 2a, 2b; D-335, `HOME_SCRUB`).**
  - `services/health.py` gains `HOME_IGNORES_CASE` (`:60`, true on Windows), `home_folder` (`:96`) and `scrub_home` (`:104-117`).
  - `console_field` (`:120-126`) scrubs first, then replaces links, redacts and cuts. So the `FIELD_LIMIT` cut keeps no part of a user name.
  - A match starts a path and ends at a separator, a quote or the end. It handles `\`, `/` and the doubled `\\` an `OSError` quotes, and it keeps a longer user name, a nested path and a path inside another path. A bare drive or an empty home folder changes nothing.
  - The six log sites, `REDACT_NEEDLES` and AC-115.9's assertions are unchanged, as D-335 ruled. The missing-weight `detail` now reads `~\.avkit\models\…`.
- **Spec text.** 03 gained the MEU-119 Delivered note (`:627-635`, row 12). It records the 8.3 short-form limit at `:633`, which Mat ruled into a later plan (D-337, `CONSOLE-HOME-SCRUB-SHORT-FORM`).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md) §MEU-119. **Execution authorization:** `USER_EXPLICIT`, 2026-11-07, "D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed", given after the Codex plan review approved in round 4 ([plan-critical-review.md](2026-11-06-tts-load-fp16-plan-critical-review.md)); recorded in [human-gate-decision.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/human-gate-decision.md) (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

Each AC-119.1 to AC-119.6 test loads model A (ONNX FP32 on `cuda`), spies on `unload_model`, fails load B, and asserts the status is `(True, A.id, "cuda")`, the spy saw no call, and one `tts.load_failed` was logged.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-119.1 | unit | B's weight file is missing: "model weight file is missing", A kept | Local Canon: triage D-221 | `tests/integration/test_tts_device_resolution.py:1117` | ✅ |
| AC-119.2 | unit | The device probe raises on B: "TTS device probe failed" with the cause, A kept | Local Canon: triage D-221 | `test_tts_device_resolution.py:1128` | ✅ |
| AC-119.3 | unit | B is PyTorch and its runtime is absent (an injected probe says `False`): `MODEL_REASONS[PyTorch]`, logged on the target with `ModelLoadError`, A kept | Local Canon: triage D-221; MEU-117 `MODEL_REASONS` | `test_tts_device_resolution.py:1151` | ✅ |
| AC-119.4 | unit | The runtime probe raises on B: "TTS runtime probe failed" with the cause; the log carries the cause's class and no `detail`; A kept | Local Canon: D-323; Session 50 raw-value rule | `test_tts_device_resolution.py:1167` | ✅ |
| AC-119.5 | unit | B's format is neither PyTorch nor ONNX: the `ValidationError`, A kept | Local Canon: triage D-221 | `test_tts_device_resolution.py:1190` | ✅ |
| AC-119.6 | unit | On a fresh adapter, a load probes the format's runtime once through `runtime_present`, and a second load probes nothing more | Local Canon: brief ("reads MEU-117's capability source") | `test_tts_device_resolution.py:1206` | ✅ |
| AC-119.7 | unit | After the checks pass, a `KModel` constructor failure leaves nothing loaded on `cpu` (guard, passes in Red) | Local Canon: triage D-221; AC-75.4 | `test_tts_device_resolution.py:1230` | ✅ |
| AC-119.8 | unit | After the checks pass, an ONNX CPU session failure leaves nothing loaded on `cpu` (guard, passes in Red) | Local Canon: triage D-221; AC-75.5 | `test_tts_device_resolution.py:1245` | ✅ |
| AC-119.9 | contract | A real `ModelService` over a real `KokoroAdapter` (fake `InferenceSession`, `FakeAssets`, models folder under `tmp_path`): `POST /models/load` INT8 answers 200; FP32, whose row holds a path whose file is gone, answers 422 "model weight file is missing"; `GET /models/status` still shows INT8 on `cpu` | Local Canon: brief | `tests/e2e/test_api_model_load_keeps.py:77` | ✅ |
| AC-75.9 (amended) | unit | `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg` asserts A is still loaded after the failed probe | Local Canon: triage D-221; grouping scoping review round 1 | `test_tts_device_resolution.py:622` (the new assert at `:647`) | ✅ |
| AC-119.10 | unit | With `home_folder` patched to a synthetic `C:\Users\SYNTHETIC_HOME_USER`: `console_field` turns the home folder into `~` with `\`, `/` and doubled `\\` separators and alone at the end; follows `HOME_IGNORES_CASE`; keeps a look-alike user folder, a path outside the home folder and a path inside another path; with a 290-character prefix the cut keeps no part of the user name; a bare drive or an empty home folder changes nothing. Through a real `HealthService` with `log_to_file` on, one `log.error` with a home-folder `detail` and a doubled-backslash `OSError` `error` reaches the ring, stdout and `console.log` with `~` and without the user name | Human-approved: D-335; Session 50 raw-value rule | `tests/unit/test_services.py:3308`, `:3330`, `:3341`, `:3354`, `:3369` (5 cases), `:3379`; row 2b's TEMP-under-home run | ✅ |
| AC-75 (cross-ref) | regression | The A′ setup (D-324) in `test_ac_75_9_engine_import_failure_is_model_load_error_neg`; its assertions and the rest of AC-75 pass unchanged | plan §MEU-119 | `test_tts_device_resolution.py:743` (gate `py-tests`) | ✅ |
| AC-115 (cross-ref) | regression | `test_ac_115_9_load_failed_carries_detail` and the AC-115.9 and AC-115.10 Console tests pass unchanged; `detail` is still the cause's first line, single-line, redacted and cut, now with `~` for the home folder | plan §Home folder scrub | `test_tts_device_resolution.py:908`, `tests/unit/test_services.py:2644`, `tests/unit/test_console_level.py` (rows 2, 2b; gate `py-tests`) | ✅ |
| AC-117 (cross-ref) | regression | AC-117.8 (the service refuses an unavailable variant before the adapter) passes unchanged; the runtime check reads MEU-117's `runtime_present` | plan §Load order | `tests/e2e/test_api_model_capability.py` (row 2; gate `py-tests`) | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged, so the byte-hash tests AC-51.6 and AC-81.13 pass | plan §Files Modified | `ui/tests/unit/layout-primitives.test.ts:200`, `ui/tests/unit/capture-action-row.test.ts:710` (gate `ui-tests`) | ✅ |
| AC-100 (cross-ref) | — | Named in the plan only as `red-check.py`'s boundary example (`AC-100.7` never matches `AC-100.70`); no AC-100 test changes | plan §Verification Plan | gate `ui-tests` | ✅ |
| AC-58, AC-120 (cross-ref) | — | Owned by the MEU-120 handoff (the models-folder default and probe; the Settings E2E as AC-58.12) | plan §MEU-120 | [MEU-120 handoff](2026-11-06-tts-load-fp16-MEU-120-handoff.md) | see MEU-120 |
| AC-63, AC-121 (cross-ref) | — | Owned by the MEU-121 handoff (`PRESELECT_ORDER`, the sentence smoke and the FP16 spike; AC-63.x holds unchanged) | plan §MEU-121 | [MEU-121 handoff](2026-11-06-tts-load-fp16-MEU-121-handoff.md) | see MEU-121 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-119.1, AC-119.2, AC-119.5, amended AC-75.9 | Row 1: `assert (False, None, 'cpu') == (True, 'kokor...fp32', 'cuda')`: today the checks run after the unload, so the status is unloaded | Row 2: pass | `test_tts_device_resolution.py:622`, `:1117`, `:1128`, `:1190` |
| AC-119.3, AC-119.4 | Row 1: `Failed: DID NOT RAISE ModelLoadError`: today `load_model` has no runtime check, so B loads | Row 2: pass | `:1151`, `:1167` |
| AC-119.6 | Row 1: `assert ([], []) == ([<ModelFormat.ONNX...>])`: today a load probes nothing | Row 2: pass | `:1206` |
| AC-119.9 | Row 1: `assert (False, None, 'cpu') == (True, 'kokor...-int8', 'cpu')`: the FP32 422 left nothing loaded | Row 2: pass | `test_api_model_load_keeps.py:77` |
| AC-119.7, AC-119.8 | Guards: pass in Red by design (the build stages already used locals) | Row 2: pass | `:1230`, `:1245` |
| AC-119.10 | Row 2a: `assert hasattr(health_module, "home_folder")` gives `AssertionError: assert False` in all 10 tests | Row 2b: pass, then 230 passed with TEMP under the home folder | `test_services.py:3308-3415` |

- **Row 1 Red:** 8 failed, 12 passed and 22 deselected in 2.08s. The 12 passes are the guards (AC-119.7, AC-119.8, the two A′ tests and the rest of the selected AC-75.9 and AC-98.5 tests). `red-check.py` required 8 tests and found 0 problems.
- **Row 2a Red:** 10 failed and 104 deselected in 0.66s (AC-119.10's 6 test functions, the bare-drive one in 5 cases). `red-check.py` required `test_ac_119_10` and found 0 problems.
- Every failure is the decisive assertion, never a collection or import error. Each AC-119.10 test first asserts that the scrub's names exist (`_scrub_ready`, `test_services.py:3297`).
- **Green:**
  - Row 2: 238 passed over the device, no-torch, load-keeps, capability, TTS models and runtime API, service and domain suites; pyright 0 errors; the real models folder unchanged (159 files, 0 changes).
  - Row 2b: 117 passed over the service and Console-level suites; pyright 0 errors. Then, with `TMP` and `TEMP` at `~\AppData\Local\Temp\avkit-s52-home-tmp` (so pytest's temp paths sit under the home folder), the 10 Console-reading test files passed: 230 passed in 17.09s. No existing expectation changed (S14).

Receipts: `C:/Temp/av-kit/s52-load-red.txt` (with `.exit`), `s52-load-red-check.txt`, `s52-load-green.txt`, `s52-load-types.txt`, `s52-r2-models.txt`, `s52-scrub-red.txt` (with `.exit`), `s52-scrub-red-check.txt`, `s52-scrub-green.txt`, `s52-scrub-types.txt`, `s52-scrub-home-tmp-dir.txt`, `s52-scrub-home-tmp.txt`, `s52-resolve.txt`, `s52-r12-*.txt`, run 1's `s52-gate-r1/`, gate run 2's `s52-gate-h1-r2.txt` and `s52-D6-<id>.txt`, and `drift-check.txt` and `openapi-check.txt`. The `s52-scrub-home-tmp-dir.txt` receipt holds the real home path, so it is cited here and not pasted.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s52-119-load-red", "command": "$env:TMP='C:\\Temp\\av-kit\\s52\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/integration/test_tts_device_resolution.py tests/e2e/test_api_model_load_keeps.py -k \"ac_119 or ac_75_9 or ac_98_5\" --tb=short -q *> C:/Temp/av-kit/s52-load-red.txt; then red-check.py --require on the eight tests *> C:/Temp/av-kit/s52-load-red-check.txt (abridged from task.md row 1's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-119 Red, load order: AC-119.1 to AC-119.9 and the amended AC-75.9 against the unchanged adapter, with the A' setup in place, and red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 (baseline.sha) plus row 1", "output": "8 failed, 12 passed, 22 deselected in 2.08s. Decisive: assert (False, None, 'cpu') == (True, 'kokor...fp32', 'cuda') for AC-75.9, AC-119.1, AC-119.2 and AC-119.5; Failed: DID NOT RAISE ModelLoadError for AC-119.3 and AC-119.4; assert ([], []) == ([<ModelFormat.ONNX...>]) for AC-119.6; assert (False, None, 'cpu') == (True, 'kokor...-int8', 'cpu') for AC-119.9. red-check: 1 receipt(s), 8 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-119-load-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s52\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/integration/test_tts_device_resolution.py tests/integration/test_tts_no_torch.py tests/e2e/test_api_model_load_keeps.py tests/e2e/test_api_model_capability.py tests/e2e/test_api_tts_models.py tests/e2e/test_api_tts_runtime.py tests/unit/test_services.py tests/unit/test_domain.py --tb=short -q *> C:/Temp/av-kit/s52-load-green.txt; then rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s52-load-types.txt and models-snapshot.py --compare models-before.json *> C:/Temp/av-kit/s52-r2-models.txt (abridged from task.md row 2's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-119 Green, load order, with the device, no-torch, capability, API, service and domain suites and the real models folder", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 and 2", "output": "238 passed in 10.55s. pyright: 0 errors, 0 warnings, 0 informations. models-snapshot: 159 file(s) recorded, 0 change(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-119-scrub-red", "command": "$env:TMP='C:\\Temp\\av-kit\\s52\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_services.py -k ac_119_10 --tb=short -q *> C:/Temp/av-kit/s52-scrub-red.txt; then red-check.py --require test_ac_119_10 *> C:/Temp/av-kit/s52-scrub-red-check.txt (abridged from task.md row 2a's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-119 Red, home-folder scrub (D-335): AC-119.10 against the unchanged health.py, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1, 2 and 2a", "output": "10 failed, 104 deselected in 0.66s: the five AC-119.10 functions and the bare-drive one in its 5 cases. Decisive: assert hasattr(health_module, \"home_folder\") gives AssertionError: assert False. red-check: 1 receipt(s), 1 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-119-scrub-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s52\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_services.py tests/unit/test_console_level.py --tb=short -q *> C:/Temp/av-kit/s52-scrub-green.txt; then rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s52-scrub-types.txt; then TMP and TEMP set to $env:LOCALAPPDATA Temp\\avkit-s52-home-tmp, tempfile.gettempdir() *> C:/Temp/av-kit/s52-scrub-home-tmp-dir.txt, and the 10 Console-reading test files *> C:/Temp/av-kit/s52-scrub-home-tmp.txt, then TMP and TEMP restored and the folder removed (abridged from task.md row 2b's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-119 Green, home-folder scrub, with the Console-level suite, then the TEMP-under-home run of test_uow_commit_log, test_services, test_console_level, test_capture_adapter, test_api_captures, test_api_conversions, test_api_health_settings, test_transcript_block_done, test_transcript_failure_delivery and test_tts_assets", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 2b", "output": "117 passed in 6.39s. pyright: 0 errors, 0 warnings, 0 informations. tempdir is the home folder's AppData\\Local\\Temp\\avkit-s52-home-tmp. TEMP-under-home run: 230 passed in 17.09s."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-row12-hub", "command": "task.md row 12 (abridged), run from P:/av-kit: its task text runs rtk proxy uv run python docs/execution/plans/2026-11-06-tts-load-fp16/issue-resolve.py --issue TTS-FAILED-LOAD-DROPS-MODEL --issue MODELS-DIR-DOCS-AND-PROBE-MISMATCH --issue TTS-ONNX-FP16-NONFINITE-AUDIO --set-file C:/Temp/av-kit/s52-resolve.json --expect-sha256 $sha *> C:/Temp/av-kit/s52-resolve.txt, then issue_triage.py render and triage; its Validation cell, through an extracted .ps1, checks C:/Temp/av-kit/s52-resolve.txt for '^issue-resolve: 0 problem', then runs rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s52-r12-render.txt, rtk proxy uv run python tools/issue_triage.py render --check *> C:/Temp/av-kit/s52-r12-issues.txt, the three issue statuses and the grouping row *> C:/Temp/av-kit/s52-r12-status.txt", "cwd": "P:/av-kit", "scope": "Row 12 hub, shared by MEU-119, MEU-120 and MEU-121: the 03 and 06 Delivered notes, the three MEUs ready_for_review, two issues resolved and the FP16 issue's verification through issue-resolve.py, and grouping row 52 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12", "output": "decision logs read: 67 of 67; parsed fields changed: 13 (issues[99] and issues[100] status, verification.last_checked, method, result and resolution_path; issues[110] verification.last_checked, method and result); issue-resolve: 0 problem(s). Drift check passed: SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content. OK: known-issues.md is up-to-date. ['resolved', 'resolved', 'open']. grouping tracker names the plan: True."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-c5-registers", "command": "task.md row C5 (abridged), run from P:/av-kit in Git Bash: rtk proxy uv run python docs/execution/plans/2026-11-06-tts-load-fp16/issue-resolve.py --issue GUI-MODELS-PROBE-LEFTOVER-FILE --issue SMOKE-TTS-WAV-HEADER-TRUSTED --set-file C:/Temp/av-kit/s52-c5-resolve.json --expect-sha256 $SHA > C:/Temp/av-kit/s52-c5-resolve.txt 2>&1, then the two issues filed and MEU-127 registered through issue_triage's model and meu-status.yaml; its Validation cell, through an extracted .ps1, checks the resolve receipt for '^issue-resolve: 0 problem', then runs rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s52-c5-render.txt, rtk proxy uv run python tools/issue_triage.py render --check *> C:/Temp/av-kit/s52-c5-issues.txt, and the five issue statuses, the FP16 issue's meu_links and the MEU-127 entry *> C:/Temp/av-kit/s52-c5-status.txt", "cwd": "P:/av-kit", "scope": "Row C5 hub, shared by MEU-119, MEU-120 and MEU-121: F1's and F2's issues resolved, CONSOLE-HOME-SCRUB-SHORT-FORM (D-337) and TRACKED-FILES-HOLD-HOME-PATH (D-344) filed, MEU-127 svc-tts-fp16-phase-guard registered (D-336, D-345: meu-status.yaml, the P2 band, matrix row 3.18, 03's residual section and the FP16 issue's meu_links), and the MEU-120 and MEU-121 notes", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12 and C1 to C5", "output": "decision logs read: 67 of 67; register sha256 before=809d53e4f9189ce5bb7b22e8c2ed1887e337e9f5b68c7d54d5747a746b4763e7, after=05152c73e598cfb2ee00c75e508e03a99ccd8a66febab97a901db812eeb1c788; parsed fields changed: 8 (issues[112] and issues[113] resolution_path, status, verification.method and verification.result); issue-resolve: 0 problem(s). Drift check passed: SSOT loaded (127 MEUs, 12 phases), rendered regions match on-disk content. OK: known-issues.md is up-to-date. ['resolved', 'resolved', 'open', 'open', 'open'] ['MEU-62', 'MEU-72', 'MEU-121', 'MEU-127'] MEU-127 registered: True."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-c5-register-fix", "command": "python -I -X utf8 s52_c5_fix_online.py (a one-off script outside the checkout, run from P:/av-kit), then python -I -X utf8 tools/issue_triage.py render --check and python -I -X utf8 tools/meu_status.py render --check", "cwd": "P:/av-kit", "scope": "Row C5 correction, after the first attempt of gate run 2: SMOKE-TTS-WAV-HEADER-TRUSTED's resolution_path said that the online and offline phases refuse 8,000 or fewer samples. phase_online generates nothing (smoke_packaged_tts.py:223), so the text now names the offline phase only. The script refuses any other change to the parsed register and saves a copy through model.save to prove the bytes", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12 and C1 to C6's first attempt", "output": "SMOKE-TTS-WAV-HEADER-TRUSTED resolution_path corrected; parsed issues otherwise equal; model.save round trip identical: True. known-issues.yaml: crlf=0 lf_only=4176, sha256 0bcd5af73a865097f2353d1f9ad9bb51c503c6924f94629c6f6f8e0ed34285fa. OK: known-issues.md is up-to-date. Drift check passed: SSOT loaded (127 MEUs, 12 phases), rendered regions match on-disk content."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-gate-c6", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-06-tts-load-fp16/session-gate.ps1 *> C:/Temp/av-kit/s52-gate-h1-r2.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s52-gate-h1-r2.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "Row C6, gate run 2 (D-341): the registered D6 gate on the whole tree after rows C1 to C5 and the register correction, with the new tooling test, the matrix and the files of Mat's instruction change added to its allowed set: identity, every static check, both full suites, the UI build, OpenAPI, the MCP types, tests and build, both renders, the targeted Electron specs, the package build, the sentence smoke on INT8 under row C4's payload check on a fresh copy of the onedir outside the checkout, the strict dev PyTorch check and the models snapshot, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (41 rows, 39 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 58, outside scope: [], head moved: False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1296 passed); ui-tests exit=0 (112 files, 1174 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-tests exit=0 (35 files, 470 passed); mcp-build exit=0; state-render exit=0 (127 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ui-electron exit=0 (46 passed); package-build exit=0; smoke-sentences exit=0 (PASS: smoke_packaged_tts sentences, kokoro-onnx-int8, 149 jobs all Done, the shortest WAV 55,200 samples); dev-pytorch exit=0 (PASS: dev-pytorch-check strict); models-untouched exit=0 (159 files, 0 changes); identity-after exit=0 (tested_state before = after); mcp-audit, build-record and smoke-capability skipped; baseline failures excused: py [], ui [], mcp []; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/drift-check.txt 2>&1 (H1-3's cell, run from Git Bash, so its *> became > 2>&1)", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here; row 12 set the three MEUs ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055", "output": "Drift check passed: SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-h1-4-openapi", "command": "rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json > C:/Temp/av-kit/openapi-check.txt 2>&1 (H1-4's cell, run from Git Bash, so its *> became > 2>&1)", "cwd": "P:/av-kit", "scope": "H1-4: packages/api doesn't change in this session; the OpenAPI check runs as a guard, and any drift would be S6", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055", "output": "exit 0; check_openapi prints nothing when openapi.committed.json matches the live schema"}
```

### Quality Gate Results

`s52-gate-c6` (row C6, gate run 2) is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors, 0 warnings; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 41 rows (39 fully checked, 2 `view_file` exempt; rows C1 to C10 are the 10 more); scope-paths found 58 changed paths, none outside scope, and HEAD b6c3895 did not move (D-341 added the tooling test, the matrix and the files of Mat's instruction change to the allowed set); the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** pytest 1296 passed (baseline 1274: AC-119.1 to AC-119.9 and AC-119.10's 10 cases are 19 of the 22 new, and row C3's three AC-121.8 tooling tests are the rest); Vitest 1174 passed in 112 files (baseline 1163); MCP tests 470 passed in 35 files (baseline 470). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render and the issue render match the files on disk.
- **Runtime:** the targeted Electron specs passed (46 of 46: `settings` 23, `tts-generate` 23). `package-build` built the onedir, and `smoke-sentences` passed 149 of 149 jobs on `kokoro-onnx-int8` on a fresh copy of it outside the checkout. `dev-pytorch` passed strict, and the real models folder was unchanged (159 files).
- **Skipped:** `mcp-audit` (live network and YouTube, which the brief forbids), `build-record` (no installer build) and `smoke-capability` (the plan's §Out of Scope: MEU-125's rc.2 gate repeats it).
- **Identity:** the tested_state was the same before and after the gate: `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e`. Row C7's `identity.py --state-only` re-derives the same value with `ELECTRON_RUN_AS_NODE` unset.
- **Earlier runs.** Run 1 (H1-2) passed every step on `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055`, the tree review round 1 read; its receipts are in `C:/Temp/av-kit/s52-gate-r1/`. Run 2's first attempt passed every step on `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+d61c5dfa0f9a1b426fc858d186b39268984f2d14ebba2e9217e60d997ad5485b` (receipts in `C:/Temp/av-kit/s52-gate-r2a/`). Then `s52-c5-register-fix` corrected one sentence in the register, which the identity binds, so the gate ran again and `s52-gate-c6` is that run. `durable_evidence.py --require-full` binds every passing full record to the tree, so neither earlier run is kept as a record.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | `load_model`: the four checks before the unload, the runtime check through `runtime_present`, the raising-probe log with the class only; docstring |
| `packages/core/src/avkit_core/services/health.py` | modified | `HOME_IGNORES_CASE`, `home_folder`, `scrub_home`; `console_field` scrubs first |
| `tests/integration/test_tts_device_resolution.py` | modified | AC-119.1 to AC-119.8; AC-75.9 amended; `_adapter`'s `runtime_probe` and the two A′ setups |
| `tests/e2e/test_api_model_load_keeps.py` | new | AC-119.9 |
| `tests/unit/test_services.py` | modified | AC-119.10, appended at the end. CRLF kept |
| `docs/build-plan/03-service-layer.md` | modified | The MEU-119 Delivered note (`:627-635`). CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md` | modified | MEU-119 to MEU-121 `ready_for_review` (row 12), shared |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | Two issues resolved and the FP16 issue's verification through `issue-resolve.py` (row 12), shared |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modified | Row 52 `executed` with the plan folder. CRLF kept |
| `.agent/context/current-focus.md` | modified | Session 52 entry on top (H1-3). CRLF kept |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `identity.py`, `red-check.py`, `models-snapshot.py`, `models-before.json`, `issue-resolve.py`, `session-gate.ps1`, `closeout-decisions.md`, `task.md` | new or modified | The plan's scripts and records, shared with MEU-120 and MEU-121 |

```diff
     def load_model(self, variant: ModelVariant, device: DeviceType) -> None:
-        self.unload_model()
         try:
             path = _require_weight_path(variant)
         ...
             raise ModelLoadError("TTS device probe failed") from exc
         ...
+        try:
+            present = self.runtime_present(variant.format)
+        except Exception as exc:
+            # The probe's text can hold a local path, so only its class is logged (D-323).
+            log.error(
+                "tts.load_failed",
+                variant_id=variant.id,
+                device=target,
+                error=type(exc).__name__,
+            )
+            raise ModelLoadError("TTS runtime probe failed") from exc
+        if not present:
+            absent = ModelLoadError(MODEL_REASONS[variant.format])
+            _log_load_failed(variant, target, absent)
+            raise absent
+        self.unload_model()
```

The excerpt is abridged. `tts/adapter.py:286-332` and `services/health.py:96-126` are the source.

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

Round 1 of loop `s52-execution-2026-11-06-tts-load-fp16` returned `approved`, intent achieved `yes`, with two Medium findings, both non-blocking ([implementation-critical-review.md](2026-11-06-tts-load-fp16-implementation-critical-review.md)). F1 is MEU-120's and F2 is MEU-121's. D-339 files both as known issues, and D-340 asks Mat whether to fix them before the commit ([closeout-decisions.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md)). The round used 14,996,767 of the loop's 21,000,000 tokens, so the ledger refuses a round 2 until Mat continues the loop (`C:/Temp/av-kit/s52-exec-ledger-state-r1.txt`). The report was validated under `C:/Temp/av-kit` and copied byte for byte; H1-7a and H1-7b passed on the canonical copy (`C:/Temp/av-kit/review-state-check.txt`, `exec-review.txt`).

Mat ruled D-340 with "all recommendations accepted", "proceed with changes", "commit and push" (2026-11-07): fix both now. The recommended continue of 10,000,000 tokens was recorded at 2026-11-07T16:34:19Z (`C:/Temp/av-kit/s52-exec-ledger-continue-1.txt`), so the loop's budget is 31,000,000. Rows C1 to C4 fix F1 and F2, C5 resolves both issues, C6 reran the gate, and round 2 (row C8) rechecked F1 and F2. Round 2 returned `approved`, intent achieved `yes`, with F1 and F2 `fixed` in its Prior Pass Summary and no new finding, using 4,694,911 tokens (19,691,678 of 31,000,000 in all). Row C9's `--approved-state-only` check passed: approved at round 2 of 6, 0 open blocking findings.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The 8.3 short form of the home folder is not scrubbed | dependency | A later plan (`CONSOLE-HOME-SCRUB-SHORT-FORM`) | Mat's D-337 ruling: `scrub_home` also matches the short form, in a row of its own with a Red, in a later plan; the next triage places the issue. The brief is in [closeout-decisions.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md) |
| Tracked files that name the home folder in full | dependency | The next triage (`TRACKED-FILES-HOLD-HOME-PATH`) | Mat's D-344 ruling: Session 52's files are committed as they are |
| FP16's guarded phase computation | dependency | MEU-127 | Mat's D-336 ruling; D-239 item 3; [closeout-decisions.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md); owned by the MEU-121 handoff |
| The rc.2 repeat of Session 51's capability smoke | dependency | MEU-125 | The plan's §Out of Scope (`implementation-plan.md:426`): MEU-125's rc.2 gate repeats it |
| Pre-existing pyright error in `tools/smoke_packaged_tts.py:734` (`__doc__.splitlines`, reportOptionalMemberAccess) | out-of-scope | — | It is at `HEAD` too (`:611` there), and `tools/` is outside the pyright include; `py-types` runs `pyright packages/`, which passes |
| Commit and push | out-of-scope | — | Authorized by Mat's "commit and push" (2026-11-07); it follows round 2's approval and the closeout addenda (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files written from the task cells, because the cells' `*>` needs PowerShell.
- **Row 2a, before the Red run.** The first draft imported `scrub_home` from `services.health`, which fails at import (`ImportError: cannot import name 'scrub_home'`), a setup failure `red-check.py` refuses. `_scrub_ready` (`test_services.py:3297`) now asserts each name on the module first, then patches it, so the Red fails by assertion.
- **Row 2a, stdout.** Stdout carries each Console line as JSON, so its backslashes are doubled there. The surface test checks the raw stdout for the user name, and the decoded `message` of each JSON line for the `~` path (`:3398-3415`). This was settled before the Red run; no expectation changed in Green.
- **Row 1's receipt.** Its captured log line shows pytest's temp root, a `pytest-of-<user>` folder under row 1's `TMP`. That is pytest's naming under `TMP`, not an app path, and it reaches no Console field.
- **8.3 form.** `scrub_home` matches the long form `Path.home()` gives. A short form such as `C:\Users\FIRSTN~1` shows the first six letters of the user name and isn't matched. The plan raised it, 03 `:633` records it, and Mat ruled the fix into a later plan (D-337, `CONSOLE-HOME-SCRUB-SHORT-FORM`). It is not a residual: this PC's user folder has no short form, and the app writes long paths.
- **H1-3 and H1-4.** They ran from Git Bash, so each cell's `*>` became `> 2>&1`, with `ELECTRON_RUN_AS_NODE` unset. The gate passed on run 1, and again on run 2 (row C6, D-341) after the review's fixes.

---

## Decision Log

```yaml
decision_log:
  - id: D-341
    stage: execution
    question: "Gate run 2 sees files that session-gate.ps1's allowed set refuses: the new tooling test, the matrix and the files of Mat's instruction change. Which tree does it test?"
    resolution: autonomous
    class: two-way
    chosen: "Add those files to the allowed set (task row C6), so the gate tests the tree both commits hold; ui/tests/e2e/test-ids.ts stays refused"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-06-tts-load-fp16/session-gate.ps1 — the allowed set refuses any changed path outside it (scope-paths)", "docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md D-340 — Mat's ruling asks for a fresh gate (C6)"]
    research: { engine: none, sources: [] }
    reasoning: "The instruction change is committed after this session's work and touches no code, but a gate that refused its files would fail on the tree the commits hold, and one that dropped them would test a tree that never exists. Widening the set by name keeps scope-paths refusing everything else, test-ids.ts included."
  - id: D-344
    stage: closeout
    question: "Session 52's new and changed files name the home folder in full in a few lines, as 56 tracked files already do. Are they rewritten before the commit?"
    resolution: human
    class: two-way
    chosen: "Commit Session 52's files as they are and file TRACKED-FILES-HOLD-HOME-PATH for the next triage"
    source_tag: Human-approved
    precedents: ["known-issues.yaml TRACKED-FILES-HOLD-HOME-PATH — 56 files and 119 lines measured with git grep", "D-335 — the Console scrub covers runtime output, not tracked files"]
    research: { engine: none, sources: [] }
    reasoning: "The repository is public and its old history keeps every earlier instance, so a rewrite in this session limits new exposure only, and it would change a plan review kept byte for byte. One issue for all 56 files lets a later plan fix them together with a check that keeps them out."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'all recommendations accepted'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Initial MEU-119 handoff after H1-2 |
| Reviewed | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 1 `approved` from the canonical report |
| Amended | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Rows C5 to C7 on Mat's rulings: D-337 and D-344 recorded, D-341 and D-344 in the Decision Log, and gate run 2's `s52-gate-c6` in place of run 1's record |
| Rechecked | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 2 `approved` from the canonical report: F1 and F2 `fixed`, no new finding (row C8) |
