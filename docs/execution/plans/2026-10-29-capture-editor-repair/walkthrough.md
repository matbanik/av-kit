# Walkthrough — Capture editor repair: undo chords, resize handles, text re-edit (Session 43)

Execution record for [implementation-plan.md](implementation-plan.md) and [task.md](task.md). Working tree `P:/av-kit` on `main`, no branch and no worktree (AGENTS.md §Commits). Receipts are under `C:/Temp/av-kit/s43-*.txt`; decisive lines are pasted here.

## Execution message

- **Plan review.** Loop `s43-plan-2026-10-29-capture-editor-repair` closed `approved` in round 2 (verdict `.agent/context/handoffs/2026-10-29-capture-editor-repair-plan-critical-review.md`). Round 1: 9,639,572 tokens, 3 blocking (F1 focus on toolbar buttons, F2 text origin clamp, F3 stationary edge on collapse) and 1 non-blocking (F4 census anchor); round 2: 5,215,443 tokens, 0 blocking.
- **Review budget.** Round 1 exhausted the default plan budget (10,500,000 tokens). Mat continued the loop, verbatim: `Continue the S43 plan review for 3 more rounds`. Ledger `continue` recorded at 2026-10-29T17:31:30-04:00, +1 round, +30,000,000 tokens (`s43-plan-ledger-continue.txt`).
- **Round 2 notes (non-blocking), applied before row 0.** The plan's Verification §2 row 2 sentence now says AC-99.3(g) fails by assertion on the baseline (it is not required Red). The reviewer's `.claude/settings.local.json` status line does not occur on this host: `git check-ignore -v` shows the global ignore `**/.claude/settings.local.json`.
- **Execution gate (`plan_to_exec_gate: human`).** Mat's execution message, 2026-10-29, verbatim: `all recommendations are accepted, continue with @.agent/workflows/create-plan.md  and execution upon review approval.` The round 2 approval met that condition (D-161).
- **Context tools.** `context_tool_decision: not_applicable` re-checked at execution, 2026-10-29: row 0's prerequisite check reports no graph directory.

## Baseline

`baseline.sha` = `1856df5048af928ea74ce83393678c17534cb59b` (HEAD, tree unchanged under `ui/src`). Installs: `s43-sync.txt`, `s43-npm-ci.txt`, `s43-npm-ci-mcp.txt` clean; `s43-prereq.txt`: `prereq problems: []`; `s43-base-check.txt`: `baseline receipts without a result summary: []`.

| Suite | Result | Failing set |
|---|---|---|
| py-tests (`s43-base-py.txt`) | 1 failed, 956 passed | `test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]` (gate `$expectedBaselinePyFailed`, EC-1 of earlier sessions) |
| ui-tests (`s43-base-ui.txt`) | 1 failed, 1081 passed | `mcp-spawn-electron.test.ts` AC-71.10: `ENOENT ... node_modules/electron/path.txt` (Electron binary not yet unpacked after `npm ci` at unit time). Re-run alone: 3 passed (`s43-base-rerun-71.txt`). Environment, not a product failure. |
| mcp-tests (`s43-base-mcp.txt`) | 446 passed | none |
| ui-build (`s43-base-build.txt`) | built | none |
| ui-electron, `capture-inbox` + `keyboard-shortcuts` (`s43-base-e2e.txt`) | 5 failed, 37 passed (3.9m) | AC-67.20 A-6 (:1584), AC-67.35 A-10 (:1606), AC-80.10 (:1641), AC-81.11 (:1930, `F2 held by another process` — ShareX, D-120), AC-87.6 (:2420) |

Isolation re-run (`s43-base-rerun-e2e.txt`): :1584, :1606, :1641 and :2420 pass alone, so they are host flakes in a long Electron run (the D-120 pattern). The same grep caught `AC-67.20 AC-67.21 AC-67.22` (:1463), which passed in the full run but fails alone twice (`s43-base-rerun-1463.txt`: `capture-apply-image-hint` not found) — order-dependent on the unchanged tree, outside this plan's files. Later rows compare against this set: a test in it may fail without counting as a regression; any other failure does.

## Census

