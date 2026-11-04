---
project: 2026-09-03-p10-queue-card-dnd
date: 2026-09-03
source: docs/build-plan/10-queue-card-ui.md
meus: [MEU-49]
status: draft
template_version: 2.0
---

# Implementation Plan: Queue card drag reorder (MEU-49, Phase 10 exit)

> All sets, thresholds, labels and policies referenced below are defined exactly once in
> [`named-sets.json`](named-sets.json) and referenced BY NAME here. A literal repeated in two
> places is a defect (`$schema-note`). There are exactly two classes of exception, both
> machine-readable. Seven NAMEs are defined in an earlier Phase 10 project and are **not** redefined
> here, because a copied definition is a definition that can drift: `INHERITED_NAMES.value` lists
> each one and the file it resolves against. Five further capitalised tokens are not named sets at
> all — `ELECTRON_RUN_AS_NODE`, `PENDING`, `BUILD_PLAN`, `FAIL_TO_PASS` and `VITEST_EXIT` —
> and are listed in `INHERITED_NAMES.non_set_token_list` with the reason for each. Round 4 stopped
> asserting this and started enforcing it: `CORRECTION_CENSUS -Gate S6` fails if any capitalised
> underscore-joined token in either plan file resolves to none of the three lists, or if a universal
> claim about NAMEs appears in a paragraph carrying no qualifier (round-3 correction R3-F7).

## Goal

Add pointer drag reorder to the shared `QueueList` via `dnd-kit`, with the ARIA live-region
announcements the spec requires, while keeping the keyboard and kebab reorder paths as the equal
path. This is the last MEU of Phase 10 (`docs/build-plan/build-priority-matrix.md` 10.9), so the
project also owns the Phase 10 exit status sweep (`PHASE_EXIT_UPDATES`).

The spec is explicit that drag is an *enhancement*, not a replacement
(`docs/build-plan/10-queue-card-ui.md:254-256`, verbatim):

> **Enhancement (MEU-49):** a 6-dot drag handle at the far left on hover, via `dnd-kit`, with
> ARIA live-region announcements. Drag is an enhancement layered on the keyboard path, never the
> only path to reorder.

