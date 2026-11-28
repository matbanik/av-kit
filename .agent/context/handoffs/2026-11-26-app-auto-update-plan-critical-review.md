---
date: "2026-11-27"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "aau-plan-2026-11-26-app-auto-update"
round: 3
---

# Critical Review: 2026-11-26-app-auto-update

> **Review Mode:** plan
> **Verdict:** changes_required

## Scope

Session 106, MEU-173 and MEU-174: both working-tree plan files, the named product/test/tooling surfaces, distribution homes, grouping Session 106/ownership/decision rows, and APP-NO-IN-APP-UPDATE. Applied PR-1 to PR-9 and Q1 to Q8. Codex is the independent reviewer, class `avkit_independent_reviewer`; Claude Code/Anthropic authored the plan.

HEAD is `c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4`, branch `main`. No repository file was edited. Only temporary report/probe/receipt files were written. No pytest, Vitest, npm, uv, builder, Electron, network or SSH command ran. Only the three specified plan-time receipts were opened. Forbidden files were not opened; the host-ignore exception is excluded from identity. Other session plans and the mockup were not reviewed. Completion-preflight was read and applied to this review deliverable; it does not authorize executing the plan's unchecked tasks.

The supplied grouping/triage decisions and exclusions stand. Open D-1543/D-1544 and D-1413 are not findings. Approval would establish plan fitness only; execution still requires Mat's authorization.

## Intent Anchor

an installed av-kit learns of a newer release by itself and installs it without a visit to the release page. On the schedule the user picks in Settings (once a week, the default; once a month; or never), the packaged app asks the public repository's releases for the version GitHub marks Latest. If it is newer, the app downloads the installer in the background, checks it against the feed's SHA-512, tells the user once, and shows **Restart and update** in Settings. One click there stops the backend in the app's own order, runs the installer silently and starts the new version. The app never restarts by itself. A release build writes the two feed files beside the installer, a script checks them against the built installer, and the upload stays Mat's step. Unit tests, an Electron E2E against a local feed, and a real update from one built version to the next on the mini-air host prove it, with no manual check.

Intent achieved: **partial**, at the plan-specification level. The proposed architecture covers the goal, but four concrete contradictions prevent safe execution as written.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | UPDATE_TICK turns a rejected settings read into weekly. A user who saved never, with no previous successful check, will therefore contact the feed and automatically download an update when the local settings request fails. AC-174.1/.2 and D-1541/D-1544 promise that Never stops scheduled requests; the pure-function never test does not exercise this controller fallback. Confidence: High. Violates: AC-174. | docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:159; docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:233; docs/execution/plans/2026-11-26-app-auto-update/task.md:63 | On an unavailable or invalid interval, skip the scheduled check and retry reading settings later; do not invent weekly. Add a controller test with saved never and a rejected settings request, asserting zero updater calls. | open |
| F2 | High | yes | behavior | INSTALL_STAGE_RULES refuses existing folders and uninstall entries, but permits pre-existing com.avkit.app Run/StartupApproved values and av-kit shortcuts. The real uninstaller deletes the two registry values unconditionally, and installation can overwrite shortcuts. A final unequal snapshot detects the loss only after modifying state this run did not create. This violates AC-174.18/.20 and the promise to leave the E2E account as found. Confidence: High. Violates: AC-174. | docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:169; docs/execution/plans/2026-11-26-app-auto-update/task.md:53; ui/build/installer.nsh:2 | Before installation, refuse every pre-existing registry value/shortcut the installer or uninstaller can modify, or explicitly preserve and restore it. Add a negative fixture with absent folders/uninstall entries but an existing Run value and shortcut; it must cause zero installer calls and zero mutations. | open |
| F3 | High | yes | behavior | UNINSTALL_CACHE_RECURSIVE cannot pass the required existing test suite within the named assertion changes. Row 13 authorizes the fixture at line 105 and regex at 112, but login-item-nsh.test.ts:119 still expects the exact non-recursive RMDir string and :125 expects zero recursive removals. The prescribed /r edit necessarily fails both; PIN_GROWTH and S5 prohibit silently changing them. AC-174.14 therefore stops at Green despite a correct macro. Confidence: High. Violates: AC-174. | docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:196; docs/execution/plans/2026-11-26-app-auto-update/task.md:63; ui/tests/unit/login-item-nsh.test.ts:119; ui/tests/unit/login-item-nsh.test.ts:125 | Name both additional assertions and their exact replacements in row 13: the sole RMDir is the recursive updater-cache line, and the recursive-removal count is one with that exact target and guard. List the complete assertion changes in User Review Required before approval, retaining the two Run-value deletion checks. | open |
| F4 | High | yes | behavior | The plan assumes the stock installer stops only processes under the installation folder, but its CHECK_APP_RUNNING macro falls back to taskkill /IM when PowerShell is unavailable/blocked. A running av-kit.exe elsewhere in the E2E account can then be stopped by the canary or update. Even the PowerShell branch uses a raw StartsWith($INSTDIR), admitting sibling paths with the same prefix. This contradicts INSTALL_STAGE_RULES and AC-174.18/.19; the helper using path-scoped stops does not constrain the installer subprocess. Confidence: High. Violates: AC-174. | docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:36; docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:169; ui/node_modules/app-builder-lib/templates/nsis/include/allowOnlyOneInstallerInstance.nsh:94; ui/node_modules/app-builder-lib/templates/nsis/include/allowOnlyOneInstallerInstance.nsh:99 | Specify a fail-closed, directory-boundary-aware process check for the installer, using the supported customCheckAppRunning hook or another explicit bounded mechanism. Prove that unavailable process-path inspection refuses before installation and that an av-kit.exe at a foreign/sibling path receives no signal; reflect the actual behavior in the trust/process brief. | open |
| F5 | Medium | no | behavior | An update silently disables Start at sign-in. The new installer runs the old uninstaller with --updated, but both DeleteRegValue statements in customUnInstall precede the isUpdated guard. UNINSTALL_CACHE_RECURSIVE says nothing else changes, so these values are still removed during updates. No boot path restores them, and the round trip never enables the login item to detect the regression. Confidence: High. | docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:167; ui/build/installer.nsh:2; ui/node_modules/app-builder-lib/templates/nsis/include/installUtil.nsh:206; ui/node_modules/app-builder-lib/templates/nsis/uninstaller.nsh:157 | Preserve the login-item values during an update while retaining their removal on a true uninstall, and exercise enabled Start at sign-in across the built-version round trip. | open |
| F6 | Medium | no | behavior | UPDATE_SCHEDULE applies the 24-hour attempt throttle even after a successful download. If the user closes the app with an update ready and reopens it one hour later, pendingVersion is persisted but ready/availableVersion is not, and the scheduled recovery check is false until 24 hours after the previous attempt. Restart and update can disappear for the rest of the day, contrary to D-1550's stated recheck at each start while an update waits. Confidence: High. | docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:157; docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:160; docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md:530 | Separate failed-attempt backoff from successful pending-update recovery, or restore ready from a revalidated cached download. Specify a close/reopen-within-24-hours test that restores the install control without issuing another notice. | open |