Row 1 receipt `s43-census.txt`: 300 hits across 39 files; `s43-census-check.txt`: `census anchors missing: []`. No hit is a new contradiction (S2 not triggered).

| Hits | Disposition | Reason |
|---|---|---|
| `ui/tests/e2e/capture-inbox.test.ts:1680` | **TA-1** | The disabled Undo hint becomes `Undo (Ctrl+Z)` (HISTORY_HINTS). |
| `ui/tests/unit/capture-page.behavior.test.ts:1506` (loop over `MEU65_TOOLBAR` :1438) | **TA-2** | Undo/Redo focused hints name their chord; `HINT_OVERRIDE[id] ?? name`, aria-label stays the name. |
| behaviour :1537-1545 (AC-65.2 no-shot hint loop) | unaffected | Iterates select/arrow/box/highlight/text only; Undo/Redo not in it. |
| behaviour :1915 | unaffected | Zoom ids only. |
| behaviour text-draft, handle, Undo/Redo click hits | unaffected | Behaviour preserved: buttons call the same `undo`/`redo`; drafts and arrow handles unchanged. |
| behaviour viewport prop fixtures :2878-3060 (`canUndo`, `onUndo`, `textDraft: null`) | unaffected | Prop names and types unchanged; MEU-100's new viewport prop is optional (re-checked at row 5). |
| `capture-hit-test.test.ts` arrow-handle cases :56-122 | unaffected | HIT_ORDER keeps the selected arrow's ends first. |
| `capture-hit-test.test.ts` AC-60.3 :140-175 | unaffected | Text plate centre and far point stay body; plate corners lie beyond `RESIZE_HIT_CSS/2`. |
| `capture-hit-test.test.ts` AC-66.5, AC-90.10/91.9 | unaffected | `selectedIndex` null: no handles exist. |
| `capture-action-row.test.ts` (24) | unaffected | Undo clicks, arrow handle layer, help loop, draft: unchanged behaviour. |
| `capture-help-content.test.ts` (17) | unaffected | Every four-tools assertion is `toContain`/`endsWith(RANGE_HELP_SENTENCE)`; the new sentence sits mid-body. |
| `capture-inbox.test.ts` :226-227, :253-254, :344-345, :431-432, :539-563, :882-883, :1479, :2009-2074, :2369 | unaffected | Visibility, clicks, disabled state, draft fill/Enter, arrow-handle drag and Tab order (arrow mark, no rect handles): unchanged. |
| `capture-inbox.test.ts` :1383-1452, :2121-2127, :2485-2491 `endsWith` | unaffected | URL path routing in seams. |
| `capture-toolbar.test.ts` :68, :85-86 | unaffected | `TOOLBAR_BUTTONS` names unchanged. |
| `capture-page.test.ts` :77-78, :268-269, :624 | unaffected | Test ids still present; region unchanged. |
| `common-shortcuts.test.tsx` :25-87, `helpers/bound-hint.ts`, `shortcuts.test.ts` | unaffected | `BOUND_CONTROLS` and `RESERVED_CHORDS` sets unchanged (RESERVED_NOTE is a comment); Undo/Redo are not registry-bound. |
| `tooltip.test.tsx` (11) | unaffected | Generic Tooltip with its own labels. |
| `test-ids.ts` (8) | unaffected | Existing constants unchanged; MEU-100 adds new ids. |
| `capture-text-metrics.test.ts:16` | unaffected | `textBackgroundBox` signature unchanged. |
| `endsWith` hits in mcp-server tests, convert/download/picker/filmstrip e2e, api-fetch, lifecycle, picker, gui-actions-audit, icon-hints, palette-curation, page tests, header-toggles, queue tests, bundle, runner | unaffected | URL, path or filename suffix checks outside the Capture editor. |
| `icon-hints.test.ts` AC-80.8 :310-327 (corrected in row 8, D-177) | TA-3 | The hint loop compares `{id}-hint` text to `spec.name`; MEU-99 makes Undo/Redo `Undo (Ctrl+Z)`/`Redo (Ctrl+Y)`. The row 1 census listed the file only for its `endsWith` hits; gate attempt 3 found it. |
| `tests/conftest.py` | unaffected | Docstring word "Undo". |

