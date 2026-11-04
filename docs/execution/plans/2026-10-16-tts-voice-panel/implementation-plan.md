---
project: "2026-10-16-tts-voice-panel"
date: "2026-10-16"
source: "docs/build-plan/03-service-layer.md#tts-device-resolution-residual"
meus: ["MEU-75", "MEU-79"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: TTS voice panel — runtime devices and one aligned control row (Session 35)

> **Project:** `2026-10-16-tts-voice-panel`
> **Build plan:**
> - `docs/build-plan/03-service-layer.md` §TTS device resolution (residual) (`:459-470`, MEU-75; matrix row 3.8 added by row 7)
> - `docs/build-plan/11-page-layout.md` §TTS voice panel alignment (residual) (MEU-79; written by task row 1 from triage D-68, matrix row 11.13 added by row 7). Its neighbours §TTS model manager (`:105-119`, MEU-63) and §TTS text panel (`:121-135`, MEU-64, "Speed and Format are visible without scrolling") are Local Canon
>
> **Grouping:** `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, Session 35 (`:123-128`), decisions D-1 to D-7 (`:220-226`).
> **Known issues:** `TTS-MODEL-FLOW-GAPS` (`known-issues.yaml:2187`, triage D-66; items (1) and (2) remain, items (3) and (4) were fixed by MEU-76 in Session 33), `TTS-MODEL-ROW-LAYOUT` (`:2235`, triage D-68).
> **Status:** `draft`. Under `plan_to_exec_gate: human`, execution starts only on the user's explicit chat message after plan-review approval.
>
> Line anchors are from `main` `4a97483` (Sessions 32, 33 and 38 merged), which is also the worktree HEAD.

## Goal

Mat picked **cuda** for the PyTorch model on a CPU-only torch build, pressed Load, and got "Failed" (2026-10-09). The Device list offers `auto/cuda/cpu/mps` whatever the runtime has (`TTSPage.tsx:471-476`), and `_resolve_device` returns `cuda` when asked even when torch is absent or has no CUDA (`tts/adapter.py:54-68`). The same report says the Voice panel controls are irregular: two selects and a short button that wraps alone, and a Format select and Speed presets styled differently (D-68).

1. **MEU-75 — `svc-tts-device-fallback`.** The runtime decides which devices exist (`DEVICE_PROBE`). An unavailable request falls back to CPU with a `tts.device_fallback` log line, and a load that fails on an accelerator retries on CPU (`DEVICE_RESOLVE`, `LOAD_FALLBACK`). The model status reports the device actually used, which also fixes the ONNX path: it falls back today but still reports `cuda`. A load the adapter cannot complete raises `ModelLoadError` with its cause, and the API answers 422 with the reason (`LOAD_ERROR_HTTP`). Every catalog row carries the devices its format can use (`DEVICE_FIELD`).
2. **MEU-79 — `gui-tts-voice-panel-layout`.** The Device list shows only the selected row's devices (`DEVICE_SELECT_VALUE`). Model, Device and the model action share one grid row and one control height; the Speed slider and presets share a second row; Format, the voice search, the slider and the presets all use the 36 px control height (`VOICE_GRID`). Electron geometry at the default window pins it (`VOICE_GEOMETRY`).

Order (grouping `:125`): MEU-75 first, because the device list feeds the row MEU-79 lays out. The worktree baseline is the branch HEAD when execution starts; row 0 records it in `baseline.sha`. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from the s35 worktree (ls: No such file or directory, 2026-10-16); no headroom MCP or binary. Scope is the TTS load path (infra tts/adapter.py, core ports/tts.py and services/models.py, api schemas/routes models.py and errors.py) and the Voice panel (ui features/tts TTSPage.tsx, useTtsJob.ts, components/ui SegmentedControl.tsx), read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). It stops (S1) if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md` §Claude Code; `.agent/context/harness.local.md` §Claude Code).
  - `native_shell: pwsh`. Every validation goes through `rtk proxy` with the receipt pattern `*> C:/Temp/av-kit/<receipt>.txt; $code=$LASTEXITCODE; Get-Content …; exit $code`.
  - `plan_to_exec_gate: human`. Reviewer `approved` does not start execution; the user's explicit chat message does.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every non-`shared` row keeps `compact_continue` as its fallback.
- **Cloud/local split: not used.** Mat's Windows host is both the driver and the target, so the gates are authoritative where they run. There is no `validate-task.sh`/`.ps1` and no `local-requests.md`. Commands are the PROFILE D6 argv (`.agent/docs/commands.md:190-210`, including the MCP ids `mcp-types`, `mcp-tests`, `mcp-build`) plus targeted file lists.
- **Working directory:** the worktree root `P:/av-kit-wt/s35-tts-voice-panel` (`WT`, branch `claude/s35-tts-voice-panel`). D6 lists `P:/av-kit` as its default cwd; this plan runs the same argv from `WT` (D-8). Row 0 runs `uv sync --frozen --all-packages`, `npm --prefix ui ci` and `npm --prefix mcp-server ci` in `WT`.
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`; `.agent/skills/cli-dispatch/SKILL.md`). The plan was authored by Claude, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable, the fallback is Mat (PROFILE B3/B4). Self-review is never allowed.
- **Never:** commit, push, upload, publish, or write to YouTube; author an `approved` verdict; send secrets to a provider.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-75` | `.agent/context/handoffs/2026-10-16-tts-voice-panel-MEU-75-handoff.md` |
| `MEU-79` | `.agent/context/handoffs/2026-10-16-tts-voice-panel-MEU-79-handoff.md` |

Plan-local tooling (project artifacts, not product):

- [session-gate.ps1](session-gate.ps1) (rows 6 and H1-2)
- [identity.py](identity.py) (input identity, H1-6b)
- [red-check.py](red-check.py) (Red proof, rows 2 and 4)

Rolling reviews:

