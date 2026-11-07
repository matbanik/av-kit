---
project: "2026-11-06-tts-build-capability"
date: "2026-11-06"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-51--tts-build-capability-meu-117-meu-118--p2"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-117", "MEU-118"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: A build offers only the models and devices it can run (Session 51)

> **Project:** `2026-11-06-tts-build-capability`
> **Build plan:** `docs/build-plan/03-service-layer.md` §TTS build capability (residual) (`:584-602`, MEU-117) and `docs/build-plan/06-gui.md` §TTS device options (residual) (`:1541-1551`, MEU-118). The scope is grouping §3 Session 51 (`.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:163`).
>
> **Source requests,** Mat, 2026-11-06. The Session 51 brief scopes MEU-117 then MEU-118 with no split. Tests inject the runtime as present and absent, with no real 327 MB download. Done means "an installed build cannot start the download of a model it cannot load, and the dev venv still loads and generates with it". The brief asks the plan to say where the packaged smoke runs: here (D-315), and MEU-125 repeats it at the rc.2 gate.
> **Known issues:** `TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME` (P2; triage D-217) and `TTS-DEVICE-OPTIONS-IN-CPU-BUILD` (P4; D-226). D-237 (espeak is never downloaded or bundled) sits under the closed `TTS-PYTORCH-RUNTIME-SETTINGS-DOWNLOAD` and still binds.
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
>
> Line anchors are from `main` `71d0d3a`, and the tree was clean at plan time. Only one worktree is open (`git worktree list`: `P:/av-kit 71d0d3a [main]`).

## Goal

**Goal anchor:** Session 51 makes the backend say, for each model variant, whether this build can run it, from whether the variant's runtime imports in this process. A variant it can't run is listed disabled with a reason that names a next step. Its download is refused with a 409 before any job or file exists, and its load keeps its 422 with the same reason. The TTS page can't select it, and the Settings device select offers only the devices that a runnable variant reports. The dev venv, which has torch and kokoro, keeps loading and generating with the PyTorch variant.

Four things are wrong today:

1. **Nothing says a variant can't run.** `GET /models/available` (`routes/models.py:56-64`) lists the PyTorch row like any other, and `ModelVariantOut` (`schemas/models.py:37-48`) has no field for it. The installed backend has no torch (`tts/adapter.py:25-29`), so `_load_pytorch` always raises "PyTorch runtime is not bundled" (`:299-302`).
2. **The download is accepted.** `ModelService.download` (`services/models.py:201-212`) checks only for a download in flight and an unknown id. It then starts the thread that fetches 327 MB for a model this build can't load.
3. **The TTS page can pick it.** `defaultModelSelection` (`tts-controls.ts:104-120`) takes the first downloaded row, else the first row. The PyTorch row is seeded first (`database/engine.py:24`), and the model select (`TTSPage.tsx:461-477`) has no disabled option.
4. **Settings offers four devices on every build.** `TTS_DEVICES` (`SettingsPage.tsx:62`) is fixed, so a CPU-only build offers `cuda` and `mps`.

