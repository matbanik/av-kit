---
date: "2026-11-12"
project: "youtube-client-runtime"
meu: "MEU-141"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-12-youtube-client-runtime/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-12-youtube-client-runtime-MEU-140-handoff.md"
---

# Handoff: 2026-11-12-youtube-client-runtime-MEU-141-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-141 `infra-ytdlp-js-runtime`. It closes `YTDLP-NO-JS-RUNTIME`.

- **The solver.** `yt-dlp-ejs==0.8.0`, the version yt-dlp's `default` extra pins, is a dependency of `avkit-infra` (`SOLVER_DEP`, D-640 A), and the backend spec collects it (`SOLVER_SPEC`).
- **The runtime.** `JsRuntimeLocator` finds Deno in this order: the `downloader.deno_path` setting, the bundled `resources/deno/deno.exe`, then `deno` on PATH (`DENO_SETTING`, `JS_RUNTIME_LOOKUP`). Every yt-dlp options builder passes it as `js_runtimes` (`JS_RUNTIME_OPTS`).
- **Health and Settings.** `GET /health/dependencies` serves a `js_runtime` block (`RUNTIME_HEALTH`, `RUNTIME_WIRE`). Settings → Dependencies shows it (`RUNTIME_ROW`), and the Deno path is a read-only field with Browse (`DENO_FIELD`).
- **The bundle.** `tools/fetch_deno_windows.ps1` pins Deno v2.9.8 by SHA-256. The installer ships it in `resources/deno` with its MIT licence (`DENO_BUNDLE`, `DENO_LICENCE`), and the packaged smoke checks it (`RUNTIME_SMOKE`).
- **The audit.** `downloader.deno_path` is an audit input key, never an isolation target (`AUDIT_INPUT`).

**Predecessor**: [MEU-140 handoff](2026-11-12-youtube-client-runtime-MEU-140-handoff.md), this session. Row 3s kept MEU-141 in this session (D-641 D, active set `MEU-140 MEU-141`). MEU-140's ACs (AC-140.1 to AC-140.12) and its pins (AC-4, AC-6, AC-122) are owned by that handoff.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-12. Mat ruled the gate decisions ("all recommendations are accepted"): D-640 A, D-641 D and D-642 A. The execution review budget is 37.5M tokens.

