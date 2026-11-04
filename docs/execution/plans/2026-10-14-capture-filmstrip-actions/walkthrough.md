# Walkthrough — 2026-10-14-capture-filmstrip-actions (Session 38)

Durable evidence for `task.md` rows. Receipts live under `C:/Temp/av-kit/s38-*` and are named by `validate-task.ps1`. Every check runs in `pwsh` from the worktree root `P:/av-kit-wt/s38-capture-filmstrip-actions`.

## Execution authorization and prerequisites (row 0)

- **Authorization:** Mat's execution message, "@.agent/workflows/execution-session.md Session 38 per session grouping" (2026-10-16), given after the plan review approval.
- **Context-tool gate (S1):** the first `prereq` run refused. `headroom` is now on PATH, but `graphify-out/` and `graphify-out-research/` are still absent. The S1 Decision Brief was answered `USER_EXPLICIT 2026-10-16`: "Going forward for this entire session all recemmendations are auto-approved." The recommendation was `not_applicable`, plus the `Invoke-Prereq` amendment, recorded in `implementation-plan.md` and `task.md` §Context-tool gate.
- **Dependencies:** `npm --prefix ui ci` exited 0, and so did the Electron `install.js`.
- **`prereq`:** `PASS MEU state {'MEU-57': 'approved', 'MEU-88': 'pending', 'MEU-89': 'pending'}; execution_plan set`, `PASS selftest`, `PASS npm-ci`, `PASS prereq`.

## Baseline

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check baseline *> C:/Temp/av-kit/s38-run-baseline.txt"
  exit: 0
  scope: "full Vitest and Playwright suites at the baseline commit"
  tested_state: "baseline.sha 90f041e0fd0ec15efddc77b8c57c4e074b0cb525 (worktree HEAD, no product edits)"
  decisive_output:
    - "PASS ui-build"
    - "PASS ui-harness-build"
    - "PASS baseline-vitest: 800 passed of 800"
    - "PASS baseline-e2e: expected 137 skipped 0"
    - "PASS baseline counts {'vitest_passed': 800, 'vitest_failed': 0, 'e2e_expected': 137, 'e2e_skipped': 0, 'e2e_unexpected': 0, 'e2e_flaky': 0, 'vitest_baseline_red': 0}"
    - "PASS baseline @ 90f041e0fd0ec15efddc77b8c57c4e074b0cb525"
```

- **First run failed: region-picker stub missing.** In the fresh worktree, the 4 `capture-picker.test.ts` specs failed with `spawn …\native\region-picker-stub\publish\avkit-region-picker-stub.exe ENOENT`. The stub had never been built there. **Fix:** `npm --prefix ui run build:picker-stub` (`dotnet publish`). The output (`native/region-picker-stub/bin|obj|publish`) is gitignored, as `git status --ignored` confirmed, so no tracked file changed. The re-run is the record above.
- `vitest_baseline_red` is 0, so `BASELINE_RED` did not fire.

## Census (row 1)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check census *> C:/Temp/av-kit/s38-run-census.txt"
  exit: 0
  scope: "TEST_AMENDMENTS census over ui/tests (channel count, clipboard, filmstrip, delete-confirm, test-id and sideEffects patterns)"
  tested_state: "baseline.sha 90f041e, before any test edit"
  decisive_output:
    - "PASS census: 274 lines in C:/Temp/av-kit/s38-census.txt; disposition each in walkthrough.md §Census"
```

`TEST_AMENDMENTS` holds exactly TA-1, TA-2 and TA-3. No hit is a `new-contradiction`, so S2 does not fire. Dispositions are grouped by file:

