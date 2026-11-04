# Walkthrough — 2026-09-30-tts-repair (Session 27)

Execution evidence for the plan. Sections are added in task-row order. The `## LOCAL_REPRO` section was recorded before execution was authorized: the request ran in parallel with plan review (plan row 1; [local-requests.md](local-requests.md) §LOCAL_REPRO). The row stays `[ ]` until execution starts, and `validate-task.sh repro-check` then verifies this section.

## LOCAL_REPRO

**Provenance.** Relayed `USER_EXPLICIT` 2026-09-30: Mat pasted the local agent's result block and screenshots into the Claude Code web chat, after the Round 2 plan approval. The block lists six screens; five images arrived. The local "[4] Capture scrolled right" screen is missing, but received image 4 shows the same scrolled-right toolbar with Settings expanded.

**Run context.**

- Dev run (`electron-vite dev`), Windows, `P:/av-kit`.
- The app was started from `f4c1a12`. `git diff f4c1a12..4d342a6 -- ui packages mcp-server` is empty, so the product code equals this plan's baseline, `175680c` (no product change since).
- **Deviation:** the window was maximized on a 4K display (3840×2063 screenshots), not 1280×800. Overflow findings therefore hold at a wider window than `DEFAULT_WINDOW`. The local side wrote no verification blocks and committed nothing; the cloud recorded them in `known-issues.yaml` on 2026-09-30.

**Screens** (committed copies of the five received images):

- [1](local-evidence/s27-repro-screen-1.webp): TTS, PyTorch FP32 loaded.
- [2](local-evidence/s27-repro-screen-2.webp): TTS, nothing loaded.
- [3](local-evidence/s27-repro-screen-3.webp): Capture toolbar scrolled left.
- [4](local-evidence/s27-repro-screen-4.webp): Capture with Settings expanded, toolbar scrolled right.
- [5](local-evidence/s27-repro-screen-5.webp): Settings.
- [6](local-evidence/s27-repro-screen-6-r5.png): TTS at the default window (R5 addendum).

