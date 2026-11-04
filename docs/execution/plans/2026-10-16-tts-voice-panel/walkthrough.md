# Walkthrough — Session 35 `tts-voice-panel` (MEU-75, MEU-79)

Worktree `P:/av-kit-wt/s35-tts-voice-panel`, branch `claude/s35-tts-voice-panel`, cut from `main` `6097cf5` (2026-10-17).

## Execution message

- **User message (2026-10-17, Claude Code chat):** "@.agent/workflows/execution-session.md  Session 35 as per session grouping"
- This message follows the round 3 plan-review approval (`2026-10-16-tts-voice-panel-plan-critical-review.md`, verdict `approved`, ledger loop `s35-plan-2026-10-16-tts-voice-panel` closed). It satisfies `plan_to_exec_gate: human`.
- **Baseline drift since planning.** The plan's line anchors were taken at `4a97483`. `main` has since gained the Session 35 plan (`34d0f74`) and Session 39 capture-new-marks (`c7d2461`, `6097cf5`). Session 39 touches only three of this plan's files:
  - `tests/unit/test_domain.py`: the `AnnotationType` enum entry only; `TTS_PORT_METHODS` moved from `:1153` to `:1154`.
  - `openapi.committed.json`: capture schemas only; `ModelVariantOut` is unchanged.
  - `meu-status.yaml`: MEU-90/91 rows; MEU-79 moved from `:2088` to `:2090`.

  No AC or contract changes. H1-4 diffs against `baseline.sha`, so Session 39's OpenAPI additions are not counted.
- **Next Session Design Rules applied** (Session 39 reflection):
  - RULE-1: the venv is created with Python 3.12.12 before `uv sync`. `RECEIPTS_DIR=C:/Temp/av-kit` is set in the process that runs every gate. The approved `session-gate.ps1` is not edited.
  - RULE-2: the execution-review prompt states the verdict schema's approval coupling.
  - RULE-3 concerns convert-queue diagnostics and is outside this scope.

## Baseline

Row 0 exited 0 (2026-10-17). Install OK (Python 3.12.12 venv). `s35-prereq.txt`: `prereq problems: []`. `baseline.sha` = `6097cf59adc7835fa6062c8bd3d55c679aef4543` (= `main` `6097cf5`). `s35-base-check.txt`: `baseline receipts without a result summary: []`. `ui-build` OK.

| Suite | Result | Failing at baseline |
|---|---|---|
| `py-tests` (`s35-base-py.txt`) | `2 failed, 904 passed, 1 warning in 89.11s` | `tests/unit/test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]`, `tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]` — the known environmental pair the gate already excuses (`$expectedBaselinePyFailed`). |
| `ui-tests` (`s35-base-ui.txt`) | `Tests 1 failed \| 974 passed (975)` | `tests/unit/queue-canon.test.ts > Phase 10 queue-card canon (MEU-41) > AC-41.3 both themes declare the ported status tokens with Zorivest hexes` — `PILL_TOKEN_SOURCE light --color-status-pending: expected '#9a3412' to be '#ea580c'`. Cause is external: Zorivest commit `1f254832` (2026-10-16, MEU-662) darkened its light palette in `P:/zorivest/ui/src/renderer/src/globals.css`, which this canon test reads. No file of this plan is involved. |
| `mcp-tests` (`s35-base-mcp.txt`) | `Tests 10 failed \| 418 passed (428)` | All ten are "dist not built" in the fresh worktree (row 0 runs `mcp-tests` before any `mcp-server` build): `capture.test.ts` AC-38.8; `convert.test.ts` AC-32.8; `audit/runner-fake-backend.test.ts` AC-68.1/68.4 (×2), AC-68.6, AC-68.7 (×2), AC-68.8, AC-68.8/68.9, AC-67.19. Row 3 and the gate build `mcp-server` first, so these are expected to pass there. |
| `ui-electron` `tts-generate.test.ts` (`s35-base-e2e.txt`) | `16 passed (31.9s)` | none |

## Census

Row 1 exited 0 (2026-10-17): `census hits: 230` (`s35-census.txt`; the count includes the one `[rtk]` banner line). `s35-spec-11.txt` finds the new 11 section at `:151` (`## Residuals registered 2026-10-09`), `:155` (anchor), `:157` (heading) and `:159` (`TTS-MODEL-ROW-LAYOUT` note). The section was written before any test (D-18).

Dispositions, grouped by file; every hit in a group shares the reason. **No `new-contradiction`; S2 not triggered.**

