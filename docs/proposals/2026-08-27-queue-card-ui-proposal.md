# Proposal: Unified Queue Cards Across av-kit

**Status:** DRAFT rev 2 — awaiting human review. Not an implementation plan; on approval this folds
into `docs/build-plan/06-gui.md` (spec canon) and a `/create-plan` session is run from §10.
Rev 2 (2026-08-27) incorporates external review (Grok 4.6 extra-high): API-mapped Cancel /
Clear-finished semantics, `--color-bg-subtle` collision fix, G31 scope correction, parameterized
(not unified) status configs, E2E testid mapping, client-only bulk fan-out, revised MEU shape.
**Date:** 2026-08-27
**Scope:** Downloader and Convert queues (full migration); Transcript and TTS (convergence onto
shared primitives). **Capture is out of scope** — it is a thumbnail filmstrip, not a work queue.

---

## 1. Summary

Replace av-kit's bare queue tables with a single **QueueCard row-card system** modeled on the
Zorivest Trade Plans card list, plus a coherent control model: per-card state-dependent actions,
checkbox multi-select with a contextual bulk-action bar, a reduced global toolbar, and a
drop-zone-first empty state. One set of shared primitives (`QueueCard`, `StatusBadge`,
`ProgressBar`, `SelectionCheckbox`, `BulkActionBar`, `EmptyDropZone`) serves the two true queues
(Downloader, Convert) fully, with Transcript/TTS converging onto the shared primitives — ending
the current per-page duplication. Capture keeps its filmstrip (§2).

Design goal: Krug's "Don't Make Me Think" — every card self-describes its state, shows only the
actions valid for that state, and borrows conventions users already know from Gmail-style
selection and download-manager rows. `Research-backed` throughout (§11 sources); visual language
is `Local Canon` (Zorivest tokens already shared by av-kit).

**API constraint (hard):** this is a GUI-only proposal. Every card/bulk verb maps to an
*existing* REST call (per-id retry/remove/reorder, queue-level start/pause/resume/cancel).
No new endpoints are in scope — see §4 (Cancel), §7 (Clear finished), §6 (bulk fan-out).

## 2. Current state (evidence)

| Surface | Today | Problems |
|---|---|---|
| Convert queue | `ConvertQueueTable.tsx` — TanStack table, 9 columns | Status is a bare colored `<span>` (no pill shape, no contrast-safe fg); progress is text `%`; no hover state; row click has no keyboard/aria affordance |
| Convert controls | `ConvertPage.tsx:770-916` | 13 buttons (Start → Open folder) in one flat wrapped row, mixed sizes, no grouping, no icons — same pattern on Downloader |
| Download queue | `DownloadQueueTable.tsx` | Near-verbatim duplicate of Convert table (incl. duplicated `formatFileSize`, envelope parsing, status list) — but its status set differs (SABR states) |
| Transcript | `TranscriptPage.tsx:493-552` `ChannelCard` | Already card-shaped, but bespoke — hand-rolled progress bar that animates `width: ${percent}%` (**G33 violation**; must be `transform: scaleX`), ad-hoc status dot |
| TTS | `TTSPage.tsx` | Single-job page + model rows, **not a job queue** — gets the shared `ProgressBar` only, not QueueCard |
| Capture | thumbnail filmstrip | Not a work queue — **out of scope** |
| Shared UI | `components/ui/` | Only `Button` + `SelectInput`. The `DataTable` / `ProgressBar` / `StatusBadge` specced in `06-gui.md:1090-1143` were never built |

No selection model exists anywhere; delete/remove operates only on the single highlighted row.

## 3. Why row-cards, not tables (`Research-backed`)

Queue monitoring is a **scanning** task, not a column-comparison task. Practitioner and design-system
consensus: cards for browsing, lists for scanning, tables for dense comparison. The winning
pattern for job queues is a **vertical list of row-shaped cards with fixed internal zones** —
table-like vertical scanability, card-like freedom for progress bars, pills, and per-row actions.
Precedents: GitHub Actions runs list, browser download shelves, Zorivest Trade Plans.
We keep aligned zones (columns' scanability) inside cards (a table cell can't hold a progress
bar + state-dependent actions cleanly, as the current UI demonstrates).

## 4. QueueCard anatomy (`Local Canon` + `Research-backed`)

