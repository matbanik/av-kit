# Walkthrough — Capture editor options (Session 37)

Execution record for [implementation-plan.md](implementation-plan.md) and [task.md](task.md). Worktree `P:/av-kit-wt/s37-capture-editor-options`, branch `claude/s37-capture-editor-options`. Receipts are under `C:/Temp/av-kit/s37-*.txt`; decisive lines are pasted here.

## Execution message

The user's explicit execution message (2026-10-16), which satisfies `plan_to_exec_gate: human` after the round 3 plan approval:

> "@.agent/workflows/execution-session.md  Session 37 per session grouping"

Latest reflection rules applied (`2026-10-14-capture-render-fidelity-reflection.md`): RULE-1 (the gate applies the baseline rule itself; build outputs are their own stages), RULE-2 (`red-check.py` strips ANSI and carries the coloured fixture), RULE-3 (every row command sets the environment it depends on).

## Baseline (row 0)

Row 0 exit 0 (`C:/Temp/av-kit/s37-row0-run.txt`). Prerequisites: `prereq problems: []`, python 3.12.12 (`s37-prereq.txt`). `BASE_MARKERS` held.

| Suite | Result | Receipt |
|---|---|---|
| pytest | 2 failed, 674 passed | `s37-base-py.txt` |
| ui Vitest | 87 files, 839 passed | `s37-base-ui.txt` |
| mcp-server Vitest | 23 files, 411 passed | `s37-base-mcp.txt` |
| Electron E2E | 34 passed | `s37-base-e2e.txt` |

Baseline pytest failing set (`s37-base-check.txt`), which the gate's baseline rule carries forward (RULE-1): `tests/unit/test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]` and `tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]`. Both are packaging checks outside the Capture renderer. No receipt lacked a result summary.

## Census (row 1)

Row 1 exit 0: `rg` over `ui/tests` for the 22 `CENSUS_PATTERNS` gave 132 hits (`C:/Temp/av-kit/s37-census.txt`; its first line is the rtk banner). The run used the baseline test tree: the row 2 drafts (`capture-scrub.test.ts` and the `capture-help-content.test.ts` addition) were held outside the tree for the run and restored after it.

Totals: 127 `unaffected`, 3 TA-1, 1 TA-2, 1 TA-4, 0 `new-contradiction` (no S2). TA-3 has no census hit: it only appends ids to `test-ids.ts`. AC-65.1 (`capture-toolbar.test.ts:42-62`) holds because the lock joins `TOOLBAR_BUTTONS` but not `TOOL_BUTTON_IDS`. `NO_SHOT_IDS` (`icon-hints.test.ts:48`) is a fixed set and the enabled lock's expected hint is its name. The Playwright `fill` calls (`capture-inbox.test.ts:258`, `:449`, `:578`) are typed edits (`TYPED_EDITS`). `<label` had no hit; the AC-57.5 `closest('label')` line is matched by `capture-stroke` (TA-4).

