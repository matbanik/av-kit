---
date: "2026-11-06"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s51-execution-2026-11-06-tts-build-capability"
round: 1
---

# Critical Review: 2026-11-06-tts-build-capability

> **Review Mode**: execution
> **Verdict**: approved

## Scope

Both MEU-117 and MEU-118 handoffs, their authoritative plan/task, the Session 51 working-tree changes against HEAD `71d0d3a`, relevant callers and regression tests, and the recorded Red/Green/full/runtime evidence. Author: Claude Code/Anthropic; independent reviewer: Codex/OpenAI. Checklist: IR-1 through IR-7, AV-1 through AV-6 and applicable contract/document checks.

**Intent anchor:** Session 51 makes the backend say, for each model variant, whether this build can run it, from whether the variant's runtime imports in this process. A variant it can't run is listed disabled with a reason that names a next step. Its download is refused with a 409 before any job or file exists, and its load keeps its 422 with the same reason. The TTS page can't select it, and the Settings device select offers only the devices that a runnable variant reports. The dev venv, which has torch and kokoro, keeps loading and generating with the PyTorch variant.

**Intent achieved: yes.** Review writes are confined to `C:/Temp/av-kit`. No product suite, app, packaging script, smoke phase, resolver or dev check was rerun. Independent probes used offline, bytecode-disabled Python, synthetic collaborators and the permitted temp directory; no model/runtime construction or network request occurred.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No evidence-backed material findings; no High or Critical findings.

## Checklist Results

### Q1 — Done, alternate routes and runtime evidence

**Accepted.** The sole production weights-fetch call is reached from `ModelService._run_download` after the guarded `download` entry (`packages/core/src/avkit_core/services/models.py:216`, `:307`). The REST and MCP routes converge there. `load` refuses before the adapter and automatic spaCy fetch (`:163`); generate requires an already loaded model (`services/tts.py:226`). Settings stores preferences; it has no alternate model loader. Sideload scans/registers existing files, without fetching weights. Asset downloads fetch shared vocab, spaCy or ONNX `.bin` voice packs, not an unavailable PyTorch variant (`model_manager/voice_packs.py:18`).

`CAPABILITY_SMOKE` checks the actual frozen backend outside the checkout, stopping on its first failed check (`tools/smoke_packaged_tts.py:533`, `:583`). The old onedir receipt records its 2026-11-04 executable identity; Red has only `listed_fields`, missing availability fields, and no download check/request. Fresh Green records four variants, unavailable downloaded PyTorch, 409/Idle/unchanged files, 422/16-byte stub retained, and both refusal logs. `DEV_CHECK` uses the same interpreter and argv shape as `buildDevSpawnArgv` (`ui/src/main/python-manager.ts:17`; plan `dev-pytorch-check.py:65`). Strict receipts prove PyTorch available, load 200 on CPU, and a 41,400-sample WAV at 24 kHz. Its 202 download is the existing-file fast path, with ready assets; snapshot comparisons show no real model changes. Accepted evidence proves this build/process contract, not arbitrary weight-file validity or the later installer gate.

### Q2 — Runtime source, memo and import hygiene

**Accepted.** `RUNTIME_PROBE` imports the same `KModel` used by `TORCH_PATH`, without constructing it; torch alone is insufficient. ONNX's runtime is already imported by the adapter module. The process shares one adapter (`packages/api/src/avkit_api/wiring.py:180`, `:198`), whose `_runtime_lock` caches both true and false per format (`tts/adapter.py:274`). Raising injected probes propagate, release the lock and leave no memo entry. The fakes provide the newly consumed port/service methods; real-adapter and real-packaged evidence supplement them.

Independent probes confirmed concurrent once-per-format calls, false caching, exception retry, and a class-only OSError log without a synthetic private-path marker. A fresh interpreter with torch blocked made zero kokoro requests. `IMPORT_HYGIENE`/AC-72.1 remains covered. The first dev catalog request incurs the accepted one-time import delay; these FastAPI handlers are synchronous worker-thread routes, not event-loop handlers. The slow probe is warmed outside the service download lock. No additional startup kokoro import was introduced, and `tts.runtime_probe_failed` emits neither exception text nor traceback (`adapter.py:119`).

