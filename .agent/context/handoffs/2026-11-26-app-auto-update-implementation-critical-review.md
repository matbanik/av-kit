---
date: "2026-11-28"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "aau-execution-2026-11-26-app-auto-update"
round: 2
---

Current verdict: **approved**, round 2, with F1 and F2 fixed and no new findings. The frontmatter describes the current round. The round-1 body below is preserved as historical evidence, including its original open rows and verdict; the final `## Recheck (round 2)` records their disposition and current Q1–Q8 conclusions.

# Critical Review: app-auto-update

> **Review Mode**: execution
> **Verdict**: changes_required

## Scope

**Intent anchor:** an installed av-kit learns of a newer release by itself and installs it without a visit to the release page. On the schedule the user picks in Settings (once a week, the default; once a month; or never), the packaged app asks the public repository's releases for the version GitHub marks Latest. If it is newer, the app downloads the installer in the background, checks it against the feed's SHA-512, tells the user once, and shows **Restart and update** in Settings. One click there stops the backend in the app's own order, runs the installer silently and starts the new version. The app never restarts by itself. A release build writes the two feed files beside the installer, a script checks them against the built installer, and the upload stays Mat's step. Unit tests, an Electron E2E against a local feed, and a real update from one built version to the next on the mini-air host prove it, with no manual check.

Independent read-only review of Claude Code/Anthropic's Session 106 implementation, MEU-173 and MEU-174. Reviewed the scoped delta from baseline/HEAD `5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9`, both implementation handoffs, the plan/task, the two 07 homes, relevant library/NSIS sources, tests and retained receipts. Session 105 and process-paperwork quality are excluded. No repository file was edited.

**tested_state:** `5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+72e0593a05f7f5e9b7084c59af095342053235e593b2d6dccb2fbdb481229875`.

Obtained independently twice with `identity.py --state-only`, ELECTRON_RUN_AS_NODE unset. It exactly equals gate r8 and H1-6b. There is no differing value to attribute to global-ignore access. Neither prohibited settings nor the global-ignore file was opened.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | The scheduled UPDATE_TICK (AC-174.2), using UPDATER_CONFIG (AC-174.3), sends a persistent installation identifier to GitHub. electron-updater creates/reuses `.updaterId` and attaches `x-user-staging-id` to feed requests; the integration leaves that default intact. A network-free probe using the real controller, NsisUpdater and GitHub provider intercepted six requests over two starts: every request carried the same UUID. This contradicts the explicit D-1544 recommended outbound contract at plan :675 and the newly delivered README/07 statement that the request carries no identifier. Every installed user with scheduled checks enabled would disclose this identifier, including before choosing to install. Contract family: AC-174. | ui/src/main/index.ts:711; README.md:63; docs/build-plan/07-distribution.md:9 | Suppress the installation-specific identifier at the updater/provider boundary while preserving Latest and checksum behavior. Add a real-library request-header regression test across two starts. Any proposal to disclose and retain it instead changes the stated recommendation and requires Mat's ruling. | open |
| F2 | Medium | no | behavior | UPDATE_QUIET_FAILURE sanitizes only its own log line (AC-174.5). The real library retains its default console logger and built-in error listener, which prints the raw error stack separately. A network-free injected HTTP error produced the controller's one sanitized line plus two library log entries; the error entry retained both the synthetic query and profile-path marker. Ordinary errors from a per-user installation can therefore expose profile paths in captured main-process logs. The mock-only test does not observe this logger. | ui/src/main/index.ts:711; ui/src/main/app-updater.ts:228; ui/tests/unit/app-updater.test.ts:557 | Configure the library logger to suppress raw details or route them through the same sanitization. Verify with a real NsisUpdater instance. | open |

## Q1 — Goal

**The functional update path is demonstrated; the delivered outbound contract is incomplete because of F1.** No Critical finding was found. F2 does not prevent checking, downloading or installing.

| Goal part | Criteria / implementation | Evidence accepted |
|---|---|---|
| Weekly/monthly/never; Latest only | AC-174.1–3, AC-174.9–12; `update-schedule.ts:19`, `app-updater.ts:170`, registry/API/MCP/UI leaf | Boundary/retry/recovery unit assertions; independent Python tests; real library GitHub provider uses `/releases/latest` with allowPrerelease false. |
| Background download, SHA-512, one notice | AC-174.4–6; `app-updater.ts:247`, :273 | Unit assertions; main-stage local-feed E2E; installed wrong-hash and good-feed requests recorded in run d7983df. |
| Settings action; backend first; silent install and new app; no automatic restart | AC-174.7–8, .12–13, .15–16, .19; `app-updater.ts:389`, IPC, UpdatesCard | Call-order/pending/duplicate tests; recorded seam call exactly `[true,true]`; real version transition and old-process death assertions. |
| Feed assets/check; Mat uploads | AC-173.1–5; builder config, feed checker and checklist | Real row-3 build: 371,756,740-byte installer, 388,536-byte blockmap; feed-ok/0, feed-missing/10, sha512-mismatch/15. |
| Scripted proof | AC-174.17–21; remote stage and install specs | Canary passes; final main 266/266 and install 2/2; snapshot bound to current product paths. No human visual check substitutes for an assertion. |