| # | Hit `file:line` | Pattern(s) | Disposition |
|---|---|---|---|
| 1 | `e2e/console-chrome.test.ts:184` | `aria-pressed` | unaffected: outside Capture |
| 2 | `e2e/console-chrome.test.ts:189` | `aria-pressed` | unaffected: outside Capture |
| 3 | `e2e/console-chrome.test.ts:198` | `aria-pressed` | unaffected: outside Capture |
| 4 | `unit/capture-action-row.test.ts:362` | `TOOLBAR_BUTTONS` | unaffected: asserts containment, uniqueness, name and icon, or iterates entries; the lock entry satisfies each (enabled with no shot, so its hint is its name) |
| 5 | `unit/capture-action-row.test.ts:376` | `TOOLBAR_BUTTONS` | unaffected: asserts containment, uniqueness, name and icon, or iterates entries; the lock entry satisfies each (enabled with no shot, so its hint is its name) |
| 6 | `unit/capture-action-row.test.ts:480` | `capture-named-color` | unaffected: the select, its values and the apply path are unchanged; only option styles change |
| 7 | `unit/capture-action-row.test.ts:702` | `four-tools` | unaffected: toContain checks; the body only gains two sentences |
| 8 | `unit/capture-action-row.test.ts:703` | `four-tools` | unaffected: toContain checks; the body only gains two sentences |
| 9 | `unit/capture-help-content.test.ts:12` | `four-tools` | unaffected: toContain checks; the body only gains two sentences |
| 10 | `unit/capture-help-content.test.ts:13` | `four-tools` | unaffected: toContain checks; the body only gains two sentences |
| 11 | `unit/capture-help-content.test.ts:19` | `four-tools` | unaffected: toContain checks; the body only gains two sentences |
| 12 | `unit/capture-help-content.test.ts:20` | `four-tools` | unaffected: toContain checks; the body only gains two sentences |
| 13 | `unit/capture-help-content.test.ts:29` | `four-tools` | unaffected: toContain checks; the body only gains two sentences |
| 14 | `unit/capture-help-content.test.ts:30` | `four-tools` | unaffected: toContain checks; the body only gains two sentences |
| 15 | `e2e/capture-inbox.test.ts:258` | `capture-stroke` | unaffected: Playwright fill is a typed edit (TYPED_EDITS) |
| 16 | `e2e/capture-inbox.test.ts:449` | `capture-font-size` | unaffected: Playwright fill is a typed edit (TYPED_EDITS) |
| 17 | `e2e/capture-inbox.test.ts:578` | `capture-font-size` | unaffected: Playwright fill is a typed edit (TYPED_EDITS) |
| 18 | `e2e/capture-inbox.test.ts:585` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 19 | `e2e/capture-inbox.test.ts:864` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 20 | `e2e/capture-inbox.test.ts:872` | `expectNoOverflow` | unaffected: helper unchanged; AC-65.4 is re-run with the lock at rows 7 and 8 (S2 if it overflows) |
| 21 | `e2e/capture-inbox.test.ts:876` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 22 | `e2e/capture-inbox.test.ts:898` | `expectNoOverflow` | unaffected: helper unchanged; AC-65.4 is re-run with the lock at rows 7 and 8 (S2 if it overflows) |
| 23 | `e2e/capture-inbox.test.ts:904` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 24 | `e2e/capture-inbox.test.ts:905` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 25 | `e2e/capture-inbox.test.ts:906` | `expectNoOverflow` | unaffected: helper unchanged; AC-65.4 is re-run with the lock at rows 7 and 8 (S2 if it overflows) |
| 26 | `e2e/capture-inbox.test.ts:1260` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 27 | `e2e/capture-inbox.test.ts:1996` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 28 | `e2e/capture-inbox.test.ts:2292` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 29 | `e2e/capture-inbox.test.ts:2299` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 30 | `e2e/download-queue.test.ts:1187` | `aria-pressed` | unaffected: outside Capture |
| 31 | `e2e/download-queue.test.ts:1191` | `aria-pressed` | unaffected: outside Capture |
| 32 | `e2e/test-ids.ts:216` | `capture-stroke` | unaffected: existing ids are unchanged; TA-3 only appends three ids |
| 33 | `e2e/test-ids.ts:217` | `capture-font-size` | unaffected: existing ids are unchanged; TA-3 only appends three ids |
| 34 | `e2e/test-ids.ts:233` | `capture-named-color` | unaffected: existing ids are unchanged; TA-3 only appends three ids |
| 35 | `e2e/test-ids.ts:388` | `capture-chrome-tools` | unaffected: existing ids are unchanged; TA-3 only appends three ids |
| 36 | `unit/capture-page.behavior.test.ts:398` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 37 | `unit/capture-page.behavior.test.ts:399` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 38 | `unit/capture-page.behavior.test.ts:401` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 39 | `unit/capture-page.behavior.test.ts:402` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 40 | `unit/capture-page.behavior.test.ts:537` | `capture-stroke` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 41 | `unit/capture-page.behavior.test.ts:538` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 42 | `unit/capture-page.behavior.test.ts:540` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 43 | `unit/capture-page.behavior.test.ts:566` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 44 | `unit/capture-page.behavior.test.ts:600` | `AC-60.4` | unaffected: the lock defaults off, so auto-Select is unchanged |
| 45 | `unit/capture-page.behavior.test.ts:604` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 46 | `unit/capture-page.behavior.test.ts:625` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 47 | `unit/capture-page.behavior.test.ts:690` | `capture-named-color` | unaffected: the select, its values and the apply path are unchanged; only option styles change |
| 48 | `unit/capture-page.behavior.test.ts:894` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 49 | `unit/capture-page.behavior.test.ts:897` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 50 | `unit/capture-page.behavior.test.ts:1111` | `capture-named-color` | unaffected: the select, its values and the apply path are unchanged; only option styles change |
| 51 | `unit/capture-page.behavior.test.ts:1121` | `capture-named-color` | unaffected: the select, its values and the apply path are unchanged; only option styles change |
| 52 | `unit/capture-page.behavior.test.ts:1131` | `capture-named-color` | TA-1: the orange-option style test (`:1129`) is rewritten as AC-86.2 in row 4 |
| 53 | `unit/capture-page.behavior.test.ts:1132` | `option.style` | TA-1 (row 4) |
| 54 | `unit/capture-page.behavior.test.ts:1133` | `option.style` | TA-1 (row 4) |
| 55 | `unit/capture-page.behavior.test.ts:1140` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 56 | `unit/capture-page.behavior.test.ts:1250` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 57 | `unit/capture-page.behavior.test.ts:1251` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 58 | `unit/capture-page.behavior.test.ts:1253` | `capture-stroke` | TA-4: `closest('label')` becomes the handle text and the input aria-label (row 2) |
| 59 | `unit/capture-page.behavior.test.ts:1270` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 60 | `unit/capture-page.behavior.test.ts:1395` | `MEU65_` | unaffected: hard-coded id lists that the lock and the scrub handles do not join |
| 61 | `unit/capture-page.behavior.test.ts:1406` | `MEU65_` | unaffected: hard-coded id lists that the lock and the scrub handles do not join |
| 62 | `unit/capture-page.behavior.test.ts:1415` | `MEU65_` | unaffected: hard-coded id lists that the lock and the scrub handles do not join |
| 63 | `unit/capture-page.behavior.test.ts:1421` | `capture-named-color` | unaffected: the select, its values and the apply path are unchanged; only option styles change |
| 64 | `unit/capture-page.behavior.test.ts:1423` | `capture-stroke` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 65 | `unit/capture-page.behavior.test.ts:1424` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 66 | `unit/capture-page.behavior.test.ts:1427` | `expectOptionGroups` | unaffected: the option groups and their input testids are unchanged; the handles carry new ids |
| 67 | `unit/capture-page.behavior.test.ts:1428` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 68 | `unit/capture-page.behavior.test.ts:1430` | `MEU65_` | unaffected: hard-coded id lists that the lock and the scrub handles do not join |
| 69 | `unit/capture-page.behavior.test.ts:1442` | `MEU65_` | unaffected: hard-coded id lists that the lock and the scrub handles do not join |
| 70 | `unit/capture-page.behavior.test.ts:1447` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 71 | `unit/capture-page.behavior.test.ts:1449` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 72 | `unit/capture-page.behavior.test.ts:1450` | `MEU65_` | unaffected: hard-coded id lists that the lock and the scrub handles do not join |
| 73 | `unit/capture-page.behavior.test.ts:1465` | `MEU65_` | unaffected: hard-coded id lists that the lock and the scrub handles do not join |
| 74 | `unit/capture-page.behavior.test.ts:1466` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 75 | `unit/capture-page.behavior.test.ts:1472` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 76 | `unit/capture-page.behavior.test.ts:1474` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 77 | `unit/capture-page.behavior.test.ts:1476` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 78 | `unit/capture-page.behavior.test.ts:1495` | `MEU65_` | unaffected: hard-coded id lists that the lock and the scrub handles do not join |
| 79 | `unit/capture-page.behavior.test.ts:1516` | `expectOptionGroups` | unaffected: the option groups and their input testids are unchanged; the handles carry new ids |
| 80 | `unit/capture-page.behavior.test.ts:1525` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 81 | `unit/capture-page.behavior.test.ts:1526` | `expectOptionGroups` | unaffected: the option groups and their input testids are unchanged; the handles carry new ids |
| 82 | `unit/capture-page.behavior.test.ts:1527` | `capture-stroke` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 83 | `unit/capture-page.behavior.test.ts:1540` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 84 | `unit/capture-page.behavior.test.ts:1541` | `expectOptionGroups` | unaffected: the option groups and their input testids are unchanged; the handles carry new ids |
| 85 | `unit/capture-page.behavior.test.ts:1542` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 86 | `unit/capture-page.behavior.test.ts:1551` | `capture-stroke` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 87 | `unit/capture-page.behavior.test.ts:1553` | `capture-stroke` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 88 | `unit/capture-page.behavior.test.ts:1554` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 89 | `unit/capture-page.behavior.test.ts:1671` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 90 | `unit/capture-page.behavior.test.ts:1840` | `capture-font-size` | unaffected: the input keeps its testid, aria-label and typed-edit behaviour (TYPED_EDITS) |
| 91 | `unit/capture-page.behavior.test.ts:1925` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 92 | `unit/capture-page.behavior.test.ts:1981` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 93 | `unit/capture-page.behavior.test.ts:2001` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 94 | `unit/capture-page.behavior.test.ts:2023` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 95 | `unit/capture-page.behavior.test.ts:2552` | `aria-pressed` | unaffected: existing toggles keep aria-pressed; the lock is a new id outside these assertions |
| 96 | `unit/capture-toolbar.test.ts:11` | `TOOL_BUTTON_IDS` | unaffected: the lock is not added to TOOL_BUTTON_IDS (AC-65.1 holds) |
| 97 | `unit/capture-toolbar.test.ts:12` | `TOOLBAR_BUTTONS` | unaffected: asserts containment, uniqueness, name and icon, or iterates entries; the lock entry satisfies each (enabled with no shot, so its hint is its name) |
| 98 | `unit/capture-toolbar.test.ts:42` | `TOOLBAR_BUTTONS` | unaffected: asserts containment, uniqueness, name and icon, or iterates entries; the lock entry satisfies each (enabled with no shot, so its hint is its name) |
| 99 | `unit/capture-toolbar.test.ts:43` | `TOOL_BUTTON_IDS` | unaffected: the lock is not added to TOOL_BUTTON_IDS (AC-65.1 holds) |
| 100 | `unit/capture-toolbar.test.ts:44` | `TOOL_BUTTON_IDS` | unaffected: the lock is not added to TOOL_BUTTON_IDS (AC-65.1 holds) |
| 101 | `unit/capture-toolbar.test.ts:47` | `TOOL_BUTTON_IDS` | unaffected: the lock is not added to TOOL_BUTTON_IDS (AC-65.1 holds) |
| 102 | `unit/capture-toolbar.test.ts:49` | `TOOLBAR_BUTTONS` | unaffected: asserts containment, uniqueness, name and icon, or iterates entries; the lock entry satisfies each (enabled with no shot, so its hint is its name) |
| 103 | `unit/capture-toolbar.test.ts:109` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 104 | `unit/capture-toolbar.test.ts:113` | `capture-chrome-tools` | unaffected: the lock is not an option control; AC-65.4 overflow is re-run at rows 7 and 8 (S2 if it overflows) |
| 105 | `unit/capture-page.test.ts:102` | `capture-stroke` | unaffected: a test-ids.ts membership list; the id is unchanged |
| 106 | `unit/capture-page.test.ts:111` | `four tools` | unaffected: section id and title are unchanged; only the body grows |
| 107 | `unit/capture-page.test.ts:259` | `four tools` | unaffected: section id and title are unchanged; only the body grows |
| 108 | `unit/capture-page.test.ts:480` | `G30` | unaffected: the raw-hex className scan passes; swatches use inline style objects and CaptureScrubField uses tokens |
| 109 | `unit/chrome-zorivest.test.ts:284` | `G30` | unaffected: outside Capture |
| 110 | `unit/chrome-zorivest.test.ts:304` | `G30` | unaffected: outside Capture |
| 111 | `unit/downloader-page.test.ts:434` | `G30` | unaffected: outside Capture |
| 112 | `unit/header-toggles.test.ts:36` | `aria-pressed` | unaffected: outside Capture |
| 113 | `unit/header-toggles.test.ts:39` | `aria-pressed` | unaffected: outside Capture |
| 114 | `unit/header-toggles.test.ts:50` | `aria-pressed` | unaffected: outside Capture |
| 115 | `unit/header-toggles.test.ts:56` | `aria-pressed` | unaffected: outside Capture |
| 116 | `unit/header-toggles.test.ts:122` | `aria-pressed` | unaffected: outside Capture |
| 117 | `unit/header-toggles.test.ts:126` | `aria-pressed` | unaffected: outside Capture |
| 118 | `unit/header-toggles.test.ts:135` | `aria-pressed` | unaffected: outside Capture |
| 119 | `unit/convert-page.test.ts:649` | `G30` | unaffected: outside Capture |
| 120 | `unit/icon-hints.test.ts:21` | `TOOLBAR_BUTTONS` | unaffected: asserts containment, uniqueness, name and icon, or iterates entries; the lock entry satisfies each (enabled with no shot, so its hint is its name) |
| 121 | `unit/icon-hints.test.ts:48` | `NO_SHOT_IDS` | unaffected: a fixed set the lock is not added to |
| 122 | `unit/icon-hints.test.ts:308` | `12 Capture toolbar` | TA-2: title becomes 13 Capture toolbar buttons (row 6) |
| 123 | `unit/icon-hints.test.ts:311` | `TOOLBAR_BUTTONS` | unaffected: asserts containment, uniqueness, name and icon, or iterates entries; the lock entry satisfies each (enabled with no shot, so its hint is its name) |
| 124 | `unit/icon-hints.test.ts:318` | `TOOLBAR_BUTTONS` | unaffected: asserts containment, uniqueness, name and icon, or iterates entries; the lock entry satisfies each (enabled with no shot, so its hint is its name) |
| 125 | `unit/icon-hints.test.ts:320` | `NO_SHOT_IDS` | unaffected: a fixed set the lock is not added to |
| 126 | `unit/icon-hints.test.ts:323` | `NO_SHOT_IDS` | unaffected: a fixed set the lock is not added to |
| 127 | `unit/queue-primitives.test.ts:803` | `G30` | unaffected: outside Capture |
| 128 | `unit/settings-rail.test.tsx:499` | `aria-pressed` | unaffected: outside Capture |
| 129 | `unit/settings-rail.test.tsx:514` | `aria-pressed` | unaffected: outside Capture |
| 130 | `unit/settings-rail.test.tsx:516` | `aria-pressed` | unaffected: outside Capture |
| 131 | `unit/tts-page.test.ts:264` | `G30` | unaffected: outside Capture |
| 132 | `unit/tts-page.test.ts:271` | `G30` | unaffected: outside Capture |

