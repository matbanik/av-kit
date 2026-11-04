# Walkthrough — GUI keyboard shortcuts, context-aware palette and common shortcuts (Session 41)

Execution record for [implementation-plan.md](implementation-plan.md) and [task.md](task.md). Working tree `P:/av-kit` on `main`, no branch and no worktree (AGENTS.md §Commits). Receipts are under `C:/Temp/av-kit/s41-*.txt`; decisive lines are pasted here.

## Execution message

- **Plan review.** Loop `s41-plan-2026-10-26-gui-keyboard-palette` closed `approved` in round 3 (verdict `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-plan-critical-review.md`). Round 1: 11,095,669 tokens, 4 blocking; round 2: 14,148,254 tokens, 1 blocking; round 3: 7,234,344 tokens, 0 blocking.
- **Review budget.** Mat raised the plan-review token budget twice, verbatim:
  - Before round 2: `Add 12M, run round 2 (Recommended)`. Ledger `continue` recorded at 2026-10-26T19:03:07-04:00, +12,000,000 tokens (budget 22,500,000; `s41-plan-ledger-continue.txt`).
  - Before round 3: `add 32M, run round 3`. Ledger `continue` recorded at 2026-10-26T20:03:31-04:00, +32,000,000 tokens (budget 54,500,000; `s41-plan-ledger-continue-r3.txt`).