| File (hits) | Disposition | Reason |
|---|---|---|
| `tests/integration/test_tts_models.py` (38) | **TA-1** for the explicit-CUDA load at `:435-437`; the rest `unaffected` | `:421` patches `torch.cuda.is_available` → False, so under `DEVICE_RESOLVE` the explicit `DeviceType.CUDA` load at `:435` would fall back to CPU; TA-1 scopes a `monkeypatch.context()` reporting CUDA to that one load. `:360-383` loads every seed on `DeviceType.CPU` (CPU → CPU; ONNX CPU never calls `get_providers`, which `FakeSession` lacks). `:387` missing-weight → `ModelLoadError` from `FileNotFoundError` is kept. `:399-405` ONNX `Auto` → CPU providers: the ONNX probe reads `get_available_providers()`, which on this host is `['AzureExecutionProvider', 'CPUExecutionProvider']` (checked 2026-10-17), so `Auto` resolves to CPU (residual: a host with `onnxruntime-gpu` would try CUDA here; recorded for the handoff). `:410-433` PyTorch `Auto` with CUDA / MPS patched → same result under the probe. `:440-441` CPU. `:43`/`:313` `TTS_PORT_METHODS` is an iteration subset (plan round 1 Q6). `:208`, `:613`, `:669-689`, `:773` (`StubKModel.to` returns self; CPU load) are fixture or unrelated assertions. |
| `tests/unit/test_domain.py` (12) | **TA-3** at `:1154`; the rest `unaffected` | `:1328` compares `_protocol_methods(TTSPort)` to `TTS_PORT_METHODS` exactly, so the new port method must be appended there. `:198` error-class list, `:323`/`:499-513` `ModelStatus.device` (unchanged), `:695`/`:1071-1077` `ModelVariant` has no `device` field (unchanged: `devices` lives on the API schema only), `:1156` another port's list. |
| `tests/unit/test_services.py` (16) | **TA-4** (`FakeTTSPort`, `:1559`); the rest `unaffected` | `FakeTTSPort` gains `available_devices`. `:135`, `:1685-1873` `is_downloaded` fixtures; `:318` a media-port `is_available`; `:456` settings `device` validation (`gpu` rejected; unchanged); `:1590`/`:1616` existing fake methods. |
| `tests/e2e/api_fakes.py` (10) | **TA-2** (`FakeModels`, `:344`); the rest `unaffected` | `FakeModels` gains `available_devices(fmt)` → `(Auto, CPU)`, which every route that builds `ModelVariantOut` now calls. `:354`/`:363`/`:374` fixture lines; `:525-548` `make_bundle`/`make_client` signatures. |
| `ui/tests/e2e/tts-generate.test.ts` (17) | **TA-6** (`E2E_DEVICE_SEAM`, `:36-100`); the rest `unaffected` | The seam rows gain `devices`. `:153`/`:209` status `device: 'cpu'`; `:224` download transition; `:286`/`:379-380`/`:502` visibility and selection by test id (ids keep); `:606-625` AC-64.6 (Speed and Format visible without scrolling) is a bound row 5 must keep green, not an amendment. |
| `ui/tests/unit/tts-page.behavior.test.ts` (21) | **TA-5: no line changes** (as the plan expected); all `unaffected` | Fixtures `:49-50`, `:501` have no `devices`, so `deviceOptions` defaults to `['auto', 'cpu']`; AC-56.3 (`:293`) selects `cpu` and `:529` posts `auto`, both inside the default. `:154`/`:167` are status payloads (`cuda` is a status display, not a select value). `:278`/`:476-478`/`:504-542` locate by `model-row`/`device-select`, which keep. |
| `ui/tests/unit/tts-page.test.ts` (14) | `unaffected` | Source-string checks for test ids that keep (`:44-69`, `:266-328`); AC-22.17 `buildLoadBody` still rejects `gpu` (`DEVICE_VALUES` unchanged, `ModelLoadIn` unchanged). |
| `ui/tests/unit/layout-primitives.test.ts` (13) | `unaffected` | AC-51.2 renders `SegmentedControl` without `size`; `SEGMENT_SIZE` keeps that markup byte-identical. AC-51.5 forbids hex, `transition-all`, page imports; ` h-9` introduces none. AC-51.6 hashes the `test-ids.ts` registry prefix, which no row changes (no id added). AC-51.7 checks primitive adoption by import. |
| `tests/integration/test_tts_assets.py` (12), `tests/integration/test_tts_voice_packs.py` (6) | `unaffected` | They run the real stack (real `ModelService` + `KokoroAdapter`, so `available_devices` exists via the real probe) and load on `device: "cpu"` (no `get_providers` call). `/models/available` reads only `is_downloaded`. |
| `tests/unit/test_tts_async.py` (5), `tests/e2e/test_api_tts_runtime.py` (6) | `unaffected` | Their TTS-port fakes (`:187`, `:118`) serve generation/voices, not the model-list routes; `AssetModels(FakeModels)` inherits TA-2. Asset downloads (`{"asset": …}`) return no variant. |
| `tests/integration/test_tts_no_torch.py` (4) | `unaffected` | Its subprocess `FakeSession` loads ONNX on `DeviceType.CPU` (CPU providers; `get_providers` never called). AC-75.1 adds a separate test. |
| `tests/e2e/test_api_tts_models.py` (2), `tests/e2e/test_api_bodies.py` (1) | `unaffected` | Load bodies with `device: "cpu"`; validation unchanged. |
| `tests/e2e/test_api_error_surface.py` (1) | `unaffected` | `:150` AC-76.5 `ExtractError: 422` precedent. **AC-76.4** (`:120-144`) raises base `DomainError("x")` and `FFmpegNotFoundError`; adding the `ModelLoadError` subclass to `DOMAIN_HTTP_MAP` maps neither, so the masked 500 and the 503 stay. |
| `tests/e2e/test_api_captures.py` (7), `tests/e2e/test_api_conversions.py` (2) | `unaffected` | `DOMAIN_HTTP_MAP` entries for other errors; the map only gains a key. |
| `tests/integration/test_sqlite_uow.py` (5), `tests/unit/test_tts_voice_packs_service.py` (3) | `unaffected` | `device` is a forbidden DB column (`:151`, `:862`) and stays so: `devices` is computed at the API, never persisted. `is_downloaded` fixtures. |
| `tests/integration/test_filesystem_media.py` (10), `tests/unit/test_domain_conversion.py` (1), `tests/unit/test_conversion_service.py` (1), `tests/e2e/real_stack.py` (1) | `unaffected` | Media/FFmpeg `is_available`, not the TTS device probe. |
| `ui/tests/e2e/capture-inbox.test.ts` (6), `ui/tests/unit/capture-page.test.ts` (2) | `unaffected` | `devicePixelRatio` / screenshot `scale: 'device'`. |
| `ui/tests/e2e/test-ids.ts` (4) | `unaffected` | Registry constants for ids that keep. |
| `ui/tests/unit/settings-rail.test.tsx` (3), `settings-page.test.ts` (3), `convert-page.test.ts` (2), `convert-page.behavior.test.ts` (1) | `unaffected` | Settings `device: 'auto'` leaf (unchanged), other pages' `SegmentedControl` used without `size`. |

**MCP:** `mcp-server/tests` has **no census hit**. Its only 500 is the audit fake backend's generic catch-all (`audit/fake-backend.ts:146`, `fake_error`), not a load-failure pin; `models-assets.test.ts` covers `download_asset` only. MCP passes the API envelope through, so the 422 needs no MCP change.

## MEU-75

### Red (row 2)

