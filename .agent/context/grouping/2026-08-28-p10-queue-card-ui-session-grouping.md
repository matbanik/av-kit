# Phase 10 — Queue Card UI · Session Grouping

> **Source:** `docs/proposals/2026-08-27-queue-card-ui-proposal.md` (DRAFT rev 2) + `docs/proposals/2026-08-27-queue-card-ui-mockup.html`
> **Date:** 2026-08-28
> **Origin:** `/create-plan` Step 3 project scoping. Registers Phase 10 and MEU-41–MEU-49.
> **Band:** P2. **Spec home:** `docs/build-plan/10-queue-card-ui.md` (authored by MEU-41).

Phases 0–8 and MEU-1–MEU-39 are `approved`; MEU-40 (`native-region-picker`, Phase 9,
`p9-capture-native-picker`) claimed the next id on 2026-09-01 while this grouping was in plan
review, so Phase 10 starts at **MEU-41** and its sessions start at **20**. Phase 10 is the first
post-Wave-9 phase: it
replaces the bare `<table>` queues in Downloader and Convert with a shared **QueueCard**
row-card system, converges Transcript/TTS onto the same primitives, and reduces the queue
toolbar from 13 buttons to 4 + overflow.

**Capture is explicitly out of scope** — `CaptureInbox` is a thumbnail filmstrip, not a
work queue (proposal §1). It keeps its current presentation.

---

## Sessions (proposed)

| # | Slug | Status | Plan folder | Notes |
|---|---|---|---|---|
| 20 | `p10-queue-card-foundations` | ✅ complete | `docs/execution/plans/2026-08-28-p10-queue-card-foundations/` | MEU-41–44. Canon + tokens, re-queue widening, shared primitives, card/list/empty-state. No page migrated. |
| 21 | `p10-queue-card-migration` | ✅ complete | `docs/execution/plans/2026-09-02-p10-queue-card-migration/` | MEU-45–47. Convert + Downloader migration, toolbar 13→4, multi-select + bulk bar. Exec review `approved`, 0 findings. |
| 22 | `p10-queue-card-dnd` | future | _(not yet created)_ | **Re-scoped 2026-09-03.** MEU-49 only — drag reorder via dnd-kit + ARIA announcements. Phase 10 exit session; runs the phase gate. |

> **Re-scoped 2026-09-03.** Session 22 was `p10-queue-card-convergence` (MEU-48 + MEU-49).
> MEU-48 is now `closed` as superseded by MEU-55 / MEU-56 in
> [Phase 11](2026-09-03-p11-page-layout-session-grouping.md); its two ACs (Transcript
> `ChannelCard` on the shared primitives incl. the G33 `width: %` fix, TTS on the shared
> `ProgressBar`) are inherited there as mandatory ACs. MEU-49's dependency is re-pointed
> MEU-48 → MEU-47, and it now runs **before** Phase 11 so Transcript inherits drag reorder by
> adopting `QueueList` instead of retrofitting it afterwards.

---

## MEUs

| MEU | Slug | Slice | Layer | Depends on |
|---|---|---|---|---|
| MEU-41 | `canon-queue-cards` | Phase 10 spec doc, `06-gui.md` supersession pointers, `--color-age-restricted` + `--color-bg-selected` tokens, `AgeRestricted` Spec-conformance fix | docs + ui/styles | MEU-39 |
| MEU-42 | `svc-requeue-widening` | Widen `reset_failed` from `{Failed}` to the re-queueable set; transition maps; route docstrings; OpenAPI regen | core + api | MEU-41 |
| MEU-43 | `gui-queue-primitives` | `StatusBadge`, `ProgressBar`, `SelectionCheckbox`, `ConfirmModal`, `lib/queue/` (dedup `formatFileSize`, envelope parser, status tokens + contrast oracle, per-feature status configs) | ui | MEU-41 |
| MEU-44 | `gui-queue-card` | `QueueCard`, `QueueList`, `EmptyDropZone`; testid registration | ui | MEU-43 |
| MEU-45 | `gui-convert-queue` | Convert queue migration to `QueueList`; toolbar 13→4 + `⋮` overflow; testid census | ui | MEU-42, MEU-44 |
| MEU-46 | `gui-downloader-queue` | Downloader queue migration; summary bar; duplicate table deleted | ui | MEU-45 |
| MEU-47 | `gui-queue-bulk` | Selection model (`Set<id>`), sticky `BulkActionBar`, shift-click range, Ctrl/Cmd-A, client-side fan-out, Clear finished, G35 partial-result toasts | ui | MEU-46 |
| ~~MEU-48~~ | ~~`gui-queue-convergence`~~ | **Closed 2026-09-03 — superseded by MEU-55 + MEU-56.** ACs inherited, not cancelled. | — | — |
| MEU-49 | `gui-queue-dnd` | dnd-kit drag reorder into `QueueList` + ARIA live-region announcements; keyboard reorder retained as the equal path | ui | MEU-47 |