### Q3 — Service, API, reasons and MCP

**Accepted.** Download warms the probe, then under the lock checks in-flight work, re-reads the row, checks not-found, refuses capability, and only then starts work (`services/models.py:224-241`). Independent probes observed the fixed reason, Idle runtime, no thread, no asset access and no model directory. Load's same-reason refusal precedes legacy/vocab checks; existing fallback and HTTP mapping remain intact. Choosing ONNX is a true next step because a running backend imports ONNX; its reinstall reason covers the complementary runtime failure rather than promising an unbuilt runtime installer.

All variant-returning routes use `_variant_out`, and the frozen domain availability value enforces reason iff unavailable (`routes/models.py:43`; `domain/tts.py:343`). OpenAPI changes are exactly the two required fields and three agreed description locations. MCP retains fields and converts the backend's 409 envelope to `ConflictError: {reason}` after one fetch (`mcp-server/src/client.ts:135`; `tests/models-availability.test.ts:37`). Shared load-409 description wording does not alter its actual 422 mapping.

### Q4 — Renderer selection and G30

**Accepted.** Disabled options carry the agreed reason and retain their G30 pair (`TTSPage.tsx:465`; `SelectInput.tsx:62`). Chosen, first-downloaded and first-row rules skip unavailable rows; missing `available` remains compatible and no runnable row returns null (`tts-controls.ts:111`). The agreed loaded-row exception is coherent with a process-stable probe and guarded loads; its available action is Unload. An unavailable unloaded row cannot become the selected model for Get/Load through normal UI selection. With no selected model the action is absent (`TTSPage.tsx:277`, `:496`). Unit and real-Electron assertions cover the changed picker output; AC-94.2–AC-94.4 remain in the recorded full UI pass.

### Q5 — Device options and Settings seams

**Accepted.** `buildDevices` ignores unavailable rows, unions the floor, filters unknown strings, deduplicates and orders the result (`tts-devices.ts:11`). Settings uses that union only after query success; pending/error includes the recognized stored device. An unsupported stored value displays auto without a PUT; a user change writes the selected value (`SettingsPage.tsx:375`, `:837`). Backend `DEVICE_RESOLVE`/`LOAD_FALLBACK` remains unchanged. The TTS page still uses its selected row's devices and the identical floor fallback, rather than Settings' union (D-317). The existing Settings seams tolerate the additional GET; the complete 112-file UI pass and 23 Settings Electron cases passed. New Electron seams explicitly cover CPU, CUDA, unavailable-row exclusion and unsupported stored values.

### Q6 — Amended tests and residual behavior

**Accepted.** AC-4.7 still asserts the exact port contract with `runtime_present` added. Both AC-98.5 cases retain device, error/cause, no-engine-call and unloaded-state assertions (`test_tts_device_resolution.py:838`, `:855`). AC-115.9 retains its nonempty/empty-detail cases and changes only the accepted torch-absent reason (`:902`). Active code/tests/UI/MCP contain no old bundled-runtime message or runtime-download offer. The remaining old sentence in 03's registration/problem history is followed by the Delivered contract, and 07 states D-217; it does not drive current behavior. The disclosed line-anchor changes and D-312 option A are sound.

### Q7 — Red evidence, test rigor and control strength

**Accepted.** Independent receipt parsing using the current `red-check.py` found assertion-only failures: port 8, service/API 5, MCP descriptions 2, renderer 6, devices/Settings 11; every required title matched, with zero setup/collection problems. The Settings Red stops at a query-state assertion because the old page never requests the report. This proves the missing query; Green and Electron assertions separately establish exact options and no-write behavior. The later `settled()` timer flushes Query's scheduled observer notification inside `act`, without changing product code or expected values (`settings-tts-device.test.ts:100`). The retained failing run, 15 isolated passes, two full UI passes and rerun full gate support that diagnosis.

