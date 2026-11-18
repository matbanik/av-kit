---
project: "2026-11-17-ui-small-fixes"
date: "2026-11-17"
source: "grouping .agent/context/grouping/2026-11-17-value-triage-session-grouping.md §3 Session 94; issues HELP-F1-BEFORE-LAZY-MOUNT-LOST (D-1128, MEU-158), DOWNLOADER-ADVANCED-PANEL-GAP (D-1129, MEU-159) and UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT (D-1130, no MEU)"
meus: ["MEU-158", "MEU-159"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
---

# Implementation Plan: F1 waits for the page, the Advanced gap closes, and preview clears ELECTRON_RUN_AS_NODE

> **Project**: `2026-11-17-ui-small-fixes`
> **Build Plan Section(s)**: 06 §F1 help waits for the page (residual) (MEU-158, matrix 6.22, `docs/build-plan/06-gui.md:1710-1721`, anchor `help-f1-after-mount-residual`); 11 §Downloader Advanced gap (residual) (MEU-159, matrix 11.14, `docs/build-plan/11-page-layout.md:172-188`, anchor `downloader-advanced-gap-residual`), with 11 §Downloader page layout (MEU-53) as its parent canon; the preview script has no MEU (D-1130) and follows the Session 90 dev-script contract (`ui/scripts/electron-vite-dev.mjs`). Both MEUs are registered `pending` in band P2 already (`us94-probe.txt`); this plan does not register them again.
> **Status**: said to execute (USER_EXPLICIT 2026-11-17 "orchestrate the plan creation for all sessions and proceed with execution for each"). `plan_to_exec_gate: human`: that message is the execution approval once the plan review approves; the plan review was approved at round 2 (.agent/context/handoffs/2026-11-17-ui-small-fixes-plan-critical-review.md). Session 94 is the last session of the value-triage grouping (D-1133: 74, 91, 92, 93, 94); it runs after Session 93 is committed.

---

## Goal

**Goal anchor:** one F1 pressed while the lazy Convert or Capture page is still loading opens that page's help panel once when it mounts, never toggles another page's panel, and is dropped if the user leaves first; with Advanced collapsed or expanded on the Downloader page the queue starts one standard gap (16 px) below the disclosure at 1280×800 and at 700 px, and Advanced still shows its eight controls in the same order; `npm run preview` with `ELECTRON_RUN_AS_NODE` set clears it, says so on stderr and opens the app window, as `npm run dev` does; each fix is proved by an Electron E2E test or a script proof in the gate, with no network and no manual check.

**Why.**

- **MEU-158.** On a help route F1 dispatches `av-kit:help:toggle-local` at once (`AppShell.tsx:203-215`, `settings-commands.ts`), and all six shell routes are help routes (`AppShell.tsx:206`). The Convert and Capture pages are lazy routes (`router.tsx:50`, `:57`), and their `HelpCard` adds its listener only when it mounts (`HelpCard.tsx:65-73`, the line at `:69`). An F1 pressed while the chunk loads is lost, and a second F1 is needed (`HELP-F1-BEFORE-LAZY-MOUNT-LOST`, `known-issues.yaml:5656`, D-1128; found in Session 89's plan and left out of MEU-157). A second effect follows from the same code: while the Convert chunk loads, the router can keep the old page mounted, so the toggle can reach the Downloader's card instead (row 1a measures whether it does).
- **MEU-159.** An empty gap sits under the Advanced disclosure on the Downloader page; it shows in the README's main screenshot (`DOWNLOADER-ADVANCED-PANEL-GAP`, `known-issues.yaml:3463`, D-1129). The register says "Cause not established", so 11's Cause row asks the plan to measure it before any change.
- **Preview.** Session 90 gave `npm run dev` a wrapper that drops `ELECTRON_RUN_AS_NODE` (`ui/scripts/electron-vite-dev.mjs`, `ui/package.json:16`). `npm run preview` still runs `electron-vite preview` directly (`ui/package.json:18`), so with the variable set Electron starts as Node and no window opens, silently (`UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`, `known-issues.yaml:5689`, D-1130; `.agent/docs/commands.md:80`).

**The rulings that bind this plan.** D-1128 (MEU-158: "the help toggle is held until the page's HelpCard listens, using the holding pattern MEU-157 built for Ctrl+O"), D-1129 (MEU-159: "the element that holds the space is found and the gap removed, proved by an Electron layout check; the README screenshot is retaken only if Mat asks") and D-1130 ("TECH-DEBT P4, no MEU: give preview the same wrapper Session 90 gave dev"). They are triage decisions on the three issues, re-read at plan time (`issues.txt`). Mat, 2026-11-16: "why are you giving me e2e tests manually! This should be done with framework and scripts! It delays the development!", so there is no human check row.

**What the code shows (plan-time reads at `HEAD` `ecfa3f3`, clean tree, one worktree; row 0 re-reads every citation on the tree it runs on):**

- **The F1 path.** `onHelpToggle` (`AppShell.tsx:203-215`) defines `helpRoutes = ['/', '/transcript', '/tts', '/convert', '/capture', '/settings']`. Off those routes it calls `queueToggleAfterNavigate()` (which sets the sessionStorage key `HELP_PENDING_TOGGLE_KEY = 'av-kit:help:pending-toggle'`) and `navigateShell('/settings')`; on them it calls `HELP_COMMANDS.toggle()`, which dispatches `new CustomEvent('av-kit:help:toggle-local')` with no detail and is not cancelable. `HelpCard` reads the pending key once on mount (`HelpCard.tsx:54-63`) and adds the toggle listener in an effect with no dependencies (`:65-73`); every mounted card toggles on every event. The card's `feature` prop is one of `downloader`, `transcript`, `tts`, `settings`, `converter`, `capture`, and its collapse state is kept in `localStorage` under `av-kit:<feature>-help:<tabKey>:state` (first visit: collapsed).
- **MEU-157's held delivery** (`convert-commands.ts:348-400`, Session 89, 06 Delivered note at `06-gui.md:1702-1708`). One module variable, `browseRequest`, is the outstanding Browse request, made as a token at press time; a second press joins it; a `hashchange` listener added with the token drops it when the hash leaves Convert (`dropBrowseOffConvert`, `isConvertHome()`); the run dispatches the cancelable `CONVERT_BROWSE_EVENT`, and a request no page received while still on Convert is held; `takeHeldBrowse()` (read on mount at `ConvertPage.tsx:515`) takes a held or still-waiting request once. 06's MEU-158 Shared row asks the plan to check whether this can serve both chords and to keep one mechanism if it can.
- **Navigation.** `navigateShell(path)` (`lib/shell-nav.ts`) sets the hash and dispatches a `hashchange`; `shell-nav.ts` already holds the shell's small shared helpers (`COLLAPSE_RAIL_EVENT`, `TOGGLE_CONSOLE_EVENT`, `requestCollapseRail`).
- **The Downloader layout.** The page `section` is `flex h-full min-h-0 flex-col gap-4 p-4` (`DownloaderPage.tsx:564`); its scroller is `flex min-h-0 flex-col gap-4 overflow-auto` (`:573`) and holds the `HelpCard` (`:574`), the add form, whose last child is the Advanced `Disclosure` (`id="downloader-add-advanced"`, `:668-815`; the form ends at `:816`), which renders a plain `section` holding `add-advanced-toggle` and a panel `div` with `id="downloader-add-advanced-panel"`, `hidden` while collapsed with its children kept in the DOM (`Disclosure.tsx:26-44`); and the status wrapper `<div className="min-h-6 max-w-[var(--layout-page-max-width)]">` (`:818`) with the `add-status` and `error-banner` paragraphs. Each paragraph is always in the DOM: with its text when it has one, else as an empty `hidden` placeholder (`:824`, `:831`). So a wrapper with no message still holds both test ids, and an empty status is told by the absence of shown text, never by a missing child. The queue region (`download-queue-region`, `flex min-h-[20rem] flex-1 flex-col gap-2`) follows the scroller. So when both messages are empty the wrapper still takes `min-h-6` (24 px) plus one `gap-4` (16 px) at the scroller's end: the plan's hypothesis is that this 40 px is the gap. Row 3 measures it before any change (11 Cause row); if another element holds the space, that is S9.
- **The Advanced panel's ids.** In panel DOM order: `sabr-status`, `sabr-check-btn`, `sabr-force-btn`, `sabr-clear-btn` (`DownloaderPage.tsx:681-691`), `cookie-browser` (`:722`), `cookie-profile` (`:747`), `cookie-file` (`:768`), `cookie-test-btn` (`:797`). All eight are in the DOM in every cookie mode, collapsed or expanded. Which are shown depends on the mode: the four SABR ids and `cookie-test-btn` always; `cookie-browser` (its `label`, `:719`) and `cookie-profile` (`:748`) only in `browser` mode; `cookie-file` (its wrapper, `:766`) only in `file` mode (`cookie-bar.ts:78-83`). So an expanded panel shows five in `none` mode, seven in `browser` and six in `file`. The mode is the checked `cookie-mode-<mode>` radio (`SegmentedControl.tsx:48-54`); it starts at `none` (`DownloaderPage.tsx:218`) and follows the saved settings. This session changes none of it, and no check here clicks a cookie mode.
- **The preview script.** `electron-vite-dev.mjs` exports `DEV_NOTICE = 'electron-vite-dev: cleared ELECTRON_RUN_AS_NODE'`, `devEnv(base)`, `devArgs(extra)`, `isEntry(argv1, moduleUrl)` and `exitCodeFor(code, signal, platform)`; a private `main()` spawns `process.execPath` with `devArgs`, stdio inherited, `devEnv(process.env)` and the `ui` folder as cwd, ignores SIGINT and SIGBREAK, forwards SIGTERM, prints `electron-vite-dev: could not start electron-vite: …` and exits 1 on a spawn error, and exits with `exitCodeFor(…)`; the file ends `if (isEntry(process.argv[1], import.meta.url)) main()`. `dev-script.test.ts:63` pins `scripts.dev` and `:64` pins `scripts.preview` as `'electron-vite preview'`, the one expectation this plan changes (`PINS_NAMED`).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and ui/graphify-out/ are absent from P:/av-kit (us94-probe.txt, 2026-11-17). The change touches one shell helper module, two command modules, the help card, one page line, two dev scripts and the package script, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go under `C:/Temp/av-kit/ui-small-fixes/`, named `us-*` (planning receipts are `us94-*`).
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE` (Session 88 RULE-3), except where `preview-proof.py` sets it on purpose for the child it starts.
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`. Playwright runs with `ELECTRON_RUN_AS_NODE` cleared and `TMP` and `TEMP` at `C:/Temp/av-kit/ui-small-fixes/tmp`.
  - Each Electron test launches through `launchElectron` (`ui/tests/e2e/electron-app.ts:70`) with a scratch `AVKIT_APP_DATA` and stops the backend it started only by the pid it recorded, checked against that pid's start time. `preview-proof.py` stops only the process tree it started, by recorded pid. No row stops a process by image name; other worktrees and Mat's own app run on this host.
  - Shared-host Electron rules: an Electron step runs only after the host-load probe reads 50 % or less; a receipt holding `unhandled rejection:` is a failure; a failure with no recorded cause is rerun alone once (S5) and never retried into a pass; no timeout is raised and no retry is added.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local (Electron and the real backend; grouping §3 "Cloud/local: local (Electron E2E)").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), run by the coordinator, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `us-plan-2026-11-17-ui-small-fixes` and `us-execution-2026-11-17-ui-small-fixes`.
  - Caps come from `.agent/review-limits.json` (plan 3 rounds, execution 6, token budgets off). This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
  - Each dispatch writes its own run log `us-exec-run-r<n>.txt`; the console goes to its own `us-exec-console-r<n>.txt`, never into the run log (redirecting into the run log loops), and the row reads both tails (Session 88 RULE-2).
- **Queue:** this plan is written against `HEAD` `ecfa3f3` and runs after Sessions 74, 91, 92 and 93 have each committed, so `HEAD` will have moved. Row 0 pins every baseline on the tree it runs on and re-reads every citation (§Sibling overlap); a moved citation is corrected in the handoff (Session 51 RULE-3), not a blocker.
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. The coordinator commits after the execution review approves. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-158 F1 help waits for the page | `.agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-158-handoff.md` |
| MEU-159 Downloader Advanced gap | `.agent/context/handoffs/2026-11-17-ui-small-fixes-MEU-159-handoff.md` |
| Preview script (no MEU) | `.agent/context/handoffs/2026-11-17-ui-small-fixes-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-17-ui-small-fixes-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-17-ui-small-fixes-implementation-critical-review.md`

Every AC family (AC-158, AC-159 and the plain AC-1 to AC-5) must appear in every handoff (`validate_closeout_artifacts.py` AC coverage), so each handoff carries one cross-reference row per family it does not own.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local checkers (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `baseline-citations.txt`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py`, `preview-proof.py`, `load-run.py`, `host-wait.py` |
| WP-2 | MEU-158 unit Red, the chunk probe, Electron Red, then Green (rows 1, 1a, 1b and 2) | WP-1 | shared | `createHeldRequest` and `currentRoute` in `shell-nav.ts`, `BROWSE_HOLD` on the helper, `HELP_HOLD`, `HELP_ROUTE_SCOPE`, `HELP_TAKE_ON_MOUNT`, `help-f1-hold.test.tsx`, `help-f1-mount.test.ts` |
| WP-3 | MEU-159 measurement, Electron Red, then Green (rows 3, 3a and 4) | WP-2 | shared | The measurement receipt, `STATUS_SLOT` in `DownloaderPage.tsx`, `downloader-advanced-gap.test.ts` |
| WP-4 | Preview Red, then Green (rows 5 and 6) | WP-3 | shared | `runElectronVite`, `electron-vite-preview.mjs`, the package script, the named pin, `preview-script.test.ts`, the proofs |
| WP-5 | Electron proof (row 7) | WP-4 | shared | The 20-run repeat receipt and the suite runs |
| WP-6 | Canon, issues and status (row 8) | WP-5 | shared | 06 and 11 Delivered notes, `commands.md:80`, three issues resolved, both MEUs `ready_for_review`, grouping §6 row 94 |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The three handoffs, the review, the reflection, the commit draft, the closing prompt |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.** Two decisions are briefs (D-1176 and D-1177, §Decision Log): whether F1 meant for the page that is loading may still toggle the page you left, and how the Downloader gap is closed. Your hand-over ('orchestrate the plan creation for all sessions and proceed with execution for each', 2026-11-17, continuing 'like we did here. But use the new HDP process.', 2026-11-15) settles them on the recommendation, and they are recorded that way. Read them if you want to overrule one before execution. There is no human check row: Electron tests and a script proof in the gate prove each fix.
>
> **What changes for you:**
>
> - Pressing **F1** right after you switch to Convert or Capture now opens that page's help panel every time, even while the page is still loading. Pressing F1 twice while it loads opens it once. If you leave before the page appears, nothing toggles later. The page you left keeps its help panel as it was. On a page that is showing, F1 works as it does now.
> - On the **Downloader**, the empty band under **Advanced** is gone: the queue starts one normal gap below it, collapsed or expanded. This holds on a fresh page. Nothing clears the message line once it has text, so after the first add message ("Adding — waiting for backend...", "Queued N job(s). Click Start to download.", "Add returned no new jobs..." or "URL is required") or a SABR or cookie error, the line stays in the place it has today and the queue sits one line plus a gap lower for the rest of the session.
> - **`npm run preview`** now opens the app even when `ELECTRON_RUN_AS_NODE` is set, and prints one line saying it cleared it, as `npm run dev` does.
> - The README screenshot is not retaken unless you ask (D-1129).

## Proposed Changes

### Single-statement contracts

- **`HELD_REQUEST` (D-1175):** `ui/src/renderer/src/lib/shell-nav.ts` (LF) gains `createHeldRequest(stillHome: (key: string) => boolean)`, which returns `{ begin(key), isCurrent(token), settle(token, unreceived), take(key) }` over one closure variable, the outstanding request `{ key, held } | null`. `begin(key)`: if a request with the same key is outstanding (waiting or held) it returns `null` (the press joins it); otherwise it replaces any request with another key, creates a new token, adds one `hashchange` listener that clears the request and removes itself as soon as `stillHome(token.key)` is false, and returns the token. `isCurrent(token)` is `outstanding === token`. `settle(token, unreceived)`: if the token is current, it sets `held = true` when `unreceived && stillHome(token.key)`, and otherwise clears the request and its listener. `take(key)`: if a request with that key is outstanding, held or waiting, it clears it with its listener and returns `true`; otherwise `false`. Renderer memory only, never persisted.
- **`CURRENT_ROUTE` (D-1175):** `currentRoute()` in `shell-nav.ts` returns the hash without its `#` and before any `?`, or `'/'` when the hash is empty.
- **`BROWSE_HOLD` on the helper (D-1175):** `convert-commands.ts` (CRLF) keeps `deliverPaletteBrowse`, `takeHeldBrowse`, `CONVERT_BROWSE_EVENT`, `isConvertHome` and their behaviour, but keeps its outstanding request in one `createHeldRequest((key) => key === '/convert' && isConvertHome())` instance instead of the module variable and its own listener: a press calls `begin('/convert')` (a `null` result joins), the run returns unless `isCurrent(token)`, dispatches the cancelable event and calls `settle(token, notPrevented)`; `takeHeldBrowse()` is `take('/convert')`. No export is added or removed, and `convert-browse-hold.test.ts`, the Convert page tests and `convert-browse-mount.test.ts` pass unchanged (AC-158.13, AC-158.14).
- **`HELP_HOLD` (D-1175, D-1176):** `HELP_COMMANDS.toggle()` in `settings-commands.ts` (CRLF) reads `route = currentRoute()`, calls `begin(route)` on its own `createHeldRequest((key) => currentRoute() === key)` instance and returns if the press joined (`null`); otherwise it dispatches `new CustomEvent('av-kit:help:toggle-local', { cancelable: true, detail: { route } })` and calls `settle(token, notPrevented)` at once. So an F1 that a mounted card receives is never held, one that no card receives on that route is held, and a second F1 while one is held joins it. `takeHeldHelpToggle(route): boolean` is that instance's `take(route)`. `HELP_FEATURE_ROUTE` maps the card features to their routes: `downloader` `'/'`, `transcript` `'/transcript'`, `tts` `'/tts'`, `settings` `'/settings'`, `converter` `'/convert'`, `capture` `'/capture'`. `queueToggleAfterNavigate`, `HELP_PENDING_TOGGLE_KEY` and the off-route path are unchanged, and `AppShell.tsx` is not edited.
- **`HELP_ROUTE_SCOPE` (D-1176):** `HelpCard.tsx` (LF) handles a toggle event with no `detail.route` as today (it toggles). With a route, a card whose `HELP_FEATURE_ROUTE[feature]` equals it calls `preventDefault()` and toggles; a card on another route ignores it. So an F1 meant for Convert never toggles the Downloader card the router still shows while the Convert chunk loads: TanStack Router keeps the old page mounted for up to `defaultPendingMs` (1 000 ms) before it shows the pending skeleton (`ui/node_modules/@tanstack/router-core/dist/esm/router.js:631`, `load-client.js:690-719`). A card's route comes only from the fixed `HELP_FEATURE_ROUTE[feature]` map, never from reading the hash when the card mounts, because a page can mount after a later navigation and the hash would then name the wrong route (AC-158.6).
- **`HELP_TAKE_ON_MOUNT` (D-1175):** the listener effect (now on `[feature]`) adds the listener first and then runs `if (takeHeldHelpToggle(HELP_FEATURE_ROUTE[feature])) setExpanded((v) => !v)`; the route it takes is the map's, not `currentRoute()`. Under StrictMode's double effect (React 19, `main.tsx`) the first run takes the request and the second finds none, so one F1 toggles once. The literal `'av-kit:help:toggle-local'` and the sessionStorage pending path stay.
- **`HELP_DROP` (D-1176):** a held F1 is dropped when the hash leaves its route, by the helper's `hashchange` listener, so a card mounted on a later visit does not toggle.
- **`STATUS_SLOT` (D-1177; applied only if row 3 confirms the hypothesis):** the status wrapper at `DownloaderPage.tsx:818` (bare LF) gets `hidden={!addStatus && !error}` (the state names are re-read at row 0; the attribute uses whatever two values decide whether `add-status` and `error-banner` render). Its class, its children and both test ids are unchanged. When either message shows, the wrapper shows as today. Nothing clears either message (`DownloaderPage.tsx:228`, the only `setAddStatus` calls at `:355-377`, errors kept at `:297-299` and `:401-408`), so the band is closed on a fresh page only: once any message has shown, the line stays with its text and the queue sits one line plus a gap lower for the rest of the session, as today.
- **`PREVIEW_WRAPPER` (D-1178):** `electron-vite-dev.mjs` (LF) exports `runElectronVite(command, notice, extra)`, the body of today's `main()` with the subcommand, the notice and the error prefix (`'electron-vite-' + command + ': could not start electron-vite: '`) as parameters; `main()` becomes `runElectronVite('dev', DEV_NOTICE, process.argv.slice(2))`. Every existing export and its behaviour stay. A new `ui/scripts/electron-vite-preview.mjs` (LF) exports `PREVIEW_NOTICE = 'electron-vite-preview: cleared ELECTRON_RUN_AS_NODE'` and `previewArgs(extra)` (`[the electron-vite bin, 'preview', ...extra]`, the same bin path as `devArgs`), imports `devEnv`, `isEntry` and `runElectronVite` from `./electron-vite-dev.mjs`, and ends `if (isEntry(process.argv[1], import.meta.url)) runElectronVite('preview', PREVIEW_NOTICE, process.argv.slice(2))`. Importing either module starts nothing. `ui/package.json:18` (CRLF) becomes `    "preview": "node ./scripts/electron-vite-preview.mjs",`.
- **`PINS_NAMED` (D-1178):** exactly one existing test expectation changes, edited at Red in row 5: `ui/tests/unit/dev-script.test.ts:64`, in the test titled "devArgs, isEntry, exitCodeFor and the package scripts" (`:41`). Old: `expect(pkg.scripts.preview).toBe('electron-vite preview')`. New: `expect(pkg.scripts.preview).toBe('node ./scripts/electron-vite-preview.mjs')`. `:63` (the dev script) is unchanged. Every other pin passes unchanged.
- **`COMMANDS_DOC` (D-1178):** `.agent/docs/commands.md:80` (CRLF), the `npm --prefix ui run preview` row, changes from "**Silent**, as `dev` was. Tracked as `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`." to the same wording the dev row uses for a cleared variable (row 8 re-reads the dev row and copies its form).
- **`SERVICES_KEPT`:** no Python, API route, OpenAPI document, MCP tool, persisted setting or database schema changes.

### MEU-158: F1 help waits for the page

1. Add `HELD_REQUEST` and `CURRENT_ROUTE` to `shell-nav.ts`.
2. Move `BROWSE_HOLD` in `convert-commands.ts` onto one helper instance; delete the module variable, `clearBrowseRequest` and `dropBrowseOffConvert` only where the helper now does their work, and keep every export.
3. Add `HELP_HOLD`, `takeHeldHelpToggle` and `HELP_FEATURE_ROUTE` to `settings-commands.ts`.
4. Add `HELP_ROUTE_SCOPE` and `HELP_TAKE_ON_MOUNT` to `HelpCard.tsx`.
5. Row 8 adds a Delivered (Session 94) note to 06 before `## Validation Commands` (`06-gui.md:1723`), in the form of the Session 89 note at `:1702-1708`.

### MEU-159: Downloader Advanced gap

1. Row 3 measures the gap on the unchanged build (§Verification Plan 2b) and records the element that holds it.
2. If the measurement matches the hypothesis (the empty status wrapper), apply `STATUS_SLOT`. If not, S9.
3. Row 8 adds a Delivered (Session 94) note to 11 before `## Supersession` (`11-page-layout.md:190`), with the measured cause and the limit: the band is closed on a fresh page; once a message has shown, the line stays where it is today.

### Preview script (no MEU)

1. Row 5 edits the named pin and writes `preview-script.test.ts`, and runs the base proofs.
2. Row 6 applies `PREVIEW_WRAPPER`.
3. Row 8 applies `COMMANDS_DOC`.

### Test pins

Each pin is cited by file, line and description (Session 83 RULE-1: no other family's AC ids are copied here as this plan's).

| Pin | What it checks | After this change |
|---|---|---|
| `ui/tests/unit/dev-script.test.ts:64`, in the test "devArgs, isEntry, exitCodeFor and the package scripts" (`:41`) | `scripts.preview` is `'electron-vite preview'` | **Changes (named).** New: `'node ./scripts/electron-vite-preview.mjs'`. Edited at Red (row 5) |
| `ui/tests/unit/dev-script.test.ts:30` and the rest of `:41-…` | `devEnv`, `devArgs`, `isEntry`, `exitCodeFor`, `scripts.dev` | Unchanged; must pass after the `runElectronVite` refactor (AC-5) |
| `ui/tests/unit/help-card.test.ts` (CRLF) | The card's render, persistence, search and toggle on a detail-less event | Unchanged (a detail-less event still toggles) |
| `ui/tests/unit/convert-browse-hold.test.ts` | The Ctrl+O hold's join, drop, take and acknowledgement | Unchanged; must pass on the helper (AC-158.14) |
| `ui/tests/unit/convert-page.behavior.test.ts`, `convert-page.test.ts`, `convert-commands.test.ts` | The page's browse take on mount, the command module | Unchanged |
| `ui/tests/unit/common-shortcuts.test.tsx`, `header-toggles.test.ts`, `palette-curation.test.tsx`, `gui-actions-audit.test.ts`, `shortcuts.test.ts`, `capture-page.test.ts` | F1's chord, hint and palette entry; the header help toggle | Unchanged |
| `ui/tests/e2e/keyboard-shortcuts.test.ts:68-105` (F1 on a mounted page) | F1 toggles the mounted page's card | Unchanged |
| `ui/tests/e2e/help-search.spec.ts` | The help card and its search on the mounted Downloader | Unchanged |
| `ui/tests/e2e/convert-browse-mount.test.ts` | Ctrl+O while the Convert chunk loads opens one picker | Unchanged; 20 of 20 (AC-158.13) |
| `ui/tests/e2e/convert-queue.test.ts:1568` ("browses on Convert and is inert") | Ctrl+O right after the switch picks one file | Unchanged; 20 of 20 (AC-158.13) |
| `ui/tests/unit/downloader-page.test.ts:519-555` | The Downloader layout classes (its `overflow-auto…<QueueList` match lands at `:895-896`) | Unchanged: no class changes |
| `ui/tests/unit/downloader-page.behavior.test.ts`, `layout-canon.test.ts`, `layout-primitives.test.ts` | Add status, error banner, layout canon | Unchanged (AC-159.6) |
| `ui/tests/e2e/download-queue.test.ts` (its 700 px case at `:1574`), `ui/tests/e2e/layout-primitives.test.ts` | The Downloader in the real app | Unchanged (AC-159.6) |

Any other existing test that fails after a Green is S5, an M-7 question, not a fix.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `av-kit:help:toggle-local` | `settings-commands.ts` | A `CustomEvent`, now `cancelable: true` with `detail: { route: string }`; a card on that route calls `preventDefault` | A detail-less event still toggles every card |
| The help hold and the browse hold | `shell-nav.ts` (`createHeldRequest`) | One `{ key, held }` per instance and one `hashchange` listener; renderer memory only | Not persisted, not sent anywhere |
| The Downloader status wrapper | `DownloaderPage.tsx` | `hidden` when both messages are empty | No test id or class changes |
| `npm run preview` | `ui/package.json`, `ui/scripts/electron-vite-preview.mjs` | Child env without `ELECTRON_RUN_AS_NODE`; one stderr notice when it was set; the child's exit code | Extra CLI arguments pass through to `electron-vite preview` |

No API route, OpenAPI document, MCP tool shape, backend service, persisted setting or database schema changes (M-4 kept clear). The new event detail is a renderer-internal event with one producer and one consumer in this repo.

### Acceptance Criteria

- **Families.** MEU-158 uses AC-158.1 to AC-158.14 and MEU-159 uses AC-159.1 to AC-159.7. The preview fix has no MEU, so it numbers its ACs AC-1 to AC-5, the session-local convention Session 90 (`2026-11-17-test-run-reliability`) used. Older titles `AC-1 ` to `AC-5 ` exist in `ui/tests/unit/e2e-harness.test.ts` and `ui/tests/e2e/electron-harness.test.ts`, so `red-check.py` reads only targeted receipts that hold this plan's files, never the full Vitest receipt.
- **Titles.** Vitest and Playwright titles start `AC-158.<n> `, `AC-159.<n> ` or `AC-<n> ` followed by a space, so `--require AC-158.1` never matches `AC-158.10`.
- **New names fail by assertion at Red.** `help-f1-hold.test.tsx` imports `shell-nav.ts` and `settings-commands.ts` as namespaces (`import * as nav …`, `import * as sc …`), and AC-158.1 to AC-158.6 assert `typeof nav.createHeldRequest === 'function'` or `typeof sc.takeHeldHelpToggle === 'function'` first. `preview-script.test.ts` asserts `existsSync(PREVIEW_SCRIPT)` first, loads the scripts by dynamic import, and asserts `typeof dev.runElectronVite === 'function'` first. So no Red fails by a missing export or a module-not-found error (Session 52 RULE-4).
- **Guards pass at Red:** AC-158.7, AC-158.12 and AC-159.5. AC-158.11 is recorded at Red, not required (at Red the F1 is lost, but the Downloader card can toggle).
- **Electron tests** fail at Red by a plain `expect(value).toBe(…)` on a value read after a signal and a fixed settle, never `expect.poll`; a precondition that the page has not yet mounted throws `Error('setup: …')`, which `red-check.py` refuses, so a fast load never passes for a Red.
- **AC-158.13, AC-158.14, AC-159.1, AC-159.6, AC-159.7, AC-3, AC-4 and AC-5 are checks** run by rows 2, 3, 4, 5, 6, 7 and the gate, not test titles.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-158.1 | unit | `createHeldRequest(stillHome)`: `begin('/x')` returns a token; a second `begin('/x')` returns `null` (join); `settle(token, true)` with `stillHome` true holds it; `take('/x')` returns `true` once and then `false`; `settle(token, false)` clears it, so `take` returns `false`. | Local Canon (06 Held, Once, Shared rows; `HELD_REQUEST`) | In Red `createHeldRequest` is not a function |
| AC-158.2 | unit | The helper's edges: with a held `/x` request, a `hashchange` to `#/y` clears it (`take('/x')` false) and removes the listener (a later `hashchange` back to `#/x` does not resurrect it); `begin('/y')` while `/x` is outstanding replaces it (`isCurrent(old)` false, `take('/x')` false); `settle(staleToken, true)` after a replacement holds nothing; `currentRoute()` gives `'/'` for an empty hash, `'/convert'` for `#/convert?x=1`. | Local Canon (06 Once row; `HELP_DROP`, `CURRENT_ROUTE`) | In Red the names are missing |
| AC-158.3 | unit | Hash `#/convert`, no card mounted: `sc.HELP_COMMANDS.toggle()`; then render `<StrictMode><HelpCard feature="converter" …/></StrictMode>`: the card's button reads `aria-expanded="true"` after one render flush, and `sc.takeHeldHelpToggle('/convert')` returns `false`. | Local Canon (06 Held row: "toggles the help panel once when it mounts") | In Red the card is collapsed |
| AC-158.4 | unit | Two `toggle()` calls before the mount, then the StrictMode render: `aria-expanded="true"` (one toggle, not two). | Local Canon (06 Once row) | In Red the card is collapsed |
| AC-158.5 | unit | `toggle()` on `#/convert`, then the hash goes to `#/` (with its `hashchange`) and back to `#/convert`, then the render: `aria-expanded="false"`, and `takeHeldHelpToggle('/convert')` is `false`. | Local Canon (06 Once row: "dropped when the user leaves the page before it mounts") | In Red the take name is missing |
| AC-158.6 | unit | `HELP_ROUTE_SCOPE`: a mounted `HelpCard feature="downloader"` with the hash `#/convert`: `toggle()` leaves it collapsed, and a card rendered next for `converter` reads expanded; a `HelpCard feature="downloader"` on `#/` toggles on `toggle()`; dispatching a detail-less `av-kit:help:toggle-local` toggles both a mounted downloader card and a mounted converter card; and with an F1 held for `/convert` (hash `#/convert`, no card mounted), a `HelpCard feature="downloader"` rendered next stays collapsed and `sc.takeHeldHelpToggle('/convert')` is then still `true` (the card takes its route from `HELP_FEATURE_ROUTE`, not from the hash at mount). | Local Canon (06 Held row: "the current page's HelpCard"); D-1176 | In Red the downloader card toggles |
| AC-158.7 | unit | Guard: a mounted `HelpCard feature="converter"` on `#/convert`: `toggle()` expands it at once and `takeHeldHelpToggle('/convert')` is `false` (a received F1 is never held); a second `toggle()` collapses it. | Local Canon (06 Held row: "an F1 after it mounts toggles at once") | Passes at Red (no typeof assertion); fails if a Green holds a received toggle |
| AC-158.8 | e2e | Fresh app, the Convert chunk held back 1 500 ms: click `nav-convert`, wait for the hash, check the page is not mounted (`setup:` otherwise), press F1; wait for `convert-page` to be visible, settle; Convert's help button reads `aria-expanded="true"`, and `localStorage['av-kit:downloader-help:main:state']` is not `'expanded'`. | Local Canon (06 Tests row: "with the Convert and Capture chunks delayed, F1 opens the help panel on every run"); D-1176 | In Red Convert's card is collapsed |
| AC-158.9 | e2e | The same with `nav-capture`, the Capture chunk and `capture-page`. | As AC-158.8 | As AC-158.8 |
| AC-158.10 | e2e | As AC-158.8 with two F1 presses while the page loads: `aria-expanded="true"`. | Local Canon (06 Once row) | In Red collapsed |
| AC-158.11 | e2e | As AC-158.8, then click `nav-downloader` before the page mounts (checked), wait for the Downloader, then click `nav-convert` and wait for `convert-page`: Convert's card reads `aria-expanded="false"`, and the Downloader key is not `'expanded'`. | Local Canon (06 Once row) | Recorded at Red, not required |
| AC-158.12 | e2e | Guard: Convert mounted (waited for), F1 gives `aria-expanded="true"`, F1 again gives `"false"`. | Local Canon (06 Held row) | Passes at Red |
| AC-158.13 | check | Row 7: `help-f1-mount.test.ts` passes 20 of 20 for each of its five tests (100 passed), `convert-browse-mount.test.ts` 20 of 20 for each test, the `convert-queue.test.ts:1568` test 20 of 20; `help-search.spec.ts` and `keyboard-shortcuts.test.ts` pass once. Counts from `us-row7-repeat.txt`. | Mat 2026-11-16 ("This should be done with framework and scripts!"); Local Canon (06 Tests row) | A count short of 20 is S7 |
| AC-158.14 | check | Row 2: the unit pins pass unchanged: `help-card.test.ts`, `convert-browse-hold.test.ts`, `convert-page.behavior.test.ts`, `convert-page.test.ts`, `convert-commands.test.ts`, `common-shortcuts.test.tsx`, `header-toggles.test.ts`, `palette-curation.test.tsx`, `gui-actions-audit.test.ts`, `capture-page.test.ts`, `shortcuts.test.ts`, with their row-0 hashes. | Local Canon (06 Shared row: one mechanism; `BROWSE_HOLD` behaviour kept) | A failure is S5 |
| AC-159.1 | check | Row 3 records, on the unchanged build at 1280×800 and at 700×650, collapsed and expanded, the boxes of the disclosure, its toggle and its panel, the form's bottom, the status wrapper, the scroller (box, `scrollHeight`, `clientHeight`, `scrollTop`) and the queue region's top, and names the element that holds the space with its measured height (`us-row3-measure.txt`, one `S94-GAP {json}` line per case). Each line also records the status wrapper's shown text, the eight Advanced ids in panel DOM order (visible or not), each id's visibility and the cookie mode shown. | Local Canon (11 Cause row) | The row fails if no line is recorded |
| AC-159.2 | e2e | A fresh page (no add and no SABR or cookie action yet, so no message has shown), 1280×800, Advanced collapsed, the scroller scrolled to its end. The status is empty: the wrapper shows no text (its trimmed `innerText` is `''`) and the `add-status` and `error-banner` placeholders are present and hidden. The eight AC-159.3 ids are in the panel's DOM in AC-159.3's order and none is visible. TAIL ≤ 1 px and GAP = 16 ± 1 px (§Verification Plan 2b), and the panel takes no height. | Local Canon (11 Collapsed row) | In Red TAIL is the measured gap (hypothesis 40 px) |
| AC-159.3 | e2e | A fresh page, 1280×800, Advanced expanded, the status empty as in AC-159.2. Presence and order: `sabr-status`, `sabr-check-btn`, `sabr-force-btn`, `sabr-clear-btn`, `cookie-browser`, `cookie-profile`, `cookie-file`, `cookie-test-btn` are each in the panel's DOM once, in this order (the order row 3 recorded), visible or not. Visibility, checked apart from the order: the ids shown are exactly the set for the cookie mode the page shows (§Goal, the Advanced panel's ids): the four SABR ids and `cookie-test-btn`, plus `cookie-browser` and `cookie-profile` in `browser` mode or `cookie-file` in `file` mode. TAIL ≤ 1 px and GAP = 16 ± 1 px. No button and no cookie mode is clicked; the cookie behaviour is unchanged. | Local Canon (11 Expanded and Tests rows) | In Red TAIL is the measured gap |
| AC-159.4 | e2e | The AC-159.2 and AC-159.3 checks, each part on its own (the empty status, the DOM order, the visibility by mode, TAIL and GAP), on a fresh page at 700×650, collapsed and expanded (`page.setViewportSize`, as `download-queue.test.ts:1574`). | Session 88 RULE-1 (probe at the default width and at 700 px) | As AC-159.2 |
| AC-159.5 | e2e | Guard, with a message: an Add with the URL empty shows `error-banner` with "URL is required", visible; the status wrapper shows where it does today (its top is at or below the form's bottom, and the banner is inside it), and the queue region's top is below the banner's bottom. The message is not cleared afterwards, and the test does not wait for it to clear. No request leaves the renderer (the check is client-side, `DownloaderPage.tsx:355`). | Local Canon (11 §Downloader page layout, MEU-53; the inline status precedent `11-page-layout.md:95`) | Passes at Red; fails if a Green hides the banner |
| AC-159.6 | check | Row 4 and the gate: unit `downloader-page.test.ts`, `downloader-page.behavior.test.ts`, `layout-canon.test.ts`, `layout-primitives.test.ts`; E2E `download-queue.test.ts` and `layout-primitives.test.ts` pass unchanged. | Local Canon (11 Tests row: "the existing Downloader layout tests keep passing") | A failure is S5 |
| AC-159.7 | check | Row 7: `downloader-advanced-gap.test.ts` passes 3 runs of 3, with no `flaky` and no `unhandled rejection:` line. | Mat 2026-11-16 | A failed run is S7 |
| AC-1 | unit | `preview-script.test.ts`: the preview script exists; `PREVIEW_NOTICE` is `'electron-vite-preview: cleared ELECTRON_RUN_AS_NODE'`; `previewArgs(['--x'])` is `[the electron-vite bin, 'preview', '--x']` with the same bin as `devArgs([])[0]`; `runElectronVite` is a function exported by the dev module; importing both modules spawns nothing (the test stubs `child_process.spawn` through `vi.mock` and counts calls). | Local Canon (D-1130; the Session 90 dev contract) | In Red the script is missing |
| AC-2 | unit | `ui/package.json` `scripts.preview` is `'node ./scripts/electron-vite-preview.mjs'` and `scripts.dev` is unchanged (`'node ./scripts/electron-vite-dev.mjs'`). | Local Canon (D-1130) | In Red `scripts.preview` is `'electron-vite preview'` |
| AC-3 | check | Row 5, base: `preview-proof.py --launch preview --run-as-node set --expect window --expect-notice no` exits 1 with `window: no` and `left: 0` (the defect reproduced); `--run-as-node unset` exits 0 with a window (the proof can see one). | Local Canon (`UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`) | `set` exiting 0 at base is S8 |
| AC-4 | check | Row 6 and the gate: `--launch preview --run-as-node set --expect window --expect-notice yes` exits 0 (a window and the notice in the child's stderr log; the notice on stdout alone counts as missing); `--run-as-node unset --expect-notice no` exits 0 (a window, no notice). | Local Canon (D-1130) | In Red `set` gives no window |
| AC-5 | check | Row 6: `dev-script.test.ts` passes with the named pin; `--launch dev --run-as-node set --expect window --expect-notice yes` exits 0, so the dev script still works after the refactor. | Local Canon (Session 90 dev contract) | A failure is S5 |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| F1 before a lazy page mounts | Local Canon | Held and toggled once on mount (06 Held row, D-1128) |
| Two F1 before the mount; leaving first | Local Canon | One toggle; dropped on leaving (06 Once row) |
| One mechanism for F1 and Ctrl+O | Local Canon | `createHeldRequest` in `shell-nav.ts` serves both (06 Shared row, D-1175) |
| Which card an F1 reaches while a page loads | Local Canon + agent decision | The card on the route the F1 was pressed on (D-1176) |
| What holds the Downloader gap | Local Canon | Measured in row 3 before any change (11 Cause row, D-1180) |
| How the gap closes | Local Canon + agent decision | The empty status wrapper is hidden (D-1177), if row 3 confirms it |
| Advanced's controls when expanded | Local Canon | The same eight controls in the same order (11 Expanded row) |
| Preview with `ELECTRON_RUN_AS_NODE` set | Local Canon | The same wrapper as dev (D-1130, D-1178) |
| How the fixes are proved | Human-approved | Electron E2E and a script proof in the gate (Mat 2026-11-16); design D-1179 |
| The README screenshot | Local Canon | Not retaken unless Mat asks (D-1129) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `ui/src/renderer/src/lib/shell-nav.ts` | modify | LF, kept | `HELD_REQUEST`, `CURRENT_ROUTE` |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | modify | CRLF, kept | `BROWSE_HOLD` on the helper; exports unchanged |
| `ui/src/renderer/src/features/settings/settings-commands.ts` | modify | CRLF, kept | `HELP_HOLD`, `takeHeldHelpToggle`, `HELP_FEATURE_ROUTE` |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | modify | LF, kept | `HELP_ROUTE_SCOPE`, `HELP_TAKE_ON_MOUNT` |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | MIXED, kept per line; `:818` bare LF | `STATUS_SLOT` (one attribute) |
| `ui/scripts/electron-vite-dev.mjs` | modify | LF, kept | `runElectronVite`; `main` calls it |
| `ui/scripts/electron-vite-preview.mjs` | new | LF | `PREVIEW_NOTICE`, `previewArgs`, the entry guard |
| `ui/package.json` | modify | CRLF, kept | `:18` the preview script |
| `ui/tests/unit/dev-script.test.ts` | modify | LF, kept | `:64` the named pin (`PINS_NAMED`) |
| `ui/tests/unit/help-f1-hold.test.tsx` | new | LF | AC-158.1 to AC-158.7 |
| `ui/tests/unit/preview-script.test.ts` | new | LF | AC-1, AC-2 |
| `ui/tests/e2e/help-f1-mount.test.ts` | new | LF | AC-158.8 to AC-158.12 |
| `ui/tests/e2e/downloader-advanced-gap.test.ts` | new | LF | AC-159.2 to AC-159.5 |
| `ui/tests/e2e/s94-help-probe.test.ts` | temporary | LF | Row 1a's chunk probe: created, run once, copied to `C:/Temp/av-kit/ui-small-fixes/us-1a-probe-copy/` and deleted in the same row; `absent` at row 0 and from row 1a's end on |
| `ui/tests/e2e/s94-gap-probe.test.ts` | temporary | LF | Row 3's measurement probe: the same lifecycle, copied to `us-row3-probe-copy/` |
| `.agent/docs/commands.md` | modify | CRLF, kept | `:80` (`COMMANDS_DOC`) |
| `docs/build-plan/06-gui.md` | modify | CRLF, kept | Row 8: a Delivered (Session 94) note before `## Validation Commands` (`:1723`) |
| `docs/build-plan/11-page-layout.md` | modify | CRLF, kept | Row 8: a Delivered (Session 94) note before `## Supersession` (`:190`) |
| `.agent/context/meu-status.yaml` | modify (tool) | LF, kept | Row 8: MEU-158 and MEU-159 `ready_for_review`; H2-2: `approved` |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/known-issues.yaml` | modify (script, tool) | LF, kept | Row 8: the three issues resolved |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | modify | LF, kept | §6 row 94 only: `executed (Session 94)` and this plan folder |

**Line endings** were measured with Python bytes (`us94-probe.txt`, at `HEAD` `ecfa3f3`). CRLF: `AppShell.tsx`, `settings-commands.ts`, `convert-commands.ts`, `Disclosure.tsx`, `ui/package.json`, `help-card.test.ts`, `.agent/docs/commands.md`, `06-gui.md`, `11-page-layout.md`, `build-priority-matrix.md`, `current-focus.md` and `docs/execution/metrics.md`. LF: `HelpCard.tsx`, `router.tsx`, `shell-nav.ts`, `electron-vite-dev.mjs`, `dev-script.test.ts`, `convert-browse-hold.test.ts`, `electron-app.ts`, `convert-browse-mount.test.ts`, `download-queue.test.ts`, `keyboard-shortcuts.test.ts`, `help-search.spec.ts`, the registers, the generated files and the grouping. MIXED: `DownloaderPage.tsx` (`:565` CRLF; `:573`, `:574`, `:575`, `:668`, `:815` and `:818` bare LF); a changed line keeps its own ending. Every new file is LF. Row 0 measures them again (`baseline-eol.json`), and `eol-check.py` checks every scope path. Edits to a CRLF file are made with Python opened with `newline=""` from CRLF text, or with an editor that keeps the ending; never by a tool that rewrites line endings.

### Project files

- **Plan-local scripts**, all in this plan folder:
  - written in row 0: `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py`, copied in shape from `2026-11-17-queue-convert-fixes/` (Session 89) with any newer form from `2026-11-17-test-run-reliability/` (Session 90); `preview-proof.py`, from Session 90's `dev-proof.py`; `load-run.py`, copied from Session 90 for its `host_load_wait`, with that function's limit changed from 60 % to 50 % (the session brief's limit) and nothing else changed; `host-wait.py`, which loads the copied `load-run.py`, calls `host_load_wait()` and exits 1 when the load it ran at is still above 50 % (S11); every Electron step in the rows runs it first;
  - written in H1-2: `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `baseline-citations.txt`.
- **Read, never changed (bound in `baseline-scope.json`):** `AppShell.tsx`, `router.tsx`, `Disclosure.tsx`, `ConvertPage.tsx`, `CapturePage.tsx`, `src/main/index.ts`, `ui/tests/e2e/electron-app.ts`, `ui/tests/e2e/electron-env.ts`, `convert-browse-mount.test.ts`, `convert-queue.test.ts`, `download-queue.test.ts`, `keyboard-shortcuts.test.ts`, `help-search.spec.ts`, `ui/tests/e2e/layout-primitives.test.ts`, the unit pin files in §Test pins, `build-priority-matrix.md`, `docs/execution/plans/2026-11-15-convert-settings-drafts/dev-app-procs.py` (sha256 prefix `03053bc97a32` at plan time) and Session 90's `dev-proof.py` and `load-run.py`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the three handoffs, the rolling reviews and the reflection.
- **New names (`DECLARED_NEW`):** `createHeldRequest`, `currentRoute`, `takeHeldHelpToggle`, `HELP_FEATURE_ROUTE`, `PREVIEW_NOTICE`, `previewArgs`, `runElectronVite`.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Earlier session in the queue | What row 0 checks |
|---|---|---|
| `ui/tests/e2e/electron-app.ts`, `electron-env.ts`, `main-error-watch.cjs` and any shared E2E helper | **Session 91** (`e2e-pointer-flakes`) edits the drag and capture specs and `electron-app.ts`, and may fix a renderer race (grouping §2: `ui/tests/e2e/` goes 91 then 94) | Re-reads `launchElectron`'s signature and options (`electron-app.ts:70`), the scratch `AVKIT_APP_DATA` contract, the close and rejection checks, and `convert-browse-mount.test.ts:27-212` (the helpers rows 1a and 1b copy). **Rows 1a, 1b, 3, 3a, 7 and the gate's Electron steps depend on them.** If Session 91 changed a helper the new specs copy, the specs copy the new form, and the handoff names it |
| Any renderer file in §Files Modified | Session 91 (a renderer race fix) | `baseline-scope.json` records the row-0 content; the plan's anchors in `baseline-citations.txt` are re-found, each once |
| `mcp-server/` | Session 92 (`mcp-audit-refresh`) | Nothing: this plan does not touch it (H1-4 skip basis) |
| `tests/integration/`, `packages/` | Sessions 74 and 93 | Nothing: this plan does not touch them (H1-4) |
| `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md` | Session 74 (MEU-144) | MEU-158 and MEU-159 still `pending`; writes go through `meu_status.py` for these two only |
| `known-issues.yaml`, `known-issues.md` | Sessions 74, 91, 92, 93 resolve their own issues | The three issues still `open`; `issue-resolve.py` binds to the row-0 hash (S4) |
| Grouping §6 table | Every session in the queue sets its own row | Rows 74 to 93 may read `executed`; only row 94 changes, and it must still read `proposed` |
| `06-gui.md`, `11-page-layout.md`, `commands.md` | None open | The anchors at `06-gui.md:1710`, `11-page-layout.md:176`, the section ends and `commands.md:80` re-found |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Retaking the README screenshot | out-of-scope | — | D-1129: only if Mat asks |
| Moving the add status inline with the Add button (the MEU-81 precedent, `11-page-layout.md:95`) | out-of-scope | — | D-1177 option B; a larger layout change |
| Preloading the Convert and Capture chunks | out-of-scope | — | It hides the race for the first visit only; it was option D of Session 89's browse brief |
| Changing `AppShell.tsx`'s help-route list or the off-route sessionStorage path | out-of-scope | — | Unchanged; the hold sits in the command module, as Ctrl+O's does |
| Other chords on lazy pages | out-of-scope | — | Session 89 checked every chord: only Ctrl+O and F1 fire before their page mounts |
| A new MEU for the preview script | out-of-scope | — | D-1130: test and tooling debt with no MEU |

## BUILD_PLAN.md Audit

MEU-158 (`gui-help-f1-after-mount`, phase 6, P2, matrix 6.22, `06-gui.md`) and MEU-159 (`gui-downloader-advanced-gap`, phase 11, P2, matrix 11.14, `11-page-layout.md`) are registered `pending` at plan time (`us94-probe.txt`); the plan does not register them again. Row 8 sets both `ready_for_review` with this plan's `execution_plan`, and H2-2 sets `approved`, both through `tools/meu_status.py update`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/ui-small-fixes/us-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-small-fixes/us-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` follows `2026-11-17-queue-convert-fixes/baseline.ps1` (and Session 90's, where newer):

1. **Tree and host state.** `baseline.sha` (`HEAD`), `baseline-dirty.txt` (`git status --porcelain --untracked-files=all`), `git worktree list` and one host-load sample, all printed into the receipt. `HEAD` is recorded, not compared with `ecfa3f3`.
2. **Path-scoped baseline, bound to content.**
   - `baseline-scope.json`: the SHA-256 of each §Files Modified path and each §Project files "Read, never changed" path, or `absent`; the five new files and the two temporary probe files must be `absent`.
   - `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`.
   - `baseline-eol.json`: for each scope path, its kind (`CRLF`, `LF`, `MIXED`) and its CRLF and bare-LF counts.
   - `baseline-skip-hashes.json`: the SHA-256 of every tracked or untracked, not-ignored file under `packages/`, `mcp-server/`, `tests/` and `tools/`; at the gate none may differ, be added or be removed (H1-4).
   - A copy of each scope file's bytes under `C:/Temp/av-kit/ui-small-fixes/baseline-copies/`, which `eol-check.py` compares against.
3. **The citation re-read (`baseline-citations.txt`).** Every anchor this plan cites in a file an earlier session may have touched, found by text and counted once, with its current line: `onHelpToggle` and `helpRoutes` (`AppShell.tsx`); `HELP_EVENTS`, `HELP_PENDING_TOGGLE_KEY`, `HELP_COMMANDS` and `queueToggleAfterNavigate` (`settings-commands.ts`); `'av-kit:help:toggle-local'` and `HELP_PENDING_TOGGLE_KEY` (`HelpCard.tsx`); `browseRequest`, `deliverPaletteBrowse`, `takeHeldBrowse`, `isConvertHome` (`convert-commands.ts`); `takeHeldBrowse` (`ConvertPage.tsx`); `navigateShell` (`shell-nav.ts`); `lazyRouteComponent` twice (`router.tsx`); `id="downloader-add-advanced"`, the status wrapper `min-h-6 max-w-[var(--layout-page-max-width)]`, `data-testid="add-status"`, `data-testid="error-banner"`, `download-queue-region` and `'URL is required'` (`DownloaderPage.tsx`); `export async function launchElectron` or its current form (`electron-app.ts`); `CHUNK_DELAY_MS`, `protocol.handle('file'`, `requireNotMounted`, `switchToLoadingConvert` (`convert-browse-mount.test.ts`); `browses on Convert and is inert` (`convert-queue.test.ts`); `setViewportSize({ width: 700` (`download-queue.test.ts`); `scripts.preview` (`dev-script.test.ts`); `"preview": "electron-vite preview"` (`ui/package.json`); `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` (`commands.md`); the 06 and 11 anchors and section ends; matrix rows 6.22 and 11.14; the window size `1280` and `800` in `src/main/index.ts`. A moved line is recorded with its new number, which the rows and the handoffs use; a missing or doubled anchor is S2.
4. **The S2 binding.** MEU-158 and MEU-159 `pending`; the three issues `open`; grouping §6 row 94 `proposed`; `dev-app-procs.py`'s sha256 prefix `03053bc97a32`.
5. **Base receipt.** The full Vitest run (`us-base-ui.txt`, pwsh in `ui/`); its failures are recorded, not fatal, and the gate's `ui-tests` excuses only those ids (the Session 49b baseline rule). No Python suite runs in this session: no Python product file changes.
6. **Plan-local scripts.**
   - `red-check.py` and `identity.py` are copied with this plan's `PLAN`, `PROJECT_ARTIFACTS` (the three handoffs, the reviews, the reflection, `metrics.md`, `current-focus.md`) and `DECLARED_NEW`. `red-check.py`'s boundary fixtures are renamed to AC-158, AC-159 and plain AC-1 (it must refuse `AC-158.1` matching `AC-158.10`, and plain `AC-1` matching a two-digit plain id). `identity.py` clears `ELECTRON_RUN_AS_NODE` (Session 88 RULE-3), and its other-plan skip covers untracked `docs/execution/plans/2026-11-1[5-7]-<slug>/` folders other than this one.
   - `issue-resolve.py` is copied with `SCRATCH` at `C:/Temp/av-kit/ui-small-fixes/issue-resolve`; `RESOLVE_KEYS` keeps `meu_links`, written only for the two MEU issues.
   - `eol-check.py` is copied with this plan's scope and `baseline-copies/`: a CRLF file has no bare LF, an LF file no CR, a new file no CR; in a MIXED file every inserted or changed line ends like the line before it, or like the line after it at the top. `--selftest` covers each rule.
   - `preview-proof.py` is Session 90's `dev-proof.py` with `--launch dev|preview` (the npm script it starts), the notice chosen by the launch (`electron-vite-dev: …` or `electron-vite-preview: …`), `SCRATCH` at `C:/Temp/av-kit/ui-small-fixes`, `--timeout 300` (preview builds before it starts), and the copied `load-run.py` beside it for `host_load_wait` (limit 50 %). It loads `dev-app-procs.py` in place after its sha check, as Session 90's does, and keeps Session 90's root check by PID, parent and creation time, its record and its cleanup checks unchanged.
   - **Separate streams (R1-F2).** Session 90's copy merges stderr into stdout at `Popen` and searches the merged log (`dev-proof.py:307`, `:365`). `preview-proof.py` gives the child two files instead, `preview-proof-<launch>-<mode>-stdout.log` and `preview-proof-<launch>-<mode>-stderr.log`, searches for the notice in the stderr log only, and prints `notice: yes` or `no` (stderr, the value `--expect-notice` is checked against) and `notice on stdout: yes` or `no` (recorded, never a pass).
   - Its `--selftest` keeps every Session 90 case and adds one per launch for the notice choice. It adds adversarial cases through `simulate()`, whose fake `Popen` writes given text to the `stdout` and `stderr` handles it is passed: the notice on stderr only with `--expect-notice yes` exits 0; the notice on stdout only exits 1 (`notice missing`); no notice on either stream exits 1; the notice on stderr with `--expect-notice no` exits 1; and a `Popen` call given `stderr=subprocess.STDOUT`, or one handle for both streams, fails the selftest.
   - The `red-check.py`, `identity.py`, `eol-check.py` and `preview-proof.py` selftests run, and `ruff format --check` and `ruff check` run on the plan folder's Python (Session 82 RULE-1).
   - The Playwright ok-line regex `^ +ok +[0-9]+ ` is self-tested on a line numbered below 10 (Session 89 RULE-1).
7. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read (Session 83 RULE-2).

If any step except the base receipt fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names AC-158.1 to AC-158.6 (row 1), AC-158.8, AC-158.9 and AC-158.10 (row 1b, Playwright), AC-159.2, AC-159.3 and AC-159.4 (row 3a, Playwright) and AC-1 and AC-2 (row 5). The named pin test in `dev-script.test.ts` also fails at Red by assertion and is not required.
- **Guards** (AC-158.7, AC-158.12, AC-159.5) must pass at Red; the row's Python counts their ok lines.
- **Expectations stay immutable in Green** (S3). Rows 1, 1b, 3a and 5 record the hashes of every test-side file they write; rows 2, 4 and 6 check them.
- **Line endings** are checked by `eol-check.py` after each Green.

### 2a. Chunk probe (row 1a, D-1179)

Session 89 proved the `file` protocol delay on the Convert chunk; this plan also delays `CapturePage-*.js` and depends on Session 91's harness, so row 1a proves the delay on the tree it runs on. It builds the unchanged renderer and writes `ui/tests/e2e/s94-help-probe.test.ts` (LF, temporary) with one test titled `S94-PROBE chunk delay` that:

- launches a fresh app through the copied `launch` with the handler regex `/(ConvertPage|CapturePage)-[^/]*\.js$/` and a 1 500 ms delay, which counts the requests it delayed in `globalThis.__s94Delayed`, and collects `pageerror` events and `console` errors;
- for Convert, then (in a second fresh app) for Capture: clicks the nav item, waits for the hash, records whether the page is absent 200 ms later and whether the Downloader's `help-card` is still in the DOM (recorded only, D-1176), then waits up to 30 s for the page and records the elapsed time;
- prints one line `S94-PROBE {json}` per page with `delayed`, `absentAt200ms`, `downloaderCardPresent`, `mountedMs`, `mounted` and `errors`, and asserts `delayed >= 1`, `absentAt200ms`, `mounted`, `mountedMs >= 1400` and no error naming a MIME type, a module script or a failed chunk.

The row's Python reads both `S94-PROBE` lines and the `1 passed` line, copies the file to `C:/Temp/av-kit/ui-small-fixes/us-1a-probe-copy/`, deletes it from `ui/tests/e2e/` and checks that it is absent. A failure is S8.

### 2b. Gap measurement (row 3, D-1180)

Row 3 builds the unchanged renderer and writes `ui/tests/e2e/s94-gap-probe.test.ts` (LF, temporary) with one test titled `S94-GAP measure` that launches a fresh app (Downloader is the home route), and for each case (1280×800 collapsed, 1280×800 expanded, 700×650 collapsed, 700×650 expanded; the window is 1280×800 by default, `src/main/index.ts:145`, and the 700 px cases use `page.setViewportSize({ width: 700, height: 650 })`, as `download-queue.test.ts:1574`) scrolls the scroller to its end and prints one `S94-GAP {json}` line with the bounding boxes of the disclosure, `add-advanced-toggle`, the panel, the form, the status wrapper, the scroller (box, `scrollHeight`, `clientHeight`, `scrollTop`) and `download-queue-region`, plus the computed `TAIL` and `GAP`. It finds them with no production id (none is added):

- **The form** is `page.getByTestId('downloader-page').locator('form')`, as `download-queue.test.ts:1596`; **the scroller** is its parent (the `overflow-auto` div at `DownloaderPage.tsx:573`).
- **The disclosure** is the `section` that holds `add-advanced-toggle` (the toggle's `closest('section')`, `Disclosure.tsx:26-44`); **the panel** is `#downloader-add-advanced-panel`, the toggle's `aria-controls`.
- **The status wrapper** is the form's next element sibling, whose class holds `min-h-6` (`:818`).

The measures:


- **TAIL** = `scrollHeight − (disclosure.bottom − scroller.top + scrollTop)`: the scrollable space below the disclosure.
- **GAP** = `queue.top − disclosure.bottom` after the scroll: the visible distance from the disclosure to the queue.
- **The empty status (R1-F1).** `statusText` is the wrapper's trimmed `innerText`; `statusEmpty` is true only when `statusText` is `''` and `add-status` and `error-banner` are both present in the wrapper and hidden. The placeholders at `:824` and `:831` always exist, so their presence never counts as a message.
- **Presence and order, apart from visibility.** `panelDomIds` lists the `data-testid` of every element inside the panel that is one of the eight AC-159.3 ids, in DOM order, visible or not, in every case. `panelVisible` maps each of the eight to its element's `checkVisibility()`, and `cookieMode` is the value of the checked `cookie-mode-*` radio.

The test clicks only the disclosure toggle, never a SABR or cookie button, and touches no network. The row's Python reads the four lines into `us-row3-measure.txt`, names the element whose height plus one gap equals `TAIL − 0` within 1 px, copies and deletes the probe file, and passes only when, in all four cases, the named element is the status wrapper (the hypothesis: TAIL = 16 + 24 = 40 px collapsed) with `statusEmpty`, `panelDomIds` equals the eight ids in AC-159.3's order, and the visible ids are none when collapsed and, when expanded, exactly the set for `cookieMode` (§Goal, the Advanced panel's ids). The receipt writes each case's mode and visible ids. Any other result is S9: stop and route back to the plan with the receipt; `STATUS_SLOT` is not applied.

### 3. Electron proof (row 7)

- **`help-f1-mount.test.ts`** copies the helpers of `convert-browse-mount.test.ts:27-212` (re-read at row 0: `launch` `:125`, `requireNotMounted` `:200`, `switchToLoadingConvert` `:207`, `CHUNK_DELAY_MS = 1_500`, `TEST_TIMEOUT_MS = 240_000`), with the handler regex `/(ConvertPage|CapturePage)-[^/]*\.js$/`, no dialog stub, and a `switchToLoading(page, nav, pageId)` generalised from `switchToLoadingConvert`. It runs with `--repeat-each 20`.
- **`convert-browse-mount.test.ts`** runs with `--repeat-each 20`, and the `convert-queue.test.ts:1568` test (`-g 'browses on Convert and is inert'`) with `--repeat-each 20` (AC-158.13), because `BROWSE_HOLD` moved onto the helper.
- **`downloader-advanced-gap.test.ts`** runs three times (AC-159.7).
- **The suites around them** run once each: `help-search.spec.ts`, `keyboard-shortcuts.test.ts`, `download-queue.test.ts` and `ui/tests/e2e/layout-primitives.test.ts`.
- **Counting.** The row's Python counts `^ +ok +[0-9]+ .*<title fragment> ` lines per test and requires the `N passed` line and no `failed`, `flaky` or `unhandled rejection:` line; the counts go to `us-row7-repeat.txt`.
- `playwright.config.ts` runs one worker with no retries, so each repeat is a fresh app in series. About 230 Electron launches in all; each Electron step first waits for the host load to read 50 % or less.

### Session gate (H1-2)

`session-gate.ps1` follows `2026-11-17-queue-convert-fixes/session-gate.ps1`: one receipt per step in `C:/Temp/av-kit/ui-small-fixes/`, named `us-D6-<step>`; fail-fast, with later steps printed as `not_run`; the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `scripts-syntax` (`node --check` on both `ui/scripts/electron-vite-*.mjs`, which `tsc` and `eslint` do not cover); `task-contract`; `scope-paths` (every changed path is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`, every `baseline-dirty.txt` path outside this scope keeps its row-0 content, and both temporary probe files are absent); `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `red-check-selftest`; `eol-check-selftest`; `preview-proof-selftest` (with its stdout-only and missing-notice cases); `py-format` and `py-lint` (`ruff format --check` and `ruff check` on this plan folder's Python only) |
| Targeted | `meu-158-unit` (`help-f1-hold.test.tsx` and the AC-158.14 pin files); `meu-159-unit` (the AC-159.6 unit files); `preview-unit` (`preview-script.test.ts`, `dev-script.test.ts`) |
| Host load | `host-load`: the copied `load-run.py`'s `host_load_wait` (also run before every Electron step in rows 1a, 1b, 2, 3, 3a, 4, 5, 6 and 7); it waits until the load reads 50 % or less, re-sampling every 30 s for up to 10 minutes, and records the value it ran at (Session 81 RULE-2). It never fails the gate |
| Fresh full | `ui-tests` (full Vitest); `preview-proof` (`--launch preview --run-as-node set --expect window --expect-notice yes`, AC-4; it builds `out/` itself); `ui-build` (after the proof, so the E2E steps run on a fresh build); `e2e-help-f1-mount`; `e2e-browse-mount`; `e2e-ctrl-o` (`convert-queue.test.ts -g 'browses on Convert and is inert'`); `e2e-help-search`; `e2e-keyboard-shortcuts`; `e2e-advanced-gap`; `e2e-download-queue`; `e2e-layout-primitives`; `state-render` (`meu_status.py render --check`); `issues-render-check` (`issue_triage.py render --check`) |
| Skipped, with reason | `py-tests`, `py-types`, `openapi`, `mcp-*`: every file under `packages/`, `mcp-server/`, `tests/` and `tools/` keeps its `baseline-skip-hashes.json` hash, and none was added or removed (H1-4). The rest of `test:e2e`: only the help toggle, the Convert browse hold, the Downloader status slot and the preview script changed, and their suites run. The clipboard specs `capture-filmstrip-actions.test.ts` and `capture-import.test.ts` never run |

`ui-tests` excuses only ids that `us-base-ui.txt` shows failing. Every E2E step fails on an `unhandled rejection:` line.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a citation anchor missing or counted twice, a MEU not `pending`, an issue not `open`, row 94 not `proposed`, or `dev-app-procs.py` with another hash | Stop; another session moved this ground. A citation that only moved lines is corrected, not a stop. Bring the receipt to Mat |
| S3 | A Red receipt fails `red-check.py` (including an E2E Red that passes on old code, or a `setup:` error), or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, a `baseline-dirty.txt` path changes content, or `known-issues.yaml` lacks its expected hash when `issue-resolve.py` runs | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test other than the named pin fails after a Green | Rerun it alone once; if it fails again, stop: that is an M-7 question (§4a), not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | An Electron test fails in any of row 7's runs, a repeat count is short of 20 of 20, or a receipt holds `unhandled rejection:` | Stop and bring the receipts to Mat; never raise a timeout or add a retry or a wait to pass |
| S8 | Row 1a's probe or a spec's `setup:` check shows that the `file` protocol delay does not hold the Convert or Capture chunk back, breaks the chunk load, or that `preview-proof.py` at base (AC-3) sees a window with the variable set | Stop and route back to the plan; never patch the handler in place, never drop the precondition |
| S9 | Row 3's measurement names an element other than the empty status wrapper, or TAIL and GAP do not fit the hypothesis within 1 px, or a fresh page's status is not empty (shown text), or the eight ids are not in the panel's DOM in AC-159.3's order, or the visible ids differ from the set for the cookie mode shown | Stop and route back to the plan with `us-row3-measure.txt`; `STATUS_SLOT` is not applied, and a new brief chooses the fix |
| S10 | A file under `packages/`, `mcp-server/`, `tests/` or `tools/` changes | Stop: this session changes no Python, API or tool file |
| S11 | The host load stays above 50 % for 10 minutes before an Electron step | Record it and wait; never run the Electron step above the limit |
| S12 | A step would need to read user data (the models folder, the app database, the settings file) or reach the network | Stop: not allowed without Mat's words (Session 70 RULE-2); every Electron run uses a scratch `AVKIT_APP_DATA` |

## Decision Log

> [!NOTE]
> D-1175, D-1178, D-1179 and D-1180 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-1176 and D-1177 hit M-5 (a user-visible fork the canon does not settle), so they are briefs (below). No other M item is hit: no API, OpenAPI or MCP change and only a dev script changes (M-4 clear), no user data is read or written (M-2 clear), and the one changed test expectation is named with its file, line, old and new text in §Test pins (M-7 clear). Mat's hand-over covers M-3, M-5, M-6 and M-8 briefs (HDP §6), so the two are recorded `autonomous` with their `mandatory:` lists kept; `open_decisions` is empty and there is no STOP item.
>
> **Why Session 94 is inside the hand-over.** Mat's 2026-11-17 message asked to "orchestrate the plan creation for all sessions and proceed with execution for each", continuing his 2026-11-15 hand-over ('like we did here. But use the new HDP process.'), and Session 94 is §3 of that grouping (this plan's `grouping_source`). The message is dated 2026-11-17, the same day as this brief set, so the hand-over is not carried from an earlier brief set (HDP §6 scopes a hand-over to one brief set), and `plan_to_exec_gate: human` puts the briefs in front of Mat again before execution. Each handed brief's reasoning starts with the same sentence, word for word.
>
> **Earlier rows are not copied here.** The triage rows D-1128, D-1129 and D-1130 live on the three issues, and the grouping rows D-1131 to D-1134 in the grouping file's §8. H2-2 reads them through `--decision-source` on the grouping and on `.agent/context/known-issues.yaml`, with `--decision-issue` for each of the three issues. `decision_sources` was probed at plan time against this plan itself, with the H2-2 validator's own source list (Session 90 RULE-2; `us94-decision-probe.txt`). Under HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. D-1181 to D-1184 are left free for execution.

```yaml
decision_log:
  - id: D-1175
    stage: planning
    question: "Can MEU-157's held delivery serve F1 as well, and where does the shared mechanism live?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes. HELD_REQUEST: createHeldRequest(stillHome) in ui/src/renderer/src/lib/shell-nav.ts holds one outstanding request per instance (begin joins the same key, replaces another, drops on hashchange off its route; settle holds an unreceived request; take clears it once). BROWSE_HOLD in convert-commands.ts moves onto one instance with its exports and behaviour unchanged; HELP_HOLD in settings-commands.ts uses a second instance keyed by the route; HelpCard takes on mount (HELP_TAKE_ON_MOUNT). AppShell.tsx is not edited."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/06-gui.md:1710-1721 — the MEU-158 Held, Once, Shared and Tests rows; Shared asks to keep one mechanism if it can"
      - "docs/build-plan/06-gui.md:1702-1708 — the Session 89 Delivered note: BROWSE_HOLD, BROWSE_DROP, BROWSE_ACK and BROWSE_TAKE_ON_MOUNT"
      - "ui/src/renderer/src/features/converter/convert-commands.ts:348-400 — browseRequest, the hashchange drop and takeHeldBrowse"
      - "ui/src/renderer/src/lib/shell-nav.ts — navigateShell and the shell's shared helpers"
      - "known-issues.yaml HELP-F1-BEFORE-LAZY-MOUNT-LOST D-1128 — the hold uses the pattern MEU-157 built"
    research: { engine: none, sources: [] }
    reasoning: "The two chords need the same four steps: make the request at press time, join a second press, hold it when no page took it, drop it on leaving, take it once on mount. A copy in settings-commands.ts would be two mechanisms the canon asks not to have. The helper goes into shell-nav.ts, an existing module, so the unit Red fails by assertion on a missing name rather than by a missing file. The refactor of BROWSE_HOLD is guarded by its own unit file, the page tests and both Ctrl+O Electron tests at 20 of 20. Two-way: one module function and two call sites."
  - id: D-1176
    stage: planning
    question: "Which help panel does an F1 pressed while a page loads toggle, and what do two presses or leaving do?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: HELP_ROUTE_SCOPE with HELP_HOLD. The toggle carries the route it was pressed on; only a card on that route takes it and calls preventDefault, so the page you left keeps its panel as it was. A press that no card on its route took is held; a second press while it is held joins it (one toggle); leaving the route drops it. A detail-less toggle still toggles every card, and a mounted page's F1 works as today."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/06-gui.md:1718-1719 — Held: the current page's HelpCard; Once: at most once, dropped on leaving"
      - "ui/node_modules/@tanstack/router-core/dist/esm/router.js:631, load-client.js:690-719 — defaultPendingMs 1e3: the page you left stays mounted for up to 1 s"
      - "ui/src/renderer/src/components/help/HelpCard.tsx:65-73 — every mounted card toggles on every event today"
      - "ui/src/renderer/src/router.tsx:50, :57 — Convert and Capture are lazy routes"
      - "docs/build-plan/06-gui.md:1702-1708 — the Ctrl+O hold: one request per press, joined, dropped on leaving"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-5 because the canon says the current page's card toggles but not what happens to a card the router still shows from the page you left, and four ways remain. A meets the Held and Once rows and keeps the help card's state on the page you left, which is what the user looked at last. The press-joins rule copies Ctrl+O's, so one keyboard rule holds for both chords. Two-way: an event detail and one comparison in the card."
  - id: D-1177
    stage: planning
    question: "How is the empty band under Advanced on the Downloader page closed?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: STATUS_SLOT, applied only if row 3 measures the empty status wrapper as the cause. The wrapper is hidden while both the add status and the error banner are empty, and shows as today when either has text. No class, test id or control changes. Nothing clears the message, so the band is closed on a fresh page only."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/11-page-layout.md:176-188 — the MEU-159 Cause, Collapsed, Expanded, Screenshot and Tests rows"
      - "ui/src/renderer/src/features/downloader/DownloaderPage.tsx:573, :818 — the scroller and the min-h-6 status wrapper inside it"
      - "docs/build-plan/11-page-layout.md:95 — the MEU-81 inline status precedent"
      - "ui/tests/unit/downloader-page.test.ts:519-555 — the layout pin, which no class change touches"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-5 because the fixes look different to the user and the canon names only the outcome. A removes the band with one attribute and keeps the message where it is today; its cost is that nothing clears the status message (DownloaderPage.tsx:228, :355-377), so once any message shows (an add, an add error or a SABR or cookie error) the line stays and the queue sits one line plus a gap lower for the rest of the session; the band is closed on a fresh page only, and later the line holds text, which the canon allows. The move happens on the user's own click, since 'Adding — waiting for backend...' is set at once. B moves the message inline beside Add (the MEU-81 form) and keeps the queue still, but changes the form's layout and its pins. C keeps the reserved line and removes the gap elsewhere, which leaves the empty band the issue reports. Two-way: one attribute."
  - id: D-1178
    stage: planning
    question: "How does npm run preview get the dev script's ELECTRON_RUN_AS_NODE handling?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "PREVIEW_WRAPPER: electron-vite-dev.mjs exports runElectronVite(command, notice, extra), the body of its main(); a new electron-vite-preview.mjs exports PREVIEW_NOTICE and previewArgs and calls runElectronVite('preview', ...) behind its isEntry guard; ui/package.json preview runs it. The one changed expectation is dev-script.test.ts:64 (PINS_NAMED), and commands.md:80 is updated (COMMANDS_DOC)."
    source_tag: Local Canon
    precedents:
      - "known-issues.yaml UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT D-1130 — give preview the same wrapper Session 90 gave dev"
      - "ui/scripts/electron-vite-dev.mjs — devEnv, devArgs, isEntry, exitCodeFor and main"
      - "ui/tests/unit/dev-script.test.ts:63-64 — the dev and preview script pins"
      - ".agent/docs/commands.md:80 — the preview row says Silent"
    research: { engine: none, sources: [] }
    reasoning: "D-1130 names the outcome; this places it. Sharing one spawn function keeps the signal, error and exit handling in one place, so the two scripts cannot drift. A second copy of main() was the alternative and lost on drift. The pin asserts the old script and must change with it; naming it keeps M-7 clear. A dev script is not a product contract, so M-4 is clear. Two-way: one exported function and one new file."
  - id: D-1179
    stage: planning
    question: "How are the three fixes proved without a manual check?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "MEU-158: help-f1-mount.test.ts delays the ConvertPage and CapturePage chunks by 1 500 ms with Session 89's file protocol handler, after row 1a proves the delay on the tree it runs on; it runs 20 of 20, with the Ctrl+O tests 20 of 20 because BROWSE_HOLD moved. MEU-159: downloader-advanced-gap.test.ts measures TAIL and GAP at 1280x800 and at 700x650, collapsed and expanded, three runs. Preview: preview-proof.py, Session 90's dev-proof.py with a launch switch, at base and after the change, and in the gate."
    source_tag: Research-backed
    precedents:
      - "ui/tests/e2e/convert-browse-mount.test.ts:27-212 — the chunk-delay helpers, 20 of 20 in Session 89"
      - "docs/execution/plans/2026-11-17-test-run-reliability/dev-proof.py — the dev script's window proof"
      - "ui/tests/e2e/download-queue.test.ts:1574 — the 700 px viewport precedent"
      - "next-session prompt carried rules — Session 88 RULE-1 (default width and 700 px), Session 89 RULE-1 (the ok regex)"
    research: { engine: local-measurement, sources: ["us94-probe.txt"] }
    reasoning: "Mat asked for framework and script proofs. Each proof forces the condition the bug needs on every run: the chunk delay makes every F1 land before the mount, the viewport cases cover the two widths Session 88 requires, and the proof script reads the window that the defect hides. Row 1a re-proves the delay because Session 91 may change the harness and Capture's chunk was never delayed before. Two-way: test files only."
  - id: D-1180
    stage: planning
    question: "How is the cause of the Downloader gap measured, and what happens if it is not the expected element?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 3 runs a temporary probe on the unchanged build that records the boxes of the disclosure, its panel, the form, the status wrapper, the scroller and the queue region in four cases (two widths, collapsed and expanded), with TAIL and GAP, the status wrapper's shown text, and the eight Advanced ids' DOM order and visibility by cookie mode, each recorded apart. The fix is applied only if the empty status wrapper explains TAIL within 1 px; otherwise S9 stops and routes back with the receipt."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/11-page-layout.md:184 — Cause: measure which element holds the space before any change"
      - "known-issues.yaml DOWNLOADER-ADVANCED-PANEL-GAP — root cause not established"
    research: { engine: none, sources: [] }
    reasoning: "The canon makes the measurement a precondition. Reading the code gives a hypothesis (24 px of min-h-6 plus a 16 px gap), and the probe either confirms it with numbers or stops the row before a guessed fix lands. Two-way: a temporary file."
  - id: D-1181
    stage: execution
    question: "The gate's host-load step: the plan says it never fails the gate, but S11 forbids an Electron step above 50 % and the plan's host-wait.py exits 1 when the load is still above the limit after 10 minutes. How does the gate keep S11?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: session-gate.ps1 runs host-wait.py as its own host-load step and again before each of its nine Electron steps (preview-proof and the eight E2E steps), each into its own load receipt; a load still above 50 % after the 10-minute wait fails that step with its exit code and the later steps print not_run. A load at or below 50 % passes at once, so on a quiet host the gate runs as the plan's table says."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md §Stop Conditions S11 — never run the Electron step above the limit"
      - "docs/execution/plans/2026-11-17-ui-small-fixes/host-wait.py — exits 1 with host-wait: above the limit when the wait ends above 50 %"
      - "docs/execution/plans/2026-11-17-ui-small-fixes/implementation-plan.md §Session gate Host load row — host_load_wait also runs before every Electron step in rows 1a to 7"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.', and USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The plan's sentence that host-load never fails the gate describes the wait, which returns as soon as the load reads 50 % or less; it cannot also mean an Electron step runs above the limit, because S11 forbids that and the plan's own script exits 1 in that case. Failing the step keeps S11 and leaves the reason in a receipt. B, ignoring the exit code, would run Electron above the limit. C, one host-load step only, would leave the later Electron steps, which run for many minutes after it, unchecked, where every row before the gate checked the load before each Electron step. Doing nothing is not open: the gate script is written in H1-2 and has to choose one of these. Two-way: a gate script line, changed back in one edit."
open_decisions: []
```

Expert pass (fresh context): 2 briefs. Holds: D-1176. Changed: D-1177. Not adopted: none. Receipt: `C:/Temp/av-kit/ui-small-fixes/us94-expert-pass.txt`. D-1176's fixes are adopted: the router citations (`defaultPendingMs` 1e3 at `router.js:631`, `load-client.js:690-719`), the 06 Held and Once rows at `06-gui.md:1718-1719` (a moved line, S2), and the card's route from the fixed `HELP_FEATURE_ROUTE` map, not the hash at mount (`HELP_ROUTE_SCOPE`, `HELP_TAKE_ON_MOUNT`, AC-158.6, task rows 1 and 2).

### D-1176: Which help panel does F1 toggle while a page is still loading?

**I recommend A: F1 opens the help panel of the page you switched to, once, when it appears, and leaves the page you came from alone.** Today, an F1 pressed right after you switch to Convert or Capture is lost while the page loads, and it can toggle the help panel of the page you just left, which the router keeps on screen for up to one second while the new page loads. With A, the key press waits for the new page and opens its panel once. Pressing F1 twice while it loads opens it once, as Ctrl+O does. If you switch away before the page appears, nothing toggles later. On a page that is already showing, F1 works as it does now.

- B: hold the press, but let every help panel on screen take it, as today. The page you left would still toggle.
- C: hold each press separately, so two presses while loading open and then close the panel. That matches pressing twice on a loaded page, but not what Ctrl+O does.
- D: keep the press in session storage, as the off-route F1 does. It would survive a reload and toggle a panel later that you did not ask for.
- Do nothing: F1 right after switching to Convert or Capture sometimes does nothing, or toggles the wrong panel.

Refs: `AppShell.tsx:203-215`, `settings-commands.ts`, `HelpCard.tsx:54-73`, `router.tsx:50`, `:57`, `convert-commands.ts:348-400`, 06 Held and Once rows (`06-gui.md:1718-1719`), `router-core/dist/esm/router.js:631` (`defaultPendingMs: 1e3`), `router-core/dist/esm/load-client.js:690-719`, D-1128, M-5.

### D-1177: How is the empty band under Advanced closed?

Expert pass: changed from "the queue moves down by one line until the message clears": nothing clears the message (`DownloaderPage.tsx:228`, `:355-377`), so the band is closed on a fresh page only and the line stays once a message has shown; "Added" is not a real message. A holds.

**I recommend A: hide the empty message line under the form until there is a message to show.** The measurement in row 3 checks first that this line is what makes the band; if it is something else, the work stops and comes back with the numbers. With A, the queue starts one normal gap below Advanced, collapsed or expanded. That holds on a fresh page. Nothing clears the message once it shows, so after the first one ("Adding — waiting for backend...", "Queued N job(s). Click Start to download.", "Add returned no new jobs..." or "URL is required", or a SABR or cookie error) the line stays in the same place as today and the queue sits one line plus a gap lower for the rest of the session.

- B: move the message onto the same line as the Add button, as the MEU-81 change did elsewhere. The queue never moves, even after a message, but the form's layout and its pins change.
- C: keep the empty line and shrink the space around it. A smaller empty band stays.
- Do nothing: the empty band stays, in the app and in the README screenshot.

Refs: `DownloaderPage.tsx:564`, `:573`, `:818`, 11 Cause, Collapsed and Expanded rows (`11-page-layout.md:176-188`), `11-page-layout.md:95`, D-1129, M-5.

## Research References

- **Electron `protocol.handle`:** since Electron 25, `protocol.handle('file', handler)` can intercept a built-in scheme, and `net.fetch(url, { bypassCustomProtocolHandlers: true })` serves the original response from inside it; Session 89's race spec uses it (`convert-browse-mount.test.ts:168-185`).
- **DOM `dispatchEvent` and `preventDefault`:** `dispatchEvent` returns `false` when the event is cancelable and a listener called `preventDefault`, and `true` otherwise. `HELP_HOLD` uses that value as the card's acknowledgement, as `BROWSE_HOLD` does.
- **React 19 StrictMode:** in development, effects run, clean up and run again on mount; a take-once read in the effect toggles once. AC-158.3 renders in `StrictMode`.
- **The HTML `hidden` attribute:** Tailwind's preflight sets `display: none` on `[hidden]`; the status wrapper has no display class that would override it.
- **electron-vite `preview`:** builds the app and starts Electron on the build, so `preview-proof.py` allows 300 s and the gate rebuilds `out/` after it.
- **Playwright `--repeat-each`:** runs each selected test the given number of times; with one worker and no retries (`ui/playwright.config.ts`) the runs are in series and a failure is never retried into a pass.

## Planning receipts

All under `C:/Temp/av-kit/ui-small-fixes/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `us94-probe.py`, `us94-probe.txt` | `HEAD` `ecfa3f3`, a clean tree and one worktree; line endings, sizes and SHA-256 prefixes of the scope; the new files absent; the `DownloaderPage.tsx` line endings at `:565`, `:573-575`, `:668`, `:815`, `:818`; no `graphify-out`; `dev-app-procs.py` `03053bc97a32`; MEU-158 and MEU-159 `pending`; the three issues `open`; grouping row 94 `proposed`; `scripts.dev` and `scripts.preview` |
| `issues.txt` | The three issues' entries with their `enrichment.decision_log` (D-1128, D-1129, D-1130) |
| `us94-decision-probe.py`, `us94-decision-probe.txt` | `decision_sources` run on this plan, the grouping and the register with the three issues, using the H2-2 validator's own list (Session 90 RULE-2) |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against D-1128, D-1129, D-1130, grouping §3 Session 94, 06 §F1 help waits for the page, 11 §Downloader Advanced gap and the code reads above | `us-plan-2026-11-17-ui-small-fixes` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-158.1 to AC-158.14, AC-159.1 to AC-159.7 and AC-1 to AC-5 | `us-execution-2026-11-17-ui-small-fixes` |
