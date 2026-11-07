---
date: "2026-11-06"
project: "tts-build-capability"
meu: "MEU-118"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md"
build_plan_section: "bp06"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-06-tts-build-capability-MEU-117-handoff.md"
---

# Handoff: 2026-11-06-tts-build-capability-MEU-118-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-118 `gui-tts-device-options` (`TTS-DEVICE-OPTIONS-IN-CPU-BUILD`, P4, triage D-226). The Settings device select offers only the devices the backend reports for this build, so the shipped CPU build offers `auto` and `cpu`. A stored value it can't offer shows as `auto` and is kept, and the load keeps the device fallback.
**Build Plan Section**: [06 §TTS device options (residual)](../../../docs/build-plan/06-gui.md).
**Predecessor**: [MEU-117 handoff](2026-11-06-tts-build-capability-MEU-117-handoff.md). MEU-117 lists `available` and `reason` beside each row's `devices`, which this MEU reads.

- **Source (D-313, `DEVICE_OPTIONS`).**
  - New `ui/src/renderer/src/features/tts/tts-devices.ts` exports `DEVICE_ORDER` (`:2`, `auto, cuda, cpu, mps`, the `runtime_devices` order), `DEVICE_FLOOR` (`:5`, `auto, cpu`) and `buildDevices` (`:11`).
  - `buildDevices(rows)` is `DEVICE_FLOOR` plus the `devices` of every row that isn't unavailable, in `DEVICE_ORDER` with no repeats. Unknown strings are dropped, and a row without `devices` adds nothing.
  - The report is the catalog the backend already returns (`GET /models/available`), so no route is added.
- **Settings (D-314, `DEVICE_SELECT_VALUE`).**
  - `SettingsPage.tsx` drops the four-value `TTS_DEVICES` literal. The device row reads `useModelsAvailable()` (`:375`), the TTS page's cached query.
  - Once the report arrives, the options are `buildDevices(items)`. While it is pending or has failed, they are `buildDevices([{ devices: [storedDevice] }])`: the floor plus the stored value when it is in `DEVICE_ORDER` (`:379-381`).
  - The select shows the stored value when it is offered, else `auto` (`:382`), and writes `{ device }` only on a user change. So a stored `cuda` in a CPU build shows `auto` and is never rewritten. The load then falls back through `DEVICE_RESOLVE`.
  - In dev, the first catalog read in a backend process now waits for MEU-117's kokoro import, about 3 s (plan, Settings note).