## MEU-99 Red

Row 2 receipts `s43-99-red-ui.txt`, `s43-99-red-build.txt`, `s43-99-red-e2e.txt`, `s43-99-red-check.txt`; no `ui/src` change against `baseline.sha`. TA-1 and TA-2 applied in the same row.

| Test | Red (assertion) |
|---|---|
| AC-99.1 | `{"ctrl":true} z: expected 2 to be 1` |
| AC-99.2 | `expected 2 to be 1` |
| AC-99.3 (e) | `(e) prevented mid-gesture: expected false to be true` (not required Red) |
| AC-99.3 (f)(g)(h) | `(h) empty history prevented: expected false to be true` (not required Red; plan §Verification row 2) |
| AC-99.4 | chord run `selected: 1` against the button run (chords did nothing) |
| AC-99.5 | `capture-undo aria-keyshortcuts: expected null to be 'Control+Z'` |
| AC-99.6 | four-tools body does not contain `HELP_EDIT_SENTENCE HISTORY_HELP_SENTENCE` |
| AC-99.7 (e2e) | `Error: expect(received).toBe(expected)`, Expected 1, Received 2 after the first surface `Control+KeyZ` |

AC-99.3 (a)(b) and (c)(d) pass on the baseline: they are negatives (the chord must not act), which hold before the feature exists. Vitest 7 failed, 2 passed (137 with 128 skipped by `-t`); `red-check: 2 receipt(s), 6 required test(s), 0 problem(s)`.

## MEU-99 Green

Row 3 receipts `s43-99-green-ui.txt`, `s43-99-green-build.txt`, `s43-99-green-e2e.txt`, `s43-99-snapshot.txt`, `s43-99-green-rerun-8010.txt`.

| Suite | Result |
|---|---|
| Vitest (behaviour, page, help, toolbar, tooltip, shortcuts, common-shortcuts) | 7 files, 200 passed |
| Build | built (`CapturePage` chunk 158.69 kB) |
| Electron `capture-inbox` + `keyboard-shortcuts` | 41 passed, 2 failed: AC-80.10 (:1641, `capture-undo-hint` gone after `toBeVisible`) and AC-81.11 (:1930, `F2 held by another process`), both in the §Baseline set; AC-99.7 passed |
| AC-80.10 alone (TA-1 line) | 1 passed: the hint reads `Undo (Ctrl+Z)`; the full-run miss is the baseline hover flake |
| `row3-ui-src.json` | 167 files |

No chord failed to reach the renderer and nothing reloaded or zoomed (S4 not hit).

## MEU-100 Red

Row 4 receipts `s43-100-red-ui.txt`, `s43-100-red-tree.txt`, `s43-100-red-build.txt`, `s43-100-red-e2e.txt`, `s43-100-red-check.txt`; `ui/src` unchanged against `row3-ui-src.json`.

| Test | Red (assertion) |
|---|---|
| AC-100.1–100.4 | `capture-transform.ts exists: expected false to be true` (the module is new) |
| AC-100.5 | `expected { kind: 'body', index: +0 } to deeply equal { kind: 'resize', handle: 'se', …(1) }` |
| AC-100.6 | `rect resized: expected [ 3, 4, 3, 3 ] to deeply equal [ 1, 1, 5, 6 ]` (the drag moves the box) |
| AC-100.7 | `preview before Escape: expected [ 3, 4, 3, 3 ] to deeply equal [ 1, 1, 5, 6 ]` |
| AC-100.8 | `eight handles: expected [] to deeply equal [ 'capture-handle-resize-e', …(7) ]` |
| AC-100.9 | `resized: expected [ 3, 4, 3, 3 ] to deeply equal [ 1, 1, 5, 6 ]` |
| AC-100.10 | four-tools body does not contain `HISTORY_HELP_SENTENCE RESIZE_HELP_SENTENCE` |
| AC-100.11 (e2e) | `Error: expect(received).toBe(expected)`, Expected 1, Received 0 (`capture-handle-resize-se` count) |

Vitest 10 failed (145 skipped by `-t`); Electron 1 failed; `red-check: 2 receipt(s), 11 required test(s), 0 problem(s)`. The eight `CAPTURE_HANDLE_RESIZE_*` constants are in `test-ids.ts`.