## Q1 — Goal and proof coverage

Accepted: each goal clause has an AC and execution row; the real install is not delegated to a human check.

| Goal clause | AC | Rows |
|---|---|---|
| Weekly/monthly/never, default and settings surfaces | AC-174.1/.2/.8-.13 | 8-15, 17 |
| GitHub Latest, newer only | AC-174.3; D-1540; FEED_CHECKLIST | 12-13, 1-3 |
| Background download and SHA-512 rejection | AC-174.3-.5/.15/.16/.19 | 12-13, 6-7, 16-17 |
| Once-only notice and Restart and update | AC-174.6/.12/.13/.16 | 12-15, 17 |
| Backend/MCP stop, silent installer, new version starts | AC-174.7/.19 | 12-13, 16-17 |
| No self-restart | AC-174.3/.6/.7/.16 | 12-13, 17 |
| Feed files, real feed check, manual upload | AC-173.1-.5 | 1-3 |
| Real host update and uninstall | AC-174.17-.20 | 4-7, 16-17 |

Not accepted: F1 defeats the off switch; F2/F4 defeat host isolation; F3 blocks the required Green suite. The monthly/weekly elapsed-time behavior and notice deduplication are unit-tested; a short local-feed E2E is an appropriate complement. GitHub's actual Latest selection is tested only through configuration/mocks: the real round trip uses a generic provider. That division is reasonable for offline testing, but it does not independently verify the unavailable GitHubProvider source.

## Q2 — Feed and publishing

Accepted: the current NSIS artifact pattern has no spaces (`ui/electron-builder.yml:18`). Builder `computeSafeArtifactNameIfNeeded` returns null for such a name (`out/platformPackager.js:693-705`), so GitHub-specific safe-name substitution (`out/publish/updateInfoBuilder.js:100-106`) does not rename it. FEED_CHECK compares both feed hash fields, size, version, URL/path and installed feed config; it checks blockmap presence/non-emptiness, not its internal chunk content. The canon's Check row requires installer hash/size comparison (`07-distribution.md:426`), so that distinction is not a blocker.

Installed 26.18.0 generates app-update.yml at `PublishManager.js:87-89`, queues metadata independently of `isPublish` at `:158-163`, and selects `latest` for an unchannelled GitHub config (`updateInfoBuilder.js:36-40`; GitHub resolution `PublishManager.js:485-490`). NSIS builds a blockmap at `NsisTarget.js:415-431`. These support row 3 even before electron-updater is installed. `--publish never` disables the upload branch even with a token; the existing workflow and release scripts carry it, and row 2 closes the unflagged npm dist entrypoint. The repository sweep found no additional effective NSIS upload entrypoint requiring amendment. Historical fixtures and a directory-only pack are not release uploads. AC-173.2's automated census itself covers package scripts/workflows, not every historical script; no concrete uncovered uploader was found.

The three-file manual checklist, retaining the prior blockmap, and one-time manual upgrade from rc.5 are consistent. Semver orders rc.5 below stable 0.1.0; with downgrade disabled, an older Latest is not offered. The claim that allowPrerelease=false uses GitHub Latest rather than a prerelease channel remains dependent on R3, not independently checked here.

## Q3 — Controller, scheduling and stored state

Accepted: the pure formula handles null/future timestamps, exact period boundaries, Never and 24-hour failed-attempt backoff. Ticks start after backend readiness; development runs have neither timers nor checks. Quiet failures and one notice are explicit observable contracts with negative tests.

Not accepted: a read failure becomes weekly (F1); a successfully downloaded pending update is also throttled for 24 hours after restart (F6). These are controller/persistence cases absent from the specified pure schedule assertions. The source-only probe reproduces both formula outcomes.

Malformed-store handling needs care in implementation: installed Conf defaults `clearInvalidConfig` to false (`conf/dist/source/index.js:73`) and rethrows JSON parse failures (`:274-290`). Writes are normally atomic, with an EXDEV direct-write fallback (`:375-382`). The plan explicitly requires unreadable values to become null, so constructor/read failure handling is part of that contract; the wrong-typed memory-store test alone does not prove it. No separate blocker is inferred from an implementation that does not yet exist. Likewise the safe controller log line is sound, but the unavailable updater's own logger must be inspected when installed before claiming all library diagnostics are redacted.

## Q4 — Installation, shutdown and restart

Accepted: set quit intent, await the owned backend shutdown, then call quitAndInstall(true,true) on the user's IPC action serves the goal. `shutdownOwned` signals/waits/retires (`python-manager.ts:70-86`); the current caller owns an immutable pid (`index.ts:268`) and always prevents quit and finally calls app.exit (`:319-345`). Row 13 must implement the promised idempotent ownership clearing and distinguish update quit as necessary while preserving normal quit. The mocked call sequence cannot prove the real handler interaction; the built round trip is the necessary final proof. Without BaseUpdater/NsisUpdater 6.8.11, I cannot establish whether app.exit races installer launch and do not invent that finding.

Not accepted: the stock installer's unconditional path-only claim is false (F4). The update also deletes the login-item values (F5). The fixed running-jobs warning covers downloads, transcripts, speech and conversions; the backend uses its existing stop order and updates preserve the data guard. The installer also closes client-started MCP processes; the process statement must describe the fallback truthfully. No new busy check is required.

The installed NSIS StartApp macro passes --updated through ExecShellAsUser (`common.nsh:123-131`) and forces a silent relaunch (`installSection.nsh:91-108`). The app's single-instance/start-minimized paths show no special --updated rejection. Issue 7807's exact cause/fix and electron-updater's quit semantics could not be checked; disabling install-on-quit is consistent with the chosen click-only policy regardless.

## Q5 — Trust, outbound request and the test seam