Accepted the approved scope, D-1543's unsigned trust recommendation and Mat's first-release gates. F1 challenges the implementation's conformity to D-1544's recommendation, not whether Mat should choose that recommendation.

## Q2 — Feed and no-publish configuration

**Accepted.** FEED_BLOCK has exactly provider/owner/repo and one entry. DIST_NEVER_PUBLISHES adds the flag to `dist`; workflow steps retain it without a supplied GitHub token. The workflow pin is unchanged.

FEED_CHECK compares both hash fields, both installer names, version, size, nonempty blockmap and app-update config; mismatch reasons 10–18 are distinct. Its independent selftest passed 10/10; the permitted Python run also exercises mismatch fixtures and malformed names. Row 3 proves the correct product build and both requested changed-copy failures.

FEED_CHECKLIST names all three assets, orders checking before upload, preserves the earlier blockmap, states Latest/pre-release semantics and explains the one-time manual install/sign-in reset. The release-upload command is explicitly Mat's. No agent-run release command was found in the scoped implementation.

## Q3 — Schedule and settings layers

**Accepted.** UPDATE_SCHEDULE has the exact seven-/thirty-day inclusive boundary, 24-hour failed-attempt bound, future-clock treatment, Never refusal and once-per-start pending-version recovery. UPDATE_TICK rereads the interval, skips unreadable/unknown values without assuming weekly, and prevents overlapping checks/downloads.

UPDATE_INTERVAL_LEAF agrees across core wires/registry, API model/OpenAPI, UI schema and MCP. API refusal occurs through the real service registry; UI/MCP use the exact-case enum and remain strict. The API tests verify 422 and an unchanged previously saved value. No tool or action was added. OpenAPI drift independently exits 0.

D-1582's delta adapter handles precisely the new SettingsPutIn property, checks its exact expected shape and has a negative fixture for a changed shape; its capture-shape expectations remain intact. F1 concerns actual outbound headers, which these schedule/schema tests do not inspect.

## Q4 — Main-process updater and trust

**Accepted except F1/F2.** UPDATER_CONFIG sets all four required flags and does not call setFeedURL. UPDATE_STATE writes only the five controller keys, guards construction/reads/writes and maps events to the required states. The library additionally owns `.updaterId`; that separate persistent file explains F1.

UPDATE_INSTALL_ORDER is reached from update-install, has the ready/once guards, sets quit intent, awaits shutdown and calls quitAndInstall(true,true). D-1571 shares the same shutdownOwned('quit') operation with before-quit and preserves its normal quit behavior; memoization prevents repeating the stop. The passing installed run independently supports that wiring.

The seam requires AVKIT_E2E=1 and a feed file; without the flag the feed/tick variables are not read and the recording global is absent. Unknown intervals cannot enable it. Failure classification and promise handling work in the real-library probe; no failure dialog or automatic installation is introduced.

**Trust as built matches D-1543:** the public GitHub provider uses HTTPS, SHA-512 comes from latest.yml, and no publisher signature authenticates the feed/installer. The card shows the required trust sentence in every state. This accepts the stated model without deciding Mat's open first-release question.

**F1 decisive source chain:** installed `electron-updater/out/AppUpdater.js:380–389` gets the persistent staging ID and calls `client.setRequestHeaders(...)`; :501–525 reads or writes `.updaterId`; `providers/Provider.js:59–68` merges those headers into each request. The app's integration at index.ts:711–720 does not override that behavior.

**Network-free probes actually executed:** load the current controller in memory with TypeScript transpilation; instantiate installed NsisUpdater with an explicit scratch app adapter; for the header probe, provide the real GitHub config and replace only the HTTP executor with in-memory Atom/Latest/YAML responses. Run two controller instances against the same scratch userDataPath. For the logging probe, replace doCheckForUpdates with a rejecting synthetic error and capture console methods. Neither probe starts Electron, reads real app data or performs a network request.