| Item | Result | Evidence (verbatim where quoted) | Disposition for this plan |
|---|---|---|---|
| R1 | reproduced | Run bar shows the "Failed" chip and "No output yet", with no reason text (screens 1, 2). Latest job `5741bf4b-b371-4258-9c85-391f57d5ff7d`: `status=Failed`, `error_message="en_core_web_sm is not available"`, `segments_done=0`, MP3, `af_heart`, PyTorch FP32 on cpu, failed 4.5 ms after creation. The four earlier jobs since 2026-09-29 have the same message, in WAV and MP3. `console.log` holds only `tts.load_model` INFO lines. | **Confirms MEU-62 and MEU-63 (failure surface).** The message is `prepare._chunk`'s `SpacyModelNotFoundError` text (`services/prepare.py:150-161`): the default-on `chunk` step fails before G2P. That is exactly Round 1 F3, now in `REQUIRED_TTS_ASSETS` / `SPACY_STEPS`. **Side notes:** `segments_total=1000` is by design (`TTS_PROGRESS_RESOLUTION`, `services/tts.py:146,181`), not a placeholder. The empty FFmpeg path (screen 5) is the later MP3 failure, out of scope per 03:422. With AC-62.11 it will surface as an `error_message` instead of being silent. |
| R2 | not-reproduced | All four variants are `is_downloaded=1` and their files exist, so all four Get buttons are correctly disabled. Load states are distinguishable (the loaded PyTorch FP32 Load is muted, the others bright). "Manage" reads as plain text. | **Premise partly unconfirmed.** This is Stop condition S2, so MEU-63 needs Decision Brief D-18 (plan §Decision Log) before row 7. After MEU-62, the three ONNX variants on this machine will read `downloaded: false` until `config.json` is fetched (AC-62.3). Their Get buttons will then be enabled, which reproduces the Get state the target could not show today. The local suggestion (Electron Red needs a not-downloaded variant) is already satisfied: the seam catalog has `kokoro-onnx-int8` and `kokoro-pt-fp32` at `is_downloaded: false` (`ui/tests/e2e/tts-generate.test.ts:45-81`). |
| R3 | reproduced | `capture-chrome-tools` scrolls horizontally even maximized at 4K. Scrolled left, Apply is clipped ("Appl"); scrolled right, Select through Undo are hidden. Expanding Settings adds a row above the toolbar; the overflow is unchanged. | Out of this plan: Session 29 / MEU-65. Recorded on `CAPTURE-TOOLBAR-ICONS`. |
| R4 | different | The rail follows Download/Transcript/TTS/Convert, but not Capture, Console & logging, Appearance, Dependencies, Readiness or MCP access; it stops at Convert on a large screen. Local hypothesis: the trailing sections cannot cross the observer threshold. The right panel has no emphasis. | Out of this plan: Session 31 / MEU-70. Triage D-19's "the rail half is done" premise does not hold, so MEU-70 must also fix the trailing-section rail highlight (under ST3). Recorded on `SETTINGS-ACTIVE-SECTION-HIGHLIGHT` for the Session 31 plan. |
| R5 | reproduced | **Addendum** (relayed `USER_EXPLICIT` 2026-09-30, [screen 6](local-evidence/s27-repro-screen-6-r5.png)): TTS at the default window, about 1280×800 (dev), Language = All, "Manage" collapsed (default), voice list not scrolled, page scrolled to the top. Speed (slider and 0.8/1.0/1.1 presets) and Format (MP3 select) are **both fully below the fold**. The voice listbox runs to the viewport's bottom edge, and the run bar is also below the fold. The page scrollbar thumb covers about 60 % of the track. With "Manage" expanded, Speed and Format sit lower still. At the maximized 4K window (screens 1–2) all three are visible. The first reply had marked R5 as not run at the default window. | **Confirms the AC-64.6 premise at `DEFAULT_WINDOW`**, so `red64`'s `require_failed_title AC-64.6` is expected to fail on the current layout, and Stop condition S8 is not expected to fire. The run bar being below the fold is recorded as an observation: 11:124 names only Speed and Format, and the run bar is not in AC-64.6. |

## Execution authorization and prerequisites (row 0)

- **Authorization:** `USER_EXPLICIT 2026-09-30 "proceed, D-18 A"`, recorded in [human-gate-decision.md](human-gate-decision.md) §Execution authorization. The context-tool gate was re-checked for execution: `graphify-out/` and `graphify-out-research/` are absent and there is no `headroom`, so `not_applicable`.
- **Dependencies:** `npm --prefix ui ci`, `npm --prefix mcp-server ci` and `uv sync` all exit 0. **Finding:** plain `uv sync` installs only the root dev group, because the workspace root has no dependencies (`pyproject.toml` `[tool.uv] package = false`). `uv sync --all-packages` (exit 0) is required for `kokoro` 0.9.4, `spacy` 3.8.15, `onnxruntime` 1.29.0 and the `avkit_*` packages. `en_core_web_sm` is **not installed** in the container (`spacy.util.is_package` → False), the same as on the target.
- **`electron-setup` / `prereq`:** Electron v42.9.3 starts under xvfb. `PASS MEU state {'MEU-16': 'approved', 'MEU-22': 'approved', 'MEU-56': 'approved', 'MEU-62': 'pending', 'MEU-63': 'pending', 'MEU-64': 'pending'}`. `PASS prereq`.

## Baseline

`validate-task.sh baseline` ran on the untouched product tree. `baseline.sha` = `bea998a7ddcca3fa610a2eea0cca56d68b840ba9`.

| Stage | Result (container) |
|---|---|
| pytest (`s27-baseline-pytest.txt`) | `63 failed, 545 passed` in 79 s. The failed set is the container's env-bound `ENV_BOUND_PY` reference for `pytest_env_ok` (Windows-bound tooling/packaging tests plus the Python-3.11 `test_ac_2_2` enum `in` check). |
| Vitest | `673 passed of 675`; env-bound tolerated: AC-51.6 (CRLF hash), AC-41.3 (`P:/zorivest`) |
| UI build / harness build | pass |
| Electron | `106 passed`; env-bound tolerated: the 4 capture-picker stub specs, for 110 in total |