Row 2 exited 0 (2026-10-17). `s35-75-red-py.txt`: `23 failed, 2 passed, 147 deselected` (`-k "ac_75"`), `.exit` = `1`. `s35-75-red-check.txt`: `red-check: 1 receipt(s), 0 required test(s), 0 problem(s)`.

| Diagnostic (count) | Declared missing subject |
|---|---|
| `TypeError: KokoroAdapter.__init__() got an unexpected keyword argument 'device_probe'` (14) | `device_probe` |
| `ImportError: cannot import name 'runtime_devices'` (4 direct; 1 more inside the AC-75.1 torch-blocked subprocess, surfaced as `assert 1 == 0` on its return code) | `runtime_devices` |
| `AttributeError: 'ModelService' object has no attribute 'available_devices'` (1) | `available_devices` |
| AC-75.8 `assert None == ['auto', 'cpu']` (`.get("devices")`), `'devices' in required` (2) | assertion |
| AC-75.9 `DOMAIN_HTTP_MAP.get(ModelLoadError)`: `assert None == 422` (1) | assertion |

The two passing tests are the `_neg` bounds, which hold at baseline by design: AC-75.8 `device: "tpu"` → 422, and AC-75.9 `RuntimeError` on load → masked 500 with one `api.unhandled_error`.

Files: new `tests/integration/test_tts_device_resolution.py` (AC-75.1–.7 adapter half, .9 contract, .10); `test_tts_no_torch.py` (AC-75.1 torch-blocked interpreter); `test_services.py` (AC-75.7 service half, **TA-4**); `test_api_tts_models.py` (AC-75.8); `test_api_error_surface.py` (AC-75.9 map and envelope). Amendments: **TA-1** `test_tts_models.py:436-440` (a `monkeypatch.context()` reports CUDA for the explicit-CUDA load only); **TA-2** `api_fakes.py` `FakeModels.available_devices` → `(Auto, CPU)`; **TA-3** `test_domain.py:1154` appends `available_devices` to `TTS_PORT_METHODS`. All files keep CRLF. `ruff check` is clean; `ruff format` was applied to the new file only, because the existing files are not formatter-clean at baseline and reformatting them would add unrelated hunks.

The `engines` fixture pins a fake module `torch` (`cuda=False`, no MPS), so the PyTorch path runs with the injected probe on any host. AC-75.10 is the only test that reads the live runtimes.

### Green (row 3)

Row 3 exited 0 (2026-10-17).

| Receipt | Result |
|---|---|
| `s35-75-green-py.txt` | `172 passed, 1 warning` (the seven row files, unfiltered) |
| `s35-75-green-openapi.txt` | `export_openapi.py --check` exit 0 (in sync) |
| `s35-75-green-mcp-build.txt` | `tsc -p tsconfig.json`, no errors |
| renderer guard | no change under `ui/src` (tracked or untracked) |
| `s35-75-green-mcp.txt` | `Test Files 26 passed (26)`, `Tests 428 passed (428)`. The ten baseline "dist not built" failures pass once `mcp-server` is built. |

Extra checks, not part of the row command: `uv run pyright packages/` gives `0 errors` and `uv run ruff check packages/ tests/` passes. A full `pytest` (`s35-75-full-py-precheck.txt`) gives `2 failed, 929 passed`: the two failures are the baseline pair AC-24.10/AC-25.10, and 929 = 904 baseline + 25 new AC-75 tests.

Source changes:
- `tts/adapter.py`:
  - **`DEVICE_PROBE`:** `runtime_devices`, `DeviceProbe`, `_DEVICE_ORDER`, and `device_probe=` on the constructor. `get_available_providers` is imported beside `InferenceSession`, with `# type: ignore[attr-defined]` because onnxruntime's stubs omit it.
  - **`DEVICE_RESOLVE`:** `_resolve`; `_resolve_device` is removed.
  - **`LOAD_FALLBACK`:** `_load_pytorch` and `_load_onnx` build in locals, and the fields are set only after success. `tts.device_fallback` and `tts.load_failed` are logged as the plan specifies.
  - `available_devices` is added.
- `ports/tts.py`: `TTSPort.available_devices`.
- `services/models.py`: `ModelService.available_devices`.
- `schemas/models.py`: `DeviceWire` and the required field `ModelVariantOut.devices`. `ModelLoadIn` is unchanged.
- `routes/models.py`: `_variant_out(variant, devices)` with `_DEVICE_TO_WIRE`, an inverse of `DEVICE_WIRE_MAP` built once in the route module. It is typed `dict[DeviceType, DeviceWire]` through `cast`, because the existing `formatters.DEVICE_ENUM_TO_WIRE` is `dict[DeviceType, str]` and fails pyright against the Literal field.
- `errors.py`: `DOMAIN_HTTP_MAP[ModelLoadError] = 422`.
- `openapi.committed.json`: regenerated. The diff is only `ModelVariantOut.properties.devices` (an array of the four wire names) and `devices` in its `required`.

## MEU-79

### Red (row 4)

Row 4 exited 0 (2026-10-17), on the row 3 tree: the renderer guard found no `ui/src` change, and `npm --prefix ui run build` passed. `s35-79-red-check.txt`: `red-check: 2 receipt(s), 3 required test(s), 0 problem(s)` (`--require AC-79.7 --require AC-79.8 --require AC-79.10`).

| Receipt | Result | Failing diagnostics |
|---|---|---|
| `s35-79-red-ui.txt` (`.exit` `1`) | `5 failed, 1 passed, 34 skipped (40)` | AC-79.1 and AC-79.3: `expected [ 'auto', 'cuda', 'cpu', 'mps' ] to deeply equal [ 'auto', 'cpu' ]`. AC-79.2: `expected 'cuda' to be 'auto'`. AC-79.5: the `md` inner class equals the baseline literal (no ` h-9`). AC-79.6: `expected [ 'flex', 'flex-wrap', …(2) ] to include 'grid'`. |
| `s35-79-red-e2e.txt` (`.exit` `1`) | `3 failed, 1 passed` | AC-79.7: `{ what: "device-select height", delta: 13.5 }`. AC-79.8: `{ what: "voice-combobox height", delta: 13.5 }`. AC-79.10: `[auto, cuda, cpu, mps]` for ONNX FP32. All are `Error: expect(received).toEqual(expected)`. |

