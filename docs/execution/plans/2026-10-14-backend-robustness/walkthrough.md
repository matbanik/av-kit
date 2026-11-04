# Session 33 walkthrough: backend-robustness

Plan: `implementation-plan.md` (approved in plan review round 4, `.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md`). Worktree `P:/av-kit-wt/backend-robustness`, branch `claude/s33-backend-robustness`.

## Execution authorization

> @.agent/workflows/execution-session.md  33 as per session grouping

Mat, 2026-10-15 (USER_EXPLICIT, direct chat message). It vetoes no TA and no decision, so TA-1 to TA-10 and D-8 to D-31 stand as approved. The MEU order is MEU-76, then MEU-78, then MEU-77.

The pre-row-0 decisions A-1 to A-3 below were answered by Mat on 2026-10-15 in the same session (USER_EXPLICIT, a direct answer to a question).

## Gate decisions

| ID | Trigger | Decision (Mat, 2026-10-15; A-12 on 2026-10-16) | Change |
|---|---|---|---|
| A-1 | S4. After planning, the branch was fast-forwarded from `7861020` to `c72fc44` (the Session 31 merge), and Mat's plan commit `ddd1117` sits on top. `7861020..HEAD` touches three Files Modified paths: `ui/src/renderer/src/features/settings/SettingsPage.tsx` (+31/−8), `ui/tests/e2e/settings.test.ts` (+217, appended) and `ui/tests/e2e/test-ids.ts` (+3, a MEU-70 block at the end). There are no local edits. `P:/av-kit` is on `main` at `c72fc44` with a clean tree. | Accept `c72fc44` as the planning head. No rebase. | `validate-task.ps1` `$planningHead` is now `c72fc4436da8534ef613264620b83c3e84e97631`. The `DEPS_CARD` cite `SettingsPage.tsx:1001-1019` is now `:1014-1032`; those 19 lines are byte-identical to the planning copy. `DependenciesOut` is still at `:65`. MEU-78's `DEPS_FFPROBE_ROW` block goes at the end of `test-ids.ts`, after the MEU-70 block. AC-78.9 is still appended to `settings.test.ts`. |
| A-2 | Context-tool gate re-check: `headroom.exe` is now on PATH (`C:/Users/Mat/AppData/Roaming/Python/Python313/Scripts`), and the prereq guard refused whenever it was. `graphify-out/` and `graphify-out-research/` are still absent. | `not_applicable` for the execution phase. The repo has no active approved Headroom disposition, the user-headroom MCP is not connected in this harness, and the payloads are source, test output and exact evidence (bypass classes). | An execution-phase `context_tool_decision` block was added to `task.md` and `implementation-plan.md`. The guard now refuses only when headroom is on PATH **and** `task.md` has no `phase: execution` record. |
| A-3 | The reviewer's pre-row-0 note: `validate-task.ps1:153` checked the plan review with `--cap 3`, but the approved review is round 4, which `review-check` rejects (round > cap). | Mat: "set cap to 6". | `--cap 6` at `validate-task.ps1` `prereq-plan-review`. S7 now reads "plan 6 since A-3". The ledger is untouched. |
| A-4 | The first `-Check prereq` failed at `prereq-uv-sync` with exit 2: spacy 3.8.15 has no `cp314` wheel. The worktree `.venv` had been created on 2026-10-14 at 22:31, during this session's planning, and uv chose CPython 3.14. `P:/av-kit/.venv` uses CPython 3.12.12. | Autonomous (obviousness test: environment only, no gate, test or plan change). Use the interpreter the main checkout uses. | `.venv` was recreated with `uv venv --python 3.12.12`, then `-Check prereq` was rerun. The failed attempt is in `s33-prereq-uv-sync.txt` (first run, overwritten by the rerun). |
| A-5 | S2, census N-1. Under `FFPROBE_RULE`, `test_ac_29_4_probe_fills_additive_media_info` (`tests/unit/test_ffmpeg_conversion.py`) and `test_ac_8_10_probe_maps_ffprobe_json` (`tests/integration/test_filesystem_media.py`) write only a fake `ffmpeg.exe`. They pass only on a host with ffprobe on PATH. | Mat: "Sibling ffprobe.exe (Recommended)". | New `FIXTURE_REPAIRS` (g): each test writes a sibling fake `ffprobe.exe`. Fixture only; no assertion changes. |
| A-6 | S2, census N-2. Repair (d), "`dependencies()` fakes need nothing", is wrong for the SimpleNamespace fakes in `tests/e2e/test_api_health_settings.py` (`_Lifecycle`) and `tests/e2e/test_api_auth.py` (`_Spy`). The `DEPS_FFMPEG` route would raise `AttributeError` and return 500. | Mat: "Add the fields to fakes (Recommended)". | Repair (d) is corrected: those fakes gain `ffmpeg_path=None, ffprobe_available=False`. No assertion changes. |
| A-7 | S2, census N-3. `test_ac_14_7_lifespan_startup_and_shutdown_spies` (`tests/e2e/test_api_auth.py`) uses one `_Spy` for transcript, tts and models. `SHUTDOWN_STOP` would double its recover and stop counts, and its `None` stop would skip unload and dispose. | Mat: "Separate tts no-op fake (Recommended)". | Repair (e) is extended: `_services()` passes `tts=` a separate no-op fake whose stop returns `True`. No assertion changes. |
| A-8 | Row 5 survey, before any MEU-78 test edit. `RESOLVER_ORDER` and AC-78.4 name an adapter `gpu_capabilities()` that "keeps its cache, keyed by the resolved ffmpeg path". No such method exists. `FFmpegAdapter.detect_gpu()` probes on every call, and its `self._gpu` is written but never read. `POST /conversions/gpu/refresh` (ConvertPage Refresh) calls it to force a new probe; the only GPU cache is `ConversionService._gpu`, outside `PRODUCT_SCOPE`. | Mat: "Retarget to detect_gpu (Recommended)". | AC-78.4 tests `detect_gpu()`: after `configured_source` changes, the next call runs the new ffmpeg, and two calls on an unchanged path probe twice. The cache clause is dropped from `RESOLVER_ORDER`. No existing test or TA changes. |
| A-9 | Row 5, while writing AC-78.9. The AC says to type a path into the FFmpeg path field, but that input is `readOnly` with a no-op `onChange` (`SettingsPage.tsx`, `settings-leaf-ffmpeg_path`). The only control that writes `ffmpeg_path` is Browse (`browse-ffmpeg-btn` → `putNow('downloader', { ffmpeg_path })`), whose E2E dialog returns a fixed path. | Mat: "Use Browse (Recommended)". | AC-78.9 clicks `browse-ffmpeg-btn` to flush the `PUT /settings/downloader` carrying `ffmpeg_path`. The `DEPS_REFRESH` proof is unchanged, and so is the product UX. |
| A-10 | S2 at row 7. The first `gate78` run failed one step, the pytest suite: `tests/unit/test_domain_conversion.py::test_ac_28_7_mediaport_additive_requires_cancel_hook` asserts that `MediaPort`'s public methods equal `keep + additive` exactly and in order. The new `ffmpeg_binaries` (`DEPS_FFMPEG`; TA-3 and TA-4 already add it to the other two port lists) breaks that. The row-1 census missed this third closed list. A sweep for `"ffmpeg_version"`, `MediaPort.__dict__` and `MEDIA_PORT_METHODS` in `tests`, `ui/tests` and `mcp-server/tests` finds no other site. | Mat: "Add TA-11 (Recommended)". | **TA-11:** the `keep` tuple gains `"ffmpeg_binaries"` after `"ffmpeg_version"`. Nothing else in the test changes. `TEST_AMENDMENTS`, S2, the MEU-78 Files Modified table, `task.md`, `exec_checks.TA_SITES` and `plan_checks` now name TA-1 to TA-11. Follow-through found before H1-3: `plan_checks.py selftest` still probed `TA-11` as an undefined TA id, which A-10 made defined, so the case went unreported (`FAIL: selftest cases not reported: ['undefined TA']`). The probe now names `TA-12`; no check was loosened. The H1-2 audit and the H1-3 gate run after this edit. |
| A-11 | H1-2, first `-Check audit` run. `validate-task.ps1:313` cleared `$rd` with `-Filter 's33-audit*'`, which also matches the row's own receipt `s33-audit-run.txt`; the task row's `*>` redirect held it open, so `Remove-Item` failed and the check exited 1 before the fingerprint, the prep or the runner. The baseline and the plan-folder evidence were untouched (`git status` clean for both). | Mat: "Skip the live receipt (Recommended)". | The cleanup pipes through `Where-Object Name -ne 's33-audit-run.txt'`, so it deletes strictly less; the task row's command is unchanged. H1-2 is rerun from the start. |
| A-12 | H1-3, first `-Check windows-gate` run on the final tree (S6). Only the ui-electron stage failed: 4 tests in `ui/tests/e2e/capture-picker.test.ts` (lines 203, 227, 243, 260) reported "the deterministic sidecar stub is missing" (spawn ENOENT on `native/region-picker-stub/publish/avkit-region-picker-stub.exe`). pytest 720, Vitest 804, MCP 423 and state-render passed; the gate fingerprint was equal before and after. The stub is gitignored build output (`.gitignore:29`, `native/**/publish/`) that row 0's install list does not build, so this worktree never had it: an environment gap, not a product defect. | Mat: "Build stub, rerun gate (Recommended)". | `npm --prefix ui run build:picker-stub` exit 0 (`s33-picker-stub-build.txt`); the publish output and `bin/`/`obj/` are ignored, so no tracked or fingerprinted path changed. No test edit. H1-3 is rerun from the start. |
| A-13 | R1 F1 correction, `-Check gate77` rerun (S6). Only the MCP Vitest stage failed: 2 of 423 tests in `mcp-server/tests/audit/runner-fake-backend.test.ts` (AC-68.7 `refusal_mutated`: `expected undefined to be 'fail'`; AC-68.8: `expected 4 to be 3`), each ending in about 30 ms with a runner error (exit 4) before any step ran. The file drives a Node fake backend and the built MCP server; it does not reach `tts.py` or any path the correction touched, and no `mcp-server/` file changed since H1-3 passed 423/423. Every other gate77 stage passed. | Autonomous (obviousness test, as A-4: environment only; no gate, test or plan change). Re-observe without editing anything; H1-3 reruns the whole MCP suite on this tree and is the gate of record. A repeat in H1-3 stops for Mat. | The file alone 5 consecutive times: 9/9 each (`s33-r1f1-mcpflake-1..5.txt`); the full MCP suite: 423/423 (`s33-r1f1-mcp-full.txt`). Not reproduced. No test edit. |
| A-14 | H2-1 dry run: `validate_closeout_artifacts.py --reflection … --decision-source implementation-plan.md` refused plan decision_log item 10 (D-17) as carrying a template placeholder. Its `PLACEHOLDER` regex (`\{…\}`, `<[a-z-]+>`) matches the literal `{id}.wav` in D-17 and `'<Type>: <message>'` in D-19, both filled decisions. A sweep of every decision source found no other match. The plan is fingerprinted, so any rewording invalidates H1-2 and H1-3. The H1-3 run that was in flight finished before the rewording: `PASS WINDOWS_GATE`, MCP 423/423 (A-13 not repeated), fingerprint `e19f9eda…` before and after (`s33-windows-gate-prereword.txt`); it is superseded. | Mat: "Reword now, rerun (Recommended)". | D-17 and D-19 `chosen` reworded with the same meaning; a §Execution Correction Notes row records it. No AC, contract, test or tool change. H1-2 and H1-3 are rerun from the start, then H1-4, H1-6 and H1-7. |