```json
{"schema_version":"evidence.v1","check_id":"review-real-library-headers","procedure":"Codex executed the real controller and installed NsisUpdater/GitHubProvider twice with scratch-only app data and a fully intercepted HTTP executor, recording every outgoing request header before returning in-memory feed responses.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"UPDATE_TICK and UPDATER_CONFIG outbound behavior; D-1544 recommended contract","phase":"targeted","exit_code":null,"result":"fail","tested_state":"5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+72e0593a05f7f5e9b7084c59af095342053235e593b2d6dccb2fbdb481229875","output":"states=[idle,idle]; interceptedRequests=6; hosts=[github.com]; allRequestsCarryId=true; sameIdAcrossStarts=true; persistedUpdaterId=true; networkRequests=0"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-real-library-logging","procedure":"Codex executed current createAppUpdater with installed NsisUpdater, replacing its internal check body with a synthetic HTTP rejection and recording console output plus the controller logger.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"AC-174.5 UPDATE_QUIET_FAILURE","phase":"targeted","exit_code":null,"result":"partial","tested_state":"5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+72e0593a05f7f5e9b7084c59af095342053235e593b2d6dccb2fbdb481229875","output":"state=error; kind=network; controllerLogs=[update: check failed kind=network]; libraryLogCount=2; libraryRetainsQuery=true; libraryRetainsProfileMarker=true; networkRequests=0"}
```

## Q5 — Updates card

**Accepted.** UPDATES_CARD follows Startup, uses the existing GridSelect/Button and theme tokens, saves through schedulePut, displays the version and status, and disables Check now in checking/downloading/disabled. Restart and its jobs-stop note appear only in ready. A ref prevents another install call while pending. The trust sentence is unconditional. An unknown state takes the idle status/default branch, with no restart button.

Unit tests assert exact options, save payload, state-specific text/buttons, pushed-state changes and pending-click suppression. E2E checks the real preload/main/renderer chain. Importing GridSelect from SettingsPage introduces no demonstrated initialization or render failure.

## Q6 — Installer, host stage and round trip

**Accepted.** APP_RUNNING_CHECK appends a separator to the normalized install directory, compares case-insensitively, excludes its own PID and stops by PID only. find=1 enters the question/stop path; every other unsuccessful result, including a nonnumeric nsExec launch error, refuses before installation mutations. Installed NSIS templates insert this macro in both installer and uninstaller paths. The unit evidence includes the stock-filter negative oracle and invalid-folder refusal; no decoy/process probe was rerun in this review.

UNINSTALL_CACHE_RECURSIVE changes only the named cache deletion and moves the same two registry lines inside the update guard. AC-61.18 remains unchanged. The successful round trip keeps Start at sign-in, and its subsequent uninstall proves cache/sign-in removal.

HOST_PAYLOAD preserves the no-payload request behavior. Flat-name/count/size/hash checks precede upload; missing, failed, flaky or skipped install results cannot produce success. INSTALL_STAGE_RULES refuses existing account traces, records ownership before mutation, spares the sibling decoy and requires before/after equality before removing the owner record.

The actual d7983df install report records AC-174.19 and AC-174.20 as expected/passed with no retry. Its annotations show both bad and good installer requests and `updater-cache-before=true`. Step (4) asserts checksum error, old version and absent restart. Steps (6)/(7) assert the old app/backend/MCP PIDs gone at the first new-version read, a new running app/healthy backend, retained setting/marker/Run value and surviving sibling. AC-174.20 checks cache and both values before teardown removes data folders.

Direct comparisons of the archived specs confirm D-1578 removed only the load-state wait, retaining root-visible/nonempty assertions; D-1579 replaced check() with unchecked → click → checked and retained registry verification. The third failed run and passing run have identical round-trip spec bytes. These did not weaken AC-174.19/.20.

D-1583 is appropriate: startup now uses `com.avkit.app`, already the builder shortcut, login-item and toast identity. It fixes the incorrect sign-in read and aligns taskbar grouping with installed shortcuts. A current rc.5 process previously using Electron's default identity can change grouping when the correct identity is applied; normal installer-created pins and toast attribution use the same intended appId. The real run proves the sign-in fix, not every historical user-created pin. One verification run after a root-caused product correction establishes this test's success; it is not a reliability statistic. The coordinator's lifted run bound is accepted.

## Q7 — Gate and pins

**Accepted.** R8's retained gate and per-step receipts show all 33 steps exiting 0, UI 1801/1801, Python 3412, MCP 560/560 and audit 104/104, with equal before/after identities. The independently rerun remote-run-2 check reports 63 product paths and zero changes from snapshot d7983dff3e7e. The full gate covers the registered scope.

