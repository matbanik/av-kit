---
date: "2026-11-07"
project: "tts-load-fp16"
meu: "MEU-120"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md"
build_plan_section: "bp06"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-06-tts-load-fp16-MEU-120-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-120 `gui-models-dir-probe` (`MODELS-DIR-DOCS-AND-PROBE-MISMATCH`, triage D-222). The desktop app's setup readiness now reads the backend's models folder, `~/.avkit/models`, when no `tts.models_directory` is stored, and its writable probe creates no folder.
**Build Plan Section**: [06 §Models folder probe (residual)](../../../docs/build-plan/06-gui.md), Delivered note at `:1574`.
**Predecessor**: none. The [MEU-119 handoff](2026-11-06-tts-load-fp16-MEU-119-handoff.md) and the [MEU-121 handoff](2026-11-06-tts-load-fp16-MEU-121-handoff.md) are the same plan's other MEUs.

- **Default (rows 3, 4; D-326, D-328, `MODELS_DEFAULT`).**
  - `ui/src/main/setup-readiness.ts` exports `DEFAULT_MODELS_DIRECTORY = '~/.avkit/models'` (`:51`), the backend's `tts.models_directory` default in `services/settings.py:67`.
  - `defaultModelsDirectory()` (`:53-55`) takes no argument and returns `expandUserPath(DEFAULT_MODELS_DIRECTORY)`.
  - `readTtsModelsDirectory` uses it at both fallbacks (`:64`, `:81`): no database, and a database without the row or that can't be read. A stored value still wins, as before.
  - AC-120.1 reads the backend's `SettingSpec` from `settings.py` in Vitest, so a change to either side fails the test.
- **Probe (rows 3, 4; D-327, `DIR_PROBE`).**
  - `probeModelsDirWritable` (`:101-117`) loses its `mkdirSync` and the import. An existing folder gets the write-and-delete probe, as before.
  - A missing folder gets the probe in its nearest existing folder (`nearestExistingEntry`, `:85-99`), which walks `dirname` up while the error is `ENOENT` or `ENOTDIR`.
  - A file on the way, another error, or a walk that reaches the root reads `false`.
  - So a fresh install reports the models folder ready when the home folder is writable. The backend creates `~/.avkit/models` at its first download.