After A-1 to A-3, `plan_checks.py static` passed (24 rows), the ps1 parse found 0 errors, and `lint_task_contract.py --allowed-builder-classes avkit_coordinator,avkit_builder` passed (24 rows), which is the same invocation as the planning receipt.

## Baseline

- `baseline.sha`: `ddd11171ceb3ce307a6a735a5b77094b7d456d39` (Mat's plan commit on `c72fc44`).
- `baseline-counts.json`: MCP suite 411 of 411 passed at `ddd1117`, measured 2026-10-15T23:01:56Z.
- D-10 overlap with `P:/av-kit`: 0 Files Modified paths. It is on `main` at `c72fc44` with a clean tree, so it is the merge-base itself.
- Python: the worktree `.venv` is CPython 3.12.12 (A-4); `uv sync --frozen --all-packages` exit 0.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row0-prereq", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check prereq", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 0: context-tool gate, MEU state, plan review, authorization, installs, baseline.sha, S4 overlap, MCP count", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ddd11171ceb3ce307a6a735a5b77094b7d456d39 plus the A-1 to A-3 plan-folder edits; no product edits", "output": "PASS MEU-76, MEU-78, MEU-77 pending | PASS plan review approved, round 4, agent gpt-6.1-sol | PASS execution authorization recorded | prereq-uv-sync, prereq-ui-ci, prereq-electron, prereq-mcp-ci exit 0 | baseline.sha ddd11171ceb3ce307a6a735a5b77094b7d456d39 | PASS no Files Modified path moved since planning; 0 overlap(s) with P:/av-kit (P:/av-kit branch main, merge-base c72fc4436da8534ef613264620b83c3e84e97631) | PASS baseline-counts.json mcp_passed 411 | PASS prereq", "fresh": true}
```

## Census

Row 1 receipt: `C:/Temp/av-kit/s33-census.txt` (`validate-task.ps1 -Check census`, untruncated `rg -n` over `tests`, `ui/tests` and `mcp-server/tests`). It has 140 lines: line 1 is the rtk banner and the other 139 are hits. These patterns have 0 hits: `is re-raised`, `MASKED_500`, `generate is one job`, `CONSOLE_FIELDS`, `_ffmpeg_path`, `internal_error`, `_probed`, `list_by_status`, `ffmpeg_binaries` and `DependencyHealth(`; `status_code == 500` has only the three hits below. Searches beyond the patterns (`HealthService(`, `.dependencies()`, `health/dependencies`, `tts_jobs`, media fakes) were added for repairs (b) to (e).

### Test amendments (TA-1 to TA-11)

| Hit | Disposition |
|---|---|
| `tests/unit/test_domain.py:181`, `:217` (`DOMAIN_ERROR_TYPE_NAMES`) | TA-1 (MEU-76) |
| `tests/integration/test_filesystem_media.py:240`, `:271`, `:284` (`test_ac_8_6`, the `count["n"] == 1` assertion) | TA-2 (MEU-78). Product note: `is_available`, `ffmpeg_version`, `convert`, `detect_gpu` and `_require_ffmpeg` resolve **only** ffmpeg, through `_resolve_ffmpeg()`. Only `probe` and `ffmpeg_binaries` look up ffprobe. Otherwise the test's raising `_which` and its `path_hits == []` would fail |
| `tests/unit/test_domain.py:1153`, `:1326` (`MEDIA_PORT_METHODS`) | TA-3 (MEU-78) |
| `tests/integration/test_filesystem_media.py:196`, `:462` (`MEDIA_PORT_METHODS`) | TA-4 (MEU-78) |
| `tests/unit/test_domain_conversion.py:177` (`test_ac_28_7`, the ordered `MediaPort.__dict__` tuple) | TA-11 (MEU-78), added by A-10. Row 1 missed it: no census pattern matched `MediaPort.__dict__` or the inline `keep` tuple |
| `tests/integration/test_sqlite_uow.py:313`, `:977` (`TTS_REPO_METHODS`) | TA-6 (MEU-77) |
| `tests/integration/test_sqlite_uow.py:764` (the `test_ac_5_11` loop over `TTS_REPO_METHODS`) | confirmed-consistent: after TA-6 the loop also checks `list_by_status` on the SQL repository, which MEU-77 adds |
| `tests/unit/test_services.py:1769` (the last block of `test_ac_12_5_progress_resolution_and_cancel`) | TA-7 (MEU-77) |
| `tests/unit/test_services.py:2064` (`test_ac_12_5_invalid_progress_marks_failed`) | TA-8 (MEU-77) |
| `tests/integration/test_tts_assets.py:633`, `:639` | TA-9 (MEU-77) |
| `tests/integration/test_tts_assets.py:701`, `:718` | TA-10 (MEU-77) |

### Fixture repairs

Each row names the bare file path in backticks, which is what `api-scope` matches. N-1 to N-3 were raised under S2 and decided by Mat as A-5 to A-7 (§Gate decisions).

| Site | Disposition |
|---|---|
| `tests/unit/test_services.py` `_tts_stack` | repair (a): `spawn=lambda fn: fn()` |
| `tests/unit/test_services.py` `FakeTTSRepo` (line 102; used via line 282) | repair (b): gains `list_by_status` |
| `tests/unit/test_services.py` `FakeMedia` (line 310; inherited by `FakeConvertMedia` at line 1648; `HealthService(...).dependencies()` at line 574) | repair (c): gains `ffmpeg_binaries` |
| `tests/e2e/test_api_health_settings.py` `_Lifecycle.dependencies` (line 44; route test `test_ac_15_12` at line 158) | repair (d) as corrected by A-6 (N-2): the SimpleNamespace gains `ffmpeg_path=None, ffprobe_available=False`. Without them the route's `deps.ffmpeg_path` raises `AttributeError` and returns 500 |
| `tests/e2e/test_api_auth.py` `_Spy.dependencies` (line 56; `test_ac_14_2` at lines 138-149 and 170-178) | repair (d) as corrected by A-6 (N-2), same change |
| `tests/e2e/test_api_auth.py` `_services()` (line 77; `test_ac_14_7_lifespan_startup_and_shutdown_spies`, asserts at lines 241-250) | repair (e) as extended by A-7 (N-3): `tts=` gets a separate no-op fake (recover does nothing, stop returns `True`). With the shared `_Spy`, `recover_calls` and `stop_calls` would become 2, and the `None` stop would skip unload and dispose |
| `tests/integration/test_tts_assets.py` `_generate`, `_generate_with` | repair (f): `stack.services.tts.wait_idle(5.0)` after the POST |
| `tests/unit/test_ffmpeg_conversion.py` `test_ac_29_4_probe_fills_additive_media_info` (probe at line 330; `_fake_ffmpeg` at line 152 writes only `ffmpeg.exe`) | repair (g), new by A-5 (N-1): the test writes a sibling fake `ffprobe.exe`. Without it, `FFPROBE_RULE` falls back to `which("ffprobe")`, and the test passes only on a host with ffprobe on PATH |
| `tests/integration/test_filesystem_media.py` `test_ac_8_10_probe_maps_ffprobe_json` (probe at line 417) | repair (g), new by A-5 (N-1), same change |

### Confirmed-consistent or not affected

| Hit | Disposition |
|---|---|
| `mcp-server/tests/audit/transcript-oracle.test.ts:80`, `:109`, `:118`; `ui/tests/e2e/fixtures/transcript-job.json:12` | not affected: transcript `"Done"` statuses |
| `tests/unit/test_domain.py:255`, `:262`, `:263`, `:264`, `:1496`, `:1498`; `tests/unit/test_domain_conversion.py:78`, `:352` | not affected: enum and requeue name lists. `TTSStatus` is unchanged |
| `tests/unit/test_services.py:437` to `:473` (16 hits), `:887`, `:1078`, `:1431`, `:1499`, `:1930`, `:1932`, `:1944`, `:1951` | not affected: settings, download, transcript and prepare validation, which keep their synchronous `ValidationError` |
| `tests/unit/test_services.py:1785`, `:1787` (`test_ac_12_6`) | confirmed-consistent: the pre-spawn checks stay synchronous (`ASYNC_GENERATE`) |
| `tests/unit/test_domain.py` 25 `pytest.raises(ValidationError)` hits (`:391` to `:1486`); `tests/unit/test_domain_conversion.py:109`, `:111`, `:325`; `tests/unit/test_domain_capture.py` 9 hits (`:135` to `:286`); `tests/unit/test_capture_service.py:421`; `tests/unit/test_capture_adapter.py:285`, `:288`, `:521`; `tests/integration/test_youtube_adapter.py:265`, `:273`, `:321`, `:416`; `tests/integration/test_sqlite_uow.py:921`, `:942`; `tests/integration/test_tts_models.py:690`; `tests/e2e/test_api_captures.py:970`; `tests/integration/test_tts_assets.py:256`; `tests/integration/test_filesystem_media.py:120`, `:124`, `:130` | not affected: domain and adapter validation that MEU-76 does not reclassify |
| `tests/unit/test_ffmpeg_conversion.py:383`, `:420`, `:459`, `:520`, `:566`, `:603`, `:649`, `:760`, `:836` | confirmed-consistent: `configured_path=` is kept, and `detect_gpu`, `convert` and `encode` need only ffmpeg |
| `tests/unit/test_ffmpeg_bundle_wire.py:53`, `:56` | confirmed-consistent: they call `_resolve_ffmpeg()` directly, so the implementation keeps that name as the latch-free ffmpeg resolver |
| `tests/integration/test_filesystem_media.py:336` (`ffmpeg_version`, then `which` patched to `None` for a second adapter), `:365` (`convert` argv) | confirmed-consistent: they need ffmpeg only, and resolving on every call does not change the outcome |
| `tests/unit/test_conversion_service.py:720` | not affected: a name match on "probed" bit depth; `RecordingMedia` (`:160`) is never asked for `ffmpeg_binaries` |
| `tests/integration/test_tts_models.py:647`, `:649`, `:650`, `:652`, `:653` (`tts_text`) | confirmed-consistent: MEU-77 adds no file under `packages/infrastructure/src/avkit_infra/tts/` (the change is in `avkit_core/services/tts.py`) |
| `tests/e2e/test_api_auth.py:186` (`status_code == 500`) | confirmed-consistent: the 500 envelope `details` stay within `{request_id}` (`CORS_SAFE_500`) |
| `tests/e2e/api_fakes.py:522` (`make_bundle`); `tests/e2e/test_api_downloads.py:179`; `tests/e2e/test_api_conversions.py:292`, `:667`; `tests/e2e/test_api_captures.py:385`; `tests/e2e/test_api_capture_flatten.py:113`; `tests/e2e/test_api_health_settings.py:115`; `tests/e2e/real_stack.py` (`replace(make_bundle(...))`) | confirmed-consistent: their tts fakes already define `recover_stale_processing` and `stop_processing` (returning `None`), so the (e) no-op addition does not apply. A `None` stop skips `models.unload()` and `engine_dispose()`. Every one of these passes `engine_dispose=None`, and no assertion reads unload (`test_ac_31_18` at `:667` asserts only `cancel_calls`) |
| `tests/unit/test_uow_commit_log.py:16`, `tests/unit/test_console_level.py:18` (`_Media`); `tests/e2e/real_stack.py:71` `StubMedia` | not affected: no `dependencies()` call reaches them |
| `tests/integration/test_tts_assets.py:182` (`/health/dependencies` via `build_services`) | confirmed-consistent: a real `FFmpegAdapter` and a real `DependencyHealth` |
| `tests/integration/test_filesystem_media.py` (the Files Modified note for (c)) | no (c) site: the file has no media fake. It carries repair (g) and TA-2 and TA-4 instead |

N-1 to N-3 were raised under S2 before any test edit. Mat decided them as A-5 to A-7.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row1-census", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check census", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 1: TEST_AMENDMENTS / FIXTURE_REPAIRS census over tests, ui/tests and mcp-server/tests; every hit dispositioned in walkthrough.md Census", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ddd11171ceb3ce307a6a735a5b77094b7d456d39 plus plan-folder edits A-1 to A-7; no product or test edits", "output": "census: 140 hit line(s) in s33-census.txt (1 rtk banner + 139 hits) | PASS census | dispositions: TA-1..TA-10 sites, repairs (a)-(g), 3 new-contradictions N-1..N-3 raised under S2 and decided by Mat as A-5..A-7", "fresh": true}
```

## MEU-76 api-error-surface

### Red (row 2)

The red-guard passed first: the 7 MEU-76 product files were unchanged versus `baseline.sha`. Every failure is an assertion failure, and each one fails for the intended reason:

- AC-76.1: the 500 carries no `access-control-allow-origin`, because the Exception handler runs outside CORS.
- AC-76.2 and AC-76.4: no `api.unhandled_error` event is emitted (`assert 0 == 1`).
- AC-76.3: the console line lacks ` request_id=rid-1 route=...`.
- AC-76.5, AC-76.6 and AC-76.7: `avkit_core.domain.errors.ExtractError is missing` (the `PY_SYMBOLS` presence assertion).
- AC-76.8: the 500 message is `Internal server error`, without the request id.
- AC-76.9: the add signatures miss the ExtractError bot wall and still match a bare `internal_error`.

Every `_neg` / `[neg]` test that does not depend on a new symbol passed.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row2-red76", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check red76", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 2: MEU-76 Red over AC-76.1-76.9 (pytest, ui Vitest, MCP Vitest); red-guard first", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ddd11171ceb3ce307a6a735a5b77094b7d456d39 plus MEU-76 test edits only; red-guard: 7 MEU-76 product files unchanged vs baseline.sha", "output": "pytest failed 8, passed 24 | vitest failed 1, passed 3 | mcp failed 2 | PASS red76 (RED_RULE)", "fresh": true}
```

### Green (row 3)

All six contracts and TA-1 are implemented. The first `green76` run failed on AC-76.2 alone: the event's `route` was `/health/dependencies`. In FastAPI 0.141, `include_router` wraps a router in an `_IncludedRouter`, so the matched `APIRoute.path_format` is relative to the include prefix and `root_path` stays empty. `_route` (errors.py) now recovers the prefix as the part of the URL path before the suffix that the route's own `path_regex` matches, so the event carries the full template. A probe on a parametrized route logged `/api/v1/transcripts/{id}`, and its 500 carried `access-control-allow-origin`. FastAPI's private effective-route context was not used.

- `ExtractError` is raised only at the three `_run_extract` sites. `_run_extract` checks for a non-dict before calling `_info_dict`, whose own plain `DomainError` would otherwise mask the type. `download()` is unchanged.
- An unmapped `DomainError` 500 logs `ERROR_EVENT` in the DomainError handler. A mapped 503 does not log it. The Exception handler is now a logging backstop that returns `internal_error_response`.
- The `census.ts` comment at `:8` names ExtractError.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row3-green76", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check green76", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 3: MEU-76 Green over AC-76.1-76.9 plus TA-1 (pytest MEU-76 files and test_domain.py, ui Vitest, MCP Vitest)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ddd11171ceb3ce307a6a735a5b77094b7d456d39 plus MEU-76 test and product edits and TA-1", "output": "PASS green pytest MEU-76: passed 83 | PASS green vitest MEU-76: passed 4 | PASS green mcp MEU-76: passed 2 | PASS green76", "fresh": true}
```

### Gate (row 4)

The first `gate76` run failed two steps.

- **py-lint (E501):** two `_require_extract_error` assertion lines in the new tests were 101 characters long. They were wrapped, and the assertion text is unchanged.
- **pytest, AC-24.10 and AC-25.10:** the fresh worktree lacked the gitignored packaging outputs (`packaging/dist/avkit-backend`, `packaging/ffmpeg-win64`). This is environment provisioning; no test or product file changed.
  - `tools/fetch_ffmpeg_windows.ps1` got a 404 for its pinned BtbN `autobuild-2026-08-24-13-10` URL, because the release has since been pruned upstream.
  - The two vendor binaries were therefore copied from the main checkout, a read-only use of `P:/av-kit`, which stays clean. Both report the pinned `n8.1.2-44-g7c533d0f86-20260824` build. Their sha256 values match the source: `ffmpeg.exe` is `a575beb7…`, `ffprobe.exe` is `6f2f2d64…`.
  - `tools/package_backend.py` (PyInstaller 6.22.2) built the onedir tree from this worktree, exit 0: `avkit-backend.exe` (47,264,534 bytes) plus `_internal`.
- **Line endings:** two heredoc appends had left LF lines in CRLF checkouts (`tests/unit/test_console_level.py`, `ui/tests/unit/api-fetch.test.ts`). Those two files and the new `census-signature.test.ts` were normalized to CRLF. The repository stores LF (`* text=auto`), so the commit content is unchanged.

The rerun is the gate of record. The pre-handoff self-review raised no findings. The handoff is `.agent/context/handoffs/2026-10-14-backend-robustness-MEU-76-handoff.md`.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row4-gate76", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate76", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 4: MEU-76 targeted gate (pyright, ruff, ui typecheck and lint, mcp typecheck, openapi --check, pytest tests/, ui Vitest, MCP Vitest, source audit, product snapshot)", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "MEU-76 final working tree (baseline ddd1117 + MEU-76 diff + TA-1)", "output": "py-types, py-lint (All checks passed!), ui-types, ui-lint, mcp-types, openapi exit 0 | PASS suite pytest: passed 668 | PASS suite vitest: passed 802 | PASS suite mcp: passed 413 | source-audit rg exit 1 (no hits) | PASS snapshot of 25 product files | PASS gate76", "fresh": true}
```

## MEU-78 svc-ffmpeg-resolver

### Red (row 5)

The red-guard passed first: the 11 MEU-78 product files were unchanged versus the row 4 snapshot `s33-gate76-product.json`. Every failure is an assertion failure, and each one fails for the intended reason:

- AC-78.1 to AC-78.4: `avkit_core.domain.conversion.FFmpegBinaries is missing` (the presence assertion that runs before any `ffmpeg_binaries()` or `configured_source` use). AC-78.4 tests `detect_gpu()` per A-8.
- AC-78.5 and AC-78.6: `YouTubeAdapter(ffmpeg_location=...) is missing`.
- AC-78.7: `ffmpeg.ffprobe_available` is absent from `/health/dependencies`. In the negative test, the route still reports the raw missing setting (`...\gone\ffmpeg.exe`) instead of the PATH binary.
- AC-78.8: an `ffmpeg_path` PUT makes no `QUERY_HEALTH_DEPENDENCIES` invalidation (`expected [] to have a length of 1`).
- AC-78.9: `deps-ffprobe-row` is not visible within 5 s. Per A-9, the spec drives the PUT through `browse-ffmpeg-btn`.

The `[neg]` Vitest case passed. The pytest `_neg` cases fail on the same presence assertions, which RED_RULE allows. The seam's `/health/dependencies` answer gained `ffprobe_available: true`, and `test-ids.ts` gained the `// MEU-78` block with `DEPS_FFPROBE_ROW`.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row5-red78", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check red78", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 5: MEU-78 Red over AC-78.1-78.9 (pytest, ui Vitest, Electron AC-78.9); red-guard first", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "MEU-76 Green tree plus MEU-78 test edits only; red-guard: 11 MEU-78 product files unchanged vs the row 4 gate76 snapshot", "output": "pytest failed 14, passed 21 | vitest failed 1, passed 1 | electron failed 1 | PASS red78 (RED_RULE)", "fresh": true}
```

### Green (row 6)

RESOLVER_ORDER, LIVE_SOURCE, FFPROBE_RULE, FFMPEG_LOCATION, DEPS_FFMPEG and DEPS_REFRESH are implemented. The first `green78` run passed.

- **Resolver:** `FFmpegAdapter` holds no latch. Its `_probed`, `_ffmpeg` and `_gpu` fields are gone. `_resolve_ffmpeg` re-reads the configured path (fixed `configured_path`, or the new `configured_source` callable), then the bundle, then `PATH`, on every call. Passing both arguments raises `ValueError`.
  - `_resolve_ffprobe` takes the sibling `ffprobe(.exe)` first, then `PATH`.
  - `ffmpeg_binaries()` returns `FFmpegBinaries(ffmpeg, ffprobe)`, or `None`. The new frozen dataclass is in `domain/conversion.py`, and the method is on `MediaPort`.
  - `probe` raises `FFmpegNotFoundError("ffprobe binary was not found")` before any subprocess runs.
  - `detect_gpu` no longer caches its capabilities (A-8).
- **Wiring:** `media` is built before `youtube`. `configured_source` reads `downloader.ffmpeg_path` from the settings service at each call. `YouTubeAdapter(ffmpeg_location=...)` gets a callable over `media.ffmpeg_binaries()`, and `_base_opts` sets `ffmpeg_location` to the resolved binary's directory.
- **Health:** `DependencyHealth` gains `ffmpeg_path` and `ffprobe_available`, filled from `ffmpeg_binaries()`. The route no longer reads the setting itself. `FfmpegDependencyOut` gains `ffprobe_available`, and `openapi.committed.json` was regenerated with `tools/export_openapi.py -o`. The diff is that one field plus the schema description.
- **UI:** the Settings dependencies list gains a `deps-ffprobe-row` FFprobe chip. `useSettingsPage` invalidates the dependencies query after a successful `downloader` PUT whose body carries `ffmpeg_path`.
- **Test amendments (TA contract):**
  - **TA-2:** `test_filesystem_media.py` expects two `shutil.which` lookups for two `is_available()` calls (previously one), because the latch is gone.
  - **TA-3 and TA-4:** `ffmpeg_binaries` was added to the media-port method lists in `test_domain.py` and `test_filesystem_media.py`.
- **Fixture repairs (FIXTURE_REPAIRS):**
  - **(c):** `FakeMedia` in `test_services.py` gains `ffmpeg_binaries()`, which returns `None`.
  - **(d):** the `SimpleNamespace` dependency fakes in `test_api_health_settings.py` and `test_api_auth.py` gain `ffmpeg_path=None, ffprobe_available=False`.
  - **(g):** sibling `ffprobe.exe` fakes were added in `test_ac_8_10` (`test_filesystem_media.py`) and `test_ac_29_4` (`test_ffmpeg_conversion.py`).
  - Each edit carries its TA or repair comment, and no assertion was weakened.
- **Static checks:**
  - pyright `packages/` reports 0 errors and `ruff check` passes.
  - `ruff format` was applied to `wiring.py`.
  - The `youtube/adapter.py` format drift (`COOKIE_AUDIO_SELECTOR`, the progress-interval `if`) is already present at baseline and was left alone.
  - `ui` typecheck and lint pass.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row6-green78", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check green78", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 6: MEU-78 Green over AC-78.1-78.9 plus TA-2/3/4 and fixture repairs (c), (d), (g) (pytest MEU-78 files with test_domain.py and test_filesystem_media.py, ui Vitest, Electron E2E AC-78.9, openapi --check)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ddd11171ceb3ce307a6a735a5b77094b7d456d39 plus MEU-76 diff plus MEU-78 test and product edits, TA-2/3/4 and repairs (c), (d), (g)", "output": "PASS green pytest MEU-78: passed 98 | PASS green vitest MEU-78: passed 2 | PASS green electron MEU-78: passed 1 | green78-openapi exit 0 | PASS green78", "fresh": true}
```

### Gate (row 7)

The first `gate78` run failed one step, the pytest suite. `test_ac_28_7_mediaport_additive_requires_cancel_hook` (`tests/unit/test_domain_conversion.py`) pins `MediaPort`'s ordered method tuple, and the new `ffmpeg_binaries` breaks it. This is S2: the row-1 census had missed the site. No test was edited until Mat chose TA-11 (A-10). TA-11 adds `"ffmpeg_binaries"` to the `keep` tuple, and `TEST_AMENDMENTS`, `TA_SITES` and `plan_checks` now name TA-1 to TA-11 (`plan_checks.py static` PASS).

The rerun is the gate of record. It also covers the Electron `settings.test.ts` `--repeat-each=5` step and writes `s33-gate78-product.json` for the MEU-77 red guard.

The pre-handoff self-review raised no findings. It checked that `configured_source` calls `SettingsService.get` from download worker threads through `_base_opts` → `ffmpeg_binaries()`, and that each `get` opens its own unit of work, the pattern the worker threads already use. The handoff is `.agent/context/handoffs/2026-10-14-backend-robustness-MEU-78-handoff.md`.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row7-gate78", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate78", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 7: MEU-78 targeted gate (pyright, ruff, ui typecheck and lint, mcp typecheck, openapi --check, pytest tests/, ui Vitest, MCP Vitest, source audit, Electron settings.test.ts --repeat-each=5, product snapshot)", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "MEU-78 final working tree (baseline ddd1117 + MEU-76 diff + MEU-78 diff + TA-1 to TA-4 and TA-11 + repairs (c), (d), (g))", "output": "py-types, py-lint, ui-types, ui-lint, mcp-types, openapi exit 0 | PASS suite pytest: passed 682 | PASS suite vitest: passed 804 | PASS suite mcp: passed 413 | source-audit rg exit 1 (no hits) | PASS suite electron: passed 65 | PASS snapshot of 25 product files | PASS gate78", "fresh": true}
```

## MEU-77 svc-tts-async-generate

### Red (row 8)

The red-guard passed first: the 11 MEU-77 product files were unchanged versus the row 7 snapshot `s33-gate78-product.json`. Every non-negative failure is an assertion failure, and each one fails for the intended reason:

- AC-77.1 to AC-77.7 and AC-77.9 (`tests/unit/test_tts_async.py`): `TTSService(spawn=...) is missing` (the `_require()` presence assertion that runs before any service use).
- AC-77.8 and AC-77.10 (appended to `tests/integration/test_tts_assets.py`): the startup row stays `Generating`, and `wait_idle` is absent.
- AC-77.11: the PyTorch branch drains every chunk (`[1, 2, 3] == [1]`), and the progress values miss the estimate. The ONNX `_neg` passes.
- AC-77.12 (`mcp-server/tests/tts.test.ts`): the description and `SERVER_INSTRUCTIONS` lack the asynchronous text. The fetch half already passes, so it shares one non-negative test with the description assertion.
- AC-77.13 (`mcp-server/tests/audit/tts-cancel-step.test.ts`): `tts_cancel_text` is absent, and the step still cancels `tts_job1` with no retry. The `destructiveStep` `[neg]` passes.

The 22 passing pytest cases are the negative tests and the untagged `test_tts_assets.py` tests, which stay unmodified until row 9 (TA-9, TA-10, repair (f)). The Electron `AC-77.14` pin passed in the same run: the run bar polled the `Generating` seam job at least twice, showed `last-output` only after `Done`, and a second run's Cancel sent one `DELETE` and returned to an enabled Generate.

Rows 4 and 7 are compact_continue by design; context after compaction is well under 50%, so S9 is not triggered.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row8-red77", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check red77", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 8: MEU-77 Red over AC-77.1-77.13 (pytest, MCP Vitest) and the Electron AC-77.14 pin; red-guard first", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "MEU-78 gate tree plus MEU-77 test edits only; red-guard: 11 MEU-77 product files unchanged vs the row 7 gate78 snapshot", "output": "pytest failed 36, passed 22 | mcp failed 9, passed 1 | electron passed 1 (pin) | PASS red77 (RED_RULE)", "fresh": true}
```

### Green, service side (row 9)

`TTSService.generate` now runs the sync checks, admits one `Generating` row under `_lock` and hands the run to `spawn` (default: a daemon thread named `tts-generate`). It returns the row at once. The worker owns every terminal write through `_finish`, which releases the reservation in a `finally`. Cancel sets a flag that `on_progress` and the post-WAV and post-MP3 checks honour. `PARTIAL_CLEANUP` unlinks the job's WAV and MP3. Startup fails stale `Generating` rows (`interrupted by restart`, via the new `list_by_status`). Shutdown refuses new runs, cancels the running one, waits up to 10 s and skips unload and dispose when the worker is still busy (`api.shutdown_tts_busy`). The PyTorch branch consumes chunks lazily against a sentence-count estimate capped at 0.99.

Two log events are beyond the plan's list, and both cover failure paths only: `tts.finish_failed` (the terminal write itself raised) and `tts.cleanup_failed` (an unlink raised `OSError`).

TA-5 to TA-10 and repairs (a), (b), (e)/A-7 and (f) are applied as written, each with its `# TA-n` / `# FIXTURE_REPAIRS` comment. One helper split goes with repair (f): `_generate` now waits for idle, and the row-8 AC-77.10 tests hold the worker on a 5 s gate, so a waiting POST would race that gate. Those three call sites now use a new non-waiting `_post_generate`, which carries the unchanged POST body; `_generate` is `_post_generate` plus `wait_idle(5.0)`. No assertion changed. `openapi.committed.json` was regenerated: the diff is the two TTS route descriptions (`OPENAPI_DIFF`) on top of the MEU-78 ffprobe fields. `tests/e2e/test_api_auth.py` and `test_api_health_settings.py` (outside this check) pass 12/12, and ruff is clean on the edited files.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row9-green77-svc", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check green77-svc", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 9: MEU-77 backend (ASYNC_GENERATE, WORKER_RULE, CANCEL_RULE, PARTIAL_CLEANUP, RESTART_RECOVERY, SHUTDOWN_STOP, PROGRESS_LAZY, list_by_status, route docstrings, openapi) with TA-5..TA-10 and repairs (a), (b), (e), (f)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "uncommitted worktree on baseline ddd11171: MEU-76, MEU-78 and the MEU-77 backend plus test edits", "output": "pytest PY77+TA77 192 passed | PASS green pytest MEU-77: passed 192 | openapi --check exit 0 | PASS green77-svc", "fresh": true}
```

### Green, MCP side (row 10)

`destructiveStep` now runs its precondition block and the refusal sequence through one inner `once`, which keeps today's body unchanged apart from moving it. `execute` loops over `once` up to `attempts` times (the default of 1 means no retry). It retries only when both refusals held (and the declined one, when present), the confirmed call had no error and no effect, and `raceLost` is true. A non-destructive outcome (`precondition_lost`) or any other result is returned at once. The `attempt n/<attempts>` prefix goes on `detail` only when `attempts > 1`, so every other destructive step's output is byte-identical to before.

`tts.cancel` targets `tts_job2`. The precondition requires it to be `Generating`, and `reestablish` POSTs the `generateArgs` body without `action` plus `tts_cancel_text`, then registers the id in the ledger. `raceLost` means `Done`, and `attempts` is 3. `AUDIT_FIXTURES.tts_cancel_text` is the 60-sentence string, and the `tts_text` comment no longer says generate is synchronous. The `tts.ts` `desc()` and the `SERVER_INSTRUCTIONS` TTS line carry the `MCP_TTS_TEXT` wording. `tsc --noEmit` and `tsc -p tsconfig.scripts.json` are clean.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row10-green77", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check green77", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 10: MEU-77 MCP side (MCP_TTS_TEXT, AUDIT_CANCEL_STEP in plan.ts and fixtures.ts); every MEU-77 AC incl. Electron AC-77.14", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "uncommitted worktree on baseline ddd11171: MEU-76, MEU-78 and MEU-77 backend plus MCP side; MCP and Electron rebuilt by the check", "output": "PASS green mcp MEU-77: passed 10 | PASS green electron MEU-77: passed 1 | PASS green pytest MEU-77: passed 192 | PASS green77", "fresh": true}
```

