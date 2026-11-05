---
project: "2026-11-04-rc2-fetch-uninstall"
date: "2026-11-04"
source: "docs/build-plan/07-distribution.md#fetch-exit-codes-residual"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-113", "MEU-114"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Fetch script exit codes and a clean uninstall (Session 49)

> **Project:** `2026-11-04-rc2-fetch-uninstall`
> **Build plan:**
> - `docs/build-plan/07-distribution.md` §Fetch script exit codes (residual, `:334`) and §Uninstall removes the installer copy (residual, `:345`)
> - `docs/build-plan/07-distribution.md` §Second release candidate (`:358`) is Local Canon
>
> **Source requests,** Mat, 2026-11-04: "OK we will go with pythorch remove as you originally suggested. All ohter recommendations are accepted. Proceed". That accepted triage D-228 (uninstall removes the installer copy) and the batching that put the exit codes in this session. Later that day: "I thought I deceided to do nothing about FFmpeg. If we build it we will loose on the updates released by ohter builders." Asked whether to do nothing about FFmpeg, keeping libdvdcss in rc.2, Mat answered: "FFmpeg, keeping libdvdcss in rc.2: yes" (D-266). So this session is the two fixes that remain.
> **Known issues:** `FETCH-FFMPEG-EXIT-CODES`, `UNINSTALL-LEAVES-INSTALLER-COPY`.
> **Status:** `in_progress`. `plan_to_exec_gate: human`; Mat's messages above direct planning. Mat's go-ahead is D-278 (2026-11-05), conditional on the D-273 review, which approved round 1 with no blocking finding (`.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-plan-critical-review.md`).
>
> Line anchors are from `main` `d287c55` plus the triage records, which `83229ea` committed without changing them (D-276, not pushed). The tree also holds another session's closeout files. Row 0 records whatever is there at execution time.
>
> The FFmpeg build plan Codex approved is parked, never run, at `docs/execution/plans/2026-11-04-rc2-ffmpeg-uninstall/`. Its approval covers that plan only.

## Goal

**Goal anchor:** Session 49 makes the fetch script return its documented exit codes and makes the uninstaller remove the installer copy, with every outward step waiting on Mat.

Two things are wrong today:

1. **`tools/fetch_ffmpeg_windows.ps1` says exit 2 to 5 in its `exit` lines and returns 1.** `Write-Error` under `$ErrorActionPreference='Stop'` throws before `exit` runs. Exit 6 already avoids this (`:50-52`). The tests only assert non-zero (`tests/unit/test_packaging_installer.py:152,172`).
2. **Uninstall leaves a 340 MB copy of the installer** at `%LOCALAPPDATA%\av-kit-ui-updater\installer.exe`. The electron-builder template writes it on install, and nothing removes it (D-228).

The session ends with both fixes tested and a round trip on this PC that proves the clean uninstall. FFmpeg doesn't change (D-266). Version stays `0.1.0-rc.1`, because MEU-125 moves it, and the local installer is never uploaded.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-04). A headroom binary is on PATH but no payload here is oversized: the scope is a named list of files read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy` with receipts under `C:/Temp/av-kit` and `C:/Temp/av-kit/rc2/`.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, under ledger loops `s49-plan-2026-11-04-rc2-fetch-uninstall` and `s49-execution-2026-11-04-rc2-fetch-uninstall`. Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable or the ledger refuses a round, the fallback is Mat. Each round is metered; the coordinator warns before dispatching.
- **Never in these rows without Mat's words:** commit, push, tag, create or edit a GitHub release, upload an asset, change RC1's state, or author an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-113` | `.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-MEU-113-handoff.md` |
| `MEU-114` | `.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-MEU-114-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-plan-critical-review.md` and `.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts |
| WP-2 | Fetch exit codes (rows 1, 2) | WP-1 | shared | Tests and script |
| WP-3 | Clean uninstall, proved on a repackaged installer (rows 3 to 6) | WP-1 | shared | Macro, pin, `ROUND_TRIP`, round-trip receipts |
| WP-4 | Records (row 7) | WP-2, WP-3 | shared | Hub and register |
| WP-5 | Closeout (H1, H2) | WP-4 | `compact_continue` | Handoffs, review, reflection |

## User Review Required