**Incident (recorded, no effect on results).** While the baseline job was still running its Electron stage, I edited `validate-task.sh` (the `pytest_red` fix). Bash reads a running script incrementally. After printing `PASS baseline at bea998a…`, it resumed at the old byte offset inside the edited file and executed two stray lines:

- a no-op token, `es: command not found`;
- the read-only `vitest_env_ok s27-post-doc-tests …` (17/18, env-bound AC-41.3).

It then hit a syntax error (exit 2). No state-changing command ran: `git status` shows no change under `.agent/`, `docs/build-plan/` or `docs/BUILD_PLAN.md`. Every baseline stage had already printed PASS. Rule adopted for the rest of the session: never edit `validate-task.sh` while a run of it is active.

## Census (row 2)

`validate-task.sh census` (exit 0) wrote 231 hit lines (`s27-census.txt`). Dispositions, grouped by file:

| File (hits) | Disposition |
|---|---|
| `ui/tests/unit/tts-page.test.ts` (30) | `:55`, `:167` → **TA-1**. `:42`, `:46`, `:56-73`, `:165-166`, `:256-258`, `:296-308`, `:326-327`, `:335`, `:358-360` → unaffected: source-string presence over `ttsSources()`, and every id stays in the TTS feature sources (D-15/D-16). Note `:259`: `not.toMatch(/lang_code/)` also binds the new `VoiceCombobox.tsx`. |
| `ui/tests/unit/tts-page.behavior.test.ts` (21) | `:169` → **TA-5** (setup helper). `:227` → **TA-2**. `:236-242` → **TA-3**. `:262`, `:329` → **TA-6**. `:221-223`, `:232`, `:249-254`, `:406` → unaffected. `:337-343` (`resolveRunBarSlot({error,status})`) → unaffected: `jobError` is an optional third field. |
| `ui/tests/e2e/tts-generate.test.ts` (21) | `:258`, `:342-346`, `:443-446` → **TA-4**. `:260`, `:346`, `:349`, `:458` → **TA-7**. `:257`, `:279-281`, `:336`, `:351`, `:441`, `:447`, `:504` → unaffected. |
| `ui/tests/e2e/test-ids.ts` (17) | registry constants; additive MEU-62/63/64 blocks only (`PRESERVED_TESTIDS`) → unaffected. |
| `mcp-server/tests/fixtures.ts` (25) | `EXPECTED_ACTION_INDEX` (46 KEEP rows). `download_asset` is appended after the capture rows, so it is untouched → unaffected. |
| `mcp-server/tests/action-index.test.ts:39`, `convert.test.ts:54`, `capture.test.ts:88`, `m7-resource.test.ts:51`, `:68` | `toHaveLength(67)` → **TA-9** (census-confirmed sites; +1 appended action → 68). The other hits in these files (`slice(0,46)`, `slice(0,59)`, the convert count of 13, capture positions) → unaffected, because the action is appended. |
| `mcp-server/tests/strict-confirm.test.ts` (7) | ZOD_STRICT over KEEP/CONVERT/CAPTURE, and `download`/`load` empty-id → unaffected. |
| `tests/unit/test_domain.py` (18) | `:321`, `:522-523`, `:602` → **TA-9**. `:525-540`, `:1437`, `:1482` constructions → `FIXTURE_REPAIRS` (`asset=None`; the asserted property is unchanged). `:25`, `:594`, `:1335-1337`, `:1422`, `:1469` → unaffected. |
| `tests/unit/test_services.py` (10) | `HealthService(` / `ModelService(` / `TTSService(` constructions → `FIXTURE_REPAIRS` (`assets=FakeAssets()`, `download_runtime=idle_runtime`). `:509` (`test_ac_13_6`) → unaffected (D-13 keeps other console lines byte-identical). |
| `tests/unit/test_uow_commit_log.py:35`, `tests/unit/test_console_level.py:27` | `FIXTURE_REPAIRS` (HealthService collaborators) |
| `tests/e2e/api_fakes.py` (4) | `:341`, `:356` positional `ModelDownloadRuntime` → `FIXTURE_REPAIRS` (`asset=None` in position 2). `:29`, `:371` → unaffected. `FakeHealth.dependencies` (`:64`) → setup: gains the asset states. |
| `tests/e2e/test_api_health_settings.py:162` | unaffected (the `yt_dlp` key survives). The file's `FakeHealth.dependencies` (`:44`) → setup: gains the asset states. |
| `tests/e2e/test_api_openapi.py` (6), `test_api_bodies.py` (4), `test_api_tts_models.py` (4) | unaffected (no new route; `ROUTE_INDEX` stays 71) |
| `tests/integration/test_tts_models.py:654`, `:659` | AC-9.12 confinement → unaffected: `assets.py` imports no `huggingface_hub`, and the vocab fetch lives in `model_manager/vocab.py` |
| `ui/tests/unit/settings-rail.test.tsx:150`, `:475` | unaffected. The fixture has no asset rows, `presentAssetRows` renders none, and the success count stays 2. |
| `ui/tests/unit/settings-page.test.ts` (0 hits; the `'yt-dlp'` pattern matched nothing) | TA-8 is not needed: no existing assertion pins the Dependencies row count |
| `ui/tests/e2e/settings.test.ts:131`, `console-chrome.test.ts:110` | unaffected (section visibility) |
| `error-banner` / `FFmpeg` / `yt_dlp` hits in Downloader, Transcript, Convert, help-card, layout-primitives, `test_youtube_adapter`, `test_sqlite_uow`, `test_packaging_backend` | unaffected (other pages / other features) |

