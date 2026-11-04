---
date: "2026-09-16"
project: "2026-09-03-p10-queue-card-dnd"
meu: "MEU-49"
status: "ready_for_review"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md"
build_plan_section: "bp10s10.8"
agent: "claude-opus-5"
reviewer: "gpt-5.6-sol"
predecessor: "2026-09-02-p10-queue-card-migration-MEU-47-handoff.md"
---

# Handoff: 2026-09-03-p10-queue-card-dnd-MEU-49-handoff

> **Status**: `ready_for_review`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-49 — `gui-queue-dnd`, the **Phase 10 exit**. Pointer drag reorder inside the
shared `QueueList` via dnd-kit, with ARIA live-region announcements, landing on both queue
pages at once. Alt+Arrow and the kebab reorder items remain **equal** paths rather than
fallbacks (`WCAG_DRAG_RULE`), and every permutation mutation — drag, keyboard, kebab and the
bulk fold — is serialised through one queue-scoped single-flight gate, because nothing
serialises them today and two overlapping absolute permutations computed from the same
pre-mutation order clobber each other.

The reorder is opt-in per `DND_OPT_IN_RULE`: `QueueList` renders `DndContext` only when
`onMoveToIndex` is supplied, so the transcript and TTS pages that already mount `QueueList`
keep their exact pre-MEU DOM. This is what lets Phase 11's MEU-55 inherit reorder by simply
adopting `QueueList` and passing the prop.

**Build Plan Section**: [10 §Drag and drop](../../../docs/build-plan/10-queue-card-ui.md)
(matrix item 10.8; canon at `10-queue-card-ui.md:254-256`)

**Predecessor**: [`2026-09-02-p10-queue-card-migration-MEU-47-handoff.md`](2026-09-02-p10-queue-card-migration-MEU-47-handoff.md)