Row 11 (MEU-77 targeted gate, gate of record). Every stage exited 0 except the source audit, whose rg exit 1 is the clean result (zero hits over `$SRC77`; `SourceAudit` maps exit 1 to pass). pytest 720 (682 at gate78, plus the 38 MEU-77 tests net of the edited ones), ui Vitest 804 (unchanged; MEU-77 has no ui product change), MCP Vitest 423 (413 + the 10 MEU-77 MCP tests), Electron `tts-generate.test.ts --repeat-each=5` 75 passed (15 x 5), and `tests/unit/test_tts_async.py` passed 34 in each of the five consecutive runs, so the worker-race tests show no flake. Self-review before the handoff: the AC table in the MEU-77 handoff maps AC-77.1 to AC-77.14 to file:line test references; the handoff's two placeholders now carry this gate's evidence line and counts; the handoff is CRLF.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row11-gate77", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate77", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 11: MEU-77 targeted gate (pyright, ruff, ui typecheck and lint, mcp typecheck, openapi --check, pytest tests/, ui Vitest, MCP Vitest, source audit, Electron tts-generate.test.ts --repeat-each=5, tests/unit/test_tts_async.py five consecutive runs)", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "MEU-77 final working tree (baseline ddd1117 + MEU-76 diff + MEU-78 diff + MEU-77 diff + TA-1 to TA-11 + repairs (a) to (g))", "output": "py-types, py-lint, ui-types, ui-lint, mcp-types, openapi exit 0 | PASS suite pytest: passed 720 | PASS suite vitest: passed 804 | PASS suite mcp: passed 423 | source-audit rg exit 1 (no hits) | PASS suite electron: passed 75 | test_tts_async.py x5: passed 34 each | PASS gate77", "fresh": true}
```

Row 12 (hub reconciliation). Applied plan §BUILD_PLAN.md Audit items 1-5: 04 Extractor failures now names `ExtractError` -> 422 (D-15); 03 drops the re-raise from the TTS error_message row (D-19), adds the TTS async Status and Restart rows (D-18, `RESTART_RECOVERY`, `SHUTDOWN_STOP`) and the FFmpeg No cache row (D-16); 02 `is_available` says resolve on every use and names the bundled `resources/ffmpeg/` path; 07 both bundle paths move to `resources/ffmpeg/`; 05 cancel bullet and the instructions line 4 match the shipped MCP text. Deviation note: the 03 error_message row reads "an unexpected exception in the background worker marks the job `Failed` ...; nothing is re-raised (Session 33 plan D-19)", which carries the plan's required substance (worker scope, no re-raise, D-19 cite) with slightly different wording for readability; the hub-strings check requires and forbids the plan's tokens, and it passed. All doc-reading suites pass on the edited hub (ui 18, MCP docs 7); `meu_status.py render --check` exits 0.

```json
{"schema_version": "evidence.v1", "check_id": "s33-row12-hub", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check hub", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 12: hub reconciliation (plan BUILD_PLAN.md Audit items 1-5) in docs/build-plan/02, 03, 04, 05, 07; hub strings, meu_status.py render --check, ui doc-reading suites (layout-canon, queue-canon, gui-actions-audit), MCP tests/audit/docs.test.ts", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "MEU-77 final working tree plus the row 12 hub edits (10 insertions, 7 deletions over 5 build-plan files)", "output": "PASS hub strings in 5 files | hub-render exit 0 | PASS suite vitest: passed 18 | PASS suite mcp: passed 7 | PASS hub", "fresh": true}
```

## Handoff gates

H1-1 (row state). `-Check task-state` proves implementation rows 0-12 are all `[x]` (no `[B]` rows this session).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-1-task-state", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check task-state", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-1: task.md rows 0-12 are [x] or evidence-backed [B]", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "MEU-76/78/77 final working tree plus row 12 hub edits; task.md rows 0-12 ticked", "output": "PASS implementation rows 0-12 done | PASS task-state", "fresh": true}
```

