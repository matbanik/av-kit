---
date: "2026-09-03"
project: "2026-09-02-p10-queue-card-migration"
meu: "MEU-47"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-02-p10-queue-card-migration/implementation-plan.md"
build_plan_section: "bp10s10.7"
agent: "claude-opus-5"
reviewer: "gpt-5.6-sol"
predecessor: "2026-09-02-p10-queue-card-migration-MEU-46-handoff.md"
---

# Handoff: 2026-09-02-p10-queue-card-migration-MEU-47-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-47 — `gui-queue-bulk`. The third and final mount of Phase 10's queue-card
surface: multi-select and bulk actions on **both** pages at once. `useQueueSelection`
implements `SELECTION_MODEL` (toggle, Shift+click range from the last anchor in render
order, Ctrl/Cmd+A over the **filtered** list, clear after a completed bulk action);
`SelectionCheckbox` and `QueueCard` are widened per `SELECTION_PRIMITIVE_EXTENSION` so
Shift+click has a production path rather than a test-only one; `bulk-reorder.ts` folds each
`PUT` from the **preceding successful** call per `BULK_REORDER_ALGORITHM`; `BulkActionBar`
renders `BULK_BAR_ACTIONS` sticky **above the list**; and `QueueSelectionHeader` supplies the
tri-state `queue-select-all` of `SELECTION_HEADER_CONTRACT`. `run-bulk.ts` (built in task
row 3a for `Clear finished`) is extended for the selection fan-out.