The r4 formatting correction is tooling-only. R5/r6 remain failed runs; the isolation receipts and the subsequent complete pass support the load/resource explanation. This review did not independently measure the other repository's historical workload. R7's audit invocation genuinely refused with exit 4; R8 uses the already proven authoritative argv and baseline. No deselection, raised timeout or excused test appears in the final gate. No product/test assertion change between these gate attempts is evidenced.

Independent pins-scan and red-unchanged both report zero problems. Direct diffs confirm added channel/section enumerations, necessary count growth and only the named five row-13 NSIS expectation changes. AC-61.18 and the other unchanged pins retain their bytes. F1/F2 are gaps in what the mocks observe, not evidence that the successful gate was bypassed.

## Q8 — Safety and fidelity

**Accepted with the F1 outbound exception and F2 logging exception.** No evidence in the scoped delta/receipts indicates a release-asset upload, publish, tag, push, stash or revert. HEAD remains the supplied baseline and the index is empty. Snapshot commit objects support testing without moving main. Pair versions are generated scratch config only; the repository version remains rc.5. Authorized remote test-payload transfers are recorded; product-test feed traffic is local.

The lock adds exactly five entries in electron-updater's closure and changes no existing version. Their licences are MIT/ISC. Eleven pre-existing entries become production dependencies; argparse retains its pre-existing Python-2.0 licence, explicitly disclosed under D-1577 rather than falsely counted among the five newly added packages. The lazy-val override matches installed package metadata (MIT and the named author) and supplies standard MIT text; this offline review did not recheck its remote repository.

Independent eol-check reports 87 paths, zero problems, including preservation of the existing mixed-ending file. scope-paths reports zero problems and accounts for Session 105/concurrent baseline paths. No out-of-scope repository write was made by the reviewer.

Some raw tool receipts contain host/profile path strings; this report uses <HOME>. A contact string in the lockfile predates this session and was not reproduced. No newly introduced personal author address or evidence of real-user file content was found in the scoped delta. Prohibited files, real app data and the host were not accessed.

## Checklist Results

All reviewer commands used RTK proxy, all-stream receipts, immediate exit capture, PYTHONDONTWRITEBYTECODE=1, scratch TMP/TEMP and ELECTRON_RUN_AS_NODE unset. UV_CACHE_DIR was redirected to scratch with UV_OFFLINE=1 after the default cache access was refused; no package sync/install occurred. An initial run-check argv-order mistake exited 2; the corrected CONSOLE-first invocation below exited 0.

| Check | Result | Command/procedure | Exit | Decisive evidence |
|---|---|---|---|---|
| IR-1 live runtime; IR-7 complete functional AC proof | pass | Read both run reports/specs; rerun run-check with the row flags and remote-run-2 | 0 | Canary 1 passed; final main 266 passed, install 2 passed; current product paths bound. |
| IR-2 stub fidelity / IR-3 mapping / IR-6 boundaries | pass | Read API/core/MCP/UI/IPC schemas and assertions; permitted pytest command below | 0 | Exact enums/422/unchanged saved value; payload refusal before side effects. |
| IR-4 generalization; IR-5 test rigor; AV-1–6 | partial | Audit scoped tests/diffs/Red receipts and probe real-library collaborators | manual | Functional assertions are substantive; library headers/logger were outside the mock observation boundary (F1/F2). No skip/expectation weakening found. |
| DR claim-to-state, architecture and freshness | partial | Compare actual delta, canon, dependency sources, receipts and independent identity | manual | Functional/gate claims agree; no-identifier claim fails (F1). |
| Pins, scope and line endings | pass | pins-scan.py --check; row-check.py red-unchanged; row-check.py scope-paths; eol-check.py | 0 | Zero problems in all four. |
| OpenAPI | pass | uv run --no-sync python tools/export_openapi.py --check openapi.committed.json | 0 | No drift. |
| Independent Python verification | pass | uv run --no-sync pytest -q --tb=short -p no:cacheprovider tests/unit/test_update_feed_config.py tests/unit/test_check_update_feed.py tests/unit/test_update_interval_setting.py tests/unit/test_ci_workflows.py tests/tooling/test_e2e_remote.py | 0 | 267 passed in 118.01s. |
| FEED_CHECK selftest | pass | uv run --no-sync python tools/check_update_feed.py --selftest | 0 | 10/10 ok. |
| Remote Green oracle | pass | uv run --no-sync python docs/execution/plans/2026-11-26-app-auto-update/run-check.py C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row17-run.txt --expect-green --require-main AC-174.15 --require-main AC-174.16 --install passed --require-install AC-174.19 --require-install AC-174.20 | 0 | Required main/install ACs passed; zero problems. |