- `.agent/context/handoffs/2026-10-16-tts-voice-panel-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census, the 11 §TTS voice panel alignment section (task rows 0–1) | — | `shared` | `walkthrough.md` §Execution message, §Baseline, §Census; `baseline.sha`; 11 section |
| WP-1 | MEU-75 TDD: `DEVICE_PROBE`, `DEVICE_RESOLVE`, `LOAD_FALLBACK`, `LOAD_ERROR_HTTP`, `DEVICE_FIELD`, OpenAPI (rows 2–3) | WP-0 | `shared` | tests + source; Red/Green receipts; `walkthrough.md` §MEU-75 |
| WP-2 | MEU-79 TDD: `DEVICE_SELECT_VALUE`, `SEGMENT_SIZE`, `VOICE_GRID`, `VOICE_GEOMETRY` (rows 4–5) | WP-1 | `compact_continue` | tests + source; `walkthrough.md` §MEU-79; compact, then re-read `task.md` and the walkthrough |
| WP-3 | Session gate and hub reconciliation (rows 6–7) | WP-2 | `shared` | gate receipts in `walkthrough.md` §Gate; 03, matrix, `docs/BUILD_PLAN.md`, `meu-status.yaml` |
| WP-4 | H1 closeout, execution review, H2 | WP-3 | `compact_continue` | two handoffs, rolling review, reflection, metrics row |

---

## User Review Required

> [!IMPORTANT]
> These items are for the review loop and for the user's execution message. They are not a pause point.
>
> 1. **API contract change: a failed model load is 422, not 500 (`LOAD_ERROR_HTTP`, D-11).** `ModelLoadError` joins `DOMAIN_HTTP_MAP` at 422, beside `ExtractError`. A caller that cannot load a model (bad weights, a missing runtime, CPU retry failed) now receives `{code: "ModelLoadError", message}` instead of the masked 500. Any other unhandled exception keeps the masked 500. MCP passes the API error through unchanged (no MCP code change).
> 2. **The catalog gains a required `devices` field (`DEVICE_FIELD`, D-12).** `GET /models/available`, `GET /models/downloaded` and the `POST /models/download` response carry `devices` per row. `openapi.committed.json` changes only in `ModelVariantOut`.
> 3. **A stored device the row cannot use is shown as `auto`, not rewritten (`DEVICE_SELECT_VALUE`, D-13).** If Settings hold `cuda` and the selected model offers only `auto`/`cpu`, the select shows `auto` and Load sends `auto`; the stored `cuda` stays, so a row that offers CUDA shows it again. The alternative (rewriting the setting to `auto`) would lose the user's choice when they switch rows.
> 4. **Format moves to its own row at Device's width (`VOICE_GRID`, D-14).** The triage text (D-68) asks for one control height and field style, not one row. Format in the Speed row would leave the slider about 76 px at the default window (D-14 estimate), below the 96 px floor. If execution measures that the plan's two-row form overflows or the slider is under 96 px, that is S4.
> 5. **`TEST_AMENDMENTS` TA-1 to TA-6.** Each one changes an existing test that pins the old behaviour or enumerates the TTS port. They are listed in advance. Any other contradiction found by the census stops execution (S2).
> 6. **Optional visual check.** At the commit gate, Mat may open the TTS page in the dev app at the default window and compare it with the 2026-10-09 screenshot. This is non-blocking; the Electron geometry tests are the gate.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once, here. ACs, task rows and tests refer to these names and never restate the values.

| Name | Definition | Source |
|---|---|---|
| `PREREQS` | Before any edit: no `graphify-out*/`; in `meu-status.yaml`, MEU-62, MEU-63, MEU-64, MEU-67 and MEU-76 are `approved`, and MEU-75 and MEU-79 are `pending`; `errors.py` maps `ExtractError` (the MEU-76 precedent this plan extends) and `tts/adapter.py` defines `_resolve_device` (the function this plan replaces). | grouping `:125` (after Session 33); D-5 |
| `DEVICE_ORDER` | Device lists are always ordered `Auto, CUDA, CPU, MPS`, filtered to the members present. Wire names are the lowercase `DEVICE_WIRE_MAP` keys (`domain/wire.py:43`). | `TTSPage.tsx:471-476` order today |
| `DEVICE_PROBE` | `runtime_devices(fmt: ModelFormat) -> tuple[DeviceType, ...]`, a module function in `tts/adapter.py`, and `DeviceProbe = Callable[[ModelFormat], tuple[DeviceType, ...]]`. **PyTorch:** `Auto` and `CPU` always; `CUDA` iff `torch.cuda.is_available()`; `MPS` iff `torch.backends.mps.is_available()` (read with `getattr`, so a torch without `backends.mps` reports no MPS); module `torch` is `None` (not installed) → `(Auto, CPU)`. It reads the module-level `torch` on each call. **ONNX:** `Auto` and `CPU` always; `CUDA` iff `"CUDAExecutionProvider" in get_available_providers()` (new import from `onnxruntime` beside `InferenceSession`); never `MPS`. Results follow `DEVICE_ORDER`. `KokoroAdapter(..., device_probe: DeviceProbe \| None = None)` stores it, defaulting to `runtime_devices`. | 03:466 "come from the runtime"; 07 §GPU (detect at runtime); R-1; D-9 |
| `DEVICE_RESOLVE` | `load_model(variant, device)` picks the device to try from `probe = self._device_probe(variant.format)`. `Auto` → `CUDA` if in `probe`, else `MPS` if in `probe`, else `CPU`; no log. `CPU` → `CPU`. An explicit `CUDA` or `MPS` in `probe` → itself. An explicit device not in `probe` → `CPU`, logging `log.warning("tts.device_fallback", variant_id=…, requested=<wire>, actual="cpu", reason="unavailable")`. `_resolve_device` is removed. | 03:465; triage D-66; D-10 |
| `LOAD_FALLBACK` | After `DEVICE_RESOLVE`, the load keeps the existing initial `unload_model()` and builds the model or session in temporary locals. **PyTorch** — `KModel(...)` construction is not retried (it takes no device; retrying the same call cannot help); if `.to(<non-cpu>)` raises, retry once with `.to("cpu")` and log `tts.device_fallback` (`reason="load_failed"`); a raising `.eval()` is a final failure, not retried. **ONNX** — if the CUDA `InferenceSession(..., providers=_onnx_providers("cuda"))` raises, or `session.get_providers()` raises on the CUDA session (round 1 Q2: a session whose providers cannot be read cannot confirm its device), retry once with the CPU providers and log `reason="load_failed"`; if the CUDA session succeeds, the actual device is `cuda` only when `"CUDAExecutionProvider" in session.get_providers()`, else `cpu` with `reason="provider_fallback"`. The CPU session path never calls `get_providers`. **Final failure** (construction, `.eval()`, or the CPU attempt): raise `ModelLoadError("PyTorch model failed to load")` / `ModelLoadError("ONNX session failed")` `from` the original exception, after `log.error("tts.load_failed", variant_id=…, device=<last tried>, error=type(exc).__name__)`; messages name no path. **State:** the model/session, variant and `_device_name` fields are set only after every stage succeeds; after a failed load, including one that follows an earlier successful CUDA load, no model is loaded (`get_model_status().is_loaded is False`), `device == "cpu"`, and no stale `_device_name` or partial model remains. The existing missing-weight `ModelLoadError` with a `FileNotFoundError` cause (`adapter.py:81`, AC-9.4 `:387`) is unchanged. | 03:465, 03:467; Local Canon AGENTS §Code Quality; D-10 |
| `LOAD_ERROR_HTTP` | `DOMAIN_HTTP_MAP[ModelLoadError] = 422` (`errors.py:27-41`). The existing domain handler (`:130-150`) then returns the 422 envelope with `code == "ModelLoadError"` and `message == str(exc)`. A non-domain exception keeps the masked 500. | 03:467; MEU-76 `ExtractError` 422 precedent; D-11 |
| `DEVICE_FIELD` | `TTSPort.available_devices(fmt: ModelFormat) -> tuple[DeviceType, ...]` (`ports/tts.py`); `KokoroAdapter.available_devices` returns `self._device_probe(fmt)`; `ModelService.available_devices(fmt)` passes through to its TTS port. `ModelVariantOut.devices: list[Literal["auto", "cuda", "cpu", "mps"]]`, required (`schemas/models.py:35`). `_variant_out(variant, devices)` (`routes/models.py:35`) fills it with the wire names (inverse of `DEVICE_WIRE_MAP`, built once in the route module) for `/models/available`, `/models/downloaded` and the `/models/download` response. `ModelLoadIn` is unchanged. `openapi.committed.json` is regenerated; its only change is `ModelVariantOut.properties.devices` and `devices` in its `required`. | 03:466; D-12 |
| `DEVICE_SELECT_VALUE` | `CatalogItem` (`useTtsJob.ts:49`) gains `devices?: string[]`. `deviceOptions = selectedModel?.devices ?? ['auto', 'cpu']`. `effectiveDevice = deviceOptions.includes(device) ? device : 'auto'`. `device-select` lists `deviceOptions` and shows `effectiveDevice`; Load posts `effectiveDevice`. Only a user change to the select calls `persistLeaf({device})` (as today); `effectiveDevice` is never persisted. | 03:466 "the TTS page lists only those"; D-13 |
| `SEGMENT_SIZE` | `SegmentedControl` gains `size?: 'sm' \| 'md'` (default `'sm'`). With `'sm'` or no `size` the rendered markup is byte-identical to the baseline. `'md'` appends ` h-9` to the inner `div`'s class string and changes nothing else; the labels stretch to the inner height (flex default) and stay centred (`items-center`). | `SegmentedControl.tsx:32`; Button `md` = `h-9` (`Button.tsx:24`); D-15 |
| `VOICE_GRID` | **Model row** (`data-testid="model-row"`): `grid grid-cols-[minmax(0,1fr)_7rem_auto] items-end gap-2`; `model-select` and `device-select` lose their `className` (their `SelectInput` root `div`s are the grid items and the selects stay `w-full h-9`); the model action button is `size="md"`. **Speed row** (the `div` around the Speed label): `grid grid-cols-[minmax(0,1fr)_auto] items-end gap-2`; the label is `flex min-w-0 flex-col gap-1`; its text `span` is `text-sm font-medium text-fg-muted` (the `SelectInput` label style); `speed-slider` gets `h-9 w-full`; the presets are `SegmentedControl size="md"`. **Format:** `format-select` sits in `<div className="w-28">` (7rem, Device's width) and loses `w-[90px]`. The voice combobox is unchanged (its input is already `h-9`, `VoiceCombobox.tsx`). No test id is added, removed or renamed. | Triage D-68; 11 §TTS model manager "Device stays beside it"; D-14 |
| `VOICE_GEOMETRY` | In Electron at the default window (1280×800, `ui/src/main/index.ts:140`), after `/tts/voices` resolves and two animation frames: (a) `model-select`, `device-select` and the model action button (located by its actual test id from `MODEL_ACTION_TEST_IDS`; the seam's default loaded state renders `unload-btn`, round 1 Q4) have equal height and equal bottom (±0.5 px), and their label tops (`model-select`/`device-select` labels) are equal (±0.5 px); `model-select` is wider than `device-select`; (b) `voice-combobox`, `format-select`, `speed-slider` and the preset group's inner `div` (`getByRole('group', { name: 'Speed preset' }).locator('> div')`) each have `model-select`'s height (±0.5 px); `speed-slider` and the preset inner `div` have equal bottoms (±0.5 px); `format-select` has `device-select`'s width (±0.5 px); (c) `model-row` and the speed row (`speed-slider`'s grandparent) have `scrollWidth <= clientWidth`, and `speed-slider` is at least 96 px wide. AC-64.6 stays green. | Triage D-68; AC-64.6 precedent; D-16 |
| `E2E_DEVICE_SEAM` | The `tts-generate.test.ts` seam's `__e2eCatalog` type (`:36-44`) and rows (`:65-100`) gain `devices`: ONNX rows `['auto', 'cpu']`, the PyTorch row `['auto', 'cuda', 'cpu']`. | D-17 |
| `TEST_AMENDMENTS` | **TA-1** `tests/integration/test_tts_models.py` AC-9.4 (`:436`): before the explicit `DeviceType.CUDA` load that expects `"cuda"`, the test makes the probe report CUDA (monkeypatch `torch.cuda.is_available` → `True` on the adapter module's torch, or pass a `device_probe` that includes CUDA). The patch or probe is scoped to that explicit CUDA case only; the other AC-9.4 cases (`:387`, `:402`, `:420`) run unchanged under the real probe. `tests/integration/test_tts_models.py:43` `TTS_PORT_METHODS` is an iteration subset (`:313`), not a complete-protocol check, and needs no change (round 1 Q6). **TA-2** `tests/e2e/api_fakes.py` `FakeModels` (`:344`) gains `available_devices(fmt)` returning `(DeviceType.Auto, DeviceType.CPU)`. **TA-3** `tests/unit/test_domain.py:1153` `TTS_PORT_METHODS` gains `"available_devices"`. **TA-4** `tests/unit/test_services.py` `FakeTTSPort` gains `available_devices`. **TA-5** `ui/tests/unit/tts-page.behavior.test.ts` fixtures that render the catalog gain `devices` where a test selects a device outside `['auto', 'cpu']` (none expected: AC-56.3 selects `cpu`, `:529` posts `auto`). **TA-6** `ui/tests/e2e/tts-generate.test.ts`: `E2E_DEVICE_SEAM`. Amendments change only those lines; every other line in those tests stays. | Local Canon |
| `CENSUS_PATTERNS` | Row 1 greps `tests`, `ui/tests` and `mcp-server/tests` for `device`, `_resolve_device`, `device-select`, `ModelVariantOut`, `get_providers`, `providers`, `is_available`, `DOMAIN_HTTP_MAP`, `ModelLoadError`, `model-row`, `size="sm"`, `SegmentedControl`, `format-select`, `speed-slider`, `w-[110px]`, `w-[90px]`, `FakeModels`, `FakeSession`, `is_downloaded`, `TTS_PORT_METHODS`, `FakeTTSPort`, `TTS_DEVICES`, `DEVICE_VALUES` and `def get_model_status`. Each hit is dispositioned: `TA-n`, `unaffected` with the reason, or `new-contradiction`, which triggers S2. | Local Canon (Session 36/39 census) |
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the Files Modified rows below; `session-gate.ps1` `scope-paths` holds the same allow-list. | grouping `:125` |

### MEU-75 — `svc-tts-device-fallback`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `TTSPort.available_devices` (`ports/tts.py`) | Protocol | `ModelFormat` in; tuple of `DeviceType` out (`DEVICE_ORDER`) | n/a |
| `KokoroAdapter.load_model` (`tts/adapter.py`) | `DEVICE_RESOLVE`, `LOAD_FALLBACK` | `DeviceType` in; raises `ModelLoadError` only | n/a |
| REST `GET /models/available`, `GET /models/downloaded`, `POST /models/download` | `ModelVariantOut` (`schemas/models.py:35`) | `devices`: required list of `"auto" \| "cuda" \| "cpu" \| "mps"` | response model |
| REST `POST /models/load` body | `ModelLoadIn` (unchanged, `schemas/models.py:32`) | `device` in the four wire names, default `auto` → 422 otherwise | `extra="forbid"` (ApiModel) → 422 |
| REST error envelope | `DOMAIN_HTTP_MAP` (`errors.py:27`) | `ModelLoadError` → 422 `{code, message}` | n/a |
| OpenAPI (`openapi.committed.json`) | generated | `ModelVariantOut.devices` (array of the enum; required) | unchanged |
| MCP `avkit_models` | passes the API body and error through | unchanged | unchanged |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-75.1 | unit | `runtime_devices(PyTorch)` over the matrix: cuda False/mps absent → `(Auto, CPU)`; cuda True → `(Auto, CUDA, CPU)`; mps True → `(Auto, CPU, MPS)`; both → `(Auto, CUDA, CPU, MPS)`; module `torch` patched to `None` → `(Auto, CPU)`; a fake torch whose `backends` has no `mps` → no MPS. In a fresh interpreter with torch blocked (`test_tts_no_torch.py`), `runtime_devices(PyTorch)` is `(Auto, CPU)`. | 03:466; `DEVICE_PROBE` | cuda False is never reported as CUDA (asserted on every row) |
| AC-75.2 | unit | `runtime_devices(ONNX)`: providers `['CPUExecutionProvider']` → `(Auto, CPU)`; with `'CUDAExecutionProvider'` → `(Auto, CUDA, CPU)`; MPS is never listed, even when the torch patch says mps True. | 03:466; `DEVICE_PROBE` | `['TensorrtExecutionProvider', 'CPUExecutionProvider']` gives no CUDA |
| AC-75.3 | unit | `DEVICE_RESOLVE`: with a CPU-only probe, a PyTorch load with `CUDA` (and one with `MPS`) loads on CPU, `get_model_status().device == "cpu"`, and exactly one `tts.device_fallback` record carries `requested`, `actual="cpu"`, `reason="unavailable"` (structlog capture). | 03:465; triage D-66 | A `CPU` request, and a `CUDA` request whose probe has CUDA, log no `tts.device_fallback` |
| AC-75.4 | unit | PyTorch `LOAD_FALLBACK`: with a probe that has CUDA and a fake `KModel` whose `.to("cuda")` raises `AssertionError`, the load retries on CPU, status device is `cpu`, and one `tts.device_fallback` has `reason="load_failed"`. If `.to("cpu")` also raises, `load_model` raises `ModelLoadError` whose `__cause__` is that exception, one `tts.load_failed` is logged, status is not loaded with device `cpu`, and `str(error)` contains no part of the weight path. A `KModel` constructor that raises is wrapped the same way and not retried (`.to` never called); an `.eval()` that raises is wrapped the same way, with no partial success. Every failure case starts from a prior successful CUDA load and asserts the terminal state: not loaded, device `cpu`, no stale `_device_name` (round 1 Q2). | 03:465, 03:467 | Without the wrap, the bare `AssertionError` would escape: the test asserts `pytest.raises(ModelLoadError)` and the cause type |
| AC-75.5 | unit | ONNX `LOAD_FALLBACK`: with a CUDA probe, a fake session whose `get_providers()` returns only `CPUExecutionProvider` gives status device `cpu` and `reason="provider_fallback"`; a CUDA session constructor that raises retries with the CPU providers (status `cpu`, `reason="load_failed"`); a CUDA session whose `get_providers()` raises also retries with the CPU providers (`reason="load_failed"`); a CPU constructor that raises gives `ModelLoadError` with the original cause. A CPU-only load never calls `get_providers` (the fake records calls); every fake session used with a CUDA request provides `get_providers()`. Each failure case starts from a prior successful CUDA load and asserts the terminal state: not loaded, device `cpu`, no stale `_device_name` (round 1 Q2). | 03:465 ("status reports the actual device") | The baseline bug: a CUDA retry that still reports `cuda` fails the status assertion |
| AC-75.6 | unit | `Auto` resolution: probe `(Auto, CUDA, CPU, MPS)` → CUDA; `(Auto, CPU, MPS)` → MPS; `(Auto, CPU)` → CPU; no `tts.device_fallback` in any case. | `DEVICE_RESOLVE` | `Auto` on a CPU-only probe never tries `.to("cuda")` (the fake records the device) |
| AC-75.7 | unit | Port and service: `KokoroAdapter.available_devices(fmt)` returns the injected probe's result; `ModelService.available_devices(fmt)` returns its port's; `TTS_PORT_METHODS` lists `available_devices` (TA-3); `FakeTTSPort` implements it (TA-4). | `DEVICE_FIELD` | A port fake without the method fails the TA-3 protocol check |
| AC-75.8 | integration | API: each item of `GET /models/available` and `GET /models/downloaded`, and the `POST /models/download` variant, has `devices == ['auto', 'cpu']` from `FakeModels` (TA-2); with a `FakeModels` returning `(Auto, CUDA, CPU)` it is `['auto', 'cuda', 'cpu']`. `openapi.committed.json` `ModelVariantOut` lists `devices` in `required`, as an array whose items enum is the four wire names. The tests read the field with `.get("devices")` so its absence is an assertion line. | 03:466; `DEVICE_FIELD` | `POST /models/load` with `device: "tpu"` is 422 |
| AC-75.9 | integration | `LOAD_ERROR_HTTP` and the status contract. `DOMAIN_HTTP_MAP[ModelLoadError] == 422`; a load route raising `ModelLoadError("ONNX session failed")` returns 422 with `code == "ModelLoadError"` and that message (`test_api_error_surface.py`, `make_bundle`/`replace`). Contract (`test_tts_device_resolution.py`): a real `KokoroAdapter` with stub engines and a CPU-only probe behind a `FakeModels` subclass whose `load` calls `adapter.load_model` and whose `get_status` returns `adapter.get_model_status()`: `POST /models/load {device: "cuda"}` returns 200 with `device == "cpu"`, and `GET /models/status` reports `cpu`. | 03:465, 03:467, 03:468 ("contract test for the status device") | A route raising `RuntimeError` still returns the masked 500 (no message leak) |
| AC-75.10 | integration | The real probe agrees with the installed runtimes: `runtime_devices(PyTorch)` contains CUDA iff `torch.cuda.is_available()` (or no CUDA when torch is absent), and `runtime_devices(ONNX)` contains CUDA iff `"CUDAExecutionProvider" in onnxruntime.get_available_providers()`. | 07 §GPU (detect at runtime); R-1 | On the CPU-only host the real probe reports neither CUDA nor MPS (R-1 environment; asserted from the live runtime, not hard-coded) |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Fallback on an unavailable device | Spec | 03:465 (`DEVICE_RESOLVE`) |
| Fallback when the accelerator load fails | Spec / Local Canon | 03:465 "as it already does for ONNX" (`adapter.py:198-202`) → `LOAD_FALLBACK` for both formats |
| ONNX actual device | Spec | 03:465 "the model status reports the actual device"; `session.get_providers()` is the runtime's own answer (D-10) |
| Device list per format | Spec / Research-backed | 03:466; ONNX: providers list; PyTorch: torch flags; ONNX never MPS (no CoreML provider in this build; D-9) |
| Error mapping and status code | Spec / Local Canon | 03:467 `ModelLoadError` with the cause; 422 per the MEU-76 `ExtractError` precedent (D-11) |
| Catalog transport | Spec | 03:466 "the TTS page lists only those" needs the devices on the row the page selects (D-12) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/ports/tts.py` | modify | `TTSPort.available_devices` |
| `packages/core/src/avkit_core/services/models.py` | modify | `ModelService.available_devices` passthrough |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | `runtime_devices`, `DeviceProbe`, `device_probe` param, `available_devices`; `DEVICE_RESOLVE` and `LOAD_FALLBACK` in `load_model`; `_resolve_device` removed; `get_available_providers` import |
| `packages/api/src/avkit_api/schemas/models.py` | modify | `ModelVariantOut.devices` |
| `packages/api/src/avkit_api/routes/models.py` | modify | `_variant_out(variant, devices)`; wire-name inverse map |
| `packages/api/src/avkit_api/errors.py` | modify | `ModelLoadError` → 422 |
| `openapi.committed.json` | regenerate | `tools/export_openapi.py -o openapi.committed.json` |
| `tests/integration/test_tts_device_resolution.py` | new | AC-75.1, .3, .4, .5, .6, .9 (contract), .10 |
| `tests/integration/test_tts_models.py` | modify | TA-1 |
| `tests/integration/test_tts_no_torch.py` | modify | AC-75.1 (torch-blocked interpreter case) |
| `tests/unit/test_domain.py` | modify | TA-3 |
| `tests/unit/test_services.py` | modify | AC-75.7, TA-4 |
| `tests/e2e/api_fakes.py` | modify | TA-2 |
| `tests/e2e/test_api_tts_models.py` | modify | AC-75.8 |
| `tests/e2e/test_api_error_surface.py` | modify | AC-75.9 (map and envelope) |