---

## Dependency graph

```
MEU-39 (p9-capture-gui, approved)
   |
   v
MEU-41 canon-queue-cards ......................... session 20
   |            \
   v             v
MEU-42         MEU-43 gui-queue-primitives
svc-requeue        |
 widening          v
   |            MEU-44 gui-queue-card
   |               |
   +-------+-------+
           v
        MEU-45 gui-convert-queue ................. session 21
           v
        MEU-46 gui-downloader-queue
           v
        MEU-47 gui-queue-bulk
           v
        MEU-49 gui-queue-dnd ..................... session 22 [Phase 10 exit]
           v
        (Phase 11 — see 2026-09-03-p11-page-layout-session-grouping.md)
```

**Critical path:** MEU-41 → MEU-43 → MEU-44 → MEU-45 → MEU-46 → MEU-47 → MEU-49
(MEU-42 is off the critical path but must land before MEU-45, because the Retry primary
action on a card is meaningless until the backend accepts a re-queue from `Cancelled`.)

---

## Why grouped

### Session 20 — `p10-queue-card-foundations` (MEU-41, 42, 43, 44)

Everything in session 20 is **unwired**: it creates the spec, the tokens, the backend
capability, and the presentational components, but does not change a single page. That is
the property that makes it one coherent session — the whole slice can be validated by unit
tests and the existing Playwright waves staying green, with **zero** new E2E waves.

- **MEU-41 first** because the design tokens (`--color-age-restricted`, `--color-bg-selected`)
  and the status→token table are inputs to MEU-43's contrast oracle, and the Phase 10 spec
  doc is the `Spec` source label every downstream AC cites.
- **MEU-42 with them** because it is the only backend work in all of Phase 10. Deferring it
  to session 21 would force a mid-session Python↔TS context switch inside the migration
  session, and the migration's Retry control cannot be honestly specced until the widened
  contract exists. Its blast radius is small and provably additive (see the plan's
  Spec Sufficiency Table: every existing negative assertion uses `Pending` or `Done`,
  neither of which enters the widened set).
- **MEU-43 → MEU-44** are a natural build-up: primitives, then the card that composes them.
  Splitting them across sessions would mean shipping primitives with no consumer, which
  makes their API contract unfalsifiable.

### Session 21 — `p10-queue-card-migration` (MEU-45, 46, 47)

The two queue pages are near-verbatim duplicates (including a duplicated `formatFileSize`),
so migrating them in one session is what actually collapses the duplication; migrating one
and not the other leaves the codebase worse than either end state. Multi-select rides along
because the `Set<id>` selection model touches both migrated pages, and splitting it out
would require a second edit pass over the same two files.

### Session 22 — `p10-queue-card-dnd` (MEU-49) · re-scoped 2026-09-03

Drag reorder is an **enhancement over a working card list**, deferred so that session 21
could be validated as a complete, shippable replacement before new interaction surface was
added. MEU-49 also introduces the phase's only new runtime dependency (dnd-kit), which is
cleaner to isolate.

Convergence (MEU-48) left this session on 2026-09-03: the six page-layout mockups make
Transcript and TTS full page recompositions, so the convergence work is now MEU-55 / MEU-56
in Phase 11. Landing dnd-kit inside `QueueList` **before** Phase 11 means Transcript picks up
drag reorder simply by adopting `QueueList` in MEU-55 — no retrofit pass.

---

## Order of `/create-plan`

1. `2026-08-28-p10-queue-card-foundations` — MEU-41, 42, 43, 44 ✅
2. `2026-09-02-p10-queue-card-migration` — MEU-45, 46, 47 ✅
3. `p10-queue-card-dnd` — MEU-49 (Phase 10 exit)
4. Phase 11 continues in
   [`2026-09-03-p11-page-layout-session-grouping.md`](2026-09-03-p11-page-layout-session-grouping.md)
