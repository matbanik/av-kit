---
date: "2026-11-05"
project: "rc2-fetch-uninstall"
meu: "MEU-114"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md"
build_plan_section: "bp07"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-04-rc2-fetch-uninstall-MEU-114-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-114, the uninstall removes the installer copy (`UNINSTALL-LEAVES-INSTALLER-COPY`, triage D-228). electron-builder's installer leaves a copy of itself at `%LOCALAPPDATA%\av-kit-ui-updater\installer.exe`, and RC1's uninstall left it behind. `customUnInstall` now deletes the copy and removes the folder, except during an in-place update.
**Build Plan Section**: [07 §Uninstall leaves the installer copy (residual)](../../../docs/build-plan/07-distribution.md).
**Predecessor**: none. The [MEU-113 handoff](2026-11-04-rc2-fetch-uninstall-MEU-113-handoff.md) is the same plan's other MEU and holds the shared gate record too.

- **The macro (row 4).** Inside `${ifNot} ${isUpdated}`, `customUnInstall` deletes `$LOCALAPPDATA\${APP_INSTALLER_STORE_FILE}` and removes `$LOCALAPPDATA\av-kit-ui-updater` with a non-recursive `RMDir`, so a folder holding anything else stays. A per-machine install switches to the current user's folders for those two lines and back. `%APPDATA%\av-kit-ui` stays, per `deleteAppDataOnUninstall: false`. AC-61.18's two `DeleteRegValue` lines are unchanged.
- **The pin (row 3).** AC-114.1 to AC-114.3 in `ui/tests/unit/login-item-nsh.test.ts` read the macro's executable lines: the delete and the `RMDir` sit inside the not-updated guard, the folder is `ui/package.json`'s name plus `-updater` (electron-builder's own rule), and nothing recursive is added.
- **The proof on a real install (rows 4 to 6).** `repackage.ps1` rebuilt the NSIS installer from RC1's existing `win-unpacked` with `--prepackaged`, so only the macro changed, and NSIS compiled it under `-WX` (AC-114.4). `install-roundtrip.ps1` then ran four phases on the build PC, with RC1's installer as the negative control (AC-114.5 to AC-114.9).
- **The hub (row 7).** 07 gains a Delivered note, MEU-114 is `ready_for_review` (`approved` after the H1-7 review), and `UNINSTALL-LEAVES-INSTALLER-COPY` is resolved ("fixed in the tree, ships in rc.2").

### What these checks don't prove

- The installer under test was repackaged, not built from clean: its app payload is RC1's, and its version still reads `0.1.0-rc.1`. MEU-125 repeats the round trip on the full rc.2 build (plan D-268).
- `${isUpdated}`'s skip can't be observed at runtime, because the install rewrites the copy straight afterwards. Phase D shows the copy present after a second install over the first, and the macro pin proves the structure (AC-114.1).
- The round trip ran on this PC, per-user. A per-machine install's `SetShellVarContext` switch compiles under `-WX` but wasn't exercised.
- The round trip started with the copy Mat's earlier RC1 install had left in `av-kit-ui-updater` (`pre-state: … holds [installer.exe]`). It's the RC1 installer, which row 0 had already kept as `RC1_INSTALLER`. Phase A's RC1 install wrote the same file over it and RC1's uninstall left it in place; phase B's new uninstall removed it with its folder. A copy RC1 already left on another machine goes the same way, once rc.2 or later is installed and then uninstalled.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md) §MEU-114. **Execution authorization:** `USER_EXPLICIT`, 2026-11-05, "all recommendations are accpeted, proceed" (D-273 to D-278). The plan review approved with no findings (D-273), and D-278 starts execution on that approval.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-114.1 | unit | `customUnInstall` holds `Delete` and a non-recursive `RMDir` inside the not-updated guard. | Local Canon (07 §Uninstall; D-228) | `ui/tests/unit/login-item-nsh.test.ts:101` | ✅ |
| AC-114.2 | unit | The folder name equals `ui/package.json`'s name plus `-updater`. | Local Canon (`app-builder-lib/out/appInfo.js:126`) | `ui/tests/unit/login-item-nsh.test.ts:115` | ✅ |
| AC-114.3 | unit | AC-61.18's two `DeleteRegValue` lines stay the only two, and there's no `RMDir /r`. | Local Canon (AC-61.18; D-258) | `ui/tests/unit/login-item-nsh.test.ts:122` | ✅ |
| AC-114.4 | integration | NSIS compiles the macro under `-WX`, through `repackage.ps1`. | Local Canon (`NsisTarget.js:623`) | row 4 (`repackage.ps1`, electron-builder exit 0) | ✅ |
| AC-114.5 | integration | Phase A: RC1's uninstall leaves the copy, so the check can see the bug. | Local Canon (D-228) | row 6 (`install-roundtrip.ps1` phase A) | ✅ |
| AC-114.6 | integration | Phase B: the new uninstall removes the copy and its folder. | Local Canon (07 §Uninstall) | row 6 phase B | ✅ |
| AC-114.7 | integration | Phase B: `%APPDATA%\av-kit-ui` stays, and `%LOCALAPPDATA%\av-kit`'s top-level entries are unchanged. | Local Canon (07 §Uninstall; `ui/electron-builder.yml:18`) | row 6 phase B (S6 snapshot) | ✅ |
| AC-114.8 | integration | Phase C: RC1 to new launches, and the later uninstall is clean. | Local Canon (07 §Uninstall: an upgrade still works) | row 6 phase C | ✅ |
| AC-114.9 | integration | Phase D: new over itself keeps the copy and launches, and the later uninstall is clean. | Local Canon (07 §Uninstall) | row 6 phase D | ✅ |
| AC-113 (cross-ref) | — | Owned by the MEU-113 handoff (the fetch script's exit codes) | plan §MEU-113 | [MEU-113 handoff](2026-11-04-rc2-fetch-uninstall-MEU-113-handoff.md) | see MEU-113 |
| AC-61 (cross-ref) | regression | AC-61.18: two executable `DeleteRegValue HKCU` lines and the `nsis.include` value. The macro edit sits in the same file; AC-114.3 adds the guard and AC-61.18 still passes | plan AC-114.3 | `ui/tests/unit/login-item-nsh.test.ts:27` (gate `ui-tests`) | ✅ |
| AC-24 (cross-ref) | regression | AC-24.10: the packaged backend folder holds its exe and support tree. Under the baseline rule it would be excused only if row 0 had seen it fail; row 0 saw it pass, so nothing is excused | plan §Session gate | `tests/unit/test_packaging_backend.py` (gate `py-tests`) | ✅ |
| AC-25 (cross-ref) | regression | AC-25.6: `deleteAppDataOnUninstall: false`, which AC-114.7 observes on a real uninstall. AC-25.10: same baseline rule as AC-24.10 | plan §Session gate | `tests/unit/test_packaging_installer.py:56`, `:94` (gate `py-tests`) | ✅ |
| AC-110 (cross-ref) | — | AC-110.9 keeps one version on every surface. The bump to `0.1.0-rc.2` is MEU-125's, so the repackaged installer still reads `0.1.0-rc.1` | plan §Out of Scope | `tests/unit/test_release_packaging.py` (gate `py-tests`) | deferred to MEU-125 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-114.1 | `AssertionError: expected [] to have a length of 1 but got +0` | pass | `login-item-nsh.test.ts:101` |
| AC-114.2 | `AssertionError: expected [] to deeply equal [ Array(1) ]` | pass | `login-item-nsh.test.ts:115` |
| AC-114.5 to AC-114.9 | Phase A, RC1's uninstall: `installer copy after the uninstall: present` | Phases B to D: `installer copy after the uninstall: absent, and so is the folder` | `install-roundtrip.ps1` |

Row 3's Red is 2 failed and 2 passed. AC-61.18 and AC-114.3 pass before the change by design, because AC-114.3 guards against what Green could break. `red-check.py` required AC-114.1 and AC-114.2 and found 0 problems. Row 4's Green is 4 passed. The runtime Red is phase A itself: the same check that passes for the new installer reports RC1's leftover copy.

Receipts: `C:/Temp/av-kit/s49-nsh-red.txt` (with `.exit`), `s49-nsh-red-check.txt`, `s49-nsh-green.txt`; under `C:/Temp/av-kit/rc2/`: `repackage.txt`, `prepackaged-installer.exe`, `roundtrip-preconditions.txt`, `roundtrip-prepackaged.txt` and the `roundtrip-prepackaged/` snapshots; the shared row 7 and gate receipts listed in the MEU-113 handoff.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s49-114-red", "command": "rtk proxy npm --prefix ui run test -- tests/unit/login-item-nsh.test.ts *> C:/Temp/av-kit/s49-nsh-red.txt; then red-check.py --require AC-114.1 --require AC-114.2 (task.md row 3 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-114 Red: the macro pin against the unchanged installer.nsh, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 83229ea (baseline.sha) plus rows 1 to 3", "output": "2 failed | 2 passed (4). AC-114.1: expected [] to have a length of 1 but got +0. AC-114.2: expected [] to deeply equal [ Array(1) ]. red-check: 1 receipt(s), 2 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-114-green-repackage", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test -- tests/unit/login-item-nsh.test.ts; then rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-04-rc2-fetch-uninstall/repackage.ps1 *> C:/Temp/av-kit/rc2/repackage.txt (task.md row 4 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-114 Green and AC-114.4: the macro pin, then NSIS compiles the macro under -WX in an installer repackaged from RC1's win-unpacked, written outside ui/dist", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 83229ea plus rows 1 to 4", "output": "Tests 4 passed (4). electron-builder version=26.18.0, target=nsis oneClick=true perMachine=false, electron-builder exit=0. PREPACKAGED_INSTALLER bytes=340348050 sha256=5d44f65ee37b8577ac5126bfdfe1e79bfa7db168fed7c210a7e01b489d63f7cd. ui/dist RC1 installer sha256=beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7. repackage: PREPACKAGED_INSTALLER written; RC1 installer unchanged."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-114-preconditions", "command": "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-04-rc2-fetch-uninstall/install-roundtrip.ps1 -PreconditionsOnly -NewInstaller C:/Temp/av-kit/rc2/prepackaged-installer.exe -OldInstaller C:/Temp/av-kit/rc2/rc1-installer.exe -OutDir C:/Temp/av-kit/rc2/roundtrip-prepackaged (task.md row 5 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "ROUND_TRIP parsed and its S5 checks run, installing nothing", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 83229ea plus rows 1 to 5", "output": "S5 preconditions: clear. Nothing installed."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-114-roundtrip", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-04-rc2-fetch-uninstall/install-roundtrip.ps1 -NewInstaller C:/Temp/av-kit/rc2/prepackaged-installer.exe -OldInstaller C:/Temp/av-kit/rc2/rc1-installer.exe -OutDir C:/Temp/av-kit/rc2/roundtrip-prepackaged *> C:/Temp/av-kit/rc2/roundtrip-prepackaged.txt (task.md row 6 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-114.5 to AC-114.9 on the build PC: phase A RC1 install and uninstall, phase B new install, smoke and uninstall, phase C RC1 then new, phase D new over new, each uninstall checked against a before-and-after snapshot", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 83229ea plus rows 1 to 6", "output": "old installer sha256 beabc509..., new 5d44f65e.... S5 preconditions: clear. A: installer copy after the uninstall: present, sha256 beabc509...; AC-114.5 A: RC1's uninstall left the copy, so the check can see the bug. B: PASS: packaged-app-smoke; S6 (B): nothing left behind, and the app data keeps the same top-level entries; installer copy after the uninstall: absent, and so is the folder; AC-114.6 B. C: RC1 then new, new copy 5d44f65e... present, PASS: packaged-app-smoke, S6 (C) clean, copy absent; AC-114.8 C. D: copy present after the second install, PASS: packaged-app-smoke, S6 (D) clean, copy absent; AC-114.9 D. Every uninstall: relaunched copy seen: False. install-roundtrip: exit 0."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-row7-hub", "command": "pwsh -NoProfile -File row7.ps1 (task.md row 7 Validation cell, verbatim, from P:/av-kit): meu_status.py render --check, issue_triage.py render --check, the issue statuses and issue-decisions.py", "cwd": "P:/av-kit", "scope": "Row 7 hub, shared by MEU-113 and MEU-114: the 07 Delivered notes, both MEUs ready_for_review, the two issues resolved and FFMPEG-LIBDVDCSS-BUNDLED left open, and the decision logs read back in the validator's grammar", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 83229ea plus rows 1 to 7", "output": "Drift check passed (126 MEUs, 12 phases). Issue renders match. Statuses FETCH-FFMPEG-EXIT-CODES resolved, UNINSTALL-LEAVES-INSTALLER-COPY resolved, FFMPEG-LIBDVDCSS-BUNDLED open. UNINSTALL-LEAVES-INSTALLER-COPY: D-228 (triage). FFMPEG-LIBDVDCSS-BUNDLED: D-214 (triage), D-215 (triage), D-266 (triage), D-275 (triage). issue-decisions: 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-04-rc2-fetch-uninstall/session-gate.ps1 *> C:/Temp/av-kit/s49-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s49-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 7: identity, every static check, both full suites, the UI build and the state render, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec", "output": "py-types 0 errors; py-lint all checks passed; ui-types and ui-lint exit 0; task-contract OK: 24 row(s), 22 fully checked, 2 exempt (view_file); scope-paths changed paths: 29 outside scope: [] head moved (S4): False; red-check selftest: 36 fixture(s), 0 wrong; py-tests 1193 passed in 110.41s; ui-tests 108 files, 1141 passed; ui-build exit 0; state-render drift check passed (126 MEUs); tested_state before and after identical. Baseline failures excused: none. session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s49-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec", "output": "Drift check passed - SSOT loaded (126 MEUs, 12 phases), rendered regions match on-disk content"}
```

### Quality Gate Results

`s49-gate-h1-2` is the fresh full record, shared with the MEU-113 handoff, and its last line is:

> session-gate: all steps exit 0

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract` (24 rows), `scope-paths` (29 changed paths, none outside scope, HEAD still `83229ea`), `red-check-selftest`: all exit 0.
- **Suites:** `py-tests` 1193 passed; `ui-tests` 108 files, 1141 passed, AC-114.1 to AC-114.3 and AC-61.18 among them. Baseline failures excused: none.
- **Build and state:** `ui-build` and `state-render` exit 0.
- **Skipped, each printed with its reason:** `openapi`, `mcp-types`, `mcp-build`, `mcp-tests`, `mcp-audit`, `build-record`, and `ui-electron` (no main, preload or renderer change; row 6's `packaged-app-smoke.mjs` launched the real packaged Electron in phases B to D).
- **Identity:** `tested_state` `83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec`, the same before and after.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/build/installer.nsh` | modified | The not-updated block in `customUnInstall`. CRLF kept |
| `ui/tests/unit/login-item-nsh.test.ts` | modified | AC-114.1 to AC-114.3. CRLF kept |
| `docs/build-plan/07-distribution.md` | modified | Delivered notes, shared with MEU-113 |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml`, `current-focus.md` | modified | Status, issues and focus, shared with MEU-113 (see its Changed Files for the `meu-status.yaml` rewrap) |
| Plan folder: `repackage.ps1`, `install-roundtrip.ps1`, plus the shared scripts | new | The repackage and the round trip. `packaged-app-smoke.mjs` is reused from RC1's plan folder by path |

```diff
 !macro customUnInstall
   DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "com.avkit.app"
   DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" "com.avkit.app"
+  ${ifNot} ${isUpdated}
+    ${if} $installMode == "all"
+      SetShellVarContext current
+    ${endif}
+    Delete "$LOCALAPPDATA\${APP_INSTALLER_STORE_FILE}"
+    RMDir "$LOCALAPPDATA\av-kit-ui-updater"
+    ${if} $installMode == "all"
+      SetShellVarContext all
+    ${endif}
+  ${endIf}
 !macroend
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

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | None. The reviewer's one clerical note, the pre-existing copy's chronology in the MEU-114 handoff's round-trip note, is corrected against `roundtrip-prepackaged.txt`. | — | — | closed |

### Verdict

Approved: Codex execution review, loop `s49-execution-2026-11-04-rc2-fetch-uninstall`, round 1 of 6, no findings, intent achieved (7,708,396 tokens). The report is `2026-11-04-rc2-fetch-uninstall-implementation-critical-review.md`.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The round trip on the full rc.2 build | deferred | MEU-125 | Plan D-268: this session repackages; MEU-125 builds from clean and repeats AC-114.5 to AC-114.9 |
| Version bump to `0.1.0-rc.2` | deferred | MEU-125 | 07 §Second release candidate; AC-110.9 |
| A per-machine install's round trip | out-of-scope | — | av-kit installs per user (`perMachine=false`); the switch compiles under `-WX` (AC-114.4) |
| Commit, push, tag and upload | out-of-scope | — | D-276 committed the triage only and authorized no push; this session's commit waits for Mat's direction (H2-5) |

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-05 | claude-code-local (Claude Opus 5.5) | Initial MEU-114 handoff after H1-2 |