## MEU-100 Green

Row 5 receipts `s43-100-green-ui.txt`, `s43-100-green-build.txt`, `s43-100-green-e2e.txt`, `s43-100-snapshot.txt`, `s43-100-green-e2e-rerun.txt`, `s43-100-green-rerun-5710.txt`, `s43-100-green-rerun-flakes.txt`.

| Suite | Result |
|---|---|
| Vitest (transform, hit test, behaviour, page, help, annotate, text metrics) | 7 files, 198 passed |
| Build | built (`CapturePage` chunk 164.30 kB) |
| Electron `capture-inbox`, first run | 37 passed, 5 failed: AC-67.20 (:1463), AC-67.20 A-6 (:1584), AC-67.35 (:1606) and AC-81.11 (:1930, `F2 held by another process`) are in the §Baseline set; AC-57.10 (:736) drew no arrow; AC-100.11 passed |
| AC-57.10 alone, `--repeat-each=5` | all passed |
| Electron `capture-inbox`, full re-run (6.8 min under load) | 39 passed, 3 failed: AC-65.4 (:868) and AC-66.13 (:1111) hit the 60 s test timeout, AC-81.11 baseline; AC-57.10 and AC-100.11 passed |
| AC-57.10, AC-65.4, AC-66.13, `--repeat-each=3` | 9 passed |
| `row5-ui-src.json` | 168 files |

`capture-transform.ts` holds `TRANSFORM`; `HIT_ORDER` adds the selected box mark's resize handles after `selectedHandle`; `RESIZE_GESTURE` adds `'resizing'` to the select-tool gesture and reuses the threshold, preview, `replaceAt` history and Escape/cancel paths; `RESIZE_HANDLES` renders the eight squares; `HELP_TEXT` adds the MEU-100 sentence. The hover cursor (`hoverHandle`) clears when the selection changes and applies only while resize handles render, so a selected arrow never keeps a box's resize cursor. The non-baseline Electron failures moved between runs and passed alone, so they are timing flakes on a loaded machine, not MEU-100 regressions; the row 8 `e2e-repeat` gate covers AC-99/100/101 under S6.

## MEU-101 Red

Row 6 receipts `s43-101-red-ui.txt`, `s43-101-red-tree.txt`, `s43-101-red-build.txt`, `s43-101-red-e2e.txt`, `s43-101-red-check.txt`; `ui/src` unchanged against `row5-ui-src.json`.

| Test | Red (assertion) |
|---|---|
| AC-101.1 | `expected 'undefined' to be 'function'` (`textPlateHandlePoints` is new) |
| AC-101.2 | `the draft opens with the text: expected undefined to be 'Hello'` (`dblclick` opens no draft) |
| AC-101.3 | `Enter on a text mark is prevented: expected false to be true` |
| AC-101.4 | `four corners: expected [] to deeply equal [ 'ne', 'nw', 'se', 'sw' ]` |
| AC-101.5 | four-tools body does not contain `RESIZE_HELP_SENTENCE TEXT_EDIT_HELP_SENTENCE` |
| AC-101.6 (e2e) | `Error: expect(received).toBe(expected)`, Expected 1, Received 0 (`capture-text-draft` count after the double-click) |

Vitest 5 failed (155 skipped by `-t`); Electron 1 failed; `red-check: 2 receipt(s), 6 required test(s), 0 problem(s)`. AC-101.3 seeds a saved text mark, so "records nothing" reads as Undo staying disabled. AC-101.6 scales with the `nw` corner, not `se`: see EC-6.

## MEU-101 Green

Row 7 receipts `s43-101-green-ui.txt`, `s43-101-green-build.txt`, `s43-101-green-e2e.txt`, `s43-101-green-w9-rerun.txt`.

| Suite | Result |
|---|---|
| Vitest (transform, hit test, behaviour, page, help, annotate, text metrics) | 7 files, 203 passed |
| Build | built (`CapturePage` chunk 168.51 kB) |
| Electron `capture-inbox` (7.9 min) | 39 passed, 4 failed: AC-67.20 (:1463, order-dependent) and AC-87.6 (:2420) are in the §Baseline set; W9-3 (:213) and W9-4 (:276) hit the 60 s test timeout; AC-101.6 passed |
| W9-3, W9-4, `--repeat-each=5` | 10 passed |