The session ends when two checks pass. The packaged capability smoke (`CAPABILITY_SMOKE`, AC-117.15) runs on a fresh onedir: the PyTorch row reads unavailable with the reason, its download answers 409, and the models folder is unchanged. The dev check (`DEV_CHECK`, AC-117.16) loads the PyTorch variant from the repo's `.venv` and generates a WAV.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-06). A headroom binary is on PATH but no payload here is oversized: the scope is a named list of adapter, service, route, MCP, renderer and test files, read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s51-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s51\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s51-plan-2026-11-06-tts-build-capability` and `s51-execution-2026-11-06-tts-build-capability`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290).
- **Never in these rows without Mat's words:** commit, push, a real model or runtime download, a YouTube request of any kind, or an `approved` verdict authored by the implementer.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-117 `svc-tts-build-capability` | `.agent/context/handoffs/2026-11-06-tts-build-capability-MEU-117-handoff.md` |
| MEU-118 `gui-tts-device-options` | `.agent/context/handoffs/2026-11-06-tts-build-capability-MEU-118-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-06-tts-build-capability-plan-critical-review.md` and `.agent/context/handoffs/2026-11-06-tts-build-capability-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `models-before.json`, base suite receipts, the dev check's baseline receipt |
| WP-2 | MEU-117 domain, port and adapter (rows 1, 2) | WP-1 | shared | `ModelAvailability`, `MODEL_REASONS`, `RUNTIME_PROBE`, `runtime_present` |
| WP-3 | MEU-117 service, API and MCP (rows 3, 4) | WP-2 | shared | `MODEL_REFUSAL`, `MODEL_FIELDS`, OpenAPI, MCP descriptions; 03, 04 and 05 spec text |
| WP-4 | MEU-117 renderer (rows 5 to 7) | WP-3 | shared | Disabled option, model selection; 06 `:878`; E2E receipt |
| WP-5 | MEU-117 packaged and dev checks (rows 8, 9) | WP-4 | shared | `--phase capability`, a fresh onedir, the smoke and dev check receipts |
| WP-6 | MEU-118 (rows 10 to 12) | WP-5 | shared | `tts-devices.ts`, the Settings select; 06 `:882`, `:1067`; E2E receipt |
| WP-7 | Records (row 13) | WP-6 | shared | Hub, MEU status, register, renders, grouping tracker |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | Handoffs, review, reflection |

The grouping marks no split for Session 51 (`:170`), and the brief says "No split flag".

## User Review Required

> [!IMPORTANT]
> **Read the reason texts in §Reasons.** The PyTorch one is what an installed build shows beside the disabled row, and what the 409 and the 422 say: "This build can't run PyTorch models. Choose an ONNX model." The model select reads "PyTorch FP32 — This build can't run PyTorch models. Choose an ONNX model."
>
> **Four existing tests change their expectations (row 1).** Each follows the residual section ("its message carries the same reason"), not convenience:
> - `test_ac_4_7_port_method_sets_and_signatures` (`tests/unit/test_domain.py:1325`) lists the `TTSPort` methods. `TTS_PORT_METHODS` (`:1154-1161`) gains `runtime_present`.
> - `test_ac_98_5_torch_absent_logs` (`tests/integration/test_tts_device_resolution.py:828`) and `test_ac_98_5_kokoro_import_logs` (`:844`) expect the adapter's `ModelLoadError` to read `MODEL_REASONS[PyTorch]` instead of "PyTorch runtime is not bundled". The log line, the cause and the device are unchanged.
> - `test_ac_115_9_load_failed_carries_detail` (`:890`) expects that text as the `detail=` of its last block.
>
> **One choice with a do-nothing option (D-312).** The plan takes A, which can change at the gate.
> - **A (chosen):** the adapter raises `MODEL_REASONS[PyTorch]` where it says "PyTorch runtime is not bundled" today (`tts/adapter.py:300`, `:308`). Every path that refuses the variant then says the same words, the log's `detail=` included. Three tests change, as above.
> - **B, do nothing in the adapter:** the service refuses first, so through the API the adapter's text is no longer reached, but it stays in the code and in `tts.load_failed` for a direct caller. The three adapter tests stay as they are.
>
> **Settings now reads `/models/available` (D-314).** It shares the TTS page's cached query. In dev, the first catalog read in a backend process now waits for the kokoro import, about 3 s, where the first load waited before (`C:/Temp/av-kit/s51-probe-import-timing.txt`: torch 0.88 s, kokoro `KModel` 3.15 s). A packaged build has no torch, so it never imports kokoro and doesn't wait. Until the report arrives, or if it fails, the select offers `auto` and `cpu` plus the stored value.
>
> **The packaged smoke runs in this session (D-315), and MEU-125 repeats it at the rc.2 gate on the installer's copy.** Row 8 adds `--phase capability` to `tools/smoke_packaged_tts.py`. It runs the phase first on a copy of the pre-session onedir (`packaging/dist/avkit-backend`, 2026-11-04) as its Red. It then builds a fresh onedir with `tools/package_backend.py`, which overwrites that ignored folder, and runs the phase on a copy outside the checkout. The run is offline, and it makes no download.
>
> **`07-distribution.md:30` and `:227` already carry D-217's wording (D-319).** Commit `83229ea` (2026-11-05, `docs(triage)`) changed both lines. Row 4 re-checks them and edits nothing. `:226` ("Known gap (Session 27)") is stale since MEU-72 was delivered, and it stays out of scope unless Mat adds it.
>
> **A disabled option may not look greyed (D-320).** Each `<option>` keeps its G30 pair (`SelectInput.tsx:16-19`), and the dark-theme Chromium list doesn't grey a disabled option drawn in an explicit colour. The row can't be chosen, and its label carries the reason. A muted colour would be a new G30 palette pair, a question for Mat.
>
> **The token estimate,** calibrated against Session 35 `tts-voice-panel`, as the grouping asks, and Session 50. Session 35 took 3 plan rounds and 4 execution rounds, with 20M tokens added to each budget. Session 50 took 14.8M over 2 plan rounds (7,335,229 and 7,464,583) and 15.4M over 2 execution rounds (11,979,136 and 3,371,933). This delta is two MEUs across domain, adapter, service, route, MCP text, renderer and Settings, plus a packaged build. Expect 1 to 3 plan rounds and 2 to 4 execution rounds, about 25M to 50M Codex tokens in all. The harness budgets are 10.5M for the plan review and 21M for the execution review. A plan round has run about 7M, so a second plan round needs Mat's grant.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `RUNTIME_PROBE` | `runtime_imports(fmt) -> bool` in `tts/adapter.py`, beside `runtime_devices`. ONNX returns `True`. PyTorch returns `False` when `torch` is `None`, with no kokoro import and no log. Otherwise it tries `from kokoro import KModel`: success returns `True`, and any `Exception` returns `False` and logs one `tts.runtime_probe_failed` WARNING with `format` and `error=` the exception's class name. |
| `RUNTIME_PRESENT` | `TTSPort.runtime_present(fmt) -> bool`. The adapter runs its `runtime_probe` (default `RUNTIME_PROBE`) at most once per format per process, under a lock, and returns the stored answer after that. |
| `MODEL_REASONS` | A map in `domain/tts.py` with one entry for each `ModelFormat` (§Reasons). |
| `AVAILABILITY` | `ModelAvailability(available: bool, reason: str \| None)`, a frozen dataclass in `domain/tts.py`. `reason` is a non-empty string exactly when `available` is `False`. `model_availability(fmt, runtime_present) -> ModelAvailability` builds it from `MODEL_REASONS`. |
| `MODEL_REFUSAL` | For a variant whose format isn't present, `ModelService.download` raises `ConflictError(reason)` (409) and `ModelService.load` raises `ModelLoadError(reason)` (422). Each check runs before any work and logs one WARNING (`model.download_refused`, `model.load_refused`) with `variant_id` and `detail=` the reason. |
| `MODEL_FIELDS` | `ModelVariantOut.available: bool` and `reason: str \| None`, set on every route that returns a variant. |
| `DEVICE_ORDER` | `['auto', 'cuda', 'cpu', 'mps']` in `ui/src/renderer/src/features/tts/tts-devices.ts`, the order `runtime_devices` uses (`tts/adapter.py:67`). |
| `DEVICE_FLOOR` | `['auto', 'cpu']` in `tts-devices.ts`, the devices every build offers (`DEVICE_PROBE`). |
| `DEVICE_OPTIONS` | `buildDevices(rows)` in `tts-devices.ts`: `DEVICE_FLOOR` plus the `devices` of each row whose `available` isn't `false`, kept to `DEVICE_ORDER` and listed in that order. |
| `CAPABILITY_SMOKE` | `tools/smoke_packaged_tts.py --phase capability`, AC-117.15. |
| `DEV_CHECK` | `dev-pytorch-check.py` in this plan folder, AC-117.16. |
| `MODELS_SNAPSHOT` | `models-snapshot.py` in this plan folder: the relative name, size and `mtime_ns` of every file under the real models folder (`~/.avkit/models`). It leaves out `*.lock` files and the interpreter caches (`__pycache__` folders and `*.pyc`), which an import of the folder's spaCy install can write. |

### Reasons (D-310)

`MODEL_REASONS` holds exactly these texts:

| Format | Text |
|---|---|
| `PyTorch` | "This build can't run PyTorch models. Choose an ONNX model." |
| `ONNX` | "This build can't run ONNX models. Reinstall av-kit." |

The ONNX entry makes the map complete, and nothing reaches it today: `onnxruntime` is imported when the adapter module loads (`tts/adapter.py:19-23`), so a build without it never starts. The texts are fixed av-kit strings and never hold exception text, so no raw value reaches a log, stdout or the Console through them.

### Capability source (MEU-117, D-309)

- **Probe.** `RUNTIME_PROBE`, as above. "Torch without kokoro counts as unavailable" is the import of `KModel` failing. The log carries the class name only. Exception text can hold a local path, and the rule carried from Session 50 is that a raw value that can reach a log is fixed in the row.
- **Adapter.** `KokoroAdapter.__init__` takes `runtime_probe: Callable[[ModelFormat], bool] | None = None`. A `None` binds the module's `runtime_imports` when the adapter is built, as `device_probe` binds `runtime_devices` (`:204`). `runtime_present(fmt)` answers from a per-format dict under a `threading.Lock`, so 8 threads asking at once probe once. A probe that raises (it shouldn't, as it catches `Exception`) propagates and stores nothing.
- **Port.** `TTSPort` (`ports/tts.py:41-43`) gains `runtime_present(fmt: ModelFormat) -> bool` after `available_devices`. Its docstring says it reports whether this process can import the format's runtime (`RUNTIME_PRESENT`). The adapter and the tests' fakes are the only implementers (`grep`, 2026-11-06): `FakeTTSPort` (`tests/unit/test_services.py:1599`) and `FakeModels` (`tests/e2e/api_fakes.py:345-384`), which `_CudaModels` and `AdapterModels` inherit.
- **Import hygiene (`IMPORT_HYGIENE`, AC-72.1).** The packaged backend has no torch, so the probe returns before any kokoro import. The import-blocked subprocess test (`tests/integration/test_tts_no_torch.py`) gains AC-117.5 to pin this. In dev, kokoro is imported at the first catalog read instead of the first load, and nothing else imports it.
- **Devices are unchanged.** `available_devices` and `DEVICE_FIELD` stay as they are, so an unavailable row still lists the devices `DEVICE_PROBE` reports. `available` decides whether the row can be used, and `DEVICE_OPTIONS` ignores the devices of an unavailable row.

### Service and API (MEU-117, D-311)

- **Availability.** `ModelService.availability(fmt) -> ModelAvailability` returns `model_availability(fmt, self._tts.runtime_present(fmt))`.
- **Download.** `download` (`services/models.py:201-212`) reads the row and warms the probe before it takes `self._lock`, because the first PyTorch probe in dev takes about 3 s. Inside the lock, it keeps today's order: the in-flight 409, re-reading the row, then `NotFoundError`. Then, for an unavailable variant, it logs `model.download_refused` and raises `ConflictError(reason)` before `_start_locked`. So the runtime stays `Idle`, no thread starts, and no file is written.
- **Load.** In `load` (`:135-157`), after `NotFoundError` and before the legacy and vocab checks, an unavailable variant logs `model.load_refused` and raises `ModelLoadError(reason)` (422). The port isn't called, and spaCy isn't started. The reason comes first because a vocab 409 would tell the user to fetch an asset for a model this build can't load anyway.
- **Unchanged.** `list_available` and `list_downloaded` return the same rows. A PyTorch file already on disk stays there and is listed `is_downloaded: true` with `available: false`. No delete route is added.
- **Schema.** `ModelVariantOut` (`schemas/models.py:37-48`) gains `available: bool` and `reason: str | None` after `devices`. Both are always present. The comment above them names `MODEL_FIELDS` and says `reason` is set exactly when `available` is false.
- **Route.** `_variant_out(variant, models)` (`routes/models.py:42-53`) sets `devices`, `available` and `reason` from the service. `list_available`, `list_downloaded` and the `download` response all use it.
- **409 text.** `CONFLICT_409` (`:26-32`) and the `download_model` docstring (`:78-96`) add "or the variant can't run in this build". `openapi.committed.json` is regenerated, and its diff must show only the two fields and the three description strings these two edits change as new (S6). `CONFLICT_409` is registered on both download and load (`:82`, `:99`), and the docstring is the download's own description (plan review round 1).
- **MCP (D-318).** `mcp-server/src/toolsets/models.ts` passes the JSON through, so the fields and the 409 reach MCP with no code change. Only the descriptions change. `available` and `download` move out of the `desc()` loop (`:17-23`) into explicit entries, as `download_asset` is (`:24-30`), and keep the four markers. `available`'s description names `devices`, `available` and `reason`. `download`'s says it answers 409 for a variant this build can't run, with the reason. This is an MCP source change, so `mcp-build` runs in the gate.

### Renderer (MEU-117, D-320)

- **Types.** `CatalogItem` (`useTtsJob.ts:49-59`) gains `available?: boolean` and `reason?: string | null`. A row without `available` counts as available, as a row without `devices` already counts as `auto` and `cpu`.
- **Option.** `SelectOption` (`components/ui/SelectInput.tsx:5-8`) gains `disabled?: boolean`, passed to each `<option>`. The option keeps `style={g30}`, so AC-94.2 to AC-94.4 still pass.
- **Model select.** In `TTSPage.tsx:461-477`, an unavailable row's option is disabled, and its label is `{name} — {reason}` in place of the state suffix.
- **Selection.** `defaultModelSelection` (`tts-controls.ts:104-120`) skips an unavailable row in each rule: the chosen row, the first downloaded and the first row. The loaded row is kept as it is, because a load of an unavailable variant is refused, so a loaded row was available when it loaded. With no available row, it returns `null`. Its `catalog` parameter type gains `available?: boolean`.
- **06.** `06-gui.md:878` says an unavailable variant is listed disabled with its reason.

### Device options (MEU-118, D-313, D-314, D-317)

- **Source.** New `ui/src/renderer/src/features/tts/tts-devices.ts` exports `DEVICE_ORDER`, `DEVICE_FLOOR` and `buildDevices`. The source is the catalog the backend already returns, read through `useModelsAvailable()` (`useTtsJob.ts:94-99`). No new route is added.
- **Settings.** `SettingsPage.tsx` removes `TTS_DEVICES` (`:62`). The device row (`:828-837`) takes its options from `buildDevices(useModelsAvailable().data?.items)`:
  - While the report is pending or has failed, the options are `DEVICE_FLOOR` plus the stored value when it is in `DEVICE_ORDER` and not already listed.
  - Once the report arrives, a stored value that isn't offered shows as `auto` and writes nothing, as the TTS page does (`DEVICE_SELECT_VALUE`, `11-page-layout.md:166`). The load then falls back through `DEVICE_RESOLVE` (03 §TTS device resolution).
  - Choosing an option writes `{ device }` once, as today.
- **TTS page.** `TTSPage.tsx:274` reads `selectedModel?.devices ?? DEVICE_FLOOR` in place of the literal. Its behaviour doesn't change.
- **06.** `:882` reads "Auto, then CUDA, CPU or MPS as the selected variant reports" and `:1067` says the Settings select offers what the backend reports for this build.
- **Wire enums.** `tts-commands.ts` `DEVICE_VALUES` and the MCP `DEVICE_WIRES` are input validation for what a client may send, not options shown to the user. They stay as they are.

### Packaged and dev checks (MEU-117, D-315, D-316)

**`CAPABILITY_SMOKE`** (`phase_capability(backend_dir, models_dir)` in `tools/smoke_packaged_tts.py`, `--phase capability --backend-dir … --models-dir … --out …`):

1. It refuses a `backend_dir` inside `REPO_ROOT`, as `phase_offline` does (`:351-410`). It also refuses a `models_dir` that exists and isn't empty, or that lies inside `REPO_ROOT` or the real `~/.avkit/models`.
2. It fails if `_forbidden_dirs` finds a `FORBIDDEN_DIRS` entry under `_internal`.
3. It writes a stub `kokoro-v1_0.pth` (16 bytes) and a `config.json` holding `{"vocab": {"a": 1}}` into `models_dir`, so the PyTorch row reads downloaded.
4. It starts the backend with `_offline_env` (dead proxies, a fresh home, `HF_HOME`) and fresh app data, then sets `tts.models_directory` with `put_tts_settings`.
5. Check `listed_fields`. `GET /models/available` lists the four seeded rows. `kokoro-pt-fp32` reads `available: false`, `reason` equal to `MODEL_REASONS[PyTorch]` and `is_downloaded: true`. Each ONNX row reads `available: true` and `reason: null`.
6. Check `download_refused`. It takes a snapshot of `models_dir`. `POST /models/download {"variant_id": "kokoro-pt-fp32"}` answers 409 with code `ConflictError` and the reason as its message. `GET /models/download-runtime` then reads `Idle`, and the snapshot is unchanged.
7. Check `load_refused`. `POST /models/load` on `cpu` answers 422 with code `ModelLoadError` and the reason. The stub is still there, and the row still reads `is_downloaded: true`.
8. Check `logged`. The backend's tail holds `model.download_refused` and `model.load_refused`.

The phase stops at the first failing check and records it as `failed_check`. Its result adds `checks`, a map from each check that ran to what it saw, beside the keys the other phases write (`errors`, `passed`, `backend_tail`). So on the old onedir it stops at `listed_fields`, before any download request, and `checks` has no `download_refused` key. `main` adds `capability` to `--phase` and requires `--backend-dir` for it, as for `offline`.

**`DEV_CHECK`** (`dev-pytorch-check.py`, plan-local):

- **Entry point.** The check defines `DevBackend`, a subclass of `Backend` (`tools/smoke_packaged_tts.py:61-93`) whose `__init__` starts `sys.executable -m avkit_api` with `--token`, `--mcp-token`, `--port 0` and `--app-data`, the argv that `npm run dev` spawns (`buildDevSpawnArgv`, `ui/src/main/python-manager.ts:17-36`). It keeps `Backend`'s ready wait, drain, client and stop. Row 0 runs the check before anything in `tools/` changes, so it can't depend on a change there, and `Backend` itself is unchanged.
- **Environment.** It uses temp app data, dead proxies, `HF_HUB_OFFLINE=1` and `PYTHONDONTWRITEBYTECODE=1`. The real `~/.avkit/models` is set as `tts.models_directory`, and the output path is a temp folder. Before it starts, it checks that spaCy reads `READY` there, so the load starts no download.
- **Checks.** `kokoro-pt-fp32` reads `available: true` with `reason: null`. `POST /models/download` answers 202 through the manager's fast path (`model_manager/manager.py:54-72`), which returns the file already on disk and writes nothing. The download runtime returns to `Idle`. `POST /models/load` on `cpu` answers 200, and a short generate makes a WAV of more than 8000 samples.
- **Modes.** Row 0 runs it with `--baseline`, where the two fields may be absent, to prove the dev path works before any change (S9). Row 9 and the gate run it strictly.

**`MODELS_SNAPSHOT`.** Row 0 runs `models-snapshot.py --record`, and rows 2, 4, 9 and 12 and the gate run `--compare`. Any change is S4. This takes the place of Session 50's real-log check: the real file at risk here is the models folder, and every test uses `tmp_path` or a fake catalog.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/03-service-layer.md` | `:588` | The anchor `tts/adapter.py:292-296` becomes `:298-308` |
| `docs/build-plan/03-service-layer.md` | after `:602` | Delivered note (row 13) |
| `docs/build-plan/04-rest-api.md` | `:275` | The download row adds "or the variant can't run in this build (the reason as message)" |
| `docs/build-plan/04-rest-api.md` | `:276` | The load row adds "422 with the reason for a variant this build can't run" |
| `docs/build-plan/04-rest-api.md` | `:283` | `ModelVariantOut` lists `devices`, `available` and `reason` |
| `docs/build-plan/05-mcp-server.md` | `:189`, `:191` | `available` names the two fields, and `download` the 409 |
| `docs/build-plan/06-gui.md` | `:878` | Available models: an unavailable variant is listed disabled with its reason |
| `docs/build-plan/06-gui.md` | `:882`, `:1067` | The device selector and `tts.device` say what is offered (row 11) |
| `docs/build-plan/06-gui.md` | after `:1551` | Delivered note (row 13) |
| `docs/build-plan/07-distribution.md` | `:30`, `:227` | No edit; row 4 checks that both already say it (D-319) |

