---
date: "2026-11-28"
project: "2026-11-26-app-auto-update"
meu: "MEU-174"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md"
build_plan_section: "docs/build-plan/07-distribution.md §In-app update (MEU-174); docs/build-plan/06-gui.md §Settings, Updates"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-26-app-auto-update-MEU-173-handoff.md"
---

# Handoff: 2026-11-26-app-auto-update-MEU-174-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-174 In-app update (phase 7), the second of two in Session 106: [MEU-173](2026-11-26-app-auto-update-MEU-173-handoff.md) → MEU-174. The session-wide gate table and the list of execution decisions are in the MEU-173 handoff.
**Build Plan Section**: `docs/build-plan/07-distribution.md` §In-app update, with its `Delivered (Session 106)` note (row 18), and `docs/build-plan/06-gui.md` §Settings, Updates. MEU-174 is `ready_for_review`.
**Predecessor**: [2026-11-26-app-auto-update-MEU-173-handoff.md](2026-11-26-app-auto-update-MEU-173-handoff.md).

- **Interval (`UPDATE_INTERVAL_LEAF`).** `app.update_interval` is `weekly` (the default), `monthly` or `never`, in the core registry, the API model and `openapi.committed.json`, the UI schema, the Settings page and the MCP settings tool. `never` stops the scheduled request.
- **Updater (`ui/src/main/app-updater.ts`).** `electron-updater` 6.8.11 with `allowPrerelease` and `allowDowngrade` false, `autoDownload` true and `autoInstallOnAppQuit` false (`UPDATER_CONFIG`). A packaged controller ticks (`UPDATE_TICK`), checks when the interval is due (`UPDATE_SCHEDULE`), downloads in the background, keeps its state in five store keys (`UPDATE_STATE`: `disabled`, `idle`, `checking`, `downloading`, `ready`, `error`), fails quietly with no network (`UPDATE_QUIET_FAILURE`) and shows one notice per downloaded version (`UPDATE_NOTICE_ONCE`). A development run never checks. `hardenUpdater()` (execution review round 1) keeps the library from sending or storing a staging id (D-1591) and from logging anything itself (D-1592).
- **Install order (`UPDATE_INSTALL_ORDER`).** **Restart and update** sets the quit intent, waits for the backend to stop, then calls `quitAndInstall(true, true)` once, through one shared `shutdownForQuit()` (D-1571).
- **IPC (`UPDATE_IPC`).** Three channels and one push, each with the no-payload schema, in the strict census and the preload; `update-check` checks whatever the interval says, also with `never` (D-1548).
- **Settings card (`UPDATES_CARD`, `UpdatesCard.tsx`).** The interval select, the version line, the status line, **Check now**, and in `ready` **Restart and update** with its note; the trust note (checked by the release's SHA-512, not signed; D-1543's recommendation) shows in every state.
- **Installer (`ui/build/installer.nsh`).** `customCheckAppRunning` stops every process under the install folder, the MCP server too, by a bounded folder match (`APP_RUNNING_CHECK`, D-1554); the not-updated uninstall block removes `$LOCALAPPDATA\av-kit-ui-updater` with `RMDir /r` and both sign-in values (`UNINSTALL_CACHE_RECURSIVE`, D-1553); an update keeps the user's data and the `Run` value.
- **AppUserModelId (D-1583).** `boot()` in `ui/src/main/index.ts` calls the new `applyAppUserModelId(app)` right after the single-instance check, before the login item is read and before any window, tray or toast. On Windows it sets the id to `LOGIN_ITEM_NAME` (`com.avkit.app`), the appId that the NSIS shortcut carries.
- **E2E.** `ui/tests/e2e/app-update.test.ts` (AC-174.15, AC-174.16) runs against a local feed in the main stage. The install stage's spec `ui/tests/e2e-install/update-roundtrip.test.ts` (AC-174.18 to AC-174.20) installs `0.0.901`, serves `0.0.902` as a local feed and updates one to the other on the mini-air host; `tools/e2e_remote.py` and the host scripts run it as a second stage (`HOST_PAYLOAD`, `INSTALL_STAGE_RULES`, `ROUND_TRIP`).