**New contradictions outside `TEST_AMENDMENTS`: none.** One structural pin found during Red is handled by design, not by amendment: `tests/unit/test_domain.py:1324` pins `ModelCatalogPort` to exactly `("download", "sideload")`. The vocab fetch therefore goes behind the new `TtsAssetPort` (`model_manager/vocab.fetch_vocab` injected into `TtsAssetAdapter`) and not onto `ModelCatalogPort`, so no port-method expectation changes.

## MEU-63 Red disposition (row 7)

`red63` passes: "PASS AC-63 RED: 1 failing AC-63 assertions, 36 passing" and "PASS AC-63 E2E RED: 2 failing AC-63 specs". The helper counts as decisive only messages that contain "expected" or "assert". It lists the other seven Vitest failures as "other", so each is dispositioned here from `s27-63-red-vitest.json`:

| Test | Red message | Disposition |
|---|---|---|
| AC-56.3 | `expected [ <div …(2)>…(3)</div>, …(1) ] to have a length of 1 but got 2` | **TA-3** site (single `model-row`), assertion Red |
| AC-63.1 ×2, AC-63.2 (disabled) | `Unable to find an element by: [data-testid="model-select"]` | new MEU-63 spec; the element does not exist yet |
| AC-63.2 (action) | `Found multiple elements by: [data-testid="model-row"]` | new MEU-63 spec; the old four-row grid |
| AC-63.3 | `Unable to find an element by: [data-testid="tts-asset-chip-tts_onnx_vocab"]` | new MEU-63 spec |
| AC-63.5 | `Unable to find an element by: [data-testid="error-banner"]` | new MEU-63 spec; a Failed job showed no banner (LOCAL_REPRO R1) |

None of these is a load, import or setup error. Electron: AC-63.6 fails on `toContainText` for `tts-asset-chip-tts_onnx_vocab`, and AC-63.5 fails on `toHaveText` for `error-banner`.

**Gate re-run note.** The first `gate63` run was stopped during `repeat-each=20`, with typecheck, lint, Vitest, build and Electron (12) already passing. The reason was a readability rename in `TTSPage.tsx`: `jobError` → `runBarText`, because the value is the whole `RUN_BAR_ERROR`, not just the job's message. `green63` and `gate63` were then re-run in full on the final tree, and the MEU-63 handoff cites that run.

## MEU-64 Red disposition (row 10)