Passing at Red, as the plan allows: AC-79.4 (characterization: a 422 `ModelLoadError` shows "ONNX session failed" in `error-banner`) and AC-79.9 (the baseline rows do not overflow, and the slider is at least 96 px).

**Observed Red reason for AC-79.7 and AC-79.8.** The plan expected the 28 px `sm` button to be the first mismatch. The measured first mismatch is `model-select` itself: it is **22.5 px** tall, not 36 px, because its `className="min-w-0 flex-1"` lands on the `<select>` inside SelectInput's `flex flex-col` root. In a column flex, `flex-1` (basis 0) overrides `h-9`. `device-select` (36 px) and `voice-combobox` (36 px) therefore differ from it by 13.5 px. `VOICE_GRID` already removes that `className`, so the contract is unchanged. The test compares every control with `model-select`, so the Green run must show 36 px throughout, not just matching values.

Two rules came out of the first row 4 attempt (red-check reported 4 problems):
- Playwright's `expect(value, message)` prints `Error: <message>` in place of the `Error: expect(` header, so red-check could not attribute it.
- The Electron tests now carry no custom messages. `expectNear` puts the pair's name in the received object (`{ what, delta }`) so the diff still names it. The rerun is the receipt above.

Files:
- `tts-page.behavior.test.ts`: AC-79.1–.4 and .6. A local `withDevices(row, devices)` adds `devices` per test, so **TA-5** needed no fixture-line change, as the plan predicted.
- `layout-primitives.test.ts`: AC-79.5.
- `tts-generate.test.ts`: **TA-6** `E2E_DEVICE_SEAM` (the `__e2eCatalog` type gains `devices: string[]`; ONNX rows `['auto', 'cpu']`, PyTorch `['auto', 'cuda', 'cpu']`), plus AC-79.7–.10. Each Electron test closes the app in `finally`.

All three files keep CRLF, and `tsc --noEmit` and `eslint` pass on them.

### Green (row 5)

Row 5 exited 0 (2026-10-17).

| Receipt | Result |
|---|---|
| `s35-79-green-ui.txt` | `Test Files 2 passed (2)`, `Tests 40 passed (40)` (both unit files, unfiltered) |
| `s35-79-green-build.txt` | `npm --prefix ui run build` passed |
| `s35-79-green-e2e.txt` | `20 passed` (the whole `tts-generate.test.ts`, AC-64.6 and AC-79.7 to AC-79.10 included) |

Extra checks, not part of the row command: `tsc --noEmit` reports no errors, and `eslint` passes on the changed renderer files.

**Measured geometry** (`s35-79-green-measure.txt`). This is an ad-hoc Electron reading from a scratch script, not a test. It uses the default 1280×800 window, whose content area is 1267×739, and it runs without the fetch seam, so the model row has no action button. It is evidence for the walkthrough only; the bounds are enforced by AC-79.7 to AC-79.9 under the seam.

| Control | Width | Height | Bottom |
|---|---|---|---|
| Voice panel | 416.7 | — | — |
| `model-select` / `device-select` | 262.7 / 112 | 36 / 36 | 243 / 243 |
| `voice-combobox` | 390.7 | 36 | — |
| `speed-slider` / preset inner `div` | **223.3** / 159.4 | 36 / 36 | 433 / 433 |
| `format-select` | 112 (= Device) | 36 | — |
| `model-row`, speed row | scroll 391 = client 391 (no overflow) | | |

The slider is 223.3 px against the 96 px floor, so S4 does not apply. With the seam's `Unload` button in the row, `model-select` gives up the button's column and Device keeps 7rem.

Source changes:
- `useTtsJob.ts`: `CatalogItem.devices?: string[]`.
- `SegmentedControl.tsx` (**`SEGMENT_SIZE`**):
  - `size?: 'sm' | 'md'` (default `'sm'`). The inner class string moves into the `GROUP_CLASSES` constant, with the same literal, so the `sm` markup is byte-identical (AC-79.5).
  - `md` appends ` h-9`.
- `TTSPage.tsx`:
  - **`DEVICE_SELECT_VALUE`:** `deviceOptions = selectedModel?.devices ?? ['auto', 'cpu']` and `effectiveDevice`. `device-select` lists `deviceOptions` and shows `effectiveDevice`, and Load posts `effectiveDevice`. `onChange` still persists only the user's choice.
  - **`VOICE_GRID`:**
    - `model-row` is `grid grid-cols-[minmax(0,1fr)_7rem_auto] items-end gap-2`. `model-select` and `device-select` lose their `className`, and the model action is `size="md"`.
    - The speed row is `grid grid-cols-[minmax(0,1fr)_auto] items-end gap-2`. Its label is `flex min-w-0 flex-col gap-1` and its span is `text-sm font-medium text-fg-muted`. The slider is `h-9 w-full`, and the presets are `size="md"`.
    - `format-select` sits in `<div className="w-28">` without `w-[90px]`.
  - No test id was added, removed or renamed.

## Gate

Row 6 exited 0 (2026-10-17) on the first run after amendment A-1. Receipts: `C:/Temp/av-kit/s35-gate.txt` and `s35-D6-<step>.txt`, snapshotted to `s35-gate-row6/`.