### Test rigor audit

| Files audited | Rating | Basis |
|---|---|---|
| test_update_feed_config.py; test_check_update_feed.py; test_update_interval_setting.py | Strong | Real config/CLI/API assertions; reason/exit fixtures; strict refusal and persistence. |
| mcp-server/tests/update-interval-setting.test.ts | Strong | Exact resource enum/default, accepted inputs and rejected input with zero HTTP calls. |
| update-schedule.test.ts; app-updater.test.ts | Strong for scheduling/state/install; Adequate for library integration | Boundary/negative/sequence/counter assertions are meaningful; handcrafted updater omits the real header/logger defaults. |
| update-ipc.test.ts; updates-card.test.tsx | Strong | Real handlers/preload plus component events, exact payload/text/state, duplicate suppression. |
| app-running-nsh.test.ts; update-uninstall-nsh.test.ts; install-preconditions.test.ts; app-user-model-id.test.ts | Strong | Behavioral decoys and bad fixtures, zero-mutation preconditions, platform identity and startup order. |
| app-update.test.ts; update-roundtrip.test.ts | Strong | Local-feed positive/negative Electron behavior and real installed version/process/data/uninstall assertions. |
| Added test_e2e_remote.py cases and all named PIN_GROWTH files, login-item-nsh.test.ts | Strong | Real tool logic with fake transport, payload/exit negative cases; existing assertions preserved except named adaptations. |

## Verdict

**changes_required.** The update/feed/installed-round-trip functionality is supported by current evidence. F1 is a concrete additional outbound disclosure that contradicts the delivered privacy contract and must be corrected before approval. F2 is a non-blocking logging correction.

Preserve D-1543/D-1544 as Mat's open first-release decisions. Correct F1 without silently changing their recommended behavior; rerun affected real-library tests and the applicable gate, then request round 2 through execution-corrections. H2, the coordinator's canonical report copy and any commit remain subsequent work.


## Recheck (round 2)

**Workflow:** `/execution-critical-review`. **Reviewer:** codex-independent-reviewer (OpenAI/Codex), independent of the Anthropic author. **Date:** 2026-11-28. **Verdict:** approved. **Intent achieved:** yes.

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Corrections Applied

- **F1 / D-1591:** `ui/src/main/app-updater.ts:167–204` confines the electron-updater 6.8.11 adaptation to the named, typed `hardenUpdater()` function, called before configuration or checks. Its lazy nil UUID prevents `getOrCreateStagingUserId()` from creating `.updaterId`; its header wrapper removes `x-user-staging-id` before the existing merge. No custom request headers reintroduce it in the delivered wiring. The real-library test at `ui/tests/unit/app-updater.test.ts:794` observes six actual provider request options across two updater instances sharing scratch userData and checks that the file does not exist. An independent in-memory probe repeated that result with a running rc.5 version. UPDATER_CONFIG, Latest selection and checksum enforcement remain intact.
- **F2 / D-1592:** `ui/src/main/app-updater.ts:187` sets the library's logger to null. The installed library's public logger setter maps null to NoOpLogger (`ui/node_modules/electron-updater/out/AppUpdater.js:65`), including the constructor's error listener at :201. The real-library test at `ui/tests/unit/app-updater.test.ts:824` injects an HTTP error with query/profile markers and observes only `update: check failed kind=network`, with zero library console entries. The independent probe confirmed the same result.
- **D-1593:** the coordinator's canonical round-1 copy uses LF. This review preserves the original review body and writes this rolling report as UTF-8 LF. No product behavior changes with that conversion.
- **D-1594:** r10 remains a failed audit run. Its capture probe reproduces `CaptureFailedError: captured frame is black`; r11 subsequently passes the complete audit and full gate. No capture test was excused or weakened.

### Tested state and scope

**tested_state:** `5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221`.

Independently obtained with `uv run --no-sync python docs/execution/plans/2026-11-26-app-auto-update/identity.py --state-only`, ELECTRON_RUN_AS_NODE unset. It exactly matches r11 before/after and H1-6b; it does **not** differ for global-ignore access or any other reason. A Git command warns that the global ignore is inaccessible, and scope-paths sees one extra untracked path, but identity.py explicitly excludes the prohibited local-settings path. Neither that path nor the global ignore was opened.