Accepted: the trust brief says that SHA-512 does not authenticate the publisher and release-asset control gives installation control. No signing is claimed. The runtime contains SHA-512 digest plumbing (`builder-util-runtime/out/httpExecutor.js:468-470`) and follows redirects; its source does not independently prove a strict HTTPS-only redirect policy. The factual product claim should mean the intended GitHub HTTPS feed and its asset delivery, not a verified universal anti-downgrade transport guarantee. R3's signature-skip and GitHub URL details are unavailable here.

The generic plain-HTTP feed is confined by the build instructions to scratch extracted trees and `s106-out`/`s106-payload`, with no version/config edit in the repository or output in ui/dist. Config read-back, provider-specific feed checks, S6 and Mat's product upload checklist keep these test installers apart. The seam is a runtime environment gate, including in a packaged app; a local launcher can redirect checks/downloads but every seam run records rather than invokes the installer. It adds no demonstrated remote install privilege, especially with the existing RunAsNode capability. Actual roundtrip builds run without the seam and install for real.

README/07/release-note/checklist changes name the request and Never. F1 must be fixed for that public off-switch claim to be true. D-1544's option C (leave false statements) is not a viable shipping choice: its real do-nothing outcome is holding the outbound feature. D-1543's hold-until-signed option is real. This is brief clarification, not an additional blocker.

## Q6 — Settings and test pins

Accepted: the new leaf is allocated consistently to wire set, core registry/default, flat API model, renderer strict schema/card, MCP resource/strict input, OpenAPI and 06 settings table. Existing service runtime validation supplies enum enforcement; new namespace/route changes are unnecessary. Check now with Never is coherent when Never means no scheduled requests, as the public brief says.

I searched ui/tests, tests and mcp-server/tests for settings leaves/sections, channel/preload lists and schema enumerations. The exact IPC census/maps, settings rail list, E2E settings list and MCP resource surfaces are named in Test pins. Other hits include settings test fixtures and the help-content facts list, not an additional exact census that must grow for this leaf. Fixture additions should stay fixture repairs. F3 is the material missed assertion pair in an already-listed file.

Row 13 plus Test pins names 22→25 and the channel additions; rows 11/15 tie schema/section growth to named files. The top User Review Required section does not list these assertion changes, while Test pins does. That placement alone is not a blocker. It must, however, present the complete actual uninstall assertion changes when correcting F3; a general update-tests instruction would not resolve M-7. OpenAPI is regenerated from the then-current working tree after Session 104, preserving that session's changes; row 9 does not install a stale snapshot.

## Q7 — Payload, host installation and round trip

Accepted: optional payloads are flat, bounded by file count/size and bound by names, byte sizes and SHA-256 before host execution. Verification is placed before extract/build/run; no-payload requests retain their prior shape and skip the install stage. The summary intentionally gains an install block, so literal byte identity is promised for the request, not every future summary byte. Failed/skipped install tests cannot yield exit 0. The real old→new pair, wrong-hash negative, expected old version, pid checks, new installed image and persisted setting/marker prevent a preinstalled new version, stale process or unchanged app from satisfying the intended round trip.

Not accepted: pre-existing Run/shortcut state is not protected before mutation (F2), and stock NSIS can escape the image-path restriction (F4). A final equality comparison proves only a completed cleanup. The helper must use teardown on failure, not rely solely on AC-174.20 as a later test in the serial block. On reboot/launcher termination there is no specified durable install recovery; current `host-release.ps1:68-77` only removes the lock. Preserve the run ownership/snapshot and keep the host quarantined until a run-bound cleanup verifies it; never interpret release as account restoration. This operational recovery requirement should be made explicit with the F2 fix.

The round-trip phrase “health route answering with the new version” needs a precise oracle: `/health` returns only status (`schemas/health.py:12-15`, `routes/health.py:28-34`), and extraMetadata changes only Electron's build version. Assert the new app/exe identity separately and health on the newly owned backend; do not invent a backend version field. This is a non-blocking clarification because the plan already checks the installed exe/new app. Check cache removal immediately after uninstall, before helper removal of residual data folders, so cleanup cannot mask a failed uninstaller.

S9 correctly blocks real-host completion when the host refuses unsigned software; it never moves the test to the dev PC or changes Smart App Control. No missing host measurement is reported.

## Q8 — Order, gates, dependencies and ownership

Accepted: feed Red/Green/build precedes the payload stage; run 1 takes the Electron Red before main/renderer implementation; settings, MCP, main and renderer Reds precede their Greens. Run 2 uses the same snapshot as its built pair and H1-2 binds the remote receipt. The full gate includes pytest without deselection, full Vitest, UI types/lint/build, MCP types/tests/build/audit, OpenAPI and the scoped checks. No local Electron fallback is authorized. The network exceptions are the named npm rows plus the explicitly authorized remote transport; feeds stay on 127.0.0.1.

The stated 2026-10-20 release date is beyond ui/.npmrc's seven-day hold on the review date; the date itself was not re-fetched. S7 and the lockfile diff must cover changed existing dependency versions as well as added packages. The licence allowlist/file checks and real-build licence generation are named and adequate as a plan contract.

S2 stops updater implementation at row 12 on a contrary ruling, but row 9 has already installed the recommended weekly default; D-1544 option B must therefore correct row 9/AC-174.9 too, as the brief already says. These edits are reversible and do not ship before Mat's release; no premature irreversible action was identified. The supplied ownership lists show no additional product-path collision beyond OpenAPI, settings-help-content and the shared 06/registry closeout paths already discussed. Broad test directories do not establish a new product-path collision. Ownership additions are resolved before row 0.

## Checklist Results

| Check | Result | Observation |
|---|---|---|
| PR-1 plan/task alignment | fail | F1-F4 are concrete behavior/test-contract conflicts. |
| PR-2 not started | pass | Draft task rows remain unstarted; named planning receipts only. |
| PR-3 task contract | pass | Both files specify rows, roles, deliverables, dependencies and validations; supplied lint receipt reports 36 rows. |
| PR-4 validation realism | fail | Prescribed macro edit fails two required unchanged assertions (F3). |
| PR-5 source-backed planning | partial | Local canon traced; updater source R1-R6 unavailable under the no-network constraint. |
| PR-6 correction readiness | pass | Two MEU handoffs, rolling reviews and stop/correction paths specified. Round-2 census rule is n/a. |
| PR-7 scope discipline | pass | Supplied scope decisions accepted; no hidden release/upload/signing/manual-check row. |
| PR-8 control behavior | fail | Off-switch fallback and installer process/pre-existing-state isolation counterexamples. |
| PR-9 boundaries and authority | pass | Human execution gate and manual publish retained; F3 correction must name all assertion changes. |