- **TTS page (D-317).** `TTSPage.tsx:275` reads `selectedModel?.devices ?? DEVICE_FLOOR` in place of the literal, so its behaviour is unchanged.
- **Spec text.** 06 `:882` reads "Auto, then CUDA, CPU or MPS as the selected variant reports", and `:1067` says the select offers what the backend reports for this build. 06 gained the MEU-118 Delivered note (row 13).
- **Wire enums unchanged.** `tts-commands.ts` `DEVICE_VALUES` and the MCP `DEVICE_WIRES` validate what a client may send. They aren't options shown to the user.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md) §MEU-118. **Execution authorization:** `USER_EXPLICIT`, 2026-11-06, "proceed", given after the Codex plan review approved in round 1 ([plan-critical-review.md](2026-11-06-tts-build-capability-plan-critical-review.md)), accepting every gate default (`plan_to_exec_gate: human`). The defaults include that Settings reads `/models/available` and that the disabled option keeps its G30 pair.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-118.1 | unit | `ui/tests/unit/tts-devices.test.ts` loads the module through `import.meta.glob`. `buildDevices(undefined)` and `([])` give `DEVICE_FLOOR`. A CPU-only report gives `auto, cpu`, and a report with an ONNX row listing `cuda` gives `auto, cuda, cpu`. An unavailable row's devices are ignored: a PyTorch row with all four, unavailable, plus an ONNX row with `auto, cpu` give `auto, cpu`. Unknown strings are dropped, the order is `DEVICE_ORDER` with no repeats, and a row without `devices` adds nothing beyond the floor. | Local Canon (triage D-226; `DEVICE_PROBE`) | `ui/tests/unit/tts-devices.test.ts:25` | ✅ |
| AC-118.2 | unit | With the catalog answering a CPU-only report, the Settings device select offers exactly `auto, cpu`. With a CUDA report, it offers `auto, cuda, cpu`. Choosing `cpu` sends one `PUT /settings/tts` with `{device: 'cpu'}`. Every option keeps the G30 style. | Local Canon (triage D-226, 06 §TTS device options, "Options") | `ui/tests/unit/settings-tts-device.test.ts:167`, `:184`, `:191` | ✅ |
| AC-118.3 | unit | A stored `cuda` with a CPU-only report shows `auto` and sends no PUT. With the report pending, and again with it answering 500, the options are `auto, cpu` plus the stored `cuda`, and `cuda` shows. | Local Canon (06, "Stored value"; `DEVICE_SELECT_VALUE`) | `ui/tests/unit/settings-tts-device.test.ts:201`, `:211`, `:222` | ✅ |
| AC-118.4 | unit | A guard in `tts-page.behavior.test.ts`, which doesn't import `tts-devices`. A selected row without `devices` lists `auto` and `cpu` on the TTS page, and a row listing `cuda` lists it. | Local Canon (D-317: the fallback reads the selected model's devices) | `ui/tests/unit/tts-page.behavior.test.ts:921` | ✅ |
| AC-118.5 | e2e | In Electron, the Settings seam's `options.catalog` answers `GET /models/available`. A CPU-only report gives `auto, cpu`, and a CUDA report gives `auto, cuda, cpu`. An unavailable PyTorch row with all four devices plus an ONNX row with `auto, cpu` give `auto, cpu`. A stored `cuda` with a CPU-only report shows `auto` with no PUT, and choosing `cpu` PUTs `{device: 'cpu'}`. The control is found by the literal `'settings-leaf-device'`, so `test-ids.ts` doesn't change. | Local Canon (06, "Tests": a Playwright pass against real Electron) | `ui/tests/e2e/settings.test.ts:859`, `:873` (row 12; gate `ui-electron`) | ✅ |
| AC-117 (cross-ref) | — | Owned by the MEU-117 handoff: `available`, `reason`, the 409 and 422 refusals, the disabled TTS row and the packaged and dev checks | plan §MEU-117 | [MEU-117 handoff](2026-11-06-tts-build-capability-MEU-117-handoff.md) | see MEU-117 |
| AC-4, AC-98, AC-115, AC-72 (cross-ref) | — | The amended AC-4.7, AC-98.5 ×2 and AC-115.9 tests and the AC-72.1 regression are MEU-117's | plan §MEU-117 | [MEU-117 handoff](2026-11-06-tts-build-capability-MEU-117-handoff.md) | see MEU-117 |
| AC-94 (cross-ref) | regression | AC-94.2 to AC-94.4 still pass, and AC-118.2 asserts the G30 pair on every Settings device option | plan §Device options | `ui/tests/unit/theme-selects.test.tsx:202`, `:235`, `:265` (row 11; gate `ui-tests`) | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged, so the byte-hash tests AC-51.6 and AC-81.13 pass | plan §Files Modified | `ui/tests/unit/layout-primitives.test.ts:200`, `ui/tests/unit/capture-action-row.test.ts:710` (row 11; gate `ui-tests`) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-118.1 (5 tests) | Row 10: "AC-118.1 tts-devices.ts exists: expected [] to have a length of 1 but got +0" in each, because the module doesn't exist yet | Row 11: pass | `tts-devices.test.ts:25` |
| AC-118.2 (3 tests), AC-118.3 (3 tests) | Row 10: the setup sync's first check fails in each, "expected undefined to be 'success'" (and `'pending'`, `'error'` for the two AC-118.3 fallback tests): the unchanged page never queries `GET /models/available`, so the option assertions don't run | Row 11: pass | `settings-tts-device.test.ts:167-233` |
| AC-118.4 | A guard: passes in Red by design and isn't required | Row 11: pass | `tts-page.behavior.test.ts:921` |
| AC-118.5 | No Red of its own: its negative is row 10's AC-118.2 Red | Row 12: pass in Electron | `settings.test.ts:859`, `:873` |

- **Row 10 Red:** 11 failed and 33 passed in 3 files, exit 1. The 33 passes are the existing `tts-page.behavior` tests and the AC-118.4 guard. `red-check.py` required AC-118.1, AC-118.2 and AC-118.3, and found 0 problems.
- **AC-118.2 and AC-118.3 Red.** These tests fail at the setup sync's check, before the option assertions run. The unchanged page never starts the catalog query, so its state reads `undefined`. That is an assertion failure on the behaviour under test (the page doesn't read the report), not an import or collection error. The Red doesn't print the old four-value list; the plan's negative, "Today it offers all four", is the `TTS_DEVICES` literal that row 11 removed.
- **Green:**
  - Row 11: the full UI unit suite, 112 files, 1163 passed, then the UI typecheck and ESLint (`--max-warnings 0`). No file that row 11 didn't mean to change failed.
  - Row 12: the UI build, then `settings.test.ts` in Electron, 23 passed with the four AC-118.5 tests. The models folder was unchanged (159 files, 0 changes).