`TEXT_SCALE` adds `textPlateHandlePoints` and `scaleTextMark` to `capture-transform.ts`; `HIT_ORDER` gives a selected text mark its four plate corners; `RESIZE_GESTURE` routes a corner drag on a text mark to `scaleTextMark` through the same preview, threshold and `replaceAt` history; `RESIZE_HANDLES` draws the four corners. `TEXT_REEDIT`: `TextDraft.editIndex` names the edited mark and `SurfacePointer` gains `'dblclick'`, emitted by the surface's `onDoubleClick`. A select-tool double-click on a text body, or plain Enter on a selected text mark, opens the draft with the mark's text; the viewport paints neither the mark nor its handles while the draft is open. Commit replaces `text` in place as one step; an empty or unchanged draft and Escape record nothing, and an unchanged draft is not dirty. While an edit draft is open, Undo, Redo and mark removal are inert so the index cannot drift. `HELP_TEXT` adds the MEU-101 sentence after the MEU-100 one.

The first row 7 attempt stopped before any test ran: a Vitest worker hit `Fatal process out of memory` with about 0.5 GB of commit free, held by other sessions' processes (not this worktree's). After memory came back, the row ran again whole, and those are the receipts above. W9-3 and W9-4 passed alone, so like the row 5 timeouts they are load flakes, not MEU-101 regressions.

## Gate

**Attempt 1 (row 8): stopped at S8.** `s43-gate.txt`: `identity-before`, `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types` and `task-contract` exit 0; `scope-paths` exit 1, so every later step printed `not_run` (fail-fast). The decisive line is `changed paths: 44 outside scope: ['.agent/model-registry.local.json', '.claude/agents/av-kit-builder.md', '.claude/agents/av-kit-verifier.md', '.cursor/agents/av-kit-builder.md', '.cursor/agents/av-kit-verifier.md'] head: 1856df5048af928ea74ce83393678c17534cb59b head moved (S8): False`. `tested_state` was `1856df5…+ad1c9c21…`.

All five files changed together at 2026-10-29T22:21:57Z, after `baseline.sha` (17:38 local). Each diff is one provenance hash: `validated_against` and the `AUTOGEN: model-registry` comments go from `a7c95972…`/`7e85d6f3…` to `7097dc5b…`. No tool call in this session wrote them (the session transcript shows only a read-only wait at that time), so they are another writer's model-registry sync. S8 applies: stop and ask Mat; no commit, stash or revert of that work. Row 8 stays open.

**Attempt 2 (row 8, 2026-11-03): stopped at S5/S8.** Attempt 1's receipt is kept as `s43-gate-attempt1.txt`. Mat committed the five paths as `7706fcd` (EC-7). `s43-gate.txt`: `identity-before` through `scope-paths` exit 0 (`changed paths: 39 outside scope: [] head: 7706fcde… registry sync (EC-7) ok: True head moved (S8): False`); `py-tests` exit 1 with `3 failed, 954 passed`, and every later step printed `not_run`. AC-25.7 is the §Baseline failure; the two others are outside it: `tests/tooling/test_framework_adoption.py::test_review_pipeline_governance_static_oracles[none]` and `::test_governance_preservation_and_routing_inventory[history]`, both `REFUSE: uncensused model pin: .cursor/agents/av-kit-builder.md` from `docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py`. `7706fcd` changed that file's line 4 from `model: cursor-grok-4.6-xhigh` (censused, `83203330…`) to `model: composer-2.5-fast` (`a559daa5…`); `routing-census.md` lists `a559daa5…` for `.cursor/agents/av-kit-verifier.md` only. A sweep with the checker's own rule finds no other uncensused pin line. This session wrote neither file, and the fix (a census entry in another plan's folder, or a change to the committed pin) is outside this plan's scope, so S5/S8 apply: stop and ask Mat. Row 8 stays open.