## Audit

H1-2 (authoritative MCP audit, `AUDIT_COMPARISON` against the pre-session baseline from `baseline.sha`). The first run of `-Check audit` stopped in its own cleanup before any audit step (A-11); this is the rerun from the start, after the A-11 fix. Runner: `mcp-audit authoritative: 99/99 pass, 0 discovery finding(s), cleanup ok, exit 0` (8 tools, 70 actions; isolation root removed, backend exited). `baseline_carry.py`: 0 issue ids carried, 70 entries. `AUDIT_EXPECT`: 70 actions pass, `avkit_tts.cancel` delta FIXED, every other tts delta UNCHANGED. The `tts.cancel` step (AUDIT_CANCEL_STEP) cancelled the running second job on attempt 1/3 (`before=false after=true`, 23.5 s), with both refusals (`confirm` omitted, `confirm: false`) rejected and unchanged. `tts.generate` reached Done (60,044 B mp3, audio header ok). `AUDIT_FINGERPRINT` 4636f314996a9987798f66652c67dc7b1d7ceb60bd9984eca0dfb955550e862b over 59 changed paths, identical before the prep and after the carry (`audit-fingerprint.json`). The audit rewrote `baseline-snapshot.json` (7 lines) and `.agent/context/MCP/mcp-tool-audit-report.md` through `--update-baseline`; neither was edited by hand.

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-2-audit", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check audit", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-2: authoritative MCP audit with --update-baseline against the pre-session baseline (AUDIT_COMPARISON), baseline_carry.py, AUDIT_EXPECT, AUDIT_FINGERPRINT before and after", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "final MEU-76/78/77 working tree plus row 12 hub edits; fingerprint 4636f314996a9987798f66652c67dc7b1d7ceb60bd9984eca0dfb955550e862b over 59 changed paths", "output": "mcp-audit authoritative: 99/99 pass, 0 discovery finding(s), cleanup ok, exit 0 | PASS baseline_carry: 0 issue ids carried; 70 entries | PASS 70 actions pass, tts.cancel FIXED, cleanup ok | PASS AUDIT_FINGERPRINT before and after | PASS audit", "fresh": true}
```

Run of record (supersedes `s33-h1-2-audit` above). The A-10 follow-through edit to `plan_checks.py` (walkthrough §Gate decisions A-10) moved the fingerprinted tree after the record above, so `-Check audit` was rerun from the start on the final tree. Runner `99/99 pass, 0 discovery finding(s), cleanup ok, exit 0`; `baseline_carry.py` 0 issue ids carried, 70 entries; `AUDIT_EXPECT` 70 actions pass, `avkit_tts.cancel` FIXED. The `tts.cancel` step won on attempt 1/3 (`before=false after=true`, 16.1 s), both refusals rejected with `changed: false`; `tts.generate` Done (60,044 B mp3, audio header ok). `AUDIT_FINGERPRINT` 420ff079885b3fcaadc028b5bd66bb5df6865cfaf20f08b7ade49396db9d8f73 over 59 changed paths, identical before and after (`audit-fingerprint.json`). Receipts: `s33-audit-run.txt`, `s33-audit-*.txt`, `s33-audit/mcp-audit-summary.json`.

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-2-audit-final", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check audit", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-2 rerun on the final tree after the A-10 follow-through: authoritative MCP audit with --update-baseline against the pre-session baseline (AUDIT_COMPARISON), baseline_carry.py, AUDIT_EXPECT, AUDIT_FINGERPRINT before and after; supersedes s33-h1-2-audit", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "final MEU-76/78/77 working tree plus row 12 hub edits and the A-10 selftest probe edit; fingerprint 420ff079885b3fcaadc028b5bd66bb5df6865cfaf20f08b7ade49396db9d8f73 over 59 changed paths", "output": "mcp-audit authoritative: 99/99 pass, 0 discovery finding(s), cleanup ok, exit 0 | PASS baseline_carry: 0 issue ids carried; 70 entries | PASS 70 actions pass, tts.cancel FIXED, cleanup ok | PASS AUDIT_FINGERPRINT before and after | PASS audit", "fresh": true}
```

