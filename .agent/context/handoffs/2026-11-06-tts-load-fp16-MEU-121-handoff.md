---
date: "2026-11-07"
project: "tts-load-fp16"
meu: "MEU-121"
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

# Handoff: 2026-11-06-tts-load-fp16-MEU-121-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-121 `svc-tts-fp16-nonfinite` (`TTS-ONNX-FP16-NONFINITE-AUDIO`, triage D-239). A fresh install now preselects ONNX INT8, which passed every job of a packaged sentence smoke. ONNX FP16 failed 12 of the same 149 jobs and stays offered. A 2-hour-boxed spike found where FP16 first goes non-finite but no setting that stops it, so the issue stays open and its outcome goes to Mat (D-336).
**Build Plan Section**: [03 §ONNX FP16 non-finite audio (residual)](../../../docs/build-plan/03-service-layer.md), Delivered note at `:653`.
**Predecessor**: none. The [MEU-119 handoff](2026-11-06-tts-load-fp16-MEU-119-handoff.md) and the [MEU-120 handoff](2026-11-06-tts-load-fp16-MEU-120-handoff.md) are the same plan's other MEUs.

- **Listening verdict (D-331).** Mat heard the INT8 sample and ruled "D-331 INT8" on 2026-11-07, after the brief in [human-gate-decision.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/human-gate-decision.md) recommended INT8 over FP32 (log-mel distance from PyTorch FP32 0.36 against FP32's 0.14, 92.4 MB against 325.5 MB, no fault tones on ARM). So the INT8 ids in AC-121.1 to AC-121.6 stand, row 9 copied no `model.onnx`, and row 10 ran on `kokoro-onnx-int8` (`task.md:34`).
- **Preselection (rows 6, 7, 8; D-329, D-330, `PRESELECT_ORDER`).**
  - `tts-controls.ts` exports `PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32'] as const` (`:108`).
  - `defaultModelSelection` (`:118`) keeps its first two rules: the chosen row while runnable, then the loaded row. For the first-downloaded and first-row fallbacks it ranks the runnable rows by `PRESELECT_ORDER`, with every other row after them in catalog order (a stable sort, `:132-139`).
  - MEU-117's skip of unavailable rows (D-320) is unchanged.
  - FP16 is still offered, and it is picked when it is the only downloaded row (D-330).
  - AC-121.1 builds the fresh-install catalog from `engine.py`'s `SEED_VARIANTS`, read as text and sorted by id as `list_catalog` returns it, so the test follows the seed (D-329).
- **Sentence smoke (rows 9, 10; D-332, `SENTENCE_SMOKE`).**
  - `tools/smoke_packaged_tts.py` gains `--phase sentences` (`phase_sentences`, `:646-730`) with `--test-set` and `--variant` (`:743-744`, required together at `:755`). The module docstring says what it does (`:21-28`).
  - `_register_variant` (`:312`) and `_generate` (`:322`) take the variant id as a keyword argument, defaulting to today's value, so `phase_offline` doesn't change.
  - The phase refuses a backend or models folder inside the checkout, and a models folder equal to `~/.avkit/models`. It starts the copied backend behind dead proxies with fresh app data, registers the variant through the download fast path, loads it on `cpu` once, and runs the test set's 149 jobs one at a time with `enabled_steps: []`.
  - The 149 jobs are each of the 40 sentences with `af_heart`, `am_michael` and `af_bella`, the first 20 with `bf_emma`, the 8 paragraphs with `af_heart` and the 96-word passage with `af_heart`.
  - It passes only when every job ends `Done` with more than 0 samples in a WAV inside its run folder.
- **FP16 spike (row 11; D-333, `FP16_SPIKE`).** `fp16-spike.py all --e5` (plan folder) phonemized the 40 sentences once, then ran ORT directly on the FP16 copy over the rate probe's 140 (sentence, voice) pairs: E0 to E4, then E5 (Mat's "E5 yes"). Its results are under AC-121.9 and in the Evidence section.
- **Spec text.** 03 gained the MEU-121 Delivered note (`:653-659`, row 12).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md) §MEU-121. **Execution authorization:** `USER_EXPLICIT`, 2026-11-07, "D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed", given after the Codex plan review approved in round 4 ([plan-critical-review.md](2026-11-06-tts-load-fp16-plan-critical-review.md)); recorded in [human-gate-decision.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/human-gate-decision.md) (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

Vitest and Playwright titles begin `AC-121.<n>`. The ids are for the INT8 verdict (D-331).

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-121.1 | unit | The fresh catalog from `engine.py`'s `SEED_VARIANTS`, sorted by id, nothing downloaded or loaded, PyTorch unavailable: the selection is `kokoro-onnx-int8` | Human-approved: triage D-239 | `ui/tests/unit/tts-model-selection.test.ts:95` | ✅ |
| AC-121.2 | unit | `PRESELECT_ORDER` exists, is `['kokoro-onnx-int8', 'kokoro-onnx-fp32']`, and each id is a seeded variant | Human-approved: D-239; Local Canon: D-330 | `tts-model-selection.test.ts:101` | ✅ |
| AC-121.3 | unit | Several rows downloaded: FP16 and FP32 give FP32; every ONNX row gives INT8; only FP16 gives FP16 | Local Canon: D-330 | `tts-model-selection.test.ts:108` | ✅ |
| AC-121.4 | unit | INT8 served unavailable and nothing downloaded: FP32 | Local Canon: D-320, D-330 | `tts-model-selection.test.ts:117` | ✅ |
| AC-121.5 | unit | The chosen and loaded rules and MEU-117's skip are unchanged: the six AC-117.13 tests pass unchanged (guard) | Local Canon: D-320 | `tts-model-selection.test.ts:19-54` | ✅ |
| AC-121.6 | E2E | On the built app with nothing downloaded or loaded, the TTS page's model select shows `kokoro-onnx-int8` | Human-approved: D-239 | `ui/tests/e2e/tts-generate.test.ts:923` (row 8; gate `ui-electron`) | ✅ |
| AC-121.7 | packaged | `SENTENCE_SMOKE` on FP16 exits 1, with at least one "generated audio must be finite" failure and no other kind of failure | Human-approved: D-239 ("fixed test set") | Row 9: `tools/smoke_packaged_tts.py --phase sentences --variant kokoro-onnx-fp16` | ✅ |
| AC-121.8 | packaged | `SENTENCE_SMOKE` on `PRESELECT_ORDER[0]` passes all 149 jobs on a fresh onedir | Human-approved: D-239 ("Done") | Row 10 (`--variant kokoro-onnx-int8`); gate `smoke-sentences` | ✅ |
| AC-121.9 | record | The spike's experiments and results, and the cause or Mat's outcome, are in this handoff and the issue's `verification` | Human-approved: D-239 | Row 11's `s52-spike-summary.json` and the E0 to E5 records; row 12 wrote issues[110]'s `verification`; the outcome is D-336 | ✅ |
| AC-117 (cross-ref) | regression | AC-117.13 (the unit tests above) and AC-117.14 (the E2E whose catalog has INT8 not downloaded and FP32 downloaded, so it still expects FP32) pass unchanged; AC-117.8 is in the [MEU-119 handoff](2026-11-06-tts-load-fp16-MEU-119-handoff.md) | plan §Preselection | `tts-model-selection.test.ts:19-54`, `ui/tests/e2e/tts-generate.test.ts:891` (rows 7, 8; gates `ui-tests`, `ui-electron`) | ✅ |
| AC-63 (cross-ref) | regression | The TTS page's AC-63.x tests pass unchanged under the new fallback | plan §Preselection (`implementation-plan.md:197`) | `ui/tests/unit/tts-page.behavior.test.ts` (row 7; gate `ui-tests`) | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged, so the byte-hash tests AC-51.6 and AC-81.13 pass | plan §Files Modified | `ui/tests/unit/layout-primitives.test.ts:200`, `ui/tests/unit/capture-action-row.test.ts:710` (gate `ui-tests`) | ✅ |
| AC-100 (cross-ref) | — | Named in the plan only as `red-check.py`'s boundary example (`AC-100.7` never matches `AC-100.70`); no AC-100 test changes | plan §Verification Plan | gate `ui-tests` | ✅ |
| AC-75, AC-115, AC-119 (cross-ref) | — | Owned by the MEU-119 handoff (the load order, the amended AC-75.9, the home-folder scrub and the AC-115 regressions) | plan §MEU-119 | [MEU-119 handoff](2026-11-06-tts-load-fp16-MEU-119-handoff.md) | see MEU-119 |
| AC-58, AC-120 (cross-ref) | — | Owned by the MEU-120 handoff (the models-folder default and probe; the Settings E2E as AC-58.12) | plan §MEU-120 | [MEU-120 handoff](2026-11-06-tts-load-fp16-MEU-120-handoff.md) | see MEU-120 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-121.1 | Row 6: `expected 'kokoro-onnx-fp16' to be 'kokoro-onnx-int8'`: today the fallback takes the first row in id order | Row 7: pass | `tts-model-selection.test.ts:95` |
| AC-121.2 | Row 6: `expected {…} to have property "PRESELECT_ORDER"`: the test first asserts the new export exists | Row 7: pass | `:101` |
| AC-121.3 | Row 6: `expected ['kokoro-onnx-fp16', …] to deeply equal ['kokoro-onnx-fp32', …]`; its "only FP16" case is the guard part, as planned | Row 7: pass | `:108` |
| AC-121.4 | Row 6: `expected 'kokoro-onnx-fp16' to be 'kokoro-onnx-fp32'` | Row 7: pass | `:117` |
| AC-121.5 | Guard: the six AC-117.13 tests pass in Red by design | Row 7: pass | `:19-54` |
| AC-121.6 | No Red of its own; its negative is AC-121.1 | Row 8: pass on the built app | `tts-generate.test.ts:923` |
| AC-121.7 → AC-121.8 | Row 9: FP16, exit 1, 12 of 149 jobs `Failed` with "generated audio must be finite" and 0 samples, no other kind of failure | Row 10: INT8, 149 of 149 `Done`, 0 failures; the gate's `smoke-sentences` repeats it | `tools/smoke_packaged_tts.py:646` |

- **Row 6 Red:** `Tests 4 failed | 6 passed (10)` in `tts-model-selection.test.ts`. The 6 passes are the AC-117.13 tests (AC-121.5). `red-check.py` required AC-121.1 to AC-121.4 and found 0 problems. Each failure is the decisive assertion, never a collection or import error.
- **Row 7 Green:** the whole Vitest suite, `Test Files 112 passed (112)` and `Tests 1172 passed (1172)` in 34.81s, with the typecheck and ESLint (`--max-warnings 0`).
- **Row 8:** the UI build passed, and the `tts-generate` E2E passed 23 of 23 (34.0s) on the built app, AC-121.6 and AC-117.14 among them. The models snapshot found 159 files and 0 changes.
- **Row 9 Red (AC-121.7).** PyInstaller built the onedir ("Build complete!"), copied to a fresh folder outside the checkout. The FP16 run took 14:09:45 to 14:12:30 UTC and exited 1 with "FAIL: smoke_packaged_tts sentences".
  - The 12 failures are each `{"status": "Failed", "error_message": "generated audio must be finite", "wav_samples": 0}`: `af_heart` sentences 0, 14, 22 and 23; `am_michael` 0 and 37; `af_bella` 24 and 33; `bf_emma` 9, 12 and 18; and the passage.
  - Those are the rate probe's 11 failing sentences (`known-issues.yaml:4010`, 4/40, 2/40, 2/40 and 3/20) and the passage it saw fail 3 of 3. The 8 paragraphs passed.
  - `errors` and `forbidden_dirs` were empty, and the register step returned `{"result": "downloaded", "state": "Idle", "error": null}`, so nothing was fetched.
- **Row 10 Green (AC-121.8).** INT8 on the same onedir, 14:16:06 to 14:18:53 UTC: `passed` true, 149 jobs, 0 failures, 0 errors, 0 forbidden folders, and the vocab, spaCy and voice-pack assets all `ready`. The models snapshot found 0 changes after rows 9, 10 and 11.
- **Row 11, the spike (AC-121.9).** It ran 14:22:28 to 14:37:03 UTC, about 15 minutes of the 7,200-second box (S13 not reached). Stop reason `done`, candidate none, no S5 event.

| Experiment | What ran | Failing pairs of 140 | Reading |
|---|---|---|---|
| E0 | Default session, ORT 1.31.1 (control) | 11 | The rate probe's 11 pairs reproduce on the copy (`e0_reproduces_rate_probe` true) |
| E1 | `ORT_DISABLE_ALL`, `ORT_ENABLE_BASIC`, `ORT_ENABLE_EXTENDED` | 15, 16, 16 | No level makes every pair finite, so no single graph rewrite is the cause |
| E2 | ORT 1.24.4 and 1.29.0 | not run | `uv run --offline --no-sync --with onnxruntime==<v>` found neither offline ("No solution found when resolving `--with` dependencies … the network was disabled") |
| E3 | For each failing pair: style row ±1 and ±2, speed 0.9 and 1.1, the trailing punctuation token | 7 of 77 nudges still fail | Each base pair was wholly non-finite, and most small changes passed, so the trigger is input-specific, not one token or one style row. Still failing: `af_heart#22` style −2; `af_heart#23` style −2, speed 0.9 and 1.1; `am_michael#37` style +2; `af_bella#33` speed 0.9; `bf_emma#12` speed 0.9 |
| E4 | `intra_op_num_threads=1`; `enable_cpu_mem_arena=False` | 16; 11 | Threading changes which pairs fail; the arena doesn't matter |
| E5 | Every node's output added as a graph output (`onnx` 1.23.2), at `ORT_DISABLE_ALL`, on the 11 failing pairs | 11 reproduced | 2,490 nodes, 2,502 outputs, 2,098 scanned. In all 11 pairs the first non-finite output in graph order is `/decoder/decoder/generator/Div`. Its inputs `Gather_5_output_0` (largest absolute value about 0.62) and `Gather_4_output_0` (about 1.35) are FP16 `[1, 11, N]` and hold no NaN or Inf |

- **E5's fetch.** The install ran once with `--no-config --no-deps --require-hashes --only-binary :all:` into a Temp target, and exited 0 with `+ ml-dtypes==0.6.0` and `+ onnx==1.23.2`.
  - The target held exactly those two distributions.
  - The uv cache gained only `onnx` and `ml-dtypes` entries (under `simple-v24` and `wheels-v6`) and lost none.
  - The project venv's `uv pip list` and the SHA-256s of `pyproject.toml` and `uv.lock` were the same before and after. So no S5.
- **What the spike means.** Two outside reports name the same node, found by D-336's research.
  - HF onnx-community Kokoro discussion 22 identifies `Div → Atan → Greater/Less → Where` as the exported `atan2` on the harmonic source's STFT.
  - sherpa-onnx issue 4086 reports that `Div` as `0/0` in bins 0 and 10 at low precision.
  - A `0/0` fits E5's two finite inputs and non-finite output. It is still a hypothesis: this session did not count the zeros in `Gather_4`, and E5 records the node, not whether its output is NaN or Inf. D-336 recommends a follow-up MEU that tests a guarded phase computation, with this smoke as its Red and Green.

Receipts: `C:/Temp/av-kit/s52-preselect-red.txt` (with `.exit`), `s52-preselect-red-check.txt`, `s52-preselect-green.txt`, `s52-preselect-types.txt`, `s52-preselect-lint.txt`, `s52-r8-build.txt`, `s52-r8-e2e.txt`, `s52-r8-models.txt`, `s52-r9-build.txt`, `s52-smoke-red.txt` (with `.exit`), `s52-smoke-red.json`, `s52-r9-models.txt`, `s52-smoke-green.txt`, `s52-smoke-green.json`, `s52-r10-models.txt`, `s52-spike.txt`, `s52-spike-summary.json`, `s52-spike-phonemes.json`, `s52-spike-e0.json` to `s52-spike-e5-run.json`, `s52-r11-models.txt`, `s52-resolve.txt`, `s52-r12-*.txt`, run 1's `s52-gate-r1/`, gate run 2's `s52-gate-h1-r2.txt` and `s52-D6-<id>.txt`, and `drift-check.txt` and `openapi-check.txt`. The HDP research receipts for D-336 are `s52-hdp-research-d336a.txt`, `-d336b.txt` and `-d336c.md`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s52-121-preselect-red", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test -- tests/unit/tts-model-selection.test.ts *> C:/Temp/av-kit/s52-preselect-red.txt; then red-check.py --require AC-121.1 --require AC-121.2 --require AC-121.3 --require AC-121.4 C:/Temp/av-kit/s52-preselect-red.txt *> C:/Temp/av-kit/s52-preselect-red-check.txt (abridged from task.md row 6's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-121 Red, preselection: AC-121.1 to AC-121.5 against the unchanged tts-controls.ts, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 (baseline.sha) plus rows 1 to 6", "output": "Tests 4 failed | 6 passed (10). Decisive: expected 'kokoro-onnx-fp16' to be 'kokoro-onnx-int8' for AC-121.1; expected {...} to have property \"PRESELECT_ORDER\" for AC-121.2; expected ['kokoro-onnx-fp16', ...] to deeply equal ['kokoro-onnx-fp32', ...] for AC-121.3; expected 'kokoro-onnx-fp16' to be 'kokoro-onnx-fp32' for AC-121.4. The six AC-117.13 tests passed (AC-121.5, guard). red-check: 1 receipt(s), 4 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-121-preselect-green", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test *> C:/Temp/av-kit/s52-preselect-green.txt; then rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/s52-preselect-types.txt and rtk proxy npm --prefix ui run lint *> C:/Temp/av-kit/s52-preselect-lint.txt (abridged from task.md row 7's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-121 Green, preselection: the whole Vitest suite, with AC-117.13 and the TTS page's AC-63.x tests unchanged, and the UI typecheck and ESLint", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 7", "output": "Test Files 112 passed (112); Tests 1172 passed (1172) in 34.81s. tsc --noEmit exit 0. eslint src/ tests/ --max-warnings 0 exit 0."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-121-e2e", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s52-r8-build.txt; then rtk proxy npm --prefix ui run test:e2e -- tests/e2e/tts-generate.test.ts *> C:/Temp/av-kit/s52-r8-e2e.txt; then models-snapshot.py --compare models-before.json *> C:/Temp/av-kit/s52-r8-models.txt (abridged from task.md row 8's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-121 Electron check: AC-121.6 and AC-117.14 on the built app, then the real models folder against row 0's snapshot", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 8", "output": "vite build passed. Playwright: 23 passed (34.0s), AC-121.6 and AC-117.14 among them. models-snapshot: 159 file(s) recorded, 0 change(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-121-smoke-red", "command": "$env:ELECTRON_RUN_AS_NODE=$null; copy C:/Temp/av-kit/s32-smoke-models to C:/Temp/av-kit/s52/smoke-models and add model_fp16.onnx from (Join-Path $HOME '.avkit/models/kokoro-v1.0-onnx/onnx'); rtk proxy uv run python tools/package_backend.py *> C:/Temp/av-kit/s52-r9-build.txt; copy packaging/dist/avkit-backend to C:/Temp/av-kit/s52/backend/avkit-backend; rtk proxy uv run python tools/smoke_packaged_tts.py --phase sentences --test-set docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json --variant kokoro-onnx-fp16 --backend-dir C:/Temp/av-kit/s52/backend/avkit-backend --models-dir C:/Temp/av-kit/s52/smoke-models --out C:/Temp/av-kit/s52-smoke-red.json *> C:/Temp/av-kit/s52-smoke-red.txt; require exit 1, variant_id kokoro-onnx-fp16, at least one failure and none other than 'generated audio must be finite'; then models-snapshot.py --compare *> C:/Temp/av-kit/s52-r9-models.txt (abridged from task.md row 9's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-121 Red of the sentence smoke (AC-121.7): a fresh onedir outside the checkout, FP16 on cpu over the 149-job test set, behind dead proxies with fresh app data", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 9", "output": "package_backend: Build complete! smoke exit 1: FAIL: smoke_packaged_tts sentences; variant_id kokoro-onnx-fp16; jobs 149; 12 failures, each status Failed, error_message 'generated audio must be finite', wav_samples 0: af_heart sentences 0, 14, 22, 23; am_michael 0, 37; af_bella 24, 33; bf_emma 9, 12, 18; passage 0. errors []; forbidden_dirs []; register {'result': 'downloaded', 'state': 'Idle', 'error': None}. models-snapshot: 159 file(s) recorded, 0 change(s). The row exits 0 because the Red conditions hold."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-121-smoke-green", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy uv run python tools/smoke_packaged_tts.py --phase sentences --test-set docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json --variant kokoro-onnx-int8 --backend-dir C:/Temp/av-kit/s52/backend/avkit-backend --models-dir C:/Temp/av-kit/s52/smoke-models --out C:/Temp/av-kit/s52-smoke-green.json *> C:/Temp/av-kit/s52-smoke-green.txt; require passed, variant_id kokoro-onnx-int8, jobs 149 and no failures; then models-snapshot.py --compare *> C:/Temp/av-kit/s52-r10-models.txt (abridged from task.md row 10's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-121 Green of the sentence smoke (AC-121.8): PRESELECT_ORDER[0] on the same fresh onedir and the same 149 jobs", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 10", "output": "PASS: smoke_packaged_tts sentences; variant_id kokoro-onnx-int8; jobs 149; failures 0; errors 0; forbidden_dirs 0; asset_states vocab, spacy and voice_packs ready. models-snapshot: 159 file(s) recorded, 0 change(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-121-spike", "command": "$env:TMP='C:\\Temp\\av-kit\\s52\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run python docs/execution/plans/2026-11-06-tts-load-fp16/fp16-spike.py all --e5 *> C:/Temp/av-kit/s52-spike.txt; require a stop reason of cause, done, box or control in C:/Temp/av-kit/s52-spike-summary.json; then models-snapshot.py --compare *> C:/Temp/av-kit/s52-r11-models.txt (abridged from task.md row 11's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-121 FP16 spike (AC-121.9, D-333 with Mat's E5 yes): E0 to E4 offline on the FP16 copy over the 140 sentence pairs, then E5's bounded hashed install and its node scan", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 11", "output": "spike stop: done; candidate none; s5 []; box 7200 s, run 14:22:28 to 14:37:03 UTC. E0 11 failing pairs (reproduces the rate probe); E1 ORT_DISABLE_ALL 15, ORT_ENABLE_BASIC 16, ORT_ENABLE_EXTENDED 16; E2 1.24.4 and 1.29.0 not_run (offline uv could not resolve them); E3 70 of 77 nudges finite, 7 still failing; E4 threads-1 16, no-arena 11; E5 install exit 0 (+ ml-dtypes==0.6.0, + onnx==1.23.2), target dists exactly the two, uv cache new entries only onnx and ml-dtypes, venv pip list, pyproject.toml and uv.lock unchanged; E5 run ORT_DISABLE_ALL, 2490 nodes, 2502 outputs, 2098 scanned, reproduced, first non-finite output in all 11 pairs /decoder/decoder/generator/Div with finite inputs Gather_5 and Gather_4. models-snapshot: 159 file(s) recorded, 0 change(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-row12-hub", "command": "task.md row 12 (abridged), run from P:/av-kit: its task text runs rtk proxy uv run python docs/execution/plans/2026-11-06-tts-load-fp16/issue-resolve.py --issue TTS-FAILED-LOAD-DROPS-MODEL --issue MODELS-DIR-DOCS-AND-PROBE-MISMATCH --issue TTS-ONNX-FP16-NONFINITE-AUDIO --set-file C:/Temp/av-kit/s52-resolve.json --expect-sha256 $sha *> C:/Temp/av-kit/s52-resolve.txt, then issue_triage.py render and triage; its Validation cell, through an extracted .ps1, checks C:/Temp/av-kit/s52-resolve.txt for '^issue-resolve: 0 problem', then runs rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s52-r12-render.txt, rtk proxy uv run python tools/issue_triage.py render --check *> C:/Temp/av-kit/s52-r12-issues.txt, the three issue statuses and the grouping row *> C:/Temp/av-kit/s52-r12-status.txt", "cwd": "P:/av-kit", "scope": "Row 12 hub, shared by MEU-119, MEU-120 and MEU-121: the 03 and 06 Delivered notes, the three MEUs ready_for_review, two issues resolved and the FP16 issue's verification through issue-resolve.py, and grouping row 52 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12", "output": "decision logs read: 67 of 67; parsed fields changed: 13 (issues[99] and issues[100] status, verification.last_checked, method, result and resolution_path; issues[110] verification.last_checked, method and result); issue-resolve: 0 problem(s). Drift check passed: SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content. OK: known-issues.md is up-to-date. ['resolved', 'resolved', 'open']. grouping tracker names the plan: True."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-121-c3-red", "command": "$env:TMP='C:\\Temp\\av-kit\\s52\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/tooling/test_smoke_packaged_tts.py --tb=short -q *> C:/Temp/av-kit/s52-c3-red.txt; then red-check.py --require test_ac_121_8_header_only_wav_counts_no_samples --require test_ac_121_8_truncated_wav_counts_no_samples C:/Temp/av-kit/s52-c3-red.txt *> C:/Temp/av-kit/s52-c3-red-check.txt (abridged from task.md row C3's Validation cell, run from P:/av-kit through an extracted .ps1)", "cwd": "P:/av-kit", "scope": "Review round 1 F2, Red (D-340, D-343): tests/tooling/test_smoke_packaged_tts.py against the unchanged _generate. A fake backend returns a Done job whose WAV is a 44-byte header declaring 100 frames, a payload cut short, or a complete file (the guard); red-check.py names the two required tests", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12 and C1 to C3", "output": "2 failed, 1 passed in 1.41s, exit 1. Decisive, in the header-only and truncated cases: assert (100, None) == (0, 100), so _generate took the header's 100 frames and had no wav_declared. The complete-file guard passed. red-check: 1 receipt(s), 2 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-121-c4-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s52\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/tooling/test_smoke_packaged_tts.py --tb=short -q *> C:/Temp/av-kit/s52-c4-green.txt; then rtk proxy uv run ruff check tools/smoke_packaged_tts.py tests/tooling/test_smoke_packaged_tts.py *> C:/Temp/av-kit/s52-c4-lint.txt (abridged from task.md row C4's Validation cell, run from P:/av-kit through an extracted .ps1)", "cwd": "P:/av-kit", "scope": "Review round 1 F2, Green (D-343): _generate counts a WAV's frames only when its payload holds every frame the header declares, else 0, and keeps the header's count as wav_declared (tools/smoke_packaged_tts.py:357-365); the sentences phase then refuses 0 samples (:714-716) and the offline phase 8,000 or fewer (:434). The three tooling tests and ruff", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12 and C1 to C4", "output": "3 passed in 57.00s. ruff check: All checks passed!"}
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
- **Suites:** Vitest 1174 passed in 112 files (baseline 1163: AC-120.1, AC-120.3 to AC-120.6, AC-121.1 to AC-121.4 and row C1's two AC-120 fault cases are the 11 new); pytest 1296 passed (baseline 1274; row C3's three AC-121.8 tooling tests are among the 22 new); MCP tests 470 passed in 35 files (baseline 470). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render and the issue render match the files on disk.
- **Runtime:** the targeted Electron specs passed (46 of 46: `settings` 23, `tts-generate` 23). `package-build` rebuilt the onedir, and `smoke-sentences` passed 149 of 149 jobs on `kokoro-onnx-int8` on a fresh copy of it outside the checkout, repeating row 10 on the final tree. Row C4's payload check ran there, so each of the 149 WAVs held every frame its header declares (the shortest, 55,200 samples). `dev-pytorch` passed strict, and the real models folder was unchanged (159 files).
- **Skipped:** `mcp-audit` (live network and YouTube, which the brief forbids), `build-record` (no installer build) and `smoke-capability` (the plan's §Out of Scope: MEU-125's rc.2 gate repeats it).
- **Identity:** the tested_state was the same before and after the gate: `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e`. Row C7's `identity.py --state-only` re-derives the same value with `ELECTRON_RUN_AS_NODE` unset.
- **Earlier runs.** Run 1 (H1-2) passed every step on `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055`, the tree review round 1 read; its receipts are in `C:/Temp/av-kit/s52-gate-r1/`. Run 2's first attempt passed every step on `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+d61c5dfa0f9a1b426fc858d186b39268984f2d14ebba2e9217e60d997ad5485b` (receipts in `C:/Temp/av-kit/s52-gate-r2a/`). Then `s52-c5-register-fix` corrected one sentence in the register, which the identity binds, so the gate ran again and `s52-gate-c6` is that run. `durable_evidence.py --require-full` binds every passing full record to the tree, so neither earlier run is kept as a record.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/tts/tts-controls.ts` | modified | `PRESELECT_ORDER`; `defaultModelSelection`'s fallbacks rank runnable rows by it; docstring. CRLF kept |
| `ui/tests/unit/tts-model-selection.test.ts` | modified | AC-121.1 to AC-121.4 appended, with the `SEED_VARIANTS` reader. The file was LF at session start and stays LF |
| `ui/tests/e2e/tts-generate.test.ts` | modified | AC-121.6 appended. CRLF kept |
| `tools/smoke_packaged_tts.py` | modified | `--phase sentences`, `--test-set`, `--variant`; `_register_variant` and `_generate` take the variant id; docstring paragraph. CRLF kept |
| `docs/build-plan/03-service-layer.md` | modified | The MEU-121 Delivered note (`:653-659`). CRLF kept |
| `docs/execution/plans/2026-11-06-tts-load-fp16/fp16-spike.py`, `fp16-test-set/` | new | The spike and its read-only test set (40 sentences, 8 paragraphs, the passage, the voices) |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, `known-issues.yaml`, `known-issues.md`, `triage-output.yaml`, the grouping, `current-focus.md` | modified | Row 12's hub and register changes and H1-3's focus entry, shared; listed in the [MEU-119 handoff](2026-11-06-tts-load-fp16-MEU-119-handoff.md) |
| Plan folder scripts and records | new or modified | Shared with MEU-119 and MEU-120, and `closeout-decisions.md` (D-336, D-337) |

```diff
+export const PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32'] as const
 ...
-  return runnable.find((row) => row.is_downloaded)?.id ?? runnable[0]?.id ?? null
+  const order: ReadonlyArray<string> = PRESELECT_ORDER
+  const rank = (id: string): number => {
+    const index = order.indexOf(id)
+    return index === -1 ? order.length : index
+  }
+  // The sort is stable, so rows outside PRESELECT_ORDER keep their catalog order.
+  const ranked = [...runnable].sort((a, b) => rank(a.id) - rank(b.id))
+  return ranked.find((row) => row.is_downloaded)?.id ?? ranked[0]?.id ?? null
```

The excerpt is abridged. `tts-controls.ts:104-139` and `tools/smoke_packaged_tts.py:646-730` are the source.

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
| F2 | Medium | `SENTENCE_SMOKE` takes the frame count from the WAV header, so a 44-byte header declaring 100 frames passes; mechanism `task-row-completion-predicate`. The reviewer read every retained WAV of both INT8 runs and found 149 + 149 complete payloads (non-blocking) | `tools/smoke_packaged_tts.py:357`, `:710` | Require a PCM payload of the declared length and add a header-only negative fixture | Fixed on Mat's D-340 ruling (D-343, rows C3 and C4); `SMOKE-TTS-WAV-HEADER-TRUSTED` resolved; round 2 closed it (`fixed`) |

### Verdict

Round 1 of loop `s52-execution-2026-11-06-tts-load-fp16` returned `approved`, intent achieved `yes`, with two Medium findings, both non-blocking ([implementation-critical-review.md](2026-11-06-tts-load-fp16-implementation-critical-review.md)). F1 is MEU-120's and F2 is MEU-121's. D-339 files both as known issues, and D-340 asks Mat whether to fix them before the commit ([closeout-decisions.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md)). The round used 14,996,767 of the loop's 21,000,000 tokens, so the ledger refuses a round 2 until Mat continues the loop (`C:/Temp/av-kit/s52-exec-ledger-state-r1.txt`). The report was validated under `C:/Temp/av-kit` and copied byte for byte; H1-7a and H1-7b passed on the canonical copy (`C:/Temp/av-kit/review-state-check.txt`, `exec-review.txt`).

Mat ruled D-340 with "all recommendations accepted", "proceed with changes", "commit and push" (2026-11-07): fix both now. The recommended continue of 10,000,000 tokens was recorded at 2026-11-07T16:34:19Z (`C:/Temp/av-kit/s52-exec-ledger-continue-1.txt`), so the loop's budget is 31,000,000. Rows C1 to C4 fix F1 and F2, C5 resolves both issues, C6 reran the gate, and round 2 (row C8) rechecked F1 and F2. Round 2 returned `approved`, intent achieved `yes`, with F1 and F2 `fixed` in its Prior Pass Summary and no new finding, using 4,694,911 tokens (19,691,678 of 31,000,000 in all). Row C9's `--approved-state-only` check passed: approved at round 2 of 6, 0 open blocking findings.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| FP16's guarded phase computation | dependency | MEU-127 | Mat's D-336 ruling: FP16 stays as shipped, `TTS-ONNX-FP16-NONFINITE-AUDIO` stays `open`, and MEU-127 `svc-tts-fp16-phase-guard` tests the guard, spike first (03 §TTS FP16 phase guard (residual), matrix 3.18, D-345). H2-2 passes no `--decision-issue` for the issue (`implementation-plan.md:92`) |
| E2, ORT 1.24.4 and 1.29.0 | dependency | MEU-127 | Not run: the plan said both were in the uv cache, and offline uv couldn't resolve either. Nothing retried them online (S5) |
| A comment on HF discussion 22 with E5's finding | out-of-scope | — | Refused: Mat's D-336 ruling posts nothing to discussion 22 |
| The rc.2 repeat of Session 51's capability smoke | dependency | MEU-125 | The plan's §Out of Scope (`implementation-plan.md:426`) |
| Pre-existing pyright error in `tools/smoke_packaged_tts.py:734` (`__doc__.splitlines`, reportOptionalMemberAccess) | out-of-scope | — | It is at `HEAD` too (`:611` there), and `tools/` is outside the pyright include; `py-types` runs `pyright packages/`, which passes |
| Commit and push | out-of-scope | — | Authorized by Mat's "commit and push" (2026-11-07); it follows round 2's approval and the closeout addenda (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files written from the task cells, because the cells' `*>` needs PowerShell. `ELECTRON_RUN_AS_NODE` was unset for every UI, Electron and package run.
- **Row 9's FP16 file.** It was copied, read only, from the real `~/.avkit/models`. The models snapshot after rows 9, 10 and 11 found 0 changes.
- **The spike's network guard.** `run()` sets dead proxies on its own environment (`fp16-spike.py:706`), so no experiment or overlay child can fetch. It keeps the prior environment (`fetch_env`, `:705`) for E5's one hashed install alone.
- **No torch block.** An early draft of the spike blocked `torch` imports to show the experiments don't need it. spaCy's `curated-transformers` imports torch while phonemizing, so the block was removed before row 11's run. ORT runs without torch either way.
- **E2.** The plan said ORT 1.24.4 and 1.29.0 were in the uv cache (`implementation-plan.md:223`). Offline uv found neither, so the spike recorded both as `not_run` with uv's error, as the plan says to.
- **E5's dependency.** `ml-dtypes` 0.6.0 is the one dependency of `onnx` 1.23.2 that the venv lacked. It was pinned by hash at plan time and installed with `--no-deps`, so uv resolved nothing else.
- **The spike stopped at `done`, not at S13.** The FP16-outcome brief went to Mat anyway, as D-336 (D-338 below).
- **Rows C3 and C4.** `_generate` is called only by the offline phase (`:428`) and the sentences phase (`:710`); `phase_online` generates no WAV. Row C5 first wrote in `SMOKE-TTS-WAV-HEADER-TRUSTED`'s resolution that the online phase refuses short WAVs too. `s52-c5-register-fix` corrected that before gate run 2's last attempt.
- **H1-3 and H1-4.** They ran from Git Bash, so each cell's `*>` became `> 2>&1`, with `ELECTRON_RUN_AS_NODE` unset. The gate passed on run 1, and again on run 2 (row C6, D-341) after the review's fixes.

---

## Decision Log

```yaml
decision_log:
  - id: D-338
    stage: execution
    question: "The spike stopped at done (every experiment ran, no cause) and not at S13's 2-hour box. Is the FP16-outcome brief still written for Mat?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: D-336 in closeout-decisions.md is the FP16-outcome brief; the issue stays open and gets no --decision-issue flag"
    source_tag: Local Canon
    precedents: ["known-issues.yaml:4011 — D-239 item 3: if FP16 can't be made to work, what happens to the variant comes back to Mat", "implementation-plan.md:92 — a spike without a cause leaves the issue open, and the FP16 outcome comes back to Mat as a brief", "implementation-plan.md:516 — S13 sends the brief at the box", "implementation-plan.md:522 — the brief is written only if S13 is reached"]
    research: { engine: none, sources: [] }
    reasoning: "Stopping at done without a cause leaves FP16 where S13 would, only sooner: every experiment ran and none made the failing pairs finite. D-239 item 3 sends the variant's outcome to Mat whenever FP16 can't be made to work, and the plan's 'only if S13' assumed the box would be the stop. Not writing the brief would leave D-239 item 3 unanswered. A brief authorizes nothing, so writing it is two-way."
  - id: D-339
    stage: closeout
    question: "How are the execution review's two non-blocking findings recorded: F1, the models probe's leftover file (MEU-120), and F2, the smoke's header-only WAV (MEU-121)?"
    resolution: autonomous
    class: two-way
    chosen: "File both, open, medium and P3: GUI-MODELS-PROBE-LEFTOVER-FILE and SMOKE-TTS-WAV-HEADER-TRUSTED, each listed under its handoff's Deferred Items. Whether to fix them before the commit is Mat's: D-340 in closeout-decisions.md"
    source_tag: Local Canon
    precedents: ["docs/execution/reflections/2026-11-03-release-rc1-reflection.md:115 — D-200 filed the execution review's non-blocking note as a known issue, because dropping it would lose the reviewer's result", "docs/execution/reflections/2026-11-05-closeout-register-grammar-reflection.md:96 — D-289 put 'fixed now or registered as a known issue' for a non-blocking review finding to Mat"]
    research: { engine: tavily, sources: ["https://codeant.ai/blogs/code-review-best-practices — before merge, every requested change is addressed or explicitly deferred", "https://docs.gitlab.com/development/code_review — review comments are labelled non-blocking when they don't hold the merge"] }
    reasoning: "Either answer to D-340 starts from a filed issue: a fix closes it, and a commit as reviewed leaves it open. Left only in the review, the findings would be lost to the next triage, as D-200 says. Fixing now is not the coordinator's call: D-289 sent the same question to Mat, and a round 2 needs a ledger continue, because round 1 left 6,003,233 of 21,000,000 tokens. The severity stays the reviewer's Medium. Neither finding puts a raw value in a log, stdout or the Console, so Session 50's rule does not force a fix in the row."
  - id: D-343
    stage: execution
    question: "How does the smoke stop trusting a WAV header's frame count (review F2)?"
    resolution: autonomous
    class: two-way
    chosen: "In _generate, read the declared frames and the payload; wav_samples is the declared count only when the payload holds every declared frame, else 0. wav_declared keeps the header's count"
    source_tag: Local Canon
    precedents: ["tools/smoke_packaged_tts.py:357-365 — _generate's WAV read", "tools/smoke_packaged_tts.py:714-716 and :434 — the sentences and offline phases refuse 0 samples and 8,000 or fewer"]
    research: { engine: none, sources: [] }
    reasoning: "Reporting 0 for an incomplete file lets both phases' existing acceptance refuse it, so no acceptance changes. wav_declared keeps the header's count in the JSON, so a failure shows what the header claimed."
  - id: D-345
    stage: closeout
    question: "Where is D-336's follow-up registered?"
    resolution: autonomous
    class: two-way
    chosen: "MEU-127 svc-tts-fp16-phase-guard, phase 3, band P2, matrix row 3.18, depends on MEU-121, with 03 §TTS FP16 phase guard (residual) and MEU-127 in TTS-ONNX-FP16-NONFINITE-AUDIO's meu_links"
    source_tag: Local Canon
    precedents: ["docs/build-plan/build-priority-matrix.md row 3.17 — MEU-122, the Phase 3 residual before it", ".agent/context/meu-status.yaml MEU-122 — the residual entry's shape"]
    research: { engine: none, sources: [] }
    reasoning: "The fix is in the TTS service's model graph, Phase 3, like the MEU-122 residual before it. Linking the issue to the MEU lets the next triage see that the open issue has an owner."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Initial MEU-121 handoff after H1-2 |
| Reviewed | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 1 `approved` from the canonical report; its F2 is filed as `SMOKE-TTS-WAV-HEADER-TRUSTED`, and D-339 is in the Decision Log |
| Amended | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Rows C3 to C7 on Mat's D-336 and D-340 rulings: F2 fixed (D-343) and its issue resolved, MEU-127 registered (D-345), and gate run 2's `s52-gate-c6` in place of run 1's record |
| Rechecked | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 2 `approved` from the canonical report: F1 and F2 `fixed`, no new finding (row C8) |