### MEU-117 `svc-tts-build-capability`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `TTSPort.runtime_present` | `ports/tts.py` | `(fmt: ModelFormat) -> bool` | Port method; no other arguments |
| `ModelAvailability` | `domain/tts.py` | `available: bool`; `reason: str \| None`, non-empty exactly when `available` is false | Frozen dataclass; no other fields |
| `GET /models/available`, `GET /models/downloaded`, the `POST /models/download` 202 → `ModelVariantOut` | `packages/api/src/avkit_api/schemas/models.py` | `available: bool`; `reason: str \| None`; `devices` unchanged | Response model; unchanged policy |
| `POST /models/download` 409 for an unavailable variant | `errors.py` envelope | `code: ConflictError`, `message` = the reason | Unchanged envelope |
| `POST /models/load` 422 for an unavailable variant | `errors.py` envelope | `code: ModelLoadError`, `message` = the reason | Unchanged envelope |
| `tts.runtime_probe_failed`, `model.download_refused`, `model.load_refused` | `tts/adapter.py`, `services/models.py` | `format` and `error` (class name); `variant_id` and `detail` (the reason) | Kept by `CONSOLE_FIELDS` as they stand; nothing else is logged |
| MCP `avkit_models` `available`, `download` | `mcp-server/src/toolsets/models.ts` | The input schemas don't change | Description text only; JSON passes through |