The diff of testing snapshots `d7983dff3e7e` → `ac98b7272f61` across product/tooling trees contains only `hardenUpdater()`/its invocation and the appended real-library regression block/imports. Existing product and test assertions are unchanged. Independently running `row-check.py remote-run-2` binds the corrected run to snapshot `ac98b7272f61`: **63 product paths, 0 changed since the snapshot**. No claim here depends on rerunning Electron, an installer, the remote tool, a build, npm or Vitest.

### Q1 — Goal

**Accepted, intent achieved.** The functional proof accepted in round 1 remains valid and has been repeated with the corrected product: the schedule's three choices and retry/recovery boundaries (AC-174.1–2, .9–12), Latest-only selection (AC-174.3), background download/checksum/state/one notice (AC-174.4–6), Settings and explicit install order (AC-174.7–8, .12–13), and feed/check/manual-upload boundary (AC-173.1–5). The corrected run `r20261128T062757Z-ac98b72` records main **266/266** and install **2/2**, no failures, flakes or skips. F1's no-identifier mismatch and F2's raw logging are now independently resolved. No manual visual check replaces the scripted assertions. Mat's first feed release and open D-1543/D-1544 rulings remain outside this approval.

### Q2 — Feed and no-publish configuration

**Accepted.** FEED_BLOCK has exactly provider/owner/repo. DIST_NEVER_PUBLISHES is present in the package script and workflow build commands, with no token supplied to those build steps. The correction snapshot diff changes none of them. FEED_CHECK's reason/exit mapping and byte/hash/name/size/blockmap/config checks remain as approved. Its independently rerun selftest gives **10/10 ok**; retained row-3 evidence gives **feed-ok/0**, **feed-missing/10** and **sha512-mismatch/15** on the real build/changed copies. FEED_CHECKLIST orders checking before Mat's upload, names all three assets, describes Latest/pre-release and the one-time manual install, and leaves release/upload/probe commands explicitly with Mat. No agent upload action is accepted or authorized.

### Q3 — Schedule, setting, API and MCP

**Accepted.** UPDATE_SCHEDULE still implements inclusive 7-/30-day boundaries, the 24-hour retry, future clocks, Never and once-per-start pending-version recovery. UPDATE_TICK skips unreadable/unknown intervals without a default or store mutation. UPDATE_INTERVAL_LEAF remains weekly by default with exact-case weekly/monthly/never in all six layers; service validation rejects invalid HTTP values with 422, and UI/MCP enums are strict. The real-library helper's deliberately unused `readInterval: daily` does not pretend to test scheduling: it calls the explicit Check-now path; the original schedule tests cover scheduled behavior. OpenAPI drift independently exits **0**. D-1582 changes only the named new property set-back and its negative fixtures; tool/action lists do not grow.

### Q4 — Main-process updater and trust

**Accepted; F1/F2 fixed.** The adaptation is named, typed and bounded to one exact library version, with source-line references and real-library upgrade regression tests. The nil UUID is parseable by the library, and no installation-specific value is generated, stored or transmitted. Staged-rollout eligibility becomes deterministic; the approved feed has no staging percentage. This does not change the delivered Latest-only behavior.

UPDATER_CONFIG remains `[allowPrerelease=false, allowDowngrade=false, autoDownload=true, autoInstallOnAppQuit=false]`; the independent probe verifies those four values on all three instances, including an rc.5 version. No setFeedURL call or checksum bypass was added. The library's raw error logger is disabled before any check; UPDATE_QUIET_FAILURE's one classified line is now the sole log output observed under real-library failure. The original event/rejection handling, five-key UPDATE_STATE, malformed-store recovery, UPDATE_NOTICE_ONCE, ready/once guards and UPDATE_INSTALL_ORDER are unchanged. The memoized `shutdownForQuit()` still preserves before-quit's operation. Only update-install reaches install; there is no automatic restart. UPDATE_IPC and UPDATE_E2E_SEAM retain their strict payload and AVKIT_E2E gating.

**Trust matches the recommendation as built:** the public GitHub provider fetches over HTTPS, latest.yml supplies SHA-512, and no publisher signature authenticates the update. The unconditional Updates-card trust sentence states that model. This approval does not rule on D-1543 or D-1544.

### Q5 — Updates card

**Accepted.** UPDATES_CARD remains after Startup, uses the existing GridSelect/Button/theme tokens, saves the three-choice select through schedulePut, and shows the installed version and state-specific status. Check-now disabled states, ready-only Restart-and-update/jobs-stop note, pending-click ref and every-state trust sentence remain correct. An unknown state follows the idle/default rendering and offers no restart. No renderer code changed between the approved functional snapshot and corrected snapshot; the fresh gate covers its existing exact text/payload/state assertions.

### Q6 — Installer, host stage and round trip