**What Mat sees.** Settings gains an Updates section. Once a week by default (or once a month, or never) the installed app asks GitHub for the newest release. A newer one downloads in the background, and the card then offers **Restart and update**. Nothing installs without that click. Start at sign-in now reads back correctly in an installed app (D-1583). Users get the updater with the first release that carries the feed files, which is Mat's step.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md). **Execution authorization:** `USER_EXPLICIT`, Mat: "commit 103 and go for 106". Decisions: `USER_EXPLICIT` 2026-11-18, "make the decisions always the recommenations". Receipts named by file name alone are in the session's receipts folder (the `2026-11-26-app-auto-update` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-174.1 | unit | `isCheckDue` follows `UPDATE_SCHEDULE` for `weekly` and `monthly`: not due 1 ms before the period ends, due at the period, due when `lastCheckAt` is null or in the future | Human-approved: triage D-1409 | `ui/tests/unit/update-schedule.test.ts:39-87` | ✅ |
| AC-174.2 | unit | With a fake clock and the updater mocked, the controller ticks per `UPDATE_TICK` and checks once when due, never twice while a check or a download runs; the interval is read at each tick | Human-approved: D-1409; Local Canon: D-1550 | `ui/tests/unit/app-updater.test.ts:233-320` | ✅ |
| AC-174.3 | unit | `UPDATER_CONFIG`: `allowPrerelease` false, `allowDowngrade` false, `autoDownload` true, `autoInstallOnAppQuit` false; no `setFeedURL` call; `forceDevUpdateConfig` unset | Research-backed: R3, R4; Local Canon: D-1540, D-1542 | `ui/tests/unit/app-updater.test.ts:353-389`, `:794` (F1, real library) | ✅ |
| AC-174.4 | unit | The events map to `UPDATE_STATE`, each change emits the state, the store holds only the five keys; a found version sets `pendingVersion`, a check that finds none clears it | Local Canon: D-1547, D-1550 | `ui/tests/unit/app-updater.test.ts:415-501` | ✅ |
| AC-174.5 | unit | `UPDATE_QUIET_FAILURE`: a rejected check and an `error` event each give `error` with its `errorKind`, one log line, `lastAttemptAt` set and `lastCheckAt` unchanged | Local Canon: 07 §In-app update, Outbound row | `ui/tests/unit/app-updater.test.ts:515-565`, `:824` (F2, real library) | ✅ |
| AC-174.6 | unit | `UPDATE_NOTICE_ONCE`: one notice per downloaded version; no `quitAndInstall` after `update-downloaded` | Human-approved: D-1409; Local Canon: D-1542 | `ui/tests/unit/app-updater.test.ts:598`, `:611` | ✅ |
| AC-174.7 | unit | `UPDATE_INSTALL_ORDER`: in `ready`, `install()` records `setQuitIntent`, `shutdownBackend` resolved, `quitAndInstall(true, true)`, once | Local Canon: 07 §In-app update, Processes row; D-1542 | `ui/tests/unit/app-updater.test.ts:634-672` | ✅ |
| AC-174.8 | unit | `UPDATE_IPC`: three channels and the push with the no-payload schema, the preload's four keys, and `update-check` runs a check also with `never` | Local Canon: D-1548 | `ui/tests/unit/update-ipc.test.ts:80-160` | ✅ |
| AC-174.9 | unit | Core and API: `update_interval` is `weekly` on a new database; `PUT` accepts `weekly`, `monthly`, `never` and the next `GET` returns it | Local Canon: 07 §In-app update; D-1409, D-1541 | `tests/unit/test_update_interval_setting.py:42`, `:46`, `:63` | ✅ |
| AC-174.10 | unit | `openapi.committed.json` holds `update_interval` in the settings request model, and the drift check passes | Local Canon: 07 §In-app update; G8 | row 9 drift (`aau-row9-drift-before.txt`, then `aau-row9-green.txt`); the H1-4 OpenAPI check | ✅ |
| AC-174.11 | unit | MCP: the schema resource lists `app.update_interval` with default and enum; `avkit_settings.set` takes the three wires; the tool and action lists are unchanged | Local Canon: D-1546 | `mcp-server/tests/update-interval-setting.test.ts:19`, `:24`, `:31` | ✅ |
| AC-174.12 | unit | `appPutSchema` takes the three wires and stays strict; `UPDATES_CARD` renders the select, the version line, the status line per state and `settings-update-check`; a select change calls `schedulePut` | Local Canon: D-1547, D-1548 | `ui/tests/unit/updates-card.test.tsx:132-200` | ✅ |
| AC-174.13 | unit | In `ready`, `settings-update-restart` and its note show and a click calls `updateInstall` once; `settings-update-trust-note` shows in every state | Local Canon: D-1549; D-1543 (open) | `ui/tests/unit/updates-card.test.tsx:210-233` | ✅ |
| AC-174.14 | unit | `UNINSTALL_CACHE_RECURSIVE`: the not-updated block holds `RMDir /r "$LOCALAPPDATA\av-kit-ui-updater"` once and both `DeleteRegValue HKCU` lines, none outside it | Local Canon: D-1553 | `ui/tests/unit/update-uninstall-nsh.test.ts:83`, `:92` | ✅ |
| AC-174.15 | integration | Main stage on mini-air, local feed: the Updates section shows, `monthly` saves and survives a reload, and a feed with `999.0.0` reaches "Version 999.0.0 is ready to install" | Local Canon: 07 §In-app update, Tests row | `ui/tests/e2e/app-update.test.ts:222-255`; run `r20261128T024018Z-d7983df`, `run-check main AC-174.15: passed (3)` | ✅ |
| AC-174.16 | integration | Same run: Check now passes through "Checking…", and Restart and update records exactly one `[true, true]` install call | Local Canon: D-1548, D-1542 | `ui/tests/e2e/app-update.test.ts:266-294`; same run, `run-check main AC-174.16: passed (3)` | ✅ |
| AC-174.17 | unit | `HOST_PAYLOAD`: `run --payload` carries the payload, refuses a bad folder before any upload, and the summary holds the `install` block; without `--payload` the request is as before | Local Canon: D-1552 | `tests/tooling/test_e2e_remote.py:3199-3303` | ✅ |
| AC-174.18 | integration | Host run 1 (canary): the row 3 installer installs silently in the E2E account, the main window shows, and the stage leaves the account as it found it | Local Canon: D-1552; D-1564 | `ui/tests/unit/install-preconditions.test.ts:150-168`; `ui/tests/e2e-install/update-roundtrip.test.ts:532`, `:555`; row 7 run | ✅ |
| AC-174.19 | integration | Host run 2 (`ROUND_TRIP`): an installed `0.0.901` finds, downloads and installs `0.0.902` from the local feed on the click; the old app, backend and MCP server are gone first; the new version runs; the setting, the marker file and the `Run` value are kept; the sibling decoy lives | Local Canon: 07 §In-app update; Human-approved: D-1409 | `ui/tests/e2e-install/update-roundtrip.test.ts:548`; run `r20261128T062757Z-ac98b72`, `install AC-174.19: passed` | ✅ |
| AC-174.20 | integration | After the round trip's uninstall, `%LOCALAPPDATA%\av-kit-ui-updater` and both sign-in values are gone as soon as the uninstaller returns; then the snapshots are equal and the owner record is deleted | Local Canon: D-1553 | `ui/tests/e2e-install/update-roundtrip.test.ts:551`; same run, `install AC-174.20: passed` | ✅ |
| AC-174.21 | unit | `APP_RUNNING_CHECK`: `customCheckAppRunning` with the fixed PowerShell path, two modes, the bounded folder match, and `appCannotBeClosed`, `SetErrorLevel 2`, `Quit` on any non-zero exit; run against two decoys | Research-backed: R7; Local Canon: D-1554 | `ui/tests/unit/app-running-nsh.test.ts:138`, `:152`, `:167` | ✅ |
| AC-173 (cross-ref) | sibling | AC-173.1 to AC-173.5 belong to MEU-173 (the feed) | the plan | see the MEU-173 handoff | cross-ref |
| AC-61 (cross-ref) | pin | AC-61.18 keeps its line in `ui/tests/unit/login-item-nsh.test.ts:124` | the plan; D-1553 | `ui/tests/unit/login-item-nsh.test.ts:124` | ✅ unchanged |
| AC-114 (cross-ref) | named change | AC-114.2 and AC-114.3 expect `RMDir /r` at `login-item-nsh.test.ts:105`, `:112`, `:119`, `:122`, `:125` (D-1553, row 13) | the plan; D-1553 | `ui/tests/unit/login-item-nsh.test.ts:105-125` | ✅ |
| AC-106 (cross-ref) | named change | AC-106.5's OpenAPI delta sets back `SettingsPutIn.update_interval`; what it asserts about the capture shapes is unchanged | D-1582 | `tests/e2e/test_api_capture_shapes.py::test_ac_106_5_openapi_snapshot_and_delta`; `openapi-delta.py --selftest` 13 cases, 0 wrong | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-174.21 | Row 2a (`aau-row2a-red.txt`): `Tests  3 failed (3)`; "the macro customCheckAppRunning: expected 0 to be greater than 0" | Row 2b (`aau-row2b-green.txt`): `Tests  7 passed (7)` | `ui/tests/unit/app-running-nsh.test.ts:138` |
| AC-174.17 | Row 4 (`aau-row4-red-py.txt`): `10 failed, 1 passed, 215 deselected`; "tools/e2e_remote.py has no read_payload yet" | Row 5 (`aau-row5-green-py.txt`): `226 passed` | `tests/tooling/test_e2e_remote.py:3199` |
| AC-174.18 | Row 4 (`aau-row4-red-ui.txt`): `Tests  15 failed (15)`; "install-helper exports checkPreconditions: expected 'undefined' to be 'function'" | Row 5 (`aau-row5-green-ui.txt`): `Tests  15 passed (15)`; row 7 `install: state=ran tests=1 expected=1 unexpected=0` | `ui/tests/unit/install-preconditions.test.ts:150` |
| AC-174.9 | Row 8 (`aau-row8-red.txt`): `6 failed`; `assert None == 'weekly'` | Row 9 (`aau-row9-green.txt`): `131 passed` | `tests/unit/test_update_interval_setting.py:42` |
| AC-174.11 | Row 10 (`aau-row10-red.txt`): `Tests  3 failed (3)` | Row 11 (`aau-row11-tests.txt`): `Tests  560 passed (560)` | `mcp-server/tests/update-interval-setting.test.ts:19` |
| AC-174.1 to AC-174.8, AC-174.14 | Row 12 (`aau-row12-red.txt`): `Tests  47 failed \| 1 passed (48)`; "app-updater exports createAppUpdater" | Row 13 (`aau-row13-green.txt`): `Tests  51 passed (51)` | `ui/tests/unit/app-updater.test.ts:233` |
| AC-174.12, AC-174.13, AC-174.15, AC-174.16 | Row 14 (`aau-row14-red.txt`): `Tests  16 failed (16)`; "UpdatesCard.tsx exports UpdatesCard" | Row 15 (`aau-row15-green.txt`): `Tests  80 passed (80)`; `aau-row15-ui-full.txt`: `Tests  1798 passed (1798)`; row 17 main stage 266/266 | `ui/tests/unit/updates-card.test.tsx:132` |
| AC-174.19 (D-1583, the AppUserModelId at startup) | `aau-b17-red.txt`: `Tests  2 failed \| 1 passed (3)`; "index.ts exports applyAppUserModelId: expected 'undefined' to be 'function'"; "boot() calls applyAppUserModelId: expected -1 to be greater than or equal to 0" | `aau-b17-green.txt`: `Tests  79 passed (79)`; `aau-b17-ui-full.txt`: `Tests  1801 passed (1801)` | `ui/tests/unit/app-user-model-id.test.ts:26`, `:41`, `:49` |
| AC-174.19, AC-174.20 | Row 17, runs 1 to 3: each `install-failures exit=41` (AC-174.19 unexpected, AC-174.20 skipped); see §Root cause | Row 17 verification run `r20261128T024018Z-d7983df`, then the corrections run `r20261128T062757Z-ac98b72`: each `install: state=ran tests=2 expected=2 unexpected=0`; `install AC-174.19: passed`, `install AC-174.20: passed` | `ui/tests/e2e-install/update-roundtrip.test.ts:548`, `:551` |
| AC-174.3 (F1, D-1591), AC-174.5 (F2, D-1592) | Corrections row c1 (`aau-c1-red.txt`): `Tests  2 failed \| 35 passed (37)`; "headers of /matbanik/av-kit/releases.atom: expected [ 'x-user-staging-id', 'accept' ] to not include 'x-user-staging-id'"; "expected [ 'Checking for update', …(2) ] to deeply equal []" | `aau-c1-green.txt`: `Tests  66 passed (66)`; gate run r11 ui-tests `Tests  1803 passed (1803)` | `ui/tests/unit/app-updater.test.ts:794`, `:824` |

### Root cause of the three failed host runs (B-17, fixed by D-1583)

Row 17's first three host runs (`r20261127T235735Z-692eb6f`, `r20261128T003726Z-2a01a7d`, `r20261128T011909Z-c447a4d`) each passed the main stage 266 of 266 and ended `install-failures exit=41`. D-1578 and D-1579 fixed two real faults in the spec's mechanics (a load-state wait and the click on a controlled checkbox) and changed nothing an AC asserts. The third run still failed at AC-174.19: in installed `0.0.901`, the start-at-sign-in box stayed unchecked 30 s after the click (`update-roundtrip.test.ts:435`, `Received: unchecked`), so the update was never reached. The coordinator's bound of three runs was reached and row 17 became `[B]` (D-1580).

The cause was in the product, not the test:

- `ui/src/main/login-item.ts` writes the Windows `Run` value with `name: LOGIN_ITEM_NAME` (`com.avkit.app`).
- Electron 42's `getLoginItemSettings` takes no `name` (`electron.d.ts`, `LoginItemSettingsOptions`). It reads `openAtLogin` from the value named after the current AppUserModelId (`Settings.name`: "Defaults to the app's AppUserModelId()").
- av-kit set that id only inside `defaultToast` (`ui/src/main/notify-user.ts:50`). At startup it was still Electron's default, so `willLaunchAtSignIn` read another value and answered false, and in an installed app the box never turned checked.
- The coordinator ruled out a disabled startup entry: a read-only query on mini-air found only OneDrive and Edge under HKCU `Run` and `StartupApproved\Run`.

D-1583 sets the id in `boot()` before the login item is read (unit test Red then Green above, full UI suite 1801 of 1801). Row 16 rebuilt the pair from snapshot `d7983df`. Row 17 then ran once more as a verification run for a root-caused product fix, not a retry; the coordinator lifted the three-run bound for that one run only. It passed: `e2e-remote: ok exit=0 run=r20261128T024018Z-d7983df`. D-1584 lifted B-17 and returned rows 18 and H1-3 to their original form.

After execution review round 1 (F1, F2; D-1591, D-1592), row 16 rebuilt the pair from snapshot `ac98b72` (69 scope paths) and row 17 ran once at it, as the coordinator directed: `e2e-remote: ok exit=0 run=r20261128T062757Z-ac98b72`, main stage tests=266, install 2 of 2, run-check 0 problem(s).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-13-ui-unit", "command": "pwsh: Set-Location 'P:\\av-kit\\ui'; npx vitest run (task.md row 13 Validation cell); receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row13-green.txt, aau-row13-licence.txt", "scope": "AC-174.1 to AC-174.8, AC-174.14, the D-1553 pins and the licence check", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 13", "output": "aau-row13-green.txt: Tests  51 passed (51). aau-row13-licence.txt: licence-check: 5 added, closure 16; 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-15-ui-full", "command": "pwsh: Set-Location 'P:\\av-kit\\ui'; npx vitest run (task.md row 15 Validation cell); receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row15-green.txt, aau-row15-ui-full.txt", "scope": "AC-174.12, AC-174.13 and the whole UI unit suite", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 15", "output": "aau-row15-green.txt: Tests  80 passed (80). aau-row15-ui-full.txt: Tests  1798 passed (1798)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-b17-aumid-unit", "command": "pwsh: Set-Location 'P:\\av-kit\\ui'; npx vitest run tests/unit/app-user-model-id.test.ts (Red before the fix, then with its neighbours), then npx vitest run (D-1583); receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-b17-red.txt, aau-b17-green.txt, aau-b17-ui-full.txt", "scope": "D-1583: boot() sets the AppUserModelId to LOGIN_ITEM_NAME on win32 before the login item, any window or the tray", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 17 and D-1583", "output": "aau-b17-red.txt: Tests  2 failed | 1 passed (3). aau-b17-green.txt: Tests  79 passed (79). aau-b17-ui-full.txt: Tests  1801 passed (1801)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-7-install-preconditions", "command": "uv run python tools/e2e_remote.py run (task.md row 7 Validation cell); receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row7-run.txt, aau-row7-run-check.txt", "scope": "AC-174.18 on mini-air: the install stage runs its precondition spec", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 7; run r20261127T225928Z-e1518e1", "output": "aau-row7-run.txt: install: state=ran tests=1 expected=1 unexpected=0 (the main stage's exit=40 at this row is the not-yet-built UI, which row 15 turned green). aau-row7-run-check.txt: run-check install: 1 passed; run-check: 0 problem(s). Host: smart_app_control Off"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-17-roundtrip-r1-r3", "command": "uv run python tools/e2e_remote.py run (task.md row 17 Validation cell), runs 1 to 3; receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row17-r1-run.txt, aau-row17-r2-run.txt, aau-row17-r3-run.txt and their -run-check files", "scope": "AC-174.15, AC-174.16 (main stage) and AC-174.19, AC-174.20 (install stage) on mini-air, before D-1583", "phase": "runtime", "exit_code": 41, "result": "fail", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 17; runs r20261127T235735Z-692eb6f, r20261128T003726Z-2a01a7d, r20261128T011909Z-c447a4d", "output": "Each run: main stage 266/266 passed; install stage AC-174.19 unexpected, AC-174.20 skipped; last line e2e-remote: install-failures exit=41 run=<id>. Run 3: toBeChecked on the start-at-sign-in box, Received: unchecked, at update-roundtrip.test.ts:435. Root cause: the AppUserModelId at startup (D-1583)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-17-roundtrip", "command": "uv run python tools/e2e_remote.py run (task.md row 17 Validation cell), the corrections run on row 16's pair rebuilt at snapshot ac98b72 after execution review round 1 (D-1591, D-1592); receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row17-run.txt, aau-row17-run-check.txt, aau-row17-snapshot.txt, aau-row16-cell.txt", "scope": "AC-174.15, AC-174.16 (main stage) and AC-174.19, AC-174.20 (install stage) on mini-air", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "snapshot ac98b7272f61 (parent 5e4ec2f, 69 scope paths); run r20261128T062757Z-ac98b72", "output": "aau-row16-cell.txt: build-update: pair-ok exit=0. aau-row17-snapshot.txt: snapshot-commit verify: bound. aau-row17-run.txt: summary: tests=266 expected=266 unexpected=0 flaky=0 skipped=0 spec_files=35; install: state=ran tests=2 expected=2 unexpected=0 flaky=0 skipped=0; e2e-remote: ok exit=0 run=r20261128T062757Z-ac98b72. aau-row17-run-check.txt: run-check main AC-174.15: passed (3); run-check main AC-174.16: passed (3); run-check install AC-174.19: passed; run-check install AC-174.20: passed; run-check: 0 problem(s). Host: smart-app-control Off; 6 polls saw another workload (polls.jsonl)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-c1-real-library", "command": "pwsh: Set-Location 'P:\\av-kit\\ui'; npx vitest run tests/unit/app-updater.test.ts (Red before hardenUpdater, row c1), then the row 13 Validation set, tsc --noEmit and eslint; receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-c1-red.txt, aau-c1-red-check.txt, aau-c1-green.txt, aau-c1-typecheck.txt, aau-c1-eslint.txt, aau-c1-red-unchanged.txt", "scope": "Execution review round 1: F1 (AC-174.3, D-1591) and F2 (AC-174.5, D-1592) against the real NsisUpdater and GitHub provider, network-free", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 5e4ec2f (baseline.sha) plus rows 0 to 18, D-1583 and corrections row c1", "output": "aau-c1-red.txt: Tests  2 failed | 35 passed (37); 'headers of /matbanik/av-kit/releases.atom: expected [ x-user-staging-id, accept ] to not include x-user-staging-id'; 'expected [ Checking for update, …(2) ] to deeply equal []'. aau-c1-red-check.txt: 2 required test(s), 0 problem(s). aau-c1-green.txt: Tests  66 passed (66). aau-c1-typecheck.txt and aau-c1-eslint.txt: exit 0. aau-c1-red-unchanged.txt: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "aau-h1-2-gate", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-26-app-auto-update/session-gate.ps1 *> C:/Temp/av-kit/2026-11-26-app-auto-update/aau-gate-h1.txt (task.md row H1-2's Validation cell), run r11 after execution review round 1; step receipts C:/Temp/av-kit/2026-11-26-app-auto-update/aau-D6-*.txt", "scope": "H1-2: the registered verification plan (implementation-plan.md Verification Plan 5): identity before and after, 20 static steps, 10 fresh full steps and remote-run-2", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221", "fresh": true, "snapshot": false, "output": "aau-gate-h1.txt: tested_state before=5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221 after=5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221; session-gate: all steps exit 0. aau-D6-ui-tests.txt: Test Files  165 passed (165), Tests  1803 passed (1803). aau-D6-py-tests.txt: 3412 passed, 37 warnings in 482.36s (0:08:02). aau-D6-mcp-tests.txt: Tests  560 passed (560). aau-D6-mcp-audit.txt: mcp-audit authoritative: 104/104 pass, 0 discovery finding(s), cleanup ok, exit 0. aau-D6-remote-run-2.txt: remote-run-2: run r20261128T062757Z-ac98b72 ok exit=0; row-check remote-run-2: 0 problem(s)"}
```

### Quality Gate Results

The session gate is in the MEU-173 handoff: run r11, after the round-1 corrections, passed all 33 steps (ui-tests 1803 of 1803, py-tests 3412, MCP 560 of 560, the tool audit 104 of 104, remote-run-2 bound to run `r20261128T062757Z-ac98b72`), with the identity unchanged.

---

## Changed Files

Counts are added / removed lines against `HEAD` `5e4ec2f` (`git diff --numstat --ignore-cr-at-eol HEAD`); a new file's count is its line count. The MEU-173 files are in that handoff.

| File | Change | Added / removed |
|------|--------|-----------------|
| `ui/src/main/app-updater.ts` | the updater; `hardenUpdater()` (D-1591, D-1592) | new, 443 |
| `ui/src/main/update-schedule.ts` | the interval schedule | new, 39 |
| `ui/src/main/index.ts` | the updater at start; one `shutdownForQuit()` (D-1571); `applyAppUserModelId` in `boot()` (D-1583) | +143 / -9 |
| `ui/src/main/ipc.ts` | the update channels | +23 / -0 |
| `ui/src/main/preload.ts` | the update bridge | +16 / -0 |
| `ui/src/renderer/src/env.d.ts` | the bridge's types | +4 / -0 |
| `ui/src/renderer/src/features/settings/UpdatesCard.tsx` | the Updates card | new, 185 |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | the card in the page; `GridSelect` exported (D-1573) | +8 / -1 |
| `ui/src/renderer/src/features/settings/settings-schemas.ts` | `update_interval` | +3 / -0 |
| `ui/src/renderer/src/features/settings/settings-sections.ts` | the Updates section | +2 / -0 |
| `ui/build/installer.nsh` | `customCheckAppRunning` (D-1554); `RMDir /r` (D-1553) | +39 / -3 |
| `ui/package.json`, `ui/package-lock.json` | `electron-updater` 6.8.11 and its closure | +2 / -1; +48 / -11 |
| `ui/playwright.install.config.ts` | the install-stage config | new, 26 |
| `ui/tests/e2e-install/install-helper.ts` | install, preconditions, feed server | new, 400 |
| `ui/tests/e2e-install/update-roundtrip.test.ts` | AC-174.18 to AC-174.20 | new, 558 |
| `ui/tests/e2e/app-update.test.ts` | AC-174.15, AC-174.16 | new, 304 |
| `ui/tests/unit/app-updater.test.ts` | AC-174.2 to AC-174.7; F1 and F2 over the real library | new, 845 |
| `ui/tests/unit/update-schedule.test.ts` | AC-174.1 | new, 97 |
| `ui/tests/unit/update-ipc.test.ts` | AC-174.8 | new, 166 |
| `ui/tests/unit/updates-card.test.tsx` | AC-174.12, AC-174.13 | new, 241 |
| `ui/tests/unit/update-uninstall-nsh.test.ts` | AC-174.14 | new, 107 |
| `ui/tests/unit/app-running-nsh.test.ts` | AC-174.21 | new, 174 |
| `ui/tests/unit/install-preconditions.test.ts` | AC-174.18 | new, 175 |
| `ui/tests/unit/app-user-model-id.test.ts` | the AppUserModelId at startup (D-1583) | new, 59 |
| `ui/tests/unit/ipc-channels.ts`, `ipc-strict-census.test.ts`, `login-item-ipc.test.ts`, `mcp-prompt-ipc.test.ts`, `clipboard-image-main.test.ts`, `settings-rail.test.tsx` | pins grown for the new channels and section (D-1569, D-1570, D-1572) | +6 / -0; +7 / -1; +2 / -2; +1 / -1; +1 / -1; +2 / -1 |
| `ui/tests/unit/login-item-nsh.test.ts` | the five `RMDir /r` lines (D-1553) | +5 / -5 |
| `ui/tests/e2e/settings.test.ts`, `ui/tests/e2e/test-ids.ts` | the Updates section and its ids | +1 / -0; +8 / -0 |
| `packages/core/src/avkit_core/domain/wire.py`, `packages/core/src/avkit_core/services/settings.py` | `app.update_interval` | +2 / -0; +2 / -0 |
| `packages/api/src/avkit_api/schemas/settings.py`, `openapi.committed.json` | `SettingsPutIn.update_interval` | +1 / -0; +11 / -0 |
| `mcp-server/src/toolsets/settings.ts` | `update_interval` | +5 / -0 |
| `tests/unit/test_update_interval_setting.py` | AC-174.9 | new, 71 |
| `mcp-server/tests/update-interval-setting.test.ts` | AC-174.11 | new, 45 |
| `tools/e2e_remote.py`, `tools/e2e_host/run-e2e.ps1`, `host-prepare.ps1`, `host-facts.ps1` | the install stage | +105 / -1; +50 / -22; +11 / -0; +4 / -0 |
| `tests/tooling/test_e2e_remote.py` | AC-174.17 | +161 / -0 |
| `.agent/docs/e2e-remote-host.md` | the install stage on the host | +63 / -1 |
| `docs/execution/plans/2026-11-14-capture-shapes-steps/openapi-delta.py` | AC-106.5's set-back (D-1582) | +28 / -1 |
| `packaging/licence-overrides/npm-lazy-val.txt` | the `lazy-val` licence text (D-1577) | new, 26 |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` | `APP-NO-IN-APP-UPDATE` resolved (row 18) | +5 / -5 and +3 / -4 |

Licences of the added closure: `electron-updater` 6.8.11 MIT, `semver` 7.7.4 ISC, `lodash.escaperegexp` 4.1.2 MIT, `lodash.isequal` 4.5.0 MIT, `tiny-typed-emitter` 2.1.0 MIT, and `lazy-val` through its override (D-1577: the package ships no licence file, so the override holds its MIT text with the author line; the `argparse` 2.0.1 Python-2.0 note is recorded there too).

Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Verdict

Pending: the H1-7 execution review.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The first release that carries the feed files; users get the updater from it | Mat's step | Mat | See the MEU-173 handoff |
| D-1543 and D-1544 | open decisions | Mat | See the MEU-173 handoff, with their recommendations; the texts follow the recommendations |
| The root cause for the reflection | H2 | H2-2 | D-1583 and §Root cause above; the plan creates no H2 artifact during H1 |

### Departures and their basis

- **D-1578, D-1579.** Two fixes to the round-trip spec's mechanics between host runs; neither changed what an AC asserts. D-1579's click-then-wait form stays after D-1583, because it is right for a controlled checkbox and the plain form would need another host run to prove.
- **D-1580, then D-1583 and D-1584.** Row 17 was `[B]` (B-17) after three runs; the coordinator found the product cause, D-1583 fixed it and one verification run passed; D-1584 lifted the block and returned rows 18 and H1-3 to their original form. The new test file joined this plan's scope (`baseline-scope.json`, `eol-check.py`, §Files Modified).
- **D-1582.** AC-106.5's delta script gains one set-back for `SettingsPutIn.update_interval`, as D-1600 did for Session 104's cookie shapes; the path joined this plan's scope.
- **D-1591, D-1592 (execution review round 1).** F1: electron-updater 6.8.11 sent a `x-user-staging-id` header and stored the id in `userData/.updaterId`; `hardenUpdater()` replaces the id with the nil UUID, never writes it, and deletes the header before the library's merge, so D-1544's recommended no-identifier contract holds without an M-list change. F2: the library's own logger printed the raw error; it is now the NoOpLogger. Both reach library internals in one typed function that names the library lines, and both have a real-library regression test (Red, then Green).
- **D-1593.** The canonical round-1 review copy took LF, its text unchanged, so the plan's line-ending rule holds.
- **D-1594.** Gate run r10 stopped at the capture audit because the display was off (every grab black); after a non-black probe, gate run r11 passed unchanged.
- **Pins.** The pins files the plan names grew for the new channels and section (D-1569, D-1570, D-1572); `login-item-nsh.test.ts` changed only the five lines D-1553 names, and AC-61.18 at `:124` stays.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-28 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3, H1-4 and H1-5; row 17 passed on the D-1583 verification run |
| Updated | 2026-11-28 | claude-code-local (Claude Opus 5.5) | Execution corrections round 1: F1 and F2 fixed (D-1591, D-1592), the review copy's line ends (D-1593), the display-off stop (D-1594); row 16 rebuilt at snapshot `ac98b72`, row 17 run `r20261128T062757Z-ac98b72` passed; gate run r10 stopped at the capture audit, display off; gate run r11 passed |
