---
project: "2026-11-17-queue-convert-fixes"
date: "2026-11-17"
source: "grouping .agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md §3 Session 89; issues QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT (D-1100, Mat's ruling 2026-11-17 'recommendation accepted, proceed') and CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE (D-1101)"
meus: ["MEU-156", "MEU-157"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md"
---

# Implementation Plan: Cancel waits for a running job, and Ctrl+O waits for the Convert page

> **Project**: `2026-11-17-queue-convert-fixes`
> **Build Plan Section(s)**: 10 §Cancel while paused (residual) (MEU-156, matrix 10.11, `docs/build-plan/10-queue-card-ui.md:360-372`, anchor `queue-cancel-paused-residual`); 06 §Convert browse waits for the page (residual) (MEU-157, matrix 6.21, `docs/build-plan/06-gui.md:1689-1700`, anchor `convert-browse-after-mount-residual`), with 06 §Common shortcuts' Ctrl+O row as its parent canon. Both MEUs are registered `pending` already (`qc89-probe.txt`); this plan does not register them again.
> **Status**: said to execute (USER_EXPLICIT 2026-11-17 "run @.agent/skills/issue-triage/ create session grouping and continue planning and executing as orchestrator", grouping §8 D-1102, D-1104). `plan_to_exec_gate: human`: that message is the execution approval once the plan review approves (D-1104); the plan review was approved at round 2 (.agent/context/handoffs/2026-11-17-queue-convert-fixes-plan-critical-review.md). Session 89 of the post-Session-88 grouping; Session 90 (`test-run-reliability`) follows it.

---

## Goal

**Goal anchor:** on the Convert and Downloader pages Cancel is disabled while the queue is Paused, and the toolbar's card Cancel, the palette's "Cancel conversions" and "Cancel downloads" and the cancel confirm all follow that one rule; Cancel stays enabled while a job runs, `Pausing…` included; one Ctrl+O on Convert opens exactly one file picker whether it is pressed before or after the lazy Convert page mounts; no service, API route, OpenAPI document or MCP tool changes; Electron E2E tests on the real backend prove both, with no network and no manual check.

**Why.**

- **MEU-156.** While a Convert or Downloader queue is Paused no job runs, so `cancel_processing` only sets a flag that nothing reads (`conversion.py:277-278`, `download.py:456-460`), and the queue stays Paused until the next Start. Both pages still enable Cancel then (`QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT`, `known-issues.yaml:5431`, found in Session 88's expert pass).
- **MEU-157.** `ConvertPage` is a lazy route (`router.tsx:50`). Ctrl+O runs `convert:browse`, which waits two animation frames and dispatches `CONVERT_BROWSE_EVENT`, but the page adds its listener only when it mounts (`ConvertPage.tsx:491-497`). A page that mounts after the dispatch drops the request, so no picker opens. AC-97.7 (`ui/tests/e2e/convert-queue.test.ts:1568`) failed 2 of 20 and 3 of 20 runs for this reason in Session 78 (`CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE`, `known-issues.yaml:5364`).

**Mat's ruling (2026-11-17, D-1100, quoted in the issue):** 'QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT - recommendation accepted, proceed'. The recommendation was: disable Cancel while Paused, keep cancel's meaning, and change no service or API. MEU-157's mechanism was left to this plan (D-1101: "The holding mechanism is the plan's"). The behaviour is proved with Electron E2E tests in the gate, never with a manual check (Mat 2026-11-16: "This should be done with framework and scripts!").

**What the code shows (plan-time reads at `HEAD` `9d6d172`):**

- **The cancel rule.** `controlEnabled('cancel', ctx)` is `Processing || Paused` in `convert-controls.ts:86-87` and `download-controls.ts:77-78`. Three surfaces read it:
  - the palette, through `PAGE_STATE` (`'convert:cancel': controlEnabled('cancel', ctx) && !busy`, `ConvertPage.tsx:564`; `'download:cancel'`, `DownloaderPage.tsx:547`), which lists a stateful command only while its page publishes it enabled (`shortcuts.ts:256-282`);
  - the commands' guard (`cancelConversion`, `convert-commands.ts:285-292`; `cancelDownload`, `download-commands.ts:210-216`);
  - nothing else. The card's Cancel shows only on the in-flight job (`resolvePrimaryAction`, `QueueCard.tsx:346-361`; `isInFlight = inFlightId === job.id`, `QueueList.tsx:215`; `inFlightId` is `processor.current_job_id`, `ConvertPage.tsx:918`, `DownloaderPage.tsx:887`). While Paused `current_job_id` is `null`, so the card already shows no Cancel; the card's `onCancelQueue` calls `cancelConversion` or `cancelDownload` directly, with no confirm (`ConvertPage.tsx:930-932`, `DownloaderPage.tsx:900-902`).
- **The confirm.** The palette's cancel never calls the API. `deliverPaletteCancel` calls `requestConfirm('cancel')` (`convert-commands.ts:332-341`, `download-commands.ts:268-277`), which navigates if needed and dispatches the page's confirm event after two frames; the page's `CONFIRM_ROUTE` listener (`ConvertPage.tsx:262-271`, `DownloaderPage.tsx:303-312`) opens `ConfirmModal` for any kind it receives. `palette-curation.test.tsx:385-414` pins that the command modules dispatch the request with no state check and no fetch, so a gate must sit in the page's listener, not in `requestConfirm`.
- **Transcript's Stop already works while Paused** (D-1107): `'stop'` is `Processing || Paused` (`transcript-controls.ts:68-69`), and `stop_processing` (`transcript.py:275-280`) applies the stop at once when no worker runs (`_apply_stop`, `:739-751`: Paused jobs go Cancelled and the processor Idle). `tests/unit/test_services.py:2099` (`test_ac_11_4_stop_after_paused_keeps_done`) pins it.
- **The browse path.** `deliverPaletteBrowse` (`convert-commands.ts:348-352`) runs `navigateAndDeliver` (`:108-115`): navigate to `/convert` if needed, then dispatch `CONVERT_BROWSE_EVENT` after two frames. `convert:browse` (`commandRegistry.ts:374-383`) is a non-stateful page entry with the chord Ctrl+O, so the shortcut handler runs it whenever the hash is `/convert`, also while the lazy chunk is still loading. The page's `browseForFiles` (`ConvertPage.tsx:476-489`) calls `window.api.showFilesDialog`; no test listens on `CONVERT_BROWSE_EVENT` other than through the page.
- **The other chords** (D-1109). Every other page-scoped chord on a lazy page is stateful (the Capture tools V, A, R, H, T, X, E, C and Ctrl+S, `commandRegistry.ts:471-590`), so it is listed only while its mounted page publishes it enabled; Ctrl+O is the only page chord that can fire before its page mounts. Two global chords also reach a lazy page:
  - **Ctrl+Enter** (`page:primary`, `commandRegistry.ts:638-655`) presses the page's primary button (`PAGE_PRIMARY_CONTROL`, `shortcuts.ts:10-17`) only while it is enabled (`pressEnabledButton`, `commandRegistry.ts:122-127`); before the page mounts there is no button, so the press does nothing, which is the documented rule (PAGE_PRIMARY, D-146). On Convert the primary is `convert-add`, which needs a staged file that a page still loading cannot have.
  - **F1** dispatches `av-kit:help:toggle-local` at once (`AppShell.tsx:203-215`, `settings-commands.ts:14`), which a lazy page's `HelpCard` (`HelpCard.tsx:69`) has not yet subscribed to while the chunk loads. `helpRoutes` (`AppShell.tsx:206`) lists all six shell routes (`router.tsx`), so the held branch (`HELP_PENDING_TOGGLE_KEY`, `settings-commands.ts:10`, `:19`, read in `HelpCard.tsx:56-57`) runs only for a hash outside them, which the NavRail never produces; on Convert and Capture F1 always takes the immediate path.
- **Navigation does not preload the chunk.** The NavRail navigates through `navigateShell` (`lib/shell-nav.ts:4-7`), not a router `Link`, so `defaultPreload: 'intent'` never fetches `ConvertPage` early; a fresh app loads it on the first visit. The production build loads the renderer with `loadFile` (`src/main/index.ts:537`), and the chunk is `out/renderer/assets/ConvertPage-<hash>.js`.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-17). The change touches two control rules, two pages, one command module and the shortcut and confirm paths around them, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go under `C:/Temp/av-kit/queue-convert-fixes/`, named `qc-*` (planning receipts are `qc89-*`).
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE` (Session 79 RULE-3, Session 85 RULE-2, Session 88 RULE-3).
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`. Playwright runs with `ELECTRON_RUN_AS_NODE` cleared.
  - Each Electron test that starts the real backend stops it only by the pid it recorded, checked against that pid's start time. No row stops a process by image name; other worktrees run their own apps.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local (Electron, FFmpeg and the real backend; grouping §3 "Cloud/local: local (Electron E2E)").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), run by the coordinator, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `qc-plan-2026-11-17-queue-convert-fixes` and `qc-execution-2026-11-17-queue-convert-fixes`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
  - Each dispatch writes its own run log; the console output goes to `> $null 2>&1` or a separate console file, and the row reads the run log's tail (Session 88 RULE-2).
- **Queue:** Session 88 is committed (`ae1a33c`), and the grouping commit is `9d6d172`. Other sessions may write into `main` while this one runs, so the baselines and scope checks are path-scoped and bound to content at row 0 (§Verification Plan 1).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-156 Cancel while paused | `.agent/context/handoffs/2026-11-17-queue-convert-fixes-MEU-156-handoff.md` |
| MEU-157 Convert browse waits for the page | `.agent/context/handoffs/2026-11-17-queue-convert-fixes-MEU-157-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-17-queue-convert-fixes-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-17-queue-convert-fixes-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local checkers (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py` |
| WP-2 | MEU-156 Red, then Green (rows 1 and 2) | WP-1 | shared | The two control rules, the two pages' confirm gate, `queue-cancel-paused.test.tsx`, the appended page tests, the two named pin edits |
| WP-3 | MEU-157 Red, the chunk-delay probe, then Green (rows 3, 3a, 3b and 4) | WP-2 | shared | `BROWSE_HOLD` in `convert-commands.ts`, the page's acknowledgement and take on mount, `convert-browse-hold.test.ts`, the appended page tests, the probe receipt, `ui/tests/e2e/convert-browse-mount.test.ts` |
| WP-4 | Electron proof (row 5) | WP-3 | shared | `ui/tests/e2e/queue-cancel-paused.test.ts`, the three cancel runs, the 20-run repeat receipt |
| WP-5 | Canon, issues and status (rows 6 and 7) | WP-4 | shared | 06's Tests row and both Delivered notes, two issues resolved and one added, both MEUs `ready_for_review`, grouping §6 row 89 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | The two handoffs, the review, the reflection |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.** MEU-156 does what you accepted on 2026-11-17 (D-1100). Three decisions are briefs (D-1108, D-1109 and D-1110, §Decision Log): how Ctrl+O waits for the page, what to do about the one other key with the same gap (F1), and whether AC-97.7's steps change. Your hand-over ('continue planning and executing as orchestrator', 2026-11-17, continuing 'like we did here. But use the new HDP process.', 2026-11-15) settles them on the recommendation, and they are recorded that way. Read them if you want to overrule one before execution. There is no human check row: the Electron tests in row 5 and the gate prove the behaviour.
>
> **What changes for you:**
>
> - On Convert and Downloader, while the queue is **Paused**, there is no way to Cancel: the running card has no Cancel (as today), the palette no longer lists "Cancel conversions" or "Cancel downloads", and a cancel confirm that was open closes by itself. Resume, Start and Clear all are unchanged.
> - While a job **runs**, Cancel works as before, also while **Pausing…** shows.
> - On the Transcript page **Stop** keeps working while Paused; it already ends the paused run at once (D-1107).
> - Pressing **Ctrl+O** right after you switch to Convert now opens the file picker every time, even when the page is still loading. Pressing it twice while the page loads opens one picker, not two. If you leave Convert before the page appears, nothing opens later.
> - **F1** pressed on Convert or Capture in the instant before the page appears can still be lost; it is registered as a low known issue, not fixed here (D-1109).

## Proposed Changes

### Single-statement contracts

- **`CANCEL_WHEN_RUNNING` (D-1100, D-1105):** `controlEnabled('cancel', ctx)` is `ctx.processorState === 'Processing'` in `convert-controls.ts:86-87` and `download-controls.ts:77-78`; it is false at `Paused` and `Idle`. The other cases in both files are unchanged.
- **`CANCEL_PALETTE` (D-1105):** `PAGE_STATE`'s `'convert:cancel'` (`ConvertPage.tsx:564`) and `'download:cancel'` (`DownloaderPage.tsx:547`) keep their code; they read `controlEnabled`, so the palette lists the cancel command only while a job runs.
- **`CANCEL_CARD` (kept):** the card shows Cancel only on the in-flight job (`QueueCard.tsx:346-361`, `QueueList.tsx:215`); while Paused `current_job_id` is `null`, so no card shows it. No card code changes.
- **`CANCEL_GUARD` (kept):** `cancelConversion` and `cancelDownload` return without a request when `controlEnabled('cancel', ctx)` is false (`convert-commands.ts:285-289`, `download-commands.ts:210-214`); under `CANCEL_WHEN_RUNNING` that now includes Paused. No command-module change for MEU-156.
- **`CANCEL_STALE_POLL` (residual, D-1105):** the guard and the pages read the cached list (`queueContext`, `convert-commands.ts:133-154`; `ctx`, `DownloaderPage.tsx:260-262`). For up to one poll after the worker goes Paused the cache can still say `Processing`, so a card Cancel click or an open confirm's Confirm in that window can still POST cancel. That is harmless: `cancel_processing` only sets a flag (`conversion.py:277-278`, `download.py:456-460`), and the next Start clears it (`conversion.py:259`, `download.py:438`); Resume runs Start (`conversion.py:272-275`, `download.py:451-454`), so a stale cancel never stops a resumed job. This is a renderer-cache boundary the plan accepts, not a backend guarantee it re-checks. The plan therefore claims "no Cancel control while the page shows Paused", not "no cancel request while the backend is Paused".
- **`CONFIRM_CANCEL_GATE` (D-1105):** each page keeps `ctxRef = useRef(ctx)`, set to the current `ctx` on every render. The `CONFIRM_ROUTE` listener (`ConvertPage.tsx:262-271`, `DownloaderPage.tsx:303-312`) returns without opening the confirm when the request's `kind` is `'cancel'` and `controlEnabled('cancel', ctxRef.current)` is false. Every other kind opens as today. `requestConfirm`, `deliverPaletteCancel` and `deliverPaletteClear` in the command modules are unchanged (`palette-curation.test.tsx:385-414`).
- **`CONFIRM_CANCEL_CLOSE` (D-1106):** each page computes `const cancelEnabled = controlEnabled('cancel', ctx)` during render and has one effect on `[confirm, cancelEnabled]` (not on `ctx`, a new object each render, and not on `processorState` alone, which `react-hooks/exhaustive-deps` rejects as an `error`, `eslint.config.js:24-25`, under `--max-warnings 0`): when `confirm?.kind === 'cancel'` and `cancelEnabled` is false, it calls `setConfirm(null)`. So an open cancel confirm closes when the queue turns Paused and also when it turns Idle (cancel is disabled there too). No request is sent; a confirm of any other kind stays open.
- **`SERVICES_KEPT` (D-1100):** `conversion.py`, `download.py`, `transcript.py`, the API routes, the OpenAPI document and the MCP tools are not changed; cancel keeps its meaning.
- **`TRANSCRIPT_STOP_KEPT` (D-1107):** `transcript-controls.ts` and the Transcript page are not changed; Stop stays enabled while Paused, because it acts then.
- **`BROWSE_HOLD` (D-1108; revised in plan review round 1, R1-F1):** in `convert-commands.ts` one module variable, `browseRequest: { held: boolean } | null`, is the single outstanding Browse request. `deliverPaletteBrowse()` decides at press time, before any frame runs. If `browseRequest` is not `null` (a request still waiting for its two frames, or held), the press joins it and schedules nothing. Otherwise it creates a new token `const token = { held: false }`, sets `browseRequest = token`, adds the `BROWSE_DROP` listener, and calls `navigateAndDeliver` with a run that returns at once unless `browseRequest === token` (so a run whose request was taken on mount, dropped, or replaced does nothing); the run then dispatches `new CustomEvent(CONVERT_BROWSE_EVENT, { cancelable: true })`, and if `dispatchEvent` returns `true` (no listener called `preventDefault`) and `isConvertHome()` is true it sets `token.held = true` and keeps the request; otherwise it clears it (`browseRequest = null`, listener removed). So any number of presses before the page takes the request are one request with one run, and no run can open a picker for a request that was already taken or delivered, whichever side of the mount its frames fall. Two presses within the same two frames on a mounted page also open one picker; a press after a delivered request opens its own.
- **`BROWSE_DROP` (D-1108):** the `hashchange` listener, added with the token at press time, clears `browseRequest` and removes itself as soon as `isConvertHome()` is false, so a request, waiting or held, never outlives a visit to Convert. A press made off Convert adds it before `navigateShell('/convert')`, whose synchronous `hashchange` (`shell-nav.ts:4-6`) finds the hash on `/convert` and keeps the request. A run that finds the hash already off `/convert` holds nothing.
- **`BROWSE_ACK` (D-1108):** the page's browse listener (`ConvertPage.tsx:491-497`) becomes `(event: Event) => { event.preventDefault(); browseForFiles() }`, so a delivered request is never held.
- **`BROWSE_TAKE_ON_MOUNT` (D-1108):** the same effect adds the listener first and then runs `if (takeHeldBrowse()) browseForFiles()`. `takeHeldBrowse(): boolean` returns whether a request is outstanding, held or still waiting for its frames, and clears it with its listener; the waiting run, if any, then finds its token gone and does nothing. Under StrictMode's double effect (the app renders in `StrictMode`, `main.tsx`; React 19) the first run takes the request and the second finds none, so one request opens one picker; AC-157.6 and AC-157.14 render inside `StrictMode` to pin it.
- **`CHORDS_CHECKED` (D-1109):** no other chord changes. Ctrl+Enter before mount does nothing, as its "only while enabled" rule says, and is not registered. F1's gap is registered as `HELP-F1-BEFORE-LAZY-MOUNT-LOST` (`open`, low, ui) by row 7 and is not fixed.
- **`AC977_KEPT` (D-1110):** `convert-queue.test.ts:1568-1583` (AC-97.7) is not edited; it keeps pressing Ctrl+O right after the switch and must pass 20 of 20 runs. 06's Tests row (`06-gui.md:1700`) is edited to name the race spec instead of a wait in AC-97.7.
- **`PINS_NAMED` (D-1105):** exactly two existing test expectations change, both edited at Red: `ui/tests/unit/convert-page.test.ts:429` and `ui/tests/unit/downloader-page.test.ts:293` (§Test pins). Every other pin passes unchanged.

### MEU-156: Cancel while paused

1. **`convert-controls.ts` (MIXED, kept per line) and `download-controls.ts` (CRLF, kept):** `CANCEL_WHEN_RUNNING`. Lines `:86-87` of `convert-controls.ts` are CRLF (its bare-LF lines are `:175-178` and `:230-233`).
2. **`ConvertPage.tsx` (CRLF, kept):** `ctxRef` beside `ctx` (`:245`), `CONFIRM_CANCEL_GATE` in the listener at `:262-271`, `CONFIRM_CANCEL_CLOSE`.
3. **`DownloaderPage.tsx` (MIXED, kept per line):** the same; `ctx` at `:260-262` is bare LF and the listener at `:303-312` is CRLF, so each new or changed line takes the ending of the line before it (`eol-check.py`).
4. **Named pin edits (row 1):** `convert-page.test.ts:429` (CRLF) and `downloader-page.test.ts:293` (CRLF) change `true` to `false` (§Test pins).
5. **Tests:** `ui/tests/unit/queue-cancel-paused.test.tsx` (new, LF; `/** @vitest-environment jsdom */`, because the Vitest default environment is node) holds AC-156.1 to AC-156.4; AC-156.5 to AC-156.7 are appended to `convert-page.behavior.test.ts` (CRLF) after the AC-155.20 test (which ends at `:1341` at `HEAD`), in its describe (the MEU-45 describe from `:766`, default `processorState` `'Processing'`, `:770` and `:817`); AC-156.8 to AC-156.10 are appended to `downloader-page.behavior.test.ts` (MIXED) after the AC-155.21 test (which ends at `:1112`), in the MEU-46 describe from `:406`; those lines are bare LF, like the range around them. `ui/tests/e2e/queue-cancel-paused.test.ts` (new, LF) holds AC-156.11 and AC-156.12 (row 5).
6. **`PAUSED_FIXTURE` (setup, not M-7):** both describes' list fixtures hard-code the in-flight id (`current_job_id: 'job-2'`, `convert-page.behavior.test.ts:865`; `'dl-2'`, `downloader-page.behavior.test.ts:548`), so a Paused fixture would still show the in-flight card's Cancel, which the real services never report (`current_job_id` is `None` while Paused, `conversion.py:497-501`, `download.py:660-664`). AC-156.5 and AC-156.8 therefore wrap the describe's stubbed `fetch` inside the new test only, returning `current_job_id: null` on the list GET while `processorState` is `'Paused'`. This is a setup change in the new tests: the existing fixture lines, every existing assertion, `QueueCard.tsx` and `QueueList.tsx` stay byte-identical, and row 1 checks that both behaviour files differ from row 0 by inserted lines only. It is not M-7, because no existing expectation changes.

### MEU-157: Convert browse waits for the page

1. **`convert-commands.ts` (CRLF, kept):** `BROWSE_HOLD`, `BROWSE_DROP`, `takeHeldBrowse` (`:348-352` and a few lines beside it).
2. **`ConvertPage.tsx` (CRLF, kept):** `BROWSE_ACK` and `BROWSE_TAKE_ON_MOUNT` in the effect at `:491-497`, importing `takeHeldBrowse`.
3. **Tests:** `ui/tests/unit/convert-browse-hold.test.ts` (new, LF, jsdom) holds AC-157.1 to AC-157.5; AC-157.6, AC-157.7 and AC-157.14 are appended to `convert-page.behavior.test.ts` at the end of the MEU-33 describe (from `:70`; its closing `})` is at `:752` at `HEAD`), using its `dialogFilters` stub (`:80`, `:94-97`) and `renderConvert()` (`:195-204`); `ui/tests/e2e/convert-browse-mount.test.ts` (new, LF) holds AC-157.8 to AC-157.11 (row 3b, Red; row 5, the repeat).
4. **06 (row 6, D-1110):** the Tests row at `:1700` (CRLF) reads: "Unit: a request before mount is delivered once on mount, and one after mount at once; Electron: a race spec presses Ctrl+O while the Convert page is still loading (its chunk delayed) and opens one picker, and AC-97.7 keeps pressing Ctrl+O right after the switch; both pass 20 of 20 runs." Its Source cell is unchanged.
5. **Known issue (row 7, D-1109):** `tools/issue_triage.py add` registers `HELP-F1-BEFORE-LAZY-MOUNT-LOST`; nothing in the code changes for it.

### Test pins

Each pin is cited by file, line and description (Session 83 RULE-1: no other family's AC ids are copied here as this plan's).

| Pin | What it checks | After this change |
|---|---|---|
| `ui/tests/unit/convert-page.test.ts:429`, in the test titled "AC-33.11 ENABLED_WHEN gates Start Pause Resume Cancel reorder and ffmpeg" (`:417`) | `expect(controlEnabled('cancel', { ...ctx, processorState: 'Paused' })).toBe(true)` | **Changes (named).** Old: `.toBe(true)`. New: `.toBe(false)`. Nothing else in the test moves; `:428` (cancel at Processing, `true`) is unchanged. Edited at Red (row 1), so the test fails at Red by assertion and passes at Green |
| `ui/tests/unit/downloader-page.test.ts:291-293`, in the test titled "AC-20.9 ENABLED_WHEN gates Start Pause Resume Cancel and queue actions" (`:273`) | `controlEnabled('cancel', { items: pending, selectedId: 'a', processorState: 'Paused' })` then `).toBe(true)` at `:293` | **Changes (named).** Old: `:293` `    ).toBe(true)`. New: `    ).toBe(false)`. Nothing else moves. Edited at Red (row 1) |
| `convert-page.behavior.test.ts:1101` (the card's Cancel on the in-flight job), `:1193-1215` (the palette's clear and cancel open the page confirm), `:1169`, `:1243`, `:1280` | Cancel in `Processing` (the describe's default, `:770`, `:817`) | Unchanged: Cancel is enabled while a job runs |
| `downloader-page.behavior.test.ts:769-798` (the cancel command is false only at Idle), `:800-833` (the palette's confirm), `:899` | Cancel in `Processing` and Idle | Unchanged |
| `palette-curation.test.tsx:385-414` ("palette clear and cancel request the page confirm after two frames and call no API") | `deliverPaletteCancel` dispatches `[{ kind }]` with no state and no fetch | Unchanged: the gate sits in the page listener (`CONFIRM_CANCEL_GATE`) |
| `queue-pause-feedback.test.tsx:478-483` and the Session 88 page tests that read `convert:cancel` and `download:cancel` true while `Pausing…` shows | Cancel during a pending pause | Unchanged: the state is `Processing` |
| `ui/tests/e2e/queue-pause-feedback.test.ts` (the Cancel during `Pausing…` test), `convert-queue.test.ts:879`, `download-queue.test.ts:731` | Cancel on a running job | Unchanged |
| `ui/tests/e2e/convert-queue.test.ts:1568-1583` ("Ctrl+O browses on Convert and is inert on Downloader") | Ctrl+O right after the switch picks one file | Unchanged (`AC977_KEPT`); it must pass 20 of 20 in row 5 |
| `shortcuts.test.ts:312`, `:330`, `:357` | The shortcut handler runs page entries and skips stateful ones that are not published | Unchanged |
| `common-shortcuts.test.tsx:37`, `:49` | `convert-browse` carries the `convert:browse` chord hint (AC-97.4 HINTS) | Unchanged |
| `convert-page.behavior.test.ts:1378-1382` ("AC-97.4 HINTS convert-add and convert-browse carry their chords") | `convert-browse` shows the `convert:browse` chord hint, and `convert-add` the `page:primary` one | Unchanged: no hint, label or chord changes. It is not a Browse delivery pin (the existing delivery pin is AC-97.7, `convert-queue.test.ts:1568-1583`, above), and nothing in the M-7 reasoning rests on this test |
| `palette-curation.test.tsx:76`, `:218`; `fixtures/chord-table.ts:14`; `gui-actions-audit.test.ts:58` | `convert:browse`'s id, label, chord and page | Unchanged |
| `tests/unit/test_services.py:2099` | Transcript Stop after Paused | Unchanged (no Python change; D-1107) |

A sweep of `ui/tests` for a cancel assertion at `Paused` finds only the two named lines (`qc89-probe.txt`). Any other existing test that fails after Green is S5, an M-7 question, not a fix.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `CONVERT_BROWSE_EVENT` | `convert-commands.ts` | A `CustomEvent` with no detail, now `cancelable: true`; a listener that handles it calls `preventDefault` | No detail is added |
| The browse hold | `convert-commands.ts` | One module boolean and one `hashchange` listener; renderer memory only, never persisted | Not sent anywhere |
| The page confirm event | `convert-commands.ts`, `download-commands.ts` (unchanged) | `{ kind }` as today | Unchanged |
| The list envelope's `processor` | Backend services (unchanged) | `state`, `current_job_id` read as today | Unchanged |

No API route, OpenAPI document, MCP tool shape, backend service, persisted setting or database schema changes (M-4 kept clear).

### Acceptance Criteria

Vitest and Playwright titles start with `AC-156.<n>` or `AC-157.<n>` followed by a space, so `red-check.py --require AC-156.1` never matches `AC-156.10`.

- **New names fail by assertion at Red.** `convert-browse-hold.test.ts` imports `convert-commands.ts` as a namespace (`import * as cc from …`) and each test asserts `typeof cc.takeHeldBrowse === 'function'` first; AC-157.7 and AC-157.14 do the same. So Red fails by assertion, never by a missing export (Session 52 RULE-4). MEU-156 adds no name.
- **AC-156.13 and AC-157.13 are pin sets.** They are not `--require`d at Red; rows 2 and 4 run them.
- **AC-156.11 and AC-156.12 are Electron tests** written in row 5 after Green and run three times there and once in the gate.
- **AC-157.8 to AC-157.11 are Electron tests** written in row 3b. AC-157.8 and AC-157.9 fail at Red by assertion (zero pickers); AC-157.10 and AC-157.11 pass at Red (they guard against a fix that opens too many). Each test launches a fresh app, so the Convert chunk is never cached, and the setup check that the page has not mounted throws a plain `Error('setup: …')`, which `red-check.py` refuses, so a fast load can never pass for a Red.
- **AC-157.12 is the repeat count.** Row 5 runs the race spec and AC-97.7 20 times each and writes the pass counts to `qc-row5-repeat.txt`.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-156.1 | unit | Convert rule table through `controlEnabled` from `convert-controls.ts`, with pending items and FFmpeg available: `'cancel'` is true at `Processing`, false at `Paused` and false at `Idle`; `'pause'`, `'resume'` and `'start'` give today's values in the same three states. | Human-approved (Mat 2026-11-17, D-1100: Cancel disabled while Paused); Local Canon (10 §Cancel while paused, Paused and Running rows) | In Red `'cancel'` at `Paused` is true |
| AC-156.2 | unit | The same table for `download-controls.ts`. | As AC-156.1 | As AC-156.1 |
| AC-156.3 | unit | `cancelConversion()` with the cached list envelope `Paused` (seeded through the shared `queryClient`, `fetch` stubbed) sends no request and resolves; with the envelope `Processing` and `current_job_id: 'c1'` it POSTs `/conversions/cancel` once. | Local Canon (`CANCEL_GUARD`; 10 §Cancel while paused, Services row: cancel keeps its meaning) | In Red the Paused call POSTs |
| AC-156.4 | unit | The same for `cancelDownload()` and `/downloads/cancel`. | As AC-156.3 | As AC-156.3 |
| AC-156.5 | unit | Appended to `convert-page.behavior.test.ts` in the MEU-45 describe. Setup (`PAUSED_FIXTURE`, in this test only): the describe's stubbed `fetch` is wrapped so the list GET returns `current_job_id: null` while `processorState` is `'Paused'`, as the service does; the shared fixture at `:865` is not edited. With `processorState = 'Paused'` and the list invalidated: `getCommandState('/convert')` has `convert:cancel` false and `convert:resume` true; no `queue-card-primary-action` reads Cancel. Then `processorState = 'Processing'` with a running job: `convert:cancel` is true and the running card shows Cancel. | Human-approved (D-1100: "the palette's cancel follows the same rule", 10 Paused row); Local Canon (10 Running row) | In Red `convert:cancel` is true while Paused |
| AC-156.6 | unit | `CONFIRM_CANCEL_GATE` on Convert, envelope `Paused`: dispatching `CONVERT_CONFIRM_EVENT` with `{ kind: 'cancel' }` opens no `confirm-modal` after two frames and no request is sent; dispatching `{ kind: 'clear' }` opens it (closed again with `confirm-modal-cancel`). With the envelope `Processing`, `{ kind: 'cancel' }` opens it. | Local Canon (D-1105; 10 Paused row: "the palette's cancel follows the same rule") | In Red the cancel confirm opens while Paused |
| AC-156.7 | unit | `CONFIRM_CANCEL_CLOSE` on Convert: with the envelope `Processing`, `{ kind: 'cancel' }` opens the confirm; then `processorState = 'Paused'` and the list is invalidated: the confirm closes, and no `/conversions/cancel` request was sent. Again from `Processing` with the cancel confirm open, `processorState = 'Idle'` and the list invalidated: the confirm closes, with no request (cancel is disabled at Idle too). A `{ kind: 'clear' }` confirm open while the state turns Paused stays open. | Local Canon (D-1106) | In Red the confirm stays open while Paused and at Idle |
| AC-156.8 | unit | Appended to `downloader-page.behavior.test.ts` in the MEU-46 describe: the AC-156.5 sequence, with the same in-test `PAUSED_FIXTURE` wrap (the shared fixture's `'dl-2'` at `:548` is not edited), `getCommandState('/')`, `download:cancel` and `download:resume`. | As AC-156.5 | As AC-156.5 |
| AC-156.9 | unit | The AC-156.6 checks on Downloader with `DOWNLOAD_CONFIRM_EVENT`. | As AC-156.6 | As AC-156.6 |
| AC-156.10 | unit | The AC-156.7 checks on Downloader (Paused, Idle and the `clear` confirm kept), with no `/downloads/cancel` request. | As AC-156.7 | As AC-156.7 |
| AC-156.11 | E2E | Convert, real backend, scratch `AVKIT_APP_DATA`, two re-encode Cuts of a 90 s 1280x720@30 `testsrc2` clip made with FFmpeg in the test's temp folder. Once job 1 runs: the running card's Cancel is enabled and the palette lists "Cancel conversions". Pause; within 180 s the backend is `Paused` with job 1 Done and job 2 Pending. While Paused: no card shows Cancel; the palette does not list "Cancel conversions"; dispatching `av-kit:convert:confirm` with `{ kind: 'cancel' }` shows no `confirm-modal` after 1 s, while `{ kind: 'clear' }` shows it (dismissed with `confirm-modal-cancel`); the backend is still `Paused`. Resume; once job 2 runs (`processor.current_job_id` = job 2), the palette lists "Cancel conversions" again and the card's Cancel is enabled; a click on it leaves the backend `Idle` with job 2 Cancelled within 30 s. | Human-approved (D-1100; Mat 2026-11-16: proved by "framework and scripts"); Local Canon (10 Tests row: "Electron E2E on the real backend: Cancel disabled on a Paused queue and enabled again once a job runs") | A Cancel offered while Paused, or one missing once job 2 runs, fails |
| AC-156.12 | E2E | Downloader, started through the same pid-recording `launch`, with an in-page fetch seam (the Session 88 `installPauseSeam` shape, `queue-pause-feedback.test.ts:490-537`, extended with a resume that returns `Processing` and a `/downloads/cancel` counter) installed by `addInitScript` and a `page.reload()`. In `Processing` the palette lists "Cancel downloads"; the seam is set `Paused` (`current_job_id` null): the palette does not list it, a `{ kind: 'cancel' }` confirm request shows no modal, and the seam counted 0 cancel POSTs; the seam is set `Processing` again: the palette lists it. No network. | As AC-156.11; Local Canon (10 Tests row: the Downloader proof through the seam, because a real download needs the network) | As AC-156.11 |
| AC-156.13 | unit | Pins: the two named edits (`convert-page.test.ts:429`, `downloader-page.test.ts:293`) read `false`; `convert-page.test.ts`, `downloader-page.test.ts`, `palette-curation.test.tsx`, `queue-pause-feedback.test.tsx`, `convert-commands.test.ts`, `download-commands.test.ts`, `command-palette.test.ts` and `queue-toolbar.test.ts` pass with no other edit (row 2). | Local Canon (§Test pins; D-1105 `PINS_NAMED`) | Any other edited expectation is S5 |
| AC-157.1 | unit | In `convert-browse-hold.test.ts` (jsdom, hash `#/convert`, no listener): `cc.deliverPaletteBrowse()`, then two animation frames: `cc.takeHeldBrowse()` returns true, and a second call returns false. | Local Canon (06 §Convert browse waits for the page, Held row; D-1101; D-1108) | In Red `takeHeldBrowse` is missing |
| AC-157.2 | unit | A listener on `CONVERT_BROWSE_EVENT` that calls `preventDefault`: one `deliverPaletteBrowse()` calls it once, and `takeHeldBrowse()` then returns false. | Local Canon (06 Held row: "a request made after it mounts is delivered at once"; D-1108 `BROWSE_ACK`) | A delivered request that is also held fails |
| AC-157.3 | unit | A held request (as AC-157.1, not yet taken), then the hash set to `#/` and a `hashchange` dispatched: `takeHeldBrowse()` returns false. | Local Canon (06 Once row: "a held request that the page never receives is dropped when the user leaves Convert"; D-1108 `BROWSE_DROP`) | A hold that survives leaving Convert fails |
| AC-157.4 | unit | `deliverPaletteBrowse()` with hash `#/convert`, then the hash set to `#/` before the two frames run: nothing is held (`takeHeldBrowse()` false). | Local Canon (D-1108 `BROWSE_DROP`) | A hold made off Convert fails |
| AC-157.5 | unit | Frame-controlled (R1-F1): `window.requestAnimationFrame` is stubbed in the test with a queue that runs only when the test calls `frame()`, and each `frame()` runs the callbacks queued before it. Hash `#/convert`, no listener: `deliverPaletteBrowse()`; `frame()`; `deliverPaletteBrowse()`; `frame()`; then a stand-in mount, as the page does it: add a listener that calls `preventDefault` and counts, then `cc.takeHeldBrowse()` returns true; then `frame()` twice: the listener was called 0 times, and `cc.takeHeldBrowse()` returns false. | Local Canon (06 Once row: "One Ctrl+O opens at most one picker"; D-1108 `BROWSE_HOLD`) | Two holds, a counter, or a second press's run that delivers after the mount (the round-0 design) fail |
| AC-157.6 | unit | Appended to the MEU-33 describe of `convert-page.behavior.test.ts`: with hash `#/convert` and no page mounted, `deliverPaletteBrowse()` and two frames; then the page is rendered inside `StrictMode` (a local wrapper of the tree `renderConvert()` builds, `createElement(StrictMode, null, …)`), so its effects run, clean up and run again as in the app (`main.tsx`): `showFilesDialog` is called once (the `dialogFilters` stub). Unmount and render again: still once. | Local Canon (06 Held and Once rows; D-1108 `BROWSE_TAKE_ON_MOUNT`) | In Red the dialog is never called |
| AC-157.7 | unit | With the page mounted, `deliverPaletteBrowse()` and two frames: `showFilesDialog` is called once at once, and `cc.takeHeldBrowse()` then returns false (asserting `typeof cc.takeHeldBrowse === 'function'` first). | Local Canon (06 Held row; D-1108 `BROWSE_ACK`) | In Red `takeHeldBrowse` is missing |
| AC-157.8 | E2E | `convert-browse-mount.test.ts`, real backend through the pid-recording `launch`. Before the first Convert visit, `app.evaluate` installs a `file` protocol handler in main that delays any request whose URL ends `ConvertPage-<hash>.js` by 1 500 ms and serves every request with `net.fetch(url, { bypassCustomProtocolHandlers: true })`, and replaces `show-files-dialog` with a stub that counts calls and returns `[]`. Click `nav-convert`, wait for the hash `#/convert`, check that `convert-page` is not yet in the DOM (else `throw new Error('setup: …')`), press Ctrl+O; once `convert-page` is visible and 1 s more has passed, the stub's count is exactly 1. | Local Canon (06 Held row; D-1101; D-1111) | In Red the count is 0 |
| AC-157.9 | E2E | As AC-157.8, but Ctrl+O is pressed twice before the page mounts: the count is exactly 1. An Electron test cannot place the mount between two frames, so the history where the presses' runs straddle the mount is pinned by AC-157.5 and AC-157.14 (frame-controlled unit tests), not here. | Local Canon (06 Once row) | In Red the count is 0; a fix that opens two fails |
| AC-157.10 | E2E | A fresh app; Convert opened and `convert-page` visible; Ctrl+O; after 2 s the count is exactly 1. | Local Canon (06 Held row: "delivered at once") | A picker that opens twice, or not at all, fails |
| AC-157.11 | E2E | As AC-157.8's setup; Ctrl+O; then wait in the page for two animation frames and 150 ms more (past `navigateAndDeliver`'s two frames, so the request has run on `/convert` and the hold is set), and check that `convert-page` is still not in the DOM (else `throw new Error('setup: …')`); only then `nav-downloader`; wait 3 s; `nav-convert` again and `convert-page` visible; after 2 s the count is 0. The wait forces the `BROWSE_DROP` path: without it the switch can land before the two frames, nothing is held, and the test passes without testing the drop. | Local Canon (06 Once row: dropped when the user leaves Convert) | A hold that opens a picker on the next visit fails |
| AC-157.12 | E2E | Row 5 runs `convert-browse-mount.test.ts` with `--repeat-each 20` and AC-97.7 (`convert-queue.test.ts`, `-g "AC-97\.7 "`) with `--repeat-each 20`; a Python check counts the `ok` lines per title in each receipt, matching each title by its `AC-<id> ` prefix so a repeat suffix in the reported title still counts, and requires 20 of 20 for each of the five titles, with no `failed` or `flaky` line, and writes the counts to `qc-row5-repeat.txt`. | Local Canon (06 Tests row as edited, D-1110; Session 78 probes: 2 and 3 failures in 20) | Any run short of 20 of 20 fails (S7) |
| AC-157.13 | unit | Pins: AC-97.7's body (`convert-queue.test.ts:1568-1583`) is byte-identical to row 0; `shortcuts.test.ts`, `common-shortcuts.test.tsx`, `palette-curation.test.tsx`, `gui-actions-audit.test.ts`, `convert-commands.test.ts`, `convert-page.test.ts` and `convert-page.behavior.test.ts` pass with no edit other than this plan's appended tests (row 4). | Local Canon (§Test pins; D-1110 `AC977_KEPT`) | Any other edited expectation is S5 |
| AC-157.14 | unit | Appended to the MEU-33 describe of `convert-page.behavior.test.ts` after AC-157.7, with AC-157.5's frame-controlled `requestAnimationFrame` stub, asserting `typeof cc.takeHeldBrowse === 'function'` first; the page is rendered inside `StrictMode` as in AC-157.6. History A (the reviewer's R1-F1 order): hash `#/convert`, no page; `deliverPaletteBrowse()`; `frame()`; `deliverPaletteBrowse()`; `frame()`; render the page; `frame()` twice: `showFilesDialog` was called exactly once and `cc.takeHeldBrowse()` returns false; then one more `deliverPaletteBrowse()` and `frame()` twice: exactly twice (a press after the mount still opens its own picker). History B: unmount, clear the stub's calls, hash `#/convert`; `deliverPaletteBrowse()`; `frame()`; `deliverPaletteBrowse()`; render the page (between the first press's two frames); `frame()` twice: exactly once. | Local Canon (06 Held and Once rows; D-1108 `BROWSE_HOLD`, `BROWSE_TAKE_ON_MOUNT`) | In Red `takeHeldBrowse` is missing; with today's code History B opens two pickers, and the round-0 design opens two in History A |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Cancel while Paused | Human-approved | Disabled on Convert and Downloader (Mat 2026-11-17, D-1100) |
| Cancel while a job runs, `Pausing…` included | Human-approved | Enabled (Mat 2026-11-16; 10 Running row) |
| Which surfaces follow the rule | Local Canon | The card (already), the palette (through `PAGE_STATE`), the page confirm (`CONFIRM_CANCEL_GATE`), and an open confirm closes (D-1105, D-1106) |
| Services, API, OpenAPI, MCP | Human-approved | Unchanged (D-1100) |
| Transcript Stop | Local Canon | Already acts while Paused; unchanged (D-1107) |
| How a browse request waits for the page | Local Canon | One request made at press time in the command module, taken on mount, dropped on leaving Convert (D-1108) |
| Other chords | Local Canon | Only Ctrl+O among page chords fires before its page mounts; Ctrl+Enter does nothing before mount, as its "only while enabled" rule says; F1's lost toggle is registered, not fixed (D-1109) |
| AC-97.7 and 06's Tests row | Local Canon | AC-97.7 unchanged; a race spec added; the Tests row edited (D-1110) |
| How the behaviour is proved | Human-approved | Electron E2E in the gate (Mat 2026-11-16); design D-1111 |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `ui/src/renderer/src/features/converter/convert-controls.ts` | modify | MIXED (255 CRLF, 8 bare LF at `:175-178`, `:230-233`), kept per line; `:86-87` CRLF | `CANCEL_WHEN_RUNNING` |
| `ui/src/renderer/src/features/downloader/download-controls.ts` | modify | CRLF, kept | `CANCEL_WHEN_RUNNING` |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | modify | CRLF, kept | `BROWSE_HOLD`, `BROWSE_DROP`, `takeHeldBrowse` |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | CRLF, kept | `ctxRef`, `CONFIRM_CANCEL_GATE`, `CONFIRM_CANCEL_CLOSE`, `BROWSE_ACK`, `BROWSE_TAKE_ON_MOUNT` |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | MIXED (752 CRLF, 222 bare LF), kept per line | `ctxRef`, `CONFIRM_CANCEL_GATE`, `CONFIRM_CANCEL_CLOSE` |
| `ui/tests/unit/queue-cancel-paused.test.tsx` | new | LF | AC-156.1 to AC-156.4 |
| `ui/tests/unit/convert-browse-hold.test.ts` | new | LF | AC-157.1 to AC-157.5 |
| `ui/tests/unit/convert-page.behavior.test.ts` | modify | CRLF, kept | AC-156.5 to AC-156.7 (row 1); AC-157.6, AC-157.7 and AC-157.14 (row 3) |
| `ui/tests/unit/downloader-page.behavior.test.ts` | modify | MIXED (2096 CRLF, 488 bare LF), kept per line | AC-156.8 to AC-156.10 after `:1112`, inside a bare-LF range, so their lines are bare LF |
| `ui/tests/unit/convert-page.test.ts` | modify | MIXED (731 CRLF, 29 bare LF), kept per line; `:429` CRLF | The named edit at `:429` (`PINS_NAMED`) |
| `ui/tests/unit/downloader-page.test.ts` | modify | MIXED (540 CRLF, 15 bare LF), kept per line; `:291-293` CRLF | The named edit at `:293` (`PINS_NAMED`) |
| `ui/tests/e2e/convert-browse-mount.test.ts` | new | LF | AC-157.8 to AC-157.11 |
| `ui/tests/e2e/queue-cancel-paused.test.ts` | new | LF | AC-156.11, AC-156.12 |
| `ui/tests/e2e/s89-chunk-delay-probe.test.ts` | temporary | LF | Row 3a's feasibility probe (D-1111): created, run once, copied to `C:/Temp/av-kit/queue-convert-fixes/qc-3a-probe-copy/` and deleted in the same row; `absent` at row 0 and from row 3a's end on (the gate's `scope-paths` requires it absent) |
| `docs/build-plan/06-gui.md` | modify | CRLF, kept | Row 6: the Tests row at `:1700` (D-1110) and a Delivered (Session 89) note before `## Validation Commands` (`:1702`) |
| `docs/build-plan/10-queue-card-ui.md` | modify | CRLF, kept | Row 6: a Delivered (Session 89) note after the Tests row at `:372` |
| `.agent/context/meu-status.yaml` | modify (tool) | LF, kept | Row 6: MEU-156 and MEU-157 `ready_for_review`; H2-2: `approved` |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/known-issues.yaml` | modify (script, tool) | LF, kept | Row 6: the two issues resolved; row 7: `HELP-F1-BEFORE-LAZY-MOUNT-LOST` added, `open` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md` | modify | LF, kept | §6 row 89 only: `executed (Session 89)` and this plan folder |

**Line endings** were measured with Python bytes (`qc89-probe.txt`, `qc89-probe2.txt`, `qc89-probe3.txt`, at `HEAD` `9d6d172`). CRLF: `download-controls.ts`, `convert-commands.ts`, `download-commands.ts`, `ConvertPage.tsx`, `convert-page.behavior.test.ts`, `06-gui.md`, `10-queue-card-ui.md`, `build-priority-matrix.md`, and the state files `current-focus.md` and `metrics.md`. MIXED: `convert-controls.ts`, `DownloaderPage.tsx`, `convert-page.test.ts`, `downloader-page.test.ts`, `downloader-page.behavior.test.ts`. LF: `router.tsx`, `palette-curation.test.tsx`, `queue-pause-feedback.test.tsx`, `convert-queue.test.ts`, the Session 88 E2E file, `electron-app.ts`, the registers, the generated files, the grouping and the four new files. A CRLF file is read and written with `newline=""` from CRLF text; in a MIXED file each new or changed line takes the ending of the line before it, and a changed line keeps its own ending. `eol-check.py` checks every scope path in rows 2 and 4 and in the gate. A new LF file is written as bytes and its CR count checked (Session 83 RULE-3).

### Project files

- **Plan-local scripts**, all in this plan folder:
  - written in row 0: `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py`, copied in shape from `2026-11-17-queue-pause-feedback/`;
  - written in H1-2: `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`.
- **Read, never changed (bound in `baseline-scope.json`):** `download-commands.ts`, `transcript-controls.ts`, `commandRegistry.ts`, `shortcuts.ts`, `router.tsx`, `QueueCard.tsx`, `QueueList.tsx`, `AppShell.tsx`, `settings-commands.ts`, `HelpCard.tsx`, `palette-curation.test.tsx`, `queue-pause-feedback.test.tsx`, `shortcuts.test.ts`, `common-shortcuts.test.tsx`, `gui-actions-audit.test.ts`, `fixtures/chord-table.ts`, `convert-queue.test.ts`, `download-queue.test.ts`, `ui/tests/e2e/queue-pause-feedback.test.ts`, `electron-app.ts`, `src/main/ipc.ts`, `src/main/preload.ts`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the two handoffs, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md` | Any session that moves a MEU | Writes go through `meu_status.py` for MEU-156 and MEU-157 only |
| `known-issues.yaml`, `known-issues.md` | Any triage session; Session 90 resolves three other issues | `issue-resolve.py` changes only the two named issues and binds to a hash (S4); row 7 adds one issue through `issue_triage.py add` |
| Grouping §6 table | Session 90 | Only row 89 changes |
| `06-gui.md`, `10-queue-card-ui.md` | None open | Only 06's Tests row at `:1700` and the two Delivered notes |
| `ui/tests/e2e/` | Session 90 changes `main-error-watch.cjs` and `electron-app.ts` after this session's commit (grouping §2) | Two new files; no existing E2E file changes |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Making Cancel act while Paused (the service goes Idle) | out-of-scope | — | Mat's ruling chose to disable the control and keep the services (D-1100); M-4 |
| Transcript's Stop while Paused | out-of-scope | — | It already acts (D-1107); no change |
| F1 lost before a lazy page mounts | out-of-scope (registered) | — | D-1109: a different, global chord whose fix touches the shell and the help card; row 7 registers `HELP-F1-BEFORE-LAZY-MOUNT-LOST` (`open`, low, ui) |
| Ctrl+Enter (`page:primary`) before a lazy page mounts | out-of-scope (not a defect) | — | D-1109: it presses the primary button only while it is enabled (PAGE_PRIMARY, D-146), and a page that has not mounted has no enabled button; not registered |
| Palette-only Convert and Capture commands with a page listener (`convert:add`, `capture:region`, `capture:open_folder`) | out-of-scope | — | They have no chord and the palette lists them only on their own page, so they need the palette opened and chosen inside the chunk load; not a chord (D-1109) |
| Editing AC-97.7's steps to wait for the page | out-of-scope | — | D-1110: a wait would hide the race; the race spec proves the fix |
| The grouping's §3 Session 89 text ("MEU-157 then edits AC-97.7's spec") and D-1101's "AC-97.7 waits for the page" | out-of-scope | — | Stale under D-1110; another planning record. Row 6's resolution text and 06's Tests row state the corrected plan |
| Preloading the Convert chunk | out-of-scope | — | D-1108 option D; it would hide the race for the first visit only |

## BUILD_PLAN.md Audit

MEU-156 (`gui-queue-cancel-paused`, phase 10, P2, matrix 10.11, `build-plan/10-queue-card-ui.md`) and MEU-157 (`gui-convert-browse-after-mount`, phase 6, P2, matrix 6.21, `06-gui.md`) are registered `pending` at plan time (`qc89-probe.txt`: `row_key: MEU-156` and `row_key: MEU-157` once each); the plan does not register them again. Row 6 sets both `ready_for_review` with this plan's `execution_plan`, and H2-2 sets `approved`, both through `tools/meu_status.py update`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/queue-convert-fixes/qc-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/queue-convert-fixes/qc-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` follows `2026-11-17-queue-pause-feedback/baseline.ps1`:

1. **Tree state.** `baseline.sha` (`HEAD`) and `baseline-dirty.txt` (`git status --porcelain --untracked-files=all`).
2. **Path-scoped baseline, bound to content.**
   - `baseline-scope.json`: the SHA-256 of each §Files Modified path and each §Project files "Read, never changed" path, or `absent`; the four new files and the row-3a probe file must be `absent`.
   - `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`.
   - `baseline-eol.json`: for each scope path, its kind (`CRLF`, `LF`, `MIXED`), its CRLF and bare-LF counts.
   - `baseline-skip-hashes.json`: the SHA-256 of every tracked or untracked, not-ignored file under `packages/`, `mcp-server/`, `tests/` and `tools/`; at the gate none may differ, and none may be added or removed (H1-4).
   - A copy of each scope file's bytes under `C:/Temp/av-kit/queue-convert-fixes/baseline-copies/`, which `eol-check.py` and AC-157.13 compare against.
   - The S2 binding: the `qc89-probe.txt` anchors each counted once (`case 'cancel':` in both control files; `CONVERT_BROWSE_EVENT`, `navigateAndDeliver`, `deliverPaletteBrowse`, `deliverPaletteCancel` and `cancelConversion` in `convert-commands.ts`; `deliverPaletteCancel` and `cancelDownload` in `download-commands.ts`; the two pages' confirm listeners and cancel `PAGE_STATE` lines; the browse listener; the `ConvertPage` line in `router.tsx`; 06's `convert-browse-after-mount-residual` anchor and Tests row; 10's `queue-cancel-paused-residual` anchor; AC-97.7's title), MEU-156 and MEU-157 `pending`, both issues `open`, `HELP-F1-BEFORE-LAZY-MOUNT-LOST` absent, and grouping row 89 `proposed`.
3. **Base receipt.** The full Vitest run (`qc-base-ui.txt`, pwsh in `ui/`); its failures are recorded, not fatal, and the gate's `ui-tests` excuses only those ids (the Session 49b baseline rule). No Python suite runs in this session: no Python file changes.
4. **Plan-local scripts.**
   - `red-check.py` and `identity.py` are copied from `2026-11-17-queue-pause-feedback/` with this plan's `PLAN`, `PROJECT_ARTIFACTS` (the two handoffs, the reviews, the reflection, `metrics.md`, `current-focus.md`) and `DECLARED_NEW` (`takeHeldBrowse`). `identity.py` clears `ELECTRON_RUN_AS_NODE` (Session 88 RULE-3), and its other-plan skip covers untracked `docs/execution/plans/2026-11-1[5-7]-<slug>/` folders other than this one.
   - `issue-resolve.py` is copied from `2026-11-17-queue-pause-feedback/` with `SCRATCH` at `C:/Temp/av-kit/queue-convert-fixes/issue-resolve`; `RESOLVE_KEYS` keeps `meu_links`.
   - `eol-check.py` is copied from `2026-11-17-queue-pause-feedback/` with this plan's scope and `baseline-copies/`: a CRLF file has no bare LF, an LF file no CR, a new file no CR; in a MIXED file every inserted or changed line ends like the line before it, or like the line after it at the top. `--selftest` covers each rule.
   - The `red-check.py`, `identity.py` and `eol-check.py` selftests run, and `ruff format --check` and `ruff check` run on the plan folder's Python (Session 82 RULE-1).
5. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read (Session 83 RULE-2).

If any step except the base receipt fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names AC-156.1 to AC-156.10 (row 1), AC-157.1 to AC-157.7 and AC-157.14 (row 3) and AC-157.8 and AC-157.9 (row 3b, Playwright). The two named pin tests (the AC-33.11 and AC-20.9 titles) also fail at Red by assertion and are not required.
- **Expectations stay immutable in Green** (S3). Rows 1, 3 and 3b record the hashes of every test-side file they write; rows 2 and 4 check them.
- **Line endings** are checked by `eol-check.py` after each Green.

### 2a. Chunk-delay feasibility probe (row 3a, D-1111)

The race spec's delay was not run at plan time, so row 3a proves it before row 3b relies on it. It builds the unchanged renderer and writes `ui/tests/e2e/s89-chunk-delay-probe.test.ts` (LF, temporary) with one test titled `S89-PROBE chunk delay` that:

- launches a fresh app through the pid-recording `launch` (as row 3b);
- installs the `file` protocol handler of AC-157.8 in main, which also counts the requests it delayed in `globalThis.__s89Delayed`, and collects the page's `pageerror` events and `console` errors;
- clicks `nav-convert`, waits for the hash `#/convert`, records whether `convert-page` is absent 200 ms later, then waits up to 30 s for `convert-page` and `convert-browse` to be visible and records the elapsed time;
- prints one line `S89-PROBE {json}` with `delayed`, `absentAt200ms`, `mountedMs`, `mounted` and `errors`, and asserts `delayed >= 1`, `absentAt200ms`, `mounted`, `mountedMs >= 1400` and no error naming a MIME type, a module script or a failed chunk.

The row's Python reads the `S89-PROBE` line and the `1 passed` line, copies the file to `C:/Temp/av-kit/queue-convert-fixes/qc-3a-probe-copy/`, deletes it from `ui/tests/e2e/`, and checks it is absent. A failure is S8: stop and route back; the handler is never patched in place in this row or a later one.

### 3. Electron proof (row 5)

- **`queue-cancel-paused.test.ts`** copies the Session 88 helpers from `ui/tests/e2e/queue-pause-feedback.test.ts`: `makeClip` `:78`, `longClip` `:101`, `probeSeconds` `:110`, `api` `:123`, `queue` `:147`, `readBackendPid` `:151`, `running` `:162`, `startTime` `:172`, `stopRecordedBackend` `:187`, `closeBounded` `:211`, `launch` `:226-284`, `setOutDir` `:286`, `openConvert` `:293`, `addCut` `:301` (with `__S88_PICKED__` renamed `__S89_PICKED__`), `row` `:332`, `start` `:336`, `waitRunning` `:375`, `jobStates` `:389`, and `installPauseSeam` `:490-537`, `seamPaused` `:538`, `seamPausePosts` `:556` as the seam's shape. Job 2 is a second 89 s re-encode Cut, so it is still running when the test reads Cancel after Resume. The palette is read through `header-palette-btn`, `command-palette-input` and `page.getByRole('dialog').getByRole('button', { name })`. Waits allow 180 s for a loaded host. The new file runs three times; a failure is S7.
- **`convert-browse-mount.test.ts`** (written in row 3b) runs with `--repeat-each 20`, and AC-97.7 runs with `--repeat-each 20` (D-1110, AC-157.12). `playwright.config.ts` runs one worker with no retries, so each repeat is a fresh app in series.
- **The suites around them** run once each: `convert-queue.test.ts`, `download-queue.test.ts` and the Session 88 `queue-pause-feedback.test.ts`.
- **Header text at the default width and at 700 px** is not re-probed: no header, toolbar or label text changes in this session (Session 88 RULE-1 does not apply).

### Session gate (H1-2)

`session-gate.ps1` follows `2026-11-17-queue-pause-feedback/session-gate.ps1`: one receipt per step in `C:/Temp/av-kit/queue-convert-fixes/`, named `qc-D6-<step>`; fail-fast, with later steps printed as `not_run`; the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content); `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `red-check-selftest`; `eol-check-selftest`; `py-format` and `py-lint` (`ruff format --check` and `ruff check` on this plan folder's Python only) |
| Targeted | `meu-156-unit` (`queue-cancel-paused.test.tsx`, the two behaviour files and the AC-156.13 pin files); `meu-157-unit` (`convert-browse-hold.test.ts`, `convert-page.behavior.test.ts` and the AC-157.13 pin files) |
| Host load | `host-load`: samples `Win32_Processor.LoadPercentage` five times; above 60 % it waits, re-sampling every 30 s for up to 10 minutes, and records the value it ran at (Session 81 RULE-2). It never fails the gate |
| Fresh full | `ui-tests` (full Vitest); `ui-build`; `e2e-cancel-paused` (`queue-cancel-paused.test.ts`); `e2e-browse-mount` (`convert-browse-mount.test.ts`); `e2e-convert-queue` (AC-97.7 included); `e2e-download-queue`; `e2e-pause-feedback`; `state-render` (`meu_status.py render --check`); `issues-render-check` (`issue_triage.py render --check`) |
| Skipped, with reason | `py-tests`, `py-types`, `openapi`, `mcp-*`: every file under `packages/`, `mcp-server/`, `tests/` and `tools/` keeps its `baseline-skip-hashes.json` hash, and none was added or removed (H1-4). The rest of `test:e2e`: only the Convert and Downloader pages' cancel and browse paths changed, and their suites run |

`ui-tests` excuses only ids that `qc-base-ui.txt` shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a `qc89-probe.txt` anchor missing or counted twice, a MEU not `pending`, an issue not `open`, the F1 issue present, or row 89 not `proposed` | Stop; another session moved this ground. Bring the probe to Mat |
| S3 | A Red receipt fails `red-check.py` (including an E2E Red that passes on old code, or a `setup:` error), or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, a `baseline-dirty.txt` path changes content, or `known-issues.yaml` lacks its expected hash when `issue-resolve.py` runs | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test other than the two named pin tests fails after Green | Stop: that is an M-7 question (§4a), not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | An Electron test fails in any of row 5's runs, or a repeat count is short of 20 of 20 | Stop and bring the receipts to Mat; never raise a timeout or add a wait to AC-97.7 to pass |
| S8 | Row 3a's probe or the race spec shows that the `file` protocol delay does not hold the Convert chunk back (no delayed request, or the page already mounted; the race spec's `setup:` check fails), or that the handler breaks the chunk load (a MIME-type, module-script or chunk-load error, or `convert-page` never mounts) | Stop and route back to the plan: a different way to delay the mount is a test-design change for a brief. Never patch the handler in place, never drop the precondition |
| S9 | A file under `packages/`, `mcp-server/`, `tests/` or `tools/` changes | Stop: this session changes no Python, API or tool file |

## Decision Log

> [!NOTE]
> D-1105, D-1106, D-1107 and D-1111 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-1108 hit M-5, D-1109 hit M-8, and D-1110 hit M-6 and M-8, so they are briefs (below). No other M item is hit: no API, OpenAPI or MCP change (M-4 clear), no user data written (M-2 clear), and the two changed test expectations are named with their files and lines in §Test pins (M-7 clear). Mat's hand-over covers M-3, M-5, M-6 and M-8 briefs (HDP §6), so the three are recorded `autonomous` with their `mandatory:` lists kept; `open_decisions` is empty and there is no STOP item.
>
> **Why Session 89 is inside the hand-over.** Mat's 2026-11-17 message asked for the triage, the grouping and then "continue planning and executing as orchestrator" (grouping §8 D-1102), continuing his 2026-11-15 hand-over ('like we did here. But use the new HDP process.'), and Session 89 is §3 of that grouping (this plan's `grouping_source`). That message is dated 2026-11-17, the same day as this brief set, so the hand-over is not carried from an earlier brief set (HDP §6 scopes a hand-over to one brief set), and `plan_to_exec_gate: human` puts the briefs in front of Mat again before execution. Each handed brief's reasoning starts with the same sentence, word for word: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'."
>
> **Earlier rows are not copied here.** The triage rows D-1100 and D-1101 live on the two issues, and the grouping rows D-1102 to D-1104 in the grouping file's §8. H2-2 reads them through `--decision-source` on the grouping and on `.agent/context/known-issues.yaml`, with `--decision-issue QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT --decision-issue CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE`. `decision_sources` was probed at plan time (`qc89-probe.txt`): the grouping alone gives D-1102 to D-1104, and with the register and both issues it gives D-1100 to D-1104. Under HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. D-1112 to D-1114 are left free for execution.

```yaml
decision_log:
  - id: D-1105
    stage: planning
    question: "Which surfaces carry Mat's Cancel-while-Paused ruling, and where does the confirm's gate sit?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "CANCEL_WHEN_RUNNING: controlEnabled('cancel') is Processing only in convert-controls.ts and download-controls.ts. The palette follows through PAGE_STATE, the card already shows Cancel only on the in-flight job, and each page's CONFIRM_ROUTE listener ignores a cancel request while controlEnabled('cancel') is false (CONFIRM_CANCEL_GATE, through a ctxRef). The command modules' requestConfirm and the services are unchanged; the two pins that assert cancel at Paused are edited at Red (PINS_NAMED). Residual, named (CANCEL_STALE_POLL): for up to one poll after the worker goes Paused the cached list can still say Processing, so a card Cancel click or an open confirm in that window can still POST cancel; it only sets a flag that the next Start clears."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:5431 — D-1100, Mat's ruling: disable Cancel while Paused; no service or API change"
      - "docs/build-plan/10-queue-card-ui.md:366-372 — the Paused, Running, Services and Tests rules"
      - "ui/src/renderer/src/features/converter/ConvertPage.tsx:564 and ui/src/renderer/src/features/downloader/DownloaderPage.tsx:547 — PAGE_STATE reads controlEnabled('cancel')"
      - "ui/src/renderer/src/components/queue/QueueCard.tsx:346-361 and ui/src/renderer/src/components/queue/QueueList.tsx:215 — the card's Cancel is only on the in-flight job"
      - "ui/tests/unit/palette-curation.test.tsx:385-414 — the command modules dispatch the confirm request with no state check"
      - "ui/tests/unit/convert-page.test.ts:429 and ui/tests/unit/downloader-page.test.ts:293 — the only assertions of cancel at Paused"
    research: { engine: none, sources: [] }
    reasoning: "The ruling names the outcome; this decision only places it. One rule in the two control files reaches the palette, the guard and the page through code that already reads it. A gate in requestConfirm would break the pinned contract that the palette never reads state, and the page already holds the state, so the listener is where the request meets it. The two pins assert the old rule and must change with it; naming them with file, line, old and new text keeps M-7 clear. The new page tests' Paused fixture returns current_job_id null inside the new tests only (PAUSED_FIXTURE), as the services do; that is a setup change, not an edited expectation, so it is not M-7 either. The one-poll residual is not closed, because closing it would need a fresh read before every cancel and the request it lets through is harmless (conversion.py:277-278, :259). Two-way: two lines and one guard per page."
  - id: D-1106
    stage: planning
    question: "What happens to a cancel confirm that is open when the queue turns Paused?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "CONFIRM_CANCEL_CLOSE: each page computes cancelEnabled = controlEnabled('cancel', ctx) in render and, in one effect on [confirm, cancelEnabled], closes an open cancel confirm when cancelEnabled is false, so it closes when the queue turns Paused and also when it turns Idle; it sends no request, and a confirm of any other kind stays open."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/10-queue-card-ui.md:366 — while Paused, Cancel is disabled and the palette's cancel follows the same rule"
      - "ui/src/renderer/src/features/converter/convert-commands.ts:285-289 — cancelConversion already does nothing when cancel is disabled"
      - "ui/eslint.config.js:24-25 and ui/package.json lint script (--max-warnings 0) — react-hooks/exhaustive-deps is an error, so the effect depends on the computed boolean, not on ctx or processorState"
    research: { engine: none, sources: [] }
    reasoning: "An open confirm is a Cancel control on screen. Left open while Paused, its Confirm would run a cancel that the guard turns into nothing, which is the reported defect in another place. Closing it shows the rule at once. Keeping it open with a disabled Confirm adds a state the modal does not have. The close at Idle follows from the same rule (cancel is disabled at Idle) and is named in AC-156.7 and AC-156.10 so a test pins it. Depending on the computed boolean keeps the lint gate clean, and ctx is a new object every render, so depending on it would rerun the effect every render. Two-way: one effect per page."
  - id: D-1107
    stage: planning
    question: "Does the Transcript page's Stop have the same gap while Paused?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No. Transcript's Stop acts while Paused (stop_processing applies the stop at once when no worker runs: Paused jobs go Cancelled and the processor Idle), so it stays enabled then and nothing on the Transcript page changes."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/transcript/transcript-controls.ts:68-69 — stop is enabled at Processing or Paused"
      - "packages/core/src/avkit_core/services/transcript.py:275-280 — stop_processing calls _apply_stop when the worker is not active"
      - "packages/core/src/avkit_core/services/transcript.py:739-751 — _apply_stop cancels Processing and Paused jobs and sets the processor Idle"
      - "tests/unit/test_services.py:2099 — test_ac_11_4_stop_after_paused_keeps_done pins it"
      - "docs/build-plan/10-queue-card-ui.md:371 — the Transcript row asks for this check at plan time with its evidence"
    research: { engine: none, sources: [] }
    reasoning: "The defect is a control that does nothing. Transcript's Stop does something while Paused, through a different service method than Convert's and Downloader's cancel, and a test pins it, so disabling it would remove a working action. Two-way: no change."
  - id: D-1108
    stage: planning
    question: "How does a Ctrl+O made before the Convert page mounts reach the page?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: BROWSE_HOLD. The browse event becomes cancelable and the page's listener calls preventDefault. Each press either joins the one outstanding request or, if there is none, creates it as a token at press time with one deferred run; the run acts only while its token is still the outstanding request, and a request that no listener took while the hash is /convert stays held. Leaving Convert drops the request, waiting or held; the page takes it once on mount (takeHeldBrowse), whether held or still waiting for its frames, and opens the picker."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/converter/convert-commands.ts:108-115, :348-352 — navigateAndDeliver and deliverPaletteBrowse dispatch after two frames"
      - "ui/src/renderer/src/features/converter/ConvertPage.tsx:491-497 — the page adds its listener only on mount"
      - "ui/src/renderer/src/router.tsx:50 — ConvertPage is a lazy route"
      - "ui/src/renderer/src/features/settings/settings-commands.ts:10, :19 and ui/src/renderer/src/components/help/HelpCard.tsx:56-57 — the help toggle's held path, a request kept for a card that is not mounted (it runs only for a hash outside the six help routes, AppShell.tsx:206)"
      - "ui/src/renderer/src/main.tsx:22-26 — the app renders in StrictMode (React ^19.2.0), so the take-once read runs under a double effect; AC-157.6 renders in StrictMode"
      - "docs/build-plan/06-gui.md:1697-1698 — the Held and Once rows"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-5 because four ways to deliver the request remain and each behaves differently at the edges. A meets the Held and Once rows exactly: the acknowledgement keeps a mounted page's path as it is, the single press-time request cannot make two pickers, and the hashchange drop keeps a request from opening a picker on a later visit. It reuses the help toggle's idea of a held request but keeps it in memory, because a request is only good for the visit it was made in. Plan review round 1 (R1-F1) showed that a flag set inside the deferred run cannot join presses whose runs fall on both sides of the mount, and that a check of the flag at press time misses it too, because neither press sees a hold yet; so the request is made at press time, and a run checks its own token rather than a flag. A pending-run counter would also need to know which run is stale, so a token is the simpler of the two. B, sessionStorage, survives a reload, which the Once row does not want. C, retrying for a few frames, still loses a request when the chunk takes longer than the retries. D, loading ConvertPage eagerly, fixes the first visit only by making every launch load the Convert code. Two-way: one module token and one effect."
  - id: D-1109
    stage: planning
    question: "Do other keys that act on a lazy page have the same gap, and what is done about them?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-8]
    chosen: "Only Ctrl+O among the page chords: every other chord on Convert or Capture is stateful and listed only while its mounted page publishes it. Of the global chords, Ctrl+Enter (page:primary) presses the primary button only while it is enabled, so a press before mount doing nothing is its documented rule and is not registered; F1 dispatches the help toggle at once on all six routes and can be lost while Convert or Capture loads, so it is registered as HELP-F1-BEFORE-LAZY-MOUNT-LOST (open, low, ui) by row 7 and not fixed here."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/registry/commandRegistry.ts:471-590 — the Capture chords are stateful; convert:browse (:374-383) is the only non-stateful page entry with a chord on a lazy page"
      - "ui/src/renderer/src/registry/shortcuts.ts:256-282 — a stateful entry is listed only while its page publishes it enabled"
      - "ui/src/renderer/src/registry/commandRegistry.ts:638-655, :122-127 and ui/src/renderer/src/registry/shortcuts.ts:10-17 — page:primary (Ctrl+Enter) presses the page's primary button only while it is enabled (PAGE_PRIMARY, D-146)"
      - "ui/src/renderer/src/components/layout/AppShell.tsx:203-215 — helpRoutes holds all six shell routes, so F1 toggles at once on every page; the held branch runs only for another hash"
      - "ui/src/renderer/src/components/help/HelpCard.tsx:69 — the toggle listener is added on mount"
      - ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md:83 — Gate: whether other chords share the gap is decided at plan time"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-8 because fixing F1 would add a third change to a session the grouping scoped to two issues; recording it is inside the plan's check. Ctrl+Enter is left out of the register on purpose: its contract is to act only while the page's primary control is enabled, and a control that is not mounted is not enabled, so dropping the press is the rule working, not a gap; on Convert the primary also needs a staged file that a page still loading cannot have. F1 has no such rule: it is a toggle the user expects to act. The window is the chunk load of a page the user just opened, and a second F1 works, so the issue is low. A, register F1, keeps the finding without growing the session. B, fix it here with the same hold, touches the shell and the help card, which no AC of this session covers. Doing nothing leaves a known gap unrecorded. Two-way: one register entry."
  - id: D-1110
    stage: planning
    question: "Does AC-97.7 change, and what does 06's Tests row say?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-6, M-8]
    chosen: "A: AC-97.7 keeps its steps (Ctrl+O right after the switch) and must pass 20 of 20; a new race spec delays the Convert chunk and proves the hold deterministically; 06's Tests row at :1700 is edited to say so, in row 6."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/convert-queue.test.ts:1568-1583 — AC-97.7 presses Ctrl+O right after nav-convert"
      - "docs/build-plan/06-gui.md:1700 — the Tests row says AC-97.7 waits for the Convert page"
      - ".agent/context/known-issues.yaml:5364, :5379-5392 — D-1101: AC-97.7 waits for the page before Ctrl+O; an autonomous triage decision (decided_by: agent), not a human ruling"
      - ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md:82 — MEU-157 then edits AC-97.7's spec"
      - "ui/src/main/index.ts:537 — the build loads the renderer from file, so a file protocol handler can delay one chunk"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-6 because D-1101 and grouping §3 say AC-97.7 waits for the page, and this plan does not; it is a conflict with canon only, because D-1101 is an autonomous triage decision (decided_by: agent, resolution: autonomous), not a human ruling, so no ruling of Mat's is overturned. M-8 because it adds a spec and edits a canon row. A wait in AC-97.7 makes it pass by never pressing during the load, so it would stop showing the defect it was failing on, and its 20 of 20 would prove nothing about the fix. Keeping its steps makes it a real-use check, and the race spec makes the before-mount case happen every run. B, add the wait as D-1101 says, passes with or without the fix. C, keep AC-97.7 as it is with no race spec, leaves the fix proved only by chance. Doing nothing keeps the flake. Two-way: test files and one canon row."
  - id: D-1111
    stage: planning
    question: "How do the Electron tests prove both fixes without the network or a manual check?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "MEU-156 on Convert runs the real backend on two FFmpeg-made 89 s re-encode Cuts and checks Cancel while running, Paused and running again, and on Downloader an in-page fetch seam keeps the queue Processing, Paused and Processing again; MEU-157's race spec delays the ConvertPage chunk by 1 500 ms through a file protocol handler in main, stubs show-files-dialog with a counter, and presses Ctrl+O before mount; a feasibility probe (row 3a) first shows that the delay holds the chunk back and the page still mounts, and a failure there or later is S8 (stop and route back, never patch in place); each test launches a fresh app and stops only the backend pid it recorded."
    source_tag: Research-backed
    precedents:
      - "ui/tests/e2e/queue-pause-feedback.test.ts:78-556 — Session 88's real-backend helpers, pid-bound stop, dialog replacement and Downloader seam"
      - "ui/playwright.config.ts — one worker, no retries, so a repeat is a fresh app in series"
      - "ui/src/main/index.ts:537 — loadFile, so the chunk is requested on the file scheme"
    research:
      engine: local-measurement
      sources:
        - "C:/Temp/av-kit/queue-convert-fixes/qc89-probe.txt — HEAD 9d6d172, line endings and anchors; ConvertPage builds to its own chunk (out/renderer/assets/ConvertPage-*.js)"
        - "Electron protocol.handle and net.fetch with bypassCustomProtocolHandlers (Electron 25 and later; the app runs Electron 42)"
    reasoning: "A real Convert job is the only way to show Cancel at each backend state, and Session 88 already measured a 90 s libx265 re-encode at about 28 s here, so two such jobs leave room to read Cancel during job 2. A real download needs the network, so the Downloader half goes through the seam. The race needs the page to mount after the request; delaying the one chunk in main makes that happen every run, and the setup check throws a plain error if it ever does not, so a fast load cannot pass for a fix or a Red. The handler was not run at plan time, and a handler that serves the chunk with the wrong type or breaks it would make every race test fail for a reason unrelated to the fix, so row 3a runs it once on the unchanged build before row 3b depends on it. Two-way: test files only."
  - id: D-1112
    stage: execution
    question: "Row 5's third run failed AC-156.11 because the new E2E helper typed the palette filter before the palette's open effect cleared it; how is the helper fixed?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: paletteLists in ui/tests/e2e/queue-cancel-paused.test.ts waits for the palette input to be focused before it fills the filter; the input is focused only in a timer that the clearing effect starts, so a focused input means the clear has run. Then the failing test ran alone once and the whole row 5 cell ran again from its build."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/components/CommandPalette.tsx:89-101 — on open the palette's effect calls setQuery('') and starts a 0 ms timer that focuses the input"
      - "row 5 first run, third queue-cancel-paused run (kept as run1-qc-row5-e2e-r3.txt) — AC-156.11 failed in paletteLists: toHaveValue received an empty string after fill; runs 1 and 2 and AC-156.12 passed"
      - "row 5 alone run (qc-row5-alone-ac15611.txt) — AC-156.11 alone after the fix: 1 passed"
      - "ui/tests/e2e/capture-inbox.test.ts:370-373, ui/tests/e2e/convert-queue.test.ts:739-746 and ui/tests/e2e/download-queue.test.ts:591-598 — existing suites fill the palette input right after the click with no focus wait; not edited (outside scope, M-7)"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The test file is new in this session, so the fix changes no existing expectation and is not M-7; it adds no retry, raises no timeout and does not touch the file protocol delay handler, so the S7 and S8 bans are kept. The failure was the helper racing the palette's own reset, not the product: the palette clears its filter on open by design. Waiting for focus ties the fill to the end of that reset instead of to a fixed delay. B, a sleep before fill, would be a timing guess; C, a retry, is banned. Doing nothing leaves a helper that fails at random. The failed run is disclosed and its receipts are kept; the rerun is the full row 5 cell under the carried rule that a single timing failure that passes alone gets one full rerun. Two-way: one test helper line."
  - id: D-1113
    stage: execution
    question: "H1-6a's dotted AC check required 13 ACs for both MEUs, but the plan has 14 for MEU-157 and the row's own text says 13 and 14; how is the check repaired?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the check compares each MEU with its own count (13 for MEU-156, 14 for MEU-157), as the row's text says; nothing else in the row changes."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-queue-convert-fixes/implementation-plan.md §Acceptance Criteria — AC-156.1 to AC-156.13 and AC-157.1 to AC-157.14"
      - "docs/execution/plans/2026-11-17-queue-convert-fixes/task.md row H1-6a — its task text says 13 for MEU-156 and 14 for MEU-157"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The validation cell compared both MEUs with 13, so it could never pass against the approved AC table; the row's prose and the plan agree on 13 and 14, so the cell was the one in error. The repair is mechanical, changes no AC, test or product file, and was made before H1-6a ran. B, cutting an AC from MEU-157, would drop approved scope. Doing nothing leaves a row that cannot pass. Two-way: one expression in task.md."
  - id: D-1114
    stage: execution
    question: "Row 5's rerun passed every Electron test (80 passed for the race spec, 20 passed for AC-97.7), but its count check reported 17, 18, 18, 18 and 11 of 20 and exited 1, because Playwright pads the run number of its first nine results ('ok  1') and the check's pattern allowed one space only; how is the check repaired?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the count pattern in row 5's cell becomes '^ +ok +[0-9]+ ' (one or more spaces before the run number); the thresholds stay 20 of 20 per title, with no failed or flaky line. Only the check step was run again, against the unchanged row 5 receipts; the Electron runs were not repeated."
    source_tag: Local Canon
    precedents:
      - "qc-row5-browse-r20.txt — the AC-157.8 results 'ok  1', 'ok  5' and 'ok  9' carry two spaces; with them, 20 ok lines per title and '80 passed (10.1m)'"
      - "qc-row5-ac977-r20.txt — results 1 to 9 padded the same way; '20 passed (55.3s)'"
      - "run2-qc-row5-repeat.txt — the check's first output: AC-157.8 17, AC-157.9 18, AC-157.10 18, AC-157.11 18, AC-97.7 11, exactly the padded results missed"
      - "docs/execution/plans/2026-11-17-queue-convert-fixes/task.md row 3b — the same pattern counted correctly there, because four results need no padding"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'continue planning and executing as orchestrator', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The shortfall in each title equals the number of its results numbered 1 to 9, and every receipt ends in a passed line with no failed or flaky line, so the tests passed and the counter was wrong. The repair widens a whitespace match only: it raises no timeout, adds no retry, changes no test and keeps 20 of 20 as the bar, so S7 and S8 do not apply and nothing is M-7. Running the whole cell again would repeat 25 minutes of Electron runs whose receipts already hold the result; the check is a pure read of those receipts. B, a full rerun, adds no evidence; doing nothing leaves row 5 unpassable. The first check output is kept as run2-qc-row5-repeat.txt and disclosed. Two-way: one character class in task.md."
open_decisions: []
```

Expert pass (fresh context) 2026-11-17: `C:/Temp/av-kit/queue-convert-fixes/qc89-expert-pass.txt` (av-kit-peer-reviewer, read only, run by the coordinator; advisory). Each cited fact was checked against the code at `9d6d172` before it was adopted: the fixtures (`convert-page.behavior.test.ts:865`, `downloader-page.behavior.test.ts:548`), `eslint.config.js:24-25` and the `--max-warnings 0` lint script, React `^19.2.0` and `StrictMode` in `main.tsx`, `:1378-1382` being the AC-97.4 HINTS test, D-1101's `decided_by: agent` (`known-issues.yaml:5379-5392`), `helpRoutes` (`AppShell.tsx:206`) against the six routes in `router.tsx`, `page:primary` and `pressEnabledButton` (`commandRegistry.ts:638-655`, `:122-127`), `navigateAndDeliver`'s two frames (`convert-commands.ts:108-115`), and `cancel_processing` and Start's reset (`conversion.py:277-278`, `:259`). Adopted, all of it:

- D-1105: the one-poll stale-cancel residual is named (`CANCEL_STALE_POLL`) in the contracts and in the decision; AC-156.5 and AC-156.8 return `current_job_id: null` while Paused inside the new tests only (`PAUSED_FIXTURE`), labelled a setup change that is not M-7, and row 1 checks that both behaviour files differ from row 0 by inserted lines only.
- D-1106: `CONFIRM_CANCEL_CLOSE` depends on `[confirm, cancelEnabled]`, a boolean computed in render, so `ui-lint` stays clean; the close at Idle is named in AC-156.7 and AC-156.10, with a `clear` confirm kept open.
- D-1107: holds; no change.
- D-1108: React 19, not 18; AC-157.6 renders inside `StrictMode`; the `:1378`/`:1381` pin is re-described as the AC-97.4 HINTS check (and `common-shortcuts.test.tsx:37`, `:49` likewise); no M-7 reasoning rested on either, because neither asserts browse delivery.
- D-1109: Ctrl+Enter (`page:primary`) is named and left out of the register under its "only while enabled" rule (§Out of Scope); the F1 description now says all six routes are help routes and the held branch runs only for another hash. The registered issue's root cause says the same (row 7).
- D-1110: D-1101 is named as an autonomous triage decision, not a human ruling, so M-6 is a canon conflict only; AC-157.11 waits two frames and 150 ms after Ctrl+O and checks the page is still absent before it leaves Convert, so the drop path is forced; AC-157.12 matches titles by their AC prefix.
- D-1111: row 3a, a feasibility probe, shows on the unchanged build that the delay holds the chunk and the page still mounts (§Verification Plan 2a); S8 now also covers a broken chunk load (a MIME-type, module-script or chunk-load error, or a page that never mounts): stop and route back, never patch in place.
- Governance: the hand-over quote is dated 2026-11-17, the same day as this brief set, and each handed brief's reasoning starts with the same sentence (the note above).

Not adopted: nothing. Adopted differently: the wait in AC-157.11 is two frames and 150 ms, not "about 100 ms", so that it plainly outlasts `navigateAndDeliver`'s two frames, and the page-absent check makes the hold observable either way; of the two options for Ctrl+Enter the plan takes the justified exclusion, because a press that acts only on an enabled control is the documented rule (D-146), so registering it would record intended behaviour as a defect; beyond the list, the `common-shortcuts.test.tsx:37`, `:49` description was corrected too, since it had the same error as `:1378`. The goal anchor is unchanged: the residual concerns a request the cached list lets through within one poll, not a Cancel control shown while the page reads Paused. No decision id was added; D-1112 to D-1114 stay free.

Round 1 response (plan review, Codex, 2026-11-17, `C:/Temp/av-kit/qcf-plan-review-round-1.md`, `changes_required`). R1-F1 is fixed as an execution of D-1108 under the HDP, inside the same hand-over; no new decision id, and D-1112 to D-1114 stay free:

- **R1-F1** (two pre-mount presses whose runs fall on both sides of the mount opened two pickers): `BROWSE_HOLD` now makes the request at press time. One module token, `browseRequest`, is the single outstanding request; a press while it exists, waiting for its frames or held, joins it and schedules nothing, so there is never a second run; the one run acts only while its token is still current. `BROWSE_TAKE_ON_MOUNT` takes the request whether held or still waiting, so the waiting run then finds its token gone and does nothing. `BROWSE_DROP` is added with the token at press time and drops a waiting or held request on leaving Convert. Checked against `BROWSE_ACK` (a run that the mounted page acknowledges clears the token), StrictMode (the second effect run finds nothing to take), a single post-mount press (it makes, delivers and clears its own token: AC-157.7, AC-157.10, AC-97.7), and two post-mount presses within two frames (one picker, which the Once row allows). Tests: AC-157.5 is now frame-controlled with a stand-in mount between the two runs; new AC-157.14 runs the reviewer's order (History A) and a mount between the first press's two frames (History B) on the real page in `StrictMode`, and fails at Red (History B opens two pickers with today's code); rows 3 and 4 require and run it, and the gate's `meu-157-unit` set already holds its file. AC-157.9 says why the straddle is pinned in unit tests: an Electron test cannot place the mount between two frames.
- **Q2 note taken:** `CANCEL_STALE_POLL` now cites both reset paths (Start clears the flag, `download.py:438` as well as `conversion.py:259`; Resume runs Start) and calls the residual a renderer-cache boundary.
- **Q4 note taken:** the uniform chunk delay and the 20 repeats do not create the straddle; AC-157.9's text now says so and points to the unit cases.
- The goal anchor is unchanged. The ACs go from 26 to 27 (MEU-157 from 13 to 14), and the task keeps 27 rows.

### D-1108: How should Ctrl+O reach the Convert page while it is still loading?

**I recommend A: remember one Ctrl+O until the page appears, and forget it if you leave Convert first.** Today the Convert page loads on your first visit, and a Ctrl+O pressed in that moment is lost, so no file picker opens. With A, the key press is kept until the page is ready, and the picker then opens once. Pressing Ctrl+O twice while it loads still opens one picker, however the presses fall against the page's loading. If you switch away before the page appears, nothing opens later. Once the page is showing, Ctrl+O works as it does now, except that two presses within a few hundredths of a second open one picker, not two. A can fail in one way: if the page never finishes loading and you stay on Convert, the press waits until you leave.

- B: keep the press in session storage, like the help panel's F1. It would also survive a reload and open a picker you did not ask for after it.
- C: retry the press for a few frames. It still loses the press when the page takes longer than the retries.
- D: load the Convert page with the app, so it is never late. Every start loads the Convert code, and the next lazy page has the same gap.
- Do nothing: Ctrl+O right after switching to Convert sometimes does nothing, as AC-97.7's failures showed.

Refs: `convert-commands.ts:108-115`, `:348-352`, `ConvertPage.tsx:491-497`, `router.tsx:50`, `settings-commands.ts:10`, `:19`, `HelpCard.tsx:56-57`, 06 Held and Once rows (`06-gui.md:1697-1698`), D-1101, M-5.

### D-1109: What about other keys that act on a page that is still loading?

**I recommend A: record the one other gap, F1, as a known issue and leave the fix for later.** I checked every keyboard shortcut. On Convert and Capture, the page shortcuts only work once the page shows them as available, so they cannot be pressed too early. Ctrl+Enter presses the page's main button only while that button is enabled, so pressing it before the page appears does nothing, which is how it is meant to work; it is not recorded. F1 is different: on Convert or Capture, in the moment before the page appears, the help panel's toggle can be lost. Pressing F1 again works. A keeps this session to the two issues it was grouped for.

- B: fix F1 here with the same kind of hold. It changes the shell and the help panel, which nothing in this session tests.
- Do nothing: the gap is known but not written down anywhere.

Refs: `commandRegistry.ts:471-590` (the Capture chords are stateful), `:638-655` and `:122-127` (Ctrl+Enter), `shortcuts.ts:10-17`, `:256-282`, `AppShell.tsx:203-215`, `HelpCard.tsx:69`, grouping §3 Session 89 Gate, M-8.

### D-1110: Should the Ctrl+O test wait for the page before pressing the key?

**I recommend A: keep the existing test pressing Ctrl+O right after the switch, and add a new test that makes the page load late on purpose.** The triage (an agent decision, D-1101, not one of your rulings) said the existing test (AC-97.7) should wait for the page first. But a test that waits would pass with or without the fix, because it would never press during the load. Keeping it as it is makes it a check of what you do in real use, and it must pass 20 times in a row. The new test slows the Convert page's code by 1.5 seconds in the test app only, so a press before the page appears happens on every run, and it checks that exactly one picker opens. The written rule for these tests in the GUI plan (06) is updated to say this.

- B: make AC-97.7 wait for the page, as the triage said. It stops failing, but it no longer shows the fix works.
- C: keep AC-97.7 as it is with no new test. The fix is then proved only when the page happens to load late.
- Do nothing: AC-97.7 keeps failing about 1 run in 8.

Refs: `convert-queue.test.ts:1568-1583`, `06-gui.md:1700`, `known-issues.yaml:5364` (D-1101), grouping §3 Session 89 Order, M-6, M-8.

## Research References

- **Electron `protocol.handle`:** since Electron 25, `protocol.handle(scheme, handler)` can intercept a built-in scheme such as `file`, and `net.fetch(url, { bypassCustomProtocolHandlers: true })` serves the original response from inside the handler; it is the documented replacement for `interceptFileProtocol`. The race spec uses it to delay one chunk.
- **DOM `dispatchEvent` and `preventDefault`:** `dispatchEvent` returns `false` when the event is cancelable and a listener called `preventDefault`, and `true` otherwise; on a non-cancelable event `preventDefault` does nothing. `BROWSE_HOLD` uses that return value as the page's acknowledgement.
- **React 19 StrictMode** (`ui/package.json` `react` `^19.2.0`; `main.tsx:22-26`): in development, effects run, clean up and run again on mount; a take-once read in the effect opens the picker once. AC-157.6 renders in `StrictMode` to pin it.
- **Playwright `--repeat-each`:** runs each selected test the given number of times; with one worker and no retries (`ui/playwright.config.ts`) the runs are in series and a failure is never retried into a pass.

## Planning receipts

All under `C:/Temp/av-kit/queue-convert-fixes/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `qc89-probe.py`, `qc89-probe.txt` | `HEAD` `9d6d172` and a clean tree; line endings, sizes and SHA-256 prefixes of the scope; the four new files absent; the row-0 anchors, each counted once; MEU-156 and MEU-157 `pending` with their phase, band, matrix row and path; both issues `open`; grouping row 89 `proposed`; `decision_sources` on the grouping alone (D-1102 to D-1104) and with the register and both issues (D-1100 to D-1104) |
| `qc89-probe2.py`, `qc89-probe2.txt` | The behaviour files' anchors (AC-155.20 ends at `:1341`, CRLF; AC-155.21 ends at `:1112`, LF) and their describes |
| `qc89-probe3.py`, `qc89-probe3.txt` | The line endings of each line the plan edits (all CRLF except `DownloaderPage.tsx:260-262`, bare LF) |
| `qc89-expert-pass.txt` | The HDP §5a expert pass (coordinator-run, advisory) adopted in §Decision Log |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against Mat's ruling (D-1100), D-1101, grouping §3 Session 89, 10 §Cancel while paused, 06 §Convert browse waits for the page, and the code reads above | `qc-plan-2026-11-17-queue-convert-fixes` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-156.1 to AC-156.13 and AC-157.1 to AC-157.14 | `qc-execution-2026-11-17-queue-convert-fixes` |