## MEU-85 Red (row 2)

Row 2 exit 0. `red-check.py`: 2 receipts, 0 problems (`C:/Temp/av-kit/s37-85-red-check.txt`). The guard found no `ui/src` change.

- **Unit** (`s37-85-red-ui.txt`, exit 1): 3 files failed; 13 tests failed, 93 skipped.
  - `capture-scrub.test.ts` (AC-85.1 to AC-85.5): `Failed to resolve import "../../src/renderer/src/features/capture/CaptureScrubField"`. That is a declared new module (`DECLARED_NEW`).
  - AC-85.11: `AssertionError: expected 'Arrow, Box, Highlight, and Text draw …' to contain 'Drag the Stroke or Size label, or use…'`.
  - AC-85.6 (two tests), AC-85.7, AC-85.8 (two), AC-85.9 (two), AC-85.12 (a) to (e): `AssertionError: expected null not to be null` at `expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()`.
- **Electron** (`s37-85-red-e2e.txt`, exit 1): AC-85.10 failed with `Error: expect(received).toBe(expected)`, expected 1 and received 0, at the handle count. The `RENDERER_PIN` assertion before it passed.
- **TA-4** is applied at the AC-57.5 line. **TA-3** adds `CAPTURE_STROKE_SCRUB` and `CAPTURE_FONT_SIZE_SCRUB` to `ui/tests/e2e/test-ids.ts`.
- **Author fix during Red:** the first run asserted the handle count before the box was drawn. With Select active and nothing selected, `optionGroups` returns `['color']`, so that check would have failed in Green too. The count now comes right after the box is drawn and shows stroke 3. Row 2 was re-run; the receipts above are from that second run.