| File (hits) | Disposition |
|---|---|
| `ui/tests/unit/ipc-strict-census.test.ts` (14) | **`:52` `toHaveLength(19)` → TA-1** (`20`), and the valid-payload and type-failure tables (`:14-15`, `:36-37`) gain `write-clipboard-image` entries (TA-1). `:3` import, `:53-75` loops and the sideEffects shape → unaffected: they iterate whatever the list holds. |
| `ui/tests/unit/login-item-ipc.test.ts` (14) | **`:50-51`, both `toHaveLength(19)` → TA-2** (`20`). `:52` (`registered` equals the test list) → kept: it holds once TA-3 and the main registration land together. `:13`, `:27-30`, `:58-59` (login-item channels, sideEffects shape, preload keys) → unaffected. |
| `ui/tests/unit/ipc-channels.ts` (5) | **The list gains `write-clipboard-image` after `login-item-set` → TA-3.** It is not added to `IPC_NO_PAYLOAD` (`:32-36`). `:10-11` (the existing clipboard-text channels) → unaffected. |
| `ui/tests/unit/web-prefs-ipc.test.ts` (7) | Containment of renderer channels in the registered set → unaffected: it holds once row 3 registers the channel. |
| `ui/tests/unit/gui-actions-audit.test.ts` (5) | `:7` import and the existing `ACTION_ROWS` checks → unaffected. MEU-88 adds an append-only block. |
| `ui/tests/unit/capture-help-content.test.ts` (8) | `toContain` checks on help text → unaffected. `original-annotated` keeps its `endsWith`. |
| `ui/tests/unit/capture-page.behavior.test.ts` (58) | Toolbar delete: confirm text, test ids, clicks and `aria-current` movement → unaffected. The menu's Delete reuses the same confirm, and the toolbar path does not change. |
| `ui/tests/unit/capture-page.test.ts` (13) | Source rules (no `openPath` in the filmstrip, no hex `className`, no TODO) → unaffected. The new code follows them. |
| `ui/tests/e2e/capture-inbox.test.ts` (51) | Confirm label, `aria-current` and thumb counts after a delete → unaffected. |
| `ui/tests/e2e/test-ids.ts` (9) | Existing ids → unaffected. MEU-88/89 ids are append-only. |
| `ui/tests/unit/tts-page.test.ts` (4), `tts-page.behavior.test.ts` (1) | The `navigator.clipboard` rule → unaffected. The new copy path goes through the preload, not `navigator.clipboard`. |
| `copy-mcp-config` (6), `api-base-ipc` (4), `secret-paths` (2), `startup-metrics` (1) | The `sideEffects` / effects shape only → unaffected: `clipboard` is already a counted effect. |
| `app-shell-wiring` (5), `chrome-zorivest` (6), `console-actions` (3), `console-polish` (1), `console-chrome` e2e (3), `header-toggles` (1), `downloader-page.behavior` (1), `transcript-page.behavior` (1), `convert-page.behavior` (1) | `window.api` mocks and clipboard-text seams → unaffected: `writeClipboardImage` is an optional key, so the existing mocks still type-check. |
| `queue-card` (15), `queue-primitives` (4), `fixtures/queue-slot-baseline-cases` (1), `voice-combobox` (13) | An unrelated `onSelect` / selection vocabulary → unaffected. |
| `capture-main.behavior` (4), `capture-picker` e2e (2), `capture-filmstrip-label` (1), `settings-page` (3), `settings-rail` (3), `settings-emphasis` (1), `settings` e2e (1), `helpers/electron-stub` (1) | Capture main-process paths, picker, filmstrip label, settings and the Electron stub's `clipboard` → unaffected: none reads the channel count, the filmstrip menu or the delete flow. |

## MEU-88 Red (row 2)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check red88 *> C:/Temp/av-kit/s38-run-red88.txt"
  exit: 0
  scope: "MEU-88 Vitest (AC-88.1-88.11) and the Electron spec -g AC-88 (AC-88.12), before any product edit"
  tested_state: "baseline.sha 90f041e plus the row 2 test files and TA-1/TA-2/TA-3; no product source changed"
  decisive_output:
    - "PASS MEU-88 Vitest RED: 13 assertion failures, 0 missing-symbol, load-tolerated files ['capture-clipboard.test.ts', 'clipboard-image-main.test.ts'], TA pins failing ['MEU-61 login-item IPC AC-61.19 listRegisteredChannels length is IPC_CHANNEL_COUNT including IPC_GET and IPC_SET']"
    - "PASS ui-build"
    - "PASS MEU-88 E2E RED: ['AC-88.12']"
    - "PASS red88"
