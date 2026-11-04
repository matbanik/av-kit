---
date: "2026-09-02"
project: "2026-08-28-p10-queue-card-foundations"
meu: "MEU-43"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md"
build_plan_section: "bp10s10.3"
agent: "claude-opus-5"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-28-p10-queue-card-foundations-MEU-42-handoff.md"
---

# Handoff: 2026-08-28-p10-queue-card-foundations-MEU-43-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-43 — `gui-queue-primitives`. Build the shared GUI foundation that the QueueCard
(MEU-44) and the page migration (MEU-45+) will stand on: a new `ui/src/renderer/src/lib/queue/`
module set (`format.ts`, `status-tokens.ts`, `status-config.ts`, `envelope.ts`) and four
primitives under `ui/src/renderer/src/components/ui/` (`StatusBadge`, `ProgressBar`,
`SelectionCheckbox`, `ConfirmModal`), plus de-duplication of `formatFileSize` and
registration of the 18 `NEW_TESTIDS`.

**Build Plan Section**: [10 §Status token table](../../../docs/build-plan/10-queue-card-ui.md#status-token-table) (matrix item 10.3)

**Predecessor**: [`2026-08-28-p10-queue-card-foundations-MEU-42-handoff.md`](2026-08-28-p10-queue-card-foundations-MEU-42-handoff.md)

**Deliberately NOT in this MEU.** Nothing is mounted on a page. No `QueueCard`, `QueueList`
or `EmptyDropZone` exists yet (MEU-44). No page migration, no removal of the four legacy
`STATUS_COLORS` maps, no drag-and-drop (MEU-49), no bulk bar. The only edit to a `features/`
file is the two-line carve-out the plan authorises: delete the duplicated `formatFileSize`
block and import the shared one. `PAGE_ISOLATION_RULE` holds — all 28 `FROZEN_GLOBS` files
are byte-identical to the row-1 baseline, both carve-out files changed only by an
`^import … lib/queue/format` line plus removals from inside their own `formatFileSize`
block, their `data-testid` multisets are unchanged, and the E2E title set is identical at 59.

---

## Acceptance Criteria

> All thirteen plan ACs are present. No AC was dropped or deferred.

| AC | Type | Description | Source | Test | Status |
|----|------|-------------|--------|------|--------|
| AC-43.1 | unit | **`formatFileSize` is defined once.** Exactly one definition repo-wide (`lib/queue/format.ts`); both `DEDUP_TARGETS.formatFileSize` feature directories import it; behaviour pinned at `null`/`NaN` -> em-dash, `999 B`, `2 KB`, `245 MB`. | Local Canon (verified duplicate in both queue tables); proposal §2 | "AC-43.1 formatFileSize is defined exactly once and both queue features import it" | PASS |
| AC-43.2 | unit | **Status pill table is single-statement and hex-free.** `status-tokens.ts` exports one record deep-equal to `STATUS_PILL_TABLE` in key order, each entry carrying exactly `{slug, token, fillAlpha, fillClass, labelClass, iconClass}`; zero hex in the module; no rival status-to-colour map on the new surface (legacy census pinned — see disclosure 2). | proposal §5 (fill + alpha); single-statement rule; `G32_RULE` | "AC-43.2 status pill table is a single hex-free statement with no rival status map" | PASS |
| AC-43.3 | unit | **Measured contrast matrix — all 80 label pairings, no debt set.** The test parses `TOKEN_FILE` into dark/light token maps and recomputes every `STATUS_PILL_TABLE` x `CONTRAST_BACKDROPS` x theme pairing: (1) all 80 label ratios >= `CONTRAST_MIN` (4.5), worst 6.61; (2) the computed matrix equals `contrast-matrix.json`'s `label` array ratio-by-ratio; the advisory `icon` array is pinned too. Three in-test negatives prove the oracle is not vacuous. | `USER_LOCKS.pill_palette` (Human-approved) for the hues; reviewer R4-F1 for the decoupled label; WCAG 2.2 SC 1.4.3 relative luminance; `CONTRAST_RULE` | "AC-43.3 every one of the 80 label pairings clears CONTRAST_MIN and matches the baseline" | PASS |
| AC-43.4 | unit | **Token/CSS parity and class-to-token binding.** Every pill `token` is defined in **both** the `@theme` and `:root:not(.dark)` blocks of `styles.css`; each `fillClass`/`iconClass` is exactly the Tailwind form of that entry's own hue token (fill at `fillAlpha`); every `labelClass` is `text-fg`; the banned washed-out `bg-accent-*/20` fill is absent. | `PILL_CLASS_RULE`; `G32_RULE`; Local Canon | "AC-43.4 every pill token exists in both theme blocks and binds to its own classes" | PASS |
| AC-43.5 | unit | **`StatusBadge` renders text, not colour alone.** For all ten statuses the badge renders a non-empty label carrying `labelClass` on `fillClass`; `StatusIcon` carries `iconClass` **and** `aria-hidden="true"` per `STATUS_ICON_RULE`; an unknown status renders the neutral pill with the raw status string as its label. | WCAG 2.2 SC 1.4.1; Zorivest `AccountTypeBadge` variant-map pattern | "AC-43.5 StatusBadge renders a text label on its fill, with an aria-hidden status icon" | PASS |
| AC-43.6 | unit | **`ProgressBar` never animates geometry.** The fill's inline style is `transform: scaleX(<clamped>)` plus `transform-origin: left` with an empty geometry property; the module contains no `transition-all`, no `w-[` arbitrary value, no geometry declaration, and transitions only `transform` at `var(--duration-normal)` / `var(--ease-out)`. | `G33_RULE`; proposal §2 (Transcript violation) | "AC-43.6 ProgressBar animates transform, never geometry" | PASS |
| AC-43.7 | unit | **`ProgressBar` ARIA plus clamping.** `role="progressbar"`, `aria-valuemin=0`, `aria-valuemax=100`, `aria-valuenow` = rounded percent; `0`, `0.427`, `1`, `-0.5`, `1.7` and `NaN` all render in range without throwing. | ARIA APG progressbar pattern | "AC-43.7 ProgressBar exposes clamped progressbar ARIA" | PASS |
| AC-43.8 | unit | **`SelectionCheckbox` indeterminate plus isolation.** `indeterminate` is set imperatively on the DOM node (no such HTML attribute is emitted); a full pointer sequence fires `onChange(true)` exactly once and does **not** reach an ancestor `role="button"`; `accentColor` resolves from `var(--color-accent)` with **no** hex anywhere in the module; `testId` is overridable. | MDN `HTMLInputElement.indeterminate`; `G32_RULE`; Zorivest port | "AC-43.8 SelectionCheckbox is indeterminate-capable, tokenised and click-isolated" | PASS |
| AC-43.9 | unit | **`ConfirmModal` is a portal dialog with a verb label.** Renders through a portal outside the triggering subtree; `role="dialog"`, `aria-modal="true"`, `aria-labelledby` bound to its title; the confirm button's text is the caller's verb (`Remove`), never `OK`/`Yes`; testids `confirm-modal`, `confirm-modal-confirm`, `confirm-modal-cancel`; zero `window.confirm` under `ui/src/renderer/src`. | `G20_RULE`; `USER_LOCKS.remove_confirm` (Human-approved); APG dialog pattern | "AC-43.9 ConfirmModal is a labelled portal dialog with a verb confirm label" | PASS |
| AC-43.10 | unit | **`ConfirmModal` dismissal plus focus.** Initial focus lands on cancel; Tab cycles **within** the dialog across two presses; Escape invokes cancel once; confirm invokes its callback once without also firing cancel; a backdrop click invokes cancel a second time. | APG dialog pattern; `G37_RULE` | "AC-43.10 ConfirmModal traps focus and routes Escape and backdrop to cancel" | PASS |
| AC-43.11 | unit | **Envelope parser is the only reader.** `parseQueueEnvelope` returns `{items, processor?}` and throws `ApiError` 422 on a bare empty array, a bare populated array, an unknown top-level key (Zod `.strict()`) and a missing `items`; no queue module maps a raw `apiFetch` result. | `ENVELOPE_UNKNOWN_KEY_POLICY` (AGENTS.md Boundary Input Contract item 4) | "AC-43.11 the envelope parser rejects bare arrays and unknown wrapper keys via ApiError" | PASS |
| AC-43.12 | unit | **Per-feature status configs, no unified enum.** `QUEUE_STATUS_CONFIGS` has exactly the four `STATUS_CONFIG_FEATURES` keys and each config's key set equals that feature's own `JOB_STATUSES` **in declaration order**; `convert` has no `Downloading`; no status literal is authored in the module. | `STATUS_CONFIG_POLICY`; verified divergent `JOB_STATUSES` in all four controls modules | "AC-43.12 each feature status config is keyed by that feature own JOB_STATUSES" | PASS |
| AC-43.13 | unit | **Standards sweep plus registry, pages untouched.** No raw hex inside a `className` or arbitrary value on the new surface; no `transition-all`; no non-token arbitrary `duration-*`; no `TODO`/`FIXME`/`NotImplementedError`; `Button`'s variant and size key lists are unchanged (`G34_RULE`); no `.skip`/`.only`/`.todo` anywhere in `ui/tests/unit` (`G36_RULE`); all 18 `NEW_TESTIDS` and all 42 `PRESERVED_TESTIDS` are registered. | `G32_RULE`, `G33_RULE`, `G34_RULE`, `G36_RULE`; AGENTS.md anti-slop; E2E testid registry canon | "AC-43.13 standards sweep passes and the testid registry carries the new and preserved ids" | PASS |

All thirteen live in `ui/tests/unit/queue-primitives.test.ts` (730 lines, one AC id per test title).

### Disclosures the reviewer should check first

1. **Ten ratios in `contrast-matrix.json` were corrected during Green — a rounding-mode
   defect in the planning-time generator, not a relaxed assertion.** AC-43.3 asserts that the
   recomputed matrix equals the committed baseline exactly. On the first Green run, 10 of the
   80 `label` rows disagreed. Root cause, proven rather than assumed: the MEU-41 baseline was
   generated with a **half-to-even** (banker's) rounder, while the Red-phase test — written
   before any implementation and unchanged since — uses JS `Math.round`, which is **half-up**,
   the direction a browser actually composites 8-bit channels. Re-deriving the whole 160-row
   matrix under each rounder settles it: half-to-even reproduces the committed file with **0**
   mismatches (so that is definitively how it was made), half-up reproduces it with exactly the
   **10** label mismatches observed and **0** icon mismatches. The baseline data was regenerated
   with half-up. Every delta is <= 0.08 and **none crossed `CONTRAST_MIN`**:

   | Pairing | Baseline | Corrected |
   |---|---|---|
   | dark / Pending / detail-open | 8.49 | 8.46 |
   | dark / Done / checkbox-selected | 9.2 | 9.18 |
   | dark / Failed / detail-open | 9.5 | 9.47 |
   | dark / Skipped / checkbox-selected | 9.87 | 9.85 |
   | dark / QualityBlocked / detail-open | 8.49 | 8.46 |
   | dark / AgeRestricted / detail-open | 8.62 | 8.59 |
   | light / Failed / card | 11.62 | 11.64 |
   | light / Cancelled / card | 12.03 | 12.05 |
   | light / Cancelled / checkbox-selected | 11.38 | 11.46 |
   | light / AgeRestricted / card | 11.62 | 11.64 |

   `label_worst` is **unchanged at 6.61**, so `CONTRAST_WORST_MEASURED` in `named-sets.json`
   still holds and needed no edit. **No test file was touched**: the assertion, the algorithm
   and all 80 `>= CONTRAST_MIN` checks are exactly as written in Red, and the equality
   assertion retains its full drift-detection force (moving any hex in `styles.css` still
   fails the suite). The alternative — changing `Math.round` in the test to banker's rounding —
   *would* have been a test modification, and would have made the oracle less browser-accurate.
   The `_meta.rounding` key in the JSON now records this.

2. **AC-43.2's "no rival status map" is enforced as a pinned 8-file census plus a new-surface
   class scan, not a repo-wide prohibition.** A literal repo-wide reading is unsatisfiable
   *today*: the four feature `*-controls.ts` modules and the four pages they feed already
   export and consume `STATUS_COLORS`, and every one of those files is either frozen by
   `FROZEN_GLOBS` or scheduled for deletion by MEU-45+. The test therefore pins that census to
   exactly those eight paths (so no **new** rival map can appear, and the census must shrink
   when the pages migrate) and separately forbids any pill class literal (`bg-status-*`,
   `text-accent-*`, ...) in every new-surface file except `status-tokens.ts` itself.

3. **The test file is `.test.ts`, not `.test.tsx`, and builds elements with `createElement`.**
   `ui/vitest.config.ts` includes only `tests/unit/**/*.test.ts`; a `.tsx` file would be
   collected by nothing and the Red oracle would have reported zero tests. This matches the
   existing `downloader-page.behavior.test.ts` convention.

4. **`@testing-library/user-event` could not be installed; a local helper implements
   `G37_RULE` instead.** `ui/package.json` and `ui/package-lock.json` are in `FROZEN_GLOBS`, so
   **no** new dependency of any kind is possible in this MEU.
   `ui/tests/unit/helpers/user-event.ts` provides `click` / `keyboard` / `tab` behind the same
   surface and honours the rule's intent — a real pointer sequence (`pointerdown` ->
   `mousedown` -> focus -> `pointerup` -> `mouseup` -> `click`), real `keydown`/`keypress`/
   `keyup`, and a `tab()` that dispatches the key first and only emulates the browser's focus
   advance when nothing called `preventDefault()` (so a focus trap is exercised through its own
   handler). Every entry point wraps its dispatches in React's `act`.

5. **`CONTRAST_BACKDROPS`'s `default` key is bridged to the matrix's `card` backdrop name.**
   The named set calls the neutral card state `default`; the measured baseline spells the same
   pairing `card`. The test carries a one-entry rename map rather than a second source of truth.

6. **`ui/tests/unit/downloader-page.behavior.test.ts:12` was repointed.** It imported
   `formatFileSize` from `DownloadQueueTable`; with the definition moved, its import is now
   split across two lines (`DownloadQueueTable` from the component, `formatFileSize` from
   `lib/queue/format`). **No assertion in that file was touched** — its `245 MB` expectation is
   unchanged and still passes.

7. **A dynamic-import indirection is required in the Red suite and remains in Green.** Vite
   statically resolves `import()` with a *literal* specifier at transform time, so a missing
   module collapsed the whole file instead of failing one AC. The loaders therefore pass a
   template-literal variable with a `@vite-ignore` comment, with `import type * as X` for
   typing. This is a Vite constraint, not a design choice, and is harmless now that all eight
   modules exist.

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

All thirteen tests were written in `ui/tests/unit/queue-primitives.test.ts` **before** any
`ui/src/renderer/src/lib/queue/` module or primitive existed, and were observed failing.
Red receipts: `C:/Temp/av-kit/fail-to-pass-meu-43-ui.txt` (and `.json`) ->
`Test Files 1 failed (1)`, `Tests 13 failed (13)`. Oracle receipt:
`C:/Temp/av-kit/red-oracle-meu-43.txt` -> `PASS: RED_ORACLE ui MEU-43 AC-43 count=13`
(13 distinct mapped ids, equal to `RED_COUNT_43`), then `PASS: FAIL_TO_PASS red`.

| Test | Red output (snippet) | Green output | Implementation |
|------|----------------------|--------------|----------------|
| AC-43.1 formatFileSize is defined exactly once ... | `AssertionError: expected [ 'ui/.../ConvertQueueTable.tsx', 'ui/.../DownloadQueueTable.tsx' ] to deeply equal [ 'ui/src/renderer/src/lib/queue/format.ts' ]` | passes — one declaration, both features import it | `ui/src/renderer/src/lib/queue/format.ts:16` |
| AC-43.2 status pill table is a single hex-free statement ... | `Error: Cannot find module '../../src/renderer/src/lib/queue/status-tokens'` | passes — record deep-equal in key order, 0 hex, census == 8 files | `ui/src/renderer/src/lib/queue/status-tokens.ts:36` |
| AC-43.3 every one of the 80 label pairings ... | `Cannot find module '.../status-tokens'` | passes — 80/80 >= 4.5, worst 6.61, matrix equal ratio-by-ratio, 3 negatives all move the matrix | `docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json` |
| AC-43.4 every pill token exists in both theme blocks ... | `Cannot find module '.../status-tokens'` | passes — 10 tokens x 2 theme blocks, every class derived from its own token | `ui/src/renderer/src/styles.css` (`@theme` + `:root:not(.dark)`) |
| AC-43.5 StatusBadge renders a text label ... | `Cannot find module '.../components/ui/StatusBadge'` | passes — 10 statuses plus unknown fallback, icon `aria-hidden="true"` | `ui/src/renderer/src/components/ui/StatusBadge.tsx:37` |
| AC-43.6 ProgressBar animates transform, never geometry | `Cannot find module '.../components/ui/ProgressBar'` | passes — `scaleX(0.42)`, empty geometry property, source clean of `transition-all` / `w-[` | `ui/src/renderer/src/components/ui/ProgressBar.tsx:76` |
| AC-43.7 ProgressBar exposes clamped progressbar ARIA | `Cannot find module '.../ProgressBar'` | passes — 6 edge values -> `0/43/100/0/100/0` | `ui/src/renderer/src/components/ui/ProgressBar.tsx:24` |
| AC-43.8 SelectionCheckbox is indeterminate-capable ... | `Cannot find module '.../SelectionCheckbox'` | passes — `indeterminate` property set with attribute absent, `onChange(true)` once, wrapper handler not called | `ui/src/renderer/src/components/ui/SelectionCheckbox.tsx:56` |
| AC-43.9 ConfirmModal is a labelled portal dialog ... | `Cannot find module '.../ConfirmModal'` | passes — portalled outside host, labelled by title, confirm text `Remove`, 0 `window.confirm` | `ui/src/renderer/src/components/ui/ConfirmModal.tsx:107` |
| AC-43.10 ConfirmModal traps focus and routes Escape ... | `Cannot find module '.../ConfirmModal'` | passes — initial focus on cancel, 2 Tabs stay inside, Escape -> cancel, confirm once, backdrop -> cancel | `ui/src/renderer/src/components/ui/ConfirmModal.tsx:82` |
| AC-43.11 the envelope parser rejects bare arrays ... | `Cannot find module '.../lib/queue/envelope'` | passes — 4 malformed bodies all raise `ApiError` 422 `ENVELOPE_INVALID` | `ui/src/renderer/src/lib/queue/envelope.ts:44` |
| AC-43.12 each feature status config is keyed by ... | `Cannot find module '.../lib/queue/status-config'` | passes — 4 configs, key order equals each `JOB_STATUSES`, no status literal in the module | `ui/src/renderer/src/lib/queue/status-config.ts:43` |
| AC-43.13 standards sweep passes and the testid registry ... | `AssertionError: expected '...test-ids.ts source...' to contain 'status-badge'` | passes — sweep clean, 18 new plus 42 preserved ids registered | `ui/tests/e2e/test-ids.ts` |

**No test assertion or expected value was modified in Green.** The only expected-value change
in this MEU is the `contrast-matrix.json` data baseline, disclosed as item 1 above with its
root-cause proof.

### Commands Executed

Every command ran under the P0 redirect-to-file pattern with receipts under `C:/Temp/av-kit/`.

| Command | Exit code | Key output |
|---------|-----------|------------|
| `npx vitest run --allowOnly=false tests/unit/queue-primitives.test.ts` (row 8, Red) | 1 by design | `Tests 13 failed (13)` — receipts `fail-to-pass-meu-43-ui.txt`, `fail-to-pass-meu-43-ui.json` |
| `assert-red-oracle.ps1 -Kind ui -Meu 43 -Receipt ... -JsonReceipt ...` (row 8) | 0 | `PASS: RED_ORACLE ui MEU-43 AC-43 count=13`; `PASS: FAIL_TO_PASS red` — receipt `red-oracle-meu-43.txt` |
| Row 9 Green chain: `npx tsc --noEmit` -> `npx vitest run --allowOnly=false` -> `npx eslint src/ tests/ --max-warnings 0` -> `npm run build` -> `assert-page-isolation.ps1` | 0 | `Test Files 42 passed (42)`; `Tests 350 passed (350)`; `built in 2.74s`; `PASS: PAGE_ISOLATION frozen=28 carveout=2 scanned=73 e2e=59 preserved=42` — receipt `ui-green-meu-43.txt` |
| Row 10 `MEU_SCOPED_GATE_UI`: tsc + vitest + eslint + build + anti-placeholder on `PLACEHOLDER_PATHS_43` + G36 on `G36_TEST_PATHS_UI` + `window.confirm` scan + `PAGE_ISOLATION_CHECK` + `HANDOFF_SOURCE_READ_43` / handoff existence, ordering and AC-coverage checks | 0 | `PASS: MEU-43 MEU_SCOPED_GATE_UI` — receipt `handoff-meu-43.txt` |

### Quality Gate Results

```
tsc --noEmit (ui):                    0 errors
vitest run (ui):                      350 passed, 0 failed (42 files)
eslint src/ tests/ --max-warnings 0:  clean, no output
electron-vite build:                  exit 0 (main 120ms, preload 9ms, renderer 2.74s)
anti-placeholder (lib/queue, ui):     0 matches
G20 window.confirm scan:              0 matches under ui/src/renderer/src
G36 skip/only/todo scan:              0 matches in ui/tests/unit, ui/tests/e2e
PAGE_ISOLATION_CHECK:                 PASS frozen=28 carveout=2 scanned=73 e2e=59 preserved=42
contrast matrix:                      80/80 label pairings >= 4.5, worst 6.61
targeted MEU-43 suite:                13 passed (13)
```

**Final session-close verification (task.md H1-2, 2026-09-02).** Re-run over the whole tree after all four MEUs landed: pytest 507 passed - pyright 0 errors - ruff clean - tsc 0 errors - vitest 366 passed (43 files) - eslint clean - electron-vite build ok - `export_openapi.py --check` clean - `PASS: PAGE_ISOLATION frozen=28 carveout=2 scanned=73 e2e=59 preserved=42`. Receipt `C:/Temp/av-kit/full-verify.txt`.

**Playwright E2E passes: 59 passed / 0 failed, EXIT=0** (task.md H1-2a), on a bundle rebuilt after the last source change (P9 RULE-1). Receipt `C:/Temp/av-kit/e2e-regression-rerun.txt`. This **retracts** the earlier `[B]` and its "external electron 42.9.3 / playwright-core 1.62.1 incompatibility" claim: the real cause of `electron.exe: bad option: --remote-debugging-port=0` was `ELECTRON_RUN_AS_NODE=1` set in the agent's own shell (inherited from the Cursor extension host) and spread into the launched app by `...process.env` at all 14 `_electron.launch()` sites. Proof: `electron --version` prints `v24.18.1` with the variable set and `v42.9.3` without. Known-issue `E2E-ELECTRON-LAUNCH-FLAG` has been re-filed against that real cause (env leakage through `...process.env`, severity lowered to low). The specs stay written and wired; no wave was added or removed (`E2E_NEW_WAVES_THIS_SESSION` = 0).

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/lib/queue/format.ts` | new | the single `formatFileSize`, moved verbatim from the two queue tables |
| `ui/src/renderer/src/lib/queue/status-tokens.ts` | new | one-statement `STATUS_PILL_TOKENS` (10 statuses), `StatusPill` type, `NEUTRAL_PILL`, `resolveStatusPill`. Zero hex |
| `ui/src/renderer/src/lib/queue/status-config.ts` | new | `QUEUE_STATUS_CONFIGS` built from each feature's imported `JOB_STATUSES` via `buildStatusConfig`; no status literal authored |
| `ui/src/renderer/src/lib/queue/envelope.ts` | new | strict Zod `{items, processor?}` parser raising `ApiError` 422 `ENVELOPE_INVALID` with per-issue details |
| `ui/src/renderer/src/components/ui/StatusBadge.tsx` | new | `StatusBadge` (text label on token fill) plus `StatusIcon` (`aria-hidden` dot) |
| `ui/src/renderer/src/components/ui/ProgressBar.tsx` | new | transform-driven determinate bar with clamped `progressbar` ARIA |
| `ui/src/renderer/src/components/ui/SelectionCheckbox.tsx` | new | tri-state checkbox, `accentColor: var(--color-accent)`, click isolated from an ancestor row |
| `ui/src/renderer/src/components/ui/ConfirmModal.tsx` | new | portal dialog, focus trap, Escape/backdrop to cancel, verb confirm label, reuses the existing `Button` |
| `ui/src/renderer/src/features/downloader/DownloadQueueTable.tsx` | modified | CARVE_OUT: `formatFileSize` block deleted, one import added |
| `ui/src/renderer/src/features/converter/ConvertQueueTable.tsx` | modified | CARVE_OUT: same |
| `ui/tests/unit/queue-primitives.test.ts` | new | the 13-test AC-43 suite (Red phase, unmodified since) |
| `ui/tests/unit/helpers/user-event.ts` | new | `G37_RULE` interaction helper — see disclosure 4 |
| `ui/tests/unit/downloader-page.behavior.test.ts` | modified | line 12 import repointed — see disclosure 6 |
| `ui/tests/e2e/test-ids.ts` | modified | the 18 `NEW_TESTIDS` constants appended |
| `docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json` | modified | 10 label ratios corrected plus `_meta.rounding` — see disclosure 1 |
| `docs/execution/plans/2026-08-28-p10-queue-card-foundations/task.md` | modified | rows 8-10 closed with evidence |

**The carve-out edit, identical in shape in both queue tables:**

```diff
+import { formatFileSize } from '../../lib/queue/format'
 import { JOB_STATUSES, STATUS_COLORS, type JobStatus } from './download-controls'
 import type { DownloadListItem } from './useDownloadQueue'
 
 type DownloadQueueTableProps = {
   items: DownloadListItem[]
   selectedId: string | null
   onSelect: (id: string) => void
 }
 
-export function formatFileSize(bytes: number | null): string {
-  if (bytes === null || Number.isNaN(bytes)) {
-    return '\u2014'
-  }
-  ...
-}
-
 const columnHelper = createColumnHelper<DownloadListItem>()
```

**The transform-only progress fill (AC-43.6):**

```diff
+      <div
+        className={fillClasses}
+        data-progress-fill=""
+        style={{
+          transform: `scaleX(${String(ratio)})`,
+          transformOrigin: 'left',
+          transitionDuration: 'var(--duration-normal)',
+          transitionTimingFunction: 'var(--ease-out)',
+        }}
+      />
```

**The per-feature config, keyed by imported status tuples (AC-43.12):**

```diff
+function buildStatusConfig<T extends readonly string[]>(statuses: T): FeatureStatusConfig<T> {
+  return Object.fromEntries(
+    statuses.map((status) => [status, { status, pill: resolveStatusPill(status) }]),
+  ) as FeatureStatusConfig<T>
+}
+
+export const QUEUE_STATUS_CONFIGS = {
+  download: buildStatusConfig(DOWNLOAD_STATUSES),
+  convert: buildStatusConfig(CONVERT_STATUSES),
+  transcript: buildStatusConfig(TRANSCRIPT_STATUSES),
+  tts: buildStatusConfig(TTS_STATUSES),
+} as const
```

---

## Codex Validation Report

_Left blank for the reviewer agent. Filled during `/execution-critical-review`._

### Recheck Protocol

1. Read Scope plus the AC table.
2. Verify each AC against the Evidence section (quote `file:line`, not memory).
3. Re-run every command in Commands Executed and compare output.
4. Run the Quality Gate commands independently.
5. Record findings below.

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | _pending review_ | — | — | — |

### Verdict

_pending_

---

## Deferred Items

None. All thirteen ACs are satisfied.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-02 | claude-opus-5 | MEU-43 Red (13 tests) -> Green (8 modules) -> `MEU_SCOPED_GATE_UI` |