**Accepted.** APP_RUNNING_CHECK still bounds the executable-path prefix with a separator, excludes its own PID, stops by PID only and refuses errors before file mutations; installed NSIS templates reach it in both installer and uninstaller. UNINSTALL_CACHE_RECURSIVE stays within the not-updated guard along with the two unchanged DeleteRegValue lines. HOST_PAYLOAD and INSTALL_STAGE_RULES retain pre-upload validation, no-payload behavior, failure/skip refusal, empty-account preconditions, ownership/quarantine, sibling-decoy survival and before/after equality. These product/tooling paths are unchanged between the two passing snapshots.

The corrected run's actual install report contains expected/passed AC-174.19 and AC-174.20, retry **0**, with **0 errors**. Its annotations record both bad-feed and good-feed installer GETs and `updater-cache-before=true`. The source at `ui/tests/e2e-install/update-roundtrip.test.ts:441–490` asserts checksum refusal/no restart before the successful click, old app/backend/MCP death at first new-version read, new process/backend health, setting/marker/Run-value retention, sibling survival and backend-stop log order. At :505–515 it calls the uninstaller and checks cache and both registry values before teardown. Passing these checks proves ROUND_TRIP and AC-174.20 at the corrected code; teardown is not supplying the uninstall result.

D-1578/D-1579 changed waiting/click mechanics only and retained the observable assertions; the snapshot diff confirms no further spec relaxation. D-1583 aligns startup's AppUserModelId with builder appId, NSIS shortcuts, login-item writes and toast identity (`com.avkit.app`). It fixes the sign-in read. An rc.5 user previously running under Electron's default identity may see taskbar grouping change to that intended identity; normal installer-created pins/toasts align with it, while arbitrary historical user-created pins are not exhaustively proven by this run. D-1584's one root-caused verification run proves this execution, not a reliability rate. These round-1 judgments stand.

### Q7 — Gate and pins

**Accepted.** The r4–r8 history remains explicit: format failure, two resource/load failures, authoritative-audit argv correction, then a complete pass. R5/r6 were not recast as passes; the isolation receipts and subsequent full gate support the diagnosis. No final assertion was weakened, timeout increased, test excused or suite deselected. Historical unrelated host load is supported by retained observations, not newly measured in this review.

R9 stops at line-endings; r10 stops at audit with **93/104**; r11 passes **all 33 steps** at exactly the independently reproduced state. Direct step receipts show UI **1803/1803** in **165** files, Python **3412**, MCP **560/560**, audit **104/104**, and remote-run-2 bound to ac98b72. The product snapshot comparison limits correction changes to D-1591/D-1592 and their added tests. Plan/receipt records identify D-1593's review-copy line endings; D-1594 records the environmental audit failure. Neither supplies a product-test waiver.

Independent PIN_GROWTH, red-unchanged and line-ending checks each report zero problems. The real-library regression assertions are unchanged from their valid Red. AC-61.18 remains intact; AC-114.2/.3 change only the row-13 expectations, with other listed pins preserved or enumerations grown as declared. Nothing about the scoped product is hidden by the reruns.

### Q8 — Safety and fidelity

**Accepted, within observed scope.** F1/F2's exceptions are closed. The review performs zero network requests, starts no app/backend/Electron/process decoy, reads no real app data, and mutates no repository file. HEAD is the baseline and the index is empty; snapshot commits are testing objects, not a moved branch. The correction diff changes no lockfile, version, feed/upload configuration, host script or installer macro. The added-package/licence assessment from round 1 stands: five added entries, no existing version changed, MIT/ISC additions; the pre-existing promoted argparse licence and lazy-val override remain disclosed, not silently reclassified. No remote licence lookup was made.

The independent EOL check covers **87 paths, 0 problems**, and scope-paths reports **0 problems**, accounting for concurrent Session 105. Receipts retain historical failures and some raw tool-generated profile paths; this report uses `<HOME>` and copies no personal email address or real-user content. No release/publish/tag/push/stash/revert action is evidenced in scope. Authorized transfers of test payloads to the E2E host are distinct from a public release upload. The handoff's corrected gate and run claims match the current receipts and tested state.

### Checklist Results — current round

All commands below exited 0. Python used PYTHONDONTWRITEBYTECODE=1, scratch TMP/TEMP, UV_OFFLINE=1, a scratch UV cache and --no-sync; ELECTRON_RUN_AS_NODE was unset. The complete full gate was inspected and reused at an exactly matching identity, not rerun. No Vitest run, build, install or host command was made by this reviewer.