```json
{"schema_version": "evidence.v1", "check_id": "aau-plan-r1-source-counterexamples", "command": "rtk proxy python C:/Temp/av-kit/2026-11-26-app-auto-update/review/probe_plan.py", "cwd": "P:/av-kit", "scope": "Written updater schedule; installer macro assertions and host/process isolation", "phase": "plan-review", "exit_code": 0, "result": "fail", "tested_state": "main@c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4; working-tree plan; source-only observations, not a product full-gate identity", "output": "Never fallback permits checking; pending success is throttled at 1 h; recursive macro fails existing assertions 119/125; pre-existing Run values are deleted; NSIS fallback uses image-name taskkill.", "fresh": true}
```

The counterexample probe reads repository text and models written predicates; it runs no product test and installs nothing. It prints:

```text
UPDATE_TICK: saved never + rejected settings read + null timestamps => weekly fallback => check allowed
UPDATE_SCHEDULE: pending after successful download; restart 1 h later => False
login-item-nsh.test.ts:119 expected non-recursive RMDir; actual recursive RMDir; passes: False
login-item-nsh.test.ts:125 expected recursive count: 0 actual: 1 passes: False
INSTALL_STAGE_RULES: permitted pre-existing Run value is deleted by customUnInstall
INSTALL_STAGE_RULES: installed NSIS fallback uses taskkill /IM
probe-plan: counterexamples reproduced; repository files read only
```

The exact command is `rtk proxy python C:/Temp/av-kit/2026-11-26-app-auto-update/review/probe_plan.py` (exit 0). Source reads/searches are captured under C:/Temp/av-kit; durable decisive observations are embedded above rather than relying on scratch links. The named planning receipts show a connection timeout (no measured host facts) and `OK: 36 row(s)` from task lint; neither is runtime update evidence.

## Verdict

**changes_required**. Correct F1-F4 before putting this plan forward for execution approval. F5/F6 are concrete non-blocking behavior findings. No review-scaffolding or formatting defect is a blocker. No approved verdict, execution authorization, commit or upload is implied.

## Recheck (round 2)

**Current verdict: changes_required. Open findings: 1 (F4, partial).** The preceding Findings table and Q1–Q8 are preserved as the round-1 record; the results below supersede their then-current assessments. This is the independent Codex recheck of Claude Code/Anthropic's corrections, not execution approval.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |
| F3 | open | fixed |
| F4 | open | partial |
| F5 | open | fixed |
| F6 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### R1 — Each correction and its regression proof

Here `plan` means `docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md`, and `task` means the adjacent `task.md`.

- **F1 fixed.** `plan:162` makes rejecting and unknown interval reads skip with no call/state/store mutation; `plan:238` (AC-174.2) covers rejected reads, `daily` and saved `never`. `plan:163` and `:240` add malformed-file/throwing-constructor recovery. Rows 12/13 (`task:62`, `:63`) own Red and Green. No interval is guessed.
- **F2 fixed.** `plan:173` refuses both sign-in values, both shortcuts, the installer key and a prior owner record before installation. It requires ownership before mutation, `finally` teardown, equal snapshots before deleting the record and quarantine otherwise. AC-174.18/.20 are at `plan:254`, `:256`; row 4's negative fixtures and row 5's implementation are at `task:52`, `:53`. S10 (`plan:410`) preserves quarantine. F4's canary-order problem below is separate from this pre-existing-state correction.
- **F3 fixed.** `plan:200`, D-1553 (`plan:591`) and row 13 (`task:63`) name all five changes, including the exact-list assertion at `login-item-nsh.test.ts:119` and recursive-removal assertion at `:125`. The two-deletion count and AC-61.18 stay. Row 0's pin scanner and S5 agree (`task:46`, `plan:405`); AC-174.14 (`plan:250`) tests the guard.
- **F4 partial.** `plan:171` and AC-174.21 (`plan:257`) repair the stock selector/fallback design, with a real sibling oracle. But rows 3/7 build and run the canary before row 13 first changes the macro (`task:50`, `:55`, `:63`). See R2 and the remaining finding: this is still an executable occurrence of the original outside-folder stop, not a new refinement of a fixed predicate.
- **F5 fixed.** `plan:170` moves the two sign-in deletions inside the not-updated guard without changing their text. AC-174.14 catches the old placement (`plan:250`); ROUND_TRIP enables sign-in, requires it kept after update and tests its removal immediately after uninstall (`plan:174`, AC-174.19/.20 at `:255`, `:256`). Row 13 applies it; rows 16/17 prove it (`task:63`, `:67`, `:68`). rc.5's one-time loss is stated truthfully in FEED_CHECKLIST (`plan:158`).
- **F6 fixed.** `plan:160` bypasses the attempt throttle exactly once per start for a pending version, after checking Never first. AC-174.1/.2 (`plan:237`, `:238`) cover an attempt one hour ago, the reopened store, one initial call and no duplicate notice; rows 12/13 own the tests and implementation. This closes the schedule defect; the library re-emitting `update-downloaded` remains an explicitly unverified R3 dependency.

### Remaining Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F4 | High | yes | behavior | APP_RUNNING_CHECK is first implemented in row 13, but row 7 runs the product installer built in row 3 with the stock check. The new install-stage sibling decoy is inside that stock check's prefix match and has its fallback image name. The early canary can stop it, fails AC-174.18 and reaches S10 before the correction exists. Confidence: High. Violates: AC-174. | docs/execution/plans/2026-11-26-app-auto-update/task.md:50; docs/execution/plans/2026-11-26-app-auto-update/task.md:53; docs/execution/plans/2026-11-26-app-auto-update/task.md:55; docs/execution/plans/2026-11-26-app-auto-update/task.md:63; ui/node_modules/app-builder-lib/templates/nsis/include/allowOnlyOneInstallerInstance.nsh:66; ui/node_modules/app-builder-lib/templates/nsis/include/allowOnlyOneInstallerInstance.nsh:94 | Apply and validate the bounded macro before the row-3 build, with its own Red/Green ordering, update dependencies and rebuild the payload before row 7. Keep the early sibling proof. | open |

### R2 — APP_RUNNING_CHECK