| Step | Stage | Exit | Decisive line |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 6097cf59…4543+38f98d80…6e09` |
| py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract | static | 0 | |
| scope-paths | static | 0 | `changed paths: 26 outside scope: []` |
| py-tests | full | 1 → accepted | `2 failed, 929 passed`; `py-tests baseline rule: failed=2 outside_baseline=[] errors=0` |
| ui-tests | full | 1 → accepted | `Tests 1 failed \| 980 passed (981)`; `ui-tests baseline rule: failed=1 summary_failed=1 outside_baseline=[] unhandled=0` |
| mcp-build, mcp-tests | full | 0 | `Tests 428 passed (428)` |
| ui-build, ui-harness-build, ui-picker-stub, openapi, state-render | full | 0 | state-render: `Drift check passed` |
| ui-electron | runtime | 0 | `161 passed (3.4m)` (the full Electron suite) |
| e2e-repeat | runtime | 0 | `50 passed` (AC-79.7 to AC-79.10 and AC-64.6, `--repeat-each=10`) |
| identity-npm, identity-after | identity | 0 | `tested_state before=… after=…` equal |

**Identity.** `tested_state 6097cf59adc7835fa6062c8bd3d55c679aef4543+38f98d80c0719d4893bf08a76f562418e845047949c51e27904f2e0221a36e09`, the same before and after. `uv_lock_sha256 5285fac8…`, `ui_package_lock_sha256 a86d9a42…`, `segoeui_sha256 704eada1…`.

**Baseline failures, listed and not counted as regressions** (plan §Verification Plan 1):
- py: `tests/unit/test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]` and `tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]`, both FAIL in `s35-base-py.txt`.
- ui: `tests/unit/queue-canon.test.ts > … > AC-41.3 both themes declare the ported status tokens with Zorivest hexes`, FAIL in `s35-base-ui.txt`. Open known issue `QUEUE-PILL-TOKEN-DRIFT`: the test reads the Zorivest hexes live, and Zorivest 1f254832 changed them. No Session 35 file is among its inputs.

**Amendment A-1 (decision D-19, disclosed).** The approved gate applied the baseline rule only to `py-tests`. `ui-tests` had no such rule, so the AC-41.3 baseline failure would have failed the step even though the plan says a baseline failure is never a regression. A-1 adds the same rule to `ui-tests`, on the pattern of Session 37's A-4 (`ui-baseline-rule.ps1`). Vitest exit 1 is accepted only when:
- every `FAIL` id is in a one-entry expected set (AC-41.3) and was also FAIL in row 0's `s35-base-ui.txt`;
- the summary's failed count equals the number of those ids;
- there is no unhandled error.

Any other failure, a crash or an empty FAIL list keeps exit 1. A-1 changes no test, assertion or product file. `session-gate.ps1` is a bound input, so the tested state above already includes it.

**A-1 probe** (`s35-a1-rule-probe.txt`; scratch script, not a plan file). The probe copies the rule's lines verbatim and stops if they drift from `session-gate.ps1`. Over 9 fake receipts it gave the expected exit every time (`9 case(s), 0 mismatch(es)`):
- It passed the real receipt's shape, plain and ANSI-coloured.
- It refused an extra non-baseline FAIL, a count mismatch, an `Unhandled Error`, an `Errors 1 error` summary, a receipt with no FAIL id, a receipt with no summary (a crash), and a single FAIL outside the baseline.

## Hub

Row 7 exited 0 (2026-10-17). Receipts: `s35-hub-rg.txt`, `s35-hub-gated.txt`, `s35-state-render.txt`, console `s35-row7-console.txt`.

Edits:
- `docs/build-plan/03-service-layer.md`:472, a `Delivered (Session 35)` note under §TTS device resolution (residual), naming `DEVICE_PROBE`, `DEVICE_RESOLVE`, `LOAD_FALLBACK`, `LOAD_ERROR_HTTP` and `DEVICE_FIELD`.
- `docs/build-plan/build-priority-matrix.md`:37 row 3.8 MEU-75, and :105 row 11.13 MEU-79.
- `.agent/context/meu-status.yaml`:
  - the Phase 3 note says MEU-75 was delivered by Session 35;
  - the Phase 11 note and the MEU-79 description no longer say the spec section waits for Session 30 approval.
- `tools/meu_status.py update MEU-75|MEU-79 ready_for_review --plan docs/execution/plans/2026-10-16-tts-voice-panel/`, then `render` (`docs/BUILD_PLAN.md` Phase 3/11 lines).

Checks:
- The hub `rg` finds every expected line (above).
- The `after Session 30 approval` `rg` over `meu-status.yaml` finds nothing.
- `render --check`: `Drift check passed — SSOT loaded (91 MEUs, 12 phases)`.

Two mechanical corrections, made before the checks:
1. The first wording of the MEU-79 description, `Spec: 11 §TTS voice panel alignment`, put `: ` inside a plain YAML scalar, so `meu_status.py` could not parse the file. It now reads `Spec in 11 §TTS voice panel alignment (residual).`
2. `meu_status.py` writes `meu-status.yaml` and `BUILD_PLAN.md` with LF. Both were converted back to CRLF, the checkout's line ending (`core.autocrlf=true`); `git diff` is unchanged by this.

These writes come before H1-2, so that gate run binds them.

## Closeout H1

Receipts are in `C:/Temp/av-kit/s35-closeout/`, apart from H1-2's (`s35-gate-h1/`, console `s35-h1-2-console.txt`). The H1-2, H1-6, H1-6a and H1-6b rows show the runs after the execution review R2 correction (the post-F2 gate, run 2, after A-4). Earlier gate receipts: round 1 in `s35-gate-h1-r1/`, the post-R1 attempt 3 that round 2 reviewed in `s35-gate-h1-r2/`.

| Row | Exit | Decisive line |
|---|---|---|
| H1-1 | 0 | `unchecked implementation rows: []` (`task-unchecked.txt`) |
| H1-2 | 0 | `session-gate: all steps exit 0`; `tested_state 6097cf59…4543+b4e8b882…1051`, which `identity.py --state-only` re-derives; scope-paths `changed paths: 39 outside scope: []`. Earlier records: round 1 `+039931ef…5758` (31 paths), round 2 `+c7e4a6b9…32e3` |
| H1-3 | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` (`drift-check.txt`); MEU-75/79 are `ready_for_review` with `execution_plan` set to this plan, both written by row 7 |
| H1-4 | 0 | `added: [] removed: [] changed: ['ModelVariantOut']` (`openapi-check.txt`) |
| H1-5 | — | read `handoffs/TEMPLATE.md` and the `2026-10-14-backend-robustness-MEU-76` exemplar |
| H1-6 | 0 | both handoffs: `20 AC row(s)`, `durable evidence present`, `all 10 plan AC(s) present`, `no [B] rows`; MEU-75 `3 decision(s) logged` (`handoff-check-MEU-75.txt`, `handoff-check-MEU-79.txt`) |
| H1-6a | 0 | `OK: all 10 plan AC(s) present in the handoff`, twice (`handoff-ac-check-MEU-75.txt`, `handoff-ac-check-MEU-79.txt`) |
| H1-6b | 0 | `OK: durable evidence records`, twice (`full-evidence-check-MEU-75.txt`, `full-evidence-check-MEU-79.txt`) |