## MEU-85 Green (row 3)

Row 3 exit 0. The recorded `ui/src` hash is `4c44299b1b304af4492af770f77e2ea353e3d6f6c3f1bb39b67e2a3f9d346629` (`s37-ui-src-3.txt`); row 4 runs against it.

- **Typecheck** (`s37-85-green-types.txt`): `tsc --noEmit` clean.
- **Unit** (`s37-85-green-ui.txt`): 8 files passed, 164 tests passed.
- **Build** (`s37-85-green-build.txt`): built in 4.08s.
- **Electron** (`s37-85-green-e2e.txt`): the whole `capture-inbox.test.ts` passed, 35 of 35, including AC-85.10 (1.6s). Pointer capture holds in Electron, so the S4 stop did not trigger.
- **Source:**
  - New `capture-scrub.ts` holds `SCRUB_MATH`, and `parsePositiveInt` moved there from `CapturePage.tsx` unchanged.
  - New `CaptureScrubField.tsx` holds `SCRUB_FIELD`, `SCRUB_GESTURES` and `SCRUB_ALT_GUARD`. The wheel listener is native with `passive: false`, and Escape is a window listener.
  - `SIZE_LABELS` is in `CaptureViewport.tsx`, with the Stroke and Size fields plus the preview, commit and cancel props.
  - `SIZE_BURST` is in `CapturePage.tsx`:
    - `previewSize`, `finishSize` and `cancelSize` hold the burst.
    - Every other edit path calls `finishSize()` first.
    - While the burst is open, Undo and Redo are disabled.
  - The scrub sentence is in `capture-help-content.ts`.
  - `TYPED_EDITS` are untouched.