> [!IMPORTANT]
> **Real installs run on this PC (row 6).** Each phase installs silently into `C:\Temp\av-kit\rc2\install`, launches with a throwaway `AVKIT_APP_DATA`, and uninstalls with `/S`, never `--delete-app-data`. `%LOCALAPPDATA%\av-kit` keeps its top-level entries and the check proves it. **The round trip deletes the 340 MB `%LOCALAPPDATA%\av-kit-ui-updater\installer.exe` left by Mat's earlier install.** It's identical to the RC1 installer (SHA-256 `beabc509…`), and row 0 keeps a copy as `RC1_INSTALLER`. S5 re-checks the machine and stops if anything has changed.
>
> **Keep `npm run dev` closed for rows 0 to 6.** Row 0 reinstalls `ui/node_modules`, which fails while a running dev app holds its files. The app also takes a single-instance lock (`ui/src/main/index.ts:96`), so a running dev app can stop the packaged app in row 6 from starting.
>
> **RC1 isn't touched.** It stays up (D-215, settled by D-266), and no row touches a release.
>
> **The local installer is never uploaded.** It carries version `0.1.0-rc.1`, the same as the published RC1, and holds RC1's stock FFmpeg, because it repackages RC1's unpacked folder.
>
> **libdvdcss stays.** Mat kept FFmpeg as it is, as an accepted risk (D-266). No row changes the pin, the source set or the notices.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `RC1_INSTALLER` | `C:/Temp/av-kit/rc2/rc1-installer.exe`, SHA-256 `beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7`. |
| `PREPACKAGED_INSTALLER` | `C:/Temp/av-kit/rc2/prepackaged-installer.exe`: the new NSIS macro around RC1's unpacked app. |
| `ROUND_TRIP` | `docs/execution/plans/2026-11-04-rc2-fetch-uninstall/install-roundtrip.ps1`. |

### Fetch script exit codes

Each of the six `Write-Error` lines (`:14`, `:18`, `:27`, `:32`, `:42`, `:56`) becomes `[Console]::Error.WriteLine(...)` with the same message, the pattern exit 6 uses at `:51`. The `exit` lines don't change, so the script's codes stay what they already say: 2 for a blank URL, a malformed SHA or a missing archive, 3 for a mismatch, 4 for a missing binary and 5 for a stub. The comment at `:50` names the cmdlet, so it's reworded and moved above the first check, where it explains every path. No caller depends on exit 1: callers read the pin or check for non-zero (`tests/unit/test_packaging_installer.py:110,120`, `tests/unit/test_assemble_ffmpeg_source.py:594`, `tools/deps_report.py:31`, `tools/assemble_ffmpeg_source.py:8`). The script runs its checks in the order exit 4, exit 6, exit 5, so AC-113.4's fixture holds both binaries and `LICENSE.txt`.

### Uninstall macro

`customUnInstall` in `ui/build/installer.nsh` gains this block after its two `DeleteRegValue` lines. The file stays CRLF.

```nsis
${ifNot} ${isUpdated}
  ${if} $installMode == "all"
    SetShellVarContext current
  ${endif}
  Delete "$LOCALAPPDATA\${APP_INSTALLER_STORE_FILE}"
  RMDir "$LOCALAPPDATA\av-kit-ui-updater"
  ${if} $installMode == "all"
    SetShellVarContext all
  ${endif}
${endIf}
```

It mirrors the template that writes the copy (`app-builder-lib/templates/nsis/include/installer.nsh:88-96`), including the switch to per-user app data on a machine-wide install, and `APP_INSTALLER_STORE_FILE` is defined for the uninstaller's compile too (`NsisTarget.js:461-463`, `:609-613`). `RMDir` has no `/r`, so it's the narrowest action available: a folder holding anything else stays. An upgrade doesn't reach the block, because `installUtil.nsh:205-206` always passes `--updated` to the old uninstaller.

**The uninstaller that runs is the one the installed version wrote** (electron.build). So rc.1 to rc.2 still runs rc.1's uninstaller, and the fix takes effect on rc.2's own uninstall. `ROUND_TRIP` tests both.

### `ROUND_TRIP`

