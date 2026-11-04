---
date: "2026-10-26"
project: "tts-sideload-load"
meu: "MEU-98"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md"
build_plan_section: "bp03s3.11"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-10-26-gui-keyboard-palette-MEU-97-handoff.md"
---

# Handoff: 2026-10-26-tts-sideload-load-MEU-98-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-98, `svc-tts-sideload-load`. A sideloaded model file is recorded with its path, so a variant listed as downloaded can be loaded. Every load failure logs `tts.load_failed`. Rider `TTS-SPACY-SYSPATH-STALE-DIR`: a `tts.models_directory` change swaps the spaCy `sys.path` entry. The session also includes the eSpeak evidence stage for `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`.
**Build Plan Section**: [03 §TTS sideload load (residual)](../../../docs/build-plan/03-service-layer.md#tts-sideload-load-residual).
**Predecessor**: [MEU-97 handoff](2026-10-26-gui-keyboard-palette-MEU-97-handoff.md) (Session 41, the grouping's previous session).

Before this MEU, `list_available()` overlaid the sideload scan of `tts.models_directory`, so a dropped file showed as downloaded. The scan never persisted its path, though, so `load()` passed the adapter a variant with `path None`, and the 422 had no `tts.load_failed` line (`MODEL-SIDELOAD-LOAD-500`). Separately, `activate_spacy_dir` only ever appended, so after a `tts.models_directory` change the old install dir stayed importable and the Dependencies card kept reading `ready`.

- **`SIDELOAD_RECORD` / `RECORD_RULE`** (`services/models.py`). `list_available()` and `load()` record each scanned file whose id has a catalog row (`mark_downloaded(id, path)`) inside their unit of work, before they read the catalog. A row already downloaded at that path is not written. A scanned id with no row stays display-only. There is one `uow.commit()`, and only if something was written. The scan is the port's job: core touches no files.
- **`LOAD_FAILURE_PATHS` / `LOG_CAUSE`** (`tts/adapter.py`). These branches now log one `tts.load_failed` before they raise:
  - a missing or unreadable weight file (device `"cpu"`);
  - `torch is None`;
  - the kokoro `ImportError`;
  - the defensive unsupported-format branch (the resolved target).

  When a `ModelLoadError` has a cause, the log records the cause's type. Exception types and messages are unchanged.
- **`SPACY_PATH_SWAP`** (`tts/assets.py`). `activate_spacy_dir` tracks the entries it appended (a module set guarded by a lock). It removes tracked entries that are no longer current, appends the current ones, and calls `importlib.invalidate_caches()` only when `sys.path` changed. It only ever appends (AC-73.12), and it never touches an entry it did not append.
- **`ESPEAK_STAGE`**. The production probe reports eSpeak NG absent, so row 10 is `[B]` (b), and `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` stays open with a fresh `verification`.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-26-tts-sideload-load/implementation-plan.md). **Execution authorization:** Mat's message "@.agent/workflows/execution-session.md  Session 42 as per session grouping" (2026-10-27), sent after plan review r2 `approved` (`plan_to_exec_gate: human`; [walkthrough.md](../../../docs/execution/plans/2026-10-26-tts-sideload-load/walkthrough.md) §Execution message).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-98.1 | unit | `SIDELOAD_RECORD` on list: a scanned `kokoro-pt-fp32` row is recorded downloaded at the scanned path with one commit; a scanned `side` id with no row is listed and never recorded; core does no file I/O | 03 "Mark downloaded", "Record on scan"; D-125 | `tests/unit/test_services.py::test_ac_98_1_list_available_records_sideload`, `::test_ac_98_1_core_does_no_file_io` | ✅ |
| AC-98.2 | unit | `SIDELOAD_RECORD` on load: the port receives the scanned path; a `side`-only id is 404; the vocab 409 is unchanged; a legacy row with a current scanned file loads, without one it still conflicts | 03 "Load resolves" | `test_services.py::test_ac_98_2_load_records_and_passes_path`, `::test_ac_98_2_side_only_id_is_not_found`, `::test_ac_98_2_vocab_conflict_unchanged`, `::test_ac_98_2_legacy_row_with_new_file_loads`, `::test_ac_98_2_legacy_row_without_file_still_conflicts` | ✅ |
| AC-98.3 | unit | `RECORD_RULE`: a changed path is re-recorded with one commit; the same path is not written | `RECORD_RULE` | `test_services.py::test_ac_98_3_changed_path_rerecorded`, `::test_ac_98_3_same_path_not_written` | ✅ |
| AC-98.4 | integration | A missing weight file (`path=None` and a nonexistent file) raises `ModelLoadError("model weight file is missing")` and logs one `tts.load_failed` (`cpu`, `FileNotFoundError`); no engine constructed | 03 "Logged failure" | `tests/integration/test_tts_device_resolution.py::test_ac_98_4_missing_weight_logs_load_failed[path_none\|no_file]` | ✅ |
| AC-98.5 | integration | `torch` absent, kokoro `ImportError` and the unsupported format each log one event with the resolved target; a successful load logs none; TA-1: the unreadable file logs `PermissionError` | 03 "Logged failure"; `LOG_CAUSE` | `test_tts_device_resolution.py::test_ac_98_5_torch_absent_logs`, `::test_ac_98_5_kokoro_import_logs`, `::test_ac_98_5_unsupported_format_logs`, `::test_ac_98_5_success_logs_none`, `::test_ac_75_9_unreadable_weight_file_is_model_load_error_neg` (TA-1) | ✅ |
| AC-98.6 | integration | Contract: a dropped ONNX file is listed by `GET /api/v1/models/downloaded`, `POST /api/v1/models/load` answers 200 from that file and the row is recorded with its size; deleted later, the load is the 422 with one `tts.load_failed` | 03 "Tests" | `tests/integration/test_tts_assets.py::test_ac_98_6_sideload_contract_list_then_load` | ✅ |
| AC-98.7 | integration | Invariant: `set(CATALOG_METADATA) == {v[0] for v in SEED_VARIANTS}` (guard; passes at Red) | `SIDELOAD_RECORD` | `tests/integration/test_tts_models.py::test_ac_98_7_catalog_metadata_matches_seed` | ✅ |
| AC-98.8 | integration | `SPACY_PATH_SWAP`: A → B leaves B's entry last and A's gone; C (no install) leaves neither and `spacy_ready(C)` is False; a repeat changes nothing; untracked entries survive | 03 "spaCy directory change"; D-128 | `test_tts_assets.py::test_ac_98_8_activate_swaps_tracked_entry`, `::test_ac_98_8_untracked_entry_survives` | ✅ |
| AC-98.9 | integration | Through `CONTRACT_STACK`: `ready` → `models_directory` change → `missing` (A's dir out of `sys.path`) → back → `ready` | known-issue blast radius | `test_tts_assets.py::test_ac_98_9_models_directory_change_reports_spacy_missing` | ✅ |
| AC-98.10 | manual | `ESPEAK_STAGE`: the row 10 probe and either the blocked (b) block or Mat's AC-74.11 outcome | grouping D-100 | row 10 probe; [task.md §B-10](../../../docs/execution/plans/2026-10-26-tts-sideload-load/task.md) | ✅ outcome (b): eSpeak NG absent, row 10 blocked (b) with B-10; follow-up `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` |
| AC-9 (cross-ref) | regression | AC-9.8: the model manager holds no unit of work; the write is core's (D-123). AC-9.10: the sideload scan is unchanged | `SIDELOAD_RECORD` | `test_tts_models.py::test_ac_9_8_download_hf_map_returns_path_no_uow`, `::test_ac_9_10_sideload_catalog_metadata_and_stat` (gate `py-tests`) | ✅ |
| AC-12 (cross-ref) | regression | AC-12.8: a sideload-only id is still listed, and core still imports no `torch` or `avkit_infra` | `RECORD_RULE` | `test_services.py::test_ac_12_8_list_load_no_torch`, `::test_ac_12_8_no_direct_mkdir_in_services` (gate `py-tests`) | ✅ |
| AC-73 (cross-ref) | regression | AC-73.12: activation appends, never inserts; AC-73.9/73.16: the legacy dir skip and post-download path need no write | `SPACY_PATH_SWAP` | `test_tts_assets.py::test_ac_73_12_activation_appends_the_install_dir`; `tests/integration/test_tts_voice_packs.py` (gate `py-tests`) | ✅ |
| AC-74 (cross-ref) | regression / manual | AC-74.3 and AC-74.4 stay green with the fake runner; AC-74.11 (live eSpeak) stays unrun: row 10 is blocked (b), see AC-98.10 | `ESPEAK_STAGE` | `tests/e2e/test_api_tts_runtime.py` (gate `py-tests`); AC-98.10 above | ✅ (AC-74.11 open under `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`) |
| AC-75 (cross-ref) | regression | AC-75.9: the already-logged branches still log exactly one event, and the 422 mapping is unchanged | `LOAD_FAILURE_PATHS` | `test_tts_device_resolution.py` AC-75.9 tests; `tests/e2e/test_api_error_surface.py::test_ac_75_9_model_load_error_maps_to_422` (gate `py-tests`) | ✅ |
| AC-24, AC-25 (cross-ref) | regression | Packaging tests in the gate's `py-tests`. AC-25.7 is the one baseline failure the baseline rule excuses (`PACKAGING-MCP-SNIPPET-TOKEN-STALE`); AC-24.10 and AC-25.10 passed | §Verification Plan baseline rule | `session-gate.ps1` `py-tests` | baseline rule |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-98.1 | `assert (False, None) == (True, …/kokoro.pth)` (the row was never recorded) | pass | `tests/unit/test_services.py:2257` |
| AC-98.2 | the fake port received `path None` | pass | `test_services.py:2297` |
| AC-98.2 legacy | `ConflictError('… needs a re-download (v0.19 file)') is None` | pass | `test_services.py:2345` |
| AC-98.3 | the row kept the managed path | pass | `test_services.py:2385` |
| AC-98.4 (2 params), AC-98.5 (3), AC-98.6, TA-1 | `AssertionError: []` against the one expected `tts.load_failed` tuple (7 failures) | pass | `test_tts_device_resolution.py:809-877`, `:657`; `test_tts_assets.py:990` |
| AC-98.8 | `assert '…\a\spacy\en_core_web_sm-3.8.0' not in [...]` (the old dir stayed) | pass | `test_tts_assets.py:1043` |
| AC-98.9 | `assert 'ready' == 'missing'` | pass | `test_tts_assets.py:1084` |

Tests that passed at Red by design: AC-98.7 (a guard), `test_ac_98_5_success_logs_none`, `test_ac_98_8_untracked_entry_survives`, and the AC-98.1/98.2/98.3 negatives. Receipts: [walkthrough.md](../../../docs/execution/plans/2026-10-26-tts-sideload-load/walkthrough.md) §Sideload record Red/Green (rows 2–3), §Load failures Red/Green (rows 4–5), §spaCy swap Red/Green (rows 6–7), §Gate (row 8), §Hub (row 9), §eSpeak (row 10).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s42-sl-red","command":"pwsh -NoProfile -File row-2.ps1 (task.md row 2 Validation cell, verbatim, from P:/av-kit)","cwd":"P:/av-kit","scope":"SIDELOAD_RECORD Red: AC-98.1 to AC-98.3 and AC-98.7, red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD c34866b plus row 1 docs and the row 2 tests; packages/ unchanged since baseline.sha","output":"4 failed, 6 passed, 82 deselected; each failure an AssertionError | red-check: 1 receipt(s), 4 required test(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-sl-green","command":"pwsh -NoProfile -File row-3.ps1 (task.md row 3, verbatim)","cwd":"P:/av-kit","scope":"SIDELOAD_RECORD Green: seven targeted files, pyright, ruff","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD c34866b plus rows 1-2 and the services/models.py change","output":"152 passed, 1 warning | pyright 0 errors, 0 warnings, 0 informations | ruff All checks passed!","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-lf-red","command":"pwsh -NoProfile -File row-4.ps1 (task.md row 4, verbatim)","cwd":"P:/av-kit","scope":"LOAD_FAILURE_PATHS Red: AC-98.4 to AC-98.6 and TA-1, red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD c34866b plus rows 1-3 and the row 4 tests; tts/adapter.py and tts/assets.py unchanged since baseline.sha","output":"7 failed, 1 passed, 47 deselected; every failure AssertionError: [] | red-check: 1 receipt(s), 6 required test(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-lf-green","command":"pwsh -NoProfile -File row-5.ps1 (task.md row 5, verbatim)","cwd":"P:/av-kit","scope":"LOAD_FAILURE_PATHS Green: six targeted files, pyright, ruff","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD c34866b plus rows 1-4 and the tts/adapter.py change","output":"100 passed, 1 warning | pyright 0 errors, 0 warnings, 0 informations | ruff All checks passed!","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-sp-red","command":"pwsh -NoProfile -File row-6.ps1 (task.md row 6, verbatim)","cwd":"P:/av-kit","scope":"SPACY_PATH_SWAP Red: AC-98.8 and AC-98.9, red-check","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD c34866b plus rows 1-5 and the row 6 tests; tts/assets.py unchanged since baseline.sha","output":"2 failed, 1 passed, 25 deselected: AC-98.8 old dir still in sys.path, AC-98.9 assert 'ready' == 'missing' | red-check: 1 receipt(s), 2 required test(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-sp-green","command":"pwsh -NoProfile -File row-7.ps1 (task.md row 7, verbatim)","cwd":"P:/av-kit","scope":"SPACY_PATH_SWAP Green: test_tts_assets.py, test_tts_voice_packs.py, test_tts_models.py, pyright, ruff","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD c34866b plus rows 1-6 and the tts/assets.py change","output":"54 passed, 1 warning | pyright 0 errors, 0 warnings, 0 informations | ruff All checks passed!","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-espeak-probe","command":"uv run python -c \"import sys; from avkit_infra.tts.espeak import EspeakCliAdapter; s=EspeakCliAdapter().status(); print('espeak-ng:', s.path or '<absent>', 'version:', s.version or '-'); sys.exit(0 if s.available else 3)\"","cwd":"P:/av-kit","scope":"ESPEAK_STAGE (row 10, AC-98.10): production eSpeak NG detection","phase":"targeted","exit_code":3,"result":"blocked","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29","output":"espeak-ng: <absent> version: -","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-gate-h1-2","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-26-tts-sideload-load/session-gate.ps1 *> C:/Temp/av-kit/s42-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s42-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','baseline'; exit $code","cwd":"P:/av-kit","scope":"H1-2 fresh full session gate after row 9 (INPUT_IDENTITY): identity, py-types, py-lint, task-contract, scope-paths, py-tests, openapi, state-render, state-canon, identity","phase":"full","exit_code":0,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29","output":"identity-before exit=0 | py-types, py-lint, task-contract exit=0 | scope-paths exit=0: changed paths: 16 outside scope: [] | py-tests exit=1: 1 failed, 956 passed, 1 warning; baseline rule: failed=1 outside_baseline=[] errors=0; every failure is in the row 0 baseline failed set; not a regression | openapi, state-render, state-canon exit=0 | identity-after exit=0 | uv_lock_sha256 5285fac845036947c7e7e8f18420b3278cac7c04a7c10892655c3f992ec5fff6 | tested_state before=c34866b116405dcbc2c70e482b5b376e017d5784+bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29 after=c34866b116405dcbc2c70e482b5b376e017d5784+bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-h1-3-render","command":"rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s42-drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s42-drift-check.txt; exit $code","cwd":"P:/av-kit","scope":"H1-3 SSOT render check after row 9's status writes","phase":"static","exit_code":0,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29","output":"Drift check passed — SSOT loaded (98 MEUs, 12 phases), rendered regions match on-disk content","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s42-h1-4-openapi","command":"task.md row H1-4 Validation cell, verbatim (committed openapi.committed.json schemas against baseline.sha)","cwd":"P:/av-kit","scope":"H1-4 OpenAPI: no schema added, removed or changed","phase":"static","exit_code":0,"result":"pass","tested_state":"c34866b116405dcbc2c70e482b5b376e017d5784+bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29","output":"added: [] removed: [] changed: [] | H1-2 openapi stage=full exit=0","fresh":true}
```

### Quality Gate Results

The H1-2 fresh gate is the session's full record. Row 9 changed bound inputs after row 8 (the 03 note, `meu-status.yaml` and the rendered `BUILD_PLAN.md`), so the record is H1-2, not row 8 (`INPUT_IDENTITY`).

- Every step exited 0 except `py-tests`, which exited 1 as the plan's baseline rule allows. Its one failure is in the baseline set: `test_mcp_snippet_keys[AC-25.7]`, `outside_baseline=[]`.
- `py-tests`: `1 failed, 956 passed`; the baseline was `1 failed, 936 passed`, and this session adds 20 test cases.
- pyright: 0 errors, 0 warnings, 0 informations. ruff: all checks passed.
- `scope-paths`: 16 changed paths, none outside scope.
- `state-render`: drift check passed. `state-canon` (the two Vitest canon suites): exit 0.
- Identity: `tested_state` `c34866b116405dcbc2c70e482b5b376e017d5784+bd4e38d544c2659a719a44abf88831db23b2cfea1396173ff26d5cb7cf8e2c29` was the same before and after.
- Row 8 also passed whole on the pre-row-9 tree (state `…+3319f4ec…`) and is kept as prose.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/models.py` | modified | `_record_sideload` (`SIDELOAD_RECORD`, `RECORD_RULE`), called from `list_available` and `load` |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | `LOG_CAUSE` in `_log_load_failed`; the four `LOAD_FAILURE_PATHS` branches log |
| `packages/infrastructure/src/avkit_infra/tts/assets.py` | modified | `SPACY_PATH_SWAP`: `_ACTIVE_SPACY_ENTRIES`, `_ACTIVE_SPACY_LOCK`, the swap in `activate_spacy_dir` |
| `tests/unit/test_services.py` | modified | AC-98.1 to AC-98.3 |
| `tests/integration/test_tts_device_resolution.py` | modified | AC-98.4, AC-98.5; TA-1 |
| `tests/integration/test_tts_assets.py` | modified | AC-98.6, AC-98.8, AC-98.9 |
| `tests/integration/test_tts_models.py` | modified | AC-98.7 |
| `docs/build-plan/03-service-layer.md` | modified | rows Record on scan and spaCy directory change; the Session 42 Delivered note |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | modified | MEU-98 `ready_for_review` (tool-written, rendered) |
| `.agent/context/known-issues.yaml` | modified | `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` `verification` refreshed |
| `.agent/context/current-focus.md` | modified | Session 42 |
| `docs/execution/plans/2026-10-26-tts-sideload-load/` (`task.md`, `implementation-plan.md`, `walkthrough.md`, `baseline.sha`) | modified/new | row states, B-10, ECN-1 to ECN-3, receipts |

```diff
+    def _record_sideload(self, uow: UnitOfWork, models_dir: Path) -> None:
+        wrote = False
+        for scanned in self._catalog.sideload(models_dir):
+            row = uow.models.get(scanned.id)
+            if row is None or scanned.path is None:
+                continue
+            if row.is_downloaded and row.path == scanned.path:
+                continue
+            uow.models.mark_downloaded(scanned.id, scanned.path)
+            wrote = True
+        if wrote:
+            uow.commit()
```

```diff
 def _log_load_failed(variant: ModelVariant, device: str, exc: BaseException) -> None:
-    log.error("tts.load_failed", variant_id=variant.id, device=device, error=type(exc).__name__)
+    cause = exc.__cause__ if isinstance(exc, ModelLoadError) else None
+    error = type(cause if cause is not None else exc).__name__
+    log.error("tts.load_failed", variant_id=variant.id, device=device, error=error)
```

```diff
+    with _ACTIVE_SPACY_LOCK:
+        for entry in sorted(_ACTIVE_SPACY_ENTRIES - set(current)):
+            _ACTIVE_SPACY_ENTRIES.discard(entry)
+            if entry in sys.path:
+                sys.path.remove(entry)
+                changed = True
+        for entry in current:
+            if entry not in sys.path:
+                sys.path.append(entry)
+                _ACTIVE_SPACY_ENTRIES.add(entry)
+                changed = True
+        if changed:
+            importlib.invalidate_caches()
```

---

## Codex Validation Report

Pending: the H1-7 Codex execution review. The verdict is recorded in `2026-10-26-tts-sideload-load-implementation-critical-review.md`.

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

_pending: H1-7 Codex execution review_

---

## Deferred Items

AC-98.10 is the row 10 evidence stage, not deferred implementation. It is `[B]` (b), missing dependency: [B-10](../../../docs/execution/plans/2026-10-26-tts-sideload-load/task.md), follow-up [TTS-ESPEAK-LIVE-PATH-UNVERIFIED](../known-issues.yaml). The AC-74.11 live run waits for Mat to install eSpeak NG 1.52. That is the issue's own open follow-up for the approved MEU-74, not a new deferral (grouping D-100).

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| AC-74.11 live eSpeak run | blocked (missing dependency) | MEU-74 (approved; MEU-EXPAND issue) | [TTS-ESPEAK-LIVE-PATH-UNVERIFIED](../known-issues.yaml) |

---

## Decision Log

```yaml
decision_log:
  - id: D-132
    stage: execution
    question: "Row 0 at d30f62b found four test_framework_adoption.py failures: the 2026-09-26 rule map pins AGENTS.md's sha256, and bb481ec's no-branches paragraph changed it. Update the pin, or carry the four as baseline failures?"
    resolution: human
    class: governance-value
    chosen: "Update the pin (counts.\"AGENTS.md\".postimage_sha256), commit and push it alone (c34866b), and re-run row 0 there (ECN-1)"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-09-30-tts-repair A-2 - the same rule-map pin carve-out", "walkthrough.md Baseline - the first row 0 run and its cause"]
    research: { engine: none, sources: [] }
    reasoning: "Mat chose 'Update pin, commit+push (Recommended)' on 2026-10-27. The AGENTS.md change was a deliberate user-directed rule. Carrying four governance failures as baseline would have hidden any later rule-map drift for this session."
  - id: D-133
    stage: execution
    question: "The plan puts row 10's ### B-10 evidence.v1 block in walkthrough.md, but the blocked-row predicate (lint_task_contract.py and durable_evidence.blocked_evidence_problems) reads task.md. Where does the block go?"
    resolution: autonomous
    class: two-way
    chosen: "In task.md, with the row citing B-10 and the follow-up link; walkthrough.md section eSpeak mirrors the outcome (ECN-2)"
    source_tag: Local Canon
    precedents: [".agent/docs/output-evidence-policy.md Blocked rows - the task linter and closeout validator share this predicate", "docs/execution/plans/2026-09-28-p11-capture-settings/task.md - its ### B-H1-6 block lives in task.md"]
    research: { engine: none, sources: [] }
    reasoning: "The [B] (b) outcome and its evidence are unchanged; only the file that holds the block moves, to the one the validator reads. Leaving it in walkthrough.md would fail the H2-4 task-contract check. Moving it back is a one-block edit."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-27 | claude-code-local (Claude Opus 5.5) | Initial MEU-98 handoff after H1-2 |
