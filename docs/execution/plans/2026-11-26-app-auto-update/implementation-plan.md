---
project: "2026-11-26-app-auto-update"
date: "2026-11-26"
source: "Mat's request, 2026-11-26 (USER_EXPLICIT): 'Create addtional plan for integration of update feature from within the app so the user does not have to go to github realease to download and run the update but it happens automaticly. Also have setting to check updates once a week or once a month.'; registered as APP-NO-IN-APP-UPDATE (triage D-1409) and MEU-173, MEU-174 in docs/build-plan/07-distribution.md §Update feed (residual) and §In-app update (residual); Session 106 of the grouping"
grouping_source: ".agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md"
meus: ["MEU-173", "MEU-174"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: the app checks GitHub Releases on a schedule, downloads a newer version and installs it on one click

> **Project**: `2026-11-26-app-auto-update`
> **Build Plan Section(s)**: 07 §Update feed (residual) (`docs/build-plan/07-distribution.md`, anchor `update-feed-residual`, matrix 7.10, MEU-173) and 07 §In-app update (residual) (anchor `in-app-update-residual`, matrix 7.11, MEU-174). Parent canon: 07 §Goal, 07 §Electron packaging (Auto-update row, Code signing row), 06 §Settings.
> **Status**: `draft`. `plan_to_exec_gate: human`. Execution approval (S1, written at row 0 on 2026-11-27): the plan review approved this plan at round 3; Mat gave the word to execute on 2026-11-26, 'go for 104 after the reviews finish and then execute rest as you see fit', and on 2026-11-27, 'commit 103 and go for 106'. Execution commits nothing and pushes nothing. The grouping's run parameters for this session are `decisions=hdp · commit_plan=false · exec_after_plan=false · commit_exec=false · push=never`, so nothing here starts execution, commits or pushes. The grouping's D-1413 is ruled: Mat, 2026-11-26, 'drafts stand' (human), so this draft is no longer provisional. Two briefs of this plan are Mat's and stay `open`: D-1543 (trust for an unsigned update) and D-1544 (the new outbound request). The tasks build the recommended option of each. They may run while the two are unruled, because nothing reaches a user before Mat's own release; the handoff, the next-session prompt and the release checklist carry both briefs as open. A different ruling changes the rows named in each brief (S2).

---

## Goal

**Goal anchor:** an installed av-kit learns of a newer release by itself and installs it without a visit to the release page. On the schedule the user picks in Settings (once a week, the default; once a month; or never), the packaged app asks the public repository's releases for the version GitHub marks Latest. If it is newer, the app downloads the installer in the background, checks it against the feed's SHA-512, tells the user once, and shows **Restart and update** in Settings. One click there stops the backend in the app's own order, runs the installer silently and starts the new version. The app never restarts by itself. A release build writes the two feed files beside the installer, a script checks them against the built installer, and the upload stays Mat's step. Unit tests, an Electron E2E against a local feed, and a real update from one built version to the next on the mini-air host prove it, with no manual check.

**Why.**

- **Mat, 2026-11-26:** "Create addtional plan for integration of update feature from within the app so the user does not have to go to github realease to download and run the update but it happens automaticly. Also have setting to check updates once a week or once a month."
- `docs/releases/v0.1.0-rc.5.md:29` tells users "av-kit doesn't update itself. To move to a later version, download that version's installer." Five release candidates shipped in three weeks; each fix reaches a user only if that user comes back to the release page.
- **Mat, 2026-11-16:** "This should be done with framework and scripts!" So every behaviour check is a test in the gate or a script on the E2E host.

**What the code and the sources show (plan-time reads at `HEAD` `c0acc89`, 2026-11-26):**

- **No feed.** `ui/electron-builder.yml` has no `publish` block; `ui/package.json` has no `electron-updater`. `docs/releases/publish-checklist-v0.1.0-rc.2.md:91` says "`latest.yml`, the `.blockmap`, `builder-debug.yml` and `win-unpacked/` stay here."
- **Installed versions.** `electron-builder` 26.18.0, `app-builder-lib` 26.18.0, `builder-util-runtime` 9.7.0, `electron` 42.11.18, `electron-store` 8.2.0 (read from `ui/node_modules`). `electron-updater` `latest` is 6.8.11 (npm, 2026-10-20), MIT, the companion of the 26 line.
- **A script that can publish.** `ui/package.json:29`: `"dist": "npm run dist:prep && electron-builder --win nsis --x64"` has no `--publish never`. Today that is harmless, because there is no `publish` block. With one, electron-builder's default publish policy applies to this script on a tag or in CI. The CI workflow and the release build script pass `--publish never` (`.github/workflows/build-windows.yml:73`; `docs/execution/plans/2026-11-22-release-rc5/build-rc5.ps1`), and `tests/unit/test_ci_workflows.py:73-78` pins the workflow only.
- **The GitHub provider (electron-updater 6.8.11 source).** For github.com it uses web URLs, not the API: `…/releases.atom`, `…/releases/latest` and `…/releases/download/<tag>/<channel>.yml`. `allowPrerelease` defaults to true when the running version has a prerelease part, so an installed `0.1.0-rc.5` would by default follow only `rc` tags and never see a stable `0.1.0`. With `allowPrerelease = false` it follows the one release GitHub marks Latest and reads `latest.yml`. GitHub's Latest never names a release flagged pre-release. av-kit publishes each release candidate with `--latest` and no pre-release flag (`release-rc5`), so Latest is the newest release candidate today.
- **Unsigned.** The installer has no publisher signature (07 `:196`). The updater then checks only the SHA-512 that `latest.yml` carries. Nothing authenticates `latest.yml` in the 26 line; signed manifests exist only in the 27 alpha.
- **The installer on an update** (`ui/node_modules/app-builder-lib/templates/nsis/`): started with `--updated /S --force-run`, it runs the running-app check (`include/allowOnlyOneInstallerInstance.nsh:32-43`, inserted at `installSection.nsh:33` and `:36`; the old uninstaller that an update runs makes the same check from `un.onInit`, `uninstaller.nsh:1-3`), replaces the files, and starts the app again through the shell with `--updated` (`common.nsh:123-131`, `installSection.nsh:85-108`). `ui/build/installer.nsh` skips its app-data lines when `${isUpdated}`, so an update deletes no user data. A start through the shell does not inherit the old process's environment.
- **The stock running-app check is not bounded** (`include/allowOnlyOneInstallerInstance.nsh`). With PowerShell it stops every process whose path starts with the install folder's text, with no separator check (`:66`, `:94`), so a sibling folder such as `…\av-kit-old` matches. When PowerShell is missing or its policy is `Restricted`, it falls back to `tasklist` and `taskkill /IM av-kit.exe` for the user (`:71-75`, `:97-99`), which stops every `av-kit.exe` of the account, a development worktree's or another install's included. A macro `customCheckAppRunning` replaces the whole check (`:5-8`, `:37-38`). The custom include `build/installer.nsh` is part of the shared header that precedes both the installer and the uninstaller script (`out/targets/nsis/NsisTarget.js:393`, `:408`, `:463`, `:709-712`), so the macro is defined before `allowOnlyOneInstallerInstance.nsh` is read. `APP_RUNNING_CHECK` (D-1554) uses it.
- **The MCP server is the app's own exe.** A client runs `av-kit.exe` with `ELECTRON_RUN_AS_NODE=1` (`ui/src/main/mcp-setup-prompt.ts:59`), so the installer's stop reaches it too. The app does not own that process.
- **Quit order today.** `ui/src/main/index.ts` `before-quit` calls `setQuitIntent()`, then `shutdownOwned('quit', …)` (`python-manager.ts:70`: signal the backend pid, wait for its exit, retire the descriptor), then `app.exit(0)`.
- **Settings layers.** A leaf lives in the core registry (`packages/core/src/avkit_core/services/settings.py`, `SettingSpec` keyed `(namespace, leaf)`), a wire set (`domain/wire.py`), the flat API model (`packages/api/src/avkit_api/schemas/settings.py` `SettingsPutIn`, extra fields refused), the UI Zod schema (`settings-schemas.ts` `appPutSchema`, `.strict()`), the Settings page, the MCP tool (`mcp-server/src/toolsets/settings.ts:53-57` and `settingsLeaves`) and the 06 settings table (`06-gui.md:1079-1081`). The `app` namespace exists, so `domain/settings.py` and `routes/settings.py` need no change.
- **Main-process state.** `index.ts:486` keeps `new Store({ cwd: appData, name: 'ui-state' })`; the same package can hold the updater's small state file.
- **No busy signal.** `/downloads`, `/transcripts` and `/conversions` each report a processor state; `/tts` has no list route. Nothing in the app answers "is any job running".
- **The remote E2E tool installs nothing.** `.agent/docs/e2e-remote-host.md`: "The tool never stops a process, never installs anything". It archives one commit, builds `ui/out-e2e`, and the scheduled task runs Playwright from `runs\<id>\tree\ui` with no arguments. It cannot carry an installer today. Smart App Control is on at the host (run book `:366`, D-1216, Mat's).
- **The host was not reachable at plan time.** `ssh -o BatchMode=yes -o StrictHostKeyChecking=yes mini-air12` timed out on 2026-11-26 (`plan-host-facts.txt`). No host fact in this plan is measured; row 0 measures them.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and ui/graphify-out/ are absent (2026-11-26). The surfaces were read directly at plan time: the settings layers, the main-process IPC and quit path, the builder config, the NSIS templates in node_modules, the remote E2E tool and its run book."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code on Mat's Windows host; the Claude Code block of `.agent/context/harness.local.md` applies (`fresh_worker: Agent tool`, `plan_to_exec_gate: human`).
  - Task-cell commands run in pwsh from `P:/av-kit` through `rtk proxy` with the receipt pattern. Receipts go to `C:/Temp/av-kit/2026-11-26-app-auto-update/`, execution receipts start `aau-`. Planning receipts are under `C:/Temp/av-kit/2026-11-26-plans/s106/`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool. In the Bash tool a redirect is `> file 2>&1`, never `*>`.
  - Vitest, pytest and the type checks stay on the dev PC. **Every Electron run is on the mini-air host** (grouping D-1411), through `uv run python tools/e2e_remote.py run <commit>` on a snapshot commit that moves no ref. No row launches Electron on the dev PC.
  - No row stops a process by image name. No row runs `npm ci --ignore-scripts` in `P:/av-kit/ui`.
- **Working directory:** `P:/av-kit` on `main`. No branch, no worktree. `.agent/fleet/hub` is never opened.
- **Network:** two rows reach the network: row 0 reads the npm dist-tags, and row 13 installs `electron-updater` from the npm registry. No row reaches GitHub Releases, and no test does: every feed in a test is `127.0.0.1`.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`; the orchestrator dispatches the plan review, not this plan's author. Ledger loops `aau-plan-2026-11-26-app-auto-update` and `aau-execution-2026-11-26-app-auto-update`; caps from `.agent/review-limits.json` (3 plan rounds, 6 execution rounds). The fallback reviewer is Mat.
- **Never in these rows:** commit, push, tag, upload, a GitHub release, a version change, or an `approved` verdict written by the implementer.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-173 Update feed | `.agent/context/handoffs/2026-11-26-app-auto-update-MEU-173-handoff.md` |
| MEU-174 In-app update, the host payload stage and the round trip | `.agent/context/handoffs/2026-11-26-app-auto-update-MEU-174-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-26-app-auto-update-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-26-app-auto-update-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline, plan-local scripts, host facts, pin scan (row 0) | — | shared | `baseline.sha`, `baseline-scope.json`, `baseline-eol.json`, `baseline-pins.json`, `aau-host-check-0.json`, the copied scripts |
| WP-2 | MEU-173: feed config, feed check, checklist; MEU-174's bounded running-app check (AC-174.21), which the first build must carry; a real build (rows 1 to 3, with 2a and 2b) | WP-1 | shared | `electron-builder.yml`, `package.json`, `tools/check_update_feed.py`, the checklist, `app-running-nsh.test.ts`, the running-app macro in `installer.nsh`, `aau-feed-real-3.json`, `aau-row3-macro.json` |
| WP-3 | Host payload stage, the E2E Red spec, host run 1 (rows 4 to 7) | WP-2 | `compact_continue` | The tool and host scripts, the run book section, `ui/tests/e2e-install/`, `ui/tests/e2e/app-update.test.ts`, the run 1 receipts |
| WP-4 | MEU-174 setting in core, API and MCP (rows 8 to 11) | WP-1 | shared | The leaf in every backend layer, `openapi.committed.json`, the MCP schema |
| WP-5 | MEU-174 main process and renderer (rows 12 to 15) | WP-4 | `compact_continue` | `update-schedule.ts`, `app-updater.ts`, IPC, preload, the Updates card, the lock file, the cache macro |
| WP-6 | The version pair and host run 2 (rows 16 and 17) | WP-3, WP-5 | `compact_continue` | The round-trip spec, `aau-pair-16.json`, the run 2 receipts |
| WP-7 | Canon, public statements, register and status (row 18) | WP-6 | shared | 07, 06, README, the registry files, the issue |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | The two handoffs, the review, the reflection, the commit draft |

At each `compact_continue` boundary the next row re-reads `task.md`, this plan's §Single-statement contracts and the durable outputs of the package before it.

## Lane Ownership

Copied from the grouping's `## Session Ownership` (tier 2):

```yaml
app-auto-update:
  tier: 2
  owns:
    - ui/electron-builder.yml
    - ui/package.json
    - ui/src/main/
    - packages/core/src/avkit_core/services/settings.py
    - packages/core/src/avkit_core/domain/wire.py
    - packages/core/src/avkit_core/domain/settings.py
    - packages/api/src/avkit_api/schemas/settings.py
    - packages/api/src/avkit_api/routes/settings.py
    - openapi.committed.json
    - ui/src/renderer/src/features/settings/
    - mcp-server/src/toolsets/settings.ts
    - docs/build-plan/07-distribution.md
    - docs/releases/
    - docs/execution/plans/2026-11-26-app-auto-update/
```

**Paths this plan needs that the list does not name** (the orchestrator adds them or rules before row 0; until then S4 treats another session's dirty copy of any of them as a stop):

- `ui/package-lock.json` (the new dependency), `ui/build/installer.nsh` (D-1553, D-1554), `ui/tests/unit/`, `ui/tests/e2e/app-update.test.ts`, `ui/tests/e2e-install/` (new folder), `ui/playwright.install.config.ts` (new).
- `tools/check_update_feed.py` (new), `tools/e2e_remote.py`, `tools/e2e_host/run-e2e.ps1`, `tools/e2e_host/host-prepare.ps1`, `tools/e2e_host/host-facts.ps1`, `.agent/docs/e2e-remote-host.md`, `tests/unit/` (new test files and `test_e2e_remote.py`), `mcp-server/tests/`, `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` (only if the audit reads the leaf list).
- `docs/build-plan/06-gui.md` (the settings table and the section list; Sessions 104 and 105 change other sections), `README.md`.
- The shared registry files in row 18: `docs/BUILD_PLAN.md`, `docs/build-plan/build-priority-matrix.md`, `.agent/context/meu-registry.md`, `.agent/context/meu-status.yaml`, `.agent/context/known-issues.yaml` and `.md`.

**Overlaps with other sessions:** `openapi.committed.json` is also owned by Session 104 (tier 1); `ui/src/renderer/src/features/settings/settings-help-content.ts` is named by Session 103 (tier 1). This plan does not change `settings-help-content.ts`. The grouping's execution order (104, 103, 106, 105) puts both tier 1 sessions before this one. `domain/settings.py` and `routes/settings.py` are owned and not changed.

## User Review Required

> [!IMPORTANT]
> **Two decisions are yours, Mat. Both are `open` in §Decision Log, and the tasks are written for the recommendation.**
>
> 1. **D-1543, trust.** An update is trusted because its SHA-512 matches the feed file fetched over HTTPS from your repository's releases. There is no publisher signature. Whoever can edit the release assets can change both the installer and the feed file, and an installed app will then install what they put there. I recommend shipping it this way and saying so in the release notes, the README and the Settings card. Do nothing: hold the updater until the installer is signed.
> 2. **D-1544, the new request to GitHub.** The app starts to contact `github.com` by itself. The statement "everything except YouTube / Hugging Face calls … works offline" (07 `:9`), the README (`:57`) and the release notes must name it. I recommend naming it, with **Never** as the user's switch. Do nothing: hold the updater back, so that no release carries it until you rule and the statements stay true (leaving the statements unchanged while the updater ships would make them untrue).
>
> **Things I decided under your 2026-11-18 hand-over that you may want to look at:**
>
> - **Never** is a third interval (D-1541). You named two. I added the off choice because the request to GitHub is new and a user must be able to stop it.
> - **"Automatically" means: check and download by itself, install on one click** (D-1542). The download is about 450 MB and starts without a question. The app never restarts by itself; **Restart and update** in Settings is the user's choice, and a sentence beside it says that running jobs stop (D-1549).
> - **Check now** is a button in Settings (D-1548). You asked only for the schedule. Do nothing there means no button.
> - **The first release with the updater is yours.** This plan changes no version and uploads nothing. A user on rc.5 or older has no updater, so that user installs the first updater release by hand, once. From the release after that, updates arrive in the app.
> - **The mini-air host gets a new stage that installs and removes av-kit** in the E2E account (D-1552). Today the run book says the tool installs nothing. The stage refuses to start if that account already has an av-kit install, app data, a Start at sign-in entry, an av-kit shortcut or a record left by an earlier run that could not clean up. It removes what it made; a run that cannot put the account back as it found it leaves its record, and every later install run on the host refuses until you have looked (S10).
> - **The installer stops only the av-kit processes inside the folder it replaces** (D-1554). Today's installer stops any process whose path merely begins with that folder's name, and, when PowerShell is unavailable, every `av-kit.exe` of your account by name. With this plan, when the check cannot run or a process will not stop, the installer says the app cannot be closed and changes nothing: the old version stays, and at its next start the app offers **Restart and update** again.
> - **An update keeps Start at sign-in** (D-1553). Today the uninstall step that an update runs removes it. A user who moves from rc.5 by hand still loses it once, because rc.5's own uninstaller runs during that install; the release notes say so.
> - **Smart App Control on the host may refuse the unsigned installer.** I could not measure it: the host did not answer on 2026-11-26. Host run 1 (row 7) measures it early with one install and one start. If the host refuses, the round-trip rows stop as blocked, MEU-174 is not complete, and the choice is yours (S9); the dev PC is not a fallback, because a relaunch after an update starts on your real app data.
>
> **What changes for a user once a release carries this:** Settings gains an **Updates** section with the interval, the current version, the last check and its result, **Check now**, and, when a version is downloaded, **Restart and update**. A Windows notice appears once per downloaded version.

## Proposed Changes

### Single-statement contracts

- **`FEED_BLOCK`.** `ui/electron-builder.yml` gains one top-level block after `nsis:`: `publish:` with one entry `provider: github`, `owner: matbanik`, `repo: av-kit`, and no other key (no token, no `private`, no `releaseType`, no `channel`), under a two-line comment "UPDATE_FEED (MEU-173, D-1540): the public repository's releases are the update feed. Every build runs with --publish never; nothing here uploads."
- **`DIST_NEVER_PUBLISHES`.** In `ui/package.json` the `dist` script ends `electron-builder --win nsis --x64 --publish never`. No script in `ui/package.json` and no workflow step runs `electron-builder` without `--publish never`.
- **`FEED_CHECK`.** `tools/check_update_feed.py --dist <dir> --version <v> [--provider github|generic] [--feed-url <url>] [--out <json>]`, and `--selftest`. It reads `<dir>/latest.yml`, the one `av-kit-Setup-<v>.exe` in `<dir>`, its `.blockmap` and `<dir>/win-unpacked/resources/app-update.yml`, and compares: the feed's `version` with `<v>`; `path` and `files[0].url` with the installer's file name (no space, no path part); `sha512` and `files[0].sha512` with the base64 SHA-512 of the installer's bytes; `files[0].size` with the byte length; the blockmap present and not empty; `app-update.yml` naming provider `github`, owner `matbanik`, repo `av-kit` (or, with `--provider generic`, the given `--feed-url`). Its last stdout line is `check-update-feed: <reason> exit=<n>`: `feed-ok` 0, `feed-missing` 10, `installer-missing` 11, `installer-ambiguous` 12, `version-mismatch` 13, `name-mismatch` 14, `sha512-mismatch` 15, `size-mismatch` 16, `blockmap-missing` 17, `app-config-mismatch` 18, usage 2. It reads files only: no network, no upload, no write outside `--out`.
- **`FEED_CHECKLIST`.** `docs/releases/publish-checklist-update-feed.md` (new, LF) is the standing addition to each release's publish steps from the first feed release on. It states: the build writes `latest.yml` and `av-kit-Setup-<v>.exe.blockmap` beside the installer; the `FEED_CHECK` command runs before the upload and must end `feed-ok`; the upload names the installer, `latest.yml` and the blockmap, and is Mat's step; a release flagged pre-release on GitHub is never offered, and the release marked Latest is the one every installed app moves to; the earlier release's blockmap stays uploaded; a read-only probe after publishing (`curl -sL https://github.com/matbanik/av-kit/releases/latest/download/latest.yml`, Mat's step); the sentences the release notes must carry (D-1543, D-1544) and the one-time manual install for a user on rc.5 or older, after which such a user turns Start at sign-in on again if they used it (rc.5's own uninstaller removes that entry during the install). It supersedes line 91 of the rc.2 checklist for later releases; the rc.1 and rc.2 checklists are history and do not change.
- **`UPDATE_INTERVAL_LEAF`.** `UPDATE_INTERVAL_WIRES: frozenset[str] = frozenset({"weekly", "monthly", "never"})` in `domain/wire.py`; `("app", "update_interval"): SettingSpec("string", "weekly", UPDATE_INTERVAL_WIRES)` in the core registry; `update_interval: str | None = None` in `SettingsPutIn`; `UPDATE_INTERVALS = ['weekly', 'monthly', 'never'] as const` and `update_interval: z.enum(UPDATE_INTERVALS).nullable().optional()` in `appPutSchema`; in the MCP tool `update_interval: { type: "string", default: "weekly", enum: UPDATE_INTERVALS }` under `app` and `update_interval: z.enum(UPDATE_INTERVALS).optional()` in `settingsLeaves`. No new namespace, route, MCP tool or MCP action.
- **`UPDATE_SCHEDULE`.** `ui/src/main/update-schedule.ts` exports the pure `isCheckDue(input: { now: number; interval: 'weekly' | 'monthly' | 'never'; lastCheckAt: number | null; lastAttemptAt: number | null; pendingVersion: string | null; recoveryDone: boolean }): boolean`. It returns false when `interval` is `never`. Otherwise it returns true when `pendingVersion` is not null and `recoveryDone` is false (the recovery check of a found version, once per app start, whatever the 24 h rule says); and else when (`lastCheckAt` is null, or `lastCheckAt > now`, or `now - lastCheckAt >= period`, or `pendingVersion` is not null) and (`lastAttemptAt` is null, or `lastAttemptAt > now`, or `now - lastAttemptAt >= 24 h`). `period` is 7 × 24 h for `weekly` and 30 × 24 h for `monthly`. A check that ends without an error sets `lastCheckAt` and `lastAttemptAt` to `now`; a check that fails sets only `lastAttemptAt`. The controller holds `recoveryDone` in memory only: false at creation, true once the first `checkForUpdates()` call of this app start has been made, whatever its result. So a found version that waits after a restart is checked at the first tick even when the last attempt was an hour ago; the library then reports `update-downloaded` again (from its cache or a new download) and **Restart and update** comes back.
- **`UPDATER_CONFIG`.** `ui/src/main/app-updater.ts` exports `createAppUpdater(deps)`. `deps` carries the updater object, `isPackaged`, the clock, the timer functions, the state store, `readInterval(): Promise<string>`, `notify`, `log`, `shutdownBackend(): Promise<void>`, `setQuitIntent` and `emitState`. The module's only import of the library is `import electronUpdater from 'electron-updater'` in the wiring (`index.ts`), which passes `electronUpdater.autoUpdater` in. On creation the controller sets `allowPrerelease = false`, `allowDowngrade = false`, `autoDownload = true`, `autoInstallOnAppQuit = false`, and never calls `setFeedURL`. `forceDevUpdateConfig` is set only by `UPDATE_E2E_SEAM`.
- **`UPDATE_TICK`.** When `isPackaged` is true (or the E2E seam is on), the controller runs its first tick 60 s after the backend is ready and then one tick every 60 minutes. A tick reads the interval with `readInterval()` (`GET <apiBase>/settings/app`, the `update_interval` leaf). A read that rejects, or that answers a value outside `UPDATE_INTERVAL_WIRES`, skips that tick's scheduled check: no call, no state change, no store write, and one log line `update: interval unavailable`; the next tick reads again. The controller never assumes an interval, so a user who chose `never` is never checked because the backend did not answer (D-1550). With a wire in hand, the tick calls `checkForUpdates()` once when `isCheckDue` is true and no check or download is running. When `isPackaged` is false and the seam is off, the controller starts no timer and `check()` returns the state `disabled`.
- **`UPDATE_STATE`.** The controller owns one state object: `{ state: 'disabled' | 'idle' | 'checking' | 'downloading' | 'ready' | 'error', currentVersion: string, availableVersion: string | null, percent: number | null, lastCheckAt: number | null, lastResult: 'up-to-date' | 'update-found' | 'error' | null, errorKind: 'network' | 'checksum' | 'other' | null }`. The library's events map to it: `checking-for-update` → `checking`; `update-available` → `downloading` with the version; `download-progress` → `percent`; `update-not-available` → `idle`, `up-to-date`; `update-downloaded` → `ready`; `error` or a rejected `checkForUpdates()` → `error` with `errorKind` (`checksum` when the message holds `ERR_CHECKSUM_MISMATCH` or `sha512 checksum mismatch`; `network` for a `net::` or `ENOTFOUND`, `ETIMEDOUT`, `ECONNREFUSED` message or an HTTP status; else `other`). Every change calls `emitState`. The store file is `update-state.json` in the app-data folder (`new Store({ cwd: appData, name: 'update-state' })`), with `lastCheckAt`, `lastAttemptAt`, `lastResult`, `pendingVersion` and `notifiedVersion`, and nothing else. The store is opened with `clearInvalidConfig: true`, and the controller wraps the store's constructor and each read: a store that cannot be opened or parsed is read as empty, and a key that holds the wrong type is read as null; the controller then works from that state and still ticks.
- **`UPDATE_QUIET_FAILURE`.** A failed check or download writes one log line `update: check failed kind=<errorKind>` (no URL query, no path under the user's profile), sets the state, and shows no dialog, no notice and no window. No rejection leaves the controller.
- **`UPDATE_NOTICE_ONCE`.** On `ready`, when `notifiedVersion` differs from the downloaded version, the controller calls `notify({ title: 'av-kit update ready', body: 'Version <v> is downloaded. Open Settings, Updates, and choose Restart and update.' })` once and stores `notifiedVersion`.
- **`UPDATE_INSTALL_ORDER`.** `install()` is the only caller of `quitAndInstall`. When the state is not `ready` it returns `{ ok: false, reason: 'not-ready' }` and does nothing. When it is `ready` it runs, in this order and once: `log('update: install requested version=<v>')`, `setQuitIntent()`, `await shutdownBackend()` (the same `shutdownOwned('quit', …)` call the `before-quit` handler makes, after which the owned pid is cleared so the handler's second call signals nothing), `log('update: backend stopped')`, `updater.quitAndInstall(true, true)`. No timer, no event and no quit path calls `install()`: only the `update-install` IPC channel does.
- **`UPDATE_IPC`.** Three renderer-to-main channels with the no-payload schema: `update-get-state` → the state object; `update-check` → runs one check now, whatever the interval says (D-1548), and returns the state; `update-install` → `install()`. One main-to-renderer push, `update-state-changed`, carries the state object. Preload keys: `updateGetState`, `updateCheck`, `updateInstall`, `onUpdateState` (returns an unsubscribe function, as `onInboxChanged` does).
- **`UPDATES_CARD`.** Settings gains the section `{ key: 'updates', testId: 'updates-settings', label: 'Updates', group: 'App', mode: 'autosave' }` after `startup`, rendered by `ui/src/renderer/src/features/settings/UpdatesCard.tsx`. It holds: the select `settings-leaf-update_interval` ("Once a week", "Once a month", "Never"), saved with `schedulePut('app', { update_interval })` like `log_level`; the line `settings-update-version` ("Installed version <v>"); the status line `settings-update-status` (one of: "Not checked yet", "Up to date. Last checked <date>", "Checking…", "Downloading version <v>: <n> %", "Version <v> is ready to install", "Could not check for updates (<kind>). Last checked <date>", "Updates run in the installed app"); the button `settings-update-check` ("Check now"), disabled in `checking`, `downloading` and `disabled`; and, only in `ready`, the button `settings-update-restart` ("Restart and update") with the two fixed sentences `settings-update-restart-note` ("av-kit closes, installs version <v> and starts again. Downloads, transcripts, speech and conversions that are running stop.") and `settings-update-trust-note` ("Updates come from github.com/matbanik/av-kit and are checked against the release's SHA-512. The installer is not signed."). The trust sentence shows in every state. Existing select and button components and theme tokens only; no new colour, motion or variant.
- **`UPDATE_E2E_SEAM`.** Only when `process.env.AVKIT_E2E === '1'` and `process.env.AVKIT_E2E_UPDATE_FEED` names a file: the wiring sets `updater.updateConfigPath` to that file and `forceDevUpdateConfig = true`, uses 500 ms for the first tick and `AVKIT_E2E_UPDATE_TICK_MS` (default 1000) for the tick, and passes a recording function in place of `quitAndInstall`, reachable at `globalThis.__AVKIT_E2E_UPDATE__ = { installCalls: [] as Array<[boolean, boolean]>, state: () => … }`. Without `AVKIT_E2E=1` neither variable is read and nothing is exposed, packaged or not.
- **`UNINSTALL_CACHE_RECURSIVE`.** In `ui/build/installer.nsh` the one line `RMDir "$LOCALAPPDATA\av-kit-ui-updater"` becomes `RMDir /r "$LOCALAPPDATA\av-kit-ui-updater"`, still inside `${ifNot} ${isUpdated}`. The two `DeleteRegValue HKCU` lines move inside the same block, their text unchanged, so an update keeps the user's Start at sign-in entry and a real uninstall still removes it (today they run before the guard, and the old uninstaller that an update runs with `--updated` deletes the entry). Nothing else in `customUnInstall` changes, and the file still holds exactly two `DeleteRegValue` lines.
- **`APP_RUNNING_CHECK`.** `ui/build/installer.nsh` defines `!macro customCheckAppRunning`, which replaces the stock running-app check in the installer and in the uninstaller (D-1554). It reads its own pid with `System::Call 'kernel32::GetCurrentProcessId() i .r9'` and runs one fixed command through `nsExec::ExecToLog`: `"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "…"`, with the mode `find` and then, when that finds a process, the mode `stop` (PowerShell variables are written `$$` in the NSIS source). The command computes `$d = [IO.Path]::GetFullPath('$INSTDIR').TrimEnd('\') + '\'` and selects the `Win32_Process` rows whose `ExecutablePath` is not empty, starts with `$d` under `OrdinalIgnoreCase`, and whose `ProcessId` is not the installer's pid. `find` exits 0 when it selects none and 1 when it selects one or more. `stop` stops the selected processes by id, selects again for up to 10 s, and exits 0 when none is left and 3 when one is. Any exception exits 2. The macro: `find` 0 continues; `find` 1, when not `${isUpdated}`, asks the stock question `$(appRunning)` (`MB_OKCANCEL`, `/SD IDOK`; Cancel quits) and then runs `stop`, and on an update runs `stop` at once; `stop` 0 continues; any other exit code of either mode, a missing or blocked PowerShell included, shows `MessageBox MB_OK|MB_ICONEXCLAMATION "$(appCannotBeClosed)" /SD IDOK`, then `SetErrorLevel 2` and `Quit`, before any file changes. The macro holds no `taskkill`, `tasklist`, `/IM`, `IMAGENAME` or `nsProcess` call. A refused update leaves the old version installed; the user starts it again, and the recovery check of `UPDATE_SCHEDULE` offers **Restart and update** again.
- **`HOST_PAYLOAD`.** `tools/e2e_remote.py run <commit> --payload <dir>` (optional). `<dir>` is flat, holds a `payload.json` and at most five other files, at most 1.2 GB together. The tool writes each file's name, size and SHA-256 into `request.json` under `payload`, uploads the files to `<root>\runs\<run-id>\payload\`, and `host-prepare.ps1 -Stage verify` refuses a mismatch with the reason `payload-mismatch`, exit 26 (the run book's mismatch family, beside `upload-mismatch`). `run-e2e.ps1` then runs a third stage, `install`, after the main stage: the specs of `ui/tests/e2e-install/` with `ui/playwright.install.config.ts`, with `AVKIT_E2E_PAYLOAD_DIR` set for that stage's process only, results under `results\<run-id>\install\`. Without `--payload` the request has no `payload`, the variable is removed and no install stage runs. The summary gains an `install` block (counts, or `not-run`), and a payload run exits 0 only when the main stage passes by today's rule and every install-stage test passed, none skipped. A main stage that passes with an install stage that does not ends `install-failures`, exit 41 (new); when the main stage has new failures its own reason is reported and the `install` block still tells the install stage's result. `host-facts.ps1` adds the Smart App Control state (`Get-MpComputerStatus`, field `SmartAppControlState`) to the facts.
- **`INSTALL_STAGE_RULES`.** A spec of the install stage: refuses (fails with a named reason, before any install) when the E2E account already has an av-kit uninstall entry, `%LOCALAPPDATA%\Programs\av-kit`, `%LOCALAPPDATA%\av-kit`, `%APPDATA%\av-kit-ui` or `%LOCALAPPDATA%\av-kit-ui-updater`, or when the feed port is taken, or when any of these exists: the HKCU `Run` value `com.avkit.app`, the HKCU `Explorer\StartupApproved\Run` value `com.avkit.app`, the shortcuts `av-kit.lnk` on the Desktop and in the Start Menu's Programs folder, the installer's key `HKCU\Software\<APP_GUID>`, or an owner record `<root>\install-owner.json` left by an earlier run (reason `install-quarantined`). `APP_GUID` is the UUID v5 of `com.avkit.app` in electron-builder's namespace `50e065bc-3134-11e6-9bab-38c9862bdaf3` (`NsisTarget.js:49`, `:261`; `multiUser.nsh:8`; no `nsis.guid` in the builder config), `c21620fd-8854-5989-9a80-a73c80a17704` by a local computation; the canary proves it by finding that key after its install. Before its first change to the account the stage writes `<root>\install-owner.json` (run id, install folder, the before snapshot, the decoy's pid). It starts a sibling decoy, a copy of `%SystemRoot%\System32\PING.EXE` named `av-kit.exe` in `<root>\runs\<run-id>\install-sibling\`, run with `-t 127.0.0.1`, and requires it alive after every installer and uninstaller call (the host proof of `APP_RUNNING_CHECK`: the stock check would match that folder by its prefix and by the image name). It installs with `<installer> /S /D=<root>\runs\<run-id>\install`; starts the installed `av-kit.exe` with no `AVKIT_E2E` and no `AVKIT_APP_DATA`; stops only processes whose image path is under that install folder; and at the end, in a `finally` block that also runs after a failed step, stops the decoy by its pid, uninstalls with `/S`, removes the three data folders it recorded as created by this run, and requires its before and after snapshots (uninstall entries, the installer's key, both sign-in values, the two shortcuts, the five folder names) to be equal; only then does it delete `install-owner.json`. A run that ends without that equality, a host reboot during the run included, keeps the owner record, so every later payload run refuses `install-quarantined` until Mat has followed the run book's recovery (read the record, compare the account with its snapshot, remove what the run made, delete the record) (S10). The tool's `release` frees the host lock and is never a restoration of the account. A start that the host refuses is reported as `installer-refused-by-host` or `app-refused-by-host` with the Code Integrity event id when one is logged.
- **`ROUND_TRIP`.** `payload.json` names `mode: "roundtrip"`, the old and new installers, their versions (`0.0.901`, `0.0.902`), the feed files and the feed port. Both installers are real builds of the session's snapshot commit whose only differences from the product config are the version and a `publish` block of `provider: generic`, `url: http://127.0.0.1:<port>/`. The spec: (1) installs the old build and starts it; (2) starts an MCP server as a client does (`av-kit.exe` with `ELECTRON_RUN_AS_NODE=1` and the packaged server entry) and records the pids of the app, its backend and the MCP server; (3) sets `app.update_interval` to `monthly` in the Updates card, turns on Start at sign-in in the Startup card and requires the HKCU `Run` value `com.avkit.app` to exist, and writes a marker file in the app-data folder; (4) serves a feed whose `latest.yml` carries a wrong SHA-512 and waits for the status "Could not check for updates (checksum)", then checks that the installed exe is still the old version and `settings-update-restart` is absent; (5) serves the true feed, clicks `settings-update-check`, waits for "Version 0.0.902 is ready to install", and clicks `settings-update-restart`; (6) polls the installed exe's version and the three pids, and requires that at the first poll that reads `0.0.902` none of the three pids is alive; (7) requires a running `av-kit.exe` under the install folder, the installed exe's file version `0.0.902` (the version proof: the health route carries no version), a backend pid read from the descriptor in the app-data folder that differs from step (2)'s and whose health route answers ok, the `Run` value `com.avkit.app` still present, the sibling decoy still alive, `app.update_interval` still `monthly`, the marker file's SHA-256 unchanged, and the main log holding `update: backend stopped` before the installer started; (8) uninstalls with `/S` and, as soon as the uninstaller returns and before the stage removes anything itself, requires `%LOCALAPPDATA%\av-kit-ui-updater` and both sign-in values to be gone (the uninstaller's own work, `UNINSTALL_CACHE_RECURSIVE`), then ends per `INSTALL_STAGE_RULES`. `mode: "canary"` is steps (1) and (8) with one installer and a wait for the app's main window.
- **`PIN_GROWTH`.** An existing test that lists IPC channels, preload keys, settings sections, `app` leaves, MCP schema leaves or the OpenAPI document may change only by gaining the new entries of this plan. The files are named in §Test pins. Any other change to an existing assertion is S5.

### MEU-173: Update feed

1. `ui/electron-builder.yml` gains `FEED_BLOCK`; `ui/package.json` follows `DIST_NEVER_PUBLISHES`.
2. `tools/check_update_feed.py` per `FEED_CHECK`, with its selftest.
3. `docs/releases/publish-checklist-update-feed.md` per `FEED_CHECKLIST`.
4. A real build with the product config proves that the three files appear and that the check passes on them and fails on a changed copy (row 3).

### MEU-174: In-app update

1. The `app.update_interval` leaf in the core registry, the API model and the OpenAPI document, the UI schema and the MCP tool (`UPDATE_INTERVAL_LEAF`).
2. `electron-updater` 6.8.11 as an exact `dependencies` entry of `ui/package.json`, with the lock file.
3. `update-schedule.ts` and `app-updater.ts`; the wiring in `index.ts`; the three channels in `ipc.ts`; the four preload keys.
4. The Updates section in Settings (`UPDATES_CARD`).
5. `UNINSTALL_CACHE_RECURSIVE` in the installer macro.
6. The install stage of the remote E2E tool (`HOST_PAYLOAD`), the canary and the round trip.
7. Canon and the public statements (row 18).

### Test pins

Existing tests that may change, and only per `PIN_GROWTH` (row 0's scan records which of them enumerate; a file that does not enumerate stays byte-identical):

- IPC and preload: `ui/tests/unit/ipc-strict-census.test.ts` (`:58` `toHaveLength(22)` becomes 25; its two maps gain three entries each), `ui/tests/unit/ipc-channels.ts`, `shell-ipc-ledger.test.ts`, `gui-actions-audit.test.ts`, `app-shell-wiring.test.ts`, `login-item-ipc.test.ts`, `mcp-prompt-ipc.test.ts`, `web-prefs-ipc.test.ts`, `capture-paste-main.test.ts`, `clipboard-image-main.test.ts`, `settings-page.test.ts`.
- Settings sections and leaves: `settings-rail.test.tsx`, `settings-page.test.ts`, `settings-runtime.test.ts`, `ui/tests/e2e/settings.test.ts` (W4-2), `ui/tests/e2e/test-ids.ts`.
- The installer macro (M-7, cleared by row 13, which names each line and its new assertion; D-1553): in `ui/tests/unit/login-item-nsh.test.ts`, `:105` (the unguarded fixture line) becomes `RMDir /r`; `:112` (the pattern `^RMDir\s+"\$LOCALAPPDATA\\[^"]+"$`) requires the `/r`; `:119` (AC-114.2) expects the one line with `RMDir /r ` in place of `RMDir `; the title at `:122` (AC-114.3) and `:125` change from "no RMDir is recursive" to "the one recursive RMDir is the updater-cache line inside the not-updated guard". `:124` (exactly two `DeleteRegValue` lines) and AC-61.18 at `:26-70` stay as they are, because the two lines move but keep their text and count.
- Python: `tests/unit/test_services.py` and `tests/e2e/test_api_health_settings.py` (only if they list the `app` leaves), `tests/unit/test_e2e_remote.py` (new tests added; existing ones unchanged), `tests/unit/test_ci_workflows.py` (unchanged, must pass).
- MCP: `mcp-server/tests/m7-resource.test.ts`, `mcp-server/tests/settings-runtime.test.ts`, and the audit baseline `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` if it holds the leaf list.
- The E2E harness census (`ui/tests/e2e/electron-harness.test.ts`) allows only `electron-app.ts` to name Playwright's launcher. The install stage lives in `ui/tests/e2e-install/` with its own helper. If the census reads that folder too, the helper is added to its allow list (one entry).

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `PUT /settings/app` body, `update_interval` | `SettingsPutIn` (API) and the core registry's wire set | string, one of `weekly`, `monthly`, `never`; exact case | Extra fields refused (422), as today |
| `GET /settings/app` | Core registry | `update_interval` always present; default `weekly` | — |
| `avkit_settings.set`, `update_interval` | `settingsLeaves` (MCP Zod) | enum of the three wires | `.strict()`, as today |
| `appPutSchema` (renderer) | `settings-schemas.ts` | enum of the three wires, nullable, optional | `.strict()`, as today |
| IPC `update-get-state`, `update-check`, `update-install` | `ipc.ts` per-channel schema | no payload | The no-payload schema refuses any payload |
| Push `update-state-changed` | `app-updater.ts` state object | the `UPDATE_STATE` shape | Main builds it; the renderer treats an unknown `state` as `idle` |
| `update-state.json` (main store) | `app-updater.ts` | numbers or null for the two times; version strings or null | An unreadable or wrong-typed value is treated as null |
| `latest.yml` from the feed | electron-updater | `version`, `files[].url`, `sha512`, `size` | The library refuses a missing field; a SHA-512 mismatch ends the download |
| `tools/check_update_feed.py` arguments | argparse | `--dist` an existing folder; `--version` a version string; `--provider` one of two | Unknown arguments exit 2 |
| `payload.json` and `request.json` `payload` | `tools/e2e_remote.py` | file names with no path part; size and SHA-256 per file; at most six files, 1.2 GB | A name with a path part, a missing file or a seventh file is refused before any upload |
| Env `AVKIT_E2E_UPDATE_FEED`, `AVKIT_E2E_UPDATE_TICK_MS` | `index.ts` wiring | read only when `AVKIT_E2E === '1'`; the tick an integer from 100 to 60000 | Ignored otherwise |

### Acceptance Criteria

**MEU-173**

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-173.1 | unit | `ui/electron-builder.yml` carries `FEED_BLOCK`: one `publish` entry, provider `github`, owner `matbanik`, repo `av-kit`, no other key. | Local Canon: 07 §Update feed, Feed address row; Research-backed: R2 | The same check on a copy with another provider, a second entry or a `token` key fails. |
| AC-173.2 | unit | `DIST_NEVER_PUBLISHES`: every `electron-builder` call in `ui/package.json` scripts and in `.github/workflows/*.yml` carries `--publish never`, and no workflow step that runs it is given `GH_TOKEN` or `GITHUB_TOKEN`. `tests/unit/test_ci_workflows.py` passes unchanged. | Local Canon: 07 §Update feed, Feed address and Manual upload rows; PROJECT-PROFILE E5 | The helper refuses a script text without the flag and one with `--publish always`. |
| AC-173.3 | integration | A build with the product config and `--publish never` writes `latest.yml` and `av-kit-Setup-<v>.exe.blockmap` beside the installer, and `win-unpacked/resources/app-update.yml` names the GitHub feed. | Local Canon: 07 §Update feed, Feed files row; Research-backed: R2, R3 | `FEED_CHECK` on that folder with `latest.yml` moved away ends `feed-missing`, exit 10. |
| AC-173.4 | unit and integration | `FEED_CHECK` ends `feed-ok` on a correct folder and gives each mismatch its own reason and exit code. On the real build of AC-173.3 it ends `feed-ok`, and on a copy whose installer has one changed byte it ends `sha512-mismatch`. | Local Canon: 07 §Update feed, Check row | One fixture per reason from 10 to 18; the selftest runs each; a name with a space ends `name-mismatch`. |
| AC-173.5 | unit | `FEED_CHECKLIST` exists and holds the three asset names, the `FEED_CHECK` command before the upload, the statement that the upload is Mat's step, the Latest and pre-release rule, and the one-time manual install. The tool and the checklist contain no upload, release or push command for an agent to run: `gh release` appears only in the checklist's lines marked as Mat's. | Local Canon: 07 §Update feed, Manual upload and Which releases rows; D-1540 | The test fails on a copy of the checklist whose upload line lacks `latest.yml` or the blockmap; `gh ` in `tools/check_update_feed.py` fails it. |

**MEU-174**

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-174.1 | unit | `isCheckDue` follows `UPDATE_SCHEDULE` for `weekly` and `monthly`: not due one millisecond before the period ends, due at the period, due when `lastCheckAt` is null or in the future. | Human-approved: triage D-1409 (the scheduled check, once a week or once a month) | `never` is not due for any input (D-1541). A failed attempt 23 h ago makes it not due; 24 h ago, due. With `pendingVersion` set, `recoveryDone` false and an attempt 1 h ago it is due; the same input with `recoveryDone` true is not due. |
| AC-174.2 | unit | With a fake clock and the updater mocked, a packaged controller ticks per `UPDATE_TICK` and calls `checkForUpdates()` once when due, and never twice while a check or a download is running. The interval is read at each tick, so a change in Settings applies with no restart. | Human-approved: D-1409; Local Canon: D-1550 | With `isPackaged` false and the seam off, 60 simulated days produce 0 calls and 0 timers (a development run never checks; Local Canon, 07 §In-app update, Check row). A `readInterval` that rejects, and one that answers `daily`, with null timestamps give 0 calls over 60 simulated days and one `update: interval unavailable` line per tick; a saved `never` gives 0 calls. A store holding `pendingVersion` and `notifiedVersion` `v` with `lastAttemptAt` 1 h ago gives one call at the first tick; the `update-downloaded` for `v` that follows sends 0 notices, and the later ticks of that start give 0 calls. |
| AC-174.3 | unit | `UPDATER_CONFIG`: after creation the mock holds `allowPrerelease` false, `allowDowngrade` false, `autoDownload` true, `autoInstallOnAppQuit` false; `setFeedURL` has 0 calls; `forceDevUpdateConfig` is unset. | Research-backed: R3 (the default follows `rc` tags only), R4; Local Canon: D-1540, D-1542 | A table test fails when any of the four values flips. With `AVKIT_E2E` unset and `AVKIT_E2E_UPDATE_FEED` set, the seam stays off. |
| AC-174.4 | unit | The events map to `UPDATE_STATE`, each change emits the state, and the store holds only the five named keys. A found version sets `pendingVersion`; a check that finds none clears it. | Local Canon: D-1547, D-1550 | A store with a string where a time belongs is read as null and the controller still ticks. A store file that is not JSON, and a store constructor that throws, are read as empty and the controller still ticks. |
| AC-174.5 | unit | `UPDATE_QUIET_FAILURE`: a rejected `checkForUpdates()` and an `error` event each give the state `error` with the right `errorKind`, one log line, `lastAttemptAt` set and `lastCheckAt` unchanged. | Local Canon: 07 §In-app update, Outbound row ("With no network the check fails quietly and the app works as before") | `notify`, the dialog mock and the window mock have 0 calls; no unhandled rejection is recorded; the log line holds no URL query and no user path. |
| AC-174.6 | unit | `UPDATE_NOTICE_ONCE`: one notice per downloaded version; a second `update-downloaded` for the same version sends none. `quitAndInstall` has 0 calls after `update-downloaded`. | Human-approved: D-1409 (downloads and installs without the release page); Local Canon: D-1542 | Any number of ticks in the state `ready` produce 0 `quitAndInstall` calls: the app never restarts unless the user chooses it (07 §In-app update, Install row). |
| AC-174.7 | unit | `UPDATE_INSTALL_ORDER`: in `ready`, `install()` records the sequence `setQuitIntent`, `shutdownBackend` resolved, `quitAndInstall(true, true)`, exactly once. | Local Canon: 07 §In-app update, Processes row; D-1542; Research-backed: R3 | In every other state `install()` returns `not-ready` and all three have 0 calls. With `shutdownBackend` pending, `quitAndInstall` has 0 calls. A second `install()` call adds none. |
| AC-174.8 | unit | The three channels and the push of `UPDATE_IPC` are registered with the no-payload schema, the preload exposes the four keys, and `update-check` runs a check whatever the interval says, also with `never`. | Local Canon: D-1548 (the check on request; an agent decision, not D-1409) | Each channel refuses a payload. `update-check` in the state `disabled` calls `checkForUpdates()` 0 times. |
| AC-174.9 | unit | Core and API: `GET /settings/app` returns `update_interval` `weekly` on a new database; `PUT` accepts `weekly`, `monthly` and `never` and the next `GET` returns the value. | Local Canon: 07 §In-app update, Setting surface and Interval rows; Human-approved: D-1409 for the two intervals; Local Canon: D-1541 for the default and `never` | `PUT` with `daily`, `Weekly`, `7` or an unknown leaf `update_intervals` answers 422 and changes nothing. |
| AC-174.10 | unit | `openapi.committed.json` holds `update_interval` in the settings request model, and the drift check passes. | Local Canon: 07 §In-app update, Setting surface row; G8 | The drift check fails before the regeneration (recorded in row 9). |
| AC-174.11 | unit | MCP: the schema resource lists `app.update_interval` with its default and enum; `avkit_settings.set` accepts the three wires. The tool list and each tool's action list are unchanged. | Local Canon: 07 §In-app update, Setting surface row; D-1546 | `avkit_settings.set` with `daily` is refused by the tool's schema before any HTTP call. |
| AC-174.12 | unit | `appPutSchema` accepts the three wires and stays strict; `UPDATES_CARD` renders the select with three options, the version line, the status line for each state, and `settings-update-check`; a change of the select calls `schedulePut('app', { update_interval })`. | Local Canon: 07 §In-app update, Setting surface row; D-1547; D-1548 for `settings-update-check` | `daily` is refused by the schema. `settings-update-restart` is absent in every state but `ready`. `settings-update-check` is disabled in `checking`, `downloading` and `disabled`. |
| AC-174.13 | unit | In `ready`, `settings-update-restart` and `settings-update-restart-note` show, and a click calls `updateInstall` once. `settings-update-trust-note` shows in every state. | Local Canon: D-1549; D-1543 (open, Mat's: the sentence is the recommended option) | A click while the call is pending sends no second call. |
| AC-174.14 | unit | `UNINSTALL_CACHE_RECURSIVE`: the macro's not-updated block holds `RMDir /r "$LOCALAPPDATA\av-kit-ui-updater"` once and no other `RMDir`, and holds both `DeleteRegValue HKCU` lines; `customUnInstall` has no `DeleteRegValue` outside that block. | Local Canon: 07 §Uninstall removes the installer copy (residual); D-1553 | The line outside the `${ifNot} ${isUpdated}` block fails the test; a second recursive delete fails it; a fixture with the two `DeleteRegValue` lines before the guard, as today, fails it. |
| AC-174.15 | integration | Electron E2E on the mini-air host, against a local feed through `UPDATE_E2E_SEAM`: the Updates section shows, the select saves `monthly` and a reload shows it, and with a feed that offers `999.0.0` the status reaches "Version 999.0.0 is ready to install". | Local Canon: 07 §In-app update, Tests row; E2; grouping D-1411 | With a feed that offers the running version the status reads "Up to date" and `settings-update-restart` is absent. |
| AC-174.16 | integration | Same run: a click on `settings-update-check` starts a check (the status passes through "Checking…"), and a click on `settings-update-restart` records exactly one `[true, true]` in `__AVKIT_E2E_UPDATE__.installCalls`. | Local Canon: D-1548; D-1542; 07 §In-app update, Tests row | Before the click `installCalls` is empty although the state is `ready`. With a feed whose SHA-512 is wrong the status reads "Could not check for updates (checksum)" and `installCalls` stays empty. |
| AC-174.17 | unit | `HOST_PAYLOAD`: `run --payload` writes the payload entries into the request, refuses a bad payload folder before any upload, and the summary carries the `install` block; a run without `--payload` builds the same request as today. | Local Canon: 07 §In-app update, Tests row ("run by script on the remote E2E host"); D-1552 | A payload run whose install stage has a failed or skipped test does not exit 0. A name with a path part and a seventh file are refused. |
| AC-174.18 | integration | Host run 1 (canary): the installer built in row 3 installs silently in the E2E account, the installed app shows its main window, and the stage leaves the account as it found it (`INSTALL_STAGE_RULES`). | Local Canon: 07 §In-app update, Tests row; D-1552 | The stage refuses to start, with 0 installer calls and 0 changes, when one of the five folders, an uninstall entry, either sign-in value, either shortcut, the installer's key or an owner record exists, or the feed port is taken (unit-tested on the precondition function with a fake file system and a fake registry). On the host the sibling decoy is alive after the install and the uninstall. |
| AC-174.19 | integration | Host run 2 (`ROUND_TRIP`): an installed `0.0.901` finds, downloads and installs `0.0.902` from the local feed on the user's click; the old app, its backend and the MCP server are gone before the new exe is read; the new version runs; the setting, the marker file and the `Run` value are kept; the sibling decoy outside the install folder is still alive. | Local Canon: 07 §In-app update, Tests, Processes and Install rows; Human-approved: D-1409 | Step (4) of `ROUND_TRIP`: with a wrong SHA-512 in the feed the installed version stays `0.0.901` and no restart control shows. |
| AC-174.20 | integration | After the round trip's uninstall, `%LOCALAPPDATA%\av-kit-ui-updater` and both sign-in values are gone, checked as soon as the uninstaller returns and before the stage removes anything itself; then the before and after snapshots are equal and the owner record is deleted. | Local Canon: D-1553; 07 §Uninstall removes the installer copy (residual) | The canary run (old macro semantics do not apply: no cache exists) passes the same snapshot rule, so a difference in run 2 is the cache. |
| AC-174.21 | unit | `APP_RUNNING_CHECK`: `installer.nsh` defines `customCheckAppRunning` with the fixed PowerShell path, the two modes, the bounded folder match, and `appCannotBeClosed`, `SetErrorLevel 2` and `Quit` on every non-zero exit. The command, taken from the macro with the NSIS substitutions applied (`$$` to `$`, `$INSTDIR`, `$SYSDIR`, the own-pid variable) and run through `powershell.exe` against two decoys (copies of `PING.EXE` named `av-kit.exe` in `<tmp>\install\` and `<tmp>\install-sibling\`, each run with `-t 127.0.0.1`), stops the inside decoy and leaves the sibling running. | Research-backed: R7 (`allowOnlyOneInstallerInstance.nsh:66`, `:94`, `:97-99`); Local Canon: D-1554 | The macro text holds no `taskkill`, `tasklist`, `/IM`, `IMAGENAME` or `nsProcess`. With an install folder that `GetFullPath` refuses, the command exits 2. The stock `StartsWith('$INSTDIR'` filter, run on the same decoys, selects the sibling, so the test proves its own oracle. `afterEach` stops both decoys by pid. |

**Control binding**

| Control | Observable | Call chain | Negative oracle |
|---|---|---|---|
| The app never restarts by itself | `quitAndInstall` call count | timer → tick → `checkForUpdates` → events → state; `install()` is reached only from `handleIpc('update-install')` | AC-174.6: 0 calls after `update-downloaded` and any number of ticks; AC-174.16: `installCalls` empty before the click |
| Backend stops before the installer runs | The recorded call sequence; the main log order; pid polls | `install()` → `setQuitIntent` → `shutdownOwned('quit')` → `quitAndInstall` | AC-174.7: 0 `quitAndInstall` calls while `shutdownBackend` is pending; AC-174.19 step (6) |
| A development run never checks | `checkForUpdates` call count, timer count | `createAppUpdater` reads `deps.isPackaged` | AC-174.2: 0 calls, 0 timers |
| A wrong installer is not installed | The state and the installed version | library download → SHA-512 compare → `error` | AC-174.16 and AC-174.19 step (4) |
| A build never publishes | The command text | `ui/package.json` scripts, workflow steps | AC-173.2: the helper refuses a text without the flag |
| The interval is honoured | `checkForUpdates` call count over a simulated period | tick → `readInterval` → `isCheckDue` | AC-174.1 and AC-174.2: 0 calls inside the period; `never` 0 calls |
| An unreadable interval never checks | `checkForUpdates` call count | tick → `readInterval` rejects or answers a value outside the wires → skip | AC-174.2: 0 calls over 60 days with a rejecting or a `daily` read |
| A found update comes back after a restart | `checkForUpdates` call count at the first tick of a start | creation (`recoveryDone` false) → tick → `isCheckDue` | AC-174.1: with `recoveryDone` true it is not due inside 24 h; AC-174.2: one call at the first tick, 0 later |
| The installer stops only processes in its own folder | Decoy liveness | `CHECK_APP_RUNNING` → `customCheckAppRunning` → `find`, `stop` | AC-174.21: the sibling decoy survives; AC-174.18 and AC-174.19: the host's sibling decoy is alive after every installer and uninstaller call |
| An update keeps Start at sign-in | The HKCU `Run` value | old uninstaller with `--updated` → `customUnInstall` → `${ifNot} ${isUpdated}` | AC-174.14: the fixture with the lines before the guard fails; AC-174.19: the value survives the update |

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| The scheduled check, weekly or monthly | Human-approved | D-1409; the two periods fixed by D-1550 (7 and 30 days) |
| The default and the off choice | Local Canon (plan-time) | D-1541 |
| Which releases are offered | Local Canon (plan-time) + Research-backed | D-1540; R3 |
| When the download starts, when the install runs, what the user sees | Local Canon (plan-time) | D-1542, D-1547, D-1549 |
| A check on request | Local Canon (plan-time) | D-1548 (not D-1409) |
| Trust for an unsigned installer | Local Canon; Mat's | D-1543, `open`; tasks follow the recommendation |
| The outbound statement | Local Canon; Mat's | D-1544, `open`; tasks follow the recommendation |
| Feed files, their names, the builder block | Research-backed | R2, R3; proved by AC-173.3 on a real build |
| The installer's behaviour on an update | Research-backed | R7 (templates read locally); proved by AC-174.19 |
| Where the state lives and the retry rule | Local Canon (plan-time) | D-1550 |
| The MCP surface | Local Canon | 07 Setting surface row; D-1546 |
| The E2E seam | Local Canon (precedent `e2e-shell.ts`, `__AVKIT_E2E_TRAY__`) | D-1551 |
| How the real update runs on the host | Local Canon; grouping D-1411 | D-1552 |
| The updater cache at uninstall; Start at sign-in across an update | Local Canon: MEU-114, MEU-61 | D-1553 |
| Which processes the installer and the uninstaller stop | Research-backed (R7) + Local Canon | D-1554; proved by AC-174.21 and the host's sibling decoy |
| The library's answer to a recovery check while a downloaded version waits | Research-backed (R3), not run here | The controller relies only on `update-downloaded` arriving again, from the cache or a new download; AC-174.2 proves the controller with the mock. A new download costs bandwidth, not correctness |
| A download in a development run with `forceDevUpdateConfig` | Research-backed, not yet run here | Probed by the E2E Red and Green runs; S8 if the library refuses |
| Playwright starting the installed `av-kit.exe` | Not verified at plan time | Probed by host run 1; S8 names the fallback (`--remote-debugging-port` and a CDP connect, inside the install-stage helper only) |
| Mark-of-the-Web on the downloaded installer; NSIS message boxes in silent mode; Smart App Control on a user's PC | Not verified (from memory only) | Not relied on. The round trip shows what the host does with a local feed. The checklist tells Mat to watch the first real update |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/electron-builder.yml` | modify | `FEED_BLOCK` |
| `ui/package.json`, `ui/package-lock.json` | modify | `dist` script; `electron-updater` 6.8.11 exact |
| `tools/check_update_feed.py` | new | `FEED_CHECK` |
| `docs/releases/publish-checklist-update-feed.md` | new | `FEED_CHECKLIST` |
| `tests/unit/test_update_feed_config.py`, `tests/unit/test_check_update_feed.py` | new | AC-173.1, .2, .4, .5 |
| `packages/core/src/avkit_core/domain/wire.py`, `…/services/settings.py` | modify | The wire set and the registry entry |
| `packages/api/src/avkit_api/schemas/settings.py`, `openapi.committed.json` | modify | The leaf; the regenerated document |
| `tests/unit/test_update_interval_setting.py` | new | AC-174.9 |
| `mcp-server/src/toolsets/settings.ts`, `mcp-server/tests/update-interval-setting.test.ts` | modify, new | AC-174.11 |
| `ui/src/main/update-schedule.ts`, `ui/src/main/app-updater.ts` | new | `UPDATE_SCHEDULE`, the controller |
| `ui/src/main/index.ts`, `ipc.ts`, `preload.ts` | modify | Wiring, channels, keys, the seam |
| `ui/src/renderer/src/features/settings/UpdatesCard.tsx` | new | `UPDATES_CARD` |
| `…/settings/settings-sections.ts`, `settings-schemas.ts`, `SettingsPage.tsx`, and the renderer's `window.api` type file | modify | The section, the schema leaf, the mount, the four keys |
| `ui/build/installer.nsh` | modify | `APP_RUNNING_CHECK` (row 2b, before the first build in row 3), then `UNINSTALL_CACHE_RECURSIVE` (row 13: the cache line and the two sign-in lines inside the update guard) |
| `ui/tests/unit/update-schedule.test.ts`, `app-updater.test.ts`, `update-ipc.test.ts`, `updates-card.test.tsx`, `update-uninstall-nsh.test.ts`, `app-running-nsh.test.ts` | new | AC-174.1 to .8, .12 to .14, .21 |
| The §Test pins files | modify | `PIN_GROWTH`, and the `login-item-nsh.test.ts` lines that row 13 names |
| `ui/tests/e2e/app-update.test.ts` | new | AC-174.15, .16 |
| `tools/e2e_remote.py`, `tools/e2e_host/run-e2e.ps1`, `host-prepare.ps1`, `host-facts.ps1`, `tests/unit/test_e2e_remote.py`, `.agent/docs/e2e-remote-host.md` | modify | `HOST_PAYLOAD`; a run book section "The install stage" |
| `ui/tests/e2e-install/install-helper.ts`, `update-roundtrip.test.ts`, `ui/playwright.install.config.ts`, `ui/tests/unit/install-preconditions.test.ts` | new | `INSTALL_STAGE_RULES` (with the owner record and the sibling decoy), `ROUND_TRIP`, AC-174.18 to .20 |
| `docs/execution/plans/2026-11-14-capture-shapes-steps/openapi-delta.py` | modify | AC-106.5's delta: Session 106's `SettingsPutIn.update_interval` is set back before the compare (D-1582, as D-1600 did for the cookie shapes) |
| `ui/tests/unit/app-user-model-id.test.ts` | new | B-17's root cause (D-1583): `boot()` in `ui/src/main/index.ts` sets the Windows AppUserModelId to `LOGIN_ITEM_NAME` before it reads the login item or creates a window or tray |
| `docs/build-plan/07-distribution.md` | modify | §Goal `:9`, the Auto-update row `:195`, a Delivered note under each home (CRLF kept) |
| `docs/build-plan/06-gui.md` | modify | The `app.update_interval` row after `:1081` and the Updates section in the section list (CRLF kept) |
| `README.md` | modify | The offline sentence at `:57` and one paragraph on updates (D-1543, D-1544 as ruled) |
| `docs/BUILD_PLAN.md`, `build-priority-matrix.md`, `.agent/context/meu-registry.md`, `meu-status.yaml`, `known-issues.yaml`, `known-issues.md` | modify | Status and the issue, row 18 |
| Plan folder scripts written in row 0 and later rows | new | `baseline.ps1`, `red-check.py`, `row-check.py`, `identity.py`, `eol-check.py`, `crlf.py`, `snapshot-commit.py`, `canon-edit.py`, `issue-resolve.py`, `session-gate.ps1`, `pins-scan.py`, `run-check.py`, `licence-check.py`, `build-update.ps1` |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Code signing of the installer or the updates | product | none registered | 07 `:196` "ship unsigned and document SmartScreen"; a certificate is a cost decision of Mat's. D-1543 states what follows from it |
| A signed feed file | product | none | Only in electron-updater 27 alpha (R6); a pre-release library is not used |
| macOS and Linux updates | product | none | 07 §Platforms: Windows is the only gated platform; the NSIS target is the only updater target here |
| A stable-only or beta channel, a channel setting | product | none | D-1540 follows the release marked Latest; no second channel exists |
| A delta-only feed, tuning of differential downloads | product | none | The blockmap is uploaded (07 Feed files row) and the library falls back to a full download; how much a delta saves on this installer is not measured |
| Detecting running jobs before the restart | product | none registered | D-1549: no busy signal exists and `/tts` has no list route; a new route is outside this session's `owns` |
| An MCP action that checks or installs | product | none | D-1546; a new tool shape is a one-way door |
| A version change, a tag, a release, an upload, release notes for a real version | release | Mat's next release | PROJECT-PROFILE E5; M-1; M-12 |
| Help text for the Updates section in `settings-help-content.ts` | product | none | The file is in Session 103's list; if a pin requires one entry per section, row 0 records it and the entry is one line added after Session 103 has landed (S5 otherwise) |
| Cleaning the updater's cache after a successful update | product | none | The library reuses the cached installer for differential downloads; the uninstall removes the folder (D-1553) |
| Changing Smart App Control, the sign-in or the scheduled task on the host | host | Mat's | D-1216 |

## BUILD_PLAN.md Audit

- `docs/BUILD_PLAN.md:51` (the Phase 7 status line) names MEU-173 and MEU-174 as registered on 2026-11-26. Row 18 changes that line to name both as delivered by Session 106 and awaiting Mat's first feed release, and changes nothing else in the file.
- `docs/build-plan/build-priority-matrix.md:103-104` (7.10, 7.11), `.agent/context/meu-registry.md:145-146` and `.agent/context/meu-status.yaml` (`:4530`, `:4556`): row 18 sets both MEUs to `ready_for_review` through `tools/meu_status.py` and renders the registry; the execution review, not this plan, moves them further.
- `.agent/context/known-issues.yaml:6777` `APP-NO-IN-APP-UPDATE`: row 18 records the delivery with `issue-resolve.py` and a note that the fix reaches users with Mat's first feed release.
- 07 `:195` "Auto-update | `electron-updater` **optional**; do not block ship on it" becomes the delivered contract; 07 `:9` gains the update check (as D-1544 is ruled).
- **A wrong reference in the homes:** both homes cite `electron.build/auto-update`, which answered 404 on 2026-11-26. Row 18 changes the citation to `https://www.electron.build/v26/docs/features/auto-update/` in the two Source cells.
- Validation: `rg -n "MEU-173|MEU-174" docs/BUILD_PLAN.md docs/build-plan/build-priority-matrix.md .agent/context/meu-registry.md` and `uv run python tools/meu_status.py render --check` (row 18 and H1-3).

## Verification Plan

Commands use the D6 argv of `.agent/docs/commands.md`. `PLAN` is `docs/execution/plans/2026-11-26-app-auto-update` and `R` is `C:/Temp/av-kit/2026-11-26-app-auto-update`.

### 1. Baseline (row 0)

`PLAN/baseline.ps1`, written in row 0 in the shape of `2026-11-22-tray-show-and-baseline-fixes/baseline.ps1`, fail-fast:

1. `uv sync --frozen --offline --all-packages`.
2. Records `baseline.sha` (`HEAD`, never compared with a pinned commit), `baseline-dirty.txt` with `git worktree list`, `baseline-dirty-hashes.json`, `baseline-scope.json` (every §Files Modified path to its SHA-256 or `absent`; every new path must be `absent`), `baseline-eol.json` (each scope file's line endings, measured from bytes) and `baseline-pins.json` (the SHA-256 of each §Test pins file).
3. Copies `red-check.py`, `identity.py`, `eol-check.py`, `canon-edit.py`, `issue-resolve.py` and `crlf.py` from `2026-11-22-tray-show-and-baseline-fixes/`, and `snapshot-commit.py` and `session-gate.ps1` from `2026-11-20-e2e-devpc-clipboard/`, each set to this plan's folder, receipts folder and scope, and records their hashes. `snapshot-commit.py` gains `--changed-scope`: the `baseline-scope.json` paths that differ from `HEAD` now, in place of a path list. Writes `row-check.py` (`red-record --row N FILE…` and `red-unchanged`, the hashes of the Red test files; and the row checks that `task.md` names: `openapi-leaf`, `electron-binary`, `canon`, `register`, `status`, and `macro-current FILE`, which compares the SHA-256 of `ui/build/installer.nsh` with the one row 3 recorded in FILE), `pins-scan.py` (lists which §Test pins files enumerate channels, keys, sections or leaves), `run-check.py` (reads a remote run's console receipt and its summary: the last `e2e-remote:` line, the main-stage failures by title, the install block; flags `--expect-red ID…`, `--expect-green`, `--require-main ID…`, `--install passed`, `--require-install ID…`; it never accepts exit 22 or 23) and `licence-check.py`. Each has a `--selftest` on fixtures.
4. Free ids: `AC-173.`, `AC-174.` and D-1540 to D-1599 appear nowhere outside this plan folder and the grouping; the new file names are absent.
5. Base receipts, failures recorded and not fatal: full Vitest (`aau-base-ui.txt`), full pytest (`aau-base-py.txt`), MCP tests (`aau-base-mcp.txt`).
6. The npm dist-tags of `electron-updater` (`npm view electron-updater dist-tags --json`): S7 if `latest` is no longer a 6.8 version.
7. The host: `uv run python tools/e2e_remote.py check --out R/aau-host-check-0.json`. An unreachable host is recorded, not fatal here; it becomes S9 at row 7.

### 2. Red, then Green

Each Red row changes no product file and passes when the named tests fail by assertion; `red-check.py` reads the receipt and its `.exit` file and refuses setup failures (a missing module, a collection error, a timeout). So a Red test of a module that does not exist yet loads it inside the test (a dynamic `import()` in Vitest, `importlib` or `hasattr` in pytest) and asserts first that the load gave the named export; Green keeps the test text. New test titles start `AC-173.<n> ` or `AC-174.<n> `; pytest names start `test_ac_173_<n>_` or `test_ac_174_<n>_`. The pytest tests of `FEED_CHECK` call the script through `subprocess`, so a missing script fails by assertion. Each Green row runs the same files to a pass, then the type check and lint of its layer, `eol-check.py` over the scope, and `pins-scan.py --check` (the pins grew only by this plan's entries).

OpenAPI (row 9, two steps): `uv run python tools/export_openapi.py --check openapi.committed.json` must fail with drift, then `uv run python tools/export_openapi.py -o openapi.committed.json`, then the check passes.

Licence (row 13): `PLAN/licence-check.py` lists every package the lock file gained and requires each `license` to be one of MIT, ISC, BSD-2-Clause, BSD-3-Clause, Apache-2.0, 0BSD or BlueOak-1.0.0 and each to carry a licence file that `tools/generate_third_party_licenses.py` can read (`_npm_section` reads `ui/package-lock.json`); row 3's sibling build in row 16 runs the generator on the real tree, and a problem line there is S7.

### 3. Real builds (rows 3 and 16)

`PLAN/build-update.ps1`, written in row 3, follows `2026-11-22-release-rc5/build-rc5.ps1` step for step (the offline guard, the build inputs, the cached FFmpeg and Deno, `tools/package_backend.py`, `npm --prefix ui run dist:prep`, `tools/generate_third_party_licenses.py`, the pack, the resources check) in a tree extracted from the session's snapshot commit under `C:/Temp/av-kit/s106-src`. It differs in three ways: it writes no build record, it never names a release version, and its pack step depends on `-Mode`:

- `-Mode product`: `npx electron-builder --win nsis --x64 --publish never` with the committed config. Output `C:/Temp/av-kit/s106-out/product`. Before the pack it stops with `build-update: macro-missing exit=12` when the extracted `ui/build/installer.nsh` lacks `!macro customCheckAppRunning` (row 2b), and it records that file's SHA-256 in `R/aau-row3-macro.json`, which row 7 checks with `row-check.py macro-current`. It then runs the three `FEED_CHECK` calls below and writes the canary payload folder `C:/Temp/av-kit/s106-payload/canary` (the installer and a `payload.json` with `mode: "canary"`).
- `-Mode pair`: two pack runs over the same prepared tree, each with a generated full copy of the config whose `publish` block is the generic local feed, `-c.extraMetadata.version=0.0.901` then `0.0.902`, and its own output folder. It checks that each `win-unpacked/resources/app.asar` lists `node_modules/electron-updater/package.json`. It then writes the payload folder `C:/Temp/av-kit/s106-payload/roundtrip`: both installers, `latest.yml` and the blockmap of `0.0.902`, a `latest-bad.yml` whose two SHA-512 values are those of the old installer, and `payload.json`.

The script takes `-Snapshot <receipt of snapshot-commit.py>` and, in pair mode, `-Out <json>`. Checks: `FEED_CHECK` on the product output (`feed-ok`, exit 0), on a copy with `latest.yml` moved away (`feed-missing`, exit 10), on a one-byte-changed copy (`sha512-mismatch`, exit 15), and with `--provider generic` on the `0.0.902` output. Each installed `resources/app-update.yml` is read back; if the generated config did not produce the generic feed, that is S8. The script's last line is `build-update: <reason> exit=<n>` (`product-ok` or `pair-ok` with 0; `macro-missing` with 12).

### 4. Electron on the mini-air host (rows 7 and 17)

Each run: `PLAN/snapshot-commit.py --changed-scope --out R/aau-snapshot-<row>.json` over this session's paths only, then `--verify` (run 2 uses row 16's snapshot, the one the pair was built from); `tools/e2e_remote.py check`; `tools/e2e_remote.py run <snapshot commit> --payload <dir>` in the background, waited on, never polled by hand. The row's evidence is the tool's last stdout line `e2e-remote: <reason> exit=<n> run=<run-id> receipts=<folder>` and the receipt folder, read by `PLAN/run-check.py`.

- **Run 1 (row 7), canary and E2E Red.** Payload: the product installer of row 3, `mode: "canary"`. The tree holds MEU-173, the bounded running-app check of rows 2a and 2b (`APP_RUNNING_CHECK`, so the installer under test stops the inside decoy and spares the sibling), the install stage and the Red `app-update.test.ts`, and no updater. Before the run, `row-check.py macro-current` proves that `ui/build/installer.nsh` is the file row 3 built; if it changed, row 3 runs again first and rebuilds the payload. Expected: the main stage fails in exactly the `AC-174.15` and `AC-174.16` titles, each by assertion; the install stage passes. So the tool's last line is `e2e-remote: new-failures exit=40 …`, and `run-check.py --expect-red AC-174.15 --expect-red AC-174.16 --install passed` decides the row: it refuses any other new failure, any other reason and an install block that is not all passed.
- **Run 2 (row 17), Green and the round trip.** Payload: the pair of row 16. Expected: `e2e-remote: … exit=0`, the main stage passing with `app-update.test.ts` in it, the install stage passing with no skip; `run-check.py --expect-green --require-main AC-174.15 --require-main AC-174.16 --install passed --require-install AC-174.19 --require-install AC-174.20` decides the row.
- `host-busy` (22) and `host-locked` (23) mean wait and run again; they are never a pass. Other refusals follow the run book's table; S9 and S10 name the stops.

### 5. Session gate (H1-2)

`PLAN/session-gate.ps1` runs the D6 full rows on the dev PC (ruff, pyright, full pytest, `npm --prefix ui run typecheck`, lint, full Vitest, the three MCP rows, the OpenAPI check, `tools/check_update_feed.py --selftest`, `tools/e2e_remote.py`'s unit tests, `eol-check.py`, `pins-scan.py --check`) and binds run 2's receipts by run id and snapshot commit. It is fail-fast, prints later steps as `not_run`, and its last line on a pass is `session-gate: all steps exit 0`. It launches no Electron.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | The plan review has not approved, or the execution approval is not written into the Status line at row 0 | Do not start |
| S2 | D-1543 or D-1544 is ruled differently from the recommendation | Stop before row 12; the plan is corrected through `/plan-corrections` (the rows named in the brief) |
| S3 | A Red test passes, or fails for a setup reason; a Red file's hash changes in Green | Stop; fix the test in its Red row, never the expectation in Green |
| S4 | `git status` shows a path that is neither this plan's nor in `baseline-dirty.txt`, or another session's dirty copy of a §Files Modified path | Stop and name it; never commit, stash or revert another session's work |
| S5 | An existing assertion must change beyond `PIN_GROWTH` and the `login-item-nsh.test.ts` lines that row 13 names | Stop; that is M-7 and needs a named plan row |
| S6 | Any row would upload, tag, publish, push, change the version or call `gh release` | Never; that is Mat's step |
| S7 | `electron-updater` `latest` is not a 6.8 version, the install adds a package other than the library and its dependencies or changes the version of any existing package, or a new package has a licence outside the list | Stop with the lock file diff |
| S8 | A probe fails: `forceDevUpdateConfig` does not allow a download in the E2E run; the generated config does not produce the generic feed; Playwright cannot start the installed exe and the CDP fallback also fails | Stop with the receipt; the design choice goes back to a brief |
| S9 | The host is unreachable, or refuses the unsigned installer or the installed app (`installer-refused-by-host`, `app-refused-by-host`), or the install stage's precondition finds an existing install | Mark rows 7, 16 and 17 `[B]` with the receipt; finish the dev-PC rows; MEU-174 is not complete; Mat decides (D-1552, D-1216). Never move the round trip to the dev PC |
| S10 | A remote run ends with an exit from 10 to 34 other than 22 and 23, or with 41, or the after snapshot differs from the before snapshot, or the install stage refuses `install-quarantined` | Per the run book: `release` once with this session's own run id; a snapshot difference or a quarantine is reported to Mat with the names that differ and the owner record's path before any further payload run; `release` frees the host lock and is never a restoration of the account |
| S11 | A test or a row would reach `github.com` or any host but `127.0.0.1` and the npm registry rows named above | Stop |

## Decision Log

Hand-over: Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'. A brief with no M-list hit, or only M-3, M-5, M-6 or M-8, is decided by its recommendation and recorded `autonomous`; any other M item stays Mat's. `Expert pass: inline, not independent.` (the planner may not dispatch a reviewer). Precedent sweep: `C:/Temp/av-kit/2026-11-26-plans/s106/precedent-sweep.txt`. The next free id is D-1555 (the round-1 corrections added D-1554).

**Carried from the grouping §8:** D-1410 (autonomous: four sessions, execution order 104, 103, 106, 105), D-1411 (human: Electron E2E on the mini-air host, 'use fleet member mini air for E2E testing during execution'), D-1412 (autonomous: tiers, `owns` lists, run parameters), D-1413 (**ruled**, human, Mat 2026-11-26: 'drafts stand'; M-6: the drafts were started before the scoping review), D-1414 (autonomous: one pass to plan drafts), and D-1200 (open, Mat's, M-12, carried unchanged). The scoping review approved the grouping at round 2; Mat's 'drafts stand' is the ruling on D-1413 (`C:/Temp/av-kit/2026-11-26-plans/mat-ruling-2026-11-26-execution.txt`).

```yaml
decision_log:
  - id: D-1540
    stage: planning
    question: Which releases does the feed offer while every release is a release candidate marked Latest?
    resolution: autonomous
    class: product-preference
    mandatory: [M-3, M-5]
    chosen: "A: the release GitHub marks Latest (allowPrerelease false, allowDowngrade false)."
    source_tag: Research-backed
    precedents:
      - "release-rc5: each release candidate is published with --latest and no pre-release flag"
      - "07 §Update feed, Which releases row: a Decision Brief of the plan"
    research:
      engine: web + source read
      sources:
        - "electron-updater 6.8.11 GitHubProvider (R3), read 2026-11-26"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The library default on an rc build follows rc tags only and would never offer a stable 0.1.0. Following Latest gives Mat one lever he already uses: mark a release Latest and it is offered; flag it pre-release and it is not."
    human_message_reference: null
  - id: D-1541
    stage: planning
    question: What is the default interval, and can the user turn the check off?
    resolution: autonomous
    class: product-preference
    mandatory: [M-3, M-5]
    chosen: "A: weekly by default; a third value, never. Never is an addition to Mat's two intervals."
    source_tag: Local Canon
    precedents:
      - "D-1409: once a week or once a month"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Releases come days apart, so weekly reaches users soonest. The check is a new request to GitHub; a user who wants none must be able to stop it, and D-1544's statement can then say how."
    human_message_reference: null
  - id: D-1542
    stage: planning
    question: What does "automatically" mean in steps?
    resolution: autonomous
    class: product-preference
    mandatory: [M-3, M-5]
    chosen: "A: check on the schedule, download at once in the background, one notice, install only on the user's click on Restart and update; nothing installs at quit."
    source_tag: Local Canon
    precedents:
      - "07 §In-app update, Install row: the app never restarts while a job runs unless the user chooses it"
      - "P:/zorivest docs/build-plan/18-first-install-ux.md §18.12, U-1 (Mat, 2026-10-23): install on the Restart and update click, quitAndInstall(true, true)"
    research:
      engine: web + source read
      sources:
        - "electron-builder issue 7807 (R4): an install at quit can leave the app unusable when Windows shuts down; fixed only in the 27 alpha"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. No visit to the release page and no file to run: that is Mat's request. A restart by itself could end a running job, and the app has no signal that says whether one runs. Close-to-tray means the app seldom quits, so an install at quit would seldom happen and carries the shutdown risk."
    human_message_reference: null
  - id: D-1545
    stage: planning
    question: Do MEU-173 and MEU-174 stay one session?
    resolution: autonomous
    class: governance-value
    mandatory: [M-8]
    chosen: "A: one session, MEU-173 first with its own handoff, three compact_continue boundaries."
    source_tag: Local Canon
    precedents:
      - "grouping, Session 106 split flag: over half a context, MEU-173 becomes its own session"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Sized by count, because metrics.md holds no row for the two calibration sessions under their names: 20 work rows, about 51 files after the round-2 corrections, two host runs of about 40 minutes and three installer builds. That is likely over half a context. But MEU-173 is 3 of the 20 rows; moving it out leaves the heavy part whole and adds a second plan, review and closeout. The round trip needs both MEUs in one tree. The boundaries and the separate MEU-173 handoff carry the context risk. This departs from the letter of the split rule, so M-8 is named."
    human_message_reference: null
  - id: D-1546
    stage: planning
    question: Does MCP expose the setting only, or also a check or install action?
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "A: the setting only, as a leaf of the existing avkit_settings tool."
    source_tag: Local Canon
    precedents:
      - "07 §In-app update, Setting surface row names the MCP settings tool"
      - "D-717 (MEU-105): style leaves added to the same tool"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The home requires the leaf. A check or install action would be a new tool shape (M-4) and would let an assistant restart the app; nobody asked for it."
    human_message_reference: null
  - id: D-1547
    stage: planning
    question: Where does the update status live in Settings?
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: a new Updates section in the App group, after Startup, holding the interval, the version, the status line and the two buttons."
    source_tag: Local Canon
    precedents:
      - "settings-sections.ts: Startup is a main-process-backed section in the App group"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The interval, the result of the last check and the restart control belong together; Console & logging is about something else."
    human_message_reference: null
  - id: D-1548
    stage: planning
    question: Does Settings also offer a check on request?
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: a Check now button in the Updates section; it works with every interval, never included."
    source_tag: Local Canon
    precedents:
      - "07 §In-app update, Check row: whether Settings offers a check on request is a Decision Brief of the plan"
      - "D-1409 covers the scheduled check only"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Mat asked only for the schedule; this is an agent choice and its ACs cite this id. With a weekly check, a user told that a fix is out would otherwise wait up to a week or fetch the installer by hand, which is what the feature removes. A user who chose never still gets updates when they ask."
    human_message_reference: null
  - id: D-1549
    stage: planning
    question: What does the app do about running jobs when the user clicks Restart and update?
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: a fixed sentence beside the button says that running downloads, transcripts, speech and conversions stop; the click is the user's choice."
    source_tag: Local Canon
    precedents:
      - "07 §In-app update, Install row"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Three of the four job kinds report a processor state and TTS has no list route, so a count would be wrong for speech; a wrong 'nothing is running' is worse than a plain warning. A true count needs a new route outside this session's files."
    human_message_reference: null
  - id: D-1550
    stage: planning
    question: Where does the schedule state live, and what are the periods and the retry rule?
    resolution: autonomous
    class: two-way
    mandatory: [M-3]
    chosen: "A: a main-process store file update-state.json in the app-data folder; weekly 7 days, monthly 30 days; first tick 60 s after the backend is ready, then hourly; a failed check is tried again no sooner than 24 h later; a found version that is not installed is checked once at each start whatever the 24 h rule says, then no sooner than 24 h after the last attempt; a failed or invalid interval read skips that tick's check and never stands in for an interval."
    source_tag: Local Canon
    precedents:
      - "ui/src/main/index.ts:486: ui-state store in the app-data folder"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The time of the last check is not a user setting, so it stays out of the settings layers and the MCP schema. A day between failed tries keeps an offline PC quiet. Round 1 found two gaps (F1, F6): a failed read that counted as weekly would check a PC whose user chose Never, and the 24 h rule blocked the check that brings Restart and update back after a restart."
    human_message_reference: null
  - id: D-1551
    stage: planning
    question: How does an Electron E2E reach a feed without a real release?
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "A: a seam read only when AVKIT_E2E is 1: a feed config file, short ticks, and a recorder in place of quitAndInstall."
    source_tag: Local Canon
    precedents:
      - "ui/src/main/e2e-shell.ts; __AVKIT_E2E_TRAY__ (MEU-164, D-1366)"
    research:
      engine: web + source read
      sources:
        - "electron-updater 6.8.11 AppUpdater forceDevUpdateConfig and updateConfigPath (R3)"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The home's Tests row asks for an E2E against a local feed. An E2E must not run an installer, so the install call is recorded there and the real install is proved by the round trip."
    human_message_reference: null
  - id: D-1552
    stage: planning
    question: How does the real update round trip run, given that the remote E2E tool installs nothing today?
    resolution: autonomous
    class: governance-value
    mandatory: [M-3]
    chosen: "A: on the mini-air host, as a third stage of tools/e2e_remote.py that takes a payload of installers built on the dev PC; a canary run early; if the host refuses the unsigned installer the rows block and Mat decides."
    source_tag: Local Canon
    precedents:
      - "07 §In-app update, Tests row: run by script on the remote E2E host"
      - "grouping D-1411"
      - "D-1216: Smart App Control on the host is Mat's"
      - "Session 49 install-roundtrip.ps1: silent install to a scratch folder, snapshots before and after"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The home already puts a real install on the host; this brief picks the smallest mechanism and changes the run book's 'never installs anything' sentence, a policy change (M-3). M-13 was read and judged not hit: the stage runs in the same account with no elevation and adds no credential or permission setting. The dev PC is refused as a fallback: after an update the installer starts the app through the shell, without the test's environment, so it would open Mat's real app data."
    human_message_reference: null
  - id: D-1553
    stage: planning
    question: What happens to the updater's cache at uninstall, now that it holds a downloaded installer?
    resolution: autonomous
    class: two-way
    mandatory: [M-5]
    chosen: "A: the uninstall macro removes the folder with its content (RMDir /r), still skipped on an update; the two DeleteRegValue lines move inside the same not-updated block, so an update keeps Start at sign-in."
    source_tag: Local Canon
    precedents:
      - "MEU-114, 07 §Uninstall removes the installer copy (residual)"
    research: {engine: none, sources: []}
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The folder holds only installer copies the app downloaded, about 450 MB after one update; the plain RMDir fails on a folder that is not empty. M-2 was read and judged not hit: no user data is in that folder, and the uninstaller already removes it when empty. M-7 was read: five lines of login-item-nsh.test.ts change (:105 the fixture, :112 the pattern, :119 the expected list, :122 the title, :125 the recursive count; :124 and AC-61.18 stay), and row 13 names each line with its new assertion, which is the condition that clears M-7. M-5 is hit by the sign-in lines (round 1, F5): today an update, or an install over an existing one, deletes the user's Start at sign-in entry, because the old uninstaller runs with --updated and the two lines sit before the guard; inside the guard the entry stays, as the Startup card says. An rc.5 user still loses it once, at the manual install of the first updater release, because rc.5's own uninstaller runs then; the checklist says so."
    human_message_reference: null
  - id: D-1554
    stage: planning
    question: Which processes may the installer and the uninstaller stop, and what happens when they cannot check?
    resolution: autonomous
    class: two-way
    mandatory: [M-5]
    chosen: "A: a customCheckAppRunning macro that stops only processes whose file is inside the install folder (a bounded path match, the installer's own pid excluded), with no image-name fallback; when PowerShell cannot run or a process does not stop, the installer shows appCannotBeClosed, sets error level 2 and quits before any file changes."
    source_tag: Research-backed
    precedents:
      - "allowOnlyOneInstallerInstance.nsh:5-8, :32-43, :66, :94, :97-99 (app-builder-lib 26.18.0)"
      - "NsisTarget.js:393, :408, :463, :709-712: the custom include is in the shared header of both scripts"
      - "task.md Processes rule: no row stops a process by image name"
    research:
      engine: source read
      sources:
        - "ui/node_modules/app-builder-lib/templates/nsis/include/allowOnlyOneInstallerInstance.nsh"
        - "ui/node_modules/app-builder-lib/out/targets/nsis/NsisTarget.js"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Round 1 (F4) found that the stock check matches any path that starts with the install folder's text and falls back to taskkill /IM av-kit.exe, which would stop a development worktree's app or another install. M-5 is hit: a user whose PowerShell is blocked sees 'cannot be closed' and the update waits, where the stock check would stop every av-kit.exe of the account. M-13 was read and judged not hit: the check asks for no elevation and stops fewer processes than today. M-4 was read and judged not hit: no API, file format or public statement changes."
    human_message_reference: null

  - id: D-1555
    stage: execution
    question: Where do the HOST_PAYLOAD unit tests live, when the plan names tests/unit/test_e2e_remote.py?
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "tests/tooling/test_e2e_remote.py, the file that exists; the plan's unit path does not."
    source_tag: Local Canon
    precedents:
      - "tests/tooling/test_e2e_remote.py holds the e2e_remote unit tests today"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The recommendation is the existing file: a second test file for one tool splits its tests."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1556
    stage: execution
    question: Which copies of the plan-local scripts does row 0 start from?
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Session 103's adapted copies (2026-11-26-capture-key-inbox-scrollbars), the newest ruff-clean copies of the named sources, with this plan's folder, receipts and scope."
    source_tag: Local Canon
    precedents:
      - "Session 103 copied the same scripts from the same sources and adapted them"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The logic is the named sources'; Session 103's copies carry the fixes made since."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1557
    stage: execution
    question: What counts as a use of a reserved decision id in the free-id check?
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Only a definition: a decision-log 'id: D-15xx' entry or a '### D-15xx' heading. A line that names an id in passing (a later plan citing this reservation, this plan's own prose) is not a use."
    source_tag: Local Canon
    precedents:
      - "Later plans (Session 105) cite D-1540 to D-1599 as this plan's reservation"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Counting mentions made a citation a collision and made a prose mention look like a taken id."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1558
    stage: execution
    question: "Row 0's selftest list named canon-edit.py, issue-resolve.py and crlf.py, which have no --selftest (nor do their sources), and the plan's Python was not ruff-clean. How does row 0 finish?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Drop the three from the selftest list (ruff covers them), fix the long lines in pins-scan.py, run-check.py, licence-check.py and red-check.py (no logic change), and run step 8 alone with baseline.ps1 -SelftestsOnly into aau-baseline-step8.txt. Steps 0 to 7 stand from aau-baseline.txt."
    source_tag: Local Canon
    precedents:
      - "2026-11-22-tray-show-and-baseline-fixes/canon-edit.py has no --selftest"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A second full record after row 1 would find row 1's new files present and fail the absent check; step 8 reads no tree state."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1559
    stage: execution
    question: What does pins-scan.py count as an enumerating file, and what growth does --check allow?
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "A file enumerates a list when it names two or more of the list's known entries. --check allows an added line that names one of this plan's new entries (or is punctuation), a count that grows by this plan's entries, and an inline list that gains only this plan's names; any other change is S5."
    source_tag: Local Canon
    precedents:
      - "PIN_GROWTH: a pin may change only by gaining the new entries of this plan"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. One name is a reference, not a list; the allowances are PIN_GROWTH's three shapes."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1560
    stage: execution
    question: What does baseline-pins.json hold?
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Per §Test pins file: whether it enumerates, which lists, and its SHA-256; the byte copies under R/baseline-copies are the diff base of --check."
    source_tag: Local Canon
    precedents:
      - "Verification Plan 1, step 2: baseline-pins.json (the SHA-256 of each §Test pins file)"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1561
    stage: execution
    question: Where does build-update.ps1 build, given that build-identity.py needs git and the snapshot commit sits on no ref?
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "A clone of P:/av-kit at C:/Temp/av-kit/s106-src (git clone --shared --no-checkout, then a detached checkout of the snapshot commit), set up offline (uv sync, npm ci in ui and mcp-server). The output is moved to C:/Temp/av-kit/s106-out/product, so the committed config builds unchanged."
    source_tag: Local Canon
    precedents:
      - "release-rc5 row 2: a clone detached at the release commit in C:/Temp/av-kit/rc5-src"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A clone is not a branch or a worktree of P:/av-kit and changes no ref there; an archive extract has no git for build-identity.py."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1562
    stage: execution
    question: "Row 2b's first Green failed: find exited 0 with one matching process running. What does the macro change?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Wrap each call of the selection block in @() ($p = @(& $s), while (@(& $s).Count, if (@(& $s).Count)), because Windows PowerShell 5.1 unrolls a one-element array into a single CimInstance with no Count. And map an nsExec result that is not a number (error, timeout) to 2 before the != 0 refusal, because LogicLib's != compares integers and reads 'error' as 0."
    source_tag: Local Canon
    precedents:
      - "R/aau-row2b-green.txt first run: expected +0 to be 1 at app-running-nsh.test.ts:160"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Both fix the contract's own refusal rule; the Red test file is unchanged."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1563
    stage: execution
    question: "Row 3's first build stopped at the ffmpeg copy: a fresh clone has no packaging/ffmpeg-win64 (gitignored). How does build-update.ps1 prepare it?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Create the folder (New-Item -Force on the archive's parent) before copying the cached ffmpeg-pin.zip, as the deno step already does; the failed receipt is kept as aau-row3-build-r1.txt."
    source_tag: Local Canon
    precedents:
      - "build-rc5.ps1 copies into a folder that already existed in its tree; its deno step creates its folder first"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Setup only; the archive and its pin are unchanged."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1564
    stage: execution
    question: "The plan names four install-stage precondition folders. Does the packaged app write any other per-user folder?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Add %APPDATA%/av-kit as the fifth folder: the packaged Electron userData follows productName (av-kit), while the dev build uses av-kit-ui. checkPreconditions refuses install-folder-exists on any of the five."
    source_tag: Local Canon
    precedents:
      - "ui/electron-builder.yml productName av-kit; Electron app.getPath('userData') = appData/<productName> when packaged"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A stricter precondition; it only refuses more."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1565
    stage: execution
    question: "The existing pins of run-e2e.ps1 allow one Start-Process and exactly one ungated and one gated AvStage call. How does the third (install) stage run?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "The main and install stages share the one ungated AvStage call in a loop over the stage names; the gated block runs inside the main iteration, so the order stays main, gated, install. AvStage gains -Config and -PayloadDir; AVKIT_E2E_PAYLOAD_DIR is set for the child only and cleared after Start-Process."
    source_tag: Local Canon
    precedents:
      - "tests/tooling/test_e2e_remote.py test_ac_14_host_static_launcher and test_s98_ac_20_clipboard_file_guard (PIN_GROWTH: existing tests unchanged)"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Keeps every existing pin byte-identical (S5) and the contract's stage order."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1566
    stage: execution
    question: "Row 5's cell parse step ran a nested pwsh -Command in double quotes, so the outer pwsh expanded $f and $e to nothing (ParserError). How is the cell corrected?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Replace the nested pwsh with an in-process script block (the call operator & on a script block) that sets $global:LASTEXITCODE; the checks are unchanged. task.md row 5's cell is edited; the failed receipt is kept as aau-row5-parse-r1.txt."
    source_tag: Local Canon
    precedents:
      - "R/aau-row5-parse-r1.txt: Missing variable name after foreach"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A defect of the cell's quoting, not of the code under test."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1567
    stage: execution
    question: "Row 11's first full MCP test run timed out one test (AC-67.19, tests/audit/runner-fake-backend.test.ts, 5000 ms) in a file this session does not touch, while the host run's local side was running. Is it a finding?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Rerun unchanged: 560 of 560 passed. The r1 receipts are kept as aau-row11-types-r1.txt and aau-row11-tests-r1.txt. No timeout or test was changed."
    source_tag: Local Canon
    precedents:
      - "D-1438 (gates under outside load: rerun unchanged and record it)"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The directive names this case: a timeout only in an untouched file under outside load."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1568
    stage: execution
    question: "Row 11's cell runs `npm --prefix mcp-server run audit` with no arguments, and the runner refuses with '--mode must be container or authoritative' (exit 4). Which audit does the row run?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "The authoritative check against the baseline, as the skill's table gives it: --mode authoritative --baseline <abs baseline> --report R/aau-row11-audit-report.md --out R/audit-11 --agent claude, with no --update-baseline. The report goes into the receipts folder, so the tracked report and the baseline do not change. task.md row 11's cell is edited; the refused receipt is kept as aau-row11-audit-r1.txt."
    source_tag: Local Canon
    precedents:
      - ".agent/skills/mcp-tool-audit/SKILL.md §Running it, row 'Authoritative check against the baseline'"
      - "The baseline holds no leaf list (no log_level entry), so PIN_GROWTH adds nothing to it"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A cell defect; the authoritative mode is the only one that checks the baseline on Windows."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1569
    stage: execution
    question: "Row 13's pins-scan --check refuses ui/tests/unit/clipboard-image-main.test.ts as 'changed but does not enumerate a list', but its AC-88.8 line pins RENDERER_TO_MAIN_CHANNELS at 22, and with the three update channels the test fails unless 22 becomes 25. Is the change S5?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "No. The file imports the channel list and names fewer than two channels, so row 0's two-name scan recorded it as 'no list', but the plan names it in §Test pins (IPC and preload) and row 13 says the channel census grows from 22 to 25. pins-scan.py sets it by hand (BY_HAND kind channel-count, as for the census and login-item-nsh), and its baseline-pins.json entry is set to that kind with the row 0 hash unchanged. Its only change is the count line. The refused receipt is kept as aau-row13-pins-r1.txt; the selftest passes 11 of 11."
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md §Test pins: clipboard-image-main.test.ts is listed under IPC and preload"
      - "PIN_GROWTH: a replaced line whose only change is a number is a growth"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A miss in the scan's heuristic, not a change of an assertion."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1570
    stage: execution
    question: "AC-132.12 pins 'capture-paste-image' as the last renderer-to-main channel and 'pasteCaptureImage' as the last preload key. Where do the three update channels and the four update keys go?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Just before 'capture-paste-image' and 'pasteCaptureImage', in ipc.ts, preload.ts and the test list ipc-channels.ts. AC-132.12 and every other existing assertion stay unchanged. The order of the lists has no other effect. The first pins run (aau-row13-pins-run-r1.txt, 1 failure in AC-132.12) is kept."
    source_tag: Local Canon
    precedents:
      - "PIN_GROWTH: an existing assertion may change only by gaining the new entries"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Placing the entries changes no existing assertion; appending would change one."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1571
    stage: execution
    question: "How does index.ts give install() the same backend stop that before-quit makes, and what does it do under AVKIT_E2E=1, where before-quit returns before any stop?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "One shared shutdownForQuit() holds the single shutdownOwned('quit', ...) call (the same arguments as before), memoised, so the update's own quit reaches before-quit, finds the stop done and exits. before-quit still calls setQuitIntent, returns under AVKIT_E2E=1, and otherwise calls event.preventDefault() and then app.exit(0) after the stop, so a normal quit does what it did before. Under AVKIT_E2E=1 the controller gets a no-op stop, which mirrors before-quit's early return: the E2E harness owns the backend, and the seam records quitAndInstall instead of running it."
    source_tag: Local Canon
    precedents:
      - "task.md row 13 (3): shutdownBackend is the same shutdownOwned('quit', ...) call that before-quit makes, with the handler unchanged in what it does on a normal quit"
      - "capture-main.behavior.test: before-quit's first 520 characters hold the AVKIT_E2E early return"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. One call site cannot drift from the other, and the E2E path matches the quit path."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1572
    stage: execution
    question: "Row 15's pins-scan --check refuses ui/tests/e2e/test-ids.ts as 'changed but does not enumerate a list', but row 15 names test-ids.ts among the pins it grows. Is adding the Updates ids S5?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "No. test-ids.ts carries the section keys only inside longer ids (settings-rail-download), so row 0's two-name scan recorded it as 'no list'. pins-scan.py sets it by hand (BY_HAND kind test-id-list, as for D-1569), and its baseline-pins.json entry is set to that kind with the row 0 hash unchanged. Its only change is eight added export lines, each naming an Updates id. The selftest passes 11 of 11."
    source_tag: Local Canon
    precedents:
      - "task.md row 15: grow test-ids.ts per PIN_GROWTH"
      - "D-1569: the same scan miss for clipboard-image-main.test.ts"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A miss in the scan's heuristic, not a change of an assertion."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1573
    stage: execution
    question: "UPDATES_CARD must use the select that the Console & logging card uses, which is GridSelect, a non-exported function in SettingsPage.tsx. How does UpdatesCard.tsx reach it?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "SettingsPage.tsx exports GridSelect (the keyword only) and UpdatesCard.tsx imports it. The import cycle is resolved at render time, not at module load, and no lint rule forbids it. No new select is written, and the Console card is unchanged."
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md UPDATES_CARD: existing select and button components only"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Reuse keeps one select; moving it to a new file would touch files the plan does not list."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1574
    stage: execution
    question: "Row 7's host run r20261127T225928Z-e1518e1 ended new-failures exit=40 with the install stage ran 1/1 passed, but run-check.py reported 3 problems: it compared the new failures as a list with repeats, it required every AC-174.16 test to be 'unexpected' although the serial file skipped them after AC-174.15's first assertion failure, and it read install.status where tools/e2e_remote.py writes install.state. Is row 7 [B], or is the checker wrong?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "The checker is wrong, and the run is not repeated. run-check.py now compares the set of AC ids; accepts a test skipped in a serial file only when the same file has an assertion failure; reads the install block in the shape e2e_remote.py writes (state 'ran' with counts); and reads --require-install from host/install/report.json. The selftest passes 15 of 15 (two new serial cases). The re-check of the same console receipt gives 0 problems: AC-174.15 fails on getByTestId('updates-settings') not found, the other five tests are not run, and the canary passed. The first check is kept as aau-row7-run-check-r1.txt. Open item: on the host, AC-174.16's Red is shown only as 'not run behind the serial block'; its own failure is shown by the unit Reds of row 12. Smart App Control was Off."
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md HOST_PAYLOAD: the summary gains an install block (counts, or not-run)"
      - "ui/tests/e2e/app-update.test.ts:220 test.describe.configure({ mode: 'serial' })"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The run's results are what the plan asks for; only the checker's reading of them was wrong, so repeating the run would add nothing."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1575
    stage: execution
    question: "ROUND_TRIP step 7 requires 'the main log holding update: backend stopped before the installer started', but the main process keeps the updater's lines only in memory (appendStdoutLog) and in the renderer's console view, which close with the old app. Where does the round-trip spec read them?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "The updater's log callback in ui/src/main/index.ts also writes each line to the main process's stdout (writeStdoutLine: one 'error' listener and a writable check, so a missing or closed stream is ignored), as the picker probe at index.ts boot() already does. The spec collects the old app's stdout (Playwright's app.process(), or a piped spawn on the CDP fallback) and requires 'update: install requested' and then 'update: backend stopped'. The lines are written in the main process before quitAndInstall, which is the call that starts the installer, so their order in that stream is the order the step asks for. No other line and no file changes."
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md UPDATE_INSTALL_ORDER: log('update: backend stopped') before updater.quitAndInstall(true, true)"
      - "ui/src/main/index.ts boot(): process.stdout.write for the picker path probe"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Reading the renderer's view races the window's close; a new log file would be a larger product change. index.ts is already in this session's scope (row 13)."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1576
    stage: execution
    question: "build-update.ps1 -Mode pair must pack 0.0.901 and 0.0.902 from one tree with the generic local feed. The plan names '-c.extraMetadata.version=VERSION' beside a generated config, but electron-builder's -c is the --config option itself, so a config path and -c.* values in one call conflict. How are the two packs configured?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Each pack uses a generated full copy of ui/electron-builder.yml (ui/electron-builder.pair-VERSION.yml in the scratch clone) whose only changes are the publish block (provider generic, url http://127.0.0.1:47911/), directories.output (dist-pair-VERSION) and an added extraMetadata.version VERSION; the script prints the line diff of each. Each mode deletes only its own output and payload folder, so row 7's canary payload stays. The licence list's output is scanned for a problem line (S7), each app-update.yml is compared with the local feed (S8), each app.asar is listed with @electron/asar, and latest-bad.yml is the 0.0.902 feed with both SHA-512 values replaced by the 0.0.901 installer's. In the spec, the feed starts in an 'off' mode (404) before the app starts, so a check at start cannot reach either feed; app.update_interval is read from avkit.db by the installed exe's own Node (ELECTRON_RUN_AS_NODE, node:sqlite read-only, as setup-readiness.ts reads it); and an afterAll runs the stage's teardown when AC-174.19 fails, because the serial block would not run AC-174.20."
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md build-update -Mode pair: a generated full copy of the config per pack"
      - "ui/src/main/setup-readiness.ts: DatabaseSync(dbPath, { readOnly: true })"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The same three values reach electron-builder, from one file per pack, with no flag conflict; the version stays out of the repository."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1577
    stage: execution
    question: "Row 16's pair build stopped at the licence list: 'lazy-val 1.0.5: no licence file and no npm-lazy-val.txt'. lazy-val was already in the lock as a development package (electron-builder's); electron-updater makes it, and ten others, production packages, so tools/generate_third_party_licenses.py now lists it, and row 13's licence-check.py looked only at added entries. The package declares MIT (on the plan's list) and neither it nor its repository (develar/lazy-val, no LICENSE at master, read 2026-11-27) ships a licence text. Is this S7, or is it fixed?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Fixed, not S7: S7 names a licence outside the list, a foreign package or a changed version, and none applies. A reviewed override packaging/licence-overrides/npm-lazy-val.txt (LF, the four header fields of npm-type-fest.txt; Source https://registry.npmjs.org/lazy-val/1.0.5, whose license is MIT and author Vladimir Krivosheev) carries the standard MIT text with the declared author. The path joins the scope as new (baseline-scope.json 'absent', true at row 0; eol-check.py 'NEW'), so row 16's new snapshot carries it. licence-check.py also lists packages whose dev flag dropped and requires a licence file or an override for each (two selftest cases); the licence list stays the rule for added packages, and a promoted package outside it is printed as a note: argparse 2.0.1 (Python-2.0, the PSF licence, a licence file present) is the one. Row 16's first receipts are kept as -r1 and the row reruns from a new snapshot."
    source_tag: Local Canon
    precedents:
      - "packaging/licence-overrides/npm-type-fest.txt: an npm package that ships no licence file"
      - "tools/generate_third_party_licenses.py _npm_block: a licence file or packaging/licence-overrides/npm-NAME.txt"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Without the file Mat's own release build stops at the same step. The copyright line comes from the package's declared author, not from an upstream text, and argparse's Python-2.0 licence is newly shipped: both are named in the handoff for Mat to confirm."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1578
    stage: execution
    question: "Row 17's host run r20261127T235735Z-692eb6f passed the main stage (tests=266 expected=266 unexpected=0) but ended install-failures exit=41: AC-174.19 failed at update-roundtrip.test.ts:120, 'page.waitForLoadState: Timeout 30000ms exceeded', with Playwright's log showing only '\"networkidle\" event fired', and AC-174.20 was skipped by the serial block. The host released the lock and the install stage's 'also' list is empty (no snapshot difference, no quarantine). Is this S10's stop, or a spec fix and a rerun?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "A spec fix in the spec's own row, not S10's report-before-rerun: S10's stop before a further payload run covers a snapshot difference or a quarantine, and the host's 'released:' line is its one release. mainWindowShows no longer calls page.waitForLoadState('domcontentloaded'). Playwright attached to the first window after its DOMContentLoaded (it recorded networkidle and never domcontentloaded), and no test of the main suite waits on that state. The two checks that follow it stay as they are: #root visible within 120 s and at least one child. So the window is still proven to show, by the same bound. No skip, retry or longer timeout. Scope: the fix changes only the spec's mechanics, never what an AC asserts. AC-174.19 still requires the old app's main window to show (#root visible, at least one child), and every later step of the round trip is unchanged; the line removed was a wait, not an assertion of the AC. Row 17's receipts are kept as -r1 and row 16's as -r2; a new snapshot is taken (the spec is a scope file), and rows 16 and 17 run again."
    source_tag: Local Canon
    precedents:
      - "task.md row 17: a failing test is fixed in the product or the spec's own row, never by a skip, a retry or a longer timeout; a rerun needs a new snapshot when a scope file changed"
      - "ui/tests/e2e/*.test.ts: firstWindow() then locator checks, with no waitForLoadState"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The wait proves nothing that the #root checks do not prove, and it depends on when Playwright attaches to the window. Row 7's canary passed it once, which shows that it depends on timing, not that it is sound."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1579
    stage: execution
    question: "Row 17's second host run r20261128T003726Z-2a01a7d again passed the main stage (tests=266 expected=266 unexpected=0) and ended install-failures exit=41. After D-1578 the round trip reached step 3 (the window, the backend, the MCP server and app.update_interval = monthly all passed) and failed at update-roundtrip.test.ts:431, 'locator.check: Clicking the checkbox did not change its state', on start-at-sign-in-checkbox. The host released the lock, and 'also' is empty. Is this a fix in the spec, or the product?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "A spec fix. StartAtSignInControl.tsx renders a controlled checkbox, checked bound to state.enabled: React keeps it unchecked until loginItemSet answers. Playwright's check() tests the state right after its click, and refuses when it has not changed, although the click went through. The spec now asserts the box is unchecked, clicks it, and waits for toBeChecked within 30 s. It then waits, as before, for the Run value in the registry. The control is unchanged, and the main suite's Startup tests pass against it. No skip, retry or longer timeout on the failing call. Scope: the fix changes only the spec's mechanics, never what an AC asserts. AC-174.19 still requires Start at sign-in to be turned on through the Settings control and the Run value to exist before the update and after it. The added not.toBeChecked is a precondition of the click, and toBeChecked is the control's answer that check() itself waited for. Bound (coordinator, 2026-11-27): the plan sets no count of row 17 reruns, and S9 names host refusals, not spec failures; r3 is therefore the last host run of this session. If r3 does not pass, no fourth spec fix is made: row 17 is marked [B] with a B-17 block naming the three runs, and rows 18 and H1 continue, with MEU-174 not complete. I read the rest of the round trip against the product before this rerun: the checksum text 'Could not check for updates (checksum)' (UpdatesCard.tsx:56, app-updater.ts:106), 'Version x is ready to install' (UpdatesCard.tsx:54), and no other check() or uncheck(). Row 17's receipts are kept as -r2 and row 16's as -r3, a new snapshot is taken, and rows 16 and 17 run again."
    source_tag: Local Canon
    precedents:
      - "D-1578: the spec's own row fixes a spec defect the host run exposed"
      - "ui/src/renderer/src/features/settings/StartAtSignInControl.tsx:95-103: checked bound to state.enabled, onChange calls apply()"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The product behaves as designed, because the box shows the operating system's answer and not the click. The test now waits for that answer."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1580
    stage: execution
    question: "Row 17's third host run r20261128T011909Z-c447a4d (snapshot c447a4d, row 16 r4 pair-ok) passed the main stage (tests=266 expected=266 unexpected=0) and AC-174.15 and AC-174.16, and ended install-failures exit=41: AC-174.19 failed at update-roundtrip.test.ts:435, 'expect(locator).toBeChecked() failed ... Received: unchecked ... Timeout: 30000ms', and AC-174.20 was skipped by serial mode. The host released the lock, and 'also' is empty. The coordinator set r3 as the last host run. What happens to row 17 and to the rows that depend on it?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Row 17 is [B] with a B-17 block naming the three runs (r20261127T235735Z-692eb6f, r20261128T003726Z-2a01a7d, r20261128T011909Z-c447a4d), each exit=41, and their failure lines. No fourth spec fix and no fourth host run. Rows 7 and 16 stay [x]: row 7's Red run and row 16's installer pair passed their own validations. MEU-174 is not complete and its status stays as it was (H1-3). Row 18 follows the plan's [B] rule ('the issue stays open and only MEU-173 moves'): issue-resolve.py, issue_triage.py render and row-check.py register are not run, APP-NO-IN-APP-UPDATE stays open, only MEU-173 goes to ready_for_review, and row-check.py status checks MEU-173 alone. The canon texts say MEU-173 is delivered and MEU-174's code is built but its installed round trip is blocked (B-17) and Mat decides; the 07 Goal, the Auto-update row and the README describe the in-app update as planned, not shipped. H1-2's gate runs remote-run-2 as written; when it fails and task.md carries a B-17 block, the gate prints 'remote-run-2 blocked reason=B-17', still runs identity-after, and exits 3 with 'session-gate: every step exit 0 except remote-run-2, blocked by B-17 (D-1580)'. H1-2 is then [B] with a B-H1-2 block; no check is skipped or loosened, and every other step must exit 0. H1-3 checks status for MEU-173 alone."
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md S9: mark the round-trip rows [B]; finish the dev-PC rows; MEU-174 is not complete; Mat decides"
      - "task.md row 18: 'If rows 7, 16 and 17 are [B], the issue stays open and only MEU-173 moves'; H1-3: 'MEU-174 stays as it was'"
      - "D-1578 and D-1579: the two spec fixes, mechanics only"
      - "Coordinator, 2026-11-28: 'If the cap is reached, mark the row [B] with its block, and carry on through row 18 and H1.'"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The plan names no count of row 17 reruns, so the coordinator's bound applies, and the plan's own [B] consequences are the closest rule: an open issue is not marked resolved without a green round trip. The r3 failure is in the product or the host, not the spec's mechanics: after the click, loginItemSet answered enabled:false. login-item.ts:120-133 reports false when openAtLogin is false or executableWillLaunchAtLogin is false, which on mini-air may come from a StartupApproved 'disabled' value or the installed path. That is not diagnosed here, because a diagnosis needs another host run. It is the lead for Mat."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1581
    stage: execution
    question: "Row 18's first run (receipt aau-row18-cell-r1.txt) failed at row-check.py canon: 'docs/BUILD_PLAN.md is not its before bytes with the edits'. The row's own meu_status.py render rewrote BUILD_PLAN.md:51, the phase 7 row, from phase 7's note in .agent/context/meu-status.yaml, and :68, the Total row. So :51 is a generated line, and the row's text cannot be written there by canon-edit.py. Where does the text go?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Into the source of the generated line. The text 'Session 106 delivered MEU-173 and built MEU-174, whose installed round trip is blocked (B-17, Mat decides); the first feed release is Mat's.' is appended to phase 7's note in meu-status.yaml (one exact-once byte replacement, LF kept), and the BUILD_PLAN.md pair is removed from canon-edit.py's EDITS. meu_status.py render then writes it to BUILD_PLAN.md:51, and render --check passes. row-check.py canon checks the other three files (07, 06, README). The rest of row 18's cell is as D-1580 adapted it, and it passed on the second run."
    source_tag: Local Canon
    precedents:
      - "task.md row 18: 'Never hand-edit a generated file.'"
      - "tools/meu_status.py render: BUILD_PLAN.md's phase table is a rendered region from meu-status.yaml"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The plan's two instructions conflict for :51; following 'never hand-edit a generated file' keeps the render and the check consistent, and the line still says what row 18 wants it to say."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1582
    stage: execution
    question: "The H1-2 gate's third run (receipts -r3) failed at py-tests: tests/e2e/test_api_capture_shapes.py::test_ac_106_5_openapi_snapshot_and_delta ('1 failed, 218 passed'). Session 72's docs/execution/plans/2026-11-14-capture-shapes-steps/openapi-delta.py pins the whole OpenAPI document against 5db3623 and refused 'a change AC-106.5 doesn't name: /components/schemas/SettingsPutIn/properties/update_interval: only in the new document'. AC-174.10 requires that leaf. How does the gate pass?"
    resolution: autonomous
    class: two-way
    mandatory: [M-7, M-8]
    chosen: "A, as D-1600 did for Session 104's cookie shapes: a narrow exemption in that script (UPDATE_INTERVAL). SettingsPutIn.update_interval must be absent or exactly the committed shape (anyOf string/null, title 'Update Interval'), not in the base and not required; it is removed before the compare, so every other change to SettingsPutIn or the document is still refused. Two selftest cases: Session 106's shape passes, the shape with an added default is refused (13 cases, 0 wrong). The script then prints 'openapi-delta: pass'; the test file passes 13 of 13. What AC-106.5 asserts about the capture shapes is unchanged; only the set-back list grows. The path joins this plan's scope: a row in §Files Modified, eol-check.py PRODUCT as LF, baseline-scope.json with the HEAD blob's SHA-256 (39549c7a..., the file unchanged since 2026-11-27 and so its row-0 state), and its row-0 copy under R/baseline-copies taken from that unchanged file. My added lines are at most 100 characters; the 17 long lines ruff names are the file's own and not in the gate's py-lint set. The H1-2 gate reruns; run 3's receipts are kept as -r3."
    source_tag: Local Canon
    precedents:
      - "D-1600 (docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md): the same exemption for CookieTestOut and CookieTestOutcome"
      - "docs/execution/plans/2026-11-21-release-rc4/task.md row 7: the release info.version set back to the base's in the same script"
      - "aau-D6-py-tests-r3.txt: '1 failed, 218 passed'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. M-7 (an assertion of another plan changes) is covered by the hand-over, as in D-1600. Options: (A) as chosen; (B) leave the leaf out, which drops AC-174.10; (C) do nothing, which sends the session to review with a failing gate. Two-way: the exemption is one constant and two branches."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1583
    stage: execution
    question: "The coordinator found B-17's root cause, a product bug and not test mechanics. login-item.ts writes the Windows Run value with name LOGIN_ITEM_NAME ('com.avkit.app'), but Electron 42's getLoginItemSettings has no name option (electron.d.ts LoginItemSettingsOptions) and reads openAtLogin from the value named after the current AppUserModelId. av-kit set that id only inside defaultToast (notify-user.ts:50), so at startup it was Electron's default, willLaunchAtSignIn returned false, and in an installed app the start-at-sign-in box never turned checked (update-roundtrip.test.ts:435 in all three runs). The coordinator ruled out a disabled startup entry on mini-air by a read-only query (HKCU Run and StartupApproved\\Run hold only OneDrive and Edge). Fix it in this session?"
    resolution: autonomous
    class: two-way
    mandatory: [M-7]
    chosen: "A, the coordinator's HDP recommendation: fix it in this session, because it blocks AC-174.19. boot() in ui/src/main/index.ts calls the new exported applyAppUserModelId(app) right after the single-instance check, before the login item is read and before any window, tray or toast; on win32 it calls app.setAppUserModelId(LOGIN_ITEM_NAME), the existing constant, which equals electron-builder's appId (the NSIS shortcut's AUMID) and NOTIFY_APP_USER_MODEL_ID. New ui/tests/unit/app-user-model-id.test.ts, Red then Green: Red 'Tests  2 failed | 1 passed (3)' (aau-b17-red.txt: index.ts exports applyAppUserModelId: expected 'undefined' to be 'function'; boot() calls applyAppUserModelId: expected -1), Green with its neighbours 'Tests  79 passed (79)' (aau-b17-green.txt) and the full UI suite 'Tests  1801 passed (1801)' (aau-b17-ui-full.txt); eslint clean; eol-check and pins-scan --check 0 problem(s). The test file joins this plan's scope (baseline-scope.json absent, eol-check NEW, a §Files Modified row). What no AC asserts changes: AC-174.19 and AC-174.20 are as written. D-1579's click-then-wait mechanics stay, because the plain check() cannot be proven to work without another host run, and the click-then-wait form is correct for a controlled checkbox either way. Row 16 is rebuilt from a new snapshot (receipts of the earlier build kept as -r4) and row 17 runs once more (receipts of run 3 kept as aau-row17-r3-*): a verification run for a root-caused product fix, not a retry, for which the coordinator lifted the three-run bound for this one run only. If it passes, row 17 becomes [x], B-17 leaves the blockers (its history stays in D-1578 to D-1580 and here), MEU-174 goes to ready_for_review and APP-NO-IN-APP-UPDATE is resolved per row 18. If it fails, row 17 stays [B] with the new evidence."
    source_tag: Local Canon
    precedents:
      - "ui/node_modules/electron/electron.d.ts, LoginItemSettingsOptions (no name) and Settings.name ('Defaults to the app's AppUserModelId()')"
      - "ui/src/main/notify-user.ts:50, the only setAppUserModelId call before this decision"
      - "D-1580, the block this decision may lift"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'; the coordinator's message gave the recommendation. Options: (A) as chosen; (B) keep row 17 [B] and hand the root cause to Mat, which leaves MEU-174 incomplete for a one-line fix; (C) do nothing. Two-way: one exported function and one call."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1584
    stage: execution
    question: "D-1583's verification run of row 17, r20261128T024018Z-d7983df on snapshot d7983df, passed: 'e2e-remote: ok exit=0', main tests=266 expected=266 unexpected=0, install tests=2 expected=2 unexpected=0, and aau-row17-run-check.txt 'install AC-174.19: passed', 'install AC-174.20: passed', 'run-check: 0 problem(s)'. B-17 and the adaptations D-1580 and D-1581 made for it (row 18 without the issue resolve and MEU-174, the blocked canon wording, the gate's B-17 branch) no longer apply. How do rows 17 and 18 and H1 proceed?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "As the coordinator directed for a pass: row 17 is [x]; the B-17 tag and the '### B-17' block leave task.md (the history of the three failed runs stays in D-1578, D-1579, D-1580 and D-1583, and their receipts stay as aau-row17-r1-*, -r2-*, -r3-*). Row 18 runs in its original form (scratchpad cell-18.ps1, not cell-18a.ps1): the issue is resolved from R/issue-resolve-set.json (verification from aau-feed-real-3.json and aau-row17-run-check.txt, resolution_path 'Fixed in Session 106 on 2026-11-28 ...', users get it with Mat's first feed release), bound to row 0's register hash (unchanged: 6021336853c9...), and MEU-173 and MEU-174 go to ready_for_review. The canon keeps D-1581's placement (BUILD_PLAN.md:51 through phase 7's note in meu-status.yaml) and takes the pass wording: 07's Auto-update row reads 'Delivered in Session 106', the MEU-174 note opens '> **Delivered (Session 106).**' and names the run, the AC-174.19 and AC-174.20 results and D-1583's root cause, the Goal sentence loses 'Once MEU-174 is complete ...', and the phase 7 note says Session 106 delivered MEU-173 and MEU-174. canon-edit.py's EDITS for 07 are re-emitted with the same text, so row-check.py canon still checks the before-copies. The earlier row 18 receipts are kept as -r2. With no '### B-17' block, session-gate.ps1 takes its normal path (remote-run-2 mandatory), and H1-3 checks both MEUs."
    source_tag: Local Canon
    precedents:
      - "the coordinator's message: 'If it passes: set row 17 [x], take B-17 out of the blockers (keep the history in the decisions), restore MEU-174 to ready_for_review and resolve the issue per the plan's row 18.'"
      - "task.md row 18 and H1-3, the original forms"
      - "D-1580 and D-1581, the adaptations this decision ends"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'; the coordinator gave the steps for a pass. Options: (A) as chosen; (B) keep the blocked wording and leave the issue open, which would contradict a passing run. Two-way: text and register edits in the working tree, nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1585
    stage: execution
    question: "The plan's row-check.py remote-run-2 step (run by session-gate.ps1 in H1-2) refused any run whose last line was not 'e2e-remote: green exit=0', but tools/e2e_remote.py ends a passing run 'e2e-remote: ok exit=0' (its REASONS table maps ok to 0; line 1550 sets reason, code = 'ok', 0). So the gate would fail on row 17's passing run r20261128T024018Z-d7983df. It had not reached that step yet; it was still waiting for the PC load to drop. How is the check fixed?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "Fix the plan tool before the gate reaches the step: a small pure function run_reason_ok(reason, code) passes only 'ok' with exit 0, remote_run_2 calls it, and the docstring names 'e2e-remote: ok exit=0'. Three selftest cases were added (ok exit=0 passes; install-failures exit=41 and green exit=0 fail): aau-d1585-selftest.txt 'row-check selftest: 22/22 ok'; aau-d1585-remote-run-2.txt 'remote-run-2: run r20261128T024018Z-d7983df ok exit=0; snapshot d7983dff3e7e', '63 product path(s), 0 changed since the snapshot', 'row-check remote-run-2: 0 problem(s)'; ruff check passes. No AC, product file or run result changes; the gate runs once, unchanged otherwise. This is a tooling-mechanics fix, not a retry for a pass."
    source_tag: Local Canon
    precedents:
      - "tools/e2e_remote.py REASONS and its success line"
      - "task.md H1-2, the session gate's remote-run-2 step"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) fix the checker to the tool's real success word, as chosen; (B) accept both 'green' and 'ok', which keeps a word the tool never prints; (C) let the gate fail and report it, which blocks H1 on a checker typo. Two-way: one plan-script edit in the working tree, nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1586
    stage: execution
    question: "The H1-2 load wait (22:19 to 23:49) reached its 90-minute deadline with the PC load at 11 to 97 percent, and the coordinator directed: run the gate anyway, no second wait; a failure in a file this session touched is a real failure, fix it, don't rerun to get past it. The gate run (receipts now aau-gate-h1-r4.txt, aau-H1-2-cell-r4.txt) failed at py-format: 'canon-edit.py:89:13 File would be reformatted', '1 file would be reformatted, 14 files already formatted'. pass18.py (D-1584) re-emitted canon-edit.py's 07 EDITS with backslash-escaped double quotes where ruff format wants single-quoted strings. How is it fixed?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "A real fault in a session file, fixed at its source: 'ruff format' on canon-edit.py alone (scratchpad fmt_ce.py), which asserts that the EDITS dict is equal before and after (9 pairs) and that LF is kept (281 lines both). aau-d1586-format.txt: '1 file reformatted', 'canon-edit.py: EDITS equal (9 pairs), LF kept, lines 281 -> 281', ruff format --check on the gate's Python set '14 files already formatted', ruff check 'All checks passed!'; aau-d1586-canon.txt 'row-check canon: 0 problem(s)'. Then the gate runs once more, unchanged and without a second load wait, as the coordinator directed."
    source_tag: Local Canon
    precedents:
      - "the coordinator's message: 'If the load wait reaches its deadline, run the H1-2 gate anyway; don't start a second wait.' and 'A failure in a file this session touched is a real failure: fix it, don't rerun to get past it.'"
      - "D-1584, whose pass18.py re-emit introduced the quoting"
      - "D-1438, the load wait"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'; the coordinator gave the rules. Options: (A) format the file and prove the data unchanged, as chosen; (B) hand-edit the two string pairs, the same result with more risk; (C) exclude the file from py-format, which hides the fault. Two-way: one plan-script reformat in the working tree, nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1587
    stage: execution
    question: "Gate run r5 (after D-1586, no second load wait) passed every static step and failed ui-tests: 'Test Files  18 failed | 147 passed (165)', 'Tests  105 failed | 1696 passed (1801)', nearly all 'Error: Test timed out in 5000ms.', Duration 58.70s against 40.02s in the earlier full run. The coordinator's rule: rerun alone only the files this session did not touch, then rerun the gate unchanged; a failure in a file this session touched is a real failure, fix it, don't rerun to get past it. 17 failing files are untouched and each passed alone (aau-h12-untouched-iso.txt, 'untouched-iso: worst exit=0'). The 18th, ui/tests/unit/settings-rail.test.tsx, is a session file (it gained the 'updates' row in the AC-58.2 table test); its failing test 'AC-58.2 AC-58.3 activation scrolls and focuses the section ...' is unchanged by the session and passed alone in 122 ms (aau-h12-settings-iso.txt, 'Tests  56 passed (56)'). How does H1-2 proceed?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "Follow the coordinator's rule as written: a failure in a touched file is not rerun to get past it, and its only test-side fix (a raised timeout) would hide it. H1-2 is [B] with reason human-decision and a '### B-H1-2' block in task.md; the gate is not rerun, and H1-3 to H1-6b (each depends on H1-2) do not run. The r4 receipts stay as -r4; r5 stays unsuffixed. The MEU-173 handoff's Deferred Items gain the gate rerun. Recommendation to the coordinator: rerun the gate unchanged when the PC is quiet, because the timed-out test does not test the session's change and passes alone at about 1/40 of its limit."
    source_tag: Local Canon
    precedents:
      - "the coordinator's message: 'If the only failures are timeouts in files this session didn't touch, rerun just those files on their own, then rerun the gate unchanged, as D-1438 did ... A failure in a file this session touched is a real failure: fix it, don't rerun to get past it.'"
      - "task.md Status Legend: [B] for a human-decision gate, with a row-bound block"
      - "D-1438, the load wait"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'; the coordinator's rule binds this case. Options: (A) [B] and report, as chosen; (B) rerun the gate, which the rule forbids for a touched file; (C) raise the test's timeout, which hides the failure and changes a gated input. Two-way: task.md and handoff text in the working tree, nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1588
    stage: execution
    question: "B-H1-2 (D-1587): gate run r5 failed ui-tests with 105 load timeouts; one is in settings-rail.test.tsx, a session file, whose failing test is unchanged and passes alone in 122 ms. The coordinator, who set the touched-file rule, rules on it. How does H1-2 proceed?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "As the coordinator ruled: the touched-file rule meant 'a failure the session's change could cause', and the evidence (an unchanged test, 122 ms alone, failing beside 104 timeouts in 17 untouched files in a 58.7 s loaded run) points to load. The gate reruns unchanged now, with no load wait (load 28 to 74 percent). On a pass, B-H1-2 is lifted and H1-3 to H1-6b continue. On load timeouts only in untouched files with settings-rail passing, D-1438 applies (isolated runs, then one more unchanged gate). If settings-rail times out again it is treated as real: before any further rerun, SettingsPage's render time in that test is measured against the base commit's SettingsPage, and with the Updates card stubbed against a fresh one, and the finding is reported instead of a rerun. No timeout is ever raised. The r5 receipts are kept as -r5."
    source_tag: Local Canon
    precedents:
      - "the coordinator's ruling on B-H1-2: 'rerun the H1-2 gate unchanged. My touched file rule meant a failure the session's change could cause.'"
      - "D-1587, the block this ends; D-1438, the isolated-rerun path"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'; the coordinator owns the rule and ruled. Options: (A) rerun as ruled; (B) keep the block, which the rule's owner has lifted. Two-way: no file changes beyond task.md text; nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1589
    stage: execution
    question: "Gate run r6 (the D-1588 rerun) passed every static step and failed ui-tests: 9 files failed to load and 2 AC-174.21 tests in app-running-nsh.test.ts (a session file) failed; settings-page and settings-mcp-prompt never started. The errors are not timeouts: 'Zone Allocation failed - process out of memory' (node, exit 134), 'runtime: cannot allocate memory' (esbuild), 'spawn UNKNOWN' (errno -4094), and the two AC-174.21 powershell runs returned null and 4294901760. None of the D-1588 branches names this case. How does H1-2 proceed?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "Treat it as a host fault and take the D-1438 path that D-1588 gives for load failures. The cause is the system commit limit: at 00:04 free commit was 4,012 MB of 111,881 MB while 15 GB of RAM was free, because a Zorivest gate candidate (P:/zorivest-wt/.gate-candidates/2026-11-05-rx3-deps-tool-debt, pytest PID 32724 with 24 pytest-xdist workers at about 1.2 GB each) started at 23:57:59 and ran through gate r6, which started at 00:01:40. The session's change cannot cause commit exhaustion. The AC-174.21 failures are powershell spawns that failed under it, and that test leaked no decoys (no PING.EXE ran after it). Those processes belong to another project and were not touched. All 12 files run alone pass, app-running-nsh 3/3 at 3,667 MB free (aau-h12-r6-iso.txt, worst exit 0). Once the Zorivest run had exited (PID 32724 gone, 0 xdist workers, 30,082 MB free), the gate reruns once, unchanged. No timeout is raised. The r6 receipts are kept as -r6. A further failure that is not host-caused, or a settings-rail timeout, follows D-1588."
    source_tag: Local Canon
    precedents:
      - "D-1588, the coordinator's ruling: a failure counts against the session only if the session's change could cause it; load failures take the D-1438 path"
      - "D-1438, isolated runs pass, then one more unchanged gate"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) the D-1438 path after the external run exits, the recommendation; (B) block again, though the cause is outside the session and the isolated runs pass; (C) rerun at once, into a commit limit that was still exhausted. Two-way: receipts only; nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1590
    stage: execution
    question: "Gate run r7 passed identity-before, every static step, ui-tests (165 of 165 files, 1801 of 1801 tests), py-tests, ui-build, mcp-types, mcp-tests and mcp-build, then failed mcp-audit with exit 4: '--mode must be container or authoritative'. The gate's step runs a bare `npm --prefix mcp-server run audit`, the form D-1568 already replaced in row 11's cell. No earlier run reached this step. What does the step run?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Row 11's form (D-1568), fixed at its source in session-gate.ps1: --mode authoritative --baseline ROOT/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json --report RECEIPTS/aau-gate-audit-report.md --out RECEIPTS/audit-gate --agent claude, with no --update-baseline, so the gate stays read-only apart from the receipts (LF kept, 128 to 131 lines; backup in the scratchpad). Run alone, it passes: 'mcp-audit authoritative: 104/104 pass, 0 discovery finding(s), cleanup ok, exit 0' (aau-d1590-audit.txt), and the tracked baseline is unchanged. The four steps no run had reached were also run alone and exit 0: openapi --check, state-render --check, issues-render --check, and row-check remote-run-2 ('63 product path(s), 0 changed since the snapshot'). The r7 receipts are kept as -r7, and the gate reruns unchanged apart from this step. A fix to the plan's tooling before the step's check ran, not a retry."
    source_tag: Local Canon
    precedents:
      - "D-1568, row 11's audit arguments (the skill's authoritative check)"
      - "D-1585 and D-1586, tooling fixes at their source before the gate passed"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) row 11's form, the recommendation, one already decided for the same check; (B) --mode container, a different check from the one row 11 passed; (C) drop the step, which the plan's Verification Plan 5 names. Technical: one argv in a plan script; nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1591
    stage: execution
    question: "Execution review round 1, F1 (High, blocking, AC-174.3 and AC-174.2): electron-updater 6.8.11 sends a persistent installation id. AppUpdater.js:189 makes stagingUserIdPromise a Lazy over getOrCreateStagingUserId (:501-525), which creates and reuses userData/.updaterId, and getUpdateInfoAndProvider (:386-387) sends it as x-user-staging-id on every feed request. The controller left that default in place, against D-1544's recommended no-identifier contract and the README :63 and 07 :9 statements. How does the controller remove it?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "The coordinator's ruling, taken as the recommendation: hardenUpdater() in ui/src/main/app-updater.ts, called first in createAppUpdater, so the controller is the one path that sets it. (a) It replaces stagingUserIdPromise with a lazy getter that resolves to the nil UUID 00000000-0000-0000-0000-000000000000, so getOrCreateStagingUserId never runs and no .updaterId file is written. (b) It wraps computeFinalHeaders to delete x-user-staging-id before the library's own merge, so no request carries the header. One typed function, with a comment that names the library version and the lines. Latest and the SHA-512 check are untouched. A side effect: isStagingMatch (:314-331) reads the nil id as percentage 0, so a staged release with stagingPercentage > 0 always applies; the project publishes no staged releases. Regression test, real library: AC-174.3 F1 in ui/tests/unit/app-updater.test.ts runs two starts of the real NsisUpdater and GitHub provider, each a new updater and controller on one scratch userData, with an in-memory HTTP executor. All 6 requests go to github.com, 2 of them to releases/latest; none carries x-user-staging-id; no .updaterId exists. Red r3 (aau-c1-red.txt) failed by assertion; red-check 0 problems; red-record row c1; Green 66/66 (aau-c1-green.txt). The tests went into the existing in-scope test file because a new file would sit outside baseline-scope.json and §Files Modified, and this workflow may not write the plan."
    source_tag: Local Canon
    precedents:
      - "D-1544, the recommended outbound contract: the update request carries no identifier (plan :675)"
      - "Execution review round 1 F1 (.agent/context/handoffs/2026-11-26-app-auto-update-implementation-critical-review.md)"
    research: { engine: none, sources: ["ui/node_modules/electron-updater/out/AppUpdater.js 6.8.11 :65-66 :189 :201-202 :314-333 :380-392 :501-525"] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'; the coordinator ruled. It keeps D-1544's recommended no-identifier contract, so it changes no M-list item. Options: (A) suppress the id and the header at the updater boundary, the recommendation; (B) disclose and keep the id, which changes D-1544 and needs Mat; (C) a custom HTTP executor, which is a larger reach into the library for the same outcome. Technical: one function and one test block; nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1592
    stage: execution
    question: "Execution review round 1, F2 (Medium, AC-174.5): the library keeps its default console logger (AppUpdater.js:179) and its constructor's error listener (:201-202), which prints the raw error stack. An injected HTTP error gave the controller's one sanitized line plus library log entries that kept the query string and a profile-path marker. How is the library's output silenced?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "The coordinator's ruling: hardenUpdater() sets logger = null, which the setter (:65-66) maps to the library's NoOpLogger. The constructor's error listener, the info lines and the staging-id line (:330, :518) then print nothing, and the controller's sanitized line 'update: check failed kind=KIND' (UPDATE_QUIET_FAILURE) is the only log output. Regression test, real library: AC-174.5 F2 in ui/tests/unit/app-updater.test.ts has the in-memory executor reject with an HttpError message that carries '?probe=QUERYMARK' and a stack frame under C:/Users/PROFILEMARK (Windows separators in the test). The state is error/network, the controller log is exactly ['update: check failed kind=network'], and console.log, info, warn, error and debug record no call. At Red the library logged 3 entries ('Checking for update', 'Generated new staging user ID: …', and the raw error with both markers)."
    source_tag: Local Canon
    precedents:
      - "AC-174.5 UPDATE_QUIET_FAILURE, one sanitized log line per check"
      - "Execution review round 1 F2"
    research: { engine: none, sources: ["ui/node_modules/electron-updater/out/AppUpdater.js 6.8.11 :65-66 :179 :201-202"] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'; the coordinator ruled. Options: (A) the NoOpLogger, the recommendation; (B) a logger that sanitizes and forwards, which adds a second log format to maintain and drifts from AC-174.5's one-line contract; (C) leave it, which keeps the profile-path disclosure. Technical: one assignment; nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1593
    stage: execution
    question: "Gate run r9 (corrections round 1) stopped at line-endings: eol-check.py found 158 CR bytes in .agent/context/handoffs/2026-11-26-app-auto-update-implementation-critical-review.md, a file new since row 0, which the plan's line-ending rule says must be LF. The coordinator copied the reviewer's CRLF report there after gate run r8. Which side changes?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "The canonical copy takes LF: every CRLF becomes LF and no other byte changes (158 line ends; the LF bytes turned back to CRLF equal the report, sha256 20f58f37bc82c3af58edabe98dc9af10cbfc47cdea01c42e5ba710b9919a48d8). The reviewer's report C:/Temp/av-kit/aau-exec-review-round-1.md stays as written. The rule in eol-check.py is unchanged. The review-state receipt's digest is of the old bytes; the Corrections Applied section changes the file in any case, so the coordinator rebuilds the --review-state-only receipt at the canonical path. The gate reruns in full as run r10; run r9's receipts are kept as -r9."
    source_tag: Local Canon
    precedents:
      - "eol-check.py: a new file (absent at row 0) must have no CR"
      - "The plan review handoff, 2026-11-26-app-auto-update-plan-critical-review.md, is LF"
    research: { engine: none, sources: ["docs/execution/plans/2026-11-26-app-auto-update/eol-check.py :18 :228", "C:/Temp/av-kit/2026-11-26-app-auto-update/aau-D6-line-endings-r9.txt"] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) LF for the canonical copy, the recommendation, since the plan's own rule and the earlier review handoff both use LF and the text stays the same; (B) let eol-check.py accept CRLF in review handoffs, which loosens a gate check during corrections; (C) leave it, which keeps the gate failing. Two-way: line ends only; nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1594
    stage: execution
    question: "Gate run r10 (corrections round 1) stopped at mcp-audit, 93/104: capture.capture returned internal_error, and 10 capture steps were blocked behind it. A probe rerun of only the audit gave the same result. Calling CaptureService.capture_fullscreen directly with an isolated app-data and inbox raised CaptureFailedError('captured frame is black') from adapter.py _reject_black_or_empty. Both mss monitors read all-zero pixels, and Win32_DesktopMonitor reports Availability 8 (off line). The input desktop is Default, the console session is Active, no LogonUI or LockApp is running, and the last input was seconds ago. Neither ES_DISPLAY_REQUIRED, a 1 px mouse input, nor SC_MONITORPOWER on brought a frame back. Since gate run r8 (104/104 at 00:33), the only source file that changed is ui/src/main/app-updater.ts, which the Python capture path never reaches. Rerun, excuse the step, or stop?"
    resolution: autonomous
    class: technical
    mandatory: []
    chosen: "Stop and report it as blocked by the environment. The dev PC's display is powered off, so every screen grab is black, and the session's change cannot cause that (D-1588). Nothing is excused, and the audit's census and the capture adapter are unchanged. When the display shows the desktop again (a non-black mss grab of monitors[0]), the gate reruns once, in full and unchanged, as run r11, following the D-1589 precedent, after the r10 receipts are kept as -r10. Until then the handoff updates, the Corrections Applied section and the round-2 prompt wait, because each one cites the gate of record."
    source_tag: Local Canon
    precedents:
      - "D-1588: a failure counts against the session only if the session's change could cause it"
      - "D-1589: rerun once the environment cause has ended"
      - "Coordinator, corrections round 1: if a run fails, stop and report; never rerun to get a pass"
    research: { engine: none, sources: ["C:/Temp/av-kit/2026-11-26-app-auto-update/aau-D6-mcp-audit.txt", "C:/Temp/av-kit/2026-11-26-app-auto-update/exec-probe/audit-probe/actions.jsonl :90", "C:/Temp/av-kit/2026-11-26-app-auto-update/aau-c1-capture-probe.txt", "packages/infrastructure/src/avkit_infra/capture/adapter.py :907 :940"] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) stop and report, the recommendation, because the cause is physical and outside the session; (B) rerun now, which would fail the same way and turn into rerunning for a pass; (C) excuse capture.capture, which breaks the gate's nothing-excused rule and needs an audit change outside scope. Two-way: nothing committed."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
  - id: D-1595
    stage: execution
    question: H2-5 names two commit messages, one per MEU. Can the session's paths be split into two commits that each build and pass their own tests?
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "A: one commit of every Session 106 path with one message whose subject names MEU-173 and MEU-174; the draft keeps the plan's two messages as the alternative. B: two commits, which needs a partial staging of ui/package.json and ui/electron-builder.yml. C: do nothing and leave only the two messages, with no path split."
    source_tag: Local Canon
    precedents:
      - "ui/package.json holds MEU-173's --publish never and MEU-174's electron-updater pin; tests/unit/test_update_feed_config.py reads ui/electron-builder.yml, whose feed block and installer lines both changed"
      - "Commits 5e4ec2f and e5028a3: one commit for a multi-MEU session"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A keeps every commit buildable, as Sessions 103 and 104 did. B splits lines inside two files, and a MEU-173-only commit would lack the dependency its tests do not need but the lock file records. C leaves the coordinator to find the split. Weakness of A: one commit carries two MEUs. Two-way: the coordinator can still use the two messages."
    human_message_reference: "Mat, USER_EXPLICIT 2026-11-18, 'make the decisions always the recommenations'"
open_decisions:
  - id: D-1543
    stage: planning
    question: Is SHA-512 from the feed over HTTPS, with no publisher signature, enough trust for an update that installs on one click?
    resolution: open
    class: one-way-door
    mandatory: [M-4]
    recommendation: "A: ship it, and say so in the release notes, the README and the Settings card."
    reasoning: "Mat's to make. Once a release carries the updater, every installed copy trusts whatever the repository's release assets hold; that cannot be taken back from installed copies, and the statement goes into public documents."
    human_message_reference: null
  - id: D-1544
    stage: planning
    question: The app starts to contact github.com by itself. How do the works-offline and privacy statements change?
    resolution: open
    class: one-way-door
    mandatory: [M-4, M-12]
    recommendation: "A: name the request in 07 §Goal, the README and the release notes, with Never as the switch."
    reasoning: "Mat's to make. The statements are public, and the request tells GitHub that an av-kit install exists at an address."
    human_message_reference: null
```

### D-1540: Which releases does the app offer?

**I recommend A: the release you mark Latest on GitHub.** Today that is each release candidate; later it is the stable version. A release you flag as pre-release is never offered, so you can hold one back.

- B: stable versions only. Release-candidate users would get nothing until 0.1.0.
- C: keep things as they are: set nothing and take the library's default. On a release-candidate build that follows only `rc` tags, so those users would never be offered the stable 0.1.0.

Refs: D-1409, R3.

### D-1541: The default interval, and an off choice

**I recommend A: once a week by default, with Never as a third choice.** Never is my addition; you named two intervals.

- B: once a month by default, with Never.
- C: keep things as they are: only the two intervals you named, weekly by default, and no way to stop the check.

Refs: D-1409, D-1544.

### D-1542: What "automatically" means

**I recommend A: the app checks and downloads by itself, tells the user once, and installs when the user clicks Restart and update.** The download is about 450 MB and starts without a question. The app never restarts by itself.

- B: also install when the user quits the app. Fewer clicks, but the app seldom quits (close-to-tray), and a Windows shutdown during that install can leave the app unusable (R4).
- C: restart by itself when the update is ready. It could end a running job; the app cannot tell whether one runs.
- D: keep things as they are, as far as your request allows: nothing downloads until the user asks (Zorivest's U-1). No updater at all is ruled out by your words in D-1409.

Refs: D-1409, D-1549, R4.

### D-1543: Trust for an unsigned update (open, yours)

**I recommend A: ship with the SHA-512 check over HTTPS and say plainly what it is.** The release notes, the README and the Settings card state that updates come from the repository's releases, are checked against the release's SHA-512, and are not signed. Whoever controls the release assets controls what installs. Your GitHub account is then the thing to protect.

- B: download the update but hand the installer to the user to run, as today's manual install does. It keeps the user's own look at the Windows warning and removes the one-click install you asked for.
- C: keep things as they are: no in-app install until the installer is signed. That needs a certificate, which 07 leaves out.

M-4: installed copies cannot be recalled, and the statement is public. If you choose B, rows 12 to 17 change: `install()` opens the downloaded file's folder, and the round trip ends at the download. Refs: 07 Trust row, R3, R6.

### D-1544: The new request to GitHub (open, yours)

**I recommend A: name it.** 07 `:9` and the README say that, besides YouTube and Hugging Face, the packaged app asks `github.com` for the newest release on the schedule in Settings, at each start while a found update waits, and when the user clicks Check now; that the request carries no identifier, only what any HTTPS request shows (the address and a user agent); and that Never stops the scheduled request. The first feed release's notes say the same.

- B: make Never the default, so the app contacts GitHub only after the user opts in. The offline statement then stays true out of the box, and most users never get an update.
- C: keep things as they are: change no statement. The statements would be untrue from the first feed release, so the true do-nothing is to hold the updater: no release carries it until you rule, and the statements stay true.

M-4 and M-12. If you choose B, `UPDATE_INTERVAL_LEAF`'s default and AC-174.9 change. Refs: 07 Outbound row, D-1541.

### D-1545: One session or two

**I recommend A: one session, MEU-173 first with its own handoff.**

- B: split MEU-173 into its own session, as the grouping's rule says for a plan over half a context. It moves 3 of 20 rows and adds a second plan, review and closeout.
- C: keep things as they are: the grouping's one session with the split flag. That is A.

Refs: grouping Session 106.

### D-1546: MCP

**I recommend A: the setting only, in the existing settings tool.**

- B: add an action that checks or installs. A new tool shape, and an assistant could restart the app.
- C: keep things as they are: MCP does not know the setting. The home's Setting surface row rules that out.

Refs: 07 Setting surface row.

### D-1547: Where the status lives

**I recommend A: a new Updates section in Settings, in the App group after Startup.**

- B: put the interval under Console & logging and show no status.
- C: keep things as they are: no status anywhere; the user learns of an update only from the notice.

Refs: D-1548, D-1549.

### D-1548: A check on request

**I recommend A: a Check now button in the Updates section.** You asked only for the schedule; this is my addition.

- B: put the check in the tray menu instead.
- C: keep things as they are: no check on request; only the schedule. Then `update-check`, `settings-update-check`, AC-174.8's check part and AC-174.16's first half are removed, and the round trip waits for the first tick with a second feed folder instead of a click.

Refs: 07 Check row.

### D-1549: Running jobs at the restart click

**I recommend A: a sentence beside the button says that running jobs stop.**

- B: count the running jobs and ask again when there are any. It needs a new backend route, because speech jobs cannot be listed today.
- C: keep things as they are: no words about jobs.

Refs: 07 Install row.

### D-1550: The schedule state and its numbers

**I recommend A: a small state file of the main process; 7 and 30 days; an hourly look; a day between failed tries.** A found update that waits is checked again once at each start, so **Restart and update** comes back after a restart, and the app never guesses the interval when it cannot read it: it skips that look.

- B: keep the time of the last check as a backend setting. It would show in the settings API and the MCP schema as if it were a user setting.
- C: keep things as they are: no stored state, so the app would check at every start and the interval would mean nothing.

Refs: D-1541.

### D-1551: The test seam

**I recommend A: a seam that only an E2E launch can switch on.**

- B: test the card with a mocked bridge only; no E2E reaches a feed. The home's Tests row asks for one.
- C: keep things as they are: no seam. That is B.

Refs: 07 Tests row.

### D-1552: Where the real update runs

**I recommend A: on the mini-air host, as a new install stage of the remote E2E tool, with a canary run first.**

- B: on the dev PC. Refused without you: the updated app starts on your real app data.
- C: keep things as they are: the tool installs nothing, so no real update is ever run. The home's Tests row asks for one.

Refs: grouping D-1411, D-1216.

### D-1553: The updater cache at uninstall

**I recommend A: the uninstaller removes the cache folder with its content, and an update keeps Start at sign-in.** Today the two lines that remove the sign-in entry run before the update guard, so every update would turn it off.

- B: remove only the files the app can name, and leave the rest.
- C: keep things as they are: the folder, with a 450 MB installer in it, stays after an uninstall, and each update turns Start at sign-in off.

Refs: MEU-114, MEU-61.

### D-1554: Which processes the installer stops

**I recommend A: only the processes whose file is inside the folder being replaced, and a refusal when that cannot be checked.** The installer and the uninstaller then never touch an av-kit started from another folder. When the check cannot run, the installer says the app cannot be closed and changes nothing; the old version stays, and at its next start the app offers Restart and update again.

- B: keep things as they are: the stock check. It stops any process whose path begins with the folder's text (a sibling `av-kit-old` folder included) and, without PowerShell, every `av-kit.exe` of the account by name.
- C: the bounded check, with the stock stop by name when PowerShell is unavailable. Updates then go on where PowerShell is blocked, and the stop by name comes back there.

M-5: a user whose PowerShell is blocked sees a refusal instead of a stop of every av-kit. Refs: R7, AC-174.21.

## Research References

Read on 2026-11-26. The three "not verified" items of the Spec Sufficiency Table have no source here on purpose.

| ID | Source | What it gave |
|---|---|---|
| R1 | `https://registry.npmjs.org/electron-updater` and `https://registry.npmjs.org/electron-builder` | dist-tags: electron-updater `latest` 6.8.11 (2026-10-20), `v26` 6.8.12, `next` 7.0.0-alpha.14; MIT; its eight dependencies. electron-builder `latest` 26.18.0. The 6.8.12 code was not read |
| R2 | `https://www.electron.build/v26/docs/features/auto-update/` | The `publish` block, `latest.yml` and the blockmap, `app-update.yml`, the generic provider, "Do not call setFeedURL". `electron.build/auto-update`, which the homes cite, answered 404 |
| R3 | The library source at tag `electron-updater@6.8.11` (`github.com/electron-userland/electron-builder`, `packages/electron-updater/src`: `providers/GitHubProvider.ts`, `AppUpdater.ts`, `NsisUpdater.ts`, `providers/GenericProvider.ts`) | The github.com URLs; `allowPrerelease` default and effect; `autoDownload`, `autoInstallOnAppQuit` defaults; `quitAndInstall(isSilent, isForceRunAfter)`; the SHA-512 check and `ERR_CHECKSUM_MISMATCH`; the signature check skipped without a publisher name; `forceDevUpdateConfig`; a generic feed over plain `http://127.0.0.1` |
| R4 | `github.com/electron-userland/electron-builder/issues/7807` | A shutdown during an install at quit leaves the app unusable; fixed in 27.0.0-alpha.6 only |
| R5 | `github.com/electron-userland/electron-builder/issues/7976` | The ESM named import fails; use the default import |
| R6 | `github.com/electron-userland/electron-builder/pull/9877` and `/pull/10214` | Signed manifests are in the 27 line; the 26 backport was closed unmerged |
| R7 | `ui/node_modules/app-builder-lib/templates/nsis/` (26.18.0, read locally): `common.nsh:123-131`, `installSection.nsh:33`, `:36`, `:85-108`, `include/allowOnlyOneInstallerInstance.nsh:5-8`, `:32-43`, `:66-99`, `uninstaller.nsh:1-3`, `:254`, `multiUser.nsh:8`; and `ui/node_modules/app-builder-lib/out/targets/nsis/NsisTarget.js:49`, `:261`, `:393`, `:408`, `:463`, `:709-712` | The `--updated` start argument, the forced start after a silent update; the stock running-app check, its unbounded match and its stop by image name; the `customCheckAppRunning` hook and where the custom include lands; the installer key `Software\${APP_GUID}` and how the GUID is derived |
| R8 | `P:/zorivest/docs/build-plan/18-first-install-ux.md` §18.12 (MEU-504, last change `25314aaae`, 2026-10-23, the U-1 ruling) | Design input only: update on the Restart and update click. Nothing later was decided there; MEU-504 is still pending. It differs here in one point: Zorivest downloads on the user's request, av-kit downloads by itself (Mat's "automaticly") |

## Planning receipts

- `C:/Temp/av-kit/2026-11-26-plans/s106/plan-host-facts.txt`: the host probe that timed out.
- `C:/Temp/av-kit/2026-11-26-plans/s106/precedent-sweep.txt`: the precedent sweep.
- `C:/Temp/av-kit/2026-11-26-plans/s106/task-lint-r3.txt` (after the round-2 corrections; the earlier runs are `task-lint.txt` and `task-lint-r2.txt`): `tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task task.md` (the form in `.agent/docs/commands.md:221`), run with `RECEIPTS_DIR=C:/Temp/av-kit` in the environment (the lint reads the receipts root from there): exit 0, `OK: 38 row(s)`, 36 rows fully checked and 2 exempt as `view_file` (H1-5, H2-1).
- **Step 4A (GUI standards):** `gui-refs-not-shipped`. `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent, so no index row is added. The emerging standards were checked for the three new controls: G30 (the select reuses the Settings select that `log_level` uses), G31 and G32 (no new accent; tokens only), G33 (no new motion), G34 (existing button variants), G35 (the select uses the Settings autosave chain; Check now answers through the status line; Restart and update closes the app), G15 (a refused `PUT` uses the Settings error path), G26 (no help entry in this session, see §Out of Scope), G8 (row 9), E2 (each new control has an E2E assertion: AC-174.15 and AC-174.16).
- **Workflow steps not run:** Step 5 (the plan review dispatch) is the orchestrator's. No reviewer was dispatched and no self-review is offered as an approval.

## Validation stage contract

- **Unit and static (dev PC):** rows 1, 2, 2a, 2b, 4, 5, 8 to 15. Each Red is recorded before its Green.
- **Real build (dev PC):** rows 3 and 16.
- **Electron and the installed app (mini-air host):** rows 7 and 17, each bound to a snapshot commit and a run id.
- **Session gate:** H1-2. **Independent review:** H1-7, never authored by the implementer.
- A row is done only when its Validation cell exits 0 and its receipt is under `C:/Temp/av-kit/2026-11-26-app-auto-update/`. A blocked row is `[B]` with its receipt and the stop id.

Proposed commit subjects (no AI attribution trailer; Mat commits or directs it): `feat(dist): write the update feed files and check them before upload (MEU-173)` and `feat(app): check for a newer release on a schedule and install it from Settings (MEU-174)`.
