---
project: "2026-09-28-p11-transcript-tts"
date: "2026-09-28"
source: "docs/build-plan/11-page-layout.md"
meus: ["MEU-55", "MEU-56"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Phase 11 Transcript and TTS Pages

> **Project**: `2026-09-28-p11-transcript-tts`
> **Build Plan Section(s)**: `docs/build-plan/11-page-layout.md` §§Decision register (TR1–TR6, TT1–TT7), Transcript page layout, TTS page layout, Supersession, Test-ID migration (TR 1–22, TT 1–28)
> **Status**: `draft`; independent plan review required before execution

---

## Goal

Deliver Session 25 of `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` as grouped:

- **MEU-55 `gui-transcript-layout`**: an Add row with its status line; channel rows on the shared `QueueCard` anatomy through `QueueList`; the 13-button footer replaced by a three-action header toolbar, per-card ▲ ▼ and a per-card ⋮ menu; single-select preserved.
- **MEU-56 `gui-tts-layout`**: a Text and Voice two-column grid, Cleanup and Manage-models disclosures, a one-line-per-voice list, a speed slider with a preset segment, and one static run bar.

Both MEUs carry the closed MEU-48 ACs as mandatory ACs (grouping §"MEU-48 is closed, not cancelled"; canon §Supersession):

- MEU-55: the Transcript `ChannelCard` renders through the shared queue primitives, with no inline `width: %` style (G33).
- MEU-56: TTS uses the shared `ProgressBar`, not a local bar.

Everything stays inside `COMPOSITION_LOCK`: same IPC, same API payloads, same persisted mutations, same enablement and save behavior, and every existing test-ID string. This session does not exit Phase 11; that happens in Session 26 (MEU-57/58).

The baseline is commit `0f51036` (the draft plan itself was committed on top of it at `9c4a341` after a stop-hook request) on branch `claude/amazing-albattani-qcl51p`, with MEU-49 through MEU-54 `approved` in `.agent/context/meu-status.yaml` and MEU-55/56 `pending`. The Session 24 reflection (`docs/execution/reflections/2026-09-26-p11-queue-pages-reflection.md` §Next Session Design Rules) carries three rules forward. Each is bound to an AC below:

- **RULE-1 (shared-root lookup)**: AC-55.3 and AC-55.5.
- **RULE-2 (async init yields to user ownership)**: AC-56.3 and AC-56.4.
- **RULE-3 (prove the fallback precondition)**: AC-55.5.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "2026-09-28 static check: graphify-out/ and graphify-out-research/ are absent (ls: No such file or directory); no headroom binary on PATH and no headroom skill under .agent/skills. Scope is TSX page/component source, canon docs, grep output and exact receipts, which are Headroom bypass classes."
  human_message_reference: null
```

Row 1 of `task.md` re-evaluates this inventory before execution (create-plan §5f).

**Resolved driver** (`.agent/docs/harness-profiles.md` + `.agent/context/harness.local.md` §Claude Code): Claude Code in a claude.ai cloud Linux container. That gives:

- `plan_to_exec_gate: human`. The Cursor `reviewer-auto` override does not transfer.
- `native_shell: bash` (harness-profiles §notes: the Bash tool resolves to `bash`), `read_tool: Read`, `shell_tool: Bash`.
- `fresh_worker: Agent tool + .claude/agents/`.

**Environment deviations from the PowerShell-shaped D6 registry.** These are recorded for the reviewer, not silently assumed:

- `rtk`, `pwsh` and PowerShell are not installed (`which rtk pwsh` returns nothing).
- The D6 argv in `.agent/docs/commands.md` §D6 are therefore run directly in POSIX form. Each command redirects all streams with `> "$RECEIPTS_DIR/<id>.txt" 2>&1`, captures `code=$?` immediately, reads the receipt with `cat`, and ends with `exit $code`. That is the form `tools/lint_task_contract.py` accepts.
- A raw invocation is the unfiltered equivalent of `rtk proxy` exact evidence.
- `RECEIPTS_DIR` is exported to the session scratchpad (fallback `/tmp/av-kit`) instead of `C:/Temp/av-kit`.
- Electron E2E runs under `xvfb-run -a` because the container has no display (`/usr/bin/xvfb-run` is present). Because the container runs as root, `ELECTRON_DISABLE_SANDBOX=1` is set; Chromium refuses to start as root with its sandbox on (verified 2026-09-28).
- `ui/node_modules` is absent (0 entries), so row 1 installs locked dependencies with `npm --prefix ui ci`, followed by `ELECTRON_SETUP`.
- **Gate location** ([human-gate-decision.md](human-gate-decision.md), `USER_EXPLICIT` 2026-09-28): two baseline Vitest tests (`ENV_BOUND_TESTS`) cannot pass in this container. The authoritative D6 fresh full gate is therefore `WINDOWS_GATE`, run by Mat on Windows. The container runs a non-authoritative pre-gate.

**Reviewer route.** The Codex CLI is not installed. Per the user's direct instruction ([human-review-decision.md](human-review-decision.md)), both review loops use a Claude Code `Agent` subagent with `model: fable` (Fable 5.1), prompted at high effort. This is a surfaced same-vendor exception to `AGENTS.md` §Dual-Agent Workflow. The author never writes the verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-55` | `.agent/context/handoffs/2026-09-28-p11-transcript-tts-MEU-55-handoff.md` |
| `MEU-56` | `.agent/context/handoffs/2026-09-28-p11-transcript-tts-MEU-56-handoff.md` |
| Plan review (rolling) | `.agent/context/handoffs/2026-09-28-p11-transcript-tts-plan-critical-review.md` |
| Project implementation review (rolling) | `.agent/context/handoffs/2026-09-28-p11-transcript-tts-implementation-critical-review.md` |

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Prerequisites: context-tool recheck, SSOT prerequisite proof, dependency install, frozen FIC and `TEST_AMENDMENTS` census | — | `shared` | `walkthrough.md` §Prerequisites; `$RECEIPTS_DIR/s25-prereq.txt` |
| WP-2 | MEU-55 Red: shared-slot unit tests, Transcript behavior tests, Electron AC-55 cases, TA-1..TA-5 amendments | WP-1 | `shared` | Test files; Red JSON and receipts |
| WP-3 | MEU-55 Green: `CARD_SLOTS`, `HEADER_FRAME`, `ProgressBar` tone, Transcript composition | WP-2 | `shared` | Production files; Green receipts |
| WP-4 | MEU-55 gate and handoff | WP-3 | `compact_continue` | MEU-55 handoff; compact, then re-read `task.md` and the handoff before WP-5 |
| WP-5 | MEU-56 Red: TTS behavior tests, Electron AC-56 cases, TA-6/TA-7 amendments | WP-4 | `shared` | Test files; Red JSON and receipts |
| WP-6 | MEU-56 Green: TTS composition | WP-5 | `shared` | Production files; Green receipts |
| WP-7 | MEU-56 gate and handoff | WP-6 | `compact_continue` | MEU-56 handoff; compact, then re-read `task.md` and the handoff before H1 |
| WP-8 | H1 container pre-gate and SSOT review state → push → `WINDOWS_GATE` (Mat) → independent execution review → H2 `POST_REVIEW_STATE`, reflection, metrics, commit draft | WP-7 | `shared` | Rolling review, reflection, metrics, final receipts |

The main session does the coder, tester and orchestrator roles inline. It does not delegate implementation rows. `fresh_worker` is available, but the page and component edits share one context and need cross-row reasoning, which excludes the `av-kit-builder` mechanical class. The only fresh workers are the reviewer subagents.

---

## User Review Required

> [!IMPORTANT]
> 1. **Reviewer route**: same-vendor Fable 5.1 subagent, user-authorized. See [human-review-decision.md](human-review-decision.md).
> 2. **Pre-declared test amendments (`TEST_AMENDMENTS`, TA-1..TA-7)**: seven existing test assertions become obsolete *interaction paths* or *mount preconditions* under the locked TR/TT decisions. They are declared below for independent plan review, so they can be applied without the mid-execution stop that Session 24 needed (`docs/execution/plans/2026-09-26-p11-queue-pages/implementation-plan.md` §Execution amendments). No expected value, request ledger assertion or IPC assertion changes. Any other pre-existing assertion that fails is a human-decision stop.
> 3. **Open questions OQ-1..OQ-3** were resolved by plan review round 1: OQ-1 A, OQ-2 A, OQ-3 A.
>
> Following an independent `approved`, this standalone `/create-plan` run ends at the human plan-to-execution gate and waits for a direct user message to execute.

---

## Proposed Changes

### Authority and single-statement contracts

Each name below is defined once, here, and referenced by name elsewhere (create-plan §4 single-statement rule).

| Name | Single definition |
|---|---|
| `COMPOSITION_LOCK`, `PRESERVED_TESTIDS`, `QUEUE_SCROLL_CONTAINER_RULE` | `docs/build-plan/11-page-layout.md` §§Scope, Test-ID migration, Queue scroll container rule. Not restated. |
| `CARD_SLOTS` | Additive, optional `QueueCard` props:<br>• `regionLabel?: string` — the activatable region's accessible name (default unchanged: `Open details for {title}`).<br>• `metaContent?: ReactNode` — replaces the text meta line when supplied.<br>• `detailContent?: ReactNode` — a third line inside the region.<br>• `trailingControls?: ReactNode` — rendered as **siblings** of the region, between the primary action and the kebab.<br>• `menuItems?: readonly QueueMenuItem<string>[]` — replaces `resolveQueueMenuItems` output when supplied.<br>• `onMenuOpen?: () => void` — fires when the kebab opens.<br>A card that passes none of them renders byte-for-byte the markup it renders today (`DND_OPT_IN_RULE` precedent). |
| `MENU_ITEM_EXTENSION` | `QueueCardMenu` and `QueueMenuItem` become generic over a caller-owned closed id union (`QueueMenuItem<Id extends string = QueueMenuActionId>`) and gain an optional `testId` rendered as `data-testid` on the `menuitem`. `QueueCardMenuProps` gains `onOpenChange?: (open: boolean) => void`. The existing download/convert items, keyboard behavior and default test IDs (`queue-card-kebab`, `queue-card-menu`) are unchanged. |
| `LIST_SLOT_RESOLVER` | `QueueList` gains `cardSlots?: (job: QueueCardJob) => CardSlotValues`, a pure per-row resolver for `CARD_SLOTS`. It follows the `metaSegments` resolver precedent in `QueueList.tsx`. Absent means unchanged markup. |
| `HEADER_FRAME` | `QueueHeaderFrame` is exported from `QueueHeaderRow.tsx`. It owns the row layout, the optional `title`, the nonzero `StatusChip` group with the read-only More summary (`queue-status-more` / `queue-status-details`), the processor chip, an optional `extraChips` node, an optional `leading` node and a required `actions` node. `QueueHeaderRow` becomes a thin wrapper that passes `QueueSelectionHeader` as `leading` and `QueueToolbar` as `actions`. Its public props and rendered DOM are unchanged. |
| `PROGRESS_TONE` | `ProgressBar` gains optional `tone?: 'accent' \| 'success'` (default `accent`, which keeps the current classes). `success` uses the `accent-green` fill token per the Transcript mockup §04. Both fill classes come from `PROGRESS_FILL_CLASSES` in `lib/queue/status-tokens.ts` (see `SOURCE_PINS`). The fill still animates `transform: scaleX` only. |
| `TRANSCRIPT_MENU_ORDER` | `['requeue','retry','compile','view-compiled','open-zip','open-folder','remove']` in `transcript-card.ts`. Menu `testId`s are the existing `requeue-btn`, `retry-btn`, `compile-btn`, `view-compiled-btn`, `open-zip-btn`, `open-folder-btn`, `remove-btn`. |
| `CARD_ACTION_AVAILABLE(card, action)` | For compile / view-compiled / open-zip / open-folder / remove / up / down: `controlEnabled(action, { items, selectedId: card.id, processorState })`. For requeue / retry: `actionVisible(action, card.status)`. `controlEnabled` stays the source of truth (Transcript mockup "Scope"; TR4). Unavailable actions are **absent** from the menu. While `busy`, available items render `disabled` (the `QueueCardMenu` absent-vs-disabled rule). |
| `CARD_LINKS` | Status → candidate links: Done → view-compiled, open-zip; Processing → open-folder; Failed → retry; Cancelled → requeue; any other status → none. Rendered only where `CARD_ACTION_AVAILABLE` holds (TR4). IDs are `view-compiled-link`, `open-zip-link`, `open-folder-link`, `retry-link`, `requeue-link` (mockup §05: links get their own IDs). Links sit in `trailingControls`, as siblings of the region, never inside it (WCAG 2.2 SC 4.1.2, `QueueCard.tsx` header). |
| `CARD_TARGET_RULE` | Every per-card control (menu item, link, ▲ ▼) targets **its own card id** and first sets `selectedId` to that card. Opening the card's ⋮ also selects it (TR3). Remove opens the existing portal confirm, which then removes the now-selected card. |
| `TRANSCRIPT_TOOLBAR` | Exactly three interactive elements, in order: `start-btn`, one Pause/Resume node, `stop-btn`. All are `Button variant="ghost" size="sm"` with text labels. The Pause/Resume node has id `resume-btn`, label Resume and action `resumeTranscripts` when `processorState === 'Paused'`. Otherwise it has id `pause-btn`, label Pause and action `pauseTranscripts`. Enablement is `controlEnabled(...) && !busy` (TR1, TR2). No Clear finished control and no overflow. |
| `CARD_LINE_RULE` | **Line 2** (`metaContent`): the text `{done} / {count} transcripts · {words} words`, then `channel-progress` (`ProgressBar` with `testId="channel-progress"`, value `done/count`, `tone="success"` when Done; mounted iff `video_count > 0 && status !== 'Failed'`), then `rate-display`/`eta-display` when status is Processing and `formatRateEta` is non-null.<br>**Line 3** (`detailContent`): `last-title` (`Last: {title} {last_item_status}`) when status is Processing and `last_title` is present. Otherwise `output-tree`, whose visible text is `{root} · raw · compiled`, whose `title` holds both full paths, and which contains `sr-only` spans with both full `outputTreeLabels` paths (TR5). |
| `RUN_BAR_SLOT` | TTS run-bar right slot, in precedence order:<br>1. `error-banner` (`role="alert"`) when an error is present.<br>2. Otherwise `segment-progress` when `RUN_ACTIVE`.<br>3. Otherwise `last-output`.<br>Exactly one of the three is mounted. |
| `RUN_ACTIVE` | `cancelEnabled({ status })` from `tts-controls.ts`: status ∈ {Pending, Generating}. Not restated as a literal set. |
| `OUTPUT_ACTIONABLE` | `openOutputEnabled(openTarget)`, with `openTarget` computed exactly as today. `open-output-btn` and `open-output-folder-btn` are mounted iff it holds (TT4, "when actionable"; `COMPOSITION_LOCK` keeps the existing predicate and target). |
| `CLEANUP_LABELS` | `Record<PrepareStep, string>` in `tts-prepare.ts`, exhaustive at compile time: `punctuation`→Punctuation, `symbols`→Symbols, `numbers`→Numbers, `currency`→Currency, `all_caps`→All caps, `chapter_markers`→Chapter markers, `urls_emails`→URLs & emails, `page_numbers`→Page numbers, `whitespace`→Whitespace, `chunk`→Chunk, `kokoro`→Kokoro. Labels come from TTS mockup §02; checkbox `value`s stay the `PREPARE_STEPS` ids (TT2). |
| `LOADED_CHIP_TEXT` | Loaded: `{catalogName ?? variant_id} · {device}`, where `catalogName` is `name` of the `useModelsAvailable` item whose `id === variant_id`, and `device` is `statusQuery.data.device ?? device`. Not loaded: `No model loaded`. The full current string (`Loaded: {variant_id} ({device}) · {bytes} B` / `No model loaded`) moves unchanged to `loaded-model-details` inside Manage (TT3). |
| `VOICE_LISTBOX` | `voice-grid` has `role="listbox"` with `aria-label="Voice"`. Each `voice-card` is a `role="option"` element with `aria-selected={voice === id}` and a roving `tabIndex` (0 on the selected option, or on the first option when none is selected; -1 otherwise). ArrowUp/ArrowDown/Home/End move focus only. Click, Enter or Space selects, and **always** PUTs `voice`, even when that voice is already selected. The option contains no nested interactive element. Resolved by plan review round 1: OQ-1 option A. |
| `SOURCE_PINS` | Frozen source-text assertions over files this plan modifies. Implementation must satisfy them unedited:<br>• `queue-primitives.test.ts` AC-43.2 (`:408-416`) forbids single-token `'bg-accent-…'`/`'text-status-…'` literals in `components/ui` and `components/queue`. So `PROGRESS_TONE`'s fill classes are exported as `PROGRESS_FILL_CLASSES` from `lib/queue/status-tokens.ts`, which that census exempts, and `ProgressBar` imports them.<br>• AC-43.6 (`:514-520`): `ProgressBar.tsx` keeps `transition-[transform]`, `var(--duration-normal)` and `var(--ease-out)`, with no `width:`, `w-[` or `transition-all`.<br>• `QueueHeaderRow.tsx` keeps the verbatim strings `<QueueSelectionHeader`, `total={total}`, `selectedCount={selectedCount}`, `onToggleAll={onToggleAll}`, `flex flex-wrap items-center`, `data-testid={summaryTestId}`, `<QueueToolbar {...toolbar} />` and `from './QueueToolbar'`. These are pinned by `bulk-action-bar.test.ts:304-308`, `convert-page.test.ts:751-754` and `downloader-page.test.ts:513-515,546-549`. `QueueHeaderRow` therefore passes `leading={<QueueSelectionHeader total={total} selectedCount={selectedCount} onToggleAll={onToggleAll} … />}` and `actions={<QueueToolbar {...toolbar} />}`, and the frame keeps its class and summary attribute text.<br>• `queue-card.test.ts:483-488`: no new `QueueCard.tsx` identifier may match `on[A-Za-z]*Cancel[A-Za-z]*` (`onMenuOpen` is compliant).<br>• `transcript-page.test.ts` AC-21.16: `TranscriptPage.tsx` keeps the exported `TRANSCRIPT_TEST_IDS` array (`:38-66`) with every current ID literally present.<br>• `help-card.test.ts:104-105`: both `TranscriptPage.tsx` and `TTSPage.tsx` keep a `HelpCard` reference.<br>• `tts-page.test.ts:386-392` (AC-22.22): every Wave-2 TTS ID stays literally present in `TTSPage.tsx` and `test-ids.ts`.<br>• `layout-primitives.test.ts` AC-51.6 (`:185-189`) hashes `test-ids.ts` up to the `// MEU-51 primitive harness IDs.` marker, so every new ID is appended at the **end** of `test-ids.ts`. |
| `ENV_BOUND_TESTS` | The only Vitest failures tolerated in the Linux container, each accepted only with its proven signature (`vitest_env_ok` in `validate-task.sh`):<br>• `layout-primitives.test.ts` AC-51.6 fails only if the recomputed CRLF hash of the `test-ids.ts` prefix equals the expected `819760B9…` and the failure message cites it.<br>• `queue-canon.test.ts` AC-41.3 fails only if `P:/zorivest` is absent and the message cites it.<br>Any other failure, or either one without its signature, fails the run. `WINDOWS_GATE` tolerates none. The two tests are never skipped or edited. |
| `ELECTRON_SETUP` | When `npm ci` leaves no Electron binary (the postinstall download aborts through the container proxy), `validate-task.sh electron-setup` downloads the matching release zip with curl, requires its SHA-256 to equal the package's `checksums.json` entry, unpacks it as `electron/install.js` does, and proves `electron --version` under xvfb. |
| `WINDOWS_GATE` | The authoritative D6 fresh full gate: `validate-task.ps1 -Check windows-gate`, run by Mat in `P:/av-kit` on the pushed commit. It runs these stages in order through `rtk proxy`, stops at the first failure, and writes `windows-gate-result.json`: `npm-ci`, `ui-types`, `ui-lint`, `ui-tests`, `ui-build`, `ui-electron`, `source-audit`, `width-audit`. `validate-task.sh windows-gate-check` accepts it only if the tree was clean, every stage exited 0, Vitest failed = 0 and E2E unexpected = 0, and `git diff` shows no `ui/`, `packages/` or `mcp-server/` change between the tested commit and HEAD. |
| `TEST_AMENDMENTS` | Only these pre-existing assertions may be edited, only in the listed class. Classes:<br>• **A** — interaction path: open a disclosure or menu first, or scope a locator to its card.<br>• **B** — mount precondition set by a locked decision (TR2, TR5, TT3, TT4, TT5, §05 rows).<br>• **C** — migration census shrink.<br>• **D** — pre-adoption restriction lift.<br>No request, IPC ledger, payload or expected value changes. Each edit is recorded before/after in its MEU handoff.<br>• **TA-1** (D) `ui/tests/unit/layout-primitives.test.ts` AC-51.7: move `TranscriptPage` and `TTSPage` from the forbidden list to a positive adoption assertion (Transcript: `StatusChip`; TTS: `Disclosure`, `SegmentedControl`, `StatusChip`). Capture and Settings keep the restriction.<br>• **TA-2** (C) `ui/tests/unit/queue-primitives.test.ts` `STATUS_COLORS` census: remove `features/transcript/TranscriptPage.tsx`. The file's own comment says to "shrink it as each page migrates". `transcript-controls.ts` and both TTS entries stay.<br>• **TA-3** (A, B) `ui/tests/e2e/transcript-queue.test.ts` W2-3: assert exactly one of `pause-btn`/`resume-btn` by processor state (TR2). W2-3 has no cards, so the test first seeds one Done card with the existing `setQueue` seam helper (a setup precondition only). Then scope `up-btn`/`down-btn` to that card and assert the menu IDs after opening its kebab. `processor-indicator` `toBeAttached` (`:258`) stays unedited.<br>• **TA-4** (B) W2-4: `last-title` on the Processing seam card and `output-tree` on a non-Processing seam card (TR5). `rate-display`/`eta-display` on the Processing card (mockup §05 row 9, "processing only").<br>• **TA-5** (A, B) W2-5: reach per-card actions through the card kebab or links. Use card-scoped ▲ ▼. Re-query the Pause/Resume node after the state swap.<br>• **TA-6** (A, B) `ui/tests/e2e/tts-generate.test.ts` W2-3: open `cleanup-toggle` before asserting `cleanup-pipeline` and `preview-cleanup-btn` (`:255`) visible, and open `model-manage-toggle` before `model-manager`. At idle, assert `last-output` ("No output yet") instead of `segment-progress` (`RUN_BAR_SLOT`).<br>• **TA-7** (A, B) W2-4/W2-5:<br>– Open `cleanup-toggle` before `preview-cleanup-btn` and `model-manage-toggle` before `model-get-btn`, `model-load-btn`, `unload-btn` and `device-select` (`:333`).<br>– After Generate (`:276`), the TTS seam job stays `Generating` on its own (`tts-generate.test.ts:156-172`; only DELETE moves it to Cancelled). So the amended W2-4 first moves the seam job to `Done` with an output path through a class-B `page.evaluate` seam mutation (the W2-5 pattern at `:305-314`; `useTtsJob.ts:76` polls). It then asserts `last-output`. While the job is `RUN_ACTIVE`, the slot shows `segment-progress`, so asserting `last-output` without the mutation would only pass by racing the POST.<br>– Assert the open-output buttons only where `OUTPUT_ACTIONABLE` holds in the seam state.<br>– Retarget any long loaded-model string assertion to `loaded-model-details`.<br>– Every ledger assertion (`:340-356`) stays byte-identical. |

**Test discipline for every AC.**

- Each control AC names a production entrypoint, the observable, and a concrete negative oracle. Test titles carry their AC IDs.
- All behavior-suite and Electron assertions for an MEU are written before its production edit. They are run to an **assertion-failure** Red receipt; a launch, build or collection failure is not Red.
- Tests are never weakened to reach Green, and `skip`/`only`/`todo` are forbidden (G36).
- Interaction tests use `userEvent` (G37).
- Electron E2E uses the existing renderer seams (`installTranscriptSeam`, `installTtsSeam`) and DOM geometry at the default window size.

### MEU-55 — `gui-transcript-layout`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Channel Add (UI → `POST /transcripts`) | `postTranscriptCreate` in `transcript-commands.ts`; `TranscriptCreateIn` in `packages/api/src/avkit_api/schemas/transcripts.py` via `ApiModel(extra="forbid")` | Body stays `{ channel_url }` only (AC-21.2). Blank/whitespace input issues no request (existing `addFromForm`). | API rejects malformed/extra fields with 422; no new create or update path. |
| Reorder (UI → `PUT /transcripts/reorder`) | `buildReorderBody` in `transcript-controls.ts`; API reorder schema in `schemas/transcripts.py` | Full `job_ids` permutation (AC-21.8). The moved id is the card's own id (`CARD_TARGET_RULE`). | 422 on a malformed body; unchanged. |
| Processor start/pause/resume/stop, compile, requeue, retry, remove; IPC openPath / showItemInFolder / openZip | Existing `transcript-commands.ts` functions | No new field; invoked from new locations only. | Existing API/IPC validation unchanged; no new IPC channel. |

No REST, MCP, file-import or env/config input surface is added.

#### Acceptance Criteria

| AC | Type | Description and production → observable chain | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-55.1 | unit | **`CARD_SLOTS`, `MENU_ITEM_EXTENSION`, `LIST_SLOT_RESOLVER`, `PROGRESS_TONE` in isolation.** `QueueCard` renders `trailingControls` and `CARD_LINKS` as siblings of the `role="button"` region. It renders `menuItems` with each item's `data-testid` in the given order, calls `onMenuOpen` when the kebab opens, and uses `regionLabel` as the region's name. `QueueList` forwards `cardSlots(job)` per row. `ProgressBar tone="success"` swaps only the fill color class and keeps `transform: scaleX`. | Local Canon: `QueueCard.tsx` header (WCAG 2.2 SC 4.1.2), `QueueList.tsx` resolver precedent; grouping §"What this grouping deliberately does not do" ("expressed as a `QueueCard` slot, not a rewrite") | A trailing control nested inside the region, a menu item missing its `data-testid`, or `onMenuOpen` not firing fails. A card rendered **without** any slot whose `outerHTML` differs from the pre-change snapshot captured in the Red row fails (byte-for-byte unchanged). |
| AC-55.2 | unit | **`HEADER_FRAME` extraction is behavior-neutral.** `QueueHeaderRow` still renders the selection header, nonzero chips, More summary, processor chip and the four-control `QueueToolbar` in the same DOM order with the same IDs. The existing `ui/tests/unit/queue-header-row.test.tsx` passes unmodified. `QueueHeaderFrame` renders `title`, `extraChips` and `actions`, with no checkbox when `leading` is absent. | Spec: canon §Queue header row ("Transcript may reuse the header anatomy"); grouping Session 25 | Any edit to `queue-header-row.test.tsx`, a changed DOM order on Downloader/Convert, or a frame rendering a checkbox without `leading` fails. |
| AC-55.3 | integration | **Header row and three-action toolbar.** `TranscriptPage` → `useTranscriptQueue` data → `QueueHeaderFrame` with title "Channels", no selection, and `JOB_STATUSES` counts from the loaded items. The chip group has `data-testid="transcript-queue-summary"` and shows nonzero chips; More lists all six counts. `processor-indicator` is a live chip for Processing/Paused. When Idle it stays attached but `hidden`, as the approved `QueueHeaderRow.tsx:78-79` does, so the existing `toBeAttached` at `transcript-queue.test.ts:258` holds unedited (TR12 move). `transcript-rate-chip` mirrors the Processing card's exact `formatRateEta` strings while the processor is Processing and is otherwise not mounted. Actions are `TRANSCRIPT_TOOLBAR`. Clicks go through `startTranscripts`/`pauseTranscripts`/`resumeTranscripts`/`stopTranscripts`. Locators resolve inside the header root (RULE-1). | Spec: TR1, TR2; canon §Transcript page layout; mockup §02 Zone 2 and §03 note | More than three interactive elements in the toolbar, both `pause-btn` and `resume-btn` in the DOM at once, a zero-count visible chip, a *visible* processor chip at Idle (it must stay attached and `hidden`), a Clear finished control, or a click on a disabled control issuing a request fails. |
| AC-55.4 | integration | **Channel rows on the shared card (inherited MEU-48 AC).** Items map to `QueueCardJob` (`id`, `position=queue_position`, `status`, `title=channel_name`) and render through `QueueList` with `rowTestId="channel-card"`, no `onMoveToIndex`/`queueKey` (drag stays off: `ReorderQueueKey` is `'download' \| 'convert'` in `reorder-single-flight.ts`), `selectedIds=[selectedId]` for the selected style, and `cardSlots` supplying `CARD_LINE_RULE`, `CARD_LINKS`, ▲ ▼ and `TRANSCRIPT_MENU_ORDER` items. Clicking a card's region selects it (TR3, TR6); the region name is `Select channel {name}`. The status pill is the shared `StatusBadge`; `TranscriptPage.tsx` no longer imports `STATUS_COLORS`. Source contains no inline `width:` style. | Spec: canon §Supersession (closed MEU-48 transcript AC), TR5, TR6; Local Canon: `lib/queue/status-tokens.ts` (single status→pill map, AC-43.2) | Any `style={{ width` or `width: \`${…}%\`` in `TranscriptPage.tsx`; a checkbox or bulk bar; a drag handle; a second card selected; or a `channel-card` without `QueueCard` markup (`data-job-id`) fails. |
| AC-55.5 | integration | **Per-card actions.** Kebab items follow `TRANSCRIPT_MENU_ORDER` ∩ `CARD_ACTION_AVAILABLE`, with the existing IDs. `CARD_LINKS` render only when available. ▲ `up-btn` / ▼ `down-btn` are ghost icon buttons with `aria-label` `Move {name} up/down`, disabled at the ends and while `busy`. Every control follows `CARD_TARGET_RULE`. ▲ ▼ issue `PUT /transcripts/reorder` with `buildReorderBody(ids, card.id, dir)`. Compile/view/open/requeue/retry/remove call the same commands as today. Remove opens the unchanged portal confirm (`remove-confirm-btn` / `remove-confirm-cancel`). After a reorder response, the moved card is re-found by `data-job-id` inside the list root (RULE-1). Before asserting focus lands on the moved card's control, the test proves the fallback precondition (RULE-3): hold the response, blur, release. | Spec: TR3, TR4; mockup §02/§05; `COMPOSITION_LOCK`; AC-21.8/21.10/21.15 | A menu showing an unavailable action; a link and a menu item sharing an ID; ▲ on the first card being enabled; ▲ on card B reordering the previously selected card A; Remove deleting a different card than the one whose menu was used; or a `window.confirm` fails. |
| AC-55.6 | integration | **Add row, status line, empty state and geometry.** `channel-input` (flex-1, md, placeholder and `aria-label` "Channel URL") and `add-btn` (primary md) sit on one row. The status line shows `channel-url-hint`, or `error-banner` (`role="alert"`) while an error exists; the empty hidden `error-banner` stays mounted otherwise. An empty queue renders `transcript-empty-invite` via `QueueList.emptyState`, whose `transcript-empty-invite-action` button focuses `channel-input` without a request. The page applies the content cap (`--layout-page-max-width`) and the `QUEUE_SCROLL_CONTAINER_RULE` chain: root `h-full min-h-0`, a controls pane `min-h-0 overflow-auto`, a `shrink-0` header, a queue region `flex-1 min-h-[20rem]` and `overflow-auto` on the wrapper around `QueueList`, never on the list. | Spec: canon §Transcript and §Shared layout primitives (cap); TR §05 rows 1–6; Local Canon: `QUEUE_SCROLL_CONTAINER_RULE` and `QueueList` overflow contract | Blank Add issuing a POST, the hint and error both visible, the empty action issuing a request, overflow on `QueueList`, or a queue region under 20rem at the default window fails. |
| AC-55.7 | integration | **Real Electron wave for MEU-55.** `ui/tests/e2e/transcript-queue.test.ts` gains AC-55 cases that exercise, against real Electron and the seam: the header chips, More and the processor chip transition; the three toolbar actions with the Pause→Resume node swap; card select by click; kebab open-selects and each available item's request/IPC ledger entry; the status links; card-scoped ▲ ▼ with the reorder body and disabled ends; remove confirm and cancel; the empty state; responsive header wrapping; and queue-region height ≥ 20rem. TA-3..TA-5 are applied. All existing W2 tests stay active. | Local Canon: `AGENTS.md` §Testing Requirements; E2; grouping Session 25 | A unit-only substitute, a conditional early return, an inert moved control, or a skipped existing test fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Toolbar census, Pause/Resume node, no Clear finished | Spec | TR1, TR2 (mockup §06 "if that action is out of scope, ship three" → locked three). |
| Menu opens select; single select; no bulk | Spec | TR3, TR6. |
| Which menu items and links show | Spec + Local Canon | TR4 ("only for actions currently available"). Candidate links come from the mockup §06 proposal. Availability is `controlEnabled`/`actionVisible` (mockup "Scope"). |
| Line 3 content and output-tree accessibility | Spec | TR5. |
| Links not nested in the activatable region | Local Canon | `QueueCard.tsx` header comment, citing WCAG 2.2 SC 4.1.2. This overrides the mockup's inline placement on line 2; the links sit visually at the right of the row. |
| Status pill colors | Local Canon | `status-tokens.ts` is the single map (AC-43.2). The mockup §04 "map from STATUS_COLORS" is superseded because canon §Supersession keeps Phase 10 binding. |
| Drag reorder | Local Canon | Excluded: `ReorderQueueKey` comment "Transcript and TTS are out of scope for drag/reorder". The mockup draws only ▲ ▼. |
| Failed-card error text (mockup §02 "429 Too Many Requests…") | Local Canon | `TranscriptListItem` carries no error field (`useTranscriptQueue.ts`). `COMPOSITION_LOCK` forbids a new API field, so the Failed line 2 shows counts only and no bar. |
| Queue scroll chain on Transcript | Local Canon | The canon rule names the two Zone 1 queue pages. Transcript adopts it because it now mounts `QueueList`, whose overflow contract requires the per-page wrapper. |
| Header rate chip | Spec (mockup) | Mockup §02/§03 note: "a duplicate view, not a replacement". It uses the existing `formatRateEta` strings only; no new computation. OQ-3 records the alternative. |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modify | `CARD_SLOTS` (additive, default markup unchanged). |
| `ui/src/renderer/src/components/queue/QueueCardMenu.tsx` | modify | `MENU_ITEM_EXTENSION` (generic id, `testId`, `onOpenChange`). |
| `ui/src/renderer/src/components/queue/QueueList.tsx` | modify | `LIST_SLOT_RESOLVER`. |
| `ui/src/renderer/src/components/queue/QueueHeaderRow.tsx` | modify | Extract `QueueHeaderFrame`; `QueueHeaderRow` wraps it with an unchanged API and DOM. |
| `ui/src/renderer/src/components/ui/ProgressBar.tsx` | modify | `PROGRESS_TONE` (classes imported from status-tokens). |
| `ui/src/renderer/src/lib/queue/status-tokens.ts` | modify | Add `PROGRESS_FILL_CLASSES` (`accent`, `success`), the single palette home per AC-43.2. |
| `ui/src/renderer/src/features/transcript/transcript-card.ts` | new | `TRANSCRIPT_MENU_ORDER`, `CARD_ACTION_AVAILABLE`, `CARD_LINKS`, status counts, `QueueCardJob` mapping (pure). |
| `ui/src/renderer/src/features/transcript/TranscriptToolbar.tsx` | new | `TRANSCRIPT_TOOLBAR`. |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modify | Composition. Removes the footer row and local `ChannelCard`. Keeps the confirm portal and error event. |
| `ui/tests/unit/queue-card-slots.test.tsx` | new | AC-55.1, AC-55.2 (frame). |
| `ui/tests/unit/transcript-page.behavior.test.ts` | new | AC-55.3–AC-55.6 with a request ledger. |
| `ui/tests/e2e/transcript-queue.test.ts` | modify | AC-55.7 cases; TA-3, TA-4, TA-5. |
| `ui/tests/e2e/test-ids.ts` | modify | Additive: `transcript-queue-summary`, `transcript-rate-chip`, `transcript-empty-invite`, `transcript-empty-invite-action`, `view-compiled-link`, `open-zip-link`, `open-folder-link`, `retry-link`, `requeue-link`. No existing string changes. |
| `ui/tests/unit/layout-primitives.test.ts` | modify | TA-1 (Transcript half). |
| `ui/tests/unit/queue-primitives.test.ts` | modify | TA-2. |

### MEU-56 — `gui-tts-layout`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| TTS settings leaves (UI → `PUT /settings/tts`: `input_text`, `voice`, `speed`, `output_format`, `device`, `output_path`) | `putSettings` in `tts-commands.ts`; the settings request model in `packages/api` via `ApiModel(extra="forbid")` | Same leaves and debounce. Speed presets set the same `speed` values `0.8/1.0/1.1` within the slider range 0.5–2.0 step 0.1 (AC-22.12). Voice/format/device values unchanged. | 422 on invalid body; unchanged. Moving a control never creates a second write path. |
| Prepare (`POST /tts/prepare`), Generate (`POST /tts/generate`), Cancel (`DELETE`), model download/load/unload | Existing `tts-commands.ts` builders | `enabled_steps` still carries raw `PREPARE_STEPS` ids (TT2). Generate body unchanged (AC-22.7). | Unchanged; the API rejects malformed input with 422. |
| IPC: readTextFile, readClipboardText, showDirectoryDialog, openPath, showItemInFolder | Existing preload bridge | Unchanged. | No new channel. |

#### Acceptance Criteria

| AC | Type | Description and production → observable chain | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-56.1 | unit | **`CLEANUP_LABELS` is exhaustive and value-preserving.** `CLEANUP_LABELS` has exactly the 11 `PREPARE_STEPS` keys (a compile-time `Record<PrepareStep, string>`). Each rendered checkbox's `value` equals its step id. | Spec: TT2; mockup §02 labels | A missing or extra key fails typecheck. A checkbox whose `value` is a human label fails. |
| AC-56.2 | integration | **Two-column grid, Text panel and Cleanup disclosure.** `TTSPage` renders a capped, left-aligned grid `minmax(0,1.45fr) minmax(300px,1fr)` at ≥ 880 px, stacked text-first below. The Text panel header "Text" labels `text-input` (11 rows, `resize-y`) and holds `load-file-btn`/`paste-btn` (ghost sm). The footer holds `word-count`/`sentence-count`/`duration-estimate` (`tabular-nums`) and the `Disclosure` toggle `cleanup-toggle` (`Cleanup · {enabledSteps.length} of 11 steps`, initially closed, local state). The panel holds `cleanup-pipeline` (3-column, `CLEANUP_LABELS`), `preview-cleanup-btn` (secondary sm) and `preview-raw`/`preview-cleaned` side by side. Toggling issues no request. Preview still posts `{ text, enabled_steps }` only. | Spec: canon §TTS page layout; TT2; mockup §02/§04/§05 rows 1–10 | A toggle click issuing a request, a hidden-panel checkbox reachable by Tab, a stale step count after unchecking, or a preview body with extra keys fails. |
| AC-56.3 | integration | **Voice panel, model chip and Manage disclosure.** The Voice header shows `loaded-model` as a `StatusChip` (`LOADED_CHIP_TEXT`; tone `success` loaded, `warning` not loaded) and the `Disclosure` toggle `model-manage-toggle` (initially closed, local state). The panel holds `model-manager` with `device-select` (SelectInput G30), `unload-btn` (ghost sm), `model-row`s keeping the existing `model-get-btn`/`model-load-btn` index rule, `download-progress` (`%` text plus `ProgressBar` `download-progress-bar`), and `loaded-model-details` carrying the unchanged full string. A late model-status refetch updates the chip but never closes a Manage panel the user opened (RULE-2). | Spec: TT3; mockup §02/§05 rows 11–15; Local Canon: Session 24 RULE-2 | Dropping bytes/variant/device detail, a refetch closing Manage, a `model-get-btn` on the wrong row, or device change not PUTting `device` fails. |
| AC-56.4 | integration | **Language, voice list, speed and format.** `language-select` (SelectInput) filters as before. `voice-grid` becomes a single-column scrollable list (max-height ~236 px) of one-line `voice-card` rows (`id · description · language`) implementing `VOICE_LISTBOX`. Each activation (click, Enter or Space), including re-activating the already-selected voice, calls `setVoice` and PUTs `voice` exactly once. This preserves the current click-always-PUTs behavior that `tts-generate.test.ts:328` and `:350-354` rely on. `speed-slider` keeps min 0.5 / max 2.0 / step 0.1 and its label shows `Speed {x.x}×`. The preset `SegmentedControl` (native radios `speed-preset-0-8`, `speed-preset-1-0`, `speed-preset-1-1`) sets the same values and PUTs `speed`; when speed is not a preset, no radio is checked. `format-select` stays a native `SelectInput` with values MP3/WAV (TT1). Settings hydration applies once and never overwrites a later user choice (RULE-2). | Spec: TT1, TT6; mockup §02/§05 rows 16–21; UX1 (segment for mutually exclusive presets); G30 | A voice preview control or dead ID (TT6), a `<select>` replaced by a segment for format, a preset changing the slider range, a hydration landing after a user choice and reverting it, or a double PUT per choice fails. |
| AC-56.5 | integration | **Static run bar (inherited MEU-48 AC).** Below both columns, not sticky (TT7): `output-path` (readonly, ~220 px), `browse-output-btn` (ghost sm), `generate-btn` (primary md), `cancel-btn` (secondary md), the status pill (unchanged `STATUS_COLORS`), and the `RUN_BAR_SLOT`. While `RUN_ACTIVE`, `segment-progress` holds the shared `ProgressBar` (`segment-progress-bar`, value `segments_done/segments_total`, 0 when total is 0) plus `Segments d/t · preview · hash`. When idle, `last-output` shows the path or muted "No output yet" (TT5), with `open-output-btn`/`open-output-folder-btn` mounted iff `OUTPUT_ACTIONABLE` (TT4). `TTSPage.tsx` contains no inline `width:` style and no local bar. | Spec: canon §Supersession (closed MEU-48 TTS AC), TT4, TT5, TT7; mockup §02/§05 rows 22–28 | A local progress div, a percentage width, `position: sticky`/`fixed` on the run bar, two slot children mounted at once, open buttons mounted when `OUTPUT_ACTIONABLE` is false, or "No output yet" missing at idle fails. |
| AC-56.6 | integration | **Real Electron wave for MEU-56.** `ui/tests/e2e/tts-generate.test.ts` gains AC-56 cases covering: grid column count at the default window and stacking at a narrow window; the Cleanup toggle count and panel; the Manage toggle and model actions; the chip text; the voice list selection PUT; the preset radios PUT; format select; the run-bar slot transitions (idle → generating with the progress bar's `aria-valuenow` → done with open buttons); and error replacing the slot. TA-6/TA-7 are applied. All existing W2 tests stay active. | Local Canon: `AGENTS.md` §Testing Requirements; E2; grouping Session 25 | A unit-only substitute, a conditional early return, or a skipped existing test fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Format control, labels, chip, open buttons, idle copy, preview, stickiness | Spec | TT1–TT7. |
| Open buttons "only when output exists" | Spec | TT4's test-ID effect says "when actionable" and `COMPOSITION_LOCK` keeps the enablement predicate, so the existing `openOutputEnabled(openTarget)` decides mounting (`OUTPUT_ACTIONABLE`). The canon decision is more specific than UX2's grayout preference. |
| Run-bar slot swap (error / progress / output) | Spec (mockup §05 rows 3, 26, 27) + TT5 | Error replaces the slot (mockup row 3). Progress only while running (row 26). Idle keeps "No output yet" (TT5 overrides row 27's "hidden when no output"). |
| Disclosure initial state | Spec (mockup §03) | Both disclosures start closed ("collapse behind a toggle", "open on demand"). No settings field drives them, so RULE-2 only forbids a refetch changing them. |
| Voice list semantics | Research-backed + reviewer decision | `VOICE_LISTBOX`. OQ-1 was resolved to option A by plan review round 1: a native radio (option B) fires no change on an already-checked voice, which would break the frozen voice-PUT ledger assertion `tts-generate.test.ts:350-354`. |
| Disclosure toggle size | Local Canon | The MEU-51 `Disclosure` primitive renders its own ghost `Button` at the default size. The mockup §04 "sm" is not applied, to avoid forking an approved primitive; recorded as a deviation. |
| No-model hint text in the run bar (mockup §02) | Spec | Excluded. TT5 locks the idle slot content to "No output yet". |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | Composition per AC-56.2–56.5. |
| `ui/src/renderer/src/features/tts/tts-prepare.ts` | modify | `CLEANUP_LABELS`. |
| `ui/src/renderer/src/features/tts/tts-run-bar.ts` | new | Pure `RUN_BAR_SLOT` resolver (`'error' \| 'progress' \| 'output'`, exhaustive switch). |
| `ui/tests/unit/tts-page.behavior.test.ts` | new | AC-56.1–AC-56.5 with a request ledger. |
| `ui/tests/e2e/tts-generate.test.ts` | modify | AC-56.6 cases; TA-6, TA-7. |
| `ui/tests/e2e/test-ids.ts` | modify | Additive: `cleanup-toggle`, `model-manage-toggle`, `loaded-model-details`, `speed-preset-0-8`, `speed-preset-1-0`, `speed-preset-1-1`, `segment-progress-bar`, `download-progress-bar`. |
| `ui/tests/unit/layout-primitives.test.ts` | modify | TA-1 (TTS half). |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Capture and Settings page composition; Phase 11 phase gate | deferred | MEU-57, MEU-58 | Grouping Session 26 is the Phase 11 exit. This session runs targeted and full UI regression, not a phase-exit claim. |
| Transcript Clear finished / toolbar overflow | out-of-scope | — | TR1 (`docs/build-plan/11-page-layout.md` decision register): no new Clear finished mutation and no empty fourth overflow. |
| Transcript multi-select, checkboxes, bulk bar | out-of-scope | — | TR6. |
| Transcript drag reorder and Alt+Arrow keyboard reorder | out-of-scope | — | `ui/src/renderer/src/lib/queue/reorder-single-flight.ts` `ReorderQueueKey` doc ("Transcript and TTS are out of scope for drag/reorder"). The Transcript mockup §05 row 17 specifies only ▲ ▼. |
| Failed-channel error message on the card | out-of-scope | — | `COMPOSITION_LOCK` (no new API field); `TranscriptListItem` has no error field. |
| "Queued … press Start" confirmation copy after Add | out-of-scope | — | Canon §Transcript page layout enumerates Add, rows and toolbar with no new feedback state. `COMPOSITION_LOCK` keeps existing feedback. |
| TTS voice preview | out-of-scope | — | TT6. |
| TTS no-model hint in the run bar | out-of-scope | — | TT5 locks the idle slot content. |
| Removing `STATUS_COLORS` from `transcript-controls.ts` | out-of-scope | — | It is asserted by the existing AC-21.18 (`ui/tests/unit/transcript-page.test.ts`), and TA-2 keeps its census entry. Only the page import retires. |
| New API endpoint, persisted mutation, IPC channel | out-of-scope | — | `COMPOSITION_LOCK`; grouping "No backend work". |
| Commit, push, merge, release, deploy | out-of-scope | — | `AGENTS.md` §Commits; PROFILE E5. Not authorized by `/create-plan`. |

---

## BUILD_PLAN.md Audit

`docs/BUILD_PLAN.md` line 72 says "Next: Phase 11 page layout (MEU-55)", and line 55 lists Sessions 25–26 as pending. Neither becomes stale during H1, while MEU-55/56 are `ready_for_review`. After independent implementation approval, H2-2 produces `POST_REVIEW_STATE`:

- MEU-55/56 `approved` with this plan's binding, via `uv run python tools/meu_status.py update`, then `render` and `render --check`.
- Grouping Session 25 row → `approved` with the real folder.
- Hub line 72 Next → `Next: Phase 11 page layout (MEU-57)`, and line 55 → MEU-55–56 approved in Session 25, with Session 26 pending for MEU-57–58.
- `.agent/context/current-focus.md` → Session 26.

Generated tracker spans are not hand-edited. `validate-task.sh post-review-state` asserts every postcondition; H1 cannot claim them.

---

## Verification Plan

Every command runs from the repo root after `export RECEIPTS_DIR=<session scratchpad>/receipts` (fallback `/tmp/av-kit`). The multi-step procedures live in [validate-task.sh](validate-task.sh), so task-table cells stay lintable. Execute them only **after plan approval and a direct human execution message**.

| Check (D6 ID) | Exact command | Required evidence |
|---|---|---|
| Prerequisites | `bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh prereq > "$RECEIPTS_DIR/s25-prereq.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-prereq.txt"; exit $code` | MEU-49/51/52 approved, MEU-55/56 pending, `ui/node_modules` present, graphs absent, Electron `--version` starts under `xvfb-run`. |
| Red unit MEU-55 (ui-tests, targeted) | `bash …/validate-task.sh red-55 > "$RECEIPTS_DIR/s25-55-red-check.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-55-red-check.txt"; exit $code` | Vitest JSON has ≥1 failed AC-55 assertion, zero pending/todo, no suite load error. |
| Red Electron MEU-55 (ui-electron, targeted) | `bash …/validate-task.sh e2e-red-55 > "$RECEIPTS_DIR/s25-55-e2e-red-check.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-55-e2e-red-check.txt"; exit $code` | Fresh build ok; Playwright JSON `stats.unexpected ≥ 1` with an AC-55 `expect(` failure. |
| Green/targeted MEU-55 | `bash …/validate-task.sh green-55 > "$RECEIPTS_DIR/s25-55-green.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-55-green.txt"; exit $code` | `queue-card-slots`, `queue-header-row` (unmodified), `queue-card`, `queue-list`, `transcript-page`, `transcript-page.behavior`, `layout-primitives` and `queue-primitives` green. Also green: every `SOURCE_PINS` suite (`bulk-action-bar`, `convert-page`, `downloader-page`, `help-card`). |
| Electron MEU-55 | `bash …/validate-task.sh e2e-55 > "$RECEIPTS_DIR/s25-55-e2e.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-55-e2e.txt"; exit $code` | Fresh build; `transcript-queue.test.ts` plus `download-queue.test.ts` and `convert-queue.test.ts` (shared-component regression) pass. |
| Red / Green / Electron MEU-56 | `validate-task.sh red-56`, `e2e-red-56`, `green-56`, `e2e-56` in the same receipt form | As above, for the AC-56 and TTS files. |
| Static per MEU (ui-types, ui-lint) | `bash …/validate-task.sh static > "$RECEIPTS_DIR/s25-55-static.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-55-static.txt"; exit $code` (the `s25-56-static` receipt for MEU-56) | Typecheck exit 0; lint exit 0 with zero warnings. |
| Handoff census | `bash …/validate-task.sh handoff-census > "$RECEIPTS_DIR/s25-handoff-census.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-handoff-census.txt"; exit $code` | Each handoff contains its first and last AC, its TA IDs, an `evidence.v1` block and `CACHE BOUNDARY`. Fails on any missing marker or file. |
| Amendment guard | `bash …/validate-task.sh amendments > "$RECEIPTS_DIR/s25-amendments.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-amendments.txt"; exit $code` | Modified pre-existing test files ⊆ the `TEST_AMENDMENTS` files. `queue-header-row.test.tsx`, `transcript-page.test.ts` and `tts-page.test.ts` are unmodified. No `.skip`/`.only`/`.todo` under `ui/tests`. |
| Container pre-gate (non-authoritative) | `bash …/validate-task.sh pregate > "$RECEIPTS_DIR/s25-pregate.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-pregate.txt"; exit $code` | Input identity; typecheck 0; lint 0 warnings; full Vitest with only `ENV_BOUND_TESTS` tolerated; build; full Electron under xvfb; zero source-audit hits for `TODO\|FIXME\|NotImplementedError\|transition-all\|bg-\[#`; no inline `width:` in the two pages. Stops at the first failure. |
| **`WINDOWS_GATE` (authoritative D6 fresh full gate)** | Mat, on Windows in `P:/av-kit`: `pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.ps1 -Check windows-gate`. Validated in the container by `bash …/validate-task.sh windows-gate-check > "$RECEIPTS_DIR/s25-windows-gate-check.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-windows-gate-check.txt"; exit $code` | A clean-tree run of all eight stages with exit 0, Vitest failed = 0, E2E unexpected = 0, and the tested commit code-identical to HEAD. |
| Electron setup | `bash …/validate-task.sh electron-setup > "$RECEIPTS_DIR/s25-electron-setup.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-electron-setup.txt"; exit $code` | `ELECTRON_SETUP`: checksum-verified binary, `--version` under xvfb. |
| Reflection markers | `bash …/validate-task.sh reflection > "$RECEIPTS_DIR/s25-reflection-markers.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-reflection-markers.txt"; exit $code` | The reflection exists with all four required markers. |
| API scope | `git status --porcelain=v1 --untracked-files=all -- packages/api > "$RECEIPTS_DIR/s25-api-status.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-api-status.txt"; exit $code` (the receipt must contain no path rows) | UI-only proof. OpenAPI drift is skip-with-basis. Any API change stops and re-plans. |
| Task contract (task-contract) | `uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-09-28-p11-transcript-tts/task.md > "$RECEIPTS_DIR/s25-task-lint.txt" 2>&1; code=$?; cat "$RECEIPTS_DIR/s25-task-lint.txt"; exit $code` | `OK:` first line. |

`…` abbreviates `docs/execution/plans/2026-09-28-p11-transcript-tts` in this table only; `task.md` cells spell out the full path. An Electron launch failure that reproduces as an external display or dependency error may be `[B]`, with the exact receipt and a linked CI follow-up (known issue `E2E-SANDBOX-NODISPLAY`). The E2E tests must still be written and wired.

### N. OpenAPI Drift Check

No `packages/api/` change is planned. H1-4 proves this. If the proof fails, stop and re-plan the boundary, then run `uv run python tools/export_openapi.py --check openapi.committed.json` before any `-o` regeneration.

## GUI Element Compliance Check (create-plan §4A)

The step is triggered: both MEUs move buttons, inputs, selects and output elements. `docs/gui-element-reference.md`, the three GUI indexes and `.agent/docs/gui-standards-enforcement.md` are absent in this checkout (`ls` exit 2), so their checklist and Target Spec columns cannot be claimed as checked (`gui-refs-not-shipped`). The plan instead maps against the live components and G-standards:

- **Button variants and sizes (G34)**, from `Button.tsx` (five variants, three sizes):
  - Add and Generate: primary md.
  - Cancel: secondary md.
  - Toolbar actions, Load file, Paste, Browse, Unload, ▲ ▼ (icon): ghost sm.
  - Preview and Get: secondary sm.
  - Load: primary sm (unchanged).
  - Remove: a destructive menu item, with the confirm's existing destructive/outline buttons.
- **Controls**: `Disclosure` toggles (MEU-51), `SegmentedControl` native radios for presets (UX1), `SelectInput` with `getG30Styles` for device, language and format (G30).
- **Status**: `StatusChip`/`StatusBadge` with readable text (G32 tokens only; no raw hex).
- **Motion (G33)**: transform-only `ProgressBar`; no `transition-all`.
- **Feedback tiers (G35)**: existing tiers kept. Action buttons use `busy` disabling (T1). The error surface is `error-banner` `role="alert"` (T3). Settings leaves keep their silent autosave with error surfacing, unchanged by `COMPOSITION_LOCK`.
- **E2E (E2)**: every new or moved interactive element has a written, wired Electron assertion in AC-55.7 or AC-56.6.

The reviewer is asked to judge this live-source substitution.

## Stop Conditions

- Do not execute before independent plan approval **and** a direct human execution message (`plan_to_exec_gate: human`).
- In execution, stop and re-plan or ask if any of these happen:
  - MEU-49/51/52 stop being `approved`.
  - Any behavior needs an API, IPC or persisted-mutation change.
  - A §05 ID or action cannot be preserved.
  - A pre-existing assertion outside `TEST_AMENDMENTS` fails.
  - Red is not demonstrated as an assertion failure.
  - `queue-header-row.test.tsx` or the Downloader/Convert E2E regress.
  - A P1 check fails.
- An Electron launch failure proven external is `[B]` with evidence, not a silent pass.
- **Planned stop at H1-6 (`WINDOWS_GATE`).** After pushing, the run ends the turn and waits for Mat's `windows-gate-result.json`. This is a human-run external step authorized in [human-gate-decision.md](human-gate-decision.md), not a completion claim. A failing Windows stage returns work to the owning MEU row.
- A reviewer `changes_required` verdict means correct and re-dispatch within the caps (plan 3, execution 6). The cap is a hard stop.
- No commit, push, merge, release or deploy without direct human direction.

---

## Open Questions

**All three are resolved by plan review round 1** (`.agent/context/handoffs/2026-09-28-p11-transcript-tts-plan-critical-review.md`, Finding 1):

- **OQ-1 → A** (`VOICE_LISTBOX`). B was rejected because of the frozen voice-PUT ledger at `tts-generate.test.ts:350-354`.
- **OQ-2 → A** (`HEADER_FRAME`).
- **OQ-3 → A** (`transcript-rate-chip`).

The table below is kept as the decision record, updated to show the locked choices.

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| **OQ-1** Voice list single-selection semantics (mockup §05 row 17 proposes "role listbox") | A. `role="listbox"` + `role="option"` + `aria-selected` | WAI-ARIA APG Listbox pattern (https://www.w3.org/WAI/ARIA/apg/patterns/listbox/); search summary: single-select options carry `aria-selected` | Most exact semantics; matches the mockup; click activation keeps the always-PUT behavior | Requires roving focus and arrow keys (specified in `VOICE_LISTBOX`) | ✅ (locked in round 1) |
| | B. Native radio group (visually hidden radio inside each `voice-card` label row, fieldset legend "Voice") | APG Radio Group pattern (https://www.w3.org/WAI/ARIA/apg/patterns/radio/); Local Canon: UX1, ST1, `SegmentedControl` native radios | Correct single-choice semantics; the browser provides arrow keys and focus; follows the repo's native-radio precedent | An already-checked radio fires no `change`, so re-choosing the selected voice sends no PUT, breaking the frozen `tts-generate.test.ts:350-354` | ❌ (rejected in round 1) |
| | C. Keep buttons, add `aria-pressed` | APG Button pattern (https://www.w3.org/WAI/ARIA/apg/patterns/button/) | Zero E2E churn | Toggle-button semantics describe on/off, not one-of-many (search summary, https://www.digitala11y.com/aria-pressed-state/) | ❌ |
| **OQ-2** How Transcript reuses the queue header | A. Extract `QueueHeaderFrame`; `QueueHeaderRow` wraps it unchanged (`HEADER_FRAME`) | Canon §Queue header row; grouping Session 25 ("its header row *is* MEU-52's component") | One chip, More and processor implementation; Downloader/Convert DOM and tests unchanged | Touches an approved component file | ✅ |
| | B. Widen `QueueHeaderRow` props (optional selection, union toolbar) | Same | No new export | Edits both approved call sites; props lose compile-time shape | ⚠️ |
| | C. Transcript builds its own header | Mockup §02 | No shared-file risk | Duplicates chip/More/processor logic, which the grouping calls the anti-pattern | ❌ |
| **OQ-3** Header rate/ETA chip | A. Include `transcript-rate-chip`, mirroring the Processing card's `formatRateEta` strings | Mockup §02 Zone 2 and §03 note ("a duplicate view, not a replacement") | Completes the mockup; no new computation | One more ID and assertion | ✅ |
| | B. Omit | Canon §Transcript and TR1–TR6 are silent | Smaller surface | Leaves a documented mockup element unbuilt, with only a silence-based basis | ⚠️ |

OQ-1 web research: the search result summary was obtained on 2026-09-28. Direct fetches of `www.w3.org` are blocked by this container's egress proxy (`EGRESS_BLOCKED`), so the APG URLs are cited but were not fetched in this session.

## Research References

- `docs/build-plan/11-page-layout.md` §§Scope, Decision register (TR1–TR6, TT1–TT7), Queue scroll container rule, Queue header row, Transcript, TTS, Supersession, Test-ID migration.
- `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` §§MEU-48 closure, Session 25, "What this grouping deliberately does not do".
- `docs/proposals/2026-09-03-transcript-page-layout-mockup.html` and `docs/proposals/2026-09-03-tts-page-layout-mockup.html` §§02–06.
- `docs/execution/reflections/2026-09-26-p11-queue-pages-reflection.md` §Next Session Design Rules; `docs/execution/plans/2026-09-26-p11-queue-pages/` (peer plan, amendments, reviewer exception).
- `ui/src/renderer/src/components/queue/{QueueCard,QueueCardMenu,QueueList,QueueHeaderRow,QueueToolbar}.tsx`, `components/ui/{ProgressBar,Disclosure,SegmentedControl,StatusChip}.tsx`, `lib/queue/{status-tokens,reorder-single-flight}.ts`.
- `.agent/docs/emerging-standards.md` UX1, UX2, G30–G37, E2.
- WAI-ARIA APG Listbox, Radio Group and Button patterns (URLs above).

## Validation stage contract

The stages bind to PROFILE D6 in POSIX form:

- **static**: typecheck, lint, task-contract.
- **targeted**: per-MEU Vitest files and Electron files, plus shared-component regressions.
- **fresh full**: `WINDOWS_GATE` on Mat's Windows machine, run once on the pushed commit immediately before the implementation review (H1-6). The container `pregate` (H1-2) is an early non-authoritative check and cannot certify the gate.

Each receipt records argv, cwd (repo root), scope, exit code and decisive output. `pregate` prints the input identity first, and `WINDOWS_GATE` records the tested commit, clean-tree state and Node version: `git rev-parse HEAD`, a `git status --porcelain` digest, the `sha256sum` of `ui/package-lock.json`, `node --version`, the resolved Electron version, and whether `ELECTRON_RUN_AS_NODE` is unset. Any change to code, tests, config or lockfile after a gate invalidates it. Both the pre-gate and `WINDOWS_GATE` rerun before the next review dispatch; `windows-gate-check` enforces this by diffing the tested commit against HEAD. Intermediate reuse is disabled.