`red64` passes, with three results:
- "PASS AC-64 RED: 1 failing AC-64 assertions, 23 passing";
- "PASS AC-64 E2E RED: 2 failing AC-64 specs";
- "PASS AC-64.6 RED on toBeLessThanOrEqual".

`VOICE_CATALOG_FIXTURE` parity passes first (`test_tts_voice_fixture.py`, 1 passed). The Vitest failures, from `s27-64-red-vitest.json`:

| Group | Red message | Disposition |
|---|---|---|
| 16 MEU-56/MEU-63 behavior tests and 6 AC-64.x behavior tests | `Unable to find an element by: [data-testid="voice-selected-chip"]` (15 + 6) or `… "voice-combobox"` (1) | **TA-5** setup, which now waits on the selection chip; the chip does not exist before MEU-64 |
| AC-22.6 (source test) | `expected '…' not to contain 'preview-raw'` | **TA-1** |
| AC-64.3 (source test) | `apply-cleanup-btn: expected -1 to be greater than -1` | new MEU-64 spec |
| `voice-combobox.test.tsx` | `Failed to resolve import "…/VoiceCombobox"` | the new-file allowance (the module does not exist yet) |

Electron: `AC-64.6` fails on its first `expect`, the `speed-slider` bounding-box `toBeLessThanOrEqual` against `window.innerHeight`. This happens on the unchanged layout with the 54-voice fixture and confirms LOCAL_REPRO R5, so Stop condition S8 does not fire. `AC-64.4` fails on `toHaveAttribute('role', 'combobox')` because the element is not found.

**Test corrections made during Green.** Neither changes an asserted expectation:

1. **`AC-64.1 a failed prepare…`** (new test). Setup now waits for the typing debounce `PUT {input_text: 'Keep me'}` before it records `putsBefore`. Without that wait, the 300 ms debounce from typing lands inside the test's 350 ms "no new PUT" window, so the count also measured typing, not the failed Apply. The assertion ("the failed Apply adds no `input_text` PUT") is unchanged. Its Red run never reached it, because the TA-5 setup failed first.
2. **`voice-combobox.test.tsx`** (new file). The harness passes `testIds` to `VoiceCombobox`. The page must own its registered ids: pinned `tts-page.test.ts` AC-22.22 requires `voice-grid` and `language-select` in `TTSPage.tsx`. The combobox therefore takes them as a prop, following the `Disclosure`/`StatusChip` `testId` idiom (D-30).

**Product adjustment found in Green.** The selection chip reads "Loading voices…" until the voice catalog arrives. Otherwise it echoed the bare setting and the TA-5 setup wait passed before any data had loaded, which made the AC-63.2 picker test race the catalog. The chip describes a catalog voice (`id · description`); before the catalog loads it cannot, and when a stored voice is missing from a loaded catalog it shows the raw id.

**Registry note (gate64, first run).** Deleting `export const PREVIEW_RAW` from `ui/tests/e2e/test-ids.ts` changed the registry prefix, which AC-51.6 (`layout-primitives.test.ts`) pins by hash. `vitest_env_ok` correctly reported a real failure (`s27-64-green` and `s27-64-vitest` FAIL). The constant was restored in place, so the registry diff is append-only. Test-ID migration "removed" applies to the page element: TA-1 asserts that `preview-raw` is absent from `TTSPage.tsx`. `green64` and `gate64` were then re-run.

## Container live run (H1-2 prep)

`tts-live-pre` was run on its own before the full pre-gate, because it is the only real-network step. It needed three runs:

1. **Harness bug.** `AttributeError: 'AssetState' object has no attribute 'state'`: `tts_live_check.py` read `.state` from the domain row. Fixed in the harness.
2. **Product defect.** `ValidationError: float samples must be within [-1.0, 1.0]`: real Kokoro output overshoots, and the AC-8.4 writer rejects it. Fixed test-first (MEU-62 D-33).
3. **Product defect.** The job reached `Done`, but `duration_s 0.325` (< 0.5): kokoro 0.9.4 `KPipeline.Result` chunks were not unpacked, so ONNX got only pad tokens. Fixed test-first (MEU-62 D-34).