Two-row card, fixed zones, 8px vertical gap between cards. Shell borrowed from Zorivest
(`px-4 py-3 rounded-[var(--radius-control)] border transition-colors`):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [☐] [#2] [◉icon]  Title / display_name            [pill]  [primary] [⋮]     │
│           meta: kind · quality · size    ▐████████░░░▌ 42% · 3.2 MB/s · 1:04│
└─────────────────────────────────────────────────────────────────────────────┘
```

| Zone | Content | Rules |
|---|---|---|
| Checkbox | `SelectionCheckbox` (ported from Zorivest, 16px, `stopPropagation`) | Always visible — sibling of the clickable region, never nested |
| Position | `queue_position`, muted, `tabular-nums` | Doubles as the reorder anchor label |
| Status icon | lucide icon, colored per §5 | Left-edge glyph = fastest scan position |
| Title + meta | `display_name` / `title`; second line kind · quality · size | Truncate with ellipsis + `title` attr (G7) |
| Progress | `ProgressBar` + `% · speed · ETA` (tabular-nums) | Only for Processing/Paused; Pending shows "waiting · N ahead"; Done shows size; Failed shows error summary |
| Status pill | `StatusBadge` per §5 | Text label always present — never color alone (WCAG 1.4.1) |
| Primary action | ONE state-dependent icon button, always visible | Failed/Cancelled→Retry ↻ (existing per-id retry), Done→Open file. Processing→Cancel ⏹ **only on the in-flight row**, wired to the existing *queue-level* cancel (`POST /downloads/cancel` / `POST /conversions/cancel`) — there is **no per-item cancel API and none is added** (§12.5). All other states: slot empty; Remove stays in the kebab. Universal icons only, tooltip required |
| Kebab ⋮ | Open file, Open folder, Copy path/URL, Move up/down/top/bottom, Remove (last, red) | Overflow menu only because >2 secondary actions exist |

Card states (Zorivest precedence order, av-kit fills): detail-open `border-accent bg-accent/10` >
checkbox-selected `border-accent/50 bg-accent/5` > default `border-border bg-bg
hover:bg-bg-elevated`. **Do NOT use `bg-bg-subtle` for the selected fill:** av-kit's
`--color-bg-subtle` already exists and is `#6272a4` — the same value as `--color-neutral`
(comment purple), i.e. a text/status color, not a subtle surface. Selection fill therefore uses
an accent tint (above); if a dedicated surface token is wanted, it must be a *new* name (e.g.
`--color-bg-selected`), never a reuse of `bg-subtle`. Card body is `role="button"` with
Enter/Space handling.

Pause is **queue-level only** per `06-gui.md:503-524` — no per-card pause (`Spec`).

## 5. Status system (`Spec` — 06-gui.md:544-567 color contract)

New `StatusBadge` primitive (variant-map style like Zorivest `AccountTypeBadge`), shell
`text-xs px-2 py-0.5 rounded-full`, colors from the existing contract:

| Status | Token | Pill (dark) |
|---|---|---|
| Pending | `--color-neutral` #6272a4 | `bg-neutral/20 text-fg-muted` |
| Processing / Downloading | `--color-accent-cyan` #8be9fd | `bg-accent-cyan/10 text-accent-cyan` |
| Paused (processor) | `--color-accent-yellow` #f1fa8c | `bg-accent-yellow/10 text-accent-yellow` |
| Done | `--color-accent-green` #50fa7b | `bg-accent-green/20 text-accent-green` |
| Failed | `--color-error` #ff5555 | `bg-error/20 text-error` |
| Skipped | `--color-accent-purple` #bd93f9 | `bg-accent-purple/10 text-accent-purple` |
| Cancelled | `--color-border` #44475a | `bg-bg-elevated text-fg-muted` |
| QualityBlocked | `--color-accent-orange` #ffb86c | `bg-accent-orange/10 text-accent-orange` |
| AgeRestricted | new `--color-age-restricted` #c4a882 | `bg-age-restricted/10 text-age-restricted` |

Zorivest measured `/20` purple at 4.08:1 (WCAG AA fail at small sizes) — use `/10` tints for
purple/orange/yellow/cyan as above and verify each pairing ≥4.5:1 in BOTH themes during
implementation (`Local Canon`).

## 6. Selection & bulk actions (`Research-backed`, Zorivest parity)

- **Model:** `Set<id>` selection state; header `SelectionCheckbox` with indeterminate state +
  "N items" count (Zorivest `TradePlanPage.tsx:806-816` pattern); select-all operates on the
  *filtered* list.
- **Shift-click range select** and Ctrl/Cmd-A — de facto desktop standard (Gmail/file managers).
- **BulkActionBar** (port from Zorivest `components/BulkActionBar.tsx`): renders only when
  ≥1 selected, sticky above the list. Contents: accent "N selected" · Retry · Move to top ·
  Move to bottom · Remove (destructive) · spacer · Clear selection. Consensus across Material /
  Carbon / Polaris: contextual bar with count + actions + clear affordance.
- **Bulk execution is client-side fan-out only:** N sequential per-id calls against the
  *existing* endpoints (retry, `DELETE /{id}`, `PUT …/reorder`) — **no `POST …/bulk` endpoint
  exists and none is invented.** Partial results reported per-item: "12 removed, 2 skipped
  (processing)" via status toast (G35).

**Recommendation** on placement: sticky above the list (Zorivest parity) rather than a floating
bottom bar — both are defensible per research; cross-app consistency wins. → Open decision §12.1.

## 7. Global toolbar — 13 buttons → 4 + overflow (`Research-backed`)

| Keep in toolbar | Rationale |
|---|---|
| **Start** (primary) / **Pause** / **Resume** | Queue-level processor verbs — the page's main job. Pause/Resume collapse into one toggle reflecting `processor.state` (UX1 segmented-state rule) |
| **Clear finished** | Frequent, safe housekeeping. **New control, no backing route exists** — implemented as client-side fan-out of the existing `DELETE /{id}` over **Done jobs only** (output files stay on disk), with a G35 partial-result toast. No new REST endpoint (§12.6) |
| ⋮ overflow: **Clear all…** (destructive, confirm dialog) | Rare + destructive → last, separated (NN/g proximity-of-consequential-options) |

Everything else moves: Up/Down/Top/Bottom → kebab + bulk bar + `Alt+↑/↓` shortcuts;
Cancel/Reset/Remove → per-card primary action, kebab, and bulk bar; Open file/folder → per-card.
Toolbar buttons are icon+label (NN/g: labels visible, not hover-only). **G31 scope
(corrected):** G31 bans per-page *accent forks* (e.g. inventing `bg-accent-green` as a Save
color) — it does **not** mean every control is `variant="primary"`. The full G34 5×3 variant
grid stays in play exactly as Convert already uses it (primary / secondary / ghost /
destructive); status colors appear only on non-interactive pills/icons/progress.

**Destructive-action ladder** (`Research-backed`, NN/g): Remove-from-queue → light confirm with
verb-labeled button ("Remove 3 jobs"); Clear all → confirm dialog; queue-level Cancel of a
re-queueable job → no dialog (re-queue is cheap) — undo toast deferred until the API can restore
a removed job (§12.2). G2: destructive controls disabled when inapplicable. **Note:** Convert's
`ConfirmDeleteModal` is a page-local portal, not a shared primitive, and Downloader's Clear All
currently has **no confirm at all** — a shared `ConfirmModal` is **new work** (lands in M1/M2),
not a port.

## 8. Reorder (`Research-backed`)

Phase 1 (baseline, fully accessible): Move up/down/top/bottom in kebab + bulk bar, `Alt+↑/↓`
keyboard shortcuts (qBittorrent precedent), reusing the existing reorder payload builder
(`convert-controls.ts:108-129`). Phase 2: drag handle (6-dot grip, far-left on hover) via
`dnd-kit`, with ARIA live-region announcements — drag is an enhancement, never the only path
(Smashing/React-Aria accessibility consensus). → Open decision §12.3.

## 9. Empty state & drop zone (`Research-backed`)

- Empty queue = **invitation**: large dashed-border drop zone, microcopy ("Drop video or audio
  files here — or"), prominent **Browse…** button as equal alternative. Never drag-only.
- Four drag states: idle / window-drag-enter (whole queue panel highlights as target) /
  direct-hover (intensified) / invalid (rejection reason shown *during* drag).
- Non-empty queue: the whole list stays a drop target with a drag-over overlay + compact
  "Drop files to add" strip, so intake stays discoverable without consuming height.

## 10. Rollout — suggested MEU breakdown (input to `/create-plan`)

This is a **new phase (MEU-41+)**, not a continuation of the completed 39. Seven slices, canon
work first:

| MEU | Deliverable | Validation |
|---|---|---|
| M1 Canon + foundations | `06-gui.md` amendment (DataTable is no longer the queue surface; glyph-prefixed controls → lucide); tokens (**fix the `bg-subtle` collision per §4** — selection fill via accent tint or a *new* `--color-bg-selected`; add `--color-age-restricted`, the only genuinely new color); `StatusBadge`, `ProgressBar`, `SelectionCheckbox`, shared `ConfirmModal`; shared `lib/queue/` = de-duplicated `formatFileSize` + envelope parser + **parameterized per-feature status configs** (Downloader has `Downloading`/`QualityBlocked`/`AgeRestricted`; Convert has `Processing` and no SABR states; Transcript/TTS differ again — a single `JOB_STATUSES` enum is **not** possible). Do **not** block on porting the missing Zorivest reference docs — use the same 4A fallback table prior GUI MEUs used | Unit tests + contrast checks both themes |
| M2 QueueCard/QueueList | Card + list primitives, `EmptyDropZone`; testid plan: `queue-row` stays on the card; new testids registered in `ui/tests/e2e/test-ids.ts` census | Unit + Playwright render wave |
| M3 Converter migration | Replace table + 13-button bar; toolbar §7, per-card actions §4. **Must keep or remap the wired E2E testids (`queue-table`, `queue-row`, `convert-queue-row`, `start-btn`, `convert-start`) and update the census in this same MEU** — otherwise Wave 1/8 fails | E2E happy-path (GUI shipping gate) |
| M4 Downloader migration | Same, incl. summary-bar glyph contract; same testid-census rule | E2E |
| M5 Multi-select + bulk | Selection model, BulkActionBar, shift-click, Ctrl/Cmd-A, **client-side fan-out** over existing per-id endpoints (§6) + G35 toasts | E2E multi-select spec |
| M6 Convergence (shrunk) | Transcript `ChannelCard` onto primitives (**fixes its G33 `width:%` violation**); TTS gets shared `ProgressBar` only; Capture out of scope (filmstrip, not a queue — §2) | E2E regression |
| M7 Drag reorder | dnd-kit + live-region announcements (keyboard/menu path already shipped in M3) | E2E reorder spec |

Each MEU follows FIC → Red → Green; per the GUI shipping gate every MEU ships route assertion,
testid registration, and `npm run build && npx playwright test <target>` evidence.
Virtualize with `@tanstack/react-virtual` only if a list exceeds ~200 items (`Spec` 06-gui.md).

## 11. Standards compliance & conflicts

**Complies with:** G1, G2, G7, G31 (single accent on interactive elements), G32 (tokens only,
zero raw hex), G33 (progress bar animates `transform: scaleX`, never `width`), G34 (all buttons
from the 5×3 variant grid), G35 (feedback tiers for every mutation), G30 (selects unchanged),
E2/G36/G37 (E2E per interactive change, no test guards).

**Conflicts to resolve at approval (flagged, not silently resolved):**
1. `06-gui.md:1090-1143` specs a sortable/resizable **DataTable** for queues → this proposal
   supersedes it with QueueList row-cards for queue surfaces. Requires a spec amendment.
2. `06-gui.md:526-542` queue-controls table prefixes labels with text glyphs (▶ ⏸ 🗑) → replaced
   by lucide icons + text labels. Requires the same amendment.
3. `docs/BUILD_PLAN.md` marks all 9 phases complete → this work is a new phase/session, not a
   continuation.
4. Emerging-standards G32–G35 cite reference docs that exist only in the Zorivest repo
   (`gui-element-reference.md`, `gui-button-index.md`) — do **not** block M1 on porting them;
   use the same 4A fallback table prior GUI MEUs used, and port/link the docs as a follow-up.
5. `--color-bg-subtle` name collision (§4): the token exists and equals `--color-neutral`
   (#6272a4) — any "subtle surface" usage must pick a new name or an accent tint.

## 12. Open decisions (recommendation first)

1. **Bulk bar placement** — Recommended: sticky above list (Zorivest parity). Alternative:
   floating bottom bar (Linear-style).
2. **Remove semantics** — Recommended: light confirm now; switch to undo-toast when/if the API
   supports restoring a removed job.
3. **Drag-and-drop timing** — Recommended: defer to M7 (keyboard/menu reorder ships first).
4. **Density toggle** — Recommended: skip (single density; avoid zombie features).
5. **Per-card Cancel semantics** — Recommended: per-card Cancel = the *queue-level* cancel,
   shown only when that row is the in-flight item; every other row's primary slot is empty and
   Remove stays in the kebab. **No new per-item cancel API in this GUI session.** Alternative
   (out of scope unless explicitly requested): add `POST /{queue}/{id}/cancel` with a Boundary
   Inventory row — a processor-state-machine change, not a GUI change.
6. **Clear-finished semantics** — Recommended: client-side fan-out of `DELETE /{id}` over
   **Done** jobs only (output files stay on disk), G35 partial-result toast, no new REST.
   Alternative: also sweep Cancelled/Skipped — a product decision that needs an explicit lock.

All six require an explicit `USER_EXPLICIT` lock before `/create-plan` so they become
`Human-approved` ACs rather than agent assumptions.

## 13. Sources (research digest)

Primary: Carbon data-table batch actions; Polaris index-table bulk actions; Material selection /
contextual app bar; PatternFly overflow-menu; NN/g icon-usability, confirmation-dialog,
proximity-of-consequential-options, contextual-menus; React Spectrum accessible DnD.
Practitioner syntheses (2024–2026): Smart Interface Design Patterns (cards vs lists vs tables;
drag-and-drop UX), LogRocket async-workflow UI patterns, Eleken bulk-actions / progress /
file-upload, Pencil & Paper DnD, uxpatterns.dev list-vs-table guide, Smashing "Dragon Drop".
Observational: qBittorrent, JDownloader, GitHub Actions runs list, Handbrake/Resolve render
queues, browser download shelves.