Notes:
- **AC-87 cross-reference row.** H1-6 counts 7 plan AC families, not the 6 that row H1-6 lists. The seventh is `AC-87`: the plan cites `AC-87.6` and `AC-87.7` once, in research note R-6, as real Session 37 receipts that `red-check.py --require` was tested against. The first H1-6 run refused both handoffs for that family. Each AC table now has an `n/a` row saying that AC-87 belongs to Session 37 and is not a Session 35 AC. No other content changed, and both handoffs passed on the re-run.
- **AC-40 and AC-41 cross-reference rows (after R1).** The plan's §Execution Correction Notes cite `AC-40.6` and `AC-40.30` (A-3) and `AC-41.3` (A-1), which brings the plan's AC families to 9. These are earlier sessions' tests, not Session 35 ACs. Each AC table gains an `n/a` row for them, in the same way as AC-87.
- **AC-66 cross-reference row (after R2).** The A-4 note cites `AC-66.14`, which brings the plan's AC families to 10. H1-6 already passed on a mention of it in the gate narrative, but each AC table gains an explicit `n/a` row, like AC-40 and AC-41.
- **F1 Red record.** The first post-correction H1-6 refused the MEU-75 handoff: `evidence 3: exit_code contradicts result`. The F1 Red record ran bare pytest (exit 1) but was written as `result: pass`. It now reads `result: fail`, which is how two earlier handoffs record a raw Red run. Nothing else changed, and both handoffs pass.
- **Line endings.** `meu-registry.md` is left with the LF that `meu_status.py render` writes. It is a bound input, so H1-2 tested it as it stands. H2-2 renders it again after the approval writes.
- **Evidence records.** Each handoff carries one `evidence.v1` full record, the H1-2 gate. `durable_evidence --require-full` matches every full record against the live state. So row 6's pass, which ran at the earlier state `6097cf5…+38f98d80…6e09`, is given only as narrative in the Quality Gate table.

## Execution review R1

Round 1 (ledger `s35-execution-2026-10-16-tts-voice-panel`, Codex): `changes_required`, one finding. The report is `.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md`.

- **F1 (High, MEU-75, AC-75.9).** When a runtime availability query raised, the error escaped `runtime_devices`. `/models/available` and a CPU load then answered HTTP 500 with a bare `RuntimeError`. The reviewer's probe is `C:/Temp/av-kit/dispatch/s35-review-probe.py`.

Corrections (`/execution-corrections`, D-21):

| Step | Exit | Decisive line |
|---|---|---|
| Red, 4 new AC-75.9 tests | 1 | `4 failed, 1 passed, 17 deselected`: `RuntimeError: provider enumeration failed`, `RuntimeError: probe failed`, HTTP `500 == 200` (`s35-f1-red-py.txt`) |
| Red, weight-file `stat` sibling | 1 | `1 failed, 1 passed, 21 deselected`: `PermissionError: access denied` (`s35-f1-red2-py.txt`) |
| Green, 5 affected test files unfiltered | 0 | `60 passed, 1 warning` (`s35-f1-green-py.txt`) |
| ruff check `packages/ tests/`; pyright `packages/` | 0 | `All checks passed!`; `0 errors` |
| H1-2 full gate re-run | see the Closeout H1 table, updated below | round 1 gate receipts kept in `C:/Temp/av-kit/s35-gate-h1-r1/` |

The fix:
- `runtime_devices` asks each runtime query through `_query`. A query that raises counts as the device being absent and logs `tts.device_probe_failed`.
- `load_model` wraps a raising injected probe in `ModelLoadError`.
- `_load_pytorch` now resolves the vocab inside the existing guard.
- `_require_weight_path` turns an `OSError` from `is_file` into `ModelLoadError`.

Sibling sweep: those are the only statements in `load_model` that ran outside a guard. `ValidationError` was already a mapped domain error. The `03-service-layer.md` delivered note still describes the behavior correctly, so the build plan is unchanged.

The plan records the correction under §Execution Correction Notes, and so does the MEU-75 handoff (D-21, plus FAIL_TO_PASS rows and red/green records).

### A-2 — post-correction gate run 1: transcript-queue W2-5 timeout (known issue)

The first H1-2 re-run after the F1 correction (`tested_state 6097cf5…+2cf1823c…5dc8`) passed every stage through `state-render`: scope-paths `changed paths: 35 outside scope: []`, and the py and ui baseline rules matched the expected ids only. It then failed `ui-electron` with `1 failed, 160 passed (8.3m)`. The failing test was `transcript-queue.test.ts:297` W2-5, which hit `Test timeout of 180000ms exceeded`, followed by `Worker teardown timeout of 60000ms exceeded`. Because the gate stops at the first failure, `e2e-repeat` and the identity steps did not run. The receipts are kept in `C:/Temp/av-kit/s35-gate-h1-r2fail/`.

Classification: this is the open known issue `DOWNLOAD-QUEUE-DRAG-OVER-MISS`, which names transcript-queue W2-5 and says "each miss fails the fail-fast session gate at ui-electron, so the run has to be repeated".
- No Session 35 change reaches the transcript page or its test.
- Every TTS and AC-79 Electron test in the same run passed.
- The host had other worktrees' processes running at the time. A `zorivest-sched-credits` Python started at 01:22, during the Electron stage.
- W2-5 run alone passed 4/4 in 13.8 s (`C:/Temp/av-kit/s35-gate-flake-w25.txt`, exit 0).

Decision (autonomous, two-way): re-run the whole H1-2 gate with no file change, following the known issue's own disposition and the Session 33 A-13 and Session 39 D-30 precedents. A second miss stops for Mat. S6 does not apply: it covers the `--repeat-each` stage for this session's own tests, and nothing here adds a retry or touches a test.