**Attempt 3 (row 8, 2026-11-03): stopped at S2 (D-176, D-177).** Attempt 2's receipt is kept as `s43-gate-attempt2.txt`. `s43-gate.txt`: `identity-before` through `scope-paths` exit 0 (`changed paths: 41 outside scope: [] ... registry sync (EC-7) ok: True head moved (S8): False`); `py-tests` exit 1 with `1 failed, 956 passed`, the one failure the row 0 baseline AC-25.7 (allowed); `ui-tests` exit 1 with `35 failed | 1071 passed (1106)` in 6 files, and every later step printed `not_run`. 34 failures are `TypeError: Cannot read properties of undefined (reading 'clear'|'getItem')`: WinGet moved the machine's Node from 24 to 26.13.0 on 2026-11-01, after the baseline, and Node 26's own `localStorage` global hides jsdom's (D-176). The 35th is AC-80.8 in `icon-hints.test.ts`, which still expects the hint `Undo`: a census miss beside TA-2 (D-177). Probes: the five storage files pass with `NODE_OPTIONS=--no-experimental-webstorage` (`s43-ls-nowebstorage.txt`, `61 passed`); the full suite under the flag gives `1 failed | 1105 passed` (`s43-ui-nowebstorage.txt`); the mcp build and suite pass on Node 26 (`s43-mcp-node26.txt`, `446 passed`).

**Attempt 4 (row 8, 2026-11-03): all steps exit 0.** Attempt 3's receipt is kept as `s43-gate-attempt3.txt`. This run came after D-176 (EC-9, the worker flag in `ui/vitest.config.ts`) and D-177 (EC-10, TA-3), with Mat having closed ShareX (S40 precedent). `s43-gate.txt`: `tested_state` `7706fcd…+40f1f572…` is the same at `identity-before` and `identity-after`. `scope-paths` gives `changed paths: 43 outside scope: [] … registry sync (EC-7) ok: True head moved (S8): False`. `py-tests` gives `1 failed, 956 passed`, the one failure being the row 0 baseline AC-25.7 (`outside_baseline=[]`). `ui-tests` gives `1106 passed (1106)` on Node 26.13.0, `mcp-tests` gives `446 passed`, and `state-render` passes its drift check. `ui-electron` gives `181 passed (4.8m)` and `e2e-repeat` gives `30 passed`, with no retries and no failures; AC-81.11 passes with F2 free. The last line is `session-gate: all steps exit 0`.

## Hub

Row 9, 2026-11-03, after gate attempt 4.

- `docs/build-plan/09-screenshot-capture.md`: one `> **Delivered (Session 43).**` note after each of the three residual MEU tables (MEU-99, MEU-100, MEU-101), naming its ACs, the gate and this plan.
- `docs/build-plan/06-gui.md`: the `RESERVED_NOTE` Delivered note after the Session 41 note. It says Capture handles the history chords while its image has focus, and that they stay in `RESERVED_CHORDS`.
- `docs/build-plan/gui-actions-index.md` (`INDEX_TRIGGER`): `capture:undo` is now `Undo overlay; Ctrl+Z on the image`, and `capture:redo` is now `Redo overlay; Ctrl+Y or Ctrl+Shift+Z on the image`.
- `meu_status.py update`: MEU-99, MEU-100 and MEU-101 are set to `ready_for_review` with `--plan docs/execution/plans/2026-10-29-capture-editor-repair/`, then `meu_status.py render` (`All regions rendered successfully`).
- The row 9 command (`s43-row9.txt`) exits 0. The hub `rg` gives 49 lines (`s43-hub-rg.txt`), `hub problems: []` (`s43-hub-status.txt`), and `render --check` gives `Drift check passed` (`s43-state-render.txt`).

## H1 verification

2026-11-03, after row 9.