- **Unchanged.** `index.ts` and `ipc.ts` don't change: `probeSetupReadiness` keeps its signature (`:133`), and the `get-setup-readiness` IPC keeps `noPayloadSchema` (`ipc-strict-census.test.ts` in row 4). No files move, and a stored `tts.models_directory` is kept as it is (D-222 "No move").
- **Electron (row 5).** The Settings E2E (AC-58.12) runs unchanged on the built app with its temporary `AVKIT_APP_DATA`. With no stored setting, its readiness probe now reads the real `~/.avkit/models`, and the models snapshot after it found no change, so no probe file was left there.
- **Spec text.** 06 gained the MEU-120 Delivered note (`:1574-1579`, row 12).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md) §MEU-120. **Execution authorization:** `USER_EXPLICIT`, 2026-11-07, "D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed", given after the Codex plan review approved in round 4 ([plan-critical-review.md](2026-11-06-tts-load-fp16-plan-critical-review.md)); recorded in [human-gate-decision.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/human-gate-decision.md) (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

Each Vitest title begins `AC-120.<n>`, and each test works in its own `mkdtempSync` folder.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-120.1 | contract | `DEFAULT_MODELS_DIRECTORY` exists and equals the `tts.models_directory` default read from `settings.py` | Local Canon: triage D-222 ("Tied") | `ui/tests/unit/setup-readiness.test.ts:111` | ✅ |
| AC-120.2 (amended) | unit | "the default models folder is the backend's": `defaultModelsDirectory()` is `join(homedir(), '.avkit', 'models')`, no longer `{appData}/models` | Local Canon: triage D-222 ("Default") | `setup-readiness.test.ts:57` | ✅ |
| AC-120.3 | unit | `readTtsModelsDirectory` with no database, and with a database that has no row, returns that default | Local Canon: triage D-222 | `setup-readiness.test.ts:122` | ✅ |
| AC-120.4 | unit | A missing folder two levels under a writable folder reads `true`; afterwards the intermediate folder doesn't exist and the writable folder is empty | Local Canon: triage D-222 ("No empty folder"); D-327 | `setup-readiness.test.ts:135` | ✅ |
| AC-120.5 | unit | A missing folder under a regular file reads `false` and creates nothing (guard, passes in Red) | Local Canon: D-327 | `setup-readiness.test.ts:149` | ✅ |
| AC-120.6 | unit | An existing folder reads `true` and holds no probe file afterwards (guard, passes in Red) | Local Canon: D-327 | `setup-readiness.test.ts:161` | ✅ |
| AC-58 (cross-ref) | E2E | AC-58.12's readiness count and card pass unchanged on the built app, now probing `~/.avkit/models`; the real models folder is unchanged afterwards | plan §MEU-120 | `ui/tests/e2e/settings.test.ts:269`, `:298`, `:323` (row 5; gate `ui-electron`) | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged, so the byte-hash tests AC-51.6 and AC-81.13 pass | plan §Files Modified | `ui/tests/unit/layout-primitives.test.ts:200`, `ui/tests/unit/capture-action-row.test.ts:710` (gate `ui-tests`) | ✅ |
| AC-100 (cross-ref) | — | Named in the plan only as `red-check.py`'s boundary example (`AC-100.7` never matches `AC-100.70`); row 3 requires the amended test by its full title for that reason | plan §Verification Plan | gate `ui-tests` | ✅ |
| AC-75, AC-115, AC-117, AC-119 (cross-ref) | — | Owned by the MEU-119 handoff (the load order, the amended AC-75.9, the home-folder scrub and the AC-115 and AC-117.8 regressions) | plan §MEU-119 | [MEU-119 handoff](2026-11-06-tts-load-fp16-MEU-119-handoff.md) | see MEU-119 |
| AC-63, AC-121 (cross-ref) | — | Owned by the MEU-121 handoff (`PRESELECT_ORDER`, the sentence smoke and the FP16 spike; AC-63.x holds unchanged) | plan §MEU-121 | [MEU-121 handoff](2026-11-06-tts-load-fp16-MEU-121-handoff.md) | see MEU-121 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-120.1, AC-120.2 | Row 3: `expected {…} to have property "DEFAULT_MODELS_DIRECTORY"`: each test first asserts the new export exists | Row 4: pass | `setup-readiness.test.ts:57`, `:111` |
| AC-120.3 | Row 3: the deep-equal against `['<home>\.avkit\models', …]` failed: today both fallbacks return `{appData}/models` | Row 4: pass | `:122` |
| AC-120.4 | Row 3: received `entries ["a"]` and `intermediate true` against `[]` and `false`: today the probe creates the folder | Row 4: pass | `:135` |
| AC-120.5, AC-120.6 | Guards: pass in Red by design | Row 4: pass | `:149`, `:161` |

- **Row 3 Red:** `Tests 4 failed | 6 passed (10)` in `setup-readiness.test.ts`. The 6 passes are AC-120.5, AC-120.6 and the file's four other tests. `red-check.py` required AC-120.1, the amended AC-120.2 by its full title ("AC-120.2 the default models folder is the backend's"), AC-120.3 and AC-120.4, and found 0 problems.
- Every failure is the decisive assertion, never a collection or import error. AC-120.1 and AC-120.2 reach the export through `import * as readiness`, so its absence fails an assertion and not the import.
- **Row 4 Green:** `Tests 11 passed (11)` in 2 files, `setup-readiness.test.ts` and `ipc-strict-census.test.ts`. The typecheck and ESLint (`--max-warnings 0`) passed.
- **Row 5:** the UI build passed, and the Settings E2E passed 23 of 23 (33.8s) on the built app, AC-58.12's three tests among them. The models snapshot then found 159 files and 0 changes.

Receipts: `C:/Temp/av-kit/s52-probe-red.txt` (with `.exit`), `s52-probe-red-check.txt`, `s52-probe-green.txt`, `s52-probe-types.txt`, `s52-probe-lint.txt`, `s52-r5-build.txt`, `s52-r5-e2e.txt`, `s52-r5-models.txt`, `s52-resolve.txt`, `s52-r12-*.txt`, run 1's `s52-gate-r1/`, gate run 2's `s52-gate-h1-r2.txt` and `s52-D6-<id>.txt`, and `drift-check.txt` and `openapi-check.txt`. The row 3 Red receipt shows the real home path in AC-120.3's expected value, so it is cited here and not pasted.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s52-120-probe-red", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test -- tests/unit/setup-readiness.test.ts *> C:/Temp/av-kit/s52-probe-red.txt; then red-check.py --require on AC-120.1, \"AC-120.2 the default models folder is the backend's\", AC-120.3 and AC-120.4 *> C:/Temp/av-kit/s52-probe-red-check.txt (abridged from task.md row 3's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-120 Red: AC-120.1 to AC-120.6 and the amended AC-120.2 against the unchanged setup-readiness.ts, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 (baseline.sha) plus rows 1 to 3", "output": "Tests 4 failed | 6 passed (10). Decisive: expected {...} to have property \"DEFAULT_MODELS_DIRECTORY\" for AC-120.1 and AC-120.2; the deep-equal against the home folder's .avkit\\models failed for AC-120.3; entries [\"a\"] and intermediate true against [] and false for AC-120.4. red-check: 1 receipt(s), 4 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-120-probe-green", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test -- tests/unit/setup-readiness.test.ts tests/unit/ipc-strict-census.test.ts *> C:/Temp/av-kit/s52-probe-green.txt; then rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/s52-probe-types.txt and rtk proxy npm --prefix ui run lint *> C:/Temp/av-kit/s52-probe-lint.txt (abridged from task.md row 4's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-120 Green: the readiness tests and the IPC strict census, with the UI typecheck and ESLint", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 4", "output": "Test Files 2 passed (2); Tests 11 passed (11). tsc --noEmit exit 0. eslint src/ tests/ --max-warnings 0 exit 0."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-120-e2e", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s52-r5-build.txt; then rtk proxy npm --prefix ui run test:e2e -- tests/e2e/settings.test.ts *> C:/Temp/av-kit/s52-r5-e2e.txt; then models-snapshot.py --compare models-before.json *> C:/Temp/av-kit/s52-r5-models.txt (abridged from task.md row 5's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-120 Electron check: the Settings spec unchanged on the built app with its temporary AVKIT_APP_DATA, whose readiness probe now reads ~/.avkit/models (AC-58.12), then the real models folder against row 0's snapshot", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 5", "output": "vite build: built in 4.26s. Playwright: 23 passed (33.8s), AC-58.12's three tests and AC-118.5 among them. models-snapshot: 159 file(s) recorded, 0 change(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-row12-hub", "command": "task.md row 12 (abridged), run from P:/av-kit: its task text runs rtk proxy uv run python docs/execution/plans/2026-11-06-tts-load-fp16/issue-resolve.py --issue TTS-FAILED-LOAD-DROPS-MODEL --issue MODELS-DIR-DOCS-AND-PROBE-MISMATCH --issue TTS-ONNX-FP16-NONFINITE-AUDIO --set-file C:/Temp/av-kit/s52-resolve.json --expect-sha256 $sha *> C:/Temp/av-kit/s52-resolve.txt, then issue_triage.py render and triage; its Validation cell, through an extracted .ps1, checks C:/Temp/av-kit/s52-resolve.txt for '^issue-resolve: 0 problem', then runs rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s52-r12-render.txt, rtk proxy uv run python tools/issue_triage.py render --check *> C:/Temp/av-kit/s52-r12-issues.txt, the three issue statuses and the grouping row *> C:/Temp/av-kit/s52-r12-status.txt", "cwd": "P:/av-kit", "scope": "Row 12 hub, shared by MEU-119, MEU-120 and MEU-121: the 03 and 06 Delivered notes, the three MEUs ready_for_review, two issues resolved and the FP16 issue's verification through issue-resolve.py, and grouping row 52 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12", "output": "decision logs read: 67 of 67; parsed fields changed: 13 (issues[99] and issues[100] status, verification.last_checked, method, result and resolution_path; issues[110] verification.last_checked, method and result); issue-resolve: 0 problem(s). Drift check passed: SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content. OK: known-issues.md is up-to-date. ['resolved', 'resolved', 'open']. grouping tracker names the plan: True."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-120-c1-red", "command": "rtk proxy npm --prefix ui run test -- tests/unit/setup-readiness.test.ts *> C:/Temp/av-kit/s52-c1-red.txt; then red-check.py --require \"AC-120.4 fault: a write that throws after creating the probe leaves no file\" --require \"AC-120.6 fault: a failed access check after the write keeps no probe file\" C:/Temp/av-kit/s52-c1-red.txt *> C:/Temp/av-kit/s52-c1-red-check.txt (abridged from task.md row C1's Validation cell, run from P:/av-kit through an extracted .ps1)", "cwd": "P:/av-kit", "scope": "Review round 1 F1, Red (D-340, D-342): the two fault cases under the AC-120.4 and AC-120.6 ids against the unchanged probeModelsDirWritable, with node:fs mocked so that one writeFileSync or accessSync call throws after the write, and red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12 and C1", "output": "Tests 2 failed | 10 passed (12) in setup-readiness.test.ts, exit 1. Decisive, in both new cases: AssertionError: expected { writable: false, …(1) } to deeply equal { writable: false, entries: [] }, so each probe answered false and left its .write-probe file in the folder. red-check: 1 receipt(s), 2 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-120-c2-green", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test -- tests/unit/setup-readiness.test.ts tests/unit/ipc-strict-census.test.ts *> C:/Temp/av-kit/s52-c2-green.txt; then rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/s52-c2-types.txt and rtk proxy npm --prefix ui run lint *> C:/Temp/av-kit/s52-c2-lint.txt (abridged from task.md row C2's Validation cell, run from P:/av-kit through an extracted .ps1)", "cwd": "P:/av-kit", "scope": "Review round 1 F1, Green (D-342): the probe's catch removes its file with rmSync(probe, { force: true }) in its own try before it answers false (setup-readiness.ts:115-122); the readiness tests and the IPC strict census, with the UI typecheck and ESLint", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12, C1 and C2", "output": "Test Files 2 passed (2); Tests 13 passed (13). tsc --noEmit exit 0. eslint src/ tests/ --max-warnings 0 exit 0."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-c5-registers", "command": "task.md row C5 (abridged), run from P:/av-kit in Git Bash: rtk proxy uv run python docs/execution/plans/2026-11-06-tts-load-fp16/issue-resolve.py --issue GUI-MODELS-PROBE-LEFTOVER-FILE --issue SMOKE-TTS-WAV-HEADER-TRUSTED --set-file C:/Temp/av-kit/s52-c5-resolve.json --expect-sha256 $SHA > C:/Temp/av-kit/s52-c5-resolve.txt 2>&1, then the two issues filed and MEU-127 registered through issue_triage's model and meu-status.yaml; its Validation cell, through an extracted .ps1, checks the resolve receipt for '^issue-resolve: 0 problem', then runs rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s52-c5-render.txt, rtk proxy uv run python tools/issue_triage.py render --check *> C:/Temp/av-kit/s52-c5-issues.txt, and the five issue statuses, the FP16 issue's meu_links and the MEU-127 entry *> C:/Temp/av-kit/s52-c5-status.txt", "cwd": "P:/av-kit", "scope": "Row C5 hub, shared by MEU-119, MEU-120 and MEU-121: F1's and F2's issues resolved, CONSOLE-HOME-SCRUB-SHORT-FORM (D-337) and TRACKED-FILES-HOLD-HOME-PATH (D-344) filed, MEU-127 svc-tts-fp16-phase-guard registered (D-336, D-345: meu-status.yaml, the P2 band, matrix row 3.18, 03's residual section and the FP16 issue's meu_links), and the MEU-120 and MEU-121 notes", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12 and C1 to C5", "output": "decision logs read: 67 of 67; register sha256 before=809d53e4f9189ce5bb7b22e8c2ed1887e337e9f5b68c7d54d5747a746b4763e7, after=05152c73e598cfb2ee00c75e508e03a99ccd8a66febab97a901db812eeb1c788; parsed fields changed: 8 (issues[112] and issues[113] resolution_path, status, verification.method and verification.result); issue-resolve: 0 problem(s). Drift check passed: SSOT loaded (127 MEUs, 12 phases), rendered regions match on-disk content. OK: known-issues.md is up-to-date. ['resolved', 'resolved', 'open', 'open', 'open'] ['MEU-62', 'MEU-72', 'MEU-121', 'MEU-127'] MEU-127 registered: True."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-c5-register-fix", "command": "python -I -X utf8 s52_c5_fix_online.py (a one-off script outside the checkout, run from P:/av-kit), then python -I -X utf8 tools/issue_triage.py render --check and python -I -X utf8 tools/meu_status.py render --check", "cwd": "P:/av-kit", "scope": "Row C5 correction, after the first attempt of gate run 2: SMOKE-TTS-WAV-HEADER-TRUSTED's resolution_path said that the online and offline phases refuse 8,000 or fewer samples. phase_online generates nothing (smoke_packaged_tts.py:223), so the text now names the offline phase only. The script refuses any other change to the parsed register and saves a copy through model.save to prove the bytes", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b6c3895 plus rows 1 to 12 and C1 to C6's first attempt", "output": "SMOKE-TTS-WAV-HEADER-TRUSTED resolution_path corrected; parsed issues otherwise equal; model.save round trip identical: True. known-issues.yaml: crlf=0 lf_only=4176, sha256 0bcd5af73a865097f2353d1f9ad9bb51c503c6924f94629c6f6f8e0ed34285fa. OK: known-issues.md is up-to-date. Drift check passed: SSOT loaded (127 MEUs, 12 phases), rendered regions match on-disk content."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-gate-c6", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-06-tts-load-fp16/session-gate.ps1 *> C:/Temp/av-kit/s52-gate-h1-r2.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s52-gate-h1-r2.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "Row C6, gate run 2 (D-341): the registered D6 gate on the whole tree after rows C1 to C5 and the register correction, with the new tooling test, the matrix and the files of Mat's instruction change added to its allowed set: identity, every static check, both full suites, the UI build, OpenAPI, the MCP types, tests and build, both renders, the targeted Electron specs, the package build, the sentence smoke on INT8 under row C4's payload check on a fresh copy of the onedir outside the checkout, the strict dev PyTorch check and the models snapshot, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (41 rows, 39 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 58, outside scope: [], head moved: False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1296 passed); ui-tests exit=0 (112 files, 1174 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-tests exit=0 (35 files, 470 passed); mcp-build exit=0; state-render exit=0 (127 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ui-electron exit=0 (46 passed); package-build exit=0; smoke-sentences exit=0 (PASS: smoke_packaged_tts sentences, kokoro-onnx-int8, 149 jobs all Done, the shortest WAV 55,200 samples); dev-pytorch exit=0 (PASS: dev-pytorch-check strict); models-untouched exit=0 (159 files, 0 changes); identity-after exit=0 (tested_state before = after); mcp-audit, build-record and smoke-capability skipped; baseline failures excused: py [], ui [], mcp []; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/drift-check.txt 2>&1 (H1-3's cell, run from Git Bash, so its *> became > 2>&1)", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here; row 12 set the three MEUs ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055", "output": "Drift check passed: SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s52-h1-4-openapi", "command": "rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json > C:/Temp/av-kit/openapi-check.txt 2>&1 (H1-4's cell, run from Git Bash, so its *> became > 2>&1)", "cwd": "P:/av-kit", "scope": "H1-4: packages/api doesn't change in this session; the OpenAPI check runs as a guard, and any drift would be S6", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055", "output": "exit 0; check_openapi prints nothing when openapi.committed.json matches the live schema"}
```

### Quality Gate Results

`s52-gate-c6` (row C6, gate run 2) is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors, 0 warnings; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 41 rows (39 fully checked, 2 `view_file` exempt; rows C1 to C10 are the 10 more); scope-paths found 58 changed paths, none outside scope, and HEAD b6c3895 did not move (D-341 added the tooling test, the matrix and the files of Mat's instruction change to the allowed set); the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** Vitest 1174 passed in 112 files (baseline 1163: AC-120.1, AC-120.3 to AC-120.6, AC-121.1 to AC-121.4 and row C1's two fault cases are the 11 new; AC-120.2 is amended in place); pytest 1296 passed (baseline 1274); MCP tests 470 passed in 35 files (baseline 470). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render and the issue render match the files on disk.
- **Runtime:** the targeted Electron specs passed (46 of 46: `settings` 23, `tts-generate` 23). `package-build` built the onedir, and `smoke-sentences` passed 149 of 149 jobs on `kokoro-onnx-int8` on a fresh copy of it outside the checkout. `dev-pytorch` passed strict, and the real models folder was unchanged (159 files).
- **Skipped:** `mcp-audit` (live network and YouTube, which the brief forbids), `build-record` (no installer build) and `smoke-capability` (the plan's §Out of Scope: MEU-125's rc.2 gate repeats it).
- **Identity:** the tested_state was the same before and after the gate: `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e`. Row C7's `identity.py --state-only` re-derives the same value with `ELECTRON_RUN_AS_NODE` unset.
- **Earlier runs.** Run 1 (H1-2) passed every step on `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055`, the tree review round 1 read; its receipts are in `C:/Temp/av-kit/s52-gate-r1/`. Run 2's first attempt passed every step on `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+d61c5dfa0f9a1b426fc858d186b39268984f2d14ebba2e9217e60d997ad5485b` (receipts in `C:/Temp/av-kit/s52-gate-r2a/`). Then `s52-c5-register-fix` corrected one sentence in the register, which the identity binds, so the gate ran again and `s52-gate-c6` is that run. `durable_evidence.py --require-full` binds every passing full record to the tree, so neither earlier run is kept as a record.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/main/setup-readiness.ts` | modified | `DEFAULT_MODELS_DIRECTORY`; `defaultModelsDirectory()` takes no argument; both fallbacks use it; `nearestExistingEntry`; the probe creates no folder; `mkdirSync` dropped. CRLF kept |
| `ui/tests/unit/setup-readiness.test.ts` | modified | AC-120.2 amended in place; AC-120.1, AC-120.3 to AC-120.6 added. CRLF kept |
| `docs/build-plan/06-gui.md` | modified | The MEU-120 Delivered note (`:1574-1579`). CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md` | modified | MEU-119 to MEU-121 `ready_for_review` (row 12), shared |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | Two issues resolved and the FP16 issue's verification through `issue-resolve.py` (row 12), shared |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md`, `.agent/context/current-focus.md` | modified | Row 52 `executed` with the plan folder; the Session 52 entry on top. CRLF kept |
| Plan folder scripts and records | new or modified | Shared with MEU-119 and MEU-121; listed in the [MEU-119 handoff](2026-11-06-tts-load-fp16-MEU-119-handoff.md) |

```diff
-export function defaultModelsDirectory(appData: string): string {
-  return join(appData, 'models')
+/** The backend's `tts.models_directory` default in `settings.py` (D-326, D-328). */
+export const DEFAULT_MODELS_DIRECTORY = '~/.avkit/models'
+
+export function defaultModelsDirectory(): string {
+  return expandUserPath(DEFAULT_MODELS_DIRECTORY)
 }
 ...
-  } catch {
-    try {
-      mkdirSync(modelsDir, { recursive: true })
-    } catch {
-      return false
+export function probeModelsDirWritable(modelsDir: string): boolean {
+  // A missing folder is not created (D-327): the backend makes it on its first write, so the
+  // nearest existing folder above it is the one that must be writable.
+  const existing = nearestExistingEntry(modelsDir)
+  if (existing === null || !existing.isDirectory) {
+    return false
+  }
   try {
-    const probe = join(modelsDir, `.write-probe-${randomUUID()}`)
+    const probe = join(existing.path, `.write-probe-${randomUUID()}`)
```

The excerpt is abridged. `ui/src/main/setup-readiness.ts:50-117` is the source.

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
| F1 | Medium | A probe write that creates its file and then throws, or an `accessSync` failure after the write, returns `false` without deleting the file, which can leave `.write-probe-*` in the nearest existing folder, possibly the home folder (non-blocking) | `ui/src/main/setup-readiness.ts:108` | Delete the probe in a `finally` and add fault cases | Fixed on Mat's D-340 ruling (D-342, rows C1 and C2); `GUI-MODELS-PROBE-LEFTOVER-FILE` resolved; round 2 closed it (`fixed`) |

### Verdict

Round 1 of loop `s52-execution-2026-11-06-tts-load-fp16` returned `approved`, intent achieved `yes`, with two Medium findings, both non-blocking ([implementation-critical-review.md](2026-11-06-tts-load-fp16-implementation-critical-review.md)). F1 is MEU-120's and F2 is MEU-121's. D-339 files both as known issues, and D-340 asks Mat whether to fix them before the commit ([closeout-decisions.md](../../../docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md)). The round used 14,996,767 of the loop's 21,000,000 tokens, so the ledger refuses a round 2 until Mat continues the loop (`C:/Temp/av-kit/s52-exec-ledger-state-r1.txt`). The report was validated under `C:/Temp/av-kit` and copied byte for byte; H1-7a and H1-7b passed on the canonical copy (`C:/Temp/av-kit/review-state-check.txt`, `exec-review.txt`).

Mat ruled D-340 with "all recommendations accepted", "proceed with changes", "commit and push" (2026-11-07): fix both now. The recommended continue of 10,000,000 tokens was recorded at 2026-11-07T16:34:19Z (`C:/Temp/av-kit/s52-exec-ledger-continue-1.txt`), so the loop's budget is 31,000,000. Rows C1 to C4 fix F1 and F2, C5 resolves both issues, C6 reran the gate, and round 2 (row C8) rechecked F1 and F2. Round 2 returned `approved`, intent achieved `yes`, with F1 and F2 `fixed` in its Prior Pass Summary and no new finding, using 4,694,911 tokens (19,691,678 of 31,000,000 in all). Row C9's `--approved-state-only` check passed: approved at round 2 of 6, 0 open blocking findings.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The RC1 checklist's models-folder path | dependency | MEU-125 | The plan's §Out of Scope (`implementation-plan.md:423`, 06 `:1572`) |
| Moving files out of `{appData}/models` | out-of-scope | — | Refused: D-222 "No move" (06 `:1570`, `implementation-plan.md:422`) |
| Commit and push | out-of-scope | — | Authorized by Mat's "commit and push" (2026-11-07); it follows round 2's approval and the closeout addenda (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files written from the task cells, because the cells' `*>` needs PowerShell. `ELECTRON_RUN_AS_NODE` was unset for every UI and Electron run.
- **Row 5.** The Settings E2E's readiness probe now writes and deletes its probe file in the real `~/.avkit/models`, which exists on this PC. The models snapshot records each file's name, size and `mtime_ns`, and it found 0 changes after the run, so no probe file was left.
- **Row 3's receipt.** AC-120.3's expected value is the real home folder joined with `.avkit\models`, so the receipt holds the home path. It reaches no app surface; it is Vitest's diff of the test's own expectation.
- **Rows C1 and C2.** C1 mocks `node:fs` so each real call runs unless a test replaces one. Both fault cases failed on the leftover probe file, by assertion. C2 names the probe path before the `try` and removes it in the `catch`; the success path is unchanged.
- **H1-3 and H1-4.** They ran from Git Bash, so each cell's `*>` became `> 2>&1`, with `ELECTRON_RUN_AS_NODE` unset. The gate passed on run 1, and again on run 2 (row C6, D-341) after the review's fixes.

---

## Decision Log

```yaml
decision_log:
  - id: D-342
    stage: execution
    question: "How does the probe remove a file that a failed write or access check leaves behind (review F1)?"
    resolution: autonomous
    class: two-way
    chosen: "Name the probe path before the try; in the catch, rmSync(probe, { force: true }) inside its own try, then return false. The success path keeps its unlinkSync"
    source_tag: Local Canon
    precedents: ["ui/src/main/setup-readiness.ts:102-124 — probeModelsDirWritable", "the review's F1 recommendation — delete the probe on failure and add fault cases"]
    research: { engine: none, sources: [] }
    reasoning: "A finally would also run after the success path's unlinkSync, so the catch is the one place a leftover can exist. force: true makes a write that never created the file a no-op, and the inner try keeps a failed removal from turning false into a throw."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Initial MEU-120 handoff after H1-2 |
| Reviewed | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 1 `approved` from the canonical report; its F1 is filed as `GUI-MODELS-PROBE-LEFTOVER-FILE` (D-339) |
| Amended | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Rows C1, C2 and C5 to C7 on Mat's D-340 ruling: F1 fixed (D-342) and its issue resolved, and gate run 2's `s52-gate-c6` in place of run 1's record |
| Rechecked | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Recorded the Codex review's round 2 `approved` from the canonical report: F1 and F2 `fixed`, no new finding (row C8) |