#### Acceptance Criteria

Pytest names are `test_ac_117_<n>_…`. Vitest and Playwright titles begin `AC-117.<n>`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-117.1 | unit | `model_availability(PyTorch, False)` is `available` false with `MODEL_REASONS[PyTorch]`. `(fmt, True)` is `available` true with `reason` `None` for both formats. `MODEL_REASONS` has a key for every `ModelFormat` and holds the §Reasons texts exactly. `ModelAvailability(True, "x")`, `(False, None)` and `(False, "")` raise `ValidationError` (`tests/unit/test_domain.py`). AC-4.7 is amended to list `runtime_present`. | Human-approved (triage D-217: a reason that names a next step) | Today the names don't exist. The test asserts `hasattr(domain_tts, "model_availability")` first, and AC-4.7 fails on the method set |
| AC-117.2 | integration | `runtime_imports` (`tests/integration/test_tts_device_resolution.py`): ONNX gives `True`. With `torch` patched to `None`, PyTorch gives `False`, logs nothing and makes no kokoro import request (an import hook records them). With a kokoro import raising `ImportError("SYNTHETIC_IMPORT_MARKER")`, it gives `False` and one `tts.runtime_probe_failed` WARNING with `format` `PyTorch` and `error` `ImportError`, and the marker is in no field. An `OSError` gives `error` `OSError`. A fake `kokoro` module holding `KModel` gives `True` and no log. | Human-approved (triage D-217: "torch without kokoro counts as unavailable") | Today `runtime_imports` doesn't exist; the test asserts `hasattr` on the module first |
| AC-117.3 | integration | `runtime_present` calls the injected probe once per format across 8 threads released together by a barrier (with a timeout) and returns its answer. With no probe injected, it calls the module's `runtime_imports` (monkeypatched before the adapter is built). | Local Canon (D-309) | Today `runtime_present` doesn't exist; the test asserts `hasattr(KokoroAdapter, "runtime_present")` first |
| AC-117.4 | integration | The amended `test_ac_98_5_torch_absent_logs` and `test_ac_98_5_kokoro_import_logs` expect `MODEL_REASONS[PyTorch]` with the same log line and cause. The amended `test_ac_115_9_load_failed_carries_detail` expects it as `detail`. | Local Canon (03 §TTS build capability, "Load": the same reason) | Today the text is "PyTorch runtime is not bundled" |
| AC-117.5 | integration | In a subprocess with `torch`, `phonemizer` and `espeakng_loader` blocked and kokoro importable, `KokoroAdapter().runtime_present(PyTorch)` is `False` and `(ONNX)` is `True`. A `sys.meta_path` recorder sees no request for `kokoro` (`tests/integration/test_tts_no_torch.py`). | Local Canon (`IMPORT_HYGIENE`, AC-72.1) | Today `runtime_present` doesn't exist; the script prints a marker the test asserts on |
| AC-117.6 | unit | `ModelService.download` with `FakeTTSPort.runtime_present` false for PyTorch raises `ConflictError` whose text is the reason. The runtime stays `Idle`, `FakeCatalog.entered` is never set, and one `model.download_refused` WARNING carries `variant_id` and `detail`. With a download in flight, the in-flight 409 comes first, with today's text. An unknown id raises `NotFoundError`. With the format present, the download starts as today (`tests/unit/test_services.py`). | Human-approved (triage D-217: 409 before any download starts) | Today the download starts and `entered` is set |
| AC-117.7 | unit | `ModelService.load` of an unavailable variant raises `ModelLoadError` with the reason, before the legacy and vocab checks (the fixture's vocab is missing, and the error is still `ModelLoadError`). The port's `load_model` isn't called, the spaCy download isn't started, and one `model.load_refused` WARNING is logged. An unknown id still raises `NotFoundError`. | Local Canon (03, "Load"; 01 §Domain errors) | Today the vocab check raises `ConflictError`, or the port is called |
| AC-117.8 | e2e | New `tests/e2e/test_api_model_capability.py`. `make_client(models=…)` takes a real `ModelService` over `FakeUnitOfWork`, `FakeCatalog`, `FakeTTSPort` (PyTorch absent) and `FakeAssets` (vocab `READY`), with a tmp models folder holding a stub `kokoro-v1_0.pth`. `GET /models/available` lists four rows: PyTorch with `available: false`, the reason and `is_downloaded: true`, and each ONNX row with `available: true` and `reason: null`. `GET /models/downloaded` carries the same fields. `POST /models/download` for PyTorch gives 409, envelope code `ConflictError` with the reason. The download runtime reads `Idle`, the catalog wasn't entered, and the tmp folder's listing is unchanged. `POST /models/load` gives 422 `ModelLoadError` with the reason, and the stub is still listed. With PyTorch present, the download gives 202 with `available: true`, and the catalog is entered once. | Human-approved (triage D-217; the brief's contract test "with no job and no file written") | Today the fields are absent and the download gives 202 |
| AC-117.9 | e2e | In `openapi.committed.json`, `ModelVariantOut` has `available` (boolean) and `reason` (string or null), and the `/models/download` 409 description names the variant this build can't run (`tests/e2e/test_api_tts_models.py`). | Local Canon (04 `ModelVariantOut`) | Today both are absent |
| AC-117.10 | unit | New `mcp-server/tests/models-availability.test.ts`. `available`'s description names `devices`, `available` and `reason`, and `download`'s names the 409 for a variant this build can't run. Both keep the four markers. | Local Canon (03, "MCP") | Today neither description names them |
| AC-117.11 | unit | Same file, a guard. A mocked `available` answer with `available: false` and a `reason` comes back unchanged. A mocked download 409 `{code: "ConflictError", message: reason}` gives `TOOL_ERROR` "ConflictError: {reason}" after one fetch. | Local Canon (03, "MCP": the same fields and 409) | A guard: true today, and fails if the toolset starts filtering fields |
| AC-117.12 | unit | With a catalog whose PyTorch row is `available: false` with the reason, the TTS page's PyTorch option is disabled, its label is "PyTorch FP32 — {reason}", an ONNX row is selected, and every option keeps the G30 style (`ui/tests/unit/tts-page.behavior.test.ts`). | Human-approved (triage D-217: "shows the row disabled with the reason") | Today the option is enabled and, seeded first, selected |
| AC-117.13 | unit | New `ui/tests/unit/tts-model-selection.test.ts`. `defaultModelSelection` skips an unavailable chosen row, the first-downloaded rule and the first-row rule skip unavailable rows, the loaded row is kept, it returns `null` when no row is available, and a row without `available` counts as available. | Human-approved (triage D-217: "`defaultModelSelection` skips it") | Today the unavailable row is returned |
| AC-117.14 | e2e | In Electron, through the TTS seam with the catalog patched to an unavailable PyTorch row, the model select's PyTorch option is disabled with the reason in its label, and an ONNX row is selected (`ui/tests/e2e/tts-generate.test.ts`). | Local Canon (E2: an E2E assertion for a changed output element) | Row 5's AC-117.12 Red is the negative; this row runs after Green |
| AC-117.15 | smoke | `CAPABILITY_SMOKE` on a fresh onedir copied outside the checkout passes all four checks. | Human-approved (the brief's Done; 03, "Tests": the packaged smoke checks the 409) | On a copy of the 2026-11-04 onedir it fails at `listed_fields`, before any download request |
| AC-117.16 | smoke | `DEV_CHECK` loads `kokoro-pt-fp32` on `cpu` from the repo's `.venv` and generates a WAV of more than 8000 samples, with `available: true` listed. | Human-approved (triage D-217, "Dev") | A guard: row 0's `--baseline` run passes today; the strict run fails if the probe wrongly reports PyTorch absent |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Capability from whether the runtime imports, torch without kokoro unavailable | Human-approved | Triage D-217; 03 §TTS build capability, "Capability" |
| The reason texts | Local Canon | D-310, shown to Mat at the plan gate |
| 409 before any job or file, 422 with the same reason | Human-approved | Triage D-217; 03, "Refused" and "Load" |
| Where the 409 sits in the download's order | Local Canon | D-311: after the in-flight 409 and `NotFoundError`, before `_start_locked` |
| A file already on disk | Human-approved | Triage D-217; 03, "Existing file" |
| MCP gets the same fields and 409 | Local Canon | `models.ts` passes the JSON through; D-318 |
| Where the packaged smoke runs | Local Canon | D-315, as the brief asks the plan to state |
| The disabled option's look | Local Canon | D-320; G30 keeps the pair |

### MEU-118 `gui-tts-device-options`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `buildDevices(rows)` | `ui/src/renderer/src/features/tts/tts-devices.ts` | `rows`: `ReadonlyArray<{ devices?: readonly string[]; available?: boolean }> \| undefined`; returns a subset of `DEVICE_ORDER` in that order, always holding `DEVICE_FLOOR` | Other row keys ignored; unknown device strings dropped |
| Settings device select (`settings-leaf-device`) | `SettingsPage.tsx` | Options from `DEVICE_OPTIONS`; the value is the stored device when offered, else `auto` | Writes `{ device }` to `PUT /settings/tts` only on a user change |
| `tts.device` setting | `services/settings.py` | Unchanged: `auto`, `cuda`, `cpu` or `mps` | Unchanged |

#### Acceptance Criteria

Vitest and Playwright titles begin `AC-118.<n>`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-118.1 | unit | New `ui/tests/unit/tts-devices.test.ts`, loading the module through `import.meta.glob`. `buildDevices(undefined)` and `([])` give `DEVICE_FLOOR`. A CPU-only report gives `auto, cpu`, and a report with an ONNX row listing `cuda` gives `auto, cuda, cpu`. An unavailable row's devices are ignored: a PyTorch row with all four, unavailable, plus an ONNX row with `auto, cpu` give `auto, cpu`. Unknown strings are dropped, the order is `DEVICE_ORDER` with no repeats, and a row without `devices` adds nothing beyond the floor. | Local Canon (triage D-226; `DEVICE_PROBE`) | Today the module doesn't exist; the glob is empty, and the test asserts the module is there first |
| AC-118.2 | unit | New `ui/tests/unit/settings-tts-device.test.ts`, on the `settings-tts-runtime.test.ts` pattern. With the catalog answering a CPU-only report, the Settings device select offers exactly `auto, cpu`. With a CUDA report, it offers `auto, cuda, cpu`. Choosing `cpu` sends one `PUT /settings/tts` with `{device: 'cpu'}`. Every option keeps the G30 style. | Local Canon (triage D-226, 06 §TTS device options, "Options") | Today it offers all four |
| AC-118.3 | unit | Same file. A stored `cuda` with a CPU-only report shows `auto` and sends no PUT. With the report pending, and again with it answering 500, the options are `auto, cpu` plus the stored `cuda`, and `cuda` shows. | Local Canon (06, "Stored value"; `DEVICE_SELECT_VALUE`) | Today `cuda` shows among four options |
| AC-118.4 | unit | A guard in `tts-page.behavior.test.ts`, which doesn't import `tts-devices`. A selected row without `devices` lists `auto` and `cpu` on the TTS page, and a row listing `cuda` lists it. | Local Canon (D-317: the fallback reads the selected model's devices) | A guard: true today, and fails if the floor changes |
| AC-118.5 | e2e | In Electron, the Settings seam gains `options.catalog`, which answers `GET /models/available` (`ui/tests/e2e/settings.test.ts`). A CPU-only report gives `auto, cpu`, and a CUDA report gives `auto, cuda, cpu`. An unavailable PyTorch row with all four devices plus an ONNX row with `auto, cpu` give `auto, cpu`. A stored `cuda` with a CPU-only report shows `auto` with no PUT, and choosing `cpu` PUTs `{device: 'cpu'}`. The control is found by the literal `'settings-leaf-device'`, as the file already does at `:297` and `:304`, so `test-ids.ts` doesn't change. | Local Canon (06, "Tests": a Playwright pass against real Electron) | Row 10's AC-118.2 Red is the negative; this row runs after Green |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Options from the backend's report for this build | Local Canon | Triage D-226; the catalog's `devices` and `available` (D-313) |
| A stored value the build can't honour | Local Canon | 06, "Stored value"; shown as `auto` and kept, as `DEVICE_SELECT_VALUE` does |
| Options before the report arrives | Local Canon | D-314: the floor plus the stored value |
| The TTS page's fallback | Local Canon | D-317 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/tts.py` | modify | `ModelAvailability`, `model_availability`, `MODEL_REASONS` |
| `packages/core/src/avkit_core/ports/tts.py` | modify | `runtime_present` |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | `runtime_imports`, `runtime_probe`, `runtime_present`; the two texts (D-312) |
| `packages/core/src/avkit_core/services/models.py` | modify | `availability`; the download and load refusals |
| `packages/api/src/avkit_api/schemas/models.py` | modify | `available`, `reason` |
| `packages/api/src/avkit_api/routes/models.py` | modify | `_variant_out`, `CONFLICT_409`, download docstring |
| `openapi.committed.json` | modify | Regenerated |
| `mcp-server/src/toolsets/models.ts` | modify | `available` and `download` descriptions |
| `tools/smoke_packaged_tts.py` | modify | `phase_capability`, `--phase capability`; the docstring names the phase |
| `ui/src/renderer/src/components/ui/SelectInput.tsx` | modify | `disabled` on an option |
| `ui/src/renderer/src/features/tts/useTtsJob.ts` | modify | `CatalogItem.available`, `.reason` |
| `ui/src/renderer/src/features/tts/tts-controls.ts` | modify | `defaultModelSelection` skips unavailable rows |
| `ui/src/renderer/src/features/tts/tts-devices.ts` | create | `DEVICE_ORDER`, `DEVICE_FLOOR`, `buildDevices` |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | Disabled option and label; `DEVICE_FLOOR` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | Device options from the report; `TTS_DEVICES` removed |
| `tests/unit/test_domain.py` | modify | AC-117.1; AC-4.7 amended |
| `tests/integration/test_tts_device_resolution.py` | modify | AC-117.2 to AC-117.4; AC-98.5 ×2 and AC-115.9 amended |
| `tests/integration/test_tts_no_torch.py` | modify | AC-117.5 |
| `tests/unit/test_services.py` | modify | AC-117.6, AC-117.7; `FakeTTSPort.runtime_present` |
| `tests/e2e/api_fakes.py` | modify | `FakeModels.availability` |
| `tests/e2e/test_api_model_capability.py` | create | AC-117.8 |
| `tests/e2e/test_api_tts_models.py` | modify | AC-117.9 |
| `mcp-server/tests/models-availability.test.ts` | create | AC-117.10, AC-117.11 |
| `ui/tests/unit/tts-page.behavior.test.ts` | modify | AC-117.12, AC-118.4 |
| `ui/tests/unit/tts-model-selection.test.ts` | create | AC-117.13 |
| `ui/tests/unit/tts-devices.test.ts` | create | AC-118.1 |
| `ui/tests/unit/settings-tts-device.test.ts` | create | AC-118.2, AC-118.3 |
| `ui/tests/e2e/tts-generate.test.ts` | modify | AC-117.14 |
| `ui/tests/e2e/settings.test.ts` | modify | AC-118.5; `options.catalog` on the seam |
| `docs/build-plan/03-service-layer.md`, `04-rest-api.md`, `05-mcp-server.md`, `06-gui.md` | modify | §Spec text |
| `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md` | modify | Row 13, H2-2 |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md`, `.agent/context/triage-output.yaml` | modify | Row 13 |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modify | §6 tracker row 51 (`:241`) gets the plan folder and status |
| `.agent/context/current-focus.md` | modify | H1-3 |

No file guarded by a byte-hash test is edited: `ui/tests/e2e/test-ids.ts` (AC-51.6, AC-81.13) gains nothing, because no test id is added. Every file keeps its line endings: measured with Python bytes, written with `newline=""`.

### Project files

Plan-local scripts, listed in §Verification Plan: `baseline.sha`, `baseline-dirty.txt`, `baseline.ps1`, `red-check.py`, `identity.py`, `models-snapshot.py`, `models-before.json`, `dev-pytorch-check.py`, `issue-resolve.py`, `session-gate.ps1`. State: `docs/execution/metrics.md`, the two handoffs, the rolling reviews and the reflection. Outside the repository: the onedir copies and smoke run folders under `C:/Temp/av-kit/s51/`. The fresh build writes `packaging/build/` and `packaging/dist/`, which `.gitignore:33-34` ignores.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| The FP16 load and the load that keeps the model | deferred | MEU-119 to MEU-121 | Grouping §3 Session 52, D-245 |
| Bundled torch, a runtime download, a `KModel` import workaround | out-of-scope | — | Triage D-217; 03, "Not built" |
| espeak, downloaded or bundled | out-of-scope | — | Triage D-237 |
| A delete route for a model file | out-of-scope | — | 03, "Existing file" |
| The NSIS installer and the rc.2 gate run of the smoke | deferred | MEU-125 | D-315; the grouping's rc.2 session |
| `07-distribution.md:226` ("Known gap (Session 27)"), stale since MEU-72 | out-of-scope | — | Not in the brief; raised at the gate |
| `tts-commands.ts` `DEVICE_VALUES` and MCP `DEVICE_WIRES` | out-of-scope | — | Wire validation, not user options (§Device options) |
| A `/tts/devices` route | out-of-scope | — | D-313: the catalog already carries the report |
| A muted colour for a disabled option | out-of-scope | — | D-320; a G30 palette question for Mat |
| `mcp-audit` | out-of-scope | — | It touches the network and YouTube; the brief forbids YouTube writes and this session needs no network |

## BUILD_PLAN.md Audit

Row 13 adds Delivered notes to the residual sections in `03-service-layer.md` and `06-gui.md`. It sets MEU-117 and MEU-118 to `ready_for_review` with this `execution_plan` through `tools/meu_status.py`, then renders `docs/BUILD_PLAN.md`. The check:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s51-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s51-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. Runs `models-snapshot.py --record`, which writes `models-before.json`.
3. Runs `uv sync --frozen --all-packages`, `npm --prefix ui ci` and `npm --prefix mcp-server ci`. It then captures the base Python suite to `s51-base-py.txt`, the base UI suite to `s51-base-ui.txt` and the base MCP suite to `s51-base-mcp.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s51\tmp`.
4. Runs `dev-pytorch-check.py --baseline` to `s51-base-dev.txt`. A failure is S9.
5. Copies the pre-session onedir (`packaging/dist/avkit-backend`, built 2026-11-04 13:08) to `C:/Temp/av-kit/s51/backend-before/avkit-backend`, the input of row 8's Red. It records the copy's `avkit-backend.exe` SHA-256 in `s51-base-onedir.txt`, and it refuses to overwrite a copy that is already there.
6. Runs `red-check.py --selftest` and `identity.py --selftest`.

`red-check.py`, `identity.py` and `issue-resolve.py` are copies of Session 50's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds every name this plan adds (§2).
- **`identity.py`.** `PLAN` is this folder.
- **`PROJECT_ARTIFACTS`.** It holds this plan's `*.md`, the two handoffs, the review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The registers and renders stay bound, because row 13 writes them before H1-2.

### 2. Red then Green (rows 1 to 12)

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error, and it refuses a required test that fails on a missing name. So a required Python test first asserts that the new name exists, with `hasattr` on the imported module or `"runtime_probe" in inspect.signature(KokoroAdapter).parameters`. Only then does it use the name. A new Vitest file for a new module (`tts-devices.test.ts`) loads it through `import.meta.glob('../../src/renderer/src/features/tts/tts-devices.ts')`, which is an empty object while the file is missing, and asserts the module is there first. `DECLARED_NEW` lists the new names: `ModelAvailability`, `model_availability`, `MODEL_REASONS`, `runtime_imports`, `runtime_present`, `runtime_probe`, `availability`, `buildDevices`, `DEVICE_FLOOR` and `DEVICE_ORDER`.
- **`--require` matches exactly, so the amended tests are required by full name.** These are `test_ac_4_7_port_method_sets_and_signatures`, `test_ac_98_5_torch_absent_logs`, `test_ac_98_5_kokoro_import_logs` and `test_ac_115_9_load_failed_carries_detail`. `red-check.py:209` won't let `test_ac_117_1` match `test_ac_117_10`.
- **One runner summary per receipt.** Row 3's MCP Red runs Vitest in its own receipt with its own `.exit`, apart from the pytest receipt.
- **Guards pass in Red by design.** These are AC-117.11 and AC-118.4, and no Red row requires them.
- **AC-117.14 and AC-118.5 have no Red of their own.** They are E2E checks after Green (rows 7 and 12). Their negatives are AC-117.12 (row 5) and AC-118.2 (row 10).
- **The smoke's Red is its own kind (row 8).** `CAPABILITY_SMOKE` isn't a test runner, so `red-check.py` doesn't read it. Row 8 checks its Red receipt directly. The receipt must hold `FAIL: smoke_packaged_tts capability`, its JSON must have `failed_check` equal to `listed_fields`, and no download request may appear in it.
- **Expectations stay immutable in Green.** The four amended tests change in row 1, each with the §User Review Required basis.
- **Every file that renders `SettingsPage` runs in row 11, which runs the whole UI unit suite.** These are the `settings-*` unit files, `theme-selects.test.tsx` and `palette-curation.test.tsx`. Each filters its fetch calls by method and URL, so the new `GET /models/available` changes no count (`grep`, 2026-11-06). If one fails anyway, that is an expectation change: stop and bring it to Mat, as a Red row with its basis.
- **No real download.** Every Python test uses `FakeCatalog`, `FakeModels` or a monkeypatched import. The packaged smoke runs offline on stub files, and the dev check runs with `HF_HUB_OFFLINE=1` on files already on disk. Any step that would fetch a model, a voice or a runtime is S5.

### 3. The real models folder stays untouched

`models-snapshot.py --compare models-before.json` exits 1 if any file under `~/.avkit/models` was added, removed, resized or rewritten. It runs at the end of rows 2, 4, 9 and 12, and in the session gate (`models-untouched`). Only `DEV_CHECK` reads that folder, and its fast path writes nothing (S4).

### Plan-local scripts

Written with their rows and kept in this plan folder:

- `baseline.ps1`, `red-check.py`, `identity.py`, `models-snapshot.py`, `dev-pytorch-check.py` (row 0)
- `issue-resolve.py` (row 13). It is Session 50's, taking `--issue` once per issue, with the exclusive handle, `--expect-sha256`, the staged save and the `--set-file` refusal of any other key.
- `session-gate.ps1` (H1-2)

### Session gate (H1-2)

`session-gate.ps1` is Session 50's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s51-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `mcp-build`, `state-render`, `issues-render` |
| Runtime | `ui-electron` targeted to the `settings` and `tts-generate` specs; `package-build` (`tools/package_backend.py`); `smoke-capability` on a fresh copy outside the checkout; `dev-pytorch`; `models-untouched` |
| Skipped, with reason | `mcp-audit`: live network and YouTube. `build-record`: no installer build. |

`py-tests`, `ui-tests` and `mcp-tests` excuse only ids that row 0's receipts show failing, as Session 50 did.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py`, or row 8's smoke Red check | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`, or a path outside `baseline-dirty.txt` and this plan appears | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S4 | `models-snapshot.py --compare` reports a change to the real models folder | Stop; find what wrote it before anything else runs |
| S5 | Any step would make a real model, voice or runtime download, or any YouTube request | Stop before it runs; bring it to Mat |
| S6 | `openapi` drifts beyond the two fields and the three description strings (the shared 409 on download and load, and the download's description) | Stop; report the diff to Mat |
| S7 | Codex is unavailable or the ledger refuses | Mat |
| S8 | The packaged build fails, or it holds a `FORBIDDEN_DIRS` entry | Stop; report the build receipt to Mat |
| S9 | `DEV_CHECK --baseline` fails at row 0 | Stop; the dev path is broken before any change, so bring it to Mat |

## Decision Log

> [!WARNING]
> No decision here needs a separate Decision Brief file. Mat's brief and triage D-217 and D-226 settle the scope, and the reason texts are shown at the plan gate. D-312 lists its options in §User Review Required, a do-nothing option among them.
>
> Carried from the grouping and not relisted in the block, because the grouping's rows hold them: every §8 row, D-240 to D-250, D-267, D-277 and D-280, with stage `grouping`. Of those, D-245 makes TTS two sessions, and Session 51 carries it. The closeout check reads all of them, and D-246 stays as a withdrawn row.
>
> The triage decisions are in `.agent/context/known-issues.yaml`: D-217 under `TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME`, D-226 under `TTS-DEVICE-OPTIONS-IN-CPU-BUILD`, and D-236 (superseded by D-217) and D-237 under the closed `TTS-PYTORCH-RUNTIME-SETTINGS-DOWNLOAD`. The brief asked whether D-237 needs its own flag. The probe says yes (`C:/Temp/av-kit/s51-decision-issue-probe.txt`), so H2-2 passes three `--decision-issue` flags: the two issues this session closes and `TTS-PYTORCH-RUNTIME-SETTINGS-DOWNLOAD`.

```yaml
decision_log:
  - id: D-309
    stage: planning
    question: "How does the backend decide whether a variant can run in this build?"
    resolution: autonomous
    class: two-way
    chosen: "runtime_imports(fmt) in the adapter, beside runtime_devices: ONNX is True; PyTorch is False when torch is None, without importing kokoro, else True when 'from kokoro import KModel' succeeds and False with a class-name-only WARNING when it raises; the adapter memoizes the answer per format under a lock and the port exposes it as runtime_present"
    source_tag: Human-approved
    precedents: [".agent/context/known-issues.yaml — TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME D-217: from whether the runtime imports, torch without kokoro unavailable", "packages/infrastructure/src/avkit_infra/tts/adapter.py:72-96 — runtime_devices, the DEVICE_PROBE the rule names", "packages/infrastructure/src/avkit_infra/tts/adapter.py:303-308 — the load already imports KModel the same way"]
    research: { engine: none, sources: [] }
    reasoning: "Importing KModel is the test the load itself runs, so the list and the load can't disagree. importlib.util.find_spec would say kokoro is on the path without proving it imports, and a native DLL failure would slip through. Probing every format at startup would add about 3 s to every dev start (s51-probe-import-timing.txt), where the memoized probe pays it once, at the first catalog read. Doing nothing leaves the 327 MB download open. A packaged build has no torch, so it returns before any kokoro import and AC-72.1 holds."
  - id: D-310
    stage: planning
    question: "What does an unavailable variant say, and in what form?"
    resolution: autonomous
    class: two-way
    chosen: "A fixed text per format in MODEL_REASONS in the domain; PyTorch says 'This build can't run PyTorch models. Choose an ONNX model.'; ModelAvailability(available, reason) carries it, the reason set exactly when the variant is unavailable"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:595 — a reason that names a next step, the same shape as Voice availability", "packages/core/src/avkit_core/domain/tts.py:160-191 — VoiceAvailability, the shape this follows"]
    research: { engine: none, sources: [] }
    reasoning: "The same words have to reach the list, the 409, the 422, the log and MCP, and only text survives all five. A closed code with a renderer map, as VOICE_REASON does, would leave the 409, the 422 and MCP without words or with a second copy. Doing nothing gives no reason. The texts never hold exception text, so nothing raw reaches a log."
  - id: D-311
    stage: planning
    question: "Where and in what order are the download and the load refused?"
    resolution: autonomous
    class: two-way
    chosen: "ModelService.availability(fmt); download warms the probe before taking its lock, then keeps the in-flight 409 and NotFoundError first and raises ConflictError(reason) before _start_locked; load raises ModelLoadError(reason) after NotFoundError and before the legacy and vocab checks; each logs one WARNING with variant_id and detail"
    source_tag: Human-approved
    precedents: [".agent/context/known-issues.yaml — D-217: 409 before any download starts", "packages/core/src/avkit_core/services/models.py:201-212 — the download's order today", "packages/core/src/avkit_core/services/models.py:135-157 — the load's checks today"]
    research: { engine: none, sources: [] }
    reasoning: "Refusing in the service covers the route and MCP at once, and refusing before _start_locked means no runtime change, no thread and no file. Warming the probe outside the lock keeps a 3 s first import from holding the download lock. The load's reason comes before the vocab 409 so the user isn't told to fetch an asset for a model that can't run. Refusing in the route instead would leave the service open to any other caller."
  - id: D-312
    stage: planning
    question: "Does the adapter's own load error say the same reason?"
    resolution: autonomous
    class: two-way
    chosen: "Option A: the adapter raises MODEL_REASONS[PyTorch] where it says 'PyTorch runtime is not bundled' today (adapter.py:300, :308); the two AC-98.5 tests and AC-115.9's last block are amended; 'PyTorch model failed to load' (:312, :334) stays"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:600 — the 422's message carries the same reason", "tests/integration/test_tts_device_resolution.py:828-926 — the three tests that pin today's text"]
    research: { engine: none, sources: [] }
    reasoning: "One text on every path keeps the log's detail and any direct caller in step with the API. Option B, doing nothing in the adapter, is safe through the API, because the service refuses first, but it leaves a second wording for the same cause. The choice is at the gate."
  - id: D-313
    stage: planning
    question: "Where does the Settings device select get what the backend reports?"
    resolution: autonomous
    class: two-way
    chosen: "From the catalog the backend already returns: buildDevices joins DEVICE_FLOOR with the devices of every row whose available isn't false, kept to DEVICE_ORDER, in tts-devices.ts"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1547 — the same capability source as MEU-117", "packages/api/src/avkit_api/routes/models.py:42-53 — every row already carries its devices (DEVICE_FIELD)"]
    research: { engine: none, sources: [] }
    reasoning: "The catalog's devices and available fields are the capability source the residual names, so a second route would be a second copy of the same answer. Settings has no selected model, so it offers what any runnable variant can use, and the load still resolves the device per variant. Doing nothing keeps cuda and mps on a CPU-only build."
  - id: D-314
    stage: planning
    question: "What does the Settings select show before the report arrives, and for a stored value the build can't honour?"
    resolution: autonomous
    class: two-way
    chosen: "Pending or failed: DEVICE_FLOOR plus the stored value; after the report: a stored value that isn't offered shows as auto and nothing is written; choosing writes once as today; TTS_DEVICES goes"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1548 — a stored value keeps the existing device fallback", "docs/build-plan/11-page-layout.md:166 — DEVICE_SELECT_VALUE: shown and sent as auto, not rewritten", "ui/src/renderer/src/features/tts/useTtsJob.ts:94-99 — the shared catalog query"]
    research: { engine: none, sources: [] }
    reasoning: "Showing the stored value while the report loads avoids a flash of auto that looks like a change. Not writing auto keeps the user's choice for a later build that can use it, as the TTS page already does. Sharing the TTS page's query means one fetch per cache window, not a second one."
  - id: D-315
    stage: planning
    question: "Does the packaged smoke that checks the 409 run here or at MEU-125's rc.2 gate?"
    resolution: autonomous
    class: two-way
    chosen: "Here: --phase capability in tools/smoke_packaged_tts.py, Red on a copy of the 2026-11-04 onedir, Green on a fresh tools/package_backend.py build copied outside the checkout, offline on stub files; MEU-125 repeats the phase at rc.2 on the installer's copy"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:602 — the packaged smoke checks the 409 on a real build", "tools/smoke_packaged_tts.py:351-410 — phase_offline, the shape the new phase follows"]
    research: { engine: none, sources: [] }
    reasoning: "The Done line is about an installed build, and the frozen app is where torch is absent for real, so the session can't call it done without one. A onedir build needs no installer and no network. Waiting for MEU-125 would leave the Done line unproven for a whole session, and a fault there would land in the release gate."
  - id: D-316
    stage: planning
    question: "How is 'the dev venv still loads and generates' checked, and how is the real models folder protected?"
    resolution: autonomous
    class: two-way
    chosen: "dev-pytorch-check.py runs the backend as npm run dev does (sys.executable -m avkit_api) through a plan-local DevBackend subclass of the smoke's Backend, offline, with the real models folder, and loads and generates with kokoro-pt-fp32; models-snapshot.py records the folder at row 0 and compares it after rows 2, 4, 9 and 12 and in the gate"
    source_tag: Human-approved
    precedents: [".agent/context/known-issues.yaml — D-217: npm run dev keeps loading and generating", "ui/src/main/python-manager.ts:17-36 — the dev spawn argv", "packages/infrastructure/src/avkit_infra/model_manager/manager.py:54-72 — the fast path for a file already on disk"]
    research: { engine: none, sources: [] }
    reasoning: "The backend process is the part this session changes, so running it as Electron does proves the dev path without a window. Offline mode and the fast path mean the check reads files and writes none, and the snapshot proves it. Launching the full app by hand would prove the same thing with no receipt."
  - id: D-317
    stage: planning
    question: "What does the TTS page's own device fallback read?"
    resolution: autonomous
    class: two-way
    chosen: "selectedModel?.devices ?? DEVICE_FLOOR, the shared constant in place of the literal; the behaviour doesn't change"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/tts/TTSPage.tsx:274 — the literal fallback", "docs/build-plan/11-page-layout.md:166 — the selected variant's devices"]
    research: { engine: none, sources: [] }
    reasoning: "The page already reads the selected model's devices, as the brief asks, so only its fallback names the floor. One constant keeps Settings and the page from drifting."
  - id: D-318
    stage: planning
    question: "What changes in MCP?"
    resolution: autonomous
    class: two-way
    chosen: "Only the available and download descriptions, as explicit entries that keep the four markers; the JSON and the 409 already pass through"
    source_tag: Local Canon
    precedents: ["mcp-server/src/toolsets/models.ts:17-30 — the desc() loop and the explicit download_asset entry", "docs/build-plan/03-service-layer.md:599 — the same routes, the same fields and 409"]
    research: { engine: none, sources: [] }
    reasoning: "An agent reads the description before it calls, so naming the fields and the 409 there tells it to check available first. A code change would add nothing the route doesn't already send."
  - id: D-319
    stage: planning
    question: "Does 07-distribution.md need the D-217 correction?"
    resolution: autonomous
    class: two-way
    chosen: "No edit: :30 and :227 already say it (commit 83229ea, 2026-11-05); row 4 checks both; :226 is stale and stays out of scope"
    source_tag: Local Canon
    precedents: ["docs/build-plan/07-distribution.md:30 — 'PyTorch runtime (see Models)'", "docs/build-plan/07-distribution.md:227 — listed disabled with a reason, refused with a 409"]
    research: { engine: "git log -S", sources: ["83229ea docs(triage) — replaced 'optional extra' on both lines"] }
    reasoning: "The brief was written from the triage, before the triage commit changed these lines. Re-checking them proves the wording without a second edit."
  - id: D-320
    stage: planning
    question: "How does a disabled model option look?"
    resolution: autonomous
    class: two-way
    chosen: "It keeps its G30 pair; it can't be chosen, and its label carries the reason"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/components/ui/SelectInput.tsx:16-27 — G30_PAIRS and useG30Styles", "ui/tests/unit/theme-selects.test.tsx — AC-94.2 to AC-94.4"]
    research: { engine: none, sources: [] }
    reasoning: "G30 exists because the native list ignored the theme, and a muted pair would be a new palette decision. The reason in the label says more than a grey row would."
  - id: D-321
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "Identity; static py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths and red-check-selftest; full py-tests, ui-tests, ui-build, openapi, mcp-types, mcp-tests, mcp-build, state-render and issues-render; runtime ui-electron for the settings and tts-generate specs, package-build, smoke-capability, dev-pytorch and models-untouched; mcp-audit and build-record skipped"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:190-207 — the D6 stages", "AGENTS.md:82 — one fresh full scoped gate before final review"]
    research: { engine: none, sources: [] }
    reasoning: "The session changes core, infrastructure, the API contract, MCP text, the renderer and the packaged behaviour, so each has its check. mcp-audit would touch the network and YouTube, and there is no installer to record."
```

## Research References

- None outside the repository. The probe and the import timings were measured on this machine (§Planning receipts).

## Planning receipts

Under `C:/Temp/av-kit/`. Each probe was read-only with respect to the repository.

- **`s51-decision-issue-probe.txt`.** Through the closeout check's reader, the register gives D-217 under `TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME`, D-226 under `TTS-DEVICE-OPTIONS-IN-CPU-BUILD`, and D-236 and D-237 under `TTS-PYTORCH-RUNTIME-SETTINGS-DOWNLOAD`. The grouping gives the §8 rows. So H2-2 passes three `--decision-issue` flags.
- **`s51-probe-import-timing.txt`.** In the repo's `.venv`: torch 2.14.1+cpu imports in 0.88 s and kokoro `KModel` in 3.15 s; `torch.cuda.is_available()` is `False`.
- **`s51/probe-dev-runtime.txt`.** torch 2.14.1+cpu and kokoro 0.9.4 are installed; `~/.avkit/models` holds `kokoro-v1_0.pth` (327,212,226 bytes), `config.json` and a `spacy` folder (`ls`, 2026-11-06).
- **`s51-meu-stats.txt`.** 126 MEUs, 109 approved.
- **GUI check (create-plan Step 4A): `gui-refs-not-shipped`.** The five reference files that §4A names are absent (`ls`, 2026-11-06), so items 1, 2 and 4 are skipped. Items 3 and 5 still apply:
  - **E2.** The changed output elements are the model select's options (disabled, with the reason) and the Settings device select's options. AC-117.12 and AC-118.2 assert them in unit tests, and AC-117.14 and AC-118.5 in Electron. No test id is added.
  - **G32.** No raw hex is added. The disabled option keeps the existing G30 pair.
  - **G30** applies, because two `<select>` elements change. Every option keeps `style={g30}`, and `theme-selects.test.tsx` (AC-94.2 to AC-94.4) runs in rows 6 and 11.
  - **G31, G33, G34 and G35** don't apply. The session adds no accent, transition or button. Choosing a device writes the setting as today, so there is no new feedback tier to assign.
- **Not run at plan time:** any test, the packaged build, and any write to the repository.

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths`, `red-check-selftest`.
- **Targeted:** each row's test files, Red then Green; `openapi` in row 4; the E2E specs in rows 7 and 12; the smoke in row 8; the dev check in row 9; `models-snapshot.py --compare` in rows 2, 4, 9 and 12.
- **Fresh full:** `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `mcp-build`, `state-render`, `issues-render`.
- **Runtime:** `ui-electron` (targeted), `package-build`, `smoke-capability`, `dev-pytorch`, `models-untouched`.
- **Identity:** from `identity.py`, independent of the receipts.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
