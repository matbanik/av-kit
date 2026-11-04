---
date: "2026-10-17"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md"
loop_id: "s35-execution-2026-10-16-tts-voice-panel"
round: 4
verdict: "approved"
findings_count: 2
blocking_findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-gpt-6.1-sol"
intent_anchor: "Session 35 delivers MEU-75 (the TTS device list comes from the runtime, an unavailable or failing device falls back to CPU with a logged reason, the model status reports the device actually used, and a failed load returns its reason as a 422) and MEU-79 (the Voice panel lists only the selected model's devices and lays out Model, Device, the model action, Speed and Format at one control height on aligned rows, pinned by Electron geometry at the default window)."
intent_achieved: "yes"
---

# Critical Review: 2026-10-16-tts-voice-panel

> **Review Mode:** execution, ledger round 1 of 6  
> **Verdict:** changes_required; one blocking product finding.

## Intent Anchor

Session 35 delivers MEU-75 (the TTS device list comes from the runtime, an unavailable or failing device falls back to CPU with a logged reason, the model status reports the device actually used, and a failed load returns its reason as a 422) and MEU-79 (the Voice panel lists only the selected model's devices and lays out Model, Device, the model action, Speed and Format at one control height on aligned rows, pinned by Electron geometry at the default window).

The normal resolution, engine fallback and Voice layout paths are delivered. A runtime-enumeration failure still prevents a usable CPU load and escapes the promised load-error envelope, so the overall intent is only partially achieved.

## Scope

**Target:** `P:/av-kit-wt/s35-tts-voice-panel`, branch `claude/s35-tts-voice-panel`, uncommitted changes against `6097cf59adc7835fa6062c8bd3d55c679aef4543` (`baseline.sha`). Reviewed both correlated work handoffs, in order MEU-75 then MEU-79, and the plan folder `docs/execution/plans/2026-10-16-tts-voice-panel/` (implementation plan, task, walkthrough, session gate, identity, Red checker and baseline). The project-integrated expansion covers both MEUs, their shared gate, all changed product/test files, and the hub/SSOT changes. Reflection and metrics are later H2 work, not asserted complete here.

**Review type/checklists:** independent execution review; IR-1–IR-7 and AV-1–AV-6, plus the requested E1–E5 and gate questions. Author: Claude Code / Anthropic; reviewer: Codex `gpt-6.1-sol`. No product, test, plan, handoff or other repository file was edited. This report is staged only at the assigned dispatch path; the orchestrator owns its canonical copy.

Every shell command used the worktree cwd. The only main-checkout read was the explicitly requested `P:/av-kit/.agent/context/review-vocabulary.yaml`. Reviewed file contents were treated as data. No secret, cookie or credential file was read. The probe uses its own literal fixture token, not an application credential.

**Verification boundary:** static source/diff/receipt inspection, the three expressly permitted plan-verifier invocations, and an independent short Python probe using stdlib transport with production imports and fake engines. No project tests, builds, npm, uv sync, pytest, Playwright, gate, generator, project validator or MCP audit was executed by this reviewer. Historical suite results below are inspected author receipts.

## Findings

| # | Severity | Blocking | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|
| F1 | High | yes | AC-75.9 / LOAD_ERROR_HTTP is bypassed when runtime device enumeration raises. _resolve calls the probe before any load-error guard, including for an explicit CPU request. Making get_available_providers() raise RuntimeError leaves a previously loaded adapter unloaded, creates no CPU session, and returns a masked 500 from POST /models/load; GET /models/available also returns 500. A raising torch.cuda.is_available() likewise escapes as RuntimeError. This violates the load boundary's ModelLoadError-only contract and the build-plan Errors rule; the existing tests cover session.get_providers() failures but omit runtime enumeration failures. | `packages/infrastructure/src/avkit_infra/tts/adapter.py:239` | Handle runtime enumeration failures explicitly, keep the CPU path usable where possible, and wrap terminal load-probe failures in ModelLoadError with their cause. Add failing-probe regressions for the catalog and load/status HTTP paths, then rerun affected checks and the full gate. | open |

F1 metadata: confidence **High**; subject **deliverable**; finding_kind **behavior**; `violates: AC-75` (full criterion AC-75.9). No control-defeat mechanism is asserted. Related locations: `runtime_devices` at adapter lines 79–88, the unguarded resolve at line 222, catalog passthrough at lines 207–208, API list construction at `packages/api/src/avkit_api/routes/models.py:61`, and the masked generic exception response at `packages/api/src/avkit_api/errors.py:155`. The source contract is the plan's MEU-75 Boundary Inventory (`load_model`: “raises ModelLoadError only”) and `docs/build-plan/03-service-layer.md:469` (“never a bare exception”). This is a reproduced product failure, not a request to redesign review machinery.

### F1 reproduction

The scratch probe `C:/Temp/av-kit/dispatch/s35-review-probe.py` imports the real adapter, domain types and production ASGI application. Its fake ONNX factory can create both CUDA and CPU sessions. It first loads CUDA successfully, then makes the module's `get_available_providers()` raise `RuntimeError("provider enumeration failed")`. It requests CPU on the same adapter and drives the real HTTP routes in process, with a tiny model-service facade and stdlib ASGI transport. All temporary fixture writes stay under dispatch; the weight fixture is removed in `finally`. No test module or suite is imported or invoked.

Decisive output (probe process exit **0**, indicating the diagnostic script completed, not that the product passed):

```text
prior_load True cuda
onnx_cpu_load {"exception": "RuntimeError", "message": "provider enumeration failed", "is_ModelLoadError": false, "session_calls": [], "events": [], "loaded": false, "device": "cpu"}
onnx_catalog_probe RuntimeError provider enumeration failed
HTTP POST /api/v1/models/load 500 {"error":{"code":"internal_error","message":"Internal server error","details":{"request_id":"202185fc-a729-46ca-932a-28cef15e82c1"}}}
HTTP GET /api/v1/models/available 500 {"error":{"code":"internal_error","message":"Internal server error","details":{"request_id":"50c30204-bc5e-425b-b4f3-961dd1417b04"}}}
pytorch_cpu_load RuntimeError is_ModelLoadError False
```

The old model is correctly cleared; the defect is the failed resolution/error path, not stale adapter state. The CPU session is never attempted despite being usable in this probe. The API's intentional generic-500 behavior is correct for unrelated programming errors; the adapter must classify its own runtime-probing failure before that handler.

## Commands Executed and Decisive Output

All exact-evidence shell operations used `rtk proxy`, all-stream receipts under `C:/Temp/av-kit/s35-review-*.txt`, immediate `$LASTEXITCODE` capture, receipt readback and exit propagation. Source/receipt reads used `rtk proxy pwsh -NoProfile -Command '... Get-Content ...'`, with numbered lines where references were needed. Independent reads were sometimes batched; dependent probe edits/runs were sequential.

### Independent executable checks

The three plan commands used the worktree `.venv/Scripts/python.exe`, `PYTHONDONTWRITEBYTECODE=1` and unset `ELECTRON_RUN_AS_NODE` (the state invocation also set `RECEIPTS_DIR=C:/Temp/av-kit`).

| Executed command | Exit | Decisive output |
|---|---|---|
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/red-check.py --selftest` | 0 | `red-check selftest: 35 fixture(s) (11 positive, 24 negative), 0 wrong: []`. Launch/locator failures, unrelated imports/keywords, missing blocks, unhandled errors, a passing required test and an absent exit file are refused. |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --selftest` | 0 | `identity selftest: 0 failure(s)`. Sixteen bound paths, an untracked test and three runtime mutations change identity; historical full evidence is refused for bound-path mutations. Nine closeout outputs leave identity unchanged. |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --state-only` | 0 | `6097cf59adc7835fa6062c8bd3d55c679aef4543+039931efaad0f7994c8995f8ddc6593ce4821f10d25c3c0ee800aa5e1fa15758` — exactly both handoffs and H1-2 before/after. |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-review-probe.py` | 0 | Product observations fail as shown under F1: CPU load throws `RuntimeError`, no session/fallback log, HTTP load/catalog 500. The initial adapter-only run established the same exceptions; the final run added production HTTP verification. |

### Static command inventory

Executed `rtk proxy git status --short`; `rtk proxy git diff 6097cf5 --stat`; and `rtk proxy git diff 6097cf5 -- <paths>` for the adapter, the remaining nine product/schema paths, all changed Python test/fixture paths, all three UI test paths, and the six hub/SSOT/rendered paths. Inspected the new untracked adapter test directly. Status has **29 modified tracked paths and five untracked paths**, including the two work handoffs, baseline, walkthrough and new test. Diff stat: `29 files changed, 757 insertions(+), 130 deletions(-)`. Git's global-ignore permission warning was visible; it did not prevent reading status/diffs or deriving the exact matching identity.

Executed bounded `Get-Content` reads of the protocol, operating context/profile/guardrails, plan/task/walkthrough/scripts, both handoffs/template/schema, reviewer role, architecture/testing guidance, completion-preflight skill, changed source and tests, supporting SelectInput/Button, the main-window factory, Playwright config and queue-canon AC-41.3. `Get-ChildItem ... -File` inventoried only the named Session 35 snapshot/closeout directories. Completed receipt reads covered baseline UI, MEU-75/79 Red/Green, H1-2 and row-6 snapshots, hub/render and closeout records. `Get-FileHash -Algorithm SHA256 ... | Format-List Path,Hash` captured the hashes below. These observations were read operations, not reruns of the recorded commands.

### Observed author evidence

| Stage / receipt | Observed result |
|---|---|
| Row 0 | Baseline SHA equals `6097cf59…4543`; Python `2 failed, 904 passed`; UI `1 failed, 974 passed (975)`; TTS Electron `16 passed`. |
| MEU-75 Red | `23 failed, 2 passed, 147 deselected`; adjacent `.exit` is `1`; Red checker `1 receipt(s), 0 required test(s), 0 problem(s)`. Missing new names/keywords and the absent response field account for the listed failures. |
| MEU-75 Green | `172 passed, 1 warning`; OpenAPI check 0; MCP build succeeds and `428 passed`. |
| MEU-79 Red | UI `5 failed, 1 passed, 34 skipped (40)`; Electron `3 failed, 1 passed`; both `.exit` files are `1`. Required AC-79.7/.8/.10 fail by `expect`; checker reports `2 receipt(s), 3 required test(s), 0 problem(s)`. The 34 skipped tests are the intended `-t AC-79` selection, not skip annotations. |
| MEU-79 Green | Unit `40 passed`; TTS Electron `20 passed`, including AC-64.6 and all four new Electron tests. |
| Row 6 | Full gate accepted the baseline-only Python/UI failures, Electron `161 passed`, repeat `50 passed`; before/after state `6097cf5…+38f98d80…6e09`. |
| H1-2, run of record | Static steps exit 0; Python only AC-24.10/AC-25.10 fail (`2 failed, 929 passed`); UI only AC-41.3 fails (`1 failed, 980 passed (981)`); MCP `428 passed`; build/OpenAPI/state-render 0; Electron `161 passed (3.6m)`; repeat `50 passed (38.0s)`; before/after state `6097cf5…+039931ef…5758`; wrapper concludes `session-gate: all steps exit 0`. |
| Hub / closeout | Render: `Drift check passed` (91 MEUs, 12 phases). OpenAPI schema comparison: `added: [] removed: [] changed: ['ModelVariantOut']`. Both handoff checks and live-state evidence checks pass. H1-7 and H2 remain pending as expected. |

H1-2's raw Python/UI exits were **1**, accepted by the declared baseline predicates; they are not represented as raw suite successes. These receipts establish the tested tree and exercised normal behavior; they do not invalidate F1's independent negative-path result.

### Snapshot hashes

SHA-256, obtained with `Get-FileHash` via `rtk proxy pwsh` (exit 0):

| Receipt (relative to `C:/Temp/av-kit/`) | SHA-256 |
|---|---|
| `s35-gate-h1/s35-gate-h1.txt` | `453308F37F2025C2A3352D59A2842B5194171B9F699F17A99BC6D79A165A6098` |
| `s35-gate-h1/s35-D6-py-tests.txt` | `8551A31F2D63AEEE1C8C7775015C22B9C9E5C8996417605B6161AC35E7DDFE80` |
| `s35-gate-h1/s35-D6-ui-tests.txt` | `39099E521010A90E706DFC3B47D6C2B08B572550CFEC28B1C83553E4343A7632` |
| `s35-gate-h1/s35-D6-ui-electron.txt` | `C7DBEE989DA2CD02D08058A6E7B0EB53DC7DDBAE7B937B2B0AD269DD249ED0F8` |
| `s35-gate-h1/s35-D6-e2e-repeat.txt` | `43331C95ADA400B1D2F1B46A3B6D04FD4F0B312F0D5F69CB6D14DEA0562505CD` |
| `s35-base-ui.txt` | `5651448EF400ADFC28ED184C5A20BBE7054352D502AA2F29C3234F15ADEF3366` |
| `s35-75-red-py.txt` | `C56FE03D9E97D3AE6427F1E9B182B2FAA939CABF9FE2B3C03F37EA472F98DD07` |
| `s35-79-red-ui.txt` | `810967E922AB9F430110E6E27D6F17818F2AA7C3FF162DFDBE6327E7BF7BDF74` |
| `s35-79-red-e2e.txt` | `FAC37E10B48A813E6177DE98FF8A1D85E2D72FB01FB283645D6EED685EBEAF35` |
| `s35-review-probe.txt` | `BAE510C78408D4C0BB03274CAD23ABEF0196A3B6BFDF6C92E5C887453555037E` |

## Acceptance-Criteria Trace

Paths are worktree-relative. “Pass” means the specified behavior has substantive code/assertions and matching recorded execution; it does not claim a fresh reviewer suite run. AC-75.9 is incomplete because its load-error contract fails in F1; existing happy-path/error-map tests do not detect that case.

### MEU-75

| AC | Product file:line delivering behavior | Test file:line that would fail without it | Status |
|---|---|---|---|
| AC-75.1 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:72` (torch flags, None and getattr; ordered filtering at 89) | `tests/integration/test_tts_device_resolution.py:187`; `tests/integration/test_tts_no_torch.py:150` | Pass specified matrix/no-torch cases; probe exceptions are F1. |
| AC-75.2 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:80` (ONNX providers, no MPS) | `tests/integration/test_tts_device_resolution.py:210` | Pass specified provider lists; raising enumeration is not covered. |
| AC-75.3 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:237`; fallback log at 92 | `tests/integration/test_tts_device_resolution.py:231`, `:255` | Pass: explicit unavailable CUDA/MPS use CPU, exact warning/no-warning bounds. |
| AC-75.4 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:250`; initial unload at 220, commit fields at 231 | `tests/integration/test_tts_device_resolution.py:309`, `:330`, `:357`, `:377` | Pass: move retry, constructor/eval final failure, original cause, log, path redaction, prior-load terminal state. |
| AC-75.5 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:282` | `tests/integration/test_tts_device_resolution.py:398`, `:420`, `:443`, `:463`, `:486` | Pass: silent provider fallback, construction/provider-read retry, CPU failure/state; CPU session does not query providers. |
| AC-75.6 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:240` | `tests/integration/test_tts_device_resolution.py:275`, `:294` | Pass specified Auto preference and no-warning cases. |
| AC-75.7 | `packages/core/src/avkit_core/ports/tts.py:41`; `packages/core/src/avkit_core/services/models.py:105`; adapter `:207` | `tests/integration/test_tts_device_resolution.py:500`; `tests/unit/test_services.py:2201`; protocol set `tests/unit/test_domain.py:1154` | Pass: actual probe/port forwarding and protocol declaration. |
| AC-75.8 | `packages/api/src/avkit_api/schemas/models.py:48`; `packages/api/src/avkit_api/routes/models.py:42`, `:61`, `:72`, `:95`; `openapi.committed.json:1886` | `tests/e2e/test_api_tts_models.py:199`, `:206`, `:215` | Pass normal catalog/download variants, required enum schema and invalid-device rejection. |
| AC-75.9 | `packages/api/src/avkit_api/errors.py:36`, `:150`; routes/models `:99`; adapter status `:184`; unguarded probe `:239` | `tests/e2e/test_api_error_surface.py:274`, `:282`; `tests/integration/test_tts_device_resolution.py:520`; independent probe above | **Fail F1:** existing tests pin mapped 422, unrelated masked 500 and CPU status after unavailable-device fallback; none covers failing runtime enumeration. |
| AC-75.10 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:72` | `tests/integration/test_tts_device_resolution.py:549` | Pass: real installed torch/ONNX availability is compared, including MPS; no hard-coded host success. |

### MEU-79

| AC | Product file:line delivering behavior | Test file:line that would fail without it | Status |
|---|---|---|---|
| AC-79.1 | `ui/src/renderer/src/features/tts/TTSPage.tsx:266`, `:474`; `useTtsJob.ts:58` | `ui/tests/unit/tts-page.behavior.test.ts:727` | Pass exact lists before/after model switch. |
| AC-79.2 | `ui/src/renderer/src/features/tts/TTSPage.tsx:267`, `:475`, `:495`; user-only persistence at 477 | `ui/tests/unit/tts-page.behavior.test.ts:737` | Pass: effective Auto posted; stored CUDA retained; no settings PUT on selection. |
| AC-79.3 | `ui/src/renderer/src/features/tts/TTSPage.tsx:266` | `ui/tests/unit/tts-page.behavior.test.ts:754` | Pass absent-field Auto/CPU fallback. |
| AC-79.4 | `ui/src/renderer/src/features/tts/TTSPage.tsx:196` (existing ApiError/message path) | `ui/tests/unit/tts-page.behavior.test.ts:761` | Pass characterization; actual 422 message, not a fetch error. |
| AC-79.5 | `ui/src/renderer/src/components/ui/SegmentedControl.tsx:22`, `:26`, `:36` | `ui/tests/unit/layout-primitives.test.ts:306` | Pass: original sm/default literal, md only adds h-9, radio/label HTML identical. Source diff leaves all other markup unchanged. |
| AC-79.6 | `ui/src/renderer/src/features/tts/TTSPage.tsx:452`, `:487`, `:585`, `:591`, `:603`, `:616` | `ui/tests/unit/tts-page.behavior.test.ts:782` | Pass DOM classes and wrapper; geometry is separately measured. |
| AC-79.7 | `ui/src/renderer/src/features/tts/TTSPage.tsx:452`, `:487`; `components/ui/SelectInput.tsx:26` | `ui/tests/e2e/tts-generate.test.ts:762` | Pass model/device/action heights/bottoms, actual label tops, model width. |
| AC-79.8 | `ui/src/renderer/src/features/tts/TTSPage.tsx:585`, `:591`, `:603`, `:616`; SegmentedControl `:36` | `ui/tests/e2e/tts-generate.test.ts:781` | Pass actual combobox/select/range/preset inner boxes, bottom and width relationships. |
| AC-79.9 | `ui/src/renderer/src/features/tts/TTSPage.tsx:452`, `:585`, `:637` | `ui/tests/e2e/tts-generate.test.ts:807`; existing AC-64.6 `:602` | Pass row scroll/client widths, slider >=96 px and default-window visibility in the same run/repeat. |
| AC-79.10 | `ui/src/renderer/src/features/tts/TTSPage.tsx:266`, `:474`; seam catalog `ui/tests/e2e/tts-generate.test.ts:67` | `ui/tests/e2e/tts-generate.test.ts:836` | Pass exact ONNX Auto/CPU -> PyTorch Auto/CUDA/CPU after real select interaction. |

## Requested Substantive Answers

### E1 — Delivery and failure paths

The successful runtime matrix and ordering are correct; ONNX never reports MPS, the injectable probe is actually used, and unavailable explicit devices log the specified reason. Auto preference is CUDA, MPS, CPU with no fallback warning. Both engine paths build in locals after the initial unload. PyTorch non-CPU `.to()` failure retries CPU; constructor/eval or a failed CPU retry is wrapped with the original cause and path-free message. ONNX CUDA constructor or session `get_providers()` failure retries CPU; a successful session without CUDA reports CPU; the CPU path never queries active providers. Fields are assigned after success, so terminal engine errors after a prior CUDA load leave all model/session/variant fields empty and device CPU. The tests assert these values and call sequences rather than merely running the code.

The prompt's E1 shorthand mentions retrying `.eval()`, but the approved `LOAD_FALLBACK` contract and AC-75.4 expressly make a raising `.eval()` final. Implementation and tests follow that approved distinction; no new retry requirement is imposed here. Missing optional torch and a kokoro `ImportError` take the named `ModelLoadError` branches. Runtime availability-query failures are different: neither `get_available_providers()` nor torch availability queries are guarded, and `_resolve` is outside the engine guards. F1 demonstrates the resulting 500 and unavailable catalog, even for CPU.

Port/service/API forwarding is real, response `devices` is required, and every catalog/download-variant construction supplies it. The OpenAPI diff consists solely of that field and its required entry. The UI consumes selected-row devices, sends effective Auto when necessary and persists only user changes. The changed primitive keeps sm/default bytes by inspection of its actual diff and the characterization assertions.

### E2 — Geometry oracles

The geometry tests execute built Electron with a fresh `AVKIT_APP_DATA` directory; `createWindowOptions` (`ui/src/main/index.ts:140`) therefore uses 1280x800. They wait for the voice request, selected default model, **present Unload button**, then two animation frames. They measure native selects and the actual action, label associations, combobox, range and the preset group's inner div. Null boxes fail; missing labels yield NaN and fail. Heights/bottoms/label tops use a genuine inclusive ±0.5 px bound, not loose rounding. D-20's helper changes only diagnostics: a delta outside the bound remains nonzero and fails `toEqual`.

AC-79.9 measures the real model row and slider grandparent, fails missing containers, rejects overflow, and requires a 96 px slider. The full/repeat receipts include AC-64.6. AC-79.10 checks exact option values on both sides of a real model switch, not just a count or a static seam field.

The height comparisons are relative to Model, as the approved VOICE_GEOMETRY states; alone they would not reject a uniform change to every control's absolute height. For this deliverable, unchanged SelectInput supplies h-9, changed action/slider classes are unit-pinned h-9, the preset test pins the md class and all boxes are compared. No uniformly wrong-height implementation or misalignment is present in the reviewed tree. The no-action ad-hoc measurement is accurately disclosed and is not used as a substitute for the action-present Electron oracle.

### E3 — Test integrity and amendments

Inspected every changed test/fixture diff plus the new 566-line adapter test. Existing assertions are preserved. TA-1 narrowly enables CUDA only around the pre-existing explicit-CUDA load, retaining status/call assertions and other real-probe cases. TA-2 provides the new facade method; TA-3 extends the exact protocol set; TA-4 adds the port fake's method/call recording; TA-5 needs no edit because legacy fixtures use Auto/CPU; TA-6 adds per-row devices to the existing Electron seam. These are honest consequences of the approved contracts. No existing assertion deletion/re-expectation, skip/only, retries or timeout increase was introduced. The new torch-blocked subprocess uses the existing module's 300-second subprocess convention; it does not alter an existing timeout. F1 is a missing negative case, not an intentionally weakened test.

IR-5 grades: all new adapter matrix/resolution/retry/error/state/status/live-probe tests, the torch-blocked subprocess, service passthrough, API values/schema/error-envelope tests, UI AC-79.1–.4 and .10, and primitive byte characterization are **Strong** (specific values, causes, call sequences or payloads). DOM-class AC-79.6 is **Adequate** for its explicit class contract and is backed by **Strong** Electron AC-79.7–.9. Existing TA-1 assertions remain Strong; TA-2/3/4/6 fixtures retain their purpose. No changed test is vacuous. The error-path coverage gap is specifically recorded in F1/IR-3.

### E4 — Evidence honesty

Both full `evidence.v1` records bind exactly the independently derived state printed above. H1-2 is the fresh run after hub/SSOT inputs changed; row 6's earlier state is correctly narrative only. Red/Green counts, actual assertions/declared-name failures, baseline diagnostics, gate totals and closeout outputs agree with the inspected receipts. The current status has three additional excluded closeout outputs beyond H1-2's 31 scoped paths (focus and two handoffs), explaining the current 34 without changing tested_state. No fabricated success or hidden skip was found. The recorded evidence is honest but lacks F1's negative case.

### E5 — Scope and hubs

Every modified/untracked path is in a Files table, the plan folder, or the session's handoff/current-focus administration. No other product surface, MCP implementation or CSS token input changed. `openapi.committed.json` only adds `ModelVariantOut.properties.devices` and its required entry. Matrix rows 3.8/11.13 have the planned names/dependencies; the 03 delivered note and 11 grid/device/geometry contracts describe the implemented normal paths. SSOT and generated rows accurately say `ready_for_review`, not approved. The build-plan promise of no bare load errors remains unmet in F1; this is the same product finding, not a separate clerical objection. The minor existing Phase-9 scalar reflow has no semantic change.

### A-1 / D-19 — UI baseline rule

**Acceptable application of the approved baseline rule for this tree.** Verification Plan §1 says baseline failures are listed and never counted as regressions, and row 6 repeats that rule without restricting it to Python. A-1 extends that existing rule to the observed UI baseline; it neither changes tests nor excuses new IDs. It is disclosed, and the modified script is included in the matching input identity.

The predicate requires raw exit 1, a nonempty unique FAIL-id set contained in the one expected AC-41.3 ID also observed in row 0, a matching failed-test summary count, and no detected unhandled-error/error-summary line. A second failure without a FAIL header makes the summary count disagree; a new suite/header or any new layout-canon/queue-canon ID is outside the allowed set. No FAIL line or no summary refuses acceptance; a non-1 crash exit is not normalized. Full-suite argv remains `npm --prefix ui run test`, with no filter; package/config/test diffs introduce no filtering. The supplied nine-case probe receipt reports nine correct outcomes, consistent with source inspection; it was read, not rerun.

A fabricated or deliberately filtered receipt with only the allowed test could satisfy this text predicate: it is not a cryptographic proof of executing a full suite. That hypothetical does not describe the inspected run: its receipt has 96 files/981 tests, complete full argv in the gate, matching bound input identity, and no filtering changes. No concrete Session 35 false-pass was demonstrated.

AC-41.3 (`ui/tests/unit/queue-canon.test.ts:160`) reads Zorivest's live globals.css and av-kit's unchanged styles.css with fixed token expectations. It does **not** read the matrix/SSOT/layout-doc files that other queue-canon tests consume. None of the Session 35 changed paths reaches AC-41.3's token inputs. Both baseline and H1-2 fail at the same light pending-token comparison (`expected '#9a3412' to be '#ea580c'`). Thus the exception cannot hide a Session 35 change to those inputs in this tree. A future token-input change would require reassessment rather than blind reuse of this conclusion.

### Python baseline

The py-tests predicate is unchanged from the approved gate. H1-2's complete short receipt contains exactly the two expected packaging failures: missing packaged executable (AC-24.10) and missing bundled ffmpeg/ffprobe (AC-25.10), followed by `2 failed, 929 passed, 1 warning`. There is no third FAILED ID or ERROR section. The baseline receipt records the same two IDs; acceptance is justified for this run.

## Checklist Results

Observed manual procedures below were performed by **codex-gpt-6.1-sol**, with null exit code; command checks carry their actual process exits. A check of recorded evidence does not claim the reviewer executed its historical suite.

| Check | Result | Command or observed procedure | Exit | Evidence |
|---|---|---|---|---|
| IR-1 Live runtime evidence | pass | Inspect AC-75.10 source and H1-2 Python receipt; inspect real-Electron full/repeat receipts. | null | Installed-runtime probe has no dependency overrides; 929 Python passes apart from the packaging pair; Electron 161 and repeat 50 passes. No real GPU synthesis claim. |
| IR-2 Stub behavioral compliance | pass | Inspect Engines, FakeModels/FakeTTSPort and Electron catalog seam against actual collaborators. | null | Calls, devices, active providers, status and selected-row payloads are explicitly asserted. |
| IR-3 Error mapping completeness | fail | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-review-probe.py` | 0 | F1: runtime enumeration escapes ModelLoadError mapping; POST load and GET catalog return masked 500. Script completion exit 0 does not denote product success. |
| IR-4 Fix generalization | n/a | First execution-review round; no preceding execution correction. | null | Both runtime query implementations were nevertheless inspected; F1 covers ONNX and torch. |
| IR-5 Test rigor audit | pass | Inspect all changed test/fixture diffs, new adapter file, existing tests touched by TA-1–TA-6 and geometry setup/helper. | null | Strong/Adequate ratings above; immutable existing assertions; missing query-failure case is F1/IR-3. |
| IR-6 Boundary validation | pass | Inspect ModelLoadIn/ApiModel and API/UI negative and payload assertions. | null | Device enum/default/extra-forbid remain; tpu returns 422; response devices has a required literal enum. |
| IR-7 Deferral and AC integrity | pass | Compare both handoff AC tables, plan AC tables, all Files tables and actual diff/status. | null | All twenty owned ACs traced; cross-family rows present; no orphan deferral. AC-87 references are explicitly Session-37 n/a. |
| E2 Geometry | pass | Inspect Electron AC-79.7–.10, default-window creation, bound primitive classes and full/repeat receipts. | null | Action present; ±0.5 px; exact list transition; row/slider constraints; no loosened D-20 check. |
| E3 / AV-1–AV-4 Test integrity | pass | Compare baseline test hunks and inspect Red/Green receipts with .exit files. | null | Approved amendments only; required Red assertions; no added masking/retries. |
| E4 Evidence freshness | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --state-only` | 0 | Exact match: `6097cf59adc7835fa6062c8bd3d55c679aef4543+039931efaad0f7994c8995f8ddc6593ce4821f10d25c3c0ee800aa5e1fa15758`. |
| E5 / AV-5–AV-6 Scope and completion claims | pass | Inspect status/diffs, hub updates and source labels; compare pending H1-7/H2 rows. | null | Product scope obeyed; no new placeholders; source-backed rules; H2 correctly pending, no overall DONE claim. |
| A-1 and Python baseline | pass | Compare gate predicates with Verification Plan §1, AC-41.3 source and baseline/H1-2 diagnostics. | null | One unrelated UI ID and the same two packaging IDs only; full commands and observed counts support acceptance. |
| Red checker selftest | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/red-check.py --selftest` | 0 | 35 fixtures, 0 wrong. |
| Identity selftest | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --selftest` | 0 | 0 failures, bound changes detected and closeout exclusions stable. |

```json
{"schema_version":"evidence.v1","check_id":"s35-review-runtime-enumeration","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-review-probe.py","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"Real adapter and production load/catalog HTTP handlers with failing runtime availability queries; fake model/session factories; no project suite","phase":"targeted","exit_code":0,"result":"fail","tested_state":"6097cf59adc7835fa6062c8bd3d55c679aef4543+039931efaad0f7994c8995f8ddc6593ce4821f10d25c3c0ee800aa5e1fa15758","output":"prior_load True cuda; ONNX CPU load raises RuntimeError, is_ModelLoadError=false, session_calls=[], events=[], loaded=false, device=cpu; POST /api/v1/models/load 500 internal_error; GET /api/v1/models/available 500 internal_error; PyTorch CPU load RuntimeError is_ModelLoadError False","fresh":true}
```

The template's source-label/validation-cell/BUILD_PLAN/post-MEU rows are supported by the plan and task reads; its naming/frontmatter/evidence/FAIL_TO_PASS checks were observed. No standalone formatting, ceremony or hypothetical harness finding is raised.

## Verdict

**changes_required** — intent **partial**. One High, High-confidence blocking behavioral finding, F1, violates AC-75 (AC-75.9 and the load-error boundary). No Critical finding. The substantive layout and normal fallback implementation are sound; the reproduced runtime-probe failure prevents approval.

Follow-up: correct F1 through the implementing agent's `/execution-corrections` phase, add a regression that fails on this tree, run affected behavior checks and a fresh full gate after corrections, refresh both handoffs' tested_state/evidence, and request execution ledger round 2 within the existing cap of 6. Preserve this finding ID. The reviewer made no correction or repository write. Orchestrator: copy this report to `.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md` and record the matching structured verdict; do not proceed through the approval gate until the blocker is resolved.

Residual limits: the review uses recorded full-suite/Electron evidence and permitted synthetic engine probes; it does not claim fresh suite execution, physical GPU loading or a new visual measurement. Those limits do not affect the deterministic F1 reproduction.

---

## Corrections Applied — 2026-10-17 (round 1 → round 2 request)

Implementer: claude-code, `/execution-corrections` inside the authorized execution loop. This section is the implementer's account. It does not change the reviewer's text above, and it does not approve anything: the verdict is `corrections_applied`, and only the round 2 independent review may set `approved`.

### F1 — runtime availability query bypasses AC-75.9 (preserved ID)

**Plan.** A runtime query that raises is read as that device being unavailable, which is the case DEVICE_RESOLVE already handles: the device is not listed, a request for it falls back to CPU with the reason logged, and the catalog and a CPU load keep working. Every other statement in `load_model` that could escape as a bare exception gets the same `ModelLoadError` wrapping, which is what `03-service-layer.md:469` asks for. Recorded as MEU-75 handoff D-21 and in the plan's §Execution Correction Notes.

**Changes** (`packages/infrastructure/src/avkit_infra/tts/adapter.py`, now +171/−43 against 6097cf5):
- `runtime_devices` makes each runtime query through `_query`: ONNX `get_available_providers`, `torch.cuda.is_available` and `torch.backends.mps.is_available`. A query that raises returns absent and logs one `tts.device_probe_failed` warning (`format`, `device`, `error` = the exception type name). `auto` and `cpu` are always listed.
- `load_model` wraps `_resolve` (the injected probe). A raise logs `tts.load_failed` and raises `ModelLoadError("TTS device probe failed")` from the cause.
- `_load_pytorch` resolves the vocab inside the existing load guard.
- `_require_weight_path` turns an `OSError` from `is_file` (for example `PermissionError` from `stat`) into `ModelLoadError("model weight file is unreadable")`, with no path in the message.

**Regressions** (`tests/integration/test_tts_device_resolution.py`; all five written first and seen failing on the reviewed tree):

| Test | Red on the round 1 tree |
|---|---|
| `:563` `test_ac_75_9_failing_runtime_query_lists_no_such_device_neg` | `RuntimeError: provider enumeration failed` |
| `:588` `test_ac_75_9_failing_runtime_query_still_loads_on_cpu` | `RuntimeError: provider enumeration failed` (CPU load after a CUDA load, the F1 scenario) |
| `:616` `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg` | `RuntimeError: probe failed` (not `ModelLoadError`) |
| `:657` `test_ac_75_9_unreadable_weight_file_is_model_load_error_neg` | `PermissionError: access denied` |
| `:681` `test_ac_75_9_failing_runtime_query_http_catalog_and_load` | `assert 500 == 200` (`internal_error`) |

**Verification.**

| Check | Exit | Decisive output | Receipt |
|---|---|---|---|
| Red (4 tests) | 1 | `4 failed, 1 passed, 17 deselected` | `C:/Temp/av-kit/s35-f1-red-py.txt` |
| Red (weight-file `stat`) | 1 | `1 failed, 1 passed, 21 deselected` | `C:/Temp/av-kit/s35-f1-red2-py.txt` |
| Green: `test_tts_device_resolution`, `test_tts_no_torch`, `test_tts_models`, `e2e/test_api_tts_models`, `e2e/test_api_error_surface` (unfiltered) | 0 | `60 passed, 1 warning` | `C:/Temp/av-kit/s35-f1-green-py.txt` |
| `ruff check packages/ tests/`, `ruff format --check` (2 files), `pyright packages/` | 0 | `All checks passed!`, clean, `0 errors` | — |
| Fresh full gate (task.md H1-2, verbatim) | 0 | `session-gate: all steps exit 0`; `tested_state 6097cf59…4543+c7e4a6b9…32e3`; `changed paths: 39 outside scope: []`; py-tests and ui-tests `outside_baseline=[]`; Electron 161 passed; e2e-repeat 50 passed | `C:/Temp/av-kit/s35-gate-h1/` (round 1 receipts kept in `s35-gate-h1-r1/`; attempt 1, failed only on the known W2-5 timeout, kept in `s35-gate-h1-r2fail/`, walkthrough A-2; attempt 2, failed only on the capture-picker clock race, kept in `s35-gate-h1-r2fail2/`, fixed under A-3 on Mat's ruling) |

**Gate amendment A-3** (Mat's ruling, 2026-10-17). Post-correction attempt 2 failed only at `ui-tests` on `capture-picker.test.ts` AC-40.6, a clock-second race (the taken name and the publication fell in different seconds; unchanged since 6097cf5; 5/5 alone). The sibling `capture-lifecycle.test.ts` AC-40.30 (a) has the same race. Both tests now pin `Date` for their own body; no assertion changed. Red: `s35-a3-red-ui.txt` (a forced one-second step reproduces the gate message, 2 failed). Green: `s35-a3-green-ui.txt` (55 passed, three runs). `session-gate.ps1` `scope-paths` allows the two files. See `walkthrough.md` §A-2 and §A-3 and the plan's §Execution Correction Notes.

Both handoffs were regenerated from the re-run: the new `tested_state` and the full `evidence.v1` gate record, then H1-6, H1-6a and H1-6b re-run (all exit 0; `identity.py --state-only` re-derives the gate's `tested_state`). The MEU-75 handoff also gains the F1 FAIL_TO_PASS rows, Red and Green records, D-21 and a History row. On the first re-run, H1-6 refused the F1 Red record (`exit_code contradicts result`: a raw pytest exit 1 was written as `pass`), so it now reads `result: fail`. The plan's correction notes now cite AC-40 (A-3) and AC-41 (A-1), so each AC table gains an `n/a` cross-reference row for them, like the AC-87 row (`all 9 plan AC(s) present`, 19 AC rows).

**Sibling sweep.** In `load_model`, the injected probe, the vocab resolver and the weight-file `stat` were the only statements outside a guard; all three are covered above. `ValidationError` was already a mapped domain error.

**Cross-doc sweep.** 13 files reference the device probe (`rg -l -i "runtime_devices|DEVICE_PROBE|device_probe"` over packages, tests, build plan, execution docs and handoffs), and 3 were updated: the plan (§Execution Correction Notes), `walkthrough.md` (§Execution review R1) and the MEU-75 handoff. The `03-service-layer.md:472` delivered note ("`cuda` from `torch.cuda.is_available()`…") and the `TTSPort.available_devices` docstring still describe the behavior correctly, so neither was edited.

**Requested.** Execution ledger round 2, within the existing cap of 6. Please re-check F1 under its ID, and check that the fix covers the whole failure class, not just the reproduced path.

---

## Round 2 review — 2026-10-17 (Codex, verbatim below this line)

## Recheck (2026-10-17)

**Execution ledger round 2 of 6. Verdict: changes_required. F1 is fixed; F2 is one open High blocker. No Critical finding.**

**Intent anchor:** Session 35 delivers MEU-75 (the TTS device list comes from the runtime, an unavailable or failing device falls back to CPU with a logged reason, the model status reports the device actually used, and a failed load returns its reason as a 422) and MEU-79 (the Voice panel lists only the selected model's devices and lays out Model, Device, the model action, Speed and Format at one control height on aligned rows, pinned by Electron geometry at the default window).

The runtime-query correction and the Voice panel achieve their intended behavior. A terminal failure during the lazy PyTorch engine import still bypasses the promised load-error response, so the overall intent remains partial.

## Scope

Reviewed worktree P:/av-kit-wt/s35-tts-voice-panel, branch claude/s35-tts-voice-panel, against baseline 6097cf59adc7835fa6062c8bd3d55c679aef4543. The change set is the baseline diff plus the six untracked paths in git status. HEAD and baseline.sha agree. The dispatcher checkout is a different checkout; its only review-data read was the explicitly named P:/av-kit/.agent/context/review-vocabulary.yaml.

The project-integrated handoff set was read in dependency order:

1. .agent/context/handoffs/2026-10-16-tts-voice-panel-MEU-75-handoff.md
2. .agent/context/handoffs/2026-10-16-tts-voice-panel-MEU-79-handoff.md

Also reviewed the entire correlated plan folder docs/execution/plans/2026-10-16-tts-voice-panel/: implementation-plan.md, task.md, walkthrough.md, session-gate.ps1, identity.py, red-check.py and baseline.sha; the round 1 report and appended Corrections Applied section; actual product/test diffs and the new adapter test; hub/SSOT changes; and the supplied Session 35 receipts. REVIEW-TEMPLATE.md v2.2 supplied this report's structure. H2 reflection/metrics remain later work behind H1-7; this review does not claim session closeout.

Author: Claude Code / Anthropic. Independent reviewer: Codex gpt-6.1-sol. No repository file was written. Report and scratch probe/audit files are confined to C:/Temp/av-kit/dispatch. Reviewed text was treated as data, and no secret/cookie/credential file was read. Probe auth uses a literal, isolated fixture token.

**Verification boundary:** static source/diff/receipt review, the three expressly permitted plan verifiers, and short Python probes using stdlib transport/import interception with production application imports and fake engines. No pytest, Vitest, Playwright, build, npm, uv sync, gate, generator, project validator or MCP audit was executed by this reviewer. All suite results below are observed author receipts.

## Findings

| # | Severity | Blocking | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|
| F2 | High | yes | AC-75.9 remains incomplete for a terminal PyTorch dependency-import failure. _load_pytorch catches only ImportError around the lazy kokoro.KModel import; an OSError raised while initializing that dependency escapes as a bare exception. The independent probe reproduces POST /models/load returning masked 500 internal_error instead of the promised 422 ModelLoadError reason. Device resolution succeeds and the adapter is correctly unloaded, so this is a separate terminal engine-initialization failure from F1's repaired, recoverable availability-query failure. | packages/infrastructure/src/avkit_infra/tts/adapter.py:284-288 | Include lazy engine import/initialization in the terminal load-error guard, preserve the original cause and a path-free ModelLoadError message, and log tts.load_failed. Add a Red-first adapter/HTTP regression for a non-ImportError import failure, then rerun affected checks and the fresh full gate and refresh both handoffs. | open |
| F1 | High | no | Fixed in round 2: AC-75.9 runtime availability-query failures now omit only the failing device, log tts.device_probe_failed, and keep CPU catalog/load paths usable. The guarded resolve, vocab resolver and weight-file access also preserve ModelLoadError causes. The refreshed independent probe passes the original ONNX/torch cases and the catalog/load/status HTTP checks. | packages/infrastructure/src/avkit_infra/tts/adapter.py:72-110,133-141,248-253,291 | Retain the five added regression tests and the post-correction evidence; no further correction is needed for F1. | fixed |

Both findings have confidence High, subject deliverable, finding_kind behavior and violates AC-75 (full criterion AC-75.9). No control-defeat mechanism is asserted. F1 retains its original severity as history, with blocking no because it is fixed.

### F2 evidence and materiality

The import at adapter.py:286 is outside the broad guard beginning at :290; its own handler at :287 handles only ImportError. Python module initialization can raise other exceptions. This is a load-time operation: the adapter imports torch at module initialization but imports kokoro.KModel only when a PyTorch load is requested. The installed kokoro/__init__.py:22-23 imports its model and pipeline, rather than supplying a preconstructed inert class.

The independent scratch probe substitutes a loader failure only for the kokoro import, raising OSError("engine dependency DLL initialization failed"). All model/device arguments are valid; the availability probe succeeds. Production adapter and ASGI error handling are used. This is a simulated dependency failure, not a claim that this host currently has a broken DLL.

Command (cwd is the worktree; PYTHONDONTWRITEBYTECODE=1; ELECTRON_RUN_AS_NODE unset):

~~~text
rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-r2-import-probe.py
process exit 0
prior_load True cuda
lazy_import {"exception": "OSError", "is_ModelLoadError": false, "message": "engine dependency DLL initialization failed", "events": [], "loaded": false, "device": "cpu"}
HTTP POST /api/v1/models/load 500 {"error":{"code":"internal_error","message":"Internal server error","details":{"request_id":"7f9a4f3a-4393-45f0-89f0-2ce3145b59c4"}}}
~~~

Exit 0 means this diagnostic probe completed; its product observation fails AC-75.9. The generic API backstop behaves correctly; the adapter must classify the terminal engine failure first. Related locations: routes/models.py:102-103 and errors.py:131-159. The missing regression is visible in test_tts_device_resolution.py:119-121: its fixture installs an already initialized kokoro module, so constructor/move/eval tests cannot exercise lazy import failure.

This meets the protocol's materiality gate: a valid CPU load request returns the wrong HTTP error and loses its reason, contrary to the plan's load_model boundary ("raises ModelLoadError only"), LOAD_ERROR_HTTP, and docs/build-plan/03-service-layer.md:469 ("never a bare exception"). This is a distinct terminal engine-initialization stage with successful device resolution; it cannot be repaired by treating an accelerator as absent, which fixes F1. It is not another encoding, delimiter or filesystem-race variant of the repaired availability query, and it does not reopen F1 or change an approved plan decision.

## R1–R3 Recheck

### R1 — F1 fixed

Actual source, not the change log, establishes the correction:

- runtime_devices at adapter.py:72 and _query at :99 independently guard ONNX enumeration and torch CUDA/MPS availability calls. A raising query omits that device, logs format/device/exception type, and leaves Auto/CPU.
- load_model:246 retains the initial unload. The resolve call at :249 is guarded and raises ModelLoadError from an injected-probe exception.
- _load_pytorch:291 resolves the vocab inside the terminal load guard.
- _require_weight_path:135-138 turns an OSError from weight-file access into ModelLoadError with its original cause and no path in the public message.

Re-ran C:/Temp/av-kit/dispatch/s35-review-probe.py after adjusting its round 1 diagnostic expectations to the corrected behavior. It now asserts successful CPU use and checks production HTTP output. Decisive final output, process exit 0:

~~~text
prior_load True cuda
onnx_cpu_load PASS {"session_calls": [["CPUExecutionProvider"]], "events": ["tts.device_probe_failed", "tts.load_model"], "loaded": true, "device": "cpu"}
onnx_catalog_probe PASS ['Auto', 'CPU']
HTTP POST /api/v1/models/load 200 ... "device":"cpu" ... "is_loaded":true
HTTP POST /api/v1/models/load 200 ... "device":"cpu" ... "is_loaded":true
HTTP POST /api/v1/models/load 200 ... "device":"cpu" ... "is_loaded":true
HTTP GET /api/v1/models/available 200 ... "devices":["auto","cpu"]
HTTP GET /api/v1/models/status 200 ... "device":"cpu"
pytorch_raising_queries PASS cpu; 2 probe warnings; fallback unavailable
injected_probe PASS ModelLoadError cause RuntimeError; unloaded cpu
HTTP POST /api/v1/models/load 422 {"error":{"code":"ModelLoadError","message":"TTS device probe failed","details":null}}
vocab_resolver PASS ModelLoadError cause PermissionError; unloaded cpu
weight_stat PASS ModelLoadError cause PermissionError; unloaded cpu
round2 probe: all assertions passed
~~~

The three ONNX POSTs request cpu, cuda and auto respectively. The torch case makes both CUDA and MPS queries raise. Probe/vocab/weight terminal failures leave the adapter unloaded on cpu.

### R2 — Generalization is incomplete only at F2

**The raising-query policy is correct.** The build plan requires runtime-detected devices and CPU fallback for a device the runtime cannot use. An unsuccessful availability query cannot establish availability. Omitting that device, with tts.device_probe_failed and the explicit-request fallback reason unavailable, preserves usable CPU loading and the catalog. Failing every catalog/CPU request instead would reproduce F1. This is consistent with DEVICE_PROBE, DEVICE_RESOLVE, LOAD_ERROR_HTTP and the source Errors rule; the correction is recorded in D-21.

The five new tests at test_tts_device_resolution.py:563, :588, :616, :657 and :681 make specific assertions about device membership, logs, engine calls, causes, clean state and HTTP values. Their Red receipts establish failure before the fix:

| New test | Observed Red |
|---|---|
| :563 query matrix | RuntimeError: provider enumeration failed |
| :588 usable CPU load after CUDA | RuntimeError: provider enumeration failed |
| :616 injected probe/vocab | RuntimeError: probe failed |
| :657 unreadable weight | PermissionError: access denied |
| :681 catalog/load HTTP | 500 versus expected 200; internal_error envelope |

s35-f1-red-py.exit and s35-f1-red2-py.exit each contain 1. Summaries are 4 failed, 1 passed, 17 deselected and 1 failed, 1 passed, 21 deselected. The combined :616 test stops first at the probe failure in Red; source inspection and the independent probe additionally verify its vocab subcase. The Green receipt is 60 passed, 1 warning, and s35-f1-green-py.exit is 0. Thus these are real failing regressions, not tests made green by unrelated setup repair.

The default production catalog uses runtime_devices, so its failing runtime queries are now contained. available_devices intentionally forwards an injected port probe; malformed custom collaborators are not a new external-input contract. Missing torch and a kokoro ImportError already produce ModelLoadError. Successful resolution, construction/move/eval failure handling, ONNX provider fallback and state clearing remain correct. The separate lazy import's non-ImportError failure is F2; the claim that every remaining load statement is guarded is therefore too broad. No new stale-model state defect was found.

### R3 — Evidence current; correction scope contained

Independently derived current state:

~~~text
6097cf59adc7835fa6062c8bd3d55c679aef4543+c7e4a6b9a982862a5f8cfea2ce1d0dc9ee0e71462917bf0ca945f60fb35a32e3
~~~

This equals BOTH handoffs' full evidence.v1 tested_state and the post-correction H1-2 gate's before/after states. Both handoffs carry attempt 3, including the F1 correction and A-3. Neither substitutes the older row-6 or round-1 state.

Compared the captured round 1 product/test/hub diffs with live baseline diffs. All 25 corresponding Git old..new blob-ID pairs remain identical. The gate's only substantive addition since round 1 is the two A-3 allowlist paths. Compared the old numbered adapter source and untracked test with current source: the adapter correction is the query/resolve/vocab/weight handling above; the test adds the five regressions, leaving the prior assertions intact. The old adapter read stops at line 355; the complete baseline adapter diffs independently show no synthesis-tail edit.

Current status is 33 modified tracked paths plus six untracked paths (39 total); baseline diff stat is 817 insertions and 139 deletions in 33 tracked files. Changes beyond the adapter/new test and A-3's two tests plus allowlist are plan/closeout administration, including the excluded known-issues.yaml note documenting W2-5. No other product implementation, shared fixture or existing assertion changed after round 1.

## Commands Executed and Evidence

Every shell process used rtk proxy, an absolute worktree cwd, all-stream redirection to a Session-35-prefixed receipt under C:/Temp/av-kit/dispatch, immediate LASTEXITCODE capture, completed receipt readback and exit propagation. Python verifiers/probes used the worktree .venv/Scripts/python.exe with PYTHONDONTWRITEBYTECODE=1; the identity run also cleared ELECTRON_RUN_AS_NODE and set RECEIPTS_DIR.

### Executable checks performed by this reviewer

| Command | Exit | Decisive result |
|---|---|---|
| rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/red-check.py --selftest | 0 | 35 fixtures: 11 positive, 24 negative; 0 wrong |
| rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --selftest | 0 | 0 failures; 16 bound paths plus untracked/runtime mutations change state; nine closeout outputs leave it unchanged |
| rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --state-only | 0 | Exact +c7e4a6b9…32e3 state above |
| rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-review-probe.py | 0 | Refreshed F1 probe: all assertions passed |
| rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-r2-import-probe.py | 0 | F2 observation: bare OSError; HTTP load 500 internal_error |
| rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-r2-static-audit.py | 0 | Read-only comparison of captured diffs/blob IDs and source; 25 unchanged captured paths; gate adds A-3 paths |

Static command inventory: rtk proxy git status --short; git log -1 --format='%H %D %s'; git diff 6097cf5 --stat; git diff 6097cf5 -- packages/infrastructure/src/avkit_infra/tts/adapter.py; baseline diffs over the remaining product/OpenAPI, tests/ui-tests, hub, known-issue and gate paths. All these git commands used rtk proxy. Read-only Get-Content/numbered source views inspected the required protocol/context/plan/handoff/template/schema/vocabulary, changed files, collaborators, main-window/Playwright setup and queue-canon inputs. Get-ChildItem inventoried only named s35 receipt files/snapshot or closeout directories. Get-FileHash -Algorithm SHA256 captured the receipt hashes below. The scratch audit invokes only allowed git diff/status reads and stdlib text comparison, not project validation.

Reviewer scaffolding corrections: a numbered-read command initially had a PowerShell quoting error and was corrected; the refreshed probe initially assumed a data wrapper, then was corrected to the actual flat response/items shapes; a scratch audit's first diagnostic print hit cp1252 encoding and was corrected to UTF-8. None is used as product failure evidence. The final probe/audit results above are the completed runs. An initial adjacent-exit lookup used .txt.exit; directory inspection located the actual .exit names, whose contents were then read. No finding is raised about these scratch details.

### Observed author evidence after correction

| Evidence | Observation |
|---|---|
| F1 Red / Green | 4 failed then 1 failed on the reviewed adapter; after correction, 60 passed |
| A-2 attempt 1 | ui-electron 1 failed, 160 passed: transcript W2-5 180000ms timeout plus teardown error; later stages not_run. W2-5 alone: 4 passed in 13.8s |
| A-3 attempt 2 | ui-tests 2 failed, 979 passed: baseline AC-41.3 plus capture-picker AC-40.6 second-boundary miss; baseline rule refused the new ID |
| A-3 Red / Green | Forced one-second clock step: two collision assertions fail; unfiltered two files after pin: 55 passed each in three runs |
| H1-2 attempt 3 | Static stages exit 0; scope 39 paths, outside scope []; raw pytest exit 1 accepted only for two packaging baseline IDs, 934 passed; raw UI exit 1 accepted only for AC-41.3, 980 passed; MCP 428 passed; build/OpenAPI/render stages exit 0; Electron 161 passed; repeat 50 passed; identity before == after; gate exits 0 |
| H1-6/6a/6b | Both handoffs: 19 AC rows, nine referenced families covered, durable evidence present; both full-state checks OK |
| H1-4 | added: []; removed: []; changed: ['ModelVariantOut'] |

The gate receipt is fresh and the recorded passing counts are honest. It does not exercise F2's missing import-failure negative case.

### SHA-256 receipt bindings

Paths below are relative to C:/Temp/av-kit/.

| Receipt | SHA-256 |
|---|---|
| s35-gate-h1/s35-gate-h1.txt | 071E288D7034128A0EC4677D06218FCB0170D7D7BA71716652805D9BA6D2BB93 |
| s35-gate-h1/s35-D6-py-tests.txt | 463E7E5A374E239FD34274D27872FEA75956960E0C5A5B688F5EDC0B4617C989 |
| s35-gate-h1/s35-D6-ui-tests.txt | 555203FC0D1BEC9EC5C8841FC0A5F3610A14EDC211C2C09B2160326C4CA0A78F |
| s35-gate-h1/s35-D6-ui-electron.txt | 542CFDEAA6D24FCF1C399C6E9FF14786A6AC7422FE3326742336587E5C70D772 |
| s35-gate-h1/s35-D6-e2e-repeat.txt | 622BC5B482FB8E66A7865E9A57B1AABDFA542B55603B7EE278E18CA5B1177A51 |
| s35-f1-red-py.txt | AFD613FDB47F6A1E9F3BA95EC9FAC3060DEF2A5D94D9B753F1A7B01302A76CBE |
| s35-f1-red2-py.txt | 4685005D9EF67386ED02E3586123B7BFD43EF65FC8895AD2BC1119B85E7AB5C5 |
| s35-f1-green-py.txt | 4C1E07975213AFC07B9DEB9E32948FB8ED689D8A8F8CF96955ED6BBACC043F6E |
| s35-a3-red-ui.txt | 32FFA97EEB4F6B2B4768FBA56B1C3158DE26094726C45106E23F1198B678D1F6 |
| s35-a3-green-ui.txt | 2AE9C4C0D3FC463ABF20043E47B1D8FCB0FD0F220D130B83C42C00FB7F4CE8E2 |
| dispatch/s35-r2-probe.txt | 9B1FC4F99C24D57B75D7C45D297E9FA95882408D403739F66F723E043C0A01D8 |
| dispatch/s35-r2-import-probe.txt | E8B2725BCDE32D00D7D57A340ED4A5BF20EBD87AF3CECD6B6B620A7DBD55DD6B |

## Acceptance-Criteria Trace

All paths are worktree-relative. A pass means source and meaningful assertions deliver the criterion, supported by matching recorded execution; it does not claim a reviewer suite rerun.

| AC | Product file:line | Test file:line that would fail without it | Status |
|---|---|---|---|
| AC-75.1 | packages/infrastructure/src/avkit_infra/tts/adapter.py:25,72,85 | tests/integration/test_tts_device_resolution.py:187; tests/integration/test_tts_no_torch.py:150 | pass |
| AC-75.2 | packages/infrastructure/src/avkit_infra/tts/adapter.py:81 | tests/integration/test_tts_device_resolution.py:210 | pass |
| AC-75.3 | packages/infrastructure/src/avkit_infra/tts/adapter.py:268,113 | tests/integration/test_tts_device_resolution.py:231,255 | pass |
| AC-75.4 | packages/infrastructure/src/avkit_infra/tts/adapter.py:281,299,308 | tests/integration/test_tts_device_resolution.py:309,330,357,377 | pass |
| AC-75.5 | packages/infrastructure/src/avkit_infra/tts/adapter.py:313 | tests/integration/test_tts_device_resolution.py:398,420,443,463,486 | pass |
| AC-75.6 | packages/infrastructure/src/avkit_infra/tts/adapter.py:271 | tests/integration/test_tts_device_resolution.py:275,294 | pass |
| AC-75.7 | packages/core/src/avkit_core/ports/tts.py:41; packages/core/src/avkit_core/services/models.py:105; packages/infrastructure/src/avkit_infra/tts/adapter.py:232 | tests/integration/test_tts_device_resolution.py:500; tests/unit/test_services.py:2201; tests/unit/test_domain.py:1154 | pass |
| AC-75.8 | packages/api/src/avkit_api/schemas/models.py:48; packages/api/src/avkit_api/routes/models.py:42,56,67,94; openapi.committed.json:1886 | tests/e2e/test_api_tts_models.py:199,206,215 | pass |
| AC-75.9 | packages/api/src/avkit_api/errors.py:36,131; packages/api/src/avkit_api/routes/models.py:99; packages/infrastructure/src/avkit_infra/tts/adapter.py:248,284 | tests/e2e/test_api_error_surface.py:274,282; tests/integration/test_tts_device_resolution.py:520,563,588,616,657,681. Missing lazy-import failure regression is F2 | fail — F2; F1 fixed |
| AC-75.10 | packages/infrastructure/src/avkit_infra/tts/adapter.py:72 | tests/integration/test_tts_device_resolution.py:722 | pass |
| AC-79.1 | ui/src/renderer/src/features/tts/TTSPage.tsx:263,266,474 | ui/tests/unit/tts-page.behavior.test.ts:727 | pass |
| AC-79.2 | ui/src/renderer/src/features/tts/TTSPage.tsx:267,475,480,495 | ui/tests/unit/tts-page.behavior.test.ts:737 | pass |
| AC-79.3 | ui/src/renderer/src/features/tts/TTSPage.tsx:266; ui/src/renderer/src/features/tts/useTtsJob.ts:58 | ui/tests/unit/tts-page.behavior.test.ts:754 | pass |
| AC-79.4 | ui/src/renderer/src/features/tts/TTSPage.tsx:196,202 | ui/tests/unit/tts-page.behavior.test.ts:761 | pass (characterization) |
| AC-79.5 | ui/src/renderer/src/components/ui/SegmentedControl.tsx:19,22,26,36 | ui/tests/unit/layout-primitives.test.ts:306 | pass |
| AC-79.6 | ui/src/renderer/src/features/tts/TTSPage.tsx:452,487,585,591,603,616 | ui/tests/unit/tts-page.behavior.test.ts:782 | pass |
| AC-79.7 | ui/src/renderer/src/features/tts/TTSPage.tsx:452; ui/src/renderer/src/components/ui/SelectInput.tsx:25; ui/src/renderer/src/components/ui/Button.tsx:24 | ui/tests/e2e/tts-generate.test.ts:762 | pass |
| AC-79.8 | ui/src/renderer/src/features/tts/TTSPage.tsx:573,585,591,603,616; ui/src/renderer/src/components/ui/SegmentedControl.tsx:36 | ui/tests/e2e/tts-generate.test.ts:781 | pass |
| AC-79.9 | ui/src/renderer/src/features/tts/TTSPage.tsx:452,585,616 | ui/tests/e2e/tts-generate.test.ts:807,602 (AC-64.6) | pass |
| AC-79.10 | ui/src/renderer/src/features/tts/TTSPage.tsx:263,266,474 | ui/tests/e2e/tts-generate.test.ts:836 | pass |

## E1–E5 and Gate Answers

### E1 — Delivery

Device ordering is Auto, CUDA, CPU, MPS filtered by format/runtime; MPS is PyTorch-only. Missing torch reports Auto/CPU. Runtime query failures now preserve healthy devices and usable CPU behavior. Auto prefers CUDA, then MPS, then CPU without a fallback warning. Unavailable explicit requests use CPU and log reason unavailable.

Initial unload and temporary model/session locals are retained. PyTorch retries a non-CPU .to failure once on CPU; constructor and .eval failures are final and wrapped, with causes and clean CPU/unloaded state. The prompt's .to/.eval retry shorthand does not override the approved contract: .eval is explicitly final. ONNX retries a CUDA constructor or session.get_providers failure on CPU, reports CPU for a session that silently drops CUDA, and never queries providers on the CPU path. Tests assert calls, actual devices, logs and state after an earlier successful CUDA load. No stale or partial state was found.

The port/service forwards available_devices, all list rows and download variants populate the required enum-valued devices field, and the OpenAPI diff is limited to that field and its required entry. UI options follow the selected row, Load posts effectiveDevice, and only user change persists device. SEGMENT_SIZE preserves the default/sm class and child markup byte-for-byte; md adds only h-9. F2 is the remaining terminal error-classification gap.

### E2 — Geometry oracles

The unchanged launch helper gives each Electron instance fresh AVKIT_APP_DATA. createWindowOptions at ui/src/main/index.ts:140 therefore supplies the default 1280×800 window. openVoicePanel waits for the voice request, loaded ONNX selection and the actual unload-btn, then two animation frames.

AC-79.7 measures Model, Device, the real action and associated label tops. AC-79.8 measures the actual combobox, Format, slider and preset inner div. AC-79.9 measures the model row and slider grandparent, rejects null/missing measurements and overflow, and enforces the 96 px slider floor. The full and repeat receipts include AC-64.6. AC-79.10 checks exact option values before and after selecting the PyTorch row.

D-20's helper maps only deltas within inclusive ±0.5 px to zero; an outside delta or NaN fails toEqual. No tolerance was widened. A measured misalignment beyond 0.5 px fails. Height comparisons alone are relative, so a hypothetical uniform wrong height for every control could pass those comparisons; unchanged SelectInput h-9, unit-pinned h-9 action/slider and exact md primitive class anchor this delivered tree to 36 px. This accepted oracle limitation is unchanged from round 1, and no such wrong-height layout is present.

### E3 — Test integrity and A-3

All changed Python/UI fixture/test diffs and every new adapter test were inspected. Existing assertions are preserved.

TA-1 scopes a CUDA availability patch to the existing explicit-CUDA load and retains its status/call assertions. TA-2 adds the new facade method; TA-3 extends the exact protocol set; TA-4 adds the port fake's method and call recording; TA-5 requires no fixture edit because existing selections use Auto/CPU; TA-6 adds format-specific devices to the existing Electron seam. These are consequences of approved contracts. No added skip/only/xfail, assertion bypass, retry or timeout padding was found. The old subprocess timeout convention is unchanged.

A-3 is test-only and complete for the demonstrated collision-test race: capture-picker.test.ts:248-249 and capture-lifecycle.test.ts:407-408 fake only Date and pin the same second for fixture naming/publication. Real timers, promises and setImmediate remain active. The _2/_3 and preservation assertions are unchanged. Picker afterEach:91 restores timers; lifecycle already does so at :114. The only gate change for A-3 is its two scope paths. The Red receipt forces a one-second step and reproduces both misses; the Green receipt runs both full files three times at 55 passes. No capture product file changed.

IR-5 grades: new adapter matrix/resolution/fallback/cause/state/HTTP/live-runtime tests, no-torch subprocess, service/API schema/envelope tests, UI device/error tests, primitive byte characterization, Electron geometry/device-switch tests and the two preserved capture collision assertions are Strong. DOM-class AC-79.6 is Adequate for its class contract and backed by Strong geometry assertions. TA fixtures retain their real call/value semantics. No changed assertion is vacuous. F2 is an omitted negative path, not a weakened assertion.

### E4 — Evidence honesty

Both handoffs now contain the post-correction H1-2 full record at the exact independently derived live identity. F1's Red/Green, the new gate totals, task evidence references, A-2 fail-fast stop, A-3 correction and closeout checks agree with the inspected receipts. H1-7 and H2 remain pending. Historical raw pytest/UI exits of 1 are disclosed as baseline-accepted failures, not raw suite success.

The handoff's universal claim that nothing else escapes bare is refuted by F2; this is the same product defect, not a separate documentation finding. Matching gate evidence remains valid evidence of what was exercised, but cannot prove an absent negative case.

### E5 — Scope and hubs

All changed paths are in the Files tables, plan-local/session-administrative scope, or the explicitly authorized A-3 test extension. The post-round-1 additions are contained as described under R3. The excluded known-issue update documents the real W2-5 recurrence; no unrelated product change is hidden there.

OpenAPI changes only ModelVariantOut.properties.devices and devices in required. Matrix rows 3.8 and 11.13 have the planned dependencies/names. The 11 layout/device/geometry section describes delivered behavior. The 03 Delivered note is accurate for probe/resolution/fallback, but its general load-error promise still has the F2 exception. SSOT and rendered BUILD_PLAN correctly remain ready_for_review, with truthful phase notes; no approval has been self-authored.

### A-1 / D-19 — UI baseline rule

A-1 applies the approved Verification Plan §1 rule to a previously uncovered suite. That rule says baseline failures are listed and not counted as regressions; it is not limited to Python. It changes neither tests nor product assertions and is included in the matching tested_state.

The code accepts only raw exit 1, a nonempty FAIL-ID set contained in the one expected AC-41.3 ID observed in row 0, a matching failed count and no unhandled/error-summary diagnostic. No FAIL or no summary rejects acceptance. An additional failed test without a FAIL header makes counts disagree; another layout-canon/queue-canon ID is outside the allowed set. A non-1 crash exit is never normalized. Attempt 2's capture-picker failure demonstrates actual rejection of a new ID.

The gate invokes the full npm test command without a filter; package/config diffs contain no filtering change. The predicate alone cannot authenticate a fabricated/filtered receipt, but the inspected run is 96 files/981 tests and shows the expected full invocation. No concrete Session 35 regression false-passes.

AC-41.3 at queue-canon.test.ts:159 reads Zorivest globals.css and av-kit's unchanged styles.css/status-token inputs; it does not read the hub/SSOT docs other canon tests use. No Session 35 change reaches those token inputs. Baseline and final receipt fail at exactly the same light-pending token: expected #ea580c, received #9a3412. Thus this exception does not hide a Session 35 change to that test's inputs in this tree.

### Python baseline

The py-tests baseline predicate is unchanged from the approved gate. Both row 0 and final H1-2 show only test_pack_dist_onedir_layout[AC-24.10] and test_nsis_pack_check_script[AC-25.10]. Final diagnostics are missing PACK_DIST_EXE and missing ffmpeg/ffprobe; summary is 2 failed, 934 passed, 1 warning. No third failed ID or collection/error section appears.

## Checklist Results

Manual procedures were performed by codex-gpt-6.1-sol and have null exit codes. Command rows record actual process exits. Recorded suite inspection is not reviewer suite execution.

| Check | Result | Command or observed procedure | Exit | Evidence |
|---|---|---|---|---|
| R1 — F1 | pass | Run refreshed s35-review-probe.py with production adapter/HTTP handlers | 0 | Original failing-query cases now succeed on CPU; terminal probe/vocab/weight failures are typed |
| R2 / E1 / IR-3 / IR-4 / DR-1 — error boundary/generalization | fail | Run s35-r2-import-probe.py; inspect adapter.py:284-310 and source Errors rule | 0 | F2: non-ImportError dependency initialization escapes; HTTP 500 instead of 422 |
| R3 / E4 / DR-5 — evidence freshness | pass | Run identity.py --state-only and compare both handoff/full-gate records | 0 | Exact +c7e4a6b9…32e3 match |
| IR-1 — runtime evidence | pass | Inspect AC-75.10 and final Python/Electron/repeat receipts | null | Installed-runtime test has no dependency overrides; 934 Python passes, Electron 161, repeat 50 |
| IR-2 — collaborator fidelity | pass | Inspect Engines, FakeModels/FakeTTSPort, API forwarding and Electron seam | null | Exact providers/devices/calls/state/payload values asserted |
| IR-5 / E3 / AV-1–AV-4 — test integrity | pass | Inspect every changed test/fixture diff, full new adapter test, Red/Green receipts and adjacent exits | null | Strong/Adequate ratings; immutable assertions; no added masking/retries |
| IR-6 — boundary validation | pass | Inspect ModelLoadIn, ApiModel and device/error contract tests | null | Existing literal/default/extra-forbid preserved; tpu is 422; devices required enum |
| IR-7 — AC/deferral integrity | pass | Compare plan and both handoff AC tables plus actual source/test trace | null | All twenty ACs represented; no disguised deferral; F2 remains explicit in AC-75.9 |
| E2 — geometry | pass | Inspect AC-79.7–.10, launch/default window, primitive classes and final runtime receipts | null | Actual action present; ±0.5 px, overflow/96 px bounds and exact model-switch values |
| E5 / AV-5–AV-6 / DR-2–DR-4 — scope/source consistency | pass | Compare baseline/status and round 1 captures; inspect hubs and correction scope | null | Only authorized product/test/admin paths; no new placeholders or unsourced behavior; error overclaim accounted for by F2 |
| A-1 and Python baseline | pass | Inspect gate predicates, AC-41.3 inputs and baseline/final diagnostics | null | One unrelated UI ID and exactly two packaging IDs accepted; new capture failure rejected |
| A-3 | pass | Inspect clock-pin/assertion diffs, timer cleanup and Red/Green/final receipts | null | Date only; _2/_3 checks preserved; 55 passes ×3; final gate includes pin |
| Red verifier | pass | rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/red-check.py --selftest | 0 | 35 fixtures, 0 wrong |
| Identity verifier | pass | rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --selftest | 0 | 0 failures |

~~~json
{"schema_version":"evidence.v1","check_id":"s35-review-r2-f1","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-review-probe.py","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"Independent failing-query/cause/state and catalog/load/status probe with fake engines and production HTTP","phase":"targeted","exit_code":0,"result":"pass","tested_state":"6097cf59adc7835fa6062c8bd3d55c679aef4543+c7e4a6b9a982862a5f8cfea2ce1d0dc9ee0e71462917bf0ca945f60fb35a32e3","output":"All assertions passed: CPU/CUDA/Auto loads with raising ONNX enumeration -> 200 cpu; catalog -> 200 auto,cpu; torch queries -> cpu with unavailable log; injected probe -> 422 ModelLoadError; vocab/weight causes retained; terminal state unloaded cpu","fresh":true}
~~~

~~~json
{"schema_version":"evidence.v1","check_id":"s35-review-r2-lazy-import","procedure":"Drive valid PyTorch CPU load through production adapter and ASGI route; intercept only kokoro import with OSError; inspect exception class, status, logs and unloaded state","observer":"codex-gpt-6.1-sol","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"AC-75.9 terminal dependency initialization boundary","phase":"targeted","exit_code":null,"result":"fail","tested_state":"6097cf59adc7835fa6062c8bd3d55c679aef4543+c7e4a6b9a982862a5f8cfea2ce1d0dc9ee0e71462917bf0ca945f60fb35a32e3","output":"Probe process exited 0; product observation failed: bare OSError, no tts.load_failed, unloaded cpu; POST /api/v1/models/load returned 500 internal_error rather than 422 ModelLoadError","fresh":true}
~~~

Template source-label, exact-validation, BUILD_PLAN audit, post-MEU sequencing, naming/frontmatter and evidence/FAIL_TO_PASS observations are supported by the inspected plan/task/handoffs. No formatting/ceremony finding is raised.

## Verdict and Follow-up

**changes_required — intent partial.** F1 is fixed. F2 is one High, High-confidence blocking deliverable/behavior finding against AC-75 (AC-75.9); no Critical finding.

The implementing agent should correct the lazy import boundary through /execution-corrections, write a failing adapter/HTTP regression first, preserve exception causes and clean state, rerun affected checks and the full gate, refresh both handoffs, then request ledger round 3 within the existing six-round cap. Keep F1 fixed and preserve F2's ID. No plan redesign or layout correction is requested.

Report staged ONLY at C:/Temp/av-kit/dispatch/s35-exec-review-report.md. The orchestrator appends this complete round 2 report to .agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md, updates frontmatter from this verdict and records the matching JSON. H1-7/H2 approval work remains pending; this is review completion, not implementation DONE.

Residual limits: recorded full-suite/Electron evidence plus synthetic dependency/engine probes; no fresh suite execution, actual broken DLL, physical GPU load or new visual measurement is claimed. The static-only and final-JSON instructions override the workflow's standalone timestamp-script/chat-line convention.

---

## Corrections Applied — 2026-10-17 (round 2 → round 3 request)

Implementer: claude-code, `/execution-corrections` inside the authorized execution loop. This section is the implementer's account. It does not change the reviewer's text above, and it does not approve anything: the verdict is `corrections_applied`, and only an independent review may set `approved`.

**Budget.** The ledger refused round 3 on tokens. Mat added 20M and pre-approved rounds up to the cap of 6 ("Add 20M, upt to 6 rounds pre-approved"; `review_ledger.py continue`, tokens 18,411,384/41,000,000, rounds 2/6).

### F2 — lazy engine import bypasses AC-75.9 (preserved ID)

**Plan.** A `kokoro` that is installed but fails to initialize is a terminal load failure on this host, the same class as a failing `KModel` constructor. So it takes the same message and log. `ImportError` keeps its existing not-bundled reason. The import has no device, so there is no CPU retry. Recorded as MEU-75 handoff D-23 and in the plan's §Execution Correction Notes.

**Change** (`packages/infrastructure/src/avkit_infra/tts/adapter.py`, now +175/−43 against 6097cf5): `_load_pytorch` keeps `except ImportError` → `ModelLoadError("PyTorch runtime is not bundled")`. It adds `except Exception` → one `tts.load_failed` log (`variant_id`, `device` = the target, `error` type name) and `ModelLoadError("PyTorch model failed to load")` from the cause. The message carries no path. The `load_model` docstring names the case.

**Regression** (`tests/integration/test_tts_device_resolution.py:730` `test_ac_75_9_engine_import_failure_is_model_load_error_neg`, written first). It starts from a successful CUDA load. Then, for an `OSError` and for a `RuntimeError` raised by the `kokoro` import, it checks:
- `ModelLoadError` is raised, with that exact cause and message;
- one `tts.load_failed` is logged;
- no engine call is made;
- the message carries no path;
- the adapter is fully unloaded.

Then, over HTTP, `POST /models/load` answers 422 `ModelLoadError` "PyTorch model failed to load". The fixture `_kokoro_failing_import` installs a `kokoro` module whose `KModel` attribute raises. That is what `from kokoro import KModel` meets when the package fails partway through its own imports.

**Verification.**

| Check | Exit | Decisive output | Receipt |
|---|---|---|---|
| Red | 1 | `1 failed, 23 deselected` (`OSError: engine dependency DLL initialization failed`) | `C:/Temp/av-kit/s35-f2-red-py.txt` |
| Green: the five F1 test files, unfiltered | 0 | `61 passed, 1 warning` | `C:/Temp/av-kit/s35-f2-green-py.txt` |
| `ruff check packages/ tests/`, `ruff format --check` (2 files), `pyright packages/` | 0 | `All checks passed!`, `2 files already formatted`, `0 errors` | `s35-f2-ruff.txt`, `s35-f2-pyright.txt` |
| Fresh full gate (task.md H1-2, verbatim) | 0 | `session-gate: all steps exit 0`; `tested_state 6097cf59…4543+b4e8b882…1051` (re-derived by `identity.py --state-only`); `changed paths: 39 outside scope: []`; py-tests and ui-tests `outside_baseline=[]`; Electron 161 passed, e2e-repeat 50 passed | `C:/Temp/av-kit/s35-gate-h1/`. The receipts round 2 reviewed are in `s35-gate-h1-r2/`. The first post-F2 attempt is in `s35-gate-h1-r3fail/`. |

**Gate re-run A-4** (autonomous, no file change). The first post-F2 attempt failed only at `ui-electron`, on `capture-inbox.test.ts:1141` AC-66.14: `ox` -920.5 against the expected -828.5 after a middle-button pan. That test belongs to an earlier capture session. No Session 35 change reaches it, and the only change since attempt 3 passed is the Python adapter and its test. Alone it passed 5/5 (`s35-gate-flake-ac6614.txt`). It is logged as known issue `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`, and the whole gate was re-run unchanged, following A-2. A second miss would have stopped for Mat. The cause is not proven and the test is another session's, so it was not edited. See `walkthrough.md` §A-4.

Both handoffs were regenerated from the re-run, and H1-6, H1-6a and H1-6b were re-run. The MEU-75 handoff gains:
- the F2 FAIL_TO_PASS row and its Red and Green records;
- D-23 and a History row;
- updated `adapter.py` and test-file rows in its Files table;
- the AC-75.10 line reference moved to `:772`.

The A-4 note makes the plan cite `AC-66.14`, so both AC tables gain an `n/a` cross-reference row for it, like AC-40 and AC-41. H1-6 now reports `20 AC row(s)` and `all 10 plan AC(s) present` for both handoffs; all three checks exit 0 (`C:/Temp/av-kit/s35-closeout/`).

**Sibling sweep.** The adapter has one other import, the module-level `import torch` inside `try/except ModuleNotFoundError`. It runs when the sidecar imports the adapter, not during a load request, so it is outside the `load_model` contract. `_load_onnx` has no lazy import: `InferenceSession` is a module-level name, and both of its constructions are inside guards. The R1 claim that only three statements in `load_model` were unguarded missed this import, because it is an import rather than a call. D-23 and the walkthrough record that.

**Cross-doc sweep.** `03-service-layer.md:469` ("never a bare exception") now holds for this path, so it is unchanged. The plan (§Execution Correction Notes), `walkthrough.md` (§Execution review R2, §A-4), the MEU-75 handoff and `known-issues.yaml` were updated.

**Requested.** Execution ledger round 3, within the cap of 6. Please re-check F2 under its ID.

---

## Round 3 review — 2026-10-17 (Codex, verbatim below this line)

> **Review Mode:** execution, ledger round 3 of 6.  
> **Verdict:** approved. F1 and F2 are fixed; no open blocking or Critical finding.

## Recheck (2026-10-17)

Standalone round 3 report for appending to the existing rolling implementation review. Preserve both earlier reports and both implementer correction accounts.

## Intent Anchor

Session 35 delivers MEU-75 (the TTS device list comes from the runtime, an unavailable or failing device falls back to CPU with a logged reason, the model status reports the device actually used, and a failed load returns its reason as a 422) and MEU-79 (the Voice panel lists only the selected model's devices and lays out Model, Device, the model action, Speed and Format at one control height on aligned rows, pinned by Electron geometry at the default window).

The delivered tree achieves that intent within the approved FIC. The lazy engine initialization failure that prevented approval in round 2 now follows the domain-error/422 path.

## Scope

Reviewed worktree `P:/av-kit-wt/s35-tts-voice-panel`, branch `claude/s35-tts-voice-panel`, against baseline `6097cf59adc7835fa6062c8bd3d55c679aef4543`. The expanded handoff set, read in execution order, is:

- `.agent/context/handoffs/2026-10-16-tts-voice-panel-MEU-75-handoff.md`;
- `.agent/context/handoffs/2026-10-16-tts-voice-panel-MEU-79-handoff.md`.

Secondary scope: the full correlated plan folder `docs/execution/plans/2026-10-16-tts-voice-panel/` (implementation plan, task, walkthrough, gate, identity, Red checker, baseline); changed product/schema/test/fixture files; hub/SSOT/rendered changes; prior rolling review/corrections; named Session 35 receipt snapshots. Applied workflow IR-1–IR-7, reviewer AV-1–AV-6, R1–R3, E1–E5 and baseline questions.

Claude Code / Anthropic authored the work; Codex `gpt-6.1-sol` is the independent reviewer. No repository file was written. Main-checkout product/plan/tests were not read; the only intentional main-checkout project read was the requested mechanism vocabulary. Reviewed strings were treated as data; no secret, cookie or credential file was read.

Verification was static except for the three allowed plan-verifier invocations and scratch Python probes. No project test runner, build, npm command, uv sync, gate, generator, task/closeout validator or MCP audit was executed. Suite totals below are inspected author receipts. H1-7 and H2 remain the orchestrator's responsibility; approval does not mean implementation closeout is already DONE.

## Findings

| # | Severity | Blocking | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|
| F1 | High | no | Fixed: AC-75.9 runtime-query failures no longer prevent a usable CPU load or escape as bare exceptions. Failed queries omit the affected accelerator with a probe warning; injected-probe terminal failures are ModelLoadError. Independent catalog/load/status and cause/state probes pass. | `packages/infrastructure/src/avkit_infra/tts/adapter.py:72`, `:99`, `:248` | Retain the failing-query and terminal-cause regressions. | fixed |
| F2 | High | no | Fixed: AC-75.9 lazy kokoro initialization failures now raise ModelLoadError with the original cause, emit one tts.load_failed event and leave unloaded CPU state; the real load route returns 422. ImportError retains the not-bundled reason. | `packages/infrastructure/src/avkit_infra/tts/adapter.py:284`, `:289`, `:123` | Retain the engine-import regression and the separate ImportError behavior. | fixed |

Both carried findings retain confidence **High**, subject **deliverable**, finding_kind **behavior**, and `violates: AC-75` (full criterion **AC-75.9**). Blocking is **no** because each is fixed. No control-defeat mechanism or new finding is asserted.

## R1 — Prior findings and decisive recheck

**F2 is fixed by code, not its change log.** `_load_pytorch` catches ImportError first at adapter `:287`. The added `except Exception` at `:289` logs through `_log_load_failed` and raises `ModelLoadError("PyTorch model failed to load") from exc`. This precedes construction, and `load_model` already called `unload_model` at `:246`. State commits only after engine success (`:262–265`), so no prior CUDA or partial replacement model survives.

Re-executed the original `s35-r2-import-probe.py`, process exit 0:

```text
prior_load True cuda
lazy_import {"exception": "ModelLoadError", "is_ModelLoadError": true, "message": "PyTorch model failed to load", "events": ["tts.load_failed"], "loaded": false, "device": "cpu"}
HTTP POST /api/v1/models/load 422 {"error":{"code":"ModelLoadError","message":"PyTorch model failed to load","details":null}}
```

Additional scratch probe `s35-r3-import-assertions.py` asserts exact cause identity, message, event count/fields, no construction and all cleared adapter fields after a prior CUDA load. It intercepts only the kokoro import:

```text
OSError PASS cause identity; message: PyTorch model failed to load ; load_failed: 1 ; no construction; unloaded cpu
RuntimeError PASS cause identity; message: PyTorch model failed to load ; load_failed: 1 ; no construction; unloaded cpu
ImportError PASS cause identity; message: PyTorch runtime is not bundled ; load_failed: 0 ; no construction; unloaded cpu
round3 import assertions: all passed
```

**F1 stays fixed.** Re-executed `s35-review-probe.py`, exit 0. Raising ONNX enumeration permits CPU/CUDA/Auto requests to load one CPU session; HTTP load/status report CPU and the catalog returns `['auto','cpu']`. Raising torch queries produce two probe warnings and unavailable-device fallback. Injected probe failure yields 422 ModelLoadError; probe, vocab and weight-stat causes remain attached with unloaded CPU terminal state. Final output: `round2 probe: all assertions passed`.

## R2 — Generalization and test sensitivity

The load-path sweep finds no materially different bare-exception failure within the declared contracts:

- Lazy KModel import/initialization is guarded. ImportError preserves the existing not-bundled reason; other Exceptions indicate installed engine initialization failure and use the constructor-failure message/log without a futile device retry. Both remain ModelLoadError/422, consistent with 03-service-layer.md:465–469, LOAD_FALLBACK and LOAD_ERROR_HTTP. The preserved ImportError path did not acquire a new logging requirement.
- Vocab resolution, its is_file check, KModel construction, both `.to()` attempts and `.eval()` are inside the outer guard (`adapter.py:294`). Failed accelerator move retries CPU once; constructor/eval failure is final **as expressly approved**. The prompt's shorthand does not override that contract.
- Both ONNX constructions are guarded (`:321`, `:332`). Raising CUDA construction/provider read retries CPU; silent CUDA-provider loss reports CPU/provider_fallback; CPU failure retains its cause. CPU sessions never read providers.
- There is **no kokoro_onnx construction** on this load path: the adapter uses module-level onnxruntime InferenceSession. The only lazy import is KModel. Module-level torch/onnxruntime import failures occur at sidecar startup, outside this load-request correction. `_load_onnx_vocab` is invoked by generation, not loading; it is not silently claimed as newly delivered load behavior.
- Catalog availability calls go through `_query`; a raising query omits that accelerator while preserving Auto/CPU. F1's independent HTTP probe verifies the production catalog path. Injected probes are internal collaborator contracts.
- Initial unload and temporary locals remain. No examined terminal path commits a variant/model/session/accelerator device. Tests inspect status and internal cleared fields after previous CUDA success.

The regression at `tests/integration/test_tts_device_resolution.py:730` is **Strong**: OSError and RuntimeError must produce ModelLoadError, the identical cause, exact message, one failure event, no engine call, path-free message and cleared state; the real HTTP route must return 422 with code/message. Without the handler its first OSError escapes `pytest.raises(ModelLoadError)`. The Red receipt proves that exact failure: `E OSError: engine dependency DLL initialization failed`, named test FAILED, `1 failed, 23 deselected`; `s35-f2-red-py.exit` is `1`. Green reports `61 passed, 1 warning`; ruff clean, two files formatted, pyright zero errors.

## R3 — Post-correction evidence and A-4

Both handoffs' single final full evidence.v1 record identifies post-F2 H1-2, second attempt after A-4. Independently executed identity.py --state-only with PYTHONDONTWRITEBYTECODE=1 and ELECTRON_RUN_AS_NODE unset, exit 0:

```text
6097cf59adc7835fa6062c8bd3d55c679aef4543+b4e8b8826bfc3656e7084cc3e63b7682214f97ad1d1b5ad141e4640573211051
```

This equals both handoffs, gate before/after, and the failed post-F2 attempt's before identity. Before/after identity receipts have identical SHA-256. Identity binds changed code/tests/config/gate/hub inputs and runtime versions, excluding documented closeout outputs; it is not a count of dirty paths.

Static comparison against saved R2 captures compares **29 tracked diff sections**: only adapter.py and excluded known-issues.yaml changed. Numbered-source comparison shows the adapter docstring/four-line exception handler plus exactly the appended import-failure helper/test in the untracked integration file (739 → 789 lines). No porcelain path was added/removed. Compared UI, API/core, other tests, hubs and gate diff blob identities remain unchanged. The issue delta adds the disclosed capture flake; plan/handoff/walkthrough changes record corrections/closeout. No additional F2 product change was found.

**A-4 is honest; its cause remains unproven.** The failed snapshot shows only capture-inbox AC-66.14 failing: expected pan origin -828.5, received -920.5, `1 failed, 160 passed`. The gate stops at ui-electron; repeat/final identity are explicitly not_run. Five isolated repetitions pass. The final full run includes that same assertion passing, 161 Electron passes and 50 repeats, with identical bound inputs.

AC-66.14 manipulates Capture zoom/pan/mouse state under its own seam. F2 changes the TTS Python import boundary and its Python test. Existing Session 35 renderer changes are TTS-local; shared SegmentedControl preserves default/sm markup. Capture product code, capture-inbox.test.ts, global styles and the window factory are unchanged. I found no plausible changed path from F2 to the pan-origin miss. This supports an unrelated intermittent failure, not proof of its timing hypothesis. A-4 discloses uncertainty and reruns the **whole** unchanged gate; no failed receipt is normalized away and no retry is added. S6's repeat stage did not fail.

**Every non-baseline raw stage exits 0.** Python/UI raw exits remain **1**, accepted by the baseline predicates below. The gate's concluding “all steps exit 0” describes normalized gate outcomes, not universal raw suite success.

## Commands Executed and Decisive Output

All commands used cwd `P:/av-kit-wt/s35-tts-voice-panel`. Exact-evidence commands used rtk proxy, all-stream receipts under `C:/Temp/av-kit/dispatch/s35-r3-*.txt`, immediate exit capture, completed receipt readback and propagation. Python used the worktree interpreter and PYTHONDONTWRITEBYTECODE=1; identity also unset ELECTRON_RUN_AS_NODE and set process RECEIPTS_DIR=C:/Temp/av-kit.

| Executed command | Exit | Decisive output |
|---|---|---|
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/red-check.py --selftest` | 0 | 35 fixtures, 11 positive/24 negative, zero wrong. |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --selftest` | 0 | Bound-path/runtime mutations invalidate history; nine closeout artifacts do not; zero failures. |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --state-only` | 0 | Exact +b4e8b882…1051 state above. |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-review-probe.py` | 0 | All F1 assertions pass; CPU catalog/load/status usable, terminal probe HTTP 422. |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-r2-import-probe.py` | 0 | F2 typed failure, one event, unloaded CPU, HTTP 422. |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-r3-import-assertions.py` | 0 | OSError/RuntimeError/ImportError exact causes, messages, log counts and clean state. |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-r3-static-audit.py` | 0 | 29 R2 tracked diff snapshots compared; only adapter and excluded issue record differ; new test adds 50 lines; no status-path additions/removals; receipt observations/SHA-256s. |
| `rtk proxy git status --short` | 0 | 33 modified tracked paths, six untracked paths. |
| `rtk proxy git diff 6097cf5 -- packages/infrastructure/src/avkit_infra/tts/adapter.py` | 0 | Added lazy-import handler; retained engine/retry/state guards. |
| `rtk proxy git diff 6097cf5 -- <explicit remaining product/schema, Python-test, UI-test and hub path groups>` | 0 | Device transport/layout, preserved assertions, OpenAPI only devices, truthful hubs. Path groups are the changed paths traced below and in the scope. |
| `rtk proxy rg -n '^' <adapter, new integration test, geometry test, gate, workflow>` and bounded `rtk proxy pwsh -NoProfile -Command 'Get-Content …'` | 0 | Current numbered source and source/receipt observations throughout this report. |

One initial plan-range read had a PowerShell quoting error (exit 1); a support read/search guessed nonexistent helper paths (exits 1/2), corrected by reading the actual local launch helper/window factory. The scratch comparison initially retained CR in path keys; corrected/rerun before using its conclusions. None ran product checks or changed repository files. Git's global-ignore permission warning remained visible but did not prevent successful status/diff/identity observations.

### Inspected author run of record

| Stage | Actual recorded result |
|---|---|
| identity-before; static py-types/py-lint/ui-types/ui-lint/mcp-types/task-contract/scope-paths | All exit 0; changed paths 39, outside scope empty. |
| py-tests | Raw 1; only AC-24.10/AC-25.10; 2 failed, 935 passed, 1 warning; baseline failed=2 outside_baseline=[] errors=0. |
| ui-tests | Raw 1; only AC-41.3; 96 files, 1 failed/980 passed (981); baseline failed=1 summary_failed=1 outside_baseline=[] unhandled=0. |
| mcp-build/tests, ui-build/harness-build/picker-stub, openapi, state-render | All exit 0; MCP 428 passes; OpenAPI in sync; render 91 MEUs/12 phases, no drift. |
| ui-electron | Exit 0; 161 passed (5.7m), including AC-66.14, AC-64.6 and all AC-79 Electron tests. |
| e2e-repeat | Exit 0; 50 passed (2.2m), AC-79/AC-64.6 repeated ten times. |
| identity-npm/identity-after | Exit 0; Playwright 1.62.1, Electron 42.9.3; before/after equal; gate concludes all steps exit 0. |
| H1-6/H1-6a/H1-6b | Console exits 0; current handoffs each have 20 AC rows, all ten referenced plan families, no blocked rows and matching durable records. |

### Receipt hashes

SHA-256 from the stdlib read-only audit; relative to C:/Temp/av-kit/:

| Receipt | SHA-256 |
|---|---|
| `s35-gate-h1/s35-gate-h1.txt` | `2ed956c262b79284fb0e374dea08a9f6a9c91cbe2c507799d798b1862b260129` |
| `s35-gate-h1/s35-D6-identity-before.txt` and `s35-D6-identity-after.txt` | `dc506941ed7dbb18d9972c42136bf660d937f542fed875eedab7fe53d28e4746` |
| `s35-gate-h1/s35-D6-py-tests.txt` | `6fc265043ab627c6562c66e69186f05b187549686344dfafdf79a5d5e87aa489` |
| `s35-gate-h1/s35-D6-ui-tests.txt` | `d13cd0eed135d3960a86d9c8fe5cfa1a9f5566b2fc1aa142c5da91c24aa63113` |
| `s35-gate-h1/s35-D6-ui-electron.txt` | `320ec8ed97e7fa3439bbc2ac1dfe0d11ce1eb77ee806430c0ef082acaa007d25` |
| `s35-gate-h1/s35-D6-e2e-repeat.txt` | `e848d31f1210b310585efdff0911428ec910b3b6ed5152d3a9ebfbfc1c071b2c` |
| `s35-f2-red-py.txt` | `0404b5ee034c15fd60bc764cf7b3780c28e59624d36e753bb946e8284c003654` |
| `s35-f2-green-py.txt` | `0435db9d3bf571cace30d60ef4de8cf4d916107cf872810557d36bfbe9c3f24b` |
| `s35-gate-h1-r3fail/s35-D6-ui-electron.txt` | `dd3e2133c7c015e5734599aeb477a6c504f343789de7fa987b7e1c46bb107e2a` |
| `s35-gate-flake-ac6614.txt` | `5f5768f33cbaf9bb9ecf61988ded018b5210d9323f05e32ccbe8a6bdfc478267` |

## Acceptance-Criteria Trace

Paths are worktree-relative. Pass means delivering code, meaningful assertions and matching recorded execution, supplemented by independent probes; it does not claim a reviewer suite run.

### MEU-75

| AC | Product file:line | Test file:line that detects absence/regression | Status |
|---|---|---|---|
| AC-75.1 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:72`, `:85`, `:96` | `tests/integration/test_tts_device_resolution.py:187`; `tests/integration/test_tts_no_torch.py:150` — exact torch matrix/None/missing-MPS/fresh blocked interpreter | pass |
| AC-75.2 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:81` | `tests/integration/test_tts_device_resolution.py:210` — exact providers, no ONNX MPS/TensorRT-as-CUDA | pass |
| AC-75.3 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:270`, `:113` | `tests/integration/test_tts_device_resolution.py:231`, `:255` — unavailable CUDA/MPS CPU calls/status, warning/no-warning bounds | pass |
| AC-75.4 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:281`, `:294`, `:246`, `:262` | `tests/integration/test_tts_device_resolution.py:309`, `:330`, `:357`, `:377` — retry/cause/log/constructor/eval/final state | pass |
| AC-75.5 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:317` | `tests/integration/test_tts_device_resolution.py:398`, `:420`, `:443`, `:463`, `:486` — provider fallback/retry/CPU failure/state/no CPU provider read | pass |
| AC-75.6 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:273` | `tests/integration/test_tts_device_resolution.py:275`, `:294` — CUDA/MPS/CPU preference, exact calls, no Auto warning | pass |
| AC-75.7 | `packages/core/src/avkit_core/ports/tts.py:41`; `packages/core/src/avkit_core/services/models.py:105`; adapter `:232` | `tests/integration/test_tts_device_resolution.py:500`; `tests/unit/test_services.py:2201`; `tests/unit/test_domain.py:1154` — forwarding/format/call/exact protocol | pass |
| AC-75.8 | `packages/api/src/avkit_api/schemas/models.py:48`; `packages/api/src/avkit_api/routes/models.py:42`, `:61`, `:72`, `:95`; `openapi.committed.json:1886` | `tests/e2e/test_api_tts_models.py:199`, `:206`, `:215` — all three payloads, exact lists, required enum schema, tpu 422 | pass |
| AC-75.9 | `packages/api/src/avkit_api/errors.py:36`, `:150`; adapter `:211`, `:248`, `:284`, `:289` | `tests/e2e/test_api_error_surface.py:274`, `:282`; `tests/integration/test_tts_device_resolution.py:520`, `:563`, `:588`, `:616`, `:657`, `:681`, `:730` — envelope/status/F1/F2/cause/state; independent probes | pass |
| AC-75.10 | `packages/infrastructure/src/avkit_infra/tts/adapter.py:72` | `tests/integration/test_tts_device_resolution.py:772` — installed flags/providers without dependency overrides | pass |

### MEU-79

| AC | Product file:line | Test file:line that detects absence/regression | Status |
|---|---|---|---|
| AC-79.1 | `ui/src/renderer/src/features/tts/TTSPage.tsx:266`, `:474`; `useTtsJob.ts:58` | `ui/tests/unit/tts-page.behavior.test.ts:727` — exact options before/after model selection | pass |
| AC-79.2 | `ui/src/renderer/src/features/tts/TTSPage.tsx:267`, `:475`, `:495`, `:477` | `ui/tests/unit/tts-page.behavior.test.ts:737` — shown/posted Auto, zero PUT, retained CUDA on supported row | pass |
| AC-79.3 | `ui/src/renderer/src/features/tts/TTSPage.tsx:266` | `ui/tests/unit/tts-page.behavior.test.ts:754` — absent devices exactly Auto/CPU | pass |
| AC-79.4 | `ui/src/renderer/src/features/tts/TTSPage.tsx:196` | `ui/tests/unit/tts-page.behavior.test.ts:761` — 422 reason in banner, no fetch-error substitution | pass |
| AC-79.5 | `ui/src/renderer/src/components/ui/SegmentedControl.tsx:22`, `:26`, `:36` | `ui/tests/unit/layout-primitives.test.ts:306` — baseline default/sm literal, only-md-height, identical children | pass |
| AC-79.6 | `ui/src/renderer/src/features/tts/TTSPage.tsx:452`, `:487`, `:585`, `:591`, `:603`, `:616` | `ui/tests/unit/tts-page.behavior.test.ts:782` — grid/height/wrapper classes and forbidden old classes | pass |
| AC-79.7 | `ui/src/renderer/src/features/tts/TTSPage.tsx:452`, `:487`; `components/ui/SelectInput.tsx:26` | `ui/tests/e2e/tts-generate.test.ts:762` — actual model/device/action height/bottom, label tops, Model wider | pass |
| AC-79.8 | `ui/src/renderer/src/features/tts/TTSPage.tsx:585`, `:591`, `:603`, `:616`; SegmentedControl `:36` | `ui/tests/e2e/tts-generate.test.ts:781` — actual combobox/Format/slider/preset inner boxes, bottom/width relations | pass |
| AC-79.9 | `ui/src/renderer/src/features/tts/TTSPage.tsx:452`, `:585`, `:637` | `ui/tests/e2e/tts-generate.test.ts:807`; AC-64.6 `:602` — no overflow, slider >=96, default-window visibility | pass |
| AC-79.10 | `ui/src/renderer/src/features/tts/TTSPage.tsx:266`, `:474` | `ui/tests/e2e/tts-generate.test.ts:836` — exact 2/3 option values through actual model selection | pass |

## E1–E5 and gate answers

### E1 — Delivery

Runtime order remains Auto, CUDA, CPU, MPS with format-specific membership; ONNX never offers MPS. Missing torch/failed queries retain Auto/CPU. Resolution, fallback/final failure, clean state and actual status are delivered as traced above. API devices appear on every required variant response; ModelLoadError returns a reason-bearing 422 while unrelated RuntimeError stays masked 500. UI uses effectiveDevice for display/load and persists only explicit user changes. Default/sm SegmentedControl's literal/fieldset/children are unchanged in the source diff; md alone adds h-9. F2 changes no normal device/UI behavior.

### E2 — Geometry oracles

The unchanged launchApp at tts-generate.test.ts:13 gives each instance fresh AVKIT_APP_DATA; the unchanged window factory at ui/src/main/index.ts:140 defaults to 1280×800. openVoicePanel waits for the voice request, selected ONNX row, actual unload button and two frames. Tests measure controls, actual labels and the preset **inner** div. Null measurements fail. expectNear permits only inclusive ±0.5 px; NaN/out-of-bound delta fails object equality. D-20 changes diagnostic presentation only.

Unequal height/bottom/label alignment beyond the tolerance cannot pass; overflow/slider <96 also fail. Relative equality alone could accept a hypothetical uniform wrong height across every control. In this tree, unchanged SelectInput h-9 and unit-pinned action/slider/preset classes anchor 36 px; no uniform wrong-height layout exists. This is the approved oracle's existing limit. AC-79.10 asserts exact option values, not just counts. Final runtime evidence includes all geometry cases and AC-64.6, each repeated ten times.

### E3 — Test integrity

All changed test/fixture diffs and all 789 lines of the new adapter test were inspected. Existing assertions remain intact. TA-1 scopes CUDA probe repair to the explicit-CUDA case; TA-2/TA-4 add the new facade/port method; TA-3 extends the exact protocol set; TA-5 needs no fixture edit; TA-6 supplies format-specific devices in the existing Electron seam. These follow approved contracts.

No added skip/only/xfail masking, retry or timeout padding was found. The new no-torch subprocess uses the existing 300-second convention, not a padded old test. Intended Red filtering explains skipped non-target cases in historical Red runs. A-3 only pins Date in the two collision tests/restores timers; _2/_3 and preservation assertions remain intact, with no capture product changes. R2 snapshot comparison confirms those tests have not changed again.

IR-5 grades: each new adapter matrix/resolution/fallback/cause/state/HTTP/live-runtime test, no-torch test, service/schema/envelope test, rendered UI device/error test, primitive markup test and Electron geometry/device-switch test is **Strong**. AC-79.6 DOM-class coverage is **Adequate** for its explicit class contract, backed by Strong geometry cases. Fixtures preserve relevant call/value behavior. No changed test is Weak.

### E4 — Evidence honesty

Both final handoff records equal the live state and saved gate. F2 Red/Green, Python 935 passes, UI 980 passes, Electron 161, repeat 50, task evidence and A-4 fail-fast/unchanged rerun match receipts. Current H1-6/a/b console reports each exit 0; older combined closeout receipts are not substituted for current per-MEU results. Prior reports remain preserved; implementer corrections_applied frontmatter was not treated as approval. Gate success does not override independent behavior evidence.

### E5 — Scope and hubs

Every changed path belongs to PRODUCT_SCOPE/Files tables, plan artifacts or administrative closeout, with the two human-authorized A-3 test extensions. OpenAPI changes only ModelVariantOut.properties.devices and its required entry. Matrix rows 3.8/11.13 preserve planned names/dependencies. 03's Delivered note now truthfully describes device detection/fallback/actual status and typed 422 failures; 11 matches the row/height/device/geometry delivery. SSOT/BUILD_PLAN/registry remain ready_for_review. Reflection, metrics, issue resolution and approved status writes belong to H2 after this verdict is collected.

### A-1 / D-19 and Python baseline

**A-1 applies Verification Plan §1's own suite-independent baseline rule.** It adds no product/test exception beyond the one baseline id. session-gate.ps1:94–104 and :162–173 accept only raw exit 1, a nonempty FAIL set entirely in the expected id observed at row 0, matching summary failure count, and no unhandled/error-summary diagnostic. Missing FAIL/summary, a new id or count mismatch fails; non-1 crash exits fail. The earlier capture-picker miss demonstrates rejection of a new id.

The gate invokes full `npm --prefix ui run test`, unfiltered; package/config have no filter change and the receipt shows 96 files/981 tests. The predicate alone cannot authenticate fabricated/filtered output; the inspected command/config/output establish this run. Another layout-canon/queue-canon id cannot be accepted. A new defect inside the already-failing AC-41.3 could theoretically hide behind its first assertion, so its inputs matter: queue-canon.test.ts:159 reads external Zorivest CSS, unchanged av-kit styles.css and unchanged expected token constants. No Session 35 diff reaches those inputs. Both receipts fail the same light pending token, expected #ea580c, received #9a3412. No concrete Session 35 regression is masked.

Python's baseline predicate is unchanged from the approved gate. Row 0/final name only test_pack_dist_onedir_layout[AC-24.10] and test_nsis_pack_check_script[AC-25.10]. Final diagnostics are missing PACK_DIST_EXE/bundled ffmpeg; summary 2 failed, 935 passed, 1 warning; no additional FAILED/ERROR id.

## Checklist Results

Manual observations were performed by **codex-gpt-6.1-sol**, with null exit. Command rows are actual reviewer invocations; suite observations are author-receipt inspection.

| Check | Result | Command or manual procedure | Exit | Evidence |
|---|---|---|---|---|
| R1 — F1 regression | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-review-probe.py` | 0 | All assertions pass; CPU catalog/load/status and typed terminal errors. |
| R1/R2 — F2 and error generalization; IR-3/IR-4 | pass | Run original import probe/additional import assertions; inspect load-time imports/construction/query guards | 0 | Other import failures: one log, exact cause, HTTP 422; ImportError preserved, clean state. |
| R3/E4 — evidence identity | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --state-only` | 0 | Exact post-F2 state equals both handoffs and gate before/after. |
| IR-1/IR-2 — runtime evidence and collaborator fidelity | pass | Inspect real-runtime AC-75.10, recording engines/facades/seams, final suite receipts | null | No overrides in installed-runtime test; exact devices/providers/calls/status; real Electron 161/repeat 50. |
| IR-5/E3/AV-1–AV-4 — test integrity | pass | Audit changed tests/fixtures and entire new adapter test against contracts/Red/Green | null | Strong/Adequate, no Weak or weakened prior assertion; F2 Red intended OSError. |
| IR-6/IR-7 — schema, AC coverage and deferrals | pass | Inspect ModelLoadIn/ApiModel and twenty plan/code/test/handoff AC rows | null | Literal/default/extra-forbid preserved; tpu 422, devices required; no missing AC/disguised deferral. |
| E2 — geometry | pass | Inspect default launch/window, measured elements/helper and final geometry receipts | null | Actual action, ±0.5 px, no overflow, slider >=96, exact selected-row options. |
| E5/AV-5/AV-6 — scope and source consistency | pass | Compare baseline/R2 snapshots and hubs against Files tables/amendments | null | F2 limited to adapter/new test/excluded records; no placeholder/unsourced behavior. |
| A-1/Python baseline | pass | Inspect predicates, AC-41.3 inputs, baseline/final diagnostics | null | One unrelated UI id and exactly two packaging ids; raw failures disclosed. |
| A-4 — capture flake and full rerun | pass | Inspect failed/passing snapshots, source connections and five isolated repetitions | null | Failed run stops; identical-state full rerun passes capture/all later stages; cause unproven. |
| Red verifier | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/red-check.py --selftest` | 0 | 35 fixtures, zero wrong. |
| Identity verifier | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --selftest` | 0 | Zero failures; bound mutations invalidate history. |

```json
{"schema_version":"evidence.v1","check_id":"s35-review-r3-import","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-r3-import-assertions.py","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"AC-75.9 lazy engine import cause/log/state after prior CUDA load; scratch fake engine","phase":"targeted","exit_code":0,"result":"pass","tested_state":"6097cf59adc7835fa6062c8bd3d55c679aef4543+b4e8b8826bfc3656e7084cc3e63b7682214f97ad1d1b5ad141e4640573211051","output":"OSError/RuntimeError: exact cause, PyTorch model failed to load, one tts.load_failed, no construction, unloaded cpu. ImportError: exact cause, PyTorch runtime is not bundled, no new failure log, unloaded cpu. All assertions passed.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s35-review-r3-http-import","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s35-r2-import-probe.py","cwd":"P:/av-kit-wt/s35-tts-voice-panel","scope":"F2 original reproduction through production adapter/ASGI route","phase":"targeted","exit_code":0,"result":"pass","tested_state":"6097cf59adc7835fa6062c8bd3d55c679aef4543+b4e8b8826bfc3656e7084cc3e63b7682214f97ad1d1b5ad141e4640573211051","output":"prior_load True cuda; lazy import ModelLoadError, one tts.load_failed, unloaded cpu; POST /api/v1/models/load 422, code ModelLoadError, message PyTorch model failed to load","fresh":true}
```

Template source-label/exact-validation/BUILD_PLAN-audit/post-MEU-sequence/naming/frontmatter/evidence observations are supported by inspected plan/task/handoffs. No ceremony-only finding is raised. All checklist outcomes pass, satisfying RULE-2.

## Verdict and Follow-up

**approved — intent achieved yes.** F1 and F2 are fixed, with zero open blocking and no Critical findings. No additional correction/review round is required for this state.

Report staged only at `C:/Temp/av-kit/dispatch/s35-exec-review-report.md`. The orchestrator should append this complete round 3 report to `.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md`, update frontmatter from this verdict, record the matching JSON in the existing ledger, then continue authorized H1-7a/b and H2 closeout. This reviewer makes no repository/status/commit/push changes.

Residual limits: suite/geometry results are inspected receipts; reviewer execution uses synthetic engine/import failures with production adapter/HTTP paths. No physical GPU, actual broken DLL, fresh suite run or visual measurement is claimed. The capture pan flake remains separately tracked with unproven root cause. No unresolved human decision is needed for this review. The user's static-only/JSON-only/receipts-only instructions override the workflow's timestamp script/chat-line and canonical repository-write conventions.

---

## Round 4 review — 2026-10-17 (Codex, verbatim below this line)

## Recheck (2026-10-17)

Session 35 delivers MEU-75 (the TTS device list comes from the runtime, an unavailable or failing device falls back to CPU with a logged reason, the model status reports the device actually used, and a failed load returns its reason as a 422) and MEU-79 (the Voice panel lists only the selected model's devices and lays out Model, Device, the model action, Speed and Format at one control height on aligned rows, pinned by Electron geometry at the default window).

Narrow confirmation, execution ledger round 4 of 6, for `P:/av-kit-wt/s35-tts-voice-panel`, branch `claude/s35-tts-voice-panel`. Claude Code / Anthropic authored the work; Codex `gpt-6.1-sol` independently confirms the round 3 conclusions. The bound tree/runtime identity is unchanged, both handoffs match it, and the rolling review preserves the round 3 body and frontmatter exactly. I still hold the intent achieved and F1/F2 closed. This round supplies the explicit carried-finding closure table; it does not repeat the full review. Verification used static reads/git only, plus the permitted `identity.py --state-only`. No tests, builds, validators, generators, probes or MCP audits ran. Reviewed strings were data; no secrets, cookies or credentials were read. No repository file was written.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| F1 | fixed in round 2; confirmed fixed in round 3 | fixed |
| F2 | fixed in round 3 | fixed |

### Confirmed Fixes

- F1: `packages/infrastructure/src/avkit_infra/tts/adapter.py:99` catches/logs runtime-query failures while preserving Auto/CPU; `:248` wraps terminal injected-probe failures in ModelLoadError. Round 3's cause/state and HTTP conclusions remain applicable.
- F2: `packages/infrastructure/src/avkit_infra/tts/adapter.py:289` logs lazy engine-initialization failure and raises ModelLoadError with its cause; `:287` preserves the separate ImportError reason. Round 3's clean-state and 422 conclusions remain applicable.

### Commands Executed and Decisive Output

Evidence commands used cwd `P:/av-kit-wt/s35-tts-voice-panel`, `rtk proxy`, all-stream receipts under `C:/Temp/av-kit/s35-r4-*.txt`, immediate exit capture and completed-receipt readback. The identity process set `PYTHONDONTWRITEBYTECODE=1`, unset `ELECTRON_RUN_AS_NODE`, and set `RECEIPTS_DIR=C:/Temp/av-kit`.

| Executed command | Exit | Decisive output |
|---|---|---|
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-tts-voice-panel/identity.py --state-only` | 0 | Exact state below; matches round 3 and both handoffs. |
| `rtk proxy git status --short --branch --untracked-files=all` | 0 | Branch claude/s35-tts-voice-panel; 33 modified tracked paths, six untracked, matching round 3. |
| `rtk proxy git diff --stat 6097cf59adc7835fa6062c8bd3d55c679aef4543` | 0 | 33 files changed, 841 insertions(+), 139 deletions(-). |
| `rtk proxy powershell -NoProfile -Command "Get-Content -LiteralPath '.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md' -Encoding UTF8 -Tail 247"` | 0 | Read the complete round 3 section: approved; F1/F2 fixed; zero blocking findings. |
| `rtk proxy rg -n 'tested_state\|"phase"' .agent/context/handoffs/2026-10-16-tts-voice-panel-MEU-75-handoff.md .agent/context/handoffs/2026-10-16-tts-voice-panel-MEU-79-handoff.md` | 0 | MEU-75 :115 and MEU-79 :99 each record the exact state below, phase full, result pass, exit_code 0. Historical evidence was read, not rerun. |
| `rtk proxy rg -n '^' packages/infrastructure/src/avkit_infra/tts/adapter.py` | 0 | Current F1/F2 handlers remain at the confirmed locations above. |

Exact observed state:

```text
6097cf59adc7835fa6062c8bd3d55c679aef4543+b4e8b8826bfc3656e7084cc3e63b7682214f97ad1d1b5ad141e4640573211051
```

Additional static comparison (exit 0) read the canonical rolling review and the original round 3 report at the assigned temporary path before replacing it. Actual command, formatted across lines for readability:

```powershell
rtk proxy pwsh -NoProfile -Command {
  $canonical=[IO.File]::ReadAllText((Join-Path (Get-Location) '.agent/context/handoffs/2026-10-16-tts-voice-panel-implementation-critical-review.md'))
  $original=[IO.File]::ReadAllText('C:/Temp/av-kit/dispatch/s35-exec-review-report.md')
  $anchor='> **Review Mode:** execution, ledger round 3 of 6.'
  $left=$canonical.Substring($canonical.IndexOf($anchor))
  $right=$original.Substring($original.IndexOf($anchor))
  Write-Output ('round3_body_exact_text_equal='+($left -ceq $right))
  Write-Output ('round3_body_equal_normalized_LF='+($left.Replace("`r`n","`n").TrimEnd() -ceq $right.Replace("`r`n","`n").TrimEnd()))
  $canonicalFm=($canonical -split '---',3)[1]
  $originalFm=($original -split '---',3)[1]
  Write-Output ('frontmatter_exact_text_equal='+($canonicalFm -ceq $originalFm))
  Get-FileHash -LiteralPath 'C:/Temp/av-kit/dispatch/s35-exec-review-report.md' -Algorithm SHA256 | Format-List
}
```

Decisive output:

```text
round3_body_exact_text_equal=True
round3_body_equal_normalized_LF=True
frontmatter_exact_text_equal=True
original round 3 report SHA256:
253F3A37E34EBB68F68BFB6A8AAC8BE1628FEA3879BA3E93BE1992D5DF16C88B
```

Supporting reads covered the review schema/template, workflow, local guardrails, identity implementation and scope/terminal/completion procedures. A first procedure-read command failed with a PowerShell quoting error (exit 1), then succeeded with literal paths (exit 0); it ran no product code. An initial handoff extraction matched only compact JSON and printed no full records; the explicit rg read above supplied both spaced full records. Git emitted its existing global-ignore permission warning and a registry CRLF advisory; exits and exact identity remained successful.

## Findings

| # | Severity | Blocking | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|
| F1 | High | no | Runtime-query failure handling remains fixed on the unchanged round 3 state. | packages/infrastructure/src/avkit_infra/tts/adapter.py:99 | Retain the failing-query and terminal-cause regressions. | fixed |
| F2 | High | no | Lazy engine-initialization failure handling remains fixed on the unchanged round 3 state. | packages/infrastructure/src/avkit_infra/tts/adapter.py:289 | Retain the engine-import regression and separate ImportError behavior. | fixed |

Both findings retain High confidence, subject deliverable and finding_kind behavior; their original contract was AC-75.9. There are two carried fixed findings, zero open findings, zero blocking findings and no new findings.

## Verdict and Follow-up

**approved — intent achieved yes.** Round 3's approval stands for the exact unchanged bound state. F1 and F2 are explicitly closed by the Prior Pass Summary above.

The orchestrator should append this report verbatim to the existing rolling review, update its frontmatter from this verdict, record ledger round 4, then rerun H1-7a/H1-7b and continue authorized closeout. Those actions were not performed by this reviewer. The temporary report is `C:/Temp/av-kit/dispatch/s35-exec-review-report.md`. This confirmation inherits round 3's stated runtime/evidence limits and makes no fresh suite, physical-GPU or geometry-execution claim.