Run of record after the execution review R1 F1 correction (supersedes `s33-h1-2-audit-final` above). The correction (§Execution review corrections) changed `services/tts.py`, `tests/unit/test_tts_async.py` and the plan, so `-Check audit` was rerun from the start. Runner `99/99 pass, 0 discovery finding(s), cleanup ok, exit 0`; `baseline_carry.py` 0 issue ids carried, 70 entries; `AUDIT_EXPECT` 70 actions pass, `avkit_tts.cancel` FIXED. The `tts.cancel` step won on attempt 1/3 (`before=false after=true`, 16.6 s), both refusals rejected with `changed: false`; `tts.generate` Done (60,044 B mp3, audio header ok). `AUDIT_FINGERPRINT` ebb77a8eaff6186475627c7b2ee41af3db4533226552c7fbdb1b4e77ba055cda over 59 changed paths, identical before and after (`audit-fingerprint.json`). Receipts: `s33-audit-run.txt`, `s33-audit-*.txt`, `s33-audit/mcp-audit-summary.json`.

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-2-audit-r2", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check audit", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-2 rerun on the R1 F1 corrected tree: authoritative MCP audit with --update-baseline against the pre-session baseline (AUDIT_COMPARISON), baseline_carry.py, AUDIT_EXPECT, AUDIT_FINGERPRINT before and after; supersedes s33-h1-2-audit-final", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "corrected tree: the Session 33 final tree plus the R1 F1 edits to services/tts.py, tests/unit/test_tts_async.py and implementation-plan.md §Execution Correction Notes; fingerprint ebb77a8eaff6186475627c7b2ee41af3db4533226552c7fbdb1b4e77ba055cda over 59 changed paths", "output": "mcp-audit authoritative: 99/99 pass, 0 discovery finding(s), cleanup ok, exit 0 | PASS baseline_carry: 0 issue ids carried; 70 entries | PASS 70 actions pass, tts.cancel FIXED, cleanup ok | PASS AUDIT_FINGERPRINT before and after | PASS audit", "fresh": true}
```

Run of record (supersedes `s33-h1-2-audit-r2` above). The A-14 rewording of plan D-17 and D-19 (§Gate decisions A-14) moved the fingerprinted plan after that run, so `-Check audit` was rerun from the start on the final tree. Runner `99/99 pass, 0 discovery finding(s), cleanup ok, exit 0`; `baseline_carry.py` 0 issue ids carried, 70 entries; `AUDIT_EXPECT` 70 actions pass, `avkit_tts.cancel` FIXED. The `tts.cancel` step won on attempt 1/3 (`before=false after=true`, 14.9 s), both refusals rejected with `changed: false`; `tts.generate` Done (60,044 B mp3, audio header ok). `AUDIT_FINGERPRINT` 49d577f4bc8c5ea65e22676d96e83050ef41bd5e37f1c7d28efec93f59a56ce7 over 59 changed paths, identical before and after (`audit-fingerprint.json`). Receipts: `s33-audit-run.txt`, `s33-audit-*.txt`, `s33-audit/mcp-audit-summary.json`.

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-2-audit-r3", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check audit", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-2 rerun on the final tree (R1 F1 correction plus the A-14 plan rewording): authoritative MCP audit with --update-baseline against the pre-session baseline (AUDIT_COMPARISON), baseline_carry.py, AUDIT_EXPECT, AUDIT_FINGERPRINT before and after; supersedes s33-h1-2-audit-r2", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "final tree: the Session 33 tree plus the R1 F1 edits to services/tts.py, tests/unit/test_tts_async.py and implementation-plan.md §Execution Correction Notes, and the A-14 D-17/D-19 rewording; fingerprint 49d577f4bc8c5ea65e22676d96e83050ef41bd5e37f1c7d28efec93f59a56ce7 over 59 changed paths", "output": "mcp-audit authoritative: 99/99 pass, 0 discovery finding(s), cleanup ok, exit 0 | PASS baseline_carry: 0 issue ids carried; 70 entries | PASS 70 actions pass, tts.cancel FIXED, cleanup ok | PASS AUDIT_FINGERPRINT before and after | PASS audit", "fresh": true}
```

