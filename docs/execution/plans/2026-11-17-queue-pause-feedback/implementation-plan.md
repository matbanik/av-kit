---
project: "2026-11-17-queue-pause-feedback"
date: "2026-11-17"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 88; issue QUEUE-PAUSE-NO-FEEDBACK (Mat's ruling 2026-11-16, 'Say what it does' and 'Small session after 83')"
meus: ["MEU-155"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: Pause says it waits for the current job

> **Project**: `2026-11-17-queue-pause-feedback`
> **Build Plan Section(s)**: 10 §Queue pause feedback (residual) (MEU-155, matrix 10.10), which row 1 adds to `docs/build-plan/10-queue-card-ui.md` with the anchor `queue-pause-feedback-residual`; the toolbar canon is 10 §Toolbar reduction (`10-queue-card-ui.md:236-248`) and the pause scope rule (`:308-309`); Transcript's waits follow 03 §TranscriptService (`03-service-layer.md:193`, §Rate cap `:256`), where row 3b adds one paragraph.
> **Status**: said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 2 (.agent/context/handoffs/2026-11-17-queue-pause-feedback-plan-critical-review.md). Session 88 of the post-rc.3 grouping, added 2026-11-17 after Session 81's commit (grouping §3). **Amended in execution (A1, 2026-11-17):** row 4 found Clear finished moving when the status text wraps the header (S8), and Mat chose to pin the toolbar right (D-1098, USER_EXPLICIT 2026-11-17 'Pin toolbar right (Recommended)'); §Execution amendment A1 says what changed. A1 has no plan review of its own; the H1-7 execution review covers it.

---

## Goal

**Goal anchor:** on the Convert and Downloader pages the toolbar's Pause button reads "Pause after this job"; after a click it reads "Pausing…" and is disabled, and the processor status reads "Queue stops when the current job ends", until the queue reports Paused (then Resume shows) or ends in another way; Cancel still stops the running job at once; the services keep pausing between jobs; on the Transcript page "Pause" keeps its name and its waits between videos end within a second of a pause or stop (D-1090); and no API, OpenAPI document or MCP tool changes.

**Why.** In Session 81's row-5 check Mat pressed Pause during a Convert job and nothing seemed to happen; he had to Cancel the job to stop it (`QUEUE-PAUSE-NO-FEEDBACK`, `known-issues.yaml:5381`). Pause is queue-level and lands only between jobs: `conversion.py:496` and `download.py:659` read `_pause` only before they pick the next job. Between the click and the end of the job the GUI showed the same enabled "Pause" button and the same "Processing…" chip, because the backend reports `Processing` until the worker loop pauses.

**Mat's ruling (2026-11-16, quoted in grouping §3 Session 88 and the issue):** "Say what it does" and "Small session after 83". The button reads "Pause after this job". After a click it shows "Pausing…", and the status says the queue stops when the current job ends. Cancel stays the way to stop at once. The behaviour is proved with Electron E2E tests in the gate, not with manual checks ("why are you giving me e2e tests manually! This should be done with framework and scripts! It delays the development!").

**What the code shows (plan-time reads at `HEAD` `ba6d8ef`):**

- `QueueToolbar` (`components/queue/QueueToolbar.tsx`, CRLF) is mounted only through `QueueHeaderRow` (`actions={<QueueToolbar {...toolbar} />}`, `QueueHeaderRow.tsx:134`, prop type `QueueToolbarProps`), and only `ConvertPage.tsx:861` and `DownloaderPage.tsx:832` mount that with a `toolbar` object. The label comes from `TOOLBAR_CONTROL_LABELS.pause` (`:51`); the toggle is `:204-217`.
- **Transcript does not share it.** It has its own `TranscriptToolbar.tsx` (CRLF; "Exactly three interactive elements: Start, one Pause/Resume node and Stop"), pinned by 11 TR1 and TR2 (`11-page-layout.md:28-29`) and by `layout-canon.test.ts:112`. The issue's root cause says the toolbar is shared with Transcript; that sentence is wrong, and D-1090 settles what Transcript does.
- The pages compute the chip text with `processorLabel(processorState)` (`ConvertPage.tsx:241`, `DownloaderPage.tsx:257`): Idle hides the chip, Processing reads "Processing…", Paused reads "Queue Paused".
- The commands (`convert-commands.ts:231-238`, `download-commands.ts:156-163`) POST pause when `controlEnabled('pause', ctx)` (state `Processing`) and invalidate the list. The palette's "Pause conversions" and "Pause downloads" (`deliverPalettePause`) reach the same functions; there is no pause keyboard shortcut (no pause entry sets the optional `shortcut` field, `commandRegistry.ts:112`; see `download:pause` at `:233-242` and `convert:pause` at `:396-405`), and the palette lists these stateful commands only on their own page while they are enabled (`shortcuts.ts:256-282`). `queueContext()` reads the cached list envelope, which keeps `processor.current_job_id` (`useConversionQueue.ts:56`, `useDownloadQueue.ts:47`).
- No backend field says "a pause is requested". Adding one would change the list envelope, the OpenAPI document and the MCP tool shapes (M-4), so the pending state is held in the renderer (D-1097).
- A job that fails while a pause is pending ends the queue Paused, not Idle: `_finish(Failed)` returns to the loop, which reads `_pause` first (`conversion.py:553-558`, `:496`). Between jobs `current_job_id` is `None` (`_finish`, `:672-676`).
- **Transcript's pause can wait minutes, not seconds.** Its between-videos check is `transcript.py:491` (`:407` is the between-channels check), and it runs before the waits: `self._sleep(delay)` (`:495`, 6 s at defaults), every `batch_size` videos `self._sleep(batch_pause)` (`:497`, 300 s), and on a retry `self._sleep(retry_delay)` (`:581`, 30 s); defaults at `settings.py:70-74`. A pause clicked at the start of the batch rest lands about 5 minutes later. The rate-cap wait already ends within a second (`_await_request_slot`, `:655-671`; 03 §Rate cap, `03-service-layer.md:256`).

## Execution amendment A1 (2026-11-17)

- **Why.** Row 4's first counted run (`C:/Temp/av-kit/queue-pause-feedback/qp-row4-e2e-r1.txt`) failed AC-155.15 on Convert: Clear finished's x read 912.1, 490.5 and 892.8 px in the three toggle states. The toggle kept its width (its label fit in every state), but the toolbar follows the chips in the header's wrapping row (`QueueHeaderRow.tsx:65`), so the long status `Queue stops when the current job ends` pushed it to a second line, and the chip and count text beside it moved it about 19 px. That is S8 (a layout choice, M-5), and the fix changes the named fixture (M-7), so it went to Mat. His answer (AskUserQuestion, 2026-11-17, relayed verbatim by the coordinator): 'Pin toolbar right (Recommended)'. The option read: 'Add right-alignment (ml-auto) to the Convert/Downloader queue toolbar, so its buttons stay at the same x whatever the status text says; if space runs out it drops to the next line at the right edge. Updates the header snapshot fixture by that one class. Transcript is untouched (it has its own toolbar).' (D-1098, `resolution: human`, `mandatory: [M-5, M-7]`).
- **What changes.** `TOOLBAR_END`: the root container of `QueueToolbar` (`QueueToolbar.tsx:201`, `relative inline-flex self-start`) gains ` ml-auto` at the end of its class, so the toolbar sits at the right end of its line in the header and its x depends only on the header's width and its own width, which `TOGGLE_WIDTH` keeps fixed. `QueueHeaderRow.tsx` is not changed (it stays read, never changed): the toolbar's own root carries the alignment, and Transcript passes its own `TranscriptToolbar` as the frame's `actions` (`TranscriptPage.tsx:558`), so Transcript's header is untouched. The named fixture edit (`PINS_NAMED`, row 2) gains one more change: in key `header`, the toolbar root's `class` becomes `relative inline-flex self-start ml-auto`; nothing else in the fixture moves beyond what row 2 already names.
- **Red and Green for A1.** The fixture is edited first and `queue-card-slots.test.tsx` is run against the unchanged toolbar, so it fails by assertion (`qp-a1-red.txt`); then the fixture's new hash replaces its row-2 entry in `qp-155-red-hashes.json` (the row-2 file is kept as `qp-155-red-hashes-pre-a1.json`; the other three hashes do not change), and the toolbar edit follows. Row 3 runs again, then a full Vitest run, then the whole row 4 cell, the build, the three runs of the new file and the `convert-queue` and `download-queue` suites (the 700-pixel header test at `convert-queue.test.ts:1409-1426` included).
- **AC-155.15 under A1.** The x check stays as written, on both pages. Where space runs out the toolbar drops to the next line at the right edge, so its y may change between states; that is accepted under the ruling ('drops to the next line at the right edge'), and x must still be equal within 0.5 px.
- **What stays.** No other product file changes; AC-155.1 to AC-155.22 keep their ids (AC-155.2 pins the toggle's classes, not the root's). A new S5 or S8 (a 700-pixel overflow or another failing test caused by the right alignment) stops again; nothing is shrunk to pass. A1 has no plan review of its own; the H1-7 execution review covers it.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-17). The change touches one toolbar component, two command modules, two pages, one help string, one new renderer module and the Transcript service's waits, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go under `C:/Temp/av-kit/queue-pause-feedback/`, named `qp-*` (planning receipts are `qp88-*`).
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE` (Session 79 RULE-3, Session 85 RULE-2).
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`. Playwright runs with `ELECTRON_RUN_AS_NODE` cleared.
  - Each Electron test stops the backend it started only by the pid it recorded, checked against that pid's start time. No row stops a process by image name; other worktrees run their own apps.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local (Electron, FFmpeg and the real backend; grouping §3 "Cloud/local: local").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), run by the coordinator, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `qp-plan-2026-11-17-queue-pause-feedback` and `qp-execution-2026-11-17-queue-pause-feedback`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Sessions 82 and 83 are committed (`86ee8e3`, `ba6d8ef`). Other sessions may write into `main` while this one runs, so the baselines and scope checks are path-scoped and bound to content at row 0 (§Verification Plan 1).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-155 queue pause feedback | `.agent/context/handoffs/2026-11-17-queue-pause-feedback-MEU-155-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-17-queue-pause-feedback-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-17-queue-pause-feedback-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local checkers (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py` |
| WP-2 | Register MEU-155 (row 1) | WP-1 | shared | `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, 10 §Queue pause feedback, matrix row 10.10 |
| WP-3 | Red, then Green (rows 2, 2b, 3 and 3b) | WP-2 | shared | `pause-request.ts`, `QueueToolbar.tsx`, the two command modules, the two pages, the help string, the fixture, `queue-pause-feedback.test.tsx`, the two appended page tests; `transcript.py`, the 03 paragraph, `test_transcript_pause_wake.py` |
| WP-4 | Electron proof (row 4) | WP-3 | shared | `ui/tests/e2e/queue-pause-feedback.test.ts` and its three run receipts |
| WP-5 | Delivered note, issues and status (rows 5 and 6) | WP-4 | shared | 10's Delivered note, `known-issues.yaml` and `.md` (one issue resolved, one added), MEU-155 `ready_for_review`, grouping §6 row 88 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.** Two decisions are briefs (D-1090 and D-1091, §Decision Log): they choose how the queue pages behave where the spec leaves it open, so the HDP writes them up for you. Your hand-over for this grouping ('like we did here. But use the new HDP process.', 2026-11-15) settles them on the recommendation, and they are recorded that way; §Decision Log says why Session 88 is inside that hand-over. Read them if you want to overrule one before execution. There is no human check row: the Electron tests in row 4 and the gate prove the behaviour.
>
> **What changes for you:**
>
> - On Convert and Downloader the button reads **Pause after this job**. Click it during a job and it reads **Pausing…** (greyed out), and the status beside the queue reads **Queue stops when the current job ends**. When the job finishes, the queue pauses and the button reads **Resume**.
> - The button keeps one width in all its states, so **Clear finished** beside it does not move under your cursor.
> - **Cancel** on the running job still stops it at once, also while Pausing… shows.
> - If the job fails while Pausing… shows, the queue still pauses (Resume shows).
> - The palette's "Pause conversions" and "Pause downloads" do the same thing as the button, and are hidden while Pausing… shows.
> - Pausing… shows only for a pause sent from this window, and it is still there when you come back to the page while the job runs, however long you were away. A pause from an MCP client or another window, or one sent before you reload the app, shows "Pause after this job" until the queue pauses; so does a click when the app cannot read the queue right after it, and clicking again then does no harm (D-1091).
> - **Transcript keeps "Pause", and now pauses promptly**: today a pause there can wait up to 5 minutes for the rest between batches of videos, and 30 s for a retry; after this change those waits end within a second of Pause or Stop (D-1090).
> - The Downloader help's "Pause vs cancel" text now says that Pause waits for the current download.

## Proposed Changes

### Single-statement contracts

- **`PAUSE_LABEL` (D-1093):** `TOOLBAR_CONTROL_LABELS.pause` is `'Pause after this job'`; `resume` stays `'Resume'`; the test ids `queue-toolbar-pause` and `queue-toolbar-resume` and the Pause and Play icons are unchanged.
- **`PAUSE_PENDING_TOGGLE` (D-1091):** `QueueToolbarProps` gains `pausePending?: boolean` (default `false`), and `QueueToolbar.tsx` exports `PAUSE_PENDING_LABEL = 'Pausing…'` (U+2026). When `pausePending` is true and `processorState` is not `Paused`, the toggle keeps the test id `queue-toolbar-pause` and the Pause icon, reads `PAUSE_PENDING_LABEL`, and is `disabled` whatever `canPauseResume` says. When `processorState` is `Paused`, `pausePending` is ignored and the toggle is Resume as today. Start, Clear finished and Clear all do not read it.
- **`TOGGLE_WIDTH` (D-1091):** `QueueToolbar.tsx` exports `PAUSE_TOGGLE_WIDTH_CLASSES = 'min-w-[12rem] justify-center'`, and the toggle's `className` is `controlClasses` plus a space plus that constant, in every state (Pause after this job, Pausing…, Resume, disabled). 12rem (192 px at the 16 px root) holds "Pause after this job" with its icon, gap and padding (about 172 px at `text-sm`), so the toggle keeps one width and Clear finished does not slide under the cursor (`ConvertPage.tsx:876`, `:880` and `DownloaderPage.tsx:841-850` run `clearFinishedNow` with no confirm). The other three controls keep `controlClasses` alone.
- **`TOOLBAR_END` (D-1098, amendment A1):** the toolbar's root container (`QueueToolbar.tsx:201`) has the class `relative inline-flex self-start ml-auto`, so the toolbar sits at the right end of its line in the header row and drops to the next line at the right edge when space runs out; its x then depends only on the header's width and its own fixed width (`TOGGLE_WIDTH`). `QueueHeaderRow.tsx` and `TranscriptToolbar.tsx` are not changed.
- **`PAUSE_MARK` (D-1097):** the new module `ui/src/renderer/src/lib/queue/pause-request.ts` (LF) keeps one mark per queue kind (`'convert' | 'download'`) in the shared `queryClient` under `pauseRequestKey(kind)` = `['queue-pause-request', kind]`, value `{ jobId: string | null; markedAt?: number }` (`markedAt` is `Date.now()` on an unbound mark, `jobId` `null`, and absent otherwise), with `gcTime: Infinity` set through `queryClient.setQueryDefaults`, so the mark outlives a page unmount. It exports `markPauseRequested(kind, jobId)`, `clearPauseRequest(kind)`, `readPauseRequest(kind)` and `PAUSE_UNBOUND_MS = 15_000`.
- **`PAUSE_PENDING_RULE` (D-1091):** the pure `isPausePending(mark, processor, now = Date.now())`, where `processor` is `{ state, current_job_id } | undefined`, is true exactly when `mark !== null`, `processor !== undefined`, `processor.state === 'Processing'`, and either `mark.jobId !== null` and (`processor.current_job_id == null` or `processor.current_job_id === mark.jobId`), or `mark.jobId === null` and `now - mark.markedAt < PAUSE_UNBOUND_MS`. An unbound mark is never a wildcard past that bound: inside it the hook binds it to the first job id it sees (`PAUSE_PENDING_HOOK`), and after it the mark is spent. A `null` `current_job_id` during `Processing` keeps a job mark pending, because between jobs the id is `null` for a moment (`conversion.py:672-676`).
- **`PAUSE_PENDING_HOOK` (D-1091, D-1097):** `usePausePending(kind, processor)` takes the observed `processor` of the list envelope, `undefined` while no list has been read. It re-renders when the mark changes and returns `isPausePending(mark, processor, Date.now())`. **It acts only on an observed list:** while `processor` is `undefined` (for example on a remount after the list's cache entry was collected, `gcTime` 5 minutes, `query-client.ts:3-4`) it returns `false` and leaves the mark as it is, so a list not yet read never counts as Idle. With an observed `processor`, in effects, never during render: an unbound mark inside `PAUSE_UNBOUND_MS` that meets `Processing` with a non-null `current_job_id` is bound to that id (`markPauseRequested(kind, id)`) and is a job mark from then on; a mark for which the rule is false is cleared, so an old mark cannot come back when the queue runs again (after Paused, Idle, another job, another client's resume, or a spent unbound mark). While an unbound mark exists, a timer at `markedAt + PAUSE_UNBOUND_MS` re-checks it, so its end does not wait for a poll.
- **`PAUSE_MARK_SET` (D-1091, D-1092):** `pauseConversion` and `pauseDownload` return without a request when `controlEnabled('pause', ctx)` is false or `isPausePending(readPauseRequest(kind), { state: ctx.processorState, current_job_id: ctx.currentJobId })` is true. Otherwise they POST pause. Only after the POST resolves they `await queryClient.cancelQueries({ queryKey: QUERY_KEY })`, read the list (`parseListEnvelope(await apiFetch('/conversions'))`, or `/downloads`), `await queryClient.cancelQueries({ queryKey: QUERY_KEY })` again, write the list with `queryClient.setQueryData(QUERY_KEY, …)` (the `replaceQueueFromList` pattern, `download-commands.ts:127-130`), and then set the mark from what that list shows, so it names the job running after the pause landed, not the one in a cache up to a second old: `Processing` with a job id → `markPauseRequested(kind, id)`; `Processing` with no job id (between jobs) → `markPauseRequested(kind, null)`, an unbound mark that `PAUSE_PENDING_HOOK` binds to the next job id it sees within `PAUSE_UNBOUND_MS`; `Paused` or `Idle` → no mark (the pause has landed, or nothing is left to wait for). The two cancels drop a poll that started before the read and would answer after it with an older list; `setQueryData` alone does not cancel it. If the read fails, they set **no mark**, invalidate the list as today, and resolve: the button stays "Pause after this job" and enabled, and a second click is harmless, because the backend's pause only sets a flag (`conversion.py:269-270`, `download.py:448-449`; the routes answer 202, `packages/api/src/avkit_api/routes/conversions.py:215-223`, `downloads.py:157-165`). A failed POST marks nothing and rejects as today. `queueContext()` in both modules adds `currentJobId: envelope.processor.current_job_id ?? null`, which the guard above reads. The job-id check in `PAUSE_PENDING_RULE` stays: it clears a mark that another client's resume left behind.
- **`PAUSE_MARK_CLEAR` (D-1091):** `startConversion`, `resumeConversion`, `cancelConversion` and the download equivalents call `clearPauseRequest(kind)` after their POST resolves.
- **`PAUSE_STATUS` (D-1093):** `pause-request.ts` exports `PAUSE_PENDING_STATUS = 'Queue stops when the current job ends'`. Each page computes `pausePending = usePausePending(kind, queue.data?.processor)` (the observed processor, `undefined` before the first list read, not the `Idle` the page maps missing data to at `ConvertPage.tsx:109-113` and `DownloaderPage.tsx:180-184`), passes `processorLabel={pausePending ? PAUSE_PENDING_STATUS : label}` and adds `pausePending` to its `toolbar` object. The chip keeps its Processing tone.
- **`PAUSE_COMMAND_STATE` (D-1092):** in each page's `PAGE_STATE`, `'convert:pause'` and `'download:pause'` gain `&& !pausePending`; the other four entries are unchanged, so `'convert:cancel'` and `'download:cancel'` stay true while Pausing… shows.
- **`CANCEL_NOW`:** Cancel (the card's primary action, the palette and the confirm) is unchanged and stays enabled while Pausing… shows. It ends the pending state: the backend goes Idle, and the hook clears the mark.
- **`BETWEEN_JOBS`:** `conversion.py` and `download.py` are not changed; Convert and Downloader keep pausing between jobs. In `transcript.py` only the waits change (`TRANSCRIPT_WAKE`); the pause and stop checks stay where they are.
- **`TRANSCRIPT_WAKE` (D-1090):** `TranscriptService.__init__` creates `self._wake = threading.Event()`, and when no `sleep` is passed it sets `self._sleep = self._wait` (an injected `sleep` is kept as it is, so the tests' recorded whole durations do not change). `_wait(seconds)` calls `time.sleep(0)` when `seconds <= 0`, as today; otherwise, until `time.monotonic()` reaches the deadline, it returns at once when `_pause` or `_stop` is set, else waits on `self._wake` for the time left, and after a wake with neither flag set it clears the event under `_lock` and waits out the rest (no busy loop). `pause_processing` and `stop_processing` set `_wake` after they set their flag; `start_processing` and `resume_processing` clear it under `_lock` where they clear the flags. No call site changes: the delay (`:495`), batch-rest (`:497`), retry (`:581`), per-parent (`:427`) and rate-cap (`:670`) waits all go through `self._sleep`. The checks after each wait already end the run (`:491`, `:568`, `:671`). No API, OpenAPI, MCP or setting changes. 03 §TranscriptService gains one paragraph after §Rate cap (`03-service-layer.md:256`) that says so.
- **`TRANSCRIPT_KEPT` (D-1090):** `TranscriptToolbar.tsx` and the Transcript page are not changed; the button there still reads "Pause".
- **`PALETTE_LABELS_KEPT` (D-1092):** the palette labels "Pause downloads" (`commandRegistry.ts:234`), "Pause transcripts" (`:310`) and "Pause conversions" (`:397`) are unchanged.
- **`HELP_PAUSE` (D-1093):** the Downloader help topic `pause` keeps its title "Pause vs cancel"; its body becomes "Pause after this job lets the current download finish, then stops the queue with its order intact; Resume continues later. Cancel stops the current download at once and does not delete finished files."
- **`PINS_NAMED` (D-1095):** exactly one existing test expectation changes, the queue header fixture's toggle (its text and its two width classes) and, under amendment A1, its toolbar root's ` ml-auto` (§Test pins); every other pin, the Python ones included, passes unchanged.

### MEU-155: queue pause feedback

1. **`lib/queue/pause-request.ts` (new, LF):** `PAUSE_MARK` (with `PAUSE_UNBOUND_MS`), `PAUSE_PENDING_RULE`, `PAUSE_PENDING_HOOK`, `PAUSE_PENDING_STATUS`. The hook subscribes to the mark through `useQuery({ queryKey: pauseRequestKey(kind), queryFn: () => readPauseRequest(kind), enabled: false, staleTime: Infinity, gcTime: Infinity })` or an equivalent `useSyncExternalStore` on the query cache; the AC tests fix the behaviour, not the hook's inside.
2. **`QueueToolbar.tsx` (CRLF, kept):** `PAUSE_LABEL` at `:51`; `PAUSE_PENDING_LABEL`; `PAUSE_TOGGLE_WIDTH_CLASSES` (`TOGGLE_WIDTH`); ` ml-auto` on the root container at `:201` (`TOOLBAR_END`, amendment A1); the `pausePending` prop in `QueueToolbarProps` and in the toggle at `:204-217` (`disabled={!canPauseResume || (pausePending && !paused)}`).
3. **`convert-commands.ts`, `download-commands.ts` (CRLF, kept):** `queueContext()` adds `currentJobId`; `PAUSE_MARK_SET` and `PAUSE_MARK_CLEAR`.
4. **`ConvertPage.tsx` (CRLF, kept) and `DownloaderPage.tsx` (MIXED, kept):** `PAUSE_STATUS`, the `pausePending` toolbar prop and `PAUSE_COMMAND_STATE`. In `DownloaderPage.tsx` the `QueueHeaderRow` block `:832-854` is bare LF and the `PAGE_STATE` block `:540-546` and the label line `:257` are CRLF; each new or changed line takes the ending of the line before it (`eol-check.py`).
5. **`downloader-help-content.ts` (CRLF, kept):** `HELP_PAUSE`.
6. **`ui/tests/unit/fixtures/queue-slot-baseline.json` (CRLF, kept):** in key `header`, the toggle's `class` gains ` min-w-[12rem] justify-center` at its end, and the one `Pause</button>` becomes `Pause after this job</button>`; under amendment A1 the toolbar root's `class` `relative inline-flex self-start` also gains ` ml-auto` at its end (`PINS_NAMED`, row 2, D-1098).
7. **Tests:** `ui/tests/unit/queue-pause-feedback.test.tsx` (new, LF) with AC-155.1 to AC-155.6, AC-155.9, AC-155.13, AC-155.14, AC-155.19 and AC-155.22; two appended tests in `convert-page.behavior.test.ts` (AC-155.7, AC-155.20) and two in `downloader-page.behavior.test.ts` (AC-155.8, AC-155.21); `ui/tests/e2e/queue-pause-feedback.test.ts` (new, LF) with AC-155.10 to AC-155.12 and AC-155.15.
8. **`packages/core/src/avkit_core/services/transcript.py` (LF, kept):** `TRANSCRIPT_WAKE` (row 3b).
9. **`docs/build-plan/03-service-layer.md` (CRLF, kept):** one paragraph, **Waits end on pause or stop (Session 88)**, inserted after §Rate cap (`:256`): the delay, batch-rest and retry waits, like the rate-cap wait, end within a second of a pause or stop, and the next check then pauses or stops the run; an injected `sleep` is used as it is (row 3b).
10. **`tests/unit/test_transcript_pause_wake.py` (new, LF):** AC-155.16 to AC-155.18 (row 2b). It builds the service like `_transcript_stack` (`tests/unit/test_services.py:1197-1237`) from that module's fakes (`from tests.unit.test_services import …`, the `tests/e2e/test_api_download_visibility.py:19` precedent), but passes no `sleep`, so the service's own wait runs.
11. **Registration (row 1, D-1096):** `register-meu-155.py` adds MEU-155 to `meu-status.yaml`, 10 §Queue pause feedback (residual) and matrix row 10.10; row 5 adds 10's Delivered note.
12. **Known issue (row 6):** `tools/issue_triage.py add` registers `QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT` (§Out of Scope); nothing in the code changes for it.

### Test pins

Each pin is cited by file, line and description (Session 83 RULE-1: no other family's AC ids are copied here).

| Pin | What it checks | After this change |
|---|---|---|
| `ui/tests/unit/fixtures/queue-slot-baseline.json`, key `header`, read by `queue-card-slots.test.tsx:153` ("QueueHeaderRow still renders the exact pre-change markup") | The header row's full markup, including the toggle's text | **Changes (the one named change).** Old: the markup holds `Pause</button>` once, and the toggle's `class` equals the other controls'. New: it holds `Pause after this job</button>` once and `Pause</button>` nowhere, and the toggle's `class` ends ` min-w-[12rem] justify-center` (the only class with `min-w-`); under amendment A1 the toolbar root's `class` becomes `relative inline-flex self-start ml-auto`; nothing else in the fixture moves. The test file itself is not edited. Row 2 makes the edit, so the test fails at Red by assertion and passes at Green. |
| `queue-toolbar.test.ts:104` ("the toolbar renders exactly … with persistent labels") | Labels equal `TOOLBAR_CONTROL_LABELS` | Unchanged; it reads the constant |
| `queue-toolbar.test.ts:149` ("pause-resume is one button whose label and testid follow …") | Label and test id per state | Unchanged; it reads the constant, and `pausePending` defaults to `false` |
| `queue-header-row.test.tsx:126` | The Idle chip is hidden and `queue-toolbar-pause` exists | Unchanged; test ids kept |
| `convert-page.behavior.test.ts:1219` ("mounts one shared queue header with live selection, all counts, and toolbar") | Chip reads Processing before a click; one pause POST after it | Unchanged; the chip is read before the click, and `queryClient.clear()` runs between tests (`:818`, `:875`) |
| `downloader-page.behavior.test.ts:999` ("mounts one shared queue header with live selection, status counts, and toolbar") | The same on Downloader | Unchanged, for the same reasons (`queryClient.clear()` at `:486`, `:560`) |
| `convert-page.test.ts:81`, `downloader-page.test.ts:39` | The `queue-toolbar-pause` test id is in each page's id inventory | Unchanged |
| `layout-canon.test.ts:112` | 11 TR1's text (Transcript's three actions) | Unchanged (D-1090) |
| `queue-canon.test.ts` | Matrix rows 10.1 to 10.9, phase 10's MEU ids and the hub row | Unchanged; row 1 adds row 10.10 and MEU-155, which its patterns do not reject (`10\.1\s*\|` does not match `10.10 |`); row 1 runs it |
| `help-card.test.ts` | The help card's structure | Unchanged; no test reads the `pause` body |
| `convert-commands.test.ts:150`, `download-commands.test.ts:151` | The command id lists | Unchanged |
| `ui/tests/e2e/convert-queue.test.ts:721`, `:770`, `:1387`, `:1421` and `download-queue.test.ts:555`, `:616`, `:1548`, `:1581` | The `queue-toolbar-pause` test id is visible or clickable | Unchanged; they read test ids, each test launches a fresh app, and their seams answer pause with `Paused`, which clears the mark. The narrow-width header test (`convert-queue.test.ts:1409-1426`, 700 px) also passes with the wider toggle, or S8 applies |
| `tests/unit/test_services.py:1363` (the retry test asserts `7 in sleeps`), `:1379-1380` (the delay and batch test asserts `6 in sleeps` and `9 in sleeps`) and `:3088` (the default-cap test asserts the sleeps are within `{0.0, 6.0, 300.0}`) | The Transcript waits are called with whole durations | Unchanged: these tests inject `sleep` through `_transcript_stack` (`:1234`), which `TRANSCRIPT_WAKE` keeps as it is |

A sweep of `ui/tests` for a literal `'Pause'` or `"Pause"` label finds none (`qp88-probe.txt`; the fixture is the only text match). Any other existing test that fails after Green is S5, an M-7 question, not a fix.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| The pause mark in the query cache | `pause-request.ts` | `{ jobId: string \| null; markedAt?: number }` per kind (`markedAt` only on an unbound mark); renderer memory only, never persisted | None; not sent anywhere |
| `QueueToolbarProps` | `QueueToolbar.tsx` | `pausePending?: boolean`, default `false` | Optional, so `QueueHeaderRow` and other callers compile unchanged |
| The list envelope's `processor` | Backend services (unchanged) | `state`, `current_job_id` read as today | Unchanged |

No API route, OpenAPI document, MCP tool shape, backend service, persisted setting or database schema changes (M-4 kept clear).

### Acceptance Criteria

Vitest and Playwright titles start with `AC-155.<n>` followed by a space, so `red-check.py --require AC-155.1` never matches `AC-155.10`.

- **New names fail by assertion at Red.** `queue-pause-feedback.test.tsx` loads the new module through `import.meta.glob('../../src/renderer/src/lib/queue/pause-request.ts', { eager: true })`, which gives an empty object while the file is absent, and each test asserts `typeof pq.isPausePending === 'function'` (and the other names it uses) first. It imports `QueueToolbar.tsx` as a namespace (`import * as qt from …`) and asserts `qt.PAUSE_PENDING_LABEL === 'Pausing…'` first. The appended page tests AC-155.20 and AC-155.21 load the module through the same `import.meta.glob` and assert `typeof pq.readPauseRequest === 'function'` first. So Red fails by assertion, never by a missing module (Session 52 RULE-4).
- **AC-155.9 is a pin set.** It is not `--require`d at Red; row 3 runs it.
- **AC-155.10 to AC-155.12 and AC-155.15 are Electron tests.** They are written in row 4 after Green and run three times there and once in the gate; they are not part of the Red run (they need a build).
- **AC-155.16 to AC-155.18 are pytest tests** in `tests/unit/test_transcript_pause_wake.py`, named `test_ac_155_16_…` to `test_ac_155_18_…`. Row 2b runs them at Red; each fails by assertion (a wait that runs its whole length), never by import: the file imports only names that exist today, and AC-155.18 reads `service._sleep` through `getattr`.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-155.1 | unit | `TOOLBAR_CONTROL_LABELS.pause === 'Pause after this job'` and `.resume === 'Resume'`. A rendered `QueueToolbar` in `Processing` with `canPauseResume` shows `queue-toolbar-pause`, enabled, with the text "Pause after this job"; in `Paused` it shows `queue-toolbar-resume` with "Resume". | Human-approved (Mat 2026-11-16, grouping §3 Session 88: "The button reads 'Pause after this job'") | In Red the label is "Pause" |
| AC-155.2 | unit | With `pausePending` true and `Processing`: test id `queue-toolbar-pause`, text `Pausing…` (U+2026, equal to `PAUSE_PENDING_LABEL`), `disabled` although `canPauseResume` is true, and a click calls no `onPauseResume`. With `pausePending` true and `Paused`: `queue-toolbar-resume`, enabled. With `pausePending` omitted: today's toggle markup plus the width classes. In all three cases the toggle's `className` contains `PAUSE_TOGGLE_WIDTH_CLASSES` (`'min-w-[12rem] justify-center'`) and Start, Clear finished and Clear all do not contain `min-w-`; they keep their `disabled` state. | Human-approved (Mat: "After a click it shows 'Pausing…'"); Local Canon (10 §Toolbar reduction: one toggle reflecting `processor.state`); D-1091 | An enabled Pausing… button, a changed test id, or a toggle without the width classes fails |
| AC-155.3 | unit | `isPausePending` truth table, with `now` passed: no mark → false; any mark with `processor` `undefined` → false; mark `{ jobId: 'j1' }` with `Processing` and `j1` → true, with `null` → true, with `j2` → false; mark `j1` with `Paused` or `Idle` → false; an unbound mark `{ jobId: null, markedAt: t }` with `Processing` and `null` or `j2` → true at `now = t + 1000` and false at `now = t + PAUSE_UNBOUND_MS`, and with `Paused` → false. `PAUSE_UNBOUND_MS === 15000`. `markPauseRequested('convert', 'j1')` then `readPauseRequest('convert')` gives `{ jobId: 'j1' }` with no `markedAt`, and `readPauseRequest('download')` gives `null`; under fake time `markPauseRequested('convert', null)` gives `{ jobId: null, markedAt: Date.now() }`; `clearPauseRequest` gives `null`. With fake timers, a mark set with no observer is still there after 10 minutes (default `gcTime` is 5). `PAUSE_PENDING_STATUS === 'Queue stops when the current job ends'`. | Local Canon (D-1091, D-1097; plan review R1-F2) | An unbound mark pending past its bound, a mark pending for a missing list, a mark lost after 5 minutes, or a wrong cell, fails |
| AC-155.4 | unit | Convert commands, with the cached envelope `Processing`, `current_job_id: 'c1'` and `fetch` stubbed (the `GET /conversions` after the POST answers `Processing` with `c1`): `pauseConversion()` POSTs `/conversions/pause` once, then GETs `/conversions` once, and leaves `{ jobId: 'c1' }`; a second `pauseConversion()` sends no request. **Ordering:** a list fetch started on the shared client before the call (`queryClient.fetchQuery` on `QUERY_KEY`, its response held by the stub) and answered with `Processing`/`c0` after `pauseConversion()` resolves leaves the cache holding the `c1` envelope. With the POST answering 500, no mark is set and the call rejects. After a mark, `cancelConversion()`, `startConversion()` (cache `Paused` with a Pending item and FFmpeg available) and `resumeConversion()` (cache `Paused`) each POST once and leave `null`. | Local Canon (D-1091 `PAUSE_MARK_SET`, D-1092; plan review Q2) | A second POST, a mark after a failed POST, or an older list written over the read, fails |
| AC-155.5 | unit | The same checks, the ordering one included, for `pauseDownload`, `cancelDownload`, `startDownload` and `resumeDownload` against `/downloads/*`, with `current_job_id: 'd1'` in the cache and in the `GET /downloads` after the POST. | Local Canon (D-1091, D-1092) | As AC-155.4 |
| AC-155.6 | unit | `usePausePending(kind, processor)` through `renderHook` inside a `QueryClientProvider` on the shared client: with no mark it returns false; after `markPauseRequested('convert', 'c1')` it re-renders true for `Processing`/`c1`; rerendered with `processor` `undefined` it returns false and the mark is still `{ jobId: 'c1' }`; rerendered with `Paused` it returns false and the mark is `null`. A `c1` mark with `Processing`/`c2` → false and `null`; a `c1` mark with `Idle` → false and `null`. An unbound mark (`markPauseRequested('convert', null)`, fake time): `Processing`/`null` → true and the mark stays unbound; `Processing`/`c5` → true and the mark becomes `{ jobId: 'c5' }`; then `Processing`/`c6` → false and `null`. A second unbound mark with `Processing`/`null` and no rerender: after `vi.advanceTimersByTime(PAUSE_UNBOUND_MS)` the hook has re-rendered false and the mark is `null`. | Local Canon (D-1091 `PAUSE_PENDING_HOOK`; plan review R1-F1, R1-F2) | A mark cleared by a missing list, a mark that survives Paused, Idle or another job, or an unbound mark that never binds or never ends, fails |
| AC-155.7 | unit | Appended to `convert-page.behavior.test.ts` after the shared-header test at `:1219`, in its describe (envelope `Processing`, `current_job_id: 'job-2'`): a click on `queue-toolbar-pause` POSTs once; the toolbar then shows `Pausing…`, disabled; `convert-processor` reads "Queue stops when the current job ends"; `getCommandState('/convert')` has `convert:pause` false and `convert:cancel` true; a second click sends nothing. Then `processorState = 'Paused'` and the list is invalidated: the toolbar shows `queue-toolbar-resume` "Resume" and the chip "Queue Paused". | Human-approved (Mat's ruling, all four parts); D-1092 | In Red the chip still reads Processing and the button stays enabled |
| AC-155.8 | unit | Appended to `downloader-page.behavior.test.ts` after the shared-header test at `:999`, in its describe: the same sequence on `processor-indicator`, `/downloads/pause` and `getCommandState('/')` with `download:pause` false and `download:cancel` true. | As AC-155.7 | As AC-155.7 |
| AC-155.9 | unit | Pins: the fixture holds `Pause after this job</button>` once and `Pause</button>` nowhere (read as UTF-8 in the new file); `queue-card-slots.test.tsx`, `queue-toolbar.test.ts`, `queue-header-row.test.tsx`, `convert-page.test.ts`, `downloader-page.test.ts`, `convert-commands.test.ts`, `download-commands.test.ts`, `help-card.test.ts`, `layout-canon.test.ts`, `queue-canon.test.ts` and `command-palette.test.ts` pass with no edit other than the fixture (row 3). | Local Canon (§Test pins; D-1095) | Any other edited expectation is S5 |
| AC-155.10 | E2E | Real backend, scratch `AVKIT_APP_DATA`. Job 1 is a Cut with re-encode of a 90 s 1280x720@30 `testsrc2` clip (libx265, about 28 s on this PC); job 2 a short copy Cut. After Start, once job 1 is running and the backend reports `Processing` with `current_job_id` = job 1, a click on Pause: within 2 s the button reads `Pausing…` and is disabled and `convert-processor` reads the status, while `GET /conversions` still reports `Processing` with job 1. Within 180 s job 1 is Done, the processor `Paused`, job 2 `Pending`, and the toolbar shows "Resume" and the chip "Queue Paused". Resume then runs job 2 to Done. | Human-approved (Mat's ruling; "proved with Electron E2E tests"); Local Canon (`conversion.py:496`) | A pause that cancels job 1, or a toolbar still reading "Pause after this job" after the click, fails |
| AC-155.11 | E2E | The same two jobs; Pause, then `Pausing…`, then Cancel on job 1's card (`queue-card-primary-action`, with the confirm when one opens): within 30 s the backend is `Idle`, job 1 `Cancelled`, job 2 `Pending`; the toolbar reads "Pause after this job" (disabled at Idle) and the chip is hidden. | Human-approved ("Cancel stays the way to stop at once") | A Cancel that waits for the job, or a Pausing… that stays, fails |
| AC-155.12 | E2E | Downloader. The app starts through the Session 81 `launch` (`convert-queue-labels.test.ts:237`), which records the backend pid and stops only that pid after its start-time check; then an in-page fetch seam modelled on `download-queue.test.ts:171-410` is installed with `addInitScript` and the window reloads (`page.reload()`), so the seam is in place before the page's first list read. The seam's pause handler counts the POST and keeps `Processing`: a click on Pause gives `Pausing…`, disabled, and `processor-indicator` the status; the running card's Cancel is enabled. The test then sets the seam to `Paused` (`page.evaluate`) and the toolbar shows "Resume". At a 700 × 650 viewport (`setViewportSize`, the narrow-width header precedent `convert-queue.test.ts:1409-1426`), in each of the three states (Pause after this job, `Pausing…`, Resume), the toolbar group's right edge is within the header's, the toggle is in the viewport, and the page has no horizontal scroll. | Human-approved (Mat's ruling); Local Canon (10 §Toolbar reduction: icon plus label, never hover-only) | A toolbar that overflows at 700 fails (S8) |
| AC-155.13 | unit | Transcript keeps "Pause": `TranscriptToolbar` in `Processing` renders `pause-btn` with the text "Pause", and in `Paused` `resume-btn` with "Resume". `DOWNLOADER_HELP_SECTIONS`'s `pause` topic keeps the title "Pause vs cancel" and its body equals the `HELP_PAUSE` text. | Local Canon (11 TR1, TR2; D-1090); D-1093 | In Red the help body is the old text |
| AC-155.14 | unit | What the read after the pause POST shows decides the mark. Convert, cached envelope `Processing` with `c1`: the `GET /conversions` answering `Processing` with `c2` → `{ jobId: 'c2' }`, the cache holds the `c2` envelope, and `isPausePending(readPauseRequest('convert'), { state: 'Processing', current_job_id: 'c2' })` is true; answering `Processing` with no job id → `{ jobId: null, markedAt: Date.now() }` (fake time); answering `Paused` → no mark and the cache `Paused`; answering 500 → no mark, the call resolves, the list is invalidated, and a second `pauseConversion()` POSTs `/conversions/pause` again (Pause stays usable; the backend's pause only sets a flag). The same four cases for `pauseDownload()` with `d1` and `d2`. | Local Canon (D-1091 `PAUSE_MARK_SET`; expert pass item b; plan review R1-F2) | A mark naming `c1`, a mark after a failed or `Paused` read, or a rejected call after a failed read, fails |
| AC-155.15 | E2E | Clear finished does not move. On Convert (the real-backend jobs of AC-155.10) and on Downloader (the seam of AC-155.12), the x of `queue-toolbar-clear-finished`'s bounding box is read in the "Pause after this job" state, in `Pausing…` and in Resume, and the three values are equal within 0.5 px (under amendment A1 the toolbar may drop to the next line at the right edge in one state, so its y may change, but x must still be equal); in each state the toggle's `scrollWidth` is at most its `clientWidth` (the label fits). | Local Canon (D-1091 `TOGGLE_WIDTH`; expert pass item c) | A toggle that shrinks to Pausing… and slides Clear finished left fails |
| AC-155.16 | py | With no injected `sleep` (the service's own wait), a pause during each of the three waits lands within 2 s. **Sync point:** after the service is built and before `start_processing()`, the test replaces the instance attribute `service._sleep` with a wrapper that sets a `threading.Event` when it is called with the target duration and then calls the original (a test-side wrap of an attribute that exists today, `transcript.py:107`; no product hook); the test waits up to 10 s for that event and then calls `pause_processing()` at once, so the worker is entering the target wait and the pause check at `:491` ran before it. (a) `delay_between_requests` 30, two videos, target 30; (b) `delay_between_requests` 0, `batch_size` 1, `pause_between_batches` 300, two videos, target 300; (c) `delay_between_requests` 0, `retry_delay` 30, `max_retries` 3, the first call raising `TranscriptRetryableError` (`FakeCaptions.retryable_left = 1`), target 30. In each case, within 2 s of `pause_processing()` the processor state is `Paused` and the job `Paused`, and `get_transcript` was called once. | Human (Mat 2026-11-16: "If it is not possible to pause it should not be called pause"); Local Canon (03 `:193` "After current video"; 03 §Rate cap `:256`); D-1090 | In Red the processor is still `Processing` after 2 s |
| AC-155.17 | py | With no injected `sleep`, `stop_processing()` during the 30 s delay wait (at the sync point of AC-155.16 (a)): within 2 s the processor state is `Idle`, the job `Cancelled`, and `get_transcript` was called once. | Local Canon (D-1090: C also ends Stop's wait) | In Red the processor is still `Processing` after 2 s |
| AC-155.18 | py | The wait itself, on a service with no injected `sleep` and an empty queue, through `wait = getattr(service, '_sleep')`: `wait(0.3)` takes at least 0.29 s; after `pause_processing()`, `wait(2)` takes under 0.5 s; after `start_processing()` (which clears the flags; the worker finds no job and goes Idle), `wait(0.3)` takes at least 0.29 s again. `tests/unit/test_services.py` passes unchanged (row 3b). | Local Canon (D-1090 `TRANSCRIPT_WAKE`) | In Red `wait(2)` after a pause takes 2 s |
| AC-155.19 | unit | A remount after the list was collected keeps the mark (fake time; both kinds). A probe component calls the real `useConversionQueue()` and `usePausePending('convert', queue.data?.processor)` inside a `QueryClientProvider` on the shared client, with `fetch` stubbed to answer `GET /conversions` with `Processing`/`c1`; after `markPauseRequested('convert', 'c1')` the probe shows pending. Unmount, then `vi.advanceTimersByTime(6 * 60 * 1000)`: `queryClient.getQueryData(QUERY_KEY)` is `undefined` (collected) and the mark is still `{ jobId: 'c1' }`. Remount with the first GET held: pending is false and the mark is still `{ jobId: 'c1' }`. Release it with `Processing`/`c1`: pending is true. The same with `useDownloadQueue()` and `d1`. | Local Canon (D-1091 `PAUSE_PENDING_HOOK`; plan review R1-F1) | A hook that clears the mark before the first list read, so pending never comes back, fails |
| AC-155.20 | unit | Appended to `convert-page.behavior.test.ts` after AC-155.7, in its describe (envelope `Processing`, `current_job_id: 'job-2'`): a click on `queue-toolbar-pause` gives `Pausing…`; unmount the page; `queryClient.removeQueries({ queryKey: QUERY_KEY })` (what collection does; AC-155.19 proves it under fake time); remount with the first `GET /conversions` held: the toggle does not read `Pausing…`, `convert-processor` does not show the status, and the mark is still `{ jobId: 'job-2' }`; release it with `Processing`/`job-2`: the toggle reads `Pausing…`, disabled, and `convert-processor` reads "Queue stops when the current job ends". | Local Canon (D-1091 `PAUSE_STATUS`; plan review R1-F1) | A page that clears the mark on its first render, so Pausing… does not come back, fails |
| AC-155.21 | unit | Appended to `downloader-page.behavior.test.ts` after AC-155.8, in its describe: the same sequence on `processor-indicator`, `QUERY_KEY` of `useDownloadQueue.ts` and `GET /downloads`, with that describe's running job. | As AC-155.20 | As AC-155.20 |
| AC-155.22 | unit | A spent pause does not block the next one (both kinds). Convert, cached `Processing`/`c1`, a probe as in AC-155.19: (a) `POST /conversions/pause` answers 202 and the `GET /conversions` after it 500; the call resolves with no mark; unmount; the stub's list moves to `Paused` and back to `Processing` with `c2` while no probe is mounted (another client paused and resumed); remount: once the list reads `Processing`/`c2`, pending is false, `controlEnabled('pause', …)` is true for that context, and `pauseConversion()` POSTs again. (b) The same, but the GET answers `Processing` with no job id (an unbound mark); unmount, `vi.advanceTimersByTime(20_000)`, the unseen `Paused` and resume, and a remount reading `Processing`/`c2`: pending is false, the mark is `null`, and `pauseConversion()` POSTs again. The same for `pauseDownload()` with `d1` and `d2`. | Local Canon (D-1091 `PAUSE_MARK_SET`, `PAUSE_PENDING_RULE`; plan review R1-F2) | A mark that stays pending for `c2`, or a Pause that sends nothing, fails |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| The button's label | Human-approved | "Pause after this job" (Mat 2026-11-16) |
| What shows after a click | Human-approved | "Pausing…" and a status that the queue stops when the current job ends (Mat 2026-11-16); the status wording is D-1093 |
| Whether Pausing… can be undone | Local Canon | No: disabled; Cancel still works (D-1091) |
| When Pausing… ends | Local Canon | On Paused, Idle or another job in a list the page has read (a list not yet read ends nothing); a failed job ends Paused (D-1091) |
| Which job the mark names | Local Canon | The job in the list read after the pause POST; between jobs, the next job seen within 15 s; none when that read fails or shows Paused or Idle (D-1091) |
| Whether the toggle changes width | Local Canon | No: one minimum width in every state (D-1091) |
| A pause from MCP, another window or before a reload | Local Canon | Shows no Pausing…; named in the D-1091 brief; a backend field is the M-4 alternative (D-1097) |
| The palette | Local Canon | Shares the mark; labels kept; there is no pause shortcut (D-1092) |
| Transcript | Human-approved and Local Canon | Keeps "Pause"; its waits end on pause or stop (Mat 2026-11-16; D-1090) |
| Where the pending state lives | Local Canon | The renderer's query cache; no API change (D-1097) |
| How the behaviour is proved | Human-approved | Electron E2E in the gate (Mat 2026-11-16); design D-1094 |
| MEU id and home | Local Canon | MEU-155 in 10 §Queue pause feedback, matrix 10.10 (D-1096) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `ui/src/renderer/src/lib/queue/pause-request.ts` | new | LF | `PAUSE_MARK`, `PAUSE_UNBOUND_MS`, `PAUSE_PENDING_RULE`, `PAUSE_PENDING_HOOK`, `PAUSE_PENDING_STATUS` |
| `ui/src/renderer/src/components/queue/QueueToolbar.tsx` | modify | CRLF, kept | `PAUSE_LABEL`, `PAUSE_PENDING_LABEL`, `PAUSE_TOGGLE_WIDTH_CLASSES`, `pausePending`, `TOOLBAR_END` (A1) |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | modify | CRLF, kept | `currentJobId`; mark set and clear |
| `ui/src/renderer/src/features/downloader/download-commands.ts` | modify | CRLF, kept | The same |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | CRLF, kept | `usePausePending`, the chip text, the toolbar prop, `PAGE_STATE` |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | MIXED (750 CRLF, 221 bare LF), kept per line | The same |
| `ui/src/renderer/src/features/downloader/downloader-help-content.ts` | modify | CRLF, kept | `HELP_PAUSE` |
| `ui/tests/unit/fixtures/queue-slot-baseline.json` | modify | CRLF, kept | The toggle's label and width classes, and the toolbar root's ` ml-auto` (A1) (`PINS_NAMED`) |
| `ui/tests/unit/queue-pause-feedback.test.tsx` | new | LF | AC-155.1 to AC-155.6, AC-155.9, AC-155.13, AC-155.14, AC-155.19, AC-155.22 |
| `ui/tests/unit/convert-page.behavior.test.ts` | modify | CRLF, kept | AC-155.7 and AC-155.20 appended |
| `ui/tests/unit/downloader-page.behavior.test.ts` | modify | MIXED (2096 CRLF, 399 bare LF), kept per line | AC-155.8 and AC-155.21 appended after `:1023`, inside a bare-LF range, so their lines are bare LF |
| `ui/tests/e2e/queue-pause-feedback.test.ts` | new | LF | AC-155.10 to AC-155.12, AC-155.15 |
| `packages/core/src/avkit_core/services/transcript.py` | modify | LF, kept | `TRANSCRIPT_WAKE` (row 3b) |
| `tests/unit/test_transcript_pause_wake.py` | new | LF | AC-155.16 to AC-155.18 (row 2b) |
| `docs/build-plan/03-service-layer.md` | modify | CRLF, kept | One paragraph after §Rate cap (row 3b) |
| `docs/build-plan/10-queue-card-ui.md` | modify | CRLF, kept | Row 1: §Queue pause feedback (residual); row 5: its Delivered note |
| `docs/build-plan/build-priority-matrix.md` | modify | CRLF, kept | Row 1: row 10.10 |
| `.agent/context/meu-status.yaml` | modify (script, tool) | LF, kept | Row 1: MEU-155 `pending`, phase 10 note, P2 range; row 5: `ready_for_review`; H2-2: `approved` |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/known-issues.yaml` | modify (script, tool) | LF, kept | Row 5: `QUEUE-PAUSE-NO-FEEDBACK` resolved, with `meu_links: [MEU-155]`; row 6: `QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT` added, `open` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modify | LF, kept | §6 row 88 only: MEU-155, `executed (Session 88)`, this plan folder |

**Line endings** were measured with Python bytes (`qp88-probe.txt`, `qp88-eol-extra.txt`, `qp88-mixed-ranges.txt`, `qp88-eol-py.txt`, at `HEAD` `ba6d8ef`). CRLF: `QueueToolbar.tsx`, `convert-commands.ts`, `download-commands.ts`, `ConvertPage.tsx`, `downloader-help-content.ts`, `queue-slot-baseline.json`, `convert-page.behavior.test.ts`, `03-service-layer.md` (872 CRLF, 0 bare LF), `10-queue-card-ui.md`, `build-priority-matrix.md`, and the state files `current-focus.md` and `metrics.md`; `test_services.py` and `settings.py`, read only, are CRLF too. MIXED: `DownloaderPage.tsx` and `downloader-page.behavior.test.ts`. LF: `transcript.py` (820 LF, 0 CR), the registers, the generated files, the grouping and the four new files. A CRLF file is read and written with `newline=""` from CRLF text; in a MIXED file each new line takes the ending of the line before it. `eol-check.py` checks all of them in rows 3 and 4 and in the gate. Files read but not changed, among them `convert-controls.ts` (MIXED), `download-controls.ts`, `QueueHeaderRow.tsx` and `TranscriptToolbar.tsx` (CRLF), are bound by hash in `baseline-scope.json`.

### Project files

- **Plan-local scripts**, all in this plan folder:
  - written at plan time: `register-meu-155.py` (row 1; `--expect-sha256`, `--dry-run`, `--selftest`; ruff-clean, `qp88-ruff-*.txt`);
  - written in row 0: `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py`;
  - written in H1-2: `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`.
- **Read, never changed (bound in `baseline-scope.json`):** `QueueHeaderRow.tsx`, `convert-controls.ts`, `download-controls.ts`, `TranscriptToolbar.tsx`, `commandRegistry.ts`, `queue-card-slots.test.tsx`, `queue-toolbar.test.ts`, `queue-header-row.test.tsx`, `convert-page.test.ts`, `downloader-page.test.ts`, `help-card.test.ts`, `layout-canon.test.ts`, `queue-canon.test.ts`, `convert-queue.test.ts`, `download-queue.test.ts`, `convert-queue-labels.test.ts`, `electron-app.ts`, `conversion.py`, `download.py`, `settings.py`, `tests/unit/test_services.py`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md` | Any session that registers or moves a MEU | `register-meu-155.py` refuses unless the file has its row-0 hash and MEU-155 is absent; later writes go through `meu_status.py` for MEU-155 only |
| `known-issues.yaml`, `known-issues.md` | Any triage session | `issue-resolve.py` changes only `QUEUE-PAUSE-NO-FEEDBACK` and binds to the row-0 hash (S4) |
| Grouping §6 table | Every session of the grouping | Only row 88 changes. Rows 76 and 83 read `proposed` although their plan folders exist; that is not this session's to fix |
| `10-queue-card-ui.md`, `build-priority-matrix.md` | None in this grouping | Only the new section, its note and row 10.10 |
| `ui/tests/e2e/` | None open | One new file; no existing E2E file changes |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A backend "pause requested" field, so a pause from MCP, another window or before a reload also shows Pausing… | out-of-scope | — | M-4: it changes the list envelope, OpenAPI and MCP shapes; the D-1091 brief presents it as option B; D-1097 |
| Pausing inside a running job (stopping an FFmpeg or yt-dlp process part-way) | out-of-scope | — | Mat: "The services keep pausing between jobs"; 10 §Pause scope (`10-queue-card-ui.md:308`) |
| Undoing a pause request before the job ends | out-of-scope | — | It needs a new backend call (M-4); D-1091 |
| Transcript's Pause wording | out-of-scope | — | D-1090 C keeps "Pause" and makes the pause prompt instead |
| Cancel stays enabled while a queue is Paused, but nothing acts on it: `cancel_processing` only sets `_cancel` (`conversion.py:277-278`, `download.py:456-460`) and no worker runs while Paused, so the state stays Paused until the next start clears the flags (`conversion.py:254-264`); the toolbar enables Cancel then (`convert-controls.ts:69-109`, `download-controls.ts:77-78`) | out-of-scope (found in the expert pass; existed before this session) | — | A fix chooses what Cancel means while Paused (go Idle, or disable the control): a product fork (M-5) and scope beyond the grouping's list (M-8), so the HDP keeps it out. Row 6 registers it as `QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT` (`open`, low, ui) through `tools/issue_triage.py add` |
| The grouping's §3 Session 88 text and the issue's root cause still cite `transcript.py:407` and say Transcript "shares the toolbar" | out-of-scope | — | Both are stale (§What the code shows). The grouping's §3 is another planning record; row 5's resolution text for `QUEUE-PAUSE-NO-FEEDBACK` states the corrected facts (`:491`, a separate `TranscriptToolbar`) |
| The MCP tools' pause description | out-of-scope | — | It already says "Pause is queue-level"; no MCP change |
| Grouping rows 76 and 83 reading `proposed` | out-of-scope | — | Another session's row; this session changes row 88 only |

## BUILD_PLAN.md Audit

MEU-155 is not registered at plan time (`qp88-probe.txt`: `row_key: MEU-154` once, no MEU-155). Row 1 registers it with `register-meu-155.py` (D-1096): MEU-155, slug `gui-queue-pause-feedback`, phase 10, band P2, matrix 10.10, build ref 10 §Queue pause feedback (residual), dependencies MEU-45 and MEU-46 (both `approved`), status `pending`. The dry run (`qp88-register-dryrun.txt`, `qp88-register-dryrun-diff.txt`) adds 27 LF lines to `meu-status.yaml`, one anchor and section to 10 and one matrix row, all CRLF where the file is. Row 5 sets `ready_for_review` with this plan's `execution_plan`, and H2-2 sets `approved`, both through `tools/meu_status.py update`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/queue-pause-feedback/qp-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/queue-pause-feedback/qp-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` follows `2026-11-15-convert-settings-drafts/baseline.ps1`:

1. **Tree state.** `baseline.sha` (`HEAD`) and `baseline-dirty.txt` (`git status --porcelain --untracked-files=all`).
2. **Path-scoped baseline, bound to content.**
   - `baseline-scope.json`: the SHA-256 of each §Files Modified path and each §Project files "Read, never changed" path, or `absent`; the four new files must be `absent`.
   - `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`.
   - `baseline-eol.json`: for each scope path, its kind (`CRLF`, `LF`, `MIXED`), its CRLF and bare-LF counts.
   - `baseline-skip-hashes.json`: the SHA-256 of every tracked or untracked, not-ignored file under `packages/`, `mcp-server/`, `tests/` and `tools/`, the basis for skipping the OpenAPI and MCP checks (H1-4): at the gate only `packages/core/src/avkit_core/services/transcript.py` and the new `tests/unit/test_transcript_pause_wake.py` may differ.
   - The S2 binding: the row-0 anchors of `qp88-probe.txt` still hold (each counted once), MEU-155 is absent, `QUEUE-PAUSE-NO-FEEDBACK` is `open`, grouping row 88 reads `proposed`, and 10 has no `queue-pause-feedback-residual` anchor.
3. **Base receipts.** The full Vitest run (`qp-base-ui.txt`, pwsh in `ui/`) and the full pytest run (`qp-base-py.txt`: `rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE`); their failures are recorded, not fatal, and the gate's `ui-tests` and `py-tests` excuse only those ids (the Session 49b baseline rule).
4. **Plan-local scripts.**
   - `red-check.py` and `identity.py` are copied from `2026-11-15-ready-handshake/` with this plan's `PLAN`, `PROJECT_ARTIFACTS` (the handoff, the reviews, the reflection, `metrics.md`, `current-focus.md`) and `DECLARED_NEW` (`isPausePending`, `markPauseRequested`, `clearPauseRequest`, `readPauseRequest`, `usePausePending`, `PAUSE_PENDING_LABEL`, `PAUSE_PENDING_STATUS`, `PAUSE_UNBOUND_MS`, `pause-request`). `identity.py`'s other-plan skip covers untracked `docs/execution/plans/2026-11-1[5-7]-<slug>/` folders other than this one.
   - `issue-resolve.py` is copied from `2026-11-15-ready-handshake/` with `SCRATCH` at `C:/Temp/av-kit/queue-pause-feedback/issue-resolve` and `RESOLVE_KEYS` extended with `meu_links`, which must be a list of MEU ids (`tools/issue_triage` model, `meu_links`); a key the issue lacks is added before `category`, or last.
   - `eol-check.py` (new, LF): for each scope path it compares the file now with its row-0 bytes (from `C:/Temp/av-kit/queue-pause-feedback/baseline-copies/`). A CRLF file must have no bare LF, an LF file no CR, a new file no CR; in a MIXED file every line inserted or changed since row 0 (difflib opcodes) must end like the line before it, or like the line after it at the top. `--selftest` covers each rule.
   - The `red-check.py`, `identity.py`, `eol-check.py` and `register-meu-155.py` selftests run, and `ruff format --check` and `ruff check` run on the plan folder's Python (Session 82 RULE-1).

If any step except the base receipt fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names AC-155.1 to AC-155.8, AC-155.13, AC-155.14 and AC-155.19 to AC-155.22 (row 2), and AC-155.16 to AC-155.18 in the pytest receipt (row 2b). The fixture-backed test in `queue-card-slots.test.tsx` also fails at Red, by assertion, and is not required.
- **Expectations stay immutable in Green** (S3). The fixture edit is made at Red, so Green changes no expectation. Row 3b checks `test_transcript_pause_wake.py` against its row-2b hash and runs `test_services.py` unchanged.
- **Line endings** are checked by `eol-check.py` after Green.

### 3. Electron proof (row 4)

`queue-pause-feedback.test.ts` copies the Session 81 helpers from `convert-queue-labels.test.ts` (`makeClip` `:85`, `longClip` `:108`, `probeSeconds` `:117`, `api` `:134`, `queue` `:158`, `readBackendPid` `:162`, `running` `:173`, `startTime` `:183`, `stopRecordedBackend` `:198`, `closeBounded` `:222`, `launch` `:237`, `useOutDir` `:297`, `openConvert` `:304`, `addCut` `:312-341` with `__S81_PICKED__` renamed `__S88_PICKED__`, `row` `:343`, `start` `:360`, `waitAllDone` `:366`). Clips are made with FFmpeg in the test's temp folder; nothing reaches the network. The 90 s clip's libx265 re-encode takes about 28 s on this PC (`qp88-calib.txt`: 10 s took 3 074 ms on 24 logical CPUs), which leaves room to click and read the pending state; the waits allow 180 s for a loaded host. The Downloader tests (AC-155.12 and its half of AC-155.15) also start through `launch`, so each records and stops only its own backend pid; the fetch seam from `download-queue.test.ts:171-410` goes in with `addInitScript` and a `page.reload()`, because an init script added after launch reaches only later loads (the seam test there ends with a plain `app.close()` and records no pid, so its launch is not copied). The build runs first, then the new file three times; `convert-queue.test.ts` and `download-queue.test.ts` run once each.

### Session gate (H1-2)

`session-gate.ps1` follows `2026-11-15-convert-settings-drafts/session-gate.ps1`: one receipt per step in `C:/Temp/av-kit/queue-pause-feedback/`, named `qp-D6-<step>`; fail-fast, with later steps printed as `not_run`; the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content); `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `red-check-selftest`; `eol-check-selftest`; `register-selftest`; `py-format` and `py-lint` (`ruff format --check` and `ruff check` on this plan folder's Python, `transcript.py` and `test_transcript_pause_wake.py`); `py-types` (`pyright packages/`) |
| Targeted | `meu-155-unit` (`queue-pause-feedback.test.tsx`, `convert-page.behavior.test.ts`, `downloader-page.behavior.test.ts`, and the AC-155.9 pin files); `meu-155-py` (`test_transcript_pause_wake.py` and `test_services.py`) |
| Host load | `host-load`: samples `Win32_Processor.LoadPercentage` five times; above 60 % it waits, re-sampling every 30 s for up to 10 minutes, and records the value it ran at (Session 81 RULE-2). It never fails the gate |
| Fresh full | `ui-tests` (full Vitest); `py-tests` (full pytest, `qp-base-py.txt` excusals only); `ui-build`; `e2e-pause` (`queue-pause-feedback.test.ts`); `e2e-convert-queue`; `e2e-download-queue`; `state-render` (`meu_status.py render --check`); `issues-render-check` (`issue_triage.py render --check`) |
| Skipped, with reason | `openapi`, `mcp-*`: every file under `packages/api/`, `mcp-server/` and `tools/` keeps its `baseline-skip-hashes.json` hash, and under `packages/` and `tests/` only `transcript.py` changed and only `test_transcript_pause_wake.py` was added (H1-4); `TRANSCRIPT_WAKE` changes no route, schema or tool. The rest of `test:e2e`: only the Convert and Downloader toolbars changed, and their two suites run; the Transcript page's markup is unchanged |

`ui-tests` excuses only ids that `qp-base-ui.txt` shows failing, and `py-tests` only ids that `qp-base-py.txt` shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a row-0 anchor missing or counted twice, MEU-155 present, the issue not `open`, row 88 not `proposed`, or 10's anchor present | Stop; another session moved this ground. Bring the probe to Mat |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, a `baseline-dirty.txt` path changes content, or `meu-status.yaml` or `known-issues.yaml` lacks its row-0 hash when its script runs | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test other than the fixture-backed one fails after Green | Stop: that is an M-7 question (§4a), not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | An Electron test fails in any of row 4's three runs | Stop and bring the receipts to Mat; never raise a timeout to pass |
| S8 | AC-155.12's 700-pixel check fails (the wider toggle overflows the toolbar), AC-155.15 finds Clear finished moving or the label clipped, or the 700-pixel header test at `convert-queue.test.ts:1409-1426` fails | Stop: how the toolbar wraps or sizes is a layout choice (M-5) for a brief; never shrink the width class to pass |
| S9 | A Python test other than the new file fails after row 3b, or a `test_services.py` sleep assertion needs a change | Stop: an M-7 question; `TRANSCRIPT_WAKE` must keep injected sleeps whole |

## Decision Log

> [!NOTE]
> D-1092 to D-1097 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-1090 hit M-5, M-6 and M-8, and D-1091 hit M-5, so they are briefs (below). No other M item is hit: no API, OpenAPI or MCP change (M-4 clear), no user data written (M-2 clear), and the one changed test expectation is named in §Test pins while the Python sleep pins pass unchanged (M-7 clear). Mat's hand-over covers M-3, M-5, M-6 and M-8 briefs (HDP §6), so the two are recorded `autonomous` with their `mandatory:` lists kept; `open_decisions` is empty and there is no STOP item.
>
> **Why Session 88 is inside the hand-over.** HDP §6 lets a hand-over cover one set. The 2026-11-15 hand-over ('like we did here. But use the new HDP process.') covers the post-rc.3 triage-residuals grouping, and Session 88 sits in §3 of that same grouping file (this plan's `grouping_source`). It was added there under Mat's own 2026-11-16 AskUserQuestion answers on `QUEUE-PAUSE-NO-FEEDBACK`, "Say what it does (Recommended)" and "Small session after 83 (Recommended)", so it joined the set by his choice and the set is still the one the hand-over names. The handed reasoning prefix is therefore kept word for word.
>
> **The Cancel-while-Paused defect** that the expert pass found (§Out of Scope) is not fixed here: choosing what Cancel means while Paused is a product fork (M-5) and adds scope beyond the grouping (M-8), so it is registered as a known issue in row 6 and nothing more. The grouping rows (D-813 to D-817) stay in the grouping file's §8 and are not copied here; H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`). The issue carries no decision row of its own (`qp88-probe.txt`: `decision_sources` with the issue adds nothing). Under the new HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices and does not restate grouping rows. D-1098 and D-1099 are left free for execution.

```yaml
decision_log:
  - id: D-1090
    stage: planning
    question: "What does the Transcript page's Pause do and say, given that it can wait minutes?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5, M-6, M-8]
    chosen: "C: Transcript keeps its Pause button and label, and its delay, batch-rest and retry waits end within a second of a pause or stop (TRANSCRIPT_WAKE), with no API, OpenAPI, MCP or setting change. Only the Convert and Downloader toolbars read Pause after this job and show Pausing…."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/transcript.py:491 — the between-videos pause check runs before the waits (:407 is the between-channels check)"
      - "packages/core/src/avkit_core/services/transcript.py:495, :497, :581 — the delay, batch-rest and retry waits: 6 s, 300 s and 30 s at the defaults in settings.py:70-74"
      - "packages/core/src/avkit_core/services/transcript.py:655-671 — _await_request_slot already sleeps in slices and returns on stop or pause"
      - "docs/build-plan/03-service-layer.md:256 — canon: a stop or pause ends the rate-cap wait within a second"
      - "docs/build-plan/03-service-layer.md:193 — canon: pause_processing lands after the current video"
      - "ui/src/renderer/src/features/transcript/TranscriptToolbar.tsx:4-8 — Transcript has its own three-action toolbar; it does not mount QueueToolbar"
      - "docs/build-plan/11-page-layout.md:28-29 — TR1 and TR2: Start, one Pause/Resume node, Stop"
      - ".agent/context/known-issues.yaml:5382 — the issue title names Convert and Downloader only"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling of the same day ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set, and Session 88 is in that set (§Decision Log note). Mat's words of 2026-11-16 weigh most here: 'Also not sure if other pages have this issue with queue pause or stop fuction. If it is not possible to pause it should not be called pause but something else.' M-5 because four product options remain. M-6 because the grouping and the issue cite :407 and say Transcript shares the toolbar, while the code shows its own toolbar and the between-videos check at :491, and because keeping the label with a 5-minute wait would sit against Mat's words. M-8 because C adds a backend file to a session the grouping scoped to the renderer, adopted from the expert pass. M-4 is clear (no route, schema or tool change), M-7 is clear (injected sleeps stay whole, so test_services.py:1363, :1379-1380 and :3088 pass unchanged), and M-2 and M-3 are clear. C makes the word true: a pause or stop lands within a second plus the video already being fetched, which answers both halves of his words, and it extends the rate-cap canon to the other waits. Risk: a pause and resume during the 300 s batch rest cuts the rest short; the hourly cap (requests_per_hour, default 300) still holds, and today's pause and resume already restart the batch count. B, Pause after this video with a pending state, keeps the wait and reads wrong during the batch rest, when no video is running. A, keeping Pause as it is, and doing nothing both leave a Pause that can do nothing for 5 minutes. Two-way: one method and two event calls in one file."
  - id: D-1091
    stage: planning
    question: "What does the button do between the click and the moment the queue pauses?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: Pausing… is disabled and cannot be undone; Cancel stays enabled and ends it; it ends when a list the page has read reports Paused or Idle or another job (a list not yet read ends nothing); the mark names the job in the list read after the pause POST, read after older polls are cancelled; a read between jobs gives an unbound mark that binds to the next job seen within 15 s and is spent after that; a failed read after a successful POST sets no mark, and a second click is harmless; the mark lives in the renderer and survives a page change but not a reload; the toggle keeps one minimum width in every state."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/10-queue-card-ui.md:243 — Pause and Resume collapse into one toggle reflecting processor.state"
      - "packages/core/src/avkit_core/services/conversion.py:269-272 — pause sets a flag; resume needs the Paused state, so there is no undo while a job runs"
      - "packages/core/src/avkit_core/services/conversion.py:553-558 and :496 — a failed job returns to the loop, which reads the pause flag first, so the queue ends Paused"
      - "packages/core/src/avkit_core/services/conversion.py:672-676 — _finish clears current_job_id, so between jobs the id is null"
      - "packages/core/src/avkit_core/services/conversion.py:269-270, download.py:448-449 — pause only sets a flag, so a repeated pause POST is harmless (routes conversions.py:215-223 and downloads.py:157-165 answer 202)"
      - "ui/src/renderer/src/features/converter/ConvertPage.tsx:109-113, ui/src/renderer/src/features/downloader/DownloaderPage.tsx:180-184 — missing list data maps to Idle, so the hook reads the observed processor instead"
      - "C:/Temp/av-kit/qpf-plan-review-round-1.md — plan review round 1, R1-F1 and R1-F2"
      - "ui/src/renderer/src/features/downloader/download-commands.ts:127-130 — replaceQueueFromList reads the list and writes the cache"
      - "ui/src/renderer/src/features/converter/ConvertPage.tsx:876, :880 — Clear finished runs at once with no confirm, beside the toggle"
      - ".agent/context/known-issues.yaml:5381 — Mat's ruling: after a click show Pausing…, and Cancel stays the way to stop at once"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set, and Session 88 is in that set (§Decision Log note). M-5 because the spec says nothing about a state between the click and Paused. The backend cannot take a pause back while a job runs (resume needs Paused), so a clickable Pausing… would promise what the services cannot do; disabled is honest. It ends on Paused, Idle or another job, so the label cannot stick: Cancel ends at Idle, and a job that fails ends Paused, because the loop reads the pause flag before it picks the next job. The mark takes its job id from the list read after the POST, not from a cache up to a second old, so a job that changed inside the poll window is named rightly; between jobs the list shows no job id for a moment, so the mark is then unbound and binds to the next job id the page sees within 15 s, never a wildcard across runs, and the id check stays to clear a mark that another client's resume left. The toggle keeps one minimum width, so Clear finished does not slide under the cursor when the label shortens. Edges, named in the brief: a pause from MCP or another window shows no Pausing…; a reload loses the mark while the backend still pauses (a second click is harmless); a pause during the last job ends Paused with nothing pending, and Resume then goes Idle. B, a backend pause_requested field in the list envelope, covers all three edges but changes the API, OpenAPI and MCP shapes (M-4), so it is presented and not chosen. C, a clickable Pausing… that takes the pause back, also needs a new backend call (M-4). D, no pending state, is what Mat's words rule out. Keeping things as they are leaves the defect. Round 1 correction (plan review R1-F1 and R1-F2, 2026-11-17), executing this choice: the hook acts only on a list it has read, because the pages map missing data to Idle and a remount after the 5-minute list collection erased a valid mark; a failed read after the POST sets no mark, and an unbound mark binds or ends within 15 s, because a null mark that matched any job outlived an unseen pause and resume and blocked the next Pause. Residual limits, named in the brief: a failed read after the POST shows no Pausing…, the cost of never guessing; and a pause sent in the instant between two jobs, then a page change and a resume from another client within 15 s, can show Pausing… for the job that resume started, until it ends. Two-way: one prop, one class constant and one module."
  - id: D-1092
    stage: planning
    question: "Do the palette pause commands share the button's Pausing… state?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes: the palette's Pause conversions and Pause downloads call the same pause functions and set the same mark; while it is set, PAGE_STATE hides convert:pause and download:pause, and a repeat sends no request. Their labels are kept. There is no pause keyboard shortcut to change."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/registry/shortcuts.ts:256-282 — PALETTE_LIST (D-137): a stateful command is listed only on its own page while that page publishes it enabled"
      - "ui/src/renderer/src/features/converter/ConvertPage.tsx:557-564 — PAGE_STATE uses the same expressions the toolbar uses"
      - "ui/src/renderer/src/features/converter/convert-commands.ts:283 — deliverPalettePause calls pauseConversion"
      - "ui/src/renderer/src/registry/commandRegistry.ts:233-242 and :396-405 — the pause entries: labels kept, no shortcut field"
    research: { engine: none, sources: [] }
    reasoning: "Passes the §4 test. Convergence: canon fixes the answer, because PALETTE_LIST lists a stateful command only while its page publishes it enabled and PAGE_STATE mirrors the toolbar, so a disabled Pausing… toggle means a hidden palette pause, and the shared mark stops a repeat request. Two-way: one boolean per page. No product fork: the labels stay and nothing new is shown; a pause from the palette is only listed on its own page, so it shows Pausing… there. No governance number. The expert pass found that no pause command has a keyboard shortcut, so the earlier keyboard half of the question was moot, the M-5 hit it rested on falls away, and the brief is dropped."
  - id: D-1093
    stage: planning
    question: "What exact strings does the change show?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The button Pause after this job; the pending button Pausing… with U+2026; the status Queue stops when the current job ends; the Downloader help body Pause after this job lets the current download finish, then stops the queue with its order intact; Resume continues later. Cancel stops the current download at once and does not delete finished files."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:231 — Mat's ruling: Pause after this job, Pausing…, the status says the queue stops when the current job ends"
      - "ui/src/renderer/src/features/converter/convert-controls.ts:139 — processorLabel already uses the U+2026 ellipsis in Processing…"
      - "ui/src/renderer/src/features/downloader/downloader-help-content.ts:27 — the old help body"
    research: { engine: none, sources: [] }
    reasoning: "The two button strings are Mat's own words. The status repeats his sentence as a short chip text without a verb in the past. The help body was 'Pause keeps queue order intact and lets you resume later', which is still true but hides the wait; the new body names the button and the wait, and keeps the Cancel half. The ellipsis matches the Processing… chip. Two-way: string constants."
  - id: D-1094
    stage: planning
    question: "How do the Electron tests prove the behaviour without the network or a manual check?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Convert runs the real backend on two local FFmpeg-made clips, a 90 s libx265 re-encode Cut as job 1 and a short copy Cut as job 2, with a scratch app-data folder; Downloader starts through the same Session 81 launch, which records the backend pid, then installs an in-page fetch seam with addInitScript and reloads, and the seam's pause keeps Processing until the test flips it; each test stops only the backend pid it recorded; the toolbar fit and the Clear finished position are checked at a 700-pixel viewport."
    source_tag: Research-backed
    precedents:
      - "ui/tests/e2e/convert-queue-labels.test.ts:85-366 — Session 81's real-backend helpers, scratch AVKIT_APP_DATA and pid-bound stop (launch at :237)"
      - "ui/tests/e2e/download-queue.test.ts:171-410 — the downloader fetch seam (its own launch records no backend pid, so it is not copied)"
      - "ui/tests/e2e/convert-queue.test.ts:1409-1426 — the narrow-width header test runs at 700 pixels; the window sets no minWidth"
    research:
      engine: local-measurement
      sources:
        - "C:/Temp/av-kit/queue-pause-feedback/qp88-calib.txt — libx265 default preset, 10 s of 1280x720@30 testsrc2: 3074 ms on 24 logical CPUs, so 90 s is about 28 s"
    reasoning: "A real Convert job is the only way to show that the backend keeps Processing during the pending state and pauses after the job, which is the defect. A 28 s job leaves a wide window to click and read, and the 180 s waits cover a loaded host. A real download needs the network, so the Downloader test checks the page's half through the seam; the services' between-jobs rule is shared code, unchanged, and already covered by their own tests. Starting through the Session 81 launch keeps the pid-bound stop on the seam test too, and the reload puts the seam in place before the page's first list read, because an init script added after launch reaches only later loads. 700 pixels is the narrowest width an existing header test already holds, so the wider toggle is checked there. Two-way: test files only."
  - id: D-1095
    stage: planning
    question: "Which existing test expectation changes, and how is it named?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Only the queue header fixture's button text: in ui/tests/unit/fixtures/queue-slot-baseline.json key header, Pause</button> becomes Pause after this job</button>, edited at Red; every other pin in §Test pins passes unchanged."
    source_tag: Local Canon
    precedents:
      - "ui/tests/unit/queue-card-slots.test.tsx:153 — the test that compares the header markup with the fixture"
      - "C:/Temp/av-kit/queue-pause-feedback/qp88-probe.txt — the fixture holds Pause</button> once and the new label nowhere; no test holds a literal Pause label"
    research: { engine: none, sources: [] }
    reasoning: "The fixture records the header's exact markup, so the new label must change it; naming the edit, its old and new text and the test that reads it keeps M-7 clear. Every other pin reads test ids or the label constant. Editing it at Red keeps Green free of expectation changes (S3). Two-way: one string."
  - id: D-1096
    stage: planning
    question: "Where is MEU-155 registered, and how?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "MEU-155 gui-queue-pause-feedback in phase 10, band P2, matrix 10.10, home 10 §Queue pause feedback (residual), dependencies MEU-45 and MEU-46, registered in row 1 by register-meu-155.py bound to the row-0 hash; the issue gets meu_links [MEU-155] when it is resolved in row 5."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/10-queue-card-ui.md:236-248 — the queue toolbar's canon lives in 10"
      - ".agent/context/meu-status.yaml — MEU-45 (QueueToolbar) and MEU-46 (the processor chip) are the toolbar and status MEUs"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:224 — one new MEU, registered at plan time; next free id MEU-155"
      - "C:/Temp/av-kit/queue-pause-feedback/qp88-register-dryrun.txt — the dry run: 27 lines, the anchor and the matrix row, line endings kept"
    research: { engine: none, sources: [] }
    reasoning: "The toolbar and the processor chip are phase 10's, so the residual sits beside them, as the ready-line residual sat in 06. B, homing it in 06 after the ready-line residual, separates it from the toolbar canon it changes. The registration is planned, not run: the grouping says registered at plan time, and the brief for this plan asks that the planner plan it; row 1 runs it, before Red, so the MEU exists before its code. The script refuses on any hash or anchor drift and keeps each file's line endings. Two-way: register rows."
  - id: D-1097
    stage: planning
    question: "Where does the pending state live?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "In the renderer's shared query cache, one mark per queue kind ({ jobId, markedAt? }), with gcTime Infinity, set by the pause commands after a successful request and cleared by start, resume, cancel or the hook; no backend or API change."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/lib/query-client.ts — the shared queryClient the commands and pages already use"
      - "ui/src/renderer/src/features/converter/convert-commands.ts:127-146 — queueContext reads the cached envelope outside React"
      - "AGENTS.md §HDP M-4 — an API, OpenAPI or MCP shape change is a human decision"
    research: { engine: none, sources: [] }
    reasoning: "The commands run outside React (palette, shortcuts) and the pages inside it, and both already share the query cache, so a mark there reaches both without a new store. gcTime Infinity keeps it when the page unmounts, which matters because a Convert job can outlast a visit to another page. A backend field lost because it changes the envelope, OpenAPI and MCP shapes (M-4). React state in the page lost because the palette path runs before the page mounts. What renderer-only costs the user is named inside the D-1091 brief, with the backend field as its option B: a pause from MCP or another window shows no Pausing…, and a reload loses the mark while the backend still pauses. Two-way: one module."
  - id: D-1098
    stage: execution
    question: "Row 4's AC-155.15 found Clear finished moving (about 420 px) when the long status text wraps the header (S8). How does the toolbar keep its place?"
    resolution: human
    class: two-way
    mandatory: [M-5, M-7]
    chosen: "Amendment A1, TOOLBAR_END: QueueToolbar's root container gains ml-auto, so the toolbar sits at the right end of its line and drops to the next line at the right edge when space runs out; the header fixture's toolbar root class gains ' ml-auto' as part of the named edit (PINS_NAMED). QueueHeaderRow.tsx and Transcript are unchanged."
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/queue-pause-feedback/qp-row4-e2e-r1.txt — Clear finished x 912.1, 490.5 and 892.8 px on Convert; the toggle's label fit in every state"
      - "ui/src/renderer/src/components/queue/QueueHeaderRow.tsx:65 — the header is one wrapping flex row; the toolbar follows the chips with no right alignment"
      - "ui/src/renderer/src/components/queue/QueueToolbar.tsx:201 — the toolbar root, relative inline-flex self-start"
      - "ui/src/renderer/src/features/transcript/TranscriptPage.tsx:558 — Transcript passes its own TranscriptToolbar, so it is not affected"
      - "docs/execution/plans/2026-11-17-queue-pause-feedback/implementation-plan.md §Stop Conditions S8 — how the toolbar wraps or sizes is a layout choice for a brief"
    research: { engine: none, sources: [] }
    reasoning: "Where the toolbar sits in the header is a layout choice (M-5), and the fix changes the one named fixture by a class (M-7), so it was Mat's call, and he chose the recommended option in his own words. Right alignment on the toolbar's own root makes its x independent of the chips and counts to its left, keeps the toggle's width class as it is, and leaves the shared frame and Transcript unchanged. Two-way: one class."
    human_message_reference: "USER_EXPLICIT 2026-11-17 'Pin toolbar right (Recommended)'"
open_decisions: []
```

Expert pass (fresh context) 2026-11-17: `C:/Temp/av-kit/queue-pause-feedback/qpf-expert-pass.txt` (av-kit-peer-reviewer, read only, run by the coordinator; advisory). Each cited fact was checked against the code at `ba6d8ef` before it was adopted:

- D-1090: the between-videos check is `transcript.py:491`, not `:407`, and the waits after it run 6 s, 300 s and 30 s at the defaults; the choice moves from A (keep "Pause" as it is) to C (keep "Pause", end the waits on pause or stop), M-8 is added, and the brief gives A, B, C and doing nothing.
- D-1091: a failure while Pausing… shows ends Paused, not Idle; the mark takes its job from the list read after the POST (AC-155.14); the toggle keeps one minimum width (`TOGGLE_WIDTH`, AC-155.15); the brief names the MCP, reload and last-job edges and gives the backend field as option B (M-4).
- D-1092: there is no pause keyboard shortcut and the palette lists the command only on its own page, so the "palette and shortcuts" claim is removed and the decision passes the §4 test: autonomous, `mandatory: none`, brief dropped.
- D-1093: holds; no change.
- D-1094: AC-155.12 starts through the Session 81 `launch` with the seam installed by `addInitScript` and a reload, and checks the fit at 700 pixels, not 760.
- D-1095: holds; the fixture edit also takes the toggle's two width classes.
- D-1096: holds; no change.
- D-1097: holds; its user-visible cost is named inside the D-1091 brief.
- Also adopted: the provenance paragraph in the note above, and the Cancel-while-Paused defect, registered in row 6 and not fixed (§Out of Scope).

Round 1 response (plan review, Codex, 2026-11-17, `C:/Temp/av-kit/qpf-plan-review-round-1.md`, `changes_required`). Both findings are fixed as an execution of D-1091 under the HDP, inside the same hand-over; no new decision id, and D-1098 and D-1099 stay free:

- **R1-F1** (a remount after the list is collected erased a valid mark): `PAUSE_PENDING_HOOK` and `PAUSE_STATUS` now take the observed `processor`, and while it is `undefined` the hook neither clears the mark nor shows Pausing…. Tests: AC-155.6 (a missing list keeps the mark), AC-155.19 (fake time past the 5-minute `gcTime`, remount with the first GET held, both kinds), AC-155.20 and AC-155.21 (one page-level remount per page).
- **R1-F2** (a failed read made a permanent wildcard): `PAUSE_MARK_SET` sets no mark when the read after the POST fails or shows Paused or Idle (the backend's pause only sets a flag, so a repeat is harmless), and `PAUSE_PENDING_RULE` drops the null wildcard: a between-jobs mark binds to the first job id seen within `PAUSE_UNBOUND_MS` (15 s) and is spent after it. Tests: AC-155.3, AC-155.6 and AC-155.14 revised; AC-155.22 runs the reviewer's history (POST ok, failed read, unmount, an unseen Paused and resume, remount on a later job; and the same with an unbound mark) and proves Pause is usable.
- **Q2 ordering:** `PAUSE_MARK_SET` awaits `queryClient.cancelQueries({ queryKey: QUERY_KEY })` before the read and again before `setQueryData`; AC-155.4 and AC-155.5 hold an older poll and check that it cannot overwrite the cache.
- **Q3:** AC-155.16 and AC-155.17 pause at a wait-entry event from a test-side wrapper of `service._sleep`, not after a fixed 0.3 s; no product hook.
- The goal anchor is unchanged. The ACs go from 18 to 22, and the task keeps 26 rows.

### D-1090: What should Transcript's Pause do, given that it can wait minutes?

**I recommend C: keep the word "Pause" on Transcript, and make it pause within a second.** Today a pause there is checked only before each video, and then the service waits: 6 s between videos, 5 minutes after every 50 videos, and 30 s before a retry. So a click at the start of the 5-minute rest does nothing for 5 minutes. On 2026-11-16 you wrote: "Also not sure if other pages have this issue with queue pause or stop fuction. If it is not possible to pause it should not be called pause but something else." C makes the word true: those waits end as soon as you press Pause or Stop, so Stop gets faster too. Nothing in the API, the MCP tools or the settings changes. A can fail in one way: if you pause and resume during the 5-minute rest, the rest is cut short. The hourly request cap (300 by default) still holds, and today's Pause and Resume already restart the count of 50.

- A: keep "Pause" and change nothing on Transcript. Only Convert and Downloader were in the issue, but a Pause that can do nothing for 5 minutes is what your words rule out.
- B: Transcript reads "Pause after this video" and shows Pausing…. It changes a second toolbar and the layout rule that names its three buttons, and the label is wrong during the 5-minute rest, when no video is running.
- Do nothing: as A.

Refs: `transcript.py:491`, `:495`, `:497`, `:581`, `:655-671`, `settings.py:70-74`, 03 §Rate cap (`03-service-layer.md:256`), `TranscriptToolbar.tsx:4-8`, 11 TR1 and TR2 (`11-page-layout.md:28-29`), `known-issues.yaml:5382`, M-5, M-6, M-8.

### D-1091: What does the button do between your click and the pause?

**I recommend A: it reads "Pausing…" and is greyed out until the job ends; Cancel still stops the job at once.** The services cannot take a pause back while a job runs, so a button you could click again would promise something they cannot do. The state ends by itself when the queue pauses, when it goes idle after a Cancel, or when another job starts, so it can never get stuck; if the job fails, the queue still pauses. It stays if you switch pages and come back, however long you were away. The button keeps the same width in every state, so Clear finished beside it never moves under your cursor.

A can fail in five cases, because the "Pausing…" state lives only in this window:

- a pause sent from an MCP client or another window shows no "Pausing…", although the queue still pauses after the job;
- if you reload the app, "Pausing…" is gone while the pause still happens; clicking Pause again does no harm;
- a pause during the last job ends "Queue Paused" with nothing left to run, and Resume then goes straight to idle;
- if the app cannot read the queue right after your click, the button stays "Pause after this job"; the pause still happens, and clicking again does no harm;
- a pause clicked in the instant between two jobs, then a page change and a resume from another window within 15 seconds, can show "Pausing…" for the job that resume started, until it ends.

- B: the backend reports "pause requested" in the queue list, so all three cases show "Pausing…". It changes the API, the OpenAPI document and the MCP tools, which is your call (M-4), so it is not chosen here.
- C: "Pausing…" stays clickable and takes the pause back. It needs a new backend call, which also changes the API.
- D: no in-between state; the button reads "Pause after this job" and stays as it is. Your ruling asks for "Pausing…", so this falls short of it.
- Do nothing: the button gives no sign, which is the reported defect.

Refs: 10 §Toolbar reduction (`10-queue-card-ui.md:243`), `conversion.py:269-272`, `:496`, `:553-558`, `:672-676`, `QueueToolbar.tsx:204-217`, `ConvertPage.tsx:876`, `:880`, `known-issues.yaml:5381`, M-5 (B and C: M-4).

## Research References

- **TanStack Query v5 caching:** `gcTime` is how long inactive cache data stays in memory (default 5 minutes); `Infinity` disables collection. `setQueryDefaults` applies options to a key, and `setQueryData` creates the entry when it is absent and notifies observers. `queryClient.clear()` removes every entry, which the existing page tests already call between tests. `cancelQueries` cancels a query's running fetch and by default reverts its state, so a response that arrives later is dropped; `setQueryData` does not cancel a running fetch (the reviewer's probe confirmed this on the installed core).
- **Python `threading.Event`:** `wait(timeout)` returns `True` as soon as another thread calls `set()`, or `False` when the timeout passes; `clear()` resets it. It is the standard way to make a sleep that another thread can end early, which `TRANSCRIPT_WAKE` uses with the flags as the source of truth.
- **libx265 speed on this PC:** `qp88-calib.txt` (the default preset, 10 s of 1280x720@30 `testsrc2` in 3 074 ms, 24 logical CPUs).

## Planning receipts

All under `C:/Temp/av-kit/queue-pause-feedback/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `qp88-probe.py`, `qp88-probe.txt` | `HEAD` `ba6d8ef` and a clean tree; line endings, sizes and SHA-256 prefixes of the scope; the three new files absent; the row-0 anchors; the fixture label counts; `decision_sources` on the grouping alone and with the issue (D-813 to D-817 both times) |
| `qp88-eol-extra.txt` | Line endings of the help, command and canon test files and of `envelope.ts` and `command-state.ts` |
| `qp88-mixed-ranges.txt` | The bare-LF line ranges of `DownloaderPage.tsx`, `convert-controls.ts` and `downloader-page.behavior.test.ts` |
| `qp88-calib.txt`, `calib/` | The libx265 calibration |
| `qp88-issue-keys.txt`, `qp88-meu-status-help.txt` | The issue's keys (no `verification`, `category` or `meu_links` yet) and the `meu_status.py` commands |
| `qp88-peer-rows.txt`, `qp88-peer-rows2.txt` | The peer plans' row shapes (Sessions 81 and 82) |
| `qp88-ruff-format.txt`, `qp88-ruff-check.txt` | `register-meu-155.py`: formatted, all checks passed |
| `qp88-register-selftest.txt` | `selftest: ok` |
| `qp88-register-dryrun.txt`, `qp88-register-dryrun-diff.txt`, `register/` | The dry run on copies: 27 LF lines in `meu-status.yaml`, 10 CRLF with one anchor, the matrix CRLF with one row, MEU-155 `pending` at 10.10 |
| `qp88-homepath-help.txt` | `tools/check_home_path.py` usage |
| `qpf-expert-pass.txt` | The HDP §5a expert pass (fresh context), adopted as §Decision Log lists |
| `qp88-eol-py.txt` | Line endings of `transcript.py` (LF), `03-service-layer.md` (CRLF), `test_services.py` (CRLF), `settings.py` (CRLF) |
| `qp88-issue-help.txt` | `tools/issue_triage.py` and its `add` usage (row 6) |
| `qp88-probe-ruff-transcript.txt`, `qp88-probe-pyright-transcript.txt` | `ruff format --check`, `ruff check` and `pyright` each exit 0 on `transcript.py` at `ba6d8ef` (row 3b) |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against Mat's ruling (grouping §3 Session 88, the issue), 10 §Toolbar reduction and §Pause scope, 11 TR1 and TR2, and the code reads above | `qp-plan-2026-11-17-queue-pause-feedback` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-155.1 to AC-155.22 | `qp-execution-2026-11-17-queue-pause-feedback` |