A copy of RC1's script, with parameters `-NewInstaller`, `-OldInstaller`, `-OutDir` and `-PreconditionsOnly`, and paths under `C:/Temp/av-kit/rc2/`. It launches the app only, so RC1's installer-identity check (exit 41) and install-root smoke (exit 44) go, because they need a full build's record. It keeps exit codes 40 (S5 precondition), 42 (install failed), 45 (app smoke) and 46 (uninstall left something or changed the app data), and adds 47 for this MEU's checks. RC1's S6 loop only flags a folder that was gained, so it can't see this bug. The updater folder leaves that loop, and these checks are explicit.

| Phase | Steps | Must hold |
|---|---|---|
| Pre-state | Read `%LOCALAPPDATA%\av-kit-ui-updater` | Absent, or holds only `installer.exe` with SHA-256 `beabc509…` |
| A, negative control | `RC1_INSTALLER` install, uninstall | The copy is **still there**. If it isn't, the check observes nothing and the script exits 47. |
| B, fresh new | New install, launch, uninstall | Copy present after install; copy and folder gone after uninstall; `%APPDATA%\av-kit-ui` still there; `%LOCALAPPDATA%\av-kit` top-level entries unchanged |
| C, upgrade | RC1, then new over it, launch, uninstall | App launches; copy and folder gone after uninstall |
| D, install over | New, new again, launch, uninstall | Copy present and app launches after the second install; copy and folder gone after uninstall |

S5 is the gate on the machine as it stands before phase A. Phases C and D then install over the script's own installation on purpose, so S5 doesn't run between their installs. `${isUpdated}`'s skip can't be observed at runtime, because the install rewrites the copy straight afterwards. The macro pin proves that structure (AC-114.1). Process stops are scoped by install path only. `packaged-app-smoke.mjs` is reused from RC1's folder by path.

### MEU-113 `dist-fetch-exit-codes`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `tools/fetch_ffmpeg_windows.ps1` parameters and `AVKIT_FFMPEG_*` env | The script's `param` block | URL non-blank; SHA-256 is 64 hex; archive must exist | PowerShell refuses an unknown parameter |

No REST, MCP or UI surface changes, so `openapi` and `mcp-*` don't apply.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-113.1 | unit | The fetch script exits 2, with its message on stderr, for a blank URL, a malformed SHA and a missing archive. | Local Canon (`FETCH-FFMPEG-EXIT-CODES`; 07 §Fetch script exit codes) | Today each returns 1 (`C:/Temp/av-kit/s49-fetch-exit-probe.txt`) |
| AC-113.2 | unit | It exits 3 on a SHA mismatch. | Local Canon (same) | Today 1 (same receipt) |
| AC-113.3 | unit | It exits 4 when the archive holds no `ffmpeg.exe` or `ffprobe.exe`. | Local Canon (same) | A zip with only `ffprobe.exe`; today 1 (same receipt) |
| AC-113.4 | unit | It exits 5 for a stub of 1024 B or less. The fixture zip holds both binaries and `LICENSE.txt`, because exit 6 is checked first. | Local Canon (same) | A 1024 B `ffmpeg.exe`; today 1 (same receipt) |
| AC-113.5 | unit | The script has no `Write-Error` left, comments included. | Local Canon (same) | A test fails on any occurrence |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Which path returns which code | Local Canon | The script's own `exit` lines; `FETCH-FFMPEG-EXIT-CODES` |
| How a message reaches stderr without a throw | Local Canon | Exit 6's pattern at `:50-52` |
| The two existing tests that only check non-zero | Local Canon | 07 §Fetch script exit codes, "Tests": they move to the exact codes in row 1 |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `tools/fetch_ffmpeg_windows.ps1` | modify | Exit codes |
| `tests/unit/test_packaging_installer.py` | modify | AC-113.1 to AC-113.5; the two existing tests assert exact codes |
| `docs/build-plan/07-distribution.md` | modify | Delivered notes (row 7) |

### MEU-114 `dist-uninstall-installer-copy`

#### Boundary Inventory

