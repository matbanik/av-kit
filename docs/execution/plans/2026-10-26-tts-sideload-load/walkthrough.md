# Walkthrough — 2026-10-26-tts-sideload-load (Session 42)

Durable observations for each task row. Raw receipts are under `C:/Temp/av-kit/s42-*.txt`.

## Execution message

- **User message (2026-10-27):** "@.agent/workflows/execution-session.md  Session 42 as per session grouping". This is the explicit execution message after plan review r2 `approved` (`plan_to_exec_gate: human`).
- **Tree:** `P:/av-kit` on `main`. HEAD was `d30f62b` (another session's MEU-95/96/97 commit, on top of this plan's `bb481ec`). That commit changes only `ui/`, the 2026-10-17 grouping and `meu-status.yaml` rows for MEU-95/96/97. It touches none of the product or test files this plan edits.
- **Peers:** Session 41, which asked for the test hold, is no longer running, and Session 40 is committed (`b6b288e`). The one live av-kit peer, `av-kit-9d`, confirmed that it has no uncommitted files and no run in progress. No process was running from `P:\av-kit\` before `npm ci`.
- **Context tool decision (execution):** this is re-evaluated by row 0's prerequisite check (no `graphify-out*/`). The `task.md` decision covers `planning_and_execution`, so `not_applicable` stands.

## Baseline

- **First row 0 run (HEAD `d30f62b`):** `prereq problems: []`; pytest `5 failed, 932 passed`. Four of the failures were `tests/tooling/test_framework_adoption.py` (`static_oracles[none]`, `routing_inventory[history]`, two `generic_class_census` ids), all `REFUSE: rule map identity mismatch: AGENTS.md`. The cause was this session's own `bb481ec` no-branches paragraph in AGENTS.md: the 2026-09-26 adoption rule map pins AGENTS.md's sha256, and the pre-edit CRLF bytes hash to the pinned `f4881dfe…`.
- **Human decision (2026-10-27, AskUserQuestion):** "Update pin, commit+push". Only `counts."AGENTS.md".postimage_sha256` in `docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md` changed, to `ac241949…`, following the 2026-09-30 tts-repair A-2 carve-out. `test_framework_adoption.py` then gave 91 passed (`C:/Temp/av-kit/s42-fa-fixed.txt`). This was committed alone as `c34866b` and pushed to `origin/main`.
- **Row 0 re-run (HEAD `c34866b`, `baseline.sha`):** exit 0; `prereq problems: []`.
  - `s42-base-py.txt`: `1 failed, 936 passed, 1 warning in 101.58s`. The failed set is `tests/unit/test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]`, an environmental packaging id the gate's baseline rule excuses.
  - `s42-base-canon.txt`: `Test Files 2 passed (2)`, `Tests 14 passed (14)`.

## Census

Receipt: `C:/Temp/av-kit/s42-census.txt` (the row 1 `CENSUS_PATTERNS` search over `tests` and `mcp-server/tests`). Every hit is covered by one of the groups below. No hit is `new-contradiction`.

| Hits | Disposition | Reason |
|------|-------------|--------|
| `tests/integration/test_tts_device_resolution.py:657` `test_ac_75_9_unreadable_weight_file_is_model_load_error_neg` | **TA-1** | The `_require_weight_path` failure now logs. The test gains `capture_logs` and asserts one `tts.load_failed` with `device == "cpu"` and `error == "PermissionError"` (the `__cause__`, `LOG_CAUSE`). |
| `test_tts_device_resolution.py:326, 605` (`== []`) | unaffected | Successful loads, which never log `tts.load_failed`. |
| `test_tts_device_resolution.py:345, 370, 388, 478, 636, 651, 744` (count `== 1` / failed lists) | unaffected | Each one drives a branch that already logs exactly once: the PyTorch retry/constructor/eval paths, the ONNX CPU session failure, the raising probe (`"cpu"`), the raising vocab resolver, and the engine-import `Exception` arm. `LOAD_FAILURE_PATHS` adds logs only to `_require_weight_path`, `torch is None`, the kokoro `ImportError` and the unsupported format. None of these tests reaches those branches (`:205` patches `torch` to `None` only for `runtime_devices`). The `error` field moves to the `__cause__` type only where a cause exists. These tests assert counts and causes, not the `error` string. |
| `test_tts_device_resolution.py:536, 709, 761` (`/models/load`) | unaffected | `FakeModels` subclasses call the adapter directly. No `ModelsService`, so no sideload record. |
| `tests/unit/test_services.py:133, 291, 300, 1630, 1660-1661` (fake `mark_downloaded`, `commits`, `sideload_rows`, `sideload`) | unaffected | Fake infrastructure that the new path calls through. No signature changes. |
| `test_services.py:1876-1881` `test_ac_12_8_list_load_no_torch` | unaffected | The scanned `side` has no repository row, so `RECORD_RULE` writes nothing: it stays display-only. `kokoro-pt-fp32` is not in `sideload_rows`. The source assertions (`torch`, `import avkit_infra` absent) still hold because core does no filesystem I/O. |
| `test_services.py:2007-2012` (`uow.commits == before + 1`) | unaffected | This counts commits around `on_download_progress`, not `list_available`/`load`. |
| `tests/unit/test_conversion_service.py:134, 146, 478, 483` | unaffected | The conversion fake UoW's commit counter. Not model code. |
| `tests/unit/test_uow_commit_log.py` | unaffected | Named explicitly (D-125 census). It asserts that a bare read-only `SqlAlchemyUnitOfWork` exit emits no `uow.commit` console line. It builds only `SettingsService`/`HealthService`, and `SIDELOAD_RECORD` commits only when `RECORD_RULE` wrote a row, so a read-only `list_available` still never commits. It matched no `CENSUS_PATTERNS` literal and is reviewed by name. |
| `tests/unit/test_domain.py:1180, 1431, 1434`; `tests/integration/test_tts_models.py:44`; `tests/integration/test_sqlite_uow.py:316, 989, 995, 998` | unaffected | Port method tuples and the `mark_downloaded` signature. `MARK_SIGNATURE` keeps both, and `list_downloaded` is still repository-only. |
| `test_sqlite_uow.py:822-840` (AC-5.13) | unaffected | Repository behaviour (size from file, missing path) is unchanged. |
| `test_tts_models.py:566` (`"mark_downloaded" not in source`) | unaffected | This asserts on the model manager's source, which this plan does not change. The write lives in `services/models.py`. |
| `test_tts_models.py:598-609` (AC-9.10 sideload metadata) | unaffected | The catalog adapter's `sideload` scan is unchanged. |
| `tests/integration/test_tts_voice_packs.py:205-345` | unaffected | AC-73.9: the scan still skips the legacy ONNX dir. The legacy int8 tests mark a legacy path that the scan never returns, so no record happens and the 409 holds. AC-73.16: after a download the scanned path equals the row path, so there is no write. `:241, 248` are the test's own `sys.path` copy. |
| `tests/integration/test_tts_assets.py:198` (`Stack.put_weights`) | unaffected | `put_weights` records the same path the scan returns, so `RECORD_RULE` makes no write. |
| `test_tts_assets.py:344, 364, 376, 506, 538, 587` (`/models/load` through the real `Stack`) | unaffected | Each load follows `put_weights` (path already recorded) or a deliberately missing file with no scan hit. The record step leaves rows as they are. |
| `test_tts_assets.py:108, 118-119` (`isolated_path`); `tests/conftest.py:23-33` (`_restore_import_path`) | unaffected | They restore `sys.path` after each test. `SPACY_PATH_SWAP` removes only tracked entries that are on `sys.path`, so stale tracked entries from earlier tests (already restored away) are skipped. |
| `test_tts_assets.py:724-749` (AC-62.14) | unaffected | Idempotence holds: a second call with the same directory changes nothing (`count == 1`). After the monkeypatch drops the install entry, the next activation finds it current and not on `sys.path`, and appends it once. |
| `test_tts_assets.py:755-767` (AC-73.12) | unaffected | The swap appends and never inserts, so `sys.path[-1] == install` and `sys.path[:-1] == before` hold. |
| `tests/e2e/api_fakes.py:360, 363`; `tests/e2e/test_api_tts_models.py:110-218`; `tests/e2e/test_api_bodies.py:40`; `tests/e2e/test_api_error_surface.py:268`; `tests/e2e/test_api_openapi.py:76, 78` | unaffected | The e2e suite uses `FakeModels`, not `ModelsService`. Routes and OpenAPI are unchanged. |
| `mcp-server/tests/fixtures.ts:51, 54` | unaffected | The MCP route list. No route changes. |

Row 1 run: exit 0. `census hits: 96` is 95 search hits plus the `[rtk] No hook installed` banner line that `rtk proxy` writes into the receipt (a sorted diff against the preview shows only that line). `s42-canon.txt`: `canon problems: []`. 03 §TTS sideload load: the "Mark downloaded" row now reads `mark_downloaded(id, path)` and says the repository records the file size. New rows **Record on scan** and **spaCy directory change** are added. The "Tests" row adds the spaCy swap.

## Sideload record Red

- `RED_TREE`: the row 2 guard found no `packages/` change since `baseline.sha` (`c34866b`).
- Tests added: `tests/unit/test_services.py` (AC-98.1–98.3: `test_ac_98_1_list_available_records_sideload`, `test_ac_98_1_core_does_no_file_io`, `test_ac_98_2_load_records_and_passes_path`, `test_ac_98_2_side_only_id_is_not_found`, `test_ac_98_2_vocab_conflict_unchanged`, `test_ac_98_2_legacy_row_with_new_file_loads`, `test_ac_98_2_legacy_row_without_file_still_conflicts`, `test_ac_98_3_changed_path_rerecorded`, `test_ac_98_3_same_path_not_written`) and `tests/integration/test_tts_models.py` (`test_ac_98_7_catalog_metadata_matches_seed`). `_record_marks` wraps the fake repository's `mark_downloaded` to count writes. `side` is never seeded, so a write for it would raise `KeyError` in `FakeModelRepo`. The legacy-409 test catches only `ConflictError` around the call, then asserts.
- `s42-sl-red.txt`: `4 failed, 6 passed, 82 deselected` (exit code in `.exit`). The four required tests fail by assertion:
  - AC-98.1: `(False, None) == (True, …/kokoro.pth)` (the row was never recorded).
  - AC-98.2: the port received `path None`.
  - AC-98.2 legacy: `ConflictError('… needs a re-download (v0.19 file)') is None`.
  - AC-98.3: the row kept the managed path.
- `s42-sl-red-check.txt`: `red-check: 1 receipt(s), 4 required test(s), 0 problem(s)`.

## Sideload record Green

- `services/models.py`:
  - `_record_sideload(uow, models_dir) -> None` scans once. For each scanned row with a repository row, it calls `mark_downloaded(id, scanned.path)` unless the row is already downloaded at that path (`RECORD_RULE`). It makes one `uow.commit()` if it wrote anything.
  - `list_available` calls it inside its unit of work, before `list_catalog()`. The scan overlay that follows is unchanged, so a display-only id is still listed.
  - `load` calls it before `uow.models.get`. `models_directory(...)` is now read before the unit of work opens in both methods, so no settings read nests inside the open session.
  - No filesystem calls and no `avkit_infra` import (`test_ac_98_1_core_does_no_file_io`). The repository's existing `model.marked_downloaded` info line logs each write.
- `s42-sl-green.txt`: `152 passed, 1 warning` (Starlette `httpx` deprecation) over the seven targeted files.
- `s42-sl-types.txt`: `0 errors, 0 warnings, 0 informations`.
- `s42-sl-lint.txt`: `All checks passed!`.

## Load failures Red

- `RED_TREE`: the row 4 guard found `tts/adapter.py` and `tts/assets.py` unchanged since `baseline.sha`. The tree already carries the row 3 `services/models.py` edit, as planned: AC-98.6 reaches its first 200 and then fails on the log count.
- Tests added:
  - `tests/integration/test_tts_device_resolution.py`:
    - `test_ac_98_4_missing_weight_logs_load_failed[path_none|no_file]`
    - `test_ac_98_5_torch_absent_logs`, `test_ac_98_5_kokoro_import_logs` (both request CUDA on a `with_cuda` probe, so the event must carry the resolved target `cuda`)
    - `test_ac_98_5_unsupported_format_logs` (forces `format` on one frozen instance, because no constructible variant reaches the branch)
    - `test_ac_98_5_success_logs_none`
  - `tests/integration/test_tts_assets.py`: `test_ac_98_6_sideload_contract_list_then_load` (`CONTRACT_STACK`; the spaCy wheel is held and released in `finally`).
- **TA-1** in `test_ac_75_9_unreadable_weight_file_is_model_load_error_neg`: the existing `with pytest.raises(ModelLoadError) as raised:` gains `capture_logs() as logs,` in the same `with` statement (this file's idiom, and ruff SIM117 forbids nested `with`). Every other line stays. After the existing cause assertion it asserts `[(variant.id, "cpu", "PermissionError")]`.
- `s42-lf-red.txt`: `7 failed, 1 passed, 47 deselected`. Every failure is `AssertionError: []` against the one expected `tts.load_failed` tuple. `test_ac_98_5_success_logs_none` passes.
- `s42-lf-red-check.txt`: `red-check: 1 receipt(s), 6 required test(s), 0 problem(s)`.

## Load failures Green

- `tts/adapter.py`:
  - `_log_load_failed` applies `LOG_CAUSE`: a `ModelLoadError` with a `__cause__` logs the cause's type name, and anything else logs its own type. The branches that already logged pass raw failures (never a `ModelLoadError`), so their values are unchanged.
  - `load_model` wraps `_require_weight_path`: it logs device `"cpu"`, then re-raises the same error.
  - The unsupported-format branch builds the `ValidationError`, logs it with the resolved target, then raises it.
  - In `_load_pytorch`, `torch is None` logs the `ModelLoadError` it raises, and the kokoro `ImportError` logs the raw `ImportError`. Both use the resolved target.
  - Exception types and messages are unchanged. The docstring adds the `ValidationError` raise and the one-event rule.
- `s42-lf-green.txt`: `100 passed, 1 warning` over the six targeted files.
- `s42-lf-types.txt`: `0 errors, 0 warnings, 0 informations`.
- `s42-lf-lint.txt`: `All checks passed!`.

## spaCy swap Red

- `RED_TREE`: the row 6 guard found `tts/assets.py` unchanged since `baseline.sha`.
- Tests added to `tests/integration/test_tts_assets.py`:
  - `test_ac_98_8_activate_swaps_tracked_entry`: A → B → B (no change) → C (no install), then `spacy_ready(C) is False`.
  - `test_ac_98_8_untracked_entry_survives`: a foreign entry, plus A's dir appended before av-kit saw it, both survive A → B → C → A.
  - `test_ac_98_9_models_directory_change_reports_spacy_missing` (`CONTRACT_STACK`; ready → missing → ready, and A's dir leaves and re-enters `sys.path` once).
  - Each test resets `assets._ACTIVE_SPACY_ENTRIES` through `monkeypatch`. At Red that reset used `raising=False`. Once row 7 created the name, the reset was switched to the strict default (`raising=True`), so a renamed global fails the setup.
- `s42-sp-red.txt`: `2 failed, 1 passed, 25 deselected`.
  - AC-98.8: `assert '…\a\spacy\en_core_web_sm-3.8.0' not in [...]` (the old dir stayed).
  - AC-98.9: `assert 'ready' == 'missing'`.
  - `test_ac_98_8_untracked_entry_survives` passes, as planned.
- `s42-sp-red-check.txt`: `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`.

## spaCy swap Green

- `tts/assets.py`:
  - New module-level `_ACTIVE_SPACY_ENTRIES: set[str]` and `_ACTIVE_SPACY_LOCK = threading.Lock()`.
  - `activate_spacy_dir` computes the current install entries. Under the lock, it drops every tracked entry that is not current, removing it from `sys.path` when present. It then appends, and tracks, every current entry missing from `sys.path`, and calls `importlib.invalidate_caches()` only if it changed `sys.path`.
  - It only ever appends (AC-73.12). An entry it did not append is never removed or tracked.
- S4 check: AC-98.9 reads `missing` after the swap, so S4 does not apply.
- `s42-sp-green.txt`: `54 passed, 1 warning` (`test_tts_assets.py`, `test_tts_voice_packs.py`, `test_tts_models.py`).
- `s42-sp-types.txt`: `0 errors, 0 warnings, 0 informations`.
- `s42-sp-lint.txt`: `All checks passed!`.

## Gate

- `s42-gate.txt` (row 8, `session-gate.ps1`, exit 0). In stage order:
  - `identity-before`: exit 0.
  - `py-types`: exit 0.
  - `py-lint`: exit 0.
  - `task-contract`: exit 0.
  - `scope-paths`: exit 0, `changed paths: 11 outside scope: []`.
  - `py-tests`: exit 1, `1 failed, 956 passed, 1 warning`. Baseline rule: `failed=1 outside_baseline=[] errors=0`, so this is not a regression.
  - `openapi`: exit 0.
  - `state-render`: exit 0.
  - `state-canon`: exit 0.
  - `identity-after`: exit 0.
  - No `not_run`.
- Baseline failure, excused (receipt `s42-base-py.txt`, row 0): `tests/unit/test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]`.
- Identity:
  - `tested_state before=c34866b116405dcbc2c70e482b5b376e017d5784+3319f4ec73a16e2dc302e77d546155793dcb5c1a073dfce9d1b96c642163a923`
  - `after=` the same value.
  - `uv_lock_sha256 5285fac845036947c7e7e8f18420b3278cac7c04a7c10892655c3f992ec5fff6`

## Hub

- `03-service-layer.md`: a `> **Delivered (Session 42).**` note follows the §TTS sideload load table. It is one note covering `SIDELOAD_RECORD`/`RECORD_RULE`, `LOG_CAUSE`, `SPACY_PATH_SWAP` and AC-98.1 to AC-98.9, and the file stays CRLF.
- `tools/meu_status.py update MEU-98 ready_for_review --plan docs/execution/plans/2026-10-26-tts-sideload-load/` reports `Updated MEU-98 → ready_for_review (updated: 2026-10-27)`.
- `meu_status.py render` reports `98 MEUs across 12 phases`, `✅ All regions rendered successfully.` The `BUILD_PLAN.md` total reads `96 + 1🟡 + 1🚫`.
- `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md` remain `i/lf w/lf`, the tool's output format.
- Row 9 receipts:
  - `s42-hub-rg.txt` shows MEU-98 with `execution_plan`, and the 03 note at line 520.
  - `s42-hub-status.txt`: `hub problems: []`.
  - `s42-state-render.txt`: `✅ Drift check passed`.

## eSpeak

- Row 10 probe `s42-espeak.txt`: exit 3, `espeak-ng: <absent> version: -`. The probe is the production `EspeakCliAdapter().status()` (`PATH`, then the Program Files locations, then `--version`).
- Outcome (b), missing dependency: row 10 is `[B]` with the `### B-10` `evidence.v1` block in `task.md` (plan ECN-2). The follow-up is `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`.
- AC-74.11 was not run, and the session continues (grouping D-100).
- `known-issues.yaml` `TTS-ESPEAK-LIVE-PATH-UNVERIFIED.verification`: `last_checked: '2026-10-27'`, with `method` (the Session 42 row 10 probe) and `result` (absent, exit 3, AC-74.11 not run). The status stays `open`.
- Checks: `lint_task_contract.py` reports `OK: 27 row(s)` (`s42-b10-lint.txt`), and `durable_evidence.py task.md` reports `OK: durable evidence records` (`s42-b10-evidence.txt`).
