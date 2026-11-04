---
project: "2026-09-02-p10-queue-card-migration"
date: "2026-09-02"
source: "docs/build-plan/10-queue-card-ui.md"
meus: ["MEU-45", "MEU-46", "MEU-47"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 10 Queue Card Migration (MEU-45 / 46 / 47)

> **Project**: `2026-09-02-p10-queue-card-migration`
> **Build Plan Section(s)**: [10-queue-card-ui.md](../../../build-plan/10-queue-card-ui.md) §Toolbar reduction (10.5), §Primary action model (10.6), §Selection and bulk model (10.7)
> **Status**: `draft`

> **Named sets**: every set, threshold, label and policy in this plan is defined once in
> [`named-sets.json`](named-sets.json) and referenced by NAME. A literal repeated in two places is a defect.

---

## Goal

Session 20 (`p10-queue-card-foundations`, MEU-41–44) built the Phase 10 queue surface — design
tokens, `StatusBadge`, `ProgressBar`, `QueueCard`, `QueueCardMenu`, `QueueList`, `ConfirmModal`,
`EmptyDropZone` — and deliberately mounted **none** of it. A plan-local gate
(`RETIRED_GATE_SCRIPT`) actively *failed the build* if any page imported the new components, so the
foundations could not be half-wired. The user's visible complaint after that session — "why are the
buttons and styles not changed as per the plan yet?" — is the correct observation: nothing is
mounted yet.

This project mounts it. It replaces the two near-verbatim `@tanstack/react-table` queue tables with
the shared card list, collapses the 13-button toolbars to `TOOLBAR_CONTROLS`, moves every retired
control to the new home named in `RETIRED_TOOLBAR_CONTROLS`, and adds the selection + sticky bulk
bar model. It also inverts `RETIRED_GATE_SCRIPT` into `MOUNT_GATE_SCRIPT`, so the gate that used to
prove "nothing is mounted" now proves "everything is mounted and no capability was lost".

Four defects in already-shipped code are corrected here because migration is the moment they become
user-visible:

1. `QueueCard.resolveMeta` emits no quality / speed / ETA, so a naive migration would silently drop
   three columns from each table (`META_SEGMENTS_CONTRACT`).
2. `QueueCard` renders `role="button" tabIndex={0}` on the title region unconditionally, producing a
   focusable control that does nothing when no `onOpen` handler is supplied (`DEAD_REGION_RULE`).
3. Both `controlEnabled('reset')` implementations still gate Retry on `Failed` only, ignoring the
   `DOWNLOAD_REQUEUEABLE_STATUSES` widening that MEU-42 landed in the domain and the API. (The converter's
   correct set is the narrower `CONVERT_REQUEUEABLE_STATUSES` — the two must not be conflated.)
4. `QueueList` renders a bare `<div>` when `items` is empty (`QueueList.tsx:77-104`), so mounting it as-is
   would replace both tables' empty-state rows with a blank panel and leave the MEU-44 `EmptyDropZone`
   unmounted (`EMPTY_STATE_CONTRACT`).

> **Round 1 plan-review correction record.** The reviewer returned `changes_required` with 10 findings.
> Two were factual errors in the plan's reading of the codebase: both `*-commands.ts` modules already
> exist as live command-palette owners (`COMMAND_MODULE_PRESERVED_EXPORTS`), and the reorder endpoints
> take a `{ job_ids }` permutation, not `{ id, direction }` (`REORDER_WIRE_CONTRACT`). Both were verified
> against the files before correcting.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: [graphify, graphify-research, headroom]
  decision: not_applicable
  eligibility_basis: "Scope is a bounded UI migration across ~14 files in one package (ui/). No cross-repo graph, no research corpus, no oversized payload. The relevant sources (Phase 10 spec, the foundations plan + named-sets, two page components, two table components, two E2E suites) were read directly and fit in context."
  human_message_reference: null
```

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-45` | `.agent/context/handoffs/2026-09-02-p10-queue-card-migration-MEU-45-handoff.md` |
| `MEU-46` | `.agent/context/handoffs/2026-09-02-p10-queue-card-migration-MEU-46-handoff.md` |
| `MEU-47` | `.agent/context/handoffs/2026-09-02-p10-queue-card-migration-MEU-47-handoff.md` |

Rolling review files (append, never fork into `-recheck` / `-final` variants):

- Plan review: `.agent/context/handoffs/2026-09-02-p10-queue-card-migration-plan-critical-review.md`
- Implementation review: `.agent/context/handoffs/2026-09-02-p10-queue-card-migration-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Shared-surface corrections (`META_SEGMENTS_CONTRACT`, `DEAD_REGION_RULE`, `QueueToolbar`) + `MOUNT_GATE_SCRIPT` authored with `-SelfTest` | — | `shared` | `ui/src/renderer/src/components/queue/*`, `MOUNT_GATE_SCRIPT`, `C:/Temp/av-kit/mount-gate-selftest.txt` |
| WP-2 | MEU-45 convert migration (commands module, mount, toolbar, kebab, confirm ids, E2E rewrite) | WP-1 | `shared` | MEU-45 handoff; `C:/Temp/av-kit/meu45-*.txt` |
| WP-3 | MEU-46 downloader migration (commands module, mount, summary bar, table + dependency deletion, E2E rewrite) | WP-2 | `compact_continue` | MEU-46 handoff on disk; compact after it lands, then re-read `task.md` + the MEU-45/46 handoffs |
| WP-4 | MEU-47 selection + sticky bulk bar + Clear finished on both pages | WP-3 | `compact_continue` | MEU-47 handoff on disk; compact after it lands, then re-read `task.md` |
| WP-5 | Closeout: registry / BUILD_PLAN / current-focus / known-issues updates, review dispatch, reflection, metrics | WP-4 | `shared` | reflection + metrics + review verdict file |

`isolated` is not used: this harness (Claude Code) has `fresh_worker: none` for this project.

---

## User Review Required

> [!IMPORTANT]
> **This is content for the reviewer, not a cue to stop.** Per GUARDRAILS SIGN 1 this plan
> auto-dispatches `/plan-critical-review` the moment it is written.
>
> 1. **`RETIRED_GATE_SCRIPT` is retired, not deleted.** It stays on disk as the executable record of
>    the Session 20 no-mount contract and gains a header comment naming `MOUNT_GATE_SCRIPT` as its
>    successor. Running it against a migrated tree will (correctly) fail; nothing runs it any more.
> 2. **Four E2E tests are rewritten** (`W1-3`, `W1-5`, `W8-3`, `W8-5`). They currently encode the
>    superseded 13-button toolbar from `06-gui.md` §Queue Controls. `E2E_REWRITE_RULE` governs the
>    rewrite: no assertion is deleted without a replacement asserting the same capability at its new
>    home, and clause 4 of `MOUNT_COMPLETENESS_RULE` enforces that mechanically.
> 3. **`@tanstack/react-table` is removed from `ui/package.json`** in MEU-46 — the two deleted tables
>    are its only consumers repo-wide (verified).
> 4. **Governance conflict flagged**: `.agent/context/harness.local.md` sets
>    `plan_to_exec_gate: reviewer-auto` with `driver: Cursor IDE`, but this session runs in Claude
>    Code (`human`). This plan takes the conservative `PLAN_TO_EXEC_GATE = "human"` path, carried
>    forward from the foundations project's explicit user decision. See Open Questions OQ-1.

---

## Design Decisions (create-plan Step 2B)

Four spec forks were unresolved by the build plan alone and are resolved here with a recommendation,
so no behaviour is invented silently at implementation time.

| ID | Fork | Options | Decision | Basis |
|---|---|---|---|---|
| DEC-1 | How does the card render feature-specific meta (quality / speed / ETA / kind / mode) without leaking downloader and convert fields into a shared component? | **A.** Widen `QueueCardJob` with every field either feature needs. **B.** `metaSegments?: readonly string[]` prop composed by the page; `resolveMeta` output stays first. **C.** Render-prop / `renderMeta` slot. | **B** — `META_SEGMENTS_CONTRACT` | A couples the shared card to both features and grows with every new queue (Transcript at MEU-48, TTS after). C makes the meta line untestable in isolation and lets a page bypass the state precedence copy. B keeps one owner for state copy (`resolveMeta`) and one owner for domain copy (the page), and is a pure-function unit-test target. |
| DEC-2 | §Toolbar reduction says "13 buttons to 4 plus an overflow" but the Kept table lists Start / Pause / Resume / Clear finished / ⋮, and Pause+Resume "collapse into one toggle" — 4 is ambiguous. | **A.** 4 = `TOOLBAR_CONTROLS` (Start, Pause⇄Resume toggle, Clear finished, ⋮ trigger); the "overflow" phrase names the *menu*. **B.** 4 buttons + a separate ⋮ = 5 elements, the 4th being a retained queue-level Cancel. | **A** — `TOOLBAR_CONTROLS` | B contradicts `USER_LOCKS` ("`Cancel queue` appears ONLY on the in-flight row") and contradicts §Toolbar reduction's own "everything else moves onto the card". A is the only reading under which every one of the 13 originals has exactly one named new home in `RETIRED_TOOLBAR_CONTROLS`. Made mechanically checkable: `[data-testid="queue-toolbar"]` contains exactly 4 interactive elements; a 5th fails AC-45.6. |
| DEC-3 | `RETIRED_GATE_SCRIPT` fails the build the moment a page mounts the queue primitives — precisely what this project does. Delete it, disable it, or replace it? | **A.** Delete. **B.** Leave it and stop running it. **C.** Retire with a superseding header + author the inverse gate. | **C** — `MOUNT_COMPLETENESS_RULE` | The foundations reflection is explicit: *"Do not silently delete it; replace it with a mount-completeness gate."* A loses the executable record of the Session 20 contract. B leaves a live-looking script that fails on a correct tree — a trap for the next session. C keeps the record, names the successor in-file, and converts the guarantee from "nothing is wired" to "everything is wired and no capability was lost". |
| DEC-4 | §Empty state and drop targets specifies a file drop target with a `Browse…` peer, but it sits in a Phase 10 whose §Scope adds no new REST surface — and `DownloaderPage` has no local-file intake at all. Does the drop invitation apply to both queues? | **A.** Both pages render `EmptyDropZone`; the downloader's `Browse…` is inert or opens a picker nothing consumes. **B.** Widen the downloader to local-file downloading (new endpoint). **C.** Per-page contract: converter keeps the file-drop invitation, downloader gets a URL invitation pointing at its real intake. | **C** — `EMPTY_STATE_CONTRACT` | A ships a dead control, which `MOUNT_GATE_CLAUSE_4` (d) exists to reject and `NO_DEAD_CONTROL_RULE` forbids outright. B needs a REST surface the spec's own §Scope excludes and no MEU in `meu-registry.md` 10.1–10.9 owns. C is the only reading where each page's empty state points at an intake that actually exists: `window.api.showFilesDialog` → `staging` on the converter (`ConvertPage.tsx:470-484`), `url-input` → `POST /downloads` on the downloader (`DownloaderPage.tsx:156-170`). |

---

## Proposed Changes

### MEU-45 — `gui-convert-queue` (Phase 10.5)

Shared-surface corrections + the Convert page migration. The convert page goes first because it
already owns a portal confirm and a kebab-free toolbar, so it exercises every new seam with the
smaller blast radius.

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `PUT /conversions/reorder` body (existing) | server-side `ReorderIn` (unchanged) | `REORDER_WIRE_CONTRACT` — `{ job_ids: string[] }`, a **complete permutation**; any other shape 422s (`routes/conversions.py:232-239`). Built by the existing `buildReorderBody` | unchanged (`extra="forbid"` server-side) |
| `POST /conversions/{id}/reset` (existing) | server-side (unchanged) | client gates the call on `CONVERT_REQUEUEABLE_STATUSES` (**not** the wider download set); a 409 surfaces per `ERROR_SURFACE` | unchanged |
| `DELETE /conversions/{id}` (existing) | server-side (unchanged) | id is an opaque string from the list envelope; never user-typed | unchanged |
| `ConversionListItem` (read boundary) | `parseListEnvelope` in `useConversionQueue.ts` | already validated; MEU-45 adds no new field | n/a — read path |

No new write surface is introduced. `BULK_ENDPOINT_POLICY` explicitly forbids inventing one.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-45.1 | unit | `QueueCard` accepts `metaSegments?: readonly string[]` and renders `[resolveMeta(job), ...metaSegments]` with empty/`—` segments dropped, joined by `META_SEPARATOR` (`META_SEGMENTS_CONTRACT`). | Research-backed (DEC-1) | Passing `[]`, `undefined`, or `['', '—']` renders exactly the unchanged `resolveMeta` output — no stray separator. |
| AC-45.2 | unit | With no `onOpen` prop, the card's title/meta region renders with no `role`, no `tabIndex` and no `aria-label` (`DEAD_REGION_RULE`); with `onOpen`, all three are present and Enter/Space activate it. | Research-backed (`DEAD_REGION_RULE`) | Querying `getByRole('button', { name: /Open details/ })` on a card without `onOpen` finds nothing. |
| AC-45.3 | unit | New `QueueToolbar` component renders exactly `TOOLBAR_CONTROLS` inside `[data-testid="queue-toolbar"]`; `pause-resume` is a single button whose label/testid reflect `PAUSE_SCOPE` state; every control renders an icon **and** a persistent text label (`TOOLBAR_LABEL_RULE`). | Spec §Toolbar reduction | A toolbar rendered with an extra control fails the "exactly 4 interactive elements" assertion; a control whose label is only a `title` attribute fails `TOOLBAR_LABEL_RULE`. |
| AC-45.4 | unit | The **existing** `convert-commands.ts` (a live module whose `CONVERT_COMMANDS` palette map is consumed by `AppShell.tsx:3` and `commandRegistry.ts:2`) is **extended** with `resetConversion`, `removeConversion`, `reorderConversion` — each an async function that throws a typed error carrying the HTTP status (`COMMAND_MODULE_RULE`, `ERROR_SURFACE`). `clearConversions` already exists and is reused unchanged. | Local Canon (`COMMAND_MODULE_RULE`) | A non-2xx response rejects with a message containing the status; it never resolves silently. |
| AC-45.4a | unit | A regression test imports `convert-commands.ts` and asserts every name in `COMMAND_MODULE_PRESERVED_EXPORTS['convert-commands.ts']` is still defined, and that `CONVERT_PALETTE_IDS` is unchanged. | Local Canon (`COMMAND_MODULE_PRESERVED_EXPORTS`) | Dropping any palette export fails in the Red phase, before the command palette silently breaks. |
| AC-45.5 | unit | `convert-controls.ts` `controlEnabled('reset')` returns true for every member of `CONVERT_REQUEUEABLE_STATUSES` and false for every member of its complement; the test enumerates the conversion status enum so `REQUEUE_EXHAUSTIVENESS_RULE` holds. | Spec §Re-queue contract + `USER_LOCKS` | `QualityBlocked`/`AgeRestricted` are **not** conversion statuses and must not be accepted here; `Skipped` returns false (the lock), asserted explicitly. |
| AC-45.6 | integration | `ConvertPage` renders `QueueList` (testid `convert-queue`) with one `convert-queue-row` card per item; `[data-testid="queue-toolbar"]` contains exactly 4 interactive elements (DEC-2). | Spec §Toolbar reduction | Rendering a 5th toolbar control fails; a `<table>` in the queue region fails. |
| AC-45.7 | integration | `ConvertQueueTable.tsx` is deleted and nothing in `ui/src` references it or `@tanstack/react-table` from the converter feature. | Spec §Toolbar reduction | A surviving import fails `MOUNT_GATE_SCRIPT -Scope convert` clause 2. |
| AC-45.8 | integration | The card kebab exposes `KEBAB_MENU_ORDER` in that order; unavailable actions are **absent**, never disabled; `copy-location` reads `Copy path` when `output_path` exists else `Copy URL`. | Spec §Kebab menu | A `Pending` card's menu contains no `open-file` entry (absent, not `disabled`). |
| AC-45.9 | integration | Kebab move actions call `reorderConversion`, which sends `REORDER_WIRE_CONTRACT` — the full `{ job_ids }` permutation produced by the existing `buildReorderBody(ids, id, direction)` (`convert-controls.ts:108-128`), not a `{ id, direction }` body. `Alt+ArrowUp` / `Alt+ArrowDown` on a focused card issue the same call with `up` / `down`. | Spec §Reorder model + `REORDER_WIRE_CONTRACT` | A `{ id, direction }` body 422s — the test asserts the intercepted body is a complete permutation of the rendered ids. `ArrowUp` without `Alt` does not reorder. |
| AC-45.10 | integration | The card primary action follows `PRIMARY_ACTION_MAP`; the in-flight row's control has accessible name `CANCEL_CONTROL_LABEL` and takes effect with **no** confirm; no card renders any label in `CANCEL_LABEL_FORBIDDEN`. | Spec §Primary action model + `USER_LOCKS` | A `Pending` card renders no `Cancel queue`; a rendered `Stop`/`Cancel` label fails. |
| AC-45.11 | integration | Remove uses the shared `ConfirmModal` (`G20_RULE`) with the verb-labeled confirm button `Remove` (`USER_LOCKS`); the hand-rolled `createPortal` confirm in `ConvertPage.tsx` is deleted and the testids follow `RETIRED_TESTIDS`. | Local Canon `G20_RULE` + `USER_LOCKS` | Dismissing the modal issues no `DELETE`; a confirm button labeled `OK`/`Yes` fails. |
| AC-45.12 | integration | The legacy `STATUS_COLORS` map in `convert-controls.ts` is deleted; status colour comes from the shared `lib/queue/status-tokens.ts` fill+label pairing. | Spec §Card state precedence | A surviving `STATUS_COLORS` export fails `MOUNT_GATE_SCRIPT` clause 6. |
| AC-45.13 | integration | `MOUNT_GATE_SCRIPT` exists, supports `-Scope convert\|downloader\|all` and `-SelfTest`, implements all **8** clauses of `MOUNT_COMPLETENESS_RULE` — clause 4 exactly as `MOUNT_GATE_CLAUSE_4` states, iterating the **per-page** sub-maps of `RETIRED_TOOLBAR_CONTROLS` and then every element of each id's home list, obligated per `MOUNT_GATE_PHASE_SCOPES` — and `-SelfTest` passes with at least one **negative** fixture per clause. | Local Canon (DEC-3) + `MOUNT_GATE_CLAUSE_4` | Clause-4 negative fixtures must include: a converter tree still containing `convert-up` (a flat downloader-id map would false-pass it); a new home that renders but is wired to nothing (fails (d)); an E2E test that only asserts `toBeVisible()` on the new home (fails (c)); a **sibling-home** tree where `kebab move-top` is wired and asserted but `bulk-move-top` renders dead — `-Scope all` must FAIL it while `-Scope convert` reports it `PENDING (MEU-47)`; and a downloader tree carrying `queue-empty-dropzone` (fails clause 7's per-page split). |
| AC-45.14 | integration | `RETIRED_GATE_SCRIPT` keeps its file and gains a header comment naming `MOUNT_GATE_SCRIPT` as its successor and stating it must not be run against a migrated tree. | Local Canon (DEC-3) | The file being absent fails. |
| AC-45.15 | integration | `convert-queue.test.ts` is rewritten under `E2E_REWRITE_RULE`: `W8-3` and `W8-5` assert `TOOLBAR_CONTROLS` + the card surface, and **every key** of `RETIRED_TOOLBAR_CONTROLS.converter` gets a replacement that satisfies `MOUNT_GATE_CLAUSE_4` (c)+(d) — it performs the interaction and asserts the resulting request or DOM state. `W8-4`'s confirm flow uses the `RETIRED_TESTIDS` mapping. | Local Canon `E2E_REWRITE_RULE` + `E2_RULE` | Deleting an assertion without a replacement fails clause 4; a replacement that only checks visibility fails (c). |
| AC-45.16 | integration | All `NEW_TESTIDS` introduced by this MEU are registered in `ui/tests/e2e/test-ids.ts`, and every id in `PRESERVED_TESTIDS` is still registered. | Local Canon | An unregistered new id fails the census; a dropped preserved id fails clause 5. |
| AC-45.17 | unit | A pure `convertMetaSegments(item)` returns `CONVERT_META_SEGMENTS` — kind label and mode label always, speed and ETA **whenever the field is non-null, regardless of status** — so the Kind/Mode/Speed/ETA columns of the deleted `ConvertQueueTable` survive as card meta. | Spec §QueueCard anatomy + Local Canon (`CONVERT_META_SEGMENTS`) | A `Done` row **with** a persisted `speed` still yields the speed segment (the backend does not clear it — `services/conversion.py:553-573`); only a null field yields no segment. A `cut` row with null `in_ms`/`out_ms` yields no empty mode segment rather than a stray `—`. |
| AC-45.18 | unit | A shared `runBulk(ids, fn)` executor and a `clearFinished(queue)` built on it land **in this MEU**, before any toolbar is mounted, implementing `CLEAR_FINISHED_SEMANTICS` clauses 1-7 over `CLEAR_FINISHED_SNAPSHOT_STATUSES`. | Local Canon (`NO_DEAD_CONTROL_RULE`) | Mounting `queue-toolbar-clear-finished` in a tree where `clearFinished` is not implemented is a dead control and fails `MOUNT_GATE_CLAUSE_4` (d). |
| AC-45.19 | integration | `QueueList` implements the **converter** half of `EMPTY_STATE_CONTRACT`: with `items=[]` it renders `EmptyDropZone` (`queue-empty-dropzone`) including the `Browse…` button; with items it renders the list plus the compact `queue-drop-strip`. Both `onBrowse` and `onDropFiles` route to the page's **existing** production intake — `window.api.showFilesDialog(CONVERT_DIALOG_FILTERS)` feeding the same `staging` state that backs today's `convert-browse` button (`ConvertPage.tsx:470-484`), which is itself untouched — the staging drop zone and the queue empty state share the handler, not the testid. The empty-state button carries `queue-empty-browse` via `EmptyDropZone`'s existing `browseTestId` prop (`EmptyDropZone.tsx:190`). | Spec §Empty state and drop targets | Today `QueueList` returns a bare `<div>` with only the hover overlay when `items=[]` (`QueueList.tsx:77-104`) — an empty converter queue would render a blank panel where the deleted table renders an empty-state row. A tree missing either id fails `MOUNT_COMPLETENESS_RULE` clause 7; so does a `Browse…` wired to a no-op — the E2E stubs the dialog, clicks `Browse…`, and asserts the picked paths appear in `staging`. |
| AC-45.19a | integration | The **downloader** half of `EMPTY_STATE_CONTRACT` is explicitly NOT this component's job: `QueueList` takes the empty-state slot as a prop so `DownloaderPage` can supply `queue-empty-invite` instead (AC-46.14). `QueueList` renders no `queue-empty-dropzone` when the host supplies its own empty slot. | Local Canon (`EMPTY_STATE_CONTRACT`) | A `QueueList` that hard-codes `EmptyDropZone` forces a file-drop invitation onto a URL-intake queue — the round 2 F12 defect. |
| AC-45.20 | integration | Before the first E2E rewrite, `E2E_ASSERTION_CENSUS_RULE`'s before-census is captured to `C:/Temp/av-kit/e2e-assertion-census-before.txt` and referenced by the handoff. | Local Canon (`E2E_ASSERTION_CENSUS_RULE`) | A rewrite performed with no before-census cannot prove no capability lost its assertions, and the MEU cannot be marked `[x]`. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Toolbar control set | Spec, ambiguous count | Resolved by DEC-2 → `TOOLBAR_CONTROLS`, made mechanically checkable |
| Meta-line composition | Spec (fields named) / under-specified (mechanism) | Resolved by DEC-1 → `META_SEGMENTS_CONTRACT`; convert's own fields are `CONVERT_META_SEGMENTS` (AC-45.17) |
| Kebab order, availability, labels | Spec | `KEBAB_MENU_ORDER` verbatim from §Kebab menu |
| Primary action per state | Spec | `PRIMARY_ACTION_MAP` verbatim from §Primary action model |
| Cancel accessible name | Spec + Human-approved | `CANCEL_CONTROL_LABEL` / `CANCEL_LABEL_FORBIDDEN` |
| Retry status set | Spec | `CONVERT_REQUEUEABLE_STATUSES` (narrower than the download set); `Skipped` excluded by `USER_LOCKS`; exhaustiveness by `REQUEUE_EXHAUSTIVENESS_RULE` |
| Reorder request shape | Local Canon | `REORDER_WIRE_CONTRACT` — `{ job_ids }` permutation via the existing `buildReorderBody`; no new wire shape is invented |
| Empty / non-empty drop surface | Spec | `EMPTY_STATE_CONTRACT` from §Empty state and drop targets |
| Command module ownership | Local Canon | `COMMAND_MODULE_RULE` + `COMMAND_MODULE_PRESERVED_EXPORTS` — both `*-commands.ts` modules already exist and are extended, never recreated |
| Confirm dialog mechanism | Local Canon | `G20_RULE` — shared `ConfirmModal`; convert's ids migrate per `RETIRED_TESTIDS` because `ConfirmModal` has no testId override prop |
| Dead focusable region | Research-backed | `DEAD_REGION_RULE` (WAI-ARIA APG: a widget role must advertise a real interaction) |
| Fate of the isolation gate | Local Canon | `MOUNT_COMPLETENESS_RULE` per the foundations reflection's Next Day Outline item 2 |
| E2E rewrite legitimacy | Local Canon | `E2E_REWRITE_RULE` — supersession with mandatory replacement assertions |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modify | `metaSegments` prop (`META_SEGMENTS_CONTRACT`); conditional title-region semantics (`DEAD_REGION_RULE`) |
| `ui/src/renderer/src/components/queue/QueueToolbar.tsx` | new | `TOOLBAR_CONTROLS` + `QUEUE_OVERFLOW_MENU`, `TOOLBAR_LABEL_RULE` |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | **modify** | Extend the **existing** module (AC-45.4); every name in `COMMAND_MODULE_PRESERVED_EXPORTS` survives |
| `ui/src/renderer/src/lib/queue/run-bulk.ts` | new | Shared `runBulk` + `clearFinished` executor (AC-45.18, `CLEAR_FINISHED_SEMANTICS`) — lands before the first toolbar mount |
| `ui/src/renderer/src/components/queue/QueueList.tsx` | modify | `EMPTY_STATE_CONTRACT` (AC-45.19, AC-45.19a) — mount `EmptyDropZone` and the non-empty drop strip, with the empty slot overridable by the host page |
| `ui/src/renderer/src/features/converter/convert-controls.ts` | modify | Retry corrected to `CONVERT_REQUEUEABLE_STATUSES`; legacy `STATUS_COLORS` deleted; `convertMetaSegments` added |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | Mount `QueueList` + `QueueToolbar`; delete the hand-rolled portal confirm; wire kebab + `Alt+↑/↓` |
| `ui/src/renderer/src/features/converter/ConvertQueueTable.tsx` | delete | Superseded by `QueueList` |
| `ui/tests/unit/queue-card.test.ts` (+ new units) | modify | AC-45.1/.2/.3/.4/.5/.17 |
| `ui/tests/e2e/convert-queue.test.ts` | modify | Rewrite under `E2E_REWRITE_RULE` |
| `ui/tests/e2e/test-ids.ts` | modify | Register `NEW_TESTIDS` |
| `MOUNT_GATE_SCRIPT` | new | Inverse gate + `-SelfTest` |
| `RETIRED_GATE_SCRIPT` | modify | Superseding header comment only |

---

### MEU-46 — `gui-downloader-queue` (Phase 10.6)

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `PUT /downloads/reorder` body (existing) | server-side `ReorderIn` (unchanged) | `REORDER_WIRE_CONTRACT` — `{ job_ids: string[] }` complete permutation; 422 otherwise (`routes/downloads.py:210-217`) | unchanged |
| `POST /downloads/{id}/reset` (existing) | server-side (unchanged) | gated on `DOWNLOAD_REQUEUEABLE_STATUSES`; 409 surfaces per `ERROR_SURFACE` | unchanged |
| `DELETE /downloads/{id}` (existing) | server-side (unchanged) | opaque id from the list envelope | unchanged |
| `DownloadListItem` (read boundary) | `parseListEnvelope` in `useDownloadQueue.ts` | unchanged | n/a — read path |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-46.1 | unit | The **existing** `download-commands.ts` (consumed by `AppShell.tsx:5`, `commandRegistry.ts:3`, `DownloaderPage.tsx:36` and three unit suites) is **extended** with `resetDownload`, `removeDownload`, `reorderDownload` under the AC-45.4 error contract (`COMMAND_MODULE_RULE`). `clearDownloads` and the SABR commands are reused unchanged. | Local Canon | Non-2xx rejects with the status in the message. |
| AC-46.1a | unit | A regression test asserts every name in `COMMAND_MODULE_PRESERVED_EXPORTS['download-commands.ts']` is still defined and `DOWNLOAD_PALETTE_IDS` is unchanged. | Local Canon (`COMMAND_MODULE_PRESERVED_EXPORTS`) | Dropping `forceSabr` or any palette deliverer fails Red. |
| AC-46.2 | unit | `download-controls.ts` `controlEnabled('reset')` returns true for every member of `DOWNLOAD_REQUEUEABLE_STATUSES` and false for every member of its complement, enumerating the download status enum per `REQUEUE_EXHAUSTIVENESS_RULE`. | Spec §Re-queue contract + `USER_LOCKS` | `Skipped` false (the lock), asserted explicitly. |
| AC-46.3 | unit | A pure `downloadMetaSegments(item)` returns `DOWNLOAD_META_SEGMENTS` — quality always, speed and ETA **whenever non-null, regardless of status**. | Spec §QueueCard anatomy + Local Canon (`DOWNLOAD_META_SEGMENTS`) | A `Done` row with persisted `speed`/`eta` still renders them (`services/download.py:559-568` does not clear them); a null field yields no empty segment. |
| AC-46.4 | integration | `DownloaderPage` renders `QueueList` with testid `queue-list` and one `queue-card` per item; the retired `queue-table`/`queue-row` ids are gone (`RETIRED_TESTIDS`). | Spec §QueueCard anatomy | A surviving `queue-table` id fails clause 4. |
| AC-46.5 | integration | `DownloadQueueTable.tsx` is deleted, `@tanstack/react-table` is removed from **both** `ui/package.json` and `ui/package-lock.json` (via `npm uninstall`, not a hand edit), and no `ui/src` file imports it. | Spec §Toolbar reduction | A surviving import **or** a surviving lockfile entry fails `MOUNT_GATE_SCRIPT -Scope all` clause 3 — a manifest-only removal leaves the package still installed by `npm ci`. |
| AC-46.6 | integration | The downloader toolbar renders exactly `TOOLBAR_CONTROLS` (DEC-2), reusing `QueueToolbar`; `queue-summary` and `processor-indicator` remain (`PRESERVED_TESTIDS`). | Spec §Toolbar reduction | A 5th control fails; a dropped `queue-summary` fails clause 5. |
| AC-46.7 | integration | The ~100 lines of inline `apiFetch` in `DownloaderPage.tsx` (lines 480–633) are replaced by `download-commands.ts` calls; the kebab, the primary action and the toolbar all call the same functions. | Local Canon `COMMAND_MODULE_RULE` | A surviving inline `apiFetch` in a page `onClick` fails review. |
| AC-46.8 | integration | Downloader `Clear all` opens a `ConfirmModal` before deleting (it currently deletes with no confirm) with a verb-labeled confirm button. | Spec §Toolbar reduction + `G20_RULE` + `USER_LOCKS` | Dismissing issues no `DELETE`. |
| AC-46.9 | integration | Cards render `DOWNLOAD_META_SEGMENTS` via `metaSegments`, so Quality/Speed/ETA information survives the loss of the table columns. | Spec §QueueCard anatomy | An in-flight card missing speed or ETA fails; a `Done` card whose envelope carries a non-null `speed` and omits it also fails (parity with what `DownloadQueueTable` renders today). |
| AC-46.10 | integration | Primary action, kebab, `Alt+↑/↓`, `CANCEL_CONTROL_LABEL` and the absent-never-disabled rule behave on the downloader exactly as AC-45.8/.9/.10 specify for convert. | Spec §Primary action model, §Kebab menu | Same negatives as AC-45.8/.10. |
| AC-46.11 | integration | `download-queue.test.ts` is rewritten under `E2E_REWRITE_RULE`: `W1-3` and `W1-5` assert `TOOLBAR_CONTROLS` + the card surface, and **all 13 keys** of `RETIRED_TOOLBAR_CONTROLS.downloader` get a replacement satisfying `MOUNT_GATE_CLAUSE_4` (c)+(d). | Local Canon `E2E_REWRITE_RULE` + `E2_RULE` | A retired id asserted with no replacement fails clause 4; the reorder replacements must assert a `REORDER_WIRE_CONTRACT` body. |
| AC-46.12 | integration | `MOUNT_GATE_SCRIPT -Scope downloader` passes and its receipt is captured under `VALIDATION_RECEIPT_DIR`. | Local Canon (DEC-3) + `MOUNT_GATE_PHASE_SCOPES` | Any clause failing blocks the MEU. `-Scope all` is **not** this MEU's gate — it obligates every MEU-47 home, which does not exist yet; it is AC-47.11's gate. The MEU-47 homes must appear in this run's `PENDING (MEU-47)` list, not be silently omitted. |
| AC-46.13 | integration | The E2E suite runs at ≥ `E2E_BASELINE_COUNT` tests, 0 failed, EXIT=0 under `E2E_SANDBOX` conditions, **and** satisfies `E2E_ASSERTION_CENSUS_RULE` — the after-census shows no capability at zero assertions and no drop in assertion count. | Local Canon | A case count held at 59 while assertions were softened fails the census, which the case floor alone would not catch. |
| AC-46.14 | integration | `DownloaderPage` implements the **downloader** half of `EMPTY_STATE_CONTRACT`: with an empty queue it renders `queue-empty-invite` — microcopy pointing at the URL field and a `queue-empty-invite-action` button that focuses the existing `url-input` (`DownloaderPage.tsx:252`). No `queue-empty-dropzone`, no `queue-drop-strip`: the page has no local-file intake and Phase 10 adds no REST surface. | Local Canon (`EMPTY_STATE_CONTRACT`) | The E2E clicks the invite and asserts `document.activeElement` is `url-input`, then types a URL and asserts the normal `POST /downloads` body — a no-op button fails `MOUNT_COMPLETENESS_RULE` clause 7. A tree carrying `queue-empty-dropzone` on this page also fails clause 7. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Downloader card meta fields | Spec | `DOWNLOAD_META_SEGMENTS` via `META_SEGMENTS_CONTRACT` |
| Summary bar retention | Local Canon | `PRESERVED_TESTIDS` — `queue-summary`, `processor-indicator` keep their ids on the same semantic element |
| Clear all confirm | Spec + Local Canon | §Toolbar reduction places `Clear all…` behind an ellipsis (a confirm); `G20_RULE` fixes the mechanism |
| `@tanstack/react-table` removal | Local Canon | Verified: the two deleted tables are its only consumers repo-wide |
| Toolbar parity across the two pages | Spec | Both pages consume the same `QueueToolbar` — one owner, one contract |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/downloader/download-commands.ts` | **modify** | Extend the **existing** module (AC-46.1); `COMMAND_MODULE_PRESERVED_EXPORTS` survives |
| `ui/src/renderer/src/features/downloader/download-controls.ts` | modify | Retry widened to `DOWNLOAD_REQUEUEABLE_STATUSES`; `downloadMetaSegments` added |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | Mount `QueueList` + `QueueToolbar`; remove inline `apiFetch`; add `Clear all` confirm; supply the `queue-empty-invite` empty slot (AC-46.14) |
| `ui/src/renderer/src/features/downloader/DownloadQueueTable.tsx` | delete | Superseded by `QueueList` |
| `ui/package.json`, `ui/package-lock.json` | modify | Drop `@tanstack/react-table` via `npm uninstall` — both manifests (AC-46.5) |
| `ui/tests/unit/*` | modify | AC-46.1/.2/.3 |
| `ui/tests/e2e/download-queue.test.ts` | modify | Rewrite under `E2E_REWRITE_RULE` |
| `ui/tests/e2e/test-ids.ts` | modify | Retire `queue-table`/`queue-row`, register replacements |

---

### MEU-47 — `gui-queue-bulk` (Phase 10.7)

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Bulk fan-out (no new endpoint) | n/a — `BULK_ENDPOINT_POLICY` | Each action issues the existing per-id request once per selected id | n/a |
| Selection state | `useQueueSelection` hook | `Set<string>` of ids that exist in the current list envelope; ids absent from the list are pruned on every refetch | n/a — client state |

> `BULK_ENDPOINT_POLICY` is load-bearing here: `POST /{queue}/bulk` does not exist and this MEU may
> not invent it. If a reviewer believes a server-side bulk endpoint is warranted, that is a new MEU,
> not a scope expansion.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-47.1 | unit | `useQueueSelection` implements `SELECTION_MODEL`: toggle, Shift+click inclusive range from the last anchor in render order, Ctrl/Cmd+A over the **filtered** list, clear after a completed bulk action. | Spec §Selection and bulk model | Shift+click with no prior anchor selects only the clicked row; ids that vanish from the envelope are pruned rather than acted on; Ctrl/Cmd+A with a filter applied selects only filtered rows. |
| AC-47.1a | unit | `SELECTION_PRIMITIVE_EXTENSION`: `SelectionCheckbox.onChange` and `QueueCard.onSelectChange` are widened to forward a `{ shiftKey: boolean }` modifiers argument, and `SelectionCheckbox`'s `onClick` stops propagation **without** discarding that modifier state. | Research-backed (`SELECTION_PRIMITIVE_EXTENSION`) | Today `onChange` is `(checked) => void` (`SelectionCheckbox.tsx:16`) and `onSelectChange` is `(id, checked) => void` (`QueueCard.tsx:93`), so AC-47.1's Shift+click range would be reachable **only from a test harness** and never from the running app. A signature that still drops `shiftKey` fails this AC. |
| AC-47.2 | unit | A shared `runBulk(ids, fn)` helper implements `CLEAR_FINISHED_SEMANTICS` clauses 1–5: snapshot, independent per-id calls, continue-on-failure, successes kept, exactly one refetch after the fan-out settles. | Spec §Clear finished | With 3 of 5 calls rejecting, the 2 successes persist, the refetch fires exactly once, and the result reports `2 succeeded / 3 failed`. |
| AC-47.3 | integration | `runBulk`'s result feeds a `G35_RULE` partial-result toast stating the removed count, the failed-or-skipped count **and a reason per failure** — clause 7 of `CLEAR_FINISHED_SEMANTICS`. Tagged `integration` because it asserts the executor is actually wired to the live toast provider, which a pure unit test of `runBulk` cannot show. | Spec §Clear finished + `G35_RULE` | An all-success run shows a success toast, not a partial one; an all-failure run shows an error toast; a partial run whose toast omits the per-failure reasons fails clause 7. |
| AC-47.4 | integration | `BulkActionBar` is **sticky above the list** — rendered inside the queue panel immediately above `QueueList`, `position: sticky` against the panel's scroll container — whenever the selection is non-empty, and unmounted when it is empty (`USER_LOCKS`). | Spec §Selection and bulk model:220-222 + Human-approved (`USER_LOCKS`) | A viewport-bottom fixed bar fails: the spec says "sticky above the list ... never a floating bottom bar". With an empty selection the bar is absent from the DOM — not merely hidden. |
| AC-47.5 | integration | The bar exposes `bulk-selection-count` then exactly `BULK_BAR_ACTIONS` in that order (`bulk-retry`, `bulk-move-top`, `bulk-move-bottom`, `bulk-remove` destructive-variant, spacer, `bulk-clear-selection`); `bulk-retry` is enabled only when at least one selected row is in that page's requeueable set. | Spec §Selection and bulk model:220-223 | A bar rendering `bulk-move-up`/`bulk-move-down` or a bar-level select-all fails — the spec's bar carries move-**top**/move-**bottom** only and select-all belongs to `SELECTION_HEADER_CONTRACT`. A selection of only `Skipped` rows disables `bulk-retry` (`USER_LOCKS`). |
| AC-47.5a | integration | A header `SelectionCheckbox` (`queue-select-all`) sits above the list at all times per `SELECTION_HEADER_CONTRACT`: checked when every filtered row is selected, `indeterminate` when some are, unchecked when none are, with an "N items" count; toggling it acts on the **filtered** list. | Spec §Selection and bulk model:215-217 | With 2 of 5 rows selected the input's `indeterminate` DOM property is `true` and `checked` is `false`; a header that only appears once a row is selected fails (it is the control that starts the selection). |
| AC-47.6 | integration | `bulk-remove` opens a `ConfirmModal` whose confirm button reads `Remove N items` (`USER_LOCKS` verb-labeled rule); dismissing issues no request. | Human-approved (`USER_LOCKS`) + `G20_RULE` | A confirm button labeled `OK` fails; dismissal issues zero `DELETE`s. |
| AC-47.7 | integration | `Clear finished` in `TOOLBAR_CONTROLS` is wired to the AC-45.18 executor on **both** pages and implements all 7 clauses of `CLEAR_FINISHED_SEMANTICS` over `CLEAR_FINISHED_SNAPSHOT_STATUSES`. | Spec §Clear finished:60,62-74 | A queue holding a mix of `TERMINAL_STATUSES` rows issues `DELETE` only for the ids in `CLEAR_FINISHED_SNAPSHOT_STATUSES` — sweeping the wider set would destroy failure evidence the user has not seen. A row that becomes `Done` *after* the click is not removed (snapshot clause). A `404` on one id does not abort the run and every snapshotted id is still attempted exactly once. Files on disk are untouched. |
| AC-47.7a | unit | Bulk `move-top` / `move-bottom` follow `BULK_REORDER_ALGORITHM`: each `PUT` body is `REORDER_WIRE_CONTRACT`-shaped and is the fold of the **preceding successful** call, never of the stale initial order. | Research-backed (`BULK_REORDER_ALGORITHM`) | Computing all N permutations up front from the initial order makes step N clobber steps 1..N-1, since the endpoint takes an absolute permutation. A run where step 2 rejects must have step 3 fold from step 1's accepted order. |
| AC-47.8 | integration | Every bulk action is a client-side fan-out of existing per-id endpoints (`BULK_ENDPOINT_POLICY`). | Spec §Selection and bulk model | Any request to a `/bulk` path fails the AC. |
| AC-47.9 | integration | Selection interaction does not fight the card's nested controls: clicking the kebab, the primary action or a link inside a card does not toggle selection. | Spec §QueueCard anatomy (nested-interactive rule) | Clicking the kebab leaves the selection unchanged. |
| AC-47.10 | integration | Both pages' E2E suites satisfy `BULK_CONTROL_E2E_OBLIGATION` in full — every one of the five `BULK_BAR_ACTIONS` is clicked and its outcome asserted (not just remove), plus a Clear finished run with a mixed queue. | Local Canon `E2_RULE` + `BULK_CONTROL_E2E_OBLIGATION` | Round 2 F4: covering only bulk Remove and Clear finished left `bulk-retry` / `bulk-move-top` / `bulk-move-bottom` / `bulk-clear-selection` with no required assertion anywhere, so `-Scope all` could pass with four dead controls. |
| AC-47.10a | integration | The `queue-select-all` header checkbox is exercised in all three `SELECTION_HEADER_CONTRACT` states (none → all, all → none, indeterminate → all) and the keyboard selection entry path is exercised end to end (focus a card, toggle its `SelectionCheckbox` by keyboard, assert the bar appears with the right count). | Local Canon `BULK_CONTROL_E2E_OBLIGATION` + `G34_RULE` | A header checkbox asserted only for presence is a dead control under `MOUNT_GATE_CLAUSE_4` (c)+(d). |
| AC-47.11 | integration | `MOUNT_GATE_SCRIPT -Scope all` passes with an **empty** `PENDING` list — every home of every retired id obligated independently per `MOUNT_GATE_PHASE_SCOPES` — and the E2E suite is ≥ `E2E_BASELINE_COUNT`, 0 failed, EXIT=0. | Local Canon + `MOUNT_GATE_PHASE_SCOPES` | A non-empty `PENDING` list at this scope means a MEU-47 home was never built; a sibling home passing does not cover it. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Selection semantics | Spec | `SELECTION_MODEL` verbatim from §Selection and bulk model |
| Bulk transport | Spec | `BULK_ENDPOINT_POLICY` — client fan-out only, explicit prohibition |
| Partial-failure reporting | Spec + Local Canon | `CLEAR_FINISHED_SEMANTICS` clause 6 + `G35_RULE` |
| Bar placement | Spec + Human-approved | Spec:220-222 — sticky **above the list**, never a floating bottom bar; consistent with `USER_LOCKS` lock 1 |
| Bar action set | Spec | `BULK_BAR_ACTIONS` verbatim from :220-223 — no bulk move-up/down, no bar-level select-all |
| Select-all affordance | Spec | `SELECTION_HEADER_CONTRACT` — header tri-state checkbox over the filtered list |
| Shift+click reachability | Research-backed | `SELECTION_PRIMITIVE_EXTENSION` — the existing primitive signatures drop modifier state, so they are widened here |
| Bulk reorder transport | Research-backed | `BULK_REORDER_ALGORITHM` over `REORDER_WIRE_CONTRACT` — sequential fold, since the endpoint takes an absolute permutation |
| Clear-finished scope | Spec | `CLEAR_FINISHED_SNAPSHOT_STATUSES`, explicitly **not** `TERMINAL_STATUSES` |
| Remove confirm wording | Human-approved | `USER_LOCKS` — verb-labeled `Remove N items` |
| Retry eligibility in bulk | Spec + Human-approved | Per page: `DOWNLOAD_REQUEUEABLE_STATUSES` / `CONVERT_REQUEUEABLE_STATUSES`, both minus `Skipped` |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/components/queue/BulkActionBar.tsx` | new | Sticky-above-the-list bar rendering `BULK_BAR_ACTIONS` |
| `ui/src/renderer/src/components/ui/SelectionCheckbox.tsx` | modify | `SELECTION_PRIMITIVE_EXTENSION` — forward `{ shiftKey }` through `onChange` |
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modify | `SELECTION_PRIMITIVE_EXTENSION` — widen `onSelectChange` |
| `ui/src/renderer/src/components/queue/QueueSelectionHeader.tsx` | new | `SELECTION_HEADER_CONTRACT` tri-state header + count |
| `ui/src/renderer/src/lib/queue/use-queue-selection.ts` | new | `SELECTION_MODEL` |
| `ui/src/renderer/src/lib/queue/bulk-reorder.ts` | new | `BULK_REORDER_ALGORITHM` over `REORDER_WIRE_CONTRACT` |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | Wire selection + bar + Clear finished |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | Wire selection + bar + Clear finished |
| `ui/tests/unit/*` | modify | AC-47.1/.2/.3 |
| `ui/tests/e2e/convert-queue.test.ts`, `download-queue.test.ts` | modify | AC-47.10 |
| `ui/tests/e2e/test-ids.ts` | modify | Register the `bulk-*` `NEW_TESTIDS` |

---

## GUI Element Compliance Check (create-plan §4A — triggered)

`GUI_ENFORCEMENT_FALLBACK` applies: `.agent/docs/gui-standards-enforcement.md`,
`docs/gui-element-reference.md` and `docs/gui-button-index.md` **do not exist** (verified
2026-09-02 by `ls` and `find`). The §4A mapping table is therefore recorded inline, against
`docs/build-plan/06-gui.md` + G30–G37 + `.agent/docs/gui-actions-index.md`.

| Element touched | Standard | Applied where |
|---|---|---|
| Toolbar buttons | `TOOLBAR_LABEL_RULE`, `G32_RULE`, `G34_RULE` | AC-45.3, AC-46.6 |
| Card primary action | `PRIMARY_ACTION_MAP`, `CANCEL_CONTROL_LABEL`, `G32_RULE` | AC-45.10, AC-46.10 |
| Kebab menu | `KEBAB_MENU_ORDER`, absent-never-disabled | AC-45.8, AC-46.10 |
| Progress indicator | `G33_RULE` (`transform: scaleX`, never width) | inherited from MEU-43 `ProgressBar`; asserted unchanged by clause 5 |
| Confirm dialogs | `G20_RULE`, `USER_LOCKS` verb labels | AC-45.11, AC-46.8, AC-47.6 |
| Sticky bulk bar | Spec §Selection and bulk model, `USER_LOCKS`, `G32_RULE` | AC-47.4, AC-47.5 |
| Selection header checkbox | `SELECTION_HEADER_CONTRACT`, `G32_RULE` | AC-47.5a |
| Empty state / drop strip | `EMPTY_STATE_CONTRACT`, `G32_RULE` | AC-45.19, AC-45.19a, AC-46.14 |
| Toasts | `G35_RULE` T0–T4 + partial result | AC-47.3 |
| Focus/keyboard | `DEAD_REGION_RULE`, `Alt+↑/↓` | AC-45.2, AC-45.9, AC-46.10 |
| E2E coverage of every changed interactive element | `E2_RULE`, `BULK_CONTROL_E2E_OBLIGATION` | AC-45.15, AC-46.11, AC-47.10, AC-47.10a |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Transcript `ChannelCard` migration onto the shared primitives (incl. its G33 width-percent violation) | deferred | MEU-48 | Scheduled in `.agent/context/meu-registry.md` L134 and `build-priority-matrix.md` 10.8, which declares `MEU-47` as its dependency. Doing it now would invert the matrix order. |
| TTS page adopting the shared `ProgressBar` | deferred | MEU-48 | Same registry row (MEU-48 covers "TTS gets the shared ProgressBar"). |
| dnd-kit drag reorder + ARIA live-region announcements | deferred | MEU-49 | `build-priority-matrix.md` 10.9, dependency `MEU-48`. Phase 10 §Reorder model explicitly assigns kebab + bulk bar + `Alt+↑/↓` to MEU-45 and drag to MEU-49. |
| Row detail panel / expandable card body | out-of-scope | — | `docs/build-plan/10-queue-card-ui.md` §Card state precedence defines only the *state classes* for a detail region; no Phase 10 section defines a detail panel and no MEU in `meu-registry.md` 10.1–10.9 owns one. `DEAD_REGION_RULE` therefore removes the dead affordance rather than inventing the panel behind it. |
| Server-side `POST /{queue}/bulk` endpoint | out-of-scope | — | `10-queue-card-ui.md` §Selection and bulk model states the bulk model is client-side fan-out and that the endpoint "does not exist and may not be invented" (`BULK_ENDPOINT_POLICY`). |
| Density toggle (compact/comfortable) | out-of-scope | — | `USER_LOCKS` — Human-approved exclusion from Phase 10, 2026-08-28. |
| Adding `MOUNT_GATE_SCRIPT` to CI or the registered MEU gate in `.agent/docs/commands.md` | out-of-scope | — | `build-priority-matrix.md` 10.5–10.9 — none of the five Phase 10 rows names tooling, CI or gate-registration work; every deliverable in them is renderer behaviour. `meu-registry.md` L131–135 likewise assigns no MEU an owner for `commands.md`. Tracked instead as OQ-3 for a Phase 10-exit governance decision. |
| Local-file drop / Browse intake on the Downloader queue | out-of-scope | — | `10-queue-card-ui.md` §Scope and non-goals: Phase 10 "changes presentation and one service contract (re-queue widening); it adds no new REST surface". `DownloaderPage`'s only intake is `addFromForm()` reading `url-input` → `POST /downloads {url, quality, audio_only, audio_format}` (`DownloaderPage.tsx:156-170`), and its one `Browse` button is the **cookie-file** picker (`DownloaderPage.tsx:411`), not media. A file drop there would need an endpoint that does not exist, so `EMPTY_STATE_CONTRACT` gives that page a URL invitation instead (AC-46.14). No MEU in `meu-registry.md` 10.1–10.9 owns local-file downloading. |
| Backend/API changes of any kind | out-of-scope | — | All three build-plan sections (§Toolbar reduction, §Primary action model, §Selection and bulk model) describe renderer behaviour over existing endpoints; the domain-side work landed in MEU-42. |

---

## BUILD_PLAN.md Audit

`docs/BUILD_PLAN.md` already carries the Phase 10 row (L53) and names
`p10-queue-card-migration (MEU-45-47)` as the next project (L70). This project therefore **updates**
those rows on completion (status + the new "Next" pointer to `MEU-48-49`) and must verify no stale
reference to this project as "next/pending" survives.

```powershell
rtk proxy pwsh -NoProfile -Command { $matches=@(Select-String -Path docs/BUILD_PLAN.md -Pattern 'p10-queue-card-migration'); [pscustomobject]@{matches=$matches.Count; lines=@($matches.LineNumber)} | ConvertTo-Json -Depth 3 } *> C:/Temp/av-kit/build-plan-audit.json; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.json; exit $code
```

---

## Verification Plan

### 1. Per-MEU gate (`MEU_GATE`)

```powershell
rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/ui-typecheck.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-typecheck.txt | Select-Object -Last 20; exit $code
rtk proxy npm --prefix ui run lint *> C:/Temp/av-kit/ui-lint.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-lint.txt | Select-Object -Last 20; exit $code
rtk proxy npm --prefix ui run test *> C:/Temp/av-kit/vitest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/vitest.txt | Select-Object -Last 30; exit $code
```

### 2. Mount-completeness gate (`MOUNT_COMPLETENESS_RULE`)

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-02-p10-queue-card-migration/assert-mount-completeness.ps1 -SelfTest *> C:/Temp/av-kit/mount-gate-selftest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/mount-gate-selftest.txt | Select-Object -Last 30; exit $code
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-02-p10-queue-card-migration/assert-mount-completeness.ps1 -Scope all *> C:/Temp/av-kit/mount-gate.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/mount-gate.txt | Select-Object -Last 30; exit $code
```

### 3. E2E (`E2_RULE`, `E2E_SANDBOX`)

`ELECTRON_RUN_AS_NODE` must be unset and the bundle rebuilt first. Pass condition: ≥
`E2E_BASELINE_COUNT` tests, 0 failed, EXIT=0.

```powershell
rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/ui-build.txt; $code=$LASTEXITCODE; if($code -ne 0){Get-Content C:/Temp/av-kit/ui-build.txt | Select-Object -Last 30; exit $code}
rtk proxy npx --prefix ui playwright test *> C:/Temp/av-kit/e2e.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e.txt | Select-Object -Last 30; exit $code
```

### 3a. E2E assertion census (`E2E_ASSERTION_CENSUS_RULE`)

Run **before** the first E2E rewrite and again after the last one. The before-file is a prerequisite for
marking any E2E rewrite row `[x]`.

```powershell
rtk proxy pwsh -NoProfile -Command { @('ui/tests/e2e/download-queue.test.ts','ui/tests/e2e/convert-queue.test.ts') | ForEach-Object { $f=$_; Select-String -Path $f -Pattern 'expect\(' | ForEach-Object { "$f`:$($_.LineNumber)`:$($_.Line.Trim())" } } } *> C:/Temp/av-kit/e2e-assertion-census-before.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-assertion-census-before.txt | Measure-Object -Line; exit $code
```

### 4. Python regression (no backend change expected — proves it)

```powershell
rtk proxy uv run pytest -q *> C:/Temp/av-kit/py-full.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/py-full.txt | Select-Object -Last 20; exit $code
```

### 5. OpenAPI Drift Check

Not applicable — `packages/api/` is not modified (see Out of Scope: "Backend/API changes of any
kind"). If any MEU ends up touching `packages/api/`, that is a scope breach and the drift check
becomes mandatory.

---

## Open Questions

| ID | Question | Blocking? | Disposition |
|---|---|---|---|
| OQ-1 | `.agent/context/harness.local.md` declares `plan_to_exec_gate: reviewer-auto` (`driver: Cursor IDE`), but this session runs in Claude Code (`human`). Which governs? | No — resolved conservatively | `PLAN_TO_EXEC_GATE = "human"`, carried forward from the foundations project's explicit user decision. Reviewer `approved` will **not** auto-continue to execution; the verdict is presented and the turn ends. Flagged rather than silently resolved, per AGENTS.md §Communication Policy. |
| OQ-2 | The foundations reflection's Next Day Outline item 1 mentions Transcript, but the grouping file and `build-priority-matrix.md` place Transcript at MEU-48 (Session 22). | No | Follow the grouping + matrix (MEU-45/46/47 this session). Drift noted here so the reflection is not read as authority over the matrix. |
| OQ-3 | Should `MOUNT_GATE_SCRIPT` be promoted into the registered MEU gate in `.agent/docs/commands.md` once Phase 10 lands? | No | Out of scope for this project (see Out of Scope). Worth a governance decision at Phase 10 exit. |

---

## Research References

| Ref | Used for |
|---|---|
| `docs/build-plan/10-queue-card-ui.md` | Primary `Spec` source for every AC labeled Spec |
| `docs/build-plan/06-gui.md` §Queue Controls | The superseded 13-button contract the E2E rewrite retires |
| `.agent/docs/emerging-standards.md` G15, G20, G32–G37, E2 | `Local Canon` rules |
| `docs/execution/plans/2026-08-28-p10-queue-card-foundations/` (plan, `named-sets.json`, `assert-page-isolation.ps1`) | Carried-forward names; the gate to invert |
| `docs/execution/reflections/2026-08-28-p10-queue-card-foundations-reflection.md` | Next Day Outline items 1–2 (DEC-3, OQ-2) |
| WAI-ARIA Authoring Practices — widget roles must advertise real interactions | `DEAD_REGION_RULE` |
| `.agent/context/meu-registry.md` L131–135, `build-priority-matrix.md` 10.5–10.9 | Deferral targets in Out of Scope |
