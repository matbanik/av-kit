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
they were seeded verbatim from Zorivest's `globals.css` at commit `61243baf`, which av-kit keeps as
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
| `--color-status-pending` | `#ffb86c` | `#ea580c` |
| `--color-status-filled` | `#50fa7b` | `#16a34a` |
| `--color-status-rejected` | `#ff5555` | `#dc2626` |
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
