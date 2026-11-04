---
date: "2026-09-28"
project: "2026-09-28-p11-transcript-tts"
meu: "MEU-55"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md"
build_plan_section: "bp11 Transcript page layout"
agent: "Claude Code (claude-opus-5-5)"
reviewer: "Fable 5.1 subagent (pending, H1-7)"
predecessor: "2026-09-26-p11-queue-pages-MEU-54-handoff.md"
---

# Handoff: 2026-09-28-p11-transcript-tts-MEU-55-handoff

> **Status**: `complete` · **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-55 — `gui-transcript-layout`. The page is composed of three parts:

- an Add row with its status line;
- a "Channels" header built on the shared `QueueHeaderFrame`, with nonzero status chips, More, the live processor chip, a rate chip and a three-action toolbar;
- channel rows rendered through `QueueList` → `QueueCard` using additive `CARD_SLOTS`.

Each card carries its own ▲ ▼, status links and ⋮ menu. The page stays single-select. The inherited closed-MEU-48 AC is met: `ChannelCard` is gone, there is no inline `width:` style, and progress uses the shared transform-only `ProgressBar`.

**Build Plan Section**: [Phase 11 Transcript page layout](../../../docs/build-plan/11-page-layout.md#transcript-page-layout) (TR1–TR6; Supersession row "Closed MEU-48 transcript AC"); [Session 25 plan](../../../docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md).

**Predecessor**: [MEU-54 handoff](2026-09-26-p11-queue-pages-MEU-54-handoff.md).

**Boundary inventory**:
- The channel Add still posts `{ channel_url }` through `postTranscriptCreate`.
- ▲ ▼ send the same `PUT /transcripts/reorder` full permutation through `buildReorderBody`, computed for the card's own id.
- Compile, requeue, retry, remove and the three IPC opens call the unchanged `transcript-commands.ts` functions.
- No API, IPC channel or persisted mutation was added. `git status -- packages/api` is empty.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|---|---|---|---|---|---|
| AC-55.1 | unit | `CARD_SLOTS`, `MENU_ITEM_EXTENSION`, `LIST_SLOT_RESOLVER`, `PROGRESS_TONE`: slot-less markup is byte-identical to the pre-change capture; trailing controls are siblings of the region; caller menu items keep `data-testid` and order; `onMenuOpen` fires; the list forwards per-row slots; the success tone swaps only the fill class. | Local Canon `QueueCard.tsx` header, `QueueList.tsx`; grouping "slot, not a rewrite" | `queue-card-slots.test.tsx:41,50,73,106,131` | ✅ |
| AC-55.2 | unit | `HEADER_FRAME` extraction is behavior-neutral: `QueueHeaderRow` markup matches the baseline, the unedited `queue-header-row.test.tsx` passes, and the frame renders title/extra chips/actions with no checkbox unless `leading` is given. `SOURCE_PINS` hold. | Spec canon §Queue header row | `queue-card-slots.test.tsx:153,161,201`; `queue-header-row.test.tsx` (unmodified) | ✅ |
| AC-55.3 | integration | Header "Channels", nonzero chips in `transcript-queue-summary`, More with all six counts, a live processor chip (attached-hidden at Idle), a rate chip mirroring the Processing card, and exactly three toolbar controls with one Pause/Resume node. | Spec TR1, TR2; mockup §02/§03 | behavior `transcript-page.behavior.test.ts:207,229,242`; Electron `transcript-queue.test.ts:525` | ✅ |
| AC-55.4 | integration | Rows render through `QueueList`/`QueueCard` (`channel-card`, `data-job-id`) with no checkbox or drag handle; region click selects; the shared `StatusBadge` is used; there is no `STATUS_COLORS`, `ChannelCard` or `width:` in the page; `CARD_LINE_RULE` applies. | Spec Supersession (MEU-48), TR5, TR6; Local Canon status-tokens | behavior `:268,287`; Electron `:558` | ✅ |
| AC-55.5 | integration | The kebab lists `TRANSCRIPT_MENU_ORDER` ∩ available actions with the existing IDs. Links render only when available and use distinct IDs. ▲ ▼ are disabled at the ends and move their own card. Every per-card action selects its card (TR3). Remove confirms, then deletes that card only. Focus returns to the moved card by `data-job-id` (RULE-1), after proving the fallback precondition (RULE-3). Controls are disabled while busy. | Spec TR3, TR4; mockup §02/§05; COMPOSITION_LOCK | behavior `:310,330,356,372,387,408` (success), rejected-reorder regression (Round 1 correction), `:438`; Electron `:558,583` | ✅ |
| AC-55.6 | integration | The Add row keeps input and Add on one row (placeholder/aria-label "Channel URL"). The status line switches between hint and `error-banner` (role alert). The empty invite focuses the field with no request. The content cap and `QUEUE_SCROLL_CONTAINER_RULE` chain hold. | Spec canon §Transcript, §Shared layout; TR §05 rows 1–6 | behavior `:459,481,493`; Electron `:583,605` | ✅ |
| AC-55.7 | integration | Real Electron wave: header/chips/More/processor/rate chip, toolbar swap, card select and kebab, links → ledger and IPC, card-scoped ▲ ▼ with the resulting order, queue region ≥ 320 px with the scroller on the wrapper, empty state, and header wrap at 760 px. TA-3..TA-5 applied; all W2 tests stay active. | Local Canon AGENTS §Testing Requirements; E2 | `transcript-queue.test.ts:525,558,583,605`; W2-1..W2-6 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|---|---|---|---|
| AC-55.1 slots (4 tests) | `Unable to find … name "Select channel …"`; `expected undefined to deeply equal { accent: 'bg-accent', … }` | pass | `queue-card-slots.test.tsx:50-131` |
| AC-55.2 frame + pins | `QueueHeaderFrame export: expected undefined to be type of 'function'` | pass | `:161,201` |
| AC-55.3–55.6 (14 tests) | `Unable to find an element by: [data-testid="queue-header-row"]`; `expected [null,…] to deeply equal ['a','b','c','d','e']`; `expected 'flex flex-col gap-4 p-4' to contain 'h-full'` | pass | `transcript-page.behavior.test.ts:207-493` |
| AC-55.7 Electron (4 specs) | `stats.unexpected = 4`, each an `expect(` failure (the header, links, ▲ ▼ and empty state did not exist) | pass | `transcript-queue.test.ts:525-605` |

The two baseline guards (AC-55.1 slot-less markup and AC-55.2 header markup) passed in Red by design: they pin the unchanged markup.

**Setup-only test repairs made after Red** (no assertion was changed):
- `renderPage` now waits for the stubbed `/transcripts` load. The empty invite rendered before the first fetch and satisfied the old wait.
- The RULE-3 blur precondition parks focus on an enabled field, because jsdom ignores `blur()` on a disabled button.

### Commands Executed

| Command | Exit Code | Key Output |
|---|---|---|
| `bash …/validate-task.sh red-55` | 0 | `PASS AC-55 RED: 9 failing AC-55 assertions, 2 passing` (23 collected; 21 failed, all assertion or element-not-found) |
| `bash …/validate-task.sh e2e-red-55` | 0 | `PASS AC-55 E2E RED: 4 failing AC-55 specs` |
| `bash …/validate-task.sh green-55` | 0 | `PASS s25-55-green-vitest: 170 passed, env-bound tolerated: [AC-51.6, AC-41.3]` |
| `bash …/validate-task.sh e2e-55` | 0 | `54 passed (10.8m)` — transcript + download + convert Electron files |
| `bash …/validate-task.sh static` | 0 | `PASS s25-static-typecheck`, `PASS s25-static-lint` (0 warnings) |
| `bash …/validate-task.sh amendments` | 0 | `PASS amendment guard` (frozen suites untouched; no skip/only/todo) |

```json
{"schema_version":"evidence.v1","check_id":"s25-55-green","command":"bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh green-55","cwd":"/home/user/av-kit","scope":"UNIT55 + REG55 (queue-card-slots, transcript-page.behavior, queue-header-row, queue-card, queue-list, transcript-page, layout-primitives, queue-primitives, bulk-action-bar, convert-page, downloader-page, help-card, queue-canon)","phase":"targeted","exit_code":0,"result":"pass","tested_state":"worktree on 1ed5c7b + MEU-55 edits","output":"PASS s25-55-green-vitest: 170 passed, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 ', 'Phase 10 queue-card canon (MEU-41) AC-41']","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s25-55-e2e","command":"bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh e2e-55","cwd":"/home/user/av-kit","scope":"fresh ui build; real Electron under xvfb-run, ELECTRON_DISABLE_SANDBOX=1: transcript-queue, download-queue, convert-queue","phase":"targeted","exit_code":0,"result":"pass","tested_state":"worktree on 1ed5c7b + MEU-55 edits (before the W2-5 timeout-budget change)","output":"54 passed (10.8m) … PASS s25-55-e2e","fresh":true}
```

### Quality Gate Results

```
tsc --noEmit: 0 errors
eslint src/ tests/ --max-warnings 0: 0 problems
vitest (targeted MEU-55 set): 170 passed; 2 ENV_BOUND_TESTS tolerated with proven signatures
playwright (3 files): 54 passed
anti-placeholder / width audit: covered by H1-2 pregate and WINDOWS_GATE
```

### W2-5 duration (observed, disclosed)

Under the Transcript seam in this container, every Playwright click settles in about 2.0 s (55 clicks, min 1.93 s, max 2.05 s in a W2-5 trace). The same clicks after the Downloader seam take 0.05 s, and the untouched W2-6 already takes 7 s for three clicks, so this behavior predates the change. TA-5 reaches per-card actions through the kebab, which added about 20 clicks, so W2-5 ran for 1.9 min against its 120 s budget. The budget was raised to 180 s as a setup-only part of TA-5 (below). The authoritative timing is the Windows gate.

### WINDOWS_GATE (authoritative D6 fresh full gate)

Mat ran `validate-task.ps1 -Check windows-gate` in `P:/av-kit` on `7dab4d1` (clean tree, Node v24.19.0, `electron@42.9.3`, lockfile `A86D9A42…`). All 9 stages exited 0: npm-ci, ui-types, ui-lint, ui-tests, ui-build, ui-harness-build, ui-electron, source-audit, width-audit. Vitest 630/630, including AC-51.6 and AC-41.3 on Windows. Electron: 103 expected, 0 unexpected, 0 flaky, including AC-49.26 and the four capture-picker specs. `validate-task.sh windows-gate-check` then passed in the container against HEAD `e71395d`, with no code change since the tested commit.

```json
{"schema_version":"evidence.v1","check_id":"s25-windows-gate","command":"pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.ps1 -Check windows-gate; then bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh windows-gate-check","cwd":"P:/av-kit (Windows) / /home/user/av-kit (check)","scope":"PROFILE D6 UI fresh full gate: npm ci, typecheck, lint, full Vitest, build, isolated harness build, full real Electron, source and width audit","phase":"full","exit_code":0,"result":"pass","tested_state":"7dab4d153c60103de1d24257deaed4b52dcb9e16 (code-identical to e71395d)","output":"PASS windows gate @ 7dab4d153c60103de1d24257deaed4b52dcb9e16: vitest {'passed': 630, 'failed': 0, 'total': 630} e2e {'expected': 103, 'unexpected': 0, 'skipped': 0, 'flaky': 0}","fresh":true}
```

**Round 1 rerun (after `9fb0153`).** On `c315640` the first run failed at `ui-electron`: Capture W9-3 hit a 60 s test timeout plus a worker-teardown timeout, the test had no code overlap with this session, and the result was not pushed. Its `error-context.md` was lost to later single-spec reruns (see walkthrough). After a quiet-machine check, the second run passed all 9 stages: Vitest 631/631, Electron 103 expected, 0 unexpected, 0 flaky, with W9-3 at 22.5 s. It was pushed as `692b483`, and `windows-gate-check` passed against that HEAD. `692b483` differs from the tested commit only in the result file.

```json
{"schema_version":"evidence.v1","check_id":"s25-windows-gate-r1","command":"pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.ps1 -Check windows-gate; then bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh windows-gate-check","cwd":"P:/av-kit (Windows) / /home/user/av-kit (check)","scope":"PROFILE D6 UI fresh full gate after the Round 1 fix","phase":"full","exit_code":0,"result":"pass","tested_state":"c315640d05cc7ddf8293c8f0b64733c209bb0028 (code-identical to 692b483)","output":"PASS windows gate @ c315640d05cc7ddf8293c8f0b64733c209bb0028: vitest {'passed': 631, 'failed': 0, 'total': 631} e2e {'expected': 103, 'unexpected': 0, 'skipped': 0, 'flaky': 0}","fresh":true}
```

---

## Changed Files

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modified | `QueueCardSlots` (regionLabel, metaContent, detailContent, trailingControls, menuItems, onMenuOpen); defaults unchanged |
| `ui/src/renderer/src/components/queue/QueueCardMenu.tsx` | modified | generic `QueueMenuItem<Id>`, optional `testId`, `onOpenChange` (transitions only) |
| `ui/src/renderer/src/components/queue/QueueList.tsx` | modified | `cardSlots` per-row resolver; slot props omitted from list-wide props |
| `ui/src/renderer/src/components/queue/QueueHeaderRow.tsx` | modified | `QueueHeaderFrame` extracted; `QueueHeaderRow` wraps it with the same API and markup |
| `ui/src/renderer/src/components/ui/ProgressBar.tsx` | modified | `tone` prop; fill class from `PROGRESS_FILL_CLASSES` |
| `ui/src/renderer/src/lib/queue/status-tokens.ts` | modified | `ProgressTone`, `PROGRESS_FILL_CLASSES` |
| `ui/src/renderer/src/features/transcript/transcript-card.ts` | new | `TRANSCRIPT_MENU_ORDER`, test IDs, `cardActionAvailable` (exhaustive), menu/link actions, counts, card mapping |
| `ui/src/renderer/src/features/transcript/TranscriptToolbar.tsx` | new | `TRANSCRIPT_TOOLBAR` (three controls, one Pause/Resume node) |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modified | page composition; the footer row and `ChannelCard` removed; `TRANSCRIPT_TEST_IDS`, error event, Escape and portal confirm kept |
| `ui/tests/unit/queue-card-slots.test.tsx` | new | AC-55.1, AC-55.2 |
| `ui/tests/unit/transcript-page.behavior.test.ts` | new | AC-55.3–AC-55.6 |
| `ui/tests/unit/fixtures/queue-slot-baseline{-cases.ts,.json}` | new | pre-change markup baseline captured at `1ed5c7b` |
| `ui/tests/e2e/transcript-queue.test.ts` | modified | AC-55.7 cases; TA-3, TA-4, TA-5 |
| `ui/tests/e2e/test-ids.ts` | modified | 9 additive IDs appended after the MEU-51 hash marker |
| `ui/tests/unit/layout-primitives.test.ts` | modified | TA-1 (Transcript half) |
| `ui/tests/unit/queue-primitives.test.ts` | modified | TA-2 |

```diff
-export type QueueMenuItem = {
-  /** Canonical action id, drawn from {@link KEBAB_MENU_ORDER}. */
-  id: QueueMenuActionId
+export type QueueMenuItem<Id extends string = QueueMenuActionId> = {
+  /** Action id: canonical by default, or the caller's own closed set. */
+  id: Id
```

```diff
-  const menuItems = resolveQueueMenuItems({
+  const menuItems = props.menuItems ?? resolveQueueMenuItems({
 ...
-      {menuItems.length > 0 ? (
+      {trailingControls !== undefined ? trailingControls : null}
+
+      {menuItems.length > 0 ? (
```

### TEST_AMENDMENTS applied (before → after)

| TA | Class | File:test | Before | After |
|---|---|---|---|---|
| TA-1 | D | `layout-primitives.test.ts` AC-51.7 | `['transcript','TranscriptPage']` in the forbidden-import list | Removed from that list; new assertion that `TranscriptPage` imports `components/ui/StatusChip`. TTS, Capture and Settings stay forbidden. |
| TA-2 | C | `queue-primitives.test.ts` STATUS_COLORS census | Census listed `features/transcript/TranscriptPage.tsx` | Entry removed; `transcript-controls.ts` and both TTS entries kept |
| TA-3 | A, B | `transcript-queue.test.ts` W2-3 | `pause-btn` and `resume-btn` both `toBeVisible`; page-level `up-btn`, `down-btn`, `remove-btn`, `compile-btn`, `view-compiled-btn`, `open-zip-btn`, `open-folder-btn` visible with zero cards | Seeds one Done card with `setQueue` (setup). `pause-btn` visible, `resume-btn` count 0 (TR2). ▲ ▼ scoped to the card; menu IDs asserted after opening its kebab. `processor-indicator` `toBeAttached` unchanged. |
| TA-4 | B | W2-4 | `output-tree`, `last-title`, `rate-display` and `eta-display` all visible on the one Pending card | `output-tree` visible on the Pending card, then `setQueue` makes it Processing and asserts `last-title`, `rate-display` and `eta-display` (TR5; mockup §05 row 9) |
| TA-5 | A, setup | W2-5 | Page-level `up-btn`/`down-btn`/`remove-btn`/`compile-btn`/`view-compiled-btn`/`open-zip-btn`/`open-folder-btn`/`requeue-btn`/`retry-btn`; `test.setTimeout(120_000)` | ▲ ▼ scoped to the moved card (re-found by `data-job-id`). Each per-card action is reached by opening `queue-card-kebab` first. `test.setTimeout(180_000)` (budget for the extra kebab clicks). Every ledger/IPC `expect.poll` assertion is byte-identical. |

---

## Codex Validation Report

The independent review is in `.agent/context/handoffs/2026-09-28-p11-transcript-tts-implementation-critical-review.md`, written by the Fable 5.1 subagent (`claude-fable-5-1-subagent`). Round 1 was `changes_required` (1 Medium, 1 Low; see Corrections Applied). Round 2 was `approved` with 0 blocking findings and one Low (F3). `validate-task.sh review-check … execution 6` passes. This section cites the reviewer's file; the coordinator authored no verdict.

---

## Corrections Applied (2026-09-28, execution review Round 1)

**Findings resolved**: 2/2

| # | Finding | Fix Applied | Verification |
|---|---|---|---|
| 1 | Medium: after a *rejected* ▲ ▼ reorder, focus stayed on `body`, because the restore effect returned early on an unchanged order (`TranscriptPage.tsx` pendingFocus effect). | Removed the early return and the unused `from` field. Once the command settles, focus goes to the card's same-direction button, else the other one (matches the Session 24 `QueueList` fallback). | New test `AC-55.5 focus returns to the card after a rejected reorder too` was Red on the old page (`expected <body> to be <button>`) and is Green after the fix. `green-55` 171 passed; `static` pass; `amendments` pass. |
| 2 | Low: W2-5 timeout 120 → 180 s is labelled TA-5 but is not a declared TA-5 edit. | Recorded as an execution amendment (setup time budget) in `walkthrough.md`, with the trace evidence. | No assertion changed. |

---

## Deferred Items

- **F3 (Low, non-blocking, optional follow-up):** the ▲ ▼ focus restore in `TranscriptPage.tsx` is unconditional, like the approved Session 24 `QueueList` fallback. If the user moves focus to the still-enabled Channel URL field during a reorder, focus returns to the card. No AC requires otherwise. A future change could skip `focus()` when `document.activeElement` is neither `body` nor inside the card, in both components. Not scheduled.

---

## History

| Event | Date | Agent | Detail |
|---|---|---|---|
| Created | 2026-09-28 | Claude Code | MEU-55 Red → Green → targeted gate |
| Corrected | 2026-09-28 | Claude Code | Execution review Round 1 fix `9fb0153` (rejected-reorder focus) |
| Windows gate | 2026-09-28 | Mat (local agent) | `c315640`: run 1 W9-3 hang (not pushed); run 2 passed, result `692b483` |
| Approved | 2026-09-28 | claude-fable-5-1-subagent | Execution review Round 2 `approved`; MEU-55 set to `approved` in H2-2 |