```

- **First run failed S4 on a test-authoring fault, not a contract mismatch.** The `gui-actions-audit` helper `preloadChannelFor` built its regex from a plain template literal, so `\b` became a backspace and `\(` lost its escape (`SyntaxError: Invalid regular expression … Unterminated group`). The fix was `String.raw`. No assertion changed. With the fix, the AC-88.11 guard test (an unknown preload key resolves to no channel) passes in Red, and AC-88.11 stays red through the `ACTION_ROWS` test, because `writeClipboardImage` is not in the preload yet.
- TA-1 (`ipc-strict-census`) is already green in Red. Its `toHaveLength(20)` reads the TA-3 test list, and both the valid and type-failure payloads for an unregistered channel return `ok:false`, so it does not fail. TA-2 fails as expected (`registered` is still 19).

## MEU-88 Green, main half (row 3)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check green88-main *> C:/Temp/av-kit/s38-run-green88-main.txt"
  exit: 0
  scope: "clipboard-image-main (AC-88.6-88.8), ipc-strict-census (TA-1), login-item-ipc (TA-2)"
  tested_state: "row 2 tests unchanged; ipc.ts (IMAGE_CHANNEL, IMAGE_PAYLOAD, IMAGE_HANDLER), clipboard-image.ts (MAIN_IMAGE_WRITE), index.ts wiring, preload.ts (PRELOAD_KEY), env.d.ts optional key"
  decisive_output:
    - "Test Files 3 passed (3); Tests 19 passed (19)"
    - "PASS green88-main-vitest: 19 passed of 19"
    - "PASS green88-main"
```

- `ipcMain.handle` throws on `{ ok: false }` and resolves `result.value` otherwise, so the renderer key is typed `writeClipboardImage?: (png: Uint8Array) => Promise<void>`, and `IMAGE_DECODE_ERROR` reaches the renderer as a rejected invoke.
- S3 (the `png` field arriving in main as a `Uint8Array` under real structured clone) is proven by the AC-88.12 Electron spec in row 4, not here.

## MEU-88 Green, renderer half (row 4)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check green88 *> C:/Temp/av-kit/s38-run-green88.txt"
  exit: 0
  scope: "MEU-88 Vitest (AC-88.1-88.11), ui build, and the Electron spec -g AC-88 (AC-88.12 a-f)"
  tested_state: "row 3 state plus capture-clipboard.ts, CaptureFilmstripMenu.tsx, CaptureFilmstrip.tsx and CapturePage.tsx; one test oracle narrowed (below)"
  decisive_output:
    - "PASS green88-vitest: 41 passed of 41"
    - "PASS ui-build"
    - "ok 1 AC-88.12 (a)(b)(f) Copy full path and Copy image reach the main-process clipboard"
    - "ok 2 AC-88.12 (c) Shift+F10 and the ContextMenu key open the menu from a focused thumb"
    - "ok 3 AC-88.12 (d)(e) menu Delete on a non-selected shot removes only it; no menu while a confirm is open"
    - "PASS green88-e2e: expected 3 skipped 0"
    - "PASS green88"
```

- **S3 and S5 did not fire.** In real Electron the `png` field reaches main as a `Uint8Array` (AC-88.12 b), and Chromium delivers both Shift+F10 and the ContextMenu key to a focused thumb (AC-88.12 c).
- **Test correction (one oracle, approved under the session's standing auto-approval, 2026-10-16).** The Red test "AC-88.5 without window.api.writeClipboardImage … fetches nothing" asserted that no request URL contained `variant=original`. The viewport already fetches the *selected* shot's original to display it, so that oracle conflicted with existing behavior and could never pass. It now asserts that no request was made for the menu target's original (`/captures/shot-b/image?variant=original`), which is what the AC means. No other Red assertion changed.
- **Portable byte read.** `toClipboardPng` reads blob bytes through `blobBytes`, which uses `Blob.arrayBuffer()` when present and falls back to `FileReader`. jsdom's `Blob` has no `arrayBuffer`; Chromium's does, so production takes the first branch.
- **Unplanned UX polish (handoff note).** `copyErrorMessage` strips Electron's `Error invoking remote method '<channel>': Error: ` prefix from a rejected invoke, so the status reads `Could not copy b.png: image could not be decoded` instead of the IPC wrapper text.
- The full behavior set for the capture page (`capture-page.behavior`, `capture-page`, `capture-clipboard`, `gui-actions-audit`, `clipboard-image-main`, `capture-filmstrip-actions.behavior`) was also run directly: 153/153.

## MEU-89 Red (row 6)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check red89 *> C:/Temp/av-kit/s38-run-red89.txt"
  exit: 0
  scope: "MEU-89 Vitest (AC-89.1-89.8) and the Electron spec -g AC-89 (AC-89.9), before any MEU-89 product edit"
  tested_state: "row 5 state plus the row 6 test files and the MEU-89 NEW_TESTIDS block; no product source changed"
  decisive_output:
    - "PASS MEU-89 Vitest RED: 9 assertion failures, 4 missing-symbol, load-tolerated files ['capture-filmstrip-select.test.ts'], TA pins failing []"
    - "PASS ui-build"
    - "PASS MEU-89 E2E RED: ['AC-89.9']"
    - "PASS red89"
```

- The 4 missing-symbol failures are `capture-batch-delete.test.ts` (`deleteCaptures is not a function`), one of the two `NEW_MODULE_FILES`. `capture-filmstrip-select.test.ts` fails to load (no module yet). The 9 assertion failures are the 8 AC-89.2–89.6 behavior tests and the AC-89.8 `endsWith` test; the AC-89.8 `original-annotated` guard already passes, as it should. Every MEU-88 test in the behavior file still passes.
- AC-89.9 fails on its first range assertion (`data-in-range` count 0, expected 3).
- The MEU-89 tests sit in a nested `describe` inside the existing behavior suite, so they reuse its fetch seam without editing any existing line. `SHOT_C` (removed in row 4 as unused) and `SHOT_D` are declared in that nested block. A nested `beforeEach` wraps the seam's `fetch`, holds each DELETE for 5 ms and records the in-flight maximum, so parallel DELETEs would show as `maxInFlight > 1` (AC-89.5).

## MEU-89 Green (row 7)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check green89 *> C:/Temp/av-kit/s38-run-green89.txt"
  exit: 0
  scope: "MEU-89 Vitest (AC-89.1-89.8), ui build, and the Electron spec -g AC-89 (AC-89.9)"
  tested_state: "row 6 tests (one type-only annotation fix, below) plus capture-filmstrip-select.ts, capture-commands.ts (deleteCaptures, removeCapture), CaptureFilmstrip.tsx, CapturePage.tsx and capture-help-content.ts"
  decisive_output:
    - "PASS green89-vitest: 34 passed of 34"
    - "PASS ui-build"
    - "ok 1 AC-89.9 Shift-click range, batch menu, ordered deletes with a reported failure, and a cancelled batch"
    - "PASS green89-e2e: expected 1 skipped 0"
    - "PASS green89"
```

- **No Red assertion changed.** The only test edit is a type annotation in `capture-batch-delete.test.ts`: the spy is typed `MockInstance<typeof queryClient.invalidateQueries>`, because `ReturnType<typeof vi.spyOn>` does not accept the generic `invalidateQueries` signature under `tsc`.
- **D-23 (autonomous): the per-shot remover lives in `capture-commands.ts`.** The plan has the page pass `remove`. The page passes `removeCapture`, a new export next to `deleteCapture` that sends one `DELETE /captures/{encodeURIComponent(id)}` with no catalog refresh, so `deleteCaptures` stays the only place that invalidates. `deleteCapture` is unchanged, as the plan says.
- **The range rides on `chooseItem`.** Every filmstrip choice passes the range it would apply (`{ anchorId: id, rangeIds: [] }` for a plain click). When the editor is dirty, the range waits in `pendingRange` next to `pendingSelect`; Confirm applies both and Cancel drops both (`RANGE_DIRTY`).
- **When `NEXT_SELECTION` moves the editor, it resets the view the way `chooseItem` does** (original variant, no text draft, empty undo and redo). This keeps the deleted shot's undo history from following the editor onto the next shot.

## Hub reconciliation (row 9)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check hub *> C:/Temp/av-kit/s38-run-hub.txt"
  exit: 0
  scope: "plan_checks.py hub (06 preload line, 09 notes, ACTION_ROWS) and the doc-reading Vitest suites"
  tested_state: "06-gui.md preload listing gains writeClipboardImage; 09 §Filmstrip context menu and §Filmstrip multi-select each gain one Session 38 plan row"
  decisive_output:
    - "PASS hub reconciliation"
    - "PASS hub-vitest: 20 passed of 20"
    - "PASS hub"
```

- 09 records its plan provenance as a table row whose Source cell reads `Session NN plan D-n` (Session 29 precedent, `09:625-641`), so each note is one such row: `Copy image source` (D-10, D-11) and `Anchor and order` (D-15, D-18).

## Gate (H1-2)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check gate *> C:/Temp/av-kit/s38-run-gate.txt"
  exit: 0
  scope: "full PROFILE D6 UI gate from npm ci: types, lint, build, harness build, Vitest, Electron E2E, state render, task contract, source audit, COUNT_FLOORS"
  tested_state: "baseline 90f041e plus the uncommitted product diff listed in gate-result.json product_uncommitted; node v24.19.0, electron@42.9.3"
  receipts: "gate-result.json; C:/Temp/av-kit/s38-gate-*.txt"
  decisive_output:
    - "vitest 848 passed of 848"
    - "e2e expected 141, unexpected 0, skipped 0, flaky 0"
    - "PASS COUNT_FLOORS: vitest 848 (baseline 800, +48 AC tests), e2e 141 (baseline 137, +4)"
    - "gate-source-audit: rg exit 1 (1 = no hits)"
    - "PASS gate"
```

- **D-24 (autonomous): a harness fix in `validate-task.ps1`, gate stage.** The first gate run ran every test green (Vitest 848/848) and then failed `gate-ui-tests` with `unhandled errors in C: ['receipt C missing']`. `$extra = $(if … { @("<receipt>") })` unrolled the one-element array to a string. Splatting a string (`@extra`) passes one character per argument, so `plan_checks.py vitest` read `C` as the receipt path. This was reproduced in isolation. The fix is `$extra = @(if … { "<receipt>" })`. The check itself (`vitest_ok` and its receipt scan for unhandled errors) is unchanged. The second run above is the gate of record.

## FILMSTRIP_LOOK (H1-2)

Mat ran both rounds on the dev app, launched detached with `Start-Process` from the worktree, with `ELECTRON_RUN_AS_NODE` removed and the live app data.

**Round 1 (2026-10-16), after the first gate.** Mat's answer, verbatim: "L3: Shift+F10 does nothing and not sure where to look for Menu key or what I should see. L5: Shift+click does nothing. All others are pass. The multi image selection shoudl enable check mark to the left of the images so they can be multi selected like items in p:/zorivest/ for example there if trades are being multi picked the checkmarks appear on the right so they can be clicked on and off."

| Item | Result |
|---|---|
| L1 right-click menu at the pointer; Copy full path | pass |
| L2 Copy image (PNG and JPEG/WebP) into Paint | pass |
| L3 Shift+F10 / Menu key | not seen. AC-88.2 (jsdom) and AC-88.12 (c) (Electron, focused thumb) both pass, so the likely cause is a thumb without focus; Mat was also unsure what the Menu key is. Re-checked in round 2 with the steps spelled out. |
| L4 menu Delete on a non-selected shot keeps the editor | pass |
| L5 Shift-click range of 3 → "Delete 3 shots" | Mat saw no result. AC-89.2–89.9 pass, but the range's only marks are a faint ring and the status count. Mat asked for checkboxes → D-25. |
| L6 the range in dark and light themes | pass |

**D-25 (human).** The plan was amended with `CHECK` and `CHECK_TOGGLE`, AC-89.10–89.15, a GUI compliance row, a Files row for `gui-actions-index.md`, a round 2 for `FILMSTRIP_LOOK`, and the D-25 decision entry. 09 §Filmstrip multi-select gains a `Checkboxes` row, and the `capture:batch_delete` label in `gui-actions-index.md` names ticked shots. MEU-89 then went back through Red and Green (below). USER_EXPLICIT 2026-10-16: "Going forward for this entire session all recemmendations are auto-approved."

**Round 2 (2026-10-16), after the D-25 Green.** Mat's answer: "All pass". This covers L3 with explicit focus steps, the new L5 (tick three boxes or Shift-click a range of 3 → only "Delete 3 shots", one confirm, all gone), and L7 (ticking leaves the editor's shot and marks alone; a plain thumb click clears the ticks).

## MEU-89 rework for D-25 (Red)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check red89b *> C:/Temp/av-kit/s38-run-red89b.txt"
  exit: 0
  scope: "MEU-89 Vitest unit set and the Electron spec -g AC-89; only AC-89.10 and above must be red (Invoke-Red -Since 10)"
  tested_state: "first gate state plus the D-25 tests (AC-89.10 in capture-filmstrip-select.test.ts; AC-89.11-89.14 appended in the behavior test; AC-89.15 appended in the Electron spec) and CAPTURE_FILMSTRIP_CHECK in test-ids.ts; no product source changed"
  receipts: "C:/Temp/av-kit/s38-red89b-vitest.json, s38-red89b-vitest.txt, s38-red89b-e2e.json"
  decisive_output:
    - "Tests 8 failed | 34 passed (42)"
    - "PASS MEU-89 Vitest RED: 5 assertion failures, 3 missing-symbol, load-tolerated files [], TA pins failing []"
    - "PASS MEU-89 E2E RED: ['AC-89.15']"
    - "PASS red89b"
```

- The 5 assertion failures are AC-89.11, AC-89.12, both AC-89.13 tests and AC-89.14, each on `expected [] to have a length of 4` (no checkbox per row yet). The 3 missing-symbol failures are AC-89.10 (`toggleSelection is not a function`) in `capture-filmstrip-select.test.ts`, one of the two `NEW_MODULE_FILES`. AC-89.1–89.9 stay green, which is why the rework Red runs with `Since 10`.
- AC-89.15 fails on `expect(checks).toHaveCount(3)`.
- **Harness (D-25):** `Invoke-Red` gains `-Suffix` (receipt ids `red89b-*`, so the row 6 receipts are kept) and `-Since`; `plan_checks.py vitest-red` and `e2e-red` take an optional `since` and filter the required ACs with `_since`. `hub` now also requires `D-25` in 09's multi-select section. The checks themselves are unchanged.

## MEU-89 rework for D-25 (Green)

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check green89 *> C:/Temp/av-kit/s38-run-green89b.txt; then -Check gate89 *> C:/Temp/av-kit/s38-run-gate89-d25.txt; then -Check hub *> C:/Temp/av-kit/s38-run-hub-d25.txt"
  exit: 0
  scope: "MEU-89 Green (Vitest, build, Electron -g AC-89), the MEU-89 gate (types, lint, unit plus regression set, build, Electron spec plus capture-inbox, --repeat-each=10 on AC-89 and AC-88), and hub reconciliation"
  tested_state: "Red state plus toggleSelection (capture-filmstrip-select.ts), the CHECK row in CaptureFilmstrip.tsx (onCheck prop) and checkChoice in CapturePage.tsx"
  receipts: "C:/Temp/av-kit/s38-green89-*.json|txt, s38-gate89-*.json|txt, s38-hub-vitest.json (these overwrite the row 7, row 8 and row 9 receipts of the same name; the earlier results stay recorded above and in the MEU-89 handoff)"
  decisive_output:
    - "PASS green89-vitest: 42 passed of 42"
    - "PASS green89-e2e: expected 2 skipped 0"
    - "PASS gate89-vitest: 283 passed of 283"
    - "PASS gate89-e2e: expected 33 skipped 0"
    - "PASS gate89-repeat: expected 20 skipped 0"
    - "PASS gate89-repeat88: expected 30 skipped 0"
    - "PASS hub reconciliation"
    - "PASS hub-vitest: 20 passed of 20"
```

- **No Red assertion changed.**
- **The checkbox is the thumb's sibling.** A `<button>` cannot contain an interactive `<input>`, so each filmstrip row is now a `div` holding the checkbox and then the unchanged thumb button. The thumb's class swaps `w-full shrink-0` for `min-w-0 flex-1` so that it shares the row. The box uses the existing `accent-accent` token (as `SegmentedControl` does).
- **Ticked means "in `rangeIds`", at any length**; `RANGE_MARK`, the count and the batch menu still apply only above one shot. Shift on a box is read from the click behind the change event (`nativeEvent.shiftKey`), so Space on a focused box toggles without extending.
- **`checkChoice` clears the editor notice** as `chooseItem` does. Without that, a notice left on the editor's shot (for example "Deleted 2 shots.") would hide the new count.

## Gate re-run after D-25 (H1-2, gate of record)

The D-25 rework changed product code after the first gate, so the full gate ran again from `npm ci`. This run is the gate of record, and `gate-result.json` now holds it. The first run (§Gate above) is kept as history.

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check gate *> C:/Temp/av-kit/s38-run-gate-d25.txt"
  exit: 0
  scope: "full PROFILE D6 UI gate from npm ci: types, lint, build, harness build, Vitest, Electron E2E, state render, task contract, source audit, COUNT_FLOORS"
  tested_state: "baseline 90f041e plus the uncommitted product diff whose 27 sha256 values gate-result.json lists (product_file_sha256), including the D-25 CaptureFilmstrip.tsx, CapturePage.tsx and capture-filmstrip-select.ts; node v24.19.0, electron@42.9.3"
  receipts: "gate-result.json (started 2026-10-16T15:03:33, finished 15:11:02); C:/Temp/av-kit/s38-gate-*.txt, s38-gate-vitest.json"
  decisive_output:
    - "PASS gate-ui-tests: 856 passed of 856"
    - "PASS gate-ui-electron: expected 142 skipped 0"
    - "PASS COUNT_FLOORS: vitest 856 (baseline 800, +56 AC tests), e2e 142 (baseline 137, +5)"
    - "gate-source-audit: rg exit 1 (1 = no hits)"
    - "PASS gate"
```

- Against the first run: Vitest +8 (AC-89.10 x3, AC-89.11, AC-89.12, AC-89.13 x2, AC-89.14) and E2E +1 (AC-89.15). `BASELINE_RED` did not fire: queue-canon AC-41.3 passed in both runs.
- `FILMSTRIP_LOOK` round 2 (§FILMSTRIP_LOOK) ran on this code before the gate. The gate changed no file that `product_file_sha256` lists.

## Gate re-run after F1 (gate of record)

The Codex execution review approved round 1 with one Medium, non-blocking finding (F1): deleting every remaining shot as a batch left `capture-status` empty, because the `Deleted {n} shots.` notice was keyed only to a surviving shot. The correction changed product code, so the full gate ran again from `npm ci`. This run is the gate of record, and `gate-result.json` now holds it. The two earlier runs (§Gate, §Gate re-run after D-25) are kept as history.

- Red: the new test `capture-filmstrip-actions.behavior.test.ts:708` ("AC-89.5 deleting every shot still reports the result once nothing is left to select") failed with `Expected "Deleted 2 shots." Received ""` after both DELETEs ran (`C:/Temp/av-kit/s38-f1-red.txt`, exit 1).
- Fix: `ShotNotice.shotId` is `string | null`, and `deleteRange` always sets the notice for the resulting selection, so it shows while the selection is empty (`CapturePage.tsx:199`, `:1104`). The status precedence is unchanged.
- Green: the behavior file passed 26/26 (`C:/Temp/av-kit/s38-f1-green.txt`, exit 0).

```yaml
evidence.v1:
  command: "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check gate *> C:/Temp/av-kit/s38-run-gate-f1.txt"
  exit: 0
  scope: "full PROFILE D6 UI gate from npm ci: types, lint, build, harness build, Vitest, Electron E2E, state render, task contract, source audit, COUNT_FLOORS"
  tested_state: "baseline 90f041e plus the uncommitted product diff that gate-result.json lists (product_file_sha256), including the F1 CapturePage.tsx and behavior test"
  receipts: "gate-result.json (started 2026-10-16T15:24:43, finished 15:35:14); C:/Temp/av-kit/s38-run-gate-f1.txt (sha256 7a08e102ca6d3af99a728ed0281ccbff3024687891af997eb9cfdbfd5dde3592), s38-gate-*.txt, s38-gate-vitest.json"
  decisive_output:
    - "PASS gate-ui-tests: 857 passed of 857"
    - "PASS gate-ui-electron: expected 142 skipped 0"
    - "PASS COUNT_FLOORS: vitest 857 (baseline 800, +57 AC tests), e2e 142 (baseline 137, +5)"
    - "gate-source-audit: rg exit 1 (1 = no hits)"
    - "PASS gate"
```

- Against the D-25 run: Vitest +1 (the F1 test); E2E unchanged. The run overwrote the shared `s38-gate-*` stage receipts; `s38-run-gate-d25.txt` keeps that run's summary.
- The same pass reconciled the static references the reviewer reported: AC-89.10–89.15 are named in task row 6, and D-20–D-24 are defined in the plan's `decision_log`. `-Check static` passes (`C:/Temp/av-kit/s38-run-static-f1.txt`).
