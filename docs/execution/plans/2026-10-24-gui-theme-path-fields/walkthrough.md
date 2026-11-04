# Walkthrough — GUI theme-reactive selects and one path-field primitive (Session 40)

Execution record for [implementation-plan.md](implementation-plan.md) and [task.md](task.md). Working tree `P:/av-kit` on `main` (plan D-104), no worktree. Receipts are under `C:/Temp/av-kit/s40-*.txt`; decisive lines are pasted here.

## Execution message

- **Plan review.** Loop `s40-plan-2026-10-24-gui-theme-path-fields` closed `approved` in round 2 (verdict `.agent/context/handoffs/2026-10-24-gui-theme-path-fields-plan-critical-review.md`). Round 1: 7,818,036 tokens; round 2: 6,228,956 tokens. The one open finding, F4 (Low, non-blocking: AC-93.4's source check against the existing Settings directory helpers), is carried to row 4.
- **Review budget.** Before round 2, Mat raised the plan-review budget, verbatim: `I approve trippling of the budget, run the command for me`. The ledger `continue` was recorded at 2026-10-24T23:53:26-04:00 (+21,000,000 tokens; budget 31,500,000; receipt `C:/Temp/av-kit/s40-ledger-continue.txt`).
- **Execution gate (`plan_to_exec_gate: human`).** After the round 2 approval, Mat's explicit execution message, 2026-10-25, verbatim: `proceed`.
- **Context tools.** `context_tool_decision: not_applicable` re-checked at execution, 2026-10-25: `graphify-out/` and `graphify-out-research/` are absent (the row 0 prerequisite check reports no graph directory).

## Baseline (row 0)

- **Row command** (task row 0, verbatim, `pwsh` from `P:/av-kit`, run through `run_row.py`): exit 0. Receipt `C:/Temp/av-kit/s40-run-row0.txt`: `prereq problems: []`, `baseline receipts without a result summary: []`, `row 0 exit=0`.
- **Install:** `uv sync --frozen --all-packages`, `npm --prefix ui ci` (`added 673 packages`), `npm --prefix mcp-server ci`, all exit 0 (`s40-sync.txt`, `s40-npm-ci.txt`, `s40-npm-ci-mcp.txt`).
- **`PREREQS`:** no graph directory; MEU-19, MEU-22, MEU-23, MEU-33, MEU-58 and MEU-92 `approved`; MEU-93 and MEU-94 `pending`; `lib/theme.ts` exports `useSyncDocumentTheme`; `SelectInput.tsx` exports `getG30Styles` (`s40-prereq.txt`: `prereq problems: []`).
- **`baseline.sha`:** `7b29fcd0efcd11a1d8c5cbf4d725aaa66be84bb2`.

| Suite | Result | Receipt | Failed set |
|---|---|---|---|
| `py-tests` | `1 failed, 936 passed, 1 warning in 109.75s` | `s40-base-py.txt` | `tests/unit/test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]` |
| `ui-tests` | `Test Files 1 failed \| 100 passed (101)`, `Tests 1 failed \| 1012 passed (1013)` | `s40-base-ui.txt` | `tests/unit/mcp-spawn-electron.test.ts > MEU-71 MCP_LAUNCH in dev (AC-71.10) > AC-71.10 Electron with ELECTRON_RUN_AS_NODE on the dev SERVER_ENTRY answers initialize as av-kit` |
| `mcp-tests` | `Test Files 31 passed (31)`, `Tests 446 passed (446)` | `s40-base-mcp.txt` | none |
| `ui-build` | `built in 4.13s`, exit 0 | `s40-base-build.txt` | — |
| `ui-electron` (settings, tts-generate, convert-queue) | `53 passed (1.5m)` | `s40-base-e2e.txt` | none |

The baseline differs from the plan's expectation (§1: two environmental packaging failures, a clean UI suite). Both differences are outside `PRODUCT_SCOPE`:

- **AC-25.7 fails on HEAD.** `test_mcp_snippet_keys` asserts `AVKIT_API_TOKEN` in `docs/distribution/mcp.json.example`. The committed file carries only `ELECTRON_RUN_AS_NODE` and `AVKIT_APP_DATA` in `env`:
  - `E   assert 'AVKIT_API_TOKEN' in '{\n  "mcpServers": {\n    "avkit": {\n      "command": "<path to av-kit.exe>", … "env": {\n        "ELECTRON_RUN_AS_NODE": "1",\n        "AVKIT_APP_DATA": "<app data folder>"\n      }…'` (`s40-base-py-fail.txt`).
  - The file is unchanged since `7b29fcd` and is not in this plan's Files Modified, so the failure is pre-existing. No known issue tracks it; H2 records it.
  - The gate excuses it under the plan's rule, which says a test failing at baseline is never a regression. See Execution Correction Note EC-1.
- **AC-24.10 and AC-25.10 passed.** These are the two expected environmental packaging tests. Re-run alone, they give `2 passed in 0.03s` (`s40-base-py-env.txt`). The gate excuses an expected id only when the row 0 receipt shows it `FAILED`, so neither is excused.
- **AC-71.10 was a first-run install race, not a baseline failure.** The failure was `ENOENT: no such file or directory, open 'P:\av-kit\ui\node_modules\electron\path.txt'`. That file was written at `2026-10-25 00:11:19` (`stat`), eight seconds after the Vitest run started (`Start at 00:11:11`), because the Electron binary setup finished while the suite was already running.
  - Re-run alone: `Test Files 1 passed (1)`, `Tests 3 passed (3)` (`s40-base-ui-ac7110-rerun.txt`).
  - The gate's empty UI excuse list stays as planned. A later failure of AC-71.10 would count as a regression.

## Census (row 1)

`CENSUS_PATTERNS` over `ui/tests`, `tests` and `mcp-server/tests` (`s40-census.txt`, 146 hits in 37 files). Under `THEME_GATE`, the route children of `AppShell` render only after the boot `GET /settings/ui` settles: on success, or on any error whose code is not `BACKEND_NOT_READY`. Every `AppShell` mount below stubs `window.api.getBackendUrl`, and every fetch mock answers `/settings/ui` without a 503. So the gate settles on the first answer in each one.

| File (hits) | Disposition | Reason |
|---|---|---|
| `ui/tests/unit/chrome-zorivest.test.ts:304` | **TA-1** | Pins `ConsolePanel.tsx` containing `getG30Styles`; becomes `useG30Styles` plus `not.toMatch(/G30_DARK\s*=/)`. |
| `ui/tests/unit/chrome-zorivest.test.ts` (other 13: `:71`, `:97`, `:102`, `:112`, `:167`, `:170`, `:254-264`, `:270-271`) | unaffected | `PAGE_FILES` no-raw-hex scan (the placeholder uses token classes); `handleGlobalShortcut` import; console `localStorage` keys; the `TOGGLE_CONSOLE_EVENT` listener scan. The mounts at `:167-170` assert on shell chrome and `main`'s class, never on `main-child`; the fetch mock (`:153-158`) answers `/settings/ui` 200. |
| `ui/tests/unit/tts-page.test.ts:271` | **TA-2** | `toMatch(/getG30Styles/)` becomes `not.toMatch`. |
| `ui/tests/unit/tts-page.test.ts` (other 7: `:12`, `:60-61`, `:279-280`, `:339`, `:355`) | unaffected | `output-path` and `browse-output-btn` are kept by `PATH_ROWS`; AC-22.13 still finds `showDirectoryDialog`; the `AppShell` palette scan is unchanged. |
| `ui/tests/unit/app-shell-wiring.test.ts` (8) | unaffected | Mounts `AppShell` with a plain child and asserts navigation, console and the root `dark` class. The fetch mock answers 200 for every URL (`:56-62`, `:104-115`). `:102-122` still holds: `applyDocumentTheme('light')` now also writes the mirror. |
| `ui/tests/unit/console-polish.test.ts` (5) | unaffected | Mounts `AppShell` (`:73-76`); fetch answers 200 (`:62-65`); assertions read console controls and `main`'s class (`:128-146`). Source scans of `AppShell.tsx` (`:149`, `:224`) check tokens and raw hex, which the placeholder does not add. |
| `ui/tests/unit/header-toggles.test.ts` (6) | unaffected | Mounts `AppShell` (`:112-114`); fetch answers 200 (`:100-103`); assertions are on header buttons and console state. |
| `ui/tests/unit/downloader-page.behavior.test.ts` (3) | unaffected, **watched at Green** | AC-20.13 (`:278-300`) mounts `AppShell` around `DownloaderPage`. Its fetch falls through to `202 ''` for `/settings/ui` (`:144`), which `apiFetch` returns as `undefined`, a success, so the gate settles after one answer. The focus assertion has a `?? document.activeElement` fallback, so it passes even if the page is not mounted yet. Row 3 records whether `url-input` is mounted when the event fires; if AC-20.13 fails there, it is S2. |
| `ui/tests/unit/theme.test.ts` (9) | unaffected | `applyDocumentTheme` and `THEME_CHANGED_EVENT` keep their contract; the added `localStorage` write is additive. |
| `ui/tests/unit/settings-page.test.ts` (10) | unaffected | Renders `SettingsPage` without `AppShell`; asserts the root class after the theme buttons and the `/settings/ui` PUT. |
| `ui/tests/unit/layout-primitives.test.ts` (17) | unaffected | AC-51.4 and AC-58.5 pin `PathRow`'s existing props, which are kept (`placeholder` and `browseDisabled` are optional, additive). AC-51.5 forbids raw hex and `apiFetch` in `PathRow`. AC-51.6 hashes the `test-ids.ts` prefix before the `// MEU-51 primitive harness IDs.` marker, so the MEU-93 block goes after it, with line endings kept. |
| `ui/tests/unit/tts-page.behavior.test.ts:399` | unaffected (**AC-56.4**) | Run-bar containment of `output-path`, `browse-output-btn` and `cancel-btn`. `PATH_ROWS` keeps the field and its Browse inside the run bar under the same ids. A break is S4. |
| `ui/tests/unit/capture-flatten.test.ts:150`, `capture-page.test.ts:600`, `ui/tests/e2e/capture-inbox.test.ts:1555`, `ui/tests/e2e/test-ids.ts:408` | unaffected (**AC-67.24 / AC-67.26**) | Pin `settings-capture-backup-browse` (and `settings-leaf-capture-backup_dir`), which `PATH_ROWS` keeps. |
| `ui/tests/unit/gui-actions-audit.test.ts` (3) | unaffected (**AC-71.14**) | `CONVERT_AUDIT_TESTIDS` gains one entry (`CONVERT_BROWSE_INDEX`). The audit pattern, every index row resolving to a registered channel and every audited test id existing in source, is unchanged. |
| `ui/tests/unit/convert-page.test.ts` (4), `convert-page.behavior.test.ts` (7) | unaffected | `convert-output-dir` is kept and editable; `/settings/ui` mocks answer the theme; `PathRow` renders the input under the same id. |
| `ui/tests/e2e/convert-queue.test.ts` (3), `tts-generate.test.ts` (2), `test-ids.ts:128-162` | unaffected | Same ids; `browse-output-btn` keeps its click and its busy-disabled state (`browseDisabled={busy}`). |
| `ui/tests/e2e/settings.test.ts` (4) | unaffected | The seam answers `GET /settings/ui` with `{theme: 'dark'}` (`:82`), so `BOOT_RETRY` makes one call. AC-78.9 counts GETs as "greater than before", which still holds. |
| `ui/tests/e2e/startup-reveal.test.ts:53`, `capture-inbox.test.ts:375`, `ui/tests/unit/capture-main.behavior.test.ts:121` | unaffected | Delayed backend publication (`AVKIT_E2E_BACKEND_DELAY_MS`): the tests wait for `app-shell` only (never gated) or check stderr. `get-backend-url` resolves once published, so the boot GET fails `FETCH_FAILED` and the gate opens; every retry is caught, so nothing is left unhandled. |
| `ui/tests/e2e/mcp-setup-prompt.test.ts` (3), `ui/tests/unit/settings-mcp-prompt.test.ts`, `settings-emphasis.test.tsx`, `settings-rail.test.tsx` (3), `icon-hints.test.ts:173`, `mcp-server/tests/tools-parity.test.ts:167`, `tests/e2e/test_api_health_settings.py` (5) | unaffected | They answer or assert the `/settings/ui` API, which is unchanged. `settings-rail.test.tsx:523` is a comment. |
| `ui/tests/unit/capture-page.test.ts:19,329`, `help-card.test.ts` (4), `command-palette.test.ts` (2), `convert-commands.test.ts:7`, `download-commands.test.ts:7`, `downloader-page.test.ts` (2), `transcript-page.test.ts` (2), `persist-ui.test.ts:30`, `ui/tests/e2e/help-search.spec.ts:49` | unaffected | `AppShell` source scans for palette listeners, raw hex and other `localStorage` keys; none is affected by the gate or the placeholder. |

**New contradictions:** none. AC-56.4, AC-67.24/AC-67.26 and AC-71.14 are `unaffected`, for the reasons above.

**Canon edits (D-109):** G30 names `useG30Styles()` in its rule, preferred approach, good example and checklist item 2. G32's exception names the `useG30Styles()` hook. In 06 §Theme-reactive selects, "Reactive styles" names `useDocumentTheme` and `useG30Styles()`, and "First paint" cites `Spec §Progressive Loading Strategy` instead of `Spec §Loading (no theme flash)`. The section's opening note still describes the measured defect in terms of `getG30Styles()`, as history.

## Execution Correction Notes

| Item | Change | Evidence |
|---|---|---|
| EC-1 | `session-gate.ps1` `$expectedBaselinePyFailed` gains `tests/unit/test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]`. It is excused, like the other two, only if `s40-base-py.txt` shows it `FAILED`. | §Baseline: it fails on HEAD `7b29fcd` against the committed `docs/distribution/mcp.json.example`, outside `PRODUCT_SCOPE`. The plan's rule (§1) is that a test failing at baseline is never a regression. |
| EC-2 | AC-93.4's source clause reads "every `showDirectoryDialog(` sits inside an `onBrowse=` handler" as: the call sits inside an `onBrowse=` handler, or inside a helper function whose every reference sits inside an `onBrowse=` handler. Plan review F4 (Low) carried this to row 4. | `SettingsPage.tsx:407`, `:437`, `:447`, `:457` call it from `browseDownloadPath`, `browseTranscriptDir`, `browseModelsDir` and `browseTtsOutputPath`, each referenced once from a `PathRow` `onBrowse` (`:589`, `:731`, `:770`, `:822`). Mat accepted D-119 A on 2026-10-25 (`walkthrough.md` §MEU-94 Green: S2 stop). |
| EC-3 | `TEST_AMENDMENTS` gains **TA-3** `ui/tests/unit/console-polish.test.ts:234` (AC-27.10): `not.toContain('SelectInput')` becomes `not.toMatch(/<SelectInput\b/)` plus `not.toMatch(/import\s*\{[^}]*\bSelectInput\b[^}]*\}/)`; lines 235–237 stay. The file joins Files Modified and the `session-gate.ps1` `scope-paths` allow-list. | S2 at row 3: ConsolePanel's `useG30Styles` import path `'../ui/SelectInput'` (AC-94.3, TA-1) tripped the substring check; `SelectInput` is not in `CENSUS_PATTERNS`. Mat accepted D-118 A on 2026-10-25 (`walkthrough.md` §MEU-94 Green: S2 stop). |
| EC-4 | The row 4 AC-93.3 test asserted the read-only `output-path` stays `''` after typing and after a cancelled Browse. It now asserts that the field keeps the value it had before typing (`initial`), which is the AC text ("Cancel ... keeps the value"; "Typing in `output-path` does not change it"). No assertion was removed, and the PUT checks are unchanged. | Row 5's first run (`s40-run-row5.txt`) failed only there: `expected '~/Documents' to be ''`. `TTSPage.tsx:64` `OUTPUT_DEFAULT` is shown while `settings.output_path` is empty. The Red run had stopped at the earlier `label[for="tts-output-path"]` assertion, so it never reached the line. This is a test-fixture fact, not a product change. Flagged for the reviewer. |
| EC-5 | Closeout under Mat's ruling D-120 (2026-10-26, option 2). Gate runs 1–4 stand as the row 6 gate, with no re-run. The H1-2 fresh gate and the H1-6b full-evidence check are waived, not run, and their task rows are `[B]` (human-decision gate) linked to §Gate ruling. The H1-7 Codex execution review runs as planned, and MEU-93/94 go to `approved` only on its approved verdict. | §Gate ruling (D-120). No passing full gate exists for this tree. Every AC-93/AC-94 test passed in all four runs, and each run's one non-baseline failure is recorded in §Session gate. |
| EC-6 | Execution review round 1, F1 (High, AC-94). `useSyncDocumentTheme` now bounds the whole boot load by `BOOT_RETRY_WINDOW_MS`. When the window passes with an attempt still pending, it logs once, settles on the current document theme, and ignores a late answer; unmount clears the deadline. New tests: `theme-selects.test.tsx` AC-94.6 (f) and (g), plus an AC-94.11 never-answering request case. No existing assertion changed. | Codex round 1 traced a `GET /settings/ui` that connects and never answers: the 60 s window was only checked after a rejection, so `THEME_GATE` held every route forever. The product change is in `lib/theme.ts` only. Checks after the fix are in §Execution review. The gate runs 1–4 tree predates this fix; under D-120 there is no gate re-run. |

## MEU-94 Red (row 2)

- **Row command** (task row 2, verbatim, run through `run_row.py`): exit 0 (`s40-run-row2.txt`: `red-check: 2 receipt(s), 5 required test(s), 0 problem(s)`, `row 2 exit=0`). The `ui/src` guard found no change since `baseline.sha`, so the build and the Electron tests ran on the baseline renderer (`s40-94-red-build.txt`: `built in 4.10s`).
- **Written:**
  - The new `ui/tests/unit/theme-selects.test.tsx` covers AC-94.1 to AC-94.6 and AC-94.11.
  - The new helper `ui/tests/e2e/theme-probe.ts` implements `THEME_PROBE`, `THEME_COLOURS` and the held checks.
  - The `themeProbe` option was added to `installSettingsSeam`, `installTtsSeam` and the Convert `installSeam`. Each seam's fetch asks `window.__avkitThemeProbe.handle` before its own routes.
  - Electron tests: AC-94.7 and AC-94.8 (a)–(d) in `settings.test.ts`, AC-94.9 in `tts-generate.test.ts`, AC-94.10 in `convert-queue.test.ts`.
  - TA-1 (`chrome-zorivest.test.ts`): `useG30Styles` plus `not.toMatch(/G30_DARK\s*=/)`. TA-2 (`tts-page.test.ts`): `not.toMatch(/getG30Styles/)`.
- **Vitest** (`s40-94-red-ui.txt`, exit 1): `Test Files 1 failed (1)`, `Tests 15 failed (15)`. Every failure is an `AssertionError`:
  - `expected 'undefined' to be 'function'` for the new exports (`useDocumentTheme`, `g30StylesFor`, `readBootTheme`, `RouteThemePending`);
  - `expected [ …(6) ] to deeply equal []` (AC-94.3, the `getG30Styles` source scan);
  - `after light: expected [ …(10) ] to deeply equal []` (AC-94.4, Settings selects off the light pair);
  - `boot-theme.ts exists: expected false to be true` (AC-94.5);
  - `expected undefined to be false` for AC-94.6 (a)–(e): the baseline `useSyncDocumentTheme` returns nothing.
- **Electron** (`s40-94-red-e2e.txt`, exit 1): `7 failed`, every failure an `Error: expect(…)`:

| Test | Failing assertion | Received |
|---|---|---|
| AC-94.7 | `expectThemeColours` dark (`settings.test.ts:683`) | 10 selects dark, each selected option `rgb(255, 255, 255)/rgb(30, 41, 59)`: the fixed `NATIVE_OPTION_MENU_STYLE` light pair, the defect this MEU fixes |
| AC-94.8 (a), (b) | `expectThemeHeld`, `route-theme-pending` shown (`theme-probe.ts:220`) | `false`: no route gate |
| AC-94.8 (c) | `documentIsDark` false while held (`settings.test.ts:726`) | `true`: no boot mirror |
| AC-94.8 (d) | `storedMirror` is `'light'` on launch 1 (`settings.test.ts:739`) | `null`: no mirror write |
| AC-94.9 | `expectThemeHeld`, `route-theme-pending` shown (`theme-probe.ts:220`) | `false` |
| AC-94.10 | `expectThemeHeld`, `route-theme-pending` shown (`theme-probe.ts:220`) | `false` |

- **Red-check** (`s40-94-red-check.txt`, exit 0): `red-check: 2 receipt(s), 5 required test(s), 0 problem(s)`. Every test titled AC-94.7, AC-94.8, AC-94.9, AC-94.10 or AC-94.11 failed by assertion, and no receipt carries a setup failure.
- **Type check at Red.** `npx tsc --noEmit` exits 2, with errors only in `theme-selects.test.tsx`:
  - TS2339/TS2551 for the six names Green adds (`useDocumentTheme`, `g30StylesFor`, `useG30Styles`, `readBootTheme`, `THEME_STORAGE_KEY`, `RouteThemePending`);
  - TS2367 at the `settled === true` comparison, because the baseline hook returns `void`.

  Green resolves all of them; row 6 runs the type check on the finished tree. eslint on the seven test files: exit 0.
- **Assertion shape.** Playwright 1.62.1 reports a `toBeVisible` miss as `Error: element(s) not found`, and an `expect.poll` with a custom message as `Error: <message>`. `red-check.py` refuses both as unattributed, so presence checks poll `isVisible()` and the polls carry no custom message.

## MEU-94 Green (row 3): S2 stop

- **Row command** (task row 3, verbatim, through `run_row.py`): exit 1 (`s40-run-row3.txt`: `Test Files 1 failed | 9 passed (10)`, `Tests 1 failed | 193 passed (194)`, `row 3 exit=1`). The one failure is AC-27.10 at `ui/tests/unit/console-polish.test.ts:234`, `expect(panel).not.toContain('SelectInput')`. ConsolePanel now imports `useG30Styles` from `'../ui/SelectInput'`, the one copy that AC-94.3 and TA-1 require, and that path string contains `SelectInput`. The census missed it because `SelectInput` is not in `CENSUS_PATTERNS`. This is S2. No test was edited and row 3 is not marked.
- **Evidence probe** (read-only, `row3_probe.ps1`; it decides nothing, it only rules S4 in or out):
  - Full UI suite (`s40-94-green-probe-ui-all.txt`): `Test Files 1 failed | 101 passed (102)`, `Tests 1 failed | 1027 passed (1028)`. The only failure is the same AC-27.10 line. All of AC-94.1 to AC-94.6 and AC-94.11 pass, and so do AC-20.13, TA-1 and TA-2.
  - Build (`s40-94-green-probe-build.txt`): ok.
  - Electron, the three row-3 specs (`s40-94-green-probe-e2e.txt`): `60 passed (1.5m)`, including AC-94.7 to AC-94.10. No S4.
  - `tsc --noEmit` and eslint on the touched files: clean.

### D-118: How AC-27.10 treats ConsolePanel's `useG30Styles` import from `SelectInput.tsx`   [source-conflict] [execution]

**Recommendation:** A. Amend `console-polish.test.ts:234` only, as TA-3: `expect(panel).not.toMatch(/<SelectInput\b/)` and `expect(panel).not.toMatch(/import\s*\{[^}]*\bSelectInput\b[^}]*\}/)`. The intent of SUPERSEDED_26 is that the console level control is no longer a `SelectInput` (plan `2026-08-20-p6-gui-console-polish` :105, :183). This keeps that ban on the component and on importing it by name, and stops the check from matching a module path. Lines 235–237 stay.

**Why not the others**
| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A: TA-3, the check bans the component, not the path | — | — | MEU-27 handoff `.agent/context/handoffs/2026-08-20-p6-gui-console-polish-MEU-27-handoff.md:168`; plan `2026-08-20-p6-gui-console-polish` :105, :183 |
| ⚠️ B: new `components/ui/g30-styles.ts` holding the pairs and both hooks; `SelectInput.tsx` re-exports them and ConsolePanel imports from the new file | No test edit, and the plan's `TEST_AMENDMENTS` list stays at two | An unplanned file outside `PRODUCT_SCOPE`. Its only purpose is to get past a substring check, and the check stays able to misfire the next time someone imports from that module | plan §`TEST_AMENDMENTS` :136; MEU-27 handoff :168 |
| ❌ C: keep the ConsolePanel copy of the pairs (the MEU-27 workaround) | No test edit, no new file | Two copies again. This contradicts G30 "one copy", AC-94.3 and TA-1 (`not.toMatch(/G30_DARK\s*=/)`), so AC-94.3 goes red | MEU-27 handoff :168 (the inlined copy MEU-94 deletes); `emerging-standards.md` G30 |

**Precedent:** MEU-27 hit this exact check. It "still saw `SelectInput` via `getG30Styles` import" and was handled by inlining `getG30Styles` into ConsolePanel (handoff :168). That inlined copy is what MEU-94 removes. Earlier S2 stops were ruled by the human: s32 D-89 and s33 A-5 to A-7.
**Research:** Pomera/Tavily. ESLint `no-restricted-imports` (`importNames`) and ast-grep rules restrict a named import or its usage, not a path substring, which supports A's shape. The results were thin.
**Reversibility / risk:** two-way. If A is wrong, a later change could import `SelectInput` under an alias without the check noticing. That is unlikely, and the JSX ban still catches any use of the component.
**If you do not answer:** row 3 stays held and nothing after it runs.

### D-119: How AC-93.4's source check treats the existing Settings directory helpers (plan-review F4)   [plan-gate] [execution]

**Recommendation:** A. Implement AC-93.4's source clause as EC-2: a `showDirectoryDialog(` call counts as inside a `PathRow` `onBrowse` when it sits inside an `onBrowse=` handler, or inside a helper function whose every reference sits inside an `onBrowse=` handler. Four calls sit in helpers today: `browseDownloadPath` (`SettingsPage.tsx:407`), `browseTranscriptDir` (`:437`), `browseModelsDir` (`:447`) and `browseTtsOutputPath` (`:457`). Each is referenced once, from a `PathRow` `onBrowse` (`:589`, `:731`, `:770`, `:822`). The intent of the AC is that every Browse in Settings goes through `PathRow`, and A tests exactly that.

**Why not the others**
| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A: EC-2, helpers count when only `onBrowse` uses them | — | — | plan AC-93.4 :222; plan review F4 (walkthrough §Plan review) |
| ⚠️ B: the literal reading; inline the four helpers into their `onBrowse` arrows | The check is a plain text scan | Edits four `PathRow`s that MEU-93 does not otherwise touch, for no change in behaviour | plan AC-93.4 :222 |
| ❌ C: the literal reading with no code change | — | Red on the baseline helpers forever. AC-93.4 can never pass, which forces B anyway | `SettingsPage.tsx:407-457` |

**Precedent:** none found for this check. The plan review rated F4 Low and non-blocking and carried it to row 4.
**Research:** not run. This is a question of how to read the project's own AC, and no outside source applies.
**Reversibility / risk:** two-way. If A is wrong, a helper called from outside `onBrowse` would fail the check, which is the behaviour the AC wants anyway.
**If you do not answer:** row 4 carries A as EC-2 and flags it for the execution reviewer.

## MEU-94 Green (row 3)

- **Ruling.** Mat accepted every recommendation on 2026-10-25 ("all recommendations are accepted, continue"): D-118 A and D-119 A.
- **TA-3** (D-118 A, `ui/tests/unit/console-polish.test.ts:234`): `expect(panel).not.toContain('SelectInput')` becomes `expect(panel).not.toMatch(/<SelectInput\b/)` and `expect(panel).not.toMatch(/import\s*\{[^}]*\bSelectInput\b[^}]*\}/)`. Only that line changed; lines 235–237 stay. CRLF kept.
- **Implemented:**
  - `THEME_HOOK`: `useDocumentTheme()` (`useSyncExternalStore` over `THEME_CHANGED_EVENT`) is the only `classList.contains('dark')` read in the renderer.
  - `G30_STYLES`: `useG30Styles()` and `g30StylesFor()` in `SelectInput.tsx`. `getG30Styles`, `NATIVE_OPTION_MENU_STYLE` and the ConsolePanel `G30_DARK`/`G30_LIGHT` copy are removed. The consumers are ConsolePanel, CaptureViewport ("Named"), SettingsPage (`GridSelect`, `audio_format`), and `SelectInput` itself for TTSPage and VoiceCombobox.
  - `BOOT_THEME`: the new `boot-theme.ts`, which is the first import of `main.tsx`; `applyDocumentTheme` writes the `av-kit.ui.theme` mirror.
  - `BOOT_RETRY`: `useSyncDocumentTheme()` retries only on `ApiError` 503, at 250/500/1000 ms and then every 2000 ms, while the next start is under 60 s from the first. It logs once and returns `settled`.
  - `THEME_GATE`: `AppShell` renders `RouteThemePending` (`route-theme-pending`, "Still loading…" after 3 s) until the theme settles.
- **Row command** (task row 3, verbatim, through `run_row.py`): exit 0 (`s40-run-row3b.txt`, `row 3 exit=0`).
  - Vitest (`s40-94-green-ui.txt`): `Test Files 10 passed (10)`, `Tests 194 passed (194)`.
  - Build (`s40-94-green-build.txt`): `built in 4.14s`.
  - Electron, the three specs whole (`s40-94-green-e2e.txt`): `60 passed (1.5m)`, AC-94.7 to AC-94.10 included. The probe held the theme request, and launch 2 of AC-94.8 (d) found the mirror. No S4.
  - Snapshot (`s40-94-snapshot.txt`): `row 3 ui/src files: 164`, written to `row3-ui-src.json`.
- **Before the ruling.** The first run (`s40-run-row3.txt`) failed only on AC-27.10. The read-only probe (`s40-94-green-probe-ui-all.txt`) ran the full UI suite at `Tests 1 failed | 1027 passed (1028)`, and that one failure is the line TA-3 amends. AC-20.13 passed there.
- No MEU-93 behaviour changed.

## MEU-93 Red (row 4)

- **Tests written:**
  - AC-93.1: `layout-primitives.test.ts`, describe "MEU-93 PathRow placeholder and browseDisabled".
  - AC-93.2: `convert-page.behavior.test.ts`, inside the MEU-33 describe after AC-33.17.
  - AC-93.3: `tts-page.behavior.test.ts`, at the end of the MEU-56 describe.
  - AC-93.4: the new `settings-path-fields.test.tsx` (CRLF). The source clause follows EC-2, and the checker is self-checked on synthetic sources.
  - AC-93.5 and AC-93.6: `gui-actions-audit.test.ts`, with the `CONVERT_AUDIT_TESTIDS` entry and the "MEU-93 gui-actions audit" describe.
  - AC-93.6 block: `test-ids.ts`, after the MEU-71 block.
  - AC-93.7: `convert-queue.test.ts`.
  - Line endings are kept per file. `convert-page.behavior.test.ts` still has its 151 baseline LF lines.
- **Row command** (task row 4, verbatim, through `run_row.py`): exit 0 (`s40-run-row4.txt`, `row 4 exit=0`).
  - Tree check (`s40-93-red-tree.txt`): `ui/src changed since row 3: []`.
  - Vitest (`s40-93-red-ui.txt`, exit 1): `Tests 7 failed | 5 passed | 83 skipped (95)`. Every failure is an `AssertionError`:
    - AC-93.1 (placeholder): `expected null to be 'D:/x'`.
    - AC-93.2 (Browse): `the FormRow wrapper of convert-output-dir: expected null not to be null`.
    - AC-93.2 (cancel): `convert-output-dir-browse: expected null not to be null`.
    - AC-93.3 (row): `the PathRow label for tts-output-path: expected null not to be null`.
    - AC-93.4 (source): `expected [ 1008 ] to deeply equal []`. That is the `onClick` at `SettingsPage.tsx:1008`; the EC-2 helpers at `:407`, `:437`, `:447` and `:457` are accepted.
    - AC-93.5: `convert:browse_output_dir: expected undefined to be truthy`.
    - AC-93.5 negative: `expected [] to deeply equal [ Array(1) ]`.
  - Passing at Red:
    - AC-93.1 (no props).
    - AC-93.3 (Browse disabled while busy; the baseline Button already has `disabled={busy}`).
    - AC-93.4 (checker self-check).
    - AC-93.4 runtime: the baseline FormRow already renders the placeholder default and Browse in the labelled row. The source clause carries the Red.
    - AC-93.6, which the plan allows.
  - Build (`s40-93-red-build.txt`): exit 0.
  - Electron (`s40-93-red-e2e.txt`, exit 1): AC-93.7 `Error: expect(received).toBe(expected)` at `convert-queue.test.ts:1549` (`isShown(page, 'convert-output-dir-browse')`).
  - red-check (`s40-93-red-check.txt`): `2 receipt(s), 1 required test(s), 0 problem(s)`.

## MEU-93 Green (row 5)

- **Implemented:**
  - `PATH_ROW_PROPS`: `PathRow` gains `placeholder?` (on the input) and `browseDisabled?` (Browse `disabled`). With neither prop the markup is unchanged.
  - `PATH_ROWS`:
    - Convert: `convert-output-dir` is a `PathRow`. Its Browse (`convert-output-dir-browse`) patches `output_dir` from `showDirectoryDialog()`; a cancel is a no-op, and only `convert-page-save` sends the PUT.
    - TTS: `output-path` is a read-only `PathRow` in the run bar with `browseDisabled={busy}`. The Browse body is unchanged.
    - Settings: the capture-backup `FormRow` and `Button` became `<PathRow id="settings-capture-backup">` with the placeholder default. Every `showDirectoryDialog(` in `SettingsPage.tsx` now sits in an `onBrowse` (EC-2).
  - `CONVERT_BROWSE_INDEX`: the `convert:browse_output_dir` row comes after `convert:gpu_refresh` in `gui-actions-index.md`.
  - Line endings are kept (CRLF). `npm run typecheck` exit 0, and ESLint `--max-warnings 0` over the touched files exit 0 (probe receipts `s40-93-tsc-probe.txt`, `s40-93-lint-probe.txt`).
- **EC-4.** The first row 5 run (`s40-run-row5.txt`) failed only on AC-93.3 line 819: `expected '~/Documents' to be ''`. The test now asserts the field keeps its pre-typing value. See §Execution Correction Notes EC-4.
- **Row command** (task row 5, verbatim, through `run_row.py`): exit 0 (`s40-run-row5b.txt`, `row 5 exit=0`).
  - Vitest (`s40-93-green-ui.txt`): `Test Files 10 passed (10)`, `Tests 202 passed (202)`.
  - Build (`s40-93-green-build.txt`): `built in 4.33s`.
  - Electron, the three specs whole (`s40-93-green-e2e.txt`): `61 passed (1.7m)`. These include:
    - `ok 22 … AC-93.7 Convert Output folder Browse sits beside the field and fills it from the dialog`.
    - AC-93.8 (regression run): `ok 45 … W2-5 E2E_ACTUATE after E2E_SEAM_INSTALL`, which holds the Browse flow at `tts-generate.test.ts:371-396`, and `ok 53 … AC-64.6 Speed and Format are visible without scrolling at the default window`.
  - AC-56.4's run-bar containment passed in the unit run. No S4.

## Session gate (row 6): environment stop

- **Row command** (task row 6, verbatim, through `run_row.py`): exit 1 (`s40-run-row6.txt`, `row 6 exit=1`). Gate summary `s40-gate.txt`, `tested_state 7b29fcd0efcd11a1d8c5cbf4d725aaa66be84bb2+154d3f8eaacdeaea0b87c90888292fc9761058a3c60309d4d5ffcfb4a5defa48`.
  - Passed: `identity-before`, `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths` (`changed paths: 41 outside scope: []`), `mcp-build`, `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`.
  - `py-tests`: `1 failed, 936 passed`; the one failure is AC-25.7, which is in the row 0 baseline failed set (`every failure is in the row 0 baseline failed set; not a regression`, EC-1).
  - `ui-tests`: `Test Files 103 passed (103)`, `Tests 1040 passed (1040)`. `mcp-tests`: `446 passed (446)`.
  - `ui-electron` (`s40-D6-ui-electron.txt`): `1 failed`, `170 passed (3.8m)`. Every AC-93 and AC-94 Electron test passed.
  - `e2e-repeat`, `identity-npm` and `identity-after`: `not_run reason=fail-fast after ui-electron`.
- **The one failure is the environment.** `capture-inbox.test.ts:1928` AC-81.11 `HOTKEY_IN_USE_FIXTURE`: `Error: F2 held by another process`, `Expected: "HELD"`, `Received: "FAILED 0"`. The test's own helper could not register F2, so it never reached the app.
  - A `RegisterHotKey` probe for F2 (`s40-f2-probe.txt`, 2026-10-25T08:50:55-04:00, three tries) returned `registered=False lastError=1409` (`ERROR_HOTKEY_ALREADY_REGISTERED`) every time. No Electron or av-kit process was running.
  - `ShareX.exe -silent` (PID 9032, `D:\sharex\ShareX.exe`) is running. Session 34 recorded that Mat's ShareX holds F2 (`2026-10-14-capture-chrome` walkthrough A-11), and that plan made "F2 free" a row 0 precondition. This plan's row 0 has no such check.
  - No file under `ui/src/main` and no capture file is in this plan's Files Modified. The test needs F2 free, which is a machine precondition, not a product state.
- No product or test edit. Row 6 is not marked. ShareX is Mat's own app outside the worktree, so it was not stopped.

**Decision Brief (environment).** **Recommended:** Mat exits ShareX (tray → Exit), or tells me to stop PID 9032. Then I confirm F2 is free with the probe and re-run row 6 unchanged. **Why:** the gate excuses nothing new; AC-81.11 must pass on this tree like every other test. **Not chosen:** excusing AC-81.11 in the gate (it is not a baseline failure, and its row 0 state is unknown because the baseline Electron run covered only the three plan specs); skipping the test. **If ShareX is not the holder,** the probe still fails after it exits, and I look for the holder before re-running.

### Gate run 2: load timeout in AC-19.17

- Mat closed ShareX. `s40-f2-probe2.txt` (09:24) registered F2 on all three tries.
- **Row command, run 2:** exit 1 (`s40-run-row6b-ac1917.txt`; the gate summary is kept as `s40-gate-run2-ac1917.txt`). The tested_state was the same as run 1.
  - `py-tests` passed the baseline rule: `1 failed, 936 passed`, AC-25.7 only (EC-1). It took 288.25 s, against 105 s in run 1.
  - `ui-tests`: `1 failed | 1039 passed (1040)`. The one failure was outside the baseline: `tests/unit/command-palette.test.ts > AC-19.17 SHELL_PALETTE_IDS > registers only shell palette ids and keeps Ctrl+K on AppShell`, `Error: Test timed out in 5000ms` (`s40-D6-ui-tests-run2-ac1917.txt`).
  - Every later step: `not_run reason=fail-fast after ui-tests`.
- **Cause: load, not this plan.**
  - The test runs `await import(...AppShell)` inside the test body, so cold-transforming AppShell's module graph counts against the 5 s timeout.
  - THEME_GATE changed no import in `AppShell.tsx` (`git diff` shows no `import` line changes).
  - The test passed in run 1 on the same tested_state. Run alone, it passed three times out of three: 496 ms, 337 ms, 482 ms (`s40-ac1917-rerun1..3.txt`).
  - CPU load was 71%, mostly Mat's own apps (Cursor, BiglyBT, Plex). None of them was stopped.
- I made no product or test edit and added no retry or timeout change. Row 6 was re-run unchanged (run 3).

### Gate run 3: Electron hang in AC-67.24

- **Row command, run 3:** exit 1 (`s40-run-row6c.txt`; the summary is kept as `s40-gate-run3.txt` and the Electron receipt as `s40-D6-ui-electron-run3.txt`). The tested_state was the same.
  - F2 probe at 09:32 (`s40-f2-probe3.txt`): registered on all three tries.
  - `py-tests` passed the baseline rule: `1 failed, 936 passed` in 142.83 s, AC-25.7 only.
  - `ui-tests`: `1040 passed (1040)`. AC-19.17 passed this time.
  - `mcp-tests`: `446 passed`. Build, OpenAPI and state-render: pass.
  - `ui-electron`: `1 failed`, `170 passed (6.7m)`, against 3.8 m in run 1. Every AC-93, AC-94 and AC-81.11 test passed.
- **The one failure:** `capture-inbox.test.ts:1543` AC-67.24 `Test timeout of 60000ms exceeded`, then `Worker teardown timeout of 60000ms exceeded`. No assertion or locator step failed. The app hung in launch or close, and Playwright then could not tear the worker down.
  - The test passed in run 1 on the same tested_state.
  - `--repeat-each=10` of that test alone: `10 passed (28.2s)`, 2.0 to 3.1 s each (`s40-ac6724-repeat10.txt`).
  - No av-kit process was left after the run.
  - The test does use the path field this plan reworked (`settings-leaf-capture-backup_dir`). But a failing path field would fail an assertion, not hang for a full minute with nothing pending, and the field passed all ten repeats.
- I made no product or test edit and added no retry. Row 6 was re-run unchanged (run 4).

### Gate run 4: Electron hang in AC-67.35 (second miss, stop)

- **Row command, run 4:** exit 1 (`s40-run-row6d.txt`; the summary is kept as `s40-gate-run4.txt` and the Electron receipt as `s40-D6-ui-electron-run4.txt`). The tested_state was the same: `7b29fcd…+154d3f8e…fa48`.
  - F2 probe at 09:45 (`s40-f2-probe4.txt`): registered on all three tries.
  - `py-tests` passed the baseline rule: `1 failed, 936 passed` in 152.29 s, AC-25.7 only.
  - `ui-tests`: `1040 passed`. `mcp-tests`: `446 passed`. Every static, build, OpenAPI and state-render step: pass.
  - `ui-electron` (09:50:03–09:59:33): `1 failed`, `170 passed (9.5m)`. Every AC-93, AC-94, AC-81.11 and AC-67.24 test passed.
- **The one failure:** `capture-inbox.test.ts:1594` AC-67.35, test 33 of the run, `Test timeout of 60000ms exceeded`, then `Worker teardown timeout of 60000ms exceeded`. No step failed. This is the same shape as run 3, two tests later.
  - Two earlier plans recorded the same shape (`2026-09-28-p11-transcript-tts` walkthrough line 151, `2026-10-16-tts-voice-panel` A-2). Each time, other agents were running on the host.
  - During this stage a new session started on the host: `P:\zorivest\.venv\Scripts\python.exe` at 09:52:36, then node, serena, graphify and miniconda MCP servers at 09:53:23–26. Test 33 would have been running at about that time.
  - `capture-inbox.test.ts` alone, after run 4: `39 passed (1.2m)` (`s40-capture-inbox-file1.txt`).
  - No av-kit or Electron process was left.
- **This plan's code cannot plausibly hang a launch or close.**
  - It touches no `ui/src/main` file.
  - `boot-theme.ts` does one guarded `localStorage` read.
  - `RouteThemePending` sets one 3 s timer.
  - The BOOT_RETRY loop waits at least 250 ms between attempts, stops inside 60 s, and clears its timer on unmount.
  - A route held by THEME_GATE would fail a locator, and Playwright would print it. These runs printed no pending step.
- **Stop.** Runs 3 and 4 are two misses of the same hang shape, back to back. The Session 35 rule is "a second miss stops for Mat", so I did not start run 5. No product or test file changed, and I added no retry. Row 6 is not marked.

**Decision Brief (environment).** **Recommended:** Mat pauses the other agent sessions on this host (the zorivest session that started at 09:52) while row 6 runs. I then re-run row 6 unchanged. If it passes, the walkthrough records runs 2–4 as environment misses. **Also recommended, for H2:** open a known issue `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` (MONITORING, P4) that lists the `2026-09-28-p11-transcript-tts`, `2026-10-16-tts-voice-panel` and Session 40 occurrences, with "SEEN" notes and receipts. The next step would be timestamped launch and close diagnostics in `launchApp`. **Not chosen:** re-running until green with no change to the host (two misses already); excusing AC-67.24 or AC-67.35 in the gate (neither is a baseline failure); a retry or longer timeout (S6, and it would hide the hang).

## Gate ruling (Mat, 2026-10-26, D-120)

- **Context.** Session 41 (`gui-keyboard-palette`) builds on this tree, so Session 40 has to be committed first. I offered three ways to finish it. Option 1: accept the gate as already passed, record runs 1–4 as the gate, do the bookkeeping (row 7, the handoffs, the reflection and metrics), skip the Codex execution review, then Mat commits.
- **Mat's answer, 2026-10-26, verbatim:** `1`. Before that, Mat asked, verbatim: `why do you need follow process on Session 40 since we are just skipping it?`
- **Revised the same day, verbatim:** `I changed my mind, I'd like the Option 2 with the codex review`. Option 2 is option 1 plus the H1-7 Codex execution review: no gate re-run, and the review is the independent check. This revision replaces option 1.
- **What stands as the row 6 gate.** Runs 1–4 on tested_state `7b29fcd0efcd11a1d8c5cbf4d725aaa66be84bb2+154d3f8eaacdeaea0b87c90888292fc9761058a3c60309d4d5ffcfb4a5defa48`.
  - Every AC-93 and AC-94 test passed in all four runs.
  - `py-tests`: AC-25.7 was the only failure, and it is a baseline failure (EC-1).
  - Each run had exactly one other failure:

    | Run | Failure | Cause | Check run on its own |
    |---|---|---|---|
    | 1 | AC-81.11 | F2 held by ShareX | — |
    | 2 | AC-19.17 | timeout under load | 3/3 passed |
    | 3 | AC-67.24 | Electron hang | `--repeat-each=10` passed 10/10 |
    | 4 | AC-67.35 | Electron hang | `capture-inbox.test.ts` passed 39/39 |

  - Never run on this tree: `e2e-repeat`, `identity-npm` and `identity-after`, because every run stopped fail-fast at its one failure.
  - No run passed whole.
- **Waived, not run:** the H1-2 fresh gate after row 7 and the H1-6b full-evidence check.
- **Still run:** the H1-7/H1-7a/H1-7b Codex execution review. Its input is the two handoffs, which carry runs 1–4 as the gate record and a `not_run` record for H1-2. MEU-93/94 go to `approved` only on its approved verdict.
- **Inputs changed after the gate's tested_state.** These are row 7 and H2 hub and state writes: the 06 Delivered notes, `meu-status.yaml`, the rendered `BUILD_PLAN.md`, the grouping, `known-issues.yaml` and its render. `layout-canon` and `queue-canon`, the suites that read them, are re-run at H2-2.

## Hub (row 7)

- 06 §Path fields and §Theme-reactive selects each gain a `> **Delivered (Session 40).**` note after the section table. Each note says the execution review was waived (D-120).
- `meu_status.py update MEU-94 ready_for_review --plan docs/execution/plans/2026-10-24-gui-theme-path-fields/`, and the same for MEU-93. Both exit 0 (`s40-hub-update-MEU-9{4,3}.txt`, `Updated MEU-9n → ready_for_review (updated: 2026-10-26)`). Then `render` (`s40-hub-render.txt`: `✅ All regions rendered successfully.`).
- **Row command** (task row 7, verbatim, through `run_row.py`): exit 0 (`s40-run-row7.txt`).
  - `rg` finds both Delivered notes at `06-gui.md:1414` and `:1436`, and `execution_plan` at `meu-status.yaml:2455` and `:2481`.
  - `hub problems: []`.
  - `✅ Drift check passed — SSOT loaded (98 MEUs, 12 phases), rendered regions match on-disk content`.
- **H1-1** (verbatim): exit 0, `unchecked implementation rows: []`. Row 6 is `[B]` under D-120, and rows 0–5 and 7 are `[x]`.

## Execution review (H1-7)

- **Ledger loop** `s40-execution-2026-10-24-gui-theme-path-fields` opened (`s40-exec-ledger-begin.txt`: `mode=execution budget=6 tokens=21,000,000`).
- **Round 1** (`s40-exec-r1`, row H1-7 exit 0): `changes_required`, 1 blocking finding, 4,937,758 tokens.
  - **F1 (High, AC-94).** A `GET /settings/ui` that connects and never answers left `settled` false, because `BOOT_RETRY_WINDOW_MS` was checked only after a rejection. `THEME_GATE` then held every route forever.
  - Codex's own checks passed: targeted Vitest 165/165 over nine files, typecheck, both handoff validators and the task linter. It found that D-118, D-119 and EC-4 keep their intent, and that the four gate-run failures show no regression from this diff.
- **Correction (EC-6).** `lib/theme.ts`: a `deadline` timer set at mount for `BOOT_RETRY_WINDOW_MS`. A shared `finish()` clears both timers and settles. Late `then`/`catch` answers return early once `finished` is set, and unmount clears the deadline. New tests: AC-94.6 (f) a never-answering attempt, (g) unmount while pending, and AC-94.11 AppShell opening the route at 60 s.
  - **Red** (`s40-f1-red-theme.txt`, exit 1). With the deadline pushed to 2,000,000,000 ms (a scratch mutation, restored byte-for-byte), `Tests 2 failed | 16 passed (18)`, both by `AssertionError`:
    - (f): `expected false to be true`, which is `settled` at 60 s;
    - AC-94.11: `expected null not to be null`, which is the route child at 60 s.
    - (g) passes on both trees; it guards cleanup.
  - **Green** (`s40-f1-green-theme.txt`, exit 0): `Tests 18 passed (18)`.
  - `npm run typecheck` exit 0 (`s40-f1-tsc.txt`). ESLint `--max-warnings 0` on the two files: exit 0 (`s40-f1-lint.txt`).
  - Full UI unit suite (`s40-f1-ui-all.txt`, exit 0): `Test Files 103 passed (103)`, `Tests 1043 passed (1043)`.
  - Row 3 re-run verbatim (`s40-run-row3c-f1.txt`, exit 0): Vitest `Tests 199 passed (199)`, build ok, and Electron `61 passed (2.7m)`. That run included AC-94.7, AC-94.8 (a)–(d), AC-94.9 and AC-94.10.
  - Not re-run, under D-120: the session gate.
- **Round 2** (`s40-exec-run-r2.txt`): `approved`, 0 open findings, `intent_achieved: yes`, 6,364,311 tokens. Codex re-ran 168 targeted tests and appended "Recheck (2026-10-26) — Round 2" to the implementation critical review.

## Closeout (H2)

- Reflection `docs/execution/reflections/2026-10-24-gui-theme-path-fields-reflection.md`. Grouping §8 D-101 is still `open` in the grouping, so it is carried as `autonomous` ("left open for its owner"), following the 2026-10-16 tts-voice-panel D-56 row.
- Clerical edits that the closeout validator needed, with no change in meaning: the plan's D-110 and D-111 precedent strings were reworded (`<leaf>` became "the settings leaf", and `disabled={busy}` became "Browse disabled while busy"). In `known-issues.yaml`, the two resolved issues' enrichment `decision_log` sequences were re-indented and their folded lines joined. The parsed YAML was asserted equal before and after.
- Known issues: `GUI-LIGHT-THEME-SELECT-STALE-DARK` and `GUI-CONVERT-OUTPUT-NO-BROWSE` resolved; `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` and `PACKAGING-MCP-SNIPPET-TOKEN-STALE` opened. MEU-93 and MEU-94 are `approved`, and the grouping lists Session 40 as `approved`.
- Rows H2-2 through H2-5 exit 0 (`s40-run-H2-2.txt` to `s40-run-H2-5.txt`). No commit.