Landing it before Phase 11 is deliberate: MEU-55 (Transcript) adopts `QueueList`
(`.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md:134-136`, and MEU-55's dependency row at `:84` names MEU-49), so it
inherits reorder by passing one prop (`DND_OPT_IN_RULE`) instead of re-implementing it.
MEU-56 (TTS) inherits the shared `ProgressBar`, not `QueueList`
(`.agent/context/meu-registry.md:150`), so no TTS reorder inheritance is claimed.

## Context Tool Decision

```yaml
context_tool_decision:
  graphify: not_applicable
  reason: >-
    No graphify graph exists on disk for this repository, and the payload for this MEU is
    source files plus grep results - a Headroom bypass class per the Context Tool Decision Gate.
    Verified 2026-09-03: no graph artifacts under the project root.
  headroom: bypass
  headroom_reason: >-
    Exact-evidence classes only (file line anchors, dependency manifest contents, test counts).
    Compression would destroy the anchors this plan's ACs are verified against.
  sequential_thinking: used
  sequential_thinking_reason: >-
    7-thought scope pass over the drag/keyboard/file-drop three-way interaction, the
    4-value direction union limitation, and the three test-supersession candidates.
```

## Handoff Set

`HANDOFFS` (count `HANDOFF_COUNT`), matched by `HANDOFF_FILTER`, each carrying every marker in
`HANDOFF_BUNDLE_MARKERS` and the AC ids matched by `HANDOFF_AC_PATTERNS`. Enforced by
`HANDOFF_MARKER_CHECK` and `HANDOFF_AC_CHECK`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|----|------|-----------|------------------|-----------------|
| WP-1 | Dependency add + `DND_DEP_GUARD_SUPERSESSION` | — | inline | `ui/package.json`, `ui/package-lock.json`, narrowed guard |
| WP-2 | `REORDER_BODY_MODULE` extraction + `MOVE_TO_INDEX_CONTRACT` | WP-1 | isolated | `ui/src/renderer/src/lib/queue/reorder-body.ts`, re-exports, unit tests |
| WP-3 | `QueueCard` drag handle (`DND_HANDLE_CONTRACT`, `DND_HOVER_REVEAL_RULE`, `ALT_ARROW_SUPPRESSION_RULE`) | WP-1 | inline | `QueueCard.tsx`, unit tests |
| WP-4 | `QueueList` `DndContext` + announcements (`DND_ANNOUNCEMENT_CONTRACT`, `DRAG_STATE_ISOLATION_RULE`) | WP-3 | inline | `QueueList.tsx`, `queue-dnd.ts`, unit tests |
| WP-5 | Page wiring — `reorderDownloadToIndex` / `reorderConversionToIndex` | WP-2, WP-4 | inline | both `*-commands.ts`, both pages, unit tests |
| WP-6 | E2E (`E2E_DRAG_DRIVER`, `DND_LIVE_REGION_LOCATOR`) | WP-5 | isolated | `download-queue.test.ts`, `convert-queue.test.ts`, `test-ids.ts` |
| WP-7 | Phase 10 exit sweep (`PHASE_EXIT_UPDATES`) | WP-6 | inline | `meu-status.yaml`, `BUILD_PLAN.md`, `meu-registry.md` |
| WP-8 | Closeout (H1/H2) | WP-7 | inline | handoff, review, reflection, metrics |

`FRESH_WORKER` is `available` this session, so `isolated` rows (WP-2, WP-6) may be dispatched to
`av-kit-builder` / `av-kit-verifier`. This is a change from the two prior Phase 10 projects, where
`isolated` degraded to `compact_continue`.

## User Review Required

1. **OQ-3 (carried forward, must resolve at Phase 10 exit)** — whether `MOUNT_GATE_SCRIPT` is
   promoted into the registered MEU gate in `.agent/docs/commands.md`. This plan **recommends NO**
   (see Open Questions). The recommendation is executable as written; the user or the reviewer may
   overturn it without changing any other row.
2. **`PLAN_TO_EXEC_GATE` is `human`** — after the Step 5 review returns `approved`, execution does
   not begin until the user's explicit next message.

## Proposed Changes

### 1. `ui/package.json` — dependency addition

#### Boundary Inventory

Not an external-input boundary. No new write surface; no runtime input crosses a trust boundary
here. `PACKAGE_FREEZE_EXPIRY` records why the foundations-era byte-freeze on this file does not
bind MEU-49.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-49.1 | unit | `ui/package.json` `dependencies` contains exactly the three entries in `DND_PACKAGES` at those ranges, and no `@dnd-kit/react` and no virtualization package. | Spec 10-queue-card-ui.md:254 (`dnd-kit`), :47 (no virtualization dep) | Adding `react-virtual` fails the narrowed guard. |
| AC-49.2 | unit | `ui/tests/unit/queue-card.test.ts` dependency guard is narrowed to `/react-virtual/` with an in-place `MEU-49` supersession comment citing 10-queue-card-ui.md:254-256; the virtualization half still fails on a planted `react-virtual` entry. Row 2’s gate ASSERTS this per `DND_DEP_GUARD_CHECK` — all four literals plus the comment window — in **both** `Test-Deps` modes, since row 2 and not row 2a owns it (round-7 correction R6-F1: `Packages` mode never read this file, so a tree with the broad guard still in place reported zero problems). | `DND_DEP_GUARD_SUPERSESSION`, `DND_DEP_GUARD_CHECK`, `G36_RULE` | Planted `@tanstack/react-virtual` entry must still fail; and four gate fixtures cover the ways the change can be absent — `Deps/dep-guard-still-broad`, `Deps/dep-guard-deleted` (narrowing replaced by outright deletion, the `G36_RULE` violation), `Deps/dep-guard-no-supersession` and `Deps/dep-guard-comment-not-in-place`. |

#### Spec Sufficiency Table

| Behavior | Classification | Basis |
|---|---|---|
| Use `dnd-kit` | `Spec` | 10-queue-card-ui.md:34, :254 |
| Which `dnd-kit` package line | `Research-backed` | npm registry 2026-09-03; `DND_PACKAGES` note rejects the pre-1.0 `@dnd-kit/react` |
| Version pins | `Research-backed` | peer-dependency compatibility recorded in `DND_PACKAGES` |
| No virtualization dependency | `Spec` | 10-queue-card-ui.md:47 |

#### Files Modified

- `ui/package.json`, `ui/package-lock.json` (add `DND_PACKAGES`)
- `ui/tests/unit/queue-card.test.ts:807` (narrow guard; `DND_DEP_GUARD_SUPERSESSION`)

---

### 2. `ui/src/renderer/src/lib/queue/` — NEW permutation builders and the reorder gate

Today `buildReorderBody` is duplicated byte-for-byte at `convert-controls.ts:112` and
`download-controls.ts:104`. A drag needs a third variant; tripling a triplicate is the defect, so
the function moves to one owner and both call sites re-export it (`REORDER_BODY_MODULE`).

A second new module lands here for the same reason. Every reorder PUT is an **absolute**
permutation computed from the order the caller can see (`REORDER_WIRE_CONTRACT`), so two
overlapping reorders each compute a valid permutation from the same pre-mutation order and the
later response silently overwrites the earlier one. Nothing serializes them today: `run()` sets
`busy` through React state (`DownloaderPage.tsx:293-304`) and `reorder()` never reads it
(`:312-322`). `reorder-single-flight.ts` is the synchronous gate every entry point passes through
(`REORDER_SINGLE_FLIGHT_RULE`).

#### Boundary Inventory

| Write surface | Schema owner | Field constraints | Extra-field policy | Error mapping | Create/update parity |
|---|---|---|---|---|---|
| `PUT /downloads/reorder` | `ReorderIn` (`REORDER_SCHEMA_OWNER`) | `job_ids: list[str]`, a complete permutation | `extra="forbid"` (inherited from `ApiModel`) | invalid body → 422, never a downstream 500 | N/A — single absolute-replace verb, no partial-update path |
| `PUT /conversions/reorder` | `ConversionReorderIn` (`REORDER_SCHEMA_OWNER`) | same | `extra="forbid"` | 422 | N/A |

**MEU-49 adds no new boundary and changes no backend file.** The drag emits the same
`{ job_ids }` permutation the keyboard path already emits (`REORDER_WIRE_CONTRACT`); only the
client-side function that computes it gains a second entry point. The Boundary Input Contract is
therefore satisfied by existing, verified code — this table is evidence of that, not a work item.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-49.3 | unit | `buildReorderBody` lives only in `REORDER_BODY_MODULE`; `convert-controls.ts` and `download-controls.ts` re-export it, and `convertControls.buildReorderBody === downloadControls.buildReorderBody` (reference identity). | `REORDER_BODY_MODULE` (single owner) | Two copies that merely behave alike fail the identity assertion. |
| AC-49.4 | unit | All four existing directions (`up`/`down`/`top`/`bottom`) and the unknown-id branch produce byte-identical output to the pre-move implementation for a fixed 5-id fixture. | Local Canon — behaviour preservation | A changed splice bound fails. |
| AC-49.5 | unit | `buildReorderBodyToIndex(ids, movedId, targetIndex)` implements `MOVE_TO_INDEX_CONTRACT` with `targetIndex` as the FINAL index resolved against the PRE-MOVE array. Three exact-order assertions are mandatory: `[A,B,C,D]` move `A`→2 ⇒ `[B,C,A,D]`; `[A,B,C,D]` move `D`→1 ⇒ `[A,D,B,C]`; `[A,B,C]` move `A`→1 ⇒ `[B,A,C]`. Plus clamp above and below range, and unknown `movedId` → unchanged copy. | `MOVE_TO_INDEX_CONTRACT` | The forward case must assert `[B,C,A,D]` **exactly** — a remove-then-insert-at-post-removal-index implementation yields `[B,A,C,D]` and must fail. `targetIndex = 99` on a 5-item list must clamp, not throw and not drop the row. |
| AC-49.6 | unit | `buildReorderBodyToIndex` with `targetIndex` equal to the row's current index returns the identity permutation, and `reorderDownloadToIndex` / `reorderConversionToIndex` issue **no** request for it. | `MOVE_TO_INDEX_CONTRACT`, `REORDER_WIRE_CONTRACT` | A spy on `apiFetch` must record zero calls for a self-drop. |
| AC-49.7 | unit | Every pre-existing import site still resolves: `convert-commands.ts:11`, `download-commands.ts:7`, `bulk-reorder.ts:38` (`deps.buildBody`). The bulk sequential fold is unchanged. | `BULK_REORDER_ALGORITHM` carried from the migration plan | Removing a re-export fails typecheck and this test. |
| AC-49.31 | unit | NEW `ui/src/renderer/src/lib/queue/reorder-single-flight.ts` exports `createSingleFlight()` returning `{ tryAcquire, release, held }` over a plain boolean (not React state): the first `tryAcquire()` returns `true` and every subsequent call returns `false` until `release()`; `release()` without a prior acquire is a no-op; two instances are independent; `held` reflects the state synchronously **within the same tick**. | `REORDER_SINGLE_FLIGHT_RULE` | A `useState`-backed implementation cannot satisfy the same-tick assertion (two synchronous `tryAcquire()` calls would both return `true`) and fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Basis |
|---|---|---|
| Absolute permutation wire shape | `Local Canon` | `REORDER_WIRE_CONTRACT`, verified at `routes/downloads.py:210-217`, `routes/conversions.py:232-239` |
| `arrayMove` index-after-removal semantics | `Research-backed` | dnd-kit sortable `arrayMove`; recorded in `MOVE_TO_INDEX_CONTRACT` |
| Clamp instead of throw on out-of-range | `Local Canon` | mirrors the existing unknown-id defensive branch at `convert-controls.ts:112-118` |
| Suppress the PUT for an identity permutation | `Research-backed` | avoids a no-op write and a spurious list reconcile; stated in `MOVE_TO_INDEX_CONTRACT` |
| `targetIndex` is the FINAL index resolved against the pre-move array | `Research-backed` | dnd-kit sortable's documented pattern — `oldIndex` and `newIndex` are both found in the original array and passed to `arrayMove` unchanged; pinned with worked examples in `MOVE_TO_INDEX_CONTRACT` (round-1 correction F2) |
| One synchronous gate serializes every reorder entry point | `Local Canon` | forced by `REORDER_WIRE_CONTRACT`'s absolute-permutation shape; the absence of any existing serialization verified at `DownloaderPage.tsx:293-322` and `ConvertPage.tsx:354-385` (round-1 correction F1) |

#### Files Modified

- **NEW** `ui/src/renderer/src/lib/queue/reorder-body.ts`
- **NEW** `ui/src/renderer/src/lib/queue/reorder-single-flight.ts` (framework-free store; no React import)
- **NEW** `ui/src/renderer/src/lib/queue/use-queue-reorder-held.ts` (`REORDER_HELD_HOOK` — the only React binding over that store)
- `ui/src/renderer/src/features/converter/convert-controls.ts` (delete body, re-export)
- `ui/src/renderer/src/features/downloader/download-controls.ts` (delete body, re-export)
- **NEW** `ui/tests/unit/reorder-body.test.ts`
- **NEW** `ui/tests/unit/reorder-single-flight.test.ts`

---

### 3. `ui/src/renderer/src/components/queue/QueueCard.tsx` — drag handle

#### Boundary Inventory

Not an external-input boundary — props only, all typed.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-49.8 | unit | When drag is enabled the card renders `DND_TESTIDS[0]` as the FIRST child of the card container: the canonical `Button` (`variant="ghost" size="sm" icon`), which resolves to a real `<button type="button">` carrying the `btn-ghost` marker class, accessible name `Reorder <job title>`, dnd-kit's `attributes` and `listeners`, and `setActivatorNodeRef` passed as `ref` (forwarded at `Button.tsx:37-50` onto the element at `:62-68`). | `DND_HANDLE_CONTRACT`, `G34_RULE`, Spec :254 | A `<div role="button">` fails the tag assertion; a bare `<button>` fails the `btn-ghost` marker-class assertion. |
| AC-49.9 | unit | The handle is a SIBLING of the checkbox, activatable region, primary action and kebab — never a descendant of the activatable region and never an ancestor of any of them. | `DND_HANDLE_CONTRACT`, QueueCard.tsx:1-13, WCAG 2.2 SC 4.1.2 | A handle wrapping the title region fails the containment assertion. |
| AC-49.10 | unit | The handle's className carries `opacity-0` plus `group-hover:`, `group-focus-within:` and `focus-visible:` opacity transitions **and `touch-none`**, and contains none of `hidden`, `aria-hidden`, `display:none`, `touch-auto`, `touch-pan-y`, or an animated `w-`/`h-`/`top-`/`left-`/`margin`/`box-shadow` property. | `DND_HOVER_REVEAL_RULE`, `DND_TOUCH_ACTION_RULE`, `G33_RULE` | `hidden group-hover:block` fails; omitting `touch-none` fails, which is the only unit-level guard against a touch drag being stolen by native scrolling. |
| AC-49.11 | unit | With drag disabled (`DND_OPT_IN_RULE`) the card renders no handle, no `DND_TESTIDS` node and no dnd attributes — the DOM matches the pre-MEU snapshot. | `DND_OPT_IN_RULE` | An always-mounted handle fails on the transcript/tts fixtures. |
| AC-49.12 | unit | While `isDragging` is true, `Alt+ArrowUp` and `Alt+ArrowDown` on the card do NOT call `onMoveUp`/`onMoveDown`; with `isDragging` false they still do, and `isFirst`/`isLast` guards are unchanged. | `ALT_ARROW_SUPPRESSION_RULE` | Firing Alt+ArrowUp mid-drag must record zero `onMoveUp` calls. |
| AC-49.13 | unit | The handle uses the canonical `Button` with an existing variant/size pair (`ghost` / `sm`, `icon`) and introduces no sixth variant and no fourth size; `Button.tsx:14,22` are unchanged and the card stays inside the frozen 5×3 maps. | `G34_RULE` | A `variant="drag"`, a new `sizeClasses` entry, or a bare `<button>` with ad-hoc padding all fail. |

#### Spec Sufficiency Table

| Behavior | Classification | Basis |
|---|---|---|
| 6-dot handle, far left, on hover | `Spec` | 10-queue-card-ui.md:254 |
| Handle must be a focusable `<button>` | `Research-backed` | dnd-kit `setActivatorNodeRef` docs (focus restoration after keyboard drag) + WCAG 2.2 SC 2.1.1; a non-focusable handle makes the spec's own announcements unreachable |
| "On hover" implemented as opacity, not display | `Research-backed` | WCAG 2.2 SC 2.4.7 + `G33_RULE`; recorded in `DND_HOVER_REVEAL_RULE` |
| Sibling-not-descendant zone rule | `Local Canon` | `QueueCard.tsx:1-13` docstring |
| `touch-action: none` on the activator | `Research-backed` | dnd-kit PointerSensor docs — a touch drag inside a scrollable list is claimed by native scrolling unless the activator disables `touch-action`; `preventDefault` on the initiating touchmove is not reliable under Pointer Events (`DND_TOUCH_ACTION_RULE`, round-1 correction F3) |
| Alt+Arrow suppression during drag | `Research-backed` | stale-base permutation clobber; `ALT_ARROW_SUPPRESSION_RULE` |

#### Files Modified

- `ui/src/renderer/src/components/queue/QueueCard.tsx`
- `ui/tests/unit/queue-card.test.ts`

---

### 4. `ui/src/renderer/src/components/queue/QueueList.tsx` — `DndContext` and announcements

`QueueList.tsx:120,130` already spreads `useDropZone` handlers and `data-drag-state` onto the list
container, and `:166-177` renders `queue-drop-overlay` with `role="status"`. `DndContext` is placed
as a **wrapper around** that container rather than merged into it, so neither prop set is
displaced — and because dnd-kit is pointer-events-only while the drop zone is HTML5-drag-based,
the isolation is provable rather than assumed (`DRAG_STATE_ISOLATION_RULE`).

#### Boundary Inventory

Not an external-input boundary — props only.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-49.14 | unit | With `onMoveToIndex` undefined, `QueueList` renders no `DndContext`, no `SortableContext`, no handle and no live region; the rendered DOM is byte-identical to the pre-MEU output for the same props. | `DND_OPT_IN_RULE` | Unconditional `DndContext` fails the byte-identity assertion. |
| AC-49.15 | unit | With `onMoveToIndex` defined, `SortableContext` receives the item ids in render order, and re-rendering with a changed `items` array updates that id list. | `DND_OPT_IN_RULE` | A stale id list fails after a queue update. |
| AC-49.16 | unit | The `announcements` object passed to `DndContext` defines all four of `onDragStart`, `onDragOver`, `onDragEnd`, `onDragCancel`, and `screenReaderInstructions` is non-empty. | `DND_ANNOUNCEMENT_CONTRACT`, Spec :255 | Omitting `onDragCancel` fails. |
| AC-49.17 | unit | Each announcement string is POSITION-based and 1-INDEXED and names the job title (e.g. `Moved "Foo" to position 3 of 7`); none contains a 0-based index; `onDragCancel` states the item returned to its starting position. | `DND_ANNOUNCEMENT_CONTRACT` | `position 2 of 7` for the third of seven rows fails. |
| AC-49.18 | unit | `onDragEnd` over a different row calls `onMoveToIndex(activeId, targetIndex)` exactly once with `arrayMove` index semantics; a drop on itself and `onDragCancel` call it zero times. | `MOVE_TO_INDEX_CONTRACT` | A self-drop that fires the callback fails. |
| AC-49.19 | unit | While a row drag is active the list container's `data-drag-state` is `idle` and `queue-drop-overlay` is absent; a simulated file `dragenter` still sets the drop state and still renders the overlay. | `DRAG_STATE_ISOLATION_RULE` | Merging `DndContext` into the drop-zone container fails one direction or the other. |
| AC-49.20 | unit | Row displacement comes from dnd-kit's `transform`/`transition` (via `CSS.Transform.toString`), never from `top`/`left`/`margin`. | `G33_RULE` | An inline `top:` offset fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Basis |
|---|---|---|
| ARIA live-region announcements | `Spec` | 10-queue-card-ui.md:255 |
| Position-based, not index-based, wording | `Research-backed` | dnd-kit accessibility docs; `DND_ANNOUNCEMENT_CONTRACT` |
| All four announcement handlers | `Research-backed` | dnd-kit `Announcements` type; omitting `onDragCancel` leaves Escape unconfirmed for screen-reader users |
| Opt-in placement on `QueueList` (not the pages) | `Local Canon` | `DND_OPT_IN_RULE`; this is what lets MEU-55/56 inherit reorder |
| Sensor activation constraint | `Research-backed` | `DND_SENSOR_CONFIG` — prevents drag activation from stealing clicks on the card's other controls |
| Drag/file-drop isolation | `Local Canon` + `Research-backed` | `DRAG_STATE_ISOLATION_RULE` |

#### Files Modified

- `ui/src/renderer/src/components/queue/QueueList.tsx`
- **NEW** `ui/src/renderer/src/components/queue/queue-dnd.ts` (announcement factory +
  `screenReaderInstructions`, exported so unit tests assert the strings directly per
  `JSDOM_RECT_RULE`)
- **NEW** `ui/tests/unit/queue-dnd.test.ts` — the announcement-string and
  `screenReaderInstructions` assertions (AC-49.16, AC-49.17). These live in their **own** file,
  not in `queue-primitives.test.ts`, because they import the not-yet-created `queue-dnd` module:
  a missing module aborts collection for the whole file it is imported from
  (`VITEST_COLLECTION_FAILURE_SHAPE`), which would silently subtract
  `queue-primitives.test.ts`'s existing cases from `numTotalTests` and break the Red oracle's
  own baseline clause. A NEW file contributes 0 to `VITEST_BASELINE_COUNT`, so the subtraction is
  zero. Round-3 correction R3-F2.
- `ui/tests/unit/queue-primitives.test.ts`

---

### 5. Page wiring — both queue pages

#### Boundary Inventory

Covered by §2's table — the same two endpoints, no new surface.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-49.21 | unit | `download-commands.ts` exports `reorderDownloadToIndex(ids, movedId, targetIndex)` and `convert-commands.ts` exports `reorderConversionToIndex`, each building the body with `buildReorderBodyToIndex` and issuing one `PUT` to its endpoint, then reconciling once — mirroring the existing `reorderDownload` shape at `download-commands.ts:381-410`. | `COMMAND_MODULE_RULE`, `REORDER_WIRE_CONTRACT` | Inline `apiFetch` in a page `onClick` fails the command-module assertion. |
| AC-49.22 | unit | Both pages pass `onMoveToIndex` to `QueueList` wired to their own command; a failed PUT surfaces through the page's existing error path and does not leave the list optimistically reordered. | `COMMAND_MODULE_RULE`, `NO_DEAD_CONTROL_RULE` | A swallowed rejection fails. |
| AC-49.23 | unit (**preservation**) | The kebab reorder items (`Move up` / `Move down` / `Move to top` / `Move to bottom`) and the Alt+Arrow path are still present and still call their existing commands on a page that also has drag. | `WCAG_DRAG_RULE`, Spec :57 | Removing a kebab item fails, proving the single-pointer alternative survives. |

> **AC-49.11, AC-49.14, AC-49.23 and AC-49.39 are preservation criteria** (`RED_PHASE_PRESERVATION_ACS`). Each asserts that behaviour which is already on the tree when task row 3 begins is still there afterwards, so each PASSES by construction. They are therefore excluded from `RED_PHASE_REQUIRED_ACS` — demanding that they fail in the Red phase would demand a regression. `RED_PHASE_ORACLE` still requires them to be **written** (its `-Census` clause scans `RED_PHASE_REQUIRED_ACS` + `RED_PHASE_PRESERVATION_ACS`, so a missing preservation test is caught) and its self-test rejects any overlap between the two sets. Round-3 correction R3-F2; AC-49.39 joined the set as execution-phase correction **X1** (see §Execution-Phase Corrections).
| AC-49.24 | unit | `DND_TESTIDS` is registered in `ui/tests/e2e/test-ids.ts` and the registry test covers it. | `E2E_LOCATOR_FORM` | An unregistered testid fails the registry test. |
| AC-49.32 | unit | Every reorder entry point on a page — kebab `Move up`/`down`/`top`/`bottom`, Alt+Arrow, and drag `onMoveToIndex` — calls `tryAcquire()` before it reads `items` or builds a body. With `apiFetch` stubbed by a **deferred promise**, an in-flight Alt+Arrow reorder followed immediately by a drag drop issues exactly **one** PUT; after the first promise resolves and the list reconciles, a second drag issues its own PUT. | `REORDER_SINGLE_FLIGHT_RULE`, `REORDER_WIRE_CONTRACT` | Removing the gate makes the same sequence issue **two** PUTs whose bodies are both computed from the same pre-mutation order — the exact stale-base clobber. The test asserts the call count, not just the final list. |
| AC-49.33 | unit | The bulk reorder fold holds the gate for the **whole** sequence: a drag drop attempted while a bulk reorder is mid-fold issues zero PUTs, and the bulk fold's own N requests are unaffected. The gate is acquired and released inside `use-queue-bulk.ts`'s `moveSelected` (`:93,:96-107`), which returns `void` and therefore cannot hand a release token to its caller — the ownership follows from the existing signature, not from preference. Both completion orders are asserted: the fold resolving before the blocked drag is retried, **and** the blocked drag arriving after `refetch()` has already resolved but before `clear()` has run. | `REORDER_SINGLE_FLIGHT_RULE`, `BULK_REORDER_ALGORITHM` | A gate acquired per-request inside the fold lets a drag interleave between two bulk PUTs and fails. A gate released before `refetch()` resolves lets the retried drag compute its body from the pre-fold order — the same stale-base clobber one level up — and fails the second ordering. |
| AC-49.34 | unit | `release()` runs in a `finally`: after a **rejected** reorder PUT the error surfaces through the page's existing error path **and** the next reorder still acquires the gate and issues its PUT. | `REORDER_SINGLE_FLIGHT_RULE`, `REORDER_FEEDBACK_TIER` | Releasing only on the success path deadlocks every later reorder after one failure — the test must prove the second attempt still fires. |
| AC-49.35 | unit | While the gate is held, every rendered drag handle is `disabled`; when it is released they are enabled again — **without a remount**. The held flag reaches the card through `useQueueReorderHeld(key)` from `REORDER_HELD_HOOK` (`useSyncExternalStore` over `REORDER_SINGLE_FLIGHT_RULE`'s module-level registry), so a gate taken by *another* card's kebab still disables *this* card's handle. The hook lives in its own module, not in `reorder-single-flight.ts`: the store is imported by the plain-TS command modules, which have no React import and must not acquire one (round-6 correction R5-F1). | `REORDER_FEEDBACK_TIER`, `REORDER_SINGLE_FLIGHT_RULE`, `REORDER_HELD_HOOK` | A handle that stays enabled but silently no-ops is an invisible dead control and fails. So does a page-local `useState` mirror of the gate: it is not written by the other card's acquire, so the assertion that a sibling's acquire disables this handle fails — which is the round-5 R4-F3 defect, a rendered consequence asserted for a state no component could observe. |
| AC-49.37 | unit | The gate's lifetime is the **queue**, not the component. `acquireQueueReorder(key)` reads a MODULE-LEVEL map keyed by `REORDER_QUEUE_KEYS`: unmounting and remounting the downloader page while a reorder PUT is still on the wire does NOT hand the next caller a free gate, and the release from the in-flight request still frees it for the remounted tree. Independently, holding the `download` gate leaves the `convert` gate acquirable. | `REORDER_SINGLE_FLIGHT_RULE` | A gate held in a `useRef` dies with the unmounting component while its PUT is still in flight, so the remounted page acquires freely and issues a second absolute-permutation body computed from the pre-mutation order — the F1 clobber, reachable by a route change. A single global boolean instead of a per-key map fails the cross-queue half. |
| AC-49.38 | unit | Feedback parity while the gate is held: **every reorder affordance that is present** is visibly inert, not just the drag handle. Asserted on **two** cards in the same list, because the menu's contents are position-dependent: on a **middle** card all four kebab reorder items (`Move up` / `Move down` / `Move to top` / `Move to bottom`) render `disabled`; on the **first** card exactly `Move down` and `Move to bottom` are present and both render `disabled`, while `Move up` and `Move to top` remain **absent** — not disabled. Alt+ArrowUp / Alt+ArrowDown issue zero PUTs on the same guard. When the gate is released every present item is live again. | `REORDER_FEEDBACK_TIER`, `NO_DEAD_CONTROL_RULE`, `WCAG_DRAG_RULE`, `QueueCardMenu.tsx:1-13` rule 1 | Disabling only the handle leaves the kebab and keyboard paths looking live while they silently no-op — three invisible dead controls, and precisely the single-pointer/keyboard alternative WCAG 2.2 SC 2.5.7 requires to remain trustworthy. The two-card form is also a negative test against the round-4 wording, which demanded four disabled items unconditionally: that is unsatisfiable on a boundary row **and** contradicts the component it constrains, whose rule 1 is “Unavailable actions are absent, never disabled” (the builder pushes `move-up`/`move-top` only `if (!isFirst && handler !== undefined)`). An implementation that disables all four everywhere fails the first-card half; one that only disables the handle fails both. |
| AC-49.39 | unit | The `G37_RULE` migration is complete, not partial, and the check is the **outcome** rather than a proxy for it. (i) `ui/tests/unit/helpers/user-event.ts` **does not exist** and no file under `ui/` imports `helpers/user-event`. (ii) **Mount half, all 14 `TL_MIGRATION_FILES`:** each imports `@testing-library/react`, calls `render(`, queries through `screen`, and retains **none** of the retired surface — no `react-dom/client` specifier, no `createRoot`, no `act` imported from `'react'`. (`createElement` is untouched and still allowed: these are `.test.ts` files with no JSX, so `render(createElement(C, props))` is the idiomatic RTL form here.) (iii) **Interaction half, the 13 `TL_INTERACTION_FILES`:** each additionally imports `@testing-library/user-event` and calls `userEvent.setup()`; the one `TL_MOUNT_ONLY_FILES` entry is exempt **by registration**, and the two sets must partition `TL_MIGRATION_FILES` exactly in both directions. (iv) All four `TESTING_LIBRARY_PACKAGES` appear in `ui/package.json` **devDependencies** at their registered ranges. | `TESTING_LIBRARY_ADOPTION`, `G37_RULE`, `TL_MIGRATION_FILES`, `TL_INTERACTION_FILES`, `TL_MOUNT_ONLY_FILES` | A half-migration fails, and so does the specific **false pass** round 5 shipped (correction R5-F3): a file that keeps its `createRoot` mount, adds one no-op `userEvent.setup()`, and changes nothing else satisfied the round-5 gate *and* the exactly-439 count while delivering no migration at all. Clause (ii) is what makes the recode observable; self-test case `Deps/tl-old-style-retained` is that exact tree and must now fail. Forcing `userEvent.setup()` into the mount-only file would have been the mirror defect — a gate satisfied by dead ceremony — which is why the exemption is registered rather than assumed. |

#### Spec Sufficiency Table

| Behavior | Classification | Basis |
|---|---|---|
| Mutations live in the commands module | `Local Canon` | `COMMAND_MODULE_RULE` |
| Kebab + keyboard remain the equal path | `Spec` | 10-queue-card-ui.md:57 |
| Single-pointer alternative is mandatory | `Research-backed` | WCAG 2.2 SC 2.5.7; `WCAG_DRAG_RULE` |
| No new `gui-actions-index.md` row | `Local Canon` | `GUI_ACTIONS_INDEX_NON_CHANGE` |
| Feedback tier for the drag mutation | `Local Canon` | `REORDER_FEEDBACK_TIER` — the canonical T0–T4 table (`docs/gui-element-reference.md` §4) does not exist (`GUI_ENFORCEMENT_FALLBACK`), so the tier is taken from the live precedent for the same mutation class at `DownloaderPage.tsx:293-322` / `ConvertPage.tsx:354-385` (round-1 correction F6/G35) |

#### Files Modified

- `ui/src/renderer/src/features/downloader/download-commands.ts`,
  `ui/src/renderer/src/features/downloader/DownloaderPage.tsx:673` (plus the single-flight gate
  around `reorder()` at `:312-322` and the bulk reorder fold)
- `ui/src/renderer/src/features/converter/convert-commands.ts`,
  `ui/src/renderer/src/features/converter/ConvertPage.tsx:844` (same gate, `:354-385`)
- `ui/src/renderer/src/lib/queue/use-queue-bulk.ts` — `moveSelected` (`:93,:96-107`) acquires the
  queue gate before the fold and releases it in a `finally` after `refetch()` resolves; the hook
  gains a required `queueKey` option (`REORDER_QUEUE_KEYS`) so the gate it takes is the same one
  the page's drag and kebab paths take (AC-49.33, AC-49.37)
- `ui/src/renderer/src/components/queue/QueueCardMenu.tsx` — the item model gains an
  optional `disabled?: boolean` and the rendered control honours it. Rule 1 of its docblock
  (`:1-13`, “Unavailable actions are absent, never disabled”) is **preserved, not amended**:
  absence keeps meaning “impossible from this row” (first row has no `Move up`), while
  `disabled` means “possible, but not right now” — a distinct state the component could
  not previously express, which is why AC-49.38 asserts both a middle and a boundary card
- `ui/src/renderer/src/components/queue/QueueCard.tsx`,
  `ui/src/renderer/src/components/queue/QueueList.tsx` — read `useQueueReorderHeld(key)`
  from `REORDER_HELD_HOOK` and pass the held flag to the handle and the menu (AC-49.35,
  AC-49.38)
- `ui/tests/e2e/test-ids.ts`
- `ui/tests/unit/downloader-page.behavior.test.ts`, `ui/tests/unit/convert-page.behavior.test.ts`
- **`TL_MIGRATION_FILES` (14 unit test files)** — all 14 recoded onto `render`/`screen`
  from `@testing-library/react`, and the 13 `TL_INTERACTION_FILES` onto
  `userEvent.setup()` as well (the one `TL_MOUNT_ONLY_FILES` entry simulates nothing and
  is registered as exempt); `ui/tests/unit/helpers/user-event.ts` is **deleted**; `ui/package.json`
  gains `TESTING_LIBRARY_PACKAGES` in `devDependencies` and a `setupFiles` entry importing
  `@testing-library/jest-dom/vitest` (`TESTING_LIBRARY_ADOPTION`, AC-49.39). Four of those 14
  are already in this MEU's own change set, so the net new files here are the other ten

---

### 6. E2E — real drag against real Electron

`JSDOM_RECT_RULE` states why the completed drag is proved here and not in jsdom.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-49.25 | integration | On a downloader queue seeded with a known 4-row order `[A,B,C,D]`, dragging `A`'s handle onto row 3 (`C`) via `E2E_DRAG_DRIVER` produces the **exact** rendered order `[B,C,A,D]`, and that exact order survives a reload. | `E2_RULE`, `MOVE_TO_INDEX_CONTRACT`, Spec :254 | The assertion is the exact 4-id sequence, not "the order changed": `[B,A,C,D]` (post-removal-index bug) and the unchanged `[A,B,C,D]` (drag never activated, e.g. via `locator.dragTo()`) must both fail. |
| AC-49.26 | integration | During and after that drag, `[id^="DndLiveRegion"]` (`DND_LIVE_REGION_LOCATOR`) contains a position-based announcement naming the dragged title. | `DND_ANNOUNCEMENT_CONTRACT`, Spec :255 | A `role=status` locator is ambiguous with `queue-drop-overlay` and is forbidden. |
| AC-49.27 | integration | Keyboard drag: focus the handle, `Space` to lift, `ArrowDown`, `Space` to drop — the order changes and focus returns to the handle on the moved row. | `DND_HANDLE_CONTRACT`, `DND_SENSOR_CONFIG` | A non-focusable handle cannot be reached by Tab and fails here. |
| AC-49.28 | integration | Throughout a row drag on the downloader page, the list container's `data-drag-state` stays `idle` and `queue-drop-overlay` never appears. | `DRAG_STATE_ISOLATION_RULE` | A merged context shows the file-drop overlay mid-drag. |
| AC-49.29 | integration | The same drag on a convert queue seeded `[A,B,C,D]` produces the exact order `[B,C,A,D]`, proving the wiring is per-page and not downloader-only. | `E2_RULE`, `MOVE_TO_INDEX_CONTRACT` | An unchanged order (the convert page never received `onMoveToIndex`) and `[B,A,C,D]` must both fail — the same exact-sequence assertion as AC-49.25, never a weaker "changed" check. |
| AC-49.30 | integration | The full Playwright suite, invoked via `E2E_RUN_COMMAND`, passes with the runtime case count ≥ `E2E_BASELINE_COUNT` **and** the static `test(`-declaration count ≥ `E2E_STATIC_CASE_FLOOR`; both floors are asserted by the gate, not read by eye. `ui/tests/e2e/transcript-queue.test.ts` and `tts-generate.test.ts` are untouched and green (`DND_OPT_IN_RULE`). | `E2_RULE`, `E2E_RUN_COMMAND`, `G36_RULE` | A dropped assertion lowers either count and fails. Invoking the suite as `npx --prefix ui playwright test` reports 0 tests and exits 1 — that form is forbidden by `E2E_RUN_COMMAND`. |
| AC-49.36 | integration | On the rendered Electron page, `getComputedStyle(handle).touchAction === 'none'` for every drag handle. | `DND_TOUCH_ACTION_RULE` | A handle resolving to `auto` or `pan-y` fails — the mouse driver alone cannot expose this, which is why the computed style is asserted directly. |

#### Spec Sufficiency Table

| Behavior | Classification | Basis |
|---|---|---|
| GUI change requires E2E | `Local Canon` | `E2_RULE` |
| `page.mouse` over `dragTo()` | `Research-backed` | `E2E_DRAG_DRIVER` |
| Live-region locator form | `Research-backed` | `DND_LIVE_REGION_LOCATOR` |
| E2E is not `[B]` in this sandbox | `Local Canon` | `E2E_SANDBOX` |

#### Files Modified

- `ui/tests/e2e/download-queue.test.ts`, `ui/tests/e2e/convert-queue.test.ts`

---

## GUI Element Compliance Check (create-plan §4A)

`GUI_ENFORCEMENT_FALLBACK` — the three enforcement documents `create-plan.md` §4A cites
(`.agent/docs/gui-standards-enforcement.md`, `docs/gui-element-reference.md`,
`docs/gui-button-index.md`) do not exist in this repository (re-verified 2026-09-03). The check is
therefore executed against the on-disk substitutes and the mapping table is recorded inline here,
as eight prior Phase 6–10 plans have done.

| Element | Action id | Registered? | Standard | Verified against | Verdict |
|---|---|---|---|---|---|
| Drag handle (downloader row) | `download:reorder` | Yes — `docs/build-plan/gui-actions-index.md:25` (`Drag row`, `PUT /downloads/reorder`) | G32, G33, G34, WCAG 2.5.7 / 2.4.7 / 4.1.2 | `GUI_ACTIONS_INDEX_NON_CHANGE` | **Satisfies an existing row — no new index row.** |
| Drag handle (convert row) | `convert:reorder` | Yes — `gui-actions-index.md:63` (`Drag / up-down`, `PUT /conversions/reorder`) | same | `GUI_ACTIONS_INDEX_NON_CHANGE` | **Satisfies an existing row.** |
| Drag handle (transcript row) | `transcript:reorder` | Yes — `gui-actions-index.md:41` | same | Out of Scope table | Deferred to MEU-55 by `DND_OPT_IN_RULE`. |
| dnd live region | — | Not an action — dnd-kit-owned DOM | Spec :255 | `DND_LIVE_REGION_LOCATOR` | No index row applies. |

**Standards verification:**

- **G32** (`G32_RULE`, no raw hex in `className`) — the handle uses token classes only
  (`text-fg-muted`, `hover:text-fg`); asserted by the existing `queue-card.test.ts` standards
  sweep, which scans every `className` line in the queue package.
- **G33** (`G33_RULE`) — the reveal animates `opacity` only (`DND_HOVER_REVEAL_RULE`, AC-49.10) and
  row displacement uses dnd-kit's `transform`/`transition` (AC-49.20). No `width`/`height`/`top`/
  `left`/`margin`/`box-shadow` is animated. Durations come from the existing
  `--duration-fast: 120ms` / `--ease-out` tokens in `ui/src/renderer/src/styles.css:61-66`; no
  `duration-[…]` without `var(…)`, which the standards sweep also rejects.
- **G34** (`G34_RULE`) — `ui/src/renderer/src/components/ui/Button.tsx:14,22` holds the frozen
  5-variant × 3-size maps. The handle **is** the canonical `Button` at `variant="ghost" size="sm"
  icon`: `Button` already forwards its ref to the underlying element (`Button.tsx:37-50`) and
  spreads `...rest` onto it (`:62-68`), so `setActivatorNodeRef`, dnd-kit `attributes`/`listeners`
  and the testid all pass through without a bare `<button>` and without a sixth variant
  (AC-49.8, AC-49.13). *(Round-1 correction F6 — the earlier bare-`<button>` design waived G34
  with no source-backed exception.)*
- **G35** (`REORDER_FEEDBACK_TIER`) — a drag drop is a state-changing action, so it gets an
  explicit tier rather than a waiver. `docs/gui-element-reference.md` §4 (the T0–T4 table G35
  cites) does not exist here — `GUI_ENFORCEMENT_FALLBACK` — so the tier is assigned from the live
  precedent for the same mutation class (`DownloaderPage.tsx:293-322`, `ConvertPage.tsx:354-385`):
  page `busy` for the duration, error banner on rejection with no optimistic reorder left behind,
  one reconcile from the PUT response, and handles rendered `disabled` while the single-flight
  gate is held (AC-49.34, AC-49.35). *(Round-1 correction F6.)*
- **G36** (`G36_RULE`) — the only edit to an existing assertion is `DND_DEP_GUARD_SUPERSESSION`
  (narrowed, not deleted, with the virtualization half still armed). No `.skip`/`.only`/`.todo`.
- **G37** (`G37_RULE`) — **met literally, not by intent.** MEU-49 installs
  `TESTING_LIBRARY_PACKAGES` (`@testing-library/react`, `@testing-library/user-event`, their
  explicit `@testing-library/dom` peer, and `jest-dom` for the matchers), **deletes**
  `ui/tests/unit/helpers/user-event.ts`, and recodes the 14 `TL_MIGRATION_FILES` onto
  `render`/`screen` + `userEvent.setup()`. After this MEU the canonical sentence
  “Use `userEvent.setup()`” has a real referent in this package and every interaction call
  site is the canonical one; `fireEvent` remains at zero call sites, where it already was.

  Rounds 1–4 got this wrong twice in opposite directions and both are corrected. Round 1
  labelled the waiver `Human-approved` with no approval on disk (rejected as R3-F3). Round 4
  withdrew that label but kept the waiver, arguing scope from a measured-sounding number that
  was false: it claimed **all 54** unit files use the local helper. Five do
  (`bulk-action-bar`, `queue-card`, `queue-list`, `queue-primitives`, `queue-toolbar`); the
  real migration surface is the **14** files that mount a React tree, and 40 files are pure
  logic that never touch the DOM. R4-F5 caught that, and the recommendation resting on it
  fell with it.

  Three facts now point the same way. The helper's own docstring
  (`ui/tests/unit/helpers/user-event.ts:4-7`) states it exists **only** because
  `ui/package.json` was byte-frozen by `PAGE_ISOLATION_RULE`'s `FROZEN_GLOBS` in
  MEU-45–47 — and MEU-49 already unfreezes both manifests to add `DND_PACKAGES`
  (`PACKAGE_FREEZE_EXPIRY`), so the exception has expired on its own stated terms. The blast
  radius fits inside this MEU. And deferring would have meant writing MEU-49's own new drag
  and keyboard interaction tests against a shim scheduled for deletion one session later —
  code written to be thrown away.

  The approach is not invented here. React Testing Library's own docs, the `user-event` v14
  docs and the dnd-kit maintainers' testing guidance converge on one stack: `render`/`screen`
  with `userEvent.setup()` per test, every method awaited, and **no** explicit `act()` wrapper
  (v14 handles it internally). `@testing-library/dom` is declared **explicitly** rather than
  left to hoisting because both `react@16` and `user-event@14` list it as a *peer*, not a
  dependency. *(`Human-approved` — user direction 2026-09-04, “No splits … if the code
  needs to be replaced it can simply be removed and recoded into better shape”; round-5
  correction R4-F5. **OQ-5 is closed**, not carried.)*
- **E2** (`E2_RULE`) — six E2E acceptance criteria (AC-49.25–49.30) cover every interactive
  affordance this MEU introduces, on both pages.
- **WCAG 2.2 SC 2.5.7** (`WCAG_DRAG_RULE`) — the single-pointer alternative (kebab reorder items)
  is asserted still present and still functional by AC-49.23.
- **WCAG 2.2 SC 2.4.7 / 2.1.1** — the handle is a real focusable `<button>` with a visible
  `focus-visible` state and is never `display:none` (AC-49.8, AC-49.10).
- **WCAG 2.2 SC 4.1.2** — the handle is a sibling of the card's other zones, never nested inside the
  activatable region (AC-49.9), preserving `QueueCard.tsx:1-13`'s rule.
- **`DEAD_REGION_RULE`** — unchanged; the handle is a control that does something, and when drag is
  not enabled it is not rendered at all (AC-49.11), so no focusable no-op is introduced.

The existing `ui/tests/unit/gui-actions-audit.test.ts` cross-checks `gui-actions-index.md` against
the codebase and must stay green — since no index row is added, it needs no change.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| List virtualization / any `react-virtual` dependency | Deferred | none — revisited above 200 rows, no MEU allocated | Spec 10-queue-card-ui.md:47 ("No new dependency this phase; revisit above 200 rows"). This is a spec-stated threshold, not an orphan deferral: the trigger is a measured row count, not a date. |
| Drag reorder on the Transcript queue | Deferred | MEU-55 | MEU-55 adopts `QueueList` for the Transcript channel cards and inherits reorder; `DND_OPT_IN_RULE` makes it a one-prop change. Source: `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md:134-136`, with MEU-55's dependency row (`:84`) naming MEU-49. |
| Drag reorder on the TTS queue | Not planned | none | MEU-56 (`gui-tts-layout`) inherits the shared `ProgressBar`, not `QueueList` (`.agent/context/meu-registry.md:150`), so no reorder follows from it. Phase 11's spec file `docs/build-plan/11-page-layout.md` does not exist yet — MEU-50 authors it (`docs/BUILD_PLAN.md:36`) — so there is no specified TTS reorder behaviour to defer. |
| Cross-list drag (moving a job between queues) | Not planned | none | No spec, no `gui-actions-index.md` row, no backend verb. Raising it would be inventing product behaviour. |
| Multi-row drag (dragging a selection) | Not planned | none | Same — the selection model's bulk reorder verbs already cover the capability via `BULK_REORDER_ALGORITHM`. |
| Promoting `MOUNT_GATE_SCRIPT` into `.agent/docs/commands.md` | Decision | resolved here | OQ-3 below. |

## BUILD_PLAN.md Audit

MEU-49 is the last MEU of Phase 10, so this project owns the phase-exit sweep. Required edits,
enumerated in `PHASE_EXIT_UPDATES`:

- `docs/BUILD_PLAN.md:36` — "Phase 10 queue cards executed through MEU-47; MEU-49 remains." → Phase 10 complete.
- `docs/BUILD_PLAN.md:54` — the Phase 10 status row `🟡 In Progress (… MEU-49 pending session 22.)` → `✅ Complete`.
- `docs/BUILD_PLAN.md:72` — "Next: `p10-queue-card-dnd (MEU-49)`, then Phase 11 sessions 23–26." → Next is Phase 11 / MEU-50.
- `.agent/context/meu-registry.md:135` — MEU-49 `⬜ pending` → complete.

The registry and the BUILD_PLAN status table are **generated** from `.agent/context/meu-status.yaml`
by `tools/meu_status.py render`. The task table therefore edits the YAML and renders; it never
hand-edits the generated files. `render --check` is the drift gate.

No new build-plan section is authored by this MEU — `docs/build-plan/10-queue-card-ui.md` already
specifies the work at :34, :45, :57 and :249-256, and `CANON_CLAUSE_NON_CHANGE` records why its
non-goal row is deliberately left as written.

## Verification Plan

Every command below is a real, verified command (`ABSENT_VALIDATOR_RULE`). Each runs as its own
receipt under `VALIDATION_RECEIPT_DIR`, never chained through a pipe (AGENTS.md PRIORITY 0).

**1. MEU gate** (`MEU_GATE`) — three separate receipts:

```powershell
rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/meu49-typecheck.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-typecheck.txt -Tail 30; exit $code
rtk proxy npm --prefix ui run lint      *> C:/Temp/av-kit/meu49-lint.txt;      $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-lint.txt -Tail 30; exit $code
rtk proxy npm --prefix ui run test      *> C:/Temp/av-kit/meu49-vitest.txt;    $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-vitest.txt -Tail 40; exit $code
```

Pass condition: exit 0 on all three; vitest count strictly greater than `VITEST_BASELINE_COUNT`
(**439**, measured live on the unstarted tree — round-1 correction F8).

**1a. Red-phase oracle** (`RED_PHASE_ORACLE`, run once before any implementation — round-1
correction F5). The Red row is fail-closed and may never `exit 0` unconditionally. Two steps: a
static census that the tests are written and armed, then the oracle that they are red.

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-03-p10-queue-card-dnd/assert-red-phase.ps1 -Census *> C:/Temp/av-kit/meu49-red-census.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-red-census.txt; exit $code
```

Pass condition: every `RED_PHASE_TEST_FILES` entry exists (**7** files, including the new
`ui/tests/unit/queue-dnd.test.ts`); every `RED_PHASE_REQUIRED_ACS` id (**26**) *and* every
`RED_PHASE_PRESERVATION_ACS` id (**4**) appears in at least one test name, in the file
`RED_PHASE_AC_OWNERSHIP` assigns it to — and the census additionally asserts that
the ownership map's union **equals** those two sets exactly, so an AC that is added to the
plan and never assigned to a file fails the census instead of silently escaping the oracle
(round-5 correction R4-F2: AC-49.37 and AC-49.38 were introduced in round 4 as full ACs and
never registered, and nothing was capable of noticing); no
`.skip(`/`.only(`/`.todo(` is present (`G36_RULE`); and each `RED_PHASE_UNCOLLECTED_FILES` entry
is a registered Red file that actually imports the specifier it names, whose target module does
not yet exist under `ui/` — so the census fails if a file was quietly created early, or if the
map names a specifier no test imports. Then:

```powershell
rtk proxy npm --prefix ui run test -- --reporter=json --outputFile=C:/Temp/av-kit/meu49-red.json *> C:/Temp/av-kit/meu49-red.txt; $vitest=$LASTEXITCODE; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-03-p10-queue-card-dnd/assert-red-phase.ps1 -ReportPath C:/Temp/av-kit/meu49-red.json -VitestExitCode $vitest *> C:/Temp/av-kit/meu49-red-oracle.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-red-oracle.txt; exit $code
```

Pass condition: the oracle exits 0, which requires ALL of — vitest exit code non-zero;
`numTotalTests` > `VITEST_BASELINE_COUNT` (the new tests were collected, not skipped);
`numFailedTests` > 0; every failing test's `fullName` contains an `AC-49.` token; and the AC ids
among the failures cover every unit AC row 3 owns.

Two further clauses were added in round 4 (R3-F2), because clause (b) alone is not satisfiable
on its own terms unless collection failures are accounted for explicitly. A test file that
imports a module which does not exist yet is **not collected at all**: Vitest reports it with
`status: failed`, an empty `assertionResults`, a non-empty top-level `message` reading `Cannot
find module …`, and it contributes **zero** to `numTotalTests` — measured, not assumed
(`VITEST_COLLECTION_FAILURE_SHAPE`; the captured reporter output ships in this folder as
`vitest-shape-probe.json`, and the oracle's self-test replays it). A missing *named export* from
a module that does exist behaves nothing like this — the file collects and the assertion simply
fails — which is why the distinction has to be encoded rather than reasoned about at the time.

- **(b2)** every `RED_PHASE_UNCOLLECTED_FILES` entry must be present in the report with
  `status: failed`, zero `assertionResults`, and a message naming both `Cannot find module` and
  its own expected specifier. A file that collects (its module already exists) fails here, and so
  does one whose message names a *different* specifier — a typo'd import, which would otherwise
  masquerade as the expected Red.
- **(b3)** no report entry outside that map may carry a non-empty message, and every other
  `RED_PHASE_TEST_FILES` entry must be present with an empty one. A stray collection failure
  anywhere in the suite — the failure mode that silently subtracts a whole file's cases from
  `numTotalTests` — is caught rather than absorbed into the count.

Round 5 closes the hole those two clauses left open (**R4-F1**). Clause (e) reads AC ids out
of *failing test names*, and an uncollected file reports **zero** `assertionResults` — so
no id owned by one of the three `RED_PHASE_UNCOLLECTED_FILES` can ever appear there. Eight of
the required ids are owned by exactly those files (AC-49.3–49.7 in `reorder-body.test.ts`,
AC-49.16/49.17 in `queue-dnd.test.ts`, AC-49.31 in `reorder-single-flight.test.ts`), so the
round-4 oracle demanded eight ids in a place they provably cannot be — the same
unsatisfiability R3-F2 fixed one level up, reintroduced one level down.

- **(e)** is therefore scoped **by derivation, never by hand**: the oracle intersects
  `RED_PHASE_REQUIRED_ACS` with the ids `RED_PHASE_AC_OWNERSHIP` assigns to files *not* in
  `RED_PHASE_UNCOLLECTED_FILES`, and requires that intersection (**19** ids on the current
  sets) among the failures. The other **8** are not excused: clause (b2) already requires
  their whole file to fail for its own missing specifier, which is a **stronger** Red fact
  than one failing assertion — it proves the module under test does not exist yet.
  Because the split is computed from the two named sets on every run, moving an AC between
  files, or creating a module early, re-partitions it automatically rather than leaving a
  stale hand-written list behind.

All three uncollected files are NEW, so each contributes 0 to `VITEST_BASELINE_COUNT` and the
`numTotalTests > 439` clause stays satisfiable. Self-test case 10 is the proof obligation for
exactly that: it feeds the real named sets — including the **real**
`RED_PHASE_AC_OWNERSHIP`, not a synthetic redistribution that quietly moves the eight
uncollected-file ids somewhere satisfiable — in the real reporter shape, and requires the
oracle to **pass**. A case that replays a friendlier topology than the plan actually declares
proves nothing about the plan, so "the Red phase is unreachable" is refuted against the
declared topology or not at all (round-5 correction R4-F1). The required AC ids are `RED_PHASE_REQUIRED_ACS`, which the script reads from
`named-sets.json` as the default for `-RequiredAcIds`, so the list is stated exactly once and
the command needs no substitution. `meu49-red.json` is retained as the FAIL_TO_PASS artifact.

The vitest exit code is captured into `$vitest` **immediately** after the process and handed to
the oracle, so it is never clobbered by the intervening `Get-Content`. This is one command, not
two rows: the run and its oracle can never drift apart.

**2. No-regression mount gate** (`MOUNT_GATE_SCRIPT`, run in place, one time, at phase exit):

```powershell
rtk proxy pwsh -File docs/execution/plans/2026-09-02-p10-queue-card-migration/assert-mount-completeness.ps1 -Scope all *> C:/Temp/av-kit/meu49-mount-gate.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-mount-gate.txt -Tail 30; exit $code
```

Pass condition: exit 0, `PENDING` list empty.

**3. E2E** (`E2E_SANDBOX` — `ELECTRON_RUN_AS_NODE` must be unset, bundle rebuilt first):

```powershell
$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/meu49-build.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-build.txt -Tail 20; exit $code
$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test:e2e *> C:/Temp/av-kit/meu49-e2e.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-e2e.txt -Tail 40; exit $code
$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test:e2e -- --list *> C:/Temp/av-kit/meu49-e2e-list.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-e2e-list.txt -Tail 5; exit $code
```

Pass condition: exit 0 on both; the run's passed count ≥ `E2E_POST_MEU_RUNTIME_FLOOR` (**79**)
and the `--list` total ≥ the same; separately the static `test(`-declaration census ≥
`E2E_POST_MEU_STATIC_FLOOR` (**73**). `E2E_BASELINE_COUNT` (73 runtime) and
`E2E_STATIC_CASE_FLOOR` (67 static) are the **PRE-MEU** floors and are satisfied by the unstarted
tree; asserting them at phase exit would prove nothing about MEU-49. The post-MEU floors are each
the pre-MEU floor plus the six cases `E2E_REQUIRED_CASES` names, and the `E2eCensus` gate
additionally requires each of those six AC ids inside a `test(` title in its own named spec, so a
count padded with filler cases cannot satisfy it. Round-3 correction R3-F5. `E2E_RUN_COMMAND` is mandatory: `npx --prefix ui playwright
test` changes package resolution but **not** the working directory, so it never loads
`ui/playwright.config.ts`, scans the Vitest unit files instead, exits 1 and reports 0 tests —
verified live on the unstarted tree (round-1 correction F4).

**4. Python suite** (no backend change is planned; this proves it):

```powershell
rtk proxy uv run pytest -q *> C:/Temp/av-kit/meu49-pytest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu49-pytest.txt -Tail 20; exit $code
```

**5. MEU SSOT drift gate**: `uv run python tools/meu_status.py render --check`.

**6. OpenAPI**: **N/A** — no route, schema or response model changes (`REORDER_SCHEMA_OWNER`).
`tools/export_openapi.py` is not run and no spec artifact changes.

**7. Closeout gates**: `HANDOFF_MARKER_CHECK`, `HANDOFF_AC_CHECK`, `EXEC_DISPATCH_CHECK` (each
`-SelfTest` first, then live) and `CHECK_EXEC_REVIEW`.

## Round 1 Review Corrections

Plan review round 1 (`gpt-5.6-sol`, `2026-09-03-p10-queue-card-dnd-plan-critical-review.md`)
returned `changes_required` with 8 findings. All eight were independently re-verified against the
tree before correcting — none was accepted on the reviewer's word.

| # | Sev | Finding | Correction | Where |
|---|---|---|---|---|
| F1 | High | Alt+Arrow suppression is input-time only; overlapping absolute-permutation PUTs across keyboard / kebab / drag / bulk can still clobber each other. `run()`'s `busy` is async React state and `reorder()` never reads it (`DownloaderPage.tsx:293-322`). | New `REORDER_SINGLE_FLIGHT_RULE` + `reorder-single-flight.ts`: one synchronous boolean gate acquired before any entry point reads `items`, released in `finally`. | `named-sets.json`, AC-49.31–49.35, task rows 4a / 8 |
| F2 | High | `MOVE_TO_INDEX_CONTRACT` said "index into the array after removal" while also claiming `arrayMove` semantics — the two admit different results, and AC-49.25 only checked "the order changed". | Contract restated as the FINAL index against the PRE-MOVE array, with three mandatory worked examples; AC-49.5/49.25/49.29 now assert exact sequences. | `named-sets.json`, AC-49.5, AC-49.25, AC-49.29 |
| F3 | High | PointerSensor was claimed to cover touch with no `touch-action: none` on the activator; the mouse E2E cannot expose the resulting scroll-steals-drag failure. | New `DND_TOUCH_ACTION_RULE` asserted twice — `touch-none` in the className (unit) and `getComputedStyle(...).touchAction === 'none'` (E2E). | `named-sets.json`, AC-49.10, AC-49.36 |
| F4 | High | `npx --prefix ui playwright test` exits 1 with 0 tests from the repo root — every E2E-dependent AC was unprovable. Confirmed live. | New `E2E_RUN_COMMAND` registers `npm --prefix ui run test:e2e` (verified: 73 tests in 12 files); both floors are now asserted. | `named-sets.json`, AC-49.30, §Verification Plan 3, task rows 9–10 |
| F5 | High | The Red row ended `exit 0` unconditionally, so a green suite or an unrelated failure satisfied the TDD checkpoint. | New `RED_PHASE_ORACLE` + the plan-local `assert-red-phase.ps1`, self-tested green over 8 cases at the time (14 after round 4). `-Census` proves the tests exist, name their AC ids and are not neutralized; the oracle proper is fail-closed on vitest exit code, collection count, failure count, `AC-49.` token in **every** failing name, and AC-id coverage. `RED_PHASE_REQUIRED_ACS` and `RED_PHASE_TEST_FILES` keep both lists stated exactly once. | `named-sets.json`, §Verification Plan 1a, task rows 3 / 3a |
| F6 | Med | G34 / G35 / G37 were waived without source-backed exceptions. | G34: use the canonical ref-forwarding `Button`. G35: `REORDER_FEEDBACK_TIER` assigned from live precedent (the canonical tier doc does not exist). G37: exception re-sourced under `TESTING_LIBRARY_ADOPTION` as a named bounded follow-up. | `named-sets.json`, §4A, AC-49.8/49.13/49.35, Out of Scope |
| F7 | Low | AC-49.29 had no negative test; AC-49.25's "negative" constrained the driver, not the outcome. | Both now assert an exact 4-id sequence with the two wrong orders named. | AC-49.25, AC-49.29 |
| F8 | Low | Vitest baseline was 438 (live: 439); MEU-56/TTS was wrongly said to inherit reorder. | Baseline corrected to 439 from a live receipt; inheritance narrowed to MEU-55 per `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md:134-136`. | `named-sets.json`, §Goal |

AC count after the round-1 corrections: **36** (AC-49.1–49.36); after round 4, **38**; after
round 5, **39** (AC-49.1–49.39 — AC-49.39 registers the `TESTING_LIBRARY_ADOPTION`
deliverable). `named-sets.json` grew from 72 to 84 keys in round 2, to **94** in round 4, and to
**98** in round 5 (`TESTING_LIBRARY_PACKAGES`, `TL_MIGRATION_FILES`, `RED_PHASE_AC_OWNERSHIP`,
`BUILD_PLAN_NEXT_POINTER`), and to **101** in round 6 (`REORDER_HELD_HOOK`, `TL_INTERACTION_FILES`,
`TL_MOUNT_ONLY_FILES`), and to **102** in round 7 (`DND_DEP_GUARD_CHECK`). The AC count is unchanged at 39 through both rounds: rounds 6 and 7 corrected four contracts between them and
added no criteria.
New files added by the corrections: `ui/src/renderer/src/lib/queue/reorder-single-flight.ts` and
`ui/src/renderer/src/lib/queue/use-queue-reorder-held.ts` (source, written during execution),
`ui/tests/unit/queue-dnd.test.ts` (test, written during execution) and
three plan-local scripts, all already written and self-testing green —
`assert-red-phase.ps1` (`RED_PHASE_ORACLE`, now **17** cases, **27** required AC ids + 3
preservation, clause (e) scoped by `RED_PHASE_AC_OWNERSHIP`) and `assert-plan-gates.ps1`
(`PLAN_GATE_SCRIPT`, now **73** cases across the same 8 gate groups — `Deps` gained a
row-2 `Packages` mode, selectable as `-Gate DepsPackages`, in round 6 (R5-F2), and that mode
gained the `DND_DEP_GUARD_CHECK` assertion plus its four negative fixtures in round 7 (R6-F1)). The third, `run-correction-census.ps1`
(`CORRECTION_CENSUS`, 11 cases), is a plan-review-time tool rather than an execution gate: no task
row depends on its census output. It produced the round-2 blast-radius census recorded in the
rolling review file; round 4 added its fail-closed `-Gate S6` sweep and pulled its `-SelfTest`
into task row 12, which is why that row now verifies **six** plan-local scripts rather than five —
leaving it out had made it the only unverified script in the folder.

### Self-review defects found after the F1–F8 pass

Four further defects were found and fixed by self-review before re-dispatch. The first two were
local; the third turned out to be systemic and is the reason `assert-plan-gates.ps1` exists; the
fourth was found by the round-2 correction blast-radius census (`run-correction-census.ps1`) and is
the reason that census is now a plan-local, self-tested script rather than an ad-hoc sweep.

1. Verification Plan §1a claimed clause (e) while omitting `-RequiredAcIds`. The script now defaults
   that parameter from `RED_PHASE_REQUIRED_ACS`, so the claim and the command agree.
2. Task row 3a carried a human-substituted `<the VITEST_EXIT from row 3>` placeholder. It is now one
   chained command that captures `$LASTEXITCODE` into `$vitest` immediately after the process.
3. **`SHELL_EXPANSION_RULE` — seven task rows carried an unexecutable validation command.** Rows 2,
   9, 11, H1-1, H1-4 and H2-2 each embedded a `$`-variable inside a `pwsh -NoProfile -Command "..."`
   payload. The *outer* shell expands those variables before the inner `pwsh` parses the string, so
   the child process receives `=@(Select-String ...)` and dies. Reproduced under both outer shells —
   `The term '=@' is not recognized as a name of a cmdlet` (PowerShell outer) and
   `ParserError: Missing statement after '=' in hash literal` (the form row 3 originally used). Every
   one of those rows would have exited non-zero for a reason unrelated to the condition it was
   written to test, which hides the condition exactly as thoroughly as a gate that always passes.
   All six are now `-Gate` selections on the new `PLAN_GATE_SCRIPT`, whose 24-case `-SelfTest` proves
   each gate passes on a well-formed fixture and fails on each of its own defect shapes — necessary
   because five of the six legitimately fail against today's tree, so a live run alone cannot tell a
   working gate from a broken one. Each was then also run live: `Deps`, `E2eCensus`,
   `BuildPlanAudit`, `Unchecked` and `Reflection` fail today naming the real missing work, and
   `ApiSkip` passes (`packages/api/` is genuinely untouched).

   The seventh row, row 1, was variable-free and therefore executable, but its
   `(Select-String ... -Pattern 'AC-49\.').Count` receipt exited 0 on a FIC containing zero ACs. It
   now calls `HANDOFF_AC_CHECK` (`assert-handoff-acs.ps1 -Only MEU-49`), which derives the required
   AC set from this plan and names every id the FIC dropped. Three `-Command` uses remain in
   `task.md`; all three are single variable-free expressions and were left as they are.

   Row 12 grew from four plan-local self-tests to five, and its stale "6 cases" claim about
   `assert-red-phase.ps1` was corrected to 8.

4. **The F8 correction was applied in the Goal but not in Out of Scope.** F8 narrowed the reorder
   inheritance claim from "MEU-55 and MEU-56" to MEU-55 alone, and §Goal was updated — but the Out
   of Scope row "Drag reorder on the Transcript and TTS queues" still read `Deferred | MEU-55,
   MEU-56 | Those MEUs adopt QueueList`, contradicting §Goal three hundred lines above it. The
   round-2 census caught it as a surviving `MEU-56` hit. That row is now split in two: Transcript
   stays `Deferred | MEU-55`; TTS is `Not planned | none`, because MEU-56 inherits the shared
   `ProgressBar`, not `QueueList` (`.agent/context/meu-registry.md:150`), and Phase 11's spec file
   does not exist yet (MEU-50 authors it — `docs/BUILD_PLAN.md:36`), so there is no specified TTS
   reorder behaviour to defer.

   Re-sourcing came with it. All four sites citing `.agent/context/meu-registry.md:149-150` for the
   QueueList-adoption claim were checked against that file: line 149 says MEU-55 builds Transcript
   channel cards "on the `QueueCard` anatomy" with per-card ▲ ▼ — it does **not** state `QueueList`
   adoption. The claim's real source is
   `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md:134-136` ("MEU-55 then
   adopts `QueueList` for Transcript channel cards and **inherits reorder for free**"), with MEU-55's
   dependency row at `:84` naming MEU-49. §Goal, the Out of Scope row, the F8 correction row and
   `DND_OPT_IN_RULE`'s note now cite that instead. Only the TTS half was ever backed by
   `meu-registry.md:150`, and that citation is retained where it applies.

5. **Six referenced NAMEs were defined nowhere in this project.** The plan header asserts that every
   set, threshold, label and policy is "defined exactly once in `named-sets.json`". Diffing the
   `` `NAME` ``-quoted tokens in both plan files against this project's keys showed 80 NAMEs
   referenced and 8 that did not resolve: `BULK_REORDER_ALGORITHM`, `COMMAND_MODULE_RULE`,
   `DEAD_REGION_RULE`, `MOUNT_GATE_PHASE_SCOPES` and `RETIRED_TOOLBAR_CONTROLS` are defined in
   `2026-09-02-p10-queue-card-migration/named-sets.json`, `FROZEN_GLOBS` in
   `2026-08-28-p10-queue-card-foundations/named-sets.json`, and `ELECTRON_RUN_AS_NODE` and `PENDING`
   are not named sets at all (an Electron environment variable and a literal argument value). A
   reader chasing `COMMAND_MODULE_RULE` would have found nothing here and no pointer to where it
   lives. The six are **not** copied forward — a duplicated definition is one that can drift, and
   the earlier project is the one whose code shipped them. The new `INHERITED_NAMES` key lists each
   name with the file it resolves against and records the non-set tokens explicitly, and the header
   states both exceptions. That diff was run by hand, and round 3 showed it had already gone stale:
   `BUILD_PLAN`, `FAIL_TO_PASS` and `VITEST_EXIT` were also unresolved and undeclared, so the
   round-2 wording (“two not named sets at all”) was wrong the day after it was
   written. All five are now in `INHERITED_NAMES.non_set_token_list`, and the diff is a script
   rather than a manual pass: `CORRECTION_CENSUS -Gate S6` re-runs it on every census and exits 1
   on an unresolved token, which is the only version of this check that cannot go stale between
   rounds.

## Round 3 Review Corrections

Plan review round 3 returned `changes_required` with 7 findings and reached
`PLAN_REVIEW_ROUND_CAP` (3). Execution HARD STOPPED and the round-4 correction pass below was run
only after the user's explicit authorisation (AGENTS.md §Human Approval Gate) — no system-injected
message was treated as that authorisation (GUARDRAILS SIGN 3).

As in rounds 1 and 2, every finding was re-verified against the tree before being accepted. One was
verified and found to rest on a *false premise that I also held*, and the correction is better than
what either the reviewer or I proposed — that is recorded below rather than quietly smoothed over.

| # | Sev | Finding | Correction | Where |
|---|---|---|---|---|
| R3-F1 | High | `REORDER_SINGLE_FLIGHT_RULE` left the gate's owner and lifetime unstated. A `useRef`-held gate dies when the route unmounts while its PUT is still on the wire, so the remounted page acquires freely — the F1 clobber, reachable by a route change. The bulk fold's gate ownership was also unassigned, and `moveSelected` returns `void` (`use-queue-bulk.ts:93,:96-107`) so it cannot hand a release token outward. | The module now exports `acquireQueueReorder(key)` over a **module-level** map keyed by `REORDER_QUEUE_KEYS` (new), outliving any component. Ownership of the bulk gate is assigned to `useQueueBulk` itself, which gains a required `queueKey` option. New AC-49.37 asserts the unmount/remount case and cross-queue independence; AC-49.33 now asserts **both** completion orders. | `named-sets.json` (`REORDER_QUEUE_KEYS`, rewritten `REORDER_SINGLE_FLIGHT_RULE`), AC-49.33, AC-49.37, §5 Files Modified, task row 8 |
| R3-F2 | High | "The Red oracle is unsatisfiable: row 3 writes tests importing modules rows 4/4a have not created, so those files never collect and `numTotalTests > 439` can never hold." | **Verified — and the premise is only half true.** A probe (`vitest --reporter=json` against a scratch suite) established the actual shape: a missing *module* aborts collection for its whole file (0 cases counted, non-empty top-level `message`), but a missing *named export* from an existing module does **not** — the file collects and the assertion fails normally. The reviewer's objection therefore applies to exactly three files, not to the design. The fix keeps clause (b) intact: the `queue-dnd` announcement tests move into a **new** `ui/tests/unit/queue-dnd.test.ts`, so every uncollected file is new and subtracts 0 from the 439 baseline. New clauses (b2)/(b3) require each expected-uncollected file to fail *for its own specifier* and reject any stray collection failure elsewhere. The probe output ships as `vitest-shape-probe.json` and self-test case 9 replays it; **case 10 feeds the real sets in the real shape and requires a PASS**, which is the direct refutation of "unsatisfiable". | `named-sets.json` (`RED_PHASE_UNCOLLECTED_FILES`, `VITEST_COLLECTION_FAILURE_SHAPE`), `vitest-shape-probe.json`, `assert-red-phase.ps1`, §Verification Plan 1a, §4 Files Modified |
| R3-F3 | High | `RED_PHASE_REQUIRED_ACS` demanded that AC-49.11, AC-49.14 and AC-49.23 fail in the Red phase. All three are *preservation* criteria — they assert existing behaviour is still present — so requiring them to fail is requiring a regression. | Required set narrowed to **24** ids; new `RED_PHASE_PRESERVATION_ACS` holds the three. The census scans both sets, so a missing preservation test is still caught, and self-test case 7 now rejects any overlap between the two sets so the mistake cannot be reintroduced silently. | `named-sets.json`, `assert-red-phase.ps1`, AC-49.23 note, §Verification Plan 1a |
| R3-F4 | High | Five of the six `PLAN_GATE_SCRIPT` gates were **satisfied by the unstarted tree**, so passing them proved nothing: `Deps` substring-matched a package name anywhere in the file text; `BuildPlanAudit` grepped only the two *generated* status files, not `meu-status.yaml`, which is the source they are rendered from; `Unchecked` scanned its own row and every later closeout row, which are open by construction; `ApiSkip` merged git's stderr into its porcelain output with `2>&1`, so one warning line read as a modified file. | Each rewritten as a predicate the unstarted tree FAILS, and each verified doing so live. `Deps` parses both manifests as JSON and checks the registered range plus lockfile resolution; `BuildPlanAudit` consumes the new `PHASE_EXIT_ASSERTIONS` (status YAML, phase row, Next pointer); `Unchecked` is scoped above its own row, rejects `[/]`, evidence-gates `[B]`, and fails closed if its anchor row is missing or nothing was scanned; `ApiSkip` captures stderr separately and validates each porcelain line against the v1 shape. Two gates added: `Metrics` and `CommitDraft`, replacing bare `Get-Content` receipts that exit 0 on an empty file. Self-test grew 24 → **53** cases. | `named-sets.json` (`PHASE_EXIT_ASSERTIONS`, `COMMIT_DRAFT_MARKERS`, `METRICS_ROW_MARKERS`, rewritten `PLAN_GATE_SCRIPT`), `assert-plan-gates.ps1`, task rows 2/9/11/H1-1/H1-4/H2-2/H2-3/H2-5 |
| R3-F5 | High | The E2E floors were the **pre-MEU** ones (73 runtime / 67 static), already satisfied before a line is written. | New `E2E_POST_MEU_RUNTIME_FLOOR` (**79**) and `E2E_POST_MEU_STATIC_FLOOR` (**73**), each the pre-MEU floor plus the six cases the new `E2E_REQUIRED_CASES` map names. The `E2eCensus` gate additionally requires each of those six AC ids inside a `test(` title in its own named spec, so a count padded with filler cannot satisfy it. | `named-sets.json`, §Verification Plan 3, AC-49.30, task rows 9–10 |
| R3-F6 | Med | `G37_RULE` had been paraphrased into a weaker sentence than canon contains, and `TESTING_LIBRARY_ADOPTION` was labelled `Human-approved` with no human approval on record. | `G37_RULE` restored **verbatim** from `.agent/docs/emerging-standards.md:1212-1218`. The label is withdrawn and replaced with `Local Canon`, anchored on two on-disk facts: `ui/package.json` declares no `@testing-library/*` package at all, and all 54 unit files use the local helper. Package-wide adoption becomes **OQ-5** with a named target. See the note under OQ-5 — this is the one correction where the user may reasonably want a different answer. | `named-sets.json`, §4A, Out of Scope, OQ-5 |
| R3-F7 | Low | `task.md:14` claimed "every capitalised NAME below is defined there once", which `INHERITED_NAMES` and two non-set tokens already contradicted. | The claim is narrowed to what is true and the exception is stated in the same sentence. The round-4 census adds the omitted S6 universal-claim sweep that would have caught it. | `task.md:14`, `run-correction-census.ps1` |

### On R3-F2

The reviewer and I had both assumed a missing import fails a test file uniformly. It does not, and
the difference decides the design: had the premise been true as stated, the Red phase would have
needed restructuring across all seven files. Measuring it cost one probe run and reduced the fix to
moving two assertions into a new file. The probe artifact is committed alongside the plan
specifically so the next reader does not have to take the claim on trust — and so that if Vitest's
reporter shape changes, self-test case 9 fails loudly instead of the oracle quietly degrading.

## Execution-Phase Corrections

> Defects found **after** the plan was approved, while executing `task.md`. Recorded here
> rather than silently patched, so the execution reviewer sees every post-approval change to a
> named set. Same table shape as the round tables above.

| # | Sev | Defect | Fix | Files |
|---|-----|--------|-----|-------|
| X1 | High | `RED_PHASE_REQUIRED_ACS` demanded that **AC-49.39** fail in the Red phase. AC-49.39 is the outcome check for the `G37_RULE` / `TESTING_LIBRARY_ADOPTION` migration delivered by task rows **2 and 2a**, which land *before* row 3 — a sequencing the required-set's own source note states. Measured on the row-3 tree: `ui/tests/unit/helpers/user-event.ts` is gone and unimported, all 14 `TL_MIGRATION_FILES` are on the RTL mount surface with no `createRoot` / `react-dom/client` / `act`-from-`react`, all 13 `TL_INTERACTION_FILES` call `userEvent.setup()`, and all four `TESTING_LIBRARY_PACKAGES` sit in `ui/package.json` devDependencies at their registered ranges. All four clauses already hold, so clause (e) was satisfiable only by authoring a regression for the oracle to observe — the R3-F2 defect a third time, arriving by sequence rather than by subject. Round 5 (R4-F2) added AC-49.37, AC-49.38 and AC-49.39 together on the correct observation that none was registered; the error was treating the three as one kind. | AC-49.39 moved from `RED_PHASE_REQUIRED_ACS` (now **26** ids) to `RED_PHASE_PRESERVATION_ACS` (now **4**). It loses nothing: `-Census` scans both sets, so the test must still be written and must still name its id in `downloader-page.behavior.test.ts`, and the row 7 Green gate still requires it to pass. Self-test case 7's overlap check and the ownership-union check both still hold (verified: overlap `[]`, union equal in both directions). No script change — `assert-red-phase.ps1` reads both sets from `named-sets.json` and hardcodes no count. | `named-sets.json` (`RED_PHASE_REQUIRED_ACS`, `RED_PHASE_PRESERVATION_ACS`), §Proposed Changes 5 preservation note, §Verification Plan 1a counts |
| X2 | High | `RED_PHASE_ORACLE` clause (b2) hard-coded the literal string `Cannot find module` as the message an expected-uncollected file must carry, on the strength of the round-4 probe. The first real Red run of this MEU falsified that: in **one** run, `reorder-body.test.ts` reported Vite's import-analysis wording (`Failed to resolve import "…" from "…". Does the file exist?`) while `reorder-single-flight.test.ts` and `queue-dnd.test.ts` reported the Node ESM loader's. All three are plain static relative imports of an absent module, so the wording is not selectable by writing the test differently. The oracle therefore FAILED a genuinely, correctly red suite — the worst failure mode available to it, since it punishes precisely the state the Red phase exists to reach, and the only escapes are to fake the message or to abandon the gate. | New named set **`VITEST_UNRESOLVED_MODULE_PATTERN`** (`Cannot find module\|Failed to resolve import`), read from `named-sets.json` like every other input; clause (b2)'s wording check now matches it. The two halves of (b2) were also **un-chained**: the pattern check (the *kind* of failure) and the `[regex]::Escape($spec)` check (its *identity*) were an `if`/`elseif`, so an unrecognised wording hid a typo'd import behind it — they are now independent `if`s, which is what makes widening the wording check safe. `VITEST_COLLECTION_FAILURE_SHAPE` gains clause (3) recording both observed wordings, their layers and the run they came from. `New-SuiteEntry` gains `-MessageStyle node\|vite` and `-RawMessage`, so the fixture builder can emit either real wording plus an unrelated failure — a builder that could only emit one wording is what let the defect ship. New self-test **case 18** replays case 10's real topology with the Vite wording and requires a PASS, then replaces those messages with a `SyntaxError` and requires a (b2) FAIL. Self-test count 17 → **18**, green. | `named-sets.json` (`VITEST_UNRESOLVED_MODULE_PATTERN`, `VITEST_COLLECTION_FAILURE_SHAPE`, `RED_PHASE_UNCOLLECTED_FILES` note), `assert-red-phase.ps1`, `task.md` rows 3a / 12 |
| X3 | High | The queue is not its own scroll container. dnd-kit measures auto-scroll and `KeyboardSensor.handleKeyDown`'s clamp against `<main>` (`flex-1 min-h-0 overflow-auto`); every row sits below `<main>`'s midpoint, so a pointer drag overshoots (AC-49.25/26/29) and a single ArrowDown scrolls instead of moving (AC-49.27, 0 PUTs). Configuration cannot reach the clamp (`handleKeyDown` is `private`). | Pointer: **`DND_AUTOSCROLL_CONFIG`**. Keyboard: **`QUEUE_SCROLL_CONTAINER_RULE`** — `h-full min-h-0` on both page roots, `flex-1 min-h-0` on both queue regions, `overflow-auto` on a per-page wrapper around `QueueList` (not on `listClasses`, which is the drop-overlay containing block and the non-drag DOM). Post-Red className unit tests in `downloader-page.test.ts` / `convert-page.test.ts` are **not an AC**; they exist so MEU-52 cannot paste the old mockup §04 string. Mockup §04 strings and the grouping "No Phase 10 reopening" bullet name the chain as a Phase 11 input. AC-49.27 also gains a live-region settle after Space (`KeyboardSensor.attach()` registers inside `setTimeout`). | `QueueList.tsx` (`autoScroll`), `DownloaderPage.tsx`, `ConvertPage.tsx`, `named-sets.json` (`DND_AUTOSCROLL_CONFIG`, `QUEUE_SCROLL_CONTAINER_RULE`), both page unit tests, `download-queue.test.ts` AC-49.27, `docs/proposals/2026-09-03-{downloader,convert}-page-layout-mockup.html`, `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` |
| X4 | High | X3 bounded the queue but did not say **which** pane yields height, and that omission inverted its own fix. The page column is oversubscribed at the app's own default window (1280x800 → 739px of content, ~515px of controls above the queue), so a pane must shrink; with every child at the flex default `shrink: 1` the deficit is split in proportion to content height and the queue lands at **92px** (downloader) / **85px** (convert). That is below the ~124px the rule itself names, so the clamp X3 removed from `<main>` was simply re-created one level down — AC-49.27 still 0 PUTs — and the now-tiny scroller also re-broke the three pointer cases X3 had fixed (AC-49.25/26/29), because a 5% auto-scroll band on a 92px box is 4.6px. Shrinking the chrome to fit was rejected: the same arithmetic fails again at any smaller window, and the geometry is a *product* property of the default window, not a test artifact. | Decide the pane split explicitly, as clause (4) of **`QUEUE_SCROLL_CONTAINER_RULE`**: the controls above the queue become ONE `flex min-h-0 flex-col gap-4 overflow-auto` pane that absorbs the entire deficit, the summary/processor/toolbar footer becomes ONE `flex shrink-0 flex-col gap-4` wrapper so it cannot be clipped instead, and the queue region trades `min-h-0` for `min-h-[20rem]` so it can never be the pane that yields. Measured after: both scroll ancestors report `maxScroll: 0` (scroller 280 == 280, `<main>` 699 == 699), an instrumented keyboard drag records zero `scrollTo` calls, and all four cases pass. AC-49.27's three settles were also re-grounded on real observables after instrumentation showed the live region is **not** one — the pickup is announced at t=140ms but the sensor's keydown listener is only registered at t=153ms, so the spec now counts `document` keydown registrations, waits for the ArrowDown's own announcement before the drop (the drop reads dnd-kit's committed `over`; an early Space ends the drag on the origin row and issues no PUT), and polls the focus assertion instead of reading it once. Every asserted value is unchanged — G36 holds. | `DownloaderPage.tsx`, `ConvertPage.tsx`, `named-sets.json` (`QUEUE_SCROLL_CONTAINER_RULE`), both page unit tests, `download-queue.test.ts` (AC-49.27 + `watchKeydownListeners`), `docs/proposals/2026-09-03-{downloader,convert}-page-layout-mockup.html`, `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` |
| X5 | Medium | `PHASE_EXIT_ASSERTIONS.status_field_pattern` required `status: complete` in `.agent/context/meu-status.yaml`. That value does not exist: `tools/meu_status.py update` accepts only `{approved, changes_required, closed, deferred, in_progress, pending, ready_for_review}`, and every completed MEU on disk carries `approved` (MEU-47, `meu-status.yaml:1275`). Row 11's own instruction is to set the status *through the tool*, so the gate could only be satisfied by hand-editing the SSOT to a value the tool would then reject at `render --check` — a gate that can only be passed by breaking the thing it guards. It went unnoticed because the gate's self-test builds its own fixture YAML and wrote `status: complete` into it, so the fixture agreed with the pattern and neither was ever compared to the real tool. | Pattern corrected to `^\s*status:\s*approved\s*$`, and the self-test fixture at `assert-plan-gates.ps1` (good tree, plus the `source-not-updated` negative case that rewrites it to `pending`) updated to the same vocabulary so the fixture is no longer self-confirming. Deliberately **not** widened to `(approved\|complete)`: accepting a value the tool cannot emit is precisely what would re-license the hand-edit. Self-test 73 cases across 8 gates PASS; `BuildPlanAudit` PASS; `meu_status.py render --check` PASS. | `named-sets.json` (`PHASE_EXIT_ASSERTIONS`), `assert-plan-gates.ps1` |
| X6 | Medium | `EXEC_DISPATCH_CHECK` matched the reviewer's `final.md` with `(?im)^\s*verdict:\s*`?([a-z_]+)`?`. The `^\s*` anchor required the reviewer's free-form closing summary to place the verdict on a line of its own — a formatting contract nothing ever communicated to the reviewer, and one the review file's own frontmatter already satisfies independently. Round 1 returned exactly the natural phrasing: `Review completed and validated. Verdict: `approved` with 0 findings.` The gate rejected that correct receipt as "states no verdict", so a genuine independent approval could not be bound to its dispatch. Left unfixed the only escapes are to hand-edit the reviewer's receipt — destroying the provenance the check exists to establish — or to re-dispatch a 23-minute review purely to reshape one sentence. Same family as X5: the gate's self-test wrote its own fixture in the anchored form, so fixture and pattern agreed and neither had met a real reviewer. **This is a repeat incident, which is what makes it worth fixing rather than working around.** `docs/execution/metrics.md:27` records the previous session hitting the identical wall: *"r3 was a gate-format re-dispatch, not a software round — my r2 prompt omitted the `verdict:` line `assert-exec-review-dispatch.ps1` requires in the dispatch's own final output."* That session paid a whole review round to satisfy the formatting and left the gate unchanged, so it was always going to recur — and it did, on the very next use. | Anchor widened to `(?im)(?:^\|[\s.;])verdict:\s*`?([a-z_]+)`?`. The anchor was never what made the check strong — the stale-receipt property it exists for is carried entirely by comparing the **captured token** to `EXEC_REVIEW_APPROVED`, which is unaffected by where in the line the token sits. Two self-test cases added so the widening is proved rather than asserted: a mid-sentence `approved` must now PASS (the exact round-1 `final.md`), and a mid-sentence `changes_required` must still FAIL. Self-test 7 → **9** cases, all green; the live gate then bound round 1 to dispatch `exec-review-p10-queue-card-dnd-r1`. | `assert-exec-review-dispatch.ps1` |
| X7 | Low | Task row **H2-4** abbreviated one of its eight closeout checks as `check_exec_review.py --review-file … --max-round 6`, eliding `--expected-mode` and `--expected-target` behind an ellipsis. Those are not optional: `--expected-target` carries a hard-coded default of `docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md` (`tools/check_exec_review.py:229-235`), so the row as written fails on a perfectly valid review with `target_plan='…2026-09-03-p10-queue-card-dnd…' expected '…2026-08-19-p2-external-adapters…'`. Observed live on the first H2-4 run: 7 of 8 checks passed and this one failed for a reason that had nothing to do with the tree. The sibling row H1-7 already carried the full, correct invocation, so the defect was purely the abbreviation. This is the same class the previous session logged against `tools/run-meu-gate.ps1` (three rows named a validator that has never existed, and all three reached `[x]`): **an ellipsis in a validation column is not an exact command**, and AGENTS.md §Roles & Workflows requires exact ones. | H2-4's validation column now spells the invocation out in full, matching H1-7. Re-run: **8/8 green**, receipt `C:/Temp/av-kit/closeout-check.txt`. No change to `check_exec_review.py` itself — the stale default is worth a separate look, but the row is what was wrong here. | `task.md` |

## Open Questions

> Round 1 reviewer positions are recorded inline below. OQ-3 and OQ-4 were both put to the
> independent reviewer with an explicit invitation to dissent; the reviewer concurred with both
> recommendations and added the supporting evidence noted.

- **OQ-1 (carried forward, resolved).** `.agent/context/harness.local.md` declares
  `plan_to_exec_gate: reviewer-auto` with `driver: Cursor IDE`; this session runs in Claude Code,
  whose profile is `human`. **Resolution: `human` wins** (`PLAN_TO_EXEC_GATE`). Flagged rather than
  silently picked, per AGENTS.md §Communication Policy. A durable fix — scoping the local override
  by driver — is a governance change outside this MEU.
- **OQ-2 (carried forward, resolved).** `FRESH_WORKER` is `available` in Claude Code
  (`.claude/agents/av-kit-builder.md`, `av-kit-verifier.md`), unlike the two prior Phase 10
  projects where `isolated` rows degraded. WP-2 and WP-6 are dispatchable.
- **OQ-3 (carried forward from `2026-09-02-p10-queue-card-migration/implementation-plan.md:446`,
  MUST resolve at Phase 10 exit).** Should `MOUNT_GATE_SCRIPT` be promoted into the registered MEU
  gate in `.agent/docs/commands.md`?
  **Recommendation: NO — retire it with Phase 10.** The script proves a *one-time migration
  property* (every retired toolbar control has a live home in `RETIRED_TOOLBAR_CONTROLS`). Its
  scopes are literally named after Phase 10 MEUs (`MOUNT_GATE_PHASE_SCOPES`), and its inputs are the
  migration plan's own named sets. Promoting a phase-scoped gate into the permanent registry makes
  every future MEU pay for a check whose subject stopped changing, and the first Phase 11 rename
  would turn it into a false failure that the next agent "fixes" by weakening it. This plan runs it
  once, unmodified and in place, as a no-regression check (Verification Plan §2), and Phase 10 exit
  retires it. **What survives instead:** `NO_DEAD_CONTROL_RULE`, which is the durable principle the
  script was an instance of, and which is already enforced per-MEU by E2E. If the reviewer or the
  user disagrees, the counter-move is a one-line addition to `.agent/docs/commands.md` and one
  extra row here — no other row changes.
  **Round 1 reviewer position: concurs (NO).** The reviewer independently confirmed the script's
  scopes resolve Phase 10 MEU names at `assert-mount-completeness.ps1:522-528`, and that its
  named-set inputs live in the migration plan folder — so promotion would bind the permanent
  registry to a retiring plan directory. No dissent recorded.
- **OQ-5 (CLOSED by human direction, 2026-09-04).** *Was:* does `ui/` adopt
  `@testing-library/user-event` to satisfy `G37_RULE` literally, or keep the hand-rolled
  `ui/tests/unit/helpers/user-event.ts` and defer adoption to session 23? Round 4 recommended
  deferral on the strength of a blast-radius figure I asserted without measuring — “all 54
  unit files use the helper”, when the true count is 5 — and R4-F5 was right to reject it.
  **Resolution: adopt inside MEU-49, no split.** The user's direction is on record verbatim:
  *“G37 / OQ-5 - No splits … There is no legacy, everything is net new, if the code needs to be
  replaced it can simply be removed and recoded into better shape.”* That is a `USER_EXPLICIT`
  chat message, which is the only provenance AGENTS.md accepts for a `Human-approved` label —
  and it is why `TESTING_LIBRARY_ADOPTION` may now carry that label where round 2's use of it
  could not. The work is specified in `TESTING_LIBRARY_ADOPTION` / `TESTING_LIBRARY_PACKAGES` /
  `TL_MIGRATION_FILES`, delivered by task rows 2 and 2a, and proven by AC-49.39: the helper file
  is gone, nothing imports it, all 14 files mount through `render`/`screen` with no
  `createRoot` left behind, and the four packages sit in `devDependencies` at the registered
  ranges. No follow-up MEU is registered because nothing is left over.
- **OQ-4 (open, low risk).** The React Compiler (`babel-plugin-react-compiler ^1.0.0`) is enabled in
  the renderer build. dnd-kit's hooks return refs and callbacks that the compiler may decline to
  memoize. If the build emits a bail-out for `QueueList` or `QueueCard`, the documented escape hatch
  is a `"use no memo"` directive on the affected component. **Not pre-applied** — adding it
  speculatively would suppress a signal we want to see. If a bail-out appears in the
  `meu49-build.txt` receipt, it is recorded in the handoff with the directive and its justification.
  **Round 1 reviewer position: accepts.** The reviewer agreed that pre-applying `"use no memo"`
  would suppress the diagnostic and raised no additional compiler risk for `useSortable`.

## Research References

1. `docs/build-plan/10-queue-card-ui.md` — lines 34, 45, 47, 57, 249-256 (the Spec).
2. `docs/build-plan/build-priority-matrix.md` §10.9 — MEU-49 `gui-queue-dnd`.
3. dnd-kit documentation — `useSortable` (`setActivatorNodeRef`, `attributes`, `listeners`,
   `transform`, `transition`, `isDragging`), `DndContext` `announcements` /
   `screenReaderInstructions`, `PointerSensor` `activationConstraint`,
   `sortableKeyboardCoordinates`, `@dnd-kit/accessibility` `<LiveRegion>` (`useUniqueId('DndLiveRegion')`).
4. W3C WCAG 2.2 — SC 2.5.7 Dragging Movements (AA), SC 2.4.7 Focus Visible, SC 4.1.2 Name Role Value.
5. npm registry, 2026-09-03 — `@dnd-kit/core` 6.3.1, `@dnd-kit/sortable` 10.0.0,
   `@dnd-kit/utilities` 3.2.2 versions, licences and peer ranges (`DND_PACKAGES`).
6. `packages/api/src/avkit_api/routes/downloads.py:210-217`,
   `routes/conversions.py:232-239`, `schemas/downloads.py:79`, `schemas/conversions.py:61`,
   `schemas/common.py:8-11` — the reorder wire contract and its `extra="forbid"` policy.
7. `ui/src/renderer/src/components/queue/QueueList.tsx:120,130,166-177` and
   `QueueCard.tsx:1-13,343-366` — the two collision surfaces (`DRAG_STATE_ISOLATION_RULE`,
   `ALT_ARROW_SUPPRESSION_RULE`).
8. `ui/tests/unit/queue-card.test.ts:776-855` — the standards sweep and the dependency guard at
   :807 that `DND_DEP_GUARD_SUPERSESSION` narrows.
9. React Compiler documentation — bail-out behaviour and the `"use no memo"` escape hatch (OQ-4).