| Check | Result | Command/procedure | Exit | Decisive evidence |
|---|---|---|---|---|
| Current state/freshness | pass | `uv run --no-sync python docs/execution/plans/2026-11-26-app-auto-update/identity.py --state-only` | 0 | Exact r11 identity above; no global-ignore discrepancy. |
| F1/F2 real collaborators | pass | `node C:/Temp/av-kit/2026-11-26-app-auto-update/exec-review/probe.cjs` | 0 | Two starts, six feed requests, two Latest requests, no staging header/file; one sanitized failure line, no library console output. |
| Red validity / IR-4, IR-5 | pass | Read the two exact c1 failed assertions, appended tests, installed library, Green/type/lint receipts; rerun `row-check.py red-unchanged` | 0 | Valid Red: 2 failed, 35 passed; Green: 66 passed; red-unchanged: 0 problems. Both fail on the pre-fix defaults of the real library, not fixture/import errors. |
| Runtime/IR-1, IR-7 | pass | `uv run --no-sync python docs/execution/plans/2026-11-26-app-auto-update/run-check.py C:/Temp/av-kit/2026-11-26-app-auto-update/aau-row17-run.txt --expect-green --require-main AC-174.15 --require-main AC-174.16 --install passed --require-install AC-174.19 --require-install AC-174.20` | 0 | Required main/install ACs pass; 0 problems. |
| Snapshot binding | pass | `uv run --no-sync python docs/execution/plans/2026-11-26-app-auto-update/row-check.py remote-run-2` | 0 | Corrected run ac98b72; 63 product paths, 0 changed. |
| Pins, scope, EOL | pass | `pins-scan.py --check`; `row-check.py scope-paths`; `eol-check.py` through `uv run --no-sync python` | 0 | Every check: 0 problems. |
| Boundary/OpenAPI / IR-3, IR-6 | pass | Source/test audit and `uv run --no-sync python tools/export_openapi.py --check openapi.committed.json` | 0 | No drift; original exact-case/refusal/persistence assertions remain. |
| Feed negative oracles | pass | `uv run --no-sync python tools/check_update_feed.py --selftest` | 0 | 10/10 ok, all reason families exercised. |
| Full gate claims | pass | Manual comparison of both handoffs, r11 and step receipts, historical failed runs, corrected install report and snapshot diff; observer codex-independent-reviewer | manual | All 33 steps pass; current identity equals before/after; no exclusions added. |

The two new tests are **Strong**: each uses the real NsisUpdater/provider boundary, exact outputs and a real pre-fix assertion failure. F1 checks requests across separate starts and absence of persistence; F2 captures all console methods plus the controller logger after a marker-bearing HTTP rejection. The equal-version fixture deliberately avoids downloading, so it is proof of feed privacy/logging, not a replacement checksum test. Existing local-feed E2E and the installed wrong-hash round trip provide that latter proof. The prior test-rigor table stands with its library-integration limitation resolved by these additions.

```json
{"schema_version":"evidence.v1","check_id":"review-r2-real-library","command":"node C:/Temp/av-kit/2026-11-26-app-auto-update/exec-review/probe.cjs","cwd":"P:/av-kit","scope":"F1 UPDATER_CONFIG/UPDATE_TICK; F2 UPDATE_QUIET_FAILURE; actual NsisUpdater and GitHub provider with in-memory executor and scratch data","phase":"targeted","exit_code":0,"result":"pass","tested_state":"5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221","output":"states=[idle,idle]; feedRequests=6; latestRequests=2; stagingHeader=false; updaterIdFile=false; libraryConsoleCalls=0; logs=[update: check failed kind=network]; flagsUnchanged=true; networkRequests=0"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r2-state","command":"uv run --no-sync python docs/execution/plans/2026-11-26-app-auto-update/identity.py --state-only","cwd":"P:/av-kit","scope":"independent current D6 identity, ELECTRON_RUN_AS_NODE unset","phase":"targeted","exit_code":0,"result":"pass","tested_state":"5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221","output":"Exactly equals gate r11 before/after: 5e4ec2fd9debecdfbafb4cf02e36cc5f2f88ded9+e2c303d189d33a0c08fca2736e76781cb9344b8c574cd5569f273a896fd04221"}
```

### Verdict

**approved.** F1 and F2 are fixed against the real library, the goal is achieved, and there are no new findings or open blockers. Approval covers the delivered work and its scripted proof. D-1543/D-1544 and Mat's first feed release remain his decisions. This report does not authorize committing, pushing, tagging, releasing or uploading. H1-7a/H1-7b and H2 remain the coordinator's subsequent work; completion-preflight was applied to this read-only review deliverable, without claiming the whole session's closeout is done.