| Scoped tests | Grade | Reason |
|---|---|---|
| `test_domain.py`: AC-117.1, amended AC-4.7 | Strong | Exact reasons, invariant failures, immutability and port method set |
| `test_tts_device_resolution.py`: AC-117.2–4, amended AC-98.5/AC-115.9 | Strong | Imports, sanitized fields, concurrency, retry, causes and retained regression assertions |
| `test_tts_no_torch.py`: AC-117.5/AC-72.1 | Strong | Fresh-process import recorder plus existing ONNX generation regression |
| `test_services.py`: AC-117.6–7 | Strong | Refusal ordering, exact errors/logs and no worker/port/asset side effects |
| `test_api_model_capability.py`: AC-117.8 | Strong | Real service through HTTP, exact fields/errors, positive acceptance and no-work checks |
| `test_api_tts_models.py`: AC-117.9 | Strong | Required schema types and specified description |
| `models-availability.test.ts`: AC-117.10 / AC-117.11 | Adequate / Strong | Description checks have their stated textual scope; guards compare complete JSON/error and fetch count |
| `tts-model-selection.test.ts`: AC-117.13 | Strong | Exact results for each selection rule, no available row and backward compatibility |
| `tts-page.behavior.test.ts`: AC-117.12/AC-118.4 | Strong | Disabled state, label, selection/G30 and selected-row device behavior |
| `tts-devices.test.ts`: AC-118.1 | Strong | Exact unions, floor/order, duplicates and unavailable/unknown exclusions |
| `settings-tts-device.test.ts`: AC-118.2–3 | Strong | Exact rendered options/value and PUT/no-PUT after a debounce window |
| `tts-generate.test.ts`, `settings.test.ts`: AC-117.14/AC-118.5 | Strong | Actual Electron controls through explicit seams; backend proof is supplied separately |

AC-117.11 and AC-118.4 are honest pre-existing-behavior guards, not claimed Red tests. Removing field pass-through would fail the former's exact-object/error assertions; changing the device floor or selected-row behavior would fail the latter's literal arrays. The material pre-change implementation demonstrably fails the actual Red receipts and packaged Red. No material broken behavior was demonstrated to false-pass the reviewed gate; description/schema tests are not treated as standalone runtime proof. Independent hashing reproduced both AC-51.6/AC-81.13's pinned prefix, `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454`. Registry content matches HEAD with normal checkout line endings; no registry edit is present.

### Q8 — Freshness, bounded writes and evidence truth

**Accepted with an explicit identity reconciliation.** The requested `uv run python -B .../identity.py --state-only`, with `ELECTRON_RUN_AS_NODE` unset, actually returns `71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+061ecf8c9cb36a116856994be67910a0f7e539995d7add456ffafe5891a89c44`. Runtime versions, distributions, font and lock hashes match the recorded gate. Git now lists one additional, unrelated untracked path: `.claude/settings.local.json`. Without inspecting its contents, an independent in-memory exclusion of that single outside-scope path reproduces **exactly** `71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62`. This is sufficient reconciliation of the reviewed inputs under Mat's explicit exclusion of unrelated work; it is not a claim that the unmodified whole-tree hashes match.

The gate's before/after states match; its step receipts support 1,274 Python, 1,163 UI, 470 MCP and 45 Electron passes, static/build checks, package build, capability smoke and strict dev check. Handoff evidence records distinguish historical row states from the final full state, and their decisive results match the examined receipts. Extracted PowerShell commands, the baseline lock-sync substitution, Git Bash redirects and the pre-existing tooling-only pyright diagnostic do not hide a failed scoped check.

Independent parsed comparison of the register against HEAD finds exactly ten changed leaf fields, all within status/verification/resolution_path on the two named issues; decision logs and other issue data are unchanged. `set_fields` preserves existing key order and adds the missing allowed key. Minor narrative correction only: the previously absent `resolution_path` belongs to the **device-options** issue at index 82, not the PyTorch issue named in MEU-117's execution note. This does not affect the bounded write or evidence. Independent file-stat comparison also reproduces MODELS_SNAPSHOT's 159 files and zero changes. The observed offline/fast-path receipts support no real model, voice, runtime or spaCy download; no review action wrote the real models folder.