**Hook placement is correct.** `NsisTarget.js:393`, `:408`, `:463` prepend the same shared header to both scripts; `:709-712` includes `build/installer.nsh` there. `installer.nsi:8-11` subsequently includes common/multiUser/allowOnlyOneInstallerInstance. A macro defined in that custom include is therefore visible to both. `allowOnlyOneInstallerInstance.nsh:5-8` omits `getProcessInfo.nsh` and `:37-42` replaces the entire active stock check. The stock fallback macro definitions, and the top-level nsProcess include, may remain in the template; the replacement does not expand/call their process-stop paths.

**The intended selector is bounded.** Canonicalizing the install directory, appending a separator, matching ordinally without case and excluding the current installer pid separates `install\av-kit.exe` from `install-sibling\av-kit.exe`. Empty ExecutablePath rows cannot identify an image as owned and are not permission to stop by name. Inspection exceptions and failed stops refuse; an inaccessible process with an empty path is not independently certified absent by this selector. The stock uninstaller's file-busy path attempts restoration (`uninstaller.nsh:164-179`). I found no demonstrated outside-folder stop in the specified replacement. This is a plan review, not proof that an unwritten macro compiles or implements all its stated exception handling.

**Refusal precedes replacement/deletion.** The installer calls the check at `installSection.nsh:33-36`, before `uninstallOldVersion` at `:52` and installation at `:66`; the uninstaller checks at `uninstaller.nsh:18-26` or `:148-150`, before `customUnInstall` at `:157`. Error level 2 followed by Quit leaves the installed payload intact in silent and interactive cases; scratch plugin extraction/window setup is not replacement of the old app. The app/backend may already be stopped. The persisted pending version plus the new recovery rule makes another offer possible after reopening, provided the interval is enabled and the library successfully revalidates/downloads again. It is not an unconditional promise for Never, offline operation or a withdrawn release. The unavailable updater's exact cache/relaunch behavior was not verified.

**AC-174.21 has a useful oracle but is not compiled-NSIS proof.** It takes the command from the macro and applies the actual NSIS substitutions, rather than independently reconstructing a passing selector. Copies of PING.EXE under inside/sibling paths are executable long-lived decoys, and the stock-filter positive control proves the sibling distinguishes the old match. A substitution/extraction bug could still diverge from compiled NSIS. The built-pair test supplies the complementary runtime proof: the inside MCP exe stops, the sibling survives and replacement completes. The early canary is currently defective: row 3 snapshots the macro before row 13 changes it; uploading a newer row-7 source snapshot does not change that installer payload. Thus F4 is not closed end to end.

**D-1554's M reading holds.** The newly specified refusal changes user-visible behavior (M-5). A narrower product process check changes neither an external interface nor the agent's own harness permission grant. PowerShell's product command line does not authorize a new agent sandbox exemption. I found no additional M-4/M-13 decision hidden by this correction; existing Mat-owned trust/disclosure decisions remain open as directed.

### R3 — Start at sign-in and existing assertions

Moving the two identical DeleteRegValue lines into `${ifNot} ${isUpdated}` skips both on `--updated` and executes both on a real uninstall. The current tests count/match their text, not their old position (`ui/tests/unit/login-item-nsh.test.ts:26-70`, `:124`). AC-114.1/.2/.3 continue their guard/target/count roles with exactly the five authorized lines changed (`:105`, `:112`, `:119`, `:122`, `:125`); no additional assertion change is needed for the planned macro. AC-174.14 adds the sign-in guard negative, and the real round trip checks preservation and immediate uninstall cleanup. The source-only probe applied the prescribed transformation in memory: two deletion lines remained inside the guard and exactly one recursive cache removal remained. It ran no Vitest.

### R4 — Ownership, quarantine and APP_GUID

The owner record makes a terminated run visible even after the ordinary host lock is released. It is written before account mutation, survives failed restoration or reboot, and makes every later install stage refuse until the recorded account state is recovered. `finally` covers ordinary assertion failures. Row 5 requires a run-book recovery procedure that reads the record, compares its saved snapshot, removes only what that run made and deletes the record after restoration; the paths, key/value names and run id are supplied rather than guessed. This is a planned procedure, not an existing recovery script or a restoration already measured on the host. `release` explicitly is not recovery. No further pre-existing-state hole was demonstrated in these corrections.

`NsisTarget.js:49` defines namespace `50e065bc-3134-11e6-9bab-38c9862bdaf3`, `:261` uses `options.guid || UUID.v5(appInfo.id, namespace)`, and `multiUser.nsh:8` uses `Software\${APP_GUID}`. The config is `com.avkit.app`, with no nsis.guid override. An independent local stdlib UUID-v5 calculation yielded **c21620fd-8854-5989-9a80-a73c80a17704**, exactly the plan's value. Row 4 pins the helper's constant; the canary additionally requires that actual key after installation and its removal afterward. The intended canary is a real integration oracle, but F4's ordering must be repaired before relying on it.

### R5 — Other correction effects and limits

No additional substantive finding. S7 now includes changed versions of existing packages (`plan:407`). S10 and the row-5 run book preserve the owner record; D-1413 is ruled and removed from S1; D-1555 is the next free id. The complete D-1544 brief now gives a real do-nothing outcome, holding the updater (`plan:676`); the shorter top summary still calls leaving false statements “do nothing” (`plan:135`), so that summary should follow the corrected brief. H1-6a (`task:78`) still says **20** MEU-174 ACs; the actual range and H1-6 row correctly include **21**. These are clerical notes only, not findings or blockers.

I could not independently check R1–R6: electron-updater 6.8.11 is absent and no network was allowed. Unverified claims include npm versions/release dates/licence metadata; GitHubProvider's exact endpoints and Latest/prerelease selection; the library's SHA-512/error/signature behavior; cached-download recovery events; quitAndInstall launch/quit/restart semantics; the development-feed seam; the import workaround; issue 7807's fix and the signed-manifest/version claims. Local builder and runtime source corroborates parts of feed generation/digest plumbing but cannot establish all of those updater-specific facts. The execution probes and named stop conditions remain necessary. No product suite, build, installer, SSH or network action ran in this review, and no host fact was measured.

### Checklist Results (round 2)

All manual checks were observed by `codex-independent-reviewer` through the numbered file reads in this pass. Commands and decisive source-only probe output are embedded below. They establish plan/source observations, not product runtime passes.

