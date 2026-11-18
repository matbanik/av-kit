---
date: "2026-11-18"
project: "2026-11-17-tts-fp16-guard-ship"
meu: "MEU-144"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-14-tts-fp16-phase-guard-MEU-127-handoff.md"
---

# Handoff: 2026-11-17-tts-fp16-guard-ship-MEU-144-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-144 `svc-tts-fp16-guard-ship`, band P2, build priority matrix row 3.21. Session 74 ships the guarded FP16 graph that Session 73 built and Mat heard (MEU-127; D-797, Mat, `USER_EXPLICIT` 2026-11-15 "Ship guarded (Recommended)"). Executed on `main` from `174bafa` (`baseline.sha`).

- **The guard, in memory (`GUARD_IN_MEMORY`, D-1136 A).** `phase_guard.splice` inserts `IsNaN` and `Where` after `/decoder/decoder/generator/Div`, so a NaN phase quotient becomes `+0` and every finite one is unchanged (`PHASE_GUARD`). It reads the protobuf wire format with the standard library (no `onnx` package) and builds the result in one join over `memoryview` slices (`ONE_JOIN`). Any shape it does not know raises `SpliceError`; nothing is guessed.
- **The gate (`GUARD_GATE`, `GUARD_REFUSE`, `GUARD_APPLIED`, `NO_FILE_WRITE`, D-1137).** `guarded_model` considers only `kokoro-onnx-fp16`, and only a file of Session 73's size (163,234,740 bytes) and source hash (`ba4527a8…c334a`); it returns the bytes only when they hash to Session 73's guarded graph (`9037c82b…6fd33`). Anything else loads as shipped; a failed splice or a wrong result logs one `tts.phase_guard` warning with no path. Nothing is written to the models folder.
- **The adapter (`BOTH_SESSIONS`).** `KokoroAdapter._load_onnx` calls `guarded_model` once and hands the same model to the CUDA and the CPU `InferenceSession` (`adapter.py:401`, `:404`, `:416`; the import at `:38`).
- **The measurements.** On the pre-change packaged build FP16 fails the same 12 of 149 jobs as Sessions 52 and 73 (row 3). On the real file the guard gives Session 73's exact bytes within the 400,000,000-byte memory limit (row 6). On the post-change build FP16 passes 149 of 149 with every WAV equal by job to Session 73's guarded run (row 7), and INT8 passes 149 of 149 with every WAV equal by job to Session 73's INT8 run (row 8). The models copy never changed.
- **The records (row 9, D-1139).** `TTS-ONNX-FP16-NONFINITE-AUDIO` is `resolved`, with MEU-144 added to its links and its `resolution_path` byte-equal to row 0's; MEU-144 is `ready_for_review`; the 03 section holds the Session 74 Delivered note; grouping row 74 reads `executed (Session 74)`.

**Build Plan Section**: bp03, `docs/build-plan/03-service-layer.md` §TTS FP16 guard ship (residual) (anchor `tts-fp16-guard-ship-residual`), written by row 1 under D-1135 A; matrix row 3.21 (`build-priority-matrix.md:54`).

**Predecessor**: [MEU-127 handoff](2026-11-14-tts-fp16-phase-guard-MEU-127-handoff.md), Session 73. MEU-144 depends on MEU-127.

**Execution authorization:** `plan_to_exec_gate: human`. The approval is the plan's Status line (`implementation-plan.md:15`), quoting Mat `USER_EXPLICIT` 2026-11-17 "orchestrate the plan creation for all sessions and proceed with execution for each"; the plan review approved at round 1 (`.agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-plan-critical-review.md`).

**Mat's rulings and the rules applied.**