**Build Plan Section**: [10 §Selection and bulk model](../../../docs/build-plan/10-queue-card-ui.md#selection-and-bulk-model) (matrix item 10.7)

**Predecessor**: [`2026-09-02-p10-queue-card-migration-MEU-46-handoff.md`](2026-09-02-p10-queue-card-migration-MEU-46-handoff.md)

**Deliberately NOT in this MEU.** No new REST surface. `BULK_ENDPOINT_POLICY` is load-bearing:
`POST /{queue}/bulk` does not exist and this MEU may not invent it — every bulk action is a
client-side fan-out of the per-id endpoints MEU-45/46 already wired. A server-side bulk
endpoint, if ever warranted, is a new MEU, not a scope expansion here. No bulk move-up /
move-down (the spec's bar carries move-**top** / move-**bottom** only) and no bar-level
select-all (that affordance belongs to the header, per `SELECTION_HEADER_CONTRACT`).
`Clear finished` sweeps `CLEAR_FINISHED_SNAPSHOT_STATUSES`, explicitly **not** the wider
`TERMINAL_STATUSES` — sweeping the wider set would destroy failure evidence the user has not
yet seen. Transcript and TTS pages stay outside Phase 10.

**This MEU closes the phase gate.** AC-47.11 is the first and only run of
`MOUNT_GATE_SCRIPT -Scope all`; the 8 `PENDING (MEU-47)` rows that MEU-46's receipt carried
must become obligated-and-passing here, with an **empty** `PENDING` list.

---

## Acceptance Criteria

> **AC-table integrity (control C4).** All 15 plan ACs for MEU-47 (AC-47.1–47.11 including
> AC-47.1a, AC-47.5a, AC-47.7a and AC-47.10a) are transcribed below from
> `implementation-plan.md` §MEU-47 → Acceptance Criteria, each carrying its plan source
> label. No AC is dropped or deferred. `Test(s)` names the test that owns the criterion; the
> Red phase (task row 19) writes every one of them before any implementation.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-47.1 | unit | `useQueueSelection` implements `SELECTION_MODEL`: toggle, Shift+click inclusive range from the last anchor in render order, Ctrl/Cmd+A over the **filtered** list, clear after a completed bulk action. Negative: Shift+click with no prior anchor selects only the clicked row; ids that vanish from the envelope are pruned rather than acted on; Ctrl/Cmd+A with a filter applied selects only filtered rows. | Spec §Selection and bulk model | `ui/tests/unit/use-queue-selection.test.ts` — "AC-47.1 SELECTION_MODEL toggle / shift-range / select-all over the filtered list / clear after bulk" | ✅ |
| AC-47.1a | unit | `SELECTION_PRIMITIVE_EXTENSION`: `SelectionCheckbox.onChange` and `QueueCard.onSelectChange` are widened to forward a `{ shiftKey: boolean }` modifiers argument, and `SelectionCheckbox`'s `onClick` stops propagation **without** discarding that modifier state. Negative: today `onChange` is `(checked) => void` (`SelectionCheckbox.tsx:16`) and `onSelectChange` is `(id, checked) => void` (`QueueCard.tsx:93`), so AC-47.1's Shift+click range would be reachable only from a test harness and never from the running app; a signature that still drops `shiftKey` fails. | Research-backed (`SELECTION_PRIMITIVE_EXTENSION`) | `ui/tests/unit/queue-primitives.test.ts` — "AC-47.1a SelectionCheckbox and QueueCard forward { shiftKey } and stopPropagation keeps it" | ✅ |
| AC-47.2 | unit | A shared `runBulk(ids, fn)` helper implements `CLEAR_FINISHED_SEMANTICS` clauses 1–5: snapshot, independent per-id calls, continue-on-failure, successes kept, exactly one refetch after the fan-out settles. Negative: with 3 of 5 calls rejecting, the 2 successes persist, the refetch fires exactly once, and the result reports `2 succeeded / 3 failed`. | Spec §Clear finished | `ui/tests/unit/run-bulk.test.ts` — "AC-47.2 runBulk snapshots, continues on failure, refetches exactly once" | ✅ |
| AC-47.3 | integration | `runBulk`'s result feeds a `G35_RULE` partial-result toast stating the removed count, the failed-or-skipped count **and a reason per failure** — clause 7 of `CLEAR_FINISHED_SEMANTICS`. Tagged `integration` because it asserts the executor is actually wired to the live toast provider, which a pure unit test of `runBulk` cannot show. Negative: an all-success run shows a success toast, not a partial one; an all-failure run shows an error toast; a partial run whose toast omits the per-failure reasons fails clause 7. | Spec §Clear finished + `G35_RULE` | `ui/tests/unit/convert-page.behavior.test.ts` — "AC-47.3 a partial bulk run raises a G35 toast naming every failure reason" | ✅ |
| AC-47.4 | integration | `BulkActionBar` is **sticky above the list** — rendered inside the queue panel immediately above `QueueList`, `position: sticky` against the panel's scroll container — whenever the selection is non-empty, and unmounted when it is empty (`USER_LOCKS`). Negative: a viewport-bottom fixed bar fails ("sticky above the list … never a floating bottom bar"); with an empty selection the bar is absent from the DOM, not merely hidden. | Spec §Selection and bulk model:220-222 + Human-approved (`USER_LOCKS`) | `ui/tests/unit/bulk-action-bar.test.ts` — "AC-47.4 the bar is sticky inside the panel above QueueList and unmounts on an empty selection" | ✅ |
| AC-47.5 | integration | The bar exposes `bulk-selection-count` then exactly `BULK_BAR_ACTIONS` in that order (`bulk-retry`, `bulk-move-top`, `bulk-move-bottom`, `bulk-remove` destructive-variant, spacer, `bulk-clear-selection`); `bulk-retry` is enabled only when at least one selected row is in that page's requeueable set. Negative: a bar rendering `bulk-move-up`/`bulk-move-down` or a bar-level select-all fails; a selection of only `Skipped` rows disables `bulk-retry` (`USER_LOCKS`). | Spec §Selection and bulk model:220-223 | `ui/tests/unit/bulk-action-bar.test.ts` — "AC-47.5 the bar renders BULK_BAR_ACTIONS in order and gates bulk-retry on the requeueable set" | ✅ |
| AC-47.5a | integration | A header `SelectionCheckbox` (`queue-select-all`) sits above the list at all times per `SELECTION_HEADER_CONTRACT`: checked when every filtered row is selected, `indeterminate` when some are, unchecked when none are, with an "N items" count; toggling it acts on the **filtered** list. Negative: with 2 of 5 rows selected the input's `indeterminate` DOM property is `true` and `checked` is `false`; a header that only appears once a row is selected fails, since it is the control that starts the selection. | Spec §Selection and bulk model:215-217 | `ui/tests/unit/bulk-action-bar.test.ts` — "AC-47.5a queue-select-all is tri-state over the filtered list and is always mounted" | ✅ |
| AC-47.6 | integration | `bulk-remove` opens a `ConfirmModal` whose confirm button reads `Remove N items` (`USER_LOCKS` verb-labeled rule); dismissing issues no request. Negative: a confirm button labeled `OK` fails; dismissal issues zero `DELETE`s. | Human-approved (`USER_LOCKS`) + `G20_RULE` | `ui/tests/unit/convert-page.behavior.test.ts` — "AC-47.6 bulk-remove confirms with the verb label and dismissing issues no DELETE" | ✅ |
| AC-47.7 | integration | `Clear finished` in `TOOLBAR_CONTROLS` is wired to the AC-45.18 executor on **both** pages and implements all 7 clauses of `CLEAR_FINISHED_SEMANTICS` over `CLEAR_FINISHED_SNAPSHOT_STATUSES`. Negative: a queue holding a mix of `TERMINAL_STATUSES` rows issues `DELETE` only for the ids in `CLEAR_FINISHED_SNAPSHOT_STATUSES`; a row that becomes `Done` *after* the click is not removed (snapshot clause); a `404` on one id does not abort the run and every snapshotted id is still attempted exactly once; files on disk are untouched. | Spec §Clear finished:60,62-74 | `ui/tests/unit/convert-page.behavior.test.ts` + `ui/tests/unit/downloader-page.behavior.test.ts` — "AC-47.7 Clear finished sweeps only CLEAR_FINISHED_SNAPSHOT_STATUSES and survives a mid-run 404" | ✅ |
| AC-47.7a | unit | Bulk `move-top` / `move-bottom` follow `BULK_REORDER_ALGORITHM`: each `PUT` body is `REORDER_WIRE_CONTRACT`-shaped and is the fold of the **preceding successful** call, never of the stale initial order. Negative: computing all N permutations up front from the initial order makes step N clobber steps 1..N-1, since the endpoint takes an absolute permutation; a run where step 2 rejects must have step 3 fold from step 1's accepted order. | Research-backed (`BULK_REORDER_ALGORITHM`) | `ui/tests/unit/bulk-reorder.test.ts` — "AC-47.7a each PUT folds from the last accepted order, including when step 2 rejects" | ✅ |
| AC-47.8 | integration | Every bulk action is a client-side fan-out of existing per-id endpoints (`BULK_ENDPOINT_POLICY`). Negative: any request to a `/bulk` path fails the AC. | Spec §Selection and bulk model | `ui/tests/unit/convert-page.behavior.test.ts` — "AC-47.8 no bulk action issues a request to a /bulk path" | ✅ |
| AC-47.9 | integration | Selection interaction does not fight the card's nested controls: clicking the kebab, the primary action or a link inside a card does not toggle selection. Negative: clicking the kebab leaves the selection unchanged. | Spec §QueueCard anatomy (nested-interactive rule) | `ui/tests/unit/queue-card.test.ts` — "AC-47.9 nested controls do not toggle selection" | ✅ |
| AC-47.10 | integration | Both pages' E2E suites satisfy `BULK_CONTROL_E2E_OBLIGATION` in full — every one of the five `BULK_BAR_ACTIONS` is clicked and its outcome asserted (not just remove), plus a Clear finished run with a mixed queue. Negative (Round 2 F4): covering only bulk Remove and Clear finished left `bulk-retry` / `bulk-move-top` / `bulk-move-bottom` / `bulk-clear-selection` with no required assertion anywhere, so `-Scope all` could pass with four dead controls. | Local Canon `E2_RULE` + `BULK_CONTROL_E2E_OBLIGATION` | `ui/tests/e2e/convert-queue.test.ts`, `ui/tests/e2e/download-queue.test.ts` — one case per `BULK_BAR_ACTIONS` member + a mixed-queue Clear finished; `MOUNT_GATE_SCRIPT` clause 4 (c)+(d) | ✅ |
| AC-47.10a | integration | The `queue-select-all` header checkbox is exercised in all three `SELECTION_HEADER_CONTRACT` states (none → all, all → none, indeterminate → all) and the keyboard selection entry path is exercised end to end (focus a card, toggle its `SelectionCheckbox` by keyboard, assert the bar appears with the right count). Negative: a header checkbox asserted only for presence is a dead control under `MOUNT_GATE_CLAUSE_4` (c)+(d). | Local Canon `BULK_CONTROL_E2E_OBLIGATION` + `G34_RULE` | `ui/tests/e2e/convert-queue.test.ts`, `ui/tests/e2e/download-queue.test.ts` — "queue-select-all tri-state" + "keyboard selection entry" | ✅ |
| AC-47.11 | integration | `MOUNT_GATE_SCRIPT -Scope all` passes with an **empty** `PENDING` list — every home of every retired id obligated independently per `MOUNT_GATE_PHASE_SCOPES` — and the E2E suite is ≥ `E2E_BASELINE_COUNT`, 0 failed, EXIT=0. Negative: a non-empty `PENDING` list at this scope means a MEU-47 home was never built; a sibling home passing does not cover it. | Local Canon + `MOUNT_GATE_PHASE_SCOPES` | `assert-mount-completeness.ps1 -Scope all` (receipt `C:/Temp/av-kit/mount-gate-all.txt`); `npm --prefix ui run test:e2e` (receipt `C:/Temp/av-kit/meu47-e2e.txt`) | ✅ |

**Source-label census (Spec Sufficiency Gate):** Spec × 9, Local Canon × 3,
Research-backed × 2, Human-approved × 1 — every AC carries exactly one primary label and
none is labelled "best practice".

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

Red phase (task row 19) ran with all nine MEU-47 test files written and **no** implementation:
`use-queue-selection.ts`, `bulk-reorder.ts`, `use-queue-bulk.ts`, `BulkActionBar.tsx`,
`BulkResultToast.tsx` and `QueueSelectionHeader.tsx` did not exist, `run-bulk.ts` still
exported only the row-3a `Clear finished` sweep, and neither page rendered a selection
column. **25 tests failed across 8 files**, covering 12 distinct AC ids. Receipt:
`C:/Temp/av-kit/meu47-red.txt`.

AC-47.10, AC-47.10a and AC-47.11 are E2E/gate criteria and so are absent from the vitest Red
receipt; their Red evidence is the row-22 gate's first run, which failed 4 of 73 E2E cases
(W8-9, W8-10, W1-11, W1-12) against a mount gate that could not yet reach an empty `PENDING`.

| AC | Red failure | Green | Test file |
|----|-------------|-------|-----------|
| AC-47.1 (5) | `useQueueSelection is not a function` - toggle, shift-range, filtered select-all, pruning and render-order all unresolvable | PASS | `tests/unit/use-queue-selection.test.ts` |
| AC-47.1a, AC-43.8 (2) | `onChange` called with `(true)`, not `(true, { shiftKey })`; no `shiftKey` anywhere in `SelectionCheckbox.tsx` / `QueueCard.tsx` | PASS | `tests/unit/queue-primitives.test.ts` |
| AC-47.2 (2) | `runBulk is not a function` - the row-3a module exported only `clearFinished` | PASS | `tests/unit/run-bulk.test.ts` |
| AC-47.7a (5) | `bulkReorder is not a function`, including the test that pins the fold's sequencing | PASS | `tests/unit/bulk-reorder.test.ts` |
| AC-47.4, .5, .5a (3) | `BulkActionBar` / `QueueSelectionHeader` modules absent | PASS | `tests/unit/bulk-action-bar.test.ts` |
| AC-47.9 (1) | the card had no `selection-checkbox` to isolate from its nested controls | PASS | `tests/unit/queue-card.test.ts` |
| AC-47.1, .3, .6, .7, .8 (5) | no `bulk-action-bar` on the convert page; `Clear finished` still swept from the page rather than the executor | PASS | `tests/unit/convert-page.behavior.test.ts` |
| AC-47.4, AC-47.7 (2) | the same, on the downloader | PASS | `tests/unit/downloader-page.behavior.test.ts` |

| Phase | Test Files | Tests | Receipt |
|-------|-----------|-------|---------|
| Red | `8 failed \| 46 passed (54)` | `25 failed \| 403 passed (428)` | `C:/Temp/av-kit/meu47-red.txt` |
| Green | `54 passed (54)` | `428 passed (428)` | `C:/Temp/av-kit/row22-unit.txt` |

### Commands Executed

| # | Command | Exit | Key output | Receipt |
|---|---------|------|-----------|---------|
| 1 | row 19 (Red) - `npm --prefix ui run test` | 1 | `Tests 25 failed \| 403 passed (428)`; 12 distinct AC-47.x ids in the failure set | `meu47-red.txt` |
| 2 | row 20 (lib Green) - `npm --prefix ui run test` | 0 | `use-queue-selection` / `run-bulk` / `bulk-reorder` green | `meu47-row20.txt` |
| 3 | row 21 (page wiring) - `npm --prefix ui run test` | 0 | both page-behavior suites green | `meu47-bar.txt` |
| 4 | row 22 - `npm --prefix ui run typecheck` | 0 | `tsc --noEmit`, no diagnostics | `row22-typecheck.txt` |
| 5 | row 22 - `npm --prefix ui run lint` | 0 | `eslint --max-warnings 0`, clean | `row22-lint.txt` |
| 6 | row 22 - `npm --prefix ui run test` | 0 | `Test Files 54 passed (54)`; `Tests 428 passed (428)` | `row22-unit.txt` |
| 7 | row 22 - `assert-mount-completeness.ps1 -SelfTest` | 0 | `self-test cases: 14  failed: 0`; `SELFTEST PASS` | `row22-mountgate-selftest.txt` |
| 8 | row 22 - `assert-mount-completeness.ps1 -Scope all` | 0 | `checks passed: 178`; `GATE PASS  scope=all`; **`PENDING (0 obligations not yet owed at scope=all)` / `<none>`** (AC-47.11) | `row22-mountgate-all.txt` |
| 9 | row 22 - `npm --prefix ui run build` | 0 | renderer `built in 2.97s` | `row22-build.txt` |
| 10 | row 22 - `npx playwright test` (full suite, `ELECTRON_RUN_AS_NODE` unset) | 0 | **73 passed (8.8m)**, 0 failed, 0 skipped - floor `E2E_BASELINE_COUNT` = 59 | `row22-e2e.txt` |
| 11 | row 22 - `e2e-assertion-census.py` (after-census) | 0 | 117 -> **308** assertions, 12 -> **26** cases | `e2e-assertion-census-after.txt` |
| 12 | row 22 - `tools/run-meu-gate.ps1 -Scope all` | n/a | script **absent** - `ABSENT_VALIDATOR_RULE`, see below | n/a |

All receipts are under `C:/Temp/av-kit/`.

### Quality Gate Results

```
tsc --noEmit:              0 errors
eslint (src/ + tests/):    0 errors, 0 warnings (--max-warnings 0)
vitest:                    428 passed, 0 failed (54 files)
npm run build:             ok (renderer built in 2.97s)
playwright e2e:            73 passed, 0 failed, 0 skipped   (baseline floor 59)
mount gate (-SelfTest):    self-test cases 14, failed 0, SELFTEST PASS
mount gate (-Scope all):   checks passed 178, GATE PASS  scope=all
  -> PENDING (0 obligations not yet owed at scope=all)   <none>      [AC-47.11]
e2e assertion census:      117 -> 308 assertions, 12 -> 26 cases
```

> **`ABSENT_VALIDATOR_RULE` applied.** `tools/run-meu-gate.ps1` does not exist in this tree,
> so row 22's `MEU_GATE` ran as its constituent commands (typecheck / lint / vitest / build),
> exactly as rows 9 and 16 did for MEU-45 and MEU-46. Task.md SS Project-Specific Execution
> Notes pre-authorises the substitution; the absence is **not** a `[B]`, and the wrapper was
> deliberately not authored mid-MEU - putting a brand-new untested script on the gate path is
> the opposite of what a gate is for.

---

## Changed Files

Nothing in this project is committed yet, so a `git diff --stat` against `HEAD` attributes
MEU-45 and MEU-46 lines to MEU-47 as well (27 files, +5179/-1135 for the three MEUs
together). Files this MEU **created** therefore carry their exact size; files it **modified**
carry the MEU-47 change rather than a stat that would double-count its predecessors.

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/lib/queue/use-queue-selection.ts` | new | 172 | `SELECTION_MODEL`: toggle, Shift+range from the anchor in render order, select-all over the **filtered** list, pruning of ids that leave the envelope |
| `ui/src/renderer/src/lib/queue/bulk-reorder.ts` | new | 84 | `BULK_REORDER_ALGORITHM` - the fold, walked reversed for `top` and in render order for `bottom`, advanced only by a resolved request |
| `ui/src/renderer/src/lib/queue/use-queue-bulk.ts` | new | 232 | The one hook both pages mount: selection + eligibility + the five bar actions + the G35 note. `BULK_CONTROL_E2E_OBLIGATION` demands identical behaviour on both pages, and a second copy is precisely where they would diverge |
| `ui/src/renderer/src/components/queue/BulkActionBar.tsx` | new | 126 | `BULK_BAR_ACTIONS` in order, sticky **above** the list, unmounted on an empty selection |
| `ui/src/renderer/src/components/queue/QueueSelectionHeader.tsx` | new | 61 | `SELECTION_HEADER_CONTRACT` - always mounted, tri-state, "N items" |
| `ui/src/renderer/src/components/queue/BulkResultToast.tsx` | new | 60 | The `G35_RULE` partial-result surface: counts plus a reason per failure |
| `ui/src/renderer/src/lib/queue/run-bulk.ts` | modify | 202 total | Widened from the row-3a sweep into the shared fan-out: caller-named verb, the clause-6 reconcile moved inside, and the `dependent` dispatch flag (Disclosure 2) |
| `ui/src/renderer/src/components/ui/SelectionCheckbox.tsx` | modify | +`{ shiftKey }` | `SELECTION_PRIMITIVE_EXTENSION` - `onChange(checked, modifiers)`, and `stopPropagation` no longer discards the modifier |
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modify | +`{ shiftKey }` | `onSelectChange(id, checked, modifiers)`; nested controls stay isolated from selection (AC-47.9) |
| `ui/src/renderer/src/components/queue/QueueList.tsx` | modify | selection pass-through | `selectable` / `selectedIds` / `onSelectChange` reach every row |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | +~70 | Mounts the header + bar + toast above `QueueList` inside `convert-queue-region`; `confirmCopy` centralises the three confirm kinds; `Clear finished` delegates to the executor |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | +~70 | The same wiring against `DOWNLOAD_REQUEUEABLE_STATUSES` in `download-queue-region` |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | modify | +2 exports | `resetConversionOnly` / `removeConversionOnly` - the non-reconciling primitives a fan-out is handed (Disclosure 3) |
| `ui/src/renderer/src/features/downloader/download-commands.ts` | modify | +2 exports | `resetDownloadOnly` / `removeDownloadOnly`, same contract |
| `ui/tests/e2e/test-ids.ts` | modify | +10 ids | `queue-select-all`, `bulk-action-bar`, `bulk-selection-count`, `bulk-retry`, `bulk-move-top`, `bulk-move-bottom`, `bulk-remove`, `bulk-clear-selection`, `bulk-toast`, `bulk-toast-dismiss` |
| `ui/tests/unit/use-queue-selection.test.ts` | new | 257 | AC-47.1 |
| `ui/tests/unit/bulk-reorder.test.ts` | new | 191 | AC-47.7a, including "the next request is built only after the previous settles" |
| `ui/tests/unit/bulk-action-bar.test.ts` | new | 328 | AC-47.4, AC-47.5, AC-47.5a |
| `ui/tests/unit/run-bulk.test.ts` | modify | 282 total | AC-47.2 added to the MEU-45 clause suite |
| `ui/tests/unit/queue-card.test.ts` | modify | +AC-47.9 | Nested-control isolation, one assertion per inner control |
| `ui/tests/unit/queue-primitives.test.ts` | modify | +AC-47.1a | And AC-43.8 retargeted onto the widened signature (Disclosure 1) |
| `ui/tests/unit/convert-page.behavior.test.ts` | modify | +AC-47.1/.3/.6/.7/.8 | The convert page's bulk block |
| `ui/tests/unit/downloader-page.behavior.test.ts` | modify | +AC-47.4/.7 | The downloader's |
| `ui/tests/e2e/convert-queue.test.ts` | modify | +W8-9 .. W8-12 | Every `BULK_BAR_ACTIONS` member clicked with its outcome asserted, plus the tri-state header and the keyboard entry path |
| `ui/tests/e2e/download-queue.test.ts` | modify | +W1-11 .. W1-14 | The same four cases on the downloader - `BULK_CONTROL_E2E_OBLIGATION` is per page, not per control |

The bar is mounted **inside** the queue region, above the list, and the region owns the
Ctrl/Cmd+A chord so select-all works from a focused card without stealing the shortcut from
the URL field above it (`USER_LOCKS` lock 1):

```diff
+      <div className="flex flex-col gap-2" data-testid="convert-queue-region" onKeyDown={bulk.onKeyDown}>
+        <QueueSelectionHeader
+          total={cards.length}
+          selectedCount={bulk.selection.count}
+          onToggleAll={bulk.onToggleAll}
+          ariaLabel="Select all conversions"
+        />
+        <BulkActionBar
+          selectedStatuses={bulk.selectedStatuses}
+          requeueableStatuses={CONVERT_REQUEUEABLE_STATUSES}
+          onRetry={bulk.retrySelected}
+          onMoveTop={() => { bulk.moveSelected('top') }}
+          onMoveBottom={() => { bulk.moveSelected('bottom') }}
+          onRemove={() => { setConfirm({ kind: 'bulk-remove' }) }}
+          onClearSelection={bulk.selection.clear}
+        />
+        <BulkResultToast result={bulk.note} onDismiss={bulk.dismissNote} />
         <QueueList
           items={cards}
-          selectable={false}
+          selectable
+          selectedIds={bulk.selection.selectedIds}
+          onSelectChange={bulk.onSelectChange}
           ...
         />
+      </div>
```

`runBulk`'s dispatch mode (Disclosure 2):

```diff
-  for (const id of attempted) {
-    try {
-      await run(id)
-      succeeded.push(id)
-    } catch (error) {
-      failed.push({ id, reason: reasonFor(error) })
-    }
-  }
+  if (dependent) {
+    for (const id of attempted) { /* the reorder fold, unchanged */ }
+  } else {
+    // `map` invokes `run` for every id in one synchronous pass, so the requests
+    // leave together and the queue is never observable half-applied between
+    // them. `allSettled` then reports in INPUT order regardless of which
+    // answered first, which keeps succeeded/failed - and the G35 message built
+    // from them - in the order the user's rows are listed.
+    const outcomes = await Promise.allSettled(attempted.map((id) => run(id)))
+    outcomes.forEach((outcome, index) => { ... })
+  }
```

---

## Disclosures

1. **AC-43.8's assertion was retargeted, not weakened.** `SELECTION_PRIMITIVE_EXTENSION`
   widens `SelectionCheckbox.onChange` from `(checked)` to `(checked, modifiers)`, so MEU-43's
   exact-arity assertion `toHaveBeenCalledWith(true)` became
   `toHaveBeenCalledWith(true, { shiftKey: false })`. The capability it pins - the checkbox
   reports exactly what changed and nothing more - is unchanged, and the plain-click arm now
   additionally proves the modifier arrives as `false` rather than `undefined`. This is the
   only pre-existing assertion MEU-47 touched, and it was edited because the *contract*
   changed under it, not to make a failing run pass.

2. **`runBulk` now issues independent requests together; the reorder fold opts out.**
   Serialising the fan-out made one user gesture arrive at the queue as N separate mutations
   spread over N round trips, with the list visibly rewriting itself between them - and
   W8-9 / W1-11 caught exactly that: the first row's `POST /{queue}/{id}/reset` was already
   observable while the second had not yet been issued. `runBulk` therefore hands every
   request to the transport in one synchronous pass by default (`Promise.allSettled`, which
   reports in **input** order, so `succeeded` / `failed` / the G35 message stay in the user's
   row order), and `bulkReorder` - the single caller whose step k is *built from* step k-1's
   accepted order - passes `dependent: true`. AC-47.7a's "requests are sequential" test is
   green **because** of that flag, not in spite of it. No test assertion was changed to reach
   this; the fix is entirely in production code.

3. **The per-id commands were split into reconciling and bare forms.** `resetConversion`
   invalidates the query cache after its `POST`, which is right for a single-row gesture and
   wrong inside a fan-out: `CLEAR_FINISHED_SEMANTICS` clause 6 gives `runBulk` exactly **one**
   reconcile after the whole run settles, so a per-row invalidation would be N redundant
   refetches interleaved between the requests. `resetConversionOnly` / `removeConversionOnly`
   (and the downloader's pair) are the primitives the fan-out is handed; the reconciling
   wrappers now delegate to them, so the single-row path is behaviourally identical.

4. **A bulk move releases the selection only when the queue actually moved.**
   `SELECTION_MODEL` clears after a *completed* bulk action, but a move whose every request
   was rejected - or whose rows were already at that edge - completed nothing, and punishing
   a no-op by dropping the selection is the one outcome the user certainly did not ask for.
   `moveSelected` reconciles first and compares the post-reconcile order against the order it
   captured before the action, clearing only on a difference. Retry and Remove clear
   unconditionally: they always change the rows they touched.

5. **The retired-id census lines legitimately read zero; the mount gate is what replaces
   them.** `E2E_ASSERTION_CENSUS_RULE` says no capability may fall to zero assertions. The
   census attributes an assertion to a capability by the **testid it references**, so every
   `retired:*` line necessarily falls to zero once the rewrite re-homes those ids - that is
   what the rewrite *is*. The same holds for the two `page:` lines of the retired downloader
   table surface (`queue-table` 1 -> 0, `queue-row` 2 -> 0), which the gate itself accounts
   for under clause 8 (`queue-row` -> its `RETIRED_TESTIDS` successor `queue-card`,
   `queue-table` -> `queue-list`); those successors rose 0 -> 16 and 0 -> 1, and
   `page:convert-queue-row` rose 2 -> 15. Every other capability rose or held. The binding
   evidence that nothing lost coverage is `-Scope all`'s 178 checks with an **empty**
   `PENDING` list - clause 4 (c)+(d) requires each home to be located, interacted with, and
   its outcome asserted - alongside the totals, 117 -> 308 assertions over 12 -> 26 cases.
   Before/after: `C:/Temp/av-kit/e2e-assertion-census-before.txt`, `-after.txt`.

6. **The four E2E failures in the row-22 gate's first run were fixed in production code.**
   W8-10 / W1-12 (reorder) failed because the selection survived a confirmed move, so the
   next two row clicks left four rows selected - fixed by Disclosure 4. W8-9 / W1-11 (retry)
   failed for the dispatch reason in Disclosure 2, which was diagnosed with a throwaway
   instrumentation spec (deleted after use) proving both POSTs were in fact issued. Two
   intermediate attempts were **reverted** rather than shipped: an unconditional clear after a
   move broke unit AC-47.8, and clearing on queue-identity change inside `useQueueSelection`
   broke AC-47.1, which requires that re-ordering the `items` prop *preserve* the selection.
   Both reverts were driven by frozen tests; neither test was edited.

7. **`ELECTRON_RUN_AS_NODE` must be unset for the E2E suite.** Unchanged from MEU-46 - this
   shell inherits `ELECTRON_RUN_AS_NODE=1` from the editor's extension host, which makes
   `electron.exe` parse Chromium flags as Node flags and fails every launch. Unset for the
   run, the suite is 73/73. This is a harness quirk, not `E2E-SANDBOX-NODISPLAY`, and not a
   `[B]`.

8. **MEU-44/45/46 components edited here.** Only the two `SELECTION_PRIMITIVE_EXTENSION`
   signatures (`SelectionCheckbox`, `QueueCard`) and `QueueList`'s pass-through of them.
   `QueueToolbar`, `QueueCardMenu`, `ConfirmModal` and the shell-IPC ledger were consumed
   unchanged.

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/execution-critical-review`._

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| _none yet_ | | | | | |

### Verdict

_pending_

---

## Deferred Items

_None. All 15 MEU-47 acceptance criteria are implemented and evidenced above; nothing
was deferred, narrowed or marked `[B]`._

---

## Round 1 Corrections (exec-review `changes_required`, 6 findings)

Round 1 returned `changes_required` with 6 findings. Five were code defects; one
(Finding 5) turned out to be a defect in this plan's own `named-sets.json`. Every
code correction is covered by a regression test that was **proved Red without its
fix** - each fix was reverted programmatically, the new test observed to fail, and
the fix restored (receipts `C:/Temp/av-kit/redcheck.txt`, `f4-red.txt`,
`r2-sel-red.txt`).

| # | Sev | Finding | Correction | Regression test | Red receipt |
|---|-----|---------|-----------|-----------------|-------------|
| 1 | High | AC-47.1 pruned only the derived projection, so a vanished id stayed in the backing set and a vanished anchor was never released | `use-queue-selection.ts` prunes the backing `Set` and the anchor **during render** on a membership change (`sameMembers` - order-insensitive, so a pure reorder costs the user neither ticks nor anchor) | 3 cases in `use-queue-selection.test.ts` | `r2-sel-red.txt` - `2 failed \| 6 passed` |
| 2 | High | `moveSelected` cleared the selection only when the reconciled order differed, making a frozen rule depend on react-query render timing and leaving a stale selection after a total failure | `await refetch(); clear()` - unconditional, per `SELECTION_MODEL` "cleared after a bulk action completes" | `R1-F2` on both pages | `redcheck.txt` - 2 failed |
| 3 | High | Both pages handed `bulkReorder` the **reconciling** single-row command, so an N-step fold issued N invalidations inside one gesture | Split into `reorderConversionOnly` / `reorderDownloadOnly` (bare PUT) folded by `bulkReorder`, with `reorderConversion` / `reorderDownload` delegating then invalidating for single-row gestures | `R1-F3` on both pages: `puts > 1`, `lists == 1`, and the reconcile ordered after the last PUT | `redcheck.txt` - 2 failed |
| 4 | High | AC-45.1's placeholder-filtering contract was not implemented - see MEU-45 handoff | `composeMeta` filters the complete `[base, ...segments]` sequence; new exported `META_PLACEHOLDER` | `R1-F4` in `queue-card.test.ts` | `f4-red.txt` |
| 5 | High | Mounted controls violate `G32_RULE`'s "frozen 44x44 CSS-pixel target" | **Not a code defect.** See Disclosure R1-A below | - | - |
| 6 | Med | Bulk actions stayed enabled while the page was busy | `BulkActionBar` takes `busy`; `bulk-retry`, `bulk-move-top`, `bulk-move-bottom`, `bulk-remove` disable, `bulk-clear-selection` stays live | `R1-F6` on both pages | `redcheck.txt` - 2 failed |

### Disclosure R1-A - Finding 5 was corrected in the plan artifact, not the code

`named-sets.json` stated `G32_RULE.value` = "Interactive targets are at least
44x44 CSS px", sourced to `.agent/docs/emerging-standards.md:1098`. That line
defines G32 as **"CSS Variable Tokens Only (No Raw Hex in className)"**. No 44px
target is stated anywhere in `emerging-standards.md` or in
`docs/build-plan/10-queue-card-ui.md`; the value was a transcription defect
introduced when the named set was written. Every AC citing `G32_RULE` (AC-45.3,
45.10, 45.19, 45.19a, 46.6, 46.14, 47.4, 47.5, 47.5a) tests the token rule, and
enforcing a 44px minimum would directly contradict the frozen `G34_RULE`
(`sm: h-7`, `md: h-9`, `lg: h-11`). The named set was corrected to its cited
source verbatim, with a `note` recording the defect. **The reviewer should
re-derive this independently rather than take it on trust.**

### Disclosure R1-B - one Green-phase test SETUP change

`AC-47.8` chained three bulk verbs off a single `queue-select-all` tick. That only
worked because of Finding 2's bug. Its **setup** now re-ticks before each verb;
its assertions are byte-identical. Disclosed because G36 forbids weakening a test
to make it pass - this is the opposite case, a test that had been passing on
buggy behaviour.

### Disclosure R1-C - two literal NUL bytes removed

`use-queue-bulk.ts` contained `order.join('\x00')` and
`latestOrder.current.join('\x00')` (intended as a space). Both lines were
deleted by the Finding 2 fix. A repo-wide scan of `ui/**/*.{ts,tsx,css,json,js}`
confirms no other source file contains a NUL. Not behavioural - the join separator
was never rendered - but a latent source defect worth naming.

### Disclosure R1-D - `tools/run-meu-gate.ps1` does not exist

`task.md` rows 22, H1-2 and H1-4 name `tools/run-meu-gate.ps1` as their validation
command. No such file is in the repo or in git history. The gate was re-run from
the authoritative `MEU_GATE` named set instead (`npm --prefix ui run typecheck`,
`lint`, `test` plus `assert-mount-completeness.ps1`), extended with `build` and
the Playwright suite.

### Post-correction gate - all green

| Stage | Result | Receipt |
|-------|--------|---------|
| `npm --prefix ui run typecheck` | EXIT 0, no errors | `C:/Temp/av-kit/r2-typecheck.txt` |
| `npm --prefix ui run lint` | EXIT 0, 0 errors / 0 warnings | `C:/Temp/av-kit/r2-lint.txt` |
| `npm --prefix ui run test` | **438 passed** / 54 files, EXIT 0 | `C:/Temp/av-kit/r2-unit.txt` |
| `assert-mount-completeness.ps1 -Scope all` | **178 checks**, `PENDING` 0, `GATE PASS scope=all` | `C:/Temp/av-kit/r2-mount.txt` |
| `npm --prefix ui run build` | EXIT 0 | `C:/Temp/av-kit/r2-build.txt` |
| `npm --prefix ui run test:e2e` | **73 passed**, EXIT 0 (>= `E2E_BASELINE_COUNT` 59) | `C:/Temp/av-kit/r2-e2e.txt` |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created (FIC) | 2026-09-03 | claude-opus-5 | Task row 18 — 15 acceptance criteria transcribed with source labels |
| Red | 2026-09-03 | claude-opus-5 | Task row 19 — 25 tests failing across 8 files, 12 AC ids (`meu47-red.txt`) |
| Green | 2026-09-03 | claude-opus-5 | Task rows 20–21 — lib layer, then both pages wired |
| Gate | 2026-09-03 | av-kit-verifier | Task row 22 — 428 unit / 73 E2E / mount gate `-Scope all` 178 checks, `PENDING` empty |
| Evidence bundle | 2026-09-03 | claude-opus-5 | Task row 23 — this handoff populated from the receipts |
| Round 1 corrections | 2026-09-03 | claude-opus-5 | Task row H1-7 - 6 findings; 5 code fixes with Red-proved regressions, 1 named-set correction; gate re-run 438 unit / 178 mount / 73 E2E |
| Approved | 2026-09-03 | gpt-5.6-sol | Exec review r2 `approved` / 0 findings - all 6 round-1 findings closed, Finding 5 independently invalidated at source; r3 re-verified an unchanged tree and restated the verdict in the dispatch final output (gate `assert-exec-review-dispatch.ps1` requires it there) |