### A-3 — post-correction gate run 2: capture-picker second-boundary race (Mat's ruling)

| Item | Value |
|---|---|
| Failure | `ui-tests` exit 1; the baseline rule found one id outside the baseline: `capture-picker.test.ts` AC-40.6 "claims _2 rather than overwriting when the second-resolution name is taken", `expected '2026-10-17_01-26-17.png' to match /_2\.png$/`. Everything before it passed, with the same `tested_state` as attempt 1. Receipts: `C:/Temp/av-kit/s35-gate-h1-r2fail2/`. |
| Classification | Test-only clock race, not a Session 35 regression. The test takes the current second's name, writes it, then publishes, and `claimInboxName` reads the clock again. When the two reads straddle a second, the name is free. Neither the test nor `ui/src/main` differs from 6097cf5; the file passed 5/5 alone (`s35-gate-flake-ac406.txt`). |
| Decision | Second miss, so it went to Mat (A-2). Options were: re-run unchanged and log a known issue; fix the race now; stop. Mat chose **fix the test race now** (2026-10-17). |
| Sibling sweep | `rg "registerFileName\(\|formatLocalTimestamp\(" ui/tests`: `capture-lifecycle.test.ts:406` AC-40.30 (a) "walks to _3" has the same race; fixed the same way. No other test builds an inbox name from the real clock. |
| Fix | Each of the two tests pins `Date` for its own body (`vi.useFakeTimers({ toFake: ['Date'] })`, `vi.setSystemTime(new Date(2026, 9, 17, 1, 26, 16, 999))`); only `Date` is faked, so timers and promises run normally. `capture-picker.test.ts`'s `afterEach` gains `vi.useRealTimers()` (`capture-lifecycle.test.ts` already had it). No assertion changed. `session-gate.ps1` `scope-paths` allows the two files. |
| Red | `s35-a3-red-ui.txt` (exit 1): the same pin plus a one-second clock step between naming and publication, so the boundary crossing is forced. 2 failed with the gate's exact message (`'2026-10-17_01-26-17.png'`). |
| Green | `s35-a3-green-ui.txt`: both files, three runs, `55 passed (55)` each, exit 0. |
| Next | H1-2 re-runs the whole gate (attempt 3). The gate script change moves `tested_state`; both handoffs are regenerated from attempt 3. |
| Attempt 3 | Exit 0: `session-gate: all steps exit 0`, `tested_state 6097cf59…4543+c7e4a6b9…32e3`, `changed paths: 39 outside scope: []`. The only accepted failures were py-tests `outside_baseline=[]` and ui-tests `outside_baseline=[]` (AC-41.3). Electron passed 161, e2e-repeat passed 50, and the identity was the same before and after. This is the record in the Closeout H1 table. |

## Execution review R2

Round 2 (ledger `s35-execution-2026-10-16-tts-voice-panel`, Codex) returned `changes_required`. F1 is `fixed`: the reviewer re-ran their probe on the corrected adapter and every case passed. There is one new finding, F2. The report is appended to `.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md`. After round 2 the ledger refused round 3 on its token budget, with 18.4M spent and 9.8M reserved, against a budget of 21M. Mat added 20M and pre-approved rounds up to the cap of 6 ("Add 20M, upt to 6 rounds pre-approved"). It is recorded with `review_ledger.py continue` (`s35-ledger-continue.txt`: tokens 18,411,384/41,000,000, rounds 2/6).

- **F2 (High, MEU-75, AC-75.9).** `_load_pytorch` imports `kokoro.KModel` lazily, and it caught only `ImportError`. If the engine is installed but fails to initialize, for example with an `OSError` from a native DLL, that exception escaped `load_model` bare. The load route then answered a masked HTTP 500. The reviewer's probe is `C:/Temp/av-kit/dispatch/s35-r2-import-probe.py`. The R1 sibling sweep had missed this statement, because it is an import rather than a call.

Corrections (`/execution-corrections`, D-23):

| Step | Exit | Decisive line |
|---|---|---|
| Red, 1 new AC-75.9 test (`:730`, an `OSError` and a `RuntimeError` import, plus the HTTP load) | 1 | `1 failed, 23 deselected`: `OSError: engine dependency DLL initialization failed` (`s35-f2-red-py.txt`) |
| Green, the same 5 test files unfiltered | 0 | `61 passed, 1 warning` (`s35-f2-green-py.txt`) |
| ruff check `packages/ tests/`; ruff format `--check` on the 2 files; pyright `packages/` | 0 | `All checks passed!`; `2 files already formatted`; `0 errors` (`s35-f2-ruff.txt`, `s35-f2-pyright.txt`) |
| H1-2 full gate re-run | see §A-4 and the Closeout H1 table | round 2 gate receipts kept in `C:/Temp/av-kit/s35-gate-h1-r2/` |

The fix:
- `ImportError` still raises `ModelLoadError("PyTorch runtime is not bundled")`.
- Any other exception from the import now logs one `tts.load_failed` and raises `ModelLoadError("PyTorch model failed to load")` from the cause. That is the same message and log as a failing constructor.
- The `load_model` docstring now names the initialization case.

Sibling sweep: `grep` finds one other import in the adapter, the module-level `import torch`. It runs when the sidecar imports the adapter, not during a load request, so it is outside AC-75.9.

The plan records the correction under §Execution Correction Notes, and so does the MEU-75 handoff (D-23, a FAIL_TO_PASS row, Red and Green records, and a History row).

### A-4 — post-F2 gate run 1: capture-inbox AC-66.14 pan origin (new flake)