- **Test changes after Red.** All four fix the test's own setup; no assertion was weakened.
  - AC-85.7 and AC-85.12 (b): the selected mark paints first, so DOM order follows the selection. `rectStrokes` now sorts the rects by `x` before reading the strokes.
  - AC-85.12 (d): Undo clears the selection, which hides the Stroke field. The test reselects the mark with `selectMarkAt(0)` before the wheel step.
  - AC-85.10: `scrubDrag` rounds the handle centre to whole pixels, so the Shift +6 px move gives exactly three coarse steps.
  - AC-85.10: the handle-count move is described under MEU-85 Red.

## MEU-86 Red (row 4)

Row 4 exit 0. `red-check.py`: 2 receipts, 0 problems (`C:/Temp/av-kit/s37-86-red-check.txt`). The guard read `ui/src` as `4c44299b…`, the same hash row 3 recorded.

- **Unit** (`s37-86-red-ui.txt`, exit 1): 2 files failed; 3 tests failed, 1 passed and 101 skipped.
  - AC-86.1, and its negative: `AssertionError: expected 'undefined' to be 'function'` at the `contrastText` presence check.
  - AC-86.2: `AssertionError: red: expected [ '#FF0000', '#ff0000', …(1) ] to include 'rgb(255, 255, 255)'`. The option still has the light menu surface.
  - The AC-86.2 negative passes on the baseline, as it should. It guards that the placeholder keeps `NATIVE_OPTION_MENU_STYLE`, which is already true and must stay true through Green.
- **Electron** (`s37-86-red-e2e.txt`, exit 1): AC-86.3 failed with `Error: expect(received).toEqual(expected)`. Every option computes `backgroundColor` `rgb(255, 255, 255)` and `color` `rgb(30, 41, 59)`; for orange that matches the plan's expected Red. The `RENDERER_PIN` assertion before it passed.
- **TA-1:** the test "named color menu options use dark text on a light surface" was rewritten under the AC-86.2 title. Its light-surface assertion now applies to the placeholder (AC-86.2 negative) and to the closed select.

## MEU-86 Green (row 5)

Row 5 exit 0. The recorded `ui/src` hash is `9c3682b0a24aa0b48c1ed6c560c6072771803f3daabeebd03c8af1e01eb03ad0` (`s37-ui-src-5.txt`); row 6 runs against it.

- **Typecheck** (`s37-86-green-types.txt`): clean.
- **Unit** (`s37-86-green-ui.txt`): 8 files passed, 167 tests passed.
- **Build** (`s37-86-green-build.txt`): built.
- **Electron** (`s37-86-green-e2e.txt`): the whole `capture-inbox.test.ts` passed, 36 of 36, including AC-86.3 (2.3s). Electron applies the option styles, so the S4 stop and `POPOVER_FALLBACK` do not apply.
- **Source:**
  - `capture-color.ts` gains `contrastText`, which is `CONTRAST_TEXT`. It uses WCAG 2.1 relative luminance and picks black when black's ratio is at least white's. Anything `normalizeHex` rejects throws `RangeError`.
  - `CaptureViewport.tsx` gains the module constant `SWATCH_OPTIONS`, built from `NAMED_COLOR_HEX`. Each named option uses `{ backgroundColor: hex, color: contrastText(hex) }`.
  - The `Named` placeholder keeps `NATIVE_OPTION_MENU_STYLE`, and the closed select keeps `namedMenuStyle`.
- No test changed after Red.

## MEU-87 Red (row 6)

Row 6 exit 0. `red-check.py`: 2 receipts, 0 problems (`C:/Temp/av-kit/s37-87-red-check.txt`). The guard read `ui/src` as `9c3682b0…`, the same hash row 5 recorded.

- **Unit** (`s37-87-red-ui.txt`, exit 1): 3 files failed; 10 tests failed, 1 passed and 111 skipped.
  - AC-87.1: `AssertionError: expected undefined to be 'Keep tool after drawing'`.
  - AC-87.2 to AC-87.5, all eight page tests including the four negatives: `AssertionError: expected null not to be null`. Each fails at the `capture-tool-lock` presence check.
  - AC-87.7: `AssertionError: expected 'Arrow, Box, Highlight, and Text draw …' to contain 'The lock button keeps the current too…'`.
  - The AC-87.1 negative passes on the baseline, as it should. It guards that `TOOL_BUTTON_IDS` keeps exactly the five tools.
