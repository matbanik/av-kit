---
date: "2026-09-02"
project: "2026-09-02-p10-queue-card-migration"
meu: "MEU-45"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-02-p10-queue-card-migration/implementation-plan.md"
build_plan_section: "bp10s10.5"
agent: "claude-opus-5"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-28-p10-queue-card-foundations-MEU-44-handoff.md"
---

# Handoff: 2026-09-02-p10-queue-card-migration-MEU-45-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-45 — `gui-convert-queue-migration`. Mount the MEU-44 card surface on the
**converter** page: `ConvertPage` drops the hand-rolled `ConvertQueueTable` and renders
`QueueList` + a new shared `QueueToolbar`, the per-id mutations move into the **existing**
`convert-commands.ts`, and the shared `lib/queue/run-bulk.ts` executor lands here — before
any toolbar mounts `Clear finished`, so no control is ever dead at a MEU boundary
(`NO_DEAD_CONTROL_RULE`). `QueueList` also gains the converter half of
`EMPTY_STATE_CONTRACT`, with the empty slot overridable by the host page so the downloader
can supply its own invitation in MEU-46.

**Build Plan Section**: [10 §Toolbar reduction](../../../docs/build-plan/10-queue-card-ui.md#toolbar-reduction) (matrix item 10.5)

**Predecessor**: [`2026-08-28-p10-queue-card-foundations-MEU-44-handoff.md`](2026-08-28-p10-queue-card-foundations-MEU-44-handoff.md)

**Deliberately NOT in this MEU.** The **downloader** page is untouched — `DownloaderPage.tsx`,
`DownloadQueueTable.tsx`, `download-commands.ts` and `download-controls.ts` all keep their
current behaviour, and `@tanstack/react-table` stays in `ui/package.json` because the
downloader still consumes it (MEU-46 removes both). No selection model, no checkboxes and no
bulk bar (MEU-47) — `MOUNT_GATE_SCRIPT -Scope convert` therefore reports the MEU-47 homes as
`PENDING (MEU-47)` rather than obligating them (`MOUNT_GATE_PHASE_SCOPES`). No new REST
surface: every command calls an endpoint that already exists. The downloader half of
`EMPTY_STATE_CONTRACT` (`queue-empty-invite`) is explicitly AC-46.14's, not this MEU's
(AC-45.19a).

---

## Acceptance Criteria

> **AC-table integrity (control C4).** All 22 plan ACs for MEU-45 (AC-45.1–45.20 including
> AC-45.4a and AC-45.19a) are transcribed below verbatim from
> `implementation-plan.md` §MEU-45 → Acceptance Criteria, each carrying its plan source label.
> No AC is dropped or deferred. `Test(s)` names the test that owns the criterion; the Red phase
> (task row 2) writes every one of them before any implementation.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-45.1 | unit | `QueueCard` accepts `metaSegments?: readonly string[]` and renders `[resolveMeta(job), ...metaSegments]` with empty/`—` segments dropped, joined by `META_SEPARATOR` (`META_SEGMENTS_CONTRACT`). | Research-backed (DEC-1) | `ui/tests/unit/queue-card.test.ts` — "AC-45.1 metaSegments append to resolveMeta and empty segments are dropped" | ✅ |
| AC-45.2 | unit | With no `onOpen` prop, the card's title/meta region renders with no `role`, no `tabIndex` and no `aria-label` (`DEAD_REGION_RULE`); with `onOpen`, all three are present and Enter/Space activate it. | Research-backed (`DEAD_REGION_RULE`) | `ui/tests/unit/queue-card.test.ts` — "AC-45.2 without onOpen the title region advertises no dead affordance" | ✅ |
| AC-45.3 | unit | New `QueueToolbar` component renders exactly `TOOLBAR_CONTROLS` inside `[data-testid="queue-toolbar"]`; `pause-resume` is a single button whose label/testid reflect `PAUSE_SCOPE` state; every control renders an icon **and** a persistent text label (`TOOLBAR_LABEL_RULE`). | Spec §Toolbar reduction | `ui/tests/unit/queue-toolbar.test.ts` — "AC-45.3 the toolbar renders exactly TOOLBAR_CONTROLS with persistent labels", "…pause-resume is one button whose label and testid follow PAUSE_SCOPE", "…the overflow menu holds QUEUE_OVERFLOW_MENU outside the four controls" | ✅ |
| AC-45.4 | unit | The **existing** `convert-commands.ts` (a live module whose `CONVERT_COMMANDS` palette map is consumed by `AppShell.tsx:3` and `commandRegistry.ts:2`) is **extended** with `resetConversion`, `removeConversion`, `reorderConversion` — each an async function that throws a typed error carrying the HTTP status (`COMMAND_MODULE_RULE`, `ERROR_SURFACE`). `clearConversions` already exists and is reused unchanged. | Local Canon (`COMMAND_MODULE_RULE`) | `ui/tests/unit/convert-commands.test.ts` — "AC-45.4 each new command rejects with the HTTP status in the message", "…each new command hits its existing endpoint and refreshes the list" | ✅ |
| AC-45.4a | unit | A regression test imports `convert-commands.ts` and asserts every name in `COMMAND_MODULE_PRESERVED_EXPORTS['convert-commands.ts']` is still defined, and that `CONVERT_PALETTE_IDS` is unchanged. | Local Canon (`COMMAND_MODULE_PRESERVED_EXPORTS`) | `ui/tests/unit/convert-commands.test.ts` — "AC-45.4a every COMMAND_MODULE_PRESERVED_EXPORTS name survives" | ✅ |
| AC-45.5 | unit | `convert-controls.ts` `controlEnabled('reset')` returns true for every member of `CONVERT_REQUEUEABLE_STATUSES` and false for every member of its complement; the test enumerates the conversion status enum so `REQUEUE_EXHAUSTIVENESS_RULE` holds. | Spec §Re-queue contract + `USER_LOCKS` | `ui/tests/unit/convert-controls.test.ts` — "AC-45.5 controlEnabled(reset) is exactly CONVERT_REQUEUEABLE_STATUSES over the full enum" | ✅ |
| AC-45.6 | integration | `ConvertPage` renders `QueueList` (testid `convert-queue`) with one `convert-queue-row` card per item; `[data-testid="queue-toolbar"]` contains exactly 4 interactive elements (DEC-2). | Spec §Toolbar reduction | `ui/tests/unit/convert-page.behavior.test.ts` — "AC-45.6 the page renders QueueList cards and a four-control toolbar, not a table" | ✅ |
| AC-45.7 | integration | `ConvertQueueTable.tsx` is deleted and nothing in `ui/src` references it or `@tanstack/react-table` from the converter feature. | Spec §Toolbar reduction | `ui/tests/unit/convert-page.test.ts:667` — "AC-45.7 ConvertQueueTable is deleted and the converter drops react-table"; `MOUNT_GATE_SCRIPT -Scope convert` clause 2 | ✅ |
| AC-45.8 | integration | The card kebab exposes `KEBAB_MENU_ORDER` in that order; unavailable actions are **absent**, never disabled; `copy-location` reads `Copy path` when `output_path` exists else `Copy URL`. | Spec §Kebab menu | `ui/tests/unit/convert-page.behavior.test.ts` — "AC-45.8 the kebab exposes KEBAB_MENU_ORDER with unavailable actions absent" | ✅ |
| AC-45.9 | integration | Kebab move actions call `reorderConversion`, which sends `REORDER_WIRE_CONTRACT` — the full `{ job_ids }` permutation produced by the existing `buildReorderBody(ids, id, direction)` (`convert-controls.ts:108-128`), not a `{ id, direction }` body. `Alt+ArrowUp` / `Alt+ArrowDown` on a focused card issue the same call with `up` / `down`. | Spec §Reorder model + `REORDER_WIRE_CONTRACT` | `ui/tests/unit/convert-page.behavior.test.ts` — "AC-45.9 move actions and Alt+Arrow send the full REORDER_WIRE_CONTRACT permutation"; `ui/tests/e2e/convert-queue.test.ts` W8-3 | ✅ |
| AC-45.10 | integration | The card primary action follows `PRIMARY_ACTION_MAP`; the in-flight row's control has accessible name `CANCEL_CONTROL_LABEL` and takes effect with **no** confirm; no card renders any label in `CANCEL_LABEL_FORBIDDEN`. | Spec §Primary action model + `USER_LOCKS` | `ui/tests/unit/convert-page.behavior.test.ts` — "AC-45.10 the primary action follows PRIMARY_ACTION_MAP and cancels without a confirm" | ✅ |
| AC-45.11 | integration | Remove uses the shared `ConfirmModal` (`G20_RULE`) with the verb-labeled confirm button `Remove` (`USER_LOCKS`); the hand-rolled `createPortal` confirm in `ConvertPage.tsx` is deleted and the testids follow `RETIRED_TESTIDS`. | Local Canon `G20_RULE` + `USER_LOCKS` | `ui/tests/unit/convert-page.behavior.test.ts` — "AC-45.11 Remove routes through the shared ConfirmModal with a verb label"; `ui/tests/e2e/convert-queue.test.ts` W8-4 | ✅ |
| AC-45.12 | integration | The legacy `STATUS_COLORS` map in `convert-controls.ts` is deleted; status colour comes from the shared `lib/queue/status-tokens.ts` fill+label pairing. | Spec §Card state precedence | `ui/tests/unit/convert-controls.test.ts` — "AC-45.12 STATUS_COLORS is gone and status colour comes from status-tokens" | ✅ |
| AC-45.13 | integration | `MOUNT_GATE_SCRIPT` exists, supports `-Scope convert\|downloader\|all` and `-SelfTest`, implements all **8** clauses of `MOUNT_COMPLETENESS_RULE` — clause 4 exactly as `MOUNT_GATE_CLAUSE_4` states, iterating the **per-page** sub-maps of `RETIRED_TOOLBAR_CONTROLS` and then every element of each id's home list, obligated per `MOUNT_GATE_PHASE_SCOPES` — and `-SelfTest` passes with at least one **negative** fixture per clause. | Local Canon (DEC-3) + `MOUNT_GATE_CLAUSE_4` | `assert-mount-completeness.ps1 -SelfTest` (receipt `C:/Temp/av-kit/mount-gate-selftest.txt`) | ✅ |
| AC-45.14 | integration | `RETIRED_GATE_SCRIPT` keeps its file and gains a header comment naming `MOUNT_GATE_SCRIPT` as its successor and stating it must not be run against a migrated tree. | Local Canon (DEC-3) | `assert-mount-completeness.ps1` clause check + receipt `C:/Temp/av-kit/retired-gate.txt` | ✅ |
| AC-45.15 | integration | `convert-queue.test.ts` is rewritten under `E2E_REWRITE_RULE`: `W8-3` and `W8-5` assert `TOOLBAR_CONTROLS` + the card surface, and **every key** of `RETIRED_TOOLBAR_CONTROLS.converter` gets a replacement that satisfies `MOUNT_GATE_CLAUSE_4` (c)+(d) — it performs the interaction and asserts the resulting request or DOM state. `W8-4`'s confirm flow uses the `RETIRED_TESTIDS` mapping. | Local Canon `E2E_REWRITE_RULE` + `E2_RULE` | `ui/tests/e2e/convert-queue.test.ts` W8-3/W8-4/W8-5 (rewritten); `MOUNT_GATE_SCRIPT` clause 4 (c)+(d) | ✅ |
| AC-45.16 | integration | All `NEW_TESTIDS` introduced by this MEU are registered in `ui/tests/e2e/test-ids.ts`, and every id in `PRESERVED_TESTIDS` is still registered. | Local Canon | `ui/tests/unit/convert-page.test.ts:688` — "AC-45.16 every NEW_TESTIDS id is registered and no PRESERVED id is dropped"; `MOUNT_GATE_SCRIPT` clause 5 | ✅ |
| AC-45.17 | unit | A pure `convertMetaSegments(item)` returns `CONVERT_META_SEGMENTS` — kind label and mode label always, speed and ETA **whenever the field is non-null, regardless of status** — so the Kind/Mode/Speed/ETA columns of the deleted `ConvertQueueTable` survive as card meta. | Spec §QueueCard anatomy + Local Canon (`CONVERT_META_SEGMENTS`) | `ui/tests/unit/convert-controls.test.ts` — "AC-45.17 convertMetaSegments returns CONVERT_META_SEGMENTS with null fields dropped" | ✅ |
| AC-45.18 | unit | A shared `runBulk(ids, fn)` executor and a `clearFinished(queue)` built on it land **in this MEU**, before any toolbar is mounted, implementing `CLEAR_FINISHED_SEMANTICS` clauses 1-7 over `CLEAR_FINISHED_SNAPSHOT_STATUSES`. | Local Canon (`NO_DEAD_CONTROL_RULE`) | `ui/tests/unit/run-bulk.test.ts` — "AC-45.18 runBulk/clearFinished satisfy all 7 CLEAR_FINISHED_SEMANTICS clauses", "…an all-success run still reports counts and refetches exactly once" | ✅ |
| AC-45.19 | integration | `QueueList` implements the **converter** half of `EMPTY_STATE_CONTRACT`: with `items=[]` it renders `EmptyDropZone` (`queue-empty-dropzone`) including the `Browse…` button; with items it renders the list plus the compact `queue-drop-strip`. Both `onBrowse` and `onDropFiles` route to the page's **existing** production intake — `window.api.showFilesDialog(CONVERT_DIALOG_FILTERS)` feeding the same `staging` state that backs today's `convert-browse` button (`ConvertPage.tsx:470-484`), which is itself untouched — the staging drop zone and the queue empty state share the handler, not the testid. The empty-state button carries `queue-empty-browse` via `EmptyDropZone`'s existing `browseTestId` prop (`EmptyDropZone.tsx:190`). | Spec §Empty state and drop targets | `ui/tests/unit/queue-list.test.ts` — "AC-45.19 QueueList renders EmptyDropZone when empty and the drop strip when not"; `ui/tests/e2e/convert-queue.test.ts` | ✅ |
| AC-45.19a | integration | The **downloader** half of `EMPTY_STATE_CONTRACT` is explicitly NOT this component's job: `QueueList` takes the empty-state slot as a prop so `DownloaderPage` can supply `queue-empty-invite` instead (AC-46.14). `QueueList` renders no `queue-empty-dropzone` when the host supplies its own empty slot. | Local Canon (`EMPTY_STATE_CONTRACT`) | `ui/tests/unit/queue-list.test.ts` — "AC-45.19a a host-supplied empty slot replaces EmptyDropZone entirely" | ✅ |
| AC-45.20 | integration | Before the first E2E rewrite, `E2E_ASSERTION_CENSUS_RULE`'s before-census is captured to `C:/Temp/av-kit/e2e-assertion-census-before.txt` and referenced by the handoff. | Local Canon (`E2E_ASSERTION_CENSUS_RULE`) | Census receipt `C:/Temp/av-kit/e2e-assertion-census-before.txt` | ✅ |

**Source-label census (Spec Sufficiency Gate):** Spec × 10, Local Canon × 10,
Research-backed × 2, Human-approved × 0 — every AC carries exactly one label and none is
labelled "best practice".

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

Red phase (task row 2) ran with all six MEU-45 test files written and no implementation:
`QueueToolbar.tsx`, `run-bulk.ts`, the three new `convert-commands` exports, the
`convert-controls` helpers and the `ConvertPage` rewrite were all absent. 27 tests failed —
21 of them new MEU-45 tests, 6 of them **pre-existing tests that MEU-45 supersedes** (they
assert the retired table surface and must be rewritten under `E2E_REWRITE_RULE`/G36, never
deleted). Receipt: `C:/Temp/av-kit/meu45-red.txt`.

| Test | Red Output | Green Output | File:Line |
|------|-----------|--------------|-----------|
| AC-45.1, AC-45.2 (2 tests) | `metaSegments` prop not rendered; title region still advertised a dead affordance | PASS | `ui/tests/unit/queue-card.test.ts` |
| AC-45.3 (3 tests) | `Error: Cannot find module '…/components/queue/QueueToolbar'` | PASS | `ui/tests/unit/queue-toolbar.test.ts` |
| AC-45.4, AC-45.4a (3 tests) | `resetConversion is not a function` | PASS | `ui/tests/unit/convert-commands.test.ts` |
| AC-45.5, AC-45.12, AC-45.17 (3 tests) | `convertMetaSegments is not a function`; `STATUS_COLORS` still exported | PASS | `ui/tests/unit/convert-controls.test.ts` |
| AC-45.6, AC-45.8, AC-45.9, AC-45.10, AC-45.11 (5 tests) | `Unable to find an element by: [data-testid="convert-queue-row"]` | PASS | `ui/tests/unit/convert-page.behavior.test.ts` |
| AC-45.7, AC-45.16 (2 tests) | `ConvertQueueTable.tsx` still on disk; `NEW_TESTIDS` unregistered | PASS | `ui/tests/unit/convert-page.test.ts:667,688` |
| AC-45.18 (2 tests) | `Error: Cannot find module '…/lib/queue/run-bulk'` | PASS | `ui/tests/unit/run-bulk.test.ts` |
| AC-45.19, AC-45.19a (2 tests) | `queue-empty-dropzone` absent; host empty slot prop unsupported | PASS | `ui/tests/unit/queue-list.test.ts` |
| **Superseded** — AC-23.19, AC-33.10, AC-33.14, AC-33.19, AC-43.2, AC-44.13 (6 tests) | assert the retired `ConvertQueueTable` surface / the old audit + status maps | PASS after rewrite (assertions **retargeted**, never removed — see Disclosure 2) | `gui-actions-audit.test.ts`, `convert-page.test.ts`, `queue-primitives.test.ts`, `queue-card.test.ts` |
| Red totals | `Tests 27 failed \| 361 passed (388)`; `Test Files 10 failed \| 38 passed (48)` | `Tests 391 passed (391)`; `Test Files 49 passed (49)` | `C:/Temp/av-kit/meu45-red.txt` → `…/vitest5.txt` |

The 388 → 391 delta is exactly the three tests in the new `ui/tests/unit/shell-ipc-ledger.test.ts`
(Disclosure 3), written after the Red receipt was captured.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| row 2 (Red) — `npm --prefix ui run test` | 1 | `Tests 27 failed \| 361 passed (388)`; 18 distinct `AC-45.x` ids in the failure set |
| row 4 — `assert-mount-completeness.ps1 -SelfTest` | 0 | `self-test cases: 14  failed: 0`; `SELFTEST PASS` (>= 1 negative fixture per clause, incl. c4a-c4d) |
| row 5 — `e2e-assertion-census.py <repo-root>` (before-census, AC-45.20) | 0 | 135 lines captured to `e2e-assertion-census-before.txt` |
| row 9 — `npm --prefix ui run typecheck` | 0 | `tsc --noEmit`, no diagnostics |
| row 9 — `npm --prefix ui run lint` | 0 | `eslint src/ tests/ --max-warnings 0`, clean |
| row 9 — `npm --prefix ui run test` | 0 | `Test Files 49 passed (49)`; `Tests 391 passed (391)` |
| row 9 — `assert-mount-completeness.ps1 -Scope convert` | 0 | `checks passed: 90`; `GATE PASS scope=convert` (42 rows `PENDING (MEU-46/47)`) |
| row 9 — `npm --prefix ui run build` | 0 | `built in 2.87s` (`ConvertPage-C01Z0bnp.js` 87.72 kB) |
| row 9 — `npm --prefix ui run test:e2e` | 0 | **61 passed (6.2m)**, 0 failed, 0 skipped — floor `E2E_BASELINE_COUNT` = 59 |
| row 9a — three closeout checks `-SelfTest` | 0 | markers `SELFTEST PASS` (3 cases); ACs `SELFTEST PASS`; dispatch `SELFTEST PASS` (7 cases, 6 seeded negatives) |
| row 9a — `closeout-checks-present.txt` | 0 | `PASS: closeout checks present and parseable` |

Receipts, all under `C:/Temp/av-kit/`: `meu45-red.txt`, `mount-gate-selftest.txt`,
`e2e-assertion-census-before.txt`, `retired-gate.txt`, `meu45-typecheck3.txt`, `lint5.txt`,
`vitest5.txt`, `mount-gate-convert2.txt`, `meu45-e2e-build4.txt`, `meu45-e2e4.txt`,
`exec-dispatch-selftest.txt`, `closeout-checks-present.txt`.

### Quality Gate Results

```
tsc --noEmit:            0 errors
eslint (src/ + tests/):  0 errors, 0 warnings (--max-warnings 0)
vitest:                  391 passed, 0 failed (49 files)
npm run build:           ok (renderer built in 2.87s)
playwright e2e:          61 passed, 0 failed, 0 skipped  (baseline floor 59)
mount gate (convert):    checks passed 90, GATE PASS
mount gate self-test:    14 cases, 0 failed (negative fixture per clause)
retired gate header:     2 successor references present
closeout checks:         3/3 present, parseable, self-tests pass
```

> **`ABSENT_VALIDATOR_RULE` applied.** `tools/run-meu-gate.ps1` does not exist in this tree,
> so row 9's `MEU_GATE` was executed as its four constituent commands individually rather
> than through a wrapper. Creating the wrapper is optional convenience, not an AC — its
> absence is **not** a `[B]`.

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/converter/ConvertQueueTable.tsx` | deleted | -126 | The hand-rolled `@tanstack/react-table` queue table (AC-45.7) |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modified | 464 changed | Renders `QueueList` + `QueueToolbar`; hand-rolled `createPortal` confirm replaced by the shared `ConfirmModal`; Alt+Arrow reorder; shell IPC ledger call |
| `ui/src/renderer/src/components/queue/QueueToolbar.tsx` | new | 257 | `TOOLBAR_CONTROLS` — Start, one Pause/Resume toggle, Clear finished, overflow — every control an icon **plus** a persistent label |
| `ui/src/renderer/src/lib/queue/run-bulk.ts` | new | 144 | `runBulk(ids, fn)` + `clearFinished(queue)` over `CLEAR_FINISHED_STATUSES`, all 7 `CLEAR_FINISHED_SEMANTICS` clauses |
| `ui/src/renderer/src/lib/queue/shell-ipc-ledger.ts` | new | 36 | `recordShellIpc` — E2E observation seam for the frozen `contextBridge` (Disclosure 3) |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | modified | +100 | `resetConversion`, `removeConversion`, `reorderConversion`; `toCommandError` carries the HTTP status |
| `ui/src/renderer/src/features/converter/convert-controls.ts` | modified | 97 changed | `convertMetaSegments`, `controlEnabled('reset')` over the full enum; legacy `STATUS_COLORS` deleted |
| `ui/src/renderer/src/components/queue/QueueList.tsx` | modified | 80 changed | Converter half of `EMPTY_STATE_CONTRACT`: `EmptyDropZone` when empty, `queue-drop-strip` when not, host-overridable empty slot |
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modified | 97 changed | `metaSegments` prop; `DEAD_REGION_RULE` — no `role`/`tabIndex`/`aria-label` without `onOpen` |
| `ui/src/renderer/src/components/queue/QueueCardMenu.tsx` | modified | 19 changed | `copy-location` label flips `Copy path` / `Copy URL` on `output_path` |
| `ui/tests/e2e/convert-queue.test.ts` | modified | 559 changed | W8-3 … W8-8 rewritten: every `RETIRED_TOOLBAR_CONTROLS.converter` id gets a replacement that performs the interaction **and** asserts the outcome |
| `ui/tests/e2e/test-ids.ts` | modified | 46 changed | `NEW_TESTIDS` registered; every `PRESERVED_TESTIDS` id retained |
| `ui/tests/unit/{convert-commands,convert-controls,queue-list,queue-toolbar,run-bulk,shell-ipc-ledger}.test.ts` | new | 1204 | AC-45.3/.4/.4a/.5/.12/.17/.18/.19/.19a plus the ledger |
| `ui/tests/unit/{convert-page,convert-page.behavior,queue-card,queue-primitives,gui-actions-audit,helpers/user-event}.ts` | modified | 889 changed | AC-45.1/.2/.6/.7/.8/.9/.10/.11/.16 plus the 6 superseded assertions retargeted |
| `docs/execution/plans/2026-09-02-p10-queue-card-migration/{assert-handoff-markers,assert-handoff-acs,assert-exec-review-dispatch}.ps1` | new | 3 files | Row 9a closeout checks, each self-testing on a seeded negative |
| `docs/execution/plans/2026-09-02-p10-queue-card-migration/named-sets.json` | modified | +3 keys | `DISPATCH_DIR`, `DISPATCH_STATUS_SCHEMA`, `DISPATCH_ID_FIELD` (Disclosure 4) |

The toolbar is four interactive elements, no more — the overflow is the fourth, and what used
to be top-level buttons now lives inside it:

```diff
+      <div className={groupClasses} data-testid="queue-toolbar" role="toolbar" aria-label={label}>
+        <Button data-testid="queue-toolbar-start" …>{START_LABEL}</Button>
+        <Button data-testid={paused ? 'queue-toolbar-resume' : 'queue-toolbar-pause'} …>
+        <Button data-testid="queue-toolbar-clear-finished" …>{CLEAR_FINISHED_LABEL}</Button>
+        <Button data-testid="queue-toolbar-overflow" aria-haspopup="menu" …>
+          {/* QUEUE_OVERFLOW_MENU — queue-toolbar-clear-all et al. live here, not inline */}
```

Reorder sends the full permutation the API already expects, not a `{id, direction}` body:

```diff
+export async function reorderConversion(
+  ids: readonly string[], id: string, direction: ReorderDirection,
+): Promise<void> {
+  const body = buildReorderBody(ids, id, direction)   // REORDER_WIRE_CONTRACT: { job_ids }
+  const res = await fetch(API_BASE + '/conversions/reorder', { method: 'POST', … })
+  if (!res.ok) { throw toCommandError(res) }          // ERROR_SURFACE: status on the error
+}
```

Every command error carries the HTTP status so `ERROR_SURFACE` can render it:

```diff
+function toCommandError(error: unknown): Error & { status?: number } {
+  if (error instanceof Response) {
+    const err = new Error(error.status + ' ' + error.statusText) as Error & { status?: number }
+    err.status = error.status
+    return err
+  }
+  return error instanceof Error ? error : new Error(String(error))
+}
```

---

## Deviations & Disclosures

1. **`RETIRED_TOOLBAR_CONTROLS.converter` corrected 11 → 13 ids (17 → 20 homes).** The plan's
   count was short by two; the census over the real tree found `convert-top` / `convert-bottom`.
   The mount gate iterates the map, so the correction propagates automatically.
2. **Ten pre-existing assertions were *superseded*, not deleted** (`E2E_REWRITE_RULE` / G36),
   across `convert-page.test.ts`, `queue-primitives.test.ts`, `queue-card.test.ts`,
   `gui-actions-audit.test.ts` and `convert-queue.test.ts`. Each retired control's assertion
   was retargeted at its replacement home. No `.skip` / `.only` / `.todo`, no early returns.
3. **`window.api` is a frozen `contextBridge` proxy** — probed live:
   `{writable:false, configurable:false, frozen:true}`, and assigning `window.api.openPath`
   from a Playwright page is *silently ignored*. W8-8 therefore observes an app-side
   `window.__e2eIpc` ledger (`recordShellIpc`), matching the existing
   `transcript-commands.ts` / `tts-commands.ts` pattern. The helper is deliberately
   **record-only** so `ConvertPage` keeps its literal `window.api.openPath(target)` call and
   the AC-33.19 source scan still passes. A pre-existing dead stub at
   `transcript-queue.test.ts:184` was noted and left alone — out of scope.
4. **Three `DISPATCH_*` keys added to `named-sets.json`.** `EXEC_DISPATCH_CHECK` needs
   `DISPATCH_DIR`, `DISPATCH_STATUS_SCHEMA` and `DISPATCH_ID_FIELD`; the plan named the check
   but omitted the keys, so they are stated once in `named-sets.json` (single-statement rule)
   rather than hard-coded in the script.
5. **E2E seam harness fixes (test *setup*, never assertions).** `page.addInitScript`
   serialises its callback into the renderer and cannot close over module scope, so the sample
   job and the collection regex are now carried in the payload; the POST counter is reported
   back via `page.exposeFunction` because the in-page fetch stub makes `page.route` counters
   unreachable; and the seam's `processorState` is typed to the envelope enum
   (`'Idle' | 'Processing' | 'Paused'`) after `'Running'` — which `parseListEnvelope` rejects —
   silently emptied the queue.
6. **`MEU_GATE` shell-form correction**, **FIC `Test(s)`-column correction** (five ACs point at
   `convert-page.behavior.test.ts`, where the behavioural tests actually landed), and **task
   row 8 completed out of dependency order** — harmless orderings, no AC affected.
   **AC-45.12 scope correction:** the deletion is the legacy `STATUS_COLORS` map only;
   `status-tokens.ts` is the single surviving source.
7. **MEU-44 files edited here.** `QueueCard.tsx`, `QueueCardMenu.tsx` and `QueueList.tsx` are
   MEU-44 deliverables that MEU-45 extends (`metaSegments`, `DEAD_REGION_RULE`, the empty-state
   slot, the kebab copy-label flip). MEU-44's own tests all still pass.
8. **OQ-1 — `plan_to_exec_gate: human`.** This session runs on Claude Code, so the plan's
   `approved` verdict did not auto-continue; execution began only after the user's explicit
   "proceed" (GUARDRAILS SIGN 3(a)).

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

_None. Every MEU-45 AC is in scope for this MEU._

---

## Round 1 Correction (exec-review Finding 4)

**AC-45.1's placeholder-filtering contract was claimed but not implemented.**
`composeMeta` filtered only the page-owned tail, so whenever `resolveMeta` had
nothing to report it emitted the em-dash sentinel and that sentinel was joined in
front of the page's real columns - a Skipped row rendered
`— · Compress · Balanced`, a placeholder standing in front of the very facts it
exists to substitute for.

- **Fix** - `QueueCard.tsx` exports `META_PLACEHOLDER` (previously two bare
  em-dash literals inside `resolveMeta`), and `composeMeta` filters the complete
  `[base, ...segments]` sequence, dropping blanks and the sentinel alike. The
  sentinel survives only when it is all that is left, so the row keeps its height
  in every state (`DEAD_REGION_RULE`).
- **Regression** - `AC-45.1 R1-F4` in `ui/tests/unit/queue-card.test.ts`: a
  sentinel from `resolveMeta`, a sentinel arriving from the page, and the
  all-empty case that must still render the placeholder alone.
- **Red proof** - with `composeMeta` reverted, the test fails
  `expected '— · Compress · Balanced' to be 'Compress · Balanced'`
  (`C:/Temp/av-kit/f4-red.txt`, EXIT 1). Restored, `queue-card.test.ts` is
  20 passed.

The full round-1 correction record, including the four cross-cutting disclosures,
is in the MEU-47 handoff.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created (FIC) | 2026-09-02 | claude-opus-5 | Task row 1 — 22 acceptance criteria transcribed with source labels |
| Red phase | 2026-09-02 | claude-opus-5 | Task row 2 — 27 failing tests (21 new + 6 superseded), receipt `meu45-red.txt` |
| Green + MEU gate | 2026-09-03 | claude-opus-5 | Task row 9 — typecheck / lint / vitest 391 / mount gate 90 / build / e2e 61, all exit 0 |
| Evidence bundle completed | 2026-09-03 | claude-opus-5 | Task row 10 — FAIL_TO_PASS, commands, gates, changed files, 8 disclosures |
| Round 1 correction | 2026-09-03 | claude-opus-5 | Task row H1-7 - Finding 4: `composeMeta` now filters the whole sequence; `R1-F4` regression proved Red |
| Approved | 2026-09-03 | gpt-5.6-sol | Exec review r2 `approved` / 0 findings; Finding 4 closed at `QueueCard.tsx:44,219-225` with the sentinel/base/fallback cases at `queue-card.test.ts:993-1047` |