| Check | Result | Observation |
|---|---|---|
| PR-1 plan/task alignment | fail | F4: the replacement macro is scheduled after the canary that requires it. |
| PR-2 not started | pass | All 36 executable task rows remain `[ ]`; draft status, planning receipts only. |
| PR-3 task contract | pass | The supplied task-lint-r2 receipt reports 36 rows, resolved acyclic dependencies; that structural pass does not detect the canary's stale compiled macro. |
| PR-4 validation realism | fail | Row 7 cannot satisfy its sibling-liveness/install-stage-pass requirement with row 3's stock-macro payload. |
| PR-5 source-backed planning | pass | Corrected choices are tied to ACs and named decisions; R7 independently traced locally. R1–R6 remain expressly unverified, not represented as checked. |
| PR-6 correction readiness | pass | Prior findings remain auditable; all six corrections traced to current ACs/rows. No paperwork issue is used as a blocker. |
| PR-7 scope discipline | pass | Manual upload, unsigned trust/disclosure decisions and remote-only Electron scope remain intact. No manual behavior-check row added. |
| PR-8 observable/control behavior | fail | F1/F2/F3/F5/F6 now have positive/negative regression contracts; F4 still invokes the stock outside-folder stop in the early canary. |
| PR-9 single-statement consistency | pass | Corrected schedule, guard, pin list, owner record and stop conditions agree in substance. The stale AC count is clerical. |

```json
{"schema_version":"evidence.v1","check_id":"aau-plan-r2-source-contracts","command":"rtk proxy python -B C:/Temp/av-kit/2026-11-26-app-auto-update/review/probe_round2.py","cwd":"P:/av-kit","scope":"Corrected schedule, installer guard and pin statements, UUID derivation, canary build/use ordering","phase":"plan-review","exit_code":0,"result":"fail","tested_state":"main@c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4; plan sha256=c15683db1f381fbc0e34abfdf41d4619e331e9f209d83e505cdd02eb6bb3504f; task sha256=e58bfc681b2b7caa0bc61b55ffbc1559929a5d9d823dd0159b762be8076271d0; read-only source-contract probe, not a product full-gate identity","output":"APP_GUID c21620fd-8854-5989-9a80-a73c80a17704; Never false; pending recovery at +1h true and recovered at +1h false; two guarded deletion lines and one recursive cache removal. F4 PARTIAL: row 3 builds canary before row 13 adds customCheckAppRunning; row 7 uses that canary. Sibling stock-prefix match=True; bounded match=False; stock fallback matches av-kit.exe by name. No installer or product suite run.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"aau-plan-r2-local-nsis-trace","procedure":"Read both complete plan files, the prior report, the installed common.nsh/installSection.nsh/uninstaller.nsh/multiUser.nsh/allowOnlyOneInstallerInstance.nsh, NsisTarget.js header/build/GUID sections, ui/build/installer.nsh and login-item-nsh.test.ts; trace row 3 payload into row 7 and compare row 13's first macro edit. Read supplied planning receipts without rerunning their commands.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Plan round-1 corrections and the local NSIS production call chain","phase":"plan-review","exit_code":null,"result":"fail","tested_state":"main@c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4; target plan/task hashes recorded above; unrelated Session 104 state excluded","output":"Shared custom include is prepended to installer and uninstaller scripts; hook bypasses the active stock check. Stock selector/fallback remain active in the row-3 payload because the custom macro is first added in row 13. Row-7 sibling install-sibling matches stock install prefix. Supplied lint: OK: 36 row(s); 34 fully checked, 2 view_file exemptions. Supplied host receipt: connection timeout; not a host/runtime pass.","fresh":true}
```

### Verdict (round 2)

**changes_required** — F4 is partial; F1, F2, F3, F5 and F6 are fixed. Move the bounded installer check and its regression test before the canary build, preserving Red/Green and the sibling oracle, then recheck the repaired dependency order. No new finding is added. The complete rolling report is staged at `C:/Temp/av-kit/aau-plan-review-round-2.md` for the coordinator to copy. No repository file was edited, and execution remains outside this review's authority.


## Recheck (round 3)

**Current verdict: approved. Open findings: 0. Intent achieved: yes, at the plan-specification level.** This section supersedes the historical verdicts above. All round-1 and round-2 body content, including F1–F6, Q1–Q8 and the round-2 recheck, is preserved verbatim. Claude Code/Anthropic authored the plan; Codex is the independent reviewer. Approval establishes fitness to execute. It does not authorize execution or Mat's release.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | fixed | fixed |
| F2 | fixed | fixed |
| F3 | fixed | fixed |
| F4 | partial | fixed |
| F5 | fixed | fixed |
| F6 | fixed | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

Here `plan` means `docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md`, and `task` means the adjacent `task.md`. Results below assess the written execution contract; they are not product/runtime passes.

### R1 — F4 and the canary build/use order

**F4 fixed.** Rows 2a and 2b now put AC-174.21's Red and Green before the installer build (`task:50`, `task:51`). The dependency chain is `2 → 2a → 2b → 3 → 4 → 5 → 6 → 7` (`task:49-57`). Row 3 snapshots that macro, refuses `macro-missing` with exit 12 before packing, and records the extracted `installer.nsh` SHA-256 in `aau-row3-macro.json` (`task:52`; `plan:380`, `plan:383`). Row 7 verifies its snapshot, then checks `macro-current` before the host check; a mismatch exits and directs a row-3 rebuild (`task:57`; `plan:389`). A newer source snapshot alone is no longer treated as a rebuilt installer.

The early sibling proof remains in run 1: the helper starts the `install-sibling/av-kit.exe` decoy, requires it alive after installation and uninstall, and the canary install stage must pass with no skip (`plan:173`, `plan:254`, `plan:389`; `task:55`, `task:57`). The canary starts with no pre-existing install, so no old stock uninstaller is introduced by this order.

Local source corroborates the binding: `NsisTarget.js:393`, `:408`, `:463` use the shared header for both scripts; `:709-712` adds the custom include. `installer.nsi:8-11` subsequently includes the stock hook, and `allowOnlyOneInstallerInstance.nsh:37-42` selects `customCheckAppRunning` instead of the stock branch. The row-3 real build and row-7 canary remain the execution proofs that the unwritten macro compiles and runs as specified.

### R2 — Test compatibility, Red hashes and checker order

**The new order is coherent.** Current `ui/tests/unit/login-item-nsh.test.ts:26-70` counts/matches the two registry deletion lines; `:77-94` extracts `customUnInstall`; `:101-125` checks its guarded cache removal and the file's deletion/recursive-removal counts. Row 2b adds a separate macro with no `DeleteRegValue` or `RMDir`, while leaving `customUnInstall` unchanged (`task:51`). Thus the prescribed change need not alter any existing assertion to get its early Green.