- **Electron** (`s37-87-red-e2e.txt`, exit 1): AC-87.6 failed with `Error: expect(received).toBe(expected)`, expected 1 and received 0, at the lock count. This is the `ELECTRON_RED` reason the plan expects. The `RENDERER_PIN` assertion before it passed.
- **TA-2:** the AC-80.8 title now reads "the 13 Capture toolbar buttons"; the body is unchanged. **TA-3:** `CAPTURE_TOOL_LOCK` is added to `ui/tests/e2e/test-ids.ts`.
- The help sentence the tests pin for `HELP_SENTENCES` is "The lock button keeps the current tool after each mark."

## MEU-87 Green (row 7)

Row 7 exit 0.

- **Typecheck** (`s37-87-green-types.txt`): clean.
- **Unit** (`s37-87-green-ui.txt`): 8 files passed, 178 tests passed.
- **Build** (`s37-87-green-build.txt`): built.
- **Electron** (`s37-87-green-e2e.txt`): the whole `capture-inbox.test.ts` passed, 37 of 37, including AC-87.6 (910ms). AC-65.4, the no-overflow check at the default window, still passes (1.8s), so the lock adds no overflow and S2 does not apply.
- **Source:**
  - `capture-toolbar.ts`: `TOOLBAR_BUTTONS` gains `'capture-tool-lock': { icon: Lock, name: 'Keep tool after drawing' }`. `TOOL_BUTTON_IDS` is unchanged.
  - `CaptureViewport.tsx`: new optional props `toolLocked`, which defaults to `false`, and `onToggleToolLock`, which defaults to a no-op. The lock is a `ToolbarIconButton` placed straight after the "Annotation tool" group. It uses `pressed={toolLocked}` and `variant={toolVariant(toolLocked)}`, and it is never disabled.
  - `CapturePage.tsx`: `toolLocked` page state, default `false` and not persisted. It is toggled only by the lock button (`LOCK_PERSISTS`).
    - With the lock on, the drawn-create path and the text commit skip `commitSelection` (`LOCK_KEEPS_TOOL`).
    - With the lock off, both paths are unchanged.
  - `capture-help-content.ts`: the `four-tools` body gains "The lock button keeps the current tool after each mark." after the scrub sentence.
- **Test change after Red:** the AC-87.2 negative called `renderPage()` without emptying the catalogue, so a shot was available and the Box tool was enabled. Its own precondition, that Box is disabled, failed. The test now uses the suite's established no-shot setup (`catalogItems = []` and an empty `['captures']` query, as in AC-57.5 and AC-65.2). No assertion changed. In the Red run it had already failed earlier, at the lock presence check, so the Red proof is unaffected.

## Gate (row 8)

Row 8 exit 0 on run 3 (`C:/Temp/av-kit/s37-gate.txt`), which is the gate of record for row 8. Runs 1 and 2 failed and are kept as `s37-gate-run1.txt` and `s37-gate-run2.txt`. Run 3 printed `tested_state 90bb40977e487f4893a1c586c2c20b8f78ef105f+3dab0639e1c9cf76cd09e0e0055069ec42b14fb84651177246fb18afe42187a3` at both identity steps, which matched (`tested_state before == after`).

| Step | Stage | Exit | Decisive line (run 3) |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 90bb409…+3dab0639…87a3` |
| py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract | static | 0 | — |
| scope-paths | static | 0 | `changed paths: 30 outside scope: []` |
| py-tests | full | 1 → pass (baseline rule) | `2 failed, 674 passed, 1 warning`; `baseline rule: failed=2 outside_baseline=[] errors=0` (the two §Baseline packaging tests) |
| ui-tests | full | 0 | `Test Files 88 passed (88)`, `Tests 878 passed (878)` (baseline 839; +39 new) |
| mcp-build, mcp-tests | full | 0 | `Test Files 23 passed (23)`, `Tests 411 passed (411)` (baseline 411) |
| ui-build, ui-harness-build, ui-picker-stub | full | 0 | — |
| openapi | full | 0 | — |
| state-render | full | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` |
| ui-electron | runtime | 0 | `147 passed (3.0m)` |
| e2e-repeat | runtime | 0 | `30 passed (32.1s)` (AC-85.10, AC-86.3, AC-87.6, `--repeat-each=10`) |
| identity-npm | identity | 0 | `@playwright/test@1.62.1`, `electron@42.9.3` |
| identity-after | identity | 0 | `tested_state before == after` |

**A-1 (run 1, failed at `ui-tests`: 2 failed, 876 passed; `s37-gate-run1-ui-tests.txt`).** AC-51.6 (`layout-primitives.test.ts:200`) and AC-81.13 (`capture-action-row.test.ts`) pin the sha256 of `ui/tests/e2e/test-ids.ts` before `// MEU-51 primitive harness IDs.`. TA-3 had inserted the three new ids inside that prefix, so both registry tests failed. The ids moved, unchanged, to a new tail block, `// MEU-85/87 Capture size scrub and tool lock (additive IDs).`. The prefix sha256 is again `6E569F82…FF454`, byte-identical to the baseline prefix. Both files then passed 25/25 (`s37-a1-check.txt`). No test, assertion or product line changed.

TA-3 as planned only said "gains" the ids. The targeted Green rows ran the files each MEU touched, not the id-registry tests, so this surfaced first at the full gate. That is a reflection lesson.