- H1-1: `unchecked implementation rows: []`, exit 0.
- H1-2 ran four times, and only `ui-electron` ever failed. Attempts 1 to 3 ran on the same tree (`tested_state` `7706fcd…+7c3a3dee…` every time). The CPU was at 100% from other processes.
  - Attempt 1 (18.4m): 178 passed, 3 failed: `command-palette-nav.spec.ts:31` and `:40`, and `console-chrome.test.ts:30` (C1-1), each `Test timeout of 60000ms exceeded`. Those two spec files then passed alone, 39 of 39 (`s43-h1-2-rerun-timeouts.txt`). Receipts: `s43-gate-h1-attempt1.txt` and `s43-h1-2-attempt1-ui-electron.txt`.
  - Attempt 2 (22.0m, still loaded): 178 passed, 3 failed: AC-90.12 (`capture-inbox.test.ts:2615`) and W2-4 (`transcript-queue.test.ts:268`) timed out, and AC-97.7 (`convert-queue.test.ts:1584`) gave up its 5 s `toHaveCount(1)` wait. Those three then passed alone, 9 of 9 in 19.5s (`s43-h1-2-rerun2-timeouts.txt`), with the CPU back near 10%. Receipts: `s43-gate-h1-attempt2.txt` and `s43-h1-2-attempt2-ui-electron.txt`.
  - Attempt 3 (`s43-gate-h1-attempt3.txt`): `session-gate: all steps exit 0`. py-tests went by the baseline rule (1 failed, 956 passed, `outside_baseline=[]`). The other counts: ui 1106 passed, MCP 446 passed, Electron 181 passed (4.1m), e2e repeat 30 passed, and `tested_state` was the same before and after. The H1-7 round 1 fix (EC-11) then changed `CapturePage.tsx` and its behaviour test, so this pass is kept as prose only.
  - Attempt 4, after EC-11 (`s43-gate-h1.txt`): `session-gate: all steps exit 0`, with the CPU near 10%. py-tests went by the baseline rule (1 failed, 956 passed, `outside_baseline=[]`). ui 1107 passed (the extra test is the F1 regression), MCP 446 passed, Electron 181 passed (4.9m), e2e repeat 30 passed (59.1s), and scope-paths reported 50 changed paths with none outside scope. `tested_state` `7706fcd…+bc2de358…` was the same before and after. This is the full record.
- H1-3: the current focus was updated to Session 43, and `render --check` gave `Drift check passed`. H1-4: `added: [] removed: [] changed: []`. Both re-ran after attempt 4, with the same output.
- H1-6, H1-6a and H1-6b: all three handoffs passed the closeout, AC-coverage (16 of 16 families) and `--require-full` durable-evidence checks, before EC-11 and again after the handoffs were regenerated for attempt 4.

## Execution Correction Notes