**Carried by this MEU but not of it — the `G37_RULE` Testing Library adoption.** Task rows 2
and 2a delete `ui/tests/unit/helpers/user-event.ts` and recode all 14 `TL_MIGRATION_FILES`
onto `render`/`screen`, with the 13 `TL_INTERACTION_FILES` on `userEvent.setup()`. This is
`Human-approved` (user direction 2026-09-04: *"No splits ... if the code needs to be replaced
it can simply be removed and recoded into better shape"*), closes OQ-5, and lands **before**
the Red phase so MEU-49's own new interaction tests are written on the canonical surface and
never on a shim scheduled for deletion. It is a mechanical call-site translation under
`G36_RULE`: no assertion or expected value may change, and Vitest must report the **same 439**
passing tests before and after — that count is the whole proof the translation preserved
behaviour.

**Deliberately NOT in this MEU.** No new REST surface: `REORDER_SCHEMA_OWNER` shows the
absolute-permutation wire contract already exists, so `packages/api/` is untouched. No
virtualization dependency (`10-queue-card-ui.md:47`) — `DND_DEP_GUARD_SUPERSESSION` narrows
the existing guard to `/react-virtual/` rather than deleting it, so the virtualization half
stays armed. No sixth `Button` variant and no fourth size (`G34_RULE`). No edit to
`docs/build-plan/10-queue-card-ui.md` (`CANON_CLAUSE_NON_CHANGE`), and none to
`ui/tests/e2e/transcript-queue.test.ts` or `tts-generate.test.ts` — those two staying green
untouched **is** the live proof that `DND_OPT_IN_RULE` holds.

**`JSDOM_RECT_RULE` — read the unit/E2E split as a division of labour, not a coverage gap.**
jsdom computes no layout and `getBoundingClientRect` is stubbed to zeros, so a *completed*
dnd-kit pointer drag cannot be simulated there. The unit tests therefore exercise
`DndContext`'s public interface — its `onDragStart`/`onDragOver`/`onDragEnd`/`onDragCancel`
callbacks and the resulting re-render — plus the pure permutation builders and announcement
factory, which is what the dnd-kit maintainers themselves recommend for jsdom. The real drag
is proved in Playwright against real Electron via `E2E_DRAG_DRIVER`
(`page.mouse.down` → `move(..., { steps })` → `up`, never `locator.dragTo()`), asserting the
**exact** resulting order `[B,C,A,D]` rather than a weaker "the order changed".

---

## Feature Intent Contract (Acceptance Criteria)

> **AC-table integrity (control C4).** All **39** plan ACs (AC-49.1–49.39) are transcribed
> below from `implementation-plan.md`, each carrying its plan `Type`, its `Source` label
> (`Spec` / `Local Canon` / `Research-backed` / `Human-approved`), the test(s) that prove it,
> and its **negative test** — the observation that must fail if the implementation is wrong.
> The table is generated from the plan rather than retyped, so it cannot drift from its
> source. `HANDOFF_AC_CHECK` re-derives the required id set from the plan on every run.
>
> **Type discipline (control C3).** The six `integration` ACs (AC-49.25–49.30, AC-49.36) name
> Playwright specs; every `unit` AC names a Vitest file or the gate that owns it. AC-49.1,
> AC-49.2 and AC-49.30 are proved by a gate rather than by a single case, and each names its
> gate in the `Test(s)` cell.
>
> Statuses are ⬜ at FIC time by construction: this is the Red-phase contract, written before
> any implementation. They are filled in as the task table advances.

| AC | Type | Description | Source | Test(s) | Negative Test | Status |
|----|------|-------------|--------|---------|---------------|--------|
| AC-49.1 | unit | `ui/package.json` `dependencies` contains exactly the three entries in `DND_PACKAGES` at those ranges, and no `@dnd-kit/react` and no virtualization package. | Spec 10-queue-card-ui.md:254 (`dnd-kit`), :47 (no virtualization dep) | `assert-plan-gates.ps1 -Gate DepsPackages` (both manifests, rejected packages) | Adding `react-virtual` fails the narrowed guard. | ✅ |
| AC-49.2 | unit | `ui/tests/unit/queue-card.test.ts` dependency guard is narrowed to `/react-virtual/` with an in-place `MEU-49` supersession comment citing 10-queue-card-ui.md:254-256; the virtualization half still fails on a planted `react-virtual` entry. Row 2’s gate ASSERTS this per `DND_DEP_GUARD_CHECK` — all four literals plus the comment window — in **both** `Test-Deps` modes, since row 2 and not row 2a owns it (round-7 correction R6-F1: `Packages` mode never read this file, so a tree with the broad guard still in place reported zero problems). | `DND_DEP_GUARD_SUPERSESSION`, `DND_DEP_GUARD_CHECK`, `G36_RULE` | `assert-plan-gates.ps1 -Gate DepsPackages` -> `DND_DEP_GUARD_CHECK`; negatives `Deps/dep-guard-still-broad|deleted|no-supersession|comment-not-in-place` | Planted `@tanstack/react-virtual` entry must still fail; and four gate fixtures cover the ways the change can be absent — `Deps/dep-guard-still-broad`, `Deps/dep-guard-deleted` (narrowing replaced by outright deletion, the `G36_RULE` violation), `Deps/dep-guard-no-supersession` and `Deps/dep-guard-comment-not-in-place`. | ✅ |
| AC-49.3 | unit | `buildReorderBody` lives only in `REORDER_BODY_MODULE`; `convert-controls.ts` and `download-controls.ts` re-export it, and `convertControls.buildReorderBody === downloadControls.buildReorderBody` (reference identity). | `REORDER_BODY_MODULE` (single owner) | `reorder-body.test.ts` | Two copies that merely behave alike fail the identity assertion. | ✅ |
| AC-49.4 | unit | All four existing directions (`up`/`down`/`top`/`bottom`) and the unknown-id branch produce byte-identical output to the pre-move implementation for a fixed 5-id fixture. | Local Canon — behaviour preservation | `reorder-body.test.ts` | A changed splice bound fails. | ✅ |
| AC-49.5 | unit | `buildReorderBodyToIndex(ids, movedId, targetIndex)` implements `MOVE_TO_INDEX_CONTRACT` with `targetIndex` as the FINAL index resolved against the PRE-MOVE array. Three exact-order assertions are mandatory: `[A,B,C,D]` move `A`→2 ⇒ `[B,C,A,D]`; `[A,B,C,D]` move `D`→1 ⇒ `[A,D,B,C]`; `[A,B,C]` move `A`→1 ⇒ `[B,A,C]`. Plus clamp above and below range, and unknown `movedId` → unchanged copy. | `MOVE_TO_INDEX_CONTRACT` | `reorder-body.test.ts` | The forward case must assert `[B,C,A,D]` **exactly** — a remove-then-insert-at-post-removal-index implementation yields `[B,A,C,D]` and must fail. `targetIndex = 99` on a 5-item list must clamp, not throw and not drop the row. | ✅ |
| AC-49.6 | unit | `buildReorderBodyToIndex` with `targetIndex` equal to the row's current index returns the identity permutation, and `reorderDownloadToIndex` / `reorderConversionToIndex` issue **no** request for it. | `MOVE_TO_INDEX_CONTRACT`, `REORDER_WIRE_CONTRACT` | `reorder-body.test.ts` | A spy on `apiFetch` must record zero calls for a self-drop. | ✅ |
| AC-49.7 | unit | Every pre-existing import site still resolves: `convert-commands.ts:11`, `download-commands.ts:7`, `bulk-reorder.ts:38` (`deps.buildBody`). The bulk sequential fold is unchanged. | `BULK_REORDER_ALGORITHM` carried from the migration plan | `reorder-body.test.ts` | Removing a re-export fails typecheck and this test. | ✅ |
| AC-49.8 | unit | When drag is enabled the card renders `DND_TESTIDS[0]` as the FIRST child of the card container: the canonical `Button` (`variant="ghost" size="sm" icon`), which resolves to a real `<button type="button">` carrying the `btn-ghost` marker class, accessible name `Reorder <job title>`, dnd-kit's `attributes` and `listeners`, and `setActivatorNodeRef` passed as `ref` (forwarded at `Button.tsx:37-50` onto the element at `:62-68`). | `DND_HANDLE_CONTRACT`, `G34_RULE`, Spec :254 | `queue-card.test.ts` | A `<div role="button">` fails the tag assertion; a bare `<button>` fails the `btn-ghost` marker-class assertion. | ✅ |
| AC-49.9 | unit | The handle is a SIBLING of the checkbox, activatable region, primary action and kebab — never a descendant of the activatable region and never an ancestor of any of them. | `DND_HANDLE_CONTRACT`, QueueCard.tsx:1-13, WCAG 2.2 SC 4.1.2 | `queue-card.test.ts` | A handle wrapping the title region fails the containment assertion. | ✅ |
| AC-49.10 | unit | The handle's className carries `opacity-0` plus `group-hover:`, `group-focus-within:` and `focus-visible:` opacity transitions **and `touch-none`**, and contains none of `hidden`, `aria-hidden`, `display:none`, `touch-auto`, `touch-pan-y`, or an animated `w-`/`h-`/`top-`/`left-`/`margin`/`box-shadow` property. | `DND_HOVER_REVEAL_RULE`, `DND_TOUCH_ACTION_RULE`, `G33_RULE` | `queue-card.test.ts` | `hidden group-hover:block` fails; omitting `touch-none` fails, which is the only unit-level guard against a touch drag being stolen by native scrolling. | ✅ |
| AC-49.11 | unit | With drag disabled (`DND_OPT_IN_RULE`) the card renders no handle, no `DND_TESTIDS` node and no dnd attributes — the DOM matches the pre-MEU snapshot. | `DND_OPT_IN_RULE` | `queue-card.test.ts` | An always-mounted handle fails on the transcript/tts fixtures. | ✅ |
| AC-49.12 | unit | While `isDragging` is true, `Alt+ArrowUp` and `Alt+ArrowDown` on the card do NOT call `onMoveUp`/`onMoveDown`; with `isDragging` false they still do, and `isFirst`/`isLast` guards are unchanged. | `ALT_ARROW_SUPPRESSION_RULE` | `queue-card.test.ts` | Firing Alt+ArrowUp mid-drag must record zero `onMoveUp` calls. | ✅ |
| AC-49.13 | unit | The handle uses the canonical `Button` with an existing variant/size pair (`ghost` / `sm`, `icon`) and introduces no sixth variant and no fourth size; `Button.tsx:14,22` are unchanged and the card stays inside the frozen 5×3 maps. | `G34_RULE` | `queue-card.test.ts` | A `variant="drag"`, a new `sizeClasses` entry, or a bare `<button>` with ad-hoc padding all fail. | ✅ |
| AC-49.14 | unit | With `onMoveToIndex` undefined, `QueueList` renders no `DndContext`, no `SortableContext`, no handle and no live region; the rendered DOM is byte-identical to the pre-MEU output for the same props. | `DND_OPT_IN_RULE` | `queue-primitives.test.ts` | Unconditional `DndContext` fails the byte-identity assertion. | ✅ |
| AC-49.15 | unit | With `onMoveToIndex` defined, `SortableContext` receives the item ids in render order, and re-rendering with a changed `items` array updates that id list. | `DND_OPT_IN_RULE` | `queue-primitives.test.ts` | A stale id list fails after a queue update. | ✅ |
| AC-49.16 | unit | The `announcements` object passed to `DndContext` defines all four of `onDragStart`, `onDragOver`, `onDragEnd`, `onDragCancel`, and `screenReaderInstructions` is non-empty. | `DND_ANNOUNCEMENT_CONTRACT`, Spec :255 | `queue-dnd.test.ts` | Omitting `onDragCancel` fails. | ✅ |
| AC-49.17 | unit | Each announcement string is POSITION-based and 1-INDEXED and names the job title (e.g. `Moved "Foo" to position 3 of 7`); none contains a 0-based index; `onDragCancel` states the item returned to its starting position. | `DND_ANNOUNCEMENT_CONTRACT` | `queue-dnd.test.ts` | `position 2 of 7` for the third of seven rows fails. | ✅ |
| AC-49.18 | unit | `onDragEnd` over a different row calls `onMoveToIndex(activeId, targetIndex)` exactly once with `arrayMove` index semantics; a drop on itself and `onDragCancel` call it zero times. | `MOVE_TO_INDEX_CONTRACT` | `queue-primitives.test.ts` | A self-drop that fires the callback fails. | ✅ |
| AC-49.19 | unit | While a row drag is active the list container's `data-drag-state` is `idle` and `queue-drop-overlay` is absent; a simulated file `dragenter` still sets the drop state and still renders the overlay. | `DRAG_STATE_ISOLATION_RULE` | `queue-primitives.test.ts` | Merging `DndContext` into the drop-zone container fails one direction or the other. | ✅ |
| AC-49.20 | unit | Row displacement comes from dnd-kit's `transform`/`transition` (via `CSS.Transform.toString`), never from `top`/`left`/`margin`. | `G33_RULE` | `queue-primitives.test.ts` | An inline `top:` offset fails. | ✅ |
| AC-49.21 | unit | `download-commands.ts` exports `reorderDownloadToIndex(ids, movedId, targetIndex)` and `convert-commands.ts` exports `reorderConversionToIndex`, each building the body with `buildReorderBodyToIndex` and issuing one `PUT` to its endpoint, then reconciling once — mirroring the existing `reorderDownload` shape at `download-commands.ts:381-410`. | `COMMAND_MODULE_RULE`, `REORDER_WIRE_CONTRACT` | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | Inline `apiFetch` in a page `onClick` fails the command-module assertion. | ✅ |
| AC-49.22 | unit | Both pages pass `onMoveToIndex` to `QueueList` wired to their own command; a failed PUT surfaces through the page's existing error path and does not leave the list optimistically reordered. | `COMMAND_MODULE_RULE`, `NO_DEAD_CONTROL_RULE` | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | A swallowed rejection fails. | ✅ |
| AC-49.23 | unit (**preservation**) | The kebab reorder items (`Move up` / `Move down` / `Move to top` / `Move to bottom`) and the Alt+Arrow path are still present and still call their existing commands on a page that also has drag. | `WCAG_DRAG_RULE`, Spec :57 | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | Removing a kebab item fails, proving the single-pointer alternative survives. | ✅ |
| AC-49.24 | unit | `DND_TESTIDS` is registered in `ui/tests/e2e/test-ids.ts` and the registry test covers it. | `E2E_LOCATOR_FORM` | `downloader-page.behavior.test.ts` | An unregistered testid fails the registry test. | ✅ |
| AC-49.25 | integration | On a downloader queue seeded with a known 4-row order `[A,B,C,D]`, dragging `A`'s handle onto row 3 (`C`) via `E2E_DRAG_DRIVER` produces the **exact** rendered order `[B,C,A,D]`, and that exact order survives a reload. | `E2_RULE`, `MOVE_TO_INDEX_CONTRACT`, Spec :254 | `download-queue.test.ts` | The assertion is the exact 4-id sequence, not "the order changed": `[B,A,C,D]` (post-removal-index bug) and the unchanged `[A,B,C,D]` (drag never activated, e.g. via `locator.dragTo()`) must both fail. | ✅ |
| AC-49.26 | integration | During and after that drag, `[id^="DndLiveRegion"]` (`DND_LIVE_REGION_LOCATOR`) contains a position-based announcement naming the dragged title. | `DND_ANNOUNCEMENT_CONTRACT`, Spec :255 | `download-queue.test.ts` | A `role=status` locator is ambiguous with `queue-drop-overlay` and is forbidden. | ✅ |
| AC-49.27 | integration | Keyboard drag: focus the handle, `Space` to lift, `ArrowDown`, `Space` to drop — the order changes and focus returns to the handle on the moved row. | `DND_HANDLE_CONTRACT`, `DND_SENSOR_CONFIG` | `download-queue.test.ts` | A non-focusable handle cannot be reached by Tab and fails here. | ✅ |
| AC-49.28 | integration | Throughout a row drag on the downloader page, the list container's `data-drag-state` stays `idle` and `queue-drop-overlay` never appears. | `DRAG_STATE_ISOLATION_RULE` | `download-queue.test.ts` | A merged context shows the file-drop overlay mid-drag. | ✅ |
| AC-49.29 | integration | The same drag on a convert queue seeded `[A,B,C,D]` produces the exact order `[B,C,A,D]`, proving the wiring is per-page and not downloader-only. | `E2_RULE`, `MOVE_TO_INDEX_CONTRACT` | `convert-queue.test.ts` | An unchanged order (the convert page never received `onMoveToIndex`) and `[B,A,C,D]` must both fail — the same exact-sequence assertion as AC-49.25, never a weaker "changed" check. | ✅ |
| AC-49.30 | integration | The full Playwright suite, invoked via `E2E_RUN_COMMAND`, passes with the runtime case count ≥ `E2E_BASELINE_COUNT` **and** the static `test(`-declaration count ≥ `E2E_STATIC_CASE_FLOOR`; both floors are asserted by the gate, not read by eye. `ui/tests/e2e/transcript-queue.test.ts` and `tts-generate.test.ts` are untouched and green (`DND_OPT_IN_RULE`). | `E2_RULE`, `E2E_RUN_COMMAND`, `G36_RULE` | `assert-plan-gates.ps1 -Gate E2eCensus` + the full suite via `E2E_RUN_COMMAND` | A dropped assertion lowers either count and fails. Invoking the suite as `npx --prefix ui playwright test` reports 0 tests and exits 1 — that form is forbidden by `E2E_RUN_COMMAND`. | ✅ |
| AC-49.31 | unit | NEW `ui/src/renderer/src/lib/queue/reorder-single-flight.ts` exports `createSingleFlight()` returning `{ tryAcquire, release, held }` over a plain boolean (not React state): the first `tryAcquire()` returns `true` and every subsequent call returns `false` until `release()`; `release()` without a prior acquire is a no-op; two instances are independent; `held` reflects the state synchronously **within the same tick**. | `REORDER_SINGLE_FLIGHT_RULE` | `reorder-single-flight.test.ts` | A `useState`-backed implementation cannot satisfy the same-tick assertion (two synchronous `tryAcquire()` calls would both return `true`) and fails. | ✅ |
| AC-49.32 | unit | Every reorder entry point on a page — kebab `Move up`/`down`/`top`/`bottom`, Alt+Arrow, and drag `onMoveToIndex` — calls `tryAcquire()` before it reads `items` or builds a body. With `apiFetch` stubbed by a **deferred promise**, an in-flight Alt+Arrow reorder followed immediately by a drag drop issues exactly **one** PUT; after the first promise resolves and the list reconciles, a second drag issues its own PUT. | `REORDER_SINGLE_FLIGHT_RULE`, `REORDER_WIRE_CONTRACT` | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | Removing the gate makes the same sequence issue **two** PUTs whose bodies are both computed from the same pre-mutation order — the exact stale-base clobber. The test asserts the call count, not just the final list. | ✅ |
| AC-49.33 | unit | The bulk reorder fold holds the gate for the **whole** sequence: a drag drop attempted while a bulk reorder is mid-fold issues zero PUTs, and the bulk fold's own N requests are unaffected. The gate is acquired and released inside `use-queue-bulk.ts`'s `moveSelected` (`:93,:96-107`), which returns `void` and therefore cannot hand a release token to its caller — the ownership follows from the existing signature, not from preference. Both completion orders are asserted: the fold resolving before the blocked drag is retried, **and** the blocked drag arriving after `refetch()` has already resolved but before `clear()` has run. | `REORDER_SINGLE_FLIGHT_RULE`, `BULK_REORDER_ALGORITHM` | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | A gate acquired per-request inside the fold lets a drag interleave between two bulk PUTs and fails. A gate released before `refetch()` resolves lets the retried drag compute its body from the pre-fold order — the same stale-base clobber one level up — and fails the second ordering. | ✅ |
| AC-49.34 | unit | `release()` runs in a `finally`: after a **rejected** reorder PUT the error surfaces through the page's existing error path **and** the next reorder still acquires the gate and issues its PUT. | `REORDER_SINGLE_FLIGHT_RULE`, `REORDER_FEEDBACK_TIER` | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | Releasing only on the success path deadlocks every later reorder after one failure — the test must prove the second attempt still fires. | ✅ |
| AC-49.35 | unit | While the gate is held, every rendered drag handle is `disabled`; when it is released they are enabled again — **without a remount**. The held flag reaches the card through `useQueueReorderHeld(key)` from `REORDER_HELD_HOOK` (`useSyncExternalStore` over `REORDER_SINGLE_FLIGHT_RULE`'s module-level registry), so a gate taken by *another* card's kebab still disables *this* card's handle. The hook lives in its own module, not in `reorder-single-flight.ts`: the store is imported by the plain-TS command modules, which have no React import and must not acquire one (round-6 correction R5-F1). | `REORDER_FEEDBACK_TIER`, `REORDER_SINGLE_FLIGHT_RULE`, `REORDER_HELD_HOOK` | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | A handle that stays enabled but silently no-ops is an invisible dead control and fails. So does a page-local `useState` mirror of the gate: it is not written by the other card's acquire, so the assertion that a sibling's acquire disables this handle fails — which is the round-5 R4-F3 defect, a rendered consequence asserted for a state no component could observe. | ✅ |
| AC-49.36 | integration | On the rendered Electron page, `getComputedStyle(handle).touchAction === 'none'` for every drag handle. | `DND_TOUCH_ACTION_RULE` | `download-queue.test.ts` | A handle resolving to `auto` or `pan-y` fails — the mouse driver alone cannot expose this, which is why the computed style is asserted directly. | ✅ |
| AC-49.37 | unit | The gate's lifetime is the **queue**, not the component. `acquireQueueReorder(key)` reads a MODULE-LEVEL map keyed by `REORDER_QUEUE_KEYS`: unmounting and remounting the downloader page while a reorder PUT is still on the wire does NOT hand the next caller a free gate, and the release from the in-flight request still frees it for the remounted tree. Independently, holding the `download` gate leaves the `convert` gate acquirable. | `REORDER_SINGLE_FLIGHT_RULE` | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | A gate held in a `useRef` dies with the unmounting component while its PUT is still in flight, so the remounted page acquires freely and issues a second absolute-permutation body computed from the pre-mutation order — the F1 clobber, reachable by a route change. A single global boolean instead of a per-key map fails the cross-queue half. | ✅ |
| AC-49.38 | unit | Feedback parity while the gate is held: **every reorder affordance that is present** is visibly inert, not just the drag handle. Asserted on **two** cards in the same list, because the menu's contents are position-dependent: on a **middle** card all four kebab reorder items (`Move up` / `Move down` / `Move to top` / `Move to bottom`) render `disabled`; on the **first** card exactly `Move down` and `Move to bottom` are present and both render `disabled`, while `Move up` and `Move to top` remain **absent** — not disabled. Alt+ArrowUp / Alt+ArrowDown issue zero PUTs on the same guard. When the gate is released every present item is live again. | `REORDER_FEEDBACK_TIER`, `NO_DEAD_CONTROL_RULE`, `WCAG_DRAG_RULE`, `QueueCardMenu.tsx:1-13` rule 1 | `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` | Disabling only the handle leaves the kebab and keyboard paths looking live while they silently no-op — three invisible dead controls, and precisely the single-pointer/keyboard alternative WCAG 2.2 SC 2.5.7 requires to remain trustworthy. The two-card form is also a negative test against the round-4 wording, which demanded four disabled items unconditionally: that is unsatisfiable on a boundary row **and** contradicts the component it constrains, whose rule 1 is “Unavailable actions are absent, never disabled” (the builder pushes `move-up`/`move-top` only `if (!isFirst && handler !== undefined)`). An implementation that disables all four everywhere fails the first-card half; one that only disables the handle fails both. | ✅ |
| AC-49.39 | unit | The `G37_RULE` migration is complete, not partial, and the check is the **outcome** rather than a proxy for it. (i) `ui/tests/unit/helpers/user-event.ts` **does not exist** and no file under `ui/` imports `helpers/user-event`. (ii) **Mount half, all 14 `TL_MIGRATION_FILES`:** each imports `@testing-library/react`, calls `render(`, queries through `screen`, and retains **none** of the retired surface — no `react-dom/client` specifier, no `createRoot`, no `act` imported from `'react'`. (`createElement` is untouched and still allowed: these are `.test.ts` files with no JSX, so `render(createElement(C, props))` is the idiomatic RTL form here.) (iii) **Interaction half, the 13 `TL_INTERACTION_FILES`:** each additionally imports `@testing-library/user-event` and calls `userEvent.setup()`; the one `TL_MOUNT_ONLY_FILES` entry is exempt **by registration**, and the two sets must partition `TL_MIGRATION_FILES` exactly in both directions. (iv) All four `TESTING_LIBRARY_PACKAGES` appear in `ui/package.json` **devDependencies** at their registered ranges. | `TESTING_LIBRARY_ADOPTION`, `G37_RULE`, `TL_MIGRATION_FILES`, `TL_INTERACTION_FILES`, `TL_MOUNT_ONLY_FILES` | `downloader-page.behavior.test.ts` | A half-migration fails, and so does the specific **false pass** round 5 shipped (correction R5-F3): a file that keeps its `createRoot` mount, adds one no-op `userEvent.setup()`, and changes nothing else satisfied the round-5 gate *and* the exactly-439 count while delivering no migration at all. Clause (ii) is what makes the recode observable; self-test case `Deps/tl-old-style-retained` is that exact tree and must now fail. Forcing `userEvent.setup()` into the mount-only file would have been the mirror defect — a gate satisfied by dead ceremony — which is why the exemption is registered rather than assumed. | ✅ |

### AC ownership at a glance

| Proved by | ACs |
|---|---|
| `reorder-body.test.ts` | AC-49.3–49.7 |
| `reorder-single-flight.test.ts` | AC-49.31 |
| `queue-dnd.test.ts` (NEW) | AC-49.16, AC-49.17 |
| `queue-card.test.ts` | AC-49.8–49.13 |
| `queue-primitives.test.ts` | AC-49.14, AC-49.15, AC-49.18–49.20 |
| `downloader-page.behavior.test.ts` | AC-49.21–49.24, AC-49.32–49.35, AC-49.37–49.39 |
| `convert-page.behavior.test.ts` | AC-49.21–49.23, AC-49.32–49.35, AC-49.37, AC-49.38 |
| `download-queue.test.ts` (E2E) | AC-49.25–49.28, AC-49.36 |
| `convert-queue.test.ts` (E2E) | AC-49.29 |
| Gate only | AC-49.1, AC-49.2 (`-Gate DepsPackages`), AC-49.30 (`-Gate E2eCensus` + full suite) |

`queue-dnd.test.ts` is a **new file** rather than additions to `queue-primitives.test.ts`
because importing the not-yet-created `queue-dnd` module aborts collection for its whole file
(`VITEST_COLLECTION_FAILURE_SHAPE`); folding AC-49.16/49.17 into an existing file would
subtract that file's existing cases from `numTotalTests` and break the Red oracle's own
baseline clause. A new file subtracts 0.

Every Red-phase test name embeds its own AC id (e.g. `AC-49.8 handle is the first child`):
`RED_PHASE_ORACLE` clause (d) reads test names, so the convention is load-bearing, not
cosmetic.

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

All 39 ACs are ✅. Every receipt below is a real file under `VALIDATION_RECEIPT_DIR`
(`C:/Temp/av-kit/`) — open any of them rather than taking a count on trust.

### FAIL_TO_PASS

The Red phase is proved by the oracle rather than by a prose claim: `assert-red-phase.ps1`
consumes the vitest JSON report **and** vitest's own exit code in one chained command, so the
run cannot drift from its evidence. Per-test Red snippets are not transcribed here because
the oracle's clauses are strictly stronger than a hand-picked list — it requires a non-zero
vitest exit, a total above the 439 baseline, at least one failure, an `AC-49.` token in
**every** failing test name, and coverage of every AC the Red row owns.

| Receipt | Result |
|---|---|
| `C:/Temp/av-kit/meu49-red-oracle.txt` | `PASS: RED_PHASE_ORACLE (vitest exit 1, baseline 439, 18 AC ids proven by clause (e) and 8 by clause (b2), 3 expected-uncollected files verified, report C:/Temp/av-kit/meu49-red.json)` |
| `C:/Temp/av-kit/meu49-red-census.txt` | `PASS: RED_PHASE_ORACLE census (7 files, 30 AC ids present and correctly placed [26 required-red + 4 preservation], ownership union exact, 18 ids proven by clause (e) and 8 by clause (b2), 3 expected-uncollected files verified, no neutralized tests)` |
| `C:/Temp/av-kit/meu49-red.json` (218 KB) | The raw JSON report both clauses were evaluated against. |

The census line `no neutralized tests` is the **G36** half: it fails on a `.skip`/`.only`/
`.todo` or a conditional early return, so "Green" cannot be reached by defeating a test.

### Commands Executed

Every row below is the tree's **current** state (re-run at H1-2 after the last correction),
not row 10's numbers.

| Command | Exit | Key Output | Receipt |
|---------|------|------------|---------|
| `npm --prefix ui run typecheck` | 0 | `tsc --noEmit` clean | `meu49-x4f-typecheck.txt` |
| `npm --prefix ui run lint` | 0 | `eslint src/ tests/ --max-warnings 0` clean | `meu49-x4f-lint.txt` |
| `npm --prefix ui run test` | 0 | **492 passed** (57 files) — baseline 439 | `full-verify-vitest.txt` |
| `assert-mount-completeness.ps1 -Scope all` | 0 | `GATE PASS`, 178 checks, `PENDING` empty | `meu49-mount-gate.txt` |
| `npm --prefix ui run build` | 0 | electron-vite build ok; **no React Compiler bail-out** on `QueueList`/`QueueCard` (OQ-4 closes with nothing to record) | `meu49-x4c-build.txt` |
| `npm --prefix ui run test:e2e` | 0 | **81 passed**, 0 failed (10.3m) — runtime floor 79 | `meu49-full-e2e.txt` |
| `npm --prefix ui run test:e2e -- --list` | 0 | `Total: 81 tests in 12 files` | `meu49-e2e-list.txt` |
| `assert-plan-gates.ps1 -Gate E2eCensus` | 0 | `PASS` — static floor 73, each `E2E_REQUIRED_CASES` id in its owning spec, zero `dragTo(` | `meu49-e2e-census.txt` |
| `uv run pytest -q` | 0 | **509 passed** — backend untouched | `meu49-pytest.txt` |
| `meu_status.py render --check` | 0 | Drift check passed (58 MEUs, 12 phases) | `meu49-meu-status.txt` |
| `assert-plan-gates.ps1 -Gate BuildPlanAudit` | 0 | `PASS` after X5 | `build-plan-audit.txt` |
| `assert-plan-gates.ps1 -Gate ApiSkip` | 0 | `PASS` — `git status --porcelain -- packages/api` empty | `openapi-skip.txt` |
| `assert-plan-gates.ps1 -Gate Unchecked` | 0 | `PASS` — no implementation row open | `task-unchecked.txt` |
| six plan-local `-SelfTest` runs | 0 | markers / ACs / dispatch PASS; red-phase 18 cases; plan-gates 73 cases across 8 gates; census 11 cases | `meu49-selftest-*.txt` |

### Quality Gate Results

```
typecheck  clean          lint        clean (--max-warnings 0)
vitest     492 passed     pytest      509 passed
playwright 81/81 passed   mount gate  178 checks, PENDING empty
build      ok             drift       clean
```

---

## Execution-phase corrections in this MEU

Seven are recorded in the plan's §Execution-Phase Corrections (X1–X7). **X4 is the one a
reviewer should spend time on**, because it is a real product defect that the first fix for
it silently recreated. X6 and X7 landed *after* the review verdict, during closeout, and are
disclosed here rather than left to the diff: X6 widened `assert-exec-review-dispatch.ps1`'s
line-anchored `verdict:` pattern so the reviewer's own round-1 phrasing could be bound to its
dispatch (self-test 7 → 9 cases; the approved-token comparison that carries the anti-forgery
property is unchanged), and X7 spelled out task row H2-4's elided
`check_exec_review.py --expected-mode/--expected-target` flags, whose stale defaults failed
1 of the 8 closeout checks against a valid review. Neither touches product code.

`KeyboardSensor.handleKeyDown` scrolls-and-returns instead of moving when
`canScrollY && clamped !== requested`. X3 bounded the queue into its own scroller so the
clamp would stop being evaluated against the page shell's `<main>`. That was necessary and
insufficient: it never said **which** pane yields height. The page column is oversubscribed
at the app's own 1280×800 default window (739px of content against ~515px of controls), so a
pane must shrink, and at the flex default the deficit is split by content height — putting
the queue at **92px** (downloader) / **85px** (convert), below the ~124px the rule itself
names. The clamp was therefore re-created one level below where it was removed, AC-49.27 was
still 0 PUTs, and the tiny scroller also re-broke the three pointer cases X3 had just fixed,
since a 5% auto-scroll band on a 92px box is 4.6px.

X4 fixes the pane split explicitly (`QUEUE_SCROLL_CONTAINER_RULE` clause 4). Measured after,
on the same default window: scroller `clientHeight 280 == scrollHeight 280` and `<main>`
`699 == 699`, so **both** ancestors report `maxScroll: 0`, `canScrollY` is false at every
level, and an instrumented keyboard drag records **zero** `scrollTo` calls.

Shrinking the chrome to fit was considered and rejected: the same arithmetic fails again at
any smaller window, and the geometry is a property of the shipped default window rather than
a test artifact.

**AC-49.27's three settles were re-grounded on measured observables, not sleeps.**
Instrumentation showed the live region is *not* a usable settle — the pickup is announced at
t=140ms but the sensor's keydown listener is only registered at t=153ms, so an ArrowDown sent
in between is dropped entirely (`defaultPrevented: false`, zero PUTs). The spec now counts
`document` keydown registrations, waits for the ArrowDown's own announcement before the drop
(the drop resolves against dnd-kit's committed `over`; an early Space ends the drag on the
origin row and issues no PUT), and polls the focus assertion instead of reading it once.
**Every asserted value is unchanged** — these are synchronisation points, not assertions, so
G36 holds. None of the three races is reachable at human typing speed.

---

## Changed Files

> Sessions 21 and 22 are both uncommitted, so `git diff` against `HEAD` mixes MEU-45–47 with
> MEU-49 on the files both touched. The `Lines` column is the raw `git diff --numstat` delta
> for the file; rows marked † carry session-21 changes in that number as well. The `Summary`
> column describes **only** MEU-49's contribution.

**New modules (this MEU):**

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/lib/queue/reorder-body.ts` | add | 126 | `REORDER_BODY_MODULE` — single owner of `buildReorderBody` (moved verbatim) plus `buildReorderBodyToIndex` per `MOVE_TO_INDEX_CONTRACT` |
| `ui/src/renderer/src/lib/queue/reorder-single-flight.ts` | add | 244 | Framework-free gate over a plain boolean + module-level per-queue Map; external-store pair for subscribers |
| `ui/src/renderer/src/lib/queue/use-queue-reorder-held.ts` | add | 45 | The only React binding over that store (`useSyncExternalStore`); kept out of the command layer, which has no React import |
| `ui/src/renderer/src/components/queue/queue-dnd.ts` | add | 173 | `DND_ANNOUNCEMENT_CONTRACT` factory (all four handlers, position-based, 1-indexed) + `screenReaderInstructions` |
| `ui/tests/unit/reorder-body.test.ts` | add | 161 | AC-49.3–49.7 |
| `ui/tests/unit/reorder-single-flight.test.ts` | add | 72 | AC-49.31 |
| `ui/tests/unit/queue-dnd.test.ts` | add | 105 | AC-49.16, AC-49.17 — a new file so the Red oracle's baseline clause is not disturbed |

**Modified:**

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/components/queue/QueueCard.tsx` † | modify | +236/−17 | Drag handle as the canonical `Button` (first child, sibling of every other zone, `touch-none`, hover/focus reveal); `ALT_ARROW_SUPPRESSION_RULE`; handle `disabled` while the gate is held |
| `ui/src/renderer/src/components/queue/QueueList.tsx` † | modify | +301/−20 | Opt-in `onMoveToIndex` → `DndContext` + `SortableContext` wrapping (not merged into) the drop-zone container; `DND_AUTOSCROLL_CONFIG` |
| `ui/src/renderer/src/components/queue/QueueCardMenu.tsx` † | modify | +46/−8 | Present reorder items render `disabled` while the gate is held; absent items stay absent |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` † | modify | +412/−175 | `onMoveToIndex` wiring; X3/X4 height chain — `h-full min-h-0` root, controls pane `min-h-0 … overflow-auto`, region `flex-1 min-h-[20rem]`, `shrink-0` footer, `overflow-auto` wrapper around `QueueList` |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` † | modify | +380/−256 | Same wiring and the same height chain |
| `ui/src/renderer/src/features/downloader/download-commands.ts` † | modify | +215/−0 | `reorderDownloadToIndex`; every permutation entry point routed through `acquireQueueReorder` |
| `ui/src/renderer/src/features/converter/convert-commands.ts` † | modify | +213/−0 | `reorderConversionToIndex`; same gate routing |
| `ui/src/renderer/src/features/downloader/download-controls.ts` † | modify | +66/−33 | Re-exports `buildReorderBody` from the new module (reference identity) |
| `ui/src/renderer/src/features/converter/convert-controls.ts` † | modify | +100/−31 | Same re-export |
| `ui/src/renderer/src/lib/queue/use-queue-bulk.ts` † | modify | — | Gate held across the **whole** bulk fold, released after `refetch()` resolves |
| `ui/package.json`, `ui/package-lock.json` | modify | +7/−1 | `DND_PACKAGES` into `dependencies`; `TESTING_LIBRARY_PACKAGES` into `devDependencies` |
| `ui/vitest.config.ts` | modify | +1/−1 | `setupFiles` → `@testing-library/jest-dom/vitest` |
| `ui/tests/e2e/test-ids.ts` † | modify | +42/−17 | `DND_TESTIDS` registered |
| `ui/tests/e2e/download-queue.test.ts` † | modify | +1197/−211 | AC-49.25–49.28, AC-49.36, the `QUEUE_SCROLL_CONTAINER_RULE` geometry probe, and `watchKeydownListeners` |
| `ui/tests/e2e/convert-queue.test.ts` † | modify | +841/−77 | AC-49.29 and the matching geometry probe |
| `ui/tests/unit/queue-card.test.ts` † | modify | +676/−110 | AC-49.8–49.13; dependency guard narrowed to `/react-virtual/` with its in-place supersession comment |
| `ui/tests/unit/queue-primitives.test.ts` † | modify | +563/−93 | AC-49.14, AC-49.15, AC-49.18–49.20 |
| `ui/tests/unit/downloader-page.behavior.test.ts` † | modify | +1745/−88 | AC-49.21–49.24, AC-49.32–49.35, AC-49.37–49.39 |
| `ui/tests/unit/convert-page.behavior.test.ts` † | modify | +1627/−62 | AC-49.21–49.23, AC-49.32–49.35, AC-49.37, AC-49.38 |
| `ui/tests/unit/downloader-page.test.ts` † | modify | +160/−25 | X3/X4 className locks (**not** an AC — they exist so MEU-52 cannot paste the old mockup §04 string) |
| `ui/tests/unit/convert-page.test.ts` † | modify | +160/−33 | Same locks |
| 10 further `TL_MIGRATION_FILES` † | modify | — | `G37_RULE` adoption: `render`/`screen` + `userEvent.setup()`, retired mount surface deleted outright |
| `ui/tests/unit/helpers/user-event.ts` | **delete** | −(all) | The shim `G37_RULE` replaces; no file under `ui/` imports it |

**Plan and canon artifacts:** `named-sets.json` (`QUEUE_SCROLL_CONTAINER_RULE` clause 4,
`PHASE_EXIT_ASSERTIONS`), `implementation-plan.md` (X4, X5), `task.md`,
`assert-plan-gates.ps1` (X5 fixture), `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`
(MEU-49 → `approved`) and the rendered `meu-registry.md`,
`.agent/context/current-focus.md`, the two `docs/proposals/2026-09-03-*-page-layout-mockup.html`
§04 sections, and the Phase 11 grouping's "No Phase 10 reopening" bullet.

---

## Codex Validation Report

**Round 1 — `approved`, 0 findings.** Reviewer `gpt-5.6-sol` (high effort), dispatch
`exec-review-p10-queue-card-dnd-r1`. Full review:
[`2026-09-03-p10-queue-card-dnd-implementation-critical-review.md`](2026-09-03-p10-queue-card-dnd-implementation-critical-review.md).

The reviewer reproduced typecheck / lint / build clean, **492 passed in 57 files**, and
**509 passed** on pytest. It could not execute Playwright: its own host's Electron dies
before the first window (GPU subprocess exits `-1073741515`), which is the known
`E2E-SANDBOX-NODISPLAY` condition and an environment non-result, not evidence against a
behaviour — the 81/81 run above is from this tree. It substituted an independent runtime
check, driving the real dnd-kit sensors against the built renderer in headless Edge:

- Pointer drag of `dl-1` over `dl-3` left the file-drop container at `data-drag-state="idle"`
  with no overlay and emitted the exact body `{"job_ids":["dl-2","dl-3","dl-1","dl-4"]}`; a
  native file `dragenter` then moved the same container to `direct-hover` and rendered
  `queue-drop-overlay` without starting a row drag. Both directions of
  `DRAG_STATE_ISOLATION_RULE` therefore hold at runtime.
- The keyboard probe emitted `{"job_ids":["dl-2","dl-1","dl-3","dl-4"]}` and the position-2
  announcement **at viewport heights from 800px down to 300px** — an independent stress of
  X4 beyond the default window. Below 450px `<main>` becomes scrollable again, but the queue
  region holds at 320px and its scroller at 280px, so the ArrowDown still commits rather than
  being swallowed by the clamp.
- It examined AC-49.27's three waits specifically and found them observation-based
  synchronisation rather than sleeps, and that none weakens the asserted outcome.

### Recheck Protocol

1. Read Scope + the AC table.
2. Verify each AC against the Evidence section by `file:line`, not from this document's prose.
3. Re-run everything in Commands Executed and compare the output to the counts claimed here.
4. Run the quality gates independently.
5. Record findings below.

Where to spend the effort: the drag / keyboard / file-drop three-way interaction
(`DRAG_STATE_ISOLATION_RULE`), the permutation builders and the single-flight gate's
ownership boundaries, the accessibility contract (`WCAG_DRAG_RULE`, announcements,
`REORDER_FEEDBACK_TIER`), and §Execution-phase corrections X4 — not on process paperwork.

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

`approved` — round 1, 0 findings. "The implementation achieves that intent: the final-index
permutation is correct, the module-level gates cover every production reorder path and release
after reconciliation, the alternative controls remain honest while held, and X4 preserves a
usable keyboard geometry."

---

## Deferred Items

_None. OQ-5 is closed by the `G37_RULE` adoption in rows 2/2a rather than deferred; OQ-3
(retiring `MOUNT_GATE_SCRIPT`) and OQ-4 (React Compiler bail-out) are recorded in the
reflection, not deferred as work._

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-04 | claude-opus-5 | FIC written (task row 1): 39 ACs transcribed from the plan |
| Finalised | 2026-09-16 | cursor-grok-4.6-xhigh | Rows 2–12 + H1-1…H1-6 complete. All 39 ACs ✅. Corrections X3–X5 recorded. Gates: vitest 492, pytest 509, Playwright 81/81, mount 178, tsc/eslint/build/drift clean. Ready for independent execution review. |