No external input surface. The macro reads NSIS variables only, and the path comes from the template's define.

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| None | — | — | — |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-114.1 | unit | `customUnInstall` holds `Delete` and a non-recursive `RMDir` inside the not-updated guard. | Local Canon (07 §Uninstall; D-228) | A macro with the guard removed fails |
| AC-114.2 | unit | The folder name equals `ui/package.json`'s name plus `-updater`. | Local Canon (`app-builder-lib/out/appInfo.js:126`) | A changed name fails |
| AC-114.3 | unit | AC-61.18's two `DeleteRegValue` lines stay the only two, and there's no `RMDir /r`. | Local Canon (AC-61.18; D-258) | An `RMDir /r` fails |
| AC-114.4 | integration | NSIS compiles the macro under `-WX`, through `repackage.ps1`. | Local Canon (`NsisTarget.js:623`) | electron-builder's own exit code |
| AC-114.5 | integration | Phase A: RC1's uninstall leaves the copy, so the check can see the bug. | Local Canon (D-228) | This is the negative control |
| AC-114.6 | integration | Phase B: the new uninstall removes the copy and its folder. | Local Canon (07 §Uninstall) | Phase A |
| AC-114.7 | integration | Phase B: `%APPDATA%\av-kit-ui` stays, and `%LOCALAPPDATA%\av-kit`'s top-level entries are unchanged. | Local Canon (07 §Uninstall; `ui/electron-builder.yml:18`) | Exit 46 or 47 if either changes |
| AC-114.8 | integration | Phase C: RC1 to new launches, and the later uninstall is clean. | Local Canon (07 §Uninstall: an upgrade still works) | Exit 42 or 45 |
| AC-114.9 | integration | Phase D: new over itself keeps the copy and launches, and the later uninstall is clean. | Local Canon (07 §Uninstall) | Exit 47 if the copy is missing after the second install |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| What's removed and what stays | Local Canon | 07 §Uninstall; D-228 |
| The path | Local Canon | The template's define, read at plan time from electron-builder's source |
| Which uninstaller runs | Research-backed | electron.build NSIS docs |
| Which installer proves it | Local Canon | D-268: the repackaged RC1 app here, the full build in MEU-125 |
| Naming `%APPDATA%\av-kit-ui` in the notes | Local Canon | Deferred to MEU-125, whose §Second release candidate writes the notes |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/build/installer.nsh` | modify | The block in §Uninstall macro |
| `ui/tests/unit/login-item-nsh.test.ts` | modify | AC-114.1 to AC-114.3 |

### Project files

Plan-local scripts, listed in §Verification Plan: `baseline.sha`, `baseline-dirty.txt`, `baseline.ps1`, `red-check.py`, `identity.py`, `repackage.ps1`, `install-roundtrip.ps1`, `issue-decisions.py`, `session-gate.ps1`. State: `docs/BUILD_PLAN.md` (rendered), `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `.agent/context/known-issues.{yaml,md}`, `.agent/context/triage-output.yaml`, `.agent/context/current-focus.md`, `docs/execution/metrics.md`, the handoffs, the rolling reviews and the reflection.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Release-notes wording for `%APPDATA%\av-kit-ui`, RC2 notes | deferred | MEU-125 | `07-distribution.md:358` §Second release candidate owns the notes; they can only be written once rc.2's contents are known |
| Version bump to `0.1.0-rc.2` | deferred | MEU-125 | `07` §Second release candidate; AC-110.9 keeps one version across surfaces until then |
| RC2 publish checklist, moving `ROUND_TRIP` into `tools/` if rc.2 needs it, and its run on the full build | deferred | MEU-125 | D-268; `07:367` names MEU-114's round trip on the full build |
| RC1 notes corrections (D-216) | deferred | MEU-125 | Grouping §5; carried into rc.2's notes |
| RC1's state | out-of-scope | — | Settled by D-215 and D-266; no row touches a release |
| The FFmpeg pin, a custom build, naming libdvdcss in NOTICES | out-of-scope | — | D-266 keeps the pin. Whether the notices name libdvdcss is a question for Mat, and no row changes them unless Mat rules |
| `_extract` left behind on exits 4 and 5 | out-of-scope | — | `07` §Fetch script exit codes covers codes only; existing behaviour |
| The validator refusing the register's YAML, and repeated `--decision-issue` flags keeping only the last | out-of-scope | — | Tooling, worked around here without changing it (D-272). Whether to register or fix it is a question for Mat |
| Other triage MEUs | out-of-scope | — | Grouping sessions 50 to 57 |

## BUILD_PLAN.md Audit