### Observed reviewer evidence

```json
{"schema_version":"evidence.v1","check_id":"s51-independent-runtime-service","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s51-review-probe.py","cwd":"P:/av-kit","scope":"RUNTIME_PROBE, RUNTIME_PRESENT, AVAILABILITY and MODEL_REFUSAL; offline synthetic collaborators","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Session 51 working tree; reviewed-input identity 71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62 after the documented unrelated-path exclusion","output":"No torch: PyTorch false, ONNX true; failing kokoro import: false and class-only log; importable KModel: true with no construction; eight threads probe once per format; service refuses with the same reason and no thread, asset access, load, download or model directory."}
```

```json
{"schema_version":"evidence.v1","check_id":"s51-independent-import-hygiene","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s51-review-import-hygiene.py","cwd":"P:/av-kit","scope":"IMPORT_HYGIENE and raising-probe memo behavior; fresh process with network connections forbidden","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Session 51 reviewed working tree","output":"Fresh process with torch blocked: zero kokoro requests; ONNX present, PyTorch absent. Raising probe propagates, releases lock, retries next call and caches success."}
```

```json
{"schema_version":"evidence.v1","check_id":"s51-independent-evidence-audit","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s51-review-audit.py","cwd":"P:/av-kit","scope":"Saved Red/Green/full receipts, regression hashes, issue-register semantic diff and read-only model file stats","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Session 51 reviewed working tree and existing receipt set","output":"Five Red groups: assertion diagnostics only, all required titles found, zero problems. Both pinned registry-prefix hashes match. Register has ten leaf differences confined to the two issues' resolve keys. Real models: 159 files, zero differences. Packaged Red stops at listed_fields; Green checks all four stages. Full receipts: Python 1274, UI 1163, MCP 470, Electron 45 passed."}
```

```json
{"schema_version":"evidence.v1","check_id":"s51-independent-identity-reconciliation","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s51-identity-scope.py","cwd":"P:/av-kit","scope":"Diagnose whole-tree identity difference without changing the repository or inspecting unrelated local settings","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Whole-tree raw state ends 061ecf8c9cb36a116856994be67910a0f7e539995d7add456ffafe5891a89c44; reviewed-input state ends bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62","output":"Excluding only unrelated untracked .claude/settings.local.json reproduces the handoffs' full tested_state exactly. Raw HEAD-blob versus checkout byte hashes differ with CRLF conversion; the separate audit verifies identical normalized registry content and the exact unchanged guarded byte prefix."}
```

| Checklist | Result | Observed basis |
|---|---|---|
| IR-1 live runtime evidence | pass | Real frozen backend and dev load/generate receipts; no dependency overrides in those checks |
| IR-2 stub compliance | pass | Port/service fakes cover consumed methods; real-service HTTP and independent synthetic refusal probes supplement them |
| IR-3 error mapping | pass | Real-service HTTP tests and packaged 409/422 envelopes agree with domain mappings |
| IR-4 generalization | pass | Variant routes, MCP, load/generate, sideload and shared asset paths traced |
| IR-5 test rigor | pass | Grades and actual assertion-only Red evidence above; no Weak scoped test identified |
| IR-6 boundaries | pass | Existing strict REST/MCP input schemas remain; output fields are required and populated |
| IR-7 AC/deferral integrity | pass | All 16 MEU-117 and five MEU-118 ACs independently mapped; agreed guard/E2E distinctions and later-session boundaries preserved |
| AV-1 through AV-6 | pass | Red/Green evidence, actual assertions, no new masking/placeholder bypass and source-bound scope |
| H2/commit/installer repeat | n/a | Explicitly follows this review or belongs to the accepted later session |

## Verdict

`approved` — the reviewed work achieves the registered intent. No material correction is required. This approves the Session 51 implementation and evidence, with the explicit outside-scope identity reconciliation above. H2 closeout and any future commit remain the coordinator's subsequent work; this review authorizes no commit, push or installer release.