- **EC-1 (row 2).** The first row 2 run gave `red-check: required test AC-99.7 did not fail by assertion alone: ['Error: surface Control+KeyZ']`. Playwright prints a custom `expect` message as the error header, which hides the `expect(` line `red-check.py` attributes. The AC-99.7 step labels moved into `test.step(...)` and the `expect` calls lost their message argument; assertions and steps are unchanged. Re-run: 0 problems.
- **EC-2 (row 3).** The row 3 command exits on any Electron failure before its snapshot step, so the two §Baseline-set failures (AC-80.10, AC-81.11) left `row3-ui-src.json` unwritten. The snapshot step ran alone, unchanged, on the same tree (`s43-99-snapshot.txt`, 167 files); `ui/src` was not edited between the run and the snapshot.
- **EC-3 (row 4).** The first row 4 run gave `red-check: required test AC-100.11 did not fail by assertion alone: ['Error: expect(locator).toBeVisible() failed', 'Error: element(s) not found']`: Playwright adds `element(s) not found` under a locator assertion on a missing element. AC-100.11 now polls `capture-handle-resize-se`'s count to 1 before the unchanged `toBeVisible`, so the Red is a plain `expect(received).toBe` line. Re-run: 0 problems.
- **EC-4 (row 5).** AC-100.8 as written in row 4 deselected with a click at CSS (190,10), which rounds to image x 8, outside the 8×8 shot, and reselected the box with a click at CSS (25,62), which on this fixture lands inside the arrow's head (head length `max(10, 5·3)` = 15 image px covers the whole box). Neither click could do what the AC asks. The deselect click moved to CSS (160,10) (image (6,0), clear of every mark) and the box is reselected from its `Box 1` chip; the AC's assertions are unchanged and one was added (a selected arrow keeps no resize cursor), which exposed a stale-cursor defect fixed in Green.
- **EC-5 (row 5).** As in EC-2, the row 5 command exited on Electron failures before its snapshot step; the snapshot step ran alone, unchanged, on the same tree (`s43-100-snapshot.txt`, 168 files).
- **EC-6 (row 6).** AC-101.6 says to drag the `se` plate handle outward. On the 8×8 fixture `Done` at font size 2 from (3,6) has the plate {3,7,5,1}, so `se` is the image corner (8,8): the pointer clamps to 0..7 and can only shrink the plate. The test drags `nw` from (3,7) out to (0,0) about the `se` anchor instead (ratio 8, `font_size` 16); the assertion (Save posts `font_size` above 2) is unchanged.
- **EC-7 (row 8).** Gate attempt 1 stopped at S8 on five registry overlay paths no tool call of this session wrote. Mat cleared them with commit `7706fcd` (`chore(registry): sync the AUTOGEN registry overlays`), whose parent is `baseline.sha` and whose diff is exactly `.agent/model-registry.local.json`, `.claude/agents/av-kit-{builder,verifier}.md` and `.cursor/agents/av-kit-{builder,verifier}.md`, then said to continue. `scope-paths` now accepts that one commit as HEAD: it checks the parent and the five paths, and diffs the work tree against HEAD, so this session's uncommitted paths are checked as before. Any other HEAD is still S8. `baseline.sha` and the row 0 receipts are unchanged; the allow-list is unchanged.
- **EC-8 (row 8).** Gate attempt 2 stopped at `py-tests` on `7706fcd`'s uncensused builder pin (§Gate). Mat ruled D-175 (`human-gate-decision.md`): one `routing-census.md` entry for `.cursor/agents/av-kit-builder.md` line 4, the same fields as the verifier's line 4 entry. That path is added to the `scope-paths` allow-list and to the §Hub and state files table together (the plan's rule: change both), and the H2 commit draft gives it its own `chore(registry)` commit. The two tests then gave `10 passed` (`s43-175-adoption.txt`).
- **EC-9 (row 8).** Gate attempt 3 failed 34 UI unit tests on storage: WinGet moved the machine's Node from 24 to 26.13.0 on 2026-11-01, after the row 0 baseline, and Node 26's own `localStorage` global hides jsdom's (§Gate). Mat ruled D-176 (`human-gate-decision.md`) after a Node 26 impact review: only the UI unit suite is affected, and `ui/vitest.config.ts` gains `test.poolOptions.forks.execArgv: ['--no-experimental-webstorage']` with a comment naming the Vitest 5 fix. The gate's step commands are unchanged. The path is added to the `scope-paths` allow-list and the §Hub and state files table together, and the H2 commit draft gives it its own `chore(test)` commit.
- **EC-10 (row 8).** Gate attempt 3 found AC-80.8 (`icon-hints.test.ts`) still expecting the hint `Undo`, a row 1 census miss beside TA-2 (§Census, §Gate). Mat ruled D-177 (`human-gate-decision.md`): TA-3 declares `HINT_OVERRIDE` for `capture-undo`/`capture-redo` and AC-80.8 compares against `HINT_OVERRIDE[id] ?? spec.name` in both loops. The path is added to the `scope-paths` allow-list and the MEU-99 Files Modified table together.
- **EC-11 (H1-7 round 1 F1).** The Codex execution review found that a text corner scale left the Size inspector on the old `font_size`, so ArrowUp, the wheel or a scrub then started from the stale value: on the AC-101.4 fixture the scale took 2 to 4, Size still showed 2, and Up set 3. The gesture commit in `CapturePage.tsx` called `applyHistory` and `setSelectedIndex` but never `inspectMark`. It now calls `inspectMark(gesture.index)` after the commit; the history step and the abort paths are unchanged. A new behaviour test, `AC-101.4 after a corner scale the Size field shows the new font_size, and ArrowUp steps from it [review F1]`, failed first (`Size after the scale: expected '2' to be '4'`, `s43-f1-red.txt`) and passes after the fix (`s43-f1-green.txt`). The five Capture unit files then gave 164 passed (`s43-f1-vitest.txt`), and ui typecheck and lint exited 0. Both paths are already in scope. H1-2 re-ran on the new tree.