This project adds no build-plan section; the two residual sections were registered with the triage and re-scoped with D-266. `docs/BUILD_PLAN.md` regions regenerate through `tools/meu_status.py render`, and row 7 is the explicit D3 hub task.

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s49-render-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s49-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` records `HEAD` in `baseline.sha` and `git status --porcelain` in `baseline-dirty.txt`. It copies `ui/dist/av-kit-Setup-0.1.0-rc.1.exe` to `RC1_INSTALLER` and checks its SHA-256 **before anything can overwrite it**, and it requires `ui/dist/win-unpacked/av-kit.exe`, which row 4 packs. It then runs `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `node ui/node_modules/electron/install.js`, `npm --prefix mcp-server ci` and `npm --prefix mcp-server run build`, and captures the base suites to `s49-base-py.txt` and `s49-base-ui.txt`. Row 0 then runs `red-check.py --selftest` and `identity.py --selftest`.

Pytest runs with `TMP` and `TEMP` at `C:\Temp\av-kit\rc2\tmp`, as RC1 did, so the selftest arms aren't misled by `C:/Users/Mat/.agent` (RC1 ECN-2, `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`). Only ids the baseline receipt really shows failing are excused. `AC-24.10` and `AC-25.10` depend on gitignored binaries being present.

`red-check.py` and `identity.py` are copies with this plan's values. This session adds no new names, so `DECLARED_NEW` holds only the five `red-check.py --selftest` needs (`resizeBox`, `hitResizeHandle`, `capture-transform`, `boxHandlePoints`, `scaleTextMark`). `PLAN` holds this folder and `PROJECT_ARTIFACTS` this plan's files.

### 2. Red then Green (rows 1 to 4)

Each Red receipt holds an assertion failure, never a setup failure. Pytest names are `test_ac_113_<n>_…`, so `--require test_ac_113_<n>` matches them exactly (`red-check.py:209`). Vitest titles begin `AC-114.<n>`. Expectations stay immutable in Green. Rows 1 to 4 preserve each file's CRLF line endings.

### 3. Prepackaged proof of MEU-114 (rows 4 to 6)

`repackage.ps1` clears `ELECTRON_RUN_AS_NODE`, requires `RC1_INSTALLER`, and runs this from `ui`:

```powershell
npx electron-builder --win nsis --x64 --publish never --prepackaged dist/win-unpacked -c.directories.output=C:/Temp/av-kit/rc2/prepackaged-out
```

It then copies the result to `PREPACKAGED_INSTALLER`. That proves the macro under `-WX` (AC-114.4) with no build of the app. The output override keeps RC1's installer in `ui/dist` untouched, because `ui/electron-builder.yml:5` sets `output: dist` and electron-builder merges `-c.` values over the file (`app-builder-lib/out/util/config/config.js:23`). It isn't a write barrier on the input folder: electron-builder can still refresh `resources/elevate.exe` inside `dist/win-unpacked` (`nsisUtil.js:119-121`, `packager.js:431-437`), as the plan review noted. If `--prepackaged` refuses, S2 applies.

### 4. Triage decisions at closeout (rows 7 and H2-2)

The closeout validator can't read `known-issues.yaml` as `model.save` writes it. Its bounded grammar refuses the indentless lists and the values wrapped at 200 characters, so it refuses both issues this reconciliation needs (D-272). `--decision-issue` also keeps only its last value (`tools/validate_closeout_artifacts.py:5556`), so naming two issues in one run would check one.

`issue-decisions.py` loads the register through `model.load`, keeps `id` and `enrichment.decision_log` for `UNINSTALL-LEAVES-INSTALLER-COPY` and `FFMPEG-LIBDVDCSS-BUNDLED`, and writes them to `C:/Temp/av-kit/rc2/issue-decisions.yaml` with indented lists and no wrapping. It reads the file back and exits non-zero unless the data equal the register's and the validator's own `issue_decision_log` returns the ids the register holds. Row 7 writes and runs it, so the review sees it. H2-2 runs it again, then runs the validator once per issue against the file. `FETCH-FFMPEG-EXIT-CODES` holds no decisions, so it needs no run. The validator and the register's format don't change.

### Plan-local scripts

Written with their rows and kept in this plan folder:

- `baseline.ps1` (row 0)
- `red-check.py`, `identity.py` (row 0)
- `repackage.ps1` (row 4)
- `install-roundtrip.ps1` (row 5)
- `issue-decisions.py` (row 7)
- `session-gate.ps1` (H1-2)

### Session gate (H1-2)

`session-gate.ps1` is RC1's shape: one receipt per step in `C:/Temp/av-kit`, named `s49-D6-<step>`, fail-fast, later steps printed `not_run`, `TMP` and `TEMP` set as in §1, `ELECTRON_RUN_AS_NODE` cleared. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `state-render` |
| Skipped, with reason | `openapi`: no `packages/api` change. `mcp-types`, `mcp-tests`, `mcp-build`, `mcp-audit`: no MCP change; the audit is required before the version bump, which is MEU-125. `ui-electron`: no main, preload or renderer change, and `packaged-app-smoke.mjs` launches the real packaged Electron in row 6. `build-record`: this session makes no full build. |

`py-tests` keeps RC1's baseline rule: it excuses only `test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]` and `test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]`, and only if row 0's receipt shows them failed. `ui-tests` excuses nothing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | `--prepackaged` refuses | Stop, record an ECN and bring it to Mat, or move AC-114.4 to AC-114.9 to MEU-125's build with those ACs named open |
| S3 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S4 | `HEAD` moves from `baseline.sha`, or a path outside `baseline-dirty.txt` and this plan appears | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | Before any install: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` or `...\Explorer\StartupApproved\Run` has `com.avkit.app`; an av-kit Uninstall entry exists; `C:\Temp\av-kit\rc2\install` exists; `%LOCALAPPDATA%\Programs\av-kit` holds anything; a Desktop or Start Menu `av-kit.lnk` exists; `av-kit.exe` is running; or `%LOCALAPPDATA%\av-kit-ui-updater` holds anything but the known copy | Skip the install, record `[B]`, list it for Mat |
| S6 | An uninstall leaves something else behind, or `%LOCALAPPDATA%\av-kit` loses a top-level entry | Report with the snapshot diff; don't retry |
| S7 | Codex is unavailable or the ledger refuses | Mat |

## Decision Log

> [!WARNING]
> Mat ruled D-273, D-276 and D-278 on 2026-11-05, recorded below; no other decision here needs Mat. Carried from the grouping and not relisted in the block, because the grouping's rows hold them: every §8 row, D-240 to D-250, D-267, D-277 and D-280. The closeout validator reads all of them, and D-246 stays as a withdrawn row. D-214, D-215, D-228, D-266 and D-275 are in `.agent/context/known-issues.yaml`. The parked plan's D-246, D-251 to D-257 and D-259 to D-265 went away with the build, so they aren't carried. Its D-258 is carried below because it still applies.

```yaml
decision_log:
  - id: D-258
    stage: planning
    question: "How does the macro remove the copy?"
    resolution: autonomous
    class: two-way
    chosen: "Delete through the template's own define, then a non-recursive RMDir, inside the not-updated guard"
    source_tag: Local Canon
    precedents: ["ui/build/installer.nsh — customUnInstall", "ui/electron-builder.yml:18 — deleteAppDataOnUninstall stays false"]
    research: { engine: tavily, sources: ["https://www.electron.build/docs/nsis — the uninstaller semantics"] }
    reasoning: "No recursive delete on an environment-derived path. A folder holding anything else stays."
  - id: D-268
    stage: planning
    question: "Does MEU-114 wait for a full build?"
    resolution: autonomous
    class: two-way
    chosen: "No. It is proved here on a repackaged RC1 installer, and the round trip on the full build moves to MEU-125"
    source_tag: Local Canon
    precedents: ["docs/build-plan/07-distribution.md:352 — an upgrade is checked on the next build", "docs/build-plan/07-distribution.md:367 — MEU-125 runs MEU-114's round trip on the full build"]
    research: { engine: none, sources: [] }
    reasoning: "The macro is the only input that changes, and the repackaged installer compiles it under the real settings with the real app. A full build here would add hours and prove nothing more about the macro. MEU-125 builds anyway, and the alternative of building twice loses on cost."
  - id: D-269
    stage: planning
    question: "Which version does the local installer carry?"
    resolution: autonomous
    class: two-way
    chosen: "The app version stays 0.1.0-rc.1, and the installer is never uploaded"
    source_tag: Local Canon
    precedents: ["docs/build-plan/07-distribution.md:364 — MEU-125 moves the version", "tests/unit/test_release_packaging.py:27 — one version across surfaces"]
    research: { engine: none, sources: [] }
    reasoning: "Moving the version here would make a surface change for a build that nobody receives, and a local-only suffix would fail the one-version check. Phase C still installs over RC1, because NSIS runs the old uninstaller whatever the version is."
  - id: D-270
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "Identity, static, the Python and UI suites, the UI build and the state render, with MCP, OpenAPI, Electron E2E and the build record skipped for the reasons in the plan's §Session gate"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:190-207 — the D6 stages", "AGENTS.md:82 — one fresh full scoped gate before final review"]
    research: { engine: none, sources: [] }
    reasoning: "The session changes one PowerShell script, one NSIS macro, two test files and records. No API, MCP or renderer code moves, and row 6 launches the real packaged Electron. Running the skipped steps would cost time and exercise nothing this session changed."
  - id: D-271
    stage: planning
    question: "Edit the approved plan or write a new one?"
    resolution: autonomous
    class: two-way
    chosen: "A new folder, goal and review loop. The approved plan stays unchanged and parked"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-04-rc2-ffmpeg-uninstall/PARKED.md — what stays valid and what moved on", ".agent/context/handoffs/2026-11-04-rc2-ffmpeg-uninstall-plan-critical-review.md — the approval is bound to that plan"]
    research: { engine: none, sources: [] }
    reasoning: "The review is bound to the old plan's bytes and its frozen goal, and that goal is no longer the session's. Editing it would leave an approval that describes a different plan. Whether the new plan gets a new review or Mat reads it is Mat's call, because the old loop's budget is spent."
  - id: D-272
    stage: planning
    question: "How does closeout reconcile the triage decisions when the validator refuses the register's YAML?"
    resolution: autonomous
    class: two-way
    chosen: "A plan-local script writes the two issues' decision logs, content unchanged, to a temp file in the grammar the validator reads, and the unmodified validator reads that once per issue"
    source_tag: Local Canon
    precedents: ["tools/issue_triage/model.py:345 — save writes indentless lists and wraps at 200", "tools/validate_closeout_artifacts.py:1480 — issue_decision_log reads the bounded grammar", ".agent/docs/human-decision-protocol.md:201 — the reconciliation and its grammar"]
    research: { engine: none, sources: [] }
    reasoning: "Measured 2026-11-04: the reader refuses 64 of the register's 66 decision logs, and 44 of 46 at HEAD. Changing the validator or the writer is tooling work, and changing the writer would rewrite the whole register, so neither belongs in this session. Dropping the check would leave D-214, D-215, D-228 and D-266 unreconciled. The script changes no content and fails unless the validator reads the ids the register holds. Whether to fix the tooling is a question for Mat."
  - id: D-273
    stage: plan-review
    question: "Who reviews this plan, now that the old loop's budget is spent and its frozen goal was removing libdvdcss?"
    resolution: human
    class: governance-value
    chosen: "Codex, in the new loop s49-plan-2026-11-04-rc2-fetch-uninstall, with the prompt limited to what the earlier approval did not cover: D-272, repackage.ps1, the changed ROUND_TRIP and S2"
    source_tag: Human-approved
    precedents: [".agent/docs/model-routing.md:23 — a new loop must not evade a stop", ".agent/workflows/execution-session.md:207 — never open a fresh loop to route around a stop", "docs/execution/reflections/2026-11-03-release-rc1-reflection.md:125 — D-210, same loop while the goal was unchanged"]
    research: { engine: "pomera_web_search (tavily, exa)", sources: ["https://www.augmentcode.com/guides/adversarial-code-review — spend review budget by blast radius", "https://dev.to/theaicommit/how-to-tell-whether-a-second-model-reviewing-your-agents-work-pays-for-itself-pel — a reviewer must fail differently from the drafter"] }
    reasoning: "The new loop is legitimate only as Mat's ruling, because this plan has a different goal from the one the old loop froze. Rows 3 to 6 install, uninstall and delete on Mat's machine, so those parts get the second vendor. Alternatives were Mat reading the delta, continuing the old loop against a dead goal, and no plan review."
    human_message_reference: "USER_EXPLICIT 2026-11-05 'all recommendations are accpeted, proceed'"
  - id: D-276
    stage: planning
    question: "Are the triage records committed before execution?"
    resolution: human
    class: two-way
    chosen: "Yes: one exact-scope commit of this session's triage and planning records, without this plan folder and without a push. The push is a separate approval, after Mat reads the register's libdvdcss wording"
    source_tag: Human-approved
    precedents: ["docs/execution/reflections/2026-11-03-release-rc1-reflection.md:130 — D-237, exact-scope mode, the register goes out with the triage commit", ".agent/skills/git-workflow/SKILL.md:59 — exact-scope signed commit mode"]
    research: { engine: "pomera_web_search (tavily, exa)", sources: ["https://amanerp.com/engineering/git-footgun-parallel-agents — git commit with paths stages the whole working file, so an isolated index is the safe form"] }
    reasoning: "Row 0 then baselines a tree holding only this plan and the other session's files. The plan folder stays out because the review may change it. The repository is public, so the push waits."
    human_message_reference: "USER_EXPLICIT 2026-11-05 'all recommendations are accpeted, proceed'"
  - id: D-278
    stage: planning
    question: "Does execution start?"
    resolution: human
    class: one-way-door
    chosen: "Yes, once the D-273 review approves with no blocking finding"
    source_tag: Human-approved
    precedents: [".agent/context/harness.local.md — plan_to_exec_gate is human for Claude Code"]
    research: { engine: "pomera_web_search (tavily)", sources: ["https://www.electron.build/docs/nsis — the uninstaller that runs is the one the installed version wrote"] }
    reasoning: "Mat accepted the recommendation that execution follows a clean review. A review that asks for changes is answered first, and if a fix changes what the plan does on Mat's machine, the coordinator returns to Mat."
    human_message_reference: "USER_EXPLICIT 2026-11-05 'all recommendations are accpeted, proceed'"