Row 13 later changes only `customUnInstall` under `UNINSTALL_CACHE_RECURSIVE`, preserves row 2b's macro, names the five authorized existing-test changes, and reruns the unchanged `app-running-nsh.test.ts` (`task:65`; `plan:170`, `plan:200`). AC-174.21 tests the separate running macro/its extracted command, not a fixed hash of the whole NSH file. The later cache/sign-in edit therefore introduces no contradictory expectation. Actual Vitest results are still execution work.

Row 0 creates the checkers before 2a (`task:46`; `plan:362`). The copied `red-check.py` accepts an assertion failure for an `AC-174.21 ` title and rejects an unrelated import failure; source-only fixtures also confirmed that `.21` does not satisfy a `.2` requirement. Row 2a records the new test under the explicit label `2a`; row 2b calls `red-unchanged`, `pins-scan.py --check` and `eol-check.py`. No pinned existing test changes in 2b. The new `row-check.py`/`pins-scan.py` are planned row-0 deliverables, not existing implementations whose runtime behavior was verified; their written contract must support the explicitly requested `2a` label and preserve its hash through row 13.

Row 12's command now contains four test files, four recorded hashes and nine required ids (AC-174.1 through .8, plus .14), with no `.21` requirement or running-macro test (`task:64`). Its prose correctly cross-references the earlier ownership. Row 13 preserves/reruns that ownership rather than reapplying `APP_RUNNING_CHECK` (`task:65`).

### R3 — Counts, receipts, dependencies and M-7 references

The tables contain **5 MEU-173 ACs, 21 MEU-174 ACs, 38 task rows and 21 numbered work rows including baseline row 0**. The **20** in D-1545's sizing/split brief counts rows 1–18 plus 2a/2b, excluding baseline (`plan:479`, `plan:684`); it does not omit an implementation row. The new build/use dependency chain is explicit. `WP-2`, `WP-5`, the NSH Files Modified entry and the validation-stage contract agree (`plan:87`, `plan:90`, `plan:315`, `plan:795-797`).

H1-6 correctly adds 2a to MEU-174's Red receipts and 2b to its Green receipts, records the E2E Red at row 7 rather than the row-6 spec-writing step, and separately requires both remote runs (`task:79`). Row 13 still owns the existing uninstall assertion changes throughout §Test pins, Files Modified and S5 (`plan:200`, `plan:317`, `plan:405`; `task:65`). This remains an explicit named-test/new-assertion row satisfying the previously reviewed M-7 condition (`plan:591`).

**Clerical note only:** H1-1's `.isdigit()` unchecked-row scan ignores `2a` and `2b` (`task:74`). Broaden that helper to include these row ids so its stated scan includes every implementation row. A source-only counterexample with only 2a/2b unchecked confirms the omission. The bounded macro itself remains required by the separate Green, build, host and handoff contracts above; this helper-shape note does not demonstrate a materially missing update deliverable passing the complete gate and does not block approval.

### R4 — The two clerical corrections

**Both corrected.** D-1544's short summary now gives the same real do-nothing outcome as option C: hold the updater so no release carries it before Mat rules and the statements stay true (`plan:136`, `plan:676`). The brief still truthfully describes the new outbound request and the explicit Check now exception to Never (`plan:673`). H1-6a now asks for **5 and 21**, with no count literal in its coverage command (`task:80`).

### R5 — Other correction effects and verification limits

No new delivery-level defect was demonstrated. The earlier fixes remain intact: **F1** skips rejected/invalid interval reads (`plan:162`, `plan:238`); **F2** refuses pre-existing account state before mutation and retains ownership/quarantine until restoration (`plan:173`, `plan:254`, `plan:256`; `task:54-55`); **F3** names all five assertion changes and retains the two deletion checks (`plan:200`; `task:65`); **F5** preserves sign-in on an update and checks its removal before helper cleanup (`plan:170`, `plan:174`, `plan:250`, `plan:255-256`); **F6** retains the first-start pending-version recovery exception after the Never check (`plan:160`, `plan:237-238`). D-1543's trust statement and hold-until-signed alternative remain truthful (`plan:135`, `plan:664-667`). No newly changed decision takes a Mat-owned action autonomously.

**R1–R6 remain independently unverified.** `ui/node_modules/electron-updater/package.json` is absent and this review made no network request. I could not check the registry versions/dates/licence metadata; GitHubProvider's exact endpoints, Latest/prerelease selection; updater SHA-512/error/signature behavior; cached-download recovery events; `quitAndInstall` launch/quit/restart semantics; development-feed behavior; the ESM import workaround; issue 7807's fix; or signed-manifest/version claims. Local R7 builder/templates were read, but they do not establish those updater-specific facts. The planned execution probes and stops remain necessary.

HEAD was independently read as `main@c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4`. Only the assigned target plans, supporting local sources and named planning receipts were considered; unrelated Session 104 state and the host-ignore exception are excluded from the source identity. The supplied round-3 lint receipt says `OK: 38 row(s)`, 36 fully checked, 2 `view_file` exemptions, dependencies resolving and acyclic. That was a receipt read, not a fresh task-lint execution. The three fenced YAML blocks and both plan/task frontmatters parsed in the independent source probe.

### Checklist Results (round 3)

Manual observations below were made by `codex-independent-reviewer` through the numbered reads in this pass, with null command exit. The independent source probe's executed command and decisive output are embedded afterward.

| Check | Result | Observation |
|---|---|---|
| PR-1 plan/task alignment | pass | The dedicated 2a/2b cycle, build dependency and row-7 freshness check now agree. |
| PR-2 not started | pass | Both artifacts are draft; all 38 task rows remain `[ ]`; planned row-0 scripts are not present yet. |
| PR-3 task contract | pass | Counts/dependencies checked independently; the supplied lint reports 38 rows, 36 checked and 2 read exemptions. |
| PR-4 validation realism | pass | Early test reads the actual macro/command; unchanged sign-in tests are compatible; row 13 reruns the early test. |
| PR-5 source-backed planning | pass | Corrections remain bound to named ACs/decisions and local R7 source; R1–R6 are explicitly unverified. |
| PR-6 correction readiness | pass | All six prior findings traced; complete prior report retained; no paperwork issue blocks this review. |
| PR-7 scope discipline | pass | No release/upload/version change or manual behavior-check row added; Mat's two release decisions remain his. |
| PR-8 observable/control behavior | pass | Presence/refusal plus source hash precede the canary; the sibling oracle still runs in host run 1. |
| PR-9 single-statement consistency | pass | APP_RUNNING_CHECK ownership and later uninstall/pin contracts agree; the H1-1 helper note is clerical. |
| Updater R1–R6 independent source verification | n/a | Package absent, network forbidden; no claim of verification. |