Final run on `43017a5` (clean tree): all five `TTS_LIVE_STEPS` PASS. `generate-wav` gave `Done`, no error, **2.075 s**, RMS 3615. Neither product defect was visible to any faked suite. This is the reason the plan has a live check, and `TTS_LIVE` on Windows now confirms rather than discovers.

A ruff E501 in `tests/unit/test_tts_voice_fixture.py` (row 10) was also fixed; the full pre-gate would have caught it.

## Pre-gate attempt 1: census misses (H1-2)

The first full pre-gate stopped at `pytest_env_ok`, with two new failures against `baseline.sha`. Both are in categories the plan already approves. The row-2 census missed them because it searched the MCP tests and not the Python e2e tests:

| Test | Failure | Disposition |
|---|---|---|
| `tests/e2e/test_api_auth.py::test_ac_14_2_auth_tokens_and_health_exempt` | `AttributeError: 'types.SimpleNamespace' object has no attribute 'tts_onnx_vocab'` (its private health fake) | **`FIXTURE_REPAIRS`**: the fake gains `tts_onnx_vocab` / `tts_spacy_model` / `tts_spacy_version`. This is the same setup-only edit as `api_fakes.FakeHealth` in §Census; assertions are unchanged. The other `SimpleNamespace` health fakes (`test_api_captures` / `downloads` / `conversions`) never reach `/health/dependencies` and pass unchanged. |
| `tests/e2e/test_api_downloads.py::test_ac_42_9_surface_counts_are_flat_and_openapi_regenerated` | `assert 68 == 67` (`ACTION_INDEX_AFTER`, the MCP registry row count) | **TA-9**: "+1 MCP action `download_asset`". This is the same count as `action-index.test.ts` `toHaveLength(68)`, at a Python site. |

The stale "67" in one `m7-resource.test.ts` test title (a TA-9 file) became "68"; its assertions already carried TA-9. No expectation outside `TEST_AMENDMENTS` changed, so Stop condition S3 does not apply.

## Container pre-gate (H1-2), non-authoritative

- **Attempt 2** was lost to a container restart during the full Electron suite. Every stage before it had passed.
- **Attempt 3** passed in full on `d793f1f`, with `git status` empty (`e3b0c442…`). Lockfiles: `ui/package-lock.json` `d26fb2de…`, `mcp-server/package-lock.json` `62147de5…`, `uv.lock` `da452c34…`. Node `v22.22.2`.

| Stage | Result |
|---|---|
| pyright / ruff / ui typecheck / ui lint / mcp typecheck / plan static / task contract | PASS |
| pytest (`pytest_env_ok`) | no new failures; baseline env-bound 63 = head 63; **566 passed** |
| Vitest (`vitest_env_ok`) | **700 passed of 702**; env-bound AC-51.6, AC-41.3 (floor 675) |
| ui build, harness build, mcp build, mcp tests, OpenAPI `--check`, state render `--check` | PASS |
| Electron (`electron_env_ok`) | **111 passed**; env-bound: the 4 capture-picker stub specs (floor 110) |
| `tts-live-pre` (real network) | all 5 steps PASS; `generate-wav` Done, **2.075 s**, RMS 3615 |
| source audit (`AUDIT_SRC`, `PREFIX_AUDIT`) | 0 hits |

`PASS container pre-gate (authoritative: windows-gate + tts-live)`.

## WINDOWS_GATE attempt 1 (FAIL) and TTS_LIVE attempt 1 (PASS)

- **TTS_LIVE** on Windows, `b9778fc` → `c0b6a84`: all five steps PASS. The ONNX int8 variant came from huggingface.co (92,360,543 B), `en_core_web_sm-3.8.0` from github.com; `generate-wav` gave Done, 2.075 s, RMS 3619.9. `tts-live-check` PASS.
- **WINDOWS_GATE**: stages 1–7 exit 0. Stage 8 `py-tests` exit 1 (322 passed, 1 failed with `-x`; without `-x`, 4 failed and 625 passed). All failures are in `tests/tooling/test_framework_adoption.py` and are pre-existing on main. The Decision Brief is at human-gate-decision.md §A-2. `windows-gate-check` FAIL (only 8 of 17 stages). Artifacts are preserved on Mat's host at `C:/Temp/av-kit/keep/b9778fc…-attempt1/`.