```

## Research References

- electron-builder NSIS: https://www.electron.build/docs/nsis. Official.

## Planning receipts

- Exit codes today: `C:/Temp/av-kit/s49-fetch-exit-probe.txt`, from throwaway zips in `C:/Temp/av-kit/s49-fetch-probe/`. A blank URL, blank SHA, malformed SHA, missing archive, mismatch, missing binary and stub each return 1. A missing licence returns 6 and a good archive 0. The October receipts this replaces are `fetch-exit-blank-sha.txt` and `fetch-exit-sha-mismatch.txt`.
- electron-builder's own source for `--prepackaged` and the `-c.` merge: `ui/node_modules/electron-builder/out/builder.js:247,257`, `ui/node_modules/app-builder-lib/out/util/config/config.js:23`.
- Measured on 2026-11-04: `HEAD` `d287c55`; `%LOCALAPPDATA%\av-kit-ui-updater\installer.exe` 340,348,020 B, SHA-256 `beabc509…`, identical to `ui/dist/av-kit-Setup-0.1.0-rc.1.exe`; `%LOCALAPPDATA%\Programs\av-kit` absent; `ui/dist/win-unpacked/av-kit.exe` present; `C:/Temp/av-kit/rc2` absent.
- The closeout reader on the register, measured on 2026-11-04: it refuses 64 of 66 decision logs, and 44 of 46 at `HEAD`. Through a prototype of `issue-decisions.py`, `decision_sources` read 18 decisions for the uninstall issue and 20 for the FFmpeg issue: D-258 and D-268 to D-271 at the time, the 12 grouping rows, and D-228 or D-214, D-215 and D-266. D-228's `chosen` said `${isUpdated}`, which the placeholder check refuses, so it now says "except when the uninstaller runs for an update". The meaning is the same.
- The macro, MEU-114's ACs and S5 come from the plan Codex approved on 2026-11-04, which covered that plan only.
- Not run at plan time: `--prepackaged`, any install.

## Validation stage contract

Static: `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths`, `red-check-selftest`. Targeted: the named test files in each Red and Green row. Fresh full: `py-tests`, `ui-tests`, `ui-build`, `state-render`. Runtime: row 6 (real NSIS install, real packaged Electron). Identity comes from `identity.py`, independent of the receipts. Blocking: all, native shell PowerShell, `evidence.v1` output. Intermediate reuse stays off.