- **D-1135 A** (human, M-8): register MEU-144 `svc-tts-fp16-guard-ship`, matrix row 3.21 and a new 03 section after MEU-127's. `human_message_reference`: `USER_EXPLICIT 2026-11-17 AskUserQuestion 'A: register MEU-144 (Recommended)'`.
- **D-1136 A** (human, M-5): build the guarded graph in memory on each FP16 load from the user's file, checked against Session 73's source and result hashes; no file written, no new package, no download, no user-data read, no new listening; the issue closes on the 149-job packaged smoke, and FP16's preselection stays a separate question. `human_message_reference`: `USER_EXPLICIT 2026-11-17 AskUserQuestion 'A: guard in memory (Recommended)'`.
- **Applied:** D-797 (the guarded graph ships, through its own Red and review); D-336 (nothing posted to Hugging Face); D-333 (an adapter change needs its own Red); D-330 and D-331 (FP16 stays offered and is never preselected while INT8 or FP32 can run).
- **Plan decisions (autonomous, `mandatory: none`):** D-1137 (the guard's design: `GUARD_GATE` then `GUARD_REFUSE`), D-1138 (the tests on a 375-byte synthetic FP16 `Div` then `Atan` graph through real ONNX Runtime), D-1139 (the record mechanics: `register-meu-144.py`, `issue-resolve.py`, `meu_status.py`).
- **Execution decisions (autonomous, `mandatory: none`, in the plan's `decision_log`):** D-1140 and D-1141; see Departures.

**Receipts.** A receipt named by its file name alone (`ff-*.txt`, `ff-*.json`) is in this session's subfolder of the receipts folder (`RECEIPTS_DIR`). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-144.1 | unit | `splice(build())` on the synthetic model returns 839 bytes with SHA-256 `fbbd7205…26b7`; a second call returns equal bytes; the input still hashes to `57ba7da4…348b` | Local Canon (`PHASE_GUARD`) | `tests/unit/test_tts_phase_guard.py:54` | ✅ |
| AC-144.2 | unit | ORT CPU: `a=0, b=0` gives NaN from the source and `+0` (sign bit clear) from the guarded graph; `a=1, b=2` gives the same FP16 bytes from both | Local Canon (D-797; GRAPH_COMPARE) | `tests/unit/test_tts_phase_guard.py:69` | ✅ |
| AC-144.3 | unit | Each refusal raises `SpliceError` with its exact text (already guarded, two and no `Div`, not a `Div`, quotient output, no `Atan`, no initializer, two and no graphs, truncated message, truncated and long varint, wire type 3, a non-UTF-8 name) | Local Canon (`GUARD_IN_MEMORY`) | `tests/unit/test_tts_phase_guard.py:105`, `:127`, `:140` | ✅ |
| AC-144.4 | unit | `GUARD_GATE`: with `read_bytes` patched to raise, INT8 on a missing path, FP16 on a missing path and FP16 one byte too long return `str(path)` and log nothing | Local Canon (`GUARD_GATE`, D-1137) | `tests/unit/test_tts_phase_guard.py:153` | ✅ |
| AC-144.5 | unit | A file of the spec's size with another hash returns `str(path)` and logs nothing | Local Canon (`GUARD_PASS_THROUGH`) | `tests/unit/test_tts_phase_guard.py:179` | ✅ |
| AC-144.6 | unit | `GUARD_REFUSE`: a refused splice and a wrong result hash each return `str(path)` with one warning (`reason` `SpliceError`, `result_hash`); no event value holds the path or the file name | Local Canon; D-323 | `tests/unit/test_tts_phase_guard.py:195` | ✅ |
| AC-144.7 | unit | `GUARD_APPLIED`: the result is `bytes` equal to `splice(build())`, with exactly one event whose keys are `event`, `log_level`, `module`, `variant_id`, `outcome` (`applied`, `info`) | Local Canon (`GUARD_APPLIED`) | `tests/unit/test_tts_phase_guard.py:244` | ✅ |
| AC-144.8 | unit | `NO_FILE_WRITE`: after an applied, a refused and a pass-through call, every file keeps its bytes and `st_mtime_ns` and the folder lists the same names | Local Canon (`NO_FILE_WRITE`) | `tests/unit/test_tts_phase_guard.py:271` | ✅ |
| AC-144.9 | integration | `BOTH_SESSIONS`: CUDA refused falls back to CPU with the same `bytes` object; an accepted CUDA session gets the bytes; INT8 gives both calls `str(path)`; one `guarded_model` call | Local Canon (`BOTH_SESSIONS`) | `tests/integration/test_tts_phase_guard_load.py:111`, `:133`, `:152` | ✅ |
| AC-144.10 | guard | The four pin files pass at Red and at Green and are byte-identical to row 0 | Local Canon (§Test pins) | the cross-reference rows below; `ff-red-pins.txt`, `ff-green.txt`, `ff-D6-scope-paths.txt` | ✅ |
| AC-144.11 | integration | Real ORT through the adapter: with the synthetic spec, `run(["y"], {a: 0, b: 0})` is `+0`; with `KOKORO_FP16` as shipped the same file gives NaN | Local Canon (`GUARD_IN_MEMORY`, `GUARD_GATE`) | `tests/integration/test_tts_phase_guard_load.py:176` | ✅ |
| AC-144.12 | check | `guard-check.py` on the models copy: 163,235,204 bytes, SHA-256 `9037c82b…`; the source keeps its hash, size and `st_mtime_ns`; an ORT CPU session builds; one `applied` event; INT8 returns `str`; `tracemalloc` peak at most 400,000,000 bytes | Local Canon (`GUARD_BYTES_EQUAL`; D-797) | row 6 `ff-guard-check.json`; gate `guard-check` | ✅ |
| AC-144.13 | check | Packaged Red: FP16 on the pre-change build exits 1, 149 jobs, 12 failures all "generated audio must be finite", equal to Sessions 52 and 73; `BUILD_SAME`: its 137 WAVs equal Session 73's control run by job | Local Canon (Session 73 row 5) | row 3 `ff-smoke-control-check.txt`, `ff-wavs-control.txt` | ✅ |
| AC-144.14 | check | Packaged Green: FP16 on the post-change build exits 0, 149 of 149; `WAV_BY_JOB`: all 149 WAVs equal Session 73's guarded run; `NO_FILE_WRITE`: the models copy equals its row-2 snapshot | Local Canon (D-797) | row 7 `ff-smoke-guarded-check.txt`, `ff-wavs-guarded.txt`, `ff-models-snapshot-7.txt` | ✅ |
| AC-144.15 | check | INT8 on the post-change build passes 149 of 149 and its WAVs equal Session 73's INT8 run by job; the snapshot still matches | Local Canon (`GUARD_GATE`) | row 8 `ff-smoke-int8-check.txt`, `ff-wavs-int8.txt`, `ff-models-snapshot-8.txt` | ✅ |
| AC-144.16 | check | `PRESELECT_KEPT`: `tts-controls.ts` and `voices.py` keep their row-0 SHA-256 and the `PRESELECT_ORDER` line is unchanged | Human-approved (D-330, D-331; D-797) | row 9 `ff-row9-check.txt` | ✅ |
| AC-144.17 | check | Records: the issue `resolved` with the five links and its `resolution_path` byte-equal to row 0's; both renders pass; MEU-144 `ready_for_review`; the 03 Delivered note; grouping row 74 only | Local Canon (D-797, D-801; D-1139) | row 9 `ff-row9-check.txt`, `ff-issues-render-check.txt`, `ff-status-render-check.txt` | ✅ |

**Cross-reference rows (the pins, §Test pins; AC-144.10's guard).** These files belong to other families and are cited by file and line only. Each passed unchanged at Red (`ff-red-pins.txt`: `62 passed in 15.51s`) and at Green (`ff-green.txt`: `171 passed in 18.22s`), and the gate's `scope-paths` found every read-only file unchanged (`ff-D6-scope-paths.txt`).

| Pin | What it checks | Result |
|-----|----------------|--------|
| `tests/integration/test_tts_device_resolution.py:126` (the fake is patched at exactly `avkit_infra.tts.adapter.InferenceSession`), `_adapter` `:132`, `_variant` `:140`, `_events` `:159` | CUDA and CPU session construction and the fallback logs | Unchanged, passes: FP32 variant, so the guard returns `str(path)` |
| `tests/integration/test_tts_models.py:278` (`FakeSession`) | The load and unload sequence | Unchanged, passes |
| `tests/integration/test_tts_no_torch.py:72` (`FakeSession.__init__` stores the path) | An ONNX load needs no torch | Unchanged, passes: INT8 passes through |
| `tests/e2e/test_api_model_load_keeps.py:35-43` (the session records the file name it was built on) | A failed load keeps the loaded model | Unchanged, passes: INT8 passes through |

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-144.1 | `E   AssertionError: avkit_infra.tts.phase_guard does not exist yet` (`ff-red.txt`, `25 failed in 1.09s`) | Row 5: `171 passed in 18.22s` (`ff-green.txt`) | `tests/unit/test_tts_phase_guard.py:54` |
| AC-144.2 | As AC-144.1 (`ff-red.txt`) | As AC-144.1 | `tests/unit/test_tts_phase_guard.py:69` |
| AC-144.3 | As AC-144.1, 14 cases (`ff-red.txt`) | As AC-144.1 | `tests/unit/test_tts_phase_guard.py:105`, `:127`, `:140` |
| AC-144.4 | As AC-144.1 (`ff-red.txt`) | As AC-144.1 | `tests/unit/test_tts_phase_guard.py:153` |
| AC-144.5 | As AC-144.1 (`ff-red.txt`) | As AC-144.1 | `tests/unit/test_tts_phase_guard.py:179` |
| AC-144.6 | As AC-144.1 (`ff-red.txt`) | As AC-144.1 | `tests/unit/test_tts_phase_guard.py:195` |
| AC-144.7 | As AC-144.1 (`ff-red.txt`) | As AC-144.1 | `tests/unit/test_tts_phase_guard.py:244` |
| AC-144.8 | As AC-144.1 (`ff-red.txt`) | As AC-144.1 | `tests/unit/test_tts_phase_guard.py:271` |
| AC-144.9 | As AC-144.1, 3 tests (`ff-red.txt`) | As AC-144.1 | `tests/integration/test_tts_phase_guard_load.py:111`, `:133`, `:152` |
| AC-144.11 | As AC-144.1 (`ff-red.txt`) | As AC-144.1 | `tests/integration/test_tts_phase_guard_load.py:176` |

AC-144.10 passed at Red and is a guard; AC-144.12 to AC-144.17 are checks. `ff-red-check.txt`: `red-check: 1 receipt(s), 10 required test(s), 0 problem(s)`; the Red's pytest exit code was 1 (`ff-red.txt.exit`).

- **Row 0, baseline** (`ff-baseline.txt`): `baseline.sha 174bafa8a9ff327d38e54bd36f3edcb0e0b62085`; `moved anchors 0`; `host-load: ran at 14.8 %`; the base suite `3087 passed, 37 warnings in 233.55s (0:03:53)` (`ff-base-py.txt`); `eol-check: 18 scope path(s), 0 problem(s)`; `baseline: all steps exit 0`. Run 1 of row 0 failed at its base ruff step and is kept as `ff-run1-*` (D-1141).
- **Row 1, registration** (`ff-register.txt`): `meu-status.yaml lines added: 25 CR bytes: 0`; `03-service-layer.md CRLF: True anchor count: 1 bytes: 86505`; `build-priority-matrix.md CRLF: True MEU-144 rows: 1 bytes: 25754`; `MEU-144: ('pending', '3', 'P2', '3.21', ['MEU-127']) order: ['MEU-143', 'MEU-144', 'MEU-145']`; `register-meu-144: ok`. `ff-register-selftest.txt`: `register-meu-144 selftest: 31 case(s), 0 wrong: []`. `ff-register-render-check.txt`: the drift check passed (`159 MEUs, 12 phases`). `ff-register-canon.txt`: `Tests  14 passed (14)`.
- **Row 2, build and copies** (`ff-s9-2.txt`: `S9: already exists: []`; `ff-host-load-2.txt`: `host-load: ran at 25.4 %`; `ff-build-control.txt`: `Build complete!`; `ff-copies-control.txt`: `smoke-check copies: pass`; `ff-models-snapshot-0.txt`: `153 file(s), 299058987 bytes`, `smoke-check snapshot: pass`).
- **Row 3, packaged Red (AC-144.13)** (`ff-host-load-3.txt`: `host-load: ran at 17 %`; `ff-smoke-control.txt`: `FAIL: smoke_packaged_tts sentences`, `"jobs": 149`). `ff-smoke-control-check.txt`: `control failures_12: True`, `control all_not_finite: True`, `control same_failures_as_ref0: True`, `control same_failures_as_ref1: True`, `control dead_proxy: True`, `smoke-check control: pass`. `BUILD_SAME` (`ff-wavs-control.txt`): `wavs jobs=149 done_ours=137 done_against=137 equal=137`, `smoke-check wavs: pass`. `ff-models-snapshot-3.txt`: `smoke-check snapshot-compare: pass`.
- **Row 4, Red** (`ff-host-load-4.txt`: `host-load: ran at 22.2 %`): `25 failed in 1.09s` (`ff-red.txt`); the pins `62 passed in 15.51s` (`ff-red-pins.txt`); `ff-red-hashes.txt` records the three test-side files' SHA-256 (`tests/tts_onnx_synthetic.py` `91365fdc…`, `tests/unit/test_tts_phase_guard.py` `d328f5d3…`, `tests/integration/test_tts_phase_guard_load.py` `602e9a7a…`), each CRLF, and `phase_guard.py` absent.
- **Row 5, Green**: `171 passed in 18.22s` (`ff-green.txt`); `test-side files changed since Red: []` (`ff-green-immutable.txt`); `5 files already formatted` (`ff-green-format.txt`); `All checks passed!` (`ff-green-lint.txt`); `0 errors, 0 warnings, 0 informations` (`ff-green-types.txt`); `eol-check: 18 scope path(s), 0 problem(s)` (`ff-green-eol.txt`). `phase_guard.py` was written CRLF, 246 lines (`ff-write-phase-guard.txt`); `adapter.py` kept CRLF, 554 lines (`ff-adapter-edit.txt`).
- **Row 6, the real file (AC-144.12)** (`ff-guard-check.json`, `ff-guard-check.txt`): `guard-check: pass`, every check `true` (`source_sha256`, `source_bytes`, `result_is_bytes`, `result_bytes`, `result_sha256`, `one_applied_event`, `peak_within_limit`, `ort_cpu_session`, `int8_returns_str`, `fp16_file_unchanged`); `result_bytes` 163235204; `result_sha256` `9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33`; `wall_seconds` 0.571; `tracemalloc_peak_bytes` 329181494 (`tracemalloc_peak_MB` 313.9) against `peak_limit_bytes` 400000000; one event `{"module": "tts", "variant_id": "kokoro-onnx-fp16", "outcome": "applied", "event": "tts.phase_guard", "log_level": "info"}`. `ff-guard-check-selftest.txt`: 4 cases, 0 wrong. `ff-models-snapshot-6.txt`: `smoke-check snapshot-compare: pass`.
- **Row 7, packaged Green (AC-144.14)** (`ff-green-source-hashes.txt`: `phase_guard.py` `04d15aa6…5f22`, `adapter.py` `a898311c…24d5`; `ff-s9-7.txt`; `ff-build-guarded.txt`: `Build complete!`; `ff-copies-run-guarded.txt`, `ff-copies-run-int8.txt`: `smoke-check copies: pass`; `ff-host-load-7.txt`: `host-load: ran at 18.4 %`). `ff-smoke-guarded.txt`: `PASS: smoke_packaged_tts sentences`. `ff-smoke-guarded-check.txt`: `green passed_true: True`, `green failures_empty: True`, `green dead_proxy: True`, `smoke-check green: pass`. `WAV_BY_JOB` (`ff-wavs-guarded.txt`): `wavs jobs=149 done_ours=149 done_against=149 equal=149`, `wavs every_key_done: True`, `wavs wavs_byte_equal: True`, `smoke-check wavs: pass`. `NO_FILE_WRITE` (`ff-models-snapshot-7.txt`): `smoke-check snapshot-compare: pass`.
- **Row 8, INT8 (AC-144.15)** (`ff-host-load-8.txt`: `host-load: ran at 25.4 %`). `ff-smoke-int8.txt`: `PASS: smoke_packaged_tts sentences`. `ff-smoke-int8-check.txt`: `green variant: True`, `green failures_empty: True`, `smoke-check green: pass`. `ff-wavs-int8.txt`: `wavs jobs=149 done_ours=149 done_against=149 equal=149`, `smoke-check wavs: pass`. `ff-models-snapshot-8.txt`: `smoke-check snapshot-compare: pass`.
- **The four snapshot compares** (rows 3, 6, 7, 8): each `snapshot ...models-copy: 153 file(s), 299058987 bytes` and `smoke-check snapshot-compare: pass` (`ff-models-snapshot-3.txt`, `-6.txt`, `-7.txt`, `-8.txt`).
- **Row 9, records (AC-144.16, AC-144.17).** `ff-delivered.txt`: `03-service-layer.md bytes: 86505 -> 88684 CRLF: True`, `Session 74 note count: 1`, `register-meu-144 --delivered: ok`. `ff-issue-resolve.txt`: `decision logs read: 104 of 104`, `register sha256 before=131fb1e0eb895f2924686a1bca76ef7bb770e8c307180ec9696068810ce93852`, `target sha256 after=7193d37747ba94f82c95ee1a531d00049e4779d6b6a0392ecfd9d4bd257ef581 CRLF=0 LF=5720`, `parsed fields changed: 5` (`meu_links`, `status`, `verification.last_checked`, `.method`, `.result`), `issue-resolve: 0 problem(s)`. `ff-issues-render.txt`: `Rendered known-issues.md: 42 lines`; `ff-issues-render-check.txt`: `OK: known-issues.md is up-to-date`. `ff-status-144.txt`: `Updated MEU-144 → ready_for_review (updated: 2026-11-18)`; `ff-status-render-check.txt`: the drift check passed. `ff-row9-check.txt`: `issue resolved, links, resolution_path kept: True ['MEU-121', 'MEU-127', 'MEU-144', 'MEU-62', 'MEU-72'] 03 note once and CRLF: True grouping lines changed: [162]`, row 74 `executed (Session 74)` with this plan folder, `preselect kept: True`.
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-0.ps1 (task.md row 0's Validation cell: baseline.ps1 records baseline.sha, the dirty list, the scope, pin and skip hashes, the line-ending baseline, the Session 73 receipts by hash and the base Python suite, with the plan-local selftests); run 2 under D-1141, run 1 kept as C:/Temp/av-kit/tts-fp16-guard-ship/ff-run1-*; receipts ff-baseline.txt, ff-base-py.txt, ff-base-ruff.txt", "scope": "Row 0: the baseline at 174bafa and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus row 0", "output": "ff-baseline.txt: baseline.sha 174bafa8a9ff327d38e54bd36f3edcb0e0b62085; moved anchors 0; host-load: ran at 14.8 %; eol-check: 18 scope path(s), 0 problem(s); baseline: all steps exit 0. ff-base-py.txt: 3087 passed, 37 warnings in 233.55s (0:03:53)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-1-register", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-1.ps1 (task.md row 1's Validation cell: register-meu-144.py --selftest, register-meu-144.py, meu_status.py get and render, render --check, the canon Vitest); receipts ff-register-selftest.txt, ff-register.txt, ff-register-get.txt, ff-register-render.txt, ff-register-render-check.txt, ff-register-eol.txt, ff-register-canon.txt", "scope": "Row 1: MEU-144 registered under D-1135 A (meu-status, the 03 section, matrix row 3.21)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 and 1", "output": "ff-register-selftest.txt: register-meu-144 selftest: 31 case(s), 0 wrong: []. ff-register.txt: meu-status.yaml lines added: 25 CR bytes: 0; 03-service-layer.md CRLF: True anchor count: 1 bytes: 86505; build-priority-matrix.md CRLF: True MEU-144 rows: 1 bytes: 25754; MEU-144: ('pending', '3', 'P2', '3.21', ['MEU-127']); register-meu-144: ok. ff-register-render-check.txt: Drift check passed (159 MEUs, 12 phases). ff-register-canon.txt: Tests  14 passed (14)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-2-build-control", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-2.ps1 (task.md row 2's Validation cell: the S9 check, host-load.ps1, tools/package_backend.py on the pre-change tree, the copy of the build, smoke-check.py copies, the models-copy snapshot); receipts ff-s9-2.txt, ff-host-load-2.txt, ff-build-control.txt, ff-copies-control.txt, ff-models-snapshot-0.txt", "scope": "Row 2: the pre-change packaged build and Session 73's copies", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 2", "output": "ff-s9-2.txt: S9: already exists: []. ff-host-load-2.txt: host-load: ran at 25.4 %. ff-build-control.txt: Build complete!. ff-copies-control.txt: smoke-check copies: pass. ff-models-snapshot-0.txt: 153 file(s), 299058987 bytes; smoke-check snapshot: pass."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-3-packaged-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-3.ps1 (task.md row 3's Validation cell: host-load.ps1, tools/smoke_packaged_tts.py --phase sentences with kokoro-onnx-fp16 on the pre-change build, smoke-check.py control, wavs and snapshot-compare); receipts ff-host-load-3.txt, ff-smoke-control.json, ff-smoke-control.txt, ff-smoke-control-check.txt, ff-wavs-control.txt, ff-models-snapshot-3.txt", "scope": "AC-144.13: packaged Red and BUILD_SAME", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 3", "output": "ff-host-load-3.txt: host-load: ran at 17 %. ff-smoke-control.txt: FAIL: smoke_packaged_tts sentences. ff-smoke-control-check.txt: control failures_12: True; control all_not_finite: True; control same_failures_as_ref0: True; control same_failures_as_ref1: True; control dead_proxy: True; smoke-check control: pass. ff-wavs-control.txt: wavs jobs=149 done_ours=137 done_against=137 equal=137; smoke-check wavs: pass. ff-models-snapshot-3.txt: smoke-check snapshot-compare: pass."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-4-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-4.ps1 (task.md row 4's Validation cell: host-load.ps1, uv run pytest tests/unit/test_tts_phase_guard.py tests/integration/test_tts_phase_guard_load.py, its exit code, red-check.py --require the ten Red tests, the four pin files, the hash check); receipts ff-host-load-4.txt, ff-red.txt, ff-red.txt.exit, ff-red-check.txt, ff-red-pins.txt, ff-red-hashes.txt, ff-red-hashes.json", "scope": "AC-144.1 to AC-144.9 and AC-144.11 Red with phase_guard.py absent; AC-144.10 pins pass", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 4", "output": "ff-host-load-4.txt: host-load: ran at 22.2 %. ff-red.txt: E   AssertionError: avkit_infra.tts.phase_guard does not exist yet; 25 failed in 1.09s; child exit 1. ff-red-check.txt: red-check: 1 receipt(s), 10 required test(s), 0 problem(s). ff-red-pins.txt: 62 passed in 15.51s. ff-red-hashes.txt: the five pin and adapter files kept since row 0: all True; CRLF: all True; phase_guard.py absent: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-5-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-5.ps1 (task.md row 5's Validation cell: phase_guard.py written and adapter.py edited by bytes, CRLF kept; uv run pytest on the two new files and the four pins; the immutability check; ruff format --check; ruff check; pyright; eol-check.py); receipts ff-write-phase-guard.txt, ff-adapter-edit.txt, ff-green.txt, ff-green-immutable.txt, ff-green-format.txt, ff-green-lint.txt, ff-green-types.txt, ff-green-eol.txt", "scope": "AC-144.1 to AC-144.11 Green", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 5", "output": "ff-write-phase-guard.txt: phase_guard.py: CRLF 246 sha256 04d15aa6e2f18a252e99912b02517b4cb2b4cef8b14767b501bc2e4a5ca45f22. ff-adapter-edit.txt: adapter.py: 4 edits, CRLF 554 sha256 a898311c34fa7ed3c8c82c4deaf46c317f3af286987692992a9d108c261b24d5. ff-green.txt: 171 passed in 18.22s. ff-green-immutable.txt: test-side files changed since Red: []. ff-green-format.txt: 5 files already formatted. ff-green-lint.txt: All checks passed!. ff-green-types.txt: 0 errors, 0 warnings, 0 informations. ff-green-eol.txt: eol-check: 18 scope path(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-6-guard-check", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-6.ps1 (task.md row 6's Validation cell: guard-check.py --selftest, then guard-check.py on C:/Temp/av-kit/tts-fp16-guard-ship/models-copy, smoke-check.py snapshot-compare); receipts ff-guard-check-selftest.txt, ff-guard-check.json, ff-guard-check.txt, ff-models-snapshot-6.txt", "scope": "AC-144.12: the real FP16 file through guarded_model (GUARD_BYTES_EQUAL)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 6", "output": "ff-guard-check-selftest.txt: guard-check selftest: 4 case(s), 0 wrong. ff-guard-check.json: result_bytes 163235204; result_sha256 9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33; wall_seconds 0.571; tracemalloc_peak_bytes 329181494; peak_limit_bytes 400000000; one applied event; every check true. ff-guard-check.txt: guard-check: pass. ff-models-snapshot-6.txt: smoke-check snapshot-compare: pass."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-7-packaged-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-7.ps1 (task.md row 7's Validation cell: the source hashes, the S9 check, host-load.ps1, tools/package_backend.py on the post-change tree, the copies, tools/smoke_packaged_tts.py --phase sentences with kokoro-onnx-fp16, smoke-check.py green, wavs against Session 73's guarded run and snapshot-compare); receipts ff-green-source-hashes.txt, ff-s9-7.txt, ff-build-guarded.txt, ff-copies-run-guarded.txt, ff-copies-run-int8.txt, ff-host-load-7.txt, ff-smoke-guarded.json, ff-smoke-guarded.txt, ff-smoke-guarded-check.txt, ff-wavs-guarded.txt, ff-models-snapshot-7.txt", "scope": "AC-144.14: packaged Green, WAV_BY_JOB and NO_FILE_WRITE", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 7", "output": "ff-s9-7.txt: S9: already exists: []. ff-build-guarded.txt: Build complete!. ff-copies-run-guarded.txt: smoke-check copies: pass. ff-host-load-7.txt: host-load: ran at 18.4 %. ff-smoke-guarded.txt: PASS: smoke_packaged_tts sentences. ff-smoke-guarded-check.txt: green passed_true: True; green failures_empty: True; green dead_proxy: True; smoke-check green: pass. ff-wavs-guarded.txt: wavs jobs=149 done_ours=149 done_against=149 equal=149; smoke-check wavs: pass. ff-models-snapshot-7.txt: smoke-check snapshot-compare: pass."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-8-int8", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-8.ps1 (task.md row 8's Validation cell: host-load.ps1, tools/smoke_packaged_tts.py --phase sentences with kokoro-onnx-int8 on the post-change build, smoke-check.py green, wavs against Session 73's INT8 run and snapshot-compare); receipts ff-host-load-8.txt, ff-smoke-int8.json, ff-smoke-int8.txt, ff-smoke-int8-check.txt, ff-wavs-int8.txt, ff-models-snapshot-8.txt", "scope": "AC-144.15: INT8 on the post-change build (GUARD_GATE)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 8", "output": "ff-host-load-8.txt: host-load: ran at 25.4 %. ff-smoke-int8.txt: PASS: smoke_packaged_tts sentences. ff-smoke-int8-check.txt: green variant: True; green failures_empty: True; smoke-check green: pass. ff-wavs-int8.txt: wavs jobs=149 done_ours=149 done_against=149 equal=149; smoke-check wavs: pass. ff-models-snapshot-8.txt: smoke-check snapshot-compare: pass."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-9-records", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-9.ps1 (task.md row 9's Validation cell: register-meu-144.py --delivered with C:/Temp/av-kit/tts-fp16-guard-ship/delivered-note.md, issue-resolve.py --issue TTS-ONNX-FP16-NONFINITE-AUDIO --set-file C:/Temp/av-kit/tts-fp16-guard-ship/issue-resolve-set.json, issue_triage.py render and render --check, meu_status.py set MEU-144 ready_for_review, render and render --check, the row 9 check), after C:/Temp/av-kit/tts-fp16-guard-ship/tmp/grouping-74.py replaced grouping line 162 by bytes; receipts ff-delivered.txt, ff-issue-resolve.txt, ff-issues-render.txt, ff-issues-render-check.txt, ff-status-144.txt, ff-status-render.txt, ff-status-render-check.txt, ff-row9-check.txt", "scope": "AC-144.16 (PRESELECT_KEPT) and AC-144.17 (the records, D-1139)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 9", "output": "ff-delivered.txt: 03-service-layer.md bytes: 86505 -> 88684 CRLF: True; Session 74 note count: 1; register-meu-144 --delivered: ok. ff-issue-resolve.txt: decision logs read: 104 of 104; register sha256 before=131fb1e0eb895f2924686a1bca76ef7bb770e8c307180ec9696068810ce93852; target sha256 after=7193d37747ba94f82c95ee1a531d00049e4779d6b6a0392ecfd9d4bd257ef581 CRLF=0 LF=5720; parsed fields changed: 5; issue-resolve: 0 problem(s). ff-issues-render.txt: Rendered known-issues.md: 42 lines. ff-issues-render-check.txt: OK: known-issues.md is up-to-date. ff-status-144.txt: Updated MEU-144 -> ready_for_review (updated: 2026-11-18). ff-status-render-check.txt: Drift check passed. ff-row9-check.txt: issue resolved, links, resolution_path kept: True; 03 note once and CRLF: True; grouping lines changed: [162]; row 74 executed (Session 74); preselect kept: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-h1-1-task-rows", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-H1-1.ps1 (task.md row H1-1's Validation cell); receipt task-unchecked.txt", "scope": "H1-1: every implementation row is checked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 174bafa (baseline.sha) plus rows 0 to 9", "output": "task-unchecked.txt: unchecked implementation rows: []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-H1-2.ps1 (task.md row H1-2's Validation cell, after the load probe: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-17-tts-fp16-guard-ship/session-gate.ps1 *> C:/Temp/av-kit/tts-fp16-guard-ship/ff-gate-h1.txt); step receipts C:/Temp/av-kit/tts-fp16-guard-ship/ff-D6-<step>.txt", "scope": "H1-2: the PROFILE D6 session gate, 22 run steps from identity-before to identity-after, including the full Python suite and the real-file guard check", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "174bafa8a9ff327d38e54bd36f3edcb0e0b62085+8afc8a7a04434687c654454239b91bef722d1ce387854ee7b8fa52ef27bfce73", "output": "ff-gate-h1.txt: every step exit=0 (identity-before, task-contract, scope-paths, line-endings, home-path, four selftests, py-format, py-lint, py-types, meu-144-unit, meu-144-integration, guard-check, green-source, host-load, py-tests, state-render, issues-render-check, canon-vitest, identity-after); tested_state before and after equal; session-gate: all steps exit 0. ff-D6-host-load.txt: host-load samples: [23, 26, 24, 40, 32] mean=29; host-load: ran at 29 % (bar 50 %, waited 13 s). ff-D6-meu-144-unit.txt: 21 passed in 1.09s. ff-D6-meu-144-integration.txt: 66 passed in 4.26s. ff-D6-guard-check.json: result_sha256 9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33; tracemalloc_peak_bytes 329181494. ff-D6-green-source.txt: green-source: same as row 7. ff-D6-py-tests.txt: 3112 passed, 37 warnings in 259.28s (0:04:19). ff-D6-state-render.txt: Drift check passed - SSOT loaded (159 MEUs, 12 phases), rendered regions match on-disk content. ff-D6-issues-render-check.txt: OK: known-issues.md is up-to-date. ff-D6-canon-vitest.txt: Test Files  2 passed (2); Tests  14 passed (14). ff-D6-identity-after.txt: tested_state 174bafa8a9ff327d38e54bd36f3edcb0e0b62085+8afc8a7a04434687c654454239b91bef722d1ce387854ee7b8fa52ef27bfce73."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ff-h1-3-h1-4-closeout-checks", "command": "python C:/Temp/av-kit/tts-fp16-guard-ship/tmp/focus-entry.py (the Session 74 paragraph on top of .agent/context/current-focus.md, by bytes, CRLF kept, after checking it still had its row-0 hash); pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-H1-3.ps1 (meu_status.py render --check *> C:/Temp/av-kit/tts-fp16-guard-ship/ff-render-check.txt; meu_status.py get MEU-144 *> C:/Temp/av-kit/tts-fp16-guard-ship/ff-h13-status-144.txt); pwsh -NoProfile -File C:/Temp/av-kit/tts-fp16-guard-ship/rows/row-H1-4.ps1 (task.md row H1-4's skip-basis check *> C:/Temp/av-kit/tts-fp16-guard-ship/skip-basis-check.txt)", "scope": "H1-3 (MEU-144 status, current-focus and the state render) and H1-4 (the UI, OpenAPI and MCP skip basis, S14)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus paragraph", "output": "focus-entry.py: current-focus.md: bytes 85128 -> 86630 CRLF 212 -> 215 bare LF 0. ff-render-check.txt: Drift check passed - SSOT loaded (159 MEUs, 12 phases), rendered regions match on-disk content. ff-h13-status-144.txt: \"status\": \"ready_for_review\". skip-basis-check.txt: ui, mcp-server, tools, packages/api or packages/core changes since row 0: []"}
```

### Quality Gate Results

| Step | Result (receipt) |
|------|------------------|
| Gate | `session-gate: all steps exit 0` (`ff-gate-h1.txt`); 22 run steps, each `exit=0` |
| Identity | `tested_state 174bafa8a9ff327d38e54bd36f3edcb0e0b62085+8afc8a7a04434687c654454239b91bef722d1ce387854ee7b8fa52ef27bfce73`, equal before and after (`ff-D6-identity-before.txt`, `ff-D6-identity-after.txt`) |
| Task contract | `OK: 27 row(s); 10-column table (with builder_model); 25 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1` (`ff-D6-task-contract.txt`) |
| Scope | `changed paths: 58 outside scope: [] other sessions plan files skipped: 25`; `read-never-changed files: 12 mismatch: [] baseline-dirty hash mismatch: []`; `head: 174bafa8a9ff327d38e54bd36f3edcb0e0b62085 head moved (S4): False` (`ff-D6-scope-paths.txt`) |
| Line endings | `eol-check: 18 scope path(s), 0 problem(s)` (`ff-D6-line-endings.txt`) |
| Home path | `check_home_path: ok files=2611 allowlisted=60 nul=31` (`ff-D6-home-path.txt`) |
| Selftests | `red-check selftest: 86 fixture(s) (21 positive, 65 negative), 0 wrong: []`; `eol-check selftest: 25 case(s), 0 wrong: []`; `smoke-check selftest: 33 case(s), 0 wrong: []`; `home-redact selftest: 19 case(s), 0 wrong: []` |
| Format, lint, types | `13 files already formatted`; `All checks passed!`; `0 errors, 0 warnings, 0 informations` (`ff-D6-py-format.txt`, `ff-D6-py-lint.txt`, `ff-D6-py-types.txt`) |
| MEU-144 tests | `21 passed in 1.09s` (`ff-D6-meu-144-unit.txt`); `66 passed in 4.26s` (`ff-D6-meu-144-integration.txt`) |
| Real file | `guard-check: pass`; `result_bytes` 163235204, `result_sha256` `9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33`, `tracemalloc_peak_bytes` 329181494 against 400000000 (`ff-D6-guard-check.json`, `ff-D6-guard-check.txt`) |
| Green source | `green-source: same as row 7` (`ff-D6-green-source.txt`) |
| Host load | `host-load: ran at 29 % (bar 50 %, waited 13 s)` (`ff-D6-host-load.txt`) |
| Python, full | `3112 passed, 37 warnings in 259.28s (0:04:19)` (`ff-D6-py-tests.txt`; row 0 had `3087 passed` (`ff-base-py.txt`), and the 25 new MEU-144 tests that failed at Red (`ff-red.txt`: `25 failed`) make 3112) |
| Registers | `Drift check passed - SSOT loaded (159 MEUs, 12 phases), rendered regions match on-disk content` (`ff-D6-state-render.txt`); `OK: known-issues.md is up-to-date` (`ff-D6-issues-render-check.txt`) |
| Canon Vitest | `Test Files  2 passed (2)`; `Tests  14 passed (14)` (`ff-D6-canon-vitest.txt`) |
| Skipped by the gate, with its reason line | `ui-types/ui-lint/ui-tests/ui-build/ui-electron`, `mcp-types/mcp-build/mcp-tests/mcp-audit` and `openapi`: every file under `ui/`, `mcp-server/`, `packages/api/` and `packages/core/` keeps its `baseline-skip-hashes.json` hash (H1-4, S14); `packaged-smokes`: rows 7 and 8 ran them on the final `phase_guard.py` and `adapter.py`, and `green-source` shows both unchanged since row 7 (`ff-gate-h1.txt`) |
| H1-3 | MEU-144 `"status": "ready_for_review"` (`ff-h13-status-144.txt`); the state render's drift check passed after the current-focus paragraph (`ff-render-check.txt`) |
| H1-4 | `ui, mcp-server, tools, packages/api or packages/core changes since row 0: []` (`skip-basis-check.txt`); so the UI, OpenAPI and MCP checks are skipped (S14) |

---

## Changed Files

Counts are added / removed lines against `HEAD` `174bafa` (`git diff --numstat --ignore-cr-at-eol`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step, `ff-D6-line-endings.txt`).

| File | Action | Lines | Line endings |
|------|--------|-------|--------------|
| `packages/infrastructure/src/avkit_infra/tts/phase_guard.py` | new | 246 | CRLF |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | +4 / -2 | CRLF, kept |
| `tests/tts_onnx_synthetic.py` | new | 120 | CRLF |
| `tests/unit/test_tts_phase_guard.py` | new | 293 | CRLF |
| `tests/integration/test_tts_phase_guard_load.py` | new | 194 | CRLF |
| `docs/build-plan/03-service-layer.md` | modify (script) | +24 / -0 | CRLF, kept |
| `docs/build-plan/build-priority-matrix.md` | modify (script) | +1 / -0 | CRLF, kept |
| `.agent/context/meu-status.yaml` | modify (script, tool) | +29 / -4 | LF, kept |
| `.agent/context/meu-registry.md` | regenerate | +1 / -0 | LF |
| `docs/BUILD_PLAN.md` | regenerate | +3 / -3 | LF |
| `.agent/context/known-issues.yaml` | modify (script) | +5 / -4 | LF, kept |
| `.agent/context/known-issues.md` | regenerate | +3 / -4 | LF |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | modify (script) | +1 / -1 (`:162`) | LF, kept |

The plan folder `docs/execution/plans/2026-11-17-tts-fp16-guard-ship/` is new (the plan, `task.md`, the row-0 data and the plan-local scripts). Nothing is committed or staged.

**`adapter.py`** (the whole diff): `:38` adds `from avkit_infra.tts.phase_guard import guarded_model`; `:401` adds `model = guarded_model(path, variant.id)`; `:404` and `:416` pass `model` in place of `str(path)` to the CUDA and the CPU `InferenceSession`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Verdict

**approved** at round 1 of 6, 0 findings, intent achieved: yes (`.agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-implementation-critical-review.md`, `agent: codex-independent-reviewer`, loop `ff-execution-2026-11-17-tts-fp16-guard-ship`). The reviewer's own `identity.py --state-only` gave the gate's `tested_state` `174bafa8a9ff327d38e54bd36f3edcb0e0b62085+8afc8a7a04434687c654454239b91bef722d1ce387854ee7b8fa52ef27bfce73`. The ledger recorded `round 1 verdict=approved agent='codex-independent-reviewer' blocking=0 intent_achieved=yes` and `loop may close: approved with no blocking findings.`; H1-7a: `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`; H1-7b: `OK: approved at round 1 of 6, 0 open blocking findings`.

- **What the review checked on its own.** A 5378-input adversarial probe of the splice (all 375 prefixes of the synthetic source, 5000 random byte strings and three hostile length and varint cases) gave 5377 `SpliceError` refusals and no hang or other error; the one accepted prefix is a complete graph that `GUARD_GATE`'s size and hash exclude. It also probed the gate's no-stat, read-error, splice-error and unknown-hash paths, rechecked every saved WAV hash pair by job (137, 149 and 149 equal), and found the 594 skip hashes, the pins and the Red-time test hashes unchanged.
- **Residual limits it names, all within the approved scope.** The guard is for the one pinned file; the real-runtime proof is CPU only, with CUDA routing proved by the recording fake (AC-144.9); and the packaged proofs are this session's saved runs, not a reviewer rerun.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A preselection change for FP16 | out-of-scope | — | D-330, D-331; D-1136 A leaves it a separate question for Mat |
| Keeping the generator in FP32 | out-of-scope | — | D-1136 |
| Posting anything to Hugging Face | out-of-scope | — | D-336, D-797 |
| Redacting the raw home prefix in the 24 tracked files and the two `known-issues.yaml` hits | out-of-scope | — | Its own docs-only change after Session 74 lands; carried in the H2-6 prompt |
| A CUDA hardware proof | out-of-scope | — | No CUDA device on this host; `BOTH_SESSIONS` is proved with a fake (AC-144.9) |
| Asserting the `tts.phase_guard` event in the packaged backend's log | out-of-scope | — | Rows 7 and 8 prove the packaged graph; the event is pinned in unit tests (AC-144.7) |
| Caching the guarded bytes across loads | out-of-scope | — | `NO_FILE_WRITE`; a load costs about 0.6 s (`wall_seconds` 0.571, `ff-guard-check.json`) |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **The plan's sha256 moved three times since the plan review.** The review read `f7cca9f396c1…`; the coordinator's approval edit to the Status line moved it to `a87b5cc2…`; D-1140 and D-1141, appended to the end of the plan's `decision_log` at execution, moved it to `64423a5f1fe530c70132ee3b458bb458918ff3d120eb0ac3c464562fb2b41514`, the plan the execution review read; D-1142, appended after the execution review at H2-2, moved it to `d4e0f975bf3e405fec614f1dfc9acca7d254b492ffc04c640125f5e6b22ba22e`. No other plan line changed. The plan and `task.md` are outside `identity.py`'s inputs, so `tested_state` did not move.
- **D-1140 (the sibling sessions' paths).** Sessions 91 to 94 were planned beside this session, and their plan folders (`e2e-pointer-flakes`, `mcp-audit-refresh`, `ui-small-fixes`, `video-tail-frame`) and plan-critical-review handoffs appeared while it ran. They are foreign: recorded in `baseline-dirty.txt`, never hashed, read or bound, skipped by `identity.py`'s `OTHER_PLAN` and `OTHER_HANDOFF` patterns and by the gate's `scope-paths` step, and left out of `commit-paths.txt`.
- **D-1141 (base ruff drift).** Row 0's first run failed at its base ruff step because `tests/integration/test_tts_models.py`, a read-only pin file, is not ruff-formatted at `174bafa` (25 files under `packages/` and `tests/` are not). `baseline.ps1` records the pin-file format drift as base and stays fatal on `ruff format --check` of `adapter.py` and on `ruff check` of all five; row 0 was rerun and passed. The first run's receipts are kept as `ff-run1-*`; its Python suite also had one failure in a video test that is not in this scope, and the rerun's suite passed (`3087 passed`).
- **Two plan-review notes.** (1) The pin fake's patch target is exactly `avkit_infra.tts.adapter.InferenceSession` (`tests/integration/test_tts_device_resolution.py:126`). (2) The plan's "the backend is never killed" is not exact: `Backend.stop()` in the smoke terminates its own child, with a kill fallback after 20 s (`tools/smoke_packaged_tts.py:162-169`, called at `:730`). The session prompt allows this; every backend stopped was the smoke's own child.
- **Moved and stale citations (Session 51 RULE-3).** Row 0 found no anchor moved (`moved anchors 0`, `ff-baseline.txt`). Two citations outside the plan are stale: 03's Session 52 Delivered note cites `PRESELECT_ORDER` at `tts-controls.ts:108`, which is now `:157` (this session does not edit that note); and the session prompt's `--phase online` build flag is not taken by `tools/package_backend.py`, which takes only `--stub-ok`, so the builds ran as Session 73's row 1 ran them.
- **`uv sync` dropped.** Row 0 ran no `uv sync`, so the shared environment was not re-synced while other sessions use it; the gate's `py-tests` runs `uv run --no-sync pytest tests/ -x --tb=short -q`.
- **Row 0's other notes.** The Session 73 smoke receipts were bound by hash at row 0; the `meu-status` `source` key is written as a note (`ff-register-get.txt`); the 03 insertion point came from the plan's line references and was checked by anchor; "all clean at plan time" covered only the two state files (`metrics.md`, `current-focus.md`) bound by content.
- **`guard-check.py --selftest`.** Added beyond the cell, and run before first use (`ff-guard-check-selftest.txt`); the gate's `guard-check` step writes `ff-D6-guard-check.json` so row 6's receipt is not overwritten.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file (an environment header with `RECEIPTS_DIR`, `TMP`, `TEMP` and `PYTHONDONTWRITEBYTECODE`, then the cell) and run with `pwsh -NoProfile -File`. Before H1-2 an extra host-load probe ran (`ff-host-load-h12pre.txt`: 33.4 %); the gate's own `host-load` step is the one recorded.
- **The build output.** Rows 2 and 7 rebuilt the shared, git-ignored `packaging/dist/avkit-backend`, as the plan names; each build was copied out at once.
- **Grouping row 74.** Row 9's cell names no command for the grouping line, so a scratch script replaced exactly the row-0 line with the plan's line (`implementation-plan.md:150`), keeping LF, after checking the file still equalled its row-0 copy; `ff-row9-check.txt` then found `grouping lines changed: [162]`.
- **The gate's `canon-vitest`** runs from `ui` inside the gate (`Push-Location`), with the cell's two test files.
- **D-1142 (the next session).** After the execution review the coordinator relayed that Session 91's plan review hit a review-ledger mechanism stop that needs Mat, so the queue runs Session 92 (`mcp-audit-refresh`), then 93, 94 and 91 last. H2-6's row text and check in `task.md` now accept a prompt starting `Start Session 92` that names `mcp-audit-refresh` and Session 91, in place of `Start Session 91`; its other checks are kept. This crosses grouping §2's soft order (Session 94 after Session 91's commit, for the shared `ui/tests/e2e/`), and the prompt says so.
- **Execution decisions** D-1140, D-1141 and D-1142 are in the plan's `decision_log`, each `resolution: autonomous`, `class: two-way`, `mandatory: none` (no M item hit); D-1137 to D-1139 are the plan's and D-1135 and D-1136 are Mat's. So the Decision Log below is `None.`.

### Execution notes

- **Processes.** Each smoke stopped only its own backend child. No process was stopped by name or path; other sessions' Electron and Python processes, and Mat's app, were left running.
- **Host load.** Every Red, build, smoke, full suite and the gate ran after the host-load wait at 50 %: rows 2 (25.4 %), 3 (17 %), 4 (22.2 %), 7 (18.4 %), 8 (25.4 %) and the gate (29 %).
- **User data.** Only Session 73's copies were read; the real models folder and app data were not touched, and nothing was downloaded.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
| Validated | 2026-11-18 | codex (H1-7 execution review) | Approved at round 1 of 6, 0 findings; the Codex Validation Report filled from it |