```json
{"schema_version": "evidence.v1", "check_id": "aau-plan-r3-source-contracts", "command": "rtk proxy python -B C:/Temp/av-kit/2026-11-26-app-auto-update/review/probe_round3.py", "cwd": "P:/av-kit", "scope": "Revised task graph, AC counts, macro test compatibility, Red parser fixtures and YAML", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "main@c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4; plan sha256=7c087b69a62442f322032fb374c14e7ea08222d84ce24508079fb9217b610ead; task sha256=e88257c1238fd783587bb7ea0f11050b07f59a5bfd340de3fb6670e4c4655454; source-only plan review, not a product full-gate identity; unrelated Session 104 state excluded", "output": "implementation-plan.md sha256=7c087b69a62442f322032fb374c14e7ea08222d84ce24508079fb9217b610ead\ntask.md sha256=e88257c1238fd783587bb7ea0f11050b07f59a5bfd340de3fb6670e4c4655454\nYAML: 3 plan fenced blocks and both frontmatters parse\nCounts: 38 tasks, all unstarted; 21 work rows including baseline, 20 excluding it; ACs 5 and 21\nBuild/use order: 2 -> 2a -> 2b -> 3 -> 4 -> 5 -> 6 -> 7; macro presence/hash/refusal before host check\nRed/Green: row 2a owns AC-174.21 and its hash; row 12 requires nine other ids in four files; row 13 reruns the early test\nMacro compatibility: current tests inspect two DeleteRegValue lines, customUnInstall and one non-recursive RMDir; the new running macro adds neither command\nLater uninstall edit model: two guarded DeleteRegValue lines, one recursive cache removal; touches only customUnInstall, leaving any separate running macro unchanged\nred-check fixture ac21-assertion: accepted as expected\nred-check fixture ac21-import: refused as expected\nred-check fixture ac21-not-ac2: refused as expected\nClerical predicate note: H1-1 .isdigit() ignores unchecked 2a/2b; separate Green/build/host/handoff checks remain specified\nprobe-round3: all source-contract assertions passed; no product suite, installer, process stop, network or SSH ran", "fresh": true}
```

```text
implementation-plan.md sha256=7c087b69a62442f322032fb374c14e7ea08222d84ce24508079fb9217b610ead
task.md sha256=e88257c1238fd783587bb7ea0f11050b07f59a5bfd340de3fb6670e4c4655454
YAML: 3 plan fenced blocks and both frontmatters parse
Counts: 38 tasks, all unstarted; 21 work rows including baseline, 20 excluding it; ACs 5 and 21
Build/use order: 2 -> 2a -> 2b -> 3 -> 4 -> 5 -> 6 -> 7; macro presence/hash/refusal before host check
Red/Green: row 2a owns AC-174.21 and its hash; row 12 requires nine other ids in four files; row 13 reruns the early test
Macro compatibility: current tests inspect two DeleteRegValue lines, customUnInstall and one non-recursive RMDir; the new running macro adds neither command
Later uninstall edit model: two guarded DeleteRegValue lines, one recursive cache removal; touches only customUnInstall, leaving any separate running macro unchanged
red-check fixture ac21-assertion: accepted as expected
red-check fixture ac21-import: refused as expected
red-check fixture ac21-not-ac2: refused as expected
Clerical predicate note: H1-1 .isdigit() ignores unchecked 2a/2b; separate Green/build/host/handoff checks remain specified
probe-round3: all source-contract assertions passed; no product suite, installer, process stop, network or SSH ran
```

```json
{"schema_version": "evidence.v1", "check_id": "aau-plan-r3-local-source-review", "procedure": "Read the prior rolling report and both complete target plan files; trace rows 2a/2b/3/7/12/13 and the local NSIS shared-header/custom-hook/installation call chain; compare current login-item test assertions and later uninstall edits; inspect named planning receipts without rerunning them.", "observer": "codex-independent-reviewer", "cwd": "P:/av-kit", "scope": "Round-2 corrections and R1-R5 recheck; PR-1 through PR-9", "phase": "plan-review", "exit_code": null, "result": "pass", "tested_state": "main@c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4; plan sha256=7c087b69a62442f322032fb374c14e7ea08222d84ce24508079fb9217b610ead; task sha256=e88257c1238fd783587bb7ea0f11050b07f59a5bfd340de3fb6670e4c4655454; source-only plan review, not a product full-gate identity; unrelated Session 104 state excluded", "output": "F4 fixed: row 3 depends on 2b, refuses a missing macro and records its extracted source hash; row 7 checks that hash before the host and requires rebuild on mismatch. Early sibling canary remains. Row 2b leaves customUnInstall unchanged; row 13 preserves the running macro and reruns its test. F1/F2/F3/F5/F6 remain fixed. D-1544 hold option and 21-AC count agree. Supplied lint: OK: 38 row(s), 36 checked, 2 exemptions. R1-R6 not independently verified; no product runtime pass claimed.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "aau-plan-r3-report-structure", "command": "rtk proxy python -B tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/aau-plan-review-round-3.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/2026-11-26-app-auto-update/review/review-state-round3.json", "cwd": "P:/av-kit", "scope": "Rolling review report parsing, target binding, round count and remaining findings", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "main@c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4; plan sha256=7c087b69a62442f322032fb374c14e7ea08222d84ce24508079fb9217b610ead; task sha256=e88257c1238fd783587bb7ea0f11050b07f59a5bfd340de3fb6670e4c4655454; source-only plan review, not a product full-gate identity; unrelated Session 104 state excluded", "output": "OK: review_mode=plan; round 3 of 3; verdict=approved; open findings=0. State receipt written under the review receipts directory. This parses the report; the coordinator still validates/records the reviewer verdict in the ledger.", "fresh": true}
```

### Verdict (round 3)

**approved** — F1–F6 are fixed at the plan-contract level; there are no open findings or new substantive findings. The H1-1 scan note is non-blocking. The report is staged only at `C:/Temp/av-kit/aau-plan-review-round-3.md` for the coordinator's canonical save. No repository file was edited. No product suite, npm/uv operation, build, installer, process stop, SSH or network action ran. Completion-preflight was applied to this review artifact; the plan's unchecked execution rows remain outside this review's authorization.