**A-2 (run 2, failed at `ui-electron`: 1 failed, 146 passed; `s37-gate-run2-ui-electron.txt`).** `convert-queue.test.ts:1059` W8-12 failed with `Error: locator.click: Target crashed`, meaning the Electron renderer process died during a click on `bulk-clear-selection`. The test is on the Convert page, outside the Capture renderer, and neither it nor any Convert source differs from `90bb409`.
- Run alone with `--repeat-each 20`, it passed 20 of 20 (`s37-w812-repeat20.txt`).
- The full suite then passed in run 3 (147 of 147).

S6 covers flakes in this session's Electron tests under `--repeat-each`, and those passed 30 of 30. A one-off renderer crash in an untouched page does not trigger it. It is recorded here and carried to the reflection rather than retried away.

**A-3 (H1-2 run 1, failed at `e2e-repeat`: 1 failed, 29 passed; `s37-gate-h1-run1.txt`, `s37-gate-h1-run1-e2e-repeat.txt`).** AC-85.10 failed on its first repeat, the first app launch after the full Electron suite: after the +40 px Stroke-label drag the box read `stroke-width` 8, not 23. 8 is one 10 px move (5 steps of 2 px); the later moves were dropped and nothing was reverted. Every step before `e2e-repeat` exited 0 at the same `tested_state` as row 8. This is S6 (a flake in this session's Electron test under `--repeat-each`).
- **Cause.** The "Stroke" label is about 34 px wide and the drag starts at its centre, so the first move stays on the label and the later ones leave it. `CaptureScrubField` read moves only from the label, so it depended on pointer capture taking effect; `setPointerCapture` sits in a silent try/catch.
- **Investigation.** An instrumented probe logged a successful scrub in all 97 observations (30 plain, 40 with every core busy, 5 with the window blurred, and 2 replays of the gate order: the full suite 181/181, then the probe ×10). These are scrub observations, not 97 clean test runs: the loaded run's suite receipt reports 39 passed and 1 timeout, although that run logged correct scrub values in all 40 iterations. Capture was taken every time. No remount, lost selection or open draw gesture can occur during a label drag.
- **Proof.** With `Element.prototype.setPointerCapture` made to throw, the pre-A-3 field fails exactly as H1-2 run 1 did (`Expected "23"`, `Received "8"`), and the A-3 field passes 5 of 5 (`s37-a3-prefix-probe.txt`, `s37-a3-nocapture-probe.txt`). The probe spec was temporary and is deleted.
- **Decision.** S6 says a racy product stops with a brief. Mat chose option 1 (harden the drag) on 2026-10-16.
- **Change.** `SCRUB_DRAG_WINDOW`: on pointerdown the field adds capture-phase window `pointermove`, `pointerup` and `pointercancel` listeners, filtered by pointer id, and removes them when the drag ends or the field unmounts. Capture is still requested, and a lost capture still cancels. New unit test `capture-page.behavior.test.ts:2214` (the moves and the release land on `document.body`): Red `expected [ '3' ] to deeply equal [ '23' ]` (`s37-a3-red.txt`), Green 123/123 with `tsc` and `eslint` clean (`s37-a3-green.txt`). No existing assertion changed; the inserted test moves later line references by +20, and the MEU-85 and MEU-87 handoffs were updated.
- **Re-gate.** H1-2 was re-run in full on the A-3 tree; its `tested_state` replaces row 8's as the fresh full record.

**A-4 (H1-2 run 2, failed at `ui-tests`: 1 failed, 878 passed; `s37-gate-h1-run2.txt`, `s37-gate-h1-run2-ui-tests.txt`).** The failure was `queue-canon.test.ts` AC-41.3, `PILL_TOKEN_SOURCE light --color-status-pending`: `Expected "#ea580c"`, `Received "#9a3412"`.
- **Cause, outside this session.** AC-41.3 reads `P:/zorivest/ui/src/renderer/src/globals.css` live. While run 2 was in progress, Zorivest committed `1f254832` (MEU-662, its `main`, 21:30). That commit changed the light hexes for `--color-status-pending` (`#ea580c` → `#9a3412`), `-filled` (`#16a34a` → `#166534`) and `-rejected` (`#dc2626` → `#991b1b`).
  - Session 37 changes none of the test's inputs: `git diff 90bb409` lists 0 paths under `styles.css`, `lib/queue` or the test.
  - av-kit `main` (`4a97483`) still carries the old hexes, so AC-41.3 fails there too.
  - The test reproduces alone: 1 failed, 7 passed (`s37-h12-queue-canon.txt`).
- **A-3 holds outside the gate.** The gate is fail-fast, so it skipped the runtime stages. Run alone on the same tree:
  - `e2e-repeat` passed 30/30 (`s37-h12-e2e-repeat-solo.txt`).
  - The full Electron suite passed 147/147 (`s37-h12-ui-electron-solo.txt`).
  - These runs are not a gate of record.
- **Decision.** No stop condition covers an external repository changing mid-gate, so this went to Mat as a Decision Brief. Mat chose option 1 on 2026-10-16: a ui-tests baseline rule plus a known issue.
- **Change.**
  - `baseline-ui-failed.txt` lists the AC-41.3 id alone.
  - `ui-baseline-rule.ps1` passes a Vitest exit 1 only when all of these hold:
    - every `FAIL` id is listed;
    - the summary's failed count equals the number of ids;
    - nothing is unhandled.
  - `session-gate.ps1` calls the rule for `ui-tests` exactly as it applies the py-tests rule.
  - A probe of six cases matched every expected exit (`s37-a4-rule-probe.txt`). It passed the run 2 receipt and refused:
    - the A-1 receipt;
    - an extra non-baseline `FAIL`;
    - a count mismatch;
    - an unhandled error;
    - a receipt with no `FAIL` id.
  - Known issue `QUEUE-PILL-TOKEN-DRIFT` (open, P2) carries the re-port of the three hexes.
  - No product or test file changed for A-4.
- **Re-gate.** H1-2 run 3 is the gate of record (`s37-gate-h1.txt`), at `tested_state 90bb409…+7f784552…24dc`; identity before == after.
  - Every step passed.
  - py-tests and ui-tests passed by their baseline rules:
    - py-tests: `failed=2 outside_baseline=[] errors=0`.
    - ui-tests: `failed=1 summary_failed=1 outside_baseline=[] unhandled=0`, AC-41.3 only; `Tests 1 failed | 878 passed (879)`.
  - The other results:
    - MCP 411/411;
    - Electron 147 passed;
    - `e2e-repeat` 30 passed;
    - `changed paths: 39 outside scope: []`.

**Execution review round 1 (Codex `gpt-6.1-sol`, `changes_required`; F1 and F2, both High, both MEU-85).** The review accepted A-1, A-3 and A-4 on substance, recorded A-2, and found MEU-86 and MEU-87 met their contracts.
- **F1, AC-85.3/AC-85.4 `SCRUB_BASE`.** The viewport passed `fallback` 3 and 16 whatever was selected, so invalid field text scrubbed a stroke-20 box to 4 and a size-40 text to 17. The fallback is now the applicable selected mark's `stroke_width` or `font_size`.
- **F2, AC-85.12 (b).** `finishSize` closed the page's burst but the field kept its own burst value, so after a keyboard selection of a stroke-20 mark between wheel notches the next notch went from the first mark's 4 to 5. The page now bumps a per-field `sizeEpoch` in `finishSize` and `cancelSize`; the viewport passes that epoch plus the selected index as `resetKey`; the field clears its wheel timer, accumulator, key and burst value when the key changes, with no callback and without ending a drag. The epochs are per field, so `previewSize` finishing the other field's burst does not reset the field that is driving.
- **Red** (`s37-F12-red.txt`, four new tests with the pre-fix viewport wiring restored): `expected [ '4' ] to deeply equal [ '21' ]`, `expected [ '17' ] to deeply equal [ '41' ]`, `expected [ '4', '5' ] to deeply equal [ '4', '21' ]`, `expected [ '17', '18' ] to deeply equal [ '17', '41' ]`; `Tests 4 failed | 1 passed | 110 skipped`. The two F1 tests focus the input before the key events; on a first try without focus, the page's window key handler read ArrowUp as a nudge of the selected box, so Undo reverted the nudge instead of the scrub.
- **Green**: the four pass (`s37-F12-green.txt`, `Tests 5 passed | 110 skipped`); `npm run typecheck` and `npm run lint` exit 0; five affected unit files 180/180 (`s37-F12-unit.txt`). No existing assertion changed. The inserted tests move later `capture-page.behavior.test.ts` references by up to +99 lines; the handoffs and the A-3 bullet above were updated, and the Census keeps its base-file line numbers.
- **E4 note.** The A-3 investigation bullet above now says the 97 are scrub observations; the loaded run's suite receipt reported 39 passed and 1 timeout.
- **Re-gate.** H1-2 run 4 is the gate of record (`s37-gate-h1.txt`; run 3 archived as `s37-gate-h1-run3.txt` and `s37-gate-run3/`), at `tested_state 90bb40977e487f4893a1c586c2c20b8f78ef105f+5b04639a56a3e580f8a41cad881a7a5043c191d1ea867dc5ae6f251dd774fa93`; identity before == after. Every step passed:
  - py-tests `2 failed, 674 passed, 1 warning`, `failed=2 outside_baseline=[] errors=0`;
  - ui-tests `Tests 1 failed | 882 passed (883)`, `failed=1 summary_failed=1 outside_baseline=[] unhandled=0` (AC-41.3 only);
  - MCP 411/411; Electron `147 passed (3.3m)`; `e2e-repeat` `30 passed (50.4s)`; `changed paths: 42 outside scope: []`.

## Hub (row 9)

Row 9 exit 0.

- **Hub edits:**
  - `docs/build-plan/09-screenshot-capture.md`: one Plan note per MEU, at `:755` (D-10–D-15), `:767` (D-16–D-17) and `:780` (D-18–D-19).
  - `docs/build-plan/gui-actions-index.md:80`: the `capture:tool_lock` row.
  - `docs/build-plan/build-priority-matrix.md:75-77`: rows 9.18–9.20.
  - The Phase 9 note "MEU-85–87 bound to capture-editor-options.".
- **`rg`** (`s37-hub-rg.txt`): 14 hits across the four hub files, including all of the above.
- **`state-render`** (`s37-state-render.txt`): `Drift check passed — SSOT loaded (91 MEUs, 12 phases)`.
- **`gui-actions-audit`** (`s37-hub-audit.txt`): `Tests 4 passed (4)`.
- **Author fix during row 9:** the first run edited the Phase 9 line in `docs/BUILD_PLAN.md` directly, and `state-render` reported `phase-tracker (BUILD_PLAN.md)` drift. That line is rendered from the `note` of phase 9 in `.agent/context/meu-status.yaml`.
  - The sentence moved to that `note`.
  - `meu_status.py render` regenerated the line, and the second run passed.
  - The rendered line is identical to the first edit.