## WINDOWS_GATE attempt 2 (FAIL at stage 16)

On `8c14927` (the A-2 rebind) → `78a5b31`. Stages 1–15 exit 0: pytest 629/0, Vitest 702/702. Stage 16 `ui-electron` failed: 113 expected, 2 unexpected (AC-49.28, W2-3; both 60 s timeouts). The root-cause analysis is at human-gate-decision.md §A-3. In short: an early `page.reload()` aborts the initial `loadFile`, `boot()` dies silently before `revealMainWindow`, and Chromium throttles the hidden window to about 1 fps, so pointer drags balloon. The race was proven 4/4 against 4/4 in the container. W2-3 is not isolated.

## A-3 product fix (STARTUP_RELOAD_RACE)

Per human-gate-decision.md §A-3:
- `ui/src/main/index.ts` reveals the window on `ready-to-show`, and the initial load is wrapped in `try/catch` with a log line.
- The new `ui/tests/e2e/startup-reveal.test.ts` holds 2 specs, proven Red 6/6 and then Green 10/10.
- The pointer-drag specs are no longer bimodal (18/18 runs at about 2 s).

Known issue `GUI-STARTUP-RELOAD-HIDDEN-WINDOW` stays open until WINDOWS_GATE attempt 3 confirms. The e2e count rises by 2; `COUNT_FLOORS` (≥ 110) is unaffected.

## WINDOWS_GATE attempt 3 (FAIL at stage 8) and TTS_LIVE attempt 3 (pass, but weaker)

On `5b55849`, results at `2a68efe`:
- **Stage 8 `py-tests`:** `test_ac_62_5` failed with `409 tts asset already ready: tts_spacy_model`. Without `-x`: 617 passed, 12 failed, all in `test_tts_assets.py`.
- **Cause, our MEU-62 defect:** startup activation of the default `~/.avkit/models` leaked Mat's real spaCy install onto `sys.path`.
- **TTS_LIVE attempt 3** "passed", but saw spaCy `ready → ready`, so the autoload path was not exercised.
- **Fix:** `isolated_home` fixture, and a hermetic, stricter `tts_live_check.py`. Details are in the MEU-62 handoff §Evidence. It is proven with a fake home install: old harness leaks, new harness passes `missing → ready`; tests 12 failed → 20 passed.

**Mat's extra diagnostic** (A-3 build, `--repeat-each=10`):
- The A-3 specs pass 20/20.
- W2-3 passes 10/10 with a median of 0.84 s (before A-3: 5.5–8.8 s).
- AC-49.28 failed 1 of 10 in a **new mode**: the A16 wait for `moved to position 3 of 4.` timed out after 30 s.
- In the container, AC-49.25/26/28 ×40 = **120/120 pass**. Decision pending: human-gate-decision.md §A-4.

## WINDOWS_GATE attempt 4 (FAIL at stage 8), TTS_LIVE attempt 4 (PASS)

On `93e8ba4`, results at `c7f9393`:
- **Stage 8:** 246 passed, 1 failed (`test_ac_62_5`, `409 already ready`). It is deterministic: 10/10 in the full `-x` run, and 10/10 for the pair of `test_api_captures` AC-37.15 followed by `test_tts_assets`.
- **TTS_LIVE:** 5/5, with `fresh-rows` spaCy `missing`, `site_spacy` false, autoload `missing → ready`, and a 2.075 s WAV.

**Cause:** the attempt-3 fix isolated `~` only inside `test_tts_assets.py`, and an earlier test's `build_services` activation leaked the real install across files. **Root fix:** the `tests/conftest.py` autouse `_restore_import_path` fixture. Reproduced and fixed in the container with a fake home (pair 12 → 0 failures; full suite 75 → 63 = the baseline env-bound set). This is an S27 defect in our own diff, fixed without an A-decision like attempt 3's.