- **Execution gate (`plan_to_exec_gate: human`).** Mat's execution message, given with the planning request, 2026-10-26, verbatim: `@.agent/workflows/create-plan.md for Session 41 as per session grouping and appon reviewer approval start executing it.` The round 3 approval met that condition.
- **Context tools.** `context_tool_decision: not_applicable` re-checked at execution, 2026-10-26: `graphify-out/` and `graphify-out-research/` are absent (row 0's prerequisite check reports no graph directory).

## Baseline (row 0)

- **Row command** (task row 0, verbatim, `pwsh` from `P:/av-kit`): exit 0. `s41-prereq.txt`: `prereq problems: []`; `s41-base-check.txt`: `baseline receipts without a result summary: []`.
- **Install:** `uv sync --frozen --all-packages`, `npm --prefix ui ci` (`added 673 packages`), `npm --prefix mcp-server ci` (`added 146 packages`), all exit 0 (`s41-npm-ci.txt`, `s41-npm-ci-mcp.txt`).
- **`PREREQS`:** cwd `P:/av-kit` on `main`; no graph directory; MEU-19, MEU-23, MEU-69, MEU-93 and MEU-94 `approved`; MEU-95/96/97 `pending`; the `AppShell.tsx`, `CommandPalette.tsx` and command-module symbols as stated. The first run stopped at S1 on this plan's own review handoff (Execution Correction Note EC-1).
- **`baseline.sha`:** `bb481ec7d46fdb45b47e533fc2ab83e47e31e227`.

| Suite | Result | Receipt | Failed set |
|---|---|---|---|
| `py-tests` | `5 failed, 932 passed, 1 warning in 461.63s` | `s41-base-py.txt` | four `tests/tooling/test_framework_adoption.py` tests (below); `tests/unit/test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]` |
| `ui-tests` | run 1: `Test Files 5 failed \| 98 passed (103)`, `Tests 6 failed \| 1037 passed (1043)`; run 2: `Test Files 103 passed (103)`, `Tests 1043 passed (1043)` | `s41-base-ui.txt`, `s41-base-ui-r2.txt` | none (run 1 was an install race, below) |
| `mcp-tests` | `Test Files 31 passed (31)`, `Tests 446 passed (446)` | `s41-base-mcp.txt` | none |
| `ui-build` | `built in 18.42s`, exit 0 | `s41-base-build.txt` | — |
| `ui-electron` (download-queue, transcript-queue, convert-queue, capture-inbox, settings, command-palette-nav) | `116 passed (8.3m)` | `s41-base-e2e.txt` | none |

The baseline differs from the plan's expectation (§Verification Plan: the Session 40 packaging set, a clean UI suite). Every difference is outside `PRODUCT_SCOPE`:

- **Four framework-adoption tests fail on HEAD.** The failed ids:
  - `test_review_pipeline_governance_static_oracles[none]`
  - `test_governance_preservation_and_routing_inventory[history]`
  - `test_registry_contract_generic_class_census[Resolve-AgentModel -Class builder -Harness cursor-task]`
  - `test_registry_contract_generic_class_census[builder_model column with class pins {builder|coordinator}]`
  
  Each one runs the framework-adoption checker of `docs/execution/plans/2026-09-26-framework-adoption/` against a manifest copy, and the checker refuses: `REFUSE: rule map identity mismatch: AGENTS.md`. Re-run alone, the module gives `4 failed, 8 passed, 79 deselected in 108.75s` (`s41-fa-probe.txt`).
  
  Cause: commit `bb481ec` (MatBanik, 2026-10-26 18:16, `docs: no branches; Session 42 plan runs on main`) added the two-line **No branches or worktrees** paragraph to `AGENTS.md` §Commits. The adoption manifest still records the earlier `AGENTS.md` identity. This plan does not touch `AGENTS.md` or the adoption manifest, so the failure is pre-existing. `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE` already tracks it (corrected at H2, which updated that issue's verification; this note first said no issue tracked it). The gate excuses all four under the plan's rule (a test failing at baseline is never counted as a regression); see EC-2.
- **AC-25.7 fails on HEAD**, as in Session 40: the committed `docs/distribution/mcp.json.example` has no `AVKIT_API_TOKEN` (known issue `PACKAGING-MCP-SNIPPET-TOKEN-STALE`). The gate already excuses it (Session 40 EC-1).
- **AC-24.10 and AC-25.10 passed.** The gate excuses an expected id only when the row 0 receipt shows it `FAILED`, so neither is excused.
- **The six run-1 UI failures were a first-run Electron install race, not baseline failures.** `npm --prefix ui ci` leaves Electron 42.9.3's binary to a lazy download on first use (`ui/node_modules/electron/index.js:5-41`). Vitest started at `20:27:17`, and `electron/path.txt` was written at `20:27:59` (`stat`).
  - One failure was `ENOENT: no such file or directory, open 'P:\av-kit\ui\node_modules\electron\path.txt'`: `mcp-spawn-electron.test.ts` AC-71.10, as in Session 40.
  - Five were `Test timed out in 5000ms` while the download ran: `g36-csp.test.ts` AC-19.20, `persist-ui.test.ts` AC-19.18 (two tests), `settings-mcp-prompt.test.ts` AC-71.13 and `single-instance.test.ts` AC-19.5.
  - Run 2 on the same tree, with the binary in place, passes everything (`s41-base-ui-r2.txt`). The gate's empty UI excuse list stays as planned, so a later failure of any of the six counts as a regression.

## Census (row 1)

`CENSUS_PATTERNS` over `ui/tests`, `tests` and `mcp-server/tests` (`s41-census.txt`, 358 hits in 57 files; the row prints `census hits: 359` because the receipt's first line is the `[rtk]` banner). The pre-run census (`s41-census-pre.txt`) has the same 358 hits. A shell chord is "affected" only if a test mounts `AppShell` and presses a chord this plan binds or rebinds; no source binds `Ctrl+S`, `Ctrl+L`, `Ctrl+O`, `Ctrl+J`, `Ctrl+Enter`, `F1` or `D` today, so nothing fires twice.

| File (hits) | Disposition | Reason |
|---|---|---|
| `ui/tests/e2e/download-queue.test.ts:590-599` (W1-6) | **TA-1** | Selects `download:add` from Transcript; rewritten to the off-page-absent / nav / on-page shape, label `'Enter download URL'`. |
| `ui/tests/e2e/transcript-queue.test.ts:482-491` (W2-6) | **TA-2** | Selects `transcript:add` from Downloader; same shape, label `'Enter transcript channel URL'`. |
| `ui/tests/e2e/convert-queue.test.ts:740-754` (W8-6) | **TA-5** | Selects `convert:add` from Downloader; same shape, the zero-POST counts kept. |
| `ui/tests/e2e/capture-inbox.test.ts:351-367` (W9-6) | **TA-6** | Selects `capture:region` from Downloader; same shape, `capturePostCount` stays 0. |
| `ui/tests/unit/capture-page.test.ts:165` (AC-39.2, `:178-179`) | **TA-3** | Pins AppShell's hard-coded `Ctrl+5`. `:334` (`category: 'capture'`) is unaffected. |
| `ui/tests/unit/convert-page.test.ts:170` (AC-33.2, `:182-183`) | **TA-4** | Pins AppShell's hard-coded `Ctrl+4`. `:92-94` (confirm-modal ids) are unaffected. |
| `ui/tests/unit/gui-actions-audit.test.ts` (18) | **`CLIPBOARD_RIDER`** (planned Files Modified) | `resolveIpcChannel` (`:68`) and `SETTINGS_HELP_TESTIDS` (`:29`) gain the clipboard resolver and the two `settings:copy_*` ids; the `settingsHelpRows` filter (`:97-109`) is why the new rows need the resolver. AC-23.18 checks only that `Palette = yes` ids appear in the registry text; `convert:browse` becomes `yes` and is added to the registry. The MEU-93 `convert:browse_output_dir` row (`:347-368`) is unchanged. |
| `ui/tests/unit/command-palette.test.ts` (4) | unaffected | AC-19.17: `arrayContaining` of nav ids; `download:add` is still in `listPaletteIds` (palette-eligible, unchanged meaning); `handleGlobalShortcut('Ctrl+K')` is kept. |
| `ui/tests/unit/chrome-zorivest.test.ts` (8) | unaffected | `listPaletteIds()` contains `console:toggle` and `getCommand('console:toggle')` are kept (`:95-98`, `:245-247`); `:234` Escape closes the console with ordering unchanged; `:124` is a clipboard stub. |
| `ui/tests/unit/header-toggles.test.ts` (4), `console-polish.test.ts` (2), `app-shell-wiring.test.ts` (1) | unaffected | `:189` `aria-keyshortcuts` `Control+K` and `:206` `Ctrl+K` keep the header palette button's hint and chord. Escape (`header-toggles:145`, `console-polish:140`) closes the console, ordering unchanged. The rest are `window.api` stubs. |
| `ui/tests/unit/downloader-page.behavior.test.ts` (22), `convert-page.behavior.test.ts` (30), `ui/tests/e2e/download-queue.test.ts` (other 24), `convert-queue.test.ts` (other 20) | unaffected | The "USER_LOCKS — cancelling the queue takes effect with NO confirm" assertions (`downloader-page.behavior:808-815`, `convert-page.behavior:702-709`, e2e `download-queue:723-730`, `convert-queue:873-879`) click the queue card's Cancel, which stays unconfirmed under `CONFIRM_ROUTE`; only the palette Clear and Cancel confirm. Kebab remove, toolbar clear-all and bulk-remove confirm flows are page and card paths, unchanged. The Alt+Arrow `keydown`s are component-local, not registry chords. The listener counter (`download-queue:1259-1270`, `convert-queue:1151`) patches `document`; AppShell listens on `window`. |
| `ui/tests/unit/capture-page.behavior.test.ts` (28), `capture-action-row.test.ts` (12), `capture-scrub.test.ts` (9), `icon-hints.test.ts` (1) | unaffected, **watched at row 7** | `Ctrl+=`, `Ctrl+-`, `Ctrl+0` are `RESERVED` (component-local zoom). The "no `title`" checks (`capture-action-row:339-340`, `capture-page.behavior:1483`, `:1519`, `:1892`, `icon-hints` `expectHinted`) cover `ToolbarIconButton`, which under `HINTS` gets a `shortcut` prop that changes only its Tooltip label, never a `title`. `capture-save`'s `aria-label` `'Save overlay'` (`expectIconAction`, AC-57.6 `:1303`, e2e `:774`) must stay. |
| `ui/tests/unit/tooltip.test.tsx` (7) | unaffected | `:387`, `:399` scan `Tooltip.tsx` only; the label change is the caller's string. |
| `ui/tests/unit/tts-page.test.ts` (4), `tts-page.behavior.test.ts` (7), `voice-combobox.test.tsx` (13), `settings-*.test.ts(x)` (10), `settings-mcp-prompt.test.ts` (8), `theme-selects.test.tsx`, `transcript-page.behavior.test.ts`, `capture-filmstrip-actions.behavior.test.ts` (7), `ui/tests/e2e/tts-generate.test.ts` (5), `fixtures/tts-voices.json` | unaffected | `af_heart` voice fixtures, `writeClipboardText` stubs and the MCP card's own copy button. `tts-generate` W2-6 dispatches a `CustomEvent`. The `TTS_COMMANDS` contract that AC-22.19 needs from `AppShell` (`av-kit:tts:` and `TTS_COMMANDS`, `AppShell.tsx:11`, `:146`) stays; **watched at row 5**. |
| `ui/tests/unit/queue-primitives.test.ts` (6), `queue-card.test.ts:369`, `fixtures/queue-slot-baseline.json` (3) | unaffected | The `ConfirmModal` primitive and the queue card are unchanged; the Space `keydown` is card-local; the baseline's `title=` is queue-card markup. |
| `ui/tests/e2e/command-palette-nav.spec.ts` (5), `test-ids.ts` (4), `ui/tests/unit/e2e-wiring.test.ts:42`, `transcript-page.test.ts:234` | unaffected | The nav spec selects global `settings`, which every page lists. `test-ids.ts:56`, `:239-241` and `e2e-wiring:42` are id lists; `transcript-page:234` is a source regex. No `getByTitle` locator exists anywhere. |
| `tests/**` Python (79 hits in 17 files) | unaffected | `title=` dataclass fields and `af_heart` voice ids; the backend is not in `PRODUCT_SCOPE`. |

Also read at row 1, outside the census hits: `download-commands.test.ts` AC-46.1a and `convert-commands.test.ts` AC-45.4a pin the feature `*_PALETTE_IDS` and `*_EVENTS` keys, which are kept, because `CONFIRM_ROUTE` adds separate `DOWNLOAD_CONFIRM_EVENT` and `CONVERT_CONFIRM_EVENT` exports.

**New contradictions:** none, so no S2.

**Canon edits (`INDEX_AMEND`, D-144):** 06 §Command palette: "Wiring" says every registry chord is bound from the registry (§Shortcut binding) and drops "Nav shortcuts stay on the rail"; "Type" adds the `appearance` category and the `page`, `stateful` and `palette` fields; "Inventory" says the palette lists `Palette = yes` rows by the context-aware model. The `gui-actions-index.md` legend adds that eligible rows are listed per page and state. Row 1 receipt `s41-canon.txt`: `canon problems: []`; the row exits 0 (`s41-row-1-run.txt`).

## MEU-95 Red (row 2)

Tests written: new `ui/tests/unit/shortcuts.test.ts` (AC-95.1 to AC-95.5 and AC-95.7; `registry/shortcuts` is loaded by a variable specifier after an `existsSync` assertion, so the missing module fails one assertion per test), AC-95.6 in `ui/tests/unit/app-shell-wiring.test.ts` (inside the existing describe, so it reuses the `window.api` and `fetch` stubs), and new `ui/tests/e2e/keyboard-shortcuts.test.ts` (AC-95.8). TA-3 (`capture-page.test.ts:178-179`) and TA-4 (`convert-page.test.ts:182-183`) applied: AppShell must contain `createShortcutHandler`, and the `navigateShell('/capture')` / `navigateShell('/convert')` checks read `commandRegistry.ts`. No `ui/src` change (the row's guard passed).

| Receipt | Result |
|---|---|
| `s41-95-red-ui.txt` (exit 1) | Vitest: 7 failed, 2 skipped (9). AC-95.1 to AC-95.5: `AssertionError: registry/shortcuts.ts exists: expected false to be true`. AC-95.6: `AssertionError: Ctrl+2: expected '#/' to be '#/transcript'`. AC-95.7: `AssertionError: nav:downloader collapsed=false: expected '' to contain 'Ctrl+1'`. |
| `s41-95-red-build.txt` | `built in 13.02s` (baseline renderer) |
| `s41-95-red-e2e.txt` (exit 1) | 1 failed: AC-95.8 `Error: expect(page).toHaveURL(expected) failed`, expected `/#\/transcript$/`, received `…index.html#/` after `Control+2`. |
| `s41-95-red-check.txt` | `red-check: 2 receipt(s), 3 required test(s), 0 problem(s)`; the row exits 0 (`s41-row-2-run.txt`). |

The first run (`s41-95-red-e2e-run1.txt`, `s41-95-red-check-run1.txt`, `s41-row-2-run-run1.txt`) was refused by `red-check.py`: AC-95.8 passed the chord as `expect`'s custom message, which Playwright prints first as `Error: Control+2`, an unattributed diagnostic. Only the test changed (S3, test setup): the custom messages were dropped, and the rail check now asserts the plan's exact shape (expanded, then `nav-rail--collapsed` after `Ctrl+B`, then expanded after a second `Ctrl+B`) instead of one conditional toggle. The rerun above is on the final test text.

## MEU-95 Green (row 3)

Implemented: new `ui/src/renderer/src/registry/shortcuts.ts` (`currentShellPage`, `normalizeChord`, `chordFromEvent`, `ariaKeyshortcuts`, `RESERVED_CHORDS`, `buildShortcutMap` and `createShortcutHandler`), the registry's `shortcut` fields, AppShell's single registry-bound keydown handler (it replaces the hard-coded navigation and Ctrl+B branches), and the NavRail chord hints through `ariaKeyshortcuts`. AppShell passes `getState: () => ({})` to the handler. That is a placeholder: MEU-96 adds `registry/command-state.ts`, and row 5 must switch AppShell to `getCommandState`. Row 3 added no stateful chords, so the empty record changes nothing yet.

| Receipt | Result |
|---|---|
| `s41-95-green-ui.txt` | Vitest: 9 files, 105 tests passed. |
| `s41-95-green-build.txt` | `built in 5.12s` |
| `s41-95-green-e2e.txt` | Electron: 65 passed (6.5m), AC-95.8 included. |
| `s41-95-snapshot.txt` | `row 3 ui/src files: 165`; `row3-ui-src.json` written. The row exits 0 (`s41-row-3-run.txt`). |

The first run's Electron step failed one test: `capture-inbox.test.ts:689` (AC-57.10 header: key cap follows hotkey registration; Settings disclosure opens and saves once) hit the 60s test timeout. The other 64 passed. The error context held no page snapshot, only the timeout. Run on its own three times (`s41-95-diag-57-10.txt`), it passed every time (1.3s, 955ms, 6.4s). The row command was rerun unchanged on the same tree and passed whole; the table above is that rerun. The first run's Electron receipt was overwritten by the rerun; this paragraph is its record.

## MEU-96 Red (row 4)

Tests written: new `ui/tests/unit/palette-curation.test.tsx` (AC-96.1 to AC-96.4 and AC-96.6 to AC-96.9), the AC-96.5 and AC-96.7 page harness tests in `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` and `tts-page.behavior.test.ts`, the `MEU-96 gui-actions audit` describe in `gui-actions-audit.test.ts` (AC-96.10 and AC-96.11), the `// MEU-96 Palette curation (additive IDs).` block in `ui/tests/e2e/test-ids.ts` (`SETTINGS_COPY_LOG_PATH`), and the Electron tests AC-96.12 (`download-queue.test.ts`) and AC-96.13 (`settings.test.ts`). The settings seam's call ledger now records the PUT `body` as well as `bodyKeys`, so AC-96.13 can read the saved theme. TA-1 (W1-6), TA-2 (W2-6), TA-5 (W8-6) and TA-6 (W9-6) are applied: each test first shows that the page entry command is absent off its page, then opens the page through the palette and runs the command there. No `ui/src` change (the row's guard printed `ui/src changed since row 3: []`).

| Receipt | Result |
|---|---|
| `s41-96-red-ui.txt` (exit 1) | Vitest: 16 failed, 3 passed, 122 skipped (141). Each failure is an `AssertionError`, for example AC-96.5 TTS `registry/command-state.ts exists: expected undefined to be defined` and AC-96.9 `expected '#/' to be '#/settings'`. The 3 that pass are designed to pass on the row 3 tree: the AC-96.10 06/legend text, the AC-96.10 registry-to-index set equality, and the AC-96.11 test-ids block. |
| `s41-96-red-tree.txt` | `ui/src changed since row 3: []` |
| `s41-96-red-build.txt` | `built in 4.16s` (row 3 renderer) |
| `s41-96-red-e2e.txt` (exit 1) | 2 failed. AC-96.12: `Error: expect(locator).toHaveCount(expected) failed` on `confirm-modal` (expected 1, received 0) after the palette's Clear download queue. AC-96.13: `Error: expect(locator).not.toHaveClass(expected) failed`; `html` stayed `dark` after `Control+Shift+L`. |
| `s41-96-red-check.txt` | `red-check: 2 receipt(s), 5 required test(s), 0 problem(s)`; the row exits 0 (`s41-row-4-run.txt`). |

`npx tsc --noEmit` reports TS2307 for the type-only imports of `registry/command-state` and `registry/appearance` in `palette-curation.test.tsx` (`s41-96-red-tsc-pre.txt`). Those modules arrive in row 5, which must clear the error.

The first run (`s41-96-red-e2e-run1.txt`, `s41-96-red-check-run1.txt`, `s41-row-4-run-run1.txt`) was refused by `red-check.py`. AC-96.12 asserted `toBeVisible()` on a `confirm-modal` that never rendered, and Playwright prints `Error: element(s) not found` for that, an unattributed diagnostic. Only the test changed (S3, test setup, as in row 2): an `expect(...).toHaveCount(1)` now runs before `toBeVisible()`. The rerun above is on the final test text.

## MEU-96 Green (row 5)

Implemented: new `ui/src/renderer/src/registry/command-state.ts` (`publishCommandState`, `clearCommandState`, `getCommandState`, `subscribeCommandState`, `usePublishCommandState`, `useCommandState`) and `registry/appearance.ts` (`setAppearance` through the Settings PUT path). `shortcuts.ts` gains `paletteCommands` (PALETTE_LIST). The registry gains the `appearance` category, `appearance:dark` and `appearance:light`, `page` on 24 entries and `stateful` on 17. `CommandPalette` lists the context-aware set, re-read on every `hashchange` and command-state change. AppShell now passes `getState: getCommandState` (this replaces row 3's placeholder). The Downloader, Transcript, TTS, Convert and Capture pages publish the state of their queue controls; Convert and Downloader route the palette's clear and cancel through their confirm. The TTS palette prepare and generate click only an enabled button. In the docs, `gui-actions-index.md` gains the two appearance rows, the two Settings copy rows (`IPC writeClipboardText`, the `GUI-AUDIT-CLIPBOARD-RESOLVER` rider) and `convert:browse` Palette yes. The `06-gui.md` palette rows (Wiring, Type, Inventory) now point to §Shortcut binding and §Command palette curation.

| Receipt | Result |
|---|---|
| `s41-96-green-ui.txt` | Vitest: 18 files, 350 tests passed. |
| `s41-96-green-build.txt` | `built in 4.14s` |
| `s41-96-green-e2e.txt` | Electron: 139 passed (3.4m), AC-96.12 and AC-96.13 included. |
| `s41-96-snapshot.txt` | `row 5 ui/src files: 167`; `row5-ui-src.json` written. The row exits 0 (`s41-row-5-run.txt`). |

The table is run 3. The earlier runs and their outcomes:

- **Run 1.** Vitest and the build passed. Electron: 4 failed, 135 passed (5.5m), namely W1-6, W2-6, W8-6 and W9-6, each with `TimeoutError: locator.click` on `getByRole('dialog').getByRole('button', { name: '<page>', exact: true })`. The cause was in the test: a navigation entry's palette button holds its `<kbd>` chord, so its accessible name is `Transcript Ctrl+2`, not `Transcript`. Row 4's red-check could not see this, because each test failed earlier, at its off-page `toHaveCount(0)` assertion. Only the four locators changed (S3, test setup), to `{ name: /^<page>( ?Ctrl\+<n>)?$/ }`. The assertions are unchanged. The four passed alone (`s41-fix4.txt`). Run 1's receipts were overwritten by run 2; this paragraph is their record.
- **Run 2** (`s41-96-green-*-run2.txt`, `s41-row-5-run-run2.txt`). Vitest (350) and the build passed. Electron: 2 failed, 137 passed (7.4m), plus `Worker teardown timeout of 60000ms exceeded`. AC-82.6 (`capture-inbox.test.ts:2223`) and AC-77.14 (`tts-generate.test.ts:722`) each hit the 60s test timeout, with no assertion failure. Both passed in run 1 on the same `ui/src`. Repeated alone three times each (`s41-flake2.txt`), they passed 6/6, in 3.3 to 4.3s. Their error contexts were lost: the isolation run cleared `ui/test-results`. Run 3 is the unchanged command on the same tree.

Watch item for row 8 and H1: an Electron test that hangs to the 60s timeout in a long run and passes on its own has now happened in row 3 (AC-57.10) and row 5 (AC-82.6, AC-77.14). None of these tests is in the plan's `e2e-repeat` set. Row 5 did change the pages they drive (`TTSPage.tsx` and `CapturePage.tsx` now publish command state), so this is not ruled out as product behaviour. The row 8 `ui-electron` run decides. A repeat there is a defect under S6.

## MEU-97 Red (row 6)

Tests written: the `MEU-97 gui-common-shortcuts` describe in `shortcuts.test.ts` (AC-97.1 to AC-97.3); new `ui/tests/unit/common-shortcuts.test.tsx` (AC-97.4 for `Header`, `HelpCard` and `ToolbarIconButton`, and AC-97.10); the AC-97.4 page tests in `downloader-page.behavior.test.ts` (`url-input`, `add-btn`), `transcript-page.behavior.test.ts` (`channel-input`, `add-btn`), `tts-page.behavior.test.ts` (`generate-btn`), `convert-page.behavior.test.ts` (`convert-add`, `convert-browse`) and `settings-page.test.ts` (theme buttons); the source-text describe `MEU-97 capture hints (AC-97.4)` in `capture-page.test.ts`; AC-97.11 in `capture-page.behavior.test.ts`; the `MEU-97 gui-actions audit` describe in `gui-actions-audit.test.ts` (AC-97.5); and the Electron tests AC-97.6 (`keyboard-shortcuts.test.ts`), AC-97.7 (`convert-queue.test.ts`), AC-97.8 (`capture-inbox.test.ts`) and AC-97.9 (`download-queue.test.ts`). Two shared test files are new: `ui/tests/unit/helpers/bound-hint.ts` (`chordOf`, `expectBoundHint`, used by every AC-97.4 test) and `ui/tests/unit/fixtures/chord-table.ts` (`CHORD_TABLE`, moved out of `shortcuts.test.ts` so AC-97.5 reads the same rows). In `capture-inbox.test.ts` the AC-59.12 annotation store is lifted into `installAnnotationStore(page)` so AC-97.8 reuses it; AC-59.12 calls it unchanged. No `ui/src` change (the row's guard printed `ui/src changed since row 5: []`).

AC-97.9 note: the Downloader `add-btn` has no disabled rule (it is a form submit, and `addFromForm` returns early on an empty URL), so "with `url-input` empty, `Ctrl+Enter` sends none" is asserted as no `POST /downloads`, not as a disabled button. No product change follows from this.

| Receipt | Result |
|---|---|
| `s41-97-red-ui.txt` (exit 1) | Vitest: 13 failed, 331 skipped (344). Each failure is an `AssertionError`: AC-97.1 to AC-97.3 (no `page:primary`, no `PAGE_PRIMARY_CONTROL`, `Ctrl+S` on `/capture` not bound), AC-97.4 in each of the seven files (`BOUND_CONTROLS` absent, no `aria-keyshortcuts`), AC-97.5 (Trigger cells lack the chords), AC-97.10 (Ctrl+Enter ran the highlighted command) and AC-97.11 (`the saved shot is clean: expected <button> to be null`). |
| `s41-97-red-tree.txt` | `ui/src changed since row 5: []` |
| `s41-97-red-build.txt` | `built in 7.01s` (row 5 renderer) |
| `s41-97-red-e2e.txt` (exit 1) | 4 failed, each by `Error: expect(`. AC-97.6: `url-input` not focused after `Control+L`. AC-97.7: `convert-staged-remove` count 0 after `Control+O` (expected 1). AC-97.8: annotate POST count 0 after `Control+S` (expected 1). AC-97.9: `POST /downloads` count 0 after `Control+Enter` (expected 1). |
| `s41-97-red-check.txt` | `red-check: 2 receipt(s), 7 required test(s), 0 problem(s)`; the row exits 0 (`s41-row-6-run.txt`). |

The first run was refused by `red-check.py` (4 problems). AC-97.8 and AC-97.9 polled with `expect.poll(..., { message })`, which Playwright prints as `Error: <message>`, an unattributed diagnostic. AC-97.7 failed before its chord: it asserted `convert-add` disabled on entry, but Convert keeps Add enabled with empty staging (W8-6 focuses the dropzone instead). Only the tests changed (S3): the three poll messages are dropped (the file's other polls carry none), and AC-97.7 now observes the staged file (`convert-staged-remove` 0, then 1, and `Add (1)`) before clicking Add. The first run's receipts were overwritten by the rerun, which is on the final test text; its refusal is quoted here.

## MEU-97 Green (row 7)

Implemented: `CHORD_TABLE` chords in `commandRegistry.ts` (`console:toggle` Ctrl+J, `download:add` and `transcript:add` Ctrl+L, `convert:browse` Ctrl+O, `capture:save` Ctrl+S, `help:toggle` F1); `PAGE_PRIMARY` as the chord-only `page:primary` (Ctrl+Enter, `palette: false`, `SHORTCUT_ONLY_IDS`), which presses `PAGE_PRIMARY_CONTROL[page]` in `shortcuts.ts` only while it is an enabled button; `HINTS` as `BOUND_CONTROLS` in `shortcuts.ts`, a `title` naming the chord plus `aria-keyshortcuts` on each bound control, and a `shortcut` prop on `ToolbarIconButton` for `capture-save`; `PALETTE_ENTER` in `CommandPalette.tsx` (a modified Enter returns before `preventDefault`); `CAPTURE_SAVE_ROUTE` in `capture-commands.ts` (clicks an enabled `capture-save`); the chords in the `gui-actions-index.md` Trigger cells; and `CAPTURE_CHORD_BUBBLE` in `CaptureViewport.tsx` (EC-3). Every chord reached the renderer in Electron, so no chord was swapped (no S4).

| Receipt | Result |
|---|---|
| `s41-97-green-ui.txt` | Vitest: 15 files, 375 passed (375). `command-palette.test.ts` took 1761ms. |
| `s41-97-green-build.txt` | `built in 7.13s` |
| `s41-97-green-e2e.txt` | 91 passed (4.9m), including AC-97.6 (`keyboard-shortcuts.test.ts:72`), AC-97.7 (`convert-queue.test.ts`), AC-97.8 (`capture-inbox.test.ts:2782`, 2.5s) and AC-97.9 (`download-queue.test.ts:1676`). |
| `s41-row-7-run.txt` | The row exits 0. |

It took three runs; the earlier receipts are kept as `-run1` and `-run2` copies.

- Run 1 (`s41-97-green-ui-run1.txt`, `s41-row-7-run-run1.txt`): 2 failed, 373 passed. `capture-page.test.ts` cuts its AC-97.4 source-text slice at the first "Capture region" after `capture-region`. The new `title="Capture region (Ctrl+Enter)"` sat before `aria-keyshortcuts`, so the slice ended early. The two attributes swapped places; nothing else changed. `command-palette.test.ts` timed out at 5s under the batch. It took 315ms alone and 490ms beside four heavy files, and it passed in runs 2 and 3 (1761ms here). It is a watch item for the row 8 repeat gate, not a fix.
- Unit probe (`s41-97-green-ui-probe.txt`, 1 failed): AC-97.11 read `getCommandState('/capture')['capture:save']` before the passive `usePublishCommandState` effect flushed. The check moved inside the `vi.waitFor` that waits for `capture-save` to unmount. This fixes the test's waiting and adds no retry (S6).
- Run 2 (`s41-97-green-ui-run2.txt` 375/375; `s41-97-green-e2e-run2.txt` 1 failed, 90 passed): AC-97.8 saw 0 annotate POSTs after Ctrl+S. The draw surface had focus and called `stopPropagation` on every key, so the chord never reached AppShell's window handler. EC-3 records the measurement, Mat's ruling and the scope change.
- AC-80.8 (icon hints) is not in this row's spec list. Row 8's full Electron suite covers it.

## Gate (row 8)

`session-gate.ps1` run 4 (`s41-gate.txt`, row exit 0 in `s41-row-8-run.txt`): `session-gate: all steps exit 0`.

| Step | Decisive line |
|---|---|
| identity-before | `exit=0`; `playwright_test 1.62.1`, `ELECTRON_RUN_AS_NODE <unset>`, `segoeui_sha256 704eada1…0f6e`, `uv_lock_sha256 5285fac8…fff6`, `ui_package_lock_sha256 a86d9a42…2980` |
| py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract | each `exit=0` |
| scope-paths | `exit=0`; `changed paths: 56 outside scope: [] head: bb481ec7d46fdb45b47e533fc2ab83e47e31e227 head moved (S8): False` |
| py-tests | `exit=1`, passed by the baseline rule: `5 failed, 932 passed`; `py-tests baseline rule: failed=5 outside_baseline=[] errors=0`. The five are the row 0 baseline ids (the four `test_framework_adoption.py` ids of EC-2 and `test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]`), not regressions. |
| ui-tests | `exit=0`; Vitest `106 passed (106)` files, `1082 passed (1082)` tests |
| mcp-build, mcp-tests | `exit=0`; `31 passed (31)` files, `446 passed (446)` tests |
| ui-build, ui-harness-build, ui-picker-stub | each `exit=0` (`built in 4.25s`, `built in 4.00s`) |
| openapi | `exit=0` (`--check`) |
| state-render | `exit=0`; `Drift check passed — SSOT loaded (98 MEUs, 12 phases)` |
| ui-electron | `exit=0`; `178 passed (4.1m)`. The watch items finished without hanging: AC-57.10 (the four tests under 1.2s), AC-82.6 (3.8s), AC-77.14 (2.8s). No test was retried. |
| e2e-repeat | `exit=0`; `--grep AC-95\|AC-96\|AC-97 --repeat-each=10` over `keyboard-shortcuts`, `download-queue`, `convert-queue`, `capture-inbox` and `settings`: `70 passed (1.2m)` (7 tests × 10), no flaky line |
| identity-npm | `exit=0`; `@playwright/test@1.62.1`, `electron@42.9.3` |
| identity-after | `exit=0`; `tested_state before=…+c30c9b0b… after=…+c30c9b0b…` (equal) |

Identity: `tested_state bb481ec7d46fdb45b47e533fc2ab83e47e31e227+c30c9b0b2fa3a9c8e101a181a16f937a3258c0eb2351b4f3a1e4cfd35976a0a0`, the same at start and end.

Earlier runs (receipts kept with `-run1` to `-run3` suffixes):

- Run 1: `task-contract exit=3`, `RECEIPTS_DIR is unset` (EC-4).
- Run 2: `scope-paths exit=1`, two row 6 test-support files outside scope (EC-5).
- Run 3 (`s41-D6-ui-tests-run3.txt`): `ui-tests exit=1`, `1 failed | 1081 passed`, AC-60.11 `Unable to find an element by: [data-testid="capture-save"]` (`capture-page.behavior.test.ts:806`). That file failed 3 of 3 runs alone (`s41-ac6011-probe-1..3.txt`) and failed the same way with the EC-3 import stubbed out (`s41-ac6011-noimport-*.txt`), so EC-3 is not the cause. Run with `-t "AC-60.11"` alone, the test passed 4 of 4. A state probe in the full file (`s41-ac6011-tracefull-3.txt`) found a `POST …/shot-1/annotate` already sent after the drag and before the click. Cause: `CAPTURE_COMMANDS.save` delivers through `navigateAndDeliver`, two animation frames after the call. AC-97.11 and both AC-60.10 tests waited only two microtasks, so AC-97.11's last `save()` fired inside the next test (AC-60.11) and pressed its Save. The same short wait meant AC-97.11's "second save posts nothing" check was vacuous. Fix (S6: the test's waiting, no retry): a `deliverSave()` helper in `capture-page.behavior.test.ts` calls `CAPTURE_COMMANDS.save()` inside `act` and waits for two `requestAnimationFrame` frames. All five calls use it, and the two now-unused local `CAPTURE_COMMANDS` imports in AC-60.10 are gone. No product change. The file then passed 8 of 8 (`s41-gatefix-cpb-1..8.txt`), and tsc and eslint exit 0.

## Hub (row 9)

`06-gui.md` gains a `> **Delivered (Session 41).**` note at the end of each residual section: §Shortcut binding (MEU-95), §Command palette curation (MEU-96) and §Common shortcuts (MEU-97). Each names its ACs, the row 8 gate and this plan. `tools/meu_status.py update MEU-9{5,6,7} ready_for_review --plan docs/execution/plans/2026-10-26-gui-keyboard-palette/`, then `meu_status.py render` (`All regions rendered successfully`). In `meu-status.yaml` only the three rows' `status`, `status_labels`, `execution_plan` and `updated` changed. The rendered `BUILD_PLAN.md` and `meu-registry.md` follow.

| Receipt | Result |
|---|---|
| `s41-hub-rg.txt` | the three `execution_plan: docs/execution/plans/2026-10-26-gui-keyboard-palette/` lines and the three `Delivered (Session 41)` notes |
| `s41-hub-status.txt` | `hub problems: []` |
| `s41-state-render.txt` | `Drift check passed — SSOT loaded (98 MEUs, 12 phases), rendered regions match on-disk content` |
| `s41-row-9-run.txt` | the row exits 0 |

## Execution Correction Notes

| Item | Change | Evidence |
|---|---|---|
| EC-1 | Row 0's S1 tree check also admits `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-*`. Before, it admitted only this plan folder. The same prefix is already in `session-gate.ps1`'s scope allow-list (`:78`), and the plan names these handoffs (§Handoffs). | The first row 0 run stopped at S1 on the untracked `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-plan-critical-review.md`, which is this plan's own round 1–3 review file. Mat ruled, verbatim: `Treat it as ours, continue (Recommended)`. |
| EC-2 | `session-gate.ps1` `$expectedBaselinePyFailed` gains the four `tests/tooling/test_framework_adoption.py` ids from §Baseline. The two census ids hold a space, so they are listed in the form the gate's `^FAILED (\S+)` capture produces, cut at the first space (`…census[Resolve-AgentModel`, `…census[builder_model`). Row 0 and the gate use the same capture. As with the others, each is excused only if `s41-base-py.txt` shows it `FAILED`. | §Baseline: each fails on HEAD `bb481ec` with `REFUSE: rule map identity mismatch: AGENTS.md`, outside `PRODUCT_SCOPE`. The plan's rule (§Verification Plan) is that a test failing at baseline is never counted as a regression. Session 40 EC-1 is the precedent. |
| EC-3 | `CaptureViewport.tsx` joins MEU-97's Files Modified table and the `scope-paths` allow-list. The draw surface's `onKeyDown` used to call `stopPropagation` on every key. It now skips that for a chord some registry entry binds (`isRegistryChord` in `commandRegistry.ts`, built from `buildShortcutMap`), so the chord reaches AppShell's window `SHORTCUT_HANDLER`. Every other surface key stays contained. `SHELL_WIRING` is unchanged. The surface's own handlers (`handleViewKey`: zoom keys and Space; `onEditorKey`: Escape, Delete, arrows) bind no registry chord, so no key is handled twice. | Row 7 run 2: AC-97.8 saw 0 posts after Ctrl+S. A probe found focus on `capture-draw-surface` and recorded no window keydown (`PROBE-FOCUS capture-draw-surface`, `PROBE-WINDOW-KEYS []`, `C:/Temp/av-kit/s41-97-probe-focus.txt`). Mat ruled, verbatim: `Registry chords bubble (Recommended)`. |
| EC-4 | `session-gate.ps1` sets `$env:RECEIPTS_DIR = $receipts` before its steps, as the 2026-10-16 gate does (`docs/execution/plans/2026-10-16-capture-editor-options/session-gate.ps1:22-24`, same comment). The task rows already pass `RECEIPTS_DIR=C:/Temp/av-kit` to the lint; only the gate's `task-contract` step lacked it. No check is weakened: the lint now reads the receipt paths it was built to check. | The first row 8 run stopped at `task-contract stage=static exit=3` with `FAIL-CLOSED: … RECEIPTS_DIR is unset` (`s41-D6-task-contract.txt`); every later step printed `not_run`, and the row exited 3. That run's `s41-gate.txt` is kept as `s41-gate-run1.txt`. |
| EC-5 | Two test-only files join MEU-97's Files Modified table and the `scope-paths` allow-list: `ui/tests/unit/fixtures/chord-table.ts` (`CHORD_TABLE`, read by AC-97.1 to AC-97.3 in `shortcuts.test.ts` and by AC-97.5 in `gui-actions-audit.test.ts`) and `ui/tests/unit/helpers/bound-hint.ts` (`chordOf`, `expectBoundHint`, used by every AC-97.4 test). Row 6 created both (§MEU-97 Red names them) but did not record the scope change in the same row as the plan requires. That was a process miss, now recorded here. No product file is involved, and the tests are unchanged. | Row 8 run 2: `scope-paths stage=static exit=1`, `changed paths: 56 outside scope: ['ui/tests/unit/fixtures/chord-table.ts', 'ui/tests/unit/helpers/bound-hint.ts']`, `head moved (S8): False` (`s41-D6-scope-paths.txt`, kept with that run's gate log as `s41-gate-run2.txt`). Under S5, Mat ruled, verbatim: `Admit both, EC-5 (Recommended)`. |