AC-75.2 lives in `test_tts_device_resolution.py` with AC-75.1.

### MEU-79 — `gui-tts-voice-panel-layout`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `GET /models/available` items read by the page (`useTtsJob.ts:95`) | `CatalogItem` | `devices?: string[]`; absent → `['auto', 'cpu']` | extra fields ignored (existing) |
| `POST /models/load` body sent by the page | `ModelLoadIn` | `device` = `effectiveDevice` (always in the row's list) | unchanged |
| `PUT /settings` leaf `device` | Settings | written only on a user change of `device-select` (unchanged) | unchanged |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-79.1 | integration | Behaviour (Vitest, rendered page): with an ONNX row `devices: ['auto', 'cpu']` selected, `device-select` options are exactly `auto, cpu`; selecting a PyTorch row with `['auto', 'cuda', 'cpu']` changes them to `auto, cuda, cpu`. | `DEVICE_SELECT_VALUE` | The static four (`auto, cuda, cpu, mps`) never appear for either row |
| AC-79.2 | integration | Settings `device: 'cuda'` with an `['auto', 'cpu']` row selected: the select shows `auto`, Load posts `{variant_id, device: 'auto'}`, and no `PUT /settings` is sent; selecting the `['auto', 'cuda', 'cpu']` row shows `cuda`. | `DEVICE_SELECT_VALUE`; D-13 | Load never posts `cuda` for the `['auto', 'cpu']` row |
| AC-79.3 | integration | A catalog row without `devices` gives options `auto, cpu`. | `DEVICE_SELECT_VALUE` | `mps` is not offered |
| AC-79.4 | integration | Characterization: `POST /models/load` answering 422 `{code: "ModelLoadError", message: "ONNX session failed"}` shows that message in `error-banner` (the existing `ApiError` → `run()` path). Green at Red; it guards the path `LOAD_ERROR_HTTP` relies on. | `LOAD_ERROR_HTTP`; `api.ts` `apiFetch` | The banner never shows "Failed to fetch" for this response |
| AC-79.5 | unit | `SEGMENT_SIZE` (`layout-primitives.test.ts`): the inner `div` class of a default render and of `size="sm"` equals the baseline literal `inline-flex rounded-[var(--radius-control)] border border-border bg-surface-0 p-0.5`; `size="md"` equals that plus ` h-9`; the inner `div`'s `innerHTML` (labels and radios) is identical for `sm` and `md`. | `SEGMENT_SIZE` | The default render does not contain `h-9` |
| AC-79.6 | integration | DOM classes (Vitest): `model-row` has `grid` and no `flex-wrap`; `device-select` and `model-select` have no `w-[110px]`/`flex-1` classes; the model action button has `h-9`; `format-select`'s parent is `w-28` and the select has no `w-[90px]`; `speed-slider` has `h-9`; the speed row has `grid`. | `VOICE_GRID` | The baseline `flex flex-wrap` model row fails |
| AC-79.7 | integration | Electron: `VOICE_GEOMETRY` (a). | Triage D-68 | Red on the baseline renderer: the `sm` button (28 px) differs from the 36 px selects |
| AC-79.8 | integration | Electron: `VOICE_GEOMETRY` (b). | Triage D-68 | Red on the baseline renderer: the preset group and the slider are not 36 px, and Format is 90 px wide |
| AC-79.9 | integration | Electron: `VOICE_GEOMETRY` (c), and AC-64.6 passes in the same run. | 11 §TTS text panel "Space"; D-14 | Overflow or a slider under 96 px is S4, never a relaxed bound |
| AC-79.10 | integration | Electron: with `E2E_DEVICE_SEAM`, `device-select` has 2 options for ONNX FP32 and 3 (`auto, cuda, cpu`) after selecting PyTorch FP32 in `model-select`. | `DEVICE_SELECT_VALUE` | Red on the baseline renderer: 4 options |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Device list on the page | Spec | 03:466 "the TTS page lists only those" (`DEVICE_SELECT_VALUE`) |
| A stored device the row lacks | Research-backed / Local Canon | D-13: show and send `auto`, keep the stored value (no silent settings write) |
| Model row layout | Spec (triage D-68) | One grid row, Model flexes, Device fixed, one control height, labels top-aligned, no wrap (`VOICE_GRID`) |
| Speed, Format, voice search | Spec (triage D-68) | Same control height and field style (`VOICE_GRID`, `SEGMENT_SIZE`) |
| Format placement | Research-backed | D-14: own row at Device's width; the three-column alternative leaves the slider under 96 px |
| Geometry proof | Local Canon | AC-64.6 method at the default window (`VOICE_GEOMETRY`) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | `DEVICE_SELECT_VALUE`, `VOICE_GRID` |
| `ui/src/renderer/src/features/tts/useTtsJob.ts` | modify | `CatalogItem.devices?` |
| `ui/src/renderer/src/components/ui/SegmentedControl.tsx` | modify | `SEGMENT_SIZE` |
| `ui/tests/unit/tts-page.behavior.test.ts` | modify | AC-79.1–79.4, AC-79.6; TA-5 |
| `ui/tests/unit/layout-primitives.test.ts` | modify | AC-79.5 |
| `ui/tests/e2e/tts-generate.test.ts` | modify | AC-79.7–79.10; TA-6 (`E2E_DEVICE_SEAM`) |

### Hub and state files (rows 1, 7, H1-3, H2)

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/11-page-layout.md` | modify (row 1) | New heading `## Residuals registered 2026-10-09` before `## Supersession` (`:151`), with `<a id="tts-voice-panel-alignment-residual"></a>` and `### TTS voice panel alignment (residual)`: a `> **MEU-79.** Known issue \`TTS-MODEL-ROW-LAYOUT\` …` note, then the Rule \| Contract \| Source table (Model row, Shared height, Speed and Format, Device list, Geometry, Test IDs "all keep; none added"), sourced to triage D-68 and this plan's `VOICE_GRID`/`VOICE_GEOMETRY`, and a "Migration record:" line naming this plan. Gated docs are open: grouping D-1's condition (Session 30 approved) is met |
| `docs/build-plan/03-service-layer.md` | modify (row 7) | After the §TTS device resolution table (`:470`): `> **Delivered (Session 35).** D-9–D-12: …` naming `DEVICE_PROBE`, `DEVICE_RESOLVE`, `LOAD_FALLBACK`, `LOAD_ERROR_HTTP`, `DEVICE_FIELD`, and `Plan \`docs/execution/plans/2026-10-16-tts-voice-panel/\`.` (Session 32 note format) |
| `docs/build-plan/build-priority-matrix.md` | modify (row 7) | Add `\| 3.8 \| MEU-75 \| \`svc-tts-device-fallback\` \| [03 §TTS device resolution (residual)](03-service-layer.md#tts-device-resolution-residual) \| MEU-62, MEU-63 \|` after row 3.7 (`:36`) and `\| 11.13 \| MEU-79 \| \`gui-tts-voice-panel-layout\` \| [11 §TTS voice panel alignment (residual)](11-page-layout.md#tts-voice-panel-alignment-residual) \| MEU-63, MEU-75 \|` after row 11.12 (`:98`) |
| `.agent/context/meu-status.yaml` | modify (row 7, H2-2) | Phase 3 note (`:39`) and Phase 11 note (`:135-136`) name Session 35; MEU-79's description (`:2088`) drops "Spec section authored after Session 30 approval (GATED_PATHS)" and points at the new 11 anchor; MEU-75/79 `execution_plan` and `ready_for_review` (row 7, before the H1-2 gate binds this file; round 1 F3); `approved` after review (H2-2, which re-runs `layout-canon` and `queue-canon`) |
| `docs/BUILD_PLAN.md` | generated | AUTOGEN regions written only by `meu_status.py render` |
| `.agent/context/meu-registry.md` | generated | written by `meu_status.py render`; never hand-edited |
| `.agent/context/current-focus.md` | modify | the current focus names Session 35 (H1-3) |
| `.agent/context/known-issues.yaml` | modify | both issues → `resolved` with the handoff links, after H1-7b approval (H2); `TTS-MODEL-FLOW-GAPS` notes that items (3)–(4) closed with MEU-76 |
| `.agent/context/known-issues.md` | generated | written by `issue_triage.py render` (H2-2); never hand-edited |
| `docs/execution/metrics.md` | modify | the Session 35 row (H2-3) |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A CUDA torch or `onnxruntime-gpu` in the bundle | out-of-scope | — | 07 §GPU: detect at runtime; packaging owns the build choice. This plan only reports what is installed |
| ONNX on Apple silicon (CoreML provider) | out-of-scope | — | No CoreML provider in this build (R-1); ONNX never lists MPS |
| Persisting the effective device back to Settings | out-of-scope | — | D-13: the stored choice is kept on purpose |
| An MCP `devices` argument or listing change | out-of-scope | — | MCP passes the catalog body through; no MCP schema names devices (census confirms) |
| Voice combobox styling | out-of-scope | — | Already `h-9` with the shared field style (`VoiceCombobox.tsx`) |
| Re-laying out the Text panel or the run bar | out-of-scope | — | MEU-64 and TT7 own them; AC-64.6 guards the space rule |
| The CORS-less 500 and unlogged errors (`TTS-MODEL-FLOW-GAPS` items 3–4) | delivered | MEU-76 | Session 33 (`approved`) |

## BUILD_PLAN.md Audit

This project edits the D3 hub in task rows 1 and 7 only (§Hub and state files). The validation is exact:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s35-state-render.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s35-state-render.txt; exit $code
```

```powershell
rtk proxy rg -n -e "MEU-7[59]" -e "3\.8 . MEU-75" -e "11\.13 . MEU-79" -e "tts-voice-panel" -e "tts-voice-panel-alignment-residual" -e "Delivered \(Session 35\)" docs/BUILD_PLAN.md docs/build-plan/build-priority-matrix.md docs/build-plan/03-service-layer.md docs/build-plan/11-page-layout.md *> C:/Temp/av-kit/s35-hub-rg.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s35-hub-rg.txt; exit $code
```

Row 7's deliverable is that the `rg` receipt shows each edit (matrix rows 3.8 and 11.13, the 03 Delivered note, the 11 anchor and section, the Phase 3/11 lines that `render` writes from `meu-status.yaml`), a second `rg` for `after Session 30 approval` over `meu-status.yaml` returns no MEU-79 line, and `render --check` exits 0.

## Verification Plan

All commands run from `WT` in `pwsh`, after `$env:ELECTRON_RUN_AS_NODE=$null` for any Electron step. Receipts go to `C:/Temp/av-kit/s35-*.txt`. The ids are PROFILE D6's (`.agent/docs/commands.md:190-210`); targeted runs are those argv with a file list.

### 1. Prerequisites and baseline (row 0)

- `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `npm --prefix mcp-server ci`.
- `PREREQS` (S1).
- `git rev-parse HEAD > docs/execution/plans/2026-10-16-tts-voice-panel/baseline.sha`.
- The baseline receipts: `py-tests`, `ui-tests`, `mcp-tests`, `ui-build`, then `ui-electron` over `tts-generate.test.ts`. The baseline failed sets are recorded in `walkthrough.md` §Baseline. A test failing at baseline is never counted as a regression, and a test passing at baseline that fails later is.

### 2. Red (rows 2 and 4)

Each MEU's new and amended tests are written first. They must fail by assertion, or because a declared-new name does not exist yet (`red-check.py` `DECLARED_NEW`: `runtime_devices`, `available_devices`, `DeviceProbe`, `device_probe`, `get_available_providers`).

- **Python imports of new names go inside the test function**, so a missing name fails that test with an `E ImportError` line instead of breaking collection of the whole module (which would hide the existing tests and is refused by `red-check.py` as a setup failure). A test that monkeypatches `get_available_providers` on the adapter module fails with `has no attribute 'get_available_providers'`, which is declared.
- **A missing response field is an assertion, not a `KeyError`:** pytest reads `item.get("devices")`; Vitest compares the rendered option values with `toEqual`. `red-check.py` refuses a bare `KeyError` line.
- **Row 2 (MEU-75):** pytest `-k "ac_75"` over the MEU-75 test files, with TA-1 to TA-4 applied. TA-2 to TA-4 add a method no product code calls yet, so they stay green; TA-1 fails only if the probe-based code is missing (it is green at Red too, because the baseline returns `cuda` when asked). The receipt fails on the AC-75 tests.
- **Row 4 (MEU-79):** Vitest `-t "AC-79"` over the two unit files, then the UI build and Electron `--grep "AC-79"` over `tts-generate.test.ts` **on the row 3 tree, whose renderer is the baseline renderer** (row 3 refuses any `ui/src` change). AC-79.4 is a characterization test and passes at Red; the receipt still fails on the other AC-79 tests. AC-79.9 may pass at Red (the baseline rows do not overflow); AC-79.7, .8 and .10 must fail by `expect`, which the checker enforces with `--require AC-79.7 --require AC-79.8 --require AC-79.10` (round 1 F1).

`RED_PROOF`: [red-check.py](red-check.py) decides each Red. Each Red command writes its child exit code to `<receipt>.exit` straight after `$code=$LASTEXITCODE`. The checker requires:

- a non-zero exit and exactly one failing-run summary (pytest, Vitest or Playwright);
- no hard setup failure anywhere in the receipt: Electron launch, a test or action timeout, a refused connection or busy port, a pytest collection error (`ERROR collecting`, or `Interrupted: N error during collection`, which stops the whole run), or Vitest unhandled errors;
- **every failure block is attributed** (round 1 F1): the receipt is split into one block per failed test (pytest `____ name ____` sections, Vitest `FAIL` headers, Playwright `N) title` headers), and the number of blocks equals the summary's failed (and pytest error) count, so a failure that is not shown cannot hide. Every block must carry at least one diagnostic, and **every** diagnostic in it must be an assertion (`AssertionError`, a pytest `assert` or `Failed: DID NOT RAISE` line, `Error: expect(`) or a load/import/attribute/keyword error whose missing *subject* is exactly a declared-new name (or ends in one after a `.` or `/`). The subject comes from the error's own grammar (`cannot import name 'X'`, `has no attribute 'X'`, `unexpected keyword argument 'X'`, …); a declared name elsewhere on the line, or a name that only starts with one, does not count. One unrelated diagnostic refuses the block, even beside a valid assertion;
- **`--require TITLE`** (row 4: AC-79.7, AC-79.8, AC-79.10): each named test has its own failure block whose diagnostics are all assertions. A required test that passed, or failed only by a declared-new name, is refused. The title match is exact (`AC-79.7` does not match `AC-79.70`).

Source-context and test-title lines never count. `red-check.py --selftest` runs 35 receipt fixtures, 11 positive and 24 negative (R-3), and R-6 runs it over real Session 37 receipts.

### 3. Targeted Green (rows 3 and 5)

Row 3 runs the pytest command, regenerates and checks OpenAPI, and proves no `ui/src` file changed. Row 5 runs the Vitest command, then the build and the whole `tts-generate.test.ts`.

```powershell
rtk proxy uv run pytest tests/integration/test_tts_device_resolution.py tests/integration/test_tts_models.py tests/integration/test_tts_no_torch.py tests/unit/test_domain.py tests/unit/test_services.py tests/e2e/test_api_tts_models.py tests/e2e/test_api_error_surface.py -q --tb=short *> C:/Temp/av-kit/s35-py-targeted.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s35-py-targeted.txt | Select-Object -Last 25; exit $code
```

```powershell
rtk proxy npm --prefix ui run test -- tests/unit/tts-page.behavior.test.ts tests/unit/layout-primitives.test.ts *> C:/Temp/av-kit/s35-ui-targeted.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s35-ui-targeted.txt | Select-Object -Last 25; exit $code
```

```powershell
$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s35-ui-build.txt; if ($LASTEXITCODE -ne 0) { Get-Content C:/Temp/av-kit/s35-ui-build.txt | Select-Object -Last 25; exit $LASTEXITCODE }; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/tts-generate.test.ts *> C:/Temp/av-kit/s35-e2e-tts.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s35-e2e-tts.txt | Select-Object -Last 30; exit $code
```

### 4. Session gate (rows 6, H1-2): `session-gate.ps1`

The plan-local [session-gate.ps1](session-gate.ps1) runs in `pwsh` from `WT`. It writes one receipt per step (`C:/Temp/av-kit/s35-D6-<id>.txt`) and prints `<id> stage=<stage> exit=<n>` and the receipt tail. It is fail-fast in stage order: after the first non-zero step, every later step is printed as `not_run`. The steps, in order:

1. `identity-before`: `INPUT_IDENTITY` (§Validation stage contract).
2. **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, then `scope-paths` (`SCOPE_CHECK`, §5).
3. **Full:** `py-tests` (whole suite; the Session 36/39 baseline rule for the two environmental packaging tests, `walkthrough.md` §Baseline: a packaging test is excused only if it appears as `FAILED <id>` in the row 0 receipt `s35-base-py.txt`, and a missing receipt excuses nothing; the gate prints the excused ids), `ui-tests`, `mcp-build`, `mcp-tests` (the build first, because the tests load `mcp-server/dist`), `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`.
4. **Runtime:** `ui-electron` (the full Electron suite, because `SegmentedControl` is shared with Convert, Downloader and Settings; it is regression evidence for those pages, not proof of byte-identity, which AC-79.5 pins on the default markup), then `e2e-repeat`: `test:e2e -- tests/e2e/tts-generate.test.ts --grep "AC-79|AC-64.6" --repeat-each=10`. Any flake is a defect (S6).
5. `identity-npm`, then `identity-after`. The gate fails when `tested_state` differs between `identity-before` and `identity-after`.

The row's command is `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-tts-voice-panel/session-gate.ps1`, with the receipt pattern (task row 6).

The D6 `mcp-audit` runtime check is not a gate step: this plan adds no MCP action and changes no MCP schema; `mcp-build` and `mcp-tests` prove the server still builds and passes against the changed API.

### 5. `SCOPE_CHECK` (row 6)

- **`scope-paths`:** every path in `git diff --no-renames --name-only -z <baseline>` plus `git ls-files --others --exclude-standard -z` is a Files Modified row (product, test, hub and state files), or one of this project's artifacts (this plan folder, the handoffs, the reflection). With `--no-renames`, a rename shows its source deletion as well as its destination, so a move out of a disallowed path is caught; `-z` keeps paths with spaces or non-ASCII names whole (round 1 F2, R-5). The allow-list in the script is the union of the Files Modified tables; changing either one means changing both.

### 6. OpenAPI drift (G8)

`packages/api/` changes, so `openapi.committed.json` is regenerated (`uv run python tools/export_openapi.py -o openapi.committed.json`) in row 3, and the `openapi` D6 check (`--check`) must pass in the gate. H1-4 proves the committed diff adds and removes no schema and changes only `ModelVariantOut` (any other schema change is S5).

### 7. Closeout (H1, H2)

These are the template commands with this project's paths. `validate_closeout_artifacts.py` is run per handoff (two runs: `--handoff` + `--plan`, then `--ac-coverage-only`), plus `durable_evidence.py --require-full`, the review-state parsers, the reflection validator with `--decision-source` for the plan, the two handoffs, the grouping file and `.agent/context/known-issues.yaml`, with `--decision-issue` for each of the two issue ids, and `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped (`docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent; recorded `gui-refs-not-shipped`). No element is added; changed elements:

| Element | Kind | Change | Standard | E2E |
|---|---|---|---|---|
| `device-select` | select (changed) | options from the row (`DEVICE_SELECT_VALUE`); grid column 7rem | E2 (`emerging-standards.md:1167`) | AC-79.7, AC-79.10 |
| `model-select` | select (changed) | grid column `minmax(0,1fr)`; `className` dropped | E2 | AC-79.7 |
| `model-row` | container (changed) | `VOICE_GRID` grid | E2 | AC-79.7, AC-79.9 |
| model action button (`model-get-btn` / `model-load-btn` / `unload-btn`) | button (changed) | `size="md"` | E2 | AC-79.7 |
| `speed-slider` | range input (changed) | `h-9 w-full`; grid row | E2 | AC-79.8, AC-79.9 |
| Speed preset group (`speed-preset-*` radios) | segmented radios (changed) | `SEGMENT_SIZE` `md` | E2 | AC-79.8 |
| `format-select` | select (changed) | own row, `w-28` wrapper | E2 | AC-79.8, AC-64.6 |
| `voice-combobox` | combobox (unchanged) | height asserted only | — | AC-79.8 |

G36 (no silent test guards): the geometry tests assert; they never `skip`. G37: behaviour tests use `userEvent`. G30: the selects keep `getG30Styles()`. No G31–G35 surface changes.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a graph directory, or a `PREREQS` status or symbol is not as stated | Stop. Ask Mat, or re-run the context-tool gate. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` (including an MCP test pinning a 500 for a load failure) | Stop for the human with a Decision Brief naming the test and the smallest amendment. No test edit. |
| S3 | `red-check.py` refuses a Red receipt (`RED_PROOF`, §2) | Fix the test setup only, then re-prove Red. |
| S4 | `VOICE_GEOMETRY` (c) fails with the planned grid: a row overflows or the slider is under 96 px | Stop for a Decision Brief with the measured widths. Option B: the presets drop under the slider. The bound is a layout contract, not a tuning knob. |
| S5 | `SCOPE_CHECK` finds a path outside `PRODUCT_SCOPE`, or the OpenAPI diff changes more than `ModelVariantOut` | Revert that change or stop with a Decision Brief. |
| S6 | An Electron flake in `--repeat-each` | Fix the test's waiting, never add retries; if the product is racy, stop with a brief. |
| S7 | Review cap (plan 3, execution 6) or the reviewer is unavailable | HARD STOP with a TL;DR (create-plan §5d). Mat is the fallback reviewer. |

## Decision Log

Research engine for this plan: `native` (Claude Code reading of the installed runtimes and their documentation, 2026-10-16). Grouping §8 D-1, D-3, D-4, D-5 and D-6 carry forward unchanged into the reflection (stage `grouping`); D-1's condition (Session 30 approved) is now met, so row 1 writes the gated 11 section; D-2 and D-7 do not touch this scope. This plan's ids start at D-8. "Triage D-66/D-68" are the 2026-10-09 triage decisions the spec and the known issues cite.

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "Where is the plan written and executed?"
    resolution: autonomous
    class: two-way
    chosen: "Worktree P:/av-kit-wt/s35-tts-voice-panel on branch claude/s35-tts-voice-panel, cut from main 4a97483 (Sessions 32, 33 and 38 merged)"
    source_tag: Local Canon
    precedents: ["Session 36 and 39 D-8 (worktree per session)"]
    research: { engine: none, sources: [] }
    reasoning: "A worktree isolates this session from the other open session branches. D6 argv are unchanged; only the cwd differs. Cutting after the Session 33 merge satisfies grouping D-5 (MEU-77 edits the same TTSPage.tsx first)."
  - id: D-9
    stage: planning
    question: "How does the runtime report which devices exist?"
    resolution: autonomous
    class: two-way
    chosen: "DEVICE_PROBE: runtime_devices(format) in the adapter; torch flags for PyTorch, onnxruntime.get_available_providers() for ONNX; injectable as device_probe"
    source_tag: Research-backed
    precedents: ["03:466 'the available devices come from the runtime'", "07 §GPU (detect CUDA/MPS at runtime)", "R-1 installed torch 2.13.0+cpu, onnxruntime providers ['AzureExecutionProvider', 'CPUExecutionProvider']"]
    research: { engine: native, sources: ["https://onnxruntime.ai/docs/api/python/api_summary.html", "https://pytorch.org/docs/stable/generated/torch.cuda.is_available.html", "https://pytorch.org/docs/stable/notes/mps.html"] }
    reasoning: "Each runtime's own query is the only reliable answer: a CPU torch reports cuda False, and an onnxruntime without the GPU package lists no CUDA provider. The two formats differ (a CUDA torch does not give ONNX CUDA), so the list is per format. ONNX never lists MPS because this build has no CoreML provider. An injected probe keeps tests independent of the host GPU."
  - id: D-10
    stage: planning
    question: "What happens when the requested device cannot be used?"
    resolution: autonomous
    class: two-way
    chosen: "DEVICE_RESOLVE (unavailable → CPU, logged) and LOAD_FALLBACK (accelerator load failure → one CPU retry, logged; ONNX reports the provider it really got); ModelLoadError with the cause on final failure"
    source_tag: Spec
    precedents: ["03:465 fallback rule (triage D-66)", "adapter.py:198-202 ONNX CPU retry today (keeps _device_name 'cuda': the status bug)", "03:467 ModelLoadError with the cause"]
    research: { engine: native, sources: ["https://onnxruntime.ai/docs/api/python/api_summary.html#onnxruntime.InferenceSession.get_providers"] }
    reasoning: "The spec asks for CPU fallback with a log line and an honest status. Checking the probe first avoids a guaranteed failure (KModel.to('cuda') on a CPU torch raises AssertionError); retrying after a real failure covers a GPU that is detected but unusable. onnxruntime can silently drop CUDA when the provider fails to initialise, so get_providers() decides what the status says. KModel construction is not retried because it does not depend on the device."
  - id: D-11
    stage: planning
    question: "Which HTTP status does a failed model load return?"
    resolution: autonomous
    class: one-way
    chosen: "LOAD_ERROR_HTTP: ModelLoadError → 422 with code and message"
    source_tag: Local Canon
    precedents: ["MEU-76 (Session 33) maps ExtractError to 422 in DOMAIN_HTTP_MAP", "errors.py:130-150 domain handler shows the message for status < 500", "AC-76.4 uses a base DomainError, so this mapping leaves it unchanged"]
    research: { engine: none, sources: [] }
    reasoning: "The load request is well formed but cannot be processed with these weights or runtime, which is what 422 means in this API. A 500 masks the reason, and the user saw no reason in the original report. One-way: it is a published API contract (User Review Required item 1)."
  - id: D-12
    stage: planning
    question: "How does the page learn which devices a model row can use?"
    resolution: autonomous
    class: two-way
    chosen: "DEVICE_FIELD: a required devices field on ModelVariantOut, filled from TTSPort.available_devices(format)"
    source_tag: Spec
    precedents: ["03:466 'the TTS page lists only those'", "the page already reads /models/available for the picker (useTtsJob.ts:95)"]
    research: { engine: none, sources: [] }
    reasoning: "The list depends on the row's format, so it belongs on the row; a separate endpoint would add a fetch and a loading state for the same data. Required, so a client never has to guess."
  - id: D-13
    stage: planning
    question: "What does the Device select show when the stored device is not in the row's list?"
    resolution: autonomous
    class: two-way
    chosen: "DEVICE_SELECT_VALUE: show and send auto; keep the stored setting"
    source_tag: Research-backed
    precedents: ["MEU-56 settings leaves persist only on a user change (touched set)", "a model switch must not rewrite settings silently"]
    research: { engine: none, sources: [] }
    reasoning: "Auto is the safe value every row offers and resolves to the best device available. Keeping the stored value means a user who chose cuda sees it again on a row that supports it. Writing auto back would turn a model switch into a hidden settings change."
  - id: D-14
    stage: planning
    question: "How are the Voice panel controls laid out?"
    resolution: autonomous
    class: two-way
    chosen: "VOICE_GRID: model row grid [1fr | 7rem | auto]; speed row grid [1fr | auto] with md presets; Format on its own row at 7rem; everything 36 px"
    source_tag: Spec
    precedents: ["Triage D-68 'one aligned grid row for Model (flexes), Device (fixed) and the model action, sharing one control height'", "SelectInput h-9 and Button md h-9 are the existing control height"]
    research: { engine: none, sources: [] }
    reasoning: "The grid keeps the three model controls on one line at any width (Model shrinks, it never wraps) and aligns their labels and bottoms. Width estimate for the alternative (Format in the speed row): the Voice content box is about 369 px at the default window, the preset group about 165 px (three radio labels with px-2, a 13 px radio and the label text, plus padding), and Format 112 px, leaving the slider about 76 px, under the 96 px floor. Format at Device's width keeps a visible column rhythm. AC-79.9 measures the real widths; a failure is S4."
  - id: D-15
    stage: planning
    question: "How do the Speed presets reach the 36 px control height without changing other pages?"
    resolution: autonomous
    class: two-way
    chosen: "SEGMENT_SIZE: an opt-in size='md' prop; the default markup stays byte-identical"
    source_tag: Local Canon
    precedents: ["SegmentedControl is used by Convert (4x), Downloader, Settings and TTS", "Button sizes sm/md/lg (Button.tsx:23-27)"]
    research: { engine: none, sources: [] }
    reasoning: "Changing the default would move every other page's segmented controls and their Electron baselines. An opt-in size follows the Button convention. AC-79.5 pins the default markup to the baseline literal; the full Electron suite in the gate is regression evidence for the other pages, not byte-identity proof (round 1 Q5)."
  - id: D-16
    stage: planning
    question: "How is the alignment proven?"
    resolution: autonomous
    class: two-way
    chosen: "VOICE_GEOMETRY: Electron bounding boxes at the default window, ±0.5 px, plus no overflow and a 96 px slider floor"
    source_tag: Local Canon
    precedents: ["AC-64.6 default-window geometry test (tts-generate.test.ts:596-631)", "triage D-68 'an Electron geometry assertion at DEFAULT_WINDOW pins it'"]
    research: { engine: none, sources: [] }
    reasoning: "jsdom has no layout, so heights and bottoms can only be measured in Chromium. ±0.5 px absorbs sub-pixel rounding and nothing else."
  - id: D-17
    stage: planning
    question: "How do the Electron tests get device lists?"
    resolution: autonomous
    class: two-way
    chosen: "E2E_DEVICE_SEAM: the existing tts-generate seam's catalog rows gain devices"
    source_tag: Local Canon
    precedents: ["the seam already serves /models/available from __e2eCatalog (tts-generate.test.ts:65-100, :198)"]
    research: { engine: none, sources: [] }
    reasoning: "The seam is the page's only backend in Electron; adding the field there is the smallest change, and a PyTorch row with cuda proves the list follows the selected row."
  - id: D-18
    stage: planning
    question: "When is the 11 §TTS voice panel alignment section written?"
    resolution: autonomous
    class: two-way
    chosen: "Task row 1, before any test, from triage D-68 and this plan's VOICE_GRID/VOICE_GEOMETRY"
    source_tag: Local Canon
    precedents: ["grouping D-1 (gated docs after Session 30 approval; now met)", "meu-status MEU-79 'Spec section authored after Session 30 approval'"]
    research: { engine: none, sources: [] }
    reasoning: "MEU-79's ACs need a spec anchor; writing it first keeps the spec ahead of the tests. The matrix row and the 03 Delivered note wait for row 7, when the work exists."
```

## Research References

- ONNX Runtime Python API (`get_available_providers`, `InferenceSession.get_providers`): https://onnxruntime.ai/docs/api/python/api_summary.html
- PyTorch `torch.cuda.is_available`: https://pytorch.org/docs/stable/generated/torch.cuda.is_available.html
- PyTorch MPS backend (`torch.backends.mps.is_available`): https://pytorch.org/docs/stable/notes/mps.html

The plan relies on three runtime facts: `torch.cuda.is_available()` is False on a CPU build, `get_available_providers()` lists `CUDAExecutionProvider` only when the GPU package is installed, and `session.get_providers()` lists the providers the session really uses. R-1 checks the first two on Mat's host.

## Planning receipts

- **R-1 (2026-10-16).** Runtime probe in the main venv (`P:/av-kit/.venv`; the fresh worktree venv has no torch until row 0's `uv sync`): torch `2.13.0+cpu`, `torch.cuda.is_available()` False, `torch.backends.mps.is_available()` False; onnxruntime `1.29.0`, `get_available_providers()` = `['AzureExecutionProvider', 'CPUExecutionProvider']`. So on this host the real probe gives `(Auto, CPU)` for both formats, and today's code would still try `cuda` when asked.
- **R-2 (2026-10-16, re-run after round 1).** `identity.py --selftest`, exit 0, 0 failures (`C:/Temp/av-kit/s35-r1c-identity-selftest.txt`): each of the 16 bound paths (lockfiles, OpenAPI, configs, the scripts, and the documents the suites read: `11-page-layout.md`, `BUILD_PLAN.md`, `meu-status.yaml`, `meu-registry.md`, the P11 grouping, `review-vocabulary.yaml`, a peer handoff), an untracked test file and three runtime keys (`node`, `python_torch`, `python_distributions_sha256`) change `tested_state` and make `durable_evidence.evidence_problems` refuse the earlier full record; edits to the 9 closeout artifacts leave it unchanged.
- **R-3 (2026-10-16, re-run after round 1).** `red-check.py --selftest`, exit 0, 35 fixtures, 0 wrong (`C:/Temp/av-kit/s35-r1c-red-check-selftest.txt`).
  - **Pass (11):** a pytest assertion; `Failed: DID NOT RAISE`; a missing `runtime_devices` import inside the test; an unexpected `device_probe` keyword; a missing `available_devices` port method; a monkeypatch of `get_available_providers` on the adapter module; a run where every block is attributed; a Vitest assertion; grouped Vitest `FAIL` headers; an ANSI-coloured Vitest assertion; a Playwright run where AC-79.7, .8 and .10 each fail by `expect` under `--require`.
  - **Refused (24):** an Electron launch failure; a locator timeout; an ANSI-coloured locator timeout; an unrelated `ImportError`; an unrelated keyword; a name that only starts with a declared one (`runtime_devices_typo`); a declared name elsewhere on the line; an undeclared missing attribute; a bare `KeyError`; a missing field read as an attribute; a pytest collection interrupt; a valid assertion beside an unrelated error (pytest and Vitest); a chained unrelated error in the same block; a failure the receipt does not show (count mismatch); the round 1 scenario (TypeErrors in AC-79.7/.8 plus an AC-79.10 `expect`); a required test that passed; a required prefix only (`AC-79.70`); a required test failing by a declared name; a Playwright retry with an unrelated error; Vitest unhandled errors; no summary; a passing run; a receipt with no `.exit` file.
- **R-4 (2026-10-16, re-checked after round 1).** `session-gate.ps1` parses with 0 PowerShell parse errors; not run during planning (it needs the execution baseline).
- **R-5 (2026-10-16).** `scope-paths` probe in a scratch repository with the gate's own Python (`C:/Temp/av-kit/s35-r1c-scope-probe.txt`), 4 of 4 correct, exit 0: a clean tree → 0 outside; a committed rename from a disallowed path into an allowed one → 1, naming the source; a new allowed file → 0; an untracked disallowed path containing a space → 1.
- **R-6 (2026-10-16).** `red-check.py` over real receipts (`C:/Temp/av-kit/s35-r1c-red-check-real.txt`): Session 37's Vitest Red (10 failures) and Playwright Red → exit 0; a real pytest collection-error receipt → exit 1; a real pytest receipt with `'NoneType' object has no attribute 'devices'` → exit 1; `--require AC-87.6` → exit 0 and `--require AC-87.7` (a test with no failure block in that receipt) → exit 1.

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths` (§4).
- **Targeted:** §3 after each production edit (blocking for its row).
- **Fresh full:** §4 in one pass after the last input edit, from `WT`, `pwsh`. Row 6 runs it after the product edits; row 7 then changes bound inputs (hub docs, `meu-status.yaml`), so H1-2's run is the fresh full record the handoffs carry. It must pass; no partial, cached or reused receipt counts. Re-run all of §4 if any input changes after it (H1-6b).
- **Runtime (optional, non-blocking):** Mat's visual check (User Review Required item 6).
- **Input identity (`INPUT_IDENTITY`):** [identity.py](identity.py) prints the runtime identity and `tested_state` = HEAD + one SHA-256. The hash covers:
  - the tracked diff and the untracked (not ignored) files of the whole work tree, except only this session's own closeout outputs, which no suite or gate step reads: this plan folder's `*.md`, this session's handoffs and reflection, `docs/execution/metrics.md`, `.agent/context/current-focus.md` and `known-issues.yaml`/`.md`. So the lockfiles (`uv.lock`, `ui/package-lock.json`, `mcp-server/package-lock.json`), `openapi.committed.json`, configs and this plan's scripts are bound, and so are the documents the suites read (round 1 F3): `docs/build-plan/` and `docs/BUILD_PLAN.md` (`layout-canon`, `queue-canon`, `capture-page`, `convert-page`, `gui-actions-audit`), `meu-status.yaml` and the grouping files (`layout-canon`, `queue-canon`), `review-vocabulary.yaml` and other sessions' handoffs (`test_framework_adoption`), and `meu-registry.md` (`state-render`). Row 7 therefore runs before H1-2 and makes the status write there; the post-approval status write in H2-2 re-runs `layout-canon` and `queue-canon`;
  - the runtime identity, observed live: the Python running it and the SHA-256 of its installed distribution set (every `name==version`), with the `torch`, `onnxruntime` and `kokoro` versions named, `node --version`, the installed `electron` and `@playwright/test` versions, the `segoeui.ttf` hash and `ELECTRON_RUN_AS_NODE`.

  `--state-only` computes the same value. The gate records the state before and after it runs (§4), and each handoff's final full `evidence.v1` record carries it. H1-6b re-derives it live with `identity.py --state-only`, so any bound change refuses the old record and forces H1-2 again.
- **Evidence:** each receipt's exit code and decisive lines, pasted as `evidence.v1` in the handoffs.

## Execution Correction Notes

Recorded during execution so that no plan-level contract changes silently. Each item is visible to the execution review.

| Item | Change | Evidence |
|---|---|---|
| Gate amendment A-1 (D-19, `ui-tests` baseline rule) | `session-gate.ps1` `ui-tests` applies §Verification Plan 1's baseline rule the way `py-tests` already did: a Vitest exit 1 is accepted only when every failing id is queue-canon AC-41.3, that id also failed in row 0's base receipt, the summary count matches and nothing is unhandled. Cause: Zorivest 1f254832 changed the hexes AC-41.3 reads live (`QUEUE-PILL-TOKEN-DRIFT`). No AC or product contract changes. | `walkthrough.md` §Gate; both handoffs' Decision Log D-19 |
| Execution review R1 F1 (`DEVICE_PROBE`, `LOAD_ERROR_HTTP`, AC-75.9) | The independent execution review (round 1, High) found that a runtime availability query that raises (ONNX provider enumeration, `torch.cuda.is_available`, `torch.backends.mps.is_available`) escaped `runtime_devices`, so `/models/available` and a CPU load answered HTTP 500 with a bare `RuntimeError`. `DEVICE_PROBE` now treats a raising query as that device absent and logs one `tts.device_probe_failed` warning (`format`, `device`, `error` type name); Auto and CPU stay listed, and an explicit request for the absent device falls back through `DEVICE_RESOLVE` with reason `unavailable`. `load_model` also wraps the three other statements that could escape bare in `ModelLoadError` with the cause: a raising injected probe, a raising vocab resolver and an unreadable weight file (`stat` raising `PermissionError`). `CPU_FALLBACK`, the route map and the response shapes are unchanged. Five appended tests in `tests/integration/test_tts_device_resolution.py` (Red first: 4 failed on the reviewed tree, then 1 for the weight-file `stat`). | `.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md` F1; `C:/Temp/av-kit/s35-f1-red-py.txt`, `s35-f1-red2-py.txt`, `s35-f1-green-py.txt` (60 passed); H1-2 gate re-run; MEU-75 handoff D-21; `walkthrough.md` §Execution review R1 |
| Gate amendment A-3 (`scope-paths` allowlist; Mat's ruling 2026-10-17) | Post-correction gate attempt 2 failed at `ui-tests` on `capture-picker.test.ts` AC-40.6: the test names the taken file from the real clock, and the publication fell in the next second, so no `_2` was needed. `capture-lifecycle.test.ts` AC-40.30 (a) (walks to `_3`) has the same race. Both tests now pin `Date` (`vi.useFakeTimers` with only `Date` faked, `vi.setSystemTime`) for that one test, and the picker file's `afterEach` restores real timers. No assertion, product code or AC changes. The two files join the `scope-paths` allowlist. | `C:/Temp/av-kit/s35-gate-h1-r2fail2/` (the failing attempt); `s35-gate-flake-ac406.txt` (5/5 alone); `s35-a3-red-ui.txt` (2 failed with a one-second clock step); `s35-a3-green-ui.txt` (55 passed x3); `walkthrough.md` §A-3 |
| Execution review R2 F2 (`LOAD_ERROR_HTTP`, AC-75.9) | The independent execution review (round 2, High) found that the lazy `kokoro` import in `_load_pytorch` caught only `ImportError`, so an engine that is installed but fails to initialize (an `OSError` from a native DLL, simulated) escaped `load_model` bare, and the load route answered a masked HTTP 500. `_load_pytorch` now maps any other exception from that import to `ModelLoadError("PyTorch model failed to load")` with the cause, after one `tts.load_failed` log; `ImportError` keeps its not-bundled message. The R1 sweep had missed this statement; this is now the only load-time import in the adapter. One appended test, `test_ac_75_9_engine_import_failure_is_model_load_error_neg` (Red first: 1 failed). | `.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md` F2; `C:/Temp/av-kit/s35-f2-red-py.txt`, `s35-f2-green-py.txt` (61 passed); H1-2 gate re-run; MEU-75 handoff D-23; `walkthrough.md` §Execution review R2 |
| Gate re-run A-4 (no file change) | The first gate run after the F2 correction failed only at `ui-electron`, on `capture-inbox.test.ts` AC-66.14 (a middle-button pan read `ox` 92 px from the expected value). It belongs to an earlier capture session, no Session 35 change reaches it, and it passed 5/5 alone. It is logged as the known issue `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`, and the whole gate was re-run unchanged, as in A-2. A second miss stops for Mat. The re-run passed: `session-gate: all steps exit 0`, Electron 161 passed. | `C:/Temp/av-kit/s35-gate-h1-r3fail/`; `s35-gate-flake-ac6614.txt` (5 passed); `s35-gate-h1/` (the passing re-run); `walkthrough.md` §A-4 |