## Windows gate

H1-3 (`WINDOWS_GATE`, the PROFILE D6 stage set, on the final tree after the H1-2 run of record). The first run on that tree failed only in ui-electron (4 `capture-picker.test.ts` tests, missing gitignored sidecar stub; A-12). After `build:picker-stub` the gate was rerun from the start: 17/17 stages exit 0 in order (npm-ci, mcp-npm-ci, py-types, py-lint, ui-types, ui-lint, mcp-types, py-tests, ui-tests, ui-build, ui-harness-build, mcp-build, mcp-tests, openapi, state-render, ui-electron, source-audit). pytest 720/0 (floor 655), Vitest 804/804, Electron 139 expected / 0 unexpected / 0 skipped / 0 flaky, MCP 423/423, source audit 0 hits. Preflight drift false (agentic-framework `e387dec`). `GATE_FINGERPRINT` 1edd908f72fc5c1598bb33a2f1e1eb8d6e73d2699bf634649b2fc6983240031a before and after (`windows-gate-result.json`, `s33-windows-gate.txt`, `s33-win-*`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-3-windows-gate", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check windows-gate", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-3: WINDOWS_GATE, the full PROFILE D6 stage set (17 stages), GATE_FINGERPRINT before and after; rerun after A-12", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "final MEU-76/78/77 working tree on baseline ddd1117 (same tree as the H1-2 run of record); fingerprint 1edd908f72fc5c1598bb33a2f1e1eb8d6e73d2699bf634649b2fc6983240031a", "output": "17/17 stages exit 0 | pytest passed 720 failed 0 | vitest passed 804/804 | e2e expected 139 unexpected 0 skipped 0 flaky 0 | mcp passed 423/423 | source-audit no hits | fingerprint before == after | PASS WINDOWS_GATE", "fresh": true}
```

H1-4 (`gate-check`): stage order and exits, `COUNT_FLOORS`, `GATE_FINGERPRINT` and `AUDIT_FINGERPRINT` against the current tree, and `AUDIT_EXPECT` all hold (`s33-gate-check.txt`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-4-gate-check", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate-check", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-4: windows-gate-result.json stage order and exits, COUNT_FLOORS, GATE_FINGERPRINT and AUDIT_FINGERPRINT recomputed on the current tree, AUDIT_EXPECT over mcp-audit-summary.json", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "final tree; gate fingerprint 1edd908f72fc5c1598bb33a2f1e1eb8d6e73d2699bf634649b2fc6983240031a, audit fingerprint 420ff079885b3fcaadc028b5bd66bb5df6865cfaf20f08b7ade49396db9d8f73", "output": "PASS gate pytest 720/0, vitest 804/0, e2e 139/0/0/0, mcp 423/0; fingerprint 1edd908f...031a; audit 70 actions pass, tts.cancel FIXED, cleanup ok | PASS gate-check (stages, COUNT_FLOORS, GATE_FINGERPRINT, AUDIT_FINGERPRINT, AUDIT_EXPECT)", "fresh": true}
```

H1-5 (`ssot-review`): MEU-76, MEU-78 and MEU-77 set to `ready_for_review` with `--plan`, rendered and drift-checked (91 MEUs, 12 phases); grouping Session 33 row set to `in review`; `current-focus.md` leads with Session 33 `ready_for_review` (`s33-h1-ssot.txt`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-5-ssot-review", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check ssot-review", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-5: meu_status update MEU-76/78/77 ready_for_review, render, render --check, and exec_checks ssot-review (status, grouping row 'in review', current-focus.md)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "final tree plus the GATE_EXCLUDED SSOT, grouping and focus edits", "output": "Updated MEU-76/78/77 -> ready_for_review | All regions rendered successfully | Drift check passed (91 MEUs, 12 phases) | PASS SSOT review state | PASS ssot-review", "fresh": true}
```

H1-6 (`api-scope`): `export_openapi.py --check` exit 0; `PRODUCT_SCOPE` holds (51 changed product files, all in Files Modified or a §Census repair site, no frozen path changed); every TA-1..TA-11 site carries its `TA-n (Session 33` comment and no stray TA comment exists; `OPENAPI_DIFF` holds against `ddd1117` (`s33-api-scope.txt`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-6-api-scope", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check api-scope", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-6: openapi --check, PRODUCT_SCOPE against baseline ddd1117, OPENAPI_DIFF, TEST_AMENDMENTS site markers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "final tree on baseline ddd1117", "output": "api-scope-openapi exit 0 | PASS product scope: 51 changed files, all listed; TA-1..TA-11 marked; OPENAPI_DIFF holds | PASS api-scope (PRODUCT_SCOPE, OPENAPI_DIFF, TEST_AMENDMENTS markers)", "fresh": true}
```

H1-7 (`handoff-ac`): the three handoffs were reconciled with the final evidence. MEU-76 and MEU-78 named the full gate `(H1-2)`; that now reads `(H1-3)`, and all three handoffs cite the H1-2 audit of record and the H1-3 gate (counts and both fingerprints). The closeout tool finds AC-76, AC-77 and AC-78 in each handoff; `exec_checks handoff-ac` finds every full AC id of each MEU in its own handoff (`s33-handoff-ac.txt`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-7-handoff-ac", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check handoff-ac", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-7: validate_closeout_artifacts --ac-coverage-only for the MEU-76, MEU-78 and MEU-77 handoffs, plus exec_checks handoff-ac (every full AC id of each MEU in its own handoff)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "three final handoffs reconciled with s33-h1-2-audit-final and s33-h1-3-windows-gate", "output": "handoff-ac-76/78/77: OK: all 3 plan AC(s) present in the handoff | PASS each handoff names all of its MEU's ACs | PASS handoff-ac", "fresh": true}
```

Run of record (supersedes `s33-h1-3-windows-gate` above). The R1 F1 correction and the A-14 rewording of plan D-17 and D-19 moved the fingerprinted tree after that run, so H1-3 was rerun from the start on the final tree, after `s33-h1-2-audit-r3`. 17/17 stages exit 0 in order. pytest 724/0 (floor 655; +4 from the R1 F1 regression tests), Vitest 804/804, Electron 139 expected / 0 unexpected / 0 skipped / 0 flaky, MCP 423/423 (A-13 not repeated), source audit 0 hits. Preflight drift false. `GATE_FINGERPRINT` 300cc234644b17997d1e6e7f2c3a7e6ffc3d0a41bb37b9e6252db41799b26f80 over 60 changed paths, before and after (`windows-gate-result.json`, `s33-windows-gate.txt`, `s33-win-*`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-3-windows-gate-r2", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check windows-gate", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-3 rerun on the final tree (R1 F1 correction plus the A-14 plan rewording): WINDOWS_GATE, the full PROFILE D6 stage set (17 stages), GATE_FINGERPRINT before and after; supersedes s33-h1-3-windows-gate", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "final tree, the same tree as s33-h1-2-audit-r3; fingerprint 300cc234644b17997d1e6e7f2c3a7e6ffc3d0a41bb37b9e6252db41799b26f80 over 60 changed paths", "output": "17/17 stages exit 0 | pytest passed 724 failed 0 | vitest passed 804/804 | e2e expected 139 unexpected 0 skipped 0 flaky 0 | mcp passed 423/423 | source-audit no hits | fingerprint before == after | PASS WINDOWS_GATE", "fresh": true}
```

H1-4 rerun (supersedes `s33-h1-4-gate-check`), on `windows-gate-result.json` from `s33-h1-3-windows-gate-r2` and `mcp-audit-summary.json` from `s33-h1-2-audit-r3`. Stage order and exits, `COUNT_FLOORS`, `GATE_FINGERPRINT` 300cc234644b17997d1e6e7f2c3a7e6ffc3d0a41bb37b9e6252db41799b26f80 and `AUDIT_FINGERPRINT` 49d577f4bc8c5ea65e22676d96e83050ef41bd5e37f1c7d28efec93f59a56ce7, both recomputed on the current tree, and `AUDIT_EXPECT` all hold (`s33-gate-check.txt`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-4-gate-check-r2", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate-check", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-4 rerun after A-14: windows-gate-result.json stage order and exits, COUNT_FLOORS, GATE_FINGERPRINT and AUDIT_FINGERPRINT recomputed on the current tree, AUDIT_EXPECT over mcp-audit-summary.json; supersedes s33-h1-4-gate-check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "final tree; gate fingerprint 300cc234644b17997d1e6e7f2c3a7e6ffc3d0a41bb37b9e6252db41799b26f80, audit fingerprint 49d577f4bc8c5ea65e22676d96e83050ef41bd5e37f1c7d28efec93f59a56ce7", "output": "PASS gate pytest 724/0, vitest 804/0, e2e 139/0/0/0, mcp 423/0; fingerprint 300cc234...6f80; audit 70 actions pass, tts.cancel FIXED, cleanup ok | PASS gate-check (stages, COUNT_FLOORS, GATE_FINGERPRINT, AUDIT_FINGERPRINT, AUDIT_EXPECT)", "fresh": true}
```

H1-6 rerun (supersedes `s33-h1-6-api-scope`). `openapi --check` exit 0; `PRODUCT_SCOPE` 51 changed product files, all listed; `OPENAPI_DIFF` holds; TA-1..TA-11 site markers present (`s33-api-scope.txt`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-6-api-scope-r2", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check api-scope", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-6 rerun after A-14: openapi --check, PRODUCT_SCOPE against baseline ddd1117, OPENAPI_DIFF, TEST_AMENDMENTS site markers; supersedes s33-h1-6-api-scope", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "final tree on baseline ddd1117, the same tree as s33-h1-3-windows-gate-r2", "output": "api-scope-openapi exit 0 | PASS product scope: 51 changed files, all listed; TA-1..TA-11 marked; OPENAPI_DIFF holds | PASS api-scope (PRODUCT_SCOPE, OPENAPI_DIFF, TEST_AMENDMENTS markers)", "fresh": true}
```

H1-7 rerun (supersedes `s33-h1-7-handoff-ac`), after the three handoffs' final-evidence paragraphs were pointed at the A-14 reruns and their Decision Logs became YAML (D-43). Each handoff names every AC of its MEU (`s33-handoff-ac.txt`).

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-7-handoff-ac-r2", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check handoff-ac", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-7 rerun after A-14 and D-43: validate_closeout_artifacts --ac-coverage-only for the MEU-76, MEU-78 and MEU-77 handoffs, plus exec_checks handoff-ac (every full AC id of each MEU in its own handoff); supersedes s33-h1-7-handoff-ac", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "three final handoffs reconciled with s33-h1-2-audit-r3 and s33-h1-3-windows-gate-r2", "output": "handoff-ac-76/78/77: OK: all 3 plan AC(s) present in the handoff | PASS each handoff names all of its MEU's ACs | PASS handoff-ac", "fresh": true}
```

## Execution review corrections

Round 1 of the execution review (`changes_required`, F1 High, AC-77.4 / AC-77.5 / AC-77.6) found that `_remove_partial` re-read `tts.output_path` at cleanup time, while `_work` had written the job's files under the root it read before the WAV write. The correction (implementation-plan §Execution Correction Notes): `_work` builds the WAV and MP3 paths once, before the write, and `_finish` passes exactly those to `_remove_partial`, which no longer reads settings. `CANCEL_RULE`, D-25 and the Done path are unchanged. Test edits: `_Stack.settings` exposes the settings fake (additive) and one appended parametrized test, `test_tts_async.py:458`. No existing assertion changed.

Red first (all 4 cases left the old-root files), then Green 38/38. The gate77 rerun failed only 2 MCP tests outside the correction's reach; A-13 re-observed them without an edit (not reproduced). The per-stage receipts `s33-gate77-*.txt` now hold this rerun (the row 11 run's copies were overwritten). Because source and tests changed, H1-2 and H1-3 are rerun from the start (superseding records in §Audit and §Windows gate).

```json
{"schema_version": "evidence.v1", "check_id": "s33-r1f1-red", "command": "uv run pytest tests/unit/test_tts_async.py -k output_path_changed -q -p no:cacheprovider", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "R1 F1 Red: test_ac_77_5_cleanup_uses_job_paths_after_output_path_changed (wav/mp3 hook x Cancelled/Failed) against the uncorrected services/tts.py; expected to fail", "phase": "red", "exit_code": 1, "result": "fail", "tested_state": "Session 33 final tree plus the R1 F1 test edits only (services/tts.py unchanged)", "output": "4 failed, 34 deselected | status assertions held; each case failed at the file assertion: assert ['<id>.wav'] == [] (wav hook) and assert ['<id>.mp3', '<id>.wav'] == [] (mp3 hook); old-root files left behind (receipt s33-r1f1-red.txt)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-r1f1-green", "command": "uv run pytest tests/unit/test_tts_async.py -q -p no:cacheprovider", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "R1 F1 Green: the whole threaded TTS unit file after the services/tts.py correction", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "corrected tree: the Session 33 final tree plus the R1 F1 edits to services/tts.py and tests/unit/test_tts_async.py", "output": "38 passed (34 before + 4 new) (receipt s33-r1f1-green.txt)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-r1f1-gate77", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate77", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "R1 F1: MEU-77 targeted gate rerun on the corrected tree (pyright, ruff, ui/mcp types and lint, openapi --check, pytest tests/, ui Vitest, MCP Vitest, source audit, Electron tts-generate --repeat-each=5, test_tts_async.py x5)", "phase": "targeted", "exit_code": 1, "result": "fail", "tested_state": "corrected tree: the Session 33 final tree plus the R1 F1 edits to services/tts.py and tests/unit/test_tts_async.py", "output": "py-types, py-lint, ui-types, ui-lint, mcp-types, openapi exit 0 | PASS suite pytest: passed 724 | PASS suite vitest: passed 804 | FAIL suite mcp: 421/423, AC-68.7 refusal_mutated expected undefined to be 'fail'; AC-68.8 expected 4 to be 3 (runner-fake-backend.test.ts) | source-audit rg exit 1 (no hits) | gate77-e2e exit 0 | test_tts_async.py x5: passed 38 each | FAIL gate77 (1 failed step) -> A-13", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-r1f1-mcp-recheck", "command": "npx vitest run tests/audit/runner-fake-backend.test.ts (x5), then npm test (mcp-server/)", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "A-13: re-observe the gate77 MCP failure without any edit", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "corrected tree: the Session 33 final tree plus the R1 F1 edits to services/tts.py and tests/unit/test_tts_async.py", "output": "runner-fake-backend.test.ts: Tests 9 passed (9) on each of 5 runs | full MCP suite: Test Files 26 passed (26), Tests 423 passed (423) | not reproduced", "fresh": true}
```

Round 2 (dispatch `s33-exec-r2`, Codex `gpt-6.1-sol`, high) rechecked the correction on the final tree and returned `approved`, 0 findings, intent achieved yes: F1 closed (R1), no regression of D-25, the Done path or `SHUTDOWN_STOP` (R2), the 912 original test lines unchanged (R3), the rerun records, A-13, A-14 and D-43 sound (R4), and no other blocker (R5). The ledger recorded round 2 of 6. The report was applied verbatim to the canonical review (`.agent/context/handoffs/2026-10-14-backend-robustness-implementation-critical-review.md`); receipts `s33-exec-review-run-r2.txt`, `s33-exec-review.txt`.

```json
{"schema_version": "evidence.v1", "check_id": "s33-h1-8-review-check", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check review-check -Target .agent/context/handoffs/2026-10-14-backend-robustness-implementation-critical-review.md -Mode execution -Cap 6", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "H1-8: the canonical rolling execution review after round 2 was applied verbatim (reviewer frontmatter replaces the canonical frontmatter; the `## Recheck (2026-10-16) — Round 2` body is appended); verdict, agent and round against cap 6", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "canonical review with round 1 (changes_required, F1) and round 2 (approved, 0 findings); ledger s33-execution-2026-10-14-backend-robustness round 2 of 6 recorded approved, blocking 0, intent_achieved yes", "output": "PASS execution review approved, round 2, agent gpt-6.1-sol | PASS review-check", "fresh": true}
```

## Closeout (H2)

- **H2-1** reflection: `docs/execution/reflections/2026-10-14-backend-robustness-reflection.md`; the closeout validator reconciles 45 recorded decisions against 57 Decisions Log rows, all 15 template sections and 7 schema fields present (`s33-reflection.txt`).
- **H2-2** `POST_REVIEW_STATE`: MEU-76/78/77 `approved`, rendered and checked; grouping Session 33 `approved`; focus and metrics updated; `API-UNHANDLED-ERROR-OPAQUE` and `FFMPEG-RESOLUTION-DIVERGENCE` resolved against `windows-gate-result.json`, `MCP-TTS-GENERATE-SYNCHRONOUS` against `mcp-audit-summary.json`; the GATE_EXCLUDED readers rerun: UI docs Vitest 18, MCP docs 7, `test_framework_adoption.py` 91 (`s33-post-review.txt`).
- **H2-3** `lint_task_contract.py`: 24 rows fully checked (`s33-closeout.txt`); rows 0 to 12 and H1-1 to H2-2 are `[x]`.

Merge note: `main` (`c72fc44`) is an ancestor of the baseline `ddd1117`, so this branch is `main` plus the plan commit and the uncommitted Session 33 work. Committing, pushing and merging are the user's decision.

### Commit-message draft

```
feat(api,tts,ffmpeg): backend robustness (Session 33, MEU-76/78/77)

MEU-76: unhandled exceptions are logged once (api.unhandled_error with
request_id, route, method and traceback) and answer a masked 500 that
carries the CORS headers, so the GUI sees the status instead of
"Failed to fetch". yt-dlp extract failures on download add raise a
typed ExtractError (422) whose message reaches the client; the Console
shows request_id and route.

MEU-78: one live ffmpeg resolver (downloader.ffmpeg_path, the bundled
resources/ffmpeg, then PATH; ffprobe beside the resolved ffmpeg; no
cache) serves Convert, TTS MP3, the Dependencies card and yt-dlp
(ffmpeg_location). Health reports the resolved binary and
ffprobe_available, and a Browse change applies without a restart.

MEU-77: POST /tts/generate returns the job at once and a background
worker synthesizes it; DELETE /tts/{id} cancels a running job and
removes the job's partial WAV and MP3 (the paths the job captured,
execution review R1 F1). Restart recovery fails interrupted jobs and
shutdown stops the worker. The MCP tts.generate returns the job id and
the audit's tts.cancel step passes.

OpenAPI diff limited to FfmpegDependencyOut.ffprobe_available and the
generate/cancel descriptions. TEST_AMENDMENTS TA-1 to TA-11.

MCP audit 99/99, tts.cancel FIXED. Windows gate on the final tree:
17/17 stages, pytest 724/0, Vitest 804/804, Electron 139/0/0/0, MCP
423/423. Plan review approved in round 4 and execution review in
round 2 (Codex gpt-6.1-sol).

Resolves API-UNHANDLED-ERROR-OPAQUE, FFMPEG-RESOLUTION-DIVERGENCE and
MCP-TTS-GENERATE-SYNCHRONOUS.
```