Receipts: `C:/Temp/av-kit/s51-devices-red.txt` (with `.exit`), `s51-devices-red-check.txt`, `s51-devices-green.txt`, `s51-devices-types.txt`, `s51-devices-lint.txt`, `s51-r12-build.txt`, `s51-r12-e2e.txt`, `s51-r12-models.txt`, `s51-r12-types.txt`, `s51-r12-lint.txt`, `s51-resolve.txt`, `s51-r13-*.txt`, the gate's `s51-gate-h1.txt` and `s51-D6-<id>.txt`, `s51-h1-2-flake-loop.txt`, `s51-h1-2-ui-full-1.txt` and `-2.txt`, and `drift-check.txt` and `openapi-check.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s51-118-devices-red", "command": "rtk proxy npm --prefix ui run test -- tests/unit/tts-devices.test.ts tests/unit/settings-tts-device.test.ts tests/unit/tts-page.behavior.test.ts *> C:/Temp/av-kit/s51-devices-red.txt; then red-check.py --require AC-118.1 --require AC-118.2 --require AC-118.3 (abridged from task.md row 10's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-118 Red: AC-118.1 to AC-118.3 against the unchanged Settings page with no tts-devices module, and the AC-118.4 guard", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 10", "output": "Test Files 2 failed | 1 passed (3); Tests 11 failed | 33 passed (44). Decisive: AssertionError: AC-118.1 tts-devices.ts exists: expected [] to have a length of 1 but got +0 (5 tests); AssertionError: expected undefined to be 'success' (AC-118.2 x3, AC-118.3 stored cuda), 'pending' and 'error' (the two AC-118.3 fallback tests). red-check: 1 receipt(s), 3 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-118-devices-green", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test *> C:/Temp/av-kit/s51-devices-green.txt; then npm --prefix ui run typecheck *> C:/Temp/av-kit/s51-devices-types.txt and npm --prefix ui run lint *> C:/Temp/av-kit/s51-devices-lint.txt (abridged from task.md row 11's Validation cell, run from P:/av-kit; the typecheck and lint ran without rtk proxy)", "cwd": "P:/av-kit", "scope": "MEU-118 Green: the full UI unit suite, because every file that renders SettingsPage must still pass, then the UI typecheck and ESLint", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 11", "output": "Test Files 112 passed (112); Tests 1163 passed (1163). tsc --noEmit exit 0. eslint src/ tests/ --max-warnings 0 exit 0."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-118-e2e", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s51-r12-build.txt; then rtk proxy npm --prefix ui run test:e2e -- tests/e2e/settings.test.ts *> C:/Temp/av-kit/s51-r12-e2e.txt; then models-snapshot.py --compare models-before.json *> C:/Temp/av-kit/s51-r12-models.txt (abridged from task.md row 12's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-118 AC-118.5 in real Electron through the Settings seam with options.catalog, with the rest of settings.test.ts, and the real models folder untouched", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 12", "output": "UI build exit 0. 23 passed (41.7s), including AC-118.5 a CPU-only report offers auto, cpu; a CUDA report offers auto, cuda, cpu; an unavailable PyTorch row with all four devices plus an ONNX row with auto and cpu offers auto, cpu; a stored cuda with a CPU-only report shows auto with no PUT, and choosing cpu PUTs it. models-snapshot: 159 file(s) recorded, 0 change(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-row13-hub", "command": "task.md row 13's Validation cell, run from P:/av-kit through an extracted .ps1 (abridged): the issue-resolve receipt check, rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s51-r13-render.txt, rtk proxy uv run python tools/issue_triage.py render --check *> C:/Temp/av-kit/s51-r13-issues.txt, the two issue statuses and the grouping row", "cwd": "P:/av-kit", "scope": "Row 13 hub, shared by MEU-117 and MEU-118: the 03 and 06 Delivered notes, both MEUs ready_for_review, both issues resolved through issue-resolve.py, and grouping row 51 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 71d0d3a plus rows 1 to 13", "output": "issue-resolve: 10 parsed fields changed (issues[82] and issues[98] status, verification, resolution_path), 67 of 67 decision logs read, 0 problem(s). Drift check passed. OK: known-issues.md is up-to-date. Statuses TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME resolved, TTS-DEVICE-OPTIONS-IN-CPU-BUILD resolved. Grouping tracker names the plan: True."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-06-tts-build-capability/session-gate.ps1 *> C:/Temp/av-kit/s51-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s51-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 13 and the AC-118.2 setup-sync fix (run 2; run 1 failed at ui-tests, see Execution notes): identity, every static check, both full suites, the UI build, OpenAPI, the MCP types, tests and build, both renders, the targeted Electron specs, the package build, the capability smoke on a fresh copy of the onedir outside the checkout, the strict dev PyTorch check and the models snapshot, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (30 rows, 28 fully checked, 2 view_file exempt); scope-paths exit=0 (changed paths: 53, outside scope: [], head moved: False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1274 passed); ui-tests exit=0 (112 files, 1163 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-tests exit=0 (35 files, 470 passed); mcp-build exit=0; state-render exit=0 (126 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ui-electron exit=0 (45 passed: settings 23, tts-generate 22); package-build exit=0; smoke-capability exit=0 (PASS: smoke_packaged_tts capability, failed_check null); dev-pytorch exit=0 (PASS: dev-pytorch-check strict, kokoro-pt-fp32 on cpu, wav_samples 41400); models-untouched exit=0 (159 files, 0 changes); identity-after exit=0 (tested_state before = after); mcp-audit and build-record skipped; baseline failures excused: py [], ui [], mcp []; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/drift-check.txt 2>&1 (H1-3's cell, run from Git Bash, so its *> became > 2>&1)", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here; row 13 set both MEUs ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62", "output": "Drift check passed: SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s51-h1-4-openapi", "command": "rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json > C:/Temp/av-kit/openapi-check.txt 2>&1 (H1-4's cell, run from Git Bash, so its *> became > 2>&1)", "cwd": "P:/av-kit", "scope": "H1-4: packages/api changed in this session, so the committed OpenAPI document is checked against the app", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62", "output": "exit 0; check_openapi prints nothing when openapi.committed.json matches the live schema"}
```

### Quality Gate Results

`s51-gate-h1-2` is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors, 0 warnings; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 30 rows (28 fully checked, 2 `view_file` exempt); scope-paths found 53 changed paths, none outside scope, and HEAD 71d0d3a did not move; the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** pytest 1274 passed (baseline 1265); Vitest 1163 passed in 112 files (baseline 1144 in 109); MCP tests 470 passed in 35 files (baseline 466 in 34). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render and the issue render match the files on disk.
- **Runtime:** the targeted Electron specs passed (45 of 45: `settings` 23, `tts-generate` 22). `package-build` built the onedir, and `smoke-capability` passed on a fresh copy of it outside the checkout. `dev-pytorch` passed strict (`kokoro-pt-fp32` on `cpu`, 41400 samples), and the real models folder was unchanged (159 files).
- **Skipped:** `mcp-audit` (live network and YouTube, which the brief forbids) and `build-record` (no installer build).
- **Identity:** the tested_state was the same before and after the gate: `71d0d3a40f9bb2a3ab37ab9c2880d96079ced0b8+bef8c81bc7de7721d0ce8117c549d11d97ebed4690501f6d21143656ef2f6a62`. After H1-3 and H1-4, `identity.py --state-only` re-derives the same value.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/tts/tts-devices.ts` | new | `DEVICE_ORDER`, `DEVICE_FLOOR`, `buildDevices` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | `TTS_DEVICES` removed; the device options and value from `useModelsAvailable()`. CRLF kept |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modified | `DEVICE_FLOOR` in place of the literal. Shared with MEU-117 (the disabled row). CRLF kept |
| `ui/tests/unit/tts-devices.test.ts`, `ui/tests/unit/settings-tts-device.test.ts` | new | AC-118.1; AC-118.2 and AC-118.3 |
| `ui/tests/unit/tts-page.behavior.test.ts` | modified | The AC-118.4 guard. Shared with MEU-117 (AC-117.12) |
| `ui/tests/e2e/settings.test.ts` | modified | `options.catalog` and `options.device` on the seam; AC-118.5. CRLF kept |
| `docs/build-plan/06-gui.md` | modified | `:882`, `:1067` and the Delivered note. CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, `known-issues.yaml`, `known-issues.md`, `triage-output.yaml`, the grouping file | modified | Row 13, shared with MEU-117 (see its Changed Files) |
| Plan folder | new or modified | Shared with MEU-117 |

```diff
-const TTS_DEVICES = ['auto', 'cuda', 'cpu', 'mps'] as const
 ...
   const tts = ttsQuery.data
+  const modelsQuery = useModelsAvailable()
+  const storedDevice = tts?.device ?? 'auto'
+  // DEVICE_OPTIONS (D-314): what this build reports; until the report arrives, or if it fails,
+  // the floor plus the stored value. A stored value it can't offer shows as auto and is kept.
+  const deviceOptions = modelsQuery.isSuccess
+    ? buildDevices(modelsQuery.data.items)
+    : buildDevices([{ devices: [storedDevice] }])
+  const deviceValue = deviceOptions.includes(storedDevice) ? storedDevice : 'auto'
 ...
             testId="settings-leaf-device"
-            options={TTS_DEVICES.map((option) => ({ value: option, label: option }))}
-            value={tts?.device ?? 'auto'}
+            options={deviceOptions.map((option) => ({ value: option, label: option }))}
+            value={deviceValue}
```

The excerpt is abridged. `SettingsPage.tsx:375-382` and `:840-841` are the source.

---

## Codex Validation Report

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

Round 1 of loop `s51-execution-2026-11-06-tts-build-capability` returned `approved`, intent achieved `yes`, with no findings ([implementation-critical-review.md](2026-11-06-tts-build-capability-implementation-critical-review.md)). Its Q8 records two notes, neither a finding:

- **Identity.** In the reviewer's sandbox, `identity.py --state-only` listed `.claude/settings.local.json` as untracked and gave another value. That file dates from 2026-10-10 and is ignored by the user-level `~/.config/git/ignore`, which the sandbox doesn't read. With that one path left out, the reviewer reproduced the gate's tested_state exactly, and this shell's `identity.py --state-only` gives it unchanged.
- **Register note.** The register-resolve execution note in the MEU-117 handoff named the wrong issue for `.issues[82]`. It is `TTS-DEVICE-OPTIONS-IN-CPU-BUILD`, and the note is corrected.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A `/tts/devices` route | out-of-scope | — | D-313: the catalog already carries the report |
| `tts-commands.ts` `DEVICE_VALUES` and the MCP `DEVICE_WIRES` | out-of-scope | — | Plan §Device options: they validate client input and aren't options shown to the user |
| Commit and push | out-of-scope | — | Waits for Mat's direction (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files from the task cells, because the cells' `*>` needs PowerShell. Row 11's typecheck and lint ran as `npm --prefix ui run typecheck` and `lint` without `rtk proxy`; both exit 0, and the gate's `ui-types` and `ui-lint` ran them again.
- **Row 12 checks.** Row 12 edited `settings.test.ts`, so it also ran the UI typecheck and ESLint (`s51-r12-types.txt`, `s51-r12-lint.txt`), both exit 0.
- **Settings seam.** `installSettingsSeam` gained `options.device` as well as the plan's `options.catalog`, so the AC-118.5 stored-`cuda` test can seed the stored device. Without a catalog the seam doesn't answer `/models/available`, as before.
- **Existing device lookups.** The plan's AC-118.5 cites `settings.test.ts:297` and `:304` as existing `'settings-leaf-device'` lookups. They aren't. AC-118.5 uses the literal itself, and `test-ids.ts` is unchanged.
- **Gate run 1.** It failed at `ui-tests` on one test, `AC-118.2 a CUDA report offers auto, cuda and cpu` (`s51-gate-h1-run1.txt`, `s51-D6-ui-tests-run1.txt`). The select listed `auto, cpu`, the page's list before the report arrives. TanStack Query tells its observers about a new state on a `setTimeout(0)`, and the test's setup sync, `settled()`, flushed only a microtask after it saw the state, so the assertion could run before the page re-rendered. Only the CUDA test can see the stale render, because the CPU tests' early and final lists are both `auto, cpu`. Row 11's full suite had passed (1163).
  - The fix changes only that setup sync (`ui/tests/unit/settings-tts-device.test.ts:100-108`): after the state check it waits for a `setTimeout(0)` inside `act`. No assertion and no source file changed. The file then passed 15 runs of 15 on its own (`s51-h1-2-flake-loop.txt`) and the full UI suite twice (112 files, 1163 passed each, `s51-h1-2-ui-full-1.txt` and `-2.txt`).
  - The whole gate was rerun (run 2), and `s51-gate-h1-2` is that run. Run 1's static steps and `py-tests` (1274) had passed.
- **H1-3 and H1-4.** They ran from Git Bash, so each cell's `*>` became `> 2>&1`. The first `identity.py --state-only` after them read another value, because that shell had `ELECTRON_RUN_AS_NODE=1`, which the runtime identity hashes. With it unset, as the gate and H1-6b set it, the value equals the gate's.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Initial MEU-118 handoff after H1-2 |
| Reviewed | 2026-11-06 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 1 `approved`, from the canonical report |
