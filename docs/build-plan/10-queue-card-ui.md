# Phase 10 — Queue Card UI

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: Phase 6 (Electron chrome, pages), Phase 8 (Convert queue), Phase 9 (Capture) | Outputs: shared queue primitives, `QueueCard` / `QueueList`, re-queue widening, migrated Convert + Downloader queues
> **Spec date:** 2026-09-02. **Does not reopen** MEU-1–40 as incomplete. This phase replaces the bare `<table>` queue surfaces with one row-card system and folds [2026-08-27-queue-card-ui-proposal.md](../proposals/2026-08-27-queue-card-ui-proposal.md) + its [mockup](../proposals/2026-08-27-queue-card-ui-mockup.html) into spec canon.

> **Page layout supersession:** [Phase 11 page layout canon](11-page-layout.md) governs composition around the queues in MEU-52–58; Phase 10 QueueCard, QueueList, ProgressBar, and MEU-49 scroll/reorder contracts remain binding.

| Source | Decision |
|--------|----------|
| Spec | This file; [BUILD_PLAN.md](../BUILD_PLAN.md) Phase 10 row; the queue-card proposal §1–§13 |
| Local Canon | Status colour contract and queue-control inventory ([06-gui.md](06-gui.md), superseded for queue surfaces below); `{ items, processor }` queue envelopes ([04-rest-api.md](04-rest-api.md)); Convert queue page ([08-video-conversion.md](08-video-conversion.md)); `gui-actions-index.md` action ids |
| Research-backed | NN/g destructive-action ladder and proximity-of-consequential-options; Material / Carbon / Polaris contextual bulk bar consensus; qBittorrent keyboard reorder precedent; React-Aria / Smashing "drag is an enhancement, never the only path"; WCAG 2.2 SC 1.4.1, 1.4.3, 1.4.11, 4.1.2 |
| Human-approved | 2026-08-28 USER_EXPLICIT locks, recorded verbatim in [§User locks](#user-locks) |

---

## Scope and non-goals

Phase 10 gives every work queue in av-kit one presentation: a row-card list built from shared
primitives, with a single primary action per card, an overflow kebab, and a selection model that
drives a bulk bar. It changes **presentation and one service contract** (re-queue widening); it
adds no new REST surface.

**In scope**

| Slice | MEU | Delivers |
|---|---|---|
| Canon + tokens | MEU-41 | This document, the supersession pointers, the four ported status tokens, the `AgeRestricted` pill fix |
| Re-queue widening | MEU-42 | `reset_failed` accepts the full re-queueable set; blocker reason invariant |
| Shared primitives | MEU-43 | `StatusBadge`, `ProgressBar`, `SelectionCheckbox`, `ConfirmModal`, `lib/queue/` |
| Card + list | MEU-44 | `QueueCard`, `QueueList`, `EmptyDropZone` |
| Convert migration | MEU-45 | Convert queue on `QueueList`; toolbar reduction |
| Downloader migration | MEU-46 | Downloader queue on `QueueList`; summary bar |
| Selection + bulk | MEU-47 | `Set<id>` selection, sticky `BulkActionBar`, Clear finished |
| Convergence | MEU-48 | Transcript `ChannelCard` and TTS onto the shared primitives |
| Drag reorder | MEU-49 | `dnd-kit` drag with ARIA live-region announcements |

**Out of scope (non-goals)** — each of these is either a later MEU or explicitly refused:

| Non-goal | Why |
|---|---|
| Capture inbox | It is a thumbnail filmstrip, not a work queue; it keeps its own presentation |
| New REST endpoints or bulk endpoints | Every Phase 10 action maps onto a route that already exists |
| Per-item cancel or per-item pause API | The processor is queue-scoped; see [§Re-queue contract](#re-queue-contract) |
| Page migration | Deferred to MEU-45 (convert) and MEU-46 (downloader); MEU-43/44 mount nothing |
| Selection model / BulkActionBar | Deferred to MEU-47 |
| dnd-kit drag reorder | Deferred to MEU-49 |
| Undo-toast for Remove | Deferred until the API can restore a removed job |
| List virtualization | No new dependency this phase; revisit above 200 rows |

### User locks

Recorded from the 2026-08-28 USER_EXPLICIT planning session. These are spec, not preference.

| Lock | Decision |
|---|---|
| Bulk bar placement | The bulk bar is **sticky above the list** (Zorivest parity), never a floating bottom bar |
| Remove confirm | A light **verb-labeled confirm** modal ("Remove 3 jobs"); the undo-toast alternative is **deferred** until the API can restore a removed job |
| Drag and drop | Pointer **drag reorder is deferred to MEU-49**; keyboard and kebab reorder ship first and remain the equal path |
| Density toggle | None — **single density** for every queue surface |
| Per-card Cancel | Rendered only on the in-flight row, accessible name `Cancel queue`, wired to the queue-level `POST /{queue}/cancel`; there is **no per-item cancel** API and none is invented |
| Clear finished | Client fan-out of `DELETE /{id}` over Done jobs only; see the clause table below |
| Retry scope | Retry widens the re-queueable set to `Cancelled`, `QualityBlocked` and `AgeRestricted`; `Skipped` stays **excluded** |
| Pill palette | Colour comes only from av-kit's [status token table](#status-token-table); a pill authors no hue outside it |

**Clear finished — every clause is normative:**

| Clause | Rule |
|---|---|
| Snapshot | The Done id set is snapshotted once before the first request; jobs that finish mid-run are not swept |
| Independence | One `DELETE /{id}` per snapshotted id, and each request is independent of the others |
| Continue on failure | A failed or `404` response must **never abort** the fan-out; every snapshotted id is attempted exactly once |
| Successes kept | Confirmed deletions are **never rolled back** |
| Files | Media **files stay on disk** — the API removes the queue record only |
| Reconcile | **Exactly one list refetch** after the fan-out settles; the refetch, not local optimistic state, is what the list renders |
| Report | The G35 partial-result toast states the **removed count**, the failed-or-skipped count, and a **reason per failure** |

---

## QueueCard anatomy

One card per job. Zones render left to right in exactly this order:

| # | Zone | Contents |
|---|---|---|
| 1 | `checkbox` | `SelectionCheckbox`; sibling of the open-region, never inside it |
| 2 | `position` | 1-based queue position, tabular numerals |
| 3 | `status-icon` | Status hue glyph, `aria-hidden="true"` — decorative, duplicates the pill text |
| 4 | `title-meta` | Job title plus the meta line (size, quality, duration, blocker reason + remediation) |
| 5 | `progress` | `ProgressBar`, `transform: scaleX` only — never an animated `width` |
| 6 | `status-pill` | `StatusBadge` from the [status token table](#status-token-table) |
| 7 | `primary-action` | At most **one** action; see [§Primary action model](#primary-action-model) |
| 8 | `kebab` | Overflow trigger; see [§Kebab menu](#kebab-menu) |

**Nested-interactive rule.** The card's `role="button"` open-region contains **no** interactive
descendant. The three interactive zones — `selection-checkbox`, `primary-action`,
`kebab-trigger` — render as siblings of that region inside the card container, and activating any
of them never invokes `onOpen`. Nesting them would bubble a Retry into an open, and would strip
the descendants of independent name/role/value (axe `nested-interactive`, WCAG 2.2 SC 4.1.2).

**Blocker copy.** A card in `QualityBlocked` or `AgeRestricted` renders, in its meta zone, both
the blocker reason (`error_message`) and the remediation — the setting the user has to change:

| Status | Remediation shown on the card |
|---|---|
| `QualityBlocked` | Settings > Downloader > Quality (choose a lower quality, or a supported audio format for audio-only jobs) |
| `AgeRestricted` | Settings > Cookies & Authentication (sign-in required for this video) |

Blocker reason strings are quality-independent and acronym-free: they interpolate no job field,
so a stored reason can never contradict the row it sits on.

---

## Status token table

Every pill hue is an av-kit token in `ui/src/renderer/src/styles.css`. av-kit owns these values;
they follow Zorivest's `globals.css` at commit `1f254832` (seeded at `61243baf`; the light hexes were
re-ported on 2026-10-26), which av-kit keeps as
`_inspiration/zorivest/globals.css` (see its `PROVENANCE.md`). The Zorivest checkout is never read,
and a later Zorivest change reaches av-kit only as an av-kit change. A pill that introduces a colour
outside this table is a defect. Fill and label are deliberately different tokens: the fill
is the status hue at 10%, the label is `text-fg`, which clears the 4.5:1 contrast minimum on all
80 theme × backdrop pairings (worst 6.61). `/20` on an accent hue remains forbidden.

| Status | Token | Fill class | Label class | Icon class |
|---|---|---|---|---|
| `Pending` | `--color-status-pending` | `bg-status-pending/10` | `text-fg` | `text-status-pending` |
| `Processing` | `--color-accent-cyan` | `bg-accent-cyan/10` | `text-fg` | `text-accent-cyan` |
| `Downloading` | `--color-accent-cyan` | `bg-accent-cyan/10` | `text-fg` | `text-accent-cyan` |
| `Paused` | `--color-accent-yellow` | `bg-accent-yellow/10` | `text-fg` | `text-accent-yellow` |
| `Done` | `--color-status-filled` | `bg-status-filled/10` | `text-fg` | `text-status-filled` |
| `Failed` | `--color-status-rejected` | `bg-status-rejected/10` | `text-fg` | `text-status-rejected` |
| `Skipped` | `--color-accent-purple` | `bg-accent-purple/10` | `text-fg` | `text-accent-purple` |
| `Cancelled` | `--color-status-canceled` | `bg-status-canceled/10` | `text-fg` | `text-status-canceled` |
| `QualityBlocked` | `--color-accent-orange` | `bg-accent-orange/10` | `text-fg` | `text-accent-orange` |
| `AgeRestricted` | `--color-accent-red` | `bg-accent-red/10` | `text-fg` | `text-accent-red` |

**Ported tokens** — MEU-41 adds these four declarations to *both* theme blocks of
`ui/src/renderer/src/styles.css`, hexes copied byte-for-byte:

| Token | Dark | Light |
|---|---|---|
| `--color-status-pending` | `#ffb86c` | `#9a3412` |
| `--color-status-filled` | `#50fa7b` | `#166534` |
| `--color-status-rejected` | `#ff5555` | `#991b1b` |
| `--color-status-canceled` | `#6272a4` | `#64748b` |

Status is never colour-alone: the pill states it in words (SC 1.4.1), and the left-edge status
icon is `aria-hidden` and therefore decorative, not contrast-gated (SC 1.4.11).

---

## Card state precedence

Exactly one state class set applies per card, evaluated top-down:

| Precedence | State | Classes |
|---|---|---|
| 1 | `detail-open` | `border-accent bg-accent/10` |
| 2 | `checkbox-selected` | `border-accent/50 bg-accent/5` |
| 3 | `default` | `border-border bg-bg hover:bg-bg-elevated` |

**Selection fill.** The only permitted selection fills are `bg-accent/5` and `bg-accent/10`.
Reusing `bg-bg-subtle` for a selected or active state is forbidden: `--color-bg-subtle` inverts
between themes (`#6272a4` dark vs `#d1d5db` light), so the same class reads as a dark highlight in
one theme and a light one in the other. This is the single disclosed divergence from Zorivest's own
card list, which uses `bg-bg-subtle` for its checkbox-selected step; it is a class choice, not a
hue, so no colour value is av-kit-authored either way. No `--color-bg-selected` token is created.

---

## Primary action model

**At most one primary action per card**, chosen by the job's status:

| Condition | Primary action |
|---|---|
| Status is re-queueable | Retry |
| Status is `Done` | Open file |
| The job is the in-flight item | Cancel |
| Otherwise | None rendered |

**Cancel scope disclosure.** The control sits on the in-flight row, but the endpoint is
queue-level `POST /{queue}/cancel`. Its accessible name is therefore `Cancel queue` and its title
is `Cancel queue - this is the in-flight item`. The strings `Cancel`, `Cancel item`,
`Cancel download` and `Stop` are forbidden as the accessible name: a row-local control reading
"Cancel" lets a person stop the whole queue believing they stopped one item.

**No confirmation on Cancel.** Queue-level Cancel takes no dialog — re-queue is cheap, and the
disclosure lives in the label and title. `ConfirmModal` is reserved for Remove and Clear all.

**Destructive-action ladder:** Remove-from-queue takes a light verb-labeled confirm; Clear all
takes a confirm dialog; Cancel takes none. Confirms are portal modals — never `window.confirm`.

---

## Kebab menu

`KEBAB_MENU_ORDER` fixes the **relative order** of the actions that are both supplied as callbacks
and applicable; it is not a membership requirement. An action is omitted entirely — never rendered
disabled, never a no-op — when its callback is absent or when availability excludes it. Availability
is evaluated **per action**, never per group: a first-but-not-last row still offers Move down and
Move to bottom, and only a single-item queue drops all four move actions.

| Order | Action id | Label | Available when |
|---|---|---|---|
| 1 | `open-file` | Open file | Status is `Done` and the job has an output path on disk |
| 2 | `open-folder` | Open folder | Status is `Done` and the job has an output path on disk |
| 3 | `copy-location` | Copy path / Copy URL | Always |
| 4 | `move-up` | Move up | The row is not first in the list |
| 5 | `move-down` | Move down | The row is not last in the list |
| 6 | `move-top` | Move to top | The row is not first in the list |
| 7 | `move-bottom` | Move to bottom | The row is not last in the list |
| 8 | `remove` | Remove | Always |

`copy-location` carries a state-dependent label: **Copy path** once an output path exists, **Copy
URL** before then — the visible label must name what actually lands on the clipboard.

---

## Selection and bulk model

- Selection state is a `Set<id>`; the header `SelectionCheckbox` carries an indeterminate state and
  an "N items" count, and select-all operates on the **filtered** list.
- Shift-click range select and Ctrl/Cmd-A are supported.
- The `BulkActionBar` renders only when at least one row is selected and is **sticky above the
  list**: accent "N selected" · Retry · Move to top · Move to bottom · Remove (destructive) ·
  spacer · Clear selection.
- **Bulk execution is client-side fan-out only.** N sequential per-id calls against the endpoints
  that already exist (reset, `DELETE /{id}`, `PUT …/reorder`). There is **no bulk endpoint** —
  `POST /{queue}/bulk` does not exist and may not be invented.
- Partial results are reported per item through a G35 status toast, on the Clear-finished clause
  table in [§Scope and non-goals](#scope-and-non-goals).

---

## Toolbar reduction

The global queue toolbar drops from 13 buttons to 4 plus an overflow:

| Kept | Rationale |
|---|---|
| Start (primary) / Pause / Resume | Queue-level processor verbs; Pause and Resume collapse into one toggle reflecting `processor.state` |
| Clear finished | Frequent, safe housekeeping; client fan-out of `DELETE /{id}` over Done jobs only |
| ⋮ overflow: Clear all… | Rare and destructive, so last and separated |

Everything else moves onto the card: Up/Down/Top/Bottom to the kebab, bulk bar and `Alt+↑/↓`;
Cancel/Reset/Remove to the primary action, kebab and bulk bar; Open file/folder to the kebab.
Toolbar buttons are icon **plus** label — never hover-only. The G34 5×3 variant grid stays in play
unchanged; status colours appear only on non-interactive pills, icons and progress bars.

---

## Reorder model

**Baseline (MEU-45), fully accessible:** Move up / down / top / bottom in the kebab and the bulk
bar, plus `Alt+↑/↓` keyboard shortcuts, reusing the existing reorder payload builder.

**Enhancement (MEU-49):** a 6-dot drag handle at the far left on hover, via `dnd-kit`, with
ARIA live-region announcements. Drag is an enhancement layered on the keyboard path, never the
only path to reorder.

---

## Empty state and drop targets

An empty queue is an **invitation**, not a blank slate: a large dashed-border drop zone, the
microcopy "Drop video or audio files here — or", and a prominent **Browse…** button as an equal
alternative. The surface is never drag-only.

| Drag state | Presentation |
|---|---|
| `idle` | Dashed border at rest |
| `window-drag` | The whole queue panel highlights as a target |
| `direct-hover` | The target intensifies |
| `invalid` | The rejection reason is shown *during* the drag, not after the drop |

A non-empty queue stays a drop target: the list shows a drag-over overlay plus a compact "Drop
files to add" strip, so intake stays discoverable without consuming height.

---

## Re-queue contract

**Re-queueable download statuses:** `Failed`, `Cancelled`, `QualityBlocked`, `AgeRestricted`.
Not re-queueable: `Pending`, `Downloading`, `Done`, `Skipped`.

**Conversion re-queueable statuses:** `Failed`, `Cancelled`. Not re-queueable: `Pending`,
`Processing`, `Done`, `Skipped`. The two sets plus their complements must exhaust the respective
status enums, so no status is silently uncovered.

A re-queue resets `status` to `Pending`, clears `error_message`, and sets `progress` to `0.0`.
An unknown id answers `404`; a non-re-queueable status answers `409`.

**Blocker re-queue is not a generic reset.** `QualityBlocked` → `Pending` must first apply the
current downloader defaults to the job (quality, audio format, audio-only) and then re-evaluate
compatibility against the live SABR snapshot; if the job is still incompatible while SABR mode is
Active, the job stays `QualityBlocked` and the route answers `409` naming the remediation.
Otherwise Retry would defeat the very quality guard that created the block. `AgeRestricted` →
`Pending` is unconditional, because cookie and authentication options are read at execution time.
`Cancelled` and `Failed` → `Pending` stay unconditional.

**Blocker reason invariant.** Every job persisted in a blocker state carries a non-empty
`error_message`, and no job persisted out of a blocker state retains a blocker reason. This is
enforced at the persistence boundary (repository `add` / `save`), backfilled once by an idempotent
migration for rows blocked before this phase, and re-asserted on the refused-Retry path.

**Pause scope.** Pause and Resume are **queue-level only**; there is **no per-item pause** control
and no per-item pause API.

**Error surface.** `422` / `409` / `ApiError` responses are shown in-page (G15) and never
swallowed. Queue envelopes are parsed with a strict wrapper schema: an unknown top-level key fails
the parse and surfaces as an error rather than being ignored.

---

## Supersession of 06-gui.md

Two blocks of [06-gui.md](06-gui.md) are superseded **for queue surfaces only**. Neither block is
deleted — each carries a pointer to this document, so the conflict stays visible in canon:

| 06-gui.md block | Superseded by |
|---|---|
| §Shared Components → `### DataTable` (TanStack table wrapper, virtual scrolling, resizable columns) | [§QueueCard anatomy](#queuecard-anatomy) — queues render row-cards, not tables |
| §Downloader Page → `### Queue Controls` (13 text-glyph buttons) | [§Toolbar reduction](#toolbar-reduction) and [§Kebab menu](#kebab-menu) |

Two further 06-gui.md wordings are superseded by the pill palette lock: the "AgeRestricted Brown"
colour, and every `--color-pill-*-fg` token an earlier round invented. `AgeRestricted` takes the
shared `--color-accent-red`; no `--color-age-restricted` token is created.

Sections of 06-gui.md that are **not** superseded — page shells, routing, discovery and IPC, API
wiring, Settings, and the Transcript and TTS page specs — remain authoritative.

---

<a id="queue-pause-feedback-residual"></a>

## Queue pause feedback (residual)

> **MEU-155.** Registered 2026-11-17 from `QUEUE-PAUSE-NO-FEEDBACK`. Pause is queue-level and takes effect between jobs (§Toolbar reduction), so a click during a long Convert or Downloader job looked like nothing happened. Mat's ruling (2026-11-16): "Say what it does".

| Rule | Contract | Source |
|------|----------|--------|
| Label | The toolbar toggle reads `Pause after this job` on the Convert and Downloader pages; `Resume` is unchanged | Human-approved 2026-11-16 ("Say what it does") |
| Pending | After a pause request succeeds while a job runs, the toggle reads `Pausing…` and is disabled until the queue reports `Paused` or `Idle`, or a different job starts; a job that fails still ends `Paused`. The toggle keeps one width in every state, so Clear finished does not move. The palette's pause shares the same request and sends no second one | Human-approved 2026-11-16; Session 88 D-1091, D-1092 |
| Status | While pending, the processor status reads `Queue stops when the current job ends` in place of the processor label | Human-approved 2026-11-16 |
| Cancel | Cancel stays enabled and stops the running job at once; it also ends the pending state | Human-approved 2026-11-16 |
| Between jobs | The Convert and Downloader services keep pausing between jobs; no API route, OpenAPI document or MCP tool changes | Human-approved 2026-11-16; §Toolbar reduction (queue-level only, no per-item pause) |
| Transcript | The Transcript page keeps its own toolbar and its `Pause` label; its waits between videos, between batches and before a retry end within a second of a pause or stop | Session 88 D-1090; 11 TR1, TR2; 03 §Rate cap |
| Tests | Electron E2E: the label, `Pausing…` while a real Convert job runs, the queue paused after that job, Cancel during `Pausing…`, the Downloader pending state and Clear finished staying put; pytest: Transcript's waits end on pause or stop | Mat, 2026-11-16 ("This should be done with framework and scripts!") |

> **Delivered (Session 88).**
> - The toggle reads `Pause after this job` (`ui/src/renderer/src/components/queue/QueueToolbar.tsx:51`). While a requested pause waits for the running job it reads `Pausing…` (`:59`, `:229`) and is disabled (`:219`), and it keeps `min-w-[12rem] justify-center` in every state (`:62`). Under amendment A1 (D-1098, Mat's ruling) the toolbar's root carries `ml-auto` (`TOOLBAR_END`, `:203`), so it sits at the right end of the header and Clear finished keeps its x whatever the status text says; when space runs out it drops to the next line at the right edge. The slot fixture's toggle class and label, and the toolbar root's class, changed to match (D-1095, D-1098). AC-155.1, AC-155.2, AC-155.9, AC-155.15.
> - `ui/src/renderer/src/lib/queue/pause-request.ts` keeps one pause mark per queue in the shared query cache, never collected, and decides when it is pending (`PAUSE_MARK`, `PAUSE_PENDING_RULE`, `PAUSE_PENDING_HOOK`; D-1091, D-1097). After the pause POST each command module reads the list and marks the job running then; Start, Resume and Cancel clear the mark (`features/converter/convert-commands.ts:166`, `:258-291`; `features/downloader/download-commands.ts:136`, `:183-216`). A failed read sets no mark, and a mark set between jobs binds to the next job within 15 s. AC-155.3 to AC-155.6, AC-155.14, AC-155.19, AC-155.22.
> - While a pause is pending the processor status reads `Queue stops when the current job ends`, and the palette's pause is disabled, so it sends no second request (`features/converter/ConvertPage.tsx:243`, `:562`, `:872`; `features/downloader/DownloaderPage.tsx:259`, `:545`, `:843`; D-1092). The Downloader help says what Pause and Cancel do (`features/downloader/downloader-help-content.ts:27`, D-1093). AC-155.7, AC-155.8, AC-155.13, AC-155.20, AC-155.21.
> - Transcript keeps its own toolbar and its `Pause` label (D-1090 C). Its delay, batch-rest and retry waits now end within a second of a pause or stop (`packages/core/src/avkit_core/services/transcript.py:108-110`, `:282`; 03 §Waits end on pause or stop). AC-155.13, AC-155.16 to AC-155.18.
> - Electron E2E on the real backend (`ui/tests/e2e/queue-pause-feedback.test.ts`): `Pausing…` while a real Convert job runs, the queue `Paused` after it with job 2 waiting, Cancel during `Pausing…`, the Downloader pending state at 700 × 650, and Clear finished staying put. AC-155.10 to AC-155.12, AC-155.15.
> - Out of scope: Cancel while Paused changes nothing (`QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT`, registered open). AC-155.1 to AC-155.22. Plan `docs/execution/plans/2026-11-17-queue-pause-feedback/`.

<a id="queue-cancel-paused-residual"></a>

## Cancel while paused (residual)

> **MEU-156.** Registered 2026-11-17 from `QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT` (triage D-1100). While a Convert or Downloader queue is Paused no job runs, so `cancel_processing` only sets a flag that nothing reads (`services/conversion.py:277-278`, `services/download.py:456-460`) and the queue stays Paused until the next Start. Both pages still enable Cancel then (`controlEnabled` `'cancel'` in `features/converter/convert-controls.ts` and `features/downloader/download-controls.ts`). Mat's ruling (2026-11-17): disable Cancel while Paused.

| Rule | Contract | Source |
|------|----------|--------|
| Paused | While the processor reports `Paused`, Cancel is disabled on the Convert and Downloader pages, and the palette's cancel follows the same rule | Human-approved 2026-11-17 (D-1100) |
| Running | Cancel stays enabled while a job runs, `Pausing…` included ([§Queue pause feedback](#queue-pause-feedback-residual)) | Human-approved 2026-11-16 |
| Services | No service, API route, OpenAPI document or MCP tool changes; cancel keeps its meaning | Human-approved 2026-11-17 (D-1100) |
| Transcript | Whether the Transcript page's Stop has the same gap is checked at plan time with its evidence | Local Canon |
| Tests | Unit: the cancel rule for Processing, Paused and Idle on both pages; Electron E2E on the real backend: Cancel disabled on a Paused queue and enabled again once a job runs | Mat, 2026-11-16 ("This should be done with framework and scripts!") |

> **Delivered (Session 89).**
> - Cancel is enabled only while a job runs: `controlEnabled` `'cancel'` is true at `Processing` and false at `Paused` and `Idle` (`features/converter/convert-controls.ts:87`, `features/downloader/download-controls.ts:78`, `CANCEL_WHEN_RUNNING`). The palette lists no cancel while Paused, and `cancelConversion` and `cancelDownload` send no request then (`features/converter/convert-commands.ts:285`, `features/downloader/download-commands.ts:210`). AC-156.1 to AC-156.4.
> - A cancel confirm request opens no confirm while no job runs, and an open cancel confirm closes once the queue is Paused or Idle; a confirm of another kind stays open (`features/converter/ConvertPage.tsx:247-250`, `:271-272`, `:281-285`; `features/downloader/DownloaderPage.tsx:261-264`, `:311-312`, `:321-325`; `CONFIRM_CANCEL_GATE`, `CONFIRM_CANCEL_CLOSE`). AC-156.5 to AC-156.10.
> - No service, API route, OpenAPI document or MCP tool changed; cancel keeps its meaning (D-1100). Transcript's Stop already acts while Paused, because `stop_processing` applies the stop at once when no worker runs (`packages/core/src/avkit_core/services/transcript.py:275`, `_apply_stop` `:739`), so the Transcript page is unchanged (D-1107).
> - Electron E2E on the real backend (`ui/tests/e2e/queue-cancel-paused.test.ts`): Convert with two re-encode jobs offers Cancel while job 1 runs, not while Paused, and again once job 2 runs; the Downloader palette lists Cancel downloads while Processing, not while Paused, and again after Resume. AC-156.11, AC-156.12. The two named pins read `false` (`ui/tests/unit/convert-page.test.ts:429`, `ui/tests/unit/downloader-page.test.ts:293`, AC-156.13).
> - AC-156.1 to AC-156.13. Plan `docs/execution/plans/2026-11-17-queue-convert-fixes/`.