| Item | Value |
|---|---|
| Failure | `ui-electron` exit 1, `1 failed, 160 passed (3.5m)`: `capture-inbox.test.ts:1141` AC-66.14, `expect(view.ox).toBeCloseTo(centred.ox - 40, 3)`, expected `-828.5`, received `-920.5`. Every earlier stage passed (`changed paths: 39 outside scope: []`, py and ui `outside_baseline=[]`). `e2e-repeat` and the identity steps did not run, because the gate stops at the first failure. Receipts: `C:/Temp/av-kit/s35-gate-h1-r3fail/`. |
| Classification | A flake, not a Session 35 regression. AC-66.14 belongs to an earlier capture session. No Session 35 file is under `ui/src/renderer/src/features/capture` or in `capture-inbox.test.ts`, and the only change since attempt 3 passed is the Python adapter and its test. Alone it passed 5/5 (`--repeat-each=5`, `s35-gate-flake-ac6614.txt`). Possible cause, not confirmed: the test reads the origin after a fixed two frames, which may not have settled under load. |
| Decision | Autonomous and reversible, following A-2: log the known issue `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` and re-run the whole gate with no file change. A second miss stops for Mat. The cause is unproven and the test belongs to another session, so this did not edit it (unlike A-3, where Mat ruled and the race was shown). |
| Run 2 | Exit 0: `session-gate: all steps exit 0`, `tested_state 6097cf59…4543+b4e8b882…1051`, `changed paths: 39 outside scope: []`. The only accepted failures were py-tests `outside_baseline=[]` and ui-tests `outside_baseline=[]` (AC-41.3). Electron passed 161 (AC-66.14 included), e2e-repeat passed 50, and the identity was the same before and after. This is the record in the Closeout H1 table (`s35-gate-h1/`, console `s35-h1-2-console.txt`). |

## Execution review R3 and R4 (approval)

Codex approved in round 3: verdict `approved`, intent achieved `yes`, F1 and F2 `fixed`, no new finding (ledger usage 8,919,831). Its report re-ran the F1 and F2 probes on the post-F2 tree and found that the tree's identity matched `tested_state 6097cf59…4543+b4e8b882…1051`.

### A-5 — H1-7b refused the round 3 approval (no Recheck Result table)

| Item | Value |
|---|---|
| Failure | H1-7a passed (`round 3 of 6; verdict=approved; open findings=2`), and H1-7b refused: `receipt records 2 open finding(s) that are not marked non-blocking while the verdict is 'approved'`. The validator carries round 1's F1 and round 2's F2 until a later `## Recheck` section closes each one in a table with a `Recheck Result` column (REVIEW-TEMPLATE §Prior Pass Summary). Neither the round 2 report nor the round 3 report had that table. Round 3's own Findings table marked both `fixed` and `no`, but an own Findings table does not close a carried finding. |
| Classification | A gap in the report's format, not in the code. The implementer did not write the table into the reviewer's verbatim text, because closing a finding is the reviewer's act. The template's sample cell `✅ Fixed` would not match the validator's closure pattern either, so the prompt asked for plain `fixed`. |
| Decision | Autonomous, within Mat's pre-approval of rounds up to the cap of 6: a narrow round 4 asked Codex to confirm that the tree had not changed and to add the Prior Pass Summary table (`C:/Temp/av-kit/dispatch/s35-exec-r4-prompt.txt`). |
| Round 4 | `approved`, intent `yes`. Codex re-derived the same `tested_state`, and its `Recheck Result` was `fixed` for both F1 and F2. Ledger usage was 2,340,844, for a loop total of 4 of 6 rounds. |
| H1-7a / H1-7b | Exit 0: `round 4 of 6; verdict=approved; open findings=0`; `approved at round 4 of 6, 0 open blocking findings`. Receipts are `review-state.json`, `review-state-check.txt` and `exec-review.txt`, in `C:/Temp/av-kit/s35-closeout/`. |

## Closeout H2

| Row | Exit | Result |
|---|---|---|
| H2-1 | n/a | Read the reflection template, `reflection.v1.yaml` and the 2026-10-14 backend-robustness reflection. |
| H2-2 | 1 (accepted) | Reflection OK: 15 sections, 7 schema fields, 3 rules, 25 decisions reconciled against 32 rows. `known-issues.md` is up to date and the drift check passed. The canon run reports `1 failed, 13 passed`; its only failure is queue-canon AC-41.3, the A-1 baseline id, with no unhandled error, so A-1 accepts it. MEU-75/79 are `approved`, and `TTS-MODEL-FLOW-GAPS` and `TTS-MODEL-ROW-LAYOUT` are `resolved`. Console: `C:/Temp/av-kit/s35-h2-2-console.txt`; receipts in `C:/Temp/av-kit/s35-closeout/`. |
| H2-3 | 0 | The `docs/execution/metrics.md` row for `2026-10-16-tts-voice-panel` was appended; `C:/Temp/av-kit/metrics-check.txt`. |
| H2-4 | 0 | Attempt 1 exited 3 (`FAIL-CLOSED: ... RECEIPTS_DIR is unset`) because the implementer's row wrapper left out `RECEIPTS_DIR`, against RULE-1 as restated above (receipt `C:/Temp/av-kit/closeout-preflight-attempt1.txt`). The row was re-run unchanged with `RECEIPTS_DIR=C:/Temp/av-kit` set: `OK: 24 row(s)`, 22 fully checked, 2 exempt (H1-5, H2-1); `C:/Temp/av-kit/closeout-preflight.txt`. |
| H2-5 | 0 | `C:/Temp/av-kit/commit-draft.txt` was written by the row as approved, with no attribution trailer. The row's `\n` is doubled for the markdown table, so the file holds a literal `
` and has no docs line. A readable draft with one message per MEU plus docs is in `C:/Temp/av-kit/commit-draft-s35.txt`. Nothing was committed. |

**Identity after H2.** After H2, `identity.py --state-only` derives `6097cf59…4543+b278250a…241d`, not the gate's `+b4e8b882…1051`. The identity excludes the plan's `.md` files, the handoffs, the reflection, metrics, current-focus and known-issues. It does not exclude `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md` or `docs/BUILD_PLAN.md`, which H2-2 re-rendered with MEU-75/79 `approved` as the row requires. A `find -newer` against `s35-gate-h1/s35-gate-h1.txt` lists only those three files and the excluded closeout artifacts. No product, test or gate file changed after the gate of record or the round 4 approval. Next time, the plan's identity should exclude the three status files.