**Receipts.** A receipt named by its file name alone (`s66-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s66/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The `deno_path` setting.** The user writes it through `PUT /settings/downloader` (`SettingsPutIn.deno_path`, `schemas/settings.py:26`), the MCP `avkit_settings` set (`mcp-server/src/toolsets/settings.ts:105`), or Browse in Settings (`SettingsPage.tsx:478`). The registry row is `("downloader", "deno_path"): SettingSpec("string", "")` (`services/settings.py:59`), the last downloader key.
- **The one reader.** `wiring.py:164` builds `JsRuntimeLocator(lambda: settings.get("downloader", "deno_path"), bundled_deno())`, so the setting is read at each resolution and a PUT needs no restart (`LIVE_SOURCE`, Session 61 RULE-2). `resolve()` (`js_runtime.py:79`) tries three sources:
  - the setting, through `_setting_path` (`:46`), which refuses a non-str, empty, control-character or non-UTF-8 value without raising or logging it;
  - the bundle (`:84`);
  - `shutil.which("deno")` (`:87`).

  Each candidate must pass `_is_file` (`:39`). Every parse and filesystem call on the value sits inside the error mapping (`JS_RUNTIME_LOOKUP`).
- **The runtime to yt-dlp.** The adapter gets `js_runtime=js_runtime.resolve` (`wiring.py:172`). `_base_opts` calls `_runtime_now()` (`adapter.py:571`) at each build and sets `js_runtimes = {name: {"path": str(path)}}` (`:568`). No runtime, or a source that raises, leaves the key out. Every builder goes through `_base_opts`:
  - both download attempts;
  - `extract_info` with and without options;
  - `extract_video_ids`;
  - `check_sabr_status`;
  - `test_cookies`.
- **The runtime to Health.** `HealthService` takes `js_runtime=lambda: runtime_status(js_runtime)` (`wiring.py:225`, `services/health.py:153`). Its value defaults to `JS_RUNTIME_UNAVAILABLE` when no callable is given (`:285`). `runtime_status` (`js_runtime.py:131`) gives `available`, `name`, `path` and `source` from `resolve()`, `version` from `probe_deno_version` (`:97`, one `deno --version` with a 5 s timeout at `:107`), and `solver` from `solver_available()` (`:123`). The route serializes it through `_js_runtime_out` (`routes/health.py:59`, `:79`), and an unknown source reads as null.
- **What leaves the process.**
  - The path shows in Health and in Settings, as `ffmpeg_path` does. It is never logged.
  - The version probe's output gives only the parsed `X.Y.Z` (AC-141.7).
  - The UI refetches the dependencies after a `deno_path` PUT (`useSettingsPage.ts:72`).
  - The audit treats `downloader.deno_path` as an input key (`classify.ts:34`).

### Row 4: the solver and the Deno files (D-640 A, D-642 A)

- **Edits (CRLF kept).** `.gitignore` gains `packaging/deno-win64/` after `packaging/ffmpeg-win64/`. `packages/infrastructure/pyproject.toml` gains `"yt-dlp-ejs==0.8.0",` after `"yt-dlp",` (`SOLVER_DEP`, D-640 A).
- **Lock.** `uv lock` reads `Resolved 147 packages in 590ms` and `Added yt-dlp-ejs v0.8.0` (`s66-r4-lock.txt`).
  - The lock diff (`s66-r4-lock-diff.txt`, 14 lines) adds only `yt-dlp-ejs`: its dependency rows in `avkit-infra` and its package block.
  - yt-dlp is unchanged at 2026.10.26.
- **Sync.** `uv sync --all-packages` reads `Installed 2 packages in 7ms` (`s66-r4-sync.txt`): `avkit-infra==0.1.0rc3` was rebuilt and `yt-dlp-ejs==0.8.0` added.
- **Pin check.** `s66-r4-check.txt` reads `yt-dlp-ejs 0.8.0`. yt-dlp's pins read `yt-dlp-ejs==0.8.0; extra == 'default'` and `yt-dlp-ejs==0.8.0; extra == 'pin'`, so the installed solver is the one yt-dlp's `default` extra names.
- **Fetches (D-642 A).** `s66-fetch-log.txt` records each request with its URL, destination, status, final host, size and SHA-256:
  - the wheel `yt_dlp_ejs-0.8.0-py3-none-any.whl` from `files.pythonhosted.org`, lock sha256 `79300e5fca7f937a1eeede11f0456862c1b41107ce1d726871e0207424f4bdb4`;
  - `deno-x86_64-pc-windows-msvc.zip` (v2.9.8) to `packaging/deno-win64/deno-pin.zip`, status 200, 42917472 bytes;
  - its published `.sha256sum`, status 200, 177 bytes;
  - `LICENSE.md` at tag v2.9.8 from `raw.githubusercontent.com`, status 200, 1074 bytes.
- **Hashes.** `s66-deno-sha.txt` has four entries, and nothing was extracted or run in this row:
  - `zip: deno-pin.zip sha256=cba84b26e0df5ae7f74fc66b86a95b866872a86292ebd84fa1e959927edd93bf`;
  - the published sum, which is the same (one hex token in the sum file);
  - `zip_match: True`;
  - `licence: LICENSE.md sha256=f62497fffecc0852960c8d3e6934b9db86d16396e9b604072e923892cae3a588`.
- **Row receipt.** `s66/r4-run.txt` ends `deno-win64 ignored: True` and `row 4 exit=0`.

### Row 1b: MEU-141's type-only names (Session 53 RULE-2)

Row 1 recorded the callers in `s66-anchors.txt`. Row 1b re-read them:

- `DependencyHealth(` has 1 site (`services/health.py:266`);
- `DependenciesOut(` has 2 (`routes/health.py:46` and the class);
- `HealthService(` has 13, `bundled_ffmpeg(` 3 and `YouTubeAdapter(` 68.

Every new field and keyword has a default, so no caller changes in this row. `HealthService`'s constructor is unchanged here.

- **`youtube/js_runtime.py` (new, LF).**
  - `JsRuntimeSource` is `setting`, `bundled` or `path`.
  - `JsRuntime` is frozen, with `name`, `path` and `source`.
  - `JsRuntimeLocator(configured, bundle_path)` takes the raw setting reader (`Callable[[], object]`), so every parse and filesystem call on the value can sit inside the locator's error mapping (`JS_RUNTIME_LOOKUP`).
  - Its `resolve()` and `probe_deno_version(path)` are stubs that return None.
- **`youtube/adapter.py` (CRLF kept).** `YouTubeAdapter` takes `js_runtime: Callable[[], JsRuntime or None] or None = None`, which it doesn't read yet. A callable keeps the lookup live at each call (AC-141.4).
- **`domain/health.py` (CRLF kept).** `JsRuntimeStatus` has `available`, `name`, `path`, `version`, `source` and `solver`. `JS_RUNTIME_UNAVAILABLE` has every field None or False. `DependencyHealth.js_runtime`, last, defaults to it.
- **`schemas/health.py` (CRLF kept).** `JsRuntimeOut` has the same six fields, with `source` typed as the three source words or null. `DependenciesOut.js_runtime`, last, defaults to `JS_RUNTIME_OUT_UNAVAILABLE`. The route doesn't set it yet.
- **`wiring.py` (CRLF kept).** `bundled_deno()` returns None. Nothing calls it yet.
- **`openapi.committed.json` (CRLF kept).** Regenerated with `tools/export_openapi.py -o`. Against the pre-row copy:
  - the paths are equal, `JsRuntimeOut` is added, nothing is removed, and only `DependenciesOut` changes;
  - without `js_runtime`, `DependenciesOut` equals its base;
  - the schema's `default` for `js_runtime` lists only `available` and `solver`, because the generator leaves out the null fields. Row 2b's AC-141.8 checks the live body for all six fields.

**Receipts.**

- `s66-types141-py.txt` ends `310 passed in 10.90s`.
- `s66-types141-openapi.txt` holds no drift line, and `--check` exited 0.
- `s66-types141-pyright.txt` reads `0 errors, 0 warnings, 0 informations`.
- `s66-types141-ruff.txt` reads `All checks passed!`.
- `s66/r1b-run.txt` ends `row 1b exit=0`.

### Row 2b: MEU-141 Red

**New files (LF).**

- **`tests/unit/test_js_runtime.py`.**
  - AC-141.2: the lookup order matrix, one id per row, and the setting read at every call.
  - AC-141.3: each unusable value is its own id, and no log line holds the marker.
  - AC-141.7: the version probe's parse, its argv and a timeout of at most 5 s. Each unparsed outcome is its own id.
- **`tests/integration/test_js_runtime_wiring.py`.**
  - AC-141.4: a PUT reaches the adapter's `js_runtime` source and Health, and clearing it falls back to the bundle.
  - AC-141.5: `js_runtimes` is in all seven builders, and absent with no runtime.
  - AC-141.6: Health per source, and none found.
  - AC-141.7's Health half: an unparsed version keeps `available`.
- **`tests/e2e/test_api_js_runtime.py`.** AC-141.1's API half and AC-141.8: all six fields served, the committed snapshot's names, and the bearer still needed.
- **`tests/unit/test_fetch_deno.py`.**
  - AC-141.11 (guard).
  - AC-141.12: the spec, and the smoke verdict per missing field.
  - AC-141.13 and AC-141.14: the fetch script, run offline on fixture files, with a licence mismatch case beside the archive one.
- **`ui/tests/unit/settings-runtime.test.ts`.** AC-141.1's UI half, AC-141.9 and AC-141.10. Every lookup is a query, and the hook harness records the error name and expects `none`.
- **`mcp-server/tests/settings-runtime.test.ts`.** AC-141.1's MCP half.
- **`tools/smoke_packaged_runtime.py` (`RUNTIME_SMOKE`).** It imports `Backend` from `smoke_packaged_tts`. It runs in a fresh temp folder with dead proxies and a PATH without any `deno.exe` folder, and stops the backend through `Backend.stop()` in a `finally`.

**Edits (CRLF kept).**

- `ui/tests/e2e/test-ids.ts` gains `DEPS_JS_RUNTIME_ROW` and `BROWSE_DENO_BTN`, in one additive block at the end (S9).
- `mcp-server/tests/audit/isolation.test.ts`: the `:35` pin now also holds `downloader.deno_path`, and `:31` and `:36` are unchanged. A `describe("AC-141.16 AUDIT_INPUT")` block is appended.
- **Departure, D-658.** The plan's pin row said that the e2e dependency fakes build unchanged.
  - **Why that failed.** They are `SimpleNamespace` objects, not `DependencyHealth`, so a dataclass default can't reach them. Row 5's route read would then raise in every e2e health test.
  - **The repair.** `tests/e2e/api_fakes.py`, `test_api_auth.py` and `test_api_health_settings.py` each gain a `js_runtime` `SimpleNamespace` with the unavailable values, under a `FIXTURE_REPAIRS (Session 66, MEU-141)` comment. No assertion changes. D-658 is in the plan YAML.

### Row 5: MEU-141 Green

**Code (CRLF kept unless marked LF).**

- **`DENO_SETTING`.** The registry row is now the last downloader key. `SettingsPutIn`, the MCP `SETTINGS_SCHEMA` and `settingsLeaves` gain `deno_path`. The UI settings schema gains it as a nullable string.
- **`AUDIT_INPUT`.** `ISOLATION_INPUT_KEYS` in `classify.ts` adds `downloader.deno_path`.
- **`JS_RUNTIME_LOOKUP` and `probe_deno_version` (LF).** These are as in §Where values go.
- **`JS_RUNTIME_OPTS`.** `_base_opts` sets `js_runtimes` from `_runtime_now()`.
- **`wiring.py`.**
  - `bundled_deno()` gives the frozen sibling `deno/deno.exe`.
  - The `# LIVE_SOURCE` locator reads the setting at each call.
  - The adapter gets `js_runtime.resolve`, and Health gets `runtime_status(js_runtime)`.
- **`RUNTIME_HEALTH` and `RUNTIME_WIRE`.** `HealthService` takes the `js_runtime` callable, and the route serializes it through `_js_runtime_out`.
- **`RUNTIME_ROW` and `DENO_FIELD` (D-648).**
  - The Settings page gains a `deps-js-runtime-row` after FFprobe. It shows the name, version, source and path, or the no-runtime text.
  - It also gains a read-only Deno path row with `browse-deno-btn`.
  - A PUT of `deno_path` refetches the dependencies.
- **`SOLVER_SPEC`.** `packaging/avkit-backend.spec` adds `yt_dlp_ejs`, its submodules and its data files.
- **`DENO_BUNDLE`.**
  - `tools/fetch_deno_windows.ps1` (new, LF) pins the v2.9.8 archive and the licence by SHA-256, using the values from `s66-deno-sha.txt`.
  - `ui/electron-builder.yml` copies `packaging/deno-win64` to `resources/deno` with the filters `!*.zip` and `!*.sha256sum`. The second filter goes beyond the plan text: it keeps out of the installer the published sum file that row 4 fetched beside the zip.
- **`DENO_LICENCE`.**
  - `tools/generate_third_party_licenses.py` (LF) lists `resources/deno/LICENSE.md: Deno`.
  - `packaging/THIRD_PARTY_NOTICES.md` gains a `## Deno 2.9.8` section.
- **The OpenAPI snapshot.** `openapi.committed.json` is regenerated, and `--check` exits 0 (`s66-r5-openapi.txt`).
- **Departure, D-659.** The UI lint refuses three unused `depsGets` lines in `ui/tests/unit/settings-runtime.test.ts` (LF), so they are removed. No assertion changes.

**Packaging.**

| Step | Receipt | Result |
|---|---|---|
| Extract | `s66-r5-fetch.txt` | `fetch_deno_windows.ps1 -ExtractOnly` reads `PASS: FETCH_DENO sha256=CBA84B...`, exit 0 |
| Version | `s66-r5-deno-version.txt` | `deno 2.9.8 (stable, release, x86_64-pc-windows-msvc)`, exit 0 |
| Onedir build | `s66-r5-package.txt` | exit 0. `_internal/yt_dlp_ejs/yt/solver/` holds `core.min.js` and `lib.min.js` |
| Deno copy | `packaging/dist/deno/` | `deno.exe` (98,081,568 bytes) and `LICENSE.md`, without the zip |
| Smoke (AC-141.12, Green half) | `s66-smoke-green.txt` | `PASS: smoke-runtime source=bundled version=2.9.8 solver=True`. The backend is stopped |
| Licences | `s66-r5-licences.txt` | exit 0. `THIRD_PARTY_LICENSES.txt` names yt-dlp-ejs 0.8.0 and `resources/deno/LICENSE.md: Deno`, and holds no mutagen |

**Installer (AC-141.15, D-650, D-660).**

- **The first run failed.** D-650's `npm --prefix ui run dist` stopped at `build:picker` with NU1100 for the three win-x64 runtime packs at 8.0.34 (`s66-r5-nsis.txt`, exit 1).
  - NuGet has no package source on this machine, and its cache stops at 8.0.33.
  - `clean:out` had already deleted `native/region-picker/publish`.
- **The rerun (D-660 A, ruled by Mat).** The 2026-11-09 picker was copied back from `ui/dist/win-unpacked/resources/region-picker`: 243 files, with the same tree SHA-256 on both sides. Then dist's other steps ran unchanged (`s66-r5-nsis-d660.txt`): `exit_build=0`, `exit_bundle=0` and `exit_builder=0`.
- **The size.** `s66-r5-size.txt` reads `installer: av-kit-Setup-0.1.0-rc.3.exe bytes: 371477462 rc.2 bytes: 340362828 budget bytes: 500000000`. That is 31,114,634 bytes over rc.2 and under S13's 500 MB.
- **The contents.** `win-unpacked/resources/deno/` holds `deno.exe` (98,081,568 bytes) and `LICENSE.md` (1,074 bytes).
- **The dev picker.** `native/region-picker/publish` now holds the 2026-11-09 build, not a rebuild from source. The next real `dist` rebuilds it once NuGet resolves 8.0.34.

**Receipts.** `run_row.py 5` exits 0 (`s66-r5-row.txt`).

| Check | Receipt | Result |
|---|---|---|
| Python tests | `s66-py-green-141.txt` | `445 passed in 36.65s` |
| UI tests | `s66-ui-green-141.txt` | `Tests  105 passed (105)` |
| MCP tests | `s66-mcp-green-141.txt` | `Tests  230 passed (230)` |
| UI types | `s66-r5-ui-types.txt` | exit 0 |
| pyright | `s66-r5-pyright.txt` | `0 errors, 0 warnings, 0 informations` |
| ruff | `s66-r5-ruff.txt` | `All checks passed!` |
| Callers | `s66-r5-callers.txt` | `408 passed in 44.96s`, exit 0. These are row 1's callers, plus the `real_stack` users |

### Row 6: spec, register and status (both MEUs)

- **S3.** HEAD is still `0553779`, and every changed path is this session's. The five record files were clean before their copy to `s66/pre-status/`.
- **Spec (D3, CRLF kept).**
  - `docs/build-plan/02-infrastructure.md`: the SABR client fallback line names `ATTEMPT_OPTS` and `RETRY_ONCE`, the Solver row records D-640 A, and each residual section gains a `Delivered (Session 66)` note.
  - `06-gui.md`: the key table gains `downloader.deno_path`, and the Dependencies card gains the JavaScript runtime.
  - `07-distribution.md` gains `## Deno (locked)`, with the probe order and the installer size.
- **Register.** `s66-resolve.txt` reads `parsed fields changed: 10` and `issue-resolve: 0 problem(s)`. Both issues are `resolved`. When row 6 ran, the live probes stood as an open manual check under D-642. H1-2m has since recorded them (see the MEU-140 handoff). `issue_triage.py render` and `triage` exit 0.
- **Status.** `meu_status.py update` set MEU-140 and MEU-141 to `ready_for_review` with this plan. Its full re-dump re-wrapped other MEUs' entries, so the file keeps the pre-status bytes with only the two entries changed (D-661).
- **S15.** `s66-r6-prestatus-diff.txt` was taken before D-661. Against the copies, the changes are:
  - the two entries in `meu-status.yaml`;
  - their two status cells in `meu-registry.md`;
  - the Total row in `BUILD_PLAN.md`;
  - the two issues in `known-issues.yaml`;
  - grouping row 66, now `executed` with this plan folder.
- **Receipt.** `run_row.py 6` exits 0 (`s66-r6-row.txt`). `s66-r6-status.txt` reads `active-set records: MEU-140 MEU-141; 0 problem(s): []`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-141.1 | behaviour | `DENO_SETTING`: the key exists with default `""`, last in the downloader namespace, and the API, MCP and UI schemas take it. An unknown leaf is still refused | Human-approved: D-540 (the setting) | `tests/e2e/test_api_js_runtime.py:84`, `:94`, `:100`, `:111`; `ui/tests/unit/settings-runtime.test.ts:189`, `:194`; `mcp-server/tests/settings-runtime.test.ts:12`, `:19`, `:24` | ✅ |
| AC-141.2 | behaviour | `JS_RUNTIME_LOOKUP`'s order over the input matrix, one parametrize id per row. A setting that names a missing file never wins | Human-approved: D-540; Local Canon: 07:159-164 | `tests/unit/test_js_runtime.py:82`, `:107`, `:114`, `:124`, `:134`, `:157` | ✅ |
| AC-141.3 | behaviour | Every unusable setting value falls through without raising and without logging the value. Each value is its own id (Session 58 RULE-2, Session 53 RULE-1) | Local Canon | `test_js_runtime.py:187`, `:199` | ✅ |
| AC-141.4 | behaviour | A `deno_path` PUT reaches the next adapter call and the next Health read without a restart (`LIVE_SOURCE`). Clearing it falls back to the bundled or PATH runtime | Local Canon: Session 61 RULE-2 | `tests/integration/test_js_runtime_wiring.py:116`, `:143` | ✅ |
| AC-141.5 | behaviour | `JS_RUNTIME_OPTS` in every options builder: both download attempts, `extract_info` with and without options, `extract_video_ids`, `check_sabr_status` and `test_cookies`. With no runtime, the key is absent | Human-approved: D-540 (`js_runtimes`) | `test_js_runtime_wiring.py:229`, `:240` | ✅ |
| AC-141.6 | behaviour | `RUNTIME_HEALTH`: a runtime found through each source gives `available`, `name="deno"`, the path and the source. None found gives `available=False`, `path=None` and `source=None` | Human-approved: D-540 | `test_js_runtime_wiring.py:251`, `:276` | ✅ |
| AC-141.7 | behaviour | The version probe parses `deno 2.9.8 (...)` to `2.9.8`. A timeout, an `OSError`, garbage and empty output give `None` and keep `available`. No output text but the parsed version leaves the probe | Local Canon | `test_js_runtime.py:243`, `:270`, `:282`; `test_js_runtime_wiring.py:295` | ✅ |
| AC-141.8 | behaviour | `GET /health/dependencies` serves `js_runtime` with all six fields, and the OpenAPI check passes on the regenerated snapshot. The snapshot's delta from `baseline.sha` is the one `RUNTIME_WIRE` names (`schemas added or removed: ['JsRuntimeOut']`, H1-4). The route still needs the bearer token | Local Canon: 02 Health row | `test_api_js_runtime.py:120`, `:140`, `:148`; gate `openapi` | ✅ |
| AC-141.9 | behaviour | `RUNTIME_ROW` in Settings → Dependencies, found and none found. The none-found text names what it costs and the fix (D-648) | Human-approved: D-540; Local Canon: 02 Health row | `settings-runtime.test.ts:201`, `:212` | ✅ |
| AC-141.10 | behaviour | `DENO_FIELD`: the read-only field and Browse render, and a `deno_path` PUT refetches the dependencies. A cancelled Browse PUTs nothing, and a quality PUT doesn't refetch | Local Canon: AC-78.8, AC-78.9 | `settings-runtime.test.ts:222`, `:245`, `:259`, `:274` | ✅ |
| AC-141.11 | guard | `SOLVER_DEP`: `yt_dlp_ejs` imports, and its installed version equals the pin in yt-dlp's `default` extra (an offline read of `importlib.metadata`). The pin reader refuses a fixture whose pin differs. Row 4 installed the solver, so it passed where row 2b wrote it | Research-backed: EJS wiki; D-640 | `tests/unit/test_fetch_deno.py:52`, `:61` | ✅ |
| AC-141.12 | behaviour | `SOLVER_SPEC` and `RUNTIME_SMOKE`: the spec names the solver, and the onedir smoke reports `source == "bundled"` and `solver` True on a fresh build. On the pre-session onedir it reports the missing `js_runtime` field (Session 51 D-315) | Research-backed: EJS wiki; Local Canon: 02 Tests row | `test_fetch_deno.py:89`, `:149`; `s66-smoke-red.txt`, `s66-smoke-green.txt`; gate `runtime-smoke` | ✅ |
| AC-141.13 | behaviour | `DENO_LICENCE` and `DENO_BUNDLE`: `OTHER_LISTS` names `resources/deno/LICENSE.md`, `THIRD_PARTY_NOTICES.md` has the Deno row, and `electron-builder.yml` copies `packaging/deno-win64` to `deno` without `*.zip`. The licence generator passes on the fresh build and still refuses a GPL-class package off the allow list | Human-approved: D-540 (MIT notice) | `test_fetch_deno.py:160`, `:178`, `:187`, `:196`, `:210`, `:218`; gate `licences` | ✅ |
| AC-141.14 | behaviour | `fetch_deno_windows.ps1` refuses an empty URL (exit 2), a non-hex SHA (exit 2) and a mismatched archive or licence SHA (exit 3), and extracts a matching archive. A SHA mismatch leaves no `deno.exe`. The tests run offline with `-ExtractOnly` on fixture files | Local Canon: `tools/fetch_ffmpeg_windows.ps1` | `test_fetch_deno.py:274`, `:281`, `:288`, `:296`, `:303` | ✅ |
| AC-141.15 | measurement | The NSIS installer built with Deno is 371,477,462 bytes, under the 500 MB budget (07:444). rc.2 (`ui/dist/av-kit-Setup-0.1.0-rc.2.exe`) is 340,362,828 bytes | Human-approved: D-540 (size check); Local Canon: 07:33, :444; D-650, D-660 | `s66-r5-size.txt` | ✅ |
| AC-141.16 | behaviour | `AUDIT_INPUT`: `ISOLATION_INPUT_KEYS` holds `downloader.deno_path`, and `isolationKeys(SETTINGS_SCHEMA)` still equals the seven output keys. `isolationKeys` never contains `downloader.deno_path` | Local Canon: AC-68.8 | `mcp-server/tests/audit/isolation.test.ts:83`, `:88` | ✅ |
| AC-68 (cross-ref) | regression | Moved pin: AC-68.8 (`isolation.test.ts:35`) now expects `ISOLATION_INPUT_KEYS` sorted to be `cookie_file_path`, `deno_path`, `ffmpeg_path`. `:31` and `:36` are unchanged. It failed in row 2b and passes from row 5 | plan §Pins that move | `mcp-server/tests/audit/isolation.test.ts:35`; gate `mcp-tests` | ✅ |
| AC-51, AC-81 (cross-ref) | regression | The byte-hash guards over `ui/tests/e2e/test-ids.ts`: AC-51.6 (`layout-primitives.test.ts:200`) and AC-81.13 (`capture-action-row.test.ts:710`). Row 2b added one block at the end and ran both in their own check (S9): `Tests  28 passed (28)` (`s66-r2b-testids.txt`) | plan §Test ids | `ui/tests/unit/layout-primitives.test.ts:200`, `ui/tests/unit/capture-action-row.test.ts:710`; gate `ui-tests` | ✅ |
| AC-78 (cross-ref) | regression | Guards that `DENO_FIELD` follows: AC-78.8 (`settings-deps-refresh.test.ts:52`), where an `ffmpeg_path` PUT refetches the dependencies and a quality PUT doesn't, and AC-78.9 (`ui/tests/e2e/settings.test.ts:643`). Unchanged, and they pass in the gate | plan §Guards | `ui/tests/unit/settings-deps-refresh.test.ts:52`; `ui/tests/e2e/settings.test.ts:643`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-25, AC-72, AC-110, AC-113 (cross-ref) | regression | The packaging pins, which check subsets, so they don't move: AC-72.6's spec (`test_packaging_backend.py`); AC-25.2 (`test_packaging_installer.py:33`), AC-72.7's notices (`:208`, `:274`) and AC-113's fetch exits; AC-110's resources and licence list (`test_release_packaging.py`, `test_generate_third_party_licenses.py`). `git diff --stat 0553779` lists none of these files, and all pass after row 5 | plan §Guards | `tests/unit/test_packaging_backend.py`, `test_packaging_installer.py`, `test_release_packaging.py`, `test_generate_third_party_licenses.py`; gate `py-tests` | ✅ |
| AC-140, AC-6, AC-122 (cross-ref) | regression | MEU-140's twelve ACs, and its AC-6.6, AC-6.16 and AC-122.6 pins, are owned by the [MEU-140 handoff](2026-11-12-youtube-client-runtime-MEU-140-handoff.md). AC-141.5 covers both of MEU-140's attempts and the add-time extract | plan §MEU-140 | MEU-140 handoff | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-141.1 to AC-141.10, AC-141.12 to AC-141.14 (Python) | `48 failed, 26 passed in 4.86s`, exit 1 (`s66-py-red-141.txt`). Decisive lines: `At index 0 diff: None != 'deno'` ×24; `assert (None, None, False) == ('deno', 'bundled', True)` ×16; `AssertionError: missing fetch_deno_windows.ps1` ×5; `assert (None, None, False) == ('deno', 'setting', True)` ×5; `assert 'deno_path' in {...get_namespace('downloader')}` ×5; `('deno','path',True)` ×3 | `445 passed in 36.65s` (`s66-py-green-141.txt`); gate `py-tests` | `test_js_runtime.py:82-282`, `test_js_runtime_wiring.py:116-295`, `test_api_js_runtime.py:84-148`, `test_fetch_deno.py:89-303` |
| AC-141.1, AC-141.9, AC-141.10 (UI) | `Tests  6 failed \| 2 passed (8)`, exit 1 (`s66-ui-red-141.txt`). Decisive lines: `browse-deno-btn: expected null not to be null`; `deps-js-runtime-row: expected null not to be null`; `settings-leaf-deno_path: expected null not to be null`; `expected -1 to be greater than or equal to 0`; `expected false to be true` | `Tests  105 passed (105)` (`s66-ui-green-141.txt`); gate `ui-tests` | `settings-runtime.test.ts:189-274` |
| AC-141.1, AC-141.16 and the AC-68.8 pin (MCP) | `Tests  5 failed \| 7 passed (12)`, exit 1 (`s66-mcp-red-141.txt`): three in `isolation.test.ts` (the moved `:35` pin and both AC-141.16 tests) and two in `settings-runtime.test.ts`. Decisive lines: `expected [ 'downloader.cookie_file_path', …(1) ] to deeply equal [ …(2) ]`; `expected [ 'downloader.ffmpeg_path', …(1) ] to include 'downloader.deno_path'`; `expected [ 'downloader.path', …(7) ] to not include 'downloader.deno_path'`; `expected [ 'path', 'ffmpeg_path', …(9) ] to include 'deno_path'`; `expected false to be true` | `Tests  230 passed (230)` (`s66-mcp-green-141.txt`); gate `mcp-tests` | `mcp-server/tests/settings-runtime.test.ts:12-24`, `isolation.test.ts:35`, `:83`, `:88` |
| AC-141.12 (packaged smoke) | `smoke-runtime: missing js_runtime` on the pre-session onedir in `packaging/dist/avkit-backend` (`s66-smoke-red.txt`) | `PASS: smoke-runtime source=bundled version=2.9.8 solver=True` (`s66-smoke-green.txt`); gate `runtime-smoke` | `tools/smoke_packaged_runtime.py` |
| AC-141.11 | A guard: row 4 installed the solver. Row 2b's guard run: `85 passed, 20 deselected in 14.16s` (`s66-r2b-guard-py.txt`, AC-141.11 and the MEU-140 tests) | Row 5 and gate `py-tests` | `test_fetch_deno.py:52`, `:61` |

- **red-check.** `s66-red-141-check.txt` reads `red-check: 3 receipt(s), 16 required test(s), 0 problem(s)`. Every failing block failed by assertion alone.
- **The byte-hash guards.** The check that ran AC-51.6 and AC-81.13 alone after the `test-ids.ts` edit reads `Tests  28 passed (28)` (`s66-r2b-testids.txt`).

### The runtime, live (H1-2m)

The live probes are recorded in full in the [MEU-140 handoff](2026-11-12-youtube-client-runtime-MEU-140-handoff.md) §Live probes. For this MEU, every one of the six lines in `s66-probes.txt` reads:

- `runtime_source` `bundled`, which is the pinned `packaging/deno-win64/deno.exe`;
- `runtime_version` `2.9.8`;
- `solver` true.

Four probes downloaded through the real adapter with `js_runtimes` set: both public videos, the logged-in probe and the member's probe.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-4-solver-deno", "command": "env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py 4 > C:/Temp/av-kit/s66/r4-run.txt (task.md row 4's Validation cell; receipts C:/Temp/av-kit/s66-r4-lock.txt, s66-r4-lock-diff.txt, s66-r4-sync.txt, s66-fetch-log.txt, s66-deno-sha.txt and s66-r4-check.txt)", "scope": "Row 4: SOLVER_DEP (yt-dlp-ejs==0.8.0 in avkit-infra, locked and synced), the solver pin read against yt-dlp's default extra, and the Deno v2.9.8 archive, published sum and licence fetched and hashed (D-640 A, D-642 A)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 4", "output": "Resolved 147 packages in 590ms; Added yt-dlp-ejs v0.8.0; lock diff 14 lines, yt-dlp-ejs only; Installed 2 packages in 7ms; yt-dlp-ejs 0.8.0, yt-dlp pins yt-dlp-ejs==0.8.0; extra == 'default' and yt-dlp-ejs==0.8.0; extra == 'pin'; zip: deno-pin.zip sha256=cba84b26e0df5ae7f74fc66b86a95b866872a86292ebd84fa1e959927edd93bf; published sum the same; zip_match: True; licence: LICENSE.md sha256=f62497fffecc0852960c8d3e6934b9db86d16396e9b604072e923892cae3a588; deno-win64 ignored: True; row 4 exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-1b-types-141", "command": "env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py 1b > C:/Temp/av-kit/s66/r1b-run.txt (task.md row 1b's Validation cell; receipts C:/Temp/av-kit/s66-types141-py.txt, s66-types141-openapi.txt, s66-types141-pyright.txt and s66-types141-ruff.txt)", "scope": "Row 1b: MEU-141's type-only names (JsRuntime, JsRuntimeLocator, JsRuntimeStatus, JsRuntimeOut, the js_runtime keyword and field defaults, bundled_deno) and the regenerated OpenAPI snapshot", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 1b", "output": "310 passed in 10.90s; export_openapi --check exit 0, no drift line; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; row 1b exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-2b-red-141", "command": "env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py 2b > C:/Temp/av-kit/s66/row2b-run.txt (task.md row 2b's Validation cell; receipts C:/Temp/av-kit/s66-py-red-141.txt, s66-ui-red-141.txt, s66-mcp-red-141.txt with their .exit files, s66-red-141-check.txt, s66-smoke-red.txt, s66-r2b-guard-py.txt and s66-r2b-testids.txt)", "scope": "MEU-141 Red: AC-141.1 to .10 and .12 to .16 in Python, UI and MCP against the row 1b stubs, the AC-68.8 pin, the packaged smoke on the pre-session onedir, AC-141.11 as a passing guard, and the byte-hash guards after the test-ids edit", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 2b", "output": "Python 48 failed, 26 passed in 4.86s (child exit 1); UI Tests 6 failed | 2 passed (8) (child exit 1); MCP Tests 5 failed | 7 passed (12) (child exit 1). Decisive: At index 0 diff: None != 'deno' x24; assert (None, None, False) == ('deno', 'bundled', True) x16; AssertionError: missing fetch_deno_windows.ps1 x5; browse-deno-btn: expected null not to be null; expected [ 'downloader.ffmpeg_path', ...(1) ] to include 'downloader.deno_path'. red-check: 3 receipt(s), 16 required test(s), 0 problem(s). smoke-runtime: missing js_runtime. Guard 85 passed, 20 deselected in 14.16s. Test ids Tests 28 passed (28). row 2b exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-5-green-141", "command": "env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py 5 > C:/Temp/av-kit/s66-r5-row.txt (task.md row 5's Validation cell; receipts C:/Temp/av-kit/s66-py-green-141.txt, s66-ui-green-141.txt, s66-mcp-green-141.txt, s66-r5-ui-types.txt, s66-r5-pyright.txt, s66-r5-ruff.txt, s66-r5-openapi.txt, s66-smoke-green.txt, s66-r5-size.txt and s66-r5-callers.txt)", "scope": "MEU-141 Green: DENO_SETTING, JS_RUNTIME_LOOKUP, JS_RUNTIME_OPTS, RUNTIME_HEALTH, RUNTIME_WIRE, RUNTIME_ROW, DENO_FIELD, SOLVER_SPEC, DENO_BUNDLE, DENO_LICENCE, RUNTIME_SMOKE, AUDIT_INPUT, and the NSIS size under D-650 and D-660", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 5", "output": "445 passed in 36.65s; UI Tests 105 passed (105); MCP Tests 230 passed (230); ui-types exit 0; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; openapi --check exit 0; PASS: smoke-runtime source=bundled version=2.9.8 solver=True; installer: av-kit-Setup-0.1.0-rc.3.exe bytes: 371477462 rc.2 bytes: 340362828 budget bytes: 500000000; callers 408 passed in 44.96s; row 5 exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-6-records", "command": "env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py 6 > C:/Temp/av-kit/s66-r6-row.txt (task.md row 6's Validation cell; receipts C:/Temp/av-kit/s66-resolve.txt, s66-r6-issues.txt, s66-r6-render.txt and s66-r6-status.txt; pre-status copies in C:/Temp/av-kit/s66/pre-status/)", "scope": "Row 6 for both MEUs: the 02, 06 and 07 spec text (D3), both issues resolved, MEU-140 and MEU-141 at ready_for_review (D-661), and S15's record diff", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 6", "output": "parsed fields changed: 10; issue-resolve: 0 problem(s); meus: MEU-140 ready_for_review, MEU-141 ready_for_review; issues: DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT resolved, YTDLP-NO-JS-RUNTIME resolved; 02 notes: 2; active-set records: MEU-140 MEU-141; 0 problem(s): []; Drift check passed (142 MEUs, 12 phases); OK: known-issues.md is up-to-date; row 6 exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-h1-3-h1-4", "command": "env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py H1-3 > C:/Temp/av-kit/s66-h13-row.txt; env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py H1-4 > C:/Temp/av-kit/s66-h14-row.txt", "scope": "H1-3: the MEU and issue records after the gate, and current-focus.md. H1-4: the OpenAPI delta from baseline.sha is RUNTIME_WIRE's one schema", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30", "output": "meus: MEU-140 ready_for_review, MEU-141 ready_for_review; issues resolved; active-set records: MEU-140 MEU-141; 0 problem(s): []; row H1-3 exit=0; schemas added or removed: ['JsRuntimeOut']; active-set openapi: MEU-140 MEU-141; 0 problem(s): []; row H1-4 exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-12-youtube-client-runtime/session-gate.ps1 *> C:/Temp/av-kit/s66-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit, row receipt C:/Temp/av-kit/s66-h12-row.txt; per-step receipts C:/Temp/av-kit/s66-D6-*.txt)", "scope": "H1-2: the registered full gate. Static: py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest, active-set. Full: py-tests, openapi, ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render, issues-render. Runtime: ui-electron, package-build, deno-copy, runtime-smoke, licences. Identity before and after. Skipped with reasons: mcp-audit, build-record, live-probes, real-ffmpeg", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; ui-types exit 0; ui-lint exit 0; task-contract OK: 28 row(s), 26 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 72 outside scope: [] head moved (S3): False; red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; active-set exit 0; py-tests 2309 passed, 37 warnings in 186.14s (0:03:06); openapi exit 0; ui-tests Test Files 121 passed (121), Tests 1293 passed (1293); ui-build exit 0; mcp-types exit 0; mcp-build exit 0; mcp-tests Test Files 36 passed (36), Tests 525 passed (525); state-render Drift check passed (142 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 24 passed (38.2s); package-build exit 0; deno-copy: deno.exe sha256=924397800533d3eb0ed0c889b20ad70e18b970d93acd8135bc043f425e528266, files ['LICENSE.md', 'deno.exe']; runtime-smoke PASS: smoke-runtime source=bundled version=2.9.8 solver=True; licences THIRD_PARTY_LICENSES.txt: 1103368 bytes; tested_state before = after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-h1-2m-runtime", "command": "uv run --no-sync python C:/Temp/av-kit/s66/live-probe.py --label L --url U --cookies off|browser [--browser firefox] [--private], once per probe on Mat's words; then task.md row H1-2m's Validation cell *> C:/Temp/av-kit/s66-probes-check.txt (row receipt C:/Temp/av-kit/s66-h12m-row.txt; probe records C:/Temp/av-kit/s66-probes.txt)", "scope": "H1-2m for MEU-141: the runtime source, version and solver that the real adapter used in each live probe (D-642 A)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30", "output": "6 probe lines, each runtime_source bundled, runtime_version 2.9.8, solver true; 4 passed downloads with js_runtimes set; row H1-2m exit=0"}
```

### Quality Gate Results

`s66-gate-h1-2` (H1-2) is the fresh full record, the same run that the MEU-140 handoff cites. Its last line is:

> session-gate: all steps exit 0

- **One run.** The gate passed every step on its first run (`s66-gate-h1.txt`, row receipt `s66-h12-row.txt`).
- **The MEU-141 steps.**
  - `package-build` rebuilt the onedir with the solver.
  - `deno-copy` placed `deno.exe` (sha256 `924397800533d3eb0ed0c889b20ad70e18b970d93acd8135bc043f425e528266`) and `LICENSE.md` (sha256 `f62497ff…a588`, as row 4 fetched it) beside it.
  - `runtime-smoke` read `PASS: smoke-runtime source=bundled version=2.9.8 solver=True`.
  - `licences` wrote `THIRD_PARTY_LICENSES.txt: 1103368 bytes`.
- **Suites.**
  - pytest: 2309 passed, the baseline's 2152 plus 157.
  - UI: 1293 passed in 121 files, the baseline's 1285 in 120 plus `settings-runtime.test.ts`'s 8.
  - MCP: 525 passed in 36 files, the baseline's 520 in 35 plus 5: three in `settings-runtime.test.ts` and two AC-141.16 tests.
  - Electron E2E: 24 passed, AC-78.9 among them.
- **Static.**
  - pyright, ruff, the UI typecheck and eslint, and lint_task_contract all pass.
  - scope-paths found 72 changed paths, none outside scope.
  - The red-check selftest and `active-set.py check` pass.
- **Skipped.** Each skip has a reason in the gate:
  - `mcp-audit`: it needs the live network;
  - `build-record`: no release (row 5 built the NSIS installer, D-650);
  - `live-probes`: a manual check after the gate (H1-2m);
  - `real-ffmpeg`: no FFmpeg change.
- **Identity.**
  - The tested_state was the same before and after: `055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30`.
  - `packaging/deno-win64/` and `packaging/dist/` are ignored and outside it.
- **Warnings.** 37, the same as the baseline.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/src/avkit_infra/youtube/js_runtime.py` | new | `JsRuntime`, `JsRuntimeLocator`, `probe_deno_version`, `solver_available`, `runtime_status`. LF, 146 lines |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modified | The `js_runtime` keyword, `_runtime_now` and `js_runtimes` in `_base_opts` (and MEU-140's attempt sequence) |
| `packages/infrastructure/pyproject.toml`, `uv.lock` | modified | `yt-dlp-ejs==0.8.0` (`SOLVER_DEP`) |
| `packages/core/src/avkit_core/domain/health.py`, `services/health.py` | modified | `JsRuntimeStatus`, `JS_RUNTIME_UNAVAILABLE`, `DependencyHealth.js_runtime`, `HealthService`'s `js_runtime` callable |
| `packages/core/src/avkit_core/services/settings.py` | modified | The `downloader.deno_path` registry row |
| `packages/api/src/avkit_api/schemas/health.py`, `schemas/settings.py`, `routes/health.py`, `wiring.py` | modified | `JsRuntimeOut`, `SettingsPutIn.deno_path`, `_js_runtime_out`, `bundled_deno` and the `LIVE_SOURCE` locator |
| `openapi.committed.json` | modified | `JsRuntimeOut` and `DependenciesOut.js_runtime` |
| `mcp-server/src/toolsets/settings.ts`, `mcp-server/scripts/audit/classify.ts` | modified | `deno_path` in `SETTINGS_SCHEMA` and `settingsLeaves`, and in `ISOLATION_INPUT_KEYS` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx`, `settings-schemas.ts`, `useSettingsPage.ts` | modified | `deps-js-runtime-row`, the Deno path field with Browse, the schema leaf and the refetch |
| `ui/tests/e2e/test-ids.ts` | modified | `DEPS_JS_RUNTIME_ROW` and `BROWSE_DENO_BTN`, in one block at the end |
| `packaging/avkit-backend.spec`, `ui/electron-builder.yml`, `packaging/THIRD_PARTY_NOTICES.md`, `tools/generate_third_party_licenses.py` | modified | `SOLVER_SPEC`, `DENO_BUNDLE` and `DENO_LICENCE` |
| `tools/fetch_deno_windows.ps1`, `tools/smoke_packaged_runtime.py` | new | The pinned fetch and the packaged smoke. LF, 77 and 135 lines |
| `.gitignore` | modified | `packaging/deno-win64/` |
| `tests/unit/test_js_runtime.py`, `tests/integration/test_js_runtime_wiring.py`, `tests/e2e/test_api_js_runtime.py`, `tests/unit/test_fetch_deno.py` | new | The Python tests for AC-141.1 to .14. LF: 292, 307, 153 and 308 lines |
| `ui/tests/unit/settings-runtime.test.ts`, `mcp-server/tests/settings-runtime.test.ts` | new | AC-141.1, .9 and .10. LF: 282 and 28 lines |
| `mcp-server/tests/audit/isolation.test.ts` | modified | The AC-68.8 pin and the AC-141.16 block |
| `tests/e2e/api_fakes.py`, `tests/e2e/test_api_auth.py`, `tests/e2e/test_api_health_settings.py` | modified | D-658's `js_runtime` fixture repairs |
| `docs/build-plan/06-gui.md`, `docs/build-plan/07-distribution.md` | modified | `downloader.deno_path`, the Dependencies row and `## Deno (locked)` (row 6) |
| `docs/execution/plans/2026-11-12-youtube-client-runtime/session-gate.ps1` | modified in this session | `tests/e2e/api_fakes.py` in `$scopePaths` (D-662) |

The MEU-140 handoff lists the files that row 6 shared and MEU-140's own files.

Line endings were measured with Python bytes before each edit and kept:

- **CRLF.** Most modified code, `test-ids.ts`, `isolation.test.ts`, the e2e fakes, 06 and 07.
- **LF.** `uv.lock` and `tools/generate_third_party_licenses.py`.
- **New files** are LF.

These are never committed: `packaging/deno-win64/` (ignored), `packaging/dist/`, and the installer folder in the session subfolder.

```diff
 # adapter.py, _base_opts
+        # JS_RUNTIME_OPTS: read per call; no runtime leaves the key out.
+        runtime = self._runtime_now()
+        if runtime is not None:
+            opts["js_runtimes"] = {runtime.name: {"path": str(runtime.path)}}
+        return opts
 # wiring.py
+    # LIVE_SOURCE: the deno setting is read at each resolution, so a PUT needs no restart.
+    js_runtime = JsRuntimeLocator(lambda: settings.get("downloader", "deno_path"), bundled_deno())
```

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-12-youtube-client-runtime-implementation-critical-review.md`, on the ledger loop `s66-execution-2026-11-12-youtube-client-runtime`. The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | 0 findings; intent achieved: yes; IR-1 to IR-7 pass | `055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30` |

### Verdict

`approved` at round 1 of 6 (dispatch `s66-exec-r1`), with no findings. The review-state check (H1-7a) and the approved-state check (H1-7b) both exit 0. MEU-141 moves to `approved` in H2-2.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The dev region picker in `native/region-picker/publish` is the 2026-11-09 build, because NuGet on this machine has no package source for the 8.0.34 runtime packs | environment, raised for Mat | None | D-660 A. The next real `dist` rebuilds the picker once NuGet resolves 8.0.34. The installer measured here carries the same 2026-11-09 picker as `win-unpacked` |
| `fetch_deno_windows.ps1` has not run online through `dist`'s own chain. Row 4 fetched the files once under D-642 A, and row 5 ran the script offline with `-ExtractOnly` | coverage note | None | The release build runs it. AC-141.14 covers its refusals and the extraction on fixture files |
| The MP3 convert | bug | MEU-142 (Session 67) | Its own grouping session (D-651) |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2-5) |

### Departures and their basis

1. **D-658.** Three e2e fixtures are `SimpleNamespace` objects that a dataclass default can't reach, so each gains a `js_runtime` namespace with the unavailable values. No assertion changes (§Row 2b).
2. **D-659.** The UI lint refused three unused `depsGets` lines in `settings-runtime.test.ts`, so they were removed. No assertion changes.
3. **D-660 A.** `dist` stopped at `build:picker` (NU1100), so the 2026-11-09 picker was copied back and dist's other steps ran unchanged (§Row 5).
4. **D-661.** `meu_status.py update` re-dumped the whole file, so `meu-status.yaml` keeps its pre-status bytes with only the two entries changed.
5. **The `!*.sha256sum` filter.** `electron-builder.yml` also keeps the published sum file out of `resources/deno`. This goes beyond the plan's `!*.zip`.
6. **D-663.** The cookies-on live probes used Firefox's cookies (MEU-140 handoff).

The departures recorded for MEU-140 (D-655, D-656, D-657, D-662) are in its handoff.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-12 | claude-code-local (Claude Opus 5.5) | Row 4's lock, sync and fetch records; row 1b's type-only names and receipts |
| Updated | 2026-11-12 | claude-code-local (Claude Opus 5.5) | MEU-141 Red: six test files, the smoke tool, the test ids, AUDIT_INPUT and D-658's fixture repairs |
| Updated | 2026-11-12 | claude-code-local (Claude Opus 5.5) | MEU-141 Green: the runtime lookup, options, Health, Settings, the bundle and the licence; installer 371,477,462 bytes (D-659, D-660) |
| Updated | 2026-11-12 | claude-code-local (Claude Opus 5.5) | Row 6: spec, register and status for both MEUs (D-661) |
| Completed | 2026-11-12 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, the evidence records and the H1-2 gate (H1-6) |