## WINDOWS_GATE attempt 5 (FAIL at stage 9), TTS_LIVE attempt 5 (PASS)

On `2909e46`, results at `5cb5f71`:
- Stages 1–8 exit 0; **pytest 629/0**, so the `sys.path` fix holds on Windows.
- Stage 9: Vitest 700/702. `persist-ui` ×2 failed with `Electron failed to install correctly` and `os error 183`: Electron's lazy first-require install raced across parallel Vitest workers after `npm ci`. This is pre-existing and toolchain-level, about 3 in 10 on Mat's host.
- **TTS_LIVE 5/5**, `missing → ready`.
- A-5 fixes the gate script's `npm-ci` stage (serial `install.js`). Known issue `UI-ELECTRON-LAZY-INSTALL-RACE`.

## WINDOWS_GATE attempt 6 (FAIL at stage 16), TTS_LIVE attempt 6 (PASS)

On `df9a3d7`, results at `c3886fe`:
- Stages 1–15 exit 0, including the A-5 `npm-ci` stage: `path.txt` was written inside it, with no `os error 183`. pytest 629/0, **Vitest 702/702**.
- Stage 16 `ui-electron`: 115 expected, **2 unexpected**. AC-49.28 passed (1.9 s, no A-4 diagnostics) and both W2-3 specs passed.
- **TTS_LIVE 5/5.**

1. **AC-63.5, our MEU-63 spec (fixed).** After the seam flips Failed → Done, the banner is only re-read at the next job poll. `ttsPollInterval` polls a non-Generating job every 5 s, which races the default 5 s `expect` timeout. The flake rate was 2–4 in 10 on Windows, both before and after A-3. Fix: the poll-driven assertion gets `{ timeout: 15_000 }`, as AC-63.6 already had. The assertion is unchanged, and the product is correct (a `Failed` job is terminal). Container: 10/10.
2. **AC-58.12 (Settings rail), 0/10 from A-3 on.** Mat's A/B gave `dc1a336` 10/10 and `054f2c7` 0/10.

   The cause is a real `SettingsRail` defect (MEU-58) that the hidden-window artifact had masked; A-3 did not create it. A click sets the entry and holds it for a fixed `CLICK_LOCK_MS = 800`, then `reconcile` re-derives the current entry when the clicked section is not on screen. A smooth scroll that outlasts 800 ms (Chromium's Windows scroll animation) is still mid-way at that moment, so an intermediate section wins and no later crossing corrects it. Before A-3 the never-shown, throttled window dropped smooth scrolls, and the 450 ms fallback jumped instantly.

   Proof in the container, with a scratch spec (deleted) whose smooth `scrollIntoView` runs as a 1.5 s animation: a click on MCP ends with **`settings-rail-capture`** current (3/3), and a 600 ms animation ends with MCP current (3/3). Chromium on Linux finishes the real scroll in about 800 ms, which is why the unchanged spec passes here. The A-6 decision is pending.

## WINDOWS_GATE attempt 7 (accepted under A-7), TTS_LIVE attempt 7 (PASS)

On `407db19`, results at `ca7a714`: pytest 629/0, Vitest 702/702, e2e 117 passed / 1 unexpected / 0 flaky. The unexpected test was AC-49.26, a drag-over miss with the A-4 diagnostic `"DL-1" was moved to position 1 of 4.`. Mat reported that he interacted with the app window during that drag. Stage 17 `source-audit` was not run on Windows (the container pre-gate audit had 0 hits). TTS_LIVE 5/5 (`missing → ready`, 2.075 s). `windows-gate-check` still reports FAIL; Mat accepted the result under A-7, and Session 27 moves to H1-7.

The fixes now verified on Windows are A-3 (startup reveal), A-5 (Electron install), A-6 (rail), the MEU-62 isolation fixes and the AC-63.5 timing: AC-58.12, the A-6 spec, AC-63.5, AC-49.28 and both W2-3 specs pass in the gate.
